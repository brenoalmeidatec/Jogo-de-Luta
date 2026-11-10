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
    # HUD (fight.def). Trilho de vida: canto superior esquerdo da prancha.
    "vida_p1": (32, 24), "vida_p2": (736, 24),
    "relogio": (640, 8),             # centro x, topo y do caxixi
    "face_p1": (32, 84), "face_p2": (1136, 84),
    "nome_p1": (152, 88), "nome_p2": (1128, 88),     # topo do texto
    "vitoria_p1": (152, 128), "vitoria_p2": (1104, 128),
    "poder_p1": (32, 664), "poder_p2": (864, 664),
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
    "grade": (372, 448), "celula": 128, "celula_espaco": 8, "colunas": 4, "linhas": 2,
    "retrato_p1": (24, 64), "retrato_p2": (816, 64),
    "nome_sel_p1": (192, 497), "nome_sel_p2": (1088, 497),   # centro x, linha de base
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


def gradiente_v(img, x0, y0, x1, y1, paradas):
    """Faixas verticais com pontilhado Bayer entre cores vizinhas. paradas: [(y, nome), ...] crescente."""
    d = ImageDraw.Draw(img)
    for y in range(y0, y1 + 1):
        for i in range(len(paradas) - 1):
            ya, ca = paradas[i]
            yb, cb = paradas[i + 1]
            if ya <= y <= yb:
                t = (y - ya) / max(1, yb - ya)
                for x in range(x0, x1 + 1):
                    nome = cb if t * 16 > BAYER[y % 4][x % 4] + 0.5 else ca
                    d.point((x, y), fill=cor(nome))
                break


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


def def_fonte(nome, larg_espaco, alto, espaco):
    return (f"; Fonte {nome} do Nazafight, desenhada por codigo (ferramentas/gerar_layout.py)\n"
            f"[FNT v2]\nfntversion = 2,00\nname = \"{nome}\"\nauthor = \"Nazafight\"\n\n"
            f"[Def]\nType = bitmap\nBankType = palette\nSize = {larg_espaco},{alto}\n"
            f"Spacing = {espaco},0\nOffset = 0,0\nFile = {nome}.sff\n")


# ----------------------------------------------------------------------------------------------------------
# Motivos de Maragogipinho: espiral de tabatinga, azulejo (so atras do relogio), caxixi
# ----------------------------------------------------------------------------------------------------------
ESPIRAL = [".###.", "#...#", "#.#.#", "#..#.", ".#..."]


def friso_espiral(img, x0, y0, x1, nome, passo=6, meia=True):
    """Fileira de espirais pequenas (5x5) de x0 a x1; meia=True pontilha 50% (tinta rala de tabatinga)."""
    px = img.load()
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
ALCA = 6  # largura logica da alca de moringa que sai da ponta de fora do trilho


def trilho_vida():
    """Prancha de saveiro 128x14 + alca de moringa (6 px) na ponta de fora (esquerda = P1). 134x14."""
    A = ALCA
    img = nova(128 + A, 14)
    d = ImageDraw.Draw(img)
    d.ellipse([0, 1, 13, 12], fill=cor("taua"))
    d.ellipse([3, 4, 10, 9], fill=(0, 0, 0, 0))
    a = arr(img)
    a[:, A + 2:] = 0
    img = de_arr(a)
    px = img.load()
    for (x, y) in [(2, 2), (1, 3), (1, 4), (3, 2), (4, 2)]:
        if px[x, y][3]:
            px[x, y] = cor("taua_vivo")
    for (x, y) in [(1, 8), (2, 10), (3, 11), (4, 11), (1, 9)]:
        if px[x, y][3]:
            px[x, y] = cor("taua_esc")
    img = contorno(img, "breu", diag=False)
    d = ImageDraw.Draw(img)
    d.rectangle([A, 0, A + 127, 13], fill=cor("madeira"))
    d.line([A, 1, A + 127, 1], fill=cor("madeira_cl"))
    d.line([A, 12, A + 127, 12], fill=cor("barro"))
    px = img.load()
    for x in range(A + 1, A + 127):   # faixa pintada de saveiro: tabatinga em cima, tauá vivo embaixo
        if (x - A) % 6 in (1, 2, 3):
            px[x, 1] = cor("tabatinga")
        if (x - A) % 6 in (4, 5, 0):
            px[x, 12] = cor("taua_vivo")
    for cx in (A + 1, A + 125):      # cavilhas nas pontas
        for (x, y, c) in [(0, 5, "tabatinga"), (1, 5, "tabatinga"), (0, 6, "tabatinga"), (1, 6, "madeira_cl"),
                          (0, 7, "madeira_cl"), (1, 7, "barro"), (0, 9, "barro"), (1, 3, "madeira_cl")]:
            px[cx + x, y] = cor(c)
    d.rectangle([A + 4, 2, A + 123, 11], fill=cor("breu"))
    for x in range(A + 4, A + 124):
        for y in range(2, 12):
            if (x * 3 + y * 5) % 11 == 0:
                px[x, y] = cor("barro")
    d.rectangle([A, 0, A + 127, 13], outline=cor("breu"))
    for (x, y) in [(A, 0), (A + 127, 0), (A, 13), (A + 127, 13)]:
        px[x, y] = (0, 0, 0, 0)
    return img


