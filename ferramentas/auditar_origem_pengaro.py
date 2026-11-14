#!/usr/bin/env python3
"""De onde vem cada quadro de cada ação da forma básica do Pengaró (issue #42: nada de misturar desenhos).

  python3 ferramentas/auditar_origem_pengaro.py [PASTA_TEMP]

Roda o gerar_pengaro.py numa pasta temporária (não mexe em chars/pengaro) com um espião no hd.aplicar, que anota a
origem de cada sprite do corpo:
  nova    gêmeo 3x de quadros_arcade_hd/<folha>/NN.png (as folhas_novas do redesenho do Breno)
  endiab  gêmeo 3x de quadros_arcade_hd/e_<folha>/ (o Endiabrado, que não muda)
  antigo  arte antiga de sprites/pengaro/quadros/<folha>/ (e antigo-meio: quadro do meio do Blender antigo)
  codigo  sem gêmeo 3x: montado por código ou quadro do meio antigo, só ampliado de 1x
e lista as ações do corpo que usam algo além de nova/endiab. Saída vazia = um conjunto só de desenhos.
"""
import json
import re
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas"))

import numpy as np  # noqa: E402

import gerar_pengaro as gp  # noqa: E402
import hd  # noqa: E402


def main():
    tmp = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.mkdtemp())
    saida = tmp / "pengaro"
    shutil.rmtree(saida, ignore_errors=True)
    shutil.copytree(RAIZ / "chars/pengaro", saida)  # os passos finais (sons, parry) leem o que já existe
    origem, nomes = {}, {}
    original = hd.aplicar

    def espiao(s, air, cns, pares, vitima=frozenset(), gemeos=None):
        gemeos = gemeos or {}
        novos, antigos = hd.Indice(pares), hd.Indice([(gp.QUADROS, gp.QUADROS)])
        for g, i, img, *_ in s.lista:
            a = np.asarray(img.convert("RGBA"))
            cx = hd._caixa(a)
            if g == 9000 or not cx:
                continue
            rec = a[cx[1]:cx[3], cx[0]:cx[2]]
            achado = novos.achar(rec)
            if achado:
                p = str(Path(achado[1]).relative_to(gp.QUADROS_ARCADE_HD))
                origem[(g, i)] = ("endiab" if p.startswith("e_") else "meio-novo" if "/meio/" in p else "nova", p)
            elif gemeos.get(id(img), (None,))[0] is img:
                origem[(g, i)] = ("endiab", "montado")
            else:
                velho = antigos.achar(rec)
                if velho:
                    p = str(Path(velho[1]).relative_to(gp.QUADROS))
                    origem[(g, i)] = ("antigo-meio" if "/meio/" in p else "antigo", p)
                else:
                    origem[(g, i)] = ("codigo", "")
        nomes.update({gi: n for n, gi in s.codigos.items()})
        return original(s, air, cns, pares, vitima, gemeos)

    hd.aplicar = espiao
    gp.SAIDA = saida
    gp.main()
    air = (saida / "pengaro.air").read_text(encoding="utf-8")
    efeito, _ = hd.acoes_de_efeito((saida / "pengaro.cns").read_text(encoding="utf-8"))
    partes = re.split(r"^\[Begin Action (\d+)\]", air, flags=re.M | re.I)
    ruins = {}
    for k in range(1, len(partes), 2):
        n = int(partes[k])
        if n in efeito or n >= 9000:
            continue
        els = [(int(g), int(i)) for g, i in re.findall(r"^\s*(-?\d+)\s*,\s*(-?\d+)\s*,", partes[k + 1], re.M)]
        cats = Counter(origem[e][0] for e in els if e in origem)
        if set(cats) - {"nova", "endiab"}:
            ruins[n] = {"origens": dict(cats),
                        "fora": sorted({(nomes.get(e, "?"), *origem[e]) for e in els
                                        if e in origem and origem[e][0] not in ("nova", "endiab")})}
    for n, r in ruins.items():
        print(n, r["origens"])
        for f in r["fora"][:12]:
            print("    ", f)
    (tmp / "origem_pengaro.json").write_text(json.dumps(ruins, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{len(ruins)} ações misturam desenhos (detalhes em {tmp / 'origem_pengaro.json'})")


if __name__ == "__main__":
    main()
