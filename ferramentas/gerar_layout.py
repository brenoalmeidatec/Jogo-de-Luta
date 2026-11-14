"""Gera o layout NAZAFIGHTS (screenpack do IKEMEN GO v1.0.0) inteiro por codigo, mais as previas.

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
RETRATO_NA_CELULA = 14  # portrait.offset da selecao (rosto 100x100 no meio da celula 128); o "?" compensa no eixo

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
    # HUD de 2026-11-13 (pedido do Breno: o antigo era alto e o poder ficava na linha dos pes): em cima tudo
    # termina em y = 120 (retrato) e as barras em y = 100; embaixo o poder vai de y = 688 a 716 (pes em 660).
    "vida_p1": (124, 16), "vida_p2": (724, 16),
    "relogio": (640, 8),             # centro x, topo y da caixa do relogio
    "face_p1": (4, 4), "face_p2": (1160, 4),         # canto da moldura 29x29 (logico)
    "nome_p1": (144, 68), "nome_p2": (1136, 68),     # P1: x da esquerda; P2: x da direita; y = topo do texto
    "vitoria_p1": (400, 72), "vitoria_p2": (856, 72),
    "placa_p1": (16, 688),           # canto da barra de poder (P1; a do P2 e o espelho)
    "round": (640, 300),
    "combo": (40, 300),
    # Titulo
    "logo": (446, 20),                # centro x e topo y do logo: no ceu da esquerda, sem tapar a Matriz e o Cristo
    "logo_larg": 640,                 # largura do logo na tela
    "menu": (640, 487),               # linha de base do 1o item
    "menu_espaco": 40,
    "faixa_menu": (440, 436, 840, 672),   # faixa escura atras do menu (x0, y0, x1, y1), multiplos de 2
    # Selecao
    "grade": (372, 392), "celula": 128, "celula_espaco": 8, "colunas": 4, "linhas": 2,
    "retrato_p1": (24, 64), "retrato_p2": (808, 64), "retrato_alto": 216,
    "tabuleta_sel_y": 71,                                     # topo (logico) da tabuleta do nome, sob o retrato
    "nome_sel_p1": (248, 331), "nome_sel_p2": (1032, 331),   # centro x (= centro do retrato), linha de base
    # Escolha de mapa (Breno, issue #35): painel por cima da selecao depois que os lutadores foram escolhidos.
    # A previa (640x400, retrato 9001 de cada cenario, feito pelo gerar_cenario.py) fica com o canto em "mapa_previa".
    "mapa_previa": (320, 124), "mapa_previa_tam": (640, 400),
    "mapa_nome": (640, 607),          # centro x e linha de base do nome do cenario (dentro da tabuleta)
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
    return (f"; Fonte {nome} do Nazafights, desenhada por codigo (ferramentas/gerar_layout.py)\n"
            f"[FNT v2]\nfntversion = 2,00\nname = \"{nome}\"\nauthor = \"Nazafights\"\n\n"
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
TRILHO_ORIGEM = (0, 0)   # eixo do sprite da barra de vida: o canto de cima-esquerda (P1)
TRILHO_W, TRILHO_H = 108, 21
PRANCHA = (TRILHO_W, 12)  # a barra (moldura) de cima; embaixo dela, colada, a plaquinha do nome
VIDA_X, VIDA_Y = 4, 3     # onde a vida comeca dentro da barra (P1)
VIDA_W, VIDA_H = 96, 6    # 384 x 24 px
TARJA = (4, 13, 60, 8)    # plaquinha do nome (x, y, w, h) no sprite: tela y 68 a 100


def anel_hud(img, m):
    """Contorno do HUD sobre fundo qualquer: 1 px de tabatinga na borda de dentro e 2 px de breu por fora."""
    a = arr(img)
    a[m & ~erodir(m, diag=True)] = cor("tabatinga")
    fora = dilatar(dilatar(m, diag=True), diag=True) & ~m
    a[fora] = cor("breu")
    return de_arr(a)


def moldura_dourada(m):
    """Moldura de ouro de 2 px por dentro da mascara m (luz em cima e a esquerda, sombra embaixo e a direita),
    com 1 px de breu por fora. Devolve (rgba, miolo) onde miolo = o que sobra dentro, para pintar de breu."""
    h, w = m.shape
    mp = np.pad(m, 2)            # a borda da imagem conta como fora (o erodir nao come a borda sozinho)
    anel1 = mp & ~erodir(mp, diag=True)
    meio = erodir(mp, diag=True)
    anel2 = meio & ~erodir(meio, diag=True)
    miolo = erodir(meio, diag=True)
    luz = anel1 & (deslocar(~mp, 0, 1) | deslocar(~mp, 1, 0))     # borda de cima e da esquerda
    sombra = anel1 & (deslocar(~mp, 0, -1) | deslocar(~mp, -1, 0))
    corte = (slice(2, 2 + h), slice(2, 2 + w))
    anel1, anel2, miolo, luz, sombra = (x[corte] for x in (anel1, anel2, miolo, luz, sombra))
    a = np.zeros((h, w, 4), np.uint8)
    a[anel1] = cor("dende")
    a[anel2] = cor("taua_esc")
    a[luz] = cor("farinha")
    a[sombra & ~luz] = cor("taua")
    a[miolo] = cor("breu")
    fora = dilatar(m, diag=True) & ~m
    a[fora] = cor("breu")
    return de_arr(a), miolo


def trilho_vida():
    """Barra de vida fina, inclinada na ponta do relogio (P1: retrato a esquerda), moldura de ouro e miolo de
    breu; colada embaixo, a plaquinha do nome. 108x21 (432x84 px)."""
    W, H = TRILHO_W, TRILHO_H
    m = np.zeros((H, W), bool)
    for y in range(PRANCHA[1]):
        m[y, 0:W - 1 - y // 3] = True       # a ponta de dentro desce em diagonal (estilo arcade)
    img, _ = moldura_dourada(m)
    a = arr(img)
    # brilho de 1 px no miolo, rente a moldura de cima (vidro escuro)
    a[VIDA_Y - 1, VIDA_X:VIDA_X + VIDA_W] = cor("barro")
    # plaquinha do nome: breu com friso de ouro embaixo
    tx, ty, tw, th = TARJA
    a[ty:ty + th, tx:tx + tw] = cor("breu")
    a[ty + th - 1, tx + 1:tx + tw - 1] = cor("dende")
    a[ty, tx + 1:tx + tw - 1] = cor("barro")
    return de_arr(a)


def enchimento_vida(corpo, escuro, luz):
    """Vida 96x6: 1 fileira de luz, 3 de corpo, 2 de sombra; um risco de brilho a cada 12 px."""
    img = nova(VIDA_W, VIDA_H)
    a = arr(img)
    a[:, :] = cor(corpo)
    a[0, :] = cor(luz)
    a[4:, :] = cor(escuro)
    for x in range(5, VIDA_W, 12):
        a[1, x:x + 3] = cor(luz)
    return de_arr(a)


def fantasma_vida():
    """Dano fantasma: farinha lisa (desce com atraso atras da vida)."""
    img = nova(VIDA_W, VIDA_H)
    ImageDraw.Draw(img).rectangle([0, 0, VIDA_W - 1, VIDA_H - 1], fill=cor("farinha"))
    return img


GEMA = [   # pedrinha de estoque 5x5 (antes do contorno): C corpo, L brilho, S sombra
    ".CCC.",
    "CLCCC",
    "CCCCS",
    "CCCSS",
    ".SSS.",
]
ESTOQUE_CORES = {   # apagada = sem estoque; meia = enchendo; cheia = estoque pronto
    "cru": {"C": "barro", "L": "madeira", "S": "barro"},
    "quente": {"C": "taua_esc", "L": "taua", "S": "barro"},
    "cozido": {"C": "dende", "L": "farinha", "S": "taua"},
}


def estoque(estado):
    """Pedrinha de estoque 7x7 (com contorno breu)."""
    base = de_desenho(GEMA, ESTOQUE_CORES[estado])
    g = nova(base.width + 2, base.height + 2)
    g.alpha_composite(base, (1, 1))
    return contorno(g, "breu", diag=False)


# barra de poder (P1) no canto de baixo: trilho fino de ouro + 3 pedrinhas de estoque. 86x7 logico = 344x28 px,
# de y 688 a 716: os pes (y 660) e a sombra ficam livres.
PLACA = {"w": 86, "h": 7, "trilho": (0, 0), "trilho_w": 64, "estoque_x": 66, "estoque_y": 0, "estoque_passo": 7}
PODER_X, PODER_Y = 3, 2
PODER_W, PODER_H = PLACA["trilho_w"] - 6, 3   # enchimento: 58x3 -> 232x12 px


def trilho_poder():
    w, h = PLACA["trilho_w"], PLACA["h"]
    m = np.zeros((h, w), bool)
    for y in range(h):
        m[y, 0:w - y // 2] = True
    img, _ = moldura_dourada(m)
    return img


def composto_poder(nivel_x2):
    """Trilho de poder com 3 pedrinhas; nivel_x2 = poder/500 (0..6). P1: trilho a esquerda, pedrinhas a direita."""
    P = PLACA
    img = nova(P["w"], P["h"])
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
    img = nova(PODER_W, PODER_H)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, PODER_W - 1, PODER_H - 1], fill=cor(corpo))
    d.line([0, 0, PODER_W - 1, 0], fill=cor(luz))
    px = img.load()
    for x in range(PODER_W):
        if x % 7 == 3:
            px[x, 1] = cor(faisca)
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


FACE = 29   # moldura logica: 2 px de anel + 25 px de dentro (o rosto 100x100 em escala 1/4 cabe inteiro)


def moldura_face(top=True):
    """Moldura de ouro 29x29 (top) ou fundo liso escuro (bg), que separa qualquer retrato do cenario."""
    n = FACE - 1
    if top:
        m = np.ones((FACE, FACE), bool)
        m[2:n - 1, 2:n - 1] = False
        img, _ = moldura_dourada(np.ones((FACE, FACE), bool))
        a = arr(img)
        a[2:n - 1, 2:n - 1] = 0                  # dentro vazio: o retrato aparece
        for (cx, cy) in [(0, 0), (n, 0), (0, n), (n, n)]:
            a[cy, cx] = cor("farinha")           # rebite de ouro nas quinas
        return de_arr(a)
    img = nova(FACE, FACE)
    ImageDraw.Draw(img).rectangle([1, 1, n - 1, n - 1], fill=cor("azulejo"))
    return img


def rachaduras_face():
    img = nova(FACE, FACE)
    d = ImageDraw.Draw(img)
    for pts in [[(3, 2), (8, 9), (7, 14), (12, 19), (11, 25)], [(8, 9), (14, 8), (20, 4)],
                [(12, 19), (18, 18), (24, 23)], [(7, 14), (3, 16)]]:
        d.line(pts, fill=cor("breu"))
    return img


RELOGIO = {"w": 36, "h": 24, "placa": (4, 2, 31, 21)}


def relogio():
    """Caixa do relogio 36x24 (144x96 px): moldura de ouro com as quinas cortadas e o visor de breu onde cabem
    os 2 digitos grandes."""
    R = RELOGIO
    m = np.ones((R["h"], R["w"]), bool)
    for k in range(3):                            # quinas cortadas em diagonal
        m[k, :3 - k] = m[k, R["w"] - 3 + k:] = False
        m[R["h"] - 1 - k, :3 - k] = m[R["h"] - 1 - k, R["w"] - 3 + k:] = False
    img, _ = moldura_dourada(m)
    a = arr(img)
    x0, y0, x1, y1 = R["placa"]
    a[y0:y1 + 1, x0:x1 + 1] = cor("breu")
    a[y1, x0 + 2:x1 - 1] = cor("barro")
    return de_arr(a)


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
# Letras de barro do emblema do VS (system.sff)
# ----------------------------------------------------------------------------------------------------------
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


def logo(palavra="NAZAFIGHTS", corpo="taua"):
    """Logo de barro brunido: letras de tauá com espiral de tabatinga nas hastes, sentadas numa contra-forma de
    breu (2 px em volta e cheia nos vaos e entre as letras, para o ceu nao vazar e cada letra se ler sozinha),
    anel de tabatinga + breu por fora e sombra breu deslocada (2, 2). Largura ~290 x 56 (logico)."""
    letras = [(c, letra_logo(c)) for c in palavra]
    M = 4                                   # 2 de contra-forma + 1 de tabatinga + 1 de breu
    extra = LOGO_GAP if palavra == "NAZAFIGHTS" else 0   # NAZA | FIGHT
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


def fundo_mapa():
    """Tela de escolha de mapa (issue #35): o mesmo tabuleiro de feira da selecao, com a moldura de madeira da
    previa animada no meio, setas dos dois lados, tabuleta do nome embaixo e a dica dos botoes."""
    rnd = random.Random(35)
    img = tabuleiro(320, 180, rnd)
    for (xa, xb, listras) in [(-6, 160, ("taua", "tabatinga")), (160, 326, ("rio", "tabatinga"))]:
        x = xa
        while x < xb:
            w = min([22, 26, 30][(x // 7) % 3], xb - x)
            if w > 8:
                img.alpha_composite(barraca(w, 18, listras, rnd), (x, 167))
            x += w + 3
    px, py = POS["mapa_previa"][0] // 4, POS["mapa_previa"][1] // 4
    pw, ph = POS["mapa_previa_tam"][0] // 4, POS["mapa_previa_tam"][1] // 4
    d = ImageDraw.Draw(img)
    d.rectangle([px - 4, py - 4, px + pw + 3, py + ph + 3], fill=cor("madeira"))
    d.rectangle([px - 4, py - 4, px + pw + 3, py + ph + 3], outline=cor("breu"))
    d.line([px - 3, py - 3, px + pw + 2, py - 3], fill=cor("madeira_cl"))
    d.line([px - 3, py + ph + 2, px + pw + 2, py + ph + 2], fill=cor("barro"))
    d.rectangle([px - 1, py - 1, px + pw, py + ph], fill=cor("breu"))
    # titulo
    faixa = nova(152, 13)
    df = ImageDraw.Draw(faixa)
    df.rectangle([0, 0, 151, 12], fill=cor("taua_esc"))
    df.line([0, 0, 151, 0], fill=cor("taua"))
    df.rectangle([0, 0, 151, 12], outline=cor("breu"))
    t = texto_bits("ESCOLHA O MAPA", 1, "farinha", "barro", 1)
    faixa.alpha_composite(t, ((152 - t.width) // 2, 3))
    img.alpha_composite(faixa, (84, 8))
    # setas
    seta = de_desenho(["#.....", "###...", "#####.", "######", "#####.", "###...", "#....."], {"#": "dende"})
    seta = seta.resize((seta.width * 2, seta.height * 2), Image.NEAREST)
    larga = nova(seta.width + 2, seta.height + 2)
    larga.alpha_composite(seta, (1, 1))
    seta = contorno(larga, "breu")
    cy = py + ph // 2 - seta.height // 2
    img.alpha_composite(seta, (px + pw + 8, cy))
    img.alpha_composite(espelhar(seta), (px - 8 - seta.width, cy))
    # tabuleta do nome (o motor escreve o nome com a fonte 1 em POS["mapa_nome"])
    img.alpha_composite(tabuleta(140, 12, "", "tabatinga"), (90, POS["mapa_nome"][1] // 4 - 11))
    dica = texto_bits("ESQUERDA E DIREITA TROCAM - ENTER CONFIRMA", 1, "tabatinga", "breu", 1)
    img.alpha_composite(dica, ((320 - dica.width) // 2, 157))
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
    for g, args in [(11, ("folha", "mangue", "tabatinga")), (12, ("dende", "taua", "farinha")),
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
    s.append((131, 0, tabua_ativa(), 44, 10))   # eixo: centro x; 10 = 42 px acima da linha de base / 4 (arred.)
    s.append((200, 0, fundo_selecao(), 0, 0))
    s.append((210, 0, fundo_mapa(), 0, 0))
    # O IKEMEN desenha cell.random.spr somando o portrait.offset (start.lua, updateDrawList), a celula
    # nao. Sem o eixo compensando, o "?" saia 14 px para baixo e para a direita da celula vazia.
    k = RETRATO_NA_CELULA / ESCALA
    s += [(300, 0, celula(True), 0, 0), (300, 1, celula_aleatoria(), k, k)]
    for j, g in [(1, 310), (2, 311)]:
        s += [(g, 0, cursor_sel(j, True), 0, 0), (g, 1, cursor_sel(j, False), 0, 0)]
    s += [(312, 0, cursor_sel(1, True), 0, 0), (313, 0, cursor_sel(2, True), 0, 0)]
    s.append((400, 0, fundo_vs(), 0, 0))
    em = emblema_vs()
    s.append((400, 1, em, 40, 28))
    return s


# ----------------------------------------------------------------------------------------------------------
# Abertura (Breno, 2026-11-13: "olha ai nazare e monta uma arte legal"). A cena do Jaguaripe e o logo foram gerados
# no ChatGPT (sprites/titulo/*_chatgpt.png) e passam aqui para pixel art de grade 2x (cada pixel do desenho vira 2x2
# na tela), sem pontilhado e com poucas cores. Ficam fora da paleta de 16 cores e da grade 4x do resto do layout.
# ----------------------------------------------------------------------------------------------------------
TITULO = RAIZ / "sprites" / "titulo"
GRADE_TITULO = 2


def arte_pixel(img, larg, cores):
    """Reduz para 'larg' pixels de desenho (proporcao mantida), poucas cores sem pontilhado, alfa so 0 ou 255,
    e amplia GRADE_TITULO vezes por vizinho."""
    alt = round(img.height * larg / img.width)
    rgba = img.convert("RGBA").resize((larg, alt), Image.LANCZOS)
    alfa = rgba.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    rgb = rgba.convert("RGB").quantize(cores, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    out = rgb.convert("RGBA")
    out.putalpha(alfa)
    return ampliar(out, GRADE_TITULO)


def fundo_titulo():
    """Nazare ao por do sol: o Jaguaripe, a ponte, o casario, a Matriz e o Cristo no morro, saveiros, caxixis e
    farinha na feira. Corta para 16:9 pelo meio e vira 640x360 de desenho (1280x720 na tela)."""
    img = Image.open(TITULO / "fundo_chatgpt.png").convert("RGB")
    alt = round(img.width * 9 / 16)
    y0 = (img.height - alt) // 2
    return arte_pixel(img.crop((0, y0, img.width, y0 + alt)), 1280 // GRADE_TITULO, 64)


def logo_titulo():
    """Logo NAZAFIGHTS com a faixa RECONCAVO • BAHIA. O fundo verde chapado do ChatGPT vira transparente."""
    a = np.array(Image.open(TITULO / "logo_chatgpt.png").convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    verde = (g > 140) & (g > r + 50) & (g > b + 50)
    ciano = (g > 170) & (b > 170) & (r < 140)          # o brilho solto que veio ao lado do N
    alfa = np.where(verde | ciano, 0, 255).astype(np.uint8)
    img = Image.fromarray(np.dstack([a.astype(np.uint8), alfa]), "RGBA")
    img = img.crop(img.getchannel("A").getbbox())
    return arte_pixel(img, POS["logo_larg"] // GRADE_TITULO, 40)


def faixa_menu():
    """Faixa escura atras do menu, com borda dourada em degrau (cantos de pixel). Opaca aqui: a transparencia vem
    do trans = addalpha da [TitleBG Faixa] (o motor nao mistura o alfa parcial do PNG)."""
    x0, y0, x1, y1 = (v // GRADE_TITULO for v in POS["faixa_menu"])
    w, h = x1 - x0, y1 - y0
    img = nova(w, h)
    d = ImageDraw.Draw(img)
    fundo = PALETA["breu"] + (255,)
    d.rectangle([2, 0, w - 3, h - 1], fill=fundo)
    d.rectangle([0, 2, w - 1, h - 3], fill=fundo)
    d.rectangle([1, 1, w - 2, h - 2], fill=fundo)
    ouro, sombra = PALETA["dende"] + (255,), PALETA["taua_esc"] + (255,)
    d.line([3, 1, w - 4, 1], fill=ouro)
    d.line([1, 3, 1, h - 4], fill=ouro)
    d.line([3, h - 2, w - 4, h - 2], fill=sombra)
    d.line([w - 2, 3, w - 2, h - 4], fill=sombra)
    for (x, y) in [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]:
        d.point((x, y), fill=ouro if x == 2 or y == 2 else sombra)
    return ampliar(img, GRADE_TITULO)


def sprites_titulo():
    """Sprites da abertura ja no tamanho da tela (nao passam por finalizar)."""
    lg = logo_titulo()
    return [(0, 0, lg, lg.width // 2, 0), (100, 0, fundo_titulo(), 0, 0), (130, 0, faixa_menu(), 0, 0)]


def finalizar(sprites, nome):
    out = []
    for (g, n, img, ax, ay) in sprites:
        checar_paleta(img, f"{nome} {g},{n}")
        out.append((g, n, ampliar(img), round(ax * ESCALA), round(ay * ESCALA)))
    return out


# ----------------------------------------------------------------------------------------------------------
# .def (system e fight). Todas as posicoes saem de POS; o .def e a fonte de verdade das previas.
# ----------------------------------------------------------------------------------------------------------
CABECALHO = ("; Nazafights - gerado por ferramentas/gerar_layout.py (nao edite a mao: rode o gerador).\n"
             "; Arte 100% desenhada por codigo em pixel art (grade logica ampliada 4x), paleta de Nazare (BA).\n")


def system_def():
    mx, my = POS["menu"]
    esp = POS["menu_espaco"]
    g = POS["grade"]
    lc = "1280,720"
    # Menu enxuto (Breno, 2026-11-13). Nome vazio esconde o item padrao do motor. "supermode" e o Modo Super
    # (nazafights.lua, ligado em [Files] module): versus com as barras de power sempre cheias.
    itens = [("arcade", "ARCADE"), ("versus", "VERSUS"), ("supermode", "MODO SUPER"), ("watch", "ASSISTIR"),
             ("options", "OPÇÕES")]
    escondidos = ["teamarcade", "teamversus", "teamcoop", "survival", "survivalcoop", "training", "exit"]
    t = CABECALHO + f"""
[Info]
name = Nazafights
author = Nazafights
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
module = nazafights.lua     ; MODO SUPER no menu (power sempre cheio) e escolha de mapa em todo modo

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
menu.item.active.bg.spacing = 0,{esp}          ; sem isso (0,0) a tabua ficava presa na 1a linha, tapando o ARCADE
menu.window.margins.y = 48,8          ; com 12 o motor cortava o alto do 1o item (ARCADE) e da tabua ativa
menu.window.visibleitems = {len(itens)}
menu.boxcursor.visible = 0
menu.boxcursor.localcoord = {lc}
menu.title.uppercase = 0
"""
    for k, v in itens:
        t += f"menu.itemname.{k} = {v}\n"
    for k in escondidos:
        t += f"menu.itemname.{k} =\n"
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

[TitleBG Fundo]
type = normal
spriteno = 100,0
layerno = 0
start = -640,0

[TitleBG Faixa]
type = normal
spriteno = 130,0
layerno = 0
start = {POS['faixa_menu'][0] - 640},{POS['faixa_menu'][1]}
trans = addalpha
alpha = 192,64

[TitleBG Logo]
type = anim
actionno = 120
layerno = 0
start = {POS['logo'][0] - 640},{POS['logo'][1]}

[Begin Action 120]
0,0, 0,-300, 2
0,0, 0,-190, 2
0,0, 0,-90, 2
0,0, 0,0, 2
0,0, 0,14, 2
0,0, 0,-8, 2
0,0, 0,4, 2
0,0, 0,-2, 2
0,0, 0,0, -1

"""
    cel, ce = POS["celula"], POS["celula_espaco"]
    rp1, rp2 = POS["retrato_p1"], POS["retrato_p2"]
    n1, n2 = POS["nome_sel_p1"], POS["nome_sel_p2"]
    mp, mn = POS["mapa_previa"], POS["mapa_nome"]
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
portrait.offset = {RETRATO_NA_CELULA},{RETRATO_NA_CELULA}          ; rosto 100x100 em PNG (sprites/retratos, trocar_retratos.py) no meio da celula
portrait.scale = 0.25,0.25       ; o motor amplia 4x o sprite do lutador: 1/4 desenha 1 por 1, nitido
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
p1.face.offset = {rp1[0]},{rp1[1]}
p1.face.facing = 1
p1.face.scale = 0.25,0.25
p1.face.window = {rp1[0]},{rp1[1]},{rp1[0] + 448},{rp1[1] + POS['retrato_alto']}
p2.face.spr = 9000,1
p2.face.offset = {rp2[0] + 448},{rp2[1]}
p2.face.facing = -1
p2.face.scale = 0.25,0.25
p2.face.window = {rp2[0]},{rp2[1]},{rp2[0] + 448},{rp2[1] + POS['retrato_alto']}
p1.name.font = 1,0,0
p1.name.offset = {n1[0]},{n1[1]}
p2.name.font = 1,0,0
p2.name.offset = {n2[0]},{n2[1]}
title.font = 1,0,0
title.offset = 640,52
; Escolha de mapa (Breno, issue #35): depois dos lutadores, painel por cima de tudo (layerno 1) com a previa animada
; do cenario (acao 9000 do .def dele, gerada pelo gerar_cenario.py com a musica embaixo). Nunca aleatorio:
; randomselect = 0 tira o "Stage: Random" da lista (o modulo nazafights.lua liga a escolha em todos os modos).
stage.randomselect = 0
stage.pos = {mp[0]},{mp[1]}
stage.portrait.anim = 9000
stage.portrait.localcoord = 1280,720
stage.portrait.layerno = 1
stage.portrait.window = {mp[0]},{mp[1]},{mp[0] + POS['mapa_previa_tam'][0]},{mp[1] + POS['mapa_previa_tam'][1]}   ; cenario sem previa nossa (Training Room) nao vaza
stage.portrait.bg.spr = 210,0
stage.portrait.bg.offset = {-mp[0]},{-mp[1]}       ; o motor soma o stage.pos: o painel cobre a tela toda
stage.portrait.bg.localcoord = 1280,720
stage.portrait.bg.layerno = 1
stage.text = %s
stage.font = 1,0,0
stage.offset = {mn[0] - mp[0]},{mn[1] - mp[1]}
stage.localcoord = 1280,720
stage.layerno = 1
stage.active.text = %s
stage.active.font = 2,0,0
stage.active.offset = {mn[0] - mp[0]},{mn[1] - mp[1]}
stage.active.localcoord = 1280,720
stage.active.layerno = 1
stage.active2.text = %s
stage.active2.font = 1,0,0
stage.active2.offset = {mn[0] - mp[0]},{mn[1] - mp[1]}
stage.active2.localcoord = 1280,720
stage.active2.layerno = 1
stage.active.switchtime = 20
stage.done.text = %s
stage.done.font = 2,0,0
stage.done.offset = {mn[0] - mp[0]},{mn[1] - mp[1]}
stage.done.localcoord = 1280,720
stage.done.layerno = 1

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
p1.offset = 0,140
p1.facing = 1
p1.scale = 0.5,0.5               ; busto 448x216 desenhado 2x (896x432), nitido
p1.window = 0,44,632,580
p2.spr = 9000,1
p2.offset = 1280,140
p2.facing = -1
p2.scale = 0.5,0.5
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
    topo_dig = (ry // ESCALA + RELOGIO["placa"][1] + 1) * ESCALA
    rel_y = topo_dig + RELOGIO_GLIFO[1] * ESCALA - 1 - ry
    # vida: P1 cheia a partir da ponta do retrato; P2 e o espelho (a barra nao e simetrica: a ponta inclinada)
    vx1 = VIDA_X * ESCALA
    vx2 = (TRILHO_W - VIDA_X - VIDA_W) * ESCALA
    vy = VIDA_Y * ESCALA
    vida = {1: (vx1, f"{vx1},{vx1 + VIDA_W * ESCALA - 1}"), 2: (vx2, f"{vx2 + VIDA_W * ESCALA - 1},{vx2}")}
    px0, py0 = PODER_X * ESCALA, PODER_Y * ESCALA
    poder_fim = px0 + PODER_W * ESCALA - 1
    face_dentro = 2 * ESCALA                   # o retrato comeca 2 px logicos dentro da moldura
    t = CABECALHO + """
[Info]
name = Nazafights
author = Nazafights
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
    for j, (pos, sufixo) in enumerate([(v1, 0), (v2, 1)], start=1):
        ox, faixa = vida[j]
        t += f"p{j}.pos = {pos[0]},{pos[1]}\n"
        t += f"p{j}.bg0.spr = 10,{sufixo}\n"
        t += f"p{j}.mid.spr = 14,{sufixo}\np{j}.mid.offset = {ox},{vy}\n"
        t += f"p{j}.front.spr = 13,{sufixo}\np{j}.front.offset = {ox},{vy}\n"
        t += f"p{j}.front26.spr = 12,{sufixo}\np{j}.front26.offset = {ox},{vy}\n"
        t += f"p{j}.front51.spr = 11,{sufixo}\np{j}.front51.offset = {ox},{vy}\n"
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
    for j, (pos, base, faixa) in enumerate([(p1, 0, f"{px0},{poder_fim}"), (p2, 10, f"{poder_fim},{px0}")],
                                           start=1):
        sufixo = j - 1
        t += f"p{j}.pos = {pos[0]},{pos[1]}\n"
        t += f"p{j}.bg0.spr = 20,{base}\n"
        for k in range(1, 7):
            t += f"p{j}.bg0{k * 500}.spr = 20,{base + k}\n"
        t += f"p{j}.front.spr = 21,{sufixo}\np{j}.front.offset = {px0},{py0}\n"
        t += f"p{j}.front3000.spr = 22,{sufixo}\np{j}.front3000.offset = {px0},{py0}\n"
        t += f"p{j}.range.x = {faixa}\np{j}.levelbars = 1\n"
    t += f"""
; Retrato: fundo liso de rio atras, 9000,0 do lutador (25x25, escala inteira 4), anel de barro por cima.
; A moldura encosta na alca da ponta de fora do trilho.
[Face]
p1.pos = {f1[0]},{f1[1]}
p1.bg.spr = 30,0
p1.face.spr = 9000,0
p1.face.offset = {face_dentro},{face_dentro}
p1.face.scale = 0.25,0.25
p1.ko.spr = 32,0
p1.top.spr = 31,0
p2.pos = {f2[0]},{f2[1]}
p2.bg.spr = 30,1
p2.face.spr = 9000,0
p2.face.offset = {FACE * ESCALA - face_dentro},{face_dentro}
p2.face.facing = -1
p2.face.scale = 0.25,0.25
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
; Fim de round mais rapido (estilo KOF). Padrao do IKEMEN: camera lenta 60 ticks a 1/4, espera 45 + 45 ticks e
; round acabando 300 ticks depois do KO: ~3 s do KO ate a pose de vitoria.
slow.time = 24
slow.fadetime = 16
slow.speed = 0.5
over.hittime = 10
over.waittime = 15
over.wintime = 10
over.time = 220
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
    return hud_por_cima(t)


HUD_POR_CIMA = ("Lifebar", "Powerbar", "Face", "Name", "Time", "Combo", "WinIcon")


def hud_por_cima(t):
    """Todo elemento do HUD (vida, poder, retrato, nome, relogio, acertos, vitorias) ganha `layerno = 2`.

    Sem isso o motor desenha o HUD na camada 0, ATRAS dos lutadores e dos Explods (heranca do MUGEN): a aura antiga
    do Despertar (mais de 2x a altura do lutador, antes da regra da aura discreta) passava por cima do relogio e das
    barras. Com layerno = 1 o HUD ficava na frente dos lutadores, mas a faisca de acerto (que o motor desenha na
    camada de cima, a dos Explods ontop) ainda tampava o relogio e a vida do P2 no super do Pengaro (filme da
    sandbox, cetico de 2026-11-12). Com layerno = 2 (o mesmo que o fight.def do motor usa no contador de combo) o HUD
    fica na frente de tudo o que e da luta (lutador que pula alto passa por tras da barra, nao por cima)."""
    saida, secao = [], ""
    for linha in t.split("\n"):
        saida.append(linha)
        s = linha.strip()
        if s.startswith("["):
            secao = s.strip("[]")
        elif secao in HUD_POR_CIMA and "=" in s and not s.startswith(";"):
            chave = s.split("=")[0].strip()
            if chave.rsplit(".", 1)[-1] in ("spr", "anim", "font"):
                saida.append(f"{chave.rsplit('.', 1)[0]}.layerno = 2")
    return "\n".join(saida)


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


def retrato_x4(char, g, n, escala=1.0):
    """O motor amplia 4x o sprite do lutador e depois aplica a escala do .def (1/4 nos retratos em PNG)."""
    img, ax, ay = ler_retrato(char, g, n)
    k = 4 * escala
    return {(g, n): (img.resize((round(img.width * k), round(img.height * k)), Image.NEAREST), ax * k, ay * k)}


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
    itens = [v for k, v in t.items() if k.startswith("menu.itemname.") and v]
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
            spr(tela, retrato_x4(LUTADORES[i], 9000, 0, nums(s.get("portrait.scale", "1"))[0]), (9000, 0), x + po[0], y + po[1])
        elif i == len(LUTADORES):   # randomselect: o motor soma o portrait.offset tambem aqui
            spr(tela, sys_spr, tuple(int(v) for v in nums(s["cell.random.spr"])), x + po[0], y + po[1])
    for j, (cel, chr_) in [(1, (0, LUTADORES[0])), (2, (cols - 1, LUTADORES[cols - 1]))]:
        x, y = celulas[cel]
        q = acoes[int(s[f"p{j}.cursor.active.anim"])][0]
        ox, oy = nums(s[f"p{j}.cursor.active.offset"])
        spr(tela, sys_spr, (q[0], q[1]), x + ox, y + oy)
        fx, fy = nums(s[f"p{j}.face.offset"])
        jan = tuple(int(v) for v in nums(s[f"p{j}.face.window"]))
        virar = int(nums(s[f"p{j}.face.facing"])[0]) < 0
        spr(tela, retrato_x4(chr_, 9000, 1, nums(s.get(f"p{j}.face.scale", "1"))[0]), (9000, 1), fx, fy, jan, virar)
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
        spr(tela, retrato_x4(chr_, 9000, 1, nums(v.get(f"p{j}.scale", "1"))[0]), (9000, 1), fx, fy, jan, int(nums(v[f"p{j}.facing"])[0]) < 0)
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
        spr(tela, sys_spr, (100, 0), 0, 0)   # fundo da abertura (Nazare ao por do sol)
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
        if f"p{j}.counter.font" in pb:   # o HUD de 2026-11-13 nao tem o numero do nivel (as pedrinhas contam)
            cf = nums(pb[f"p{j}.counter.font"])
            cx_, cy_ = nums(pb[f"p{j}.counter.offset"])
            escrever(tela, fontes[int(cf[0])], str(e["poder"] // 1000), qx + cx_, qy + cy_, int(cf[2]))
        # retrato
        fa = secao(fdefs, "face")
        fx, fy = nums(fa[f"p{j}.pos"])
        spr(tela, fig_spr, tuple(int(v) for v in nums(fa[f"p{j}.bg.spr"])), fx, fy)
        ox, oy = nums(fa[f"p{j}.face.offset"])
        virar = int(nums(fa.get(f"p{j}.face.facing", "1"))[0]) < 0
        spr(tela, retrato_x4(e["char"], 9000, 0, nums(fa.get(f"p{j}.face.scale", "1"))[0]), (9000, 0), fx + ox + (1 if virar else 0), fy + oy, virar=virar)
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
    escrever_sff2(MOTIF / "system.sff", finalizar(sprites_system(), "system") + sprites_titulo())
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
            # 300,1 ("?" da escolha aleatoria): o motor soma portrait.offset na posicao, entao o que tem de cair
            # na grade e o eixo menos esse deslocamento (a celula desenhada fica no mesmo pixel da vazia).
            dx = RETRATO_NA_CELULA if (sff.name, g, n) == ("system.sff", 300, 1) else 0
            if (ax - dx) % 4 or (ay - dx) % 4:
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
                if (k.endswith(".anim") or k == "actionno") and k != "stage.portrait.anim":  # essa e do .def do cenario
                    if int(nums(v)[0]) not in acoes:
                        raise SystemExit(f"ERRO: {nome_def} {k} = {v}: acao nao definida")
        for a, quadros in acoes.items():
            for q in quadros:
                if (q[0], q[1]) not in dados:
                    raise SystemExit(f"ERRO: {nome_def} acao {a} usa {q[0]},{q[1]} que nao existe")
        files = secao(secs, "files")
        for k, v in files.items():
            if (k.startswith("font") or k == "module") and not (MOTIF / v).exists():
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
