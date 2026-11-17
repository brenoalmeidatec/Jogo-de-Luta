#!/usr/bin/env python3
"""Junta os 4 quartos (768x512) de uma imagem 1536x1024 do ChatGPT capturados com moldura verde de 4 px.

  python3 ferramentas/juntar_quartos.py SE.png SD.png IE.png ID.png SAIDA.png
  (superior esquerdo, superior direito, inferior esquerdo, inferior direito)
"""
import sys

import numpy as np
from PIL import Image


def interior(p):
    a = np.array(Image.open(p).convert("RGB")).astype(int)
    g = (a[..., 1] > 200) & (a[..., 0] < 80) & (a[..., 2] < 80)
    rows, cols = np.nonzero(g.mean(1) > 0.5)[0], np.nonzero(g.mean(0) > 0.5)[0]
    im = Image.fromarray(a.astype(np.uint8)).crop((cols.min(), rows.min(), cols.max() + 1, rows.max() + 1))
    w, h = im.size
    b = 4 * w / 776
    return im.crop((round(b), round(b), round(w - b), round(h - b))).resize((768, 512), Image.NEAREST)


F = Image.new("RGB", (1536, 1024))
for k, p in enumerate(sys.argv[1:5]):
    F.paste(interior(p), ((k % 2) * 768, (k // 2) * 512))
F.save(sys.argv[5])
