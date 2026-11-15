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

VITIMA = (822, 825, 826, 827, 828, 829, 823, 824, 835)  # estados do oponente que ficam no bloco do fim do .cns


# ---------------------------------------------------------------- agarrões com animação própria (#45, 2026-11-15)
# Pedido do Breno: cada agarrão (em pé, agachado e de comando) com folha própria de quem agarra (pegada, cada pancada
# e o arremesso), e quem é agarrado reagindo com desenhos próprios (preso, apanhando alto e baixo, arremessado, caindo).
# Enquanto um lutador não tem a folha de um agarrão, ele fica como estava (o em pé, com os golpes emprestados acima).
@dataclass(frozen=True)
class Batida:
    prep: tuple       # desenhos do preparo (índices na folha do agarrão), na ordem
    bate: int         # desenho do contato
    dano: int
    alto: bool = True  # a pancada pega em cima (cabeça, peito) ou embaixo (barriga, perna): escolhe a reação do oponente
    som: str = "F5,0"


@dataclass(frozen=True)
class Proprio:
    nome: str
    segura: int       # desenho da pegada (ele segurando o oponente); volta a ele entre as pancadas
    batidas: tuple    # pancadas segurando
    final: Batida     # o golpe que solta
    solta: tuple = ()   # desenhos depois do golpe que solta (o embalo e a volta)
    alcanca: tuple = ()  # desenhos da tentativa (ação 800/840/830); vazio = a tentativa fica com os desenhos de hoje
    bind: int = 34
    fim: str = "joga"   # "joga": para longe, ou por cima segurando ←; "por_cima": o desenho é de arremesso por cima
    #                     do ombro (vai para trás dele; segurando ←, ele vira antes); "derruba": cai no lugar
    entre: int = 8      # ticks de volta na pose de segurar entre uma pancada e outra (menos = porrada mais seguida)


# tipo -> (estado da tentativa, estado de quem agarrou). O oponente fica sempre no 820.
TIPOS = {"pe": (800, 810), "baixo": (840, 841), "comando": (830, 831)}


def padrao(nome, danos=(22, 22, 22, 54), altos=(True, False, True), fim="joga", bind=34, som="F5,0"):
    """Roteiro da folha padrão de agarrão (8 desenhos numa fileira, docs/agarroes-proprios.md):
    1 alcança, 2 segura, 3 prepara a pancada A, 4 bate A, 5 prepara a pancada B, 6 bate B, 7 prepara o arremesso,
    8 arremessa. A sequência é A, B, A e o arremesso."""
    a, b, c = (Batida((2,), 3, danos[0], altos[0], som), Batida((4,), 5, danos[1], altos[1], som),
               Batida((2,), 3, danos[2], altos[2], som))
    return Proprio(nome, 1, (a, b, c), Batida((6,), 7, danos[3], True, som), alcanca=(0, 1), bind=bind, fim=fim)


# Hazak: desenhos de golpes dele que entram nos agarrões depois dos 8 da folha do agarrão (índices 8 em diante). O
# Breno não gostou dos agarrões dele na #45 (2026-11-15): pediu "sequência de porrada", várias pancadas seguidas e
# bem visíveis, cada uma com impacto, antes do final. Só desenhos que já estão no .sff do jogo (o 0 de várias folhas
# foi podado).
HAZAK_EXTRAS = {
    "pe": (("jab_duplo", 1), ("jab_duplo", 2), ("jab_duplo", 4), ("jab_duplo", 5), ("cruzado", 2), ("cruzado", 5),
           ("cotovelada", 2), ("cotovelada", 5), ("soco_reto", 2), ("soco_reto", 4)),
    "baixo": (("baixo_soco", 2), ("baixo_soco", 3), ("baixo_soco", 4), ("cotovelada", 2), ("cotovelada", 5)),
    "comando": (("tapa_costas", 3), ("tapa_costas", 5), ("jab_duplo", 1), ("jab_duplo", 2), ("cruzado", 2),
                ("cruzado", 5)),
}

