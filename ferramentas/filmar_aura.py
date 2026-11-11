#!/usr/bin/env python3
"""Filma o lutador de teste das auras (chars/teste_aura) na Windows Sandbox e guarda o que o motor fez a cada tick.

  python ferramentas/gerar_teste_aura.py
  python ferramentas/filmar_aura.py --saida PASTA [--segundos 10] [--lenta 4]

P1 (aura "ck") e P2 (aura "sombra") ficam parados; o roteiro liga o Despertar dos dois, solta dois surtos (o
especial de teste, estado 1000), troca o P1 de lado para os dois virarem, e desliga. Saída em PASTA: luta.mp4
(60 fps, um tick por quadro), aura_log.txt (por tick e por lutador: lado, nº de explods e, de cada camada, escala,
posição, elemento da animação e ângulo lidos do motor), ticks.txt e os logs do motor.
Usa as peças de filmar_sandbox.py e a trava de sandbox.py (uma sandbox por vez: espera a vez). Depois:
  python ferramentas/medir_aura.py PASTA
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import filmar_sandbox as fs  # noqa: E402
import sandbox  # noqa: E402

LIGA, SURTO1, VIRA, SURTO2, DESLIGA = 60, 220, 320, 390, 480
CAMADAS = {1: [9300, 9301, 9302, 9303], 2: [9340, 9341, 9342, 9343]}

ROTEIRO = """
-- ROTEIRO DO TESTE DE AURA (so na copia de dentro da sandbox)
do
  local t = 0
  local log = io.open("C:/nf/saida/aura_log.txt", "w")
  local CAM = {[1] = {@C1@}, [2] = {@C2@}}
  local function com(n, fn)
    local old = id()
    player(n)
    local a = fn()
    playerId(old)
    return a
  end
  local function v(x) if x == nil then return "-" end return string.format("%.3f", x) end
  hook.add("loop", "aura_teste", function()
    local ok, err = pcall(function()
      if roundState() ~= 2 or log == nil then return end
      t = t + 1
      local linha = {tostring(t)}
      for n = 1, 2 do
        com(n, function()
          mapSet("t_desp", (t >= @LIGA@ and t < @DESLIGA@) and 1 or 0)
          mapSet("t_surto", (t == @SURTO1@ or t == @SURTO2@) and 1 or 0)
          mapSet("t_pos", 0)
          if t == 2 then mapSet("t_posx", n == 1 and -90 or 20); mapSet("t_pos", 1) end
          if t == @VIRA@ and n == 1 then mapSet("t_posx", 118); mapSet("t_pos", 1) end
          linha[#linha + 1] = string.format("P%d f=%d x=%.1f st=%d ne=%d", n, facing(), posX(), stateNo(), numExplod())
          for _, e in ipairs(CAM[n]) do
            if numExplod(e) > 0 then
              linha[#linha + 1] = string.format("%d sx=%s sy=%s px=%s py=%s el=%s an=%s fa=%s", e,
                v(explodVar(e, 0, "scale x")), v(explodVar(e, 0, "scale y")), v(explodVar(e, 0, "pos x")),
                v(explodVar(e, 0, "pos y")), v(explodVar(e, 0, "animelem")), v(explodVar(e, 0, "angle")),
                v(explodVar(e, 0, "facing")))
            else
              linha[#linha + 1] = e .. " fora"
            end
          end
          return 0
        end)
      end
      log:write(table.concat(linha, " | "), "\\n")
      log:flush()
      if t > @FIM@ then log:close(); log = nil end
    end)
    if not ok and log then log:write("ERRO " .. tostring(err) .. "\\n"); log:flush() end
  end)
end
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--segundos", type=float, default=10)
    ap.add_argument("--lenta", type=int, default=4)
    ap.add_argument("--espera", type=float, default=900)
    a = ap.parse_args()
    if not (fs.RAIZ / "chars/teste_aura/teste_aura.sff").exists():
        sys.exit("rode antes: python ferramentas/gerar_teste_aura.py")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        sys.exit("ffmpeg não está no PATH do host")
    saida = a.saida.resolve()
    saida.mkdir(parents=True, exist_ok=True)
    trava = sandbox.esperar_vez()
    trab = Path(tempfile.mkdtemp(prefix="filme_aura_"))
    try:
        for velho in ("luta.mp4", "pronto.txt", "log_sandbox.txt", "ticks.txt", "aura_log.txt"):
            (saida / velho).unlink(missing_ok=True)
        roteiro = ROTEIRO
        for chave, valor in (("@C1@", ", ".join(map(str, CAMADAS[1]))), ("@C2@", ", ".join(map(str, CAMADAS[2]))),
                             ("@LIGA@", LIGA), ("@DESLIGA@", DESLIGA), ("@SURTO1@", SURTO1), ("@SURTO2@", SURTO2),
                             ("@VIRA@", VIRA), ("@FIM@", int(a.segundos * 60) + 120)):
            roteiro = roteiro.replace(chave, str(valor))
        lua = ((fs.MOTOR / "external/script/debug.lua").read_text(encoding="utf-8") + "\n"
               + fs.MARCA.replace("@LENTA@", str(a.lenta)) + "\n" + roteiro)
        (trab / "por_cima/external/script").mkdir(parents=True)
        (trab / "por_cima/external/script/debug.lua").write_text(lua, encoding="utf-8")
        args = ["-p1", "teste_aura", "-p2", "teste_aura", "-s", "stages/stage0-720.def", "-rounds", "1"]
        ps1 = (fs.PS1.replace("@LUTADORES@", "'teste_aura'").replace("@ARGS@", " ".join(args))
               .replace("@SEGUNDOS_REAIS@", f"{a.segundos * a.lenta:g}").replace("@LENTA@", str(a.lenta))
               .replace("@FPS_CAPTURA@", f"{60 / a.lenta:g}").replace("@TITULO@", fs.titulo_da_janela()))
        (trab / "rodar.ps1").write_text(ps1, encoding="utf-8-sig")
        pastas = [(fs.MOTOR, r"C:\nf\motor", True), (fs.RAIZ, r"C:\nf\repo", True), (fs.MESA, r"C:\nf\mesa", True),
                  (Path(ffmpeg).parent, r"C:\nf\ffmpeg", True), (trab, r"C:\nf\trabalho", True),
                  (saida, r"C:\nf\saida", False)]
        wsb = trab / "filme.wsb"
        wsb.write_text(fs.wsb_xml(pastas, r"powershell.exe -NoProfile -ExecutionPolicy Bypass -File "
                                          r"C:\nf\trabalho\rodar.ps1"), encoding="utf-8")
        print(f"abrindo a Windows Sandbox (sem rede, sem vGPU); saída em {saida}", flush=True)
        t0 = time.time()
        subprocess.Popen([str(fs.SANDBOX_EXE), str(wsb)])
        while time.time() - t0 < a.espera and not (saida / "pronto.txt").exists():
            time.sleep(2)
        pronto = (saida / "pronto.txt").exists()
        time.sleep(3)
        fs.fechar_sandbox()
        video = saida / "luta.mp4"
        if not pronto:
            sys.exit(f"a sandbox não terminou em {a.espera:g} s; veja {saida / 'log_sandbox.txt'}")
        if not video.exists() or video.stat().st_size == 0:
            sys.exit(f"sem vídeo; veja {saida / 'log_sandbox.txt'}")
        ticks = (saida / "ticks.txt").read_text(encoding="utf-8").strip() if (saida / "ticks.txt").exists() else "?"
        print(f"vídeo: {video} ({time.time() - t0:.0f} s; {ticks}, esperado ~{a.segundos * 60:g})")
    finally:
        shutil.rmtree(trab, ignore_errors=True)
        trava.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
