#!/usr/bin/env python3
"""Desenhos doadores do Raiclaven com A Cliente (ChatGPT 17/11, no Chrome do PC de casa), levados ao tamanho e à cor
do ginga/00 do kit.

  python ferramentas/doador_cliente.py

Cada pedido ao ChatGPT veio com duas figuras lado a lado: à esquerda a cópia do ginga/00 (anexado) e à direita a pose
nova. A cópia da esquerda dá a régua: os pontos dela casados com o ginga/00 (SIFT) dão a escala, e as cores dela
casadas com as do ginga/00 dão a correção de cor (por canal), que vale também para a figura da direita, desenhada na
mesma imagem. Capturas em sprites/raiclaven_cliente/doadores/<nome>_cap.png (figura nova) e <nome>_orig.png (a cópia);
saída em sprites/raiclaven_cliente/quadros_arcade_hd/doador/<nome>.png (tela 1080x780, pés em 540,660).
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importar_garanhao as ig  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "sprites/raiclaven_cliente/doadores"
REF = RAIZ / "sprites/raiclaven_cliente/quadros_arcade_hd/ginga/00.png"
SAIDA = RAIZ / "sprites/raiclaven_cliente/quadros_arcade_hd/doador"
TELA, EIXO = (1080, 780), (540, 660)
DOADORES = {"agachado": "original", "defesa": "original"}  # figura nova -> cópia do ginga da mesma imagem
# o doador vira folhas de quadros iguais (o kit mexe o tronco, a criatura e os braços em cima da metade de baixo dele)
COPIAS = {"agachado": (("agachado_d", "x_agd", "y_agd", "a_agd", "b_agd"), 8)}
# deslocamento na tela para o tronco do doador cair em cima do tronco do parado (sem pulo de lado ao agachar)
AJUSTE = {"agachado": (-15, 0)}  # o doador vira uma folha de N quadros iguais (o kit respira em cima dela)


def recorte(caminho):
    a = np.array(Image.open(caminho).convert("RGB"))
    # tira a moldura verde da captura
    verde = (a[..., 1] > 200) & (a[..., 0] < 80) & (a[..., 2] < 80)
    a[verde] = (255, 0, 255)
    a[:6], a[-6:], a[:, :6], a[:, -6:] = 255, 255, 255, 255
    a[:6, :, 1] = a[-6:, :, 1] = a[:, :6, 1] = a[:, -6:, 1] = 0
    m = ig.so_o_boneco(ig.chave(a))
    rgba = np.zeros(a.shape[:2] + (4,), np.uint8)
    rgba[..., :3] = a
    rgba[..., 3] = m * 255
    rgba[~m, :3] = 0
    return rgba


def escala_e_cor(orig, ref):
    """Escala da cópia para o ginga/00 (mediana das razões de distância entre pares de pontos casados) e a cor."""
    sift = cv2.SIFT_create()
    g1 = cv2.cvtColor(orig[..., :3], cv2.COLOR_RGB2GRAY)
    g2 = cv2.cvtColor(ref[..., :3], cv2.COLOR_RGB2GRAY)
    k1, d1 = sift.detectAndCompute(g1, (orig[..., 3] > 0).astype(np.uint8))
    k2, d2 = sift.detectAndCompute(g2, (ref[..., 3] > 0).astype(np.uint8))
    bons = [m for m, n in cv2.BFMatcher().knnMatch(d1, d2, k=2) if m.distance < 0.7 * n.distance]
    p1 = np.float32([k1[m.queryIdx].pt for m in bons])
    p2 = np.float32([k2[m.trainIdx].pt for m in bons])
    M, inl = cv2.estimateAffinePartial2D(p1, p2, method=cv2.RANSAC, ransacReprojThreshold=4)
    s = float(np.hypot(M[0, 0], M[1, 0]))
    # cor: a cópia levada ao ginga, pixel a pixel onde os dois têm boneco, ajuste linear por canal
    w = cv2.warpAffine(orig, M, TELA, flags=cv2.INTER_LINEAR)
    junto = (w[..., 3] == 255) & (ref[..., 3] == 255)
    cor = []
    for c in range(3):
        x, y = w[..., c][junto].astype(float), ref[..., c][junto].astype(float)
        cor.append(np.polyfit(x, y, 1))
    return s, cor, int(inl.sum()), len(bons)


def main():
    ref = np.array(Image.open(REF).convert("RGBA"))
    SAIDA.mkdir(parents=True, exist_ok=True)
    for nome, de in DOADORES.items():
        cap = PASTA / f"{nome}_cap.png"
        if not cap.exists():
            continue
        s, cor, inl, n = escala_e_cor(recorte(PASTA / f"{de}_cap.png"), ref)
        a = recorte(cap)
        for c in range(3):
            a[..., c] = np.clip(np.polyval(cor[c], a[..., c].astype(float)), 0, 255).astype(np.uint8)
        a[a[..., 3] == 0, :3] = 0
        h, w = a.shape[:2]
        nw, nh = int(round(w * s)), int(round(h * s))
        rgb = np.array(Image.fromarray(np.ascontiguousarray(a[..., :3])).resize((nw, nh), Image.LANCZOS))
        alfa = np.array(Image.fromarray(a[..., 3]).resize((nw, nh), Image.BILINEAR)) >= 128
        p = np.zeros((nh, nw, 4), np.uint8)
        p[..., :3], p[..., 3] = rgb, alfa * 255
        p = ig.limpar_borda(p)
        ys, xs = np.nonzero(p[..., 3])
        chao, meio = ys.max(), (xs.min() + xs.max()) / 2
        tela = np.zeros((TELA[1], TELA[0], 4), np.uint8)
        ox, oy = int(round(EIXO[0] - meio)) + AJUSTE.get(nome, (0, 0))[0], int(EIXO[1] - 1 - chao)
        t = Image.fromarray(tela)
        t.alpha_composite(Image.fromarray(p), (max(0, ox), max(0, oy)))
        t.save(SAIDA / f"{nome}.png")
        folhas, n = COPIAS.get(nome, ((), 0))
        for f in folhas:
            (SAIDA.parent / f).mkdir(exist_ok=True)
            for k in range(n):
                t.save(SAIDA.parent / f / f"{k:02d}.png")
        print(f"{nome}: escala {s:.3f} ({inl}/{n} pontos), cor {[np.round(c, 2).tolist() for c in cor]}")


if __name__ == "__main__":
    main()
