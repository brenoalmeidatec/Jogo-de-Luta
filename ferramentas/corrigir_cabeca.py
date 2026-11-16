#!/usr/bin/env python3
"""Conserta o tamanho da cabeça nos quadros que já estão no jogo, sem redesenhar o resto (pedido do Alisson, 16/11).

O boneco de peças montado do zero mudava o movimento e chapava a cor. Aqui o quadro original fica como está (mesma
pose, mesmo contorno, mesmas cores) e só a cabeça, que é o que varia de um desenho para o outro, volta para o tamanho
do parado de referência:

  1. a régua (ferramentas/pixel/reguas.py) acha a cabeça do parado no quadro e dá a escala dela (ex.: 110%);
  2. a cabeça é recortada acima da linha do queixo e encolhida em volta do queixo, com Scale2x três vezes e
     amostragem (não borra e não vira escada);
  3. o pescoço que ficava atrás da cabeça é puxado para cima (o mesmo que `pixel.py estica`), para não abrir
     buraco entre a cabeça e os ombros;
  4. a régua mede de novo.

  python ferramentas/corrigir_cabeca.py ENTRADA.png SAIDA.png [--escala 1.10]
  python ferramentas/corrigir_cabeca.py --pasta ENTRADA_DIR SAIDA_DIR
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI / "pixel"))
import reguas  # noqa: E402
from pixel import scale2x  # noqa: E402

RAIZ = AQUI.parent
REF = RAIZ / "sprites/pengaro/quadros_arcade_hd/ginga/00.png"
QUEIXO_REF = 392      # linha do queixo no parado de referência (ginga/00, 3x)
LIMITE = 0.03         # abaixo disso a cabeça fica como está
PESCOCO = 14          # quantas linhas acima do queixo o pescoço é puxado para tapar a folga


def abrir(c):
    return np.asarray(Image.open(c).convert("RGBA")).copy()


def referencia():
    r = abrir(REF)
    tmpl, caixa = reguas.cabeca_do_parado(r)
    return tmpl, caixa


def encolher(pedaco, f, pivo):
    """Encolhe o RGBA f vezes em volta do pivô (x, y): Scale2x x3 e amostra o centro de cada célula."""
    H, W = pedaco.shape[:2]
    big = scale2x(scale2x(scale2x(pedaco)))
    px, py = pivo
    ys, xs = np.mgrid[0:H, 0:W]
    sx = np.floor((px + (xs + 0.5 - px) / f) * 8).astype(int)
    sy = np.floor((py + (ys + 0.5 - py) / f) * 8).astype(int)
    ok = (sx >= 0) & (sy >= 0) & (sx < W * 8) & (sy < H * 8)
    out = np.zeros_like(pedaco)
    out[ok] = big[sy[ok], sx[ok]]
    return out


def corrigir(a, tmpl, caixa, escala=None):
    e, nota, (x, y) = reguas.escala_cabeca(a, tmpl)
    if escala is not None:
        e = escala
    info = {"escala_antes": e, "nota": nota}
    if abs(e - 1) <= LIMITE:
        info["mexeu"] = False
        return a, info
    x0r, y0r, x1r, _ = caixa
    # linha do queixo e centro do rosto neste quadro, pela posição e escala achadas
    queixo = int(round(y + (QUEIXO_REF - y0r) * e))
    cx = int(round(x + (x1r - x0r) * e / 2))
    larg = int((x1r - x0r) * e * 0.7) + 4
    xa, xb = max(0, cx - larg), min(a.shape[1], cx + larg)
    topo = max(0, y - 6)
    m = np.zeros(a.shape[:2], bool)
    m[topo:queixo, xa:xb] = a[topo:queixo, xa:xb, 3] > 0
    # só o que está ligado à cabeça achada: mão levantada perto do rosto fica de fora
    n, lab = cv2.connectedComponents(m.astype(np.uint8), connectivity=4)
    cab = lab[y:y + int((caixa[3] - y0r) * e), x:x + int((x1r - x0r) * e)]
    manter = [v for v in np.unique(cab) if v and (cab == v).sum() > 30]
    m = np.isin(lab, manter)
    cabeca = np.zeros_like(a)
    cabeca[m] = a[m]
    nova = encolher(cabeca, 1 / e, (cx, queixo))
    out = a.copy()
    # some a borda velha da cabeça; na faixa do queixo, a parte de trás (nuca, ombro, trapézio) fica como está e
    # só a frente do queixo velho sai, para não sobrar um queixo fantasma
    sob = nova[..., 3] > 0
    faixa = np.zeros_like(m)
    faixa[max(0, queixo - PESCOCO):queixo] = True
    tras = np.zeros_like(m)
    tras[:, :cx] = True
    apaga = m & ~(faixa & tras)
    out[apaga & ~sob] = 0
    out[sob] = nova[sob]
    info["mexeu"] = True
    info["queixo"] = queixo
    return out, info


def main():
    args = sys.argv[1:]
    tmpl, caixa = referencia()
    if args and args[0] == "--pasta":
        ent, sai = Path(args[1]), Path(args[2])
        sai.mkdir(parents=True, exist_ok=True)
        for f in sorted(ent.glob("*.png")):
            out, info = corrigir(abrir(f), tmpl, caixa)
            Image.fromarray(out).save(sai / f.name)
            e2 = reguas.escala_cabeca(out, tmpl)[0]
            print(f"{f.name}: cabeça {info['escala_antes']:.0%} -> {e2:.0%}")
        return
    esc = None
    if "--escala" in args:
        i = args.index("--escala")
        esc = float(args[i + 1])
        del args[i:i + 2]
    out, info = corrigir(abrir(args[0]), tmpl, caixa, esc)
    Image.fromarray(out).save(args[1])
    print(info, "->", reguas.escala_cabeca(out, tmpl)[0])


if __name__ == "__main__":
    main()
