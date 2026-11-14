"""Confere a trilha no motor de verdade (Linux sem tela, como o testar_pengaro.py --linux).

    python3 ferramentas/testar_musica.py [--lutador pengaro] [--volta]

--volta: em vez do Despertar, espera a música do cenário chegar ao fim e confere para onde o loop volta.

Abre uma luta no cenário da Maria Fumaça com o layout Nazafights e registra, tique a tique, o que o motor está
tocando (bgmVar). Roteiro: a música do cenário toca e dá a volta do loop; o P1 desperta (barra cheia + x+y) e a do
cenário baixa até sumir antes de entrar a do Despertar; o Despertar acaba e a do cenário volta.
O som sai no driver "dummy", mas o motor abre e decodifica os .ogg do mesmo jeito.
"""
import shutil
import subprocess
import sys
import tempfile
import time
import os
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import testar_pengaro as tp  # noqa: E402

RAIZ = tp.RAIZ

LUA = r'''
do
  local LOG = io.open("@SAIDA@", "w")
  local function log(s) LOG:write(s, "\n"); LOG:flush() end
  local function com(n, fn) local old = id(); player(n); local a = fn(); playerId(old); return a end
  local t, ultimo, fase, t_fase = 0, "", "cenario", 0
  local VOLTA, pos_antes = @VOLTA@, -1
  local function marca(nome) fase = nome; t_fase = t; log(string.format("[%5d] FASE %s", t, nome)) end
  local function mapa(nome, v) com(1, function() mapSet("t_" .. nome, v); return 0 end) end
  hook.add("loop", "musica", function()
    local ok, err = pcall(function()
      if roundState() ~= 2 then return end
      t = t + 1
      local f = bgmVar("filename") or "(nada)"
      local vol = bgmVar("volume") or -1
      local pos = bgmVar("position") or -1
      local d = com(1, function() return string.format("var20=%d var51=%d var52=%d st=%d", var(20), var(51), var(52), stateNo()) end)
      local linha = f .. " vol " .. vol
      if linha ~= ultimo or t % 60 == 0 then
        log(string.format("[%5d] %s pos %d  %s", t, linha, pos, d)); ultimo = linha
      end
      mapa("despertar", 0); mapa("fimdesp", 0)
      if VOLTA then  -- só a volta do loop do cenário: espera a posição voltar e diz para onde
        if pos_antes > 0 and pos < pos_antes then
          log(string.format("VOLTA DO LOOP: de %d para %d", pos_antes, pos)); log("FIM"); fase = "fim"
        end
        pos_antes = pos
        com(1, function() setLife(lifeMax()); return 0 end); com(2, function() setLife(lifeMax()); return 0 end)
        return
      end
      if fase == "cenario" and t >= 120 then com(1, function() setPower(3000); return 0 end); marca("aperta_despertar") end
      if fase == "aperta_despertar" and t - t_fase < 20 then mapa("despertar", 1) end
      if fase == "aperta_despertar" and t - t_fase >= 20 then marca("desperto") end
      if fase == "desperto" and t - t_fase >= 300 then marca("acaba_despertar") end
      if fase == "acaba_despertar" then mapa("fimdesp", 1) end
      if fase == "acaba_despertar" and t - t_fase >= 200 then log("FIM"); fase = "fim" end
      com(1, function() setLife(lifeMax()); return 0 end); com(2, function() setLife(lifeMax()); return 0 end)
    end)
    if not ok then log("ERRO NO ROBO: " .. tostring(err)) end
  end)
  log("musica carregado")
end
'''


def main():
    args = sys.argv[1:]
    lutador = args[args.index("--lutador") + 1] if "--lutador" in args else "pengaro"
    motor = tp.motor_linux()
    tmp = Path(tempfile.mkdtemp(prefix="teste_musica_"))
    try:
        copia = tmp / "motor"
        shutil.copytree(motor, copia, symlinks=True)
        for nome in (lutador, "hazaki"):
            shutil.copytree(RAIZ / "chars" / nome, copia / "chars" / nome, dirs_exist_ok=True)
        shutil.copytree(RAIZ / "stages", copia / "stages", dirs_exist_ok=True)
        shutil.copytree(RAIZ / "motif" / "nazafight", copia / "data" / "nazafight", dirs_exist_ok=True)
        tp.INI_LINUX["Motif"] = "data/nazafight/system.def"
        saida = tmp / "musica.txt"
        tp.preparar(copia, motor, lutador, saida.as_posix())
        debug = copia / "external/script/debug.lua"
        debug.write_text((motor / "external/script/debug.lua").read_text(encoding="utf-8") + "\n" +
                         LUA.replace("@SAIDA@", saida.as_posix())
                         .replace("@VOLTA@", "true" if "--volta" in args else "false"), encoding="utf-8")
        tp.ajustar_ini(copia)
        proc = subprocess.Popen(["xvfb-run", "-a", "-s", "-screen 0 1280x720x24", "./Ikemen_GO_Linux",
                                 "-p1", lutador, "-p2", "hazaki", "-s", "stages/maria_fumaca.def", "-rounds", "1"],
                                cwd=copia, env=tp.ambiente_linux(copia), stdout=open(tmp / "motor_log.txt", "w"),
                                stderr=subprocess.STDOUT, start_new_session=True)
        limite = time.time() + 1500
        while time.time() < limite and proc.poll() is None:
            if saida.exists() and re.search(r"^FIM|ERRO NO ROBO", saida.read_text(encoding="utf-8"), re.M):
                break
            time.sleep(2)
        try:
            os.killpg(proc.pid, 9)
        except ProcessLookupError:
            pass
        print(saida.read_text(encoding="utf-8") if saida.exists() else "sem saída")
        log = (tmp / "motor_log.txt").read_text(errors="replace")
        erros = [l for l in log.splitlines() if re.search(r"bgm|ogg|music", l, re.I)]
        print("\nlog do motor (bgm/ogg):", *erros[-20:] or ["nada"], sep="\n  ")
        for p in (copia / "save" / "logs").glob("*") if (copia / "save" / "logs").exists() else []:
            txt = p.read_text(errors="replace")
            if re.search(r"bgm|ogg", txt, re.I):
                print(p.name, txt[-1500:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
