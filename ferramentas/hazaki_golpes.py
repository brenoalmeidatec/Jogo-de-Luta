#!/usr/bin/env python3
"""Tabela de golpes do Hazak (só dados; quem monta é ferramentas/gerar_hazaki.py).

Notação dos quadros: "folha d/t d/tA ...": desenho d da folha por t ticks; `A` marca o desenho com caixa de golpe
(Clsn1). Uma palavra sem barra troca de folha no meio ("rolada_tatame 1/3 ... chute 3/2 4/4A"). O tick do acerto
(o gatilho `Time = N` do HitDef) é a soma dos ticks antes do primeiro `A`: muda aqui, muda no .cns.

Clsn1 em pixels do jogo (eixo nos pés, x para a frente, y para cima negativo), já com 4 px além do membro; o gerador
ainda encurta até o membro de cada desenho (gp.ajustar_clsn1). Dano para attack = 100.
Numeração do elenco (200/210/230/240, 301-333, 340-347, 800-846, 1000-1701, 3000-3203), não a 5.1 literal das regras.
O Despertar (Diabo Loiro, folhas d_*) NÃO está aqui: as folhas não existem ainda.
"""
from dataclasses import dataclass


@dataclass
class Golpe:
    n: int
    nome: str
    quadros: str
    clsn1: tuple
    dano: object            # número ou tupla (um por trecho ativo)
    classe: str             # fraco, forte, final (define congelamento, faísca e som)
    tipo: str = "S"         # S em pé, C agachado, A no ar
    guarda: str = "MA"
    avanco: float = 0       # VelSet x de 3 ticks antes do ativo até o fim dele
    vel: str = None         # ground.velocity
    ar: str = None          # air.velocity
    queda: bool = False
    recupera: bool = True
    chao: str = None        # ground.type
    animtype: str = None
    hit: int = None         # ground.hittime
    leve: bool = False      # conta na corrente de fracos (var(5))
    extra: str = ""         # controladores a mais, com {n} no lugar do número
    no_hitdef: str = ""     # linhas a mais dentro do HitDef


NORMAIS = [
    Golpe(200, "Jab", "soco 3/3 5/3A 6/4 7/3", (16, -90, 59, -76), 22, "fraco", leve=True),
    Golpe(210, "Soco reto", "soco_reto 1/2 2/3 3/2 4/4A 5/5 6/5 7/4", (14, -88, 52, -72), 55, "forte", avanco=2),
    Golpe(230, "Chute baixo", "chute_baixo 1/2 2/2 3/3A 4/4 5/3 6/2", (14, -44, 63, -26), 25, "fraco", leve=True),
    Golpe(240, "Chute lateral", "chute_lateral 1/2 2/3 3/3 4/4A 5/5 6/5 7/4", (14, -82, 56, -58), 60, "forte",
          vel="-5"),
    Golpe(400, "Jab baixo", "baixo_soco 2/1 3/2 4/3A 5/4 6/3", (14, -54, 57, -42), 20, "fraco", tipo="C",
          chao="Low", leve=True),
    Golpe(410, "Joelhada subindo", "joelhada_baixo 1/3 2/4 4/5A 5/6 6/6 7/5", (2, -104, 31, -36), 58, "forte",
          tipo="C", animtype="Up", vel="-3", ar="-2,-7",
          extra="[State {n}, Antiaéreo]\ntype = NotHitBy\ntrigger1 = Time = [3,8]\nvalue = A\ntime = 1\n\n"
                "[State {n}, Efeito]\ntype = Explod\ntrigger1 = MoveHit = 1\nanim = 9208\npostype = p1\n"
                "pos = 24, -70\nremovetime = -2\nsprpriority = 4\nownpal = 1\n\n"),
    Golpe(430, "Chute na canela", "chute_canela 1/2 2/2 4/3A 5/4 6/3", (14, -22, 58, -4), 22, "fraco", tipo="C",
          guarda="L", leve=True),
    Golpe(440, "Rasteira", "rasteira_arco 1/3 2/3 3/2 4/4A 6/8 7/7", (12, -28, 69, -8), 55, "forte", tipo="C",
          guarda="L", chao="Trip", animtype="Back", queda=True, recupera=False, vel="-3,-2", ar="-3,-2"),
    Golpe(600, "Soco de martelo", "ar_soco 2/1 3/2 4/8A 6/-1", (10, -42, 54, -12), 25, "fraco", tipo="A",
          guarda="HA"),
    Golpe(601, "Cotovelo descendo", "ar_cotovelo 2/3 3/4 4/8A 6/-1", (6, -64, 36, -16), 50, "forte", tipo="A",
          guarda="HA"),
    Golpe(610, "Joelhada no ar", "ar_joelho 2/2 3/2 4/8A 6/-1", (6, -60, 33, -18), 28, "fraco", tipo="A",
          guarda="HA"),
    Golpe(611, "Chute duplo", "ar_chute_duplo 0/3 1/4 2/4A 3/3 5/5A 6/-1", (-10, -26, 59, 0), (30, 30), "forte",
          tipo="A", guarda="HA"),
    Golpe(216, "Cotovelo de Faixa", "cotovelo_faixa 1/3 2/2 3/2 4/4A 5/5 6/5 7/4", (10, -84, 42, -62), 60, "forte",
          avanco=3),
    Golpe(246, "Machado de Dojô (por cima)", "machado_curto 1/5 2/7 3/4A 4/5 5/4 6/4", (10, -98, 49, -56), 55,
          "forte", guarda="HA", avanco=1.5),
    Golpe(201, "Cutucão Sacana", "cutucao_recuo 1/2 2/3 4/3A 5/4 6/4 7/3", (20, -76, 56, -58), 30, "fraco"),
    Golpe(231, "Coice de calcanhar", "coice 1/3 2/4 3/4A 5/5 6/5 7/4", (-48, -68, -14, -46), 50, "forte"),
]

