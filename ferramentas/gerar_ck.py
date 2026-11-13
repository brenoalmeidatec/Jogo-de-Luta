#!/usr/bin/env python3
"""Gera o CK, o Boxeador de Rua (ficha em docs/fichas/ck.md), sobre o gerador do Pengaró.

O kit (números de estado, nomes de comando, correntes, agarrões, Despertar) é o do gerar_pengaro.py, porque o robô
(ferramentas/robo/robo.lua) testa por estado e por nome de comando. O que é do CK: a arte inteira (arcade, 58 folhas em
sprites/ck/quadros_arcade, sem quadro do meio), os movimentos dos comandos da ficha, os golpes (tabelas abaixo), os
projéteis (nuvem da Tragada, Boné Voador que vai e volta, Garrafa Voadora e óculos no Modo Ratão), o Contragolpe, o
Pêndulo, a Rajada da Esquina, o paredão de som (entrada, Despertar, Baile e Grave) e a aura de fumaça verde.

  python ferramentas/converter_ck.py         folhas_arcade -> quadros_arcade e efeitos (já rodado; leva ~15 min)
  python ferramentas/gerar_ck.py             monta chars/ck
  python ferramentas/gerar_ck.py --alcance   imprime até onde vai a caixa de cada golpe, sem gravar nada
"""
import functools
import re
import shutil
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
from PIL import Image

import gerar_pengaro as gp
import aura_ck
import hd
from repertorio import Golpe

N = gp.extra.N
RAIZ = gp.RAIZ
SAIDA = RAIZ / "chars/ck"
QUADROS = RAIZ / "sprites/ck/quadros_arcade"
QUADROS_HD = RAIZ / "sprites/ck/quadros_arcade_hd"  # os mesmos desenhos em 3x (converter_ck.py com HD=3)
EFEITOS = RAIZ / "sprites/ck/efeitos"
RETRATO = RAIZ / "sprites/ck-selecao-kof.png"
EX, EY = gp.EIXO_X, gp.EIXO_Y

# ================================================================ o gerador comum no modo "só desenhos" (arcade)
gp.SAIDA = SAIDA
gp.QUADROS = gp.QUADROS_PENGARO = gp.QUADROS_ARCADE = QUADROS  # desenhado() verdadeiro: ginga e andar sem fluxo
# no fim: os números dos sprites de antes não andam. corre e recuo (Lote 7) são folhas do Pengaró que o CK não tem.
gp.FOLHAS = tuple(f for f in gp.FOLHAS if f not in ("corre", "recuo")) + ("bone_voador", "e_beck")
gp.ARCADE = set(gp.FOLHAS)
# retoques que são do desenho do Pengaró: nada disso vale para as folhas do CK
gp.PASTA_ARCADE, gp.DESLOCA_ARCADE, gp.DESENHOS_ARCADE_DO_GOLPE = {}, {}, {}
gp.CAIXA_ARCADE, gp.CAIXA_DESPERTADA, gp.ULTIMO_DESENHO, gp.TROCA_ENDIABRADA = {}, {}, {}, {}
gp.MEIO_PROIBIDO, gp.DESENHO_PROIBIDO, gp.ALGEMA_SO_ATRAS = set(), set(), set()
# Lote 7 do Pengaró (2026-11-11, o Endiabrado virou boss na arte arcade) mudou o gerador comum para as folhas DELE:
# a 2ª metade do Despertar lê quadros_arcade/e_despertar (que o CK não tem: o gerador quebrava com FileNotFoundError),
# as folhas e_ passam por colar_boss (que desliza o desenho até 30 px), o sprite sem folha cai em POSE_BOSS e alguns
# desenhos se repetem (REPETE_ARCADE). Nada disso vale para o CK: o Despertar dele é a folha despertar_b dele e o
# Ratão entra como está, no lugar em que foi desenhado.
gp.BOSS, gp.TROCA_BOSS, gp.REPETE_ARCADE, gp.ENDIABRADO_EMPRESTADO = set(), {}, {}, {}
gp.eh_boss = lambda arquivo: False
gp.colar_boss = lambda normal, boss: boss
_quadro_folha_do_kit = gp.quadro_folha


def quadro_folha(folha, i):
    if folha == "despertar_b":
        arquivo = QUADROS / folha / f"{i:02d}.png"
        return abrir_quadro(arquivo) if arquivo.exists() else None
    return _quadro_folha_do_kit(folha, i)


gp.quadro_folha = quadro_folha
gp.LOOPS = {"ginga_fluida": ("referencia_ginga", tuple(range(8)), (5,) * 8),
            "anda_fluida": ("anda", tuple(range(8)), (5,) * 8)}
gp.LOOPS_ENDIABRADOS = {"ginga_fluida": ("e_referencia_ginga", tuple(range(8))),
                        "anda_fluida": ("e_anda", tuple(range(8)))}

# Folhas de golpe: o conversor centra cada figura na célula, então no soco esticado o punho ia só 34 px à frente do
# eixo e o pé de trás aparecia 17 px atrás do lugar dele na guarda (o corpo "escorregava" para trás ao bater). Nestas
# folhas o calcanhar de trás fica onde está na guarda (x = -23 na base, -24 no Ratão): se a figura centrada o põe mais
# atrás, ela anda para a frente (até 24 px). Nunca anda para trás. Folhas de ar, queda, andar e cena ficam centradas.
ANCORA = {"soco", "martelo", "chute_baixo", "chute_alto", "afastar", "baixo_soco", "cabecada", "rasteirinha",
          "rasteira", "agarrao", "bola", "bone_voador", "compasso", "armada", "caneta", "golaco", "rolamento", "beck",
          "juliet_voadora"}
CALCANHAR = {False: -23, True: -24}


@functools.lru_cache(maxsize=None)
def _abrir(arquivo):
    a = np.array(Image.open(arquivo).convert("RGBA"))
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    pasta = Path(arquivo).parent.name
    ratao = pasta.startswith("e_")
    if ratao:
        # risquinhos soltos acima da cabeça (resto do fiapo de fumaça depois de quantizar): sai toda ilha de até 12 px
        import cv2
        n, rot, info, _ = cv2.connectedComponentsWithStats((a[..., 3] > 0).astype(np.uint8), connectivity=8)
        for k in range(1, n):
            if info[k, cv2.CC_STAT_AREA] <= 12:
                a[rot == k] = 0
    if (pasta[2:] if ratao else pasta) in ANCORA and a.shape[:2] == (gp.ALT, gp.LARG):
        chao = np.flatnonzero((a[EY - 8:EY, :, 3] > 0).any(axis=0))
        if len(chao):
            dx = max(0, min(24, EX + CALCANHAR[ratao] - int(chao[0])))
            if dx:
                a = np.roll(a, dx, axis=1)
                a[:, :dx] = 0
    return Image.fromarray(a)


def abrir_quadro(arquivo):
    """Quadro arcade do CK, já na tela do jogo (360x260, base em y=219): só o alfa duro e a âncora do calcanhar. As
    limpezas do abrir_quadro do Pengaró (franja magenta, rosa, caneleira) apagariam o roxo do boné e da camisa."""
    return _abrir(str(arquivo)).copy()


gp.abrir_quadro = abrir_quadro
gp.quadro_loop = lambda pasta, i: abrir_quadro(QUADROS / gp.LOOPS[pasta][0] / f"{gp.LOOPS[pasta][1][i]:02d}.png")
# As duas formas saem do conversor na mesma escala e com a mesma base: o desenho do Ratão entra como está.
gp.fator_endiabrado = lambda pasta: 1.0
gp.dx_chave = lambda pasta, n: 0
gp.colar_endiabrado = lambda normal, endiabrado, fator=1.0, dx=None: endiabrado

# Folha da base sem folha e_ própria: usa a folha do Ratão que faz o movimento mais parecido (provisório, veja o
# LOGBOOK). (folha do Ratão, desenhos na ordem dos 8 da base ou None para os mesmos).
# golaco (ganchos da base): na e_golaco refeita o desenho 3 é a rasteira deslizando e o 5-6 o agachado; os ganchos do
# Ratão usam só as estocadas em pé (1 arma, 2 estoca, 4 estoca por cima, 7 estoca baixa de passo) e o soco agachado
# usa o agachado (5) e a estocada rente ao chão (3).
E_FOLHA = {"afastar": ("e_chute_alto", None), "baixo_soco": ("e_golaco", (5, 5, 5, 3, 3, 5, 5, 5)),
           "golaco": ("e_golaco", (0, 1, 2, 4, 4, 7, 2, 7)),
           "rasteirinha": ("e_rasteira", (0, 0, 3, 4, 4, 3, 5, 7)), "bicicleta": ("e_ar_soco", None),
           "compasso": ("e_martelo", None), "armada": ("e_martelo", None), "lata": ("e_provoca", None),
           "bone_voador": ("e_juliet_voadora", None), "e_beck": ("e_beck", None)}


def arquivo_ratao(pasta, n):
    folha, ordem = E_FOLHA.get(pasta, (f"e_{pasta}", None))
    return QUADROS / folha / f"{ordem[n] if ordem else n:02d}.png"


gp.arquivo_endiabrado_da_chave = arquivo_ratao
gp.pasta_endiabrada = lambda pasta: (E_FOLHA.get(pasta, (f"e_{pasta}", None))[0], 1)
# as 8 poses de reserva do Ratão (sprite antigo sem folha): parado, andando, agachado, soco, chute, por cima,
# especial e pulo (a ordem de gp.POSES_ENDIABRADO)
POSES_RATAO = (("e_referencia_ginga", 0), ("e_anda", 2), ("e_agachado", 6), ("e_soco", 5), ("e_chute_alto", 4),
               ("e_cabecada", 4), ("e_bola", 4), ("e_pulo", 3))
# Lote 7: o preset_despertado do kit lê a pose de reserva por POSE_BOSS (folha normal, desenho) e arquivo_ratao
gp.POSE_BOSS = {i: (folha[2:], d) for i, (folha, d) in enumerate(POSES_RATAO)}


def carregar_poses():
    """As 9 poses que o gerador comum espera, cada uma de um desenho das folhas do CK."""
    d = lambda pasta, i: abrir_quadro(QUADROS / pasta / f"{i:02d}.png")
    p = {"parado": d("referencia_ginga", 0), "andando": d("anda", 2), "andando2": d("anda", 6),
         "defesa": d("defesa", 3), "apanhando": d("apanha", 3), "agachado": d("agachado", 6), "pulo": d("pulo", 3),
         "soco": d("soco", 5), "chute": d("chute_alto", 4), "rasteira": d("rasteira", 4), "especial": d("bola", 4)}
    return p, Itens.lata()


class Itens:
    """No lugar do itens_pengaro: o CK não segura garrafa na base e os projéteis dele vêm de sprites/ck/efeitos."""

    @staticmethod
    def lata():
        return Image.open(EFEITOS / "bone/00.png").convert("RGBA")

    @staticmethod
    def garrafa():
        return Image.open(EFEITOS / "garrafa/00.png").convert("RGBA")

    @staticmethod
    def latas_girando(escala=2):
        return [Image.open(EFEITOS / f"garrafa/{i:02d}.png").convert("RGBA") for i in (1, 2, 3, 4)]

    @staticmethod
    def com_whisky(img):
        return img


gp.itens_pengaro = Itens
gp.carregar_poses = carregar_poses

# Os desenhos que a vítima de um arremesso empresta (ações 5001 e 5030) têm número fixo em gp.SPRITES_VITIMA. Com a
# mesma ordem de FOLHAS do kit os do CK caem em 382, 384-386 e 49, os mesmos do Gutto e do Raiclaven (main confere).


# ================================================================ medidas tiradas do desenho
def _alfa(folha, d, ratao=False):
    arquivo = arquivo_ratao(folha, d) if ratao else QUADROS / folha / f"{d:02d}.png"
    return np.asarray(abrir_quadro(arquivo))[..., 3] > 0


