"""Gera o ícone do atalho do jogo (assets/icone-jogo.ico) a partir do retrato do Pengaró.

Uso: python ferramentas/gerar_icone.py
Fundo de raios (roxo e laranja, as cores do Pengaró), rosto em pixel art e moldura preta arredondada.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
T = 256


def fundo():
    img = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, n = T * 0.55, T * 0.62, 18
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        cor = (255, 138, 28) if i % 2 == 0 else (212, 62, 20)
        pts = [(cx, cy)] + [(cx + 400 * math.cos(a), cy + 400 * math.sin(a)) for a in (a0, a1)]
        d.polygon(pts, fill=cor)
    # escurece as bordas para o rosto saltar
    sombra = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sombra)
    for r in range(0, 70):
        sd.rounded_rectangle((r, r, T - 1 - r, T - 1 - r), radius=max(8, 44 - r // 2),
                             outline=(40, 12, 70, int(150 * (1 - r / 70) ** 2)))
    img.alpha_composite(sombra)
    return img


def rosto():
    ret = Image.open(RAIZ / "sprites/pengaro-selecao-kof.png").convert("RGBA")
    ret = ret.crop(ret.getbbox())
    w, h = ret.size
    ret = ret.crop((int(w * 0.04), 0, int(w * 0.98), int(h * 0.92)))
    escala = 236 / ret.height
    ret = ret.resize((round(ret.width * escala), 236), Image.NEAREST)
    return ret


def montar():
    base = fundo()
    r = rosto()
    base.alpha_composite(r, (T - r.width + 14, T - r.height + 2))
    mascara = Image.new("L", (T, T), 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, T - 1, T - 1), radius=44, fill=255)
    saida = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    saida.paste(base, (0, 0), mascara)
    ImageDraw.Draw(saida).rounded_rectangle((2, 2, T - 3, T - 3), radius=42, outline=(10, 6, 14, 255), width=6)
    return saida


if __name__ == "__main__":
    icone = montar()
    destino = RAIZ / "assets/icone-jogo.ico"
    icone.save(destino, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    icone.save(destino.with_suffix(".png"))
    print("ok", destino, destino.stat().st_size, "bytes")
