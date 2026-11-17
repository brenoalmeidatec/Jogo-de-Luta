#!/usr/bin/env python3
"""Efeitos de combate de todos os lutadores (issue #38 do Breno, 2026-11-14): pixelfx na cor de cada lutador.

  python ferramentas/efeitos.py                     aplica nos 5 lutadores de chars/
  python ferramentas/efeitos.py gutto ck            só nesses
  python ferramentas/efeitos.py --folha PASTA       folha com os efeitos de cada lutador (para mostrar ao Breno)

Regra do Breno (#38): os efeitos saem só do pixelfx e do Blender, nada do ChatGPT. Golpe normal (soco, chute, fraco,
forte, agachado, no ar, agarrão, defesa) usa os desenhos do pixelfx de assets/efeitos/, escolhidos pelo que acontece
(faísca no impacto, poeira no chão, rastro no movimento) e pintados na cor do lutador e da forma. Especial, super e
transformação usam os efeitos do Blender (ferramentas/efeitos_blender.py).

Como o parry.py, trabalha em cima do que já está em chars/<l>/ (sff, air, cns), sem regerar o lutador: o corpo, a
paleta e as caixas não mudam. Os efeitos vão para o .sff como PNG de 32 bits (formato 12, no bloco tdata, como os
retratos), fora da paleta do corpo: assim a cor de cada degrau é a da rampa do lutador, sem cair na cor mais perto do
corpo. Pode rodar quantas vezes quiser: o que ele monta é substituído, não duplicado.

Pintura "em degraus" (técnica do pixelfx): o brilho de cada pixel do desenho escolhe um dos 7 tons da rampa, sem
mistura; o halo translúcido do pixelfx sai (o SFF não guarda meia transparência e o halo virava mancha). A ação de cada
efeito continua com o número de sempre (9200, 9201, ...), então HitDef e Explod não mudam; só os sprites vêm de grupos
novos (8xxx) e os antigos que ninguém usa mais saem do .sff.
"""
import json
import re
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conferir_sff as cs  # noqa: E402
from layout_sff import png_rgba  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FX = RAIZ / "assets/efeitos"
LUTADORES = ("pengaro", "hazaki", "ck", "gutto", "raiclaven")


def hexa(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


# ---------------------------------------------------------------- cores (issue #38): do escuro ao claro, 7 degraus
CORES = {
    "pengaro": {"base": ["#1e0f04", "#4a2508", "#8a4a0c", "#c97a14", "#f0ae2c", "#ffd968", "#fff4cc"],   # whisky
                "desperto": ["#0c0414", "#2a0c4a", "#4e1a86", "#7a32c4", "#a860f0", "#d4a4ff", "#f4e6ff"]},  # violeta
    "hazaki": {"base": ["#200a00", "#5a2004", "#a04808", "#e07a10", "#ffaa22", "#ffd65a", "#fff6c8"],    # laranja-ouro
               "desperto": ["#2a0800", "#701a00", "#c03e00", "#ff7010", "#ffb030", "#ffe070", "#ffffff"]},
    "gutto": {"base": ["#1a0406", "#4a0a0e", "#8c1418", "#cc2420", "#f2502a", "#ff8a5a", "#ffd2c0"],     # vermelho
              "desperto": ["#140202", "#400604", "#8a1404", "#d43008", "#ff6a10", "#ffaa30", "#ffe890"]},  # brasa
    "raiclaven": {"base": ["#0c1214", "#202a2e", "#3a484c", "#5c6e70", "#8aa09c", "#bfe0c8", "#f0fff4"],  # aço e verde
                  "desperto": ["#021404", "#06380e", "#0e6a1c", "#1aa030", "#3cd84c", "#8cff7c", "#e4ffd8"]},  # verde
    "ck": {"base": ["#0e120e", "#222a22", "#3a463a", "#58665a", "#7e8e7e", "#aebcaa", "#e2ecdc"],        # cinza-esverdeado
           "desperto": ["#061008", "#10261a", "#1e4430", "#2e6a48", "#4c9466", "#86c898", "#d4f4dc"]},     # Ratão
    "gbzin": {"base": ["#1c1008", "#3e2412", "#6a3f1c", "#9a6630", "#c89a4c", "#e8c878", "#fff0c0"],     # poeira e palha
              "desperto": ["#04140c", "#0a301c", "#0f5a32", "#179050", "#2cc878", "#84f4b0", "#dcfff0"]},  # Grão-Pastor
}


def rampa(lutador, forma):
    return [hexa(c) for c in CORES[lutador][forma]]


def clarear(r, k=.45):
    """Rampa da defesa: a do lutador puxada para o branco (a defesa não é acerto: sai mais fria e mais clara)."""
    return [tuple(round(c + (235 - c) * k * (i / 6) ** .5) for c in cor) for i, cor in enumerate(r)]


# ---------------------------------------------------------------- desenhos do pixelfx
_CACHE = {}


def quadros_fx(nome):
    """[(RGBA do quadro, pivô do pixelfx)] na ordem da folha (assets/efeitos/<nome>.png + .json)."""
    if nome not in _CACHE:
        dados = json.loads((FX / f"{nome}.json").read_text(encoding="utf-8"))
        folha = Image.open(FX / dados["meta"]["image"]).convert("RGBA")
        pivo = tuple(dados["meta"]["pixelfx"]["pivot"])
        _CACHE[nome] = [(folha.crop((q["frame"]["x"], q["frame"]["y"], q["frame"]["x"] + q["frame"]["w"],
                                     q["frame"]["y"] + q["frame"]["h"])), pivo) for q in dados["frames"]]
    return _CACHE[nome]


def pintar(img, r, corte=190, luz_min=0.0, gama=1.8):
    """Pinta em degraus: o brilho do pixel escolhe o tom da rampa, sem mistura. Pixel com alfa < corte sai (halo)."""
    a = np.asarray(img).astype(np.float32)
    luz = (0.30 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]) / 255
    luz = np.clip(luz * 1.08, 0, 1) ** gama  # gamma: o meio-tom desce na rampa e só o miolo fica quase branco
    idx = np.clip((luz * len(r)).astype(int), 0, len(r) - 1)
    cores = np.array(r, np.uint8)[idx]
    vivo = (a[..., 3] >= corte) & (luz >= luz_min)
    return Image.fromarray(np.dstack([cores, np.where(vivo, 255, 0).astype(np.uint8)]), "RGBA")


