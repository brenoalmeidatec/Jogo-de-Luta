#!/usr/bin/env python3
"""Extrai o pacote baixado do ChatGPT na pasta de folhas do lutador, limpando as faixas de cima e de baixo.

  python ferramentas/baixar_folhas.py pengaro
"""
import sys
import tarfile
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent


def limpa_faixas(dados):
    a = np.array(Image.open(BytesIO(dados)).convert("RGB"))
    magenta = (a[..., 0] > 150) & (a[..., 2] > 150) & (a[..., 1] < 110)
    linhas = np.where(magenta.mean(axis=1) > 0.2)[0]
    a[:linhas[0] + 4] = (255, 0, 255)
    a[linhas[-1] - 4:] = (255, 0, 255)
    return Image.fromarray(a)


def main():
    pasta = RAIZ / "sprites" / sys.argv[1] / "quadros/folhas"
    pasta.mkdir(parents=True, exist_ok=True)
    downloads = Path.home() / "Downloads"
    candidatos = [*downloads.glob("*.tmp"), *downloads.glob("folhas*.tar")]
    pacote = max(candidatos, key=lambda f: f.stat().st_mtime)
    with tarfile.open(pacote) as t:
        membros = t.getmembers()
        for m in membros:
            if not m.isfile() or "/" in m.name or not m.name.endswith(".png"):
                raise SystemExit(f"arquivo inesperado no pacote: {m.name}")
            limpa_faixas(t.extractfile(m).read()).save(pasta / m.name)
    print(f"{len(membros)} folhas em {pasta}")


if __name__ == "__main__":
    main()
