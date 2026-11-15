#!/usr/bin/env python3
"""Caixas de golpe da dupla do Raiclaven despertado (issue #43): a Clsn1 vai para a arma que chega na frente.

  python3 ferramentas/caixas_dupla.py [--conferir]      reescreve chars/raiclaven/raiclaven.air

No despertado a parceira vai no arnês, nas costas dele, e bate com a navalha e o secador; ele bate com a tesoura de
aço e as botas. As caixas das ações 1xxxx vinham da forma base (punho e pé do cientista sozinho) e ficavam no ar.
Aqui cada Clsn1 de quadro das ações >= 10000 é refeita em cima do desenho endiabrado que o RemapPreset põe no
lugar: pega a ponta mais à frente do desenho (navalha, secador, tesoura ou bota), e a caixa cobre essa ponta,
`FUNDO` px para trás e só a altura do que está nessa faixa. Quando a faixa junta pedaços muito separados na
vertical (a navalha lá em cima e a tesoura embaixo, por exemplo), fica o pedaço mais perto da caixa antiga, que
diz a altura do golpe (alto, meio ou baixo).

Pós-passo como o parry.py e o legibilidade.py, idempotente; o gerar_raiclaven.py chama `aplicar` antes do
legibilidade (que só apara o que passar de 12 px do membro).
"""
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conferir_sff  # noqa: E402
import legibilidade  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FUNDO = 18     # px (1x, tela) da caixa para trás da ponta
SOBRA = 2      # px (1x) além da ponta e acima/abaixo
VAO = 5        # px (1x): pedaços separados por mais que isso na vertical são pedaços diferentes
ALTURA_MAX = 45  # px (1x): faixa mais alta que isso é cortada no pedaço da altura do golpe
RE_ELEM = re.compile(r"^\s*(\d+)\s*,\s*(\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)(.*)$")


class Pontos:
    def __init__(self, nos):
        self.n = {(n["g"], n["i"]): n for n in nos if not n.get("png")}
        self.cache = {}

    def de(self, cod, x0, y0, flip):
        n = self.n.get(cod)
        if n is None:
            return None
        if cod not in self.cache:
            ys, xs = np.nonzero(np.frombuffer(n["px"], np.uint8).reshape(n["h"], n["w"]) > 0)
            self.cache[cod] = (xs - n["x"], ys - n["y"])
        xs, ys = self.cache[cod]
        if "H" in flip:
            xs = -xs
        return xs + x0, ys + y0


def caixa(pts, velha, e):
    xs, ys = pts
    frente = int(xs.max())
    tira = xs >= frente - FUNDO * e
    yy = np.unique(ys[tira])
    # pedaços na vertical
    cortes = np.nonzero(np.diff(yy) > VAO * e)[0]
    pedacos = np.split(yy, cortes + 1)
    if yy.max() - yy.min() > ALTURA_MAX * e or len(pedacos) > 1:
        meio = (velha[1] + velha[3]) / 2
        pedacos.sort(key=lambda p: 0 if p.min() <= meio <= p.max() else min(abs(p.min() - meio), abs(p.max() - meio)))
        p = pedacos[0]
        if p.max() - p.min() > ALTURA_MAX * e:
            lo = int(max(p.min(), meio - ALTURA_MAX * e / 2))
            p = p[(p >= lo) & (p <= lo + ALTURA_MAX * e)]
        sel = tira & (ys >= p.min()) & (ys <= p.max())
        frente = int(xs[sel].max())
        y1, y2 = int(p.min()), int(p.max())
    else:
        y1, y2 = int(yy.min()), int(yy.max())
    return frente - FUNDO * e, y1 - SOBRA * e, frente + SOBRA * e, y2 + SOBRA * e


def refazer(air, pontos, pares, e, log):
    saida = []
    for bloco in re.split(r"(?m)^(?=\[Begin Action )", air):
        m = re.match(r"\[Begin Action (\d+)\]", bloco)
        if not m or int(m.group(1)) < 10000 or not re.search(r"(?mi)^\s*clsn1\s*:", bloco):
            saida.append(bloco)
            continue
        acao = int(m.group(1))
        linhas = bloco.split("\n")
        pend = []
        for k, ln in enumerate(linhas):
            s = ln.split(";")[0].strip()
            if re.match(r"clsn1\s*\[", s, re.I):
                pend.append(k)
                continue
            if re.match(r"clsn", s, re.I):
                continue
            el = RE_ELEM.match(s)
            if el and pend:
                g, i, x, y = (int(v) for v in el.groups()[:4])
                flip = el.group(6).split(",")[1].strip().upper() if el.group(6).count(",") >= 1 else ""
                cod = pares.get((g, i), (g, i))
                pts = pontos.de(cod, x, y, flip)
                if pts is not None and len(pts[0]):
                    # só a primeira caixa do quadro vira a da arma; outras (se houver) saem
                    mm = re.match(r"(\s*Clsn1\[\s*\d+\s*\]\s*=\s*)(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)(.*)$",
                                  linhas[pend[0]], re.I)
                    velha = tuple(int(v) for v in mm.groups()[1:5])
                    nova = caixa(pts, velha, e)
                    linhas[pend[0]] = f"{mm.group(1)}{nova[0]}, {nova[1]}, {nova[2]}, {nova[3]}"
                    for k2 in pend[1:]:
                        linhas[k2] = None
                    if len(pend) > 1:
                        cab = max(j for j in range(pend[0]) if linhas[j] and re.match(r"\s*clsn1\s*:", linhas[j], re.I))
                        linhas[cab] = "Clsn1: 1"
                    if nova != velha:
                        log.append(f"ação {acao}: {velha} -> {nova}")
                pend = []
        saida.append("\n".join(x for x in linhas if x is not None))
    return "".join(saida)


def aplicar(lutador="raiclaven", pasta=None, gravar=True):
    pasta = Path(pasta) if pasta else RAIZ / "chars" / lutador
    pa, pc = pasta / f"{lutador}.air", pasta / f"{lutador}.cns"
    air, cns = pa.read_text(encoding="utf-8"), pc.read_text(encoding="utf-8")
    e = 3 if re.search(r"^\s*xscale\s*=\s*0\.33", cns, re.M) else 1
    _, nos, _ = conferir_sff.ler(pasta / f"{lutador}.sff")
    log = []
    air2 = refazer(air, Pontos(nos), legibilidade.remap(cns), e, log)
    if gravar and air2 != air:
        pa.write_text(air2, encoding="utf-8", newline="\n")
    print(f"{lutador}: {len(log)} caixas da dupla refeitas")
    return log


if __name__ == "__main__":
    for linha in aplicar(gravar="--conferir" not in sys.argv):
        print(" ", linha)