def so_maior(img):
    """Só a maior mancha conectada (o rastro sem os pontinhos soltos e a fumaça do pé)."""
    import cv2
    m = (np.asarray(img)[..., 3] > 0).astype(np.uint8)
    n, rot, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    if n <= 2:
        return img
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    a = np.array(img)
    a[rot != k, 3] = 0
    return Image.fromarray(a, "RGBA")


def desfazer(img, passo):
    """Some em xadrez (sem translucidez): passo 1 tira metade dos pixels, passo 2 três quartos."""
    a = np.array(img)
    yy, xx = np.mgrid[:a.shape[0], :a.shape[1]]
    tira = ((xx + yy) % 2 == 0) if passo == 1 else ~((xx % 2 == 0) & (yy % 2 == 0))
    a[tira, 3] = 0
    return Image.fromarray(a, "RGBA")


def centro_do_clarao(img):
    a = np.asarray(img).astype(np.float32)
    luz = a[..., :3].max(axis=2) * (a[..., 3] >= 200)
    if luz.max() <= 0:
        return img.width // 2, img.height // 2
    yy, xx = np.nonzero(luz >= luz.max() * .9)
    return int(round(xx.mean())), int(round(yy.mean()))


# Papéis. Cada um é uma lista de (fonte, índice do quadro, ticks, transformação). A escala vai no elemento do .air.
# Tempos da regra dos efeitos proporcionais: o fraco é um ventinho de 8 ticks; o forte se sente; o final é o maior.
# O pixelfx anda a 30 quadros por segundo, então cada quadro dele vale 2 ticks.
PAPEIS = {
    #            fonte        quadros                            escala  pivô
    "fraco":   (("hit-spark", (0, 1, 2, 3)),),
    "forte":   (("blunt-hit", (0, 1, 2, 3, 4, 5)),),
    "final":   (("crit-hit", (0, 1)), ("blunt-hit", (2, 3, 4, 5, 6, 7, 8))),
    "defesa":  (("hit-spark", (0, 1, 2)),),
    "rastro":  (("uppercut", (2, 2, "x1", "x2")),),
    "poeira":  (("heavy-landing", (3, 5, 7, 9)),),
    "asfalto": (("heavy-landing", (3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23)),),
}
ESCALA = {"fraco": .6, "forte": .85, "final": 1.15, "defesa": .55, "rastro": .9, "poeira": .8, "asfalto": 1.25,
          "parry": .5}
# Nível do Hazak (Breno, #44): o que bate forte acende. Halo de brilho (raio do desfoque, força, margem) por baixo do
# pixel seco, o caminho escolhido na #47. O fraco, a defesa e a poeira ficam secos (regra dos efeitos proporcionais).
HALO = {"forte": (3, .7, 6), "final": (4, .8, 8), "rastro": (3, .6, 6), "parry": (3, .7, 6), "super": (6, .8, 12)}


def com_halo(quadro, papel):
    """(RGBA, ex, ey, ticks) com o brilho desfocado do próprio desenho por baixo (alfa suave: PNG de 32 bits)."""
    if papel not in HALO:
        return quadro
    from PIL import ImageFilter
    img, ex, ey, ticks = quadro
    raio, forca, m = HALO[papel]
    tela = Image.new("RGBA", (img.width + 2 * m, img.height + 2 * m), (0, 0, 0, 0))
    tela.paste(img, (m, m))
    halo = tela.filter(ImageFilter.GaussianBlur(raio))
    halo.putalpha(halo.getchannel("A").point(lambda v: min(255, int(v * forca * 1.6))))
    halo.alpha_composite(tela)
    return halo, ex + m, ey + m, ticks
ESCALA_BLENDER = .75  # escala no .air dos efeitos do Blender (efeitos_blender.py): o mesmo pixel dos do pixelfx
NO_CHAO = {"poeira", "asfalto"}  # pivô do pixelfx (o chão), não o centro do clarão


def montar_papel(papel, r):
    """[(RGBA recortado, eixo x, eixo y, ticks)]."""
    saida = []
    for fonte, quadros in PAPEIS[papel]:
        lista = quadros_fx(fonte)
        if papel in NO_CHAO:
            pivo = lista[0][1]
        else:
            ref = next(i for i in quadros if isinstance(i, int))
            pivo = centro_do_clarao(lista[ref][0])
        anterior = None
        for q in quadros:
            if isinstance(q, str):  # "x1"/"x2": o quadro anterior sumindo em xadrez
                img = desfazer(anterior, int(q[1]))
            else:
                img = pintar(lista[q][0], r, luz_min=.25 if papel == "rastro" else 0)
                if papel == "rastro":
                    img = so_maior(img)
                if papel == "defesa":
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)  # na defesa a faísca volta para quem bateu
            anterior = img
            cx = img.getchannel("A").getbbox()
            if not cx:
                continue
            px = (img.width - 1 - pivo[0]) if papel == "defesa" else pivo[0]
            saida.append(com_halo((img.crop(cx), px - cx[0], pivo[1] - cx[1], 2), papel))
    return saida


