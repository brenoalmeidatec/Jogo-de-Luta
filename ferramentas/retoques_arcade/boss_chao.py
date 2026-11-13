"""Move figuras de uma folha de 8 quadros sem redesenhar nada (fundo magenta ou verde, pela cor do canto).

Cada pedaço vai para a célula do centro dele (a regra do conversor). Dois usos:

    python ferramentas/retoques_arcade/boss_chao.py ENTRADA SAIDA --dy -60            (folha toda sobe 60 px)
    python ferramentas/retoques_arcade/boss_chao.py ENTRADA SAIDA --cel 7:-4,0 0:6,0  (só a célula 7 vai 4 px para a esquerda)

O deslocamento é por pixel inteiro (sem reamostrar). No fim confere: nada saiu da tela, nada encosta na borda, e
nenhuma figura passou a encostar na vizinha (máscaras dilatadas de 1 px não se tocam).
"""
import argparse

import cv2
import numpy as np
from PIL import Image


def fundo(a):
    r, g, b = (a[..., i].astype(int) for i in range(3))
    cr, cg, cb = (int(v) for v in a[3, 3])
    if cg > 170 and cr < 120 and cb < 120:
        return (g > 170) & (r < 120) & (b < 120), (cr, cg, cb)
    return (r > 150) & (b > 150) & (g < 110), (cr, cg, cb)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('entrada'); ap.add_argument('saida')
    ap.add_argument('--dy', type=int, default=0)
    ap.add_argument('--cel', nargs='*', default=[], help='k:dx,dy (célula 0-7)')
    o = ap.parse_args()
    im = Image.open(o.entrada).convert('RGB'); a = np.array(im); H, W = a.shape[:2]
    bg, cor = fundo(a); fg = ~bg
    n, lab, st, cen = cv2.connectedComponentsWithStats(fg.astype(np.uint8), connectivity=8)
    cel = np.array([-1] + [min(7, int(cen[i][0] // (W / 8))) for i in range(1, n)])
    desl = {k: (0, o.dy) for k in range(8)}
    for c in o.cel:
        k, v = c.split(':'); dx, dy = (int(x) for x in v.split(','))
        desl[int(k)] = (dx, dy + o.dy)
    out = np.empty_like(a); out[:] = cor
    masc = []
    for k in range(8):
        m = (cel[lab] == k) & fg
        ys, xs = np.nonzero(m); dx, dy = desl[k]
        ny, nx = ys + dy, xs + dx
        if (ny < 0).any() or (ny >= H).any() or (nx < 0).any() or (nx >= W).any():
            raise SystemExit(f'célula {k}: sai da tela com dx={dx} dy={dy}')
        out[ny, nx] = a[ys, xs]
        mm = np.zeros((H, W), np.uint8); mm[ny, nx] = 1; masc.append(mm)
    Image.fromarray(out).save(o.saida)
    k3 = np.ones((3, 3), np.uint8)
    for k in range(7):
        if (cv2.dilate(masc[k], k3) & masc[k + 1]).any():
            print(f'AVISO: células {k} e {k + 1} se encostam')
    tudo = np.any(masc, axis=0)
    borda = tudo[0].any() or tudo[-1].any() or tudo[:, 0].any() or tudo[:, -1].any()
    sola = [int(np.nonzero(m.any(1))[0].max()) for m in masc]
    print('borda', 'ENCOSTA' if borda else 'ok', 'sola', sola)


if __name__ == '__main__':
    main()
