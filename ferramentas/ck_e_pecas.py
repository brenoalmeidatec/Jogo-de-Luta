#!/usr/bin/env python3
"""CK despertado (Modo Ratão) no corpo firme: o firme.py com o kit_ck_e, mais a barriga que o antebraço de perto
esconde no parado.

  python ferramentas/importar_ck_e.py      (uma vez: quadros 3x do despertado em sprites/ck_e)
  python ferramentas/ck_e_pecas.py [anims] [--so-pose] [--video]

Nenhum outro desenho do despertado tem o corpo na mesma pose com a barriga à vista (o ChatGPT muda a camisa de um
quadro para outro), então a barriga é continuada do próprio parado: cada coluna escondida repete, em espelho, o pano
que aparece logo acima do antebraço (a camisa aberta à esquerda, a regata branca no meio), e a barra da camisa ganha
o contorno escuro do desenho. Mesmo pano, mesmas cores, sem borrão.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import firme  # noqa: E402

CONTORNO = (34, 18, 48)


def montar_kit_ck_e(original):
    def montar():
        original()
        b = firme.b
        kit = b.ler_kit()
        p = kit["pecas"]["tronco"]
        ox, oy = p["origem"]
        img = np.asarray(Image.open(b.PECAS / p["arquivo"]).convert("RGBA"))
        h, w = img.shape[:2]
        tela = np.zeros((b.TELA[1], b.TELA[0], 4), np.uint8)
        tela[oy:oy + h, ox:ox + w] = img
        pm = np.asarray(Image.open(b.PECAS / "tronco_pintado.png"))
        pint = np.zeros(b.TELA[::-1], bool)
        pint[oy:oy + pm.shape[0], ox:ox + pm.shape[1]] = pm[..., 3] > 0
        visto = (tela[..., 3] > 0) & ~pint
        hsv = cv2.cvtColor(np.ascontiguousarray(tela[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
        pele = (hsv[..., 0] <= 25) & (hsv[..., 1] > 80) & (hsv[..., 2] > 90)
        ys, xs = np.nonzero(pint)
        sem_fonte = np.zeros_like(pint)
        for x in range(xs.min(), xs.max() + 1):
            col = np.nonzero(pint[:, x])[0]
            if not len(col):
                continue
            topo = col.min()
            # só a faixa de pano logo acima do antebraço (abaixo do logo do peito) e nunca pele (pescoço, mão)
            cima = [y for y in range(topo - 1, topo - 14, -1) if visto[y, x] and not pele[y, x]]
            if len(cima) < 3:
                sem_fonte[col, x] = True
                continue
            for y in col:
                d = y - topo
                ciclo = len(cima)
                k = d % (2 * ciclo)
                fonte = cima[k] if k < ciclo else cima[2 * ciclo - 1 - k]
                tela[y, x] = tela[fonte, x]
        # o lado do corpo debaixo da manga não tem pano à vista em cima: fica na sombra da manga, no tom escuro da
        # própria camisa (o lado do corpo na sombra do braço, como um desenhista faria), com um risco de luz na dobra
        roxo = visto & (hsv[..., 0] >= 120) & (hsv[..., 0] <= 160) & (hsv[..., 1] > 60)
        lum = tela[roxo][:, :3].astype(int).sum(-1)
        cor = tela[roxo][:, :3][(lum >= np.percentile(lum, 20)) & (lum <= np.percentile(lum, 40))]
        sombra = np.median(cor, 0).astype(np.uint8)
        dobra = np.median(tela[roxo][:, :3][(lum >= np.percentile(lum, 60)) & (lum <= np.percentile(lum, 75))], 0)
        tela[sem_fonte, :3] = sombra
        yy, xx = np.mgrid[:b.TELA[1], :b.TELA[0]]
        risco = sem_fonte & ((np.abs((xx - 497) - (yy - 430) * 0.15) < 1.0) & (yy > 432) & (yy < 470) |
                             (np.abs((xx - 503) - (yy - 410) * 0.3) < 1.0) & (yy > 408) & (yy < 438))
        tela[risco, :3] = dobra.astype(np.uint8)
        # a barra da camisa: contorno escuro na linha de baixo do que foi continuado
        al = (tela[..., 3] > 0).astype(np.uint8)
        borda = (al > 0) & (cv2.erode(al, np.ones((3, 3), np.uint8)) == 0) & pint
        tela[borda, :3] = CONTORNO
        Image.fromarray(tela[oy:oy + h, ox:ox + w]).save(b.PECAS / p["arquivo"])
        Image.fromarray(np.zeros_like(pm)).save(b.PECAS / "tronco_pintado.png")
        # o cigarro é uma linha de 1 px na diagonal: ao girar a cabeça ela partia e a brasa ficava solta no ar.
        # engrossa a linha para 2 px (o pixel de baixo, com a mesma cor)
        c = kit["pecas"]["cabeca"]
        cx, cy = c["origem"]
        cab = np.asarray(Image.open(b.PECAS / c["arquivo"]).convert("RGBA")).copy()
        ch, cw = cab.shape[:2]
        nova = cab.copy()
        for y in range(380 - cy, 390 - cy):
            for x in range(580 - cx, 592 - cx):
                if 0 <= y < ch - 1 and 0 <= x < cw and cab[y, x, 3] and cab[y + 1, x, 3] == 0 and \
                        int(cab[y, x, :3].sum()) < 200:
                    nova[y + 1, x] = cab[y, x]
        Image.fromarray(nova).save(b.PECAS / c["arquivo"])
        # o quadril não tem desenho próprio (o short é das pernas): sobrava só a fresta escura entre as coxas, que
        # ficava solta no ar quando a perna da frente dá o passo
        q = kit["pecas"]["quadril"]
        qi = np.asarray(Image.open(b.PECAS / q["arquivo"]).convert("RGBA")).copy()
        qi[min(14, qi.shape[0] - 1):] = 0
        Image.fromarray(qi).save(b.PECAS / q["arquivo"])
        print(f"barriga continuada do próprio parado: {int(pint.sum())} px")
    return montar


def main():
    sys.argv = [sys.argv[0], "ck_e"] + sys.argv[1:]
    firme.montar_kit = montar_kit_ck_e(firme.montar_kit)
    firme.main()


if __name__ == "__main__":
    main()
