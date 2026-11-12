#!/usr/bin/env python3
"""Filma o lutador de teste das auras (chars/teste_aura) na Windows Sandbox e guarda o que o motor fez a cada tick.

  python ferramentas/gerar_teste_aura.py
  python ferramentas/filmar_aura.py --saida PASTA [--roteiro padrao|extra] [--segundos 10] [--lenta 6]

Roteiro "padrao" (10 s): P1 (aura "ck") e P2 (aura "sombra") parados; liga o Despertar dos dois, solta dois surtos
(o especial de teste, estado 1000), troca o P1 de lado para os dois virarem, desliga e, com a aura apagada, repete o especial (referência do corpo).
Roteiro "extra" (2 rounds, o que o padrão não cobre): superpausa do P1, P2 em estado custom (golpe de teste), os
dois pulando, KO do P2 (a aura do vencedor tem de seguir na pose de vitória) e o round 2 (nada sobra antes da intro;
a aura volta na intro porque o Despertar segue ligado).
Os dois usam o HUD do jogo (motif/nazafight deste checkout), não o do motor.
Saída em PASTA: luta.mp4 (60 fps, um tick por quadro), aura_log.txt (por tick e por lutador: lado, posição, estado,
nº de explods e, de cada camada, escala, posição, elemento da animação e ângulo lidos do motor), ticks.txt e os logs
do motor. Usa as peças de filmar_sandbox.py e a trava de sandbox.py (uma sandbox por vez: espera a vez). Depois:
  python ferramentas/medir_aura.py PASTA            (roteiro padrao)
  python ferramentas/medir_aura.py PASTA --extra    (roteiro extra)
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
SOCO_SEM_AURA = 545  # o mesmo especial com a aura já apagada: referência do corpo para medir o surto
# roteiro extra (ticks do round 1; no round 2 o Despertar segue ligado até o tick X_DESLIGA2)
X_LIGA, X_SUPER, X_GOLPE, X_PULO, X_KO, X_DESLIGA2 = 30, 120, 220, 320, 420, 90
CAMADAS = {1: [9600, 9601, 9602, 9603], 2: [9640, 9641, 9642, 9643]}

ROTEIRO = """
-- ROTEIRO DO TESTE DE AURA (so na copia de dentro da sandbox)
do
  local g, t, rn = 0, 0, 0
  local extra = @EXTRA@
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
      if log == nil then return end
      local rs = roundState()
      if not extra and rs ~= 2 then return end
      g = g + 1
      if roundNo() ~= rn then rn = roundNo(); t = 0 end
      if rs == 2 then t = t + 1 end
      local linha = {tostring(extra and g or t), string.format("t=%d rs=%d rn=%d", t, rs, rn)}
      for n = 1, 2 do
        com(n, function()
          if rs == 2 and not extra then
            mapSet("t_desp", (t >= @LIGA@ and t < @DESLIGA@) and 1 or 0)
            mapSet("t_surto", (t == @SURTO1@ or t == @SURTO2@ or t == @SOCO@) and 1 or 0)
            mapSet("t_pos", 0)
            if t == 2 then mapSet("t_posx", n == 1 and -90 or 20); mapSet("t_pos", 1) end
            if t == @VIRA@ and n == 1 then mapSet("t_posx", 118); mapSet("t_pos", 1) end
          elseif rs == 2 then
            if rn == 1 then mapSet("t_desp", t >= @X_LIGA@ and 1 or 0)
            elseif t >= @X_DESLIGA2@ then mapSet("t_desp", 0) end
            mapSet("t_pos", 0)
            if t == 2 then mapSet("t_posx", n == 1 and -30 or 30); mapSet("t_pos", 1) end
            mapSet("t_super", (rn == 1 and n == 1 and t == @X_SUPER@) and 1 or 0)
            mapSet("t_golpe", (rn == 1 and n == 1 and t == @X_GOLPE@) and 1 or 0)
            mapSet("t_pulo", (rn == 1 and t == @X_PULO@) and 1 or 0)
            if rn == 1 and n == 2 and t == @X_KO@ then setLife(0) end
          end
          linha[#linha + 1] = string.format("P%d f=%d x=%.1f st=%d ne=%d y=%.1f h=%.2f", n, facing(), posX(),
            stateNo(), numExplod(), posY(), map(n == 1 and "au_ck_h2" or "au_sombra_h2"))
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
      if g > @FIM@ then log:close(); log = nil end
    end)
    if not ok and log then log:write("ERRO " .. tostring(err) .. "\\n"); log:flush() end
  end)
