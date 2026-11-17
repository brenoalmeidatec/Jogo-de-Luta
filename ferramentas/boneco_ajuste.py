#!/usr/bin/env python3
"""Boneco de peças, versão 2 (pedido do Alisson em 2026-11-16, depois do piloto):

- cor cheia: as peças guardam as cores do desenho aprovado (nada de paleta de 15 cores), então a nitidez é a mesma do
  jogo de hoje;
- juntas que não descolam: cada osso tem a ponta presa na junta da peça mãe, e cada peça leva uma "sobra" redonda em
  volta da junta que só pinta onde ficou buraco; o peito e a calça escondidos atrás dos braços foram tapados no kit;
- os movimentos de hoje: em vez de inventar a pose, o programa encaixa cada peça fixa em cima de cada quadro que o jogo
  mostra hoje (procura o giro e o deslocamento que mais casam), então o golpe se mexe igual ao atual, mas o corpo não
  muda de tamanho entre os quadros.

  python ferramentas/boneco_ajuste.py kit                 recorta o kit em sprites/pengaro/pecas/ (RGBA + kit.json)
  python ferramentas/boneco_ajuste.py animar [NOMES]      parado, soco e chute_alto em quadros_pecas_hd/ e quadros_pecas/
"""
import json
import math
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from boneco_pecas import scale2x  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SPR = RAIZ / "sprites" / "pengaro"
HD = SPR / "quadros_arcade_hd"
PECAS = SPR / "pecas"
TELA = (1080, 780)
REF = "ginga/00"


