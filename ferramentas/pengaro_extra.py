"""Golpes que completam o kit do Pengaró (docs/regras-dos-lutadores.md, seções 3 e 4).

Aqui ficam só os dados: correntes de 3 golpes + finalizador, kombos de assinatura e os golpes exclusivos do
Despertar. Quem monta AIR, CNS e CMD é o gerar_pengaro.py. Os desenhos são das folhas que já existem em
sprites/pengaro/quadros (sem arte nova ainda); cada golpe usa uma sequência e um tempo próprios.

Quadros: "folha desenho/ticks desenho/ticks...", e um A no fim do tempo marca o desenho com caixa de golpe.
Os ticks são antes do RITMO; o gerador aplica o mesmo arredondamento no AIR e no CNS.
"""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Novo:
    estado: int
    nome: str
    quadros: tuple  # (folha, desenho, ticks, ativo)
    caixa: tuple
    danos: tuple  # um dano por trecho ativo; mais de um = golpe de vários acertos
    attr: str = "S, NA"
    guarda: str = "MA"
    tipo_st: str = "S"  # S em pé, C agachado
    chao: str = "High"
    queda: bool = False
    avanco: float = 0.0
    vel: str = ""
    ar: str = ""
    area: str = "CORPO"  # caixa do corpo: CORPO, BAIXO
    final: bool = False  # finalizador de corrente: impacto forte e derruba


def _quadros(spec):
    folha, saida = None, []
    for tok in spec.split():
        if "/" not in tok:
            folha = tok
            continue
        d, t = tok.split("/")
        ativo = t.endswith("A")
        saida.append((folha, int(d), int(t.rstrip("A")), ativo))
    return tuple(saida)


def N(estado, nome, spec, caixa, danos, **k):
    return Novo(estado, nome, _quadros(spec), caixa, tuple(danos) if isinstance(danos, (list, tuple)) else (danos,), **k)


# ---------------------------------------------------------------- correntes: golpes 2, 3 e finalizador
# O 1º golpe de cada corrente é o normal do botão (200 x, 210/215 y, 230 a, 240/245 b).
CORRENTES = (
    # soco fraco: rápida
    N(301, "Jab de Retorno", "soco 1/3 2/2 4/3A 5/2A 6/4 7/4", (10, -94, 58, -70), 35),
    N(302, "Cotovelo de Ginga", "martelo 1/4 2/3 4/3A 5/3A 6/5 7/5", (14, -94, 70, -64), 45),
    N(303, "Cabeçada de Roda", "cabecada 1/4 2/4 3/3 4/3A 5/3A 6/8 7/8", (5, -124, 66, -60), 90,
      queda=True, avanco=3.0, final=True, vel="-4,-5", ar="-3,-6"),
    # soco forte: pesada
    N(311, "Martelada", "martelo 1/5 2/4 4/4A 5/3A 6/7 7/6", (14, -94, 76, -62), 60),
    N(312, "Sola de Baixo", "chute_baixo 1/4 2/4 3/4A 4/3A 5/6 6/6 7/6", (12, -62, 66, -40), 70),
    N(313, "Armada Final", "armada 1/5 2/5 3/4A 4/4A 5/4A 6/8 7/8", (8, -122, 90, -40), 110,
      queda=True, final=True, avanco=3.0, vel="-5,-4", ar="-4,-5"),
    # chute fraco: mistura alto e baixo
    N(321, "Bicuda Dupla", "chute_baixo 1/3 2/2 3/3A 4/2A 5/4 6/4 7/4", (10, -62, 60, -42), 35),
    N(322, "Ponta Rasteira", "rasteirinha 1/3 2/3 3/3A 4/3A 5/4 6/5 7/5", (12, -20, 62, -4), 40,
      guarda="L", chao="Low", area="BAIXO"),
    N(323, "Meia-Lua Final", "chute_alto 1/3 2/3 3/3A 4/3A 5/5 6/6 7/6", (9, -110, 74, -60), 85,
      queda=True, final=True, vel="-5,-4", ar="-4,-5"),
    # chute forte: pesada
    N(331, "Calcanhar de Roda", "chute_alto 1/4 2/4 3/4A 4/3A 5/6 6/6 7/6", (9, -104, 72, -58), 60),
    N(332, "Chute de Afastar", "afastar 1/4 2/4 3/4A 4/3A 5/6 6/6 7/6", (12, -96, 78, -56), 70, vel="-6"),
    N(333, "Compasso de Roda", "compasso 1/4 2/4 3/3A 4/3A 5/6 6/6 7/6", (-30, -100, 84, -30), 110,
      queda=True, final=True, avanco=2.0, vel="-5,-4", ar="-4,-5"),
)