end
"""


def pane(saida):
    """Texto do erro se o roteiro falhou dentro do motor (linha ERRO no log), senão None."""
    log = saida / "aura_log.txt"
    if log.exists():
        for linha in log.read_text(encoding="utf-8", errors="replace").splitlines()[:40]:
            if linha.startswith("ERRO"):
                return linha
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--roteiro", choices=("padrao", "extra"), default="padrao")
    ap.add_argument("--segundos", type=float, help="padrão: 10 (roteiro padrao) ou 26 (extra)")
    ap.add_argument("--lenta", type=int, help="padrão: 6 (roteiro padrao) ou 3 (extra); o motor na sandbox, sem placa de vídeo, não segura mais que isso")
    ap.add_argument("--espera", type=float, default=900)
    ap.add_argument("--arranque", type=float, default=360,
                    help="segundos para o roteiro começar a escrever o log; se não começar, é pane do motor")
    ap.add_argument("--hud", choices=("jogo", "motor"), default="jogo",
                    help="jogo: motif/nazafight deste checkout; motor: o que estiver no config do motor")
    a = ap.parse_args()
    extra = a.roteiro == "extra"
    segundos = a.segundos or (26 if extra else 10)
    lenta = a.lenta or (3 if extra else 6)
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
                             ("@VIRA@", VIRA), ("@SOCO@", SOCO_SEM_AURA), ("@FIM@", int(segundos * 60) + 600), ("@EXTRA@", str(extra).lower()),
                             ("@X_LIGA@", X_LIGA), ("@X_SUPER@", X_SUPER), ("@X_GOLPE@", X_GOLPE),
                             ("@X_PULO@", X_PULO), ("@X_KO@", X_KO), ("@X_DESLIGA2@", X_DESLIGA2)):
            roteiro = roteiro.replace(chave, str(valor))
        lua = ((fs.MOTOR / "external/script/debug.lua").read_text(encoding="utf-8") + "\n"
               + fs.MARCA.replace("@LENTA@", str(lenta)) + "\n" + roteiro)
        (trab / "por_cima/external/script").mkdir(parents=True)
        (trab / "por_cima/external/script/debug.lua").write_text(lua, encoding="utf-8")
        ps1 = fs.PS1
        if a.hud == "jogo":  # o HUD do jogo por cima do motor, e o config apontando para ele
            shutil.copytree(fs.RAIZ / "motif/nazafight", trab / "por_cima/data/nazafight")
            marca = "@('MasterVolume','0')"
            assert marca in ps1
            ps1 = ps1.replace(marca, "@('Motif','data/nazafight/system.def')," + marca)
        args = ["-p1", "teste_aura", "-p2", "teste_aura", "-s", "stages/stage0-720.def", "-rounds",
                "2" if extra else "1"]
        ps1 = (ps1.replace("@LUTADORES@", "'teste_aura'").replace("@ARGS@", " ".join(args))
               .replace("@SEGUNDOS_REAIS@", f"{segundos * lenta:g}").replace("@LENTA@", str(lenta))
               .replace("@FPS_CAPTURA@", f"{60 / lenta:g}").replace("@TITULO@", fs.titulo_da_janela()))
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
        motivo = None
        while time.time() - t0 < a.espera and not (saida / "pronto.txt").exists():
            time.sleep(2)
            # pane do motor (Lua que não carrega, lutador que não abre): o roteiro nunca escreve, ou escreve ERRO.
            # Sem isto a sandbox e a trava ficavam presas até o fim de --espera.
            if pane(saida):
                motivo = f"o roteiro falhou dentro do motor: {pane(saida)}"
            elif time.time() - t0 > a.arranque and not (saida / "aura_log.txt").exists():
                motivo = f"o roteiro não começou em {a.arranque:g} s (pane do motor ou do Lua)"
            if motivo:
                break
        pronto = (saida / "pronto.txt").exists()
        time.sleep(3)
        fs.fechar_sandbox()
        video = saida / "luta.mp4"
        if motivo:
            erro = saida / "motor_stderr.txt"
            rabo = erro.read_text(encoding="utf-8", errors="replace")[-600:] if erro.exists() else ""
            sys.exit(f"{motivo}; sandbox fechada aos {time.time() - t0:.0f} s. {rabo}")
        if not pronto:
            sys.exit(f"a sandbox não terminou em {a.espera:g} s; veja {saida / 'log_sandbox.txt'}")
        if not video.exists() or video.stat().st_size == 0:
            sys.exit(f"sem vídeo; veja {saida / 'log_sandbox.txt'}")
        ticks = (saida / "ticks.txt").read_text(encoding="utf-8").strip() if (saida / "ticks.txt").exists() else "?"
        print(f"vídeo: {video} ({time.time() - t0:.0f} s; {ticks}, esperado ~{segundos * 60:g})")
    finally:
        shutil.rmtree(trab, ignore_errors=True)
        trava.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
