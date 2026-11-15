#!/usr/bin/env python3
"""Aura como nos animes: colada na silhueta do lutador despertado, quadro a quadro (issue #51, Breno 2026-11-15 02:07Z).

  python3 ferramentas/aura_silhueta.py [lutador ...]          gera e liga em chars/<l>/ (sem nome: todos com aura)
  python3 ferramentas/aura_silhueta.py --previa PASTA l [ação] folha do corpo com a aura, sem o motor
  python3 ferramentas/aura_silhueta.py --tirar l               tira a aura de silhueta de chars/<l>/

O pedido: a aura tem o formato do corpo naquele quadro (agachado fica agachada, no pulo sobe junto, caído deita junto),
corre pelo braço e sai pelo punho no soco (pela perna e pelo pé no chute), tem inércia (arrasta quando ele anda, continua
o embalo quando ele para) e as labaredas sobem e balançam. A aura grande de cada um (asas, garanhão, elos, paredão)
continua como está: esta é uma camada a mais, por baixo dela e colada no corpo.

Como é feita (pós-passo idempotente, como o aura_no_corpo.py; quem regrava o .sff ou o .air do lutador roda de novo):

  1. Para cada desenho que o despertado mostra (o sprite do RemapPreset despertado), tira a silhueta do alfa, reduz pela
     metade (o pixel da aura fica do tamanho de 2 pixels do desenho: o mesmo grão do pixelfx) e mede a distância de cada
     ponto de fora até o corpo. Duas camadas:
       pele    a borda colada no corpo (alguns pixels), mais forte no membro que bate: nos elementos com caixa de golpe
               (Clsn1), o pedaço do corpo dentro da caixa ganha uma labareda maior e um estouro pequeno na ponta, do
               tamanho do golpe (regra-efeitos-proporcionais.md);
       chama   as labaredas: a distância é medida "subindo mais barato que descendo" (o fogo sobe) e a borda é cortada
               por um ruído que corre para cima; QUADROS fases do ruído fazem a labareda viva, em laço.
     Tons por lutador (a cor da aura grande dele), em degraus duros, sem borrar.
  2. Grava os desenhos nos grupos GRUPO_PELE e GRUPO_CHAMA do .sff e, para cada ação do corpo N, as ações BASE_PELE + N e
     BASE_CHAMA + N com QUADROS elementos por elemento do corpo (mesmo deslocamento e mesmo espelho).
  3. No [Statedef -4], dois Explods (ID_PELE, ID_CHAMA) que mostram, a cada tique, o elemento da ação espelho igual ao do
     corpo (AnimElemNo(1): o elemento que vai para a tela neste tique) e a fase da labareda. A chama tem inércia: um map
     de mola segue a velocidade (au_sil_x, au_sil_v) e inclina a chama com xshear (a parte de cima arrasta mais que a de
     baixo, os pés ficam presos) e estica quando ele cai.
"""
import argparse
import io
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aura_no_corpo as anc  # noqa: E402
import conferir_sff as cs  # noqa: E402
import efeitos  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FATOR = 2                      # 1 pixel da aura = FATOR pixels do desenho
QUADROS = 6                    # fases da labareda (laço)
TROCA = 2                      # tiques por fase
FASES_PELE = 3                 # a pele mexe menos: 3 desenhos, repetidos no laço
GRUPO_PELE, GRUPO_CHAMA = 9710, 9711
BASE_PELE, BASE_CHAMA = 30000, 40000
ID_PELE, ID_CHAMA = 9610, 9611
MARGEM = (34, 56, 6)           # lados, cima, baixo, em pixels da aura
R_PELE = 2.5                   # borda colada
R_CHAMA = 36.0                 # alcance da labareda (pixels da aura)
SOBE = 0.25                    # custo de subir na distância da chama (descer custa 1)
R_GOLPE = 12.0                 # labareda a mais no membro que bate
R_ESTOURO = 11                 # raio do estouro na ponta do golpe
ALFA_PELE = 170                # a pele somada fica mais fraca: brilho, não contorno
ALFA_CHAMA = (205, 225, 245, 255)  # a chama se mistura ao fundo por alfa (somada, o laranja no azul vira rosa)
PERIODO = 72                   # período vertical do ruído (laço exato em QUADROS fases)
MARCA = "; >>> aura_silhueta.py"
FIM = "; <<< aura_silhueta.py"
PRIORIDADE = {"chama": -4, "pele": -3}


