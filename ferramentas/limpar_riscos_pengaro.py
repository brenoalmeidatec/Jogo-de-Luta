#!/usr/bin/env python3
"""Pengaró redesenhado: apaga os riscos soltos que o ChatGPT deixou nas folhas novas (rastro colorido atrás da garrafa
na corrida, fiapos rosa/roxos/azuis perto do pé, da mão e do rosto), direto na folha de folhas_novas/, para o 1x e o 3x
saírem limpos do converter_pengaro.py.

  python ferramentas/limpar_riscos_pengaro.py            limpa os quadros da lista RISCOS
  python ferramentas/limpar_riscos_pengaro.py --ver      só mostra (antes | depois) em docs/arcade/img/pengaro_riscos.png

Risco = pixel fino (longe de qualquer parte grossa do desenho) que não é pele, cordão laranja nem contorno escuro,
ou pedacinho solto do corpo. Dedos, cordões e contornos ficam. Só mexe nos quadros da lista, que foram conferidos.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import animar_folha as af  # noqa: E402

FOLHAS = af.RAIZ / "sprites/pengaro/quadros/folhas_novas"
SAIDA_VER = af.RAIZ / "docs/arcade/img/pengaro_riscos.png"

# folha: quadros (0..7) com riscos soltos, conferidos olhando quadro a quadro
RISCOS = {
    "corre": (1, 2, 3, 4, 5, 6, 7),
    "afastar": (1, 2, 3, 4, 5),
    "pulo": (2, 3, 4, 5),
    "rasteira": (2, 5),
}


def riscos(rgb, corpo):
    """Máscara dos pixels de risco dentro de corpo (bool), no recorte de uma célula."""
    a = corpo.astype(np.uint8)
    grosso = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    perto = cv2.dilate(grosso, np.ones((9, 9), np.uint8)) > 0
    r, g, b = (rgb[..., i].astype(int) for i in range(3))
    quente = (r > g + 15) & (g >= b - 5) & (r > 90)        # pele e cordão laranja
    escuro = (r + g + b) < 150                             # contorno
    fino = corpo & ~perto & ~quente & ~escuro
    # pedacinhos soltos (não ligados ao corpo grande)
    n, rot, info, _ = cv2.connectedComponentsWithStats(a, connectivity=8)
    solto = np.zeros_like(corpo)
    if n > 1:
        maior = 1 + int(np.argmax(info[1:, cv2.CC_STAT_AREA]))
        for j in range(1, n):
            if j != maior and info[j, cv2.CC_STAT_AREA] < 150:
                solto |= rot == j
    # o contorno escuro que sobrou colado só no risco apagado também sai
    fora = fino | solto
    resto = corpo & ~fora
    n, rot, info, _ = cv2.connectedComponentsWithStats(resto.astype(np.uint8), connectivity=8)
    if n > 1:
        maior = 1 + int(np.argmax(info[1:, cv2.CC_STAT_AREA]))
        for j in range(1, n):
            if j != maior and info[j, cv2.CC_STAT_AREA] < 60:
                fora |= rot == j
    return fora


def limpar(nome, quadros):
    caminho = FOLHAS / f"{nome}.png"
    original = Image.open(caminho).convert("RGB")
    limpa = np.array(af.fundo_ck(original).convert("RGB"))
    fundo = (limpa[..., 0] == 255) & (limpa[..., 1] == 0) & (limpa[..., 2] == 255)
    saida = np.array(original)
    largura = saida.shape[1] / 8
    total = 0
    for i in quadros:
        x0, x1 = round(i * largura), round((i + 1) * largura)
        m = riscos(limpa[:, x0:x1], ~fundo[:, x0:x1])
        saida[:, x0:x1][m] = (255, 0, 255)
        total += int(m.sum())
    return original, Image.fromarray(saida), total


def main():
    ver = "--ver" in sys.argv
    linhas = []
    for nome, quadros in RISCOS.items():
        antes, depois, n = limpar(nome, quadros)
        print(f"{nome}: {n} pixels de risco apagados nos quadros {quadros}")
        if ver:
            linhas.append((antes, depois))
        else:
            depois.save(FOLHAS / f"{nome}.png")
    if ver:
        w = 1400
        tiras = []
        for a, d in linhas:
            for im in (a, d):
                im = im.copy()
                im.thumbnail((w, 10_000))
                tiras.append(im)
        out = Image.new("RGB", (w, sum(t.height for t in tiras)), (0, 0, 0))
        y = 0
        for t in tiras:
            out.paste(t, (0, y))
            y += t.height
        out.save(SAIDA_VER)
        print(SAIDA_VER)


if __name__ == "__main__":
    main()