def alcance(folha, d, y1=-200, y2=0, ratao=False):
    """x do pixel mais à frente do desenho (em relação ao eixo), na faixa de altura dada."""
    a = _alfa(folha, d, ratao)[max(0, EY + y1):EY + y2 + 1]
    xs = np.flatnonzero(a.any(axis=0))
    return int(xs[-1]) - EX if len(xs) else 0


def caixa(folha, d, x0=10, ratao=False):
    """Caixa de golpe em volta do membro esticado: do que passa de 24 px à frente do eixo (o corpo em guarda vai até
    23), o pedaço que chega mais longe (o pé da frente, plantado, é outro pedaço), com 3 px de folga em cima e
    embaixo e 4 à frente. Se nada passa de 24, tenta com 16. ratao=True mede no desenho do Modo Ratão."""
    import cv2
    a = _alfa(folha, d, ratao)
    for lim in (24, 16):
        n, _, st, _ = cv2.connectedComponentsWithStats(a[:, EX + lim:].astype(np.uint8), connectivity=8)
        pedacos = [st[k] for k in range(1, n) if st[k][cv2.CC_STAT_AREA] >= 6]
        if pedacos:
            x, y, w, h, _ = max(pedacos, key=lambda p: (p[0] + p[2], p[4]))
            y1, y2 = int(y) - EY - 3, min(-2, int(y + h - 1) - EY + 4)
            if y2 - y1 < 16:
                y1 -= (16 - (y2 - y1)) // 2
                y2 = min(-2, y1 + 16)
            return (x0, y1, lim + int(x + w - 1) + 4, y2)
    raise SystemExit(f"caixa: {folha} {d} não tem membro à frente")


SOBRA = gp.SOBRA_CLSN1
ALVO_SEGUE = 80   # caixa + passo dos golpes que emendam (o oponente já foi empurrado pelo golpe anterior)


def com_passo(m, alvo=ALVO_SEGUE, teto=6.5, ratao=False):
    """O CK é de luta curta: o braço dele vai uns 40 px à frente, contra 70 do Pengaró. Para a corrente encaixar ele
    entra com um passo junto do golpe (boxe: pé e mão juntos): o avanço cobre a distância que falta até `alvo`."""
    ini, _ = gp.inicios_extra(m)
    trechos = gp._trechos_ativos(m)
    if not trechos or m.avanco < 0:
        return m
    a, b = trechos[0][0], trechos[-1][1]
    folha, d = m.quadros[a][:2]
    comeco = max(1, ini[a] - 3)
    fim = ini[b] if b < len(ini) else ini[-1]
    falta = alvo - (min(alcance(folha, d, m.caixa[1], m.caixa[3], ratao) + SOBRA, m.caixa[2]))
    return replace(m, avanco=round(max(m.avanco, min(teto, falta / max(1, fim - comeco))), 2))


# ================================================================ golpes (docs/fichas/ck.md)
def _c(folha, d, **k):
    return caixa(folha, d, **k)


def _e(folha, d, padrao=None):
    """Caixa medida no desenho do Ratão que o RemapPreset põe no lugar de (folha, d)."""
    try:
        return caixa(folha, d, ratao=True)
    except SystemExit:
        if padrao is None:
            raise
        return padrao


def ratao(m, alvo=ALVO_SEGUE):
    return com_passo(m, alvo, ratao=True)


SOCO_J, SOCO_C = _c("soco", 2), _c("soco", 5)          # jab e cruzado
CX_GANCHO = (8, -102, 34, -70)                         # gancho: a luva gira junto do corpo
CX_UPPER = (2, -132, 38, -60)                          # uppercut: a luva sobe acima da cabeça, junto do corpo
gp.extra.CORRENTES = tuple(com_passo(m) for m in (
    # x: jab, jab duplo, cruzado, Uno-Dos de Rua
    N(301, "Jab Duplo", "soco 1/2 2/2A 3/2 2/2A 3/4 7/4", SOCO_J, (18, 20)),
    N(302, "Cruzado", "soco 3/3 4/3 5/3A 5/2A 6/5 7/5", SOCO_C, 45),
    N(303, "Uno-Dos de Rua", "soco 1/3 2/3A 3/2 4/2 5/3A 5/3A 6/8 7/8", SOCO_C, (35, 55),
      queda=True, final=True, avanco=3.0, vel="-4,-5", ar="-3,-6"),
    # y: direto, gancho de esquerda, gancho no fígado, Levanta, Comédia (uppercut que lança)
    N(311, "Gancho de Esquerda", "golaco 1/4 2/3 3/4A 3/3A 1/6 0/5", CX_GANCHO, 60),
    N(312, "Gancho no Fígado", "golaco 1/4 4/3 5/4A 5/3A 1/6 0/6", (8, -84, 26, -48), 70),
    N(313, "Levanta, Comédia", "cabecada 1/4 2/4 3/3 4/3A 5/3A 6/8 7/8", CX_UPPER, 110,
      queda=True, final=True, avanco=3.0, vel="-2,-8", ar="-2,-9"),
    # a: bicuda na canela, chute baixo de rua, joelhada na coxa, Bicuda de Pedreiro
    N(321, "Chute Baixo de Rua", "chute_baixo 1/3 2/2 3/3A 4/2A 5/4 6/4 7/4", _c("chute_baixo", 4), 35),
    N(322, "Joelhada na Coxa", "chute_alto 0/3 1/3 2/3A 2/3A 6/5 7/5", (4, -74, 18, -34), 40),
    N(323, "Bicuda de Pedreiro", "chute_alto 1/3 2/3 3/3A 4/3A 5/5 6/6 7/6", _c("chute_alto", 4), 85,
      queda=True, final=True, vel="-7,-4", ar="-5,-5"),
    # b: chute frontal, chute alto de rua, pisão na coxa, Voadora da Esquina
    N(331, "Chute Alto de Rua", "afastar 2/4 3/4 4/4A 4/3A 5/6 6/6 7/6", _c("afastar", 4), 60),
    N(332, "Pisão na Coxa", "chute_baixo 1/4 2/4 3/4A 4/3A 5/6 6/6 7/6", _c("chute_baixo", 4), 70),
    N(333, "Voadora da Esquina", "bicicleta 1/4 2/4 3/3A 4/3A 5/6 6/6 7/6", (4, -84, 30, -30), 110,
      queda=True, final=True, avanco=3.0, vel="-6,-4", ar="-5,-5"),
))
gp.extra.KOMBOS = tuple(com_passo(m) for m in (
    # Bom Dia, Cumpadi: → + y (overhand, o 216), x, b
    N(340, "Bom Dia: jab", "soco 1/3 2/3A 2/2A 3/4 7/4", SOCO_J, 40),
    N(341, "Bom Dia: chute frontal", "chute_alto 1/4 2/4 3/4A 4/3A 5/6 6/6 7/6", _c("chute_alto", 4), 80),
    # Sobe e Desce: x, ↓ + a (baixo), y (por cima)
    N(342, "Sobe e Desce: ponta do pé", "rasteirinha 1/3 2/3 3/3A 4/3A 5/4 6/5 7/5", _c("rasteirinha", 4), 35,
      guarda="L", chao="Low", area="BAIXO"),
    N(343, "Sobe e Desce: overhand", "martelo 1/5 2/4 3/4A 4/3A 5/6 6/6 7/6", _c("martelo", 4), 70, guarda="HA",
      queda=True, vel="-4,-4", ar="-3,-5"),
    # Encosta na Parede: ← + x (o 201), y, → + b
    N(344, "Encosta: direto", "soco 3/4 4/3 5/3A 5/3A 6/5 7/5", SOCO_C, 55, avanco=1.8),
    N(345, "Encosta: empurrão de sola", "afastar 2/4 3/4 4/4A 4/3A 5/6 6/6 7/6", _c("afastar", 4), 65, vel="-9"),
    # Sobe pro Teto: x, y, ↓ + y
    N(346, "Sobe pro Teto: direto", "soco 3/3 4/3 5/4A 5/3A 6/5 7/5", SOCO_C, 55),
    N(347, "Sobe pro Teto: uppercut", "cabecada 1/4 2/4 3/3 4/3A 5/3A 6/8 7/8", CX_UPPER, 70,
      queda=True, vel="-2,-4", ar="-2,-9", final=True),
))
# ---- Modo Ratão (os desenhos são os da base; o RemapPreset troca cada um pelo e_ equivalente)
# As caixas destes golpes são medidas no desenho do Ratão (a chinelada alta bate na altura da cabeça, a da base na
# barriga) e o gp.ajustar_clsn1 não mexe nelas (RATAO_SO): ele limitaria a caixa ao membro do desenho da base.
E_SOCO_J, E_SOCO_C, E_CHUTE = _e("soco", 2), _e("soco", 5), _e("chute_alto", 4)
E_UPPER = (2, -136, 44, -60)
gp.extra.DESPERTO_KOMBO = (  # Fim de Baile: x, → + y (o 3431), b
    ratao(N(349, "Fim de Baile: chinelada alta", "chute_alto 1/4 2/4 3/4A 4/4A 5/5 6/6 7/6", E_CHUTE, 80,
            queda=True, vel="-5,-4", ar="-4,-5")),
)
gp.extra.DESPERTO_CORRENTES = (
    ratao(N(3410, "Corte de Lado", "soco 1/4 2/3A 2/3A 3/5 7/5", E_SOCO_J, 55), alvo=56),
    ratao(N(3411, "Corte de Volta", "soco 2/3 3/3A 3/3A 4/5 7/5", _e("soco", 3, (10, -100, 34, -66)), 60)),
    ratao(N(3412, "Estocada", "soco 3/4 4/3 5/3A 5/3A 6/6 7/6", E_SOCO_C, 70)),
    ratao(N(3413, "Caco no Peito", "cabecada 1/4 2/4 3/3 4/3A 5/3A 6/8 7/8", E_UPPER, 120,
            queda=True, final=True, avanco=2.2, vel="-3,-8", ar="-3,-9")),
    ratao(N(3420, "Chinelada Alta", "chute_alto 1/4 2/3 3/3A 4/3A 5/5 6/5 7/5", E_CHUTE, 60), alvo=56),
    ratao(N(3421, "Chute de Meia", "chute_baixo 1/4 2/3 3/3A 4/3A 5/5 6/5 7/5", _e("chute_baixo", 4), 70)),
    ratao(N(3422, "Rasteira de Baile", "rasteira 1/4 2/4 3/3A 4/3A 5/6 6/6 7/6", _e("rasteira", 4), 75,
            guarda="L", chao="Low")),
    ratao(N(3423, "Passinho do Baile", "caneta 1/5 2/5 3/4A 4/4A 5/8 6/8 7/8", _e("caneta", 4), 125,
            queda=True, final=True, avanco=2.0, vel="-6,-4", ar="-5,-5")),
)
gp.extra.DESPERTO_NORMAIS = (
    ratao(N(3430, "Garrafa Subindo", "cabecada 1/4 2/4 3/3 4/3A 5/3A 6/7 7/7", E_UPPER, 95,
            tipo_st="C", area="BAIXO", queda=True, vel="-2,-4", ar="-2,-10"), alvo=46),
    ratao(N(3431, "Garrafada por Cima", "martelo 1/5 2/4 3/3A 4/3A 5/6 6/6 7/6", _e("martelo", 4), 85,
            guarda="HA"), alvo=62),
    ratao(N(3432, "Chinelada de Passo", "chute_baixo 1/6 2/5 3/4A 4/3A 5/7 6/7 7/7", _e("chute_baixo", 4), 100),
          alvo=74),
    # assopro: a caixa é a fumaça na frente da boca (ele sopra curvado para a frente), não um membro
    N(3433, "Assopro na Cara", "e_beck 1/4 2/4 3/4 4/3A 5/3A 6/6 7/6", (14, -96, 62, -58), 20, avanco=1.5),
    ratao(N(3434, "Chute de Recuo", "chute_baixo 1/4 2/3 3/3A 4/3A 5/5 6/5 7/5", _e("chute_baixo", 4), 70,
            queda=True, vel="-3,-3", ar="-3,-4"), alvo=62),
    ratao(N(3435, "Rasteira Chapada", "rasteira 1/6 2/5 3/3A 4/4A 5/6 6/8 7/8", _e("rasteira", 4), 100,
            tipo_st="C", attr="C, NA", guarda="L", chao="Trip", queda=True, area="BAIXO", vel="-3,-2",
            ar="-3,-2"), alvo=64),
)
gp.extra.DESPERTO_ESPECIAL = (
    N(3401, "Passinho Ratão", "caneta 1/5 2/4 3/3A 4/4A 3/2 4/4A 5/6 6/8 7/8", _e("caneta", 4), (45, 70),
      attr="S, SA", queda=True, avanco=5.0, final=True, vel="-6,-4", ar="-5,-5"),
)
RATAO_SO = {m.estado for m in gp.extra.DESPERTO_KOMBO + gp.extra.DESPERTO_CORRENTES + gp.extra.DESPERTO_NORMAIS
            + gp.extra.DESPERTO_ESPECIAL} | {3436}
