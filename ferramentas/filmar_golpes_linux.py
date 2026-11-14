#!/usr/bin/env python3
"""Filma golpes escolhidos dentro do jogo, na nuvem (Linux, Xvfb + Mesa), com o oponente parado na frente.

  python3 ferramentas/filmar_golpes_linux.py SAIDA.mp4 --p1 ck --p2 gutto --golpes "holdfwd+y,x" [--distancia 4]
                                             [--segundos 12] [--lenta 2] [--despertar] [--fotos PASTA]

É o modo --golpes do filmar_sandbox.py (Windows) para a nuvem: o P1 fica sem IA, se posiciona a --distancia px do
P2 (que fica parado) e solta, em volta, os comandos do .cmd ("+" junta comandos no mesmo tick: holdfwd+y é o
agarrão). O jogo roda a 1/--lenta da velocidade (o llvmpipe não segura 60 fps com a luta inteira) e o vídeo é
retimado para 60 fps: cada quadro do vídeo é um tick do jogo. --despertar entra na forma despertada antes dos golpes
(barra cheia e estado 2000). Usa a cópia do IKEMEN GO Linux do robô (~/.cache/nazafight/ikemen); o jogo instalado
não é tocado. Precisa de Xvfb e ffmpeg.
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

LUA = """
-- FILME NA NUVEM (ferramentas/filmar_golpes_linux.py): câmera lenta e marca de começo/fim da gravação
do
  local fase, ticks = "espera", 0
  hook.add("loop", "marca_luta", function()
    if fase == "espera" and roundState() == 2 then
      fase = "grava"
      setAccel(1 / @LENTA@)
      local f = io.open("@PASTA@/luta_comecou.txt", "w")
      if f then f:write("ok"); f:close() end
    elseif fase == "grava" then
      ticks = ticks + 1
    end
  end)
end
"""


def preparar_cmd(origem, destino, nomes, despertar):
    txt = origem.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "[Statedef -1]\n\n" in txt, f"sem [Statedef -1] em {origem}"
    faltam = sorted(set(nomes) - set(re.findall(r'^\s*name\s*=\s*"([^"]+)"', txt, re.M)))
    if faltam:
        sys.exit(f"comandos que não existem em {origem.name}: {', '.join(faltam)}")
    b = ""
    for c in sorted(set(nomes)):
        b += f'[State -1, F_{c}]\ntype = AssertCommand\ntrigger1 = map(t_{c}) = 1\nname = "{c}"\nbuffer.time = 1\n\n'
    b += '[State -1, F_pos]\ntype = PosSet\ntrigger1 = map(t_pos) = 1\nx = map(t_posx) - 1000\n\n'
    if despertar:
        quando = "triggerall = roundstate = 2 && var(20) = 0 && map(t_desp) = 0\ntrigger1 = statetype = S && ctrl\n"
        b += (f"[State -1, Filme enche a barra]\ntype = PowerSet\n{quando}value = powermax\n\n"
              "[State -1, Filme marca]\ntype = MapSet\ntrigger1 = stateno = 2000\nmap = \"t_desp\"\nvalue = 1\n\n"
              f"[State -1, Filme ativa o Despertar]\ntype = ChangeState\n{quando}value = 2000\n\n")
    destino.write_text(txt.replace("[Statedef -1]\n\n", "[Statedef -1]\n\n" + b, 1), encoding="utf-8", newline="\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("saida", type=Path)
    ap.add_argument("--p1", default="ck")
    ap.add_argument("--p2", default="gutto")
    ap.add_argument("--golpes", required=True)
    ap.add_argument("--distancia", type=int, default=4)
    ap.add_argument("--segundos", type=float, default=12, help="segundos de jogo filmados (em 60 ticks/s)")
    ap.add_argument("--lenta", type=int, default=2)
    ap.add_argument("--despertar", action="store_true")
    ap.add_argument("--fotos", type=Path, help="pasta para um quadro a cada 4 ticks (folha de contato)")
    ap.add_argument("--cenario", default="stages/stage0-720.def")
    a = ap.parse_args()
    golpes = [[n.strip() for n in g.split("+") if n.strip()] for g in a.golpes.split(",") if g.strip()]
    nomes = [n for g in golpes for n in g]
    motor = motor_linux()
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        copia = td / "motor"
        shutil.copytree(motor, copia, symlinks=True)
        for nome in {a.p1, a.p2}:
            shutil.copytree(RAIZ / "chars" / nome, copia / "chars" / nome, dirs_exist_ok=True)
        shutil.copytree(RAIZ / "motif" / "nazafight", copia / "data" / "nazafight", dirs_exist_ok=True)
        if (RAIZ / a.cenario).exists():
            shutil.copytree(RAIZ / "stages", copia / "stages", dirs_exist_ok=True)
        INI_LINUX["Motif"] = "data/nazafight/system.def"
        ajustar_ini(copia)
        preparar_cmd(RAIZ / "chars" / a.p1 / f"{a.p1}.cmd", copia / "chars" / a.p1 / f"{a.p1}.cmd", nomes,
                     a.despertar)
        lista = ", ".join("{" + ", ".join(f'"{n}"' for n in g) + "}" for g in golpes)
        lua = ((motor / "external/script/debug.lua").read_text(encoding="utf-8") + "\n"
               + LUA.replace("@LENTA@", str(a.lenta)).replace("@PASTA@", td.as_posix()) + "\n"
               + (RAIZ / "ferramentas/robo/golpes.lua").read_text(encoding="utf-8")
               .replace("{@GOLPES@}", "{" + lista + "}").replace("= @DIST@", f"= {a.distancia}"))
        (copia / "external/script/debug.lua").write_text(lua, encoding="utf-8")
        disp = f":{90 + os.getpid() % 9}"
        xvfb = subprocess.Popen(["Xvfb", disp, "-screen", "0", "1280x720x24"], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(2)
        amb = {**ambiente_linux(copia), "DISPLAY": disp}
        args = ["-p1", a.p1, "-p2", a.p2, "-s", a.cenario, "-rounds", "1"]
        jogo = subprocess.Popen(["./Ikemen_GO_Linux"] + args, cwd=copia, env=amb, stdout=open(td / "log.txt", "w"),
                                stderr=subprocess.STDOUT)
        try:
            limite = time.time() + 120
            while not (td / "luta_comecou.txt").exists():
                if time.time() > limite or jogo.poll() is not None:
                    sys.exit("a luta não começou:\n" + (td / "log.txt").read_text(errors="replace")[-2000:])
                time.sleep(0.5)
            bruto = td / "bruto.mp4"
            fps = 60 / a.lenta
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "x11grab", "-framerate", f"{fps:g}",
                            "-video_size", "1280x720", "-i", disp, "-t", f"{a.segundos * a.lenta:g}",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(bruto)], env=amb, check=True)
        finally:
            jogo.kill()
            xvfb.kill()
        a.saida.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(bruto), "-vf", f"setpts=PTS/{a.lenta}",
                        "-r", "60", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(a.saida)], check=True)
        if a.fotos:
            a.fotos.mkdir(parents=True, exist_ok=True)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(a.saida), "-vf", "fps=15,scale=640:-2",
                            str(a.fotos / "q_%04d.png")], check=True)
    print(f"vídeo: {a.saida}")


if __name__ == "__main__":
    main()
