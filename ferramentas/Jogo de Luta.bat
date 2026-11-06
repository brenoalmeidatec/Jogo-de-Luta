@echo off
title Jogo de Luta
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((Get-Content -LiteralPath '%~f0' -Raw) -split '#PS#START\r?\n',2)[1]"
exit /b
#PS#START
# Jogo de Luta: baixa a versao mais nova do GitHub e abre o jogo no IKEMEN GO.
# Tudo fica em %USERPROFILE%\JogoDeLuta. O IKEMEN GO so e baixado na primeira vez.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$repo   = 'brenoalmeidatec/Jogo-de-Luta'
$branch = 'mugen'   # branch com o jogo. Troque quando o PR for aceito.
$ikemen = 'https://github.com/ikemen-engine/Ikemen-GO/releases/download/v1.0.0/Ikemen_GO-v1.0.0-windows.zip'
$base   = Join-Path $env:USERPROFILE 'JogoDeLuta'
$game   = Join-Path $base 'jogo'
$motor  = Join-Path $base 'ikemen'
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
    robocopy $src $game /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
    Remove-Item $tmp -Recurse -Force
    Remove-Item $zip -Force
    Write-Host 'Jogo atualizado!' -ForegroundColor Green
} catch {
    Write-Host "Nao consegui atualizar: $($_.Exception.Message)" -ForegroundColor Yellow
    if (-not (Test-Path (Join-Path $game 'chars\pengaro\pengaro.def'))) {
        Fechar 'Ainda nao tem nenhuma versao do jogo baixada. Confira a internet e tente de novo.'
    }
    Write-Host 'Abrindo a ultima versao que ja estava baixada.'
}

# 2. Baixa o IKEMEN GO na primeira vez
$exe = Join-Path $motor 'Ikemen_GO.exe'
if (-not (Test-Path $exe)) {
    try {
        Write-Host 'Baixando o IKEMEN GO (so na primeira vez, uns 55 MB)...'
        $gz = Join-Path $base 'ikemen.zip'
        Invoke-WebRequest $ikemen -OutFile $gz -UseBasicParsing
        Expand-Archive $gz $motor -Force
        Remove-Item $gz -Force
    } catch {
        Fechar "Nao consegui baixar o IKEMEN GO: $($_.Exception.Message)"
    }
}

# 3. Instala os lutadores disponiveis e os registra na selecao.
$select = Join-Path $motor 'data\select.def'
$texto = [IO.File]::ReadAllText($select)
foreach ($lutador in @('pengaro', 'hazaki')) {
    $origem = Join-Path $game "chars\$lutador"
    if (-not (Test-Path (Join-Path $origem "$lutador.def"))) { continue }
    robocopy $origem (Join-Path $motor "chars\$lutador") /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { Fechar "Nao consegui instalar $lutador." }
    if ($texto -notmatch "(?m)^\s*$lutador\s*(?:,|$)") {
        $texto = $texto -replace '(?m)^randomselect', "$lutador, stages/stage0.def`r`nrandomselect"
    }
}
[IO.File]::WriteAllText($select, $texto)

# 4. Teclas do jogador 1: anda com W A S D, socos nas setas esquerda (fraco) e cima (forte),
# chutes nas setas baixo (fraco) e direita (forte). z e w saem de d e w para nao colidir. O IKEMEN so cria o save\config.ini depois da
# primeira abertura; se ainda nao existe, abre e fecha o jogo uma vez para ele nascer.
$cfg = Join-Path $motor 'save\config.ini'
function Ajustar-Teclas($arquivo) {
    $t = [IO.File]::ReadAllText($arquivo)
    $novo = @{ up='w'; down='s'; left='a'; right='d'; x='LEFT'; y='UP'; a='DOWN'; b='RIGHT'; z='v'; w='r' }
    $m = [regex]::Match($t, '(?ims)^\[Keys_P1\][^\r\n]*\r?\n.*?(?=^\[|\z)')
    if (-not $m.Success) { return }
    $bloco = $m.Value
    foreach ($k in $novo.Keys) {
        $bloco = [regex]::Replace($bloco, "(?im)^$k\s*=.*$", "$k = $($novo[$k])")
    }
    $t = $t.Substring(0, $m.Index) + $bloco + $t.Substring($m.Index + $m.Length)
    [IO.File]::WriteAllText($arquivo, $t)
}
if (-not (Test-Path $cfg)) {
    Write-Host 'Primeira abertura: preparando as teclas...'
    $p = Start-Process $exe -WorkingDirectory $motor -PassThru
    for ($i = 0; $i -lt 30 -and -not (Test-Path $cfg); $i++) { Start-Sleep 1 }
    Start-Sleep 2
    if (-not $p.HasExited) { Stop-Process $p -Force }
    Start-Sleep 1
}
if (Test-Path $cfg) { Ajustar-Teclas $cfg }

# 5. Abre o jogo
Write-Host 'Abrindo o jogo!' -ForegroundColor Green
Start-Process $exe -WorkingDirectory $motor -WindowStyle Normal
