"""Kit do Raiclaven despertado com A Cliente nas costas (#43, versão B aprovada pelo Breno) para o boneco de peças
"corpo firme" (ferramentas/firme.py).

Os desenhos vêm das folhas do ChatGPT (sprites/raiclaven/quadros/folhas_criatura, importadas por importar_cliente.py).
Tudo sai do ginga/00: o tronco do Raiclaven (com o tanque verde e o arnês), a cabeça dele, a criatura e os três braços
dela (navalha, secador e garra) são peças, e só os ossos giram. Tela 3x 1080x780, pés em 540,660. "tras" = lado
esquerdo da tela (o braço mecânico com a tesoura, na frente do corpo); "frente" = lado direito (a luva de longe).
"""
LUTADOR = "raiclaven_cliente"
REF = "ginga/00"
CINTURA = 445  # linha do cinto

CABECA = [(524, 300), (545, 284), (575, 282), (598, 294), (606, 316), (600, 346), (590, 370), (570, 386), (545, 386),
          (530, 372), (522, 340)]
BRACO_TRAS = [(450, 366), (505, 364), (518, 392), (512, 420), (530, 444), (598, 446), (602, 470), (597, 504),
              (588, 516), (560, 506), (520, 490), (480, 496), (452, 488), (418, 466), (410, 430), (424, 404), (444, 384)]


def SO_DO_BRACO_TRAS(ref):
    """Dentro do polígono do braço mecânico, só o metal e a luz verde: o cinto marrom e o avental entre as lâminas
    ficam com o corpo (assim o braço sobe sem levar pedaço do cinto e sem deixar buraco)."""
    import cv2
    import numpy as np
    hsv = cv2.cvtColor(ref[..., :3], cv2.COLOR_RGB2HSV)
    h, s, v = (hsv[..., i].astype(int) for i in range(3))
    quente = (h >= 4) & (h <= 35) & (s > 70) & (v > 45)
    m = np.zeros(ref.shape[:2], np.uint8)
    cv2.fillPoly(m, [np.int32(BRACO_TRAS)], 1)
    m = (m > 0) & (ref[..., 3] > 0) & ~quente
    n, rot, est, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=4)
    m = rot == (np.argmax(est[1:, 4]) + 1)
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cheio = np.zeros_like(m)
    cv2.drawContours(cheio, cs, -1, 1, -1)  # sem furo dentro (o brilho escuro da luz verde)
    return cheio > 0


BRACO_FRENTE = [(598, 394), (624, 374), (624, 334), (646, 322), (670, 334), (674, 372), (666, 412), (652, 442),
                (630, 452), (604, 446), (594, 420)]
PERNA_TRAS = [(428, 556), (506, 556), (508, 600), (494, 630), (502, 662), (388, 662), (394, 630), (412, 600)]
PERNA_FRENTE = [(564, 556), (642, 556), (652, 600), (678, 640), (682, 662), (568, 662), (576, 630), (570, 600)]
# o lado do tronco e o avental que o braço mecânico esconde (aparecem quando ele sobe na defesa ou recua no apanha)
TRONCO_ESCONDIDO = [(0, 0), (1, 0), (0, 1)]  # o peito sob o braço mecânico sai da faixa do TAPAR (não conta como pintado)
QUADRIL_ESCONDIDO = [(430, 444), (600, 444), (600, 516), (560, 508), (520, 494), (470, 498), (436, 486), (424, 466)]
# a criatura e os braços dela (ordem = prioridade do recorte)
EXTRAS = {
    "navalha": [(476, 166), (500, 148), (568, 136), (580, 150), (516, 192), (502, 204), (480, 198)],
    "secador": [(586, 268), (598, 262), (606, 250), (606, 232), (612, 206), (640, 196), (690, 196), (692, 232),
                (660, 238), (640, 248), (632, 268), (618, 290), (610, 306), (594, 310), (584, 296)],
    "garra": [(606, 314), (625, 300), (640, 290), (652, 262), (675, 254), (700, 268), (710, 300), (704, 332),
              (680, 338), (660, 338), (640, 332), (628, 346), (612, 348), (606, 332)],
    # a cabeça da Cliente é peça própria (presa no pescoço): no Pescoço de Borracha o corpo dela estica e a cara não
    "cri_cabeca": [(498, 206), (510, 192), (530, 184), (560, 180), (584, 192), (590, 214), (586, 240), (576, 262),
                   (556, 272), (530, 272), (512, 262), (500, 240), (494, 222)],
    "criatura": [(432, 214), (468, 194), (500, 168), (540, 172), (584, 178), (592, 214), (590, 262), (572, 290),
                 (546, 300), (534, 332), (500, 332), (468, 322), (440, 292), (428, 252)],
}

JOELHO_TRAS, JOELHO_FRENTE = (438, 596), (620, 594)
TORNOZELO = {"canela_tras": (436, 632), "canela_frente": (632, 632)}
OSSOS = {  # junta no parado, mãe, ponta
    "quadril": ((530, 466), None, (530, 490)),
    "tronco": ((530, 446), "quadril", (540, 330)),
    "cabeca": ((560, 382), "tronco", (566, 300)),
    "braco_tras": ((480, 386), "tronco", (590, 500)),
    "braco_frente": ((604, 410), "tronco", (650, 330)),
    "coxa_tras": ((472, 546), "quadril", JOELHO_TRAS),
    "canela_tras": (JOELHO_TRAS, "coxa_tras", TORNOZELO["canela_tras"]),
    "coxa_frente": ((582, 546), "quadril", JOELHO_FRENTE),
    "canela_frente": (JOELHO_FRENTE, "coxa_frente", TORNOZELO["canela_frente"]),
    "criatura": ((522, 302), "tronco", (530, 190)),
    "cri_cabeca": ((540, 270), "criatura", (545, 186)),
    "navalha": ((498, 196), "criatura", (572, 142)),
    "secador": ((592, 292), "criatura", (684, 198)),
    "garra": ((614, 334), "criatura", (704, 300)),
}
# de trás para a frente: a criatura atrás do Raiclaven, o quadril (pintado por baixo das pernas) atrás delas, a tesoura na frente
CAMADAS = ["navalha", "criatura", "cri_cabeca", "secador", "garra", "quadril", "coxa_frente", "canela_frente", "coxa_tras",
           "canela_tras", "tronco", "cabeca", "braco_frente", "braco_tras"]
