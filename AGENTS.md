# Instruções para o Codex

O jogo saiu da Godot e agora roda no IKEMEN GO, com personagens em formato MUGEN.

- Trabalhe sempre na branch `mugen`. Dê `git pull` antes de começar e não use mais `codex/pengaro`.
- Não recrie o projeto Godot.
- O Pengaró é gerado: mude `ferramentas/gerar_pengaro.py`, rode esse script e depois
  `python ferramentas/verificar_pengaro.py`. Não edite `chars/pengaro/` à mão.
- O atalho do Breno baixa a branch `mugen`, então o que subir nela vai para o jogo no clique seguinte.
- Use só mecânicas do KOF: nada de personagens, arte, nomes de golpes, sons ou músicas de jogos existentes.
- Resenha pesada pode. Não pode piada de escravidão nem o estereótipo da mulher loira.
- Lata e camisa sem marca real.

## Animação e recursos (regra fixa)

- Nenhum golpe pode pular direto de uma pose para outra. Todo movimento novo precisa de quadros
  intermediários: preparação, meio do caminho, golpe (com rastro de velocidade) e volta.
- Quadros desenhados de verdade (folha gerada por imagem e cortada com `ferramentas/recortar_quadros.py`)
  têm prioridade. Enquanto não houver, gere os intermediários com `ferramentas/quadros_intermediarios.py`,
  que gira e encurta o membro em volta da junta a partir das 9 poses. Não volte a usar só `gira`/`estica`
  na pose inteira.
- Os quadros ficam em `sprites/pengaro/quadros/<movimento>/00.png...` (224x128, pés em 104,119) e o
  `gerar_pengaro.py` lê de lá.
- Antes de criar algo do zero, veja `docs/recursos-github.md`: lista de projetos livres (verificador de
  combos, editores de .sff/.air, RotSprite, LibreSprite, interpolação por IA) com licença e uso.
  Use só o que tiver licença livre e nunca arte de jogo comercial.
