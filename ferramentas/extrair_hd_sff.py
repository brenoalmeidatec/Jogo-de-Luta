#!/usr/bin/env python3
"""Tira do .sff os sprites que o jogo mostra hoje, em 3x (o .sff do Gutto e do Raiclaven sai do Blender, fora do git),
numa tela 1080x780 com o eixo do jogo em (540, 660), igual a quadros_arcade_hd do Pengaró.

  python ferramentas/extrair_hd_sff.py gutto [GRUPOS...]     grava sprites/gutto/quadros_sff_hd/<grupo>_<indice>.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conferir_sff as c  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
TELA = (1080, 780)
EIXO = (540, 660)


def paleta(pal):
    p = np.frombuffer(pal, np.uint8)
    p = p[:len(p) // 4 * 4].reshape(-1, 4) if len(pal) == 1024 else p[:len(p) // 3 * 3].reshape(-1, 3)
    rgba = np.zeros((256, 4), np.uint8)
    rgba[:len(p), :3] = p[:256, :3]
    rgba[:, 3] = 255
    rgba[0, 3] = 0
    return rgba


def sprites(lutador):
    pal, nos, _ = c.ler(RAIZ / "chars" / lutador / f"{lutador}.sff")
    cores = paleta(pal)
    return cores, {(n["g"], n["i"]): n for n in nos}


def tela(cores, n):
    if n.get("png"):
        return None
    a = np.frombuffer(n["px"], np.uint8).reshape(n["h"], n["w"])
    img = cores[a]
    out = np.zeros((TELA[1], TELA[0], 4), np.uint8)
    x0, y0 = EIXO[0] - n["x"], EIXO[1] - n["y"]
    h, w = img.shape[:2]
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(TELA[0], x0 + w), min(TELA[1], y0 + h)
    out[Y0:Y1, X0:X1] = img[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    return out


def main():
    lut = sys.argv[1]
    grupos = {int(g) for g in sys.argv[2:]}
    cores, sp = sprites(lut)
    dest = RAIZ / "sprites" / lut / "quadros_sff_hd"
    dest.mkdir(parents=True, exist_ok=True)
    k = 0
    for (g, i), n in sp.items():
        if grupos and g not in grupos:
            continue
        t = tela(cores, n)
        if t is not None:
            Image.fromarray(t).save(dest / f"{g}_{i}.png")
            k += 1
    print(k, "sprites em", dest)


if __name__ == "__main__":
    main()
