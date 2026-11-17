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
    "cabecada/00": P(q=(-2, 26), tronco=6, cabeca=2, bt=12, abt=-10, bf=6),
    "cabecada/01": P(q=(0, 22), tronco=4, cabeca=1, braco="frente", bt=40, bf=4),
    "cabecada/02": P(q=(2, 12), tronco=2, braco="frente", bt=10),
    "cabecada/03": P(q=(6, 4), tronco=-2, cabeca=-3, braco="armado", bf=-10, pe_frente=10),
    "cabecada/04": P(q=(8, 0), tronco=-4, cabeca=-5, braco="alto", bf=-14, pe_frente=12),
    "cabecada/05": P(q=(6, 2), tronco=-3, cabeca=-4, braco="alto", bt=6, bf=-12, pe_frente=12),
    "cabecada/06": P(q=(0, 20), tronco=4, cabeca=1, bt=8, abt=-6),
    "cabecada/07": P(q=(-1, 24), tronco=5, cabeca=2, bt=10, abt=-8),
}


def acoes():
    m = json.loads(MAPA.read_text(encoding="utf-8"))
    out, faltam = {}, {}
    for num, els in m.items():
        num = int(num)
        if num >= 10000:  # despertado: o ligar_pecas cuida pelo remap
            continue
        ds = [e["desenho"] if e["iou"] > 0.6 else None for e in els]
        sem = [d for d in ds if d not in POSE]
        if not sem:
            out[num] = els
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
            erros = pf.conferir(out, ref, None)
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
