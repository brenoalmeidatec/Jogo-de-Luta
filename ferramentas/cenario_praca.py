#!/usr/bin/env python3
"""Monta o cenário da Praça da Prefeitura (Praça Alexandre Bittencourt) numa manhã de sol, issue #35.

  cd ferramentas && python3 cenario_praca.py && cd .. && python3 ferramentas/gerar_cenario.py cenarios/praca/cenario.json

Projeto em docs/arcade/cenarios_nazare.md (seção 4, branch cenarios). Para gastar pouco do plano do ChatGPT a arte veio
em poucas imagens (chat "Pixel Art Background Request", conta do Alisson), em sprites/cenarios/praca/bruto/:
  cena.png       prefeitura verde, Igreja Matriz com o sino, casario, morros, canteiros azuis, busto e o piso;
                 céu magenta (vira transparente)
  ceu.png        céu de manhã em faixas com cúmulos (as nuvens são separadas e andam)
  ambulante.png  folha de 8 quadros do ambulante com o carrinho de fruta (opcional)
  ciclista.png   folha de 8 quadros do ciclista passando (opcional)
O resto é desenhado aqui: as três bandeiras (Bahia, Brasil e uma do município) tremulando nos mastros que a arte
deixou vazios, o sino da Matriz balançando, pombos cruzando o céu e pombos ciscando no chão, na frente dos lutadores.
Tudo na resolução da janela (localcoord 1280x720), como a Maria Fumaça e a Katiara.
"""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

from cenario_katiara import alfa_duro, emendar, folha, magenta

RAIZ = Path(__file__).resolve().parent.parent
BRUTO = RAIZ / "sprites" / "cenarios" / "praca" / "bruto"
SAIDA = RAIZ / "cenarios" / "praca"
ESCALA = 0.95
PES_NA_CENA = 880        # y da cena original onde ficam os pés (no piso, depois do meio-fio azul em 785)
CHAO_Y = 660
LARGURA = round(1536 * ESCALA) // 2 * 2
TOPO = CHAO_Y - round(PES_NA_CENA * ESCALA)
MARGEM = (LARGURA - 1280) // 2

MASTROS = [(714, 412, "bahia"), (768, 392, "brasil"), (821, 412, "municipio")]  # topo de cada mastro na cena
SINO = (1346, 166, 1390, 244)   # vão do sino da Matriz na cena (x0, y0, x1, y1)
SINO_X = (1351, 1384)           # largura do sino (a viga passa dos lados e fica parada)
SINO_EIXO = (1367, 182)


def na_tela(x, y):
    return round(x * ESCALA) - MARGEM, TOPO + round(y * ESCALA)


def pixels(grade, cores, p):
    """Desenha uma grade de letras em pixel de p x p."""
    h, w = len(grade), max(len(s) for s in grade)
    img = Image.new("RGBA", (w * p, h * p))
    px = img.load()
    for y, s in enumerate(grade):
        for x, ch in enumerate(s):
            if ch in cores:
                for dy in range(p):
                    for dx in range(p):
                        px[x * p + dx, y * p + dy] = cores[ch]
    return img