def montar_parry(r):
    """Faísca do parry: a estrela do crit-hit (quadros 0 e 1, antes de abrir o anel proibido), na cor da forma."""
    lista = quadros_fx("crit-hit")
    pivo = centro_do_clarao(lista[0][0])
    saida = []
    for q, t in ((0, 2), (1, 2), (1, 2), (0, 2)):
        img = pintar(lista[q][0], r)
        if t and len(saida) == 3:
            img = desfazer(img, 1)
        cx = img.getchannel("A").getbbox()
        saida.append(com_halo((img.crop(cx), pivo[0] - cx[0], pivo[1] - cx[1], t), "parry"))
    return saida


# ---------------------------------------------------------------- estouros, carga e projéteis de energia (pixelfx)
# Pedido do Breno na #51 (2026-11-14): todo efeito de acerto sai do pixelfx, sem imagem do ChatGPT e sem a faísca
# pronta de círculo com raios. O estouro de especial, a explosão de super e a carga, que eram do Blender (anel com
# miolo), viraram composição de desenhos do pixelfx: cada camada é (fonte, quadro por desenho, zoom inteiro, desvio).
# O zoom é inteiro e por vizinho mais próximo, para o pixel continuar seco; o tamanho e o halo são os do nível do Hazak.
def _seq(*q, n):
    return (list(q) + [None] * n)[:n]


TEMA = {  # a camada que dá o jeito de cada lutador ao estouro
    "pengaro": ("hit-spark", (0, 1, 2, 3, 4, 5), 2, "espelho"),      # respingo para os dois lados
    "gutto": ("blunt-hit", (None, None, 0, 1, 2, 3, 4, 5), 1, (26, -22)),  # segunda pancada (o chute dobrado)
    "raiclaven": ("zap-hit", (2, 3, 4, 5, 6, 7, 8), 2, None),        # relâmpago
    "ck": ("heavy-landing", (2, 3, 5, 7, 9, 11), 2, None),           # onda baixa de poeira (o grave do paredão)
    "gbzin": ("ground-slam", (20, 26, 32, 38, 44, 50), 1, None),      # terra e palha do cajado no chão
}


def camadas(lutador, efeito):
    tema = TEMA[lutador]
    if efeito == "especial":
        n = 8
        base = [("blunt-hit", _seq(0, 1, 1, 2, 3, 4, 5, 6, n=n), 2, (0, 0)),
                ("crit-hit", _seq(0, 1, 1, n=n), 2, (0, 0))]
    elif efeito == "super":
        n = 11
        base = [("blunt-hit", _seq(0, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8, n=n), 2, (0, 0)),
                ("crit-hit", _seq(0, 1, 1, 1, n=n), 2, (0, 0)),
                ("blunt-hit", _seq(None, 0, 1, 1, 2, 3, 4, 5, 6, 7, n=n), 2, (4, -66)),
                ("blunt-hit", _seq(None, None, 0, 1, 1, 2, 3, 4, 5, 6, 7, n=n), 2, (-6, 62)),
                ("blunt-hit", _seq(None, None, 0, 1, 1, 2, 3, 4, 5, 6, n=n), 2, (-72, -34)),
                ("blunt-hit", _seq(None, None, None, 0, 1, 1, 2, 3, 4, 5, 6, n=n), 2, (70, 30)),
                ("blunt-hit", _seq(None, None, None, None, 0, 1, 1, 2, 3, 4, 5, n=n), 2, (62, -50)),
                ("blunt-hit", _seq(None, None, None, None, None, 0, 1, 1, 2, 3, 4, n=n), 2, (-64, 46))]
    else:  # carga: as faíscas vêm de longe, juntam e acendem
        n = 8
        # só os quadros do começo do charge-up: depois dele abre um círculo pontilhado em volta, que o Breno não quer
        return [("charge-up", [2, 4, 6, 8, 10, 12, 14, 14], 2, (0, 0)),
                ("crit-hit", _seq(None, None, None, None, None, None, 1, 0, n=n), 2, (0, 0))], n
    fonte, quadros, zoom, onde = tema
    z = zoom
    if onde == "espelho":
        base += [(fonte, _seq(*quadros, n=n), z, (0, 0)), (fonte, _seq(*quadros, n=n), -z, (0, 0))]
    else:
        base.append((fonte, _seq(*quadros, n=n), z, onde or (0, 0)))
    return base, n


_CENTRO = {}


def centro_fx(fonte):
    """O ponto do efeito no desenho do pixelfx: o miolo do clarão (na carga, o do quadro em que ela acende)."""
    if fonte not in _CENTRO:
        lista = quadros_fx(fonte)
        ref = {"charge-up": 10, "zap-hit": 4, "heavy-landing": None, "energy-disc": None, "fireball": None,
               "ground-slam": None}
        k = ref.get(fonte, 0)
        _CENTRO[fonte] = lista[0][1] if k is None else centro_do_clarao(lista[k][0])
    return _CENTRO[fonte]


def compor(lista, n, r, papel, ticks, corte=190, gama=1.8, so_fumaca=False):
    """Junta as camadas (o mais claro ganha), pinta na rampa e põe o halo: [(RGBA, ex, ey, ticks)]."""
    lado = 1000
    c = lado // 2
    saida = []
    for k in range(n):
        tela = np.zeros((lado, lado, 4), np.uint8)
        for fonte, quadros, zoom, (dx, dy) in lista:
            if quadros[k] is None:
                continue
            img = quadros_fx(fonte)[quadros[k]][0]
            px, py = centro_fx(fonte)
            if so_fumaca:  # só a fumaça que sobe: o chão, o anel e os estilhaços do desenho ficam de fora
                a = np.array(img)
                a[py - 18:] = 0
                img = Image.fromarray(a, "RGBA")
                py -= 44
            z = abs(zoom)
            if zoom < 0:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
                px = img.width - 1 - px
            a = np.asarray(img.resize((img.width * z, img.height * z), Image.NEAREST))
            x0, y0 = c + dx - px * z, c + dy - py * z
            alvo = tela[y0:y0 + a.shape[0], x0:x0 + a.shape[1]]
            ganha = a[..., 3:4].astype(int) * a[..., :3].max(axis=2, keepdims=True) \
                > alvo[..., 3:4].astype(int) * alvo[..., :3].max(axis=2, keepdims=True)
            alvo[...] = np.where(ganha, a, alvo)
        img = pintar(Image.fromarray(tela, "RGBA"), r, corte=corte, gama=gama)
        if so_fumaca:
            img = so_maior(img)
        cx = img.getchannel("A").getbbox()
        if cx:
            saida.append(com_halo((img.crop(cx), c - cx[0], c - cx[1], ticks), papel))
    return saida


