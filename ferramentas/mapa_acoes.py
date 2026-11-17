#!/usr/bin/env python3
"""Qual desenho de sprites/<l>/quadros/<pasta>/NN.png cada elemento de cada ação do .air mostra hoje.

  python ferramentas/mapa_acoes.py raiclaven [pasta ...]    grava docs/boneco-pecas/<l>/mapa_acoes.json

Compara a máscara de cada sprite do .sff (3x, reduzida para 1x com os pés em 180,220) com as máscaras dos quadros de
1x das pastas. Serve para saber, sem abrir o jogo, quais ações usam os desenhos de um golpe e com que ticks.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conferir_sff as cs  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent


def main():
    lut = sys.argv[1]
    pastas = sys.argv[2:]
    q = RAIZ / "sprites" / lut / "quadros"
    pastas = pastas or sorted(p.name for p in q.iterdir() if p.is_dir() and not p.name.startswith("folha"))
    ref = {}
    for p in pastas:
        for f in sorted((q / p).glob("[0-9][0-9].png")):
            m = np.asarray(Image.open(f).convert("RGBA"))[..., 3] > 0
            ref[f"{p}/{f.stem}"] = m
    _, nos, _ = cs.ler(RAIZ / "chars" / lut / f"{lut}.sff")
    spr = {}
    for n in nos:
        if (n["g"], n["i"]) in spr or n.get("png"):
            continue
        spr[(n["g"], n["i"])] = n
    air = (RAIZ / "chars" / lut / f"{lut}.air").read_text(encoding="latin-1")
    cache = {}

    def melhor(g, i):
        if (g, i) in cache:
            return cache[(g, i)]
        n = spr.get((g, i))
        if not n:
            return None
        px = np.frombuffer(n["px"], np.uint8).reshape(n["h"], n["w"]) > 0
        tela = np.zeros((780, 1080), bool)
        x0, y0 = 540 - n["x"], 660 - n["y"]
        ys, xs = slice(max(0, y0), min(780, y0 + n["h"])), slice(max(0, x0), min(1080, x0 + n["w"]))
        tela[ys, xs] = px[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]
        m1 = tela[1::3, 1::3][:260, :360]
        best = (0, None)
        for k, m in ref.items():
            iou = (m & m1).sum() / max(1, (m | m1).sum())
            if iou > best[0]:
                best = (iou, k)
        cache[(g, i)] = (round(float(best[0]), 3), best[1])
        return cache[(g, i)]

    out = {}
    for m in re.finditer(r"^\[Begin Action (\d+)\][^\n]*\n(.*?)(?=^\[Begin Action|\Z)", air, re.M | re.S):
        num = int(m.group(1))
        if num >= 5000 and num not in range(1000, 4000):
            pass
        els = []
        caixa = False
        for linha in m.group(2).splitlines():
            s = linha.strip()
            if re.match(r"(?i)clsn1:", s):
                caixa = True
                continue
            mm = re.match(r"^(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)", s)
            if mm:
                g, i, t = int(mm.group(1)), int(mm.group(2)), int(mm.group(5))
                b = melhor(g, i) if g >= 0 else None
                els.append({"sprite": [g, i], "ticks": t, "caixa": caixa, "desenho": b[1] if b else None,
                            "iou": b[0] if b else 0})
                caixa = False
        if any(e["desenho"] and e["iou"] > 0.6 for e in els):
            out[num] = els
    destino = RAIZ / "docs" / "boneco-pecas" / lut / "mapa_acoes.json"
    destino.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    for num, els in out.items():
        nomes = sorted({e["desenho"].split("/")[0] for e in els if e["desenho"] and e["iou"] > 0.6})
        print(num, sum(max(e["ticks"], 0) for e in els), "ticks", nomes)


if __name__ == "__main__":
    main()
