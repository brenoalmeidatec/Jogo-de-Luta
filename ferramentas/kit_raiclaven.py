#!/usr/bin/env python3
"""Kit todo próprio do Raiclaven despertado, com A Cliente nas costas (issues #43 e #47, aprovado pelo Breno 15/11).

Regra da seção 4 (docs/regras-dos-lutadores.md, Breno na #47): no despertado NADA do modo normal entra. Aqui ficam os
golpes da lista aprovada (docs/fichas/raiclaven-despertado-golpes.md) e o que liga eles no motor:

  * estados 20xxx (normais, direcionais, correntes e kombo), 21xxx (especiais), 23000 (super) e 24xxx (agarrões);
  * ações 20xxx no .air;
  * no .cmd, um bloco só do despertado (var(20) > 0) e o resto dos golpes trancado com var(20) = 0. Ficam para as duas
    formas só a mecânica de defesa (parry, rolamento, afastar), o Despertar e o kit da #47 (Cadeira Elétrica 4700 e
    Secador de Raio 4750, que já são do despertado).

ARTE: enquanto as folhas da criatura (folhas_criatura.py, c_<nome>.png) não chegam, cada golpe copia os quadros de uma
ação da dupla (`fonte`, a arte do arnês) com tempo e caixa próprios. Quando a folha `folha` existir, o gerar_raiclaven
troca os quadros (o número da ação e do estado não muda).

  python3 ferramentas/kit_raiclaven.py            aplica em chars/raiclaven (air, cns e cmd), idempotente
  python3 ferramentas/kit_raiclaven.py --cmd      só o .cmd (depois do `git checkout chars/raiclaven/raiclaven.cmd`)
  python3 ferramentas/kit_raiclaven.py --lista    a tabela dos golpes
"""
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agarrao_mk as mk  # noqa: E402
import efeitos  # noqa: E402
import gerar_pengaro as gp  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
MARCA = "(kit_raiclaven.py)"
INI = "; ---- kit próprio do Raiclaven despertado (ferramentas/kit_raiclaven.py) ----\n"
FIM = "; ---- fim do kit próprio do Raiclaven despertado ----\n"
TRAVA = "triggerall = var(20) = 0 ; só no modo normal (kit_raiclaven.py)"
DESP = "var(20) > 0"
# valores do .cmd que valem nas duas formas: defesa (parry, rolamento, afastar) e o Despertar
MECANICA = {260, 650, 700, 705, 720, 760, 764, 2000}
E = 3  # .air em 3x (xscale .33)


@dataclass
class Golpe:
    estado: int
    nome: str
    folha: str            # folha da criatura (folhas_criatura.FOLHAS)
    fonte: int            # ação da dupla usada até a folha chegar
    danos: tuple = (40,)
    tipo: str = "S"       # S, C ou A
    attr: str = ""
    guarda: str = ""
    chao: str = "High"
    queda: bool = False
    final: bool = False
    avanco: float = 0.0
    vel: str = ""
    ar: str = ""
    ritmo: float = 1.0    # multiplica a duração dos quadros da fonte
    alcance: int = 0      # px (1x) a mais na frente da caixa de golpe (braço que estica)
    caixa: tuple = ()     # caixa de golpe fixa (1x), no lugar da da fonte
    comando: str = ""     # descrição para a lista de golpes
    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        self.danos = tuple(self.danos) if isinstance(self.danos, (list, tuple)) else (self.danos,)
        self.attr = self.attr or {"S": "S, NA", "C": "C, NA", "A": "A, NA"}[self.tipo]
        self.guarda = self.guarda or {"S": "MA", "C": "L", "A": "HA"}[self.tipo]


G = Golpe
# ---------------------------------------------------------------------------------------------- A. normais (16)
NORMAIS = (
    G(20200, "Tapa de Garra", "x_pe", 10200, 34, comando="x"),
    G(20210, "Navalha Comprida", "y_pe", 10210, 62, caixa=(30, -104, 96, -74), ritmo=1.15, comando="y"),
    G(20230, "Bota e Gosma", "a_pe", 10230, 44, comando="a"),
    G(20240, "Três Braços", "b_pe", 10240, (30, 40), ritmo=1.1, comando="b"),
    G(20400, "Belisco no Tornozelo", "x_ag", 10400, 30, tipo="C", comando="↓ + x"),
    G(20410, "Mordida Antiaérea", "y_ag", 10410, 60, tipo="C", guarda="MA", attr="C, NA",
      caixa=(0, -150, 46, -60), queda=True, vel="-2,-6", ar="-2,-7", comando="↓ + y"),
    G(20430, "Tubo no Chão", "a_ag", 10430, 36, tipo="C", chao="Low", comando="↓ + a"),
    G(20440, "Varrida de Garra", "b_ag", 10440, 66, tipo="C", chao="Trip", queda=True, vel="-2,-2", ar="-2,-3",
      alcance=16, comando="↓ + b"),
    G(20600, "Arranhão de Cima", "x_ar", 10600, 34, tipo="A", comando="no ar x"),
    G(20610, "Navalha em Arco", "y_ar", 10610, 58, tipo="A", comando="no ar y (cruza por cima)"),
    G(20630, "Joelhada e Mordida", "a_ar", 10601, 46, tipo="A", comando="no ar a"),
    G(20640, "Por Baixo Mordendo", "b_ar", 10611, 60, tipo="A", comando="no ar b"),
    G(20250, "Mordida por Cima", "f_y", 10215, 66, guarda="HA", ritmo=1.2, comando="→ + y (por cima)"),
    G(20260, "Pisão de Choque", "f_b", 10245, 62, guarda="L", chao="Low", comando="→ + b"),
    G(20270, "Bafo do Secador", "t_x", 10201, 40, vel="-10", alcance=20, comando="← + x (afasta)"),
    G(20280, "Puxa pela Gola", "t_a", 10231, 36, vel="4", ar="2,-3", comando="← + a (puxa)"),
)