# Golpes da base que no Ratão trocam de desenho: a variante despertada (ação 1xxxx) leva a caixa medida no desenho
# do Ratão. estado -> caixa
gp.CAIXA_DESPERTADA = {
    200: E_SOCO_J, 210: E_SOCO_C, 215: E_SOCO_C, 230: _e("chute_baixo", 4), 240: E_CHUTE, 245: E_CHUTE,
    260: _e("afastar", 4), 410: E_UPPER, 430: _e("rasteirinha", 4), 440: _e("rasteira", 4),
    216: _e("martelo", 4), 246: _e("afastar", 5), 201: _e("compasso", 4), 231: _e("chute_baixo", 4),
    1400: _e("caneta", 4), 1401: _e("caneta", 4), 1500: _e("rasteirinha", 4), 1501: _e("rasteirinha", 4),
    1200: (0, -138, 44, -40), 1201: (0, -138, 50, -40),
}
def _caixa_ratao(m):
    """Caixa do golpe medida no desenho do Ratão que entra no lugar do desenho de contato (se não houver membro à
    frente, fica a da base)."""
    a = gp._trechos_ativos(m)[0][1] - 1  # o último desenho do 1º trecho ativo é o do contato (a pose segurada)
    folha, d = m.quadros[a][:2]
    return _e(folha, d, m.caixa)


# correntes e kombos da base também saem no Ratão (y, b e os kombos): ganham a variante 1xxxx com a caixa do Ratão
for _m in gp.extra.CORRENTES + gp.extra.KOMBOS:
    if _m.estado != 322:  # joelhada: a caixa é o joelho, igual nas duas formas
        gp.ATAQUES_DESPERTADOS.add(_m.estado)
        gp.CAIXA_DESPERTADA[_m.estado] = _caixa_ratao(_m)
gp.CAIXA_DESPERTADA[313] = gp.CAIXA_DESPERTADA[347] = E_UPPER  # a garrafa sobe acima da cabeça, junto do corpo
gp.CAIXA_DESPERTADA[400] = (10, -54, 46, -36)                  # estocada rente ao chão (e_golaco 3): a garrafa
gp.ATAQUES_DESPERTADOS.add(1701)
gp.CAIXA_DESPERTADA[1701] = _e("golaco", 3)
# supers de soco: no Ratão são estocadas (e_golaco 2, 4 e 7); a caixa cobre as três alturas
_est = [_e("golaco", d) for d in (2, 3, 5)]
CX_ESTOCADAS = (10, min(c[1] for c in _est), max(c[2] for c in _est), max(c[3] for c in _est))
gp.CAIXA_DESPERTADA[3000] = gp.CAIXA_DESPERTADA[3200] = CX_ESTOCADAS
# Fim da Rajada no Ratão (13000): na base é a voadora (bicicleta 2-4) e a aterrissagem (pulo 6-7); no Ratão esses
# desenhos viravam e_ar_soco e e_pulo, poses de pulo encolhido num golpe que não sai do chão, e a caixa ficava acima
# do desenho (32 px dentro). No Ratão o fim é o chute alto em pé da e_chute_alto (3 arma, 4 estica, 5 recolhe, 6-7
# guarda), com a caixa no pé esticado. Mesmos tempos e o mesmo número de elementos: o .cns conta por Time.
FIM_RAJADA_RATAO = {"f_bicicleta2": "f_chute_alto3", "f_bicicleta3": "f_chute_alto4", "f_bicicleta4": "f_chute_alto5",
                    "f_pulo6": "f_chute_alto6", "f_pulo7": "f_chute_alto7"}
_acao_do_kit = gp.Air.acao


def _acao(self, numero, quadros, *resto, **k):
    if numero == 13000:
        novos = []
        for nome, ticks, *cx in quadros:
            novo = FIM_RAJADA_RATAO.get(nome, nome)
            if novo == "f_chute_alto4" and cx and cx[0]:
                cx = [E_CHUTE, *cx[1:]]
            novos.append((novo, ticks, *cx))
        assert sum(n != q[0] for (n, *_), q in zip(novos, quadros)) == 6, "fim da Rajada mudou no kit"
        quadros = novos
    return _acao_do_kit(self, numero, quadros, *resto, **k)


gp.Air.acao = _acao
gp.extra.TODOS = (gp.extra.CORRENTES + gp.extra.KOMBOS + gp.extra.DESPERTO_KOMBO + gp.extra.DESPERTO_CORRENTES
                  + gp.extra.DESPERTO_NORMAIS + gp.extra.DESPERTO_ESPECIAL)

# ---- golpes com lógica própria: aqui só a animação (os tempos saem de gp.inicios_extra)
CX_RAJADA = (6, -100, 44, -60)    # Rajada e Nocaute: a luva dos ganchos (do ombro ao fígado), não o corpo todo
CX_GUARDA = (-8, -105, 30, -12)   # Contragolpe: o corpo inteiro é a caixa que apara (como o parry 760)
CX_GRAVE = (-10, -110, 110, 0)    # Grave do Paredão: a onda do grave, não um membro
M = {m.estado: m for m in (
    N(1000, "Tragada (perto)", "bola 1/3 2/5 3/4 4/5 5/5 7/10", (0, 0, 0, 0), []),
    N(1001, "Tragada (longe)", "bola 1/3 2/5 3/4 4/5 5/5 7/13", (0, 0, 0, 0), []),
    N(1600, "Boné Voador fraco", "bone_voador 1/5 2/6 3/4 4/5 6/6 6/-1", (0, 0, 0, 0), []),
    N(1601, "Boné Voador forte", "bone_voador 1/5 2/6 3/4 4/5 6/6 6/-1", (0, 0, 0, 0), []),
    N(1602, "Boné de volta", "bone_voador 2/2 1/2 0/2", (0, 0, 0, 0), []),
    # Gingado de Esquiva: abaixa, passa por baixo (o jogo vira o lutador no desenho 3) e sobe. Depois de virar não
    # entram os desenhos 4 a 6 da folha, que já estão desenhados de costas.
    N(1700, "Gingado de Esquiva", "rolamento 1/3 2/3 3/3 3/3 2/4 1/5 7/8", (0, 0, 0, 0), []),
    N(1701, "Gingado de Esquiva e gancho", "rolamento 1/3 2/3 3/3 3/3 2/3 golaco 2/3 3/3A 3/3A 1/5 rolamento 7/8",
      CX_GANCHO, [70]),
    N(1300, "Contragolpe", "armada 1/4 2/16A 0/6", CX_GUARDA, []),
    N(1301, "Contragolpe (pega baixo)", "armada 1/4 2/20A 0/6", CX_GUARDA, []),
    N(1310, "Contragolpe: cruzado", "armada 3/3 4/2 5/6A 6/8 7/8", _c("armada", 5), [110], attr="S, SA", queda=True,
      vel="-6,-5", ar="-5,-5"),
    N(1100, "Pêndulo", "rolamento 1/4 2/5 1/5 2/5 1/5 0/6", (0, 0, 0, 0), []),
    N(1101, "Pêndulo longo", "rolamento 1/4 2/5 1/5 2/5 1/5 2/5 1/5 0/6", (0, 0, 0, 0), []),
    N(1110, "Pêndulo: direto", "soco 4/3 5/4A 6/6 7/6", SOCO_C, [80], attr="S, SA"),
    N(3000, "Rajada da Esquina",
      "golaco 1/6 2/3A 3/3A 4/3A 5/3A 2/3A 3/3A 6/4A bicicleta 2/3 3/4A 4/5 pulo 6/4 7/6", CX_RAJADA, []),
    N(3400, "Tragada de Beck", "e_beck 1/4 2/5 3/5 4/6 5/6 6/6 7/6", (0, 0, 0, 0), []),
    N(3402, "Garrafa Voadora", "bola 1/5 2/6 3/4 4/5 5/6 7/22", (0, 0, 0, 0), []),
    N(3403, "Grave do Paredão", "chute_baixo 1/5 2/5 3/6A 5/8 7/10", CX_GRAVE, [30]),
    N(840, "Abaixa Aí", "agarrao 1/3A 2/4 3/4 4/4", (10, -60, 44, -10), []),
    N(841, "Abaixa Aí: joelhada", "agachado 2/3 3/3 chute_alto 0/4 1/4 2/5 2/4 6/4 7/5", (0, 0, 0, 0), [],
      area="BAIXO"),
)}
M[1110] = com_passo(M[1110], alvo=70)
M[1310] = com_passo(M[1310], alvo=90)
gp.extra.ESPECIAIS_A_MAO = tuple(M.values())
gp.SEM_RASTRO = gp.SEM_RASTRO | {1300, 1301, 3000}
SEM_AJUSTE = {1300, 1301, 3403} | RATAO_SO  # caixa que não é membro, ou medida no Ratão: fica como está

# Saideira (← → + y): abraça de lado, tapa na nuca (índice 5, 60 de dano) e bicuda (índice 10, 90). Sem folha própria:
# pegada do agarrão, overhand curto e bicuda.
gp.AGARRAO_WHISKY = [("agarrao", 1, 3), ("agarrao", 2, 3),
                     ("martelo", 1, 4), ("martelo", 2, 4), ("martelo", 3, 4), ("martelo", 4, 2), ("martelo", 5, 3),
                     ("martelo", 6, 4), ("martelo", 7, 4),
                     ("chute_baixo", 2, 5), ("chute_baixo", 3, 4), ("chute_baixo", 4, 4), ("chute_baixo", 5, 4),
                     ("chute_baixo", 7, 4)]
_cns_agarrao = gp.cns_agarrao_whisky


def cns_saideira():
    texto = _cns_agarrao()  # sem a garrafa do Pengaró caindo
    texto = texto[:texto.index("[State 831, Garrafa]")] + texto[texto.index("[State 831, Whisky dano]"):]
    # rótulos do kit com o golpe do CK (ficha: tapa na nuca e bicuda); só nomes, o motor não lê
    return texto.replace("[State 831, Capoeira ", "[State 831, Tapa na nuca: ").replace(
        "[State 831, Whisky ", "[State 831, Bicuda: ")


gp.cns_agarrao_whisky = cns_saideira
_cns_especiais = gp.cns_especiais_extra


