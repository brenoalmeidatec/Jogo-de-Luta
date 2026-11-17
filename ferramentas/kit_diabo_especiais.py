"""Poses das folhas dos especiais do Diabo demônio (motor do #47: Bola de Trevas, Voo Infernal, Rasgo Ascendente e o
super Juízo Final), no boneco de peças. Lido pelo fim do kit_diabo.py.

Folha nova não tem desenho de hoje: cada quadro é TROCA, ou uma pose inteira da folha-modelo (M(n, dx, dy, ang), giro
em graus em volta do meio do corpo) ou a pose do kit de outro quadro (golpe com garra, guarda). O recorte sai sem margem
e o motor põe o boneco no lugar (altura do voo e do pulo vêm da velocidade, não do quadro).
modelo: 00 agachado, 01 agachado garra baixa, 02 defesa, 03 defesa agachada, 04 deitado, 05 apanha, 06 no ar,
07 ajoelhado, 08 corrida, 09 cobrança (voando reto), 10 vitória, 11 sentado, 12 provoca, 13 agarra, 14 garra que sobe,
15 pulo para trás, 16 de costas, 17 de frente
"""


def M(n, dx=0, dy=-1, ang=0):
    """Pose inteira da folha-modelo. dy -1: o desenho do modelo pisa uma linha abaixo do chão do kit. Giro positivo é
    horário (garras descem); no ar o quadro sobe (dy) para o robô não cobrar o pé no chão."""
    return (f"modelo/{n:02d}", dx, dy, ang)


AR = -80  # no ar


GUARDA = "pe_pes/07"  # guarda do kit (mesma do fim dos golpes em pé)
POSES = {}
TROCA = {
    # Bola de Trevas: arma a garra atrás do quadril, empurra aberta na altura do peito, segura e volta
    "bola_trevas/00": "pe_maos/00", "bola_trevas/01": ("pe_maos/00", -4, 2), "bola_trevas/02": "pe_maos/02",
    "bola_trevas/03": "pe_maos/01", "bola_trevas/04": "pe_maos/01", "bola_trevas/05": "pe_maos/02",
    "bola_trevas/06": "pe_pes/02", "bola_trevas/07": GUARDA,
    # Voo Infernal: agacha, sobe encolhido, paira inclinando e mergulha com as garras na frente
    "voo/00": M(0), "voo/01": M(6, 0, AR, -8), "voo/02": M(6, 0, AR), "voo/03": M(6, 0, AR, 6),
    "voo/04": M(6, 0, AR, 16), "voo/05": M(9, 0, AR, 30), "voo/06": M(9, 0, AR, 36), "voo/07": M(0),
    # Rasgo Ascendente: agacha com a garra baixa, sobe rasgando, gira de costas, garra no alto, cai encolhido
    "rasgo/00": M(1), "rasgo/01": M(14, 0, AR, 6), "rasgo/02": M(16, 0, AR), "rasgo/03": M(14, 0, AR, -6),
    "rasgo/04": M(10, 0, AR), "rasgo/05": M(6, 0, AR), "rasgo/06": M(0), "rasgo/07": GUARDA,
    # Juízo Final, parte 1: agacha, voa reto com as garras, crava (modelo 13), sobe girando e fica de cabeça para baixo
    "juizo_a/00": M(0), "juizo_a/01": M(9, 0, AR, -8), "juizo_a/02": M(9, 0, AR), "juizo_a/03": M(13, 0, AR),
    "juizo_a/04": M(13, 0, AR, -20), "juizo_a/05": M(17, 0, AR), "juizo_a/06": M(16, 0, AR),
    "juizo_a/07": M(6, 0, AR, 180),
    # parte 2: de cabeça para baixo joga a vítima no chão, cai de pé, pousa agachado e ruge
    "juizo_b/00": M(6, 0, AR, 180), "juizo_b/01": M(9, 0, 2 * AR, 90), "juizo_b/02": M(15, 0, AR), "juizo_b/03": M(0),
    "juizo_b/04": M(12), "juizo_b/05": M(10), "juizo_b/06": M(10, 0, -3), "juizo_b/07": GUARDA,
}
