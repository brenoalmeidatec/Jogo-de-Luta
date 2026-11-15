#!/usr/bin/env python3
"""Prende a aura do Despertar ao corpo: asas, garanhão, elos e o resto acompanham o lutador em todo estado (issue #51).

  python3 ferramentas/aura_no_corpo.py [lutador ...]        mede e liga em chars/<l>/<l>.cns (sem nome: todos com aura)
  python3 ferramentas/aura_no_corpo.py --conferir PASTA l    confere o aura_log.txt do ferramentas/filmar_aura_corpo.py
  python3 ferramentas/aura_no_corpo.py --robo [lutador ...]  roda o roteiro no motor (sem filme) e confere

O defeito (Breno, 2026-11-14): as camadas do ferramentas/aura.py nascem presas ao EIXO do lutador (os pés) numa posição
fixa. O eixo não se mexe quando ele agacha, cai ou deita, só o desenho muda; então as asas do Diabo Loiro ficavam no
ar, na altura de quem está em pé, com o corpo no chão. Segunda volta (Breno, 2026-11-15): seguir a posição não basta.
A asa é parte do corpo: fica grudada nas costas, INCLINA no ângulo do tronco e FECHA quando ele cai.

O conserto é um pós-passo, como o parry.py e o efeitos.py: trabalha em cima do que já está em chars/<l>/ e pode rodar
quantas vezes for (refaz o próprio bloco). Quem regrava o [Statedef -4] da aura chama `aplicar` no fim.

  1. Mede, em cada desenho de cada ação do .air (no sprite do despertado, quando o RemapPreset troca), o TRONCO: o
     ponto das costas (centro da metade do corpo que tem a cabeça), o ângulo do tronco (da metade das pernas para a
     metade da cabeça; 0 = em pé, + = inclinado para a frente, -90 = deitado de costas), o centro e a altura. Em pé a
     metade da cabeça é a de cima; deitado é a ponta mais pesada do eixo comprido do desenho.
  2. Escreve no [Statedef -4] duas tabelas por ação/elemento (trechos vizinhos iguais viram um só gatilho) com o alvo
     daquele tique, e cinco maps que correm atrás do alvo com atraso curto (o movimento secundário: a asa chega um
     instante depois do corpo):
        au_<nome>_ax, _ay   deslocamento das costas        au_<nome>_th   ângulo do tronco, em graus
        au_<nome>_g         0 em pé .. 1 deitado           au_<nome>_bx   deslocamento do centro (camadas de chão)
  3. Troca a posição, a escala, o ângulo e o alfa de cada camada (os controladores do aura.py):
        camada do corpo (asas, garanhão, elos soltos): gira no ângulo do tronco em volta do ponto das costas (o
          `angle` do Explod gira em volta do eixo do desenho, nos pés; a posição compensa para o pivô ser as costas);
        camada com desenhos fechando (<nome>, <nome>_meio, <nome>_fechada: as asas do Hazak): o alfa troca um desenho
          pelo outro conforme o corpo deita (g) e reabre quando ele levanta;
        camada do corpo sem desenho fechado (garanhão, elos): recolhe (encolhe em volta das costas) com g;
        camada do chão (brasa, crateras, anel, névoa, coluna, paredão): continua no chão, mas anda em x com o corpo;
        a coluna e o paredão (mais altos que o lutador) baixam quando ele cai, em vez de ficar de pé sobre o corpo.

Conferência (--conferir, --robo): em todo tique do roteiro, o ponto das costas de cada camada do corpo tem de ficar
perto das costas medidas no desenho que está na tela, e o ângulo da camada perto do ângulo do tronco. Aceite: distância
com percentil 95 <= 12 px, pior tique <= 70 px e no máximo 4 tiques seguidos a mais de 20 px. O pior é o pouso de quem
foi arremessado: o desenho passa de em pé (5030) para deitado (5100) num tique só, o [Statedef -4] roda antes da troca
de ação e vê a ação nova um tique depois, e a camada leva mais um tique para chegar (60 px por 2 tiques no filme).; ângulo com percentil 95 <= 25 graus; camada de chão a <= 6 px do chão.
"""
import argparse
import io
import math
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
PASSO, PASSO_B, NIVEIS, PASSO_T = 2, 4, 8, 7.5  # px por degrau das costas e do centro, degraus do recolher, graus
SALTO = {"ax": 24, "ay": 24, "th": 40, "g": 0.45}  # acima disto (px, graus, recolher) a camada não corre atrás: pula junto com o corpo
ATRASO = 0.6                     # fração do caminho que a camada anda por tique
RECOLHE = 0.5                     # deitado, a camada do corpo sem desenho fechado fica com (1 - RECOLHE) do tamanho
ALTA, BAIXA = 120, 0.45           # camada de chão com desenho de ALTA px ou mais perde BAIXA da altura com ele deitado
COLA = 8                          # deitado, o ponto das costas desce isto: a asa fechada fica colada no corpo, não por cima
INCLINA = 50                      # em pé, o tronco inclina no máximo isto (um chute alto não deita a asa)
ZERO_P = 64 + 128 * 64
ZERO_Q = 8 * 32 + 512 * 16
# o ponto do DESENHO da camada que gruda nas costas, em px a partir do eixo dela (os pés): onde as asas se encontram.
# Sem entrada, é o ponto das costas do lutador parado (o desenho foi feito em volta dele).
PIVO = {"diabo": (1.0, -90.0)}


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
        self._cache, self._medidas = {}, {}
        self.ref = (0.0, 0.0, 0.0, 0.0, 1.0)
        alturas = [self._nuvem(0, e) for e in range(1, len(self.acoes[0]) + 1)]
        self.altura = float(np.mean([np.percentile(n[1], 97) - np.percentile(n[1], 3) for n in alturas if n]))
        ref = [v for v in (self.pontos(0, e) for e in range(1, len(self.acoes[0]) + 1)) if v]
        self._medidas = {}
        self.ref = tuple(float(np.mean([r[k] for r in ref])) for k in range(5))  # costas x, y, centro x, ângulo, g

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

    def _nuvem(self, acao, elem):
        """(xs, ys) dos pixels do corpo do elemento, em px do jogo a partir do eixo: x para a frente, y para baixo."""
        els = self.acoes.get(acao)
        if not els or not 1 <= elem <= len(els):
            return None
        g, i, ox, oy, esp = els[elem - 1]
        m = self._mascara((g, i))
        if m is None:
            return None
        return (-m[0] if esp else m[0]) + ox * self.escala, m[1] + oy * self.escala

    def pontos(self, acao, elem):
        """(costas x, costas y, centro x, ângulo do tronco em graus, g) do desenho do elemento; None se não tem corpo.
        g: 0 em pé .. 1 deitado, pela altura do desenho contra a do parado."""
        chave = (acao, elem)
        if chave in self._medidas:
            return self._medidas[chave]
        n = self._nuvem(acao, elem)
        if n is None:
            self._medidas[chave] = None
            return None
        xs, ys = n
        g = float(np.clip((0.62 - (np.percentile(ys, 97) - np.percentile(ys, 3)) / self.altura) / 0.27, 0, 1))
        # em pé: a metade de cima é a da cabeça
        cima = ys <= np.median(ys)
        cab = np.array([xs[cima].mean(), ys[cima].mean()])
        per = np.array([xs[~cima].mean(), ys[~cima].mean()])
        ang = float(np.clip(math.degrees(math.atan2(cab[0] - per[0], per[1] - cab[1])), -INCLINA, INCLINA))
        if g > 0:
            # deitando: o eixo comprido do desenho, e a cabeça na ponta mais pesada (o tronco é compacto, as pernas
            # são compridas: o centro de massa fica mais perto da cabeça). Empate: a ponta de cima.
            pts = np.stack([xs - xs.mean(), ys - ys.mean()], 1)
            _, vecs = np.linalg.eigh(np.cov(pts.T))
            u = vecs[:, -1]
            proj = pts @ u
            mais, menos = np.percentile(proj, 99), -np.percentile(proj, 1)
            if abs(mais - menos) < 0.08 * (mais + menos):
                u = u if u[1] < 0 else -u
            elif mais > menos:
                u = -u
            proj = pts @ u
            lado = proj > 0
            cab_d = np.array([xs[lado].mean(), ys[lado].mean()])
            ang_d = math.degrees(math.atan2(u[0], -u[1]))
            if ang_d - ang > 180:
                ang_d -= 360
            elif ang - ang_d > 180:
                ang_d += 360
            cab = (1 - g) * cab + g * (cab_d + np.array([0.0, COLA]))
            ang = (1 - g) * ang + g * float(np.clip(ang_d, -110, 110))
        self._medidas[chave] = (float(cab[0]), float(cab[1]), float(xs.mean()), ang, g)
        return self._medidas[chave]

    def alvo(self, acao, elem):
        """(ax, ay, g, bx, ângulo) do elemento, relativo ao parado; None se não tem corpo."""
        p = self.pontos(acao, elem)
        if p is None:
            return None
        return p[0] - self.ref[0], p[1] - self.ref[1], p[4], p[2] - self.ref[2], p[3] - self.ref[3]

    def costas(self):
        return self.ref[0], self.ref[1]


