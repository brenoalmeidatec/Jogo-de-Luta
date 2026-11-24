#!/usr/bin/env python3
"""Luz em todo efeito que brilha (issue #51, item 2, pedido do Alisson em 2026-11-16: "coloca em todos os efeitos que
têm luz"). Parte da `luz.py`, que chama `aplicar_efeitos` no fim.

  python3 ferramentas/luz_efeitos.py --inventario PASTA [lutador ...]   folha + JSON do que acende e do que não acende

A ideia: a luz de cada efeito sai do próprio efeito.
  - O que acende: efeito com pixel claro e saturado (fogo, ki, raio, faísca) ou branco quente junto de cor. Pedra,
    poeira, garrafa, fumaça e sombra não acendem. A lista NAO_ACENDE de cada lutador corrige o automático.
  - Cor: a média dos pixels que brilham, avivada.
  - Tamanho: a caixa dos pixels que brilham, vezes FOLGA.
  - Piscada: cada quadro do efeito vira um quadro de luz com a força do brilho daquele quadro (5 degraus), o mesmo
    tempo e o mesmo centro. A luz acende, pisca e apaga junto com o efeito, sem ModifyExplod.
  - Curva do KIKIU (GRAD_OFF/GRAD_VAL), em degraus com pontilhado, grão de um vinte e quatro avos do diâmetro.

Os Explods ganham um Explod irmão logo depois (mesmos gatilhos, posição, ligação e id, para um RemoveExplod do
efeito levar a luz junto), um pouco atrás dele e em addalpha. As faíscas de golpe (HitDef sparkno) ganham um clarão
no ponto do impacto pelo [Statedef -4], no tique em que o golpe entra.
"""
import argparse
import colorsys
import functools
import io
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aura_no_corpo as anc  # noqa: E402
import aura_silhueta as asil  # noqa: E402
import conferir_sff as cs  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
GRAD_OFF = (0.0, 0.22, 0.55, 1.0)
GRAD_VAL = (1.0, 0.5, 0.1, 0.0)
GRUPO_EF = 9725           # 9725,k: degrau k (0..NIVEIS-1) da luz do efeito e; índice = e * NIVEIS + k
ACAO_EF = 9800            # ações 9800 + e
NIVEIS = 5
FOLGA = 1.7               # a luz passa do efeito
LUM_MIN = 0.12            # fração mínima de pixels que brilham para o efeito acender
PX_MIN = 30
# corrigido à mão depois da revisão: ações de efeito que parecem brilhar mas não são luz (ou o contrário)
NAO_ACENDE = {}
ACENDE = {}

RE_CTL = re.compile(r"^\[State (-?\d+),([^\]]*)\]\n(.*?)(?=^\[|\Z)", re.M | re.S)


# ---------------------------------------------------------------- leitura
LACOS = {}   # {id(lista da ação): índice do elemento depois do Loopstart}; preenchido por ler_air_completo


def ler_air_completo(texto):
    """{ação: [(g, i, x, y, tempo, flip, trans)]}; o Loopstart de cada ação fica em laco_de(lista)."""
    acoes, atual = {}, None
    for linha in texto.splitlines():
        s = linha.split(";")[0].strip()
        m = re.match(r"\[Begin Action (-?\d+)\]", s, re.I)
        if m:
            atual = acoes.setdefault(int(m.group(1)), [])
            continue
        if atual is not None and re.match(r"loopstart", s, re.I):
            LACOS[id(atual)] = len(atual)
            continue
        if atual is None or not s or re.match(r"clsn", s, re.I):
            continue
        p = [v.strip() for v in s.split(",")]
        if len(p) >= 5 and all(re.fullmatch(r"-?\d+", v) for v in p[:5]):
            g, i, x, y, t = (int(v) for v in p[:5])
            atual.append((g, i, x, y, t, p[5] if len(p) > 5 else "", p[6] if len(p) > 6 else ""))
    return acoes


class Desenhos:
    def __init__(self, arq_sff):
        self.pal, nos, _ = cs.ler(arq_sff)
        self.paleta = asil._paleta(arq_sff)
        self.nos = {}
        for n in nos:
            self.nos.setdefault((n["g"], n["i"]), n)
        self._cache = {}

    def rgba(self, g, i):
        k = (g, i)
        if k not in self._cache:
            n = self.nos.get(k)
            if n is None:
                self._cache[k] = None
            else:
                px = n["px"]
                if n.get("png") or (len(px) > 12 and px[4:8] == b"\x89PNG"):
                    a = np.asarray(Image.open(io.BytesIO(px[px.index(b"\x89PNG"):])).convert("RGBA"))
                else:
                    a = asil._rgba(n, self.paleta)
                self._cache[k] = (a, n["x"], n["y"])
        return self._cache[k]