# ---------------------------------------------------------------------------------------------- B. correntes (4 x 3 + final)
# o 1º golpe é o normal do botão; aqui o 2º, o 3º e o finalizador
CORRENTES = {
    "x": (G(20301, "Tesourinha: garra", "corrente_x", 10201, 34, avanco=2.4, alcance=22, vel="-1.5"),
          G(20302, "Tesourinha: mordida", "corrente_x", 10216, 40, avanco=3.2, caixa=(30, -100, 92, -60), vel="-1.5"),
          G(20303, "Tesourinha: dentes e chacoalha", "corrente_x", 11100, (30, 30, 50), final=True, queda=True,
            vel="-6,-4", ar="-5,-5")),
    "y": (G(20311, "Navalha Comprida 2", "corrente_y", 10216, 50, caixa=(30, -104, 108, -74), avanco=1.8, vel="-1.5"),
          G(20312, "Navalha Comprida 3", "corrente_y", 10246, 56, caixa=(30, -104, 118, -74), avanco=1.8, vel="-1.5"),
          G(20313, "Corte em X", "corrente_y", 11200, 120, final=True, queda=True, alcance=30, vel="-6,-4",
            ar="-5,-5")),
    "a": (G(20321, "Tubo Chicote baixo", "corrente_a", 10231, 40, guarda="L", chao="Low", avanco=1.8, vel="-1.5"),
          G(20322, "Tubo Chicote alto", "corrente_a", 10430, 44, avanco=2.4, alcance=26, vel="-1.5"),
          G(20323, "Tubo Laça o Pé", "corrente_a", 11300, 110, final=True, queda=True, chao="Trip", guarda="L",
            vel="3,-2", ar="2,-3")),
    "b": (G(20331, "Pião da Cadeira 1", "corrente_b", 10245, 44, avanco=1.8, vel="-1.5"),
          G(20332, "Pião da Cadeira 2", "corrente_b", 10246, 50, avanco=1.8, vel="-1.5"),
          G(20333, "Choque em Círculo", "corrente_b", 11400, 125, final=True, queda=True, vel="-6,-4", ar="-5,-5",
            caixa=(-60, -110, 70, 0))),
}
PRIMEIRO = {"x": 20200, "y": 20210, "a": 20230, "b": 20240}

# ---------------------------------------------------------------------------------------------- C. kombo Cobaia
# ← + a (20280, puxa pela gola), y (enfia a navalha), ↓ + b (varre e lança)
KOMBO = (
    G(20341, "Cobaia: navalha", "y_pe", 10210, 50, caixa=(30, -104, 96, -74), avanco=1.5),
    G(20342, "Cobaia: varre e lança", "b_ag", 10440, 85, tipo="C", attr="C, NA", guarda="L", chao="Low",
      queda=True, vel="-1.5,-9", ar="-1.5,-9", final=True),
)

# ---------------------------------------------------------------------------------------------- D. especiais
ESPECIAIS = (
    G(21000, "Peruca Viva fraca", "peruca", 11000, (), comando="↓ ↘ → + x"),
    G(21001, "Peruca Viva forte", "peruca", 11001, (), comando="↓ ↘ → + y"),
    G(21100, "Pescoço de Borracha", "pescoco", 11101, 80, alcance=100, ritmo=1.2, vel="-5",
      comando="↓ ↙ ← + x"),
    G(21101, "Pescoço de Borracha (puxa)", "pescoco", 11101, 70, alcance=100, ritmo=1.25, vel="6", ar="4,-3",
      comando="↓ ↙ ← + y"),
    G(21200, "Tanque Estourado", "tanque", 11501, 100, caixa=(-75, -120, 80, 0), queda=True, vel="-5,-5",
      ar="-4,-6", attr="S, SA", comando="→ ↓ ↘ + a/b"),
    G(21300, "Bigodes Carnívoros", "bigodes", 11001, (), comando="← → + b"),
)
SUPER = G(23000, "Sala de Cirurgia", "cirurgia_a", 13000, (40, 25, 25, 25, 25, 140), attr="S, HA",
          caixa=(10, -110, 72, -30),
          comando="← → ↓ + y (2 barras)")
# agarrões novos (o em pé é a Cadeira Elétrica 4700 da #47, que já bate com golpes do kit: despertados_47.CFG)
AGARROES = {
    24100: ("Lavagem", (mk.Golpe(20400, 24, "pega a cabeça"), mk.Golpe(20430, 24, "enfia no tanque")),
            mk.Golpe(20342, 60, "solta encharcado"), "↓ + y perto"),
    24200: ("Transplante", (mk.Golpe(20240, 24, "abraço de três braços"), mk.Golpe(20331, 24, "gira"),
                            mk.Golpe(20332, 24, "gira")), mk.Golpe(20333, 66, "arremesso com choque"),
            "→ ↓ → + y perto"),
}

SIMPLES = NORMAIS + tuple(g for c in CORRENTES.values() for g in c) + KOMBO + tuple(
    g for g in ESPECIAIS if g.danos)
TODOS = SIMPLES + tuple(g for g in ESPECIAIS if not g.danos) + (SUPER,)


# ---------------------------------------------------------------------------------------------- arte nova
# Arte do corpo firme (boneco de peças, ferramentas/firme.py cliente): cada animação do kit_cliente.ANIMS com quadros
# em sprites/raiclaven_cliente/quadros_pecas_hd/<nome>/ entra no .sff como PNG RGBA (formato 12) no grupo
# GRUPO_PECAS + posição no ANIMS. O golpe com arte nova usa os desenhos e os ticks do tempos.json (a caixa de golpe sai
# de lá); sem arte nova continua a provisória. O parado (ação 0) entra pelo remap do despertado (86..93).
PECAS = RAIZ / "sprites/raiclaven_cliente/quadros_pecas_hd"
GRUPO_PECAS = 26000
EIXO_PECAS = (540, 660)