# o tronco, o quadril e a criatura são pintados por baixo das peças que os cobrem (até 10 px para dentro da beirada):
# quando a peça de cima respira ou gira um pouco, aparece pano e pele, e não buraco com contorno
TAPAR_FAIXA = 10
TAPAR = ("tronco", "quadril", "criatura")  # (o pescoço da Cliente fica pintado por baixo da cabeça dela)
SEM_REGUA = True  # as folhas já vêm na mesma escala (importar_cliente.py)


def _p(dx=0, dy=0, tronco=0, cabeca=0, bf=0, bt=0, cri=0, nav=0, sec=0, gar=0, pes=(0, 0), cx=0, cy=0, en=1, es=1,
       eg=1, td=0, ec=1, cc=0, **pernas):
    """Pose à mão: corpo (dx, dy a partir do parado), inclinação do tronco, cabeça do Raiclaven, luva (bf), braço
    mecânico (bt); criatura (cri, relativa ao tronco) e os braços dela: navalha, secador, garra (relativos à criatura).
    + = horário na tela. cx, cy: a criatura escorrega no assento (para a frente e para cima). en/es/eg: quanto a navalha,
    o secador e a garra esticam (borracha, 1 = normal). Pernas: coxa_frente/canela_frente/coxa_tras/canela_tras."""
    # a criatura só escorrega um pouco no assento: mais que isso abre vão entre ela e as mangueiras das costas
    cx, cy = max(-8, min(8, cx)), max(-6, min(6, cy))
    out = {"quadril": {"ang": 0, "dx": dx, "dy": dy, "abs": 1, "pes": pes}, "tronco": {"ang": tronco, "dy": td},
           "cabeca": {"ang": cabeca}, "braco_frente": {"ang": bf}, "braco_tras": {"ang": bt},
           "criatura": {"ang": cri, "dx": cx, "dy": cy, "estica": ec}, "cri_cabeca": {"ang": cc},
           "navalha": {"ang": nav, "estica": en},
           "secador": {"ang": sec, "estica": es}, "garra": {"ang": gar, "estica": eg}}
    for k, v in pernas.items():
        out[k] = {"ang": v}
    if dx is None:  # metade de baixo inteira de um desenho doador (PERNAS_DE): o quadril fica onde ela foi recortada
        del out["quadril"]
    return out


