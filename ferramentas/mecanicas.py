#!/usr/bin/env python3
"""Mecânicas do Nazafights Moderno (missão docs/missao-alisson-estilo-melty.md, item 5; issue #51).

  python3 ferramentas/mecanicas.py                 monta moderno/chars/<lutador>/ para os 5 lutadores
  python3 ferramentas/mecanicas.py hazaki ck       só esses

O Arcade (chars/) NÃO é tocado. O Moderno é o lutador do Arcade com as mecânicas por cima: a ferramenta lê
chars/<l>/ e grava em moderno/chars/<l>/ só os arquivos de texto que mudam (.cns, .cmd, .air, movelist.dat).
Para jogar ou testar, copie chars/<l>/ e ponha moderno/chars/<l>/ por cima (o robô faz isso com --moderno).
Rode de novo sempre que o lutador do Arcade mudar: o Moderno é refeito do zero a partir dele.

O que entra (igual para todos):
  1. Parry no estilo Shield: janela de JANELA ticks; acertou, os dois congelam CONGELA ticks com um clarão na cor do
     lutador e o som seco na hora do contato; o acertou continua cancelável em qualquer golpe e o oponente aberto 20
     ticks; errou, fica exposto EXPOSTO ticks a mais.
  2. Golpe final: parry certo na forma endiabrada vira super-cena (tela preta, zoom, golpe) e encerra o Despertar.
  3. Corrente: soco fraco (x) -> chute fraco (a) -> soco forte (y) -> chute forte (b) -> especial, por cancelamento
     quando o golpe encosta, em pé ou agachado. Pode pular degrau, não pode voltar.
  4. Dash no ar: -> -> ou <- <- no pulo, uma vez por pulo.

Todo controlador desta ferramenta tem "Mec:" no título, e os estados novos são 660, 661, 7700 e 7710.
"""
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

RAIZ = Path(__file__).resolve().parent.parent
LUTADORES = ("pengaro", "hazaki", "ck", "gutto", "raiclaven")

# ---- parry Shield
JANELA = 6      # ticks em que o parry pega (Arcade: 4)
CONGELA = 8     # ticks em que os dois ficam parados no parry certo (Arcade: 0)
EXPOSTO = 8     # ticks a mais de recuperação para quem errou
CLARAO = 14     # ticks do clarão (some aos poucos)

# ---- golpe final
# FINAL_BARRA = 0: basta estar na forma endiabrada (a barra zera ao despertar e a forma dura 10 s: não dá tempo de
# encher de novo). O golpe final encerra o Despertar. Se o Breno quiser exigir barra, ponha aqui o quanto (1000 = 1
# estoque) e ela é gasta.
FINAL_BARRA = 0
FINAL_DANO = 190   # dano cru; a forma endiabrada multiplica por 1,45 e o ataque do lutador entra por cima
FINAL_CARGA = 26   # ticks de carga no escuro antes do golpe
FINAL_PAUSA = 22   # ticks de congelamento no impacto (os estouros saem aqui)
FINAL_FONTE = 240  # golpe que empresta os desenhos (chute forte; 10240 quando o lutador tem a arte despertada)
E_FINAL, E_PRESO, A_FINAL = 7700, 7710, 7701

# ---- dash no ar
E_DASH, E_DASH_TRAS = 660, 661
DASH_VEL, DASH_VEL_TRAS, DASH_TICKS, DASH_BATE = 6.5, -6.0, 9, 5
DASH_ALTURA = 18  # altura mínima (px) para sair o dash

NOVOS = (E_DASH, E_DASH_TRAS, E_FINAL, E_PRESO)


# ---------------------------------------------------------------- texto
def secao(txt, n):
    """(início, fim) do [Statedef n] no texto."""
    m = re.search(rf"^\[Statedef {n}\][^\n]*\n.*?(?=^\[Statedef |\Z)", txt, re.M | re.S)
    assert m, f"sem Statedef {n}"
    return m.start(), m.end()


