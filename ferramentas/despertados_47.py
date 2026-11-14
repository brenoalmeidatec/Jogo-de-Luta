#!/usr/bin/env python3
"""Agarrão da forma e poder de longe de cada despertado (issue #47 do Breno, 2026-11-14): Pengaró, Gutto e CK.

  python ferramentas/despertados_47.py [lutador ...]      (sem nome: os três) reescreve chars/<l>/ .sff .air .cns .cmd
                                                          e o movelist.dat. Roda de novo sem duplicar nada.

O Hazak (Diabo Loiro, #44) e o Raiclaven (Cientista Louco, #43) ganham os deles nas threads dessas issues.

Agarrão da forma (estado 4700 -> 4710), no lugar do agarrão da forma básica enquanto var(20) > 0 (o Despertar):
  mesmo comando (y ou b com → ou ← colado), mesma pega e mesmo escape do agarrão segura-e-bate
  (ferramentas/agarrao_mk.py, de onde vem a montagem), mas as pancadas são golpes da forma desperta e o efeito
  da forma fica preso no oponente o tempo todo (ação 47000), com um estouro próprio no golpe que solta (47001):
    Pengaró  Algema das Sombras: correntes de sombra sobem do chão e enrolam o oponente; elos voam no final
    Gutto    Coice do Garanhão: raios caem em cima dele; o final solta ferraduras de raio
    CK       Paredão na Cara: as caixas de som estouram nele; o final é um estrondo
Poder de longe (estado 4750, ↓ → ↓ → + x ou y, só no Despertar, um por vez na tela):
  brilho de carga na mão (47003) e o projétil grande da forma (47002), 3 acertos que derrubam, estouro 47001 no fim:
    Pengaró  Maré das Correntes: onda de sombra rolando com duas correntes chicoteando na frente
    Gutto    Estouro do Garanhão: um garanhão de raio galopando pela tela
    CK       Paredão no Talo: anéis de som em fila, um paredão andando

Os desenhos saem do Blender (ferramentas/despertados_47_blender.py), em sprites/efeitos_blender/<l>/d47_*/. Vão
para o .sff como PNG de 32 bits (grupos 47000 a 47003), igual aos efeitos da #38, pelo efeitos.gravar. Rode depois do
gerador, do parry.py e do efeitos.py (eles regravam o .sff).
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))
import agarrao_mk as mk  # noqa: E402
import conferir_sff as cs  # noqa: E402
import efeitos  # noqa: E402

LUTADORES = ("pengaro", "gutto", "ck")
GRUPOS = {"agarrao": 47000, "final": 47001, "poder": 47002, "carga": 47003}
MARCA = "(despertados_47.py)"
ESCALA = efeitos.ESCALA_BLENDER  # o mesmo tamanho de pixel dos outros efeitos do Blender


class Cfg:
    def __init__(self, nome_agarrao, golpes, final, prio_agarrao, nome_poder, solta, offset, vel, som_carga,
                 som_solta, som_acerto, som_final=None):
        self.nome_agarrao, self.golpes, self.final = nome_agarrao, golpes, final
        self.prio_agarrao = prio_agarrao          # sprpriority do efeito preso no oponente (CK atrás dele)
        self.nome_poder, self.solta, self.offset, self.vel = nome_poder, solta, offset, vel
        # sons das formas da issue #46 (docs/sons.md): corrente do Pengaró 50,7; paredão do CK 50,5/50,2;
        # coice/galope/relincho do Gutto 50,5/50,2/50,3; 53,k é o acerto endiabrado. O gerar_sons.py não mexe
        # nestes estados (4700, 4710, 4750): os sons vêm daqui.
        self.som_carga, self.som_solta, self.som_acerto = som_carga, som_solta, som_acerto
        self.som_final = som_final or som_solta


# padrão do Breno (#47): tela escurece e tinge na cor da forma enquanto o golpe da forma acontece; clarão no impacto
TINTA = {"pengaro": ("120,96,150", "70,20,110"), "gutto": ("150,90,90", "120,20,20"),
         "ck": ("110,130,115", "40,90,60")}   # (BGPalFX mul do fundo, PalFX add no oponente atingido)

G = mk.Golpe
CFG = {
    "pengaro": Cfg("Algema das Sombras", (G(3433, 26, "palma torta"), G(3410, 26, "revolta de corrente"),
                                          G(3430, 26, "mão de chão possuída")), G(3413, 62, "roda da possessão"), -1,
                   "Maré das Correntes", 25, (60, -52), 3.0, "F40,4", "50,7", "S53,2"),
    "gutto": Cfg("Coice do Garanhão", (G(3433, 26, "palma"), G(3420, 26, "calcanhar"), G(3410, 26, "revolta")),
                 G(3423, 62, "coice final"), 4, "Estouro do Garanhão", 25, (40, -56), 3.6, "50,3", "50,2", "S53,2", "50,5"),
    "ck": Cfg("Paredão na Cara", (G(3433, 26, "palma"), G(3410, 26, "revolta"), G(3421, 26, "afastar pesado")),
              G(3413, 62, "roda"), -1, "Paredão no Talo", 22, (50, -78), 3.2, "50,2", "50,5", "S53,0"),
}


# ---------------------------------------------------------------------------------------------------------------- .sff
def desenhos(lutador, efeito):
    pasta = efeitos.BLENDER / lutador / f"d47_{efeito}"
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    ims = [Image.open(pasta / f"{i:02d}.png").convert("RGBA") for i in range(meta["quadros"])]
    return ims, meta


def gravar_sff(sff, lutador):
    pal, nos, _ = cs.ler(sff)
    rle, png, vistos = [], [], set()
    for n in nos:
        k = (n["g"], n["i"])
        if k in vistos or n["g"] in GRUPOS.values():
            continue
        vistos.add(k)
        (png if n.get("png") else rle).append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
    for efeito, g in GRUPOS.items():
        ims, meta = desenhos(lutador, efeito)
        px, py = meta["pivo"]
        for i, img in enumerate(ims):
            png.append((g, i, img.width, img.height, int(px), int(py), efeitos.blob_png(img)))
    efeitos.gravar(sff, pal, rle, png)


# ---------------------------------------------------------------------------------------------------------------- .air
def acao_efeito(lutador, efeito, escala=ESCALA, clsn=None):
    g = GRUPOS[efeito]
    ims, meta = desenhos(lutador, efeito)
    linhas = [f"[Begin Action {g}]", f"; {efeito} do despertado, issue #47 {MARCA}"]
    if clsn:
        linhas += ["Clsn2Default: 1", f" Clsn2[0] = {clsn}", "Clsn1Default: 1", f" Clsn1[0] = {clsn}"]
    for i in range(meta["quadros"]):
        if i == meta["laco"] and meta["laco"] >= 0:
            linhas.append("Loopstart")
        esc = f", , , {escala:g}, {escala:g}" if escala != 1 else ""
        linhas.append(f"{g},{i}, 0,0, {meta['ticks']}{esc}")
    return "\n".join(linhas)


def clsn_projetil(lutador):
    """Caixa do projétil: 80% do desenho. O motor desenha o projétil no projscale, mas mede a caixa na escala do
    lutador ([Size] 1/3), então a caixa vai em 3x."""
    ims, meta = desenhos(lutador, "poder")
    w, h = ims[0].size
    esc = escala_poder(lutador)
    mx = round((w - meta["pivo"][0]) * esc * 0.8 * 3)       # o corpo vai do pivô para a frente; o rastro não bate
    my = round(h * esc * 0.36 * 3)
    return f"-{mx}, -{my}, {mx}, {my}"


def escala_poder(lutador):
    """Escala do projétil na tela: a dos efeitos do Blender, ou a do desenho (o garanhão da aura do Gutto)."""
    return desenhos(lutador, "poder")[1].get("escala", ESCALA)


# ---------------------------------------------------------------------------------------------------------------- .cns
def ctl(n, nome, tipo, *linhas):
    return mk.ctl(n, f"{nome} {MARCA}", tipo, *linhas)


def statedef(cns, n):
    m = re.search(rf"^\[Statedef {n}\]\n.*?(?=^\[Statedef|^; ---- |\Z)", cns, re.M | re.S)
    return m.group(0) if m else None


def tirar_estados(cns, numeros):
    for n in numeros:
        m = re.search(rf"^\[Statedef {n}\]\n.*?(?=^\[Statedef|^; ---- |\Z)", cns, re.M | re.S)
        if m:
            cns = cns[:m.start()] + cns[m.end():]
    return cns


def estados_agarrao(lutador, air, cns):
    c = CFG[lutador]
    chave = f"{lutador}_47"
    base = mk.ROTEIROS[lutador]
    mk.ROTEIROS[chave] = mk.Roteiro(c.nome_agarrao, c.golpes, c.final, base.pega, base.bind)
    try:
        r, quadros, contatos, _ = mk.montar(chave, air, cns)
    finally:
        del mk.ROTEIROS[chave]
    acao = mk.acao_810(quadros, r).replace("[Begin Action 810]", "[Begin Action 4710]")
    texto, _ = mk.estados(r, contatos, None, 820)  # só o 810; os estados do oponente são os do agarrão básico
    texto = (texto.replace("[Statedef 810]", "[Statedef 4710]").replace("anim = 810", "anim = 4710")
             .replace("[State 810,", "[State 4710,"))
    fim = contatos[-1][0]
    primeiro = contatos[0][0]
    xf, yf = contatos[-1][4], contatos[-1][5]
    extra = (
        ctl(4710, "Efeito da forma no oponente", "Explod", f"trigger1 = Time = {max(1, primeiro - 6)}",
            "trigger1 = NumTarget", f"anim = {GRUPOS['agarrao']}", f"id = {GRUPOS['agarrao']}", "postype = p1",
            f"pos = {r.bind}, 0", "bindtime = -1", "removetime = -1", f"sprpriority = {c.prio_agarrao}",
            "ownpal = 1", "ignorehitpause = 1")
        + ctl(4710, "Tira o efeito", "RemoveExplod", f"trigger1 = Time = {fim}", f"trigger2 = !NumTarget",
              f"id = {GRUPOS['agarrao']}")
        + ctl(4710, "Estouro do final", "Explod", f"trigger1 = Time = {fim}", "trigger1 = NumTarget",
              f"anim = {GRUPOS['final']}", "postype = p1", f"pos = {xf}, {yf}", "removetime = -2",
              "sprpriority = 6", "ownpal = 1", "pausemovetime = 12")
        + ctl(4710, "Fundo escurece na cor da forma", "BGPalFX", "trigger1 = Time = 1", "trigger1 = NumTarget",
              f"time = {fim + 20}", f"mul = {TINTA[lutador][0]}", "sinadd = 0,0,0,0")
        + "".join(ctl(4710, f"Pancada {k + 1}: tremida", "EnvShake", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                      "time = 8", "freq = 140", "ampl = -4") for k, (t, *_r) in enumerate(contatos[:-1]))
        + "".join(ctl(4710, f"Pancada {k + 1}: oponente pisca", "PalFX", f"trigger1 = Time = {t}",
                      "trigger1 = NumTarget", "redirectid = target,id", "time = 6", f"add = {TINTA[lutador][1]}")
                  for k, (t, *_r) in enumerate(contatos))
        + ctl(4710, "Final: congela no impacto", "Pause", f"trigger1 = Time = {fim}", "trigger1 = NumTarget",
              "time = 12", "movetime = 0")
        + ctl(4710, "Final: clarão", "BGPalFX", f"trigger1 = Time = {fim}", "time = 6", "add = 120,120,120",
              f"mul = {TINTA[lutador][0]}")
        + ctl(4710, "Final: tremida forte", "EnvShake", f"trigger1 = Time = {fim}", "time = 30", "freq = 90",
              "ampl = -11")
        + ctl(4710, "Som do final", "PlaySnd", f"trigger1 = Time = {fim}", f"value = {c.som_final}")
        + ctl(4710, "Som de pegar", "PlaySnd", "trigger1 = Time = 0", "value = F35,0")
        + ctl(4710, "Som da forma", "PlaySnd", f"trigger1 = Time = {max(1, primeiro - 6)}", "trigger1 = NumTarget",
              f"value = {c.som_solta}", "channel = 3")
    )
    # entra antes do "Fim" do 4710
    texto = texto.replace("[State 4710, Fim]", extra + "[State 4710, Fim]", 1)
    pega = statedef(cns, 800)
    assert pega and "p1stateno = 810" in pega, f"{lutador}: [Statedef 800] sem p1stateno = 810"
    pega = (pega.replace("[Statedef 800]", "[Statedef 4700]").replace("[State 800,", "[State 4700,")
            .replace("p1stateno = 810", "p1stateno = 4710"))
    pega = f"; Agarrão do despertado: {c.nome_agarrao} (issue #47) {MARCA}\n" + pega
    return acao, pega.rstrip() + "\n\n" + texto, r, contatos


def estado_poder(lutador):
    c = CFG[lutador]
    s = c.solta
    ox, oy = c.offset
    t = [f"; Poder de longe do despertado: {c.nome_poder} (issue #47) {MARCA}\n",
         "[Statedef 4750]\ntype = S\nmovetype = A\nphysics = S\nctrl = 0\nsprpriority = 2\nanim = 3400\n"
         "juggle = 4\nvelset = 0,0\npoweradd = 0\n\n"]
    esc = escala_poder(lutador)
    t.append(ctl(4750, "Som da carga", "PlaySnd", "trigger1 = Time = 0", f"value = {c.som_carga}"))
    # carga: o mundo para e escurece, só ele se mexe (SuperPause), com rastro do corpo e a carga crescendo na mão
    t.append(ctl(4750, "Carga: tudo para e escurece", "SuperPause", "trigger1 = Time = 0", f"time = {s}",
                 f"movetime = {s}", "anim = -1", "darken = 1", "poweradd = 0", "unhittable = 0"))
    t.append(ctl(4750, "Carga: rastro do corpo", "AfterImage", "trigger1 = Time = 0", f"time = {s + 14}",
                 "length = 8", "timegap = 2", "framegap = 2", "trans = add", f"palcolor = 0",
                 f"paladd = {TINTA[lutador][1]}", "palmul = .55,.55,.55"))
    t.append(ctl(4750, "Carga na mão", "Explod", f"trigger1 = Time = {max(0, s - 20)}",
                 f"anim = {GRUPOS['carga']}", "postype = p1", f"pos = {ox - 6}, {oy}", "bindtime = -1",
                 "removetime = -2", "sprpriority = 5", "ownpal = 1", "supermovetime = 30", "scale = 1.4, 1.4"))
    t.append(ctl(4750, "Carga: treme de leve", "EnvShake", f"trigger1 = Time = {max(0, s - 14)}", "time = 14",
                 "freq = 180", "ampl = -2"))
    t.append(ctl(4750, "Som de soltar", "PlaySnd", f"trigger1 = Time = {s}", f"value = {c.som_solta}"))
    t.append(ctl(4750, "Solta: tremida forte", "EnvShake", f"trigger1 = Time = {s}", "time = 26", "freq = 100",
                 "ampl = -7"))
    t.append(ctl(4750, "Solta: fundo na cor da forma", "BGPalFX", f"trigger1 = Time = {s}", "time = 70",
                 f"mul = {TINTA[lutador][0]}"))
    t.append(ctl(4750, "Solta: recuo", "VelSet", f"trigger1 = Time = {s}", "x = -2.2"))
    t.append(ctl(4750, "Solta: freia", "VelMul", f"trigger1 = Time > {s}", "x = .8"))
    t.append(ctl(4750, c.nome_poder, "Projectile", f"trigger1 = Time = {s}",
                 "projid = 4750", f"projanim = {GRUPOS['poder']}", f"projhitanim = {GRUPOS['final']}",
                 f"projremanim = {GRUPOS['final']}", f"projscale = {esc:g}, {esc:g}", "projhits = 3",
                 "projmisstime = 7", "projpriority = 5", "projsprpriority = 4", f"offset = {ox}, {oy}",
                 f"velocity = {c.vel}, 0", "attr = S, SP", "damage = 42, 6", "animtype = Heavy",
                 "guardflag = MA", "hitflag = MAFD", "pausetime = 14, 18", "sparkno = -1", "guard.sparkno = S9202",
                 "envshake.time = 24", "envshake.freq = 90", "envshake.ampl = -9", f"hitsound = {c.som_acerto}",
                 "guardsound = F6,0", "ground.type = High", "ground.slidetime = 14", "ground.hittime = 18",
                 "ground.velocity = -3.5, -4", "air.velocity = -3, -4", "fall = 1", "fall.recover = 0",
                 "air.fall = 1", "down.velocity = -3, -4", "down.hittime = 18", "palfx.time = 14",
                 f"palfx.add = {TINTA[lutador][1]}", "palfx.sinadd = 30,30,30,4"))
    t.append(ctl(4750, "Fim", "ChangeState", "trigger1 = AnimTime = 0", "value = 0", "ctrl = 1"))
    return "".join(t)


def ligar_cns(lutador, air, cns):
    cns = tirar_estados(cns, (4700, 4710, 4750))
    cns = re.sub(rf"^; (Agarrão|Poder de longe) do despertado:[^\n]*{re.escape(MARCA)}\n", "", cns, flags=re.M)
    acao, texto, r, contatos = estados_agarrao(lutador, air, cns)
    bloco = texto + "\n" + estado_poder(lutador)
    # antes dos estados do oponente do agarrão (bloco do agarrao_mk, no fim do .cns)
    i = cns.index(mk.MARCA)
    cns = cns[:i].rstrip() + "\n\n" + bloco.rstrip() + "\n\n" + cns[i:]
    return acao, cns, r, contatos


# ---------------------------------------------------------------------------------------------------------------- .cmd
CMD_PODER = '[Command]\r\nname = "poder47"\r\ncommand = ~D, F, D, F, {b}\r\ntime = 30\r\n\r\n'


def ligar_cmd(lutador, cmd):
    cmd = re.sub(rf"\[State -1, [^\]]*{re.escape(MARCA)}\]\r?\n.*?\r?\n\r?\n", "", cmd, flags=re.S)
    cmd = re.sub(r'\[Command\]\r?\nname = "poder47"\r?\n.*?\r?\n\r?\n', "", cmd, flags=re.S)
    nl = "\r\n" if "\r\n" in cmd else "\n"
    # comando: antes do primeiro [Command] (vem antes de "bola_fraca" ~D, F, x)
    i = cmd.index("[Command]")
    cmd = cmd[:i] + (CMD_PODER.format(b="x") + CMD_PODER.format(b="y")).replace("\r\n", nl) + cmd[i:]
    # agarrão do despertado: uma cópia de cada entrada do agarrão básico, antes dela, com var(20) > 0
    partes = re.split(r"(?=\[State -1, Agarrao\])", cmd)
    out = [partes[0]]
    for p in partes[1:]:
        bloco = re.match(r"\[State -1, Agarrao\].*?(?:\r?\n){2}", p, re.S)
        if bloco and re.search(r"^value = 800\r?$", bloco.group(0), re.M):
            novo = (bloco.group(0).replace("[State -1, Agarrao]", f"[State -1, Agarrao do despertado {MARCA}]")
                    .replace("value = 800", "value = 4700"))
            novo = re.sub(r"(value = 4700\r?\n)", rf"\1triggerall = var(20) > 0{nl}", novo, count=1)
            out.append(novo)
        out.append(p)
    cmd = "".join(out)
    # poder: logo no começo do [Statedef -1], antes dos especiais de meia-lua
    poder = (f"[State -1, Poder de longe do despertado {MARCA}]{nl}type = ChangeState{nl}value = 4750{nl}"
             f'triggerall = command = "poder47"{nl}triggerall = var(20) > 0{nl}triggerall = statetype != A{nl}'
             f"triggerall = NumProjID(4750) = 0{nl}trigger1 = ctrl{nl}{nl}")
    m = re.search(r"^\[Statedef -1\][^\n]*\n(?:[^\[\n][^\n]*\n)*\r?\n?", cmd, re.M)
    cmd = cmd[:m.end()] + poder + cmd[m.end():]
    assert cmd.count("value = 4700") >= 1, f"{lutador}: não achei o agarrão básico no .cmd"
    return cmd


# ---------------------------------------------------------------------------------------------------------------- movelist
def ligar_movelist(lutador, texto):
    c = CFG[lutador]
    texto = re.sub(rf"^.*\(#47\).*\n", "", texto, flags=re.M)
    linhas = (f"{c.nome_poder} <#bebebe>(poder de longe) (#47)</>\t\t_D_F_D_F^P\n"
              f"{c.nome_agarrao} <#bebebe>(agarrão da forma) (#47)</>\t\t_F/_B+^Y\n")
    chave = ":Exclusivos do Despertar:</>\n"
    if chave in texto:
        return texto.replace(chave, chave + linhas, 1)
    return texto.rstrip("\n") + "\n" + linhas


# ---------------------------------------------------------------------------------------------------------------- tudo
def aplicar(lutador, pasta=None):
    pasta = Path(pasta) if pasta else RAIZ / "chars" / lutador
    arq = {e: pasta / f"{lutador}.{e}" for e in ("sff", "air", "cns", "cmd")}
    air = arq["air"].read_text(encoding="utf-8")
    cns = arq["cns"].read_text(encoding="utf-8")
    cmd = arq["cmd"].read_bytes().decode("utf-8")
    acao, cns, r, contatos = ligar_cns(lutador, air, cns)
    air = efeitos.por_acao(air, 4710, acao.split("\n", 1)[1])
    for efeito in ("agarrao", "final", "carga"):
        air = efeitos.por_acao(air, GRUPOS[efeito], acao_efeito(lutador, efeito).split("\n", 1)[1])
    air = efeitos.por_acao(air, GRUPOS["poder"],
                           acao_efeito(lutador, "poder", escala=1, clsn=clsn_projetil(lutador)).split("\n", 1)[1])
    air = re.sub(r"\n{3,}", "\n\n", air)
    cmd = ligar_cmd(lutador, cmd)
    gravar_sff(arq["sff"], lutador)
    arq["air"].write_text(air, encoding="utf-8", newline="\n")
    arq["cns"].write_text(cns, encoding="utf-8", newline="\n")
    arq["cmd"].write_bytes(cmd.encode("utf-8"))
    mv = pasta / "movelist.dat"
    if mv.exists():
        mv.write_text(ligar_movelist(lutador, mv.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    print(f"{lutador}: {r.nome} ({len(contatos) - 1} pancadas + final, dano {sum(x[1] for x in contatos)}, "
          f"solta no tick {contatos[-1][0]}); {CFG[lutador].nome_poder} (3 x 42)")


def main():
    for l in sys.argv[1:] or LUTADORES:
        aplicar(l)


if __name__ == "__main__":
    main()
