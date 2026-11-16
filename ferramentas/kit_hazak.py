"""Kit do Hazak (base) para o boneco de peças "corpo firme" (ferramentas/firme.py).

Tudo medido no parado/00 (tela 3x 1080x780, pés em 540,660). Polígonos e juntas são do Hazak, nada do Pengaró.
Nomes dos ossos seguem o boneco_ajuste.py: "tras" é o lado esquerdo da tela (braço com o punho no peito, perna de
trás da base) e "frente" o lado direito (punho levantado, perna da frente, a que chuta).
"""
LUTADOR = "hazaki"
REF = "parado/00"
CINTURA = 469  # linha de cima da faixa: daqui para baixo é quadril

CABECA = [(524, 346), (540, 332), (566, 332), (584, 346), (584, 384), (570, 394), (562, 400), (540, 400),
          (528, 380)]
BRACO_TRAS = [(472, 397), (482, 387), (506, 386), (519, 394), (520, 410), (535, 404), (542, 401), (552, 398),
              (566, 404), (567, 414), (562, 430), (549, 445), (529, 452), (509, 465), (492, 472), (479, 465),
              (469, 434)]
BRACO_FRENTE = [(578, 396), (590, 392), (598, 400), (604, 410), (612, 404), (626, 404), (634, 412), (633, 428),
                (626, 446), (612, 452), (600, 456), (590, 463), (578, 461), (574, 445), (578, 425), (576, 410)]
PERNA_TRAS = [(478, 512), (546, 512), (546, 556), (520, 592), (503, 622), (500, 662), (438, 662), (444, 638),
              (449, 600), (465, 555)]
PERNA_FRENTE = [(546, 512), (602, 510), (613, 545), (622, 590), (628, 620), (632, 640), (662, 648), (662, 662),
                (584, 662), (586, 635), (572, 592), (558, 565), (546, 558)]
# peito e lado do tronco escondidos pelo braço de trás (punho no peito): pintados por baixo no kit
TRONCO_ESCONDIDO = [(506, 392), (522, 392), (545, 398), (567, 404), (567, 446), (545, 456), (520, 469),
                    (506, 469)]

JOELHO_TRAS, JOELHO_FRENTE = (489, 578), (598, 580)
TORNOZELO = {"canela_tras": (472, 630), "canela_frente": (606, 630)}
OSSOS = {  # junta no parado, mãe, ponta
    "quadril": ((548, 492), None, (548, 520)),
    "tronco": ((548, 470), "quadril", (552, 400)),
    "cabeca": ((552, 398), "tronco", (555, 345)),
    "braco_tras": ((497, 402), "tronco", (545, 420)),
    "antebraco_tras": ((487, 452), "braco_tras", (540, 428)),
    "braco_frente": ((586, 410), "tronco", (620, 420)),
    "coxa_tras": ((515, 515), "quadril", JOELHO_TRAS),
    "canela_tras": (JOELHO_TRAS, "coxa_tras", TORNOZELO["canela_tras"]),
    "coxa_frente": ((575, 515), "quadril", JOELHO_FRENTE),
    "canela_frente": (JOELHO_FRENTE, "coxa_frente", TORNOZELO["canela_frente"]),
}
# de trás para a frente: braço de cima levantado fica atrás do tronco; o braço do punho no peito fica na frente
CAMADAS = ["braco_frente", "coxa_frente", "canela_frente", "coxa_tras", "canela_tras", "quadril", "tronco",
           "cabeca", "braco_tras", "antebraco_tras"]
