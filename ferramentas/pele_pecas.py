#!/usr/bin/env python3
"""Boneco de peças sem linha de corte (pedido do Alisson, 17/11: "tem que ficar como se fosse o personagem sempre
por inteiro").

O kit continua separado em peças (cabeça, tronco, quadril, coxas, canelas, braços, pés e as variantes), para trocar a
cabeça ou uma peça e fazer ajuste fino depois. O que muda é o desenho na tela: em vez de colar peças rígidas giradas
(a beira de cada peça aparecia como corte), cada camada é uma pele que dobra nas juntas, como no Spine/Live2D.

  camadas      perna de trás, corpo (tronco + quadril), perna da frente, braço de trás, braço da frente; a cabeça vai
               rígida (troca de expressão) por baixo do tronco, como no kit
  pesos        cada pixel segue o próprio osso e, perto da emenda, também o osso vizinho (dos dois lados: a beira
               do quadril acompanha a coxa e a beira da coxa acompanha o quadril), com peso que cai até MISTURA px
               da região do vizinho no parado. Na emenda os dois lados estão no mesmo lugar: sem fresta nem degrau.
  desenho      cada pixel vira SUB x SUB pontinhos levados pela soma ponderada dos ossos (skinning linear) e
               pintados no vizinho mais perto: sem buraco quando a peça gira.

Variante (punho, braço esticado, perna levantada) entra do mesmo jeito: a imagem dela está no lugar do parado, então
o peso sai da mesma região da mãe.
"""
import numpy as np

import boneco_ajuste as b

MISTURA = 28   # px (HD) da faixa de mistura na emenda (quadril, coxa, canela)
SUB = 3        # pontinhos por lado de cada pixel

# camada: [(slot, ossos vizinhos com quem a peça se mistura na emenda)] na ordem em que se pinta dentro da camada.
# A mistura é dos dois lados da emenda (a beira do quadril também acompanha a coxa), então nenhum corte aparece.
CAMADAS = [
    ("perna_tras", [("canela_tras", ("coxa_tras",)), ("coxa_tras", ("quadril", "canela_tras"))]),
    ("corpo", [("quadril", ("tronco", "coxa_tras", "coxa_frente")), ("tronco", ("quadril", "braco_tras", "braco_frente"))]),
    ("perna_frente", [("canela_frente", ("coxa_frente",)), ("coxa_frente", ("quadril", "canela_frente"))]),
    ("braco_tras", [("braco_tras", ("tronco",))]),
    ("braco_frente", [("braco_frente", ("tronco",))]),
]
# braço puxa pouco o peito (o tronco não deforma); perna e quadril se misturam numa faixa maior
MISTURA_OSSO = {"braco_tras": 8, "braco_frente": 8}


def _regioes(kit):
    """Região de cada peça do parado (alfa no lugar do parado)."""
    if "_regioes" in kit:
        return kit["_regioes"]
    import cv2
    out = {}
    for slot in b.OSSOS:
        p = kit["pecas"][slot]
        m = np.zeros((b.TELA[1], b.TELA[0]), np.uint8)
        ox, oy = p["origem"]
        h, w = p["img"].shape[:2]
        m[oy:oy + h, ox:ox + w] = p["img"][..., 3] > 0
        out[slot] = m
    dist = {s: cv2.distanceTransform(1 - m, cv2.DIST_L2, 5) for s, m in out.items()}
    kit["_regioes"] = (out, dist)
    return kit["_regioes"]


# perna da frente em variante (levantada/esticada): a parte do quadril que no parado é o alto da coxa da frente (abaixo
# da junta) fica de fora, senão sobra um pedaço de calça pendurado embaixo da perna erguida
SEM_ALTO_DA_COXA = 2   # px: distância até a coxa da frente do parado que conta como "alto da coxa"
ALTO_DA_COXA_Y = -12   # px em relação à junta da coxa da frente


