#!/usr/bin/env python3
"""Monta uma folha 2172x724 (8 quadros, fundo magenta) a partir de duas imagens do Gemini com 4 quadros cada.

O Gemini do Alisson (plano Pro) devolve na página imagens de 1024 px de largura. Com 8 quadros numa imagem só, o boneco
sai pequeno (~280 px) e borraria no 3x (receita, seção 3). Com 4 quadros numa imagem 16:9 (1024x572) ele sai com
~460 px, o mesmo tamanho da referencia_ginga do ChatGPT. Então cada folha vira dois pedidos (quadros 1-4 e 5-8), e
este script junta as duas metades no formato que o converter_<lutador>.py espera:

  - recorta as figuras pelo magenta (componentes conectados, agrupados em 4 colunas);
  - põe cada figura no centro da sua célula de 271 px, com o chão da metade em y=CHAO (pulo e queda guardam a altura);
  - escala ESCALA (1.0 = mesmo tamanho da referência); figura mais larga que a célula é reduzida só o necessário.

  python ferramentas/montar_folha_gemini.py METADE_1.png METADE_2.png SAIDA.png [--chao 612] [--escala 1.0]
"""
import argparse

import cv2
import numpy as np
from PIL import Image

LARG, ALT, CEL = 2172, 724, 2172 / 8


def mascara(a):
    """Tudo o que não é fundo magenta (o Gemini entrega magenta com ruído de compressão)."""
    r, g, b = (a[..., i].astype(int) for i in range(3))
    fundo = (r > 150) & (b > 150) & (g < 110) & (abs(r - b) < 90)
    m = (~fundo).astype(np.uint8)
    return m


def figuras(caminho, n=4):
    a = np.array(Image.open(caminho).convert("RGB"))
    m = mascara(a)
    k, rot, dados, centros = cv2.connectedComponentsWithStats(m, connectivity=8)
    for i in range(1, k):  # tira sujeira solta
        if dados[i, cv2.CC_STAT_AREA] < 40:
            m[rot == i] = 0
    # cortes entre as figuras: a coluna mais vazia perto de cada divisa (figuras que se encostam, pé em cajado)
    w = a.shape[1] / n
    perfil = m.sum(0).astype(float)
    cortes = [0]
    for j in range(1, n):
        x0, x1 = int(j * w - 0.3 * w), int(j * w + 0.3 * w)
        cortes.append(x0 + int(np.argmin(perfil[x0:x1])))
    cortes.append(a.shape[1])
    # cada pedaço inteiro vai para a coluna onde está a maior parte dele; só um pedaço grande dos dois lados (duas
    # figuras coladas) é cortado na divisa
    coluna = np.searchsorted(cortes, np.arange(a.shape[1]), side="right") - 1
    k, rot = cv2.connectedComponents(m, connectivity=8)
    dono = np.full(m.shape, -1, int)
    for i in range(1, k):
        ys, xs = np.where(rot == i)
        cont = np.bincount(coluna[xs], minlength=n)
        if (cont > 0.15 * len(xs)).sum() > 1 and len(xs) > 2000:
            dono[ys, xs] = coluna[xs]
        else:
            dono[ys, xs] = int(np.argmax(cont))
    chao = 0
    saida = []
    for j in range(n):
        sel = dono == j
        ys, xs = np.where(sel)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.dstack([a, (sel * 255).astype(np.uint8)])[y0:y1, x0:x1]
        saida.append((rgba, y0, y1))
        chao = max(chao, y1)
    return saida, chao


def montar(m1, m2, destino, chao_folha=612, escala=1.0):
    folha = Image.new("RGB", (LARG, ALT), (255, 0, 255))
    quadros = []
    for caminho in (m1, m2):
        figs, chao = figuras(caminho)
        quadros += [(f, y0, y1, chao) for f, y0, y1 in figs]
    for i, (f, y0, y1, chao) in enumerate(quadros):
        s = escala
        if f.shape[1] * s > CEL - 6:
            s = (CEL - 6) / f.shape[1]
        img = Image.fromarray(f, "RGBA")
        if s != 1:
            img = img.resize((max(1, round(f.shape[1] * s)), max(1, round(f.shape[0] * s))), Image.LANCZOS)
        fundo_ate_chao = (chao - y1) * s  # quanto a figura está acima do chão da metade (pulo, queda)
        x = round(CEL * i + (CEL - img.width) / 2)
        y = round(chao_folha - fundo_ate_chao - img.height)
        y = max(0, min(ALT - img.height, y))
        alfa = img.split()[3].point(lambda v: 255 if v > 127 else 0)
        folha.paste(img.convert("RGB"), (x, y), alfa)
    folha.save(destino)
    return [(q[0].shape[1], q[0].shape[0]) for q in quadros]


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("m1")
    p.add_argument("m2")
    p.add_argument("saida")
    p.add_argument("--chao", type=int, default=612)
    p.add_argument("--escala", type=float, default=1.0)
    a = p.parse_args()
    print(montar(a.m1, a.m2, a.saida, a.chao, a.escala))
