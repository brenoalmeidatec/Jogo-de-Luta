#!/usr/bin/env python3
"""Prende a aura do Despertar ao corpo: asas, garanhão, elos e o resto acompanham o lutador em todo estado (issue #51).

  python3 ferramentas/aura_no_corpo.py [lutador ...]        mede e liga em chars/<l>/<l>.cns (sem nome: todos com aura)
  python3 ferramentas/aura_no_corpo.py --conferir PASTA l    confere o aura_log.txt do ferramentas/filmar_aura_corpo.py
  python3 ferramentas/aura_no_corpo.py --robo [lutador ...]  roda o roteiro no motor (sem filme) e confere

O defeito (Breno, 2026-11-14): as camadas do ferramentas/aura.py nascem presas ao EIXO do lutador (os pés) numa posição
fixa. O eixo não se mexe quando ele agacha, cai ou deita, só o desenho muda; então as asas do Diabo Loiro ficavam no
ar, na altura de quem está em pé, com o corpo no chão.

O conserto é um pós-passo, como o parry.py e o efeitos.py: trabalha em cima do que já está em chars/<l>/ e pode rodar
quantas vezes for (refaz o próprio bloco). Quem regrava o [Statedef -4] da aura chama `aplicar` no fim.

  1. Mede, em cada desenho de cada ação do .air (no sprite do despertado, quando o RemapPreset troca), onde o corpo
     está: o PEITO (centro da metade de cima da massa do desenho; braço erguido e arma pesam pouco), o centro do corpo
     e a altura. Tudo relativo ao parado (ação 0), em px do jogo.
  2. Escreve no [Statedef -4] uma tabela por ação/elemento (trechos vizinhos iguais viram um só gatilho) que diz o alvo
     daquele tique, e quatro maps que correm atrás do alvo com atraso curto (o movimento secundário: a asa chega um
     instante depois do corpo):
        au_<nome>_ax, _ay   deslocamento do peito          au_<nome>_bx   deslocamento do centro (camadas de chão)
        au_<nome>_g         0 em pé .. 1 deitado: quanto a camada recolhe
  3. Troca a posição e a escala de cada camada (o controlador "move" do aura.py):
        camada do corpo (asas, garanhão, elos soltos): segue o peito, e recolhe (encolhe em volta do peito) com g;
        camada do chão (brasa, crateras, anel, névoa, coluna, paredão): continua no chão, mas anda em x com o corpo;
        a coluna e o paredão (mais altos que o lutador) baixam quando ele cai, em vez de ficar de pé sobre o corpo.

Conferência (--conferir, --robo): em todo tique do roteiro, o ponto do peito de cada camada do corpo tem de ficar perto
do peito medido no desenho que está na tela. Aceite: percentil 95 <= 12 px, pior tique <= 45 px e no máximo 4 tiques
seguidos a mais de 20 px (o tranco de um pouso ou de um golpe, que o atraso alcança logo); camada de chão a <= 6 px
do chão.
"""
import argparse
import io
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conferir_sff as cs  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
LUTADORES = ("hazaki", "gutto", "pengaro", "ck")
INICIO, FIM = "; >>> aura_no_corpo.py", "; <<< aura_no_corpo.py"
ORIG = "; aura_no_corpo.py, antes: "
PASSO, PASSO_B, NIVEIS = 2, 4, 8  # px por degrau do peito, do centro, e degraus do recolher
ATRASO = 0.45                     # fração do caminho que a camada anda por tique
RECOLHE = 0.5                     # deitado, a camada do corpo fica com (1 - RECOLHE) do tamanho
SOBE = 22                         # px que a camada recolhida sobe, para não entrar no chão
ALTA, BAIXA = 120, 0.45           # camada de chão com desenho de ALTA px ou mais perde BAIXA da altura com ele deitado
ZERO = 64 + 128 * 64 + 131072 * 32


