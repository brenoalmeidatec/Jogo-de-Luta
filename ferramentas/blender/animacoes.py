"""Animações do lutador como quadros-chave de pose (veja rig.py para as chaves).

Cada animação é (n_quadros, loop, [(tempo 0..1, pose), ...]). O tempo vai de 0 a 1; em animação com loop o último
quadro-chave volta para o primeiro sozinho. Mexa nos ângulos aqui e rode ferramentas/blender/gerar.py de novo.
Todo lutador novo reaproveita as mesmas animações (a pose é só ângulo); só muda o dicionário de medidas em rig.py.
"""
import math

# ------------------------------------------------------------------ poses-base
# F = lado da frente (perto da câmera), T = lado de trás. Ângulo positivo = para frente.
GUARDA = dict(tronco=9, pescoco=-3, cabeca=-5,
              ombro_F=58, cotovelo_F=62, mao_F=-10, ombro_T=22, cotovelo_T=100,
              coxa_F=27, joelho_F=26, coxa_T=-24, joelho_T=14, giro=-8)

GINGA_A = dict(GUARDA, ombro_F=62, cotovelo_F=58, ombro_T=24, cotovelo_T=98, giro=-10)
GINGA_B = dict(tronco=14, pescoco=-4, cabeca=-6, ombro_F=38, cotovelo_F=78, ombro_T=40, cotovelo_T=84,
               coxa_F=10, joelho_F=34, coxa_T=-12, joelho_T=30, giro=-2, quadril=2)
GINGA_C = dict(tronco=9, pescoco=-3, cabeca=-5,  # troca: perna de trás vem para frente
               ombro_F=26, cotovelo_F=96, ombro_T=60, cotovelo_T=60, mao_T=-10,
               coxa_F=-24, joelho_F=14, coxa_T=27, joelho_T=26, giro=-6)
GINGA_D = dict(GINGA_B, ombro_F=42, cotovelo_F=82, ombro_T=36, cotovelo_T=80, giro=-10)

AGACHADO = dict(tronco=28, pescoco=-8, cabeca=-14, ombro_F=64, cotovelo_F=70, ombro_T=26, cotovelo_T=96,
                coxa_F=78, joelho_F=118, coxa_T=64, joelho_T=126, giro=-10, quadril=-6)

SOCO_PREP = dict(tronco=14, ombro_F=-14, cotovelo_F=112, ombro_T=70, cotovelo_T=70,
                 coxa_F=26, joelho_F=26, coxa_T=-26, joelho_T=16, giro=-26)
SOCO_ACERTO = dict(tronco=12, pescoco=-4, cabeca=-4, ombro_F=88, cotovelo_F=0, ombro_T=10, cotovelo_T=112,
                   coxa_F=34, joelho_F=34, coxa_T=-28, joelho_T=10, giro=18, quadril=3, dx=0.07)

CHUTE_PREP = dict(tronco=-6, ombro_F=48, cotovelo_F=82, ombro_T=22, cotovelo_T=96,
                  coxa_F=70, joelho_F=104, pe_F=-10, coxa_T=-6, joelho_T=8, giro=-6)
CHUTE_ACERTO = dict(tronco=-22, pescoco=6, cabeca=8, ombro_F=26, cotovelo_F=96, ombro_T=-22, cotovelo_T=60,
                    coxa_F=92, joelho_F=2, pe_F=-70, coxa_T=-2, joelho_T=2, giro=-12, dx=-0.05)

PULO_PREP = dict(AGACHADO, coxa_F=60, joelho_F=100, coxa_T=52, joelho_T=104, tronco=22)
PULO_SOBE = dict(tronco=6, ombro_F=95, cotovelo_F=20, ombro_T=70, cotovelo_T=40,
                 coxa_F=18, joelho_F=44, pe_F=40, coxa_T=-10, joelho_T=30, pe_T=40, giro=-8)
PULO_TOPO = dict(tronco=20, pescoco=-6, cabeca=-10, ombro_F=64, cotovelo_F=80, ombro_T=40, cotovelo_T=96,
                 coxa_F=78, joelho_F=100, pe_F=10, coxa_T=62, joelho_T=110, pe_T=10, giro=-10)
