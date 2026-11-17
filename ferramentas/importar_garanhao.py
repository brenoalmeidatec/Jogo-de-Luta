#!/usr/bin/env python3
"""Folhas do Garanhão (Gutto despertado, ChatGPT 16/11, 8 células iguais em fundo magenta) -> quadros 3x do jogo.

  python ferramentas/importar_garanhao.py

Cada célula vira sprites/garanhao/quadros_arcade_hd/<golpe>/<NN>.png na tela 1080x780 com os pés em 540,660 (a mesma
do firme.py). O chão da folha é a linha mais baixa dos quadros em pé; o centro da célula vai para x=540, então o
andar dentro da folha continua. Escala única (ALTURA): o Garanhão de hoje no jogo tem 88 px em 1x (264 em 3x).
Borda magenta (antialias do ChatGPT) vira contorno escuro.
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
FOLHAS = RAIZ / "sprites/garanhao/folhas"
SAIDA = RAIZ / "sprites/garanhao/quadros_arcade_hd"
TELA = (1080, 780)
EIXO = (540, 660)
ALTURA = 264 / 294  # parado da folha (294 px) -> 264 px, o tamanho do endiabrado no jogo hoje, em 3x
CONTORNO = (34, 18, 22)


def chave(a):
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    magenta = (r - g > 70) & (b - g > 70) & (abs(r - b) < 90)
    m = ~magenta
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    # tira ilhas pequenas (respingo do fundo)
    n, rot, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < 40:
            m[rot == i] = False
    return m


def so_o_boneco(m):
    """Fica só o boneco da célula: o pedaço maior e o que encosta nele (sem pé do quadro vizinho)."""
    n, rot, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
    if n <= 2:
        return m
    maior = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    perto = cv2.dilate((rot == maior).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    ok = [i for i in range(1, n) if i == maior or (perto & (rot == i)).any()]
    return np.isin(rot, ok)


def limpar_borda(rgba):
    a = rgba[..., 3] > 0
    borda = a & ~(cv2.erode(a.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    r, g, b = (rgba[..., i].astype(int) for i in range(3))
    roxo = a & ((r + b) / 2 - g > 45) & (b > 60)
    alvo = borda | (roxo & ~(cv2.erode(a.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0))
    out = rgba.copy()
    out[alvo & roxo, :3] = CONTORNO
    out[borda, :3] = np.minimum(out[borda, :3], 90)
    return out


def importar(folha):
    a = np.array(Image.open(folha).convert("RGB"))
    h, w = a.shape[:2]
    m = chave(a)
    cel = w / 8
    cortes = []
    for k in range(8):
        x0, x1 = int(round(k * cel)), int(round((k + 1) * cel))
        sub = m[:, x0:x1]
        if sub.sum() < 500:
            continue
        cortes.append((k, x0, x1))
    pes = [np.nonzero(m[:, x0:x1].any(1))[0].max() for _, x0, x1 in cortes]
    chao = int(np.median(pes))  # golpes no ar: os quadros em pé (maioria) dão o chão
    nome = folha.stem[2:]
    (SAIDA / nome).mkdir(parents=True, exist_ok=True)
    for k, x0, x1 in cortes:
        mc = so_o_boneco(m[:, x0:x1])
        rgba = np.zeros((h, x1 - x0, 4), np.uint8)
        rgba[..., :3] = a[:, x0:x1]
        rgba[..., 3] = mc * 255
        rgba[..., :3][~mc] = 0
        im = Image.fromarray(rgba)
        nw, nh = int(round(im.width * ALTURA)), int(round(im.height * ALTURA))
        # cor sem alfa misturado: reduz cor e alfa separados e corta o alfa em 50%
        cor = Image.fromarray(np.ascontiguousarray(rgba[..., :3])).resize((nw, nh), Image.LANCZOS)
        alfa = np.array(Image.fromarray(rgba[..., 3]).resize((nw, nh), Image.BILINEAR)) >= 128
        p = np.zeros((nh, nw, 4), np.uint8)
        p[..., :3] = np.array(cor)
        p[..., 3] = alfa * 255
        p = limpar_borda(p)
        tela = np.zeros((TELA[1], TELA[0], 4), np.uint8)
        ox = int(round(EIXO[0] - nw / 2))
        oy = int(round(EIXO[1] - 1 - chao * ALTURA))  # última linha do pé em 659
        ys, xs = slice(max(0, oy), min(TELA[1], oy + nh)), slice(max(0, ox), min(TELA[0], ox + nw))
        sub = p[ys.start - oy:ys.stop - oy, xs.start - ox:xs.stop - ox]
        tela[ys, xs][sub[..., 3] > 0] = sub[sub[..., 3] > 0]
        Image.fromarray(tela).save(SAIDA / nome / f"{k:02d}.png")
    print(nome, len(cortes), "quadros, chão", chao)


if __name__ == "__main__":
    for f in sorted(FOLHAS.glob("g_*.png")):
        importar(f)
