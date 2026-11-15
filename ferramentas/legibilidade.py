#!/usr/bin/env python3
"""Golpes legíveis (issue #45 do Breno: "tem hora que os lutadores batem e o Breno não entende nada").

  python3 ferramentas/legibilidade.py [lutador ...]      (sem nome: os cinco) reescreve chars/<l>/<l>.air e .cns
  python3 ferramentas/legibilidade.py --conferir         (só diz o que mudaria)

Pós-passo como o parry.py e o agarrao_mk.py: mexe direto nos arquivos do lutador, sem desenho novo, e é idempotente
(só sobe o que está abaixo do piso e só encurta o que passa do limite; rodar de novo não muda nada). Os gerar_*.py
chamam `aplicar` no fim. O que ele conserta, pela seção 8.3 das regras e pela #45:

  contato     a caixa de golpe (Clsn1) não passa mais de 12 px do membro desenhado no quadro (nem do endiabrado que
              o RemapPreset põe no lugar). Golpe que "bate no ar" longe do punho ou do pé deixa de existir. Caixa
              que fica toda atrás do membro, ou de estado que solta projétil/ajudante, não é mexida (vai para a
              tabela da revisão).
  congela     pausetime (o congelamento no contato) no piso: fraco 7, forte 11, finalizador/super 14. Golpes do meio
              de uma rajada (vários HitDefs no mesmo estado) ficam como estão.
  treme       tremida no contato (envshake do HitDef, só quando acerta): forte pequena, finalizador maior.
  reação      animtype casado com a força: fraco Light, forte Medium (ou Hard/Back se já era), finalizador Hard
              (ou Back/Up/DiagUp se já era).
  baixo       golpe só-baixo (guardflag L) faz o oponente reagir baixo (ground.type = Low).
  faísca      a faísca nasce na altura da caixa de golpe (sparkxy y dentro da faixa da Clsn1).
  preparo     o golpe mostra a intenção antes de bater: a pose de carga (último quadro antes da caixa) fica mais
              tempo até o preparo chegar no piso (fraco 3, forte 7, finalizador 10 ticks; até 6 ticks a mais), e os
              gatilhos de Time do estado andam junto para o HitDef cair no contato.

A força vem de auditar_golpes.forca. A conferência de tudo é `python3 ferramentas/auditar_golpes.py`.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auditar_golpes as ag  # noqa: E402
import conferir_sff  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
TREME = {"forte": ("6", "-2"), "final": ("12", "-4")}  # envshake.time, envshake.ampl
REACAO = {"fraco": "Light", "forte": "Medium", "final": "Hard"}


def remap(cns):
    m = re.search(r"^\[RemapPreset despertado\]\n(.*?)(?=^\[|\Z)", cns, re.M | re.S)
    if not m:
        return {}
    return {(int(a), int(b)): (int(c), int(d))
            for a, b, c, d in re.findall(r"^(\d+),\s*(\d+)\s*=\s*(\d+),\s*(\d+)", m.group(1), re.M)}


def estados_protegidos(cns):
    """Estados que soltam projétil ou ajudante: a caixa do corpo pode ser de propósito maior (o efeito bate)."""
    out = set()
    for n, corpo in ag.estados(cns).items():
        if re.search(r"^\s*type\s*=\s*(Projectile|Helper)\s*$", corpo, re.M | re.I):
            out.add(n)
    return out


def anims_por_estado(cns):
    """{ação: {estados}}: a ação do Statedef e as de ChangeAnim dentro dele."""
    out = {}
    for n, corpo in ag.estados(cns).items():
        for v in re.findall(r"^\s*anim\s*=\s*(\d+)\s*$", corpo.split("\n[State")[0], re.M):
            out.setdefault(int(v), set()).add(n)
        for b in re.split(r"(?m)^(?=\[State )", corpo):
            if re.search(r"^\s*type\s*=\s*ChangeAnim\s*$", b, re.M | re.I):
                v = re.search(r"^\s*value\s*=\s*(\d+)\s*$", b, re.M)
                if v:
                    out.setdefault(int(v.group(1)), set()).add(n)
    return out


def aparar_air(air, mask, pares, escala, protegidas, log):
    """Encosta a frente de cada Clsn1 no membro + 12 px (1x). Vale para Clsn1 de quadro e Clsn1Default."""
    limite = ag.SOBRA * escala
    saida = []
    for bloco in re.split(r"(?m)^(?=\[Begin Action )", air):
        m = re.match(r"\[Begin Action (\d+)\]", bloco)
        if not m or int(m.group(1)) in protegidas or not re.search(r"(?mi)^\s*clsn1", bloco):
            saida.append(bloco)
            continue
        acao = int(m.group(1))
        linhas = bloco.split("\n")
        # para cada linha de Clsn1, os elementos que ela cobre (o próximo elemento; o Default cobre todos que não
        # têm Clsn1 próprio)
        grupos, atual, modo, padrao, els_padrao = [], None, None, None, []
        for k, ln in enumerate(linhas):
            s = ln.split(";")[0].strip()
            cab = re.match(r"(clsn[12])(default)?\s*:", s, re.I)
            if cab:
                modo = (cab.group(1).lower(), bool(cab.group(2)))
                if modo == ("clsn1", True):
                    padrao = []
                elif modo == ("clsn1", False):
                    atual = []
                continue
            if re.match(r"clsn1\s*\[", s, re.I) and modo and modo[0] == "clsn1":
                (padrao if modo[1] else atual).append(k)
                continue
            e = ag.RE_ELEM.match(s)
            if e:
                g, i, x, y = (int(v) for v in e.groups()[:4])
                resto = e.group(6)
                flip = resto.split(",")[1].strip().upper() if resto.count(",") >= 1 else ""
                el = (g, i, x, y, flip)
                if atual is not None:
                    grupos.append((atual, [el]))
                elif padrao:
                    els_padrao.append(el)
                atual = None
        if padrao:
            grupos.append((padrao, els_padrao))
        mudou = False
        for idx, els in grupos:
            for k in idx:
                mm = re.match(r"(\s*Clsn1\[\s*\d+\s*\]\s*=\s*)(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)(.*)$",
                              linhas[k], re.I)
                if not mm:
                    continue
                x1, y1, x2, y2 = (int(v) for v in mm.groups()[1:5])
                membros = []
                for g, i, x, y, flip in els:
                    for cod in ((g, i), pares.get((g, i))):
                        if cod and cod in mask.sprites:
                            f = mask.frente(cod[0], cod[1], x, y, flip, y1, y2)
                            if f is not None:
                                membros.append(f)
                if not membros:
                    continue
                teto = max(membros) + limite
                frente_box, tras_box = max(x1, x2), min(x1, x2)
                if frente_box <= teto or teto - tras_box < 15 * escala:
                    continue  # já encosta, ou a caixa ficaria fina demais: fica para a revisão
                if x1 >= x2:
                    x1 = teto
                else:
                    x2 = teto
                linhas[k] = f"{mm.group(1)}{x1}, {y1}, {x2}, {y2}{mm.group(6)}"
                mudou = True
                log.append(f"ação {acao}: caixa de golpe encostada no membro (frente {frente_box // escala} -> "
                           f"{teto // escala} px)")
        saida.append("\n".join(linhas) if mudou else bloco)
    return "".join(saida)


def chave(bloco, k):
    m = re.search(rf"(?mi)^\s*{re.escape(k)}\s*=\s*([^;\n]*)", bloco)
    return m.group(1).strip() if m else None


def por(bloco, k, v, depois="damage"):
    """Troca o valor da chave k no bloco (ou acrescenta logo depois da chave `depois`)."""
    if re.search(rf"(?mi)^\s*{re.escape(k)}\s*=", bloco):
        return re.sub(rf"(?mi)^(\s*{re.escape(k)}\s*=\s*)[^;\n]*?(\s*(;[^\n]*)?)$",
                      lambda m: m.group(1) + v + (" " + m.group(3) if m.group(3) else ""), bloco, count=1)
    return re.sub(rf"(?mi)^(\s*{re.escape(depois)}\s*=[^\n]*\n)", lambda m: m.group(1) + f"{k} = {v}\n", bloco,
                  count=1)


def volta_para_si(corpo, n):
    """O estado tem um ChangeState para ele mesmo (golpe de várias passagens, como um super em rajada)."""
    return any(re.search(r"(?mi)^\s*type\s*=\s*ChangeState\s*$", b) and
               re.search(rf"(?mi)^\s*value\s*=\s*{n}\s*$", b) for b in re.split(r"(?m)^(?=\[State )", corpo))


def ajustar_cns(cns, air_acoes, escala, log):
    partes = re.split(r"(?m)^(?=\[Statedef )", cns)
    for pi, parte in enumerate(partes):
        m = re.match(r"\[Statedef (-?\d+)\]", parte)
        if not m:
            continue
        n = int(m.group(1))
        if n < 0 or 800 <= n <= 899 or n >= 5000:
            continue
        cab = parte.split("\n[State")[0]
        am = re.search(r"(?mi)^\s*anim\s*=\s*(\d+)\s*$", cab)
        els = air_acoes.get(int(am.group(1)), []) if am else []
        ys = [v for e in els if e[6] for c in e[6] for v in (c[1], c[3])]
        blocos = re.split(r"(?m)^(?=\[State )", parte)
        hits = [i for i, b in enumerate(blocos) if re.search(r"(?mi)^\s*type\s*=\s*HitDef\s*$", b)]
        for ordem, i in enumerate(hits):
            b = blocos[i]
            attr = (chave(b, "attr") or "").replace(" ", "").upper()
            if "T" in attr.split(",", 1)[-1]:
                continue
            kv = {k: v for k, v in ((k.lower(), chave(b, k)) for k in ("fall", "damage")) if v is not None}
            f = ag.forca(n, kv, False, None)
            # rajada: vários HitDefs no estado, ou o estado que volta para ele mesmo (passagens do super)
            rajada = (len(hits) > 1 and ordem < len(hits) - 1) or volta_para_si(parte, n)
            if rajada and f == "final":
                f = "forte"
            novo = b
            if not rajada:
                p = re.findall(r"-?\d+", chave(b, "pausetime") or "0,0")
                p1, p2 = (int(p[0]), int(p[1])) if len(p) >= 2 else (0, 0)
                piso = ag.PISO_PAUSA[f]
                if p1 < piso or p2 < piso:
                    novo = por(novo, "pausetime", f"{max(p1, piso)}, {max(p2, piso)}")
                at = (chave(b, "animtype") or "Light").lower()
                if at not in ag.REACAO_OK[f]:
                    novo = por(novo, "animtype", REACAO[f])
                if f in TREME and chave(b, "envshake.time") is None:
                    novo = por(novo, "envshake.time", TREME[f][0])
                    novo = por(novo, "envshake.freq", "150", "envshake.time")
                    novo = por(novo, "envshake.ampl", TREME[f][1], "envshake.freq")
            gf = (chave(b, "guardflag") or "MA").upper()
            if "L" in gf and "H" not in gf and (chave(b, "ground.type") or "High").lower() == "high":
                novo = por(novo, "ground.type", "Low")
            sp = re.findall(r"-?\d+", chave(b, "sparkxy") or "")
            if ys and len(sp) == 2:
                lo, hi = min(ys) // escala, max(ys) // escala
                y = int(sp[1])
                if y < lo - 20 or y > hi + 20:
                    novo = por(novo, "sparkxy", f"{sp[0]}, {(lo + hi) // 2}")
            if novo != b:
                log.append(f"estado {n} HitDef {ordem + 1}: " + ", ".join(
                    k for k in ("pausetime", "animtype", "envshake.time", "ground.type", "sparkxy")
                    if chave(novo, k) != chave(b, k)))
                blocos[i] = novo
        partes[pi] = "".join(blocos)
    return "".join(partes)


MAX_PREPARO = 6  # no máximo 6 ticks a mais de preparo por golpe; o que faltar além disso vai para a revisão


def uso_das_acoes(cns):
    """{ação: [(estado, começa no Time 0?)]}: a ação do Statedef começa no Time 0; ChangeAnim só conta como começo
    quando o gatilho é Time = 0 (a variante do Despertar)."""
    out = {}
    for n, corpo in ag.estados(cns).items():
        cab = corpo.split("\n[State")[0]
        am = re.search(r"(?mi)^\s*anim\s*=\s*(\d+)\s*$", cab)
        if am:
            out.setdefault(int(am.group(1)), []).append((n, True))
        for b in re.split(r"(?m)^(?=\[State )", corpo):
            if re.search(r"(?mi)^\s*type\s*=\s*ChangeAnim\s*$", b):
                v = re.search(r"(?mi)^\s*value\s*=\s*(\d+)\s*$", b)
                if v:
                    zero = bool(re.search(r"(?mi)^\s*trigger1\s*=\s*Time\s*=\s*0\s*$", b))
                    out.setdefault(int(v.group(1)), []).append((n, zero))
    return out


RE_TIME = re.compile(r"(?<![A-Za-z.])(Time\s*(?:=|>=|>|<=|<|!=)\s*)(\[\s*(-?\d+)\s*,\s*(-?\d+)\s*\]|-?\d+)", re.I)


def adiar_gatilhos(corpo, desde, delta):
    """Soma delta a todo `Time <op> N` (e `Time = [a, b]`) com N >= desde nas linhas de trigger do estado."""
    def troca(m):
        if m.group(3) is not None:
            a, b = int(m.group(3)), int(m.group(4))
            a, b = a + delta if a >= desde else a, b + delta if b >= desde else b
            return f"{m.group(1)}[{a}, {b}]"
        v = int(m.group(2))
        return m.group(1) + str(v + delta if v >= desde else v)
    linhas = corpo.split("\n")
    for k, ln in enumerate(linhas):
        if re.match(r"\s*trigger(all|\d+)\s*=", ln, re.I):
            linhas[k] = RE_TIME.sub(troca, ln)
    return "\n".join(linhas)


def esticar_preparo(air, cns, protegidas, log):
    """Segura a pose de carga (o último quadro antes da caixa de golpe) até o preparo chegar no piso da força
    (fraco 3, forte 7, finalizador 10 ticks; regra 8.3 e #45 "o golpe mostra a intenção antes de bater"), e adia
    os gatilhos de Time do estado no mesmo tanto, para o HitDef, o som e os efeitos continuarem no contato."""
    acoes = ag.ler_air(air)
    uso = uso_das_acoes(cns)
    sts = ag.estados(cns)
    adiar = {}  # estado -> [(desde, delta)]
    esticar = {}  # ação -> (índice do elemento, delta)
    for n, corpo in sorted(sts.items()):
        if n < 0 or 800 <= n <= 899 or n >= 5000:
            continue
        cab = corpo.split("\n[State")[0]
        am = re.search(r"(?mi)^\s*anim\s*=\s*(\d+)\s*$", cab)
        if not am:
            continue
        a = int(am.group(1))
        hits = [b for b in ag.blocos(corpo) if b[1].get("type", "").lower() == "hitdef"]
        if not hits or a in protegidas or a in esticar or volta_para_si(corpo, n):
            continue
        kv = hits[0][1]
        if "T" in kv.get("attr", "").replace(" ", "").upper().split(",", 1)[-1]:
            continue
        f = ag.forca(n, kv, False, None)
        if len(hits) > 1 and f == "final":
            f = "forte"
        jan = ag.janelas(acoes.get(a, []))
        if not jan:
            continue
        prep = jan[0][0]
        delta = min(MAX_PREPARO, ag.PISO_PREPARO[f] - prep)
        if delta <= 0:
            continue
        # a ação (e a gêmea do Despertar, a+10000) só pode ser esticada se todo estado que a usa começa por ela
        gemeas = [x for x in (a, a + 10000) if x in acoes]
        if any(not zero for x in gemeas for _, zero in uso.get(x, [])):
            continue
        if len(gemeas) == 2 and ag.janelas(acoes[a + 10000])[:1] != jan[:1]:
            continue
        els = acoes[a]
        j0 = next(j for j, e in enumerate(els) if e[6])
        if j0 == 0:
            continue  # sem quadro de preparo para segurar: fica para a revisão
        for x in gemeas:
            esticar[x] = (j0 - 1, delta)
            for est, _ in uso.get(x, []):
                adiar.setdefault(est, set()).add((prep, delta))
        log.append(f"estado {n} (ação {a}): preparo {prep} -> {prep + delta} ticks")
    # .air: soma delta na duração do quadro de carga
    saida = []
    for bloco in re.split(r"(?m)^(?=\[Begin Action )", air):
        m = re.match(r"\[Begin Action (\d+)\]", bloco)
        if not m or int(m.group(1)) not in esticar:
            saida.append(bloco)
            continue
        alvo, delta = esticar[int(m.group(1))]
        linhas, k_el = bloco.split("\n"), -1
        for k, ln in enumerate(linhas):
            e = ag.RE_ELEM.match(ln.split(";")[0].strip())
            if e and not re.match(r"\s*clsn", ln, re.I):
                k_el += 1
                if k_el == alvo:
                    linhas[k] = re.sub(r"^(\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+\s*,\s*)(-?\d+)",
                                       lambda mm: mm.group(1) + str(int(mm.group(2)) + delta), ln)
                    break
        saida.append("\n".join(linhas))
    air = "".join(saida)
    partes = re.split(r"(?m)^(?=\[Statedef )", cns)
    for i, p in enumerate(partes):
        m = re.match(r"\[Statedef (-?\d+)\]", p)
        if m and int(m.group(1)) in adiar:
            for desde, delta in adiar[int(m.group(1))]:
                p = adiar_gatilhos(p, desde, delta)
            partes[i] = p
    return air, "".join(partes)


def aplicar(lutador, pasta=None, gravar=True):
    pasta = Path(pasta) if pasta else RAIZ / "chars" / lutador
    pa, pc = pasta / f"{lutador}.air", pasta / f"{lutador}.cns"
    air, cns = pa.read_text(encoding="utf-8"), pc.read_text(encoding="utf-8")
    escala = 3 if re.search(r"^\s*xscale\s*=\s*0\.33", cns, re.M) else 1
    _, nos, _ = conferir_sff.ler(pasta / f"{lutador}.sff")
    mask = ag.Mascaras(nos)
    usa = anims_por_estado(cns)
    prot = estados_protegidos(cns)
    protegidas = {a for a, ns in usa.items() if ns & prot} | {810}
    log = []
    air2 = aparar_air(air, mask, remap(cns), escala, protegidas, log)
    cns2 = cns
    for _ in range(4):  # uma ação esticada pode liberar outra que dividia estado com ela; repete até parar
        antes = (air2, cns2)
        air2, cns2 = esticar_preparo(air2, cns2, protegidas, log)
        if (air2, cns2) == antes:
            break
    cns2 = ajustar_cns(cns2, ag.ler_air(air2), escala, log)
    if gravar:
        if air2 != air:
            pa.write_text(air2, encoding="utf-8", newline="\n")
        if cns2 != cns:
            pc.write_text(cns2, encoding="utf-8", newline="\n")
    print(f"{lutador}: {len(log)} ajustes de legibilidade")
    return log


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    gravar = "--conferir" not in sys.argv
    for l in args or ag.LUTADORES:
        for linha in aplicar(l, gravar=gravar):
            if "-v" in sys.argv:
                print("  " + linha)


if __name__ == "__main__":
    main()
