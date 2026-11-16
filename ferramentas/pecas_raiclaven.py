#!/usr/bin/env python3
"""Kit de peças do Raiclaven (boneco de peças, método "corpo firme + vida" aprovado no Pengaró em 16/11).

O desenho de referência é o parado arcade (quadros_arcade_hd/ginga/00, 3x). Ele é cortado em peças em cor cheia:

  cabeca         cabeça, cabelo, barba e pescoço
  tronco         camisa, gola, ombros e o poste de barbeiro do peito
  braco_tras     o braço mecânico inteiro (ombreira, braço, mão) com a tesoura grande na mão
  braco_frente   o braço de carne (manga, braço, antebraço, mão) com o pente
  quadril        avental, cinto e o laço do avental
  coxa_*/canela_* as pernas da calça larga, com o sapato separado (fica reto no chão)

O resto do método (encaixe peça por peça em cima do quadro de hoje, juntas presas, sobra na junta, RotSprite em cor
cheia) é o do ferramentas/boneco_ajuste.py, que este módulo configura para o Raiclaven: depois de `import
pecas_raiclaven`, as funções do boneco_ajuste (`b.desenhar`, `b.encaixar`, `b.mundo`...) usam o kit dele.

  python ferramentas/pecas_raiclaven.py        recorta o kit em sprites/raiclaven/pecas/ (PNG + kit.json)
  python ferramentas/pecas_raiclaven.py ver    folha com o recorte pintado por peça (docs/boneco-pecas/raiclaven/)
"""
import json
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import boneco_ajuste as b  # noqa: E402

RAIZ = AQUI.parent
SPR = RAIZ / "sprites" / "raiclaven"
DOCS = RAIZ / "docs" / "boneco-pecas" / "raiclaven"

# ------------------------------------------------------------------ geometria, medida no ginga/00 em 3x
CINTO = 486  # linha do cinto: acima é tronco, abaixo é quadril e pernas

CABECA = [(521, 330), (528, 312), (560, 300), (595, 312), (600, 345), (597, 366), (590, 382), (577, 393),
          (556, 394), (540, 388), (528, 374), (521, 356)]
BRACO_FRENTE = [(580, 400), (594, 390), (594, 360), (602, 350), (602, 298), (642, 298),
                (642, 344), (656, 346), (662, 372), (655, 410), (648, 437), (600, 440), (586, 434), (580, 418)]
# braço de carne em duas peças: manga + bíceps (curto, visto de frente) e antebraço + mão + pente
ANTEBRACO_FRENTE = [(603, 440), (601, 412), (610, 402), (612, 392), (604, 374), (612, 358), (612, 336), (616, 308),
                    (642, 306), (642, 344), (656, 346), (664, 372), (661, 402), (653, 422), (646, 441)]
# braço mecânico + tesoura: ombreira, braço, cotovelo, antebraço, mão e as duas lâminas
# o pente sozinho (gira entre os dedos no parado), por trás da mão
PENTE = [(604, 300), (648, 300), (648, 339), (636, 341), (631, 356), (614, 356), (604, 346)]
BRACO_TRAS = [(444, 372), (466, 351), (504, 349), (517, 364), (519, 398), (510, 428), (503, 446), (540, 452),
              (575, 445), (610, 437), (638, 432), (642, 442), (600, 457), (572, 468), (604, 481), (642, 495),
              (642, 509), (602, 506), (566, 499), (546, 506), (500, 492), (470, 482), (453, 476), (436, 466),
              (427, 446), (432, 420), (437, 395)]
OMBREIRA = [(428, 403), (430, 380), (444, 372), (466, 351), (504, 349), (517, 364), (519, 399), (505, 403), (484, 400),
            (470, 397), (450, 397)]
BRACO_MECANICO = [(431, 404), (440, 393), (486, 393), (488, 410), (484, 436), (472, 445), (456, 443), (442, 438),
                  (431, 430)]
AVENTAL = [(481, 484), (592, 488), (599, 579), (560, 585), (502, 584), (486, 576)]
LACO = [(424, 478), (474, 478), (480, 500), (462, 534), (424, 534)]
PERNA_TRAS = [(436, 492), (470, 488), (494, 498), (500, 560), (516, 578), (514, 604), (502, 628), (482, 640),
              (482, 664), (416, 664), (416, 620), (430, 560), (432, 520)]
