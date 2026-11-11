"""Mede o chicote: fase do 1º harmônico (em quadros) e curso pico a pico de cada ponto exportado pelo Blender."""
import json, sys, numpy as np
PT = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "render/pontos.json")); P = PT["pontos"]; N = len(P)
t = np.arange(N)
res = {}
for k in ["esq_ombro", "esq_braco", "esq_antebraco", "esq_garra", "esq_d5a", "esq_d5b", "esq_d4a", "esq_d4b", "esq_d4c", "esq_d3a", "esq_d3b", "esq_d3c",
          "esq_d2a", "esq_d2b", "esq_d2c", "esq_d1a", "esq_d1b", "esq_d1c", "coroa"]:
    xy = np.array([p[k][:2] for p in P]); y = xy[:, 1] - xy[:, 1].mean()
    c = (y * np.exp(-2j * np.pi * t / N)).sum()
    fase = (-np.angle(c) / (2 * np.pi) * N) % N
    passo = max(float(np.hypot(*(xy[(i + 1) % N] - xy[i]))) for i in range(N))
    res[k] = dict(fase_q=round(float(fase), 1), curso_x=round(float(np.ptp(xy[:, 0])), 1), curso_y=round(float(np.ptp(xy[:, 1])), 1), passo_max=round(passo, 2))
    print(f"{k:14s} fase {fase:5.1f} q   curso x {np.ptp(xy[:,0]):5.1f}  y {np.ptp(xy[:,1]):5.1f}   passo max {passo:4.2f}")
xs = [p[k][0] for p in P for k in p if k.startswith("esq_")]; print("x min das pontas esq", round(min(xs), 1))
json.dump(res, open("chicote.json", "w"), indent=1)
