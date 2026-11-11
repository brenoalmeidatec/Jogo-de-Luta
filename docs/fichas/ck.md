# CK, o Boxeador de Rua (id técnico `ck`)

Ficha no modelo da seção 10 de [`docs/regras-dos-lutadores.md`](../regras-dos-lutadores.md), feita a partir das fotos e
do áudio que o Breno mandou em 2026-11-11. Arte no [estilo arcade anos 90](../biblia-de-arte.md#estilo-arcade-anos-90).
Modelo aprovado pelo Breno: [`sprites/ck/quadros/folhas/modelo.png`](../../sprites/ck/quadros/folhas/modelo.png)
(esquerda: base; direita: endiabrado). Roteiro das folhas: `ferramentas/folhas_ck.py`.

**Estilo de luta:** boxe com briga de rua. O forte dele é **esquiva e contra-ataque**: pêndulo, passo lateral, e responde
quando o outro erra. Socos de boxe nas mãos, bicuda e chute de rua nas pernas. Médio de velocidade, ótimo de perto.
**Personalidade / falas:** sacana, debochado, marrento. Ri da cara do oponente, ajeita o boné, chama para a briga.
As falas viram áudio que o Breno manda depois (balões continuam desligados).
**Cores e paleta:** pele marrom, cabelo preto curto, bigode fino e cavanhaque, brinco de pedrinha nas duas orelhas.
**Forma base toda de Lacoste:** polo branca com friso verde na gola e o jacaré verde no peito, boné preto com o jacaré,
short largo zebrado preto e branco, tênis branco liso, luva de boxe vermelha com atadura branca. Altura ~112 px
(magro e atlético), proporção de KOF.
**Marcas (exceção pedida pelo Breno):** a regra do jogo é sem marca, mas o CK usa Lacoste na base e roupa de marca de
"ratão" no endiabrado (camisa e bermuda estampadas no estilo Cyclone, chinelo com meia, óculos espelhado tipo Juliet).
Risco anotado: logo de verdade num jogo público pode dar problema com a dona da marca; se der, troca por marca inventada
parecida sem mudar o resto.
**Efeitos:** impacto de soco seco (poeira curta) e faísca branca no contra-ataque. Fumaça do pod: nuvem branca com
cheiro de "uva" (lilás clara). No endiabrado: estilhaço verde de vidro na garrafa e a aura.
**Aura do Despertar (regra da seção 4):** **fumaça cinza-esverdeada do baseado subindo dos pés**, densa e lenta, com
umas folhinhas de brasa. Nenhum outro lutador usa (Pengaró violeta, Gutto vermelho, Raiclaven prata, Hazak laranja-ouro).

## O que o áudio pediu

| Ideia no áudio | Como entra |
|---|---|
| "Briga de rua muito doida", boxe | Base de boxe com golpes de rua |
| "Meu bagulho é mais de esquiva", "focado em contra-ataque" | Esquiva de verdade (Pêndulo, Gingado de Esquiva) e contra-ataques (Contragolpe, Cruzado no Vácuo) |
| Forma base "com a roupa normal e a luvinha", "o kit da Lacoste" | Lacoste + luva vermelha |
| "Quando despertar, ele ativa o modo ratão" | Despertar **Modo Ratão** |
| Paredão de som atrás dele tocando, antes do round | Entrada do round: o paredão aparece atrás dele tocando |
| No Despertar: aparece o paredão, ele dança, gingada, mão no chão, pega uma garrafa, quebra e briga com ela | Animação do Despertar, e no Modo Ratão ele luta com a garrafa quebrada |
| "O golpe de lançar coisa é lançando a garrafa" | Projétil do Despertar: garrafa arremessada |
| Ataque do pod: puxa e solta a fumaça; no Despertar o pod vira um beck | **Tragada** na base (pod) e **Tragada de Beck** no endiabrado |
| Cachimbo de crack "é sacanagem" | Fica de fora, como a turma decidiu |
| Cabelo platinado, fumando, meio chapado (pedido do Breno) | Arte do endiabrado |

## Correntes (3 golpes + finalizador)

| Botão | 1º | 2º | 3º | Finalizador (derruba) |
|---|---|---|---|---|
| x | jab | jab duplo | cruzado | **Uno-Dos de Rua**: jab no queixo e cruzado no fígado juntos |
| y | direto | gancho de esquerda | gancho no fígado | **Levanta, Comédia**: uppercut que lança |
| a | bicuda na canela | chute baixo de rua | joelhada na coxa | **Bicuda de Pedreiro**: chute de bico na barriga que joga longe |
| b | chute frontal na barriga | chute alto de rua | pisão na coxa | **Voadora da Esquina**: pulinho e chute com os dois pés |

## Kombos de assinatura (4)

| Kombo | Entrada | Papel |
|---|---|---|
| Bom Dia, Cumpadi | → + y, x, b | abre **por cima** (overhand descendo) |
| Sobe e Desce | x, ↓ + a, y | alto e **baixo** |
| Encosta na Parede | ← + x, y, → + b | empurra para o canto |
| Sobe pro Teto | x, y, ↓ + y | **lança** para continuar no ar |

## Normais (16)

| Em pé | Agachado (↓ +) | No ar | Direcionais |
|---|---|---|---|
| x jab · y direto · a bicuda baixa · b chute frontal | x jab no corpo · y **uppercut (antiaéreo)** · a ponta do pé na canela · b **rasteira de rua (derruba)** | x soco descendo · y cotovelada · a joelhada · b **chute duplo (pega agachado, cross-up)** | → + y **overhand por cima (overhead)** · → + b pisão de rua · ← + x tapa de luva (afasta) · ← + a chute de calcanhar |

## Especiais (8): todos com comando cardinal

| Especial | Comando | Papel | Fraco / forte |
|---|---|---|---|
| Tragada | ↓ → x/y | **projétil lento / armadilha**: puxa o pod e solta uma nuvem de fumaça que fica parada um tempo e tonteia quem encosta | x nuvem perto; y nuvem longe e maior |
| Boné Voador | → ← x/y | **projétil reto que volta (bumerangue)**: joga o boné como disco, ele vai e volta para a cabeça | x curto; y atravessa a tela |
| Levanta, Comédia | → ↓ x/y | **antiaéreo**: uppercut subindo com a esquiva antes | y invencível até o fim do ativo, recuperação longa |
| Bote | ↓ → a/b | **avanço**: avança abaixado e solta o direto, atravessa meia tela | b vai mais longe e derruba |
| Bicuda Baixa | ↓ ← a/b | **golpe baixo**: desliza e dá a bicuda no tornozelo | b derruba |
| Gingado de Esquiva | ← → a/b | **ir para trás**: pêndulo, passa de lado por baixo do braço do oponente e chega virado; recuperação visível | a só passa; b passa e já solta o gancho |
| Contragolpe | ↓ ← x/y | **livre (contra-ataque)**: pose de guarda baixa; se apanhar nesse tempo, esquiva e responde com cruzado | y pega golpe baixo também |
| Pêndulo | ← ↓ a/b | **livre (esquiva)**: balança o tronco para os lados, invencível a golpe alto; aperta x ou y no meio para sair com soco | b balança mais tempo |

## Agarrões (3)

| Agarrão | Entrada | O que faz |
|---|---|---|
| Gola na Mão (em pé) | colado, → ou ← + y | segura pela gola, dá três socos curtos e empurra |
| Abaixa Aí (agachado) | colado, ↓ + y | puxa pelo boné/cabelo, joelhada e larga |
| Saideira (lore / comando) | ← → + y | abraça de lado como quem vai tirar foto, dá um tapa na nuca e uma bicuda; escapa com y ou b no começo. A lore por oponente vem depois |

## Supers (2)

| Super | Custo | Comando | O que faz |
|---|---|---|---|
| Rajada da Esquina | 1 estoque | ← → ↓ + a/b | pêndulo para frente e uma rajada de socos de boxe, fecha com a Voadora da Esquina |
| Nocaute de Rua | 2 estoques | ← → ↓ + x/y | esquiva do primeiro golpe que vier (ou avança), ajeita o boné e solta um cruzado de nocaute em câmera lenta, com o oponente rodando no ar |

Os dois são invencíveis do tick 1 ao fim do superpause.

## Entrada do round

O paredão de som aparece atrás dele tocando (som do Breno depois, nada de música de terceiros), ele dá uma gingada no
ritmo e entra na guarda. O paredão some quando o round começa.

## Despertar: **Modo Ratão**

- **Ativação:** barra cheia + **x + y**, gasta a barra inteira.
- **Animação (pedido do Breno, 2026-11-11):** o paredão aparece atrás dele tocando e ele dança. Tira as luvas, puxa o beck,
  dá uma tragada funda e solta uma fumaçona que **cobre o corpo todo**. Quando a fumaça passa, ele já está de ratão
  (platinado, camisa estampada aberta, regata, bermuda, chinelo com meia, Juliet na cabeça, cordão de ouro). A turma do
  paredão joga uma garrafa no chão, ele olha, pega, **quebra no chão** e luta com o caco. Invencível durante a animação,
  empurra o oponente. A aura de fumaça sobe dos pés. Folhas `despertar_a` (base) e `despertar_b` (ratão) + `fx_paredao`.
- **Jeito de bater (pedido do Breno):** chapado, **todo golpe é instável e louco**: cambaleia, quase cai, bate de ângulo
  estranho, lento e de repente explosivo. No jogo: os normais do Ratão variam um pouco o alcance e o tempo de cada vez
  (sorteio pequeno), e alguns têm um tropeço que vira golpe baixo.
- **O que ganha:** alcance com a garrafa, cortes que fazem o oponente sangrar a vida aos pouquinhos (dano pequeno por
  um tempo), e a fumaça tonteia mais.
- **O que perde:** sem luva, larga o boxe certinho: a esquiva fica mais lenta e o Contragolpe sai do kit (está chapado).

### Correntes novas (2)

| Botão | 1º | 2º | 3º | Finalizador |
|---|---|---|---|---|
| y | corte de garrafa de lado | corte de volta | estocada | **Caco no Peito**: estocada que lança |
| b | chinelada (chute com o chinelo) | chute de meia | rasteira de baile | **Passinho do Baile**: gira dançando e solta a voadora de chinelo |

### Normais novos (6)

y em pé vira **corte de garrafa**, ↓ + y vira **garrafa subindo** (antiaéreo com mais alcance), → + y vira
**garrafada por cima** (overhead), x no ar vira **corte descendo**, ← + x vira **assopro de fumaça na cara** (tonteia de
leve), b em pé vira **chinelada alta**.

### Especiais exclusivos (4)

| Especial | Comando | Papel |
|---|---|---|
| Garrafa Voadora | ↓ → x/y | **projétil novo**: arremessa uma garrafa em arco que estilhaça no chão e deixa cacos um tempo |
| Tragada de Beck | ↓ ↑ x/y | puxa o beck e solta uma nuvem grande que segue o oponente devagar |
| Passinho Ratão | → ← a/b | avanço dançando o passinho do baile, várias chineladas |
| Grave do Paredão | ↓ ↑ a/b | bate o pé, o paredão aparece um instante e o grave empurra o oponente para longe (quebra a pressão) |

### Kombo novo (1)

**Fim de Baile:** x, → + y, b (corte, garrafada por cima, chinelada alta).

### Super exclusivo (1): **Baile da Esquina**

← → ↓ + x + y, 1 estoque, só no Despertar. O paredão aparece tocando, o grave treme a tela, o CK dança em volta do oponente
cortando com a garrafa e fecha quebrando uma garrafa nova na cabeça dele.

### Especiais da base que ficam

- **Tragada:** vira a Tragada de Beck no `↓ ↑` x/y; o `↓ →` x/y vira a Garrafa Voadora.
- **Boné Voador:** sai, porque ele jogou o boné fora na transformação; o `→ ←` x/y vira **Juliet Voadora** (joga o óculos,
  que volta), mesmo papel de bumerangue com pose nova.
- **Bote** e **Levanta, Comédia:** saem com a garrafa na mão (mais alcance, menos rapidez).
- **Gingado de Esquiva:** vira um rolê de passinho de baile para trás do oponente.

## Derrota, vitória e provocação

- **Derrota:** senta no chão, tira o boné e coça a cabeça, inconformado.
- **Vitória:** ajeita o boné, tira as luvas com os dentes e faz pose de campeão, rindo.
- **Provocação (c):** bate as luvas, abaixa a guarda e chama com a mão ("vem").

## Estado (2026-11-11)

- **62 folhas prontas** em `sprites/ck/quadros/folhas_arcade/`: referência e 31 da forma base, `despertar_a/b` (a
  transformação nova: dança no paredão, fuma, a fumaça cobre tudo, sai de ratão, pega a garrafa que jogaram e quebra), a
  referência e 23 do Modo Ratão (instáveis, chapado) e 4 efeitos (`fx_aura`, `fx_fumaca`, `fx_garrafa` em magenta,
  `fx_paredao`). Cada folha foi revisada a olho (anatomia e regra da seção 7); as que falharam foram refeitas (uppercut com
  braço sumindo nas costas, soco no ar fraco, garrafa sumindo, garrafa aparecendo antes da hora no Despertar).
- **Recusas do ChatGPT:** ele não desenha uso de vape nem fumar como golpe. A Tragada (pod) e a Tragada de Beck viraram
  **pose de soprar** + `fx_fumaca`, e o pod é desenhado por código (`sprites/ck/quadros/itens/pod.png`). O jogo junta as
  três peças. A cena de fumar dentro da transformação ele desenhou.
- **Falta para ir para o jogo:** papéis do CK no `quantizar_folha.py`, passar as folhas pelo pipeline arcade, cortar,
  o `gerar_ck.py` (no molde do `gerar_raiclaven.py`) com os comandos desta ficha, retrato, a vítima dos agarrões e o CK no
  `Jogo de Luta.bat`. Nada disso foi testado no motor ainda.
- As fotos de referência do CK ficaram fora do repositório.
- **Correções pedidas pelo Breno (2026-11-11, tarde):** braço de trás saindo pelas costas e garrafa trocando de mão.
  Refeitos com a regra nova (luva de trás sempre na frente do queixo; caco sempre no braço de perto, desenhado na frente
  do corpo; mão de trás vazia): `cabecada`, `golaco` e 18 folhas do Ratão. Na segunda conta (gratuita) saíram `e_anda`,
  `e_vitoria` e `e_derrota` com a garrafa certa, com retoque por código onde o ChatGPT não acertou (garrafa extra apagada
  no quadro 6 do `e_anda`; quadros 2–3 da vitória e 8 da derrota copiados de quadros vizinhos certos). **Ainda a refazer**
  (as duas contas bateram o limite de imagens): `e_provoca` e `e_beck` (feitos antes da regra) e `e_golaco` e
  `e_juliet_voadora` (a garrafa ainda some ou sobe pelo braço de trás em alguns quadros). Dica que funcionou melhor no
  ChatGPT: dizer que a garrafa fica na mão "mais à direita na imagem" e pedir correção em cima da imagem, quadro a quadro. Os pedidos já estão com a regra
  em `ferramentas/folhas_ck.py`.

## Folhas (ChatGPT, estilo arcade)

Todas em `sprites/ck/quadros/folhas_arcade/`, 8 quadros, magenta liso, com a `referencia_ginga.png` anexada (as `e_`
com a `e_referencia_ginga.png`). Os nomes são os espaços do kit no gerador, como no Raiclaven; a lista e os pedidos
completos estão em `ferramentas/folhas_ck.py`. O que falta para ir para o jogo: quantizar com a paleta fixa
(`quantizar_folha.py` precisa dos papéis do CK), cortar e um `gerar_ck.py` no molde do `gerar_raiclaven.py`.
