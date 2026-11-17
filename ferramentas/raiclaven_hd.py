#!/usr/bin/env python3
"""Desenhos-chave do Raiclaven em 3x (1080x780, pés em 540,660), para o boneco de peças.

Cada pasta sai da mesma folha que o jogo usa hoje (as 8 do ARCADE do gerar_raiclaven.py vêm de folhas_arcade, o resto
de folhas), com o mesmo recorte do animar_folha.poses, só que 3 vezes maior (a folha tem resolução de sobra).

  python ferramentas/raiclaven_hd.py ginga soco chute_alto      grava sprites/raiclaven/quadros_arcade_hd/<pasta>/NN.png
"""
import os
import sys
from pathlib import Path

os.environ["LUTADOR"] = "raiclaven"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import animar_folha as af  # noqa: E402
import gerar_raiclaven as gr  # noqa: E402

Q = gr.QUADROS
HD = Q.parent / "quadros_arcade_hd"


def gerar(nome):
    arcade = nome in gr.ARCADE
    folha = Q / ("folhas_arcade" if arcade else "folhas") / f"{nome}.png"
    destino = HD / nome
    destino.mkdir(parents=True, exist_ok=True)
    for i, pose in enumerate(af.poses(folha, "pes", 3)):
        pose.putalpha(pose.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
        pose = af.sem_magenta(pose, 15 * 9)
        if arcade:
            pose = gr.calca_das_folhas_antigas(pose)
        pose.save(destino / f"{i:02d}.png")
    print(f"{nome}: 8 desenhos 3x de {folha.parent.name}")


if __name__ == "__main__":
    for nome in sys.argv[1:]:
        gerar(nome)
