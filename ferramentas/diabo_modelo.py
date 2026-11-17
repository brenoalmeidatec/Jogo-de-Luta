#!/usr/bin/env python3
"""Poses novas do Diabo demônio (folha de poses do ChatGPT feita em cima da folha-modelo) levadas ao tamanho e às
cores do kit, na tela 3x do firme.py: sprites/diabo_demonio/quadros_arcade_hd/modelo/NN.png.

São os desenhos-fonte das peças que o kit não tinha (corpo agachado, braços na defesa, deitado, no ar, ajoelhado).
A escala sai da altura da defesa em pé (curvado como o parado) contra a do parado; as cores são trocadas cor a cor
pelas do parado (paleta travada).

    python3 ferramentas/diabo_modelo.py
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
PECAS = RAIZ / "sprites/diabo_demonio/pecas"
SAIDA = RAIZ / "sprites/diabo_demonio/quadros_arcade_hd/modelo"
TELA, PE = (1080, 780), (540, 659)
# ordem da folha de poses (2 linhas x 4 colunas)
NOMES = ["agachado", "agachado_garra", "defesa", "defesa_baixa", "deitado", "apanha", "no_ar", "ajoelhado"]
# segunda folha (mesma escala pedida): modelo/08 a 15
NOMES2 = ["corrida", "cobranca", "vitoria", "sentado", "provoca", "agarra", "garra_sobe", "pulo_tras"]
# folhas de poses seguintes (na mesma escala da primeira): entram depois da frente e das costas, de modelo/18 em diante
MAIS = [("folha_poses3.png", ["ar_garra", "ar_garras_alto", "mergulho", "ar_joelho", "ar_pisao", "martelo", "chicote_rabo", "mordida"])]  # 18-25
REF_ESCALA = 2  # a defesa em pé tem a mesma curvatura do parado


def figuras(img):
    a = np.array(img.convert("RGB")).astype(int)
    mag = (a[..., 0] > 190) & (a[..., 2] > 190) & (a[..., 1] < 110)
    fg = cv2.morphologyEx((~mag).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg, 8)
    figs = [(i, st[i]) for i in range(1, n) if st[i, 4] > 3000]
    figs.sort(key=lambda t: (t[1][1] + t[1][3] / 2 > 512, t[1][0]))
    out = []
    for i, (x, y, w, h, _) in figs:
        m = lab[y:y + h, x:x + w] == i
        rgba = np.zeros((h, w, 4), np.uint8)
        rgba[..., :3] = a[y:y + h, x:x + w]
        rgba[..., 3] = m * 255
        out.append(rgba)
    return out


def travar(rgba, paleta):
    al = rgba[..., 3] > 0
    px = rgba[al][:, :3].astype(np.float32)
    idx = np.empty(len(px), np.int64)
    for k in range(0, len(px), 20000):
        d = ((px[k:k + 20000, None, :] - paleta[None]) ** 2).sum(-1)
        idx[k:k + 20000] = d.argmin(1)
    out = rgba.copy()
    out[al, :3] = paleta[idx].astype(np.uint8)
    return out


def main():
    par = np.array(Image.open(RAIZ / "sprites/diabo_demonio/quadros_arcade_hd/parado/00.png").convert("RGBA"))
    paleta = np.unique(par[par[..., 3] > 0][:, :3], axis=0).astype(np.float32)
    h_par = np.ptp(np.nonzero(par[..., 3] > 0)[0]) + 1
    figs = figuras(Image.open(PECAS / "folha_poses.png"))
    assert len(figs) == len(NOMES), len(figs)
    e = h_par / figs[REF_ESCALA].shape[0]
    SAIDA.mkdir(parents=True, exist_ok=True)
    figs2 = figuras(Image.open(PECAS / "folha_poses2.png"))
    assert len(figs2) == len(NOMES2), len(figs2)
    # folha-modelo: frente e costas (modelo/16 e 17), na escala em que o perfil dela fica do tamanho do parado
    fm = figuras(Image.open(PECAS / "folha_modelo.png"))
    e_fm = h_par / fm[0].shape[0]
    todas = [(n, f, e) for n, f in zip(NOMES + NOMES2, figs + figs2)] + [("frente", fm[1], e_fm), ("costas", fm[2], e_fm)]
    for arq, nomes in MAIS:
        fs = figuras(Image.open(PECAS / arq))
        assert len(fs) == len(nomes), (arq, len(fs))
        todas += [(n, f, e) for n, f in zip(nomes, fs)]
    for k, (nome, f, e) in enumerate(todas):
        h, w = f.shape[:2]
        im = Image.fromarray(f).resize((round(w * e), round(h * e)), Image.LANCZOS)
        a = np.array(im)
        a[..., 3] = np.where(a[..., 3] > 127, 255, 0)
        a = travar(a, paleta)
        m = a[..., 3] > 0
        hh = a.shape[0]
        xs = np.nonzero(m[int(hh * 0.25):max(int(hh * 0.25) + 1, int(hh * 0.6))])[1]
        ax = float(np.median(xs)) if len(xs) else a.shape[1] / 2
        tela = Image.new("RGBA", TELA, (0, 0, 0, 0))
        tela.alpha_composite(Image.fromarray(a), (int(round(PE[0] - ax)), PE[1] - (hh - 1)))
        tela.save(SAIDA / f"{k:02d}.png")
        print(k, nome, a.shape[:2])
    print("escala", round(e, 3))


if __name__ == "__main__":
    main()