# O oponente quica: bate no chão e sobe de novo bem mais alto que o quique comum do motor (-4,5).
QUIQUE = "fall.yvelocity = -7\nfall.xvelocity = -1.2"

ESTOURO = ("[State {n}, Asfalto]\ntype = Explod\ntrigger1 = MoveHit = 1\nanim = 9205\npostype = p1\npos = 40, 0\n"
           "removetime = -2\nsprpriority = 4\nownpal = 1\n\n")

# 2º, 3º e finalizador de cada botão (o 1º é o normal do botão). O finalizador derruba.
CORRENTES = [
    Golpe(301, "Jab duplo", "jab_duplo 1/3 2/3A 3/2 4/2 5/3A 6/4 7/3", (14, -94, 52, -80), (12, 12), "fraco",
          avanco=2.5),
    Golpe(302, "Cutucão Sacana", "cutucao 2/2 3/2 4/3A 5/4 6/3 7/3", (16, -70, 50, -54), 30, "fraco", avanco=3),
    Golpe(303, "Tá Achando Ruim?", "tapa_costas 1/3 2/4 3/3 4/4A 5/5 6/6 7/5", (16, -96, 63, -80), 70, "final",
          avanco=3, queda=True, vel="-4,-5", ar="-4,-5", no_hitdef="p2stateno = 304"),  # 304: o oponente gira
    Golpe(311, "Cruzado", "cruzado 1/2 2/3 3/2 4/4A 5/5 6/4 7/4", (10, -92, 38, -74), 50, "forte", avanco=4.5),
    Golpe(312, "Cotovelada descendo", "cotovelada 1/3 2/4 4/4A 5/5 6/5 7/4", (8, -92, 40, -56), 55, "forte",
          avanco=4.5),
    Golpe(313, "Punho de Concreto curto", "calcada_levantada 1/4 2/4 3/3 4/4A 5/5 6/8 7/6", (12, -36, 41, 0), 80,
          "final", avanco=4, queda=True, vel="-2,-8", ar="-2,-8", extra=ESTOURO),
    Golpe(321, "Chute na cintura", "chute 2/2 3/2 4/3A 5/4 6/4 7/3", (14, -82, 61, -62), 30, "fraco", avanco=2.5),
    # recolhe (0), chuta alto (1), recolhe (6) e desce (7): cada desenho uma vez só, sem vai-e-volta
    Golpe(322, "Chute alto sem descer", "chute_alto_rajada 0/5 1/3A 6/5 7/5", (14, -104, 59, -74), 35,
          "fraco", avanco=2.5),
    Golpe(323, "Tesoura de Bairro", "tesoura 1/3 2/3 3/3 4/3 5/4A 6/7 7/6", (10, -88, 59, -66), 80, "final",
          avanco=3, queda=True, vel="-4,-5", ar="-4,-5"),
    Golpe(331, "Chute giratório", "chute_giratorio 1/2 2/3 3/3 4/4A 5/5 6/6 7/5", (14, -74, 61, -50), 60, "forte",
          avanco=3),
    Golpe(332, "Chute de gancho", "chute_gancho 1/4 2/4 3/2A 4/3A 5/5 6/5 7/4", (12, -100, 42, -66), 60, "forte",
          avanco=4.5),
    # o oponente quica: cai e sobe de novo num quique alto (QUIQUE)
    Golpe(333, "Machado de Dojô", "machado 1/3 2/4 3/6 4/4A 5/5 6/7 7/5", (10, -104, 51, -66), 85, "final",
          avanco=3, queda=True, vel="-1.5,-3", ar="-1.5,7", extra=ESTOURO, no_hitdef=QUIQUE),
]
# acertos exigidos (var(10)) para o finalizador sair: a corrente x conta 4 porque o jab duplo acerta duas vezes
ACERTOS_DO_FINAL = {"x": 4, "y": 3, "a": 3, "b": 3}
CORRENTE_DO_BOTAO = {"x": (200, 301, 302, 303), "y": (210, 311, 312, 313), "a": (230, 321, 322, 323),
                     "b": (240, 331, 332, 333)}

