"""Gera o layout NAZAFIGHT (screenpack do IKEMEN GO v1.0.0) inteiro por codigo, mais as previas.

Uso:  python ferramentas/gerar_layout.py            (gera tudo; sai com codigo 0 se passou nas checagens)

Saidas:
  motif/nazafight/system.def system.sff fight.def fight.sff fonts/*.def fonts/*.sff
  docs/previas-layout/titulo.png selecao.png vs.png hud.png   (1280x720)

Regras (docs/regras-dos-lutadores.md, AGENTS.md e a direcao do layout):
  * pixel art de arcade: tudo e desenhado numa grade logica (320x180 na tela cheia) e ampliado 4x por vizinho
    mais proximo; todo eixo e toda posicao no .def e o valor final (multiplo de 4);
  * so as 16 cores de PALETA; o gerador falha se achar pixel opaco de outra cor;
  * nada baixado nem copiado: fontes, molduras e cenas sao desenhadas aqui; sem marca; do KOF so a convencao
    (vida no alto, relogio no meio, retrato nas pontas, poder embaixo, estoques);
  * deterministico: rodar duas vezes da o mesmo hash (sem data, sem aleatorio sem semente).
As previas sao montadas com os MESMOS sprites que entram no SFF e com as posicoes lidas de volta do .def gerado.
"""
import hashlib
import random
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from layout_sff import escrever_sff2, ler_sff2  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
MOTIF = RAIZ / "motif" / "nazafight"
PREVIAS = RAIZ / "docs" / "previas-layout"
ESCALA = 4  # grade logica -> tela final

# ----------------------------------------------------------------------------------------------------------
# Paleta (16 cores, so estas) e posicoes finais (1280x720)
# ----------------------------------------------------------------------------------------------------------
PALETA = {
    "breu": (0x14, 0x0C, 0x10),
    "barro": (0x3A, 0x1C, 0x14),       # barro queimado
    "taua_esc": (0x7A, 0x2E, 0x1C),
    "taua": (0xB4, 0x47, 0x2A),
    "taua_vivo": (0xE0, 0x70, 0x3E),
    "tabatinga": (0xED, 0xE3, 0xCF),
    "farinha": (0xF6, 0xE7, 0xA8),
    "dende": (0xF2, 0xA8, 0x1D),
    "madeira": (0x6B, 0x44, 0x24),
    "madeira_cl": (0x9C, 0x6B, 0x3C),
    "folha": (0x3E, 0x8A, 0x3A),
    "mangue": (0x1F, 0x4A, 0x33),
    "rio": (0x2C, 0x6E, 0x80),
    "reflexo": (0x5F, 0xAA, 0xB0),
    "ceu": (0xF0, 0x8A, 0x6C),
    "azulejo": (0x2E, 0x4E, 0x9E),
}

POS = {
    # HUD (fight.def). Trilho de vida: canto superior esquerdo da prancha; o retrato encosta na alca da ponta de
    # fora e a tarja do nome fica colada embaixo do trilho (y 88 a 120): o HUD de cima termina em y = 120.
    "vida_p1": (144, 24), "vida_p2": (720, 24),
    "relogio": (640, 8),             # centro x, topo y do caxixi
    "face_p1": (4, 4), "face_p2": (1160, 4),         # canto da moldura 29x29 (logico)
    "nome_p1": (152, 88), "nome_p2": (1128, 88),     # P1: x da esquerda; P2: x da direita; y = topo do texto
    "vitoria_p1": (424, 92), "vitoria_p2": (832, 92),
    "placa_p1": (16, 668),           # canto da placa de breu do poder (P1; a do P2 e o espelho)
    "round": (640, 300),
    "combo": (40, 300),
    # Titulo
    "logo": (640, 152),               # centro do logo (x, y)
    "subtitulo": (640, 288),
    "menu": (640, 487),               # linha de base do 1o item
    "menu_espaco": 40,
    "painel_menu": (448, 432),
    "canoa_y": 496,
    # Selecao
    "grade": (372, 392), "celula": 128, "celula_espaco": 8, "colunas": 4, "linhas": 2,
    "retrato_p1": (24, 64), "retrato_p2": (808, 64), "retrato_alto": 216,
    "tabuleta_sel_y": 71,                                     # topo (logico) da tabuleta do nome, sob o retrato
    "nome_sel_p1": (248, 331), "nome_sel_p2": (1032, 331),   # centro x (= centro do retrato), linha de base
}


def cor(nome, a=255):
    return PALETA[nome] + (a,)


# ----------------------------------------------------------------------------------------------------------
# Desenho basico (tudo em pixels logicos)
# ----------------------------------------------------------------------------------------------------------
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])


def nova(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def ampliar(img, k=ESCALA):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


def espelhar(img):
    return img.transpose(Image.FLIP_LEFT_RIGHT)


def arr(img):
    return np.array(img, dtype=np.uint8)


def de_arr(a):
    return Image.fromarray(a.astype(np.uint8), "RGBA").copy()   # copia: fromarray devolve imagem so de leitura


def opaco(img):
    return arr(img)[:, :, 3] > 0


def deslocar(m, dx, dy):
    """Desloca uma mascara booleana sem dar a volta."""
    h, w = m.shape
    out = np.zeros_like(m)
    ys0, ys1 = max(0, -dy), min(h, h - dy)
    xs0, xs1 = max(0, -dx), min(w, w - dx)
    out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = m[ys0:ys1, xs0:xs1]
    return out


def dilatar(m, diag=True):
    out = m.copy()
    viz = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if diag:
        viz += [(1, 1), (-1, -1), (1, -1), (-1, 1)]
    for dx, dy in viz:
        out |= deslocar(m, dx, dy)
    return out


def erodir(m, diag=False):
    return ~dilatar(~m, diag)


def pintar_mascara(img, m, nome):
    a = arr(img)
    a[m] = cor(nome)
    return de_arr(a)


def contorno(img, nome, diag=True):
    m = opaco(img)
    borda = dilatar(m, diag) & ~m
    return pintar_mascara(img, borda, nome)


def com_sombra(img, nome, dx=1, dy=1):
    """Sombra dura (copia deslocada) atras do desenho; cresce a imagem para caber."""
    w, h = img.size
    out = nova(w + abs(dx), h + abs(dy))
    m = opaco(img)
    som = nova(w, h)
    som = pintar_mascara(som, m, nome)
    ox, oy = max(0, -dx), max(0, -dy)
    out.alpha_composite(som, (ox + dx, oy + dy))
    out.alpha_composite(img, (ox, oy))
    return out


def faixas_v(img, x0, x1, faixas, y_fim, trans=6):
    """Faixas chapadas; o pontilhado Bayer so aparece em 'trans' linhas (<= 8) em volta de cada troca de cor.
    faixas: [(y_inicio, nome), ...] crescente; vai ate y_fim."""
    assert trans <= 8
    a = arr(img)
    for y in range(faixas[0][0], y_fim + 1):
        i = max(k for k in range(len(faixas)) if faixas[k][0] <= y)
        nome = faixas[i][1]
        for j in (i, i + 1):   # troca logo acima (j = i) ou logo abaixo (j = i + 1)
            if 1 <= j < len(faixas):
                b = faixas[j][0]
                ini = b - trans // 2
                if ini <= y < ini + trans:
                    t = (y - ini + 0.5) / trans
                    ca, cb = faixas[j - 1][1], faixas[j][1]
                    linha = np.where(t * 16 > BAYER[y % 4][np.arange(x0, x1 + 1) % 4] + 0.5, 1, 0)
                    for x, v in zip(range(x0, x1 + 1), linha):
                        a[y, x] = cor(cb if v else ca)
                    break
        else:
            a[y, x0:x1 + 1] = cor(nome)
    return de_arr(a)


def pontilhar(img, m, nome, nivel=8):
    """Pinta 'nivel'/16 dos pixels da mascara m com a cor (Bayer)."""
    a = arr(img)
    h, w = m.shape
    yy, xx = np.mgrid[0:h, 0:w]
    sel = m & (BAYER[yy % 4, xx % 4] < nivel)
    a[sel] = cor(nome)
    return de_arr(a)


def de_desenho(linhas, mapa):
    """Monta uma imagem de uma lista de strings; mapa: caractere -> nome de cor ('.' e ' ' = transparente)."""
    h, w = len(linhas), max(len(s) for s in linhas)
    img = nova(w, h)
    px = img.load()
    for y, s in enumerate(linhas):
        for x, ch in enumerate(s):
            if ch in mapa:
                px[x, y] = cor(mapa[ch])
    return img


def checar_paleta(img, nome):
    a = arr(img)
    op = a[:, :, 3] > 0
    if np.any((a[:, :, 3] != 0) & (a[:, :, 3] != 255)):
        raise SystemExit(f"ERRO de paleta: {nome} tem alfa parcial")
    cores = {tuple(c) for c in a[op][:, :3].reshape(-1, 3).tolist()} if op.any() else set()
    fora = cores - set(PALETA.values())
    if fora:
        raise SystemExit(f"ERRO de paleta: {nome} usa cor fora da lista: {sorted(fora)[:5]}")


# ----------------------------------------------------------------------------------------------------------
# Fontes (bitmap FNT v2; glifo = grupo 0, numero = codigo Unicode; o motor aceita ate 65535)
# ----------------------------------------------------------------------------------------------------------
LETRAS = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "J": ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    "!": ["#", "#", "#", "#", "#", ".", "#"],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    ".": [".", ".", ".", ".", ".", ".", "#"],
    ",": ["..", "..", "..", "..", "..", ".#", "#."],
    "-": ["...", "...", "...", "###", "...", "...", "..."],
    ":": [".", ".", "#", ".", ".", "#", "."],
    "'": ["#", "#", ".", ".", ".", ".", "."],
    "/": ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."],
    "%": ["##..#", "##.#.", "...#.", "..#..", ".#...", ".#.##", "#..##"],
    "(": [".#", "#.", "#.", "#.", "#.", "#.", ".#"],
    ")": ["#.", ".#", ".#", ".#", ".#", ".#", "#."],
    "•": ["..", "..", "..", "##", "##", "..", ".."],
}
ACENTOS = {  # 2 linhas acima da letra
    "agudo": ["...#.", "..#.."], "grave": [".#...", "..#.."], "circ": ["..#..", ".#.#."],
    "til": [".##.#", "#..#."],
}
ACENTUADAS = {
    "Á": ("A", "agudo"), "À": ("A", "grave"), "Â": ("A", "circ"), "Ã": ("A", "til"), "É": ("E", "agudo"),
    "Ê": ("E", "circ"), "Í": ("I", "agudo"), "Ó": ("O", "agudo"), "Ô": ("O", "circ"), "Õ": ("O", "til"),
    "Ú": ("U", "agudo"), "Ç": ("C", None),
}

DIGITOS = {  # 6x10, traco de 2 px, para o relogio e o combo
    "0": [".####.", "##..##", "##..##", "##.###", "##.###", "###.##", "###.##", "##..##", "##..##", ".####."],
    "1": ["..##..", ".###..", "####..", "..##..", "..##..", "..##..", "..##..", "..##..", "..##..", "######"],
    "2": [".####.", "##..##", "....##", "....##", "...##.", "..##..", ".##...", "##....", "##....", "######"],
    "3": [".####.", "##..##", "....##", "....##", "..###.", "....##", "....##", "....##", "##..##", ".####."],
    "4": ["...##.", "..###.", ".####.", "##.##.", "##.##.", "######", "...##.", "...##.", "...##.", "...##."],
    "5": ["######", "##....", "##....", "#####.", "....##", "....##", "....##", "....##", "##..##", ".####."],
    "6": [".####.", "##..##", "##....", "##....", "#####.", "##..##", "##..##", "##..##", "##..##", ".####."],
    "7": ["######", "....##", "....##", "...##.", "...##.", "..##..", "..##..", "..##..", "..##..", "..##.."],
    "8": [".####.", "##..##", "##..##", "##..##", ".####.", "##..##", "##..##", "##..##", "##..##", ".####."],
    "9": [".####.", "##..##", "##..##", "##..##", "##..##", ".#####", "....##", "....##", "##..##", ".####."],
    ":": ["..", "..", "##", "##", "..", "..", "##", "##", "..", ".."],
}


def glifo_letra(ch, com_acento_espaco):
    """Bitmap (lista de strings) da letra; com_acento_espaco = 2 linhas em cima e 1 embaixo (cedilha)."""
    base_ch = ch.upper()
    acento = None
    if base_ch in ACENTUADAS:
        base_ch, acento = ACENTUADAS[base_ch]
    base = LETRAS[base_ch]
    w = len(base[0])
    if not com_acento_espaco:
        return base
    cima = [("." * w), ("." * w)]
    if acento:
        cima = [s[:w].ljust(w, ".") for s in ACENTOS[acento]]
    baixo = ["." * w]
    if ch.upper() == "Ç":
        baixo = ["..##."]
    return cima + base + baixo


def render_glifo(bits, corpo, sombra, alto_luz=None):
    img = de_desenho(bits, {"#": corpo})
    if alto_luz:
        a = arr(img)
        m = a[:, :, 3] > 0
        topo = m & ~deslocar(m, 0, 1)   # pixel sem nada em cima
        a[topo] = cor(alto_luz)
        img = de_arr(a)
    return com_sombra(img, sombra, 1, 1)


def chars_texto():
    s = [c for c in LETRAS] + list(ACENTUADAS)
    return s + [c.lower() for c in s if c.isalpha() and c.lower() != c]


def fonte_texto(nome, com_acentos, corpo, sombra, alto_luz=None):
    """Fonte de letras (tabuleta). Devolve (sprites, def_texto, glifos_logicos)."""
    glifos = {}
    for ch in chars_texto():
        if not com_acentos and (ch.upper() in ACENTUADAS or ch == "•"):
            continue
        glifos[ch] = render_glifo(glifo_letra(ch, com_acentos), corpo, sombra, alto_luz)
    alto = 11 if com_acentos else 8
    for ch, g in list(glifos.items()):
        if g.height != alto:
            raise SystemExit(f"glifo {ch!r} de {nome} com altura {g.height} != {alto}")
    sprites = [(0, ord(ch), ampliar(g), 0, 0) for ch, g in glifos.items()]
    d = def_fonte(nome, 16, alto * ESCALA, 4)
    return sprites, d, glifos


def fonte_numero(nome, corpo, alto_luz, base_esc):
    glifos = {}
    for ch, bits in DIGITOS.items():
        img = de_desenho(bits, {"#": corpo})
        a = arr(img)
        m = a[:, :, 3] > 0
        h = len(bits)
        yy = np.mgrid[0:h, 0:len(bits[0])][0]
        a[m & (yy <= 1)] = cor(alto_luz)
        a[m & (yy >= h - 2)] = cor(base_esc)
        img = de_arr(a)
        g = nova(img.width + 2, img.height + 2)
        g.alpha_composite(img, (1, 1))
        glifos[ch] = contorno(g, "breu", diag=True)
    glifos["o"] = glifos["0"]   # tempo infinito
    sprites = [(0, ord(ch), ampliar(g), 0, 0) for ch, g in glifos.items()]
    return sprites, def_fonte(nome, 32, 12 * ESCALA, 4), glifos


SEGMENTOS = {  # digito grande do relogio: corpo 10x16, traco de 3 px (a b c d e f g = sete segmentos)
    "a": (0, 0, 9, 2), "b": (7, 0, 9, 8), "c": (7, 7, 9, 15), "d": (0, 13, 9, 15), "e": (0, 7, 2, 15),
    "f": (0, 0, 2, 8), "g": (0, 7, 9, 8),
}
DIG_SEG = {"0": "abcdef", "2": "abged", "3": "abgcd", "4": "fbgc", "5": "afgcd", "6": "afgecd", "7": "abc",
           "8": "abcdefg", "9": "abfgcd"}
RELOGIO_GLIFO = (12, 18)   # com o contorno de 1 px
RELOGIO_VAO = 2            # espaco logico entre os dois digitos (par: o numero fica centrado na grade)


def digito_grande(ch, corpo, alto_luz, base_esc):
    m = np.zeros((16, 10), bool)
    if ch == "1":
        m[0:16, 4:7] = True
        m[1:4, 2:4] = True
        m[13:16, 2:9] = True
    else:
        for s in DIG_SEG[ch]:
            x0, y0, x1, y1 = SEGMENTOS[s]
            m[y0:y1 + 1, x0:x1 + 1] = True
        for (y, x) in [(0, 0), (0, 9), (15, 0), (15, 9)]:   # quinas arredondadas
            m[y, x] = False
    a = np.zeros((16, 10, 4), np.uint8)
    a[m] = cor(corpo)
    a[m & (np.arange(16)[:, None] <= 1)] = cor(alto_luz)
    a[m & (np.arange(16)[:, None] >= 14)] = cor(base_esc)
    g = nova(12, 18)
    g.alpha_composite(de_arr(a), (1, 1))
    return contorno(g, "breu", diag=True)


