# Raiclaven, o Barbeiro (id técnico `raiclaven`)

Ficha no modelo da seção 10 de [`docs/regras-dos-lutadores.md`](../regras-dos-lutadores.md). Referência de arte:
[`sprites/barbeiro/referencia.png`](../../sprites/barbeiro/referencia.png). Origem das ideias: áudio do Breno de 2026-11-06.

**Estilo de luta:** a arte marcial do cabeleireiro. Só golpe "cabeleiral": tesoura, pente, escova, vassoura, talco e
cadeira de barbeiro. Pressão de perto, cortes que travam o oponente e uma boa dose de teleporte ("Próximo!").
**Personalidade / falas:** psicopata simpático. Sorriso largo, olhos arregalados, fala de balcão ("quem é o próximo?",
"vai querer na régua?", "deixa que eu capricho"). Resenha pesada pode (regra do jogo); nada de piada com
escravidão, deficiência ou estereótipo de mulher loira.
**Cores e paleta:** camisa e avental pretos com friso prateado, calça preta larga, sapato preto brilhoso, pele marrom,
cabelo crespo curto preto com degradê, cavanhaque. Distintivo de barbearia no bolso (tubo listrado vermelho, branco e
azul genérico, sem marca). Braço direito mecânico: ombreira de aço escuro e **tesoura gigante** no lugar da mão
(lâminas prateadas, pino no meio). Braço esquerdo humano, enorme e com veias, **mão sempre rodando um pente**. Avental
com pente e pincel de barba no bolso. Altura **120 px** (musculoso, entre o normal de 112 e o grande de 128).
**Efeitos (pixelfx e recolor):** impactos pelo `LEIA-ME.md` de `assets/efeitos/`. Faísca de aço (`hit-spark` e
`crit-hit` recoloridos para prata e branco) nos cortes; talco branco na fumaça de teleporte; `zap-hit` recolorido para
amarelo na Máquina Explosiva.

Tudo na tela é pixel art desenhada à mão no estilo SNES/arcade. Nunca 3D pixelizado, nem como quebra-galho.

## Estado (2026-11-10)

- **Montado na forma normal:** referência aprovada pelo Breno (`sprites/raiclaven/quadros/folhas/referencia_ginga.png`) e
  30 folhas próprias de barbeiro (pedidos em `ferramentas/folhas_raiclaven.py`), cortadas com `LUTADOR=raiclaven
  animar_folha.py` e montadas por `ferramentas/gerar_raiclaven.py` em `chars/raiclaven`. Chat "Generate Fighting Sprite" no
  ChatGPT (`chatgpt.com/c/6af2f2fe-a370-83e8-8f01-68ab7a3d36be`), feito pelo Brave.
- **Próximo! forte (pedido do Breno):** joga o pente, some no talco, aparece nas costas e bate numa sequência própria de 3
  acertos (folha `pente_combo`, estado 1701).
- Ele usa a lógica de estados do kit (a mesma do Pengaró e do Gutto) com desenhos próprios em cada golpe; os comandos e
  papéis da tabela de especiais abaixo ainda não foram ligados um a um. O robô passa 143 de 144 (a que falha, arte do
  super no Despertar, falha igual no Gutto).
- **Falta:** o Despertar (Surto de Tesoura) com arte própria (hoje: poses normais escurecidas; `despertar_a/b` são cópias da
  provocação), Borrifada, Máquina Explosiva e Fila de Clientes com arte própria, efeitos prateados, retrato e áudios.
  Não filmado: a captura de tela pegou outra janela por cima do jogo.

## Despertar novo: o Cientista Louco (pedido do Breno, 2026-11-10; branch `raiclaven`)

Substitui o "Surto de Tesoura" descrito no fim desta ficha.

- **Transformação:** penteia o cabelo para trás, põe óculos de lente verde, grita, e o jaleco vem voando e gruda nele
  (`despertar_a`, `despertar_b`). Modelo aprovado: `folhas/cientista_modelo.png`.
- **Estilo de luta:** muda tudo. Ele fica quase parado, fazendo pose, estalando os dedos e dando ordens com a tesoura, e
  as criaturas do laboratório lutam por ele. Golpes dele mesmo: tubo de ensaio (projétil), seringa (agarrão), choque
  verde para cima (antiaéreo), fumaça verde (teleporte) e o super de raios.
