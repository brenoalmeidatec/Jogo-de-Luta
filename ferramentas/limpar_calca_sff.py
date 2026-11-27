#!/usr/bin/env python3
"""Tira manchas escuras de dentro da calça clara direto nos sprites do .sff (auditoria do Breno, #32, 24/11, item 3:
"chute forte de longe do Pengaró: calça branca com manchas escuras").

  python3 ferramentas/limpar_calca_sff.py pengaro 49049 [--quadros 2-9] [--ver SAIDA.png]

Para cada sprite do grupo: acha a calça (pixel claro e pouco saturado), fecha os buracos dela e repinta só o que
está DENTRO da calça e é escuro ou arroxeado (as manchas), mais as rachaduras transparentes finas dentro do corpo,
com a cor clara mais próxima em volta. Listras verdes e
amarelas, corda, pele e garrafa não entram (têm cor). Paleta e tamanho do sprite não mudam; o resto do .sff é
regravado igual (conferir_sff.religar).
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conferir_sff as cs  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
LIMITE = 150  # maior mancha (px) que ainda é mancha; --limite muda


def rgb_da_paleta(pal):
    return np.array([[pal[4 * k], pal[4 * k + 1], pal[4 * k + 2]] for k in range(256)], np.int32)


def limpar(px, w, h, cores):
    """Duas coisas, no miolo da calça (calça clara fechada por um disco de 11 px):
    - mancha: pedaço pequeno (até LIMITE px), escuro (a 1 px da borda) ou arroxeado (a 4 px), que não é listra
      verde/amarela nem pele/corda;
    - rachadura: buraco transparente fino dentro do corpo (o corpo fechado por um disco de 7 px), até 300 px, só a
      3 px ou mais da borda da calça (na borda, os dentes do contorno são desenho e ficam).
    Repinta com a cor de calça mais comum em volta (se não houver calça perto, a cor mais comum em volta)."""
    idx = np.frombuffer(bytes(px), np.uint8).reshape(h, w)
    rgb = cores[idx]
    mx, mn = rgb.max(2), rgb.min(2)
    lum = rgb.mean(2)
    sat = (mx - mn) / np.maximum(mx, 1)
    calca = (idx != 0) & (lum > 170) & (sat < 0.22)
    if calca.sum() < 50:
        return px, 0
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    fechada = cv2.morphologyEx(calca.astype(np.uint8), cv2.MORPH_CLOSE, k).astype(bool)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    listra = (g > r) | ((r > 180) & (g > 120) & (b < 90))
    pele = (r > g + 25) & (r > b + 25)
    def miolo(n):
        return cv2.erode(fechada.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=n).astype(bool)
    # escura (lum < 130) até 1 px da borda; o meio-tom arroxeado só bem dentro (a 4 px), porque a sombra da barra
    # da calça também é arroxeada e é desenho
    escura = miolo(1) & (lum < 130)
    roxa = miolo(4) & (b > g + 10) & (lum < 200)
    mancha = ~calca & (((idx != 0) & (escura | roxa) & ~listra & ~pele) | (miolo(3) & (idx == 0)))
    tira = _pequenos(mancha, LIMITE)
    corpo = cv2.morphologyEx((idx != 0).astype(np.uint8), cv2.MORPH_CLOSE,
                             cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))).astype(bool)
    tira |= _pequenos(corpo & miolo(3) & (idx == 0), 300)
    if not tira.any():
        return px, 0
    novo = idx.copy()
    for y, x in zip(*np.nonzero(tira)):
        y0, y1, x0, x1 = max(0, y - 5), min(h, y + 6), max(0, x - 5), min(w, x + 6)
        viz = idx[y0:y1, x0:x1][calca[y0:y1, x0:x1]]
        if viz.size < 3:
            viz = idx[y0:y1, x0:x1]
            viz = viz[viz != 0]
        if viz.size:
            vals, cont = np.unique(viz, return_counts=True)
            novo[y, x] = vals[np.argmax(cont)]
    return novo.tobytes(), int(tira.sum())


def _pequenos(mascara, limite):
    n, rot, st, _ = cv2.connectedComponentsWithStats(mascara.astype(np.uint8), 8)
    out = np.zeros_like(mascara)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] <= limite:
            out |= rot == i
    return out


def main():
    a = sys.argv[1:]
    lutador, grupo = a[0], int(a[1])
    quadros = None
    if "--quadros" in a:
        q = a[a.index("--quadros") + 1]
        i0, i1 = (int(v) for v in q.split("-"))
        quadros = set(range(i0, i1 + 1))
    ver = Path(a[a.index("--ver") + 1]) if "--ver" in a else None
    global LIMITE
    if "--limite" in a:
        LIMITE = int(a[a.index("--limite") + 1])
    sff = RAIZ / "chars" / lutador / f"{lutador}.sff"
    pal, nos, _ = cs.ler(sff)
    cores = rgb_da_paleta(pal)
    antes, depois, total = [], [], 0
    for n in nos:
        if n["g"] != grupo or n["link"] is not None or n.get("png") or (quadros and n["i"] not in quadros):
            continue
        novo, k = limpar(n["px"], n["w"], n["h"], cores)
        if k:
            antes.append(n["px"]); depois.append(novo)
            n["px"] = novo
            total += k
            print(f"{grupo},{n['i']}: {k} pixels de mancha repintados")
    # links para esses sprites apontam para os mesmos pixels: atualiza
    for n in nos:
        if n["link"] is not None and nos[n["link"]]["g"] == grupo:
            n["px"] = nos[n["link"]]["px"]
    if not total:
        print("nada a limpar")
        return
    if ver:
        ims = []
        for n in nos:
            if n["g"] == grupo and n["link"] is None and (not quadros or n["i"] in quadros):
                im = Image.frombytes("P", (n["w"], n["h"]), bytes(n["px"]))
                im.putpalette([int(c) for c in cores.flatten()])
                ims.append(im.convert("RGB"))
        W = sum(i.width for i in ims); H = max(i.height for i in ims)
        o = Image.new("RGB", (W, H), (60, 60, 120)); x = 0
        for i in ims:
            o.paste(i, (x, H - i.height)); x += i.width
        o.save(ver)
    if any(n.get("png") for n in nos):
        cs._gravar_misto(sff, pal, nos, cs.EXTRAS[str(sff)])
    else:
        import gerar_pengaro as gp
        gp.gravar_sff(sff, pal, [cs._item(n) for n in nos], cs.EXTRAS[str(sff)])
    print(f"{sff}: {total} pixels repintados")


if __name__ == "__main__":
    main()
