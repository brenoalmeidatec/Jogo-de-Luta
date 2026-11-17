#!/usr/bin/env python3
"""Vida no boneco de peças (pedido do Alisson, 16/11: "fluidez, vida e qualidade").

As poses-chave saem do piloto_firme.py (uma por desenho de hoje). Aqui elas viram animação:

  intermediários  cada elemento com 4 ticks ou mais ganha quadros no meio do caminho até a pose seguinte (um desenho
                  a cada 2 ticks, curva suave). A soma dos ticks e o elemento com caixa de acerto não mudam: o golpe
                  bate na mesma hora e dura o mesmo.
  impacto         o elemento que bate fica parado na pose (segurado), como no arcade; o que vem antes acelera
                  até ele e o que vem depois desacelera.
  respiração      no parado, o peito sobe e desce 1 pixel do jogo (3 no HD) num ciclo, com os braços juntos.
  atraso          a cabeça chega um pouco depois do corpo e as bolinhas da faixa balançam atrás do quadril (o que
                  é solto acompanha o movimento com atraso: sobreposição de movimento).

  sem meio no bote  o elemento logo antes do que bate (a antecipação) não ganha quadro do meio: fica segurado e o golpe
                  sai seco até o contato (Lei 10 do estudo-anatomia-golpes.md; meio-termo do Alisson, 17/11: no
                  máximo 1 borrão nesse trecho, e o borrão, se houver, é desenho próprio da folha, não mistura).

Peça trocada de desenho (punho -> mão aberta, perna levantada, expressão) não é misturada: o desenho troca na pose.
"""
import math

PASSO = 2          # ticks por desenho nos intermediários (60 por segundo -> 30 desenhos por segundo)
RESPIRA_PX = 3     # subida do peito no HD (1 pixel do jogo)
ATRASO_CABECA = 0.35
ATRASO_BOLINHA = 0.8
LIMITE_CABECA = 3
LIMITE_BOLINHA = 7
MEIO_NO_BOTE = False  # True volta ao jeito antigo (quadros do meio também entre a antecipação e o contato)


def suave(t):
    return t * t * (3 - 2 * t)


def acelera(t):
    return t * t


def desacelera(t):
    return 1 - (1 - t) * (1 - t)


def misturar(a, b_, t):
    """Pose no meio do caminho de a até b_ (t de 0 a 1). Peça com desenho diferente fica com o de a."""
    out = {}
    for slot in set(a) | set(b_):
        pa, pb = a.get(slot, {}), b_.get(slot, {})
        if pa.get("var") != pb.get("var"):
            out[slot] = dict(pa)
            continue
        p = {k: v for k, v in pa.items() if k not in ("ang", "dx", "dy", "custo", "estica")}
        for k in ("ang", "dx", "dy"):
            p[k] = pa.get(k, 0) + (pb.get(k, 0) - pa.get(k, 0)) * t
        if "estica" in pa or "estica" in pb:  # membro que estica (borracha): estica e volta junto com o giro
            p["estica"] = pa.get("estica", 1) + (pb.get("estica", 1) - pa.get("estica", 1)) * t
        out[slot] = p
    return out


def animar(poses, elems, bate=None, laco=False, guarda=None, fixos=frozenset(), meio_no_bote=None):
    """Lista de (pose, ticks, caixa, desenho_de_hoje) a partir das poses-chave.
    elems: [(desenho_de_hoje, ticks)]; bate: índice do elemento com caixa; laco: a última volta para a primeira;
    guarda: pose para onde o golpe volta no fim (a guarda); fixos: desenhos que não se misturam (quadro especial,
    desenhado inteiro): não ganham intermediário nem servem de destino de um. meio_no_bote: None segue MEIO_NO_BOTE;
    False segura a antecipação (o elemento logo antes de um que bate) sem quadro do meio."""
    if meio_no_bote is None:
        meio_no_bote = MEIO_NO_BOTE
    saida = []
    n = len(elems)
    batem = set(bate) if isinstance(bate, (set, list, tuple)) else ({bate} if bate is not None else set())
    for k, (q, ticks) in enumerate(elems):
        a = poses[q]
        if k + 1 < n:
            b_ = poses[elems[k + 1][0]]
        elif laco:
            b_ = poses[elems[0][0]]
        else:
            b_ = guarda if guarda is not None else a
        caixa = k in batem
        prox = elems[k + 1][0] if k + 1 < n else (elems[0][0] if laco else None)
        bote = not meio_no_bote and (k + 1) in batem
        if caixa or bote or ticks < 4 or q in fixos or prox in fixos or "_especial" in a or "_especial" in b_:
            # impacto segurado; antecipação segurada (sai seco até o contato); elemento curto não tem espaço para meio; desenho de hoje (especial) não se mistura
            saida.append((dict(a), ticks, caixa, q))
            continue
        if batem and k < min(batem):
            curva = acelera
        elif batem and k > max(batem):
            curva = desacelera
        else:
            curva = suave
        partes = []
        resto = ticks
        while resto > 0:
            t = min(PASSO, resto)
            partes.append(t)
            resto -= t
        if partes[-1] == 1 and len(partes) > 1:
            partes[-2] += 1
            partes.pop()
        feito = 0
        for t in partes:
            frac = curva(feito / ticks)
            saida.append((misturar(a, b_, frac), t, caixa, q))
            feito += t
    return saida


def respirar(quadros, ciclo=None):
    """Peito sobe e desce num ciclo do tamanho da animação (laço do parado)."""
    total = sum(t for _, t, _, _ in quadros)
    ciclo = ciclo or total
    tick = 0
    out = []
    for pose, t, cx, q in quadros:
        fase = 2 * math.pi * (tick + t / 2) / ciclo
        p = {k: dict(v) for k, v in pose.items()}
        tr = p.setdefault("tronco", {"ang": 0})
        tr["dy"] = tr.get("dy", 0) - RESPIRA_PX * (0.5 - 0.5 * math.cos(fase))
        out.append((p, t, cx, q))
        tick += t
    return out


def atrasar(quadros, laco=False):
    """Cabeça e bolinhas atrás do movimento do corpo (diferença do quadril entre um desenho e o anterior)."""
    out = []
    n = len(quadros)
    for i, (pose, t, cx, q) in enumerate(quadros):
        j = i - 1 if i > 0 else (n - 1 if laco else 0)
        ant = quadros[j][0]
        dx = pose.get("quadril", {}).get("dx", 0) - ant.get("quadril", {}).get("dx", 0)
        dy = (pose.get("quadril", {}).get("dy", 0) + pose.get("tronco", {}).get("dy", 0)) - \
             (ant.get("quadril", {}).get("dy", 0) + ant.get("tronco", {}).get("dy", 0))
        p = {k: dict(v) for k, v in pose.items()}
        cab = p.setdefault("cabeca", {"ang": 0})
        lim = lambda v, m: max(-m, min(m, v))
        cab["dx"] = cab.get("dx", 0) + lim(-ATRASO_CABECA * dx, LIMITE_CABECA)
        cab["dy"] = cab.get("dy", 0) + lim(-ATRASO_CABECA * dy, LIMITE_CABECA)
        p["_bolinhas"] = {"dx": lim(-ATRASO_BOLINHA * dx, LIMITE_BOLINHA),
                          "dy": lim(-ATRASO_BOLINHA * dy * 0.5, LIMITE_BOLINHA),
                          "ang": lim(ATRASO_BOLINHA * dx * 1.5, 12)}
        out.append((p, t, cx, q))
    return out
