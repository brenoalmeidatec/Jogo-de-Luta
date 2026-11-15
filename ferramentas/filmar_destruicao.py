#!/usr/bin/env python3
"""Filma um cenário nos três estados (inteiro, destruição 1, destruição 2) no jogo de verdade, na nuvem (Xvfb).

  python3 ferramentas/filmar_destruicao.py PASTA --cenario praca [--p1 pengaro] [--p2 gutto] [--stages stages]
                                           [--primeiro 240] [--segundo 780] [--segundos 30]

O P1 desperta sozinho aos --primeiro tiques de luta e o P2 aos --segundo (os dois parados, barra cheia, sem IA), como o
filmar_transformacao.py faz. Sai PASTA/<cenario>.mp4 e três fotos: <cenario>_0.png (inteiro), _1.png e _2.png.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from testar_pengaro import RAIZ, INI_LINUX, ambiente_linux, motor_linux, ajustar_ini  # noqa: E402
from filmar_transformacao import forcar_despertar  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("saida", type=Path)
    ap.add_argument("--cenario", required=True)
    ap.add_argument("--p1", default="pengaro")
    ap.add_argument("--p2", default="gutto")
    ap.add_argument("--stages", type=Path, default=RAIZ / "stages")
    ap.add_argument("--primeiro", type=int, default=240)
    ap.add_argument("--segundo", type=int, default=780)
    ap.add_argument("--segundos", type=float, default=30)
    ap.add_argument("--espera", type=float, default=9)
    ap.add_argument("--tela", default="640x360")
    a = ap.parse_args()
    if a.p1 == a.p2:
        raise SystemExit("use dois lutadores diferentes (cada um desperta numa hora)")
    a.saida.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        copia = Path(td) / "motor"
        shutil.copytree(motor_linux(), copia, symlinks=True)
        for nome in (a.p1, a.p2):
            shutil.copytree(RAIZ / "chars" / nome, copia / "chars" / nome, dirs_exist_ok=True)
        shutil.copytree(RAIZ / "motif" / "nazafight", copia / "data" / "nazafight", dirs_exist_ok=True)
        shutil.copytree(a.stages, copia / "stages", dirs_exist_ok=True)
        larg, alt = a.tela.split("x")
        ini = {**INI_LINUX, "Motif": "data/nazafight/system.def", "GameWidth": larg, "GameHeight": alt}
        INI_LINUX.clear()
        INI_LINUX.update(ini)
        ajustar_ini(copia)
        forcar_despertar(copia / "chars" / a.p1 / f"{a.p1}.cns", a.primeiro)
        forcar_despertar(copia / "chars" / a.p2 / f"{a.p2}.cns", a.segundo)
        disp = f":{80 + os.getpid() % 9}"
        xvfb = subprocess.Popen(["Xvfb", disp, "-screen", "0", f"{a.tela}x24"], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(2)
        amb = {**ambiente_linux(copia), "DISPLAY": disp}
        jogo = subprocess.Popen(["./Ikemen_GO_Linux", "-p1", a.p1, "-p2", a.p2, "-s", f"stages/{a.cenario}.def",
                                 "-rounds", "1", "-time", "-1"], cwd=copia, env=amb,
                                stdout=open(a.saida / f"{a.cenario}_log.txt", "w"), stderr=subprocess.STDOUT,
                                start_new_session=True)
        video = a.saida / f"{a.cenario}.mp4"
        try:
            time.sleep(a.espera)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "x11grab", "-draw_mouse", "0", "-framerate",
                            "30", "-video_size", a.tela, "-i", disp, "-t", str(a.segundos), "-vf",
                            "scale=1280:720:flags=neighbor", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                            str(video)], env=amb, check=True)
        finally:
            try:
                os.killpg(jogo.pid, 9)
            except ProcessLookupError:
                pass
            xvfb.kill()
    # o llvmpipe não dá 60 tiques por segundo: as fotos saem a uma fração do filme, não a um tempo fixo
    for n, fr in enumerate((0.04, 0.55, 0.97)):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a.segundos * fr:.2f}", "-i", str(video),
                        "-frames:v", "1", str(a.saida / f"{a.cenario}_{n}.png")], check=True)
    print("pronto:", video)


if __name__ == "__main__":
    main()