def no_estado(txt, n, fn):
    a, b = secao(txt, n)
    return txt[:a] + fn(txt[a:b]) + txt[b:]


def antes_do_controlador(sec, titulo, bloco):
    """Põe o bloco antes do controlador `[State ..., titulo]`; sem título, antes do primeiro controlador."""
    m = re.search(rf"^\[State [^\]\n]*, {re.escape(titulo)}\]" if titulo else r"^\[State ", sec, re.M)
    assert m, f"sem controlador {titulo!r}"
    return sec[:m.start()] + bloco + sec[m.start():]


def troca(sec, padrao, novo, n=1):
    sec, k = re.subn(padrao, novo, sec, flags=re.M)
    assert k == n, f"esperava {n} troca(s) de {padrao!r}, fiz {k}"
    return sec


def acao(air, numero):
    m = re.search(rf"^\[Begin Action {numero}\][^\n]*\n(.*?)(?=^\[Begin Action|\Z)", air, re.M | re.S)
    return m.group(1) if m else None


def elementos(texto):
    """[(linha do elemento, ticks, tem Clsn1)] da ação."""
    saida, clsn1 = [], False
    for ln in texto.splitlines():
        if re.match(r"\s*Clsn1\s*:", ln, re.I):
            clsn1 = True
        p = ln.split(";")[0].split(",")
        if len(p) >= 5 and re.fullmatch(r"\s*-?\d+\s*", p[0]) and re.fullmatch(r"\s*-?\d+\s*", p[1]):
            saida.append((ln, int(p[4]), clsn1))
            clsn1 = False
    return saida


def duracao(air, numero):
    return sum(max(t, 0) for _, t, _ in elementos(acao(air, numero)))


# ---------------------------------------------------------------- cores
def cores(lutador):
    """(clarão da forma base, clarão da endiabrada, brilho da carga do golpe final)."""
    import cena_transformacao as ct
    import parry
    base, endiabrado = parry.RAMPAS[lutador]
    return base[2][1], endiabrado[2][1], ct.LUTADORES[lutador]["brilho"]


