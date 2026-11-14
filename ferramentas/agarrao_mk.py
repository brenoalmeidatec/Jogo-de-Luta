#!/usr/bin/env python3
"""Agarrão em pé no estilo dos jogos de luta clássicos (pedido do Breno, missão 2026-11-14, item 3).

O lutador pega, SEGURA o oponente e bate nele várias vezes (cada pancada com dano, faísca, som e o oponente
reagindo), e no fim arremessa. Vale para todos os lutadores: o roteiro de cada um (abaixo, em ROTEIROS) diz quais
golpes ele dá, no jeito dele (boxe sujo do CK, clinch de Muay Thai do Gutto, capoeira e garrafa do Pengaró...).

Como funciona, sem desenho novo: a ação 810 do .air é montada com os quadros dos golpes que o lutador já tem
(pega -> golpe 1 -> golpe 2 -> ... -> finalizador). Cada contato cai no tick em que o golpe emprestado tem a caixa de
acerto (Clsn1), então o soco encosta no oponente no quadro certo. As caixas de acerto saem (o 810 não tem HitDef) e a
caixa de corpo de cada quadro fica explícita. Como só usa sprites que o .sff já tem, o .sff não muda, e o
RemapPreset do Despertar troca os desenhos sozinho.

Estados (no .cns do lutador):
  800       pega (HitDef de agarrão, igual a antes) -> 810 nele, 820 no oponente
  810       segura (TargetBind) e bate; o escape continua o de antes (y ou b nos 7 primeiros ticks do 820)
  820       oponente preso (fica como estava em cada lutador: pose e escape)
  822/825/826  oponente levando a pancada, preso: ChangeAnim (a ação 5000/5001/5002 DELE, do .air dele, que todo
            lutador tem; o ChangeAnim2 usaria a do agarrador)
  823/824   oponente arremessado para longe (823) ou por cima, para trás de quem agarrou (824, segurando ←);
            cai no 5100 como o arremesso antigo

Uso: python ferramentas/agarrao_mk.py [lutador ...]   (sem nome: todos) reescreve chars/<l>/<l>.air e .cns.
Os geradores (gerar_*.py) também chamam `aplicar` no fim, então regenerar o lutador mantém o agarrão.
É idempotente: rodar de novo dá o mesmo arquivo.
"""
import re
import sys
from dataclasses import dataclass
from pathlib import Path

CHARS = Path(__file__).resolve().parent.parent / "chars"
MARCA = "; ---- agarrão segura-e-bate (ferramentas/agarrao_mk.py) ----"


@dataclass(frozen=True)
class Golpe:
    acao: int      # ação/estado emprestado (os quadros e a faísca/som do HitDef dele)
    dano: int      # dano total do golpe (dividido entre os contatos dele)
    nome: str


@dataclass(frozen=True)
class Roteiro:
    nome: str
    golpes: tuple  # pancadas segurando
    final: Golpe   # o que solta o oponente
    pega: int = 10  # ticks segurando antes da 1ª pancada (cobre a janela de escape do 820)
    bind: int = 34  # distância em que o oponente fica preso


# Dano total perto de 120 (o antigo era 100 em uma pancada): é o agarrão mais longo e não pode ser defendido.
ROTEIROS = {
    "ck": Roteiro("Gola na Mão: boxe sujo", (
        Golpe(301, 24, "jab duplo"), Golpe(312, 22, "gancho no fígado"), Golpe(322, 22, "joelhada na coxa"),
    ), Golpe(313, 52, "uppercut 'Levanta, Comédia'")),
    "gutto": Roteiro("Clinch de Muay Thai", (
        Golpe(303, 22, "joelhada"), Golpe(347, 22, "joelhada subindo"), Golpe(303, 22, "joelhada"),
    ), Golpe(240, 54, "chute alto")),
    "pengaro": Roteiro("Roda de Capoeira com Garrafa", (
        Golpe(321, 20, "chute baixo"), Golpe(303, 24, "garrafada"), Golpe(313, 22, "meia-lua"),
    ), Golpe(333, 54, "aú com garrafa")),
    "raiclaven": Roteiro("Corte de Cabelo à Força", (
        Golpe(301, 22, "tesourada"), Golpe(302, 22, "tesourada de lado"), Golpe(343, 22, "corte de cima"),
    ), Golpe(313, 54, "chute giratório")),
    "hazaki": Roteiro("Abraço de Quebrada", (
        Golpe(301, 22, "soco"), Golpe(302, 22, "cutucão"), Golpe(347, 22, "joelhada"),
    ), Golpe(333, 54, "chute alto"), bind=30),
}