def _degraus(v):
    ax, ay, g, bx, th = v
    return (int(np.clip(round(ax / PASSO), -63, 63)), int(np.clip(round(ay / PASSO), -63, 63)),
            int(np.clip(round(g * (NIVEIS - 1)), 0, NIVEIS - 1)), int(np.clip(round(bx / PASSO_B), -31, 31)),
            int(np.clip(round(th / PASSO_T), -15, 15)))


def tabela(corpo, ids_da_aura):
    """({valor de p: [gatilhos]}, {valor de q: [gatilhos]}). p guarda as costas (ax, ay); q guarda g, o centro e o
    ângulo. Um trecho por ação enquanto os elementos vizinhos ficam a menos de 5 px, 0,2 de recolher e 10 graus uns
    dos outros. O que dá igual ao parado não entra (é o valor de partida)."""
    tp, tq = {}, {}
    for acao, els in sorted(corpo.acoes.items()):
        # 30000+: as ações espelho do aura_silhueta.py; 9720 a 9739: as luzes da luz.py
        if acao in ids_da_aura or acao < 0 or acao >= 30000 or 9720 <= acao < 9740:
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
                if folga[0] <= 5 and folga[1] <= 5 and folga[2] <= 0.2 and folga[3] <= 8 and folga[4] <= 10:
                    continue
            trechos.append((ini + 1, e, _degraus(np.array(alvos[ini:e]).mean(0))))
            ini = e
        for a, b, (qx, qy, qg, qb, qt) in trechos:
            if a == 1 and b == len(alvos):
                gat = f"Anim = {acao}"
            elif a == b:
                gat = f"Anim = {acao} && AnimElemNo(0) = {a}"
            else:
                gat = f"Anim = {acao} && AnimElemNo(0) = [{a}, {b}]"
            p, q = (qx + 64) + 128 * (qy + 64), qg + 8 * (qb + 32) + 512 * (qt + 16)
            if p != ZERO_P:
                tp.setdefault(p, []).append(gat)
            if q != ZERO_Q:
                tq.setdefault(q, []).append(gat)
    return tp, tq


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
    cns = re.sub(rf"^{re.escape(ORIG)}\(linha nova\)\n[^\n]*\n", "", cns, flags=re.M)
    return re.sub(rf"^{re.escape(ORIG)}([^\n]*)\n[^\n]*\n", r"\1\n", cns, flags=re.M)


