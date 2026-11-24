"""Kit do CK despertado (Modo Ratão: chapado, caco de garrafa e paredão) para o boneco de peças "corpo firme"
(firme.py).

Tudo sai do parado do despertado (e_referencia_ginga/00, copiado para sprites/ck_e por importar_ck_e.py). Tela 3x
1080x780, pés em 540,660. "tras" = lado esquerdo da tela: o antebraço de perto, com a faixa no pulso, que cruza a
barriga (a manga larga fica no tronco e o antebraço sai dela no cotovelo); "frente" = a mão de longe com o caco da
garrafa, na beira da camisa.
"""
LUTADOR = "ck_e"
REF = "referencia_ginga/00"
CINTURA = 500  # barra da camisa aberta, por cima do short

# rosto, cabelo e o óculos na testa; o pescoço fica no tronco
CABECA = [(528, 330), (592, 330), (598, 380), (596, 392), (578, 398), (562, 394), (548, 390), (534, 380),
          (527, 360)]
# braço de perto inteiro: a manga larga no ombro e o antebraço que cruza a barriga até o punho fechado
BRACO_TRAS = [(474, 400), (484, 390), (498, 384), (512, 384), (518, 396), (514, 420), (508, 440), (516, 446),
              (540, 449), (553, 458), (559, 474), (557, 494), (540, 497), (520, 492), (505, 479), (490, 472),
              (476, 464), (472, 440), (470, 420)]
# mão de longe com o caco da garrafa
BRACO_FRENTE = [(564, 460), (584, 457), (590, 444), (600, 436), (628, 438), (630, 462), (610, 480), (604, 500),
                (592, 509), (576, 506), (570, 492), (564, 480)]
PERNA_TRAS = [(482, 500), (540, 500), (541, 560), (530, 575), (520, 600), (512, 625), (516, 664), (462, 664),
              (466, 625), (484, 595), (490, 560), (484, 530)]
PERNA_FRENTE = [(540, 500), (600, 500), (598, 560), (593, 590), (586, 618), (606, 638), (612, 664), (546, 664),
                (552, 630), (560, 600), (562, 575), (546, 560)]
# o lado do corpo debaixo da manga, a barriga e a barra da camisa por baixo do antebraço de perto
TRONCO_ESCONDIDO = [(502, 388), (522, 386), (522, 440), (562, 440), (562, 500), (490, 500), (490, 446), (493, 420),
                    (497, 400)]

JOELHO_TRAS, JOELHO_FRENTE = (505, 578), (575, 578)
TORNOZELO = {"canela_tras": (490, 622), "canela_frente": (570, 620)}
OSSOS = {  # junta no parado, mãe, ponta
    "quadril": ((540, 505), None, (540, 520)),
    "tronco": ((540, 500), "quadril", (552, 392)),
    "cabeca": ((556, 390), "tronco", (565, 345)),
    "braco_tras": ((500, 402), "tronco", (545, 480)),
    "braco_frente": ((572, 452), "tronco", (600, 470)),
    "coxa_tras": ((512, 515), "quadril", JOELHO_TRAS),
    "canela_tras": (JOELHO_TRAS, "coxa_tras", TORNOZELO["canela_tras"]),
    "coxa_frente": ((568, 515), "quadril", JOELHO_FRENTE),
    "canela_frente": (JOELHO_FRENTE, "coxa_frente", TORNOZELO["canela_frente"]),
}
CAMADAS = ["coxa_tras", "canela_tras", "coxa_frente", "canela_frente", "quadril", "tronco", "cabeca",
           "braco_frente", "braco_tras"]
SEM_REGUA = True


def _p(dx=0, dy=0, tronco=0, cabeca=0, bf=0, bt=0, pes=(0, 0), btv=None, **pernas):
    """Pose à mão: corpo (dx, dy a partir do parado), inclinação do tronco, cabeça (relativa ao tronco), mão do
    caco (bf) e antebraço de perto (bt); + = horário na tela."""
    out = {"quadril": {"ang": 0, "dx": dx, "dy": dy, "abs": 1, "pes": pes}, "tronco": {"ang": tronco},
           "cabeca": {"ang": cabeca}, "braco_frente": {"ang": bf}, "braco_tras": {"ang": bt}}
    if btv:  # antebraço de perto trocado por um desenho dele em outra pose (VARIANTES)
        out["braco_tras"]["var"] = btv
    for k, v in pernas.items():
        out[k] = {"ang": v}
    return out


