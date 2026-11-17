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
BRACO_TRAS = [(450, 366), (505, 364), (518, 392), (512, 420), (530, 444), (598, 446), (600, 468), (592, 512),
              (560, 502), (520, 480), (480, 492), (452, 484), (418, 466), (410, 430), (424, 404), (444, 384)]
BRACO_FRENTE = [(598, 394), (624, 374), (624, 334), (646, 322), (670, 334), (674, 372), (666, 412), (652, 442),
                (630, 452), (604, 446), (594, 420)]
PERNA_TRAS = [(428, 556), (506, 556), (508, 600), (494, 630), (502, 662), (388, 662), (394, 630), (412, 600)]
PERNA_FRENTE = [(564, 556), (642, 556), (652, 600), (678, 640), (682, 662), (568, 662), (576, 630), (570, 600)]
TRONCO_ESCONDIDO = [(0, 0), (1, 0), (0, 1)]  # o peito sob o braço mecânico sai da faixa do TAPAR (não conta como pintado)
# a criatura e os braços dela (ordem = prioridade do recorte)
EXTRAS = {
    "navalha": [(476, 166), (500, 148), (568, 136), (580, 150), (516, 192), (502, 204), (480, 198)],
    "secador": [(586, 268), (598, 262), (606, 250), (606, 232), (612, 206), (640, 196), (690, 196), (692, 232),
                (660, 238), (640, 248), (632, 268), (618, 290), (610, 306), (594, 310), (584, 296)],
    "garra": [(606, 314), (625, 300), (640, 290), (652, 262), (675, 254), (700, 268), (710, 300), (704, 332),
              (680, 338), (660, 338), (640, 332), (628, 346), (612, 348), (606, 332)],
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
    "navalha": ((498, 196), "criatura", (572, 142)),
    "secador": ((592, 292), "criatura", (684, 198)),
    "garra": ((614, 334), "criatura", (704, 300)),
}
# de trás para a frente: a criatura atrás do Raiclaven, o quadril (pintado por baixo das pernas) atrás delas, a tesoura na frente
CAMADAS = ["navalha", "criatura", "secador", "garra", "quadril", "coxa_frente", "canela_frente", "coxa_tras",
           "canela_tras", "tronco", "cabeca", "braco_frente", "braco_tras"]
# o tronco, o quadril e a criatura são pintados por baixo das peças que os cobrem (até 10 px para dentro da beirada):
# quando a peça de cima respira ou gira um pouco, aparece pano e pele, e não buraco com contorno
TAPAR_FAIXA = 10
TAPAR = ("tronco", "quadril", "criatura")
SEM_REGUA = True  # as folhas já vêm na mesma escala (importar_cliente.py)


def _p(dx=0, dy=0, tronco=0, cabeca=0, bf=0, bt=0, cri=0, nav=0, sec=0, gar=0, pes=(0, 0), cx=0, cy=0, en=1, es=1,
       eg=1, **pernas):
    """Pose à mão: corpo (dx, dy a partir do parado), inclinação do tronco, cabeça do Raiclaven, luva (bf), braço
    mecânico (bt); criatura (cri, relativa ao tronco) e os braços dela: navalha, secador, garra (relativos à criatura).
    + = horário na tela. cx, cy: a criatura escorrega no assento (para a frente e para cima). en/es/eg: quanto a navalha,
    o secador e a garra esticam (borracha, 1 = normal). Pernas: coxa_frente/canela_frente/coxa_tras/canela_tras."""
    # a criatura só escorrega um pouco no assento: mais que isso abre vão entre ela e as mangueiras das costas
    cx, cy = max(-8, min(8, cx)), max(-6, min(6, cy))
    out = {"quadril": {"ang": 0, "dx": dx, "dy": dy, "abs": 1, "pes": pes}, "tronco": {"ang": tronco},
           "cabeca": {"ang": cabeca}, "braco_frente": {"ang": bf}, "braco_tras": {"ang": bt},
           "criatura": {"ang": cri, "dx": cx, "dy": cy}, "navalha": {"ang": nav, "estica": en},
           "secador": {"ang": sec, "estica": es}, "garra": {"ang": gar, "estica": eg}}
    for k, v in pernas.items():
        out[k] = {"ang": v}
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
}
BRACO_VAR = {}
VARIANTES = {}
ANIMS = {
    "parado": (0, "ginga 0/10 2/8 4/10 6/8", None),
    "garra": (20200, "x_pe 0/2 1/3 2/1 3/4A 4/4 0/3", (40, -116, 76, -84)),
    "navalha": (20210, "y_pe 0/2 1/4 2/5 3/2 4/5A 5/6 0/5", (34, -128, 80, -96)),
    "bota": (20230, "a_pe 0/2 1/3 2/2 3/4A 4/4 0/3", (20, -50, 62, -20)),
    "pancada": (20240, "b_pe 0/2 1/4 2/5 3/2 4/5A 5/6 6/5 0/3", (24, -150, 80, -96)),
}
AUTO_ESPECIAL = set()
FIRMES = set()
ESPECIAIS = set()
EXPRESSOES = {}
PERNA_NO_AR = {f"a_pe/{i:02d}": "livre" for i in (1, 2, 3, 4)}
LACOS = {0}
NO_DA_FAIXA = [(0, 0), (1, 0), (0, 1)]  # sem nó de faixa
MANCHA_FOLGA = 1500  # calça e botas escuras
