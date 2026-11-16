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

SPR = AQUI.parent / "sprites/pengaro"
ACAO = {"parado": 0, "soco": 200, "chute_alto": 240}
# elemento com Clsn1 (caixa de acerto) hoje, e a caixa
CAIXA = {"soco": (1, (45, -276, 153, -192)), "chute_alto": (2, (36, -300, 159, -174))}


def main():
    tmpl, caixa = cc.referencia()
    for nome, elems in ATUAL.items():
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            shutil.rmtree(SPR / pasta / nome, ignore_errors=True)
            (SPR / pasta / nome).mkdir(parents=True)
        unicos = list(dict.fromkeys(q for q, _ in elems))
        for i, q in enumerate(unicos):
            a = cc.abrir(SPR / "quadros_arcade_hd" / f"{q}.png")
            out, info = cc.corrigir(a, tmpl, caixa)
            Image.fromarray(out).save(SPR / "quadros_pecas_hd" / nome / f"{i:02d}.png")
            Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(SPR / "quadros_pecas" / nome / f"{i:02d}.png")
            print(f"{nome}/{i:02d} <- {q}: cabeça {info['escala_antes']:.0%}", "(corrigida)" if info["mexeu"] else "")
        bate, cx = CAIXA.get(nome, (None, None))
        tempos = {"acao": ACAO[nome], "caixa": cx, "origem": unicos,
                  "elementos": [{"desenho": unicos.index(q), "ticks": t, "caixa": k == bate}
                                for k, (q, t) in enumerate(elems)]}
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            (SPR / pasta / nome / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False),
                                                            encoding="utf-8")


if __name__ == "__main__":
    main()
