#!/usr/bin/env python3
"""Piloto do boneco de peças (docs/missao-alisson-boneco-de-pecas.md, etapa 1): parado, soco e chute alto do Pengaró
base montados só com as peças do kit (sprites/pengaro/pecas/), sem mexer no gerador nem no .sff da mugen.

  python ferramentas/piloto_pecas.py            grava quadros_pecas_hd/<animação>/NN.png (3x) e quadros_pecas/ (1x)

Cada animação guarda também tempos.json: o desenho e os ticks de cada elemento, iguais aos da [Begin Action] de hoje
(parado 0, soco 200, chute alto 240), com a mesma caixa de golpe.
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boneco_pecas as b  # noqa: E402

GUARDA = {}
CAMARA_BAIXA = {"perna_frente": {"var": "camara", "dx": -14, "dy": 4, "ang": 14}, "perna_tras": {"ang": -6},
                "tronco": {"dx": -2}}
CAMARA = {"perna_frente": {"var": "camara", "dx": -25, "dy": -10}, "perna_tras": {"ang": -12}, "tronco": {"dx": -4},
          "braco_frente": {"dx": 2}}
ANIMACOES = {
    # parado: respiração e balanço da ginga; só o tronco desce (o quadril e os pés ficam no chão)
    "parado": {
        "poses": [
            {},
            {"tronco": {"dy": 1}, "braco_frente": {"dx": 1}},
            {"tronco": {"dy": 2}, "braco_frente": {"dx": 1, "dy": 1}, "braco_tras": {"dy": 1}},
            {"tronco": {"dy": 3}, "braco_frente": {"dy": 1}, "braco_tras": {"dy": 1}},
            {"tronco": {"dy": 2}, "braco_frente": {"dx": -1}},
            {"tronco": {"dy": 1}},
        ],
        "acao": 0, "elementos": [(0, 6), (1, 6), (2, 5), (3, 7), (4, 7), (5, 5)],
    },
    # soco (jab, ação 200): guarda, preparo curto, contato com o braço todo esticado, recuo em 2 desenhos
    "soco": {
        "poses": [
            GUARDA,
            {"braco_frente": {"var": "punho", "dx": -5, "dy": 1}, "tronco": {"dx": -2}, "cabeca": {"dx": -1},
             "perna_tras": {"ang": 1}},
            {"braco_frente": {"var": "esticado", "dx": 2}, "tronco": {"dx": 4}, "cabeca": {"dx": 2},
             "perna_tras": {"ang": -2}},
            {"braco_frente": {"var": "punho", "dx": 1}, "tronco": {"dx": 2}},
            GUARDA,
        ],
        # 89 x4 (1+1+2), 91 x6 (2+3 com caixa, +1), 92 x3, 93 x6: o preparo é o 1, o contato o 2, o recuo 3 e 4
        "acao": 200, "elementos": [(1, 1), (1, 1), (1, 2), (2, 2, "caixa"), (2, 3, "caixa"), (2, 1), (3, 3), (4, 6)],
        "caixa": [45, -276, 153, -192],
    },
    # chute alto (ação 240): joelho sobe (câmara), contato com a perna esticada, joelho volta, pé no chão
    "chute_alto": {
        "poses": [
            GUARDA,
            CAMARA_BAIXA,
            CAMARA,
            {"perna_frente": {"var": "esticada", "dx": -25, "dy": -10}, "perna_tras": {"ang": -12},
             "tronco": {"dx": -8}, "cabeca": {"dx": -1}, "braco_frente": {"dx": 1}},
            CAMARA,
            CAMARA_BAIXA,
        ],
        # 430 x5, 431 x4, 433 x2+4 com caixa, 434 x3, 435 x12, 436 x12
        "acao": 240, "elementos": [(1, 5), (2, 4), (3, 2, "caixa"), (3, 4, "caixa"), (4, 3), (5, 12), (0, 12)],
        "caixa": [36, -300, 159, -174],
    },
}


def main():
    kit = b.ler_kit()
    for nome, an in ANIMACOES.items():
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            shutil.rmtree(b.SPR / pasta / nome, ignore_errors=True)
        for i, pose in enumerate(an["poses"]):
            b.gravar(b.montar(kit, pose), nome, i)
        tempos = {"acao": an["acao"], "caixa": an.get("caixa"),
                  "elementos": [{"desenho": e[0], "ticks": e[1], "caixa": len(e) > 2} for e in an["elementos"]],
                  "poses": an["poses"]}
        (b.SPR / "quadros_pecas_hd" / nome / "tempos.json").write_text(json.dumps(tempos, indent=1), encoding="utf-8")
        print(f"{nome}: {len(an['poses'])} desenhos, {sum(e[1] for e in an['elementos'])} ticks")


if __name__ == "__main__":
    main()
