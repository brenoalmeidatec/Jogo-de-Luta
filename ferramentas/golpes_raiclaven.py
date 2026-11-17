#!/usr/bin/env python3
"""Golpes do Raiclaven no boneco de peças, por desenho: cada desenho de hoje (sprites/raiclaven/quadros/<pasta>/NN)
ganha uma pose-chave montada com o kit (POSE abaixo), e toda ação do jogo que usa só desenhos com pose é refeita com
os mesmos ticks e a caixa no mesmo tempo (docs/boneco-pecas/raiclaven/mapa_acoes.json, de ferramentas/mapa_acoes.py).

  python ferramentas/golpes_raiclaven.py                 todas as ações que dá para montar
  python ferramentas/golpes_raiclaven.py 215 216          só essas
  python ferramentas/golpes_raiclaven.py --lista          mostra quais ações dá e quais desenhos faltam

Saída: sprites/raiclaven/quadros_pecas_hd/a<ação>/ (3x) e quadros_pecas/a<ação>/ (1x) com tempos.json, e o robô de
defeitos em docs/boneco-pecas/raiclaven/robo_golpes.md. Depois: python ferramentas/ligar_pecas.py raiclaven (todas as
pastas, sempre) e o robô de luta.

Regra do Alisson (17/11): golpe natural, nada de braço que estica sozinho. O peso vai para trás antes, o pé da frente
dá o passo e o quadril entra no golpe; braço erguido usa o desenho do braço erguido (variante), não a peça girada
para trás.
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import piloto_raiclaven as R  # noqa: E402  (configura o kit do Raiclaven)
import piloto_firme as pf  # noqa: E402
import boneco_ajuste as b  # noqa: E402
import vida_pecas as vida  # noqa: E402

P = R.P
ESP = R.ESP
MAPA = R.DOCS / "mapa_acoes.json"

# ------------------------------------------------------------------ pose-chave de cada desenho de hoje
POSE = {
    # guarda e parado
    **{f"ginga/{i:02d}": p for i, p in enumerate(R.POSES["parado"])},
    # martelo: arma o braço de metal, ergue a tesoura acima da cabeça, desce num corte com passo e quadril baixo
    "martelo/00": P(),
    "martelo/01": P(q=(-6, 6), tronco=-4, cabeca=-3, braco="armado", bf=-10),
    "martelo/02": P(q=(-8, 2), tronco=-5, cabeca=-4, braco="alto", bf=-15),
    "martelo/03": P(q=(8, 14), tronco=6, cabeca=3, braco="frente", bt=22, bf=10, pe_frente=16),
    "martelo/04": P(q=(20, 20), tronco=8, cabeca=5, braco="estocada", bt=34, bf=20, pe_frente=32, pe_tras=8),
    "martelo/05": P(q=(10, 16), tronco=6, cabeca=2, braco="frente", bt=6, bf=-4, pe_frente=20),
    "martelo/06": P(q=(-2, 4), tronco=-2, cabeca=-2, braco="alto", bf=-12),
    "martelo/07": P(q=(1, 1), bt=-2, abt=2, bf=2),
    # cabeçada (golpe agachado que sobe): agachado com a tesoura baixa, levanta, arma o braço e sobe a tesoura aberta
    # acima da cabeça (antiaéreo), volta a agachar
    "cabecada/00": P(baixo="agachado", tronco=6, cabeca=2, bt=12, abt=-10, bf=6),
    "cabecada/01": P(q=(0, 22), tronco=4, cabeca=1, braco="frente", bt=40, bf=4),
    "cabecada/02": P(q=(2, 12), tronco=2, braco="frente", bt=10),
    "cabecada/03": P(q=(6, 4), tronco=-2, cabeca=-3, braco="armado", bf=-10, pe_frente=10),
    "cabecada/04": P(q=(8, 0), tronco=-4, cabeca=-5, braco="alto", bf=-14, pe_frente=12),
    "cabecada/05": P(q=(6, 2), tronco=-3, cabeca=-4, braco="alto", bt=6, bf=-12, pe_frente=12),
    "cabecada/06": P(q=(0, 18), tronco=4, cabeca=1, bt=8, abt=-6),
    "cabecada/07": P(baixo="agachado", tronco=5, cabeca=2, bt=10, abt=-8),
    # agachar: desce em três desenhos e fica agachado respirando (metade de baixo agachada = peça do agachado/04)
    "agachado/00": P(),
    "agachado/01": P(q=(0, 14), tronco=2, bt=2),
    "agachado/02": P(q=(0, 24), tronco=4, cabeca=1, bt=6, abt=-4),
    "agachado/03": P(baixo="agachado", tronco=3, cabeca=1, bt=6, abt=-4),
    "agachado/04": P(baixo="agachado", tronco=2, bt=4, abt=-2),
    "agachado/05": P(baixo="agachado", q=(0, 2), tronco=3, cabeca=1, bt=5, abt=-3),
    "agachado/06": P(baixo="agachado", q=(0, 3), tronco=3, cabeca=1, bt=6, abt=-4),
    "agachado/07": P(baixo="agachado", q=(0, 1), tronco=2, bt=4, abt=-2),
    # rasteira: agachado, tira a vassoura e ergue ao lado da cabeça, varre rente ao chão para a frente e guarda
    "rasteira/00": P(baixo="agachado", tronco=6, cabeca=1, bt=8, bf=30),
    "rasteira/01": P(baixo="agachado", tronco=4, mao="vassoura", bf=-10, bt=6),
    "rasteira/02": P(baixo="agachado", tronco=3, mao="vassoura", bt=6),
    "rasteira/03": P(baixo="agachado", tronco=6, cabeca=2, mao="varre", bt=10, bf=-6),
    "rasteira/04": P(baixo="agachado", q=(10, 0), tronco=10, cabeca=3, mao="varre", bf=-35, bt=12),
    "rasteira/05": P(baixo="agachado", q=(8, 0), tronco=10, cabeca=3, mao="varre", bf=-25, bt=12),
    "rasteira/06": P(baixo="agachado", tronco=4, mao="vassoura", bf=-6, bt=6),
    "rasteira/07": P(baixo="agachado", tronco=6, cabeca=1, bt=8, bf=30),
    # golaço: abaixa e puxa o pente para trás, ergue a tesoura, avança o pé e lança o pente com o braço todo
    # esticado (o tronco e o quadril vão junto), e desce na base baixa com a tesoura à frente
    "golaco/00": P(),
    "golaco/01": P(q=(-4, 22), tronco=8, cabeca=3, bt=12, abt=-8, bf=14, abf=10),
    "golaco/02": P(q=(-6, 16), tronco=-2, cabeca=-2, braco="alto", bf=12, abf=12),
    "golaco/03": P(q=(14, 18), tronco=8, cabeca=3, mao="arremesso", bt=22, abt=-6, pe_frente=20),
    "golaco/04": P(baixo="agachado", q=(6, 0), tronco=10, cabeca=3, bt=28, abt=-8, bf=-4),
    # armada (chute girando de costas): gira no pé de apoio (desenhos de costas inteiros), a perna sobe esticada na
    # altura da cabeça, recolhe e o pé volta ao chão na guarda
    "armada/00": P(q=(2, 2), tronco=1, bt=2, abt=-2),
    "armada/01": ESP("armada/01"),
    "armada/02": ESP("armada/02"),
    "armada/03": ESP("armada/03"),
    "armada/04": P(q=(-10, -4), tronco=-10, cabeca=-4, bt=10, abt=-6, bf=-10, abf=-12, perna="esticada"),
    "armada/05": P(q=(-6, -2), tronco=-5, cabeca=-2, bt=8, abt=-4, bf=-4, abf=-6, perna="baixa"),
    "armada/06": P(q=(2, 4), tronco=1, bt=3, abt=-2, pe_frente=8),
    "armada/07": P(q=(1, 1), bt=-2, abt=2, bf=2),
    # agarrão: tira a toalha, passa nas duas mãos e gira por cima da cabeça (desenhos inteiros: a toalha não é peça),
    # estica o braço agarrando, penteia o cabelo e volta à guarda
    "agarrao/00": P(),
    "agarrao/01": ESP("agarrao/01"),
    "agarrao/02": ESP("agarrao/02"),
    "agarrao/03": ESP("agarrao/03"),
    "agarrao/04": ESP("agarrao/04"),
    "agarrao/05": P(q=(10, 8), tronco=5, cabeca=2, mao="agarra", bt=6, abt=-4, pe_frente=14),
    "agarrao/06": P(q=(2, 3), tronco=0, mao="cabelo", bt=2, abt=-2),
    "agarrao/07": P(q=(1, 1), bt=-2, abt=2, bf=2),
    # pente_combo: sai do rolamento, estoca o pente, ergue a tesoura, gira (desenho inteiro) e corta duas vezes com a
    # tesoura à frente, e termina penteando o cabelo
    # soco no ar e levantar: no ar e no chão o kit de pé não serve; ficam os desenhos de hoje inteiros (mesma folha
    # do kit, mesma cara e mesmas cores), e o fim do levantar entra na guarda do kit
    **{f"ar_soco/{i:02d}": ESP(f"ar_soco/{i:02d}") for i in range(8)},
    **{f"levanta/{i:02d}": ESP(f"levanta/{i:02d}") for i in range(1, 7)},
    "levanta/07": P(),
    "rolamento/05": P(baixo="agachado", tronco=6, cabeca=2, bt=8, abt=-8, bf=6),  # sai do rolamento
    "rolamento/06": P(q=(2, 6), tronco=2, cabeca=1, bt=4, abt=-4, bf=-4),
    "pente_combo/01": P(q=(12, 10), tronco=6, cabeca=2, mao="arremesso", bt=18, abt=-6, pe_frente=18),
    "pente_combo/02": P(q=(-6, 8), tronco=-3, cabeca=-2, braco="alto", bf=10, abf=12),
    "pente_combo/04": ESP("pente_combo/04"),
    "pente_combo/05": P(q=(12, 10), tronco=5, cabeca=2, braco="frente", bt=2, bf=8, pe_frente=20),
    "pente_combo/06": P(q=(16, 12), tronco=7, cabeca=3, braco="estocada", bt=-2, bf=10, pe_frente=24, pe_tras=6),
    "pente_combo/07": P(q=(2, 3), tronco=0, mao="cabelo", bt=2, abt=-2),
}


# sprite do jogo que o mapa casou errado, conferido de olho: o desenho certo
SPRITE_E = {
    (894, 0): "martelo/04",  # idem, a variante do 343
    # soco no ar (600, 601): encolhido no pulo, tesoura erguida, estocada para baixo e volta encolhido
    (462, 0): "ar_soco/00", (463, 0): "ar_soco/02", (465, 0): "ar_soco/04", (467, 0): "ar_soco/07",
    # levantar (5120): sentado no chão, apoia na tesoura, sobe e fica na guarda
    **{(398 + i, 0): f"levanta/{i + 1:02d}" for i in range(7)},
    (893, 0): "martelo/04",  # contato do martelo forte (210, 302, 343, 344): passo longo, tesoura lá embaixo à frente
}


def acoes():
    m = json.loads(MAPA.read_text(encoding="utf-8"))
    out, faltam = {}, {}
    for num, els in m.items():
        els = [dict(e, desenho=SPRITE_E[tuple(e["sprite"])], iou=1.0) if tuple(e["sprite"]) in SPRITE_E else e
               for e in els]
        num = int(num)
        if num >= 10000:  # despertado: o ligar_pecas cuida pelo remap
            continue
        # casamento firme (>0.85) vale sempre; um fraco (>0.7) só vale se for da mesma pasta de um vizinho firme
        # (o contato do martelo e da cabeçada é o mesmo desenho com a lâmina borrada; o 893 do 210 não é agachado)
        firmes = [e["desenho"] if e["iou"] > 0.85 else None for e in els]
        ds = []
        for k, e in enumerate(els):
            viz = {str(d).split("/")[0] for d in firmes[max(0, k - 3):k + 4] if d}
            ok = e["iou"] > 0.85 or (e["iou"] > 0.7 and str(e["desenho"]).split("/")[0] in viz)
            if not ok and 0.6 < e["iou"] <= 0.7 and ds and ds[-1] is not None and \
                    str(ds[-1]).split("/")[0] in viz:
                ds.append(ds[-1])  # quadro de meio desenhado à parte (0.6-0.7): segue o desenho anterior
                continue
            ds.append(e["desenho"] if ok else None)
        sem = [d for d in ds if d not in POSE]
        if not sem:
            out[num] = [dict(e, desenho=d) for e, d in zip(els, ds)]
        elif len(sem) < len(ds):
            faltam[num] = sorted({str(d) for d in sem})
    return out, faltam


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    todas, faltam = acoes()
    if "--lista" in sys.argv:
        print("dá para montar:", sorted(todas))
        for n, f in sorted(faltam.items()):
            print(f"  {n}: falta {f}")
        return
    so = {int(a) for a in args}
    kit = R.separar(b.ler_kit())
    pf.PES_REF = None
    pf.MANCHA_REF = R.mancha_maxima(kit)
    ref = b.abrir(b.REF)
    relatorio = ["| ação | desenhos | robô de defeitos |", "|---|---|---|"]
    for num, els in sorted(todas.items()):
        if so and num not in so:
            continue
        if num == 0 or num == 200 or num == 240:
            continue  # parado, soco e chute alto: piloto_raiclaven.py
        elems, bate = [], set()
        for k, e in enumerate(els):
            elems.append((f"{e['desenho']}#{k}", e["ticks"] if e["ticks"] > 0 else 1))
            if e["caixa"]:
                bate.add(k)
        poses = {q: POSE[q.split("#")[0]] for q, _ in elems}
        quadros = vida.animar(poses, elems, bate=bate or None, laco=False, guarda=P())
        quadros = vida.atrasar(quadros, laco=False)
        nome = f"a{num}"
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            shutil.rmtree(R.SPR / pasta / nome, ignore_errors=True)
            (R.SPR / pasta / nome).mkdir(parents=True)
        defeitos = []
        for i, (pose, t, caixa_on, q) in enumerate(quadros):
            out = R.desenhar(kit, R.plantar(pose))
            # quadro especial é o desenho de hoje inteiro (no ar, no chão, de costas): o robô do kit não se aplica
            erros = [] if "_especial" in pose else pf.conferir(out, ref, None)
            if erros:
                defeitos.append(f"{i:02d} ({q.split('#')[0]}): {'; '.join(erros)}")
            Image.fromarray(out).save(R.SPR / "quadros_pecas_hd" / nome / f"{i:02d}.png")
            Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(R.SPR / "quadros_pecas" / nome / f"{i:02d}.png")
        tempos = {"acao": num, "elementos": [{"desenho": i, "ticks": t, "caixa": c, "de": q.split("#")[0]}
                                            for i, (_, t, c, q) in enumerate(quadros)]}
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            (R.SPR / pasta / nome / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False),
                                                             encoding="utf-8")
        relatorio.append(f"| {num} | {len(quadros)} | {'PASS' if not defeitos else '<br>'.join(defeitos)} |")
        print(num, len(quadros), "desenhos", "PASS" if not defeitos else f"{len(defeitos)} com defeito", flush=True)
    falhas = sum("PASS" not in l for l in relatorio[2:])
    (R.DOCS / "robo_golpes.md").write_text("\n".join(relatorio) + f"\n\n{falhas} ação(ões) com defeito.\n",
                                           encoding="utf-8")
    print(f"{falhas} ação(ões) com defeito")


if __name__ == "__main__":
    main()
