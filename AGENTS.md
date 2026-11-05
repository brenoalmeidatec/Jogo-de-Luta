# Instruções para o Codex

O jogo saiu da Godot e agora roda no IKEMEN GO, com personagens em formato MUGEN.

> **Obrigatório:** todo trabalho em lutador segue [`docs/regras-dos-lutadores.md`](docs/regras-dos-lutadores.md)
> (kit mínimo de golpes, correntes, Despertar, ferramentas e efeitos pixelfx). Leia antes de mexer em qualquer
> personagem. Se outra instrução disser o contrário, vale esse arquivo.

- Comece por `docs/missoes-codex.md`: faça as missões na ordem. O Codex faz o jogo, e o Claude revisa e escreve as missões.
- Trabalhe sempre na branch `mugen`. Dê `git pull` antes de começar e não use mais `codex/pengaro`.
- Não recrie o projeto Godot.
- O Pengaró é gerado: mude `ferramentas/gerar_pengaro.py`, rode esse script e depois
  `python ferramentas/verificar_pengaro.py`. Não edite `chars/pengaro/` à mão.
- O atalho do Breno baixa a branch `mugen`, então o que subir nela vai para o jogo no clique seguinte.
- A base de mecânica é Mortal Kombat (comando de toques cardeais, sem girar analógico), com sistemas de KOF e
  Street Fighter. Só mecânica: nada de personagens, arte, nomes de golpes, sons ou músicas de jogos existentes.
- Resenha pesada pode. Não pode piada de escravidão nem o estereótipo da mulher loira.
- Lata e camisa sem marca real.
