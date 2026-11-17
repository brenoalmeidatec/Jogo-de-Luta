#!/usr/bin/env python3
"""Grão-Pastor (Gbzin despertado) pelo boneco de peças com corpo firme e vida, no mesmo desenho do gbzin_pecas.py.

O desenho-mestre é o parado do Grão-Pastor (quadros_e_firmes_hd/e_referencia_ginga/00: pose do rascunho, cabeça do kit
e as 15 cores travadas da paleta dele). Dele sai o kit inteiro, em sprites/gbzin/pecas_e/corpo/ (kit.json + um PNG por
peça, com a sobra de cada junta e os furos do desenho). Os arquivos de antes (pecas_e/cabeca.png, kit.json, ref.png e
paleta.json) continuam do gbzin_e_pecas.py, que troca a cabeça dos rascunhos.

  python ferramentas/kit_grao_pastor.py kit              recorta o kit e grava a prova de remontagem em
                                                         docs/boneco-pecas/gbzin/grao_pastor_kit*.png
  python ferramentas/kit_grao_pastor.py animar [NOMES]   parado, chifrada e estampido em quadros_e_pecas_hd/ (3x) e
                                                         quadros_e_pecas/ (1x), com tempos.json, robô e régua
  python ferramentas/kit_grao_pastor.py provas           poses x rascunho, antes/depois e vídeo lado a lado (60 fps)

No jogo: o gerar_gbzin.py roda no fim `ligar_pecas.py gbzin --de gbzin --pasta quadros_e_pecas_hd --grupo 49000`
(depois da ligação da forma base): o parado entra pelo remap do despertado, a chifrada reescreve a ação 10200 e o
estampido a 10240, com a mesma soma de ticks, o mesmo tick de acerto e as mesmas caixas.

Peças: cabeça (chifres, cabelo, rosto e o pescoço por baixo da gola), tronco (placa de caveira, correntes, gola de pelo e
o manto atrás de tudo, pintado também por trás das pernas e dos braços), braço de trás (ombreira de chifre, bracelete
de osso, mão e o cajado de osso com o gancho em chama), braço da frente (ombreira, antebraço de osso e a garra),
quadril (faixa vermelha e o alto da calça), as pontas da faixa em chama (peça solta que balança presa no nó), coxa e
canela de cada lado e os cascos (sempre retos no chão). O desenho na tela é pele que dobra nas juntas
(pele_pecas.py): sem linha de corte.

Os golpes saem das poses à mão em POSES (o rascunho de cada golpe só guia a pose; tamanho, rosto e cores são do kit),
pelas 12 leis do estudo de anatomia: quadril e tronco antes do membro, peso no casco de apoio, mão livre fora do
golpe e camadas perto/longe. A soma de ticks e o tick de acerto são os das ações do jogo (ATUAL).
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
HD = SPR / "quadros_e_firmes_hd"           # rascunhos (só guia de pose) e o parado-mestre
PECAS = SPR / "pecas_e" / "corpo"           # o kit do corpo
SAIDA_HD, SAIDA_1X = SPR / "quadros_e_pecas_hd", SPR / "quadros_e_pecas"
DOCS = RAIZ / "docs" / "boneco-pecas" / "gbzin"
REF = "e_referencia_ginga/00"
CHAO = 659
MANTO_ATE = 570       # o manto atrás das pernas termina aqui (abaixo é chão entre os cascos)
CINTURA_MANTO = 472   # alto da faixa: abaixo dela o tronco só tem o manto
SOBRA = 9

# ------------------------------------------------------------------ paleta travada (as 15 cores do Grão-Pastor)
_PAL = None


def paleta():
    global _PAL
    if _PAL is None:
        _PAL = np.array(json.loads((SPR / "pecas_e" / "paleta.json").read_text())["cores"], int)
    return _PAL


def quantizar(img):
    """Toda cor fora das 15 (pintura por baixo, borda de giro, fresta fechada) vira a mais perto delas."""
    out = img.copy()
    al = out[..., 3] > 0
    px = out[al][:, :3].astype(int)
    pal = paleta()
    if len(px):
        cores, inv = np.unique(px, axis=0, return_inverse=True)
        d = ((cores[:, None, :] - pal[None, :, :]) ** 2).sum(-1)
        out[al, :3] = pal[d.argmin(1)][inv.ravel()]
    out[..., 3] = np.where(al, 255, 0)
    return out


def abrir(nome):
    return np.array(Image.open(HD / f"{nome}.png").convert("RGBA"))


# ------------------------------------------------------------------ kit (coordenadas do e_referencia_ginga/00, 3x)
CABECA = [(502, 294), (634, 294), (634, 345), (620, 360), (612, 372), (606, 384), (602, 396), (592, 404), (560, 406),
          (545, 394), (538, 376), (528, 369), (508, 367), (500, 350)]
# braço de trás: ombreira de chifre, braço, bracelete de osso, pulseira, mão e a ponta de osso do cajado
BRACO_TRAS = [(484, 376), (522, 374), (548, 384), (550, 404), (538, 424), (514, 430), (508, 446), (503, 470),
              (494, 478), (495, 496), (504, 504), (503, 518), (488, 523), (462, 522), (446, 516), (440, 496), (422, 492), (420, 466), (442, 462),
              (450, 436), (460, 410)]
# o cajado (haste e gancho com a chama) passa por cima da calça: só as cores de osso e de chama dentro daqui
CAJADO = [(470, 494), (512, 494), (538, 502), (546, 520), (546, 545), (544, 570), (524, 574), (503, 563),
          (494, 545), (498, 530), (486, 521), (470, 522)]
BRACO_FRENTE = [(597, 396), (616, 394), (630, 404), (632, 416), (644, 414), (660, 416), (670, 426), (672, 448),
                (664, 470), (650, 482), (628, 486), (608, 486), (602, 472), (603, 440), (600, 420)]
QUADRIL = [(508, 472), (616, 470), (624, 498), (628, 528), (590, 532), (545, 536), (505, 530), (500, 500)]
PONTAS_FAIXA = [(543, 496), (606, 496), (612, 528), (610, 574), (534, 574), (532, 528)]
PERNA_TRAS = [(452, 520), (546, 520), (548, 560), (540, 605), (515, 615), (505, 662), (436, 662), (444, 612),
              (452, 600), (450, 560)]
PERNA_FRENTE = [(548, 520), (626, 515), (636, 560), (642, 605), (644, 662), (560, 662), (562, 615), (548, 605)]

COR_OSSO = {(242, 182, 125), (243, 212, 174), (240, 143, 95), (163, 96, 69)}
COR_CHAMA = {(90, 216, 20), (214, 230, 48), (77, 105, 32)}
COR_FAIXA = {(226, 28, 58), (188, 66, 66), (122, 48, 52)}
CONTORNO = (20, 20, 27)

# joelhos um pouco à frente da linha quadril-tornozelo (Lei 4: joelho sempre um pouco dobrado; a calça larga esconde)
JOELHO_TRAS, JOELHO_FRENTE = (495, 583), (604, 583)
TORNOZELO = {"canela_tras": (474, 620), "canela_frente": (598, 622)}
OSSOS = {  # junta (pivô) no parado, peça mãe, ponta (régua)
    "quadril": ((550, 505), None, (550, 535)),
    "tronco": ((550, 488), "quadril", (560, 400)),
    "cabeca": ((572, 396), "tronco", (575, 330)),
    "braco_tras": ((505, 410), "tronco", (468, 495)),
    "braco_frente": ((610, 420), "tronco", (645, 445)),
    "coxa_tras": ((505, 528), "quadril", JOELHO_TRAS),
    "canela_tras": (JOELHO_TRAS, "coxa_tras", TORNOZELO["canela_tras"]),
    "coxa_frente": ((588, 528), "quadril", JOELHO_FRENTE),
    "canela_frente": (JOELHO_FRENTE, "coxa_frente", TORNOZELO["canela_frente"]),
}
# ordem rígida (montador e conferência): o lado da frente é o de longe da câmera, então a perna da frente nasce atrás
# da perna de trás e da faixa; o braço de trás (cajado) é o de perto e fica por cima de tudo
CAMADAS = ["cabeca", "tronco", "coxa_frente", "canela_frente", "coxa_tras", "canela_tras", "quadril", "braco_frente",
           "braco_tras"]
PELE_CAMADAS = [
    ("tronco", [("tronco", ("quadril", "braco_tras", "braco_frente"))]),
    ("perna_frente", [("canela_frente", ("coxa_frente",)), ("coxa_frente", ("quadril", "canela_frente"))]),
    ("perna_tras", [("canela_tras", ("coxa_tras",)), ("coxa_tras", ("quadril", "canela_tras"))]),
    ("quadril", [("quadril", ("tronco", "coxa_tras", "coxa_frente"))]),
    ("braco_frente", [("braco_frente", ("tronco",))]),
    ("braco_tras", [("braco_tras", ("tronco",))]),
]

# faixa de mistura da pele em cada emenda (px 3x): a canela do Grão-Pastor é curta (o casco é alto), então a dobra do
# joelho mistura pouco, senão o joelho erguido do estampido arrasta a calça num risco até a canela
MISTURA_OSSO = {"braco_tras": 8, "braco_frente": 8, "coxa_tras": 14, "coxa_frente": 14, "canela_tras": 14,
                "canela_frente": 14}


def mascara(poli):
    m = Image.new("L", b.TELA, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in poli], fill=255)
    return np.array(m) > 0


def so_cores(img, m, cores):
    rgb = img[..., :3]
    ok = np.zeros(m.shape, bool)
    for c in cores:
        ok |= np.all(rgb == c, -1)
    return m & ok


MANTO = {(33, 26, 43), (64, 48, 71), (114, 80, 105)}


def sem_manto(ref, m):
    """Só o braço dentro do polígono: o pelo roxo do manto atrás dele fica no tronco, e o contorno escuro só conta
    colado no braço (o resto é sombra do manto)."""
    braco = m & ~so_cores(ref, m, MANTO | {CONTORNO})
    braco = pf.sem_migalha(np.where(braco[..., None], ref, 0).astype(np.uint8), minimo=30)[..., 3] > 0
    perto = cv2.dilate(braco.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    return braco | (so_cores(ref, m & perto, {CONTORNO}))


def configurar():
    """Aponta o boneco_ajuste e o piloto_firme para o Grão-Pastor (as funções deles leem estes nomes)."""
    b.SPR, b.HD, b.PECAS, b.REF = SPR, HD, PECAS, REF
    b.OSSOS, b.CAMADAS = OSSOS, CAMADAS
    b.abrir = abrir
    pf.TORNOZELO, pf.CHAO, pf.PES_REF = TORNOZELO, CHAO, None


def por_linha(m):
    """Cada linha da máscara preenchida da primeira à última coluna dela (o que fica entre as bordas do manto)."""
    out = np.zeros_like(m)
    for y in np.nonzero(m.any(1))[0]:
        xs = np.nonzero(m[y])[0]
        out[y, xs.min():xs.max() + 1] = True
    return out


def pintar_por_baixo(img, regiao, cores=None):
    """Pinta `regiao` da peça com as cores dela mesma (inpaint só com os pixels da peça, ou só com os de `cores`) e
    trava na paleta. É o que fica escondido no parado (manto atrás dos braços e das pernas, calça atrás das pontas da
    faixa e do cajado)."""
    dono = img[..., 3] > 0
    alvo = regiao & ~dono
    if not alvo.any():
        return img
    fonte = img if cores is None else np.where(so_cores(img, dono, cores)[..., None], img, 0).astype(np.uint8)
    pint = b.tapar(fonte, alvo, fonte[..., 3] > 0)
    out = img.copy()
    out[alvo] = quantizar(pint)[alvo]
    return out


def montar_kit():
    configurar()
    if PECAS.exists():
        shutil.rmtree(PECAS)
    PECAS.mkdir(parents=True)
    ref = abrir(REF)
    assert {tuple(c) for c in ref[ref[..., 3] > 0][:, :3].tolist()} <= {tuple(c) for c in paleta().tolist()}
    alfa = ref[..., 3] > 0
    yy, xx = np.mgrid[:b.TELA[1], :b.TELA[0]]
    m_cab = mascara(CABECA) & alfa
    # cajado: osso e chama dentro do polígono, mais o contorno escuro colado no osso
    osso = so_cores(ref, mascara(CAJADO) & alfa, COR_OSSO | COR_CHAMA)
    osso = pf.sem_migalha(np.where(osso[..., None], ref, 0).astype(np.uint8), minimo=60)[..., 3] > 0
    perto = cv2.dilate(osso.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    cajado = osso | (so_cores(ref, perto & mascara(CAJADO) & alfa, {CONTORNO}))
    m_bt = sem_manto(ref, mascara(BRACO_TRAS) & alfa & ~m_cab) | cajado
    m_bf = sem_manto(ref, mascara(BRACO_FRENTE) & alfa & ~m_bt & ~m_cab)
    pt_cor = so_cores(ref, mascara(PONTAS_FAIXA) & alfa & ~m_bt, COR_FAIXA | COR_CHAMA | {(243, 212, 174)})
    pt_cor &= yy >= 498
    pt_cor = pf.sem_migalha(np.where(pt_cor[..., None], ref, 0).astype(np.uint8), minimo=40)[..., 3] > 0
    pontas = pt_cor | (so_cores(ref, (cv2.dilate(pt_cor.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
                                & mascara(PONTAS_FAIXA) & alfa & ~m_bt & (yy >= 506), {CONTORNO}))
    m_q = mascara(QUADRIL) & alfa & ~m_bt & ~m_bf & ~pontas
    usados = m_cab | m_bt | m_bf | pontas | m_q
    pt = mascara(PERNA_TRAS) & alfa & ~usados
    pfr = mascara(PERNA_FRENTE) & alfa & ~usados & ~pt
    # o que sobra no meio, abaixo da faixa (entre as pernas), vai com a perna mais perto; o manto dos lados fica
    resto = alfa & ~usados & ~pt & ~pfr & (yy >= 520) & (xx > 500) & (xx < 615)
    dt = cv2.distanceTransform((~pt).astype(np.uint8), cv2.DIST_L2, 3)
    df = cv2.distanceTransform((~pfr).astype(np.uint8), cv2.DIST_L2, 3)
    pt |= resto & (dt <= df)
    pfr |= resto & (df < dt)
    tronco = alfa & ~usados & ~pt & ~pfr
    # fio de pelo do manto que só encosta no resto por outra peça (junto do casco, ao lado da garra) vai com a peça
    # mais perto: o tronco é um pedaço só, senão o fio fica solto quando o corpo respira ou o membro sai
    n, rot, st, _ = cv2.connectedComponentsWithStats(tronco.astype(np.uint8), connectivity=8)
    if n > 2:
        maior = 1 + int(np.argmax(st[1:, 4]))
        ilha = tronco & (rot != maior) & (rot > 0)
        tronco &= ~ilha
        donos = [m_bt, m_bf, pt, pfr, m_q]
        dist = np.stack([cv2.distanceTransform((~m).astype(np.uint8), cv2.DIST_L2, 3) for m in donos])
        perto = np.argmin(dist, 0)
        for i, m in enumerate(donos):
            m |= ilha & (perto == i)
    partes = {
        "cabeca": m_cab,
        "braco_tras": m_bt,
        "braco_frente": m_bf,
        "tronco": tronco,
        "quadril": m_q,
        "coxa_tras": pt & (yy < JOELHO_TRAS[1]),
        "canela_tras": pt & (yy >= JOELHO_TRAS[1] - 12),   # 12 linhas por baixo da coxa: sem fresta no joelho
        "coxa_frente": pfr & (yy < JOELHO_FRENTE[1]),
        "canela_frente": pfr & (yy >= JOELHO_FRENTE[1] - 12),
    }
    imgs = {k: np.where(m[..., None], ref, 0).astype(np.uint8) for k, m in partes.items()}
    # o que fica escondido no parado é pintado com as cores da própria peça:
    #   tronco: o manto e o lado do peito atrás dos braços, a gola atrás do pescoço e o manto atrás das pernas
    #   quadril: a calça atrás das pontas da faixa e do cajado; coxas: o alto da calça atrás das pontas e do cajado
    corpo = por_linha(tronco | m_q | pt | pfr | m_bt | m_bf) & (yy < 615)
    # atrás das pernas o manto desce só até o meio da coxa (no parado o chão aparece entre os cascos)
    atras = (m_bt | m_bf | ((pt | pfr) & (yy < MANTO_ATE)) | m_q | pontas | cajado | (m_cab & (yy > 366))) & corpo \
        & (xx > 432) & (xx < 652)
    # da faixa para baixo o que aparece atrás é só o manto de pelo (nunca a pele da barriga): pinta com o manto dos
    # lados; acima da faixa continua o que está em volta (lado do peito, gola, manto)
    t = imgs["tronco"]
    so_manto = np.where(((yy >= CINTURA_MANTO) & tronco)[..., None], t, 0).astype(np.uint8)
    baixo = pintar_por_baixo(so_manto, atras & (yy >= CINTURA_MANTO))
    t = pintar_por_baixo(t, atras & (yy < CINTURA_MANTO))
    m_baixo = atras & (yy >= CINTURA_MANTO) & ~tronco
    t[m_baixo] = baixo[m_baixo]
    # pintura que ficou ilhada (atrás da garra, longe do manto) sai: só fica o que encosta no tronco
    n, rot, st, _ = cv2.connectedComponentsWithStats((t[..., 3] > 0).astype(np.uint8), connectivity=8)
    if n > 2:
        maior = 1 + int(np.argmax(st[1:, 4]))
        t[(rot != maior) & (rot > 0) & ~tronco] = 0
    imgs["tronco"] = t
    calca = MANTO | {CONTORNO, (72, 38, 40)}  # a calça de pelo atrás das pontas e do cajado (nunca a pele)
    # logo abaixo do nó a faixa continua vermelha (a ponta que balança não deixa fresta escura no nó)
    imgs["quadril"] = pintar_por_baixo(imgs["quadril"], pontas & mascara(QUADRIL) & (yy < 516), COR_FAIXA | {CONTORNO})
    imgs["quadril"] = pintar_por_baixo(imgs["quadril"], (pontas | cajado) & mascara(QUADRIL) & (yy > 490), calca)
    for lado, m in (("tras", pt), ("frente", pfr)):
        pinta = (pontas | cajado) & mascara(PERNA_TRAS if lado == "tras" else PERNA_FRENTE) & (yy < partes[f"coxa_{lado}"].nonzero()[0].max())
        imgs[f"coxa_{lado}"] = pintar_por_baixo(imgs[f"coxa_{lado}"],
                                                pinta & ~partes[f"coxa_{'frente' if lado == 'tras' else 'tras'}"], calca)
    kit = {"ref": f"quadros_e_firmes_hd/{REF}.png", "pecas": {}, "regua": {}}

    def guardar(nome, img, junta, mae):
        a = img[..., 3] > 0
        ys, xs = np.nonzero(a)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        Image.fromarray(img[y0:y1, x0:x1]).save(PECAS / f"{nome}.png")
        disco = np.zeros(b.TELA[::-1], np.uint8)
        raio = 16 if nome.startswith("coxa") else SOBRA  # a coxa gira muito no estampido: sobra maior no quadril
        cv2.circle(disco, (int(junta[0]), int(junta[1])), raio, 1, -1)
        # sobra: o desenho em volta da junta (da peça e das vizinhas, como no parado), só para tapar buraco
        sob = np.where((disco.astype(bool) & alfa)[..., None], ref, 0).astype(np.uint8)
        sob = sob[y0 - SOBRA:y1 + SOBRA, x0 - SOBRA:x1 + SOBRA]
        Image.fromarray(sob).save(PECAS / f"{nome}_sobra.png")
        kit["pecas"][nome] = {"arquivo": f"{nome}.png", "origem": [int(x0), int(y0)], "junta": list(junta),
                              "mae": mae, "fonte": f"quadros_e_firmes_hd/{REF}.png",
                              "sobra": f"{nome}_sobra.png", "origem_sobra": [int(x0 - SOBRA), int(y0 - SOBRA)]}

    for nome, img in imgs.items():
        junta, mae, _ = OSSOS[nome]
        guardar(nome, img, junta, mae)
    # perna inteira (calça, canela e casco) para a malha da perna plantada (firme.malha_perna): a calça larga de pelo
    # dobra no joelho como pano, sem leque de pixels nem emenda
    for lado in ("tras", "frente"):
        perna = imgs[f"canela_{lado}"].copy()
        cx = imgs[f"coxa_{lado}"][..., 3] > 0
        perna[cx] = imgs[f"coxa_{lado}"][cx]
        guardar(f"perna_{lado}", perna, OSSOS[f"coxa_{lado}"][0], "quadril")
    # furos do desenho (vão entre os dedos, entre o cajado e a mão): ficam vazios mesmo quando o fechamento de
    # frestas age perto da junta; cada furo vai com a peça mais perto
    fech = cv2.morphologyEx(alfa.astype(np.uint8), cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))) > 0
    furos = fech & ~alfa
    dist = {k: cv2.distanceTransform((~m).astype(np.uint8), cv2.DIST_L2, 3) for k, m in partes.items()}
    dono = np.argmin(np.stack([dist[k] for k in partes]), 0)
    for i, nome in enumerate(partes):
        f = furos & (dono == i)
        p = kit["pecas"][nome]
        x0, y0 = p["origem"]
        h, w_ = np.asarray(Image.open(PECAS / p["arquivo"])).shape[:2]
        f = f[y0:y0 + h, x0:x0 + w_]
        if not f.any():
            continue
        sub = np.zeros((h, w_, 4), np.uint8)
        sub[f] = (255, 0, 255, 255)
        Image.fromarray(sub).save(PECAS / f"{nome}_furo.png")
        p["furo"] = f"{nome}_furo.png"
    # pontas da faixa: peça solta, presa no nó
    pont = np.where(pontas[..., None], ref, 0).astype(np.uint8)
    ys, xs = np.nonzero(pontas)
    Image.fromarray(pont[ys.min():ys.max() + 1, xs.min():xs.max() + 1]).save(PECAS / "pontas_faixa.png")
    kit["pontas_faixa"] = {"arquivo": "pontas_faixa.png", "origem": [int(xs.min()), int(ys.min())],
                           "no": [float(xs.mean()), float(ys.min())]}
    # régua: comprimento de cada osso no parado e a distância entre as raízes das coxas
    for nome, (j, mae, ponta) in OSSOS.items():
        kit["regua"][nome] = round(float(np.hypot(ponta[0] - j[0], ponta[1] - j[1])), 1)
    kit["regua"]["entre_coxas"] = round(float(np.hypot(*np.subtract(OSSOS["coxa_frente"][0],
                                                                    OSSOS["coxa_tras"][0]))), 1)
    kit["regua"]["ombros"] = round(float(np.hypot(*np.subtract(OSSOS["braco_frente"][0], OSSOS["braco_tras"][0]))), 1)
    (PECAS / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")
    conferencia_kit(partes, pontas)
    return partes


CORES_CONF = {"cabeca": (255, 80, 80), "tronco": (80, 160, 255), "braco_tras": (80, 220, 120),
              "braco_frente": (240, 200, 60), "coxa_tras": (200, 90, 220), "canela_tras": (140, 60, 160),
              "coxa_frente": (60, 220, 220), "canela_frente": (30, 140, 140), "quadril": (240, 240, 240)}


def conferencia_kit(partes, pontas):
    """docs/boneco-pecas/gbzin/grao_pastor_kit.png: o parado, as peças coloridas por cima e cada peça sozinha (com o
    que foi pintado por baixo)."""
    DOCS.mkdir(parents=True, exist_ok=True)
    ref = abrir(REF)
    cor = np.zeros_like(ref)
    for k, m in partes.items():
        cor[m, :3] = CORES_CONF[k]
        cor[m, 3] = 255
    cor[pontas, :3] = (255, 140, 0)
    cor[pontas, 3] = 255
    x0, y0, x1, y1 = 410, 285, 690, 670
    fundo = (60, 60, 70, 255)

    def em(img):
        bg = Image.new("RGBA", (x1 - x0, y1 - y0), fundo)
        bg.alpha_composite(Image.fromarray(img).crop((x0, y0, x1, y1)))
        return bg

    a = em(ref)
    over = Image.blend(a, em(cor), 0.55)
    pecas = []
    kit = json.loads((PECAS / "kit.json").read_text())
    for nome in ("tronco", "quadril", "braco_tras", "braco_frente", "coxa_tras", "canela_tras", "coxa_frente",
                 "canela_frente", "cabeca"):
        p = kit["pecas"][nome]
        t = np.zeros_like(ref)
        im = np.asarray(Image.open(PECAS / p["arquivo"]).convert("RGBA"))
        b.colar(t, im, *p["origem"])
        pecas.append(em(t))
    W, H = a.size
    folha = Image.new("RGB", (W * 6, H * 2), (40, 40, 48))
    folha.paste(a.convert("RGB"), (0, 0))
    folha.paste(over.convert("RGB"), (W, 0))
    for i, im in enumerate(pecas):
        folha.paste(im.convert("RGB"), (W * (2 + i % 4), H * (i // 4)) if i < 8 else (0, H))
    folha.save(DOCS / "grao_pastor_kit.png")


# ------------------------------------------------------------------ montagem
def ler_kit():
    configurar()
    kit = b.ler_kit()
    pt = kit["pontas_faixa"]
    pt["img"] = np.asarray(Image.open(PECAS / pt["arquivo"]).convert("RGBA"))
    cab = kit["pecas"]["cabeca"]
    ox, oy = cab["origem"]
    h, w_ = cab["img"].shape[:2]
    topo = np.zeros_like(cab["img"])
    mt = mascara(CABECA)[oy:oy + h, ox:ox + w_]
    topo[mt] = cab["img"][mt]
    kit["topo"] = topo
    for p in kit["pecas"].values():
        if "furo" in p:
            p["furo_img"] = np.asarray(Image.open(PECAS / p["furo"]).convert("RGBA"))
    kit["pes"] = {}
    for slot, (tx, ty) in TORNOZELO.items():
        p = kit["pecas"][slot]
        img = p["img"].copy()
        ox, oy = p["origem"]
        corte = ty - oy
        pe = np.zeros_like(img)
        pe[corte:] = img[corte:]
        img[corte + 4:] = 0  # 4 linhas de sobra: a canela cobre o começo do casco, sem fresta
        p["img"] = img
        ys = np.nonzero(pe[..., 3].any(1))[0]
        kit["pes"][slot] = {"img": pe, "origem": (ox, oy), "tornozelo": (tx, ty), "fundo": int(ys.max()),
                            "chao": int(ys.max()) + oy}
    return kit


def no_ar(pose, lado):
    """A perna está solta (joelho erguido) quando a pose dá o giro do casco na canela."""
    return pose.get(f"canela_{lado}", {}).get("pe") is not None


def _pele(kit, pose, w, tela, slot, vizinhos):
    """Uma peça como pele (pele_pecas.py): cada pontinho segue o próprio osso e, perto da emenda, o vizinho."""
    import pele_pecas as pele
    antes_m, pele.MISTURA_OSSO = pele.MISTURA_OSSO, MISTURA_OSSO
    try:
        X, Y, cor, pesos = pele._pontos(kit, b.chave(slot, pose), slot, tuple(vizinhos))
    finally:
        pele.MISTURA_OSSO = antes_m
    ax = np.zeros_like(X)
    ay = np.zeros_like(Y)
    for k_, osso in enumerate((slot,) + tuple(vizinhos)):
        tx, ty = pele._transformar(w, osso, X, Y)
        ax += pesos[:, k_] * tx
        ay += pesos[:, k_] * ty
    xi, yi = np.rint(ax).astype(np.int32), np.rint(ay).astype(np.int32)
    ok = (xi >= 0) & (xi < tela.shape[1]) & (yi >= 0) & (yi < tela.shape[0])
    tela[yi[ok], xi[ok]] = cor[ok]


def desenhar_pele(kit, pose):
    """O corpo inteiro como um desenho só, sem linha de corte:
      cabeça rígida por baixo (o pescoço some na gola), tronco com o manto como pele (pele_pecas.py), pernas plantadas
      deformadas por malha (firme.malha_perna: a calça de pelo dobra no joelho como pano, o casco só anda e fica reto
      no chão), perna solta (joelho erguido) como pele, quadril e braços como pele. Depois a sobra das juntas só em
      buraco, a cabeça por cima, os cascos e as pontas da faixa balançando (_acabar)."""
    import firme
    firme.K = sys.modules[__name__]
    w = b.mundo(pose)
    tela = np.zeros((b.TELA[1], b.TELA[0], 4), np.uint8)
    furo = np.zeros_like(tela)
    cab = kit["pecas"][b.chave("cabeca", pose)]
    r, x0, y0 = b.colocar(cab, cab["img"], cab["origem"], *w["cabeca"])
    b.colar(tela, r, x0, y0)
    _pele(kit, pose, w, tela, "tronco", ("quadril",))  # o manto não estica atrás dos braços
    for lado in ("frente", "tras"):  # a de longe (frente) primeiro: fica atrás da de perto
        if no_ar(pose, lado):
            _pele(kit, pose, w, tela, f"canela_{lado}", (f"coxa_{lado}",))
            # a coxa erguida gira inteira na junta (misturar com o quadril num giro de 85° espalha a calça num leque);
            # a junta fica escondida atrás do quadril e das pontas da faixa
            _pele(kit, pose, w, tela, f"coxa_{lado}", (f"canela_{lado}",))
        else:
            p = kit["pecas"][f"perna_{lado}"]
            ts, td = firme.malha_perna(lado, w)
            firme.deformar(p["img"], p["origem"], ts, td, tela)
            for slot in (f"coxa_{lado}", f"canela_{lado}"):  # os furos do desenho andam com a malha
                pp = kit["pecas"][slot]
                if "furo_img" in pp:
                    firme.deformar(pp["furo_img"], pp["origem"], ts, td, furo)
    _pele(kit, pose, w, tela, "quadril", ("tronco",))
    _pele(kit, pose, w, tela, "braco_frente", ("tronco",))
    _pele(kit, pose, w, tela, "braco_tras", ("tronco",))
    usados = [(kit["pecas"][b.chave(s, pose)],) + tuple(w[s]) for s in CAMADAS
              if not (s.split("_")[0] in ("coxa", "canela") and not no_ar(pose, s.split("_")[1]))]
    return _acabar(kit, pose, w, tela, usados, furo)


def _acabar(kit, pose, w, tela, usados, furo):
    for p, pos, ang in usados:
        r, x0, y0 = b.colocar(p, p["sob"], p["origem_sobra"], pos, ang)
        b.colar(tela, r, x0, y0, so_vazio=True)
    cab = kit["pecas"][b.chave("cabeca", pose)]
    pos, ang = w["cabeca"]
    r, x0, y0 = b.colocar(cab, kit["topo"], cab["origem"], pos, ang)
    b.colar(tela, r, x0, y0)
    for p, pos, ang in usados:
        if "furo_img" in p:
            r, x0, y0 = b.colocar(p, p["furo_img"], p["origem"], pos, ang)
            b.colar(furo, r, x0, y0)
    # pontas da faixa: penduradas no nó, atrás do movimento do quadril (por baixo dos cascos e do cajado)
    pt = kit["pontas_faixa"]
    bo = pose.get("_bolinhas", {})
    (qx, qy), qang = w["quadril"]
    jq = OSSOS["quadril"][0]
    no = b.girar(pt["no"], jq, qang)
    no = (no[0] + qx - jq[0] + bo.get("dx", 0), no[1] + qy - jq[1] + bo.get("dy", 0))
    piv = (pt["no"][0] - pt["origem"][0], pt["no"][1] - pt["origem"][1])
    r, piv2 = b.rotsprite(pt["img"], qang * 0.4 + bo.get("ang", 0), piv)  # a ponta pende: gira menos que o quadril
    b.colar(tela, r, int(round(no[0] - piv2[0])), int(round(no[1] - piv2[1])))
    for slot in ("canela_frente", "canela_tras"):
        if not no_ar(pose, slot.split("_")[1]):
            continue  # perna plantada: o casco já veio na malha da perna, reto no chão
        joelho, ang = w[slot]
        jr = OSSOS[slot][0]
        pe = kit["pes"][slot]
        giro_pe = pose.get(slot, {}).get("pe", None)
        t = b.girar(pe["tornozelo"], jr, ang)
        tx, ty = t[0] + joelho[0] - jr[0], t[1] + joelho[1] - jr[1]
        if giro_pe is None:  # casco no chão: fica reto e encosta no chão dele
            x0 = int(round(pe["origem"][0] + tx - pe["tornozelo"][0]))
            y0 = int(round(pe["origem"][1] + ty - pe["tornozelo"][1]))
            fundo = pe["fundo"] + y0
            if abs(fundo - pe["chao"]) <= 10:
                y0 += pe["chao"] - fundo
            b.colar(tela, pe["img"], x0, y0, so_vazio=(slot == "canela_frente"))
        else:  # casco no ar: gira com a canela mais o giro próprio
            piv = (pe["tornozelo"][0] - pe["origem"][0], pe["tornozelo"][1] - pe["origem"][1])
            r, piv2 = b.rotsprite(pe["img"], ang + giro_pe, piv)
            b.colar(tela, r, int(round(tx - piv2[0])), int(round(ty - piv2[1])))
    # o braço de trás (com o cajado) é o de perto: por cima das pontas da faixa e do casco
    _pele(kit, pose, w, tela, "braco_tras", ("tronco",))
    antes = tela[..., 3] > 0
    tela = pf.fechar_frestas(tela, juntas=[w[sl][0] for sl in OSSOS])
    tela[(tela[..., 3] > 0) & ~antes & (furo[..., 3] > 0)] = 0
    # o manto comprido arrasta no chão quando o corpo abaixa (pisão): nada passa da linha do chão
    tela[CHAO + 1:] = 0
    return quantizar(pf.sem_migalha(tela, minimo=40))


# ------------------------------------------------------------------ poses
def plantar(pose, lados=("tras", "frente"), pes=(0, 0)):
    """Pernas no chão por IK: o tornozelo fica onde está no parado (mais o passo `pes`, trás e frente, em px 3x).
    Perna não estica: se o quadril subiu além do alcance, o corpo desce até o casco encostar."""
    for _ in range(2):
        w = b.mundo(pose)
        descer = 0.0
        for lado in lados:
            coxa, canela = f"coxa_{lado}", f"canela_{lado}"
            qr, jr, tr = OSSOS[coxa][0], OSSOS[canela][0], TORNOZELO[canela]
            L = np.hypot(*np.subtract(jr, qr)) + np.hypot(*np.subtract(tr, jr)) - 1.5
            q = w[coxa][0]
            t = (tr[0] + pes[0 if lado == "tras" else 1], tr[1])
            ddx = t[0] - q[0]
            if abs(ddx) < L:
                descer = max(descer, (t[1] - np.sqrt(L * L - ddx * ddx)) - q[1])
        if descer > 0:
            pose["quadril"] = dict(pose["quadril"], dy=pose["quadril"].get("dy", 0) + float(np.ceil(descer)))
    w = b.mundo(pose)
    qang = w["quadril"][1]
    for lado in lados:
        coxa, canela = f"coxa_{lado}", f"canela_{lado}"
        qr, jr, tr = OSSOS[coxa][0], OSSOS[canela][0], TORNOZELO[canela]
        t = (tr[0] + pes[0 if lado == "tras" else 1], tr[1])
        c1, c2 = pf.ik(w[coxa][0], t, jr, qr, tr)
        rel = lambda a: round(float((a + 180) % 360 - 180), 1)  # noqa: E731 (sem volta inteira no meio do caminho)
        pose[coxa], pose[canela] = {"ang": rel(c1 - qang)}, {"ang": rel(c2)}
    return pose


def _p(dx=0, dy=0, q=0, tronco=0, cab=0, bt=0, bf=0, pes=(0, 0), coxa_f=None, canela_f=None, pe_f=None):
    """Pose à mão (graus horários na tela; + inclina o corpo para a frente, para o oponente): corpo (dx, dy a partir do
    parado), giro do quadril, do tronco sobre o quadril e da cabeça sobre o tronco, braço de trás (cajado) e da frente
    (garra). Pernas plantadas por IK; `coxa_f`/`canela_f` soltam a perna da frente (joelho no ar), com o casco girando
    `pe_f` além da canela."""
    configurar()
    pose = {"quadril": {"ang": q, "dx": dx, "dy": dy}, "tronco": {"ang": tronco}, "cabeca": {"ang": cab},
            "braco_tras": {"ang": bt}, "braco_frente": {"ang": bf}}
    if coxa_f is None:
        return plantar(pose, pes=pes)
    pose = plantar(pose, lados=("tras",), pes=pes)
    pose["coxa_frente"] = {"ang": coxa_f}
    pose["canela_frente"] = {"ang": canela_f or 0, "pe": pe_f or 0}
    return pose


# Poses-chave dos três golpes que mais aparecem (o rascunho de cada uma, normalizado ao tamanho do parado, só guiou a
# pose; ele está ao lado de cada pose em docs/boneco-pecas/gbzin/grao_pastor_poses.png).
POSES = {
    # parado: a guarda é o próprio desenho-mestre (o parado respira e as pontas balançam: vida.respirar e atrasar)
    "e_referencia_ginga/00": {},
    # chifrada (x): recua o peso para o casco de trás com o queixo erguido (antecipação curta), e explode para a
    # frente: o quadril vai primeiro (passo do casco da frente, joelhos afundam), o tronco cai sobre ele e a cabeça
    # baixa por último com os chifres na frente (Lei 1). A garra (mão livre) desce para fora da linha da cabeça e o
    # cajado vai para trás de contrapeso (Lei 5); os dois cascos plantados. Volta pela base e assenta na guarda.
    "e_chifrada/01": _p(dx=-6, dy=-2, q=-3, tronco=-5, cab=-10, bt=6, bf=-8),
    "e_chifrada/02": _p(dx=18, dy=14, q=6, tronco=10, cab=14, bt=12, bf=20, pes=(4, 22)),
    "e_chifrada/03": _p(dx=8, dy=6, q=2, tronco=4, cab=4, bt=5, bf=8, pes=(2, 12)),
    "e_chifrada/07": _p(dx=2, dy=2, pes=(0, 4)),
    # estampido (chute alto): o peso passa todo para o casco de trás (o umbigo em cima dele, Lei 3), o joelho da frente
    # sobe até a faixa (câmara, perna de longe atrás da faixa) com o tronco para trás de contrapeso e a garra no alto;
    # o casco desce com o corpo inteiro caindo junto (pisão: o corpo afunda 40 px e vai à frente), o casco planta
    # um passo à frente e a onda sai do chão. Levanta pela base larga e volta à guarda.
    "e_estampido/03": _p(dx=-8, dy=-6, tronco=-6, cab=4, bt=6, bf=-20, coxa_f=-85, canela_f=80),
    "e_estampido/04": _p(dx=8, dy=40, q=4, tronco=8, cab=-4, bt=10, bf=10, pes=(0, 26)),
    "e_estampido/06": _p(dx=6, dy=20, q=2, tronco=4, bt=4, bf=4, pes=(0, 18)),
    "e_estampido/07": _p(dy=4, pes=(0, 8)),
    "e_estampido/00": _p(),
}
# o que o jogo mostra hoje em cada elemento da ação (desenho do rascunho, ticks), lido do .air e do remap do
# despertado: 10200 = 566/567/568/572 -> 970/971/972/976 = e_chifrada 01/02/03/07; 10240 = 422..428 -> 826..832 =
# e_estampido 03/04/04/06/07/00 (ordem do GRAO_PASTOR no gerar_gbzin.py). O parado (ação 0) tem 16 elementos de 2 e
# 3 ticks depois da ligação da forma base.
ATUAL = {
    "parado": [("e_referencia_ginga/00", t) for t in (2, 3) * 8],
    "chifrada": [("e_chifrada/01", 4), ("e_chifrada/02", 6), ("e_chifrada/03", 3), ("e_chifrada/07", 6)],
    "estampido": [("e_estampido/03", 5), ("e_estampido/04", 10), ("e_estampido/06", 3), ("e_estampido/07", 12),
                  ("e_estampido/00", 12)],
}
ACAO = {"parado": 0, "chifrada": 10200, "estampido": 10240}
# elemento que bate (índice em ATUAL) e Clsn1 do .air (px 3x, relativo aos pés)
CAIXA = {"chifrada": (1, (30, -360, 150, -225)), "estampido": (1, (30, -237, 201, -102))}


def quadros_de(nome):
    """(pose, ticks, caixa, desenho) de cada desenho do golpe, com a vida: meio só na volta e na guarda (nada entre a
    antecipação e o contato: vida.animar segura a antecipação e o contato), respiração no parado e atraso da cabeça
    e das pontas da faixa."""
    elems = ATUAL[nome]
    laco = nome == "parado"
    if laco:  # um desenho só que respira: um quadro por elemento do jogo (16), sem salto do último para o primeiro
        quadros = [(dict(POSES[q]), t, False, q) for q, t in elems]
        quadros = vida.respirar(quadros)
    else:
        bate, _ = CAIXA[nome]
        quadros = vida.animar(POSES, elems, bate=bate, laco=False, guarda=POSES["e_referencia_ginga/00"])
    quadros = vida.atrasar(quadros, laco=laco)
    # o atraso da cabeça fica dentro da régua (até 4,5% do osso do pescoço)
    lim = 0.045 * float(np.hypot(*np.subtract(OSSOS["cabeca"][2], OSSOS["cabeca"][0])))
    for pose, _, _, _ in quadros:
        c = pose.get("cabeca", {})
        d = float(np.hypot(c.get("dx", 0), c.get("dy", 0)))
        if d > lim:
            c["dx"], c["dy"] = c["dx"] * lim / d, c["dy"] * lim / d
    return quadros


# ------------------------------------------------------------------ robô de defeitos e régua
def regua(pose):
    """Maior escorregão de junta (px que o filho anda além da mãe) sobre o comprimento do osso, em %. O desenho de cada
    peça não muda de tamanho (RotSprite sem escala), então o osso mede sempre o mesmo; o que pode mudar é a junta."""
    pior = (0.0, "")
    for slot, (j, mae, ponta) in OSSOS.items():
        if mae is None:
            continue
        p = pose.get(slot, {})
        desl = float(np.hypot(p.get("dx", 0), p.get("dy", 0)))
        L = float(np.hypot(ponta[0] - j[0], ponta[1] - j[1]))
        if 100 * desl / L > pior[0]:
            pior = (100 * desl / L, slot)
    return pior


def retas(tela, L=16):
    """Linha de corte: px de beira reta (horizontal ou vertical, L px ou mais) entre duas cores chapadas por dentro
    do corpo. Pixel art à mão quase não tem; emenda de peça e pintura por baixo com borda reta têm."""
    dentro = cv2.erode((tela[..., 3] > 0).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    c = tela[..., :3].astype(np.int32)
    c = (c[..., 0] << 16) | (c[..., 1] << 8) | c[..., 2]
    tot = 0
    for cc, dd in ((c, dentro), (c.T, dentro.T)):
        a, bb = cc[:-1], cc[1:]
        ok = (a != bb) & dd[:-1] & dd[1:]
        mesmo = ok[:, :-1] & ok[:, 1:] & (a[:, :-1] == a[:, 1:]) & (bb[:, :-1] == bb[:, 1:])
        for linha in mesmo:
            if not linha.any():
                continue
            d = np.diff(np.r_[0, linha.astype(int), 0])
            for i0, i1 in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
                if i1 - i0 + 1 >= L:
                    tot += int(i1 - i0 + 1)
    return tot


def conferir(tela, w, guarda_contorno, no_chao=True, juntas=tuple(OSSOS)):
    """Defeitos do quadro (vazio = passou):
      solta     pedaço de figura separado do resto (membro descolado, migalha)
      fresta    buraco perto de uma junta (peça desgrudou)
      chão      casco fora do chão (o pixel mais baixo tem que ficar no 659, como no parado)
      cor       cor fora das 15 da paleta travada
      corte     beira reta entre cores chapadas por dentro do corpo a mais que no parado (linha de corte à vista)"""
    erros = []
    al = (tela[..., 3] > 0).astype(np.uint8)
    n, _, st, _ = cv2.connectedComponentsWithStats(al, connectivity=8)
    soltos = sorted(int(x) for x in st[1:, 4] if x >= 4)[:-1]
    if soltos:
        erros.append(f"solta {soltos}")
    k_ = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    buraco = (cv2.morphologyEx(al, cv2.MORPH_CLOSE, k_) > 0) & (al == 0)
    for slot in juntas:
        x, y = w[slot][0]
        m = np.zeros_like(al)
        cv2.circle(m, (int(round(x)), int(round(y))), 14, 1, -1)
        if (buraco & (m > 0)).sum() > 6:
            erros.append(f"fresta em {slot}")
    ys = np.nonzero(al.any(1))[0]
    if no_chao and not (CHAO - 2 <= ys.max() <= CHAO + 1):
        erros.append(f"chão: casco em y={ys.max()}")
    pal = {tuple(c) for c in paleta().tolist()}
    fora = {tuple(c) for c in tela[al > 0][:, :3].tolist()} - pal
    if fora:
        erros.append(f"{len(fora)} cor(es) fora da paleta")
    c = retas(tela)
    if c > guarda_contorno + 16:
        erros.append(f"corte: {c} px de beira reta por dentro do corpo (parado {guarda_contorno})")
    return erros


def gravar(kit, nome, quadros):
    for pasta in (SAIDA_HD, SAIDA_1X):
        shutil.rmtree(pasta / nome, ignore_errors=True)
        (pasta / nome).mkdir(parents=True)
    guarda_c = retas(desenhar_pele(kit, {}))
    linhas = []
    for i, (pose, t, caixa, q) in enumerate(quadros):
        out = desenhar_pele(kit, pose)
        # joelho de perna plantada não é emenda: a perna inteira é um desenho só deformado pela malha (o vão entre as
        # pontas de pelo da barra da calça, que no agachado fica na altura do joelho, é do desenho)
        juntas = [s_ for s_ in OSSOS if not (s_.startswith("canela") and not no_ar(pose, s_.split("_")[1]))]
        erros = conferir(out, b.mundo(pose), guarda_c, juntas=juntas)
        pior, osso = regua(pose)
        if pior > 5:
            erros.append(f"régua: junta de {osso} andou {pior:.1f}% do osso")
        linhas.append(f"| {nome}/{i:02d} | {q} | {t} | {'sim' if caixa else ''} | {pior:.1f}% {osso} | "
                      f"{'PASS' if not erros else 'FAIL ' + '; '.join(erros)} |")
        Image.fromarray(out).save(SAIDA_HD / nome / f"{i:02d}.png")
        Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(SAIDA_1X / nome / f"{i:02d}.png")
    cx = CAIXA.get(nome, (None, None))[1]
    tempos = {"acao": ACAO[nome], "caixa": list(cx) if cx else None,
              "origem": list(dict.fromkeys(q for _, _, _, q in quadros)),
              "elementos": [{"desenho": i, "ticks": t, "caixa": c, "de": q} for i, (_, t, c, q) in enumerate(quadros)]}
    assert sum(e["ticks"] for e in tempos["elementos"]) == sum(t for _, t in ATUAL[nome])
    for pasta in (SAIDA_HD, SAIDA_1X):
        (pasta / nome / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False), encoding="utf-8")
    return linhas


def animar(nomes=None):
    nomes = nomes or list(ATUAL)
    kit = ler_kit()
    linhas = ["| desenho | pose-chave (guia) | ticks | caixa | régua (pior junta) | robô de defeitos |",
              "|---|---|---|---|---|---|"]
    for nome in nomes:
        quadros = quadros_de(nome)
        linhas += gravar(kit, nome, quadros)
        print(nome, len(dict.fromkeys(q for q, _ in ATUAL[nome])), "poses-chave ->", len(quadros), "desenhos")
    Image.fromarray(desenhar_pele(kit, {})).save(SAIDA_HD / "guarda.png")
    (SAIDA_HD / "poses.json").write_text(json.dumps(POSES, indent=1, default=float), encoding="utf-8")
    falhas = sum("FAIL" in l for l in linhas)
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "grao_pastor_robo.md").write_text(
        "# Grão-Pastor no boneco de peças: robô de defeitos e régua\n\n`python ferramentas/kit_grao_pastor.py animar`"
        " (solta, fresta na junta, casco fora do chão, cor fora da paleta, linha de corte; régua: junta que anda mais "
        "de 5% do osso).\n\n" + "\n".join(linhas) + f"\n\n{falhas} desenho(s) com defeito de {len(linhas) - 2}.\n",
        encoding="utf-8")
    print(f"robô: {falhas} desenho(s) com defeito de {len(linhas) - 2}")
    return falhas


def prova_kit():
    """Porta do kit (regra, seção 4): o kit remonta o parado sem diferença. Grava a prova lado a lado."""
    kit = ler_kit()
    ref = abrir(REF)
    out = desenhar_pele(kit, {})
    dif = np.abs(out.astype(int) - ref.astype(int)).sum(-1) > 0
    x0, y0, x1, y1 = 410, 285, 690, 670
    tiras = []
    for img in (ref, out):
        bg = Image.new("RGBA", (1080, 780), (60, 60, 70, 255))
        bg.alpha_composite(Image.fromarray(img))
        tiras.append(bg.crop((x0, y0, x1, y1)).convert("RGB"))
    d = np.full((780, 1080, 3), 30, np.uint8)
    d[ref[..., 3] > 0] = (70, 70, 80)
    d[dif] = (255, 0, 0)
    tiras.append(Image.fromarray(d).crop((x0, y0, x1, y1)))
    folha = Image.new("RGB", ((x1 - x0) * 3, y1 - y0))
    for i, t in enumerate(tiras):
        folha.paste(t, ((x1 - x0) * i, 0))
    folha = folha.resize((folha.width * 2, folha.height * 2), Image.NEAREST)
    ImageDraw.Draw(folha).text((10, 10), f"parado | kit remontado | diferença: {int(dif.sum())} px", fill=(255, 255, 0))
    folha.save(DOCS / "grao_pastor_kit_remonta.png")
    print(f"kit remonta o parado: {int(dif.sum())} px diferentes")
    return int(dif.sum())


# ------------------------------------------------------------------ provas: poses, antes/depois e vídeo lado a lado
CORTE = (380, 250, 760, 670)
FUNDO = (60, 60, 70, 255)


def _tela(img, caixa=None, rotulo=None, z=1):
    bg = Image.new("RGBA", (1080, 780), FUNDO)
    bg.alpha_composite(img if isinstance(img, Image.Image) else Image.fromarray(img))
    d = ImageDraw.Draw(bg)
    if caixa:
        x0, y0, x1, y1 = caixa
        d.rectangle([540 + x0, 660 + y0, 540 + x1, 660 + y1], outline=(255, 60, 60, 255), width=2)
    c = bg.crop(CORTE).convert("RGB")
    if z != 1:
        c = c.resize((c.width * z, c.height * z), Image.NEAREST)
    if rotulo:
        ImageDraw.Draw(c).text((6, 4), rotulo, fill=(255, 255, 0))
    return c


def _ticks(nome):
    """[(antes, depois, caixa)] tick a tick: antes = o rascunho que o jogo mostra hoje, depois = o desenho do kit."""
    tempos = json.loads((SAIDA_HD / nome / "tempos.json").read_text(encoding="utf-8"))
    antes = []
    for q, t in ATUAL[nome]:
        antes += [HD / f"{q}.png"] * t
    depois = []
    for e in tempos["elementos"]:
        cx = tuple(tempos["caixa"]) if e["caixa"] and tempos.get("caixa") else None
        depois += [(SAIDA_HD / nome / f"{e['desenho']:02d}.png", cx)] * e["ticks"]
    assert len(antes) == len(depois)
    return [(a, d, c) for a, (d, c) in zip(antes, depois)]


def provas():
    """docs/boneco-pecas/gbzin/: grao_pastor_poses.png (rascunho guia x pose do kit), grao_pastor_antes_depois.png
    (cada elemento do jogo, hoje e com o kit, mesma escala) e grao_pastor_lado_a_lado.mp4 (60 fps, tick a tick)."""
    import subprocess
    import tempfile
    kit = ler_kit()
    # poses-chave: o rascunho (no tamanho dele) e a pose do kit
    chaves = [q for q in POSES if q != REF]
    W, H = CORTE[2] - CORTE[0], CORTE[3] - CORTE[1]
    folha = Image.new("RGB", (W * 2, H * len(chaves)), (40, 40, 48))
    for i, q in enumerate(chaves):
        nome = "chifrada" if "chifrada" in q else "estampido"
        bate = q == ATUAL[nome][CAIXA[nome][0]][0]
        cx = CAIXA[nome][1] if bate else None
        folha.paste(_tela(abrir(q), cx, f"rascunho {q}"), (0, H * i))
        folha.paste(_tela(desenhar_pele(kit, POSES[q]), cx, "kit"), (W, H * i))
    folha.save(DOCS / "grao_pastor_poses.png")
    # antes e depois: um quadro por elemento do jogo
    linhas = []
    for nome in ATUAL:
        tk = _ticks(nome)
        vistos, el = set(), []
        for i, (a, d, c) in enumerate(tk):
            if (a, d) not in vistos:
                vistos.add((a, d))
                el.append((i, a, d, c))
        linhas.append((nome, el))
    cols = max(len(el) for _, el in linhas)
    z = 0.5
    w2, h2 = int(W * z), int(H * z)
    folha = Image.new("RGB", (w2 * cols, h2 * 2 * len(linhas)), (40, 40, 48))
    d = ImageDraw.Draw(folha)
    for r, (nome, el) in enumerate(linhas):
        for c_, (i, a, dd, cx) in enumerate(el):
            folha.paste(_tela(Image.open(a).convert("RGBA"), cx).resize((w2, h2), Image.NEAREST), (w2 * c_, h2 * 2 * r))
            folha.paste(_tela(Image.open(dd).convert("RGBA"), cx).resize((w2, h2), Image.NEAREST),
                        (w2 * c_, h2 * (2 * r + 1)))
            d.text((w2 * c_ + 4, h2 * 2 * r + 4), f"{nome} tick {i} hoje", fill=(255, 255, 0))
            d.text((w2 * c_ + 4, h2 * (2 * r + 1) + 4), "kit", fill=(120, 255, 120))
    folha.save(DOCS / "grao_pastor_antes_depois.png")
    # vídeo lado a lado: cada golpe 3 vezes, 60 fps
    with tempfile.TemporaryDirectory() as tmp:
        n = 0
        for nome in ATUAL:
            tk = _ticks(nome)
            for _ in range(3):
                for i, (a, dd, cx) in enumerate(tk):
                    q = Image.new("RGB", (W * 4, H * 2 + 40), (30, 30, 36))
                    q.paste(_tela(Image.open(a).convert("RGBA"), cx, z=2), (0, 40))
                    q.paste(_tela(Image.open(dd).convert("RGBA"), cx, z=2), (W * 2, 40))
                    ImageDraw.Draw(q).text((8, 10), f"Grão-Pastor {nome} (ação {ACAO[nome]}) tick {i}: hoje (rascunho) "
                                                    f"| boneco de peças", fill=(255, 255, 255))
                    q.save(Path(tmp) / f"{n:05d}.png")
                    n += 1
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "60", "-i", str(Path(tmp) / "%05d.png"),
                        "-pix_fmt", "yuv420p", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                        str(DOCS / "grao_pastor_lado_a_lado.mp4")], check=True)
    print("provas em", DOCS.relative_to(RAIZ))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "kit":
        montar_kit()
        prova_kit()
    elif len(sys.argv) > 1 and sys.argv[1] == "animar":
        animar(sys.argv[2:] or None)
    elif len(sys.argv) > 1 and sys.argv[1] == "provas":
        provas()
