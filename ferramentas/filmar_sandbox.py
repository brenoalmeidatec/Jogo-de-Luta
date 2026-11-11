#!/usr/bin/env python3
"""Filma uma luta curta DENTRO do Windows Sandbox, a 60 fps, sem fotografar a tela do dono.

  python ferramentas/filmar_sandbox.py [--p1 pengaro] [--p2 hazaki] [--segundos 10] [--despertar N]
                                       [--golpes "x,y,holddown+a,garrafa_x"] [--roteiro arquivo.lua] [--saida PASTA]

Por que a sandbox: filmar_luta.py fotografa a área da tela do PC e já pegou a tela de bloqueio e janelas pessoais.
Aqui o jogo roda numa Windows Sandbox descartável (sem rede, sem placa de vídeo: vGPU desligada e OpenGL por software
com o opengl32.dll do Mesa llvmpipe) e o ffmpeg gdigrab grava o desktop DA SANDBOX, onde só existe o jogo.

O que é mapeado (tudo somente leitura, menos a saída): o motor (%USERPROFILE%/JogoDeLuta/ikemen), o repositório
(para copiar chars/), o Mesa (%USERPROFILE%/JogoDeLuta/ferramentas_sandbox/mesa), a pasta do ffmpeg do host e uma
pasta de trabalho com o rodar.ps1 e os .cmd já preparados. Lá dentro o rodar.ps1 copia o motor para C:/jogo, instala
os lutadores, zera o volume, abre a luta em janela 1280x720 e, no início do round, põe o jogo a 1/--lenta e grava
N segundos de jogo (gdigrab a 60/LENTA fps, retimado para 60 fps: na sandbox o gdigrab não passa de ~31 fps reais).
Depois desliga a sandbox. Saída: luta.mp4, log_sandbox.txt e os logs do motor em --saida (padrão:
%USERPROFILE%/JogoDeLuta/filmagens/P1_x_P2_DATA).

--golpes: o P1 fica sem IA, se posiciona a --distancia px (padrão 28) e solta os comandos do .cmd em volta; "+" junta
comandos apertados no mesmo tick (holddown+a). O P2 fica parado. Sem --golpes, os dois lutam na IA 8.
--despertar N: liga o Despertar do Pengaró aos N segundos de round (como filmar_luta.py).
--roteiro: um .lua a mais, anexado ao debug.lua da cópia (hook.add("loop", ...), como o robo.lua).
--cenario: o .def do cenário (padrão stages/stage0-720.def); a pasta stages/ do repositório é copiada para o motor.
--passeio: filme de cenário: os dois sem IA passeiam juntos até as duas pontas e sobem (ferramentas/robo/passeio.lua).
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CASA = Path(os.environ["USERPROFILE"]) / "JogoDeLuta"
MOTOR = CASA / "ikemen"
MESA = CASA / "ferramentas_sandbox" / "mesa"
SANDBOX_EXE = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsSandbox.exe"
# WindowsSandboxServer.exe fica rodando sempre (serviço), mesmo sem sandbox aberta: não entra na lista.
PROCESSOS = ["WindowsSandbox.exe", "WindowsSandboxClient.exe", "WindowsSandboxRemoteSession.exe"]

PS1 = r"""$ErrorActionPreference = 'Continue'
Start-Transcript -Path 'C:\nf\saida\log_sandbox.txt' -Force | Out-Null
try {
  $jogo = 'C:\jogo'
  robocopy 'C:\nf\motor' $jogo /E /NFL /NDL /NJH /NJS /NP | Out-Null
  foreach ($c in @(@LUTADORES@)) { robocopy "C:\nf\repo\chars\$c" "$jogo\chars\$c" /E /NFL /NDL /NJH /NJS /NP | Out-Null }
  if (Test-Path 'C:\nf\repo\stages') { robocopy 'C:\nf\repo\stages' "$jogo\stages" /E /NFL /NDL /NJH /NJS /NP | Out-Null }
  robocopy 'C:\nf\trabalho\por_cima' $jogo /E /NFL /NDL /NJH /NJS /NP | Out-Null
  Copy-Item 'C:\nf\mesa\opengl32.dll','C:\nf\mesa\libgallium_wgl.dll' $jogo
  $ini = "$jogo\save\config.ini"
  $t = Get-Content $ini -Raw
  foreach ($par in @(@('MasterVolume','0'),@('PauseMasterVolume','0'),@('Fullscreen','0'),@('VSync','0'),
                     @('Framerate','60'),@('TickInterpolation','0'),@('WindowCentered','1'))) {
    $t = [regex]::Replace($t, '(?m)^(' + $par[0] + '\s*=\s*)[^\r\n]*', '${1}' + $par[1])
  }
  Set-Content -Path $ini -Value $t -NoNewline -Encoding UTF8
  $env:GALLIUM_DRIVER = 'llvmpipe'
  # A sandbox herda a escala do host (125%): sem isto a janela vira 1600x900 esticada e o gdigrab recorta errado.
  $env:__COMPAT_LAYER = 'HighDpiAware'
  # ffmpeg local e já aberto uma vez: rodar do compartilhamento demora segundos e atrasaria o começo da gravação.
  robocopy 'C:\nf\ffmpeg' 'C:\ff' ffmpeg.exe /NFL /NDL /NJH /NJS /NP | Out-Null
  & 'C:\ff\ffmpeg.exe' -hide_banner -version | Select-Object -First 1
  Write-Output ("inicio do jogo: " + (Get-Date -Format o))
  $p = Start-Process -FilePath "$jogo\Ikemen_GO.exe" -ArgumentList '@ARGS@' -WorkingDirectory $jogo -PassThru `
       -RedirectStandardOutput 'C:\nf\saida\motor_stdout.txt' -RedirectStandardError 'C:\nf\saida\motor_stderr.txt'
  $limite = (Get-Date).AddSeconds(180)
  while (-not (Test-Path "$jogo\luta_comecou.txt") -and (Get-Date) -lt $limite -and -not $p.HasExited) { Start-Sleep -Milliseconds 100 }
  if (-not (Test-Path "$jogo\luta_comecou.txt")) { Write-Output "o round nao comecou (motor saiu: $($p.HasExited))" }
  else {
    Write-Output ("round comecou: " + (Get-Date -Format o))
    & 'C:\ff\ffmpeg.exe' -hide_banner -loglevel warning -y -f gdigrab -framerate @FPS_CAPTURA@ -draw_mouse 0 `
      -t @SEGUNDOS_REAIS@ -i 'title=@TITULO@' -vf 'setpts=(PTS-STARTPTS)/@LENTA@,fps=60' -c:v libx264 -preset ultrafast `
      -crf 16 -pix_fmt yuv420p 'C:\nf\saida\luta.mp4' 2>&1 | Out-String | Write-Output
    Write-Output "ffmpeg saiu com $LASTEXITCODE"
    Set-Content "$jogo\parar.txt" 'parar'
    $limite = (Get-Date).AddSeconds(10)
    while (-not (Test-Path 'C:\nf\saida\ticks.txt') -and (Get-Date) -lt $limite) { Start-Sleep -Milliseconds 50 }
  }
  if (-not $p.HasExited) { $p.Kill() }
  Copy-Item "$jogo\save\logs\*" 'C:\nf\saida\' -ErrorAction SilentlyContinue
} catch { Write-Output "ERRO: $_" }
Stop-Transcript | Out-Null
Set-Content 'C:\nf\saida\pronto.txt' 'pronto'
Stop-Computer -Force
"""

MARCA = """
-- FILME NA SANDBOX: no inicio do round poe o jogo em camera lenta (1/@LENTA@) e avisa o rodar.ps1 para gravar; conta
-- os ticks ate o rodar.ps1 pedir para parar e grava a conta em ticks.txt (prova de que o video cobre o tempo pedido).
do
  local fase, ticks = "espera", 0
  hook.add("loop", "marca_luta", function()
    if fase == "espera" and roundState() == 2 then
      fase = "grava"
      setAccel(1 / @LENTA@)
      local f = io.open("C:/jogo/luta_comecou.txt", "w")
      if f then f:write("ok"); f:close() end
    elseif fase == "grava" then
      ticks = ticks + 1
      local p = io.open("C:/jogo/parar.txt", "r")
      if p then
        p:close(); fase = "fim"
        local f = io.open("C:/nf/saida/ticks.txt", "w")
        if f then f:write(ticks .. " ticks de jogo durante a gravacao"); f:close() end
      end
    end
  end)
end
"""


def sandbox_rodando():
    out = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True, errors="replace").stdout
    return [p for p in PROCESSOS if f'"{p.lower()}"' in out.lower()]


def fechar_sandbox():
    try:  # wsb.exe (Windows 11 24H2+) fecha pela id; taskkill fica de reserva
        ids = re.findall(r"[0-9a-fA-F]{8}-[0-9a-fA-F-]{27}",
                         subprocess.run(["wsb", "list"], capture_output=True, text=True, timeout=30).stdout)
        for i in ids:
            subprocess.run(["wsb", "stop", "--id", i], capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        pass
    for _ in range(30):
        if not sandbox_rodando():
            return
        time.sleep(1)
    for p in PROCESSOS:
        subprocess.run(["taskkill", "/F", "/IM", p], capture_output=True)


def titulo_da_janela():
    m = re.search(r"^WindowTitle\s*=\s*(.+?)\s*$", (MOTOR / "save/config.ini").read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else "Ikemen GO"


def comandos_do_cmd(txt):
    return set(re.findall(r'^\s*name\s*=\s*"([^"]+)"', txt, re.M))


def preparar_cmd(origem, destino, nomes_golpes, despertar):
    txt = origem.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "[Statedef -1]\n\n" in txt, f"sem [Statedef -1] em {origem}"
    b = ""
    if nomes_golpes:
        faltam = sorted(set(nomes_golpes) - comandos_do_cmd(txt))
        if faltam:
            sys.exit(f"comandos que não existem em {origem.name}: {', '.join(faltam)}")
        for c in sorted(set(nomes_golpes)):
            b += f'[State -1, F_{c}]\ntype = AssertCommand\ntrigger1 = map(t_{c}) = 1\nname = "{c}"\nbuffer.time = 1\n\n'
        b += '[State -1, F_pos]\ntype = PosSet\ntrigger1 = map(t_pos) = 1\nx = map(t_posx) - 1000\n\n'
    if despertar is not None:
        # var(50) não é usada pelo Pengaró: marca que a ativação do filme já aconteceu, para não religar.
        quando = (f"triggerall = roundstate = 2 && var(50) = 0 && var(20) = 0\n"
                  f"trigger1 = gametime >= {int(despertar * 60)} && statetype = S && ctrl\n")
        b += ("[State -1, Filme marca o Despertar feito]\ntype = VarSet\ntrigger1 = stateno = 2000\nvar(50) = 1\n\n"
              f"[State -1, Filme enche a barra]\ntype = PowerSet\n{quando}value = powermax\n\n"
              f"[State -1, Filme ativa o Despertar]\ntype = ChangeState\n{quando}value = 2000\n\n")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(txt.replace("[Statedef -1]\n\n", "[Statedef -1]\n\n" + b, 1), encoding="utf-8", newline="\n")


def injetar_passeio(arquivo):
    """PosAdd comandado por map (c_dx no mundo, c_dy na vertical) no [Statedef -1], para o passeio.lua."""
    txt = arquivo.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "[Statedef -1]\n\n" in txt, f"sem [Statedef -1] em {arquivo}"
    b = ("[State -1, F_passeio]\ntype = PosAdd\ntrigger1 = map(c_dx) != 0 || map(c_dy) != 0\n"
         "x = map(c_dx) * facing\ny = map(c_dy)\n\n")
    arquivo.write_text(txt.replace("[Statedef -1]\n\n", "[Statedef -1]\n\n" + b, 1), encoding="utf-8", newline="\n")


def wsb_xml(pastas, logon):
    m = "".join(f"    <MappedFolder><HostFolder>{h}</HostFolder><SandboxFolder>{s}</SandboxFolder>"
                f"<ReadOnly>{'true' if ro else 'false'}</ReadOnly></MappedFolder>\n" for h, s, ro in pastas)
    return ("<Configuration>\n  <vGPU>Disable</vGPU>\n  <Networking>Disable</Networking>\n"
            "  <AudioInput>Disable</AudioInput>\n  <VideoInput>Disable</VideoInput>\n"
            "  <ClipboardRedirection>Disable</ClipboardRedirection>\n  <PrinterRedirection>Disable</PrinterRedirection>\n"
            "  <ProtectedClient>Disable</ProtectedClient>\n  <MemoryInMB>4096</MemoryInMB>\n"
            f"  <MappedFolders>\n{m}  </MappedFolders>\n"
            f"  <LogonCommand><Command>{logon}</Command></LogonCommand>\n</Configuration>\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--p1", default="pengaro")
    ap.add_argument("--p2", default="hazaki")
    ap.add_argument("--segundos", type=float, default=10)
    ap.add_argument("--despertar", type=float)
    ap.add_argument("--golpes", help='comandos do .cmd do P1 separados por vírgula; "+" junta no mesmo tick')
    ap.add_argument("--distancia", type=int, default=28)
    ap.add_argument("--roteiro", type=Path, help="Lua extra anexado ao debug.lua")
    ap.add_argument("--saida", type=Path)
    ap.add_argument("--lenta", type=int, default=4,
                    help="o jogo roda a 1/LENTA da velocidade e o gdigrab grava a 60/LENTA fps (padrão 4)")
    ap.add_argument("--espera", type=float, default=900, help="segundos máximos esperando o vídeo")
    ap.add_argument("--cenario", default="stages/stage0-720.def", help="cenário da luta (.def dentro do motor)")
    ap.add_argument("--passeio", action="store_true", help="filme de cenário: os dois sem IA passeiam pelas pontas")
    a = ap.parse_args()
    if not 5 <= a.segundos <= 10:
        print(f"aviso: --segundos {a.segundos} fora da faixa recomendada de 5 a 10")
    for p, nome in ((SANDBOX_EXE, "WindowsSandbox.exe"), (MOTOR / "Ikemen_GO.exe", "motor"),
                    (MESA / "opengl32.dll", "Mesa (opengl32.dll)")):
        if not p.exists():
            sys.exit(f"falta {nome}: {p}")
    for c in (a.p1, a.p2):
        if not (RAIZ / "chars" / c).is_dir():
            sys.exit(f"lutador {c} não existe em chars/")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        sys.exit("ffmpeg não está no PATH do host")
    if sandbox_rodando():
        sys.exit("já existe uma Windows Sandbox aberta (só cabe uma): feche-a e rode de novo")

    saida = (a.saida or CASA / "filmagens" / f"{a.p1}_x_{a.p2}_{datetime.now():%Y%m%d_%H%M%S}").resolve()
    saida.mkdir(parents=True, exist_ok=True)
    for velho in ("luta.mp4", "pronto.txt", "log_sandbox.txt", "ticks.txt"):
        (saida / velho).unlink(missing_ok=True)
    trab = Path(tempfile.mkdtemp(prefix="filme_sandbox_"))
    try:
        golpes = [[n.strip() for n in g.split("+") if n.strip()] for g in (a.golpes or "").split(",") if g.strip()]
        nomes = [n for g in golpes for n in g]
        por_cima = trab / "por_cima"
        preparar_cmd(RAIZ / "chars" / a.p1 / f"{a.p1}.cmd", por_cima / "chars" / a.p1 / f"{a.p1}.cmd", nomes, a.despertar)
        lua = (MOTOR / "external/script/debug.lua").read_text(encoding="utf-8") + "\n" + MARCA.replace("@LENTA@", str(a.lenta))
        if golpes:
            lista = ", ".join("{" + ", ".join(f'"{n}"' for n in g) + "}" for g in golpes)
            lua += "\n" + (RAIZ / "ferramentas/robo/golpes.lua").read_text(encoding="utf-8") \
                .replace("{@GOLPES@}", "{" + lista + "}").replace("= @DIST@", f"= {a.distancia}")
        if a.roteiro:
            lua += "\n" + a.roteiro.read_text(encoding="utf-8")
        if a.passeio:
            for c in dict.fromkeys((a.p1, a.p2)):
                alvo = por_cima / "chars" / c / f"{c}.cmd"
                if not alvo.exists():
                    alvo.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(RAIZ / "chars" / c / f"{c}.cmd", alvo)
                injetar_passeio(alvo)
            lua += "\n" + (RAIZ / "ferramentas/robo/passeio.lua").read_text(encoding="utf-8")
        (por_cima / "external/script").mkdir(parents=True)
        (por_cima / "external/script/debug.lua").write_text(lua, encoding="utf-8")
        args = ["-p1", a.p1, "-p2", a.p2, "-s", a.cenario, "-rounds", "1"]
        if not golpes and not a.passeio:
            args[2:2] = ["-p1.ai", "8"]
            args += ["-p2.ai", "8"]
        lutadores = ",".join(f"'{c}'" for c in dict.fromkeys((a.p1, a.p2)))
        ps1 = (PS1.replace("@LUTADORES@", lutadores).replace("@ARGS@", " ".join(args))
               .replace("@SEGUNDOS_REAIS@", f"{a.segundos * a.lenta:g}").replace("@LENTA@", str(a.lenta))
               .replace("@FPS_CAPTURA@", f"{60 / a.lenta:g}").replace("@TITULO@", titulo_da_janela()))
        (trab / "rodar.ps1").write_text(ps1, encoding="utf-8-sig")
        pastas = [(MOTOR, r"C:\nf\motor", True), (RAIZ, r"C:\nf\repo", True), (MESA, r"C:\nf\mesa", True),
                  (Path(ffmpeg).parent, r"C:\nf\ffmpeg", True), (trab, r"C:\nf\trabalho", True),
                  (saida, r"C:\nf\saida", False)]
        wsb = trab / "filme.wsb"
        wsb.write_text(wsb_xml(pastas, r"powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\nf\trabalho\rodar.ps1"),
                       encoding="utf-8")
        shutil.copy2(wsb, saida / "filme.wsb")  # fica junto do vídeo para conferir o que a sandbox recebeu
        print(f"abrindo a Windows Sandbox (sem rede, sem vGPU); saída em {saida}")
        t0 = time.time()
        subprocess.Popen([str(SANDBOX_EXE), str(wsb)])
        while time.time() - t0 < a.espera and not (saida / "pronto.txt").exists():
            time.sleep(2)
        pronto = (saida / "pronto.txt").exists()
        time.sleep(3)
        fechar_sandbox()
        video = saida / "luta.mp4"
        if not pronto:
            sys.exit(f"a sandbox não terminou em {a.espera:g} s; veja {saida / 'log_sandbox.txt'}")
        if not video.exists() or video.stat().st_size == 0:
            sys.exit(f"sem vídeo; veja {saida / 'log_sandbox.txt'}")
        info = subprocess.run([str(Path(ffmpeg).with_name("ffprobe.exe")), "-v", "error", "-select_streams", "v:0",
                               "-show_entries", "stream=width,height,r_frame_rate,nb_frames:format=duration",
                               "-of", "default=nw=1", str(video)], capture_output=True, text=True).stdout
        ticks = (saida / "ticks.txt").read_text(encoding="utf-8").strip() if (saida / "ticks.txt").exists() else "?"
        print(f"vídeo: {video} ({time.time() - t0:.0f} s no total; {ticks}, esperado ~{a.segundos * 60:g})\n{info.strip()}")
    finally:
        shutil.rmtree(trab, ignore_errors=True)


if __name__ == "__main__":
    main()
