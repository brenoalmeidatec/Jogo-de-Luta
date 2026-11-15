#!/usr/bin/env python3
"""Monta o cenário do Cristo (Monumento Jesus de Nazaré, Morro do Silêncio) ao entardecer, issue #35.

  python3 ferramentas/cenario_cristo.py && python3 ferramentas/gerar_cenario.py cenarios/cristo/cenario.json

Projeto em docs/arcade/cenarios_nazare.md (seção 2), aqui na resolução da janela (localcoord 1280x720, como a Maria
Fumaça): as medidas do projeto (tela 320x180) vão x4. Arte bruta do ChatGPT em sprites/cenarios/cristo/bruto/ (branch
cenarios: céu, nuvens longe e perto, longe, morro, torres, cristo, cerca, chão) e a folha dos visitantes na escada em
sprites/cenarios/cristo/bruto/visitantes.png (chat "Cristo", conta do Alisson).
O que se mexe: nuvens em duas alturas, halo do sol pulsando, luzes da cidade lá embaixo piscando, pássaros planando,
farol vermelho das torres, holofote na estátua respirando e os visitantes subindo a escada.
"""
import json
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from cenario_katiara import alfa_duro, emendar, folha, sem_magenta

RAIZ = Path(__file__).resolve().parent.parent
BRUTO = RAIZ / "sprites" / "cenarios" / "cristo" / "bruto"
SAIDA = RAIZ / "cenarios" / "cristo"
LARGURA = 1800


def peca(nome):
    """Desenho do bruto sem o magenta, recortado na caixa do que tem."""
    im = sem_magenta(Image.open(BRUTO / f"{nome}.png"))
    return im.crop(im.getchannel("A").getbbox())


def no_tamanho(im, largura=None, altura=None):
    if largura is None:
        largura = round(im.width * altura / im.height)
    if altura is None:
        altura = round(im.height * largura / im.width)
    return alfa_duro(im.resize((largura, altura), Image.LANCZOS))


def faixa_sem_emenda(im, largura):
    """Faixa que repete na horizontal (nuvens, cerca): as peças do bruto já têm as pontas vazias ou no mesmo ponto."""
    return no_tamanho(im, largura=largura)


def pixel_quadrado(img, xy, lado, cor):
    d = ImageDraw.Draw(img)
    d.rectangle([xy[0], xy[1], xy[0] + lado - 1, xy[1] + lado - 1], fill=cor)


def halo_sol(n=8):
    """Halo somado em volta do sol (anéis em faixas, sem degradê liso), pulsando."""
    quadros = []
    for q in range(n):
        img = Image.new("RGBA", (256, 256), (0, 0, 0, 255))
        d = ImageDraw.Draw(img)
        puls = 6 * math.sin(2 * math.pi * q / n)
        for r, c in [(124, (28, 14, 4)), (100, (46, 24, 6)), (78, (70, 38, 10)), (58, (96, 56, 14))]:
            rr = r + puls
            d.ellipse([128 - rr, 128 - rr, 128 + rr, 128 + rr], fill=c + (255,))
        quadros.append(pixelar(img, 4))
    return quadros


