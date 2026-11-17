"""Kit do Garanhão (Gutto despertado, minotauro-cavalo) para o boneco de peças "corpo firme" (ferramentas/firme.py).

Os desenhos vêm das folhas do ChatGPT de 16/11 (sprites/garanhao/folhas, importadas por importar_garanhao.py). Nas
folhas a cabeça, o tronco e a pele mudam de quadro para quadro; aqui tudo sai do rasga_couro/00 e só os membros
mexem. Tela 3x 1080x780, pés em 540,660. "tras" = lado esquerdo da tela (o braço de perto, com a corda e o punho na
frente da coxa); "frente" = lado direito (braço de longe, garras abertas; perna da frente, a que pisa).
"""
LUTADOR = "garanhao"
REF = "rasga_couro/00"
CINTURA = 528  # linha de cima da corda da cintura

# só o rosto, as orelhas e os chifres: a crina fica no tronco (cabeça que gira não corta a crina)
CABECA = [(572, 420), (584, 410), (600, 422), (616, 418), (636, 432), (642, 452), (648, 472), (646, 500),
          (630, 508), (606, 504), (588, 500), (574, 492), (570, 470), (568, 444)]
BRACO_TRAS = [(446, 494), (470, 484), (492, 484), (508, 494), (514, 514), (506, 538), (502, 552), (520, 558),
              (534, 574), (534, 602), (518, 614), (494, 614), (478, 602), (468, 578), (460, 548), (456, 520)]
BRACO_FRENTE = [(570, 504), (592, 498), (608, 512), (622, 532), (642, 546), (662, 560), (672, 586), (664, 608),
                (640, 608), (624, 592), (610, 576), (596, 560), (584, 546), (572, 530)]
PERNA_TRAS = [(472, 542), (534, 542), (540, 578), (524, 606), (508, 628), (502, 662), (444, 662), (452, 640),
              (462, 612), (470, 580)]
PERNA_FRENTE = [(538, 542), (578, 538), (602, 558), (612, 588), (618, 612), (628, 640), (634, 662), (578, 662),
                (584, 640), (574, 616), (558, 600), (544, 580)]
TRONCO_ESCONDIDO = [(488, 496), (514, 496), (516, 524), (494, 524)]

JOELHO_TRAS, JOELHO_FRENTE = (493, 608), (596, 602)  # o de trás = joelho da frente girado (garanhao_pecas.py)
TORNOZELO = {"canela_tras": (470, 642), "canela_frente": (604, 642)}
OSSOS = {  # junta no parado, mãe, ponta
    "quadril": ((530, 540), None, (530, 562)),
    "tronco": ((530, 528), "quadril", (548, 466)),
    "cabeca": ((566, 492), "tronco", (604, 452)),
    "braco_tras": ((486, 500), "tronco", (506, 598)),
    "braco_frente": ((586, 510), "tronco", (648, 588)),
    "coxa_tras": ((508, 552), "quadril", JOELHO_TRAS),
    "canela_tras": (JOELHO_TRAS, "coxa_tras", TORNOZELO["canela_tras"]),
    "coxa_frente": ((566, 552), "quadril", JOELHO_FRENTE),
    "canela_frente": (JOELHO_FRENTE, "coxa_frente", TORNOZELO["canela_frente"]),
}
# de trás para a frente (o quadril, com o rabo e o calção do meio, fica atrás das pernas): o braço de longe atrás de tudo, o de perto (corda, punho na coxa) na frente
CAMADAS = ["braco_frente", "quadril", "coxa_frente", "canela_frente", "coxa_tras", "canela_tras", "tronco",
           "cabeca", "braco_tras"]
SEM_REGUA = True  # a régua da cabeça é humana; as folhas já vêm na mesma escala (importar_garanhao.py)


