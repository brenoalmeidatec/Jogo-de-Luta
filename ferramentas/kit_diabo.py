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
