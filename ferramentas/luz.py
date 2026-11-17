#!/usr/bin/env python3
"""Luz e brilho nas auras e nos poderes, na base do KIKIU (issue #51, Breno 2026-11-15 03:51Z).

  python3 ferramentas/luz.py [lutador ...]     liga em chars/<l>/ (sem nome: hazaki)
  python3 ferramentas/luz.py --tirar l         desfaz
  python3 ferramentas/luz.py --previa PASTA l  folha com os desenhos de luz

A base do KIKIU (v2/luzes.gd e v2/mundo.gd, só lida, adaptada para o IKEMEN):
  - luz pontual com queda forte: GRAD_OFF = [0, 0.22, 0.55, 1], GRAD_VAL = [1, 0.5, 0.1, 0] (miolo forte, longe escuro);
  - um orbe somado no miolo do poder;
  - tremor leve da luz (aqui travado em no máximo 2,5 Hz, para não piscar);
  - o mundo escurece por um tom de ambiente e a camada de brilho, somada, fica por cima sem escurecer junto.

Aqui:
  1. ESCURO   Explod preto bem grande, por trás de tudo do lutador e na frente do cenário, com addalpha (0, 256 - k): o
              cenário fica k/256 mais escuro (um pouco no despertado, mais com um poder no ar). Não usa BGPalFX: o
              BGPalFX é um só para a luta e apagaria os clarões das supers dos dois lutadores.
  2. HALO     brilho na cor da forma em volta do corpo do despertado, centrado no meio do corpo (os maps do
              aura_no_corpo.py: centro e quanto está deitado) e com tremor. A curva do KIKIU vai no alfa de cada pixel
              (addalpha): somada pura, a luz laranja no fundo azul virava rosa, e fraca demais ela sumia atrás da aura.
  3. POÇA     a mesma luz achatada no chão embaixo dele; some conforme ele sobe no pulo.
  4. OPONENTE perto clareia na cor da luz (PalFX leve com redirectid), só quando não está apanhando, não está num
              estado próprio (1000 para cima) e não está despertado (var(20) > 0: o Gutto e o Raiclaven têm tom
              próprio no Despertar, e os dois PalFX brigariam).
  5. PODER    cada projétil de energia ganha um orbe somado no miolo e um halo, que andam com ele (mesma posição e
              velocidade do Projectile) e somem quando ele some (o orbe é somado, o halo é brilho por alfa); a poça de luz corre no chão embaixo. Enquanto há poder
              no ar o mundo escurece mais.

  6. EFEITOS  (luz_efeitos.py) todo Explod de efeito que brilha ganha um Explod irmão com a luz tirada do próprio
              desenho (cor, tamanho e força quadro a quadro), e todo golpe que entra solta um clarão no ponto do impacto.
              O que acende e o que não acende está revisado em luz_classes.json.

Os poderes que acendem são os projéteis cujo desenho brilha (luz_classes.json): pedra, garrafa e latinha ficam fora.
O lutador sem aura em camadas (Raiclaven) fica só com os itens 1 (no poder), 5 e 6.

Pós-passo idempotente (refaz os próprios blocos). Roda encadeado no fim do aura_silhueta.aplicar (e no fim do
gerar_raiclaven.py).
"""
import argparse
import colorsys
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aura_no_corpo as anc  # noqa: E402
import aura_silhueta as asil  # noqa: E402
import conferir_sff as cs  # noqa: E402
import efeitos  # noqa: E402
import luz_efeitos as le  # noqa: E402
import luz_junta as lj  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
GRAD_OFF = (0.0, 0.22, 0.55, 1.0)
GRAD_VAL = (1.0, 0.5, 0.1, 0.0)
GRUPO = 9720                     # 9720,0 halo; 9720,1 poça; 9720,2 escuro; 9721,k orbe e 9722,k halo do poder k
ID_HALO, ID_POCA, ID_ESCURO = 9620, 9621, 9623
ID_PODER = 9630                  # 9630 + 3k: orbe, halo e poça do poder k


def id_poder(k):
    """1º id (orbe; +1 halo, +2 poça) da luz do poder k: 9630 + 3k, pulando o 9640 da luz da faísca dos golpes
    (luz_efeitos.ID_FAISCA): com 4 poderes acesos o 4º caía em 9639-9641 e o -4 apagava a luz de toda faísca."""
    base = ID_PODER + 3 * k
    return base if base + 2 < 9640 else 9641 + 3 * (k - 3)