PERNA_FRENTE = [(556, 495), (602, 500), (642, 532), (656, 556), (654, 604), (642, 626), (668, 642), (672, 664),
                (566, 664), (566, 630), (558, 600), (560, 584), (595, 580)]
# o que os braços escondem no parado: tapado no kit (pintado por baixo), senão abre buraco quando o braço sai
PEITO_ESCONDIDO = [(570, 392), (592, 388), (600, 404), (600, 425), (594, 446), (570, 452)]
LADO_ESCONDIDO = [(474, 350), (522, 350), (522, 486), (476, 486), (470, 462), (468, 440), (470, 420),
                  (474, 402)]
AVENTAL_ESCONDIDO = [(480, 440), (600, 440), (600, 510), (480, 510)]
CINTO_ESCONDIDO = [(442, 478), (584, 482), (584, 496), (442, 496)]
COXA_ESCONDIDA = [(596, 492), (645, 492), (645, 512), (596, 512)]

# o que fica escondido debaixo do avental: a coxa continua por baixo (pintada no kit), senão abre fresta quando o
# quadril desce ou a perna gira
COXA_TRAS_OCULTA = [(476, 492), (520, 492), (524, 584), (480, 584)]
COXA_FRENTE_OCULTA = [(548, 496), (598, 496), (600, 584), (548, 584)]

CONTORNO = (34, 18, 30)  # cor do contorno do desenho (roxo quase preto)
JOELHO_TRAS, JOELHO_FRENTE = (456, 598), (630, 586)
OSSOS = {  # junta (pivô) no parado, peça mãe, ponta (para a régua)
    "quadril": ((530, 510), None, (530, 560)),
    "tronco": ((530, 484), "quadril", (560, 390)),
    "cabeca": ((560, 388), "tronco", (562, 330)),
    "ombreira": ((470, 392), "tronco", (480, 360)),
    "braco_tras": ((462, 398), "tronco", (447, 448)),
    "antebraco_tras": ((447, 448), "braco_tras", (525, 474)),
    "braco_frente": ((594, 410), "tronco", (606, 432)),
    "coxa_tras": ((490, 520), "quadril", JOELHO_TRAS),
    "canela_tras": (JOELHO_TRAS, "coxa_tras", (446, 634)),
    "coxa_frente": ((572, 524), "quadril", JOELHO_FRENTE),
    "canela_frente": (JOELHO_FRENTE, "coxa_frente", (612, 632)),
}
CAMADAS = ["coxa_tras", "canela_tras", "coxa_frente", "canela_frente", "tronco", "cabeca", "quadril",
           "braco_frente", "braco_tras", "ombreira", "antebraco_tras"]
TORNOZELO = {"canela_tras": (446, 632), "canela_frente": (612, 630)}
CHAO = 659

VARIANTES = {}  # preenchido por golpe (piloto_raiclaven.py)


def configurar():
    """Aponta o boneco_ajuste para o Raiclaven."""
    b.SPR, b.HD, b.PECAS = SPR, SPR / "quadros_arcade_hd", SPR / "pecas"
    b.REF = "ginga/00"
    b.OSSOS, b.CAMADAS, b.VARIANTES = OSSOS, CAMADAS, VARIANTES
    b.BUSCA = {
        "quadril": (range(-6, 7, 2), 30, [None]),
        "tronco": (range(-10, 11, 2), 3, [None]),
        "cabeca": (range(-10, 11, 2), 3, [None]),
        "ombreira": (range(-6, 7, 2), 2, [None]),
        "braco_tras": (range(-30, 31, 2), 3, [None]),
        "antebraco_tras": (range(-30, 31, 2), 3, [None]),
        "braco_frente": (range(-30, 31, 2), 3, [None]),

        "coxa_tras": (range(-30, 31, 2), 2, [None]),
        "canela_tras": (range(-30, 31, 2), 2, [None]),
        "coxa_frente": (range(-30, 31, 2), 2, [None]),
        "canela_frente": (range(-30, 31, 2), 2, [None]),
    }
    b.ORDEM = ["quadril", "tronco", "cabeca", "braco_tras", "antebraco_tras", "braco_frente",
               "coxa_tras", "canela_tras", "coxa_frente", "canela_frente"]


