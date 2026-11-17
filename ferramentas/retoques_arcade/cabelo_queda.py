"""Cabelo da queda (cabeça tombada/deitada): os vinhos da pele (PS, GE) a até 2 px de um pixel de cabelo (CE, CL),
dentro da caixa da cabeça, viram cabelo_escuro. uso: cabelo_queda.py <entrada> <saida>"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
PS, GE, CE, CL = (0x8A,0x32,0x1C), (0x5F,0x1A,0x14), (0x33,0x2C,0x20), (0x75,0x6C,0x4E)
# caixa do cabelo (x0, y0, x1, y1) em cada desenho, vista ampliada
CAIXA = {0: (134, 104, 156, 130), 1: (120, 120, 142, 146), 2: (106, 150, 124, 178), 3: (106, 168, 124, 192),
         4: (118, 176, 136, 200), 5: (122, 180, 140, 204), 6: (116, 176, 136, 200), 7: (108, 190, 124, 214)}
ent, sai = Path(sys.argv[1]), Path(sys.argv[2])
for q, (x0, y0, x1, y1) in CAIXA.items():
    a = np.array(Image.open(ent / f"{q:02d}.png").convert("RGBA"))
    eh = lambda c: (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & (a[..., 3] > 0)
    caixa = np.zeros(a.shape[:2], bool); caixa[y0:y1, x0:x1] = True
    cabelo = (eh(CE) | eh(CL)) & caixa
    for _ in range(2):
        perto = ndimage.binary_dilation(cabelo, structure=np.ones((3, 3), bool))
        cabelo |= perto & (eh(PS) | eh(GE)) & caixa
    troca = cabelo & (eh(PS) | eh(GE))
    a[troca] = CE + (255,)
    Image.fromarray(a).save(sai / f"{q:02d}.png")
    print(q, int(troca.sum()))
