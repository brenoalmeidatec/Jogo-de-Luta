#!/usr/bin/env python3
"""Gera as animações de um lutador no Blender e converte em pixel art 224x128 (pés em 104,119), com GIFs de prévia.

  python ferramentas/blender/gerar.py pengaro                 todas as animações
  python ferramentas/blender/gerar.py pengaro soco chute      só essas
  python ferramentas/blender/gerar.py pengaro --oculos        versão Despertar (de óculos) em ginga_endiabrada

Precisa de: pip install bpy pillow numpy   (ou o Blender instalado: use --blender "C:/Program Files/Blender Foundation/Blender 4.2/blender.exe")
Saída: sprites/<lutador>/blender/<animacao>/NN.png, <animacao>.gif e <animacao>_folha.png
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(AQUI))
import animacoes  # noqa: E402
import pixelizar_quadros  # noqa: E402


def renderizar(pasta, personagem, nomes, oculos, blender):
    extra = ["--oculos"] if oculos else []
    if blender:
        cmd = [blender, "-b", "-P", str(AQUI / "renderizar.py"), "--", str(pasta), personagem, *nomes, *extra]
    else:
        cmd = [sys.executable, str(AQUI / "renderizar.py"), str(pasta), personagem, *nomes, *extra]
    subprocess.run(cmd, check=True)


def gif(quadros, destino, ticks):
    fundo = (62, 54, 78)
    imgs = []
    for q in quadros:
        base = Image.new("RGBA", q.size, (*fundo, 255))
        base.alpha_composite(q)
        imgs.append(base.resize((q.width * 3, q.height * 3), Image.NEAREST).convert("P", palette=Image.ADAPTIVE))
    imgs[0].save(destino, save_all=True, append_images=imgs[1:], duration=int(ticks * 1000 / 60), loop=0, disposal=2)


def folha(quadros, destino):
    w, h = quadros[0].size
    cols = min(8, len(quadros))
    lin = -(-len(quadros) // cols)
    f = Image.new("RGBA", (w * cols, h * lin), (62, 54, 78, 255))
    for i, q in enumerate(quadros):
        f.alpha_composite(q, ((i % cols) * w, (i // cols) * h))
    f.save(destino)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("personagem")
    ap.add_argument("animacoes", nargs="*")
    ap.add_argument("--oculos", action="store_true")
    ap.add_argument("--blender", help="caminho do blender.exe (se não usar o pacote bpy)")
    ap.add_argument("--cores", type=int, default=40)
    ap.add_argument("--saida")
    a = ap.parse_args()
    nomes = a.animacoes or list(animacoes.ANIMACOES)
    saida = Path(a.saida) if a.saida else RAIZ / "sprites" / a.personagem / "blender"
    with tempfile.TemporaryDirectory() as tmp:
        renderizar(Path(tmp), a.personagem, nomes, a.oculos, a.blender)
        pixelizar_quadros.processar(tmp, saida, cores=a.cores)
    for nome in nomes:
        quadros = [Image.open(f).convert("RGBA") for f in sorted((saida / nome).glob("*.png"))]
        ticks = animacoes.ANIMACOES[nome][3]
        gif(quadros, saida / f"{nome}.gif", ticks)
        folha(quadros, saida / f"{nome}_folha.png")
    print(f"pronto: {saida}")


if __name__ == "__main__":
    main()
