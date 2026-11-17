"""Kit do Pengaró despertado (Endiabrado: sombras e correntes) para o boneco de peças "corpo firme" (firme.py).

Tudo sai do parado do despertado (e_ginga/00, copiado para sprites/pengaro_e por importar_pengaro_e.py). Tela 3x
1080x780, pés em 540,660. "tras" = lado esquerdo da tela (braço de perto, punho fechado com a corrente pendurada);
"frente" = lado direito (braço de longe, mão aberta erguida com a algema).
"""
LUTADOR = "pengaro_e"
REF = "ginga/00"
CINTURA = 462  # linha de cima da faixa amarela

# rosto e o topo do cabelo (o cabelo de trás, que cai no ombro, fica no tronco)
CABECA = [(498, 289), (630, 289), (634, 330), (630, 366), (620, 388), (600, 398), (578, 394), (560, 384),
          (546, 372), (528, 358), (506, 340), (498, 316)]
BRACO_TRAS = [(446, 380), (470, 368), (500, 370), (516, 384), (514, 410), (504, 432), (502, 456), (510, 472),
              (512, 500), (502, 528), (482, 534), (462, 528), (450, 512), (436, 504), (424, 540), (406, 540),
              (406, 470), (430, 460), (442, 440), (440, 410)]
BRACO_FRENTE = [(586, 392), (604, 382), (622, 386), (630, 368), (652, 358), (684, 362), (696, 378), (690, 404),
                (676, 424), (664, 444), (664, 494), (630, 494), (628, 452), (612, 446), (598, 434), (588, 414)]
PERNA_TRAS = [(478, 470), (556, 470), (560, 520), (546, 560), (528, 596), (520, 630), (514, 664), (406, 664),
              (406, 610), (440, 580), (462, 548), (472, 510)]
PERNA_FRENTE = [(612, 470), (634, 510), (662, 556), (690, 596), (704, 664), (604, 664), (612, 624),
                (596, 596), (590, 582), (612, 560), (614, 500)]
TRONCO_ESCONDIDO = [(500, 396), (520, 396), (522, 450), (504, 450)]

JOELHO_TRAS, JOELHO_FRENTE = (500, 576), (604, 572)
TORNOZELO = {"canela_tras": (468, 628), "canela_frente": (636, 626)}
OSSOS = {  # junta no parado, mãe, ponta
    "quadril": ((556, 478), None, (556, 500)),
    "tronco": ((556, 466), "quadril", (576, 392)),
    "cabeca": ((574, 392), "tronco", (596, 340)),
    "braco_tras": ((484, 396), "tronco", (480, 500)),
    "braco_frente": ((604, 400), "tronco", (668, 384)),
    "coxa_tras": ((524, 490), "quadril", JOELHO_TRAS),
    "canela_tras": (JOELHO_TRAS, "coxa_tras", TORNOZELO["canela_tras"]),
    "coxa_frente": ((584, 490), "quadril", JOELHO_FRENTE),
    "canela_frente": (JOELHO_FRENTE, "coxa_frente", TORNOZELO["canela_frente"]),
}
CAMADAS = ["braco_frente", "coxa_tras", "canela_tras", "coxa_frente", "canela_frente", "quadril", "tronco",
           "cabeca", "braco_tras"]
SEM_REGUA = True


def _p(dx=0, dy=0, tronco=0, cabeca=0, bf=0, bt=0, pes=(0, 0), bfv=None, **pernas):
    """Pose à mão: corpo (dx, dy a partir do parado), inclinação do tronco, cabeça (relativa ao tronco), braço de
    longe (bf) e de perto (bt); + = horário na tela."""
    out = {"quadril": {"ang": 0, "dx": dx, "dy": dy, "abs": 1, "pes": pes}, "tronco": {"ang": tronco},
           "cabeca": {"ang": cabeca}, "braco_frente": {"ang": bf}, "braco_tras": {"ang": bt}}
    if bfv:  # braço de longe trocado por um desenho dele esticado (VARIANTES)
        out["braco_frente"]["var"] = bfv
    for k, v in pernas.items():
        out[k] = {"ang": v}
    return out


