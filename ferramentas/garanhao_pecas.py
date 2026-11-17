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


CALCAO = (524, 558, 26, 26)  # pedaço só de calção preto no parado (rasga_couro/00)


def repintar(pecas, kit, nome, poli, so_ref=False, perto=0, claro=False, sob_braco=False, textura=None):
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
    if textura:  # pano do calção copiado em ladrilho de um pedaço só de calção do parado (sem o branco da faixa)
        tx, ty, tw, th = textura
        ref = firme.abrir(firme.K.REF)
        yy, xx = np.nonzero(m)
        rgb[yy, xx] = ref[ty + (yy - ty) % th, tx + (xx - tx) % tw, :3]
    tela[m, :3] = rgb[m]
    tela[m, 3] = 255
    ys, xs = np.nonzero(tela[..., 3] > 0)
    X0, Y0, X1, Y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    Image.fromarray(tela[Y0:Y1, X0:X1]).save(pecas / p["arquivo"])
    p["origem"] = [int(X0), int(Y0)]


def perna_de_tras_da_da_frente(pecas, kit):
    """A perna de trás quase toda some atrás do braço de perto no parado (só a canela e o casco aparecem). Ela passa a
    ser o desenho inteiro da perna da frente, girado no quadril até o tornozelo cair no tornozelo de trás e um pouco
    mais escuro (fica do lado de lá do corpo). Coxa e canela saem dela no joelho de trás."""
    b, K = firme.b, firme.K
    pf_ = kit["pecas"]["perna_frente"]
    im = np.array(Image.open(pecas / pf_["arquivo"]).convert("RGBA"))
    qf, qt = K.OSSOS["coxa_frente"][0], K.OSSOS["coxa_tras"][0]
    tf, tt = K.TORNOZELO["canela_frente"], K.TORNOZELO["canela_tras"]
    ang = np.degrees(np.arctan2(tt[1] - qt[1], tt[0] - qt[0]) - np.arctan2(tf[1] - qf[1], tf[0] - qf[0]))
    piv = (qf[0] - pf_["origem"][0], qf[1] - pf_["origem"][1])
    r, pv = b.rotsprite(im, ang, piv)
    r[..., :3] = (r[..., :3].astype(float) * 0.85).astype(np.uint8)
    tela = np.zeros((b.TELA[1], b.TELA[0], 4), np.uint8)
    x0, y0 = int(round(qt[0] - pv[0])), int(round(qt[1] - pv[1]))
    fundo = y0 + int(np.nonzero((r[..., 3] > 0).any(1))[0].max())
    b.colar(tela, r, x0, y0 - (fundo - (firme.EIXO[1] - 1)))  # casco no chão (linha 659), como o da frente
    yy = np.mgrid[:b.TELA[1], :b.TELA[0]][0]
    jt = K.JOELHO_TRAS[1]
    for nome, m in (("perna_tras", np.ones(yy.shape, bool)), ("coxa_tras", yy < jt), ("canela_tras", yy >= jt - 12)):
        img = np.where((m & (tela[..., 3] > 0))[..., None], tela, 0).astype(np.uint8)
        ys, xs = np.nonzero(img[..., 3] > 0)
        X0, Y0, X1, Y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        Image.fromarray(img[Y0:Y1, X0:X1]).save(pecas / kit["pecas"][nome]["arquivo"])
        kit["pecas"][nome]["origem"] = [int(X0), int(Y0)]
    return round(float(ang), 1)