POSES = {
    "ginga/00": _p(),
    "ginga/02": _p(dy=3, tronco=1, cri=-2, nav=-4, sec=4, gar=-5),
    "ginga/04": _p(dy=5, tronco=2, cabeca=2, cri=-3, nav=-6, sec=6, gar=-8, bf=2),
    "ginga/06": _p(dy=3, tronco=1, cri=-1, nav=-2, sec=3, gar=-3),
    # x de pé (Tapa de Garra): o Raiclaven gira o ombro e dá meio passo, a criatura se debruça e a garra estala na cara
    "x_pe/00": _p(),
    "x_pe/01": _p(dx=-2, dy=3, tronco=-3, cabeca=1, cri=-4, cx=-4, cy=-4, gar=-30, sec=-6, bf=-2),
    "x_pe/02": _p(dx=6, dy=3, tronco=3, cri=3, cx=10, gar=6, sec=4, pes=(0, 6)),
    "x_pe/03": _p(dx=12, dy=5, tronco=6, cri=6, cx=4, cy=2, gar=26, sec=6, nav=6, bf=2, pes=(0, 12)),
    "x_pe/04": _p(dx=6, dy=3, tronco=3, cri=2, cx=8, gar=10, pes=(0, 6)),
    # y de pé (Navalhada): arma a navalha atrás e a navalha de borracha corta longe, com o corpo indo junto
    "y_pe/00": _p(),
    "y_pe/01": _p(dx=-4, dy=2, tronco=-5, cabeca=2, cri=-6, cx=-6, cy=-4, nav=-30, gar=-6, bf=-4),
    "y_pe/02": _p(dx=-6, dy=3, tronco=-7, cabeca=3, cri=-8, cx=-8, cy=-6, nav=-44, gar=-10, bf=-5),
    "y_pe/03": _p(dx=8, dy=6, tronco=12, cri=3, cx=6, cy=-2, nav=40, sec=8, gar=8, bf=3, en=1.8, pes=(0, 6)),
    "y_pe/04": _p(dx=12, dy=8, tronco=18, cri=4, cx=8, cy=-2, nav=60, sec=10, gar=10, bf=4, en=2.2, pes=(0, 12)),
    "y_pe/05": _p(dx=6, dy=4, tronco=6, cri=2, cx=4, nav=20, gar=2, en=1.3, pes=(0, 6)),
    # a de pé (Bota e Cuspe): a bota de aço chuta baixo e a criatura se debruça para a frente
    "a_pe/00": _p(),
    "a_pe/01": _p(dy=-4, tronco=-3, cri=-2, cy=-2, coxa_frente=-35, canela_frente=40),
    "a_pe/02": _p(dx=4, dy=-2, tronco=-4, cri=3, cx=10, gar=6, sec=10, coxa_frente=-55, canela_frente=20),
    "a_pe/03": _p(dx=6, dy=-2, tronco=-5, cri=4, cx=16, cy=-2, gar=8, sec=14, coxa_frente=-62, canela_frente=8),
    "a_pe/04": _p(dx=3, dy=-2, tronco=-2, cri=1, cx=4, coxa_frente=-30, canela_frente=35),
    # b de pé (Pancada Tripla): o Raiclaven enrola o tronco para trás e solta com passo, a criatura bate com os três
    "b_pe/00": _p(),
    "b_pe/01": _p(dx=-6, dy=4, tronco=-8, cabeca=4, cri=-8, cx=-8, cy=-6, nav=-30, sec=-24, gar=-34, bt=-2, bf=-2),
    "b_pe/02": _p(dx=-8, dy=6, tronco=-10, cabeca=5, cri=-10, cx=-10, cy=-8, nav=-40, sec=-30, gar=-42, bt=-3, bf=-3),
    "b_pe/03": _p(dx=12, dy=6, tronco=8, cri=4, cx=14, cy=-6, nav=50, sec=16, gar=14, bt=2, bf=2, pes=(0, 10)),
    "b_pe/04": _p(dx=18, dy=8, tronco=10, cri=6, cx=20, cy=-6, nav=60, sec=22, gar=18, bt=2, bf=3, pes=(0, 16)),
    "b_pe/05": _p(dx=10, dy=4, tronco=4, cri=2, cx=8, nav=26, sec=8, gar=6, pes=(0, 10)),
    "b_pe/06": _p(dx=4, dy=2, tronco=1, cri=1, cx=2, pes=(0, 4)),
    # agachado: a metade de baixo vem inteira do doador (pés abertos, joelhos para fora, ChatGPT 17/11); em cima o
    # tronco respira e a criatura se encolhe junto
    "agachado_d/00": _p(dx=None, tronco=2, cri=3, cy=2, nav=-6, sec=6, gar=10),
    "agachado_d/01": _p(dx=None, td=2, tronco=3, cri=3, cy=3, nav=-8, sec=8, gar=12),
    "agachado_d/02": _p(dx=None, td=3, tronco=3, cabeca=1, cri=2, cy=4, nav=-10, sec=10, gar=14),
    "agachado_d/03": _p(dx=None, td=2, tronco=3, cri=3, cy=3, nav=-8, sec=8, gar=12),
    # x agachado (Belisco no Tornozelo): o tronco se debruça, a Cliente desce por cima do ombro e belisca baixo com a garra
    "x_agd/00": _p(dx=None, tronco=2, cri=3, cy=2, nav=-6, sec=6, gar=10),
    "x_agd/01": _p(dx=None, tronco=-3, cabeca=2, cri=-6, cx=-4, cy=-2, nav=-14, sec=-4, gar=-20),
    "x_agd/02": _p(dx=None, td=2, tronco=8, cri=14, cx=8, cy=4, nav=4, sec=10, gar=30),
    "x_agd/03": _p(dx=None, td=3, tronco=12, cri=20, cx=8, cy=6, nav=8, sec=14, gar=46),
    "x_agd/04": _p(dx=None, td=2, tronco=7, cri=10, cx=4, cy=4, nav=0, sec=10, gar=26),
    # y agachado (Mordida Antiaérea): o Raiclaven joga o tronco para trás e a Cliente empina e morde para cima
    "y_agd/00": _p(dx=None, tronco=2, cri=3, cy=2, nav=-6, sec=6, gar=10),
    "y_agd/01": _p(dx=None, td=3, tronco=6, cabeca=-2, cri=8, cx=4, cy=4, nav=6, sec=10, gar=16),
    "y_agd/02": _p(dx=None, td=-2, tronco=-4, cabeca=-5, cri=3, cx=6, cy=-5, nav=-34, sec=-12, gar=-54),
    "y_agd/03": _p(dx=None, td=-3, tronco=-6, cabeca=-7, cri=6, cx=8, cy=-6, nav=-46, sec=-16, gar=-74),
    "y_agd/04": _p(dx=None, td=-2, tronco=-4, cabeca=-5, cri=4, cx=6, cy=-4, nav=-34, sec=-12, gar=-56),
    "y_agd/05": _p(dx=None, tronco=-1, cabeca=-2, cri=3, cx=2, cy=-2, nav=-16, sec=-4, gar=-20),
    # a agachado (Secador no Chão): a Cliente bate o secador de cima para baixo na frente dos pés, o tronco vai junto
    "a_agd/00": _p(dx=None, tronco=2, cri=3, cy=2, nav=-6, sec=6, gar=10),
    "a_agd/01": _p(dx=None, td=-2, tronco=-4, cabeca=2, cri=-8, cx=-4, cy=-4, nav=-12, sec=-40, gar=-6),
    "a_agd/02": _p(dx=None, td=2, tronco=10, cri=14, cx=8, cy=4, nav=0, sec=36, gar=14),
    "a_agd/03": _p(dx=None, td=3, tronco=14, cri=20, cx=8, cy=6, nav=4, sec=56, gar=22),
    "a_agd/04": _p(dx=None, td=2, tronco=6, cri=8, cx=4, cy=4, nav=-2, sec=30, gar=12),
    # b agachado (Varrida de Garra): enrola o tronco para trás e solta a Cliente num arco baixo com os três braços
    "b_agd/00": _p(dx=None, tronco=2, cri=3, cy=2, nav=-6, sec=6, gar=10),
    "b_agd/01": _p(dx=None, td=-2, tronco=-6, cabeca=3, cri=-10, cx=-6, cy=-4, nav=-28, sec=-24, gar=-36),
    "b_agd/02": _p(dx=None, td=-3, tronco=-8, cabeca=4, cri=-12, cx=-8, cy=-6, nav=-36, sec=-30, gar=-44),
    "b_agd/03": _p(dx=None, td=2, tronco=10, cri=16, cx=8, cy=4, nav=20, sec=30, gar=30),
    "b_agd/04": _p(dx=None, td=4, tronco=14, cri=24, cx=8, cy=6, nav=34, sec=46, gar=56),
    "b_agd/05": _p(dx=None, td=3, tronco=9, cri=14, cx=6, cy=4, nav=18, sec=26, gar=34),
    "b_agd/06": _p(dx=None, td=1, tronco=5, cri=6, cx=2, cy=3, nav=4, sec=12, gar=18),
    # andar (pesado, com a Cliente nas costas): o pé da frente sobe e pisa à frente, o peso passa para ele e o pé de
    # trás vem arrastado; o corpo sobe e desce e a criatura balança ao contrário do passo
    "anda/00": _p(tronco=2, cri=-1, nav=-2, sec=2, gar=-2),
    "anda/01": _p(dx=2, dy=-3, tronco=3, cri=-4, cy=-2, nav=-6, sec=-2, gar=-8, pes=(-2, 4)),
    "anda/02": _p(dx=4, dy=2, tronco=4, cri=2, cy=2, nav=2, sec=6, gar=4, pes=(-4, 8)),
    "anda/03": _p(dx=4, dy=1, tronco=3, cri=3, cy=2, nav=4, sec=6, gar=6, pes=(-6, 6)),
    "anda/04": _p(dx=3, dy=-3, tronco=2, cri=-2, cy=-1, nav=-4, sec=0, gar=-4, pes=(-2, 4)),
    "anda/05": _p(dx=2, dy=1, tronco=2, cri=-3, cy=-2, nav=-6, sec=-2, gar=-6, pes=(2, 2)),
    "anda/06": _p(dx=1, dy=2, tronco=2, cri=0, nav=-2, sec=2, gar=0, pes=(1, 1)),
    "anda/07": _p(dy=0, tronco=2, cri=1, nav=0, sec=3, gar=1, pes=(0, 0)),
    # pulo: joelhos encolhidos (metade de baixo do doador); subindo, os braços da Cliente ficam para baixo (arrasto);
    # no alto ficam soltos; descendo, sobem
    "pulo_d/00": _p(dx=None, tronco=2, cri=4, cy=3, nav=6, sec=10, gar=12),
    "pulo_d/01": _p(dx=None, tronco=1, cri=2, cy=1, nav=0, sec=4, gar=4),
    "pulo_d/02": _p(dx=None, tronco=0, cri=0, nav=-4, sec=0, gar=-2),
    "pulo_d/03": _p(dx=None, td=-1, tronco=-2, cri=-4, cy=-4, nav=-12, sec=-10, gar=-14),
    "pulo_d/04": _p(dx=None, td=-2, tronco=-3, cri=-6, cy=-6, nav=-16, sec=-14, gar=-20),
    # x no ar (Arranhão de Cima): a Cliente se debruça e a garra rasga de cima para baixo na frente
    "x_ard/00": _p(dx=None, tronco=0, cri=0, nav=-4, sec=0, gar=-2),
    "x_ard/01": _p(dx=None, tronco=-4, cabeca=2, cri=-6, cy=-4, nav=-10, sec=-6, gar=-46),
    "x_ard/02": _p(dx=None, td=2, tronco=8, cri=14, cx=8, cy=4, nav=4, sec=8, gar=40),
    "x_ard/03": _p(dx=None, td=1, tronco=4, cri=6, cx=4, cy=2, nav=0, sec=4, gar=16),
    # y no ar (Navalha em Arco, da família da Navalhada: a navalha de borracha estica, escolha do Alisson): sai de trás
    # por cima da cabeça e corta na frente, para baixo
    "y_ard/00": _p(dx=None, tronco=0, cri=0, nav=-4, sec=0, gar=-2),
    "y_ard/01": _p(dx=None, td=-1, tronco=-6, cabeca=3, cri=-8, cx=-4, cy=-4, nav=-40, sec=-6, gar=-8),
    "y_ard/02": _p(dx=None, td=2, tronco=10, cri=12, cx=8, cy=2, nav=70, sec=8, gar=8, en=1.9),
    "y_ard/03": _p(dx=None, td=1, tronco=5, cri=6, cx=4, nav=40, sec=4, gar=4, en=1.3),
    # a no ar (Joelhada e Mordida): os joelhos já vêm na frente e a Cliente desce mordendo por cima do ombro
    "a_ard/00": _p(dx=None, tronco=0, cri=0, nav=-4, sec=0, gar=-2),
    "a_ard/01": _p(dx=None, td=-1, tronco=-5, cabeca=2, cri=-8, cx=-6, cy=-4, nav=-10, sec=-8, gar=-10),
    "a_ard/02": _p(dx=None, td=2, tronco=8, cri=22, cx=8, cy=6, nav=6, sec=16, gar=20),
    "a_ard/03": _p(dx=None, td=1, tronco=4, cri=10, cx=4, cy=3, nav=0, sec=8, gar=10),
    # b no ar (Por Baixo Mordendo): o corpo se inclina para a frente e a Cliente mergulha por baixo com os três braços
    "b_ard/00": _p(dx=None, tronco=0, cri=0, nav=-4, sec=0, gar=-2),
    "b_ard/01": _p(dx=None, td=-2, tronco=-6, cabeca=3, cri=-10, cx=-6, cy=-6, nav=-24, sec=-20, gar=-30),
    "b_ard/02": _p(dx=None, td=3, tronco=14, cri=30, cx=8, cy=6, nav=30, sec=40, gar=50),
    "b_ard/03": _p(dx=None, td=2, tronco=8, cri=16, cx=6, cy=4, nav=14, sec=20, gar=26),
    # defesa: o Raiclaven se encolhe (ombro para a frente, queixo para baixo, braço mecânico fechado na frente do
    # corpo) e a Cliente se debruça por cima dele, recolhendo a garra e o secador junto do corpo
    "defesa/00": _p(dx=-2, dy=2, tronco=3, cabeca=4, bt=-4, bf=-4, cri=6, cx=4, cy=2, nav=-10, sec=20, gar=24),
    "defesa/01": _p(dx=-3, dy=4, tronco=5, cabeca=6, bt=-6, bf=-8, cri=10, cx=6, cy=4, nav=-16, sec=34, gar=40),
    "defesa/02": _p(dx=-4, dy=5, tronco=6, cabeca=7, bt=-7, bf=-10, cri=12, cx=7, cy=5, nav=-20, sec=42, gar=50),
    "defesa/03": _p(dx=-4, dy=6, tronco=6, cabeca=7, bt=-7, bf=-10, cri=13, cx=7, cy=6, nav=-22, sec=44, gar=52),
    "defesa/04": _p(dx=-8, dy=6, tronco=4, cabeca=6, bt=-6, bf=-12, cri=10, cx=4, cy=6, nav=-26, sec=38, gar=44),
    "defesa/05": _p(dx=-10, dy=6, tronco=3, cabeca=5, bt=-5, bf=-12, cri=9, cx=3, cy=6, nav=-28, sec=36, gar=42),
    # apanha: o golpe empurra o quadril para trás e o tronco tomba, a cabeça vai junto e a criatura chicoteia
    "apanha/00": _p(dx=-2, dy=2, tronco=-3, cabeca=-3, cri=2, nav=4, sec=-4, gar=-6, bf=-4),
    "apanha/01": _p(dx=-6, dy=3, tronco=-8, cabeca=-8, cri=6, cx=4, nav=10, sec=-10, gar=-14, bf=-12, bt=-1),
    "apanha/02": _p(dx=-9, dy=4, tronco=-12, cabeca=-10, cri=10, cx=6, cy=2, nav=16, sec=-16, gar=-20, bf=-18, bt=-2),
    "apanha/03": _p(dx=-12, dy=5, tronco=-16, cabeca=-12, cri=14, cx=8, cy=3, nav=22, sec=-22, gar=-28, bf=-24, bt=-2),
    "apanha/04": _p(dx=-14, dy=6, tronco=-18, cabeca=-14, cri=-6, cx=-6, cy=-4, nav=-20, sec=14, gar=20, bf=-28,
                    bt=-3),
}
BRACO_VAR = {}
VARIANTES = {}
ANIMS = {
    "parado": (0, "ginga 0/10 2/8 4/10 6/8", None),
    "agachado": (11, "agachado_d 0/10 1/8 2/10 3/8", None),
    "belisco": (20400, "x_agd 0/2 1/3 2/2 3/4A 4/4 0/3", (32, -72, 58, -48)),
    "mordida": (20410, "y_agd 0/2 1/3 2/2 3/5A 4/6 5/4 0/3", (0, -140, 46, -70)),
    "secador_chao": (20430, "a_agd 0/2 1/4 2/2 3/4A 4/5 0/3", (40, -82, 64, -56)),
    "varrida": (20440, "b_agd 0/2 1/4 2/4 3/2 4/5A 5/6 6/5 0/3", (26, -84, 66, -54)),
    "pulo": (41, "pulo_d 0/4 1/4 2/6 3/4 4/4", None),
    "arranhao_ar": (20600, "x_ard 0/2 1/3 2/5A 3/5 0/3", (28, -100, 62, -68)),
    "navalha_ar": (20610, "y_ard 0/2 1/4 2/5A 3/6 0/3", (20, -110, 70, -40)),
    "mordida_ar": (20630, "a_ard 0/2 1/4 2/5A 3/6 0/3", (8, -144, 40, -108)),
    "por_baixo": (20640, "b_ard 0/2 1/4 2/2 2/4A 3/6 0/3", (10, -100, 62, -45)),
    "anda": (20, "anda 0/6 1/6 2/6 3/6 4/6 5/6 6/6 7/6", None),
    "defesa": (150, "defesa 0/3 1/3 2/4 3/4 4/3 5/3", None),
    "apanha": (5000, "apanha 0/3 1/3 2/3 3/3 4/3", None),
    # queda: desenhos inteiros do doador (no ar, deitado, de joelho); o corpo do kit não deita
    "queda": (5100, "queda_d 1/6 0/10 2/8", None),
    "garra": (20200, "x_pe 0/2 1/3 2/1 3/4A 4/4 0/3", (40, -116, 76, -84)),
    "navalha": (20210, "y_pe 0/2 1/4 2/5 3/2 4/5A 5/6 0/5", (34, -128, 80, -96)),
    "bota": (20230, "a_pe 0/2 1/3 2/2 3/4A 4/4 0/3", (20, -50, 62, -20)),
    "pancada": (20240, "b_pe 0/2 1/4 2/5 3/2 4/5A 5/6 6/5 0/3", (24, -150, 80, -96)),
}
AUTO_ESPECIAL = set()
FIRMES = set()
ESPECIAIS = {"queda_d/00", "queda_d/01", "queda_d/02"}
EXPRESSOES = {}
PERNA_NO_AR = {f"a_pe/{i:02d}": "livre" for i in (1, 2, 3, 4)}
LACOS = {0, 11}
NO_DA_FAIXA = [(0, 0), (1, 0), (0, 1)]  # sem nó de faixa
MANCHA_FOLGA = 1500  # calça e botas escuras

