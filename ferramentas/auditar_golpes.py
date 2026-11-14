#!/usr/bin/env python3
"""Revisão de todos os golpes (issues #45 e #48 do Breno): mede cada HitDef dos lutadores e diz o que deixa o golpe
confuso, sem abrir o jogo.

  python3 ferramentas/auditar_golpes.py                 (os cinco lutadores; tabela em docs/revisao-golpes/medidas.md)
  python3 ferramentas/auditar_golpes.py ck gutto        (só esses)
  python3 ferramentas/auditar_golpes.py --saida ARQ.md

Para cada HitDef (estado, nome do .cmd, ação do .air) a ferramenta lê o .air e o .sff finais e confere, pela seção
8.3 das regras (preparo, congelamento, tremida, reação) e pela #45 (golpe legível):

  preparo    ticks da ação antes da 1ª caixa de golpe (Clsn1): fraco >= 3, forte >= 7, finalizador/super >= 10
  nao_bate   o HitDef liga depois que a última caixa de golpe já sumiu (o golpe nunca encosta) ou a ação não tem caixa
  longe      a caixa de golpe passa mais de 12 px do membro desenhado no quadro (bate no ar, "encosta longe demais")
  congela    pausetime abaixo do piso: fraco 7, forte 11, finalizador/super 14
  reacao     animtype que não casa com a força (fraco Light, forte Medium/Hard, finalizador Hard/Back/Up)
  baixo      golpe agachado ou só-baixo (guardflag L) com ground.type High: o oponente reage alto num golpe baixo
  faisca     a altura da faísca (sparkxy y) fica a mais de 20 px da faixa da caixa de golpe: estoura longe do contato
  tremida    finalizador/super sem envshake nem fall.envshake

A força sai do próprio golpe: finalizador/super quando derruba (fall = 1) ou é estado 3000+, forte quando o dano é
>= 60 ou a ação é de botão forte (y/b), senão fraco. Agarrões (attr *T) e o 810 (agarrão segura-e-bate) ficam fora
destas réguas: a conferência deles é a de agarrao_mk.py.
"""
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conferir_sff  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
CHARS = RAIZ / "chars"
LUTADORES = ("ck", "gutto", "hazaki", "pengaro", "raiclaven")
NOMES = {"ck": "CK", "gutto": "Gutto", "hazaki": "Hazak", "pengaro": "Pengaró", "raiclaven": "Raiclaven"}
SOBRA = 12          # px (em 1x) de caixa além do membro (regra 8.3, verificar_pengaro.SOBRA_CLSN1)
PISO_PREPARO = {"fraco": 3, "forte": 7, "final": 10}
PISO_PAUSA = {"fraco": 7, "forte": 11, "final": 14}
REACAO_OK = {"fraco": {"light"}, "forte": {"medium", "hard", "heavy", "back"},
             "final": {"hard", "heavy", "back", "up", "diagup"}}

RE_ACAO = re.compile(r"^\[Begin Action (\d+)\][^\n]*\n(.*?)(?=^\[Begin Action|\Z)", re.M | re.S | re.I)
RE_ELEM = re.compile(r"^\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?[\d.]+)(.*)$")
RE_BOX = re.compile(r"=\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)")


def ler_air(texto):
    """{ação: [(grupo, índice, x, y, ticks, flip, [caixas Clsn1])]} com Clsn1Default resolvido."""
    acoes = {}
    for m in RE_ACAO.finditer(texto):
        els, padrao1, atual1, modo = [], [], None, None
        for ln in m.group(2).splitlines():
            s = ln.split(";")[0].strip()
            if not s or s.lower().startswith("loopstart"):
                continue
            cab = re.match(r"(clsn[12])(default)?\s*:\s*(\d+)", s, re.I)
            if cab:
                modo = (cab.group(1).lower(), bool(cab.group(2)))
                if modo == ("clsn1", True):
                    padrao1 = []
                elif modo == ("clsn1", False):
                    atual1 = []
                continue
            if re.match(r"clsn[12]\s*\[", s, re.I):
                if modo and modo[0] == "clsn1":
                    caixa = tuple(int(v) for v in RE_BOX.search(s).groups())
                    (padrao1 if modo[1] else atual1).append(caixa)
                continue
            e = RE_ELEM.match(s)
            if e:
                g, i, x, y, t, resto = e.groups()
                flip = resto.split(",")[1].strip().upper() if resto.count(",") >= 1 else ""
                caixas = atual1 if atual1 is not None else padrao1
                els.append((int(g), int(i), int(x), int(y), int(float(t)), flip, list(caixas)))
                atual1 = None
        acoes[int(m.group(1))] = els
    return acoes


def estados(cns):
    """{n: texto do Statedef}"""
    return {int(m.group(1)): m.group(2) for m in
            re.finditer(r"^\[Statedef (-?\d+)\][^\n]*\n(.*?)(?=^\[Statedef|\Z)", cns, re.M | re.S | re.I)}