# ação do .air -> (efeito, forma, ticks por desenho, papel do halo, escala no .air)
GRANDES = {9240: ("especial", "base", 2, "final", .85), 9270: ("especial", "desperto", 2, "final", .85),
           9241: ("super", "base", 3, "super", .8), 9271: ("super", "desperto", 3, "super", .8),
           9243: ("carga", "base", 2, "forte", .85), 9273: ("carga", "desperto", 2, "forte", .85),
           9244: ("carga", "base", 4, "forte", .85), 9274: ("carga", "desperto", 4, "forte", .85)}


def efeitos_grandes(lutador):
    """{ação: desenhos} e {ação: escala} do estouro de especial, da explosão de super e da carga, no pixelfx."""
    acoes, escalas = {}, {}
    for acao, (efeito, forma, ticks, papel, escala) in GRANDES.items():
        lista, n = camadas(lutador, efeito)
        acoes[acao] = compor(lista, n, rampa(lutador, forma), papel, ticks)
        escalas[acao] = escala
    return acoes, escalas


# Efeitos que ainda eram imagem do ChatGPT dentro de ações de projétil (lista na #51): o corte roxo do especial da
# forma (ação 3012, grupo 9212) e a nuvem do CK (grupo 9300). Só o desenho troca: caixas e tempos da ação ficam.
# lutador -> {ação: (fonte, quadros, zoom, forma, escala no .air, alfa mínimo)}
PROJETEIS = {
    "pengaro": {3012: ("energy-disc", (0, 2, 4, 6, 8, 10, 12, 14), 2, "desperto", .8, 190)},
    "raiclaven": {3012: ("energy-disc", (0, 2, 4, 6, 8, 10, 12, 14), 2, "desperto", .8, 190)},
    "gutto": {3012: ("fireball", (0, 4, 8, 12, 16, 20, 24, 28), 2, "desperto", .8, 190)},
    "ck": {1005: ("ground-slam", (20, 26, 32, 38, 44), 1, "fumaca", 1.0, 70),
           1006: ("ground-slam", (50, 56, 62), 1, "fumaca", 1.0, 50),
           9253: ("ground-slam", (26, 32, 38, 44, 50, 56), 1, "fumaca", 1.0, 60)},
    # Gbzin: a poeira da Cabra Solta (até a folha fx_cabra) e a onda rasteira do Cajado no Chão (1505)
    "gbzin": {1005: ("ground-slam", (20, 26, 32, 38, 44), 1, "fumaca", 1.0, 70),
              1006: ("ground-slam", (50, 56, 62), 1, "fumaca", 1.0, 50),
              1505: ("ground-slam", (14, 20, 26, 20), 1, "fumaca", 1.0, 70)},
}


def efeitos_projeteis(lutador):
    acoes, escalas = {}, {}
    for acao, (fonte, quadros, zoom, forma, escala, corte) in PROJETEIS.get(lutador, {}).items():
        fumaca = forma == "fumaca"  # a nuvem do CK: rampa clara e gama baixa, para a fumaça não virar carvão
        r = clarear(rampa(lutador, "base"), .75) if fumaca else rampa(lutador, forma)
        acoes[acao] = compor([(fonte, list(quadros), zoom, (0, 0))], len(quadros), r, "rastro", 2, corte,
                             .6 if fumaca else 1.8, fumaca)
        escalas[acao] = escala
    return acoes, escalas


def trocar_desenhos(air, acao, grupo, n, escala):
    """Na ação (de projétil), troca só o sprite de cada elemento, na ordem: caixas, tempos e Loopstart ficam."""
    m = re.search(rf"(?ms)^\[Begin Action {acao}\][^\n]*\n.*?(?=^\[Begin Action|\Z)", air)
    if not m:
        return air
    k = [0]

    def el(mm):
        i = k[0] % n
        k[0] += 1
        return f"{grupo},{i}, 0,0, {mm.group(1)}, , , {escala:g}, {escala:g}"
    novo = re.sub(r"(?m)^\s*\d+\s*,\s*\d+\s*,\s*-?\d+\s*,\s*-?\d+\s*,\s*(-?\d+)[^\n]*$", el, m.group(0))
    return air[:m.start()] + novo + air[m.end():]


# ---------------------------------------------------------------- o que cada lutador usa
# ação do .air -> (papel, forma). O kit do Pengaró (Pengaró, Gutto, Raiclaven, CK): 9200 fraco, 9201 forte,
# 9202 defesa, 9205 finalizador; +30 na forma despertada; 9213/9212 rastro e 9214/9215 poeira (normal/despertado).
KIT = {9200: ("fraco", "base"), 9201: ("forte", "base"), 9202: ("defesa", "base"), 9205: ("final", "base"),
       9230: ("fraco", "desperto"), 9231: ("forte", "desperto"), 9232: ("defesa", "desperto"),
       9234: ("defesa", "desperto"), 9235: ("final", "desperto"),
       9213: ("rastro", "base"), 9212: ("rastro", "desperto"), 9214: ("poeira", "base"), 9215: ("poeira", "desperto"),
       7690: ("parry", "base"), 7691: ("parry", "desperto")}
