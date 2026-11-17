#!/usr/bin/env python3
"""Folhas do Raiclaven despertado com A Cliente nas costas (ChatGPT 15-16/11, 8 células em fundo magenta) -> quadros 3x.

  python ferramentas/importar_cliente.py [nomes...]

Mesmo corte do importar_garanhao.py (tela 1080x780, pés em 540,660). O ChatGPT desenhou cada folha num tamanho
(b_ag saiu com o boneco 35% menor, despertar maior), então cada folha tem a sua escala, medida pelo tanque verde das
costas, que é uma peça dura e aparece em todo quadro: a área dele na folha vira a área do tanque no ginga. O ginga dá a
escala do jogo: o Raiclaven da folha (do cabelo à sola, 284 px) vira o Raiclaven do jogo hoje (359 px em 3x); a criatura
vem junto, por cima. Saída em sprites/raiclaven_cliente/quadros_arcade_hd/<golpe>/NN.png (gitignored).
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importar_garanhao as ig  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FOLHAS = RAIZ / "sprites/raiclaven/quadros/folhas_criatura"
SAIDA = RAIZ / "sprites/raiclaven_cliente/quadros_arcade_hd"
TELA, EIXO = ig.TELA, ig.EIXO
ALTURA = 359 / 284  # ginga da folha -> jogo
NO_AR = {"pulo"}  # folha só de quadros no ar: o quadro mais baixo encosta no chão


def area_tanque(a, x0, x1):
    r, g, b = (a[:, x0:x1, i].astype(int) for i in range(3))
    lime = ((g > 170) & (r > 90) & (r < 215) & (b < 110)).astype(np.uint8)
    lime = cv2.morphologyEx(lime, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, _, st, _ = cv2.connectedComponentsWithStats(lime, 8)
    return int(st[1:, cv2.CC_STAT_AREA].max()) if n > 1 else None


_REF = None


def ref_tanque():
    global _REF
    if _REF is None:
        a = np.array(Image.open(FOLHAS / "c_ginga.png").convert("RGB"))
        cel = a.shape[1] / 8
        _REF = float(np.median([area_tanque(a, int(k * cel), int((k + 1) * cel)) for k in range(8)]))
    return _REF


def importar(folha):
    a = np.array(Image.open(folha).convert("RGB"))
    h, w = a.shape[:2]
    m = ig.chave(a)
    cel = w / 8
    cortes = [(k, int(round(k * cel)), int(round((k + 1) * cel))) for k in range(8)]
    cortes = [c for c in cortes if m[:, c[1]:c[2]].sum() >= 500]
    areas = [x for x in (area_tanque(a, x0, x1) for _, x0, x1 in cortes) if x]
    folha_esc = float(np.clip(np.sqrt(ref_tanque() / np.median(areas)), 0.75, 1.7))
    esc = ALTURA * folha_esc
    pes = [np.nonzero(m[:, x0:x1].any(1))[0].max() for _, x0, x1 in cortes]
    nome = folha.stem[2:]
    chao = int(max(pes)) if nome in NO_AR else int(np.median(pes))
    (SAIDA / nome).mkdir(parents=True, exist_ok=True)
    for k, x0, x1 in cortes:
        mc = ig.so_o_boneco(m[:, x0:x1])
        rgba = np.zeros((h, x1 - x0, 4), np.uint8)
        rgba[..., :3] = a[:, x0:x1]
        rgba[..., 3] = mc * 255
        rgba[..., :3][~mc] = 0
        nw, nh = int(round(rgba.shape[1] * esc)), int(round(h * esc))
        cor = Image.fromarray(np.ascontiguousarray(rgba[..., :3])).resize((nw, nh), Image.LANCZOS)
        alfa = np.array(Image.fromarray(rgba[..., 3]).resize((nw, nh), Image.BILINEAR)) >= 128
        p = np.zeros((nh, nw, 4), np.uint8)
        p[..., :3] = np.array(cor)
        p[..., 3] = alfa * 255
        p = ig.limpar_borda(p)
        tela = np.zeros((TELA[1], TELA[0], 4), np.uint8)
        ox = int(round(EIXO[0] - nw / 2))
        oy = int(round(EIXO[1] - 1 - chao * esc))
        ys, xs = slice(max(0, oy), min(TELA[1], oy + nh)), slice(max(0, ox), min(TELA[0], ox + nw))
        sub = p[ys.start - oy:ys.stop - oy, xs.start - ox:xs.stop - ox]
        tela[ys, xs][sub[..., 3] > 0] = sub[sub[..., 3] > 0]
        Image.fromarray(tela).save(SAIDA / nome / f"{k:02d}.png")
    print(f"{nome}: {len(cortes)} quadros, escala da folha {folha_esc:.2f}, chão {chao}")


if __name__ == "__main__":
    nomes = sys.argv[1:]
    for f in sorted(FOLHAS.glob("c_*.png")):
        if not nomes or f.stem[2:] in nomes:
            importar(f)
