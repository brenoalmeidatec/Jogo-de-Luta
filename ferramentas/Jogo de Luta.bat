@echo off
title Nazafights
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((Get-Content -LiteralPath '%~f0' -Raw) -split '#PS#START\r?\n',2)[1]"
exit /b
#PS#START
# Nazafights: baixa a versao mais nova do GitHub e abre o jogo no IKEMEN GO.
# Tudo fica em %USERPROFILE%\JogoDeLuta (pasta com o nome antigo, para nao baixar o IKEMEN de novo).
# O IKEMEN GO so e baixado na primeira vez.
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

# 1. Atualiza o jogo. O repositorio tem centenas de MB de sprites que o jogo nao usa; so as pastas chars (lutadores)
# e motif (layout Nazafights: titulo, selecao, VS e HUD) valem.
# Pergunta primeiro so o sha do commit (40 bytes): se e o mesmo da ultima atualizacao completa e os arquivos estao
# no lugar (pengaro.def, o system.def do motif e todo arquivo do manifesto), nao baixa nada.
# Se mudou, pega so a lista dessas duas pastas e baixa os arquivos delas que mudaram (compara o hash de cada arquivo).
# Cada arquivo baixa para .part e so troca o antigo quando terminou: queda de rede nao deixa .sff pela metade.
$manifesto = Join-Path $base 'manifesto.json'
$manif = @{}
if (Test-Path $manifesto) {
    try {
        (Get-Content $manifesto -Raw | ConvertFrom-Json).PSObject.Properties | ForEach-Object { $manif[$_.Name] = $_.Value }
    } catch {
        Write-Host 'O registro do que ja foi baixado estava estragado; vou conferir todos os arquivos.' -ForegroundColor Yellow
        $manif = @{}
    }
}
$mudou = $false
try {
    Write-Host 'Procurando a versao mais nova do jogo no GitHub...'
    $ua = @{ 'User-Agent' = 'JogoDeLuta' }
    $api = New-Object Net.WebClient
    $api.Headers.Add('User-Agent', 'JogoDeLuta')
    $api.Headers.Add('Accept', 'application/vnd.github.sha')
    $commit = $api.DownloadString("https://api.github.com/repos/$repo/commits/$branch").Trim()
    if ($commit -notmatch '^[0-9a-f]{40}$') { throw "resposta estranha do GitHub: $commit" }
    # Atalho so vale se, alem do commit igual, existem os dois marcadores e todo arquivo do manifesto.
    $marcadores = @('chars/pengaro/pengaro.def', 'motif/nazafight/system.def') + @($manif.Keys | Where-Object { $_ -ne '@commit' })
    $faltando = @($marcadores | Where-Object { -not (Test-Path -LiteralPath (Join-Path $game ($_ -replace '/', '\'))) })
    if ($manif['@commit'] -eq $commit -and $faltando.Count -eq 0) {
        Write-Host 'O jogo ja esta na versao mais nova.' -ForegroundColor Green
    } else {
        $raiz = Invoke-RestMethod "https://api.github.com/repos/$repo/git/trees/$commit" -Headers $ua
        # Cada pasta tem a sua subarvore (sha proprio); o caminho de cada arquivo leva o nome da pasta na frente.
        $arquivos = @()
        foreach ($nome in @('chars', 'motif')) {
            $pasta = @($raiz.tree | Where-Object { $_.path -eq $nome -and $_.type -eq 'tree' })
            if ($pasta.Count -ne 1) { throw "a pasta $nome nao apareceu no GitHub" }
            $arvore = Invoke-RestMethod "https://api.github.com/repos/$repo/git/trees/$($pasta[0].sha)?recursive=1" -Headers $ua
            if ($arvore.truncated) { throw "a lista de arquivos de $nome veio cortada" }
            $arquivos += @($arvore.tree | Where-Object { $_.type -eq 'blob' } | ForEach-Object {
                [pscustomobject]@{ caminho = "$nome/$($_.path)"; sha = $_.sha }
            })
        }
        # Os .def por ultimo e o system.def do motif no fim de tudo: se a rede cair no meio, o marcador que liga o
        # layout (e o .def de cada lutador) so existe quando os arquivos que ele cita ja chegaram.
        $arquivos = @($arquivos | Sort-Object { $_.caminho -eq 'motif/nazafight/system.def' }, { $_.caminho -like '*.def' }, caminho)
        $wc = New-Object Net.WebClient
        $wc.Headers.Add('User-Agent', 'JogoDeLuta')
        $i = 0
        foreach ($a in $arquivos) {
            $i++
            $caminho = $a.caminho
            $dest = Join-Path $game ($caminho -replace '/', '\')
            if ((Test-Path $dest) -and $manif[$caminho] -eq $a.sha) { continue }
            New-Item -ItemType Directory -Force (Split-Path $dest) | Out-Null
            Write-Host "Baixando $caminho ($i de $($arquivos.Count))..."
            $url = "https://raw.githubusercontent.com/$repo/$commit/" + (($caminho -split '/' | ForEach-Object { [Uri]::EscapeDataString($_) }) -join '/')
            $parte = "$dest.part"
            $wc.DownloadFile($url, $parte)
            Move-Item -LiteralPath $parte -Destination $dest -Force
            $manif[$caminho] = $a.sha
            $mudou = $true
        }
        # Esquece arquivos que sairam do repositorio; senao o atalho acima nunca mais vale se um deles sumir do disco.
        $noRepo = @{}; foreach ($a in $arquivos) { $noRepo[$a.caminho] = $true }
        foreach ($k in @($manif.Keys)) { if ($k -ne '@commit' -and -not $noRepo.ContainsKey($k)) { $manif.Remove($k) } }
        $manif['@commit'] = $commit
        $mudou = $true
        Write-Host 'Jogo atualizado!' -ForegroundColor Green
    }
} catch {
    Write-Host "Nao consegui atualizar: $($_.Exception.Message)" -ForegroundColor Yellow
    if (-not (Test-Path (Join-Path $game 'chars\pengaro\pengaro.def'))) {
        Fechar 'Ainda nao tem nenhuma versao do jogo baixada. Confira a internet e tente de novo.'
    }
    Write-Host 'Abrindo a ultima versao que ja estava baixada.'
} finally {
    if ($mudou -and $manif.Count -gt 0) {
        $manif | ConvertTo-Json | Set-Content "$manifesto.tmp" -Encoding ASCII
        Move-Item -LiteralPath "$manifesto.tmp" -Destination $manifesto -Force
    }
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
foreach ($lutador in @('pengaro', 'hazaki', 'gutto', 'raiclaven', 'ck')) {
    $origem = Join-Path $game "chars\$lutador"
    if (-not (Test-Path (Join-Path $origem "$lutador.def"))) { continue }
    robocopy $origem (Join-Path $motor "chars\$lutador") /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { Fechar "Nao consegui instalar $lutador." }
    if ($texto -notmatch "(?m)^\s*$lutador\s*(?:,|$)") {
        $texto = $texto -replace '(?m)^randomselect', "$lutador, stages/stage0-720.def`r`nrandomselect"
    }
}
# Tira da selecao os lutadores de exemplo que vem com o IKEMEN (Kung Fu Man e variacoes): so comenta a linha,
# os arquivos ficam (o motor ainda pode precisar deles).
$texto = [regex]::Replace($texto, '(?m)^([ \t]*kfm\w*[ \t]*,)', ';$1')
[IO.File]::WriteAllText($select, $texto)

# Layout Nazafights: espelha so a pasta dele em data\nazafight. O /MIR desfaz o que o Ajustar-Menus (passo 5)
# injetou da ultima vez, por isso ele roda depois deste passo e injeta de novo.
$motifOrigem = Join-Path $game 'motif\nazafight'
$motifDef = Join-Path $motor 'data\nazafight\system.def'
if (Test-Path (Join-Path $motifOrigem 'system.def')) {
    robocopy $motifOrigem (Join-Path $motor 'data\nazafight') /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { Fechar 'Nao consegui instalar o layout Nazafights.' }
}

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
if (Test-Path $cfg) {
    Ajustar-Teclas $cfg
    # Nome do jogo na barra da janela e layout Nazafights (se ele foi instalado; senao fica o motif que ja estava).
    # Carrega a luta durante a tela de VS (esconde parte da espera) e estica a janela sem borrar o pixel art.
    # VSync, tela cheia, modo de video, Framerate e volumes ficam como o jogador deixou.
    $t = [IO.File]::ReadAllText($cfg)
    $t = [regex]::Replace($t, '(?im)^WindowTitle\s*=[^\r\n]*', 'WindowTitle       = Nazafights')
    if (Test-Path $motifDef) {
        $linha = 'Motif             = data/nazafight/system.def'
        if ($t -match '(?im)^Motif\s*=') {
            $t = [regex]::Replace($t, '(?im)^Motif\s*=[^\r\n]*', $linha)
        } else {
            # Sem a linha o IKEMEN usa o motif padrao: poe logo abaixo do [Config], com a quebra de linha do arquivo.
            $nl = if ($t -match "`r`n") { "`r`n" } else { "`n" }
            $t = ([regex]'(?im)^\[Config\][^\r\n]*').Replace($t, ('$0' + $nl + $linha), 1)
        }
    }
    $t = [regex]::Replace($t, '(?im)^(VsScreenLoading\s*=)[^\r\n]*', '${1} 1')
    $t = [regex]::Replace($t, '(?im)^(WindowScaleMode\s*=)[^\r\n]*', '${1} 0')
    [IO.File]::WriteAllText($cfg, $t)
}

# 5. Menus: navega com W A S D e confirma so com Enter. Os botoes de ataque (as setas) nao confirmam
# nada nos menus. O IKEMEN le as teclas de confirmacao do motif (system.def); a selecao de personagem
# usa os botoes para escolher o personagem, entao tambem ajustamos essa funcao no main.lua.
function Set-Chave($t, $secao, $chave, $valor) {
    $m = [regex]::Match($t, '(?ims)^\[' + [regex]::Escape($secao) + '\][^\r\n]*\r?\n(.*?)(?=^\[|\z)')
    if (-not $m.Success) { return $t }
    $corpo = $m.Groups[1].Value
    $ek = [regex]::Escape($chave)
    if ($corpo -match "(?im)^\s*$ek\s*=") {
        $corpo = [regex]::Replace($corpo, "(?im)^(\s*)$ek\s*=.*$", ('${1}' + "$chave = $valor"))
    } else {
        $corpo = "$chave = $valor`r`n" + $corpo
    }
    return $t.Substring(0, $m.Groups[1].Index) + $corpo + $t.Substring($m.Groups[1].Index + $m.Groups[1].Length)
}
function Ajustar-Menus {
    $motif = 'data\ikemen1\system.def'
    if (Test-Path $cfg) {
        $mm = [regex]::Match([IO.File]::ReadAllText($cfg), '(?im)^Motif\s*=\s*(\S+)')
        if ($mm.Success) { $motif = $mm.Groups[1].Value -replace '/', '\' }
    }
    $def = Join-Path $motor $motif
    if (Test-Path $def) {
        $t = [IO.File]::ReadAllText($def)
        foreach ($sec in @('Title Info', 'Option Info', 'Pause Menu', 'Replay Info')) {
            $t = Set-Chave $t $sec 'menu.done.key' 's'
        }
        foreach ($ch in @('done.key', 'p1.teammenu.done.key', 'p2.teammenu.done.key', 'p1.palmenu.done.key', 'p2.palmenu.done.key')) {
            $t = Set-Chave $t 'Select Info' $ch 's'
        }
        $t = Set-Chave $t 'VS Screen' 'done.key' 's'
        $t = Set-Chave $t 'Continue Screen' 'done.key' 's'
        [IO.File]::WriteAllText($def, $t)
    }
    $lua = Join-Path $motor 'external\script\main.lua'
    if (Test-Path $lua) {
        $l = [IO.File]::ReadAllText($lua)
        if ($l -notmatch 'jogo-de-luta: Endiabrado v2') {
            # Enter escolhe o lutador normal; o soco forte (y) escolhe a paleta 2 (Pengaro Endiabrado; nos outros vira 1).
            # Os dois contam no APERTO ('s', 'y'), nao enquanto estao segurados ('/s'): segurado, o Enter que escolheu
            # o 1o lutador confirmava sozinho o 2o (no modo assistir sempre saia o primeiro da lista). O motor nao tem
            # o comando '/y' (segurar y) na tela de selecao, so 'y'.
            $novo = "function main.f_btnPalNo(p)`n`t-- jogo-de-luta: Endiabrado v2 = Enter escolhe normal, soco forte escolhe o endiabrado; conta no aperto`n`tif commandGetState(p, 's') then return 1 end`n`tif commandGetState(p, 'y') then return 2 end`n`treturn 0`nend"
            $l2 = [regex]::Replace($l, '(?s)function main\.f_btnPalNo\(p\).*?\r?\nend', { param($x) $novo }, 1)
            if ($l2 -ne $l) { [IO.File]::WriteAllText($lua, $l2) }
        }
    }
    # A paleta 2 so existe no Pengaro: em qualquer outro lutador volta para a 1.
    $st = Join-Path $motor 'external\script\start.lua'
    if (Test-Path $st) {
        $s = [IO.File]::ReadAllText($st)
        if ($s -notmatch 'jogo-de-luta: paleta 2') {
            $alvo = 'start.p[side].t_selTemp[member].pal = main.f_btnPalNo(cmd)'
            $extra = $alvo + "`n`t`t`t`t`t-- jogo-de-luta: paleta 2 so no Pengaro`n`t`t`t`t`tif start.p[side].t_selTemp[member].pal == 2 and not tostring(start.f_getCharData(start.c[player].selRef).def):lower():find('pengaro', 1, true) then start.p[side].t_selTemp[member].pal = 1 end"
            $s2 = $s.Replace($alvo, $extra)
            if ($s2 -ne $s) { [IO.File]::WriteAllText($st, $s2) }
        }
    }
}
try { Ajustar-Menus } catch { Write-Host "Nao consegui ajustar os menus: $($_.Exception.Message)" -ForegroundColor Yellow }

# 6. Abre o jogo
Write-Host 'Abrindo o jogo!' -ForegroundColor Green
Start-Process $exe -WorkingDirectory $motor -WindowStyle Normal