def anims_pecas():
    """{nome: (ação, grupo, tempos)} das animações do corpo firme que já têm quadros."""
    import json
    import kit_cliente as kc
    out = {}
    for k, (nome, (acao, _q, _c)) in enumerate(kc.ANIMS.items()):
        t = PECAS / nome / "tempos.json"
        if t.exists():
            out[nome] = (acao, GRUPO_PECAS + k, json.loads(t.read_text(encoding="utf-8")))
    return out


def pecas_da_acao(estado):
    for nome, (acao, grupo, tempos) in anims_pecas().items():
        if acao == estado:
            return nome, grupo, tempos
    return None


PALETA_PECAS = RAIZ / "sprites/raiclaven_cliente/paleta_sff.bin"


def paleta_pecas(quadros):
    """Paleta travada do despertado com A Cliente: 255 cores tiradas de todos os desenhos do corpo firme (corte pela
    mediana) + o 0 transparente. Cor fora dela não entra no .sff (regra da paleta indexada)."""
    from PIL import Image
    import numpy as np
    amostra = np.concatenate([q[q[..., 3] > 0][::3, :3] for q in quadros])
    lado = int(np.ceil(np.sqrt(len(amostra))))
    tira = np.zeros((lado * lado, 3), np.uint8)
    tira[:len(amostra)] = amostra
    tira[len(amostra):] = amostra[0]
    q = Image.fromarray(tira.reshape(lado, lado, 3)).quantize(255, method=Image.Quantize.MEDIANCUT,
                                                               dither=Image.Dither.NONE)
    cores = np.array(q.getpalette()[:255 * 3], np.uint8).reshape(-1, 3)
    pal = np.zeros((256, 4), np.uint8)
    pal[1:1 + len(cores), :3] = cores
    pal[1:, 3] = 255
    return pal


def indexar(rgba, pal):
    """Índices na paleta travada (cor mais próxima, sem pontilhado); transparente = 0."""
    import numpy as np
    al = rgba[..., 3] > 0
    px = rgba[al][:, :3].astype(np.int32)
    cores = pal[1:, :3].astype(np.int32)
    idx = np.empty(len(px), np.uint8)
    for i in range(0, len(px), 20000):
        d = ((px[i:i + 20000, None, :] - cores[None]) ** 2).sum(-1)
        idx[i:i + 20000] = d.argmin(1) + 1
    out = np.zeros(rgba.shape[:2], np.uint8)
    out[al] = idx
    return out


def sprites_pecas(sff):
    """Põe no .sff os desenhos do corpo firme (some o que havia nos grupos GRUPO_PECAS..+99), indexados na paleta
    travada da dupla (uma paleta a mais no .sff, PALETA_PECAS), em RLE como o resto do corpo."""
    import conferir_sff as cs
    from PIL import Image
    import numpy as np
    pal, nos, _ = cs.ler(sff)
    extras = list(cs.EXTRAS.get(str(Path(sff).resolve()), []))
    antiga = PALETA_PECAS.read_bytes() if PALETA_PECAS.exists() else None
    pis = {}
    rle, png, vistos = [], [], set()
    for n in nos:
        k = (n["g"], n["i"])
        if k in vistos or GRUPO_PECAS <= n["g"] < GRUPO_PECAS + 100:
            continue
        vistos.add(k)
        if n.get("png"):
            png.append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
        else:
            rle.append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"], n.get("pi", 0)))
    quadros = []
    for nome, (_a, grupo, tempos) in anims_pecas().items():
        for i in sorted({e["desenho"] for e in tempos["elementos"]}):
            a = np.array(Image.open(PECAS / nome / f"{i:02d}.png").convert("RGBA"))
            ys, xs = np.nonzero(a[..., 3])
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            quadros.append((grupo, i, np.ascontiguousarray(a[y0:y1, x0:x1]), int(EIXO_PECAS[0] - x0),
                            int(EIXO_PECAS[1] - y0)))
    nova = paleta_pecas([q[2] for q in quadros])
    bnova = nova.tobytes()
    if antiga is not None and antiga in extras:  # a paleta da rodada anterior sai (só os desenhos dela a usavam)
        j = extras.index(antiga)
        extras.pop(j)
        rle = [r[:7] + ((r[7] - 1 if r[7] > 2 + j else r[7]),) for r in rle]
    extras.append(bnova)
    pi = 2 + len(extras) - 1
    for grupo, i, a, ex, ey in quadros:
        px = indexar(a, nova)
        rle.append((grupo, i, a.shape[1], a.shape[0], ex, ey, px.tobytes(), pi))
    efeitos.gravar(sff, pal, rle, png, extras)
    PALETA_PECAS.write_bytes(bnova)
    return len(quadros)


def remap_parado(cns, air):
    """O parado do despertado (ação 0 com o remap) passa a mostrar o parado do corpo firme: cada sprite da ação 0
    aponta para o desenho que o corpo firme mostra naquele tick (a ação 0 tem 8 sprites de 7 ticks)."""
    pec = anims_pecas().get("parado")
    if not pec:
        return cns
    _a, grupo, tempos = pec
    els = mk.elementos(mk.acoes(air)[0])
    linha = []
    for e in tempos["elementos"]:
        linha += [e["desenho"]] * e["ticks"]
    total_base = sum(max(t, 1) for _e, t, *_ in els)
    t = 0
    for el, d, *_ in els:
        g, i = (int(v) for v in el.split(",")[:2])
        meio = t + max(d, 1) / 2
        desenho = linha[min(len(linha) - 1, int(meio / total_base * len(linha)))]
        cns, k = re.subn(rf"^{g},{i} = \d+,\d+$", f"{g},{i} = {grupo},{desenho}", cns, count=1, flags=re.M)
        assert k == 1, f"remap do despertado sem a linha {g},{i}"
        t += max(d, 1)
    return cns


