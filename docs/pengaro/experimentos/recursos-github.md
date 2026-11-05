# Recursos no GitHub para o jogo de luta

Pesquisa de 05/11/2026. Só projetos sem arte ou personagens de jogos comerciais. Estrelas e licenças como aparecem no GitHub hoje; "sem licença" quer dizer que o autor não declarou, então só dá para usar como referência.

## Personagem e motor (IKEMEN GO / MUGEN)

| Projeto | Licença | Como eu usaria |
|---|---|---|
| [KiloTheLoser/ikemen-combo-finder](https://github.com/KiloTheLoser/ikemen-combo-finder) | MIT | Lê o .cmd/.cns do Pengaró e lista os combos que realmente encaixam. Bom para conferir a corrente de fracos e os cancelamentos em especial. |
| [eduardovbe/CharFactory](https://github.com/eduardovbe/CharFactory) | MIT | Editor de personagem MUGEN/IKEMEN que conversa com Claude/Codex via MCP. Útil para ver e ajustar caixas de colisão no .air. Projeto novo (3 estrelas), testar antes de confiar. |
| [openkakutou/character-editor](https://github.com/openkakutou/character-editor) e [openkakutou/stage](https://github.com/openkakutou/stage) | MIT | Editor web de .sff/.air e biblioteca para ler e escrever cenários. Serve para abrir o pengaro.sff e conferir os quadros. Também é novo. |
| [RealFoobs/stage-intro](https://github.com/RealFoobs/stage-intro) e [RealFoobs/Extended-Intro-Winpose](https://github.com/RealFoobs/Extended-Intro-Winpose) | MIT | Intros de cenário e poses de vitória mais caprichadas (esconde o HUD, troca a música). |
| [ikemen-engine/Ikemen-GO-Screenpack](https://github.com/ikemen-engine/Ikemen-GO-Screenpack) | não declarada (é o screenpack da Elecbyte) | Base de menus e fontes que já vem com o motor. Dá para trocar as imagens pelas nossas e manter a estrutura. |
| [NoisyChain/Sakuga-Engine](https://github.com/NoisyChain/Sakuga-Engine) | MIT | Motor de luta em Godot 4 (C#). Não vamos usar o motor, mas o código de buffer de comandos e cancelamentos é boa referência. |

## Animação e quadros intermediários

| Projeto | Licença | Como eu usaria |
|---|---|---|
| [LibreSprite/LibreSprite](https://github.com/LibreSprite/LibreSprite) | GPL-2.0 (só o programa; o que você desenha é seu) | Editor de pixel art grátis para retocar os quadros que o script gera (limpar costura do quadril, mão etc.). |
| [spuuntries/rotsprite-js](https://github.com/spuuntries/rotsprite-js) / [adnanlah/rotsprite-webgl](https://github.com/adnanlah/rotsprite-webgl) | Apache-2.0 / MIT | Algoritmo RotSprite: gira pixel art sem serrilhar. Vou portar a ideia para o script que gira braço e perna. |
| [javierbyte/morphin](https://github.com/javierbyte/morphin) | BSD-3-Clause | Interpolação simples entre dois sprites. Bom para testar transições rápidas. |
| [Doubiiu/ToonCrafter](https://github.com/Doubiiu/ToonCrafter) | Apache-2.0 (código; confira os termos do modelo) | IA que cria os quadros do meio entre duas poses desenhadas. Precisa de placa de vídeo forte; o resultado sai em alta resolução e depois passa pelo pixelizar.py. |

## Cenários

Não achei no GitHub cenário livre de qualidade que não seja tirado de jogo comercial. Para cenário, o caminho é OpenGameArt/itch.io com licença CC0 ou desenhar o nosso.

## Repositórios da conta brenoalmeidatec

- **Jogo-de-Luta**: este jogo.
- **KIKIU-Survival** (público): jogo de hordas em pixel art. Pode ter efeitos, partículas e paleta para reaproveitar. Não consegui abrir daqui porque esta sessão só tem acesso ao repositório do jogo de luta.
- **KIKIU-Releases**, **hz-optimizer**, **podologo-edson**: não têm nada para o jogo.