def _p(dx=0, dy=0, tronco=0, cabeca=0, bf=0, bt=0, pes=(0, 0), ar=False, **pernas):
    """Pose à mão: corpo (dx, dy a partir do parado), inclinação do tronco, cabeça (relativa ao tronco; + = focinho
    para baixo), braço de longe (bf) e de perto (bt); + = horário na tela. Pernas: coxa_frente/canela_frente."""
    out = {"quadril": {"ang": 0, "dx": dx, "dy": dy, "abs": 1, "pes": pes}, "tronco": {"ang": tronco}, "cabeca": {"ang": cabeca},
           "braco_frente": {"ang": bf}, "braco_tras": {"ang": bt}}
    for k, v in pernas.items():
        out[k] = {"ang": v}
    if ar:
        out["_ar"] = {"sim": 1}
    return out


def _m(base, **mud):
    """Uma pose base com mudanças (as pernas e o resto que não mudam ficam iguais)."""
    d = dict(base)
    d.update(mud)
    return _p(**d)


# agachado de quatro (inclina o tronco, patas no chão) e no ar (cascos encolhidos)
C = dict(dy=30, tronco=22, cabeca=-14, bf=-16, bt=-20, pes=(-12, 16))
A = dict(dy=-40, tronco=6, coxa_frente=-60, canela_frente=95, coxa_tras=-35, canela_tras=95, ar=True)


POSES = {
    # chifrada: abaixa a cabeça com os chifres na frente e engancha para cima
    "gancho_chifre/00": _p(),
    "gancho_chifre/01": _p(dy=8, tronco=8, cabeca=8, bf=10),
    "gancho_chifre/02": _p(dx=4, dy=18, tronco=16, cabeca=12, bf=16),
    "gancho_chifre/03": _p(dx=8, dy=8, tronco=6, cabeca=2, pes=(0, 8)),
    "gancho_chifre/04": _p(dx=10, dy=-4, tronco=-8, cabeca=-14, bf=-24, pes=(0, 10)),
    "gancho_chifre/05": _p(dx=8, dy=-2, tronco=-6, cabeca=-12, bf=-18, pes=(0, 10)),
    "gancho_chifre/06": _p(dx=4, tronco=-2, cabeca=-4, pes=(0, 6)),
    "gancho_chifre/07": _p(),
    # investida: empina o peito para trás e esmaga a testa para baixo com um passo à frente
    "cabecada_touro/00": _p(),
    "cabecada_touro/01": _p(dy=-6, tronco=-10, cabeca=-10, bf=-10, bt=-6),
    "cabecada_touro/02": _p(dx=-6, dy=-8, tronco=-14, cabeca=-14, bf=-16, bt=-10, pes=(-4, 0)),
    "cabecada_touro/03": _p(dx=12, dy=0, tronco=0, cabeca=-4, pes=(0, 22)),
    "cabecada_touro/04": _p(dx=26, dy=16, tronco=20, cabeca=12, bf=20, pes=(10, 34)),
    "cabecada_touro/05": _p(dx=24, dy=12, tronco=14, cabeca=10, bf=12, pes=(10, 34)),
    "cabecada_touro/06": _p(dx=14, dy=4, tronco=6, cabeca=2, pes=(6, 20)),
    "cabecada_touro/07": _p(dx=6, pes=(4, 8)),
    # pisão: joelho sobe até o peito e o casco desce rachando o chão, o corpo cai com o peso
    "pisao/00": _p(),
    "pisao/01": _p(dy=-10, tronco=-6, cabeca=-4, coxa_frente=-70, canela_frente=70),
    "pisao/02": _p(dy=-16, tronco=-8, cabeca=-6, bf=-14, coxa_frente=-110, canela_frente=105),
    "pisao/03": _p(dx=6, dy=-4, tronco=4, cabeca=2, coxa_frente=-45, canela_frente=30),
    "pisao/04": _p(dx=10, dy=18, tronco=16, cabeca=8, bf=16, pes=(0, 16)),
    "pisao/05": _p(dx=8, dy=10, tronco=10, cabeca=4, pes=(0, 16)),
    "pisao/06": _p(dx=4, dy=2, tronco=2, pes=(0, 10)),
    "pisao/07": _p(),
}