# Kombos de assinatura: o 1º golpe é um normal; aqui estão o 2º e o 3º.
KOMBOS = [
    Golpe(340, "Bom Dia, Vizinho (2)", "chute_baixo 1/2 2/2 3/3A 4/4 5/3 6/2", (14, -44, 63, -26), 30, "fraco",
          avanco=3),
    Golpe(341, "Bom Dia, Vizinho (3)", "chute_lateral 1/2 2/3 3/3 4/4A 5/5 6/5 7/4", (14, -82, 56, -58), 65,
          "forte", avanco=3.5, queda=True, vel="-5,-4", ar="-5,-4"),
    Golpe(342, "Rasteira de Calçada (2)", "chute_canela 1/2 2/2 4/3A 5/4 6/3", (14, -22, 58, -4), 28, "fraco",
          tipo="C", guarda="L", avanco=3),
    Golpe(343, "Rasteira de Calçada (3)", "chute_lateral 1/2 2/3 3/3 4/4A 5/5 6/5 7/4", (14, -82, 56, -58), 65,
          "forte", avanco=3.5, queda=True, vel="-5,-4", ar="-5,-4"),
    Golpe(344, "Sai Daqui (2)", "soco_reto 1/2 2/3 3/2 4/4A 5/5 6/5 7/4", (14, -88, 52, -72), 50, "forte",
          avanco=3),
    Golpe(345, "Sai Daqui (3)", "cotovelo_faixa 1/3 2/2 3/2 4/4A 5/5 6/5 7/4", (10, -84, 42, -62), 70, "forte",
          avanco=4.5, vel="-9", hit=24),
    Golpe(346, "Sobe, Mentiroso (2)", "chute_lateral 1/2 2/3 3/3 4/4A 5/5 6/5 7/4", (14, -82, 56, -58), 50,
          "forte", avanco=3, vel="-3"),
    Golpe(347, "Sobe, Mentiroso (3)", "joelhada_baixo 1/3 2/5 4/5A 5/6 6/6 7/5", (2, -104, 31, -36), 70, "forte",
          avanco=5, animtype="Up", queda=True, vel="-2,-8", ar="-2,-8"),
]
# entrada do .cmd: (estado, botão, direção segurada ou None, estado de onde vem)
ENTRADAS_KOMBO = [(340, "a", None, 246), (341, "b", None, 340), (342, "a", "holddown", 200), (343, "b", None, 342),
                  (344, "y", None, 201), (345, "y", "holdfwd", 344), (346, "b", None, 230),
                  (347, "y", "holddown", 346)]

