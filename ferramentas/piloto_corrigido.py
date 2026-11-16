#!/usr/bin/env python3
"""Piloto do boneco de peças, versão 2 (16/11): parte dos quadros que o jogo já mostra e só conserta a cabeça.

O Alisson gostou da régua do boneco de peças, mas não do resultado montado do zero: perdia nitidez (paleta de 15
cores), os membros se soltavam e o movimento mudava. Aqui:

  - os desenhos são exatamente os que o jogo mostra hoje em cada elemento (mesma ordem, mesmos ticks, mesma caixa);
  - a cabeça, que era o que passava da régua (107% a 112% no soco e no chute), volta ao tamanho do parado com
    ferramentas/corrigir_cabeca.py;
  - braços, pernas, tronco e cores ficam os pixels originais.

  python ferramentas/piloto_corrigido.py      grava quadros_pecas_hd/<animação>/NN.png (3x), quadros_pecas/ (1x)
                                              e tempos.json, no formato que o video_pecas.py lê
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import corrigir_cabeca as cc  # noqa: E402
from video_pecas import ATUAL  # noqa: E402

sys.path.insert(0, str(AQUI / "pixel"))
import cv2  # noqa: E402
import cores  # noqa: E402

# expressão de cada desenho (o rosto é sempre o mesmo; muda a expressão)
EXPRESSAO = {"ginga/03": "guarda", "ginga/07": "guarda", "ginga/01": "guarda", "ginga/06": "guarda",
             "ginga/02": "guarda", "soco/03": "foco", "soco/05": "esforco", "soco/06": "esforco",
             "soco/07": "foco", "chute_alto/01": "foco", "chute_alto/02": "foco", "chute_alto/04": "esforco",
             "chute_alto/05": "esforco", "chute_alto/06": "foco", "chute_alto/07": "guarda"}
N_CORES = 64  # paleta única do parado: pele, calça, faixa e garrafa saem sempre do mesmo tom


def paleta_do_parado(ref, extras):
    """64 cores do parado (k-means em Lab) + 16 para o que ele não tem (sola, dentes...)."""
    px = ref[..., :3][ref[..., 3] > 0]
    L = cores.lab(px)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 80, 0.1)
    cv2.setRNGSeed(0)
    _, _, cen = cv2.kmeans(L, N_CORES, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    lo = []
    for a in extras:
        Lq = cores.lab(a[..., :3][a[..., 3] > 0])
        d = np.sqrt(((Lq[:, None] - cen[None]) ** 2).sum(-1)).min(1)
        lo.append(Lq[d > cores.LONGE])
    lo = np.concatenate(lo)
    if len(lo) > 64:
        _, _, ce = cv2.kmeans(lo[::max(1, len(lo) // 20000)], 16, None, crit, 3, cv2.KMEANS_PP_CENTERS)
        cen = np.concatenate([cen, ce])
    return np.unique(cores.rgb_de_lab(cen.astype(np.float32)), axis=0)

SPR = AQUI.parent / "sprites/pengaro"
ACAO = {"parado": 0, "soco": 200, "chute_alto": 240}
# elemento com Clsn1 (caixa de acerto) hoje, e a caixa
CAIXA = {"soco": (1, (45, -276, 153, -192)), "chute_alto": (2, (36, -300, 159, -174))}


def main():
    tmpl, caixa = cc.referencia()
    kit = {n: cc.cabeca_do_kit(n, tmpl, caixa) for n in cc.EXPRESSOES}
    ref = cc.abrir(cc.REF)
    refcor = cores.RefCor([str(cc.REF)])
    todos = [q for el in ATUAL.values() for q, _ in el]
    pal = paleta_do_parado(ref, [cc.abrir(SPR / "quadros_arcade_hd" / f"{q}.png") for q in dict.fromkeys(todos)])
    for nome, elems in ATUAL.items():
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            shutil.rmtree(SPR / pasta / nome, ignore_errors=True)
            (SPR / pasta / nome).mkdir(parents=True)
        unicos = list(dict.fromkeys(q for q, _ in elems))
        for i, q in enumerate(unicos):
            a = cc.abrir(SPR / "quadros_arcade_hd" / f"{q}.png")
            out, info = cc.trocar(a, tmpl, caixa, kit[EXPRESSAO[q]])
            out = cores.pintar_na_paleta(refcor.corrigir(out), pal)
            Image.fromarray(out).save(SPR / "quadros_pecas_hd" / nome / f"{i:02d}.png")
            Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(SPR / "quadros_pecas" / nome / f"{i:02d}.png")
            print(f"{nome}/{i:02d} <- {q}: cabeça {info['escala_antes']:.0%} -> {EXPRESSAO[q]}, "
                  f"deriva de cor {refcor.medir(a)['deriva']:.1f} -> {refcor.medir(out)['deriva']:.1f}")
        bate, cx = CAIXA.get(nome, (None, None))
        tempos = {"acao": ACAO[nome], "caixa": cx, "origem": unicos,
                  "elementos": [{"desenho": unicos.index(q), "ticks": t, "caixa": k == bate}
                                for k, (q, t) in enumerate(elems)]}
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            (SPR / pasta / nome / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False),
                                                            encoding="utf-8")


if __name__ == "__main__":
    main()