def enchimento_vida(corpo, luz, escuro):
    img = nova(120, 10)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 119, 9], fill=cor(corpo))
    d.line([0, 8, 119, 8], fill=cor(escuro))
    d.line([0, 9, 119, 9], fill=cor(escuro))
    px = img.load()
    for x in range(120):
        if x % 2 == 0:
            px[x, 0] = cor(luz)
        if x % 4 == 1:
            px[x, 1] = cor(luz)
    friso_espiral(img, 2, 3, 120, "tabatinga", passo=7, meia=True)
    return img


def fantasma_vida():
    img = nova(120, 10)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 119, 9], fill=cor("farinha"))
    d.line([0, 0, 119, 0], fill=cor("tabatinga"))
    d.line([0, 9, 119, 9], fill=cor("dende"))
    return img


def estoque(estado):
    """Caxixi de estoque 8x10: cru, quente ou cozido."""
    if estado == "cru":
        return caxixi(8, 10, "madeira_cl", "tabatinga", "madeira")
    if estado == "quente":
        return caxixi(8, 10, "taua_esc", "taua", "barro", friso="taua_vivo")
    return caxixi(8, 10, "taua", "taua_vivo", "taua_esc", friso="tabatinga", brilho="farinha")


def trilho_poder():
    img = nova(96, 6)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 95, 5], fill=cor("madeira"))
    d.line([1, 1, 94, 1], fill=cor("madeira_cl"))
    d.rectangle([3, 1, 92, 4], fill=cor("breu"))
    d.rectangle([0, 0, 95, 5], outline=cor("breu"))
    px = img.load()
    for x in (1, 94):
        px[x, 2] = cor("tabatinga")
        px[x, 3] = cor("barro")
    for x in (0, 95):
        px[x, 0] = (0, 0, 0, 0)
        px[x, 5] = (0, 0, 0, 0)
    return img


def composto_poder(nivel_x2):
    """Trilho de poder + 3 estoques; nivel_x2 = poder/500 (0..6). P1: trilho a esquerda, estoques a direita."""
    img = nova(125, 10)
    img.alpha_composite(trilho_poder(), (0, 4))
    cozidos = nivel_x2 // 2
    for i in range(3):
        if i < cozidos:
            est = "cozido"
        elif i == cozidos and nivel_x2 % 2 == 1:
            est = "quente"
        else:
            est = "cru"
        img.alpha_composite(estoque(est), (99 + 9 * i, 0))
    return img


def enchimento_poder(corpo, luz, faisca):
    img = nova(90, 4)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 89, 3], fill=cor(corpo))
    d.line([0, 0, 89, 0], fill=cor(luz))
    px = img.load()
    for x in range(90):
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
    img = nova(16, 16)
    pedacos = [(0, 0, 4, 5), (4, 0, 8, 5), (0, 5, 4, 10), (4, 5, 8, 10)]
    desl = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    for (x0, y0, x1, y1), (dx, dy) in zip(pedacos, desl):
        p = de_arr(a[y0:y1, x0:x1].copy())
        k = q * 2
        img.alpha_composite(p, (4 + x0 + dx * k, 3 + y0 + dy * k))
    if q >= 2:
        img = pontilhar(img, dilatar(opaco(img)) & ~opaco(img), "farinha", 4 + q)
    return img