# ------------------------------------------------------------------------------------------------------------ medida
def ler_air(texto):
    """{ação: [(grupo, índice, x, y, espelhado)]} na ordem dos elementos."""
    acoes, atual = {}, None
    for linha in texto.splitlines():
        m = re.match(r"\s*\[Begin Action (-?\d+)\]", linha, re.I)
        if m:
            atual = acoes.setdefault(int(m.group(1)), [])
            continue
        m = re.match(r"\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*(?:,\s*([HVhv]*))?", linha)
        if m and atual is not None:
            g, i, x, y, _ = (int(v) for v in m.groups()[:5])
            atual.append((g, i, x, y, "h" in (m.group(6) or "").lower()))
    return acoes


def _remap(cns):
    bloco = re.search(r"^\[RemapPreset despertado\]\n(.*?)(?=^\[)", cns, re.M | re.S)
    pares = {}
    for a, b, c, d in re.findall(r"^(\d+)\s*,\s*(\d+)\s*=\s*(\d+)\s*,\s*(\d+)", bloco.group(1) if bloco else "", re.M):
        pares[(int(a), int(b))] = (int(c), int(d))
    return pares


class Corpo:
    """As medidas do corpo do lutador despertado, por (ação, elemento)."""

    def __init__(self, pasta, lutador):
        self.cns = (pasta / f"{lutador}.cns").read_text(encoding="utf-8").replace("\r\n", "\n")
        self.acoes = ler_air((pasta / f"{lutador}.air").read_text(encoding="utf-8"))
        _, nos, _ = cs.ler(pasta / f"{lutador}.sff")
        self.nos = {}
        for n in nos:
            self.nos.setdefault((n["g"], n["i"]), n)
        self.remap = _remap(self.cns)
        m = re.search(r"^xscale\s*=\s*([\d.]+)", self.cns, re.M)
        self.escala = float(m.group(1)) if m else 1.0
        self._cache = {}
        ref = [v for v in (self.pontos(0, e) for e in range(1, len(self.acoes[0]) + 1)) if v]
        self.ref = tuple(float(np.mean([r[k] for r in ref])) for k in range(5))  # px, py, cx, cy, altura

    def _mascara(self, chave):
        if chave not in self._cache:
            n = self.nos.get(self.remap.get(chave, chave)) or self.nos.get(chave)
            if n is None or n["w"] * n["h"] == 0:
                self._cache[chave] = None
            else:
                if n.get("png"):
                    cru = n["px"][n["px"].index(b"\x89PNG"):]  # o .sff guarda 4 bytes de tamanho antes do PNG
                    m = np.asarray(Image.open(io.BytesIO(cru)).convert("RGBA"))[..., 3] > 0
                else:
                    m = np.frombuffer(n["px"], np.uint8).reshape(n["h"], n["w"]) != 0
                ys, xs = np.nonzero(m)
                self._cache[chave] = None if len(xs) < 30 else ((xs - n["x"]) * self.escala, (ys - n["y"]) * self.escala)
        return self._cache[chave]

    def pontos(self, acao, elem):
        """(peito x, peito y, centro x, centro y, altura) do desenho do elemento (1..n), em px do jogo a partir do eixo;
        x para a frente do lutador, y para baixo. None se o elemento não tem corpo."""
        els = self.acoes.get(acao)
        if not els or not 1 <= elem <= len(els):
            return None
        g, i, ox, oy, esp = els[elem - 1]
        m = self._mascara((g, i))
        if m is None:
            return None
        xs, ys = (-m[0] if esp else m[0]) + ox * self.escala, m[1] + oy * self.escala
        cima = ys <= np.median(ys)
        altura = float(np.percentile(ys, 97) - np.percentile(ys, 3))
        return float(xs[cima].mean()), float(ys[cima].mean()), float(xs.mean()), float(ys.mean()), altura

    def alvo(self, acao, elem):
        """(ax, ay, g, bx) do elemento, relativo ao parado; None se não tem corpo."""
        p = self.pontos(acao, elem)
        if p is None:
            return None
        rel = p[4] / self.ref[4]
        g = float(np.clip((0.62 - rel) / 0.27, 0, 1))
        return p[0] - self.ref[0], p[1] - self.ref[1], g, p[2] - self.ref[2]

    def peito(self):
        return self.ref[0], self.ref[1]