# ---------------------------------------------------------------------------------------------- .air
def quadros(g, tabela):
    """[(elemento, ticks, resto, caixas2, caixa1)] do golpe, a partir da fonte (arte provisória da dupla) ou, quando
    o corpo firme já tem a animação, dos desenhos novos."""
    if g.fonte not in tabela:
        raise SystemExit(f"kit_raiclaven: a ação {g.fonte} ({g.nome}) não existe no .air")
    out = []
    els = mk.elementos(tabela[g.fonte])
    nova = pecas_da_acao(g.estado)
    if nova:
        _nome, grupo, tempos = nova
        c2 = els[0][3]
        cx = tuple(tempos["caixa"]) if tempos.get("caixa") else (tuple(v * E for v in g.caixa) if g.caixa else None)
        return [(f"{grupo},{e['desenho']}, 0,0, ", e["ticks"], "", c2, cx if e["caixa"] else None)
                for e in tempos["elementos"]]
    for el, t, resto, c2, c1 in els:
        if t > 0:
            t = max(1, round(t * g.ritmo))
        if c1 and g.caixa:
            c1 = tuple(v * E for v in g.caixa)
        elif c1 and g.alcance:
            c1 = (c1[0], c1[1], c1[2] + g.alcance * E, c1[3])
        out.append((el, t, resto, c2, c1))
    if g.caixa and not any(q[4] for q in out):  # fonte sem caixa de golpe (o super): do 3º quadro em diante
        out = [(el, t, resto, c2, tuple(v * E for v in g.caixa) if k >= 2 else None)
               for k, (el, t, resto, c2, _c) in enumerate(out)]
    if g is SUPER:  # o último quadro segura a operação inteira
        el, t, resto, c2, c1 = out[-1]
        out[-1] = (el, 70, resto, c2, c1)
    return out


def texto_acao(g, qs):
    linhas = [f"; {g.nome} {MARCA}"]
    for el, t, resto, c2, c1 in qs:
        if c2:
            linhas.append(f"Clsn2: {len(c2)}")
            linhas += [" " + re.sub(r"^Clsn2\s*\[\s*(\d+)\s*\]", r"Clsn2[\1]", b, flags=re.I) for b in c2]
        if c1:
            linhas += ["Clsn1: 1", f" Clsn1[0] = {c1[0]}, {c1[1]}, {c1[2]}, {c1[3]}"]
        linhas.append(f"{el}{t}{resto}")
    return "\n".join(linhas)


def trechos(qs):
    """[(tick de início, tick de fim)] de cada trecho de quadros com caixa de golpe."""
    t, out, aberto = 0, [], None
    for el, d, resto, c2, c1 in qs:
        d = max(d, 1)
        if c1 and aberto is None:
            aberto = t
        if not c1 and aberto is not None:
            out.append((aberto, t))
            aberto = None
        t += d
    if aberto is not None:
        out.append((aberto, t))
    return out


def duracao(qs):
    return sum(max(d, 0) for _, d, *_ in qs)


# ---------------------------------------------------------------------------------------------- .cns
def classe(g, k, n):
    ultimo = k == n - 1
    dano = g.danos[k]
    if g.final and ultimo:
        return "final"
    return "forte" if dano >= 85 else "medio" if dano >= 45 else "fraco"


