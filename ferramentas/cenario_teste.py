#!/usr/bin/env python3
"""Cenário de TESTE, todo desenhado por código, para provar o gerar_cenario.py no motor (não é arte do jogo).

  python ferramentas/cenario_teste.py [--previa PASTA] [--furo-magenta]

Grava os PNG e o cenario.json em cenarios/teste/ e gera stages/teste.def + stages/teste.sff. Tem um exemplo de cada
recurso: céu em degradê de faixas (delta 0), duas camadas de nuvem com velocidades diferentes (a de trás lisa, a da
frente presa na malha do pixel, para comparar), morro distante, rio animado em quadros e repetido, barco que vai e
volta por BGCtrl, balão que sobe e desce por seno, bandeira animada em quadros, chão com régua e mato + poste na
frente dos lutadores, sol e halo do poste somados à cor de trás (mistura soma, parado e em quadros) e reflexo no chão. A régua do chão (marca a cada 32 px, linha clara em y = 165) serve para medir no filme.
"""
import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_cenario  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "cenarios" / "teste"
MUNDO, SUBIDA, CHAO = 768, 40, 165
CURSO = (MUNDO - 320) // 2


def largura(delta):
    """Largura mínima de uma camada parada para cobrir a tela em todo o curso da câmera."""
    return 320 + math.ceil(2 * CURSO * delta)


def ceu():
    faixas = [(38, 70, 150), (52, 92, 172), (70, 116, 190), (96, 142, 206), (128, 168, 218), (164, 192, 226),
              (198, 212, 228), (230, 222, 210), (244, 214, 170), (248, 196, 132)]
    im = Image.new("RGBA", (320, 180))
    d = ImageDraw.Draw(im)
    for i, c in enumerate(faixas):
        d.rectangle((0, i * 18, 319, i * 18 + 17), fill=c + (255,))
    return im


def nuvens(l, a, cor, sombra, semente):
    im = Image.new("RGBA", (l, a))
    d = ImageDraw.Draw(im)
    x = 6
    k = semente
    while x < l - 60:
        k = (k * 1103515245 + 12345) & 0x7FFFFFFF
        w = 34 + k % 30
        y = 4 + (k >> 8) % (a - 22)
        d.rectangle((x + 6, y + 8, x + w - 6, y + 15), fill=sombra + (255,))
        d.rectangle((x, y + 4, x + w, y + 11), fill=cor + (255,))
        d.rectangle((x + 8, y, x + w - 12, y + 6), fill=cor + (255,))
        x += w + 26 + (k >> 4) % 30
    return im


def morro():
    l = largura(0.35)
    im = Image.new("RGBA", (l, 84))
    d = ImageDraw.Draw(im)
    for x in range(l):
        h = 30 + 16 * math.sin(x / 47) + 9 * math.sin(x / 19 + 1) + 5 * math.sin(x / 7)
        topo = int(84 - 40 - h)
        d.line((x, topo, x, 83), fill=(58, 104, 92, 255))
        d.line((x, topo, x, topo + 2), fill=(96, 148, 112, 255))
    for x in range(8, l, 64):  # marcas para ver o deslocamento
        d.rectangle((x, 50, x + 5, 62), fill=(40, 78, 76, 255))
    return im


def rio(n=4):
    qs = []
    for f in range(n):
        im = Image.new("RGBA", (64, 22), (44, 112, 168, 255))
        d = ImageDraw.Draw(im)
        for y in range(2, 22, 5):
            for x in range(0, 64, 16):
                xx = (x + f * 4 + y * 3) % 64
                d.line((xx, y, min(xx + 7, 63), y), fill=(150, 204, 232, 255))
        qs.append(im)
    return qs


def barco():
    im = Image.new("RGBA", (30, 18))
    d = ImageDraw.Draw(im)
    d.polygon([(0, 10), (29, 10), (24, 17), (5, 17)], fill=(120, 66, 40, 255))
    d.rectangle((13, 0, 14, 10), fill=(90, 50, 34, 255))
    d.polygon([(15, 1), (26, 9), (15, 9)], fill=(240, 232, 208, 255))
    return im


def balao():
    im = Image.new("RGBA", (22, 30))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, 21, 21), fill=(220, 60, 60, 255))
    d.rectangle((9, 0, 12, 21), fill=(248, 208, 80, 255))
    d.line((4, 20, 8, 26), fill=(90, 50, 34, 255))
    d.line((17, 20, 13, 26), fill=(90, 50, 34, 255))
    d.rectangle((8, 25, 13, 29), fill=(150, 96, 50, 255))
    return im


def bandeira(n=8):
    qs = []
    for f in range(n):
        im = Image.new("RGBA", (40, 70))
        d = ImageDraw.Draw(im)
        d.rectangle((2, 0, 4, 69), fill=(110, 110, 124, 255))
        for x in range(30):
            dy = round(2.5 * math.sin(2 * math.pi * (x / 20 - f / n)) * x / 30)
            d.line((5 + x, 4 + dy, 5 + x, 12 + dy), fill=(250, 250, 240, 255))
            d.line((5 + x, 13 + dy, 5 + x, 21 + dy), fill=(40, 150, 90, 255))
        qs.append(im)
    return qs