RE_ACAO = re.compile(r"^\[Begin Action (\d+)\][^\n]*\n(.*?)(?=^\[Begin Action|\Z)", re.M | re.S | re.I)
RE_ELEM = re.compile(r"^\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)(.*)$")
RE_BOX = re.compile(r"=\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)")


def acoes(air):
    return {int(m.group(1)): m.group(2) for m in RE_ACAO.finditer(air)}


def elementos(corpo):
    """[(linha do elemento sem a duração, duração, [linhas Clsn2], caixa Clsn1 ou None)] com a caixa de corpo
    explícita (Clsn2Default resolvido) e o Clsn1 do quadro."""
    out, padrao2, padrao1, atual2, atual1, modo = [], [], None, None, None, None
    for ln in corpo.splitlines():
        s = ln.strip()
        if not s or s.startswith(";") or s.lower().startswith("loopstart"):
            continue
        cab = re.match(r"(clsn[12])(default)?\s*:\s*(\d+)", s, re.I)
        if cab:
            modo = (cab.group(1).lower(), bool(cab.group(2)))
            if modo == ("clsn2", True):
                padrao2 = []
            elif modo == ("clsn2", False):
                atual2 = []
            elif modo == ("clsn1", True):
                padrao1 = []
            else:
                atual1 = []
            continue
        if re.match(r"clsn[12]\s*\[", s, re.I):
            alvo = {("clsn2", True): padrao2, ("clsn2", False): atual2,
                    ("clsn1", True): padrao1, ("clsn1", False): atual1}[modo]
            alvo.append(s)
            continue
        e = RE_ELEM.match(ln)
        if e:
            g, i, x, y, t, resto = e.groups()
            caixas2 = atual2 if atual2 is not None else padrao2
            caixas1 = atual1 if atual1 is not None else padrao1
            caixa1 = None
            if caixas1:
                bs = [tuple(int(v) for v in RE_BOX.search(b).groups()) for b in caixas1]
                caixa1 = (min(min(b[0], b[2]) for b in bs), min(min(b[1], b[3]) for b in bs),
                          max(max(b[0], b[2]) for b in bs), max(max(b[1], b[3]) for b in bs))
            out.append((f"{g},{i}, {x},{y}, ", int(t), resto, list(caixas2 or []), caixa1))
            atual2 = atual1 = None
    return out


def hitdef(cns, n):
    """(anim da faísca, som) do HitDef do estado n ('[State n, Golpe]' ou o primeiro HitDef)."""
    m = re.search(rf"^\[Statedef {n}\]\n(.*?)(?=^\[Statedef|\Z)", cns, re.M | re.S | re.I)
    corpo = m.group(1) if m else ""
    sp = re.search(r"^\s*sparkno\s*=\s*S\s*(.+?)\s*$", corpo, re.M | re.I)
    so = re.search(r"^\s*hitsound\s*=\s*(.+?)\s*$", corpo, re.M | re.I)
    return (sp.group(1) if sp else "9200"), (so.group(1) if so else "F5,0")