ACAO = 9720                      # ações 9720.. (halo, poça, escuro) e 9730 + 2k (orbe e halo do poder k)
R_HALO, R_POCA, R_ORBE, R_HALO_PODER = 170, 120, 20, 115
ESCURO_DESPERTO, ESCURO_PODER = 0.16, 0.2   # quanto o cenário escurece (fração)
MARCA, FIM = "; >>> luz.py", "; <<< luz.py"
# os poderes que acendem saem da revisão em luz_classes.json (o desenho do projétil brilha); pedra, garrafa e
# latinha não acendem. Quem tem a luz: o aura_silhueta.py chama a luz.py no fim para estes.
LIGADOS = ("hazaki", "gutto", "pengaro", "ck", "raiclaven")
FORCA_OPONENTE = 0.08   # 0,3 e 0,16 deixavam o oponente do CK chapado de verde-oliva
FEIXE = 100             # projétil com brilho de raio maior que isto (pixels do jogo) é um raio: luz quadro a quadro
GRAO = 2                          # pixel da luz, em pixels do jogo


def queda(t):
    """A curva de luz do KIKIU: 1 no miolo, 0,5 a 22% do raio, 0,1 a 55%, 0 na borda."""
    return np.interp(t, GRAD_OFF, GRAD_VAL)


BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def _pixel(v, niveis=10):
    """Degraus de luz com pontilhado de 4x4 entre eles: o grão do pixel, sem faixa dura. A borda fraquinha vai a zero
    (le.CORTE): o pontilhado dela virava pontinhos soltos no cenário escurecido."""
    h, w = v.shape
    lim = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    q = np.floor(v * niveis + lim) / niveis
    q[v < le.CORTE] = 0
    return q


