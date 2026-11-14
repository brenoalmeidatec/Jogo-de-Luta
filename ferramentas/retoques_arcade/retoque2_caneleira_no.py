"""Retoque de 2026-11-11 (2ª passada), registro do que foi pintado à mão nos PNGs de quadros_arcade do Pengaró.
Rodar DUAS vezes estraga (o retoque parte do desenho como estava no commit 4fc03ed). Uso, da raiz do repositório:
    python ferramentas/retoques_arcade/retoque2_caneleira_no.py

1. queda/07 (deitado, ações 5110, 5150, 5160, 5170): a perna visível não tinha caneleira; ela sumia quando ele
   encostava no chão e voltava na levantada. Pinta a caneleira oliva na canela (x 207..227), como no desenho 06.
2. levanta/04: nó amarelo do cinto solto atrás do ombro, a 25 px do cinto. Apagado; o ombro fecha com contorno.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "sprites/pengaro/quadros_arcade"
PAL = {c["id"]: tuple(c["rgb"]) for c in json.loads((RAIZ / "sprites/pengaro/paleta_arcade.json").read_text("utf-8"))["cores"]}


def eh(a, *nomes):
    m = np.zeros(a.shape[:2], bool)
    for n in nomes:
        m |= (a[..., :3] == np.array(PAL[n], np.uint8)).all(-1)
    return m & (a[..., 3] > 0)


def queda_07():
    arq = PASTA / "queda/07.png"
    a = np.array(Image.open(arq).convert("RGBA"))
    x0, x1 = 207, 227
    faixa = np.zeros(a.shape[:2], bool)
    faixa[192:214, x0:x1 + 1] = True
    perna = faixa & eh(a, "calca_branco", "pele_brilho", "calca_sombra", "faixa_verde", "faixa_amarelo", "pele_luz",
                       "pele_medio", "cabelo_luz", "cabelo_escuro", "faixa_escuro", "garrafa_ambar", "garrafa_escuro",
                       "pele_sombra")
    claro = perna & eh(a, "calca_branco", "pele_brilho")
    a[perna, :3] = PAL["cabelo_escuro"]
    a[claro, :3] = PAL["cabelo_luz"]
    xs = np.arange(a.shape[1])[None, :].repeat(a.shape[0], 0)
    a[perna & ((xs <= x0 + 1) | (xs >= x1 - 1)), :3] = PAL["cabelo_escuro"]  # bordas da caneleira
    a[claro & (xs >= 216) & (xs <= 217), :3] = PAL["faixa_escuro"]  # tira do meio
    Image.fromarray(a).save(arq)
    print("queda/07:", int(perna.sum()), "px")


def levanta_04():
    arq = PASTA / "levanta/04.png"
    a = np.array(Image.open(arq).convert("RGBA"))
    a[143:147, 142:157] = 0  # o nó e as pontas acima do ombro
    a[147, 142:155] = 0
    a[147, 143:155, :3] = PAL["pele_contorno"]
    a[147, 143:155, 3] = 255
    trecho = np.zeros(a.shape[:2], bool)
    trecho[148:153, 142:156] = True
    for de, para in (("faixa_amarelo", "pele_medio"), ("garrafa_ambar", "pele_sombra"), ("calca_sombra", "pele_medio"),
                     ("calca_contorno", "pele_sombra")):
        a[trecho & eh(a, de), :3] = PAL[para]
    a[148, 151, :3] = PAL["pele_sombra"]  # pedaço de contorno que separava o nó do ombro
    Image.fromarray(a).save(arq)
    print("levanta/04 ok")


if __name__ == "__main__":
    queda_07()
    levanta_04()