def fonte_relogio(nome, corpo, alto_luz, base_esc, zero_na_frente):
    """Relogio de 2 digitos, 48x72 cada. O motor escreve o tempo sem zero a esquerda; a fonte de alerta so e
    usada abaixo de 10 s, entao cada glifo dela ja vem desenhado como '0' + digito (o 8 aparece como 08)."""
    w, h = RELOGIO_GLIFO
    glifos = {}
    for ch in "0123456789":
        g = digito_grande(ch, corpo, alto_luz, base_esc)
        if zero_na_frente:
            dois = nova(2 * w + RELOGIO_VAO, h)
            dois.alpha_composite(digito_grande("0", corpo, alto_luz, base_esc), (0, 0))
            dois.alpha_composite(g, (w + RELOGIO_VAO, 0))
            g = dois
        glifos[ch] = g
    glifos["o"] = glifos["0"]   # tempo infinito
    sprites = [(0, ord(ch), ampliar(g), 0, 0) for ch, g in glifos.items()]
    return sprites, def_fonte(nome, w * ESCALA, h * ESCALA, RELOGIO_VAO * ESCALA), glifos


def def_fonte(nome, larg_espaco, alto, espaco):
    return (f"; Fonte {nome} do Nazafight, desenhada por codigo (ferramentas/gerar_layout.py)\n"
            f"[FNT v2]\nfntversion = 2,00\nname = \"{nome}\"\nauthor = \"Nazafight\"\n\n"
            f"[Def]\nType = bitmap\nBankType = palette\nSize = {larg_espaco},{alto}\n"
            f"Spacing = {espaco},0\nOffset = 0,0\nFile = {nome}.sff\n")


# ----------------------------------------------------------------------------------------------------------
# Motivos de Maragogipinho: espiral de tabatinga, azulejo (so atras do relogio), caxixi
# ----------------------------------------------------------------------------------------------------------
ESPIRAL = [".###.", "#...#", "#.#.#", "#..#.", ".#..."]


def friso_espiral(img, x0, y0, x1, nome, passo=6, meia=True, traco=False):
    """Fileira de espirais pequenas (5x5) de x0 a x1; meia=True pontilha 50% (tinta rala de tabatinga).
    traco=True espaca as espirais (passo 14) e poe um traco de 4 px entre elas, para nao ler como texto."""
    px = img.load()
    if traco:
        passo = 14
        for bx in range(x0, x1 - 4, passo):
            for x in range(bx + 7, min(bx + 11, x1)):
                if px[x, y0 + 2][3] > 0:
                    px[x, y0 + 2] = cor(nome)
    for bx in range(x0, x1 - 4, passo):
        for yy, s in enumerate(ESPIRAL):
            for xx, ch in enumerate(s):
                x, y = bx + xx, y0 + yy
                if ch == "#" and (not meia or (x + y) % 2 == 0) and px[x, y][3] > 0:
                    px[x, y] = cor(nome)


def azulejo_tile():
    q = ["AttA", "tAtt", "ttAt", "AttA"]
    linhas = [s + s[::-1] for s in q]
    linhas += linhas[::-1]
    return de_desenho(linhas, {"A": "azulejo", "t": "tabatinga"})


def caxixi(w, h, corpo, luz, sombra, borda="breu", friso=None, brilho=None):
    """Moringa/caxixi visto de lado: boca, pescoco curto, bojo redondo. Devolve imagem w x h (logica)."""
    img = nova(w, h)
    d = ImageDraw.Draw(img)
    cx = (w - 1) / 2
    boca_w = max(3, w // 2 - (0 if w < 10 else 1))
    pesc_w = max(2, boca_w - 2)
    boca_h = max(1, h // 10)
    pesc_h = max(1, h // 8)
    bx0 = int(round(cx - (boca_w - 1) / 2))
    px0 = int(round(cx - (pesc_w - 1) / 2))
    bojo_y0 = boca_h + pesc_h - 1
    d.ellipse([0, bojo_y0, w - 1, h - 1], fill=cor(corpo))
    d.rectangle([px0, boca_h, px0 + pesc_w - 1, bojo_y0 + 1], fill=cor(corpo))
    d.rectangle([bx0, 0, bx0 + boca_w - 1, boca_h - 1], fill=cor(corpo))
    a = arr(img)
    m = a[:, :, 3] > 0
    yy, xx = np.mgrid[0:h, 0:w]
    ry = (h - 1 - bojo_y0) / 2
    cy = bojo_y0 + ry
    rel = (xx - cx) / max(1, (w - 1) / 2)
    rely = (yy - cy) / max(1, ry)
    a[m & (rel > 0.42) & (yy >= bojo_y0)] = cor(sombra)
    a[m & (rely > 0.6) & (rel > -0.2) & (yy >= bojo_y0)] = cor(sombra)
    a[m & (rel < -0.45) & (rely < 0.35) & (yy >= bojo_y0)] = cor(luz)
    img = de_arr(a)
    if friso:
        fy = bojo_y0 + max(1, int(ry * 0.45))
        px = img.load()
        for x in range(1, w - 1):
            if px[x, fy][3] and (x % 2 == 0):
                px[x, fy] = cor(friso)
    if brilho and w >= 8:
        px = img.load()
        bx, by = int(cx - (w - 1) * 0.28), bojo_y0 + max(1, int(ry * 0.35))
        px[bx, by] = cor(brilho)
        if w >= 16:
            px[bx + 1, by] = cor(brilho)
    m = opaco(img)
    borda_m = m & ~erodir(m, diag=False)
    return pintar_mascara(img, borda_m, borda)


# ----------------------------------------------------------------------------------------------------------
# HUD (fight.sff)
# ----------------------------------------------------------------------------------------------------------
TRILHO_ORIGEM = (8, 2)   # onde comeca a prancha dentro do sprite do trilho (P1); e o eixo do sprite
PRANCHA = (104, 14)      # prancha de saveiro (logico); a vida corre por dentro dela, 4 px longe de cada ponta
VIDA_W = PRANCHA[0] - 8  # 96 -> 384 px
TARJA = (8, 18, 84, 8)   # tarja do nome e das vitorias (x, y, w, h) no sprite do trilho: tela y 88 a 120, 32 px


def anel_hud(img, m):
    """Contorno do HUD sobre fundo qualquer: 1 px de tabatinga na borda de dentro e 2 px de breu por fora."""
    a = arr(img)
    a[m & ~erodir(m, diag=True)] = cor("tabatinga")
    fora = dilatar(dilatar(m, diag=True), diag=True) & ~m
    a[fora] = cor("breu")
    return de_arr(a)


def trilho_vida():
    """Prancha de saveiro 104x14 com alca de moringa em meia-lua na ponta de fora (esquerda = P1; e nela que o
    retrato encosta), contorno breu de 2 px + linha de tabatinga, vazio em breu liso e, colada embaixo, a tarja
    de madeira de 32 px do nome e das vitorias. 114x27."""
    ox, oy = TRILHO_ORIGEM
    pw, ph = PRANCHA
    W, H = ox + pw + 2, 27
    img = nova(W, H)
    d = ImageDraw.Draw(img)
    # alca: meia-lua de barro colada na prancha
    alca = nova(W, H)
    da = ImageDraw.Draw(alca)
    da.ellipse([2, oy + 1, 15, oy + 12], fill=cor("taua"))
    da.ellipse([5, oy + 4, 14, oy + 9], fill=(0, 0, 0, 0))
    a = arr(alca)
    a[:, ox - 2:] = 0
    m_alca = a[:, :, 3] > 0
    yy = np.mgrid[0:H, 0:W][0]
    a[m_alca & (yy <= oy + 4)] = cor("taua_vivo")
    a[m_alca & (yy >= oy + 10)] = cor("taua_esc")
    alca = de_arr(a)
    # prancha
    d.rectangle([ox, oy, ox + pw - 1, oy + ph - 1], fill=cor("madeira"))
    d.line([ox, oy + 1, ox + pw - 1, oy + 1], fill=cor("madeira_cl"))
    d.line([ox, oy + 12, ox + pw - 1, oy + 12], fill=cor("barro"))
    px = img.load()
    for x in range(ox + 1, ox + pw - 1):   # faixa pintada de saveiro: tauá vivo embaixo
        if (x - ox) % 6 in (4, 5, 0):
            px[x, oy + 12] = cor("taua_vivo")
    d.rectangle([ox + 4, oy + 2, ox + pw - 5, oy + 11], fill=cor("breu"))   # vazio: breu liso
    m_prancha = opaco(img)
    img = anel_hud(img, m_prancha)
    # a alca entra por baixo do contorno e ganha o proprio contorno breu de 2 px
    m_a = opaco(alca) & ~dilatar(dilatar(m_prancha))
    alca = de_arr(np.where(m_a[:, :, None], arr(alca), 0))
    borda_a = dilatar(dilatar(m_a, diag=False), diag=False) & ~m_a & ~opaco(img)
    a = arr(img)
    a[m_a] = arr(alca)[m_a]
    a[borda_a] = cor("breu")
    img = de_arr(a)
    # tarja de madeira do nome e das bolinhas, colada no contorno de baixo do trilho (32 px de altura: a letra
    # de tabuleta de 8 linhas ocupa a tarja inteira, com a sombra na ultima)
    tx, ty, tw, th = TARJA
    d = ImageDraw.Draw(img)
    d.rectangle([tx - 1, ty, tx + tw, ty + th], fill=cor("breu"))
    d.rectangle([tx, ty, tx + tw - 1, ty + th - 1], fill=cor("madeira"))
    d.line([tx, ty + th - 1, tx + tw - 1, ty + th - 1], fill=cor("barro"))
    return img


FRISO_VIDA = "###.#..."   # a espiral achatada numa fileira so, no topo do enchimento


def enchimento_vida(corpo, escuro, friso):
    """Vida 96x10: corpo liso, 1 fileira de friso no topo (y +1) e 2 de sombra embaixo. Sem textura no meio."""
    img = nova(VIDA_W, 10)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, VIDA_W - 1, 9], fill=cor(corpo))
    d.line([0, 8, VIDA_W - 1, 8], fill=cor(escuro))
    d.line([0, 9, VIDA_W - 1, 9], fill=cor(escuro))
    px = img.load()
    for x in range(VIDA_W):
        if FRISO_VIDA[x % len(FRISO_VIDA)] == "#":
            px[x, 1] = cor(friso)
    return img


def fantasma_vida():
    """Dano fantasma: farinha lisa (desce com atraso atras da vida)."""
    img = nova(VIDA_W, 10)
    ImageDraw.Draw(img).rectangle([0, 0, VIDA_W - 1, 9], fill=cor("farinha"))
    return img


MORINGA = [   # moringa de estoque (antes do contorno): T boca, C corpo, L brilho, S sombra; alca do lado
    "..TTTT...",
    "...CC....",
    "..CCCC...",
    ".CCCCCCC.",
    "CLCCCCC.C",
    "CCCCCCS.C",
    "CCCCCSSCC",
    "CCCCSSS..",
    ".CCSSS...",
    "..SSS....",
]
ESTOQUE_CORES = {   # cru = silhueta apagada; quente = no forno; cozido = tauá com brilho de 1 px
    "cru": {"T": "madeira", "C": "madeira", "L": "madeira", "S": "madeira"},
    "quente": {"T": "madeira_cl", "C": "taua_esc", "L": "taua_esc", "S": "barro"},
    "cozido": {"T": "tabatinga", "C": "taua", "L": "taua_vivo", "S": "taua_esc"},
}


def estoque(estado):
    """Moringa de estoque 11x12 (com contorno breu): gargalo de 2 px, boca, alca lateral."""
    base = de_desenho(MORINGA, ESTOQUE_CORES[estado])
    g = nova(base.width + 2, base.height + 2)
    g.alpha_composite(base, (1, 1))
    return contorno(g, "breu", diag=False)


# placa de breu do poder (P1), pequena e no canto como no genero: abraca so o trilho, as 3 moringas e o numero
# do nivel. 109x12 logico = 436x48, de y 668 a 716; o resto do rodape fica livre (os pes dos lutadores aparecem).
PLACA = {"w": 109, "h": 12, "trilho": (2, 3), "trilho_w": 64, "estoque_x": 68, "estoque_y": 0,
         "estoque_passo": 10, "numero_x": 100, "numero_y": 0}
PODER_W = PLACA["trilho_w"] - 6   # enchimento: 58 -> 232 px


def trilho_poder():
    w = PLACA["trilho_w"]
    img = nova(w, 6)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, 5], fill=cor("madeira"))   # canaleta de madeira inteira (nao so as pontas)
    d.line([1, 0, w - 2, 0], fill=cor("madeira_cl"))
    d.rectangle([3, 1, w - 4, 4], fill=cor("breu"))
    px = img.load()
    for x in (0, w - 1):
        px[x, 0] = (0, 0, 0, 0)
        px[x, 5] = (0, 0, 0, 0)
    return img


def composto_poder(nivel_x2):
    """Placa de breu (friso de madeira clara por dentro) com o trilho de poder e 3 moringas; nivel_x2 =
    poder/500 (0..6). P1: trilho a esquerda, moringas e numero do nivel a direita. O numero e o counter do motor."""
    P = PLACA
    img = nova(P["w"], P["h"])
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, P["w"] - 1, P["h"] - 1], radius=2, fill=cor("breu"))
    d.line([2, 1, P["w"] - 3, 1], fill=cor("madeira_cl"))
    d.line([2, P["h"] - 2, P["w"] - 3, P["h"] - 2], fill=cor("barro"))
    img.alpha_composite(trilho_poder(), P["trilho"])
    cozidos = nivel_x2 // 2
    for i in range(3):
        if i < cozidos:
            est = "cozido"
        elif i == cozidos and nivel_x2 % 2 == 1:
            est = "quente"
        else:
            est = "cru"
        img.alpha_composite(estoque(est), (P["estoque_x"] + P["estoque_passo"] * i, P["estoque_y"]))
    return img


def enchimento_poder(corpo, luz, faisca):
    img = nova(PODER_W, 4)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, PODER_W - 1, 3], fill=cor(corpo))
    d.line([0, 0, PODER_W - 1, 0], fill=cor(luz))
    px = img.load()
    for x in range(PODER_W):
        if x % 7 == 3:
            px[x, 1] = cor(faisca)
        if x % 7 == 4:
            px[x, 1] = cor(luz)
        if x % 9 == 0:
            px[x, 3] = cor(luz)
    return img


def cacos(q):
    """Caxixi de estoque quebrando, 4 quadros. Nao ligado no v1.0.0 (o motor nao avisa o gasto do estoque)."""
    a = arr(estoque("cozido"))
    img = nova(26, 26)
    pedacos = [(0, 0, 5, 6), (5, 0, 11, 6), (0, 6, 5, 12), (5, 6, 11, 12)]
    desl = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    for (x0, y0, x1, y1), (dx, dy) in zip(pedacos, desl):
        p = de_arr(a[y0:y1, x0:x1].copy())
        k = q * 2
        img.alpha_composite(p, (7 + x0 + dx * k, 7 + y0 + dy * k))
    if q >= 2:
        img = pontilhar(img, dilatar(opaco(img)) & ~opaco(img), "farinha", 4 + q)
    return img


FACE = 29   # moldura logica: 2 px de anel + 25 px de dentro (o retrato 9000,0 de 25x25 cabe inteiro, escala 4)


def moldura_face(top=True):
    """Anel de barro 29x29 (top) ou fundo liso de rio (bg), que separa qualquer retrato do cenario."""
    n = FACE - 1
    img = nova(FACE, FACE)
    d = ImageDraw.Draw(img)
    if top:
        d.rectangle([0, 0, n, n], fill=cor("taua"))
        d.rectangle([2, 2, n - 2, n - 2], fill=(0, 0, 0, 0))
        d.line([1, 1, n - 1, 1], fill=cor("taua_vivo"))
        d.line([1, 1, 1, n - 1], fill=cor("taua_vivo"))
        d.line([1, n - 1, n - 1, n - 1], fill=cor("taua_esc"))
        d.line([n - 1, 1, n - 1, n - 1], fill=cor("taua_esc"))
        d.rectangle([0, 0, n, n], outline=cor("breu"))
        px = img.load()
        for (cx, cy) in [(0, 0), (n, 0), (0, n), (n, n)]:
            sx = 1 if cx == 0 else -1
            sy = 1 if cy == 0 else -1
            px[cx, cy] = (0, 0, 0, 0)
            for (x, y) in [(1, 1), (2, 1), (3, 1), (1, 2), (1, 3), (3, 2), (2, 3), (3, 3)]:
                px[cx + sx * x, cy + sy * y] = cor("tabatinga")
            px[cx + sx * 2, cy + sy * 2] = cor("taua_esc")
        return img
    d.rectangle([1, 1, n - 1, n - 1], fill=cor("rio"))
    return img


def rachaduras_face():
    img = nova(FACE, FACE)
    d = ImageDraw.Draw(img)
    for pts in [[(3, 2), (8, 9), (7, 14), (12, 19), (11, 25)], [(8, 9), (14, 8), (20, 4)],
                [(12, 19), (18, 18), (24, 23)], [(7, 14), (3, 16)]]:
        d.line(pts, fill=cor("breu"))
    return img


RELOGIO = {"w": 48, "h": 36, "pote_x": 7, "pote_w": 34, "pote_h": 32, "placa": (9, 9, 38, 28)}


