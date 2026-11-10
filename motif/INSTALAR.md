# Como o launcher instala o layout Nazafight

`motif/nazafight/` é o screenpack inteiro (título, seleção, VS e HUD). Tudo nele é **gerado** por
`python ferramentas/gerar_layout.py`, mas fica versionado porque o `.bat` não roda Python. Não edite à mão: mude o gerador
e rode de novo (ele é determinístico, então o diff só mostra o que mudou de verdade).

O `ferramentas/Jogo de Luta.bat` já instala o motif sozinho. O que ele faz, na ordem:

1. **Download (passo 1).** Busca no GitHub a árvore do commit e, dela, as subárvores `chars` **e** `motif` (cada uma tem
   o seu sha). Cada arquivo vira `chars/...` ou `motif/...` no manifesto (`%USERPROFILE%\JogoDeLuta\manifesto.json`) e
   em `jogo\`; só baixa o que mudou de hash, sempre para `.part` e depois `Move-Item`.
   O atalho "já está na versão mais nova" exige o mesmo sha de commit **e** que existam os marcadores
   `jogo\chars\pengaro\pengaro.def` e `jogo\motif\nazafight\system.def` e todo arquivo listado no manifesto: se
   faltar qualquer um, ele busca as listas de novo e baixa só o que falta.
2. **Cópia (logo depois dos lutadores).** `robocopy /MIR` de `jogo\motif\nazafight` para `ikemen\data\nazafight`, só
   essa pasta. O `/MIR` desfaz o que o `Ajustar-Menus` injetou da última vez; ele roda depois e injeta de novo.
3. **Config (passo 4).** Na mesma leitura/escrita do `save\config.ini` que grava `WindowTitle = Nazafight`, se
   `data\nazafight\system.def` existe, grava `Motif = data/nazafight/system.def`.
4. **Menus (passo 5).** O `Ajustar-Menus` lê o `Motif` do config e injeta `menu.done.key = s` / `done.key = s` em
   `data\nazafight\system.def`. O system.def gerado já traz vazias as seções que ele procura (`[Option Info]`,
   `[Pause Menu]`, `[Replay Info]`, `[Continue Screen]`).

## Não fazer

- Não usar `-r` no `Start-Process`: o config basta e o `Ajustar-Menus` depende dele.
- Não pôr `select.def` dentro de `motif/nazafight/`: ele passaria na frente do `data\select.def` que o passo 3 edita
  (o gerador falha se encontrar um).

## Voltar ao layout antigo

O `.bat` regrava o `Motif` a cada abertura. Para ver o antigo, troque a linha do config para
`Motif = data/ikemen1/system.def` e abra o `Ikemen_GO.exe` direto, sem o `.bat`. Se der erro na tela, o log vai para
`ikemen\save\logs\Ikemen_*.log`.
