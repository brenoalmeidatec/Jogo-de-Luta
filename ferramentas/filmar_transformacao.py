#!/usr/bin/env python3
"""Filma a cena da transformação (issue #49) na nuvem, com o som do jogo: Linux, Xvfb + Mesa, IKEMEN GO v1.0.0.

  python3 ferramentas/filmar_transformacao.py SAIDA.mp4 [--lutador pengaro] [--oponente gutto] [--segundos 12]
                                              [--quando 150] [--fotos PASTA] [--cenario stages/...def]

O lutador entra no Despertar (estado 2000) uma vez só, --quando tiques depois de a luta começar, parado e com a barra
cheia. Ninguém controla os dois lutadores (sem IA e sem controle), para a cena aparecer inteira. O vídeo sai a 60 fps e com o áudio do
motor (driver "disk" do SDL, que grava o que sairia na caixa de som), para conferir a música entrando.
O jogo instalado não é tocado: tudo roda numa cópia do motor em pasta temporária.
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


def forcar_despertar(cns, quando):
    txt = cns.read_text(encoding="utf-8")
    extra = (f"[State -2, Filmar: barra cheia]\ntype = PowerSet\ntrigger1 = RoundState = 2 && map(filma_desp) = 0\n"
             f"value = PowerMax\n\n"
             f"[State -2, Filmar: conta]\ntype = MapAdd\ntrigger1 = RoundState = 2\nmap = \"filma_t\"\nvalue = 1\n\n"
             f"[State -2, Filmar: desperta uma vez]\ntype = ChangeState\n"
             f"trigger1 = RoundState = 2 && map(filma_desp) = 0 && map(filma_t) >= {quando}\n"
             f"trigger1 = ctrl && statetype = S && var(20) <= 0\nvalue = 2000\n\n"
             f"[State -2, Filmar: marca]\ntype = MapSet\ntrigger1 = stateno = 2000\nmap = \"filma_desp\"\nvalue = 1\n\n")
    txt = re.sub(r"^\[Statedef -2\][^\n]*\n(?:[^\n\[][^\n]*\n)*\n?", lambda m: m.group(0) + extra, txt, count=1,
                 flags=re.M)
    cns.write_text(txt, encoding="utf-8", newline="\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("saida", type=Path)
    ap.add_argument("--lutador", default="pengaro")
    ap.add_argument("--oponente", default="gutto")
    ap.add_argument("--segundos", type=float, default=12)
    ap.add_argument("--espera", type=float, default=9, help="segundos de motor antes de gravar (intro)")
    ap.add_argument("--quando", type=int, default=150, help="tiques de luta antes do Despertar")
    ap.add_argument("--fotos", type=Path, help="pasta para um quadro a cada 5 tiques da gravação")
    ap.add_argument("--tela", default="640x360",
                    help="resolução do motor; menor = mais quadros por segundo no llvmpipe (o vídeo sai ampliado para 1280x720)")
    ap.add_argument("--lento", type=int, default=0,
                    help="roda o motor a N tiques por segundo e grava todo tique (a nuvem não dá 60 fps em tempo real);"
                         " o vídeo sai acelerado de volta para 60 fps")
    ap.add_argument("--cenario", default="stages/stage0-720.def")
    a = ap.parse_args()
    motor = motor_linux()
    with tempfile.TemporaryDirectory() as td:
        copia = Path(td) / "motor"
        shutil.copytree(motor, copia, symlinks=True)
        for nome in {a.lutador, a.oponente}:
            shutil.copytree(RAIZ / "chars" / nome, copia / "chars" / nome, dirs_exist_ok=True)
        shutil.copytree(RAIZ / "motif" / "nazafight", copia / "data" / "nazafight", dirs_exist_ok=True)
        if a.cenario.startswith("stages/") and (RAIZ / a.cenario).exists():
            shutil.copytree(RAIZ / "stages", copia / "stages", dirs_exist_ok=True)
        ini = {**INI_LINUX, "Motif": "data/nazafight/system.def", "VSync": "1", "MasterVolume": "100",
               "PauseMasterVolume": "100"}
        larg, alt = a.tela.split("x")
        ini.update({"GameWidth": larg, "GameHeight": alt})
        if a.lento:
            ini["Framerate"] = str(a.lento)
        INI_LINUX.clear()
        INI_LINUX.update(ini)
        ajustar_ini(copia)
        forcar_despertar(copia / "chars" / a.lutador / f"{a.lutador}.cns", a.quando)
        disp = f":{90 + os.getpid() % 9}"
        xvfb = subprocess.Popen(["Xvfb", disp, "-screen", "0", f"{a.tela}x24"], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(2)
        som = Path(td) / "som.raw"
        amb = {**ambiente_linux(copia), "DISPLAY": disp, "SDL_AUDIODRIVER": "disk", "SDL_DISKAUDIOFILE": str(som)}
        args = ["-p1", a.lutador, "-p2", a.oponente, "-s", a.cenario, "-rounds", "1"]
        t0 = time.time()
        jogo = subprocess.Popen(["./Ikemen_GO_Linux"] + args, cwd=copia, env=amb, stdout=open(Path(td) / "log.txt", "w"),
                                stderr=subprocess.STDOUT, start_new_session=True)
        video = Path(td) / "video.mp4"
        try:
            time.sleep(a.espera)
            t_video = time.time() - t0
            fps = a.lento or 60
            real = a.segundos * 60 / fps
            cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "x11grab", "-draw_mouse", "0", "-framerate", str(fps), "-video_size", a.tela,
                   "-i", disp, "-t", str(real), "-vf", "scale=1280:720:flags=neighbor", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(video)]
            subprocess.run(cmd, env=amb, check=True)
        finally:
            try:
                os.killpg(jogo.pid, 9)
            except ProcessLookupError:
                pass
            xvfb.kill()
        a.saida.parent.mkdir(parents=True, exist_ok=True)
        if a.lento:
            rapido = Path(td) / "rapido.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-vf", f"setpts={a.lento}/60*PTS",
                            "-r", "60", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(rapido)], check=True)
            video = rapido
        if os.environ.get("NAZA_CRU"):
            for f in (video, som, Path(td) / "log.txt"):
                if f.exists():
                    shutil.copy(f, a.saida.parent / f"cru_{f.name}")
        if som.exists() and som.stat().st_size > 0:
            # o motor abre o som em 44,1 kHz estéreo 16 bits (SDL disk grava cru); o começo do .raw é o começo do motor
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-f", "s16le",
                            "-ar", "44100", "-ac", "2", "-ss", f"{t_video:.2f}", "-i", str(som), "-map", "0:v", "-map", "1:a",
                            "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", str(a.saida)], check=True)
        else:
            print("sem áudio do motor (o SDL não gravou som.raw); vídeo mudo")
            shutil.copy(video, a.saida)
        if a.fotos:
            a.fotos.mkdir(parents=True, exist_ok=True)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(a.saida), "-vf", "fps=12",
                            str(a.fotos / "f_%03d.png")], check=True)
        print(f"{a.saida} (gravação começou {t_video:.1f} s depois de abrir o motor)")


if __name__ == "__main__":
    main()