# ações da base que o despertado mostra com o corpo firme (remap de sprite): nome da animação (a linha do tempo dela
# inteira, para laços) ou a lista de poses-chave, uma por elemento da ação da base (ou espalhadas pelo tempo)
REMAP = {
    0: "parado", 11: "agachado",
    20: ["anda/00", "anda/01", "anda/02", "anda/03", "anda/04", "anda/05", "anda/06", "anda/07"],
    21: ["anda/07", "anda/06", "anda/05", "anda/04", "anda/03", "anda/02", "anda/01", "anda/00"],
    40: ["agachado_d/00", "agachado_d/01", "pulo_d/00", "pulo_d/00"],
    41: ["pulo_d/00", "pulo_d/01", "pulo_d/02"], 42: ["pulo_d/00", "pulo_d/01", "pulo_d/02"],
    43: ["pulo_d/00", "pulo_d/01", "pulo_d/02"],
    44: ["pulo_d/02", "pulo_d/03", "pulo_d/04"], 45: ["pulo_d/02", "pulo_d/03", "pulo_d/04"],
    46: ["pulo_d/02", "pulo_d/03", "pulo_d/04"],
    47: ["pulo_d/04", "agachado_d/00", "agachado_d/00", "ginga/00"],
    120: ["defesa/00", "defesa/01", "defesa/01", "defesa/02"],
    130: ["defesa/02", "defesa/03"],
    140: ["defesa/01", "defesa/01", "defesa/00"],
    150: ["defesa/04", "defesa/05", "defesa/02"],
    5000: ["apanha/01", "apanha/02", "apanha/00"],
    5001: ["apanha/02", "apanha/03", "apanha/04", "apanha/00"],
    5002: ["apanha/03", "apanha/04", "apanha/02", "apanha/00"],
    5005: ["apanha/02", "apanha/00"],
    5020: ["apanha/03", "apanha/03", "queda_d/01"], 5021: ["apanha/03", "apanha/03", "queda_d/01", "queda_d/01"],
    5022: ["apanha/03", "apanha/03", "queda_d/01", "queda_d/01"],
    5030: ["queda_d/01"], 5035: ["queda_d/01"], 5040: ["queda_d/01"], 5050: ["queda_d/01", "queda_d/01", "queda_d/01"], 5051: ["queda_d/01", "queda_d/01"], 5061: ["queda_d/01"],
    5070: ["queda_d/01", "queda_d/01"], 5080: ["queda_d/01", "queda_d/01", "queda_d/00"], 5090: ["queda_d/00"], 5100: ["queda_d/00", "queda_d/00", "queda_d/00"], 5101: ["queda_d/00", "queda_d/00"],
    5110: ["queda_d/00"], 5160: ["queda_d/00", "queda_d/00"], 5170: ["queda_d/00", "queda_d/00"], 5150: ["queda_d/00"],
    5120: ["queda_d/00", "queda_d/00", "queda_d/02", "queda_d/02", "queda_d/02", "queda_d/02", "ginga/00"],
}

