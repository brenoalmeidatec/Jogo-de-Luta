# Como o launcher instala o layout Nazafight

`motif/nazafight/` é o screenpack inteiro (título, seleção, VS e HUD). Tudo nele é **gerado** por
`python ferramentas/gerar_layout.py`, mas fica versionado porque o `.bat` não roda Python. Não edite à mão: mude o gerador
e rode de novo (ele é determinístico, então o diff só mostra o que mudou de verdade).

O `ferramentas/Jogo de Luta.bat` ainda **não** faz isto. Os passos abaixo são o que falta integrar nele, nesta ordem.

## 1. Baixar também `motif/*`

No passo 2 (manifesto), o filtro passa a pegar as duas pastas:

```powershell
$arquivos = @($arvore.tree | Where-Object { $_.type -eq 'blob' -and ($_.path -like 'chars/*' -or $_.path -like 'motif/*') })
```

O resto do passo (manifesto por SHA, `DownloadFile`) não muda. Os arquivos caem em `$game\motif\nazafight\...`.

## 2. Copiar para `data\nazafight` (logo depois do passo 3, dos lutadores)

```powershell
$motifOrigem = Join-Path $game 'motif\nazafight'
if (Test-Path (Join-Path $motifOrigem 'system.def')) {
    robocopy $motifOrigem (Join-Path $motor 'data\nazafight') /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { Fechar 'Nao consegui instalar o layout Nazafight.' }
}
```

O `/MIR` apaga o que o `Ajustar-Menus` injetou da última vez, então ele tem que vir **antes** do passo 5.

## 3. Apontar o config para o motif (dentro do bloco `if (Test-Path $cfg)` do passo 4)

Com o jogo fechado, na mesma leitura que já grava o `WindowTitle`:

```powershell
$t = [IO.File]::ReadAllText($cfg)
$t = [regex]::Replace($t, '(?im)^WindowTitle\s*=.*$', 'WindowTitle       = Nazafight')
if (Test-Path (Join-Path $motor 'data\nazafight\system.def')) {
    $t = [regex]::Replace($t, '(?im)^Motif\s*=.*$', 'Motif             = data/nazafight/system.def')
}
[IO.File]::WriteAllText($cfg, $t)
```

Se o `config.ini` ainda não existir, vale a mesma abertura única que o passo 4 já faz para ele nascer.

## 4. Depois disso, o passo 5 (`Ajustar-Menus`) roda como está

Ele lê o `Motif` do config e injeta `menu.done.key = s` / `done.key = s` em `data\nazafight\system.def`. O system.def
gerado já traz vazias as seções que ele procura (`[Option Info]`, `[Pause Menu]`, `[Replay Info]`, `[Continue Screen]`).

## Não fazer

- Não usar `-r` no `Start-Process`: o config basta e o `Ajustar-Menus` depende dele.
- Não pôr `select.def` dentro de `motif/nazafight/`: ele passaria na frente do `data\select.def` que o passo 3 edita
  (o gerador falha se encontrar um).

## Conferir depois de integrar

1. Rodar o `.bat` numa pasta limpa: o `save\config.ini` final tem que ter `Motif = data/nazafight/system.def` e as teclas
   do P1 preservadas.
2. Abrir o jogo, ver o título NAZAFIGHT, a seleção e uma luta. Se der erro, ele vai para `ikemen\save\logs\Ikemen_*.log`.
3. Para voltar ao layout antigo: trocar a linha do config para `Motif = data/ikemen1/system.def`.
