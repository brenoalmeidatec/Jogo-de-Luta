#!/usr/bin/env python3
"""Liga a destruição do cenário ao Despertar dos lutadores (issue #35, item 4.2 da missão dos cenários).

  python3 ferramentas/destruicao.py [lutador ...]      # sem nome: todos de chars/

O cenário (ferramentas/gerar_cenario.py, campo "nivel" da camada) tem grupos de camadas com um BGCtrl Visible cada, de
sctrlid 909 a 913. Este pós-passo põe no [Statedef -2] do lutador um ModifyBGCtrl por grupo, a cada tique, com o nível
  nível = (eu estou endiabrado) + (o oponente está endiabrado)        var(20) > 0 nos dois
   909 só no lugar inteiro (nível 0)      910 enquanto não é o nível 2      911 do nível 1 em diante
   912 só no nível 2                      913 só no nível 1
O var(20) liga no clarão da cena da transformação (issue #49) e, com a forma permanente (forma_permanente.py), não
desliga mais nem entre os rounds: a destruição sobe no clarão e fica até o fim da luta. Cenário sem esses grupos
(os de exemplo do motor) ignora o controlador. O motor marca o cenário para recarregar, então a luta seguinte começa
com o lugar inteiro.
Roda de novo à vontade (troca o bloco antigo). Os gerar_<lutador>.py chamam `aplicar` por último.
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
INICIO = "; --- destruição do cenário (ferramentas/destruicao.py) ---\n"
FIM = "; --- fim da destruição do cenário ---\n\n"
NIVEL = "((var(20) > 0) + (NumEnemy > 0 && enemy, var(20) > 0))"
GRUPOS = [(909, "= 0"), (910, "< 2"), (911, ">= 1"), (912, "= 2"), (913, "= 1")]


def bloco():
    L = [INICIO]
    for gid, quando in GRUPOS:
        L.append(f"[State -2, Destruição do cenário {gid}]\ntype = ModifyBGCtrl\ntrigger1 = !IsHelper\n"
                 f"id = {gid}\nvalue = ({NIVEL} {quando})\nignorehitpause = 1\n\n")
    L.append(FIM)
    return "".join(L)


def aplicar(lutador, pasta=None):
    pasta = Path(pasta or RAIZ / "chars" / lutador)
    arq = pasta / f"{lutador}.cns"
    txt = arq.read_text(encoding="utf-8")
    if "[Statedef 2000]" not in txt:
        print(f"{lutador}: sem Despertar (estado 2000), destruição não ligada")
        return
    limpo = re.sub(re.escape(INICIO) + r".*?" + re.escape(FIM), "", txt, flags=re.S)
    m = re.search(r"(?m)^\[Statedef -2\][^\n]*\n(?:[^\n\[][^\n]*\n)*\n?", limpo)
    if not m:
        raise SystemExit(f"{lutador}: sem [Statedef -2] para ligar a destruição do cenário")
    novo = limpo[:m.end()] + bloco() + limpo[m.end():]
    if novo != txt:
        arq.write_text(novo, encoding="utf-8", newline="\n")
    print(f"{lutador}: destruição do cenário ligada ao Despertar")


if __name__ == "__main__":
    nomes = sys.argv[1:] or sorted(p.name for p in (RAIZ / "chars").iterdir() if (p / f"{p.name}.cns").exists())
    for nome in nomes:
        aplicar(nome)