def moldura_face(top=True):
    """Anel de barro 28x28 (top) ou fundo de reserva com pano listrado e silhueta generica."""
    img = nova(28, 28)
    d = ImageDraw.Draw(img)
    if top:
        d.rectangle([0, 0, 27, 27], fill=cor("taua"))
        d.rectangle([2, 2, 25, 25], fill=(0, 0, 0, 0))
        d.line([1, 1, 26, 1], fill=cor("taua_vivo"))
        d.line([1, 1, 1, 26], fill=cor("taua_vivo"))
        d.line([1, 26, 26, 26], fill=cor("taua_esc"))
        d.line([26, 1, 26, 26], fill=cor("taua_esc"))
        d.rectangle([0, 0, 27, 27], outline=cor("breu"))
        px = img.load()
        for (cx, cy) in [(0, 0), (27, 0), (0, 27), (27, 27)]:
            sx = 1 if cx == 0 else -1
            sy = 1 if cy == 0 else -1
            px[cx, cy] = (0, 0, 0, 0)
            for (x, y) in [(1, 1), (2, 1), (3, 1), (1, 2), (1, 3), (3, 2), (2, 3), (3, 3)]:
                px[cx + sx * x, cy + sy * y] = cor("tabatinga")
            px[cx + sx * 2, cy + sy * 2] = cor("taua_esc")
        return img
    for y in range(28):
        d.line([0, y, 27, y], fill=cor("taua_esc" if (y // 3) % 2 == 0 else "barro"))
    d.ellipse([9, 6, 18, 16], fill=cor("madeira"))
    d.ellipse([4, 15, 23, 33], fill=cor("madeira"))
    d.rectangle([12, 15, 15, 17], fill=cor("madeira"))
    return img


def rachaduras_face():
    img = nova(28, 28)
    d = ImageDraw.Draw(img)
    for pts in [[(3, 2), (8, 9), (7, 14), (12, 19), (11, 25)], [(8, 9), (14, 8), (20, 4)],
                [(12, 19), (18, 18), (24, 23)], [(7, 14), (3, 16)]]:
        d.line(pts, fill=cor("breu"))
    return img


def relogio():
    """Caxixi brunido 32x28 com uma faixa de azulejo atras (48x30)."""
    img = nova(48, 30)
    tile = azulejo_tile()
    for x in range(0, 48, 8):
        img.alpha_composite(tile, (x, 6))
        img.alpha_composite(tile, (x, 14))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 5, 47, 22], outline=cor("breu"))
    pote = caxixi(32, 28, "taua", "taua_vivo", "taua_esc", brilho="farinha")
    friso_espiral(pote, 4, 5, 28, "tabatinga", passo=6, meia=False)
    px = pote.load()
    for x in range(3, 29):
        if px[x, 25][3] and px[x, 25] != cor("breu") and x % 3 != 0:
            px[x, 25] = cor("tabatinga")
    dd = ImageDraw.Draw(pote)
    dd.rounded_rectangle([7, 11, 24, 23], radius=2, fill=cor("barro"))
    dd.line([8, 23, 23, 23], fill=cor("taua_esc"))
    img.alpha_composite(pote, (8, 0))
    return img


def bolinha(cozida):
    img = nova(6, 6)
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, 5, 5], fill=cor("breu"))
    px = img.load()
    if cozida:
        d.ellipse([1, 1, 4, 4], fill=cor("taua"))
        px[1, 2] = cor("taua_vivo")
        px[2, 1] = cor("farinha")
        px[4, 3] = cor("taua_esc")
        px[3, 4] = cor("taua_esc")
    else:
        d.ellipse([1, 1, 4, 4], fill=cor("tabatinga"))
        px[3, 4] = cor("madeira_cl")
        px[4, 3] = cor("madeira_cl")
        px[4, 2] = cor("madeira_cl")
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
SOL = (236, 104)  # o sol se pondo atras da ponte


def ceu():
    img = nova(320, 180)
    gradiente_v(img, 0, 0, 319, 179, [(0, "taua_esc"), (22, "taua"), (52, "taua_vivo"), (82, "ceu"),
                                      (102, "dende"), (118, "farinha"), (179, "farinha")])
    d = ImageDraw.Draw(img)
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


