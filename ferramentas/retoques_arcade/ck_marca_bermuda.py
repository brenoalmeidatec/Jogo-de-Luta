"""Apaga a marquinha em forma de olho com redemoinho (cara de logo) da barra do bermudão do CK boss.

A marca veio do próprio conceito (e_conceito.png, vista de frente e vista com aura) e passou para as folhas b_.
Para cada ponto da lista: usa o centro achado por casamento de recorte (e conferido no zoom),
pega só os pedaços claros pequenos com o centro perto do ponto (as listras compridas da camuflagem ficam)
e pinta por cima com cv2.inpaint, que puxa o roxo em volta. Roda uma vez sobre a folha bruta:

    python ferramentas/retoques_arcade/ck_marca_bermuda.py            (todas as folhas da lista, no lugar)
    python ferramentas/retoques_arcade/ck_marca_bermuda.py b_soco      (só uma)
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

PASTA = Path(__file__).resolve().parents[2] / "sprites/ck/quadros/folhas_arcade"

# folha -> centros aproximados (x, y) da marca, um por quadro em que ela aparece (achados por casamento e olhados no zoom).
# (x, y, rx, ry): a marca encosta na listra da barra; apaga todo claro dentro da elipse de raios rx, ry.
PONTOS = {
    "e_conceito": [(270, 492), (1260, 492)],
    "b_ginga": [(202, 478), (465, 481), (734, 488), (999, 497), (1264, 487), (1531, 483), (1802, 480), (2078, 480)],
    "b_anda": [(501, 494), (751, 476), (1562, 462)],  # nos outros quadros a perna da marca está de costas
    "b_soco": [(204, 471, 13, 8), (458, 470, 15, 8), (716, 460), (1015, 462), (1261, 452), (1532, 457), (1826, 462), (2095, 472, 15, 8)],
}
# pedaço claro da marca: centro a até RAIO px do ponto e caixa de no máximo LARG_MAX x ALT_MAX (as listras da
# camuflagem em volta são mais compridas que isso e ficam)
RAIO, LARG_MAX, ALT_MAX = 16, 50, 32


def claro(a):
    r, g, b = (a[..., i].astype(int) for i in range(3))
    magenta = (r > 170) & (g < 100) & (b > 170)
    return ((r + g + b) / 3 > 150) & ~magenta


def apagar(nome):
    arq = PASTA / f"{nome}.png"
    a = np.array(Image.open(arq).convert("RGB"))
    luz = claro(a)
    mascara = np.zeros(luz.shape, np.uint8)
    for ponto in PONTOS[nome]:
        cx, cy = ponto[:2]
        if len(ponto) == 4:
            el = np.zeros(luz.shape, np.uint8)
            cv2.ellipse(el, (cx, cy), ponto[2:], 0, 0, 360, 1, -1)
            mascara |= el & luz
            print(f"{nome} ({cx},{cy}): {int((el & luz).sum())} px claros apagados (elipse)")
            continue
        x0, y0 = cx - 60, cy - 60
        n, rot, st, cen = cv2.connectedComponentsWithStats(luz[y0:cy + 60, x0:cx + 60].astype(np.uint8), connectivity=8)
        tot = 0
        for i in range(1, n):
            w, h, ar = st[i, 2], st[i, 3], st[i, 4]
            perto = np.hypot(cen[i][0] + x0 - cx, cen[i][1] + y0 - cy) <= RAIO
            if perto and w <= LARG_MAX and h <= ALT_MAX and ar >= 3:
                mascara[y0:cy + 60, x0:cx + 60][rot == i] = 1
                tot += ar
        print(f"{nome} ({cx},{cy}): {tot} px claros apagados")
    mascara = cv2.dilate(mascara, np.ones((3, 3), np.uint8))
    novo = cv2.inpaint(a[..., ::-1].copy(), mascara, 4, cv2.INPAINT_TELEA)[..., ::-1]
    Image.fromarray(novo).save(arq)


if __name__ == "__main__":
    for nome in sys.argv[1:] or PONTOS:
        apagar(nome)