def relogio():
    """Caxixi brunido 34x32 (contorno breu de 2 px + linha de tabatinga) com a boca de breu onde cabem os 2
    digitos grandes. 48x36. (O azulejo saiu: lia como pixel solto e nao e fato de Nazare.)"""
    R = RELOGIO
    img = nova(R["w"], R["h"])
    # pote: boca, pescoco curto, bojo de superelipse (largo embaixo para caber a placa)
    w, h = R["pote_w"], R["pote_h"]
    pote = np.zeros((h, w), bool)
    yy, xx = np.mgrid[0:h, 0:w]
    cx = (w - 1) / 2
    pote[0:3, 9:25] = True
    pote[3:5, 11:23] = True
    cy, ry, rx = 18.0, 13.5, w / 2
    pote |= (np.abs((xx - cx) / rx) ** 4 + np.abs((yy - cy) / ry) ** 4) <= 1.0
    a = np.zeros((h, w, 4), np.uint8)
    a[pote] = cor("taua")
    rel = (xx - cx) / rx
    a[pote & (rel > 0.55) & (yy >= 5)] = cor("taua_esc")
    a[pote & (yy >= 29)] = cor("taua_esc")
    a[pote & (rel < -0.6) & (yy >= 6) & (yy <= 20)] = cor("taua_vivo")
    a[0:1, 10:24] = cor("tabatinga")    # boca de tabatinga
    a[2, 9:25] = cor("taua_esc")
    a[7, 4:6] = cor("farinha")          # brilho do brunido
    pote_img = de_arr(a)
    px0, py0 = R["pote_x"], 2
    full = nova(R["w"], R["h"])
    full.alpha_composite(pote_img, (px0, py0))
    m = opaco(full)
    full = anel_hud(full, m)
    # placa dos digitos (boca de breu)
    d = ImageDraw.Draw(full)
    x0, y0, x1, y1 = R["placa"]
    d.rounded_rectangle([x0, y0 + py0, x1, y1 + py0], radius=3, fill=cor("breu"))
    d.line([x0 + 3, y1 + py0 + 1, x1 - 3, y1 + py0 + 1], fill=cor("tabatinga"))   # friso embaixo da boca
    img.alpha_composite(full)
    return img


def bolinha(cozida):
    """Vitoria. Cozida: tauá com aro de tabatinga e brilho de tauá vivo. Crua: barro cru, madeira clara com
    contorno breu (aparece sobre a tarja de madeira)."""
    img = nova(6, 6)
    d = ImageDraw.Draw(img)
    px = img.load()
    if cozida:
        d.ellipse([0, 0, 5, 5], fill=cor("tabatinga"))
        d.ellipse([1, 1, 4, 4], fill=cor("taua"))
        px[2, 2] = cor("taua_vivo")
        px[2, 1] = cor("taua_vivo")
        px[3, 4] = cor("taua_esc")
        px[4, 3] = cor("taua_esc")
    else:
        d.ellipse([0, 0, 5, 5], fill=cor("breu"))
        d.ellipse([1, 1, 4, 4], fill=cor("madeira_cl"))
        px[2, 1] = cor("tabatinga")
        px[1, 2] = cor("tabatinga")
    return img


def texto_bits(texto, escala, corpo, sombra=None, desloc=1, espaco=1):
    """Escreve com as LETRAS 5x7 ampliadas 'escala' vezes (ainda na grade logica)."""
    glifos = []
    for ch in texto:
        if ch == " ":
            glifos.append(None)
            continue
        g = de_desenho(glifo_letra(ch, False), {"#": corpo})
        glifos.append(g.resize((g.width * escala, g.height * escala), Image.NEAREST))
    w = sum((g.width if g else 3 * escala) for g in glifos) + espaco * escala * (len(glifos) - 1)
    img = nova(w, 7 * escala)
    x = 0
    for g in glifos:
        if g:
            img.alpha_composite(g, (x, 0))
            x += g.width
        else:
            x += 3 * escala
        x += espaco * escala
    if sombra:
        img = com_sombra(img, sombra, desloc, desloc)
    return img


def tabuleta(w, h, texto, cor_letra, escala=2):
    img = nova(w, h)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], fill=cor("madeira"))
    for y in range(2, h - 2):
        for x in range(2, w - 2):
            if (x * 7 + (y // 3) * 13) % 23 == 0:
                d.line([x, y, min(w - 3, x + 5), y], fill=cor("madeira_cl"))
    d.line([1, 1, w - 2, 1], fill=cor("madeira_cl"))
    d.line([1, h - 2, w - 2, h - 2], fill=cor("barro"))
    d.rectangle([0, 0, w - 1, h - 1], outline=cor("breu"))
    px = img.load()
    for (x, y) in [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]:
        px[x, y] = cor("tabatinga")
    if texto:
        t = texto_bits(texto, escala, cor_letra, "barro", 1)
        img.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2))
    return img


def letreiro_ko(q):
    """'K.O.' de barro rachando, quadro q de 0 a 5."""
    letras = texto_bits("K.O.", 4, "taua", None, espaco=1)
    base = nova(letras.width + 6, letras.height + 6)
    base.alpha_composite(letras, (2, 1))
    a = arr(base)
    m = a[:, :, 3] > 0
    topo = m & ~deslocar(m, 0, 1)
    a[topo] = cor("taua_vivo")
    dir_ = m & ~deslocar(m, -1, 0)
    a[dir_ & ~topo] = cor("taua_esc")
    base = contorno(de_arr(a), "barro", diag=True)
    base = com_sombra(base, "breu", 2, 2)
    w, h = base.size
    out = nova(w + 8, h + 8)
    if q < 4:
        out.alpha_composite(base, (4, 4))
    else:   # os pedacos se separam
        meio = w // 2
        k = 1 if q == 4 else 2
        out.alpha_composite(base.crop((0, 0, meio, h)), (4 - k, 4 + k - 1))
        out.alpha_composite(base.crop((meio, 0, w, h)), (4 + meio + k, 4 + k))
    racha = [[(6, 4), (10, 12), (8, 20), (13, 28)], [(36, 3), (33, 11), (38, 19), (35, 30)],
             [(50, 6), (56, 14), (52, 24)], [(10, 12), (18, 14)], [(38, 19), (45, 21)]]
    om = opaco(out)
    for pts in racha[:[0, 1, 2, 3, 5, 5][q]]:
        lin = nova(*out.size)
        ImageDraw.Draw(lin).line([(x + 4, y + 4) for x, y in pts], fill=cor("breu"))
        out = de_arr(np.where((opaco(lin) & om)[:, :, None], arr(lin), arr(out)))
    if q >= 3:
        rnd = random.Random(70 + q)
        nuvem = nova(*out.size)
        dp = ImageDraw.Draw(nuvem)
        for _ in range(10 + 6 * (q - 3)):
            x, y = rnd.randrange(0, out.width), rnd.randrange(out.height - 14, out.height)
            r = rnd.randrange(1, 3)
            dp.ellipse([x - r, y - r, x + r, y + r], fill=cor("farinha"))
        poeira = pontilhar(nova(*out.size), opaco(nuvem), "farinha", {3: 12, 4: 10, 5: 6}[q])
        poeira.alpha_composite(out)
        out = poeira
    return out


# ----------------------------------------------------------------------------------------------------------
# Titulo: o Jaguaripe ao fim da tarde (system.sff)
# ----------------------------------------------------------------------------------------------------------
HORIZONTE = 118  # linha d'agua, em pixels logicos
SOL = (236, 88)   # o sol se pondo atras da ponte: metade acima do parapeito, o resto escondido pelo tabuleiro


def ceu():
    img = faixas_v(nova(320, 180), 0, 319, [(0, "taua_esc"), (16, "taua"), (40, "taua_vivo"), (68, "ceu"),
                                            (94, "dende"), (110, "farinha")], 179, trans=6)
    sx, sy = SOL
    halo = nova(320, 180)
    ImageDraw.Draw(halo).ellipse([sx - 22, sy - 22, sx + 22, sy + 22], fill=cor("farinha"))
    img = pontilhar(img, opaco(halo), "farinha", 6)
    d = ImageDraw.Draw(img)
    d.ellipse([sx - 13, sy - 13, sx + 13, sy + 13], fill=cor("dende"))
    d.ellipse([sx - 11, sy - 11, sx + 11, sy + 11], fill=cor("farinha"))
    d.ellipse([sx - 7, sy - 9, sx + 5, sy - 3], fill=cor("tabatinga"))
    return img


def nuvens():
    """Faixa de nuvens compridas (tile horizontal, anda devagar)."""
    img = nova(320, 70)
    d = ImageDraw.Draw(img)
    rnd = random.Random(11)
    for (x, y, w) in [(8, 10, 70), (120, 4, 52), (210, 16, 88), (40, 34, 46), (150, 42, 64), (262, 52, 50),
                      (90, 58, 40)]:
        for i in range(3):
            yy = y + i * 2
            x0 = x + rnd.randrange(0, 8) + i * 3
            x1 = x + w - rnd.randrange(0, 10) - i * 5
            d.line([x0, yy, x1, yy], fill=cor("farinha" if i == 0 else "ceu"))
            d.line([x0 + 2, yy + 1, x1 - 3, yy + 1], fill=cor("tabatinga" if i == 0 else "taua_vivo"))
        d.line([x + 6, y + 6, x + w - 14, y + 6], fill=cor("taua_vivo"))
    return img


FACHADAS = [("tabatinga", "madeira_cl"), ("farinha", "madeira_cl"), ("taua_vivo", "taua"), ("tabatinga", "madeira_cl"),
            ("farinha", "madeira_cl"), ("taua_vivo", "taua")]   # o azul de rio entra numa casa so (CASA_AZUL)
CASA_AZUL = 5


def casa(w, andares, parede, sombra_parede, acesas=()):
    """Sobrado: telhado capa-canal em tauá escuro (3 linhas) com fileira de sombra embaixo do beiral, janelas
    2x3 em ritmo fixo de 4 px, porta no terreo. A base da imagem e o chao. acesas: indices de janela com luz."""
    hp = 6 * andares + 1
    img = nova(w + 2, hp + 3)
    d = ImageDraw.Draw(img)
    d.rectangle([1, 3, w, hp + 2], fill=cor(parede))
    d.line([w, 3, w, hp + 2], fill=cor(sombra_parede))
    d.line([1, 3, w, 3], fill=cor(sombra_parede))          # sombra do beiral
    d.rectangle([2, 0, w - 1, 0], fill=cor("taua_esc"))     # cumeeira
    d.rectangle([0, 1, w + 1, 2], fill=cor("taua_esc"))     # beiral
    for x in range(0, w + 2, 2):                            # canal da telha
        d.point((x, 1), fill=cor("barro"))
    d.line([0, 2, w + 1, 2], fill=cor("barro"))
    k = 0
    base = hp + 2
    for andar in range(andares):
        jy = base - 6 * (andar + 1) + 2
        for jx in range(3, w - 1, 4):
            if andar == 0 and abs(jx + 1 - (w + 1) / 2) < 2:
                continue                                     # lugar da porta
            d.rectangle([jx, jy, jx + 1, jy + 2], fill=cor("dende" if k in acesas else "barro"))
            k += 1
    px_ = (w + 1) // 2
    d.rectangle([px_, base - 3, px_ + 1, base], fill=cor("madeira"))
    return img


def colar_casa(img, c, x, chao):
    img.alpha_composite(c, (x, chao - c.height + 1))