# Hazak (gerar_hazaki.py): 9200 fraco, 9207 soco seco (forte), 9201 crítico (final), 9216 defesa, 9208 subida
# (rastro), 9209 poeira do pé, 9205 asfalto (especiais: o do Blender entra por cima quando existir).
HAZAK = {9200: ("fraco", "base"), 9207: ("forte", "base"), 9201: ("final", "base"), 9216: ("defesa", "base"),
         9208: ("rastro", "base"), 9209: ("poeira", "base"), 9205: ("asfalto", "base"),
         7690: ("parry", "base"), 7691: ("parry", "desperto")}
# grupos antigos dos efeitos: saem do .sff se nenhum .air os usa mais
VELHOS = {9300, 9200, 9201, 9202, 9205, 9207, 9208, 9209, 9212, 9213, 9214, 9215, 9216, 9230, 9231, 9232, 9234, 9235,
          29212, 7690, 7691}


def grupo_novo(acao):
    return {7690: 8290, 7691: 8291}.get(acao, acao - 1000)


def efeitos_do(lutador):
    """{ação: [(RGBA, ex, ey, ticks)]} e {ação: escala}."""
    mapa = HAZAK if lutador == "hazaki" else KIT
    acoes, escalas = {}, {}
    for acao, (papel, forma) in mapa.items():
        r = rampa(lutador, forma)
        if papel == "parry":
            acoes[acao] = montar_parry(r)
        else:
            acoes[acao] = montar_papel(papel, clarear(r) if papel == "defesa" else r)
        escalas[acao] = ESCALA[papel]
    return acoes, escalas


# ---------------------------------------------------------------- especial, super e transformação (Blender)
BLENDER = RAIZ / "sprites/efeitos_blender"
# ação do .air -> (efeito, forma). O Blender renderiza em efeitos_blender.py; aqui só se liga o que já está pronto.
CORTE = {"especial": 7, "super": 10}  # desenhos usados de cada render
ACOES_BLENDER = {9240: ("especial", "base"), 9270: ("especial", "desperto"), 9241: ("super", "base"),
                 9271: ("super", "desperto"), 9272: ("transformacao", "desperto"),
                 # a carga: energia do lutador juntando no corpo antes do especial; na super ela é lenta e maior
                 9243: ("carga", "base"), 9273: ("carga", "desperto"),
                 9244: ("carga_lenta", "base"), 9274: ("carga_lenta", "desperto")}


def efeitos_blender(lutador):
    """{ação: [(RGBA, ex, ey, ticks)]} dos efeitos do Blender que existem para o lutador."""
    acoes = {}
    for acao, (efeito, forma) in ACOES_BLENDER.items():
        pasta = BLENDER / lutador / f"{efeito.replace('_lenta', '')}_{forma}"
        if not (pasta / "meta.json").exists():
            continue
        meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
        if efeito == "carga_lenta":
            meta["ticks"] *= 2
        quadros = []
        # o fim do render é a fumaça escura se desfazendo: no jogo virava borrão marrom em cima dos lutadores
        for arq in sorted(pasta.glob("[0-9][0-9].png"))[:meta.get("corte", CORTE.get(efeito))]:
            img = Image.open(arq).convert("RGBA")
            cx = img.getchannel("A").getbbox()
            if not cx:
                continue
            quadros.append((img.crop(cx), meta["pivo"][0] - cx[0], meta["pivo"][1] - cx[1], meta["ticks"]))
        if quadros:
            acoes[acao] = quadros
    return acoes


# ---------------------------------------------------------------- .cns: especial, super e transformação
MARCA = "(efeitos.py)"


def blocos(cns):
    return list(re.finditer(r"^\[Statedef (-?\d+)\][^\n]*\n.*?(?=^\[Statedef |\Z)", cns, re.M | re.S))


def tinta(lutador, forma):
    """(mul do fundo, add no oponente e no rastro) na cor da forma: o fundo escurece puxando para a cor."""
    r = rampa(lutador, forma)
    m = max(r[3])
    return tuple(round(70 + 100 * v / m) for v in r[3]), tuple(round(v * .5) for v in r[4])


def por_forma(lutador, qual, k=1.0):
    """Os três números de uma cor como expressão: a da forma despertada se var(20) > 0, senão a normal."""
    b, d = (tuple(round(v * k) for v in tinta(lutador, f)[qual]) for f in ("base", "desperto"))
    return ", ".join(str(x) if x == y else f"ifelse(var(20) > 0, {y}, {x})" for x, y in zip(b, d))


def ctl(n, nome, tipo, *linhas):
    return f"[State {n}, {nome} {MARCA}]\ntype = {tipo}\n" + "\n".join(linhas) + "\n\n"


def limpar(cns):
    """Tira tudo o que este arquivo pôs (controladores e linhas marcadas), para pôr de novo sem duplicar."""
    cns = re.sub(rf"^\[State -?\d+, [^\]\n]*{re.escape(MARCA)}\]\n(?:[^\n]+\n)+\n?", "", cns, flags=re.M)
    return re.sub(rf"^[^\n]*; {re.escape(MARCA)}\n", "", cns, flags=re.M)


def linhas_marcadas(bloco, depois, linhas):
    return re.sub(rf"(?m)^({depois} = [^\n]*\n)", lambda m: m.group(1) + "".join(f"{l} ; {MARCA}\n" for l in linhas),
                  bloco, count=1)


RE_BATE = re.compile(r"(?m)^type = (HitDef|Projectile)$")