# braço de perto em dois ossos: abaixo desta linha (dobra do cotovelo) e da coluna do punho é antebraço
ANTEBRACO_LINHA = ((470, 441), (528, 429))
PUNHO_X = 519
# pose dada à mão (vence o encaixe). "quadril" com so_dy: só a altura (-60 = o mais alto que a perna de apoio
# alcança, perna esticada); o x continua o do encaixe: onde o desenho de hoje é confuso demais para casar as peças.
# ângulos em graus (horário na tela), relativos à peça mãe; "var" troca o desenho da peça.
GUARDA = {"braco_tras": {"ang": 0}, "antebraco_tras": {"ang": 0}, "braco_frente": {"ang": 0}}
POSES = {
    "soco_reto/03": {"braco_tras": {"var": "cruzado", "ang": -2}, "tronco": {"ang": 8}},
    "soco_reto/04": {"braco_tras": {"var": "cruzado", "ang": -1}, "tronco": {"ang": 9}},
    "soco_reto/05": {"braco_tras": {"var": "cruzado", "ang": 1}, "tronco": {"ang": 8}},
    "machado/01": {**GUARDA, "coxa_frente": {"var": "esticada", "ang": -36}, "tronco": {"ang": -6}},
    "machado/02": {**GUARDA, "quadril": {"ang": 0, "dx": 0, "dy": -60, "so_dy": 1}, "coxa_frente": {"var": "esticada", "ang": -58}, "tronco": {"ang": -15}},
    "machado/03": {**GUARDA, "quadril": {"ang": 0, "dx": 0, "dy": -60, "so_dy": 1}, "coxa_frente": {"var": "esticada", "ang": -62}, "tronco": {"ang": -18}},
    "machado/04": {**GUARDA, "coxa_frente": {"var": "esticada", "ang": -14}, "tronco": {"ang": -4}},
    "machado/05": dict(GUARDA), "machado/06": dict(GUARDA), "machado/07": dict(GUARDA),
    "machado_curto/01": dict(GUARDA),
    "machado_curto/02": {**GUARDA, "quadril": {"ang": 0, "dx": 0, "dy": -60, "so_dy": 1}, "coxa_frente": {"var": "esticada", "ang": -55}, "tronco": {"ang": -12}},
    "machado_curto/03": {**GUARDA, "coxa_frente": {"var": "esticada", "ang": -25}, "tronco": {"ang": -5}},
    **{f"agachado/{i:02d}": dict(GUARDA) for i in range(2, 7)},
    **{f"chute_canela/{i:02d}": dict(GUARDA) for i in range(0, 8)},
    # rasteira: agacha, joga a perna rente ao chão e apoia a mão de perto no chão (o corpo continua o do kit)
    **{f"{g}/{i:02d}": {**GUARDA, "tronco": {"ang": 6}} for g in ("rasteira", "rasteira_arco") for i in (0, 1, 6, 7)},
    **{f"{g}/{i:02d}": {**GUARDA, "tronco": {"ang": 16}, "braco_tras": {"ang": -8}, "antebraco_tras": {"ang": 100},
                        "braco_frente": {"ang": 22}} for g in ("rasteira", "rasteira_arco") for i in (2, 3, 4, 5)},
    "machado_curto/04": dict(GUARDA), "machado_curto/05": dict(GUARDA), "machado_curto/06": dict(GUARDA),
}
# variantes de braço só nos quadros listados (senão o encaixe usa variante onde não deve)
BRACO_VAR = {"soco/03": ["esticado"], "soco/05": ["esticado"], "soco/06": ["esticado"],
             **{f"baixo_soco/{i:02d}": ["esticado"] for i in range(2, 7)}}

# variantes: peça que muda de desenho (não só de ângulo). (quadro de onde sai, polígono, junta nesse quadro)
VARIANTES = {
    "braco_tras": {  # soco cruzado: o braço de perto esticado, desenho do soco_reto/04, preso pelo ombro
        "cruzado": ("soco_reto/04", [(507, 408), (530, 401), (560, 403), (600, 407), (640, 404), (680, 404),
                                     (691, 414), (691, 441), (675, 443), (640, 438), (600, 437), (570, 441),
                                     (545, 449), (520, 453), (507, 441)], (528, 425), "fixa"),
    },
    "braco_frente": {
        "esticado": ("soco/05", [(568, 425), (580, 412), (600, 413), (630, 418), (660, 416), (687, 419),
                                 (690, 447), (670, 453), (640, 447), (610, 453), (590, 461), (569, 452)],
                     (582, 433)),
    },
    "coxa_frente": {
        "camara": ("chute_lateral/02", [(503, 470), (530, 450), (560, 444), (592, 448), (611, 462), (608, 492),
                                        (596, 512), (585, 503), (572, 508), (563, 522), (566, 547), (556, 562),
                                        (539, 562), (533, 530), (528, 508), (512, 500)], (528, 486)),
        "esticada": ("chute_lateral/04", [(518, 470), (545, 452), (580, 448), (620, 444), (662, 440),
                                          (676, 417), (695, 415), (699, 440), (695, 471), (676, 483),
                                          (650, 485), (600, 487), (560, 493), (535, 501), (516, 496)],
                     (535, 478)),
    },
}

