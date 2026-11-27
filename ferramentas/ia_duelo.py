#!/usr/bin/env python3
"""Duelo na nuvem: o lutador COM a IA nova contra ele mesmo SEM IA (a CPU do motor, que só aperta botão ao acaso).

  python3 ferramentas/ia_duelo.py [--rounds 6] [--ia 8] [--lutadores pengaro,ck] [--ref origin/mugen]

Espelho (mesmo lutador dos dois lados), para medir só a IA. O "sem IA" é o .cns tirado do commit --ref com o bloco
da ia_cpu.py removido. Roda os dois lados (IA nova de P1 e de P2) e imprime quantos rounds a IA nova ganhou, a vida
média que sobrou e quantos golpes cada lado acertou (torneio.lua). Saída em saida_ia_duelo/.
"""
import argparse
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
from torneio_cpu import RE  # noqa: E402
import ia_cpu  # noqa: E402


def preparar_velho(copia, nome, ref):
    destino = copia / "chars" / f"{nome}_velho"
    shutil.copytree(RAIZ / "chars" / nome, destino, dirs_exist_ok=True)
    for ext in ("cns", "cmd"):
        txt = subprocess.run(["git", "show", f"{ref}:chars/{nome}/{nome}.{ext}"], cwd=RAIZ, capture_output=True,
                             check=True).stdout.decode("utf-8")
        if ext == "cns":
            txt = ia_cpu.tirar(txt.replace("\r\n", "\n"))
        (destino / f"{nome}.{ext}").write_bytes(txt.encode("utf-8"))
    return f"{nome}_velho/{nome}.def"


def luta(motor, nome, novo_p1, rounds, ia, ref, tmp):
    copia = tmp / f"{nome}_{int(novo_p1)}"
    shutil.copytree(motor, copia, symlinks=True)
    shutil.copytree(RAIZ / "chars" / nome, copia / "chars" / nome, dirs_exist_ok=True)
    velho = preparar_velho(copia, nome, ref)
    shutil.copytree(RAIZ / "motif" / "nazafight", copia / "data" / "nazafight", dirs_exist_ok=True)
    INI_LINUX["Motif"] = "data/nazafight/system.def"
    saida = tmp / f"{nome}_{int(novo_p1)}.txt"
    debug = copia / "external/script/debug.lua"
    debug.write_text(debug.read_text(encoding="utf-8") + "\n" + (RAIZ / "ferramentas/robo/torneio.lua").read_text(
        encoding="utf-8").replace("@SAIDA@", saida.as_posix()).replace("@ROUNDS@", str(rounds)), encoding="utf-8")
    ajustar_ini(copia)
    p1, p2 = (nome, velho) if novo_p1 else (velho, nome)
    args = ["-p1", p1, "-p1.ai", str(ia), "-p2", p2, "-p2.ai", str(ia), "-s", "stages/stage0-720.def", "-rounds", "99"]
    log = open(tmp / f"{nome}_{int(novo_p1)}_log.txt", "w")
    proc = subprocess.Popen(["xvfb-run", "-a", "-s", "-screen 0 1280x720x24", "./Ikemen_GO_Linux"] + args, cwd=copia,
                            env=ambiente_linux(copia), stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
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
    ap.add_argument("--rounds", type=int, default=6)
    ap.add_argument("--ia", type=int, default=8)
    ap.add_argument("--lutadores", default=",".join(ia_cpu.LUTADORES))
    ap.add_argument("--ref", default="origin/mugen")
    ap.add_argument("--saida", type=Path, default=RAIZ / "saida_ia_duelo")
    a = ap.parse_args()
    a.saida.mkdir(parents=True, exist_ok=True)
    motor = motor_linux()
    linhas = []
    with tempfile.TemporaryDirectory() as td:
        for nome in a.lutadores.split(","):
            v = n = 0
            sobra, hits_novo, hits_velho, desp = [], 0, 0, 0
            for novo_p1 in (True, False):
                txt = luta(motor, nome, novo_p1, a.rounds, a.ia, a.ref, Path(td))
                (a.saida / f"{nome}_{'p1' if novo_p1 else 'p2'}.txt").write_text(txt, encoding="utf-8")
                for m in RE.finditer(txt):
                    v1, m1, v2, m2 = int(m[2]), int(m[3]), int(m[4]), int(m[5])
                    vn, vv = (v1 / m1, v2 / m2) if novo_p1 else (v2 / m2, v1 / m1)
                    hn, hv = (int(m[9]), int(m[10])) if novo_p1 else (int(m[10]), int(m[9]))
                    desp += int(m[7] if novo_p1 else m[8]) > 0
                    hits_novo += hn
                    hits_velho += hv
                    n += 1
                    if vn > vv:
                        v += 1
                        sobra.append(max(vn, 0))
            media = sum(sobra) / len(sobra) if sobra else 0
            linha = (f"{nome}: IA nova venceu {v} de {n} rounds; vida que sobra quando vence {media:.0%}; "
                     f"golpes acertados nova {hits_novo} x antiga {hits_velho}; rounds com Despertar {desp}")
            print(linha, flush=True)
            linhas.append(linha)
    (a.saida / "resumo.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