# ---------------------------------------------------------------- 1. parry Shield
def parry_shield(cns, air, lutador):
    base, endiabrado, _ = cores(lutador)
    for postura in (760, 764):
        e = 10000 + postura if acao(air, 10000 + postura) else postura  # o Hazak usa a mesma ação nas duas formas
        d_base, d_end = duracao(air, postura) + EXPOSTO, duracao(air, e) + EXPOSTO
        n_base, n_end = len(elementos(acao(air, postura))), len(elementos(acao(air, e)))
        segura = (f"[State {postura}, Mec: errou, segura o último quadro]\ntype = ChangeAnim\ntrigger1 = AnimTime = 0\n"
                  f"value = Anim\nelem = ifelse(var(20) > 0, {n_end}, {n_base})\n\n")

        def fn(sec):
            sec = troca(sec, r"(, Desvia\]\ntype = ReversalDef\ntrigger1 = Time < )\d+", rf"\g<1>{JANELA}")
            sec = troca(sec, r"^pausetime = [^\n]*", f"pausetime = {CONGELA},{CONGELA}")
            sec = troca(sec, r"(, Fim\]\ntype = ChangeState\ntrigger1 = )[^\n]*",
                        rf"\g<1>Time >= ifelse(var(20) > 0, {d_end}, {d_base})")
            return antes_do_controlador(sec, "Fim", segura)
        cns = no_estado(cns, postura, fn)
    # o som do acertou tocava no fim do congelamento: agora toca no contato (Statedef -2, abaixo)
    for acertou in (761, 765):
        cns = no_estado(cns, acertou, lambda sec: re.sub(
            r"^\[State \d+, som comum\]\ntype = PlaySnd\n(?:[^\[\n][^\n]*\n)*?value = F30,\d\n(?:; som: fim\n)?\n", "",
            sec, flags=re.M))
    m = f"map(mec_c) / {CLARAO}.0"
    cor = lambda k, f: f"ifelse(var(20) > 0, {endiabrado[k]}, {base[k]}) * {f} * {m}"
    pegou = "(stateno = 761 || stateno = 765) && Time = 0 && map(mec_c) = 0"
    blocos = f"""[State -2, Mec: parry certo, som seco no contato]
type = PlaySnd
trigger1 = {pegou}
value = F30, (var(20) > 0)
ignorehitpause = 1

[State -2, Mec: parry certo, clarão liga]
type = MapSet
trigger1 = {pegou}
map = "mec_c"
value = {CLARAO + 1}
ignorehitpause = 1

[State -2, Mec: clarão conta]
type = MapAdd
trigger1 = map(mec_c) > 0
map = "mec_c"
value = -1
ignorehitpause = 1

[State -2, Mec: clarão no cenário, na cor do lutador]
type = BGPalFX
trigger1 = map(mec_c) > 0
time = 1
add = {cor(0, 0.55)}, {cor(1, 0.55)}, {cor(2, 0.55)}
ignorehitpause = 1

[State -2, Mec: clarão no lutador]
type = PalFX
trigger1 = map(mec_c) > 0
time = 1
add = {cor(0, 0.8)}, {cor(1, 0.8)}, {cor(2, 0.8)}
ignorehitpause = 1

[State -2, Mec: clarão no oponente]
type = PalFX
trigger1 = map(mec_c) > 0 && NumEnemy > 0
redirectid = enemynear,id
time = 1
add = {cor(0, 0.5)}, {cor(1, 0.5)}, {cor(2, 0.5)}
ignorehitpause = 1

[State -2, Mec: zera o clarão antes do round]
type = MapSet
trigger1 = RoundState < 2 && map(mec_c) != 0
map = "mec_c"
value = 0
ignorehitpause = 1

"""
    return cns, blocos


# ---------------------------------------------------------------- 2. golpe final
def golpe_final_air(air):
    fonte = 10000 + FINAL_FONTE if acao(air, 10000 + FINAL_FONTE) else FINAL_FONTE
    els = elementos(acao(air, fonte))
    k = next(i for i, e in enumerate(els) if e[2])  # 1º quadro com caixa de golpe
    impacto = FINAL_CARGA + sum(t for _, t, _ in els[:k])
    corpo = re.search(r"Clsn2(?:Default)?:\s*\d+\s*\n\s*Clsn2\[0\]\s*=\s*([-\d, ]+)", acao(air, fonte)).group(1).strip()
    linhas = ["Clsn2Default: 1", f" Clsn2[0] = {corpo}"]
    for i, (ln, t, _) in enumerate(els):
        p = [x.strip() for x in ln.split(",")]
        if i == 0:
            p[4] = str(t + FINAL_CARGA)  # a carga: segura a antecipação no escuro
        if k <= i <= k + 1:
            linhas += ["Clsn1: 1", " Clsn1[0] = 0, -330, 270, -20"]  # caixa larga: a cena não pode errar
        linhas.append(", ".join(p))
    total = FINAL_CARGA + sum(t for _, t, _ in els)
    texto = "\n".join(linhas)
    bloco = f"[Begin Action {A_FINAL}]\n{texto}\n\n"
    air = re.sub(rf"^\[Begin Action {A_FINAL}\][^\n]*\n.*?(?=^\[Begin Action|\Z)", "", air, flags=re.M | re.S)
    return air.rstrip() + "\n\n" + bloco, impacto, total