def cns_especiais_ck():
    """O gerador comum monta o 3402 do Pengaró (atravessa batendo) e pede um desenho com caixa; o do CK é um
    arremesso, sem caixa, e o estado é trocado inteiro em cns_ck. Só para essa passagem o 3402 leva uma caixa."""
    reais = gp.extra.ESPECIAIS_A_MAO
    gp.extra.ESPECIAIS_A_MAO = tuple(
        replace(m, quadros=tuple((fl, d, t, k == 2) for k, (fl, d, t, _) in enumerate(m.quadros)))
        if m.estado == 3402 else m for m in reais)
    try:
        return _cns_especiais()
    finally:
        gp.extra.ESPECIAIS_A_MAO = reais


gp.cns_especiais_extra = cns_especiais_ck

# ---- repertório: direcionais, no ar, Bote, Bicuda Baixa e o super de 2 estoques (mesmos estados e comandos do kit)
P3 = ("a", "b", "c")  # só a quantidade de poses importa: os desenhos estão em FOLHA_DO_GOLPE
FOLHA_DO_GOLPE = {
    216: (("martelo", 2), ("martelo", 4), ("martelo", 6)),        # → + y overhand por cima
    246: (("afastar", 3), ("afastar", 5), ("afastar", 7)),        # → + b pisão de rua
    201: (("compasso", 2), ("compasso", 4), ("compasso", 6)),     # ← + x tapa de luva (costas da mão)
    231: (("chute_baixo", 2), ("chute_baixo", 4), ("chute_baixo", 6)),  # ← + a chute de calcanhar
    601: (("ar_soco", 1), ("ar_soco", 4), ("ar_soco", 6)),        # ar y cotovelada
    611: (("bicicleta", 1), ("bicicleta", 4), ("bicicleta", 6)),  # ar b chute duplo
    1400: (("caneta", 2), ("caneta", 4), ("caneta", 6)), 1401: (("caneta", 2), ("caneta", 4), ("caneta", 6)),
    1500: (("rasteirinha", 2), ("rasteirinha", 4), ("rasteirinha", 6)),
    1501: (("rasteirinha", 2), ("rasteirinha", 4), ("rasteirinha", 6)),
    # Nocaute de Rua: ajeita, jab, gancho e o cruzado de nocaute
    3200: (("armada", 2), ("golaco", 2), ("golaco", 3), ("armada", 5), ("armada", 6)),
}
CX_AR = (4, -74, 34, -14)
NORMAIS_CK = (
    Golpe(216, "Overhand por Cima", "/F, y", P3, (8, 3, 14), _c("martelo", 4), 76, guarda="HA", avanco=2.5),
    Golpe(246, "Pisão de Rua", "/F, b", P3, (17, 4, 20), _c("afastar", 5), 90, avanco=2.5),
    Golpe(201, "Tapa de Luva", "/B, x", P3, (6, 3, 12), _c("compasso", 4), 47, avanco=2.0),
    Golpe(231, "Chute de Calcanhar", "/B, a", P3, (8, 3, 14), _c("chute_baixo", 4), 57, avanco=1.0),
    Golpe(601, "Cotovelada no Ar", "y", P3, (7, 5, -1), CX_AR, 79, "A", "HA"),
    Golpe(611, "Chute Duplo", "b", P3, (9, 6, -1), (-20, -60, 34, -6), 88, "A", "HA"),
)
# (estado, nome, nome no Ratão, direção, botões, caixa, dano, avanço, guarda, o forte derruba)
# Bote: o desenho inteiro passa de 24 px do eixo (ele se joga), então a caixa medida pegava do boné ao chão; fica
# só a faixa do braço esticado
CX_BOTE = (10, _c("caneta", 4)[1] + 8, _c("caneta", 4)[2], _c("caneta", 4)[1] + 44)
FAMILIAS_CK = (
    (1400, "Bote", "Bote de Garrafa", "~D, F", "ab", CX_BOTE, 73, 8.0, "MA", True),
    (1500, "Bicuda Baixa", "Chinelada Rasteira", "~D, B", "ab", _c("rasteirinha", 4), 70, 5.5, "L", True),
)


def golpes_ck(hazaki=False):
    yield from NORMAIS_CK
    for n, nome, desperto, direcao, botoes, cx, dano, avanco, guarda, queda in FAMILIAS_CK:
        for i, botao in enumerate(botoes):
            yield Golpe(n + i, nome, f"{direcao}, {botao}", P3, (8 + i * 3, 4 + i * 2, 16 + i * 7), cx, dano + i * 22,
                        guarda=guarda, avanco=avanco * (1 + i * .35), queda=queda and i == 1, nome_desperto=desperto,
                        lancamento="-3,-3.5")
    yield Golpe(3200, "Nocaute de Rua", "~B, F, D, x", ("a",) * 5, (11, 5, 5, 6, 26), (6, -100, 46, -60), 345,
                avanco=4, queda=True, custo=2000, nome_desperto="Nocaute de Rua")


gp.golpes = golpes_ck

# Normais do kit (o CNS bate em `Time = N`): passo curto antes do contato, para a caixa chegar a 52 px do eixo (o
# robô e o jogo abrem a 28 px de corpo a corpo: a caixa do oponente começa a 40 px do eixo do CK).
# estado -> (folha, desenho do contato, tick do contato)
NORMAIS_DO_KIT = {200: ("soco", 2, 4), 210: ("soco", 5, 7), 215: ("soco", 5, 4), 230: ("chute_baixo", 4, 5),
                  240: ("chute_alto", 4, 9), 245: ("chute_alto", 4, 5), 260: ("afastar", 4, 12),
                  400: ("baixo_soco", 4, 4), 430: ("rasteirinha", 4, 5), 440: ("rasteira", 4, 10)}
ALVO_NORMAL = 52


# ================================================================ ações (.air)
_acoes_do_kit = gp.acoes_folhas


def acoes_ck(Q):
    """As ações do CK vêm antes das do kit (a primeira definição vale)."""
    f = lambda folha, i: f"f_{folha}{i}"
    CORPO, BAIXO, NO_AR, DEITADO, ROLANDO = gp.CORPO, gp.BAIXO, gp.NO_AR, gp.DEITADO, gp.ROLANDO
    # os golpes com lógica própria primeiro: o kit define 1100, 1200 e 1300 com os desenhos do Pengaró
    for m in gp.extra.ESPECIAIS_A_MAO:
        Q(m.estado, [(f(fl, d), n, m.caixa) if ativo else (f(fl, d), n) for fl, d, n, ativo in m.quadros],
          BAIXO if m.area == "BAIXO" else CORPO)
    # correr: o andar do CK em 3 ticks (o kit, no Lote 7, passou a ler a folha corre, que é só do Pengaró)
    Q(100, [(f"q_anda_fluida{i}", 3) for i in (0, 1, 2, 4, 5)])
    Q(105, [("recua", -1)], NO_AR)  # recuo: a pose de reserva de antes (o kit agora lê a folha recuo do Pengaró)
    # agachar: a folha desce nos desenhos 0 a 3 e fica embaixo balançando do 4 ao 7
    Q(10, [(f("agachado", 2), 2)], BAIXO)
    Q(11, [(f("agachado", i), 8) for i in (4, 5, 6, 7, 6, 5)], BAIXO)
    Q(12, [(f("agachado", 2), 2)], BAIXO)
    for n in (5020, 5021, 5022):  # apanhando agachado: encolhe atrás das luvas (não há folha própria)
        Q(n, [(f("agachado", 3), 4), (f("agachado", 4), 8)], BAIXO)
        Q(n + 5, [(f("agachado", 5), 8)], BAIXO)
    # queda (folha refeita, 8 figuras separadas): 4 de costas no ar, 5 bate no chão, 6 quica, 7 deitado. Mesmos
    # desenhos e tempos do Pengaró
    Q(5100, [(f("queda", 4), 3), (f("queda", 5), 3), (f("queda", 6), 3)], DEITADO)
    Q(5101, [(f("queda", 5), 3), (f("queda", 6), 3)], DEITADO)
    Q(5160, [(f("queda", 6), 6), (f("queda", 7), -1)], DEITADO)
    Q(5170, [(f("queda", 6), 6), (f("queda", 7), 10)], DEITADO)  # tem de acabar (ver gerar_hazaki.py)
    # rolar para trás: só abaixa e balança (os desenhos 4 a 6 do rolamento estão de costas)
    Q(705, [(f("rolamento", d), t) for d, t in ((1, 4), (2, 5), (3, 6), (3, 5), (2, 5), (1, 4), (0, 3))], ROLANDO)
    # entrada do round (190), no lugar da embaixadinha do kit: aquecimento de sombra
    Q(190, [(f("lata", i), 7) for i in range(8)] + [("q_ginga_fluida0", 6)])
    for n in (191, 192):
        Q(n, [(f("lata", i), 7) for i in (1, 2, 3, 4)])

    def normal(n, folha, des, tempos, cx, area=CORPO, ativos=(2, 3)):
        Q(n, [(f(folha, d), t, cx) if k in ativos else (f(folha, d), t)
              for k, (d, t) in enumerate(zip(des, tempos))], area)

    # mesmos tempos e a mesma quantidade de elementos do kit (o CNS bate em Time = N)
    normal(200, "soco", (0, 1, 1, 2, 2, 3, 7), (1, 1, 2, 1, 2, 3, 4), SOCO_J, ativos=(3, 4))
    normal(210, "soco", (3, 4, 5, 5, 6, 6, 7), (4, 3, 1, 3, 6, 5, 5), SOCO_C)
    normal(215, "soco", (3, 4, 5, 5, 6, 6, 7), (2, 2, 1, 2, 6, 4, 4), SOCO_C)
    normal(230, "chute_baixo", (1, 2, 3, 4, 5, 6, 7), (3, 2, 1, 2, 3, 3, 3), _c("chute_baixo", 4))
    normal(240, "chute_alto", (1, 2, 3, 4, 5, 6, 7), (5, 4, 1, 3, 2, 8, 8), _c("chute_alto", 4))
    normal(245, "chute_alto", (1, 2, 3, 4, 5, 6, 7), (3, 2, 1, 2, 6, 5, 5), _c("chute_alto", 4))
    normal(260, "afastar", (1, 2, 3, 4, 4, 5, 6, 7), (4, 4, 4, 1, 3, 8, 6, 6), _c("afastar", 4), ativos=(3, 4))
    normal(400, "baixo_soco", (1, 2, 3, 4, 4, 5, 6), (2, 1, 1, 1, 2, 4, 3), _c("baixo_soco", 4), BAIXO, (3, 4))
    normal(410, "cabecada", (1, 2, 3, 4, 5, 6, 7), (3, 3, 1, 4, 6, 6, 6), CX_UPPER, BAIXO)
    normal(430, "rasteirinha", (1, 2, 3, 4, 5, 6, 7), (3, 2, 1, 2, 4, 3, 3), _c("rasteirinha", 4), BAIXO)
    normal(440, "rasteira", (1, 2, 3, 4, 5, 6, 7), (5, 5, 1, 3, 8, 7, 7), _c("rasteira", 4), BAIXO)
    Q(600, [(f("ar_soco", 2), 2), (f("ar_soco", 3), 3), (f("ar_soco", 4), 8, CX_AR), (f("ar_soco", 6), -1)], NO_AR)
    Q(610, [(f("bicicleta", 1), 6), (f("bicicleta", 4), 10, (4, -64, 32, -24)), (f("bicicleta", 6), -1)], NO_AR)
    Q(650, [(f("bicicleta", 2), 3), (f("bicicleta", 3), 4), (f("bicicleta", 4), 6, (4, -70, 34, -16)),
            (f("bicicleta", 6), -1)], NO_AR)
    # Ratão: corte descendo (x no ar), estado novo
    Q(3436, [(f("ar_soco", 2), 2), (f("ar_soco", 3), 3), (f("ar_soco", 4), 10, (4, -78, 38, -10)),
             (f("ar_soco", 6), -1)], NO_AR)
    for g in golpes_ck():
        des = FOLHA_DO_GOLPE[g.estado]
        Q(g.estado, [(f(*d), t, g.caixa) if 0 < k < len(des) - 1 else (f(*d), t)
                     for k, (d, t) in enumerate(zip(des, g.tempo))], NO_AR if g.tipo == "A" else CORPO)
    # agarrões: a luva que pega é o desenho 1 da folha
    pega = (10, -90, 42, -50)
    Q(800, [(f("agarrao", 1), 3, pega)])
    Q(830, [(f("agarrao", 1), 3, pega), (f("agarrao", 2), 4), (f("agarrao", 3), 4), (f("agarrao", 0), 4)])
    # Levanta, Comédia (→ ↓ + x/y): o uppercut subindo
    for i in (0, 1):
        Q(1200 + i, [(f("cabecada", 2), 4), (f("cabecada", 4), 6, (0, -134, 40 + 6 * i, -40)), (f("cabecada", 5), 8),
                     (f("cabecada", 6), -1)], NO_AR)
    # Baile da Esquina (3100, só no Ratão): 8 cortes e o fecho, com os desenhos do super
    cx = (0, -112, 50, -10)
    Q(3100, [(f("golaco", 1), 4)] + [(f("golaco", d), 4, cx) for d in (2, 3, 4, 5, 2, 3, 6, 7)]
      + [(f("golaco", 7), 20)])
    # Despertar: dança, acende, a fumaça cobre tudo (4 desenhos com a cor certa da fumaça, de efeitos/despertar_fumaca,
    # no lugar de despertar_a 6-7 e despertar_b 0-1), sai de Ratão, pega a garrafa e quebra
    Q(2000, [(f("despertar_a", i), 7) for i in range(6)] + [("ck_dfum0", 7), ("ck_dfum1", 6), ("ck_dfum2", 7),
                                                            ("ck_dfum3", 7)]
      + [(f("despertar_b", i), 7) for i in range(2, 7)] + [(f("despertar_b", 7), 10)])
    # projéteis e efeitos do CK
    Q(1005, [(f"ck_fumaca{i}", 3) for i in range(3)] + [("ck_fumaca3", 6), ("ck_fumaca4", 6)],
      [(-26, -20, 26, 20)], loop=3)
    Q(1006, [(f"ck_fumaca{i}", 4) for i in (5, 6, 7)], [])
    Q(1606, [("ck_bone", 3), ("ck_bone", 3, None, "H")], [(-10, -6, 10, 6)])
    Q(1608, [("ck_juliet", 3), ("ck_juliet", 3, None, "H")], [(-10, -6, 10, 6)])
    Q(3010, [(f"ck_garrafa{i}", 3) for i in range(6)], [(-12, -12, 12, 12)])
    Q(3013, [("ck_caco6", 4), ("ck_caco7", 6)], [])
    Q(3014, [("ck_caco7", -1)], [(-22, -12, 22, 0)])
    Q(9250, [(f"ck_paredao{i}", 4) for i in range(8)], [])
    Q(9251, [("ck_pod", -1)], [])
    Q(9253, [(f"ck_fumaca{i}", 3) for i in range(2, 8)], [])
    _acoes_do_kit(Q)


