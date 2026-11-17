"""Hazak, retoque de pixel da faixa e da atadura. Chamado por ferramentas/folhas_hazak_arcade.py depois do retoque da
pulseira; pode rodar de novo à vontade (o que já foi trocado não casa mais com a regra).

 1. FAIXA: nos desenhos de FAIXA_MARROM a quantização pintou as pontas soltas da faixa com o contorno e a sombra da
    pele (marrom avermelhado), e a faixa "mudava de cor" no meio do golpe. Toda mancha dessas duas cores que não
    encosta em pele (médio, luz, brilho) nem no debrum laranja (a sombra do debrum usa o mesmo marrom) é faixa: vira a
    cor da faixa (quase preta).
 2. ATADURA: desenhos em que o pulso da pulseira saiu só com a tira verde-água, sem a atadura branca que ele tem na
    ginga. Pinta de branco os pixels de pele colados na tira, do lado da mão.
"""
import cv2
import numpy as np
from PIL import Image

CONTORNO_PELE, SOMBRA_PELE = (122, 46, 38), (176, 79, 48)
PELE = ((222, 132, 72), (246, 180, 104), (252, 217, 160))
FAIXA = (58, 42, 48)
DEBRUM = (216, 102, 28)
VERDE, BRANCO = (0x2a, 0x9d, 0x9a), (0xf4, 0xf1, 0xea)
FAIXA_MARROM = {"chute_alto_rajada": range(7)}
# pontas que se misturam com o laranja do debrum (a regra 1 não separa): retângulo (x1, y1, x2, y2) da tela 360x260
# onde só há ponta de faixa; ali contorno e sombra de pele e o laranja viram faixa
PONTAS = {("chute_alto_rajada", 1): (150, 157, 173, 184), ("chute_alto_rajada", 5): (150, 157, 173, 184)}
LARANJAS = ((216, 102, 28), (142, 58, 26))
# (folha, desenho): (dx da mão em relação à tira, quantos px de atadura)
ATADURA = {("soco_reto", 4): (1, 4), ("soco_reto", 5): (1, 4)}


def cor(a, *rgbs):
    m = np.zeros(a.shape[:2], bool)
    for rgb in rgbs:
        m |= (a[..., :3] == rgb).all(-1) & (a[..., 3] > 0)
    return m


def faixa(a):
    """Devolve a máscara do que é faixa pintada de marrom."""
    marrom = cor(a, CONTORNO_PELE, SOMBRA_PELE).astype(np.uint8)
    perto_da_pele = cv2.dilate(cor(a, *PELE, DEBRUM).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    n, rot = cv2.connectedComponents(marrom, connectivity=8)
    saida = np.zeros(marrom.shape, bool)
    for k in range(1, n):
        m = rot == k
        if not (m & perto_da_pele).any():
            saida |= m
    return saida


def retocar(nome, i, img):
    a = np.array(img.convert("RGBA"))
    trocados = 0
    if i in FAIXA_MARROM.get(nome, ()):
        m = faixa(a)
        a[m, :3] = FAIXA
        trocados += int(m.sum())
    if (nome, i) in PONTAS:
        x1, y1, x2, y2 = PONTAS[nome, i]
        m = np.zeros(a.shape[:2], bool)
        m[y1:y2, x1:x2] = cor(a, CONTORNO_PELE, SOMBRA_PELE, *LARANJAS)[y1:y2, x1:x2]
        a[m, :3] = FAIXA
        trocados += int(m.sum())
    if (nome, i) in ATADURA:
        dx, n = ATADURA[nome, i]
        ys, xs = np.nonzero(cor(a, VERDE))
        pele = cor(a, *PELE, SOMBRA_PELE)
        for y in set(ys.tolist()):
            ponta = xs[ys == y].max() if dx > 0 else xs[ys == y].min()
            for k in range(1, n + 1):
                x = ponta + dx * k
                if 0 <= x < a.shape[1] and pele[y, x]:
                    a[y, x, :3] = BRANCO
                    trocados += 1
    return Image.fromarray(a), trocados


def aplicar(nome, pasta):
    """Retoca os desenhos da pasta. Devolve quantos pixels mudaram."""
    total = 0
    for i, f in enumerate(sorted(pasta.glob("[0-9][0-9].png"))):
        img, n = retocar(nome, i, Image.open(f))
        if n:
            img.save(f)
            total += n
    return total
