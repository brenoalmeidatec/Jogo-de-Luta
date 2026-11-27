#!/usr/bin/env python3
"""Gbzin: converte sprites/gbzin/quadros/folhas_arcade/ para a arte arcade do jogo, com o mesmo código do CK.

  python ferramentas/converter_gbzin.py                 todas as folhas (corpo e efeitos)
  python ferramentas/converter_gbzin.py soco e_soco     só essas
  python ferramentas/converter_gbzin.py --contato DIR   folhas de contato do resultado
  python ferramentas/converter_gbzin.py --medir         altura e largura de cada quadro convertido
  HD=3 python ferramentas/converter_gbzin.py            o gêmeo 3x em quadros_arcade_hd/

Tudo o que vale para o converter_ck.py vale aqui (corte por célula, fundo magenta com degradê, 15 cores + transparente,
pés em 180,220). O que muda: paleta_arcade.json (base) e paleta_arcade_motoboy.json (e_* e despertar_b), os retoques de
retoques_arcade/gbzin.py e a lista de efeitos abaixo. As paletas saem de quantizar_folha.py --montar-paleta (PAPEIS_GBZIN).
"""
import os
import sys
from pathlib import Path

os.environ["LUTADOR"] = "gbzin"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import converter_ck as cv  # noqa: E402

# Deitado o corpo não cabe na célula e vem menor: escala por quadro, medida com --medir quando a arte final chegar.
cv.ESCALA_QUADRO = {}
# Efeitos fx_* (fundo verde, menos pizza e mochila, que vêm no magenta): (escala sobre o corpo, largura final, de chão)
cv.EFEITOS = {"cabra": (1.0, None, True), "cabra_salto": (1.0, None, False), "onda_cajado": (1.0, None, True),
              "feno": (1.0, None, False), "pizza": (1.0, None, False), "mochila": (1.0, None, False),
              "notas": (1.0, None, True), "buzina": (1.0, None, False), "giroflex": (1.0, None, False),
              "moto": (1.0, None, True)}
cv.FUMACA_DO_DESPERTAR = {}
FUNDO_MAGENTA = {"pizza", "mochila"}

_recortar = cv.recortar_efeito


def recortar_efeito(nome):
    """O converter_ck só conhece a garrafa no magenta; aqui pizza e mochila também."""
    if nome in FUNDO_MAGENTA:
        return _recortar_magenta(nome)
    return _recortar(nome)


def _recortar_magenta(nome):
    import numpy as np
    import cv2
    from PIL import Image
    a = np.array(Image.open(cv.ENTRADA / f"fx_{nome}.png").convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    fundo = (r > 170) & (b > 170) & (g < 130)
    rgba = np.dstack([r, g, b, np.where(fundo, 0, 255)]).astype(np.uint8)
    n, rot, info, centros = cv2.connectedComponentsWithStats((~fundo).astype(np.uint8), connectivity=8)
    largura = rgba.shape[1] / 8
    celula = np.full(n, -1)
    for i in range(1, n):
        if info[i, cv2.CC_STAT_AREA] >= 12:
            celula[i] = min(7, int(centros[i][0] // largura))
    return [np.where((celula[rot] == i)[..., None], rgba, 0).astype(np.uint8) for i in range(8)], largura


cv.recortar_efeito = recortar_efeito

if __name__ == "__main__":
    cv.main()
