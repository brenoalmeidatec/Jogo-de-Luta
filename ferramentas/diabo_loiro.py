#!/usr/bin/env python3
"""Pós-passo do Hazak (issue #44 do Breno, 2026-11-14): golpes de longe novos e o Diabo Loiro.

  python ferramentas/diabo_loiro.py        reaplica em chars/hazaki (o gerar_hazaki.py já chama no fim)

Como o efeitos.py e o parry.py, trabalha em cima do que o gerador gravou em chars/hazaki (sff, air, cns): os efeitos
entram no .sff como PNG de 32 bits (fora da paleta do corpo) e as ações do .air são escritas aqui.

Golpes de longe (os estados estão no gerar_hazaki.py, cns_especiais; os efeitos, no hazak_poderes_blender.py):
  Pedra       7401 a pedra subindo do chão (Explod), 1005 a pedra em voo (projétil), 7402 a pedra quebrando
  Bola de ki  7410 o ki juntando nas mãos (Explod), 1605 a bola vermelha (projétil), 7411 a bola estourando
Diabo Loiro (o Despertar do Hazak, que até aqui não existia no jogo):
  arte        cada desenho 3x do corpo ganha o gêmeo do Diabo no terno do conceito (diabo_terno.py) no grupo + 20000, e o
              [RemapPreset despertado] troca um pelo outro enquanto o var(20) corre (como no Pengaró e no Gutto)
  cena        estado 2000 (x + y com a barra cheia): bate o pé, olha para trás e pergunta "Ô vida, posso despertar?";
              a patroa (7450-7452) entra, faz que sim e sai; no último desenho ele vira o Diabo num estouro de ouro
  aura        as asas de ouro derretido, a coroa, a brasa no chão e as notas queimando (sprites/hazaki/aura, já
              aprovadas), ligadas pelo ferramentas/aura.py (Explods 9600-9601, [Statedef -4])
  rajadona    Rajadona de Ki das Trevas (1650): com o Diabo e 1 estoque, → ← x/y vira o raio enorme e contínuo, preto,
              vermelho e ouro (7420 o raio, 7421 o raio se desfazendo), 12 acertos
  cobrança    Cobrança do Diabo (1660/1661, #44, no lugar do Chapéu Bumerangue): com o Diabo, ↓ → a/b (no lugar do Giro
              de Garagem) abre o sobretudo, desliza num rastro de brasa atravessando projétil e bate com o ombro; se
              acerta, cobra a dívida: tira 150 de barra do oponente e põe na dele. Desenho próprio d_cobranca (8 quadros)
  agarrão     o Abraço de Quebrada (810) do Diabo pega fogo: cada pancada solta chama laranja-ouro no oponente e o fim
              explode em ouro, com mais dano
Grupos e ações 7400-7499: fora dos do efeitos.py (8200-8291, 9200-9272) e do parry (7690/7691, 8290/8291).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conferir_sff as cs  # noqa: E402
import diabo_terno  # noqa: E402
import efeitos  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "chars/hazaki"
BLENDER = RAIZ / "sprites/efeitos_blender/hazaki"
E = efeitos.ESCALA_BLENDER  # escala no .air dos efeitos do Blender (o mesmo pixel dos do efeitos.py)
HD = 3                      # caixas do .air do Hazak: em 3x (hd.py), o motor divide pela escala do dono


def render(nome):
    """[(RGBA, eixo x, eixo y)] e ticks do efeito do Blender, cada desenho cortado no que tem pixel."""
    pasta = BLENDER / nome
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    quadros = []
    for arq in sorted(pasta.glob("[0-9][0-9].png")):
        img = Image.open(arq).convert("RGBA")
        cx = img.getchannel("A").getbbox() or (0, 0, 1, 1)
        quadros.append((img.crop(cx), meta["pivo"][0] - cx[0], meta["pivo"][1] - cx[1]))
    return quadros, meta["ticks"]


def caixa(nome, x0, y0, x1, y1):
    return f"{nome}Default: 1\n{nome}[0] = {x0 * HD}, {y0 * HD}, {x1 * HD}, {y1 * HD}"


# ação -> (efeito do Blender, grupo dos sprites, ticks por desenho ou None (o do render), laço a partir do desenho,
#          caixa de golpe (Clsn1) e de projétil (Clsn2) em px do jogo)
ACOES = {
    7401: ("pedra", 7401, 2, 0, None),
    1005: ("pedra", 7405, 2, 0, (-18, -18, 18, 18)),
    7402: ("pedra_quebra", 7402, None, None, None),
    7410: ("ki_carga", 7410, None, 6, None),
    1605: ("ki_bola", 7406, None, 0, (-26, -19, 10, 19)),
    7411: ("ki_estouro", 7411, None, None, None),
}
DIABO = 20000       # grupo do desenho do Diabo = grupo do Hazak + DIABO
LIGA = 122          # tick da cena (estado 2000) em que ele vira o Diabo: início do último desenho (gerar_hazaki)
TEMPO = 600         # ticks de Diabo Loiro (10 s), como os outros despertados
RAJADA = {"sai": 28, "dura": 66, "acertos": 12, "dano": 16, "x": 52, "y": -80, "comp": 286}
# Cobrança do Diabo: ticks por desenho; desenhos com caixa de golpe; a (curta) e b (longa)
COBRANCA = {"pasta": "d_cobranca", "grupo": 21660, "ticks": [4, 6, 3, 3, 3, 6, 8, 10], "ativos": (3, 4, 5),
            "sai": 10, 1660: {"vel": 6.5, "dura": 12, "dano": 60, "cai": False},
            1661: {"vel": 8.5, "dura": 14, "dano": 80, "cai": True}, "barra": 150}
PATROA = RAIZ / "sprites/hazaki/quadros_arcade_hd"
EIXO_HD = (540, 660)  # pé do lutador nos desenhos 3x (o EIXO 180, 220 do gerar_pengaro vezes 3)


def texto_acao(grupo, quadros, ticks, laco, clsn):
    linhas = []
    if clsn:
        linhas.append(caixa("Clsn2", *clsn))
        linhas.append(caixa("Clsn1", *clsn))
    for i in range(len(quadros)):
        if laco is not None and i == laco:
            linhas.append("LoopStart")
        linhas.append(f"{grupo},{i}, 0,0, {ticks}, , , {E:g}, {E:g}")
    return "\n".join(linhas)


def sprites_do_diabo(nos):
    """[(grupo, índice, RGBA, eixo x, eixo y)] do Diabo, um para cada desenho do corpo (índices 1 a 15 da paleta):
    o quadro de mesmo número da folha do terno do conceito (ferramentas/diabo_terno.py), alinhado pelo apoio."""
    nitida = RAIZ / "sprites/hazaki/paleta_nitida.json"  # Hazak nítido (#36): o corpo usa mais que as 15 cores
    n_corpo = len(json.loads(nitida.read_text(encoding="utf-8"))["cores"]) if nitida.exists() else 15
    terno = diabo_terno.Terno()
    saida, vistos, fora = [], set(), []
    for n in nos:
        k = (n["g"], n["i"])
        if k in vistos or n.get("png") or n["g"] == 9000 or n["g"] >= DIABO:
            continue
        vistos.add(k)
        ind = np.frombuffer(n["px"], np.uint8).reshape(n["h"], n["w"])
        if ind.max() > n_corpo or not ind.any():
            continue
        par = terno.diabo(ind > 0, (n["x"], n["y"]))
        if par is None:
            fora.append(k)  # objeto ou efeito na paleta do corpo (não é ele): fica como está
            continue
        img, (ex, ey) = par
        saida.append((n["g"] + DIABO, n["i"], img, ex, ey))
    if fora:
        print(f"hazaki: {len(fora)} sprites da paleta do corpo sem quadro do corpo (ficam sem gêmeo do Diabo): {fora}")
    return saida


def patroa():
    """{ação: [(RGBA, eixo x, eixo y, ticks)]}: a patroa chegando (anda), parada fazendo que sim e saindo."""
    def q(folha, i):
        img = Image.open(PATROA / folha / f"{i:02d}.png").convert("RGBA")
        cx = img.getchannel("A").getbbox()
        return img.crop(cx), EIXO_HD[0] - cx[0], EIXO_HD[1] - cx[1]
    return {7450: [(*q("patroa_chega_sim", i), 7) for i in (0, 1)],
            7451: [(*q("patroa_chega_sim", i), t) for i, t in ((2, 6), (3, 8), (4, 8), (5, 10), (6, 12), (7, 14))],
            7452: [(*q("patroa_sai", i), 6) for i in range(1, 8)]}


RAIZ_ASAS = (181, 100)  # onde as duas asas se encontram, em px da tela da aura (sprites/hazaki/aura, 360 x 200)


def montar_aura():
    import aura
    pasta = RAIZ / "sprites/hazaki/aura"
    info = json.loads((pasta / "aura.json").read_text(encoding="utf-8"))
    assert info["tela"] == [360, 200] and info["tiques_por_quadro"] == 2, info

    def ler(nome):
        n = next(c["quadros"] for c in info["camadas"] if c["nome"] == nome)
        return [np.asarray(Image.open(pasta / info["arquivo"].format(nome=nome, quadro=k)).convert("RGBA"))
                for k in range(n)]

    def sobre(*camadas):
        n = max(len(c) for c in camadas)
        out = []
        for k in range(n):
            img = Image.fromarray(camadas[0][k % len(camadas[0])], "RGBA")
            for c in camadas[1:]:
                img.alpha_composite(Image.fromarray(c[k % len(c)], "RGBA"))
            out.append(np.asarray(img))
        return out
    pe = tuple(info["pe"])
    resta = f"ifelse(StateNo = 2000, ifelse(Time >= {LIGA}, 999, 0), var(20))"
    camadas = [
        # asas e coroa voam junto com ele; a brasa e as notas ficam no chão (no pulo não sobem)
        aura.Camada("asas", sobre(ler("asas"), ler("coroa")), plano="tras", eixo=pe, tique=1, prioridade=-6,
                    cresce=False, mov=aura.Movimento(deriva=(0.6, 1.5), deriva_periodo=120, alfa=0.95, respira=0.06)),
        aura.Camada("chao", sobre(ler("chao"), ler("particulas")), plano="tras", no_chao=True, eixo=pe, tique=0,
                    prioridade=-5, cresce=False,
                    mov=aura.Movimento(deriva=(1.0, 0), deriva_periodo=130, alfa=0.92, respira=0.06)),
    ]
    # issue #51: caído, a asa fecha colada nas costas. Dois desenhos a mais (meio e fechada), dobrados como leque em
    # volta da raiz; o ferramentas/aura_no_corpo.py troca um pelo outro pelo alfa, conforme o corpo deita e levanta.
    # Entram no fim da lista para as asas e o chão continuarem em 9600 e 9601.
    mov = aura.Movimento(deriva=(0.6, 1.5), deriva_periodo=120, alfa=0.95, respira=0.06)
    # fechada: as duas asas quase juntas apontando para baixo, uma faixa colada nas costas (vista de lado, as duas
    # dobram por cima uma da outra); com o corpo deitado ela deita ao longo dele, sem ponta para cima
    for nome, fecha, encolhe, alvo, aperta in (("asas_meio", 0.55, 0.9, -84.0, 0.75),
                                               ("asas_fechada", 0.5, 0.82, -90.0, 0.3)):
        dobradas = aura.dobrar_asas(ler("asas"), RAIZ_ASAS, fecha, encolhe, alvo, aperta)
        camadas.append(aura.Camada(nome, sobre(dobradas, ler("coroa")),
                                   plano="tras", eixo=pe, tique=1, prioridade=-6, cresce=False, mov=mov))
    surto = f"(StateNo = 1650 && Time = 1) || (StateNo = 2000 && Time = {LIGA})"
    return aura.Aura("diabo", camadas, ligada=f"({resta}) > 0", surto=surto, base=9600, entra=30, sai=34,
                     virada_fundo=0.6, resta=resta)


# ---------------------------------------------------------------- .cns
def ctl(estado, titulo, tipo, *linhas):
    return f"[State {estado}, {titulo}]\ntype = {tipo}\n" + "".join(f"{x}\n" for x in linhas) + "\n"


def cns_despertar():
    c = ["[Statedef 2000]\ntype = S\nmovetype = I\nphysics = S\nctrl = 0\nsprpriority = 2\nanim = 2000\n"
         "velset = 0,0\n\n"]
    fim = LIGA + 40
    c.append(ctl(2000, "Pausa", "Pause", "trigger1 = Time = 0", f"time = {fim}", f"movetime = {fim}"))
    c.append(ctl(2000, "Gasta", "PowerAdd", "trigger1 = Time = 0", "value = -3000"))
    c.append(ctl(2000, "Invencivel", "NotHitBy", "trigger1 = 1", "value = SCA", "time = 1"))
    c.append(ctl(2000, "Bate o pé", "EnvShake", "trigger1 = Time = 8", "time = 6", "ampl = 2", "freq = 120"))
    # a patroa: chega andando por trás dele, para, faz que sim com a cabeça e vai embora
    comum = ("postype = p1", "sprpriority = -1", "ownpal = 1", "pausemovetime = 999", "supermovetime = 999",
             "ignorehitpause = 1")
    c.append(ctl(2000, "Patroa chega", "Explod", "trigger1 = Time = 26", "anim = 7450", "id = 7450",
                 "pos = -170, 0", "vel = 2, 0", "removetime = 30", *comum))
    c.append(ctl(2000, "Patroa faz que sim", "Explod", "trigger1 = Time = 56", "anim = 7451", "id = 7451",
                 "pos = -110, 0", "removetime = 58", *comum))
    c.append(ctl(2000, "Patroa sai", "Explod", "trigger1 = Time = 114", "anim = 7452", "id = 7452",
                 "pos = -110, 0", "vel = -2.4, 0", "removetime = 60", *comum))
    # vira o Diabo: estouro de ouro, clarão e tremida no início do último desenho
    c.append(ctl(2000, "Estouro de ouro", "Explod", f"trigger1 = Time = {LIGA}", "anim = 9271", "postype = p1",
                 "pos = 0, -60", "scale = 1.6, 1.6", "sprpriority = 3", "ownpal = 1", "pausemovetime = 999",
                 "removetime = -2", "ignorehitpause = 1"))
    c.append(ctl(2000, "Clarão", "BGPalFX", f"trigger1 = Time = {LIGA}", "time = 6", "add = 160, 90, 20",
                 "ignorehitpause = 1"))
    c.append(ctl(2000, "Tremida", "EnvShake", f"trigger1 = Time = {LIGA}", "time = 24", "ampl = 5", "freq = 90"))
    c.append(ctl(2000, "Liga", "VarSet", f"trigger1 = Time = {LIGA}", f"var(20) = {TEMPO}"))
    c.append(ctl(2000, "Fim", "ChangeState", "trigger1 = AnimTime = 0", "value = 0", "ctrl = 1"))
    return "".join(c)


def cns_rajada():
    r = RAJADA
    c = ["[Statedef 1650]\ntype = S\nmovetype = A\nphysics = S\nctrl = 0\nsprpriority = 2\nanim = 1650\n"
         "juggle = 0\nvelset = 0,0\npoweradd = 0\n\n"]
    c.append(ctl(1650, "Pausa", "SuperPause", "trigger1 = Time = 0", "time = 25", "anim = S9271", "pos = 10, -60",
                 "movetime = 0", "darken = 1"))
    c.append(ctl(1650, "Gasta", "PowerAdd", "trigger1 = Time = 0", "value = -1000"))
    # padrão do Breno para os despertados (#47): grande, sombrio e pesado
    c.append(ctl(1650, "Carga: rastro do corpo", "AfterImage", "trigger1 = Time = 0", f"time = {r['sai'] + 20}",
                 "length = 8", "timegap = 2", "framegap = 2", "trans = add", "palcolor = 0",
                 "paladd = 120, 50, 0", "palmul = .55, .55, .55"))
    c.append(ctl(1650, "Carga: treme de leve", "EnvShake", f"trigger1 = Time = {r['sai'] - 14}", "time = 14",
                 "freq = 180", "ampl = -2"))
    c.append(ctl(1650, "Solta: tremida forte", "EnvShake", f"trigger1 = Time = {r['sai']}", "time = 26",
                 "freq = 100", "ampl = -8"))
    c.append(ctl(1650, "Solta: fundo escurece em vermelho", "BGPalFX", f"trigger1 = Time = {r['sai'] + 4}",
                 f"time = {r['dura'] + 10}", "mul = 120, 55, 50"))
    c.append(ctl(1650, "Invencivel na carga", "NotHitBy", f"trigger1 = Time < {r['sai']}", "value = SCA", "time = 1"))
    for k, (x, y) in enumerate(((22, -46), (-30, -46))):
        c.append(ctl(1650, f"Carga {k + 1}", "Explod", "trigger1 = Time = 4", "anim = 7410", f"id = {7412 + k}",
                     "postype = p1", f"pos = {x}, {y}", f"removetime = {r['sai'] - 4}", "sprpriority = 4",
                     "ownpal = 1"))
    c.append(ctl(1650, "Projétil", "Projectile", f"trigger1 = Time = {r['sai']}", "projid = 1650",
                 "projanim = 7420", "projhitanim = 7421", "projremanim = 7421", "projcancelanim = 7421",
                 f"projhits = {r['acertos']}", "projmisstime = 5", f"projremovetime = {r['dura']}",
                 "projpriority = 9", f"offset = {r['x']}, {r['y']}", "velocity = 0, 0", "attr = S, HP",
                 f"damage = {r['dano']}, 4", "animtype = Med", "guardflag = MA", "hitflag = MAF",
                 "pausetime = 2, 6", "sparkno = -1", "guard.sparkno = S9216", "hitsound = F5,2",
                 "guardsound = F6,0", "ground.type = High", "ground.slidetime = 8", "ground.hittime = 12",
                 "ground.velocity = -1.2", "air.velocity = -1.5,-2", "air.juggle = 0",
                 "palfx.time = 6", "palfx.add = 140, 50, 0", "palfx.sinadd = 30, 30, 30, 4",
                 # o raio fica parado na boca: sem isto, quem está longe não entra na guarda e não consegue defender
                 f"guard.dist = {r['comp'] + 60}"))
    c.append(ctl(1650, "Chama no oponente", "Explod", "trigger1 = ProjHitTime(1650) = 0", "anim = 9270",
                 "postype = p2", "pos = -10, -60", "sprpriority = 5", "ownpal = 1", "removetime = -2",
                 "random = 30, 40"))
    c.append(ctl(1650, "Tremida", "EnvShake", f"trigger1 = Time = {r['sai'] + 26}", f"time = {r['dura'] - 26}", "ampl = 3",
                 "freq = 140"))
    c.append(ctl(1650, "Clarão", "BGPalFX", f"trigger1 = Time = {r['sai']}", "time = 4", "add = 120, 40, 0",
                 "ignorehitpause = 1"))
    c.append(ctl(1650, "Fim", "ChangeState", "trigger1 = AnimTime = 0", "value = 0", "ctrl = 1"))
    return "".join(c)


def acao_cobranca():
    """(desenhos [(RGBA, eixo x, eixo y)], texto da ação 1660) do Diabo na Cobrança, ou (None, None) sem a folha.
    Eixo nos pés (âncora do diabo_terno); caixas medidas no desenho, em px 3x como o resto do corpo."""
    pasta = diabo_terno.SAIDA / COBRANCA["pasta"]
    if not (pasta / "00.png").exists():
        return None, None
    quadros, linhas = [], []
    for i, t in enumerate(COBRANCA["ticks"]):
        img = Image.open(pasta / f"{i:02d}.png").convert("RGBA")
        m = np.array(img)[..., 3] > 0
        ax, ay = diabo_terno.ancora(m)
        ex, ey = round(ax), int(ay)
        quadros.append((img, ex, ey))
        ys, xs = np.nonzero(m)
        x0, x1, y0, y1 = xs.min() - ex, xs.max() - ex, ys.min() - ey, ys.max() - ey
        topo = y0 + round(0.18 * (y1 - y0))  # sem a copa do chapéu
        tronco = (max(x0, -75), 0, min(x1, 75), topo)
        linhas.append(f"Clsn2: 1\n Clsn2[0] = {tronco[0]}, {tronco[1]}, {tronco[2]}, {tronco[3]}")
        if i in COBRANCA["ativos"]:
            ombro = (x1 - 70, topo + round(0.10 * (y1 - y0)), x1 + 6, topo + round(0.50 * (y1 - y0)))
            linhas.append(f"Clsn1: 1\n Clsn1[0] = {ombro[0]}, {ombro[1]}, {ombro[2]}, {ombro[3]}")
        linhas.append(f"{COBRANCA['grupo']},{i}, 0,0, {t}")
    return quadros, "\n".join(linhas)


def cns_cobranca(n):
    c, k = COBRANCA, COBRANCA[n]
    sai, fim = c["sai"], c["sai"] + k["dura"]
    e = [f"[Statedef {n}]\ntype = S\nmovetype = A\nphysics = N\nctrl = 0\nsprpriority = 2\nanim = 1660\n"
         "juggle = 4\nvelset = 0,0\n\n"]
    e.append(ctl(n, "Zera", "VarSet", "trigger1 = Time = 0", "var(12) = 0"))
    e.append(ctl(n, "Rastro do corpo em brasa", "AfterImage", "trigger1 = Time = 0", f"time = {fim + 4}",
                 "length = 6", "timegap = 2", "framegap = 2", "trans = add", "palcolor = 0", "paladd = 120, 50, 0",
                 "palmul = .55, .55, .55"))
    e.append(ctl(n, "Abre o sobretudo: brasa nos pés", "Explod", "trigger1 = Time = 2", "anim = 9270",
                 "postype = p1", "pos = 0, 0", "scale = .8, .8", "sprpriority = 3", "ownpal = 1", "removetime = -2"))
    e.append(ctl(n, "Som do arranque", "PlaySnd", f"trigger1 = Time = {sai}", "value = F40,4"))
    e.append(ctl(n, "Desliza", "VelSet", f"trigger1 = Time = {sai}", f"x = {k['vel']}"))
    e.append(ctl(n, "Para", "VelSet", f"trigger1 = Time = {fim}", "trigger2 = MoveContact = 1", "x = 0"))
    e.append(ctl(n, "Rastro de brasa no chão", "Explod", f"trigger1 = Time >= {sai} && Time < {fim}",
                 f"trigger1 = (Time - {sai}) % 3 = 0", "anim = 9270", "postype = p1", "pos = -18, 0",
                 "bindtime = 1", "scale = .55, .55", "sprpriority = 1", "ownpal = 1", "removetime = -2"))
    e.append(ctl(n, "Atravessa projétil", "NotHitBy", f"trigger1 = Time >= {sai - 2} && Time < {fim}",
                 "value = SCA, NP, SP, HP", "time = 1"))
    queda = ["fall = 1", "fall.recover = 0", "ground.velocity = -6, -3.5", "air.velocity = -6, -3.5"] if k["cai"] \
        else ["ground.velocity = -6", "air.velocity = -5, -3"]
    e.append(ctl(n, "Ombrada", "HitDef", f"trigger1 = Time = {sai}", "attr = S, SA", f"damage = {k['dano']}, 8",
                 "animtype = Heavy", "guardflag = MA", "hitflag = MAF", "priority = 5, Hit", "pausetime = 14, 14",
                 "guard.pausetime = 10, 10", "sparkxy = -6, -40", "sparkno = S9240", "guard.sparkno = S9216",
                 "sparkscale = 1.2, 1.2", "hitsound = S52,2", "guardsound = F6,0", "ground.type = High",
                 "ground.slidetime = 10", "ground.hittime = 20", "envshake.time = 10", "envshake.freq = 120",
                 "envshake.ampl = -5", "palfx.time = 8", "palfx.add = 140, 50, 0", *queda))
    e.append(ctl(n, "Cobra a dívida: tira barra", "TargetPowerAdd", "trigger1 = MoveHit = 1",
                 f"value = -{c['barra']}"))
    e.append(ctl(n, "Cobra a dívida: põe na dele", "PowerAdd", "trigger1 = MoveHit = 1", f"value = {c['barra']}"))
    # o estouro acompanha o P2 no começo do voo e é menor que o da Rajadona (conferência do vídeo: parecia preso)
    e.append(ctl(n, "Estouro de ouro", "Explod", "trigger1 = MoveHit = 1", "anim = 9271", "postype = p2",
                 "pos = 0, -50", "bindtime = 14", "scale = .75, .75", "sprpriority = 6", "ownpal = 1",
                 "removetime = -2", "ignorehitpause = 1"))
    e.append(ctl(n, "Fundo escurece", "BGPalFX", "trigger1 = MoveHit = 1", "time = 24", "mul = 120, 55, 50",
                 "ignorehitpause = 1"))
    e.append(ctl(n, "Defendido", "VarSet", "trigger1 = MoveGuarded = 1", "var(12) = 1"))
    e.append(ctl(n, "Freia", "VelMul", f"trigger1 = Time > {fim}", "x = .8"))
    e.append(ctl(n, "Fim", "ChangeState", "trigger1 = AnimTime = 0", "value = 0", "ctrl = 1"))
    return "".join(e)


MENOS_2 = """[State -2, Conta Diabo Loiro]
type = VarAdd
trigger1 = var(20) > 0
var(20) = -1

