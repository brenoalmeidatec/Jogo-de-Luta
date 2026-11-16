# Missão para o Alisson (2026-11-15): Pengaró pelo método do boneco de peças

Pedido do Breno: o Claude do Alisson refaz o **Pengaró (forma base)** pelo método novo do
[`estudo-animacao.md`](estudo-animacao.md). Leia o estudo inteiro antes de começar: ele explica por que os bonecos
deformam e de onde vem cada passo. **Se o Breno gostar do resultado, o método vira regra para todos os lutadores.**

O Breno pediu com todas as letras: **"quero bem feito"**. Esta missão vale mais pela qualidade do que pela quantidade.
Melhor três golpes impecáveis do que o lutador inteiro mais ou menos.

Siga as regras de sempre no que não contrariar esta missão: [`como-trabalhar.md`](como-trabalhar.md),
[`regras-dos-lutadores.md`](regras-dos-lutadores.md), [`biblia-de-arte.md`](biblia-de-arte.md) (estilo arcade anos 90
e as 12 regras), [`regra-alta-resolucao.md`](regra-alta-resolucao.md) e
[`conferencia-de-golpe.md`](conferencia-de-golpe.md).

## A ideia em uma frase

Hoje a IA desenha cada quadro do zero e reinventa o corpo a cada desenho (braço que estica, costas de outro tamanho,
terceiro braço). No método novo, **o Pengaró é desenhado uma vez só**, esse desenho vira um kit de peças, e todo quadro
sai dessas mesmas peças giradas e movidas, com retoque pixel a pixel nas juntas. O braço não tem como mudar de tamanho
porque é sempre o mesmo desenho.

Continua sendo sprite desenhado no estilo arcade. **Nada de modelo 3D nem 3D pixelizado** (o boneco 3D do PR #17 foi
rejeitado). O Blender, se usado, só deforma o sprite desenhado.

## Etapa 1: piloto (parar aqui e mostrar ao Breno)

Só três animações, feitas com todo o capricho:

1. **Parado** (a ginga, loop).
2. **Soco** (o jab, `[Statedef 200]`, `[Begin Action 200]` e o par endiabrado 10200 fica como está).
3. **Chute alto** (`chute_alto`).

### Passo 1: folha-modelo

- Monte a folha-modelo do Pengaró base: **perfil virado para a direita (a pose de guarda do parado), frente e costas**,
  os três na mesma escala, mesma altura e mesma linha de chão. Ponha também a paleta de 15 cores de
  `paleta_arcade.json` em quadradinhos ao lado.
- Parta do melhor desenho aprovado que já existe (a ginga arcade em `sprites/pengaro/quadros/folhas_arcade/ginga.png`
  e o soco). Frente e costas podem ser pedidas ao ChatGPT com a folha anexada, mas **saem medidas**: altura do topo da
  cabeça ao pé, largura dos ombros e da cintura iguais às do perfil (tolerância de 2%). O defeito "de costas mais baixo
  e largo" da #51 não pode aparecer aqui.
- Grave em `sprites/pengaro/pecas/folha_modelo.png`. **Garrafa de whisky na mão de trás em toda vista.**

### Passo 2: kit de peças

- Recorte o desenho do parado em camadas, **na resolução grande** (a da folha, boneco com ~500 px ou mais), para depois
  sair o 3x e o 1x direto dele, como manda a regra da alta resolução:
  cabeça, pescoço, tronco, quadril com a faixa, braço e antebraço de cada lado, cada mão, coxa, canela e pé de cada lado,
  garrafa, pontas da faixa.
- Cada peça tem uma **sobra escondida na junta** (o pedaço que fica por baixo da peça vizinha), senão abre buraco quando
  gira. Desenhe essa sobra, não estique.
- Peças que mudam de desenho e não de ângulo entram como **variantes**: punho fechado de lado, punho visto de frente
  (contato do soco), mão aberta, cabeça gritando, pé de lado e pé visto de cima. Peça cada variante ao ChatGPT como peça
  solta em cima da folha-modelo, e confira o tamanho contra a peça original.
- Grave em `sprites/pengaro/pecas/` (um PNG por peça + um `kit.json` com o ponto de junta de cada peça, a peça mãe e a
  ordem de camada).

### Passo 3: esqueleto e régua

- No `kit.json`, guarde o comprimento de cada osso medido no parado (ombro-cotovelo, cotovelo-punho, quadril-joelho,
  joelho-tornozelo, altura da cabeça, largura do ombro).
- Escreva um conferidor (por exemplo `ferramentas/conferir_pecas.py`) que mede todo quadro novo contra essa régua e
  **reprova** osso que mudou mais de 5%, com uma exceção marcada à mão: no quadro de contato pode passar até 15% no membro
  que bate (a regra 10 da bíblia), e só nele.
- Ele também compara a silhueta (altura e largura da figura) com o parado e acusa o quadro que fugir sem motivo.

### Passo 4: poses-chave montadas por código

- Um script (por exemplo `ferramentas/boneco_pecas.py`) monta cada pose a partir de uma lista de ângulos e posições por
  peça e cola as peças na ordem de camada.
- **Gire com RotSprite** (ou o algoritmo equivalente sem mistura de cor), nunca com rotação bilinear: rotação comum
  borra e cria cor nova. Depois de montar, re-quantize para a paleta fixa sem dithering.
