#!/usr/bin/env python3
"""Torneio CPU x CPU na nuvem (Linux, Xvfb + llvmpipe) para o balanceamento (missão 2026-11-14, item 7).

  python3 ferramentas/torneio_cpu.py [--rounds 12] [--ia 8] [--lutadores pengaro,ck,...] [--saida PASTA]

Cada par de lutadores luta numa cópia do motor (a mesma do robô: ~/.cache/nazafight/ikemen), as duas CPUs no nível
--ia, em velocidade acelerada. O script ferramentas/robo/torneio.lua anota cada round (vencedor, vida que sobrou,
duração, acertos, tempo transformado, barra máxima) e reinicia o round sem deixar a luta acabar. No fim imprime a
tabela de vitórias de cada um e a média de vida que sobra para quem venceu.
"""
import argparse
import itertools
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from testar_pengaro import RAIZ, INI_LINUX, ambiente_linux, motor_linux, ajustar_ini  # noqa: E402

LUTADORES = ["pengaro", "ck", "gutto", "hazaki", "raiclaven"]
RE = re.compile(r"ROUND (\d+) v1=(-?\d+)/(\d+) v2=(-?\d+)/(\d+) ticks=(\d+) desp1=(\d+) desp2=(\d+) hit1=(\d+) "
                r"hit2=(\d+) pow1=(\d+) pow2=(\d+)")


def luta(motor, a, b, rounds, ia, tmp):
    copia = tmp / f"{a}_{b}"
    shutil.copytree(motor, copia, symlinks=True)
    for nome in {a, b}:
        shutil.copytree(RAIZ / "chars" / nome, copia / "chars" / nome, dirs_exist_ok=True)
    shutil.copytree(RAIZ / "motif" / "nazafight", copia / "data" / "nazafight", dirs_exist_ok=True)
    INI_LINUX["Motif"] = "data/nazafight/system.def"
    saida = tmp / f"{a}_{b}.txt"
    debug = copia / "external/script/debug.lua"
    debug.write_text(debug.read_text(encoding="utf-8") + "\n" + (RAIZ / "ferramentas/robo/torneio.lua").read_text(
        encoding="utf-8").replace("@SAIDA@", saida.as_posix()).replace("@ROUNDS@", str(rounds)), encoding="utf-8")
    ajustar_ini(copia)
    args = ["-p1", a, "-p1.ai", str(ia), "-p2", b, "-p2.ai", str(ia), "-s", "stages/stage0-720.def", "-rounds", "99"]
    proc = subprocess.Popen(["xvfb-run", "-a", "-s", "-screen 0 1280x720x24", "./Ikemen_GO_Linux"] + args, cwd=copia,
                            env=ambiente_linux(copia), stdout=open(tmp / f"{a}_{b}_log.txt", "w"),
                            stderr=subprocess.STDOUT, start_new_session=True)
    limite = time.time() + 300 * rounds
    while time.time() < limite and proc.poll() is None:
        if saida.exists() and re.search(r"^FIM|ERRO NO TORNEIO", saida.read_text(encoding="utf-8"), re.M):
            break
        time.sleep(3)
    try:
        os.killpg(proc.pid, 9)
    except ProcessLookupError:
        pass
    shutil.rmtree(copia, ignore_errors=True)
    return saida.read_text(encoding="utf-8") if saida.exists() else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rounds", type=int, default=10, help="rounds de cada lado do par")
    ap.add_argument("--ia", type=int, default=8)
    ap.add_argument("--lutadores", default=",".join(LUTADORES))
    ap.add_argument("--saida", type=Path, default=RAIZ / "saida_torneio")
    a = ap.parse_args()
    a.saida.mkdir(parents=True, exist_ok=True)
    nomes = a.lutadores.split(",")
    motor = motor_linux()
    tot = {n: {"v": 0, "d": 0, "e": 0, "sobra": [], "hits": 0, "desp": 0, "rounds": 0} for n in nomes}
    with tempfile.TemporaryDirectory() as td:
        for x, y in itertools.permutations(nomes, 2):  # os dois lados: P1 e P2 não são iguais
            t0 = time.time()
            txt = luta(motor, x, y, a.rounds, a.ia, Path(td))
            (a.saida / f"{x}_x_{y}.txt").write_text(txt, encoding="utf-8")
            vx = vy = 0
            for m in RE.finditer(txt):
                v1, m1, v2, m2 = int(m[2]), int(m[3]), int(m[4]), int(m[5])
                p1, p2 = max(v1, 0) / m1, max(v2, 0) / m2
                for nome, desp, hits in ((x, m[7], m[9]), (y, m[8], m[10])):
                    tot[nome]["desp"] += int(desp)
                    tot[nome]["hits"] += int(hits)
                    tot[nome]["rounds"] += 1
                if p1 > p2:
                    vx += 1
                    tot[x]["v"] += 1; tot[y]["d"] += 1; tot[x]["sobra"].append(p1)
                elif p2 > p1:
                    vy += 1
                    tot[y]["v"] += 1; tot[x]["d"] += 1; tot[y]["sobra"].append(p2)
                else:
                    tot[x]["e"] += 1; tot[y]["e"] += 1
            print(f"{x:>10} {vx:2d} x {vy:2d} {y:<10} ({time.time() - t0:.0f} s)", flush=True)
    print(f"\n{'lutador':10} {'V':>3} {'D':>3} {'E':>3} {'%vit':>5} {'sobra':>6} {'acertos/r':>9} {'transf/r':>8}")
    for n in sorted(nomes, key=lambda k: -tot[k]["v"]):
        t = tot[n]
        j = t["v"] + t["d"] + t["e"]
        sobra = sum(t["sobra"]) / len(t["sobra"]) if t["sobra"] else 0
        r = max(t["rounds"], 1)
        print(f"{n:10} {t['v']:3d} {t['d']:3d} {t['e']:3d} {100 * t['v'] / max(j, 1):5.0f} {100 * sobra:5.0f}% "
              f"{t['hits'] / r:9.1f} {t['desp'] / r / 60:7.1f}s")


if __name__ == "__main__":
    main()
