#!/usr/bin/env python3
"""Peças comuns da destruição dos cenários (issue #35, item 4.2): fogo, fumaça, rachaduras, gente correndo, caídos.

Usado pelos cenario_<id>.py. Cada função devolve camadas prontas para o cenario.json, já com o campo "nivel"
(ver gerar_cenario.py): "1" = só na destruição 1 (um lutador despertou), "2" = só na destruição 2 (os dois),
">=1" = nas duas.
Arte bruta do ChatGPT (chat "Pixel Art Background Request", conta do Alisson) em sprites/cenarios/comum/bruto/:
  fogo.png       8 quadros de fogo em fundo preto
  correndo.png   8 células: 4 quadros de um homem correndo e 4 de uma mulher correndo (fundo magenta)
  destrocos.png  5 pessoas caídas (estilo arcade, sem sangue), 3 montes de entulho, carrinho quebrado, carro capotado
Fumaça, rachaduras, fagulhas e o céu esfumaçado são desenhados aqui, por código.
"""
import math
import random
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from cenario_katiara import alfa_duro, emendar, sem_magenta

RAIZ = Path(__file__).resolve().parent.parent
BRUTO = RAIZ / "sprites" / "cenarios" / "comum" / "bruto"

# caixas (x, y, l, a) de cada peça em destrocos.png, medidas por componentes ligados
PECAS = {"caido_homem": (28, 187, 379, 95), "caida_amarela": (448, 169, 320, 112), "caido_velho": (825, 169, 413, 121),
         "caido_verde": (1287, 161, 363, 128), "caida_sacola": (1680, 175, 465, 116),
         "entulho_p": (31, 505, 226, 95), "entulho_m": (284, 458, 354, 149), "entulho_g": (661, 391, 556, 229),
         "carrinho": (1241, 447, 377, 171), "carro": (1643, 391, 502, 221)}

_cache = {}


def _alto(img, alto):
    return alfa_duro(img.resize((max(1, round(img.width * alto / img.height)), alto), Image.LANCZOS))


def quadros_fogo():
    """8 quadros do fogo, fundo preto virando transparente, todos na mesma caixa e com a base embaixo."""
    if "fogo" not in _cache:
        a = np.array(Image.open(BRUTO / "fogo.png").convert("RGBA"))
        a[..., 3] = np.where(a[..., :3].astype(int).max(axis=2) > 60, 255, 0)
        img = Image.fromarray(a)
        lq = img.width / 8
        cels = [img.crop((round(i * lq), 0, round((i + 1) * lq), img.height)) for i in range(8)]
        cels = _mesma_caixa(cels)
        _cache["fogo"] = cels
    return _cache["fogo"]