def brilho(a):
    """Máscara dos pixels que brilham: claros e saturados, ou branco quente quando o desenho tem cor."""
    rgb = a[..., :3].astype(float)
    op = a[..., 3] > 40
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1)
    cor = op & (mx >= 185) & (sat >= 0.45)
    quente = op & (mn >= 215) & (rgb[..., 0] >= rgb[..., 2])
    if cor.sum() < max(8, 0.04 * op.sum()):
        quente = np.zeros_like(quente)
    return cor | quente, op


def claro(a):
    """Pixels claros de qualquer cor (faísca branca, que o brilho() não pega por não ter saturação)."""
    rgb = a[..., :3].astype(float)
    op = a[..., 3] > 40
    return op & (rgb.max(-1) >= 200) & (rgb.mean(-1) >= 170), op


def medir(acao, elems, desenhos, mascara=None):
    """Medidas de uma ação de efeito: fração que brilha, cor, raio e, por quadro, força e centro.

    Se quase nada brilha com cor (faísca branca), mede de novo pelos pixels claros."""
    if mascara is None:
        m1 = medir(acao, elems, desenhos, brilho)
        if m1 is None or m1["px"] >= PX_MIN:
            return m1
        m2 = medir(acao, elems, desenhos, claro)
        if m2 is not None and m2["px"] > m1["px"]:
            m2["branca"] = True
            return m2
        return m1
    quadros, tot_lum, tot_op, soma_cor = [], 0, 0, np.zeros(3)
    caixa, larg, alt = None, 0, 0
    for g, i, x, y, t, flip, _ in elems:
        d = desenhos.rgba(g, i) if g >= 0 else None
        if d is None:
            quadros.append((0.0, 0, 0, t, 0.0))
            continue
        a, ax, ay = d
        m, op = mascara(a)
        n = int(m.sum())
        tot_lum += n
        tot_op += int(op.sum())
        if n:
            soma_cor += a[..., :3][m].astype(float).sum(0)
            ys, xs = np.nonzero(m)
            cx, cy = xs.mean() - ax, ys.mean() - ay
            if "H" in flip.upper():
                cx = -cx
            if "V" in flip.upper():
                cy = -cy
            x0, x1, y0, y1 = xs.min() - ax, xs.max() - ax, ys.min() - ay, ys.max() - ay
            r = max(x1 - x0, y1 - y0) / 2
            caixa = r if caixa is None else max(caixa, r)
            larg, alt = max(larg, x1 - x0), max(alt, y1 - y0)
            quadros.append((n, cx + x, cy + y, t, r))
        else:
            quadros.append((0.0, 0, 0, t, 0.0))
    if not tot_op:
        return None
    pico = max((q[0] for q in quadros), default=0)
    cor = tuple(int(v) for v in soma_cor / tot_lum) if tot_lum else (255, 220, 160)
    return dict(acao=acao, lum=round(tot_lum / tot_op, 3), px=int(pico), cor=cor, raio=float(caixa or 0), larg=int(larg), alt=int(alt),
                quadros=[(round(n / pico, 3) if pico else 0.0, round(float(cx)), round(float(cy)), t,
                          round(float(r) / caixa, 3) if caixa else 1.0)
                         for n, cx, cy, t, r in quadros])


ARQ_CLASSES = Path(__file__).resolve().parent / "luz_classes.json"