def casa(w, h, parede, sombra_parede, rnd):
    img = nova(w, h + 4)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 4, w - 1, h + 3], fill=cor(parede))
    d.rectangle([w - 2, 4, w - 1, h + 3], fill=cor(sombra_parede))
    # telhado de telha (tauá) com beiral
    d.polygon([(-1, 4), (2, 0), (w - 3, 0), (w, 4)], fill=cor("taua"))
    d.line([0, 4, w - 1, 4], fill=cor("taua_esc"))
    d.line([2, 0, w - 3, 0], fill=cor("taua_vivo"))
    for x in range(1, w - 1, 2):
        d.point((x, 2), fill=cor("taua_esc"))
    # janelas e porta
    nj = max(1, (w - 2) // 4)
    for j in range(nj):
        jx = 1 + j * 4 + (1 if w % 4 else 0)
        if jx + 1 >= w - 2:
            continue
        acesa = rnd.random() < 0.3
        for andar in range(max(1, (h - 3) // 5)):
            jy = 6 + andar * 5
            if jy + 2 >= h + 2:
                break
            d.rectangle([jx, jy, jx + 1, jy + 2], fill=cor("dende" if acesa and andar == 0 else "barro"))
            d.point((jx, jy - 1), fill=cor("tabatinga"))
    d.rectangle([w // 2 - 1, h, w // 2, h + 3], fill=cor("madeira"))
    return img


def cidade():
    """Morros, Cristo pequeno no Morro do Silencio, casario na ladeira, torre da Matriz e ponte de arcos."""
    img = nova(320, 180)
    d = ImageDraw.Draw(img)
    rnd = random.Random(7)
    # morro distante (silhueta de mangue com neblina)
    for x in range(320):
        y = int(100 + 4 * np.sin(x / 23.0) + 3 * np.sin(x / 9.0 + 1.3))
        d.line([x, y, x, HORIZONTE], fill=cor("mangue"))
    nevoa = np.zeros((180, 320), bool)
    nevoa[96:106, :] = True
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
    morro = np.zeros((180, 320), bool)
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
    # ladeira com casario: fileiras de casas descendo ate o rio
    def chao(x):
        return int(84 + (HORIZONTE - 4 - 84) * min(1.0, max(0.0, x / 168.0)) ** 1.15)
    paredes = [("tabatinga", "madeira_cl"), ("farinha", "dende"), ("ceu", "taua_vivo"), ("reflexo", "rio"),
               ("dende", "taua_vivo"), ("taua_vivo", "taua"), ("tabatinga", "madeira_cl"), ("farinha", "dende")]
    for fileira in range(3):
        x = -4 + fileira * 5
        while x < 176 - fileira * 6:
            w = rnd.choice([9, 10, 12, 13, 14])
            h = rnd.choice([9, 10, 12, 14]) + (4 if rnd.random() < 0.25 else 0)
            base = chao(x + w // 2) - fileira * 7 + 2
            p, s = paredes[rnd.randrange(len(paredes))]
            c = casa(w, h, p, s, rnd)
            img.alpha_composite(c, (x, base - c.height))
            x += w + rnd.choice([0, 1, 1, 2])
    d = ImageDraw.Draw(img)
    # Matriz: fachada clara com torre e sino
    mx, my = 30, 86
    d.rectangle([mx, my - 16, mx + 22, my], fill=cor("tabatinga"))
    d.polygon([(mx - 1, my - 16), (mx + 11, my - 24), (mx + 23, my - 16)], fill=cor("tabatinga"))
    d.line([(mx - 1, my - 16), (mx + 11, my - 24), (mx + 23, my - 16)], fill=cor("taua_vivo"))
    d.rectangle([mx + 21, my - 16, mx + 22, my], fill=cor("madeira_cl"))
    d.rectangle([mx + 8, my - 7, mx + 13, my], fill=cor("madeira"))
    d.ellipse([mx + 8, my - 9, mx + 13, my - 5], fill=cor("madeira"))
    d.ellipse([mx + 9, my - 17, mx + 12, my - 14], fill=cor("barro"))
    for jx in (mx + 3, mx + 17):
        d.rectangle([jx, my - 11, jx + 1, my - 8], fill=cor("barro"))
    tx = mx - 9
    d.rectangle([tx, my - 40, tx + 8, my], fill=cor("tabatinga"))
    d.rectangle([tx + 7, my - 40, tx + 8, my], fill=cor("madeira_cl"))
    d.rectangle([tx + 2, my - 34, tx + 6, my - 28], fill=cor("breu"))
    d.ellipse([tx + 3, my - 33, tx + 5, my - 30], fill=cor("dende"))
    d.polygon([(tx - 1, my - 40), (tx + 4, my - 48), (tx + 9, my - 40)], fill=cor("taua"))
    d.line([(tx + 4, my - 48), (tx + 9, my - 40)], fill=cor("taua_esc"))
    d.line([tx + 4, my - 53, tx + 4, my - 48], fill=cor("tabatinga"))
    d.line([tx + 2, my - 51, tx + 6, my - 51], fill=cor("tabatinga"))
    for y in (my - 25, my - 13):
        d.line([tx, y, tx + 8, y], fill=cor("madeira_cl"))
    # cais de pedra na beira
    d.rectangle([0, HORIZONTE - 3, 170, HORIZONTE], fill=cor("madeira_cl"))
    for x in range(0, 170, 5):
        d.line([x, HORIZONTE - 3, x, HORIZONTE], fill=cor("madeira"))
    d.line([0, HORIZONTE - 3, 170, HORIZONTE - 3], fill=cor("tabatinga"))
    # ponte de pedra em arcos (silhueta de barro contra o poente)
    p0, p1 = 140, 320
    topo = 98
    d.rectangle([p0, topo, p1, HORIZONTE], fill=cor("barro"))
    d.line([p0, topo, p1, topo], fill=cor("taua_esc"))
    d.line([p0, topo + 1, p1, topo + 1], fill=cor("taua_esc"))
    for x in range(p0, p1, 3):   # parapeito vazado
        d.rectangle([x, topo - 3, x + 1, topo - 1], fill=cor("barro"))
    d.line([p0, topo - 4, p1, topo - 4], fill=cor("barro"))
    a = arr(img)
    vao = 22
    for k in range(9):
        ax = p0 + 6 + k * vao
        caixa = nova(320, 180)
        ImageDraw.Draw(caixa).ellipse([ax, topo + 5, ax + 15, topo + 21], fill=(255, 255, 255, 255))
        ImageDraw.Draw(caixa).rectangle([ax, topo + 13, ax + 15, HORIZONTE], fill=(255, 255, 255, 255))
        m = opaco(caixa)
        borda = dilatar(m, diag=False) & ~m & (a[:, :, 3] > 0)
        a[m] = 0
        a[borda & (np.mgrid[0:180, 0:320][0] < topo + 13)] = cor("breu")
    img = de_arr(a)
    d = ImageDraw.Draw(img)
    for k in range(5):   # postes de luz na ponte
        lx = p0 + 18 + k * 40
        d.line([lx, topo - 10, lx, topo - 4], fill=cor("breu"))
        d.point((lx, topo - 11), fill=cor("dende"))
        d.point((lx - 1, topo - 10), fill=cor("farinha"))
    # mato na beira, embaixo da ladeira
    for x in range(168, 182):
        y = HORIZONTE - 2 - (x % 3)
        d.line([x, y, x, HORIZONTE], fill=cor("mangue"))
    return img


def rio():
    img = nova(320, 180)
    gradiente_v(img, 0, HORIZONTE, 319, 179, [(HORIZONTE, "reflexo"), (HORIZONTE + 8, "rio"), (150, "rio"),
                                               (179, "mangue")])
    d = ImageDraw.Draw(img)
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
    # luzes da cidade refletidas
    for x in (28, 44, 63, 90, 118, 150):
        for y in range(HORIZONTE + 2, HORIZONTE + 12, 3):
            d.line([x, y, x + 1, y], fill=cor("dende"))
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


def letra_logo(ch, cw=4, chh=5):
    bits = LOGO_LETRAS[ch]
    img = nova(len(bits[0]) * cw, len(bits) * chh)
    d = ImageDraw.Draw(img)
    for y, s in enumerate(bits):
        for x, c in enumerate(s):
            if c == "#":
                d.rectangle([x * cw, y * chh, x * cw + cw - 1, y * chh + chh - 1], fill=cor("taua"))
    # chanfro nos cantos de fora
    a = arr(img)
    m = a[:, :, 3] > 0
    for _ in range(1):
        quina = m & ((~deslocar(m, 0, 1) & ~deslocar(m, 1, 0)) | (~deslocar(m, 0, 1) & ~deslocar(m, -1, 0)) |
                     (~deslocar(m, 0, -1) & ~deslocar(m, 1, 0)) | (~deslocar(m, 0, -1) & ~deslocar(m, -1, 0)))
        a[quina] = 0
        m = a[:, :, 3] > 0
    return de_arr(a)


def logo(palavra="NAZAFIGHT", corpo="taua"):
    """Logo de barro brunido com friso de espiral de tabatinga. 240x56 (logico)."""
    letras = [letra_logo(c) for c in palavra]
    gap, P = 1, 3
    larg = sum(l.width for l in letras) + gap * (len(letras) - 1) + (4 if palavra == "NAZAFIGHT" else 0) + 2 * P
    corpo_img = nova(larg, 40 + 2 * P)
    x = P
    for i, l in enumerate(letras):
        corpo_img.alpha_composite(l, (x, P))
        x += l.width + gap + (4 if (palavra == "NAZAFIGHT" and i == 3) else 0)
    a = arr(corpo_img)
    m = a[:, :, 3] > 0
    a[m] = cor(corpo)
    topo = m & ~deslocar(m, 0, 1)
    esq = m & ~deslocar(m, 1, 0)
    baixo = m & ~deslocar(m, 0, -1)
    dirr = m & ~deslocar(m, -1, 0)
    a[baixo | dirr] = cor("taua_esc")
    a[topo | esq] = cor("taua_vivo")
    yy = np.mgrid[0:a.shape[0], 0:a.shape[1]][0]
    a[m & (yy >= 33 + P) & ~(topo | esq)] = cor("taua_esc")
    img = de_arr(a)
    # friso de espiral no meio das letras, so onde cabe inteiro
    interior = erodir(m, diag=True)
    px = img.load()
    fy = 17 + P
    for bx in range(0, larg - 4):
        ok = all(interior[fy + yy2, bx + xx2] for yy2 in range(5) for xx2 in range(5)
                 if ESPIRAL[yy2][xx2] == "#")
        livre = all(px[bx + xx2, fy + yy2] != cor("tabatinga") for yy2 in range(5) for xx2 in range(-1, 6)
                    if 0 <= bx + xx2 < larg)
        if ok and livre:
            for yy2, s in enumerate(ESPIRAL):
                for xx2, ch in enumerate(s):
                    if ch == "#":
                        px[bx + xx2, fy + yy2] = cor("tabatinga")
    # linha de tabatinga embaixo do friso (pintura de barro)
    for x in range(larg):
        if interior[fy + 8, x] and x % 2 == 0:
            px[x, fy + 8] = cor("tabatinga")
    # brilho do brunido
    for x in range(larg):
        if interior[P + 2, x] and x % 5 in (1, 2):
            px[x, P + 2] = cor("farinha")
    img = contorno(img, "barro", diag=True)
    img = contorno(img, "barro", diag=False)
    img = com_sombra(img, "breu", 2, 3)
    out = nova(240, 56)
    out.alpha_composite(img, ((240 - img.width) // 2, 4))
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
def pano_listrado(w, h, c1, c2, c3, larg=4, diagonal=False):
    img = nova(w, h)
    px = img.load()
    for y in range(h):
        for x in range(w):
            k = ((x + (y if diagonal else 0)) // larg) % 3
            px[x, y] = cor([c1, c2, c1, c3][((x + (y if diagonal else 0)) // larg) % 4] if k >= 0 else c1)
    return img


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


def fundo_selecao():
    img = nova(320, 180)
    d = ImageDraw.Draw(img)
    # chao da praca: pedra de cantaria
    d.rectangle([0, 0, 319, 179], fill=cor("madeira_cl"))
    for y in range(0, 180, 4):
        off = (y // 4) % 2 * 3
        for x in range(-off, 320, 6):
            d.line([x, y, x + 5, y], fill=cor("madeira"))
            d.point((x, y + 1), fill=cor("madeira"))
            d.point((x + 2, y + 2), fill=cor("tabatinga"))
    rnd = random.Random(21)
    listras = [("taua", "tabatinga"), ("rio", "tabatinga"), ("folha", "farinha"), ("dende", "taua_esc"),
               ("taua_vivo", "farinha")]
    for linha_y in (0, 96, 140):
        x = -6
        while x < 320:
            w = rnd.choice([22, 26, 30])
            img.alpha_composite(barraca(w, 18, listras[rnd.randrange(len(listras))], rnd), (x, linha_y + 1))
            x += w + 3
    # sacos de farinha e pilhas de caxixi soltos
    for _ in range(26):
        x, y = rnd.randrange(0, 316), rnd.randrange(22, 92)
        if rnd.random() < 0.5:
            d.ellipse([x, y, x + 5, y + 4], fill=cor("farinha"))
            d.line([x + 1, y, x + 4, y], fill=cor("tabatinga"))
            d.point((x + 2, y + 4), fill=cor("dende"))
        else:
            img.alpha_composite(caxixi(4, 5, rnd.choice(["taua", "taua_vivo", "taua_esc"]), "farinha", "barro"),
                                (x, y))
    # mesa grande de oleiro no meio: fileiras de caxixis, moringas e pratos de barro
    mesa = nova(78, 70)
    dm = ImageDraw.Draw(mesa)
    dm.rectangle([0, 0, 77, 69], fill=cor("madeira"))
    dm.rectangle([2, 2, 75, 67], fill=cor("madeira_cl"))
    for y in range(4, 66, 5):
        dm.line([3, y, 74, y], fill=cor("madeira"))
    dm.rectangle([0, 0, 77, 69], outline=cor("breu"))
    for fil in range(4):
        y = 4 + fil * 16
        x = 4
        while x < 70:
            tipo = rnd.random()
            if tipo < 0.8:
                w, h = rnd.choice([(7, 9), (8, 10), (9, 12), (10, 12), (6, 8)])
                c = rnd.choice([("taua", "taua_vivo", "taua_esc"), ("taua_esc", "taua", "barro"),
                                ("madeira_cl", "tabatinga", "madeira"), ("taua_vivo", "farinha", "taua")])
                p = caxixi(w, h, *c, friso=rnd.choice([None, "tabatinga", "farinha"]))
                mesa.alpha_composite(p, (x, y + 12 - h))
                x += w
            elif tipo < 0.93:
                pr = nova(9, 4)
                dp = ImageDraw.Draw(pr)
                dp.ellipse([0, 0, 8, 3], fill=cor("taua"))
                dp.line([2, 1, 6, 1], fill=cor("tabatinga"))
                mesa.alpha_composite(pr, (x, y + 8))
                x += 10
            else:
                x += 3
    img.alpha_composite(mesa, (121, 22))
    d = ImageDraw.Draw(img)
    # tabuleiro de madeira onde fica a grade
    gx, gy = POS["grade"][0] // 4, POS["grade"][1] // 4
    gw = (POS["colunas"] * (POS["celula"] + POS["celula_espaco"]) - POS["celula_espaco"]) // 4
    gh = (POS["linhas"] * (POS["celula"] + POS["celula_espaco"]) - POS["celula_espaco"]) // 4
    d.rectangle([gx - 4, gy - 4, gx + gw + 3, min(179, gy + gh + 3)], fill=cor("madeira"))
    d.rectangle([gx - 4, gy - 4, gx + gw + 3, 182], outline=cor("breu"))
    d.line([gx - 3, gy - 3, gx + gw + 2, gy - 3], fill=cor("madeira_cl"))
    # panos de feira atras dos retratos grandes
    for (x0, c) in [(POS["retrato_p1"][0] // 4, ("taua", "tabatinga", "taua_esc")),
                    (POS["retrato_p2"][0] // 4, ("rio", "tabatinga", "reflexo"))]:
        pano = pano_listrado(112, 96, *c, larg=4, diagonal=True)
        dp = ImageDraw.Draw(pano)
        dp.rectangle([0, 0, 111, 95], outline=cor("breu"))
        for x in range(0, 112, 2):
            dp.point((x, 95), fill=cor("breu"))
        img.alpha_composite(pano, (x0, 16))
        # varal: pau de madeira em cima do pano
        dd = ImageDraw.Draw(img)
        dd.rectangle([x0 - 2, 14, x0 + 113, 16], fill=cor("madeira"))
        dd.line([x0 - 2, 14, x0 + 113, 14], fill=cor("madeira_cl"))
        dd.rectangle([x0 - 2, 14, x0 + 113, 16], outline=cor("breu"))
    # tabuletas dos nomes, embaixo dos panos
    for cx in (POS["nome_sel_p1"][0] // 4, POS["nome_sel_p2"][0] // 4):
        t = tabuleta(84, 14, "", "tabatinga")
        img.alpha_composite(t, (cx - 42, 114))
    # faixa do titulo em cima
    faixa = nova(152, 13)
    df = ImageDraw.Draw(faixa)
    df.rectangle([0, 0, 151, 12], fill=cor("taua_esc"))
    df.line([0, 0, 151, 0], fill=cor("taua"))
    df.rectangle([0, 0, 151, 12], outline=cor("breu"))
    friso_espiral(faixa, 3, 4, 149, "taua", passo=6, meia=False)
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
    """Cantoneiras 36x36 por fora da celula; P1 dende, P2 rio; etiqueta 1P/2P."""
    c = "dende" if jogador == 1 else "rio"
    luz = "farinha" if jogador == 1 else "reflexo"
    img = nova(40, 40)
    d = ImageDraw.Draw(img)
    for (x, y, sx, sy) in [(0, 0, 1, 1), (39, 0, -1, 1), (0, 39, 1, -1), (39, 39, -1, -1)]:
        d.line([x, y, x + sx * 9, y], fill=cor(c), width=1)
        d.line([x, y + sy, x + sx * 9, y + sy], fill=cor(c))
        d.line([x, y, x, y + sy * 9], fill=cor(c))
        d.line([x + sx, y, x + sx, y + sy * 9], fill=cor(c))
        if aceso:
            d.point((x + sx, y + sy), fill=cor(luz))
    img = contorno(img, "breu", diag=False)
    eti = nova(13, 9)
    de = ImageDraw.Draw(eti)
    de.rectangle([0, 0, 12, 8], fill=cor(c))
    de.rectangle([0, 0, 12, 8], outline=cor("breu"))
    t = nova(11, 7)
    t1 = de_desenho(LETRAS[str(jogador)], {"#": "breu"})
    t2 = de_desenho(LETRAS["P"], {"#": "breu"})
    t.alpha_composite(t1, (0, 0))
    t.alpha_composite(t2, (6, 0))
    eti.alpha_composite(t, (1, 1))
    img.alpha_composite(eti, (2, 2) if jogador == 1 else (25, 29))
    return img


# ----------------------------------------------------------------------------------------------------------
# Tela de VS: pano de feira dividido, emblema de remos cruzados
# ----------------------------------------------------------------------------------------------------------
def fundo_vs():
    img = nova(320, 180)
    esq = pano_listrado(320, 180, "taua", "tabatinga", "taua_esc", larg=6, diagonal=True)
    dirr = pano_listrado(320, 180, "rio", "tabatinga", "reflexo", larg=6, diagonal=True)
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
    friso_espiral(img, 2, 172, 318, "taua", passo=6, meia=False)
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
    s += [(10, 0, t, ALCA, 0), (10, 1, espelhar(t), 0, 0)]
    for g, args in [(11, ("folha", "tabatinga", "mangue")), (12, ("dende", "farinha", "taua_vivo")),
                    (13, ("taua", "taua_vivo", "taua_esc"))]:
        e = enchimento_vida(*args)
        s += [(g, 0, e, 0, 0), (g, 1, espelhar(e), 0, 0)]
    f = fantasma_vida()
    s += [(14, 0, f, 0, 0), (14, 1, espelhar(f), 0, 0)]
    for k in range(7):
        c = composto_poder(k)
        s += [(20, k, c, 0, 4), (20, 10 + k, espelhar(c), 29, 4)]
    for g, args in [(21, ("rio", "reflexo", "farinha")), (22, ("dende", "farinha", "tabatinga"))]:
        e = enchimento_poder(*args)
        s += [(g, 0, e, 0, 0), (g, 1, espelhar(e), 0, 0)]
    fundo, anel, racha = moldura_face(False), moldura_face(True), rachaduras_face()
    s += [(30, 0, fundo, 0, 0), (30, 1, espelhar(fundo), 0, 0), (31, 0, anel, 0, 0), (31, 1, espelhar(anel), 0, 0),
          (32, 0, racha, 0, 0), (32, 1, espelhar(racha), 0, 0)]
    s.append((40, 0, relogio(), 24, 0))
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
        s.append((70, q, cacos(q), 8, 8))
    s.append((71, 0, nova(1, 1), 0, 0))
    return s


def sprites_system():
    s = []
    lg = logo()
    s.append((0, 0, lg, 120, 28))
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
footer.title.font = 3,0,1
footer.title.offset = 8,716
footer.title.scale = 0.5,0.5
footer.title.text = NAZAFIGHT - RECONCAVO BAIANO
footer.title.localcoord = {lc}
footer.info.font = 3,0,-1
footer.info.offset = 1272,716
footer.info.scale = 0.5,0.5
footer.info.text = F1: INFO
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
portrait.offset = 14,14
portrait.scale = 1,1
p1.cursor.startcell = 0,0
p1.cursor.active.anim = 310
p1.cursor.active.offset = -16,-16
p1.cursor.done.spr = 312,0
p1.cursor.done.offset = -16,-16
p2.cursor.startcell = 0,{POS['colunas'] - 1}
p2.cursor.active.anim = 311
p2.cursor.active.offset = -16,-16
p2.cursor.done.spr = 313,0
p2.cursor.done.offset = -16,-16
p2.cursor.blink = 0
p1.face.spr = 9000,1
p1.face.offset = {rp1[0] + 4},{rp1[1] + 2}
p1.face.facing = 1
p1.face.scale = 1,1
p1.face.window = {rp1[0]},{rp1[1]},{rp1[0] + 448},{rp1[1] + 384}
p2.face.spr = 9000,1
p2.face.offset = {rp2[0] + 436},{rp2[1] + 2}
p2.face.facing = -1
p2.face.scale = 1,1
p2.face.window = {rp2[0]},{rp2[1]},{rp2[0] + 448},{rp2[1] + 384}
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
    p1, p2 = POS["poder_p1"], POS["poder_p2"]
    f1, f2 = POS["face_p1"], POS["face_p2"]
    nm1, nm2 = POS["nome_p1"], POS["nome_p2"]
    w1, w2 = POS["vitoria_p1"], POS["vitoria_p2"]
    rx, ry = POS["relogio"]
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
font2 = fonts/naza_num_alerta.def
font3 = fonts/naza_tab.def
font4 = fonts/naza_menu.def
fightfx.sff = fightfx.sff     ; data/
fightfx.air = fightfx.air
common.snd = common.snd

[FightFx]
scale = 4

; Vida: prancha de saveiro com alca de moringa; esvazia para o centro. folha > 50%, dende 26-50%, taua <= 25%.
[Lifebar]
mid.delay = 30
"""
    for j, (pos, sufixo, faixa) in enumerate([(v1, 0, "495,16"), (v2, 1, "16,495")], start=1):
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
    for j, (pos, base, faixa) in enumerate([(p1, 0, "12,371"), (p2, 10, "371,12")], start=1):
        sufixo = j - 1
        t += f"p{j}.pos = {pos[0]},{pos[1]}\n"
        t += f"p{j}.bg0.spr = 20,{base}\n"
        for k in range(1, 7):
            t += f"p{j}.bg0{k * 500}.spr = 20,{base + k}\n"
        t += f"p{j}.front.spr = 21,{sufixo}\np{j}.front.offset = 12,4\n"
        t += f"p{j}.front3000.spr = 22,{sufixo}\np{j}.front3000.offset = 12,4\n"
        t += f"p{j}.range.x = {faixa}\np{j}.levelbars = 1\n"
    t += f"""
; Retrato: fundo de reserva (pano + silhueta) atras, 9000,0 do lutador, anel de barro por cima.
[Face]
p1.pos = {f1[0]},{f1[1]}
p1.bg.spr = 30,0
p1.face.spr = 9000,0
p1.face.offset = 6,6
p1.ko.spr = 32,0
p1.top.spr = 31,0
p2.pos = {f2[0]},{f2[1]}
p2.bg.spr = 30,1
p2.face.spr = 9000,0
p2.face.offset = 106,6
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

; Relogio: caxixi brunido com faixa de azulejo; numeros em taua vivo abaixo de 10 s (fonte 2).
[Time]
pos = {rx},{ry}
bg.spr = 40,0
counter.font = 2,0,0
counter.offset = 0,91
counter10.font = 1,0,0
counter10.offset = 0,91
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
    for j, (pos, dx) in enumerate([(w1, 32), (w2, -32)], start=1):
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


def previa_hud(fig_spr, fdefs, fontes, sys_spr, sdefs, sacoes):
    tela = Image.new("RGBA", (1280, 720), (20, 12, 16, 255))
    for gn in [(100, 0), (100, 2), (100, 3)]:      # so de fundo, para contraste (nao e um cenario)
        spr(tela, sys_spr, gn, 0, 0)
    lb, pb = secao(fdefs, "lifebar"), secao(fdefs, "powerbar")
    estado = {1: {"vida": 1.0, "fantasma": 1.0, "poder": 2500, "vitorias": 1, "char": "pengaro"},
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
    # o motor escreve o numero sem zero a esquerda (fmt "%v"): 8 s aparece como "8"
    escrever(tela, fontes[int(nums(ti[f"{chave}.font"])[0])], str(tempo), tx + ox, ty + oy, 0)
    return tela


# ----------------------------------------------------------------------------------------------------------
def gerar():
    (MOTIF / "fonts").mkdir(parents=True, exist_ok=True)
    PREVIAS.mkdir(parents=True, exist_ok=True)
    # fontes
    fontes_geradas = {
        "naza_num": fonte_numero("naza_num", "farinha", "tabatinga", "dende"),
        "naza_num_alerta": fonte_numero("naza_num_alerta", "taua_vivo", "farinha", "taua"),
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
    ff = {i: fonte_do(fdefs, i, MOTIF) for i in range(1, 5)}
    saidas = {
        "titulo.png": previa_titulo(sys_spr, sdefs, sacoes, sf),
        "selecao.png": previa_selecao(sys_spr, sdefs, sacoes, sf),
        "vs.png": previa_vs(sys_spr, sdefs, sacoes, sf),
        "hud.png": previa_hud(fig_spr, fdefs, ff, sys_spr, sdefs, sacoes),
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
