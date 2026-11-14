#!/usr/bin/env python3
"""Recorta o retrato bruto do ChatGPT (sprites/retratos/brutos/<lutador>.png, busto em fundo magenta) nos dois
retratos do jogo, já no tamanho final da tela (o layout desenha com escala 1/4, o motor amplia 4x):

  sprites/retratos/<lutador>_busto.png   448x216  retrato grande da seleção e da tela de VS (9000,1)
  sprites/retratos/<lutador>_rosto.png   100x100  quadradinho da grade e do HUD (9000,0)

  python ferramentas/preparar_retratos.py [lutador ...]      (sem nome: todos os brutos)
Depois: python ferramentas/trocar_retratos.py
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from animar_cenario import sem_fundo, sem_rosa  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "sprites" / "retratos"
BUSTO = (448, 216)
ROSTO = 100
# deslocamento do quadrado do rosto (fração do lado): o boné do CK fica alto e o rosto mais embaixo e à frente
AJUSTE_ROSTO = {"ck": (0.06, 0.20)}


def cabeca(a):
    """Centro x da cabeça e topo: o meio das linhas cheias no quinto de cima da figura."""
    m = a[..., 3] > 0
    ys = np.flatnonzero(m.any(axis=1))
    topo, base = ys[0], ys[-1]
    faixa = m[topo:topo + max(1, (base - topo) // 5)]
    xs = np.flatnonzero(faixa.any(axis=0))
    return (xs[0] + xs[-1]) / 2, topo


def preparar(lutador):
    img = sem_fundo(Image.open(PASTA / "brutos" / f"{lutador}.png"))
    a = np.array(img)
    cx, topo = cabeca(a)
    # busto: do topo da cabeça para baixo, largura 2,4x a altura da cabeça... na proporção 448x216
    larg = img.width * 0.78
    alt = larg * BUSTO[1] / BUSTO[0]
    x0 = min(max(0, cx - larg * 0.55), img.width - larg)
    y0 = max(0, topo - alt * 0.06)
    busto = img.crop((round(x0), round(y0), round(x0 + larg), round(y0 + alt))).resize(BUSTO, Image.LANCZOS)
    # rosto: quadrado em volta da cabeça
    lado = img.height * 0.40
    dx, dy = AJUSTE_ROSTO.get(lutador, (0, 0))
    rx0 = min(max(0, cx - lado * (0.30 - dx)), img.width - lado)  # olha para a direita: mais espaço na frente
    ry0 = max(0, topo - lado * (0.05 - dy))
    rosto = img.crop((round(rx0), round(ry0), round(rx0 + lado), round(ry0 + lado))).resize((ROSTO, ROSTO), Image.LANCZOS)
    for nome, im in (("busto", busto), ("rosto", rosto)):
        im.putalpha(im.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
        sem_rosa(im).save(PASTA / f"{lutador}_{nome}.png")
    print(f"{lutador}: busto {BUSTO[0]}x{BUSTO[1]}, rosto {ROSTO}x{ROSTO}")


def main():
    nomes = sys.argv[1:] or sorted(p.stem for p in (PASTA / "brutos").glob("*.png"))
    for n in nomes:
        preparar(n)


if __name__ == "__main__":
    main()
