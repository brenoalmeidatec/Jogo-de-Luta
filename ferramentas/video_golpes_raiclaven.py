#!/usr/bin/env python3
"""Vídeo antes e depois (hoje x boneco de peças) de ações do Raiclaven montadas pelo golpes_raiclaven.py, 60 fps.

  python ferramentas/video_golpes_raiclaven.py 215:martelo 410:cabeçada      grava docs/boneco-pecas/raiclaven/golpes.mp4
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
SPR = RAIZ / "sprites/raiclaven"
DOCS = RAIZ / "docs/boneco-pecas/raiclaven"
CORTE = (330, 130, 750, 680)


def quadro(arq):
    f = Image.open(arq).convert("RGBA")
    bg = Image.new("RGBA", f.size, (60, 60, 70, 255))
    bg.alpha_composite(f)
    return bg.crop(CORTE).convert("RGB")


def main():
    mapa = json.loads((DOCS / "mapa_acoes.json").read_text(encoding="utf-8"))
    fonte = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    w, h = CORTE[2] - CORTE[0], CORTE[3] - CORTE[1]
    tmp = DOCS / "_quadros"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir()
    guarda_a, guarda_n = SPR / "quadros_arcade_hd/ginga/00.png", SPR / "quadros_pecas_hd/guarda.png"
    k = 0
    for arg in sys.argv[1:]:
        num, nome = arg.split(":")
        hoje = []
        for e in mapa[num]:
            hoje += [SPR / "quadros_arcade_hd" / f"{e['desenho']}.png"] * max(e["ticks"], 1)
        pasta = SPR / "quadros_pecas_hd" / f"a{num}"
        t = json.loads((pasta / "tempos.json").read_text(encoding="utf-8"))
        novo = []
        for e in t["elementos"]:
            novo += [pasta / f"{e['desenho']:02d}.png"] * e["ticks"]
        n = max(len(hoje), len(novo))
        hoje += [hoje[-1]] * (n - len(hoje))
        novo += [novo[-1]] * (n - len(novo))
        hoje = [guarda_a] * 20 + hoje + [guarda_a] * 20
        novo = [guarda_n] * 20 + novo + [guarda_n] * 20
        cache = {}
        for volta in range(3):
            for a, b in zip(hoje, novo):
                if (a, b) not in cache:
                    img = Image.new("RGB", (w * 2, h + 34), (40, 40, 48))
                    img.paste(quadro(a), (0, 34))
                    img.paste(quadro(b), (w, 34))
                    d = ImageDraw.Draw(img)
                    d.text((8, 6), f"{nome}: hoje", fill=(255, 230, 120), font=fonte)
                    d.text((w + 8, 6), "boneco de peças", fill=(140, 255, 160), font=fonte)
                    cache[(a, b)] = img
                cache[(a, b)].save(tmp / f"{k:06d}.png")
                k += 1
    saida = DOCS / "golpes_lado_a_lado.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "60", "-i", str(tmp / "%06d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(saida)], check=True)
    shutil.rmtree(tmp)
    print(saida)


if __name__ == "__main__":
    main()