def chao():
    topo = 140  # y na tela em repouso
    a = 180 - topo + 12  # 12 px de sobra embaixo, para o tremor de tela
    im = Image.new("RGBA", (MUNDO, a), (150, 122, 92, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, MUNDO - 1, 3), fill=(196, 170, 120, 255))
    y = CHAO - topo
    d.line((0, y, MUNDO - 1, y), fill=(250, 236, 180, 255))  # linha do chão: os pés têm de pisar aqui
    for x in range(0, MUNDO, 32):
        cor = (220, 70, 60, 255) if (x // 32) % 4 == 0 else (110, 84, 64, 255)
        d.rectangle((x, y + 2, x + 1, y + 9), fill=cor)
    d.rectangle((MUNDO // 2 - 1, 6, MUNDO // 2, a - 1), fill=(60, 60, 200, 255))  # centro do mundo
    d.rectangle((0, 6, 3, a - 1), fill=(200, 40, 160, 255))  # ponta esquerda do mundo
    d.rectangle((MUNDO - 4, 6, MUNDO - 1, a - 1), fill=(40, 200, 160, 255))  # ponta direita
    return im


def mato():
    im = Image.new("RGBA", (48, 12))
    d = ImageDraw.Draw(im)
    for x, h in ((2, 7), (6, 10), (11, 6), (20, 9), (25, 5), (33, 8), (38, 11), (44, 6)):
        d.line((x, 11, x + 1, 11 - h), fill=(36, 110, 60, 255))
        d.line((x + 2, 11, x + 1, 11 - h + 2), fill=(70, 160, 80, 255))
    return im


def poste():
    im = Image.new("RGBA", (16, 200))
    d = ImageDraw.Draw(im)
    d.rectangle((5, 14, 10, 199), fill=(70, 62, 84, 255))
    d.rectangle((0, 0, 15, 13), fill=(250, 232, 150, 255))
    d.rectangle((0, 0, 15, 2), fill=(70, 62, 84, 255))
    return im


def sol():
    im = Image.new("RGBA", (36, 36))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, 35, 35), fill=(60, 44, 10, 255))
    d.ellipse((6, 6, 29, 29), fill=(120, 96, 40, 255))
    return im


def halo(n=4):
    qs = []
    for f in range(n):
        im = Image.new("RGBA", (32, 32))
        d = ImageDraw.Draw(im)
        r = (8, 11, 14, 11)[f]
        d.ellipse((16 - r, 16 - r, 15 + r, 15 + r), fill=(90, 80, 30, 255))
        qs.append(im)
    return qs


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--previa", type=Path)
    ap.add_argument("--furo-magenta", action="store_true")
    a = ap.parse_args()
    PASTA.mkdir(parents=True, exist_ok=True)

    def salva(nome, im):
        im.save(PASTA / nome)
        return nome

    def folha(nome, quadros):
        f = Image.new("RGBA", (quadros[0].width * len(quadros), quadros[0].height))
        for i, q in enumerate(quadros):
            f.paste(q, (i * q.width, 0))
        return {"imagem": salva(nome, f), "n": len(quadros)}

    desc = {
        "id": "teste", "nome": "Teste de cenario", "largura_mundo": MUNDO, "subida": SUBIDA, "chao_y": CHAO,
        "reflexo": 48,
        "camadas": [
            {"nome": "ceu", "imagem": salva("ceu.png", ceu()), "delta": [0, 0], "x": 0, "y": 0},
            {"nome": "sol", "imagem": salva("sol.png", sol()), "delta": [0.03, 0.03], "x": 40, "y": 30,
             "mistura": "soma"},
            {"nome": "nuvens_longe",
             "imagem": salva("nuvens_longe.png", nuvens(300, 44, (236, 240, 248), (190, 204, 230), 7)),
             "delta": [0.08, 0.05], "x": 0, "y": 8, "repete": [1, 0], "velocidade": [-0.08, 0], "suave": True},
            {"nome": "nuvens_perto",
             "imagem": salva("nuvens_perto.png", nuvens(380, 50, (255, 255, 255), (206, 216, 236), 31)),
             "delta": [0.18, 0.1], "x": 40, "y": 34, "repete": [1, 0], "vao": [30, 0], "velocidade": [-0.3, 0],
             "suave": False},
            {"nome": "balao", "imagem": salva("balao.png", balao()), "delta": [0.25, 0.2], "x": 210, "y": 40,
             "seno_y": [7, 200, 0], "seno_x": [3, 330, 0]},
            {"nome": "morro", "imagem": salva("morro.png", morro()), "delta": [0.35, 0.35], "y": 92},
            {"nome": "rio", "folha": folha("rio.png", rio()), "ticks": 8, "delta": [0.7, 0.7], "x": 0, "y": 126,
             "repete": [1, 0]},
            {"nome": "barco", "imagem": salva("barco.png", barco()), "delta": [0.7, 0.7], "x": 100, "y": 118,
             "seno_y": [1.5, 90, 0], "ciclo": 480,
             "controles": [{"tipo": "VelSet", "tempo": [0], "x": 0.4}, {"tipo": "VelSet", "tempo": [240], "x": -0.4}]},
            {"nome": "chao", "imagem": salva("chao.png", chao()), "delta": [1, 1], "y": 140},
            {"nome": "bandeira", "folha": folha("bandeira.png", bandeira()), "ticks": 5, "delta": [1, 1],
             "x": 240, "y": 74},
            {"nome": "mato", "imagem": salva("mato.png", mato()), "delta": [1.25, 1.25], "x": 0, "y": 172,
             "repete": [1, 0], "vao": [9, 0], "frente": True},
            {"nome": "poste", "imagem": salva("poste.png", poste()), "delta": [1.25, 1.25], "x": -150, "y": -8,
             "frente": True},
            {"nome": "halo", "folha": folha("halo.png", halo()), "ticks": 7, "delta": [1.25, 1.25], "x": -158,
             "y": -17, "frente": True, "mistura": "soma"},
        ],
    }
    (PASTA / "cenario.json").write_text(json.dumps(desc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    gerar_cenario.gerar(desc, PASTA, previa=a.previa, furo_magenta=a.furo_magenta)


if __name__ == "__main__":
    main()
