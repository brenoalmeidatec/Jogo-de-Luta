#!/usr/bin/env python3
"""Régua do boneco de peças: mede cada quadro contra o parado do kit e reprova o que mudou de tamanho.

  python ferramentas/conferir_pecas.py PASTA [PASTA ...]         (pastas de quadros 3x, 1080x780, pés em 540,660)
  opções: --ref sprites/pengaro/quadros_arcade_hd/ginga/00.png   --contato 02 (quadro em que o membro que bate pode
          crescer até 15%, regra 10)   --relatorio ARQ.md

Mede, em cada quadro:
  cabeça   escala da cabeça do parado achada no quadro (ferramentas/pixel/reguas.py): limite 5%
  tronco   escala do peito (do ombro à cintura, sem os braços) achada do mesmo jeito: limite 5%
  ossos    no boneco de peças, o comprimento de cada osso vem do kit.json; a régua confere a cabeça e o tronco medidos
           na imagem, que é o que o jogador vê (serve também para quadro desenhado fora do kit)
  altura   altura da figura contra o parado: só aviso (agachar e pular mudam de propósito)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent / "pixel"))
import reguas  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
LIMITE = 0.05
TRONCO = (512, 395, 575, 465)  # peito e barriga no parado do kit (ginga/00), sem os braços


def abrir(c):
    return np.asarray(Image.open(c).convert("RGBA"))


def medir(a, cab, tro):
    m = a[..., 3] > 0
    ys, xs = np.nonzero(m)
    e_cab, n_cab, _ = reguas.escala_cabeca(a, cab)
    e_tro, n_tro, _ = reguas.escala_cabeca(a, tro)
    return {"cabeca": e_cab, "nota_cabeca": n_cab, "tronco": e_tro, "nota_tronco": n_tro,
            "altura": int(ys.max() - ys.min() + 1), "largura": int(xs.max() - xs.min() + 1)}


def main():
    args = sys.argv[1:]

    def opcao(nome, padrao):
        if nome in args:
            i = args.index(nome)
            v = args[i + 1]
            del args[i:i + 2]
            return v
        return padrao

    ref = Path(opcao("--ref", str(RAIZ / "sprites/pengaro/quadros_arcade_hd/ginga/00.png")))
    relatorio = opcao("--relatorio", "")
    r = abrir(ref)
    cab, _ = reguas.cabeca_do_parado(r)
    x0, y0, x1, y1 = TRONCO
    tro = r[y0:y1, x0:x1]
    alt_ref = medir(r, cab, tro)["altura"]
    linhas = ["| quadro | cabeça | tronco | altura | resultado |", "|---|---|---|---|---|"]
    falhas = 0
    for pasta in args:
        for f in sorted(Path(pasta).glob("[0-9][0-9].png")):
            m = medir(abrir(f), cab, tro)
            ruim = [n for n in ("cabeca", "tronco") if abs(m[n] - 1) > LIMITE]
            falhas += bool(ruim)
            linhas.append(f"| {Path(pasta).name}/{f.name} | {m['cabeca']:.0%} | {m['tronco']:.0%} | "
                          f"{m['altura'] / alt_ref:.0%} | {'FAIL ' + ', '.join(ruim) if ruim else 'PASS'} |")
    texto = "\n".join(linhas) + f"\n\n{falhas} quadro(s) reprovado(s); limite {LIMITE:.0%} na cabeça e no tronco.\n"
    print(texto)
    if relatorio:
        Path(relatorio).write_text(texto, encoding="utf-8")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