PROPRIOS = {
    "hazaki": {
        # abraça (1), e com ele preso: jab, jab, cruzado, cotovelada e soco no estômago; gira levantando (4) e joga
        # por cima do ombro (5); 6 e 7 são a volta. Extras: 8/9 e 10/11 jab, 12/13 cruzado, 14/15 cotovelada,
        # 16/17 soco reto
        "pe": Proprio("Abraço de Quebrada", 1, (Batida((8,), 9, 14), Batida((10,), 11, 14), Batida((12,), 13, 18),
                                                 Batida((14,), 15, 18), Batida((16,), 17, 18, False)),
                      Batida((4,), 5, 50), solta=(6, 7), bind=30, fim="por_cima", entre=5),
        # agacha e pega o tornozelo (2): soco baixo, soco baixo, cotovelada de cima e o puxão (3); levanta a perna
        # dele até derrubar (4); 5 e 6 são a volta. Extras: 8 preparo e 9/10 soco baixo, 11/12 cotovelada
        "baixo": Proprio("Puxa a Perna", 2, (Batida((8,), 9, 16, False), Batida((8,), 10, 16, False),
                                            Batida((11,), 12, 18), Batida((2,), 3, 20, False)),
                         Batida((3,), 4, 60, False), solta=(5, 6), fim="derruba", entre=5),
        # prende pelo pescoço (1): dois cutucões nas costelas, tapa, jab e cruzado; empurra (6); 7 é a piada.
        # Extras: 8/9 tapa, 10/11 jab, 12/13 cruzado
        "comando": Proprio("Cutucão Sacana", 1, (Batida((2,), 3, 14, False), Batida((4,), 5, 14, False),
                                                  Batida((8,), 9, 18), Batida((10,), 11, 18), Batida((12,), 13, 20)),
                           Batida((5,), 6, 64), solta=(7,), bind=30, fim="derruba", entre=5),
    },
}

# Reação própria de quem é agarrado: ações do .air DELE (o oponente), usadas quando existem (SelfAnimExist); sem
# elas, vale a reação de tomar golpe de sempre (5000/5001/5011/5030).
V_PRESO, V_ALTO, V_BAIXO, V_SOBE, V_CAI = 5940, 5941, 5942, 5943, 5944
RE_DESENHOS = re.compile(r"^; desenhos do agarrão (\w+) = (.+)$", re.M)

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


