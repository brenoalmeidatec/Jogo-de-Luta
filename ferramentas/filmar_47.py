#!/usr/bin/env python3
"""Filma o agarrão e o poder de longe do despertado (issue #47) no motor de verdade, na nuvem (Xvfb + Mesa).

  python3 ferramentas/filmar_47.py SAIDA.mp4 --p1 gutto [--p2 hazaki] [--segundos 28] [--fotos PASTA]

Usa a cópia do IKEMEN GO Linux do robô (~/.cache/nazafight/ikemen). Só na cópia, o .cns do P1 ganha um roteiro de
demonstração no [Statedef -2]: desperta no começo do round, segura o Despertar ligado e, num ciclo de 7 segundos,
põe o P2 a meia tela e solta o poder de longe (4750), depois põe o P2 colado e dá o agarrão da forma (4700). O P2
fica parado (sem IA) e com a vida cheia a cada ciclo. O jogo e os chars/ do repositório não são tocados.
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

CICLO = 420
PEGA = "RoundState = 2 && var(20) > 0 && GameTime % CICLO >= 260 && GameTime % CICLO < 400 && ctrl && stateno = 0 && enemynear,stateno = 0".replace("CICLO", str(CICLO))
ROTEIRO = f"""
[State -2, demo47 desperta]
type = ChangeState
trigger1 = RoundState = 2 && var(20) <= 0 && ctrl && statetype = S && stateno != 2000
value = 2000

[State -2, demo47 barra]
type = PowerSet
trigger1 = 1
value = PowerMax
ignorehitpause = 1

[State -2, demo47 segura o Despertar]
type = VarSet
trigger1 = var(20) > 0 && var(20) < 300
var(20) = 600
ignorehitpause = 1

[State -2, demo47 longe: P1]
type = PosSet
trigger1 = RoundState = 2 && var(20) > 0 && GameTime % {CICLO} = 10
x = -110
y = 0

[State -2, demo47 longe: P2]
type = PosSet
trigger1 = RoundState = 2 && var(20) > 0 && GameTime % {CICLO} = 10
redirectid = enemynear,id
x = 60
y = 0

[State -2, demo47 vida do P2]
type = LifeSet
trigger1 = RoundState = 2 && GameTime % {CICLO} = 10
redirectid = enemynear,id
value = 1000

[State -2, demo47 vira]
type = Turn
trigger1 = RoundState = 2 && (GameTime % {CICLO} = 12 || GameTime % {CICLO} = 255) && facing = -1

[State -2, demo47 poder]
type = ChangeState
trigger1 = RoundState = 2 && var(20) > 0 && GameTime % {CICLO} = 20
value = 4750

[State -2, demo47 colado: P1]
type = PosSet
trigger1 = {PEGA}
x = -40
y = 0

[State -2, demo47 colado: P2]
type = PosSet
trigger1 = {PEGA}
redirectid = enemynear,id
x = -6
y = 0

[State -2, demo47 agarrão]
type = ChangeState
trigger1 = {PEGA}
value = 4700

"""


def injetar(cns):
    txt = cns.read_text(encoding="utf-8")
    i = txt.index("[Statedef -2]")
    j = txt.index("\n\n", i) + 2
    cns.write_text(txt[:j] + ROTEIRO + txt[j:], encoding="utf-8", newline="\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("saida", type=Path)
    ap.add_argument("--p1", default="gutto")
    ap.add_argument("--p2", default="hazaki")
    ap.add_argument("--segundos", type=int, default=28)
    ap.add_argument("--espera", type=int, default=12)
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
        if (RAIZ / "stages").exists() and a.cenario.startswith("stages/"):
            shutil.copytree(RAIZ / "stages", copia / "stages", dirs_exist_ok=True)
        INI_LINUX["Motif"] = "data/nazafight/system.def"
        INI_LINUX["VSync"] = "1"
        ajustar_ini(copia)
        injetar(copia / "chars" / a.p1 / f"{a.p1}.cns")
        disp = f":{80 + os.getpid() % 9}"
        xvfb = subprocess.Popen(["Xvfb", disp, "-screen", "0", "1280x720x24"], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(2)
        amb = {**ambiente_linux(copia), "DISPLAY": disp}
        args = ["-p1", a.p1, "-p2", a.p2, "-s", a.cenario, "-rounds", "1"]
        log = open(Path(td) / "jogo.log", "w")
        jogo = subprocess.Popen(["./Ikemen_GO_Linux"] + args, cwd=copia, env=amb, stdout=log, stderr=log,
                                start_new_session=True)
        try:
            time.sleep(a.espera)
            a.saida.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "x11grab", "-framerate", "30", "-video_size",
                            "1280x720", "-i", disp, "-t", str(a.segundos), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                            "-crf", "22", str(a.saida)], env=amb, check=True)
            if a.fotos:
                a.fotos.mkdir(parents=True, exist_ok=True)
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(a.saida), "-vf", "fps=3",
                                str(a.fotos / "f_%03d.png")], check=True)
        finally:
            try:
                os.killpg(jogo.pid, 9)
            except ProcessLookupError:
                pass
            xvfb.kill()
            log.close()
            erros = [l for l in (Path(td) / "jogo.log").read_text(errors="replace").splitlines() if "rror" in l]
            for l in erros[:20]:
                print("motor:", l)
            logs = copia / "save" / "logs"
            if logs.exists():
                for f in logs.iterdir():
                    t = f.read_text(errors="replace")
                    if "rror" in t:
                        print(f"log {f.name}:", t[-1500:])
    print(a.saida)


if __name__ == "__main__":
    main()
