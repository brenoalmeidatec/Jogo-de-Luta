"""Captura no X11 duas lutas reais, avançando o motor um tique por captura."""
import os
import argparse
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageGrab
from testar_pengaro import ajustar_ini, ambiente_linux, motor_linux


GANCHO = """
local t = 0
hook.add("loop", "gbzin_captura", function()
  if roundState() ~= 2 then return end
  player(1)
  if @DESPERTADO@ and t == 0 and (var(20) <= 0 or stateNo() ~= 0 or not ctrl()) then return end
  t = t + 1
  if t > 82 then return end
  local f = assert(io.open("quadro.tmp", "w"))
  f:write(t .. " " .. stateNo() .. " " .. anim()); f:close()
  os.rename("quadro.tmp", "quadro")
  local inicio = os.time()
  while os.time() - inicio < 15 do
    local ack = io.open("avancar", "r")
    if ack then ack:close(); os.remove("avancar"); break end
  end
end)
"""


def filmar(chars, lutador, despertado):
    motor = motor_linux()
    with tempfile.TemporaryDirectory() as pasta:
        copia = Path(pasta) / "motor"
        shutil.copytree(motor, copia)
        rival = "gbzin" if lutador == "hazaki" else "hazaki"
        for nome in (lutador, rival):
            shutil.copytree(chars / nome, copia / "chars" / nome, dirs_exist_ok=True)
        ajustar_ini(copia)
        if despertado:
            from filmar_golpes_linux import preparar_cmd
            cmd = Path("chars") / lutador / f"{lutador}.cmd"
            preparar_cmd(chars.parent / cmd, copia / cmd, [], True)
        with (copia / "external/script/debug.lua").open("a") as f:
            f.write(GANCHO.replace("@DESPERTADO@", "true" if despertado else "false"))
        jogo = subprocess.Popen(["./Ikemen_GO_Linux", "-p1", lutador, "-p2", rival,
                                 "-s", "stages/stage0-720.def", "-rounds", "1"],
                                cwd=copia, env=ambiente_linux(copia))
        quadros, estados = [], []
        try:
            for tick in range(1, 83):
                marca = copia / "quadro"
                prazo = time.monotonic() + 120
                while not marca.exists():
                    if jogo.poll() is not None or time.monotonic() > prazo:
                        raise RuntimeError(f"Motor parou antes do tique {tick}")
                    time.sleep(.005)
                numero, estado, animacao = map(int, marca.read_text().split())
                assert numero == tick
                estados.append((estado, animacao))
                if tick == 1:
                    janela = subprocess.check_output(["xdotool", "search", "--onlyvisible", "--pid",
                                                      str(jogo.pid)], text=True).splitlines()[-1]
                    geometria = subprocess.check_output(["xdotool", "getwindowgeometry", "--shell", janela], text=True)
                    dados = dict(l.split("=", 1) for l in geometria.splitlines() if "=" in l)
                    x, y, w, h = (int(dados[k]) for k in ("X", "Y", "WIDTH", "HEIGHT"))
                    subprocess.run(["xdotool", "windowfocus", janela], check=True)
                captura = ImageGrab.grab(bbox=(x, y, x + w, y + h), xdisplay=os.environ["DISPLAY"])
                recorte = captura.crop((int(w*.10), int(h*.27), int(w*.53), int(h*.96)))
                quadros.append(recorte.resize((320, 290), Image.Resampling.NEAREST))
                if tick in (10, 66):
                    subprocess.run(["xdotool", "keydown" if tick == 10 else "keyup", "Down"], check=True)
                marca.unlink()
                (copia / "avancar").touch()
        finally:
            jogo.kill()
            jogo.wait()
            subprocess.run(["xdotool", "keyup", "Down"])
        print("Estados capturados", sorted(set(estados)), flush=True)
        assert {0, 10, 11, 12} <= {a for _, a in estados}, estados
        return quadros, estados


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("antes", type=Path)
    parser.add_argument("depois", type=Path)
    parser.add_argument("gif", type=Path)
    parser.add_argument("--lutador", default="gbzin")
    parser.add_argument("--despertado", action="store_true")
    parser.add_argument("--medir-tenis-ck", action="store_true")
    args = parser.parse_args()
    antes, ea = filmar(args.antes, args.lutador, args.despertado)
    depois, ed = filmar(args.depois, args.lutador, args.despertado)
    assert ea == ed, "As transições não coincidem nos dois filmes"
    if args.medir_tenis_ck:
        from medir_tenis_ck import medir
        medir(depois, ed)
    quadros = []
    for a, b in zip(antes, depois):
        tela = Image.new("RGB", (644, 316), "#20232c")
        tela.paste(a, (0, 26))
        tela.paste(b, (324, 26))
        d = ImageDraw.Draw(tela)
        d.text((12, 6), "ANTES", fill="white")
        d.text((336, 6), "DEPOIS  /  KIT DE PECAS", fill="white")
        quadros.append(tela)
    assert any(a.tobytes() != b.tobytes() for a, b in zip(antes[16:50], depois[16:50]))
    quadros[0].save(args.gif, save_all=True, append_images=quadros[1:], duration=50, loop=0)
