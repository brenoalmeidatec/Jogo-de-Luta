"""Kit do Diabo Loiro demônio (forma do Hazak, #47) para o boneco de peças "corpo firme" (ferramentas/firme.py).

Os desenhos de hoje são as pastas m_* do diabo_terno (branch vpkpcf 7a097185), postas na tela 3x por
ferramentas/diabo_tela.py em sprites/diabo_demonio/quadros_arcade_hd. Tudo medido no parado/00 (pés em 540,660).
"tras" = lado esquerdo da tela, "frente" = lado direito (para onde ele olha).
"""
LUTADOR = "diabo_demonio"
REF = "parado/00"
CINTURA = 486  # daqui para baixo é quadril (cinto, barra do paletó, rabo e pernas)
ESCALA_FIXA = True  # as folhas da IA vieram todas na mesma escala; a régua da cabeça do Hazak não serve no demônio

CABECA = [(525, 308), (618, 308), (618, 386), (602, 401), (580, 406), (560, 406), (545, 401), (520, 399),
          (495, 399), (470, 391), (480, 377), (500, 368), (515, 358), (525, 345)]
# borda direita colada no paletó (x 492): o paletó fica todo no tronco
BRACO_TRAS = [(476, 397), (502, 399), (504, 412), (493, 432), (490, 460), (489, 500), (496, 530), (494, 548),
              (470, 549), (444, 536), (434, 500), (436, 470), (446, 440), (460, 414)]
BRACO_FRENTE = [(590, 399), (613, 404), (626, 430), (631, 458), (646, 478), (662, 503), (665, 537), (645, 542),
                (624, 532), (614, 506), (604, 482), (596, 461), (591, 441), (587, 420)]
PERNA_TRAS = [(470, 492), (538, 492), (542, 520), (531, 560), (521, 600), (507, 630), (504, 662), (436, 662),
              (448, 630), (460, 600), (466, 560)]
PERNA_FRENTE = [(540, 492), (602, 492), (616, 520), (626, 560), (626, 600), (642, 630), (650, 662), (572, 662),
                (584, 630), (588, 600), (574, 560), (548, 530)]
# rabo: linha do meio (de onde sai, atrás da mão de trás, até a ponta de flecha) e a ponta; a peça é o que é da cor do
# rabo numa faixa em volta da linha, e o trecho escondido atrás da perna é completado com a cor dele
CAUDA_LINHA = [(492, 533), (474, 541), (460, 552), (455, 570), (462, 584), (478, 591), (503, 595), (537, 590),
               (570, 581), (600, 573), (621, 569), (634, 575)]
CAUDA_LARG = 15
CAUDA_PONTA = [(628, 566), (650, 572), (664, 590), (662, 614), (646, 612), (632, 596)]
# o braço de trás fica atrás do corpo: nada fica escondido por ele
TRONCO_ESCONDIDO = [(0, 0), (1, 0), (1, 1)]
TRONCO_SOBRA = 6  # o tronco desce 6 px por cima do cinto: a respiração não abre linha no cinto
NO_DA_FAIXA = [(0, 0), (1, 0), (1, 1)]

JOELHO_TRAS, JOELHO_FRENTE = (505, 560), (606, 556)
TORNOZELO = {"canela_tras": (476, 628), "canela_frente": (600, 624)}
OSSOS = {  # junta no parado, mãe, ponta
    "quadril": ((545, 492), None, (545, 520)),
    "tronco": ((548, 486), "quadril", (562, 400)),
    "cabeca": ((566, 402), "tronco", (572, 350)),
    "braco_tras": ((490, 412), "tronco", (466, 528)),
    "braco_frente": ((598, 412), "tronco", (642, 524)),
    "coxa_tras": ((506, 506), "quadril", JOELHO_TRAS),
    "canela_tras": (JOELHO_TRAS, "coxa_tras", TORNOZELO["canela_tras"]),
    "coxa_frente": ((580, 506), "quadril", JOELHO_FRENTE),
    "canela_frente": (JOELHO_FRENTE, "coxa_frente", TORNOZELO["canela_frente"]),
    "cauda": ((500, 536), "quadril", (650, 595)),
}
CAMADAS = ["braco_tras", "coxa_tras", "canela_tras", "quadril", "coxa_frente", "canela_frente", "cauda", "tronco",
           "cabeca", "braco_frente"]