def _mesma_caixa(cels, minimo=6):
    """Recorta todos os quadros na mesma caixa, centrando cada um pela base (a célula do ChatGPT não é exata)."""
    caixas = []
    for c in cels:
        op = np.array(c.getchannel("A")) > 0
        n, rot, st, _ = cv2.connectedComponentsWithStats(op.astype(np.uint8), connectivity=8)
        grande = np.zeros_like(op)
        for i in range(1, n):
            if st[i, cv2.CC_STAT_AREA] >= 150:
                grande |= rot == i
        ys, xs = np.nonzero(grande.sum(axis=1) >= minimo)[0], np.nonzero(grande.sum(axis=0) >= 2)[0]
        caixas.append((xs[0], ys[0], xs[-1] + 1, ys[-1] + 1))
    L = max(b[2] - b[0] for b in caixas)
    A = max(b[3] - b[1] for b in caixas)
    out = []
    for c, b in zip(cels, caixas):
        q = Image.new("RGBA", (L, A))
        peca = c.crop(b)
        q.paste(peca, ((L - peca.width) // 2, A - peca.height))
        out.append(q)
    return out


def quadros_correndo(quem):
    """4 quadros do homem (quem = 0) ou da mulher (quem = 1) correndo para a direita."""
    if "correndo" not in _cache:
        img = sem_magenta(Image.open(BRUTO / "correndo.png"))
        a = np.array(img)
        n, rot, st, _ = cv2.connectedComponentsWithStats(
            cv2.dilate((a[..., 3] > 0).astype(np.uint8), np.ones((9, 9), np.uint8)), connectivity=8)
        figs = sorted((st[i] for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 8000), key=lambda s: s[0])
        if len(figs) != 8:
            raise SystemExit(f"correndo.png: achei {len(figs)} figuras, esperava 8")
        cels = [img.crop((s[0], s[1], s[0] + s[2], s[1] + s[3])) for s in figs]
        _cache["correndo"] = [_base_comum(cels[:4]), _base_comum(cels[4:])]
    return _cache["correndo"][quem]


def _base_comum(cels):
    L, A = max(c.width for c in cels), max(c.height for c in cels)
    out = []
    for c in cels:
        q = Image.new("RGBA", (L, A))
        q.paste(c, ((L - c.width) // 2, A - c.height))
        out.append(q)
    return out


def peca(nome):
    if "destrocos" not in _cache:
        _cache["destrocos"] = sem_magenta(Image.open(BRUTO / "destrocos.png"))
    x, y, l, a = PECAS[nome]
    im = _cache["destrocos"].crop((x - 4, y - 4, x + l + 4, y + a + 4))
    return im.crop(im.getchannel("A").getbbox())


def quadros_fumaca(larg=160, alto=420, n=8, seed=1):
    """Coluna de fumaça escura subindo, em loop: bolotas que sobem, crescem e balançam, cada uma com a luz em cima
    e a sombra embaixo; pixel de 3."""
    rnd = random.Random(seed)
    P = 3
    bolas = [(rnd.random(), rnd.uniform(-0.22, 0.22), rnd.uniform(0.75, 1.15)) for _ in range(26)]
    escuro, meio, claro = (34, 31, 38, 255), (58, 54, 62, 255), (88, 83, 90, 255)
    quadros = []
    for q in range(n):
        img = Image.new("RGBA", (larg, alto))
        d = ImageDraw.Draw(img)
        for fase, lado, tam in sorted(bolas, key=lambda b: (b[0] + q / n) % 1):   # as de baixo primeiro
            h = (fase + q / n) % 1                      # 0 embaixo, 1 no topo
            y = alto - 16 - h * (alto - 50)
            x = larg / 2 + lado * larg * (0.25 + 1.1 * h) + 8 * math.sin(2 * math.pi * (h * 2 + fase))
            r = (10 + 0.26 * larg * h) * tam * (1 if h < 0.8 else max(0.0, (1 - h) / 0.2))
            if r > 3:
                d.ellipse([x - r, y - r * 0.85, x + r, y + r * 0.85], fill=escuro)
                d.ellipse([x - r * 0.92, y - r * 0.85, x + r * 0.78, y + r * 0.6], fill=meio)
                d.ellipse([x - r * 0.7, y - r * 0.75, x + r * 0.25, y + r * 0.05], fill=claro)
        quadros.append(img.resize((larg // P, alto // P), Image.NEAREST).resize((larg // P * P, alto // P * P),
                                                                               Image.NEAREST))
    return quadros


def rachaduras(larg, alto, pontos, seed=2, cor=(26, 20, 24, 255), borda=(96, 86, 84, 255), grosso=7, achata=1.0,
               torto=0.9):
    """Imagem transparente com rachaduras saindo de cada ponto (x, y, comprimento, ângulo em graus): racha grossa
    no começo que afina e se divide, com a beirada lascada mais clara de um lado. achata < 1 deita as rachas (piso
    visto de longe) e torto é quanto cada passo vira."""
    rnd = random.Random(seed)
    P = 3
    esc = Image.new("L", (larg, alto))
    d = ImageDraw.Draw(esc)

    def risco(x, y, comp, ang, g):
        total = comp
        while comp > 0:
            passo = rnd.uniform(10, 26)
            ang += rnd.uniform(-torto, torto)
            nx, ny = x + passo * math.cos(ang), y + passo * math.sin(ang) * achata
            d.line([x, y, nx, ny], fill=255, width=max(P, round(g * (0.35 + 0.65 * comp / total))))
            if rnd.random() < 0.35 and comp > 50:
                risco(nx, ny, comp * 0.45, ang + rnd.choice((-1, 1)) * rnd.uniform(0.6, 1.3), max(P, g - 2))
            x, y, comp = nx, ny, comp - passo

    for x, y, comp, ang in pontos:
        for k in range(3):   # três braços saindo do mesmo ponto
            risco(x, y, comp * (1 if k == 0 else 0.6), math.radians(ang + k * 120 + rnd.uniform(-25, 25)), grosso)
    m = np.array(esc.resize((larg // P, alto // P), Image.NEAREST)) > 0
    out = np.zeros(m.shape + (4,), np.uint8)
    lasca = np.roll(m, 1, axis=0) & ~m          # beirada clara logo abaixo da racha
    out[lasca] = borda
    out[m] = cor
    return Image.fromarray(out).resize((larg // P * P, alto // P * P), Image.NEAREST)


def fagulhas(larg=1280, alto=420, n=8, seed=5, quantas=40):
    """Brasas subindo (pontos somados), em loop, para a faixa de cima do fogo."""
    rnd = random.Random(seed)
    pts = [(rnd.randrange(larg), rnd.random(), rnd.uniform(0.5, 1.0), rnd.uniform(-30, 30)) for _ in range(quantas)]
    quadros = []
    for q in range(n):
        img = Image.new("RGBA", (larg, alto), (0, 0, 0, 255))
        d = ImageDraw.Draw(img)
        for x, fase, vel, dx in pts:
            h = (fase + vel * q / n) % 1
            y = alto - h * alto
            xx = x + dx * math.sin(2 * math.pi * (h + fase))
            c = (200, 110, 20) if h < 0.5 else (110, 50, 10)
            d.rectangle([xx - xx % 4, y - y % 4, xx - xx % 4 + 3, y - y % 4 + 3], fill=c + (255,))
        quadros.append(img)
    return quadros


class Destruicao:
    """Junta as camadas de destruição de um cenário e grava as imagens na pasta dele."""

    def __init__(self, saida):
        self.saida = Path(saida)
        self.camadas = []
        self._n = 0

    def _nome(self, base):
        self._n += 1
        return f"d{self._n:02d}_{base}"

    def _folha(self, quadros, arquivo):
        emendar(quadros).save(self.saida / arquivo)

    def ceu(self, nivel, tira, antes_de=None):
        """Céu esfumaçado: tira (r, g, b) do céu e das nuvens (subtrai). Devolve a camada (quem chama põe no lugar)."""
        arq = f"d_ceu_{nivel}.png"
        Image.new("RGBA", (1280, 960), tuple(tira) + (255,)).save(self.saida / arq)
        return {"nome": f"d_ceu_{nivel}", "imagem": arq, "delta": [0, 0], "x": 0, "y": -220, "mistura": "subtrai",
                "nivel": str(nivel)}

    def fogo(self, x, base_y, alto, nivel, delta=1, ticks=5, frente=False, fase=0):
        """Fogo com a base em (x no centro, base_y) na tela em repouso."""
        q = [_alto(f, alto) for f in quadros_fogo()]
        q = q[fase:] + q[:fase]
        arq = f"d_fogo_{alto}_{fase}.png"
        self._folha(q, arq)
        c = {"nome": self._nome("fogo"), "folha": {"imagem": arq, "n": 8}, "ticks": ticks, "delta": [delta, delta],
             "x": round(x - q[0].width / 2), "y": base_y - alto, "nivel": str(nivel)}
        if frente:
            c["frente"] = True
        self.camadas.append(c)
        return c

    def fumaca(self, x, base_y, alto, nivel, delta=1, ticks=7, seed=1, larg=None):
        larg = larg or round(alto * 0.42)
        arq = f"d_fumaca_{larg}x{alto}_{seed}.png"
        self._folha(quadros_fumaca(larg // 3 * 3, alto // 3 * 3, seed=seed), arq)
        self.camadas.append({"nome": self._nome("fumaca"), "folha": {"imagem": arq, "n": 8}, "ticks": ticks,
                             "delta": [delta, delta], "x": round(x - larg / 2), "y": base_y - alto,
                             "nivel": str(nivel)})

    def fogo_com_fumaca(self, x, base_y, alto, nivel, delta=1, seed=1, fase=0, fumaca=2.6):
        self.fumaca(x, base_y - round(alto * 0.5), round(alto * fumaca), nivel, delta, seed=seed)
        self.fogo(x, base_y, alto, nivel, delta, fase=fase)

    def correndo(self, quem, pe_y, alto, nivel, vel, x0, vao, delta=1, ticks=5):
        """Pessoa correndo que cruza a tela de tempos em tempos (vel < 0 corre para a esquerda)."""
        q = [_alto(f, alto) for f in quadros_correndo(quem)]
        if vel < 0:
            q = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in q]
        arq = f"d_correndo_{quem}_{alto}_{'e' if vel < 0 else 'd'}.png"
        self._folha(q, arq)
        self.camadas.append({"nome": self._nome("correndo"), "folha": {"imagem": arq, "n": 4}, "ticks": ticks,
                             "delta": [delta, delta], "x": x0, "y": pe_y - alto, "velocidade": [vel, 0],
                             "repete": [1, 0], "vao": [vao, 0], "nivel": str(nivel)})

    def peca(self, nome, x, base_y, alto, nivel, delta=1, espelha=False, frente=False):
        """Peça parada (caído, entulho, carrinho, carro) com a base em base_y e a esquerda em x."""
        im = _alto(peca(nome), alto)
        if espelha:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        arq = f"d_{nome}_{alto}{'_e' if espelha else ''}.png"
        im.save(self.saida / arq)
        c = {"nome": self._nome(nome), "imagem": arq, "delta": [delta, delta], "x": x, "y": base_y - alto,
             "nivel": str(nivel)}
        if frente:
            c["frente"] = True
        self.camadas.append(c)

    def rachaduras(self, x, y, larg, alto, pontos, nivel, delta=1, seed=2, **jeito):
        arq = f"d_rachaduras_{seed}.png"
        rachaduras(larg, alto, pontos, seed, **jeito).save(self.saida / arq)
        self.camadas.append({"nome": self._nome("rachaduras"), "imagem": arq, "delta": [delta, delta], "x": x, "y": y,
                             "nivel": str(nivel)})

    def fagulhas(self, y, nivel, seed=5, quantas=40, alto=420):
        arq = f"d_fagulhas_{seed}.png"
        self._folha(fagulhas(1536, alto, seed=seed, quantas=quantas), arq)
        self.camadas.append({"nome": self._nome("fagulhas"), "folha": {"imagem": arq, "n": 8}, "ticks": 6,
                             "delta": [1, 1], "x": -128, "y": y, "mistura": "soma", "nivel": str(nivel)})

    def clarao_do_fogo(self, nivel, cor=(40, 14, 0), n=6):
        """Luz do fogo tremendo por cima de tudo que fica atrás dos lutadores (soma fraca, tela inteira)."""
        arq = f"d_clarao_{nivel}.png"
        k = [1.0, 0.7, 0.9, 0.55, 0.85, 0.65]
        self._folha([Image.new("RGBA", (64, 36), tuple(int(v * k[i]) for v in cor) + (255,)).resize((1280, 720))
                     for i in range(n)], arq)
        self.camadas.append({"nome": self._nome("clarao"), "folha": {"imagem": arq, "n": n},
                             "ticks": [5, 4, 6, 3, 5, 4], "delta": [0, 0], "x": 0, "y": 0, "mistura": "soma",
                             "nivel": str(nivel)})
