#!/usr/bin/env python3
"""Gbzin pelo boneco de peças, no jeito "corpo firme + vida" que o Alisson aprovou no Pengaró (16/11).

O Gbzin tinha dois bonecos: 17 golpes vieram do ChatGPT com outra pele (laranja), sem barba e com a franja nos olhos.
Aqui o corpo inteiro sai de um desenho só, o parado certo (referencia_ginga/00, do conceito v3): cabeça, tronco,
calção, braços e pernas são peças desse desenho, giradas nas juntas com RotSprite em cor cheia. Nada de paleta reduzida.

  python ferramentas/gbzin_pecas.py kit             recorta o kit em sprites/gbzin/pecas/ e grava a conferência
                                                    docs/boneco-pecas/gbzin/kit_conferencia.png
  python ferramentas/gbzin_pecas.py animar [NOMES]  monta as animações em quadros_pecas_hd/ e quadros_pecas/ (1x),
                                                    com tempos.json e o robô de defeitos

Peças: cabeça (com o pescoço escondido por baixo do tronco), tronco (com a faixa marrom amarrada), calção, braço de
trás (com o cajado na mão), braço da frente, coxa e canela de cada lado, pé de cada lado (sempre reto) e as pontas da
faixa, que balançam atrás do quadril. Peças que mudam de desenho e não de ângulo (mão do tapa, mão recolhida) são
variantes recortadas dos desenhos rosados aprovados. Desenho laranja nunca entra no kit: dele só se aproveita a pose.
"""
import json
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import boneco_ajuste as b  # noqa: E402
import piloto_firme as pf  # noqa: E402
import vida_pecas as vida  # noqa: E402

RAIZ = AQUI.parent
SPR = RAIZ / "sprites" / "gbzin"
DOCS = RAIZ / "docs" / "boneco-pecas" / "gbzin"
REF = "referencia_ginga/00"
CINTO = 487        # linha de baixo da faixa amarrada: acima é tronco, abaixo é calção e pernas
CHAO = 659         # pixel mais baixo do tênis no parado (3x)

# ------------------------------------------------------------------ desenho laranja -> cores do Gbzin certo
# os desenhos laranja têm as mesmas 15 cores em outro tom; a troca é 1 para 1 (pele, sombra, calção, regata, faixa)
LARANJA_PARA_ROSADO = {
    (240, 168, 77): (252, 183, 140), (252, 186, 135): (252, 183, 140), (231, 119, 87): (238, 140, 120),
    (212, 83, 72): (220, 82, 94), (144, 43, 54): (149, 44, 65), (90, 28, 43): (101, 29, 53),
    (76, 26, 51): (76, 23, 53), (191, 88, 55): (194, 88, 55), (57, 47, 95): (55, 48, 88),
    (36, 28, 58): (39, 33, 64), (164, 139, 185): (165, 140, 188), (253, 241, 252): (241, 231, 237),
    (75, 56, 86): (74, 58, 84), (216, 190, 221): (210, 188, 217),
}


def rosado(img):
    out = img.copy()
    chave = img[..., :3]
    for de, para in LARANJA_PARA_ROSADO.items():
        m = np.all(chave == de, -1) & (img[..., 3] > 0)
        out[m, :3] = para
    return out


def sem_grade(img):
    """Tira as linhas retas finas que sobraram da grade da folha (1 a 3 px de largura, longe do corpo)."""
    al = (img[..., 3] > 0).astype(np.uint8)
    corpo = cv2.morphologyEx(al, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    corpo = cv2.dilate(corpo, np.ones((5, 5), np.uint8))
    out = img.copy()
    out[(al > 0) & (corpo == 0)] = 0
    return pf.sem_migalha(out, minimo=30)


_PALETA = None


def paleta():
    global _PALETA
    if _PALETA is None:
        r = np.array(Image.open(SPR / "quadros_arcade_hd" / f"{REF}.png").convert("RGBA"))
        _PALETA = np.unique(r[r[..., 3] > 0][:, :3], axis=0).astype(int)
    return _PALETA


def quantizar(img):
    """Toda cor fora das 15 do parado (pintura por baixo, borda de giro) vira a mais perto delas: paleta travada."""
    out = img.copy()
    al = out[..., 3] > 0
    px = out[al][:, :3].astype(int)
    pal = paleta()
    d = ((px[:, None, :] - pal[None, :, :]) ** 2).sum(-1)
    out[al, :3] = pal[d.argmin(1)]
    out[..., 3] = np.where(al, 255, 0)
    return out


def abrir(nome):
    img = np.array(Image.open(SPR / "quadros_arcade_hd" / f"{nome}.png").convert("RGBA"))
    return sem_grade(rosado(img))


# ------------------------------------------------------------------ kit (coordenadas do referencia_ginga/00, 3x)
CABECA = [(529, 320), (608, 320), (608, 372), (600, 380), (592, 387), (582, 392), (570, 392), (560, 388),
          (550, 378), (540, 368), (529, 364)]
PESCOCO = [(548, 370), (566, 386), (586, 391), (592, 400), (562, 404), (544, 394), (538, 380)]
BRACO_FRENTE = [(579, 392), (592, 387), (601, 395), (604, 404), (611, 396), (626, 390), (646, 392), (659, 400),
                (659, 430), (643, 436), (628, 441), (622, 456), (606, 470), (582, 470), (570, 462), (569, 446),
                (574, 439), (577, 424), (578, 408)]
# braço de trás com o cajado (gancho por cima da regata, haste saindo por baixo da mão)
BRACO_TRAS = [(468, 372), (500, 362), (517, 364), (520, 378), (519, 398), (514, 412), (506, 422), (490, 428),
              (480, 432), (479, 446), (487, 456), (493, 470), (494, 489), (481, 495), (458, 495), (442, 487),
              (435, 466), (433, 430), (437, 410), (449, 392)]
GANCHO = [(474, 429), (500, 427), (519, 433), (526, 448), (524, 470), (511, 472), (504, 463), (500, 447),
          (490, 441), (481, 447)]
HASTE = [(430, 500), (448, 487), (463, 478), (472, 490), (456, 506), (443, 527), (429, 527)]
PERNA_TRAS = [(462, 527), (523, 529), (526, 546), (511, 575), (493, 600), (479, 622), (489, 640), (489, 663),
              (430, 663), (432, 640), (443, 622), (445, 580), (456, 553)]
# perna da frente com a boca do calção (o calção da frente sobe junto quando a coxa levanta)
PERNA_FRENTE = [(548, 556), (566, 548), (575, 528), (574, 505), (590, 500), (607, 512), (626, 545), (627, 580),
                (612, 600), (606, 621), (642, 629), (655, 645), (655, 663), (569, 663), (572, 640), (581, 622),
                (583, 597), (577, 580), (566, 565)]
PONTAS_FAIXA = [(522, 487), (563, 487), (563, 546), (541, 549), (522, 542)]
# o que fica por baixo dos braços no parado (tapado no kit, para não abrir buraco quando o braço sai)
PEITO_ESCONDIDO = [(562, 392), (577, 394), (581, 405), (580, 425), (576, 445), (571, 462), (560, 467)]
LADO_ESCONDIDO = [(476, 368), (531, 368), (531, 410), (526, 470), (478, 470)]
CALCA_ESCONDIDA = [(458, 487), (497, 487), (497, 530), (462, 530)]

JOELHO_TRAS, JOELHO_FRENTE = (466, 580), (601, 582)
TORNOZELO = {"canela_tras": (459, 622), "canela_frente": (592, 622)}
OSSOS = {  # junta (pivô) no parado, peça mãe, ponta (régua)
    "quadril": ((540, 500), None, (540, 530)),
    "tronco": ((540, 487), "quadril", (560, 395)),
    "cabeca": ((568, 392), "tronco", (568, 335)),
    "braco_tras": ((506, 397), "tronco", (466, 482)),
    "braco_frente": ((586, 404), "tronco", (632, 410)),
    "coxa_tras": ((496, 535), "quadril", JOELHO_TRAS),
    "canela_tras": (JOELHO_TRAS, "coxa_tras", TORNOZELO["canela_tras"]),
    "coxa_frente": ((585, 532), "quadril", JOELHO_FRENTE),
    "canela_frente": (JOELHO_FRENTE, "coxa_frente", TORNOZELO["canela_frente"]),
}
CAMADAS = ["cabeca", "tronco", "coxa_tras", "canela_tras", "canela_frente", "coxa_frente", "quadril", "braco_tras",
           "braco_frente"]
# variantes (desenho rosado de onde sai, polígono nesse desenho); a junta no desenho de origem sai do casamento do tronco
VARIANTES = {
    "braco_frente": {
        "recolhido": ("soco/01", [(572, 388), (590, 381), (606, 381), (619, 393), (624, 410), (622, 433),
                                  (614, 453), (600, 457), (584, 453), (571, 446), (563, 431), (562, 412),
                                  (566, 398)]),
        "tapa": ("soco/02", [(546, 377), (575, 376), (600, 381), (627, 379), (633, 364), (642, 351), (655, 347),
                             (666, 354), (671, 375), (663, 392), (646, 401), (628, 403), (605, 409), (585, 413),
                             (565, 417), (549, 413), (541, 398)]),
    },
}
SOBRA = 9


def mascara(poli):
    m = Image.new("L", b.TELA, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in poli], fill=255)
    return np.array(m) > 0