def golpe_final(lutador, impacto, total):
    _, _, brilho = cores(lutador)
    T, L, C = impacto, total, FINAL_CARGA
    luz = L - 14  # a luz começa a voltar
    escuro = f"ifelse(Time < 10, 256 - 25.6 * Time, ifelse(Time < {luz}, 0, min(256, 256 * (Time - {luz}) / 12.0)))"
    escuro_p2 = f"max(110, {escuro})"
    ease = f"(min(Time, {T}) / {T}.0) * (min(Time, {T}) / {T}.0) * (3 - 2 * min(Time, {T}) / {T}.0)"
    gasta = (f"[State {E_FINAL}, Mec: gasta a barra]\ntype = PowerAdd\ntrigger1 = Time = 0\nvalue = -{FINAL_BARRA}\n\n"
             if FINAL_BARRA else "")
    estados = f"""[Statedef {E_FINAL}]
type = S
movetype = A
physics = N
ctrl = 0
sprpriority = 3
anim = {A_FINAL}
velset = 0,0

[State {E_FINAL}, Mec: som de entrada]
type = PlaySnd
trigger1 = Time = 0
value = F31,0

{gasta}[State {E_FINAL}, Mec: chega perto]
type = VelSet
trigger1 = Time = 0
x = (P2BodyDist X - 22) / 8.0

[State {E_FINAL}, Mec: para]
type = VelSet
trigger1 = Time = 8
x = 0

[State {E_FINAL}, Mec: invencível]
type = NotHitBy
trigger1 = 1
value = SCA
time = 1
ignorehitpause = 1

[State {E_FINAL}, Mec: sem HUD e relógio parado]
type = AssertSpecial
trigger1 = Time < {L - 6}
flag = nobardisplay
flag2 = timerfreeze
ignorehitpause = 1

[State {E_FINAL}, Mec: tela preta]
type = BGPalFX
trigger1 = 1
time = 2
mul = {escuro}, {escuro}, {escuro}
ignorehitpause = 1

[State {E_FINAL}, Mec: oponente na penumbra]
type = PalFX
trigger1 = NumEnemy > 0 && !MoveHit
redirectid = enemynear,id
time = 2
mul = {escuro_p2}, {escuro_p2}, {escuro_p2}
ignorehitpause = 1

[State {E_FINAL}, Mec: brilho da forma]
type = PalFX
trigger1 = Time < {luz}
time = 2
add = {brilho[0]} * min(Time, {C}) / {C}, {brilho[1]} * min(Time, {C}) / {C}, {brilho[2]} * min(Time, {C}) / {C}
ignorehitpause = 1

[State {E_FINAL}, Mec: zoom]
type = Zoom
trigger1 = Time < {L - 8}
time = 2
pos = Pos X + P2Dist X * Facing * 0.5, Pos Y - 15
scale = 1.24 * (1 + 0.3 * {ease}) ** 0.5
lag = 0
endlag = 0.9
camerabound = 0
stagebound = 0
ignorehitpause = 1

[State {E_FINAL}, Mec: vento do golpe]
type = PlaySnd
trigger1 = Time = {C}
value = F40,3

[State {E_FINAL}, Mec: rastro]
type = AfterImage
trigger1 = Time = {C}
time = {L - C}
length = 8
trans = add
palbright = 40,40,40
palmul = .6,.6,.6
timegap = 1
framegap = 2

[State {E_FINAL}, Mec: o golpe]
type = HitDef
trigger1 = Time = {T}
attr = S, HA
damage = {FINAL_DANO}, 0
animtype = Up
hitflag = MAFD
priority = 7, Hit
pausetime = {FINAL_PAUSA}, {FINAL_PAUSA}
sparkno = S(ifelse(var(20) > 0, 7691, 7690))
sparkxy = -10, -65
sparkscale = 3, 3
hitsound = F5,3
envshake.time = {FINAL_PAUSA + 10}
envshake.freq = 60
envshake.ampl = 7
ground.type = High
ground.slidetime = 12
ground.hittime = 30
ground.velocity = -8,-9
air.velocity = -8,-9
fall = 1
fall.recover = 0
getpower = 0
givepower = 0
palfx.time = {FINAL_PAUSA}
palfx.add = 200,200,200

[State {E_FINAL}, Mec: encerra o Despertar]
type = VarSet
trigger1 = AnimTime = 0 && var(20) > 2
var(20) = 2

[State {E_FINAL}, Mec: fim]
type = ChangeState
trigger1 = AnimTime = 0
value = 0
ctrl = 1

[Statedef {E_PRESO}]
type = S
movetype = H
physics = N
ctrl = 0
anim = 5000
velset = 0,0

[State {E_PRESO}, Mec: no chão]
type = PosSet
trigger1 = Time = 0
y = 0

[State {E_PRESO}, Mec: de frente]
type = Turn
trigger1 = Time = 0 && P2Dist X < 0

[State {E_PRESO}, Mec: segura a pose]
type = ChangeAnim
trigger1 = AnimTime = 0
value = 5000

[State {E_PRESO}, Mec: solta se a cena acabar]
type = SelfState
trigger1 = Time >= {L + 10}
trigger2 = Time > 2 && NumEnemy > 0 && enemynear, stateno != {E_FINAL}
value = 0
ctrl = 1

"""
    cond = "(stateno = 761 || stateno = 765) && Time = 0 && var(20) > 0" + (
        f" && power >= {FINAL_BARRA}" if FINAL_BARRA else "")
    estouros = ""
    for i, (quando, dx, dy, esc) in enumerate(((FINAL_PAUSA, 0, -60, 4), (FINAL_PAUSA - 4, -18, -85, 2.6),
                                               (FINAL_PAUSA - 8, 16, -40, 3), (FINAL_PAUSA - 12, -8, -70, 3.4),
                                               (FINAL_PAUSA - 16, 10, -95, 2.4), (FINAL_PAUSA - 20, 0, -55, 4.5))):
        estouros += f"""[State -2, Mec: golpe final, estouro {i + 1}]
type = Explod
trigger1 = map(mec_f) = {quando} && NumEnemy > 0
anim = ifelse(var(20) > 0, 7691, 7690)
postype = p2
pos = {dx}, {dy}
scale = {esc}, {esc}
sprpriority = 6
ownpal = 1
removetime = -2
ignorehitpause = 1

"""
    menos2 = f"""[State -2, Mec: golpe final entra]
type = ChangeState
trigger1 = {cond}
value = {E_FINAL}
ctrl = 0

[State -2, Mec: golpe final, relógio do impacto]
type = MapSet
trigger1 = stateno = {E_FINAL} && MoveHit = 1 && map(mec_f) = 0
map = "mec_f"
value = {FINAL_PAUSA + 1}
ignorehitpause = 1

[State -2, Mec: golpe final, relógio conta]
type = MapAdd
trigger1 = map(mec_f) > 0
map = "mec_f"
value = -1
ignorehitpause = 1

[State -2, Mec: golpe final, clarão branco]
type = EnvColor
trigger1 = map(mec_f) = {FINAL_PAUSA}
value = 255, 255, 255
time = 3
ignorehitpause = 1

{estouros}[State -2, Mec: zera o golpe final antes do round]
type = MapSet
trigger1 = RoundState < 2 && map(mec_f) != 0
map = "mec_f"
value = 0
ignorehitpause = 1

"""
    preso = (f"[State 762, Mec: preso no golpe final]\ntype = ChangeState\n"
             f"trigger1 = NumEnemy > 0 && enemynear, stateno = {E_FINAL}\nvalue = {E_PRESO}\n\n")
    return estados, menos2, preso