# Animações dos golpes escritos à mão no gerador: número -> (quadros, Clsn1, área do corpo S/C/A)
CAIXA_REVERSAO = (-8, -105, 46, -12)
ANIM = {
    260: ("chute_lateral 1/4 2/4 3/4 4/4A 5/6 6/7 7/7", (14, -82, 56, -58), "S"),
    650: ("ar_chute 2/3 3/4 4/6A 6/-1", (10, -38, 73, -18), "A"),
    700: ("rolada_tatame 1/4 2/4 3/4 4/4 5/4 6/4", None, "C"),
    705: ("rolada_tatame 6/4 5/4 4/4 3/4 2/4 1/4", None, "C"),
    760: ("defesa 1/4A 2/10 3/10", CAIXA_REVERSAO, "S"),
    761: ("defesa 2/3", None, "S"),
    800: ("agarrao_abraco 0/3A 1/9", (10, -90, 58, -50), "S"),  # o gerador encurta até a mão + 4 px
    810: ("agarrao_abraco 1/4 2/5 3/5 4/4 5/5 6/5 7/8", None, "S"),
    830: ("agarrao_cutucao 0/3A 1/9", (10, -90, 58, -50), "S"),
    831: ("agarrao_cutucao 1/3 2/4 3/6 4/6 3/6 4/6 5/6 6/6 7/12", None, "S"),
    840: ("agarrao_perna 1/3A 2/9", (10, -40, 46, -4), "C"),
    841: ("agarrao_perna 2/4 3/4 4/5 5/5 6/5 7/6", None, "C"),
    # Punho de Concreto: soca o chão e solta a lasca
    1000: ("punho_chao 1/4 2/4 3/4 4/4 5/6 6/8 7/6", None, "S"),
    1001: ("punho_chao 1/3 2/3 3/4 4/4 5/6 6/8 7/6", None, "S"),
    # Estatueta Dourada
    1600: ("estatueta_arremesso 1/4 2/4 3/6 4/4 5/6 6/6 7/6", None, "S"),
    1601: ("estatueta_arremesso 1/4 2/4 3/6 4/4 5/6 6/6 7/6", None, "S"),
    # Ascensão de Faixa: pés no chão
    1200: ("ascensao 0/2 1/2 4/5A 5/5 6/6 7/6", (0, -116, 30, -38), "S"),
    1201: ("ascensao 0/2 1/3 4/5A 5/3A 5/8 6/10 7/10", (0, -116, 30, -38), "S"),
    # Giro de Garagem
    1300: ("giro_garagem 1/3 2/4 3/3 4/4A 5/3A 6/8 7/6", (14, -74, 66, -50), "S"),
    1301: ("giro_garagem 1/3 2/4 3/5 4/4A 5/3A 6/8 7/6", (14, -74, 66, -50), "S"),
    # Corte de Base
    1400: ("rasteira 0/4 1/5 2/3A 3/3A 4/4A 5/4A 6/8 7/6", (14, -20, 78, -2), "C"),
    1401: ("rasteira 0/5 1/6 2/3A 3/3A 4/4A 5/4A 6/8 7/6", (14, -20, 78, -2), "C"),
    # Rolada de Tatame (o chute do b é a folha `chute`: depois de virar, o coice bateria para longe)
    1700: ("rolada_tatame 1/3 2/3 3/3 4/3 5/4 6/5 7/5", None, "C"),
    1701: ("rolada_tatame 1/3 2/3 3/3 4/3 5/3 chute 3/2 4/4A 5/4 6/4 7/4", (14, -82, 61, -62), "S"),
    # Pega Bolado: corre, salta e dá a voadora; 1502/1503 são o pouso (1503 = defendido, erra feio)
    1500: ("corrida 0/3 1/3 voadora 1/3 2/3 4/12A 5/-1", (10, -44, 57, -10), "S"),
    1501: ("corrida 0/3 1/3 2/3 3/3 4/2 voadora 1/3 2/3 4/12A 5/-1", (10, -44, 57, -10), "S"),
    1502: ("voadora 6/6 7/8", None, "C"),
    1503: ("voadora 6/10 7/20", None, "C"),
    # Guarda de Aço: a caixa do 1100 é a da reversão (não tem HitDef); 1102/1103 é a resposta
    1100: ("guarda_aco 1/2 2/4A 3/14A 0/6", CAIXA_REVERSAO, "S"),
    1101: ("guarda_aco 1/2 2/4A 3/14A 0/6", CAIXA_REVERSAO, "S"),
    1102: ("guarda_aco 4/3 5/4A 6/5 7/5", (14, -78, 56, -50), "S"),
    1103: ("guarda_aco 4/3 5/4A 6/5 7/5", (14, -78, 56, -50), "S"),
    # Faixa no Asfalto (1 estoque)
    3000: ("pose_super 1/4 2/4 4/6 6/6", None, "S"),
    3001: ("chute_alto_rajada 0/3 1/3A 2/3 3/3A 4/3 5/3A 6/3 7/14", (14, -104, 59, -40), "S"),
    3002: ("sobe_chutando 1/5A 2/3 3/5A 4/3 5/5A 6/-1", (0, -120, 56, -20), "A"),
    3003: ("machado 4/4A 5/6 6/8 7/6", (6, -150, 54, -40), "S"),
    # Rapidinho da Quebrada (2 estoques)
    3200: ("pose_super 1/4 2/4 4/6 6/6", None, "S"),
    3201: ("passagem_rapida 0/2 1/2 2/4A 3/3 4/3 5/3", (-10, -90, 50, -30), "S"),
    3202: ("voadora 2/3 4/8A 6/6 7/10", (10, -44, 57, -10), "S"),
    3203: ("passagem_rapida 4/6 5/8 6/8", None, "S"),
}