[State -2, Vira o Diabo]
type = RemapSprite
trigger1 = var(20) > 0 && var(37) = 0
preset = "despertado"

[State -2, Diabo ligado]
type = VarSet
trigger1 = var(20) > 0
var(37) = 1

[State -2, Volta ao normal]
type = RemapSprite
trigger1 = var(20) <= 0 && var(37) = 1
trigger2 = roundstate < 2
reset = 1

[State -2, Diabo desligado]
type = VarSet
trigger1 = var(20) <= 0
var(37) = 0

[State -2, Peso do Diabo]
type = AttackMulSet
trigger1 = 1
value = ifelse(var(20) > 0, 1.25, 1)

"""


# Fogo do agarrão do Diabo (#45, 2026-11-15): o Breno pediu que no Diabo Loiro o agarrão vire um poder que queima
# o inimigo: ele segura, o fogo das trevas (vermelho e ouro) toma conta, o oponente fica queimando nas mãos dele até
# o final explodir em fogo, no padrão grande e pesado da #47. Desenhos do ferramentas/despertados_47_blender.py hazaki.
FOGO = {"agarrao": 7470, "final": 7471, "pancada": 7472}   # ação = grupo dos sprites


def acoes_do_fogo():
    """{ação: (quadros, texto da ação)} dos três efeitos do fogo do agarrão (sprites/efeitos_blender/hazaki/d47_*)."""
    out = {}
    for ef, g in FOGO.items():
        pasta = BLENDER / f"d47_{ef}"
        if not pasta.exists():
            continue
        quadros, ticks = render(f"d47_{ef}")
        laco = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))["laco"]
        out[g] = (quadros, texto_acao(g, quadros, ticks, laco if laco >= 0 else None, None))
    return out


def agarrao_do_diabo(cns, fogo=True):
    """No Diabo os três agarrões (810, 841, 831) queimam o oponente: o fogo das trevas toma conta dele na primeira
    pancada e fica até o final, ele pisca vermelho e ouro, cada pancada estoura em fogo e o final explode."""
    for n in (810, 841, 831):
        m = re.search(rf"^\[Statedef {n}\][^\n]*\n.*?(?=^\[Statedef )", cns, re.M | re.S)
        if not m:
            assert n != 810, "sem o estado 810 (agarrão em pé)"
            continue
        bloco = m.group(0)
        d = "trigger1 = var(20) > 0"
        tempos = [int(x) for x in re.findall(rf"\[State {n}, Pancada \d+: dano\]\ntype = TargetLifeAdd\n"
                                             r"trigger1 = Time = (\d+)", bloco)]
        fim = re.search(rf"\[State {n}, Final: dano\]\ntype = TargetLifeAdd\ntrigger1 = Time = (\d+)", bloco)
        assert fim, f"agarrão {n} sem o golpe final"
        t = int(fim.group(1))
        bind = re.search(rf"\[State {n}, Segura\]\ntype = TargetBind\n(?:[^\n]+\n)*?pos = (-?\d+)", bloco)
        x = int(bind.group(1)) if bind else 30
        acende = max(2, (tempos[0] if tempos else t) - 8)
        extra = []
        if fogo:
            extra.append(ctl(n, "Diabo: o fogo toma conta", "Explod", f"trigger1 = Time = {acende}", d,
                             "trigger1 = NumTarget", f"anim = {FOGO['agarrao']}", f"id = {FOGO['agarrao']}",
                             "postype = p1", f"pos = {x}, 0", "bindtime = -1", "removetime = -1", "sprpriority = 6",
                             "ownpal = 1", "trans = addalpha", "alpha = 170, 256", "scale = .85, .85",
                             "ignorehitpause = 1"))  # somado: o oponente aparece queimando dentro do fogo
            extra.append(ctl(n, "Diabo: o fogo apaga", "RemoveExplod", f"trigger1 = Time = {t}",
                             "trigger2 = !NumTarget", f"id = {FOGO['agarrao']}"))
            extra.append(ctl(n, "Diabo: oponente queimando", "PalFX", f"trigger1 = Time = [{acende}, {t}]", d,
                             "trigger1 = NumTarget", "redirectid = target,id", "time = 2", "add = 90, 25, 0",
                             "mul = 256, 200, 160", "sinadd = 60, 40, 0, 10"))
        for k, tk in enumerate(tempos):
            if fogo:
                extra.append(ctl(n, f"Diabo: estouro de fogo {k + 1}", "Explod", f"trigger1 = Time = {tk}", d,
                                 "trigger1 = NumTarget", f"anim = {FOGO['pancada']}", "postype = p2", "pos = 0, -60",
                                 "sprpriority = 7", "ownpal = 1", "removetime = -2", "scale = .85, .85",
                                 "ignorehitpause = 1"))
            if not fogo:  # sem o fogo novo, a chama antiga em cada pancada
                extra.append(ctl(n, f"Diabo: chama {k + 1}", "Explod", f"trigger1 = Time = {tk}", d,
                                 "trigger1 = NumTarget", "anim = 9270", "postype = p2", "pos = 0, -55",
                                 "sprpriority = 6", "ownpal = 1", "removetime = -2"))
            extra.append(ctl(n, f"Diabo: tremida {k + 1}", "EnvShake", f"trigger1 = Time = {tk}", d,
                             "trigger1 = NumTarget", "time = 8", "freq = 140", "ampl = -4"))
            extra.append(ctl(n, f"Diabo: oponente pisca {k + 1}", "PalFX", f"trigger1 = Time = {tk}", d,
                             "trigger1 = NumTarget", "redirectid = target,id", "time = 6", "add = 140, 50, 0"))
        if fogo:
            extra.append(ctl(n, "Diabo: explosão de fogo", "Explod", f"trigger1 = Time = {t}", d,
                             "trigger1 = NumTarget", f"anim = {FOGO['final']}", "postype = p2", "pos = 0, -60",
                             "sprpriority = 7", "ownpal = 1", "removetime = -2",
                             "pausemovetime = 14", "ignorehitpause = 1", "scale = .95, .95"))
        extra.append(ctl(n, "Diabo: estouro de ouro", "Explod", f"trigger1 = Time = {t}", d,
                         "trigger1 = NumTarget", "anim = 9271", "postype = p2", "pos = 0, -50", "sprpriority = 6",
                         "ownpal = 1", "removetime = -2"))
        extra.append(ctl(n, "Diabo: dano do fogo", "TargetLifeAdd", f"trigger1 = Time = {t}", d,
                         "trigger1 = NumTarget", "value = -40"))
        extra.append(ctl(n, "Diabo: tremida", "EnvShake", f"trigger1 = Time = {t}", d,
                         "time = 30", "ampl = -11", "freq = 90"))
        extra.append(ctl(n, "Diabo: fundo escuro", "BGPalFX", "trigger1 = Time = 1", d,
                         "trigger1 = NumTarget", f"time = {t + 20}", "mul = 120, 55, 50", "sinadd = 0,0,0,0"))
        extra.append(ctl(n, "Diabo: congela no impacto", "Pause", f"trigger1 = Time = {t}", d,
                         "trigger1 = NumTarget", "time = 14", "movetime = 0"))
        extra.append(ctl(n, "Diabo: clarão", "BGPalFX", f"trigger1 = Time = {t}", d,
                         "time = 8", "add = 140, 110, 60", "mul = 120, 55, 50"))
        marca = f"[State {n}, Segura]"
        assert marca in bloco
        cns = cns.replace(bloco, bloco.replace(marca, "".join(extra) + marca, 1), 1)
    return cns


def tirar_agarrao_do_diabo(cns):
    """Tira o que o agarrao_do_diabo pôs (para pôr de novo com os tempos de agora)."""
    return re.sub(r"\[State 8[134]\d, Diabo[^\]]*\]\n(?:[^\n]+\n)+\n", "", cns)


def ligar_cns(cns, diabo, aura_cns, cobranca=False):
    assert "[Statedef 2000]" not in cns, "o Hazak já tem estado 2000: rode o gerar_hazaki.py antes"
    preset = "[RemapPreset despertado]\n" + "".join(f"{g - DIABO},{i} = {g},{i}\n" for g, i, *_ in diabo) + "\n"
    assert cns.count("[Data]") == 1
    cns = cns.replace("[Data]", preset + "[Data]", 1)
    cab = "[Statedef -2]\n\n"
    assert cns.count(cab) == 1
    cns = cns.replace(cab, cab + MENOS_2, 1)
    cns = agarrao_do_diabo(cns)
    extra = cns_cobranca(1660) + cns_cobranca(1661) if cobranca else ""
    cns = cns.replace(cab, cns_despertar() + cns_rajada() + extra + cab, 1)
    return cns.rstrip() + "\n\n" + aura_cns


def ligar_cmd(cmd, cobranca=False):
    comando = '[Command]\nname = "despertar"\ncommand = x+y\ntime = 3\n\n'
    cab = "[Statedef -1]\n\n"
    assert cmd.count(cab) == 1 and 'name = "despertar"' not in cmd
    entradas = ('[State -1, Diabo Loiro (Despertar)]\ntype = ChangeState\nvalue = 2000\n'
                'triggerall = command = "despertar"\ntriggerall = power >= powermax\ntriggerall = var(20) <= 0\n'
                'triggerall = statetype != A\ntrigger1 = ctrl\n\n'
                '[State -1, Rajadona de Ki das Trevas]\ntype = ChangeState\nvalue = 1650\n'
                'triggerall = command = "fb_x" || command = "fb_y"\ntriggerall = var(20) > 0\n'
                'triggerall = power >= 1000\ntriggerall = statetype != A\ntriggerall = numproj = 0\n'
                'trigger1 = ctrl || var(1)\n\n')
    if cobranca:
        entradas += ('[State -1, Cobrança do Diabo]\ntype = ChangeState\nvalue = ifelse(command = "df_b", 1661, 1660)\n'
                     'triggerall = command = "df_a" || command = "df_b"\ntriggerall = var(20) > 0\n'
                     'triggerall = statetype != A\ntrigger1 = ctrl || var(1)\n\n')
    return cmd.replace(cab, comando + cab + entradas, 1)


def acoes_da_rajada():
    quadros, ticks = render("rajada")
    r = RAJADA
    linhas = []
    for i in range(12):
        if i == 6:
            linhas.append("LoopStart")
        comp = r["comp"] * min(1.0, (i + 1) / 6)
        linhas.append(f"Clsn1: 1\nClsn1[0] = 0, {-18 * HD}, {round(comp) * HD}, {18 * HD}")
        linhas.append(f"7420,{i}, 0,0, 3, , , {E:g}, {E:g}")
    fim = [f"7420,{i}, 0,0, 3, , , {E:g}, {E:g}" for i in range(12, len(quadros))]
    return quadros, "\n".join(linhas), "\n".join(fim)


def aplicar(pasta=SAIDA):
    pasta = Path(pasta)
    sff, arq_air, arq_cns, arq_cmd = (pasta / f"hazaki.{e}" for e in ("sff", "air", "cns", "cmd"))
    air = arq_air.read_text(encoding="utf-8")
    cns = arq_cns.read_text(encoding="utf-8")
    cmd = arq_cmd.read_text(encoding="utf-8")
    # os sprites antigos da lasca e da estatueta (o que as ações 1005 e 1605 mostravam antes): saem do .sff
    velhos = set()
    for n in (1005, 1605):
        m = re.search(rf"^\[Begin Action {n}\][^\n]*\n(.*?)(?=^\[Begin Action|\Z)", air, re.M | re.S)
        if m:
            velhos |= {int(g) for g, _ in efeitos.RE_ELEMENTO.findall(m.group(1))}
    novos = {}
    for acao, (nome, grupo, ticks, laco, clsn) in ACOES.items():
        quadros, t = render(nome)
        air = efeitos.por_acao(air, acao, texto_acao(grupo, quadros, ticks or t, laco, clsn))
        novos[grupo] = [(img, ex, ey) for img, ex, ey in quadros]
    quadros, raio, some = acoes_da_rajada()
    air = efeitos.por_acao(air, 7420, raio)
    air = efeitos.por_acao(air, 7421, some)
    novos[7420] = quadros
    for g, (quadros, texto) in acoes_do_fogo().items():  # o fogo do agarrão do Diabo (#45)
        air = efeitos.por_acao(air, g, texto)
        novos[g] = quadros
    cob, texto = acao_cobranca()
    if cob:
        air = efeitos.por_acao(air, 1660, texto)
        novos[COBRANCA["grupo"]] = cob
    for acao, quadros in patroa().items():
        air = efeitos.por_acao(air, acao, "\n".join(f"{acao},{i}, 0,0, {t}, , , 0.3333, 0.3333"
                                                      for i, (*_, t) in enumerate(quadros)))
        novos[acao] = [(img, ex, ey) for img, ex, ey, _ in quadros]
    a = montar_aura()
    a.conferir(acoes=re.findall(r"^\[Begin Action (\d+)\]", air, re.M))
    air = air.rstrip() + "\n\n" + a.air()
    for g, k, img, ex, ey in a.sprites():
        novos.setdefault(g, []).append((img, ex, ey))
    air = re.sub(r"\n{3,}", "\n\n", air)
    usados = {(int(g), int(i)) for g, i in efeitos.RE_ELEMENTO.findall(air)}
    velhos = {g for g in velhos if not any(u[0] == g for u in usados)}
    pal, nos, _ = cs.ler(sff)
    diabo = sprites_do_diabo(nos)
    rle, png, vistos = [], [], set()
    for n in nos:
        k = (n["g"], n["i"])
        if k in vistos or n["g"] in novos or n["g"] in velhos or n["g"] >= DIABO:
            continue
        vistos.add(k)
        (png if n.get("png") else rle).append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
    for g, quadros in novos.items():
        for i, (img, ex, ey) in enumerate(quadros):
            png.append((g, i, img.width, img.height, int(ex), int(ey), efeitos.blob_png(img)))
    for g, i, img, ex, ey in diabo:
        png.append((g, i, img.width, img.height, int(ex), int(ey), efeitos.blob_png(img)))
    efeitos.gravar(sff, pal, rle, png)
    arq_air.write_text(air, encoding="utf-8", newline="\n")
    arq_cns.write_text(ligar_cns(cns, diabo, a.cns(cabecalho=True), bool(cob)), encoding="utf-8", newline="\n")
    arq_cmd.write_text(ligar_cmd(cmd, bool(cob)), encoding="utf-8", newline="\n")
    import gerar_sons  # sons da pedra, do ki e da rajadona (ESPECIAIS["hazaki"]): depois dos estados novos
    gerar_sons.ligar("hazaki", pasta)
    import aura_no_corpo  # as asas seguem o corpo (issue #51): mede os desenhos e refaz a tabela no [Statedef -4]
    aura_no_corpo.aplicar("hazaki", pasta)
    print(f"hazaki: pedra, bola de ki e Diabo Loiro ({len(diabo)} desenhos do Diabo, aura de {len(a.camadas)} "
          f"camadas); {len(rle) + len(png)} sprites no .sff")


def religar_aura(pasta=SAIDA):
    """Só a aura, em cima de um chars/hazaki já pronto (o `aplicar` só roda logo depois do gerar_hazaki.py): troca as
    ações, os sprites e o [Statedef -4] da aura pelos do montar_aura() de agora e prende de novo ao corpo."""
    import aura_no_corpo
    import despertados_47
    pasta = Path(pasta)
    sff, arq_air, arq_cns = (pasta / f"hazaki.{e}" for e in ("sff", "air", "cns"))
    a = montar_aura()
    cns = aura_no_corpo.desfazer(arq_cns.read_text(encoding="utf-8"))
    air, cns = despertados_47.ligar_aura(a, arq_air.read_text(encoding="utf-8"), cns)
    pal, nos, _ = cs.ler(sff)
    grupos = set(a.ids())
    rle, png, vistos = [], [], set()
    for n in nos:
        k = (n["g"], n["i"])
        if k in vistos or n["g"] in grupos:
            continue
        vistos.add(k)
        (png if n.get("png") else rle).append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
    for g, i, img, ex, ey in a.sprites():
        png.append((g, i, img.width, img.height, int(ex), int(ey), efeitos.blob_png(img)))
    efeitos.gravar(sff, pal, rle, png)
    arq_air.write_text(re.sub(r"\n{3,}", "\n\n", air), encoding="utf-8", newline="\n")
    arq_cns.write_text(cns, encoding="utf-8", newline="\n")
    aura_no_corpo.aplicar("hazaki", pasta)
    print(f"hazaki: aura religada ({len(a.camadas)} camadas, explods {a.ids()[0]} a {a.ids()[-1]})")


if __name__ == "__main__":
    religar_aura() if "--aura" in sys.argv else aplicar()
