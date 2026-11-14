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


def pintar(img, r, corte=190, luz_min=0.0):
    """Pinta em degraus: o brilho do pixel escolhe o tom da rampa, sem mistura. Pixel com alfa < corte sai (halo)."""
    a = np.asarray(img).astype(np.float32)
    luz = (0.30 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]) / 255
    luz = np.clip(luz * 1.08, 0, 1) ** 1.8  # gamma: o meio-tom desce na rampa e só o miolo fica quase branco
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
ESCALA = {"fraco": .6, "forte": .75, "final": 1.0, "defesa": .55, "rastro": .9, "poeira": .8, "asfalto": 1.25,
          "parry": .5}
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
            saida.append((img.crop(cx), px - cx[0], pivo[1] - cx[1], 2))
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
        saida.append((img.crop(cx), pivo[0] - cx[0], pivo[1] - cx[1], t))
    return saida


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
VELHOS = {9200, 9201, 9202, 9205, 9207, 9208, 9209, 9212, 9213, 9214, 9215, 9216, 9230, 9231, 9232, 9234, 9235,
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
    novos = {}
    for acao, quadros in acoes.items():
        if acao not in tem:
            continue  # o lutador não tem esse efeito (ex.: 9234 só em alguns)
        g = grupo_novo(acao)
        air = por_acao(air, acao, texto_acao(g, quadros, escalas[acao]))
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
    print(f"{lutador}: {len(novos)} efeitos pixelfx, {sum(len(q) for q in novos.values())} desenhos; "
          f"{len(rle) + len(png)} sprites no .sff")


# ---------------------------------------------------------------- folha para o Breno
NOMES = {"fraco": "fraco (ventinho)", "forte": "forte (estalo)", "final": "finalizador (impacto)",
         "defesa": "defesa", "rastro": "rastro do golpe", "poeira": "poeira no chão", "asfalto": "asfalto",
         "parry": "parry"}


def folha(destino, lutadores=LUTADORES):
    """Uma imagem por lutador: cada linha é um efeito, quadro a quadro, em 3x, no tamanho do jogo (escala do .air)."""
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    z = 3
    for lutador in lutadores:
        acoes, escalas = efeitos_do(lutador)
        mapa = HAZAK if lutador == "hazaki" else KIT
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
            d.text((6, 24), "forma despertada" if forma == "desperto" else "forma normal", fill=(170, 170, 190))
            for k, (img, ex, ey, t) in enumerate(quadros):
                q = img.resize((max(1, round(img.width * e)), max(1, round(img.height * e))), Image.NEAREST)
                cx, cy = 200 + k * cel_w + cel_w // 2, 8 + cima
                tira.alpha_composite(q, (cx - round(ex * e), cy - round(ey * e)))
                d.line((cx - 3, cy, cx + 3, cy), fill=(255, 60, 60)); d.line((cx, cy - 3, cx, cy + 3), fill=(255, 60, 60))
            linhas.append(tira)
        w = max(t.width for t in linhas)
        img = Image.new("RGBA", (w, sum(t.height + 2 for t in linhas) + 34), (20, 22, 30, 255))
        ImageDraw.Draw(img).text((8, 10), f"{lutador}: efeitos pixelfx dos golpes normais (cruz vermelha = ponto do "
                                 "golpe; 3x o tamanho do jogo)", fill=(255, 255, 255))
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
