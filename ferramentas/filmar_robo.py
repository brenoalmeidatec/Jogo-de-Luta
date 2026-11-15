#!/usr/bin/env python3
"""Filma o robô de teste na nuvem (Linux, Xvfb), em velocidade normal, só com os roteiros escolhidos.

  python3 ferramentas/filmar_robo.py --lutador hazaki --filtro "projetil" --saida SAIDA/ [--nome golpes.mp4]

Usa o mesmo robô do testar_pengaro.py (ferramentas/robo/robo.lua), com o motor sem aceleração (setAccel 1) e VSync,
e grava a tela virtual com o ffmpeg (x11grab, 30 quadros/s) do começo ao FIM do robô. O resultado do robô (PASS/FAIL)
fica em SAIDA/resultado.txt. --filtro pega os roteiros cujo nome contém o texto (vazio = todos). Pode repetir
--filtro: cada um vira um vídeo à parte (nome-1.mp4, nome-2.mp4...).
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
import testar_pengaro as tp  # noqa: E402


def filmar(lutador, filtro, destino, nome, segundos_max=900):
    motor = tp.motor_linux()
    tmp = Path(tempfile.mkdtemp(prefix="filmar_"))
    try:
        copia = tmp / "motor"
        shutil.copytree(motor, copia, symlinks=True)
        for n in (lutador, "hazaki"):
            shutil.copytree(tp.RAIZ / "chars" / n, copia / "chars" / n, dirs_exist_ok=True)
        if (tp.RAIZ / "motif" / "nazafight" / "system.def").exists():
            shutil.copytree(tp.RAIZ / "motif" / "nazafight", copia / "data" / "nazafight", dirs_exist_ok=True)
            tp.INI_LINUX["Motif"] = "data/nazafight/system.def"
        saida = tmp / "resultado.txt"
        tp.preparar(copia, motor, lutador, saida.as_posix(), filtro=filtro, acelera=1)
        tp.INI_LINUX["VSync"] = "1"
        tp.ajustar_ini(copia)
        disp = ":%d" % (90 + os.getpid() % 100)
        xvfb = subprocess.Popen(["Xvfb", disp, "-screen", "0", "1280x720x24"], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(1.5)
        amb = {**tp.ambiente_linux(copia), "DISPLAY": disp}
        jogo = subprocess.Popen(["./Ikemen_GO_Linux"] + tp.argumentos(lutador), cwd=copia, env=amb,
                                stdout=open(tmp / "motor_log.txt", "w"), stderr=subprocess.STDOUT)
        destino.mkdir(parents=True, exist_ok=True)
        video = destino / nome
        grava = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "x11grab", "-video_size", "1280x720",
                                  "-framerate", "30", "-i", disp, "-t", str(segundos_max), "-c:v", "libx264",
                                  "-preset", "veryfast", "-crf", "26", "-pix_fmt", "yuv420p", str(video)],
                                 stdin=subprocess.PIPE, env=amb)
        limite = time.time() + segundos_max
        while time.time() < limite and jogo.poll() is None:
            if saida.exists() and re.search(r"^FIM|ERRO NO ROBO", saida.read_text(encoding="utf-8"), re.M):
                time.sleep(1.5)
                break
            time.sleep(1)
        grava.communicate(b"q")
        jogo.kill()
        xvfb.kill()
        texto = saida.read_text(encoding="utf-8") if saida.exists() else "(sem resultado)\n" + \
            (tmp / "motor_log.txt").read_text(errors="replace")[-2000:]
        (destino / (Path(nome).stem + "_resultado.txt")).write_text(texto, encoding="utf-8")
        return video, texto
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lutador", default="hazaki")
    ap.add_argument("--filtro", action="append", default=None)
    ap.add_argument("--saida", type=Path, default=tp.RAIZ / "saida_filme")
    ap.add_argument("--nome", default="robo.mp4")
    a = ap.parse_args()
    filtros = a.filtro or [""]
    for k, f in enumerate(filtros):
        nome = a.nome if len(filtros) == 1 else f"{Path(a.nome).stem}-{k + 1}.mp4"
        video, texto = filmar(a.lutador, f, a.saida, nome)
        print(f"{video}: {texto.count('  PASS ')} PASS, {texto.count('  FAIL ')} FAIL")


if __name__ == "__main__":
    main()
