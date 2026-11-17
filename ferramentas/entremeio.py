#!/usr/bin/env python3
"""Cria quadros do meio entre os desenhos de uma animação (fluxo óptico), em loop ou não.

  python ferramentas/entremeio.py ginga ginga_fluida --entre 3 --loop

Lê sprites/pengaro/quadros/<origem>/NN.png e escreve sprites/pengaro/quadros/<destino>/NN.png com
(n - 1) * (entre + 1) + 1 quadros (n * (entre + 1) com --loop). Cada quadro do meio vem de um só
desenho deformado, o mais próximo, para não aparecer corpo duplo (a paleta do jogo é cheia ou vazia).
Precisa de: pip install numpy opencv-python-headless
"""
import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "sprites/pengaro/quadros"


def cinza(a):
    g = cv2.cvtColor(a[..., :3], cv2.COLOR_RGB2GRAY)
    g[a[..., 3] < 128] = 0
    return g


def fluxo(a, b):
    return cv2.calcOpticalFlowFarneback(cinza(a), cinza(b), None, 0.5, 5, 25, 10, 7, 1.5, 0)


def deforma(a, mx, my):
    return cv2.remap(a, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_NEAREST,
                     borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))


def meio(a, b, t, gx, gy):
    """Quadro entre a (t=0) e b (t=1)."""
    if t < 0.5:
        f = fluxo(b, a)
        return deforma(a, gx + t * f[..., 0], gy + t * f[..., 1])
    f = fluxo(a, b)
    return deforma(b, gx + (1 - t) * f[..., 0], gy + (1 - t) * f[..., 1])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("origem")
    p.add_argument("destino")
    p.add_argument("--entre", type=int, default=3, help="quadros novos entre cada par")
    p.add_argument("--loop", action="store_true", help="o último desenho também vai até o primeiro")
    a = p.parse_args()

    arquivos = sorted((BASE / a.origem).glob("[0-9][0-9].png"))
    q = [np.array(Image.open(f).convert("RGBA")) for f in arquivos]
    h, w = q[0].shape[:2]
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    saida = BASE / a.destino
    saida.mkdir(parents=True, exist_ok=True)
    for f in saida.glob("*.png"):
        f.unlink()
    n = len(q)
    pares = n if a.loop else n - 1
    lista = []
    for i in range(pares):
        A, B = q[i], q[(i + 1) % n]
        lista.append(A)
        for k in range(1, a.entre + 1):
            lista.append(meio(A, B, k / (a.entre + 1), gx, gy))
    if not a.loop:
        lista.append(q[-1])
    for i, im in enumerate(lista):
        im[..., 3] = np.where(im[..., 3] >= 128, 255, 0)
        Image.fromarray(im).save(saida / f"{i:02d}.png")
    print(f"{a.destino}: {len(lista)} quadros")


if __name__ == "__main__":
    main()
