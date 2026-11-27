#!/usr/bin/env python3
"""Calcula o guard.hittime de cada golpe a partir da vantagem medida no motor (ferramentas/vantagem.py) e grava
ferramentas/mecanica_guarda.json, que o ferramentas/mecanica.py aplica.

  python3 ferramentas/calibrar_guarda.py MEDIDA.json [--ajuste MEDIDA_DEPOIS.json]

Alvo da vantagem quando o golpe é defendido (padrão dos jogos de luta grandes: SF/KOF):
  - golpe que não derruba: a vantagem no acerto menos 6, no máximo +2 (fraco fica perto de 0, médio -2 a -5, forte -5 a -9);
  - golpe normal ou corrente que derruba: -12 (dá para punir com um golpe médio);
  - especial que derruba: -8; super: -14;
  - antiaéreo (animtype Up) e o afastar de defesa (720): ficam como estão (o Breno quer antiaéreo bem punível).
Só deixa a defesa MENOS punida do que está: se o golpe já está melhor que o alvo, não mexe.

Sem --ajuste: o guard.hittime sai da trava de hoje (o deslize do golpe, ground.slidetime) mais a diferença para o alvo.
Com --ajuste: corrige a tabela atual pela diferença que ainda sobrou na medida nova (segunda volta).
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TABELA = RAIZ / "ferramentas" / "mecanica_guarda.json"


def deslize(lutador, estado):
    txt = (RAIZ / "chars" / lutador / f"{lutador}.cns").read_text(encoding="utf-8", errors="replace")
    m = re.search(rf"(?ms)^\[Statedef {estado}\]\n(.*?)(?=^\[Statedef |\Z)", txt)
    vals = re.findall(r"(?m)^ground\.slidetime\s*=\s*(\d+)", m.group(1)) if m else []
    return int(vals[-1]) if vals else 0


def alvo(estado, r):
    hit, dfs = r.get("hit", {}), r.get("def", {})
    if "vantagem" not in dfs or dfs.get("res") != "def" or "vantagem" not in hit:
        return None
    if estado == 720 or (r.get("anim") or "").lower() == "up":
        return None
    caiu = hit.get("caiu") == "sim"
    if not caiu:
        return min(int(hit["vantagem"]) - 6, 2)
    if 3000 <= estado <= 3399:
        return -14
    if 1000 <= estado <= 2999 or 4000 <= estado <= 4999:
        return -8
    return -12


def main():
    args = sys.argv[1:]
    medida = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    ajuste = None
    if "--ajuste" in args:
        ajuste = json.loads(Path(args[args.index("--ajuste") + 1]).read_text(encoding="utf-8"))
    tabela = json.loads(TABELA.read_text(encoding="utf-8")) if TABELA.exists() else {}
    for lutador, golpes in medida.items():
        saida = tabela.get(lutador, {}) if ajuste else {}
        for e, r in golpes.items():
            n = int(e)
            a = alvo(n, r)
            if a is None:
                continue
            hoje = int(r["def"]["vantagem"])
            if ajuste:
                if e not in saida:
                    continue
                novo = ajuste.get(lutador, {}).get(e, {}).get("def", {})
                if "vantagem" not in novo or novo.get("res") != "def":
                    continue
                saida[e] = max(1, int(saida[e]) + a - int(novo["vantagem"]))
            elif hoje < a:
                saida[e] = max(1, deslize(lutador, n) + a - hoje)
        tabela[lutador] = dict(sorted(saida.items(), key=lambda kv: int(kv[0])))
        print(f"{lutador}: {len(tabela[lutador])} golpes com guard.hittime")
    TABELA.write_text(json.dumps(tabela, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
