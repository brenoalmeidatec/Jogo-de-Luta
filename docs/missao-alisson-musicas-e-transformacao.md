# Missão para o Alisson: músicas, transformação com cena e telas com cara de luta (2026-11-13)

Pedido do Breno. Ele quer que **você** faça tudo isto. Siga as regras de sempre (`docs/como-trabalhar.md`,
`docs/regras-dos-lutadores.md`, estilo arcade). Complementa a [`missao-alisson-2026-11-13.md`](missao-alisson-2026-11-13.md).

## 1. Músicas do jogo

Feitas no Suno (conta do Breno, plano gratuito) e escolhidas por ele. Como o plano gratuito não deixa baixar, o Breno
gravou a tela tocando cada uma; o áudio foi tirado desses vídeos **sem reconverter** (AAC 128 kbps, 48 kHz, estéreo,
igual ao do vídeo, conferido por md5). Os arquivos estão em [`musicas/originais/`](../musicas/originais/).

Todas são instrumentais, metal pesado com 8-bit, como o Breno pediu.

| Arquivo | Onde toca | Duração |
|---|---|---|
| `lobby.m4a` | tela de título e menus | 3:04 (os 10,6 s do começo são silêncio) |
| `selecao.m4a` | seleção de lutadores | 3:01 |
| `cenario_cristo.m4a` | cenário do Cristo | 3:04 |
| `cenario_maria_fumaca.m4a` | cenário da Maria Fumaça | 1:00 |
| `cenario_praca.m4a` | cenário da praça da prefeitura | 2:58 |
| `cenario_passarela.m4a` | cenário da passarela | 3:28 |
| `boss_pengaro_endiabrado.m4a` | transformação do Pengaró (Senhor das Trevas) | 0:55 |
| `boss_hazak_diabo_loiro.m4a` | transformação do Hazak (Diabo Loiro) | 3:38 |
| `boss_gutto_garanhao.m4a` | transformação do Gutto (Senhor da Guerra Garanhão) | 3:20 |
| `boss_ck_ratao.m4a` | transformação do CK (Ratão do Paredão) | 3:18 |
| `boss_raiclaven_cientista.m4a` | transformação do Raiclaven (Cientista Louco) | 3:13 |

Regras do Breno para a trilha:

- **Música é por tela e por cenário, nunca por lutador.** Os rounds são curtos e sempre há dois lutadores na tela.
- **A música da transformação substitui a do cenário**, para as duas nunca tocarem juntas (item 2).
- O que ele pediu para cada transformação: Pengaró vira um senhor das trevas; Hazak, um diabo loiro **tenebroso, de dar
  medo**; CK é ratão de paredão, baiano, de **pagodão baiano de bloquinho**; Raiclaven gosta de **trap**, então trap com
  pegada de laboratório; Gutto, senhor da guerra garanhão. A da praça antiga parecia forró de São João e foi refeita.
- Se alguma não servir, o Breno gera outra no Suno. Os títulos lá começam por "Nazafights - ".

Notas técnicas (conferidas no código do IKEMEN GO v1.0.0):

- O motor toca `.ogg`, `.mp3`, `.wav` e `.flac`, **não `.m4a`**. Converta na hora de ligar (OGG Vorbis de qualidade
  alta) e corte o silêncio das pontas: quase todas começam com cerca de 1 s de silêncio da gravação.
- Lobby e seleção: `[Music]` do `motif/nazafight/system.def`, chaves `title.bgm` e `select.bgm` (com `.loop = 1`).
- Lutas: `bgmusic` no `[Music]` de cada cenário, ou `music=` na linha do cenário em `[ExtraStages]` do `select.def`. Se
  houver vários `music=` na mesma linha, o motor sorteia um.
- Troca no meio da luta: controladores `PlayBGM` e `ModifyBGM` (existem no compilador do v1.0.0).
- O launcher só baixa `chars/`, `motif/` e `stages/`. Música que o jogo usa tem de ficar numa dessas pastas (por exemplo
  `motif/nazafight/musicas/`).
- Os `.m4a` somam uns 30 MB. Se o repositório pesar, deixe no git só os `.ogg` usados e guarde os originais fora.

## 2. Transformação com cena de anime e cenário destruído

Do jeito que o Breno descreveu, vale para **todo lutador que se transforma** (Pengaró, Hazak, Gutto, CK, Raiclaven e o
Deus Motoboy do Gbzin):

1. Quando o lutador se transforma, a luta para e roda uma **mini cena**.
2. A câmera **corta e foca no lutador que está se transformando**, como numa cena de anime de transformação.
3. A **música da transformação começa** (item 1) e entra uma **ambientação** (aura subindo, vento, tremor, partículas).
4. Ele **estoura**: no auge da transformação vem um **clarão** ou explosão de poder.
5. Quando o clarão some, o **cenário aparece destruído**, remodelado pelo poder dele, como se a explosão de poder tivesse
   transformado o lugar.
6. A luta volta com a forma nova, a música da transformação no lugar da do cenário e o cenário destruído até o fim do
   round.

Pontos que precisam de você:

- **Cenário destruído:** cada cenário de Nazaré precisa da sua versão destruída (Cristo, Maria Fumaça, praça, passarela,
  Katiara). Pode ser uma camada do próprio cenário que liga na hora, ou outro jogo de camadas. Se der, a destruição tem a
  cara do lutador que transformou (fumaça e correntes do Pengaró, fogo e ouro do Hazak, raios e crateras do Gutto e
  assim por diante, ver as auras em `docs/arcade/bosses_kit.md` na branch `efeitos`).
- **Câmera:** o IKEMEN tem o controlador `Zoom` para aproximar no lutador; `Pause` ou `SuperPause` seguram o oponente;
  `EnvColor` faz o clarão; `BGPalFX` escurece o fundo durante a ambientação. Confira tudo no motor antes de assumir.
- **Música:** `PlayBGM` com a faixa do lutador no começo da cena. A música do cenário não volta enquanto a forma durar.
- **Lugar no código:** o Despertar do Pengaró é o estado 2000 (`gerar_pengaro.py`). Os outros lutadores têm o seu.
  A cena entra ali, sem mudar a regra de quando se pode despertar.
- **Teste:** grave um vídeo curto da transformação e confira quadro a quadro (`docs/conferencia-de-golpe.md`). Rode o
  robô (`testar_pengaro.py --lutador ...`) para ver que nada quebrou.

## 3. Telas com cara de jogo de luta

O Breno acha o **lobby e as telas muito feios** e quer que pareçam de um **jogo de luta de verdade**. Remodele:

- **Tela de título e menu** (`ferramentas/gerar_layout.py`, `sprites/titulo/`, `motif/nazafight/`): mais impacto e
  energia de fliperama de luta anos 90.
- **Seleção de lutadores, tela de VS e HUD da luta** (barras de vida e de poder, retratos, cronômetro), no mesmo estilo.
- Só mecânica e clima de KOF e companhia; nada copiado de arte de outro jogo. Sem marcas reais.
- Junte com a abertura animada do item 3 da outra missão.

## 4. Efeitos de cada ataque

Pedido anterior do Breno, que ainda vale: **cada ataque de cada lutador tem o seu efeito**, para o golpe fazer mais
sentido na tela (fraco, forte, chute, agarrão, especial, super). Combine com o jeito de cada um e com o momento do golpe:
faísca no impacto, rastro no movimento, poeira na rasteira, brilho no super. Estilo sprite de arcade, nunca 3D.

## Ao terminar

Teste com o robô e no jogo, suba na `mugen`, regenere o que precisar e anote no `LOGBOOK.md` o que fez e o que ficou.