def configurar():
    """Aponta o boneco_ajuste e o piloto_firme para o Gbzin (as funções deles leem estes nomes)."""
    b.SPR, b.HD, b.PECAS, b.REF = SPR, SPR / "quadros_arcade_hd", SPR / "pecas", REF
    b.OSSOS, b.CAMADAS = OSSOS, CAMADAS
    b.abrir = abrir
    pf.TORNOZELO, pf.CHAO, pf.PES_REF = TORNOZELO, CHAO, None


CORES_CAJADO = {(194, 88, 55), (149, 44, 65), (246, 171, 81), (101, 29, 53), (76, 23, 53), (22, 20, 36),
                (252, 183, 140), (238, 140, 120)}


def so_cores(img, m, cores):
    rgb = img[..., :3]
    ok = np.zeros(m.shape, bool)
    for c in cores:
        ok |= np.all(rgb == c, -1)
    return m & ok


def tapar(img, regiao, dono):
    return b.tapar(img, regiao, dono)


REGATA, REGATA_SOMBRA, CONTORNO = (55, 48, 88), (39, 33, 64), (22, 20, 36)


def forrar(img, regiao, ref):
    """O que os braços escondem no tronco vira regata lisa (cor chapada, sem borrão de inpaint), com sombra perto do
    braço e o contorno escuro só na beira de fora da figura. Tira também o contorno do gancho que ficou no tronco."""
    out = img.copy()
    al = out[..., 3] > 0
    reg = regiao & al
    rgb = out[..., :3].astype(int)
    # dentro da região: tudo vira regata, menos a faixa (marrom) que já é do desenho
    faixa = so_cores(out, reg, {(194, 88, 55), (149, 44, 65), (220, 82, 94), (101, 29, 53), (76, 23, 53)})
    faixa &= np.mgrid[:out.shape[0], :out.shape[1]][0] >= 462
    alvo = reg & ~faixa
    out[alvo, :3] = REGATA
    perto = cv2.dilate((regiao & ~al).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    out[alvo & perto, :3] = REGATA_SOMBRA
    borda = al & ~(cv2.erode(al.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    out[borda & reg, :3] = CONTORNO
    del rgb
    return out


def montar_kit():
    configurar()
    pecas = SPR / "pecas"
    if pecas.exists():
        shutil.rmtree(pecas)
    pecas.mkdir(parents=True)
    ref = abrir(REF)
    alfa = ref[..., 3] > 0
    yy, xx = np.mgrid[:b.TELA[1], :b.TELA[0]]
    baixo = yy >= CINTO
    m_cab = mascara(CABECA)
    gancho = so_cores(ref, mascara(GANCHO), CORES_CAJADO - {(252, 183, 140), (238, 140, 120)})
    # o contorno escuro do gancho só conta colado na madeira (o buraco do gancho é regata e fica no tronco)
    madeira = so_cores(ref, mascara(GANCHO), CORES_CAJADO - {(22, 20, 36), (252, 183, 140), (238, 140, 120)})
    perto = cv2.dilate(madeira.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    gancho &= perto
    m_bt = ((mascara(BRACO_TRAS) | mascara(HASTE)) & alfa) | gancho
    m_bf = mascara(BRACO_FRENTE) & alfa & ~m_bt
    pontas = mascara(PONTAS_FAIXA) & baixo & alfa
    # calção branco e lilás não é faixa
    rgb = ref[..., :3].astype(int)
    branco = (rgb.min(-1) > 150) & (np.ptp(rgb, -1) < 90)
    pontas &= ~branco & ~so_cores(ref, pontas, {(165, 140, 188), (210, 188, 217), (241, 231, 237)})
    pontas = cv2.morphologyEx(pontas.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)) > 0
    pt = baixo & ~m_bt & mascara(PERNA_TRAS) & alfa
    pfr = baixo & ~m_bt & mascara(PERNA_FRENTE) & alfa & ~pontas
    # o que sobra embaixo do calção (beira de dentro da panturrilha) é da perna mais perto, nunca do calção
    resto = baixo & alfa & ~m_bt & ~pt & ~pfr & (yy > 556)
    pfr |= resto & (xx >= 540)
    pt |= resto & (xx < 540)
    partes = {
        "cabeca": (m_cab | mascara(PESCOCO)) & ~m_bf & ~m_bt & alfa,
        "braco_tras": m_bt,
        "braco_frente": m_bf,
        "tronco": ~baixo & ~m_bt & ~m_cab & ~m_bf & alfa,
        "coxa_tras": pt & (yy < JOELHO_TRAS[1]),
        "canela_tras": pt & (yy >= JOELHO_TRAS[1] - 12),
        "coxa_frente": pfr & (yy < JOELHO_FRENTE[1]),
        "canela_frente": pfr & (yy >= JOELHO_FRENTE[1] - 12),
    }
    partes["quadril"] = baixo & ~m_bt & ~pt & ~pfr & alfa  # inclui as pontas da faixa: tapadas logo abaixo
    imgs = {k: np.where(m[..., None], ref, 0).astype(np.uint8) for k, m in partes.items()}
    peito = mascara(PEITO_ESCONDIDO) & ~baixo
    imgs["tronco"] = tapar(np.where((partes["tronco"] | peito)[..., None], ref, 0).astype(np.uint8), peito,
                           partes["tronco"])
    lado = mascara(LADO_ESCONDIDO) & m_bt & ~baixo
    imgs["tronco"] = tapar(imgs["tronco"], lado, imgs["tronco"][..., 3] > 0)
    canto = mascara([(466, 425), (482, 425), (482, 487), (466, 487)])
    t = imgs["tronco"]
    novo = peito & (t[..., 3] == 0)
    t[novo] = (*REGATA, 255)  # o flanco que o bíceps tapava ganha forma lisa
    imgs["tronco"] = forrar(t, peito | lado | ((mascara(GANCHO) | canto) & ~baixo), ref)
    calca = mascara(CALCA_ESCONDIDA) & m_bt & baixo
    imgs["quadril"] = tapar(imgs["quadril"], calca, partes["quadril"])
    # as pontas da faixa saem do calção (vão por cima, balançando): o calção atrás delas é pintado por baixo
    q = imgs["quadril"]
    fechado = cv2.morphologyEx(((q[..., 3] > 0) & ~pontas).astype(np.uint8), cv2.MORPH_CLOSE,
                               np.ones((15, 15), np.uint8)) > 0
    q2 = tapar(np.where((~pontas)[..., None], q, 0).astype(np.uint8), pontas & fechado, (q[..., 3] > 0) & ~pontas)
    imgs["quadril"] = q2
    kit = {"ref": f"quadros_arcade_hd/{REF}.png", "pecas": {}}

    def guardar(nome, img, junta, mae, fonte_img, fonte, sobra_propria=False):
        img = quantizar(pf.sem_migalha(img, minimo=80))
        if sobra_propria:
            fonte_img = img
        a = img[..., 3] > 0
        ys, xs = np.nonzero(a)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        Image.fromarray(img[y0:y1, x0:x1]).save(pecas / f"{nome}.png")
        disco = np.zeros(b.TELA[::-1], np.uint8)
        raio = 16 if nome.startswith("coxa") else SOBRA  # a coxa gira muito no chute: sobra maior no quadril
        cv2.circle(disco, (int(junta[0]), int(junta[1])), raio, 1, -1)
        sob = np.where((disco.astype(bool) & (fonte_img[..., 3] > 0))[..., None], fonte_img, 0).astype(np.uint8)
        sob = sob[y0 - SOBRA:y1 + SOBRA, x0 - SOBRA:x1 + SOBRA]
        Image.fromarray(sob).save(pecas / f"{nome}_sobra.png")
        kit["pecas"][nome] = {"arquivo": f"{nome}.png", "origem": [int(x0), int(y0)], "junta": list(junta),
                              "mae": mae, "fonte": f"quadros_arcade_hd/{fonte}.png",
                              "sobra": f"{nome}_sobra.png", "origem_sobra": [int(x0 - SOBRA), int(y0 - SOBRA)]}

    for nome, img in imgs.items():
        junta, mae, _ = OSSOS[nome]
        guardar(nome, img, junta, mae, ref, REF)
    # furos do desenho (vão entre o braço e o corpo, entre o queixo e o ombro): ficam vazios mesmo quando o
    # fechamento de frestas age perto da junta. Cada furo vai com a peça mais perto dele.
    fech = cv2.morphologyEx(alfa.astype(np.uint8), cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))) > 0
    furos = fech & ~alfa
    dist = {k: cv2.distanceTransform((~m).astype(np.uint8), cv2.DIST_L2, 3) for k, m in partes.items()}
    dono = np.argmin(np.stack([dist[k] for k in partes]), 0)
    for i, nome in enumerate(partes):
        f = furos & (dono == i)
        if not f.any():
            continue
        p = kit["pecas"][nome]
        x0, y0 = p["origem"]
        h, w_ = np.asarray(Image.open(pecas / p["arquivo"])).shape[:2]
        sub = np.zeros((h, w_, 4), np.uint8)
        ff = f[y0:y0 + h, x0:x0 + w_]
        sub[ff] = (255, 0, 255, 255)
        Image.fromarray(sub).save(pecas / f"{nome}_furo.png")
        p["furo"] = f"{nome}_furo.png"
    # pontas da faixa: peça solta, presa no nó
    pont = np.where(pontas[..., None], ref, 0).astype(np.uint8)
    ys, xs = np.nonzero(pontas)
    Image.fromarray(pont[ys.min():ys.max() + 1, xs.min():xs.max() + 1]).save(pecas / "pontas_faixa.png")
    kit["pontas_faixa"] = {"arquivo": "pontas_faixa.png", "origem": [int(xs.min()), int(ys.min())],
                           "no": [float(xs.mean()), float(ys.min())]}
    # variantes do braço da frente: a junta no desenho de origem vem do casamento do tronco
    kit_tmp = {"pecas": {"tronco": {"img": imgs["tronco"][partes["tronco"].any(1)][:, partes["tronco"].any(0)]}}}
    ys, xs = np.nonzero(imgs["tronco"][..., 3] > 0)
    kit_tmp["pecas"]["tronco"]["img"] = imgs["tronco"][ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    kit_tmp["pecas"]["tronco"]["origem"] = [int(xs.min()), int(ys.min())]
    for slot, vs in VARIANTES.items():
        junta, mae, _ = OSSOS[slot]
        for var, (fonte, poli) in vs.items():
            f = abrir(fonte)
            dx, dy = corpo(kit_tmp, f)
            m = mascara(poli) & (f[..., 3] > 0)
            M = np.float32([[1, 0, -dx], [0, 1, -dy]])
            img = cv2.warpAffine(np.where(m[..., None], f, 0).astype(np.uint8), M, b.TELA, flags=cv2.INTER_NEAREST)
            guardar(f"{slot}_{var}", img, junta, mae, None, fonte, sobra_propria=True)
            print(f"{slot}_{var}: de {fonte} (corpo a {dx:+d},{dy:+d})")
    (pecas / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")
    conferencia_kit(partes, pontas)


FOLGA_CORPO = 60


def corpo(kit, alvo):
    """(dx, dy) do tronco do kit no quadro: casamento só por translação, nos ombros e no peito."""
    p = kit["pecas"]["tronco"]
    t = p["img"]
    x0, y0 = p["origem"]
    h, w = t.shape[:2]
    X0, Y0 = max(0, x0 - FOLGA_CORPO), max(0, y0 - FOLGA_CORPO)
    reg = alvo[Y0:y0 + h + FOLGA_CORPO, X0:x0 + w + FOLGA_CORPO]
    # só os pixels do tronco que aparecem no parado (o que foi tapado por baixo dos braços não conta)
    refp = abrir(REF)[y0:y0 + h, x0:x0 + w]
    m = ((t[..., 3] > 0) & np.all(refp == t, -1)).astype(np.float32)
    m[462 - y0:] = 0
    r = cv2.matchTemplate(pf.cinza(reg), pf.cinza(t), cv2.TM_SQDIFF, mask=np.ascontiguousarray(np.repeat(m[..., None], 3, -1)))
    _, _, p_min, _ = cv2.minMaxLoc(r)
    return p_min[0] + X0 - x0, p_min[1] + Y0 - y0


CORES_CONF = {"cabeca": (255, 80, 80), "tronco": (80, 160, 255), "braco_tras": (80, 220, 120),
              "braco_frente": (240, 200, 60), "coxa_tras": (200, 90, 220), "canela_tras": (140, 60, 160),
              "coxa_frente": (60, 220, 220), "canela_frente": (30, 140, 140), "quadril": (240, 240, 240)}


def conferencia_kit(partes, pontas):
    DOCS.mkdir(parents=True, exist_ok=True)
    ref = abrir(REF)
    cor = np.zeros_like(ref)
    for k, m in partes.items():
        cor[m, :3] = CORES_CONF[k]
        cor[m, 3] = 255
    cor[pontas, :3] = (255, 140, 0)
    cor[pontas, 3] = 255
    x0, y0, x1, y1 = 420, 310, 670, 670
    a = Image.fromarray(ref).crop((x0, y0, x1, y1))
    c = Image.fromarray(cor).crop((x0, y0, x1, y1))
    mist = Image.blend(Image.new("RGBA", a.size, (60, 60, 70, 255)), a, 1.0)
    bg = Image.new("RGBA", a.size, (60, 60, 70, 255))
    bg.alpha_composite(a)
    over = Image.blend(bg, Image.alpha_composite(Image.new("RGBA", a.size, (60, 60, 70, 255)), c), 0.55)
    folha = Image.new("RGB", (a.width * 4, a.height * 2), (40, 40, 48))
    folha.paste(bg.convert("RGB").resize((a.width * 2, a.height * 2), Image.NEAREST), (0, 0))
    folha.paste(over.convert("RGB").resize((a.width * 2, a.height * 2), Image.NEAREST), (a.width * 2, 0))
    folha.save(DOCS / "kit_conferencia.png")
    del mist


# ------------------------------------------------------------------ montagem
def ler_kit():
    configurar()
    kit = b.ler_kit()
    pec = SPR / "pecas"
    pt = kit["pontas_faixa"]
    pt["img"] = np.asarray(Image.open(pec / pt["arquivo"]).convert("RGBA"))
    cab = kit["pecas"]["cabeca"]
    ox, oy = cab["origem"]
    h, w_ = cab["img"].shape[:2]
    topo = np.zeros_like(cab["img"])
    mt = mascara(CABECA)[oy:oy + h, ox:ox + w_]
    topo[mt] = cab["img"][mt]
    kit["topo"] = topo
    for p in kit["pecas"].values():
        if "furo" in p:
            p["furo_img"] = np.asarray(Image.open(pec / p["furo"]).convert("RGBA"))
    kit["pes"] = {}
    for slot, (tx, ty) in TORNOZELO.items():
        p = kit["pecas"][slot]
        img = p["img"].copy()
        ox, oy = p["origem"]
        corte = ty - oy
        pe = np.zeros_like(img)
        pe[corte:] = img[corte:]
        img[corte + 4:] = 0  # 4 linhas de sobra: a canela cobre o começo do tênis, sem fresta
        p["img"] = img
        ys = np.nonzero(pe[..., 3].any(1))[0]
        kit["pes"][slot] = {"img": pe, "origem": (ox, oy), "tornozelo": (tx, ty), "fundo": int(ys.max()),
                            "chao": int(ys.max()) + oy}
    return kit


def desenhar(kit, pose):
    """Peças nas juntas (RotSprite em cor cheia), sobra só em buraco, pés retos no chão e pontas da faixa por cima."""
    w = b.mundo(pose)
    tela = np.zeros((b.TELA[1], b.TELA[0], 4), np.uint8)
    usados = []
    bx = pose.get("_baixo")
    if bx:
        q = pose.get("quadril", {})
        img = baixo_da_fonte(kit, bx["var"], int(bx["dy"]), pose)
        sx, sy = int(round(q.get("dx", 0) - bx["dx"])), int(round(q.get("dy", 0) - bx["dy"]))
        b.colar(tela, img, sx, sy)
    for slot in CAMADAS:
        if bx and slot in ("quadril", "coxa_tras", "canela_tras", "coxa_frente", "canela_frente"):
            continue
        p = kit["pecas"][b.chave(slot, pose)]
        pos, ang = w[slot]
        r, x0, y0 = b.colocar(p, p["img"], p["origem"], pos, ang)
        b.colar(tela, r, x0, y0)
        usados.append((p, pos, ang))
        if slot == "canela_frente":  # o tênis de trás vai antes da perna da frente
            pass
    for p, pos, ang in usados:
        r, x0, y0 = b.colocar(p, p["sob"], p["origem_sobra"], pos, ang)
        b.colar(tela, r, x0, y0, so_vazio=True)
    # a cabeça (sem o pescoço) vai por cima do braço da frente: o braço do tapa passa embaixo do queixo
    cab = kit["pecas"][b.chave("cabeca", pose)]
    if "topo" in kit:
        pos, ang = w["cabeca"]
        r, x0, y0 = b.colocar(cab, kit["topo"], cab["origem"], pos, ang)
        b.colar(tela, r, x0, y0)
    furo = np.zeros_like(tela)
    for p, pos, ang in usados:
        if "furo_img" in p:
            r, x0, y0 = b.colocar(p, p["furo_img"], p["origem"], pos, ang)
            b.colar(furo, r, x0, y0)
    for slot in (() if bx else ("canela_tras", "canela_frente")):
        joelho, ang = w[slot]
        jr = OSSOS[slot][0]
        pe = kit["pes"][slot]
        giro_pe = pose.get(slot, {}).get("pe", None)
        t = b.girar(pe["tornozelo"], jr, ang)
        tx, ty = t[0] + joelho[0] - jr[0], t[1] + joelho[1] - jr[1]
        if giro_pe is None:  # pé no chão: fica reto
            x0 = int(round(pe["origem"][0] + tx - pe["tornozelo"][0]))
            y0 = int(round(pe["origem"][1] + ty - pe["tornozelo"][1]))
            fundo = pe["fundo"] + y0
            if abs(fundo - pe["chao"]) <= 10:  # cada tênis encosta no chão dele no parado
                y0 += pe["chao"] - fundo
            b.colar(tela, pe["img"], x0, y0, so_vazio=(slot == "canela_tras"))
        else:  # pé no ar: gira com a canela mais o giro próprio (sola para a frente no chute)
            piv = (pe["tornozelo"][0] - pe["origem"][0], pe["tornozelo"][1] - pe["origem"][1])
            r, piv2 = b.rotsprite(pe["img"], ang + giro_pe, piv)
            b.colar(tela, r, int(round(tx - piv2[0])), int(round(ty - piv2[1])))
    if bx:
        antes = tela[..., 3] > 0
        tela = pf.fechar_frestas(tela, juntas=[w[sl][0] for sl in ("tronco", "cabeca", "braco_tras",
                                                                     "braco_frente")])
        tela[(tela[..., 3] > 0) & ~antes & (furo[..., 3] > 0)] = 0
        return quantizar(pf.sem_migalha(tela))
    # pontas da faixa: penduradas no nó, atrás do movimento do quadril
    pt = kit["pontas_faixa"]
    bo = pose.get("_bolinhas", {})
    (qx, qy), qang = w["quadril"]
    tr_dx = pose.get("tronco", {}).get("dx", 0)
    tr_dy = pose.get("tronco", {}).get("dy", 0)
    jq = OSSOS["quadril"][0]
    no = b.girar(pt["no"], jq, qang)
    no = (no[0] + qx - jq[0] + bo.get("dx", 0) + tr_dx * 0, no[1] + qy - jq[1] + bo.get("dy", 0))
    piv = (pt["no"][0] - pt["origem"][0], pt["no"][1] - pt["origem"][1])
    r, piv2 = b.rotsprite(pt["img"], qang + bo.get("ang", 0), piv)
    b.colar(tela, r, int(round(no[0] - piv2[0])), int(round(no[1] - piv2[1])))
    antes = tela[..., 3] > 0
    tela = pf.fechar_frestas(tela, juntas=[w[sl][0] for sl in OSSOS])
    tela[(tela[..., 3] > 0) & ~antes & (furo[..., 3] > 0)] = 0
    return quantizar(pf.sem_migalha(tela))


# ------------------------------------------------------------------ poses
# o que o jogo mostra hoje em cada elemento (sprite do .sff -> quadro de origem, casado pela silhueta)
ATUAL = {
    "parado": [(f"referencia_ginga/{i:02d}", 5) for i in range(8)],
    "soco": [("soco/01", 4), ("soco/02", 6), ("soco/03", 3), ("soco/07", 6)],
    "chute_alto": [("chute_alto/01", 5), ("chute_alto/02", 4), ("chute_alto/04", 6), ("chute_alto/05", 3),
                   ("chute_alto/06", 12), ("chute_alto/07", 12)],
}
ACAO = {"parado": 0, "soco": 200, "chute_alto": 240}
# elemento que bate (índice em ATUAL) e caixa de acerto do .air de hoje
CAIXA = {"soco": (1, (30, -297, 150, -219)), "chute_alto": (2, (30, -240, 108, -156))}
VARIANTES_GOLPE = {"soco": [None, "recolhido", "tapa"]}


def pose_de(kit, q, nome):
    """Pose-chave que leva as peças fixas para cima do desenho de hoje (só desenhos rosados)."""
    alvo = abrir(q)
    dx, dy = corpo(kit, alvo)
    if nome == "parado":
        b.BUSCA["braco_tras"] = (range(-9, 10, 3), 3, [None])
        b.BUSCA["braco_frente"] = (range(-12, 13, 3), 3, [None])
    else:
        b.BUSCA["braco_tras"] = (range(-30, 31, 3), 3, [None])
        b.BUSCA["braco_frente"] = (range(-45, 46, 3), 4, VARIANTES_GOLPE.get(nome, [None]))
    pose = {"quadril": {"ang": 0, "dx": dx, "dy": dy}}
    if nome != "parado":  # a cabeça acompanha o golpe (mesmo desenho, só vai junto com o corpo)
        b.BUSCA["cabeca"] = (range(-8, 9, 2), 8, [None])
        pose = b.encaixar(kit, alvo, pose, ordem=["cabeca"])
    pose = b.encaixar(kit, alvo, pose, ordem=["braco_tras", "braco_frente"])
    # calção e pernas: o desenho de hoje (rosado, ou laranja trocado de cor), preso embaixo da faixa do kit.
    # As pernas do kit dobradas no joelho quebravam o desenho na ginga funda (joelho aberto, boca do calção abrindo).
    pose["_baixo"] = {"var": q, "dx": dx, "dy": dy}
    if q in PASSO:  # golpe com o corpo: o quadril vai junto e o pé da frente dá o passo (pernas de outro desenho)
        pq = PASSO[q]
        pdx, pdy = corpo(kit, abrir(pq))
        pose["quadril"] = dict(pose["quadril"], dx=pdx, dy=pdy)
        pose["_baixo"] = {"var": pq, "dx": pdx, "dy": pdy}
    return pose


# Regra do Alisson (17/11): soco não é só esticar o braço. No tapa o corpo desce e vai para a frente com o passo do
# soco/04 (pé da frente avança, quadril gira junto); na volta passa pela base do soco/06 antes da guarda.
PASSO = {"soco/02": "soco/04", "soco/03": "soco/06"}


_BAIXO = {}


def baixo_da_fonte(kit, q, dy, pose):
    """Calção e pernas do desenho q (abaixo da faixa), sem o cajado e a mão de trás (que são do kit)."""
    chave = (q, dy, round(pose.get("braco_tras", {}).get("ang", 0), 1))
    if chave in _BAIXO:
        return _BAIXO[chave]
    src = abrir(q)
    corte = CINTO + dy - 4
    out = src.copy()
    out[:corte] = 0
    # tira o braço de trás e o cajado do desenho de hoje (o do kit vai por cima)
    w = b.mundo(pose)
    p = kit["pecas"][b.chave("braco_tras", pose)]
    pos, ang = w["braco_tras"]
    r, x0, y0 = b.colocar(p, p["img"], p["origem"], pos, ang)
    m = np.zeros_like(src)
    b.colar(m, r, x0, y0)
    tira = cv2.dilate((m[..., 3] > 0).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    madeira = so_cores(src, np.ones(src.shape[:2], bool), {(194, 88, 55), (246, 171, 81), (252, 183, 140),
                                                            (238, 140, 120), (22, 20, 36), (101, 29, 53),
                                                            (149, 44, 65), (76, 23, 53), (220, 82, 94)})
    yy, xx = np.mgrid[:src.shape[0], :src.shape[1]]
    perto_mao = cv2.dilate(tira.astype(np.uint8), np.ones((31, 31), np.uint8)) > 0
    tira |= madeira & perto_mao & (xx < pos[0] - 10)  # haste e mão que sobram à esquerda
    tira &= out[..., 3] > 0
    al = (out[..., 3] > 0) & ~tira
    fech = cv2.morphologyEx(al.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8)) > 0
    tapa = tira & fech
    pint = cv2.inpaint(np.ascontiguousarray(out[..., :3]), (tira | (out[..., 3] == 0)).astype(np.uint8), 3,
                       cv2.INPAINT_TELEA)
    out[tira] = 0
    out[tapa, :3] = pint[tapa]
    out[tapa, 3] = 255
    out = pf.sem_migalha(out, minimo=40)
    _BAIXO[chave] = out
    return out


def gravar(kit, nome, quadros, cx):
    for pasta in ("quadros_pecas_hd", "quadros_pecas"):
        shutil.rmtree(SPR / pasta / nome, ignore_errors=True)
        (SPR / pasta / nome).mkdir(parents=True)
    relatorio = []
    originais = {}
    for i, (pose, t, caixa_on, q) in enumerate(quadros):
        out = desenhar(kit, pose)
        if q not in originais:
            originais[q] = abrir(q)
        erros = pf.conferir(out, originais[q], None)
        relatorio.append(f"| {nome}/{i:02d} | {q} | {'PASS' if not erros else 'FAIL ' + '; '.join(erros)} |")
        Image.fromarray(out).save(SPR / "quadros_pecas_hd" / nome / f"{i:02d}.png")
        Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(SPR / "quadros_pecas" / nome / f"{i:02d}.png")
    tempos = {"acao": ACAO[nome], "caixa": cx, "origem": list(dict.fromkeys(q for _, _, _, q in quadros)),
              "elementos": [{"desenho": i, "ticks": t, "caixa": c, "de": q} for i, (_, t, c, q) in enumerate(quadros)]}
    assert sum(e["ticks"] for e in tempos["elementos"]) == sum(t for _, t in ATUAL[nome])
    for pasta in ("quadros_pecas_hd", "quadros_pecas"):
        (SPR / pasta / nome / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False),
                                                        encoding="utf-8")
    return relatorio


def animar(nomes):
    kit = ler_kit()
    pf.MANCHA_REF = pf.mancha_ref()
    relatorio = ["| quadro | desenho de hoje | robô de defeitos |", "|---|---|---|"]
    poses = {}
    for nome in nomes:
        elems = ATUAL[nome]
        if nome in POSES_FEITAS:  # golpe confuso: poses desenhadas aqui, pelo pedido original da folha
            chaves = POSES_FEITAS[nome]()
            for q, _ in elems:
                poses[q] = chaves[q]
        else:
            for q in dict.fromkeys(q for q, _ in elems):
                poses[q] = pose_de(kit, q, nome)
        bate, cx = CAIXA.get(nome, (None, None))
        laco = nome == "parado"
        quadros = vida.animar(poses, elems, bate=bate, laco=laco, guarda={} if not laco else None)
        # com o calção e as pernas do desenho de hoje, o corpo anda junto com eles (não desliza no meio)
        for pose, _, _, _ in quadros:
            if "_baixo" in pose:
                pose["quadril"] = dict(pose.get("quadril", {}), dx=pose["_baixo"]["dx"], dy=pose["_baixo"]["dy"])
        if laco:
            quadros = vida.respirar(quadros)
        quadros = vida.atrasar(quadros, laco=laco)
        relatorio += gravar(kit, nome, quadros, cx)
        print(nome, len(dict.fromkeys(q for q, _ in elems)), "poses-chave ->", len(quadros), "desenhos")
    Image.fromarray(desenhar(kit, {})).save(SPR / "quadros_pecas_hd" / "guarda.png")
    falhas = sum("FAIL" in l for l in relatorio)
    texto = "\n".join(relatorio) + f"\n\n{falhas} quadro(s) com defeito.\n"
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "robo_defeitos.md").write_text(texto, encoding="utf-8")
    (SPR / "quadros_pecas_hd" / "poses.json").write_text(json.dumps(poses, indent=1, default=float), encoding="utf-8")
    print(f"robô: {falhas} quadro(s) com defeito")


def _perna_de_apoio(pose):
    """Perna de trás plantada onde está no parado (IK), com o quadril onde a pose pôs."""
    w = b.mundo(pose)
    qr, jr = OSSOS["coxa_tras"][0], OSSOS["canela_tras"][0]
    tr = TORNOZELO["canela_tras"]
    c1, c2 = pf.ik(w["coxa_tras"][0], tr, jr, qr, tr)
    pose["coxa_tras"], pose["canela_tras"] = {"ang": c1}, {"ang": c2}
    return pose


def _chute(qdx, qdy, coxa, canela, braco=0, cab=0, pe_no_ar=True):
    pose = {"quadril": {"ang": 0, "dx": qdx, "dy": qdy}, "coxa_frente": {"ang": coxa},
            "canela_frente": {"ang": canela}, "braco_frente": {"ang": braco}, "braco_tras": {"ang": -braco / 2},
            "cabeca": {"ang": 0, "dx": cab, "dy": 0}}
    if pe_no_ar:
        pose["canela_frente"]["pe"] = 0
    return _perna_de_apoio(pose)


def poses_chute_alto():
    """Chute frontal no peito (pedido da folha: o joelho sobe até o peito e a sola empurra reto para a frente na
    altura do peito, inclinado para trás). O desenho de hoje mal estica a perna: aqui as poses são do kit."""
    return {
        "chute_alto/01": _chute(-4, 0, -28, 22, braco=-4),             # tira o peso da perna da frente
        "chute_alto/02": _chute(-8, -1, -86, 70, braco=-8, cab=-2),     # joelho no peito (câmara)
        "chute_alto/04": _chute(-14, -2, -94, -28, braco=-14, cab=-4),  # perna esticada, sola no peito
        "chute_alto/05": _chute(-10, -1, -84, 52, braco=-8, cab=-2),    # recolhe
        "chute_alto/06": _chute(-4, 0, -40, 34, braco=-3),             # o pé desce
        "chute_alto/07": _chute(0, 0, -6, 4, braco=0, pe_no_ar=False),  # pisa na guarda
    }


POSES_FEITAS = {"chute_alto": poses_chute_alto}


def video(saida=None):
    """Vídeo lado a lado (jogo de hoje x corpo firme), tira de ticks e folha antes/depois (video_pecas.py)."""
    import video_pecas as vp
    vp.SPR, vp.ATUAL, vp.GUARDA = SPR, ATUAL, REF
    vp.CORTE = (380, 270, 760, 680)
    sys.argv = ["video_pecas.py", str(saida or DOCS)]
    vp.main()


# ------------------------------------------------------------------ quadro especial: desenho de hoje + cabeça do kit
CABELO = {(149, 44, 65), (101, 29, 53), (76, 23, 53), (22, 20, 36)}
CENTRO_CABECA = (569, 365)   # meio da cabeça no referencia_ginga/00 (a junta do pescoço fica 27 px abaixo)


def _cabeca_girada(kit, ang, esc=1.0):
    """Cabeça do kit girada (horário na tela) em volta da junta do pescoço. `esc` < 1 só nos desenhos de deitado, que
    vieram menores que o parado (a cabeça acompanha o tamanho do corpo daquele desenho)."""
    cab = kit["pecas"]["cabeca"]
    junta = cab["junta"]
    piv = (junta[0] - cab["origem"][0], junta[1] - cab["origem"][1])
    img, topo = cab["img"], kit["topo"]
    if esc != 1.0:
        h, w = img.shape[:2]
        tam = (max(1, round(w * esc)), max(1, round(h * esc)))
        img = np.asarray(Image.fromarray(np.ascontiguousarray(img)).resize(tam, Image.NEAREST))
        topo = np.asarray(Image.fromarray(np.ascontiguousarray(topo)).resize(tam, Image.NEAREST))
        piv = (piv[0] * esc, piv[1] * esc)
    r, p = b.rotsprite(img, ang, piv)
    t, _ = b.rotsprite(topo, ang, piv)
    return r, t, p


def achar_por_centro(kit, src, centro, ang0, abertura, raio=15, escalas=(1.0,), frente=None, passo=5):
    """Busca guiada para os quadros em que a busca livre erra (deitado, de ponta-cabeça, braço na frente): o centro da
    cabeça no desenho é dado à mão (± raio), o giro corre ang0 ± abertura e o que está na frente (`frente`) não conta."""
    cab = kit["pecas"]["cabeca"]
    jx, jy = cab["junta"][0] - CENTRO_CABECA[0], cab["junta"][1] - CENTRO_CABECA[1]
    cinza = pf.cinza(src)
    melhor = None
    for esc in escalas:
        for ang in range(ang0 - abertura, ang0 + abertura + 1, passo):
            r, t, p = _cabeca_girada(kit, ang, esc)
            a = np.radians(ang)
            vx = (jx * np.cos(a) - jy * np.sin(a)) * esc
            vy = (jx * np.sin(a) + jy * np.cos(a)) * esc
            h, w = r.shape[:2]
            X0 = int(centro[0] - (p[0] - vx) - raio)
            Y0 = int(centro[1] - (p[1] - vy) - raio)
            Xc, Yc = max(0, X0), max(0, Y0)
            reg = cinza[Yc:Y0 + h + 2 * raio, Xc:X0 + w + 2 * raio]
            if reg.shape[0] <= h or reg.shape[1] <= w:
                continue
            m = (t[..., 3] > 0).astype(np.float32)
            if frente is not None:  # o que está na frente da cabeça não conta: busca com a máscara furada por posição
                res = np.full((reg.shape[0] - h + 1, reg.shape[1] - w + 1), np.inf, np.float32)
                fr = frente[Yc:Yc + reg.shape[0], Xc:Xc + reg.shape[1]]
                for yy in range(res.shape[0]):
                    for xx in range(res.shape[1]):
                        mm = m * (~fr[yy:yy + h, xx:xx + w])
                        n = mm.sum()
                        if n < 0.4 * m.sum():
                            continue
                        d = ((reg[yy:yy + h, xx:xx + w] - pf.cinza(r)) ** 2).sum(-1) * mm
                        res[yy, xx] = d.sum() / (n * 3)
                v, _, pm, _ = cv2.minMaxLoc(res)
                nota = np.sqrt(v)
            else:
                res = cv2.matchTemplate(reg, pf.cinza(r), cv2.TM_SQDIFF,
                                        mask=np.ascontiguousarray(np.repeat(m[..., None], 3, -1)))
                res = np.nan_to_num(res, nan=1e18, posinf=1e18)
                v, _, pm, _ = cv2.minMaxLoc(res)
                nota = np.sqrt(v / (m.sum() * 3))
            if melhor is None or nota < melhor[0]:
                melhor = (nota, ang, (pm[0] + Xc + p[0], pm[1] + Yc + p[1]), esc)
    return melhor


def achar_cabeca(kit, src, angulos=range(-60, 61, 5), regiao=None):
    """Onde a cabeça do kit casa melhor no desenho (giro e lugar da junta do pescoço). Casa pela cor já trocada, então
    acha a cabeça laranja também (sem barba e de franja, mas no mesmo lugar)."""
    al = src[..., 3] > 0
    ys, xs = np.nonzero(al)
    if regiao is None:
        y_lim = ys.min() + int((ys.max() - ys.min()) * 0.55)
        regiao = (max(0, xs.min() - 20), max(0, ys.min() - 20), xs.max() + 20, y_lim + 40)
    X0, Y0, X1, Y1 = regiao
    reg = pf.cinza(src[Y0:Y1, X0:X1])
    melhor = None
    for ang in angulos:
        r, t, p = _cabeca_girada(kit, ang)
        m = (t[..., 3] > 0).astype(np.float32)
        if r.shape[0] >= reg.shape[0] or r.shape[1] >= reg.shape[1]:
            continue
        res = cv2.matchTemplate(reg, pf.cinza(r), cv2.TM_SQDIFF,
                                mask=np.ascontiguousarray(np.repeat(m[..., None], 3, -1)))
        v, _, pm, _ = cv2.minMaxLoc(res)
        nota = np.sqrt(v / (m.sum() * 3))
        if melhor is None or nota < melhor[0]:
            melhor = (nota, ang, (pm[0] + X0 + p[0], pm[1] + Y0 + p[1]))
    return melhor


def trocar_cabeca(kit, src, achado=None, frente=None):
    """Tira a cabeça do desenho e põe a do kit no mesmo lugar e giro. `frente` (máscara) é o que o desenho tem na
    frente da cabeça (braço, punho, bengala): volta por cima no fim. Devolve (quadro, nota do casamento)."""
    achado = achado or achar_cabeca(kit, src)
    nota, ang, junta = achado[:3]
    esc = achado[3] if len(achado) > 3 else 1.0
    r, t, p = _cabeca_girada(kit, ang, esc)
    x0, y0 = int(round(junta[0] - p[0])), int(round(junta[1] - p[1]))
    lugar_t = np.zeros_like(src)
    b.colar(lugar_t, t, x0, y0)
    mt = lugar_t[..., 3] > 0
    out = src.copy()
    apaga = cv2.dilate(mt.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    # franja e cabelo da cabeça velha que passam da cabeça nova
    perto = cv2.dilate(mt.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
    cabelo = so_cores(src, perto & ~apaga, CABELO - {(22, 20, 36)})
    contorno = so_cores(src, perto & ~apaga, {(22, 20, 36)})
    cabelo |= contorno & (cv2.dilate(cabelo.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    # o que sobra só fica se não for parte do corpo (o corpo fica mais longe do alto da cabeça)
    out[(apaga | cabelo) & (src[..., 3] > 0)] = 0
    pesc = np.zeros_like(src)
    b.colar(pesc, r, x0, y0)
    b.colar(out, pesc, 0, 0, so_vazio=True)  # pescoço só no vazio (por baixo da regata)
    b.colar(out, np.where(mt[..., None], pesc, 0).astype(np.uint8), 0, 0)
    # pedaço da cabeça velha que ficou solto (nariz, orelha) some; o que já era solto no desenho (gancho) fica
    al = (out[..., 3] > 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(al, connectivity=8)
    solto_antes = cv2.connectedComponents((src[..., 3] > 0).astype(np.uint8), connectivity=8)[1]
    maior = 1 + int(np.argmax(st[1:, 4])) if n > 1 else 0
    for i in range(1, n):
        if i != maior and st[i, 4] < 600:
            m = lab == i
            rot = np.unique(solto_antes[m])
            era_solto = any(r != 0 and (solto_antes == r).sum() < 2000 for r in rot)
            if not era_solto:
                out[m] = 0
    if frente is not None:
        out[frente] = src[frente]
    # fresta entre a cabeça nova e o ombro/braço (onde a cabeça velha era maior que a nova): fecha perto do pescoço
    ys_c, xs_c = np.nonzero(mt)
    perto_antes, pf.PERTO_DA_JUNTA = pf.PERTO_DA_JUNTA, 40
    try:
        out = pf.fechar_frestas(out, raio=4, juntas=[junta, (xs_c.mean(), ys_c.mean())])
    finally:
        pf.PERTO_DA_JUNTA = perto_antes
    return quantizar(pf.sem_migalha(out, minimo=30)), nota


# ------------------------------------------------------------------ consertos do desenho de origem (17/11/2026)
# Desenhos de pé que vieram 80 px acima do chão (o 1º quadro de cada linha da folha): descem até o chão do jogo.
# Nos golpes de pulo (pulo, ar_soco, bicicleta) quem sobe é o motor: o desenho que veio mais alto fazia o boneco dar
# um salto a mais de 100 px no meio do pulo; desce também. afastar 03-04, golaco/01, levanta/02 e queda/05 são o
# próprio desenho saltando (o motor não sobe) e ficam.
CHAO_ERRADO = {"apanha/00", "apanha/03", "apanha/04", "chute_baixo/00", "chute_baixo/05", "defesa/00", "defesa/04",
               "levanta/04", "pulo/00", "queda/00",
               "pulo/04", "ar_soco/00", "ar_soco/04"}
# Gancho da bengala solto do cabo na defesa (já veio assim): direção do cabo e ponta dele, lidas à mão.
GANCHO = {"defesa/05": ((0.963, -0.268), (597, 398)), "defesa/06": ((0.94, -0.34), (583, 387))}


def assentar(out):
    """Desce o desenho até o pixel mais baixo encostar no chão (CHAO)."""
    ys = np.nonzero(out[..., 3].any(1))[0]
    return np.roll(out, CHAO - ys.max(), 0)

def prender_gancho(a, dirx, diry, ponta, passo_max=25, folga=3):
    """Gancho da bengala solto do cabo (já veio assim no desenho): estica a ponta do cabo na direção dele, copiando os
    últimos 10 px do próprio cabo para a frente (mesmas cores e sombra), até grudar firme no gancho (+ folga)."""
    a = a.copy()
    n, lab, st, _ = cv2.connectedComponentsWithStats((a[..., 3] > 0).astype(np.uint8), connectivity=8)
    big = 1 + int(np.argmax(st[1:, 4]))
    solto = [k for k in range(1, n) if k != big and st[k, 4] > 300]
    if not solto:
        return a, 0
    g = lab == solto[0]
    cores = {tuple(c) for c in a[g][:, :3]}
    ys, xs = np.nonzero(lab == big)
    eh = np.array([tuple(c) in cores for c in a[ys, xs, :3]])
    gy, gx = np.nonzero(g)
    # só o cabo: perto da ponta dada à mão (a pele do braço tem as mesmas cores)
    perp = np.abs((xs - ponta[0]) * -diry + (ys - ponta[1]) * dirx)
    ao_longo = (xs - ponta[0]) * dirx + (ys - ponta[1]) * diry
    m = eh & (perp < 6) & (ao_longo > -14) & (ao_longo < 6)
    yy, xx = ys[m], xs[m]
    proj = xx * dirx + yy * diry
    tras = proj > proj.max() - 10
    sy, sx = yy[tras], xx[tras]
    py, px = gy[0], gx[0]
    preso = None
    for k in range(1, passo_max + 1):
        ox, oy = int(round(k * dirx)), int(round(k * diry))
        for y, x in zip(sy + oy, sx + ox):
            if a[y, x, 3] == 0:
                a[y, x] = a[y - oy, x - ox]
        l4 = cv2.connectedComponents((a[..., 3] > 0).astype(np.uint8), connectivity=4)[1]
        if preso is None and l4[py, px] == l4[sy[0], sx[0]]:
            preso = k
        if preso is not None and k >= preso + folga:
            return a, k
    return a, -1


LIMITE_CABECA = 63   # nota do casamento da cabeça: acima disso o quadro vai para a revisão (cabeça escondida ou girada)

# Os 41 quadros que passaram do limite, olhados um a um (17/11/2026):
# 1) a busca livre acertou o lugar e o giro; a nota só passou porque o desenho tem a cabeça laranja de franja.
CABECA_CONFERIDA = {"agarrao/05", "apanha/02", "apanha/03", "apanha/04", "ar_soco/02", "ar_soco/03", "baixo_soco/04",
                    "cabecada/02", "cabecada/03",
                    "compasso/04", "lata/02", "levanta/03", "levanta/04", "parry_alto/04", "queda/01", "rasteira/03",
                    "rasteira/04", "rasteira/05"} | {f"bicicleta/{i:02d}" for i in range(8)}
# 2) de costas: não tem rosto para trocar, fica a nuca do desenho (na cor certa).
COSTAS = {"rolamento/05"}
# 3) busca guiada: centro da cabeça no desenho (lido à mão), giro inicial (horário +, 180 = de ponta-cabeça),
#    abertura do giro, tamanhos tentados, espelho (virado para a esquerda) e o que fica na frente da cabeça.
_DEITADO = (0.65, 0.7, 0.75, 0.8, 0.85, 0.9)
CABECA_GUIA = {
    "agarrao/04": dict(centro=(452, 418), ang=-70, abertura=15),
    "cabecada/04": dict(centro=(560, 400), ang=0, abertura=25, escalas=(0.9, 0.95, 1.0)),
    "levanta/00": dict(centro=(470, 615), ang=-90, abertura=40, escalas=_DEITADO),
    "parry_baixo/03": dict(centro=(562, 630), ang=180, abertura=40, escalas=(0.85, 0.9, 0.95, 1.0)),
    "parry_baixo/04": dict(centro=(490, 625), ang=-135, abertura=45, escalas=_DEITADO),
    "queda/03": dict(centro=(410, 550), ang=-90, abertura=45, escalas=_DEITADO),
    "queda/04": dict(centro=(405, 570), ang=-90, abertura=40, escalas=_DEITADO),
    "queda/05": dict(centro=(420, 500), ang=-90, abertura=40, escalas=_DEITADO),
    "queda/06": dict(centro=(425, 620), ang=-90, abertura=40, escalas=_DEITADO),
    "queda/07": dict(centro=(440, 625), ang=-90, abertura=40, escalas=_DEITADO),
    "rolamento/06": dict(centro=(507, 400), ang=0, abertura=25, escalas=(0.9, 0.95, 1.0), espelho=True),
    "soco/05": dict(centro=(565, 381), ang=0, abertura=25),
}
# Defesa: punho, antebraço e bengala cruzam na frente do rosto. A cabeça do kit entra por baixo deles.
_FRENTE_DEFESA = {
    1: [(577, 380), (590, 376), (600, 372), (640, 370), (640, 440), (470, 440), (470, 390), (500, 385), (525, 388),
        (530, 400), (560, 402), (575, 398)],
    2: [(560, 375), (575, 370), (590, 367), (640, 360), (640, 440), (470, 440), (470, 385), (515, 385), (525, 393),
        (555, 397)],
    3: [(562, 378), (580, 375), (590, 368), (640, 365), (640, 440), (470, 440), (470, 385), (515, 385), (525, 393),
        (560, 392)],
    4: [(560, 298), (575, 295), (588, 292), (640, 288), (640, 360), (470, 360), (470, 302), (510, 303), (525, 310),
        (560, 312)],
    5: [(545, 384), (560, 380), (575, 375), (620, 370), (640, 440), (470, 440), (470, 400), (505, 400), (525, 404),
        (545, 402)],
    6: [(532, 378), (545, 373), (565, 365), (620, 360), (630, 440), (460, 440), (460, 398), (500, 396), (520, 398),
        (532, 395)],
    7: [(560, 380), (575, 377), (587, 372), (640, 365), (640, 440), (470, 440), (470, 383), (510, 385), (525, 392),
        (560, 393)],
}
_CENTRO_DEFESA = {1: (548, 372), 2: (545, 372), 3: (545, 372), 4: (545, 292), 5: (525, 382), 6: (515, 378),
                  7: (548, 372)}
for _i, _pol in _FRENTE_DEFESA.items():
    CABECA_GUIA[f"defesa/{_i:02d}"] = dict(centro=_CENTRO_DEFESA[_i], ang=0, abertura=15, raio=20,
                                            escalas=(1.0,), frente=_pol)


def _mascara(pol, forma):
    m = np.zeros(forma[:2], np.uint8)
    cv2.fillPoly(m, [np.array(pol, np.int32)], 1)
    return m > 0


def cabeca_guiada(kit, src, guia):
    """Troca de cabeça pela busca guiada (CABECA_GUIA). Devolve (quadro, nota, achado)."""
    esp = guia.get("espelho", False)
    centro = guia["centro"]
    frente = _mascara(guia["frente"], src.shape) & (src[..., 3] > 0) if "frente" in guia else None
    if esp:
        src = np.ascontiguousarray(src[:, ::-1])
        centro = (src.shape[1] - 1 - centro[0], centro[1])
        frente = None if frente is None else np.ascontiguousarray(frente[:, ::-1])
    achado = achar_por_centro(kit, src, centro, guia["ang"], guia["abertura"], raio=guia.get("raio", 15),
                              escalas=guia.get("escalas", (1.0,)), frente=frente)
    out, nota = trocar_cabeca(kit, src, achado, frente=frente)
    if esp:
        out = np.ascontiguousarray(out[:, ::-1])
    return out, nota, achado
FIRMES = SPR / "quadros_firmes_hd"


def firmes(golpes=None):
    """Todos os quadros de todos os golpes, na mesma numeração de quadros_arcade_hd (o gerador só troca a pasta):
    cor do Gbzin certo, sem grade e com a cabeça do kit. Os golpes montados pelo kit (POSES_QUADRO) saem do kit."""
    kit = ler_kit()
    linhas = ["| quadro | como saiu | nota da cabeça |", "|---|---|---|"]
    golpes = golpes or sorted(p.name for p in (SPR / "quadros_arcade_hd").iterdir()
                              if p.is_dir() and p.name not in SO_DESENHO)
    for gn in golpes:
        (FIRMES / gn).mkdir(parents=True, exist_ok=True)
        (FIRMES.parent / "quadros_firmes" / gn).mkdir(parents=True, exist_ok=True)
        for i in range(8):
            q = f"{gn}/{i:02d}"
            if q in SILHUETA:  # fim do Despertar: só a silhueta escura contra a luz verde
                base = np.asarray(Image.open(FIRMES / SILHUETA[q][0] / f"{SILHUETA[q][1]:02d}.png")).copy()
                out = silhueta(base)
                como, nota = f"silhueta de {SILHUETA[q][0]}/{SILHUETA[q][1]:02d}", None
            elif q == "rolamento/06" and False:  # termina o giro virado para a esquerda: a guarda espelhada
                out, como, nota = np.ascontiguousarray(desenhar(kit, {})[:, ::-1]), "kit espelhado", None
                ys, xs = np.nonzero(out[..., 3] > 0)
                out = np.roll(out, 1080 - 2 * 540 + (540 - (xs.min() + xs.max()) // 2) * 0, 1)
            elif q in POSES_QUADRO:
                out, como, nota = desenhar(kit, POSES_QUADRO[q](kit)), "kit", None
                if gn in NO_AR:
                    ys = np.nonzero(out[..., 3].any(1))[0]
                    out = np.roll(out, 659 - ys.max(), 0)
            elif q in CABECA_GUIA:
                out, nota, ach = cabeca_guiada(kit, abrir(TROCA_QUADRO.get(q, q)), CABECA_GUIA[q])
                como = (f"desenho + cabeça do kit (guiada: giro {ach[1]}°"
                        + (f", tamanho {ach[3]:.2f}" if ach[3] != 1.0 else "")
                        + (", espelhada" if CABECA_GUIA[q].get("espelho") else "")
                        + (", braço e bengala por cima" if "frente" in CABECA_GUIA[q] else "") + ")")
            elif q in COSTAS:
                out, nota, como = quantizar(abrir(TROCA_QUADRO.get(q, q))), None, "de costas: fica a nuca do desenho (na cor certa)"
            else:
                src = abrir(TROCA_QUADRO.get(q, q))
                achado = achar_cabeca(kit, src)
                if achado[0] <= LIMITE_CABECA or q in CABECA_CONFERIDA:
                    out, nota = trocar_cabeca(kit, src, achado)
                    como = "desenho + cabeça do kit" + (f" (desenho de {TROCA_QUADRO[q]})" if q in TROCA_QUADRO else "")
                    if achado[0] > LIMITE_CABECA:
                        como += " (conferida à mão)"
                else:
                    out, nota, como = quantizar(src), achado[0], "REVISAR: cabeça não achada (fica a do desenho, na cor certa)"
            if q in GANCHO:
                out, _ = prender_gancho(out, *GANCHO[q][0], GANCHO[q][1])
                como += "; gancho da bengala preso no cabo"
            if q in CHAO_ERRADO:
                out = assentar(out)
                como += "; descido até o chão"
            Image.fromarray(out).save(FIRMES / gn / f"{i:02d}.png")
            Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(FIRMES.parent / "quadros_firmes" / gn /
                                                                         f"{i:02d}.png")
            linhas.append(f"| {q} | {como} | {'' if nota is None else round(float(nota), 1)} |")
        print(gn, "ok", flush=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "firmes.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def _quadro_kit(nome, q):
    def f(kit):
        pose = POSES_FEITAS[nome]()[q] if nome in POSES_FEITAS else pose_de(kit, q, nome)
        return pose
    return f


POSES_QUADRO = {}
# Despertar: a folha pedia três pancadas do cajado no chão; vieram celular e caixa de pizza (02 a 06). As pancadas saem
# dos desenhos bons do Cajado no Chão (mesmo boneco, mesmas mãos no cajado), na ordem do pedido.
TROCA_QUADRO = {
    "despertar_a/01": "cajado_chao/01",   # levanta o cajado com as duas mãos
    "despertar_a/02": "cajado_chao/04",   # 1ª pancada
    "despertar_a/03": "cajado_chao/02",   # levanta de novo, mais bravo
    "despertar_a/04": "cajado_chao/04",   # 2ª pancada (o quadro segue o 02 do jogo: mais tempo segurado)
    "despertar_a/05": "cajado_chao/02",   # cajado no alto
    "despertar_a/06": "cajado_chao/04",   # 3ª pancada, com o corpo todo
}
# Folhas novas pedidas ao ChatGPT em 17/11/2026 (pedidos em docs/boneco-pecas/gbzin/pedidos_chatgpt.json): as velhas
# tinham a bicicleta de joelho dobrado (não era chute), o soco sem cotovelada de verdade e o pinguim de braço mole.
SO_DESENHO = {"bicicleta_v2", "soco_cotovelo", "rolamento_v2"}  # folhas que só emprestam desenhos (não viram golpe)
TROCA_QUADRO.update({f"bicicleta/{i:02d}": f"bicicleta_v2/{i:02d}" for i in range(8)})   # pernas retas, 3 chutes
TROCA_QUADRO.update({"soco/04": "soco_cotovelo/04",    # cotovelo armado, pé de trás já vindo
                     "soco/05": "soco_cotovelo/05"})   # cotovelada com o quadril girado
TROCA_QUADRO.update({f"rolamento/{i:02d}": f"rolamento_v2/{i:02d}" for i in range(1, 7)})  # braços duros de pinguim
SILHUETA = {"despertar_a/07": ("despertar_a", 6)}


def _ar(coxa_f, canela_f, coxa_t, canela_t, braco=0, cab=0, quadril=0):
    """Pose no ar (as duas pernas soltas, pés girando com a canela). O quadro desce depois até o pé mais baixo
    encostar na linha do chão do desenho (o pulo é do motor), como nos desenhos de hoje."""
    return {"quadril": {"ang": quadril, "dx": 0, "dy": 0}, "coxa_frente": {"ang": coxa_f},
            "canela_frente": {"ang": canela_f, "pe": 0}, "coxa_tras": {"ang": coxa_t},
            "canela_tras": {"ang": canela_t, "pe": 0}, "braco_frente": {"ang": braco},
            "braco_tras": {"ang": -braco / 2}, "cabeca": {"ang": 0, "dx": cab, "dy": 0}}


# coxa da frente: -92 encolhida, -87 esticada; canela: 89 pendurada, -31 reta. Coxa de trás: -134 encolhida, -139
# esticada; canela de trás: 134 pendurada, 24 reta (ângulos medidos no osso do parado).
ENC_F, EST_F = (-92, 89), (-87, -31)
ENC_T, EST_T = (-134, 128), (-139, 24)
BICICLETA = {  # chute duplo no ar: a perna da frente estica três vezes (a de trás fica dobrada, encolhida)
    "bicicleta/00": _ar(-86, 70, -40, 70, braco=0),
    "bicicleta/01": _ar(-94, -28, -46, 76, braco=-10, cab=-2),
    "bicicleta/02": _ar(-86, 70, -40, 70, braco=-4),
    "bicicleta/03": _ar(-100, -22, -48, 78, braco=-12, cab=-3),
    "bicicleta/04": _ar(-86, 70, -40, 70, braco=-4),
    "bicicleta/05": _ar(-94, -28, -46, 76, braco=-10, cab=-2),
    "bicicleta/06": _ar(-80, 60, -36, 66, braco=-2),
    "bicicleta/07": _ar(-60, 50, -30, 60, braco=0),
}
NO_AR = {"bicicleta"}


def _cotovelada(ang, cab=0, qdx=0, var="recolhido"):
    bf = {"ang": ang, "var": var} if var else {"ang": ang}
    pose = {"quadril": {"ang": 0, "dx": qdx, "dy": 0}, "braco_frente": bf,
            "cabeca": {"ang": 0, "dx": cab, "dy": 0}}
    return pf.pernas_no_chao(pose, abrir("referencia_ginga/00"))


def _pinguim(braco_f, braco_t, balanco, passo):
    """Passinho de Pinguim: braços duros abertos para os lados, o corpo balança e o pé anda curtinho."""
    pose = {"quadril": {"ang": balanco, "dx": passo, "dy": -2 if balanco else 0}, "braco_frente": {"ang": braco_f},
            "braco_tras": {"ang": braco_t}, "cabeca": {"ang": -balanco, "dx": 0, "dy": 0}}
    return _perna_de_apoio_dupla(pose)


def _perna_de_apoio_dupla(pose):
    w = b.mundo(pose)
    for coxa, canela in (("coxa_tras", "canela_tras"), ("coxa_frente", "canela_frente")):
        qr, jr = OSSOS[coxa][0], OSSOS[canela][0]
        tr = TORNOZELO[canela]
        alvo = (tr[0] + pose["quadril"]["dx"] * 0.6, tr[1])
        c1, c2 = pf.ik(w[coxa][0], alvo, jr, qr, tr)
        pose[coxa], pose[canela] = {"ang": c1}, {"ang": c2}
    return pose


def silhueta(img):
    """Silhueta escura com a borda acesa (a luz verde do Despertar vem de trás, como efeito à parte)."""
    out = img.copy()
    al = cv2.morphologyEx((img[..., 3] > 0).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)) > 0
    n, lab = cv2.connectedComponents((~al).astype(np.uint8))
    al |= (lab != lab[0, 0]) & ~al  # buracos de dentro também ficam escuros
    out[..., 3] = np.where(al, 255, 0)
    dentro = cv2.erode(al.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    out[al, :3] = (54, 40, 68)
    out[al & ~dentro, :3] = (250, 176, 90)
    return out
for _q in ("referencia_ginga/%02d" % i for i in range(8)):
    POSES_QUADRO[_q] = _quadro_kit("parado", _q)
for _q in ("soco/01", "soco/02", "soco/03", "soco/07", "soco/00"):
    POSES_QUADRO[_q] = _quadro_kit("soco", _q)
for _q in ("chute_alto/01", "chute_alto/02", "chute_alto/04", "chute_alto/05", "chute_alto/06", "chute_alto/07"):
    POSES_QUADRO[_q] = _quadro_kit("chute_alto", _q)
POSES_QUADRO["chute_alto/00"] = lambda kit: {}
POSES_QUADRO["chute_alto/03"] = lambda kit: vida.misturar(poses_chute_alto()["chute_alto/02"],
                                                          poses_chute_alto()["chute_alto/04"], 0.5)
# Bicicleta, cotovelada e Passinho de Pinguim pedem peças novas (perna esticada de lado, braço da cotovelada, braços
# abertos): girar o desenho de três quartos do parado nesses ângulos rasga a coxa e o calção. Ficam como desenho +
# cabeça do kit até as peças novas existirem; as poses de tentativa (BICICLETA, _cotovelada, PINGUIM) ficam aqui.
POSES_QUADRO["rolamento/00"] = lambda kit: {}
POSES_QUADRO["rolamento/07"] = lambda kit: {}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "kit":
        montar_kit()
    elif len(sys.argv) > 1 and sys.argv[1] == "animar":
        animar(sys.argv[2:] or list(ATUAL))
    elif len(sys.argv) > 1 and sys.argv[1] == "video":
        video()
    elif len(sys.argv) > 1 and sys.argv[1] == "firmes":
        firmes(sys.argv[2:] or None)
