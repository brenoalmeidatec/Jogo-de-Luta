#!/usr/bin/env python3
"""Gráfico da vantagem na defesa, antes x depois (para o comentário do Breno).

  python3 ferramentas/vantagem_grafico.py ANTES.json DEPOIS.json SAIDA.png

Cada ponto é um golpe que o robô conseguiu medir defendido (ferramentas/vantagem.py). Cinza é antes, azul é depois;
o traço grosso é a mediana. A faixa clara é onde ficam os golpes que não derrubam nos jogos grandes (-6 a +2).
"""
import json
import statistics
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

NOMES = {"pengaro": "Pengaró", "hazaki": "Hazak", "ck": "CK", "gutto": "Gutto", "raiclaven": "Raiclaven", "gbzin": "Gbzin"}
CINZA, AZUL, TEXTO, TEXTO2, GRADE = "#9c9c9c", "#257de0", "#191919", "#666666", "#e6e6e6"


def valores(d, l):
    out = []
    for r in d.get(l, {}).values():
        x = r.get("def", {})
        if "vantagem" in x and x.get("res") == "def":
            out.append(int(x["vantagem"]))
    return out


def main():
    antes, depois = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:3])
    lut = [l for l in NOMES if l in antes]
    fig, ax = plt.subplots(figsize=(11, 6.8), dpi=110)
    fig.patch.set_facecolor("white")
    ax.axvspan(-6, 2, color="#eef4fc", zorder=0)
    ax.axvline(0, color="#bdbdbd", lw=1, zorder=1)
    for k, l in enumerate(lut):
        y = len(lut) - 1 - k
        for dy, d, cor in ((0.18, antes, CINZA), (-0.18, depois, AZUL)):
            v = valores(d, l)
            if not v:
                continue
            ax.scatter(v, [y + dy] * len(v), s=22, color=cor, alpha=0.75, edgecolors="white", linewidths=0.6, zorder=3)
            m = statistics.median(v)
            ax.plot([m, m], [y + dy - 0.13, y + dy + 0.13], color=cor, lw=4, solid_capstyle="round", zorder=4)
            ax.text(m, y + dy + 0.16, f"{m:+.0f}", ha="center", va="bottom", fontsize=9, color=TEXTO)
    ax.set_yticks(range(len(lut)))
    ax.set_yticklabels([NOMES[l] for l in reversed(lut)], fontsize=12, color=TEXTO)
    ax.set_xlabel("quanto quem bateu fica preso depois que o golpe é DEFENDIDO (1 tique = 1/60 s)\n"
                  "à esquerda do 0: quem defendeu age primeiro e pode revidar; quanto mais à esquerda, mais fácil revidar",
                  fontsize=10, color=TEXTO2)
    ax.set_xlim(-60, 15)
    ax.grid(axis="x", color=GRADE, lw=0.8, zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#bdbdbd")
    ax.tick_params(colors=TEXTO2, length=0)
    ax.scatter([], [], s=40, color=CINZA, label="antes: quem defendia revidava qualquer golpe")
    ax.scatter([], [], s=40, color=AZUL, label="depois: tempo da defesa acertado golpe a golpe")
    ax.plot([], [], color=TEXTO2, lw=4, label="traço grosso: o golpe do meio (metade fica de cada lado)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.17), ncol=2, frameon=False, fontsize=10, labelcolor=TEXTO)
    ax.text(-2, -0.75, "faixa dos jogos grandes\n(golpe que não derruba)", ha="center", va="bottom", fontsize=9,
            color=TEXTO2)
    ax.set_ylim(-0.8, len(lut) - 0.45)
    ax.set_title("Defender: cada ponto é um golpe, medido dentro do jogo", fontsize=14,
                 color=TEXTO, loc="left", pad=12)
    fig.tight_layout()
    fig.savefig(sys.argv[3], facecolor="white")


if __name__ == "__main__":
    main()