# ---------------------------------------------------------------- 3. corrente
def tem_estado(cns, n):
    return re.search(rf"^\[Statedef {n}\]", cns, re.M) is not None


def corrente(cns):
    """Blocos do .cmd: degraus x(1) < a(2) < y(3) < b(4); o golpe cancela em qualquer degrau acima quando encosta."""
    ex = lambda *ns: [n for n in ns if tem_estado(cns, n)]
    x, a, y, b = ex(200, 400), ex(230, 430), ex(210, 215, 410), ex(240, 245, 440)
    ou = lambda ns: "(" + " || ".join(f"stateno = {n}" for n in ns) + ")"
    blocos = ""

    def entrada(nome, valor, botao, agachado, de, perto=None):
        gat = [f'triggerall = command = "{botao}"',
               f'triggerall = command {"=" if agachado else "!="} "holddown"', "triggerall = statetype != A"]
        if perto is not None:
            gat.append(f"triggerall = p2bodydist x {'<' if perto else '>='} 30")
        return (f"[State -1, Mec: corrente, {nome}]\ntype = ChangeState\nvalue = {valor}\n" + "\n".join(gat) +
                f"\ntrigger1 = {ou(de)} && movecontact\n\n")
    for botao, nome, de, baixo, perto, longe in (("b", "chute forte", x + a + y, 440, 245, 240),
                                                 ("y", "soco forte", x + a, 410, 215, 210),
                                                 ("a", "chute fraco", x, 430, None, 230)):
        if tem_estado(cns, baixo):
            blocos += entrada(f"{nome} agachado", baixo, botao, True, de)
        if perto and tem_estado(cns, perto):
            blocos += entrada(f"{nome} de perto", perto, botao, False, de, True)
            blocos += entrada(nome, longe, botao, False, de, False)
        else:
            blocos += entrada(nome, longe, botao, False, de)
    fortes = y + b
    cancela = (f"[State -1, Mec: o forte cancela em especial]\ntype = VarSet\n"
               f"trigger1 = {ou(fortes)} && movecontact && movecontact <= 8\nvar(1) = 1\n\n")
    return blocos, cancela


