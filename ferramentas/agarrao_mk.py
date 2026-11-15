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

VITIMA = (822, 825, 826, 827, 828, 829, 823, 824)  # estados do oponente que ficam no bloco do fim do .cns

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
    som = so.group(1).split(";")[0].strip() if so else "F5,0"
    return (sp.group(1).split(";")[0].strip() if sp else "9200"), som


# Ritmo da sequência (issue #45 do Breno: "os agarrões estão bem confusos"). Cada pancada é lida em três tempos:
# prepara (os quadros do golpe antes do contato, nunca menos que PREPARO ticks), bate (o quadro de contato segurado
# CONTATO ticks, com congelamento de CONGELA ticks, faísca no ponto do contato e o oponente reagindo) e volta para a
# pose de segurar (SEGURA ticks), para dar para ver uma pancada separada da outra. O finalizador prepara mais, congela
# mais, treme a tela e arremessa.
PEGA = 16        # ticks mostrando a pegada antes da 1ª pancada (cobre a janela de escape do 820, 7 ticks)
PREPARO = 6      # mínimo de ticks de preparo de cada pancada
PREPARO_FINAL = 10
CONTATO = 5      # ticks do quadro de contato (fora o congelamento)
SEGURA = 8       # ticks de volta na pose de segurar entre uma pancada e outra
CONGELA = 7      # hitstop de cada pancada (Pause): regra 8.3, fraco 7-8
CONGELA_FINAL = 14  # finalizador: 14+


def esticar(els, minimo):
    """Durações do preparo (quadros antes do contato), cada uma entre 2 e 5 ticks, e o último quadro segura o que
    faltar para chegar no mínimo (a pose de carga, regra 7.2: antecipação)."""
    durs = [max(2, min(5, e[1] if e[1] > 0 else 5)) for e in els]
    if durs and sum(durs) < minimo:
        durs[-1] += minimo - sum(durs)
    return durs