# metade de baixo inteira de um desenho doador (a saia esconde as pernas do kit: dobrar coxa e canela deixava linha de
# corte e pedaço solto). Doadores: ferramentas/doador_cliente.py
PERNAS_VAR = {"agachado": "doador/agachado", "pulo": "doador/pulo"}
PERNAS_DE = {f"{f}/{i:02d}": "agachado" for f in ("agachado_d", "x_agd", "y_agd", "a_agd", "b_agd") for i in range(8)}
PERNAS_NO_AR = {"pulo"}  # o doador do pulo fica no ar (o robô não cobra pé no chão)
PERNAS_DE.update({f"{f}/{i:02d}": "pulo" for f in ("pulo_d", "x_ard", "y_ard", "a_ard", "b_ard") for i in range(8)})


# ------------------------------------------------------------------------------------------- lote 3 (17/11)
# golpes de pé que faltavam: direcionais, correntes, kombo, especiais e super. Pastas novas = cópias do ginga/00
# (ferramentas/doador_cliente.py, PASTAS_DE_PE); a pose vem toda daqui. Regras: corpo inteiro vai junto (passo, quadril,
# tronco), um quadro de contato seco depois da preparação (meio-termo), borracha só no Pescoço e na família da Navalhada.
def _seq(pasta, *poses):
    for i, p in enumerate(poses):
        POSES[f"{pasta}/{i:02d}"] = p


