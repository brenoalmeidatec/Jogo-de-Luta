# Cenários animados

> Pedido do Alisson (2026-11-11): cenários de luta de Nazaré das Farinhas (o Cristo, a Maria Fumaça, a praça da
> prefeitura, a passarela), **animados**, nada estático. Este arquivo é o método: as medidas que a arte precisa ter,
> como o gerador monta o cenário e como se prova no motor. A base foi provada na sandbox com um cenário de teste
> desenhado por código (`stages/teste.def`); a arte dos quatro lugares ainda não existe.

## 1. Como o motor enxerga o cenário (medido na sandbox, IKEMEN GO v1.0.0)

- A janela é 1280x720, mas a **tela lógica é 320x180**: 1 px de arte = 1 px de lutador = 4 px na janela. O cenário usa
  `localcoord = 320, 180`, a mesma malha dos lutadores (`localcoord = 320,240`, escala 1). Conferido no filme: a linha do
  chão desenhada em y = 165 saiu em y = 660 da janela e a sola dos pés encosta nela.
- **Linha do chão: y = 165** (`zoffset`), a mesma do `stage0-720` (660/4). Sobram 15 px de chão abaixo dos pés.
- Lutador em pé: cerca de 110 px, cabeça em y ≈ 55. No começo do round ficam em x = 90 e x = 230 (centro ± 70).
- **Câmera:** anda `(largura_mundo − 320) / 2` para cada lado (224 px com o mundo de 768) e sobe até 40 px quando alguém
  pula (o pulo tem 80 px; a câmera segue 60% do que passar de 30 px). Sem zoom (`zoomin = zoomout = 1`).
- **Paralaxe:** cada camada tem um `delta`. Posição na tela = posição em repouso − câmera × delta. Delta 0 não anda (céu),
  1 anda junto com o chão, maior que 1 anda mais que o chão (frente). Conferido no filme: bateu com a simulação do gerador.
- O `.sff` do cenário é **SFF v2 com PNG de 32 bits (RGBA)**, sem paleta, o mesmo formato do layout (`layout_sff.py`). O
  motor aceitou. Não há limite técnico de cores; o limite é o estilo (seção 3).
- Movimento contínuo sai liso: o motor desenha com fração de pixel da janela (a nuvem anda de 1 em 1 px de janela, não de
  4 em 4). `roundpos = 1` **não** prende o movimento na malha de 4 px (medido); o campo `suave` existe, mas não mudou nada
  visível no teste.

## 2. Medidas da arte (mundo de 768, que é o padrão)

Toda camada é um PNG com fundo transparente (alfa 0 ou 255, sem borda suavizada), já na malha do jogo: **não ampliar**.
Largura mínima de uma camada parada = `320 + 448 × delta`, centralizada (o gerador centraliza sozinho). Se a camada for
uma faixa que se repete (`repete`), a largura é livre.

| Camada | delta | Largura x altura (px) | Onde fica |
|---|---|---|---|
| Céu | 0 | 320 x 180 | parado, cobre a tela toda |
| Nuvens (1 ou 2 faixas) | 0,05 a 0,2 | faixa de 256 a 400 x até 60, repetida | no alto; cada faixa com velocidade própria |
| Fundo distante (morros, outra margem) | 0,35 | 478 x o que precisar | a base tem de descer **26 px abaixo** da linha em que a camada da frente começa |
| Meio (rio, casario, trilho ao fundo) | 0,7 | 634 x o que precisar | a base desce **12 px abaixo** do começo do chão |
| Principal (chão + o lugar: fachada, coreto, estação) | 1 | 768 x até 232 | topo em y = −40 se for de tela cheia; a base vai até y = 192 (12 px além da tela) |
| Frente dos lutadores (poste, grade, mato) | 1,25 | 880 x …, ou peças soltas, ou faixa repetida | só nas pontas ou abaixo de y = 170 |

Regra da altura: quando a câmera sobe 40 px, uma camada de delta `d` desce `40 × d` na tela. Por isso a camada de trás
precisa continuar `40 × (1 − d)` px para baixo, escondida atrás da camada que a cobre; senão abre um furo entre as duas. O
céu com delta 0 não se mexe e tapa o alto. O gerador simula os quatro cantos da câmera e **recusa cenário com furo**.

