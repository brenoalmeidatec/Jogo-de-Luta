#!/usr/bin/env python3
"""Recorta uma folha gerada (fundo magenta, quadros em fila) em quadros prontos para o jogo.

Cada quadro sai transparente, na altura do personagem e alinhado no chão.

  python ferramentas/recortar_quadros.py folha.png soco --quadros 8 --ancora pes
  python ferramentas/recortar_quadros.py folha.png anda --quadros 8 --ancora cabeca

Saída: sprites/pengaro/quadros/<nome>/00.png, 01.png...
A âncora "pes" mantém o pé de trás parado; "cabeca" centra o corpo, para quem troca os pés.
"""
import argparse
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
LARG, ALT = 224, 128
PIVO = (104, 119)  # onde os pés ficam em cada quadro, igual à folha das 9 poses
PE_DE_TRAS = 56  # coluna do pé de trás parado, para o corpo não escorregar entre os quadros


def tira_fundo(img):
    img = img.convert("RGBA")
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, _ = px[x, y]
            if r > 150 and b > 150 and g < 110 and abs(r - b) < 70:
                px[x, y] = (0, 0, 0, 0)
    return img


def fatias(img, n):
    """Acha os n quadros pelos vãos vazios entre as colunas."""
    alfa = img.getchannel("A")
    w, h = img.size
    ocupadas = [alfa.crop((x, 0, x + 1, h)).getbbox() is not None for x in range(w)]
    grupos = []
    inicio = None
    for x, cheio in enumerate(ocupadas + [False]):
        if cheio and inicio is None:
            inicio = x
        elif not cheio and inicio is not None:
            grupos.append((inicio, x))
            inicio = None
    grupos = [g for g in grupos if g[1] - g[0] > 20]  # tira sujeira solta
    if len(grupos) != n:
        raise SystemExit(f"achei {len(grupos)} quadros em vez de {n}; confira a folha")
    return [img.crop((a, 0, b, h)) for a, b in grupos]


def ponto_ancora(q, ancora):
    caixa = q.getchannel("A").getbbox()
    if ancora == "pes":
        faixa = q.crop((0, caixa[3] - 10, q.width, caixa[3]))
        return faixa.getchannel("A").getbbox()[0]
    faixa = q.crop((0, caixa[1], q.width, caixa[1] + (caixa[3] - caixa[1]) // 4))
    a = faixa.getchannel("A").getbbox()
    return (a[0] + a[2]) // 2


def main():
    p = argparse.ArgumentParser()
    p.add_argument("folha")
    p.add_argument("nome")
    p.add_argument("--quadros", type=int, default=8)
    p.add_argument("--ancora", choices=("pes", "cabeca"), default="pes")
    p.add_argument("--escala", type=float, default=0.40, help="fator de redução; use o mesmo em todas as folhas")
    a = p.parse_args()

    quadros = fatias(tira_fundo(Image.open(a.folha)), a.quadros)
    escala = a.escala
    saida = RAIZ / "sprites/pengaro/quadros" / a.nome
    saida.mkdir(parents=True, exist_ok=True)

    for i, q in enumerate(quadros):
        c = q.getchannel("A").getbbox()
        q = q.crop(c)
        ancora = ponto_ancora(q, a.ancora)
        pequeno = q.resize((round(q.width * escala), round(q.height * escala)), Image.LANCZOS)
        pequeno.putalpha(pequeno.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
        x = round(ancora * escala)
        tela = Image.new("RGBA", (LARG, ALT))
        referencia = PE_DE_TRAS if a.ancora == "pes" else PIVO[0]
        tela.alpha_composite(pequeno, (max(0, referencia - x), max(0, PIVO[1] - pequeno.height)))
        tela.save(saida / f"{i:02d}.png")
    print(f"{a.nome}: {len(quadros)} quadros, escala {escala:.3f}")


if __name__ == "__main__":
    main()
