#!/usr/bin/env python3
"""Ginga (parado) do Hazak pelo desenho original (Breno, #32, 24/11: "o ginga dele entorta a perna de um jeito muito
feio"). Regra do desenho original (passo 5 da docs/regra-de-criacao-de-personagem.md):

- a pose de cada desenho-chave é a do quadro original (quadros_arcade_hd/parado/00..06): pernas, cintura e braços
  como foram desenhados, nada dobrado por malha;
- a cabeça é sempre a do kit (sprites/hazaki/pecas/cabeca.png, rosto do parado), assentada onde a cabeça do
  desenho está, para a cara não mudar de um quadro para o outro;
- quadros do meio da guarda: as pernas ficam as do desenho-chave e só o tronco (com a cabeça) anda um terço e dois
  terços do caminho até o tronco do desenho seguinte. O cinto do quadro de baixo fica por baixo do tronco, então o
  corpo não abre vão na cintura.

    python3 ferramentas/hazak_do_original.py          (refaz quadros_pecas_hd/parado e quadros_pecas/parado)

Os tempos (tempos.json) ficam os de antes. Depois: python3 ferramentas/ligar_pecas.py hazaki parado
"""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
SPR = RAIZ / "sprites/hazaki"
ORIG = SPR / "quadros_arcade_hd"
HD, UM = SPR / "quadros_pecas_hd", SPR / "quadros_pecas"
REF = "parado/00"
TRONCO = (470, 380, 640, 469)   # caixa do tronco no parado/00 (ombros até o alto da faixa)
CINTURA = 469                    # alto da faixa no parado/00
SOBRA_CINTO = 10                 # o pedaço de baixo leva 10 px acima da faixa (fica por baixo do tronco)
CABECA_POLI = [(524, 346), (540, 332), (566, 332), (584, 346), (584, 384), (570, 394), (562, 400), (540, 400),
               (528, 380)]       # kit_hazak.CABECA


def abrir(q):
    return np.array(Image.open(ORIG / f"{q}.png").convert("RGBA"))


def casar(alvo, molde, x0, y0, folga=40):
    """(dx, dy) do molde (recortado em x0,y0 do parado) dentro do alvo."""
    m = (molde[..., 3] > 0).astype(np.float32)
    h, w = molde.shape[:2]
    X0, Y0 = max(0, x0 - folga), max(0, y0 - folga)
    reg = alvo[Y0:y0 + h + folga, X0:x0 + w + folga, :3].astype(np.float32)
    res = cv2.matchTemplate(reg, molde[..., :3].astype(np.float32), cv2.TM_SQDIFF,
                            mask=np.repeat(m[..., None], 3, -1))
    _, _, p, _ = cv2.minMaxLoc(res)
    return p[0] + X0 - x0, p[1] + Y0 - y0


def colar(tela, img, x, y):
    h, w = img.shape[:2]
    a = img[..., 3] > 0
    tela[y:y + h, x:x + w][a] = img[a]


def cabeca_kit():
    k = json.loads((SPR / "pecas/kit.json").read_text(encoding="utf-8"))["pecas"]["cabeca"]
    return np.array(Image.open(SPR / "pecas" / k["arquivo"]).convert("RGBA")), tuple(k["origem"])


def mascara_cabeca(forma, dx, dy, folga=5):
    im = Image.new("L", forma, 0)
    ImageDraw.Draw(im).polygon([(x + dx, y + dy) for x, y in CABECA_POLI], fill=255)
    m = np.array(im) > 0
    return cv2.dilate(m.astype(np.uint8), np.ones((2 * folga + 1, 2 * folga + 1), np.uint8)) > 0


