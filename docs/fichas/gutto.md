# Gutto (id técnico `gutto`)

Ficha no modelo da seção 10 de [`docs/regras-dos-lutadores.md`](../regras-dos-lutadores.md). **Montado (forma normal) em 2026-11-06.** Nasceu do áudio
do Breno de 2026-11-06 (transcrito com WhisperX, que erra em trechos; o que está marcado *(confirmar)* é interpretação).
As fotos de referência do Gutto ainda vão chegar e mandam na aparência. Arte no **mesmo estilo do Pengaró**: sprite 2D
de SNES/arcade desenhado à mão, nunca 3D pixelizado.

## Aparência (referência v3, 2026-11-06)

Folha-referência em `sprites/gutto/quadros/folhas/referencia_idle.png` (guarda de Muay Thai quicando, 8 quadros). Feita no
chat "Gutto" do ChatGPT a partir de duas fotos do Breno (corpo inteiro e rosto), no estilo do Pengaró. **Base de Muay Thai
com a postura clássica** (em pé, mãos altas, quicando no pé da frente), como a do Joe no KOF: só a postura, nada do visual
nem da arte de nenhum personagem existente (regra do projeto).

- Pele marrom escura; cabelo curto e crespo; bigode grosso com barba rala; olhos grandes e redondos; corpo forte.
- **Roupa característica de Muay Thai** (pedido do próprio Gutto): sem camisa, calção de cetim preto com cós largo branco
  e listra branca em cada lado (liso, sem logo), ataduras brancas, **braçadeiras de corda (prajioud)** nos dois bíceps,
  descalço, sem faixa na cabeça.
- Histórico: a v1 saiu clara demais e com detalhes vermelho e azul; a v2 (camisa branca de gola e mangas pretas, em
  `referencia_idle_v2_camisa.png`) acertou pele e rosto; a v3 trocou a camisa pela roupa de Muay Thai.

## O que o Breno disse no áudio

- É **lutador de Muay Thai**. Ataques padrão de Muay Thai, com **low kick**; "só chute" (chutes, joelhadas e cotovelos).
- **Beijinho**: um golpe de beijo, bom de ver, com **uma segunda variação** *(confirmar o que muda: alcance, trajetória ou
  efeito)*. Faz o papel de **projétil**.
- **Teleporte diferente**, de Muay Thai: levanta a perna numa ginga e dá uma "metidinha" (empurrão de pé) para a frente,
  e **aparece atrás do oponente** do nada. É o golpe de ir para trás do oponente (regra F).
- **Endiabrado (Despertar): cara de cavalo.** Fica com a cabeça de cavalo, **bufando**.
  - Chute giratório que parece **coice de cavalo**.
  - **Carrinho** (carrinho de futebol) "igual a Satanás": golpe baixo, de deslize.
  - **Corre no modo cavalo**: corrida mais rápida, galope.
- Tom: resenha entre amigos. Vale a regra do jogo: resenha pesada pode; nada de piada de escravidão nem do estereótipo da
  mulher loira.

## Ficha (proposta; ajusto quando as fotos chegarem)

**Estilo de luta:** Muay Thai: chutes baixos e altos, teep, joelhada e cotovelo; pressão e entrada rápida.
**Personalidade / falas:** a definir pelo Breno (áudios depois).
**Cores e paleta:** a partir das fotos. Altura-alvo: escala do arcade, **112 px** (normal), como o Pengaró.
**Efeitos (pixelfx e recolor):** `hit-spark` e `crit-hit` nos chutes; `heavy-landing` no carrinho; fumaça/vapor do
nariz (bufando) no Endiabrado; rastro de poeira no galope.

### Correntes (3 golpes + finalizador)

| Botão | 1º | 2º | 3º | Finalizador (derruba) |
|---|---|---|---|---|
| x | jab | direto | gancho | cotovelo giratório |
| y | cotovelo | cotovelo de cima | joelhada | joelhada voadora |
| a | low kick | low kick alto | teep | chute giratório baixo |
| b | chute alto | chute duplo | chute giratório | **chute de coice** |

### Kombos de assinatura (4), Especiais (8), Agarrões (3), Supers (2)

A preencher depois das fotos, mantendo no kit o que veio do áudio:

| Do áudio | Papel no kit |
|---|---|
| Beijinho (2 variações) | projétil (um dos 2 projéteis; o outro deve ter papel diferente) |
| Teleporte de Muay Thai | ir para trás do oponente, chega virado (regra F) |
| Low kick | golpe baixo/de chão |
| Agarrão de Muay Thai | clinch com joelhadas (agarrão em pé); agachado e o de lore a definir |

