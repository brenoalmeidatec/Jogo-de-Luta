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
        img = pf.sem_migalha(img, minimo=80)
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
        return pf.sem_migalha(tela)
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
    return pf.sem_migalha(tela)


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
    return pose


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


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "kit":
        montar_kit()
    elif len(sys.argv) > 1 and sys.argv[1] == "animar":
        animar(sys.argv[2:] or list(ATUAL))
    elif len(sys.argv) > 1 and sys.argv[1] == "video":
        video()
