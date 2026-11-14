"""Gera o layout NAZAFIGHTS (screenpack do IKEMEN GO v1.0.0) inteiro por codigo, mais as previas.

Uso:  python ferramentas/gerar_layout.py            (gera tudo; sai com codigo 0 se passou nas checagens)

Saidas:
  motif/nazafight/system.def system.sff fight.def fight.sff fonts/*.def fonts/*.sff
  docs/previas-layout/titulo.png selecao.png vs.png hud.png   (1280x720)

Regras (docs/regras-dos-lutadores.md, AGENTS.md e a direcao do layout):
  * pixel art: as telas e o HUD do estilo novo (issue #39) sao desenhados numa grade de 2x (640x360 na tela
    cheia) e as fontes de menu numa de 4x, sempre ampliadas por vizinho mais proximo; todo eixo de sprite e
    multiplo de 4 e toda posicao no .def e o valor final;
  * a abertura e a cena de Nazare do ChatGPT (sprites/titulo) com animacao por cima: agua, sol, aves, brasas e
    brilho no logo;
  * so as cores de PALETA (Nazare + as 15 do estilo novo ARENA); o gerador falha se achar pixel de outra cor;
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


def loop_da_musica(arquivo):
    """loopstart (amostras) da faixa em musicas/loops.json, feito por converter_musicas.py; 0 se não tiver."""
    import json
    loops = RAIZ / "musicas" / "loops.json"
    if not loops.exists():
        return 0
    for faixa in json.loads(loops.read_text(encoding="utf-8")).values():
        if faixa["arquivo"] == arquivo:
            return int(faixa["loopstart"])
    return 0
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
    # HUD novo (issue #39, grade 2x): retrato 104 px nas pontas, vida de 468 px ate o relogio, nome pequeno embaixo
    # da vida, vitorias (losangos) junto do relogio e o poder fino no rodape (pes em y = 660).
    "vida_p1": (128, 18), "vida_p2": (684, 18),
    "relogio": (640, 12),            # centro x, topo y da caixa do relogio (80 x 56)
    "face_p1": (16, 12), "face_p2": (1160, 12),      # canto da moldura (104 x 104)
    "nome_p1": (140, 66), "nome_p2": (1140, 66),     # P1: x da esquerda; P2: x da direita; y = linha de base
    "vitoria_p1": (582, 54), "vitoria_p2": (684, 54),
    "poder_p1": (16, 688),           # canto da barra de poder (P1; a do P2 e o espelho)
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


def fonte_texto(nome, com_acentos, corpo, sombra, alto_luz=None, k=ESCALA):
    """Fonte de letras (tabuleta). Devolve (sprites, def_texto, glifos_logicos). k = grade (4 ou 2 no HUD novo)."""
    glifos = {}
    for ch in chars_texto():
        if not com_acentos and (ch.upper() in ACENTUADAS or ch == "•"):
            continue
        glifos[ch] = render_glifo(glifo_letra(ch, com_acentos), corpo, sombra, alto_luz)
    alto = 11 if com_acentos else 8
    for ch, g in list(glifos.items()):
        if g.height != alto:
            raise SystemExit(f"glifo {ch!r} de {nome} com altura {g.height} != {alto}")
    sprites = [(0, ord(ch), ampliar(g, k), 0, 0) for ch, g in glifos.items()]
    d = def_fonte(nome, 4 * k, alto * k, k)
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


def fonte_relogio(nome, corpo, alto_luz, base_esc, zero_na_frente, k=ESCALA):
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
    sprites = [(0, ord(ch), ampliar(g, k), 0, 0) for ch, g in glifos.items()]
    return sprites, def_fonte(nome, w * k, h * k, RELOGIO_VAO * k), glifos


def def_fonte(nome, larg_espaco, alto, espaco):
    return (f"; Fonte {nome} do Nazafights, desenhada por codigo (ferramentas/gerar_layout.py)\n"
            f"[FNT v2]\nfntversion = 2,00\nname = \"{nome}\"\nauthor = \"Nazafights\"\n\n"
            f"[Def]\nType = bitmap\nBankType = palette\nSize = {larg_espaco},{alto}\n"
            f"Spacing = {espaco},0\nOffset = 0,0\nFile = {nome}.sff\n")


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


# ----------------------------------------------------------------------------------------------------------
# ESTILO NOVO "ARENA" (Breno, missao de 2026-11-14, issue #39): mais moderno com cara de jogo de luta.
# Fundo de noite azulada, paineis inclinados, P1 em laranja (fogo) e P2 em azul (mar), ouro so no destaque.
# Desenhado numa grade de 2x (640x360 de desenho na tela cheia): a linha fina de 2 px e o que da o ar moderno.
# Os textos que o motor escreve continuam nas fontes de grade 4x; a fonte do HUD e o relogio sao de grade 2x.
# ----------------------------------------------------------------------------------------------------------
ARENA = {
    "noite": (0x0D, 0x0E, 0x1A),
    "noite2": (0x16, 0x18, 0x29),
    "aco": (0x23, 0x26, 0x3D),
    "aco2": (0x33, 0x38, 0x5A),
    "aco3": (0x4C, 0x54, 0x80),
    "nevoa": (0x88, 0x90, 0xB8),
    "giz": (0xEE, 0xF0, 0xF8),
    "fogo_esc": (0x9A, 0x34, 0x12),
    "fogo": (0xF2, 0x6B, 0x1D),
    "fogo_cl": (0xFF, 0xB3, 0x47),
    "mar_esc": (0x0E, 0x5A, 0x78),
    "mar": (0x1F, 0xB3, 0xD6),
    "mar_cl": (0x8B, 0xE6, 0xF7),
    "ouro": (0xFF, 0xD2, 0x3F),
    "sangue": (0xE0, 0x28, 0x3C),
}
PALETA.update(ARENA)
G2 = 2                                     # grade do estilo novo: 1 px de desenho = 2x2 na tela
LADO = {1: ("fogo_esc", "fogo", "fogo_cl"), 2: ("mar_esc", "mar", "mar_cl")}


def paralelo(w, h, incl=2, lado=1):
    """Mascara de paralelogramo w x h: a borda anda 1 px a cada 'incl' linhas. lado 1 = '/', -1 = '\\'."""
    m = np.zeros((h, w), bool)
    d = (h - 1) // incl
    for y in range(h):
        s = (h - 1 - y) // incl if lado > 0 else y // incl
        m[y, s:s + w - d] = True
    return m


def quinas(w, h, k=2):
    """Retangulo com as quinas de cima-esquerda e baixo-direita cortadas em diagonal (k px)."""
    m = np.ones((h, w), bool)
    for i in range(k):
        m[i, :k - i] = False
        m[h - 1 - i, w - k + i:] = False
    return m


def pintar_painel(m, fundo, borda, fora="noite", luz=None):
    """Pinta a mascara m (ja com 1 px de folga em volta): miolo 'fundo', 1 px de 'borda' por dentro, 1 px de 'fora'
    por fora e, se pedir, a linha de cima em 'luz'. Devolve a imagem."""
    h, w = m.shape
    a = np.zeros((h, w, 4), np.uint8)
    if fundo:
        a[m] = cor(fundo)
    anel = m & ~erodir(m, diag=True)
    if borda:
        a[anel] = cor(borda)
    if luz:
        a[anel & ~deslocar(m, 0, 1)] = cor(luz)
    if fora:
        a[dilatar(m, diag=True) & ~m] = cor(fora)
    return de_arr(a)


def folga(m, k=1):
    return np.pad(m, k)


def listras(w, h, nome, passo=8, larg=1, lado=1, fase=0):
    """Riscos diagonais finos (a textura de fundo do estilo novo)."""
    yy, xx = np.mgrid[0:h, 0:w]
    sel = ((xx + (yy if lado > 0 else -yy) + fase) % passo) < larg
    a = np.zeros((h, w, 4), np.uint8)
    a[sel] = cor(nome)
    return de_arr(a)


def recortar(img, m):
    """Deixa so o que esta dentro da mascara m."""
    a = arr(img)
    a[~m] = 0
    return de_arr(a)


def texto2(texto, escala, corpo, sombra="noite", contorno_cor=None):
    """Texto nas LETRAS 5x7 (grade 2x). Sombra dura de 1 px e, se pedir, contorno."""
    t = texto_bits(texto, escala, corpo, sombra, 1)
    if contorno_cor:
        g = nova(t.width + 2, t.height + 2)
        g.alpha_composite(t, (1, 1))
        t = contorno(g, contorno_cor, diag=True)
    return t


def inclinar(img, incl=4):
    """Itálico de pixel: cada 'incl' linhas de cima andam 1 px para a direita."""
    w, h = img.size
    d = (h - 1) // incl
    out = nova(w + d, h)
    for y in range(h):
        out.alpha_composite(img.crop((0, y, w, y + 1)), ((h - 1 - y) // incl, y))
    return out


# ---------------------------------- HUD (fight.sff, grade 2x) ----------------------------------------------
HUD2 = {
    "face": 52,                       # moldura do retrato (2 px de anel + o rosto 100x100 em 1/4)
    "vida": (234, 14),                # barra de vida P1 (468 x 28 px), inclinada '/'
    "poder": (150, 10),               # trilho de poder (300 x 20 px)
    "gema": 8, "gema_passo": 10,      # estoques (losangos)
    "relogio": (40, 28),              # caixa do relogio (80 x 56 px)
}


def barra2(w, h, incl=2):
    """Trilho inclinado: fundo noite2, anel aco3, brilho de cima nevoa, contorno noite. Devolve (img, miolo)."""
    m = folga(paralelo(w - 2, h - 2, incl, 1))
    img = pintar_painel(m, "noite2", "aco3", "noite", luz="nevoa")
    return img, erodir(m, diag=True)


def enchimento2(miolo, corpo, luz, sombra, brilho=None):
    """Enchimento recortado no miolo do trilho (mesmo tamanho do trilho, o .def usa a caixa do miolo)."""
    ys, xs = np.nonzero(miolo)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    h = y1 - y0 + 1
    a = np.zeros(miolo.shape + (4,), np.uint8)
    yy = np.arange(miolo.shape[0])[:, None] + np.zeros(miolo.shape, int)
    a[miolo] = cor(corpo)
    a[miolo & (yy == y0)] = cor(luz)
    a[miolo & (yy >= y1 - max(1, h // 4) + 1)] = cor(sombra)
    if brilho:
        xx = np.arange(miolo.shape[1])[None, :] + np.zeros(miolo.shape, int)
        a[miolo & (yy == y0 + 1) & ((xx % 24) < 6)] = cor(brilho)
    return de_arr(a[y0:y1 + 1, x0:x1 + 1]), (int(x0), int(y0), int(x1 - x0 + 1), int(h))


def vida_sprites():
    w, h = HUD2["vida"]
    trilho, miolo = barra2(w, h)
    cores = {"alta": ("ouro", "giz", "fogo_cl", "giz"), "media": ("fogo", "fogo_cl", "fogo_esc", None),
             "baixa": ("sangue", "fogo_cl", "fogo_esc", None), "fantasma": ("giz", "giz", "nevoa", None)}
    ench = {k: enchimento2(miolo, *v) for k, v in cores.items()}
    caixa = ench["alta"][1]
    return trilho, {k: v[0] for k, v in ench.items()}, caixa


def losango(n, corpo, luz, borda="noite"):
    m = np.zeros((n, n), bool)
    c = (n - 1) / 2
    yy, xx = np.mgrid[0:n, 0:n]
    m[np.abs(xx - c) + np.abs(yy - c) <= c + 0.01] = True
    a = np.zeros((n, n, 4), np.uint8)
    a[m] = cor(corpo)
    a[m & (yy + xx <= c + 1) & ~(erodir(m, diag=True))] = cor(luz)
    a[m & ~erodir(m, diag=False) & (yy + xx > c + 1)] = cor(borda)
    return de_arr(a)


def gema2(estado):
    n = HUD2["gema"]
    return {"vazia": losango(n, "noite2", "aco3", "aco2"), "meia": losango(n, "mar_esc", "mar", "noite"),
            "cheia": losango(n, "ouro", "giz", "fogo")}[estado]


def poder_sprites():
    w, h = HUD2["poder"]
    trilho, miolo = barra2(w, h)
    cheio, caixa = enchimento2(miolo, "mar", "mar_cl", "mar_esc")
    pronto, _ = enchimento2(miolo, "ouro", "giz", "fogo_cl")
    compostos = []
    larg = w + 4 + 3 * HUD2["gema_passo"]
    for k in range(7):
        img = nova(larg, max(h, HUD2["gema"]))
        img.alpha_composite(trilho, (0, 0))
        for i in range(3):
            est = "cheia" if i < k // 2 else ("meia" if i == k // 2 and k % 2 else "vazia")
            img.alpha_composite(gema2(est), (w + 4 + i * HUD2["gema_passo"], (h - HUD2["gema"]) // 2))
        compostos.append(img)
    return compostos, cheio, pronto, caixa


def face_sprites(jogador):
    n = HUD2["face"]
    escuro, base, claro = LADO[jogador]
    fundo = nova(n, n)
    ImageDraw.Draw(fundo).rectangle([0, 0, n - 1, n - 1], fill=cor(base))   # o anel fica no fundo: o motor
    ImageDraw.Draw(fundo).rectangle([1, 1, n - 2, n - 2], fill=cor("noite2"))  # desenha o top antes do rosto
    fundo.alpha_composite(listras(n - 2, n - 2, "aco", 6, 1, 1), (1, 1))
    m = np.ones((n, n), bool)
    top = nova(n, n)
    a = arr(top)
    anel = m & ~erodir(m, diag=True)
    a[anel] = cor(base)
    a[0, :n // 3] = cor(claro)
    a[:n // 3, 0] = cor(claro)
    top = de_arr(a)
    racha = nova(n, n)
    d = ImageDraw.Draw(racha)
    for pts in [[(4, 2), (14, 16), (12, 26), (22, 36), (20, 49)], [(14, 16), (26, 14), (38, 6)],
                [(22, 36), (34, 34), (46, 44)], [(12, 26), (4, 30)]]:
        d.line(pts, fill=cor("noite"))
    return fundo, top, racha


def relogio2():
    w, h = HUD2["relogio"]
    m = folga(quinas(w - 2, h - 2, 4))
    m2 = m.copy()
    m2[:, :] = m
    img = pintar_painel(m, "noite", "aco3", "noite", luz="nevoa")
    a = arr(img)
    a[h - 2, 6:w - 6] = cor("ouro")            # risco de ouro embaixo
    return de_arr(a)


def bolinha2(ganha):
    return losango(7, "ouro", "giz", "fogo") if ganha else losango(7, "noite2", "aco3", "aco2")


def letreiro2(texto, escala, corpo, luz, fundo_faixa=True):
    """Letreiro de round/luta: letra inclinada com contorno noite e uma faixa escura inclinada atras."""
    t = texto_bits(texto, escala, corpo, None)
    a = arr(t)
    m = a[:, :, 3] > 0
    a[m & ~deslocar(m, 0, 1)] = cor(luz)
    t = inclinar(de_arr(a), 4)
    g = nova(t.width + 4, t.height + 4)
    g.alpha_composite(t, (2, 2))
    g = contorno(contorno(g, "noite"), "noite")
    g = com_sombra(g, "noite", 2, 2)
    if not fundo_faixa:
        return g
    fw, fh = g.width + 40, g.height // 2 + 6
    faixa = pintar_painel(folga(paralelo(fw - 2, fh - 2, 1, 1)), "noite2", "aco3", None)
    out = nova(fw, g.height + 8)
    out.alpha_composite(faixa, (0, (out.height - fh) // 2 + 4))
    out.alpha_composite(g, ((fw - g.width) // 2, 2))
    return out


def ko2(q):
    """K.O.: clarao branco (q 0), depois vermelho com um brilho correndo da esquerda para a direita."""
    corpo = "giz" if q == 0 else "sangue"
    g = letreiro2("K.O.", 7, corpo, "giz" if q == 0 else "fogo_cl", fundo_faixa=False)
    if q >= 1:
        a = arr(g)
        m = (a[:, :, 3] > 0) & np.all(a[:, :, :3] == ARENA["sangue"], axis=2)
        yy, xx = np.mgrid[0:g.height, 0:g.width]
        x0 = (q - 1) * g.width // 4 - 10
        a[m & ((xx + yy // 2) >= x0) & ((xx + yy // 2) < x0 + 8)] = cor("giz")
        g = de_arr(a)
    out = nova(g.width + 8, g.height + 8)
    out.alpha_composite(g, (4, 4))
    return out


# ---------------------------------- telas (system.sff, grade 2x) -------------------------------------------
def fundo_arena(w=640, h=360, fase=0):
    img = nova(w, h)
    ImageDraw.Draw(img).rectangle([0, 0, w - 1, h - 1], fill=cor("noite"))
    img.alpha_composite(listras(w, h, "noite2", 10, 3, 1, fase))
    return img


def aba_titulo(w, h, texto=None, destaque="ouro"):
    """Aba do alto da tela: trapezio escuro com risco de destaque embaixo."""
    m = np.zeros((h, w), bool)
    for y in range(h):
        k = (h - 1 - y) // 2
        m[y, k:w - k] = True
    img = pintar_painel(folga(m), "noite2", "aco3", "noite")
    a = arr(img)
    a[h - 1, 4:w - 2] = cor(destaque)
    a[h, 4:w - 2] = cor(destaque)
    img = de_arr(a)
    if texto:
        t = texto2(texto, 2, "giz")
        img.alpha_composite(t, ((img.width - t.width) // 2, (img.height - t.height) // 2))
    return img


def painel_lado(w, h, jogador, inclinado=True):
    """Painel do retrato grande: fundo aco com riscos na cor do jogador, borda da cor e quinas cortadas."""
    escuro, base, claro = LADO[jogador]
    m = folga(quinas(w - 2, h - 2, 8))
    if jogador == 2:
        m = m[:, ::-1]
    img = pintar_painel(m, "aco", base, "noite", luz=claro)
    tex = recortar(listras(w, h, escuro, 7, 2, 1 if jogador == 1 else -1), erodir(m, diag=True))
    img.alpha_composite(tex)
    return img


def placa_nome(w, h, jogador):
    """Placa do nome: barra inclinada escura com o bloco da cor do jogador na ponta de fora."""
    escuro, base, claro = LADO[jogador]
    m = folga(paralelo(w - 2, h - 2, 2, 1 if jogador == 1 else -1))
    img = pintar_painel(m, "noite2", "aco3", "noite")
    a = arr(img)
    xs = np.nonzero(m.any(axis=0))[0]
    bloco = np.zeros_like(m)
    if jogador == 1:
        bloco[:, :xs.min() + 10] = True
    else:
        bloco[:, xs.max() - 9:] = True
    a[bloco & erodir(m, diag=True)] = cor(base)
    return de_arr(a)


def selecao_arena():
    """Selecao (200,0): paineis dos dois retratos, placas dos nomes, aba do modo, base da grade e marcas 1P/2P."""
    img = fundo_arena()
    rp1, rp2 = POS["retrato_p1"], POS["retrato_p2"]
    alto = POS["retrato_alto"]
    for j, (x, y) in [(1, rp1), (2, rp2)]:
        img.alpha_composite(painel_lado(448 // G2 + 4, alto // G2 + 4, j), (x // G2 - 2, y // G2 - 2))
    for j, c in [(1, POS["nome_sel_p1"]), (2, POS["nome_sel_p2"])]:
        pw = 180
        img.alpha_composite(placa_nome(pw, 24, j), (c[0] // G2 - pw // 2, c[1] // G2 - 22))
    img.alpha_composite(aba_titulo(220, 26), (210, 0))
    g = POS["grade"]
    cel, esp = POS["celula"], POS["celula_espaco"]
    gw = (POS["colunas"] * cel + (POS["colunas"] - 1) * esp) // G2
    gh = (POS["linhas"] * cel + (POS["linhas"] - 1) * esp) // G2
    base = pintar_painel(folga(quinas(gw + 14, gh + 14, 6)), "noite2", "aco2", "noite")
    img.alpha_composite(base, (g[0] // G2 - 8, g[1] // G2 - 8))
    for j, x in [(1, 24), (2, 476)]:
        marca = inclinar(texto_bits(f"{j}P", 10, "aco", None), 4)
        img.alpha_composite(marca, (x + (140 - marca.width) // 2, 214))
        escuro, base_c, claro = LADO[j]
        img.alpha_composite(pintar_painel(folga(paralelo(110, 4, 1, 1 if j == 1 else -1)), base_c, base_c, None),
                            (x + 14, 300))
    rodape = nova(640, 12)
    ImageDraw.Draw(rodape).rectangle([0, 0, 639, 11], fill=cor("noite2"))
    ImageDraw.Draw(rodape).line([0, 0, 639, 0], fill=cor("aco3"))
    img.alpha_composite(rodape, (0, 348))
    return img


def celula2(vazia=True):
    n = POS["celula"] // G2
    m = folga(quinas(n - 2, n - 2, 6))
    img = pintar_painel(m, "noite2", "aco3", None, luz="nevoa")
    if vazia:
        img.alpha_composite(recortar(listras(n, n, "aco", 6, 1, 1), erodir(m, diag=True)))
    return img


def celula_aleatoria2():
    img = celula2(vazia=False)
    t = texto2("?", 5, "ouro", "fogo_esc", "noite")
    img.alpha_composite(t, ((img.width - t.width) // 2, (img.height - t.height) // 2))
    return img


def cursor2(jogador, aceso):
    """Cantoneiras por fora da celula (80x100 com a etiqueta), P1 laranja a esquerda e P2 azul a direita."""
    escuro, base, claro = LADO[jogador]
    c = claro if aceso else base
    img = nova(80, 100)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 3, 23, 76, 96
    for (x, y, sx, sy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        for k in range(2):
            d.line([x, y + sy * k, x + sx * 14, y + sy * k], fill=cor(c))
            d.line([x + sx * k, y, x + sx * k, y + sy * 14], fill=cor(c))
    img = contorno(img, "noite", diag=False)
    eti = pintar_painel(folga(paralelo(28, 14, 2, 1 if jogador == 1 else -1)), c, c, "noite")
    t = texto_bits(f"{jogador}P", 1, "noite", None)
    eti.alpha_composite(t, ((eti.width - t.width) // 2 + (1 if jogador == 1 else -1), 4))
    img.alpha_composite(eti, (x0 if jogador == 1 else x1 - eti.width + 1, y0 - eti.height + 1))
    return img


def fundo_vs2():
    """VS (400,0): metade laranja e metade azul com riscos de velocidade, corte diagonal branco no meio, faixas
    escuras em cima e embaixo."""
    w, h = 640, 360
    a = np.zeros((h, w, 4), np.uint8)
    yy, xx = np.mgrid[0:h, 0:w]
    corte = 352 - yy * 64 // 360               # x do corte diagonal em cada linha
    esq = xx < corte
    a[esq] = cor("fogo_esc")
    a[~esq] = cor("mar_esc")
    risco_e = esq & (((xx + yy * 2) % 22) < 3)
    risco_d = ~esq & (((xx - yy * 2) % 22) < 3)
    a[risco_e] = cor("fogo")
    a[risco_d] = cor("mar")
    a[np.abs(xx - corte) <= 2] = cor("noite")
    a[np.abs(xx - corte) <= 1] = cor("giz")
    img = de_arr(a)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, 31], fill=cor("noite"))
    d.line([0, 32, w - 1, 32], fill=cor("ouro"))
    d.rectangle([0, 328, w - 1, h - 1], fill=cor("noite"))
    d.line([0, 327, w - 1, 327], fill=cor("aco3"))
    for j, x in [(1, 56), (2, 404)]:
        img.alpha_composite(placa_nome(180, 24, j), (x, 236))
    return img


def emblema_vs2():
    """Letras VS desenhadas a mao (a fonte 5x7 ampliada virava um 'LS'), italico, ouro com pe laranja."""
    w, h = 96, 62
    img = nova(w, h)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (15, 0), (23, 42), (31, 0), (46, 0), (32, 61), (14, 61)], fill=cor("ouro"))
    sx = 54
    for (x0, y0, x1, y1) in [(4, 0, 41, 13), (0, 4, 13, 30), (4, 24, 37, 37), (28, 31, 41, 57), (0, 48, 37, 61)]:
        d.rectangle([sx + x0, y0, sx + x1, y1], fill=cor("ouro"))
    for (x, y) in [(sx, 0), (sx + 41, 61)]:     # quinas cortadas do S
        d.polygon([(x, y), (x + (4 if x == sx else -4), y), (x, y + (4 if y == 0 else -4))], fill=(0, 0, 0, 0))
    a = arr(img)
    m = a[:, :, 3] > 0
    yy = np.mgrid[0:h, 0:w][0]
    a[m & (yy >= h * 2 // 3)] = cor("fogo")
    a[m & (yy >= h - 6)] = cor("fogo_esc")
    a[m & ~deslocar(m, 0, 1)] = cor("giz")
    a[m & ~deslocar(m, 0, 2) & deslocar(m, 0, 1)] = cor("giz")
    g = inclinar(de_arr(a), 3)
    big = nova(g.width + 8, g.height + 8)
    big.alpha_composite(g, (4, 4))
    big = contorno(contorno(big, "noite"), "noite")
    big = contorno(big, "giz", diag=False)
    return com_sombra(big, "noite", 3, 3)


def mapa_arena():
    """Escolha de mapa (210,0), por cima da selecao: aba, moldura da previa com quinas de ouro, setas, placa do
    nome e a dica dos botoes."""
    img = fundo_arena(fase=5)
    px, py = (v // G2 for v in POS["mapa_previa"])
    pw, ph = (v // G2 for v in POS["mapa_previa_tam"])
    img.alpha_composite(aba_titulo(220, 26, "ESCOLHA O MAPA"), (210, 0))
    mold = pintar_painel(folga(np.ones((ph + 6, pw + 6), bool)), "noite", "aco3", "noite", luz="nevoa")
    img.alpha_composite(mold, (px - 4, py - 4))
    d = ImageDraw.Draw(img)
    for (x, y, sx, sy) in [(px - 6, py - 6, 1, 1), (px + pw + 5, py - 6, -1, 1), (px - 6, py + ph + 5, 1, -1),
                           (px + pw + 5, py + ph + 5, -1, -1)]:
        for k in range(2):
            d.line([x, y + sy * k, x + sx * 18, y + sy * k], fill=cor("ouro"))
            d.line([x + sx * k, y, x + sx * k, y + sy * 18], fill=cor("ouro"))
    seta = nova(30, 44)
    ds = ImageDraw.Draw(seta)
    for k in range(3):
        ds.line([2 + k * 7, 2, 2 + k * 7 + 18, 22, 2 + k * 7, 42], fill=cor(["fogo_esc", "fogo", "ouro"][k]), width=4)
    seta = contorno(seta, "noite")
    cy = py + ph // 2 - seta.height // 2
    img.alpha_composite(seta, (px + pw + 14, cy))
    img.alpha_composite(espelhar(seta), (px - 14 - seta.width, cy))
    ny = POS["mapa_nome"][1] // G2
    pl = pintar_painel(folga(paralelo(260, 26, 2, 1)), "noite2", "aco3", "noite", luz="nevoa")
    a = arr(pl)
    a[pl.height - 3:pl.height - 1, 12:pl.width - 12] = cor("ouro")
    img.alpha_composite(de_arr(a), (320 - pl.width // 2, ny - 22))
    dica = texto2("ESQUERDA E DIREITA TROCAM   ENTER CONFIRMA", 1, "nevoa")
    img.alpha_composite(dica, ((640 - dica.width) // 2, 340))
    return img


def barra_menu2():
    """Item ativo do menu: barra inclinada laranja com setinhas de ouro (176x20 de desenho)."""
    w, h = 176, 20
    m = folga(paralelo(w - 2, h - 2, 2, 1))
    img = pintar_painel(m, "fogo_esc", "fogo", "noite", luz="fogo_cl")
    for x, s in [(14, 1), (w - 20, -1)]:
        sx = de_desenho(["#...", "##..", "###.", "##..", "#..."] if s > 0 else
                        ["...#", "..##", ".###", "..##", "...#"], {"#": "ouro"})
        img.alpha_composite(sx, (x, (h - 5) // 2))
    return img


def painel_menu2():
    """Painel escuro atras do menu (o motor deixa translucido pelo addalpha)."""
    x0, y0, x1, y1 = (v // G2 for v in POS["faixa_menu"])
    w, h = x1 - x0, y1 - y0
    m = folga(quinas(w - 2, h - 2, 8))
    img = pintar_painel(m, "noite", "aco3", "noite", luz="nevoa")
    a = arr(img)
    a[h - 3:h - 1, 10:w - 10] = cor("ouro")
    return de_arr(a)


# ----------------------------------------------------------------------------------------------------------
# Montagem dos SFF: (grupo, numero, imagem logica, eixo logico x, eixo logico y)
# Os eixos ficam em pixels logicos aqui e saem multiplicados por 4.
# ----------------------------------------------------------------------------------------------------------
def sprites_fight():
    """HUD do estilo novo (grade 2x): trilhos inclinados, enchimentos, retrato, relogio, vitorias e letreiros."""
    s = []
    trilho, ench, _ = vida_sprites()
    s += [(10, 0, trilho, 0, 0), (10, 1, espelhar(trilho), 0, 0)]
    for g, k in [(11, "alta"), (12, "media"), (13, "baixa"), (14, "fantasma")]:
        s += [(g, 0, ench[k], 0, 0), (g, 1, espelhar(ench[k]), 0, 0)]
    compostos, cheio, pronto, _ = poder_sprites()
    for k, c in enumerate(compostos):
        s += [(20, k, c, 0, 0), (20, 10 + k, espelhar(c), 0, 0)]
    for g, e in [(21, cheio), (22, pronto)]:
        s += [(g, 0, e, 0, 0), (g, 1, espelhar(e), 0, 0)]
    for j in (1, 2):
        fundo, top, racha = face_sprites(j)
        if j == 2:
            fundo, top, racha = espelhar(fundo), espelhar(top), espelhar(racha)
        s += [(30, j - 1, fundo, 0, 0), (31, j - 1, top, 0, 0), (32, j - 1, racha, 0, 0)]
    s.append((40, 0, relogio2(), HUD2["relogio"][0] // 2, 0))
    s += [(50, 0, bolinha2(False), 4, 4), (50, 1, bolinha2(True), 4, 4)]
    for n in range(1, 6):
        lt = letreiro2(f"ROUND {n}", 4, "giz", "nevoa")
        s.append((60, n, lt, lt.width // 4 * 2, lt.height // 4 * 2))
    lt = letreiro2("LUTA!", 6, "ouro", "giz")
    s.append((61, 0, lt, lt.width // 4 * 2, lt.height // 4 * 2))
    for q in range(6):
        k = ko2(q)
        s.append((62, q, k, k.width // 4 * 2, k.height // 4 * 2))
    return s


def sprites_system():
    """Telas do estilo novo (grade 2x)."""
    s = []
    s.append((131, 0, barra_menu2(), 88, 20))   # eixo: centro x; 20 = 40 px acima da linha de base do texto
    s.append((200, 0, selecao_arena(), 0, 0))
    s.append((210, 0, mapa_arena(), 0, 0))
    # O IKEMEN desenha cell.random.spr somando o portrait.offset (start.lua, updateDrawList), a celula
    # nao. Sem o eixo compensando, o "?" saia 14 px para baixo e para a direita da celula vazia.
    k = RETRATO_NA_CELULA / G2
    s += [(300, 0, celula2(True), 0, 0), (300, 1, celula_aleatoria2(), k, k)]
    for j, g in [(1, 310), (2, 311)]:
        s += [(g, 0, cursor2(j, True), 0, 0), (g, 1, cursor2(j, False), 0, 0)]
    s += [(312, 0, cursor2(1, True), 0, 0), (313, 0, cursor2(2, True), 0, 0)]
    s.append((400, 0, fundo_vs2(), 0, 0))
    em = emblema_vs2()
    s.append((400, 1, em, em.width // 4 * 2, em.height // 4 * 2))
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


# ---------------------------------- abertura animada (Breno, 2026-11-14) -----------------------------------
# A cena parada ganha movimento de verdade: o rio ondula (8 quadros so da agua), o sol pulsa, aves cruzam o ceu,
# brasas sobem pela tela e um brilho corre pelo logo de tempos em tempos. Tudo na grade 2x da cena.
AGUA = [(200, 410), (1130, 410), (1130, 470), (1090, 520), (1010, 580), (1000, 660), (250, 660), (250, 600),
        (200, 560)]                      # contorno da agua na tela (sem as barracas, os potes e os cestos)
BARCOS = [(225, 330, 380, 500), (1015, 330, 1145, 462), (940, 500, 1095, 538), (455, 412, 520, 432)]  # nao ondulam
AGUA_QUADROS, AGUA_TICKS = 8, 7
SOL = (240, 300)                         # centro do sol na tela


def caixa_agua():
    xs, ys = [x for x, _ in AGUA], [y for _, y in AGUA]
    return min(xs), min(ys), max(xs), max(ys)


def agua_quadros(fundo):
    """Ondas: cada linha da agua anda ate 2 px de desenho para os lados, em fase com a altura; brilhos piscando no
    reflexo do sol. Devolve os quadros recortados na caixa da agua (so os pixels de agua)."""
    cena = np.array(fundo.resize((640, 360), Image.NEAREST).convert("RGBA")).astype(np.uint8)
    x0, y0, x1, y1 = (v // G2 for v in caixa_agua())
    masc = Image.new("L", (640, 360), 0)
    dm = ImageDraw.Draw(masc)
    dm.polygon([(x // G2, y // G2) for x, y in AGUA], fill=255)
    for (bx0, by0, bx1, by1) in BARCOS:
        dm.rectangle([bx0 // G2, by0 // G2, bx1 // G2, by1 // G2], fill=0)
    m = np.array(masc) > 0
    rnd = random.Random(39)
    brilhos = [(rnd.randrange(112, 178), rnd.randrange(244, 322), rnd.randrange(AGUA_QUADROS)) for _ in range(26)]
    quadros = []
    for q in range(AGUA_QUADROS):
        out = np.zeros_like(cena)
        for y in range(y0, y1 + 1):
            perto = (y - y0) / max(1, y1 - y0)
            amp = 1 + round(perto)                  # 1 px la longe, 2 px perto
            dx = int(round(amp * np.sin(2 * np.pi * (y / 6.0 + q / AGUA_QUADROS))))
            linha = np.roll(cena[y], dx, axis=0)
            out[y][m[y]] = linha[m[y]]
        for (bx, by, fase) in brilhos:
            k = (q - fase) % AGUA_QUADROS
            if m[by, bx] and k < 3:
                out[by, bx] = (255, 244, 214, 255) if k == 1 else (255, 214, 140, 255)
                if k == 1:
                    for ddx in (-1, 1):
                        if m[by, bx + ddx]:
                            out[by, bx + ddx] = (255, 214, 140, 255)
        quadros.append(ampliar(Image.fromarray(out[y0:y1 + 1, x0:x1 + 1], "RGBA"), G2))
    return quadros


AVE = [["#.......#", ".#.....#.", "..##.##..", "....#...."],
       [".........", "###...###", "...###...", "....#...."],
       [".........", "...###...", ".##...##.", "#.......#"]]


def ave(q):
    img = nova(9, 4)
    px = img.load()
    for y, s in enumerate(AVE[q]):
        for x, ch in enumerate(s):
            if ch == "#":
                px[x, y] = (46, 20, 44, 255)
    return ampliar(img, G2)


def brasas(semente, n):
    """Folha de brasas (320x360 na tela) que se repete em ladrilho subindo; desenhada para soma (trans = add)."""
    rnd = random.Random(semente)
    img = nova(160, 180)
    px = img.load()
    for _ in range(n):
        x, y = rnd.randrange(1, 159), rnd.randrange(1, 179)
        c = rnd.choice([(220, 110, 20), (240, 150, 40), (180, 70, 10)])
        px[x, y] = c + (255,)
        if rnd.random() < 0.4:
            px[x + 1, y] = c + (255,)
        if rnd.random() < 0.5:
            px[x, y + 1] = (c[0] // 2, c[1] // 3, c[2] // 3, 255)
    return ampliar(img, G2)


def brilho_sol(forca):
    """Halo do sol para soma: aneis pontilhados que acendem a volta do sol (3 forcas)."""
    r = 50
    img = nova(2 * r, 2 * r)
    a = arr(img)
    yy, xx = np.mgrid[0:2 * r, 0:2 * r]
    dist = np.hypot(xx - r + 0.5, yy - r + 0.5) / r
    for lim, c, nivel in [(1.0, (40, 18, 6), 8), (0.75, (60, 28, 8), 12), (0.5, (80, 40, 10), 16)]:
        sel = (dist < lim) & (BAYER[yy % 4, xx % 4] < nivel * (0.6 + 0.2 * forca))
        a[sel] = c + (255,)
    return ampliar(de_arr(a), G2)


def brilho_logo(lg, q, n=12):
    """Faixa de luz inclinada correndo pelo logo (quadro q de n), so por cima das letras, para soma."""
    m = np.array(lg.getchannel("A").resize((lg.width // G2, lg.height // G2), Image.NEAREST)) > 0
    h, w = m.shape
    yy, xx = np.mgrid[0:h, 0:w]
    pos = -30 + q * (w + 60) / (n - 1)
    d = xx + yy // 2 - pos
    a = np.zeros((h, w, 4), np.uint8)
    a[m & (np.abs(d) < 9)] = (70, 70, 60, 255)
    a[m & (np.abs(d) < 4)] = (140, 140, 120, 255)
    return ampliar(de_arr(a), G2)


def sprites_titulo():
    """Sprites da abertura ja no tamanho da tela (nao passam por finalizar)."""
    lg = logo_titulo()
    fundo = fundo_titulo()
    s = [(0, 0, lg, lg.width // 2, 0), (100, 0, fundo, 0, 0), (130, 0, ampliar(painel_menu2(), G2), 0, 0)]
    s += [(101, q, img, 0, 0) for q, img in enumerate(agua_quadros(fundo))]
    s += [(102, q, ave(q), 8, 4) for q in range(3)]
    s += [(103, 0, brasas(1, 26), 0, 0), (103, 1, brasas(2, 16), 0, 0)]
    s += [(104, k, brilho_sol(k), 100, 100) for k in range(3)]
    s += [(105, q, brilho_logo(lg, q), lg.width // 2, 0) for q in range(12)]
    s.append((105, 99, nova(4, 4), 0, 0))
    return s


def finalizar(sprites, nome, k=ESCALA):
    out = []
    for (g, n, img, ax, ay) in sprites:
        checar_paleta(img, f"{nome} {g},{n}")
        out.append((g, n, ampliar(img, k), round(ax * k), round(ay * k)))
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

; Abertura animada (issue #39): rio ondulando, sol pulsando, aves, brasas subindo e brilho no logo.
[TitleBG Agua]
type = anim
actionno = 101
layerno = 0
start = {caixa_agua()[0] - 640},{caixa_agua()[1]}

[TitleBG Sol]
type = anim
actionno = 104
layerno = 0
start = {SOL[0] - 640},{SOL[1]}
trans = add

[TitleBG Ave1]
type = anim
actionno = 102
layerno = 0
start = 300,112
velocity = -0.7,0
tile = 1,0
tilespacing = 1500,0

[TitleBG Ave2]
type = anim
actionno = 103
layerno = 0
start = 520,146
velocity = -0.55,0
tile = 1,0
tilespacing = 1700,0

[TitleBG Ave3]
type = anim
actionno = 106
layerno = 0
start = 420,92
velocity = -0.8,0
tile = 1,0
tilespacing = 1900,0

[TitleBG Brasas1]
type = normal
spriteno = 103,0
layerno = 0
start = -640,0
velocity = 0.25,-0.7
tile = 1,1
trans = add

[TitleBG Brasas2]
type = normal
spriteno = 103,1
layerno = 0
start = -480,90
velocity = 0.12,-0.4
tile = 1,1
trans = add

[TitleBG Faixa]
type = normal
spriteno = 130,0
layerno = 0
start = {POS['faixa_menu'][0] - 640},{POS['faixa_menu'][1]}
trans = addalpha
alpha = 200,56

[TitleBG Logo]
type = anim
actionno = 120
layerno = 0
start = {POS['logo'][0] - 640},{POS['logo'][1]}

[TitleBG BrilhoLogo]
type = anim
actionno = 121
layerno = 0
start = {POS['logo'][0] - 640},{POS['logo'][1]}
trans = add

[Begin Action 101]
{''.join(f'101,{q}, 0,0, {AGUA_TICKS}' + chr(10) for q in range(AGUA_QUADROS))}
[Begin Action 102]
102,0, 0,0, 6
102,1, 0,0, 6
102,2, 0,0, 6
102,1, 0,0, 6

[Begin Action 103]
102,1, 0,0, 7
102,2, 0,0, 7
102,1, 0,0, 7
102,0, 0,0, 7

[Begin Action 106]
102,2, 0,0, 5
102,1, 0,0, 5
102,0, 0,0, 5
102,1, 0,0, 5

[Begin Action 104]
104,0, 0,0, 24
104,1, 0,0, 24
104,2, 0,0, 24
104,1, 0,0, 24

[Begin Action 120]
0,0, 0,-300, 2
0,0, 0,-190, 2
0,0, 0,-90, 2
0,0, 0,0, 2
0,0, 0,14, 2
0,0, 0,-8, 2
0,0, 0,4, 2
0,0, 0,-2, 2
Loopstart
0,0, 0,0, 28
0,0, 0,-2, 28
0,0, 0,-4, 28
0,0, 0,-2, 28

; brilho no logo: comeca junto do balanco (18 ticks da queda) e roda a cada 224 ticks = 2 balancos, sempre no
; quarto quadro do balanco (logo 2 px acima)
[Begin Action 121]
105,99, 0,0, 18
Loopstart
105,99, 0,0, 200
{''.join(f'105,{q}, 0,-2, 2' + chr(10) for q in range(12))}

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
title.offset = 640,48
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
match.offset = 640,54
match.text = LUTA %i
; Busto em tamanho natural (1/4 do 4x do motor = 448x216, nitido), em pe sobre a placa do nome, sem corte
; (Breno, 2026-11-14: os de antes eram grandes demais e saiam cortados).
p1.spr = 9000,1
p1.offset = 68,254
p1.facing = 1
p1.scale = 0.25,0.25
p1.window = 0,66,640,654
p2.spr = 9000,1
p2.offset = 1212,254
p2.facing = -1
p2.scale = 0.25,0.25
p2.window = 640,66,1280,654
p1.name.font = 1,0,0
p1.name.offset = 292,518
p2.name.font = 1,0,0
p2.name.offset = 988,518

[VersusBGdef]
bgclearcolor = 20,12,16

[VersusBG Pano]
type = normal
spriteno = 400,0
layerno = 0
start = -640,0

[VersusBG Emblema]
type = anim                      ; anim respeita o alfa do PNG; o tipo normal desenhava uma caixa preta em volta
actionno = 401
layerno = 0
start = 0,360

[Begin Action 401]
400,1, 0,0, -1

; Trilha (Suno, escolhida pelo Breno; OGG feito por ferramentas/converter_musicas.py). Caminho relativo a esta pasta.
; Musica e por tela, nunca por lutador. Luta: bgmusic do cenario. Despertar: PlayBGM no lutador.
; Loop sem emenda (issue #33): o arquivo termina no fim do loop e volta em loopstart (amostras de 44,1 kHz).
[Music]
title.bgm = musicas/lobby.ogg
title.bgm.volume = 100
title.bgm.loop = 1
title.bgm.loopstart = {loop_da_musica("motif/nazafight/musicas/lobby.ogg")}
select.bgm = musicas/selecao.ogg
select.bgm.volume = 100
select.bgm.loop = 1
select.bgm.loopstart = {loop_da_musica("motif/nazafight/musicas/selecao.ogg")}

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
    k = G2
    _t, _e, (vx, vy, vw, vh) = vida_sprites()
    VW = HUD2["vida"][0]
    vx2 = VW - vx - vw                          # o trilho do P2 e o espelho do P1
    vida = {1: (vx * k, f"{vx * k},{(vx + vw) * k - 1}"), 2: (vx2 * k, f"{(vx2 + vw) * k - 1},{vx2 * k}")}
    vy = vy * k
    compostos, _c, _p, (px, py, pw, ph) = poder_sprites()
    CW = compostos[0].width
    px2 = CW - px - pw
    p1 = POS["poder_p1"]
    p2 = (1280 - p1[0] - CW * k, p1[1])
    poder = {1: (p1, 0, px * k, f"{px * k},{(px + pw) * k - 1}"), 2: (p2, 10, px2 * k, f"{(px2 + pw) * k - 1},{px2 * k}")}
    py0 = py * k
    f1, f2 = POS["face_p1"], POS["face_p2"]
    nm1, nm2 = POS["nome_p1"], POS["nome_p2"]
    w1, w2 = POS["vitoria_p1"], POS["vitoria_p2"]
    rx, ry = POS["relogio"]
    rel_y = (HUD2["relogio"][1] * k - RELOGIO_GLIFO[1] * k) // 2 + RELOGIO_GLIFO[1] * k - 1
    face_dentro = k                              # o retrato comeca 1 px de desenho dentro da moldura
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
font2 = fonts/naza_relogio2_alerta.def
font3 = fonts/naza_hud.def
font4 = fonts/naza_menu.def
font5 = fonts/naza_relogio2.def
fightfx.sff = fightfx.sff     ; data/
fightfx.air = fightfx.air
common.snd = common.snd

[FightFx]
scale = 4

; Vida (estilo novo, issue #39): trilho fino inclinado. A vida fica presa na ponta de fora (junto do retrato) e o dano
; abre junto do relogio: o motor prende o enchimento no 1o valor de range.x. Ouro > 50%, laranja 26-50%, vermelho <= 25%;
; o dano que ainda vai cair fica em branco.
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

; Poder: trilho fino azul + 3 losangos de estoque (vazio -> enchendo -> pronto, em ouro). levelbars = enche de novo
; a cada estoque; com 3 estoques a barra fica de ouro.
[Powerbar]
"""
    for j in (1, 2):
        pos, base, px0, faixa = poder[j]
        sufixo = j - 1
        t += f"p{j}.pos = {pos[0]},{pos[1]}\n"
        t += f"p{j}.bg0.spr = 20,{base}\n"
        for nv in range(1, 7):
            t += f"p{j}.bg0{nv * 500}.spr = 20,{base + nv}\n"
        t += f"p{j}.front.spr = 21,{sufixo}\np{j}.front.offset = {px0},{py0}\n"
        t += f"p{j}.front3000.spr = 22,{sufixo}\np{j}.front3000.offset = {px0},{py0}\n"
        t += f"p{j}.range.x = {faixa}\np{j}.levelbars = 1\n"
    t += f"""
; Retrato pequeno: fundo escuro riscado atras, 9000,0 do lutador (100x100), anel fino na cor do jogador por cima.
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
p2.face.offset = {HUD2['face'] * k - face_dentro},{face_dentro}
p2.face.facing = -1
p2.face.scale = 0.25,0.25
p2.ko.spr = 32,1
p2.top.spr = 31,1
[Simul Face]
[Turns Face]
[Tag Face]

[Name]
p1.pos = {nm1[0]},{nm1[1]}
p1.name.font = 3,0,1
p2.pos = {nm2[0]},{nm2[1]}
p2.name.font = 3,0,-1
[Simul Name]
[Turns Name]
[Tag Name]

; Relogio: caixinha escura de quinas cortadas com 2 digitos (fonte 5, grade 2x); abaixo de 10 s, fonte 2 em vermelho,
; cujos glifos ja trazem o zero na frente (o motor escreve 8, a tela mostra 08).
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

; Vitorias: losangos junto do relogio; escuro = falta ganhar, ouro = round ganho.
[WinIcon]
useiconupto = 4
"""
    for j, (pos, dx) in enumerate([(w1, -18), (w2, 18)], start=1):
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
            if "," in s:                       # "Loopstart" nao e quadro
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
        "naza_menu_ativo": fonte_texto("naza_menu_ativo", True, "giz", "noite"),
        "naza_hud": fonte_texto("naza_hud", False, "giz", "noite", k=G2),
        "naza_relogio2": fonte_relogio("naza_relogio2", "giz", "giz", "nevoa", False, k=G2),
        "naza_relogio2_alerta": fonte_relogio("naza_relogio2_alerta", "sangue", "fogo_cl", "fogo_esc", True, k=G2),
    }
    for nome, (sprites, d, glifos) in fontes_geradas.items():
        for ch, g in glifos.items():
            checar_paleta(g, f"fonte {nome} {ch!r}")
        escrever_sff2(MOTIF / "fonts" / f"{nome}.sff", sprites)
        (MOTIF / "fonts" / f"{nome}.def").write_text(d, encoding="utf-8", newline="\n")
    escrever_sff2(MOTIF / "fight.sff", finalizar(sprites_fight(), "fight", G2))
    escrever_sff2(MOTIF / "system.sff", finalizar(sprites_system(), "system", G2) + sprites_titulo())
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