def nivel(bloco, n, lutador):
    """Nível do Hazak (Breno, #44) nos especiais (1000-1999, 3400-3403) e nas supers (3000-3399): carga no corpo e
    rastro na cor da forma antes do golpe; no acerto, tela treme, oponente pisca na cor da forma e o fundo acende.
    Na super o fundo fica escuro na cor da forma enquanto ela dura. Nos normais, só o finalizador faz o oponente piscar."""
    especial = 1000 <= n <= 1999 or 3400 <= n <= 3403
    super_ = 3000 <= n <= 3399
    partes = re.split(r"(?m)^(?=\[State )", bloco)
    add = por_forma(lutador, 1)
    if not (especial or super_):
        for i, c in enumerate(partes):
            if RE_BATE.search(c) and re.search(r"(?m)^sparkno = [^\n]*9205", c) and "palfx." not in c:
                partes[i] = linhas_marcadas(c, "damage", ("palfx.time = 8", f"palfx.add = {add}"))
        return "".join(partes)
    if not any(RE_BATE.search(c) for c in partes[1:]):
        return bloco
    for i, c in enumerate(partes):
        if i and RE_BATE.search(c):
            c = re.sub(r"(?m)^(?:envshake\.(?:time|freq|ampl)|palfx\.[a-z]+) = [^\n]*\n", "", c)
            p = [int(v) for v in re.findall(r"-?\d+", (re.search(r"(?m)^pausetime = ([^\n;]*)", c) or [0, "0"])[1])]
            pesado = max(p or [0]) >= 10
            if super_:
                treme, pisca = ((28, 90, -10), 18) if pesado else ((8, 160, -3), 6)
                if not pesado:  # rajada da super: estouro de especial em cada acerto; o de super fica para o final
                    c = re.sub(r"(?m)^(sparkno = [^\n]*)$",
                               lambda m: m.group(1).replace("9271", "9270").replace("9241", "9240"), c)
            else:
                treme, pisca = ((16, 120, -6), 12) if pesado else ((10, 150, -3), 8)
            # o estouro novo já é grande: a escala da faísca não passa de 1
            c = re.sub(r"(?m)^sparkscale = ([\d.]+), ([\d.]+)$",
                       lambda m: f"sparkscale = {min(1.0, float(m.group(1))):g}, {min(1.0, float(m.group(2))):g}", c)
            partes[i] = linhas_marcadas(c, "damage", (
                f"envshake.time = {treme[0]}", f"envshake.freq = {treme[1]}", f"envshake.ampl = {treme[2]}",
                f"palfx.time = {pisca}", f"palfx.add = {add}"))
        elif i and re.search(r"(?m)^type = AfterImage$", c) and super_:
            c = re.sub(r"(?m)^paladd = 0,0,0\n", "", c)
            if "paladd" not in c:
                partes[i] = linhas_marcadas(c, "palcolor", (f"paladd = {add}",))
    corpo = "".join(partes[1:])
    carga, lenta = "ifelse(var(20) > 0, 9273, 9243)", "ifelse(var(20) > 0, 9274, 9244)"
    novo = ctl(n, "Carga", "Explod", "trigger1 = Time = 0", f"anim = {lenta if super_ else carga}", "id = 9243",
               "postype = p1", "pos = 8, -60", "bindtime = -1", "removetime = -2", "sprpriority = 3", "ownpal = 1",
               *(("scale = 1.5, 1.5", "supermovetime = 90") if super_ else ()), "ignorehitpause = 1")
    if not re.search(r"(?m)^type = AfterImage$", corpo):
        novo += ctl(n, "Rastro do corpo", "AfterImage", "trigger1 = Time = 0", "time = 18", "length = 6",
                    "timegap = 2", "framegap = 2", "trans = add", "palcolor = 0", "palbright = 0,0,0",
                    f"paladd = {por_forma(lutador, 1, 1.5)}", "palmul = .3,.3,.3")
    if super_:
        novo += ctl(n, "Fundo na cor da forma", "BGPalFX", "trigger1 = Time >= 1", "time = 2",
                    f"mul = {por_forma(lutador, 0)}")
        novo += ctl(n, "Solta: tremida", "EnvShake", "trigger1 = Time = 1", "time = 16", "freq = 170", "ampl = -3")
    if not re.search(r"(?m)^type = BGPalFX\ntrigger1 = MoveHit", corpo) and re.search(r"(?m)^type = HitDef$", corpo):
        novo += ctl(n, "Clarão do acerto", "BGPalFX", "trigger1 = MoveHit = 1", "persistent = 0", "time = 5",
                    f"add = {por_forma(lutador, 1, .7)}", f"mul = {por_forma(lutador, 0)}", "ignorehitpause = 1")
    return partes[0] + novo + corpo


def ligar_cns(cns, acoes, hazak, lutador=None):
    """Faísca dos especiais (1000-1999) e das supers (3000-3399) trocada pela do Blender; pilar no Despertar (2000);
    e o nível do Hazak (função nivel) nos lutadores que têm a carga do Blender."""
    def faisca(base, desperto):
        if hazak or desperto not in acoes:
            return f"sparkno = S{base}"
        return f"sparkno = S(ifelse(var(20) > 0, {desperto}, {base}))"
    cns = limpar(cns)
    sobe = lutador and not hazak and 9243 in acoes
    trocas = []
    for m in blocos(cns):
        n = int(m.group(1))
        bloco = m.group(0)
        novo = bloco
        if (n == 2000 or 3000 <= n <= 3399) and 9240 in acoes:
            # o clarão da pausa da super era o anim 100 do motor (a faísca azul do fightfx): vira o estouro do lutador
            # (no Despertar) ou some (na super, onde a carga grande do lutador faz esse papel)
            alvo = "-1" if sobe and n != 2000 else faisca(9240, 9270).split(" = ", 1)[1]
            novo = re.sub(r"(type = SuperPause\n(?:[^\n]+\n)*?)anim = (?:100|-1|S[^\n]+)\n",
                          lambda mm: mm.group(1) + f"anim = {alvo}\n", novo)
        if (1000 <= n <= 1999 or (sobe and 3400 <= n <= 3403)) and 9240 in acoes:
            novo = re.sub(r"^sparkno = (?!-1\b)[^\n]+$", faisca(9240, 9270), novo, flags=re.M)
        elif 3000 <= n <= 3399 and 9241 in acoes:
            novo = re.sub(r"^sparkno = (?!-1\b)[^\n]+$", faisca(9241, 9271), novo, flags=re.M)
        elif n == 2000 and 9272 in acoes:
            pilar = (f"[State 2000, Pilar da transformação {MARCA}]\ntype = Explod\ntrigger1 = AnimTime = 0\n"
                     "anim = 9272\nid = 9272\npostype = p1\npos = 0, 0\nsprpriority = -2\nownpal = 1\n"
                     "removetime = -2\nbindtime = 1\nignorehitpause = 1\n\n")
            assert "[State 2000, Liga]" in novo, "estado 2000 sem o [State 2000, Liga]"
            novo = novo.replace("[State 2000, Liga]", pilar + "[State 2000, Liga]", 1)
        if sobe and n >= 0:
            novo = nivel(novo, n, lutador)
        if novo != bloco:
            trocas.append((m.start(), m.end(), novo))
    for a, b, novo in reversed(trocas):
        cns = cns[:a] + novo + cns[b:]
    return cns