def montar(lutador, air, cns):
    r = ROTEIROS[lutador]
    tabela = acoes(air)
    # corpo em alta resolução ([Size] xscale 1/3): Clsn do .air em 3x e Explod em 1x (ferramentas/hd.py)
    escala = 3 if re.search(r"^\s*xscale\s*=\s*0\.33", cns, re.M) else 1
    if 810 not in tabela:
        raise SystemExit(f"{lutador}: sem ação 810 no .air")
    pega = elementos(tabela[810])[0]
    quadros = [(pega[0], r.pega, pega[2], pega[3])]
    t = r.pega
    contatos = []  # (tick, dano, faísca, som, x, y, final)
    for k, g in enumerate(r.golpes + (r.final,)):
        final = k == len(r.golpes)
        if g.acao not in tabela:
            raise SystemExit(f"{lutador}: ação {g.acao} ({g.nome}) não existe no .air")
        els = elementos(tabela[g.acao])
        ativos = [j for j, e in enumerate(els) if e[4] and (j == 0 or not els[j - 1][4])]
        if not ativos:
            raise SystemExit(f"{lutador}: ação {g.acao} ({g.nome}) não tem caixa de acerto")
        ultimo_ativo = max(j for j, e in enumerate(els) if e[4])
        # pancada segurando: corta a recuperação (só um quadro depois do contato); o finalizador vai inteiro
        fim = len(els) if final else min(len(els), ultimo_ativo + 2)
        faisca, som = hitdef(cns, g.acao)
        partes = [g.dano // len(ativos)] * len(ativos)
        partes[-1] += g.dano - sum(partes)
        for j, e in enumerate(els[:fim]):
            dur = e[1]
            if dur < 0:
                dur = 10
            if not final:
                dur = max(2, min(dur, 5))
            if j in ativos:
                c = e[4]
                x = max(18, min(30, max(c[0], c[2]) // escala - 8))
                y = (c[1] + c[3]) // 2 // escala
                contatos.append((t, partes[ativos.index(j)], faisca, som, x, y,
                                 final and j == ativos[-1]))
            quadros.append((e[0], dur, e[2], e[3]))
            t += dur
    return r, quadros, contatos


def acao_810(quadros, r):
    linhas = [f"[Begin Action 810]", f"; {r.nome} (ferramentas/agarrao_mk.py)"]
    for ini, dur, resto, caixas2 in quadros:
        if caixas2:
            linhas.append(f"Clsn2: {len(caixas2)}")
            linhas += [" " + re.sub(r"^Clsn2\s*\[\s*(\d+)\s*\]", r"Clsn2[\1]", b, flags=re.I) for b in caixas2]
        linhas.append(f"{ini}{dur}{resto}")
    return "\n".join(linhas) + "\n\n"


def ctl(n, nome, tipo, *linhas):
    return f"[State {n}, {nome}]\ntype = {tipo}\n" + "".join(l + "\n" for l in linhas) + "\n"


def estados(r, contatos, vitima_preso):
    """Statedef 810 (quem agarra) e os estados do oponente 822 a 826."""
    fim = contatos[-1][0]
    primeiro = contatos[0][0]
    reacoes = (822, 825, 826)
    c = [f"[Statedef 810]\ntype = S\nmovetype = A\nphysics = N\nanim = 810\nvelset = 0,0\nctrl = 0\n"
         f"sprpriority = 2\n\n"]
    c.append(f"; {r.nome}: pega, segura, {len(contatos) - 1} pancadas e arremessa. Escape: y ou b no começo.\n")
    c.append(ctl(810, "Lado", "VarSet", "trigger1 = Time = 0", 'var(2) = command = "holdback"'))
    c.append(ctl(810, "Segura", "TargetBind", f"trigger1 = Time < {fim}", "trigger1 = NumTarget",
                 f"pos = {r.bind}, 0"))
    c.append(ctl(810, "Escapou", "ChangeState", "trigger1 = Time > 1", f"trigger1 = Time < {primeiro}",
                 f"trigger1 = enemynear,stateno != {vitima_preso}", "value = 0", "ctrl = 1"))
    # se o oponente sumiu do agarrão por qualquer motivo, quem agarrou não fica preso no meio da sequência
    c.append(ctl(810, "Perdeu", "ChangeState", f"trigger1 = Time > {primeiro}", f"trigger1 = Time < {fim}",
                 "trigger1 = !NumTarget", "value = 0", "ctrl = 1"))
    for k, (t, dano, faisca, som, x, y, final) in enumerate(contatos):
        nome = "Final" if final else f"Pancada {k + 1}"
        c.append(ctl(810, f"{nome}: dano", "TargetLifeAdd", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                     f"value = -{dano}"))
        c.append(ctl(810, f"{nome}: faísca", "Explod", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                     f"anim = {faisca}", "postype = p1", f"pos = {x}, {y}", "removetime = -2", "sprpriority = 5",
                     "ownpal = 1"))
        c.append(ctl(810, f"{nome}: som", "PlaySnd", f"trigger1 = Time = {t}", f"value = {som}"))
        c.append(ctl(810, f"{nome}: barra", "PowerAdd", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                     f"value = {dano // 2}"))
        if not final:
            c.append(ctl(810, f"{nome}: reage", "TargetState", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                         f"value = {reacoes[min(k, 2)]}"))
    c.append(ctl(810, "Final: treme", "EnvShake", f"trigger1 = Time = {fim}", "time = 10", "freq = 150",
                 "ampl = -4"))
    c.append(ctl(810, "Joga para trás", "TargetState", f"trigger1 = Time = {fim}", "trigger1 = NumTarget",
                 "trigger1 = var(2)", "value = 824"))
    c.append(ctl(810, "Joga", "TargetState", f"trigger1 = Time = {fim}", "trigger1 = NumTarget",
                 "trigger1 = !var(2)", "value = 823"))
    # jogou para trás: o oponente passa por cima (824 sem empurrão) e quem agarrou vira para ele no fim
    c.append(ctl(810, "Vira", "Turn", f"trigger1 = Time = {fim + 10}", "trigger1 = var(2)"))
    c.append(ctl(810, "Fim", "ChangeState", "trigger1 = AnimTime = 0", "value = 0", "ctrl = 1"))
    # oponente: pancada segurando (a reação de tomar golpe DELE) e arremessado
    for n, anim in zip(reacoes, (5000, 5001, 5002)):
        c.append(f"[Statedef {n}]\ntype = S\nmovetype = H\nphysics = N\nvelset = 0,0\nctrl = 0\n\n")
        c.append(ctl(n, "Apanha", "ChangeAnim", "trigger1 = Time = 0", f"value = {anim}"))
        c.append(ctl(n, "Solto", "SelfState", "trigger1 = Time > 0", "trigger1 = !gethitvar(isbound)",
                     "value = 5050"))
    for n, vel in ((823, "-4.2, -5.5"), (824, "4.6, -6.5")):
        c.append(f"[Statedef {n}]\ntype = A\nmovetype = H\nphysics = N\nvelset = {vel}\nctrl = 0\n\n")
        c.append(ctl(n, "Pose", "ChangeAnim", "trigger1 = Time = 0", "value = 5030"))
        if n == 824:
            c.append(ctl(n, "Passa por cima", "PlayerPush", "trigger1 = 1", "value = 0"))
        c.append(ctl(n, "Queda", "VelAdd", "trigger1 = 1", "y = .45"))
        c.append(ctl(n, "Chão", "SelfState", "trigger1 = Vel Y > 0", "trigger1 = Pos Y >= 0", "value = 5100"))
    return "".join(c)


def trocar_statedef(cns, n, novo):
    m = re.search(rf"^\[Statedef {n}\]\n.*?(?=^\[Statedef|\Z)", cns, re.M | re.S)
    if not m:
        raise SystemExit(f"sem [Statedef {n}] no .cns")
    return cns[:m.start()] + novo + cns[m.end():]


def aplicar(lutador, air, cns):
    """Devolve (air, cns) com o agarrão segura-e-bate. Idempotente."""
    # tira o que uma aplicação anterior pôs (estados do oponente no fim do .cns)
    if MARCA in cns:
        cns = cns[:cns.index(MARCA)].rstrip() + "\n"
        for n in (822, 825, 826, 823, 824):
            assert f"[Statedef {n}]" not in cns, f"{lutador}: Statedef {n} fora do bloco do agarrão"
    else:
        for n in (822, 825, 826, 823, 824):
            assert f"[Statedef {n}]" not in cns, f"{lutador}: Statedef {n} já existe no .cns (conflito)"
    r, quadros, contatos = montar(lutador, air, cns)
    m = re.search(r"^\[Begin Action 810\][^\n]*\n.*?(?=^\[Begin Action|\Z)", air, re.M | re.S)
    air = air[:m.start()] + acao_810(quadros, r) + air[m.end():]
    texto = estados(r, contatos, 820)
    corte = texto.index("[Statedef 822]")
    cns = trocar_statedef(cns, 810, texto[:corte])
    cns = cns.rstrip() + "\n\n" + MARCA + "\n\n" + texto[corte:].rstrip() + "\n"
    return air, cns


def resumo(lutador, air, cns):
    r, quadros, contatos = montar(lutador, air, cns)
    total = sum(q[1] for q in quadros)
    return (f"{lutador}: {r.nome} | {len(contatos) - 1} pancadas + final em {contatos[-1][0]} ticks, "
            f"animação {total} ticks, dano {sum(c[1] for c in contatos)} | contatos "
            + " ".join(f"{c[0]}:{c[1]}" for c in contatos))


def main():
    nomes = sys.argv[1:] or list(ROTEIROS)
    for l in nomes:
        pa, pc = CHARS / l / f"{l}.air", CHARS / l / f"{l}.cns"
        air, cns = pa.read_text(encoding="utf-8"), pc.read_text(encoding="utf-8")
        air2, cns2 = aplicar(l, air, cns)
        pa.write_text(air2, encoding="utf-8", newline="\n")
        pc.write_text(cns2, encoding="utf-8", newline="\n")
        print(resumo(l, air2, cns2))


if __name__ == "__main__":
    main()