def cidade():
    """Morros, Cristo pequeno no Morro do Silencio, casario descendo a ladeira em degraus ate o cais, torre da
    Matriz, ponte de pedra com cabeceira e talha-mar e um trecho de casario na margem direita."""
    img = nova(320, 180)
    d = ImageDraw.Draw(img)
    # morro distante (silhueta de mangue com neblina)
    for x in range(320):
        y = int(100 + 4 * np.sin(x / 23.0) + 3 * np.sin(x / 9.0 + 1.3))
        d.line([x, y, x, HORIZONTE], fill=cor("mangue"))
    nevoa = np.zeros((180, 320), bool)
    nevoa[96:104, :] = True
    img = pontilhar(img, nevoa & opaco(img), "taua_esc", 5)
    d = ImageDraw.Draw(img)
    # Morro do Silencio (direita) com o Cristo pequeno no topo
    pts = [(222, HORIZONTE)]
    for x in range(222, 321, 2):
        t = (x - 222) / 98.0
        y = 74 + int(40 * (abs(t - 0.62) ** 1.6)) + int(2 * np.sin(x / 5.0))
        pts.append((x, y))
    pts.append((320, HORIZONTE))
    d.polygon(pts, fill=cor("mangue"))
    morro_img = nova(320, 180)
    ImageDraw.Draw(morro_img).polygon(pts, fill=cor("folha"))
    morro = opaco(morro_img)
    copa = morro & ~deslocar(morro, 0, 3)
    img = pontilhar(img, copa, "folha", 7)
    d = ImageDraw.Draw(img)
    cx, cy = 282, 73
    for (x, y, c) in [(0, -9, "tabatinga"), (0, -8, "tabatinga"), (-3, -7, "tabatinga"), (-2, -7, "tabatinga"),
                      (-1, -7, "tabatinga"), (0, -7, "tabatinga"), (1, -7, "tabatinga"), (2, -7, "tabatinga"),
                      (3, -7, "tabatinga"), (0, -6, "tabatinga"), (0, -5, "tabatinga"), (0, -4, "tabatinga"),
                      (1, -6, "madeira_cl"), (1, -5, "madeira_cl"), (1, -4, "madeira_cl"), (-1, -3, "madeira_cl"),
                      (0, -3, "madeira_cl"), (1, -3, "madeira_cl"), (-1, -2, "madeira"), (0, -2, "madeira"),
                      (1, -2, "madeira")]:
        d.point((cx + x, cy + y), fill=cor(c))
    # ladeira: encosta de mato atras e degraus de arrimo descendo ate o cais
    degraus = [(-2 + 18 * i, -2 + 18 * (i + 1), 82 + 4 * i) for i in range(8)]   # (x0, x1, chao)
    encosta = [(0, 60), (40, 70), (90, 86), (150, HORIZONTE - 3), (0, HORIZONTE - 3)]
    d.polygon(encosta, fill=cor("mangue"))
    enc = nova(320, 180)
    ImageDraw.Draw(enc).polygon(encosta, fill=cor("folha"))
    m_enc = opaco(enc)
    img = pontilhar(img, m_enc & ~deslocar(m_enc, 0, 2), "folha", 8)
    # fileira de tras (o andar de cima e o telhado aparecem por tras), depois a da frente
    n = 0
    for fileira, recuo in [(0, 9), (1, 0)]:
        for i, (x0, x1, chao) in enumerate(degraus):
            if (fileira == 0 and i < 3) or (fileira == 1 and i in (1, 2)):
                continue                          # ali fica a Matriz, no adro dela
            xx = x0 + (5 if fileira == 0 else 1)
            while xx < x1 - 6:
                w = [9, 11, 7, 9, 11][(i + xx + fileira) % 5]
                w = min(w, x1 - xx - 1)
                andares = 2 if (i + fileira + xx) % 3 else 3
                p, s = ("rio", "mangue") if n == CASA_AZUL else FACHADAS[n % len(FACHADAS)]
                acesas = (1,) if n % 4 == 1 else ()
                colar_casa(img, casa(w, andares, p, s, acesas), xx, chao - recuo)
                n += 1
                xx += w + 2
    d = ImageDraw.Draw(img)
    for i, (x0, x1, chao) in enumerate(degraus):   # muro de arrimo de pedra embaixo de cada degrau
        prox = degraus[i + 1][2] if i + 1 < len(degraus) else HORIZONTE - 3
        d.rectangle([max(0, x0), chao + 1, x1, max(chao + 2, prox)], fill=cor("madeira_cl"))
        for y in range(chao + 2, max(chao + 3, prox + 1), 2):
            for x in range(max(0, x0) + (y % 4), x1, 4):
                d.point((x, y), fill=cor("madeira"))
        d.line([max(0, x0), chao + 1, x1, chao + 1], fill=cor("tabatinga"))
    # Matriz no alto: fachada com frontao e torre ~30% maior, com 2 sineiras
    # Matriz num adro de pedra mais abaixo na ladeira: a torre inteira fica a esquerda do logo (cruz em x ~21,
    # longe da borda) e o frontao comeca logo abaixo dele, entao nada da igreja fica escondido
    mx, chao_m = 27, 96
    d.rectangle([mx - 14, chao_m + 1, mx + 28, chao_m + 5], fill=cor("madeira_cl"))
    for y in range(chao_m + 2, chao_m + 6, 2):
        for x in range(mx - 14 + (y % 4), mx + 28, 4):
            d.point((x, y), fill=cor("madeira"))
    d.line([mx - 14, chao_m + 1, mx + 28, chao_m + 1], fill=cor("tabatinga"))
    fw, fh = 26, 22
    d.rectangle([mx, chao_m - fh, mx + fw, chao_m], fill=cor("tabatinga"))
    d.rectangle([mx + fw - 1, chao_m - fh, mx + fw, chao_m], fill=cor("madeira_cl"))
    fr = [(mx - 1, chao_m - fh), (mx + 4, chao_m - fh - 3), (mx + 9, chao_m - fh - 4), (mx + 13, chao_m - fh - 9),
          (mx + 17, chao_m - fh - 4), (mx + 22, chao_m - fh - 3), (mx + fw + 1, chao_m - fh)]
    d.polygon(fr, fill=cor("tabatinga"))
    d.line(fr, fill=cor("taua_esc"))
    d.line([mx - 1, chao_m - fh, mx + fw + 1, chao_m - fh], fill=cor("madeira_cl"))
    d.ellipse([mx + 11, chao_m - fh - 5, mx + 15, chao_m - fh - 1], fill=cor("barro"))   # oculo
    d.rectangle([mx + 10, chao_m - 9, mx + 16, chao_m], fill=cor("madeira"))           # portada
    d.ellipse([mx + 10, chao_m - 12, mx + 16, chao_m - 6], fill=cor("madeira"))
    for jx in (mx + 3, mx + 21):
        d.rectangle([jx, chao_m - 14, jx + 1, chao_m - 11], fill=cor("barro"))
        d.rectangle([jx, chao_m - 7, jx + 1, chao_m - 4], fill=cor("barro"))
    tx, tw, th = mx - 12, 12, 52
    d.rectangle([tx, chao_m - th, tx + tw - 1, chao_m], fill=cor("tabatinga"))
    d.rectangle([tx + tw - 2, chao_m - th, tx + tw - 1, chao_m], fill=cor("madeira_cl"))
    for y in (chao_m - 33, chao_m - 17):
        d.line([tx - 1, y, tx + tw, y], fill=cor("madeira_cl"))
    for sx in (tx + 2, tx + 7):                                     # 2 sineiras com sino
        d.rectangle([sx, chao_m - 45, sx + 2, chao_m - 39], fill=cor("breu"))
        d.point((sx + 1, chao_m - 46), fill=cor("breu"))
        d.rectangle([sx, chao_m - 42, sx + 2, chao_m - 41], fill=cor("dende"))
    d.rectangle([tx + 4, chao_m - 28, tx + 6, chao_m - 24], fill=cor("barro"))   # janela da torre
    d.polygon([(tx - 1, chao_m - th), (tx + tw // 2, chao_m - th - 9), (tx + tw, chao_m - th)], fill=cor("taua"))
    d.line([(tx + tw // 2, chao_m - th - 9), (tx + tw, chao_m - th)], fill=cor("taua_esc"))
    d.line([tx + tw // 2, chao_m - th - 14, tx + tw // 2, chao_m - th - 9], fill=cor("tabatinga"))
    d.line([tx + tw // 2 - 2, chao_m - th - 12, tx + tw // 2 + 2, chao_m - th - 12], fill=cor("tabatinga"))
    # cais de pedra na beira
    d.rectangle([0, HORIZONTE - 3, 146, HORIZONTE], fill=cor("madeira_cl"))
    for x in range(0, 146, 5):
        d.line([x, HORIZONTE - 3, x, HORIZONTE], fill=cor("madeira"))
    d.line([0, HORIZONTE - 3, 146, HORIZONTE - 3], fill=cor("tabatinga"))
    # margem direita: casario ao pe do morro do Cristo, com cais
    for (x, w, andares, k) in [(301, 9, 3, 0), (290, 9, 2, 2), (310, 11, 2, 4), (299, 9, 2, 1)]:
        p, s = FACHADAS[k]
        colar_casa(img, casa(w, andares, p, s, (0,) if k == 2 else ()), x, HORIZONTE - 4 - (6 if k == 0 else 0))
    d = ImageDraw.Draw(img)
    d.rectangle([286, HORIZONTE - 3, 319, HORIZONTE], fill=cor("madeira_cl"))
    d.line([286, HORIZONTE - 3, 319, HORIZONTE - 3], fill=cor("tabatinga"))
    # ponte de pedra em arcos: aparelho de blocos, cabeceira na margem direita, talha-mar nos pilares
    p0, p1 = 139, 296
    topo = 98
    antes = arr(img).copy()   # o que fica atras da ponte (morro distante), para aparecer por baixo dos arcos
    vao, larg = 21, 15
    arcos = [p0 + 6 + k * vao for k in range(7)]
    d.rectangle([p0, topo, p1, HORIZONTE], fill=cor("madeira"))
    for y in range(topo + 2, HORIZONTE + 1, 3):                    # blocos em amarracao
        d.line([p0, y, p1, y], fill=cor("barro"))
        for x in range(p0 + (3 if (y // 3) % 2 else 0), p1, 6):
            d.line([x, y - 2, x, y - 1], fill=cor("barro"))
    d.line([p0, topo, p1, topo], fill=cor("madeira_cl"))
    d.line([p0, topo + 1, p1, topo + 1], fill=cor("barro"))
    for x in range(p0, p1, 3):   # parapeito vazado
        d.rectangle([x, topo - 3, x + 1, topo - 1], fill=cor("madeira"))
    d.line([p0, topo - 4, p1, topo - 4], fill=cor("madeira_cl"))
    # cabeceira: bloco mais alto de pedra
    d.rectangle([p1 - 8, topo - 6, p1 + 2, HORIZONTE], fill=cor("madeira"))
    for y in range(topo - 3, HORIZONTE, 3):
        d.line([p1 - 8, y, p1 + 2, y], fill=cor("barro"))
    d.rectangle([p1 - 8, topo - 6, p1 + 2, HORIZONTE], outline=cor("barro"))
    d.line([p1 - 8, topo - 6, p1 + 2, topo - 6], fill=cor("madeira_cl"))
    a = arr(img)
    yy = np.mgrid[0:180, 0:320][0]
    for k, ax in enumerate(arcos):
        caixa = nova(320, 180)
        ImageDraw.Draw(caixa).ellipse([ax, topo + 5, ax + larg, topo + 21], fill=(255, 255, 255, 255))
        ImageDraw.Draw(caixa).rectangle([ax, topo + 13, ax + larg, HORIZONTE], fill=(255, 255, 255, 255))
        m = opaco(caixa)
        aduela = dilatar(m, diag=False) & ~m & (yy < topo + 13)
        a[aduela] = cor("madeira_cl")
        # por baixo do arco: o morro do outro lado, a beira (2 linhas) e a agua do Jaguaripe chegando ate o pilar
        beira = HORIZONTE - 8
        a[m & (yy < beira)] = antes[m & (yy < beira)]
        a[m & (yy >= beira) & (yy < beira + 2)] = cor("mangue")
        agua = m & (yy >= beira + 2)
        a[agua] = cor("rio")
        xx = np.mgrid[0:180, 0:320][1]
        a[agua & (yy == beira + 2)] = cor("reflexo")
        a[agua & ((yy - beira) % 3 == 1) & ((xx + yy) % 5 < 2)] = cor("reflexo")
        perto_sol = agua & (np.abs(xx - SOL[0]) <= 3) & ((yy - beira) % 2 == 0)
        a[perto_sol] = cor("dende")
    img = de_arr(a)
    d = ImageDraw.Draw(img)
    for ax in arcos[1:]:                               # talha-mar: quebra-mar pontudo no pe de cada pilar
        c = ax - 3
        d.polygon([(c - 4, HORIZONTE), (c - 4, HORIZONTE - 4), (c, HORIZONTE - 8), (c + 4, HORIZONTE - 4),
                   (c + 4, HORIZONTE)], fill=cor("madeira"))
        d.line([(c - 4, HORIZONTE - 4), (c, HORIZONTE - 8)], fill=cor("madeira_cl"))
        d.line([(c, HORIZONTE - 8), (c + 4, HORIZONTE - 4)], fill=cor("barro"))
        d.line([c - 4, HORIZONTE - 1, c + 4, HORIZONTE - 1], fill=cor("barro"))
    for k in range(4):   # postes de luz na ponte
        lx = p0 + 18 + k * 40
        d.line([lx, topo - 10, lx, topo - 4], fill=cor("breu"))
        d.point((lx, topo - 11), fill=cor("dende"))
        d.point((lx - 1, topo - 10), fill=cor("farinha"))
    # mato na beira, no pe da ponte
    for x in range(134, 142):
        y = HORIZONTE - 2 - (x % 3)
        d.line([x, y, x, HORIZONTE], fill=cor("mangue"))
    return img


def rio():
    img = faixas_v(nova(320, 180), 0, 319, [(HORIZONTE, "reflexo"), (HORIZONTE + 6, "rio"), (166, "mangue")],
                   179, trans=6)
    rnd = random.Random(3)
    # reflexo da ponte e da margem: a cidade espelhada, em linhas alternadas e tremidas, toda em barro
    cid = arr(cidade())
    a = arr(img)
    for k in range(1, 26):
        y = HORIZONTE + k
        if k % 2 == 0 and k > 6:
            continue
        src = cid[HORIZONTE - k]
        desl = int(round(1.5 * np.sin(k * 1.3)))
        linha = np.roll(src[:, 3] > 0, desl)
        if k > 12:
            linha &= (np.arange(320) + k) % 3 != 0
        a[y][linha] = cor("barro" if k > 2 else "taua_esc")
    img = de_arr(a)
    d = ImageDraw.Draw(img)
    # coluna de luz do sol na agua
    for y in range(HORIZONTE + 1, 180, 2):
        larg = int(3 + (y - HORIZONTE) * 0.35)
        x0 = SOL[0] - larg + rnd.randrange(-2, 3)
        comp = rnd.randrange(larg, larg * 2 + 2)
        d.line([x0, y, x0 + comp, y], fill=cor("dende" if y < 150 else "farinha"))
        if rnd.random() < 0.5:
            d.line([x0 + 2, y, x0 + comp // 2, y], fill=cor("farinha"))
    # marolas
    for _ in range(140):
        x, y = rnd.randrange(0, 320), rnd.randrange(HORIZONTE + 4, 178)
        comp = rnd.randrange(2, 7)
        d.line([x, y, x + comp, y], fill=cor("reflexo" if y < 150 else "rio"))
    # reflexo de lamparina: 2 linhas curtas embaixo de cada janela acesa do cais (nao pixel solto)
    for x in (40, 96, 300):
        d.line([x - 1, HORIZONTE + 3, x + 2, HORIZONTE + 3], fill=cor("dende"))
        d.line([x, HORIZONTE + 6, x + 1, HORIZONTE + 6], fill=cor("farinha"))
    # mangue em primeiro plano nos cantos
    for (xa, xb, lado) in [(0, 34, 1), (290, 320, -1)]:
        for x in range(xa, xb):
            t = (x - xa) / (xb - xa) if lado == 1 else (xb - x) / (xb - xa)
            topo = int(150 + 26 * t + 3 * np.sin(x * 0.9))
            d.line([x, topo, x, 179], fill=cor("breu"))
            if x % 3 == 0:
                d.line([x, topo - 3, x, topo], fill=cor("mangue"))
        for _ in range(16):
            x = rnd.randrange(xa, xb)
            y = rnd.randrange(150, 172)
            d.ellipse([x - 2, y - 1, x + 2, y + 1], fill=cor("mangue"))
            d.point((x - 1, y - 1), fill=cor("folha"))
    a = arr(img)
    a[:HORIZONTE] = 0
    return de_arr(a)


def brilho_agua(q):
    img = nova(320, 62)
    d = ImageDraw.Draw(img)
    rnd = random.Random(100 + q)
    for _ in range(46):
        x, y = rnd.randrange(30, 290), rnd.randrange(2, 30)
        if abs(x - SOL[0]) < 30 or rnd.random() < 0.4:
            comp = rnd.randrange(1, 4)
            d.line([x, y, x + comp, y], fill=cor("farinha" if abs(x - SOL[0]) < 26 else "reflexo"))
    return img


def canoa(q):
    """Canoa do oleiro com caxixis atravessando o rio, 8 quadros de remada. 48x18."""
    img = nova(48, 18)
    d = ImageDraw.Draw(img)
    bob = [0, 0, 1, 1, 1, 0, 0, 0][q]
    y0 = 9 + bob
    # carga de caxixis
    for i, (x, w, h, c) in enumerate([(8, 4, 5, "taua"), (12, 5, 6, "taua_vivo"), (17, 4, 4, "madeira_cl"),
                                      (21, 5, 6, "taua"), (26, 4, 5, "taua_esc"), (13, 3, 3, "tabatinga")]):
        p = caxixi(w, h, c, "taua_vivo" if c != "taua_vivo" else "farinha", "taua_esc" if c != "taua_esc"
                   else "barro")
        img.alpha_composite(p, (x, y0 - h + 1 if i < 5 else y0 - 8))
    # canoeiro: corpo, chapeu de palha e remo
    bx = 34
    d.rectangle([bx, y0 - 6, bx + 2, y0], fill=cor("barro"))
    d.rectangle([bx, y0 - 8, bx + 2, y0 - 7], fill=cor("madeira"))
    d.line([bx - 2, y0 - 9, bx + 4, y0 - 9], fill=cor("farinha"))
    d.line([bx, y0 - 10, bx + 2, y0 - 10], fill=cor("dende"))
    ang = [-0.9, -0.5, -0.1, 0.3, 0.6, 0.3, -0.2, -0.6][q]
    rx, ry = bx + 1 + int(round(3 * np.cos(ang + 1.2))), y0 - 4
    px_ = rx + int(round(9 * np.sin(ang)))
    py_ = ry + int(round(9 * np.cos(ang)))
    d.line([rx, ry, px_, py_], fill=cor("madeira_cl"))
    d.line([px_, py_, px_ + (1 if ang > 0 else -1), py_ + 2], fill=cor("madeira_cl"))
    d.line([bx + 1, y0 - 5, rx, ry], fill=cor("barro"))
    # casco
    d.polygon([(1, y0), (46, y0), (44, y0 + 3), (40, y0 + 4), (6, y0 + 4), (3, y0 + 3)], fill=cor("madeira"))
    d.line([1, y0, 46, y0], fill=cor("madeira_cl"))
    d.line([6, y0 + 4, 40, y0 + 4], fill=cor("barro"))
    d.line([0, y0 - 1, 2, y0], fill=cor("madeira"))
    d.line([47, y0 - 1, 45, y0], fill=cor("madeira"))
    img = contorno(img, "breu", diag=False)
    d = ImageDraw.Draw(img)
    # marola
    for i, x in enumerate(range(0, 48, 4)):
        if (i + q) % 3 == 0:
            d.line([x, y0 + 6, x + 2, y0 + 6], fill=cor("reflexo"))
    if q % 2 == 0:
        d.point((px_, min(17, py_ + 3)), fill=cor("tabatinga"))
    return img


LOGO_LETRAS = {
    "N": ["##..##", "###.##", "######", "######", "##.###", "##..##", "##..##", "##..##"],
    "A": [".####.", "##..##", "##..##", "##..##", "######", "##..##", "##..##", "##..##"],
    "Z": ["######", "....##", "...##.", "..##..", ".##...", "##....", "##....", "######"],
    "F": ["######", "##....", "##....", "#####.", "##....", "##....", "##....", "##...."],
    "I": ["######", "..##..", "..##..", "..##..", "..##..", "..##..", "..##..", "######"],
    "G": [".####.", "##..##", "##....", "##....", "##.###", "##..##", "##..##", ".####."],
    "H": ["##..##", "##..##", "##..##", "######", "##..##", "##..##", "##..##", "##..##"],
    "T": ["######", "..##..", "..##..", "..##..", "..##..", "..##..", "..##..", "..##.."],
    "V": ["##..##", "##..##", "##..##", "##..##", "##..##", ".####.", ".####.", "..##.."],
    "S": [".#####", "##....", "##....", ".####.", "....##", "....##", "....##", "#####."],
}


LOGO_GAP = 4   # breu entre as letras (logico): cada letra se le sozinha
# espiral de tabatinga (5x5, 1 px) dentro das hastes largas: (x, y) do canto, por letra
LOGO_ESPIRAIS = {"N": [(2, 26), (17, 8)], "A": [(2, 28), (17, 28)], "F": [(2, 26)], "I": [(10, 18)],
                 "G": [(2, 18)], "H": [(2, 26), (17, 26)], "T": [(10, 24)]}


def letra_logo(ch, cw=4, chh=5):
    bits = LOGO_LETRAS[ch]
    img = nova(len(bits[0]) * cw, len(bits) * chh)
    d = ImageDraw.Draw(img)
    w, h = img.size
    if ch == "V":   # V com ponta (em bloco ele lia "U")
        d.polygon([(0, 0), (7, 0), (w // 2, h - 12), (w - 8, 0), (w - 1, 0), (w // 2 + 3, h - 1),
                   (w // 2 - 4, h - 1)], fill=cor("taua"))
        return img
    if ch == "N":   # 2 hastes + faixa diagonal franca do topo esquerdo a base direita (le N, nao H/M)
        d.rectangle([0, 0, 7, h - 1], fill=cor("taua"))
        d.rectangle([w - 8, 0, w - 1, h - 1], fill=cor("taua"))
        d.polygon([(0, 0), (9, 0), (w - 1, h - 10), (w - 1, h - 1), (w - 10, h - 1), (0, 9)], fill=cor("taua"))
    else:
        for y, s in enumerate(bits):
            for x, c in enumerate(s):
                if c == "#":
                    d.rectangle([x * cw, y * chh, x * cw + cw - 1, y * chh + chh - 1], fill=cor("taua"))
    # chanfro nos cantos de fora
    a = arr(img)
    m = a[:, :, 3] > 0
    quina = m & ((~deslocar(m, 0, 1) & ~deslocar(m, 1, 0)) | (~deslocar(m, 0, 1) & ~deslocar(m, -1, 0)) |
                 (~deslocar(m, 0, -1) & ~deslocar(m, 1, 0)) | (~deslocar(m, 0, -1) & ~deslocar(m, -1, 0)))
    a[quina] = 0
    img = de_arr(a)
    if ch == "A":   # furo em boca de moringa: aba de 6 px, gargalo de 4 px e bojo de 8 px de quinas redondas
        d = ImageDraw.Draw(img)
        d.rectangle([8, 5, 15, 8], fill=cor("taua"))
        d.rectangle([9, 5, 14, 5], fill=(0, 0, 0, 0))
        d.rectangle([10, 6, 13, 8], fill=(0, 0, 0, 0))
        for (x, y) in [(8, 9), (15, 9), (8, 19), (15, 19)]:
            d.point((x, y), fill=cor("taua"))
    return img


def logo(palavra="NAZAFIGHT", corpo="taua"):
    """Logo de barro brunido: letras de tauá com espiral de tabatinga nas hastes, sentadas numa contra-forma de
    breu (2 px em volta e cheia nos vaos e entre as letras, para o ceu nao vazar e cada letra se ler sozinha),
    anel de tabatinga + breu por fora e sombra breu deslocada (2, 2). Largura ~262 x 56 (logico)."""
    letras = [(c, letra_logo(c)) for c in palavra]
    M = 4                                   # 2 de contra-forma + 1 de tabatinga + 1 de breu
    extra = LOGO_GAP if palavra == "NAZAFIGHT" else 0   # NAZA | FIGHT
    larg = sum(l.width for _c, l in letras) + LOGO_GAP * (len(letras) - 1) + extra + 2 * M
    alto = 40 + 2 * M
    corpo_img = nova(larg, alto)
    caixas = np.zeros((alto, larg), bool)
    vaos = []
    x = M
    for i, (c, l) in enumerate(letras):
        corpo_img.alpha_composite(l, (x, M))
        caixas[M:M + l.height, x:x + l.width] = True
        x += l.width
        if i < len(letras) - 1:
            g = LOGO_GAP + (extra if i == 3 else 0)
            vaos.append((x, x + g))
            x += g
    a = arr(corpo_img)
    m = a[:, :, 3] > 0
    a[m] = cor(corpo)
    topo = m & ~deslocar(m, 0, 1)
    esq = m & ~deslocar(m, 1, 0)
    baixo = m & ~deslocar(m, 0, -1)
    dirr = m & ~deslocar(m, -1, 0)
    a[baixo | dirr] = cor("taua_esc")
    a[topo | esq] = cor("taua_vivo")
    yy = np.mgrid[0:alto, 0:larg][0]
    a[m & (yy >= 33 + M) & ~(topo | esq)] = cor("taua_esc")
    # espiral de tabatinga de 1 px nas hastes largas (o motivo de Maragogipinho)
    x = M
    for i, (c, l) in enumerate(letras):
        for (sx, sy) in LOGO_ESPIRAIS.get(c, []):
            for ey, linha in enumerate(ESPIRAL):
                for ex, ch_ in enumerate(linha):
                    if ch_ == "#" and m[M + sy + ey, x + sx + ex]:
                        a[M + sy + ey, x + sx + ex] = cor("tabatinga")
        x += l.width + (LOGO_GAP + (extra if i == 3 else 0) if i < len(letras) - 1 else 0)
    # contra-forma de breu: as caixas das letras + 2 px; nos vaos entre letras ela recua em cima e embaixo
    base = dilatar(dilatar(caixas, diag=False), diag=False)
    for (x0, x1) in vaos:
        base[:M, x0:x1] = False
        base[M + 40:, x0:x1] = False
    a[base & ~m] = cor("breu")
    anel1 = dilatar(base, diag=False) & ~base
    a[anel1] = cor("tabatinga")
    anel2 = dilatar(base | anel1, diag=True) & ~(base | anel1)
    a[anel2] = cor("breu")
    img = com_sombra(de_arr(a), "breu", 2, 2)
    out = nova(img.width + img.width % 2, 56)
    out.alpha_composite(img, (0, (56 - img.height) // 2))
    return out


def nuvem_farinha(q):
    """Nuvem de farinha que levanta quando o logo cai (6 quadros). 264x40."""
    img = nova(264, 40)
    if q == 0:
        return img
    rnd = random.Random(40)
    bolhas = [(rnd.randrange(10, 254), rnd.randrange(20, 34), rnd.randrange(4, 10)) for _ in range(34)]
    abre = [0, 0.35, 0.65, 0.9, 1.05, 1.15][q]
    nivel = [0, 14, 16, 12, 8, 4][q]
    d = ImageDraw.Draw(img)
    for (x, y, r) in bolhas:
        cx = 132 + (x - 132) * abre
        cy = 36 - (36 - y) * abre * 1.1
        rr = r * (0.6 + 0.5 * abre)
        d.ellipse([cx - rr, cy - rr * 0.7, cx + rr, cy + rr * 0.7], fill=cor("farinha"))
    m = opaco(img)
    out = pontilhar(nova(264, 40), m, "farinha", nivel)
    out = pontilhar(out, m & ~deslocar(m, 0, 2), "tabatinga", min(16, nivel + 2))
    return out


def subtitulo():
    t = nova(1, 1)
    glifos = [render_glifo(glifo_letra(ch, True), "tabatinga", "breu") if ch != " " else None
              for ch in "RECÔNCAVO • BAHIA"]
    w = sum(g.width + 1 if g else 4 for g in glifos)
    t = nova(w, 11)
    x = 0
    for g in glifos:
        if g:
            t.alpha_composite(g, (x, 0))
            x += g.width + 1
        else:
            x += 4
    faixa = nova(w + 16, 13)
    d = ImageDraw.Draw(faixa)
    d.rectangle([4, 1, w + 11, 11], fill=cor("taua_esc"))
    d.line([4, 1, w + 11, 1], fill=cor("taua"))
    d.polygon([(0, 1), (4, 1), (4, 11), (0, 11), (2, 6)], fill=cor("taua"))
    d.polygon([(w + 15, 1), (w + 11, 1), (w + 11, 11), (w + 15, 11), (w + 13, 6)], fill=cor("taua"))
    faixa = contorno(faixa, "breu", diag=False)
    faixa.alpha_composite(t, (9, 1))
    return faixa


def painel_menu(w=96, h=66):
    """Tabuleta de feira atras do menu: madeira com cantos de barro e espirais."""
    img = nova(w, h)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], fill=cor("madeira"))
    for y in range(3, h - 3):
        for x in range(3, w - 3):
            if (x * 5 + (y // 2) * 17) % 29 == 0:
                d.line([x, y, min(w - 4, x + 7), y], fill=cor("barro"))
            elif (x * 11 + (y // 2) * 7) % 37 == 0:
                d.line([x, y, min(w - 4, x + 4), y], fill=cor("madeira_cl"))
    d.rectangle([1, 1, w - 2, h - 2], outline=cor("madeira_cl"))
    d.line([2, h - 2, w - 2, h - 2], fill=cor("barro"))
    d.line([w - 2, 2, w - 2, h - 2], fill=cor("barro"))
    d.rectangle([0, 0, w - 1, h - 1], outline=cor("breu"))
    for (cx, cy) in [(0, 0), (w - 9, 0), (0, h - 9), (w - 9, h - 9)]:
        canto = nova(9, 9)
        dc = ImageDraw.Draw(canto)
        dc.rectangle([0, 0, 8, 8], fill=cor("taua"))
        dc.rectangle([0, 0, 8, 8], outline=cor("breu"))
        esp = de_desenho(ESPIRAL, {"#": "tabatinga"})
        canto.alpha_composite(esp, (2, 2))
        img.alpha_composite(canto, (cx, cy))
    friso_espiral(img, 12, 2, w - 12, "taua_vivo", passo=6, meia=True)
    return img


def tabua_ativa(w=88, h=10):
    img = nova(w, h)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], fill=cor("barro"))
    d.rectangle([0, 0, w - 1, h - 1], outline=cor("dende"))
    d.line([1, 1, w - 2, 1], fill=cor("taua_esc"))
    for (x, s) in [(2, 1), (w - 6, -1)]:
        seta = de_desenho(["#...", "##..", "###.", "##..", "#..."] if s > 0 else ["...#", "..##", ".###", "..##",
                                                                                  "...#"], {"#": "dende"})
        img.alpha_composite(seta, (x, 2))
    return img


# ----------------------------------------------------------------------------------------------------------
# Selecao: a Feira dos Caxixis vista de cima
# ----------------------------------------------------------------------------------------------------------
def pano_listrado(w, h, c1, c2, larg=4, diagonal=False):
    """Pano de feira de 2 cores (P1 tauá/tabatinga, P2 rio/tabatinga), a listra de c2 mais fina."""
    yy, xx = np.mgrid[0:h, 0:w]
    k = (xx + (yy if diagonal else 0)) % (larg * 2)
    a = np.zeros((h, w, 4), np.uint8)
    a[:, :] = cor(c1)
    a[k >= larg + larg // 2] = cor(c2)
    return de_arr(a)


def barraca(w, h, listras, rnd):
    """Barraca vista de cima: toldo listrado com franja e uma mesa de caxixis aparecendo embaixo."""
    img = nova(w, h)
    d = ImageDraw.Draw(img)
    c1, c2 = listras
    d.rectangle([0, 0, w - 1, h - 6], fill=cor("madeira"))
    for x in range(0, w, 3):
        d.rectangle([x, 0, x + 2, h - 6], fill=cor(c1 if (x // 3) % 2 == 0 else c2))
    for x in range(0, w, 2):
        d.point((x, h - 5), fill=cor(c1))
    d.rectangle([0, 0, w - 1, h - 5], outline=cor("breu"))
    d.rectangle([1, h - 4, w - 2, h - 1], fill=cor("madeira_cl"))
    for x in range(2, w - 3, 3):
        p = caxixi(3, 3, rnd.choice(["taua", "taua_vivo", "madeira_cl", "taua_esc"]), "farinha", "barro")
        img.alpha_composite(p, (x, h - 4))
    return img


def tabuleiro(w, h, rnd):
    """Tabuleiro de barraca visto de cima: tabuas compridas de madeira (6 px), emenda escura, junta so de vez
    em quando (tabua de feira, nao parede de tijolo)."""
    img = nova(w, h)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], fill=cor("madeira"))
    for y0 in range(0, h, 6):
        d.line([0, y0, w - 1, y0], fill=cor("barro"))
        d.line([0, y0 + 1, w - 1, y0 + 1], fill=cor("madeira_cl"))
        x = -rnd.randrange(0, 60)
        while x < w:
            x += rnd.randrange(54, 96)
            d.line([x, y0 + 1, x, y0 + 5], fill=cor("barro"))
        for _ in range(w // 40):   # veio da madeira: tracos curtos, sem pontilhado
            vx, vy = rnd.randrange(0, w), y0 + rnd.randrange(3, 5)
            d.line([vx, vy, vx + rnd.randrange(4, 10), vy], fill=cor("madeira_cl" if rnd.random() < 0.5 else "barro"))
    return img


def pano_com_caxixis(w, h, listras, rnd, n_linhas=2):
    """Pano listrado estendido no tabuleiro, com caxixis em fileiras em cima (a mercadoria da feira)."""
    pano = pano_listrado(w, h, *listras, larg=6)
    d = ImageDraw.Draw(pano)
    for x in range(1, w - 1, 2):   # franja
        d.point((x, h - 1), fill=cor(listras[1]))
    d.rectangle([0, 0, w - 1, h - 2], outline=cor("breu"))
    cores = [("taua", "taua_vivo", "taua_esc"), ("taua_esc", "taua", "barro"), ("taua_vivo", "farinha", "taua"),
             ("madeira_cl", "farinha", "madeira")]
    for k in range(n_linhas):
        base = 3 + (k + 1) * (h - 4) // n_linhas - 1
        x = 3 + (k % 2) * 3
        while x < w - 8:
            cw, ch = rnd.choice([(6, 8), (7, 9), (5, 7), (8, 10)])
            if x + cw > w - 3:
                break
            c = rnd.choice(cores)
            pano.alpha_composite(caxixi(cw, ch, *c, friso="tabatinga" if rnd.random() < 0.4 else None),
                                 (x, base - ch + 1))
            x += cw + rnd.randrange(1, 4)
    return pano


def fundo_selecao():
    """A Feira dos Caxixis vista de cima: tabuleiro de barraca, toldos listrados nas bordas, panos com caxixis
    espalhados pelo campo, os panos dos retratos (P1 tauá, P2 rio) com o fundo liso de rio e a tabuleta do nome
    centrada embaixo de cada retrato."""
    rnd = random.Random(21)
    img = tabuleiro(320, 180, rnd)
    # toldos so nas bordas, 2 cores por lado (em sintonia com o VS)
    for (xa, xb, listras) in [(-6, 160, ("taua", "tabatinga")), (160, 326, ("rio", "tabatinga"))]:
        for linha_y in (0, 161):
            x = xa
            while x < xb:
                w = [22, 26, 30][(x // 7) % 3]
                w = min(w, xb - x)
                if w > 8:
                    img.alpha_composite(barraca(w, 18, listras, rnd), (x, linha_y + 1))
                x += w + 3
    # panos de feira com caxixis espalhados pelo campo: no meio, entre os retratos, e dos dois lados da grade
    img.alpha_composite(pano_com_caxixis(70, 30, ("farinha", "tabatinga"), rnd), (125, 26))
    for (x0, listras) in [(4, ("mangue", "folha")), (236, ("mangue", "folha"))]:
        img.alpha_composite(pano_com_caxixis(80, 34, listras, rnd), (x0, 100))
        img.alpha_composite(pano_com_caxixis(56, 18, ("farinha", "tabatinga"), rnd, 1), (x0 + 12, 138))
    # panos dos retratos grandes: borda listrada do lado (P1 tauá, P2 rio) e dentro liso de rio
    alto = POS["retrato_alto"] // 4
    for (x0, c) in [(POS["retrato_p1"][0] // 4, ("taua", "tabatinga")),
                    (POS["retrato_p2"][0] // 4, ("rio", "tabatinga"))]:
        pano = pano_listrado(112, alto, *c, larg=4, diagonal=True)
        dp = ImageDraw.Draw(pano)
        dp.rectangle([4, 4, 107, alto - 1], fill=cor("rio"))
        dp.rectangle([3, 3, 108, alto], outline=cor("breu"))
        dp.rectangle([0, 0, 111, alto - 1], outline=cor("breu"))
        img.alpha_composite(pano, (x0, 16))
        dd = ImageDraw.Draw(img)   # varal: pau de madeira em cima do pano
        dd.rectangle([x0 - 2, 14, x0 + 113, 16], fill=cor("madeira"))
        dd.line([x0 - 2, 14, x0 + 113, 14], fill=cor("madeira_cl"))
        dd.rectangle([x0 - 2, 14, x0 + 113, 16], outline=cor("breu"))
        # tabuleta do nome, centrada embaixo do retrato
        img.alpha_composite(tabuleta(80, 12, "", "tabatinga"), (x0 + 56 - 40, POS["tabuleta_sel_y"]))
    d = ImageDraw.Draw(img)
    # tabuleiro de madeira onde fica a grade (com moldura embaixo, dentro da tela)
    gx, gy = POS["grade"][0] // 4, POS["grade"][1] // 4
    gw = (POS["colunas"] * (POS["celula"] + POS["celula_espaco"]) - POS["celula_espaco"]) // 4
    gh = (POS["linhas"] * (POS["celula"] + POS["celula_espaco"]) - POS["celula_espaco"]) // 4
    assert gy + gh + 4 < 180, "a grade nao cabe com a moldura de baixo"
    d.rectangle([gx - 4, gy - 4, gx + gw + 3, gy + gh + 3], fill=cor("madeira"))
    d.rectangle([gx - 4, gy - 4, gx + gw + 3, gy + gh + 3], outline=cor("breu"))
    d.line([gx - 3, gy - 3, gx + gw + 2, gy - 3], fill=cor("madeira_cl"))
    d.line([gx - 3, gy + gh + 2, gx + gw + 2, gy + gh + 2], fill=cor("barro"))
    # faixa do titulo em cima
    faixa = nova(152, 13)
    df = ImageDraw.Draw(faixa)
    df.rectangle([0, 0, 151, 12], fill=cor("taua_esc"))
    df.line([0, 0, 151, 0], fill=cor("taua"))
    df.rectangle([0, 0, 151, 12], outline=cor("breu"))
    friso_espiral(faixa, 3, 4, 149, "taua", meia=False, traco=True)
    img.alpha_composite(faixa, (84, 1))
    return img


def celula(vazia=True):
    """Barraquinha 32x32: moldura de barro; dentro, um caxixi tampado (slot vazio ou bloqueado)."""
    img = nova(32, 32)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 31, 31], fill=cor("taua"))
    d.line([1, 1, 30, 1], fill=cor("taua_vivo"))
    d.line([1, 1, 1, 30], fill=cor("taua_vivo"))
    d.line([30, 2, 30, 30], fill=cor("taua_esc"))
    d.line([2, 30, 30, 30], fill=cor("taua_esc"))
    d.rectangle([3, 3, 28, 28], fill=cor("barro"))
    d.rectangle([0, 0, 31, 31], outline=cor("breu"))
    px = img.load()
    for (x, y) in [(0, 0), (31, 0), (0, 31), (31, 31)]:
        px[x, y] = (0, 0, 0, 0)
    for x in range(4, 28, 2):
        px[x, 2] = cor("tabatinga")
    if vazia:
        pote = caxixi(14, 16, "taua_esc", "taua", "barro", friso="madeira_cl")
        pd = ImageDraw.Draw(pote)
        pd.rectangle([3, 0, 10, 2], fill=cor("madeira"))     # tampa
        pd.rectangle([3, 0, 10, 2], outline=cor("breu"))
        pd.point((6, 0), fill=cor("madeira_cl"))
        img.alpha_composite(pote, (9, 9))
    return img


def celula_aleatoria():
    img = celula(vazia=False)
    t = texto_bits("?", 3, "dende", "breu", 1)
    img.alpha_composite(t, ((32 - t.width) // 2, (32 - t.height) // 2))
    return img


def cursor_sel(jogador, aceso):
    """Cantoneiras 40x40 por fora da celula; P1 dende, P2 reflexo (o rio escuro sumia na madeira), as duas com
    contorno breu. Etiqueta 1P/2P em letra de tabuleta numa tarja de breu, FORA da celula e em espelho: P1 em
    cima a esquerda, P2 em cima a direita. Sprite 40x50."""
    c = "dende" if jogador == 1 else "reflexo"
    luz = "farinha" if jogador == 1 else "tabatinga"
    img = cantos_cursor(c, luz, aceso)
    eti = nova(17, 10)
    de = ImageDraw.Draw(eti)
    de.rectangle([0, 0, 16, 9], fill=cor("breu"))
    de.line([1, 9, 15, 9], fill=cor(c))
    x = 2
    for ch in f"{jogador}P":
        g = render_glifo(LETRAS[ch], "tabatinga", "barro")
        eti.alpha_composite(g, (x, 1))
        x += g.width + 1
    out = nova(40, 50)
    out.alpha_composite(eti, (0 if jogador == 1 else 23, 0))
    out.alpha_composite(img, (0, 10))
    return out


def cantos_cursor(c, luz, aceso):
    img = nova(40, 40)
    d = ImageDraw.Draw(img)
    for (x, y, sx, sy) in [(0, 0, 1, 1), (39, 0, -1, 1), (0, 39, 1, -1), (39, 39, -1, -1)]:
        d.line([x, y, x + sx * 9, y], fill=cor(c), width=1)
        d.line([x, y + sy, x + sx * 9, y + sy], fill=cor(c))
        d.line([x, y, x, y + sy * 9], fill=cor(c))
        d.line([x + sx, y, x + sx, y + sy * 9], fill=cor(c))
        if aceso:
            d.point((x + sx, y + sy), fill=cor(luz))
    return contorno(img, "breu", diag=False)


# ----------------------------------------------------------------------------------------------------------
# Tela de VS: pano de feira dividido, emblema de remos cruzados
# ----------------------------------------------------------------------------------------------------------
def fundo_vs():
    img = nova(320, 180)
    # listra tom sobre tom: o lado continua tauá x rio, mas atras do retrato o pano fica quieto
    esq = pano_listrado(320, 180, "taua", "taua_esc", larg=6, diagonal=True)
    dirr = pano_listrado(320, 180, "rio", "mangue", larg=6, diagonal=True)
    a, b = arr(esq), arr(dirr)
    yy, xx = np.mgrid[0:180, 0:320]
    corte = xx > 160 + (yy - 90) * 0.35
    out = np.where(corte[:, :, None], b, a)
    img = de_arr(out)
    d = ImageDraw.Draw(img)
    for k in range(-3, 4):
        d.line([(160 + k - 90 * 0.35 * -1 * -1 - 31.5 + 31.5, 0), (160 + k + 31.5, 180)], fill=cor("madeira"))
    d.line([(160 - 31.5 - 4, 0), (160 + 31.5 - 4, 180)], fill=cor("breu"))
    d.line([(160 - 31.5 + 4, 0), (160 + 31.5 + 4, 180)], fill=cor("breu"))
    # faixas escuras em cima e embaixo (onde ficam os nomes)
    d.rectangle([0, 0, 319, 12], fill=cor("barro"))
    d.rectangle([0, 146, 319, 179], fill=cor("barro"))
    d.line([0, 13, 319, 13], fill=cor("breu"))
    d.line([0, 145, 319, 145], fill=cor("breu"))
    friso_espiral(img, 4, 172, 318, "taua", meia=False, traco=True)
    return img


def emblema_vs():
    img = nova(80, 56)
    d = ImageDraw.Draw(img)
    for (a0, a1) in [((8, 50), (72, 6)), ((8, 6), (72, 50))]:   # dois remos cruzados
        d.line([a0, a1], fill=cor("madeira_cl"), width=3)
        ex, ey = a1
        sx = 1 if a1[0] > a0[0] else -1
        sy = 1 if a1[1] > a0[1] else -1
        d.polygon([(ex, ey), (ex - sx * 10, ey - sy * 4), (ex - sx * 4, ey - sy * 10)], fill=cor("madeira"))
    img = contorno(img, "breu", diag=False)
    vs = logo("VS")
    a = arr(vs)
    m = a[:, :, 3] > 0
    ys, xs = np.where(m)
    vs = vs.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    img.alpha_composite(vs, ((80 - vs.width) // 2, (56 - vs.height) // 2))
    return img


# ----------------------------------------------------------------------------------------------------------
# Montagem dos SFF: (grupo, numero, imagem logica, eixo logico x, eixo logico y)
# Os eixos ficam em pixels logicos aqui e saem multiplicados por 4.
# ----------------------------------------------------------------------------------------------------------
def sprites_fight():
    s = []
    t = trilho_vida()
    ox, oy = TRILHO_ORIGEM
    s += [(10, 0, t, ox, oy), (10, 1, espelhar(t), t.width - ox - PRANCHA[0], oy)]
    for g, args in [(11, ("folha", "mangue", "tabatinga")), (12, ("dende", "taua_vivo", "taua_esc")),
                    (13, ("taua", "taua_esc", "taua_vivo"))]:
        e = enchimento_vida(*args)
        s += [(g, 0, e, 0, 0), (g, 1, espelhar(e), 0, 0)]
    f = fantasma_vida()
    s += [(14, 0, f, 0, 0), (14, 1, espelhar(f), 0, 0)]
    tx, ty = PLACA["trilho"]
    for k in range(7):
        c = composto_poder(k)
        s += [(20, k, c, tx, ty), (20, 10 + k, espelhar(c), PLACA["w"] - tx - PLACA["trilho_w"], ty)]
    for g, args in [(21, ("rio", "tabatinga", "reflexo")), (22, ("dende", "farinha", "tabatinga"))]:
        e = enchimento_poder(*args)
        s += [(g, 0, e, 0, 0), (g, 1, espelhar(e), 0, 0)]
    fundo, anel, racha = moldura_face(False), moldura_face(True), rachaduras_face()
    s += [(30, 0, fundo, 0, 0), (30, 1, espelhar(fundo), 0, 0), (31, 0, anel, 0, 0), (31, 1, espelhar(anel), 0, 0),
          (32, 0, racha, 0, 0), (32, 1, espelhar(racha), 0, 0)]
    s.append((40, 0, relogio(), RELOGIO["w"] // 2, 0))
    s += [(50, 0, bolinha(False), 0, 0), (50, 1, bolinha(True), 0, 0)]
    for n in range(1, 6):
        tb = tabuleta(100, 24, f"ROUND {n}", "tabatinga")
        s.append((60, n, tb, 50, 12))
    tb = tabuleta(80, 24, "LUTA!", "dende", escala=3)
    s.append((61, 0, tb, 40, 12))
    for q in range(6):
        k = letreiro_ko(q)
        s.append((62, q, k, k.width // 2, k.height // 2))
    for q in range(4):
        s.append((70, q, cacos(q), 13, 13))
    s.append((71, 0, nova(1, 1), 0, 0))
    return s


def sprites_system():
    s = []
    lg = logo()
    s.append((0, 0, lg, lg.width // 2, 28))
    sub = subtitulo()
    s.append((0, 1, sub, sub.width // 2, 0))
    s.append((0, 2, nova(1, 1), 0, 0))
    s += [(100, 0, ceu(), 0, 0), (100, 1, nuvens(), 0, 0), (100, 2, cidade(), 0, 0), (100, 3, rio(), 0, 0)]
    for q in range(4):
        s.append((101, q, brilho_agua(q), 0, 0))
    for q in range(8):
        s.append((110, q, canoa(q), 0, 0))
    for q in range(6):
        s.append((121, q, nuvem_farinha(q), 132, 35))
    s.append((130, 0, painel_menu(), 0, 0))
    s.append((131, 0, tabua_ativa(), 44, 10))   # eixo: centro x; 10 = 42 px acima da linha de base / 4 (arred.)
    s.append((200, 0, fundo_selecao(), 0, 0))
    s += [(300, 0, celula(True), 0, 0), (300, 1, celula_aleatoria(), 0, 0)]
    for j, g in [(1, 310), (2, 311)]:
        s += [(g, 0, cursor_sel(j, True), 0, 0), (g, 1, cursor_sel(j, False), 0, 0)]
    s += [(312, 0, cursor_sel(1, True), 0, 0), (313, 0, cursor_sel(2, True), 0, 0)]
    s.append((400, 0, fundo_vs(), 0, 0))
    em = emblema_vs()
    s.append((400, 1, em, 40, 28))
    return s


def finalizar(sprites, nome):
    out = []
    for (g, n, img, ax, ay) in sprites:
        checar_paleta(img, f"{nome} {g},{n}")
        out.append((g, n, ampliar(img), ax * ESCALA, ay * ESCALA))
    return out


# ----------------------------------------------------------------------------------------------------------
# .def (system e fight). Todas as posicoes saem de POS; o .def e a fonte de verdade das previas.
# ----------------------------------------------------------------------------------------------------------
CABECALHO = ("; Nazafight - gerado por ferramentas/gerar_layout.py (nao edite a mao: rode o gerador).\n"
             "; Arte 100% desenhada por codigo em pixel art (grade logica ampliada 4x), paleta de Nazare (BA).\n")


def system_def():
    mx, my = POS["menu"]
    esp = POS["menu_espaco"]
    pmx, pmy = POS["painel_menu"]
    g = POS["grade"]
    lc = "1280,720"
    itens = [("arcade", "ARCADE"), ("versus", "VERSUS"), ("training", "TREINO"), ("watch", "ASSISTIR"),
             ("options", "OPÇÕES"), ("exit", "SAIR")]
    t = CABECALHO + f"""
[Info]
name = Nazafight
author = Nazafight
versiondate = 11,10,2026
mugenversion = 1.0
ikemenversion = 1.0
localcoord = {lc}

[Files]
spr = system.sff
snd = system.snd            ; nao existe aqui: cai em data/system.snd
select = select.def         ; idem: data/select.def (o .bat edita esse; NUNCA ponha um select.def nesta pasta)
fight = fight.def
font1 = fonts/naza_menu.def
font2 = fonts/naza_menu_ativo.def
font3 = fonts/naza_tab.def
font4 = fonts/naza_num.def

[Title Info]
fadein.time = 20
fadeout.time = 10
menu.pos = {mx},{my}
menu.item.font = 1,0,0
menu.item.localcoord = {lc}
menu.item.spacing = 0,{esp}
menu.item.layerno = 2
menu.item.active.font = 2,0,0
menu.item.active.localcoord = {lc}
menu.item.active.layerno = 2
menu.item.active.bg.spr = 131,0
menu.item.active.bg.offset = 0,0
menu.item.active.bg.localcoord = {lc}
menu.item.active.bg.layerno = 2
menu.window.margins.y = 12,8
menu.window.visibleitems = {len(itens)}
menu.boxcursor.visible = 0
menu.boxcursor.localcoord = {lc}
menu.title.uppercase = 0
"""
    for k, v in itens:
        t += f"menu.itemname.{k} = {v}\n"
    t += f"""title.font = -1
loading.font = 3,0,-1
loading.offset = 1248,700
loading.text = CARREGANDO...
loading.localcoord = {lc}
footer.title.font = -1
footer.title.localcoord = {lc}
footer.info.font = -1          ; o "F1: INFO" saiu: em escala 0,5 a letra ficava fina, fora da grade de 4x
footer.info.text =
footer.info.localcoord = {lc}
footer.version.font = -1
footer.version.localcoord = {lc}
footer.overlay.col = 20,12,16
footer.overlay.alpha = 255,0
footer.overlay.window = 0,700,1280,720
footer.overlay.localcoord = {lc}

[TitleBGdef]
bgclearcolor = 20,12,16

[TitleBG Ceu]
type = normal
spriteno = 100,0
layerno = 0
start = -640,0

[TitleBG Nuvens]
type = normal
spriteno = 100,1
layerno = 0
start = -640,48
tile = 1,0
velocity = -0.15,0

[TitleBG Cidade]
type = normal
spriteno = 100,2
layerno = 0
start = -640,0

[TitleBG Rio]
type = normal
spriteno = 100,3
layerno = 0
start = -640,0

[TitleBG Brilho]
type = anim
actionno = 101
layerno = 0
start = -640,{HORIZONTE * 4}

[TitleBG Canoa]
type = anim
actionno = 110
layerno = 0
start = -880,{POS['canoa_y']}
tile = 1,0
tilespacing = 1700,0
velocity = 0.4,0

[TitleBG Painel]
type = normal
spriteno = 130,0
layerno = 0
start = {pmx - 640},{pmy}

[TitleBG Logo]
type = anim
actionno = 120
layerno = 0
start = {POS['logo'][0] - 640},{POS['logo'][1]}

[TitleBG Farinha]
type = anim
actionno = 121
layerno = 0
start = {POS['logo'][0] - 640},{POS['logo'][1] + 112}

[TitleBG Subtitulo]
type = normal
spriteno = 0,1
layerno = 0
start = {POS['subtitulo'][0] - 640},{POS['subtitulo'][1]}

[Begin Action 101]
101,0, 0,0, 10
101,1, 0,0, 10
101,2, 0,0, 10
101,3, 0,0, 10

[Begin Action 110]
"""
    for q in range(8):
        t += f"110,{q}, 0,0, 6\n"
    t += """
[Begin Action 120]
0,0, 0,-160, 2
0,0, 0,-100, 2
0,0, 0,-48, 2
0,0, 0,0, 2
0,0, 0,12, 2
0,0, 0,-8, 2
0,0, 0,4, 2
0,0, 0,-4, 2
0,0, 0,0, -1

[Begin Action 121]
0,2, 0,0, 8
121,1, 0,0, 4
121,2, 0,0, 4
121,3, 0,0, 5
121,4, 0,0, 6
121,5, 0,0, 8
0,2, 0,0, -1

"""
    cel, ce = POS["celula"], POS["celula_espaco"]
    rp1, rp2 = POS["retrato_p1"], POS["retrato_p2"]
    n1, n2 = POS["nome_sel_p1"], POS["nome_sel_p2"]
    t += f"""[Select Info]
fadein.time = 10
fadeout.time = 10
rows = {POS['linhas']}
columns = {POS['colunas']}
wrapping = 1
pos = {g[0]},{g[1]}
showemptyboxes = 1
moveoveremptyboxes = 0
cell.size = {cel},{cel}
cell.spacing = {ce},{ce}
cell.bg.spr = 300,0
cell.random.spr = 300,1
portrait.spr = 9000,0
portrait.offset = 12,12          ; 3 px logicos: o retrato 25x25 fica na grade de 4
portrait.scale = 1,1
p1.cursor.startcell = 0,0
p1.cursor.active.anim = 310
p1.cursor.active.offset = -16,-56
p1.cursor.done.spr = 312,0
p1.cursor.done.offset = -16,-56
p2.cursor.startcell = 0,{POS['colunas'] - 1}
p2.cursor.active.anim = 311
p2.cursor.active.offset = -16,-56
p2.cursor.done.spr = 313,0
p2.cursor.done.offset = -16,-56
p2.cursor.blink = 0
p1.face.spr = 9000,1
p1.face.offset = {rp1[0] + 4},{rp1[1] + 2}
p1.face.facing = 1
p1.face.scale = 1,1
p1.face.window = {rp1[0]},{rp1[1]},{rp1[0] + 448},{rp1[1] + POS['retrato_alto']}
p2.face.spr = 9000,1
p2.face.offset = {rp2[0] + 436},{rp2[1] + 2}
p2.face.facing = -1
p2.face.scale = 1,1
p2.face.window = {rp2[0]},{rp2[1]},{rp2[0] + 448},{rp2[1] + POS['retrato_alto']}
p1.name.font = 1,0,0
p1.name.offset = {n1[0]},{n1[1]}
p2.name.font = 1,0,0
p2.name.offset = {n2[0]},{n2[1]}
title.font = 1,0,0
title.offset = 640,52

[Begin Action 310]
310,0, 0,0, 8
310,1, 0,0, 8

[Begin Action 311]
311,0, 0,0, 8
311,1, 0,0, 8

[SelectBGdef]
bgclearcolor = 20,12,16

[SelectBG Feira]
type = normal
spriteno = 200,0
layerno = 0
start = -640,0

[VS Screen]
match.font = 1,0,0
match.offset = 640,48
match.text = LUTA %i
p1.spr = 9000,1
p1.offset = 100,196
p1.facing = 1
p1.window = 0,44,632,580
p2.spr = 9000,1
p2.offset = 1180,196
p2.facing = -1
p2.window = 648,44,1280,580
p1.name.font = 1,0,0
p1.name.offset = 320,674
p2.name.font = 1,0,0
p2.name.offset = 960,674

[VersusBGdef]
bgclearcolor = 20,12,16

[VersusBG Pano]
type = normal
spriteno = 400,0
layerno = 0
start = -640,0

[VersusBG Emblema]
type = normal
spriteno = 400,1
layerno = 0
start = 0,360

; secoes vazias: o .bat (Ajustar-Menus) injeta done.key nelas
[Victory Screen]

[Option Info]

[Pause Menu]

[Replay Info]

[Continue Screen]
"""
    return t


def fight_def():
    v1, v2 = POS["vida_p1"], POS["vida_p2"]
    # poder: o pos do .def e o canto do trilho; a placa do P2 e o espelho da do P1
    P = PLACA
    tx, ty = P["trilho"]
    qx, qy = POS["placa_p1"]
    p1 = (qx + tx * ESCALA, qy + ty * ESCALA)
    p2 = (1280 - qx - P["w"] * ESCALA + (P["w"] - tx - P["trilho_w"]) * ESCALA, qy + ty * ESCALA)
    f1, f2 = POS["face_p1"], POS["face_p2"]
    nm1, nm2 = POS["nome_p1"], POS["nome_p2"]
    w1, w2 = POS["vitoria_p1"], POS["vitoria_p2"]
    rx, ry = POS["relogio"]
    # relogio: topo do digito 1 px abaixo da boca de breu; o .def quer a linha de base (topo + altura - 1)
    topo_dig = (ry // ESCALA + 2 + RELOGIO["placa"][1] + 1) * ESCALA
    rel_y = topo_dig + RELOGIO_GLIFO[1] * ESCALA - 1 - ry
    # numero do nivel do poder: centro do glifo de naza_num na placa, relativo ao canto do trilho
    centro_p1 = P["numero_x"] + 4 - tx
    centro_p2 = (P["w"] - P["numero_x"] - 8) + 4 - (P["w"] - tx - P["trilho_w"])
    vida_fim = 16 + VIDA_W * ESCALA - 1        # 399: a faixa da vida em px, a partir do canto da prancha
    poder_fim = 12 + PODER_W * ESCALA - 1      # 243
    face_dentro = 2 * ESCALA                   # o retrato comeca 2 px logicos dentro da moldura
    num_x = {1: centro_p1 * ESCALA, 2: centro_p2 * ESCALA}
    num_y = (P["numero_y"] - ty) * ESCALA + 12 * ESCALA - 1
    t = CABECALHO + """
[Info]
name = Nazafight
author = Nazafight
ikemenversion = 1.0
localcoord = 1280,720

[Files]
sff = fight.sff
snd = fight.snd               ; data/fight.snd
font1 = fonts/naza_num.def
font2 = fonts/naza_relogio_alerta.def
font3 = fonts/naza_tab.def
font4 = fonts/naza_menu.def
font5 = fonts/naza_relogio.def
fightfx.sff = fightfx.sff     ; data/
fightfx.air = fightfx.air
common.snd = common.snd

[FightFx]
scale = 4

; Vida: prancha de saveiro com alca de moringa. A vida fica presa na ponta de fora (junto do retrato) e o dano
; abre junto do relogio: o motor prende o enchimento no 1o valor de range.x. folha > 50%, dende 26-50%, taua <= 25%.
[Lifebar]
mid.delay = 30
"""
    for j, (pos, sufixo, faixa) in enumerate([(v1, 0, f"16,{vida_fim}"), (v2, 1, f"{vida_fim},16")], start=1):
        t += f"p{j}.pos = {pos[0]},{pos[1]}\n"
        t += f"p{j}.bg0.spr = 10,{sufixo}\n"
        t += f"p{j}.mid.spr = 14,{sufixo}\np{j}.mid.offset = 16,8\n"
        t += f"p{j}.front.spr = 13,{sufixo}\np{j}.front.offset = 16,8\n"
        t += f"p{j}.front26.spr = 12,{sufixo}\np{j}.front26.offset = 16,8\n"
        t += f"p{j}.front51.spr = 11,{sufixo}\np{j}.front51.offset = 16,8\n"
        t += f"p{j}.range.x = {faixa}\n"
    t += """
[Simul Lifebar]
[Simul_3P Lifebar]
[Simul_4P Lifebar]
[Turns Lifebar]
[Tag Lifebar]

; Poder: trilho de madeira + 3 caxixis de estoque (cru -> quente -> cozido). levelbars = enche de novo a cada estoque.
[Powerbar]
"""
    for j, (pos, base, faixa) in enumerate([(p1, 0, f"12,{poder_fim}"), (p2, 10, f"{poder_fim},12")], start=1):
        sufixo = j - 1
        t += f"p{j}.pos = {pos[0]},{pos[1]}\n"
        t += f"p{j}.bg0.spr = 20,{base}\n"
        for k in range(1, 7):
            t += f"p{j}.bg0{k * 500}.spr = 20,{base + k}\n"
        t += f"p{j}.front.spr = 21,{sufixo}\np{j}.front.offset = 12,4\n"
        t += f"p{j}.front3000.spr = 22,{sufixo}\np{j}.front3000.offset = 12,4\n"
        t += f"p{j}.range.x = {faixa}\np{j}.levelbars = 1\n"
        t += f"p{j}.counter.font = 1,0,0\np{j}.counter.offset = {num_x[j]},{num_y}\n"
    t += f"""
; Retrato: fundo liso de rio atras, 9000,0 do lutador (25x25, escala inteira 4), anel de barro por cima.
; A moldura encosta na alca da ponta de fora do trilho.
[Face]
p1.pos = {f1[0]},{f1[1]}
p1.bg.spr = 30,0
p1.face.spr = 9000,0
p1.face.offset = {face_dentro},{face_dentro}
p1.ko.spr = 32,0
p1.top.spr = 31,0
p2.pos = {f2[0]},{f2[1]}
p2.bg.spr = 30,1
p2.face.spr = 9000,0
p2.face.offset = {FACE * ESCALA - face_dentro},{face_dentro}
p2.face.facing = -1
p2.ko.spr = 32,1
p2.top.spr = 31,1
[Simul Face]
[Turns Face]
[Tag Face]

[Name]
p1.pos = {nm1[0]},{nm1[1] + 31}
p1.name.font = 3,0,1
p2.pos = {nm2[0]},{nm2[1] + 31}
p2.name.font = 3,0,-1
[Simul Name]
[Turns Name]
[Tag Name]

; Relogio: caxixi brunido com a boca cheia de 2 digitos grandes (fonte 5); abaixo de 10 s, fonte 2 em taua
; vivo, cujos glifos ja trazem o zero na frente (o motor escreve 8, a tela mostra 08).
[Time]
pos = {rx},{ry}
bg.spr = 40,0
counter.font = 2,0,0
counter.offset = 0,{rel_y}
counter10.font = 5,0,0
counter10.offset = 0,{rel_y}
framespercount = 60

[Combo]
pos = {POS['combo'][0]},{POS['combo'][1]}
start.x = -320
counter.font = 1,0,1
counter.shake = 1
text.font = 3,0,1
text.text = "ACERTOS"
text.offset = 12,0
displaytime = 90

[Round]
pos = {POS['round'][0]},{POS['round'][1]}
match.wins = 2
match.maxdrawgames = 1
start.waittime = 30
ctrl.time = 30
round.default.font = 4,0,0
round.default.text = "ROUND %i"
round.default.displaytime = 60
"""
    for n in range(1, 6):
        t += f"round{n}.anim = {600 + n}\nround{n}.displaytime = 60\n"
    t += """fight.anim = 610
fight.displaytime = 45
ko.anim = 620
dko.font = 4,0,0
dko.text = "DUPLO K.O."
to.font = 4,0,0
to.text = "TEMPO!"
win.font = 4,0,0
win.text = "%s VENCEU"
draw.font = 4,0,0
draw.text = "EMPATE"

; Vitorias: bolinhas de barro; crua = falta ganhar, cozida = round ganho.
[WinIcon]
useiconupto = 4
"""
    for j, (pos, dx) in enumerate([(w1, 28), (w2, -28)], start=1):
        t += f"p{j}.pos = {pos[0]},{pos[1]}\np{j}.iconoffset = {dx},0\np{j}.bg0.spr = 50,0\n"
        for tipo in ("n", "s", "h", "c", "t", "throw", "suicide", "teammate", "perfect", "clutch"):
            t += f"p{j}.{tipo}.spr = 50,1\n"
        t += f"p{j}.counter.font = 3,0,{1 if j == 1 else -1}\n"
    for n in range(1, 6):
        t += f"\n[Begin Action {600 + n}]\n"
        for dy, tm in [(-240, 2), (-160, 2), (-80, 2), (0, 2), (12, 2), (-8, 2), (4, 2), (0, -1)]:
            t += f"60,{n}, 0,{dy}, {tm}\n"
    t += "\n[Begin Action 610]\n"
    for dy, tm in [(-80, 2), (0, 2), (8, 2), (-4, 2), (0, -1)]:
        t += f"61,0, 0,{dy}, {tm}\n"
    t += "\n[Begin Action 620]\n"
    for q, tm in enumerate([6, 5, 5, 6, 6, -1]):
        t += f"62,{q}, 0,0, {tm}\n"
    t += ("\n; Caxixi de estoque quebrando. Pronto, mas sem gatilho no v1.0.0 (o Powerbar nao avisa o gasto).\n"
          "[Begin Action 700]\n70,0, 0,0, 3\n70,1, 0,0, 3\n70,2, 0,0, 3\n70,3, 0,0, 3\n71,0, 0,0, -1\n")
    return t


# ----------------------------------------------------------------------------------------------------------
# Leitura de volta (.def, .sff, fontes) e previas montadas como o motor posicionaria
# ----------------------------------------------------------------------------------------------------------
def ler_def(caminho):
    """Devolve (secoes, acoes): secoes = [(nome_minusculo, {chave: valor})] na ordem; acoes = {n: [quadros]}."""
    secoes, acoes = [], {}
    atual, acao = None, None
    for linha in Path(caminho).read_text(encoding="utf-8").splitlines():
        s = linha.split(";", 1)[0].strip()
        if not s:
            continue
        if s.startswith("[") and s.endswith("]"):
            nome = s[1:-1].strip().lower()
            if nome.startswith("begin action"):
                acao = int(nome.split()[-1])
                acoes[acao] = []
                atual = None
            else:
                atual = {}
                secoes.append((nome, atual))
                acao = None
            continue
        if acao is not None:
            acoes[acao].append([int(v) for v in s.split(",")[:5]])
        elif atual is not None and "=" in s:
            k, v = s.split("=", 1)
            atual[k.strip().lower()] = v.strip().strip('"')
    return secoes, acoes


def secao(secoes, nome):
    for n, d in secoes:
        if n == nome:
            return d
    raise KeyError(nome)


def nums(v):
    return [float(x) for x in v.split(",")]


def carregar_sff(caminho):
    from io import BytesIO
    out = {}
    for (g, n), (w, h, ax, ay, _fmt, png) in ler_sff2(caminho).items():
        out[(g, n)] = (Image.open(BytesIO(png)).convert("RGBA"), ax, ay)
    return out


def carregar_fonte(def_caminho):
    secs, _ = ler_def(def_caminho)
    d = secao(secs, "def")
    glifos = {chr(n): img for (g, n), (img, ax, ay) in carregar_sff(Path(def_caminho).parent / d["file"]).items()
              if g == 0}
    tam = [int(x) for x in nums(d["size"])]
    esp = int(nums(d["spacing"])[0])
    return {"glifos": glifos, "w": tam[0], "h": tam[1], "esp": esp}


def colar(tela, img, x, y, janela=None):
    """alpha_composite com recorte (aceita x, y negativos e uma janela x0, y0, x1, y1)."""
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = (int(round(v)) for v in janela) if janela else (0, 0, tela.width, tela.height)
    cx0, cy0 = max(x, x0, 0), max(y, y0, 0)
    cx1, cy1 = min(x + img.width, x1, tela.width), min(y + img.height, y1, tela.height)
    if cx1 <= cx0 or cy1 <= cy0:
        return
    pedaco = img.crop((cx0 - x, cy0 - y, cx1 - x, cy1 - y))
    tela.alpha_composite(pedaco, (cx0, cy0))


def spr(tela, sprites, gn, x, y, janela=None, virar=False, escala=1):
    img, ax, ay = sprites[gn]
    if escala != 1:
        img = img.resize((img.width * escala, img.height * escala), Image.NEAREST)
        ax, ay = ax * escala, ay * escala
    if virar:
        img = espelhar(img)
        colar(tela, img, x - (img.width - ax), y - ay, janela)
    else:
        colar(tela, img, x - ax, y - ay, janela)


def largura_texto(fonte, texto, escala=1.0):
    w = 0
    for i, ch in enumerate(texto):
        g = fonte["glifos"].get(ch)
        w += fonte["w"] if (ch == " " or g is None) else g.width
        if i < len(texto) - 1:
            w += fonte["esp"]
    return w * escala


def escrever(tela, fonte, texto, x, y, alinhar=1, escala=1.0):
    """Como Fnt.DrawText: y e a linha de base (topo = y - altura + 1); alinhar 1 esq, 0 centro, -1 dir."""
    w = largura_texto(fonte, texto, escala)
    if alinhar == 0:
        x -= w / 2
    elif alinhar < 0:
        x -= w
    topo = y - (fonte["h"] - 1) * escala
    for ch in texto:
        g = fonte["glifos"].get(ch)
        if ch == " " or g is None:
            x += (fonte["w"] + fonte["esp"]) * escala
            continue
        if escala != 1:
            g = g.resize((max(1, int(g.width * escala)), max(1, int(g.height * escala))), Image.NEAREST)
        colar(tela, g, x, topo)
        x += g.width + fonte["esp"] * escala


def fonte_do(defs, idx, base):
    """Fonte N do [Files] de um .def."""
    files = secao(defs, "files")
    return carregar_fonte(base / files[f"font{idx}"])


def ler_retrato(char, g, n):
    """Decodifica um sprite (RLE8 ou PNG) do SFF v2 de um lutador em chars/, para as previas."""
    from io import BytesIO
    b = (RAIZ / "chars" / char / f"{char}.sff").read_bytes()
    nos_ofs, qtd, pal_ofs, n_pal, ldata_ofs, _l, tdata_ofs = struct.unpack_from("<7I", b, 36)
    nos = [struct.unpack_from("<HHHHhhHBBIIHH", b, nos_ofs + 28 * k) for k in range(qtd)]
    k = next(i for i, no in enumerate(nos) if no[0] == g and no[1] == n)
    while nos[k][10] == 0:
        k = nos[k][6]
    gg, nn, w, h, ax, ay, _link, fmt, _d, ofs, tam, palidx, flags = nos[k]
    base = tdata_ofs if flags & 1 else ldata_ofs
    dado = b[base + ofs + 4: base + ofs + tam]
    pg, pi, ncol, plink, pofs, ptam = struct.unpack_from("<HHHHII", b, pal_ofs + 16 * palidx)
    while ptam == 0:
        pg, pi, ncol, plink, pofs, ptam = struct.unpack_from("<HHHHII", b, pal_ofs + 16 * plink)
    pal = b[ldata_ofs + pofs: ldata_ofs + pofs + ptam]
    if fmt == 2:
        idx, i = bytearray(), 0
        while i < len(dado):
            c = dado[i]
            i += 1
            if c & 0xC0 == 0x40:
                idx += bytes([dado[i]]) * (c & 0x3F)
                i += 1
            else:
                idx.append(c)
        rgba = bytearray()
        for v in idx[:w * h]:
            rgba += bytes([pal[v * 4], pal[v * 4 + 1], pal[v * 4 + 2], 0 if v == 0 else 255])
        img = Image.frombytes("RGBA", (w, h), bytes(rgba))
    elif fmt in (10, 11, 12):
        img = Image.open(BytesIO(dado)).convert("RGBA")
    else:
        raise ValueError(f"formato {fmt} nao suportado na previa")
    return img, ax, ay


def retrato_x4(char, g, n):
    img, ax, ay = ler_retrato(char, g, n)
    return {(g, n): (img.resize((img.width * 4, img.height * 4), Image.NEAREST), ax * 4, ay * 4)}


def fundo_bg(tela, secoes, prefixo, sprites, acoes, tempo=0, quadro_fim=False):
    """Desenha as camadas [<prefixo> *] como o motor: x relativo ao centro (640), y ao topo."""
    for nome, d in secoes:
        if not nome.startswith(prefixo + " "):
            continue
        sx, sy = nums(d.get("start", "0,0"))
        vx = nums(d.get("velocity", "0,0"))[0]
        x = 640 + sx + vx * tempo
        if d.get("type", "normal") == "anim":
            quadros = acoes[int(d["actionno"])]
            q = quadros[-1] if quadro_fim else quadros[0]
            if "tile" in d:
                passo = nums(d["tilespacing"])[0] if "tilespacing" in d else 0
                x = 640 + sx + (vx * tempo) % (passo + sprites[(q[0], q[1])][0].width)
            if (q[0], q[1]) in sprites:
                spr(tela, sprites, (q[0], q[1]), x + q[2], sy + q[3])
            continue
        gn = tuple(int(v) for v in nums(d["spriteno"]))
        if d.get("tile", "0,0").split(",")[0].strip() == "1":
            w = sprites[gn][0].width
            xx = x - w * 3
            while xx < 1280:
                spr(tela, sprites, gn, xx, sy)
                xx += w
        else:
            spr(tela, sprites, gn, x, sy)


def previa_titulo(sys_spr, defs, acoes, fontes):
    t = secao(defs, "title info")
    bgdef = secao(defs, "titlebgdef")
    tela = Image.new("RGBA", (1280, 720), tuple(int(v) for v in nums(bgdef["bgclearcolor"])) + (255,))
    fundo_bg(tela, defs, "titlebg", sys_spr, acoes, tempo=1150, quadro_fim=True)
    mx, my = nums(t["menu.pos"])
    esp = nums(t["menu.item.spacing"])[1]
    itens = [v for k, v in t.items() if k.startswith("menu.itemname.")]
    for i, item in enumerate(itens):
        y = my + i * esp
        if i == 0:
            ox, oy = nums(t["menu.item.active.bg.offset"])
            spr(tela, sys_spr, tuple(int(v) for v in nums(t["menu.item.active.bg.spr"])), mx + ox, y + oy)
            escrever(tela, fontes[int(nums(t["menu.item.active.font"])[0])], item, mx, y, 0)
        else:
            escrever(tela, fontes[int(nums(t["menu.item.font"])[0])], item, mx, y, 0)
    x0, y0, x1, y1 = (int(v) for v in nums(t["footer.overlay.window"]))
    ImageDraw.Draw(tela).rectangle([x0, y0, x1 - 1, y1 - 1], fill=tuple(int(v) for v in nums(t["footer.overlay.col"])))
    for k in ("footer.title", "footer.info"):
        f = nums(t[k + ".font"])
        if f[0] < 0:
            continue
        ox, oy = nums(t[k + ".offset"])
        escrever(tela, fontes[int(f[0])], t[k + ".text"], ox, oy, int(f[2]), nums(t[k + ".scale"])[0])
    return tela


LUTADORES = ["pengaro", "hazaki", "gutto", "raiclaven"]
NOMES = {"pengaro": "Pengaro", "hazaki": "Hazaki", "gutto": "Gutto", "raiclaven": "Raiclaven"}


def previa_selecao(sys_spr, defs, acoes, fontes):
    s = secao(defs, "select info")
    tela = Image.new("RGBA", (1280, 720), (20, 12, 16, 255))
    fundo_bg(tela, defs, "selectbg", sys_spr, acoes)
    escrever(tela, fontes[int(nums(s["title.font"])[0])], "ARCADE", *nums(s["title.offset"]), 0)
    px, py = nums(s["pos"])
    cw, ch = nums(s["cell.size"])
    ex, ey = nums(s["cell.spacing"])
    cols, linhas = int(s["columns"]), int(s["rows"])
    po = nums(s["portrait.offset"])
    celulas = []
    for i in range(cols * linhas):
        r, c = divmod(i, cols)
        x, y = px + c * (cw + ex), py + r * (ch + ey)
        celulas.append((x, y))
        spr(tela, sys_spr, tuple(int(v) for v in nums(s["cell.bg.spr"])), x, y)
        if i < len(LUTADORES):
            spr(tela, retrato_x4(LUTADORES[i], 9000, 0), (9000, 0), x + po[0], y + po[1])
    for j, (cel, chr_) in [(1, (0, LUTADORES[0])), (2, (cols - 1, LUTADORES[cols - 1]))]:
        x, y = celulas[cel]
        q = acoes[int(s[f"p{j}.cursor.active.anim"])][0]
        ox, oy = nums(s[f"p{j}.cursor.active.offset"])
        spr(tela, sys_spr, (q[0], q[1]), x + ox, y + oy)
        fx, fy = nums(s[f"p{j}.face.offset"])
        jan = tuple(int(v) for v in nums(s[f"p{j}.face.window"]))
        virar = int(nums(s[f"p{j}.face.facing"])[0]) < 0
        spr(tela, retrato_x4(chr_, 9000, 1), (9000, 1), fx, fy, jan, virar)
        nx, ny = nums(s[f"p{j}.name.offset"])
        escrever(tela, fontes[int(nums(s[f"p{j}.name.font"])[0])], NOMES[chr_], nx, ny, 0)
    return tela


def previa_vs(sys_spr, defs, acoes, fontes):
    v = secao(defs, "vs screen")
    tela = Image.new("RGBA", (1280, 720), (20, 12, 16, 255))
    fundo_bg(tela, defs, "versusbg", sys_spr, acoes)
    for j, chr_ in [(1, "pengaro"), (2, "hazaki")]:
        fx, fy = nums(v[f"p{j}.offset"])
        jan = tuple(int(x) for x in nums(v[f"p{j}.window"]))
        spr(tela, retrato_x4(chr_, 9000, 1), (9000, 1), fx, fy, jan, int(nums(v[f"p{j}.facing"])[0]) < 0)
        nx, ny = nums(v[f"p{j}.name.offset"])
        escrever(tela, fontes[int(nums(v[f"p{j}.name.font"])[0])], NOMES[chr_], nx, ny, 0)
    mx, my = nums(v["match.offset"])
    escrever(tela, fontes[int(nums(v["match.font"])[0])], v["match.text"].replace("%i", "1"), mx, my, 0)
    return tela


def faixa_preenchida(pos_x, faixa, fracao):
    a, b = faixa
    lo, hi = min(a, b), max(a, b)
    tam = int((hi - lo + 1) * fracao + 0.5)
    ini = pos_x + hi + 1 - tam if a > b else pos_x + lo
    return ini, ini + tam


def fundo_teste(tipo, sys_spr):
    """Fundos de teste de contraste do HUD (nao sao cenarios): o titulo (ceu laranja), parede caiada e agua."""
    tela = Image.new("RGBA", (1280, 720), (20, 12, 16, 255))
    if tipo == "ceu":
        for gn in [(100, 0), (100, 2), (100, 3)]:
            spr(tela, sys_spr, gn, 0, 0)
        return tela
    f = nova(320, 180)
    if tipo == "caiada":   # parede caiada com rodape de barro
        f = faixas_v(f, 0, 319, [(0, "tabatinga"), (120, "farinha"), (150, "madeira_cl")], 179, trans=6)
    else:                  # agua de rio/mangue ate em cima
        f = faixas_v(f, 0, 319, [(0, "reflexo"), (40, "rio"), (140, "mangue")], 179, trans=6)
        d = ImageDraw.Draw(f)
        for k in range(90):
            x, y = (k * 37) % 316, (k * 23) % 176
            d.line([x, y, x + 3, y], fill=cor("reflexo" if y > 44 else "rio"))
    tela.alpha_composite(ampliar(f))
    return tela


def previa_hud(fig_spr, fdefs, fontes, sys_spr, sdefs, sacoes, fundo="ceu"):
    tela = fundo_teste(fundo, sys_spr)
    lb, pb = secao(fdefs, "lifebar"), secao(fdefs, "powerbar")
    estado = {1: {"vida": 1.0, "fantasma": 1.0, "poder": 2400, "vitorias": 1, "char": "pengaro"},
              2: {"vida": 0.30, "fantasma": 0.55, "poder": 1200, "vitorias": 0, "char": "hazaki"}}
    for j in (1, 2):
        e = estado[j]
        px_, py_ = nums(lb[f"p{j}.pos"])
        spr(tela, fig_spr, tuple(int(v) for v in nums(lb[f"p{j}.bg0.spr"])), px_, py_)
        faixa = [int(v) for v in nums(lb[f"p{j}.range.x"])]
        for chave, fr in [(f"p{j}.mid", e["fantasma"]), (None, e["vida"])]:
            if chave is None:
                limites = sorted((float(k[len(f"p{j}.front"):-4] or 0), k) for k in lb
                                 if k.startswith(f"p{j}.front") and k.endswith(".spr"))
                chave = [k for lim, k in limites if fr >= lim / 100][-1][:-4]
            ox, oy = nums(lb[f"{chave}.offset"])
            x0, x1 = faixa_preenchida(px_, faixa, fr)
            spr(tela, fig_spr, tuple(int(v) for v in nums(lb[f"{chave}.spr"])), px_ + ox, py_ + oy,
                janela=(x0, 0, x1, 720))
        # poder
        qx, qy = nums(pb[f"p{j}.pos"])
        niveis = sorted(int(k[len(f"p{j}.bg0"):-4] or 0) for k in pb if k.startswith(f"p{j}.bg0")
                        and k.endswith(".spr"))
        nv = max(n for n in niveis if e["poder"] >= n)
        chave = f"p{j}.bg0{nv if nv else ''}.spr"
        spr(tela, fig_spr, tuple(int(v) for v in nums(pb[chave])), qx, qy)
        fr = e["poder"] / 1000 - min(e["poder"] // 1000, 2)
        x0, x1 = faixa_preenchida(qx, [int(v) for v in nums(pb[f"p{j}.range.x"])], fr)
        ox, oy = nums(pb[f"p{j}.front.offset"])
        spr(tela, fig_spr, tuple(int(v) for v in nums(pb[f"p{j}.front.spr"])), qx + ox, qy + oy,
            janela=(x0, 0, x1, 720))
        cf = nums(pb[f"p{j}.counter.font"])
        cx_, cy_ = nums(pb[f"p{j}.counter.offset"])
        escrever(tela, fontes[int(cf[0])], str(e["poder"] // 1000), qx + cx_, qy + cy_, int(cf[2]))
        # retrato
        fa = secao(fdefs, "face")
        fx, fy = nums(fa[f"p{j}.pos"])
        spr(tela, fig_spr, tuple(int(v) for v in nums(fa[f"p{j}.bg.spr"])), fx, fy)
        ox, oy = nums(fa[f"p{j}.face.offset"])
        virar = int(nums(fa.get(f"p{j}.face.facing", "1"))[0]) < 0
        spr(tela, retrato_x4(e["char"], 9000, 0), (9000, 0), fx + ox + (1 if virar else 0), fy + oy, virar=virar)
        spr(tela, fig_spr, tuple(int(v) for v in nums(fa[f"p{j}.top.spr"])), fx, fy)
        # nome
        nm = secao(fdefs, "name")
        f = nums(nm[f"p{j}.name.font"])
        nx, ny = nums(nm[f"p{j}.pos"])
        escrever(tela, fontes[int(f[0])], NOMES[e["char"]], nx, ny, int(f[2]))
        # vitorias
        wi = secao(fdefs, "winicon")
        wx, wy = nums(wi[f"p{j}.pos"])
        dx, dy = nums(wi[f"p{j}.iconoffset"])
        precisa = int(secao(fdefs, "round")["match.wins"])
        for i in range(precisa):
            spr(tela, fig_spr, tuple(int(v) for v in nums(wi[f"p{j}.bg0.spr"])), wx + dx * i, wy + dy * i)
        for i in range(e["vitorias"]):
            spr(tela, fig_spr, tuple(int(v) for v in nums(wi[f"p{j}.n.spr"])), wx + dx * i, wy + dy * i)
    ti = secao(fdefs, "time")
    tx, ty = nums(ti["pos"])
    spr(tela, fig_spr, tuple(int(v) for v in nums(ti["bg.spr"])), tx, ty)
    tempo = 8
    chave = "counter10" if tempo >= 10 else "counter"
    ox, oy = nums(ti[f"{chave}.offset"])
    # o motor escreve o numero sem zero a esquerda; abaixo de 10 s a fonte de alerta desenha o 8 como "08"
    escrever(tela, fontes[int(nums(ti[f"{chave}.font"])[0])], str(tempo), tx + ox, ty + oy, 0)
    return tela


# ----------------------------------------------------------------------------------------------------------
def gerar():
    (MOTIF / "fonts").mkdir(parents=True, exist_ok=True)
    PREVIAS.mkdir(parents=True, exist_ok=True)
    # fontes
    fontes_geradas = {
        "naza_num": fonte_numero("naza_num", "farinha", "tabatinga", "dende"),
        "naza_relogio": fonte_relogio("naza_relogio", "farinha", "tabatinga", "dende", False),
        "naza_relogio_alerta": fonte_relogio("naza_relogio_alerta", "taua_vivo", "farinha", "taua", True),
        "naza_tab": fonte_texto("naza_tab", False, "tabatinga", "breu"),
        "naza_menu": fonte_texto("naza_menu", True, "tabatinga", "breu"),
        "naza_menu_ativo": fonte_texto("naza_menu_ativo", True, "dende", "barro"),
    }
    for nome, (sprites, d, glifos) in fontes_geradas.items():
        for ch, g in glifos.items():
            checar_paleta(g, f"fonte {nome} {ch!r}")
        escrever_sff2(MOTIF / "fonts" / f"{nome}.sff", sprites)
        (MOTIF / "fonts" / f"{nome}.def").write_text(d, encoding="utf-8", newline="\n")
    escrever_sff2(MOTIF / "fight.sff", finalizar(sprites_fight(), "fight"))
    escrever_sff2(MOTIF / "system.sff", finalizar(sprites_system(), "system"))
    (MOTIF / "system.def").write_text(system_def(), encoding="utf-8", newline="\n")
    (MOTIF / "fight.def").write_text(fight_def(), encoding="utf-8", newline="\n")


def verificar():
    """Le de volta cada SFF (cabecalho, contagem, sem repetido, PNG decodificavel) e as referencias dos .def."""
    from io import BytesIO
    total = 0
    for sff in sorted(MOTIF.rglob("*.sff")):
        dados = ler_sff2(sff)
        for (g, n), (w, h, ax, ay, fmt, png) in dados.items():
            img = Image.open(BytesIO(png))
            img.load()
            if img.size != (w, h) or img.mode != "RGBA":
                raise SystemExit(f"ERRO: {sff.name} {g},{n} PNG {img.size} {img.mode}")
            if ax % 4 or ay % 4:
                raise SystemExit(f"ERRO: {sff.name} {g},{n} eixo fora da grade ({ax},{ay})")
        total += len(dados)
        print(f"  {sff.relative_to(RAIZ)}: {len(dados)} sprites ok")
    for nome_def, sff in [("system.def", "system.sff"), ("fight.def", "fight.sff")]:
        secs, acoes = ler_def(MOTIF / nome_def)
        dados = ler_sff2(MOTIF / sff)
        for _n, d in secs:
            for k, v in d.items():
                if k.endswith(".spr") or k == "spriteno":
                    g, n = (int(x) for x in nums(v)[:2])
                    if g != 9000 and (g, n) not in dados:
                        raise SystemExit(f"ERRO: {nome_def} {k} = {v} nao existe em {sff}")
                if k.endswith(".anim") or k == "actionno":
                    if int(nums(v)[0]) not in acoes:
                        raise SystemExit(f"ERRO: {nome_def} {k} = {v}: acao nao definida")
        for a, quadros in acoes.items():
            for q in quadros:
                if (q[0], q[1]) not in dados:
                    raise SystemExit(f"ERRO: {nome_def} acao {a} usa {q[0]},{q[1]} que nao existe")
        files = secao(secs, "files")
        for k, v in files.items():
            if k.startswith("font") and not (MOTIF / v).exists():
                raise SystemExit(f"ERRO: {nome_def} {k} = {v} nao existe")
    obrig = ["lifebar", "simul lifebar", "turns lifebar", "powerbar", "face", "simul face", "turns face", "name",
             "simul name", "turns name", "time", "combo", "round", "winicon"]
    secs_f = [n for n, _ in ler_def(MOTIF / "fight.def")[0]]
    falta = [s for s in obrig if s not in secs_f]
    if falta:
        raise SystemExit(f"ERRO: fight.def sem as secoes obrigatorias {falta}")
    if (MOTIF / "select.def").exists():
        raise SystemExit("ERRO: motif/nazafight/select.def nao pode existir (passaria na frente do data/select.def)")
    print(f"  verificacao ok: {total} sprites, secoes obrigatorias presentes, referencias resolvidas")


def previas():
    sys_spr = carregar_sff(MOTIF / "system.sff")
    fig_spr = carregar_sff(MOTIF / "fight.sff")
    sdefs, sacoes = ler_def(MOTIF / "system.def")
    fdefs, _facoes = ler_def(MOTIF / "fight.def")
    sf = {i: fonte_do(sdefs, i, MOTIF) for i in range(1, 5)}
    ff = {i: fonte_do(fdefs, i, MOTIF) for i in range(1, 6)}
    saidas = {
        "titulo.png": previa_titulo(sys_spr, sdefs, sacoes, sf),
        "selecao.png": previa_selecao(sys_spr, sdefs, sacoes, sf),
        "vs.png": previa_vs(sys_spr, sdefs, sacoes, sf),
        "hud.png": previa_hud(fig_spr, fdefs, ff, sys_spr, sdefs, sacoes),
        "hud_caiada.png": previa_hud(fig_spr, fdefs, ff, sys_spr, sdefs, sacoes, "caiada"),
        "hud_agua.png": previa_hud(fig_spr, fdefs, ff, sys_spr, sdefs, sacoes, "agua"),
    }
    for nome, img in saidas.items():
        assert img.size == (1280, 720)
        img.convert("RGB").save(PREVIAS / nome, optimize=False)


def main():
    gerar()
    verificar()
    previas()
    h = hashlib.sha256()
    arquivos = sorted(list(MOTIF.rglob("*.*")) + list(PREVIAS.glob("*.png")))
    for p in arquivos:
        h.update(p.relative_to(RAIZ).as_posix().encode())
        h.update(p.read_bytes())
    print(f"ok: {len(arquivos)} arquivos, hash {h.hexdigest()[:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
