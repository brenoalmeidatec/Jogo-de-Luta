#!/usr/bin/env python3
"""CK despertado (Modo Ratão) para o boneco de peças: copia os quadros 3x e_* do CK para
sprites/ck_e/quadros_arcade_hd/<nome sem e_>/ (fora do git), para o firme.py tratar o despertado como um lutador à
parte (kit próprio em sprites/ck_e/pecas, sem tocar no kit do CK base).

Golpes novos sem desenho de hoje (agarrão Paredão na Cara, poder Paredão no Talo) ganham uma pasta com o parado
repetido: o firme.py precisa de um quadro-guia, mas a pose vem toda à mão do kit_ck_e.POSES.

  python ferramentas/importar_ck_e.py
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIG = RAIZ / "sprites" / "ck" / "quadros_arcade_hd"
DEST = RAIZ / "sprites" / "ck_e" / "quadros_arcade_hd"
NOVOS = {"paredao": 8, "talo": 8}


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
            shutil.copy(ORIG / "e_referencia_ginga" / "00.png", alvo / f"{i:02d}.png")
    for f in ("paleta_arcade_ratao.json", "paleta_arcade.json"):
        if (RAIZ / "sprites/ck" / f).exists():
            shutil.copy(RAIZ / "sprites/ck" / f, DEST.parent / f)
    print("ok", len(list(DEST.iterdir())), "pastas")


if __name__ == "__main__":
    sys.exit(main())
