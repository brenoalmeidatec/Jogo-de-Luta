"""Aura juntando na mão antes do poder (issue #51, pedido do Alisson em 2026-11-17).

Nos tiques antes de cada poder que brilha sair, a energia junta no ponto de onde ele nasce: fagulhas da cor do poder
vêm de longe em espiral e entram na mão, um miolo branco cresce e pisca, e uma luz fraca em volta acende o corpo, como
nos animes. Quando o Projectile nasce, a junção some e o poder sai do mesmo ponto.

Chamado no fim do luz.aplicar (não rode sozinho). Gera:
  grupo 9728, índice k * QUADROS + f    desenho f da junção do poder k (cor do poder, trans = add)
  ação  9760 + 2k (+1)                  a junção do poder k (QUADROS quadros de TQ tiques; +1: de 1 tique)
  Explod id 9660, título "Luz junta na mao", no estado do poder, uns DURA tiques antes do Projectile
"""
import colorsys
import math
import re

import numpy as np
from PIL import Image

GRUPO = 9728
ACAO = 9760
ID = 9660
TITULO = "Luz junta na mao"
QUADROS = 11
TQ = 2
DURA = QUADROS * TQ          # 22 tiques: um pouco mais de 1/3 de segundo
R = 84                       # de onde as fagulhas vêm (pixels do jogo)
GRAO = 2
N_FAGULHAS = 26
CEU = -150                   # projétil que nasce acima disto (chuva da super) não junta na mão


def _cor(c, s=None, v=1.0):
    h, s0, _ = colorsys.rgb_to_hsv(*(x / 255 for x in c))
    return np.array(colorsys.hsv_to_rgb(h, s0 if s is None else s, v)) * 255


def _suave(t):
    return t * t * (3 - 2 * t)