- **Quem luta por ele (2ª versão, a 1ª de monstros de laboratório foi recusada pelo Breno):** clientes comuns da barbearia
  que saíram errados da máquina e das poções dele, e a **Cliente Zero** presa na corrente.
- **Limite de conteúdo:** ninguém aqui é pessoa com deficiência (cadeirante, microcefalia, deformidade de nascença) nem
  pessoa real; o estranho vem do experimento dele (regra do jogo).
- **Folhas:** `despertar_a`, `despertar_b`, `endiabrado` (8 poses), as `e_<golpe>` do cientista, `e_corrente_*` (ele
  segurando a corrente), `mulher_*` (a Cliente Zero), `cobaia_*` e `fila_clientes`. Pedidos em `CIENTISTA` de
  `ferramentas/folhas_raiclaven.py`.

### Cliente Zero, a mulher na corrente (ataque principal)

Era uma cliente comum; a máquina a deixou magra, cinzenta, torta, de cabelo vivo até o joelho e olhos verdes, mexendo aos
trancos. Coleira de ferro no pescoço, corrente até a mão do cientista. Ela fica agachada como aranha na frente dele (ajudante
que segue a posição dele, sem barra de vida própria; apanha junto com ele) e a corrente é desenhada entre os dois.

| Golpe | Comando (Despertar) | Cientista | Cliente Zero | Papel |
|---|---|---|---|---|
| **Chicotada** | x | `e_corrente_chicotada`: estala a corrente | `mulher_chicotada`: bote com as duas garras | golpe médio rápido, alcance longo (a corrente estica) |
| **Mangual** | y | `e_corrente_mangual`: gira acima da cabeça e desce | `mulher_mangual`: voa em arco e cai de cabeça e garras | **por cima** (defender em pé), derruba |
| **Rasteira de Aranha** | ↓ + x | `e_corrente_parado` | `mulher_rasteja`: corre rente ao chão e volta puxada | **baixo**, avança meia tela |
| **Pulo de Aranha** | ↓ + y | `e_corrente_parado` | `mulher_sobe`: salta e arranha para cima | **antiaéreo** |
| **Abraço da Cliente** | → ← + y (agarrão) | `e_corrente_puxao`: puxa a corrente de volta | `mulher_agarra`: gruda no oponente | agarra a distância e **traz o oponente** até o cientista, que encerra com a seringa (`e_agarrao`) |
| **Corrente Giratória** | super, ← → ↓ + x + y | `e_corrente_giro`: gira como arremesso de martelo | `mulher_mangual` em volta dele | 4 a 6 acertos dos dois lados, empurra |

### Cobaias da barbearia (especiais de invocação)

Cada uma entra por uma porta de fumaça verde atrás do cientista, faz um ataque e some. Ele só estala os dedos (`e_soco`) ou
manda com a tesoura (`e_martelo`). Só uma cobaia por vez na tela.

| Cobaia | Comando | Ataque | Papel |
|---|---|---|---|
| **Pescoço de Borracha** (`cobaia_pescoco`) | ↓ → x/y | o pescoço estica e dá cabeçada na altura da cabeça | **cutucada de longe**, forte vai mais longe |
| **Cabelo Tentáculo** (`cobaia_tentaculo`) | ↓ ← x/y | tentáculos de cabelo varrem o chão e prendem o tornozelo | **baixo** que segura o oponente por um instante |
| **Cabeça Virada** (`cobaia_avesso`) | → ↓ a/b | anda de costas, pula em arco e chuta caindo | **por cima / cruzado**, chega pelas costas |
| **Balão de Gel** (`cobaia_gel`) | ↓ → a/b | rola até o oponente e estoura em gel | **projétil** que deixa poça de gel que escorrega e atrasa |

Golpes dele mesmo continuam: tubo de ensaio (← ↓ x/y), choque verde para cima, fumaça verde (teleporte) e o super
**Fila de Clientes** (clientes hipnotizados de olho de coração que passam pelo oponente e cortam o cabelo dele).
- **Ainda não está no jogo** (pedido do Breno): falta cortar, ligar as criaturas como ajudantes que atacam e montar o
  Despertar no gerador.

## Correntes (3 golpes + finalizador)

