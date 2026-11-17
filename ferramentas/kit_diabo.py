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
BRACO_TRAS = [(470, 408), (490, 408), (492, 432), (490, 460), (489, 500), (496, 530), (494, 548),
              (470, 549), (444, 536), (434, 500), (436, 470), (446, 440), (458, 418)]
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
MANCHA_FOLGA = 180  # o demônio é escuro (garras e calça): a mancha varia mais quando a garra gira ou sobe na guarda
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
    "pe_maos/00": {"braco_tras": {"var": "alto", "ang": 0}, "tronco": {"ang": -4},
                   # gancho (estudo de anatomia): a garra da frente arma para trás, atrás do tronco, até o contato
                   "braco_frente": {"ang": 34}, "_atras": {"slots": ["braco_frente"]}},
    "pe_maos/01": {"braco_frente": {"var": "esticado", "ang": 0}},
    "pe_maos/02": {"braco_frente": {"var": "esticado", "ang": 22}},
    "pe_maos/04": {"braco_tras": {"var": "erguido", "ang": 0}, "braco_frente": {"var": "erguido", "ang": 0},
                   "tronco": {"ang": -5}, "_atras": {"slots": ["braco_frente"]}},
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
    "pe_pes/01": {**_GUARDA, "quadril": {"abs": 1, "dx": 10, "dy": 0, "pes": (0, 0)},  # o quadril empurra o joelho
                  "coxa_frente": {"var": "camara", "ang": -10}, "tronco": {"ang": -9}},
    "pe_pes/04": {**_GUARDA, "coxa_frente": {"var": "camara", "ang": -4}, "tronco": {"ang": -3}},
    "pe_pes/05": {**_GUARDA, "coxa_frente": {"var": "esticada", "ang": -8}, "tronco": {"ang": -8},
                  "braco_frente": {"ang": -30}, "braco_tras": {"ang": 12}},
})
# fim dos chutes: volta à guarda do kit com os pés do parado
POSES.update({f"pe_pes/{i:02d}": dict(_GUARDA) for i in (2, 3, 6, 7)})
TIRA_FAIXA = False  # o demônio não tem faixa: o marrom da pele nos rasgos da calça fica na perna
PELE = ("braco_tras", "braco_frente", "coxa_frente")
PELE_VIZINHOS = {"coxa_frente": ("quadril",)}  # ombro desenhado como pele (sem linha de corte entre braço e tronco)
# o tronco é pintado por baixo da beira da cabeça (6 px): quando o tronco inclina e a cabeça contra-gira não abre vão
TAPAR_FAIXA = 6
TAPAR = ("tronco",)