def _degraus(v):
    ax, ay, g, bx = v
    return (int(np.clip(round(ax / PASSO), -63, 63)), int(np.clip(round(ay / PASSO), -63, 63)),
            int(np.clip(round(g * (NIVEIS - 1)), 0, NIVEIS - 1)), int(np.clip(round(bx / PASSO_B), -31, 31)))


def tabela(corpo, ids_da_aura):
    """{valor empacotado: [gatilhos]}: um trecho por ação enquanto os elementos vizinhos ficam a menos de 5 px (e 0,2
    de recolher) uns dos outros. O que dá igual ao parado não entra (é o valor de partida)."""
    saida = {}
    for acao, els in sorted(corpo.acoes.items()):
        if acao in ids_da_aura or acao < 0:
            continue
        alvos, ultimo = [], None
        for e in range(1, len(els) + 1):
            ultimo = corpo.alvo(acao, e) or ultimo
            alvos.append(ultimo)
        if not any(alvos):
            continue
        primeiro = next(a for a in alvos if a)
        alvos = [a or primeiro for a in alvos]
        trechos, ini = [], 0
        for e in range(1, len(alvos) + 1):
            if e < len(alvos):
                bloco = np.array(alvos[ini:e + 1])
                folga = bloco.max(0) - bloco.min(0)
                if folga[0] <= 5 and folga[1] <= 5 and folga[2] <= 0.2 and folga[3] <= 8:
                    continue
            trechos.append((ini + 1, e, _degraus(np.array(alvos[ini:e]).mean(0))))
            ini = e
        for a, b, (qx, qy, qg, qb) in trechos:
            valor = (qx + 64) + 128 * (qy + 64) + 16384 * qg + 131072 * (qb + 32)
            if valor == ZERO:
                continue
            if a == 1 and b == len(alvos):
                gat = f"Anim = {acao}"
            elif a == b:
                gat = f"Anim = {acao} && AnimElemNo(0) = {a}"
            else:
                gat = f"Anim = {acao} && AnimElemNo(0) = [{a}, {b}]"
            saida.setdefault(valor, []).append(gat)
    return saida


# -------------------------------------------------------------------------------------------------------------- .cns
def aura_do_cns(cns):
    m = re.search(r"Aura animada '(\w+)' \(ferramentas/aura\.py\): (\d+) camadas, \d+ partículas, explods (\d+)", cns)
    if not m:
        return None, []
    return m.group(1), [int(m.group(3)) + k for k in range(int(m.group(2)))]


def _partes(expr):
    """Corta 'a, b' na vírgula de fora dos parênteses."""
    nivel = 0
    for k, ch in enumerate(expr):
        nivel += ch == "("
        nivel -= ch == ")"
        if ch == "," and nivel == 0:
            return expr[:k].strip(), expr[k + 1:].strip()
    raise ValueError(expr)


def desfazer(cns):
    """Tira o que este pós-passo pôs: o bloco da tabela e as linhas trocadas (a original fica guardada em comentário)."""
    cns = re.sub(rf"{re.escape(INICIO)}.*?{re.escape(FIM)}\n\n?", "", cns, flags=re.S)
    return re.sub(rf"^{re.escape(ORIG)}([^\n]*)\n[^\n]*\n", r"\1\n", cns, flags=re.M)


