# Layout novo "Arena" (issue #39, missão de 2026-11-14 item 1)

Pedido do Breno: layout mais moderno, com cara de jogo de luta, título animado, HUD bem simples, sprites menores na
tela de VS e seleção de lutador e de mapa no mesmo estilo. Tudo sai de `ferramentas/gerar_layout.py` (rodar e
subir o que mudar em `motif/nazafight/` e `docs/previas-layout/`).

## O estilo

- Fundo de noite azulada com riscos diagonais finos, painéis inclinados ou de quinas cortadas.
- **P1 laranja (fogo), P2 azul (mar)**, ouro só no que está em destaque (item ativo, cursor do "?", moldura do mapa).
- Desenhado numa **grade de 2x** (640x360 de desenho na tela cheia): a linha de 2 px dá o ar moderno. As fontes de
  menu continuam na grade de 4x; a fonte do HUD e o relógio são de 2x.
- 15 cores novas na paleta (`ARENA` no gerador); o gerador ainda recusa qualquer cor fora da lista.

## Tela por tela

| Tela | O que mudou |
| --- | --- |
| Título | A cena de Nazaré continua, agora com o rio ondulando (8 quadros só da água, barcos parados), halo do sol pulsando, 3 aves cruzando o céu, brasas subindo, o logo caindo, balançando e com um brilho que corre a cada ~4 s. Menu num painel escuro translúcido com a barra laranja inclinada no item ativo. |
| Seleção | Retratos grandes em painéis da cor de cada jogador, placas de nome inclinadas, aba do modo no alto, grade de células escuras e cursor de cantoneiras com a etiqueta 1P/2P. |
| Mapa (#35) | Mesmo fundo, aba "ESCOLHA O MAPA", moldura da prévia com quinas de ouro, setas em chevron, placa do nome e a dica dos botões. |
| VS | Metade laranja e metade azul com corte diagonal branco. Os bustos agora em tamanho natural (448x216, 1/4 do que era em área), inteiros, em pé sobre a placa do nome. Emblema VS desenhado à mão. |
| HUD | Retrato 104 px com anel na cor do jogador, vida fina inclinada (ouro, laranja abaixo de 50%, vermelho abaixo de 25%, dano que vai cair em branco), nome pequeno embaixo, vitórias em losango junto do relógio, relógio pequeno, poder fino no rodapé com 3 losangos de estoque. Letreiros de ROUND, LUTA! e K.O. novos. |

## Conferido

- Robô na nuvem (`testar_pengaro.py --linux`): 151 verificações, 0 falhas.
- Jogo de verdade na nuvem (`testar_mapas.py`, que agora tira foto da tela de VS e grava a abertura com
  `--filmar-titulo S`): fotos em `docs/previas-layout/jogo/` e a abertura em `titulo_animado.gif`.

## Armadilhas

- Camada `type = normal` do `[VersusBG]`/`[TitleBG]` **ignora o alfa do PNG** (desenhava uma caixa preta em volta
  do emblema). Use `type = anim` com uma ação de um quadro.
- No `[Face]` o motor desenha o `top` **antes** do rosto; o anel da moldura vai no `bg`.
- Ficar parado na abertura liga a demonstração (luta CPU x CPU) depois de uns segundos; filmar a abertura atrasa
  as fotos seguintes do `testar_mapas.py`.

## Sugestões para depois

- Retrato do HUD menor de verdade (80 px) pede um sprite 9000,2 em cada lutador; reduzir na escala do motor borra.
- Painel do P2 vazio no Arcade (o adversário ainda não foi sorteado): dá para pôr um "?" ou "CPU" ali.
- Textos em inglês do motor que ainda aparecem ("VERSUS MODE" na seleção do Versus) entram na revisão geral (item 6).
- Sons de menu novos (item 2 da missão).