def montar_proprio(p, refs, caixas2):
    """(quadros, contatos) do agarrão com desenhos próprios, no mesmo formato do `montar`. refs = "grupo,índice" de
    cada desenho da folha; caixas2 = caixa de corpo usada em todos os quadros (a da pose de agarrar)."""
    q = lambda i, dur: (f"{refs[i]}, 0,0, ", dur, "", caixas2)
    quadros, t, contatos = [q(p.segura, PEGA)], PEGA, []
    for k, b in enumerate(p.batidas + (p.final,)):
        final = k == len(p.batidas)
        minimo = PREPARO_FINAL if final else PREPARO
        cada = max(3, minimo // len(b.prep))
        durs = [cada] * len(b.prep)
        durs[-1] += max(0, minimo - sum(durs))
        for i, dur in zip(b.prep, durs):
            quadros.append(q(i, dur))
            t += dur
        base = 9201 if final else 9200
        faisca = f"(ifelse(var(20) > 0, {base + 30}, {base}))"
        y = -74 if b.alto else -44
        contatos.append((t, b.dano, faisca, b.som, p.bind - 8, y, final, b.alto))
        if final:
            quadros.append(q(b.bate, CONTATO + 5))
            t += CONTATO + 5
            for j, i in enumerate(p.solta):
                dur = 12 if j == len(p.solta) - 1 else 6
                quadros.append(q(i, dur))
                t += dur
        else:
            quadros += [q(b.bate, CONTATO + 1), q(p.segura, p.entre)]
            t += CONTATO + 1 + p.entre
    return quadros, contatos


def acao_810(quadros, r, numero=810):
    linhas = [f"[Begin Action {numero}]", f"; {r.nome} (ferramentas/agarrao_mk.py)"]
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
    """Controladores que deixam o oponente preso parado na pose de quem foi agarrado: a própria (V_PRESO) se ele
    tem, senão o 1º quadro do tranco dele."""
    return (ctl(n, "Preso: pose", "ChangeAnim", f"triggerall = !SelfAnimExist({V_PRESO})",
                f"trigger1 = Anim != {PRESO} && AnimTime = 0",
                f"trigger2 = Anim = {PRESO} && AnimElemTime(2) >= 0", f"value = {PRESO}", "elem = 1")
            + ctl(n, "Preso: pose própria", "ChangeAnim", f"triggerall = SelfAnimExist({V_PRESO})",
                  f"trigger1 = Anim != {V_PRESO} && AnimTime = 0", f"value = {V_PRESO}"))


def pose(n, nome, quando, propria, comum, elem=None):
    """ChangeAnim para a ação própria do oponente se ele tem, senão para a comum."""
    extra = (f"elem = {elem}",) if elem else ()
    return (ctl(n, nome, "ChangeAnim", f"trigger1 = {quando}", f"trigger1 = SelfAnimExist({propria})",
                f"value = {propria}")
            + ctl(n, nome, "ChangeAnim", f"trigger1 = {quando}", f"trigger1 = !SelfAnimExist({propria})",
                  f"value = {comum}", *extra))


def estados(r, contatos, frente, vitima_preso, fim_tipo="joga"):
    """Statedef 810 (quem agarra), 820 (oponente preso) e os estados do oponente 822 a 829, 823/824 e 835."""
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
        reacao = REACOES[k % 3 + (0 if alto else 3)][0]  # varia a reação a cada pancada
        if not final:
            c.append(ctl(810, f"{nome}: reage", "TargetState", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                         f"value = {reacao}"))
        # congelamento no contato (hitstop): os dois param e a faísca estoura; no final, mais longo e com tremida
        c.append(ctl(810, f"{nome}: congela", "Pause", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                     f"time = {CONGELA_FINAL if final else CONGELA}", "movetime = 0"))
        c.append(ctl(810, f"{nome}: treme", "EnvShake", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                     f"time = {16 if final else 6}", "freq = 150", f"ampl = {-5 if final else -2}"))
    if fim_tipo == "derruba":  # cai no lugar, na frente de quem agarrou
        c.append(ctl(810, "Derruba", "TargetState", f"trigger1 = Time = {fim}", "trigger1 = NumTarget",
                     "value = 835"))
    elif fim_tipo == "por_cima":
        # o desenho é de arremesso por cima do ombro, que cai atrás dele: segurando ← é isso (824). Para a frente, ele
        # vira antes de jogar, o oponente passa por cima e cai do lado em que estava (823), e ele vira de volta
        c.append(ctl(810, "Vira antes", "Turn", f"trigger1 = Time = {fim}", "trigger1 = !var(2)"))
        c.append(ctl(810, "Joga para a frente", "TargetState", f"trigger1 = Time = {fim}",
                     "trigger1 = NumTarget", "trigger1 = !var(2)", "value = 823"))
        c.append(ctl(810, "Joga por cima", "TargetState", f"trigger1 = Time = {fim}", "trigger1 = NumTarget",
                     "trigger1 = var(2)", "value = 824"))
        c.append(ctl(810, "Vira", "Turn", f"trigger1 = Time = {fim + 10}"))
    else:
        c.append(ctl(810, "Joga para trás", "TargetState", f"trigger1 = Time = {fim}", "trigger1 = NumTarget",
                     "trigger1 = var(2)", "value = 824"))
        c.append(ctl(810, "Joga", "TargetState", f"trigger1 = Time = {fim}", "trigger1 = NumTarget",
                     "trigger1 = !var(2)", "value = 823"))
        # jogou para trás: o oponente passa por cima (824 sem empurrão) e quem agarrou vira para ele no fim
        c.append(ctl(810, "Vira", "Turn", f"trigger1 = Time = {fim + 10}", "trigger1 = var(2)"))
    c.append(ctl(810, "Fim", "ChangeState", "trigger1 = AnimTime = 0", "value = 0", "ctrl = 1"))
    # 820: o oponente agarrado fica EM PÉ, na pose dele de quem levou o tranco (antes ficava na pose de queda)
    v = [f"[Statedef {vitima_preso}]\ntype = S\nmovetype = H\nphysics = N\nvelset = 0,0\nctrl = 0\n\n",
         pose(vitima_preso, "Pose", "Time = 0", V_PRESO, PRESO, 1),
         segura_pose(vitima_preso),
         ctl(vitima_preso, "Escape", "SelfState", "triggerall = Time <= 7", 'trigger1 = command = "y"',
             'trigger2 = command = "b"', "value = 0", "ctrl = 1"),
         ctl(vitima_preso, "Solto", "SelfState", "trigger1 = Time > 0", "trigger1 = !gethitvar(isbound)",
             "value = 5050")]
    # oponente: pancada segurando (a reação de tomar golpe DELE, alta ou baixa) e volta para a pose de preso
    for n, anim in REACOES:
        v.append(f"[Statedef {n}]\ntype = S\nmovetype = H\nphysics = N\nvelset = 0,0\nctrl = 0\n\n")
        v.append(pose(n, "Apanha", "Time = 0", V_ALTO if anim < 5010 else V_BAIXO, anim))
        v.append(segura_pose(n).replace(f"Anim != {PRESO} && AnimTime = 0", f"Time > 0 && Anim = {anim} && AnimTime = 0"))
        v.append(ctl(n, "Solto", "SelfState", "trigger1 = Time > 0", "trigger1 = !gethitvar(isbound)",
                     "value = 5050"))
    # 823 para longe, 824 por cima de quem agarrou, 835 derrubado no lugar
    for n, vel in ((823, "-4.2, -5.5"), (824, "4.6, -6.5"), (835, "-1.6, -4")):
        v.append(f"[Statedef {n}]\ntype = A\nmovetype = H\nphysics = N\nvelset = {vel}\nctrl = 0\n\n")
        v.append(pose(n, "Pose", "Time = 0", V_SOBE, 5030))
        v.append(ctl(n, "Caindo", "ChangeAnim", "trigger1 = Vel Y > 0", f"trigger1 = Anim = {V_SOBE}",
                     f"trigger1 = SelfAnimExist({V_CAI})", f"value = {V_CAI}"))
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


def renumerar(texto, n):
    """O texto do estado 810 (ou da ação) com o número n."""
    return (texto.replace("[Statedef 810]", f"[Statedef {n}]").replace("anim = 810", f"anim = {n}")
            .replace("[State 810,", f"[State {n},"))


def trocar_acao(air, n, novo):
    m = re.search(rf"^\[Begin Action {n}\][^\n]*\n.*?(?=^\[Begin Action|\Z)", air, re.M | re.S)
    if not m:
        return air.rstrip() + "\n\n" + novo
    return air[:m.start()] + novo + air[m.end():]


def desenhos_anotados(cns):
    """{tipo: [refs]} anotado no .cns por uma aplicação anterior (para rodar sozinho, sem o gerador)."""
    return {m.group(1): m.group(2).split() for m in RE_DESENHOS.finditer(cns)}


def aplicar_proprios(lutador, air, cns, desenhos):
    """Troca os agarrões que têm folha própria (desenhos = {tipo: ["grupo,índice", ...]}) pelos roteiros de PROPRIOS."""
    cns = RE_DESENHOS.sub("", cns)
    for tipo, p in PROPRIOS.get(lutador, {}).items():
        refs = desenhos.get(tipo)
        if not refs:
            continue
        tenta, agarra = TIPOS[tipo]
        tabela = acoes(air)
        if tenta not in tabela:
            raise SystemExit(f"{lutador}: sem ação {tenta} no .air")
        els = elementos(tabela[tenta])
        pega = next((e for e in els if e[4]), els[0])
        if p.alcanca:  # a tentativa com os desenhos da folha, nas caixas e nos tempos de hoje
            corpo = tabela[tenta]
            k = iter(range(len(els)))
            def troca(m, k=k):
                j = next(k)
                return f"{refs[p.alcanca[min(j, len(p.alcanca) - 1)]]}, 0,0, {m.group(5)}{m.group(6)}"
            corpo = "\n".join(RE_ELEM.sub(troca, ln) if RE_ELEM.match(ln) else ln for ln in corpo.splitlines())
            air = trocar_acao(air, tenta, f"[Begin Action {tenta}]\n{corpo.rstrip()}\n\n")
        quadros, contatos = montar_proprio(p, refs, pega[3])
        air = trocar_acao(air, agarra, acao_810(quadros, p, agarra))
        texto, _ = estados(p, contatos, None, 820, p.fim)
        if agarra != 810:
            texto = renumerar(texto, agarra)
            # a tentativa manda quem agarrou para o estado novo e o oponente para o 820 de todos
            m = re.search(rf"^\[Statedef {tenta}\]\n.*?(?=^\[Statedef|\Z)", cns, re.M | re.S)
            bloco = re.sub(r"(?m)^p2stateno\s*=\s*\d+", "p2stateno = 820", m.group(0))
            cns = cns[:m.start()] + bloco + cns[m.end():]
        # anotado no .cns (comentário dentro do estado), para o agarrao_mk.py rodar sozinho e manter as folhas
        nota = f"; desenhos do agarrão {tipo} = {' '.join(refs)}\n"
        cns = trocar_statedef(cns, agarra, texto.replace("\n\n", "\n" + nota + "\n", 1))
    return air, cns


def aplicar(lutador, air, cns, desenhos=None):
    """Devolve (air, cns) com o agarrão segura-e-bate. Idempotente. desenhos = {tipo: refs} dos agarrões com folha
    própria (o gerador passa; rodando sozinho, vale o que uma aplicação anterior deixou anotado no .cns)."""
    if desenhos is None:
        desenhos = desenhos_anotados(cns)
    # tira o que uma aplicação anterior pôs (estados do oponente no fim do .cns)
    if MARCA in cns:
        # tira só o bloco do agarrão: o que outras ferramentas puseram depois dele no fim do .cns (aura, cenário) fica
        i = cns.index(MARCA)
        resto = cns[i + len(MARCA):]
        for n in VITIMA:
            m = re.search(rf"^\[Statedef {n}\]\n.*?(?=^\[Statedef|^; ---- |\Z)", resto, re.M | re.S)
            if m:
                resto = resto[:m.start()] + resto[m.end():]
        cns = cns[:i].rstrip() + "\n\n" + resto.strip() + "\n" if resto.strip() else cns[:i].rstrip() + "\n"
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
    return aplicar_proprios(lutador, air, cns, desenhos)


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
