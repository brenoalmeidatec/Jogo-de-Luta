# Bíblia de arte

O que mantém os lutadores com cara de um jogo só. Vale para todo lutador novo e para qualquer folha refeita. As regras de
jogo ficam em [`regras-dos-lutadores.md`](regras-dos-lutadores.md); o jeito de produzir, em
[`como-trabalhar.md`](como-trabalhar.md).

## Estilo

- Sprite desenhado de SNES/arcade dos anos 90, com contorno escuro e sombreado em blocos. Nunca 3D pixelizado nem
  render suave.
- Proporção de KOF: escala 1 no `.cns`, figura em pé com cerca de 110 de 180 de altura de tela.
- Vista de lado, virado para a direita, pés no chão quando o golpe não sai do chão.
- Folha de 8 quadros em fila, células iguais, figura inteira dentro da célula, fundo magenta `#FF00FF` liso, sem faixa
  branca ou cinza, sem texto e sem sombra no chão.
- Toda folha alinhada pelo **centro do tronco** no eixo do lutador (`animar_folha.py`). As caixas de golpe são centradas
  no eixo, então o tronco no eixo faz golpe e desenho baterem.
- Marca e texto proibidos em garrafa, lata ou roupa.

## Pengaró

| | Normal | Endiabrado (Despertar) |
|---|---|---|
| Pele | morena, tom médio (matiz perto de 23°) | marrom-escura arroxeada; corpo inteiro, rachaduras violeta acesas no peito |
| Olhos | normais | violeta brilhante, sem pupila |
| Cabelo | escuro, curto | mais comprido e revolto, pontas violeta, dois chifres curtos de fumaça violeta |
| Tronco | nu | casaco de mestre preto sem manga, aberto no peito, friso dourado, forro roxo, barra rasgada até a canela |
| Calça | branca, listras verde e amarela | preta e larga, barra em brasa violeta |
| Faixa | teal, cordão amarelo | corda grossa trançada ouro e violeta, duas pontas com pingente até o joelho |
| Perna | caneleira verde escura | algema de ferro com 3 elos de corrente partida nos dois tornozelos |
| Mão de trás | garrafa de whisky âmbar, rótulo creme | vazia; algema com corrente partida e bracelete de ouro nos dois braços |
| Efeitos | whisky: âmbar e dourado (`WHISKY` em `gerar_pengaro.py`) | sombra: violeta e preto (`SOMBRA`, `SOMBRA_ESCURA`) |

O endiabrado é o boss final do conceito aprovado em 2026-11-11 (`sprites/pengaro/quadros/folhas_arcade/e_conceito.png`);
a aura dele (coluna de fumaça violeta-preta, anel de sombra no chão rachado, elos e pedras flutuando) é efeito à parte.

Referências: "Socos" na biblioteca do ChatGPT (normal) e o arquivo `e_conceito.png` (endiabrado). Meça o matiz da pele das folhas
novas: acima de 26° ele está desviando para o amarelo.

## Efeitos

- **Sem pixelfx no Pengaró** (o Breno não gostou). Efeito é desenhado como lutador: folha de 8 quadros no ChatGPT, estilo
  pixel art de arcade, **fundo verde `#00FF00`** (o roxo da sombra some no magenta), salva como
  `sprites/<lutador>/quadros/folhas/fx_<nome>.png`. `python ferramentas/efeitos_folha.py <lutador>` recorta, põe na escala
  do jogo e cria 2 quadros do meio por intervalo (fluxo óptico): 8 desenhos viram 22, bem animados.
- Pixel opaco, sem mistura de cor: soma de dourado sobre o palco azul vira rosa.
- Cada forma tem a sua cor e o seu efeito (`FX_PENGARO` em `gerar_pengaro.py`). A faísca de acerto é do motor e não passa
  pela troca do Despertar: o HitDef escolhe a do endiabrado pelo `var(20)` (ação + 30).
- O efeito de golpe nasce no elemento em que a caixa de golpe liga, na caixa do golpe. Nada de efeito solto no meio da tela.
- Nada de escudo em grade: parece rede de futebol.
- Endiabrado com corpo inteiro, sem buraco nem membro solto; a sombra que se mexe é a aura (efeito à parte). Anexe a
  referência em **toda** folha: sem isso, em 30 folhas seguidas ele virou marrom.

## Lutador novo

1. Defina na ficha a tabela de cima: pele, roupa, objeto, cor dos efeitos de cada forma.
2. Gere a folha-referência e guarde na biblioteca do ChatGPT com um nome fácil de buscar.
3. Escolha a rampa de cor dos efeitos dele, diferente das que já existem.

## Estilo arcade anos 90

