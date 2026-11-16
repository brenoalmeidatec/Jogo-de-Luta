#!/usr/bin/env python3
"""Boneco de peças (missão docs/missao-alisson-boneco-de-pecas.md, piloto do Pengaró base).

O Pengaró é desenhado uma vez só (o parado aprovado, quadros_arcade_hd/ginga/00.png), recortado em peças, e cada pose
sai dessas mesmas peças giradas (RotSprite, sem misturar cor) e movidas. Mãos e braços que mudam de desenho (punho de
guarda, braço esticado no contato) entram como VARIANTES recortadas de desenhos já aprovados e encaixadas na junta do
kit. Tudo é feito em índice de paleta (paleta_arcade_pecas.json), então cor nova não tem como aparecer.

  python ferramentas/boneco_pecas.py kit            recorta o kit em sprites/pengaro/pecas/ (PNG por peça + kit.json)
  python ferramentas/boneco_pecas.py pose soco      monta as poses do golpe em quadros_pecas_hd/ e quadros_pecas/

Tela e eixo iguais aos do jogo: 3x = 1080x780 com os pés em (540,660); 1x = 360x260 com os pés em (180,220).
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

os.environ.setdefault("LUTADOR", "pengaro")
os.environ.setdefault("FORMA", "pecas")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from quantizar_folha import ler_paleta, limpar, para_imagem, quantizar  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SPR = RAIZ / "sprites" / "pengaro"
HD = SPR / "quadros_arcade_hd"
PECAS = SPR / "pecas"
DADOS, PAL = ler_paleta()
TELA = (1080, 780)
EIXO = (540, 660)


# ---------------------------------------------------------------- RotSprite (Scale2x 3x, gira no vizinho, reduz 8x)
def scale2x(idx):
    p = np.pad(idx, 1, mode="edge")
    e = p[1:-1, 1:-1]
    b, h, d, f = p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]
    cond = (b != h) & (d != f)
    e0 = np.where(cond & (d == b), d, e)
    e1 = np.where(cond & (b == f), f, e)
    e2 = np.where(cond & (d == h), d, e)
    e3 = np.where(cond & (h == f), f, e)
    out = np.empty((idx.shape[0] * 2, idx.shape[1] * 2), idx.dtype)
    out[0::2, 0::2], out[0::2, 1::2], out[1::2, 0::2], out[1::2, 1::2] = e0, e1, e2, e3
    return out


def rotsprite(idx, ang, pivo):
    """Gira o recorte indexado (-1 = vazio) em `ang` graus (horário na tela) em volta de `pivo` (x, y) do recorte.
    Devolve (recorte novo, pivo novo). Nenhuma cor nova: só índices que já existiam."""
    if abs(ang) < 0.01:
        return idx.copy(), pivo
    big = idx
    for _ in range(3):
        big = scale2x(big)
    hb, wb = big.shape
    px, py = pivo[0] * 8 + 4, pivo[1] * 8 + 4
    r = np.radians(ang)
    c, s = np.cos(r), np.sin(r)
    cantos = np.array([[0, 0], [wb, 0], [0, hb], [wb, hb]], float) - (px, py)
    rx = cantos[:, 0] * c - cantos[:, 1] * s
    ry = cantos[:, 0] * s + cantos[:, 1] * c
    x0, x1 = int(np.floor(rx.min())) - 8, int(np.ceil(rx.max())) + 8
    y0, y1 = int(np.floor(ry.min())) - 8, int(np.ceil(ry.max())) + 8
    # alinha a grade de 8 com o pivô para o pivô cair no centro de um pixel
    x0 -= (x0 - (-4)) % 8
    y0 -= (y0 - (-4)) % 8
    w, h = (x1 - x0) // 8 + 1, (y1 - y0) // 8 + 1
    # amostra só o centro de cada célula 8x8 (vizinho mais próximo na grade grande)
    gx = x0 + np.arange(w) * 8 + 4
    gy = y0 + np.arange(h) * 8 + 4
    X, Y = np.meshgrid(gx, gy)
    sx = X * c + Y * s + px
    sy = -X * s + Y * c + py
    sxi, syi = np.round(sx).astype(int), np.round(sy).astype(int)
    ok = (sxi >= 0) & (sxi < wb) & (syi >= 0) & (syi < hb)
    out = np.full((h, w), -1, idx.dtype)
    out[ok] = big[syi[ok], sxi[ok]]
    novo_pivo = ((0 - x0 - 4) / 8, (0 - y0 - 4) / 8)
    return out, novo_pivo


# ---------------------------------------------------------------- kit
def indexar(caminho):
    return quantizar(Image.open(caminho), DADOS, PAL)


def mascara(poli, forma=TELA):
    m = Image.new("L", forma, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in poli], fill=255)
    return np.array(m) > 0


def recorte(idx, m):
    ys, xs = np.nonzero(m & (idx >= 0))
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    r = np.where(m[y0:y1, x0:x1], idx[y0:y1, x0:x1], -1)
    return r, (int(x0), int(y0))


def cinto(x):
    """Linha de cima da faixa no parado: acima é tronco, abaixo é quadril e pernas."""
    return 468 + (x - 511) * 4 / 56


REF = "ginga/00"
POLI = {
    "cabeca": [(522, 318), (604, 318), (604, 396), (586, 394), (566, 391), (549, 384), (539, 376), (528, 362)],
    "braco_tras": [(497, 392), (506, 405), (500, 425), (500, 440), (497, 460), (500, 470), (510, 478), (512, 500),
                   (500, 512), (498, 553), (470, 557), (449, 546), (455, 500), (461, 470), (461, 440), (469, 420),
                   (484, 399)],
    "braco_frente": [(578, 397), (585, 393), (592, 378), (612, 378), (642, 383), (644, 410), (632, 442), (616, 466),
                     (590, 468), (572, 460), (568, 449), (578, 437), (581, 421), (577, 405)],
}
# variantes do braço da frente: (desenho aprovado de onde sai, polígono nele). O encaixe no kit é achado pelo peito.
VARIANTES = {
    "aberta": (REF, POLI["braco_frente"]),
    "punho": ("parado/00", [(588, 398), (594, 392), (605, 389), (617, 391), (631, 397), (632, 420), (621, 439),
                            (608, 453), (594, 462), (581, 461), (574, 452), (580, 440), (587, 425)]),
    "esticado": ("soco/05", [(572, 393), (600, 393), (640, 393), (660, 395), (687, 397), (689, 435), (660, 434),
                             (625, 428), (595, 431), (578, 431), (569, 420)]),
}
OMBRO_FRENTE = (580, 411)
# pernas: a de trás (caneleira) e a da frente (calça branca) saem do quadril; o nó da faixa e as bolinhas ficam no quadril
POLI_PERNAS = {
    "perna_tras": [(485, 515), (520, 505), (552, 530), (552, 545), (530, 575), (522, 600), (510, 625), (505, 662),
                   (452, 662), (460, 630), (475, 610), (478, 580), (490, 550)],
    "perna_frente": [(552, 545), (552, 520), (575, 505), (598, 505), (610, 540), (614, 600), (602, 612), (598, 625),
                     (632, 645), (634, 662), (558, 662), (566, 630), (564, 612), (556, 580)],
}
NO_DA_FAIXA = [(545, 466), (600, 466), (598, 540), (565, 545), (548, 520)]
QUADRIL_TRAS, QUADRIL_FRENTE = (522, 510), (572, 512)
# variantes da perna da frente no chute: (desenho aprovado, polígono, quadril no desenho)
VARIANTES_PERNA = {
    "camara": ("chute_alto/02", [(512, 472), (530, 455), (545, 440), (575, 425), (600, 420), (611, 432), (613, 480),
                                 (599, 491), (589, 502), (586, 540), (584, 562), (564, 562), (558, 520), (553, 497),
                                 (538, 492), (518, 497), (511, 486)], (525, 485)),
    "esticada": ("chute_alto/04", [(512, 470), (560, 430), (600, 405), (628, 388), (640, 350), (660, 341), (693, 344),
                                   (693, 373), (670, 399), (645, 405), (643, 441), (600, 463), (575, 479), (555, 506),
                                   (535, 521), (512, 522)], (525, 490)),
}
JUNTAS = {  # pivô de cada peça no parado e a peça mãe
    "pernas": ((540, 470), None),
    "quadril": ((540, 490), None),
    "perna_tras": (QUADRIL_TRAS, "quadril"),
    "perna_frente": (QUADRIL_FRENTE, "quadril"),
    "tronco": ((540, 470), "quadril"),
    "braco_tras": ((497, 406), "tronco"),
    "cabeca": ((560, 386), "tronco"),
    "braco_frente": (OMBRO_FRENTE, "tronco"),
}
# a cabeça vai por baixo do tronco: o pescoço dela (sobra escondida) fica atrás do pescoço do tronco e não abre buraco
# quando a cabeça mexe
CAMADAS = ["cabeca", "tronco", "perna_tras", "quadril", "perna_frente", "braco_tras", "braco_frente"]
PESCOCO = [(536, 372), (552, 380), (568, 390), (588, 394), (588, 404), (566, 406), (540, 402), (530, 390)]


def alinhar(fonte, alvo, caixa=(530, 395, 572, 455), raio=14):
    """Deslocamento (dx, dy) que leva o desenho `fonte` para cima do `alvo`, medido no peito (onde os dois são o
    mesmo corpo)."""
    a = np.asarray(Image.open(HD / f"{alvo}.png").convert("RGB"), float)
    b = np.asarray(Image.open(HD / f"{fonte}.png").convert("RGB"), float)
    x0, y0, x1, y1 = caixa
    melhor = None
    for dy in range(-raio, raio + 1):
        for dx in range(-raio, raio + 1):
            d = np.abs(a[y0:y1, x0:x1] - b[y0 - dy:y1 - dy, x0 - dx:x1 - dx]).mean()
            if melhor is None or d < melhor[0]:
                melhor = (d, dx, dy)
    return melhor[1], melhor[2]


def montar_kit():
    PECAS.mkdir(parents=True, exist_ok=True)
    idx = indexar(HD / f"{REF}.png")
    yy, xx = np.mgrid[:TELA[1], :TELA[0]]
    m_cab = mascara(POLI["cabeca"])
    m_bt = mascara(POLI["braco_tras"])
    m_bf = mascara(POLI["braco_frente"])
    baixo = yy >= cinto(xx)
    partes = {
        "cabeca": (m_cab | mascara(PESCOCO)) & ~m_bf,
        "braco_tras": m_bt,
        "perna_tras": baixo & ~m_bt & mascara(POLI_PERNAS["perna_tras"]),
        "perna_frente": baixo & ~m_bt & mascara(POLI_PERNAS["perna_frente"]) & ~mascara(NO_DA_FAIXA),
        "tronco": ~baixo & ~m_bt & ~m_cab & ~m_bf,
    }
    # o que sobrou abaixo da virilha (contorno, beirada da calça) vai para a perna mais perto, para não ficar pixel
    # solto no lugar quando a perna sai
    resto = baixo & ~m_bt & ~partes["perna_tras"] & ~partes["perna_frente"] & (idx >= 0) & (yy >= 540)
    import cv2
    d_tras = cv2.distanceTransform(np.uint8(~partes["perna_tras"]), cv2.DIST_L2, 3)
    d_frente = cv2.distanceTransform(np.uint8(~partes["perna_frente"]), cv2.DIST_L2, 3)
    partes["perna_tras"] |= resto & (d_tras <= d_frente)
    partes["perna_frente"] |= resto & (d_frente < d_tras)
    # a calça branca atrás das bolinhas é da coxa da frente (sai com ela no chute); o nó e as bolinhas ficam
    ids = [c["id"] for c in DADOS["cores"]]
    calca = np.isin(idx, [ids.index(c) for c in ("calca_branco", "calca_sombra", "calca_contorno")])
    partes["perna_frente"] |= baixo & ~m_bt & calca & (yy >= 498) & (xx >= 566)
    partes["quadril"] = baixo & ~m_bt & ~partes["perna_tras"] & ~partes["perna_frente"]
    kit = {"ref": f"quadros_arcade_hd/{REF}.png", "tela": TELA, "eixo": EIXO, "camadas": CAMADAS, "pecas": {}}
    for nome, m in partes.items():
        r, (x0, y0) = recorte(idx, m)
        Image.fromarray(np.uint8(r + 1)).save(PECAS / f"{nome}.png")  # 0 = vazio, i+1 = cor i da paleta
        piv, mae = JUNTAS[nome]
        kit["pecas"][nome] = {"arquivo": f"{nome}.png", "origem": [x0, y0], "pivo": list(piv), "mae": mae}
    for var, (fonte, poli) in VARIANTES.items():
        dx, dy = (0, 0) if fonte == REF else alinhar(fonte, REF)
        fidx = indexar(HD / f"{fonte}.png")
        r, (x0, y0) = recorte(fidx, mascara(poli))
        nome = f"braco_frente_{var}"
        Image.fromarray(np.uint8(r + 1)).save(PECAS / f"{nome}.png")
        # origem já no lugar do kit (deslocada pelo alinhamento do peito)
        kit["pecas"][nome] = {"arquivo": f"{nome}.png", "origem": [x0 + dx, y0 + dy], "pivo": list(OMBRO_FRENTE),
                              "mae": "tronco", "fonte": f"quadros_arcade_hd/{fonte}.png", "alinhamento": [dx, dy]}
        print(f"{nome}: de {fonte}, alinhado {dx:+d},{dy:+d}")
    for var, (fonte, poli, quadril) in VARIANTES_PERNA.items():
        fidx = indexar(HD / f"{fonte}.png")
        r, (x0, y0) = recorte(fidx, mascara(poli))
        nome = f"perna_frente_{var}"
        Image.fromarray(np.uint8(r + 1)).save(PECAS / f"{nome}.png")
        # o quadril do desenho vai para o quadril da frente do kit
        dx, dy = QUADRIL_FRENTE[0] - quadril[0], QUADRIL_FRENTE[1] - quadril[1]
        kit["pecas"][nome] = {"arquivo": f"{nome}.png", "origem": [x0 + dx, y0 + dy], "pivo": list(QUADRIL_FRENTE),
                              "mae": "quadril", "fonte": f"quadros_arcade_hd/{fonte}.png", "alinhamento": [dx, dy]}
        print(f"{nome}: de {fonte}, quadril {quadril} -> {QUADRIL_FRENTE}")
    (PECAS / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")
    return kit


def ler_kit():
    kit = json.loads((PECAS / "kit.json").read_text(encoding="utf-8"))
    for p in kit["pecas"].values():
        p["idx"] = np.asarray(Image.open(PECAS / p["arquivo"]), int) - 1
    return kit


# ---------------------------------------------------------------- pose
def girar_ponto(p, piv, ang):
    r = np.radians(ang)
    x, y = p[0] - piv[0], p[1] - piv[1]
    return (piv[0] + x * np.cos(r) - y * np.sin(r), piv[1] + x * np.sin(r) + y * np.cos(r))


def montar(kit, pose):
    """pose: {peça: {"ang": graus, "dx": px, "dy": px, "var": variante}}. Ângulo e deslocamento são somados aos da
    mãe (a cabeça vai junto com o tronco). Devolve o quadro indexado na tela do jogo (3x)."""
    mundo = {}

    def transf(nome):
        if nome in mundo:
            return mundo[nome]
        piv, mae = JUNTAS[nome]
        p = pose.get(nome, {})
        if mae is None:
            pos, ang = (piv[0] + p.get("dx", 0), piv[1] + p.get("dy", 0)), p.get("ang", 0)
        else:
            mpos, mang, mpiv = transf(mae)
            # onde o pivô desta peça foi parar depois do movimento da mãe
            base = girar_ponto(piv, mpiv, mang)
            base = (base[0] + mpos[0] - mpiv[0], base[1] + mpos[1] - mpiv[1])
            pos, ang = (base[0] + p.get("dx", 0), base[1] + p.get("dy", 0)), mang + p.get("ang", 0)
        mundo[nome] = (pos, ang, piv)
        return mundo[nome]

    tela = np.full((TELA[1], TELA[0]), -1, int)
    for nome in CAMADAS:
        p = pose.get(nome, {})
        if p.get("esconde"):
            continue
        var = p.get("var") or ("aberta" if nome == "braco_frente" else None)
        chave = f"{nome}_{var}" if var else nome
        peca = kit["pecas"][chave]
        pos, ang, piv = transf(nome)
        ox, oy = peca["origem"]
        r, npiv = rotsprite(peca["idx"], ang, (piv[0] - ox, piv[1] - oy))
        x0 = int(round(pos[0] - npiv[0]))
        y0 = int(round(pos[1] - npiv[1]))
        h, w = r.shape
        sub = tela[y0:y0 + h, x0:x0 + w]
        rr = r[:sub.shape[0], :sub.shape[1]]
        sub[rr >= 0] = rr[rr >= 0]
    return limpar(sem_migalha(tela), DADOS)


def sem_migalha(idx, minimo=40):
    """Tira os pedacinhos soltos (menos de `minimo` px) que sobram nas emendas."""
    import cv2
    n, rot, st, _ = cv2.connectedComponentsWithStats(np.uint8(idx >= 0), connectivity=8)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < minimo:
            idx[rot == i] = -1
    return idx


def para_1x(idx):
    """3x -> 1x: a cor que mais aparece em cada bloco 3x3 (transparente só se o bloco for quase todo vazio)."""
    h, w = idx.shape[0] // 3, idx.shape[1] // 3
    blocos = idx[:h * 3, :w * 3].reshape(h, 3, w, 3).transpose(0, 2, 1, 3).reshape(h, w, 9)
    out = np.full((h, w), -1, int)
    for y, x in zip(*np.nonzero((blocos >= 0).sum(-1) >= 4)):
        v = blocos[y, x]
        v = v[v >= 0]
        valores, n = np.unique(v, return_counts=True)
        out[y, x] = valores[n.argmax()]
    return limpar(out, DADOS)


def gravar(idx, nome, i):
    for pasta, img in (("quadros_pecas_hd", idx), ("quadros_pecas", para_1x(idx))):
        destino = SPR / pasta / nome
        destino.mkdir(parents=True, exist_ok=True)
        para_imagem(img, PAL).save(destino / f"{i:02d}.png")


# ---------------------------------------------------------------- caminho B (comparativo): o mesmo kit no esqueleto do Blender
OSSOS_B = {
    "quadril": {"de": (540, 470), "para": (540, 540)},
    "coluna": {"de": (540, 470), "para": (556, 392), "mae": "quadril"},
    "cabeca": {"de": (558, 392), "para": (566, 340), "mae": "coluna"},
    "ombro_tras": {"de": (497, 406), "para": (470, 450), "mae": "coluna"},
}
CADEIA_BRACO = {"aberta": ((588, 458), (605, 432)), "punho": ((586, 459), (612, 415)),
                "esticado": ((625, 413), (680, 415))}
for _v, (_cot, _pun) in CADEIA_BRACO.items():
    OSSOS_B[f"umero_{_v}"] = {"de": OMBRO_FRENTE, "para": _cot, "mae": "coluna"}
    OSSOS_B[f"ante_{_v}"] = {"de": _cot, "para": _pun, "mae": f"umero_{_v}"}


def plano_blender(kit, quadros, pasta):
    """Grava as peças como imagens do tamanho da tela e o plano.json que o boneco_blender.py lê."""
    pasta.mkdir(parents=True, exist_ok=True)
    pecas = {}
    for chave, p in kit["pecas"].items():
        tela = np.full((TELA[1], TELA[0]), -1, int)
        ox, oy = p["origem"]
        h, w = p["idx"].shape
        tela[oy:oy + h, ox:ox + w] = p["idx"]
        arq = pasta / f"peca_{chave}.png"
        para_imagem(tela, PAL).save(arq)
        caixa = [ox - 2, oy - 2, ox + w + 2, oy + h + 2]
        if chave == "tronco":
            pesos = {"coluna": {"tipo": "y", "y0": 470, "y1": 420},
                     "quadril": {"tipo": "y", "y0": 470, "y1": 420, "inverte": True}}
        elif chave == "pernas":
            pesos = {"quadril": {"tipo": "fixo", "valor": 1}}
        elif chave == "cabeca":
            pesos = {"cabeca": {"tipo": "fixo", "valor": 1}}
        elif chave == "braco_tras":
            pesos = {"ombro_tras": {"tipo": "fixo", "valor": 1}}
        else:
            var = chave.split("_")[-1]
            cot, pun = CADEIA_BRACO[var]
            j = {"tipo": "junta", "junta": cot, "rumo": pun, "faixa": 6}
            pesos = {f"umero_{var}": dict(j, inverte=True), f"ante_{var}": j}
        pecas[chave] = {"imagem": str(arq), "caixa": caixa, "pesos": pesos}
    ordem = ["cabeca", "tronco", "pernas", "braco_tras"] + [k for k in pecas if k.startswith("braco_frente_")]
    plano = {"tela": TELA, "passo": 2, "ossos": OSSOS_B, "pecas": {k: pecas[k] for k in ordem}, "quadros": quadros}
    (pasta / "plano.json").write_text(json.dumps(plano, indent=1), encoding="utf-8")
    return pasta / "plano.json"
