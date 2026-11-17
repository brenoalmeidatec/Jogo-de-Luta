"""Quadros do Diabo demônio (pastas m_* do diabo_terno, branch vpkpcf) na tela 3x do firme.py (1080x780, pés em
540,660), para o kit de peças: sprites/diabo_demonio/quadros_arcade_hd/<folha>/NN.png.

    python ferramentas/diabo_tela.py PASTA_DIABO_TERNO
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "sprites/diabo_demonio/quadros_arcade_hd"
TELA, PE = (1080, 780), (540, 660)


def ancora(m):  # o mesmo do diabo_terno.ancora_demonio: x = mediana do tronco, y = base
    h = m.shape[0]
    xs = np.nonzero(m[int(h * 0.25):max(int(h * 0.25) + 1, int(h * 0.6))])[1]
    if not len(xs):
        xs = np.nonzero(m)[1]
    return float(np.median(xs)), h - 1


def main(origem):
    for pasta in sorted(Path(origem).glob("m_*")):
        destino = SAIDA / pasta.name[2:]
        destino.mkdir(parents=True, exist_ok=True)
        for f in sorted(pasta.glob("[0-9][0-9].png")):
            img = Image.open(f).convert("RGBA")
            ax, ay = ancora(np.array(img)[..., 3] > 0)
            tela = Image.new("RGBA", TELA, (0, 0, 0, 0))
            tela.alpha_composite(img, (int(round(PE[0] - ax)), int(PE[1] - ay)))
            tela.save(destino / f.name)
    print("ok", len(list(SAIDA.glob("*/*.png"))))


if __name__ == "__main__":
    main(sys.argv[1])
