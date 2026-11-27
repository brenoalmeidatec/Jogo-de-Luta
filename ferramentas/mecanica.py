#!/usr/bin/env python3
"""Consertos de mecânica da auditoria do Breno (#32, 24/11/2026), aplicados em cima de chars/<l>/ sem regerar o lutador.

  python3 ferramentas/mecanica.py                 aplica nos 6 lutadores
  python3 ferramentas/mecanica.py pengaro ck      só nesses
  python3 ferramentas/mecanica.py --conferir      só diz o que falta (sai com erro se faltar algo)

Pode rodar quantas vezes quiser (o que ele põe tem a marca "mecanica 25/11" e é trocado, não duplicado). Os
gerar_<lutador>.py chamam `aplicar` no fim, para nada se perder quando o lutador for regerado.

O que muda (itens da auditoria):
  1. Afastar na defesa (y+b defendendo, estado 720) só sai com 1 barra e gasta a barra ao entrar no 720. Antes ele
     saía de graça sem barra (Pengaró, CK, Gutto, Raiclaven, Gbzin) e, no Hazak, a barra era gasta no [State -1]
     antes de o ChangeState conferir "power >= 1000": com 1 barra ele gastava e não afastava.
  4. "Jab, jab": no [State -1, Soco fraco] sai o "stateno = 200" da corrente, que nunca rodava (a Corrente x, logo
     antes, pega o x depois do soco fraco). Só onde a Corrente x vale nas duas formas (no Hazak ela é só da base e o
     Diabo usa o jab repetido).
  7. Vantagem na defesa: cada golpe ganha guard.hittime pela tabela ferramentas/mecanica_guarda.json, medida no motor
     com ferramentas/vantagem.py (sem guard.hittime o motor usava a trava curta do deslize, ~5 tiques, e TODO golpe
     ficava muito negativo defendido: o soco fraco a -9, os médios a -23).
  8. Desconto de dano em combo: 100% nos 2 primeiros acertos, 80% no 3º, 70%, 60% e piso de 50% (multiplica o
     AttackMulSet que já existia no [State -2], o do bônus do despertado).
 10. Parry: janela de 4 para 8 tiques (ReversalDef do 760 e do 764) e comando com 4 tiques para fechar e 3 de buffer.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LUTADORES = ("pengaro", "hazaki", "ck", "gutto", "raiclaven", "gbzin")
MARCA = "mecanica 25/11"
TABELA = Path(__file__).resolve().parent / "mecanica_guarda.json"

PARRY_JANELA = 8
PARRY_TIME, PARRY_BUFFER = 4, 3
# hc = acertos que o oponente já levou neste combo; o golpe sai com 1 - 0,1 x hc a partir do 3º acerto, piso de 50%
_HC = "(enemynear, gethitvar(hitcount))"
COMBO = f"ifelse((enemynear, movetype = H), ifelse({_HC} >= 5, .5, ifelse({_HC} >= 2, 1 - .1 * {_HC}, 1)), 1)"
# a super não sofre desconto: os acertos dela mesma não podem comer o dano dela. Super = 3000 a 3399 e todo estado
# com SuperPause (a Rajadona 1650 do Diabo Loiro gasta 1000 de barra; com desconto os 12 raios caíam de 250 para 225)
SUPER = "stateno = [3000, 3399]"


def _supers(cns):
    extra = [n for ini, fim, n in _blocos(cns)
             if not 3000 <= n <= 3399 and re.search(r"(?mi)^type\s*=\s*SuperPause\s*$", cns[ini:fim])]
    return " || ".join([SUPER] + [f"stateno = {n}" for n in extra])


def _blocos(txt):
    """[(início, fim, número)] de cada [Statedef N]."""
    marcas = [(m.start(), int(m.group(1))) for m in re.finditer(r"(?m)^\[Statedef (-?\d+)\]", txt)]
    return [(ini, marcas[k + 1][0] if k + 1 < len(marcas) else len(txt), n) for k, (ini, n) in enumerate(marcas)]


def afastar(cmd, cns):
    # cmd: o PowerAdd do [State -1] sai (gastava antes de conferir); o ChangeState passa a exigir a barra
    cmd = re.sub(r"(?ms)^\[State -1, Gasta afastar de defesa\]\n.*?\n\n", "", cmd)
    m = re.search(r"(?ms)^\[State -1, Afastar de defesa\]\n(.*?)\n\n", cmd)
    if m and "power >= 1000" not in m.group(1):
        novo = m.group(0).replace('triggerall = command = "afastar"\n',
                                  'triggerall = command = "afastar"\ntriggerall = power >= 1000\n', 1)
        cmd = cmd.replace(m.group(0), novo, 1)
    # cns: gasta ao entrar no 720
    ctl = f"[State 720, Gasta a barra ({MARCA})]\ntype = PowerAdd\ntrigger1 = Time = 0\nvalue = -1000\n\n"
    cns = re.sub(rf"(?ms)^\[State 720, Gasta a barra \({re.escape(MARCA)}\)\]\n.*?\n\n", "", cns)
    m = re.search(r"(?ms)^\[Statedef 720\]\n.*?\n\n", cns)
    if m:
        cns = cns[:m.end()] + ctl + cns[m.end():]
    return cmd, cns


def jab(cmd):
    cx = re.search(r"(?ms)^\[State -1, Corrente x: 2o\]\n(.*?)\n\n", cmd)
    if not cx or "var(20)" in cx.group(1) or not re.search(r"(?m)^trigger1 = \(?stateno = 200\)? && movecontact", cx.group(1)):
        return cmd
    m = re.search(r"(?ms)^\[State -1, Soco fraco\]\n(.*?)\n\n", cmd)
    if not m:
        return cmd
    novo = m.group(0).replace("(stateno = 200 || stateno = 400", "(stateno = 400", 1)
    return cmd.replace(m.group(0), novo, 1)


def parry(cmd, cns):
    for nome in ("parry", "parry_baixo"):
        cmd = re.sub(rf'(?m)(^name = "{nome}"\ncommand = [^\n]+\n)time = \d+\nbuffer\.time = \d+',
                     rf"\g<1>time = {PARRY_TIME}\nbuffer.time = {PARRY_BUFFER}", cmd)
    for ini, fim, n in reversed(_blocos(cns)):
        if n in (760, 764):
            b = re.sub(r"(?m)(type = ReversalDef\ntrigger1 = )Time < \d+", rf"\g<1>Time < {PARRY_JANELA}", cns[ini:fim])
            cns = cns[:ini] + b + cns[fim:]
    return cmd, cns


def combo(cns):
    cond = f"ifelse({_supers(cns)}, 1, {COMBO})"

    def troca(m):
        valor = m.group(2)
        if MARCA in m.group(0):
            # versão de antes: tira o desconto antigo e refaz (a lista de supers pode ter mudado)
            valor = valor.split(") * ifelse(", 1)[0][1:]
        return f"{m.group(1)}value = ({valor}) * {cond} ; desconto de combo ({MARCA})\n"
    return re.sub(r"(?m)^(\[State -2, [^\]]*\]\ntype = AttackMulSet\ntrigger1 = 1\n)value = ([^;\n]*?)\s*(;[^\n]*)?\n",
                  troca, cns)


def guarda(lutador, cns, tabela):
    valores = tabela.get(lutador, {})
    for ini, fim, n in reversed(_blocos(cns)):
        if str(n) not in valores:
            continue
        g = int(valores[str(n)])
        b = cns[ini:fim]
        b = re.sub(rf"(?m)^guard\.hittime = -?\d+ ; {re.escape(MARCA)}\n", "", b)
        b = re.sub(r"(?m)^(ground\.hittime\s*=\s*[^\n]*\n)", rf"\g<1>guard.hittime = {g} ; {MARCA}\n", b)
        cns = cns[:ini] + b + cns[fim:]
    return cns


def aplicar(lutador, pasta=None):
    pasta = Path(pasta) if pasta else RAIZ / "chars" / lutador
    pc, pn = pasta / f"{lutador}.cmd", pasta / f"{lutador}.cns"
    cmd_bruto, cns_bruto = pc.read_text(encoding="utf-8"), pn.read_text(encoding="utf-8")
    fim_cmd = "\r\n" if b"\r\n" in pc.read_bytes() else "\n"  # o .cmd é -text no .gitattributes: alguns são CRLF
    fim_cns = "\r\n" if b"\r\n" in pn.read_bytes() else "\n"
    cmd, cns = cmd_bruto.replace("\r\n", "\n"), cns_bruto.replace("\r\n", "\n")
    tabela = json.loads(TABELA.read_text(encoding="utf-8")) if TABELA.exists() else {}
    cmd, cns = afastar(cmd, cns)
    cmd = jab(cmd)
    cmd, cns = parry(cmd, cns)
    cns = combo(cns)
    cns = guarda(lutador, cns, tabela)
    pc.write_text(cmd, encoding="utf-8", newline=fim_cmd)
    pn.write_text(cns, encoding="utf-8", newline=fim_cns)


def conferir(lutador):
    pasta = RAIZ / "chars" / lutador
    cmd = (pasta / f"{lutador}.cmd").read_text(encoding="utf-8")
    cns = (pasta / f"{lutador}.cns").read_text(encoding="utf-8")
    falta = []
    if "Gasta afastar de defesa" in cmd:
        falta.append("afastar: PowerAdd no [State -1]")
    m = re.search(r"(?ms)^\[State -1, Afastar de defesa\]\n(.*?)\n\n", cmd)
    if m and "power >= 1000" not in m.group(1):
        falta.append("afastar: sem conferir a barra")
    if f"Gasta a barra ({MARCA})" not in cns:
        falta.append("afastar: 720 não gasta a barra")
    if re.search(r"(?m)type = ReversalDef\ntrigger1 = Time < 4\b", cns):
        falta.append("parry: janela de 4")
    if f"desconto de combo ({MARCA})" not in cns:
        falta.append("combo: sem desconto")
    tab = json.loads(TABELA.read_text(encoding="utf-8")).get(lutador, {}) if TABELA.exists() else {}
    if tab and cns.count(f"; {MARCA}\n") < len(tab):
        falta.append("guarda: tabela não aplicada")
    return falta


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    lutadores = args or LUTADORES
    if "--conferir" in sys.argv:
        erro = False
        for l in lutadores:
            f = conferir(l)
            print(f"{l}: {'ok' if not f else '; '.join(f)}")
            erro |= bool(f)
        sys.exit(1 if erro else 0)
    for l in lutadores:
        aplicar(l)
        print(f"{l}: aplicado")


if __name__ == "__main__":
    main()
