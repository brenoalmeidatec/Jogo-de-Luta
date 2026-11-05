@echo off
title Jogo de Luta
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((Get-Content -LiteralPath '%~f0' -Raw) -split '#PS#START\r?\n',2)[1]"
exit /b
#PS#START
# Jogo de Luta: baixa a versao mais nova do GitHub e abre o jogo.
# Tudo fica em %LOCALAPPDATA%\JogoDeLuta (jogo + Godot). Nao mexe em nenhuma outra pasta.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$repo     = 'brenoalmeidatec/Jogo-de-Luta'
$branch   = 'claude/base-godot'   # branch com o jogo. Troque quando o PR for aceito.
$base     = Join-Path $env:LOCALAPPDATA 'JogoDeLuta'
$game     = Join-Path $base 'jogo'
$godotDir = Join-Path $base 'godot'
$godotExe = Join-Path $godotDir 'Godot_v4.3-stable_win64.exe'
New-Item -ItemType Directory -Force $base | Out-Null

function Fechar($msg) {
    Write-Host $msg -ForegroundColor Red
    Read-Host 'Aperte Enter para fechar'
    exit 1
}

# 1. Atualiza o jogo
try {
    Write-Host 'Baixando a versao mais nova do jogo no GitHub...'
    $zip = Join-Path $base 'jogo.zip'
    $tmp = Join-Path $base 'tmp'
    Invoke-WebRequest "https://github.com/$repo/archive/refs/heads/$branch.zip" -OutFile $zip -UseBasicParsing
    if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
    Expand-Archive $zip $tmp -Force
    $src = (Get-ChildItem $tmp -Directory | Select-Object -First 1).FullName
    robocopy $src $game /MIR /XD .godot /NFL /NDL /NJH /NJS /NP | Out-Null
    Remove-Item $tmp -Recurse -Force
    Remove-Item $zip -Force
    Write-Host 'Jogo atualizado!' -ForegroundColor Green
} catch {
    Write-Host "Nao consegui atualizar: $($_.Exception.Message)" -ForegroundColor Yellow
    if (-not (Test-Path (Join-Path $game 'project.godot'))) {
        Fechar 'Ainda nao tem nenhuma versao do jogo baixada. Confira a internet e tente de novo.'
    }
    Write-Host 'Abrindo a ultima versao que ja estava baixada.'
}

# 2. Baixa a Godot na primeira vez
if (-not (Test-Path $godotExe)) {
    try {
        Write-Host 'Baixando a Godot 4.3 (so na primeira vez, uns 60 MB)...'
        $gz = Join-Path $base 'godot.zip'
        Invoke-WebRequest 'https://github.com/godotengine/godot/releases/download/4.3-stable/Godot_v4.3-stable_win64.exe.zip' -OutFile $gz -UseBasicParsing
        Expand-Archive $gz $godotDir -Force
        Remove-Item $gz -Force
    } catch {
        Fechar "Nao consegui baixar a Godot: $($_.Exception.Message)"
    }
}

# 3. Prepara os arquivos novos e abre o jogo
Write-Host 'Preparando os arquivos do jogo...'
Start-Process $godotExe -ArgumentList @('--headless', '--path', "`"$game`"", '--import') -Wait -WindowStyle Hidden
Write-Host 'Abrindo o jogo!' -ForegroundColor Green
Start-Process $godotExe -ArgumentList @('--path', "`"$game`"")