def ligar(cns, corpo):
    nome, ids = aura_do_cns(cns)
    assert nome, "o lutador não tem aura do ferramentas/aura.py no [Statedef -4]"
    cns = desfazer(cns)
    m = lambda letra: f"map(au_{nome}_{letra})"  # noqa: E731
    p = m("p")
    a0x, a0y = corpo.peito()
    s = f"(1 - {RECOLHE} * {m('g')})"

    def mapa(titulo, letra, valor, gatilhos=("1",), tipo="MapSet"):
        return (f"[State -4, Aura {nome} no corpo: {titulo}]\ntype = {tipo}\n"
                + "".join(f"trigger{k + 1} = {g}\n" for k, g in enumerate(gatilhos))
                + f"map = \"au_{nome}_{letra}\"\nvalue = {valor}\nignorehitpause = 1\n\n")

    tab = tabela(corpo, set(ids))
    bloco = [f"{INICIO}: a aura segue o corpo (issue #51). Tabela medida nos desenhos do .air: {len(tab)} valores, "
             f"{sum(len(g) for g in tab.values())} trechos. Peito do parado em {a0x:.0f}, {a0y:.0f}. Não edite: rode "
             f"python3 ferramentas/aura_no_corpo.py\n",
             mapa("alvo de quem está em pé", "p", ZERO)]
    for valor, gatilhos in sorted(tab.items()):
        qx, qy = valor % 128 - 64, valor // 128 % 128 - 64
        qg, qb = valor // 16384 % 8, valor // 131072 - 32
        # sem ponto e vírgula no título: no .cns ele começa comentário e o controlador some
        bloco.append(mapa(f"peito {qx * PASSO:+d} {qy * PASSO:+d}, recolhe {qg} de {NIVEIS - 1}, centro {qb * PASSO_B:+d}",
                          "p", valor, gatilhos))
    alvos = {"ax": f"((floor({p}) % 128) - 64) * {PASSO}", "ay": f"((floor({p} / 128) % 128) - 64) * {PASSO}",
             "g": f"(floor({p} / 16384) % 8) / {NIVEIS - 1}.0", "bx": f"(floor({p} / 131072) - 32) * {PASSO_B}"}
    for letra, alvo in alvos.items():
        bloco.append(mapa(f"{letra} zera antes do round", letra, "0", ("RoundState = 0",)))
        bloco.append(mapa(f"{letra} corre atrás do corpo", letra,
                          f"{m(letra)} + (({alvo}) - {m(letra)}) * {ATRASO}", ("RoundState > 0",)))
    bloco.append(FIM + "\n\n")
    marco = re.search(rf"^\[State -4, Aura {nome} \w+: nasce\]", cns, re.M)
    cns = cns[:marco.start()] + "".join(bloco) + cns[marco.start():]

    altas = {e for e in ids if max((n["h"] for (g, _), n in corpo.nos.items() if g == e), default=0) >= ALTA}

    def trocar(mo):
        corpo_ctrl = mo.group(0)
        do_chao = "\nbindtime = 0" in corpo_ctrl
        px, py = _partes(re.search(r"^pos = ([^\n]*)$", corpo_ctrl, re.M).group(1))
        sx, sy = _partes(re.search(r"^scale = ([^\n]*)$", corpo_ctrl, re.M).group(1))
        if do_chao:
            # o aura.py descontava só a altura do pulo (- min(0, Pos Y)); na queda o motor leva o lutador para baixo
            # do chão por alguns tiques antes de pousar, e a camada do chão afundava junto (26 px no filme)
            py = py.replace("- min(0, Pos Y)", "- Pos Y")
            nova_pos, nova_escala = f"pos = {px} + {m('bx')}, {py}", None
            if int(re.search(r"^id = (\d+)", corpo_ctrl, re.M).group(1)) in altas:
                # coluna e paredão: nascem do chão e são mais altos que o lutador; com ele caído, baixam junto
                nova_escala = f"scale = {sx}, ({sy}) * (1 - {BAIXA} * {m('g')})"
        else:
            nova_pos = (f"pos = {px} + {m('ax')} + ({a0x:.1f}) * (1 - {s}), "
                        f"{py} + {m('ay')} + ({a0y:.1f}) * (1 - {s}) - {SOBE} * {m('g')}")
            nova_escala = f"scale = ({sx}) * {s}, ({sy}) * {s}"

        def linha(chave, nova):
            return lambda mm: f"{ORIG}{mm.group(0)}\n{nova}"
        corpo_ctrl = re.sub(r"^pos = [^\n]*$", linha("pos", nova_pos), corpo_ctrl, count=1, flags=re.M)
        if nova_escala:
            corpo_ctrl = re.sub(r"^scale = [^\n]*$", linha("scale", nova_escala), corpo_ctrl, count=1, flags=re.M)
        return corpo_ctrl
    cns, n = re.subn(rf"^\[State -4, Aura {nome} \w+: move\]\n(?:[^\n]+\n)+", trocar, cns, flags=re.M)
    assert n == len(ids), f"achei {n} controladores 'move' para {len(ids)} camadas"
    return cns


