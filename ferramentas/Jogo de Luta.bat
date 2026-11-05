@echo off
title Jogo de Luta
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((Get-Content -LiteralPath '%~f0' -Raw) -split '#PS#START\r?\n',2)[1]"
exit /b
#PS#START
# Jogo de Luta: baixa a versao mais nova do GitHub e abre o jogo.
# Tudo fica em %LOCALAPPDATA%\JogoDeLuta. Usa a Godot que ja estiver no computador.
# Para trocar a Godot usada, apague %LOCALAPPDATA%\JogoDeLuta\godot_caminho.txt.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$repo     = 'brenoalmeidatec/Jogo-de-Luta'
$branch   = 'codex/pengaro'   # branch com o jogo. Troque quando o PR for aceito.
$base     = Join-Path $env:LOCALAPPDATA 'JogoDeLuta'
$game     = Join-Path $base 'jogo'
$godotDir = Join-Path $base 'godot'
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

# 2. Acha a Godot que ja esta no computador (4.3 ou mais nova). Se nao achar, baixa uma.
function Versao($arquivo) {
    if ($arquivo.Name -match 'v(\d+)\.(\d+)(?:\.(\d+))?') {
        $p = if ($Matches[3]) { [int]$Matches[3] } else { 0 }
        return [version]::new([int]$Matches[1], [int]$Matches[2], $p)
    }
    return [version]'4.3.0'  # sem versao no nome (ex.: Steam): tenta usar mesmo assim
}
$godotExe = $null
$salvo = Join-Path $base 'godot_caminho.txt'
if (Test-Path $salvo) {
    $c = (Get-Content $salvo -Raw).Trim()
    if ($c -and (Test-Path $c)) { $godotExe = $c }
}
if (-not $godotExe) {
    Write-Host 'Procurando a Godot no computador...'
    $lugares = @(
        "$env:USERPROFILE\Desktop", "$env:USERPROFILE\Downloads", "$env:USERPROFILE\Documents",
        "$env:LOCALAPPDATA", "$env:ProgramFiles", "${env:ProgramFiles(x86)}",
        "${env:ProgramFiles(x86)}\Steam\steamapps\common\Godot Engine", "C:\Godot", "D:\Godot"
    ) | Where-Object { $_ -and (Test-Path $_) }
    $achados = foreach ($l in $lugares) {
        Get-ChildItem $l -Recurse -Depth 3 -File -ErrorAction SilentlyContinue -Include 'Godot*.exe', 'godot*.exe' |
            Where-Object { $_.Name -notmatch 'console|mono' }
    }
    $cmd = Get-Command godot -ErrorAction SilentlyContinue
    if ($cmd) { $achados = @($achados) + (Get-Item $cmd.Source) }
    $melhor = $achados | Where-Object { (Versao $_) -ge [version]'4.3.0' -and (Versao $_).Major -eq 4 } |
        Sort-Object { Versao $_ } -Descending | Select-Object -First 1
    if ($melhor) {
        $godotExe = $melhor.FullName
        Write-Host "Usando a Godot que ja estava aqui: $godotExe" -ForegroundColor Green
    } else {
        $baixada = Join-Path $godotDir 'Godot_v4.3-stable_win64.exe'
        if (-not (Test-Path $baixada)) {
            try {
                Write-Host 'Nao achei a Godot 4.3 ou mais nova. Baixando (so na primeira vez, uns 60 MB)...'
                $gz = Join-Path $base 'godot.zip'
                Invoke-WebRequest 'https://github.com/godotengine/godot/releases/download/4.3-stable/Godot_v4.3-stable_win64.exe.zip' -OutFile $gz -UseBasicParsing
                Expand-Archive $gz $godotDir -Force
                Remove-Item $gz -Force
            } catch {
                Fechar "Nao consegui baixar a Godot: $($_.Exception.Message)"
            }
        }
        $godotExe = $baixada
    }
    Set-Content $salvo $godotExe
}

# 3. Prepara os arquivos novos e abre o jogo
Write-Host 'Preparando os arquivos do jogo...'
Start-Process $godotExe -ArgumentList @('--headless', '--path', "`"$game`"", '--import') -Wait -WindowStyle Hidden
Write-Host 'Abrindo o jogo!' -ForegroundColor Green
Start-Process $godotExe -ArgumentList @('--path', "`"$game`"")
