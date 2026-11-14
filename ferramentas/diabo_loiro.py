#!/usr/bin/env python3
"""Pós-passo do Hazak (issue #44 do Breno, 2026-11-14): golpes de longe novos e o Diabo Loiro.

  python ferramentas/diabo_loiro.py        reaplica em chars/hazaki (o gerar_hazaki.py já chama no fim)

Como o efeitos.py e o parry.py, trabalha em cima do que o gerador gravou em chars/hazaki (sff, air, cns): os efeitos
entram no .sff como PNG de 32 bits (fora da paleta do corpo) e as ações do .air são escritas aqui.

Golpes de longe (os estados estão no gerar_hazaki.py, cns_especiais; os efeitos, no hazak_poderes_blender.py):
  Pedra       7401 a pedra subindo do chão (Explod), 1005 a pedra em voo (projétil), 7402 a pedra quebrando
  Bola de ki  7410 o ki juntando nas mãos (Explod), 1605 a bola vermelha (projétil), 7411 a bola estourando
Diabo Loiro (o Despertar do Hazak, que até aqui não existia no jogo):
  arte        cada desenho 3x do corpo ganha o gêmeo do Diabo (diabo_arte.py) no grupo + 20000, e o
              [RemapPreset despertado] troca um pelo outro enquanto o var(20) corre (como no Pengaró e no Gutto)
  cena        estado 2000 (x + y com a barra cheia): bate o pé, olha para trás e pergunta "Ô vida, posso despertar?";
              a patroa (7450-7452) entra, faz que sim e sai; no último desenho ele vira o Diabo num estouro de ouro
  aura        as asas de ouro derretido, a coroa, a brasa no chão e as notas queimando (sprites/hazaki/aura, já
              aprovadas), ligadas pelo ferramentas/aura.py (Explods 9600-9601, [Statedef -4])
  rajadona    Rajadona de Ki das Trevas (1650): com o Diabo e 1 estoque, → ← x/y vira o raio enorme e contínuo, preto,
              vermelho e ouro (7420 o raio, 7421 o raio se desfazendo), 12 acertos
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
import diabo_arte  # noqa: E402
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
    """[(grupo, índice, RGBA, eixo x, eixo y)] do Diabo, um para cada desenho do corpo (índices 1 a 15 da paleta)."""
    saida, vistos = [], set()
    for n in nos:
        k = (n["g"], n["i"])
        if k in vistos or n.get("png") or n["g"] == 9000 or n["g"] >= DIABO:
            continue
        vistos.add(k)
        ind = np.frombuffer(n["px"], np.uint8).reshape(n["h"], n["w"])
        if ind.max() > 15 or not ind.any():
            continue
        img, (ex, ey) = diabo_arte.diabo(ind, (n["x"], n["y"]))
        cx = img.getchannel("A").getbbox()
        saida.append((n["g"] + DIABO, n["i"], img.crop(cx), ex - cx[0], ey - cx[1]))
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
                 "pausetime = 1, 3", "sparkno = -1", "guard.sparkno = S9216", "hitsound = F5,2",
                 "guardsound = F6,0", "ground.type = High", "ground.slidetime = 8", "ground.hittime = 12",
                 "ground.velocity = -1.2", "air.velocity = -1.5,-2", "air.juggle = 0"))
    c.append(ctl(1650, "Chama no oponente", "Explod", "trigger1 = ProjHitTime(1650) = 0", "anim = 9270",
                 "postype = p2", "pos = -10, -60", "sprpriority = 5", "ownpal = 1", "removetime = -2",
                 "random = 30, 40"))
    c.append(ctl(1650, "Tremida", "EnvShake", f"trigger1 = Time = {r['sai']}", f"time = {r['dura']}", "ampl = 2",
                 "freq = 140"))
    c.append(ctl(1650, "Clarão", "BGPalFX", f"trigger1 = Time = {r['sai']}", "time = 4", "add = 120, 40, 0",
                 "ignorehitpause = 1"))
    c.append(ctl(1650, "Fim", "ChangeState", "trigger1 = AnimTime = 0", "value = 0", "ctrl = 1"))
    return "".join(c)


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


def agarrao_do_diabo(cns):
    """No Diabo o Abraço de Quebrada (810) pega fogo: chama laranja-ouro em cada pancada e o fim explode em ouro."""
    m = re.search(r"^\[Statedef 810\][^\n]*\n.*?(?=^\[Statedef )", cns, re.M | re.S)
    assert m, "sem o estado 810 (agarrão em pé)"
    bloco = m.group(0)
    extra = []
    for k, t in enumerate(int(x) for x in re.findall(r"\[State 810, Pancada \d+: dano\]\ntype = TargetLifeAdd\n"
                                                      r"trigger1 = Time = (\d+)", bloco)):
        extra.append(ctl(810, f"Diabo: chama {k + 1}", "Explod", f"trigger1 = Time = {t}", "trigger1 = var(20) > 0",
                         "trigger1 = NumTarget", "anim = 9270", "postype = p2", "pos = 0, -55", "sprpriority = 6",
                         "ownpal = 1", "removetime = -2"))
    fim = re.search(r"\[State 810, Final: dano\]\ntype = TargetLifeAdd\ntrigger1 = Time = (\d+)", bloco)
    assert fim, "agarrão 810 sem o golpe final"
    t = int(fim.group(1))
    extra.append(ctl(810, "Diabo: estouro de ouro", "Explod", f"trigger1 = Time = {t}", "trigger1 = var(20) > 0",
                     "trigger1 = NumTarget", "anim = 9271", "postype = p2", "pos = 0, -50", "sprpriority = 6",
                     "ownpal = 1", "removetime = -2"))
    extra.append(ctl(810, "Diabo: dano do fogo", "TargetLifeAdd", f"trigger1 = Time = {t}", "trigger1 = var(20) > 0",
                     "trigger1 = NumTarget", "value = -40"))
    extra.append(ctl(810, "Diabo: tremida", "EnvShake", f"trigger1 = Time = {t}", "trigger1 = var(20) > 0",
                     "time = 14", "ampl = 4", "freq = 100"))
    marca = "[State 810, Segura]"
    assert marca in bloco
    novo = bloco.replace(marca, "".join(extra) + marca, 1)
    return cns.replace(bloco, novo, 1)


def ligar_cns(cns, diabo, aura_cns):
    assert "[Statedef 2000]" not in cns, "o Hazak já tem estado 2000: rode o gerar_hazaki.py antes"
    preset = "[RemapPreset despertado]\n" + "".join(f"{g - DIABO},{i} = {g},{i}\n" for g, i, *_ in diabo) + "\n"
    assert cns.count("[Data]") == 1
    cns = cns.replace("[Data]", preset + "[Data]", 1)
    cab = "[Statedef -2]\n\n"
    assert cns.count(cab) == 1
    cns = cns.replace(cab, cab + MENOS_2, 1)
    cns = agarrao_do_diabo(cns)
    cns = cns.replace(cab, cns_despertar() + cns_rajada() + cab, 1)
    return cns.rstrip() + "\n\n" + aura_cns


def ligar_cmd(cmd):
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
    arq_cns.write_text(ligar_cns(cns, diabo, a.cns(cabecalho=True)), encoding="utf-8", newline="\n")
    arq_cmd.write_text(ligar_cmd(cmd), encoding="utf-8", newline="\n")
    import gerar_sons  # sons da pedra, do ki e da rajadona (ESPECIAIS["hazaki"]): depois dos estados novos
    gerar_sons.ligar("hazaki", pasta)
    print(f"hazaki: pedra, bola de ki e Diabo Loiro ({len(diabo)} desenhos do Diabo, aura de {len(a.camadas)} "
          f"camadas); {len(rle) + len(png)} sprites no .sff")


if __name__ == "__main__":
    aplicar()
