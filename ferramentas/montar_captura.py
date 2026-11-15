#!/usr/bin/env python3
"""Junta as duas metades capturadas do ChatGPT (1086 px cada) numa folha 2172x724 e monta o antes/depois.

  python ferramentas/montar_captura.py ESQ.png DIR.png sprites/<l>/quadros/folhas_anatomia/<folha>.png [FOLHA_ANTIGA.png]
"""
import sys
from pathlib import Path
from PIL import Image

esq, dir_, saida = sys.argv[1:4]
a, b = Image.open(esq).convert("RGB"), Image.open(dir_).convert("RGB")
folha = Image.new("RGB", (2172, 724), (255, 0, 255))
folha.paste(a.resize((1086, 724), Image.NEAREST) if a.size != (1086, 724) else a, (0, 0))
folha.paste(b.resize((1086, 724), Image.NEAREST) if b.size != (1086, 724) else b, (1086, 0))
Path(saida).parent.mkdir(parents=True, exist_ok=True)
folha.save(saida)
if len(sys.argv) > 4:
    velha = Image.open(sys.argv[4]).convert("RGBA")
    fundo = Image.new("RGBA", velha.size, (255, 0, 255, 255))
    fundo.alpha_composite(velha)
    velha = fundo.convert("RGB").resize((2172, 724))
    par = Image.new("RGB", (2172, 724 * 2 + 8), (20, 20, 30))
    par.paste(velha, (0, 0))
    par.paste(folha, (0, 732))
    destino = Path(saida).with_name(Path(saida).stem + "_antes_depois.jpg")
    par.resize((1448, 971), Image.LANCZOS).save(destino, quality=88)
    print(destino)
print(saida)
