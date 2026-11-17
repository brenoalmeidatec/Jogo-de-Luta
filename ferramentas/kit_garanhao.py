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

JOELHO_TRAS, JOELHO_FRENTE = (488, 606), (596, 602)
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


def _p(dx=0, dy=0, tronco=0, cabeca=0, bf=0, bt=0, pes=(0, 0), **pernas):
    """Pose à mão: corpo (dx, dy a partir do parado), inclinação do tronco, cabeça (relativa ao tronco; + = focinho
    para baixo), braço de longe (bf) e de perto (bt); + = horário na tela. Pernas: coxa_frente/canela_frente."""
    out = {"quadril": {"ang": 0, "dx": dx, "dy": dy, "abs": 1, "pes": pes}, "tronco": {"ang": tronco}, "cabeca": {"ang": cabeca},
           "braco_frente": {"ang": bf}, "braco_tras": {"ang": bt}}
    for k, v in pernas.items():
        out[k] = {"ang": v}
    return out


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
}
AUTO_ESPECIAL = set()
FIRMES = set()
ESPECIAIS = set()
EXPRESSOES = {}
PERNA_NO_AR = {"pisao/01": "livre", "pisao/02": "livre", "pisao/03": "livre"}
LACOS = {0}
NO_DA_FAIXA = [(0, 0), (1, 0), (0, 1)]  # o Garanhão não tem nó de faixa
# o Garanhão é escuro (calção, crina, cascos): quando as pernas abrem e o corpo abaixa aparece mais calção escuro entre
# as pernas, que é desenho e não contorno sobrando; a régua de mancha do robô aceita até isto a mais que a guarda
MANCHA_FOLGA = 900
