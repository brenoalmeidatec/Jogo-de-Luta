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


def filmar(chars, lutador, despertado, combate=False, isolar_tenis=False, roteiro=None):
    motor = motor_linux()
    with tempfile.TemporaryDirectory() as pasta:
        copia = Path(pasta) / "motor"
        shutil.copytree(motor, copia)
        rival = "gbzin" if lutador == "hazaki" else "hazaki"
        for nome in (lutador, rival):
            shutil.copytree(chars / nome, copia / "chars" / nome, dirs_exist_ok=True)
        ajustar_ini(copia)
        if roteiro:
            # Usa o mesmo HUD do jogo instalado, inclusive a escala dos retratos HD.
            motif = Path(__file__).resolve().parents[1] / "motif/nazafight"
            if (motif / "system.def").is_file():
                import re
                shutil.copytree(motif, copia / "data/nazafight", dirs_exist_ok=True)
                ini = copia / "save/config.ini"
                config = re.sub(r"(?im)^(Motif\s*=\s*)[^\r\n]*", r"\g<1>data/nazafight/system.def",
                                ini.read_text(encoding="utf8"))
                ini.write_text(config, encoding="utf8")
        if despertado:
            from filmar_golpes_linux import preparar_cmd
            cmd = Path("chars") / lutador / f"{lutador}.cmd"
            preparar_cmd(chars.parent / cmd, copia / cmd, [], True)
        gancho = GANCHO
        total = 82
        if combate:
            import ck_roteiro as roteiro
        if roteiro:
            total, gancho = roteiro.configurar(copia, gancho, isolar_tenis)
        with (copia / "external/script/debug.lua").open("a") as f:
            f.write(gancho.replace("@DESPERTADO@", "true" if despertado else "false"))
        jogo = subprocess.Popen(["./Ikemen_GO_Linux", "-p1", lutador, "-p2", rival,
                                 "-s", "stages/stage0-720.def", "-rounds", "1"],
                                cwd=copia, env=ambiente_linux(copia))
        quadros, estados = [], []
        try:
            for tick in range(1, total + 1):
                marca = copia / "quadro"
                prazo = time.monotonic() + 120
                while not marca.exists():
                    if jogo.poll() is not None or time.monotonic() > prazo:
                        raise RuntimeError(f"Motor parou antes do tique {tick}")
                    time.sleep(.005)
                numero, estado, animacao, *dados = map(float, marca.read_text().split())
                assert numero == tick
                estados.append((int(estado), int(animacao), *dados))
                if tick == 1:
                    janela = subprocess.check_output(["xdotool", "search", "--onlyvisible", "--pid",
                                                      str(jogo.pid)], text=True).splitlines()[-1]
                    geometria = subprocess.check_output(["xdotool", "getwindowgeometry", "--shell", janela], text=True)
                    dados = dict(l.split("=", 1) for l in geometria.splitlines() if "=" in l)
                    x, y, w, h = (int(dados[k]) for k in ("X", "Y", "WIDTH", "HEIGHT"))
                    subprocess.run(["xdotool", "windowfocus", janela], check=True)
                captura = ImageGrab.grab(bbox=(x, y, x + w, y + h), xdisplay=os.environ["DISPLAY"])
                recorte = captura.crop((int(w*.10), int(h*.27), int(w*.53), int(h*.96)))
                if roteiro:
                    recorte = captura.crop((int(w*.08), int(h*.24), int(w*.90), int(h*.99)))
                    if getattr(roteiro, "tela_inteira", False):
                        recorte = captura.crop((int(w*.07), 0, int(w*.94), int(h*.98)))
                    quadros.append(recorte.resize((480, 290), Image.Resampling.NEAREST))
                else:
                    quadros.append(recorte.resize((320, 290), Image.Resampling.NEAREST))
                if roteiro:
                    roteiro.teclas(tick)
                elif tick in (10, 66):
                    subprocess.run(["xdotool", "keydown" if tick == 10 else "keyup", "Down"], check=True)
                marca.unlink()
                (copia / "avancar").touch()
        finally:
            jogo.kill()
            jogo.wait()
            subprocess.run(["xdotool", "keyup", "Down", "Left", "Right"])
        print("Estados capturados", sorted({e[:2] for e in estados}), flush=True)
        if roteiro:
            roteiro.validar(estados)
        else:
            assert {0, 10, 11, 12} <= {e[1] for e in estados}, estados
        return quadros, estados


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("antes", type=Path)
    parser.add_argument("depois", type=Path)
    parser.add_argument("gif", type=Path)
    parser.add_argument("--lutador", default="gbzin")
    parser.add_argument("--despertado", action="store_true")
    parser.add_argument("--medir-tenis-ck", action="store_true")
    parser.add_argument("--combate-ck", action="store_true")
    args = parser.parse_args()
    antes, ea = filmar(args.antes, args.lutador, args.despertado, args.combate_ck)
    depois, ed = filmar(args.depois, args.lutador, args.despertado, args.combate_ck)
    assert ea == ed, "As transições não coincidem nos dois filmes"
    if args.medir_tenis_ck:
        from medir_tenis_ck import medir
        medir(depois, ed)
    quadros = []
    largura = antes[0].width
    for a, b in zip(antes, depois):
        tela = Image.new("RGB", (largura*2+4, 316), "#20232c")
        tela.paste(a, (0, 26))
        tela.paste(b, (largura+4, 26))
        d = ImageDraw.Draw(tela)
        d.text((12, 6), "ANTES", fill="white")
        d.text((largura+16, 6), "DEPOIS  /  KIT DE PECAS", fill="white")
        quadros.append(tela)
    assert any(a.tobytes() != b.tobytes() for a, b in zip(antes[16:50], depois[16:50]))
    quadros[0].save(args.gif, save_all=True, append_images=quadros[1:], duration=50, loop=0)

    if args.combate_ck:
        from ck_roteiro import medir
        isolados, telemetria = filmar(args.depois, args.lutador, False, True, True)
        assert ed == telemetria, "A repetição para medir mudou a luta"
        try:
            medir(isolados, telemetria)
        except AssertionError:
            import json
            pasta = Path("diagnostico")
            pasta.mkdir(exist_ok=True)
            for i, im in enumerate(isolados):
                im.save(pasta / f"{i:03d}.png")
            (pasta / "estados.json").write_text(json.dumps(telemetria))
            raise