def pixelar(img, k):
    return img.resize((img.width // k, img.height // k), Image.NEAREST).resize(img.size, Image.NEAREST)


def passaro(n=8):
    """Pássaro em silhueta (urubu planando), asa batendo devagar: 8 quadros de 48x24, pixel de 4."""
    asas = [[".....#.....#.....", "......#...#......", ".......###.......", "........#........"],
            ["...................", "##.....###.....##", "..#####...#####..", "........#........"],
            ["...................", ".................", "#######.#.#######", "........#........"],
            ["...................", ".................", "...#####.#####...", "#######.#.#######"]]
    ordem = [0, 1, 2, 3, 3, 2, 1, 0]
    quadros = []
    for q in range(n):
        img = Image.new("RGBA", (17 * 4, 6 * 4))
        for y, s in enumerate(asas[ordem[q]]):
            for x, ch in enumerate(s):
                if ch == "#":
                    pixel_quadrado(img, (x * 4, (y + 1) * 4), 4, (52, 34, 64, 255))
        quadros.append(img)
    return quadros


def farol(n_torres_xy):
    """Dois quadros (aceso, apagado) com um ponto vermelho somado no topo de cada torre."""
    w = max(x for x, _ in n_torres_xy) + 24
    h = max(y for _, y in n_torres_xy) + 24
    aceso = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    for x, y in n_torres_xy:
        d = ImageDraw.Draw(aceso)
        d.rectangle([x - 12, y - 12, x + 11, y + 11], fill=(60, 8, 4, 255))
        d.rectangle([x - 8, y - 8, x + 7, y + 7], fill=(150, 24, 12, 255))
        d.rectangle([x - 4, y - 4, x + 3, y + 3], fill=(255, 90, 60, 255))
    apagado = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    return [aceso, apagado]


def topos_das_torres(torres):
    """Ponta de cada torre: a coluna mais alta de cada grupo de colunas com desenho."""
    a = np.array(torres)[..., 3] > 0
    alto = np.array([np.argmax(c) if c.any() else 10 ** 6 for c in a.T])
    pontas = []
    x = 0
    while x < len(alto):
        if alto[x] < 10 ** 6:
            x0 = x
            while x < len(alto) and alto[x] < 10 ** 6:
                x += 1
            seg = alto[x0:x]
            i = int(np.argmin(seg))
            if seg[i] < a.shape[0] * 0.5:
                pontas.append((x0 + i, int(seg[i])))
        x += 1
    # torres encostadas viram um grupo só: separa pelos picos locais
    if len(pontas) < 3:
        picos = []
        for i in range(4, len(alto) - 4):
            if alto[i] < 10 ** 6 and alto[i] == alto[i - 4:i + 5].min() and alto[i] < a.shape[0] * 0.4:
                if not picos or i - picos[-1][0] > 20:
                    picos.append((i, int(alto[i])))
        pontas = picos
    return pontas


def holofote(cristo, n=8):
    """Luz somada saindo do terraço e subindo na estátua, respirando (faixas, sem degradê liso)."""
    w, h = cristo.size
    a = np.array(cristo)[..., 3] > 0
    quadros = []
    for q in range(n):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
        d = ImageDraw.Draw(img)
        k = 0.75 + 0.25 * math.sin(2 * math.pi * q / n)
        cx, base = w * 0.5, h * 0.70
        for larg, cor in [(0.30, (26, 22, 12)), (0.20, (44, 38, 20)), (0.11, (64, 56, 30))]:
            c = tuple(int(v * k) for v in cor) + (255,)
            d.polygon([(cx - w * 0.04, base), (cx + w * 0.04, base), (cx + w * larg, 0), (cx - w * larg, 0)], fill=c)
        m = np.array(img)
        m[~a] = (0, 0, 0, 255)  # a luz só pega na estátua e no terraço
        quadros.append(pixelar(Image.fromarray(m), 2))
    return quadros


def luzes_cidade(longe, n=16, seed=7):
    """Janelas acendendo e piscando no casario do longe (pontos somados)."""
    rnd = random.Random(seed)
    a = np.array(longe)
    h, w = a.shape[:2]
    r, g, b = (a[..., i].astype(int) for i in range(3))
    casa = (a[..., 3] > 0) & (r > 150) & (g > 90) & (b > 80) & (r > b + 20)  # paredes claras e telhados
    ys, xs = np.nonzero(casa)
    pts = [(int(xs[i]), int(ys[i])) for i in rnd.sample(range(len(xs)), min(60, len(xs)))] if len(xs) else []
    fases = [rnd.randrange(n) for _ in pts]
    quadros = []
    for q in range(n):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
        for (x, y), f in zip(pts, fases):
            if (q + f) % n < n * 0.7:
                pixel_quadrado(img, (x - x % 4, y - y % 4), 4, (120, 92, 30, 255))
        quadros.append(img)
    return quadros


def destruir(camadas):
    """Destruição em dois níveis (issue #35, 4.2). Nível 1: o morro de sempre com fogo no terraço, nas torres e na
    cidade lá embaixo, rachaduras no piso, os visitantes e os pássaros somem, o povo foge. Nível 2: o morro em ruínas
    (cena_destruida_larga.png: o Cristo inteiro em cima do pedestal rachado, o terraço quebrado, a escadaria
    desabando, uma torre torta, uma partida e uma caída, casas sem telhado, cerca quebrada, crateras)."""
    from cenario_destruicao import Destruicao
    for c in camadas:
        if c["nome"] == "visitantes" or c["nome"].startswith("passaro"):
            c["nivel"] = "0"
        elif c["nome"] in ("longe", "luzes", "morro", "torres", "farol", "cristo", "holofote", "cerca", "chao"):
            c["nivel"] = "<2"
    d = Destruicao(SAIDA)
    i_ceu = [c["nome"] for c in camadas].index("nuvens_perto") + 1
    ceus = [d.ceu(1, (16, 34, 50)), d.ceu(2, (40, 80, 110))]
    m = (LARGURA - 1280) // 2

    # ---- nível 1 (posições na tela em repouso; o delta de cada efeito é o da camada em que ele está) ----
    d.rachaduras(-m, 0, LARGURA, 720, [(x + m, y, c, a) for x, y, c, a in
                 [(330, 640, 260, 5), (900, 620, 240, 175), (1500, 650, 200, 10)]], 1, seed=3, achata=0.4,
                 torto=0.45, grosso=6)
    d.fogo_com_fumaca(90, 488, 44, 1, delta=0.35, seed=1)           # a cidade lá embaixo
    d.fogo_com_fumaca(1230, 474, 44, 1, delta=0.35, seed=2, fase=3)
    d.fogo_com_fumaca(470, 525, 80, 1, delta=0.7, seed=3, fase=5)   # o terraço do Cristo
    d.fogo_com_fumaca(840, 525, 70, 1, delta=0.7, seed=4, fase=2)
    d.fogo_com_fumaca(1010, 545, 80, 1, delta=0.7, seed=5, fase=6)  # o pé das torres
    d.peca("entulho_m", 250, 610, 100, 1)
    d.peca("entulho_p", 980, 600, 64, 1)
    d.correndo(0, 590, 240, 1, 6.5, -900, 2300)
    d.correndo(1, 596, 240, 1, -5.5, 2400, 3100)
    d.fagulhas(80, 1, seed=5, quantas=30)
    d.clarao_do_fogo(1, (26, 9, 0))
    nivel1 = d.camadas
    d.camadas = []

    # ---- nível 2: o morro em ruínas, uma peça só do tamanho do mundo ----
    ruina = sem_magenta(Image.open(BRUTO / "cena_destruida_larga.png"))
    k = LARGURA / ruina.width
    topo = 660 - round(640 * k)                 # o meio da praça de pedra (y 640) fica no pé dos lutadores
    alfa_duro(ruina.resize((LARGURA, round(ruina.height * k)), Image.LANCZOS)).save(SAIDA / "morro_ruina.png")
    base2 = {"nome": "morro_ruina", "imagem": "morro_ruina.png", "delta": [1, 1], "y": topo, "nivel": "2"}
    R = lambda x, y: (round(x * k) - m, topo + round(y * k))
    d.fogo_com_fumaca(*R(130, 450), 70, 2, seed=11)                 # casas sem telhado da esquerda
    d.fogo_com_fumaca(*R(330, 420), 60, 2, seed=12, fase=4)
    d.fogo_com_fumaca(*R(500, 330), 90, 2, seed=13, fase=2)         # o terraço quebrado
    d.fogo_com_fumaca(*R(1010, 430), 80, 2, seed=14, fase=6)
    d.fogo_com_fumaca(*R(1220, 340), 90, 2, seed=15, fase=1)        # o pé das torres
    d.fogo_com_fumaca(*R(1300, 420), 70, 2, seed=16, fase=3)        # a torre caída
    d.fogo_com_fumaca(*R(1830, 440), 70, 2, seed=17, fase=5)        # a cidade
    d.fogo_com_fumaca(*R(2000, 460), 70, 2, seed=18, fase=7)
    d.peca("caido_velho", *R(700, 0)[:1], R(0, 600)[1], 60, 2)
    d.peca("caida_amarela", *R(1500, 0)[:1], R(0, 606)[1], 58, 2, espelha=True)
    d.correndo(0, R(0, 585)[1], 240, 2, 7.5, -700, 1700)
    d.correndo(1, R(0, 590)[1], 240, 2, -6, 2200, 2300)
    d.correndo(0, R(0, 582)[1], 240, 2, -8, 3600, 2900)
    d.fagulhas(40, 2, seed=6, quantas=70, alto=520)
    d.clarao_do_fogo(2, (44, 14, 0))
    d.peca("caida_sacola", 40, 718, 80, 2, frente=True)
    nivel2 = d.camadas
    return (camadas[:i_ceu] + ceus + camadas[i_ceu:] + nivel1 + [base2] +
            [c for c in nivel2 if not c.get("frente")] + [c for c in nivel2 if c.get("frente")])


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    camadas = []

    ceu = Image.open(BRUTO / "ceu.png").convert("RGBA").resize((1280, 880), Image.NEAREST)
    ceu.save(SAIDA / "ceu.png")
    camadas.append({"nome": "ceu", "imagem": "ceu.png", "delta": [0, 0], "x": 0, "y": -160})
    emendar(halo_sol()).save(SAIDA / "sol.png")
    camadas.append({"nome": "sol", "folha": {"imagem": "sol.png", "n": 8}, "ticks": 10, "delta": [0, 0], "x": 16,
                    "y": 256, "mistura": "soma"})

    nl = faixa_sem_emenda(peca("nuvens_longe"), 1536)
    nl.save(SAIDA / "nuvens_longe.png")
    camadas.append({"nome": "nuvens_longe", "imagem": "nuvens_longe.png", "delta": [0.05, 0.05], "y": 236,
                    "velocidade": [-0.12, 0], "repete": [1, 0], "vao": [0, 0]})
    npt = faixa_sem_emenda(peca("nuvens_perto"), 1536)
    npt.save(SAIDA / "nuvens_perto.png")
    camadas.append({"nome": "nuvens_perto", "imagem": "nuvens_perto.png", "delta": [0.15, 0.15], "y": 40,
                    "velocidade": [-0.36, 0], "repete": [1, 0], "vao": [0, 0]})

    longe = no_tamanho(peca("longe"), largura=1912)
    longe.save(SAIDA / "longe.png")
    yl = 648 - longe.height
    camadas.append({"nome": "longe", "imagem": "longe.png", "delta": [0.35, 0.35], "y": yl})
    emendar(luzes_cidade(longe)).save(SAIDA / "luzes.png")
    camadas.append({"nome": "luzes", "folha": {"imagem": "luzes.png", "n": 16}, "ticks": 12,
                    "delta": [0.35, 0.35], "x": (1280 - longe.width) // 2, "y": yl, "mistura": "soma"})

    emendar(passaro()).save(SAIDA / "passaro.png")
    for i, (x, y, fase) in enumerate([(300, 150, 0), (420, 200, 140), (980, 120, 260)]):
        camadas.append({"nome": f"passaro{i + 1}", "folha": {"imagem": "passaro.png", "n": 8}, "ticks": 7 + i,
                        "delta": [0.3, 0.3], "x": x, "y": y, "seno_x": [160, 840, fase], "seno_y": [36, 420, fase]})

    morro = no_tamanho(peca("morro"), largura=2200)
    morro.save(SAIDA / "morro.png")
    camadas.append({"nome": "morro", "imagem": "morro.png", "delta": [0.7, 0.7], "y": 650 - morro.height})

    torres = no_tamanho(peca("torres"), altura=430)
    torres.save(SAIDA / "torres.png")
    xt, yt = 880, 600 - torres.height - 60
    camadas.append({"nome": "torres", "imagem": "torres.png", "delta": [0.7, 0.7], "x": xt, "y": yt})
    pontas = topos_das_torres(torres)
    if pontas:
        emendar(farol([(x + 12, y + 12) for x, y in pontas])).save(SAIDA / "farol.png")
        camadas.append({"nome": "farol", "folha": {"imagem": "farol.png", "n": 2}, "ticks": [40, 24],
                        "delta": [0.7, 0.7], "x": xt - 12, "y": yt - 12, "mistura": "soma"})

    cristo = no_tamanho(peca("cristo"), largura=600)
    cristo.save(SAIDA / "cristo.png")
    xc, yc = 340, 560 - cristo.height
    camadas.append({"nome": "cristo", "imagem": "cristo.png", "delta": [0.7, 0.7], "x": xc, "y": yc})
    emendar(holofote(cristo)).save(SAIDA / "holofote.png")
    camadas.append({"nome": "holofote", "folha": {"imagem": "holofote.png", "n": 8}, "ticks": 9,
                    "delta": [0.7, 0.7], "x": xc, "y": yc, "mistura": "soma"})
    if (BRUTO / "visitantes.png").exists():
        vq = folha(BRUTO / "visitantes.png", 8)
        alto = round(cristo.height * 0.36)
        vq = [no_tamanho(q, altura=alto) for q in vq]
        emendar(vq).save(SAIDA / "visitantes.png")
        # a escada dos visitantes fica encostada na ponta direita do terraço
        camadas.append({"nome": "visitantes", "folha": {"imagem": "visitantes.png", "n": 8}, "ticks": 14,
                        "delta": [0.7, 0.7], "x": xc + cristo.width - 30, "y": yc + cristo.height - alto})

    cerca = faixa_sem_emenda(peca("cerca"), 540)
    cerca.save(SAIDA / "cerca.png")
    camadas.append({"nome": "cerca", "imagem": "cerca.png", "delta": [1, 1], "y": 572 - cerca.height,
                    "repete": [1, 0], "vao": [0, 0]})
    chao = peca("chao")
    chao = chao.crop((48, 0, chao.width - 48, chao.height))  # as pontas do bruto são mais escuras: viravam emenda
    # uma peça só, esticada na largura do mundo: as lajotas em perspectiva não emendam lado a lado
    chao = alfa_duro(chao.resize((LARGURA + 40, round(chao.height * 1024 / chao.width)), Image.LANCZOS))
    chao.save(SAIDA / "chao.png")
    camadas.append({"nome": "chao", "imagem": "chao.png", "delta": [1, 1], "y": 548})

    camadas = destruir(camadas)
    desc = {"id": "cristo", "nome": "Cristo", "musica": "musicas/cristo.ogg", "musica_nome": "Cenário Cristo",
            "tela": [1280, 720], "largura_mundo": LARGURA, "subida": 160, "chao_y": 660,
            "camera": {"tensao": 200, "segue_vertical": 0.6, "tensao_chao": 120},
            "jogadores": {"p1x": -280, "p2x": 280, "margem_tela": 60}, "reflexo": 0, "camadas": camadas}
    (SAIDA / "cenario.json").write_text(json.dumps(desc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("cenarios/cristo pronto:", [c["nome"] for c in camadas], "torres:", pontas)


if __name__ == "__main__":
    main()