**É a regra do jogo desde 2026-11-10** (definida pelo Alisson e confirmada pelo Breno): toda folha nova de qualquer
lutador, efeito ou transformação sai neste estilo, e onde ele contrariar o que está acima nesta bíblia, vale ele.

Alvo: pixel art de lutador de arcade dos anos 90, pelas **convenções do gênero** (paleta curta, contorno colorido,
sombra em blocos, pose de contato exagerada). Nunca um personagem, sprite, pose-assinatura, nome ou golpe de jogo
comercial, e nada de imagem de jogo comercial no repositório nem anexada no ChatGPT: a única referência é a folha do
próprio lutador. Escala e proporção não mudam; muda cor, contorno, sombra e pose de contato. Estado em 2026-11-10: só o
`soco` do Pengaró passou pelo pipeline (piloto), nada disso está ligado no gerador nem foi testado na sandbox.

Por lutador (paleta, prompt base, folhas com MOTION, kit, problemas): [`arcade/pengaro.md`](arcade/pengaro.md),
[`arcade/gutto.md`](arcade/gutto.md), [`arcade/raiclaven.md`](arcade/raiclaven.md), [`arcade/hazaki.md`](arcade/hazaki.md).
Fila de geração no ChatGPT, com o prompt pronto de cada folha: [`arcade/fila.md`](arcade/fila.md).

### Regras

Medidas no **quadro final**, depois do Blender: os quadros do meio criam cor nova (na piloto, 42 de 42 falhavam a regra 1
antes de re-quantizar). As faixas de matiz da regra 3 são as do Pengaró; cada lutador pode deslocá-las para a pele dele
(o Raiclaven usa sombra 0–10°, médio 13–18°, luz 21–26°, brilho 32–40°), e o documento dele diz quais valem.

| # | Regra | Como medir | Passa se | Quem mede |
|---|---|---|---|---|
| 1 | Paleta fixa de 15 cores + transparente para todas as folhas normais | cores únicas por quadro | <= 15, todas de `paleta_arcade.json` | `conferir_arte.py` |
| 2 | Paleta somando 15 por papel (Pengaró: pele 5, calça 3, faixa 3, cabelo 2, garrafa 2; contorno dentro dos grupos) | tabela da paleta | soma 15 | olho no JSON |
| 3 | Rampa com matiz deslocado: sombra da pele ao vinho, luz ao creme | matiz HSV de cada tom | sombra 5–15°, médio 21–26°, luz 30–40° | `conferir_arte.py` |
| 4 | Branco (ou preto) da roupa com sombra fria | matiz e saturação da sombra | 220–270°, saturação >= 10% | `conferir_arte.py` |
| 5 | Contorno de 1 px colorido: vinho na pele, azul-roxo escuro na roupa | borda externa | nenhum canal < 20; 1 px | `conferir_arte.py` |
| 6 | Sel-out: contorno some ou clareia no lado da luz | borda do lado da luz | mais claro que o do lado da sombra | olho |
| 7 | Sem dithering, sem ruído, sem AA externo | pixel diferente dos 4 vizinhos | < 2% da figura | `conferir_arte.py` |
| 8 | Músculo em 2–3 planos grandes; abdômen em 6 blocos | folha de contato a 1x | sem veia, sem gomo a mais | olho |
| 9 | Brilho duro de 1–3 px (testa, ombro, peito, nó dos dedos, canela); uma faixa no cabelo | zoom 3x | blocos sem degradê nem halo | olho |
| 10 | Contato alonga: punho ou pé 10–20% maior, ombro ou quadril à frente, tronco gira | ponta do membro no contato x quadro 1 | +10% a +20% | `conferir_arte.py` (grosseiro: o antebraço em guarda entra na altura) |
| 11 | Antecipação visível no quadro 2; recuperação mais longa que o ativo | silhueta e contagem de desenhos | quadro 2 muda > 5%; volta >= 3 desenhos no forte | `conferir_arte.py` (`--forte`) |
| 12 | Roupa reage: calça abre no chute, pontas de faixa ou cordão atrasam 1–2 quadros | quadros vizinhos | dobra e atraso presentes | olho |

O ChatGPT não entrega 15 cores: entrega pose e volume. A paleta entra depois, por quantização sem dithering para a
paleta fixa, com retoque à mão onde sobrar chiado. Transformações (Surto, Diabo Loiro): troca de paleta sobre
o mesmo desenho onde der; folha própria só onde o desenho muda. O endiabrado do Pengaró muda de roupa inteira (boss
final) e por isso é todo em folha própria. Índice de paleta compartilhado (lâmina e dente, por
exemplo) não pode ser trocado sozinho: o que precisa mudar de cor isolado vai desenhado.

