#!/usr/bin/env python3
"""Grão-Pastor (Gbzin despertado) pelo boneco de peças.

O desenho-mestre é a vista 3/4 do conceito aprovado pelo Breno (quadros/folhas_arcade/e_conceito.png, 2ª figura).
Dela sai o parado de referência em 3x (1080x780, cascos em y=660, eixo x=540), a paleta própria de 15 cores e o kit
de peças (cabeça separada para trocar depois). Os rascunhos de pose do ChatGPT só dão a pose: rosto, corpo e cores
vêm do kit.

  python ferramentas/gbzin_e_pecas.py ref      parado de referência + paleta em sprites/gbzin/pecas_e/
"""
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
SPR = RAIZ / "sprites" / "gbzin"
PECAS = SPR / "pecas_e"
CONCEITO = SPR / "quadros/folhas_arcade/e_conceito.png"
TELA = (1080, 780)
CHAO, EIXO = 660, 540
FIGURA_X = (451, 1017)     # coluna da vista 3/4 no e_conceito
ESCALA = 0.613             # 630 px do cabelo ao casco no conceito -> ~386 px no 3x (rascunho de 545 px x 0.708)
CORES = 15


def sem_magenta(rgb):
    r, g, b = (rgb[..., i].astype(int) for i in range(3))
    mag = (r > 140) & (b > 140) & (g < 130) & (np.abs(r - b) < 100)
    roxo_fundo = (r > 110) & (b > 110) & (g < 60) & ((r + b) - 2 * g > 260)
    fundo = mag | roxo_fundo
    a = (~fundo).astype(np.uint8)
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return a


def lab(rgb):
    return cv2.cvtColor(np.asarray(rgb, np.float32).reshape(-1, 1, 3) / 255, cv2.COLOR_RGB2LAB).reshape(-1, 3)


def ref():
    PECAS.mkdir(parents=True, exist_ok=True)
    im = np.asarray(Image.open(CONCEITO).convert("RGB"))
    sub = im[:, FIGURA_X[0]:FIGURA_X[1]].astype(np.float32)
    a = sem_magenta(sub)
    a = cv2.erode(a, np.ones((2, 2), np.uint8))  # a borda antialiasada puxa magenta
    h, w = a.shape
    nw, nh = round(w * ESCALA), round(h * ESCALA)
    pm = cv2.resize(sub * a[..., None], (nw, nh), interpolation=cv2.INTER_AREA)
    aa = cv2.resize(a.astype(np.float32), (nw, nh), interpolation=cv2.INTER_AREA)
    cor = pm / np.maximum(aa[..., None], 1e-3)
    opaco = aa >= 0.55
    px = cor[opaco]
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 80, 0.1)
    _, lbl, cen = cv2.kmeans(lab(px), CORES, None, crit, 6, cv2.KMEANS_PP_CENTERS)
    pal = (cv2.cvtColor(cen.reshape(-1, 1, 3), cv2.COLOR_LAB2RGB).reshape(-1, 3) * 255).round().clip(20, 255)
    pal = pal.astype(np.uint8)
    ordem = np.argsort(lab(pal)[:, 0])
    pal = pal[ordem]
    idx = np.argmin(((lab(px)[:, None] - lab(pal)[None]) ** 2).sum(-1), 1)
    fig = np.zeros((nh, nw, 4), np.uint8)
    fig[opaco, :3] = pal[idx]
    fig[opaco, 3] = 255
    ys, xs = np.nonzero(opaco)
    base = ys.max()
    # eixo: meio do quadril (entre os cascos), medido na linha dos cascos
    pes = xs[ys > base - 40]
    meio = (pes.min() + pes.max()) // 2
    tela = np.zeros((TELA[1], TELA[0], 4), np.uint8)
    x0, y0 = EIXO - meio, CHAO - base
    tela[y0:y0 + nh, x0:x0 + nw] = fig
    Image.fromarray(tela).save(PECAS / "ref.png")
    (PECAS / "paleta.json").write_text(json.dumps({"fonte": "e_conceito.png (vista 3/4)", "cores": pal.tolist()},
                                                  indent=1), encoding="utf-8")
    ys, xs = np.nonzero(tela[..., 3])
    print(f"ref: figura {xs.min()}-{xs.max()} x {ys.min()}-{ys.max()} ({ys.max() - ys.min() + 1} px de altura)")



# ------------------------------------------------------------------ parado vivo (respiração sem corte)
# O parado não é montado em peças soltas: o corpo inteiro respira por um campo de deslocamento contínuo (cada linha
# desce um pouco mais que a de baixo), então não existe emenda nem linha de corte. Os cascos ficam presos no chão,
# a cintura desce 1 pixel do jogo, o peito e os ombros 1,3 e a cabeça chega um tique depois (atraso).
RESPIRA = 4.0          # descida do peito no 3x
CINTURA, COXA = 450, 560
PESCOCO = 365


def _passo(y, a, b_):
    t = np.clip((y - a) / (b_ - a), 0, 1)
    return t * t * (3 - 2 * t)


def _quadro_parado(base, t, n):
    fase = lambda k: (1 - math.cos(2 * math.pi * k / n)) / 2  # noqa: E731
    corpo, cabeca = RESPIRA * fase(t), RESPIRA * 1.15 * fase(t - 0.7)
    yy, xx = np.mgrid[:TELA[1], :TELA[0]].astype(np.float32)
    peso_corpo = 1 - _passo(yy, CINTURA, COXA)           # 1 em cima da cintura, 0 na coxa
    peso_peito = 1 + 0.3 * (1 - _passo(yy, 380, CINTURA))  # o peito sobe mais que a cintura
    peso_cab = 1 - _passo(yy, PESCOCO - 25, PESCOCO + 15)
    dy = corpo * peso_corpo * peso_peito * (1 - peso_cab) + cabeca * peso_cab
    # a pele do manto nos lados balança meio pixel do jogo, atrasada (sobreposição de movimento)
    lado = _passo(np.abs(xx - EIXO), 110, 170) * _passo(yy, 330, 420) * (1 - _passo(yy, 560, 600))
    dx = 1.5 * math.sin(2 * math.pi * (t - 1.5) / n) * lado * np.sign(xx - EIXO)
    mapa_x, mapa_y = xx - dx, yy - dy
    return cv2.remap(base, mapa_x, mapa_y, cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def parado(n=8):
    base = np.asarray(Image.open(PECAS / "ref.png"))
    saida = SPR / "quadros_e_pecas_hd" / "referencia_ginga"
    saida.mkdir(parents=True, exist_ok=True)
    quadros = [_quadro_parado(base, t, n) for t in range(n)]
    for i, q in enumerate(quadros):
        Image.fromarray(q).save(saida / f"{i:02d}.png")
    print(f"parado: {n} quadros em {saida.relative_to(RAIZ)}")
    return quadros


if __name__ == "__main__":
    {"ref": ref, "parado": parado}[sys.argv[1]]()
