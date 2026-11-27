"""Garanhão (Gutto despertado) para os golpes da #47 que não têm folha: o agarrão em pé Levanta e Arremessa e o poder
Estouro do Garanhão. É o kit da thread do Gutto (kit_garanhao.py: mesmo corpo, recorte e poses) com braços trocados
por desenhos da própria folha do parado (g_rasga_couro, mesmas cores): a garra de longe esticada na frente
(rasga_couro/01) e erguida (rasga_couro/02). O braço de perto fica embaixo: erguido, ele abria um buraco
no lado do tronco que nenhum desenho do mesmo corpo cobre. Sai em sprites/garanhao_47, sem mexer no kit do Gutto.

  python ferramentas/importar_garanhao.py     (uma vez: quadros 3x do Garanhão)
  python ferramentas/garanhao_47_pecas.py [anims]
"""
from kit_garanhao import *  # noqa: F401,F403
from kit_garanhao import _p as _p_base

LUTADOR = "garanhao_47"


def _p(bfv=None, btv=None, **kw):
    out = _p_base(**kw)
    if bfv:
        out["braco_frente"]["var"] = bfv
    if btv:
        out["braco_tras"]["var"] = btv
    return out


VARIANTES = {
    "braco_frente": {
        # garra de longe esticada na frente, na altura do peito (agarra / empurra)
        "frente": ("rasga_couro/01", [(586, 478), (590, 458), (598, 440), (600, 420), (594, 405), (604, 392),
                                      (625, 385), (645, 395), (648, 420), (638, 432), (624, 440), (616, 460),
                                      (606, 478), (596, 486)], (592, 476), 1),
        # braço de longe erguido, garra no alto (ergue o oponente / empina)
        "alto": ("rasga_couro/02", [(592, 446), (592, 420), (604, 408), (618, 392), (622, 376), (600, 366),
                                    (588, 357), (592, 340), (615, 330), (640, 335), (645, 355), (642, 380),
                                    (640, 400), (626, 420), (612, 440), (600, 452)], (596, 442), 1),
    },
}

POSES = {
    "rasga_couro/00": _p(),
    # Levanta e Arremessa (agarrão em pé, #47): dá o passo e crava a garra no oponente, ergue os dois braços com ele
    # acima da cabeça (os raios caem), segura lá em cima, e arremessa para a frente com o corpo todo
    "levanta/00": _p(),
    "levanta/01": _p(dx=6, tronco=4, cabeca=2, bf=24, bt=-6, pes=(0, 8), bfv="frente"),
    "levanta/02": _p(dx=14, dy=2, tronco=8, cabeca=4, bf=36, bt=-8, pes=(2, 18), bfv="frente"),
    "levanta/03": _p(dx=10, dy=-4, tronco=-6, cabeca=-6, bf=22, bt=-4, pes=(2, 18), bfv="alto"),
    "levanta/04": _p(dx=8, dy=-8, tronco=-10, cabeca=-8, bf=18, bt=-8, pes=(2, 18), bfv="alto"),
    "levanta/05": _p(dx=8, dy=-6, tronco=-8, cabeca=-6, bf=20, bt=-6, pes=(2, 18), bfv="alto"),
    "levanta/06": _p(dx=18, dy=10, tronco=16, cabeca=8, bf=24, bt=-10, pes=(4, 22), bfv="frente"),
    "levanta/07": _p(dx=10, dy=4, tronco=6, cabeca=2, pes=(2, 12)),
    # Estouro do Garanhão (poder, #47): empina com os braços no alto (o garanhão da aura enche), desce com tudo e
    # empurra a garra para a frente: o garanhão sai correndo
    "estouro/00": _p(),
    "estouro/01": _p(dy=-6, tronco=-8, cabeca=-6, bf=22, bt=-6, bfv="alto"),
    "estouro/02": _p(dy=-12, tronco=-14, cabeca=-10, bf=20, bt=-10, bfv="alto"),
    "estouro/03": _p(dx=16, dy=12, tronco=16, cabeca=8, bf=34, bt=-4, pes=(2, 20), bfv="frente"),
    "estouro/04": _p(dx=18, dy=14, tronco=18, cabeca=8, bf=38, bt=-6, pes=(2, 20), bfv="frente"),
    "estouro/05": _p(dx=14, dy=10, tronco=12, cabeca=6, bf=36, bt=-4, pes=(2, 20), bfv="frente"),
    "estouro/06": _p(dx=8, dy=4, tronco=6, cabeca=2, bf=6, pes=(2, 12)),
    "estouro/07": _p(dx=2, pes=(0, 4)),
}
BRACO_VAR = {}
ANIMS = {
    "parado": (0, "rasga_couro 0/12 0/12 0/12 0/12", None),
    # agarrão em pé: o pega (4700) usa os desenhos 0 a 2; o 4710 segura com 3 a 7
    "levanta": (4710, "levanta 0/3 1/4 2/3A 3/6 4/8A 5/6 6/6A 7/6", (20, -110, 60, -70)),
    # poder: o garanhão sai no desenho 3
    "estouro": (4750, "estouro 0/3 1/5 2/8 3/3A 4/10 5/6 6/6 7/5", None),
}
PERNA_NO_AR = {}
