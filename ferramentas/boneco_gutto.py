#!/usr/bin/env python3
"""Gutto pelo boneco de peças, método "corpo firme + vida" aprovado pelo Alisson no Pengaró (16/11).

Usa as mesmas ferramentas do piloto do Pengaró (boneco_ajuste.py, piloto_firme.py, vida_pecas.py), trocando só o que
é do desenho: os polígonos de cada peça e as juntas, medidos no parado do Gutto (sprite 94,0 do .sff, em 3x).

O Gutto não tem quadros_arcade_hd no git (o .sff dele vem do Blender), então os desenhos de hoje saem do próprio .sff
(ferramentas/extrair_hd_sff.py) numa tela 1080x780 com o eixo em (540, 660).

  python ferramentas/boneco_gutto.py kit            recorta o kit em sprites/gutto/pecas/ e grava a prova das peças
  python ferramentas/boneco_gutto.py animar [NOMES] monta parado, soco, chute_alto... em quadros_pecas_hd/quadros_pecas
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
import extrair_hd_sff as sff  # noqa: E402

RAIZ = AQUI.parent
SPR = RAIZ / "sprites" / "gutto"
HD = SPR / "quadros_sff_hd"
REF = "94_0"
PROVA = RAIZ / "docs" / "boneco-pecas" / "gutto"

# ------------------------------------------------------------------ medidas do parado do Gutto (94,0, 3x)
CABECA = [(526, 318), (610, 318), (612, 372), (602, 392), (584, 402), (566, 400), (548, 392), (536, 380), (526, 360)]
PESCOCO = [(540, 378), (556, 390), (572, 398), (588, 400), (588, 410), (560, 412), (536, 404)]
# braço de trás (o da esquerda, que cruza o peito com o punho na frente do abdome) com o cordão que pende
BRACO_TRAS = [(482, 388), (504, 384), (518, 396), (520, 420), (556, 422), (566, 438), (560, 462), (520, 466),
              (500, 470), (478, 474), (456, 470), (444, 470), (438, 452), (452, 428), (462, 404)]
BRACO_FRENTE = [(576, 410), (590, 402), (604, 398), (622, 392), (640, 386), (660, 396), (668, 420), (654, 446),
                (640, 470), (620, 484), (598, 482), (582, 474), (572, 452), (572, 430)]
PERNA_TRAS = [(478, 500), (520, 500), (548, 520), (546, 560), (532, 590), (510, 610), (490, 640), (488, 664),
              (430, 664), (440, 640), (462, 610), (476, 580), (480, 540)]
PERNA_FRENTE = [(548, 520), (560, 500), (590, 500), (612, 520), (632, 560), (626, 600), (616, 630), (640, 640),
                (666, 664), (575, 664), (586, 630), (596, 600), (590, 580), (560, 565)]
NO_DA_FAIXA = [(0, 0), (1, 0), (0, 1)]  # o Gutto não tem nó de faixa
# o que os braços tapam no tronco: o kit pinta por baixo para não abrir buraco quando o braço sai
PEITO_ESCONDIDO = [(500, 400), (580, 410), (600, 440), (596, 478), (500, 478), (488, 440)]
# o braço de trás do Gutto é a beira das costas (não tem tronco atrás dele): nada a tapar do lado
LADO_ESCONDIDO = [(0, 0), (1, 0), (0, 1)]
CALCA_ESCONDIDA = [(0, 0), (1, 0), (0, 1)]
JOELHO_TRAS, JOELHO_FRENTE = (516, 574), (612, 562)
TORNOZELO = {"canela_tras": (472, 636), "canela_frente": (606, 634)}
OSSOS = {
    "quadril": ((540, 500), None, (540, 530)),
    "tronco": ((540, 478), "quadril", (560, 400)),
    "cabeca": ((566, 396), "tronco", (568, 330)),
    "braco_tras": ((496, 400), "tronco", (520, 450)),
    "braco_frente": ((588, 418), "tronco", (630, 420)),
    "coxa_tras": ((514, 512), "quadril", JOELHO_TRAS),
    "canela_tras": (JOELHO_TRAS, "coxa_tras", TORNOZELO["canela_tras"]),
    "coxa_frente": ((574, 510), "quadril", JOELHO_FRENTE),
    "canela_frente": (JOELHO_FRENTE, "coxa_frente", TORNOZELO["canela_frente"]),
}
CAMADAS = ["coxa_tras", "canela_tras", "quadril", "tronco", "cabeca", "canela_frente", "coxa_frente", "braco_frente",
           "braco_tras"]


def cinto(x):
    return 474 + (x - 480) * 0.06


def configurar():
    """Aponta o boneco_ajuste para o Gutto (as funções de lá leem estes nomes do módulo)."""
    b.SPR, b.HD, b.PECAS, b.REF = SPR, HD, SPR / "pecas", REF
    for nome in ("CABECA", "PESCOCO", "BRACO_TRAS", "BRACO_FRENTE", "PERNA_TRAS", "PERNA_FRENTE", "NO_DA_FAIXA",
                 "PEITO_ESCONDIDO", "LADO_ESCONDIDO", "CALCA_ESCONDIDA", "JOELHO_TRAS", "JOELHO_FRENTE", "OSSOS",
                 "CAMADAS"):
        setattr(b, nome, globals()[nome])
    b.cinto = cinto
    b.VARIANTES = {"braco_frente": {}, "coxa_frente": {}}


def garantir_hd(nomes):
    """Grava em quadros_sff_hd os sprites que faltam (grupo_indice)."""
    falta = [n for n in nomes if not (HD / f"{n}.png").exists()]
    if not falta:
        return
    cores, sp = sff.sprites("gutto")
    HD.mkdir(parents=True, exist_ok=True)
    for n in falta:
        g, i = map(int, n.split("_"))
        Image.fromarray(sff.tela(cores, sp[(g, i)])).save(HD / f"{n}.png")


def prova_segmentos(saida):
    """Parado com cada peça pintada de uma cor e as juntas marcadas: confere os polígonos."""
    ref = b.abrir(REF)
    cores = {"cabeca": (255, 80, 80), "tronco": (80, 200, 255), "braco_tras": (255, 220, 0),
             "braco_frente": (0, 255, 120), "coxa_tras": (200, 120, 255), "canela_tras": (255, 140, 0),
             "coxa_frente": (255, 0, 200), "canela_frente": (0, 160, 255), "quadril": (160, 255, 160)}
    kit = b.ler_kit()
    tela = np.zeros_like(ref)
    tela[..., :3] = 40
    tela[..., 3] = 255
    out = tela.copy()
    for slot in CAMADAS:
        p = kit["pecas"][slot]
        im = p["img"]
        x0, y0 = p["origem"]
        h, w = im.shape[:2]
        m = im[..., 3] > 0
        sub = out[y0:y0 + h, x0:x0 + w]
        mix = (im[..., :3].astype(int) * 0.45 + np.array(cores[slot]) * 0.55).astype(np.uint8)
        sub[m, :3] = mix[m]
    for slot, (j, _, ponta) in OSSOS.items():
        cv2.circle(out, (int(j[0]), int(j[1])), 4, (255, 255, 255, 255), -1)
        cv2.line(out, (int(j[0]), int(j[1])), (int(ponta[0]), int(ponta[1])), (255, 255, 255, 255), 1)
    c = Image.fromarray(out).crop((400, 300, 700, 680))
    c.resize((c.width * 3, c.height * 3), Image.NEAREST).save(saida)


def kit():
    configurar()
    garantir_hd([REF])
    b.montar_kit()
    PROVA.mkdir(parents=True, exist_ok=True)
    prova_segmentos(PROVA / "kit_pecas.png")
    g = b.desenhar(b.ler_kit(), {})
    c = Image.fromarray(g).crop((400, 300, 700, 680))
    c.resize((c.width * 3, c.height * 3), Image.NEAREST).save(PROVA / "kit_montado.png")


# ------------------------------------------------------------------ variantes (peça que muda de desenho, não de ângulo)
# (desenho de onde sai, polígono, junta no desenho de origem: None = acha pelo tronco)
VARIANTES = {
    "braco_frente": {
        "cotovelo": ("970_0", [(548, 388), (575, 384), (595, 391), (625, 392), (655, 392), (668, 398), (670, 416),
                               (660, 424), (630, 426), (605, 430), (585, 432), (560, 428), (548, 410)], (562, 408)),
        "esticado": ("1252_0", [(588, 384), (640, 382), (680, 384), (700, 387), (726, 390), (728, 422), (700, 420),
                                (660, 414), (626, 422), (600, 428), (588, 410)], (606, 404)),
    },
    "coxa_tras": {  # perna de apoio esticada (chute): desenho inteiro da perna do 957, preso no quadril de trás
        "apoio": ("957_0", [(500, 505), (556, 500), (556, 540), (546, 570), (527, 600), (517, 630), (540, 648),
                            (548, 664), (466, 664), (476, 635), (494, 600), (504, 560), (499, 530)], (522, 512)),
    },
    "coxa_frente": {
        "camara": ("965_0", [(538, 420), (560, 414), (600, 424), (617, 440), (616, 470), (590, 493), (556, 502),
                             (550, 522), (506, 527), (503, 505), (518, 490), (536, 470)], (544, 440)),
        # perna esticada do chute baixo agachado de hoje (449): a mesma escala e grossura da perna do parado. A do 957
        # (desenho de lado, menor) saía fina e comprida, 61% da grossura do parado (régua das pernas, Breno 22/11)
        # leva junto a boca do calção (o desenho tem a coxa dentro dele): a perna sai do calção, sem fresta
        "esticada": ("449_0", [(532, 574), (562, 566), (600, 582), (640, 596), (700, 606), (748, 610), (756, 640),
                               (704, 662), (640, 652), (600, 642), (566, 640), (548, 636), (534, 612)], None),
        # perna dobrada do agachado (359): joelho para a frente, canela para baixo. É a câmara dos chutes agachados
        # (girar a câmara em pé do 965 virava uma bolota no agachado)
        "agachada": ("359_0", [(546, 536), (580, 528), (612, 540), (626, 560), (620, 600), (608, 626), (630, 644),
                               (632, 664), (552, 664), (556, 630), (566, 600), (556, 580), (546, 560)], None),
    },
}
# ângulo natural de cada variante (graus, do quadril até a ponta) contra a do 957 que as poses usavam: as poses abaixo
# somam este desvio para a perna nova ficar onde a velha ficava
GIRO_ESTICADA = -35
COM_CALCAO = {("coxa_frente", "esticada")}  # variantes que levam a boca do calção junto (não passam pelo so_pele)

TR_CAMARA, TR_ALTO = -4, -8     # tronco para trás na câmara e no chute alto (graus)
BF_CAMARA, BF_ALTO = 10, 25     # braço da frente descendo para trás da perna

# as animações: (ação do .air, elementos [(sprite, ticks, caixa?)], caixa de golpe)
ANIM = {
    "parado": (0, [("94_0", 9, 0), ("102_0", 9, 0), ("134_0", 9, 0), ("126_0", 9, 0)], None),
    "soco": (200, [("81_0", 3, 0), ("1278_0", 1, 0), ("1252_0", 5, 1), ("1252_0", 1, 0), ("84_0", 3, 0),
                   ("85_0", 6, 0)], (45, -276, 222, -192)),
    # estudo de anatomia (Breno, 17/11): perna da frente (longe) nasce atrás da faixa; na coxa alta o tronco vai para
    # trás e o braço do lado da perna (o da frente) desce um pouco, sem tapar o chute; a mão de trás fica no rosto.
    # (mandar o braço da guarda para trás do tronco com `_atras` deixou uma aba de ombro solta: pede desenho novo)
    "chute_alto": (240, [("422_0", 5, 0), ("423_0", 2, 0),
                         ("965_0", 1, 0, {"tronco": {"ang": TR_CAMARA}, "braco_frente": {"ang": BF_CAMARA}}),
                         ("966_0", 1, 0, {"tronco": {"ang": TR_CAMARA}, "braco_frente": {"ang": BF_CAMARA}}),
                         ("957_0", 6, 1, {"tronco": {"ang": TR_ALTO}, "braco_frente": {"ang": BF_ALTO}}),
                         ("957_0", 2, 0, {"tronco": {"ang": TR_ALTO}, "braco_frente": {"ang": BF_ALTO}}),
                         ("426_0", 7, 0, {"tronco": {"ang": TR_CAMARA}, "braco_frente": {"ang": BF_CAMARA}}),
                         ("427_0", 9, 0), ("428_0", 9, 0)],
                   (36, -300, 208, -174)),
    # golpes refeitos (lista dos confusos): o 4º campo força a pose de uma peça no lugar do encaixe
    # 1) soco forte: era mão atrás da cabeça + cotovelo + soco; agora é uma cotovelada só, com preparo e volta
    "soco_forte": (210, [("558_0", 4, 0), ("559_0", 2, 0, {"braco_frente": {"ang": -28}, "braco_tras": {"ang": -6}}),
                         ("984_0", 1, 0, {"braco_frente": {"ang": -30, "var": "cotovelo"}, "_dy": 2, "_pes": "558_0"}),
                         ("970_0", 6, 1, {"braco_frente": {"ang": 0, "var": "cotovelo"}, "_dy": 4, "_pes": "558_0"}),
                         ("970_0", 2, 0, {"braco_frente": {"ang": 6, "var": "cotovelo"}, "_dy": 4, "_pes": "558_0"}),
                         ("562_0", 7, 0, {"braco_frente": {"ang": -12}, "_dy": 1, "_pes": "558_0"}), ("563_0", 8, 0), ("564_0", 8, 0)],
                   (45, -276, 163, -192)),
    # cotovelo giratório / cotovelada pesada: o cotovelo sobe acima da cabeça e desce pesado (caixa alta)
    "cotovelo": (1400, [("558_0", 6, 0),
                        ("971_0", 1, 0, {"braco_frente": {"ang": -60, "var": "cotovelo"}, "_dy": -4, "_pes": "558_0"}),
                        ("972_0", 1, 0, {"braco_frente": {"ang": -38, "var": "cotovelo"}, "_dy": -2, "_pes": "558_0"}),
                        ("561_0", 6, 1, {"braco_frente": {"ang": 22, "var": "cotovelo"}, "_dy": 8, "_pes": "558_0"}),
                        ("561_0", 2, 0, {"braco_frente": {"ang": 26, "var": "cotovelo"}, "_dy": 8, "_pes": "558_0"}),
                        ("562_0", 8, 0, {"braco_frente": {"ang": -12}, "_dy": 3, "_pes": "558_0"}), ("563_0", 7, 0), ("564_0", 7, 0)],
                 (27, -294, 170, -144)),
    # chute giratório (coice): era costas, frente com joelho e chute com outro tronco. Agora: câmara, coice reto na
    # altura da barriga (perna esticada deitada), segura e recolhe
    "coice": (1100, [("526_0", 6, 0), ("1043_0", 1, 0, {"coxa_frente": {"ang": 20, "var": "camara"}}),
                     ("1044_0", 3, 0, {"coxa_frente": {"ang": 4, "var": "camara"}, "braco_frente": {"ang": -10}}),
                     ("1013_0", 6, 1, {"coxa_frente": {"ang": 34 + GIRO_ESTICADA, "var": "esticada"}, "braco_frente": {"ang": -14}}),
                     ("1019_0", 6, 1, {"coxa_frente": {"ang": 30 + GIRO_ESTICADA, "var": "esticada"}, "braco_frente": {"ang": -14}}),
                     ("529_0", 6, 1, {"coxa_frente": {"ang": 32 + GIRO_ESTICADA, "var": "esticada"}, "braco_frente": {"ang": -12}}),
                     ("1034_0", 6, 0, {"coxa_frente": {"ang": 6, "var": "camara"}}),
                     ("1034_0", 2, 0, {"coxa_frente": {"ang": 14, "var": "camara"}}),
                     ("531_0", 10, 0), ("532_0", 9, 0)],
              (-120, -240, 206, -60)),
    # joelhada voadora: era de costas e com a perna esticada. Agora: agacha, sobe com o joelho na frente do peito,
    # a perna de trás dobrada atrás, e cai na guarda
    "joelhada": (1200, [("535_0", 2, 0, {"_dy": 5, "_base": "94_0"}),
                        ("1061_0", 1, 0, {"_dy": 8, "_base": "94_0", "braco_frente": {"ang": 8}}),
                        ("1062_0", 7, 0, {"_dy": 10, "_base": "94_0", "braco_frente": {"ang": 10},
                                          "braco_tras": {"ang": 6}}),
                        # Time = 10: o CNS tira do chão
                        ("1050_0", 9, 1, {"coxa_frente": {"ang": -16, "var": "camara"}, "coxa_tras": {"ang": 30},
                                          "canela_tras": {"ang": 44}, "braco_frente": {"ang": -24},
                                          "braco_tras": {"ang": -8}, "_ar": 1, "_y": -24}),
                        ("1050_0", 2, 0, {"coxa_frente": {"ang": -12, "var": "camara"}, "coxa_tras": {"ang": 28},
                                          "canela_tras": {"ang": 40}, "braco_frente": {"ang": -18}, "_ar": 1, "_y": -24}),
                        ("1045_0", 5, 0, {"coxa_frente": {"ang": 4, "var": "camara"}, "coxa_tras": {"ang": 18},
                                          "canela_tras": {"ang": 26}, "_ar": 1, "_y": -20}),
                        ("538_0", 5, 0, {"coxa_frente": {"ang": -16}, "canela_frente": {"ang": 26},
                                         "coxa_tras": {"ang": 10}, "canela_tras": {"ang": 14}, "_ar": 1, "_y": -12}),
                        ("539_0", 1, 0, {"coxa_frente": {"ang": -8}, "canela_frente": {"ang": 12},
                                         "coxa_tras": {"ang": 6}, "canela_tras": {"ang": 8}, "_ar": 1, "_y": -4})],
                 (0, -390, 169, -90)),
    # chute de quina: era o chute fraco com outro nome. Agora: chute baixo na canela, perna esticada para baixo
    "quina": (1500, [("415_0", 6, 0), ("935_0", 1, 0, {"coxa_frente": {"ang": 40, "var": "camara"}}),
                     ("936_0", 1, 0, {"coxa_frente": {"ang": 46 + GIRO_ESTICADA, "var": "esticada"}}),
                     ("417_0", 6, 1, {"coxa_frente": {"ang": 58 + GIRO_ESTICADA, "var": "esticada"}, "braco_frente": {"ang": 8}}),
                     ("417_0", 2, 0, {"coxa_frente": {"ang": 56 + GIRO_ESTICADA, "var": "esticada"}}),
                     ("418_0", 8, 0, {"coxa_frente": {"ang": 36, "var": "camara"}}), ("419_0", 7, 0),
                     ("420_0", 7, 0)],
              (24, -111, 192, -6)),
    # chute forte de longe: começava com o joelho já em cima. Agora: guarda, joelho sobe, chute na altura do peito
    "chute_forte": (260, [("550_0", 6, 0), ("551_0", 4, 0, {"coxa_frente": {"ang": 26, "var": "camara"}}),
                          ("1001_0", 1, 0, {"coxa_frente": {"ang": 6, "var": "camara"}}),
                          ("1002_0", 1, 0, {"coxa_frente": {"ang": 0, "var": "camara"}}),
                          ("992_0", 6, 1, {"coxa_frente": {"ang": 14 + GIRO_ESTICADA, "var": "esticada"}}),
                          ("992_0", 2, 0, {"coxa_frente": {"ang": 16 + GIRO_ESTICADA, "var": "esticada"}}),
                          ("991_0", 5, 0, {"coxa_frente": {"ang": 4, "var": "camara"}}),
                          ("554_0", 5, 0, {"coxa_frente": {"ang": 18, "var": "camara"}}), ("555_0", 9, 0),
                          ("556_0", 9, 0)],
                    (45, -300, 189, -180)),
    # SUPER 3000 Chuva de Beijinhos: guarda, abaixa juntando força, joelho sobe, chute alto e fica no joelho
    # enquanto os beijinhos (3010/3011, ajudantes) voam. Sem caixa própria: quem bate são os beijinhos
    "super_beijinhos": (3000, [("573_0", 9, 0, {"_base": "94_0"}),
                               ("574_0", 9, 0, {"_base": "94_0", "_dy": 8, "braco_frente": {"ang": 10},
                                                "braco_tras": {"ang": 8}}),
                               ("575_0", 9, 0, {"_base": "965_0"}), ("576_0", 9, 0, {"_base": "957_0"}),
                               ("577_0", 9, 0, {"_base": "965_0"}), ("577_0", 15, 0, {"_base": "965_0"}),
                               ("577_0", 36, 0, {"_base": "965_0"})], None),
    # SUPER 3100 Bando de Chutes: misturava costas, frente, rasteira com a mão no chão e socos de outro tronco. Agora
    # é uma sequência só de frente com as peças: joelho, jab, joelhada, chute baixo, jab, chute alto, joelhada,
    # chute baixo, chute alto e volta. Mesmos ticks; caixa = a maior das 9 (o .air muda só a largura, 128 a 220)
    "super_chutes": (3100, [("202_0", 7, 0, {"_base": "965_0"}),
                            ("199_0", 6, 1, {"_base": "94_0", "braco_frente": {"ang": 4, "var": "esticado"}}),
                            ("203_0", 6, 1, {"_base": "965_0", "coxa_frente": {"ang": -14, "var": "camara"}}),
                            ("210_0", 6, 1, {"_base": "417_0", "coxa_frente": {"ang": 58 + GIRO_ESTICADA, "var": "esticada"}}),
                            ("200_0", 6, 1, {"_base": "94_0", "braco_frente": {"ang": 2, "var": "esticado"}}),
                            ("204_0", 6, 1, {"_base": "957_0"}),
                            ("222_0", 6, 1, {"_base": "965_0", "coxa_frente": {"ang": -14, "var": "camara"}}),
                            ("211_0", 6, 1, {"_base": "417_0", "coxa_frente": {"ang": 56 + GIRO_ESTICADA, "var": "esticada"}}),
                            ("225_0", 6, 1, {"_base": "957_0"}),
                            ("225_0", 2, 0, {"_base": "957_0", "coxa_frente": {"ang": 4 + GIRO_ESTICADA, "var": "esticada"}}),
                            ("205_0", 28, 0, {"_base": "426_0"})],
                     (0, -330, 220, -30)),
    # agachado: o corpo do parado desce (o mesmo tronco e rosto), joelhos dobram, respira
    "agachado": (11, [("359_0", 6, 0, {"_base": "359_0"})] * 8, None),  # 48 ticks como a ação 11 do jogo
    # soco agachado: começava com o braço já esticado e terminava na guarda. Agora: guarda baixa, jab, volta
    "soco_agachado": (400, [("432_0", 2, 0, {"_base": "359_0"}),
                            ("432_0", 1, 0, {"_base": "359_0", "braco_frente": {"ang": -10}}),
                            ("432_0", 1, 0, {"_base": "359_0", "braco_frente": {"ang": 14, "var": "esticado"}}),
                            ("433_0", 2, 1, {"_base": "359_0", "braco_frente": {"ang": 4, "var": "esticado"}}),
                            ("433_0", 3, 1, {"_base": "359_0", "braco_frente": {"ang": 4, "var": "esticado"}}),
                            ("433_0", 1, 0, {"_base": "359_0", "braco_frente": {"ang": 8, "var": "esticado"}}),
                            ("435_0", 5, 0, {"_base": "359_0", "braco_frente": {"ang": -6}}),
                            ("436_0", 4, 0, {"_base": "359_0"})],
                      (45, -168, 162, -126)),
    # chute baixo agachado: perna da frente esticada rente ao chão, a de trás dobrada
    "chute_baixo_agachado": (430, [("447_0", 3, 0, {"_base": "359_0"}),
                                   ("447_0", 1, 0, {"_base": "359_0", "_sem_apoio": 1,
                                                    "coxa_frente": {"ang": -10, "var": "agachada"}}),
                                   ("1146_0", 1, 0, {"_base": "359_0", "_sem_apoio": 1,
                                                     "coxa_frente": {"ang": 52 + GIRO_ESTICADA, "var": "esticada"}}),
                                   ("449_0", 5, 1, {"_base": "359_0", "_sem_apoio": 1,
                                                    "coxa_frente": {"ang": 46 + GIRO_ESTICADA, "var": "esticada"}}),
                                   ("449_0", 1, 0, {"_base": "359_0", "_sem_apoio": 1,
                                                    "coxa_frente": {"ang": 48 + GIRO_ESTICADA, "var": "esticada"}}),
                                   ("450_0", 5, 0, {"_base": "359_0", "_sem_apoio": 1,
                                                    "coxa_frente": {"ang": -10, "var": "agachada"}}),
                                   ("450_0", 4, 0, {"_base": "359_0"}), ("452_0", 4, 0, {"_base": "359_0"})],
                             (36, -54, 186, -12)),
    # chute alto agachado: ficava em pé no meio. Agora chuta para cima sem levantar, apoiado na perna de trás
    "chute_alto_agachado": (410, [("438_0", 3, 0, {"_base": "359_0"}),
                                  ("439_0", 2, 0, {"_base": "359_0", "_sem_apoio": 1,
                                                   "coxa_frente": {"ang": -20, "var": "agachada"}}),
                                  ("1128_0", 2, 0, {"_base": "359_0", "_sem_apoio": 1,
                                                    "coxa_frente": {"ang": -40, "var": "agachada"}}),
                                  ("1118_0", 8, 1, {"_base": "359_0", "_sem_apoio": 1,
                                                    "coxa_frente": {"ang": -20 + GIRO_ESTICADA, "var": "esticada"}}),
                                  ("1118_0", 2, 0, {"_base": "359_0", "_sem_apoio": 1,
                                                    "coxa_frente": {"ang": -16 + GIRO_ESTICADA, "var": "esticada"}}),
                                  ("442_0", 7, 0, {"_base": "359_0", "_sem_apoio": 1,
                                                   "coxa_frente": {"ang": -24, "var": "agachada"}}),
                                  ("443_0", 9, 0, {"_base": "359_0"}), ("444_0", 9, 0, {"_base": "359_0"})],
                            (15, -366, 126, -180)),
    # rasteira (chute forte agachado): mais baixo e mais longo que o chute baixo
    "rasteira": (440, [("454_0", 5, 0, {"_base": "359_0"}),
                       ("455_0", 3, 0, {"_base": "359_0", "_sem_apoio": 1,
                                        "coxa_frente": {"ang": -6, "var": "agachada"}}),
                       ("1163_0", 1, 0, {"_base": "359_0", "_sem_apoio": 1,
                                         "coxa_frente": {"ang": 53 + GIRO_ESTICADA, "var": "esticada"}}),
                       ("1164_0", 1, 0, {"_base": "359_0", "_sem_apoio": 1,
                                         "coxa_frente": {"ang": 53 + GIRO_ESTICADA, "var": "esticada"}}),
                       ("457_0", 6, 1, {"_base": "359_0", "_sem_apoio": 1,
                                        "coxa_frente": {"ang": 54 + GIRO_ESTICADA, "var": "esticada"}}),
                       ("457_0", 2, 0, {"_base": "359_0", "_sem_apoio": 1,
                                        "coxa_frente": {"ang": 53 + GIRO_ESTICADA, "var": "esticada"}}),
                       ("1153_0", 5, 0, {"_base": "359_0", "_sem_apoio": 1,
                                         "coxa_frente": {"ang": -4, "var": "agachada"}}),
                       ("458_0", 5, 0, {"_base": "359_0"}),
                       # volta da rasteira (o jogo tem 48 ticks: sem isso o golpe acabava 20 ticks antes)
                       ("459_0", 5, 0, {"_base": "359_0"}), ("1173_0", 5, 0, {"_base": "359_0"}),
                       ("460_0", 10, 0, {"_base": "359_0"})],
                 (36, -54, 207, -6)),
}
AGACHADOS = {"agachado", "soco_agachado", "chute_baixo_agachado", "chute_alto_agachado", "rasteira"}
PERNA = {"423_0": "camara", "965_0": "camara", "966_0": "camara", "957_0": "esticada", "426_0": "camara"}


_MOLDE = None


def corpo(kit, alvo, folga_x=100, folga_y=(-50, 70)):
    """(dx, dy) do tronco do parado no quadro, só por translação (corpo firme). O molde é o tronco e a cabeça como
    aparecem no parado (sem os braços, sem o que eles tapam): o pedaço tapado do kit é chute, não serve de molde.
    Custo = diferença de cor, com fundo transparente contando como erro cheio (assim ele não "casa" no vazio)."""
    global _MOLDE
    if _MOLDE is None:
        ref = b.abrir(REF)
        yy, xx = np.mgrid[:ref.shape[0], :ref.shape[1]]
        m = (ref[..., 3] > 0) & (yy < cinto(xx)) & ~b.mascara(BRACO_TRAS) & ~b.mascara(BRACO_FRENTE)
        m = cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        sel = m[y0:y1, x0:x1]
        _MOLDE = (x0, y0, ref[y0:y1, x0:x1, :3].astype(np.int16)[sel], sel)
    x0, y0, cor, sel = _MOLDE
    h, w = sel.shape
    H, W = alvo.shape[:2]

    def custo(dx, dy):
        X, Y = x0 + dx, y0 + dy
        if X < 0 or Y < 0 or X + w > W or Y + h > H:
            return 1e9
        a = alvo[Y:Y + h, X:X + w][sel]
        d = np.minimum(np.abs(a[:, :3].astype(np.int16) - cor).mean(1), 120)
        d[a[:, 3] == 0] = 120
        return float(d.mean())

    melhor = min(((custo(dx, dy), dx, dy) for dy in range(folga_y[0], folga_y[1] + 1, 3)
                  for dx in range(-folga_x, folga_x + 1, 3)))
    _, bx, by = melhor
    melhor = min(((custo(dx, dy), dx, dy) for dy in range(by - 3, by + 4) for dx in range(bx - 3, bx + 4)))
    return melhor[1], melhor[2]


def configurar_piloto():
    import piloto_firme as pf
    pf.corpo = corpo
    pf.TORNOZELO = TORNOZELO
    pf.CHAO = 659
    pf.FOLGA_CORPO = 90
    pf.PES_REF = None
    pf.RAIZ_DOCS = PROVA
    return pf


def montar_com_variantes(pf):
    """Kit com as variantes presas na junta certa: a junta de origem sai do tronco achado no desenho de origem."""
    b.VARIANTES = {k: {v: (f, p, jf or OSSOS[k][0]) for v, (f, p, jf) in vs.items()} for k, vs in VARIANTES.items()}
    b.montar_kit()
    kit = b.ler_kit()
    for slot, vs in VARIANTES.items():
        for var, (fonte, poli, jf) in vs.items():
            garantir_hd([fonte])
            if jf is None:
                dx, dy = corpo(kit, b.abrir(fonte), folga_y=(-50, 150))
                j = OSSOS[slot][0]
                jf = (j[0] + dx, j[1] + dy)
                print(f"{slot}_{var}: tronco em {fonte} a {dx:+d},{dy:+d}")
            b.VARIANTES[slot][var] = (fonte, poli, jf)
    b.montar_kit()
    kit = json.loads((b.PECAS / "kit.json").read_text(encoding="utf-8"))
    # a perna levantada é só a perna (pele e contorno): o calção e o pé de apoio do desenho de origem ficam de fora
    for slot in ("coxa_frente", "coxa_tras"):
        for var in VARIANTES[slot]:
            if (slot, var) not in COM_CALCAO:
                so_pele(b.PECAS / kit["pecas"][f"{slot}_{var}"]["arquivo"])
            aparar(kit, f"{slot}_{var}")
        calcao_no_quadril(kit, slot)
    limpar_contorno_dos_bracos(kit)
    tronco_inteiro(kit)


def calcao_no_quadril(kit, slot="coxa_frente"):
    """A boca do calção da perna da frente vai para o quadril: quando a perna levanta (ou troca pelo desenho do
    chute), o calção fica inteiro no lugar e a coxa sai de dentro dele, sem buraco preto."""
    cf, qd = kit["pecas"][slot], kit["pecas"]["quadril"]
    a = np.asarray(Image.open(b.PECAS / cf["arquivo"]).convert("RGBA")).copy()
    q = np.asarray(Image.open(b.PECAS / qd["arquivo"]).convert("RGBA"))
    hsv = cv2.cvtColor(np.ascontiguousarray(a[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    al = a[..., 3] > 0
    pele = al & (hsv[..., 0] <= 25) & (hsv[..., 1] > 70) & (hsv[..., 2] > 50)
    perto = cv2.dilate(pele.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    calcao = al & ~perto
    ox, oy = cf["origem"]
    qx, qy = qd["origem"]
    x0, y0 = min(ox, qx), min(oy, qy)
    x1 = max(ox + a.shape[1], qx + q.shape[1])
    y1 = max(oy + a.shape[0], qy + q.shape[0])
    novo = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    novo[qy - y0:qy - y0 + q.shape[0], qx - x0:qx - x0 + q.shape[1]] = q
    sub = novo[oy - y0:oy - y0 + a.shape[0], ox - x0:ox - x0 + a.shape[1]]
    sub[calcao] = a[calcao]
    # pele solta no meio do calção (resto da coxa que ficou no quadril) vira calção
    hq = cv2.cvtColor(np.ascontiguousarray(novo[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    yy = np.arange(novo.shape[0])[:, None] + y0
    pele_q = (novo[..., 3] > 0) & (hq[..., 0] <= 25) & (hq[..., 1] > 70) & (hq[..., 2] > 50) & (yy > 498)
    if pele_q.any():
        rgb = cv2.inpaint(np.ascontiguousarray(novo[..., :3]), pele_q.astype(np.uint8), 3, cv2.INPAINT_TELEA)
        novo[pele_q, :3] = rgb[pele_q]
    Image.fromarray(novo).save(b.PECAS / qd["arquivo"])
    qd["origem"] = [int(x0), int(y0)]
    a[calcao] = 0
    Image.fromarray(a).save(b.PECAS / cf["arquivo"])
    (b.PECAS / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")


def aparar(kit, nome):
    """Recorta a peça no que sobrou depois do so_pele (a origem acompanha), para a régua e o kit verem só a perna."""
    p = kit["pecas"][nome]
    arq = b.PECAS / p["arquivo"]
    im = np.asarray(Image.open(arq).convert("RGBA"))
    ys, xs = np.nonzero(im[..., 3] > 0)
    if not len(ys):
        return
    Image.fromarray(im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]).save(arq)
    p["origem"] = [int(p["origem"][0] + xs.min()), int(p["origem"][1] + ys.min())]
    (b.PECAS / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")


def so_pele(arq):
    im = np.asarray(Image.open(arq).convert("RGBA")).copy()
    hsv = cv2.cvtColor(np.ascontiguousarray(im[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    al = im[..., 3] > 0
    pele = al & (hsv[..., 0] <= 25) & (hsv[..., 1] > 70) & (hsv[..., 2] > 50)
    n, lab, st, _ = cv2.connectedComponentsWithStats(pele.astype(np.uint8), connectivity=8)
    if n > 1:  # só o pedaço de pele maior (a perna); pele de outra parte que entrou no polígono sai
        pele = lab == (1 + int(np.argmax(st[1:, 4])))
    pele = cv2.morphologyEx(pele.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0
    contorno = (cv2.dilate(pele.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & al & \
        (im[..., :3].astype(int).sum(-1) < 200)
    # mancha escura grossa encostada na perna (sombra do calção do desenho de origem) não é contorno
    grosso = cv2.morphologyEx(contorno.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    contorno &= ~(cv2.dilate(grosso.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    manter = (pele & al) | contorno
    im[~manter] = 0
    Image.fromarray(im).save(arq)


# silhueta do tronco sem os braços (o que fica atrás deles): o kit pinta por dentro só com cor de pele vizinha
PEITO_DE = "558_0"
TRONCO_INTEIRO = [(484, 394), (506, 384), (530, 378), (548, 380), (572, 398), (592, 402), (594, 412), (590, 440),
                  (584, 460), (578, 478), (486, 478), (478, 450), (478, 420)]


def tronco_inteiro(kit):
    """Tapa o peito e o abdome que os braços escondem no parado: pinta por dentro da silhueta do tronco com a cor da
    pele em volta (o contorno escuro e o fundo não entram na mistura) e fecha a beira com contorno de 1 px."""
    pe = kit["pecas"]["tronco"]
    arq = b.PECAS / pe["arquivo"]
    im = np.asarray(Image.open(arq).convert("RGBA"))
    ox, oy = pe["origem"]
    tela = np.zeros((b.TELA[1], b.TELA[0], 4), np.uint8)
    tela[oy:oy + im.shape[0], ox:ox + im.shape[1]] = im
    # o que sobrou do tronco fora da silhueta, perto do braço da frente (sombra e cordão do braço), sai: quando o
    # braço sai dali, isso ficaria boiando
    fora = ~b.mascara(TRONCO_INTEIRO) & (cv2.dilate(b.mascara(BRACO_FRENTE).astype(np.uint8),
                                                     np.ones((15, 15), np.uint8)) > 0)
    fora &= np.mgrid[:b.TELA[1], :b.TELA[0]][0] > 418  # o ombro em cima é a junta do braço: fica
    # essa sombra é do braço (fica entre o cotovelo e o corpo): passa para a peça do braço e anda com ele
    pb = kit["pecas"]["braco_frente"]
    arq_b = b.PECAS / pb["arquivo"]
    ib = np.asarray(Image.open(arq_b).convert("RGBA"))
    bx, by = pb["origem"]
    tb = np.zeros_like(tela)
    tb[by:by + ib.shape[0], bx:bx + ib.shape[1]] = ib
    passa = fora & (tela[..., 3] > 0) & (tb[..., 3] == 0)
    tb[passa] = tela[passa]
    ys, xs = np.nonzero(tb[..., 3] > 0)
    Image.fromarray(tb[ys.min():ys.max() + 1, xs.min():xs.max() + 1]).save(arq_b)
    pb["origem"] = [int(xs.min()), int(ys.min())]
    tela[fora] = 0
    silh = b.mascara(TRONCO_INTEIRO) | (tela[..., 3] > 0)
    rgb = tela[..., :3].astype(int)
    escuro = rgb.sum(-1) < 210
    hsv = cv2.cvtColor(np.ascontiguousarray(tela[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    roxo = (hsv[..., 0] >= 125) & (hsv[..., 0] <= 175) & (hsv[..., 1] > 60)
    branco = (rgb.min(-1) > 150) & (np.ptp(rgb, -1) < 60)
    bom = (tela[..., 3] > 0) & ~escuro & ~roxo & ~branco & (hsv[..., 1] >= 60)
    dentro = b.mascara(TRONCO_INTEIRO)
    # só o que o braço tapava no parado (vazio no kit, cheio no parado): o desenho à mostra fica como está
    ref_a = b.abrir(REF)[..., 3] > 0
    bracos_ref = (b.mascara(BRACO_TRAS) | b.mascara(BRACO_FRENTE)) & ref_a
    buraco = dentro & ref_a & (bracos_ref | (tela[..., 3] == 0))
    # o peito que o braço tapa no parado aparece aberto no 558 (guarda aberta): vem de lá, no lugar do tronco achado
    doador = b.abrir(PEITO_DE)
    dx, dy = corpo(kit, doador)
    M = np.float32([[1, 0, -dx], [0, 1, -dy]])
    doador = cv2.warpAffine(doador, M, b.TELA, flags=cv2.INTER_NEAREST)
    hd = cv2.cvtColor(np.ascontiguousarray(doador[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    pele_d = (doador[..., 3] > 0) & (hd[..., 0] <= 25) & (hd[..., 1] > 90) & (hd[..., 2] < 235) & \
        (doador[..., :3].astype(int).sum(-1) >= 150)
    # longe das faixas brancas das mãos do 558 (o brilho delas puxa a pele para o branco)
    faixa_d = (doador[..., :3].min(-1) > 170) & (doador[..., 3] > 0)
    pele_d &= ~(cv2.dilate(faixa_d.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0)
    vem = buraco & pele_d
    # a pele do 558 é mais clara: casa a cor média com a pele do parado em volta
    pele_k = bom & (hsv[..., 0] <= 25)
    ref_c = tela[pele_k][:, :3].astype(float).mean(0)
    doa_c = doador[pele_d][:, :3].astype(float).mean(0)
    cor = np.clip(doador[..., :3].astype(float) * (ref_c / doa_c), 0, 255).astype(np.uint8)
    tela[vem, :3] = cor[vem]
    tela[vem, 3] = 255
    bom |= vem
    buraco &= ~vem
    print(f"tronco: {int(vem.sum())} px do peito aberto do {PEITO_DE}")
    preenchido = buraco.copy()
    if buraco.any():
        pint = cv2.inpaint(np.ascontiguousarray(tela[..., :3]), (~bom).astype(np.uint8), 6, cv2.INPAINT_TELEA)
        tela[buraco, :3] = pint[buraco]
        tela[buraco, 3] = 255
    # beira do peito tapado que dá para o fundo: contorno de 1 px, como o resto do desenho
    cheio = tela[..., 3] > 0
    beira = preenchido & cheio & ~(cv2.erode(cheio.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    tela[beira, :3] = (46, 20, 26)
    # resto do cordão do braço (branco e roxo) perto do braço da frente: some
    hsv = cv2.cvtColor(np.ascontiguousarray(tela[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    cordao = (tela[..., 3] > 0) & ((hsv[..., 1] < 60) | ((hsv[..., 0] >= 125) & (hsv[..., 0] <= 175))) & \
        ~b.mascara(TRONCO_INTEIRO) & (cv2.dilate(b.mascara(BRACO_FRENTE).astype(np.uint8),
                                                  np.ones((15, 15), np.uint8)) > 0)
    tela[cordao] = 0
    ys, xs = np.nonzero(tela[..., 3] > 0)
    y0, x0 = ys.min(), xs.min()
    Image.fromarray(tela[y0:ys.max() + 1, x0:xs.max() + 1]).save(arq)
    pe["origem"] = [int(x0), int(y0)]
    (b.PECAS / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"tronco: {int(buraco.sum())} px tapados por dentro")


def limpar_contorno_dos_bracos(kit):
    """Contorno escuro dos braços do parado que ficou no tronco: vira a cor de volta (só no tronco; o calção do Gutto
    é preto e não entra)."""
    ref = b.abrir(REF)
    bracos = (b.mascara(BRACO_TRAS) | b.mascara(BRACO_FRENTE)) & (ref[..., 3] > 0)
    perto = cv2.dilate(bracos.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    pe = kit["pecas"]["tronco"]
    arq = b.PECAS / pe["arquivo"]
    im = np.asarray(Image.open(arq).convert("RGBA")).copy()
    ox, oy = pe["origem"]
    h, w = im.shape[:2]
    dentro = cv2.erode((im[..., 3] > 0).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    hsv = cv2.cvtColor(np.ascontiguousarray(im[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    roxo = (hsv[..., 0] >= 125) & (hsv[..., 0] <= 175) & (hsv[..., 1] > 60)  # contorno roxo do braço
    escuro = ((im[..., :3].astype(int).sum(-1) < 150) | roxo) & dentro & perto[oy:oy + h, ox:ox + w]
    if escuro.any():
        rgb = cv2.inpaint(np.ascontiguousarray(im[..., :3]), escuro.astype(np.uint8), 4, cv2.INPAINT_TELEA)
        im[escuro, :3] = rgb[escuro]
        Image.fromarray(im).save(arq)
        print(f"tronco: {int(escuro.sum())} px de contorno de braço tirados")


def separar_pes(kit):
    """Pé separado da canela (fica reto no chão, preso no tornozelo). O Gutto luta descalço: o pé é só pele."""
    kit["pes"] = {}
    for slot, (tx, ty) in TORNOZELO.items():
        p = kit["pecas"][slot]
        img = p["img"].copy()
        ox, oy = p["origem"]
        corte = ty - oy
        pe = np.zeros_like(img)
        pe[corte:] = img[corte:]
        img[corte + 3:] = 0
        p["img"] = img
        kit["pes"][slot] = {"img": pe, "origem": (ox, oy), "tornozelo": (tx, ty),
                            "fundo": int(np.nonzero(pe[..., 3].any(1))[0].max())}
    return kit


# agachado: da cintura para baixo é o desenho do agachado de hoje (359,0), um desenho só e sempre o mesmo. Dobrar as
# peças da perna em pé até o agachado fundo quebrava o joelho em lascas. A perna da frente sai à parte (só pele) para
# os chutes agachados poderem trocá-la pelo desenho da perna do chute.
AGACHADO = "359_0"
PERNA_FRENTE_AGACHADA = [(546, 536), (580, 528), (612, 540), (626, 560), (620, 600), (608, 626), (630, 644),
                         (632, 664), (552, 664), (556, 630), (566, 600), (556, 580), (546, 560)]
_BAIXO = {}


def baixo_agachado(kit):
    """(lower body sem a perna da frente, perna da frente) do agachado, em coordenadas do kit (tronco no lugar do
    parado), e o deslocamento do corpo no 359."""
    if _BAIXO:
        return _BAIXO
    a = b.abrir(AGACHADO)
    dx, dy = corpo(kit, a, folga_y=(-50, 150))
    yy, xx = np.mgrid[:a.shape[0], :a.shape[1]]
    baixo = (a[..., 3] > 0) & (yy >= cinto(xx - dx) + dy + 2)
    hsv = cv2.cvtColor(np.ascontiguousarray(a[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    pele = (hsv[..., 0] <= 25) & (hsv[..., 1] > 70) & (hsv[..., 2] > 50)
    poli = b.mascara(PERNA_FRENTE_AGACHADA) & baixo
    frente = poli & (cv2.dilate((poli & pele).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    frente &= pele | (a[..., :3].astype(int).sum(-1) < 200)
    M = np.float32([[1, 0, -dx], [0, 1, -dy]])
    sem = np.where((baixo & ~frente)[..., None], a, 0).astype(np.uint8)
    so = np.where(frente[..., None], a, 0).astype(np.uint8)
    # sem a perna da frente inteira (quando ela vem de variante): tira o polígono todo e as lascas que sobrarem soltas
    # o calção da perna da frente fica (a coxa da variante sai de baixo dele); só pele e contorno saem
    calcao = (hsv[..., 1] < 70) & (a[..., :3].astype(int).sum(-1) > 90) & (yy < 566)
    calcao = cv2.morphologyEx(calcao.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0
    vazio = (baixo & ~(poli & ~(calcao & (yy < 566)))).astype(np.uint8)
    n, rot, st, _ = cv2.connectedComponentsWithStats(vazio, 8)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < 400:
            vazio[rot == i] = 0
    sem_tudo = np.where(vazio.astype(bool)[..., None], a, 0).astype(np.uint8)
    _BAIXO.update(resto_sem_frente=cv2.warpAffine(sem_tudo, M, b.TELA, flags=cv2.INTER_NEAREST))
    _BAIXO.update(resto=cv2.warpAffine(sem, M, b.TELA, flags=cv2.INTER_NEAREST),
                  frente=cv2.warpAffine(so, M, b.TELA, flags=cv2.INTER_NEAREST), dx=dx, dy=dy)
    return _BAIXO


def desenhar_agachado(pf, kit, pose):
    bx = baixo_agachado(kit)
    w = b.mundo(pose)
    (qx, qy), _ = w["quadril"]
    j = OSSOS["quadril"][0]
    ox, oy = int(round(qx - j[0])), int(round(qy - j[1]))
    tela = np.zeros((b.TELA[1], b.TELA[0], 4), np.uint8)
    var = pose.get("coxa_frente", {}).get("var")
    usados = []
    if var:  # a coxa da variante vai por baixo do calção do agachado
        p = kit["pecas"][b.chave("coxa_frente", pose)]
        pos, ang = w["coxa_frente"]
        r, x0, y0 = b.colocar(p, p["img"], p["origem"], pos, ang)
        b.colar(tela, r, x0, y0)
    b.colar(tela, bx["resto_sem_frente" if var else "resto"], ox, oy)
    if not var:
        b.colar(tela, bx["frente"], ox, oy)
    camadas = ["tronco", "cabeca", "braco_frente", "braco_tras"]
    for slot in camadas:
        p = kit["pecas"][b.chave(slot, pose)]
        pos, ang = w[slot]
        r, x0, y0 = b.colocar(p, p["img"], p["origem"], pos, ang)
        b.colar(tela, r, x0, y0)
        usados.append((p, pos, ang))
    for p, pos, ang in usados:
        r, x0, y0 = b.colocar(p, p["sob"], p["origem_sobra"], pos, ang)
        b.colar(tela, r, x0, y0, so_vazio=True)
    return pf.sem_migalha(pf.fechar_frestas(tela, juntas=[w[sl][0] for sl in ("tronco", "cabeca", "braco_frente",
                                                                          "braco_tras", "coxa_frente")]), minimo=80)


def sem_pontinhos(tela):
    """Pontinho de pele no meio do calção (sobra do recorte da perna): mancha pequena de pele cercada de calção
    (preto/branco) vira a cor do calção em volta."""
    a = tela[..., 3] > 0
    hsv = cv2.cvtColor(np.ascontiguousarray(tela[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    pele = (a & (hsv[..., 0] <= 25) & (hsv[..., 1] > 70) & (hsv[..., 2] > 50)).astype(np.uint8)
    calcao = a & (hsv[..., 1] < 60)
    n, rot, st, _ = cv2.connectedComponentsWithStats(pele, 8)
    out = tela.copy()
    k = np.ones((7, 7), np.float32)
    for c in range(1, n):
        if st[c, cv2.CC_STAT_AREA] > 60:
            continue
        x, y, w, h = st[c, :4]
        x0, y0, x1, y1 = max(0, x - 4), max(0, y - 4), x + w + 4, y + h + 4
        m = rot[y0:y1, x0:x1] == c
        anel = (cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & ~m
        cal = calcao[y0:y1, x0:x1]
        if anel.sum() == 0 or (anel & cal).sum() < 0.75 * anel.sum():
            continue
        cor = np.median(tela[y0:y1, x0:x1][anel & cal][:, :3], axis=0).astype(np.uint8)
        out[y0:y1, x0:x1][m, :3] = cor
    return out


def desenhar(pf, kit, pose):
    return sem_pontinhos(_desenhar(pf, kit, pose))


def _desenhar(pf, kit, pose):
    if "_agachado" in pose:
        return desenhar_agachado(pf, kit, pose)
    atras = ["braco_frente"] if "_atras" in pose else []
    if pose.get("coxa_frente", {}).get("var"):
        # estudo de anatomia do Breno (Parte 2): a perna da frente é a do lado LONGE da câmera. Levantada, ela nasce
        # atrás da faixa e do tronco; só aparece o que sai da silhueta (antes passava por cima e lia "duas pernas
        # direitas")
        atras = ["coxa_frente", "canela_frente"] + atras
    if atras:
        # `_atras` na pose: o braço da frente (longe) vai para trás do tronco nesta pose (camada por pose do estudo)
        antes = b.CAMADAS
        b.CAMADAS = atras + [c for c in CAMADAS if c not in atras]
        try:
            tela = b.desenhar(kit, pose)
        finally:
            b.CAMADAS = antes
    else:
        tela = b.desenhar(kit, pose)
    w = b.mundo(pose)
    for slot in ("canela_tras", "canela_frente"):
        if pose.get(slot.replace("canela", "coxa"), {}).get("var"):
            continue
        joelho, ang = w[slot]
        jr = OSSOS[slot][0]
        pe = kit["pes"][slot]
        t = b.girar(pe["tornozelo"], jr, ang)
        tx, ty = t[0] + joelho[0] - jr[0], t[1] + joelho[1] - jr[1]
        x0 = int(round(pe["origem"][0] + tx - pe["tornozelo"][0]))
        y0 = int(round(pe["origem"][1] + ty - pe["tornozelo"][1]))
        fundo = pe["fundo"] + y0
        if abs(fundo - pf.CHAO) <= 10 and "_ar" not in pose:
            y0 += pf.CHAO - fundo
        b.colar(tela, pe["img"], x0, y0, so_vazio=(slot == "canela_tras"))
    return pf.sem_migalha(pf.fechar_frestas(tela, juntas=[w[sl][0] for sl in OSSOS]), minimo=80)


def pernas_no_chao(pf, pose, alvo, so_tras=False):
    """O pernas_no_chao do piloto, mas a perna nunca estica além do tamanho dela: se o pé de hoje está longe demais
    (base larga), o quadril desce até a perna alcançar com o joelho dobrado. Pé que não alcança vira pé solto."""
    if pf.PES_REF is None:
        pf.PES_REF = pf.pes(b.abrir(REF))
    agora = pf.pes(alvo)
    pernas = [("coxa_tras", "canela_tras", 0)] + ([] if so_tras else [("coxa_frente", "canela_frente", -1)])
    for _ in range(60):
        w = b.mundo(pose)
        longe = False
        for coxa, canela, i in pernas:
            qr, jr = OSSOS[coxa][0], OSSOS[canela][0]
            tr = TORNOZELO[canela]
            dx = (agora[i] - pf.PES_REF[i]) if agora and (i == 0 or len(agora) > 1) else 0
            l = np.hypot(jr[0] - qr[0], jr[1] - qr[1]) + np.hypot(tr[0] - jr[0], tr[1] - jr[1])
            q = w[coxa][0]
            if np.hypot(tr[0] + dx - q[0], tr[1] - q[1]) > l - 6:
                longe = True
        if not longe:
            break
        pose["quadril"]["dy"] = pose["quadril"].get("dy", 0) + 1
    return pf.pernas_no_chao(pose, alvo, so_tras=so_tras)


CHUTES_ALTOS = {"chute_alto", "super_beijinhos", "super_chutes"}  # perna levantada no ângulo do desenho


def pose_de(pf, kit, q, nome):
    alvo = b.abrir(q)
    dx, dy = corpo(kit, alvo, folga_y=(-50, 150)) if nome in AGACHADOS else pf.corpo(kit, alvo)
    pose = {"quadril": {"ang": 0, "dx": dx, "dy": dy}}
    if nome == "parado":  # respira, não pula: a respiração do vida_pecas cuida do peito
        pose["quadril"]["dy"] = max(-2, min(2, dy))
    # guarda de muay thai: fora do parado e do jab os braços ficam na guarda do parado (o mesmo desenho, sem a
    # beira do peito aparecendo); o que o golpe pede de braço vem escrito na ANIM
    if nome == "soco":
        b.BUSCA["braco_tras"] = (range(-12, 13, 2), 3, [None])
        b.BUSCA["braco_frente"] = (range(-30, 31, 3), 4, [None, "esticado"])
    else:
        b.BUSCA["braco_tras"] = (range(0, 1), 1, [None])
        b.BUSCA["braco_frente"] = (range(0, 1), 1, [None])
    pose = b.encaixar(kit, alvo, pose, ordem=["braco_tras", "braco_frente"])
    if q in PERNA and nome in CHUTES_ALTOS:
        # a perna levantada fica no ângulo em que foi desenhada (joelho para cima); a esticada nova (449) nasce
        # deitada, então gira GIRO_ESTICADA para ficar no ângulo do desenho de hoje
        g0 = GIRO_ESTICADA if PERNA[q] == "esticada" else 0
        giro = range(g0 - 6, g0 + 7, 2)
        b.BUSCA["coxa_frente"] = (giro, 2, [PERNA[q]])
        b.ANGULOS_VARIANTE = giro
        pose = b.encaixar(kit, alvo, pose, ordem=["coxa_frente"])
        # perna de apoio: o desenho da perna esticada, no ângulo dele; o quadril fica na altura em que o pé
        # dela encosta no chão
        pose["coxa_tras"] = {"ang": 0, "var": "apoio"}
        pose["quadril"]["dy"] = 0
    elif nome in CHUTES_ALTOS and len(pf.pes(alvo)) < 2:
        pose = pernas_no_chao(pf, pose, alvo, so_tras=True)
        b.BUSCA["coxa_frente"] = (range(-40, 41, 2), 2, [None])
        b.BUSCA["canela_frente"] = (range(-40, 41, 2), 2, [None])
        pose = b.encaixar(kit, alvo, pose, ordem=["coxa_frente", "canela_frente"])
    else:
        pose = pernas_no_chao(pf, pose, alvo)
    return pose


def animar():
    import vida_pecas as vida
    configurar()
    pf = configurar_piloto()
    nomes = sys.argv[2:] or list(ANIM)
    garantir_hd([e[0] for n in ANIM.values() for e in n[1]])
    if "--so-pose" not in sys.argv:
        montar_com_variantes(pf)
    nomes = [n for n in nomes if not n.startswith("--")]
    kit = separar_pes(b.ler_kit())
    b.FOLGA_VARIANTE = {"coxa_frente": 3}
    b.PESO_GIRO = 0.4  # na dúvida, o braço fica na guarda do parado (o mesmo desenho em todo golpe)
    b.BUSCA["coxa_tras"] = (range(-20, 21, 2), 2, [None])
    b.BUSCA["canela_tras"] = (range(-20, 21, 2), 2, [None])
    b.BUSCA["canela_tras"] = (range(-20, 21, 2), 2, [None])
    b.BUSCA["canela_frente"] = (range(-24, 25, 2), 2, [None])
    pf.MANCHA_REF = pf.mancha_ref()
    relatorio = ["| quadro | desenho de hoje | robô de defeitos |", "|---|---|---|"]
    poses = {}
    for nome in nomes:
        acao, elems, cx = ANIM[nome]
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            shutil.rmtree(SPR / pasta / nome, ignore_errors=True)
            (SPR / pasta / nome).mkdir(parents=True)
        rotulos = []
        for k, e in enumerate(elems):
            q, forca = e[0], (e[3] if len(e) > 3 else None)
            rot = q if forca is None else f"{q}@{nome}{k}"
            rotulos.append(rot)
            if rot not in poses:
                # `_base`: o corpo e os pés saem de outro desenho (ex.: preparo que parte da guarda do parado)
                pose = pose_de(pf, kit, (forca or {}).get("_base", q), nome)
                forca = dict(forca or {})
                if forca.get("coxa_frente", {}).get("var") and "coxa_tras" not in forca and "_sem_apoio" in forca:
                    # agachado: a perna de trás continua dobrada, com o pé onde está
                    pose["coxa_frente"] = dict(forca["coxa_frente"])
                    pose = pernas_no_chao(pf, pose, b.abrir(forca.get("_base", q)), so_tras=True)
                elif forca.get("coxa_frente", {}).get("var") and "coxa_tras" not in forca:
                    # perna levantada: a de trás é a perna de apoio esticada, com o pé no chão
                    forca["coxa_tras"] = {"ang": 0, "var": "apoio"}
                    pose["quadril"]["dy"] = 0
                if "_ar" in forca:  # no ar: as pernas ficam nos ângulos dados, sem pé plantado
                    for sl in ("coxa_tras", "canela_tras", "coxa_frente", "canela_frente"):
                        pose[sl] = {"ang": 0}
                    pose["_ar"] = {"ang": 0}
                if nome in AGACHADOS:
                    pose["_agachado"] = {"ang": 0}
                    bx = baixo_agachado(kit)
                    pose["quadril"] = {"ang": 0, "dx": bx["dx"], "dy": bx["dy"]}
                    forca.pop("_sem_apoio", None)
                    if forca.get("coxa_frente", {}).get("var"):
                        # no agachado o quadril da frente fica dentro da perna do calção (o 359 é mais baixo)
                        # (as pernas tiradas de desenho agachado, esticada do 449 e agachada do 359, já têm o quadril
                        # do agachado: não sobem)
                        if forca["coxa_frente"]["var"] not in ("esticada", "agachada"):
                            forca["coxa_frente"] = {"dx": -3, "dy": -22, **forca["coxa_frente"]}
                for slot, v in forca.items():
                    if slot in ("_pes", "_ar", "_base", "_sem_apoio"):  # (_atras vai para a pose)
                        continue
                    if slot == "_y":  # altura do quadril escrita à mão (no ar o desenho de hoje pula de altura)
                        pose["quadril"]["dy"] = v
                        continue
                    if slot == "_dy":
                        pose["quadril"]["dy"] += v
                    else:
                        pose[slot] = dict(v)
                if nome in AGACHADOS:
                    pass
                elif "_sem_apoio" in forca and "_dy" in forca:
                    pose = pernas_no_chao(pf, pose, b.abrir(forca.get("_base", q)), so_tras=True)
                elif ("_dy" in forca or "_pes" in forca) and "_ar" not in forca and \
                        not pose.get("coxa_frente", {}).get("var"):
                    # o quadril mudou: os pés continuam no chão (onde estão hoje, ou onde `_pes` manda)
                    pose = pernas_no_chao(pf, pose, b.abrir(forca.get("_pes", forca.get("_base", q))))
                poses[rot] = pose
        bate = [k for k, e in enumerate(elems) if e[2]]
        laco = nome in ("parado", "agachado")
        quadros = vida.animar(poses, [(r, e[1]) for r, e in zip(rotulos, elems)], bate=bate or None, laco=laco,
                              guarda=poses[rotulos[0]] if nome in AGACHADOS else {})
        for pose, _, _, _ in quadros:  # perna de apoio esticada: o pé dela encosta no chão com o quadril em 0
            if pose.get("coxa_tras", {}).get("var") == "apoio":
                pose["quadril"]["dy"] = 0
        if laco:
            quadros = vida.respirar(quadros)
        quadros = vida.atrasar(quadros, laco=laco)
        originais = {}
        for i, (pose, t, caixa_on, q) in enumerate(quadros):
            out = desenhar(pf, kit, pose)
            q0 = q.split("@")[0]
            originais.setdefault(q0, b.abrir(q0))
            erros = pf.conferir(out, originais[q0], None)
            if "_ar" in pose:  # no ar o pé não encosta no chão de propósito
                erros = [e for e in erros if not e.startswith("chão")]
            relatorio.append(f"| {nome}/{i:02d} | {q} | {'PASS' if not erros else 'FAIL ' + '; '.join(erros)} |")
            Image.fromarray(out).save(SPR / "quadros_pecas_hd" / nome / f"{i:02d}.png")
            Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(SPR / "quadros_pecas" / nome / f"{i:02d}.png")
        tempos = {"acao": acao, "caixa": cx, "origem": list(dict.fromkeys(e[0] for e in elems)),
                  "elementos": [{"desenho": i, "ticks": t, "caixa": c, "de": q}
                                for i, (_, t, c, q) in enumerate(quadros)]}
        assert sum(e["ticks"] for e in tempos["elementos"]) == sum(e[1] for e in elems)
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            (SPR / pasta / nome / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False),
                                                            encoding="utf-8")
        print(nome, "->", len(quadros), "desenhos")
    Image.fromarray(desenhar(pf, kit, poses.get("94_0") or pose_de(pf, kit, "94_0", "parado"))).save(
        SPR / "quadros_pecas_hd" / "guarda.png")
    falhas = sum("FAIL" in linha for linha in relatorio)
    texto = "\n".join(relatorio) + f"\n\n{falhas} quadro(s) com defeito.\n"
    print(texto)
    PROVA.mkdir(parents=True, exist_ok=True)
    (PROVA / "robo_defeitos.md").write_text(texto, encoding="utf-8")
    (SPR / "quadros_pecas_hd" / "poses.json").write_text(json.dumps(poses, indent=1), encoding="utf-8")


def video():
    """Vídeo lado a lado, tira de ticks e antes/depois (video_pecas.py), com o atual tirado do .sff."""
    import tempfile
    import video_pecas as vp
    saida = PROVA / (sys.argv[2] if len(sys.argv) > 2 else "corpo_firme")
    tmp = Path(tempfile.mkdtemp())
    (tmp / "quadros_arcade_hd" / "ginga").mkdir(parents=True)
    (tmp / "quadros_arcade_hd" / "ginga" / "00.png").symlink_to(HD / f"{REF}.png")
    for _, elems, _ in ANIM.values():
        for e in elems:
            q = e[0]
            alvo = tmp / "quadros_arcade_hd" / f"{q}.png"
            if not alvo.exists():
                alvo.symlink_to(HD / f"{q}.png")
    (tmp / "quadros_pecas_hd").symlink_to(SPR / "quadros_pecas_hd")
    vp.SPR = tmp
    nomes = [n for n in sys.argv[3:]] or [n for n in ANIM if (SPR / "quadros_pecas_hd" / n).exists()]
    vp.ATUAL = {n: [(e[0], e[1]) for e in ANIM[n][1]] for n in nomes}
    sys.argv = [sys.argv[0], str(saida)]
    vp.main()
    shutil.rmtree(tmp)


if __name__ == "__main__":
    {"kit": kit, "animar": animar, "video": video}[sys.argv[1]]()