# ---------------------------------------------------------------------------------------------------------------------
# Folhas que o kit de frente não monta: quadro trocado por uma pose nova da folha-modelo (diabo_modelo.py, mesma
# escala e paleta do parado; modelo/NN inteiro, com deslocamento e giro) ou pela pose do kit de outro quadro.
# Quadro "modelo/" é quadro especial (dívida): vira montado quando a peça entrar no kit.
# modelo: 00 agachado, 01 agachado com garra baixa, 02 defesa, 03 defesa agachada, 04 deitado, 05 apanha, 06 no ar,
# 07 ajoelhado, 08 corrida, 09 cobrança, 10 vitória, 11 sentado, 12 provoca, 13 agarra, 14 garra que sobe,
# 15 pulo para trás, 16 de frente, 17 de costas
M = lambda n, dx=0, dy=0, ang=0: (f"modelo/{n:02d}", dx, dy, ang)
RESPIRA = [0, 1, 2, 2, 1, 0, 1, 2]  # px: o agachado parado respira
TROCA = {
    **{f"agachado/{i:02d}": M(0, 0, RESPIRA[i]) for i in range(2, 8)},
    "agachado_maos/00": M(0), "agachado_maos/01": M(1), "agachado_maos/02": M(1, 8), "agachado_maos/03": M(0),
    "agachado_maos/04": M(0, 0, 2), "agachado_maos/05": M(14), "agachado_maos/06": M(14, 0, -10),
    "agachado_maos/07": M(0),
    "agachado_pes/00": M(0), "agachado_pes/01": M(1, 4), "agachado_pes/02": M(1), "agachado_pes/03": M(0),
    "agachado_pes/04": M(0, 0, 2), "agachado_pes/05": M(1, 10), "agachado_pes/06": M(1, 16), "agachado_pes/07": M(0),
    "defesa/02": M(2), "defesa/03": M(2, -3), "defesa/04": M(2, -6), "defesa/05": M(2, -3),
    **{f"defesa_baixa/{i:02d}": M(3, -(0, 0, 2, 4, 6, 3, 0, 0)[i]) for i in range(8)},
    **{f"parry_baixo/{i:02d}": M((0, 3, 3, 1, 1, 3, 0, 0)[i]) for i in range(8)},
    "apanha/01": M(5), "apanha/02": M(5, -8), "apanha/03": M(5, -16, 0, -25), "apanha/04": M(5, -24, -20, -60),
    "apanha/05": M(4, -20, -12, 10), "apanha/06": M(4, -16), "apanha/07": M(4, -16),
    **{f"queda/{i:02d}": M(4, 0, (0, -10, 0, 0, 0, 0, 0, 0)[i]) for i in range(8)},
    "levanta/00": M(4), "levanta/01": M(11), "levanta/02": M(11, 0, -2), "levanta/03": M(7), "levanta/04": M(7, 0, -3),
    "levanta/05": M(0),
    "pulo/00": M(0), "pulo/01": M(0, 0, 3), "pulo/02": M(6), "pulo/03": M(6, 0, -4), "pulo/04": M(6, 0, -4),
    "pulo/05": M(6), "pulo/06": M(6, 0, 2), "pulo/07": M(0),
    **{f"vira/{i:02d}": M(16) for i in range(1, 7)},
    **{f"corrida/{i:02d}": M(8, 0, (0, -4, -6, -4, 0, -4, -6, -4)[i]) for i in range(8)},
    "recuo/02": M(0), "recuo/03": M(15), "recuo/04": M(15, -6), "recuo/05": M(0),
    **{f"provoca/{i:02d}": M(12, 0, (0, 0, 1, 2, 2, 1, 0, 0)[i]) for i in range(1, 7)},
    "vitoria/01": M(12), "vitoria/02": M(12, 0, 1), **{f"vitoria/{i:02d}": M(10, 0, (0, 0, 0, 1, 2)[i - 3]) for i in range(3, 8)},
    "intro/00": M(0), "intro/01": M(0, 0, 2), "intro/02": M(7), "intro/04": M(12), "intro/05": M(12, 0, 1),
    "intro/06": M(10), "intro/07": M(10, 0, 1),
    "derrota_sirene/00": M(4), "derrota_sirene/01": M(4), "derrota_sirene/02": M(11), "derrota_sirene/03": M(11),
    "derrota_sirene/04": M(7), "derrota_sirene/05": M(7, 0, -2), "derrota_sirene/06": M(0),
    "cobranca_garras/00": M(0), "cobranca_garras/01": M(8), "cobranca_garras/02": M(9), "cobranca_garras/03": M(9, 0, -6),
    "cobranca_garras/04": M(13),
    # agarrões: pega com as duas garras (modelo/13) e bate com as garras do kit (arranhão e garra cruzada)
    **{f"{g}/{i:02d}": v for g in ("agarrao_abraco", "agarrao_cutucao", "agarrao_perna")
       for i, v in enumerate([None, M(13), M(13, 4), "pe_maos/01", "pe_maos/04", "pe_maos/05", "pe_maos/06", None]) if v},
}
# o resto das folhas em pé é a guarda do kit (nada de desenho de hoje)
for _f in ("agachado", "defesa", "parry_alto", "recuo", "vira", "provoca", "vitoria", "intro", "derrota_sirene",
           "cobranca_garras", "agarrao_abraco", "agarrao_cutucao", "agarrao_perna", "levanta", "apanha"):
    for _i in range(8):
        FIRMES.add(f"{_f}/{_i:02d}")
        POSES.setdefault(f"{_f}/{_i:02d}", dict(_GUARDA))
POSES["agachado/01"] = {**_GUARDA, "quadril": {"abs": 1, "dx": 0, "dy": 26, "pes": (0, 0)}, "tronco": {"ang": 6}}
POSES["levanta/06"] = dict(POSES["agachado/01"])
POSES["recuo/01"] = {**_GUARDA, "quadril": {"abs": 1, "dx": -8, "dy": 8, "pes": (0, 0)}, "tronco": {"ang": -5}}
# aparar no alto: a garra da frente sobe e corta na frente da cabeça
for _i, _a in enumerate((0, -40, -75, -85, -75, -45, -15, 0)):
    if _a:
        POSES[f"parry_alto/{_i:02d}"] = {**_GUARDA, "braco_frente": {"var": "esticado", "ang": _a}, "tronco": {"ang": -3}}

# poses das folhas dos especiais (bola_trevas, voo, rasgo, juizo_a, juizo_b), feitas pela thread do motor do #47
try:
    from kit_diabo_especiais import POSES as _P_ESP, TROCA as _T_ESP  # noqa: E402
    POSES.update(_P_ESP)
    TROCA.update(_T_ESP)
except ImportError:
    pass