# ---------------------------------------------------------------- .sff com PNG no tdata
NO = "<HHHHhhHBBIIHH"


def gravar(destino, pal, rle, png):
    """SFF v2.01: rle = [(g, i, w, h, x, y, pixels indexados)] no ldata (duplicata vira link, como o gravar_sff do
    gerador); png = [(g, i, w, h, x, y, blob com o tamanho na frente)] no tdata, formato 12 (PNG RGBA)."""
    ldata, tdata, nos, vistos = bytearray(pal), bytearray(), bytearray(), {}
    from gerar_pengaro import rle8
    for k, (g, i, w, h, x, y, px) in enumerate(rle):
        chave = (w, h, px)
        if chave in vistos:
            nos += struct.pack(NO, g, i, w, h, x, y, vistos[chave], 2, 8, 0, 0, 0, 0)
            continue
        vistos[chave] = k
        corpo = struct.pack("<I", len(px)) + rle8(px)
        nos += struct.pack(NO, g, i, w, h, x, y, 0, 2, 8, len(ldata), len(corpo), 0, 0)
        ldata += corpo
    for g, i, w, h, x, y, blob in png:
        nos += struct.pack(NO, g, i, w, h, x, y, 0, 12, 32, len(tdata), len(blob), 0, 1)
        tdata += blob
    n = len(rle) + len(png)
    ofs_pal, ofs_spr = 512, 512 + 32
    ofs_l = ofs_spr + len(nos)
    cab = bytearray(512)
    cab[0:12] = b"ElecbyteSpr\x00"
    cab[12:16] = bytes((0, 1, 0, 2))
    cab[24:28] = bytes((0, 1, 0, 2))
    struct.pack_into("<8I", cab, 36, ofs_spr, n, ofs_pal, 2, ofs_l, len(ldata), ofs_l + len(ldata), len(tdata))
    no_pal = struct.pack("<HHHHII", 1, 1, 256, 0, 0, 1024) + struct.pack("<HHHHII", 1, 2, 256, 0, 0, 1024)
    Path(destino).write_bytes(bytes(cab) + no_pal + bytes(nos) + bytes(ldata) + bytes(tdata))


def blob_png(img):
    return struct.pack("<I", img.width * img.height * 4) + png_rgba(img.width, img.height, img.tobytes())


# ---------------------------------------------------------------- .air
RE_ELEMENTO = re.compile(r"^\s*(\d+)\s*,\s*(\d+)\s*,", re.M)


def por_acao(air, numero, texto):
    bloco = f"[Begin Action {numero}]\n{texto.rstrip()}\n\n"
    padrao = rf"^\[Begin Action {numero}\][^\n]*\n.*?(?=^\[Begin Action|\Z)"
    if not re.search(padrao, air, re.M | re.S):
        return air.rstrip() + "\n\n" + bloco
    return re.sub(padrao, lambda m: bloco, air, count=1, flags=re.M | re.S)


def texto_acao(grupo, quadros, escala):
    linhas = []
    for i, (*_, ticks) in enumerate(quadros):
        linhas.append(f"{grupo},{i}, 0,0, {ticks}" + (f", , , {escala:g}, {escala:g}" if escala != 1 else ""))
    return "\n".join(linhas)


