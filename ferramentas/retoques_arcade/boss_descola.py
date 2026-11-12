"""Descola figuras que se encostam numa folha de 8 quadros (fundo magenta ou verde), sem gerar de novo.

O conversor põe cada pedaço na célula do centro dele; duas figuras encostadas viram um pedaço só e deixam uma célula
vazia. Dois modos:

  gargalo A-B   acha o ponto onde as figuras das células A e B (0 a 7) se tocam e corta ali: núcleos por erosão
                progressiva, cada pixel da mancha vai para o núcleo mais perto POR DENTRO da figura (crescimento
                geodésico), e a fronteira entre os dois lados vira fundo. O pé, a ponta do rabo etc. ficam com o dono.
  linha:A-B     corte reto na linha entre as células, apagando as pontas pequenas que ficam do lado errado. Para
                aura rendada (leque de lâminas), em que o gargalo não funciona: a erosão desmancha a renda.
  corrente      para corrente que sai de um quadro e entra no seguinte: corta a corrente na linha da célula e apaga o
                pedaço que passou para a célula vizinha, seguindo o trilho da corrente coluna a coluna até ela entrar no
                corpo do vizinho. O último quadro também perde a ponta que encostava na borda direita.

    python ferramentas/retoques_arcade/boss_descola.py ENTRADA SAIDA [--tela LxA] 2-3 4-5 ...
    python ferramentas/retoques_arcade/boss_descola.py ENTRADA SAIDA corrente
    python ferramentas/retoques_arcade/boss_descola.py ENTRADA SAIDA linha:2-3 ...   (corte reto, para aura rendada)

--tela completa (ou apara) a tela na direita/embaixo até o tamanho pedido, com a cor do fundo, depois dos cortes.
No fim confere com a mesma regra do conversor (maior pedaço por célula; colado se algum < 25% do maior).
"""
import sys

import cv2
import numpy as np
from PIL import Image

K3 = np.ones((3, 3), np.uint8)


def mascara(a):
    r, g, b = (a[..., i].astype(int) for i in range(3))
    return ~(((r > 170) & (g < 100) & (b > 170)) | ((g > 170) & (r < 120) & (b < 120)))