def tapar_furinhos(a, maximo=40):
    """Furinho fechado de 1 a 40 px dentro da figura (erro do desenho da IA) é pintado com a cor em volta."""
    fundo = (a[..., 3] == 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(fundo, connectivity=4)
    borda = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    m = np.isin(lab, [i for i in range(1, n) if st[i, 4] <= maximo and i not in borda])
    if m.any():
        rgb = cv2.inpaint(np.ascontiguousarray(a[..., :3]), m.astype(np.uint8), 3, cv2.INPAINT_TELEA)
        a[m, :3], a[m, 3] = rgb[m], 255
    return a


class Chave:
    """Um desenho-chave: o original, onde está o tronco e onde está a cabeça."""

    def __init__(self, q, ref, cab, cab_xy):
        self.a = abrir(q)
        x0, y0, x1, y1 = TRONCO
        self.t = casar(self.a, ref[y0:y1, x0:x1], x0, y0)          # tronco em relação ao parado/00
        hx, hy = cab_xy
        self.c = casar(self.a, cab, hx, hy, folga=25)                # cabeça do desenho em relação à do kit
        self.cint = CINTURA + self.t[1]
        # sem a cabeça do desenho (o kit põe a dele) e só a parte de cima (tronco e braços)
        sem = self.a.copy()
        m = mascara_cabeca(sem.shape[1::-1], *self.c)
        m[self.cint + 30:] = False   # nada abaixo do pescoço sai
        pesc = 398 + self.c[1]       # queixo/pescoço: abaixo disso só sai o que é da cabeça (cabelo)
        m[pesc - 4:] = False
        sem[m] = 0
        self.sem = sem

    def montar(self, frac, prox, cab, cab_xy):
        """Pernas desta chave; tronco (e cabeça) andando `frac` do caminho até o tronco da chave `prox`."""
        h, w = self.a.shape[:2]
        tela = np.zeros_like(self.a)
        corte = self.cint - SOBRA_CINTO
        tela[self.cint:] = self.a[self.cint:]  # pernas e faixa do desenho
        # a sobra acima da faixa (fica por baixo do tronco) só na largura da cintura: braço e punho não vão junto
        xs = np.nonzero(self.a[self.cint + 6, :, 3] > 0)[0]
        x0, x1 = xs.min() + 6, xs.max() - 6
        tela[corte:self.cint, x0:x1] = self.a[corte:self.cint, x0:x1]
        ddx = int(round(frac * (prox.t[0] - self.t[0]))) if prox else 0
        ddy = int(round(frac * (prox.t[1] - self.t[1]))) if prox else 0
        cima = np.zeros_like(self.a)
        cima[:self.cint + 3] = self.sem[:self.cint + 3]
        cima = np.roll(np.roll(cima, ddy, 0), ddx, 1)
        a = cima[..., 3] > 0
        tela[a] = cima[a]
        hx, hy = cab_xy
        colar(tela, cab, hx + self.c[0] + ddx, hy + self.c[1] + ddy)
        return tapar_furinhos(tela)


def main():
    cab, cab_xy = cabeca_kit()
    ref = abrir(REF)
    arq = HD / "parado/tempos.json"
    t = json.loads(arq.read_text(encoding="utf-8"))
    chaves = {q: Chave(q, ref, cab, cab_xy) for q in t["origem"]}
    ordem = list(t["origem"])
    els = t["elementos"]
    for q in ordem:
        print(q, "tronco", chaves[q].t, "cabeça", chaves[q].c)
    k = 0
    while k < len(els):
        q = els[k]["de"]
        grupo = [e for e in els if e["de"] == q]
        prox = chaves[ordem[(ordem.index(q) + 1) % len(ordem)]]
        for j, e in enumerate(grupo):
            img = chaves[q].montar(j / len(grupo), prox, cab, cab_xy)
            Image.fromarray(img).save(HD / "parado" / f"{e['desenho']:02d}.png")
            Image.fromarray(np.ascontiguousarray(img[1::3, 1::3])).save(UM / "parado" / f"{e['desenho']:02d}.png")
        k += len(grupo)
    print("parado:", len(els), "desenhos de", len(ordem), "desenhos originais")


if __name__ == "__main__":
    main()