def blocos(corpo):
    """[(título, {chave: valor}, texto)] dos controladores do estado (chaves em minúsculas; triggers numerados)."""
    out = []
    for b in re.split(r"(?m)^(?=\[State )", corpo):
        if not b.startswith("[State "):
            continue
        titulo = b.splitlines()[0]
        kv = {}
        for ln in b.splitlines()[1:]:
            ln = ln.split(";")[0]
            if "=" in ln:
                k, v = ln.split("=", 1)
                kv.setdefault(k.strip().lower(), v.strip())
        out.append((titulo, kv, b))
    return out


def nomes_do_cmd(cmd):
    nomes = {}
    for m in re.finditer(r"^\[State -1,\s*([^\]]+)\]\s*\n(.*?)(?=^\[|\Z)", cmd, re.M | re.S):
        v = re.search(r"^\s*value\s*=\s*(\d+)\s*$", m.group(2), re.M)
        if v and re.search(r"type\s*=\s*ChangeState", m.group(2), re.I):
            nomes.setdefault(int(v.group(1)), m.group(1).strip())
    return nomes


def tick_do_gatilho(kv, els):
    """Primeiro tick (Time) em que o HitDef liga, ou None se não der para saber só pelo gatilho."""
    for k in sorted(k for k in kv if k.startswith("trigger")):
        v = kv[k].replace(" ", "").lower()
        m = re.fullmatch(r"time=(\d+)", v) or re.fullmatch(r"time>=(\d+)", v)
        if m:
            return int(m.group(1))
        m = re.fullmatch(r"time=\[(\d+),\d+\]", v)
        if m:
            return int(m.group(1))
        m = re.fullmatch(r"animelem=(\d+)", v)
        if m:
            k_el = int(m.group(1)) - 1
            return sum(max(e[4], 0) for e in els[:k_el])
        if v in ("1", "animtime<0", "!time"):
            return 0
    return None


def janelas(els):
    """[(início, fim)] em ticks de cada trecho com Clsn1."""
    out, t = [], 0
    for e in els:
        dur = e[4] if e[4] > 0 else 30
        if e[6]:
            if out and out[-1][1] == t:
                out[-1] = (out[-1][0], t + dur)
            else:
                out.append((t, t + dur))
        t += dur
    return out


class Mascaras:
    def __init__(self, nos):
        self.sprites = {(n["g"], n["i"]): n for n in nos if not n.get("png")}
        self.cache = {}

    def frente(self, g, i, x0, y0, flip, y1, y2):
        """Pixel opaco mais à frente (eixo x do .air) na faixa vertical y1..y2, nas unidades do .air (3x)."""
        n = self.sprites.get((g, i))
        if n is None:
            return None
        if (g, i) not in self.cache:
            ys, xs = np.nonzero(np.frombuffer(n["px"], np.uint8).reshape(n["h"], n["w"]) > 0)
            self.cache[(g, i)] = (xs - n["x"], ys - n["y"])
        xs, ys = self.cache[(g, i)]
        if "H" in flip:
            xs = -xs
        xs, ys = xs + x0, ys + y0
        faixa = (ys >= min(y1, y2)) & (ys <= max(y1, y2))
        return int(xs[faixa].max()) if faixa.any() else None


def volta_para_si(corpo, n):
    """O estado tem um ChangeState para ele mesmo (golpe de várias passagens, como um super em rajada)."""
    return any(re.search(r"(?mi)^\s*type\s*=\s*ChangeState\s*$", b) and
               re.search(rf"(?mi)^\s*value\s*=\s*{n}\s*$", b) for b in re.split(r"(?m)^(?=\[State )", corpo))


def forca(n, kv, botao_forte, el_stype):
    if kv.get("fall", "0").strip() in ("1",) or n >= 3000:
        return "final"
    dano = int(re.match(r"-?\d+", kv.get("damage", "0") or "0").group())
    if dano >= 60 or botao_forte:
        return "forte"
    return "fraco"


