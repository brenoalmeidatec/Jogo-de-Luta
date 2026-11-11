# Aura animada no Blender a partir do desenho aprovado

Ideia: não redesenhar. O desenho do conceito aprovado vira textura de uma malha com ossos; o Blender só entorta. Fogo,
fumaça, raio, gotas e partículas são camadas em Python por cima, todas em laço. Saída: camadas PNG 360x200, alfa 0/255,
15 cores fixas, pé do lutador em (180,190), mais um `aura.json`. Padrão aprovado pelo Alisson em 2026-11-11 depois do
teste com a asa do Hazak.

## Arquivos (`ferramentas/aura_blender/`)

- `comum.py` — tudo que serve para qualquer aura: recortes, malha, pesos, animação, redução, paleta, fogo, partículas,
  exportação, vídeo, tira e medidas. É importado pelo Python comum e pelo Python do Blender (funções `bl_*`).
- `hazak_asas.py` — a aura do Hazak (asas, coroa, brasa, notas, gotas). É a referência de nível.
- `aura_modelo.py` — molde comentado de uma aura nova (uma peça com ossos, fogo na borda, fagulhas).

## Rodar

    python ferramentas/aura_blender/hazak_asas.py <pasta de trabalho>                  # tudo (~1 min)
    python ferramentas/aura_blender/hazak_asas.py <pasta de trabalho> pontos chicote   # só o movimento (1 s), para afinar
    python ferramentas/aura_blender/hazak_asas.py <pasta de trabalho> compor instala   # refaz só as camadas

Etapas, nesta ordem: `recortes` (corta o conceito) → `rig` (abre o Blender em segundo plano, saída em
`<pasta>/blender.log`) → `chicote` (mede as juntas) → `compor` (camadas, medidas, tiras, vídeo) → `instala` (copia
para `sprites/<id>/aura/`). A pasta de trabalho fica FORA do repositório (render bruto, vídeo, tiras). O Blender é o de
`C:/Dev/Tools/Blender/blender-4.5.15-windows-x64/blender.exe`; outro caminho vai na variável de ambiente `BLENDER`.
Precisa de numpy, opencv, scipy, Pillow e ffmpeg no Python comum.

## Criar uma aura nova em 10 passos

1. **Conceito.** A textura é o conceito aprovado (fundo magenta), em `sprites/<id>/quadros/folhas_arcade/`. Não se gera
   imagem nova. Ele precisa de uma vista só com o corpo e uma com corpo + aura.
2. **Copie o molde**: `aura_modelo.py` → `<lutador>_<aura>.py` e preencha só o bloco `DECLARE`.
3. **Meça o conceito** num editor de imagem: colunas da vista sem aura (`CORPO_X`) e com aura (`AURA_X`), caixa de cada
   peça, eixo do corpo e y do chão na vista com aura. `Tela(cx, chao, escala)` com escala = altura do corpo no jogo
   (112 px) / altura no conceito.
4. **Rode `recortes` e olhe `p_recortes.png`.** O corpo é achado sozinho na vista com aura (`casa_corpo`; nota abaixo
   de ~0,9 = a pose mudou entre as vistas, confira). O que o corpo escondia é remendo: feche com `discos` +
   `remenda_clone`/`remenda_vizinho` e deixe ATRÁS do corpo. Traço fino (osso, vareta, corrente) some em 1/4: reforce
   com `reforca_linhas`. Gota fina sai do recorte e vira partícula.
5. **Ossos** (`OSSOS`): em px do conceito, uma cadeia de 3 a 5 juntas por ramo, da raiz para a ponta. A cabeça do
   primeiro osso é o pivô da peça.
6. **Animação** (`ANIM`): por junta, (amplitude, atraso, 2º harmônico, fase). A raiz gira POUCO e CEDO; cada junta
   adiante gira MAIS e mais TARDE. Mesma amplitude com atraso zero em todas é placa rígida girando. A peça inteira
   também respira (`bl_anima_objeto`). Peça gêmea: ossos espelhados, `sinal=-1`, alguns quadros de fase.
7. **Afine sem renderizar**: `pontos chicote` (1 s). `fase_q` tem de crescer da raiz para a ponta e `passo_max` ficar
   abaixo de ~3 px. Passou de 3? Mais quadros (`N`) com menos tiques, não menos amplitude.
8. **Camadas procedurais** (em `compor`): paleta do próprio desenho + cor escura de contorno; `encaixa_seq` (histerese);
   `contorno`; `linguas` na borda; `cintila` no miolo; partículas com `semeia` + `emite`, nascendo nas pontas exportadas
   pelo Blender, em quadros espalhados. Laço das partículas e do chão = 2N, para não repetirem a cada batida.
