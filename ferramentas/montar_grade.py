#!/usr/bin/env python3
"""Junta as duas metades capturadas do ChatGPT (zoom do Chrome, 800x1040 com a metade 768x1024 no canto e preto em
volta) na folha 1536x1024 de sprites/hazaki/quadros/folhas_novas/<folha>.png.

  python ferramentas/montar_grade.py <folha> ESQ.png DIR.png
  python ferramentas/montar_grade.py <folha>            usa as duas capturas mais novas de tool-results (pelo número)
"""
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "sprites/hazaki/quadros/folhas_novas"
CAPTURAS = Path("/root/.claude/projects/-home-user/0466e52a-6077-5cdb-b129-abc9e71cd30e/tool-results")
MW, MH = 768, 1024


def metade(caminho):
    a = np.asarray(Image.open(caminho).convert("RGB"))
    assert a.shape[0] >= MH + 4 and a.shape[1] >= MW + 4, f"{caminho}: captura pequena {a.shape}"
    assert a[:MH, MW + 2:].max() < 40 and a[MH + 2:, :MW].max() < 40, f"{caminho}: a metade não está em 768x1024"
    assert a[:MH, MW - 1].max() > 100 and a[MH - 1, :MW].max() > 100, f"{caminho}: a metade veio menor"
    return a[:MH, :MW]


def main():
    nome = sys.argv[1]
    if len(sys.argv) >= 4:
        esq, dir_ = sys.argv[2], sys.argv[3]
    else:  # pelo número do blob: ls -t empata no mesmo segundo
        pngs = sorted(CAPTURAS.glob("mcp-claude-in-chrome-blob-*.png"),
                      key=lambda p: int(re.search(r"blob-(\d+)", p.name).group(1)))
        esq, dir_ = pngs[-2], pngs[-1]
    folha = np.concatenate([metade(esq), metade(dir_)], axis=1)
    DESTINO.mkdir(parents=True, exist_ok=True)
    Image.fromarray(folha).save(DESTINO / f"{nome}.png")
    print(f"{nome}: {folha.shape[1]}x{folha.shape[0]} de {Path(esq).name} + {Path(dir_).name}")


if __name__ == "__main__":
    main()
