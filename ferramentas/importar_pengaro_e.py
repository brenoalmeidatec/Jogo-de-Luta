#!/usr/bin/env python3
"""Pengaró despertado (Endiabrado) para o boneco de peças: copia os quadros 3x e_* do Pengaró para
sprites/pengaro_e/quadros_arcade_hd/<nome sem e_>/ (fora do git), para o firme.py tratar o despertado como um lutador
à parte (kit próprio em sprites/pengaro_e/pecas, sem tocar no kit do Pengaró base).

Golpes novos que não têm desenho de hoje (agarrão Algema das Sombras, poder Maré das Correntes...) ganham uma pasta
com o parado repetido: o firme.py precisa de um quadro-guia, mas a pose vem toda à mão do kit_pengaro_e.POSES.

  python ferramentas/importar_pengaro_e.py
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIG = RAIZ / "sprites" / "pengaro" / "quadros_arcade_hd"
DEST = RAIZ / "sprites" / "pengaro_e" / "quadros_arcade_hd"
NOVOS = {"algema": 8, "mare": 8}


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    for d in sorted(ORIG.glob("e_*")):
        alvo = DEST / d.name[2:]
        shutil.rmtree(alvo, ignore_errors=True)
        shutil.copytree(d, alvo)
    for nome, n in NOVOS.items():
        alvo = DEST / nome
        alvo.mkdir(exist_ok=True)
        for i in range(n):
            shutil.copy(ORIG / "e_ginga" / "00.png", alvo / f"{i:02d}.png")
    for f in ("paleta_arcade_endiabrado.json", "paleta_arcade.json"):
        if (RAIZ / "sprites/pengaro" / f).exists():
            shutil.copy(RAIZ / "sprites/pengaro" / f, DEST.parent / f)
    print("ok", len(list(DEST.iterdir())), "pastas")


if __name__ == "__main__":
    sys.exit(main())