9. **Rode tudo e OLHE**: `tira.png` (o ciclo), `tira_consecutivos.png` (fervura), `tira_sem_corpo.png` (remendos),
   `aura.mp4` quadro a quadro. Em `medidas.json`: `pixels_que_nunca_mudam` ~0 em toda camada,
   `pares_consecutivos_iguais` 0, `emenda` do tamanho de `vizinhos_da_emenda`.
10. **`instala`**, confira `sprites/<id>/aura/aura.json` (ordem das camadas e plano atrás/à frente), anote no LOGBOOK,
    commit.

## `aura.json`

    {"formato": 1, "lutador": "hazaki", "aura": "asas",
     "tela": [360, 200], "pe": [180, 190], "tiques_por_quadro": 2, "alfa": "0 ou 255",
     "arquivo": "{nome}_{quadro:02d}.png",
     "camadas": [{"nome": "chao", "quadros": 96, "plano": "atras", "o_que": "..."}, ...],
     "paleta": [[r, g, b] x 15, da mais escura (contorno) à mais clara],
     "nota": "...", "gerado_por": "ferramentas/aura_blender/hazak_asas.py"}

`camadas` está na ORDEM DE DESENHO (a primeira fica mais ao fundo); `plano` diz se a camada vai atrás ou à frente do
corpo. Cada camada roda no seu próprio laço: quadro = (tique // tiques_por_quadro) % quadros. Todo PNG tem o tamanho de
`tela` e o pé do lutador cai em `pe`.

## Regras que valem para qualquer aura

1. **Laço**: tudo é função periódica do quadro. Ruído ladrilhável rolando um número inteiro de voltas (`Campo.fecha`
   confere); nunca aleatório por quadro.
2. **Chicote**: atraso só na rotação não basta, porque a raiz tem a maior alavanca e domina a ponta. Confira em
   `chicote.json` a fase da POSIÇÃO da ponta.
3. **Malha filha da armação**: `bl_malha_com_ossos` já faz. O modificador de armação sozinho ignora mover ou escalar o
   objeto armação e a peça vira placa solta.
4. **Nada parado**, nenhuma camada. **Passo por quadro** da ponta abaixo de ~3 px.
5. **Histerese** no encaixe da paleta (`encaixa_seq`), senão o miolo ferve. Folga alta demais gruda a cor na tela.
6. **Contorno escuro** como o dos lutadores, embaixo e dos lados; em cima fica o fogo.
7. **O que é fino some em 1/4**: reforçar no recorte (ossos) ou desenhar direto em 1x (gotas, fagulhas).

## Ideias de rig para as outras auras

- **Garanhão** (cavalo de fogo): espinha pescoço→cabeça, 4 pernas de 3 segmentos, crina e rabo em cadeias de 4-5
  ossos com atraso crescente. Galope = duas ondas defasadas nas pernas + sobe-e-desce do tronco.
- **Leque**: um osso por vareta saindo do mesmo pivô; amplitude e atraso crescendo da vareta de dentro para a de fora
  (abre em cascata). Pano entre varetas = pesos repartidos, como a membrana da asa.
- **Paredão** (muro de som/fogo): sem rotação grande. Colunas de ossos verticais com onda viajando de lado (fase =
  posição x) + tremor mais forte. O grosso do movimento vem das camadas procedurais.
- **Coluna de fumaça**: cadeia vertical de 6-8 ossos, onda em S subindo, tremor forte e ruído rolando para cima.

## Limites conhecidos

- Não foi testado dentro do jogo (SFF/AIR/Explod, camadas, borda da tela, barras de vida). Só a pose parada de frente.
- A asa refeita com o `comum.py` não é idêntica bit a bit à do teste aprovado: chão, coroa e partículas saíram
  iguais; nas asas mudam ~13 pixels por quadro (de ~18 mil), porque os pesos passaram a ser calculados em precisão
  dupla. Nas tiras não se vê diferença.
- `derrame_quente` e `rampa_quente` só servem para aura de fogo/ouro. Aura fria usa `derrame_de_borda` e rampa montada
  à mão; esse caminho ainda não foi testado com um conceito de verdade.
- Os remendos (raiz atrás do corpo, buraco dos pés no chão) e os números de corte continuam escritos à mão por aura.
- Partículas com desenho próprio (a nota de dinheiro do Hazak) ficam no script da aura; no comum só há fagulha e gota.
- Um osso só gira no plano da tela; profundidade é fingida com escala. Não há deformação por curva nem física.