configurar()


def limpar_franja(img):
    """Fiapos roxos soltos em volta do pente (sobra do fundo magenta da folha): some com pedacinhos separados e com
    pixel roxo-escuro isolado fora do contorno."""
    img = img.copy()
    al = (img[..., 3] > 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(al, connectivity=8)
    out = img.copy()
    maior = 1 + int(np.argmax(st[1:, 4])) if n > 1 else 0
    for i in range(1, n):
        if i != maior and st[i, 4] < 400:
            out[lab == i] = 0
    return out


def cor_base(img):
    """Cor cheia da roupa da peça: a mediana dos pixels escuros (camisa preta, avental)."""
    a = img[..., 3] > 0
    rgb = img[..., :3].astype(int)
    v = rgb.max(-1)
    m = a & (v >= 18) & (v <= 55)
    return np.median(rgb[m], axis=0).astype(np.uint8) if m.any() else np.array(CONTORNO, np.uint8)


def pintar(img, reg, contorno=True, friso=()):
    """Pinta `reg` na cor cheia da peça e põe contorno onde a parte pintada encosta no vazio. `friso`: segmentos
    onde o debrum claro do avental continua por baixo da tesoura (2 px, na cor do debrum que aparece)."""
    out = img.copy()
    out[reg, :3] = cor_base(img)
    out[reg, 3] = 255
    if friso:
        hsv = cv2.cvtColor(np.ascontiguousarray(img[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
        claro = (img[..., 3] > 0) & (hsv[..., 2] > 150) & (hsv[..., 1] < 70) & ~reg
        cor = np.median(img[claro][:, :3], axis=0).astype(np.uint8) if claro.any() else (170, 160, 180)
        linha = np.zeros(reg.shape, np.uint8)
        for (x0, y0), (x1, y1) in friso:
            cv2.line(linha, (int(x0), int(y0)), (int(x1), int(y1)), 1, 2)
        m = (linha > 0) & reg
        out[m, :3] = cor
    if contorno:
        a = out[..., 3] > 0
        borda = a & ~(cv2.erode(a.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & reg
        out[borda, :3] = CONTORNO
    return out


def sem_farelo(img, minimo=40):
    al = (img[..., 3] > 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(al, connectivity=8)
    out = img.copy()
    for i in range(1, n):
        if st[i, 4] < minimo:
            out[lab == i] = 0
    return out


def montar_kit():
    P = b.PECAS
    if P.exists():
        shutil.rmtree(P)
    P.mkdir(parents=True)
    ref = limpar_franja(b.abrir(b.REF))
    alfa = ref[..., 3] > 0
    yy, xx = np.mgrid[:b.TELA[1], :b.TELA[0]]
    M = b.mascara
    baixo = yy >= CINTO
    m_bt = M(BRACO_TRAS) & alfa
    # o contorno escuro das lâminas fica com o braço (senão sobra uma cunha preta no cinto quando a tesoura sai)
    m_bt |= (cv2.dilate(m_bt.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & alfa & (yy > 440) & ~M(AVENTAL)
    m_omb = M(OMBREIRA) & m_bt
    m_bm = M(BRACO_MECANICO) & m_bt & ~m_omb
    m_abt = m_bt & ~m_omb & ~m_bm
    m_bf = M(BRACO_FRENTE) & alfa & ~m_bt
    # o braço do pente fica numa peça só (girar o cotovelo e o pente abria emenda no bíceps e espalhava os dentes)
    m_pente = np.zeros_like(m_bf)
    m_abf = np.zeros_like(m_bf)
    m_bf1 = m_bf & ~m_abf & ~m_pente
    m_cab = M(CABECA) & alfa & ~m_bf & ~m_bt
    avental = (M(AVENTAL) | M(LACO)) & alfa & ~m_bt
    pt = baixo & M(PERNA_TRAS) & alfa & ~m_bt & ~avental
    pf = baixo & M(PERNA_FRENTE) & alfa & ~m_bt & ~avental
    resto = baixo & alfa & ~m_bt & ~avental & ~pt & ~pf
    dt = cv2.distanceTransform(np.uint8(~pt), cv2.DIST_L2, 3)
    df = cv2.distanceTransform(np.uint8(~pf), cv2.DIST_L2, 3)
    perto = resto & (yy >= 575)  # calça entre as pernas, abaixo do avental
    pt |= perto & (dt <= df)
    pf |= perto & (df < dt)
    quadril = baixo & alfa & ~m_bt & ~pt & ~pf
    partes = {
        "cabeca": m_cab,
        "ombreira": m_omb,
        "braco_tras": m_bm,
        "antebraco_tras": m_abt,
        "braco_frente": m_bf1,
        "tronco": ~baixo & alfa & ~m_bt & ~m_bf & ~m_cab,
        "coxa_tras": pt & (yy < JOELHO_TRAS[1]),
        "canela_tras": pt & (yy >= JOELHO_TRAS[1] - 12),
        "coxa_frente": pf & (yy < JOELHO_FRENTE[1]),
        "canela_frente": pf & (yy >= JOELHO_FRENTE[1] - 12),
        "quadril": quadril,
    }
    imgs = {k: np.where(m[..., None], ref, 0).astype(np.uint8) for k, m in partes.items()}
    # o que os braços escondem (peito atrás do braço do pente, lado e ombro atrás do braço mecânico, cinto atrás da
    # tesoura) é pintado na cor cheia da camisa/do avental, sem borrão, com contorno de 1 px na beira nova
    t = imgs["tronco"]
    esc_t = (M(PEITO_ESCONDIDO) | M(LADO_ESCONDIDO)) & ~baixo & (m_bf | m_bt | ~alfa) & ~(t[..., 3] > 0)
    esc_t &= ~(M(CABECA) & alfa)
    imgs["tronco"] = pintar(t, esc_t)
    q = imgs["quadril"]
    esc_q = ((M(AVENTAL_ESCONDIDO) & M(AVENTAL)) | M(CINTO_ESCONDIDO)) & baixo & m_bt
    imgs["quadril"] = pintar(q, esc_q, friso=[AVENTAL[1:3], AVENTAL[-1:] + AVENTAL[0:1]])
    # as coxas continuam por baixo do avental e da tesoura (calça pintada por baixo)
    for nome, oculta, extra in (("coxa_tras", COXA_TRAS_OCULTA, None), ("coxa_frente", COXA_FRENTE_OCULTA,
                                                                     COXA_ESCONDIDA)):
        reg = M(oculta) & (baixo | (yy >= 490))
        reg &= ~(imgs[nome][..., 3] > 0) & alfa & M(AVENTAL)  # só o que o avental cobre
        imgs[nome] = b.tapar(imgs[nome], reg, imgs[nome][..., 3] > 0)
    kit = {"ref": f"quadros_arcade_hd/{b.REF}.png", "pecas": {}}
    SOB = b.SOBRA

    # costura: a sobra das peças do corpo pega também a beira da peça mãe (5 px), para não abrir linha na cintura,
    # no joelho e entre a coxa e o avental quando as duas se mexem um pouco diferente
    costura = {"tronco": "quadril", "coxa_tras": "quadril", "coxa_frente": "quadril", "canela_tras": "coxa_tras",
               "canela_frente": "coxa_frente", "quadril": "tronco"}
    alfas = {k: v[..., 3] > 0 for k, v in imgs.items()}

    def guardar(nome, img, junta, mae, fonte=b.REF, fonte_img=None):
        a = img[..., 3] > 0
        ys, xs = np.nonzero(a)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        Image.fromarray(img[y0:y1, x0:x1]).save(P / f"{nome}.png")
        if fonte_img is None:
            fonte_img = ref
        disco = np.zeros(b.TELA[::-1], np.uint8)
        cv2.circle(disco, (int(junta[0]), int(junta[1])), SOB, 1, -1)
        perto = disco.astype(bool)
        if nome in costura:
            perto |= (cv2.dilate(a.astype(np.uint8), np.ones((11, 11), np.uint8)) > 0) & alfas[costura[nome]]
        sob = np.where((perto & (fonte_img[..., 3] > 0))[..., None], fonte_img, 0).astype(np.uint8)
        pad = np.zeros((b.TELA[1] + 2 * SOB, b.TELA[0] + 2 * SOB, 4), np.uint8)
        pad[SOB:-SOB, SOB:-SOB] = sob
        Image.fromarray(pad[y0:y1 + 2 * SOB, x0:x1 + 2 * SOB]).save(P / f"{nome}_sobra.png")
        kit["pecas"][nome] = {"arquivo": f"{nome}.png", "origem": [int(x0), int(y0)], "junta": list(junta),
                              "mae": mae, "fonte": f"quadros_arcade_hd/{fonte}.png",
                              "sobra": f"{nome}_sobra.png", "origem_sobra": [int(x0 - SOB), int(y0 - SOB)]}

    for nome, img in imgs.items():
        junta, mae, _ = OSSOS[nome]
        if nome not in ("braco_frente", "ombreira", "braco_tras", "antebraco_tras"):
            img = sem_farelo(img)
        guardar(nome, img, junta, mae)
    for slot, vs in VARIANTES.items():
        junta, mae, _ = OSSOS[slot]
        for var, (fonte, poli, ancora, filtro) in vs.items():
            img, inteira = variante(fonte, poli, ancora, filtro, imgs)
            guardar(f"{slot}_{var}", img, junta, mae, fonte=fonte, fonte_img=inteira)
            print(f"{slot}_{var}: de {fonte} (preso pelo {ancora})")
    # peça vazia: o filho de uma variante que já traz o membro inteiro (antebraço na estocada, canela na perna)
    vazio = np.zeros((b.TELA[1], b.TELA[0], 4), np.uint8)
    vazio[0, 0] = (0, 0, 0, 1)
    for slot in ("antebraco_tras", "canela_frente"):
        guardar(f"{slot}_vazio", vazio, OSSOS[slot][0], OSSOS[slot][1])
    (P / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")
    return partes


# ------------------------------------------------------------------ variantes vindas de outro desenho
# O soco e o chute de hoje são de uma folha antiga, com o boneco ~5% menor. A variante (braço esticado, perna
# levantada) é recortada de lá, ampliada para a escala do kit (medida pela cabeça) e posta no lugar do kit pelo
# avental (pernas) ou pela cabeça (braços), então ela fica presa no corpo do jeito que estava no desenho.
def _ampliar(a, f, pivo):
    """Amplia (ou reduz) o RGBA f vezes em volta do pivô sem misturar cor (Scale2x x3 e amostragem)."""
    import corrigir_cabeca as cc
    return cc.encolher(a, f, pivo)


def escala_e_canto(a):
    sys.path.insert(0, str(AQUI / "pixel"))
    import reguas
    cab = np.asarray(Image.open(b.PECAS / "cabeca.png").convert("RGBA"))[:70]
    e, nota, (x, y) = reguas.escala_cabeca(a, cab)
    return e, (int(x), int(y))


REF_CABECA = None


def variante(fonte, poli, ancora, filtro, imgs):
    """(peça, desenho inteiro) no espaço do kit."""
    global REF_CABECA
    f = limpar_franja(b.abrir(fonte))
    if REF_CABECA is None:
        REF_CABECA = escala_e_canto(b.abrir(b.REF))
    e_ref, c_ref = REF_CABECA
    e, c = escala_e_canto(f)
    k = e_ref / e
    big = _ampliar(f, k, c)
    if ancora == "chao":  # o pé de trás no chão é o mesmo ponto nos dois desenhos (o corte é pelos pés)
        c = (446, CHAO)
        big = _ampliar(f, k, c)
        dx, dy = 0, 0
    elif ancora == "cabeca":
        dx, dy = c_ref[0] - c[0], c_ref[1] - c[1]
    else:  # avental: a faixa do cinto ao bolso do quadril do kit casada no desenho ampliado
        q = imgs["quadril"]
        ys, xs = np.nonzero(q[..., 3] > 0)
        t = q[ys.min():ys.min() + 70, xs.min():xs.max() + 1]
        m = (t[..., 3] > 0).astype(np.uint8)
        F = 60
        Y0, X0 = max(0, ys.min() - F), max(0, xs.min() - F)
        reg = big[Y0:ys.min() + 70 + F, X0:xs.max() + 1 + F]
        cz = lambda a: np.where(a[..., 3:] > 0, a[..., :3], 110).astype(np.float32)
        r = cv2.matchTemplate(cz(reg), cz(t), cv2.TM_SQDIFF, mask=np.repeat(m[..., None], 3, -1))
        _, _, p, _ = cv2.minMaxLoc(r)
        dx, dy = xs.min() - (p[0] + X0), ys.min() - (p[1] + Y0)
    T = np.float32([[1, 0, dx], [0, 1, dy]])
    inteira = cv2.warpAffine(big, T, b.TELA, flags=cv2.INTER_NEAREST)
    msk = b.mascara(poli) & (f[..., 3] > 0)  # o polígono é medido no desenho de origem
    if filtro:
        msk &= ~filtro(f)
    so = np.where(msk[..., None], f, 0).astype(np.uint8)
    img = cv2.warpAffine(_ampliar(so, k, c), T, b.TELA, flags=cv2.INTER_NEAREST)
    n, lab, st, _ = cv2.connectedComponentsWithStats((img[..., 3] > 0).astype(np.uint8), connectivity=8)
    if n > 2:
        maior = 1 + int(np.argmax(st[1:, 4]))
        img[(lab != maior) & (lab > 0)] = 0
    print(f"  {fonte}: cabeça {e:.2f} -> escala {k:.3f}, deslocamento {dx:+d},{dy:+d}")
    return img, inteira


def pele(a):
    hsv = cv2.cvtColor(np.ascontiguousarray(a[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    m = (a[..., 3] > 0) & (hsv[..., 0] <= 22) & (hsv[..., 1] > 90) & (hsv[..., 2] > 70)
    return cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)


def claro(a):
    """Lâmina e friso do avental (cinza-lilás claro): fora da peça de calça."""
    hsv = cv2.cvtColor(np.ascontiguousarray(a[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    return (a[..., 3] > 0) & (hsv[..., 2] > 150) & (hsv[..., 1] < 80)


def pele_ou_claro_perto_do_corpo(a):
    m = pele(a) | claro(a)
    m[:, 600:] = pele(a)[:, 600:]  # o brilho do sapato fica
    return m


CORES = {"cabeca": (255, 200, 0), "tronco": (0, 160, 255), "braco_tras": (255, 60, 60), "braco_frente": (0, 220, 120),
         "ombreira": (255, 0, 160), "pente": (255, 255, 0), "antebraco_tras": (255, 120, 120), "antebraco_frente": (120, 255, 80),
         "quadril": (200, 80, 255), "coxa_tras": (255, 140, 0), "canela_tras": (160, 90, 0),
         "coxa_frente": (0, 255, 255), "canela_frente": (0, 120, 160)}


def ver():
    """Folha: o parado, o recorte pintado por peça e o kit remontado sem pose (tem que ser igual ao parado)."""
    DOCS.mkdir(parents=True, exist_ok=True)
    partes = montar_kit()
    ref = b.abrir(b.REF)
    cor = np.zeros_like(ref)
    for k, m in partes.items():
        cor[m, :3] = CORES[k]
        cor[m, 3] = 255
    mix = ref.copy()
    mix[..., :3] = (ref[..., :3] * 0.45 + cor[..., :3] * 0.55).astype(np.uint8)
    for x, y in [o[0] for o in OSSOS.values()]:
        cv2.circle(mix, (int(x), int(y)), 4, (255, 255, 255, 255), -1)
    kit = b.ler_kit()
    junto = b.desenhar(kit, {})
    corte = (380, 280, 700, 680)
    tiras = []
    for a in (ref, mix, junto):
        im = Image.new("RGBA", (b.TELA[0], b.TELA[1]), (235, 235, 240, 255))
        im.alpha_composite(Image.fromarray(a))
        tiras.append(im.crop(corte).resize(((corte[2] - corte[0]) * 2, (corte[3] - corte[1]) * 2), Image.NEAREST))
    folha = Image.new("RGB", (tiras[0].width * 3, tiras[0].height), (235, 235, 240))
    for i, t in enumerate(tiras):
        folha.paste(t.convert("RGB"), (i * t.width, 0))
    folha.save(DOCS / "kit_recorte.png")
    dif = np.abs(junto[..., :3].astype(int) - ref[..., :3].astype(int)).sum(-1)
    print("kit remontado x parado: pixels diferentes", int(((dif > 30) | ((junto[..., 3] > 0) != (ref[..., 3] > 0))).sum()))


if __name__ == "__main__":
    if sys.argv[1:] == ["ver"]:
        ver()
    else:
        montar_kit()
