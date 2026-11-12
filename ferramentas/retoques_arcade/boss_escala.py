"""Corrige a escala de uma folha de 8 quadros que veio maior ou menor que a parada do lutador, sem gerar de novo.

Separa as 8 figuras com a regra do conversor (cada pedaço vai para a célula do centro dele), aumenta ou diminui cada
uma pelo fator dela e devolve à mesma célula: o centro da figura mantém a distância (escalada) ao centro da célula, e a
sola mantém a distância (escalada) ao chão da folha (mediana das solas). A tela pode mudar de tamanho (--tela) e o
chão pode ir para outra altura (--sola).

    python ferramentas/retoques_arcade/boss_escala.py ENTRADA SAIDA 1.107
    python ferramentas/retoques_arcade/boss_escala.py ENTRADA SAIDA 0.938,0.931,...   (8 fatores, um por quadro)
    python ferramentas/retoques_arcade/boss_escala.py ENTRADA SAIDA 0.961 --tela 2172x724 --sola 563

No fim mede a altura de cada figura e confere que nenhuma encosta na vizinha nem na borda.
"""
import sys

import cv2
import numpy as np
from PIL import Image


def mascara(a):
    """Pixels de figura. O fundo é o da cor do canto: magenta (corpo) OU verde (aura). Só um dos dois, porque há
    figura com verde vivo (cabelo e tanques do Raiclaven, garrafa do CK) em folha de fundo magenta."""
    r, g, b = (a[..., i].astype(int) for i in range(3))
    cr, cg, cb = (int(v) for v in a[3, 3])
    if cg > 170 and cr < 120 and cb < 120:
        return ~((g > 170) & (r < 120) & (b < 120))
    return ~((r > 170) & (g < 100) & (b > 170))


def figuras(a):
    """[(máscara da figura k, caixa x0, y0, x1, y1)] para k = 0..7, com a regra do conversor."""
    H, W = a.shape[:2]
    L = W / 8
    fg = mascara(a)
    n, lab, st, cen = cv2.connectedComponentsWithStats(fg.astype(np.uint8), connectivity=8)
    cel = np.full(n, -1)
    for i in range(1, n):
        if st[i, 4] >= 12:
            cel[i] = min(7, int(cen[i][0] // L))
    saida = []
    for k in range(8):
        m = cel[lab] == k
        m &= fg
        ys, xs = np.nonzero(m)
        saida.append((m, (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)) if len(xs) else (None, None))
    return saida


def confere(a, rotulo):
    H, W = a.shape[:2]
    figs = figuras(a)
    alturas = [c[3] - c[1] if c else 0 for _, c in figs]
    solas = [c[3] for _, c in figs if c]
    n, _, st, cen = cv2.connectedComponentsWithStats(mascara(a).astype(np.uint8), connectivity=8)
    gr = [0] * 8
    for i in range(1, n):
        if st[i, 4] >= 12:
            k = min(7, int(cen[i][0] // (W / 8)))
            gr[k] = max(gr[k], int(st[i, 4]))
    fg = mascara(a)
    borda = {"cima": int(fg[:2].sum()), "baixo": int(fg[-2:].sum()), "esq": int(fg[:, :2].sum()), "dir": int(fg[:, -2:].sum())}
    colado = min(gr) < .25 * max(gr)
    print(f"  {rotulo}: {W}x{H}, alturas {alturas}, solas {min(solas)}-{max(solas)}, borda {borda}, "
          f"{'COLADO' if colado else 'um pedaço grande por célula'}")


def main(args):
    ent, sai, fat = args[0], args[1], args[2]
    resto = args[3:]
    fatores = [float(v) for v in fat.split(",")]
    fatores = fatores * 8 if len(fatores) == 1 else fatores
    a = np.array(Image.open(ent).convert("RGB"))
    H, W = a.shape[:2]
    fundo = tuple(int(v) for v in a[3, 3])
    tela = (W, H)
    sola_nova = None
    if "--tela" in resto:
        tela = tuple(int(v) for v in resto[resto.index("--tela") + 1].split("x"))
    if "--sola" in resto:
        sola_nova = int(resto[resto.index("--sola") + 1])
    print(ent)
    confere(a, "antes")
    figs = figuras(a)
    sola = float(np.median([c[3] for _, c in figs if c]))
    sola_nova = sola if sola_nova is None else sola_nova
    nova = Image.new("RGBA", tela, fundo + (255,))
    for k, ((m, c), f) in enumerate(zip(figs, fatores)):
        if m is None:
            continue
        x0, y0, x1, y1 = c
        rgba = np.dstack([a[y0:y1, x0:x1], (m[y0:y1, x0:x1] * 255).astype(np.uint8)])
        q = Image.fromarray(rgba, "RGBA").convert("RGBa")
        q = q.resize((max(1, round((x1 - x0) * f)), max(1, round((y1 - y0) * f))), Image.LANCZOS).convert("RGBA")
        cx = (k + .5) * tela[0] / 8 + ((x0 + x1) / 2 - (k + .5) * W / 8) * f
        base = sola_nova + (y1 - sola) * f
        px, py = round(cx - q.width / 2), round(base - q.height)
        if px < 0 or py < 0:  # alpha_composite não aceita destino negativo: corta o que sairia da tela
            q = q.crop((max(0, -px), max(0, -py), q.width, q.height))
            print(f"  quadro {k + 1}: {max(0, -px)} px cortados na esquerda, {max(0, -py)} em cima")
            px, py = max(0, px), max(0, py)
        nova.alpha_composite(q, (px, py))
    b = np.array(nova.convert("RGB"))
    confere(b, "depois")
    Image.fromarray(b).save(sai)


if __name__ == "__main__":
    main(sys.argv[1:])