| Botão | 1º | 2º | 3º | Finalizador (derruba) |
|---|---|---|---|---|
| x (pente, rápida) | Pentada: jab de pente, mão esquerda | Contrapentada: costas da mão com o pente | Escovada: pincel de barba sobe do avental | **Degradê**: tesoura fecha seca ("tchac") na altura do pescoço |
| y (tesoura, pesada) | Abertura: lâmina aberta em corte horizontal | Fechada: as lâminas fecham numa mordida | Talho em X: corte diagonal duplo | **Tesourão**: golpe de cima para baixo com a tesoura aberta, crava e derruba |
| a (chute rápido) | Bico de Sapato: ponta do pé na canela | Pisada de Pedal: pisão baixo, como no pedal da cadeira | Joelhada de Encosto: joelho alto | **Cadeira Giratória**: chute girando no próprio eixo |
| b (chute pesado) | Chute de Navalha: frontal alto | Calcanhar Afiado: calcanhar em arco | Vassourada: rasteira meio-giro | **Fim de Expediente**: pontapé largo que joga longe |

## Kombos de assinatura (4)

| Kombo | Entrada | Função |
|---|---|---|
| Corte Social | → + y, x, b | abertura de perto, termina em chute pesado |
| Barba e Cabelo | x, ↓ + a, y | **baixo** no meio (a golpe baixo) e fecha em cima |
| Navalhada | ← + x, y, → + b | empurrão que termina em **golpe por cima** (→ + b) |
| Lavagem e Escova | a, b, ↓ + y | **lançador**: o ↓ + y joga para cima e dá para seguir no ar |

Todos avançam só se o golpe anterior encostou (regra B das correntes).

## Normais (16)

| Em pé | Agachado (↓ +) | No ar | Direcionais |
|---|---|---|---|
| x Pentada seca (jab, mão esquerda) | x Pentada baixa | x Pente no voo, disputa aérea | → + y Cotovelo de Balcão (confirma de perto) |
| y Tesoura aberta (corte de alcance médio) | **y Tesoura Ascendente (antiaéreo)** | y Mergulho de Lâmina, diagonal abaixo | **→ + b Machadada de Tesoura (por cima, tem que defender em pé)** |
| a Bico de sapato | a Canela de Sapato (baixo rápido) | a Joelho de Pulo, curto | ← + x Palma de Recuo (mão aberta de trás) |
| b Chute de navalha | **b Vassoura Baixa (derruba)** | **b Voadora Cruzada (acerta quem está agachado, pulo por cima)** | ← + a Sola de Recuo, chute que recua |

## Especiais (8): todos com comando cardinal

| # | Nome | Comando | Fraco / forte | Papel |
|---|---|---|---|---|
| 1 | **Pente Voador** | ↓ → x/y | fraco: rápido e curto; forte: lento e vai longe | **Projétil 1: reto no chão** (arremessa o pente grande) |
| 2 | **Borrifada** | ↓ ← x/y | fraco: arco curto; forte: arco longo e cai atrás | **Projétil 2: em arco** (esguicho do borrifador, passa por cima do agachado) |
| 3 | **Tesoura Ascendente** | → ↓ x/y | forte sobe mais e erra pior | **Antiaéreo**: sai rápido, ganha de pulo, `uppercut` |
| 4 | **Tesoura Voadora** | ↓ → a/b | forte atravessa meia tela | **Avanço**: investida com a tesoura abrindo e fechando, encerra combo |
| 5 | **Próximo!** | ← → a/b | fraco: aparece atrás e para; forte: aparece atrás e já solta 3 cortes | **Ir para trás do oponente**: some em nuvem de talco, chega virado, recuperação visível |
| 6 | **Varrida** | ↓ ← a/b | forte avança mais e derruba | **Golpe baixo de chão**: vassoura varrendo rente ao chão, pega quem fica agachado |
| 7 | **Pente Girando** | ← ↓ x/y | fraco: guarda média; forte: guarda média e alta | **Especial de leitura**: a mão esquerda gira o pente como escudo, rebate o golpe e responde com um corte de tesoura |
| 8 | **Tesoura Helicóptero** | → ← x/y | forte gira mais vezes | **Livre, a cara do lutador**: o braço mecânico roda como hélice, 3 a 4 acertos, empurra para frente |

Comando de cada um é único no lutador. Projéteis têm papéis diferentes (reto e arco). Só 1 projétil próprio na tela.

## Agarrões (3)

| Agarrão | Entrada | Animação |
|---|---|---|
| Em pé (800) | colado, → ou ← + y | **Toalha Quente**: enrola a toalha na cara, gira o oponente e joga; depois **arruma o pente** no cabelo, de pose |
| Agachado (810) | colado, ↓ + y | **Cabeça na Pia**: pega o oponente agachado pelo cangote e bate a cabeça no chão |
| Lore (820) | ← → + y | **Corte Personalizado**: segura o oponente, estala a tesoura nas mechas e solta com o cabelo estragado. Genérico até a lore chegar, depois troca animação e fala por `p2name` |