@functools.lru_cache(maxsize=1)
def classes():
    """A revisão feita à mão (e por revisores) de cada lutador: {lutador: {acende, nao_acende, faisca_motor}}."""
    try:
        return json.loads(ARQ_CLASSES.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def acende(m, lutador):
    if m is None:
        return False
    c = classes().get(lutador, {})
    if m["acao"] in c.get("acende", ()) or m["acao"] in ACENDE.get(lutador, ()):
        return True
    if m["acao"] in c.get("nao_acende", ()) or m["acao"] in NAO_ACENDE.get(lutador, ()):
        return False
    return m["lum"] >= LUM_MIN and m["px"] >= PX_MIN


def _campo(corpo, chave):
    mm = re.search(rf"^\s*{chave}\s*=\s*([^;\n]+)", corpo, re.M | re.I)
    return mm.group(1).strip() if mm else None


def anims_da_expr(v, air):
    """Ações citadas numa anim (número fixo ou expressão como ifelse(var(20) > 0, 9273, 9243)); F... fica de fora."""
    if v is None or re.search(r"\bF\s*\d", v):
        return []
    return [int(n) for n in re.findall(r"(?<![\w.(])(\d{3,})(?![\w.])", v) if int(n) in air]


def _anim_fixa(v):
    """Número da ação quando a anim é fixa (F de fightfx fica de fora: não é do lutador)."""
    if v is None:
        return None
    v = v.strip()
    return int(v) if re.fullmatch(r"\d+", v) else None


def explods_do_cns(cns, air, gerados=("Luz ", "Aura ", "chama")):
    """[(início, fim, estado, título, corpo, [ações])] de cada Explod com ação do lutador, fora dos blocos gerados."""
    achados = []
    for m in RE_CTL.finditer(cns):
        titulo, corpo = m.group(2).strip(), m.group(3)
        if not re.search(r"^type\s*=\s*Explod\s*$", corpo, re.M | re.I):
            continue
        if any(titulo.startswith(gg) for gg in gerados) or int(m.group(1)) == 9610:
            continue
        anims = anims_da_expr(_campo(corpo, "anim"), air)
        if not anims:
            continue
        achados.append((m.start(), m.end(), int(m.group(1)), titulo, corpo, anims))
    return achados


def faiscas_do_cns(cns, air=None):
    """{estado: [(ação da faísca ou None se for do motor, sparkxy, guarda?)]} dos HitDef.

    Com `air`, também lê a faísca em expressão (S(ifelse(var(20) > 0, 9231, 9201))): a ação vem como o texto da
    expressão, para o gerar() trocar cada número pelo clarão da cor dele."""
    out = {}
    for m in RE_CTL.finditer(cns):
        corpo = m.group(3)
        if not re.search(r"^type\s*=\s*HitDef\s*$", corpo, re.M | re.I):
            continue
        for chave, guarda in (("sparkno", False), ("guard\\.sparkno", True)):
            v = _campo(corpo, chave)
            if v is None:
                v = "-1" if guarda else "0"
            v = v.strip()
            proprio = v.upper().startswith("S")
            num = re.sub(r"^[Ss]", "", v).strip()
            xy = _campo(corpo, "sparkxy") or "0,0"
            if re.fullmatch(r"-?\d+", num):
                if int(num) < 0:
                    continue
                out.setdefault(int(m.group(1)), []).append((int(num) if proprio else None, xy, guarda))
            elif proprio and air is not None and anims_da_expr(num, air):
                out.setdefault(int(m.group(1)), []).append((num, xy, guarda))
    return out


def inventario(lutador, pasta=None):
    pasta = Path(pasta or RAIZ / "chars" / lutador)
    cns = (pasta / f"{lutador}.cns").read_text(encoding="utf-8", errors="replace")
    air = ler_air_completo((pasta / f"{lutador}.air").read_text(encoding="utf-8", errors="replace"))
    des = Desenhos(pasta / f"{lutador}.sff")
    _, ids_aura = anc.aura_do_cns(cns)
    medidas = {}

    def med(a):
        if a not in medidas:
            medidas[a] = medir(a, air[a], des) if a in air else None
        return medidas[a]

    explods = []
    for ini, fim, est, tit, corpo, anims in explods_do_cns(cns, air):
        for anim in anims:
            if anim in ids_aura or 9600 <= anim < 9900 or e_da_aura(air.get(anim, ())):
                continue
            explods.append(dict(estado=est, titulo=tit, anim=anim, acende=acende(med(anim), lutador)))
    projs = []
    for m in RE_CTL.finditer(cns):
        corpo = m.group(3)
        if not re.search(r"^type\s*=\s*Projectile\s*$", corpo, re.M | re.I):
            continue
        pa = _anim_fixa(_campo(corpo, "projanim"))
        pid = _campo(corpo, "projid")
        projs.append(dict(estado=int(m.group(1)), projid=int(pid) if pid and re.fullmatch(r"-?\d+", pid) else -1,
                          anim=pa, hitanim=_anim_fixa(_campo(corpo, "projhitanim")),
                          acende=acende(med(pa), lutador) if pa is not None else False))
    faiscas = []
    for est, lst in sorted(faiscas_do_cns(cns).items()):
        for a, xy, guarda in lst:
            faiscas.append(dict(estado=est, anim=a, sparkxy=xy, guarda=guarda,
                                acende=acende(med(a), lutador) if a is not None else True))
    for d in (*explods, *projs):
        for k in ("hitanim",):
            if d.get(k) is not None:
                med(d[k])
    return dict(lutador=lutador, explods=explods, projeteis=projs, faiscas=faiscas,
                medidas={a: m for a, m in medidas.items() if m}), air, des


def folha(inv, air, des, saida):
    """Uma ficha por ação: o quadro mais claro em fundo azul, número, fração que brilha e se acende."""
    acoes = sorted(inv["medidas"])
    usos = {}
    for k in ("explods", "projeteis", "faiscas"):
        for d in inv[k]:
            for c in ("anim", "hitanim"):
                if d.get(c) is not None:
                    usos.setdefault(d[c], set()).add(f"{k[:4]}@{d['estado']}")
    W, H, cols = 200, 230, 8
    linhas = math.ceil(len(acoes) / cols) or 1
    img = Image.new("RGB", (cols * W, linhas * H), (18, 30, 90))
    dr = ImageDraw.Draw(img)
    for n, a in enumerate(acoes):
        m = inv["medidas"][a]
        el = air[a]
        k = max(range(len(el)), key=lambda j: m["quadros"][j][0]) if el else 0
        g, i = el[k][0], el[k][1]
        d = des.rgba(g, i) if g >= 0 else None
        x0, y0 = (n % cols) * W, (n // cols) * H
        if d is not None:
            im = Image.fromarray(d[0], "RGBA")
            im.thumbnail((W - 10, H - 50))
            img.paste(im, (x0 + (W - im.width) // 2, y0 + 5), im)
        ok = acende(m, inv["lutador"])
        dr.rectangle((x0, y0, x0 + W - 1, y0 + H - 1), outline=(255, 210, 60) if ok else (90, 90, 110), width=3)
        dr.text((x0 + 6, y0 + H - 44), f"{a}  lum {m['lum']:.2f}  {'ACENDE' if ok else 'apagado'}",
                fill=(255, 255, 255))
        dr.text((x0 + 6, y0 + H - 28), ",".join(sorted(usos.get(a, ())))[:30], fill=(200, 200, 220))
        dr.rectangle((x0 + W - 30, y0 + H - 28, x0 + W - 8, y0 + H - 8), fill=tuple(m["cor"]))
    img.save(saida)
    return saida


# ---------------------------------------------------------------- geração
ACAO_VAZIA = 9799         # luz apagada (efeito de uma expressão que não acende)
GRUPO_FA = 9726           # 9726, f * NIVEIS + k: clarão da faísca f
ACAO_FA = 9950            # ações 9950 + f
FAISCA_R = (36, 52, 76)   # raio do clarão do impacto (pixels do jogo): golpe normal, especial, super
FAISCA_PASSOS = ((1.0, 2), (0.8, 2), (0.55, 2), (0.3, 3), (0.12, 3))
COR_MOTOR = (255, 236, 196)
ID_FAISCA = 9640
TITULO = "Luz do efeito"
MARCA_FA, FIM_FA = "; >>> luz_efeitos.py", "; <<< luz_efeitos.py"
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def _queda(t):
    return np.interp(t, GRAD_OFF, GRAD_VAL)


CORTE = 0.07   # abaixo disto a luz é zero: o pontilhado fraco virava pontinhos soltos no cenário escurecido (CK)


def luz_redonda(r, cor, pico, grao, miolo=0.0):
    """RGBA da luz (alfa por pixel, cor cheia) com a curva do KIKIU em degraus e pontilhado; eixo no centro.

    `miolo`: fração do raio em que a cor vai para o branco (o clarão do golpe: aparece em qualquer fundo e a cor da
    faísca não vira oliva nem some no verde-claro)."""
    n = max(3, int(math.ceil(r / grao)))
    w = 2 * n + 1
    ys, xs = np.mgrid[0:w, 0:w].astype(float)
    t = np.hypot(xs - n, ys - n) / n
    v0 = np.clip(_queda(np.minimum(t, 1.0)), 0, 1)
    lim = np.tile(BAYER, (w // 4 + 1, w // 4 + 1))[:w, :w]
    v = np.floor(v0 * 10 + lim) / 10 * pico
    v[v0 * pico < CORTE] = 0
    img = np.zeros((w, w, 4), np.uint8)
    rgb = np.broadcast_to(np.array(cor, float), (w, w, 3)).copy()
    if miolo > 0:
        k = np.clip((miolo - t) / miolo, 0, 1)[..., None]
        k = np.floor(k * 4 + lim[..., None]) / 4          # o branco também em degraus de pixel
        rgb = rgb * (1 - k) + 255 * k
    img[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    img[..., 3] = np.clip(v * 255, 0, 255).astype(np.uint8)
    im = Image.fromarray(img, "RGBA").resize((w * grao, w * grao), Image.NEAREST)
    return im, w * grao // 2, w * grao // 2


def cor_da_luz(rgb):
    h, s_, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
    if s_ < 0.25:                      # faísca branca: luz branca com um fio do tom dela
        return tuple(int(round(c * 255)) for c in colorsys.hsv_to_rgb(h, 0.16, 1.0))
    return tuple(int(round(c * 255)) for c in colorsys.hsv_to_rgb(h, min(1.0, max(s_, 0.65)), 1.0))


def _nivel(f):
    """Degrau de luz (0..NIVEIS-1) de um quadro com força f (0..1); -1 é quadro apagado."""
    if f < 0.03:
        return -1
    return max(0, min(NIVEIS - 1, int(round(f * NIVEIS)) - 1))


TAMANHOS = (1.0, 0.7, 0.45)   # a luz de cada quadro no tamanho do brilho dele (o raio que cresce não leva a luz na frente)


def _tamanho(rr):
    return min(range(len(TAMANHOS)), key=lambda b: abs(TAMANHOS[b] - max(rr, TAMANHOS[-1])))


def acao_de_luz(numero, grupo, base_i, elems, quadros):
    """Texto .air da luz de um efeito: um quadro de luz por quadro do efeito, mesmo tempo, centro, tamanho e laço."""
    linhas = [f"[Begin Action {numero}]"]
    laco = LACOS.get(id(elems))
    for j, ((g, i, x, y, t, flip, tr), (f, cx, cy, _, rr)) in enumerate(zip(elems, quadros)):
        if laco == j:
            linhas.append("Loopstart")
        k = _nivel(f)
        idx = base_i + _tamanho(rr) * NIVEIS + k
        linhas.append(f"-1,-1, 0,0, {t}" if k < 0 else f"{grupo},{idx}, {cx},{cy}, {t}")
    return "\n".join(linhas) + "\n"


GRUPO_FX = 9727          # grupo antigo da luz do contorno em Explod (só para tirar de .sff velhos)
R_FEIXE = 40             # quanto a luz do raio passa do contorno dele (pixels do jogo); usada em luz.assar_feixes


def luz_do_contorno(a, ax, ay, cor, pico, r=R_FEIXE, grao=2):
    """RGBA da luz que abraça o desenho: distância até o pixel que brilha, na curva do KIKIU, em grão e pontilhado.

    A luz nasce do contorno do brilho, então acompanha a ponta do raio enquanto ele cresce e não vai na frente."""
    m, _ = brilho(a)
    if m.sum() < 8:
        m, _ = claro(a)
    h, w = m.shape
    n = int(math.ceil(r / grao))
    # máscara em grão, com folga de n em volta
    hh, ww = -(-h // grao), -(-w // grao)
    mg = np.zeros((hh * grao, ww * grao), bool)
    mg[:h, :w] = m
    mg = mg.reshape(hh, grao, ww, grao).any(axis=(1, 3))
    big = np.zeros((hh + 2 * n, ww + 2 * n), bool)
    big[n:n + hh, n:n + ww] = mg
    dist = np.where(big, 0.0, np.inf)
    cur = big.copy()
    for d in range(1, n + 1):   # dilatação passo a passo: distância de xadrez, arredondada pelo passo diagonal
        viz = cur.copy()
        viz[1:, :] |= cur[:-1, :]
        viz[:-1, :] |= cur[1:, :]
        viz[:, 1:] |= cur[:, :-1]
        viz[:, :-1] |= cur[:, 1:]
        if d % 3:   # 2 de cada 3 passos também na diagonal: o contorno sai redondo e não quadrado
            viz[1:, 1:] |= cur[:-1, :-1]
            viz[1:, :-1] |= cur[:-1, 1:]
            viz[:-1, 1:] |= cur[1:, :-1]
            viz[:-1, :-1] |= cur[1:, 1:]
        novo = viz & ~cur
        dist[novo] = d
        cur = viz
    t = np.clip(dist / n, 0, 1)
    v = np.clip(_queda(np.minimum(t, 1.0)), 0, 1)
    v[big] = 1.0
    H, W = big.shape
    lim = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W]
    v0 = v
    v = np.floor(v * 10 + lim) / 10 * pico
    v[v0 * pico < CORTE] = 0
    img = np.zeros((H, W, 4), np.uint8)
    img[..., :3] = np.array(cor, np.uint8)
    img[..., 3] = np.clip(v * 255, 0, 255).astype(np.uint8)
    im = Image.fromarray(img, "RGBA").resize((W * grao, H * grao), Image.NEAREST)
    return im, ax + n * grao, ay + n * grao


def _troca_anim(expr, mapa):
    def sub(m):
        return str(mapa.get(int(m.group(1)), m.group(1)))
    return re.sub(r"(?<![\w.(])(\d{3,})(?![\w.])", sub, expr)


FORA = re.compile(r"^\s*(type|anim|sprpriority|trans|alpha|ontop|under|palfx\.[\w.]*|ownpal|shadow)\s*=", re.I)


def irmao(estado, corpo, anim_luz):
    """O Explod da luz: tudo do efeito (gatilhos, posição, ligação, tempo, id), menos o desenho e a mistura."""
    linhas = [ln for ln in corpo.rstrip().splitlines() if ln.strip() and not ln.strip().startswith(";")]
    prio = _campo(corpo, "sprpriority") or "0"
    resto = [ln for ln in linhas if not FORA.match(ln)]
    gat = [ln for ln in resto if re.match(r"\s*trigger", ln, re.I)]
    outros = [ln for ln in resto if ln not in gat]
    # efeito ampliado (scale 1.5): a luz fica no tamanho 1, senão o clarão da super lava a tela inteira
    for n_, ln in enumerate(outros):
        mm = re.match(r"\s*scale\s*=\s*([\d.]+)\s*,\s*([\d.]+)\s*$", ln, re.I)
        if mm and max(float(mm.group(1)), float(mm.group(2))) > 1:
            outros[n_] = f"scale = {min(1.0, float(mm.group(1)))}, {min(1.0, float(mm.group(2)))}"
    return "\n".join([f"[State {estado}, {TITULO}]", "type = Explod", *gat, f"anim = {anim_luz}", *outros,
                      f"sprpriority = ({prio}) - 1", "ownpal = 1", "trans = addalpha", "alpha = 255, 0", ""]) + "\n"


def _forca_do_golpe(estado):
    return 2 if estado >= 3000 else 1 if estado >= 1000 else 0


R_MAX = 90        # a luz de um efeito do tamanho da tela (clarão de super) não passa disto (a tela tem uns 430)
R_CHEIO = 50      # até este raio a luz vai com força cheia; acima, cai com a raiz
GRAO_MAX = 2      # grão maior que 3 pixels vira tabuleiro de quadrados (visto no clarão da super do CK)


def e_da_aura(elems):
    """Ação feita de desenhos da aura (camadas 9600.. e silhueta 9710/9711, que moram nas ações 30000+ e 40000+)."""
    return any(9600 <= g < 10000 for g, *_ in elems)


def gerar(lutador, cns, air_texto, pasta, extras=()):
    """(cns com os irmãos de luz, texto .air, {(g, i): (img, ex, ey)}, bloco do -4, resumo).

    O cns e o .air chegam já sem as luzes velhas (tirar_cns, tirar_air)."""
    air = ler_air_completo(air_texto)
    des = Desenhos(Path(pasta) / f"{lutador}.sff")
    _, ids_aura = anc.aura_do_cns(cns)
    medidas, lit = {}, {}

    def med(a):
        if a not in medidas:
            medidas[a] = medir(a, air[a], des) if a in air else None
        return medidas[a]

    def luz_de(a):
        """Número da ação de luz do efeito a (criada na primeira vez), ou ACAO_VAZIA se não acende."""
        if a in ids_aura or 9600 <= a < 10000 or e_da_aura(air.get(a, ())):
            return ACAO_VAZIA
        if not acende(med(a), lutador):
            return ACAO_VAZIA
        if a not in lit:
            lit[a] = len(lit)
        return ACAO_EF + lit[a]

    # 1. Explods: irmão de luz logo depois de cada um (de trás para a frente, para os índices valerem)
    n_ex = 0
    for ini, fim, est, tit, corpo, anims in sorted(explods_do_cns(cns, air), key=lambda e: -e[0]):
        mapa = {a: luz_de(a) for a in anims}
        if all(v == ACAO_VAZIA for v in mapa.values()):
            continue
        expr = _troca_anim(_campo(corpo, "anim"), mapa)
        cns = cns[:fim] + irmao(est, corpo, expr) + "\n" + cns[fim:]
        n_ex += 1
    mapa_extras = {a: luz_de(a) for a in extras}
    sp, texto = {}, [f"[Begin Action {ACAO_VAZIA}]\n-1,-1, 0,0, -1\n"]
    for a, e in sorted(lit.items(), key=lambda kv: kv[1]):
        m = medidas[a]
        r = min(R_MAX, max(10.0, m["raio"] * FOLGA))
        grao = max(1, min(GRAO_MAX, int(round(2 * r / 24))))
        cor = cor_da_luz(m["cor"])
        pico = 0.85 * min(1.0, (R_CHEIO / r) ** 0.5)   # efeito do tamanho da tela não lava a tela
        if m.get("branca"):
            pico *= 0.65                                # luz branca por alfa clareia tudo: vai mais fraca
        base = e * NIVEIS * len(TAMANHOS)
        for b, fator in enumerate(TAMANHOS):
            for k in range(NIVEIS):
                sp[(GRUPO_EF, base + b * NIVEIS + k)] = luz_redonda(max(8.0, r * fator), cor, pico * (k + 1) / NIVEIS,
                                                                    max(1, min(grao, int(round(2 * r * fator / 24)))))
        texto.append(acao_de_luz(ACAO_EF + e, GRUPO_EF, base, air[a], m["quadros"]))
    # 2. faíscas de golpe: clarão no ponto do impacto, pelo -4
    motor_acende = classes().get(lutador, {}).get("faisca_motor", True)
    grupos, cores_fa = {}, []

    def cor_fa(cor):
        if cor not in cores_fa:
            cores_fa.append(cor)
        return ACAO_FA + cores_fa.index(cor)

    def cor_da_faisca(a):
        m = med(a)
        return cor_da_luz(m["cor"]) if acende(m, lutador) else None

    for est, lst in faiscas_do_cns(cns, air).items():
        for a, xy, guarda in lst:
            if a is None:
                if not motor_acende:
                    continue
                expr = str(cor_fa(COR_MOTOR))
            elif isinstance(a, int):
                cor = cor_da_faisca(a)
                if cor is None:
                    continue
                expr = str(cor_fa(cor))
            else:   # expressão: cada ação dela vira o clarão da cor dela (ou nada, se não acende)
                mapa = {n: (cor_fa(c) if (c := cor_da_faisca(n)) else ACAO_VAZIA) for n in anims_da_expr(a, air)}
                if all(v == ACAO_VAZIA for v in mapa.values()):
                    continue
                expr = _troca_anim(a, mapa)
            grupos.setdefault((expr, _forca_do_golpe(est), guarda, xy.replace(" ", "")), set()).add(est)
    # um estado com vários HitDef: fica o primeiro de cada tipo (golpe/guarda)
    visto = set()
    for chave in sorted(grupos, key=str):
        for est in sorted(grupos[chave]):
            if (est, chave[2]) in visto:
                grupos[chave].discard(est)
            visto.add((est, chave[2]))
    grupos = {k: v for k, v in grupos.items() if v}
    for f, cor in enumerate(cores_fa):
        texto_f = [f"[Begin Action {ACAO_FA + f}]"]
        for k, (forca, t) in enumerate(FAISCA_PASSOS):
            sp[(GRUPO_FA, f * NIVEIS + k)] = luz_redonda(40, cor, forca, 2, miolo=0.3)
            texto_f.append(f"{GRUPO_FA},{f * NIVEIS + k}, 0,0, {t}")
        texto.append("\n".join(texto_f) + "\n")
    bloco = [MARCA_FA + ": clarão das faíscas de golpe (issue #51). Não edite: rode python3 ferramentas/luz.py"]
    sim = ["postype = p1", "bindtime = 1", "removetime = -2", "ownpal = 1", "removeongethit = 0",
           "supermovetime = -1", "pausemovetime = -1", "trans = addalpha", "alpha = 255, 0", "ignorehitpause = 1"]
    for (expr, forca, guarda, xy), ests in sorted(grupos.items(), key=lambda kv: (kv[0][2], kv[0][1], kv[0][3],
                                                                                 kv[0][0])):
        esc = FAISCA_R[forca] / 40 * (0.6 if guarda else 1.0)
        sx, sy = (xy.split(",") + ["0"])[:2]
        cond = "MoveGuarded > 0 && map(luz_mg) = 0" if guarda else "HitCount > map(luz_hc) && MoveHit > 0"
        linhas = [f"[State -4, Luz da faisca {'guarda' if guarda else 'golpe'}]", "type = Explod",
                  f"triggerall = {cond} && NumEnemy > 0"]
        ests = sorted(ests)
        for k in range(0, len(ests), 12):
            linhas.append(f"trigger{k // 12 + 1} = " + " || ".join(f"StateNo = {e_}" for e_ in ests[k:k + 12]))
        linhas += [f"anim = {expr}",
                   f"pos = const(size.ground.front) + P2BodyDist X + ({sx}), ({sy})",
                   f"scale = {esc:.3f}, {esc:.3f}", f"id = {ID_FAISCA}", "sprpriority = 4", *sim]
        bloco.append("\n".join(linhas) + "\n")
    if grupos:
        bloco.append('[State -4, Luz da faisca conta golpes]\ntype = MapSet\ntrigger1 = 1\nmap = "luz_hc"\n'
                     "value = HitCount\nignorehitpause = 1\n")
        bloco.append('[State -4, Luz da faisca conta defesas]\ntype = MapSet\ntrigger1 = 1\nmap = "luz_mg"\n'
                     "value = MoveGuarded > 0\nignorehitpause = 1\n")
    bloco.append(FIM_FA)
    resumo = dict(efeitos=len(lit), explods=n_ex, faiscas=sum(len(v) for v in grupos.values()),
                  cores_faisca=len(cores_fa), acoes=sorted(lit), extras=mapa_extras)
    return cns, "\n".join(texto), sp, "\n".join(bloco) + "\n", resumo


def tirar_cns(cns):
    cns = re.sub(rf"\n?{re.escape(MARCA_FA)}.*?{re.escape(FIM_FA)}\n", "\n", cns, flags=re.S)
    return re.sub(rf"^\[State -?\d+, {TITULO}\]\n.*?(?=^\[|\Z)", "", cns, flags=re.M | re.S)


def tirar_air(air):
    def fora(m):
        n = int(m.group(1))
        return "" if n == ACAO_VAZIA or ACAO_EF <= n < ACAO_EF + 150 or ACAO_FA <= n < ACAO_FA + 50 else m.group(0)
    return re.sub(r"\[Begin Action (\d+)\].*?(?=\[Begin Action|\Z)", fora, air, flags=re.S | re.I).rstrip() + "\n"


def tira(lutador, acao, saida):
    """Todos os quadros de uma ação, lado a lado em fundo azul de cenário, com o tempo de cada um."""
    pasta = RAIZ / "chars" / lutador
    air = ler_air_completo((pasta / f"{lutador}.air").read_text(encoding="utf-8", errors="replace"))
    des = Desenhos(pasta / f"{lutador}.sff")
    ims = []
    for g, i, x, y, t, flip, tr in air[acao]:
        d = des.rgba(g, i) if g >= 0 else None
        im = Image.fromarray(d[0], "RGBA") if d else Image.new("RGBA", (40, 40))
        ims.append((im, f"{g},{i} t{t} {tr}"))
    W = max(max(im.width for im, _ in ims), 120)
    H = max(im.height for im, _ in ims) + 20
    out = Image.new("RGB", (W * len(ims), H), (18, 30, 90))
    dr = ImageDraw.Draw(out)
    for k, (im, txt) in enumerate(ims):
        out.paste(im, (k * W, 0), im)
        dr.text((k * W + 4, H - 16), txt, fill=(255, 255, 255))
    if out.width > 4000:
        out = out.resize((4000, max(1, out.height * 4000 // out.width)))
    out.save(saida)
    return saida


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lutadores", nargs="*")
    ap.add_argument("--inventario", type=Path)
    ap.add_argument("--tira", type=int, help="ação: grava os quadros dela em --saida")
    ap.add_argument("--saida", type=Path)
    a = ap.parse_args()
    if a.tira is not None:
        print(tira(a.lutadores[0], a.tira, a.saida))
        return
    a.inventario.mkdir(parents=True, exist_ok=True)
    for l in a.lutadores or ["ck", "gutto", "hazaki", "pengaro", "raiclaven"]:
        inv, air, des = inventario(l)
        (a.inventario / f"{l}.json").write_text(json.dumps(inv, ensure_ascii=False, indent=1), encoding="utf-8")
        folha(inv, air, des, a.inventario / f"{l}.png")
        ac = sum(d["acende"] for k in ("explods", "projeteis", "faiscas") for d in inv[k])
        print(f"{l}: {len(inv['explods'])} explods, {len(inv['projeteis'])} projéteis, {len(inv['faiscas'])} faíscas, "
              f"{ac} acendem, {len(inv['medidas'])} ações medidas")


if __name__ == "__main__":
    main()
