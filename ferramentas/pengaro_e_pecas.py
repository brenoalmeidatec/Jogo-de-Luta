#!/usr/bin/env python3
"""Pengaró despertado no corpo firme: o firme.py com o kit_pengaro_e, mais o lado do peito que o braço de longe
esconde no parado (o ombro, a beira do colete e o peito embaixo do cotovelo).

  python ferramentas/importar_pengaro_e.py      (uma vez: quadros 3x do despertado em sprites/pengaro_e)
  python ferramentas/pengaro_e_pecas.py [anims] [--so-pose] [--video]

Quando o braço sai da frente (agarra, ergue, empurra a maré) aparecia a beira do tronco recortada. Aqui esse pedaço
vem do e_agarrao/01, em que o braço está esticado e o peito aparece inteiro, levado ao corpo do kit (corpo firme: o
desenho do peito é o mesmo; só a área que o braço tapava é preenchida).
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

DOADOR = "agarrao/01"
# por baixo do braço de longe no parado: ombro, beira do colete e peito até a faixa
ESCONDIDO = [(576, 380), (606, 380), (630, 400), (636, 430), (628, 462), (586, 462), (578, 420)]


def montar_kit_pengaro_e(original):
    def montar():
        original()
        b = firme.b
        kit = b.ler_kit()
        dx, dy, giro = firme.corpo(kit, firme.normal(DOADOR))
        d = firme.normal(DOADOR)
        if giro:
            jt = firme.K.OSSOS["tronco"][0]
            r, piv = b.rotsprite(d, -giro, jt)
            d = np.zeros_like(d)
            b.colar(d, r, int(round(jt[0] - piv[0])), int(round(jt[1] - piv[1])))
        d = cv2.warpAffine(d, np.float32([[1, 0, -dx], [0, 1, -dy]]), b.TELA, flags=cv2.INTER_NEAREST)
        # o braço do doador não entra (só corpo): tira o polígono do braço esticado dele, levado junto
        braco = firme.K.VARIANTES["braco_frente"]["aberta"][1]
        sem_braco = ~cv2.warpAffine(b.mascara(braco).astype(np.uint8), np.float32([[1, 0, -dx], [0, 1, -dy]]),
                                    b.TELA, flags=cv2.INTER_NEAREST).astype(bool)
        p = kit["pecas"]["tronco"]
        ox, oy = p["origem"]
        img = np.asarray(Image.open(b.PECAS / p["arquivo"]).convert("RGBA"))
        h, w = img.shape[:2]
        tela = np.zeros((b.TELA[1], b.TELA[0], 4), np.uint8)
        tela[oy:oy + h, ox:ox + w] = img
        ref = firme.abrir(firme.K.REF)
        bf = b.mascara(firme.K.BRACO_FRENTE) & (ref[..., 3] > 0)
        alvo = b.mascara(ESCONDIDO) & bf & (d[..., 3] > 0) & sem_braco & (np.mgrid[:b.TELA[1], :b.TELA[0]][0] < firme.K.CINTURA)
        tela[alvo] = d[alvo]
        # tira as tiras finas do colete que ficavam penduradas do lado do peito (sem o braço na frente elas pareciam
        # pedaço solto): o que some numa abertura de 7 px, à direita do peito e acima da faixa
        a = (tela[..., 3] > 0).astype(np.uint8)
        grosso = cv2.dilate(cv2.erode(a, np.ones((7, 7), np.uint8)), np.ones((9, 9), np.uint8)) > 0
        yy, xx = np.mgrid[:b.TELA[1], :b.TELA[0]]
        fino = (a > 0) & ~grosso & (xx > 598) & (yy > 405)
        tela[fino] = 0
        # e o que ficou solto do peito (lasca do doador separada do corpo)
        n, lab, st, _ = cv2.connectedComponentsWithStats((tela[..., 3] > 0).astype(np.uint8), connectivity=8)
        maior = 1 + int(np.argmax(st[1:, 4]))
        tela[(lab > 0) & (lab != maior)] = 0
        ys, xs = np.nonzero(tela[..., 3] > 0)
        X0, Y0 = xs.min(), ys.min()
        Image.fromarray(tela[Y0:ys.max() + 1, X0:xs.max() + 1]).save(b.PECAS / p["arquivo"])
        raw = json.loads((b.PECAS / "kit.json").read_text(encoding="utf-8"))
        raw["pecas"]["tronco"]["origem"] = [int(X0), int(Y0)]
        (b.PECAS / "kit.json").write_text(json.dumps(raw, indent=1, ensure_ascii=False), encoding="utf-8")
        old = np.asarray(Image.open(b.PECAS / "tronco_pintado.png"))
        grande = np.zeros((b.TELA[1], b.TELA[0], 4), np.uint8)
        grande[oy:oy + old.shape[0], ox:ox + old.shape[1]] = old
        grande[tela[..., 3] == 0] = 0
        pm = grande[Y0:ys.max() + 1, X0:xs.max() + 1]
        Image.fromarray(pm).save(b.PECAS / "tronco_pintado.png")
        # a sobra (o pedaço por baixo da junta) das variantes de braço sai de outro desenho e trazia lascas do corpo
        # dele (cabelo, ombro) para longe do ombro: fica só o que encosta no próprio braço
        for nome, pp in raw["pecas"].items():
            if not nome.startswith("braco_frente_"):
                continue
            sob = np.asarray(Image.open(b.PECAS / pp["sobra"]).convert("RGBA")).copy()
            br = np.asarray(Image.open(b.PECAS / pp["arquivo"]).convert("RGBA"))
            m = np.zeros(sob.shape[:2], np.uint8)
            ox2, oy2 = pp["origem"][0] - pp["origem_sobra"][0], pp["origem"][1] - pp["origem_sobra"][1]
            m[oy2:oy2 + br.shape[0], ox2:ox2 + br.shape[1]] = br[..., 3] > 0
            perto = cv2.dilate(m, np.ones((9, 9), np.uint8)) > 0
            sob[~perto] = 0
            Image.fromarray(sob).save(b.PECAS / pp["sobra"])
        print(f"tiras finas tiradas: {int(fino.sum())} px; peito do lado do braço de longe: {int(alvo.sum())} px do {DOADOR} (corpo {dx:+d},{dy:+d}, giro {giro})")
    return montar


def main():
    sys.argv = [sys.argv[0], "pengaro_e"] + sys.argv[1:]
    firme.montar_kit = montar_kit_pengaro_e(firme.montar_kit)
    firme.main()


if __name__ == "__main__":
    main()