def montar_kit_garanhao(original):
    def montar():
        original()
        pecas = firme.b.PECAS
        kit = json.loads((pecas / "kit.json").read_text(encoding="utf-8"))
        repintar(pecas, kit, "quadril", QUADRIL_ESCONDIDO, textura=CALCAO)
        repintar(pecas, kit, "quadril", QUADRIL_FUNDO, textura=CALCAO)
        print("perna de trás = perna da frente girada", perna_de_tras_da_da_frente(pecas, kit), "graus")  # a perna no chão é desenhada por malha (peça inteira)
        # crina atrás do rosto: a cabeça que gira não abre vão entre o rosto e a crina
        repintar(pecas, kit, "tronco", firme.K.CABECA, so_ref=True, perto=14)
        lado_do_peito(pecas, kit)
        (pecas / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")
    return montar


PEITO_AO_LADO = 28  # o lado do tronco sob o braço de trás vem do tronco logo à frente (mesma pele e tatuagem)


def lado_do_peito(pecas, kit):
    """O pedaço do tronco que o braço de trás tapa no parado ganha a pele do tronco ao lado (cópia do desenho, com
    tatuagem e sombra), em vez de inpaint borrado; aí deixa de ser 'pintado' para o robô."""
    p = kit["pecas"]["tronco"]
    ox, oy = p["origem"]
    img = np.array(Image.open(pecas / p["arquivo"]).convert("RGBA"))
    pm = np.array(Image.open(pecas / "tronco_pintado.png").convert("RGBA"))
    ref = firme.abrir(firme.K.REF)
    ys, xs = np.nonzero(pm[..., 3] > 0)
    X, Y = xs + ox + PEITO_AO_LADO, ys + oy
    ok = ref[Y, X, 3] > 0
    img[ys[ok], xs[ok], :3] = ref[Y[ok], X[ok], :3]
    pm[ys[ok], xs[ok]] = 0
    Image.fromarray(img).save(pecas / p["arquivo"])
    Image.fromarray(pm).save(pecas / "tronco_pintado.png")
    print(f"lado do peito: {int(ok.sum())} de {len(ys)} px copiados do tronco ao lado")


def na_cor_do_parado(a):
    """Desenho de hoje (especial) nas cores do parado: casa a distribuição de cor (LAB, por percentil) com a do REF e
    usa só cores que existem no REF. Sem isso o coice saía mais rosado que o resto (cor mudando de quadro para quadro)."""
    ref = firme.abrir(firme.K.REF)
    m1, m2 = a[..., 3] > 0, ref[..., 3] > 0
    lab = lambda x: cv2.cvtColor(np.ascontiguousarray(x[..., :3]), cv2.COLOR_RGB2LAB).astype(float)
    L1, L2 = lab(a), lab(ref)
    out = L1.copy()
    qs = np.linspace(0, 100, 101)
    for c in range(3):
        out[..., c][m1] = np.interp(L1[..., c][m1], np.percentile(L1[..., c][m1], qs), np.percentile(L2[..., c][m2], qs))
    rgb = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)
    pal = np.unique(ref[..., :3][m2].reshape(-1, 3), axis=0).astype(int)
    cores, inv = np.unique(rgb[m1].reshape(-1, 3), axis=0, return_inverse=True)
    idx = np.concatenate([((cores[k:k + 256, None, :].astype(int) - pal[None]) ** 2).sum(-1).argmin(1)
                          for k in range(0, len(cores), 256)])
    a = a.copy()
    a[..., :3][m1] = pal[idx][inv.ravel()]
    # só o boneco (sem lasca solta) e pé no chão do jogo (linha 659, não 660)
    al = (a[..., 3] > 0).astype(np.uint8)
    n, lab_, st, _ = cv2.connectedComponentsWithStats(al, connectivity=8)
    if n > 2:
        maior = 1 + int(np.argmax(st[1:, 4]))
        a[(lab_ != maior) & (lab_ > 0)] = 0
    ys = np.nonzero((a[..., 3] > 0).any(1))[0]
    sobe = max(0, int(ys.max()) - (firme.EIXO[1] - 1))
    if sobe:
        a = np.roll(a, -sobe, axis=0)
    return a


def especial_garanhao(original):
    def esp(q):
        if q not in firme._ESP:
            firme._ESP[q] = na_cor_do_parado(original(q))
        return firme._ESP[q].copy()
    return esp


def main():
    sys.argv = [sys.argv[0], "garanhao"] + sys.argv[1:]
    firme.montar_kit = montar_kit_garanhao(firme.montar_kit)
    firme.especial = especial_garanhao(firme.especial)
    firme.main()


if __name__ == "__main__":
    main()