R0 = dict()  # parado
_seq("f_y",  # Mordida por Cima: a Cliente empina por cima da cabeça do Raiclaven e desce mordendo
     _p(), _p(dx=-4, dy=2, tronco=-6, cabeca=2, cri=-14, cx=-6, cy=-6, cc=-14, nav=-20, sec=-10, gar=-20),
     _p(dx=-5, dy=3, tronco=-8, cabeca=3, cri=-18, cx=-8, cy=-6, cc=-22, nav=-26, sec=-14, gar=-26),
     _p(dx=10, dy=6, tronco=14, cri=24, cx=8, cy=6, cc=20, nav=10, sec=14, gar=20, pes=(0, 8)),
     _p(dx=8, dy=4, tronco=8, cri=14, cx=6, cy=4, cc=10, nav=4, sec=8, gar=10, pes=(0, 8)))
_seq("f_b",  # Pisão de Choque: ergue a bota de aço e pisa com o peso do corpo
     _p(), _p(dy=-4, tronco=-4, cri=-4, cy=-4, gar=-10, sec=-10, coxa_frente=-50, canela_frente=50),
     _p(dy=-5, tronco=-5, cabeca=2, cri=-6, cy=-5, gar=-14, sec=-14, coxa_frente=-62, canela_frente=58),
     _p(dx=8, dy=6, tronco=8, cri=8, cx=6, cy=4, gar=10, sec=10, pes=(0, 14)),
     _p(dx=8, dy=5, tronco=6, cri=6, cx=4, cy=3, gar=6, sec=6, pes=(0, 14)))
_seq("t_x",  # Bafo do Secador: a Cliente aponta o secador na cara e sopra (o Raiclaven firma o pé de trás)
     _p(), _p(dx=-3, dy=2, tronco=-4, cri=-6, cx=-4, cy=-2, sec=-30, gar=-10),
     _p(dx=4, dy=3, tronco=4, cri=10, cx=10, cy=-2, sec=50, gar=-14, pes=(0, 4)),
     _p(dx=4, dy=3, tronco=5, cri=11, cx=10, cy=-1, sec=46, gar=-12, pes=(0, 4)),
     _p(dx=2, dy=1, tronco=2, cri=4, cx=4, sec=20, gar=-4, pes=(0, 2)))
_seq("t_a",  # Puxa pela Gola: a garra agarra na frente e o corpo todo puxa para trás
     _p(), _p(dx=-3, dy=2, tronco=-4, cri=-6, cx=-4, gar=-24, sec=-6),
     _p(dx=8, dy=4, tronco=8, cri=14, cx=10, gar=40, sec=8, pes=(0, 8)),
     _p(dx=-6, dy=3, tronco=-8, cabeca=2, cri=-8, cx=-6, gar=10, sec=-4, pes=(0, 0)),
     _p(dx=-2, dy=1, tronco=-3, cri=-3, cx=-2, gar=0))
# correntes: o 1º quadro já é a guarda (vem do golpe anterior); um de preparação e o contato
_seq("c_x1",  # Tesourinha: garra de costas de mão
     _p(), _p(dx=-2, dy=2, tronco=-4, cri=-6, cx=-6, cy=-2, gar=-36, sec=-4),
     _p(dx=10, dy=4, tronco=6, cri=8, cx=12, gar=34, sec=6, pes=(0, 10)),
     _p(dx=6, dy=2, tronco=3, cri=4, cx=6, gar=14, pes=(0, 6)))
_seq("c_x2",  # Tesourinha: mordida
     _p(), _p(dx=-2, dy=2, tronco=-4, cri=-8, cx=-6, cy=-2, cc=-12, gar=-10),
     _p(dx=12, dy=5, tronco=10, cri=16, cx=14, cy=2, cc=14, gar=12, sec=8, pes=(0, 10)),
     _p(dx=6, dy=3, tronco=5, cri=8, cx=6, cc=6, gar=6, pes=(0, 6)))
_seq("c_x3",  # Tesourinha: dentes e chacoalha (3 acertos)
     _p(), _p(dx=-3, dy=3, tronco=-6, cabeca=2, cri=-10, cx=-8, cy=-4, cc=-14, gar=-20, sec=-10),
     _p(dx=12, dy=5, tronco=10, cri=18, cx=14, cy=2, cc=16, gar=16, sec=10, pes=(0, 10)),
     _p(dx=12, dy=6, tronco=12, cri=12, cx=10, cy=4, cc=-4, gar=24, sec=4, pes=(0, 10)),
     _p(dx=12, dy=5, tronco=9, cri=20, cx=14, cy=2, cc=20, gar=10, sec=14, pes=(0, 10)),
     _p(dx=6, dy=3, tronco=4, cri=6, cx=6, cc=4, gar=6, pes=(0, 6)))
_seq("c_y1",  # Navalha Comprida 2 (borracha da Navalhada): corta de cima para baixo
     _p(), _p(dx=-4, dy=2, tronco=-5, cabeca=2, cri=-6, cx=-6, cy=-4, nav=-40, gar=-6),
     _p(dx=12, dy=8, tronco=18, cri=4, cx=8, cy=-2, nav=62, sec=10, gar=10, en=2.2, pes=(0, 10)),
     _p(dx=6, dy=4, tronco=6, cri=2, cx=4, nav=20, en=1.3, pes=(0, 6)))
_seq("c_y2",  # Navalha Comprida 3: volta de baixo para cima
     _p(), _p(dx=-2, dy=4, tronco=6, cri=4, cx=2, cy=2, nav=95, gar=4),
     _p(dx=12, dy=5, tronco=8, cri=4, cx=8, cy=-2, nav=42, sec=8, gar=8, en=2.4, pes=(0, 12)),
     _p(dx=6, dy=3, tronco=4, cri=2, cx=4, nav=20, en=1.3, pes=(0, 6)))