def camadas_do_cns(cns):
    """{id: (nome da camada, True se é do corpo / False se é do chão)}."""
    nome, _ = aura_do_cns(desfazer(cns))
    saida = {}
    for mo in re.finditer(rf"^\[State -4, Aura {nome} (\w+): move\]\n(?:[^\n]+\n)+", cns, re.M):
        saida[int(re.search(r"^id = (\d+)", mo.group(0), re.M).group(1))] = (mo.group(1), "\nbindtime = 0" not in mo.group(0))
    return saida


def _pesos(g):
    """Quanto cada desenho da asa aparece conforme o corpo deita: aberta, meio, fechada (somam 1 ou mais)."""
    # fecha cedo: no quique do chão (5100, 5160) o desenho fica meio levantado (g perto de 0,6) e a asa tem de
    # continuar fechada; a meio só aparece na passagem (g de 0,15 a 0,5), caindo ou levantando
    return {"": f"min(1, max(0, (0.3 - {g}) / 0.15))",
            "_meio": f"min(1, max(0, min(({g} - 0.15) / 0.15, (0.5 - {g}) / 0.15)))",
            "_fechada": f"min(1, max(0, ({g} - 0.35) / 0.15))"}


def ligar(cns, corpo):
    nome, ids = aura_do_cns(cns)
    assert nome, "o lutador não tem aura do ferramentas/aura.py no [Statedef -4]"
    cns = desfazer(cns)
    m = lambda letra: f"map(au_{nome}_{letra})"  # noqa: E731
    p, q = m("p"), m("q")
    pvx, pvy = PIVO.get(nome, corpo.costas())
    camadas = camadas_do_cns(cns)
    nomes = {n for n, _ in camadas.values()}
    familias = {n for n in nomes if n + "_meio" in nomes and n + "_fechada" in nomes}

    def familia(n):
        for f in familias:
            for sufixo in ("_fechada", "_meio", ""):
                if n == f + sufixo:
                    return sufixo
        return None

    def mapa(titulo, letra, valor, gatilhos=("1",)):
        return (f"[State -4, Aura {nome} no corpo: {titulo}]\ntype = MapSet\n"
                + "".join(f"trigger{k + 1} = {g}\n" for k, g in enumerate(gatilhos))
                + f"map = \"au_{nome}_{letra}\"\nvalue = {valor}\nignorehitpause = 1\n\n")

    tp, tq = tabela(corpo, set(ids))
    bloco = [f"{INICIO}: a aura segue o corpo (issue #51). Tabelas medidas nos desenhos do .air: {len(tp)} + {len(tq)} "
             f"valores, {sum(len(g) for g in tp.values()) + sum(len(g) for g in tq.values())} trechos. Pivô nas costas "
             f"em {pvx:.0f}, {pvy:.0f}. Não edite: rode python3 ferramentas/aura_no_corpo.py\n",
             mapa("costas de quem está em pé", "p", ZERO_P), mapa("tronco de quem está em pé", "q", ZERO_Q)]
    # sem ponto e vírgula nos títulos: no .cns ele começa comentário e o controlador some sem erro
    for valor, gatilhos in sorted(tp.items()):
        qx, qy = valor % 128 - 64, valor // 128 - 64
        bloco.append(mapa(f"costas {qx * PASSO:+d} {qy * PASSO:+d}", "p", valor, gatilhos))
    for valor, gatilhos in sorted(tq.items()):
        qg, qb, qt = valor % 8, valor // 8 % 64 - 32, valor // 512 - 16
        bloco.append(mapa(f"recolhe {qg} de {NIVEIS - 1}, centro {qb * PASSO_B:+d}, tronco {qt * PASSO_T:+.0f} graus",
                          "q", valor, gatilhos))
    alvos = {"ax": f"((floor({p}) % 128) - 64) * {PASSO}", "ay": f"(floor({p} / 128) - 64) * {PASSO}",
             "g": f"(floor({q}) % 8) / {NIVEIS - 1}.0", "bx": f"((floor({q} / 8) % 64) - 32) * {PASSO_B}",
             "th": f"(floor({q} / 512) - 16) * {PASSO_T}"}
    for letra, alvo in alvos.items():
        bloco.append(mapa(f"{letra} zera antes do round", letra, "0", ("RoundState = 0",)))
        # salto grande (o corpo bate no chão de uma vez, o pouso de um arremesso): a camada vai direto, sem atraso
        passo = f"ifelse(abs(({alvo}) - {m(letra)}) > {SALTO[letra]}, 1, {ATRASO})" if letra in SALTO else str(ATRASO)
        bloco.append(mapa(f"{letra} corre atrás do corpo", letra,
                          f"{m(letra)} + (({alvo}) - {m(letra)}) * {passo}", ("RoundState > 0",)))
    bloco.append(FIM + "\n\n")
    marco = re.search(rf"^\[State -4, Aura {nome} \w+: nasce\]", cns, re.M)
    cns = cns[:marco.start()] + "".join(bloco) + cns[marco.start():]
    altas = {e for e in ids if max((n["h"] for (g, _), n in corpo.nos.items() if g == e), default=0) >= ALTA}
    rad = f"({m('th')} * 0.0174533)"

    def linha(nova):
        return lambda mm: f"{ORIG}{mm.group(0)}\n{nova}"

    def trocar(mo):
        ctrl = mo.group(0)
        camada, movendo = mo.group(1), mo.group(2) == "move"
        do_chao = camadas[int(re.search(r"^id = (\d+)", ctrl, re.M).group(1))][1] is False
        sufixo = familia(camada)
        if sufixo is not None:   # a asa abre e fecha: o alfa escolhe o desenho
            peso = _pesos(m("g"))[sufixo]
            ctrl = re.sub(r"^alpha = [^\n]*$", lambda mm: f"{ORIG}{mm.group(0)}\n"
                          + mm.group(0).replace("min(1, max(0, ", f"min(1, max(0, {peso} * "), ctrl, count=1, flags=re.M)
        if not movendo:
            return ctrl
        px, py = _partes(re.search(r"^pos = ([^\n]*)$", ctrl, re.M).group(1))
        sx, sy = _partes(re.search(r"^scale = ([^\n]*)$", ctrl, re.M).group(1))
        if do_chao:
            # o aura.py descontava só a altura do pulo (- min(0, Pos Y)); na queda o motor leva o lutador para baixo
            # do chão por alguns tiques antes de pousar, e a camada do chão afundava junto (26 px no filme)
            py = py.replace("- min(0, Pos Y)", "- Pos Y")
            nova_pos, nova_escala, angulo = f"pos = {px} + {m('bx')}, {py}", None, None
            if int(re.search(r"^id = (\d+)", ctrl, re.M).group(1)) in altas:
                # coluna e paredão: nascem do chão e são mais altos que o lutador; com ele caído, baixam junto
                nova_escala = f"scale = {sx}, ({sy}) * (1 - {BAIXA} * {m('g')})"
        else:
            # gira em volta das costas: o motor gira o Explod em volta do eixo do desenho (os pés), então a posição
            # leva o pivô de volta para o lugar. s encolhe a camada sem desenho fechado (garanhão, elos).
            s = "1" if sufixo is not None else f"(1 - {RECOLHE} * {m('g')})"
            nova_pos = (f"pos = {px} + {m('ax')} + ({pvx:.1f}) - {s} * (({pvx:.1f}) * cos({rad}) - ({pvy:.1f}) * sin({rad})), "
                        f"{py} + {m('ay')} + ({pvy:.1f}) - {s} * (({pvx:.1f}) * sin({rad}) + ({pvy:.1f}) * cos({rad}))")
            nova_escala = None if s == "1" else f"scale = ({sx}) * {s}, ({sy}) * {s}"
            angulo = f"angle = {SINAL} * {m('th')}"
        ctrl = re.sub(r"^pos = [^\n]*$", linha(nova_pos), ctrl, count=1, flags=re.M)
        if nova_escala:
            ctrl = re.sub(r"^scale = [^\n]*$", linha(nova_escala), ctrl, count=1, flags=re.M)
        if angulo:
            ctrl = re.sub(r"^(trans = addalpha)$", lambda mm: f"{ORIG}(linha nova)\n{angulo}\n{mm.group(1)}", ctrl,
                          count=1, flags=re.M)
        return ctrl
    cns, n = re.subn(rf"^\[State -4, Aura {nome} (\w+): (move|apaga para virar)\]\n(?:[^\n]+\n)+", trocar, cns, flags=re.M)
    assert n == 2 * len(ids), f"achei {n} controladores para {len(ids)} camadas"
    return cns


