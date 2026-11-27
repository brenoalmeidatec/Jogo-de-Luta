#!/usr/bin/env python3
"""Golpes do CK feitos do desenho original (regra do Breno, 24/11: "o desenho original do golpe é a base"; as peças só
tapam lacuna e corrigem textura e rosto). O Breno viu o Bote (1400) e o uppercut agachado (410) montados só com as
peças e reclamou de cintura torcida, perna entortada e buraco nas costas. Aqui:

- Bote (1400) e Bote forte (1401): cada elemento é o quadro original da folha `caneta` que ele já usava ("de" do
  tempos.json), sem mudar nada.
- Uppercut agachado (410, pedido da #32: golpe agachado não levanta): os quadros agachados são os originais da folha
  `cabecada` (00, 01, 06, 07); no golpe, o tronco do uppercut original (cabecada/04 e 05: braço no alto) é assentado
  na cintura do agachado original (cabecada/07), pela barra da camisa. Nada é girado, esticado nem engrossado.

    python3 ferramentas/ck_do_original.py            (os três)
    python3 ferramentas/ck_do_original.py uppercut

Os tempos (tempos.json) ficam os de antes: depois rode `trocar_desenhos.py ck <golpes>`, `aura_no_corpo.py ck` e
`encolher_sff.py ck`.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
ORIG = RAIZ / "sprites/ck/quadros_arcade_hd"
HD, UM = RAIZ / "sprites/ck/quadros_pecas_hd", RAIZ / "sprites/ck/quadros_pecas"

# barra da camisa (y na tela 1080x780) de cada quadro original usado na montagem
BARRA = {"cabecada/04": 460, "cabecada/05": 462, "cabecada/07": 525}
PERNAS = "cabecada/07"


def abrir(nome):
    return np.array(Image.open(ORIG / f"{nome}.png").convert("RGBA"))


def meio(a, y):
    xs = np.nonzero(a[y, :, 3] > 0)[0]
    return (xs.min() + xs.max()) / 2


def assentar(tronco, pernas=PERNAS):
    """O tronco do quadro `tronco` (acima da barra da camisa) na cintura do quadro `pernas` (da barra para baixo)."""
    a, p = abrir(tronco), abrir(pernas)
    ya, yp = BARRA[tronco], BARRA[pernas]
    dy = yp - ya
    dx = int(round(meio(p, yp + 4) - meio(a, ya - 4)))
    out = np.zeros_like(p)
    out[yp:] = p[yp:]
    cima = a[:ya + 3]  # com o contorno da barra
    h, w = out.shape[:2]
    for y in range(cima.shape[0]):
        yy = y + dy
        if not 0 <= yy < h:
            continue
        linha = cima[y]
        xs = np.nonzero(linha[:, 3] > 0)[0]
        for x in xs:
            if 0 <= x + dx < w:
                out[yy, x + dx] = linha[x]
    return out


UPPERCUT = {"uppercut_baixo/00": "cabecada/00", "uppercut_baixo/01": "cabecada/01", "uppercut_baixo/02": "cabecada/07",
            "uppercut_baixo/03": ("cabecada/04",), "uppercut_baixo/04": ("cabecada/04",),
            "uppercut_baixo/05": ("cabecada/05",), "uppercut_baixo/06": "cabecada/07",
            "uppercut_baixo/07": "cabecada/07"}


def desenho(de, golpe):
    if golpe == "uppercut":
        f = UPPERCUT[de]
        return assentar(f[0]) if isinstance(f, tuple) else abrir(f)
    return abrir(de)


def fazer(golpe):
    arq = HD / golpe / "tempos.json"
    t = json.loads(arq.read_text(encoding="utf-8"))
    feitos = {}
    for e in t["elementos"]:
        if e["de"] not in feitos:
            feitos[e["de"]] = desenho(e["de"], golpe)
        img = feitos[e["de"]]
        Image.fromarray(img).save(HD / golpe / f"{e['desenho']:02d}.png")
        Image.fromarray(np.ascontiguousarray(img[1::3, 1::3])).save(UM / golpe / f"{e['desenho']:02d}.png")
    print(f"{golpe}: {len(t['elementos'])} elementos de {len(feitos)} desenhos originais")


if __name__ == "__main__":
    for g in sys.argv[1:] or ["bote", "bote_forte", "uppercut"]:
        fazer(g)