Zona segura (com a câmera em repouso):

- **Chão de luta:** faixa de y = 140 a 180, sem objeto alto. Os pés ficam em y = 165.
- **Lutadores cobrem** x = 60 a 260, y = 55 a 165 no começo, e andam pela tela toda. O que identifica o lugar (o Cristo,
  a locomotiva, a fachada) deve ficar legível **acima de y = 100** ou no vão do meio (x = 120 a 200).
- **HUD:** barras de vida, retratos e nomes ocupam y = 0 a 38. Nada importante ali.
- **Frente:** nada de frente pode tapar o corpo. No teste, o poste de frente tapa o lutador que para atrás dele: por isso
  peça de frente só na ponta do mundo ou rente ao chão (até 10 px de altura).

Quantas camadas: de 5 a 8 (céu, 1 ou 2 de nuvem, fundo, meio, principal, 1 a 3 elementos animados, frente). Cada cenário
precisa de **pelo menos três coisas se mexendo sem depender da câmera**.

### Elemento animado

- **Em quadros:** uma folha horizontal com N quadros do mesmo tamanho, lado a lado, sem espaço, fundo transparente
  (`"folha": {"imagem": "x.png", "n": 8}`), ou N arquivos (`"quadros"`). Loop sem emenda: o último quadro liga no primeiro.
  8 quadros ou mais, 4 a 8 ticks cada (60 ticks = 1 s). O objeto não pode sair da caixa do quadro.
- **Que anda sozinho** (nuvem, pássaro, barco, fumaça): um desenho + `velocidade` em px por tick. Com `repete` e `vao`
  ele some de um lado e volta do outro sem fim (o vão é a distância entre as cópias).
- **Que balança** (bandeira no mastro, barco na água, galho): `seno_x` / `seno_y` = amplitude em px, período em ticks, fase.
- **Que vai e volta ou muda de velocidade:** `controles` (BGCtrl) com `ciclo` em ticks. No teste, o barco vai 4 s para um
  lado e 4 s para o outro com dois `VelSet`.
- **Luz** (sol, halo de poste, brilho na água): `mistura: "soma"`, desenhada escura (a cor é somada à de trás).

## 3. Estilo