POSES.update({
    # patada: puxa a pata, gira o ombro e o quadril, dá meio passo e rasga na altura do peito
    "patada/00": _p(), "patada/07": _p(),
    "patada/01": _p(dx=-4, tronco=-6, cabeca=-2, bf=30),
    "patada/02": _p(dx=6, tronco=6, bf=-10, pes=(0, 10)),
    "patada/03": _p(dx=12, tronco=14, cabeca=4, bf=-50, pes=(2, 18)),
    "patada/04": _p(dx=12, tronco=12, cabeca=4, bf=-45, pes=(2, 18)),
    "patada/05": _p(dx=8, tronco=6, bf=-15, pes=(2, 12)),
    "patada/06": _p(dx=4, tronco=2, pes=(0, 6)),
    # casco na canela: tira o peso da perna da frente e estala o casco baixo
    "casco_canela/00": _p(), "casco_canela/07": _p(),
    "casco_canela/01": _p(dy=-4, tronco=-4, coxa_frente=-25, canela_frente=25),
    "casco_canela/02": _p(dy=-4, tronco=-6, coxa_frente=-40, canela_frente=15),
    "casco_canela/03": _p(dx=4, dy=-2, tronco=-8, cabeca=4, coxa_frente=-55, canela_frente=-15),
    "casco_canela/04": _p(dx=4, dy=-2, tronco=-8, cabeca=4, coxa_frente=-52, canela_frente=-12),
    "casco_canela/05": _p(tronco=-4, coxa_frente=-25, canela_frente=20),
    "casco_canela/06": _p(tronco=-2),
    # bufada: enche o peito puxando a cabeça, e joga o focinho para a frente com meio passo
    "bufada/00": _p(), "bufada/07": _p(),
    "bufada/01": _p(dy=-4, tronco=-8, cabeca=-10, bf=8),
    "bufada/02": _p(dy=-6, tronco=-10, cabeca=-14, bf=10),
    "bufada/03": _p(dx=8, tronco=8, cabeca=10, pes=(0, 10)),
    "bufada/04": _p(dx=10, tronco=10, cabeca=12, pes=(0, 12)),
    "bufada/05": _p(dx=6, tronco=4, cabeca=4, pes=(0, 8)),
    "bufada/06": _p(dx=2),
    # corrente X: revés com a pata cruzando o peito e gancho de garra subindo, sempre com o corpo indo junto
    "corrente_x/00": _p(),
    "corrente_x/01": _p(dx=-2, tronco=-8, cabeca=-4, bf=40),
    "corrente_x/02": _p(dx=10, tronco=12, bf=-70, pes=(0, 14)),
    "corrente_x/03": _p(dx=8, tronco=6, bf=-30, pes=(0, 12)),
    "corrente_x/04": _p(dx=6, dy=10, tronco=10, bf=25, pes=(0, 12)),
    "corrente_x/05": _p(dx=12, dy=-4, tronco=-8, cabeca=-10, bf=-120, pes=(4, 20)),
    "corrente_x/06": _p(dx=12, dy=-6, tronco=-12, cabeca=-14, bf=-150, pes=(4, 20)),
    "corrente_x/07": _p(dx=4, pes=(0, 6)),
    # rasga-couro: as duas patas sobem e descem em X, o corpo cai com o peso e avança
    "rasga_couro/07": _p(),
    "rasga_couro/01": _p(dy=-6, tronco=-10, cabeca=-8, bf=-120, bt=-110),
    "rasga_couro/02": _p(dy=-10, tronco=-14, cabeca=-12, bf=-160, bt=-150),
    "rasga_couro/03": _p(dx=10, dy=8, tronco=14, cabeca=6, bf=-40, bt=-50, pes=(0, 16)),
    "rasga_couro/04": _p(dx=14, dy=14, tronco=20, cabeca=10, bf=10, pes=(2, 20)),
    "rasga_couro/05": _p(dx=12, dy=12, tronco=16, cabeca=8, bf=20, bt=10, pes=(2, 20)),
    "rasga_couro/06": _p(dx=6, dy=4, tronco=6, pes=(0, 10)),
    # empinada: sobe nas patas de trás com as garras no alto e despenca para a frente
    "empinada/00": _p(),
    "empinada/01": _p(dy=-10, tronco=-12, cabeca=-10, bf=-80, bt=-60),
    "empinada/02": _p(dy=-18, tronco=-18, cabeca=-14, bf=-120, bt=-100),
    "empinada/03": _p(dy=-24, tronco=-22, cabeca=-18, bf=-150, bt=-140),
    "empinada/04": _p(dy=-24, tronco=-22, cabeca=-18, bf=-150, bt=-140),
    "empinada/05": _p(dx=18, dy=16, tronco=22, cabeca=10, bf=-30, bt=-20, pes=(4, 24)),
    "empinada/06": _p(dx=12, dy=8, tronco=10, pes=(2, 16)),
    "empinada/07": _p(dx=4, pes=(0, 6)),
    # garra rasteira: de quatro, puxa a pata e rasga rente ao chão avançando
    **{f"garra_rasteira/{i:02d}": _p(**C) for i in (0, 6, 7)},
    "garra_rasteira/01": _m(C, bf=-4),
    "garra_rasteira/02": _m(C, bf=10),
    "garra_rasteira/03": _m(C, dx=10, bf=-55, pes=(-6, 16)),
    "garra_rasteira/04": _m(C, dx=12, bf=-60, pes=(-6, 18)),
    "garra_rasteira/05": _m(C, dx=6, bf=-30, pes=(-6, 14)),
    # chifrada que sobe: de quatro, abaixa a cabeça e explode para cima com os chifres
    **{f"chifrada_sobe/{i:02d}": _p(**C) for i in (0, 6, 7)},
    "chifrada_sobe/01": _m(C, dy=32, tronco=26, cabeca=-8),
    "chifrada_sobe/02": _m(C, dy=32, tronco=28, cabeca=-2, bf=-24, bt=-28),
    "chifrada_sobe/03": _p(dy=10, tronco=4, cabeca=-16, bf=-30, bt=-20, pes=(0, 6)),
    "chifrada_sobe/04": _p(dy=-20, tronco=-14, cabeca=-32, bf=-70, bt=-50, pes=(0, 8)),
    "chifrada_sobe/05": _p(dy=-14, tronco=-10, cabeca=-24, bf=-50, bt=-30, pes=(0, 8)),
    # casco raspa: de quatro, raspa o casco para trás como touro bravo e chuta rente ao chão
    **{f"casco_raspa/{i:02d}": _p(**C) for i in (0, 6, 7)},
    "casco_raspa/01": _m(C, coxa_frente=15, canela_frente=15),
    "casco_raspa/02": _m(C, coxa_frente=25, canela_frente=25),
    "casco_raspa/03": _m(C, dx=4, coxa_frente=-35, canela_frente=-20),
    "casco_raspa/04": _m(C, dx=6, coxa_frente=-50, canela_frente=-30),
    "casco_raspa/05": _m(C, coxa_frente=-20, canela_frente=5),
    # rabo-chicote: bem baixo, a perna da frente varre o chão esticada
    **{f"rabo_chicote/{i:02d}": _p(**C) for i in (0, 6, 7)},
    "rabo_chicote/01": _m(C, dy=32),
    "rabo_chicote/02": _m(C, dy=32, coxa_frente=-40, canela_frente=-20),
    "rabo_chicote/03": _m(C, dy=32, dx=8, coxa_frente=-65, canela_frente=-35),
    "rabo_chicote/04": _m(C, dy=32, dx=8, coxa_frente=-65, canela_frente=-35),
    "rabo_chicote/05": _m(C, dy=32, coxa_frente=-25, canela_frente=0),
    # no ar
    **{f"ar_garras/{i:02d}": _p(**A) for i in (0, 6, 7)},
    "ar_garras/01": _m(A, bf=-120, bt=-100),
    "ar_garras/02": _m(A, tronco=0, bf=-140, bt=-120),
    "ar_garras/03": _m(A, tronco=12, bf=-40, bt=-40),
    "ar_garras/04": _m(A, tronco=14, bf=0, bt=0),
    "ar_garras/05": _m(A, tronco=8, bf=-10),
    **{f"ar_joelho/{i:02d}": _p(**A) for i in (0, 6, 7)},
    "ar_joelho/01": _m(A, coxa_frente=-80),
    "ar_joelho/02": _m(A, tronco=0, coxa_frente=-90, canela_frente=110),
    "ar_joelho/03": _m(A, tronco=12, dx=6, coxa_frente=-45, canela_frente=70),
    "ar_joelho/04": _m(A, tronco=12, dx=6, coxa_frente=-45, canela_frente=70),
    "ar_joelho/05": _m(A, coxa_frente=-65),
    **{f"ar_cabecada/{i:02d}": _p(**A) for i in (0, 6, 7)},
    "ar_cabecada/01": _m(A, tronco=-14, cabeca=-14),
    "ar_cabecada/02": _m(A, dy=-50, tronco=-20, cabeca=-20),
    "ar_cabecada/03": _m(A, dx=10, dy=-30, tronco=38, cabeca=18),
    "ar_cabecada/04": _m(A, dx=14, dy=-24, tronco=46, cabeca=22),
    "ar_cabecada/05": _m(A, tronco=20, cabeca=8),
    **{f"ar_cascos/{i:02d}": _p(**A) for i in (0, 6, 7)},
    "ar_cascos/01": _m(A, dy=-50, coxa_frente=-95, canela_frente=110, coxa_tras=-75, canela_tras=110),
    "ar_cascos/02": _m(A, dy=-54, coxa_frente=-100, canela_frente=115, coxa_tras=-80, canela_tras=115),
    "ar_cascos/03": _m(A, dy=-20, coxa_frente=-15, canela_frente=5, coxa_tras=-5, canela_tras=5),
    "ar_cascos/04": _m(A, dy=-20, coxa_frente=-15, canela_frente=5, coxa_tras=-5, canela_tras=5),
    "ar_cascos/05": _m(A, coxa_frente=-40, canela_frente=60, coxa_tras=-20, canela_tras=60),
    # coice: abaixa com as garras no chão, vira de costas e escoiceia (de costas = desenho da folha)
    "coice/00": _p(), "coice/07": _p(),
    "coice/01": _p(dx=-2, dy=20, tronco=26, cabeca=-14, bf=-20, bt=-20),
    "coice/06": _p(dx=-2, dy=20, tronco=26, cabeca=-14, bf=-20, bt=-20),
})
BRACO_VAR = {}
VARIANTES = {}
ANIMS = {
    "parado": (0, "rasga_couro 0/12 0/12 0/12 0/12", None),
    # chifrada: abaixa a cabeça e engancha os chifres para cima (folha g_gancho_chifre)
    "chifrada": (10210, "gancho_chifre 0/4 1/4 2/5 3/2 4/5A 5/4 6/6 7/6", (14, -96, 52, -64)),
    # investida de touro: cabeçada de cima para baixo com um passo à frente (folha g_cabecada_touro)
    "investida": (10215, "cabecada_touro 0/4 1/4 2/5 3/2 4/6A 5/5 6/6 7/6", (16, -92, 58, -56)),
    # pisão que racha o chão (folha g_pisao)
    "pisao": (10245, "pisao 0/4 1/5 2/6 3/2 4/6A 5/5 6/6 7/6", (10, -24, 54, 0)),
    # ações propostas (o .air do despertado ainda usa os desenhos da base); caixas em px do jogo
    "patada": (10200, "patada 0/3 1/3 2/2 3/4A 4/2 5/4 6/4 7/4", (14, -84, 50, -56)),
    "casco_canela": (10230, "casco_canela 0/3 1/3 2/2 3/4A 4/2 5/4 6/4 7/4", (12, -30, 50, -6)),
    "bufada": (10260, "bufada 0/3 1/5 2/5 3/3 4/6A 5/5 6/5 7/5", (14, -100, 46, -76)),
    "corrente_x": (10300, "corrente_x 0/3 1/3 2/4A 3/4 4/3 5/4A 6/4 7/5", (12, -110, 52, -56)),
    "rasga_couro": (10310, "rasga_couro 0/3 1/4 2/6 3/3A 4/5A 5/6 6/6 7/6", (10, -110, 54, -30)),
    "empinada": (10250, "empinada 0/3 1/4 2/4 3/5 4/5 5/5A 6/6 7/6", (10, -80, 56, -20)),
    "garra_rasteira": (10400, "garra_rasteira 0/3 1/3 2/3 3/4A 4/2 5/4 6/4 7/3", (12, -24, 56, -2)),
    "chifrada_sobe": (10410, "chifrada_sobe 0/3 1/3 2/4 3/2 4/6A 5/5 6/6 7/5", (6, -120, 40, -40)),
    "casco_raspa": (10430, "casco_raspa 0/3 1/4 2/4 3/2 4/5A 5/4 6/4 7/3", (12, -20, 54, -2)),
    "rabo_chicote": (10440, "rabo_chicote 0/3 1/3 2/3 3/5A 4/3 5/5 6/5 7/4", (8, -20, 62, 0)),
    "ar_garras": (10600, "ar_garras 0/3 1/3 2/3 3/5A 4/3 5/4 6/3 7/3", (6, -70, 46, -20)),
    "ar_joelho": (10630, "ar_joelho 0/3 1/3 2/3 3/6A 4/3 5/4 6/3 7/3", (8, -60, 44, -24)),
    "ar_cabecada": (10610, "ar_cabecada 0/3 1/4 2/4 3/6A 4/3 5/4 6/3 7/3", (10, -60, 52, -10)),
    "ar_cascos": (10640, "ar_cascos 0/3 1/4 2/4 3/6A 4/3 5/4 6/3 7/3", (0, -30, 40, 10)),
    "coice": (10240, "coice 0/3 1/4 2/4 3/6A 4/3 5/5 6/5 7/5", (-60, -70, 40, -30)),
}
AUTO_ESPECIAL = set()
FIRMES = set()
ESPECIAIS = {"coice/02", "coice/03", "coice/04", "coice/05"}  # de costas: desenho da folha
EXPRESSOES = {}
PERNA_NO_AR = {"pisao/01": "livre", "pisao/02": "livre", "pisao/03": "livre",
               **{f"casco_canela/{i:02d}": "livre" for i in range(1, 6)},
               **{f"casco_raspa/{i:02d}": "livre" for i in range(1, 6)},
               **{f"rabo_chicote/{i:02d}": "livre" for i in range(2, 6)}}
LACOS = {0}
NO_DA_FAIXA = [(0, 0), (1, 0), (0, 1)]  # o Garanhão não tem nó de faixa
# o Garanhão é escuro (calção, crina, cascos): quando as pernas abrem e o corpo abaixa aparece mais calção escuro entre
# as pernas, que é desenho e não contorno sobrando; a régua de mancha do robô aceita até isto a mais que a guarda
MANCHA_FOLGA = 900