_seq("c_y3",  # Corte em X: a navalha desce e a garra cruza junto
     _p(), _p(dx=-5, dy=3, tronco=-8, cabeca=3, cri=-10, cx=-8, cy=-6, nav=-50, gar=-40, sec=-12),
     _p(dx=14, dy=7, tronco=16, cri=10, cx=12, cy=0, nav=60, gar=46, sec=12, en=2.4, pes=(0, 14)),
     _p(dx=8, dy=4, tronco=8, cri=4, cx=6, nav=24, gar=18, en=1.4, pes=(0, 8)))
_seq("c_a1",  # Tubo Chicote baixo: chute baixo da bota
     _p(), _p(dy=-4, tronco=-3, cri=-2, cy=-2, coxa_frente=-35, canela_frente=40),
     _p(dx=4, dy=-2, tronco=-5, cri=3, cx=10, gar=6, sec=10, coxa_frente=-50, canela_frente=10),
     _p(dx=3, dy=-2, tronco=-2, cri=1, cx=4, coxa_frente=-30, canela_frente=35))
_seq("c_a2",  # Tubo Chicote alto: a Cliente desce o secador por cima, com passo
     _p(), _p(dx=-3, dy=2, tronco=-5, cri=-10, cx=-6, cy=-6, sec=-46, gar=-10),
     _p(dx=10, dy=5, tronco=10, cri=16, cx=12, cy=2, sec=60, gar=10, pes=(0, 10)),
     _p(dx=6, dy=3, tronco=4, cri=6, cx=6, sec=24, pes=(0, 6)))
_seq("c_a3",  # Tubo Laça o Pé: o corpo desce e a garra fisga o tornozelo
     _p(), _p(dx=-3, dy=4, tronco=-4, cri=-8, cx=-6, gar=-30, sec=-10),
     _p(dx=12, dy=10, tronco=16, cri=26, cx=12, cy=6, gar=60, sec=16, nav=10, pes=(0, 12)),
     _p(dx=4, dy=6, tronco=6, cri=10, cx=4, cy=2, gar=20, sec=4, pes=(0, 6)))
_seq("c_b1",  # Pião da Cadeira 1: torce o tronco para um lado e os três braços varrem
     _p(), _p(dx=-4, dy=4, tronco=-10, cabeca=4, cri=-12, cx=-8, cy=-4, nav=-40, sec=-30, gar=-44),
     _p(dx=10, dy=5, tronco=10, cri=12, cx=12, cy=-2, nav=50, sec=20, gar=30, pes=(0, 10)),
     _p(dx=6, dy=3, tronco=4, cri=4, cx=6, nav=20, sec=8, gar=10, pes=(0, 6)))
_seq("c_b2",  # Pião da Cadeira 2: torce de volta
     _p(), _p(dx=4, dy=4, tronco=10, cri=10, cx=8, nav=50, sec=24, gar=30, pes=(0, 6)),
     _p(dx=10, dy=5, tronco=-6, cabeca=-2, cri=-4, cx=10, cy=-4, nav=-30, sec=-20, gar=-20, pes=(0, 10)),
     _p(dx=6, dy=3, tronco=-2, cri=0, cx=6, nav=-10, sec=-6, gar=-6, pes=(0, 6)))
_seq("c_b3",  # Choque em Círculo: agacha, abre tudo e solta o choque em volta
     _p(), _p(dy=8, tronco=8, cri=10, cy=6, nav=-30, sec=-30, gar=-30),
     _p(dy=-2, tronco=-6, cabeca=-4, cri=-14, cy=-6, nav=70, sec=60, gar=70),
     _p(dy=-1, tronco=-4, cabeca=-3, cri=-10, cy=-5, nav=64, sec=54, gar=64),
     _p(dy=3, tronco=2, cri=2, cy=2, nav=20, sec=20, gar=20))
_seq("k_nav",  # Cobaia: navalha (a vítima está presa pela gola: a navalha entra curta)
     _p(), _p(dx=-4, dy=2, tronco=-5, cabeca=2, cri=-6, cx=-6, cy=-4, nav=-34, gar=20),
     _p(dx=12, dy=8, tronco=18, cri=4, cx=8, cy=-2, nav=62, sec=8, gar=26, en=2.0, pes=(0, 10)),
     _p(dx=6, dy=4, tronco=6, cri=2, cx=4, nav=20, gar=12, en=1.2, pes=(0, 6)))
_seq("peruca",  # Peruca Viva: a Cliente arranca o topete verde e arremessa
     _p(), _p(dx=-3, dy=2, tronco=-5, cri=-12, cx=-6, cy=-4, cc=-10, gar=-50, sec=-6),
     _p(dx=-4, dy=3, tronco=-6, cabeca=2, cri=-14, cx=-8, cy=-6, cc=-12, gar=-64, sec=-8),
     _p(dx=8, dy=4, tronco=8, cri=12, cx=10, cy=2, cc=8, gar=50, sec=8, pes=(0, 8)),
     _p(dx=6, dy=3, tronco=4, cri=6, cx=6, cc=4, gar=24, pes=(0, 6)))
_seq("pescoco",  # Pescoço de Borracha: a Cliente se joga para a frente e morde (o esticão do kit borrava o corpo dela: a borracha
# de verdade pede um desenho do pescoço esticado, ver docs/raiclaven-despertado-43.md)
     _p(), _p(dx=-4, dy=3, tronco=-6, cabeca=2, cri=-10, cx=-6, cy=-4, cc=-10, gar=-10, sec=-10),
     _p(dx=6, dy=4, tronco=8, cri=36, cx=8, cy=6, cc=-24, gar=-16, sec=-16, pes=(0, 6)),
     _p(dx=6, dy=4, tronco=8, cri=40, cx=8, cy=6, cc=-26, gar=-18, sec=-18, pes=(0, 6)),
     _p(dx=3, dy=2, tronco=4, cri=16, cx=4, cy=2, cc=-10, gar=-6, sec=-6, pes=(0, 4)))
