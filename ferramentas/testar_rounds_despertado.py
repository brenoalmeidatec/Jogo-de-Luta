#!/usr/bin/env python3
"""Robô de dois rounds: quem vence despertado tem de começar o round seguinte despertado (Breno, #32, 2026-11-24).

    python3 ferramentas/testar_rounds_despertado.py [lutador ...] [--video PASTA] [--antes REF]

Roda na nuvem (Linux, Xvfb + Mesa llvmpipe), na mesma cópia do IKEMEN GO v1.0.0 do testar_pengaro.py. Para cada
lutador com Despertar: luta de 2 rounds contra o Hazak parado. No round 1 o P1 desperta (barra cheia + despertar),
espera a cena acabar, e o robô nocauteia o P2. No round 2 o registro segue tique a tique e confere:

  1. a forma volta (var20 > 0) e o corpo é o endiabrado (var37 = 1 com o RemapSprite ligado de verdade: ver abaixo);
  2. o lutador não fica travado: ganha ctrl, solta um chute fraco e depois um soco fraco;
  3. a aura do endiabrado está viva (Explods 9600+).

O RemapSprite não aparece no Lua do motor, então a cópia de teste ganha uma marca (var 57, só na cópia): vai a 1 a cada
"Vira endiabrado" e a 0 a cada "Volta ao normal" que dispara. Com a forma ligada ela tem de terminar o tique em 1.

--video PASTA grava um .mp4 por lutador (tempo real, 30 quadros por segundo) e a última foto da luta.
--antes REF usa os chars/ do commit REF do git (para o vídeo "antes" sair do jogo antigo, não do atual).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import testar_pengaro as tp  # noqa: E402

RAIZ = tp.RAIZ
LUTADORES = ("pengaro", "ck", "gutto", "raiclaven", "hazaki", "gbzin")

LUA = r'''
do
  local LOG = io.open("@SAIDA@", "w")
  local function log(s) LOG:write(s, "\n"); LOG:flush() end
  local function com(n, fn) local old = id(); player(n); local a = fn(); playerId(old); return a end
  local function mapa(nome, v) com(1, function() mapSet("t_" .. nome, v); return 0 end) end
  local ACCEL = @ACCEL@
  local fase, t, tf, rodada, t2 = "espera", 0, 0, 1, 0
  local x0, st_soco, st_chute, falhas = 0, -1, -1, 0
  local visto = {forma = false, corpo = false, ctrl = false, anda = false, soco = false, aura = false}
  local function aura() return com(1, function() local k = 0; for e = 9600, 9609 do k = k + numExplod(e) end; return k end) end
  local function p1(campo)
    return com(1, function()
      if campo == "linha" then
        return string.format("st=%d ctrl=%s anim=%d var20=%d var37=%d var57=%d var58=%d x=%.0f",
          stateNo(), tostring(ctrl()), (anim and anim()) or -1, var(20), var(37), var(57), var(58), posX())
      end
      return 0
    end)
  end
  local function v(n) return com(1, function() return var(n) end) end
  local function marca(nome) fase = nome; tf = t; log(string.format("[%5d] FASE %s", t, nome)) end
  local function confere(ok, txt) log((ok and "PASS " or "FAIL ") .. txt); if not ok then falhas = falhas + 1 end end
  hook.add("loop", "rounds", function()
    local ok, err = pcall(function()
      local rs = roundState()
      t = t + 1
      mapa("despertar", 0); mapa("a", 0); mapa("x", 0)
      if rodada == 1 then
        if rs ~= 2 then return end
        com(1, function() setLife(lifeMax()); return 0 end)
        if fase == "espera" and t > 60 then com(1, function() setPower(powerMax()); return 0 end); marca("desperta") end
        if fase == "desperta" then
          if t - tf < 20 then mapa("despertar", 1) end
          if v(20) > 0 and com(1, function() return ctrl() and stateNo() == 0 end) then marca("forma") end
          if t - tf > 900 then log("FAIL nao despertou no round 1"); falhas = falhas + 1; log("FIM"); rodada = 9 end
        end
        if fase == "forma" and t - tf >= 90 then
          log("round 1 antes do nocaute: " .. p1("linha") .. string.format(" aura=%d", aura()))
          com(2, function() setLife(0); return 0 end); marca("nocaute")
        end
        if fase == "nocaute" then
          com(2, function() setLife(0); return 0 end)
        end
        return
      end
      if rodada == 9 then return end
      t2 = t2 + 1
      if t2 % 10 == 0 or (rs == 2 and t2 % 2 == 0 and fase ~= "fim") then
        log(string.format("[r2 %4d] rs=%d %s aura=%d", t2, rs, p1("linha"), aura()))
      end
      if rs < 2 then return end
      if fase ~= "r2" and fase ~= "anda" and fase ~= "soco" and fase ~= "fim" then marca("r2") end
      if v(20) > 0 then visto.forma = true end
      if v(37) == 1 and v(57) == 1 then visto.corpo = true end
      if aura() > 0 then visto.aura = true end
      if com(1, function() return ctrl() end) then visto.ctrl = true end
      if fase == "r2" and t - tf >= 30 and com(1, function() return ctrl() and stateNo() == 0 end) then
        x0 = com(1, function() return posX() end); marca("anda")
      end
      if fase == "r2" and t - tf >= 400 then marca("soco") end
      if fase == "anda" then
        -- chute fraco primeiro (o andar do motor não sai por AssertCommand: o holdfwd do robô não anda)
        if t - tf < 4 then mapa("a", 1) end
        local st = com(1, function() return stateNo() end)
        if com(1, function() return moveType() end) == "A" then visto.anda = true; st_chute = st end
        if t - tf >= 60 and com(1, function() return ctrl() end) then marca("soco") end
        if t - tf >= 200 then marca("soco") end
      end
      if fase == "soco" then
        if t - tf < 4 then mapa("x", 1) end
        local st = com(1, function() return stateNo() end)
        if t - tf < 30 and com(1, function() return moveType() end) == "A" then visto.soco = true; st_soco = st end
        if t - tf >= 60 then
          log("round 2: " .. p1("linha") .. string.format(" aura=%d", aura()))
          confere(visto.forma, "round 2 comeca com a forma (var20 > 0)")
          confere(visto.corpo and v(37) == 1 and v(57) == 1, "round 2 com o corpo endiabrado (RemapSprite ligado, var37 = 1)")
          confere(visto.aura, "round 2 com a aura do endiabrado viva")
          confere(visto.ctrl, "round 2 o lutador ganha ctrl (nao trava)")
          confere(visto.anda, "round 2 solta o chute fraco (estado " .. st_chute .. ")")
          confere(visto.soco, "round 2 solta o soco fraco (estado " .. st_soco .. ")")
          log(falhas == 0 and "RESULTADO OK" or ("RESULTADO " .. falhas .. " FALHA(S)"))
          log("FIM"); marca("fim"); rodada = 9
        end
      end
    end)
    if not ok then log("ERRO NO ROBO: " .. tostring(err)) end
  end)
  hook.add("loop", "rounds_r2", function()
    -- troca de round: o nocaute aconteceu e o motor voltou para a apresentação
    if rodada == 1 and fase == "nocaute" and roundState() < 2 then
      rodada = 2; t2 = 0; fase = "apresentacao"; log("ROUND 2 (apresentacao)")
    end
  end)
  pcall(function() setAccel(ACCEL) end)
  log("robo dos rounds carregado")
end
'''

# contador do RemapSprite (só na cópia de teste): +1 quando liga o endiabrado, -1 quando volta ao normal
REMAP = re.compile(r"(?ms)^(\[State -2, [^\]]*\]\ntype = RemapSprite\n)(.*?)(?=^\[|\Z)")


def contar_remap(cns):
    txt = cns.read_text(encoding="utf-8")

    def troca(m):
        cab, corpo = m.group(1), m.group(2)
        trig = re.findall(r"(?m)^(trigger\w+\s*=.*)$", corpo)
        valor = -1 if re.search(r"(?m)^reset\s*=\s*1", corpo) else 1
        extra = "[State -2, Teste: conta RemapSprite]\ntype = VarSet\n" + "\n".join(trig) + \
            f"\nvar(57) = {'0' if valor < 0 else '1'}\n\n"
        return cab + corpo + extra
    novo, n = REMAP.subn(troca, txt)
    if re.search(r"var\(57\)", txt):
        raise SystemExit(f"{cns}: var(57) já usado; escolha outra para o teste")
    cns.write_text(novo, encoding="utf-8", newline="\n")
    return n


def chars_do_commit(ref, nomes, destino):
    """Extrai chars/<nome> do commit ref (git archive), para o vídeo 'antes'."""
    for nome in nomes:
        dst = destino / nome
        dst.mkdir(parents=True, exist_ok=True)
        tar = subprocess.run(["git", "-C", str(RAIZ), "archive", ref, f"chars/{nome}"], capture_output=True, check=True)
        subprocess.run(["tar", "-x", "--strip-components=2", "-C", str(dst)], input=tar.stdout, check=True)
    return destino


def rodar(lutador, video=None, antes=None):
    motor = tp.motor_linux()
    tmp = Path(tempfile.mkdtemp(prefix="teste_rounds_"))
    try:
        origem = chars_do_commit(antes, {lutador, "hazaki"}, tmp / "antes") if antes else RAIZ / "chars"
        copia = tmp / "motor"
        shutil.copytree(motor, copia, symlinks=True)
        for nome in {lutador, "hazaki"}:
            shutil.copytree(origem / nome, copia / "chars" / nome, dirs_exist_ok=True)
        shutil.copytree(RAIZ / "motif" / "nazafight", copia / "data" / "nazafight", dirs_exist_ok=True)
        tp.INI_LINUX["Motif"] = "data/nazafight/system.def"
        n = contar_remap(copia / "chars" / lutador / f"{lutador}.cns")
        cmd = copia / "chars" / lutador / f"{lutador}.cmd"
        shutil.copy2(origem / lutador / f"{lutador}.cmd", cmd)
        tp.injetar(cmd, lutador == "hazaki")
        saida = tmp / "rounds.txt"
        debug = copia / "external/script/debug.lua"
        debug.write_text((motor / "external/script/debug.lua").read_text(encoding="utf-8") + "\n" +
                         LUA.replace("@SAIDA@", saida.as_posix()).replace("@ACCEL@", "1" if video else "4"),
                         encoding="utf-8")
        if video:
            tp.INI_LINUX["VSync"] = "1"
        tp.ajustar_ini(copia)
        disp = f":{70 + os.getpid() % 20}"
        xvfb = subprocess.Popen(["Xvfb", disp, "-screen", "0", "1280x720x24"], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(2)
        amb = {**tp.ambiente_linux(copia), "DISPLAY": disp}
        proc = subprocess.Popen(["./Ikemen_GO_Linux", "-p1", lutador, "-p2", "hazaki", "-s", "stages/stage0-720.def",
                                 "-rounds", "2"], cwd=copia, env=amb, stdout=open(tmp / "motor_log.txt", "w"),
                                stderr=subprocess.STDOUT, start_new_session=True)
        grav = None
        if video:
            video.mkdir(parents=True, exist_ok=True)
            mp4 = video / f"{lutador}_{'antes' if antes else 'depois'}.mp4"
            grav = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "x11grab", "-framerate", "30",
                                     "-video_size", "1280x720", "-i", disp, "-t", "150", "-c:v", "libx264",
                                     "-pix_fmt", "yuv420p", "-crf", "23", str(mp4)], env=amb, stdin=subprocess.PIPE)
        limite = time.time() + 900
        while time.time() < limite and proc.poll() is None:
            if saida.exists() and re.search(r"^FIM|ERRO NO ROBO", saida.read_text(encoding="utf-8"), re.M):
                break
            time.sleep(1)
        if grav:
            time.sleep(1)
            grav.communicate(b"q", timeout=30)
        try:
            os.killpg(proc.pid, 9)
        except ProcessLookupError:
            pass
        xvfb.kill()
        txt = saida.read_text(encoding="utf-8") if saida.exists() else "sem saída\n" + \
            (tmp / "motor_log.txt").read_text(errors="replace")[-2000:]
        return f"({n} RemapSprite contados)\n" + txt
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    args = sys.argv[1:]
    video = antes = None
    if "--video" in args:
        i = args.index("--video"); video = Path(args[i + 1]).resolve(); del args[i:i + 2]
    if "--antes" in args:
        i = args.index("--antes"); antes = args[i + 1]; del args[i:i + 2]
    falhou = []
    for lutador in args or LUTADORES:
        print(f"===== {lutador} =====", flush=True)
        txt = rodar(lutador, video, antes)
        print(txt, flush=True)
        if "RESULTADO OK" not in txt:
            falhou.append(lutador)
    print("\nTUDO OK" if not falhou else f"\nFALHOU: {', '.join(falhou)}")
    sys.exit(1 if falhou else 0)


if __name__ == "__main__":
    main()
