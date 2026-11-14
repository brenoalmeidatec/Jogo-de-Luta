#!/usr/bin/env python3
"""Amplia as folhas antigas do Pengaró num super-resolução (Real-ESRGAN), sem redesenhar: mesmas poses e cores.

  python ferramentas/ampliar_folhas.py MODELO.pth [folha ...]     (padrão: as folhas da forma normal)

Saída: sprites/pengaro/quadros/folhas_arcade_sr/<folha>.png, 2x a folha antiga (o boneco fica com ~550 px, como o
do CK na folha dele). O modelo roda em 4x e o resultado é reduzido para 2x (borda mais limpa que o 2x direto).
Precisa de torch e spandrel (pip install torch spandrel). Os pesos (RealESRGAN_x4plus_anime_6B.pth, licença BSD-3,
github.com/xinntao/Real-ESRGAN/releases) ficam fora do git. Depois rode ferramentas/nitidez_pengaro.py.
"""
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from spandrel import ModelLoader

RAIZ = Path(__file__).resolve().parent.parent
FOLHAS = RAIZ / "sprites/pengaro/quadros/folhas_arcade"
SAIDA = RAIZ / "sprites/pengaro/quadros/folhas_arcade_sr"


def ampliar(modelo, img, bloco=384, borda=16):
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255
    H, W = a.shape[:2]
    s = modelo.scale
    out = np.zeros((H * s, W * s, 3), np.float32)
    with torch.inference_mode():
        for y in range(0, H, bloco):
            for x in range(0, W, bloco):
                y0, x0 = max(0, y - borda), max(0, x - borda)
                y1, x1 = min(H, y + bloco + borda), min(W, x + bloco + borda)
                t = torch.from_numpy(a[y0:y1, x0:x1]).permute(2, 0, 1)[None]
                r = modelo(t)[0].permute(1, 2, 0).clamp(0, 1).numpy()
                yy, xx = (y - y0) * s, (x - x0) * s
                h, w = min(bloco, H - y) * s, min(bloco, W - x) * s
                out[y * s:y * s + h, x * s:x * s + w] = r[yy:yy + h, xx:xx + w]
    return Image.fromarray((out * 255 + .5).astype(np.uint8))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    torch.set_num_threads(max(1, torch.get_num_threads()))
    modelo = ModelLoader().load_from_file(sys.argv[1]).eval()
    nomes = sys.argv[2:] or sorted(p.stem for p in FOLHAS.glob("*.png") if not p.stem.startswith("e_"))
    SAIDA.mkdir(parents=True, exist_ok=True)
    for nome in nomes:
        img = Image.open(FOLHAS / f"{nome}.png")
        g = ampliar(modelo.model, img)
        g.resize((img.width * 2, img.height * 2), Image.LANCZOS).save(SAIDA / f"{nome}.png", optimize=True)
        print(nome, flush=True)
