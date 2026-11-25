#!/usr/bin/env python3
"""IA da CPU (checkup geral, 25/11/2026): a CPU deixa de apertar botão ao acaso e passa a lutar.

  python3 ferramentas/ia_cpu.py                 aplica nos 6 lutadores
  python3 ferramentas/ia_cpu.py pengaro ck      só nesses
  python3 ferramentas/ia_cpu.py --tirar         tira a IA (volta a CPU do motor, que só aperta botão ao acaso)
  python3 ferramentas/ia_cpu.py --mostrar ck    mostra o que a IA vai usar de cada lutador

Antes, nenhum lutador tinha IA: a CPU do IKEMEN só "amassa" botão e direção ao acaso (AiInput.Update) e, de vez em
quando, solta um comando especial sorteado. Por isso a CPU pulava e agachava à toa, soltava bola de longe sem motivo
e nunca usava o Despertar.

Como funciona: um bloco no fim do [Statedef -2] de cada .cns (só quando AILevel > 0, isto é, só na CPU):
  1. desliga o botão aleatório e o comando sorteado do motor (AssertSpecial noaibuttonjam/noaicheat);
  2. decide UMA ação por tique (var(49)) e "aperta" os comandos dela com AssertCommand, os mesmos nomes que o
     jogador aperta. Quem decide se o golpe sai é o próprio .cmd do lutador (barra, forma, cancelamento): a IA
     não pula regra nenhuma e não tem golpe exclusivo;
  3. anda, agacha e pula por conta própria (o motor só faz isso com tecla de verdade);
  4. defende pela chance do nível (AssertSpecial autoguard, sorteado UMA vez por golpe que vem).
A tabela de golpes sai sozinha do .cmd/.cns/.air (ferramentas/ia_analise.py): alcance da caixa de ataque, início,
se é projétil, agarrão, antiaéreo, super. Golpe novo entra sozinho na próxima vez que o gerador rodar.

O nível da CPU (Opções > Dificuldade, 1 a 8) muda reflexo, chance de defender, de emendar combo e de punir.
Variáveis usadas (livres nos 6): var(44) tempo do plano de andar, var(45) plano, var(46) vontade de cutucar,
var(47) combo, var(48) defesa, var(49) ação do tique.
Pode rodar quantas vezes quiser: o bloco fica entre as marcas e é trocado, não duplicado.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ia_analise  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
LUTADORES = ("pengaro", "hazaki", "ck", "gutto", "raiclaven", "gbzin")
INICIO = "; >>> ia_cpu.py (IA da CPU, checkup 25/11): gerado, nao edite a mao\n"
FIM = "; <<< ia_cpu.py\n"
BOTOES = {"x", "y", "a", "b", "c", "z", "s"}
DIRECOES = {"holdfwd", "holdback", "holddown", "holdup"}
FORA = ("parry", "rolar", "afastar", "FF", "BB", "superpulo")
ESCAPE_ESTADOS = (820, 832)  # agarrão normal dos 6: y ou b nos 7 primeiros tiques soltam (estado do agarrador)


# nível efetivo: o da dificuldade; o chefe final do Arcade luta sempre no 8
NIVEL = "ifelse(map(chefe_final) > 0, 8, AILevel)"


def L(a, b):
    """Chance (em milésimos, contra random) que cresce com o nível da CPU: a no nível 0, +b por nível."""
    return f"random < {a} + {b} * {NIVEL}"


def classificar(an):
    """Separa os golpes do lutador nas gavetas que a IA usa."""
    gav = {"normal": [], "especial": [], "projetil": [], "super": [], "despertar": [], "agarrao": [], "ar": [],
           "antiaereo": [], "provoca": []}
    vistos = set()
    for g in an["golpes"]:
        cmds = list(g["cmds"])
        if "holdfwd" in cmds and "holdback" in cmds:
            cmds.remove("holdback")  # agarrão: "frente ou trás" no .cmd; a IA aperta frente
        nomeados = [c for c in cmds if c not in BOTOES and c not in DIRECOES]
        if any(c in FORA for c in cmds):
            continue
        tl = g["trig"].lower().replace(" ", "")
        neutro = any(re.search(r"^trigger\d+=(ctrl|var\(1\)|1)$", ln) for ln in tl.split("\n"))
        chave = (tuple(cmds), g["forma"], g["ar"])
        acao = {"cmds": cmds, "forma": g["forma"], "estado": g["estado"], "titulo": g["titulo"], "barra": g["barra"],
                "alcance": g["alcance"], "inicio": g["inicio"], "topo": g["topo"], "dano": g["dano"],
                "derruba": g["derruba"], "ar": g["ar"], "neutro": neutro}
        if "despertar" in cmds or g["titulo"].lower().startswith("despertar") or "(despertar)" in g["titulo"].lower():
            gav["despertar"].append(acao)
            continue
        if cmds == ["c"]:
            gav["provoca"].append(acao)
            continue
        if not neutro:
            continue  # continuação de corrente/kombo: sai quando a IA aperta o botão no combo
        if chave in vistos:
            # mesmo aperto, outro golpe (ex.: soco forte perto/longe): a IA fica com o maior alcance
            for a in gav["normal"] + gav["especial"] + gav["ar"]:
                if (tuple(a["cmds"]), a["forma"], a["ar"]) == chave and (g["alcance"] or 0) > (a["alcance"] or 0):
                    a["alcance"] = g["alcance"]
            continue
        vistos.add(chave)
        if g["ar"]:
            if g["hitdef"] and g["alcance"] is not None:
                gav["ar"].append(acao)
            continue
        if g["agarrao"]:
            gav["agarrao"].append(acao)
        elif g["barra"] >= 1000 and g["hitdef"]:
            gav["super"].append(acao)
        elif g["projetil"]:
            gav["projetil"].append(acao)
        elif g["hitdef"] and g["alcance"] is not None and g["inicio"] is not None and g["alcance"] >= 5:
            (gav["especial"] if nomeados else gav["normal"]).append(acao)
    for a in gav["normal"] + gav["especial"]:
        if a["topo"] is not None and a["topo"] <= -105 and a["inicio"] <= 11 and a["alcance"] >= 10:
            gav["antiaereo"].append(a)
    gav["antiaereo"].sort(key=lambda a: (a["inicio"], a["topo"]))
    return gav


def cond_forma(a):
    return {"despertado": "var(20) > 0", "base": "var(20) = 0"}.get(a["forma"], "1")


def bloco(an, gav):
    """Texto do bloco da IA para o fim do [Statedef -2]."""
    out = [INICIO]
    acoes = []  # (id, acao)

    def nova(a):
        acoes.append(a)
        return len(acoes)

    def ctl(titulo, tipo, linhas, ihp=True):
        txt = f"[State -2, IA: {titulo}]\ntype = {tipo}\n" + "\n".join(linhas) + "\n"
        if ihp:
            txt += "ignorehitpause = 1\n"
        out.append(txt + "\n")

    def escolhe(titulo, a, trig, chance):
        """VarSet var(49) = id da ação quando nada foi escolhido ainda neste tique."""
        i = nova(a)
        linhas = ["triggerall = AILevel > 0 && var(49) = 0 && roundstate = 2", f"triggerall = {cond_forma(a)}"]
        if a["barra"]:
            linhas.append(f"triggerall = power >= {a['barra']}")
        for k, t in enumerate(trig if isinstance(trig, list) else [trig], 1):
            linhas.append(f"trigger{k} = ({t}) && {chance}")
        linhas.append(f"var(49) = {i}")
        ctl(f"{titulo}: {a['titulo']}", "VarSet", linhas, ihp=False)

    D = "p2bodydist x"
    # 1. o motor para de amassar botão e de sortear comando
    ctl("sem botao aleatorio", "AssertSpecial", ["trigger1 = AILevel > 0", "flag = noaibuttonjam", "flag2 = noaicheat"])
    ctl("zera a acao do tique", "VarSet", ["trigger1 = AILevel > 0", "var(49) = 0"])
    # 2. defesa: sorteia uma vez por golpe que vem (golpe baixo é mais difícil de ler)
    ctl("decide se defende", "VarSet", ["trigger1 = AILevel > 0 && var(48) = 0 && inguarddist",
                                         f"var(48) = 1 + (random < 140 + 80 * {NIVEL} - 120 * (p2statetype = C))"])
    ctl("esquece a defesa", "VarSet", ["trigger1 = AILevel > 0 && var(48) != 0 && !inguarddist && p2movetype != A",
                                        "var(48) = 0"])
    ctl("defende", "AssertSpecial", ["trigger1 = AILevel > 0 && var(48) = 2 && roundstate = 2", "flag = autoguard"])
    # 3. combo: decide uma vez por golpe que acertou se emenda
    ctl("esquece o combo", "VarSet", ["trigger1 = AILevel > 0 && (movetype != A || time = 0)", "var(47) = 0"])
    ctl("decide o combo", "VarSet", ["trigger1 = AILevel > 0 && var(47) = 0 && movetype = A && movehit",
                                      f"var(47) = 1 + (random < 200 + 95 * {NIVEL})"])
    # 4. o dado do tique (0 a 999): escolhe a emenda do combo e a vontade de cutucar com um sorteio só
    ctl("dado do tique", "VarSet", ["trigger1 = AILevel > 0", "var(46) = random"])

    # ---- plano de andar (antes das escolhas: o pulo e o andar do tique já usam o plano novo)
    normais = sorted(a["alcance"] for a in gav["normal"]) or [40]
    R = normais[int(len(normais) * 0.7)] if len(normais) > 1 else normais[0]
    ctl("conta o plano", "VarAdd", ["trigger1 = AILevel > 0 && var(44) > 0", "var(44) = -1"])
    novo = "AILevel > 0 && var(44) <= 0 && roundstate = 2 && stateno != 40"  # não troca no meio do pulo
    ctl("sorteia o plano", "VarSet", [f"trigger1 = {novo}", "var(45) = random"])
    # 1 anda para frente, 2 para trás, 3 fica, 4 pula para frente, 5 agacha, 6 pula para trás
    far = f"{D} > {R + 70:.0f}"
    meio = f"{D} > {R - 5:.0f}"
    plano = (
        f"ifelse(p2statetype = L, ifelse(var(45) < 650, 1, 3), "
        f"ifelse({far}, ifelse(var(45) < 560, 1, ifelse(var(45) < 700, 4, ifelse(var(45) < 900, 3, 2))), "
        f"ifelse({meio}, ifelse(var(45) < 380, 1, ifelse(var(45) < 600, 3, ifelse(var(45) < 790, 2, "
        f"ifelse(var(45) < 880, 4, 5)))), "
        f"ifelse(var(45) < 250, 3, ifelse(var(45) < 430, 2, ifelse(var(45) < 570, 5, ifelse(var(45) < 920, 1, 6)))))))")
    ctl("escolhe o plano", "VarSet", [f"trigger1 = {novo}", f"var(45) = {plano}"])
    ctl("tempo do plano", "VarSet", [f"trigger1 = {novo}", "var(44) = 14 + random % 34"])
    ctl("encurralado nao recua", "VarSet", ["trigger1 = AILevel > 0 && (var(45) = 2 || var(45) = 6) && "
                                             "backedgebodydist < 20", "var(45) = 1"])
    # ---- escolhas, da mais urgente para a menos
    escape = {"cmds": ["y"], "forma": "as duas", "titulo": "escapar do agarrao", "barra": 0}
    estados = " || ".join(f"stateno = {s}" for s in ESCAPE_ESTADOS)
    escolhe("escapa", escape, f"movetype = H && ({estados}) && time >= 1 && time <= 6", L(60, 45))

    # emenda do combo: cada opção tem uma fatia igual do dado (sem a primeira da lista ganhar sempre)
    enders = [a for a in gav["especial"] if a["derruba"] or a["dano"] >= 70] or gav["especial"]
    pool = [("combo super", a, f"(var(20) > 0 || life < 300 || p2life < 250)")
            for a in gav["super"] if a["alcance"] is not None]  # na forma base guarda a barra para o Despertar
    pool += [("combo especial", a, "stateno = [200, 499]") for a in enders]
    pool += [("combo corrente", {"cmds": [b], "forma": "as duas", "titulo": b, "barra": 0}, "stateno = [200, 499]")
             for b in ("x", "y", "a", "b") if b in an["comandos"]]
    for k, (tit, a, cond) in enumerate(pool):
        lo, hi = 1000 * k // len(pool), 1000 * (k + 1) // len(pool)
        escolhe(tit, a, f"var(47) = 2 && movehit && movehit <= 8 && {cond}", f"var(46) >= {lo} && var(46) < {hi}")

    # chefe final do Arcade (motif/nazafight/nazafights.lua põe o map): barra cheia até despertar
    ctl("chefe final enche a barra", "PowerSet", ["trigger1 = AILevel > 0 && map(chefe_final) > 0 && var(20) = 0 && "
                                                  "roundstate = 2", "value = powermax"])
    for a in gav["despertar"]:
        a = dict(a, barra=0)  # o gatilho já pede power >= powermax
        escolhe("desperta", a, f"ctrl && statetype = S && power >= powermax && var(20) = 0 && ({D} > 90 || "
                               f"p2statetype = L || p2movetype = H || map(chefe_final) > 0)", L(20, 12))

    for a in gav["antiaereo"][:3]:
        alc = a["alcance"]
        escolhe("antiaereo", a, f"ctrl && statetype != A && p2statetype = A && p2dist y < -20 && p2dist y > -150 && "
                                f"{D} < {alc + 12:.0f} && enemynear, vel y > -3", L(40, 32))

    punir = sorted([a for a in gav["normal"] + gav["especial"] + gav["super"]
                    if a["inicio"] is not None and a["alcance"] is not None], key=lambda a: (a["inicio"], -a["dano"]))
    rapidos = [a for a in punir if a["inicio"] <= 9][:6]
    for a in sorted([s for s in gav["super"] if s["inicio"] is not None and s["alcance"] is not None],
                    key=lambda a: a["inicio"]):
        escolhe("pune com super", a, [f"ctrl && p2movetype = A && enemynear, movecontact = 0 && "
                                      f"enemynear, animtime >= -18 && {D} < {a['alcance'] + 4:.0f}",
                                      f"ctrl && prevstateno = [150, 155] && time <= 3 && {D} < {a['alcance'] + 4:.0f}"],
                f"(var(20) > 0 || life < 300 || random < 150) && {L(40, 30)}")
    for a in sorted(rapidos, key=lambda a: -a["dano"]):
        escolhe("pune", a, [f"ctrl && p2movetype = A && enemynear, movecontact = 0 && enemynear, animtime >= -18 && "
                            f"{D} < {a['alcance'] + 2:.0f}",
                            f"ctrl && prevstateno = [150, 155] && time <= 3 && {D} < {a['alcance'] + 2:.0f}"],
                L(60, 50))

    for a in gav["ar"]:
        escolhe("no ar", a, f"statetype = A && ctrl && p2dist y > 12 && {D} < {a['alcance'] + 8:.0f}", L(60, 30))

    for a in gav["agarrao"]:
        escolhe("agarra", a, [f"ctrl && statetype = S && {D} < 7 && "
                              f"p2statetype != A && p2movetype = I",
                              f"ctrl && statetype = S && {D} < 7 && p2stateno = [120, 155]"], L(25, 22))

    for a in gav["projetil"]:
        escolhe("solta de longe", a, f"ctrl && statetype = S && {D} > 110 && {D} < 330 && p2statetype != A",
                L(4, 4))

    for a in gav["normal"] + gav["especial"]:
        alc = a["alcance"]
        peso = "random < 380" if a in gav["normal"] else "random < 200"
        escolhe("cutuca", a, f"ctrl && statetype != A && p2statetype != A && p2statetype != L && "
                             f"var(46) < 8 + 7 * {NIVEL} && {D} >= {max(alc - 30, -10):.0f} && {D} <= {alc + 3:.0f}", peso)

    for a in gav["provoca"]:
        escolhe("provoca", a, f"ctrl && statetype = S && p2statetype = L && {D} > 120", "random < 4")

    # ---- aperta os comandos da ação escolhida (o .cmd do lutador decide se sai)
    for i, a in enumerate(acoes, 1):
        for c in a["cmds"]:
            ctl(f"aperta {c} ({a['titulo']})", "AssertCommand",
                [f"trigger1 = AILevel > 0 && var(49) = {i}", f'name = "{c}"', "buffer.time = 1"])

    parado = "AILevel > 0 && var(49) = 0 && roundstate = 2"
    ctl("segura frente", "AssertCommand", [f"trigger1 = {parado} && var(45) = 1 && ctrl && statetype = S",
                                           f"trigger2 = {parado} && var(45) = 4 && (ctrl && statetype = S || "
                                           f"stateno = 40)", 'name = "holdfwd"', "buffer.time = 1"])
    ctl("segura tras", "AssertCommand", [f"trigger1 = {parado} && var(45) = 2 && ctrl && statetype = S",
                                         f"trigger2 = {parado} && var(45) = 6 && (ctrl && statetype = S || "
                                         f"stateno = 40)", 'name = "holdback"', "buffer.time = 1"])
    ctl("segura cima", "AssertCommand", [f"trigger1 = {parado} && (var(45) = 4 || var(45) = 6) && "
                                         f"(ctrl && statetype = S || stateno = 40)", 'name = "holdup"',
                                         "buffer.time = 1"])
    ctl("segura baixo", "AssertCommand", [f"trigger1 = {parado} && var(45) = 5 && ctrl && statetype != A",
                                          'name = "holddown"', "buffer.time = 1"])
    # o freio e o "levanta" do motor rodam no começo do tique seguinte, olhando a tecla de verdade: as travas valem
    # já no tique em que a IA começa a andar ou agachar (senão ele para e recomeça todo tique)
    ctl("anda sem frear", "AssertSpecial", ["trigger1 = AILevel > 0 && (stateno = 0 || stateno = 20) && ctrl && "
                                            "(var(45) = 1 || var(45) = 2)", "flag = nobrake"])
    ctl("fica agachado", "AssertSpecial", ["trigger1 = AILevel > 0 && var(45) = 5 && statetype != A", "flag = nostand"])
    ctl("pulou: fica", "VarSet", ["trigger1 = AILevel > 0 && stateno = 50 && (var(45) = 4 || var(45) = 6)",
                                  "var(45) = 3"])
    # trocas de estado por último (ChangeState encerra o resto do -2)
    ctl("comeca a andar", "ChangeState", [f"trigger1 = {parado} && (var(45) = 1 || var(45) = 2) && ctrl && "
                                          f"stateno = 0", "value = 20"], ihp=False)
    ctl("para de andar", "ChangeState", [f"trigger1 = AILevel > 0 && stateno = 20 && ctrl && var(45) != 1 && "
                                         f"var(45) != 2", "value = 0"], ihp=False)
    ctl("agacha", "ChangeState", [f"trigger1 = {parado} && var(45) = 5 && ctrl && statetype = S && "
                                  f"stateno != 10", "value = 10"], ihp=False)
    ctl("pula", "ChangeState", [f"trigger1 = {parado} && (var(45) = 4 || var(45) = 6) && ctrl && statetype = S",
                                "value = 40"], ihp=False)
    out.append(FIM)
    return "".join(out), acoes


def tirar(txt):
    return re.sub(re.escape(INICIO) + r".*?" + re.escape(FIM) + r"\n?", "", txt, flags=re.S)


def aplicar(nome, pasta=None):
    pasta = Path(pasta) if pasta else RAIZ / "chars" / nome
    arq = pasta / f"{nome}.cns"
    bruto = arq.read_bytes().decode("utf-8")
    crlf = "\r\n" in bruto
    txt = tirar(bruto.replace("\r\n", "\n"))
    an = ia_analise.analisar(nome, pasta)
    gav = classificar(an)
    blo, acoes = bloco(an, gav)
    m = re.search(r"(?m)^\[Statedef -2\]\s*$", txt)
    assert m, f"sem [Statedef -2] em {arq}"
    prox = re.search(r"(?m)^\[Statedef ", txt[m.end():])
    pos = m.end() + (prox.start() if prox else len(txt) - m.end())
    novo = txt[:pos].rstrip("\n") + "\n\n" + blo + "\n" + txt[pos:]
    if crlf:
        novo = novo.replace("\n", "\r\n")
    arq.write_bytes(novo.encode("utf-8"))
    return gav, acoes


def mostrar(nome):
    gav = classificar(ia_analise.analisar(nome))
    print(f"== {nome}")
    for k, v in gav.items():
        print(f"  {k:10} {len(v):3}: " + ", ".join(f"{a['titulo']}[{'+'.join(a['cmds'])}]"
                                                   f"{'' if a.get('alcance') is None else ' a' + str(a['alcance'])}"
                                                   for a in v)[:400])


def main():
    args = sys.argv[1:]
    if "--mostrar" in args:
        args.remove("--mostrar")
        for n in args or LUTADORES:
            mostrar(n)
        return
    if "--tirar" in args:
        args.remove("--tirar")
        for n in args or LUTADORES:
            arq = RAIZ / "chars" / n / f"{n}.cns"
            b = arq.read_bytes().decode("utf-8")
            crlf = "\r\n" in b
            t = tirar(b.replace("\r\n", "\n"))
            arq.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
            print(f"{n}: IA tirada")
        return
    for n in args or LUTADORES:
        gav, acoes = aplicar(n)
        print(f"{n}: IA com {len(acoes)} escolhas (" + ", ".join(f"{k} {len(v)}" for k, v in gav.items()) + ")")


if __name__ == "__main__":
    main()
