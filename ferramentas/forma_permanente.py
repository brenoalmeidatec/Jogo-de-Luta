#!/usr/bin/env python3
"""Endiabrado até o fim da luta (Breno, 2026-11-14 à noite, docs/missao-alisson-cenarios.md seção 4.1).

  python3 ferramentas/forma_permanente.py [lutador ...]     aplica em chars/<lutador>/ (pode rodar de novo)

Pós-passo no .cns, como o cena_transformacao.py; os gerar_<lutador>.py chamam `aplicar` por último.

Quem desperta fica na forma até a luta acabar: não volta por tempo nem no fim do round, e a música da forma segue.

- O contador que descia o var(20) a cada tique sai: o var(20) fica parado em 600 enquanto a forma durar.
- var(58) = 1 marca "já despertou nesta luta". Ele atravessa os rounds (IntPersistIndex = 58 no [Data]; o motor zera os
  outros). No round seguinte, com var(58) = 1 e var(20) zerado, a forma volta já na apresentação.
- var(59) = 1 marca "a música da forma está tocando". O motor recomeça a música do cenário a cada round (medido com
  testar_musica.py --rounds), então na apresentação do round seguinte a música da forma entra de novo, direto, sem
  esperar a do cenário baixar.
- O super da forma (estado 3100) não encerra mais a forma (o "Fim Despertar" sai). Em troca custa 2 estoques na forma,
  como fora dela (antes custava 1 e acabava com a forma, ou no CK valia só nos 10 s).
- O cenário destruído (seção 4.2) é da thread dos cenários (ferramentas/destruicao.py), que lê o mesmo var(20) > 0.
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LUTADORES = ("pengaro", "ck", "gutto", "raiclaven", "hazaki")
MARCA = "; Forma até o fim da luta (forma_permanente.py)\n"

BLOCOS = MARCA + """[State -2, Forma fica: marca que despertou]
type = VarSet
trigger1 = var(20) > 0
var(58) = 1

[State -2, Forma fica: volta no round seguinte]
type = VarSet
trigger1 = var(58) = 1 && var(20) <= 0
var(20) = 600

[State -2, Forma fica: marca a musica]
type = VarSet
trigger1 = var(51) = 1
var(59) = 1

[State -2, Forma fica: musica volta no round seguinte]
type = PlayBGM
trigger1 = var(59) = 1 && var(51) = 0 && roundstate >= 1
bgm = "despertar.ogg"
volume = 100
loop = 1
loopstart = @LOOPSTART@

[State -2, Forma fica: musica marcada no round seguinte]
type = VarSet
trigger1 = var(59) = 1 && var(51) = 0 && roundstate >= 1
var(51) = 1

"""


def aplicar(lutador, pasta=None):
    arq = Path(pasta or RAIZ / "chars" / lutador) / f"{lutador}.cns"
    txt = arq.read_text(encoding="utf-8")
    if "[Statedef 2000]" not in txt:
        print(f"{lutador}: sem Despertar, nada a fazer")
        return
    novo = re.sub(re.escape(MARCA) + r"(?:\[State -2, Forma fica:[^\n]*\n(?:[^\n\[][^\n]*\n)*\n?)+", "", txt)
    if re.search(r"var\((58|59)\)", novo):
        raise SystemExit(f"{lutador}: var(58)/var(59) já em uso")
    loop = re.search(r"(?ms)^\[State -2, Musica do Despertar entra\].*?^loopstart\s*=\s*(\d+)", novo)
    novo, n = re.subn(r"(?m)^(IntPersistIndex\s*=\s*)\d+", r"\g<1>58", novo, count=1)
    if n != 1:
        raise SystemExit(f"{lutador}: sem IntPersistIndex no [Data]")
    # o contador de tempo da forma sai
    novo = re.sub(r"(?m)^\[State -2, Conta (Despertar|Diabo Loiro)\]\n(?:[^\n\[][^\n]*\n)*\n?", "", novo)
    # o super 3100 não encerra a forma e custa 2 estoques (balanceamento da forma permanente)
    novo = re.sub(r"(?m)^\[State 3100, Fim Despertar\]\n(?:[^\n\[][^\n]*\n)*\n?", "", novo)
    novo = novo.replace("value = ifelse(var(20) > 0, -1000, -2000)", "value = -2000")
    cmd = arq.with_suffix(".cmd")
    c0 = cmd.read_bytes().decode("utf-8")
    c1 = re.sub(r"(?m)^(value = 3100\r?\ntriggerall = command = \"\w+\"\r?\ntriggerall = power >= )1000", r"\g<1>2000", c0)
    if c1 != c0:
        cmd.write_bytes(c1.encode("utf-8"))
    # os blocos entram antes da música: depois do "zera na intro" de cada um e antes de a música olhar o var(20)
    ancora = "[State -2, Musica do cenario comeca a baixar]\n"
    if novo.count(ancora) != 1:
        raise SystemExit(f"{lutador}: não achei a música do Despertar no [Statedef -2] (rode o cena_transformacao.py antes)")
    novo = novo.replace(ancora, BLOCOS.replace("@LOOPSTART@", loop.group(1) if loop else "0") + ancora)
    if novo != txt:
        arq.write_text(novo, encoding="utf-8", newline="\n")
    print(f"{lutador}: forma até o fim da luta (var 58/59)")


if __name__ == "__main__":
    for nome in sys.argv[1:] or LUTADORES:
        aplicar(nome)
