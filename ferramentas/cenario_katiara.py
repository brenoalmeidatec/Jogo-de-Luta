#!/usr/bin/env python3
"""Monta as camadas do cenário Katiara (issue #35) a partir da arte do ChatGPT e grava cenarios/katiara/.

  python3 ferramentas/cenario_katiara.py && python3 ferramentas/gerar_cenario.py cenarios/katiara/cenario.json

Arte bruta em sprites/cenarios/katiara/esbocos/ (capturada do chat "Katiara" do ChatGPT, conta do Alisson):
  cena.png    a rua com o muro pichado de 7 e KT, casas de laje, fios e o bar; céu magenta (vira transparente)
  ceu.png     céu da hora dourada em faixas, com o sol e as nuvens
  guardas.png folha de 8 poses dos três de guarda fazendo o sinal do 7 (fundo magenta)
  moto.png    moto passando (fundo magenta)
O que se mexe sem depender da câmera: nuvens andando, roupa no varal balançando, os guardas (respirando e fazendo o 7),
a pipa no céu, a moto que passa de tempos em tempos e a lâmpada do bar piscando de leve.
Tudo na resolução da janela (localcoord 1280x720), como a Maria Fumaça.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
BRUTO = RAIZ / "sprites" / "cenarios" / "katiara" / "esbocos"
SAIDA = RAIZ / "cenarios" / "katiara"
ESCALA = 0.95            # a cena de 1536 px vira um mundo de 1458 px (a câmera anda 89 px para cada lado);
                         # maior que isso o céu e a laje somem da tela com a câmera em repouso
PES_NA_CENA = 850        # linha da rua (y na cena original) onde ficam os pés dos lutadores
CHAO_Y = 660             # pés na tela 1280x720


def magenta(a, folga=60):
    r, g, b = (a[..., i].astype(int) for i in range(3))
    return (r > 255 - folga - 40) & (b > 255 - folga - 40) & (g < 90 + folga // 2) & (np.abs(r - b) < 70)


def sem_magenta(img):
    """Fundo magenta vira transparente, inclusive a franja rosa que o ChatGPT deixa no contorno."""
    a = np.array(img.convert("RGBA"))
    m = magenta(a)
    a[m, 3] = 0
    # franja: pixel opaco encostado no fundo e puxado para o magenta
    import cv2
    perto = cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~m
    r, g, b = (a[..., i].astype(int) for i in range(3))
    rosa = perto & (r > 150) & (b > 120) & (g < 0.65 * np.minimum(r, b))
    a[rosa, 3] = 0
    return Image.fromarray(a)


def escala(img, k=ESCALA):
    return img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)


def alfa_duro(img):
    a = np.array(img)
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    return Image.fromarray(a)


def varal(cena):
    """Recorta a roupa no varal da laje e faz 8 quadros dela balançando (só desloca colunas: o desenho não muda)."""
    caixa = (395, 105, 670, 205)  # roupas penduradas, na cena original
    peca = cena.crop(caixa)
    a = np.array(peca)
    alto = a[..., 3] > 0
    quadros = []
    for q in range(8):
        f = np.zeros_like(a)
        fase = 2 * np.pi * q / 8
        for y in range(a.shape[0]):
            # mais solto embaixo (a roupa presa no varal em cima)
            dx = int(round(3 * np.sin(fase + y / 18) * (y / a.shape[0])))
            f[y] = np.roll(a[y], dx, axis=0)
            if dx > 0:
                f[y, :dx] = 0
            elif dx < 0:
                f[y, dx:] = 0
        quadros.append(Image.fromarray(f))
    del alto
    return caixa, quadros


def nuvens_do_ceu(ceu):
    """Separa o céu em faixas paradas (com o sol) e as nuvens, que andam devagar e repetem sem emenda."""
    a = np.array(ceu.convert("RGBA")).astype(int)
    h = a.shape[0]
    fundo = a.copy()
    nuvem = np.zeros_like(a)
    for y in range(h):
        linha = a[y, :, :3]
        cores, cont = np.unique(linha.reshape(-1, 3), axis=0, return_counts=True)
        moda = cores[cont.argmax()]
        dif = np.abs(linha - moda).sum(axis=1) > 40
        if y > h * 0.84:     # faixa do sol: fica parada no céu
            dif[:] = False
        nuvem[y, dif] = a[y, dif]
        fundo[y, dif, :3] = moda
    return Image.fromarray(fundo.astype(np.uint8)), Image.fromarray(nuvem.astype(np.uint8))


def pipa():
    """Pipa de papel de seda (losango) com rabiola, desenhada por pixel; 8 quadros com a rabiola ondulando."""
    P = 6  # pixel grande, do tamanho do pixel da arte
    corpo = ["....r....", "...rrr...", "..rryrr..", ".rryyyrr.", "rryyyyyrr", ".rryyyrr.", "..rryrr..",
             "...rrr...", "....r...."]
    cores = {"r": (204, 52, 66, 255), "y": (247, 196, 64, 255), "o": (62, 34, 40, 255)}
    quadros = []
    for q in range(8):
        img = Image.new("RGBA", (20 * P, 30 * P))
        px = img.load()
        for y, s in enumerate(corpo):
            for x, ch in enumerate(s):
                if ch != ".":
                    for dy in range(P):
                        for dx in range(P):
                            px[(x + 5) * P + dx, (y + 1) * P + dy] = cores[ch]
        for k in range(18):  # rabiola
            x = 9 + int(round(2 * np.sin(2 * np.pi * q / 8 + k / 3)))
            y = 10 + k
            c = cores["r"] if k % 4 < 2 else cores["y"]
            for dy in range(P):
                for dx in range(P):
                    px[x * P + dx, y * P + dy] = c
        quadros.append(img)
    return quadros


def folha(imagem, n):
    """Corta a folha em n quadros iguais (fundo magenta) e devolve uma folha horizontal com fundo transparente,
    todos com a mesma caixa (alinhados pela base)."""
    img = sem_magenta(Image.open(imagem))
    a = np.array(img)
    escuro = (a[..., 3] > 0) & (a[..., :3].astype(int).sum(axis=2) < 150)
    # linhas pretas que o ChatGPT desenha entre os quadros e a moldura em cima e embaixo (com 2 px de folga,
    # porque a borda da linha é mais clara e sobrava um risco fino no jogo)
    for eixo in (0, 1):
        idx = np.nonzero(escuro.mean(axis=eixo) > 0.6)[0]
        for d in range(-2, 3):
            ok = np.clip(idx + d, 0, a.shape[1 - eixo] - 1)
            if eixo == 0:
                a[:, ok, 3] = 0
            else:
                a[ok, :, 3] = 0
    import cv2
    n_, rot, dados, _ = cv2.connectedComponentsWithStats((a[..., 3] > 0).astype(np.uint8), connectivity=8)
    for i in range(1, n_):
        if dados[i, cv2.CC_STAT_AREA] < 400:  # sobras (pontas das linhas, poeira)
            a[rot == i, 3] = 0
    img = Image.fromarray(a)
    lq = img.width / n
    cels = [img.crop((round(i * lq), 0, round((i + 1) * lq), img.height)) for i in range(n)]
    def caixa(c):  # só linhas e colunas com corpo de verdade (sobra fina de moldura não conta)
        op = np.array(c.getchannel("A")) > 0
        ys, xs = np.nonzero(op.sum(axis=1) >= 8)[0], np.nonzero(op.sum(axis=0) >= 8)[0]
        return xs[0], ys[0], xs[-1] + 1, ys[-1] + 1
    caixas = [caixa(c) for c in cels]
    x0 = min(b[0] for b in caixas)
    x1 = max(b[2] for b in caixas)
    y0 = min(b[1] for b in caixas)
    y1 = max(b[3] for b in caixas)
    return [c.crop((x0, y0, x1, y1)) for c in cels]


def emendar(quadros):
    L = sum(q.width for q in quadros)
    out = Image.new("RGBA", (L, quadros[0].height))
    x = 0
    for q in quadros:
        out.paste(q, (x, 0))
        x += q.width
    return out


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    cena = sem_magenta(Image.open(BRUTO / "cena.png"))
    if cena.height < 1024:  # a captura pode vir com 1023: repete a última linha
        c2 = Image.new("RGBA", (cena.width, 1024))
        c2.paste(cena, (0, 0))
        c2.paste(cena.crop((0, cena.height - 1, cena.width, cena.height)).resize((cena.width, 1024 - cena.height)),
                 (0, cena.height))
        cena = c2
    caixa_varal, quadros_varal = varal(cena)
    # na cena fica o varal apagado (a camada animada vai por cima no mesmo lugar)
    base = np.array(cena)
    vx0, vy0, vx1, vy1 = caixa_varal
    pano = np.array(quadros_varal[0])[..., 3] > 0
    base[vy0:vy1, vx0:vx1][pano] = 0
    cena_sem_varal = Image.fromarray(base)
    topo = CHAO_Y - round(PES_NA_CENA * ESCALA)  # y da cena na tela com a câmera em repouso
    escala(alfa_duro(cena_sem_varal)).save(SAIDA / "rua.png")
    emendar([alfa_duro(escala(q)) for q in quadros_varal]).save(SAIDA / "varal.png")
    lv = round((vx1 - vx0) * ESCALA)

    ceu_fundo, ceu_nuvens = nuvens_do_ceu(Image.open(BRUTO / "ceu.png"))
    largura_mundo = round(1536 * ESCALA) // 2 * 2
    ceu_alto = 720 + 160 + 40
    ceu_fundo.resize((1280, ceu_alto), Image.NEAREST).save(SAIDA / "ceu.png")
    nuv = ceu_nuvens.resize((1536, ceu_alto), Image.NEAREST)
    nuv.save(SAIDA / "nuvens.png")
    emendar(pipa()).save(SAIDA / "pipa.png")

    camadas = [
        {"nome": "ceu", "imagem": "ceu.png", "delta": [0, 0], "x": 0, "y": -200},
        {"nome": "nuvens", "imagem": "nuvens.png", "delta": [0.1, 0.1], "y": -200, "velocidade": [-0.15, 0],
         "repete": [1, 0], "vao": [0, 0]},
        {"nome": "rua", "imagem": "rua.png", "delta": [1, 1], "y": topo},
        # pipa no ar por cima da rua (na frente das casas, atrás dos lutadores)
        {"nome": "pipa", "folha": {"imagem": "pipa.png", "n": 8}, "ticks": 7, "delta": [0.9, 0.9], "x": 900,
         "y": 20, "seno_x": [40, 420, 0], "seno_y": [18, 260, 0]},
        {"nome": "varal", "folha": {"imagem": "varal.png", "n": 8}, "ticks": 9, "delta": [1, 1],
         "x": round(vx0 * ESCALA) - (largura_mundo - 1280) // 2, "y": topo + round(vy0 * ESCALA)},
    ]
    if (BRUTO / "guardas.png").exists():
        g = folha(BRUTO / "guardas.png", 8)
        alvo = 280  # altura dos guardas na tela (os lutadores têm ~440)
        k = alvo / g[0].height
        gq = [alfa_duro(q.resize((round(q.width * k), alvo), Image.LANCZOS)) for q in g]
        emendar(gq).save(SAIDA / "guardas.png")
        pe = topo + round(712 * ESCALA)  # pé dos guardas: calçada colada no muro, na boca do beco
        camadas.append({"nome": "guardas", "folha": {"imagem": "guardas.png", "n": 8}, "ticks": [14, 14, 12, 10,
                        16, 16, 12, 14], "delta": [1, 1], "x": round(640 * ESCALA) - (largura_mundo - 1280) // 2
                        - gq[0].width // 2, "y": pe - alvo})
    if (BRUTO / "moto.png").exists():
        m = sem_magenta(Image.open(BRUTO / "moto.png"))
        m = m.crop(m.getchannel("A").getbbox())
        alto = 260
        m = alfa_duro(m.resize((round(m.width * alto / m.height), alto), Image.LANCZOS))
        m.save(SAIDA / "moto.png")
        camadas.append({"nome": "moto", "imagem": "moto.png", "delta": [1, 1], "x": -2600,
                        "y": topo + round(800 * ESCALA) - alto, "velocidade": [7, 0], "repete": [1, 0],
                        "vao": [9000, 0], "seno_y": [1, 6, 0]})
    desc = {"id": "katiara", "nome": "Katiara", "musica_nome": "Cenário Katiara (a escolher)",
            "tela": [1280, 720], "largura_mundo": largura_mundo, "subida": 160, "chao_y": CHAO_Y,
            "camera": {"tensao": 200, "segue_vertical": 0.6, "tensao_chao": 120},
            "jogadores": {"p1x": -280, "p2x": 280, "margem_tela": 60}, "reflexo": 0, "camadas": camadas}
    (SAIDA / "cenario.json").write_text(json.dumps(desc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("cenarios/katiara pronto:", [c["nome"] for c in camadas])


if __name__ == "__main__":
    main()