_seq("tanque",  # Tanque Estourado: encolhe e estoura o tanque das costas, a Cliente abre os três braços
     _p(), _p(dy=6, tronco=10, cri=-6, cy=6, nav=-10, sec=-10, gar=-10),
     _p(dy=8, tronco=12, cabeca=2, cri=-8, cy=6, nav=-14, sec=-14, gar=-14),
     _p(dy=-2, tronco=-8, cabeca=-6, cri=-16, cy=-6, nav=-40, sec=40, gar=-50),
     _p(dy=-1, tronco=-6, cabeca=-5, cri=-14, cy=-5, nav=-36, sec=36, gar=-46),
     _p(dy=2, tronco=0, cri=-4, nav=-10, sec=10, gar=-10))
_seq("bigodes",  # Bigodes Carnívoros: a Cliente escancara a boca para a frente e cospe os bigodes
     _p(), _p(dx=-2, dy=2, tronco=-4, cri=-10, cx=-6, cy=-4, cc=-14, gar=-10, sec=-10),
     _p(dx=6, dy=4, tronco=6, cri=16, cx=12, cy=2, cc=12, gar=16, sec=16, pes=(0, 6)),
     _p(dx=6, dy=4, tronco=7, cri=18, cx=12, cy=2, cc=14, gar=18, sec=18, pes=(0, 6)),
     _p(dx=3, dy=2, tronco=3, cri=6, cx=4, cc=4, gar=6, sec=6, pes=(0, 4)))
_seq("cir",  # Sala de Cirurgia: avança e a Cliente opera com tudo (navalha, garra, secador), arremate com o corpo
     _p(), _p(dx=-5, dy=4, tronco=-8, cabeca=3, cri=-12, cx=-8, cy=-6, nav=-40, sec=-30, gar=-40),
     _p(dx=12, dy=5, tronco=10, cri=12, cx=12, nav=50, sec=-10, gar=-10, pes=(0, 12)),
     _p(dx=12, dy=5, tronco=8, cri=14, cx=12, cy=2, nav=-10, sec=10, gar=50, pes=(0, 12)),
     _p(dx=12, dy=5, tronco=10, cri=10, cx=10, cy=-2, nav=10, sec=50, gar=0, pes=(0, 12)),
     _p(dx=12, dy=6, tronco=12, cri=16, cx=14, cy=2, cc=14, nav=40, sec=20, gar=30, pes=(0, 12)),
     _p(dx=16, dy=8, tronco=16, cri=22, cx=14, cy=4, cc=16, nav=64, sec=40, gar=60, pes=(0, 16)),
     _p(dx=8, dy=4, tronco=6, cri=8, cx=6, nav=24, sec=14, gar=20, pes=(0, 8)))
PERNA_NO_AR.update({f"f_b/{i:02d}": "livre" for i in (1, 2)})
PERNA_NO_AR.update({f"c_a1/{i:02d}": "livre" for i in (1, 2, 3)})
PASTAS_DE_PE = ("f_y", "f_b", "t_x", "t_a", "c_x1", "c_x2", "c_x3", "c_y1", "c_y2", "c_y3", "c_a1", "c_a2", "c_a3",
                "c_b1", "c_b2", "c_b3", "k_nav", "peruca", "pescoco", "tanque", "bigodes", "cir")
ANIMS.update({
    "mordida_cima": (20250, "f_y 0/2 1/4 2/5 3/5A 4/6 0/4", (30, -124, 80, -80)),
    "pisao": (20260, "f_b 0/2 1/4 2/5 3/5A 4/6 0/4", (14, -26, 66, 0)),
    "bafo": (20270, "t_x 0/2 1/4 2/5A 3/6 4/4 0/3", (40, -136, 100, -96)),
    "puxa_gola": (20280, "t_a 0/2 1/3 2/4A 3/6 4/3 0/2", (30, -124, 80, -84)),
    "tesoura_1": (20301, "c_x1 0/1 1/3 2/4A 3/5 0/2", (34, -120, 78, -84)),
    "tesoura_2": (20302, "c_x2 0/1 1/3 2/5A 3/5 0/2", (30, -150, 92, -100)),
    "tesoura_3": (20303, "c_x3 0/1 1/4 2/4A 3/4A 4/4A 5/6 0/3", (30, -150, 92, -90)),
    "navalha_2": (20311, "c_y1 0/1 1/3 2/5A 3/5 0/2", (34, -140, 84, -100)),
    "navalha_3": (20312, "c_y2 0/1 1/3 2/5A 3/5 0/2", (30, -156, 82, -112)),
    "corte_x": (20313, "c_y3 0/1 1/5 2/6A 3/8 0/3", (30, -120, 120, -60)),
    "chicote_baixo": (20321, "c_a1 0/1 1/3 2/4A 3/4 0/2", (20, -50, 66, -16)),
    "chicote_alto": (20322, "c_a2 0/1 1/3 2/5A 3/5 0/2", (36, -150, 96, -90)),
    "laca_pe": (20323, "c_a3 0/1 1/4 2/6A 3/7 0/3", (30, -60, 100, 0)),
    "piao_1": (20331, "c_b1 0/1 1/3 2/5A 3/5 0/2", (24, -150, 84, -80)),
    "piao_2": (20332, "c_b2 0/1 1/3 2/5A 3/5 0/2", (24, -150, 84, -80)),
    "choque_circulo": (20333, "c_b3 0/2 1/5 2/6A 3/6A 4/6 0/3", (-60, -110, 70, 0)),
    "cobaia_navalha": (20341, "k_nav 0/1 1/3 2/5A 3/5 0/2", (34, -140, 84, -100)),
    "cobaia_varre": (20342, "b_agd 0/2 1/3 2/3 4/6A 5/6 6/5 0/3", (26, -84, 70, -50)),
    "peruca_fraca": (21000, "peruca 0/2 1/4 2/4 3/6 4/6 0/3", None),
    "peruca_forte": (21001, "peruca 0/2 1/5 2/5 3/7 4/6 0/3", None),
    "pescoco": (21100, "pescoco 0/2 1/5 2/4A 3/8A 4/6 0/4", (20, -164, 74, -108)),
    "pescoco_puxa": (21101, "pescoco 0/2 1/5 2/4A 3/8A 4/6 0/4", (20, -164, 74, -108)),
    "tanque": (21200, "tanque 0/2 1/4 2/6 3/6A 4/8A 5/6 0/3", (-75, -120, 80, 0)),
    "bigodes": (21300, "bigodes 0/2 1/5 2/5 3/8 4/6 0/3", None),
    "cirurgia": (23000, "cir 0/3 1/8 2/5A 3/4A 4/5A 3/4A 2/5A 4/4A 5/5A 6/10A 7/10 0/4", (10, -130, 90, -30)),
})