# animações refeitas: nome -> (ação no .air, quadros como no hazaki_golpes.py, Clsn1 em px do jogo ou None)
ANIMS = {
    "parado": (0, "parado 0/7 1/7 2/7 3/7 4/7 5/7 6/7", None),
    "soco": (200, "soco 3/3 5/3A 6/4 7/3", (16, -90, 59, -76)),
    "chute_lateral": (240, "chute_lateral 1/2 2/3 3/3 4/4A 5/5 6/5 7/4", (14, -82, 56, -58)),
    "agachado": (11, "agachado 3/8 4/8 5/8 6/8", None),
    "baixo_soco": (400, "baixo_soco 2/1 3/2 4/3A 5/4 6/3", (14, -54, 57, -42)),
    "chute_canela": (430, "chute_canela 1/2 2/2 4/3A 5/4 6/3", (14, -22, 58, -4)),
    "rasteira_arco": (440, "rasteira_arco 1/3 2/3 3/2 4/4A 6/8 7/7", (12, -28, 69, -8)),
    "rasteira": (1400, "rasteira 0/4 1/5 2/3A 3/3A 4/4A 5/4A 6/8 7/6", (14, -20, 78, -2)),
    "soco_reto": (210, "soco_reto 1/2 2/3 3/2 4/4A 5/5 6/5 7/4", (14, -88, 52, -72)),
    "machado": (333, "machado 1/3 2/4 3/6 4/4A 5/5 6/7 7/5", (10, -104, 51, -66)),
    "machado_curto": (246, "machado_curto 1/5 2/7 3/4A 4/5 5/4 6/4", (10, -98, 49, -56)),
}
# expressão do rosto por quadro (o rosto é sempre o mesmo desenho; muda só a expressão)
EXPRESSOES = {}
# nó e pontas da faixa: ficam no quadril, nunca nas pernas
NO_DA_FAIXA = [(534, 470), (578, 470), (578, 562), (534, 562)]
# quadros com a perna da frente no ar e o desenho que ela usa ("livre" = coxa e canela do parado giradas)
PERNA_NO_AR = {"chute_lateral/02": "camara", "chute_lateral/03": "esticada", "chute_lateral/04": "esticada",
               "chute_lateral/05": "esticada", "chute_lateral/06": "camara",
               "machado/01": "esticada", "machado/02": "esticada", "machado/03": "esticada",
               "machado/04": "esticada", "machado_curto/01": "camara", "machado_curto/02": "esticada",
               "machado_curto/03": "esticada"}
# desenho em que o peito aparece (braços para baixo) e a área dele que serve para o peito escondido do kit
PEITO_DOADOR = ("vitoria/00", [(516, 390), (568, 400), (568, 448), (545, 458), (516, 470)])
# metade de baixo inteira tirada de um desenho bom (agachar dobra a calça larga demais para a malha)
PERNAS_VAR = {"agachado": "agachado/04", "canela": "chute_canela/03"}
PERNAS_DE = {**{f"agachado/{i:02d}": "agachado" for i in range(2, 7)},
             **{f"baixo_soco/{i:02d}": "agachado" for i in range(0, 8)},
             **{f"chute_canela/{i:02d}": ("canela" if i in (2, 3, 4) else "agachado") for i in range(0, 8)},
             **{f"{g}/{i:02d}": ("canela" if i in (2, 3, 4, 5) else "agachado")
                for g in ("rasteira", "rasteira_arco") for i in range(0, 8)}}
LACOS = {0, 11}  # animações em laço (parado, agachado)