### Despertar: Endiabrado (cara de cavalo)

Ativação: barra cheia + x + y. Cara de cavalo, bufando; corrida de galope; chute giratório vira coice; carrinho de
Satanás. Regra 4: pelo menos 2 correntes novas, 6 normais novos, 4 especiais exclusivos (1 projétil novo), 1 kombo novo
e 1 super exclusivo. **Arte redesenhada**, não só recolorida.

## Estado (2026-11-06)

- **Forma normal pronta:** 27 folhas desenhadas no estilo do Pengaró, cortadas por `animar_folha.py` (`LUTADOR=gutto`) e montadas
  por `ferramentas/gerar_gutto.py`. O robô de teste (`testar_pengaro.py --lutador gutto`) passa 126 verificações.
- **Provisório:** `derrota`, `lata`, `despertar_a` e `despertar_b` são cópias de outras folhas e as 8 poses do `endiabrado` são as
  normais escurecidas (`ferramentas/provisorios_gutto.py`, `PROVISORIAS.txt`). O ChatGPT Plus bloqueou imagens por 10 horas.
- **Falta:** as 5 folhas verdadeiras, as folhas `e_<golpe>` da cabeça de cavalo (uma por movimento), o retrato de seleção, o
  projétil do Beijinho em arte própria (hoje é um coração em código) e os áudios.

## Estado (2026-11-07)

- As 5 folhas provisórias viraram arte de verdade: `derrota`, `lata`, `endiabrado` (8 poses com cabeça de cavalo),
  `despertar_a` e `despertar_b`. `animar_folha.py` reduz `lata` e `derrota` (vieram 12% maiores) e tira os fiapos de magenta
  da fumaça das folhas do cavalo. O Despertar passou a usar o cavalo do Gutto (antes lia as poses do Pengaró).
- Filmado: a transformação aparece. O robô passa 126 verificações. Ainda não jogado por uma pessoa.
- **Falta:** as folhas `e_<golpe>` (hoje todo golpe do Endiabrado cai numa das 8 poses), efeitos próprios do Gutto (ainda
  usa os violeta do Pengaró), retrato de seleção, projétil do Beijinho em arte própria e os áudios.

## Retomar e ver (nota de 2026-11-06, noite)

**Ver o Gutto:** `git pull` na branch `mugen`, depois dois cliques em `ferramentas/Jogo de Luta.bat` (ele baixa o Gutto junto) e
escolha o Gutto na seleção. Os quadros e as folhas estão em `sprites/gutto/quadros/`; o personagem pronto em `chars/gutto/`.

**Retomar a arte (o ChatGPT Plus libera imagens de novo às 07:49 de 2026-11-07):**

1. Chat "Gutto" no ChatGPT (conta do Breno): `chatgpt.com/c/6aee6f73-fa5c-83e8-a30f-88f87f91425b`, referência
   "Sequência de Guarda Muay Thai em Pixel Art" na biblioteca (a v3 do Gutto).
2. Folhas que faltam, com os pedidos prontos em `ferramentas/folhas_gutto.py` (`python ferramentas/folhas_gutto.py <nome>`):
   `derrota`, `lata`, `endiabrado`, `despertar_a`, `despertar_b`. Depois uma folha `e_<golpe>` por movimento, nos mesmos 8 tempos,
   com a cabeça de cavalo (veja "Formas transformadas" em `docs/como-trabalhar.md`).
3. Salvar em `sprites/gutto/quadros/folhas/<nome>.png` (`ferramentas/baixar_folhas.py gutto` extrai o pacote do navegador) e apagar a
   cópia provisória correspondente (e `PROVISORIAS.txt` quando não sobrar nenhuma).
4. Cortar: `LUTADOR=gutto BLENDER="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" python ferramentas/animar_folha.py <nomes>`.
5. Gerar e testar: `python ferramentas/gerar_gutto.py` e `python ferramentas/testar_pengaro.py --lutador gutto`.

## Passos

1. Chegar as fotos de referência; desenhar a **folha-referência** (ChatGPT, chat "Gutto", estilo do Pengaró).
2. Conferir personagem e cor; depois uma folha por movimento (8 quadros, fundo magenta `#FF00FF`).
3. `ferramentas/gerar_gutto.py` (a criar, no molde do `gerar_pengaro.py`), verificador e teste do robô.