def montar(lutador, air, cns):
    r = ROTEIROS[lutador]
    tabela = acoes(air)
    # corpo em alta resolução ([Size] xscale 1/3): Clsn do .air em 3x e Explod em 1x (ferramentas/hd.py)
    escala = 3 if re.search(r"^\s*xscale\s*=\s*0\.33", cns, re.M) else 1
    if 800 not in tabela:
        raise SystemExit(f"{lutador}: sem ação 800 no .air")
    # pose de segurar: o quadro da tentativa de agarrão (ação 800) em que a mão alcança o oponente (tem Clsn1)
    pega_els = elementos(tabela[800])
    pega = next((e for e in pega_els if e[4]), pega_els[0])
    segurar = (pega[0], pega[2], pega[3])
    frente = max(pega[4][0], pega[4][2]) // escala if pega[4] else 40
    quadros = [(pega[0], PEGA, pega[2], pega[3])]
    t = PEGA
    contatos = []  # (tick, dano, faísca, som, x, y, final, alto)
    for k, g in enumerate(r.golpes + (r.final,)):
        final = k == len(r.golpes)
        if g.acao not in tabela:
            raise SystemExit(f"{lutador}: ação {g.acao} ({g.nome}) não existe no .air")
        els = elementos(tabela[g.acao])
        j0 = next((j for j, e in enumerate(els) if e[4]), None)
        if j0 is None:
            raise SystemExit(f"{lutador}: ação {g.acao} ({g.nome}) não tem caixa de acerto")
        _, som = hitdef(cns, g.acao)
        # faísca fixa: leve nas pancadas, média no final. A crítica (9205) estoura do tamanho dos dois corpos
        # e escondia a pancada (#45)
        base = 9201 if final else 9200
        faisca = (f"(ifelse(var(20) > 0, {base + 30}, {base}))" if base + 30 in tabela else str(base))
        for e, dur in zip(els[:j0], esticar(els[:j0], PREPARO_FINAL if final else PREPARO)):
            quadros.append((e[0], dur, e[2], e[3]))
            t += dur
        c = els[j0][4]
        x = max(18, min(34, max(c[0], c[2]) // escala - 8))
        y = (c[1] + c[3]) // 2 // escala
        contatos.append((t, g.dano, faisca, som, x, y, final, y < -60))
        if final:
            # o finalizador vai até o fim: contato e o embalo do golpe (recuperação) no tempo dele
            quadros.append((els[j0][0], CONTATO + 2, els[j0][2], els[j0][3]))
            t += CONTATO + 2
            for e in els[j0 + 1:]:
                dur = max(3, min(8, e[1] if e[1] > 0 else 10))
                quadros.append((e[0], dur, e[2], e[3]))
                t += dur
        else:
            quadros.append((els[j0][0], CONTATO, els[j0][2], els[j0][3]))
            t += CONTATO
            if j0 + 1 < len(els):  # um quadro do embalo, e volta a segurar
                e = els[j0 + 1]
                quadros.append((e[0], 3, e[2], e[3]))
                t += 3
            quadros.append((segurar[0], SEGURA, segurar[1], segurar[2]))
            t += SEGURA
    return r, quadros, contatos, frente


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


# reação do oponente preso a cada pancada: alta (5001/5002) ou baixa (5011/5012); a 5000 é a pose de preso
REACOES = ((822, 5001), (825, 5002), (826, 5002), (827, 5011), (828, 5012), (829, 5012))
PRESO = 5000  # ação do oponente (a DELE) segurada no 1º quadro enquanto está preso: o tranco de quem foi agarrado


def segura_pose(n):
    """Controladores que deixam o oponente preso parado na pose de quem foi agarrado (1º quadro do tranco dele)."""
    return ctl(n, "Preso: pose", "ChangeAnim", f"trigger1 = Anim != {PRESO} && AnimTime = 0",
               f"trigger2 = Anim = {PRESO} && AnimElemTime(2) >= 0", f"value = {PRESO}", "elem = 1")


def estados(r, contatos, frente, vitima_preso):
    """Statedef 810 (quem agarra), 820 (oponente preso) e os estados do oponente 822 a 829, 823/824."""
    fim = contatos[-1][0]
    primeiro = contatos[0][0]
    c = [f"[Statedef 810]\ntype = S\nmovetype = A\nphysics = N\nanim = 810\nvelset = 0,0\nctrl = 0\n"
         f"sprpriority = 2\n\n"]
    c.append(f"; {r.nome}: pega, segura, {len(contatos) - 1} pancadas e arremessa. Escape: y ou b no começo.\n")
    c.append(ctl(810, "Lado", "VarSet", "trigger1 = Time = 0", 'var(2) = command = "holdback"'))
    # colados: o oponente fica com a frente do corpo encostada na mão da pose de segurar
    c.append(ctl(810, "Segura", "TargetBind", f"trigger1 = Time < {fim}", "trigger1 = NumTarget",
                 f"pos = {r.bind}, 0"))
    c.append(ctl(810, "Escapou", "ChangeState", "trigger1 = Time > 1", f"trigger1 = Time < {primeiro}",
                 f"trigger1 = enemynear,stateno != {vitima_preso}", "value = 0", "ctrl = 1"))
    # se o oponente sumiu do agarrão por qualquer motivo, quem agarrou não fica preso no meio da sequência
    c.append(ctl(810, "Perdeu", "ChangeState", f"trigger1 = Time > {primeiro}", f"trigger1 = Time < {fim}",
                 "trigger1 = !NumTarget", "value = 0", "ctrl = 1"))
    for k, (t, dano, faisca, som, x, y, final, alto) in enumerate(contatos):
        nome = "Final" if final else f"Pancada {k + 1}"
        c.append(ctl(810, f"{nome}: dano", "TargetLifeAdd", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                     f"value = -{dano}"))
        c.append(ctl(810, f"{nome}: faísca", "Explod", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                     f"anim = {faisca}", "postype = p1", f"pos = {x}, {y}", "removetime = -2", "sprpriority = 5",
                     # faísca menor que a do HitDef: colada nos dois corpos, a grande escondia a pancada (#45)
                     f"scale = {'.6, .6' if final else '.75, .75'}", "ignorehitpause = 1", "pausemovetime = 99"))
        c.append(ctl(810, f"{nome}: som", "PlaySnd", f"trigger1 = Time = {t}", f"value = {som}"))
        if not final:  # o oponente recua um pouco no tranco (no final ele já sai voando)
            c.append(ctl(810, f"{nome}: tranco", "TargetBind", f"trigger1 = Time = [{t}, {t + 5}]",
                         "trigger1 = NumTarget", f"pos = {r.bind + 5}, 0"))
        c.append(ctl(810, f"{nome}: barra", "PowerAdd", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                     f"value = {dano // 2}"))
        reacao = REACOES[min(k, 2) + (0 if alto else 3)][0]
        if not final:
            c.append(ctl(810, f"{nome}: reage", "TargetState", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                         f"value = {reacao}"))
        # congelamento no contato (hitstop): os dois param e a faísca estoura; no final, mais longo e com tremida
        c.append(ctl(810, f"{nome}: congela", "Pause", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                     f"time = {CONGELA_FINAL if final else CONGELA}", "movetime = 0"))
        c.append(ctl(810, f"{nome}: treme", "EnvShake", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                     f"time = {16 if final else 6}", "freq = 150", f"ampl = {-5 if final else -2}"))
    c.append(ctl(810, "Joga para trás", "TargetState", f"trigger1 = Time = {fim}", "trigger1 = NumTarget",
                 "trigger1 = var(2)", "value = 824"))
    c.append(ctl(810, "Joga", "TargetState", f"trigger1 = Time = {fim}", "trigger1 = NumTarget",
                 "trigger1 = !var(2)", "value = 823"))
    # jogou para trás: o oponente passa por cima (824 sem empurrão) e quem agarrou vira para ele no fim
    c.append(ctl(810, "Vira", "Turn", f"trigger1 = Time = {fim + 10}", "trigger1 = var(2)"))
    c.append(ctl(810, "Fim", "ChangeState", "trigger1 = AnimTime = 0", "value = 0", "ctrl = 1"))
    # 820: o oponente agarrado fica EM PÉ, na pose dele de quem levou o tranco (antes ficava na pose de queda)
    v = [f"[Statedef {vitima_preso}]\ntype = S\nmovetype = H\nphysics = N\nvelset = 0,0\nctrl = 0\n\n",
         ctl(vitima_preso, "Pose", "ChangeAnim", "trigger1 = Time = 0", f"value = {PRESO}", "elem = 1"),
         segura_pose(vitima_preso),
         ctl(vitima_preso, "Escape", "SelfState", "triggerall = Time <= 7", 'trigger1 = command = "y"',
             'trigger2 = command = "b"', "value = 0", "ctrl = 1"),
         ctl(vitima_preso, "Solto", "SelfState", "trigger1 = Time > 0", "trigger1 = !gethitvar(isbound)",
             "value = 5050")]
    # oponente: pancada segurando (a reação de tomar golpe DELE, alta ou baixa) e volta para a pose de preso
    for n, anim in REACOES:
        v.append(f"[Statedef {n}]\ntype = S\nmovetype = H\nphysics = N\nvelset = 0,0\nctrl = 0\n\n")
        v.append(ctl(n, "Apanha", "ChangeAnim", "trigger1 = Time = 0", f"value = {anim}"))
        v.append(segura_pose(n).replace(f"Anim != {PRESO} && AnimTime = 0", f"Time > 0 && Anim = {anim} && AnimTime = 0"))
        v.append(ctl(n, "Solto", "SelfState", "trigger1 = Time > 0", "trigger1 = !gethitvar(isbound)",
                     "value = 5050"))
    for n, vel in ((823, "-4.2, -5.5"), (824, "4.6, -6.5")):
        v.append(f"[Statedef {n}]\ntype = A\nmovetype = H\nphysics = N\nvelset = {vel}\nctrl = 0\n\n")
        v.append(ctl(n, "Pose", "ChangeAnim", "trigger1 = Time = 0", "value = 5030"))
        if n == 824:
            v.append(ctl(n, "Passa por cima", "PlayerPush", "trigger1 = 1", "value = 0"))
        v.append(ctl(n, "Queda", "VelAdd", "trigger1 = 1", "y = .45"))
        v.append(ctl(n, "Chão", "SelfState", "trigger1 = Vel Y > 0", "trigger1 = Pos Y >= 0", "value = 5100"))
    return "".join(c), "".join(v)


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
        for n in VITIMA:
            assert f"[Statedef {n}]" not in cns, f"{lutador}: Statedef {n} fora do bloco do agarrão"
    else:
        for n in VITIMA:
            assert f"[Statedef {n}]" not in cns, f"{lutador}: Statedef {n} já existe no .cns (conflito)"
    r, quadros, contatos, frente = montar(lutador, air, cns)
    m = re.search(r"^\[Begin Action 810\][^\n]*\n.*?(?=^\[Begin Action|\Z)", air, re.M | re.S)
    air = air[:m.start()] + acao_810(quadros, r) + air[m.end():]
    agarra, vitima = estados(r, contatos, frente, 820)
    cns = trocar_statedef(cns, 810, agarra)
    corte = vitima.index("[Statedef 822]")
    cns = trocar_statedef(cns, 820, vitima[:corte])
    cns = cns.rstrip() + "\n\n" + MARCA + "\n\n" + vitima[corte:].rstrip() + "\n"
    return air, cns


def resumo(lutador, air, cns):
    r, quadros, contatos, _ = montar(lutador, air, cns)
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