# ---------------------------------------------------------------- 4. dash no ar
def dash():
    def estado(n, vel, anim):
        return f"""[Statedef {n}]
type = A
movetype = I
physics = N
ctrl = 0
sprpriority = 1

[State {n}, Mec: gasta o dash do pulo]
type = MapSet
trigger1 = Time = 0
map = "mec_d"
value = 1

[State {n}, Mec: pose]
type = ChangeAnim
trigger1 = Time = 0 && SelfAnimExist({anim})
value = {anim}

[State {n}, Mec: vento]
type = PlaySnd
trigger1 = Time = 0
value = F40,1

[State {n}, Mec: rastro]
type = AfterImage
trigger1 = Time = 0
time = {DASH_TICKS + 3}
length = 6
trans = add
palbright = 30,30,30
palmul = .7,.7,.7
timegap = 1
framegap = 2

[State {n}, Mec: reto, sem cair]
type = VelSet
trigger1 = 1
x = {vel}
y = 0

[State {n}, Mec: pode bater]
type = CtrlSet
trigger1 = Time = {DASH_BATE}
value = 1

[State {n}, Mec: freia]
type = VelSet
trigger1 = Time >= {DASH_TICKS}
x = {vel * 0.45:.2f}

[State {n}, Mec: fim]
type = ChangeState
trigger1 = Time >= {DASH_TICKS}
value = 50
ctrl = 1

"""
    estados = estado(E_DASH, DASH_VEL, 42) + estado(E_DASH_TRAS, DASH_VEL_TRAS, 43)
    cmd = ""
    for nome, comando, valor in (("dash no ar", "FF", E_DASH), ("dash no ar para trás", "BB", E_DASH_TRAS)):
        cmd += (f"[State -1, Mec: {nome}]\ntype = ChangeState\nvalue = {valor}\ntriggerall = command = \"{comando}\"\n"
                f"triggerall = statetype = A\ntriggerall = map(mec_d) = 0\ntriggerall = Pos Y <= -{DASH_ALTURA}\n"
                f"trigger1 = ctrl\n\n")
    menos2 = ("[State -2, Mec: dash no ar, um por pulo]\ntype = MapSet\ntrigger1 = statetype != A && map(mec_d) != 0\n"
              "map = \"mec_d\"\nvalue = 0\nignorehitpause = 1\n\n")
    return estados, cmd, menos2