gp.acoes_folhas = acoes_ck
gp.PROJETEIS = gp.PROJETEIS | {1606, 1608, 3013, 3014}


def efeitos_ck(s):
    """Sprites dos efeitos do CK (grupos 9300+, fora do RemapPreset do Ratão)."""
    def pasta(nome):
        return [Image.open(a).convert("RGBA") for a in sorted((EFEITOS / nome).glob("*.png"))]
    meio = lambda q: (q.width // 2, q.height // 2)
    chao = lambda q: (q.width // 2, q.height - 1)
    for i, q in enumerate(pasta("fumaca")):
        s.add(f"ck_fumaca{i}", q, 9300, i, meio(q))
    for i, q in enumerate(pasta("garrafa")):
        s.add(f"ck_garrafa{i}", q, 9301, i, meio(q))
        if i >= 6:
            s.add(f"ck_caco{i}", q, 9301, i + 4, chao(q))
    s.add("ck_bone", pasta("bone")[0], 9302, 0, meio(pasta("bone")[0]))
    s.add("ck_juliet", pasta("juliet")[0], 9302, 1, meio(pasta("juliet")[0]))
    for i, q in enumerate(pasta("paredao")):
        s.add(f"ck_paredao{i}", q, 9303, i, chao(q))
    pod = Image.open(RAIZ / "sprites/ck/quadros/itens/pod.png").convert("RGBA").resize((6, 14), Image.NEAREST)
    s.add("ck_pod", pod, 9304, 0, meio(pod))
    for i, q in enumerate(pasta("despertar_fumaca")):
        s.add(f"ck_dfum{i}", q, 9305, i, (EX, EY))


# ---- faíscas e aura: os desenhos de faísca são os do Pengaró repintados (branco seco na base, verde de vidro no
# Ratão). A aura do Modo Ratão é a do Blender (paredão de som de fumaça, grande: o Breno quer a aura
# monstruosa no Despertar, 2026-11-13), ligada por ferramentas/aura_ck.py ([Statedef -4], Explods 9600 a 9602). A fumaça verde antiga (ck_aura, ação 9210) não nasce mais no jogo: os
# desenhos dela seguem carregados só porque entram na escolha da paleta do .sff (tirá-los mudaria as 255 cores e
# todos os pixels da forma base); a ação sai do .air e a poda os tira do .sff, como no Pengaró.
BRANCA = ((0, (40, 40, 50)), (.5, (190, 190, 200)), (1, (255, 255, 255)))
VIDRO = ((0, (8, 30, 12)), (.4, (40, 120, 50)), (.75, (120, 210, 110)), (1, (230, 255, 220)))
gp.CLARAO = {"whisky": ((255, 255, 255), (40, 40, 50)), "sombra": ((200, 255, 190), (8, 30, 12))}
gp.FX_PENGARO = {k: v for k, v in gp.FX_PENGARO.items() if k != 9211}
gp.FX_PENGARO[9210] = (None, "ck_aura", 5)
gp.CHAO = gp.CHAO | {"ck_aura"}
_quadros_proprios = gp.quadros_proprios
AURA_MONTE = 22  # linhas de baixo do desenho da aura (o monte de fumaça no chão), que não entram


def quadros_proprios(nome):
    if nome == "ck_aura":
        # o desenho tem um monte de fumaça no pé da coluna: opaco e preso ao lutador ele virava um arbusto em que o
        # CK pisava (e subia junto no pulo). Fica só a coluna, com a base desfeita em xadrez; o Explod é translúcido.
        qs = []
        for arq in sorted((EFEITOS / "aura").glob("*.png")):
            a = np.array(Image.open(arq).convert("RGBA"))
            a = a[:a.shape[0] - AURA_MONTE]
            yy, xx = np.mgrid[:a.shape[0], :a.shape[1]]
            a[(yy >= a.shape[0] - 8) & ((xx + yy) % 2 == 0), 3] = 0
            qs.append(Image.fromarray(a))
        return [(q, (q.width // 2, q.height - 1)) for q in qs]
    rampa = VIDRO if nome.startswith("sombra") else BRANCA if nome.startswith("whisky") else None
    return [(gp.pintar(q, rampa) if rampa else q, pivo) for q, pivo in _quadros_proprios(nome)]


gp.quadros_proprios = quadros_proprios


# ================================================================ estados próprios (.cns)
def ritmo(txt):
    """O mesmo ajuste que o montar_cns faz no fim: o atordoamento acompanha o RITMO dos golpes."""
    return re.sub(r"(?m)^((?:ground|guard|air)\.hittime = )(\d+)",
                  lambda m: f"{m[1]}{round(int(m[2]) * gp.RITMO)}", txt)


def trocar_estado(cns, n, novo):
    m = re.search(rf"\[Statedef {n}\]\n.*?(?=\[Statedef )", cns, re.S)
    assert m, f"estado {n} não encontrado"
    return cns[:m.start()] + novo + cns[m.end():]


def no_estado(cns, n, funcao):
    m = re.search(rf"\[Statedef {n}\]\n.*?(?=\[Statedef )", cns, re.S)
    assert m, f"estado {n} não encontrado"
    return cns[:m.start()] + funcao(m[0]) + cns[m.end():]


def antes_de(bloco, marca, novo):
    assert bloco.count(marca) >= 1, marca
    return bloco.replace(marca, novo + marca, 1)


def paredao(n, gatilho, dura, id_=9250):
    """O paredão de som atrás do lutador (Explod preso ao chão, atrás de tudo)."""
    return (f"[State {n}, Paredão]\ntype = Explod\ntrigger1 = {gatilho}\nanim = 9250\nid = {id_}\npostype = p1\n"
            f"pos = -46, 0\nremovetime = {dura}\nsprpriority = -3\nownpal = 1\nscale = 1, 1\n"
            "ignorehitpause = 1\nsupermovetime = -1\n\n")


def tremor(n, gatilho, tempo, ampl=-3):
    return f"[State {n}, Grave]\ntype = EnvShake\ntrigger1 = {gatilho}\ntime = {tempo}\nfreq = 90\nampl = {ampl}\n\n"


FAISCA = "\n".join


def nuvem(n, gatilho, id_, vel, mul, dura, escala, stun, dano=25, ofs="46, -90"):
    """Nuvem de fumaça: anda um pouco, para e fica no ar; quem encosta fica tonto (atordoamento longo, dano baixo)."""
    return (f"[State {n}, Nuvem]\ntype = Projectile\ntrigger1 = {gatilho}\nprojid = {id_}\nprojanim = 1005\n"
            "projhitanim = 1006\nprojremanim = 1006\nprojcancelanim = 1006\nprojhits = 1\nprojpriority = 1\n"
            f"projremovetime = {dura}\nprojscale = {escala}, {escala}\noffset = {ofs}\nvelocity = {vel}, 0\n"
            f"velmul = {mul}, 1\nattr = S, SP\ndamage = {dano}, 2\nanimtype = Light\nguardflag = MA\nhitflag = MAF\n"
            "pausetime = 0, 6\nsparkno = -1\nguard.sparkno = -1\nhitsound = F5,0\nguardsound = F6,0\n"
            f"ground.type = High\nground.slidetime = 10\nground.hittime = {stun}\nground.velocity = 0\n"
            "air.velocity = -1,-2\n\n")


def cns_ck(cns):
    E, fim, hitdef, ini = gp.estado, gp.fim, gp.hitdef, lambda n: gp.inicios_extra(M[n])[0]
    # ---- Tragada (↓ → + x/y): puxa o pod e solta a nuvem. x perto e pequena, y longe e maior
    # (a fraca nasce junto da boca e para a uns 70 px; a forte para a uns 175 px)
    for n, vel, mul, dura, escala in ((1000, 3.0, .9, 150, .75), (1001, 9, .93, 180, 1)):
        i = ini(n)
        cns = trocar_estado(cns, n, E(n, "S", "A", "S", anim=n, juggle=4)
                            + f"[State {n}, Pod]\ntype = Explod\ntrigger1 = Time = {i[0] + 2}\ntrigger1 = var(20) = 0\n"
                              f"anim = 9251\nid = 9251\npostype = p1\npos = 13, -93\nbindtime = -1\n"
                              f"removetime = {i[3] - i[0] - 2}\nsprpriority = 3\nownpal = 1\n\n"
                            + ritmo(nuvem(n, f"Time = {i[3]}", 1000, vel, mul, dura, escala, 30,
                                          ofs="40, -90" if n == 1000 else "46, -90")) + fim(n))
    # ---- Boné Voador (→ ← + x/y): sai da mão, vai e volta para a cabeça. No Ratão é o óculos (mesma lógica)
    for n, vel, freio in ((1600, 6.5, .36), (1601, 12, .26)):
        i = ini(n)
        solta, volta = i[3], round(2 * vel / freio)
        proj = "".join(
            f"[State {n}, {nome}]\ntype = Projectile\ntrigger1 = Time = {solta}\ntrigger1 = {forma}\nprojid = 1002\n"
            f"projanim = {anim}\nprojhitanim = -1\nprojremanim = -1\nprojhits = 2\nprojmisstime = 20\n"
            f"projpriority = 2\nprojremovetime = {volta}\noffset = 30, -84\nvelocity = {vel}, 0\naccel = -{freio}, 0\n"
            "attr = S, SP\ndamage = 45, 3\nanimtype = Med\nguardflag = MA\nhitflag = MAF\npausetime = 4, 8\n"
            f"sparkxy = 0, 0\n{FAISCA(gp.faiscas(9200))}\nsparkscale = 1, 1\nhitsound = F5,1\nguardsound = F6,0\n"
            "ground.type = High\nground.slidetime = 10\nground.hittime = 16\nground.velocity = -3\n"
            "air.velocity = -2,-3\n\n"
            for nome, forma, anim in (("Boné", "var(20) = 0", 1606), ("Óculos", "var(20) > 0", 1608)))
        cns = trocar_estado(cns, n, E(n, "S", "A", "S", anim=n, juggle=4) + ritmo(proj)
                            + f"[State {n}, Pega de volta]\ntype = ChangeAnim\ntrigger1 = Time > {solta + 4}\n"
                              "trigger1 = NumProjID(1002) = 0\ntrigger1 = Anim != 1602\nvalue = 1602\n\n"
                            + f"[State {n}, Fim]\ntype = ChangeState\ntrigger1 = Anim = 1602 && AnimTime = 0\n"
                              "value = 0\nctrl = 1\n\n")
    # ---- Levanta, Comédia forte: invencível até o fim do ativo
    velho = "trigger1 = Time < 5\nvalue = SCA"
    cns = no_estado(cns, 1201, lambda b: antes_de(b, velho, "").replace(velho, "trigger1 = Time < 13\nvalue = SCA"))
    # ---- Contragolpe (↓ ← + x/y): guarda baixa; se apanhar na janela, esquiva e responde com o cruzado (1310).
    # x apara golpe em pé e no ar; y apara também o agachado. Não apara projétil nem agarrão.
    for n, attr in ((1300, "SA, NA, SA, HA"), (1301, "SCA, NA, SA, HA")):
        i = ini(n)
        cns = trocar_estado(cns, n, E(n, "S", "A", "N", anim=n)
                            + gp.reversao(n, 1310, attr, f"Time = [{i[1]}, {i[2] - 1}]") + fim(n))
    cruzado = antes_de(gp.cns_novo(M[1310]), "[State 1310, Golpe]",
                       f"[State 1310, Esquiva]\ntype = NotHitBy\ntrigger1 = Time < {ini(1310)[2] + 4}\n"
                       "value = SCA\ntime = 1\n\n")
    cns = antes_de(cns, "[Statedef 1400]", ritmo(cruzado))
    # ---- Pêndulo (← ↓ + a/b): balança o tronco, invencível a golpe em pé e no ar (não a agachado, agarrão ou
    # projétil); x ou y no meio sai com o direto (1110). No Ratão a esquiva liga 3 ticks mais tarde.
    for n in (1100, 1101):
        balanca = ini(n)[-1]
        cns = trocar_estado(cns, n, E(n, "S", "I", "N", anim=n)
                            + f"[State {n}, Esquiva]\ntype = NotHitBy\n"
                              f"trigger1 = Time >= ifelse(var(20) > 0, 6, 3) && Time < {balanca}\n"
                              "value = SA, NA, SA, HA\ntime = 1\n\n"
                            + f"[State {n}, Sai com o direto]\ntype = ChangeState\ntriggerall = Time >= 6\n"
                              f"triggerall = Time < {balanca}\ntrigger1 = command = \"x\"\ntrigger2 = command = \"y\"\n"
                              "value = 1110\n\n" + fim(n))
    cns = antes_de(cns, "[Statedef 1200]", ritmo(gp.cns_novo(M[1110])))
    # ---- Rajada da Esquina (← → ↓ + a/b, 1 estoque): entra de pêndulo, 7 socos e fecha com a voadora
    i = ini(3000)
    socos = "".join(hitdef(3000, f"Time = {i[k]}", "S, HA", 22, tipo="Medium", hit=16, escorrega=4, vel="-1",
                           ar="-1,-3", pausa=(2, 6), pesado=True, classe="super", extra="getpower = 0, 0\n")
                    for k in range(1, 8))
    voadora = hitdef(3000, f"Time = {i[9]}", "S, HA", 70, tipo="Back", queda=True, recupera=False, vel="-7,-6",
                     ar="-7,-6", pausa=(14, 14), pesado=True, classe="super_final", extra="getpower = 0, 0\n")
    cns = trocar_estado(cns, 3000, E(3000, "S", "A", "S", anim=3000, juggle=0) + gp.superpausa(3000, "Time = 0")
                        + "[State 3000, Gasta]\ntype = PowerAdd\ntrigger1 = Time = 0\nvalue = -1000\n\n"
                        + f"[State 3000, Invencivel]\ntype = NotHitBy\ntrigger1 = Time < {i[1] + 2}\nvalue = SCA\n"
                          "time = 1\n\n"
                        + f"[State 3000, Entra]\ntype = PosAdd\ntrigger1 = Time = [1, {i[1] + 6}]\n"
                          "trigger1 = p2bodydist x > 6\nx = 5\n\n"
                        + f"[State 3000, Cola]\ntype = PosAdd\ntrigger1 = Time = [{i[1] + 7}, {i[10]}]\n"
                          "trigger1 = p2bodydist x > 4\nx = 1.5\n\n"
                        + ritmo(socos + voadora)
                        + "[State 3000, Clarão]\ntype = BGPalFX\n"
                          f"trigger1 = Time >= {i[9]} && MoveHit = 1\ntime = 4\nadd = 128, 128, 128\n"
                          "ignorehitpause = 1\n\n" + fim(3000))
    # ---- Nocaute de Rua (3200): invencível no preparo
    cns = no_estado(cns, 3200, lambda b: antes_de(
        b, "[State 3200, Golpe]", "[State 3200, Invencivel]\ntype = NotHitBy\ntrigger1 = Time < 11\nvalue = SCA\n"
                                  "time = 1\n\n"))

    # ---- Baile da Esquina (3100, super do Ratão): o grave treme a tela, ele entra cortando. O paredão que toca é o
    # da aura do Ratão (ferramentas/aura_ck.py, em surto no tique 1): a caixa preta (9250) por cima dele era corte seco
    # e dois paredões juntos (cético de 2026-11-12). A aura grande voltou a pedido do Breno (2026-11-13)
    def baile(b):
        velho = "[State 3100, Avança]\ntype = VelSet\ntrigger1 = Time = 4\nx = 2\n"
        assert velho in b
        b = b.replace(velho, velho.replace("x = 2", "x = 8"))
        return antes_de(b, "[State 3100, Avança]", tremor(3100, "Time = 4", 50))
    cns = no_estado(cns, 3100, baile)
    # ---- Despertar (2000): a caixa preta toca atrás dele enquanto ele dança; quando a fumaça cobre tudo
    # (aura_ck.FUMACA a aura_ck.RATAO) ela apaga e o paredão de fumaça da aura nasce no mesmo trecho, atrás da nuvem.
    # O removetime 112 fica só de garantia: ele conta na superpausa e venceria no tique 82 do estado.
    a0, a1 = aura_ck.FUMACA, aura_ck.RATAO
    some = (f"[State 2000, Paredão vira fumaça]\ntype = ModifyExplod\ntrigger1 = Time >= {a0} && Time < {a1}\n"
            f"id = 9250\ntrans = addalpha\nalpha = floor(255 * ({a1} - Time) / {a1 - a0}), "
            f"255 - floor(255 * ({a1} - Time) / {a1 - a0})\nignorehitpause = 1\n\n"
            f"[State 2000, Paredão sai]\ntype = RemoveExplod\ntrigger1 = Time >= {a1}\ntrigger1 = NumExplod(9250)\n"
            "id = 9250\nignorehitpause = 1\n\n")
    cns = no_estado(cns, 2000, lambda b: antes_de(b, "[State 2000, Liga]", paredao(2000, "Time = 0", 112) + some))
    # ---- entrada do round (191): o paredão toca atrás dele e some quando o round começa (no -2)
    cns = no_estado(cns, 191, lambda b: antes_de(b, "[State 191, Fim]", paredao(191, "Time = 0", -1, 9254)))
    # ---- Ratão: ↓ ↑ pode pegar o lutador no começo do pulo; o golpe sai do chão
    chao = lambda n: (f"[State {n}, No chão]\ntype = PosSet\ntrigger1 = Time = 0\ny = 0\n\n"
                      f"[State {n}, Parado]\ntype = VelSet\ntrigger1 = Time = 0\nx = 0\ny = 0\n\n")
    # Tragada de Beck (↓ ↑ + x/y): nuvem grande e lenta, tonteia mais
    i = ini(3400)
    cns = trocar_estado(cns, 3400, E(3400, "S", "A", "S", anim=3400, juggle=4) + chao(3400)
                        + ritmo(nuvem(3400, f"Time = {i[3]}", 1004, 1.6, .985, 200, 1.4, 44, dano=30, ofs="50, -84"))
                        + fim(3400))
    # Garrafa Voadora (↓ → + x/y): arco; estilhaça no chão e os cacos ficam um tempo (pegam por baixo)
    i = ini(3402)
    voo = 46
    garrafa = (f"[State 3402, Garrafa]\ntype = Projectile\ntrigger1 = Time = {i[3]}\nprojid = 1002\nprojanim = 3010\n"
               "projhitanim = 3013\nprojremanim = 3013\nprojhits = 1\nprojpriority = 2\noffset = 40, -100\n"
               "velocity = 3.6, -2.6\naccel = 0, .2\nprojheightbound = -400, 0\nattr = S, SP\ndamage = 75, 5\n"
               "animtype = Med\nguardflag = MA\nhitflag = MAF\npausetime = 4, 10\nsparkxy = 0, 0\n"
               f"{FAISCA(gp.faiscas(9200))}\nsparkscale = 1, 1\nhitsound = F5,1\nguardsound = F6,0\n"
               "ground.type = High\nground.slidetime = 12\nground.hittime = 18\nground.velocity = -4\n"
               "air.velocity = -2,-3.5\n\n"
               f"[State 3402, Cacos]\ntype = Projectile\ntrigger1 = Time = {i[3] + voo}\n"
               "trigger1 = NumProjID(1002) > 0\nprojid = 1003\nprojanim = 3014\nprojhitanim = 3014\n"
               "projremanim = -1\nprojhits = 1\nprojpriority = 1\nprojremovetime = 120\n"
               f"postype = p1\noffset = {40 + round(3.6 * voo)}, 0\nvelocity = 0, 0\nattr = S, SP\ndamage = 20, 2\n"
               "animtype = Light\nguardflag = L\nhitflag = MF\npausetime = 0, 6\nsparkno = -1\nguard.sparkno = -1\n"
               "hitsound = F5,0\nguardsound = F6,0\nground.type = Low\nground.slidetime = 6\nground.hittime = 14\n"
               "ground.velocity = -2\nair.velocity = -1,-2\n\n")
    cns = trocar_estado(cns, 3402, E(3402, "S", "A", "S", anim=3402, juggle=4) + ritmo(garrafa) + fim(3402))
    # Grave do Paredão (↓ ↑ + a/b): bate o pé, o paredão da aura incha no grave (surto) e o grave empurra para longe
    i = ini(3403)
    assert aura_ck.GRAVE == i[2], f"o surto do Grave (aura_ck.GRAVE = {aura_ck.GRAVE}) fora do grave (tique {i[2]})"
    cns = trocar_estado(cns, 3403, E(3403, "S", "A", "S", anim=3403, juggle=4) + chao(3403)
                        + "[State 3403, Invencivel]\ntype = NotHitBy\ntrigger1 = Time < 8\nvalue = SCA\ntime = 1\n\n"
                        + tremor(3403, f"Time = {i[2]}", 16, -4)
                        + ritmo(hitdef(3403, f"Time = {i[2]}", "S, SA", 30, tipo="Heavy", hit=18, escorrega=14,
                                       vel="-12", ar="-8,-4", pausa=(4, 10), pesado=True, classe="especial"))
                        + fim(3403))
    # Corte descendo (x no ar, só no Ratão): estado novo, no molde do 600
    cns = antes_de(cns, "[Statedef 700]", ritmo(gp.normal(3436, "A, NA", 80, "Time = 5", fis="A", tipo_st="A",
                                                          guarda="HA", tipo="Medium", hit=18, pesado=True,
                                                          classe="forte")))
    # ---- normais do kit: passo curto antes do contato (o braço do CK é mais curto que o do Pengaró)
    for n, (folha, d, tick) in NORMAIS_DO_KIT.items():
        cx = caixa(folha, d)
        falta = ALVO_NORMAL - (alcance(folha, d, cx[1], cx[3]) + SOBRA)
        if falta > 0:
            passo = -(-falta // min(3, tick - 1))
            cns = no_estado(cns, n, lambda b, n=n, passo=passo, tick=tick: antes_de(
                b, f"[State {n}, Golpe]", f"[State {n}, Passo]\ntype = PosAdd\n"
                                          f"trigger1 = Time = [{max(1, tick - 3)}, {tick - 1}]\nx = {passo}\n\n"))
    # ---- Statedef -2: paredão da entrada, jeito chapado do Ratão e o corte que sangra
    chapado = "(stateno = [3410, 3435]) && statetype != A"
    garrafa_corta = "((stateno = [3410, 3413]) || stateno = 3430 || stateno = 3431 || stateno = 3436)"
    extras = (
        "[State -2, Paredão some no começo do round]\ntype = RemoveExplod\ntrigger1 = roundstate = 2\n"
        "trigger1 = NumExplod(9254)\nid = 9254\n\n"
        # chapado: cada golpe do Ratão sai com o alcance e o tempo um pouco diferentes (sorteio pequeno)
        f"[State -2, Chapado: tempo]\ntype = VarSet\ntrigger1 = var(20) > 0 && Time = 0 && {chapado}\n"
        "var(40) = Random % 3\n\n"
        f"[State -2, Chapado: alcance]\ntype = PosAdd\ntrigger1 = var(20) > 0 && Time = 0 && {chapado}\n"
        "x = Random % 6\n\n"
        # corte de garrafa: o oponente perde 3 de vida a cada 15 ticks por 90 ticks (não mata)
        "[State -2, Zera o corte na intro]\ntype = VarSet\ntrigger1 = roundstate < 2\nvar(42) = 0\n\n"
        f"[State -2, Corte abre]\ntype = VarSet\ntrigger1 = var(20) > 0 && MoveHit = 1 && {garrafa_corta}\n"
        "var(42) = 90\n\n"
        "[State -2, Corte sangra]\ntype = LifeAdd\ntrigger1 = var(42) > 0 && (var(42) % 15) = 0 && NumEnemy > 0\n"
        "trigger1 = roundstate = 2\nvalue = -3\nkill = 0\nredirectid = enemynear,id\n\n"
        "[State -2, Corte fecha]\ntype = VarAdd\ntrigger1 = var(42) > 0\nvar(42) = -1\n\n")
    cns = antes_de(cns, "[State -2, Bônus de dano]", extras)
    # o tempo sorteado atrasa o contato dos golpes do Ratão em 0 a 2 ticks (a caixa fica ligada 4 ou mais)
    cns, k = re.subn(r"(\[State (34[1-3]\d), Golpe\]\ntype = HitDef\ntrigger1 = Time = )(\d+)",
                     lambda m: f"{m[1]}{m[3]} + var(40)", cns)
    assert k >= 14, k
    return cns


# ================================================================ comandos (.cmd)
def cmd_ck(cmd):
    def comando(nome, *movimentos, tempo=18):
        nonlocal cmd
        velho = re.compile(rf'(?:\[Command\]\nname = "{nome}"\ncommand = [^\n]*\n(?:time = \d+\n)?'
                           r'(?:buffer\.time = \d+\n)?\n)+')
        assert velho.search(cmd), nome
        cmd = velho.sub("".join(gp.comando(nome, mv, tempo) for mv in movimentos), cmd, count=1)

    def na_entrada(titulo, valor, funcao):
        nonlocal cmd
        velho = re.compile(rf"\[State -1, {re.escape(titulo)}\]\ntype = ChangeState\nvalue = {valor}\n(?:[^\n]+\n)+\n")
        assert len(velho.findall(cmd)) == 1, (titulo, valor)
        cmd = velho.sub(lambda m: funcao(m[0]), cmd, count=1)

    com = lambda cond: lambda b: b.replace("triggerall", f"triggerall = {cond}\ntriggerall", 1)
    # movimentos da ficha nos nomes de comando do kit
    comando("bola_fraca", "~D, F, x")          # Tragada
    comando("bola_forte", "~D, F, y")
    for b in "ab":
        comando(f"compasso_{b}", f"~B, D, {b}")  # Pêndulo
        comando(f"role_{b}", f"~B, F, {b}")      # Gingado de Esquiva
    comando("sombra_x", "~D, U, x", "~D, U, y")  # Tragada de Beck
    comando("sombra_y", "~F, B, a", "~F, B, b")  # Passinho Ratão
    comando("sombra_a", "~D, F, x", "~D, F, y")  # Garrafa Voadora
    comando("sombra_b", "~D, U, a", "~D, U, b")  # Grave do Paredão
    cmd = antes_de(cmd, '[Command]\nname = "parry"', gp.comando("baile", "~B, F, D, x+y", 24))
    # Tragada e Contragolpe só na base; Boné Voador vale nas duas formas (no Ratão é o óculos)
    na_entrada("Bola forte", 1001, com("var(20) = 0"))
    na_entrada("Bola fraca", 1000, com("var(20) = 0"))
    na_entrada("caneta", 1300, com("var(20) = 0"))
    na_entrada("caneta", 1301, com("var(20) = 0"))
    sem = lambda b: b.replace("triggerall = var(20) = 0\n", "")
    na_entrada("Garrafada forte", 1601, sem)
    na_entrada("Garrafada fraca", 1600, sem)
    # ↓ ↑: o ↑ faz pular; a entrada vale também no pré-pulo e nos 7 primeiros ticks do pulo
    pulo = lambda b: b.replace("triggerall = statetype != A\n",
                               "triggerall = statetype != A || (stateno = 50 && Time < 8)\n").rstrip("\n") + \
        "\ntrigger2 = stateno = 40\n\n"
    na_entrada("Mao de Sombra", 3400, pulo)
    na_entrada("Queda Escura", 3403, pulo)
    na_entrada("Sombra Atravessada", 3402, lambda b: b.replace("triggerall = p2dist x > 0\n", ""))
    # Baile da Esquina: só no Ratão, com ← → ↓ + x+y (e com o comando do super da base, que no Ratão vira o Baile)
    velho = "triggerall = ((var(20) > 0) || (life <= 200 && power >= 2000))"
    assert velho in cmd
    # o ← → ↓ + a/b do kit levava ao Baile no Ratão e escondia a Rajada: sai; o Baile é só ← → ↓ + x+y
    na_entrada("Saideira Sombria", 3100, lambda b: "")
    cmd = antes_de(cmd, "[State -1, Nocaute de Rua]", gp.entrada(
        "Baile da Esquina", 3100, ['command = "baile"', "power >= 1000", "var(20) > 0", "statetype != A"],
        ("var(1)", "(stateno = [1000,1501]) && movehit && movehit <= 8")))
    # Encosta na Parede (← + x, y, → + b): ← segurado e depois → + b é o mesmo movimento do Gingado b (← → b), que
    # vem antes na lista e roubava o fim do kombo; do 344 não sai Gingado b
    na_entrada("Role por tras e chute", 1701, com("stateno != 344"))
    # cada projétil trava só a si mesmo: a nuvem da Tragada (2,5 s no ar) não impede o Boné, nem o contrário
    trava = "triggerall = numprojid(1000) + numprojid(1001) + numprojid(1002) + numprojid(1003) = 0\n"
    for titulo, n, proj in (("Bola forte", 1001, 1000), ("Bola fraca", 1000, 1000),
                            ("Garrafada forte", 1601, 1002), ("Garrafada fraca", 1600, 1002)):
        na_entrada(titulo, n, lambda b, proj=proj: b.replace(trava, f"triggerall = numprojid({proj}) = 0\n"))
    # Tragada de Beck: a nuvem tem id próprio (1004; o 1003 é dos cacos da Garrafa) e trava só a si mesma. Antes os
    # Óculos e a Garrafa no ar (1002) e os cacos no chão impediam a Tragada.
    na_entrada("Mao de Sombra", 3400, lambda b: b.replace(trava, "triggerall = numprojid(1004) = 0\n"))
    # Sobe pro Teto: x, y, ↓ + y (no kit era a, b, ↓ + y)
    na_entrada("Kombo 4: b", 346, lambda b: b.replace('command = "b"', 'command = "y"').replace(
        "stateno = 230 && movecontact", "stateno = 200 && movecontact").replace(
        "triggerall", 'triggerall = command != "holdfwd"\ntriggerall', 1))
    # Fim de Baile: x, → + y (o kit já cancela o 200 no 3431), b
    na_entrada("Desp: Kombo 2", 348, lambda b: "")
    na_entrada("Desp: Kombo 3", 349, lambda b: b.replace('command = "x"', 'command = "b"').replace(
        "stateno = 348 && movecontact", "stateno = 3431 && movecontact"))
    # Corte descendo: x no ar, no Ratão
    i = cmd.index("[State -1, Golpe no ar]")
    cmd = cmd[:i] + gp.entrada("Desp: Corte descendo", 3436, ['command = "x"', "statetype = A", "var(20) > 0"],
                               ("ctrl",)) + cmd[i:]
    for velho, novo in (("Chuva de Bebidas", "Rajada da Esquina"), ("Mao de Sombra", "Tragada de Beck"),
                        ("Queda Escura", "Grave do Paredao"), ("Sombra Atravessada", "Garrafa Voadora"),
                        ("Garrafada f", "Bone Voador f"), ("Role por tras", "Gingado de Esquiva")):
        assert f"[State -1, {velho}" in cmd, velho
        cmd = cmd.replace(f"[State -1, {velho}", f"[State -1, {novo}")  # rótulos do kit do Pengaró (só comentário)
    return cmd.replace("gerar_pengaro.py", "gerar_ck.py").replace("[State -1, Agarrao whisky]", "[State -1, Saideira]")


# ================================================================ textos
gp.VITORIAS = [
    "Tá achando que é quem, parça?",
    "Errou o soco, tomou o troco.",
    "Ajeita o boné que a aula acabou.",
    "Vem de novo, eu deixo.",
    "Nem suei a camisa.",
    "Na esquina é assim: piscou, dormiu.",
    "Avisa lá que o CK passou.",
    "Essa luva aqui não é enfeite.",
]

DEF = """; Gerado por ferramentas/gerar_ck.py. Edite lá, não aqui.
[Info]
name = "CK"
displayname = "CK"
versiondate = 11,11,2026
mugenversion = 1.1
author = "Breno"
pal.defaults = 1
localcoord = 320,240

[Files]
cmd = ck.cmd
cns = ck.cns
st = ck.cns
stcommon = common1.cns
sprite = ck.sff
anim = ck.air
movelist = movelist.dat

[Palette Keymap]
x = 1
"""

GOLPES = """<#f0f000>:Especiais:</>
Tragada <#bebebe>(nuvem que fica parada e tonteia)</>	_D_F^P
Boné Voador <#bebebe>(vai e volta)</>			_F_B^P
Levanta, Comédia <#bebebe>(antiaéreo)</>		_F_D^P
Bote <#bebebe>(avanço)</>					_D_F^K
Bicuda Baixa <#bebebe>(golpe baixo)</>			_D_B^K
Gingado de Esquiva <#bebebe>(a passa, b passa e bate)</>	_B_F^K
Contragolpe <#bebebe>(apanhou na guarda baixa, responde)</>	_D_B^P
Pêndulo <#bebebe>(esquiva; x ou y sai com soco)</>	_B_D^K

<#f0f000>:Só no Modo Ratão:</>
Garrafa Voadora <#bebebe>(arco, deixa caco no chão)</>	_D_F^P
Tragada de Beck <#bebebe>(nuvem grande)</>		_D_U^P
Óculos Voador <#bebebe>(vai e volta)</>			_F_B^P
Passinho Ratão <#bebebe>(avanço)</>				_F_B^K
Grave do Paredão <#bebebe>(empurra para longe)</>	_D_U^K
Corrente Y e B de 4 golpes			^Y^Y^Y^Y / ^B^B^B^B
Fim de Baile						^X, _F+^Y, ^B

<#f0f000>:Correntes (acertando os 3, o 4º derruba):</>
Jab, Jab Duplo, Cruzado, Uno-Dos de Rua		^X^X^X^X
Direto, Ganchos, Levanta, Comédia			^Y^Y^Y^Y
Bicuda, Chute Baixo, Joelhada, Bicuda de Pedreiro	^A^A^A^A
Chute Frontal, Chute Alto, Pisão, Voadora da Esquina	^B^B^B^B

<#f0f000>:Kombos:</>
Bom Dia, Cumpadi					_F+^Y, ^X, ^B
Sobe e Desce						^X, _D+^A, ^Y
Encosta na Parede					_B+^X, ^Y, _F+^B
Sobe pro Teto						^X, ^Y, _D+^Y

<#f0f000>:Supers:</>
Rajada da Esquina <#bebebe>(1000)</>		_B_F_D^K
Nocaute de Rua <#bebebe>(2000)</>			_B_F_D^P
Baile da Esquina <#bebebe>(1000, no Modo Ratão)</>	_B_F_D^X_+^Y

<#f0f000>:Sistema:</>
Modo Ratão <#bebebe>(barra cheia)</>		^X_+^Y
Rolamento							^X_+^A
Golpe de afastar					^Y_+^B
Gola na Mão <#bebebe>(agarrão)</>			[_B/_F]_+^Y
Abaixa Aí <#bebebe>(oponente agachado)</>	_D_+^Y
Saideira <#bebebe>(colado)</>				_B_F^Y
Provocação							^C
Parry                              _F^C
"""


# ================================================================ arquivos derivados
def retrato():
    """Retrato da seleção: o busto do desenho 0 da referência, em resolução cheia, sem o magenta."""
    folha = np.array(Image.open(RAIZ / "sprites/ck/quadros/folhas_arcade/referencia_ginga.png").convert("RGBA"))
    cel = folha[40:400, 4:276]
    r, g, b = (cel[..., i].astype(int) for i in range(3))
    cel[(r > 150) & (b > 150) & (g < 120) & (abs(r - b) < 70), 3] = 0
    img = Image.fromarray(cel)
    img.crop(img.getbbox()).save(RETRATO)


def preparar():
    pasta = QUADROS / "endiabrado"  # as 8 poses de reserva que gp.arte_endiabrada e gp.preset_despertado leem
    pasta.mkdir(exist_ok=True)
    for i, (folha, d) in enumerate(POSES_RATAO):
        shutil.copyfile(QUADROS / folha / f"{d:02d}.png", pasta / f"{i:02d}.png")
    if not RETRATO.exists():
        retrato()


def ajustar_clsn1(blocos, s, preset):
    ajustados = gp.ajustar_clsn1(blocos, s, preset)
    for k, bloco in enumerate(blocos):
        m = re.match(r"\[Begin Action (\d+)\]", bloco)
        if m and int(m[1]) % 10000 in SEM_AJUSTE:
            ajustados[k] = bloco
    return ajustados


def imprimir_alcance(air):
    """Até onde vai a caixa de cada golpe no .air (x máximo da Clsn1), para conferir contra a distância do robô."""
    for bloco in air.split("[Begin Action ")[1:]:
        n = int(bloco.split("]")[0])
        xs = [max(int(a), int(c)) for a, c in re.findall(r"Clsn1\[0\] = (-?\d+),-?\d+,(-?\d+),-?\d+", bloco)]
        if xs and 200 <= n < 4000 and n not in gp.PROJETEIS:
            m = next((m for m in gp.extra.TODOS + gp.extra.ESPECIAIS_A_MAO if m.estado == n), None)
            print(f"{n:5d}  caixa até {max(xs):3d}" + (f"  avanço {m.avanco}" if m and m.avanco else ""))


def main():
    preparar()
    SAIDA.mkdir(parents=True, exist_ok=True)
    gp.BAIXO[0] = (-26, 0, 26, -84)    # agachado do CK: 78 a 84 px
    gp.DEITADO[0] = (-62, 0, 40, -28)  # deitado: 97 x 26 px
    s = gp.montar_sprites(retrato=RETRATO)
    efeitos_ck(s)
    faiscas = gp.carregar_proprios(s)  # faíscas do kit repintadas + a fumaça antiga (só pela paleta)
    cns = cns_ck(gp.montar_cns())
    # estilo de pose segurada: os fracos são os golpes com hitsound F5,0 (no Pengaró a lista é fixa e conferida)
    gp.FRACOS = {int(n) for n in re.findall(r"\[State (\d+), Golpe\]\n(?:[^\n]+\n)*?hitsound = F5,0\n", cns)}
    del faiscas[9210]  # a fumaça antiga: só pela paleta, fora do .air (a poda a tira do .sff)
    a = gp.montar_air(s, faiscas, arte_despertada=gp.arte_endiabrada(s))
    preset = gp.preset_despertado(s)
    aura = aura_ck.ligar(s)  # aura do Ratão (Blender): grupos e ações 9600 a 9602, fora da paleta
    air = "\n".join(ajustar_clsn1(a.txt, s, preset)).replace("gerar_pengaro.py", "gerar_ck.py") + "\n" + aura.air()
    vitima = {(int(g), int(i)) for n in gp.ACOES_VITIMA
              for g, i in gp.RE_ELEMENTO.findall(air.split(f"[Begin Action {n}]")[1].split("[Begin Action")[0])}
    assert vitima <= gp.SPRITES_VITIMA, f"sprites da vítima fora do conjunto comum: {sorted(vitima - gp.SPRITES_VITIMA)}"
    if "--alcance" in sys.argv:
        return imprimir_alcance(air)
    cns = gp.despertar_do_pengaro(gp.ajustar_sparkxy(gp.remapear_animelem(cns, a.mapas), a.ativos))
    cns = gp.sem_ginga_9203(cns)
    # o Pengaró entra endiabrado pela 2ª paleta da seleção; o CK não tem isso
    cns, k = re.subn(r"\[State -2, Endiabrado pela seleção\]\n(?:[^\n]+\n)+\n", "", cns)
    assert k == 1
    cns = cns.replace("anim = 9215\nid = 9215", "anim = 9253\nid = 9215")  # saída do Ratão: fumaça do CK
    # nada da aura pintado no corpo (regras-dos-lutadores, seção 4): sai o PalFX que tingia o Ratão (como no Lote 7 do
    # Pengaró) e o rastro (AfterImageTime) que mantinha o AfterImage da cena vivo o Despertar inteiro, um halo
    # branco-azulado em volta do corpo (cético de 2026-11-12). O rastro de 40 tiques de cada super continua.
    cns = gp.sem_tinta_do_despertar(cns)
    cns, k = re.subn(r"\[State -2, Rastro\]\ntype = AfterImageTime\n(?:[^\n]+\n)+\n", "", cns)
    assert k == 1, "rastro do Despertar não encontrado"
    cns = cns.rstrip() + "\n\n" + gp.efeitos_cns(a.ativos, gp.FRACOS)
    cns = cns.replace("[Data]", preset + "[Quotes]\n" + "".join(
        f'victory{i + 1} = "{v}"\n' for i, v in enumerate(gp.VITORIAS)) + "\n[Data]", 1)
    cns = cns.replace("gerar_pengaro.py", "gerar_ck.py")
    # Baile da Esquina (ficha: 1 estoque, só no Despertar): no kit o super encerrava o Despertar no 1º tick e a aura
    # sumia durante o próprio super. No CK o Ratão continua.
    cns, k = re.subn(r"\[State 3100, Fim Despertar\]\n(?:[^\n]+\n)+\n", "", cns)
    assert k == 1
    # ...mas o dano do Baile continua o de antes: no kit ele batia já sem o bônus de 45% do Despertar (436 de dano;
    # com o bônus ia a 631 por 1 estoque)
    velho = "value = ifelse(var(20) > 0, 1.45, 1)"
    assert cns.count(velho) == 1
    cns = cns.replace(velho, "value = ifelse(var(20) > 0 && stateno != 3100, 1.45, 1)")
    # Agarrão em pé (ficha: três socos curtos e empurra): o dano de 100 sai em três socos (30, 30, 40)
    velho = "[State 810, Dano]\ntype = TargetLifeAdd\ntrigger1 = Time = 14\nvalue = -100\n\n"
    assert cns.count(velho) == 1
    cns = cns.replace(velho, "".join(
        f"[State 810, Soco {i}]\ntype = TargetLifeAdd\ntrigger1 = Time = {t}\nvalue = -{d}\n\n"
        + (f"[State 810, Som {i}]\ntype = PlaySnd\ntrigger1 = Time = {t}\nvalue = F5, 0\n\n" if t < 14 else "")
        for i, (t, d) in enumerate(((4, 30), (9, 30), (14, 40)), 1)))
    assert "[Statedef -4]" not in cns and "NumExplod(9210)" not in cns, "o CK ganhou um -4 ou a aura antiga voltou"
    aura.conferir(acoes=a.acoes, explods=re.findall(r"^\s*id\s*=\s*(\d+)", cns, re.M))
    cns = cns.rstrip() + "\n\n" + aura.cns(cabecalho=True)
    # corpo em alta resolução (ferramentas/hd.py): os desenhos 3x de quadros_arcade_hd e o lutador em 1/3. Vem DEPOIS
    # da aura entrar no .cns: o hd.py só reconhece a ação 9600 como efeito (e não a amplia: ela já é 3x e o Explod
    # usa scale 1/3) pelo Explod dela; antes disso a aura contava como corpo e era ampliada 3x.
    if QUADROS_HD.exists():
        air, cns = hd.aplicar(s, air, cns, [(QUADROS, QUADROS_HD)], gp.SPRITES_VITIMA)
    (SAIDA / "ck.air").write_text(air, encoding="utf-8", newline="\n")
    (SAIDA / "ck.cns").write_text(cns, encoding="utf-8", newline="\n")
    gp.escrever_sff(SAIDA / "ck.sff", s, manter=gp.sprites_mantidos(air, cns))
    (SAIDA / "ck.cmd").write_text(cmd_ck(gp.montar_cmd()), encoding="utf-8")
    (SAIDA / "ck.def").write_text(DEF, encoding="utf-8", newline="\n")
    (SAIDA / "movelist.dat").write_text(GOLPES, encoding="utf-8", newline="\n")
    print(f"{len(s.lista)} sprites, {len(a.acoes)} ações em {SAIDA}")


if __name__ == "__main__":
    main()
