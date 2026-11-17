#!/usr/bin/env python3
"""Refaz os pós-passos do Raiclaven em chars/raiclaven, na ordem, sem o HD do Blender (que fica fora do git).

  python3 ferramentas/raiclaven_no_jogo.py

1. kit do despertado com A Cliente (kit_raiclaven: golpes 20xxx+, desenhos do corpo firme no .sff, parado pelo remap);
2. legibilidade, Cadeira Elétrica/Secador (despertados_47) e a trava do .cmd;
3. aura presa ao corpo, aura de silhueta e luz (quem regrava o .sff ou o .air roda de novo);
4. por último, o Raiclaven base no boneco de peças (ligar_pecas.py com TODOS os golpes de
   sprites/raiclaven/quadros_pecas_hd, em ordem alfabética, como pede o ligar_pecas): o despertado herda dele o remap.
Depois rode o robô: python3 ferramentas/testar_pengaro.py --linux --lutador raiclaven
"""
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
RAIZ = AQUI.parent
P = RAIZ / "chars" / "raiclaven"


def main():
    import aura_no_corpo
    import aura_silhueta
    import despertados_47
    import kit_raiclaven as k
    import legibilidade
    import luz
    k.aplicar(P, com_cmd=False)
    legibilidade.aplicar("raiclaven", P)
    despertados_47.aplicar("raiclaven", P)
    k.aplicar(P, so_cmd=True)
    aura_no_corpo.aplicar("raiclaven", P)
    aura_silhueta.aplicar("raiclaven", P)
    luz.aplicar("raiclaven", P)
    base = RAIZ / "sprites/raiclaven/quadros_pecas_hd"
    golpes = sorted(d.name for d in base.iterdir() if (d / "tempos.json").exists()) if base.exists() else []
    if golpes:
        subprocess.run([sys.executable, str(AQUI / "ligar_pecas.py"), "raiclaven", *golpes], check=True)


if __name__ == "__main__":
    main()