MOVELIST = """<#f0f000>:Especiais:</>
Punho de Concreto <#bebebe>(projétil rasteiro)</>	_D_F^P
Estatueta Dourada <#bebebe>(projétil em arco)</>	_F_B^P
Ascensão de Faixa					_F_D^P
Guarda de Aço <#bebebe>(contra-ataque)</>		_D_B^P
Giro de Garagem						_D_F^K
Corte de Base						_D_B^K
Rolada de Tatame					_B_F^K
Pega Bolado							_B_D^K

<#f0f000>:Correntes (acertando os 3, o 4º derruba):</>
Jab, Jab duplo, Cutucão Sacana, Tá Achando Ruim?	^X^X^X^X
Soco reto, Cruzado, Cotovelada, Punho de Concreto curto	^Y^Y^Y^Y
Chute baixo, Cintura, Alto, Tesoura de Bairro	^A^A^A^A
Lateral, Giratório, Gancho, Machado de Dojô	^B^B^B^B

<#f0f000>:Kombos:</>
Bom Dia, Vizinho					_F+^B, ^A, ^B
Rasteira de Calçada					^X, _D+^A, ^B
Sai Daqui							_B+^X, ^Y, _F+^Y
Sobe, Mentiroso						^A, ^B, _D+^Y

<#f0f000>:Direcionais:</>
Cotovelo de Faixa					_F+^Y
Machado de Dojô <#bebebe>(por cima)</>		_F+^B
Cutucão Sacana						_B+^X
Coice de calcanhar					_B+^A

<#f0f000>:Supers:</>
Faixa no Asfalto <#bebebe>(1000)</>		_B_F_D^K
Rapidinho da Quebrada <#bebebe>(2000)</>	_B_F_D^P

<#f0f000>:Sistema:</>
Rolamento							^X_+^A
Golpe de afastar					^Y_+^B
Abraço de Quebrada <#bebebe>(colado)</>		[_B/_F]_+^Y
Puxa a Perna <#bebebe>(oponente agachado)</>	_D_+^Y
Cutucão Sacana <#bebebe>(agarrão, colado)</>	_B_F^Y
Provocação							^C
Parry								_F_+^C
Corrida								_F_F
Passo para trás						_B_B

<#f0f000>:No ar:</>
Soco de martelo						^X
Cotovelo descendo					^Y
Joelhada no ar						^A
Chute duplo <#bebebe>(pega agachado)</>		^B
Golpe de afastar no ar				^Y_+^B
"""