POSES = {
    # parado: quase não encosta no chão; o corpo balança devagar em cima das pernas paradas, a mão aberta chama as
    # sombras e o punho de trás pesa com a corrente. Pernas iguais ao parado (a calça larga não abre).
    "ginga/00": _p(),
    "ginga/01": _p(tronco=-1, cabeca=1, bf=-3, bt=-2),
    "ginga/02": _p(dx=-1, tronco=-2, cabeca=2, bf=-6, bt=-3),
    "ginga/03": _p(dx=-1, tronco=-2, cabeca=1, bf=-4, bt=-2),
    "ginga/04": _p(tronco=0, cabeca=0, bf=0, bt=0),
    "ginga/05": _p(dx=1, tronco=1, cabeca=-1, bf=3, bt=-1),
    "ginga/06": _p(dx=1, tronco=2, cabeca=-2, bf=5, bt=-1),
    "ginga/07": _p(tronco=1, cabeca=-1, bf=2, bt=0),
    # Algema das Sombras (agarrão em pé, #47): a mão aberta avança com um passo e agarra o pescoço, a corrente do
    # pulso enrola (efeito), ele ergue o oponente com o braço esticado para o alto e bate de volta no chão
    "algema/00": _p(),
    "algema/01": _p(dx=4, tronco=4, cabeca=-2, bf=-4, bt=-4, pes=(0, 6), bfv="aberta"),
    "algema/02": _p(dx=14, dy=2, tronco=6, cabeca=-4, bf=2, bt=-8, pes=(4, 18), bfv="aberta"),
    "algema/03": _p(dx=10, dy=0, tronco=2, cabeca=0, bf=0, bt=-6, pes=(4, 18), bfv="punho"),
    "algema/04": _p(dx=6, dy=-2, tronco=-8, cabeca=6, bf=0, bt=-4, pes=(4, 18), bfv="alto"),
    "algema/05": _p(dx=14, dy=8, tronco=12, cabeca=-8, bf=34, bt=-10, pes=(4, 18), bfv="punho"),
    "algema/06": _p(dx=10, dy=4, tronco=6, cabeca=-3, bf=16, bt=-6, pes=(4, 14), bfv="punho"),
    "algema/07": _p(dx=4, tronco=2, bf=6, bt=-2, pes=(2, 6)),
    # Maré das Correntes (poder de longe, #47): recolhe as duas mãos para trás (carga), dá o passo e empurra a mão
    # aberta para a frente soltando a torrente; o punho de trás sobe junto
    "mare/00": _p(),
    "mare/01": _p(dx=-4, tronco=-4, cabeca=3, bf=-14, bt=-2, pes=(-2, 0)),
    "mare/02": _p(dx=-8, dy=2, tronco=-8, cabeca=5, bf=-26, bt=-3, pes=(-2, 0)),
    "mare/03": _p(dx=12, dy=2, tronco=6, cabeca=-5, bf=0, bt=-6, pes=(0, 16), bfv="garra"),
    "mare/04": _p(dx=14, dy=4, tronco=8, cabeca=-6, bf=2, bt=-8, pes=(0, 16), bfv="garra"),
    "mare/05": _p(dx=10, dy=2, tronco=4, cabeca=-3, bf=6, bt=-6, pes=(0, 16), bfv="aberta"),
    "mare/06": _p(dx=5, tronco=2, cabeca=-1, bf=10, bt=-6, pes=(0, 8)),
    "mare/07": _p(),
}
BRACO_VAR = {}
# braço de longe em outros desenhos do despertado (só o braço; o resto do corpo continua o do kit). Junta marcada à
# mão no ombro de cada desenho.
VARIANTES = {
    "braco_frente": {
        # mão aberta esticada para a frente (agarrar, soltar a torrente)
        "aberta": ("agarrao/01", [(596, 384), (620, 380), (660, 372), (676, 358), (714, 360), (718, 384), (708, 406),
                                  (678, 412), (670, 422), (672, 470), (636, 470), (640, 422), (620, 422), (600, 428),
                                  (596, 420)], (598, 402), 1),
        # punho fechado na frente (segurando o pescoço)
        "punho": ("agarrao/02", [(598, 386), (620, 376), (650, 378), (680, 382), (714, 386), (718, 414), (702, 426),
                                 (680, 422), (678, 468), (644, 468), (648, 426), (620, 426), (600, 430), (598, 418)],
                  (600, 404), 1),
        # braço erguido com o punho no alto (levanta o oponente)
        "alto": ("bola/03", [(572, 318), (584, 312), (610, 298), (640, 278), (670, 270), (686, 286), (682, 308),
                             (662, 318), (644, 322), (652, 340), (652, 372), (616, 372), (614, 342), (596, 352),
                             (586, 356), (574, 346)], (566, 350), 1),
        # garra aberta esticada (empurra a maré para a frente)
        "garra": ("bola/04", [(598, 368), (620, 362), (660, 360), (690, 350), (700, 332), (742, 334), (746, 360),
                              (736, 386), (714, 402), (714, 442), (666, 442), (662, 410), (640, 404), (610, 404),
                              (598, 398)], (600, 388), 1),
    },
}
ANIMS = {
    "parado": (0, "ginga 0/6 1/6 2/6 3/6 4/6 5/6 6/6 7/6", None),
    # agarrão em pé: o pega (4700) usa os desenhos 0 a 2; o 4710 segura com 3 a 7
    "algema": (4710, "algema 0/3 1/4 2/3A 3/6 4/8 5/6A 6/6 7/5", (20, -110, 60, -70)),
    # poder: a torrente nasce no desenho 3
    "mare": (4750, "mare 0/3 1/5 2/6 3/3A 4/10 5/6 6/6 7/5", None),
}
AUTO_ESPECIAL = set()
FIRMES = set()
ESPECIAIS = set()
EXPRESSOES = {}
PERNA_NO_AR = {}
LACOS = {0}
NO_DA_FAIXA = [(0, 0), (1, 0), (0, 1)]
MANCHA_FOLGA = 900
