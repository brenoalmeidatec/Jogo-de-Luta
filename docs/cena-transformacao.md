# Cena da transformação (issue #49)

Pedido do Breno (2026-11-14): a transformação tem de ser "foda". Tudo fica preto, a câmera foca e dá um zoom leve no
lutador, entra a música da forma, e no auge vem o clarão e a luta volta. Primeiro no Pengaró; os outros depois que o
Breno aprovar o vídeo.

## Onde está

- `ferramentas/cena_transformacao.py`: pós-passo no `[Statedef 2000]` do `.cns`. Pode rodar de novo à vontade. O
  `gerar_pengaro.py` chama no fim, depois do parry, dos sons e do balanceamento.
- `ferramentas/filmar_transformacao.py`: filma a cena na nuvem (Xvfb), com o som do motor gravado pelo driver `disk`
  do SDL. Exemplo: `python3 ferramentas/filmar_transformacao.py saida.mp4 --cenario stages/cristo.def`.

## O que a cena faz

| Tique (Pengaró, L = 114) | O quê |
|---|---|
| 0 | `Pause` de L + 36 tiques congela o oponente; toca o som de entrada |
| 0 a 14 | o cenário apaga até o preto (`BGPalFX`); oponente, HUD, cronômetro e sombras somem |
| 0 a L | a câmera fecha devagar no lutador (`Zoom`, de 1 até 1,18, ease in-out) |
| 0 a 45 | a música do cenário baixa até sumir e entra a do boss (já existia, issue #33) |
| 55 a L | brilho violeta crescendo no Pengaró enquanto as sombras o possuem; tremor leve quando a garrafa quebra |
| L - 8 | a câmera empurra até 1,30 |
| L | clarão branco, tremor forte, forma nova |
| L a L + 36 | a luz volta aos poucos, a câmera solta, o HUD volta e a luta continua |

## Armadilhas do IKEMEN v1.0 (medidas no motor)

- `Zoom pos` é em relação ao centro da câmera: `Pos X` já serve. Subtrair `CameraPos X` dobra o desvio.
- `Zoom scale = 1` não é a câmera da luta: os lutadores ficam a 0,65 do tamanho, e o tamanho cresce com o quadrado do
  `scale`. A cena usa `1,24 * raiz(zoom)`.
- `camerabound = 0` e `stagebound = 0`, senão perto do canto a câmera não centra no lutador.
- `PalFX` com `redirectid` no oponente pausado não escurece nada. Para sumir com ele, `AssertSpecial` `invisible`
  com `redirectid`.
- A `SuperPause` antiga congelava o próprio Pengaró 30 tiques (`movetime = 0`). Com a `Pause` e `movetime` igual ao
  tempo, os controladores dele rodam a cada tique, o que a cena precisa.
- No Xvfb a 1280x720 o llvmpipe só desenha uns 17 quadros por segundo; a 640x360 sobe para uns 26. O filme sai ampliado.

## Os outros lutadores (aprovado pelo Breno em 2026-11-14)

A mesma cena vale para CK, Gutto, Raiclaven e Hazak. Cada um tem a cor do brilho e o tique em que ele começa em
`LUTADORES`, e o `gerar_<lutador>.py` chama `cena_transformacao.aplicar` por último.

| Lutador | Brilho | Auge | Observação |
|---|---|---|---|
| Pengaró | violeta | tique 114 | garrafa quebra no 55 |
| CK | verde do Ratão | tique 114 | o paredão aparece no escuro e vira fumaça |
| Gutto | brasa | tique 114 | |
| Raiclaven | verde de laboratório | tique 114 | |
| Hazak | ouro e fogo | tique 122 | a forma liga em `Time = 122` (diabo_loiro.py); a câmera mira 45 atrás dele para a patroa caber; a música do Despertar dele não estava ligada e a cena liga |

O auge é lido do `[State 2000, Liga]`: se o gatilho for `Time = N`, é N; senão é o fim da animação 2000. A `Pause` e o
clarão `BGPalFX` próprios do estado saem, porque a cena põe os dela. Gbzin: quando ganhar Despertar, entra na tabela.

## Sugestões

- A arte do Despertar do Pengaró muda de tamanho: os quadros de joelhos (596 a 599) são bem maiores que os de pé, e com
  o zoom isso aparece mais. Vale acertar na folha (issue #42).
- O rastro azul (`AfterImage`) fica como fantasmas no escuro. Se o Breno não gostar, é só tirar nesse estado.
- Cenário destruído depois do clarão (item 2 da missão de músicas e transformação) ainda não existe.
