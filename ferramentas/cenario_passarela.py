#!/usr/bin/env python3
"""Monta o cenário da Passarela (beira do rio Jaguaripe, passarela branca para a Ilha das Cobras) ao amanhecer, issue #35.

  cd ferramentas && python3 cenario_passarela.py && cd .. && python3 ferramentas/gerar_cenario.py cenarios/passarela/cenario.json

Projeto em docs/arcade/cenarios_nazare.md (seção 5, branch cenarios). Arte do ChatGPT (chat "Pixel Art Background
Request", conta do Alisson) em sprites/cenarios/passarela/bruto/:
  cena.png    calçadão com a ciclofaixa vermelha, guarda-corpo, dois lampiões acesos, o rio, a passarela coberta saindo
              pela direita, a outra margem com casas, coqueiros, morros e a chaminé; céu magenta (vira transparente)
  ceu.png     céu do amanhecer em faixas, com nuvens finas (o sol do desenho fica de fora: o sol daqui é desenhado
              por código, logo acima dos morros)
  canoa.png   folha de 8 quadros do pescador remando na canoa (opcional)
O que se mexe: nuvens finas, o sol nascendo com o halo pulsando, garça cruzando o céu, a água do rio ondulando
(as linhas da água andam de lado, fora de fase), o reflexo do sol tremendo na água, duas faixas de neblina andando em
sentidos opostos, a canoa a remo passando, os lampiões ainda acesos tremendo a luz e uma neblina rasteira na frente.
Tudo na resolução da janela (localcoord 1280x720), como a Maria Fumaça.
"""
import json
import math
import random
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from cenario_katiara import alfa_duro, emendar, folha, magenta
from cenario_praca import apara, pixels

RAIZ = Path(__file__).resolve().parent.parent
BRUTO = RAIZ / "sprites" / "cenarios" / "passarela" / "bruto"
SAIDA = RAIZ / "cenarios" / "passarela"
ESCALA = 0.95
PES_NA_CENA = 900        # logo depois da ciclofaixa vermelha (830 a 880 na cena)
CHAO_Y = 660
LARGURA = round(1536 * ESCALA) // 2 * 2
TOPO = CHAO_Y - round(PES_NA_CENA * ESCALA)
MARGEM = (LARGURA - 1280) // 2

AGUA_Y = (536, 668)      # faixa do rio na cena (da mureta da outra margem ao guarda-corpo)
AGUA_X1 = 1338           # dali para a direita é a escada da passarela
# caixas que não são água dentro da faixa (poste e lanternas dos lampiões, pilares da passarela)
OBSTACULOS = [(290, 470, 326, 668), (232, 470, 384, 566), (1212, 470, 1248, 668), (1156, 470, 1306, 566),
              (1108, 488, 1188, 600), (1290, 530, 1346, 630)]
LAMPIOES = [(258, 512), (356, 512), (1180, 512), (1280, 512)]   # centro de cada lanterna acesa na cena
SOL = (150, 64)          # centro do sol na tela, logo acima dos morros da esquerda


def na_tela(x, y):
    return round(x * ESCALA) - MARGEM, TOPO + round(y * ESCALA)


def escala(img, k=ESCALA):
    return img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)


def largura_1536(img):
    if img.width >= 1536:
        return img
    out = Image.new(img.mode, (1536, img.height))
    out.paste(img, (0, 0))
    out.paste(img.crop((img.width - 1, 0, img.width, img.height)).resize((1536 - img.width, img.height)),
              (img.width, 0))
    return out


def com_1024(img):
    if img.height >= 1024:
        return img
    out = Image.new(img.mode, (img.width, 1024))
    out.paste(img, (0, 0))
    out.paste(img.crop((0, img.height - 1, img.width, img.height)).resize((img.width, 1024 - img.height)),
              (0, img.height))
    return out


