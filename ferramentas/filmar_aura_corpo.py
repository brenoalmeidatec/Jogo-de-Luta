#!/usr/bin/env python3
"""Filma o lutador endiabrado passando por todo tipo de estado e guarda, tique a tique, onde cada camada da aura está.

  python3 ferramentas/filmar_aura_corpo.py hazaki --saida PASTA            (filme em tempo real: luta.mp4 + aura_log.txt)
  python3 ferramentas/filmar_aura_corpo.py hazaki --saida PASTA --sem-filme (só o log, o mais rápido que der: o robô)

Issue #51, item 1 (as auras e asas têm de seguir o corpo). Roda no Linux sem tela (Xvfb + Mesa), com a cópia do IKEMEN
GO do robô (~/.cache/nazafight/ikemen). Só na cópia, o .cmd dos dois lutadores ganha controladores que um roteiro Lua
aciona por map, e o .cns ganha dois golpes de teste (7790 derruba, 7791 só encosta). O jogo e chars/ não são tocados.

Roteiro do P1 (endiabrado o tempo todo), em tiques do round:
  parado, agachado, pulo, anda para a frente e para trás, corre, leva golpe em pé, solta três golpes, é derrubado
  (voa, cai, fica no chão, levanta), é agarrado e arremessado pelo P2, defende, e vence (pose de vitória).
O aura_log.txt traz por tique: estado, ação, elemento, posição e lado do P1, os maps da âncora (ax, ay, g) e, de cada
camada, a posição e a escala lidas do motor. Quem confere é o ferramentas/aura_no_corpo.py --conferir PASTA.
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

FIM = 1120  # tiques de round do roteiro

# (de, até, o quê): o que o roteiro manda em cada janela. O nome da fase vai para o log.
FASES = [(1, 40, "parado"), (40, 110, "agachado"), (110, 190, "pulo"), (190, 240, "anda_frente"),
         (240, 290, "anda_tras"), (290, 345, "corre"), (345, 395, "golpe_em_pe"), (395, 465, "golpes"),
         (465, 650, "derrubado"), (650, 900, "agarrado"), (900, 960, "defende"), (960, FIM, "vitoria")]

LUA = """
-- ROTEIRO DO FILME DA AURA NO CORPO (so na copia do motor)
do
  local t, rn = 0, 0
  local log = io.open("@SAIDA@", "w")
  local CAM = {@CAMADAS@}
  local NOME = "@NOME@"
  local FASES = {@FASES@}
  local function com(n, fn)
    local old = id()
    if player(n) then fn() end
    playerId(old)
  end
  local function v(x) if x == nil then return "-" end return string.format("%.2f", x) end
  local function entre(a, b) return t >= a and t < b end
  hook.add("loop", "aura_corpo", function()
    local ok, err = pcall(function()
      if log == nil then return end
      if roundState() ~= 2 and t == 0 then return end
      t = t + 1
      local fase = "-"
      for _, f in ipairs(FASES) do if entre(f[1], f[2]) then fase = f[3] end end
      com(1, function()
        mapSet("f_desp", 1)
        mapSet("f_pos", 0); mapSet("f_estado", 0)
        mapSet("f_baixo", entre(40, 110) and 1 or 0)
        mapSet("f_frente", (entre(190, 240) or entre(290, 335)) and 1 or 0)
        mapSet("f_tras", (entre(240, 290) or entre(900, 960)) and 1 or 0)
        if t == 2 then mapSet("f_posx", -70); mapSet("f_pos", 1) end
        if t == 112 then mapSet("f_estado", 40) end
        if t == 292 then mapSet("f_estado", 100) end
        if t == 398 then mapSet("f_estado", 230) end
        if t == 422 then mapSet("f_estado", 240) end
        if t == 446 then mapSet("f_estado", 210) end
        if t == 346 or t == 396 or t == 466 or t == 651 or t == 901 then mapSet("f_posx", -30); mapSet("f_pos", 1) end
      end)
      com(2, function()
        mapSet("f_desp", 0)
        mapSet("f_pos", 0); mapSet("f_estado", 0)
        mapSet("f_baixo", 0); mapSet("f_frente", 0); mapSet("f_tras", 0)
        if t == 2 then mapSet("f_posx", 140); mapSet("f_pos", 1) end
        if t == 346 or t == 466 or t == 901 then mapSet("f_posx", 14); mapSet("f_pos", 1) end
        if t == 396 then mapSet("f_posx", 140); mapSet("f_pos", 1) end
        if t == 651 then mapSet("f_posx", 4); mapSet("f_pos", 1) end
        if t == 356 or t == 910 or t == 930 then mapSet("f_estado", 7791) end
        if t == 476 then mapSet("f_estado", 7790) end
        if t == 656 then mapSet("f_estado", 800) end
        if t == 962 then setLife(0) end
      end)
      com(1, function()
        local linha = {string.format("p=%.1f t=%d fase=%s st=%d anim=%d el=%d x=%.2f y=%.2f tx=%.2f ty=%.2f cx=%.2f cy=%.2f f=%d ax=%.2f ay=%.2f g=%.3f th=%.1f", map("au_" .. NOME .. "_p"), t, fase,
          stateNo(), anim(), animElemNo(0), posX(), posY(), screenPosX(), screenPosY(), cameraPosX(), cameraPosY(), facing(), map("au_" .. NOME .. "_ax"),
          map("au_" .. NOME .. "_ay"), map("au_" .. NOME .. "_g"), map("au_" .. NOME .. "_th"))}
        for _, e in ipairs(CAM) do
          if numExplod(e) > 0 then
            linha[#linha + 1] = string.format("%d px=%s py=%s sx=%s sy=%s an=%s", e, v(explodVar(e, 0, "pos x")),
              v(explodVar(e, 0, "pos y")), v(explodVar(e, 0, "scale x")), v(explodVar(e, 0, "scale y")), v(explodVar(e, 0, "angle")))
          else
            linha[#linha + 1] = e .. " fora"
          end
        end
        log:write(table.concat(linha, " | "), "\\n")
        log:flush()
      end)
      if t >= @FIM@ then log:write("FIM\\n"); log:close(); log = nil end
    end)
    if not ok and log then log:write("ERRO " .. tostring(err) .. "\\n"); log:flush() end
  end)
end
"""

CMD = """[State -1, filme: Despertar ligado]
type = VarSet
trigger1 = map(f_desp) = 1 && RoundState = 2 && var(20) < 300
var(20) = 600
ignorehitpause = 1

[State -1, filme: baixo]
type = AssertCommand
trigger1 = map(f_baixo) = 1
name = "holddown"
buffer.time = 1

[State -1, filme: baixo (o motor lê a tecla, não o comando)]
type = AssertInput
trigger1 = map(f_baixo) = 1
flag = D

[State -1, filme: para a direita]
type = AssertInput
trigger1 = (map(f_frente) = 1 && Facing = 1) || (map(f_tras) = 1 && Facing = -1)
flag = R

[State -1, filme: para a esquerda]
type = AssertInput
trigger1 = (map(f_frente) = 1 && Facing = -1) || (map(f_tras) = 1 && Facing = 1)
flag = L

[State -1, filme: frente]
type = AssertCommand
trigger1 = map(f_frente) = 1
name = "holdfwd"
buffer.time = 1

[State -1, filme: tras]
type = AssertCommand
trigger1 = map(f_tras) = 1
name = "holdback"
buffer.time = 1

[State -1, filme: lugar]
type = PosSet
trigger1 = map(f_pos) = 1
x = map(f_posx)
y = 0

[State -1, filme: olha para o outro]
type = Turn
trigger1 = map(f_pos) = 1 && ifelse(map(f_posx) < 0, 1, -1) != Facing

[State -1, filme: estado]
type = ChangeState
trigger1 = map(f_estado) > 0 && ctrl && statetype != A
value = map(f_estado)

"""

GOLPES = """
; ---- golpes de teste do filme da aura (só na cópia do motor)
[Statedef 7790]
type = S
movetype = A
physics = S
anim = 200
ctrl = 0
velset = 0, 0

[State 7790, derruba]
type = HitDef
trigger1 = Time = 0
attr = S, NA
damage = 20
animtype = Back
hitflag = MAF
guardflag = MA
pausetime = 8, 8
sparkno = -1
ground.type = High
ground.slidetime = 14
ground.hittime = 16
ground.velocity = -3.5, -7.5
air.velocity = -3.5, -7.5
fall = 1

[State 7790, fim]
type = ChangeState
trigger1 = AnimTime = 0
value = 0
ctrl = 1

[Statedef 7791]
type = S
movetype = A
physics = S
anim = 200
ctrl = 0
velset = 0, 0

[State 7791, encosta]
type = HitDef
trigger1 = Time = 0
attr = S, NA
damage = 10
animtype = Medium
hitflag = MAF
guardflag = MA
pausetime = 8, 8
sparkno = -1
ground.type = High
ground.slidetime = 16
ground.hittime = 18
ground.velocity = -2
air.velocity = -2, -3

[State 7791, fim]
type = ChangeState
trigger1 = AnimTime = 0
value = 0
ctrl = 1

"""


def aura_do_cns(cns):
    """(nome, [ids das camadas]) da aura que o aura.py escreveu no [Statedef -4], ou (None, [])."""
    m = re.search(r"Aura animada '(\w+)' \(ferramentas/aura\.py\): (\d+) camadas, \d+ partículas, explods (\d+)", cns)
    if not m:
        return None, []
    return m.group(1), [int(m.group(3)) + k for k in range(int(m.group(2)))]


def injetar(pasta, nome):
    cmd = pasta / f"{nome}.cmd"
    txt = cmd.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "[Statedef -1]\n\n" in txt, f"sem Statedef -1 em {cmd}"
    cmd.write_text(txt.replace("[Statedef -1]\n\n", "[Statedef -1]\n\n" + CMD, 1), encoding="utf-8", newline="\n")
    cns = pasta / f"{nome}.cns"
    txt = cns.read_text(encoding="utf-8").replace("\r\n", "\n")
    i = txt.index("[Statedef -2]")
    cns.write_text(txt[:i] + GOLPES + txt[i:], encoding="utf-8", newline="\n")


def filmar(lutador, saida, filme=True, p2=None, cenario="stages/stage0-720.def", chars=None, espera=11):
    """Roda o roteiro e devolve o caminho do aura_log.txt. `chars` troca a pasta de onde o lutador vem (o antes)."""
    p2 = p2 or ("pengaro" if lutador == "hazaki" else "hazaki")
    saida.mkdir(parents=True, exist_ok=True)
    log_aura = saida / "aura_log.txt"
    log_aura.unlink(missing_ok=True)
    motor = motor_linux()
    with tempfile.TemporaryDirectory() as td:
        copia = Path(td) / "motor"
        shutil.copytree(motor, copia, symlinks=True)
        for nome in (lutador, p2):
            origem = (chars if chars and nome == lutador else RAIZ / "chars") / nome
            shutil.copytree(origem, copia / "chars" / nome, dirs_exist_ok=True)
            injetar(copia / "chars" / nome, nome)
        shutil.copytree(RAIZ / "motif" / "nazafight", copia / "data" / "nazafight", dirs_exist_ok=True)
        if (RAIZ / "stages").exists() and cenario.startswith("stages/"):
            shutil.copytree(RAIZ / "stages", copia / "stages", dirs_exist_ok=True)
        nome_aura, camadas = aura_do_cns((copia / "chars" / lutador / f"{lutador}.cns").read_text(encoding="utf-8"))
        lua = (LUA.replace("@SAIDA@", log_aura.as_posix()).replace("@CAMADAS@", ", ".join(map(str, camadas)))
               .replace("@NOME@", nome_aura or "x").replace("@FIM@", str(FIM))
               .replace("@FASES@", ", ".join(f'{{{a}, {b}, "{n}"}}' for a, b, n in FASES)))
        dbg = copia / "external/script/debug.lua"
        dbg.write_text(dbg.read_text(encoding="utf-8") + "\n" + lua, encoding="utf-8")
        ini = dict(INI_LINUX)
        INI_LINUX["Motif"] = "data/nazafight/system.def"
        INI_LINUX["VSync"] = "1" if filme else "0"
        ajustar_ini(copia)
        INI_LINUX.clear()
        INI_LINUX.update(ini)
        disp = f":{60 + os.getpid() % 19}"
        xvfb = subprocess.Popen(["Xvfb", disp, "-screen", "0", "1280x720x24"], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(2)
        amb = {**ambiente_linux(copia), "DISPLAY": disp}
        log = open(Path(td) / "jogo.log", "w")
        jogo = subprocess.Popen(["./Ikemen_GO_Linux", "-p1", lutador, "-p2", p2, "-s", cenario, "-rounds", "1"],
                                cwd=copia, env=amb, stdout=log, stderr=log, start_new_session=True)
        grava = None
        try:
            limite = time.time() + 240
            while time.time() < limite and not log_aura.exists() and jogo.poll() is None:
                time.sleep(0.05)   # o log nasce no primeiro tique de luta: o filme começa aí
            if filme:
                grava = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "x11grab", "-framerate", "30",
                                          "-video_size", "1280x720", "-i", disp, "-c:v", "libx264", "-pix_fmt",
                                          "yuv420p", "-crf", "20", str(saida / "luta.mp4")], env=amb,
                                         stdin=subprocess.PIPE)
            while time.time() < limite and jogo.poll() is None:
                if log_aura.exists() and re.search(r"^(FIM|ERRO)", log_aura.read_text(errors="replace"), re.M):
                    break
                time.sleep(0.5)
            if grava:
                time.sleep(1.5)
                grava.communicate(b"q", timeout=30)
        finally:
            try:
                os.killpg(jogo.pid, 9)
            except ProcessLookupError:
                pass
            xvfb.kill()
            log.close()
            for linha in [x for x in (Path(td) / "jogo.log").read_text(errors="replace").splitlines() if "rror" in x][:20]:
                print("motor:", linha)
    assert log_aura.exists(), "o roteiro não escreveu o aura_log.txt: o motor fechou antes da luta"
    return log_aura


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lutador")
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--sem-filme", action="store_true")
    ap.add_argument("--p2")
    ap.add_argument("--chars", type=Path, help="pasta chars/ de onde o lutador vem (para filmar o antes)")
    ap.add_argument("--cenario", default="stages/stage0-720.def")
    a = ap.parse_args()
    print(filmar(a.lutador, a.saida, filme=not a.sem_filme, p2=a.p2, chars=a.chars, cenario=a.cenario))


if __name__ == "__main__":
    main()