# ---------------------------------------------------------------- tudo
def aplicar(lutador, pasta=None):
    pasta = Path(pasta) if pasta else RAIZ / "chars" / lutador
    sff, arq_air, arq_cns = (pasta / f"{lutador}.{e}" for e in ("sff", "air", "cns"))
    air = arq_air.read_text(encoding="utf-8")
    cns = arq_cns.read_text(encoding="utf-8")
    acoes, escalas = efeitos_do(lutador)
    tem = set(int(n) for n in re.findall(r"^\[Begin Action (\d+)\]", air, re.M))
    blender = efeitos_blender(lutador)
    if lutador != "hazaki":  # o Hazak fica com o estouro de chamas dele (Blender, conversa da #44)
        blender = {a: q for a, q in blender.items() if a not in GRANDES}
    for acao in blender:
        tem.add(acao)
        escalas[acao] = ESCALA_BLENDER
    acoes.update(blender)
    if lutador != "hazaki":
        grandes, esc = efeitos_grandes(lutador)
        acoes.update(grandes)
        escalas.update(esc)
        tem.update(grandes)
    proj, esc_proj = efeitos_projeteis(lutador)
    cns = ligar_cns(cns, set(blender) | set(acoes), lutador == "hazaki", lutador)
    novos = {}
    for acao, quadros in acoes.items():
        if acao not in tem:
            continue  # o lutador não tem esse efeito (ex.: 9234 só em alguns)
        g = grupo_novo(acao)
        air = por_acao(air, acao, texto_acao(g, quadros, escalas[acao]))
        novos[g] = quadros
    for acao, quadros in proj.items():  # projéteis: grupo 83xx, só o desenho troca
        g = 8300 + acao % 100
        air = trocar_desenhos(air, acao, g, len(quadros), esc_proj[acao])
        novos[g] = quadros
    air = re.sub(r"\n{3,}", "\n\n", air)
    # o que fica: todo sprite que algum .air usa (e os destinos do remap), menos os grupos antigos dos efeitos
    import gerar_pengaro as gp
    usados = gp.sprites_mantidos(air, cns)
    pal, nos, _ = cs.ler(sff)
    rle, png, vistos = [], [], set()
    for n in nos:
        k = (n["g"], n["i"])
        if k in vistos or n["g"] in novos or (n["g"] in VELHOS and k not in usados):
            continue
        vistos.add(k)
        if n.get("png"):
            png.append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
        else:
            rle.append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
    for g, quadros in novos.items():
        for i, (img, ex, ey, _) in enumerate(quadros):
            png.append((g, i, img.width, img.height, int(ex), int(ey), blob_png(img)))
    gravar(sff, pal, rle, png)
    arq_air.write_text(air, encoding="utf-8", newline="\n")
    arq_cns.write_text(cns, encoding="utf-8", newline="\n")
    print(f"{lutador}: {len(blender)} efeitos do Blender; {len(novos) - len(blender)} efeitos pixelfx, {sum(len(q) for q in novos.values())} desenhos; "
          f"{len(rle) + len(png)} sprites no .sff")


# ---------------------------------------------------------------- folha para o Breno
NOMES = {"projetil": "projétil de energia / nuvem",
         "fraco": "fraco (ventinho)", "forte": "forte (estalo)", "final": "finalizador (impacto)",
         "defesa": "defesa", "rastro": "rastro do golpe", "poeira": "poeira no chão", "asfalto": "asfalto",
         "parry": "parry", "especial": "estouro de especial", "super": "explosão de super",
         "transformacao": "transformação (Blender)", "carga": "carga do especial",
         "carga_lenta": "carga da super"}


def folha(destino, lutadores=LUTADORES):
    """Uma imagem por lutador: cada linha é um efeito, quadro a quadro, em 3x, no tamanho do jogo (escala do .air)."""
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    z = 3
    for lutador in lutadores:
        acoes, escalas = efeitos_do(lutador)
        mapa = dict(HAZAK if lutador == "hazaki" else KIT)
        for acao, quadros in efeitos_blender(lutador).items():
            if lutador != "hazaki" and acao in GRANDES:
                continue
            acoes[acao] = quadros
            escalas[acao] = ESCALA_BLENDER
            mapa[acao] = ACOES_BLENDER[acao]
        if lutador != "hazaki":
            grandes, esc = efeitos_grandes(lutador)
            for acao, quadros in grandes.items():
                efeito, forma, ticks = GRANDES[acao][:3]
                acoes[acao], escalas[acao] = quadros, esc[acao]
                mapa[acao] = ("carga_lenta" if efeito == "carga" and ticks == 4 else efeito, forma)
        proj, esc = efeitos_projeteis(lutador)
        for acao, quadros in proj.items():
            acoes[acao], escalas[acao] = quadros, esc[acao]
            mapa[acao] = ("projetil", PROJETEIS[lutador][acao][3])
        linhas = []
        for acao, quadros in acoes.items():
            if acao == 9234:
                continue
            papel, forma = mapa[acao]
            e = escalas[acao] * z
            cel_w = int(max(max(ex, img.width - ex) for img, ex, ey, _ in quadros) * 2 * e) + 12
            cima = int(max(ey for img, ex, ey, _ in quadros) * e)
            baixo = int(max(img.height - ey for img, ex, ey, _ in quadros) * e)
            tira = Image.new("RGBA", (200 + cel_w * len(quadros), max(56, cima + baixo + 16)), (34, 38, 52, 255))
            d = ImageDraw.Draw(tira)
            d.text((6, 8), f"{acao}  {NOMES[papel]}", fill=(235, 235, 235))
            d.text((6, 24), {"desperto": "forma despertada", "fumaca": "fumaça"}.get(forma, "forma normal"),
                   fill=(170, 170, 190))
            for k, (img, ex, ey, t) in enumerate(quadros):
                q = img.resize((max(1, round(img.width * e)), max(1, round(img.height * e))), Image.NEAREST)
                cx, cy = 200 + k * cel_w + cel_w // 2, 8 + cima
                tira.alpha_composite(q, (cx - round(ex * e), cy - round(ey * e)))
                d.line((cx - 3, cy, cx + 3, cy), fill=(255, 60, 60)); d.line((cx, cy - 3, cx, cy + 3), fill=(255, 60, 60))
            linhas.append(tira)
        w = max(t.width for t in linhas)
        img = Image.new("RGBA", (w, sum(t.height + 2 for t in linhas) + 34), (20, 22, 30, 255))
        ImageDraw.Draw(img).text((8, 10), f"{lutador}: todos os efeitos de acerto no pixelfx; só a "
                                 "transformação é do Blender; cruz vermelha = ponto do golpe; 3x o tamanho do jogo", fill=(255, 255, 255))
        y = 34
        for t in linhas:
            img.alpha_composite(t, (0, y))
            y += t.height + 2
        img.convert("RGB").save(destino / f"efeitos_{lutador}.png")
        print(destino / f"efeitos_{lutador}.png")


def main():
    args = sys.argv[1:]
    if args[:1] == ["--folha"]:
        folha(args[1], args[2:] or LUTADORES)
        return
    for lutador in args or LUTADORES:
        aplicar(lutador)


if __name__ == "__main__":
    main()