# ------------------------------------------------------------------ RotSprite em cor cheia
def rotsprite(rgba, ang, pivo):
    """Gira o recorte RGBA em `ang` graus (horário na tela) em volta de `pivo`. Sem misturar cor: Scale2x três vezes
    (8x), amostra no vizinho mais próximo e volta para 1x. Devolve (recorte, pivo novo)."""
    h0, w0 = rgba.shape[:2]
    if abs(ang) < 0.01:
        return rgba.copy(), pivo
    chave = rgba.reshape(-1, 4).view(np.uint32).reshape(h0, w0)
    cores, idx = np.unique(chave, return_inverse=True)
    idx = idx.reshape(h0, w0)
    big = idx
    for _ in range(3):
        big = scale2x(big)
    hb, wb = big.shape
    px, py = pivo[0] * 8 + 4, pivo[1] * 8 + 4
    r = np.radians(ang)
    c, s = np.cos(r), np.sin(r)
    cant = np.array([[0, 0], [wb, 0], [0, hb], [wb, hb]], float) - (px, py)
    rx, ry = cant[:, 0] * c - cant[:, 1] * s, cant[:, 0] * s + cant[:, 1] * c
    x0 = int(np.floor(rx.min() / 8)) * 8 - 4 - 8
    y0 = int(np.floor(ry.min() / 8)) * 8 - 4 - 8
    w = int((rx.max() - x0) // 8) + 3
    h = int((ry.max() - y0) // 8) + 3
    X, Y = np.meshgrid(x0 + np.arange(w) * 8 + 4, y0 + np.arange(h) * 8 + 4)
    sx = np.round(X * c + Y * s + px).astype(int)
    sy = np.round(-X * s + Y * c + py).astype(int)
    ok = (sx >= 0) & (sx < wb) & (sy >= 0) & (sy < hb)
    out = np.zeros((h, w), np.uint32)
    out[ok] = cores[big[sy[ok], sx[ok]]]
    out = out.view(np.uint8).reshape(h, w, 4).copy()
    return out, ((-x0 - 4) / 8, (-y0 - 4) / 8)


# ------------------------------------------------------------------ kit
def mascara(poli, forma=TELA):
    m = Image.new("L", forma, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in poli], fill=255)
    return np.array(m) > 0


def abrir(nome):
    return np.array(Image.open(HD / f"{nome}.png").convert("RGBA"))


def cinto(x):
    return 468 + (x - 511) * 4 / 56


CABECA = [(522, 318), (604, 318), (604, 396), (586, 394), (566, 391), (549, 384), (539, 376), (528, 362)]
PESCOCO = [(536, 372), (552, 380), (568, 390), (588, 394), (588, 404), (566, 406), (540, 402), (530, 390)]
BRACO_TRAS = [(497, 392), (506, 405), (500, 425), (500, 440), (497, 460), (500, 470), (510, 478), (512, 500),
              (500, 512), (498, 553), (470, 557), (449, 546), (455, 500), (461, 470), (461, 440), (469, 420),
              (484, 399)]
BRACO_FRENTE = [(578, 397), (585, 393), (592, 378), (612, 378), (642, 383), (644, 410), (632, 442), (616, 466),
                (590, 468), (572, 460), (568, 449), (578, 437), (581, 421), (577, 405)]
PERNA_TRAS = [(485, 515), (520, 505), (552, 530), (552, 545), (530, 575), (522, 600), (510, 625), (505, 662),
              (452, 662), (460, 630), (475, 610), (478, 580), (490, 550)]
PERNA_FRENTE = [(552, 545), (552, 520), (575, 505), (598, 505), (610, 540), (614, 600), (602, 612), (598, 625),
                (632, 645), (634, 662), (558, 662), (566, 630), (564, 612), (556, 580)]
NO_DA_FAIXA = [(545, 466), (600, 466), (598, 540), (565, 545), (548, 520)]
# região do peito e da calça que o braço tapa no parado: tapada no kit para não abrir buraco quando o braço sai
PEITO_ESCONDIDO = [(566, 394), (581, 398), (585, 420), (583, 440), (576, 462), (556, 466), (556, 396)]
LADO_ESCONDIDO = [(497, 400), (512, 400), (514, 470), (500, 470)]
CALCA_ESCONDIDA = [(498, 470), (515, 470), (518, 530), (498, 530)]

JOELHO_TRAS, JOELHO_FRENTE = (500, 576), (586, 576)
OSSOS = {  # junta (pivô) no parado, peça mãe, ponta (para a régua)
    "quadril": ((540, 490), None, (540, 520)),
    "tronco": ((540, 470), "quadril", (558, 392)),
    "cabeca": ((560, 388), "tronco", (566, 330)),
    "braco_tras": ((497, 406), "tronco", (480, 500)),
    "braco_frente": ((580, 411), "tronco", (600, 430)),
    "coxa_tras": ((522, 510), "quadril", JOELHO_TRAS),
    "canela_tras": (JOELHO_TRAS, "coxa_tras", (487, 630)),
    "coxa_frente": ((572, 512), "quadril", JOELHO_FRENTE),
    "canela_frente": (JOELHO_FRENTE, "coxa_frente", (590, 628)),
}
CAMADAS = ["cabeca", "tronco", "coxa_tras", "canela_tras", "quadril", "canela_frente", "coxa_frente", "braco_tras",
           "braco_frente"]
# variantes: desenhos aprovados de onde sai a peça quando ela muda de desenho (não de ângulo)
VARIANTES = {
    "braco_frente": {
        "punho": ("parado/00", [(588, 398), (594, 392), (605, 389), (617, 391), (631, 397), (632, 420), (621, 439),
                                (608, 453), (594, 462), (581, 461), (574, 452), (580, 440), (587, 425)], (582, 418)),
        "esticado": ("soco/05", [(572, 393), (600, 393), (640, 393), (660, 395), (687, 397), (689, 435), (660, 434),
                                 (625, 428), (595, 431), (578, 431), (569, 420)], (580, 411)),
    },
    "coxa_frente": {  # a perna da frente inteira levantada (coxa + canela + pé num desenho só)
        "camara": ("chute_alto/02", [(512, 472), (530, 455), (545, 440), (575, 425), (600, 420), (611, 432),
                                     (613, 480), (599, 491), (589, 502), (586, 540), (584, 562), (564, 562),
                                     (558, 520), (553, 497), (538, 492), (518, 497), (511, 486)], (525, 485)),
        "esticada": ("chute_alto/04", [(512, 470), (560, 430), (600, 405), (628, 388), (640, 350), (660, 341),
                                       (693, 344), (693, 373), (670, 399), (645, 405), (643, 441), (600, 463),
                                       (575, 479), (555, 506), (535, 521), (512, 522)], (525, 490)),
    },
}
SOBRA = 9  # raio da sobra em volta de cada junta


def tapar(img, regiao, dono):
    """Pinta por baixo (inpaint) a parte de `regiao` que fica dentro do contorno da peça `dono`."""
    alvo = regiao & ~dono
    if not alvo.any():
        return img
    rgb = cv2.cvtColor(img[..., :3], cv2.COLOR_RGB2BGR)
    # o fundo transparente (preto) não serve de cor: entra na máscara junto, senão o preto escorre para dentro
    vazio = (img[..., 3] == 0) & (cv2.dilate(np.uint8(alvo), np.ones((25, 25), np.uint8)) > 0)
    pint = cv2.inpaint(rgb, np.uint8(alvo | vazio) * 255, 4, cv2.INPAINT_TELEA)
    out = img.copy()
    out[alvo, :3] = cv2.cvtColor(pint, cv2.COLOR_BGR2RGB)[alvo]
    out[alvo, 3] = 255
    return out


def contornar(img, m):
    """Contorno escuro de 1 px na beirada nova de uma peça tapada (onde a peça termina e antes tinha outra)."""
    borda = m & ~cv2.erode(np.uint8(m), np.ones((3, 3), np.uint8)).astype(bool)
    out = img.copy()
    out[borda, :3] = (40, 14, 22)
    return out


def montar_kit():
    if PECAS.exists():
        shutil.rmtree(PECAS)
    PECAS.mkdir(parents=True)
    ref = abrir(REF)
    alfa = ref[..., 3] > 0
    yy, xx = np.mgrid[:TELA[1], :TELA[0]]
    baixo = yy >= cinto(xx)
    m_cab, m_bt, m_bf = mascara(CABECA), mascara(BRACO_TRAS) & alfa, mascara(BRACO_FRENTE) & alfa
    pt = baixo & ~m_bt & mascara(PERNA_TRAS) & alfa
    pf = baixo & ~m_bt & mascara(PERNA_FRENTE) & ~mascara(NO_DA_FAIXA) & alfa
    resto = baixo & ~m_bt & ~pt & ~pf & alfa & (yy >= 540)
    dt = cv2.distanceTransform(np.uint8(~pt), cv2.DIST_L2, 3)
    df = cv2.distanceTransform(np.uint8(~pf), cv2.DIST_L2, 3)
    pt |= resto & (dt <= df)
    pf |= resto & (df < dt)
    # a calça branca atrás das bolinhas é da coxa da frente
    rgb = ref[..., :3].astype(int)
    branco = (rgb.min(-1) > 150) & (np.ptp(rgb, -1) < 90)
    pf |= baixo & ~m_bt & branco & (yy >= 498) & (xx >= 566) & alfa
    partes = {
        "cabeca": (m_cab | mascara(PESCOCO)) & ~m_bf & alfa,
        "braco_tras": m_bt,
        "braco_frente": m_bf,
        "tronco": ~baixo & ~m_bt & ~m_cab & ~m_bf & alfa,
        "coxa_tras": pt & (yy < JOELHO_TRAS[1]),
        "canela_tras": pt & (yy >= JOELHO_TRAS[1]),
        "coxa_frente": pf & (yy < JOELHO_FRENTE[1]),
        # a canela da frente leva 12 linhas da coxa acima do joelho: fica por baixo da coxa e tapa a fresta quando
        # o joelho dobra
        "canela_frente": pf & (yy >= JOELHO_FRENTE[1] - 12),
    }
    partes["quadril"] = baixo & ~m_bt & ~pt & ~pf & alfa
    imgs = {k: np.where(m[..., None], ref, 0).astype(np.uint8) for k, m in partes.items()}
    # tapa o que os braços escondem: peito (braço da frente), lado do tronco e calça (braço de trás com a garrafa)
    peito = mascara(PEITO_ESCONDIDO) & m_bf
    imgs["tronco"] = tapar(np.where((partes["tronco"] | peito)[..., None], ref, 0).astype(np.uint8), peito,
                           partes["tronco"])
    lado = mascara(LADO_ESCONDIDO) & m_bt & ~baixo
    imgs["tronco"] = tapar(imgs["tronco"], lado, imgs["tronco"][..., 3] > 0)
    calca = mascara(CALCA_ESCONDIDA) & m_bt & baixo
    imgs["quadril"] = tapar(imgs["quadril"], calca, partes["quadril"])
    kit = {"ref": f"quadros_arcade_hd/{REF}.png", "pecas": {}}

    def guardar(nome, img, junta, mae, fonte=REF, fonte_img=None):
        a = img[..., 3] > 0
        ys, xs = np.nonzero(a)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        Image.fromarray(img[y0:y1, x0:x1]).save(PECAS / f"{nome}.png")
        # sobra: o desenho em volta da junta (do mesmo desenho de onde a peça saiu), para tapar buraco na emenda
        if fonte_img is None:
            fonte_img = abrir(fonte)
        disco = np.zeros(TELA[::-1], np.uint8)
        cv2.circle(disco, (int(junta[0]), int(junta[1])), SOBRA, 1, -1)
        sob = np.where((disco.astype(bool) & (fonte_img[..., 3] > 0))[..., None], fonte_img, 0).astype(np.uint8)
        Image.fromarray(sob[y0 - SOBRA:y1 + SOBRA, x0 - SOBRA:x1 + SOBRA]).save(PECAS / f"{nome}_sobra.png")
        kit["pecas"][nome] = {"arquivo": f"{nome}.png", "origem": [int(x0), int(y0)], "junta": list(junta),
                              "mae": mae, "fonte": f"quadros_arcade_hd/{fonte}.png",
                              "sobra": f"{nome}_sobra.png", "origem_sobra": [int(x0 - SOBRA), int(y0 - SOBRA)]}

    for nome, img in imgs.items():
        junta, mae, _ = OSSOS[nome]
        guardar(nome, img, junta, mae)
    for slot, vs in VARIANTES.items():
        junta, mae, _ = OSSOS[slot]
        for var, (fonte, poli, junta_fonte) in vs.items():
            f = abrir(fonte)
            m = mascara(poli) & (f[..., 3] > 0)
            dx, dy = junta[0] - junta_fonte[0], junta[1] - junta_fonte[1]
            img = np.zeros_like(f)
            M = np.float32([[1, 0, dx], [0, 1, dy]])
            img = cv2.warpAffine(np.where(m[..., None], f, 0).astype(np.uint8), M, TELA, flags=cv2.INTER_NEAREST)
            guardar(f"{slot}_{var}", img, junta, mae, fonte=fonte,
                    fonte_img=cv2.warpAffine(f, M, TELA, flags=cv2.INTER_NEAREST))
            print(f"{slot}_{var}: de {fonte}")
    (PECAS / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")


def ler_kit():
    kit = json.loads((PECAS / "kit.json").read_text(encoding="utf-8"))
    for p in kit["pecas"].values():
        p["img"] = np.asarray(Image.open(PECAS / p["arquivo"]).convert("RGBA"))
        p["sob"] = np.asarray(Image.open(PECAS / p["sobra"]).convert("RGBA"))
    return kit


# ------------------------------------------------------------------ pose e desenho
def girar(p, piv, ang):
    r = np.radians(ang)
    x, y = p[0] - piv[0], p[1] - piv[1]
    return (piv[0] + x * np.cos(r) - y * np.sin(r), piv[1] + x * np.sin(r) + y * np.cos(r))


def chave(slot, pose):
    v = pose.get(slot, {}).get("var")
    return f"{slot}_{v}" if v else slot


def mundo(pose):
    """Junta e ângulo de cada osso na tela: a junta do filho vai junto com a mãe (gira e anda com ela) e só pode
    escorregar o `dx, dy` da pose (poucos pixels), então membro não descola."""
    out = {}

    def t(slot):
        if slot in out:
            return out[slot]
        junta, mae, _ = OSSOS[slot]
        p = pose.get(slot, {})
        if mae is None:
            pos, ang = (junta[0] + p.get("dx", 0), junta[1] + p.get("dy", 0)), p.get("ang", 0)
        else:
            mpos, mang = t(mae)
            mjunta = OSSOS[mae][0]
            est = pose.get(mae, {}).get("estica", 1)
            if abs(est - 1) > 0.01:  # mãe de borracha esticada: a junta do filho vai junto, na linha do osso da mãe
                ponta = OSSOS[mae][2]
                th = math.atan2(ponta[1] - mjunta[1], ponta[0] - mjunta[0])
                ux, uy = math.cos(th), math.sin(th)
                rx, ry = junta[0] - mjunta[0], junta[1] - mjunta[1]
                ao_longo = (rx * ux + ry * uy) * (est - 1)
                junta = (junta[0] + ux * ao_longo, junta[1] + uy * ao_longo)
            g = girar(junta, mjunta, mang)
            pos = (g[0] + mpos[0] - mjunta[0] + p.get("dx", 0), g[1] + mpos[1] - mjunta[1] + p.get("dy", 0))
            ang = mang + p.get("ang", 0)
        out[slot] = (pos, ang)
        return out[slot]

    for s in OSSOS:
        t(s)
    return out


def colocar(peca, img, origem, pos, ang):
    """(recorte girado, x0, y0) da peça com a junta em `pos`."""
    junta = peca["junta"]
    r, piv = rotsprite(img, ang, (junta[0] - origem[0], junta[1] - origem[1]))
    return r, int(round(pos[0] - piv[0])), int(round(pos[1] - piv[1]))


def colar(tela, r, x0, y0, so_vazio=False):
    h, w = r.shape[:2]
    X0, Y0 = max(0, x0), max(0, y0)
    X1, Y1 = min(tela.shape[1], x0 + w), min(tela.shape[0], y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return
    sub = tela[Y0:Y1, X0:X1]
    rr = r[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    m = rr[..., 3] > 0
    if so_vazio:
        m &= sub[..., 3] == 0
    sub[m] = rr[m]


def desenhar(kit, pose):
    w = mundo(pose)
    tela = np.zeros((TELA[1], TELA[0], 4), np.uint8)
    usados = []
    for slot in CAMADAS:
        if slot.startswith("canela_") and pose.get(slot.replace("canela", "coxa"), {}).get("var"):
            continue  # a perna levantada é um desenho só (coxa, canela e pé)
        p = kit["pecas"][chave(slot, pose)]
        pos, ang = w[slot]
        r, x0, y0 = colocar(p, p["img"], p["origem"], pos, ang)
        colar(tela, r, x0, y0)
        usados.append((p, pos, ang))
    # sobra das juntas: só pinta onde ficou buraco (nunca por cima de outra peça)
    for p, pos, ang in usados:
        r, x0, y0 = colocar(p, p["sob"], p["origem_sobra"], pos, ang)
        colar(tela, r, x0, y0, so_vazio=True)
    return tela


# ------------------------------------------------------------------ encaixe em cima do quadro de hoje
def custo(r, x0, y0, alvo):
    h, w = r.shape[:2]
    H, W = alvo.shape[:2]
    if x0 < 0 or y0 < 0 or x0 + w > W or y0 + h > H:
        return 1e9
    m = r[..., 3] > 0
    a = alvo[y0:y0 + h, x0:x0 + w]
    d = np.abs(a[..., :3].astype(int) - r[..., :3].astype(int)).mean(-1)
    d = np.where(a[..., 3] > 0, np.minimum(d, 120), 120)
    return d[m].mean()


BUSCA = {  # slot: (ângulos, folga da junta em px, variantes)
    "quadril": (range(-8, 9, 2), 30, [None]),
    "tronco": (range(-14, 15, 2), 3, [None]),
    "cabeca": (range(-14, 15, 2), 3, [None]),
    "braco_tras": (range(-30, 31, 3), 3, [None]),
    "braco_frente": (range(-45, 46, 3), 4, [None, "punho", "esticado"]),
    "coxa_tras": (range(-30, 31, 2), 2, [None]),
    "canela_tras": (range(-30, 31, 2), 2, [None]),
    "coxa_frente": (range(-30, 31, 2), 2, [None, "camara", "esticada"]),
    "canela_frente": (range(-30, 31, 2), 2, [None]),
}
# a perna levantada (variante) pode puxar o quadril: ela é buscada com folga grande e o corpo vem atrás dela
FOLGA_VARIANTE = {"coxa_frente": 16}
ANGULOS_VARIANTE = range(-20, 21, 2)
PESO_GIRO = 0.12  # custo por grau de giro (prefere a pose mais perto do parado quando o casamento empata)
ORDEM = ["quadril", "tronco", "cabeca", "braco_tras", "braco_frente", "coxa_tras", "canela_tras", "coxa_frente",
         "canela_frente"]


def encaixar(kit, alvo, pose=None, ordem=ORDEM):
    """Pose que leva as peças fixas para cima do quadro `alvo` (RGBA 3x), osso por osso, da raiz para as pontas."""
    pose = dict(pose or {})
    for slot in ordem:
        angs0, folga0, vars_ = BUSCA[slot]
        if slot.startswith("canela_") and pose.get(slot.replace("canela", "coxa"), {}).get("var"):
            continue
        melhor = None
        for var in vars_:
            angs = ANGULOS_VARIANTE if var else angs0
            folga = FOLGA_VARIANTE.get(slot, folga0) if var else folga0
            tent = dict(pose)
            p = kit["pecas"][f"{slot}_{var}" if var else slot]
            for ang in angs:
                tent[slot] = {"ang": ang, "var": var} if var else {"ang": ang}
                pos, a_mundo = mundo(tent)[slot]
                r, x0, y0 = colocar(p, p["img"], p["origem"], pos, a_mundo)
                passo = 3 if folga > 6 else 1
                giro = 0 if slot == "quadril" else PESO_GIRO * abs(ang)
                for dy in range(-folga, folga + 1, passo):
                    for dx in range(-folga, folga + 1, passo):
                        c = custo(r, x0 + dx, y0 + dy, alvo) + giro
                        if melhor is None or c < melhor[0]:
                            melhor = (c, var, ang, dx, dy)
        c, var, ang, dx, dy = melhor
        folga = FOLGA_VARIANTE.get(slot, folga0) if var else folga0
        if folga > 6:  # refina a translação de 1 em 1
            tent = dict(pose)
            p = kit["pecas"][f"{slot}_{var}" if var else slot]
            for ang2 in (ang - 1, ang, ang + 1):
                tent[slot] = {"ang": ang2, "var": var} if var else {"ang": ang2}
                pos, a_mundo = mundo(tent)[slot]
                r, x0, y0 = colocar(p, p["img"], p["origem"], pos, a_mundo)
                for ddy in range(dy - 2, dy + 3):
                    for ddx in range(dx - 2, dx + 3):
                        c2 = custo(r, x0 + ddx, y0 + ddy, alvo)
                        if c2 < c:
                            c, ang, dx, dy = c2, ang2, ddx, ddy
        pose[slot] = {"ang": ang, "dx": dx, "dy": dy}
        if var:
            pose[slot]["var"] = var
        pose[slot]["custo"] = round(float(c), 1)
    # perna levantada fora do lugar: o quadril (e o corpo todo) vai até ela, e a perna fica presa na junta
    v = pose.get("coxa_frente", {})
    if v.get("var") and (abs(v.get("dx", 0)) > 2 or abs(v.get("dy", 0)) > 2) and ordem is ORDEM:
        q = dict(pose["quadril"])
        q["dx"] += v["dx"]
        q["dy"] += v["dy"]
        nova = {"quadril": q, "coxa_frente": dict(v, dx=0, dy=0)}
        return encaixar(kit, alvo, nova, ["tronco", "cabeca", "braco_tras", "braco_frente", "coxa_tras",
                                          "canela_tras"])
    return pose
