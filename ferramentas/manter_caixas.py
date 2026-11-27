#!/usr/bin/env python3
"""Mantém as caixas (Clsn1 e Clsn2) do .air de um lutador iguais às de uma referência guardada, quadro por quadro.

O gerador mede a caixa de dano em cada desenho (gerar_hazaki.caixas_do_corpo). Com desenho novo (Hazak nítido, #36) a
medida muda alguns pixels e o Breno pediu o jogo igual: "sem mudar caixas, .air ou .cns". Este pós-passo pega cada ação
do .air novo e devolve as linhas da referência (caixas, LoopStart, comentários), trocando só as linhas de quadro
(sprite, deslocamento, ticks) pelas do .air novo, na mesma ordem. Ação com número de quadros diferente da referência
fica como o gerador fez (e é avisada).

  python ferramentas/manter_caixas.py hazaki --guardar REF_GIT   grava sprites/<lutador>/caixas_base.air do commit REF_GIT
  python ferramentas/manter_caixas.py hazaki                     aplica em chars/<lutador>/<lutador>.air

O gerar_hazaki.py chama aplicar() depois dos pós-passos que mexem no .air e antes do trocar_retratos.
"""
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CABECA = re.compile(r"^\s*\[\s*begin\s+action\s+(-?\d+)\s*\]", re.I)
QUADRO = re.compile(r"^\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+")


def referencia(lutador):
    return RAIZ / f"sprites/{lutador}/caixas_base.air"


def acoes(txt):
    """(texto antes da 1ª ação, [(número, [linhas])]) na ordem do arquivo."""
    antes, lista = [], []
    for linha in txt.splitlines():
        m = CABECA.match(linha)
        if m:
            lista.append((int(m.group(1)), [linha]))
        elif lista:
            lista[-1][1].append(linha)
        else:
            antes.append(linha)
    return antes, lista


def aplicar(lutador, pasta=None):
    ref = referencia(lutador)
    if not ref.exists():
        return 0, []
    air = Path(pasta or RAIZ / "chars" / lutador) / f"{lutador}.air"
    _, velhas = acoes(ref.read_text(encoding="utf-8"))
    velhas = dict(velhas)
    antes, novas = acoes(air.read_text(encoding="utf-8"))
    saida, trocadas, diferentes = list(antes), 0, []
    for num, linhas in novas:
        velha = velhas.get(num)
        qn = [x for x in linhas if QUADRO.match(x)]
        if velha is None or len([x for x in velha if QUADRO.match(x)]) != len(qn):
            if velha is not None:
                diferentes.append(num)
            saida += linhas
            continue
        it = iter(qn)
        saida += [next(it) if QUADRO.match(x) else x for x in velha]
        trocadas += 1
    air.write_text("\n".join(saida) + "\n", encoding="utf-8", newline="\n")
    return trocadas, diferentes


def guardar(lutador, commit):
    txt = subprocess.run(["git", "show", f"{commit}:chars/{lutador}/{lutador}.air"], cwd=RAIZ, capture_output=True,
                         check=True).stdout.decode("utf-8")
    referencia(lutador).write_text(txt, encoding="utf-8", newline="\n")
    print(f"{lutador}: caixas de {commit} guardadas em {referencia(lutador).relative_to(RAIZ)}")


if __name__ == "__main__":
    lut = sys.argv[1]
    if "--guardar" in sys.argv:
        guardar(lut, sys.argv[sys.argv.index("--guardar") + 1])
    else:
        n, dif = aplicar(lut)
        print(f"{lut}: caixas da referência em {n} ações" + (f"; quadros diferentes em {dif}" if dif else ""))