# ---------------------------------------------------------------- kombos de assinatura (2º e 3º golpes)
KOMBOS = (
    # Abertura: → + y, x, b
    N(340, "Ombrada Rápida", "soco 1/3 2/2 4/3A 5/2A 6/4 7/4", (10, -94, 58, -70), 40),
    N(341, "Passo de Letra Cruzado", "chute_alto 1/4 2/4 3/4A 4/3A 5/6 6/6 7/6", (9, -114, 70, -34), 80,
      guarda="HA"),
    # Alto e baixo: x, ↓ + a, y   (o 2º é baixo; o 3º é por cima)
    N(342, "Ponta de Esquiva", "rasteirinha 1/3 2/3 3/3A 4/3A 5/4 6/5 7/5", (12, -20, 62, -4), 35,
      guarda="L", chao="Low", area="BAIXO"),
    N(343, "Martelo por Cima", "martelo 1/5 2/4 4/4A 5/3A 6/6 7/6", (14, -100, 72, -70), 70, guarda="HA",
      queda=True, vel="-4,-4", ar="-3,-5"),
    # Empurrão: ← + x, y, → + b
    N(344, "Cotovelada de Recuo", "martelo 1/4 2/3 4/3A 5/3A 6/5 7/5", (14, -94, 70, -64), 55),
    N(345, "Empurrão de Sola", "afastar 1/4 2/4 3/4A 4/3A 5/6 6/6 7/6", (12, -96, 80, -56), 65, vel="-9"),
    # Lançador: a, b, ↓ + y
    N(346, "Calcanhar de Entrada", "chute_alto 1/3 2/3 3/4A 4/3A 5/5 6/5 7/5", (9, -104, 70, -58), 55),
    N(347, "Cabeçada Lançadora", "cabecada 1/4 2/4 3/3 4/3A 5/3A 6/8 7/8", (5, -124, 48, -60), 70,
      queda=True, vel="-2,-4", ar="-2,-9", final=True),
)

# ---------------------------------------------------------------- Despertar: tudo isto só vale com var(20) > 0
DESPERTO_KOMBO = (
    # Possessão: b, a, x
    N(348, "Compasso Possuído", "compasso 1/4 2/4 3/3A 4/3A 5/6 6/6 7/6", (-30, -100, 80, -30), 65),
    N(349, "Caneta Sombria", "caneta 1/4 2/4 3/4A 4/4A 5/5 6/6 7/6", (10, -20, 76, -4), 80,
      attr="C, NA", guarda="L", chao="Low", queda=True, area="BAIXO", vel="-3,-3"),
)

# correntes novas (os 4 golpes são novos): y e b
DESPERTO_CORRENTES = (
    N(3410, "Revolta de Corrente", "martelo 1/4 2/3 4/3A 5/3A 6/5 7/5", (14, -96, 78, -62), 55),
    N(3411, "Sola de Ferro", "chute_baixo 1/4 2/3 3/3A 4/3A 5/5 6/5 7/5", (12, -64, 72, -40), 60),
    N(3412, "Cabeçada Escura", "cabecada 1/4 2/3 3/3 4/3A 5/3A 6/6 7/6", (5, -124, 52, -60), 70),
    N(3413, "Roda da Possessão", "compasso 1/4 2/4 3/3A 4/3A 5/6 6/6 7/6", (-34, -104, 90, -30), 120,
      queda=True, final=True, avanco=2.2, vel="-6,-4", ar="-5,-5"),
    N(3420, "Calcanhar Sombrio", "chute_alto 1/4 2/3 3/3A 4/3A 5/5 6/5 7/5", (9, -106, 76, -58), 60),
    N(3421, "Afastar Pesado", "afastar 1/4 2/3 3/3A 4/3A 5/5 6/5 7/5", (12, -98, 82, -56), 70, vel="-7"),
    N(3422, "Armada Torta", "armada 1/4 2/4 3/3A 4/3A 5/3A 6/6 7/6", (8, -124, 80, -40), 75, guarda="HA"),
    N(3423, "Chute da Corrente Partida", "armada 1/5 2/5 3/4A 4/4A 5/4A 6/8 7/8", (8, -124, 86, -40), 125,
      queda=True, final=True, avanco=1.8, vel="-6,-4", ar="-5,-5"),
)

