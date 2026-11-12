# Aura animada no Blender a partir do desenho aprovado (teste: asa do Hazak)

Ideia: não redesenhar. O desenho do conceito vira textura de uma malha com ossos; o Blender só entorta. Fogo,
notas, gotas e brasa são camadas em Python por cima, todas em laço. Saída: PNGs 360x200, alfa 0/255, 15 cores fixas.

## Rodar (nesta ordem, dentro desta pasta)

    python recortes.py
    C:/Dev/Tools/Blender/blender-4.5.15-windows-x64/blender.exe -b --python rig_asa.py -- <esta pasta>
    python medir_pontos.py        # chicote: fase e curso de cada junta -> chicote.json
    python compor.py              # camadas/, medidas.json, tira*.png, asa_blender.mp4, asa_comparacao.mp4

Para afinar o movimento sem renderizar: acrescente `so_pontos` no fim da linha do Blender (1 s) e rode `medir_pontos.py`.
Tempo: Blender ~13 s, compor ~27 s. A versão anterior (antes do retoque) está em `v1/`.

## O que cada script faz

- `recortes.py` — tira o magenta (R>170, B>170, G<110; na aura, todo pixel com azul > verde é derrame), separa
  corpo, asas, coroa e chão. Pedaços soltos grandes ficam NA asa (silhueta do conceito); só as gotas finas saem.
  Fecha o que o corpo escondia: toco arredondado da raiz atrás do corpo (as duas asas se cruzam no meio) e buraco
  dos pés espelhando a própria faixa. Reforça os ossos de ouro por cima do desenho (`OSSOS_DESENHO`: polilinhas com
  largura, lidas do desenho com grade), porque osso de 12 px do conceito some na redução para 1/4.
- `rig_asa.py` — unidade = 1 px do jogo, câmera ortográfica, render 4x, textura Closest, Cycles 1 amostra.
  Malha em grade de 8 px só onde há desenho; pesos = 1/(distância ao osso+1,5)^3 nos 4 ossos mais próximos.
  A malha é FILHA da armação (o modificador de armação sozinho ignora mover/escalar o objeto armação).
  Animação por junta em `ANIM`: (amplitude, atraso em fração do ciclo, ondulação 2x, fase).
  Tremor de pena: dois modificadores Displace com ruído Clouds amostrado num vazio que anda em círculo (fecha o
  laço sozinho), com peso zero em cima dos ossos. Exporta `render/pontos.json` (posição de cada junta por quadro).
- `compor.py` — 4x -> 1x (média dos subpixels opacos, alfa por maioria), paleta fixa (14 cores do desenho + 1 escura
  de contorno), encaixe com histerese (pixel só troca de cor se a anterior deixou de servir), contorno queimado
  embaixo e dos lados, línguas de fogo na borda de cima, partículas presas aos pontos exportados.

## Regras que valem para qualquer aura

1. **Laço**: tudo é função periódica do quadro. Asa = N quadros; partículas e chão = 2N (não repetem a cada batida).
   Ruído ladrilhável de lado T rolando um número inteiro de voltas; nunca aleatório por quadro.
2. **Chicote**: a raiz gira pouco e cedo, cada junta adiante gira MAIS e mais TARDE. Atraso só na rotação não basta:
   a raiz tem a maior alavanca e domina a ponta. Conferir em `chicote.json` a fase da POSIÇÃO da ponta.
3. **Nada parado**: `medidas.json` tem `pixels_que_nunca_mudam` por camada; tem que dar ~0.
4. **Passo por quadro** da ponta abaixo de ~3 px (senão pica): mais quadros com menos tiques, não menos amplitude.
5. **O que é fino some em 1/4**: ossos, gotas, contorno. Reforçar no recorte (ossos) ou desenhar direto em 1x (gotas).
6. Olhar `tira_sem_corpo.png`: os remendos escondidos aparecem ali.

## Adaptar para outra aura

Troque `SRC`, as caixas de recorte e `OSSOS`/`ANIM`; o `compor.py` quase não muda (troque `PONTAS`/`GOTAS`).

- **Garanhão** (cavalo de fogo): espinha pescoço->cabeça, 4 pernas de 3 segmentos, crina e rabo em cadeias de 4-5
  ossos com atraso crescente (são o chicote). Galope = duas ondas defasadas nas pernas + sobe-e-desce do tronco.
- **Leque**: um osso por vareta saindo do mesmo pivô; `ANIM` com amplitude crescente da vareta de dentro para a de
  fora e atraso por vareta (abre em cascata). Pano entre varetas = pesos repartidos, como a membrana da asa.
- **Paredão** (muro de som/fogo): sem rotação grande. Colunas de ossos verticais com onda viajando de lado
  (mesma amplitude, fase = posição x) + Displace mais forte. O grosso do movimento vem do `compor.py`.
- **Coluna de fumaça**: uma cadeia vertical de 6-8 ossos, onda em S subindo (atraso cresce com a altura), escala
  crescendo para cima; Displace forte e textura rolando para cima no `compor.py`. Aqui o rig é o de menos.

## Limites conhecidos

Não foi testado dentro do jogo (SFF/AIR/Explod, camadas, borda da tela, barras de vida). Só a pose parada de
frente. A aura ocupa quase a tela inteira de largura. Ainda não existe a folha de 8 quadros do ChatGPT: o vídeo
de comparação mostra o desenho parado só como referência.
