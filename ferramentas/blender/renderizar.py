"""Passo do Blender: monta o rig, posa cada quadro e salva o render grande (896x512, fundo transparente).

Rodar direto não é preciso; use gerar.py. Argumentos (depois de --): saida personagem anim [anim ...] [--oculos]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import animacoes  # noqa: E402
import cena  # noqa: E402
import rig  # noqa: E402

LUTADORES = {"pengaro": rig.PENGARO}


def main(argv):
    oculos = "--oculos" in argv
    argv = [a for a in argv if a != "--oculos"]
    saida, personagem, nomes = Path(argv[0]), argv[1], argv[2:] or list(animacoes.ANIMACOES)
    lutador = rig.Lutador(LUTADORES[personagem], oculos=oculos)
    cena.montar()
    for nome in nomes:
        n = animacoes.ANIMACOES[nome][0]
        pasta = saida / nome
        pasta.mkdir(parents=True, exist_ok=True)
        for i in range(n):
            lutador.posar(animacoes.pose(nome, i))
            cena.renderizar(pasta / f"{i:02d}.png")
        print(f"{nome}: {n} quadros", flush=True)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    main(args)