def desenho_bandeira(tipo):
    """Bandeira parada em 16x11 células (cada célula vira 3 px na tela)."""
    W, H = 16, 11
    g = [["w"] * W for _ in range(H)]
    if tipo == "brasil":
        for y in range(H):
            for x in range(W):
                g[y][x] = "g"
                if abs(x - 7.5) / 7.5 + abs(y - 5) / 5 <= 0.95:
                    g[y][x] = "y"
                if (x - 7.5) ** 2 + ((y - 5) * 1.1) ** 2 <= 10:
                    g[y][x] = "b"
        for x in range(5, 11):
            g[5 if x < 8 else 4][x] = "w"
    elif tipo == "bahia":
        for y in range(H):
            for x in range(W):
                g[y][x] = "w" if (y * 4 // H) % 2 == 0 else "r"
                if x < 6 and y < 6:
                    g[y][x] = "b"
        for y, (a, b) in enumerate([(2, 3), (2, 3), (1, 4), (1, 4)], start=1):
            for x in range(a, b + 1):
                g[y][x] = "w"
    else:  # município: branca com o brasão verde e amarelo no meio
        for y in range(H):
            for x in range(W):
                d = (x - 7.5) ** 2 + ((y - 5) * 1.15) ** 2
                if d <= 7:
                    g[y][x] = "y"
                elif d <= 13:
                    g[y][x] = "g"
        for x in range(W):
            g[0][x] = g[H - 1][x] = "g"
    return g


CORES_BAND = {"w": (244, 240, 226), "g": (38, 150, 72), "y": (244, 204, 48), "b": (36, 64, 170),
              "r": (204, 44, 52)}


def bandeira(tipo, n=8, p=3):
    """8 quadros da bandeira tremulando: cada coluna sobe e desce numa onda que sai do mastro, com sombra nas dobras."""
    g = desenho_bandeira(tipo)
    W, H = len(g[0]), len(g)
    quadros = []
    for q in range(n):
        img = Image.new("RGBA", (W * p, (H + 4) * p))
        px = img.load()
        for x in range(W):
            fase = 2 * math.pi * q / n - x * 0.55
            dy = round(1.6 * math.sin(fase) * (x / W) ** 0.8)
            sombra = math.cos(fase) * min(1.0, x / 4)
            k = 1 - 0.22 * max(0.0, sombra)
            for y in range(H):
                c = CORES_BAND[g[y][x]]
                c = tuple(int(v * k) for v in c) + (255,)
                yy = y + 1 + dy
                for ddy in range(p):
                    for ddx in range(p):
                        px[x * p + ddx, yy * p + ddy] = c
        quadros.append(img)
    return quadros


def sino(cena, n=8):
    """O sino balançando no vão da torre: o vão (com o sino apagado) mais o sino girado em volta do eixo."""
    x0, y0, x1, y1 = SINO
    vao = np.array(cena.crop(SINO)).copy()
    r, g, b = (vao[..., i].astype(int) for i in range(3))
    dourado = (r > 120) & (r > b + 50) & (g > 70)
    col = np.zeros_like(dourado)
    col[:, SINO_X[0] - x0:SINO_X[1] - x0] = True
    corpo = dourado & col
    # o vão atrás do sino é escuro: cor mais comum entre os pixels escuros
    escuro = vao[(r + g + b) < 150][:, :3]
    fundo = tuple(int(v) for v in np.median(escuro, axis=0)) if len(escuro) else (30, 24, 20)
    base = vao.copy()
    base[corpo, :3] = fundo
    peca = np.zeros_like(vao)
    peca[corpo] = vao[corpo]
    peca_img = Image.fromarray(peca)
    eixo = (SINO_EIXO[0] - x0, SINO_EIXO[1] - y0)
    quadros = []
    for q in range(n):
        ang = 14 * math.sin(2 * math.pi * q / n)
        girado = peca_img.rotate(ang, resample=Image.NEAREST, center=eixo)
        f = Image.fromarray(base.copy())
        f.alpha_composite(girado)
        quadros.append(f)
    return quadros


PALETA_POMBO = {"k": (54, 56, 70, 255), "c": (128, 134, 150, 255), "l": (178, 184, 196, 255),
                "v": (92, 140, 120, 255), "o": (230, 120, 60, 255), "p": (220, 120, 130, 255)}


def pombo_voando(n=8):
    asas = [
        ["....kk......", "...kllk.....", "...kllk.....", ".kcclllck...", "kcccvccccckk", ".kkcccckk...", "...p..p....."],
        ["............", "............", "..kkllk.....", "kcclllllkk..", "kcccvccccckk", ".kkcccckk...", "...p..p....."],
        ["............", "............", "............", ".kcccvcccckk", "kcclllllcck.", "..kllllk....", "...kllk....."],
        ["............", "............", "..kkllk.....", "kcclllllkk..", "kcccvccccckk", ".kkcccckk...", "...p..p....."],
    ]
    ordem = [0, 1, 2, 2, 3, 0, 0, 1]
    return [pixels(asas[i], PALETA_POMBO, 4) for i in ordem]


def pombos_ciscando(n=8):
    """Dois pombos no chão: um bica, o outro anda a cabeça para a frente e para trás (fora de fase)."""
    em_pe = ["..kk......", ".kclk.....", "okcck.....", "..kcvccck.", "..kcccccck", "...kcccck.", "....p..p.."]
    bica = ["..........", "..........", "..........", "..kcvccck.", "okkccccckk", ".kclccck..", "....p..p.."]
    meio = ["..........", "..kk......", ".kclk.....", "okcvcccck.", "..kcccccck", "...kcccck.", "....p..p.."]
    seq_a = [em_pe, em_pe, meio, bica, bica, meio, em_pe, em_pe]
    seq_b = [meio, bica, bica, meio, em_pe, em_pe, em_pe, meio]
    quadros = []
    for q in range(n):
        a = pixels(seq_a[q], PALETA_POMBO, 4)
        b = pixels(seq_b[q], PALETA_POMBO, 4).transpose(Image.FLIP_LEFT_RIGHT)
        img = Image.new("RGBA", (a.width + b.width + 40, a.height))
        img.paste(a, (0, 0))
        img.paste(b, (a.width + 40, 0))
        quadros.append(img)
    return quadros


def cena_sem_magenta(img):
    """Como o sem_magenta da Katiara, mas a buganvília é rosa-choque e caía no mesmo filtro: só vira transparente o
    magenta grande (o céu) ou o que é magenta puro (os vãos da balaustrada)."""
    import cv2
    a = np.array(img.convert("RGBA"))
    m = magenta(a)
    n_, rot, dados, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    r, g, b = (a[..., i].astype(int) for i in range(3))
    puro = (np.abs(r - b) < 28) & (b > 215) & (g < 70)
    fundo = np.zeros_like(m)
    for i in range(1, n_):
        # a buganvília fica toda abaixo de y 600: o magenta de cima é sempre céu (inclusive os vãos da balaustrada)
        if dados[i, cv2.CC_STAT_AREA] > 3000 or dados[i, cv2.CC_STAT_TOP] < 560:
            fundo |= rot == i
    fundo |= m & puro
    # nos vãos da balaustrada o ChatGPT deixou um magenta sombreado (mais escuro) que o filtro não pega
    rosado = (g < 0.6 * np.minimum(r, b)) & (r > 110) & (b > 90)
    rosado[300:] = False
    fundo |= rosado
    a[fundo, 3] = 0
    perto = cv2.dilate(fundo.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~fundo
    rosa = perto & (r > 150) & (b > 120) & (g < 0.65 * np.minimum(r, b))
    a[rosa, 3] = 0
    return Image.fromarray(a)


def ceu_e_nuvens(ceu):
    """Céu em faixas paradas e as nuvens à parte. A cor da faixa é a mais comum entre os pixels azuis da linha (nas
    linhas cheias de nuvem a cor mais comum era o branco e o céu saía branco)."""
    a = np.array(ceu.convert("RGBA")).astype(int)
    fundo = a.copy()
    nuvem = np.zeros_like(a)
    ult = None
    for y in range(a.shape[0]):
        linha = a[y, :, :3]
        azul = (linha[:, 2] - linha[:, 0]) > 60
        if azul.sum() > 20:
            cores, cont = np.unique(linha[azul], axis=0, return_counts=True)
            ult = cores[cont.argmax()]
        moda = ult if ult is not None else np.array([63, 143, 224])
        dif = np.abs(linha - moda).sum(axis=1) > 40
        nuvem[y, dif] = a[y, dif]
        fundo[y, :, :3] = moda
    return Image.fromarray(fundo.astype(np.uint8)), Image.fromarray(nuvem.astype(np.uint8))


def com_1024(img):
    if img.height >= 1024:
        return img
    c2 = Image.new("RGBA", (img.width, 1024))
    c2.paste(img, (0, 0))
    c2.paste(img.crop((0, img.height - 1, img.width, img.height)).resize((img.width, 1024 - img.height)),
             (0, img.height))
    return c2


def nuvens_sem_ponta(nuv):
    """Tira as nuvens cortadas na borda da imagem: a faixa repete e elas virariam um corte seco no céu."""
    import cv2
    a = np.array(nuv)
    n_, rot, dados, _ = cv2.connectedComponentsWithStats((a[..., 3] > 0).astype(np.uint8), connectivity=8)
    for i in range(1, n_):
        x, w = dados[i, cv2.CC_STAT_LEFT], dados[i, cv2.CC_STAT_WIDTH]
        if x <= 1 or x + w >= a.shape[1] - 1 or dados[i, cv2.CC_STAT_AREA] < 60:
            a[rot == i, 3] = 0
    return Image.fromarray(a)


def apara(quadros):
    """Corta a sobra comum dos quadros: linha e coluna só contam com 8 px de desenho ou mais (a costura das capturas
    deixa um risco de 1 px que esticava a caixa até embaixo e deixava o ambulante flutuando)."""
    import cv2
    limpos = []
    for q in quadros:
        a = np.array(q)
        n_, rot, dados, _ = cv2.connectedComponentsWithStats((a[..., 3] > 0).astype(np.uint8), connectivity=4)
        for i in range(1, n_):
            if dados[i, cv2.CC_STAT_WIDTH] <= 3 or dados[i, cv2.CC_STAT_AREA] < 200:
                a[rot == i, 3] = 0
        limpos.append(a)
    tot = sum((a[..., 3] > 0).astype(int) for a in limpos)
    ys, xs = np.nonzero(tot.max(axis=1) > 0)[0], np.nonzero(tot.max(axis=0) > 0)[0]
    lin = np.nonzero((tot > 0).sum(axis=1) >= 8)[0]
    col = np.nonzero((tot > 0).sum(axis=0) >= 8)[0]
    caixa = (col[0], lin[0], col[-1] + 1, lin[-1] + 1)
    del ys, xs
    return [Image.fromarray(a).crop(caixa) for a in limpos]


def escala(img, k=ESCALA):
    return img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    cena = com_1024(cena_sem_magenta(Image.open(BRUTO / "cena.png")))
    camadas = []

    ceu_fundo, ceu_nuvens = ceu_e_nuvens(com_1024(Image.open(BRUTO / "ceu.png").convert("RGBA")))
    ceu_alto = 720 + 160 + 40
    ceu_fundo.resize((1280, ceu_alto), Image.NEAREST).save(SAIDA / "ceu.png")
    nuvens_sem_ponta(ceu_nuvens).resize((1536, ceu_alto), Image.NEAREST).save(SAIDA / "nuvens.png")
    camadas += [
        {"nome": "ceu", "imagem": "ceu.png", "delta": [0, 0], "x": 0, "y": -200},
        {"nome": "nuvens", "imagem": "nuvens.png", "delta": [0.1, 0.1], "y": -200, "velocidade": [-0.18, 0],
         "repete": [1, 0], "vao": [0, 0]},
    ]

    emendar(pombo_voando()).save(SAIDA / "pombo.png")
    for i, (y, vel, vao, fase) in enumerate([(70, 1.6, 2600, 0), (130, 1.25, 3400, 90), (40, 1.9, 4200, 200)]):
        camadas.append({"nome": f"pombo{i + 1}", "folha": {"imagem": "pombo.png", "n": 8}, "ticks": 3 + i % 2,
                        "delta": [0.8, 0.8], "x": -400 - 900 * i, "y": y, "velocidade": [vel, 0],
                        "repete": [1, 0], "vao": [vao, 0], "seno_y": [14, 120, fase]})

    escala(alfa_duro(cena)).save(SAIDA / "praca.png")
    camadas.append({"nome": "praca", "imagem": "praca.png", "delta": [1, 1], "y": TOPO})

    sq = [alfa_duro(escala(q)) for q in sino(cena)]
    emendar(sq).save(SAIDA / "sino.png")
    sx, sy = na_tela(SINO[0], SINO[1])
    camadas.append({"nome": "sino", "folha": {"imagem": "sino.png", "n": 8}, "ticks": 7, "delta": [1, 1],
                    "x": sx, "y": sy})

    for x, y, tipo in MASTROS:
        bq = bandeira(tipo)
        emendar(bq).save(SAIDA / f"bandeira_{tipo}.png")
        bx, by = na_tela(x, y)
        camadas.append({"nome": f"bandeira_{tipo}", "folha": {"imagem": f"bandeira_{tipo}.png", "n": 8},
                        "ticks": 5, "delta": [1, 1], "x": bx + 3, "y": by})

    if (BRUTO / "ambulante.png").exists():
        aq = apara(folha(BRUTO / "ambulante.png", 8, linhas=False))
        alto = 300
        aq = [alfa_duro(q.resize((round(q.width * alto / q.height), alto), Image.LANCZOS)) for q in aq]
        emendar(aq).save(SAIDA / "ambulante.png")
        # na ponta esquerda, no piso entre a casa azul e o poste (aparece com a câmera para a esquerda)
        camadas.append({"nome": "ambulante", "folha": {"imagem": "ambulante.png", "n": 8}, "ticks": 8,
                        "delta": [1, 1], "x": -MARGEM + 20, "y": TOPO + round(800 * ESCALA) - alto + 30})
    if (BRUTO / "ciclista.png").exists():
        cq = apara(folha(BRUTO / "ciclista.png", 8, linhas=False))
        alto = 250
        cq = [alfa_duro(q.resize((round(q.width * alto / q.height), alto), Image.LANCZOS)) for q in cq]
        emendar(cq).save(SAIDA / "ciclista.png")
        camadas.append({"nome": "ciclista", "folha": {"imagem": "ciclista.png", "n": 8}, "ticks": 4,
                        "delta": [1, 1], "x": -1400, "y": TOPO + round(810 * ESCALA) - alto,
                        "velocidade": [1.8, 0], "repete": [1, 0], "vao": [14000, 0]})

    emendar(pombos_ciscando()).save(SAIDA / "pombos_chao.png")
    for i, (x, fase) in enumerate([(120, 0), (980, 3)]):
        camadas.append({"nome": f"pombos_chao{i + 1}", "folha": {"imagem": "pombos_chao.png", "n": 8},
                        "ticks": [8, 6, 5, 9, 7, 6, 10, 8][fase:] + [8, 6, 5, 9, 7, 6, 10, 8][:fase],
                        "delta": [1.15, 1.15], "x": x, "y": 652, "frente": True})

    desc = {"id": "praca", "nome": "Praça", "musica": "musicas/praca.ogg", "musica_nome": "Cenário Praça",
            "tela": [1280, 720], "largura_mundo": LARGURA, "subida": 160, "chao_y": CHAO_Y,
            "camera": {"tensao": 200, "segue_vertical": 0.6, "tensao_chao": 120},
            "jogadores": {"p1x": -280, "p2x": 280, "margem_tela": 60}, "reflexo": 0, "camadas": camadas}
    (SAIDA / "cenario.json").write_text(json.dumps(desc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("cenarios/praca pronto:", [c["nome"] for c in camadas])


if __name__ == "__main__":
    main()