def mancha(rx, ry, cor, pico, miolo=None, raio_miolo=0.0, modo="add"):
    """RGBA de uma luz elíptica (rx, ry em pixels do jogo) já em grão GRAO.

    modo "add": cor já multiplicada pela luz, para trans = add (o miolo branco do orbe).
    modo "alfa": cor cheia e a luz no alfa de cada pixel, para trans = addalpha (o brilho quente em volta,
    que no fundo azul não vira rosa como a soma pura)."""
    w, h = 2 * int(math.ceil(rx / GRAO)) + 1, 2 * int(math.ceil(ry / GRAO)) + 1
    ys, xs = np.mgrid[0:h, 0:w].astype(float)
    t = np.hypot((xs - w // 2) / (rx / GRAO), (ys - h // 2) / (ry / GRAO))
    v = _pixel(np.clip(queda(np.minimum(t, 1.0)), 0, 1)) * pico
    img = np.zeros((h, w, 4), np.uint8)
    rgb = np.array(cor, float)[None, None, :] * v[..., None]
    if miolo is not None:
        k = np.clip((raio_miolo - t) / max(raio_miolo, 1e-3), 0, 1)[..., None] ** 0.7
        rgb = rgb * (1 - k) + np.array(miolo, float)[None, None, :] * k
    if modo == "alfa":
        img[..., :3] = np.array(cor, np.uint8)[None, None, :]
        img[..., 3] = np.clip(v * 255, 0, 255).astype(np.uint8)
    else:
        img[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
        img[..., 3] = np.where(v > 0.004, 255, 0)
    im = Image.fromarray(img, "RGBA").resize((w * GRAO, h * GRAO), Image.NEAREST)
    return im, w * GRAO // 2, h * GRAO // 2


def cor_viva(rgb, sat=0.85, val=1.0):
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
    return tuple(int(round(c * 255)) for c in colorsys.hsv_to_rgb(h, max(s, sat * (0.5 if s < 0.3 else 1)), val))


def cor_do_poder(nos, pal, air, anim):
    """A cor mais viva dos desenhos do projétil (média dos pixels claros e saturados)."""
    px = []
    for g, i, *_ in air.get(anim, [])[:6]:
        n = next((x for x in nos if x["g"] == g and x["i"] == i), None)
        if n is None:
            continue
        a = asil._rgba(n, pal).reshape(-1, 4)
        a = a[a[:, 3] > 0, :3].astype(float)
        if len(a):
            sat = a.max(1) - a.min(1)
            a = a[(a.max(1) > 150) & (sat > 60)]
            if len(a):
                px.append(a)
    if not px:
        return (255, 200, 120)
    return cor_viva(tuple(np.concatenate(px).mean(0)))


# ---------------------------------------------------------------- .cns
def ctl(estado, titulo, tipo, *linhas):
    assert ";" not in titulo, titulo
    return "\n".join([f"[State {estado}, {titulo}]", f"type = {tipo}", *linhas, "ignorehitpause = 1", ""])


def tremor(fase=0.0):
    # 2,2 Hz e 1,3 Hz (rad por tique a 60 tiques/s): nunca acima de 2,5 Hz
    return f"(0.88 + 0.08 * sin(GameTime * 0.2304 + {fase}) + 0.04 * sin(GameTime * 0.1361 + {fase * 1.7:.2f}))"


def bloco_menos4(nome, altura, cor, poderes):
    """`nome` None: lutador sem aura em camadas (Raiclaven); só o escuro do poder e a luz dos poderes."""
    e = f"map(au_{nome}_e)" if nome else "0"
    g, bx = (f"map(au_{nome}_g)", f"map(au_{nome}_bx)") if nome else ("0", "0")
    p = "map(luz_p)"
    vivo = f"{e} > 0.01"
    sim = ("bindtime = -1", "removetime = -1", "ownpal = 1", "removeongethit = 0", "supermovetime = -1",
           "pausemovetime = -1")
    out = [MARCA + ": luz e brilho na base do KIKIU (issue #51). Não edite: rode python3 ferramentas/luz.py"]
    tem_poder = " || ".join(f"NumProjID({pid})" for pid, _ in poderes) or "0"
    out.append(ctl(-4, "Luz zera o poder", "MapSet", "trigger1 = RoundState = 0", 'map = "luz_p"', "value = 0"))
    out.append(ctl(-4, "Luz do poder no ar", "MapAdd", "trigger1 = 1", 'map = "luz_p"',
                   f"value = 0.12 * (ifelse({tem_poder}, 1, 0) - {p})"))
    # 1. escuro
    k = f"floor(256 * min(0.45, {ESCURO_DESPERTO} * min(1, max(0, {e})) + {ESCURO_PODER} * {p}))"
    out.append(ctl(-4, "Luz escuro nasce", "Explod", f"trigger1 = NumExplod({ID_ESCURO}) = 0 && RoundState > 0",
                   f"anim = {ACAO + 2}", f"id = {ID_ESCURO}", "postype = p1", "pos = 0, -120", "facing = 1",
                   "scale = 400, 120", "sprpriority = -20", *sim, "trans = addalpha", "alpha = 0, 256"))
    out.append(ctl(-4, "Luz escuro", "ModifyExplod", f"trigger1 = NumExplod({ID_ESCURO})", f"id = {ID_ESCURO}",
                   "trans = addalpha", f"alpha = 0, 256 - {k}"))
    # 2. halo e 3. poça (só no despertado)
    a_halo = f"floor(255 * min(1, max(0, {e})) * {tremor()})"
    out.append(ctl(-4, "Luz halo nasce", "Explod", f"trigger1 = NumExplod({ID_HALO}) = 0 && {vivo}",
                   f"anim = {ACAO}", f"id = {ID_HALO}", "postype = p1", "pos = 0, 0", "facing = 1",
                   "sprpriority = -7", *sim, "trans = addalpha", "alpha = 0, 256"))
    out.append(ctl(-4, "Luz halo", "ModifyExplod", f"trigger1 = NumExplod({ID_HALO})", f"id = {ID_HALO}",
                   "postype = p1", f"pos = {bx}, -{altura * 0.5:.1f} * (1 - 0.7 * {g})",
                   "trans = addalpha", f"alpha = {a_halo}, 255 - {a_halo}"))
    alto = "min(1, max(0, -Pos Y / 140))"
    a_poca = f"floor(255 * min(1, max(0, {e})) * {tremor(1.1)} * (1 - {alto}))"
    out.append(ctl(-4, "Luz poca nasce", "Explod", f"trigger1 = NumExplod({ID_POCA}) = 0 && {vivo}",
                   f"anim = {ACAO + 1}", f"id = {ID_POCA}", "postype = p1", "pos = 0, 0", "facing = 1",
                   "sprpriority = -8", *sim, "trans = addalpha", "alpha = 0, 256"))
    out.append(ctl(-4, "Luz poca", "ModifyExplod", f"trigger1 = NumExplod({ID_POCA})", f"id = {ID_POCA}",
                   "postype = p1", f"pos = {bx}, 0 - Pos Y", "bindtime = 0", "trans = addalpha",
                   f"alpha = {a_poca}, 255 - {a_poca}"))
    for ident in (ID_HALO, ID_POCA):
        out.append(ctl(-4, f"Luz apaga {ident}", "RemoveExplod", f"trigger1 = NumExplod({ident}) && {e} <= 0.01",
                       f"id = {ident}"))
    # 4. oponente perto clareia (leve)
    perto = "max(0, 1 - abs(P2BodyDist X) / 110)"
    forca = f"{FORCA_OPONENTE} * min(1, max(0, {e})) * {perto} * {tremor()}"
    r, gg, b = ((c + 255) // 2 for c in cor)   # metade branco: clareia sem pintar o oponente da cor da aura
    out.append(ctl(-4, "Luz no oponente", "PalFX",
                   f"trigger1 = {vivo} && NumEnemy > 0 && RoundState = 2",
                   "trigger1 = enemynear,MoveType != H && enemynear,StateNo < 1000 && enemynear,var(20) <= 0",
                   f"trigger1 = abs(P2BodyDist X) < 110", "redirectid = enemynear,id", "time = 2",
                   f"add = floor({r} * {forca}), floor({gg} * {forca}), floor({b} * {forca})"))
    # 5. poder some: a luz dele também
    for k_, (pid, _) in enumerate(poderes):
        for d in range(3):
            ident = id_poder(k_) + d
            out.append(ctl(-4, f"Luz do poder {pid} apaga {ident}", "RemoveExplod",
                           f"trigger1 = NumExplod({ident}) && NumProjID({pid}) = 0", f"id = {ident}"))
    out.append(FIM)
    return "\n".join(out) + "\n"


def explod_do_feixe(estado, gatilhos, proj, k_):
    """O raio leva a luz no próprio desenho (assar_feixes); aqui só o orbe quente parado na boca, e só no raio preso
    nela: no raio que anda ele ficava para trás, no chão perto do casco do Gutto (offset 0, 0)."""
    ox, oy = proj["offset"]
    vx, vy = proj["velocity"]
    if abs(vx) > 0 or abs(vy) > 0:
        return ""
    return "\n".join([f"[State {estado}, Luz do poder orbe]", "type = Explod", *gatilhos, f"anim = {ACAO + 10 + 2 * k_}",
                      f"id = {id_poder(k_)}", "postype = p1", f"pos = {ox}, {oy}", "bindtime = -1",
                      "removetime = -1", "ownpal = 1", "removeongethit = 0", "ignorehitpause = 1", "sprpriority = 6",
                      "trans = add", f"alpha = floor(255 * {tremor(0.5)}), 255", ""])


GRUPO_PJ = 9729          # 9729,k: desenho do raio com a luz assada em volta
ACAO_PJ = 9780           # ações 9780 + j: cópia da ação do raio j (mesmas caixas e tempos) com os desenhos assados
NOTA_PJ = "luz assada de"


def assar_feixes(feixes, air_txt, des):
    """({ação original: ação nova}, sprites, texto .air) dos raios com a luz do contorno assada no desenho.

    A luz fica por baixo do desenho, por alfa normal, até R_FEIXE pixels do brilho (le.luz_do_contorno). Efeito grande
    vai mais fraco (como a luz redonda), para o anel do KO não virar névoa na tela."""
    blocos = {int(m.group(1)): m.group(0) for m in
              re.finditer(r"\[Begin Action (\d+)\].*?(?=\[Begin Action|\Z)", air_txt, re.S | re.I)}
    air = le.ler_air_completo(air_txt)
    novas, sp, texto, feitos = {}, {}, [], {}
    for j, a in enumerate(feixes):
        if a not in blocos or a not in air:
            continue
        m = le.medir(a, air[a], des)
        cor = le.cor_da_luz(m["cor"])
        pico = 0.6 * min(1.0, (60.0 / max(m["raio"], 1.0)) ** 0.5) * (0.65 if m.get("branca") else 1.0)

        def troca(mm):
            g, i = int(mm.group(2)), int(mm.group(3))
            if g < 0:
                return mm.group(0)
            if (g, i) not in feitos:
                d = des.rgba(g, i)
                if d is None:
                    return mm.group(0)
                feitos[(g, i)] = len(feitos)
                sp[(GRUPO_PJ, feitos[(g, i)])] = assado(d, cor, pico)
            return f"{mm.group(1)}{GRUPO_PJ},{feitos[(g, i)]},"
        corpo = blocos[a].split("\n", 1)[1]
        corpo = re.sub(r"^(\s*)(-?\d+)\s*,\s*(-?\d+)\s*,", troca, corpo, flags=re.M)
        novas[a] = ACAO_PJ + j
        texto.append(f"[Begin Action {ACAO_PJ + j}]\n; {NOTA_PJ} {a} (luz.py, não edite)\n" + corpo.rstrip() + "\n")
    return novas, sp, "\n".join(texto)


def assado(d, cor, pico):
    """O desenho com a luz do contorno por baixo (alfa normal), no mesmo eixo."""
    a, ax, ay = d
    luz, lx, ly = le.luz_do_contorno(a, ax, ay, cor, pico)
    base = np.asarray(luz).astype(float) / 255
    ox, oy = lx - ax, ly - ay
    h, w = a.shape[:2]
    top = np.zeros_like(base)
    top[oy:oy + h, ox:ox + w] = a.astype(float) / 255
    at, ab = top[..., 3:], base[..., 3:]
    ao = at + ab * (1 - at)
    rgb = np.where(ao > 0, (top[..., :3] * at + base[..., :3] * ab * (1 - at)) / np.maximum(ao, 1e-6), 0)
    out = np.concatenate([rgb, ao], -1)
    return Image.fromarray(np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8), "RGBA"), lx, ly


def trocar_projanim(cns, novas):
    for a, n in novas.items():
        cns = re.sub(rf"^(projanim\s*=\s*){a}\s*$", rf"\g<1>{n} ; {NOTA_PJ} {a}", cns, flags=re.M | re.I)
    return cns


def destrocar_projanim(cns):
    return re.sub(rf"^(projanim\s*=\s*)\d+ ; {NOTA_PJ} (\d+)\s*$", r"\g<1>\2", cns, flags=re.M | re.I)


ALONGADO = 2.2   # brilho com largura maior que isto vezes a altura é raio, não bola
BOLA = 50   # projétil com brilho até este raio é uma bola: o orbe somado vai por cima e é o miolo quente dela


def explods_do_poder(estado, gatilhos, proj, k_, cor_poder, centro=(0, 0), raio=0.0):
    """Orbe, halo e poça que saem junto com o Projectile e andam com ele, na altura do brilho do desenho dele."""
    ox, oy = proj["offset"]
    oy = round(oy + centro[1], 1)
    ax, ay = proj.get("accel", (0.0, 0.0))   # só a altura: no x, o centro do brilho cai no rastro (bola) ou no meio (raio)
    vx, vy = proj["velocity"]
    base = id_poder(k_)
    comum = [*gatilhos, "postype = p1", f"velocity = {vx}, {vy}", f"accel = {ax}, {ay}", "removetime = -1", "ownpal = 1",
             "removeongethit = 0", "ignorehitpause = 1"]
    out = []
    a = tremor(0.5)
    for d, (anim, prio, pos, alfa, modo) in enumerate((
            (ACAO + 10 + 2 * k_, 6 if raio <= BOLA else 2, f"{ox}, {oy}", f"floor(255 * {a})", "add"),
            (ACAO + 11 + 2 * k_, 1, f"{ox}, {oy}", f"floor(230 * {a})", "addalpha"),
            (ACAO + 1, -8, f"{ox}, 0", f"floor(220 * {a})", "addalpha"))):
        nome = ("orbe", "halo", "poca")[d]
        linhas = [x for x in comum]
        linhas[len(gatilhos):len(gatilhos)] = [f"anim = {anim}", f"id = {base + d}"]
        fundo = "255" if modo == "add" else f"255 - {alfa}"
        linhas += [f"pos = {pos}", f"sprpriority = {prio}", f"trans = {modo}", f"alpha = {alfa}, {fundo}"]
        out.append("\n".join([f"[State {estado}, Luz do poder {nome}]", "type = Explod", *linhas, ""]))
    return "\n".join(out)


RE_CTL = re.compile(r"^\[State (-?\d+),([^\]]*)\]\n(.*?)(?=^\[|\Z)", re.M | re.S)


def projeteis(cns):
    """[(início, fim, estado, gatilhos, dict)] de cada Projectile."""
    achados = []
    for m in RE_CTL.finditer(cns):
        corpo = m.group(3)
        if not re.search(r"^type\s*=\s*Projectile\s*$", corpo, re.M | re.I):
            continue
        d = {}
        for chave in ("projid", "offset", "velocity", "projanim", "postype", "projscale", "accel"):
            mm = re.search(rf"^{chave}\s*=\s*([^;\n]+)", corpo, re.M | re.I)
            if mm:
                d[chave] = mm.group(1).strip()
        try:
            d["projid"] = int(d.get("projid", "-1"))
            d["offset"] = tuple(float(v) for v in d.get("offset", "0,0").split(",")[:2])
            d["velocity"] = tuple(float(v) for v in d.get("velocity", "0,0").split(",")[:2])
            d["projanim"] = int(d.get("projanim", "0"))
            mm = re.search(rf"^projanim\s*=\s*\d+ ; {NOTA_PJ} (\d+)", corpo, re.M | re.I)
            if mm:   # raio com a luz assada: quem lê quer a ação original
                d["projanim"] = int(mm.group(1))
            d["escala"] = float(d.get("projscale", "1").split(",")[0])
            d["accel"] = tuple(float(v) for v in (d.get("accel", "0,0").split(",") + ["0"])[:2])
        except ValueError:
            continue
        gat = [ln for ln in corpo.splitlines() if re.match(r"\s*trigger(all|\d+)\s*=", ln, re.I)]
        achados.append((m.start(), m.end(), int(m.group(1)), gat, d))
    return achados


def tirar_cns(cns):
    cns = destrocar_projanim(lj.tirar_cns(le.tirar_cns(cns)))
    cns = re.sub(rf"\n?{re.escape(MARCA)}.*?{re.escape(FIM)}\n", "\n", cns, flags=re.S)
    cns = re.sub(r"^\[State -?\d+, Luz do poder (orbe|halo|poca)\]\n.*?(?=^\[|\Z)", "", cns, flags=re.M | re.S)
    return cns


def tirar_air(air):
    air = lj.tirar_air(le.tirar_air(air))
    return re.sub(rf"\[Begin Action ({ACAO}|{ACAO + 1}|{ACAO + 2}|97[34]\d|978\d|979[0-8])\].*?(?=\[Begin Action|\Z)", "", air,
                  flags=re.S | re.I).rstrip() + "\n"


def desenhos(cor, cores_poder, tamanhos=None, com_corpo=True):
    """{(grupo, i): (img, ex, ey)} e o texto do .air. `tamanhos`: fator do orbe e do halo de cada poder."""
    sp, air = {}, []
    tamanhos = tamanhos or [1.0] * len(cores_poder)
    if com_corpo:
        sp[(GRUPO, 0)] = mancha(R_HALO, R_HALO * 1.1, cor, 0.85, modo="alfa")
    sp[(GRUPO, 1)] = mancha(R_POCA, R_POCA * 0.2, cor, 0.9, modo="alfa")
    preto = Image.new("RGBA", (8, 8), (0, 0, 0, 255))
    sp[(GRUPO, 2)] = (preto, 4, 4)
    for a, i in ((ACAO, 0), (ACAO + 1, 1), (ACAO + 2, 2)):
        air.append(f"[Begin Action {a}]\n{GRUPO},{i}, 0,0, -1\n")
    for k_, c in enumerate(cores_poder):
        miolo = tuple(int(255 - (255 - v) * 0.15) for v in c)
        h_, s_, v_ = colorsys.rgb_to_hsv(*(x / 255 for x in c))
        if h_ < 0.07 or h_ > 0.95:   # vermelho no fundo azul vira roxo: o halo puxa para o laranja
            c = tuple(int(round(x * 255)) for x in colorsys.hsv_to_rgb(0.07, s_, v_))
        f = tamanhos[k_]
        sp[(GRUPO + 1, k_)] = mancha(R_ORBE * f, R_ORBE * f, c, 1.0, miolo=miolo, raio_miolo=0.5)
        sp[(GRUPO + 2, k_)] = mancha(R_HALO_PODER * f, R_HALO_PODER * 0.8 * f, c, 0.85, modo="alfa")
        air.append(f"[Begin Action {ACAO + 10 + 2 * k_}]\n{GRUPO + 1},{k_}, 0,0, -1\n")
        air.append(f"[Begin Action {ACAO + 11 + 2 * k_}]\n{GRUPO + 2},{k_}, 0,0, -1\n")
    return sp, "\n".join(air)


def poderes_que_acendem(lutador, cns, air_txt, pasta):
    """[(projid, projanim, raio em pixels do jogo)] dos projéteis cujo desenho brilha (revisão em luz_classes.json)."""
    air = le.ler_air_completo(air_txt)
    des = le.Desenhos(Path(pasta) / f"{lutador}.sff")
    out = []
    for ini, fim, estado, gat, d in projeteis(cns):
        anim = d["projanim"]
        if anim not in air or d["projid"] in [o[0] for o in out]:
            continue
        m = le.medir(anim, air[anim], des)
        if le.acende(m, lutador):
            pesos = [q[0] for q in m["quadros"]]
            tot = sum(pesos) or 1
            cx = sum(w * q[1] for w, q in zip(pesos, m["quadros"])) / tot * d.get("escala", 1.0)
            cy = sum(w * q[2] for w, q in zip(pesos, m["quadros"])) / tot * d.get("escala", 1.0)
            out.append((d["projid"], anim, m["raio"] * d.get("escala", 1.0), (cx, cy), m["larg"] / max(1, m["alt"])))
    return out


def aplicar(lutador, pasta=None):
    pasta = Path(pasta or RAIZ / "chars" / lutador)
    arq_sff, arq_air, arq_cns = (pasta / f"{lutador}.{e}" for e in ("sff", "air", "cns"))
    cns = tirar_cns(arq_cns.read_text(encoding="utf-8").replace("\r\n", "\n"))
    air = tirar_air(arq_air.read_text(encoding="utf-8").replace("\r\n", "\n"))
    nome, ids = anc.aura_do_cns(cns)
    pal, nos, _ = cs.ler(arq_sff)
    paleta = asil._paleta(arq_sff)
    cor = cor_viva(asil.tons_da_aura(nos, set(ids), paleta)[1]) if nome else (255, 230, 190)
    air_acoes = asil.ler_air_clsn(air)
    ordem = poderes_que_acendem(lutador, cns, air, pasta)
    quer = [o[0] for o in ordem]
    cores_poder = [cor_do_poder(nos, paleta, air_acoes, o[1]) for o in ordem]
    tamanhos = [min(1.15, max(0.45, o[2] * 2.9 / R_HALO_PODER)) for o in ordem]
    # a luz de todo efeito que brilha (Explods e faíscas de golpe); os raios ganham a luz do próprio desenho
    # raio = fica preso na boca (velocidade 0); a bola que voa, mesmo com brilho grande, leva orbe/halo/poça que andam
    # com ela (Bola das Trevas do Diabo demônio: o orbe ficava grudado na garra e o halo não seguia o arco)
    voam = {d["projanim"] for *_, d in projeteis(cns) if any(abs(float(v)) > 0 for v in d["velocity"])}
    # o raio que anda (o KO dos despertados) é comprido: continua raio, com a luz no contorno do desenho, andando junto
    feixes = {o[1] for o in ordem if o[2] > FEIXE and (o[1] not in voam or o[4] >= ALONGADO)}
    cns, air_ef, sp_ef, bloco_ef, resumo = le.gerar(lutador, cns, air, pasta)
    # o raio leva a luz assada no próprio desenho (cópia da ação com outro grupo): um Explod irmão não acompanha o
    # Projectile quando ele para no acerto (pausetime do HitDef) e corria na frente do raio do KO
    acoes_luz, sp_pj, air_pj = assar_feixes(sorted(feixes), air, le.Desenhos(arq_sff))
    sp_ef.update(sp_pj)
    air_ef = air_ef + "\n" + air_pj
    cns = trocar_projanim(cns, acoes_luz)
    # explods dos poderes logo depois de cada Projectile (de trás para a frente, para os índices valerem)
    projs = [p for p in projeteis(cns) if p[4]["projid"] in quer]
    for ini, fim, estado, gat, d in sorted(projs, key=lambda p: -p[0]):
        k_ = quer.index(d["projid"])
        if d["projanim"] in feixes:
            novo = explod_do_feixe(estado, gat, d, k_)
        else:
            novo = explods_do_poder(estado, gat, d, k_, cores_poder[k_], ordem[k_][3], ordem[k_][2])
        cns = cns[:fim] + novo + "\n" + cns[fim:]
    # a energia junta na mão antes de cada poder sair
    cns, sp_j, air_j, n_j = lj.aplicar(cns, le.ler_air_completo(air), le.Desenhos(arq_sff), projeteis(cns), ordem,
                                       cores_poder, le.brilho)
    sp_ef.update(sp_j)
    air_ef = air_ef + "\n" + air_j
    altura = anc.Corpo(pasta, lutador).altura if nome else 0
    bloco = bloco_menos4(nome, altura, cor, [(o[0], o[1]) for o in ordem]) + bloco_ef
    m = (re.search(r"^; <<< aura_silhueta\.py\n", cns, re.M) or re.search(r"^; <<< aura_no_corpo\.py\n", cns, re.M)
         or re.search(r"^\[Statedef -4\][^\n]*\n", cns, re.M | re.I))
    if not m:
        cns = cns.rstrip() + "\n\n[Statedef -4]\n\n"
        m = re.search(r"^\[Statedef -4\][^\n]*\n\n", cns, re.M | re.I)
    cns = cns[:m.end()] + bloco + cns[m.end():]
    cns = re.sub(r"\n{3,}(; >>> (aura_no_corpo|luz))", r"\n\n\1", cns)
    cns = re.sub(r"(\[Statedef -4\][^\n]*\n)\n*(; >>> luz\.py)", r"\1\2", cns, flags=re.I)
    cns = re.sub(r"(; <<< luz_efeitos\.py\n)\n*", r"\1\n", cns)
    sp, texto = desenhos(cor, cores_poder, tamanhos, com_corpo=bool(nome))
    sp.update(sp_ef)
    meus = (GRUPO, GRUPO + 1, GRUPO + 2, le.GRUPO_EF, le.GRUPO_FA, le.GRUPO_FX, lj.GRUPO, GRUPO_PJ)
    rle, png, vistos = [], [], set()
    for n in nos:
        k = (n["g"], n["i"])
        if k in vistos or n["g"] in meus:
            continue
        vistos.add(k)
        (png if n.get("png") else rle).append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
    for (g, i), (img, ex, ey) in sp.items():
        png.append((g, i, img.width, img.height, ex, ey, efeitos.blob_png(img)))
    efeitos.gravar(arq_sff, pal, rle, png)
    arq_air.write_text(air.rstrip() + "\n\n" + texto + "\n" + air_ef, encoding="utf-8", newline="\n")
    arq_cns.write_text(cns, encoding="utf-8", newline="\n")
    print(f"{lutador}: luz ligada; cor {cor if nome else 'sem aura'}, poderes {quer}, "
          f"{resumo['efeitos']} efeitos em {resumo['explods']} Explods, {resumo['faiscas']} golpes com clarão, "
          f"{n_j} poderes juntando na mão")


def tirar(lutador, pasta=None):
    pasta = Path(pasta or RAIZ / "chars" / lutador)
    arq_sff, arq_air, arq_cns = (pasta / f"{lutador}.{e}" for e in ("sff", "air", "cns"))
    arq_cns.write_text(tirar_cns(arq_cns.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    arq_air.write_text(tirar_air(arq_air.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    pal, nos, _ = cs.ler(arq_sff)
    rle, png, vistos = [], [], set()
    for n in nos:
        k = (n["g"], n["i"])
        if k in vistos or n["g"] in (GRUPO, GRUPO + 1, GRUPO + 2, le.GRUPO_EF, le.GRUPO_FA):
            continue
        vistos.add(k)
        (png if n.get("png") else rle).append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
    efeitos.gravar(arq_sff, pal, rle, png)


def previa(saida, lutador):
    pasta = RAIZ / "chars" / lutador
    pal, nos, _ = cs.ler(pasta / f"{lutador}.sff")
    nome, ids = anc.aura_do_cns((pasta / f"{lutador}.cns").read_text(encoding="utf-8"))
    cor = cor_viva(asil.tons_da_aura(nos, set(ids), asil._paleta(pasta / f"{lutador}.sff"))[1])
    sp, _ = desenhos(cor, [(255, 120, 60)])
    larg = sum(im.width for im, *_ in sp.values()) + 20 * len(sp)
    folha = Image.new("RGB", (larg, max(im.height for im, *_ in sp.values())), (20, 24, 60))
    x = 0
    for im, *_ in sp.values():
        base = np.asarray(folha.crop((x, 0, x + im.width, im.height))).astype(int)
        a = np.asarray(im).astype(int)
        al = a[..., 3:4] / 255.0
        if set(np.unique(a[..., 3])) <= {0, 255}:
            base = np.clip(base + a[..., :3] * (al > 0), 0, 255).astype(np.uint8)
        else:
            base = np.clip(base * (1 - al) + a[..., :3] * al, 0, 255).astype(np.uint8)
        folha.paste(Image.fromarray(base), (x, 0))
        x += im.width + 20
    folha.save(saida)
    print(saida)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lutadores", nargs="*")
    ap.add_argument("--tirar", action="store_true")
    ap.add_argument("--previa", type=Path)
    a = ap.parse_args()
    if a.previa:
        previa(a.previa, (a.lutadores or ["hazaki"])[0])
        return
    for l in a.lutadores or ["hazaki"]:
        tirar(l) if a.tirar else aplicar(l)


if __name__ == "__main__":
    main()
