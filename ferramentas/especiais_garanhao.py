#!/usr/bin/env python3
"""Especiais e super do Garanhão (Gutto despertado), da lista aprovada pelo Breno (docs/despertados-47/golpes-novos.md):

  Bufada de Fogo       ↓→ x/y      bufa duas labaredas pelas narinas que correm rentes ao chão (projétil)
  Investida do Touro   ↓→ a/b      abaixa a cabeça e dispara de chifre; aguenta um golpe no caminho; b vai mais longe
  Pisão Racha-Chão     ↓↓ a/b      pisa e a rachadura corre pelo chão com brasa (golpe baixo, não pega no ar)
  Chifrada Ascendente  →↓→ x/y     antiaéreo, chifrada subindo, invencível no começo
  Fúria do Minotauro   ←→↓ + a/b   super: pega o oponente nos chifres, carrega até a parede, joga no alto e desce
                                   os cascos nele no chão; o chão racha com brasa vermelha

Os corpos são os desenhos do boneco de peças do Garanhão (sprites/garanhao/quadros_pecas_hd, da thread do Gutto) e
do kit da #47 (sprites/garanhao_47: o levanta), gravados em grupos próprios (47200 a 47260) para um religar da thread
do Gutto (49000+) não passar por cima. Os efeitos novos (labareda e rachadura) são pixel art feita aqui, na paleta da
forma, alfa só 0 ou 255 e contorno seco. Só vale com o despertar ligado (var(20) > 0), antes das entradas da base.

  python ferramentas/especiais_garanhao.py            (depois do despertados_47.py gutto)
  python ferramentas/aura_silhueta.py gutto && python ferramentas/encolher_sff.py gutto --indexar 49000-49099
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import agarrao_mk as mk  # noqa: E402
import conferir_sff as cs  # noqa: E402
import efeitos  # noqa: E402

RAIZ = AQUI.parent
PASTA = RAIZ / "chars" / "gutto"
MARCA = "(especiais_garanhao.py)"
EIXO = (540, 660)
PECAS = RAIZ / "sprites" / "garanhao" / "quadros_pecas_hd"
PECAS47 = RAIZ / "sprites" / "garanhao_47" / "quadros_pecas_hd"
# corpo: grupo -> (pasta, animação)
CORPOS = {47200: (PECAS, "bufada"), 47210: (PECAS, "investida"), 47220: (PECAS, "pisao"),
          47230: (PECAS, "chifrada_sobe"), 47240: (PECAS47, "levanta")}
G_CHAMA, G_RACHA, G_BRASA = 47250, 47251, 47252
PANCADA = 47004          # estouro da forma (despertados_47.py)
SUPER_FX = 9232          # explosão grande do despertado, se existir no .sff; senão a pancada
PALETA = [(34, 6, 10), (92, 10, 16), (160, 24, 22), (214, 58, 26), (246, 120, 34), (255, 196, 70), (255, 246, 206)]
CONTORNO = (24, 4, 8)


def ctl(n, nome, tipo, *linhas):
    return mk.ctl(n, f"{nome} {MARCA}", tipo, *linhas)


# ------------------------------------------------------------------------------------------------ efeitos (pixel art)
def _pinta(nivel, alfa):
    """Campo 0..1 -> RGBA na paleta da forma, alfa só 0/255, contorno seco de 1 px."""
    h, w = nivel.shape
    idx = np.clip((nivel * (len(PALETA) - 1) + .5).astype(int), 0, len(PALETA) - 1)
    out = np.zeros((h, w, 4), np.uint8)
    out[..., :3] = np.array(PALETA, np.uint8)[idx]
    out[..., 3] = np.where(alfa, 255, 0)
    a = alfa.astype(np.uint8)
    viz = np.zeros_like(a)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        viz |= np.roll(np.roll(a, dy, 0), dx, 1)
    borda = (viz > 0) & (a == 0)
    out[borda] = (*CONTORNO, 255)
    return Image.fromarray(out, "RGBA")


def _ruido(h, w, sem, escala=6):
    rng = np.random.default_rng(sem)
    g = rng.random((h // escala + 3, w // escala + 3))
    img = Image.fromarray((g * 255).astype(np.uint8)).resize((w + 3 * escala, h + 3 * escala), Image.BICUBIC)
    return np.asarray(img, float)[:h, :w] / 255


def chama(n=8, w=168, h=84):
    """Labareda dupla (as duas narinas) rente ao chão, correndo para a frente: a cabeça grossa na frente e a cauda
    lambendo para trás, tremendo quadro a quadro."""
    ims = []
    yy, xx = np.mgrid[:h, :w].astype(float)
    for f in range(n):
        campo = np.zeros((h, w))
        for cy, amp in ((h * .40, 1.0), (h * .70, .85)):
            u = xx / w                                   # 0 cauda .. 1 frente
            meia = (6 + 26 * u ** .8) * amp              # mais grossa na frente
            onda = 4 * np.sin(u * 9 - f * 1.6 + cy)
            d = np.abs(yy - cy - onda) / meia
            corpo = np.clip(1 - d, 0, 1) * np.clip(u * 1.4, 0, 1) * np.clip((1 - u) * 6, 0, 1)
            campo = np.maximum(campo, corpo)
        campo *= .75 + .5 * _ruido(h, w, 100 + f, 5)
        alfa = campo > .22
        ims.append(_pinta(np.clip(campo * 1.25, 0, 1), alfa))
    return ims


def racha(n=8, w=216, h=96):
    """Rachadura no chão que corre para a frente, com brasa subindo das bordas (o chão abre em vermelho)."""
    rng = np.random.default_rng(7)
    pts = [(0, h - 14)]
    x = 0
    while x < w - 8:
        x += rng.integers(10, 22)
        pts.append((min(x, w - 6), h - 14 + rng.integers(-6, 6)))
    ims = []
    for f in range(n):
        campo = np.zeros((h, w))
        yy, xx = np.mgrid[:h, :w]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            for t in np.linspace(0, 1, 30):
                cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                r = 4 + 2 * np.sin(cx * .2 + f)
                m = (xx - cx) ** 2 + (yy - cy) ** 2 < r * r
                campo[m] = np.maximum(campo[m], 1 - ((xx[m] - cx) ** 2 + (yy[m] - cy) ** 2) / (r * r) * .6)
        # brasas subindo
        r2 = np.random.default_rng(300 + f)
        for _ in range(26):
            bx = r2.integers(4, w - 4)
            by = h - 18 - int(((f * 5 + r2.integers(0, 50)) % 60))
            campo[max(0, by - 2):by + 2, bx - 1:bx + 2] = np.maximum(campo[max(0, by - 2):by + 2, bx - 1:bx + 2], .8)
        # o chão em volta da fenda escurece em lasca
        alfa = campo > .2
        ims.append(_pinta(np.clip(campo, 0, 1), alfa))
    return ims


def brasa(n=6, w=90, h=90):
    """Estouro de brasa no chão (impacto do pisão e da super)."""
    ims = []
    yy, xx = np.mgrid[:h, :w].astype(float)
    for f in range(n):
        r = 12 + f * 7
        d = np.hypot(xx - w / 2, (yy - h * .8) * 1.4)
        anel = np.clip(1 - np.abs(d - r) / (6 + f), 0, 1) * (1 - f / n) + np.clip(1 - d / (r * .6), 0, 1) * (1 - f / n)
        anel *= .7 + .6 * _ruido(h, w, 500 + f, 4)
        ims.append(_pinta(np.clip(anel, 0, 1), anel > .25))
    return ims


# ----------------------------------------------------------------------------------------------------------- corpos
def corpo(grupo):
    pasta, anim = CORPOS[grupo]
    t = json.loads((pasta / anim / "tempos.json").read_text(encoding="utf-8"))
    return pasta / anim, t


def contato(t):
    tick = 0
    for e in t["elementos"]:
        if e.get("caixa"):
            return tick
        tick += e["ticks"]
    return tick // 2


def total(t):
    return sum(e["ticks"] for e in t["elementos"])


def sprites():
    out = []
    for g in CORPOS:
        pasta, t = corpo(g)
        for i in sorted({e["desenho"] for e in t["elementos"]}):
            im = Image.open(pasta / f"{i:02d}.png").convert("RGBA")
            x0, y0, x1, y1 = im.getbbox()
            out.append((g, i, im.crop((x0, y0, x1, y1)), EIXO[0] - x0, EIXO[1] - y0))
    for g, ims, piv in ((G_CHAMA, chama(), lambda im: (im.width // 2, im.height // 2)),
                        (G_RACHA, racha(), lambda im: (im.width // 2, im.height - 14)),
                        (G_BRASA, brasa(), lambda im: (im.width // 2, int(im.height * .8)))):
        for i, im in enumerate(ims):
            px, py = piv(im)
            out.append((g, i, im, px, py))
    return out


def gravar_sff():
    sff = PASTA / "gutto.sff"
    pal, nos, extra = cs.ler(sff)
    meus = set(CORPOS) | {G_CHAMA, G_RACHA, G_BRASA}
    rle, png, vistos = [], [], set()
    for n in nos:
        k = (n["g"], n["i"])
        if k in vistos or n["g"] in meus:
            continue
        vistos.add(k)
        (png if n.get("png") else rle).append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
    for g, i, im, ex, ey in sprites():
        png.append((g, i, im.width, im.height, int(ex), int(ey), efeitos.blob_png(im)))
    efeitos.gravar(sff, pal, rle, png)


# -------------------------------------------------------------------------------------------------------------- .air
def acao_corpo(numero, grupo, nome, caixa_extra=None):
    _, t = corpo(grupo)
    linhas = [f"[Begin Action {numero}]", f"; {nome}: corpo do boneco de peças {MARCA}", "Clsn2Default: 1",
              " Clsn2[0] = -72, 0, 72, -312"]
    for e in t["elementos"]:
        if e.get("caixa"):
            x1, y1, x2, y2 = caixa_extra or t["caixa"]
            linhas += ["Clsn1: 1", f" Clsn1[0] = {x1}, {y1}, {x2}, {y2}"]
        linhas.append(f"{grupo},{e['desenho']}, 0,0, {e['ticks']}")
    return "\n".join(linhas)


def acao_fx(numero, grupo, n, ticks, clsn=None, laco=True, escala=.75):
    linhas = [f"[Begin Action {numero}]", f"; efeito {MARCA}"]
    if clsn:
        linhas += ["Clsn2Default: 1", f" Clsn2[0] = {clsn}", "Clsn1Default: 1", f" Clsn1[0] = {clsn}"]
    if laco:
        linhas.append("Loopstart")
    linhas += [f"{grupo},{i}, 0,0, {ticks}, , , {escala:g}, {escala:g}" if escala != 1 else f"{grupo},{i}, 0,0, {ticks}"
               for i in range(n)]
    return "\n".join(linhas)


ACOES = {  # número: texto
}


def air_novo(air):
    blocos = {
        4800: acao_corpo(4800, 47200, "Bufada de Fogo"),
        4810: acao_corpo(4810, 47210, "Investida do Touro"),
        4820: acao_corpo(4820, 47220, "Pisão Racha-Chão"),
        4830: acao_corpo(4830, 47230, "Chifrada Ascendente"),
        4900: acao_corpo(4900, 47210, "Fúria do Minotauro: investida"),
        4902: acao_corpo(4902, 47220, "Fúria do Minotauro: pisão"),
        4903: acao_corpo(4903, 47240, "Fúria do Minotauro: joga no alto"),
        # projéteis: o motor desenha na projscale e mede a caixa na escala do lutador (1/3): caixa em 3x
        G_CHAMA: acao_fx(G_CHAMA, G_CHAMA, 8, 2, clsn="-150, -90, 150, 60", escala=1),
        G_RACHA: acao_fx(G_RACHA, G_RACHA, 8, 2, clsn="-200, -60, 200, 0", escala=1),
        G_BRASA: acao_fx(G_BRASA, G_BRASA, 6, 3, laco=False, escala=1),
    }
    for n, txt in blocos.items():
        air = efeitos.por_acao(air, n, txt.split("\n", 1)[1])
    return re.sub(r"\n{3,}", "\n\n", air)


# -------------------------------------------------------------------------------------------------------------- .cns
def hitdef(n, gatilho, dano, *extra, attr="S, SA", guard="MA", hit="MAF", tipo="Heavy", som="S53,2", pausa="12, 12"):
    return ctl(n, "Golpe", "HitDef", gatilho, f"attr = {attr}", f"damage = {dano}", f"animtype = {tipo}",
               f"guardflag = {guard}", f"hitflag = {hit}", "priority = 5, Hit", f"pausetime = {pausa}",
               "guard.pausetime = 9, 9", f"sparkno = S{PANCADA}" if False else "sparkno = S9231",
               "guard.sparkno = S9202", "sparkxy = -10, -60", f"hitsound = {som}", "guardsound = F6,0",
               "envshake.time = 10", "envshake.freq = 120", "envshake.ampl = -4", "palfx.time = 10",
               "palfx.add = 140,20,20", *extra)


def cab(n, nome, anim, tipo="S", physics="S", juggle=4):
    return (f"; {nome} (Garanhão, golpes-novos.md) {MARCA}\n[Statedef {n}]\ntype = {tipo}\nmovetype = A\n"
            f"physics = {physics}\nctrl = 0\nsprpriority = 2\nanim = {anim}\njuggle = {juggle}\nvelset = 0,0\n"
            "poweradd = 40\n\n")


def fim(n):
    return ctl(n, "Fim", "ChangeState", "trigger1 = AnimTime = 0", "value = 0", "ctrl = 1")


def estados():
    s = []
    # Bufada de Fogo: 4800 (x, labareda lenta) e 4801 (y, rápida e mais longe)
    _, t = corpo(47200)
    c = contato(t)
    for n, vel, dano in ((4800, 4.2, 55), (4801, 6.0, 62)):
        s.append(cab(n, "Bufada de Fogo", 4800))
        s.append(ctl(n, "Bufa", "PlaySnd", "trigger1 = Time = 0", "value = F40,3"))
        s.append(ctl(n, "Fumaça nas narinas", "Explod", f"trigger1 = Time = {max(1, c - 8)}", f"anim = {G_BRASA}",
                     "postype = p1", "pos = 46, -78", "scale = .35, .35", "removetime = -2", "sprpriority = 4",
                     "ownpal = 1"))
        s.append(ctl(n, "Bufada de Fogo", "Projectile", f"trigger1 = Time = {c}", f"projid = {n}",
                     f"projanim = {G_CHAMA}", f"projhitanim = {G_BRASA}", f"projremanim = {G_BRASA}",
                     "projscale = .62, .62", "projremove = 1", "projremovetime = 120", "projpriority = 2",
                     "projsprpriority = 3", "offset = 52, -14", f"velocity = {vel}, 0", "attr = S, SP",
                     f"damage = {dano}, 6", "animtype = Medium", "guardflag = MA", "hitflag = MAF",
                     "pausetime = 0, 14", "sparkno = -1", "guard.sparkno = S9202", "hitsound = S53,2",
                     "guardsound = F6,0", "ground.type = Low", "ground.slidetime = 12", "ground.hittime = 16",
                     "ground.velocity = -4", "air.velocity = -3, -3", "palfx.time = 14", "palfx.add = 160,30,20"))
        s.append(fim(n))
    # Investida do Touro: 4810 (a) e 4811 (b, atravessa a tela). Aguenta um golpe no caminho: o 1º golpe que pega
    # vira só dano e um piscar vermelho (HitOverride para o 4815, que volta para a investida)
    _, t = corpo(47210)
    c = contato(t)
    for n, vel, dur, dano in ((4810, 6.5, 18, 80), (4811, 9.0, 30, 90)):
        s.append(cab(n, "Investida do Touro", 4810))
        s.append(ctl(n, "Bufa e parte", "PlaySnd", "trigger1 = Time = 0", "value = F40,1"))
        s.append(ctl(n, "Guarda um golpe", "VarSet", "trigger1 = Time = 0", "var(31) = 0"))
        s.append(ctl(n, "Aguenta um golpe", "HitOverride", f"trigger1 = Time < {c + dur}", "trigger1 = var(31) = 0",
                     "attr = SCA, AA, AP", "slot = 0", "stateno = 4815", "time = 1", "forceair = 0"))
        s.append(ctl(n, "Dispara", "VelSet", f"trigger1 = Time = [{c - 4}, {c + dur}]", f"x = {vel}"))
        s.append(ctl(n, "Rastro", "AfterImage", f"trigger1 = Time = {c - 4}", f"time = {dur + 6}", "length = 6",
                     "timegap = 2", "framegap = 2", "trans = add", "paladd = 90,10,10", "palmul = .6,.4,.4"))
        s.append(ctl(n, "Segura o chifre na frente", "ChangeAnim", f"trigger1 = Time = [{c + 6}, {c + dur - 1}]",
                     "trigger1 = AnimElemTime(1) >= 0", "value = 4810",
                     f"elem = {next(i for i, e in enumerate(t['elementos'], 1) if e.get('caixa'))}"))
        s.append(hitdef(n, f"trigger1 = Time = {c}", f"{dano}, 8", "ground.type = High", "ground.slidetime = 14",
                        "ground.hittime = 18", "ground.velocity = -6, -4", "air.velocity = -5, -5", "fall = 1",
                        "air.fall = 1", "fall.recover = 0", attr="S, SA"))
        s.append(ctl(n, "Freia", "VelMul", f"trigger1 = Time > {c + dur}", "x = .75"))
        s.append(ctl(n, "Fim", "ChangeState", f"trigger1 = Time >= {c + dur + total(t) - c}", "trigger2 = AnimTime = 0",
                     "value = 0", "ctrl = 1"))
    s.append(f"; Investida do Touro: aguentou o golpe {MARCA}\n[Statedef 4815]\ntype = S\nmovetype = A\nphysics = S\n"
             "ctrl = 0\nvelset = 0,0\n\n")
    s.append(ctl(4815, "Já aguentou", "VarSet", "trigger1 = Time = 0", "var(31) = 1"))
    s.append(ctl(4815, "Sente o golpe", "LifeAdd", "trigger1 = Time = 0", "value = -(GetHitVar(damage))", "kill = 1"))
    s.append(ctl(4815, "Pisca vermelho", "PalFX", "trigger1 = Time = 0", "time = 10", "add = 180,20,20"))
    s.append(ctl(4815, "Segue", "ChangeState", "trigger1 = Time >= 2", "value = 4816"))
    s.append(f"[Statedef 4816]\ntype = S\nmovetype = A\nphysics = S\nctrl = 0\nanim = 4810\nvelset = 7,0\n\n")
    s.append(hitdef(4816, "trigger1 = Time = 1", "80, 8", "ground.type = High", "ground.slidetime = 14",
                    "ground.hittime = 18", "ground.velocity = -6, -4", "air.velocity = -5, -5", "fall = 1",
                    "air.fall = 1", "fall.recover = 0"))
    s.append(ctl(4816, "Freia", "VelMul", "trigger1 = Time > 10", "x = .75"))
    s.append(ctl(4816, "Fim", "ChangeState", "trigger1 = Time >= 24", "value = 0", "ctrl = 1"))
    # Pisão Racha-Chão: 4820 (a, rachadura curta e lenta) e 4821 (b, longa): golpe baixo, não pega no ar
    _, t = corpo(47220)
    c = contato(t)
    for n, vel, vida in ((4820, 4.5, 60), (4821, 6.5, 90)):
        s.append(cab(n, "Pisão Racha-Chão", 4820))
        s.append(ctl(n, "Pisa", "PlaySnd", f"trigger1 = Time = {c}", "value = S53,2"))
        s.append(ctl(n, "Chão treme", "EnvShake", f"trigger1 = Time = {c}", "time = 18", "freq = 70", "ampl = -6"))
        s.append(ctl(n, "Estouro no casco", "Explod", f"trigger1 = Time = {c}", f"anim = {G_BRASA}", "postype = p1",
                     "pos = 40, 0", "scale = .7, .7", "removetime = -2", "sprpriority = 4", "ownpal = 1"))
        s.append(ctl(n, "Pisão Racha-Chão", "Projectile", f"trigger1 = Time = {c + 2}", f"projid = {n}",
                     f"projanim = {G_RACHA}", f"projhitanim = {G_BRASA}", f"projremanim = {G_BRASA}",
                     "projscale = .5, .5", "projremove = 1", f"projremovetime = {vida}", "projpriority = 1",
                     "projsprpriority = -1", "offset = 56, 0", f"velocity = {vel}, 0", "attr = S, SP",
                     "damage = 58, 6", "animtype = Medium", "guardflag = L", "hitflag = M-", "pausetime = 0, 14",
                     "sparkno = -1", "guard.sparkno = S9202", "hitsound = S53,2", "guardsound = F6,0",
                     "ground.type = Trip", "ground.slidetime = 10", "ground.hittime = 16",
                     "ground.velocity = -2, -3", "fall = 1", "fall.recover = 0", "palfx.time = 14",
                     "palfx.add = 160,30,20"))
        s.append(fim(n))
    # Chifrada Ascendente: 4830 (x) e 4831 (y, sobe mais). Invencível até o contato
    _, t = corpo(47230)
    c = contato(t)
    for n, vy, dano in ((4830, -6.5, 70), (4831, -8.5, 82)):
        s.append(cab(n, "Chifrada Ascendente", 4830))
        s.append(ctl(n, "Invencível no começo", "NotHitBy", f"trigger1 = Time < {c + 2}", "value = SCA", "time = 1"))
        s.append(ctl(n, "Sobe", "VelSet", f"trigger1 = Time = {c - 1}", "x = 1.6", f"y = {vy}"))
        s.append(ctl(n, "No ar", "StateTypeSet", f"trigger1 = Time = {c - 1}", "statetype = A", "physics = N"))
        s.append(ctl(n, "Gravidade", "VelAdd", f"trigger1 = Time >= {c}", "y = .45"))
        s.append(ctl(n, "Rastro", "AfterImage", f"trigger1 = Time = {c - 1}", "time = 16", "length = 5",
                     "timegap = 2", "framegap = 2", "trans = add", "paladd = 90,10,10", "palmul = .6,.4,.4"))
        s.append(hitdef(n, f"trigger1 = Time = {c}", f"{dano}, 8", "ground.type = High", "ground.hittime = 18",
                        "ground.velocity = -2, -8", "air.velocity = -2, -8", "fall = 1", "air.fall = 1",
                        "fall.recover = 0", attr="S, SA", hit="MAF"))
        s.append(ctl(n, "Segura no alto", "ChangeAnim", f"trigger1 = Time > {c} && AnimTime = 0 && Pos Y < -2",
                     "value = 4830", f"elem = {len(t['elementos'])}"))
        s.append(ctl(n, "Pousa", "ChangeState", f"trigger1 = Time > {c} && Vel Y > 0 && Pos Y >= 0", "value = 52"))
    # Fúria do Minotauro (super, 1 barra): investida que pega nos chifres (o oponente fica preso no 820 do agarrão),
    # carrega até a parede, joga no alto e desce os cascos nele no chão; o chão racha com brasa
    _, ti = corpo(47210)
    ci = contato(ti)
    s.append(cab(4900, "Fúria do Minotauro", 4900, juggle=0).replace("poweradd = 40", "poweradd = -1000"))
    s.append(ctl(4900, "Para tudo", "SuperPause", "trigger1 = Time = 0", "time = 30", "movetime = 30",
                 "anim = -1", "darken = 1", "poweradd = 0", "sound = F40,1"))
    s.append(ctl(4900, "Fundo vermelho", "BGPalFX", "trigger1 = Time = 0", "time = 60", "mul = 150,90,90"))
    s.append(ctl(4900, "Dispara", "VelSet", f"trigger1 = Time = [{ci - 4}, {ci + 30}]", "x = 9"))
    s.append(ctl(4900, "Rastro", "AfterImage", f"trigger1 = Time = {ci - 4}", "time = 40", "length = 8",
                 "timegap = 2", "framegap = 2", "trans = add", "paladd = 120,10,10", "palmul = .6,.4,.4"))
    s.append(ctl(4900, "Segura o chifre na frente", "ChangeAnim", f"trigger1 = Time = [{ci + 6}, {ci + 30}]",
                 "trigger1 = AnimElemTime(1) >= 0", "value = 4900",
                 f"elem = {next(i for i, e in enumerate(ti['elementos'], 1) if e.get('caixa'))}"))
    s.append(hitdef(4900, f"trigger1 = Time = [{ci}, {ci + 30}]", "40, 0", "p1stateno = 4901", "p2stateno = 820",
                    "p2getp1state = 1", "ground.type = High", "ground.hittime = 30", attr="S, HA",
                    pausa="8, 8"))
    s.append(ctl(4900, "Errou: freia", "VelMul", f"trigger1 = Time > {ci + 30}", "x = .7"))
    s.append(ctl(4900, "Errou: fim", "ChangeState", f"trigger1 = Time > {ci + 50}", "value = 0", "ctrl = 1"))
    s.append(f"; Fúria do Minotauro: carrega nos chifres até a parede {MARCA}\n[Statedef 4901]\ntype = S\n"
             "movetype = A\nphysics = N\nctrl = 0\nanim = 4900\nvelset = 0,0\n\n")
    s.append(ctl(4901, "Chifre na frente", "ChangeAnim", "trigger1 = Time = 0", "value = 4900",
                 f"elem = {next(i for i, e in enumerate(ti['elementos'], 1) if e.get('caixa'))}"))
    s.append(ctl(4901, "Corre com ele", "VelSet", "trigger1 = 1", "x = 8"))
    s.append(ctl(4901, "Nos chifres", "TargetBind", "trigger1 = 1", "pos = 46, -46"))
    s.append(ctl(4901, "Trote", "EnvShake", "trigger1 = Time % 8 = 0", "time = 4", "freq = 120", "ampl = -2"))
    s.append(ctl(4901, "Bate na parede", "ChangeState", "trigger1 = FrontEdgeBodyDist < 26", "trigger2 = Time >= 46",
                 "value = 4902"))
    s.append(f"; Fúria do Minotauro: bate na parede e joga no alto {MARCA}\n[Statedef 4902]\ntype = S\n"
             "movetype = A\nphysics = S\nctrl = 0\nanim = 4903\nvelset = 0,0\n\n")
    s.append(ctl(4902, "Na parede", "TargetBind", "trigger1 = Time < 10", "pos = 46, -46"))
    s.append(ctl(4902, "Parede: estouro", "Explod", "trigger1 = Time = 0", f"anim = {G_BRASA}", "postype = p1",
                 "pos = 60, -50", "scale = 1.4, 1.4", "removetime = -2", "sprpriority = 5", "ownpal = 1"))
    s.append(ctl(4902, "Parede: congela", "Pause", "trigger1 = Time = 0", "time = 10", "movetime = 0"))
    s.append(ctl(4902, "Parede: tremida", "EnvShake", "trigger1 = Time = 0", "time = 24", "freq = 80", "ampl = -9"))
    s.append(ctl(4902, "Parede: dano", "TargetLifeAdd", "trigger1 = Time = 1", "value = -90", "kill = 1"))
    s.append(ctl(4902, "Parede: som", "PlaySnd", "trigger1 = Time = 0", "value = S53,2"))
    s.append(ctl(4902, "Joga no alto", "TargetState", "trigger1 = Time = 12", "value = 4951"))
    s.append(ctl(4902, "Vai pisar", "ChangeState", "trigger1 = Time >= 14", "value = 4903"))
    _, tp = corpo(47220)
    cp = contato(tp)
    s.append(f"; Fúria do Minotauro: desce os cascos {MARCA}\n[Statedef 4903]\ntype = S\nmovetype = A\nphysics = S\n"
             "ctrl = 0\nanim = 4902\nvelset = 0,0\n\n")
    s.append(ctl(4903, "Segura o pisão no alto", "ChangeAnim", f"trigger1 = Time = 0", "value = 4902"))
    s.append(ctl(4903, "Anda até ele", "VelSet", "trigger1 = Time < 18", "x = ifelse(P2BodyDist X > 30, 3, 0)"))
    s.append(ctl(4903, "Cascos", "TargetState", f"trigger1 = Time = {cp + 22}", "value = 4952"))
    s.append(ctl(4903, "Cascos: dano", "TargetLifeAdd", f"trigger1 = Time = {cp + 22}", "value = -150", "kill = 1"))
    for k, (dx, esc) in enumerate(((50, 1.1), (110, .9), (-20, .8))):
        s.append(ctl(4903, f"Chão racha {k + 1}", "Explod", f"trigger1 = Time = {cp + 22 + 3 * k}",
                     f"anim = {G_RACHA if k else G_BRASA}", "postype = p1", f"pos = {dx}, 0", f"scale = {esc}, {esc}",
                     "removetime = 50", "sprpriority = -1", "ownpal = 1"))
    s.append(ctl(4903, "Cascos: congela", "Pause", f"trigger1 = Time = {cp + 22}", "time = 14", "movetime = 0"))
    s.append(ctl(4903, "Cascos: tremida", "EnvShake", f"trigger1 = Time = {cp + 22}", "time = 34", "freq = 70",
                 "ampl = -12"))
    s.append(ctl(4903, "Cascos: clarão", "BGPalFX", f"trigger1 = Time = {cp + 22}", "time = 8", "add = 140,40,40"))
    s.append(ctl(4903, "Cascos: som", "PlaySnd", f"trigger1 = Time = {cp + 22}", "value = S53,2"))
    s.append(ctl(4903, "Fim", "ChangeState", f"trigger1 = Time >= {cp + 22 + 30}", "value = 0", "ctrl = 1"))
    # o oponente: jogado no alto (4951), cai e fica deitado; os cascos (4952) o fazem quicar e ele volta ao comum
    s.append(f"; Fúria do Minotauro: o oponente no alto {MARCA}\n[Statedef 4951]\ntype = A\nmovetype = H\n"
             "physics = N\nvelset = -1.2, -9\nctrl = 0\n\n")
    s.append(ctl(4951, "Pose", "ChangeAnim", "trigger1 = Time = 0", "value = ifelse(SelfAnimExist(5943), 5943, 5030)"))
    s.append(ctl(4951, "Gravidade", "VelAdd", "trigger1 = 1", "y = .45"))
    s.append(ctl(4951, "Caiu", "VelSet", "trigger1 = Vel Y > 0 && Pos Y >= 0", "x = 0", "y = 0"))
    s.append(ctl(4951, "No chão", "PosSet", "trigger1 = Vel Y >= 0 && Pos Y >= 0", "y = 0"))
    s.append(ctl(4951, "Deitado", "ChangeAnim", "trigger1 = Pos Y >= 0 && Vel Y = 0 && Anim != 5110",
                 "trigger1 = SelfAnimExist(5110)", "value = 5110"))
    s.append(ctl(4951, "Ninguém pisou", "SelfState", "trigger1 = Time > 90", "value = 5100"))
    s.append(f"; Fúria do Minotauro: os cascos {MARCA}\n[Statedef 4952]\ntype = A\nmovetype = H\nphysics = N\n"
             "velset = -1.5, -3.5\nctrl = 0\n\n")
    s.append(ctl(4952, "Pose", "ChangeAnim", "trigger1 = Time = 0", "value = ifelse(SelfAnimExist(5030), 5030, 5000)"))
    s.append(ctl(4952, "Gravidade", "VelAdd", "trigger1 = 1", "y = .45"))
    s.append(ctl(4952, "Chão", "SelfState", "trigger1 = Vel Y > 0 && Pos Y >= 0", "value = 5100"))
    return "".join(s)


NUMEROS = (4800, 4801, 4810, 4811, 4815, 4816, 4820, 4821, 4830, 4831, 4900, 4901, 4902, 4903, 4951, 4952)


def ligar_cns(cns):
    cns = re.sub(rf"^; [^\n]*{re.escape(MARCA)}\n\[Statedef (\d+)\]\n.*?(?=^; [^\n]*\n\[Statedef|^\[Statedef|^; ---- |^; >>> |\Z)",
                 "", cns, flags=re.M | re.S)
    for n in NUMEROS:
        cns = re.sub(rf"^\[Statedef {n}\]\n.*?(?=^\[Statedef|^; ---- |^; >>> |^; <<< |\Z)", "", cns, flags=re.M | re.S)
    i = cns.index(mk.MARCA)
    return cns[:i].rstrip() + "\n\n" + estados().rstrip() + "\n\n" + cns[i:]


# -------------------------------------------------------------------------------------------------------------- .cmd
COMANDOS = [("bufada_x", "~D, F, x"), ("bufada_y", "~D, F, y"), ("investida_a", "~D, F, a"),
            ("investida_b", "~D, F, b"), ("pisao_a", "~D, D, a"), ("pisao_b", "~D, D, b"),
            ("chifrada_x", "~F, D, F, x"), ("chifrada_y", "~F, D, F, y"), ("furia_a", "~B, F, D, a"),
            ("furia_b", "~B, F, D, b")]
ENTRADAS = [("Fúria do Minotauro", 4900, "furia_a", "furia_b", "power >= 1000"),
            ("Chifrada Ascendente", 4830, "chifrada_x", None, None), ("Chifrada Ascendente", 4831, "chifrada_y", None, None),
            ("Bufada de Fogo", 4800, "bufada_x", None, "NumProjID(4800) + NumProjID(4801) = 0"),
            ("Bufada de Fogo", 4801, "bufada_y", None, "NumProjID(4800) + NumProjID(4801) = 0"),
            ("Investida do Touro", 4810, "investida_a", None, None), ("Investida do Touro", 4811, "investida_b", None, None),
            ("Pisão Racha-Chão", 4820, "pisao_a", None, "NumProjID(4820) + NumProjID(4821) = 0"),
            ("Pisão Racha-Chão", 4821, "pisao_b", None, "NumProjID(4820) + NumProjID(4821) = 0")]


def ligar_cmd(cmd):
    nl = "\r\n" if "\r\n" in cmd else "\n"
    cmd = re.sub(rf"\[State -1, [^\]]*{re.escape(MARCA)}\]\r?\n.*?\r?\n\r?\n", "", cmd, flags=re.S)
    cmd = re.sub(r'\[Command\]\r?\nname = "(?:' + "|".join(n for n, _ in COMANDOS) + r')"\r?\n.*?\r?\n\r?\n', "", cmd,
                 flags=re.S)
    i = cmd.index("[Command]")
    cmd = cmd[:i] + "".join(f'[Command]{nl}name = "{n}"{nl}command = {c}{nl}time = {30 if n.startswith("furia") else 20}{nl}{nl}'
                            for n, c in COMANDOS) + cmd[i:]
    ent = []
    for nome, n, c1, c2, extra in ENTRADAS:
        linhas = [f"[State -1, {nome} {MARCA}]", "type = ChangeState", f"value = {n}",
                  f'triggerall = command = "{c1}"' + (f' || command = "{c2}"' if c2 else ""),
                  "triggerall = var(20) > 0", "triggerall = statetype != A"]
        if extra:
            linhas.append(f"triggerall = {extra}")
        linhas += ["trigger1 = ctrl", "trigger2 = var(1)"]
        ent.append(nl.join(linhas) + nl + nl)
    # logo depois do poder da #47 (o primeiro do [Statedef -1]): antes de toda entrada da base
    m = re.search(r"\[State -1, Poder de longe do despertado[^\]]*\].*?(?:\r?\n){2}", cmd, re.S)
    j = m.end() if m else re.search(r"^\[Statedef -1\][^\n]*\n", cmd, re.M).end()
    return cmd[:j] + "".join(ent) + cmd[j:]


def ligar_movelist(texto):
    texto = re.sub(r"^.*\(golpes-novos\).*\n", "", texto, flags=re.M)
    linhas = ("Bufada de Fogo <#bebebe>(golpes-novos)</>\t\t_D_F^X/^Y\n"
              "Investida do Touro <#bebebe>(golpes-novos)</>\t\t_D_F^A/^B\n"
              "Pisão Racha-Chão <#bebebe>(golpes-novos)</>\t\t_D_D^A/^B\n"
              "Chifrada Ascendente <#bebebe>(golpes-novos)</>\t\t_F_D_F^X/^Y\n"
              "Fúria do Minotauro <#bebebe>(super, golpes-novos)</>\t\t_B_F_D^A/^B\n")
    chave = ":Exclusivos do Despertar:</>\n"
    if chave in texto:
        return texto.replace(chave, chave + linhas, 1)
    return texto.rstrip("\n") + "\n" + linhas


def main():
    air = (PASTA / "gutto.air").read_text(encoding="utf-8")
    cns = (PASTA / "gutto.cns").read_text(encoding="utf-8")
    cmd = (PASTA / "gutto.cmd").read_bytes().decode("utf-8")
    gravar_sff()
    (PASTA / "gutto.air").write_text(air_novo(air), encoding="utf-8", newline="\n")
    (PASTA / "gutto.cns").write_text(ligar_cns(cns), encoding="utf-8", newline="\n")
    (PASTA / "gutto.cmd").write_bytes(ligar_cmd(cmd).encode("utf-8"))
    mv = PASTA / "movelist.dat"
    if mv.exists():
        mv.write_text(ligar_movelist(mv.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    print("Garanhão: Bufada de Fogo, Investida do Touro, Pisão Racha-Chão, Chifrada Ascendente e Fúria do Minotauro "
          "ligados")


if __name__ == "__main__":
    main()
