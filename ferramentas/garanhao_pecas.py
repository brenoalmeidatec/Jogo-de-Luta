#!/usr/bin/env python3
"""Garanhão (Gutto despertado) no corpo firme: o firme.py com o kit_garanhao, mais o que o braço de perto esconde.

  python ferramentas/garanhao_pecas.py [anims] [--so-pose] [--video]

No rasga_couro/00 o braço de perto (corda no ombro, punho na frente da coxa) tapa a raiz do rabo, a coxa de trás e o
lado do quadril. Sem isso o rabo vira pedaço solto e abre buraco quando o braço ou a perna mexem. Aqui essas áreas
escondidas são pintadas por baixo do braço, na cor do que está em volta (calção escuro e pelo da perna), depois que o
firme.py monta o kit. Fica escondido pelo braço na guarda.
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

# por baixo do braço de perto: do rabo até a faixa (quadril) e a coxa de trás até o joelho
QUADRIL_ESCONDIDO = [(458, 544), (530, 534), (534, 556), (500, 566), (464, 574)]
# entre as pernas: o calção atrás das coxas (aparece quando as pernas abrem)
QUADRIL_FUNDO = [(530, 532), (570, 532), (572, 556), (552, 572), (532, 566)]
COXA_ESCONDIDA = [(472, 552), (532, 548), (534, 578), (520, 604), (500, 616), (476, 612), (470, 584)]


def repintar(pecas, kit, nome, poli, so_ref=False, perto=0, claro=False, sob_braco=False):
    b = firme.b
    p = kit["pecas"][nome]
    im = np.array(Image.open(pecas / p["arquivo"]).convert("RGBA"))
    tela = np.zeros((b.TELA[1], b.TELA[0], 4), np.uint8)
    x0, y0 = p["origem"]
    tela[y0:y0 + im.shape[0], x0:x0 + im.shape[1]] = im
    m = b.mascara(poli) & (tela[..., 3] == 0)
    tem = tela[..., 3] > 0
    if so_ref:  # só onde o parado tem desenho (não pinta o fundo em volta)
        m &= firme.abrir(firme.K.REF)[..., 3] > 0
    if sob_braco:  # só o que o braço de perto tapa no parado (com folga de 4 px para dentro): nunca fica à vista
        braco = firme.b.mascara(firme.K.BRACO_TRAS) & (firme.abrir(firme.K.REF)[..., 3] > 0)
        m &= cv2.erode(braco.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    if perto:  # só a faixa encostada no que a peça já tem
        m &= cv2.dilate(tem.astype(np.uint8), np.ones((2 * perto + 1, 2 * perto + 1), np.uint8)) > 0
    viz = cv2.dilate(m.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
    amostra = tela[viz & tem][:, :3]
    if claro:  # pele/pelo da perna, não o contorno nem o calção
        amostra = amostra[amostra.astype(int).sum(-1) > 150] if (amostra.astype(int).sum(-1) > 150).any() else amostra
    if len(amostra) == 0:
        return
    # textura do que está em volta (inpaint), não cor chapada; o fundo transparente não entra na conta
    desconhecido = (m | ~tem).astype(np.uint8)
    rgb = cv2.inpaint(np.ascontiguousarray(tela[..., :3]), desconhecido, 9, cv2.INPAINT_TELEA)
    if claro:  # sem puxar o contorno escuro para dentro: clareia até o tom do pelo em volta
        alvo = np.median(amostra, axis=0)
        esc = rgb[m].astype(float)
        fator = np.clip(alvo.sum() / np.maximum(esc.sum(-1, keepdims=True), 1), 1, 2.5)
        rgb[m] = np.clip(esc * fator, 0, 255).astype(np.uint8)
    tela[m, :3] = rgb[m]
    tela[m, 3] = 255
    ys, xs = np.nonzero(tela[..., 3] > 0)
    X0, Y0, X1, Y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    Image.fromarray(tela[Y0:Y1, X0:X1]).save(pecas / p["arquivo"])
    p["origem"] = [int(X0), int(Y0)]


def montar_kit_garanhao(original):
    def montar():
        original()
        pecas = firme.b.PECAS
        kit = json.loads((pecas / "kit.json").read_text(encoding="utf-8"))
        repintar(pecas, kit, "quadril", QUADRIL_ESCONDIDO)
        repintar(pecas, kit, "quadril", QUADRIL_FUNDO)
        repintar(pecas, kit, "coxa_tras", COXA_ESCONDIDA, claro=True, sob_braco=True)
        repintar(pecas, kit, "perna_tras", COXA_ESCONDIDA, claro=True, sob_braco=True)  # a perna no chão é desenhada por malha (peça inteira)
        # crina atrás do rosto: a cabeça que gira não abre vão entre o rosto e a crina
        repintar(pecas, kit, "tronco", firme.K.CABECA, so_ref=True, perto=14)
        (pecas / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")
    return montar


def main():
    sys.argv = [sys.argv[0], "garanhao"] + sys.argv[1:]
    firme.montar_kit = montar_kit_garanhao(firme.montar_kit)
    firme.main()


if __name__ == "__main__":
    main()