- Para achar os ângulos, vale usar como guia a folha atual do golpe, um rascunho da IA ou um esboço: **o guia só dá a
  pose, o quadro final usa só as peças do kit**.
- Poucas poses, bem escolhidas (o estudo explica por quê):
  - **Soco:** guarda, preparo curto (ombro de trás recua, punho perto do queixo), **contato** (braço todo esticado, ombro
    da frente à frente, tronco girado, punho na variante de frente e até 15% maior), recuo em 2 desenhos voltando à
    guarda. São 4 a 5 desenhos.
  - **Chute alto:** guarda, joelho sobe (câmara), contato com a perna esticada e o tronco inclinado para trás, joelho
    volta, pé no chão. A calça abre no chute e as pontas da faixa atrasam 1 a 2 desenhos (regra 12).
  - **Parado:** 4 a 6 desenhos de respiração e balanço da ginga, a garrafa acompanhando, em loop sem salto do último para
    o primeiro.

### Passo 5: retoque pixel a pixel

- Toda junta montada ganha retoque: emenda de contorno, músculo que muda com o ângulo (o bíceps encurta quando o braço
  dobra), dobra da calça, sombra da peça de cima caindo na de baixo.
- O contorno segue as regras 5 e 6 da bíblia (1 px colorido, mais claro do lado da luz). Nada de contorno duplo onde
  duas peças se encontram.
- Pode ser feito por script em Python (Pillow) ou no Aseprite. Se der para instalar o Aseprite no PC do Alisson, use a
  casca de cebola para conferir quadro contra quadro; o [pixel-mcp](http://github.com/willibrandon/pixel-mcp) liga o
  Aseprite direto no Claude.

### Passo 6: tempo e quadros do meio

- **Nada dos 6 quadros do meio do Blender** nestas três animações. Cada desenho fica **segurado** alguns ticks; no
  máximo 1 quadro do meio, só onde o salto ficar feio, e feito com as peças, não por fluxo óptico.
- O soco tem que manter a **mesma frame data** de hoje: o HitDef liga em `Time = 4`, a caixa de golpe
  (`Clsn1 = 45, -276, 153, -192` no 3x) fica encostada no punho do desenho de contato, e a animação dura os mesmos
  16 ticks da `[Begin Action 200]`. Confira no `gerar_pengaro.py` quais índices de quadro o gerador lê (o contato do
  soco é lido por índice fixo) e entregue os desenhos nesses índices.
- O chute alto, do mesmo jeito, mantém tempo e caixa do que está no jogo.

### Passo 7: saída e prova

- Saída em pasta própria, **sem ligar no gerador e sem mexer no `.sff` da `mugen`**:
  `sprites/pengaro/quadros_pecas/<animação>/` (1x, 360x260, pés em 180,220) e
  `sprites/pengaro/quadros_pecas_hd/<animação>/` (3x, 1080x780).
- Rode o `conferir_arte.py` (regras 1, 3, 4, 5 e 7) e o conferidor de peças do passo 3 em todos os quadros: tudo PASS.
- Monte uma **folha de contato antes e depois**: a folha atual em cima, a nova embaixo, mesma escala.
- Grave **vídeos lado a lado** (atual à esquerda, novo à direita) das três animações, a 60 fps, mais a tira com todos os
  ticks (`ferramentas/video_golpe.py`). Para ver no jogo, use uma cópia de teste do lutador, como manda a
  [`conferencia-de-golpe.md`](conferencia-de-golpe.md), nunca o `.sff` da `mugen`.
- Poste folha de contato e vídeos na issue do Pengaró (#32) com o título "Piloto boneco de peças" e **espere o Breno**.

### Critério de aceite da etapa 1

- Nenhum osso muda de tamanho entre quadros além da régua; nenhum braço, mão ou garrafa a mais ou a menos.
- Rosto, cabelo, pele (matiz 21–26°), calça, faixa e caneleira idênticos em todo quadro, porque são as mesmas peças.
- O soco tem que parecer **mais forte** que o atual: preparo legível, contato com congelamento, volta sem estalo.
- Nada de borrão, cor nova, dithering ou contorno quebrado na junta (olhar em zoom 3x).
- Folha de contato e vídeo lado a lado na issue.

## Etapa 2: o resto do Pengaró base (só depois do ok do Breno)

Com o piloto aprovado, o mesmo kit faz o resto da forma base, começando pelas 10 folhas que a revisão da #51 mandou
redesenhar (`docs/anatomia-51/LEIA-ME.md`) e pelos golpes mais vistos: andar, agachar, defesa, chute baixo, soco
agachado, pulo, apanhar, queda e levantar, agarrão (com as costas da folha-modelo) e as vitórias. Para cada animação
nova que precisar de peça que não existe (pose de costas, agachado visto de lado), a peça entra no kit primeiro, medida
pela régua.

Só nessa etapa as animações novas são ligadas no `gerar_pengaro.py`, com o 3x pelo `hd.py`, o robô
(`python ferramentas/testar_pengaro.py --lutador pengaro`) sem falha e vídeo de cada golpe na issue antes de juntar na
`mugen`, como sempre.

O endiabrado fica de fora desta missão: ele tem roupa inteira própria e vai precisar de um kit próprio, feito do mesmo
jeito depois que o método for aprovado.

## Ao terminar cada etapa

Anote no `LOGBOOK.md` o que foi feito, o que não foi testado e quanto tempo levou cada animação (o Breno quer saber se o
método compensa para os outros lutadores).
