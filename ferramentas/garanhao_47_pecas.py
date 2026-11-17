#!/usr/bin/env python3
"""Garanhão dos golpes da #47 (kit_garanhao_47): o mesmo montador do garanhao_pecas.py (repinta o que o braço de perto
esconde, perna de trás = perna da frente girada), saindo em sprites/garanhao_47.

  python ferramentas/importar_garanhao.py && python ferramentas/garanhao_47_pecas.py [anims]

As pastas-guia levanta/ e estouro/ (golpes sem folha) são o parado repetido; a pose vem toda à mão do kit.
"""
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import firme  # noqa: E402
import garanhao_pecas  # noqa: E402

RAIZ = AQUI.parent
HD = RAIZ / "sprites" / "garanhao" / "quadros_arcade_hd"


def guias():
    link = RAIZ / "sprites" / "garanhao_47" / "quadros_arcade_hd"
    link.parent.mkdir(parents=True, exist_ok=True)
    if not link.exists():
        link.symlink_to(Path("..") / "garanhao" / "quadros_arcade_hd")
    for nome in ("levanta", "estouro"):
        (HD / nome).mkdir(exist_ok=True)
        for i in range(8):
            shutil.copy(HD / "rasga_couro" / "00.png", HD / nome / f"{i:02d}.png")


def main():
    guias()
    sys.argv = [sys.argv[0], "garanhao_47"] + sys.argv[1:]
    firme.montar_kit = garanhao_pecas.montar_kit_garanhao(firme.montar_kit)
    firme.main()


if __name__ == "__main__":
    main()