POSES = {
    # parado chapado: balança devagar e meio torto em cima das pernas, a cabeça pende atrasada
    "referencia_ginga/00": _p(),
    "referencia_ginga/01": _p(dx=-1, tronco=-1, cabeca=2, bf=-1, bt=1),
    "referencia_ginga/02": _p(dx=-2, dy=1, tronco=-2, cabeca=3, bf=-2, bt=2),
    "referencia_ginga/03": _p(dx=-2, dy=1, tronco=-2, cabeca=2, bf=-1, bt=2),
    "referencia_ginga/04": _p(dx=-1, tronco=-1, cabeca=0, bf=0, bt=1),
    "referencia_ginga/05": _p(dx=1, tronco=1, cabeca=-1, bf=1, bt=-1),
    "referencia_ginga/06": _p(dx=2, dy=1, tronco=2, cabeca=-2, bf=2, bt=-2),
    "referencia_ginga/07": _p(dx=1, tronco=1, cabeca=-1, bf=1, bt=-1),
    # Paredão na Cara (agarrão em pé, #47): dá o passo e estica a mão na gola, fecha o punho e puxa, empurra a cara
    # dele na caixa de som; puxa de novo com o corpo todo e afunda a cara na caixa
    "paredao/00": _p(),
    "paredao/01": _p(dx=6, tronco=3, cabeca=-1, bf=2, bt=-6, pes=(0, 8), btv="aberta"),
    "paredao/02": _p(dx=16, dy=2, tronco=6, cabeca=-3, bf=4, bt=-2, pes=(4, 20), btv="aberta"),
    "paredao/03": _p(dx=10, tronco=0, cabeca=0, bf=2, bt=12, pes=(4, 20), btv="punho"),
    "paredao/04": _p(dx=18, dy=3, tronco=8, cabeca=-4, bf=4, bt=4, pes=(4, 20), btv="aberta"),
    "paredao/05": _p(dx=4, dy=-1, tronco=-6, cabeca=4, bf=-2, bt=14, pes=(4, 20), btv="punho"),
    "paredao/06": _p(dx=20, dy=4, tronco=11, cabeca=-6, bf=6, bt=8, pes=(4, 22), btv="aberta"),
    "paredao/07": _p(dx=8, dy=1, tronco=3, cabeca=-1, bf=2, bt=0, pes=(2, 10)),
    # Paredão no Talo (poder de longe, #47): ergue a garrafa num brinde (a caixa enche), dá o passo e solta o grave
    # com a mão aberta lá na frente
    "talo/00": _p(),
    "talo/01": _p(dx=-3, dy=1, tronco=-3, cabeca=2, bf=-2, bt=0, pes=(-2, 0), btv="garrafa"),
    "talo/02": _p(dx=-6, dy=2, tronco=-7, cabeca=4, bf=-3, bt=-4, pes=(-2, 0), btv="garrafa"),
    "talo/03": _p(dx=12, dy=2, tronco=6, cabeca=-4, bf=2, bt=-10, pes=(0, 16), btv="aberta"),
    "talo/04": _p(dx=14, dy=3, tronco=7, cabeca=-5, bf=3, bt=-8, pes=(0, 16), btv="aberta"),
    "talo/05": _p(dx=10, dy=2, tronco=4, cabeca=-2, bf=2, bt=-2, pes=(0, 16), btv="aberta"),
    "talo/06": _p(dx=5, dy=1, tronco=2, cabeca=-1, bf=1, bt=0, pes=(0, 8)),
    "talo/07": _p(),
}
BRACO_VAR = {}
# antebraço de perto em outros desenhos do despertado (só o braço; o resto do corpo continua o do kit). A peça sai
# da manga no cotovelo: junta marcada à mão onde o braço sai da camisa em cada desenho.
VARIANTES = {
    "braco_tras": {
        # mão aberta esticada para a frente (alcança a gola): manga e braço inteiros, o braço cruza o peito
        "aberta": ("agarrao/01", [(484, 400), (500, 392), (520, 395), (535, 410), (545, 424), (562, 420), (582, 414),
                                  (604, 404), (626, 400), (644, 404), (644, 420), (638, 448), (614, 450), (592, 452),
                                  (568, 458), (546, 462), (530, 460), (514, 452), (498, 448), (486, 440), (482, 420)],
                   (505, 410), 1),
        # punho fechado na altura do peito (segura a gola e puxa)
        "punho": ("agarrao/03", [(480, 420), (498, 412), (516, 416), (526, 428), (532, 446), (560, 446), (568, 440),
                                 (584, 428), (594, 420), (606, 420), (614, 426), (614, 446), (600, 452), (586, 458),
                                 (572, 466), (562, 478), (540, 482), (515, 482), (495, 478), (482, 465), (478, 440)],
                  (502, 425), 1),
        # garrafa erguida (brinde do paredão: carga do poder)
        "garrafa": ("bola/03", [(460, 364), (478, 356), (500, 366), (522, 394), (522, 410), (512, 420), (522, 432),
                                (528, 450), (520, 468), (500, 472), (484, 465), (480, 440), (484, 428), (476, 410),
                                (468, 396), (460, 380)], (508, 432), 1),
    },
}
# garrafa erguida: o braço saiu 71% da grossura do braço do parado (régua do corpo, 24/11); engorda na largura
ENGROSSAR = {("braco_tras", "garrafa"): 1.16}
ANIMS = {
    "parado": (0, "referencia_ginga 0/7 1/7 2/7 3/7 4/7 5/7 6/7 7/7", None),
    # agarrão em pé: o pega (4700) usa os desenhos 0 a 2; o 4710 segura com 3 a 7
    "paredao": (4710, "paredao 0/3 1/4 2/3A 3/6 4/6A 5/8 6/8A 7/6", (20, -110, 60, -70)),
    # poder: o grave nasce no desenho 3
    "talo": (4750, "talo 0/3 1/5 2/8 3/3A 4/10 5/6 6/6 7/5", None),
}
AUTO_ESPECIAL = set()
FIRMES = set()
ESPECIAIS = set()
EXPRESSOES = {}
PERNA_NO_AR = {}
LACOS = {0}
MANCHA_FOLGA = 900
NO_DA_FAIXA = [(0, 0), (1, 0), (0, 1)]
BURACO_CHAPADO = True  # vão fechado entre braço e corpo: sombra chapada, sem borrão
