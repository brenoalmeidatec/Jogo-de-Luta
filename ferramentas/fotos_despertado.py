#!/usr/bin/env python3
"""Fotos (e um vídeo curto) de uma luta CPU x CPU com o P1 preso na forma despertada, na nuvem Linux (Xvfb + llvmpipe).

  python3 ferramentas/fotos_despertado.py raiclaven [SAIDA] [--segundos 40] [--video]

Usa o mesmo IKEMEN GO v1.0.0 Linux do robô (ferramentas/testar_pengaro.py, ~/.cache/nazafight/ikemen). No .cmd do P1
entra um VarSet no [Statedef -1] que segura var(20) (o contador do Despertar) em 600: ele fica despertado a luta toda,
com a aura e os golpes da forma. Os dois lutam sozinhos (-p1.ai e -p2.ai). Tira uma foto da tela a cada 2 s com o
`import` do ImageMagick e, com --video, grava um .mp4 com o ffmpeg (x11grab), se ele existir.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import testar_pengaro as tp  # noqa: E402

RAIZ = tp.RAIZ
TELA = 97


def main():
    args = sys.argv[1:]
    video = "--video" in args
    if video:
        args.remove("--video")
    segundos = 40
    if "--segundos" in args:
        i = args.index("--segundos")
        segundos = int(args[i + 1])
        del args[i:i + 2]
    lutador = args[0] if args else "raiclaven"
    saida = Path(args[1]) if len(args) > 1 else RAIZ / "fotos_despertado"
    saida.mkdir(parents=True, exist_ok=True)
    motor = tp.motor_linux()
    tmp = Path(tempfile.mkdtemp(prefix="fotos_desp_"))
    copia = tmp / "motor"
    shutil.copytree(motor, copia, symlinks=True)
    for nome in (lutador, "hazaki"):
        shutil.copytree(RAIZ / "chars" / nome, copia / "chars" / nome, dirs_exist_ok=True)
    if (RAIZ / "motif" / "nazafight" / "system.def").exists():
        shutil.copytree(RAIZ / "motif" / "nazafight", copia / "data" / "nazafight", dirs_exist_ok=True)
        tp.INI_LINUX["Motif"] = "data/nazafight/system.def"
    cmd = copia / "chars" / lutador / f"{lutador}.cmd"
    txt = cmd.read_text(encoding="utf-8").replace("\r\n", "\n")
    preso = ("[State -1, Fotos: preso no Despertar]\ntype = VarSet\ntrigger1 = var(20) < 500 && roundstate = 2\n"
             "var(20) = 600\n\n")
    cmd.write_text(txt.replace("[Statedef -1]\n\n", "[Statedef -1]\n\n" + preso, 1), encoding="utf-8", newline="\n")
    tp.ajustar_ini(copia)
    amb = tp.ambiente_linux(copia)
    xvfb = subprocess.Popen(["Xvfb", f":{TELA}", "-screen", "0", "1280x720x24"], stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    time.sleep(2)
    amb["DISPLAY"] = f":{TELA}"
    jogo = subprocess.Popen(["./Ikemen_GO_Linux", "-p1", lutador, "-p1.ai", "8", "-p2", "hazaki", "-p2.ai", "8",
                             "-s", "stages/stage0-720.def", "-rounds", "1"], cwd=copia, env=amb,
                            stdout=open(tmp / "motor_log.txt", "w"), stderr=subprocess.STDOUT)
    gravador = None
    try:
        time.sleep(8)
        if video and shutil.which("ffmpeg"):
            gravador = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "x11grab", "-framerate", "30",
                                         "-video_size", "1280x720", "-i", f":{TELA}", "-t", str(min(segundos, 20)),
                                         "-pix_fmt", "yuv420p", str(saida / f"{lutador}_despertado.mp4")], env=amb)
        for k in range(segundos // 2):
            subprocess.run(["import", "-display", f":{TELA}", "-window", "root", str(saida / f"{lutador}_{k:02d}.png")],
                           env=amb, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
        if gravador:
            gravador.wait(timeout=60)
    finally:
        jogo.kill()
        xvfb.kill()
    print(f"fotos em {saida}")


if __name__ == "__main__":
    main()