def quadros(cor):
    """[(img RGBA, ex, ey)] da junção na cor do poder, já multiplicada pela luz (trans = add)."""
    n = int(math.ceil(R / GRAO)) + 4
    w = 2 * n + 1
    viva, clara = _cor(cor, v=1.0), _cor(cor, s=0.12)
    ys, xs = np.mgrid[0:w, 0:w].astype(float)
    dist = np.hypot(xs - n, ys - n) * GRAO
    bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
    lim = np.tile(bayer, (w // 4 + 1, w // 4 + 1))[:w, :w]
    saida = []
    ouro = math.pi * (3 - math.sqrt(5))
    for f in range(QUADROS):
        p = (f + 1) / QUADROS
        img = np.zeros((w, w, 3))
        # 1. luz fraca em volta, crescendo: acende a mão e o corpo
        rl = 24 + 56 * p
        v = np.interp(dist / rl, (0, 0.22, 0.55, 1.0), (1, 0.5, 0.1, 0))
        v = np.floor(v * 8 + lim) / 8 * (0.2 + 0.45 * p)
        img += viva[None, None, :] * v[..., None]
        # 2. fagulhas: cada uma sai num momento, gira um pouco e entra no miolo
        for k in range(N_FAGULHAS):
            atraso = (k * 0.37) % 0.55
            q = (p - atraso) / (1 - atraso)
            if q <= 0 or q >= 1:
                continue
            ang = k * ouro + 1.1 * q              # espiral
            r0 = R * (0.7 + 0.3 * ((k * 0.61) % 1))
            r = r0 * (1 - _suave(q))
            if r < 5:
                continue
            cauda = 4 + 14 * q                     # mais rápida, mais comprida
            brilho = 0.85 + 0.15 * q
            for s in np.linspace(0, 1, 9):         # da cabeça (perto do miolo) até a cauda
                rr = r + cauda * s
                a2 = ang - 0.25 * s * q
                x = n + rr * math.cos(a2) / GRAO
                y = n + rr * math.sin(a2) / GRAO
                xi, yi = int(round(x)), int(round(y))
                c = (clara * (1 - s) + viva * s) * brilho * (1 - 0.6 * s)
                for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)) if s < 0.5 else ((0, 0), (1, 0)):   # grossa: aparece na aura
                    if 0 <= xi + dx < w and 0 <= yi + dy < w:
                        img[yi + dy, xi + dx] = np.maximum(img[yi + dy, xi + dx], c)
        # 3. sem anel: o círculo tracejado que fechava junto lia como a "rede de futebol" que o Breno vetou nos efeitos
        #    (docs/efeitos-51/LEIA-ME.md); quem mostra a energia sendo puxada são as fagulhas e o miolo
        # 4. miolo: cresce, branco no centro, pisca
        rc = 4 + 20 * p ** 1.3
        pisca = 1.0 if f % 2 == 0 else 0.82
        t = dist / rc
        m = np.clip(1 - t, 0, 1)
        m = np.floor(m * 5 + lim) / 5 * pisca
        branco = np.clip(1.6 - 2.2 * t, 0, 1)[..., None]
        cm = viva[None, None, :] * (1 - branco) + 255 * branco
        img = np.maximum(img, cm * m[..., None])
        a = np.zeros((w, w, 4), np.uint8)
        a[..., :3] = np.clip(img, 0, 255).astype(np.uint8)
        a[..., 3] = np.where(a[..., :3].max(-1) > 3, 255, 0)
        im = Image.fromarray(a, "RGBA").resize((w * GRAO, w * GRAO), Image.NEAREST)
        saida.append((im, n * GRAO + GRAO // 2, n * GRAO + GRAO // 2))
    return saida


# ---------------------------------------------------------------- .cns
RE_TEMPO = re.compile(r"^\s*(trigger\d+)\s*=\s*(Time\s*=\s*(\d+)|AnimElem\s*=\s*(\d+))\s*$", re.I)


def anim_do_estado(cns, estado):
    m = re.search(rf"^\[Statedef {estado}\b[^\]]*\]\n(.*?)(?=^\[)", cns, re.M | re.S | re.I)
    if not m:
        return None
    a = re.search(r"^\s*anim\s*=\s*(\d+)\s*$", m.group(1), re.M | re.I)
    return int(a.group(1)) if a else None


def nasce(cns, air, estado, gat):
    """Tique do estado em que o Projectile nasce (Time = N ou AnimElem = k), e os outros gatilhos; None se não dá."""
    tempo, resto = None, []
    for ln in gat:
        mm = RE_TEMPO.match(ln)
        if mm and tempo is None:
            if mm.group(3):
                tempo = int(mm.group(3))
            else:
                anim = anim_do_estado(cns, estado)
                els = air.get(anim) if anim is not None else None
                k = int(mm.group(4))
                if not els or k > len(els) or any(e[4] < 0 for e in els[:k - 1]):
                    return None
                tempo = sum(e[4] for e in els[:k - 1])
        elif re.match(r"\s*trigger1\s*=", ln, re.I):
            resto.append(ln.split("=", 1)[1].strip())
        elif re.match(r"\s*triggerall\s*=", ln, re.I):
            resto.append(ln.split("=", 1)[1].strip())
        else:
            return None   # gatilho com trigger2..: não sei juntar sem errar
    return (tempo, resto) if tempo is not None else None


def ponto(proj, elems, des, brilho, alongado):
    """(x, y) de onde o poder nasce: o centro do brilho do 1º quadro (bola) ou a ponta de trás (raio, a mão)."""
    ox, oy = proj["offset"]
    esc = proj.get("escala", 1.0)
    for g, i, x, y, t, flip, _ in elems:
        d = des.rgba(g, i) if g >= 0 else None
        if d is None:
            continue
        a, ax, ay = d
        m, op = brilho(a)
        if m.sum() < 8:
            m = op
        ys, xs = np.nonzero(m)
        if not len(xs):
            continue
        if "H" in (flip or "").upper():
            xs = a.shape[1] - 1 - xs
            ax = a.shape[1] - 1 - ax
        if alongado:
            corte = xs.min() + 0.12 * (xs.max() - xs.min())
            sel = xs <= corte
            cx, cy = xs[sel].mean(), ys[sel].mean()
        else:
            cx, cy = xs.mean(), ys.mean()
        return round(ox + (cx - ax + x) * esc, 1), round(oy + (cy - ay + y) * esc, 1)
    return ox, oy


def explod(estado, gatilho, t0, dura, x, y, acao):
    linhas = [f"[State {estado}, {TITULO}]", "type = Explod", f"trigger1 = {gatilho}", f"anim = {acao}",
              f"id = {ID}", "postype = p1", f"pos = {x}, {y}", "bindtime = -1", f"removetime = {dura}",
              "ownpal = 1", "removeongethit = 1", "ignorehitpause = 1", "pausemovetime = -1", "supermovetime = -1",
              "sprpriority = 5", "trans = add", "alpha = 256, 256"]
    return "\n".join(linhas) + "\n\n"


def aplicar(cns, air, des, projs, poderes, cores, brilho):
    """Põe a junção antes de cada poder que brilha. projs: luz.projeteis(cns); poderes: [(pid, anim, raio, centro,
    alongamento)]; cores: cor de cada poder. Devolve (cns, {(g, i): (img, ex, ey)}, texto .air, quantos)."""
    quer = [o[0] for o in poderes]
    escolhidos = {}
    for ini, fim, estado, gat, d in projs:
        if d["projid"] not in quer:
            continue
        k_ = quer.index(d["projid"])
        n_ = nasce(cns, air, estado, gat)
        if n_ is None:
            continue
        tempo, resto = n_
        elems = air.get(d["projanim"], [])
        x, y = ponto(d, elems, des, brilho, poderes[k_][4] >= 2.2)
        if y < CEU:
            continue
        chave = (estado, tuple(resto))
        if chave not in escolhidos or tempo < escolhidos[chave][1]:
            escolhidos[chave] = (fim, tempo, x, y, k_)
    for (estado, resto), (fim, tempo, x, y, k_) in sorted(escolhidos.items(), key=lambda kv: -kv[1][0]):
        # poder que sai cedo (menos de DURA tiques): a junção corre no dobro da velocidade, 1 tique por quadro
        rapida = tempo < DURA
        t0 = max(0, tempo - (QUADROS if rapida else DURA))
        dura = max(4, tempo - t0)
        gat = " && ".join([f"Time = {t0}", *[f"({r})" for r in resto]])
        cns = cns[:fim] + explod(estado, gat, t0, dura, x, y, ACAO + 2 * k_ + rapida) + cns[fim:]
    sp, texto = {}, []
    usados = sorted({v[4] for v in escolhidos.values()})
    for k_ in usados:
        for f, q in enumerate(quadros(cores[k_])):
            sp[(GRUPO, k_ * QUADROS + f)] = q
        for rapida, tq in ((0, TQ), (1, 1)):
            linhas = [f"[Begin Action {ACAO + 2 * k_ + rapida}]"]
            for f in range(QUADROS):
                linhas.append(f"{GRUPO},{k_ * QUADROS + f}, 0,0, {tq if f < QUADROS - 1 else -1}")
            texto.append("\n".join(linhas) + "\n")
    return cns, sp, "\n".join(texto), len(escolhidos)


def tirar_cns(cns):
    return re.sub(rf"^\[State -?\d+, {TITULO}\]\n.*?(?=^\[|\Z)", "", cns, flags=re.M | re.S)


def tirar_air(air):
    return re.sub(rf"\[Begin Action ({ACAO}|{ACAO}\d|97[67]\d)\].*?(?=\[Begin Action|\Z)", "", air,
                  flags=re.S | re.I).rstrip() + "\n"
