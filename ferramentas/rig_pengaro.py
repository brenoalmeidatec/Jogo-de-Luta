#!/usr/bin/env python3
"""Esqueleto do Pengaró: recorta a pose "parado" em partes e anima as juntas.

Cada pixel do sprite vai para o osso mais próximo. As mãos e os pés seguem alvos (cinemática
inversa), então o pé fica plantado no chão enquanto o corpo se move. Todo quadro sai do mesmo
desenho, por isso o traço não muda de um quadro para outro.

Uso direto, para ver a amostra: python ferramentas/rig_pengaro.py saida.gif
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
FOLHA = RAIZ / "sprites/pengaro/pixel/pengaro.png"
INFO = RAIZ / "sprites/pengaro/pixel/pengaro.json"
ESCALA = 4  # desenha 4x maior e reduz no fim, para o giro não serrilhar
MARGEM = 3  # quanto cada parte invade a vizinha, para não abrir buraco na junta

# Juntas na pose "parado", em pixels da folha.
J = {
    "ombroB": (84, 34), "cotoveloB": (71, 46), "maoB": (64, 67),
    "ombroF": (118, 37), "cotoveloF": (130, 44), "maoF": (147, 32),
    "quadrilB": (92, 62), "joelhoB": (78, 88), "tornozeloB": (65, 108),
    "quadrilF": (112, 62), "joelhoF": (126, 82), "tornozeloF": (132, 104),
    "cintura": (102, 60), "pescoco": (107, 29),
}

# Partes: osso (ou ossos) que define a área, raio do osso e junta em que ela gira.
PARTES = {
    "pelve": ([((92, 61), (114, 62))], 13, "cintura"),
    "tronco": ([((102, 56), (104, 34)), ((90, 34), (118, 36))], 15, "cintura"),
    "cabeca": ([((108, 27), (107, 15))], 12, "pescoco"),
    "bracoB": ([(J["ombroB"], J["cotoveloB"])], 11, "ombroB"),
    "antebracoB": ([(J["cotoveloB"], J["maoB"]), (J["maoB"], (74, 72)), (J["maoB"], (58, 70))], 11, "cotoveloB"),
    "bracoF": ([(J["ombroF"], J["cotoveloF"])], 10, "ombroF"),
    "antebracoF": ([(J["cotoveloF"], J["maoF"])], 11, "cotoveloF"),
    "coxaB": ([(J["quadrilB"], J["joelhoB"])], 14, "quadrilB"),
    "canelaB": ([(J["joelhoB"], J["tornozeloB"])], 12, "joelhoB"),
    "peB": ([((65, 111), (62, 116))], 9, "tornozeloB"),
    "coxaF": ([(J["quadrilF"], J["joelhoF"])], 16, "quadrilF"),
    "canelaF": ([(J["joelhoF"], J["tornozeloF"])], 14, "joelhoF"),
    "peF": ([((134, 108), (150, 116))], 8, "tornozeloF"),
}
ORDEM = ["bracoF", "antebracoF", "coxaB", "canelaB", "peB", "coxaF", "canelaF", "peF",
         "pelve", "tronco", "cabeca", "bracoB", "antebracoB"]


def dist_seg(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy or 1)
    t = max(0, min(1, t))
    return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)


def maior_pedaco(img):
    """Fica só com o maior pedaço conectado, para nenhum dedo solto andar junto com a parte errada."""
    px = img.load()
    w, h = img.size
    visto = set()
    maior = []
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0 or (x, y) in visto:
                continue
            pilha, pedaco = [(x, y)], []
            visto.add((x, y))
            while pilha:
                a, b = pilha.pop()
                pedaco.append((a, b))
                for n in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                    if 0 <= n[0] < w and 0 <= n[1] < h and n not in visto and px[n][3]:
                        visto.add(n)
                        pilha.append(n)
            if len(pedaco) > len(maior):
                maior = pedaco
    limpo = Image.new("RGBA", img.size)
    alvo = limpo.load()
    for p in maior:
        alvo[p] = px[p]
    return limpo


def recortar():
    """Devolve {parte: imagem 4x} com o sprite repartido entre os ossos."""
    folha = Image.open(FOLHA).convert("RGBA")
    r = json.loads(INFO.read_text(encoding="utf-8"))["frames"]["parado"]["frame"]
    base = folha.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"]))
    px = base.load()
    w, h = base.size
    cortes = {nome: Image.new("RGBA", base.size) for nome in PARTES}
    alvos = {nome: c.load() for nome, c in cortes.items()}
    for y in range(h):
        for x in range(w):
            if px[x, y][3] < 128:
                continue
            medidas = {nome: min(dist_seg((x, y), a, b) for a, b in ossos) - raio
                       for nome, (ossos, raio, _) in PARTES.items()}
            menor = min(medidas.values())
            for nome, m in medidas.items():
                if m <= menor + MARGEM:
                    alvos[nome][x, y] = px[x, y]
    return {nome: maior_pedaco(c).resize((w * ESCALA, h * ESCALA), Image.NEAREST) for nome, c in cortes.items()}, base.size


def ik(a, alvo, l1, l2, dobra):
    """Junta do meio de um membro de dois ossos que vai de a até alvo."""
    dx, dy = alvo[0] - a[0], alvo[1] - a[1]
    d = max(1e-3, min(math.hypot(dx, dy), l1 + l2 - 0.01))
    cos_a = max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)))
    ang = math.atan2(dy, dx) + dobra * math.acos(cos_a)
    return (a[0] + l1 * math.cos(ang), a[1] + l1 * math.sin(ang))


def dobra_de(a, meio, fim):
    """Lado para o qual o membro dobra na pose parado: mantém a junta do meio onde ela está."""
    return min((1, -1), key=lambda s: comp(ik(a, fim, comp(a, meio), comp(meio, fim), s), meio))


def comp(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def angulo(a, b):
    return math.atan2(b[1] - a[1], b[0] - a[0])


class Rig:
    def __init__(self):
        self.cortes, self.tam = recortar()

    def pose(self, quadril=(0, 0), giro=0.0, cabeca=0.0, maoF=None, maoB=None, peF=None, peB=None):
        """Monta um quadro. Alvos são deslocamentos em pixels a partir da pose parado.

        quadril move o corpo, giro inclina o tronco (graus, positivo para frente).
        maoF, maoB, peF e peB movem as mãos e os pés, e os pés não seguem o quadril.
        """
        qx, qy = quadril
        mover = lambda p, d: (p[0] + d[0], p[1] + d[1])
        g = math.radians(giro)

        def no_tronco(p):
            x, y = p[0] - J["cintura"][0], p[1] - J["cintura"][1]
            return (J["cintura"][0] + qx + x * math.cos(g) - y * math.sin(g),
                    J["cintura"][1] + qy + x * math.sin(g) + y * math.cos(g))

        pos = {}  # parte: (junta nova, giro em radianos)
        pos["pelve"] = (mover(J["cintura"], quadril), g * 0.3)
        pos["tronco"] = (mover(J["cintura"], quadril), g)
        pos["cabeca"] = (no_tronco(J["pescoco"]), g * 0.4 + math.radians(cabeca))

        for lado, alvo_mao in (("F", maoF), ("B", maoB)):
            ombro = no_tronco(J["ombro" + lado])
            cot, mao = J["cotovelo" + lado], J["mao" + lado]
            l1, l2 = comp(J["ombro" + lado], cot), comp(cot, mao)
            alvo = mover(mao, (qx, qy))
            alvo = mover(alvo, alvo_mao or (0, 0))
            novo = ik(ombro, alvo, l1, l2, dobra_de(J["ombro" + lado], cot, mao))
            pos["braco" + lado] = (ombro, angulo(ombro, novo) - angulo(J["ombro" + lado], cot))
            pos["antebraco" + lado] = (novo, angulo(novo, alvo) - angulo(cot, mao))

        for lado, alvo_pe in (("F", peF), ("B", peB)):
            quadril_l = mover(J["quadril" + lado], quadril)
            joe, tor = J["joelho" + lado], J["tornozelo" + lado]
            l1, l2 = comp(J["quadril" + lado], joe), comp(joe, tor)
            alvo = mover(tor, alvo_pe or (0, 0))
            novo = ik(quadril_l, alvo, l1, l2, dobra_de(J["quadril" + lado], joe, tor))
            pos["coxa" + lado] = (quadril_l, angulo(quadril_l, novo) - angulo(J["quadril" + lado], joe))
            pos["canela" + lado] = (novo, angulo(novo, alvo) - angulo(joe, tor))
            pos["pe" + lado] = (alvo, 0.0)

        w, h = self.tam
        tela = Image.new("RGBA", (w * ESCALA, h * ESCALA))
        for nome in ORDEM:
            junta = J[PARTES[nome][2]]
            nova, rot = pos[nome]
            parte = self.cortes[nome].rotate(-math.degrees(rot), resample=Image.NEAREST,
                                             center=(junta[0] * ESCALA, junta[1] * ESCALA),
                                             translate=(round((nova[0] - junta[0]) * ESCALA),
                                                        round((nova[1] - junta[1]) * ESCALA)))
            tela.alpha_composite(parte)
        final = tela.resize((w, h), Image.BOX)
        alfa = final.getchannel("A").point(lambda a: 255 if a >= 110 else 0)
        final.putalpha(alfa)
        return final


def suave(t):
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def parado(rig, n=12):
    """Ginga no lugar: quadril desce e sobe, tronco balança, mãos fazem círculo."""
    quadros = []
    for i in range(n):
        a = 2 * math.pi * i / n
        quadros.append(rig.pose(quadril=(2.5 * math.sin(a), 2.5 + 2.5 * math.cos(2 * a)), giro=2.5 * math.sin(a),
                                cabeca=-1.5 * math.sin(a), maoF=(2.5 * math.sin(a) - 2, 3 * math.cos(a)),
                                maoB=(-2 * math.sin(a), 2.5 * math.cos(a + 1))))
    return quadros


def andando(rig, n=12):
    """Passo curto: os pés se revezam no chão e o quadril sobe a cada passada."""
    quadros = []
    passo = 13
    for i in range(n):
        a = 2 * math.pi * i / n
        fase = math.sin(a)
        # o pé de trás avança enquanto o da frente empurra, e cada um levanta na ida
        pf = (-10 + passo * fase, -max(0.0, math.cos(a)) * 7)
        pb = (10 - passo * fase, -max(0.0, -math.cos(a)) * 7)
        quadros.append(rig.pose(quadril=(0, 4 + 2.5 * abs(math.cos(a)) - 2.5), giro=3 + 1.5 * math.cos(2 * a),
                                peF=pf, peB=pb, maoF=(-5 - 5 * fase, 3), maoB=(5 * fase, -1)))
    return quadros


def soco(rig):
    """Antecipa recuando o ombro, estica o braço com o corpo e volta devagar."""
    chaves = [  # (tempo, quadril, giro, mão da frente, mão de trás)
        (0.00, (0, 3), 0, (0, 0), (0, 0)),
        (0.18, (-5, 4), -6, (-14, 6), (2, -2)),
        (0.40, (11, 6), 9, (32, 11), (9, -9)),
        (0.60, (12, 6), 10, (34, 11), (10, -9)),
        (1.00, (0, 3), 0, (0, 0), (0, 0)),
    ]
    quadros = []
    n = 10
    for i in range(n):
        t = i / (n - 1)
        for k in range(len(chaves) - 1):
            if chaves[k][0] <= t <= chaves[k + 1][0]:
                a, b = chaves[k], chaves[k + 1]
                u = suave((t - a[0]) / (b[0] - a[0]))
                quadros.append(rig.pose(quadril=mix(a[1], b[1], u), giro=a[2] + (b[2] - a[2]) * u,
                                        maoF=mix(a[3], b[3], u), maoB=mix(a[4], b[4], u)))
                break
    return quadros


def ginga(rig, n=48):
    """Ginga de capoeira em loop sem emenda: os pés se revezam no triângulo, o quadril balança com
    o passo e as mãos se alternam na guarda. Um desenho novo por tick (n=48 dá 0,8 s de ciclo)."""
    quadros = []
    for i in range(n):
        a = 2 * math.pi * i / n
        s1, c1, c2 = math.sin(a), math.cos(a), math.cos(2 * a)
        # pé de trás vai e volta e levanta na ida; o da frente acompanha em contratempo
        pb = (-13 * c1 + 2, -max(0.0, s1) * 9)
        pf = (8 * c1 - 3, -max(0.0, -s1) * 4)
        quadros.append(rig.pose(
            quadril=(6 * s1, 4 + 3.5 * c2), giro=5 * s1 + 2 * c2,
            cabeca=-2.5 * s1,
            maoF=(-5 * s1 - 2, 8 * c1 + 1), maoB=(5 * s1 + 2, -8 * c1 + 3),
            peF=pf, peB=pb))
    return quadros


def amostra(destino):
    rig = Rig()
    tela = (224, 128)
    fundo = (58, 46, 66, 255)
    quadros = []
    for lista, repete, ms in ((ginga(rig), 3, 20),):
        for _ in range(repete):
            for q in lista:
                im = Image.new("RGBA", tela, fundo)
                im.alpha_composite(q)
                quadros.append((im.resize((tela[0] * 3, tela[1] * 3), Image.NEAREST).convert("RGB"), ms))
    quadros[0][0].save(destino, save_all=True, append_images=[q for q, _ in quadros[1:]],
                       duration=[m for _, m in quadros], loop=0)


if __name__ == "__main__":
    amostra(sys.argv[1] if len(sys.argv) > 1 else "pengaro_rig.gif")