Vale a seção [Estilo arcade anos 90](../biblia-de-arte.md#estilo-arcade-anos-90): sem dithering, sem ruído, sem borda
suavizada, degradê em faixas, rampas curtas com matiz deslocado. O fundo tem menos contraste e menos saturação que os
lutadores, para o corpo destacar. Os lugares são reais e públicos: foto e mapa servem só de referência do que existe
(forma, cor, posição). O desenho é original, sem pessoa real reconhecível (figurante genérico), sem logo, marca ou placa
de empresa, sem texto legível além do nome público do lugar quando for essencial, e nada copiado de cenário de jogo
comercial. Foto não entra no repositório.

## 4. Como gerar

A arte de um cenário fica em `cenarios/<id>/` (os PNG e o `cenario.json`). O gerador grava `stages/<id>.def` e
`stages/<id>.sff`:

```bash
python ferramentas/gerar_cenario.py cenarios/<id>/cenario.json --previa PASTA
```

`--previa` grava a simulação sem motor: três PNG (câmera na esquerda, no centro, na direita) e um GIF com a câmera indo
e voltando. O fundo da prévia é magenta: se aparecer magenta, é furo. Os campos do `cenario.json` estão no cabeçalho de
[`ferramentas/gerar_cenario.py`](../../ferramentas/gerar_cenario.py); o exemplo completo é
[`cenarios/teste/cenario.json`](../../cenarios/teste/cenario.json), montado por `ferramentas/cenario_teste.py`.

Convenção de posição: `x`, `y` são o canto de cima-esquerda da imagem **na tela de 320x180 com a câmera em repouso**
(x = 0 é a borda esquerda da tela, y = 0 o topo). Sem `x`, a camada fica centralizada; sem `y`, a base da imagem encosta
na base da tela. As camadas são desenhadas na ordem da lista; as de `"frente": true` vão por cima dos lutadores.

Também dá para chamar de outro script: `gerar_cenario.gerar(desc, pasta_dos_png, destino, previa, furo_magenta)`.

## 5. Como provar na sandbox

```bash
python ferramentas/filmar_cenario.py <id> --saida PASTA
```

Espera a vez da sandbox, filma 8 s com os dois lutadores sem IA passeando até a ponta esquerda, subindo, indo até a
ponta direita, subindo, e voltando (`ferramentas/robo/passeio.lua`), e monta `tira_geral.png`, `tira_fluidez.png` e três
quadros de tela cheia. Para só abrir uma luta no cenário: `python ferramentas/sandbox.py --args "-p1 pengaro -p2 hazaki
-s stages/<id>.def" --espera 45`. O `sandbox.py` e o `filmar_sandbox.py` copiam a pasta `stages/` do repositório para o
motor da sandbox; o `filmar_sandbox.py` ganhou `--cenario` e `--passeio`.

Critérios de aceite, olhando as tiras e os quadros:

1. O cenário aparece e o motor não escreve erro nem aviso de cenário (`motor_stdout.txt`).
2. Os pés dos dois lutadores pisam na linha do chão do desenho, com a sombra logo abaixo.
3. Nas duas pontas e com a câmera no alto, nenhuma borda preta nem furo (rodar com `--furo-magenta` na dúvida).
4. Paralaxe na ordem certa: o que está longe anda menos que o que está perto.
5. Toda animação roda sem salto: quadros seguidos mudam pouco e o loop não tem emenda visível.
6. Nada de frente tapa o corpo dos lutadores na área de luta.
7. O que identifica o lugar continua legível com os dois lutadores e o HUD na tela.

## 6. O que foi provado e o que não foi (2026-11-11)

Provado no filme do cenário de teste: carregamento do `.def` e do `.sff` RGBA, linha do chão, câmera nas duas pontas e
no alto sem borda preta (480 quadros conferidos por programa e as tiras olhadas), paralaxe com deltas de 0 a 1,25,
repetição com velocidade (nuvens), repetição de camada animada (rio, troca de quadro a cada 8 ticks como pedido),
animação em quadros (bandeira), seno em x e y (balão), `VelSet` por BGCtrl (barco), camada na frente dos lutadores,
`mistura: "soma"` parada e em quadros (sol e halo do poste) e `reflexo` no chão.

Não provado: tremor de tela (a sobra de 12 px embaixo é precaução), `repete` na vertical e com número de cópias,
`mistura: "subtrai"` e `alfa`, os outros tipos de BGCtrl além do `VelSet` (a volta do barco aos 4 s aparece na tira, mas
não foi medida), se `debugbg = 1` (`--furo-magenta`) pinta mesmo o furo de magenta no motor (o teste não tinha furo),
música de cenário, o retrato 9000,1 na tela de escolha e o cenário escolhido pelo menu do jogo (só foi aberto pela
linha de comando `-s`). O teste rodou com o layout padrão do motor na sandbox, com Pengaró x Hazak.

## 7. O que falta para o jogador escolher o cenário

Nada disto foi feito ainda, de propósito (o padrão continua `stages/stage0-720.def`):

1. `ferramentas/Jogo de Luta.bat`, passo 1: a lista de pastas baixadas do GitHub é `@('chars', 'motif')`; incluir
   `'stages'` (só depois de a pasta existir na `mugen`, porque o launcher falha se a pasta não aparecer).
2. No passo 3 do launcher: copiar `stages\` do jogo para `ikemen\stages\` com `robocopy /E` (sem `/MIR`, que apagaria os
   cenários do próprio motor).
3. `data\select.def` do motor: o launcher escreve `<lutador>, stages/stage0-720.def` para cada lutador. Para o cenário
   aparecer na escolha manual, acrescentar uma linha `stages/<id>.def` por cenário logo abaixo de `[ExtraStages]`; para
   virar o cenário fixo de um lutador no arcade, trocar o `stages/stage0-720.def` da linha dele.