# seis normais com função nova no Despertar (substituem o normal base enquanto var(20) > 0)
DESPERTO_NORMAIS = (
    N(3430, "Mão de Chão Possuída", "cabecada 1/4 2/4 3/3 4/3A 5/3A 6/7 7/7", (5, -128, 46, -60), 95,
      tipo_st="C", area="BAIXO", queda=True, vel="-2,-4", ar="-2,-10"),
    N(3431, "Tranco Possuído", "martelo 1/5 2/4 4/3A 3/2 4/3A 5/3 6/6 7/6", (12, -90, 70, -62), (50, 60),
      avanco=2.4),
    N(3432, "Passo de Sombra", "chute_alto 1/6 2/5 3/4A 4/3A 5/7 6/7 7/7", (9, -116, 92, -34), 100, guarda="HA",
      avanco=1.2),
    N(3433, "Palma Torta", "soco 1/3 2/2 4/3A 5/2A 6/4 7/4", (10, -94, 66, -66), 58, avanco=-1.0),
    N(3434, "Puxada Sombria", "chute_baixo 1/4 2/3 3/3A 4/3A 5/5 6/5 7/5", (10, -78, 66, -44), 70,
      queda=True, vel="-3,-3", ar="-3,-4", avanco=-1.0),
    N(3435, "Foice Escura", "rasteira 1/6 2/5 3/3A 4/4A 5/6 6/8 7/8", (12, -20, 90, -2), 100, tipo_st="C",
      attr="C, NA", guarda="L", chao="Trip", queda=True, area="BAIXO", vel="-3,-2", ar="-3,-2"),
)

# especial exclusivo simples (o resto, com projétil, passagem e mergulho, é montado à mão no gerador)
DESPERTO_ESPECIAL = (
    N(3401, "Chute da Corrente", "chute_alto 1/5 2/4 3/3A 4/4A 5/6 6/8 7/8", (9, -110, 88, -34), 115,
      attr="S, SA", queda=True, avanco=5.0, final=True, vel="-6,-4", ar="-5,-5"),
)

# golpes montados à mão no gerador: aqui só a animação (os tempos de soltar, atravessar e bater vêm dos quadros)
ESPECIAIS_A_MAO = (
    # Garrafada em Arco (→ ← + x/y): projétil em arco, o segundo papel de projétil do Pengaró
    N(1600, "Garrafada em Arco fraca", "bola 1/5 2/6 3/4 4/5 5/6 7/22", (0, 0, 0, 0), []),
    N(1601, "Garrafada em Arco forte", "bola 1/5 2/6 3/4 4/5 5/6 7/26", (0, 0, 0, 0), []),
    # Rolê por Trás (→ ← + a/b): passa por trás do oponente e chega virado
    N(1700, "Rolê por Trás", "rolamento 1/3 2/3 3/3 4/3 5/3 6/5 7/8", (0, 0, 0, 0), []),
    N(1701, "Rolê por Trás e Chute", "rolamento 1/3 2/3 3/3 4/3 5/3 chute_alto 2/3 3/3A 4/3A 5/5 6/8", (9, -104, 72, -58),
      [70]),
    # Despertar: Mão de Sombra (projétil novo), Sombra Atravessada (passa batendo), Queda Escura (mergulho)
    N(3400, "Mão de Sombra", "golaco 1/5 2/6 3/5 4/26", (0, 0, 0, 0), []),
    N(3402, "Sombra Atravessada", "rolamento 1/3 2/3 3/3A 4/3A 5/4 6/6 7/8", (-24, -80, 70, -10), [75]),
    N(3403, "Queda Escura", "bicicleta 1/4 2/4 3/4 4/4A 5/4A 6/-1", (6, -70, 70, -20), [105]),
    # Agarrão agachado (↓ + y, colado no oponente agachado)
    N(840, "Agarrão agachado", "agarrao 2/3A 3/4 4/4 5/4", (10, -60, 44, -10), []),
    N(841, "Rasteira de Pegada", "agachado 2/3 3/3 rasteira 2/4 3/4 4/5 5/4 6/4 7/5", (0, 0, 0, 0), [], area="BAIXO"),
)

# o 2º e o 3º golpe de cada corrente dão um passo à frente: o golpe anterior empurra o oponente e, sem isso,
# o seguinte fica curto (visto no teste automático)
_SEGUE = {301, 302, 311, 312, 321, 322, 331, 332, 3410, 3411, 3412, 3420, 3421, 3422}
CORRENTES = tuple(replace(m, avanco=m.avanco or 1.8) if m.estado in _SEGUE else m for m in CORRENTES)
DESPERTO_CORRENTES = tuple(replace(m, avanco=m.avanco or 1.8) if m.estado in _SEGUE else m for m in DESPERTO_CORRENTES)

TODOS = CORRENTES + KOMBOS + DESPERTO_KOMBO + DESPERTO_CORRENTES + DESPERTO_NORMAIS + DESPERTO_ESPECIAL