## Supers (2)

| Super | Custo | Comando | O que faz |
|---|---|---|---|
| **Próximo, Cliente!** | 1 estoque | ← → ↓ + a/b | Some, **aparece no cara** e solta um combo de 8 cortes, termina com a tesoura fechando e `crit-hit` |
| **Máquina Explosiva** | 2 estoques | ← → ↓ + x/y | Joga a máquina de cortar cabelo no oponente. Ela faz barulho, esquenta, sobe faísca e **explode**. Se o oponente morre na explosão, o nocaute dele fica **com o cabelo cortado na régua** (arte opcional do nocaute) |

## Despertar: **Surto de Tesoura**

**Ativação:** barra cheia + **x + y** (padrão). **Dura:** até a barra drenar ou o fim do round.
**Visual (sem forçar no endiabrado):** o cabelo **continua preto** (não clareia). Ele fica ainda mais musculoso, veias
saltadas, **olhos esbugalhados e arregalados**, sorriso de psicopata, ombreira do braço mecânico soltando faísca.
Transformação por **arte redesenhada**, não recolor.
**Ganha:** mais alcance e dano, mais golpes novos, a tesoura vira serra nos cortes, mais acertos nos especiais.
**Perde:** menos precisão (recuperação maior nos golpes fortes que erram) e o Pente Girando passa a ser só de guarda
média. Mesmo ritmo de resenha, mas a Borrifada e a Varrida mudam de função (abaixo).

### Correntes novas (2)

| Botão | 1º | 2º | 3º | Finalizador |
|---|---|---|---|---|
| y | Corte Duplo | Corte Cruzado | Giro de Tesoura completo | **Corte Raso**: tesoura aberta crava no chão e levanta o oponente |
| b | Chute Duplo | Calcanhar de Cadeira | Voadora Rasante | **Cadeira de 3 Voltas**: chute que dá 3 voltas antes de bater |

### Normais novos (6)

x em pé **Pente Serra** (o pente vira serra, mais alcance) · y em pé **Tesoura Estendida** (alcance longo) ·
↓ + y **Tesoura Cravada** (antiaéreo que cobre dos dois lados) · y no ar **Mergulho Serra** (cross-up) ·
→ + b **Machadada Serrada** (por cima, mais lenta e pesada) · ↓ + b **Rasteira de Lâmina** (derruba e deixa corte no chão).

### Especiais exclusivos (4)

| Nome | Comando | Papel |
|---|---|---|
| **Disco de Máquina** | ← → x/y | **Projétil novo, volta (bumerangue)**: disco serrilhado que vai e volta |
| **Mergulho de Tesoura** | ↓ ↑ x/y | pulo curto e mergulho em diagonal com a tesoura aberta, por cima |
| **Corte Cruzado no Chão** | → ↓ a/b | cravada de tesoura no chão que abre um X de corte na frente |
| **Reflexo no Espelho** | ← ↓ a/b | levanta um espelho de mão e rebate projétil (volta com a cor dele) |

### Kombo novo (1)
**Corte Navalhado**: y, → + y, ↓ + y (termina lançando, com a tesoura-serra).

### Super exclusivo (1): **Fila de Clientes**
Comando ← → ↓ + x + y (só no Despertar), 2 estoques. Ele faz uma pose de balcão, e **uma fila de clientes** (o moleque
da frente segura uma senha numerada) aparece **atrás dele**, de olhos de coração e andando torto, se arrastando rente
ao chão em direção ao oponente. Quando cada cliente **passa pelo oponente, o oponente fica com o cabelo cortado**
(dano em várias batidas). Os clientes são uma animação própria do super e não têm vida nem colisão.

### Especiais da base que ficam
Pente Voador vira o mesmo pente em chamas de faísca (mais um acerto). Borrifada vira esguicho que **deixa poça** que
atrasa o oponente. Tesoura Ascendente sobe com a serra (mais um acerto). Tesoura Voadora termina com giro. Próximo!
chega e já solta 1 corte, mesmo na versão fraca. Varrida vira a vassoura com lâmina (derruba sempre). Pente Girando
passa a só de guarda média. Tesoura Helicóptero ganha mais 2 voltas.
