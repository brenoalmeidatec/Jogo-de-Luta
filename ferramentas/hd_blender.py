#!/usr/bin/env python3
"""Gera sprites/<lutador>/quadros_hd/: os quadros de quadros/ (chaves e quadros do meio do Blender) em 3x.

  python ferramentas/hd_blender.py gutto        (ou raiclaven; ~20 min, 4 folhas por vez)

É o animar_folha.py com HD=3: a mesma renderização 4x do Blender, reduzida para 3x em vez de 1x; quadros/ não muda.
Pula a folha que já tem quadros_hd completo. Depois rode o gerador do lutador: o ferramentas/hd.py troca cada sprite
pelo gêmeo 3x. quadros_hd fica fora do git (.gitignore) por ser grande; o .sff pronto em chars/ vai no git.
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

lutador = sys.argv[1]
os.environ["LUTADOR"], os.environ["HD"] = lutador, "3"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import animar_folha as af  # noqa: E402

q = af.QUADROS
pastas = [p.name for p in sorted(q.iterdir()) if p.is_dir() and p.name not in ("folhas", "folhas_arcade")]


def um(nome):
    n1 = len(list((q / nome).rglob("*.png")))
    hd = q.parent / "quadros_hd" / nome
    if hd.exists() and len(list(hd.rglob("*.png"))) == n1:
        return f"{nome}: já feito"
    try:
        af.animar(nome)
        return f"{nome}: ok {len(list(hd.rglob('*.png')))}/{n1}"
    except Exception as e:  # pasta que não é folha animada: fica sem HD (o gerador só amplia)
        return f"{nome}: sem HD ({type(e).__name__}: {e})"


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    with ThreadPoolExecutor(4) as t:
        for r in t.map(um, pastas):
            print(r, flush=True)