def aplicar(lutador, pasta=None):
    pasta = Path(pasta) if pasta else RAIZ / "chars" / lutador
    arq = pasta / f"{lutador}.cns"
    corpo = Corpo(pasta, lutador)
    novo = ligar(corpo.cns, corpo)
    arq.write_text(novo, encoding="utf-8", newline="\n")
    nome, ids = aura_do_cns(novo)
    tab = tabela(corpo, set(ids))
    print(f"{lutador}: aura '{nome}' presa ao corpo; {len(corpo.acoes)} ações medidas, {len(tab)} valores, "
          f"{sum(len(g) for g in tab.values())} trechos na tabela")


# ---------------------------------------------------------------------------------------------------------- conferir
def camadas_do_corpo(cns):
    """{id: True se a camada é do corpo, False se é do chão}."""
    nome, ids = aura_do_cns(cns)
    tipo = {}
    for mo in re.finditer(rf"^\[State -4, Aura {nome} \w+: move\]\n(?:[^\n]+\n)+", cns, re.M):
        tipo[int(re.search(r"^id = (\d+)", mo.group(0), re.M).group(1))] = "\nbindtime = 0" not in mo.group(0)
    return tipo


def conferir(log, lutador, pasta=None, mostrar=True):
    """Lê o aura_log.txt e devolve (passou, texto). Mede a distância do peito de cada camada ao peito do desenho."""
    pasta = Path(pasta) if pasta else RAIZ / "chars" / lutador
    corpo = Corpo(pasta, lutador)
    tipo = camadas_do_corpo(corpo.cns)
    a0x, a0y = corpo.peito()
    linhas = []
    for linha in Path(log).read_text(encoding="utf-8", errors="replace").splitlines():
        if linha.startswith("ERRO"):
            return False, linha
        m = re.search(r"t=(\d+) fase=(\S+) st=(-?\d+) anim=(-?\d+) el=(-?\d+) x=(\S+) y=(\S+) tx=\S+ ty=\S+ cx=(\S+) "
                     r"cy=\S+ f=(-?\d+)", linha)
        if not m:
            continue
        d = dict(t=int(m.group(1)), fase=m.group(2), st=int(m.group(3)), anim=int(m.group(4)), el=int(m.group(5)),
                 x=float(m.group(6)) + float(m.group(8)), y=float(m.group(7)), f=int(m.group(9)), cam={})
        for e, px, py, sx, sy in re.findall(r"(\d+) px=(\S+) py=(\S+) sx=(\S+) sy=(\S+)", linha):
            d["cam"][int(e)] = tuple(float(v) for v in (px, py, sx, sy))
        linhas.append(d)
    assert linhas, f"{log}: sem tiques"
    texto, passou = [], True
    for e, do_corpo in sorted(tipo.items()):
        base = [d["cam"][e] for d in linhas if d["fase"] == "parado" and e in d["cam"] and d["t"] > 34]
        assert base, f"camada {e} não apareceu com o lutador parado"
        sx0 = float(np.median([b[2] for b in base]))
        fases = {}
        for d in linhas:
            if e not in d["cam"] or d["t"] <= 34:
                continue
            px, py, sx, _ = d["cam"][e]
            dx, dy = (px - d["x"]) * d["f"], py - d["y"]
            if do_corpo:
                alvo = corpo.alvo(d["anim"], d["el"])
                if alvo is None:
                    continue
                s = sx / sx0
                # onde o ponto do peito da camada caiu, contra o peito do desenho da tela (o "sobe" do recolher sai)
                ex = dx + s * a0x - (a0x + alvo[0])
                ey = dy + s * a0y - (a0y + alvo[1]) + SOBE * alvo[2]
                dist = float(np.hypot(ex, ey))
            else:
                dist = abs(py)
            fases.setdefault(d["fase"], []).append((dist, d["t"], d["st"], d["anim"]))
        todas = np.array([v[0] for f in fases.values() for v in f])
        p95, pior = float(np.percentile(todas, 95)), max((v for f in fases.values() for v in f))
        # o maior trecho seguido com a camada a mais de 20 px do peito: um tranco (pouso, golpe) pode passar por um
        # ou dois tiques, porque a tabela vê a ação nova um tique depois; ficar solta, não
        solta, seguidos, antes = 0, 0, None
        for dist, t, _, _ in sorted((v for f in fases.values() for v in f), key=lambda v: v[1]):
            seguidos = seguidos + 1 if dist > 20 and antes == t - 1 else (1 if dist > 20 else 0)
            solta, antes = max(solta, seguidos), t
        ok = (p95 <= 12 and solta <= 4 and pior[0] <= 45) if do_corpo else pior[0] <= 6
        passou &= ok
        texto.append(f"  {'PASS' if ok else 'FAIL'} camada {e} ({'corpo' if do_corpo else 'chão'}): "
                     + (f"distância ao peito p95 {p95:.1f} px, pior {pior[0]:.1f} px, solta (> 20 px) por no máximo "
                        f"{solta} tiques seguidos"
                        if do_corpo else f"distância ao chão, pior {pior[0]:.1f} px")
                     + f" (tique {pior[1]}, estado {pior[2]}, ação {pior[3]})")
        for fase, vs in fases.items():
            arr = np.array([v[0] for v in vs])
            texto.append(f"       {fase:<15} média {arr.mean():5.1f}  pior {arr.max():5.1f}")
    estados = sorted({d["st"] for d in linhas})
    texto.append(f"  estados visitados: {len(estados)} ({', '.join(map(str, estados))})")
    return passou, "\n".join(texto)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lutadores", nargs="*")
    ap.add_argument("--conferir", type=Path, help="pasta com o aura_log.txt do filmar_aura_corpo.py")
    ap.add_argument("--robo", action="store_true", help="roda o roteiro no motor (sem filme) e confere")
    ap.add_argument("--chars", type=Path, help="pasta chars/ de onde o lutador vem (para medir o antes)")
    a = ap.parse_args()
    nomes = a.lutadores or list(LUTADORES)
    if a.conferir:
        ok, texto = conferir(a.conferir / "aura_log.txt", nomes[0], a.chars / nomes[0] if a.chars else None)
        print(texto)
        sys.exit(0 if ok else 1)
    if a.robo:
        import tempfile
        import filmar_aura_corpo
        falhou = False
        for nome in nomes:
            with tempfile.TemporaryDirectory() as td:
                log = filmar_aura_corpo.filmar(nome, Path(td), filme=False, chars=a.chars)
                ok, texto = conferir(log, nome, a.chars / nome if a.chars else None)
            print(f"{nome}:\n{texto}")
            falhou |= not ok
        print("\nRESUMO: " + ("FALHOU" if falhou else "a aura segue o corpo em todos"))
        sys.exit(1 if falhou else 0)
    for nome in nomes:
        aplicar(nome)


if __name__ == "__main__":
    main()