def _pontos(kit, chave_peca, slot, vizinhos, sem_coxa=False):
    """Pontinhos da peça (no lugar do parado), cor e pesos: [próprio osso, vizinhos...] (somam 1)."""
    cache = kit.setdefault("_pontos", {})
    if (chave_peca, vizinhos, sem_coxa) in cache:
        return cache[(chave_peca, vizinhos, sem_coxa)]
    p = kit["pecas"][chave_peca]
    img = p["img"]
    ox, oy = p["origem"]
    ys, xs = np.nonzero(img[..., 3] > 0)
    if sem_coxa:
        _, dist0 = _regioes(kit)
        jy = b.OSSOS["coxa_frente"][0][1] + ALTO_DA_COXA_Y
        fica = ~((dist0["coxa_frente"][ys + oy, xs + ox] < SEM_ALTO_DA_COXA) & (ys + oy > jy))
        ys, xs = ys[fica], xs[fica]
    cor = img[ys, xs]
    X, Y = xs + ox, ys + oy
    _, dist = _regioes(kit)
    yc, xc = np.clip(Y, 0, b.TELA[1] - 1), np.clip(X, 0, b.TELA[0] - 1)
    pesos = [np.ones(len(X), np.float32)]
    for v in vizinhos:
        r = MISTURA_OSSO.get(v, MISTURA_OSSO.get(slot, MISTURA))
        d = dist[v][yc, xc]
        pesos.append((np.clip(1 - d / r, 0, 1) ** 2).astype(np.float32))
    pesos = np.stack(pesos, 1)
    pesos /= pesos.sum(1, keepdims=True)
    o = (np.arange(SUB) + 0.5) / SUB - 0.5
    gx, gy = np.meshgrid(o, o)
    gx, gy = gx.ravel(), gy.ravel()
    PX = (X[:, None] + gx[None]).ravel().astype(np.float32)
    PY = (Y[:, None] + gy[None]).ravel().astype(np.float32)
    res = (PX, PY, np.repeat(cor, SUB * SUB, 0), np.repeat(pesos, SUB * SUB, 0))
    cache[(chave_peca, vizinhos, sem_coxa)] = res
    return res


def _transformar(w, slot, X, Y):
    """Ponto do parado -> tela pelo osso `slot` (gira na junta e anda com ela)."""
    jr = b.OSSOS[slot][0]
    pos, ang = w[slot]
    r = np.radians(ang)
    c, s = np.cos(r), np.sin(r)
    dx, dy = X - jr[0], Y - jr[1]
    return pos[0] + dx * c - dy * s, pos[1] + dx * s + dy * c


def desenhar(kit, pose):
    w = b.mundo(pose)
    tela = np.zeros((b.TELA[1], b.TELA[0], 4), np.uint8)
    # cabeça rígida, por baixo do tronco (como no kit); o pescoço fica coberto pela gola do tronco
    cab = kit["pecas"][b.chave("cabeca", pose)]
    pos, ang = w["cabeca"]
    r, x0, y0 = b.colocar(cab, cab["img"], cab["origem"], pos, ang)
    b.colar(tela, r, x0, y0)
    H, W = tela.shape[:2]
    for _, pecas in CAMADAS:
        for slot, vizinhos in pecas:
            if slot == "canela_frente" and pose.get("coxa_frente", {}).get("var"):
                continue  # perna levantada: um desenho só (coxa, canela e pé)
            if slot == "coxa_frente" and pose.get("coxa_frente", {}).get("var"):
                vizinhos = ("quadril",)
            if slot == "quadril" and pose.get("coxa_frente", {}).get("var"):
                vizinhos = tuple(v for v in vizinhos if v != "coxa_frente")
            sem_coxa = slot == "quadril" and pose.get("coxa_frente", {}).get("var") in ("camara", "esticada")
            X, Y, cor, pesos = _pontos(kit, b.chave(slot, pose), slot, vizinhos, sem_coxa)
            ax = np.zeros_like(X)
            ay = np.zeros_like(Y)
            for k, osso in enumerate((slot,) + tuple(vizinhos)):
                tx, ty = _transformar(w, osso, X, Y)
                ax += pesos[:, k] * tx
                ay += pesos[:, k] * ty
            xi = np.rint(ax).astype(np.int32)
            yi = np.rint(ay).astype(np.int32)
            ok = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
            tela[yi[ok], xi[ok]] = cor[ok]
    return tela
