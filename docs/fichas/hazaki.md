# Hazak, o Rapidinho da Quebrada (id técnico `hazaki`)

Ficha no modelo da seção 10 de [`docs/regras-dos-lutadores.md`](../regras-dos-lutadores.md), feita a partir de dois áudios
que o Breno mandou em 2026-11-10 (a turma decidindo o personagem). Arte no
[estilo arcade anos 90](../biblia-de-arte.md#estilo-arcade-anos-90), que é regra do Nazafights; paleta, prompt base e
problemas da arte atual em [`docs/arcade/hazaki.md`](../arcade/hazaki.md).

> **Nome:** nos áudios e no pedido do Breno ele é **Hazak**. No código e na tela ainda está "Hazaki" (`chars/hazaki`). O id
> técnico fica `hazaki` para não quebrar o launcher; o nome na tela muda para Hazak quando o personagem for refeito.

**Estilo de luta:** karatê de quebrada ("a base eu já tenho") com perna de taekwondo: quase tudo é chute, rápido e em
sequência, chutando várias vezes com a mesma perna sem descer o pé. Ele é **o mais rápido do jogo** (o "rapidinho"):
anda e corre mais rápido que todos, golpes fracos curtíssimos, mas apanha um pouco mais (vida e defesa menores). Não é
saco de pancada: tem como se armar (projéteis, voadora, contra-ataque).
**Personalidade / falas:** sacana, provocador, abusado. Fica balançando o dedo para o oponente. Provocação:
"Australopiteco mentiroso!". O bordão de hoje ("EU SOU GOSTOSO!") fica. As falas viram áudio que o Breno manda depois
(balões continuam desligados).
**Cores e paleta:** as da forma normal de hoje, corrigidas pela paleta fixa de [`arcade/hazaki.md`](../arcade/hazaki.md#a-paleta-fixa-15-cores--transparente):
cabelo escuro curto com degradê, pele bronzeada, kimono sem manga azul-índigo com debrum laranja, faixa quase preta
com duas pontas soltas, ataduras brancas nos pulsos, pulseira teal só no pulso de trás, descalço. Altura de hoje
(~109 px em pé), proporção de KOF.
**Efeitos:** poeira e lasca de asfalto nos chutes fortes; rastro de velocidade curto (2 ticks no máximo) na corrida e na
voadora; brilho dourado na Estatueta; no Despertar, brasa laranja-ouro (rampa própria, diferente do âmbar do whisky e do
violeta do Pengaró) e notas de dinheiro voando.

## O que os áudios pediram (e o que ficou de fora)

Transcrição automática local (Whisper medium, português), com ruído e várias vozes falando junto: vale como pista.

| Ideia nos áudios | Como entra |
|---|---|
| Estilo taekwondo, "só chute", "ele corre muito", "o mais rápido" | Kit de chutes, velocidade maior do elenco |
| "Gustavo disse que eu vou ser lutador de karatê, de quebrada; a base eu já tenho" | Mantém o karateca de hoje (rosto, kimono, faixa) e mistura com a perna de taekwondo |
| "Antigamente me chamavam de Diabo Louro": vira diabão loiro, cabelo jogado para trás, chifres, olhinho vermelho | Despertar **Diabo Loiro**, com a juba jogada para trás (não espetada) |
| "A versão demoníaca é de terno", "mafioso com maleta de dinheiro", chapelão | O Diabo Loiro veste **terno de mafioso**, chapéu e luta com a maleta |
| Despertar "pedindo permissão": levanta, olha para trás, "ô vida, posso despertar?", ela diz sim e sai da arena | Animação do Despertar (abaixo), com a **patroa** (personagem inventada) |
| "Pega Bolado": sai correndo e dá uma bicuda de dois pés | Especial **Pega Bolado** |
| "Ataque de dedadinha sacana", "fica balançando o dedo" | Cutucão nas costelas e o dedo balançando na provocação |
| "Ele tem que se armar de algum jeito; qual a graça de ser todo fodido" | Projéteis, contra-ataque e voadora de verdade |
| "Lança uma escultura dourada" | Projétil **Estatueta Dourada** (estátua genérica, sem rosto de ninguém) |
| Derrota: aparece "um bonde de policial" / alguém fala no ouvido e ele levanta doido e sai da tela | Derrota: toca uma sirene, ele levanta num pulo e foge correndo da tela |
| "Australopiteco mentiroso" | Fala da provocação |

**Ficou de fora:**
- O conteúdo sexual (a lambida que desperta, o agarrão com o dedo, a piada dos policiais, a foto, a "chibata"). Ataque
  sexual não vira golpe nem piada, nem de brincadeira. No lugar ficam a permissão da patroa e o cutucão nas costelas.
- Pessoas reais: o Marquito (os próprios áudios dizem que ele não entra), a escultura do Barack Obama, o "Yuri" e o "ET".
  A estatueta é genérica; Yuri e ET ficaram sem dar para entender na gravação.
- "Mafioso pique cafetão": entra como mafioso de terno chamativo (risca de giz, chapelão, anel), sem cafetão.

## Correntes (3 golpes + finalizador)

| Botão | 1º | 2º | 3º | Finalizador (derruba) |
|---|---|---|---|---|
| x | jab rápido | jab duplo | **Cutucão Sacana**: dois dedos nas costelas, o oponente encolhe | **Tá Achando Ruim?**: tapa de costas de mão que gira o oponente e derruba |
| y | soco reto | cruzado | cotovelada descendo | **Punho de Concreto curto**: soco no chão que levanta asfalto e lança |
| a | chute baixo na canela | chute na cintura com a mesma perna | chute alto com a mesma perna, sem descer o pé | **Tesoura de Bairro**: giro de 540° com o chute de trás |
| b | chute lateral | chute giratório | chute de gancho na cabeça | **Machado de Dojô**: calcanhar descendo do alto, o oponente quica |

## Kombos de assinatura (4)

| Kombo | Entrada | Papel |
|---|---|---|
| Bom Dia, Vizinho | → + b, a, b | abre **por cima** (Machado curto) |
| Rasteira de Calçada | x, ↓ + a, b | alto e **baixo** |
| Sai Daqui | ← + x, y, → + y | empurra para o canto |
| Sobe, Mentiroso | a, b, ↓ + y | **lança** para continuar no ar |

## Normais (16)

| Em pé | Agachado (↓ +) | No ar | Direcionais |
|---|---|---|---|
| x jab · y soco reto · a chute baixo · b chute lateral | x jab baixo · y **joelhada subindo (antiaéreo)** · a chute na canela · b **rasteira (derruba)** | x soco de martelo · y cotovelo descendo · a joelhada · b **chute duplo (pega agachado, cross-up)** | → + y Cotovelo de Faixa · → + b **Machado de Dojô (por cima)** · ← + x Cutucão Sacana · ← + a coice de calcanhar para trás |

## Especiais (8): todos com comando cardinal

| Especial | Comando | Papel | Fraco / forte |
|---|---|---|---|
| Punho de Concreto | ↓ → x/y | **projétil baixo**: soca o chão e solta lasca de asfalto rasteira (defende agachado) | x lenta e curta; y rápida e vai até o fim da tela |
| Estatueta Dourada | → ← x/y | **projétil em arco**: arremessa uma estatueta dourada que cai na frente | x cai perto; y cai longe |
| Ascensão de Faixa | → ↓ x/y | **antiaéreo**: joelho e ombro subindo, faixa chicoteando, pés no chão | x invencível só contra ar no começo; y invencível até o fim do ativo, recuperação longa |
| Giro de Garagem | ↓ → a/b | **avanço**: chute girando que atravessa meia tela | b vai mais longe e derruba |
| Corte de Base | ↓ ← a/b | **golpe baixo**: desliza com a perna esticada no chão | b derruba |
| Rolada de Tatame | ← → a/b | **ir para trás**: rola por baixo e chega virado; recuperação visível | a só passa; b passa e já chuta |
| Pega Bolado | ← ↓ a/b | **livre (a cara dele)**: sai correndo e dá a voadora de dois pés | a curta; b atravessa a tela e derruba, erra feio se defenderem |
| Guarda de Aço | ↓ ← x/y | **livre**: contra-ataque, defende e responde com chute | y pega golpe baixo também |

## Agarrões (3)

| Agarrão | Entrada | O que faz |
|---|---|---|
| Abraço de Quebrada (em pé) | colado, → ou ← + y | abraça apertado, levanta e joga por cima do ombro |
| Puxa a Perna (agachado) | colado, ↓ + y | puxa a perna do oponente e derruba sentado |
| Cutucão Sacana (lore / comando) | ← → + y | prende pelo pescoço e cutuca as costelas até o oponente cair tonto de rir; escapa com y ou b no começo. A lore por oponente vem depois |

## Supers (2)

| Super | Custo | Comando | O que faz |
|---|---|---|---|
| Faixa no Asfalto | 1 estoque | ← → ↓ + a/b | rajada de chutes de taekwondo com a mesma perna, sobe chutando e fecha com o Machado de Dojô |
| Rapidinho da Quebrada | 2 estoques | ← → ↓ + x/y | corre e atravessa a tela várias vezes, batendo a cada passagem, e fecha com o Pega Bolado |

Os dois são invencíveis do tick 1 ao fim do superpause.

## Despertar: **Diabo Loiro**

- **Ativação:** barra cheia + **x + y**, gasta a barra inteira (seção 4; troca o `x+a+y` de hoje).
- **Animação (dos áudios):** ele bate o pé, olha para trás e pergunta "Ô vida, posso despertar?". A **patroa** (personagem
  inventada, só nesta cena) aparece no fundo, faz que sim com a cabeça e sai da arena. Ele se vira: o cabelo cresce loiro e
  vai todo para trás, nascem dois chifres, o olho fica vermelho, e o terno de mafioso aparece nele (risca de giz,
  chapelão, anel), com a maleta de dinheiro na mão. Invencível durante a animação, empurra o oponente.
- **O que ganha:** alcance e peso. A maleta bate como um porrete, os chutes de sapato social empurram mais, e o dinheiro
  vira arma (notas fictícias, sem moeda real nem marca).
- **O que perde:** velocidade. Deixa de ser o rapidinho: anda e corre na média do elenco, e os fracos ficam mais lentos.

### Correntes novas (2)

| Botão | 1º | 2º | 3º | Finalizador |
|---|---|---|---|---|
| y | maletada de lado | maletada de volta | maletada de cima | **Negócio Fechado**: abre a maleta na cara do oponente e fecha com tudo |
| b | chute de sapato na canela | chute de sapato na barriga | coice de costas | **Pisão de Chefe**: pisa no oponente e arruma a gravata |

### Normais novos (6)

↓ + y vira a **maleta subindo** (antiaéreo com mais alcance), → + b vira **chapelada por cima** (overhead com o chapéu),
x em pé vira **tapa com anel**, ← + x vira **dedo balançando** (provoca e anula um projétil fraco), b no ar vira
**pisão de sapato descendo**, a agachado vira **chute de bico de sapato**.

### Especiais exclusivos (4)

| Especial | Comando | Papel |
|---|---|---|
| Chapéu Bumerangue | ↓ → a/b | **projétil novo**: joga o chapéu, que vai e volta (toma o comando do Giro de Garagem, que sai no Despertar) |
| Maleta Giratória | → ← a/b | avanço girando a maleta, várias batidas |
| Nota Falsa | ↓ ↑ x/y | armadilha: deixa um maço de notas no chão que estoura em papel picado quando o oponente passa |
| Suborno | ↓ ↑ a/b | agarrão de comando: oferece o maço, o oponente pega, leva a maletada |

### Kombo novo (1)

**Sociedade Fechada:** x, → + b, y (tapa com anel, chapelada por cima, maletada de lado).

### Super exclusivo (1): **Chuva de Dinheiro**

← → ↓ + x + y, 1 estoque, só no Despertar. Abre a maleta, as notas cobrem a tela, ele bate no meio do papel e fecha com a
Estatueta Dourada gigante.

### Especiais da base que ficam

- **Estatueta Dourada:** maior, mais lenta, e se acertar o chão fica um tempo parada como obstáculo.
- **Pega Bolado:** vira a voadora de sapato social, mais lenta e quica o oponente.
- **Punho de Concreto:** vira soco com anel; a lasca sai em brasa e anda mais devagar.
- **Rolada de Tatame:** some na fumaça de brasa e reaparece atrás (o terno não rola no chão).

## Derrota, vitória e provocação

- **Derrota:** toca uma sirene, ele levanta num pulo e foge correndo para fora da tela.
- **Vitória:** amarra a faixa com um puxão e balança o dedo para o oponente ("EU SOU GOSTOSO!").
- **Provocação (c):** balança o dedo e solta "Australopiteco mentiroso!".

## Pedido para o Alisson: recriar o Hazak

Oi, Alisson! O Breno pediu para você **refazer o Hazak** seguindo esta ficha, partindo do que já existe:

1. **Base que já tem:** o `ferramentas/gerar_hazaki.py`, a identidade do `sprites/hazaki/karate.png` (rosto, kimono índigo com
   debrum laranja, faixa, ataduras, pulseira teal) e o estudo arcade em [`docs/arcade/hazaki.md`](../arcade/hazaki.md)
   (paleta fixa, prompt base, a lista de folhas e os problemas da arte atual: a pose de palmas juntas com bola de fogo e o
   soco para cima saem).
2. **Estilo arcade é regra:** pipeline `quantizar_folha` → `animar_folha --arcade` → `conferir_arte`, com os papéis do Hazaki
   no `PAPEIS` antes da primeira folha. Folhas em `sprites/hazaki/quadros/folhas_arcade/`, um chat "Hazak — arcade" no ChatGPT.
3. **Diabo Loiro de terno:** o prompt `d_` do `arcade/hazaki.md` muda para o terno de mafioso com chapéu e maleta (juba
   loira para trás, chifres, olho vermelho, mesmo rosto e tamanho do normal). E faltam as folhas da patroa (só na animação
   do Despertar).
4. **Gerador:** o `gerar_hazaki.py` passa a ler folhas próprias (hoje recorta `karate.png`, e o `montar_sprites(hazaki=True)`
   desliga as folhas), com os golpes e comandos daqui. Corrige junto o furo conhecido: arremessado pelos outros ele some
   (faltam os desenhos de vítima).
5. **Aceite:** checklist da seção 9 das regras. Golpes próprios dele, sem copiar animação de outro lutador.
6. **Onde subir:** esta ficha está na branch `hazak`. Trabalhe nela; vai para a `mugen` quando o Breno aprovar.
