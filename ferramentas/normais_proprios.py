#!/usr/bin/env python3
"""Normais com cara própria (auditoria do Breno, #32, 24/11, item 9) e o quadro congelado no contato (item 6, achado
da ferramentas/regua_sff.py).

  python3 ferramentas/normais_proprios.py               aplica nos 4 lutadores do PERFIL
  python3 ferramentas/normais_proprios.py gutto         só esse
  python3 ferramentas/normais_proprios.py --conferir    sai com erro se falta aplicar em algum golpe

O Breno viu que Pengaró, Gutto e Raiclaven tinham os normais idênticos (tempo e dano), e CK e Gbzin também entre si.
Sugestão dele: "dar uma cara a cada um (Gutto lento e forte...)". Sem desenho novo, a cara vem dos números:

  lutador    dano dos normais   volta do golpe (tiques a mais no fim)   ideia
  pengaro    igual (a base)     igual                                   capoeirista equilibrado
  gutto      +15%               +2                                      boxeador pesado: bate forte, demora a voltar
  raiclaven  -8%                -1                                      tesoura rápida: bate menos, volta antes
  ck         -8%                -1                                      moleque ligeiro: pressão, golpe curto
  gbzin      +8%                +1                                      malandro de pancada: um pouco mais pesado

A volta muda a vantagem no acerto e na defesa no mesmo tanto; depois de aplicar, meça (vantagem.py) e corrija a trava
da defesa (calibrar_guarda.py --ajuste) para a defesa seguir a regra.

CONGELADO: o quadro do contato ficava parado 10 a 17 tiques (o mesmo sprite repetido, com e sem caixa de ataque).
Aqui sai só o pedaço parado DEPOIS da caixa de ataque (vai para os quadros da volta, que vêm logo depois; o golpe dura o
mesmo tanto). O preparo e a caixa de ataque não mudam: a 1ª versão encurtava a caixa e o 311 do CK parou de encostar
na corrente (robô). O resto do parado é o tempo em que o golpe pega, e só some com um desenho novo de acompanhamento.

Mexe nos normais em pé, agachado e corrente (200 a 499 e 3410 a 3499); aéreo não (a volta dele é a queda). Guarda os
valores de antes num comentário (`; normais proprios base ...`), então pode rodar quantas vezes quiser. Chamado no
fim dos gerar_<lutador>.py, antes do mecanica.py.
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PERFIL = {
    "pengaro": dict(dano=1.0, volta=0),
    "gutto": dict(dano=1.15, volta=2),
    "raiclaven": dict(dano=0.92, volta=-1),
    "ck": dict(dano=0.92, volta=-1),
    "gbzin": dict(dano=1.08, volta=1),
}
MARCA = "; normais proprios base"
CONGELA_MAX, CONGELA_LIMITE = 6, 10


def _normal(n):
    return 200 <= n <= 499 or 3410 <= n <= 3499


def _elementos(corpo):
    """Linhas da ação -> lista de (índice da linha, g, i, x, y, tiques, tem_clsn1). Clsn1 vale só para o elemento
    logo depois do bloco (sem Clsn1Default nos normais; se houver, a ação fica como está)."""
    linhas = corpo.split("\n")
    els, clsn1 = [], False
    for k, ln in enumerate(linhas):
        s = ln.strip()
        if s.lower().startswith("clsn1default"):
            return linhas, None
        if s.lower().startswith("clsn1:"):
            clsn1 = True
            continue
        m = re.match(r"^(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)(.*)$", s)
        if m:
            g, i, x, y, t = (int(v) for v in m.groups()[:5])
            els.append([k, g, i, x, y, t, clsn1])
            clsn1 = False
    return linhas, els


def descongelar(ticks, els, hit_time=None):
    """Sequência do mesmo sprite (>= CONGELA_LIMITE tiques): o pedaço parado depois da caixa de ataque cai para o
    mínimo (até CONGELA_MAX no total) e os tiques vão para a volta. Preparo e caixa de ataque não mudam (`hit_time`
    fica para quem quiser conferir o tique do HitDef)."""
    t = list(ticks)
    k = 0
    while k < len(els):
        j = k
        while j + 1 < len(els) and els[j + 1][1:5] == els[k][1:5]:
            j += 1
        run = list(range(k, j + 1))
        total = sum(t[q] for q in run)
        depois = [q for q in range(j + 1, len(els)) if t[q] > 0]
        ativos = [q for q in run if els[q][6]]
        if len(run) > 1 and total >= CONGELA_LIMITE and depois:
            # só o que vem depois do 1º quadro com caixa (ou o run inteiro, se não tem caixa)
            corte = [q for q in run if not ativos or q >= ativos[0]]
            fixo = sum(t[q] for q in run if q not in corte)
            alvo = max(CONGELA_MAX - fixo, 1)
            ativo = sum(t[q] for q in ativos)
            piso_ativo = ativo  # a caixa de ataque fica inteira: o alcance da corrente depende dela (CK 311 no robô)
            sobra = sum(t[q] for q in corte) - alvo
            for q in [q for q in reversed(corte) if not els[q][6]] + [q for q in reversed(corte) if els[q][6]]:
                if sobra <= 0:
                    break
                if els[q][6]:
                    tira = min(sobra, t[q] - 1, ativo - piso_ativo)
                    ativo -= max(tira, 0)
                else:
                    tira = min(sobra, t[q] - 1)
                if tira > 0:
                    t[q] -= tira
                    sobra -= tira
            tirado = sum(ticks[q] for q in corte) - sum(t[q] for q in corte)
            q = 0
            while tirado > 0:
                t[depois[q % len(depois)]] += 1
                tirado -= 1
                q += 1
        k = j + 1
    return t


def ajustar_air(air, perfil, hits=None):
    trocas = 0
    partes = re.split(r"(?m)^(?=\[Begin Action )", air)
    for p, bloco in enumerate(partes):
        m = re.match(r"\[Begin Action (\d+)\]", bloco)
        if not m or not _normal(int(m.group(1))):
            continue
        linhas, els = _elementos(bloco)
        if not els:
            continue
        base = None
        for ln in linhas:
            if ln.startswith(MARCA):
                base = [int(v) for v in ln[len(MARCA):].split(",")]
        if base is None or len(base) != len(els):
            base = [e[5] for e in els]
        t = descongelar(base, els, (hits or {}).get(int(m.group(1))))
        if perfil["volta"] and t[-1] > 0:
            # volta: no fim; tirar tique sai do quadro mais longo da volta (depois da última caixa de ataque)
            ult = max([q for q, e in enumerate(els) if e[6]], default=-1)
            volta = [q for q in range(ult + 1, len(els)) if t[q] > 0]
            if perfil["volta"] > 0:
                t[-1] += perfil["volta"]
            elif volta:
                for _ in range(-perfil["volta"]):
                    q = max(volta, key=lambda v: t[v])
                    if t[q] > 1:
                        t[q] -= 1
        if t == [e[5] for e in els] and base == [e[5] for e in els]:
            continue
        for q, e in enumerate(els):
            ln = linhas[e[0]]
            linhas[e[0]] = re.sub(r"^(\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+\s*,\s*)-?\d+", rf"\g<1>{t[q]}", ln)
        linhas = [ln for ln in linhas if not ln.startswith(MARCA)]
        cab = linhas[0]
        linhas = [cab, f"{MARCA} {','.join(str(v) for v in base)}"] + linhas[1:]
        novo = "\n".join(linhas)
        if novo != bloco:
            partes[p] = novo
            trocas += 1
    return "".join(partes), trocas


def tempos_hitdef(cns):
    """Statedef -> menor Time do HitDef (trigger1 = Time = N ou Time = [a, b])."""
    out = {}
    for m in re.finditer(r"(?ms)^\[Statedef (-?\d+)\](.*?)(?=^\[Statedef |\Z)", cns):
        for p in re.split(r"(?m)^(?=\[State )", m.group(2)):
            if re.search(r"(?m)^type\s*=\s*HitDef\s*$", p):
                for v in re.findall(r"(?mi)^trigger\w*\s*=.*?\bTime\s*=\s*\[?\s*(\d+)", p):
                    n = int(m.group(1))
                    out[n] = min(out.get(n, 999), int(v))
    return out


def ajustar_cns(cns, perfil):
    trocas = 0
    marcas = [(m.start(), int(m.group(1))) for m in re.finditer(r"(?m)^\[Statedef (-?\d+)\]", cns)]
    pedacos, fim = [], len(cns)
    for k in range(len(marcas) - 1, -1, -1):
        ini, n = marcas[k]
        bloco = cns[ini:fim]
        if _normal(n):
            def troca(m):
                nonlocal trocas
                a, b = int(m.group(2)), int(m.group(3))
                if m.group(4):
                    a, b = (int(v) for v in m.group(4).split(","))
                na, nb = round(a * perfil["dano"]), round(b * perfil["dano"])
                trocas += 1
                if perfil["dano"] == 1.0:
                    return f"{m.group(1)}{a}, {b}"
                return f"{m.group(1)}{na}, {nb} ; normais proprios base {a},{b}"
            bloco = re.sub(r"(?m)^(damage\s*=\s*)(\d+)\s*,\s*(\d+)[ \t]*(?:; normais proprios base (\d+,\d+))?[ \t]*$",
                           troca, bloco)
        pedacos.append(bloco)
        fim = ini
    return cns[:fim] + "".join(reversed(pedacos)), trocas


def aplicar(lutador, pasta=None):
    perfil = PERFIL.get(lutador)
    if not perfil:
        return 0, 0
    pasta = Path(pasta) if pasta else RAIZ / "chars" / lutador
    pa, pn = pasta / f"{lutador}.air", pasta / f"{lutador}.cns"
    cns0 = pn.read_text(encoding="utf-8").replace("\r\n", "\n")
    air, ta = ajustar_air(pa.read_text(encoding="utf-8").replace("\r\n", "\n"), perfil, tempos_hitdef(cns0))
    cns, tc = ajustar_cns(cns0, perfil)
    pa.write_text(air, encoding="utf-8", newline="\r\n" if b"\r\n" in pa.read_bytes() else "\n")
    pn.write_text(cns, encoding="utf-8", newline="\r\n" if b"\r\n" in pn.read_bytes() else "\n")
    return ta, tc


def conferir(lutador):
    """Ação normal cujo tempo não é o que o aplicar() daria (a ferramenta não rodou depois da última geração)."""
    pasta = RAIZ / "chars" / lutador
    air = (pasta / f"{lutador}.air").read_text(encoding="utf-8").replace("\r\n", "\n")
    cns = (pasta / f"{lutador}.cns").read_text(encoding="utf-8").replace("\r\n", "\n")
    novo, _ = ajustar_air(air, PERFIL[lutador], tempos_hitdef(cns))
    ruins = []
    for a, b in zip(re.split(r"(?m)^(?=\[Begin Action )", air), re.split(r"(?m)^(?=\[Begin Action )", novo)):
        if a != b:
            ruins.append(re.match(r"\[Begin Action (\d+)\]", a).group(1))
    return ruins


def main():
    nomes = [a for a in sys.argv[1:] if not a.startswith("--")] or list(PERFIL)
    erro = False
    for l in nomes:
        if "--conferir" in sys.argv:
            r = conferir(l)
            print(f"{l}: {'ok' if not r else 'falta aplicar: ' + ', '.join(r)}")
            erro |= bool(r)
        else:
            ta, tc = aplicar(l)
            print(f"{l}: {ta} ações com o tempo mexido, {tc} danos")
    sys.exit(1 if erro else 0)


if __name__ == "__main__":
    main()