# ---------------------------------------------------------------- .air com as caixas de golpe
def ler_air_clsn(texto):
    """{ação: [(grupo, índice, x, y, flip, tempo, [caixas Clsn1])]}; flip é o texto do campo (H, V, HV ou vazio)."""
    acoes, atual, padrao, proxima, lendo = {}, None, [], None, None
    for linha in texto.splitlines():
        s = linha.split(";")[0].strip()
        m = re.match(r"\[Begin Action (-?\d+)\]", s, re.I)
        if m:
            atual, padrao, proxima, lendo = acoes.setdefault(int(m.group(1)), []), [], None, None
            continue
        if atual is None or not s:
            continue
        m = re.match(r"Clsn([12])(Default)?\s*:\s*(\d+)", s, re.I)
        if m:
            lendo = None
            if m.group(1) == "1":
                lendo = []
                if m.group(2):
                    padrao = lendo
                else:
                    proxima = lendo
            continue
        m = re.match(r"Clsn([12])\[\d+\]\s*=\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)", s, re.I)
        if m:
            if m.group(1) == "1" and lendo is not None:
                x1, y1, x2, y2 = (int(v) for v in m.groups()[1:])
                lendo.append((min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))
            continue
        if re.match(r"loopstart", s, re.I):
            continue
        p = [v.strip() for v in s.split(",")]
        if len(p) >= 5 and all(re.fullmatch(r"-?\d+", v) for v in p[:5]):
            g, i, x, y, t = (int(v) for v in p[:5])
            flip = p[5] if len(p) > 5 else ""
            atual.append((g, i, x, y, flip, t, list(proxima if proxima is not None else padrao)))
            proxima, lendo = None, None
    return acoes


# ---------------------------------------------------------------- desenho
def _dilata(m, quadrado):
    p = np.pad(m, 1)
    out = p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    if quadrado:
        out |= p[:-2, :-2] | p[:-2, 2:] | p[2:, :-2] | p[2:, 2:]
    return out


def distancia(m, ate):
    """Distância (octogonal, perto da euclidiana) de cada ponto até a máscara, até `ate` pixels; além disso, ate + 1."""
    d = np.full(m.shape, ate + 1.0, np.float32)
    d[m] = 0
    atual = m.copy()
    for r in range(1, int(ate) + 1):
        novo = _dilata(atual, quadrado=(r % 3 != 0))
        d[novo & ~atual] = r
        atual = novo
    return d


def distancia_subindo(d, sobe=SOBE):
    """Como a distância, mas subir custa `sobe` por pixel: o fogo vai mais longe para cima do que para os lados."""
    u = d.copy()
    for y in range(u.shape[0] - 2, -1, -1):
        np.minimum(u[y], u[y + 1] + sobe, out=u[y])
    # espalha um pouco para os lados depois de subir (a labareda não sobe como coluna reta)
    for _ in range(2):
        e = np.minimum(np.roll(u, 1, 1), np.roll(u, -1, 1)) + 1.0
        np.minimum(u, e, out=u)
    return u