def tempos_dos_acertos(g, qs):
    tr = trechos(qs)
    if not tr:
        raise SystemExit(f"kit_raiclaven: {g.nome} ({g.fonte}) sem caixa de golpe")
    n = len(g.danos)
    if len(tr) >= n:
        return [a for a, _ in tr[:n]]
    # mais acertos que trechos: espalha os que faltam dentro do último trecho
    a, b = tr[-1]
    base = [x for x, _ in tr[:-1]]
    resto = n - len(base)
    passo = max(3, (b - a) // resto)
    return base + [a + i * passo for i in range(resto)]


def estado_simples(g, qs):
    agachado, no_ar = g.tipo == "C", g.tipo == "A"
    fis = "A" if no_ar else "C" if agachado else "S"
    t = [gp.estado(g.estado, g.tipo, "A", fis, anim=g.estado, juggle=3, velset=None if no_ar else "0,0").replace(
        "\n\n", f"\n; {g.nome} {MARCA}\n\n", 1)]
    t.append(f"[State {g.estado}, som vento]\ntype = PlaySnd\ntrigger1 = Time = 0\nvalue = F40,0\n\n")
    tempos = tempos_dos_acertos(g, qs)
    if g.avanco:
        t.append(f"[State {g.estado}, Avanço]\ntype = VelSet\ntrigger1 = Time = {max(1, tempos[0] - 3)}\n"
                 f"x = {g.avanco}\n\n[State {g.estado}, Freia]\ntype = VelSet\ntrigger1 = Time = {tempos[-1] + 2}\n"
                 "x = 0\n\n")
    for k, (tick, dano) in enumerate(zip(tempos, g.danos)):
        cl = classe(g, k, len(g.danos))
        ultimo = k == len(g.danos) - 1
        forte, medio = cl in ("forte", "final"), cl == "medio"
        queda = g.queda and ultimo
        gat = f"Time = {tick}" + (" && MoveHit" if k else "")
        t.append(gp.hitdef(g.estado, gat, g.attr, dano, tipo="Heavy" if forte else "Medium" if medio else "Light",
                           guarda=g.guarda, hit=21 if forte else 20 if medio else 14,
                           escorrega=8 if forte else 7 if medio else 5,
                           vel=g.vel or ("-7" if forte else "-3.5" if medio else "-2.5"),
                           ar=g.ar or ("-3,-4" if queda else "-1.4,-3"), queda=queda, chao=g.chao, classe=cl))
    if no_ar:
        t.append(f"[State {g.estado}, Cai]\ntype = ChangeState\ntrigger1 = Vel Y > 0\ntrigger1 = Pos Y >= 0\n"
                 "value = 52\n\n")
    else:
        t.append(gp.fim(g.estado, 11 if agachado else 0))
    return "".join(t)


def ctl(n, nome, tipo, *linhas):
    return mk.ctl(n, f"{nome} {MARCA}", tipo, *linhas)


def estado_peruca(g, qs):
    forte = g.estado == 21001
    solta = trechos(qs)[0][0] if trechos(qs) else 8
    t = [f"[Statedef {g.estado}]\ntype = S\nmovetype = A\nphysics = S\nctrl = 0\nsprpriority = 2\n"
         f"anim = {g.estado}\nvelset = 0,0\n; {g.nome} {MARCA}\n\n"]
    t.append(ctl(g.estado, "Som", "PlaySnd", f"trigger1 = Time = {solta}", "value = F40,1"))
    t.append(ctl(g.estado, "Peruca corre pelo chão", "Projectile", f"trigger1 = Time = {solta}", "projid = 21000",
                 "projanim = 21050", "projhitanim = 21051", "projremanim = 21051", "projscale = 1,1",
                 "offset = 40, -10", f"velocity = {4.6 if forte else 3.2}, 0", "attr = S, SP",
                 "damage = 60, 6", "animtype = Light", "guardflag = L", "hitflag = MAF", "ground.type = Low",
                 "pausetime = 0, 10", "ground.hittime = 16", "ground.velocity = -3", "air.velocity = -2,-3",
                 "sparkno = S9200", "guard.sparkno = S9202", "hitsound = S51,0", "guardsound = F6,0",
                 "projpriority = 1", "projremovetime = 160", "sprpriority = 3"))
    t.append(gp.fim(g.estado))
    return "".join(t)


def estado_bigodes(g, qs):
    solta = trechos(qs)[0][0] if trechos(qs) else 8
    t = [f"[Statedef {g.estado}]\ntype = S\nmovetype = A\nphysics = S\nctrl = 0\nsprpriority = 2\n"
         f"anim = {g.estado}\nvelset = 0,0\n; {g.nome} {MARCA}\n\n"]
    t.append(ctl(g.estado, "Som", "PlaySnd", f"trigger1 = Time = {solta}", "value = F40,2"))
    t.append(ctl(g.estado, "Nuvem de bigodes", "Projectile", f"trigger1 = Time = {solta}", "projid = 21300",
                 "projanim = 21350", "projhitanim = 21350", "projremanim = 21351", "offset = 50, -70",
                 "velocity = 3.4, 0", "projhits = 5", "projmisstime = 6", "projremove = 0",
                 "attr = S, SP", "damage = 18, 2", "animtype = Light", "guardflag = MA", "hitflag = MAF",
                 "pausetime = 0, 6", "ground.hittime = 12", "ground.velocity = -.5", "air.velocity = -.5,-2",
                 "sparkno = S9200", "guard.sparkno = S9202", "hitsound = S51,0", "guardsound = F6,0",
                 "projpriority = 2", "projremovetime = 150", "sprpriority = 4"))
    t.append(gp.fim(g.estado))
    return "".join(t)


def estado_tanque(g, qs):
    """Pula e cai de costas: o choque em volta é a caixa larga do quadro do impacto."""
    texto = estado_simples(g, qs)
    a = trechos(qs)[0][0]
    pulo = (ctl(g.estado, "Pula", "VelSet", "trigger1 = Time = 2", "y = -4.5")
            + ctl(g.estado, "Gravidade", "VelAdd", f"trigger1 = Time > 2 && Time < {a}", "y = .5")
            + ctl(g.estado, "Cai de costas", "PosSet", f"trigger1 = Time = {a}", "y = 0")
            + ctl(g.estado, "Para", "VelSet", f"trigger1 = Time = {a}", "y = 0")
            + ctl(g.estado, "Choque: tremida", "EnvShake", f"trigger1 = Time = {a}", "time = 18", "freq = 120",
                  "ampl = -6")
            + ctl(g.estado, "Choque: estouro verde", "Explod", f"trigger1 = Time = {a}", "anim = 47004",
                  "postype = p1", "pos = 0, -10", "removetime = -2", "scale = 2.2, 1.2", "sprpriority = 5",
                  "ownpal = 1")
            + ctl(g.estado, "Choque: som", "PlaySnd", f"trigger1 = Time = {a}", "value = 50,8"))
    return texto.replace(f"[State {g.estado}, som vento]", pulo + f"[State {g.estado}, som vento]", 1).replace(
        "physics = S\n", "physics = N\n", 1)


def estado_super(g, qs):
    tempos = tempos_dos_acertos(g, qs)
    t0 = tempos[0]
    tempos = [t0 + 9 * k for k in range(len(g.danos))]
    t = [f"[Statedef {g.estado}]\ntype = S\nmovetype = A\nphysics = S\nctrl = 0\nsprpriority = 2\n"
         f"anim = {g.estado}\nvelset = 0,0\njuggle = 0\npoweradd = -2000\n; {g.nome} {MARCA}\n\n"]
    t.append(ctl(g.estado, "Escurece: centro cirúrgico", "SuperPause", "trigger1 = Time = 0", "time = 40",
                 "anim = -1", "sound = 50,7", "darken = 1", "p2defmul = 1", "poweradd = 0"))
    t.append(ctl(g.estado, "Luz de cirurgia pisca", "BGPalFX", "trigger1 = Time = 0", "time = 40",
                 "mul = 60,80,60", "sinadd = 90,110,90,8"))
    t.append(ctl(g.estado, "Rastro", "AfterImage", "trigger1 = Time = 0", f"time = {tempos[-1] + 10}", "length = 8",
                 "palcolor = 0", "paladd = 0,60,0", "palmul = .6,.9,.6", "timegap = 2", "framegap = 3"))
    t.append(ctl(g.estado, "Prende com o braço de aço", "VelSet", f"trigger1 = Time = {max(1, t0 - 6)}", "x = 5"))
    t.append(ctl(g.estado, "Freia", "VelSet", f"trigger1 = Time = {t0 + 1}", "x = 0"))
    n = len(g.danos)
    for k, (tick, dano) in enumerate(zip(tempos, g.danos)):
        ultimo = k == n - 1
        gat = f"Time = {tick}" + (" && MoveHit" if k else "")
        t.append(gp.hitdef(g.estado, gat, g.attr, dano, tipo="Heavy" if ultimo else "Light", guarda="MA",
                           hit=12 if ultimo else 40, escorrega=0 if not ultimo else 10,
                           vel="-8,-6" if ultimo else "0", ar="-6,-7" if ultimo else "0,-1",
                           queda=ultimo, classe="final" if ultimo else "super"))
        if k:
            t.append(ctl(g.estado, f"Operação {k}: estouro verde", "Explod", f"trigger1 = Time = {tick}",
                         "trigger1 = MoveHit", "anim = 47004", "postype = p1", f"pos = {40 + 6 * k}, {-70 + 8 * k}",
                         "removetime = -2", "sprpriority = 6", "ownpal = 1", "ignorehitpause = 1"))
    fim = tempos[-1]
    t.append(ctl(g.estado, "Raio da Cabeça no Pote", "Explod", f"trigger1 = Time = {fim - 9}", "trigger1 = MoveHit",
                 "anim = 47002", "postype = p1", "pos = 20, -60", "removetime = -2", "scale = .9, .9",
                 "sprpriority = 6", "ownpal = 1"))
    t.append(ctl(g.estado, "Final: tanques estouram", "Explod", f"trigger1 = Time = {fim}", "trigger1 = MoveHit",
                 "anim = 47001", "postype = p1", "pos = 50, -60", "removetime = -2", "sprpriority = 6",
                 "ownpal = 1"))
    t.append(ctl(g.estado, "Final: congela", "Pause", f"trigger1 = Time = {fim}", "trigger1 = MoveHit", "time = 14",
                 "movetime = 0"))
    t.append(ctl(g.estado, "Final: clarão", "BGPalFX", f"trigger1 = Time = {fim}", "time = 6", "add = 120,160,120"))
    t.append(ctl(g.estado, "Final: tremida forte", "EnvShake", f"trigger1 = Time = {fim}", "time = 30", "freq = 90",
                 "ampl = -11"))
    t.append(ctl(g.estado, "Final: som", "PlaySnd", f"trigger1 = Time = {fim}", "value = 50,8"))
    t.append(gp.fim(g.estado))
    return "".join(t)


def acoes_projeteis(air):
    """Peruca Viva (21050/21051) e Bigodes (21350/21351): por enquanto a faísca e o raio da #47 em miniatura."""
    corpo = lambda g, esc, t, n=4: "\n".join(
        [f"; provisório até a folha da criatura {MARCA}", "Clsn1Default: 1", " Clsn1[0] = -14, -14, 14, 14",
         "Clsn2Default: 1", " Clsn2[0] = -14, -14, 14, 14"]
        + [f"{g},{i}, 0,0, {t}, , , {esc}, {esc}" for i in range(n)])
    for n, (g, esc) in {21050: (47004, .5), 21350: (47003, .7)}.items():
        air = efeitos.por_acao(air, n, corpo(g, esc, 3))
        air = efeitos.por_acao(air, n + 1, "\n".join(f"{g},{i}, 0,0, 2, , , {esc}, {esc}" for i in range(4)))
    return air


def aplicar_air_cns(air, cns):
    tabela = mk.acoes(air)
    blocos, saida = {}, []
    for g in TODOS:
        qs = quadros(g, tabela)
        air = efeitos.por_acao(air, g.estado, texto_acao(g, qs))
        if g.estado in (21000, 21001):
            saida.append(estado_peruca(g, qs))
        elif g.estado == 21300:
            saida.append(estado_bigodes(g, qs))
        elif g.estado == 21200:
            saida.append(estado_tanque(g, qs))
        elif g is SUPER:
            saida.append(estado_super(g, qs))
        else:
            saida.append(estado_simples(g, qs))
        blocos[g.estado] = qs
    air = acoes_projeteis(air)
    cns = re.sub(re.escape(INI) + r".*?" + re.escape(FIM), "", cns, flags=re.S)
    texto = INI + "".join(saida)
    # agarrões novos: o mesmo segura-e-bate da Cadeira Elétrica (despertados_47), com golpes do kit
    cns_com = cns + "\n" + texto
    for n, (nome, golpes, final, _) in AGARROES.items():
        acao, estados = agarrao(nome, golpes, final, n, air, cns_com)
        air = efeitos.por_acao(air, n + 10, acao.split("\n", 1)[1])
        texto += estados
    texto += FIM
    i = cns.index(mk.MARCA) if mk.MARCA in cns else len(cns)
    cns = cns[:i].rstrip() + "\n\n" + texto + "\n" + cns[i:]
    return re.sub(r"\n{3,}", "\n\n", air), cns


def agarrao(nome, golpes, final, n, air, cns):
    import despertados_47 as d47
    velho = d47.CFG["raiclaven"]
    c = d47.Cfg(nome, golpes, final, velho.prio_agarrao, velho.nome_poder, velho.solta, velho.offset, velho.vel,
                velho.som_carga, velho.som_solta, velho.som_acerto, velho.som_final)
    d47.CFG["raiclaven"] = c
    try:
        acao, texto, _r, _c = d47.estados_agarrao("raiclaven", air, cns)
    finally:
        d47.CFG["raiclaven"] = velho
    troca = lambda s: (re.sub(r"\b4710\b", str(n + 10), re.sub(r"\b4700\b", str(n), s))
                       .replace("despertados_47.py", "kit_raiclaven.py").replace("issue #47", "issue #43"))
    return troca(acao), troca(texto)


# ---------------------------------------------------------------------------------------------- .cmd
COMANDOS = {
    "k_peruca_x": "~D, DF, F, x", "k_peruca_y": "~D, DF, F, y",
    "k_pescoco_x": "~D, DB, B, x", "k_pescoco_y": "~D, DB, B, y",
    "k_tanque_a": "~F, D, DF, a", "k_tanque_b": "~F, D, DF, b",
    "k_bigodes": "~B, F, b", "k_cirurgia": "~B, F, D, y", "k_transplante": "~F, D, F, y",
}


def entrada(nome, valor, conds, gatilhos=("ctrl",)):
    t = [f"[State -1, Desp {nome} {MARCA}]", "type = ChangeState", f"value = {valor}", f"triggerall = {DESP}"]
    t += [f"triggerall = {c}" for c in conds]
    t += [f"trigger{i + 1} = {g}" for i, g in enumerate(gatilhos)]
    return "\n".join(t) + "\n\n"


def faixa(estados):
    return " || ".join(f"stateno = {s}" for s in estados)


def bloco_cmd():
    em_pe, chao = "statetype = S", "statetype != A"
    sem_dir = ['command != "holddown"', 'command != "holdfwd"', 'command != "holdback"']
    normais_chao = [g.estado for g in NORMAIS if g.tipo != "A"] + [g.estado for c in CORRENTES.values() for g in c[:2]]
    cancela_especial = f"({faixa(normais_chao + [20341])}) && movecontact"
    especial = ["ctrl", cancela_especial]
    perto = ["p2bodydist x < 10", "p2statetype != A", "p2movetype != H", "stateno != 100", "ctrl"]
    c = []
    c.append(entrada("Sala de Cirurgia", 23000, ['command = "k_cirurgia"', "power >= 2000", chao],
                     ("ctrl", f"({faixa(normais_chao + [20341, 21100, 21101, 21200])}) && movehit")))
    c.append(entrada("Transplante", 24200, ['command = "k_transplante"', em_pe] + perto, ("1",)))
    for b, n in (("x", 21000), ("y", 21001)):
        c.append(entrada(f"Peruca Viva {b}", n, [f'command = "k_peruca_{b}"', chao, "NumProjID(21000) = 0"],
                         especial))
        c.append(entrada(f"Pescoço {b}", 21100 if b == "x" else 21101, [f'command = "k_pescoco_{b}"', chao],
                         especial))
    for b in "ab":
        c.append(entrada(f"Tanque Estourado {b}", 21200, [f'command = "k_tanque_{b}"', chao], especial))
    c.append(entrada("Bigodes Carnívoros", 21300, ['command = "k_bigodes"', chao, "NumProjID(21300) = 0"], especial))
    c.append(entrada("Lavagem", 24100, ['command = "y"', 'command = "holddown"', chao] + perto, ("1",)))
    # kombo Cobaia: ← + a (20280), y, ↓ + b
    c.append(entrada("Cobaia 3", 20342, ['command = "b"', 'command = "holddown"', chao],
                     ("stateno = 20341 && movecontact",)))
    c.append(entrada("Cobaia 2", 20341, ['command = "y"', 'command != "holddown"', chao],
                     ("stateno = 20280 && movecontact",)))
    # correntes: o 2º, o 3º e o finalizador
    for b, (g2, g3, gf) in CORRENTES.items():
        p = PRIMEIRO[b]
        c.append(entrada(f"corrente {b} final", gf.estado, [f'command = "{b}"', 'command != "holddown"', em_pe],
                         (f"stateno = {g3.estado} && movehit",)))
        c.append(entrada(f"corrente {b} 3", g3.estado, [f'command = "{b}"', 'command != "holddown"', em_pe],
                         (f"stateno = {g2.estado} && movecontact",)))
        c.append(entrada(f"corrente {b} 2", g2.estado, [f'command = "{b}"', 'command != "holddown"', em_pe],
                         (f"stateno = {p} && movecontact",)))
    # normais: direcionais, agachados, no ar e em pé
    for g in NORMAIS:
        b = re.search(r"(?<![a-z])([xyab])(?![a-z])", g.comando).group(1)
        if g.comando.startswith("→"):
            conds = [f'command = "{b}"', 'command = "holdfwd"', 'command != "holddown"', em_pe]
        elif g.comando.startswith("←"):
            conds = [f'command = "{b}"', 'command = "holdback"', 'command != "holddown"', em_pe]
        elif g.tipo == "C":
            conds = [f'command = "{b}"', 'command = "holddown"', chao]
        elif g.tipo == "A":
            conds = [f'command = "{b}"', "statetype = A"]
        else:
            conds = [f'command = "{b}"', 'command != "holddown"', em_pe]
        c.append((g, entrada(g.nome, g.estado, conds)))
    # direcionais antes dos neutros do mesmo botão
    fixos = [x for x in c if isinstance(x, str)]
    norm = [x for x in c if not isinstance(x, str)]
    norm.sort(key=lambda x: 0 if x[0].comando[0] in "→←" else 1)
    return "".join(fixos) + "".join(t for _, t in norm)


def ligar_cmd(cmd):
    nl = "\r\n" if "\r\n" in cmd else "\n"
    cmd = cmd.replace("\r\n", "\n")
    # tira o que este script pôs antes
    cmd = re.sub(rf"\[State -1, [^\]]*{re.escape(MARCA)}\]\n.*?\n\n", "", cmd, flags=re.S)
    cmd = re.sub(r'\[Command\]\nname = "k_[a-z_]+"\n.*?\n\n', "", cmd, flags=re.S)
    cmd = cmd.replace(TRAVA + "\n", "")
    # comandos novos, antes do primeiro [Command]
    i = cmd.index("[Command]")
    cmd = cmd[:i] + "".join(f'[Command]\nname = "{k}"\ncommand = {v}\ntime = {30 if k == "k_cirurgia" else 20}\n\n'
                            for k, v in COMANDOS.items()) + cmd[i:]
    cab, corpo = cmd.split("[Statedef -1]", 1)
    blocos = re.split(r"(?m)^(?=\[State -1)", corpo)
    novos = [blocos[0]]
    tirados = []
    for b in blocos[1:]:
        tipo = re.search(r"(?m)^type\s*=\s*(\w+)", b)
        val = re.search(r"(?m)^value\s*=\s*(-?\d+)", b)
        if not tipo or tipo.group(1).lower() != "changestate" or not val:
            novos.append(b)
            continue
        v = int(val.group(1))
        if v in MECANICA or "(despertados_47.py)" in b:
            novos.append(b)
            continue
        if re.search(r"(?m)^triggerall = var\(20\) > 0\s*$", b):
            tirados.append(re.match(r"\[State -1, ([^\]]*)\]", b).group(1))  # golpe antigo do despertado (Pengaró)
            continue
        if "var(20) = 0" not in b:
            # a trava entra junto dos outros triggerall, antes do 1º trigger
            m = re.search(r"(?m)^trigger1\s*=", b)
            b = b[:m.start()] + TRAVA + "\n" + b[m.start():] if m else b
        novos.append(b)
    corpo = "".join(novos)
    # o kit entra logo no começo do [Statedef -1], depois do poder da #47
    m = re.search(r"\[State -1, Poder de longe do despertado \(despertados_47\.py\)\].*?\n\n", corpo, re.S)
    j = m.end() if m else corpo.index("\n") + 1
    if not m:
        corpo = "\n" + corpo.lstrip("\n")
        j = 1
    corpo = corpo[:j] + bloco_cmd() + corpo[j:]
    cmd = cab + "[Statedef -1]" + corpo
    return cmd.replace("\n", nl), tirados


# ---------------------------------------------------------------------------------------------- tudo
MOVELIST = """<#f0f000>:Surto de Tesoura: Cientista Louco e A Cliente (kit todo próprio):</>
Peruca Viva <#bebebe>(projétil pelo chão)</>		_D_F^X / _D_F^Y
Pescoço de Borracha <#bebebe>(y puxa)</>		_D_B^X / _D_B^Y
Tanque Estourado		_F_D^A / _F_D^B
Bigodes Carnívoros <#bebebe>(vários acertos)</>		_B_F^B
Sala de Cirurgia <#bebebe>(super, 2000)</>		_B_F_D^Y
Lavagem <#bebebe>(agarrão baixo)</>		_D+^Y
Transplante <#bebebe>(agarrão de comando)</>		_F_D_F^Y
Por cima / Pisão de Choque		_F+^Y / _F+^B
Bafo do Secador / Puxa pela Gola		_B+^X / _B+^A
Tesourinha / Navalha Comprida		^X^X^X^X / ^Y^Y^Y^Y
Tubo Chicote / Pião da Cadeira		^A^A^A^A / ^B^B^B^B
Kombo Cobaia		_B+^A, ^Y, _D+^B
"""


def ligar_movelist(texto):
    """Troca a seção do despertado pela do kit e tira o super do normal que não sai mais no Surto."""
    texto = re.sub(r"<#f0f000>:(Exclusivos do Surto de Tesoura|Surto de Tesoura: Cientista Louco)[^\n]*\n(?:[^\n]+\n)*",
                   MOVELIST.replace("\\", "\\\\"), texto, count=1)
    return re.sub(r"(?m)^Último Cliente \(no Surto de Tesoura\)[^\n]*\n", "", texto)


def aplicar(pasta=None, so_cmd=False, com_cmd=True):
    pasta = Path(pasta) if pasta else RAIZ / "chars" / "raiclaven"
    pa, pc, pm = (pasta / f"raiclaven.{e}" for e in ("air", "cns", "cmd"))
    if not so_cmd:
        air, cns = aplicar_air_cns(pa.read_text(encoding="utf-8"), pc.read_text(encoding="utf-8"))
        cns = remap_parado(cns, air)
        n = sprites_pecas(pasta / "raiclaven.sff") if anims_pecas() else 0
        print(f"raiclaven: {n} desenhos do corpo firme no .sff ({', '.join(anims_pecas())})")
        pa.write_text(air, encoding="utf-8", newline="\n")
        pc.write_text(cns, encoding="utf-8", newline="\n")
    mv = pasta / "movelist.dat"
    if mv.exists():
        mv.write_text(ligar_movelist(mv.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    tirados = []
    if com_cmd:
        cmd, tirados = ligar_cmd(pm.read_bytes().decode("utf-8"))
        pm.write_bytes(cmd.encode("utf-8"))
    print(f"raiclaven: kit próprio do despertado com {len(TODOS) + len(AGARROES)} golpes"
          + ("" if so_cmd else f" ({len(TODOS)} ações + {len(AGARROES)} agarrões)")
          + f"; {len(tirados)} golpes antigos do despertado saíram do .cmd")


def lista():
    for g in TODOS:
        print(f"{g.estado:6d}  {g.nome:34s} {g.comando:28s} folha {g.folha:12s} provisória {g.fonte}")
    for n, (nome, _, _, cmdo) in AGARROES.items():
        print(f"{n:6d}  {nome:34s} {cmdo}")


if __name__ == "__main__":
    if "--lista" in sys.argv:
        lista()
    else:
        aplicar(so_cmd="--cmd" in sys.argv)
