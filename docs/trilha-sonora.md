# Trilha sonora (ligada em 2026-11-14)

As 11 músicas do Suno escolhidas pelo Breno (`musicas/originais/*.m4a`) tocam no jogo em OGG. Regras do Breno: música é
por tela e por cenário, nunca por lutador; a do Despertar substitui a do cenário; todo loop sem emenda audível; na
transformação a do cenário baixa até sumir e só então entra a do boss (issue #33).

## Onde cada uma toca

| Faixa | Arquivo no jogo | Ligada em | Loop (s) |
|---|---|---|---|
| lobby | `motif/nazafight/musicas/lobby.ogg` | `system.def` `title.bgm` (título e menus) | 71,1 → 156,6 |
| selecao | `motif/nazafight/musicas/selecao.ogg` | `system.def` `select.bgm` | 75,4 → 160,8 |
| cenario_maria_fumaca | `stages/musicas/maria_fumaca.ogg` | `stages/maria_fumaca.def` `[Music]` | 22,3 → 53,4 |
| cenario_cristo | `stages/musicas/cristo.ogg` | cenário ainda não existe | 35,1 → 170,9 |
| cenario_praca | `stages/musicas/praca.ogg` | cenário ainda não existe | 36,0 → 153,8 |
| cenario_passarela | `stages/musicas/passarela.ogg` | cenário ainda não existe | 83,6 → 182,7 |
| boss_pengaro_endiabrado | `chars/pengaro/despertar.ogg` | Despertar (Statedef -2) | 14,7 → 40,2 |
| boss_ck_ratao | `chars/ck/despertar.ogg` | Despertar | 72,3 → 161,5 |
| boss_gutto_garanhao | `chars/gutto/despertar.ogg` | Despertar | 42,4 → 184,8 |
| boss_raiclaven_cientista | `chars/raiclaven/despertar.ogg` | Despertar | 54,2 → 161,0 |
| boss_hazak_diabo_loiro | `chars/hazaki/despertar.ogg` | ainda não: o Hazak não tem Despertar nesta versão | 94,6 → 194,2 |

Os arquivos ficam em `chars/`, `motif/` e `stages/` porque o launcher só baixa essas pastas.

## Como foi feito

- `python3 ferramentas/converter_musicas.py [faixa]`: corta o silêncio da gravação de tela, iguala tudo em -14 LUFS,
  acha o loop (fim e começo em batidas, longe do corte e do fade da gravação, onde os 8 s que levam a cada ponto soam
  mais parecidos, acerto fino na amostra), assa um crossfade de 120 ms entre o fim do loop e o trecho que leva ao
  começo e corta o arquivo no fim do loop. Grava `musicas/loops.json` com o `loopstart` (amostras de 44,1 kHz).
  Requer ffmpeg e `pip install librosa soundfile`.
- Os geradores leem `musicas/loops.json`: `gerar_layout.py` (`title.bgm.loopstart`, `select.bgm.loopstart`),
  `gerar_cenario.py` (`bgmloop`/`bgmloopstart` quando `"musica"` do `cenario.json` aponta para uma faixa de lá, por
  exemplo `"musica": "musicas/cristo.ogg"`) e `gerar_pengaro.py` (`musica_despertar_cns()`, usado por todos os
  lutadores do kit). Não precisa de `loopend`: o arquivo termina no fim do loop.
- Despertar (`musica_despertar_cns()` no `[Statedef -2]`): ao entrar no estado 2000 (ou com `var(20) > 0`, caso do
  endiabrado pela seleção), `ModifyBGM` baixa a música do cenário a cada tique por 45 tiques (0,75 s); no fim,
  `PlayBGM` toca `despertar.ogg` da pasta do lutador com o `loopstart`. Quando o Despertar acaba, `PlayBGM source =
  "stagedef."` (prefixo vazio do `[Music]` do cenário) volta a do cenário, a não ser que o oponente esteja desperto.
  `var(51)` = estado da música (0, 2 baixando, 1 boss), `var(52)` = tiques do fade. O round seguinte já começa com a
  do cenário (o motor troca sozinho).

## Testes

- `python3 ferramentas/testar_musica.py [--lutador pengaro]`: luta na Maria Fumaça e registra o `bgmVar` tique a
  tique: a do cenário toca, baixa de 100 a 0 em 45 tiques, entra `chars/pengaro/despertar.ogg`, e a do cenário volta
  quando o Despertar acaba.
- `python3 ferramentas/testar_musica.py --volta`: espera o fim da Maria Fumaça e confere que o motor volta para o
  `loopstart` (deu 2355712 → 982852, isto é, 981316 mais um bloco de áudio).
- Emendas medidas (fluxo espectral na volta / percentil 95 da música): de 1,0 a 1,6, o mesmo de uma batida comum.
  Ninguém ouviu ainda: o som da nuvem é `dummy`. **Falta ouvir a volta de cada loop umas três vezes no PC.**

## Em aberto (perguntado ao Breno na #33)

- Katiara e Deus Motoboy (Gbzin) sem música; faixa de vitória/game over.
- Pengaró (0:55) e Maria Fumaça (1:00) são curtas: se o Breno regravar inteiras, rode o conversor de novo.