def cena_sem_ceu(img):
    """Só o magenta do céu (componente grande que começa lá em cima) vira transparente: o rio tem reflexo rosa."""
    a = np.array(img.convert("RGBA"))
    m = magenta(a)
    n_, rot, dados, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    fundo = np.zeros_like(m)
    for i in range(1, n_):
        if dados[i, cv2.CC_STAT_TOP] < 380:
            fundo |= rot == i
    a[fundo, 3] = 0
    r, g, b = (a[..., i].astype(int) for i in range(3))
    perto = cv2.dilate(fundo.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~fundo
    rosa = perto & (r > 150) & (b > 120) & (g < 0.65 * np.minimum(r, b))
    a[rosa, 3] = 0
    return Image.fromarray(a)


def mascara_agua(a):
    """Onde é água na faixa do rio: tira o verde das baronesas, o claro dos pilares, o escuro do poste e as caixas."""
    h, w = a.shape[:2]
    y0, y1 = AGUA_Y
    m = np.zeros((h, w), bool)
    m[y0:y1, :AGUA_X1] = True
    r, g, b = (a[..., i].astype(int) for i in range(3))
    verde = (g > r + 8) & (g > b)
    pilar = (r > 150) & (g > 135) & (r - g < 40) & (b < g + 5) & (r - b > 15)
    escuro = (r + g + b) < 110
    lanterna = (r > 190) & (g > 150) & (b < 120)
    m &= ~(verde | pilar | escuro | lanterna)
    for x0, yy0, x1, yy1 in OBSTACULOS:
        m[yy0:yy1, x0:x1] = False
    # baronesas: o verde tem flor roxa e borda escura no meio: alarga um pouco o buraco
    tira = cv2.dilate((verde & (np.arange(h)[:, None] >= y0)).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    m &= ~tira
    return m


def agua(cena, n=8):
    """Quadros da água: cada linha da faixa anda de lado num seno (o reflexo ondula); só nos pixels de água."""
    a = np.array(cena)
    m = mascara_agua(a)
    y0, y1 = AGUA_Y
    faixa = a[y0:y1].copy()
    mf = m[y0:y1]
    # o que não é água vira água em volta (inpaint), para o deslocamento não arrastar poste e baronesa
    cor = cv2.inpaint(np.ascontiguousarray(faixa[..., :3]), (~mf).astype(np.uint8) * 255, 5, cv2.INPAINT_TELEA)
    quadros = []
    for q in range(n):
        f = np.zeros_like(faixa)
        for y in range(faixa.shape[0]):
            k = (y / faixa.shape[0])
            dx = int(round((2 + 4 * k) * math.sin(2 * math.pi * q / n + y * 0.55)))
            f[y, :, :3] = np.roll(cor[y], dx, axis=0)
        f[..., 3] = np.where(mf, 255, 0)
        quadros.append(Image.fromarray(f))
    return quadros, m


def halo(n=8, raio=110, cores=((34, 22, 10), (56, 36, 14), (84, 56, 20), (120, 84, 30))):
    quadros = []
    for q in range(n):
        img = Image.new("RGBA", (raio * 2 + 16, raio * 2 + 16), (0, 0, 0, 255))
        d = ImageDraw.Draw(img)
        c = img.width / 2
        puls = 0.06 * math.sin(2 * math.pi * q / n)
        for i, cor in enumerate(cores):
            rr = raio * (1 - i / len(cores) * 0.75) * (1 + puls)
            d.ellipse([c - rr, c - rr, c + rr, c + rr], fill=cor + (255,))
        quadros.append(img.resize((img.width // 4, img.height // 4), Image.NEAREST).resize(img.size, Image.NEAREST))
    return quadros


def disco_sol(raio=34):
    img = Image.new("RGBA", (raio * 2 + 8, raio * 2 + 8))
    d = ImageDraw.Draw(img)
    c = img.width / 2
    d.ellipse([c - raio, c - raio, c + raio, c + raio], fill=(255, 236, 170, 255))
    d.ellipse([c - raio * 0.7, c - raio * 0.7, c + raio * 0.7, c + raio * 0.7], fill=(255, 246, 206, 255))
    return img.resize((img.width // 4, img.height // 4), Image.NEAREST).resize(img.size, Image.NEAREST)


def reflexo_sol(mask_tela, n=8, seed=3):
    """Coluna de brilhos somados embaixo do sol, tremendo (pedacinhos de linha que acendem e apagam)."""
    rnd = random.Random(seed)
    w, h = 90, mask_tela.shape[0]
    quadros = []
    tracos = [(rnd.randrange(h // 4) * 4, rnd.randrange(-30, 30), rnd.randrange(8, 28), rnd.randrange(n))
              for _ in range(46)]
    for q in range(n):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
        d = ImageDraw.Draw(img)
        for y, dx, L, f in tracos:
            larg = L * (0.4 + y / h)
            if (q + f) % n < 5:
                x = w / 2 + dx * (0.3 + y / h) + 3 * math.sin(2 * math.pi * (q + f) / n)
                c = (110, 76, 34, 255) if (q + f) % n < 3 else (60, 40, 18, 255)
                d.rectangle([x - larg / 2, y, x + larg / 2, y + 3], fill=c)
        m = np.array(img)
        m[~mask_tela] = (0, 0, 0, 255)
        quadros.append(Image.fromarray(m))
    return quadros


def neblina(largura, alto, seed, forca=1.0):
    """Faixa de neblina para somar: manchas compridas em 3 tons, pixel de 4, pontas emendando para repetir."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (largura, alto), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for _ in range(int(largura / 70)):
        x = rnd.randrange(largura)
        L = rnd.randrange(120, 360)
        y = rnd.randrange(alto // 4, alto * 3 // 4)
        a = rnd.randrange(alto // 6, alto // 3)
        for k, c in enumerate([(18, 20, 24), (30, 32, 38), (44, 46, 54)]):
            s = 1 - k * 0.3
            for dxx in (0, -largura, largura):
                d.ellipse([x + dxx - L * s / 2, y - a * s / 2, x + dxx + L * s / 2, y + a * s / 2],
                          fill=tuple(int(v * forca) for v in c) + (255,))
    return img.resize((largura // 4, alto // 4), Image.NEAREST).resize((largura, alto), Image.NEAREST)


def garca(n=8):
    """Garça branca planando: asa comprida batendo devagar, pescoço dobrado e pernas para trás."""
    P = {"w": (240, 236, 236, 255), "s": (190, 184, 196, 255), "k": (60, 56, 70, 255), "y": (236, 190, 70, 255)}
    asas = [
        ["......ww..........", ".....wsw..........", "....wsw...........", "..kwwwwwwwk.......", "yywwwwwwwwwwkkkk..",
         "....ssssss........", "..................", ".................."],
        ["..................", "..................", "..................", "..kwwwwwwwk.......", "yywwwwwwwwwwkkkk..",
         "....wwssww........", "...wsw.ww.........", "...ww............."],
        ["..................", "..................", "..................", "..kwwwwwwwk.......", "yywwwwwwwwwwkkkk..",
         ".....wsww.........", ".....wsw..........", "......ww.........."],
    ]
    ordem = [0, 0, 1, 2, 2, 1, 0, 0]
    return [pixels(asas[i], P, 4) for i in ordem]


def brilho_lampiao(n=6):
    quadros = []
    k = [1.0, 0.9, 1.0, 0.75, 0.95, 0.85]
    for q in range(n):
        img = Image.new("RGBA", (96, 96), (0, 0, 0, 255))
        d = ImageDraw.Draw(img)
        for rr, c in [(46, (40, 26, 6)), (32, (70, 48, 12)), (18, (110, 80, 24))]:
            cc = tuple(int(v * k[q]) for v in c) + (255,)
            d.ellipse([48 - rr, 48 - rr, 48 + rr, 48 + rr], fill=cc)
        quadros.append(img.resize((24, 24), Image.NEAREST).resize((96, 96), Image.NEAREST))
    return quadros


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    cena = com_1024(largura_1536(cena_sem_ceu(Image.open(BRUTO / "cena.png"))))
    camadas = []

    # céu: as faixas paradas e as nuvens finas à parte (o sol desenhado do bruto fica de fora)
    ceu = np.array(com_1024(largura_1536(Image.open(BRUTO / "ceu.png").convert("RGBA")))).astype(int)
    fundo, nuv = ceu.copy(), np.zeros_like(ceu)
    for y in range(ceu.shape[0]):
        linha = ceu[y, :, :3]
        cores, cont = np.unique(linha.reshape(-1, 3), axis=0, return_counts=True)
        moda = cores[cont.argmax()]
        dif = np.abs(linha - moda).sum(axis=1) > 40
        if y < ceu.shape[0] * 0.8:
            nuv[y, dif] = ceu[y, dif]
        fundo[y, :, :3] = moda
    ceu_alto = 540
    # as faixas vão até 540 (o rosa fica logo acima dos morros); dali para baixo repete a última faixa, para a
    # câmera subindo não achar buraco
    cf = Image.fromarray(fundo.astype(np.uint8)).resize((1280, ceu_alto), Image.NEAREST)
    ceu_img = Image.new("RGBA", (1280, 920))
    ceu_img.paste(cf, (0, 0))
    ceu_img.paste(cf.crop((0, ceu_alto - 1, 1280, ceu_alto)).resize((1280, 920 - ceu_alto)), (0, ceu_alto))
    ceu_img.save(SAIDA / "ceu.png")
    Image.fromarray(nuv.astype(np.uint8)).resize((1536, ceu_alto), Image.NEAREST).save(SAIDA / "nuvens.png")
    camadas += [{"nome": "ceu", "imagem": "ceu.png", "delta": [0, 0], "x": 0, "y": -200},
                {"nome": "nuvens", "imagem": "nuvens.png", "delta": [0.05, 0.05], "y": -200,
                 "velocidade": [-0.1, 0], "repete": [1, 0], "vao": [0, 0]}]

    hq = halo()
    emendar(hq).save(SAIDA / "halo.png")
    camadas.append({"nome": "halo", "folha": {"imagem": "halo.png", "n": 8}, "ticks": 10, "delta": [0.02, 0.02],
                    "x": SOL[0] - hq[0].width // 2, "y": SOL[1] - hq[0].height // 2, "mistura": "soma"})
    ds = disco_sol()
    ds.save(SAIDA / "sol.png")
    camadas.append({"nome": "sol", "imagem": "sol.png", "delta": [0.02, 0.02], "x": SOL[0] - ds.width // 2,
                    "y": SOL[1] - ds.height // 2})

    emendar(garca()).save(SAIDA / "garca.png")
    camadas.append({"nome": "garca", "folha": {"imagem": "garca.png", "n": 8}, "ticks": 6, "delta": [0.3, 0.3],
                    "x": 1500, "y": 30, "velocidade": [-0.9, 0], "repete": [1, 0], "vao": [2600, 0],
                    "seno_y": [14, 240, 0]})

    escala(alfa_duro(cena)).save(SAIDA / "rio.png")
    camadas.append({"nome": "rio", "imagem": "rio.png", "delta": [1, 1], "y": TOPO})

    aq, m = agua(cena)
    aq = [alfa_duro(escala(q)) for q in aq]
    emendar(aq).save(SAIDA / "agua.png")
    ax, ay = na_tela(0, AGUA_Y[0])
    camadas.append({"nome": "agua", "folha": {"imagem": "agua.png", "n": 8}, "ticks": 9, "delta": [1, 1],
                    "x": ax, "y": ay})

    # reflexo do sol na água, embaixo do sol (o sol quase não anda: a coluna fica na mesma altura da tela)
    m_tela = np.array(Image.fromarray(m[AGUA_Y[0]:AGUA_Y[1]].astype(np.uint8) * 255).resize(
        (aq[0].width, aq[0].height), Image.NEAREST)) > 0
    rx = SOL[0] - 45 - ax
    rq = reflexo_sol(m_tela[:, max(0, rx):max(0, rx) + 90])
    emendar(rq).save(SAIDA / "reflexo.png")
    camadas.append({"nome": "reflexo", "folha": {"imagem": "reflexo.png", "n": 8}, "ticks": 6, "delta": [1, 1],
                    "x": ax + max(0, rx), "y": ay, "mistura": "soma"})

    nl = neblina(1536, 120, 5, 0.9)
    nl.save(SAIDA / "neblina_longe.png")
    camadas.append({"nome": "neblina_longe", "imagem": "neblina_longe.png", "delta": [1, 1], "y": ay - 70,
                    "velocidade": [0.12, 0], "repete": [1, 0], "vao": [0, 0], "mistura": "soma"})

    if (BRUTO / "canoa.png").exists():
        cq = apara(folha(BRUTO / "canoa.png", 8, linhas=False))
        alto = 76  # no meio do rio, longe: menor que os lutadores
        cq = [alfa_duro(q.resize((round(q.width * alto / q.height), alto), Image.LANCZOS)) for q in cq]
        emendar(cq).save(SAIDA / "canoa.png")
        camadas.append({"nome": "canoa", "folha": {"imagem": "canoa.png", "n": 8}, "ticks": 8, "delta": [1, 1],
                        "x": -900, "y": TOPO + round(612 * ESCALA) - alto, "velocidade": [0.7, 0],
                        "repete": [1, 0], "vao": [3000, 0], "seno_y": [2, 90, 0]})

    # na frente da água e da canoa: tudo que não é água na faixa do rio e tudo dali para baixo
    a = np.array(cena)
    frente = a.copy()
    corte = np.zeros(a.shape[:2], bool)
    corte[:AGUA_Y[0]] = True
    corte |= m
    frente[corte, 3] = 0
    fr = alfa_duro(escala(Image.fromarray(frente)))
    fr = fr.crop((0, round(AGUA_Y[0] * ESCALA) - 40, fr.width, fr.height))
    fr.save(SAIDA / "frente.png")
    camadas.append({"nome": "frente", "imagem": "frente.png", "delta": [1, 1],
                    "y": TOPO + round(AGUA_Y[0] * ESCALA) - 40})

    emendar(brilho_lampiao()).save(SAIDA / "lampiao.png")
    for i, (x, y) in enumerate(LAMPIOES):
        lx, ly = na_tela(x, y)
        camadas.append({"nome": f"lampiao{i + 1}", "folha": {"imagem": "lampiao.png", "n": 6},
                        "ticks": [7, 5, 9, 4, 8, 6][i:] + [7, 5, 9, 4, 8, 6][:i], "delta": [1, 1],
                        "x": lx - 48, "y": ly - 48, "mistura": "soma"})

    npt = neblina(1536, 90, 11, 0.8)
    npt.save(SAIDA / "neblina_perto.png")
    camadas.append({"nome": "neblina_perto", "imagem": "neblina_perto.png", "delta": [1, 1], "y": ay + 40,
                    "velocidade": [-0.2, 0], "repete": [1, 0], "vao": [0, 0], "seno_y": [4, 300, 0],
                    "mistura": "soma"})
    nr = neblina(1536, 80, 21, 0.55)
    nr.save(SAIDA / "neblina_rasteira.png")
    camadas.append({"nome": "neblina_rasteira", "imagem": "neblina_rasteira.png", "delta": [1.2, 1.2],
                    "y": 640, "velocidade": [0.3, 0], "repete": [1, 0], "vao": [0, 0], "mistura": "soma",
                    "frente": True})

    desc = {"id": "passarela", "nome": "Passarela", "musica": "musicas/passarela.ogg",
            "musica_nome": "Cenário Passarela", "tela": [1280, 720], "largura_mundo": LARGURA, "subida": 160,
            "chao_y": CHAO_Y, "camera": {"tensao": 200, "segue_vertical": 0.6, "tensao_chao": 120},
            "jogadores": {"p1x": -280, "p2x": 280, "margem_tela": 60}, "reflexo": 0, "camadas": camadas}
    (SAIDA / "cenario.json").write_text(json.dumps(desc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("cenarios/passarela pronto:", [c["nome"] for c in camadas])


if __name__ == "__main__":
    main()
