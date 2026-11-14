#!/usr/bin/env python3
"""Troca os retratos (grupo 9000) de um lutador por PNG colorido de 32 bits, sem mexer em mais nada do .sff.

  python ferramentas/trocar_retratos.py pengaro [ck ...]       (sem nome: todos os que têm retrato novo)

Lê sprites/retratos/<lutador>_rosto.png (9000,0: o quadradinho da grade e do HUD) e <lutador>_busto.png (9000,1: o
retrato grande da seleção) e grava no chars/<lutador>/<lutador>.sff. O corpo continua em RLE8 na paleta do lutador; os
retratos vão para o bloco tdata (o último do arquivo) como PNG RGBA (formato 12), fora da paleta, com cor cheia.
Rode depois do gerar_<lutador>.py, que regrava o .sff com os retratos antigos.
"""
import struct
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from layout_sff import png_rgba  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
RETRATOS = RAIZ / "sprites" / "retratos"
NO = "<HHHHhhHBBIIHH"


def trocar(lutador):
    sff = RAIZ / "chars" / lutador / f"{lutador}.sff"
    novos = {}
    for n, nome in ((0, "rosto"), (1, "busto")):
        arq = RETRATOS / f"{lutador}_{nome}.png"
        if arq.exists():
            novos[n] = Image.open(arq).convert("RGBA")
    if not novos:
        return False
    b = bytearray(sff.read_bytes())
    so, ns, _po, _np, _lo, _ll, to, tl = struct.unpack_from("<IIIIIIII", b, 0x24)
    if to + tl != len(b):
        raise SystemExit(f"{sff}: o tdata não é o fim do arquivo; não sei acrescentar com segurança")
    for i in range(ns):
        g, n, w, h, ax, ay, lk, fmt, dp, ofs, ln, pal, fl = struct.unpack_from(NO, b, so + i * 28)
        if g != 9000 or n not in novos:
            continue
        img = novos.pop(n)
        blob = struct.pack("<I", img.width * img.height * 4) + png_rgba(img.width, img.height, img.tobytes())
        if fmt == 12 and fl == 1 and bytes(b[to + ofs:to + ofs + ln]) == blob:
            continue   # já é este retrato: rodar de novo não acrescenta outra cópia
        struct.pack_into(NO, b, so + i * 28, g, n, img.width, img.height, 0, 0, 0, 12, 32, tl, len(blob), 0, 1)
        b += blob
        tl += len(blob)
    if novos:
        raise SystemExit(f"{sff}: faltou o sprite 9000,{sorted(novos)} para trocar")
    struct.pack_into("<I", b, 0x24 + 28, tl)
    sff.write_bytes(bytes(b))
    print(f"{lutador}: retratos trocados ({sff.stat().st_size} bytes)")
    return True


def main():
    nomes = sys.argv[1:] or sorted({p.stem.rsplit("_", 1)[0] for p in RETRATOS.glob("*_*.png")})
    for n in nomes:
        trocar(n)


if __name__ == "__main__":
    main()