def gargalo(a, A, B, fundo):
    H, W = a.shape[:2]
    L = W / 8
    fg = mascara(a).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
    ids = [i for i in range(1, n) if st[i, 4] > 5000 and st[i, 0] < (A + 1) * L and st[i, 0] + st[i, 2] > B * L]
    for i in ids:
        m = (lab == i).astype(np.uint8)
        for k in range(1, 60):
            e = cv2.erode(m, np.ones((2 * k + 1, 2 * k + 1), np.uint8))
            n2, l2, s2, c2 = cv2.connectedComponentsWithStats(e, connectivity=8)
            # núcleos de cada lado: os pedaços erodidos com o centro na célula e longe da linha entre as duas (ponta de
            # vizinho que passou da linha fica perto dela e não vira núcleo)
            linha = B * L
            ja = [j for j in range(1, n2) if s2[j, 4] > 300 and int(c2[j][0] // L) == A and linha - c2[j][0] > 40]
            jb = [j for j in range(1, n2) if s2[j, 4] > 300 and int(c2[j][0] // L) == B and c2[j][0] - linha > 40]
            if ja and jb:
                break
        else:
            continue
        g = np.zeros((H, W), np.uint8)
        g[np.isin(l2, ja)] = 1
        g[np.isin(l2, jb)] = 2
        while True:
            livre = (m > 0) & (g == 0)
            d1 = cv2.dilate((g == 1).astype(np.uint8), K3) > 0
            d2 = cv2.dilate((g == 2).astype(np.uint8), K3) > 0
            n1, n2_, amb = livre & d1 & ~d2, livre & d2 & ~d1, livre & d1 & d2
            if not (n1.any() or n2_.any() or amb.any()):
                break
            g[n1], g[n2_], g[amb] = 1, 2, 3
        lado1 = (g == 1) & (cv2.dilate(((g == 2) | (g == 3)).astype(np.uint8), K3) > 0)
        lado2 = (g == 2) & (cv2.dilate(((g == 1) | (g == 3)).astype(np.uint8), K3) > 0)
        corte = (cv2.dilate((lado1 | lado2 | (g == 3)).astype(np.uint8), K3) > 0) & (m > 0)
        ys, xs = np.nonzero(corte)
        print(f"  {A}-{B}: núcleos na erosão {k}; corte em x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()} ({len(xs)} px)")
        a[corte] = fundo
        return
    print(f"  {A}-{B}: nada colado")


def linha(a, A, B, fundo, faixa=1, ponta_max=1500):
    """Corte reto na linha entre as células A e B; as pontas que ficaram do lado errado (pedaço pequeno e estreito
    encostado no corte) são apagadas, para não irem parar no quadro vizinho."""
    W = a.shape[1]
    x = round(B * W / 8)
    a[:, x - faixa:x + faixa + 1][mascara(a[:, x - faixa:x + faixa + 1])] = fundo
    n, lab, st, _ = cv2.connectedComponentsWithStats(mascara(a).astype(np.uint8), connectivity=8)
    apagadas = 0
    for i in range(1, n):
        x0, w, ar = st[i, 0], st[i, 2], st[i, 4]
        encosta = x0 <= x + faixa + 2 and x0 + w >= x - faixa - 2
        if encosta and ar < ponta_max and w < 50:
            a[lab == i] = fundo
            apagadas += 1
    print(f"  {A}-{B}: corte reto em x={x}; {apagadas} pontas do lado errado apagadas")


def trechos(col):
    ys = np.flatnonzero(col)
    if not len(ys):
        return []
    q = np.flatnonzero(np.diff(ys) > 1)
    return list(zip(np.r_[ys[0], ys[q + 1]], np.r_[ys[q], ys[-1]]))


def corrente(a, fundo, folga=3, alt_max=16):
    H, W = a.shape[:2]
    L = W / 8
    rastro = np.zeros((H, W), np.uint8)
    for k in range(1, 9):
        x = min(W - 1, round(k * L))
        fg = mascara(a)
        so = [t for t in trechos(fg[:, x]) if t[1] - t[0] <= alt_max]
        if len(so) != 1:
            print(f"  linha {k}: {len(so)} trechos finos na coluna {x}, pulei")
            continue
        y0, y1 = so[0]
        apagados = 0
        # da linha para a direita: segue o trilho até ele engrossar (entrou no corpo do vizinho) ou acabar
        ini = x - folga if k < 8 else W - 1 - 2 * folga  # na borda direita a ponta perde uns pixels a mais
        xx, fim = ini, (x + 120 if k < 8 else W)
        while xx < fim:
            cand = [t for t in trechos(fg[:, xx]) if t[0] <= y1 + 1 and t[1] >= y0 - 1]
            if len(cand) != 1 or cand[0][1] - cand[0][0] > alt_max:
                break
            y0, y1 = cand[0]
            a[y0:y1 + 1, xx] = fundo
            rastro[y0:y1 + 1, xx] = 1
            apagados += y1 - y0 + 1
            xx += 1
        print(f"  linha {k} (x={x}): corrente apagada de x={ini} até {xx - 1} ({apagados} px)")
    # a franja rosada (mistura do cinza da corrente com o magenta) que sobrou em volta do trilho apagado
    r, g, b = (a[..., i].astype(int) for i in range(3))
    rosa = (r > 120) & (b > 110) & (g < 0.62 * np.minimum(r, b))
    perto = cv2.dilate(rastro, np.ones((5, 5), np.uint8)) > 0
    a[perto & rosa] = fundo


def confere(a):
    W = a.shape[1]
    L = W / 8
    n, _, st, cen = cv2.connectedComponentsWithStats(mascara(a).astype(np.uint8), connectivity=8)
    gr = [0] * 8
    for i in range(1, n):
        if st[i, 4] >= 12:
            k = min(7, int(cen[i][0] // L))
            gr[k] = max(gr[k], int(st[i, 4]))
    print("  maior pedaço por célula:", gr, "COLADO" if min(gr) < .25 * max(gr) else "ok")


def main(args):
    ent, sai, resto = args[0], args[1], args[2:]
    a = np.array(Image.open(ent).convert("RGB"))
    fundo = a[3, 3].copy()
    tela = None
    if "--tela" in resto:
        i = resto.index("--tela")
        tela = tuple(int(v) for v in resto[i + 1].split("x"))
        resto = resto[:i] + resto[i + 2:]
    print(ent)
    for r in resto:
        if r == "corrente":
            corrente(a, fundo)
        elif r.startswith("linha:"):
            A, B = map(int, r[6:].split("-"))
            linha(a, A, B, fundo)
        else:
            A, B = map(int, r.split("-"))
            gargalo(a, A, B, fundo)
    if tela:
        nova = np.empty((tela[1], tela[0], 3), np.uint8)
        nova[:] = fundo
        h, w = min(tela[1], a.shape[0]), min(tela[0], a.shape[1])
        nova[:h, :w] = a[:h, :w]
        a = nova
    confere(a)
    Image.fromarray(a).save(sai)


if __name__ == "__main__":
    main(sys.argv[1:])
