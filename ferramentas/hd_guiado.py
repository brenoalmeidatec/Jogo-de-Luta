#!/usr/bin/env python3
"""Recria em 3x (quadros_arcade_hd/) os quadros arcade que já estão no jogo, guiado pelo próprio quadro de 1x.

  python ferramentas/hd_guiado.py <lutador> [folha ...]      (padrão: todas as pastas de quadros_arcade)

Para cada quadros_arcade/<folha>/NN.png (tela 360x260, até 15 cores):
  1. acha, na folha original (quadros/folhas_arcade/<folha>.png, em alta resolução), a figura que deu aquele quadro e a
     escala e a posição em que ela foi colada (comparando a silhueta reduzida com a do quadro, em várias escalas);
  2. cola essa figura 3x maior na tela 3x (1080x780);
  3. pinta cada pixel 3x com a cor mais próxima ENTRE AS CORES DO QUADRO DE 1x na vizinhança 3x3 do ponto
     correspondente. Assim o 3x herda tudo o que os conversores e os retoques fizeram no 1x (paleta de cada forma, cabelo
     repintado, faísca apagada, pixel solto limpo), só que com o detalhe da folha original.
Quadro que não casa com nenhuma figura da folha (montado à mão ou por código) fica sem gêmeo: o gerador só o amplia.
Serve para qualquer lutador cujos quadros arcade vieram das folhas (é o que ferramentas/hd.py procura).
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "ferramentas"))
from recortar_quadros import tira_fundo  # noqa: E402

E = 3


def figuras(folha):
    """As figuras da folha (RGBA recortadas), uma por célula: o maior pedaço de cada célula e os pedaços pequenos que
    caem nela. Folha com fundo em degradê vira magenta puro antes."""
    a = np.array(folha.convert("RGB"))
    r, g, b = (a[..., i].astype(int) for i in range(3))
    a[(r > 170) & (b > 170) & (g < 130) & (np.abs(r - b) < 60)] = (255, 0, 255)
    limpa = np.array(tira_fundo(Image.fromarray(a)))
    largura = limpa.shape[1] / 8
    n, rot, info, cen = cv2.connectedComponentsWithStats((limpa[..., 3] > 0).astype(np.uint8), connectivity=8)
    cel = np.full(n, -1)
    for j in range(1, n):
        if info[j, cv2.CC_STAT_AREA] >= 12:
            cel[j] = min(7, int(cen[j][0] // largura))
    out = []
    for c in range(8):
        m = cel[rot] == c
        if not m.any():
            continue
        ys, xs = np.nonzero(m)
        out.append(np.where(m[..., None], limpa, 0)[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8))
    return out


def registrar(alvo, fig):
    """Melhor (iou, escala, x, y) colando `fig` reduzida em `alvo` (máscaras booleanas)."""
    ys, xs = np.nonzero(alvo)
    if not len(xs):
        return None
    h1 = ys.max() - ys.min() + 1
    f0 = h1 / fig.shape[0]
    fa = (fig[..., 3] >= 128).astype(np.float32)
    A = alvo.astype(np.float32)
    melhor = None
    for f in f0 * np.linspace(0.85, 1.18, 34):
        w, h = max(1, round(fig.shape[1] * f)), max(1, round(fig.shape[0] * f))
        if w >= A.shape[1] or h >= A.shape[0]:
            continue
        t = cv2.resize(fa, (w, h), interpolation=cv2.INTER_AREA) >= .5
        res = cv2.matchTemplate(A, t.astype(np.float32), cv2.TM_CCORR)
        _, _, _, (x, y) = cv2.minMaxLoc(res)
        recorte = alvo[y:y + h, x:x + w]
        inter = (recorte & t).sum()
        iou = inter / (alvo.sum() + t.sum() - inter)
        if melhor is None or iou > melhor[0]:
            melhor = (iou, f, x, y)
    return melhor


def guiado(alta, q1):
    """Pinta `alta` (RGBA 3x) só com as cores de `q1` (RGBA 1x quantizado) na vizinhança 3x3 de cada ponto."""
    H, W = alta.shape[:2]
    a1 = q1.astype(int)
    pad = np.pad(a1, ((1, 1), (1, 1), (0, 0)))
    rgb = alta[..., :3].astype(int)
    melhor = np.full((H, W), 10 ** 9)
    cor = np.zeros((H, W, 3), int)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            viz = pad[1 + dy:1 + dy + a1.shape[0], 1 + dx:1 + dx + a1.shape[1]]
            viz = np.repeat(np.repeat(viz, E, axis=0), E, axis=1)[:H, :W]
            peso = 0 if (dx, dy) == (0, 0) else 1500  # empate: fica a cor do próprio ponto
            d = ((rgb - viz[..., :3]) ** 2).sum(axis=2) + peso
            d = np.where(viz[..., 3] >= 128, d, 10 ** 9)
            troca = d < melhor
            melhor = np.where(troca, d, melhor)
            cor[troca] = viz[..., :3][troca]
    opaco = (alta[..., 3] >= 128) & (melhor < 10 ** 9)
    out = np.zeros((H, W, 4), np.uint8)
    out[opaco, :3] = cor[opaco]
    out[opaco, 3] = 255
    return out


def converter(lutador, nomes=None):
    base = RAIZ / "sprites" / lutador
    q1d, hdd, fol = base / "quadros_arcade", base / "quadros_arcade_hd", base / "quadros/folhas_arcade"
    nomes = nomes or sorted(p.name for p in q1d.iterdir() if p.is_dir())
    for nome in nomes:
        arq = fol / f"{nome}.png"
        if not arq.exists():
            print(f"{nome}: sem folha original, fica sem HD")
            continue
        figs = figuras(Image.open(arq))
        destino = hdd / nome
        destino.mkdir(parents=True, exist_ok=True)
        notas = []
        for q in sorted((q1d / nome).glob("*.png")):
            q1 = np.asarray(Image.open(q).convert("RGBA"))
            alvo = q1[..., 3] >= 128
            i = int(q.stem) if q.stem.isdigit() else -1
            ordem = ([i] if 0 <= i < len(figs) else []) + [k for k in range(len(figs)) if k != i]
            melhor = None
            for k in ordem:
                r = registrar(alvo, figs[k])
                if r and (melhor is None or r[0] > melhor[0][0]):
                    melhor = (r, k)
                if melhor and melhor[0][0] >= .9:
                    break
            if not melhor or melhor[0][0] < .8:
                notas.append(f"{q.stem}:sem")
                (destino / q.name).unlink(missing_ok=True)
                continue
            (iou, f, x, y), k = melhor
            fig = Image.fromarray(figs[k])
            g = fig.resize((max(1, round(fig.width * f * E)), max(1, round(fig.height * f * E))), Image.LANCZOS)
            tela = Image.new("RGBA", (q1.shape[1] * E, q1.shape[0] * E))
            tela.paste(g, (x * E, y * E), g)
            Image.fromarray(guiado(np.asarray(tela), q1)).save(destino / q.name)
            notas.append(f"{q.stem}:{iou:.2f}")
        print(f"{nome}: {' '.join(notas)}", flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    converter(sys.argv[1], sys.argv[2:] or None)
