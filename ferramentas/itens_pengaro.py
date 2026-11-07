"""Itens do Pengaró desenhados em pixel art (estilo sprite de SNES, contorno escuro de 1 px, 3 a 4 tons por cor):
garrafa de whisky na mão de trás e lata de cerveja (projétil). Sem marca real: rótulo liso.

Tudo é desenhado pixel a pixel por código, sem girar nem reduzir imagem, para não sair borrado.
"""
from PIL import Image

TINTA = (28, 16, 20, 255)

# paleta da garrafa: vidro âmbar (escuro, médio, claro, brilho), tampa, rótulo
VIDRO = [(92, 38, 10, 255), (150, 70, 18, 255), (204, 112, 30, 255), (250, 200, 120, 255)]
TAMPA = [(30, 26, 30, 255), (70, 62, 66, 255)]
ROTULO = [(214, 196, 150, 255), (240, 228, 190, 255), (150, 40, 32, 255)]

# lata: alumínio (escuro, médio, claro, brilho) e faixa vermelha e amarela genérica
ALUMINIO = [(96, 100, 112, 255), (150, 156, 168, 255), (200, 206, 216, 255), (244, 246, 250, 255)]
FAIXA = [(150, 30, 28, 255), (206, 52, 40, 255), (236, 196, 60, 255)]


def _desenho(linhas, cores):
    """linhas: strings do mesmo tamanho; cada caractere é uma chave de `cores` ('.' = vazio)."""
    img = Image.new("RGBA", (len(linhas[0]), len(linhas)))
    px = img.load()
    for y, linha in enumerate(linhas):
        for x, c in enumerate(linha):
            if c != ".":
                px[x, y] = cores[c]
    return img


# Garrafa segurada pelo gargalo (o gargalo fica dentro do punho, o corpo pendurado para baixo). 9 x 22 px.
GARRAFA = [
    "...###...",
    "...#tT#..",
    "...#tT#..",
    "...#mc#..",
    "...#mc#..",
    "...#mc#..",
    "..#mmcb#.",
    ".#mmccbb#",
    ".#dmmcbs#",
    ".#dmmcbs#",
    ".#rRRRRr#",
    ".#rRxxRr#",
    ".#rRRRRr#",
    ".#rRRRRr#",
    ".#dmmcbb#",
    ".#dmmccb#",
    ".#dmmccb#",
    ".#ddmmcb#",
    ".#ddmmcb#",
    ".#ddmmmc#",
    "..#dddd#.",
    "...####..",
]
CORES_GARRAFA = {"#": TINTA, "d": VIDRO[0], "m": VIDRO[1], "c": VIDRO[2], "b": VIDRO[2], "s": VIDRO[3],
                 "t": TAMPA[0], "T": TAMPA[1], "r": ROTULO[0], "R": ROTULO[1], "x": ROTULO[2]}

# Lata de cerveja de pé. 10 x 15 px.
LATA = [
    "..######..",
    ".#bbccbb#.",
    "#ddmmccss#",
    "#dmmmccbs#",
    "#fFFFFFFf#",
    "#fFyyyyFf#",
    "#fFyyyyFf#",
    "#fFFFFFFf#",
    "#dmmmccbs#",
    "#dmmmccbs#",
    "#dmmmccbs#",
    "#dmmmccbs#",
    "#ddmmccbs#",
    ".#dddmmm#.",
    "..######..",
]
CORES_LATA = {"#": TINTA, "d": ALUMINIO[0], "m": ALUMINIO[1], "c": ALUMINIO[2], "b": ALUMINIO[2], "s": ALUMINIO[3],
              "f": FAIXA[0], "F": FAIXA[1], "y": FAIXA[2]}


def garrafa():
    return _desenho(GARRAFA, CORES_GARRAFA)


def lata():
    return _desenho(LATA, CORES_LATA)


def latas_girando(escala=1):
    """4 quadros da lata girando no ar (0°, 90°, 180°, 270°: só giro de 90°, que não borra)."""
    base = lata()
    quadros = [base, base.transpose(Image.ROTATE_270), base.transpose(Image.ROTATE_180), base.transpose(Image.ROTATE_90)]
    if escala != 1:
        quadros = [q.resize((q.width * escala, q.height * escala), Image.NEAREST) for q in quadros]
    return quadros


def _pele(r, g, b):
    return r > 110 and r > g + 25 and g > b and r - b > 55


def mao_de_tras(img):
    """Punho de trás de um lutador virado para a direita: o pixel de pele mais à esquerda entre 15% e 70% da altura.
    Devolve (x, y) ou None."""
    alfa = img.getchannel("A")
    caixa = alfa.getbbox()
    if not caixa:
        return None
    x0, y0, x1, y1 = caixa
    alt = y1 - y0
    px = img.load()
    melhor = None
    for y in range(y0 + int(alt * .15), y0 + int(alt * .70)):
        for x in range(x0, (x0 + x1) // 2):
            r, g, b, a = px[x, y]
            if a >= 128 and _pele(r, g, b):
                if melhor is None or x < melhor[0]:
                    melhor = (x, y)
                break
    if melhor is None:
        return None
    # centro do punho: média da pele num raio de 5 px em volta da ponta
    mx, my = melhor
    sx = sy = n = 0
    for y in range(my - 5, my + 6):
        for x in range(mx, mx + 7):
            if 0 <= x < img.width and 0 <= y < img.height:
                r, g, b, a = px[x, y]
                if a >= 128 and _pele(r, g, b):
                    sx, sy, n = sx + x, sy + y, n + 1
    return (round(sx / n), round(sy / n)) if n else melhor


def com_whisky(img):
    """Põe a garrafa na mão de trás, por trás do corpo (o corpo cobre o que ficar atrás dele)."""
    mao = mao_de_tras(img)
    if mao is None:
        return img
    g = garrafa()
    tela = Image.new("RGBA", img.size)
    # o gargalo (colunas 3 a 6, linhas 0 a 5) fica dentro do punho
    tela.alpha_composite(g, (mao[0] - 4, mao[1] - 3))
    tela.alpha_composite(img)
    return tela
