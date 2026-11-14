#!/usr/bin/env python3
"""Filma uma luta CPU x CPU de verdade na nuvem (Linux, Xvfb + Mesa), para mostrar efeitos, auras e supers.

  python3 ferramentas/filmar_luta_linux.py SAIDA.mp4 [--p1 gutto] [--p2 pengaro] [--segundos 30] [--ia 8]
                                           [--barra] [--fotos PASTA]

Usa a mesma cópia do IKEMEN GO v1.0.0 Linux do robô (~/.cache/nazafight/ikemen), com o HUD Nazafights. As duas CPUs
lutam no nível --ia. Com --barra, a barra de super dos dois fica cheia o tempo todo (um script Lua no motor), para a
CPU soltar especial, super e Despertar no vídeo. --fotos tira um quadro por segundo numa pasta (para olhar sem vídeo).
Precisa de Xvfb e ffmpeg (x11grab). O jogo instalado não é tocado.
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

BARRA = """
-- barra cheia para a CPU usar super e Despertar (só na cópia de filmagem: ferramentas/filmar_luta_linux.py)
hook.add("loop", "barra_cheia", function()
  pcall(function()
    for p = 1, 2 do
      local old = id()
      if player(p) then setPower(powermax()) end
      playerId(old)
    end
  end)
end)
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("saida", type=Path)
    ap.add_argument("--p1", default="gutto")
    ap.add_argument("--p2", default="pengaro")
    ap.add_argument("--segundos", type=int, default=30)
    ap.add_argument("--ia", type=int, default=8)
    ap.add_argument("--espera", type=int, default=12, help="segundos até a luta começar (intro)")
    ap.add_argument("--barra", action="store_true")
    ap.add_argument("--fotos", type=Path)
    ap.add_argument("--cenario", default="stages/stage0-720.def")
    a = ap.parse_args()
    motor = motor_linux()
    with tempfile.TemporaryDirectory() as td:
        copia = Path(td) / "motor"
        shutil.copytree(motor, copia, symlinks=True)
        for nome in {a.p1, a.p2}:
            shutil.copytree(RAIZ / "chars" / nome, copia / "chars" / nome, dirs_exist_ok=True)
        shutil.copytree(RAIZ / "motif" / "nazafight", copia / "data" / "nazafight", dirs_exist_ok=True)
        if (RAIZ / "stages").exists() and a.cenario.startswith("stages/") and (RAIZ / a.cenario).exists():
            shutil.copytree(RAIZ / "stages", copia / "stages", dirs_exist_ok=True)
        INI_LINUX["Motif"] = "data/nazafight/system.def"
        INI_LINUX["VSync"] = "1"
        ajustar_ini(copia)
        if a.barra:
            debug = copia / "external/script/debug.lua"
            debug.write_text(debug.read_text(encoding="utf-8") + BARRA, encoding="utf-8")
        disp = f":{90 + os.getpid() % 9}"
        xvfb = subprocess.Popen(["Xvfb", disp, "-screen", "0", "1280x720x24"], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(2)
        amb = {**ambiente_linux(copia), "DISPLAY": disp}
        args = ["-p1", a.p1, "-p1.ai", str(a.ia), "-p2", a.p2, "-p2.ai", str(a.ia), "-s", a.cenario, "-rounds", "3"]
        jogo = subprocess.Popen(["./Ikemen_GO_Linux"] + args, cwd=copia, env=amb, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            time.sleep(a.espera)
            a.saida.parent.mkdir(parents=True, exist_ok=True)
            cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "x11grab", "-framerate", "30", "-video_size", "1280x720",
                   "-i", disp, "-t", str(a.segundos), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                   str(a.saida)]
            subprocess.run(cmd, env=amb, check=True)
            if a.fotos:
                a.fotos.mkdir(parents=True, exist_ok=True)
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(a.saida), "-vf", "fps=2",
                                str(a.fotos / "f_%03d.png")], check=True)
        finally:
            try:
                os.killpg(jogo.pid, 9)
            except ProcessLookupError:
                pass
            xvfb.kill()
    print(a.saida)


if __name__ == "__main__":
    main()