PULO_DESCE = dict(tronco=10, ombro_F=80, cotovelo_F=40, ombro_T=60, cotovelo_T=60,
                  coxa_F=32, joelho_F=40, pe_F=30, coxa_T=-8, joelho_T=26, pe_T=30, giro=-8)


def _suave(t):
    return t * t * (3 - 2 * t)


def mistura(a, b, t):
    chaves = set(a) | set(b)
    return {k: a.get(k, 0.0) + (b.get(k, 0.0) - a.get(k, 0.0)) * t for k in chaves}


def amostrar(chaves, t, loop):
    """Pose no instante t (0..1) entre quadros-chave, com suavização nas pontas de cada trecho."""
    ks = sorted(chaves, key=lambda c: c[0])
    if loop:
        ks = ks + [(ks[0][0] + 1.0, ks[0][1])]
    t = t if not loop else t % 1.0
    for (t0, p0), (t1, p1) in zip(ks, ks[1:]):
        if t0 <= t <= t1:
            u = 0 if t1 == t0 else (t - t0) / (t1 - t0)
            return mistura(p0, p1, _suave(u))
    return dict(ks[-1][1])


def _cicl(ang, amp, fase=0):
    return ang + amp * math.sin(math.tau * fase)


def andar():
    """Passo: 8 quadros-chave de um ciclo de caminhada com guarda alta."""
    base = dict(tronco=9, pescoco=-3, cabeca=-5, ombro_F=55, cotovelo_F=70, ombro_T=24, cotovelo_T=96, giro=-8)
    chaves = []
    for i in range(8):
        f = i / 8
        a = math.sin(math.tau * f)          # perna da frente: + = para frente
        b = -a
        pf = dict(base)
        pf["coxa_F"] = 26 * a + 4
        pf["coxa_T"] = 26 * b + 4
        # joelho dobra quando a perna passa para frente (balanço)
        pf["joelho_F"] = 6 + 46 * max(0.0, math.cos(math.tau * f))
        pf["joelho_T"] = 6 + 46 * max(0.0, -math.cos(math.tau * f))
        pf["ombro_F"] += 5 * a
        pf["ombro_T"] += 5 * b
        pf["quadril"] = 2 * a
        chaves.append((f, pf))
    return chaves


# n_quadros, loop, chaves, ticks por quadro sugeridos
ANIMACOES = {
    "ginga": (32, True, [(0.0, GINGA_A), (0.25, GINGA_B), (0.5, GINGA_C), (0.75, GINGA_D)], 2),
    "andar": (32, True, andar(), 2),
    "agachar": (8, False, [(0.0, GINGA_A), (0.45, mistura(GINGA_A, AGACHADO, 0.6)), (1.0, AGACHADO)], 2),
    "soco": (8, False, [(0.0, GUARDA), (0.28, SOCO_PREP), (0.5, SOCO_ACERTO), (0.72, SOCO_ACERTO),
                        (1.0, GUARDA)], 2),
    "chute": (12, False, [(0.0, GUARDA), (0.28, CHUTE_PREP), (0.5, CHUTE_ACERTO), (0.66, CHUTE_ACERTO),
                          (0.84, CHUTE_PREP), (1.0, GUARDA)], 2),
    "pulo": (16, False, [(0.0, GUARDA), (0.16, PULO_PREP), (0.32, PULO_SOBE), (0.52, PULO_TOPO),
                         (0.72, PULO_DESCE), (0.86, PULO_PREP), (1.0, GUARDA)], 3),
}


def altura(nome, t):
    """Altura do salto em metros (parábola) para animações no ar."""
    # No jogo a trajetória do salto vem do motor (.cns); o sprite fica no chão do quadro, só muda a pose.
    return 0.0


def pose(nome, i):
    n, loop, chaves, _ = ANIMACOES[nome]
    t = i / n if loop else i / (n - 1)
    p = amostrar(chaves, t, loop)
    p["altura"] = altura(nome, t)
    return p
