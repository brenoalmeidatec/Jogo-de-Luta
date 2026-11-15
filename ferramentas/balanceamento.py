#!/usr/bin/env python3
"""Balanceamento dos lutadores (missão 2026-11-14, item 7): uma tabela só com os números que mudaram.

  python3 ferramentas/balanceamento.py            aplica em chars/<lutador>/ (pode rodar de novo: troca o valor)

Mexe só nas chaves do [Data] e do [Velocity] do .cns (attack, defence, life, walk.fwd, run.fwd...). Cada golpe
continua com o dano dele; o attack multiplica o dano de tudo que o lutador acerta e o defence divide o que ele leva.
Os gerar_<lutador>.py chamam `aplicar` no fim, para o número não voltar quando o lutador for regerado.
Os porquês e os resultados do torneio CPU x CPU (ferramentas/torneio_cpu.py) estão no LOGBOOK.md.
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Antes (2026-11-14): todos attack 100 / defence 100 / life 1000, menos o Hazak (life 900, defence 90).
TABELA = {
    "pengaro": {},
    "ck": {"attack": "125", "defence": "105", "walk.fwd": "3.4", "run.fwd": "7.0, 0"},
    "gutto": {"attack": "90"},
    "hazaki": {"attack": "125", "defence": "100"},
    "raiclaven": {"attack": "90"},
}


def ajustar(cns, valores):
    for chave, valor in valores.items():
        novo, n = re.subn(rf"(?m)^({re.escape(chave)}\s*=\s*)[^;\r\n]*?(\s*(;[^\r\n]*)?)$",
                          lambda m: m.group(1) + valor + (" " + m.group(3) if m.group(3) else ""), cns, count=1)
        if n != 1:
            raise SystemExit(f"não achei '{chave}' no .cns")
        cns = novo
    return cns


def aplicar(lutador, pasta=None):
    arq = Path(pasta or RAIZ / "chars" / lutador) / f"{lutador}.cns"
    txt = arq.read_bytes().decode("utf-8")
    novo = ajustar(txt, TABELA.get(lutador, {}))
    if novo != txt:
        arq.write_bytes(novo.encode("utf-8"))
    if TABELA.get(lutador):
        print(f"{lutador}: balanceamento " + ", ".join(f"{k} = {v}" for k, v in TABELA[lutador].items()))


if __name__ == "__main__":
    for nome in sys.argv[1:] or TABELA:
        aplicar(nome)
