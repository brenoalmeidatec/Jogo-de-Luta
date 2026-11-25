#!/usr/bin/env python3
"""Faísca do tamanho do golpe nos normais (recado do Breno, #32, 25/11: "gutto todo ataque dele tem uma esplosão
vermelha, coloque esses efeitos nos impactos ou nos poderes especiais"; regra em docs/regra-efeitos-proporcionais.md).

  python3 ferramentas/faisca_proporcional.py               aplica nos lutadores do kit do Pengaró
  python3 ferramentas/faisca_proporcional.py gutto         só nesse
  python3 ferramentas/faisca_proporcional.py --conferir    sai com erro se algum normal sem queda ainda explode

Antes: 9201 (o "forte" do pixelfx: estouro com lascas, que no Gutto é vermelho) saía em quase todo golpe médio, nos
fortes que não derrubam e até em 5 fracos. Agora, na forma base:
  - golpe fraco (animtype Light) que não derruba: 9200, o ventinho;
  - golpe médio ou forte que não derruba: 9206, o estalo (o risco de luz do 9200 em tamanho maior; sem o clarão
    rosado nem o estouro do 9201, que a revisão de 25/11 achou parecendo nuvem em cima do corpo);
  - golpe que derruba ou joga longe, especial e super: ficam como estavam (o estouro é deles).
A forma despertada não muda (regra do Breno de 13/11: os efeitos do endiabrado ficam como eram).

Mexe só nos normais e nas correntes (200 a 999 e 3410 a 3499). Roda quantas vezes quiser. Chamado no fim dos
gerar_<lutador>.py, depois do efeitos.py.
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LUTADORES = ("pengaro", "ck", "gutto", "raiclaven", "gbzin")
MARCA = "faisca proporcional"
ESTALO = 9206
ESCALA, TICKS = 0.95, 2


def _normal(n):
    return 200 <= n <= 999 or 3410 <= n <= 3499


def air_estalo(air):
    """Ação 9206: os quadros da 9200 (risco de luz) maiores que no fraco."""
    air = re.sub(rf"(?ms)^; {MARCA}\n\[Begin Action {ESTALO}\]\n.*?(?=^\[Begin Action|^; |\Z)", "", air)
    m = re.search(r"(?ms)^\[Begin Action 9200\]\n(.*?)(?=^\[Begin Action|\Z)", air)
    if not m:
        return air, False
    quadros = re.findall(r"(?m)^\s*(\d+)\s*,\s*(\d+)\s*,", m.group(1))[:4]
    if not quadros:
        return air, False
    linhas = "".join(f"{g},{i}, 0,0, {TICKS}, , , {ESCALA:g}, {ESCALA:g}\n" for g, i in quadros)
    return air.rstrip("\n") + f"\n\n; {MARCA}\n[Begin Action {ESTALO}]\n{linhas}\n", True


def cns_faiscas(cns):
    trocas = 0
    marcas = [(m.start(), int(m.group(1))) for m in re.finditer(r"(?m)^\[Statedef (-?\d+)\]", cns)]
    pedacos, fim = [], len(cns)
    for k in range(len(marcas) - 1, -1, -1):
        ini, n = marcas[k]
        bloco = cns[ini:fim]
        if _normal(n):
            partes = re.split(r"(?m)^(?=\[State )", bloco)
            for j, p in enumerate(partes):
                if not re.search(r"(?m)^type\s*=\s*HitDef\s*$", p) or re.search(r"(?m)^fall\s*=\s*1", p):
                    continue
                fraco = re.search(r"(?m)^animtype\s*=\s*Light", p, re.I)
                novo = ESTALO if not fraco else 9200
                q = re.sub(r"(?m)^(sparkno = S\(ifelse\(var\(20\) > 0, \d+, )(9201|9206)(\)\))", rf"\g<1>{novo}\g<3>", p)
                q = re.sub(r"(?m)^sparkno = S(9201|9206)$", f"sparkno = S{novo}", q)
                if q != p:
                    trocas += 1
                    partes[j] = q
            bloco = "".join(partes)
        pedacos.append(bloco)
        fim = ini
    return cns[:fim] + "".join(reversed(pedacos)), trocas


def aplicar(lutador, pasta=None):
    pasta = Path(pasta) if pasta else RAIZ / "chars" / lutador
    pa, pn = pasta / f"{lutador}.air", pasta / f"{lutador}.cns"
    air, ok = air_estalo(pa.read_text(encoding="utf-8").replace("\r\n", "\n"))
    if not ok:
        print(f"{lutador}: sem ação 9200 no .air, nada a fazer")
        return 0
    cns, trocas = cns_faiscas(pn.read_text(encoding="utf-8").replace("\r\n", "\n"))
    pa.write_text(air, encoding="utf-8", newline="\r\n" if b"\r\n" in pa.read_bytes() else "\n")
    pn.write_text(cns, encoding="utf-8", newline="\r\n" if b"\r\n" in pn.read_bytes() else "\n")
    return trocas


def conferir(lutador):
    cns = (RAIZ / "chars" / lutador / f"{lutador}.cns").read_text(encoding="utf-8")
    ruins = []
    for m in re.finditer(r"(?ms)^\[Statedef (-?\d+)\](.*?)(?=^\[Statedef |\Z)", cns):
        if not _normal(int(m.group(1))):
            continue
        for p in re.split(r"(?m)^(?=\[State )", m.group(2)):
            if re.search(r"(?m)^type\s*=\s*HitDef\s*$", p) and not re.search(r"(?m)^fall\s*=\s*1", p) and \
                    re.search(r"(?m)^sparkno = S(?:\(ifelse\(var\(20\) > 0, \d+, )?9201\b", p):
                ruins.append(m.group(1))
    return ruins


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    erro = False
    for l in args or LUTADORES:
        if "--conferir" in sys.argv:
            r = conferir(l)
            print(f"{l}: {'ok' if not r else 'estouro em normal sem queda: ' + ', '.join(sorted(set(r)))}")
            erro |= bool(r)
        else:
            print(f"{l}: {aplicar(l)} faíscas trocadas")
    sys.exit(1 if erro else 0)


if __name__ == "__main__":
    main()
