#!/usr/bin/env python3
"""Roda o IKEMEN dentro do Windows Sandbox e traz o resultado de volta (base do robô e da conferência do layout).

Regra do dono (2026-11-10): testes, robô e validação do motor rodam só na sandbox, nunca na máquina local.

  python ferramentas/sandbox.py --lutadores pengaro,hazaki --args "-p1 pengaro -p2 hazaki -s stages/stage0-720.def"
                                [--por-cima PASTA] [--ini Chave=valor ...] [--fim-arquivo resultado.txt]
                                [--fim-regex "^FIM"] [--espera 1800] [--saida PASTA]

Como funciona: monta um .wsb sem rede e sem placa de vídeo (vGPU desligada, OpenGL por software com o opengl32.dll do
Mesa llvmpipe), mapeia somente leitura o motor (%USERPROFILE%/JogoDeLuta/ikemen), o repositório e o Mesa, e com
escrita só a pasta de saída (C:/nf/saida lá dentro). Lá dentro copia o motor para C:/jogo, instala os lutadores de
chars/ e os cenários de stages/ (se a pasta existir no repositório), aplica a pasta --por-cima (arquivos que
substituem os do motor: debug.lua, .cmd injetado, data/nazafight...),
zera o volume, aplica os --ini, abre o Ikemen_GO.exe com --args e espera: o motor sair, o --fim-arquivo da saída casar
com --fim-regex, ou o tempo acabar. Depois copia save/logs para a saída, mata o motor e desliga a sandbox.

Uso como módulo: rodar(lutadores=[...], args=[...], saida=Path, por_cima=Path|None, ini={...}, fim_arquivo=...,
fim_regex=..., espera=...). Devolve True se a sandbox terminou sozinha (pronto.txt). Só cabe uma sandbox por vez.
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

RAIZ = Path(__file__).resolve().parent.parent
CASA = Path(os.environ["USERPROFILE"]) / "JogoDeLuta"
MOTOR = CASA / "ikemen"
MESA = CASA / "ferramentas_sandbox" / "mesa"
SANDBOX_EXE = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsSandbox.exe"
# WindowsSandboxServer.exe fica rodando sempre (serviço), mesmo sem sandbox aberta: não entra na lista.
PROCESSOS = ["WindowsSandbox.exe", "WindowsSandboxClient.exe", "WindowsSandboxRemoteSession.exe"]
INI_PADRAO = {"MasterVolume": "0", "PauseMasterVolume": "0", "Fullscreen": "0", "VSync": "0"}

PS1 = r"""$ErrorActionPreference = 'Continue'
Start-Transcript -Path 'C:\nf\saida\log_sandbox.txt' -Force | Out-Null
try {
  $jogo = 'C:\jogo'
  robocopy 'C:\nf\motor' $jogo /E /NFL /NDL /NJH /NJS /NP | Out-Null
  foreach ($c in @(@LUTADORES@)) { robocopy "C:\nf\repo\chars\$c" "$jogo\chars\$c" /E /NFL /NDL /NJH /NJS /NP | Out-Null }
  if (Test-Path 'C:\nf\repo\stages') { robocopy 'C:\nf\repo\stages' "$jogo\stages" /E /NFL /NDL /NJH /NJS /NP | Out-Null }
  if (Test-Path 'C:\nf\trabalho\por_cima') { robocopy 'C:\nf\trabalho\por_cima' $jogo /E /NFL /NDL /NJH /NJS /NP | Out-Null }
  Copy-Item 'C:\nf\mesa\opengl32.dll','C:\nf\mesa\libgallium_wgl.dll' $jogo
  $ini = "$jogo\save\config.ini"
  $t = Get-Content $ini -Raw
  foreach ($par in @(@INI@)) {
    $t = [regex]::Replace($t, '(?m)^(' + $par[0] + '\s*=\s*)[^\r\n]*', '${1}' + $par[1])
  }
  Set-Content -Path $ini -Value $t -NoNewline -Encoding UTF8
  $env:GALLIUM_DRIVER = 'llvmpipe'
  Write-Output ("inicio do motor: " + (Get-Date -Format o))
  # -ArgumentList '' falha no Start-Process: so passa quando houver argumentos.
  $extra = @{}
  if ('@ARGS@' -ne '') { $extra['ArgumentList'] = '@ARGS@' }
  $p = Start-Process -FilePath "$jogo\Ikemen_GO.exe" @extra -WorkingDirectory $jogo -PassThru `
       -RedirectStandardOutput 'C:\nf\saida\motor_stdout.txt' -RedirectStandardError 'C:\nf\saida\motor_stderr.txt'
  $limite = (Get-Date).AddSeconds(@ESPERA@)
  $fim = 'C:\nf\saida\@FIM_ARQUIVO@'
  $motivo = 'tempo esgotado'
  while ((Get-Date) -lt $limite) {
    if ($p.HasExited) { $motivo = "motor saiu (codigo $($p.ExitCode))"; break }
    if ('@FIM_REGEX@' -ne '' -and (Test-Path $fim) -and (Select-String -Path $fim -Pattern '@FIM_REGEX@' -Quiet)) {
      $motivo = 'fim encontrado'; break
    }
    Start-Sleep -Seconds 1
  }
  Write-Output ("parou: $motivo em " + (Get-Date -Format o))
  Start-Sleep -Seconds 2
  if (-not $p.HasExited) { $p.Kill() }
  New-Item -ItemType Directory -Force 'C:\nf\saida\logs' | Out-Null
  Copy-Item "$jogo\save\logs\*" 'C:\nf\saida\logs\' -ErrorAction SilentlyContinue
} catch { Write-Output "ERRO: $_" }
Stop-Transcript | Out-Null
Set-Content 'C:\nf\saida\pronto.txt' 'pronto'
Stop-Computer -Force
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


def wsb_xml(pastas, logon):
    m = "".join(f"    <MappedFolder><HostFolder>{h}</HostFolder><SandboxFolder>{s}</SandboxFolder>"
                f"<ReadOnly>{'true' if ro else 'false'}</ReadOnly></MappedFolder>\n" for h, s, ro in pastas)
    return ("<Configuration>\n  <vGPU>Disable</vGPU>\n  <Networking>Disable</Networking>\n"
            "  <AudioInput>Disable</AudioInput>\n  <VideoInput>Disable</VideoInput>\n"
            "  <ClipboardRedirection>Disable</ClipboardRedirection>\n  <PrinterRedirection>Disable</PrinterRedirection>\n"
            "  <ProtectedClient>Disable</ProtectedClient>\n  <MemoryInMB>4096</MemoryInMB>\n"
            f"  <MappedFolders>\n{m}  </MappedFolders>\n"
            f"  <LogonCommand><Command>{logon}</Command></LogonCommand>\n</Configuration>\n")


def esperar_vez(limite=3 * 3600):
    """Só cabe uma sandbox: espera a trava e a sandbox aberta por outro (ex.: filmar_sandbox.py) fecharem."""
    trava = CASA / "sandbox.trava"
    t0, avisou = time.time(), False
    while time.time() - t0 < limite:
        if trava.exists() and time.time() - trava.stat().st_mtime > 4 * 3600:
            trava.unlink(missing_ok=True)  # trava esquecida por um processo que morreu
        if not sandbox_rodando():
            try:
                os.close(os.open(trava, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
                if not sandbox_rodando():
                    return trava
                trava.unlink(missing_ok=True)
            except FileExistsError:
                pass
        if not avisou:
            print("a sandbox está ocupada; esperando a vez...", flush=True)
            avisou = True
        time.sleep(20)
    sys.exit("a sandbox ficou ocupada por 3 h; nada rodou")


def _ps_str(s):
    return str(s).replace("'", "''")


def rodar(lutadores, args, saida, por_cima=None, ini=None, fim_arquivo="resultado.txt", fim_regex="", espera=1800):
    for p, nome in ((SANDBOX_EXE, "WindowsSandbox.exe"), (MOTOR / "Ikemen_GO.exe", "motor"),
                    (MESA / "opengl32.dll", "Mesa (opengl32.dll)")):
        if not p.exists():
            sys.exit(f"falta {nome}: {p}")
    for c in lutadores:
        if not (RAIZ / "chars" / c).is_dir():
            sys.exit(f"lutador {c} não existe em chars/")
    trava = esperar_vez()
    saida = Path(saida).resolve()
    saida.mkdir(parents=True, exist_ok=True)
    for velho in ("pronto.txt", "log_sandbox.txt", fim_arquivo):
        (saida / velho).unlink(missing_ok=True)
    trab = Path(tempfile.mkdtemp(prefix="nf_sandbox_"))
    try:
        if por_cima:
            shutil.copytree(por_cima, trab / "por_cima")
        pares = {**INI_PADRAO, **(ini or {})}
        ini_ps = ",".join(f"@('{_ps_str(re.escape(k))}','{_ps_str(v)}')" for k, v in pares.items())
        ps1 = (PS1.replace("@LUTADORES@", ",".join(f"'{c}'" for c in dict.fromkeys(lutadores)))
               .replace("@INI@", ini_ps).replace("@ARGS@", _ps_str(" ".join(args)))
               .replace("@ESPERA@", str(int(espera))).replace("@FIM_ARQUIVO@", _ps_str(fim_arquivo))
               .replace("@FIM_REGEX@", _ps_str(fim_regex)))
        (trab / "rodar.ps1").write_text(ps1, encoding="utf-8-sig")
        pastas = [(MOTOR, r"C:\nf\motor", True), (RAIZ, r"C:\nf\repo", True), (MESA, r"C:\nf\mesa", True),
                  (trab, r"C:\nf\trabalho", True), (saida, r"C:\nf\saida", False)]
        wsb = trab / "rodar.wsb"
        wsb.write_text(wsb_xml(pastas, r"powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\nf\trabalho\rodar.ps1"),
                       encoding="utf-8")
        print(f"abrindo a Windows Sandbox (sem rede, sem vGPU); saída em {saida}", flush=True)
        t0 = time.time()
        subprocess.Popen([str(SANDBOX_EXE), str(wsb)])
        # margem para o boot da sandbox e a cópia do motor antes do relógio do rodar.ps1 começar
        while time.time() - t0 < espera + 300 and not (saida / "pronto.txt").exists():
            time.sleep(2)
        pronto = (saida / "pronto.txt").exists()
        time.sleep(3)
        fechar_sandbox()
        print(f"sandbox {'terminou' if pronto else 'NÃO terminou'} em {time.time() - t0:.0f} s", flush=True)
        return pronto
    finally:
        shutil.rmtree(trab, ignore_errors=True)
        trava.unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lutadores", default="pengaro,hazaki")
    ap.add_argument("--args", required=True, help="linha de comando do Ikemen_GO.exe")
    ap.add_argument("--por-cima", type=Path)
    ap.add_argument("--ini", nargs="*", default=[], help="Chave=valor aplicados no save/config.ini da cópia")
    ap.add_argument("--fim-arquivo", default="resultado.txt")
    ap.add_argument("--fim-regex", default="")
    ap.add_argument("--espera", type=float, default=600)
    ap.add_argument("--saida", type=Path, default=CASA / "sandbox_saida")
    a = ap.parse_args()
    ini = dict(kv.split("=", 1) for kv in a.ini)
    ok = rodar(a.lutadores.split(","), a.args.split(), a.saida, a.por_cima, ini, a.fim_arquivo, a.fim_regex, a.espera)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