# ---------------------------------------------------------------- lista de golpes
MOVELIST = ("\n<#f0f000>:Moderno:</>\n"
            "Corrente <#bebebe>(encostou, cancela no próximo)</>\t\t^X^A^Y^B\n"
            "Dash no ar <#bebebe>(1 por pulo)</>\t\t_F_F / _B_B\n"
            "Golpe final <#bebebe>(parry certo no Endiabrado)</>\t\t_F^C / _D^C\n")


# ---------------------------------------------------------------- tudo
def aplicar(lutador, origem=None, destino=None):
    origem = Path(origem) if origem else RAIZ / "chars" / lutador
    destino = Path(destino) if destino else RAIZ / "moderno" / "chars" / lutador
    le = lambda ext: (origem / f"{lutador}.{ext}").read_bytes().decode("utf-8")
    cns, air, cmd = le("cns").replace("\r\n", "\n"), le("air").replace("\r\n", "\n"), le("cmd")
    crlf = "\r\n" in cmd
    cmd = cmd.replace("\r\n", "\n")
    assert "Mec:" not in cns and "Mec:" not in cmd, f"{origem} já tem as mecânicas: a origem é sempre o Arcade"
    for n in NOVOS:
        assert not tem_estado(cns, n), f"{lutador}: o estado {n} já existe"
    assert acao(air, A_FINAL) is None, f"{lutador}: a ação {A_FINAL} já existe"
    assert 'name = "FF"' in cmd and 'name = "BB"' in cmd

    cns, m2_parry = parry_shield(cns, air, lutador)
    air, impacto, total = golpe_final_air(air)
    e_final, m2_final, preso = golpe_final(lutador, impacto, total)
    c_blocos, c_cancela = corrente(cns)
    e_dash, cmd_dash, m2_dash = dash()

    cns = no_estado(cns, 762, lambda sec: antes_do_controlador(sec, None, preso))
    cns = troca(cns, r"^\[Statedef -2\]\n\n", "[Statedef -2]\n\n" + m2_final + m2_parry + m2_dash)
    a, _ = secao(cns, -2)
    cns = cns[:a] + e_dash + e_final + cns[a:]

    cmd = troca(cmd, r"(^\[State -1, Pode cancelar\]\n(?:[^\[\n][^\n]*\n)+\n)", lambda m: m.group(1) + c_cancela)
    cmd = troca(cmd, r"(?=^\[State -1, Corre\]\n)", lambda m: c_blocos + cmd_dash)

    destino.mkdir(parents=True, exist_ok=True)
    (destino / f"{lutador}.cns").write_text(cns, encoding="utf-8", newline="\n")
    (destino / f"{lutador}.air").write_text(air, encoding="utf-8", newline="\n")
    (destino / f"{lutador}.cmd").write_bytes((cmd.replace("\n", "\r\n") if crlf else cmd).encode("utf-8"))
    mov = origem / "movelist.dat"
    if mov.exists():
        (destino / "movelist.dat").write_text(mov.read_text(encoding="utf-8").rstrip("\n") + "\n" + MOVELIST,
                                              encoding="utf-8", newline="\n")
    print(f"{lutador}: Moderno em {destino.relative_to(RAIZ) if destino.is_relative_to(RAIZ) else destino} "
          f"(golpe final: impacto no tick {impacto}, cena de {total} ticks)")


def montar(lutador, pasta):
    """Lutador do Moderno inteiro em `pasta`: o do Arcade com moderno/chars/<lutador>/ por cima (robô e filmagem)."""
    pasta = Path(pasta)
    shutil.copytree(RAIZ / "chars" / lutador, pasta, dirs_exist_ok=True)
    shutil.copytree(RAIZ / "moderno" / "chars" / lutador, pasta, dirs_exist_ok=True)


def main():
    for lutador in sys.argv[1:] or LUTADORES:
        aplicar(lutador)


if __name__ == "__main__":
    main()
