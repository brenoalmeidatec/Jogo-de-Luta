"""Lote 7 (2026-11-11): e_queda. A 2ª geração (a que estava no repo) tinha a cor certa e a figura ~13% menor, com as
pernas levantadas nos desenhos 4 a 7; a 3ª tem a escala e as poses da queda normal, mas a pele veio marrom-alaranjada
e o casaco esverdeado. Este retoque leva a COR da 2ª para a 3ª (média e desvio de cada canal em Lab, só nos pixels da
figura) e grava a folha de volta com o fundo magenta.

  python ferramentas/retoques_arcade/lote7_queda.py <3ª geração.png> <2ª geração.png> <saída.png>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import cv2  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from recortar_quadros import tira_fundo  # noqa: E402


def figura(arq):
    a = np.array(tira_fundo(Image.open(arq)))
    lab = cv2.cvtColor(a[..., :3], cv2.COLOR_RGB2LAB).astype(np.float32)
    return a, lab, a[..., 3] > 0


def main():
    a, lab, m = figura(sys.argv[1])
    _, ref, mr = figura(sys.argv[2])
    for c in range(3):
        x, r = lab[..., c][m], ref[..., c][mr]
        lab[..., c][m] = (x - x.mean()) / (x.std() + 1e-6) * r.std() + r.mean()
    rgb = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)
    saida = np.array(Image.open(sys.argv[1]).convert("RGB"))
    saida[~m] = (255, 0, 255)
    saida[m] = rgb[m]
    Image.fromarray(saida).save(sys.argv[3])
    print("gravado", sys.argv[3])


main()