### Pipeline

As folhas novas ficam em `sprites/<lutador>/quadros/folhas_arcade/<folha>.png` e a saída em
`sprites/<lutador>/quadros_arcade/<folha>/` (`00..07.png` e `meio/`), paralela a `quadros/`: o jogo não muda até o
gerador ser ligado. Escala do jogo: tela 360x260, pés em 180,220 (`animar_folha.poses(..., amplia=1)`), a mesma altura do
soco atual.

```bash
python ferramentas/quantizar_folha.py --montar-paleta soco   # uma vez por lutador: mede a folha e grava paleta_arcade.json
python ferramentas/quantizar_folha.py soco                   # recorta, quantiza em Lab sem dithering, contorno de 1 px
python ferramentas/animar_folha.py --arcade soco             # quadros do meio pelo Blender, só em quadros_arcade/soco/meio/
python ferramentas/quantizar_folha.py soco --meio            # obrigatório: re-quantiza os quadros do meio
python ferramentas/conferir_arte.py soco --relatorio conferir_soco.md   # PASS/FAIL por quadro e por regra
```

- `LUTADOR=<nome>` escolhe o lutador, como no `animar_folha.py`. Hoje `quantizar_folha.py` só tem os papéis do Pengaró e
  `conferir_arte.py` só as faixas dele: Gutto, Raiclaven e Hazaki precisam dos papéis próprios antes da primeira folha, e
  o Hazaki ainda precisa de um gerador que leia folhas.
- `paleta_arcade.json` é dado: cada cor tem papel, valor medido e valor ajustado, e pode ser retocada à mão. Rode
  `conferir_arte.py` de novo depois de qualquer retoque.
- `conferir_arte.py soco --pasta quadros` mede a arte atual, para comparar. `--forte` cobra a regra 11 como golpe forte.
- `animar_folha.py --arcade` ainda **não aceita loops** (`parado`, `ginga`, `anda`): as folhas de loop só passam pelo
  quantizador até isso mudar.
- **Ligado no Pengaró desde 2026-11-11:** `ginga` e `anda` (loops, em `LOOPS` do gerador, só desenhos segurados) e
  `levanta` (em `ARCADE`). O resto ainda é a arte antiga. Para ligar outra folha: `quantizar_folha.py <folha>`, olhar
  a folha de contato, pôr o nome em `ARCADE` e conferir a caixa de golpe.
- Ligar no jogo: o `gerar_<lutador>.py` lê `quadros_arcade/<nome>` quando a pasta existir (os nomes de arquivo já são os
  mesmos); o `.sff` já é indexado, então a paleta pode virar a paleta do SFF e preparar a troca da transformação.

### Prompt base

Um por lutador, no documento dele, sempre neste formato. Troque só o bloco MOTION e anexe a referência em toda folha.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: <descrição fiel ao que está na folha: rosto, cabelo, pele,
roupa, objeto e de que lado ele fica>.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; <a roupa clara ou escura> gets cool lilac-blue shadows, never grey or beige. 1-pixel colored outline
(dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3
pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited
palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: <bloco da folha>
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

Ao escrever o MOTION: o gerador lê os quadros por **índice fixo** (quase sempre o 5 é o contato). O MOTION novo mantém
o contato, o arremesso e a pose de recuperação nos mesmos quadros da folha atual, senão a arte deixa de bater com a caixa
de golpe. Contato com o membro 15% maior; recuperação em pelo menos 3 desenhos, voltando aos poucos (na piloto, o quadro 7
já era guarda e o braço estalou em 1 tick); quadro 1 e 8 com a mesma mão e a mesma pose da folha de base.

### Critério de aceite

Uma folha por vez; as 4 mais vistas de cada lutador primeiro, e só passa para a próxima com esta aprovada.

1. Folha crua: 8 quadros inteiros, magenta liso, mesmo chão, virado para a direita, personagem reconhecível ao lado da
   referência; matiz mediano da pele na faixa do lutador (Pengaró 21–26°; acima disso está desviando para o amarelo).
2. Depois de quantizar, do Blender e do `--meio`: regras 1, 3, 4, 5 e 7 passam no `conferir_arte.py`; 10, 11 e 12 no
   olho, com o número do script como apoio.
3. Quadro 1 e 8 emendam com o parado (ou o agachado) sem salto no vídeo do `video_golpe.py`. O limite de salto de 0,45
   não pega o estalo de 1 tick: confira a tira de ticks.
4. Vídeo curto na sandbox conferido tick a tick, como manda a [`conferencia-de-golpe.md`](conferencia-de-golpe.md), e
   visto por uma pessoa antes de subir.