class Ruido:
    """Ruído de valor em duas oitavas, em coordenadas do lutador (a partir do eixo), periódico em y (PERIODO px): a
    fase k desloca o ruído para cima PERIODO / QUADROS px, e o laço fecha certinho."""

    def __init__(self, semente=51):
        r = np.random.default_rng(semente)
        self.oitavas = [(12, r.random((PERIODO // 12, 64))), (6, r.random((PERIODO // 6, 128)))]

    def __call__(self, xs, ys, fase):
        tot = 0
        for (cel, g), peso in zip(self.oitavas, (0.65, 0.35)):
            yy = (ys + fase * PERIODO / QUADROS) / cel
            xx = xs / cel + 17.3
            y0, x0 = np.floor(yy).astype(int), np.floor(xx).astype(int)
            fy, fx = yy - y0, xx - x0
            fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
            ny, nx = g.shape

            def v(a, b):
                return g[a % ny, b % nx]
            tot = tot + peso * ((v(y0, x0) * (1 - fx) + v(y0, x0 + 1) * fx) * (1 - fy)
                                + (v(y0 + 1, x0) * (1 - fx) + v(y0 + 1, x0 + 1) * fx) * fy)
        return tot


RUIDO = Ruido()


def tons_da_aura(nos, grupos, pal=None):
    """4 tons (fora, meio, claro, miolo) na cor da aura grande do lutador (grupo da camada 9600): o matiz dominante dos
    pixels saturados, numa rampa de energia (escuro e saturado por fora, quase branco no miolo; o fogo puxa do
    vermelho por fora para o amarelo por dentro)."""
    import colorsys
    px = []
    for n in nos:
        if n["g"] not in grupos or (not n.get("png") and pal is None):
            continue
        a = _rgba(n, pal).reshape(-1, 4)
        a = a[a[:, 3] > 128, :3]
        if len(a):
            px.append(a[:: max(1, len(a) // 4000)])
        if len(px) > 12:
            break
    a = np.concatenate(px).astype(float) / 255
    hsv = np.array([colorsys.rgb_to_hsv(*c) for c in a[:: max(1, len(a) // 3000)]])
    hsv = hsv[hsv[:, 2] > 0.3]
    # aura pouco saturada (a fumaça cinza-esverdeada do CK) dá rampa pouco saturada: a cor é a dele, não um neon
    forca = float(np.clip(np.median(hsv[:, 1]) / 0.55, 0.3, 1.0))
    ang, peso = hsv[:, 0] * 2 * np.pi, hsv[:, 1] ** 2
    h = (math.atan2((np.sin(ang) * peso).sum(), (np.cos(ang) * peso).sum()) / (2 * np.pi)) % 1
    rampa = ((-0.035, 0.97, 0.9), (0.0, 0.9, 1.0), (0.03, 0.55, 1.0), (0.05, 0.18, 1.0))
    return [tuple(int(round(v * 255)) for v in colorsys.hsv_to_rgb((h + dh * forca) % 1, sat * forca,
                                                                   val * (1 - (1 - forca) * (0.6 if sat > 0.8 else 0.25))))
            for dh, sat, val in rampa]


class Desenhista:
    def __init__(self, tons):
        self.tons = np.array(tons, np.uint8)

    def _pinta(self, nivel, alfas=(255, 255, 255, 255)):
        """nivel: 0 vazio, 1..4 tons. Devolve RGBA (alfa por tom: a chama é translúcida por fora)."""
        h, w = nivel.shape
        img = np.zeros((h, w, 4), np.uint8)
        for k in range(1, 5):
            sel = nivel == k
            img[sel, :3] = self.tons[k - 1]
            img[sel, 3] = alfas[k - 1]
        return img

    def preparar(self, mascara, eixo):
        """mascara: bool HxW no desenho; eixo (x, y) do desenho. Devolve o contexto na escala da aura."""
        h, w = mascara.shape
        hh, ww = (h + FATOR - 1) // FATOR, (w + FATOR - 1) // FATOR
        m = np.zeros((hh * FATOR, ww * FATOR), bool)
        m[:h, :w] = mascara
        m = m.reshape(hh, FATOR, ww, FATOR).any(axis=(1, 3))
        lado, cima, baixo = MARGEM
        c = np.zeros((hh + cima + baixo, ww + 2 * lado), bool)
        c[cima:cima + hh, lado:lado + ww] = m
        ex, ey = eixo[0] / FATOR + lado, eixo[1] / FATOR + cima
        d = distancia(c, R_CHAMA + 2)
        ys, xs = np.mgrid[0:c.shape[0], 0:c.shape[1]].astype(np.float32)
        return dict(m=c, d=d, u=distancia_subindo(d), xs=xs - ex, ys=ys - ey, eixo=(ex, ey))

    def pele(self, ctx, caixas=(), fase=0):
        m, d, xs, ys = ctx["m"], ctx["d"], ctx["xs"], ctx["ys"]
        n = RUIDO(xs * 2.2, ys * 0.9, fase)
        raio = R_PELE * np.clip(n * 1.9 - 0.55, 0, 1.4)
        nivel = np.zeros(m.shape, np.uint8)
        fora = (d <= raio) & (raio >= 1)
        nivel[fora] = 2
        nivel[fora & (d <= 1) & (n > 0.6)] = 3
        for (x1, y1, x2, y2) in caixas:
            # caixa do golpe, do desenho para a aura (o eixo é o mesmo); o pedaço do corpo dentro dela é o membro
            bx1, bx2 = x1 / FATOR, x2 / FATOR
            by1, by2 = y1 / FATOR, y2 / FATOR
            dentro = m & (xs >= bx1 - 3) & (xs <= bx2 + 3) & (ys >= by1 - 3) & (ys <= by2 + 3)
            if dentro.sum() < 4:
                continue
            dm = distancia(dentro, R_GOLPE + 2)
            rr = R_GOLPE * (0.6 + 0.7 * RUIDO(xs * 2.3 + 40, ys * 2.3, fase))
            zona = ~m & (dm <= rr)
            nivel[zona & (nivel < 2)] = 2
            nivel[zona & (dm <= rr * 0.6)] = np.maximum(nivel[zona & (dm <= rr * 0.6)], 3)
            nivel[~m & (dm <= 2.5)] = 4
            # ponta: o ponto do membro mais longe do meio do corpo (o punho, o pé) e o estouro em volta dele
            ys_d, xs_d = np.nonzero(dentro)
            my, mx = np.nonzero(m)
            k = np.argmax(np.hypot(xs_d - mx.mean(), (ys_d - my.mean()) * 0.6))
            px, py = xs_d[k], ys_d[k]
            ang = np.arctan2(ys - ys[py, px], xs - xs[py, px])
            dist = np.hypot(xs - xs[py, px], ys - ys[py, px])
            raios = R_ESTOURO * (0.45 + 0.55 * np.abs(np.cos(ang * 3 + fase * 0.7)) ** 3)
            est = dist <= raios
            nivel[est & ~m & (nivel < 3)] = 3
            nivel[(dist <= R_ESTOURO * 0.35)] = 4
        return self._pinta(nivel)

    def chama(self, ctx, fase=0):
        m, u, xs, ys = ctx["m"], ctx["u"], ctx["xs"], ctx["ys"]
        n = RUIDO(xs * 1.5, ys * 0.6, fase)
        # o alcance cai nos pés (não queima o chão) e sobe com o ruído em línguas; perto do corpo sempre tem chama
        alcance = R_CHAMA * np.clip(n * 1.7 - 0.5, 0.07, 1.15)
        alcance = np.where(ys > -4, alcance * 0.35, alcance)
        t = u / np.maximum(alcance, 1e-3)
        nivel = np.zeros(m.shape, np.uint8)
        nivel[(t <= 1.0)] = 1
        nivel[(t <= 0.6)] = 2
        nivel[(t <= 0.3)] = 3
        nivel[(t <= 0.12) & (n > 0.45)] = 4
        nivel[m] = 3  # por trás do corpo também: sem fresta entre o corpo e a chama
        # faíscas soltas que sobem (poucas, só acima do corpo)
        f = RUIDO(xs * 3.1 + 91, ys * 3.1, fase)
        faisca = (f > 0.9) & (u > R_CHAMA * 0.5) & (u < R_CHAMA * 1.1) & (ys < -20)
        nivel[faisca & ~m] = 3
        nivel[ys > 4] = 0
        return self._pinta(nivel, ALFA_CHAMA)


def _corta(img, eixo):
    """Recorta o RGBA no que tem tinta; devolve (Image, eixo x, eixo y) ou None."""
    a = img[..., 3] > 0
    if not a.any():
        return None
    ys, xs = np.nonzero(a)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    return Image.fromarray(img[y0:y1, x0:x1], "RGBA"), int(round(eixo[0] - x0)), int(round(eixo[1] - y0))


# ---------------------------------------------------------------- o lutador
def _mascara_do_no(n):
    if n.get("png"):
        cru = n["px"][n["px"].index(b"\x89PNG"):]
        return np.asarray(Image.open(io.BytesIO(cru)).convert("RGBA"))[..., 3] > 0
    return np.frombuffer(n["px"], np.uint8).reshape(n["h"], n["w"]) != 0


def acoes_do_corpo(acoes, remap):
    """As ações do corpo do despertado: todo elemento com sprite trocado pelo RemapPreset despertado."""
    return sorted(a for a, els in acoes.items()
                  if els and a < 9000 and all((g, i) in remap for g, i, *_ in els if g >= 0))


def gerar(pasta, lutador, so=None):
    """Monta os desenhos e as ações espelho. Devolve (sprites [(g, i, img, ex, ey)], texto do .air, info)."""
    pasta = Path(pasta)
    cns = (pasta / f"{lutador}.cns").read_text(encoding="utf-8")
    air = (pasta / f"{lutador}.air").read_text(encoding="utf-8")
    acoes = ler_air_clsn(air)
    remap = anc._remap(cns)
    _, nos, _ = cs.ler(pasta / f"{lutador}.sff")
    por_chave = {}
    for n in nos:
        por_chave.setdefault((n["g"], n["i"]), n)
    nome, ids = anc.aura_do_cns(cns)
    base = ids[0]
    des = Desenhista(tons_da_aura(nos, set(ids), _paleta(pasta / f"{lutador}.sff")))
    corpo = acoes_do_corpo(acoes, remap)
    if so:
        corpo = [a for a in corpo if a in so]
    ctxs, pele_idx, chama_idx, sprites = {}, {}, {}, []
    texto = []

    def desenho(chave, caixas, flip):
        n = por_chave.get(remap.get(chave, chave)) or por_chave.get(chave)
        if n is None or n["w"] * n["h"] == 0:
            return None
        if chave not in ctxs:
            ctxs[chave] = des.preparar(_mascara_do_no(n), (n["x"], n["y"]))
        ctx = ctxs[chave]
        frente = -1 if "h" in flip.lower() else 1
        kp = (chave, tuple(caixas), frente)
        if kp not in pele_idx:
            pele_idx[kp] = []
            for f in range(FASES_PELE):
                # caixa do .air: em pixels do desenho já no lado da tela; o desenho espelhado tem x ao contrário
                cx = [((-x2, y1, -x1, y2) if frente < 0 else (x1, y1, x2, y2)) for x1, y1, x2, y2 in caixas]
                r = _corta(des.pele(ctx, cx, f), ctx["eixo"])
                pele_idx[kp].append(_guarda(sprites, GRUPO_PELE, r))
        if chave not in chama_idx:
            chama_idx[chave] = []
            for f in range(QUADROS):
                r = _corta(des.chama(ctx, f), ctx["eixo"])
                chama_idx[chave].append(_guarda(sprites, GRUPO_CHAMA, r))
        return pele_idx[kp], chama_idx[chave]

    for a in corpo:
        linhas_p, linhas_c = [f"[Begin Action {BASE_PELE + a}]"], [f"[Begin Action {BASE_CHAMA + a}]"]
        for g, i, x, y, flip, t, caixas in acoes[a]:
            r = desenho((g, i), caixas, flip) if g >= 0 else None
            for f in range(QUADROS):
                ox, oy = int(round(x / FATOR)), int(round(y / FATOR))
                ip = r[0][f % FASES_PELE] if r else None
                ic = r[1][f] if r else None
                linhas_p.append(f"{GRUPO_PELE},{ip if ip is not None else 0}, {ox},{oy}, 1, {flip}".rstrip(", ")
                                if ip is not None else "-1,0, 0,0, 1")
                linhas_c.append(f"{GRUPO_CHAMA},{ic if ic is not None else 0}, {ox},{oy}, 1, {flip}".rstrip(", ")
                                if ic is not None else "-1,0, 0,0, 1")
        texto += linhas_p + [""] + linhas_c + [""]
    info = dict(nome=nome, acoes=len(corpo), desenhos=len(ctxs), sprites=len(sprites))
    return sprites, "\n".join(texto), info


def _guarda(sprites, grupo, r):
    if r is None:
        return None
    img, ex, ey = r
    i = sum(1 for s in sprites if s[0] == grupo)
    sprites.append((grupo, i, img, ex, ey))
    return i


# ---------------------------------------------------------------- .cns
def ctl(titulo, tipo, *linhas):
    assert ";" not in titulo, titulo  # ; no título vira comentário e o controlador some sem erro
    return "\n".join([f"[State -4, {titulo}]", f"type = {tipo}", *linhas, "ignorehitpause = 1", ""])


def bloco_cns(nome, escala):
    """O helper ID_PELE é a pele: ele roda DEPOIS do lutador no mesmo tique, então já vê a ação nova (um Explod nascido
    no [Statedef -4] veria a ação um tique atrasada). Ele mesmo solta a chama, um Explod de um tique."""
    e = f"root,map(au_{nome}_e)"
    esc = round(escala * FATOR, 6)
    fase = f"(floor(GameTime / {TROCA}) % {QUADROS})"
    elem = f"(parent,AnimElemNo(0) - 1) * {QUADROS} + 1 + {fase}"
    vivo = f"SelfAnimExist({BASE_PELE} + parent,Anim) && parent,AnimElemNo(0) > 0"
    alfa = f"floor(255 * min(1, max(0, {e})))"
    out = [MARCA + ": aura colada na silhueta (issue #51). Não edite: rode python3 ferramentas/aura_silhueta.py"]
    # mola da inércia: x segue a velocidade para a frente com atraso e passa um pouco do ponto quando ele para
    for m in ("x", "v", "y"):
        out.append(ctl(f"Aura silhueta zera au_sil_{m}", "MapSet", "trigger1 = RoundState = 0",
                       f'map = "au_sil_{m}"', "value = 0"))
    out.append(ctl("Aura silhueta mola acelera", "MapAdd", "trigger1 = 1", 'map = "au_sil_v"',
                   "value = 0.09 * (Vel X - map(au_sil_x)) - 0.22 * map(au_sil_v)"))
    out.append(ctl("Aura silhueta mola anda", "MapAdd", "trigger1 = 1", 'map = "au_sil_x"', "value = map(au_sil_v)"))
    out.append(ctl("Aura silhueta queda", "MapAdd", "trigger1 = 1", 'map = "au_sil_y"',
                   "value = 0.2 * (Vel Y - map(au_sil_y))"))
    out.append(ctl("Aura silhueta nasce", "Helper", f"trigger1 = NumHelper({ID_PELE}) = 0", "helpertype = normal",
                   'name = "aura silhueta"', f"id = {ID_PELE}", f"stateno = {ID_PELE}", "pos = 0, 0",
                   "postype = p1", "ownpal = 1", f"size.xscale = {esc}", f"size.yscale = {esc}",
                   "supermovetime = -1", "pausemovetime = -1"))
    out.append(FIM)
    est = [MARCA + " estado: o helper da aura de silhueta",
           f"[Statedef {ID_PELE}]", "type = A", "movetype = I", "physics = N", f"anim = {BASE_PELE}", "ctrl = 0",
           "velset = 0, 0", f"sprpriority = {PRIORIDADE['pele']}", ""]

    def c(titulo, tipo, *linhas):
        assert ";" not in titulo, titulo
        return "\n".join([f"[State {ID_PELE}, {titulo}]", f"type = {tipo}", *linhas, "ignorehitpause = 1", ""])
    est.append(c("cola no corpo", "BindToParent", "trigger1 = 1", "pos = 0, 0", "facing = 1", "time = 1"))
    est.append(c("mesmo quadro do corpo", "ChangeAnim", f"trigger1 = {vivo}", f"value = {BASE_PELE} + parent,Anim",
                 f"elem = {elem}"))
    est.append(c("brilho", "Trans", "trigger1 = 1", "trans = add",
                 f"alpha = ifelse({vivo}, floor({ALFA_PELE} * {alfa} / 255), 0), 255"))
    est.append(c("sem sombra", "AssertSpecial", "trigger1 = 1", "flag = noshadow"))
    # a chama: a parte de cima arrasta (xshear em volta dos pés) e estica quando ele cai
    est.append(c("chama", "Explod", f"trigger1 = {vivo} && {e} > 0.02", f"anim = {BASE_CHAMA} + parent,Anim",
                 f"id = {ID_CHAMA}", f"animelem = {elem}", "animfreeze = 1", "postype = p1", "pos = 0, 0",
                 "facing = 1", "bindtime = 1", "removetime = 1", f"sprpriority = {PRIORIDADE['chama']}",
                 "ownpal = 1", "removeongethit = 0", "supermovetime = -1", "pausemovetime = -1",
                 "trans = addalpha", f"alpha = {alfa}, 255 - {alfa}",
                 f"scale = {esc}, {esc} * (1 + 0.04 * max(-3, min(6, root,map(au_sil_y))))",
                 "xshear = -0.02 * max(-5, min(5, root,map(au_sil_x)))"))
    est.append(FIM)
    return "\n".join(out) + "\n", "\n".join(est) + "\n"


def tirar_cns(cns):
    return re.sub(rf"\n?{re.escape(MARCA)}.*?{re.escape(FIM)}\n", "\n", cns, flags=re.S).rstrip() + "\n"


def tirar_air(air):
    return re.sub(rf"\[Begin Action ({BASE_PELE}|{BASE_CHAMA})\d*\].*?(?=\[Begin Action|\Z)", "",
                  air, flags=re.S | re.I).rstrip() + "\n"


def _lugar_no_cns(cns, bloco):
    """Logo depois do bloco do aura_no_corpo (ou do fim da aura animada), ainda dentro do [Statedef -4]."""
    m = re.search(r"^; <<< aura_no_corpo\.py\n", cns, re.M)
    if not m:
        raise SystemExit("o [Statedef -4] não tem o bloco do aura_no_corpo.py; rode ele antes")
    return cns[:m.end()] + bloco + cns[m.end():]


def aplicar(lutador, pasta=None):
    pasta = Path(pasta or RAIZ / "chars" / lutador)
    arq_sff, arq_air, arq_cns = (pasta / f"{lutador}.{e}" for e in ("sff", "air", "cns"))
    cns = tirar_cns(arq_cns.read_text(encoding="utf-8").replace("\r\n", "\n"))
    air = tirar_air(arq_air.read_text(encoding="utf-8").replace("\r\n", "\n"))
    arq_air.write_text(air, encoding="utf-8", newline="\n")
    arq_cns.write_text(cns, encoding="utf-8", newline="\n")
    sprites, texto, info = gerar(pasta, lutador)
    escala = float(re.search(r"^xscale\s*=\s*([\d.]+)", cns, re.M).group(1))
    pal, nos, _ = cs.ler(arq_sff)
    rle, png, vistos = [], [], set()
    for n in nos:
        k = (n["g"], n["i"])
        if k in vistos or n["g"] in (GRUPO_PELE, GRUPO_CHAMA):
            continue
        vistos.add(k)
        (png if n.get("png") else rle).append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
    for g, i, img, ex, ey in sprites:
        png.append((g, i, img.width, img.height, ex, ey, efeitos.blob_png(img)))
    efeitos.gravar(arq_sff, pal, rle, png)
    arq_air.write_text(air.rstrip() + "\n\n" + texto, encoding="utf-8", newline="\n")
    menos4, estado = bloco_cns(info["nome"], escala)
    novo = _lugar_no_cns(cns, menos4).rstrip() + "\n\n" + estado
    # o aura_no_corpo.py refaz o bloco dele logo antes deste e deixa uma linha em branco a mais a cada volta
    novo = re.sub(r"\n{3,}(; >>> aura_no_corpo)", r"\n\n\1", novo)
    arq_cns.write_text(novo, encoding="utf-8", newline="\n")
    print(f"{lutador}: aura de silhueta ligada; {info['acoes']} ações, {info['desenhos']} desenhos do corpo, "
          f"{info['sprites']} sprites da aura")


def tirar(lutador, pasta=None):
    pasta = Path(pasta or RAIZ / "chars" / lutador)
    arq_sff, arq_air, arq_cns = (pasta / f"{lutador}.{e}" for e in ("sff", "air", "cns"))
    arq_cns.write_text(tirar_cns(arq_cns.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    arq_air.write_text(tirar_air(arq_air.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    pal, nos, _ = cs.ler(arq_sff)
    rle, png, vistos = [], [], set()
    for n in nos:
        k = (n["g"], n["i"])
        if k in vistos or n["g"] in (GRUPO_PELE, GRUPO_CHAMA):
            continue
        vistos.add(k)
        (png if n.get("png") else rle).append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
    efeitos.gravar(arq_sff, pal, rle, png)


# ---------------------------------------------------------------- prévia sem o motor
def previa(saida, lutador, acoes_pedidas, pasta=None, fundo=(28, 52, 170)):
    pasta = Path(pasta or RAIZ / "chars" / lutador)
    cns = (pasta / f"{lutador}.cns").read_text(encoding="utf-8")
    air = ler_air_clsn((pasta / f"{lutador}.air").read_text(encoding="utf-8"))
    remap = anc._remap(cns)
    _, nos, _ = cs.ler(pasta / f"{lutador}.sff")
    pal = _paleta(pasta / f"{lutador}.sff")
    por = {}
    for n in nos:
        por.setdefault((n["g"], n["i"]), n)
    sprites, txt, info = gerar(pasta, lutador, so=set(acoes_pedidas))
    sp = {(g, i): (img, ex, ey) for g, i, img, ex, ey in sprites}
    espelho = ler_air_clsn(txt)
    quadros = []
    for a in acoes_pedidas:
        for e, (g, i, x, y, flip, t, cx) in enumerate(air[a]):
            n = por.get(remap.get((g, i), (g, i)))
            if n is None:
                continue
            corpo = _rgba(n, pal)
            f = (e * 2) % QUADROS
            tela = Image.new("RGBA", (560, 520), fundo + (255,))
            ox, oy = 280, 470
            for base in (BASE_CHAMA, BASE_PELE):
                gg, ii, *_ = espelho[base + a][e * QUADROS + f]
                if gg < 0:
                    continue
                img, ex, ey = sp[(gg, ii)]
                big = img.resize((img.width * FATOR, img.height * FATOR), Image.NEAREST)
                if "h" in flip.lower():
                    big = big.transpose(Image.FLIP_LEFT_RIGHT)
                    px = ox - (big.width - ex * FATOR)
                else:
                    px = ox - ex * FATOR
                if base == BASE_CHAMA:
                    tela.alpha_composite(big, (max(0, px), max(0, oy - ey * FATOR)))
                else:
                    fraca = np.asarray(big).copy()
                    fraca[..., :3] = (fraca[..., :3].astype(int) * ALFA_PELE // 255).astype(np.uint8)
                    _soma(tela, Image.fromarray(fraca, "RGBA"), px, oy - ey * FATOR)
            c = Image.fromarray(corpo, "RGBA")
            if "h" in flip.lower():
                c = c.transpose(Image.FLIP_LEFT_RIGHT)
                cxp = ox - (c.width - n["x"])
            else:
                cxp = ox - n["x"]
            tela.alpha_composite(c, (cxp, oy - n["y"]))
            quadros.append(tela.resize((280, 260), Image.NEAREST))
    col = 8
    lin = (len(quadros) + col - 1) // col
    folha = Image.new("RGB", (280 * col, 260 * lin), fundo)
    for k, q in enumerate(quadros):
        folha.paste(q.convert("RGB"), ((k % col) * 280, (k // col) * 260))
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    folha.save(saida)
    print(f"prévia: {saida} ({len(quadros)} quadros)")


def _soma(tela, img, x, y):
    base = np.asarray(tela).astype(np.int16).copy()
    a = np.asarray(img).astype(np.int16)
    h, w = a.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(base.shape[1], x + w), min(base.shape[0], y + h)
    if x1 <= x0 or y1 <= y0:
        return
    sub = a[y0 - y:y1 - y, x0 - x:x1 - x]
    m = sub[..., 3:4] > 0
    base[y0:y1, x0:x1, :3] = np.where(m, np.minimum(255, base[y0:y1, x0:x1, :3] + sub[..., :3]),
                                      base[y0:y1, x0:x1, :3])
    tela.paste(Image.fromarray(base.astype(np.uint8), "RGBA"))


def _paleta(arq):
    pal, _, _ = cs.ler(arq)
    p = np.frombuffer(pal, np.uint8)
    return p.reshape(-1, 4)[:, :3] if len(p) % 4 == 0 else p.reshape(-1, 3)


def _rgba(n, pal):
    if n.get("png"):
        return np.asarray(Image.open(io.BytesIO(n["px"][n["px"].index(b"\x89PNG"):])).convert("RGBA"))
    idx = np.frombuffer(n["px"], np.uint8).reshape(n["h"], n["w"])
    out = np.zeros((n["h"], n["w"], 4), np.uint8)
    out[..., :3] = pal[idx]
    out[..., 3] = np.where(idx > 0, 255, 0)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lutadores", nargs="*")
    ap.add_argument("--previa", type=Path)
    ap.add_argument("--acoes", default="0,20,200,230,240,11,40,5100")
    ap.add_argument("--tirar", action="store_true")
    a = ap.parse_args()
    if a.previa:
        previa(a.previa, a.lutadores[0], [int(v) for v in a.acoes.split(",")])
        return
    for l in a.lutadores or ["hazaki"]:
        tirar(l) if a.tirar else aplicar(l)


if __name__ == "__main__":
    main()
