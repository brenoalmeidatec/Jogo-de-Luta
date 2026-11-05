# Instruções para o Codex

O jogo saiu da Godot e agora roda no IKEMEN GO, com personagens em formato MUGEN.

- A branch `mugen` é a do jogo: o atalho do Breno baixa ela a cada clique. Não faça push direto nela.
  Dê `git pull` na `mugen`, crie uma branch `codex/<assunto>` a partir dela e abra um PR para a `mugen`.
- Cada mudança no Pengaró vai num commit só, com `ferramentas/gerar_pengaro.py` e os arquivos de
  `chars/pengaro/` juntos. Nunca suba o gerador num commit e os arquivos gerados em outro.
- Não recrie o projeto Godot.
- O Pengaró é gerado: mude `ferramentas/gerar_pengaro.py`, rode esse script e depois
  `python ferramentas/verificar_pengaro.py`. Não edite `chars/pengaro/` à mão.
- Só abra o PR se `python ferramentas/verificar_pengaro.py` terminar sem erros.
- Use só mecânicas do KOF: nada de personagens, arte, nomes de golpes, sons ou músicas de jogos existentes.
- Resenha pesada pode. Não pode piada de escravidão nem o estereótipo da mulher loira.
- Lata e camisa sem marca real.