SINAL = -1  # o `angle` do Explod gira ao contrário do relógio; o tronco inclinado para a frente gira no sentido dele


def aplicar(lutador, pasta=None):
    pasta = Path(pasta) if pasta else RAIZ / "chars" / lutador
    arq = pasta / f"{lutador}.cns"
    corpo = Corpo(pasta, lutador)
    novo = ligar(corpo.cns, corpo)
    arq.write_text(novo, encoding="utf-8", newline="\n")
    nome, ids = aura_do_cns(novo)
    tp, tq = tabela(corpo, set(ids))
    print(f"{lutador}: aura '{nome}' presa ao corpo; {len(corpo.acoes)} ações medidas, {len(tp)} + {len(tq)} valores, "
          f"{sum(len(g) for g in tp.values()) + sum(len(g) for g in tq.values())} trechos nas tabelas")
    import aura_silhueta  # a aura colada na silhueta (issue #51, quarta volta) vem logo depois deste bloco
    aura_silhueta.aplicar(lutador, pasta)


# ---------------------------------------------------------------------------------------------------------- conferir
def conferir(log, lutador, pasta=None, mostrar=True):
    """Lê o aura_log.txt e devolve (passou, texto). Mede a distância das costas de cada camada às costas do desenho
    e a diferença entre o ângulo da camada e o do tronco."""
    pasta = Path(pasta) if pasta else RAIZ / "chars" / lutador
    corpo = Corpo(pasta, lutador)
    nome, _ = aura_do_cns(corpo.cns)
    camadas = camadas_do_cns(corpo.cns)
    pvx, pvy = PIVO.get(nome, corpo.costas())
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
        for e, px, py, sx, sy, an in re.findall(r"(\d+) px=(\S+) py=(\S+) sx=(\S+) sy=(\S+)(?: an=(\S+))?", linha):
            d["cam"][int(e)] = tuple(float(v or 0) for v in (px, py, sx, sy, an))
        linhas.append(d)
    assert linhas, f"{log}: sem tiques"
    texto, passou = [], True
    for e, (camada, do_corpo) in sorted(camadas.items()):
        base = [d["cam"][e] for d in linhas if d["fase"] == "parado" and e in d["cam"] and d["t"] > 34]
        assert base, f"camada {e} não apareceu com o lutador parado"
        sx0 = float(np.median([b[2] for b in base]))
        fases, angulos = {}, []
        for d in linhas:
            if e not in d["cam"] or d["t"] <= 34:
                continue
            px, py, sx, _, an = d["cam"][e]
            dx, dy = (px - d["x"]) * d["f"], py - d["y"]
            if do_corpo:
                alvo = corpo.alvo(d["anim"], d["el"])
                if alvo is None:
                    continue
                s, th = sx / sx0, math.radians(SINAL * an)
                # onde o pivô da camada caiu (o motor gira em volta do eixo dela), contra as costas do desenho da tela
                ex = dx + s * (pvx * math.cos(th) - pvy * math.sin(th)) - (pvx + alvo[0])
                ey = dy + s * (pvx * math.sin(th) + pvy * math.cos(th)) - (pvy + alvo[1])
                dist = float(np.hypot(ex, ey))
                angulos.append(abs(SINAL * an - alvo[4]))
            else:
                dist = abs(py)
            fases.setdefault(d["fase"], []).append((dist, d["t"], d["st"], d["anim"]))
        todas = np.array([v[0] for f in fases.values() for v in f])
        p95, pior = float(np.percentile(todas, 95)), max((v for f in fases.values() for v in f))
        # o maior trecho seguido com a camada a mais de 20 px das costas: um tranco (pouso, golpe) pode passar por um
        # ou dois tiques, porque a tabela vê a ação nova um tique depois; ficar solta, não
        solta, seguidos, antes = 0, 0, None
        for dist, t, _, _ in sorted((v for f in fases.values() for v in f), key=lambda v: v[1]):
            seguidos = seguidos + 1 if dist > 20 and antes == t - 1 else (1 if dist > 20 else 0)
            solta, antes = max(solta, seguidos), t
        a95 = float(np.percentile(angulos, 95)) if angulos else 0.0
        ok = (p95 <= 12 and solta <= 4 and pior[0] <= 70 and a95 <= 25) if do_corpo else pior[0] <= 6
        passou &= ok
        texto.append(f"  {'PASS' if ok else 'FAIL'} camada {e} {camada} ({'corpo' if do_corpo else 'chão'}): "
                     + (f"distância às costas p95 {p95:.1f} px, pior {pior[0]:.1f} px, solta (> 20 px) por no máximo "
                        f"{solta} tiques seguidos; ângulo contra o tronco p95 {a95:.0f} graus"
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