def auditar(lutador):
    pasta = CHARS / lutador
    air = ler_air((pasta / f"{lutador}.air").read_text(encoding="utf-8"))
    cns = (pasta / f"{lutador}.cns").read_text(encoding="utf-8")
    cmd = (pasta / f"{lutador}.cmd").read_text(encoding="utf-8")
    escala = 3 if re.search(r"^\s*xscale\s*=\s*0\.33", cns, re.M) else 1
    _, nos, _ = conferir_sff.ler(pasta / f"{lutador}.sff")
    mask = Mascaras(nos)
    nomes = nomes_do_cmd(cmd)
    linhas = []
    for n, corpo in sorted(estados(cns).items()):
        if n < 0 or 800 <= n <= 899 or n >= 5000:
            continue
        cab = {}
        for ln in corpo.split("\n[State")[0].splitlines():
            if "=" in ln:
                k, v = ln.split(";")[0].split("=", 1)
                cab[k.strip().lower()] = v.strip()
        anim = int(cab["anim"]) if re.fullmatch(r"\d+", cab.get("anim", "")) else None
        stype = cab.get("type", "S").upper()
        bs = blocos(corpo)
        hits = [b for b in bs if b[1].get("type", "").lower() == "hitdef"]
        if not hits:
            continue
        for k, (titulo, kv, _) in enumerate(hits):
            attr = kv.get("attr", "").replace(" ", "").upper()
            if "T" in attr.split(",", 1)[-1]:
                continue  # agarrão
            els = air.get(anim, [])
            jan = janelas(els)
            t_hd = tick_do_gatilho(kv, els)
            botao_forte = re.search(r"\b(y|b)\b", titulo.lower()) is not None
            f = forca(n, kv, botao_forte, stype)
            # golpe do meio de uma rajada (vários HitDefs no estado): sem piso de congelamento, reação e tremida
            rajada = (len(hits) > 1 and k < len(hits) - 1) or volta_para_si(corpo, n)
            if rajada and f == "final":
                f = "forte"
            prob = []
            nome = nomes.get(n, "")
            if not jan:
                if anim is not None:
                    prob.append(("nao_bate", f"a ação {anim} não tem caixa de golpe"))
            else:
                prep = jan[0][0]
                if t_hd is not None and t_hd >= jan[-1][1]:
                    prob.append(("nao_bate", f"HitDef liga no tick {t_hd}, a caixa some no {jan[-1][1]}"))
                if k == 0 and prep < PISO_PREPARO[f]:
                    prob.append(("preparo", f"{prep} ticks antes da caixa ({f}: piso {PISO_PREPARO[f]})"))
                # alcance: no 1º quadro com caixa depois do gatilho
                pior = 0
                for e in els:
                    if not e[6]:
                        continue
                    for c in e[6]:
                        membro = mask.frente(e[0], e[1], e[2], e[3], e[5], c[1], c[3])
                        if membro is None:
                            continue
                        pior = max(pior, (max(c[0], c[2]) - membro) // escala)
                if pior > SOBRA:
                    prob.append(("longe", f"caixa passa {pior} px do membro"))
                ys = [v for e in els if e[6] for c in e[6] for v in (c[1], c[3])]
                sp = re.findall(r"-?\d+", kv.get("sparkxy", ""))
                if ys and len(sp) == 2:
                    y_sp = int(sp[1])
                    lo, hi = min(ys) / escala, max(ys) / escala
                    fora = max(lo - y_sp, y_sp - hi, 0)
                    if fora > 20:
                        prob.append(("faisca", f"faísca em y {y_sp}, caixa de {lo:.0f} a {hi:.0f}"))
            pausa = re.findall(r"-?\d+", kv.get("pausetime", "0,0"))
            p1 = int(pausa[0]) if pausa else 0
            if not rajada and p1 < PISO_PAUSA[f]:
                prob.append(("congela", f"pausetime {p1} ({f}: piso {PISO_PAUSA[f]})"))
            at = kv.get("animtype", "light").lower()
            if not rajada and at not in REACAO_OK[f]:
                prob.append(("reacao", f"animtype {at} num golpe {f}"))
            gf = kv.get("guardflag", "MA").upper()
            gt = kv.get("ground.type", "high").lower()
            if "L" in gf and "H" not in gf and gt == "high":
                prob.append(("baixo", "golpe baixo com ground.type High"))
            if f == "final" and not rajada and "envshake.time" not in kv and not any(
                    b[1].get("type", "").lower() == "envshake" for b in bs):
                prob.append(("tremida", "finalizador sem tremida"))
            linhas.append(dict(lutador=lutador, estado=n, hit=k + 1, nome=nome, anim=anim, forca=f,
                               preparo=jan[0][0] if jan else None, pausa=p1, animtype=at, problemas=prob))
    return linhas


def main():
    args = sys.argv[1:]
    saida = RAIZ / "docs" / "revisao-golpes" / "medidas.md"
    if "--saida" in args:
        i = args.index("--saida")
        saida = Path(args[i + 1])
        del args[i:i + 2]
    lutadores = args or LUTADORES
    todas = []
    for l in lutadores:
        todas += auditar(l)
    cont = {}
    for d in todas:
        for p, _ in d["problemas"]:
            cont[p] = cont.get(p, 0) + 1
    md = ["# Medidas de todos os golpes (ferramentas/auditar_golpes.py)", "",
          f"{len(todas)} HitDefs medidos em {', '.join(NOMES[l] for l in lutadores)}. "
          f"Com algum problema: {sum(1 for d in todas if d['problemas'])}.", "",
          "| Problema | Quantos |", "|---|---|"]
    md += [f"| {p} | {c} |" for p, c in sorted(cont.items(), key=lambda x: -x[1])]
    md += ["", "| Lutador | Estado | Golpe | Força | Preparo | Congela | Reação | O que está errado |",
           "|---|---|---|---|---|---|---|---|"]
    for d in todas:
        if not d["problemas"]:
            continue
        md.append(f"| {NOMES[d['lutador']]} | {d['estado']}{'' if d['hit'] == 1 else '.' + str(d['hit'])} | "
                  f"{d['nome'] or '-'} | {d['forca']} | {d['preparo']} | {d['pausa']} | {d['animtype']} | "
                  + "; ".join(t for _, t in d["problemas"]) + " |")
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:8 + len(cont)]))
    print(f"tabela em {saida}")


if __name__ == "__main__":
    main()
