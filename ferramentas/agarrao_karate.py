#!/usr/bin/env python3
"""Agarrão em pé do Hazak no estilo karatê (Breno, #32, 24/11: "não consigo entender nada que ele faz: usa alguma coisa
do karatê, tipo pegar o cara, colocar e dar uma sequência de soco com rapidez que nem dá pra ver o braço direito").

Leitura do golpe, sem desenho confuso:
  1. pega: a mão da frente estica e agarra a gola do oponente (e fica agarrando a rajada inteira);
  2. rajada: o braço de perto soca sem parar, rápido demais para ver: só o borrão do braço (ferramentas/borrao.py)
     e o punho nítido no contato, com o vento estourando. Três socos na tela a cada pancada de dano, alternando
     rosto e estômago;
  3. final: solta a gola, gira o quadril para trás (preparo) e dá o soco reto inteiro (gyaku-zuki), nítido, com
     vento grande; o oponente voa.

O tempo e as caixas da ação 810 não mudam (as pancadas continuam nos ticks 22, 39, 56, 73 e 90 e o final no 111, como
o .cns espera); a tentativa (800) também fica com os 12 ticks de hoje. Os quadros são montados com as peças do kit
(golpe sem desenho próprio: passo 5 da regra de criação) e com o soco reto que já está no jogo (quadros_pecas_hd/
soco_reto). O despertado (Diabo) continua com o agarrão dele: o ligar_pecas dá a cada quadro novo o destino do
quadro antigo daquele tick no [RemapPreset despertado].

    python3 ferramentas/agarrao_karate.py         grava quadros_karate_hd/agarrao_karate (810) e agarrao_karate_pega (800)
    python3 ferramentas/ligar_pecas.py hazaki agarrao_karate agarrao_karate_pega --pasta quadros_karate_hd --grupo 49000
    python3 ferramentas/agarrao_karate.py --binds   (o oponente preso na mão da gola, mais longe que no abraço)
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import borrao as bz  # noqa: E402
import firme  # noqa: E402

RAIZ = AQUI.parent
SPR = RAIZ / "sprites/hazaki"

SEGURA = {"tronco": {"ang": 5}, "cabeca": {"ang": -3}, "braco_frente": {"var": "esticado", "ang": 4}}
ALCANCA = {"tronco": {"ang": 3}, "cabeca": {"ang": -2}, "braco_frente": {"var": "esticado", "ang": -6}}
# soco de perto, com o quadril indo junto: rosto (alto) e estômago (baixo)
SOCO = {
    "alto": {"quadril": {"ang": 0, "dx": 6, "dy": 0}, "tronco": {"ang": 8}, "cabeca": {"ang": -5},
             "braco_frente": {"var": "esticado", "ang": 2}, "braco_tras": {"var": "cruzado", "ang": 4}},
    "baixo": {"quadril": {"ang": 0, "dx": 6, "dy": 0}, "tronco": {"ang": 9}, "cabeca": {"ang": -6},
              "braco_frente": {"var": "esticado", "ang": 2}, "braco_tras": {"var": "cruzado", "ang": 13}},
}
# preparo do final: solta a gola, braço da frente volta para a guarda e o tronco gira para trás
PREPARO_FINAL = {"quadril": {"ang": 0, "dx": -6, "dy": 0}, "tronco": {"ang": -6}, "cabeca": {"ang": 3}}


def render(pose, sem=()):
    """Desenho do kit; `sem` tira camadas (o braço de perto some quando vira borrão)."""
    camadas = firme.K.CAMADAS
    if sem:
        firme.K.CAMADAS = [c for c in camadas if c not in sem]
    try:
        return firme.desenhar(KIT, dict(pose))
    finally:
        firme.K.CAMADAS = camadas


def mascara_braco(pose):
    """Pixels do braço de perto na pose (a diferença entre o desenho com e sem ele)."""
    a, b = render(pose), render(pose, sem=("braco_tras", "antebraco_tras"))
    return (a[..., 3] > 0) & ((b[..., 3] == 0) | (np.abs(a.astype(int) - b.astype(int)).sum(-1) > 0)), a


PEITO_X = 588  # frente do peito na guarda (3x): o borrão nasce daqui; atrás disso o braço some no corpo


def borrao_de(base, estendido, m, punho=40):
    """Borrão do braço `m` do `estendido` em cima da `base` (que já está sem o braço de perto). Só o antebraço e o
    punho (o que passa da frente do peito) viram borrão; a parte que cruza o peito some (rápido demais)."""
    m = m.copy()
    m[:, :PEITO_X] = False
    ys, xs = np.nonzero(m)
    ombro = PEITO_X
    return bz.borrao(estendido, base, ombro, (int(ys.min()), int(ys.max()) + 1), punho=punho, tirar_guarda=False,
                     mascara=m)


def ponta(m):
    ys, xs = np.nonzero(m)
    x = int(xs.max())
    return x, int(np.median(ys[xs > x - 30]))


def _q(n, d):
    return np.array(Image.open(SPR / f"quadros_pecas_hd/{n}/{d:02d}.png").convert("RGBA"))


def fantasma(rgb):
    """Cor do rastro (afterimage dos jogos de luta dos anos 90): a cor do braço puxada para azul-claro."""
    return np.clip(rgb.astype(int) * 0.45 + np.array([150, 185, 235]) * 0.55, 0, 255).astype(np.uint8)


def rajada(ang, rastros, alto=True, vento_x=0):
    """Soco de perto em `ang` (nítido) com os rastros dos socos anteriores em `rastros` (ângulos), por baixo do braço
    nítido e por cima do corpo, mais riscos de velocidade. vento_x > 0 = vento estourando na frente do punho."""
    base = dict(SOCO["alto" if alto else "baixo"])
    pose = dict(base, braco_tras={"var": "cruzado", "ang": ang})
    m0, out = mascara_braco(pose)
    out = out.copy()
    for a2 in rastros:
        m, img = mascara_braco(dict(base, braco_tras={"var": "cruzado", "ang": a2}))
        m = m & ~m0
        m[:, :PEITO_X] = False
        out[m, :3] = fantasma(img[m, :3])
        out[m, 3] = 255
    x, y = ponta(m0)
    ys = np.nonzero(m0[:, x - 20:x + 1].any(1))[0]
    for yy, comp in ((ys.min() - 5, 70), (ys.max() + 5, 50)):  # riscos de velocidade acima e abaixo do braço
        faixa = out[yy:yy + 2, x - 30 - comp:x - 30]
        faixa[faixa[..., 3] == 0] = bz.BRANCO
    if vento_x:
        out = bz.vento(out, x + vento_x, y, alt=40)
    return out


def quadros():
    """[(imagem, ticks, nome)] da ação 810 (139 ticks) e da 800 (12 ticks)."""
    seg = render(SEGURA)
    # ângulos do braço de perto: alto (rosto) de 0 a 6, baixo (estômago) de 10 a 16
    A = {"alto": (2, (8, 14)), "baixo": (13, (3, 8)), "alto2": (5, (12, 0)), "baixo2": (10, (16, 4))}
    def r(k, vento=0):
        ang, rastros = A[k]
        return rajada(ang, rastros, alto=k.startswith("alto"), vento_x=vento)
    # a pancada de dano (6 de preparo, 6 de contato, 5 segurando), com três socos na tela
    def ciclo(dano, f1, f2):
        return [(seg, 2, "segura"), (r(f1), 2, f"rajada {f1}"), (r(f2), 2, f"rajada {f2}"),
                (r(dano, 16), 3, f"contato {dano}"), (r(dano), 2, f"contato {dano}"), (seg, 1, "segura"),
                (r(f1), 2, f"rajada {f1}"), (r(f2), 3, f"rajada {f2}")]
    seq = [(render(ALCANCA), 4, "alcança"), (seg, 12, "segura")]
    for dano, f1, f2 in (("alto", "baixo2", "alto2"), ("baixo", "alto2", "baixo2"), ("alto2", "baixo", "alto"),
                         ("baixo2", "alto", "baixo"), ("alto", "baixo2", "alto2")):
        seq += ciclo(dano, f1, f2)
    # final: solta a gola e prepara (10), soco reto inteiro nítido (10), segura (6), volta (12)
    prep = render(PREPARO_FINAL)
    sr = {d: _q("soco_reto", d) for d in (3, 6, 8)}
    xs = np.nonzero(sr[3][..., 3] > 0)[1]
    xr = int(xs.max())
    ys = np.nonzero(sr[3][:, xr - 20:, 3] > 0)[0]
    yr = int(np.median(ys))
    seq += [(seg, 3, "solta a gola"), (prep, 7, "preparo do final"),
            (bz.vento(sr[3], xr + 20, yr, alt=64, larg=44), 4, "soco reto"),
            (bz.vento(sr[3], xr + 34, yr, alt=80, larg=56), 6, "soco reto"),
            (sr[3], 6, "segura o soco"), (sr[6], 6, "volta"), (sr[8], 6, "volta")]
    assert sum(t for _, t, _ in seq) == 139, sum(t for _, t, _ in seq)
    pega = [(render(ALCANCA), 3, "alcança"), (seg, 9, "segura")]
    return seq, pega


def gravar(nome, acao, seq):
    for pasta in ("quadros_karate_hd", "quadros_karate"):
        shutil.rmtree(SPR / pasta / nome, ignore_errors=True)
        (SPR / pasta / nome).mkdir(parents=True)
    els = []
    for i, (img, t, de) in enumerate(seq):
        img = firme.tapar_buracos(firme.sem_migalha(img))
        Image.fromarray(img).save(SPR / "quadros_karate_hd" / nome / f"{i:02d}.png")
        Image.fromarray(np.ascontiguousarray(img[1::3, 1::3])).save(SPR / "quadros_karate" / nome / f"{i:02d}.png")
        els.append({"desenho": i, "ticks": t, "caixa": False, "de": de})
    tempos = {"acao": acao, "caixa": None, "origem": sorted({e["de"] for e in els}), "elementos": els}
    for pasta in ("quadros_karate_hd", "quadros_karate"):
        (SPR / pasta / nome / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False),
                                                         encoding="utf-8")
    print(nome, acao, len(els), "desenhos,", sum(e["ticks"] for e in els), "ticks")


firme.configurar("hazak")
KIT = firme.ler_kit()

if __name__ == "__main__" and "--binds" not in sys.argv:
    s, p = quadros()
    gravar("agarrao_karate", 810, s)
    gravar("agarrao_karate_pega", 800, p)


# o oponente fica preso na mão que agarra a gola (punho a ~56 do eixo): mais longe que o abraço de antes (30). O Diabo
# (var(20) > 0) usa o mesmo estado com o agarrão dele e continua com a distância de antes.
BIND = {"30": "60", "35": "65"}


def binds():
    """Distância do oponente preso no estado 810 (rode depois do gerar_hazaki.py/agarrao_mk.py e do ligar_pecas)."""
    import re
    arq = RAIZ / "chars/hazaki/hazaki.cns"
    cns = arq.read_text(encoding="utf-8")
    m = re.search(r"^\[Statedef 810\]\n.*?(?=^\[Statedef)", cns, re.M | re.S)
    bloco = m.group(0)
    n = 0
    for a, b in BIND.items():
        bloco, k = re.subn(rf"(type = TargetBind\n(?:trigger.*\n)+)pos = {a}, 0",
                           rf"\1pos = ifelse(var(20) > 0, {a}, {b}), 0", bloco)
        n += k
    # o soco final joga o oponente para a FRENTE (o abraço virava antes e jogava para trás dele). Segurando ←
    # continua como era: por cima, para o outro lado (824). O Diabo continua como era.
    trocas = [
        ("[State 810, Vira antes]\ntype = Turn\ntrigger1 = Time = 111\ntrigger1 = !var(2)\n",
         "[State 810, Vira antes]\ntype = Turn\ntrigger1 = Time = 111\ntrigger1 = var(20) > 0 && !var(2)\n"),
        ("[State 810, Vira]\ntype = Turn\ntrigger1 = Time = 121\n",
         "[State 810, Vira]\ntype = Turn\ntrigger1 = Time = 121\ntrigger1 = var(20) > 0 || var(2)\n"),
    ]
    for a, b in trocas:
        if b in bloco:
            continue
        assert a in bloco, a
        bloco = bloco.replace(a, b)
    arq.write_text(cns[:m.start()] + bloco + cns[m.end():], encoding="utf-8", newline="\n")
    print(f"810: {n} TargetBind com a distância do karatê; soco final joga para a frente")


if __name__ == "__main__" and "--binds" in sys.argv:
    binds()