VARIANTES = {}
EXPRESSOES = {}
POSES = {}
ANIMS = {  # nome -> (estado no jogo, quadros, caixa) ; estados do diabo_demonio.py
    "parado": (0, "parado 0/7 1/7 2/7 3/7 4/7 5/7 6/7 7/7", None),
    "anda": (20, "anda 0/6 1/6 2/6 3/6 4/6 5/6 6/6 7/6", None),
    "arranhao": (4200, "pe_maos 0/3 1/3A 2/4 3/5", None),
    "garra_cruzada": (4201, "pe_maos 4/6 5/4A 6/6 7/10", None),
    "joelhada": (4202, "pe_pes 0/4 1/4A 2/5 3/7", None),
    "coice": (4203, "pe_pes 4/6 5/5A 6/6 7/10", None),
}
LACOS = {0, 20}
AUTO_ESPECIAL = {"parado", "anda", "pe_maos", "pe_pes", "agachado_maos", "agachado_pes", "agachado", "pulo",
                 "cobranca_garras"}
FIRMES = set()
ESPECIAIS = set()
# vão fechado maior que isto é de propósito (entre o braço, a coxa e o rabo): não tapa nem reprova
BURACO_MAX = 60
MANCHA_FOLGA = 150  # o demônio é escuro (garras e calça): a mancha varia mais quando a garra gira
FIRMES.update(f"parado/{i:02d}" for i in range(8))
FIRMES.update(f"anda/{i:02d}" for i in range(8))
# as garras sobem por cima da cabeça (garra cruzada) e varrem para a frente: faixa de giro maior que a do Hazak
BUSCA = {"braco_tras": (range(-170, 61, 3), 2, [None]), "braco_frente": (range(-170, 61, 3), 4, [None])}
# variantes desenhadas: (desenho de onde sai, polígono nele, junta nele, "fixa" = junta marcada à mão)
VARIANTES["braco_frente"] = {
    # garra esticada para a frente (pe_maos/01)
    "esticado": ("pe_maos/01", [(545, 398), (570, 394), (600, 400), (630, 402), (660, 402), (690, 397), (712, 398),
                                (712, 434), (690, 428), (660, 431), (630, 436), (610, 443), (590, 441), (565, 433),
                                (545, 428)], (562, 414), "fixa"),
    # garra erguida por cima da cabeça (pe_maos/04)
    "erguido": ("pe_maos/04", [(560, 280), (590, 284), (610, 300), (625, 320), (640, 345), (652, 362), (646, 392),
                               (630, 410), (605, 416), (588, 405), (592, 385), (600, 365), (590, 345), (575, 332),
                               (556, 326), (548, 300)], (596, 404), "fixa"),
}
VARIANTES["braco_tras"] = {
    # garra de trás erguida ao lado da cabeça (pe_maos/00)
    "alto": ("pe_maos/00", [(455, 338), (475, 336), (492, 343), (490, 360), (483, 372), (492, 385), (505, 395),
                            (505, 425), (495, 448), (470, 453), (440, 453), (427, 436), (437, 400), (449, 376),
                            (452, 355)], (494, 414), "fixa"),
    "erguido": ("pe_maos/04", [(455, 345), (470, 330), (490, 310), (505, 290), (520, 287), (532, 298), (526, 320),
                               (510, 332), (495, 346), (482, 362), (486, 385), (500, 400), (506, 420), (492, 438),
                               (465, 440), (448, 420), (438, 392), (444, 365)], (496, 412), "fixa"),
    "esticado": ("pe_maos/01", [(545, 398), (570, 394), (600, 400), (630, 402), (660, 402), (690, 397), (712, 398),
                                (712, 434), (690, 428), (660, 431), (630, 436), (610, 443), (590, 441), (565, 433),
                                (545, 428)], (562, 414), "fixa"),
}
# perna da frente: joelho erguido (pe_pes/04) e esticada no coice (pe_pes/05), presas no quadril
VARIANTES["coxa_frente"] = {
    "camara": ("pe_pes/04", [(550, 445), (580, 440), (605, 441), (626, 447), (630, 470), (623, 500), (626, 540),
                             (634, 560), (632, 571), (612, 571), (588, 556), (591, 520), (595, 495), (588, 480),
                             (570, 488), (550, 502)], (566, 478), "fixa"),
    "esticada": ("pe_pes/05", [(545, 452), (565, 447), (600, 446), (622, 443), (650, 440), (668, 428), (685, 417),
                               (706, 417), (706, 470), (690, 473), (650, 478), (600, 484), (565, 496), (545, 500)],
                 (552, 472), "fixa"),
}
PERNA_NO_AR = {"pe_pes/00": "camara", "pe_pes/01": "camara", "pe_pes/04": "camara", "pe_pes/05": "esticada"}
# golpes em pé: o corpo é sempre o do kit (nada de desenho de hoje), braços e perna postos à mão
FIRMES.update(f"pe_maos/{i:02d}" for i in range(8))
FIRMES.update(f"pe_pes/{i:02d}" for i in range(8))
POSES.update({
    "pe_maos/00": {"braco_tras": {"var": "alto", "ang": 0}, "tronco": {"ang": -4}},
    "pe_maos/01": {"braco_frente": {"var": "esticado", "ang": 0}},
    "pe_maos/02": {"braco_frente": {"var": "esticado", "ang": 22}},
    "pe_maos/04": {"braco_tras": {"var": "erguido", "ang": 0}, "braco_frente": {"var": "erguido", "ang": 0},
                   "tronco": {"ang": -5}},
    "pe_maos/05": {"braco_frente": {"var": "esticado", "ang": -18}, "braco_tras": {"var": "esticado", "ang": 24}},
    "pe_maos/06": {"braco_frente": {"var": "esticado", "ang": 36}, "braco_tras": {"var": "esticado", "ang": 52}},
})
# corpo inteiro no golpe: o quadril vai à frente, o tronco inclina e o pé da frente avança
PASSO = {
    "pe_maos/00": {"quadril": -4, "tronco": -3},
    "pe_maos/01": {"quadril": 12, "tronco": 7, "frente": 16},
    "pe_maos/02": {"quadril": 8, "tronco": 5, "frente": 16},
    "pe_maos/04": {"quadril": -5, "tronco": -4},
    "pe_maos/05": {"quadril": 12, "tronco": 9, "frente": 16},
    "pe_maos/06": {"quadril": 9, "tronco": 7, "frente": 14},
}
# chutes: corpo do kit parado no lugar, perna de trás plantada, perna da frente (peça desenhada) girada no quadril
_GUARDA = {"quadril": {"abs": 1, "dx": 0, "dy": 0, "pes": (0, 0)}, "braco_tras": {"ang": 0},
           "braco_frente": {"ang": -12}}
POSES.update({
    "pe_pes/00": {**_GUARDA, "coxa_frente": {"var": "camara", "ang": 0}, "tronco": {"ang": -2}},
    "pe_pes/01": {**_GUARDA, "coxa_frente": {"var": "camara", "ang": -6}, "tronco": {"ang": -4}},
    "pe_pes/04": {**_GUARDA, "coxa_frente": {"var": "camara", "ang": -4}, "tronco": {"ang": -3}},
    "pe_pes/05": {**_GUARDA, "coxa_frente": {"var": "esticada", "ang": -8}, "tronco": {"ang": -8},
                  "braco_frente": {"ang": -30}, "braco_tras": {"ang": 12}},
})
# fim dos chutes: volta à guarda do kit com os pés do parado
POSES.update({f"pe_pes/{i:02d}": dict(_GUARDA) for i in (2, 3, 6, 7)})
TIRA_FAIXA = False  # o demônio não tem faixa: o marrom da pele nos rasgos da calça fica na perna
