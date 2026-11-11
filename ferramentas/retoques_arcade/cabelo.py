"""Retoque: cabelo que a quantizacao levou para os vinhos da pele volta para cabelo_escuro/cabelo_luz.
uso: cabelo.py <dir_entrada> <dir_saida> folha:quadros ...   (quadros = 0-7 ou lista 0,5,6,7)"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

PC, PS, PM, PL, PB = (0x4C,0x14,0x14), (0x8A,0x32,0x1C), (0xDF,0x7E,0x3F), (0xFD,0xC3,0x72), (0xFD,0xEC,0xCF)
GE, CE, CL = (0x5F,0x1A,0x14), (0x33,0x2C,0x20), (0x75,0x6C,0x4E)

def eh(a, c):
    return (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & (a[..., 3] > 0)

def retoca(img):
    a = np.array(img.convert("RGBA"))
    ys, xs = np.nonzero(a[..., 3] > 0)
    y0 = ys.min(); xc = int(np.median(xs[ys < y0 + 6]))
    yy, xx = np.mgrid[:a.shape[0], :a.shape[1]]
    dy, dx = yy - y0, xx - xc
    caixa = (dy >= 0) & (np.abs(dx) <= 14) & (((dx > 4) & (dy <= 6)) | ((dx >= -3) & (dx <= 4) & (dy <= 9)) | ((dx < -3) & (dy <= 13)))
    escuro = eh(a, PC) | eh(a, PS) | eh(a, GE) | eh(a, CE) | eh(a, CL)
    rot, n = ndimage.label(escuro & caixa)
    semente = np.unique(rot[(dy <= 3) & caixa & (rot > 0)])
    cabelo = np.isin(rot, semente) & (rot > 0)
    troca = cabelo & (eh(a, PS) | eh(a, GE))
    claro = eh(a, PL) | eh(a, PB) | eh(a, PM)
    perto_do_brilho = ndimage.binary_dilation(claro & caixa & (dy <= 5), iterations=1)
    a[troca & eh(a, GE)] = CE + (255,)
    luz = troca & eh(a, PS) & perto_do_brilho & (dy <= 5)
    a[luz] = CL + (255,)
    a[troca & eh(a, PS)] = CE + (255,)
    return Image.fromarray(a), int(troca.sum())

ent, sai = Path(sys.argv[1]), Path(sys.argv[2])
for item in sys.argv[3:]:
    folha, qs = item.split(":")
    qs = range(8) if qs == "0-7" else [int(q) for q in qs.split(",")]
    (sai / folha).mkdir(parents=True, exist_ok=True)
    for q in qs:
        img, n = retoca(Image.open(ent / folha / f"{q:02d}.png"))
        img.save(sai / folha / f"{q:02d}.png")
        print(folha, q, n)
