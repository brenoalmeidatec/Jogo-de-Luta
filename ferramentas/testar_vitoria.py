#!/usr/bin/env python3
"""Filma a tela de vitória de verdade na nuvem (Xvfb), no modo Assistir (CPU x CPU).

  python3 ferramentas/testar_vitoria.py [--baixo N] [--casa N] [--rival N] [--despertado] [--saida PASTA] [--segundos S]

Monta o jogo como o testar_mapas.py (lutadores, cenários, layout Nazafights), entra em Assistir, escolhe o lutador da
casa --casa (P1) e o da
casa --rival (P2: o cursor dele nasce na 4a casa da 1a linha e dá a volta; 0 Raiclaven, 1 Pengaró, 2 Hazak, 3 Gutto) e, para a luta não demorar, deixa
o P2 com 1 de vida a cada round (um script no debug.lua da cópia): o P1 vence a luta e aparece a tela de vitória
dele. Com --despertado, a barra do P1 fica cheia para a CPU despertar, e a fala sai da lista do Despertar.
Grava vitoria.mp4, fotos dos passos do menu e vitoria_log.txt (quem venceu e a forma de cada um).
"""
import argparse
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from testar_mapas import Tela, montar  # noqa: E402
from testar_pengaro import RAIZ  # noqa: E402

LUA = """
-- testar_vitoria.py: o P2 fica com 1 de vida depois de 1,5 s de luta (o P1 vence rapido); --despertado enche a
-- barra do P1 para a CPU despertar antes de ganhar.
do
  local t, despertado = 0, @DESPERTADO@
  hook.add("loop", "testar_vitoria", function()
    pcall(function()
      if roundState() ~= 2 then t = 0; return end
      t = t + 1
      local old = id()
      if despertado then player(1); setPower(powerMax()) end
      if t == (despertado and 600 or 90) then player(2); setLife(1) end
      playerId(old)
    end)
  end)
  hook.add("game.victory_init", "testar_vitoria_log", function()
    pcall(function()
      local f = io.open("@LOG@", "a")
      local old = id()
      local s = "vence=" .. tostring(getWinnerTeam())
      for p = 1, 2 do player(p); s = s .. string.format(" p%d=%s var20=%d", p, name(), var(20)) end
      playerId(old)
      f:write(s, string.char(10)); f:close()
    end)
  end)
end
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", type=Path, default=RAIZ / "saida_vitoria")
    ap.add_argument("--casa", type=int, default=0)
    ap.add_argument("--baixo", type=int, default=0, help="linhas para baixo antes do --casa (CK e Gbzin na 2a linha)")
    ap.add_argument("--rival", type=int, default=1)
    ap.add_argument("--despertado", action="store_true")
    ap.add_argument("--segundos", type=float, default=70)
    ap.add_argument("--espera-titulo", type=float, default=25)
    a = ap.parse_args()
    a.saida.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        copia = montar(Path(td))
        dbg = copia / "external/script/debug.lua"
        dbg.write_text(dbg.read_text(encoding="utf-8") + LUA.replace("@DESPERTADO@", "true" if a.despertado else "false").replace("@LOG@", (a.saida / "vitoria_log.txt").as_posix()),
                       encoding="utf-8")
        t = Tela(copia, a.saida)
        try:
            time.sleep(a.espera_titulo)
            t.tecla("Return")
            time.sleep(3)
            t.tecla("Down", 4)            # Assistir
            t.tecla("Return")
            time.sleep(5)
            t.foto("passo_1.png")
            t.tecla("Return")             # Assistir abre o menu de time (Single) do P1...
            time.sleep(1.5)
            t.tecla("Down", a.baixo)
            t.tecla("Right", a.casa)
            t.tecla("Return")             # ... o lutador do P1
            time.sleep(1.5)
            t.foto("passo_2.png")
            t.tecla("Return")             # o menu de time do P2
            time.sleep(1.5)
            t.tecla("Right", a.rival)     # o cursor do P2 nasce na 4a casa e dá a volta na linha
            t.tecla("Return")
            time.sleep(3.5)
            t.foto("passo_3.png")
            t.tecla("Return")             # mapa
            filme = subprocess.Popen(
                ["ffmpeg", "-y", "-loglevel", "error", "-f", "x11grab", "-video_size", "1280x720", "-framerate", "30",
                 "-i", t.disp, "-t", str(a.segundos), "-pix_fmt", "yuv420p", str(a.saida / "vitoria.mp4")],
                env=t.amb)
            filme.wait()
        finally:
            t.fechar()
    print("pronto:", a.saida / "vitoria.mp4")


if __name__ == "__main__":
    main()
