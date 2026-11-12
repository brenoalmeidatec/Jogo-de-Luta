# Kit dos bosses: golpes, efeitos, aura e folhas da forma despertada

Escrito em 2026-11-11 a partir de cinco planos de leitura (um por lutador) e do sistema de aura de
[`aura_animada.md`](aura_animada.md). **É plano para execução: nada daqui rodou em motor**, fora o sistema de aura, que
foi filmado na sandbox com um lutador de teste. Tempos, danos e alcances marcados "alvo" são proposta; os marcados
"calculado" saíram da fórmula do gerador (`RITMO` 1,5), sem medir em jogo. Os nomes de folha foram conferidos contra
`docs/arcade/fila_bosses.md` (branch `bosses`) e o Lote 7 de `docs/arcade/fila.md` (branch `endiabrado`).

## 1. Regra do dono (2026-11-11)

O dono aprovou a forma despertada de cada lutador como **boss final** (conceitos em
`sprites/<id>/quadros/folhas_arcade/e_conceito.png`; Hazak: `d_conceito.png`) e disse:

> "olhe toda a ficha deles para já ir colocando no jogo essa versão e já ir fazendo os movimentos deles; eu não quero
> nada estático, essas auras e esses elementos vão ter que ter uma animação para dar movimento, e eu não quero um
> movimento todo duro, eu quero fluidez"

E antes, no mesmo dia: **cada boss tem, só dele, a aura, os efeitos, os especiais e o estilo de ataque.**

Três consequências que valem para os cinco:

1. **Só dele.** Nenhum golpe próprio, efeito ou camada de aura se repete entre lutadores. Dado de golpe copiado de
   outro lutador (o Gutto hoje usa os do Pengaró byte a byte) não passa.
2. **Nada estático.** Aura, elemento de aura, efeito de golpe e projétil têm animação própria e ainda são mexidos
   pelo motor a cada tick. Efeito de um quadro só, ou camada colada dura no corpo, não passa.
3. **Fluidez.** Corpo e efeito passam na regra da seção 2, conferida em vídeo da sandbox, não em folha parada.

As cinco auras aprovadas (todas efeito à parte por `Explod`, seção 4 das regras; nunca desenhadas na folha do corpo):

| Lutador | Cor | Forma |
|---|---|---|
| Pengaró | violeta-preto | coluna de fumaça + anel de sombra girando no chão + chicotes, elos e pedras flutuando |
| Gutto | vermelho, miolo branco | garanhão gigante de raio empinado atrás dele + crateras de casco + ferraduras-faísca |
| Raiclaven (cabelo verde) | aço com raio branco-prata | leque radial de tesouras, navalhas e pentes + anel interno de foices girando + lascas no chão |
| Hazak | laranja-ouro | asas de diabo de notas em chamas + coroa de ouro derretido pingando + faixa de brasa |
| CK | cinza-esverdeado | paredão de som de fumaça soltando anéis de fumaça |

## 2. Regra de fluidez

Vale para a forma boss dos cinco. Não muda o frame data (início, ativo, total, caixa): muda quantos desenhos há,
quanto cada um segura e o que se mexe em volta. **Anatomia vem antes** (regra 7): quadro do meio por fluxo óptico
continua proibido no corpo; a fluidez do corpo vem de desenho. Na aura e nos efeitos o entremeio é liberado
(`aura.alongar_loop`).

### 2.1 Corpo (cada item se confere no `.air`, no `.cns` ou na tira quadro a quadro do vídeo)

| # | Critério | Como conferir |
|---|---|---|
| C1 | **Antecipação.** Todo golpe tem pose de preparo antes do 1º tick ativo: 1 pose no fraco, 2 (carga e tensão) no forte, no finalizador e no especial. Golpe por cima e finalizador avisam: preparo ≥ 10 ticks | `.air`: elementos antes do primeiro com `Clsn1` |
| C2 | **Recuperação com 3 quadros ou mais.** Depois do contato vêm ≥ 3 desenhos distintos (≥ 2 no fraco), cada um de 4 a 9 ticks, soltando aos poucos; nunca contato → guarda direto | `.air`: elementos depois do último com `Clsn1` |
| C3 | **Panos atrasando.** O que é solto (casaco, sobretudo, jaleco, crina, rabo, corda, corrente, cordão, camisa aberta) chega 1 desenho depois do corpo e ainda está em posição diferente nos 2 desenhos seguintes ao contato. Tem que estar escrito no MOTION da folha | tira do golpe: o pano muda de lugar em desenhos em que o tronco já parou |
| C4 | **Deslocamento por velocidade.** Nenhum `PosAdd` maior que 2 px em estado de golpe (único salto permitido: ir para trás do oponente, e mesmo esse viaja de 6 a 8 ticks em silhueta). Avanço entra em rampa de 2 a 3 ticks e freia com `VelMul x` entre 0,75 e 0,85 por tick; proibido `VelSet x = 0` seco com velocidade acima de 1 | `grep PosAdd` no `.cns`; log de posição por tick: passo ≤ velocidade máxima do golpe |
| C5 | **Sem pose trocando seca.** Entre duas poses em que o membro anda mais de 20 px há 1 ou 2 smears de 1 tick, ou um desenho de passagem. Fora do contato nenhum desenho segura mais de 9 ticks. Nenhum vai-e-volta de desenho (ex.: 4, 3, 4) | `.air`: tempos por elemento; tira: nenhum par de quadros vizinhos com o membro pulando sem smear |
| C6 | **Movimento contínuo.** Ginga com ≥ 16 desenhos e andar/correr com ≥ 12, nenhum acima de 2 ticks. Enquanto só houver folha de 8, o teto é 4 ticks por desenho e a folha `_b` fica na lista de pedidos | `.air` das ações de parado, andar e correr da forma |
| C7 | **Corpo nunca parado sozinho.** Enquanto um desenho do corpo segura mais de 6 ticks (contato de super, espera do projétil), algum efeito preso ao golpe está andando (rastro, vapor, corrente, aura em surto) | tira do golpe |
| C9 | **Uma folha, um golpe.** Cada golpe próprio tem a sua folha de 8 desenhos. Folha dividida entre dois golpes, ou golpe montado com 2 ou 3 desenhos fatiados de outra folha, não passa: não sobra desenho para a antecipação (C1) nem para a recuperação (C2) | tabela de golpes: entre os golpes próprios nenhum nome se repete na coluna Folha |
| C10 | **Ritmo próprio.** Golpes da mesma corrente não repetem a notação de tempos: o que abre entra rápido, o do meio segura, o último carrega. Notação igual golpe após golpe é metrônomo | tabela de golpes: notação e início/ativo/total diferentes de um golpe para o seguinte |
| C11 | **Sem sorteio.** Nenhum `random` escolhe animação, tempo ou alcance. Variação só determinística (alterna pelo contador de uso) e só de desenho: o frame data é o mesmo nas variantes | grep por `random` nos estados de golpe |
| C8 | **Frame data intacto.** Soma de ticks, caixa por tick e tick em que a caixa liga iguais aos da tabela do kit | assert do gerador e robô |

C5 afrouxa a "troca seca" da regra 7 só no sentido de exigir smear ou desenho de passagem; não libera entremeio
automático. É a decisão 1 da seção 8.

### 2.2 Efeito e aura (os números de aceite do `aura_animada.md`, medidos por `ferramentas/medir_aura.py`)

| # | Aceite | Limite |
|---|---|---|
| E1 | mesmo quadro de uma camada na tela | no máximo 3 ticks (`tempo` da camada ≤ 3; padrão 2); camada com menos de 8 quadros o `aura.py` recusa |
| E2 | mudança entre quadros do vídeo no loop | percentil 95 / mediana ≤ 2,5; maior / mediana ≤ 3,5; nenhum quadro parado |
| E3 | volta do loop (último desenho para o primeiro) | ≤ 2,5x a mediana |
| E4 | grade do pixel | no loop o motor **não escala nem gira** nada: escala 1 e ângulo 0 em toda camada e toda partícula. O que cresce, gira ou balança é **assado em quadros** (`aura.reduzir`, `aura.girar_loop`, `aura.ondular`, `escala`/`giro` da `Particula`). A escala do motor só sai de 1 ligando, desligando e no surto, e anda ≤ 7% por tick |
| E5 | camadas vivas e fora de fase | a posição muda em ≥ 90% dos ticks, no máximo 1 px por tick (tremor incluído); correlação da posição < 0,9 em módulo entre qualquer par; elementos diferentes ao mesmo tempo |
| E6 | surto | escala passa de 1,05; animação a 1 quadro por tick; folga de 90 ticks entre um surto e o próximo. O gatilho é **super e especial escolhido** (`StateNo = [3000, 3999]` mais `disparo_surto()` nos que merecem), não a faixa inteira dos especiais |
| E7 | virada | não é corte: as camadas apagam, trocam de lado 3 a 8 ticks depois do lutador e voltam |
| E8 | franja | 0 pixel do fundo (`#00FF00` ou magenta) a mais |
| E9 | corpo legível | medido **por faixa** contra o mesmo desenho sem aura, no loop **e no surto**: tronco ≥ 97%, pernas ≥ 95%, pés ≥ 60% dos pixels do corpo iguais. Na frente do corpo só existe névoa rasteira: camada `"frente"` com no máximo 13% da altura do lutador acima dos pés, alfa ≤ 0,5 contando o surto, e que não é cópia de outra camada. Partícula nunca passa na frente. O `aura.py` recusa montar fora disso |
| E10 | tamanho | aura ≥ 2x a altura do lutador |
| E11 | desligar | nenhum `Explod` vivo depois do fade (cerca de 35 ticks) |
| E12 | efeito solto e partícula | ≥ 6 desenhos, 2 ticks cada, nasce e morre com fade ou escala; **nunca 1 sprite parado**. Peça de assinatura (elo, ferradura, nota, lâmina, anel) tem ≥ 4 desenhos próprios dela virando; farelo miúdo (lasca, fagulha de 3 a 5 px) pode ser 1 desenho com giro e escala assados. Partícula de um desenho só, sem giro nem escala, o `aura.py` recusa |
| E13 | HUD na frente | nas caixas da vida, do retrato, do nome e do poder, ≤ 0,5% dos pixels muda com a aura ligada (o HUD do jogo tem `layerno = 1`) |
| E14 | custo | no máximo 30 `Explod` vivos por aura no pior caso (camadas + partículas no surto); o `aura.py` faz a conta e recusa montar acima |
| E15 | nunca para | a aura roda no `[Statedef -4]`: segue viva em superpausa de outro, com o lutador em estado custom (agarrado), na intro e na pose de vitória; antes da intro de cada round não sobra `Explod` |
| E16 | espalhamento das partículas | duas peças seguidas nascem a ≥ 20% da área uma da outra (o `resumo()` da aura imprime); nada de fila que anda |

E1 a E11 e E13 a E15 são medidos em filme pelo `medir_aura.py` (E15 no roteiro `extra`); E12 confere-se no `.air` e
na tira; E16 sai da conta do `aura.py`. Limite conhecido do teste: E2 foi afrouxado depois de ver os dados (o
gravador da sandbox pula e repete quadros). **Não testado em nenhum filme:** `mistura="soma"`, golpe recebido com
dano, e a aura num lutador de verdade (só o `escrever_sff` do Hazak foi rodado no host com os quadros da aura: as
cores saíram exatas, mas ali a aura não disputava as 240 cores com as faíscas).

### 2.3 O que o `aura.py` faz e o que fica com o gerador

O `aura.py` entrega: camadas em loop presas ao lutador (deriva, tremor e alfa pelo motor; crescer, girar e balançar
assados no desenho), partículas (nascem numa área, andam, giram, somem), fade de entrada e saída, virada suave,
**um** tipo de reação, o surto, e `esconde`: uma camada apaga enquanto uma condição vale. Reações específicas de cada
boss (o garanhão dar o coice junto, as asas fecharem na defesa, a lâmina do leque estocar, o anel soltar onda no
pouso) **não estão no `aura.py`**: são `Explod` avulsos do gerador, disparados no estado do golpe; a camada em loop
que a reação substitui leva `esconde=` com a mesma condição, para não aparecerem dois garanhões nem dois pares de
asas. Em cada lutador elas aparecem em "Reações fora do `aura.py`". Também não há hoje: órbita com troca de plano
(partícula não passa na frente do corpo, de propósito), camada que atrasa em relação ao corpo, e troca de animação
de uma camada viva (`anim` não troca por `ModifyExplod` neste motor).

Em todos os dicionários abaixo: `RAIZ` e `sprites` são os do gerador; tamanhos em px do jogo (tela 320x240, lutador
perto de 110 px); **`base=9600` em todos** (em 2026-11-11 o maior número que algum gerador usa é 9305, no CK, que já
ocupa 9300 a 9305; depois de montar, `AURA.conferir(grupos=..., acoes=..., explods=...)` falha se bater). Posições e
amplitudes são ponto de partida, a acertar no filme. Os cinco foram **montados** com arte de mentira (as folhas
`fx_aura_*` não existem): o `aura.py` aceitou os limites da frente, o teto de 30 `Explod` e as partículas; nenhum
rodou no motor. Folha marcada FOLHA NOVA não está em fila nenhuma.

Camada que vem do Blender (`docs/arcade/aura_blender.md`) já chega em laço e na grade: entra com
`aura.ler_quadros(pasta)` no lugar da linha `recortar_folha`/`alongar_loop`, sem `ondular`.

### 2.4 Ordem de ligação comum a todos os geradores

1. Converter as folhas boss para `quadros_arcade` e ligar a troca de desenho da forma (o que cada gerador já usa:
   `RemapSprite` ou animação +10000). Antes, tirar o que apaga ou sobrescreve arte desperta (ver cada lutador).
2. **Remover** a aura antiga (`aura_cns()`, Explods 9210/9211, PalFX de aura) e pôr `AURA.registrar(sprites)`,
   `air += AURA.air()` e `AURA.cns()` num **`[Statedef -4]`** (se o lutador não tem, `AURA.cns(cabecalho=True)` já
   traz a linha). É -4 e não -2 porque o -2 para em pausa e superpausa. Não empilhar a nova sobre a velha. No
   Hazak, o `registrar(s)` devolve o conjunto que tem de entrar no `manter` do `escrever_sff`.
3. Dados dos golpes próprios num módulo só de dados (`pengaro_extra.py`, `gutto_boss.py`, `raiclaven_boss.py`,
   `hazaki_diabo.py`, `ck_boss.py`) e os estados à mão.
4. Efeitos de golpe (acerto, rastro, projétil) e as reações fora do `aura.py`.
5. Entradas do `.cmd` na ordem: Despertar → supers → 2 toques → agarrões → kombos → correntes → direcionais → normais.
6. `movelist.dat` e ficha batendo com o `.cmd`.
7. Robô do lutador na sandbox, depois filme (`filmar_sandbox.py`) com tira por golpe, e `medir_aura.py` na aura do
   lutador de verdade. Só então marcar a linha de fluidez do checklist (seção 9 das regras).

## 3. Pengaró Endiabrado

Fontes: `docs/fichas/pengaro.md`, `ferramentas/pengaro_extra.py`, `ferramentas/gerar_pengaro.py` e o Lote 7 de
`docs/arcade/fila.md`, todos na branch `endiabrado`. Tempos da tabela: calculados com a fórmula do gerador, não
medidos no motor.

**Estado hoje.** O Despertar existe e cumpre a contagem da regra 4 (2 correntes, 6 normais, 4 especiais, 1 projétil,
1 kombo, 1 super), mas **todo golpe próprio reaproveita folha da base em outra ordem**: nenhum usa corrente, sombra ou
casaco como desenho. As 24 folhas `e_` dos grupos A e B do Lote 7 estão geradas no modelo boss e **não ligadas**; o
grupo C (inclui `e_despertar` e as três `fx_aura_*`) não foi gerado. A aura em jogo são dois Explods antigos
(9210/9211) que não reagem a nada. Ativação: `x + y` com barra cheia, estado 2000, `var(20) = 600` (10 s fixos), dano
x1,45, avanço x1,22.

### 3.1 Golpes do boss

P = próprio do boss; "Folha hoje" é a da base que o gerador usa (vira `e_<folha>` pela troca da forma); "Folha
pedida" dá pose própria ao golpe. Dano = base (com x1,45).

| Estado | Nome | Comando (desperto) | Folha hoje | Folha pedida | iní/ativo/total | Dano | Alc. | Propriedade |
|---|---|---|---|---|---|---|---|---|
| 3410 | Revolta de Corrente | y | martelo | `e_c_revolta` | 7/8/31 | 55 (80) | 78 | médio, cancela em especial |
| 3411 | Sola de Ferro | y, y | chute_baixo | `e_c_sola_ferro` | 7/8/39 | 60 (87) | 72 | cancela se acertou |
| 3412 | Cabeçada Escura | y, y, y | cabecada | `e_c_cabecada_escura` | 10/8/36 | 70 (102) | 52 | curto |
| 3413 | Roda da Possessão | y x4 (3 acertos) | compasso | `e_c_roda` + `_b` | 8/8/43 | 120 (174) | 90 | finalizador, derruba, avanço 2,2 |
| 3420 | Calcanhar Sombrio | b (neutro) | chute_alto | `e_c_calcanhar` | 7/8/39 | 60 (87) | 76 | cancela; abre o kombo |
| 3421 | Afastar Pesado | b, b | afastar | `e_c_afastar_pesado` | 7/8/39 | 70 (102) | 82 | empurra (vel -7) |
| 3422 | Armada Torta | b, b, b | armada | `e_c_armada_torta` | 8/12/38 | 75 (109) | 80 | por cima |
| 3423 | Chute da Corrente Partida | b x4 (3 acertos) | armada (a mesma do 3422) | `e_c_corrente_partida` + `_b` | 10/18/52 | 125 (181) | 86 | finalizador, derruba |
| 3430 | Mão de Chão Possuída | ↓ + y | cabecada | `e_mao_chao` | 11/8/39 | 95 (138) | 46 | lançador (-2, -10) |
| 3435 | Foice Escura | ↓ + b | rasteira | `e_foice` | 11/10/54 | 100 (145) | 90 | baixo, derruba |
| 3431 | Tranco Possuído | → + y | martelo (vai-e-volta 4, 3, 4) | `e_tranco` | 9/8/42 | 50+60 | 70 | 2 acertos, avanço 2,4 |
| 3432 | Passo de Sombra | → + b | chute_alto | `e_passo_sombra` | 11/10/51 | 100 (145) | 92 | por cima, longo |
| 3433 | Palma Torta | ← + x | soco | `e_palma` | 5/7/24 | 58 (84) | 66 | rápido, recua |
| 3434 | Puxada Sombria | ← + a | chute_baixo | `e_puxada` | 7/8/39 | 70 (102) | 66 | derruba, recua |
| 348 | Compasso Possuído | b, a | compasso | (usa `e_c_roda`) | 8/8/43 | 65 (94) | 80 | 2º do kombo b, a, x |
| 349 | Caneta Sombria | b, a, x | caneta | `e_caneta` (Lote 7 B) | 8/12/46 | 80 (116) | 76 | baixo, derruba |
| 3400 | Mão de Sombra | ↓ ↓ + x | golaco (39 ticks parado no último desenho) | `e_mao_sombra` + `fx_mao_sombra` | solta no 25 / total 64 | 50 x 2 | tela | projétil que acelera, 1 por vez |
| 3401 | Chute da Corrente | ↓ ↓ + y | chute_alto | `e_chute_corrente` + `fx_corrente_chicote` | 9/10/52 | 115 (167) | 88 | avanço 5,0, derruba |
| 3402 | Sombra Atravessada | ↓ ↓ + a | rolamento | `e_atravessa` + `_b` | 6/8/41 | 75 (109) | 70 | atravessa invencível, chega virado |
| 3403 | Queda Escura | ↓ ↓ + b | bicicleta | `e_queda_escura` | sobe no 4, bate a partir do 8 | 105 (152) | 70 | mergulho, derruba, `fx_cratera` |
| 3100 | Saideira Sombria | ← → ↓ + a/b (1000 de barra, encerra o Despertar) | soco/chute/rasteira colados | `e_saideira_a` + `e_saideira_b` | 8 acertos (ticks 4 a 32) + final no 36 | 8x47 + 60 | perto | super, invencível 4 ticks |
| 2000 | Despertar | x + y, barra cheia | despertar_a + despertar_b | `e_despertar` (Lote 7 C) + `e_despertar_b` | 16 desenhos, 112 ticks | 0 | empurra | invencível |

Continuam da base, só com desenho `e_`: normais x (200), a (230), agachados e os quatro do ar, correntes x e a,
kombos "Alto e Baixo" e "Lançador", Latada (no Despertar solta a 2ª lata "Dobrada"), Rolê por Trás, Compasso, Armada,
Caneta, Mão de Chimpá, Sola de Várzea, Bando da Várzea e os agarrões. A Garrafada (1600/1601) é bloqueada no
Despertar, então `→ ← + x/y` fica livre.

**Propostas (nada disto está na ficha; alvos, não dados do projeto):**

| Estado | Nome | Comando | Folha | iní/ativo/total | Dano | Alc. | Ideia |
|---|---|---|---|---|---|---|---|
| 3404 / 3405 | Chicote de Elo | → ← + x / y | `e_chicote` + `_b` + `fx_corrente_chicote` | 14/6/48 e 18/6/54 | 70 / 90 | 150 / 190 | a corrente da algema estica como chicote; a fraca bate no meio e empurra, a forte bate por cima e derruba no lugar. **Não puxa** (puxar com corrente é só do Raiclaven, decisão 48). Ocupa o papel do 2º projétil |
| 1000 / 1001 (ramo desperto) | Pedra de Sombra | ↓ → + a / b | `e_bola` redesenhada + `fx_pedra` | os da Latada | iguais | tela | boss de mãos vazias chuta uma pedra da aura em vez de lata |
| 835 / 836 | Algema | colado, ← → + y | `e_algema` + `_b` + `e_algema_vitima` | 5 de pega | 60 + 90 | colado | laça com a corrente, gira e bate no chão dentro do anel (no lugar da garrafada 830/831) |
| 3406 | Véu do Mestre | ← ↓ + x / y | `e_veu` | 4/14/40 | 0 (contra 90) | curto | gira o casaco: apaga projétil; se tomar golpe no ativo, some e reaparece batendo |
| 3110 | Prisão do Quilombo | ← → ↓ + x / y, 2 estoques | `e_prisao_a` + `e_prisao_b` + `fx_correntes_chao` | cena de 90+ | ~330 | meia tela | correntes sobem do anel, prendem, a coluna engole (no lugar do Bando da Várzea) |
| 3436 | Elo de Cima | no ar, ↓ + b | `e_elo_cima` | 8 / até pousar | 85 | diagonal | mergulho com a corrente do tornozelo esticada |

### 3.2 Efeitos e como cada um se mexe

- **Acerto:** `sombra_acerto` (fraco) e `sombra_forte` (forte) já existem. Acrescentar no forte e no finalizador o
  **estilhaço de elo**: 2 ou 3 elos saem do ponto de contato e caem com gravidade (`Explod` com `accel y`), girando.
  No finalizador, mais a onda do anel.
- **Rastro:** `sombra_rastro` (9212) segue o membro. Nos golpes de corrente entra `fx_corrente_chicote` (enrolada,
  estica em arco, reta no contato, onda voltando, recolhe) presa à mão ou ao pé.
- **Mão de Sombra:** `fx_mao_sombra`, mão de fumaça que abre e fecha os dedos em loop, com rastro que alonga
  conforme acelera (escala x do rastro ligada à velocidade).
- **Sombra Atravessada:** corpo vira silhueta, 3 pós-imagens violeta, poça de sombra abrindo na saída e na chegada.
- **Queda Escura:** `fx_cratera`, rachadura violeta que abre em 6 ticks e apaga em 30.
- **Saideira:** fundo escuro desde a superpausa, coluna em surto, um elo estoura a cada um dos 8 acertos, no final o
  anel explode para fora.
- **Transformação (2000):** anel nasce pequeno e abre → rachaduras correm do centro → coluna sobe do chão em 12
  ticks → detritos arrancados sobem → clarão violeta e empurrão. No fim do Despertar a coluna desaba para dentro do
  anel (o fade de saída do `aura.py` já encolhe para os pés; a ação "desaba" desenhada fica para depois).
- **No corpo, não na aura:** chifres de fumaça e brasa da barra da calça. Só mexem se o desenho mexer: todo MOTION
  de `e_` pede que tremulem.

### 3.3 Aura (dicionário para o `aura.py`)

```python
import aura
M = aura.Movimento
F = RAIZ / "sprites/pengaro/quadros/folhas"
coluna = aura.ondular(aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura_coluna.png"), altura=236),
                                        total=32), amplitude=3)            # o balanço é assado, não giro do motor
anel = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura_anel.png"), largura=176, ancora="centro"),
                         total=24, metodo="mistura")
chicotes = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura_chicotes.png"), altura=190),
                             total=24)                                     # FOLHA NOVA: correntes chicoteando
nevoa = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura_nevoa.png"), altura=13), total=24)  # NOVA
pecas = aura.recortar_folha(F / "fx_aura_detritos.png")   # 8 células: 4 desenhos da pedra virando, 4 do elo virando
pedra = aura.enquadrar(pecas[0:4], altura=11, ancora="centro")
elo = aura.enquadrar(pecas[4:8], altura=13, ancora="centro")
AURA = aura.Aura("pengaro", ligada="var(20) > 0", surto="StateNo = [3000, 3999] && Time = 1", base=9600, camadas=[
    aura.Camada("anel", anel, plano="chao", pos=(0, -3), surto_incha=0.25, mov=M(deriva=(0, 0), alfa=0.9)),
    aura.Camada("coluna", coluna, plano="tras", pos=(-4, 2), mov=M(deriva=(3, 4))),
    aura.Camada("chicotes", chicotes, plano="tras", pos=(12, 2), mov=M(deriva=(5, 2), deriva_periodo=113, alfa=0.7)),
    aura.Camada("nevoa", nevoa, plano="frente", pos=(2, 3), surto_incha=0.0, surto_alfa=0.08,
                mov=M(deriva=(3, 0.5), deriva_periodo=90, alfa=0.4, respira=0.2)),
], particulas=[
    aura.Particula("pedra", pedra, periodo=12, vida=64, area=(-58, 0, 58, -24), vel=(0, -0.55), vel_var=(0.5, 0.5),
                   giro=(0, 90), semente=1),
    aura.Particula("elo", elo, periodo=17, vida=78, area=(-52, -4, 52, -30), vel=(0, -0.45), vel_var=(0.6, 0.4),
                   giro=(-40, 140), semente=2),
    aura.Particula("lasca", aura.pedra_procedural(5), periodo=10, vida=40, area=(-64, 0, 64, -10), vel=(0, -0.9),
                   giro=(0, 200), escala=(1.0, 0.6), semente=3),
])
```

Mudou em relação à primeira versão do kit: a camada "chicotes" era a coluna de fumaça espelhada e reduzida (não
era chicote nem corrente) e a camada "pes" era a mesma coluna achatada por cima dos pés. Agora os chicotes pedem
**folha própria** (`fx_aura_chicotes`: 2 ou 3 correntes saindo da fumaça e estalando, 8 desenhos) e a frente é só a
névoa rasteira (`fx_aura_nevoa`, 13 px de altura; enquanto não existir, `aura.nevoa_rasteira(124, 13, 24)` em
violeta). Pedra e elo têm 4 desenhos cada, virando; nenhuma partícula passa na frente do corpo.

Enquanto as folhas não existirem, a aura "sombra" do `gerar_teste_aura.py` (toda por código) serve de substituta: é
a que foi filmada. Com `fx_aura_coluna_b` (16 desenhos), a coluna sai de `recortar_folha` das duas folhas juntas e o
`alongar_loop` vai a 48.

**Reações fora do `aura.py`:** onda do anel (cópia do anel em soma, escala 1,0 a 1,6 em 10 ticks) no pouso e em todo
finalizador; coluna encolhendo e piscando ao apanhar; coluna falhando de 4 em 4 ticks nos últimos 120 ticks do
`var(20)`; detritos sugados para o corpo no super; empurrão dos detritos na direção do golpe. O atraso da coluna ao
andar (ficar 4 a 6 px para trás) não existe no `aura.py`: a `deriva` dá o balanço, não o atraso.

### 3.4 Fluidez do corpo

Atrasa em toda pose de recuperação: barra rasgada do casaco, as duas pontas da corda, os quatro pedaços de corrente
das algemas, o cabelo. Texto fixo para todo MOTION novo: *"coat hem, rope tails and chain links arrive one frame late
and keep swinging"*.

- **Ginga e andar** são o que mais se vê e o mais duro (6 desenhos a 8 ticks). `e_ginga_b` e `e_anda_b` primeiro.
  A `e_anda` gerada repete 1 a 4 em 5 a 8 (as pernas não alternam): refazer.
- **Deslocamento:** hoje `VelSet` constante com parada seca. Trocar por rampa de 3 ticks e `VelMul 0,8` do fim do
  ativo em diante (3413, 3431, 3401, 3433, 3434).
- **Único teleporte:** `PosAdd x = p2dist x + 36` no Rolê e na Sombra Atravessada. Trocar por 6 a 8 ticks de
  velocidade alta com o corpo em silhueta.
- **Giros** (3413, 3423): 8 desenhos dão fatias de 45 graus; pedem folha `_b`.
- **3431 Tranco:** o vai-e-volta 4, 3, 4 é proibido; precisa da folha com dois contatos.
- **3400 Mão de Sombra:** 39 ticks no mesmo desenho; a folha própria traz a recuperação.
- **3100 Saideira:** colagem de 4 em 4 ticks; 16 desenhos no mínimo.

### 3.5 Folhas

Na fila (Lote 7): `e_ginga`, `e_anda`, `e_soco`, `e_chute_alto`, `e_martelo`, `e_afastar`, `e_apanha`, `e_queda`,
`e_levanta`, `e_defesa`, `e_agachado`, `e_pulo`, `e_chute_baixo`, `e_baixo_soco`, `e_cabecada`, `e_rasteirinha`,
`e_rasteira`, `e_ar_soco`, `e_bicicleta`, `e_bola`, `e_compasso`, `e_armada`, `e_caneta`, `e_rolamento`, `e_agarrao`,
`e_golaco`, `e_lata`, `e_provoca`, `e_vitoria`, `e_derrota`, `e_despertar`, `fx_aura_coluna`, `fx_aura_anel`,
`fx_aura_detritos`.

**O kit pede e a fila não tem** (corpo em fundo magenta, efeito em fundo verde; 8 desenhos por folha; em toda folha
de corpo acrescentar a frase fixa da 3.4). Prioridade 1 = sem ela o golpe continua com pose da base; 2 = fluidez; P =
só se a proposta for aprovada.

| Pri | Folha | MOTION |
|---|---|---|
| 1 | `e_ginga_b` | second half of the idle loop, frames 9-16 continuing `e_ginga`: weight shifts to the back foot and returns, shoulders roll the other way, smoke horns flicker, last frame flows into frame 1 of `e_ginga` |
| 1 | `e_anda_b` | second half of the walk cycle, frames 9-16: the OTHER leg leads, arms counter-swing, last frame flows into frame 1 of `e_anda`; feet never slide |
| 1 | `e_c_revolta` | chain backfist: 1 guard, 2 shoulder winds back, 3 smear, 4-5 forearm swings across with the wrist shackle chain stretched straight at contact, 6-8 arm recoils in three steps while the chain coils back |
| 1 | `e_c_sola_ferro` | stamping front kick with the sole: 1 guard, 2 knee chambers, 3 smear, 4-5 leg locked out at belly height, 6-8 foot comes down in three steps, ankle chain whipping after the foot |
| 1 | `e_c_cabecada_escura` | short headbutt: 1 guard, 2-3 torso leans back and loads, 4-5 head driven forward, hair and smoke horns overshoot, 6-8 head returns in three steps |
| 1 | `e_c_roda` | spinning compass kick finisher, first half: 1 guard, 2 hand goes to the floor, 3-4 body turns a quarter each frame, 5-6 heel sweeps through at head height with the coat opening like a fan, 7-8 leg continues past the target |
| 2 | `e_c_roda_b` | second half of the spin: 1-3 the leg finishes the circle, 4-5 foot plants, 6-8 he rises back to guard while the coat hem closes last |
| 1 | `e_c_calcanhar` | high heel kick: 1 guard, 2 knee up with torso leaning away, 3 smear, 4-5 heel extended at face height, 6-8 leg folds and lands in three steps |
| 1 | `e_c_afastar_pesado` | heavy two-handed shove: 1 guard, 2-3 both palms pull to the chest, 4-5 both arms thrust out at chest height, 6-8 he slides back half a step and the coat settles |
| 1 | `e_c_armada_torta` | crooked spinning hook kick coming down from above: 1 guard, 2-3 he turns his back, 4 smear, 5-6 leg whips over and down, 7-8 lands sideways and squares up |
| 1 | `e_c_corrente_partida` | broken-chain spin kick finisher, first half: 1 guard, 2-4 full wind-up turn with the ankle chain trailing in a circle, 5-6 leg fully extended at chest height, chain straight, 7-8 follow-through |
| 2 | `e_c_corrente_partida_b` | second half: 1-3 leg comes around and down, 4-5 he lands low, 6-8 stands in three steps, chain and coat still swinging |
| 1 | `e_mao_chao` | rising palm from a crouch: 1 crouch with one hand on the floor, 2-3 loads, 4-5 open palm shoots straight up above the head, 6-8 he comes down to standing in three steps |
| 1 | `e_foice` | low scythe sweep with both hands on the floor: 1 crouch, 2-3 hands plant, 4-6 the leg sweeps a wide low arc, coat dragging on the ground, 7-8 he gathers the leg and rises |
| 1 | `e_tranco` | two shoulder-and-forearm rams while stepping forward: 1 guard, 2 loads, 3 first ram (contact), 4 short recoil, 5 second ram deeper (contact), 6-8 recovery in three steps; the two contact poses are clearly different |
| 1 | `e_passo_sombra` | long stepping overhead axe kick: 1 guard, 2-3 long slow leg raise high above the head (the warning), 4 smear, 5-6 heel comes straight down far in front, 7-8 recovery, rope and coat rising then falling |
| 1 | `e_palma` | fast retreating palm strike: 1 guard, 2 short load, 3-4 open palm snaps out at face height while the body leans back, 5-6 hops half a step back, 7-8 settles |
| 1 | `e_puxada` | pulling hook kick that drags the opponent down: 1 guard, 2 leg reaches out past the target, 3-5 heel hooks and pulls back toward him, 6-8 foot returns and he steps back |
| 1 | `e_mao_sombra` | shadow hand cast, body only (the hand of smoke is `fx_mao_sombra`): 1 guard, 2-3 rear arm draws back with fingers clawed, 4 thrust forward with open hand, 5 holds the pose, 6-8 arm lowers in three steps and returns to guard |
| 1 | `e_chute_corrente` | lunging chain kick: 1 guard, 2 crouches to launch, 3-4 flies forward leg first, 5-6 leg locked out with the ankle chain trailing straight behind, 7-8 lands and skids to a stop |
| 1 | `e_atravessa` | passing through as a shadow, first half: 1 guard, 2-3 he sinks and the body darkens to a silhouette, 4-8 the silhouette stretches forward low to the ground |
| 2 | `e_atravessa_b` | second half: 1-3 the silhouette gathers again, 4-5 he rises facing the other way with a short strike, 6-8 colour returns and he settles into guard, coat arriving last |
| 1 | `e_queda_escura` | diving drop: 1 crouch, 2 jumps, 3 top of the jump tucked with the coat up, 4-5 dives foot first diagonally, 6 impact crouch, 7-8 rises in two steps |
| 1 | `e_saideira_a` | super, first half of an eight-hit flurry: eight different strikes in a row, palm, elbow, knee, backfist, low kick, hook, headbutt, spinning backfist, each a clear contact pose |
| 1 | `e_saideira_b` | super, second half: 1-2 he pulls both fists back, 3-4 huge double palm blast forward, 5-8 recovery, chest heaving, chains and coat settling |
| 2 | `e_despertar_b` | second half of the transformation: 1-2 the coat falls on his shoulders, 3-4 shackle chains snap, 5-6 smoke horns grow, 7-8 arms thrown wide with the head back |
| 1 | `fx_aura_coluna_b` | frames 9-16 of the smoke column loop continuing `fx_aura_coluna`: the same rising violet-black smoke, shapes travelling upward, last frame flows into frame 1 of `fx_aura_coluna` |
| 1 | `fx_corrente_chicote` | a chain whipping to the right: 1 coiled, 2-3 uncoils in an arc, 4 fully straight, 5 a wave travels back along it, 6-8 recoils |
| 1 | `fx_mao_sombra` | a large hand made of violet-black smoke flying to the right: fingers open and close over the loop, a trail of smoke behind the wrist |
| 2 | `fx_cratera` | ground crack seen from the side: 1 a small violet crack, 2-4 cracks spread outward and glow, 5-8 the glow dies and the cracks fade |
| P | `e_chicote` | chain whip, first half: 1 guard, 2-4 wrist circles overhead with the shackle chain uncoiling, 5-6 arm throws forward, 7-8 arm fully extended, hand open toward the right |
| P | `e_chicote_b` | chain whip, second half: 1-2 holds the extended arm, 3-5 yanks the arm back hard, 6-8 the chain returns and wraps the forearm |
| P | `e_algema` | chain throw, first half, only him drawn: 1 guard, 2-3 loops the chain around an unseen opponent at arm's length, 4-8 spins in place hauling the weight around |
| P | `e_algema_b` | chain throw, second half: 1-3 heaves the weight overhead, 4-5 slams it to the floor in front of him, 6-8 lets the chain go and straightens |
| P | `e_algema_vitima` | the victim of the chain throw, generic fighter silhouette, eight frames matched one to one with `e_algema`: bound at the waist, dragged around in a circle |
| P | `e_veu` | coat veil: 1 guard, 2-3 grabs the coat edge, 4-6 spins once with the coat spread wide like a curtain, 7-8 the coat falls back |
| P | `e_prisao_a` | super, first half: 1 guard, 2-3 drops to one knee and slams a palm on the floor, 4-8 holds the palm down, straining, head rising |
| P | `e_prisao_b` | super, second half: 1-3 stands slowly raising a clenched fist, 4-5 closes the fist hard, 6-8 pulls the fist down to his side |
| P | `e_elo_cima` | air dive: 1 tucked in the air, 2-3 extends one leg diagonally down with the ankle chain stretched behind, 4-6 holds the dive, 7-8 landing crouch |
| P | `fx_correntes_chao` | chains bursting from the ground: 1 cracks, 2-4 four chains shoot up, 5-6 cross over each other, 7-8 pull tight |
| P | `fx_pedra` | a fist-sized dark stone with violet glowing cracks tumbling to the right, eight rotation frames |

### 3.6 Ordem de ligação no `gerar_pengaro.py`

1. Ligar as 24 `e_` já geradas (grupos A e B) na troca da forma; refazer `e_anda`.
2. Aura nova no lugar do `aura_cns()` (9210/9211), primeiro com a coluna e o anel por código, depois com as folhas.
3. Rampa e freio nos avanços; viagem de 6 a 8 ticks no lugar do `PosAdd` do Rolê e do 3402.
4. Folhas próprias golpe a golpe, começando por 3431 (vai-e-volta), 3423 (folha repetida) e 3400 (corpo parado).
5. Efeitos: estilhaço de elo, `fx_corrente_chicote`, `fx_mao_sombra`, `fx_cratera`, onda do anel.
6. Propostas aprovadas, por último.

## 4. Gutto, o senhor da guerra garanhão

Fontes: `docs/fichas/gutto.md`, `ferramentas/gerar_gutto.py`, `ferramentas/pengaro_extra.py`,
`ferramentas/folhas_gutto.py` (checkout `efeitos`) e a seção do Gutto em `fila_bosses.md`. Tempos da 4.1: calculados
com a fórmula do gerador; os das propostas são alvo.

**Estado hoje, o achado que muda o plano: o kit despertado do Gutto é o do Pengaró, byte a byte.** O
`gerar_gutto.py` não tem dado de golpe próprio; importa `gerar_pengaro` e, por ele, `pengaro_extra.py`. Só mudam a
arte (`e_<folha>`) e os nomes no `movelist.dat`. A aura são os Explods 9210/9211 do Pengaró mais um PalFX vermelho. O
visual do conceito (ombreira com espinhos, coleira com corrente partida, braceletes e caneleiras de ferro, faixa de
corda com borla, saiote rasgado com argolas, chifres curvos, crina e rabo preto-vermelhos, rachadura acesa no peito)
é diferente do das 28 folhas `e_*` de 2026-11-07: **todas precisam ser refeitas**, e a fila já pede isso.

Como `gerar_gutto.py` não se edita nesta rodada, o executor entrega `ferramentas/gutto_boss.py` (dados no formato
`Novo` do `pengaro_extra`, trechos de CNS/AIR/CMD e a aura); o gancho no gerador fica para depois.

### 4.1 Golpes do boss

Os estados já existem (herdados); o que muda é o **dado**, que passa a ser do Gutto, e a folha. A primeira versão
desta tabela repetia a do Pengaró número por número (era o que o gerador dá hoje) e dividia folhas entre golpes: não
passava na própria regra do dono. Os números abaixo são o **alvo do Gutto**, não o herdado: ele é o pesado do
elenco. Entra de 2 a 6 ticks mais tarde que o Pengaró, bate de 10 a 25% mais forte e mais longe, dá menos acertos
por golpe, empurra mais, e três golpes aguentam um golpe fraco na subida (armadura). Nada medido em jogo. Dano base
(no Despertar, x1,45). Cada golpe tem a sua folha (C9).

| Estado | Nome | Comando | Folha | iní/ativo/total | Dano | Alc. | Propriedade |
|---|---|---|---|---|---|---|---|
| 3410 | Marreta de Ferro | y | `e_martelo` | 10/6/36 | 68 | 84 | avança 1,2; aguenta 1 golpe fraco do tick 4 ao 10; cancela em especial |
| 3411 | Pisão de Casco | y, y | `e_chute_baixo` | 9/5/35 | 62 | 64 | baixo; treme a tela 4 ticks; cancela se acertou |
| 3412 | Chifrada | y, y, y | `e_cabecada` | 12/7/40 | 82 | 58 | empurra -9 |
| 3413 | Coice de Roda | y x4 (2 acertos) | **FOLHA NOVA** `e_coice_roda` | 13/5+5/50 | 60+85 | 96 | derruba; quica o oponente no canto |
| 3420 | Coice Alto | b | `e_chute_alto` | 9/6/34 | 66 | 82 | abre o kombo |
| 3421 | Empurrão de Casco | b, b | `e_afastar` | 8/9/38 | 58 | 88 | empurra -11, o maior empurrão do elenco |
| 3422 | Gancho Giratório | b, b, b | `e_armada` | 11/10/42 | 84 | 78 | por cima |
| 3423 | Coice de Aríete | b x4 (1 acerto) | **falta** `e_coice_final` | 16/6/58 | 150 | 92 | um coice só, pesado: derruba e joga a meia tela; aguenta 1 golpe fraco do tick 6 ao 16 |
| 3430 | Chifrada Subindo | ↓ + y | **FOLHA NOVA** `e_chifrada_sobe` | 9/9/44 | 104 | 50 | antiaéreo, lança (-1, -11,5) |
| 3431 | Patada Dupla | → + y | `e_soco` (a folha já tem dois golpes) | 11/4+4/46 | 44+72 | 74 | 2 acertos, avança 2,0 |
| 3432 | Pisão de Cima | → + b | **FOLHA NOVA** `e_pisao_cima` | 15/7/52 | 112 | 80 | por cima; onda baixa de 40 px no pouso do casco |
| 3433 | Garra de Recuo | ← + x | **FOLHA NOVA** `e_garra_recuo` | 6/5/27 | 52 | 70 | recua 1,4 |
| 3434 | Coice de Recuo | ← + a | **FOLHA NOVA** `e_coice_recuo` | 9/6/41 | 78 | 86 | derruba; ele sai 30 px para trás |
| 3435 | Varrida de Rabo | ↓ + b | `e_rasteira` | 13/12/56 | 92 | 104 | baixo; a rasteira mais longa do elenco |
| 348 | Coice Giratório | b, a | `e_compasso` | 10/7/40 | 72 | 84 | 2º do kombo |
| 349 | Carrinho de Guerra | b, a, x | `e_caneta` | 11/14/52 | 88 | corre 70 px | baixo, derruba |
| 3400 | Bufada de Fogo (movelist: "Beijo do Cavalo") | ↓ ↓ + x | `e_bola` + `fx_bufada` | solta no 30 / total 70 | 95 x 1 | tela | um projétil só, grande e lento (vel 2,2), some ao bater; 1 por vez |
| 3401 | Estouro de Casco | ↓ ↓ + y | **FOLHA NOVA** `e_coice_corrente` | 12/8/58 | 128 | 94 | avança 4,0, derruba; na guarda tira 30% a mais |
| 3402 | Galope Atravessado | ↓ ↓ + a | `e_rolamento` (na fila já é a investida que passa para trás) | 9/12/48 | 82 | atravessa 120 px | invencível do tick 3 ao 14, chega virado |
| 3403 | Queda do Cavalo | ↓ ↓ + b | `e_bicicleta` | 15 / até pousar | 118 | 76 | salta e mergulha; estouro no chão com onda de 60 px |
| 3100 | Estouro do Garanhão | ← → ↓ + a/b | `e_estouro_a/b/c` + `fx_aura_garanhao_estouro` | 6 / 5 acertos de 12 em 12 + final / ~110 | 60x5 + 120 | tela, a caixa segue o garanhão | super, encerra o Despertar: o garanhão da aura se solta e atravessa a tela pisoteando; o Gutto fecha com o coice. Conferir o desenho contra a decisão 47 |
| 3200 | Fúria do Cavalo | ← → ↓ + x/y | poses de soco e chute | não li | 345 em 3 | 87 | 2 estoques, versão boss do Bando de Chutes |
| 2000 | Endiabrado | x + y, barra cheia | `despertar_boss` (fila: uma folha só) | 114 total | 0 | empurra | invencível |

Folhas novas desta revisão (prioridade 1, MOTION a escrever junto com as da 4.5): `e_coice_roda` (meia-volta e dois
coices de costas, um por perna), `e_chifrada_sobe` (agacha, sobe de chifre), `e_pisao_cima` (levanta o joelho até o
peito e desce o casco), `e_garra_recuo` (tapa de mão aberta saindo de ré), `e_coice_recuo` (coice de uma perna só
pulando para trás), `e_coice_corrente` (corre dois passos e solta os dois cascos). A "Saideira do Cavalo" (os 8
acertos do Pengaró) saiu: o 3100 dele é o Estouro do Garanhão.

Continuam da base com pose de cavalo: normais, correntes x e a, agarrões (o 830 vira mordida, `e_agarrao`), 1000/1001
(sai "dobrada" no Despertar), 1100 a 1501 e o Teleporte de Ginga. O **Beijinho em Arco (1600/1601) é bloqueado** no
Despertar.

**Propostas, para o estilo ser só dele** (casco, chifre, corrente do pescoço e o garanhão). Numeração 3440 a 3479,
que o grep não mostrou em uso; não usar 5000 a 5999 (decisão 4).

| Estado | Nome | Comando | Folhas | iní/ativo/total | Dano | Alcance | Propriedade |
|---|---|---|---|---|---|---|---|
| 3440 / 3441 | Relincho de Guerra | → ← + x / y | `e_relincho_a` + `e_relincho_b` + `fx_relincho` | 12/8/44 e 22/10/60 | 0 / 40 | cone de 120 px à frente | urro de garanhão: x não dá dano, empurra -14 e deixa o oponente 20 ticks sem agir (abre a guarda); y carrega, dá dano e derruba. Substitui o Laço da Corrente, que repetia o chicote que puxa de outros três bosses (decisão 48) |
| 3450 / 3451 | Investida de Chifres | → ↓ + a / b | `e_investida_a` + `e_investida_b` | 12/14/50 e 16/18/60 | 90 / 115 | corre 110 / 170 px | cabeça baixa; b aguenta 1 golpe e quica o oponente no canto |
| 3460 / 3461 | Empinada | ← ↓ + x / y | `e_empinada_a` + `e_empinada_b` | 16/4+6/58 e 20/4+8/66 | 70+40 / 90+50 | cascos por cima + onda baixa de 110 px | empina e desce os dois cascos; cratera; o garanhão da aura desce junto |
| 3470 / 3471 | Ferradura-Faísca (opcional) | ← → + a / b | `e_ferradura_arremesso` + `fx_ferradura_voa` | solta no 14 / total 44 | 55 / 70 | projétil rasteiro, vel 4 / 5,5, quica 1 vez | bate baixo; papel diferente da Bufada |
| 3100 (conteúdo novo) | Estouro do Garanhão | ← → ↓ + a/b | `e_estouro_a/b/c` + `fx_aura_garanhao_estouro` | 6 / 5 acertos de 12 em 12 + final / ~110 | 60x5 + 120 | tela, a caixa segue o garanhão | o garanhão se solta e atravessa a tela pisoteando; o Gutto fecha com o coice |
| 100 | Galope | → → | `e_galope` (fila) + `e_galope_b` | loop | - | - | corrida x1,3 no Despertar, poeira e cratera a cada casco |

### 4.2 Efeitos e como cada um se mexe

Folhas em fundo verde, em `sprites/gutto/efeitos/`. **Nas folhas do corpo não entram raio, garanhão, cratera,
ferradura nem o vapor das narinas** (o conceito mostra tudo junto). Rampa sugerida: (20,0,0) → (150,10,20) →
(255,60,60) → (255,235,235).

- **Acerto:** fraco = `zap-hit` vermelho; forte = `crit-hit` vermelho mais uma **marca de ferradura que estala**
  (`fx_ferradura` da fila), a assinatura dos coices; pisão, Empinada e Queda = `ground-slam` vermelho mais cratera
  nova. Defesa segue neutra.
- **Rastro:** arco de raio vermelho no casco ou no chifre; poeira vermelha na rasteira.
- **Bufada:** cone de fogo vermelho em loop de 8 (`fx_bufada`), com vapor ficando para trás.
- **Laço:** elos em brasa, faísca correndo até a ponta. **Investida:** risco de raio no chão atrás dele.
- **Super:** fundo escurece, o garanhão atravessa, cada pisada dá cratera e tremida, clarão branco no coice final.
- **Transformação:** carga vermelha; três raios caem em pulsos; o garanhão sobe do chão atrás dele
  (`fx_aura_garanhao_nasce`); relincho, onda de choque, crateras nos dois pés. As partículas só ligam no fim.
- **Rachadura do peito:** o PalFX pulsando que já existe; é reforço do corpo, não aura.

### 4.3 Aura (dicionário para o `aura.py`)

```python
import aura
M = aura.Movimento
F = RAIZ / "sprites/gutto/quadros/folhas_arcade"
garanhao = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura_garanhao.png"), altura=232),
                             total=32, metodo="mistura")           # raio: "mistura" ou "dissolve", não "fluxo"
raios = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura_garanhao_raios.png"), altura=232),
                          total=24, metodo="dissolve")             # FOLHA NOVA: só os raios do contorno, sem o corpo
crateras = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura_crateras.png"), largura=150,
                                            ancora="centro"), total=20, metodo="mistura")
ferradura = aura.enquadrar(aura.recortar_folha(F / "fx_ferradura.png"), altura=14, ancora="centro")   # 8 desenhos
faisca = aura.enquadrar(aura.recortar_folha(F / "fx_faisca_casco.png"), altura=7, ancora="centro")    # FOLHA NOVA
vapor = aura.enquadrar(aura.recortar_folha(F / "fx_vapor.png"), altura=26, ancora="centro")
AURA = aura.Aura("gutto", ligada="var(20) > 0", surto="StateNo = [3000, 3999] && Time = 1", base=9600, camadas=[
    aura.Camada("crateras", crateras, plano="chao", pos=(0, -2), surto_incha=0.2,
                mov=M(deriva=(0, 0), alfa=0.9, respira=0.3, respira_periodo=40)),
    aura.Camada("garanhao", garanhao, tempo=3, plano="tras", pos=(-20, 0), mistura="soma",
                esconde="map(gutto_reacao) > 0",        # o gerador põe 1 enquanto o garanhão do coice ou da empinada toca
                mov=M(deriva=(2, 5), deriva_periodo=170, tremor=0.6, alfa=0.8, respira=0.2)),
    aura.Camada("raios", raios, plano="tras", pos=(-20, 0), mistura="soma", esconde="map(gutto_reacao) > 0",
                mov=M(deriva=(3, 2), deriva_periodo=97, tremor=1.2, alfa=0.45, respira=0.5, respira_periodo=31)),
], particulas=[
    aura.Particula("ferradura", ferradura, periodo=14, vida=90, area=(-46, -20, 46, -90), vel=(0, -0.5),
                   vel_var=(3.0, 0.6), mistura="soma", semente=1),
    aura.Particula("faisca", faisca, periodo=6, vida=26, area=(-60, 0, 60, -160), vel=(0, -0.6),
                   vel_var=(2.4, 1.6), mistura="soma", semente=3),
    aura.Particula("vapor", vapor, periodo=90, vida=40, area=(14, -98, 20, -102), vel=(0.7, -0.5),
                   vel_var=(0.2, 0.2), escala=(0.8, 1.6), alfa=0.7, surto_extra=1, semente=4),
])
```

O garanhão tem `tempo=3` (16 desenhos pedidos, 3 ticks cada; cabe no limite E1). A camada "eco" da primeira versão
era a mesma folha do garanhão um pouco maior: saiu. No lugar entra `fx_aura_garanhao_raios`, **folha própria** só
com os raios do contorno (8 desenhos, sem o corpo do cavalo), em soma e fora de fase. As duas partículas de
ferradura eram a mesma sequência deslocada: viraram uma, com 8 desenhos da ferradura virando, que sai para os dois
lados. A faísca era um desenho da ferradura reduzido: pede `fx_faisca_casco` (6 desenhos). Nenhuma partícula passa
na frente do corpo (a órbita com metade da volta à frente saiu: escondia golpe). `mistura="soma"` nunca foi testada
no motor; se falhar, volta para `"normal"`. O vapor nasce na altura das narinas (conferir na arte nova).

As camadas "garanhao" e "raios" levam `esconde="map(gutto_reacao) > 0"`: o gerador põe esse map em 1 enquanto a
reação (`fx_aura_garanhao_coice`, `fx_aura_garanhao_empina`) toca, e o garanhão em loop apaga em cerca de 8 ticks e
volta depois. Assim não aparecem dois garanhões.

**Reações fora do `aura.py`:** `fx_aura_garanhao_coice` junto com o quadro ativo de todo coice (3413, 3420, 3423,
3401, 348, 1100) e `fx_aura_garanhao_empina` na Empinada e no pouso da Queda, **só visuais, sem caixa** (regra 8.3);
relâmpagos soltos em posição sorteada a cada 8 a 20 ticks (`fx_raios`); cratera nova a cada passo, pouso ou pisão,
solta do corpo, esfriando de branco para vermelho em 40 ticks; garanhão sumindo 6 ticks ao apanhar; as ferraduras
voando para o ponto de contato no finalizador.

### 4.4 Fluidez do corpo

Atrasa em todo golpe (1 a 2 desenhos depois, balançando até parar): crina, rabo, borla da faixa de corda, corrente do
pescoço, tiras e argolas do saiote. Texto fixo para o MOTION: *"mane, tail, rope tassel, neck chain and the torn kilt
strips arrive one frame late and keep swinging"*.

- **Deslocamento:** hoje `VelSet` e depois `VelSet x = 0` seco. Rampa de 2 ticks e `VelMul x = .82` na recuperação.
  O 3402 é teleporte herdado do Rolê: fazer galope de verdade (vel 9, `PlayerPush 0`, freia depois de cruzar),
  mantendo a checagem do canto.
- **Patadas** (3431, 3433, x): ombro antecipa 3 a 5 ticks, 1 smear de garra, contato ativo + 1, 2 poses de volta.
- **Coices** (3413, 3420, 3423, 3401, 348): vira de costas e olha por cima do ombro, smear de 2, perna esticada
  ativo + 2, 3 poses de volta com o rabo completando o giro.
- **Pisões** (3411, 3432): casco sobe devagar, desce em 1 smear, corpo afunda 2 px no contato, poeira.
- **Chifradas** (3412, 3430): afunda, sobe em arco, crina atrasada, pouso em 2 poses.
- **Bufada:** inspira com o peito inchando (2 poses), cabeça para a frente, vapor residual em 3 poses.
- Entremeio por fluxo óptico segue desligado no Gutto (erro de anatomia): só desenho.

### 4.5 Folhas

Na fila (`fila_bosses.md`, 36): `e_ginga`, `e_anda`, `e_soco`, `e_chute_alto`, `e_apanha`, `e_queda`, `e_levanta`,
`e_defesa`, `e_agachado`, `e_pulo`, `e_compasso`, `e_chute_baixo`, `e_martelo`, `e_afastar`, `e_baixo_soco`,
`e_cabecada`, `e_rasteirinha`, `e_rasteira`, `e_ar_soco`, `e_bicicleta`, `e_rolamento`, `e_agarrao`, `e_bola`,
`e_armada`, `e_caneta`, `e_golaco`, `e_galope`, `e_provoca`, `e_vitoria`, `e_derrota`, `despertar_boss`,
`fx_aura_garanhao`, `fx_aura_crateras`, `fx_bufada`, `fx_ferradura`, `fx_vapor`.

Nomes do plano que mudam para bater com a fila: `e_chifrada` → `e_cabecada`; `aura_garanhao_a` → `fx_aura_garanhao`;
o 3402 usa `e_rolamento` (não `e_galope`, que na fila é a corrida).

**O kit pede e a fila não tem:**

| Pri | Folha | MOTION |
|---|---|---|
| 1 | `e_ginga_b` | frames 9-16 of the war stance loop continuing `e_ginga`: weight rocks to the other hoof, he snorts and the head tosses once, tail swishes the other way, last frame flows into frame 1 of `e_ginga` |
| 1 | `e_anda_b` | frames 9-16 of the heavy march continuing `e_anda`: the OTHER hoof leads, shoulders roll the opposite way, last frame flows into frame 1 of `e_anda` |
| 1 | `e_coice_final` | full spinning back kick finisher: 1 stance, 2-3 he turns all the way around with the tail tracing the circle, 4 looks over the shoulder, 5-6 rear hoof fully extended at chest height, 7-8 the leg drops and he squares up |
| 2 | `e_coice_final_b` | recovery of the spinning back kick: 1-3 hoof lands hard and he sinks, 4-5 turns back to face right, 6-8 rises to the stance, mane and kilt strips settling |
| 1 | `fx_aura_garanhao_b` | frames 9-16 of the lightning stallion loop continuing `fx_aura_garanhao`: front legs paw the air the other way, the mane ripples, the head throws back and returns, last frame flows into frame 1 |
| 1 | `fx_aura_garanhao_coice` | the lightning stallion kicks: 1 rearing, 2-3 it drops to the front legs and turns its haunches forward, 4-5 both hind legs kick out to the right, 6-8 it rears back up |
| 1 | `fx_aura_garanhao_nasce` | the lightning stallion is born: 1 a crackle of red lightning on the ground, 2-4 legs and chest rise out of the floor, 5-6 the neck and head form, 7-8 it rears up fully |
| 2 | `fx_aura_garanhao_empina` | the lightning stallion slams down: 1 rearing at full height, 2-3 the front hooves rise higher, 4-5 both front hooves crash down to the right, 6-8 it rears back up |
| 1 | `fx_raios` | eight separate small bolts of crimson lightning with white cores, one per cell, each a different jagged shape, no ground, no figure |
| 2 | `e_galope_b` | frames 9-16 of the gallop continuing `e_galope`: the opposite legs reach forward, mane and tail streaming, last frame flows into frame 1 of `e_galope` |
| 2 | `despertar_boss_b` | second half of the transformation: 1-2 the horns curl out and the muzzle lengthens, 3-4 iron pauldron and bracers snap on, 5-6 the chest crack lights up, 7-8 he rears with the head back, neighing |
| 2 | `despertar_boss_c` | end of the transformation: 1-3 both hooves stamp down, 4-5 he snorts and lowers the horns, 6-8 settles into the war stance |
| 2 | `e_golaco_b` | super, second half of the flurry of hooves: 1-4 four more hoof strikes alternating legs, each a clear contact pose, 5-6 he turns for the final back kick, 7-8 leg locked out |
| 2 | `e_agarrao_b` | bite throw, second half, only him drawn: 1-3 he shakes the head side to side holding the unseen opponent in his teeth, 4-5 flings it away to the right, 6-8 spits and wipes the muzzle |
| P | `e_relincho_a` | war neigh, light: 1 stance, 2-3 rears the head back filling the chest, horns up, 4-5 throws the head forward mouth wide open, mane and tail blown back, 6 holds the roar, 7-8 chest empties and he settles |
| P | `e_relincho_b` | war neigh, heavy: 1-3 long wind-up, both fists clenched low, one hoof scraping the ground twice, 4-5 rears up on the back leg and roars downward, 6 holds, 7-8 lands the hoof and exhales (pair with `fx_relincho`: red shout cone, 8 drawings that open and thin out) |
| P | `e_investida_a` | horn charge, first half: 1 stance, 2-3 scrapes a hoof and lowers the horns, 4-8 runs bent forward with the horns leading |
| P | `e_investida_b` | horn charge, second half: 1-3 still charging, 4-5 tosses the head upward at impact, 6-8 skids to a stop and straightens |
| P | `e_empinada_a` | rearing stomp, first half: 1 stance, 2-4 rears up on the hind legs, both front hooves high, 5-6 hangs at the top, 7-8 starts to fall forward |
| P | `e_empinada_b` | rearing stomp, second half: 1-2 both hooves crash down in front, body sunk low, 3-5 holds the impact, 6-8 pushes back up to the stance |
| P | `e_ferradura_arremesso` | low throw, body only: 1 stance, 2-3 crouches and winds the arm back, 4-5 skims the arm low along the ground releasing, 6-8 follows through and stands |
| P | `fx_ferradura_voa` | a red-hot horseshoe spinning flat and low to the right, eight rotation frames, sparks trailing |
| P | `e_estouro_a` | super, first part: 1 stance, 2-4 rears and roars pointing forward, 5-8 holds the point while leaning into it |
| P | `e_estouro_b` | super, second part: 1-8 he stamps in place eight times alternating hooves, driving the stampede, fists clenched |
| P | `e_estouro_c` | super, last part: 1-2 runs two steps, 3-4 turns his back, 5-6 huge double back kick with both hooves, 7-8 lands and snorts |
| P | `fx_aura_garanhao_estouro` | the lightning stallion galloping to the right at full stretch, eight frames of a gallop cycle, hooves striking sparks |

### 4.6 Ordem de ligação

1. `ferramentas/gutto_boss.py` com os dados próprios dos estados 34xx (deixar de importar os do Pengaró).
2. Folhas `e_*` novas convertidas; remedir `CORPO` e `CAIXA_DESPERTADA` na arte nova (o corpo boss é maior).
3. Aura nova no lugar de 9210/9211 e do PalFX; efeitos de acerto em vermelho (hoje são os do Pengaró).
4. 3402 como galope de verdade; rampa e freio nos avanços.
5. Reações do garanhão (coice, empinada, nascer).
6. Propostas aprovadas e o super novo.

## 5. Raiclaven, o Cientista Louco (cabelo verde)

Fontes: `docs/fichas/barbeiro.md`, `docs/fichas/barbeiro-audio.md`, `ferramentas/gerar_raiclaven.py`,
`ferramentas/folhas_raiclaven.py` (checkout `efeitos`) e a seção dele em `fila_bosses.md`. **Todos os tempos, danos e
alcances desta seção são alvo**, calibrados pelos da base; nada medido.

**Estado hoje.** Os comandos reais não são os da ficha (a ficha admite). Exclusivos do Despertar em 34xx; animação
desperta = base + 10000. O kit não tem nenhum Helper: tudo que voa é `Projectile`. A arte da forma e a aura não
existem no jogo; `retocar()` hoje **apaga** `quadros/endiabrado` e `ginga_endiabrada` e sobrescreve `despertar_a/b`
com cópia da provocação, e `gp.FLUXO` aponta a forma para os desenhos normais: isso sai antes de a arte nova entrar,
senão destrói a arte. A ficha diz "o cabelo continua preto"; o conceito aprovado é de cabelo verde.

### 5.1 Golpes do boss

P = próprio; V = versão boss de golpe da base; [F] = está na ficha; [prop] = proposta. Folhas com **falta** não estão
na fila.

**Normais e correntes**

| Golpe | Comando | Estado | Folha | Tempos | Dano | Alc. | Propriedade | |
|---|---|---|---|---|---|---|---|---|
| Chicotada (Cliente Zero dá o bote) | x | 3436 | `e_corrente_chicotada` + **falta** `mulher_chicotada` | 8/4/30 | 55 | 150 | médio, cancela | P [F] |
| Segundo Bote | x, x | 3440 | **FOLHA NOVA** `e_corrente_bote2` (a Cliente recolhe e dá o bote por baixo) | 9/5/31 | 45 | 150 | baixo | P [prop] |
| Puxão de Coleira | x, x, x | 3441 | `e_corrente_puxao` | 8/4/30 | 50 | 150 | traz o oponente 60 px | P [prop] |
| Queda de Aranha | x x4 | 3442 | `e_corrente_mangual` + **falta** `mulher_mangual` | 14/5/46 | 115 | 130 | finalizador, derruba | P [prop] |
| Mangual | y | 3410 | `e_corrente_mangual` | 16/5/44 | 95 | 110 a 170 | por cima, derruba, golpe único | P [F] |
| Bota de Aço | a | 230 (+10000) | `e_chute_baixo` | 5/3/19 | 45 | 55 | corrente a com arte boss | V |
| Escape de Vapor | b | 3420 | `e_chute_alto` | 9/4/34 | 95 | 80 | chute + jato dos 3 canos da ombreira | P [prop] |
| Calcanhar de Aço | b, b | 3421 | **falta** `e_afastar` | 8/4/30 | 70 | 82 | empurra | P [prop] |
| Voadora Rasante | b, b, b | 3422 | **falta** `e_bicicleta` | 9/5/34 | 75 | 85 | por cima | P |
| Cadeira de 3 Voltas | b x4 | 3423 | **falta** `e_compasso` + `_b` | 16/3x3/56 | 125 | 90 | 3 acertos, derruba | P |
| Rasteira de Aranha | ↓ + x | 3438 | `e_corrente_parado` + **falta** `mulher_rasteja` | 10/12/40 | 50 | 160 | baixo | P [F] |
| Pulo de Aranha | ↓ + y | 3430 | **FOLHA NOVA** `e_corrente_salto` + **falta** `mulher_sobe` | 6/8/38 | 85 | 20 a 90, até y -150 | antiaéreo | P [F] |
| Canela de Aço | ↓ + a | 430 (+10000) | **falta** `e_rasteirinha` | 5/3/18 | 35 | 60 | baixo | V |
| Rasteira de Lâmina | ↓ + b | 3435 | **falta** `e_rasteira` | 10/5/40 | 100 | 95 | baixo, derruba, deixa lascas | P |
| Pistão | → + y | 3431 | **falta** `e_pistao` | 9/3+3/36 | 50+60 | 85 | braço mecânico dispara, 2 acertos | P [prop] |
| Machadada Serrada | → + b | 3432 | `e_martelo` | 18/4/46 | 105 | 95 | por cima | P |
| Borrifo de Tanque | ← + x | 3433 | **falta** `e_borrifo` | 6/4/22 | 58 | 70 | jato verde, empurra | P [prop] |
| Sola de Recuo de Aço | ← + a | 3434 | `e_chute_baixo` | 8/3/26 | 70 | 66 | derruba leve | V |
| Tesourada no Voo | ar x | 600 (+10000) | `e_ar_soco` | 5/8/pouso | 60 | 50 | por cima | V |
| Mergulho Serra | ar y | 3439 | **falta** `e_ar_mergulho` | 7 / até pousar | 85 | 62 | cruza | P |
| Bota no Voo / Voadora de Jaleco | ar a / ar b | 610 / 611 | **falta** `e_bicicleta` | 6/6 e 9/6 | 75 / 88 | 60 a 68 | por cima | V |
| Descarga | y + b | 260 (+10000) | **falta** `e_afastar` | 12/4/40 | 90 | 60 dos dois lados | bobinas soltam arco, afasta | V [prop] |
| Corte Navalhado (kombo) | b, a, x | 348, 349 | **falta** `e_compasso`, `e_caneta` | 8/4/30 e 10/5/36 | 65, 80 | 80 / 76 | termina baixo e derruba | P |

Normais novos: 9 (mínimo 6); correntes novas: x e b. No gerador, o laço `("y", 3410), ("b", 3420)` vira
`("x", 3436/3440-3442), ("b", 3420)` e o 3410 fica golpe único.

**Especiais, agarrões, supers**

| Golpe | Comando | Estado | Folha | Tempos | Dano | Alcance | Propriedade | |
|---|---|---|---|---|---|---|---|---|
| Balão de Gel | ↓ ↓ + x | 3400 | `e_soco` + **falta** `cobaia_gel` | 18 / até estourar / 50 | 70 | tela | projétil novo; poça que atrasa por 120 ticks | P [F] |
| Pescoço de Borracha | ↓ ↓ + y | 3401 | **FOLHA NOVA** `e_pescoco` + **falta** `cobaia_pescoco` | 14/6/46 | 85 | 190 | cutucada alta, erra agachado | P [F] |
| Cabeça Virada | ↓ ↓ + a | 3402 | **FOLHA NOVA** `e_cabeca_virada` + **falta** `cobaia_avesso` | 20/6/56 | 95 | cai a 120-200 | por cima, cruza | P [F] |
| Cabelo Tentáculo | ↓ ↓ + b | 3403 | **FOLHA NOVA** `e_tentaculo` + **falta** `cobaia_tentaculo` | 16/8/50 | 55 | 180 | baixo, prende 30 ticks | P [F] |
| Vendaval do Leque | ↓ → + a / b | 1000/1001 | `e_bola` | 12/-/40 e 16/-/48 | 30 por lâmina | tela | 3 ou 5 lâminas da aura disparam em fila | V [prop] |
| Tubo de Ensaio | → ← + x / y | 1600/1601 (religar) | `e_bola` + `fx_tubo` | 14/-/44 | 75 / 90 | 110 / 190 | granada em arco, deixa poça | V [F] |
| Serra Circular | ↓ ← + a / b | 1100/1101 | **falta** `e_compasso` + `_b` | 10 / 5 acertos / 60 | 5x22 / 6x22 | 84 | empurra | V [F] |
| Arrancada a Vapor | → ↓ + x / y | 1200/1201 | **falta** `e_armada` | 10/8/44 | 90 / 110 | meia tela no forte | avanço, termina com giro | V [F] |
| Varredura de Lâmina | ↓ ← + x / y | 1300/1301 | **falta** `e_caneta` | 12/6/42 | 80 / 100 | 100 a 140 | baixo, derruba sempre | V [F] |
| Descarga Ascendente | ↓ → + x / y | 1400/1401 | `e_cabecada` + `fx_choque` | 5/8/46 | 100 / 122 | 54, até y -150 | antiaéreo, invencível 1 a 6 | V [F] |
| Pisão Sísmico | ← ↓ + a / b | 1500/1501 | **falta** `e_pisao` | 16/5/46 | 88 / 110 | 64 / 110 | baixo, derruba, levanta lascas | V [prop] |
| Fumaça Verde | → ← + a / b | 1700/1701 | `e_rolamento` + **falta** `e_pente_combo` | 10 some / 8 invisível / 14 chega | 0+60 / 3 cortes | atrás do oponente | chega virado | V [F] |
| Abraço da Cliente | ← → + y | 830 (831 vítima) | `e_corrente_puxao`, `e_agarrao` + **falta** `mulher_agarra` | 14/6/90 | 150 | 40 a 170 | agarrão à distância, não pega no ar | P [F] |
| Seringa | colado, → ou ← + y ou b | 800 | `e_agarrao` | 5/2/70 | 130 | 8 | agarrão | V |
| Cabeça no Tanque | colado, ↓ + y | 840/841 | **falta** `e_agarrao_baixo` | 5/2/60 | 120 | 8 | agarrão agachado | V [prop] |
| Corrente Giratória | ← → ↓ + a/b, 1 estoque | 3100 | `e_corrente_giro` + **falta** `mulher_mangual` | 8 + pausa / 6 acertos / 90 | 260 | 120 dos dois lados | invencível até o 1º acerto | P [F] |
| Sobrecarga | ← → ↓ + x/y, 2 estoques | 3200 | `e_golaco` + **falta** `_b` | 10 + pausa / 8 acertos / 120 | 345 | tela | raios de laboratório, o leque dispara tudo | V [F] |
| Fila de Clientes | ← → ↓ + x+y, 2 estoques | 3300 (novo) | `e_provoca` + **falta** `fila_clientes` | 20 + pausa / 6 passadas / 150 | 6x60 | tela, rente ao chão | super exclusivo | P [F] |
| Transformação | x + y, barra cheia | 2000 | `despertar_boss` + **falta** `_b`, `_c`, `_d` | ~150, invencível | 0 | empurra 80 px | | P |

Cobaias e Cliente Zero sem Helper: o corpo dela parado é `Explod` preso a ele; cada ataque é `Projectile` com
`projanim` própria saindo da posição dela. "Uma cobaia por vez" = `numprojid`.

**Plano B, se o dono tirar a Cliente Zero** (ela não aparece no conceito aprovado): x = Bote de Navalha (uma lâmina
do leque estoca), y = corrente de tesoura da ficha Surto (3410 a 3413), ↓ + x volta ao 400 com arte boss, ↓ + y =
Tesoura Cravada (3430), 830 = Seringa de perto, 3100 = Vendaval total do leque.

### 5.2 Efeitos e como cada um se mexe

- **Acerto:** `hit-spark` e `crit-hit` em prata com fagulha verde. **Corte:** rastro prata (`uppercut`).
- **Choque e gel:** `zap-hit` verde; poça de gel em loop de 8 a 3 ticks. Folhas de efeito verde vão em **fundo
  magenta** (`fx_tubo` e `fx_choque` da fila já estão assim).
- **Cobaias:** porta de fumaça verde atrás dele, 10 ticks abrindo e 10 fechando.
- **Vapor:** puff branco nos 3 canos da ombreira na antecipação de todo golpe do braço mecânico.
- **Super:** fundo escurecido, tanques borbulhando, o leque abre a 140% e todas as pontas viram para o oponente.
- **Transformação:** jaleco voando → tanques e bobinas encaixam → o leque abre lâmina por lâmina em 40 ticks, com
  tremida no fim.

### 5.3 Aura (dicionário para o `aura.py`)

```python
import aura
M = aura.Movimento
F = RAIZ / "sprites/raiclaven/quadros/folhas_arcade"
# leque: 8 desenhos do brilho correndo pelas lâminas, desenhado com 12 lâminas IGUAIS; o giro é assado (1/12 de volta
# em 48 quadros de 2 ticks = 0,31 grau por tick) e fecha sozinho por causa da simetria
leque = aura.girar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura_leque.png"), altura=236, ancora="centro"),
                        quadros=48, volta=1 / 12)
# anel de 6 foices iguais, sentido contrário: 1/6 de volta em 24 quadros de 1 tick = 2,5 graus por tick
foices = aura.girar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura_foices.png"), altura=120, ancora="centro"),
                         quadros=24, volta=1 / 6, sentido=-1)              # folha que falta
raios = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_raios_prata.png"), altura=200, ancora="centro"),
                          total=16, metodo="dissolve")                     # folha que falta
lascas = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura_lascas.png"), largura=170,
                                          ancora="centro"), total=20, metodo="mistura")
pecas = aura.recortar_folha(F / "fx_aura_pecas.png")          # falta: 4 desenhos da navalha virando, 4 da lasca
lamina = aura.enquadrar(pecas[0:4], altura=18, ancora="centro")
lasca = aura.enquadrar(pecas[4:8], altura=8, ancora="centro")
AURA = aura.Aura("raiclaven", ligada="var(20) > 0", surto="StateNo = [3000, 3999] && Time = 1", base=9600, camadas=[
    aura.Camada("lascas", lascas, plano="chao", pos=(0, -2), surto_incha=0.2, mov=M(deriva=(0, 0), alfa=1.0, respira=0)),
    aura.Camada("leque", leque, plano="tras", pos=(-2, -62), eixo=(leque[0].shape[1] // 2, leque[0].shape[0] // 2),
                surto_incha=0.15, surto_tremor=0.5, mov=M(deriva=(0, 2), alfa=0.95, respira=0.05)),
    aura.Camada("raios", raios, plano="tras", pos=(-2, -62), eixo=(raios[0].shape[1] // 2, raios[0].shape[0] // 2),
                mistura="soma", surto_alfa=0.3, mov=M(deriva=(0, 0), tremor=0.8, alfa=0.7, respira=0.6, respira_periodo=11)),
    aura.Camada("foices", foices, tempo=1, plano="tras", pos=(-2, -62),
                eixo=(foices[0].shape[1] // 2, foices[0].shape[0] // 2), mov=M(deriva=(0, 0), alfa=0.9)),
], particulas=[
    aura.Particula("lamina", lamina, periodo=24, vida=60, area=(-70, -20, 70, -150), vel=(0, -0.3),
                   vel_var=(1.0, 0.6), giro=(0, 360), semente=1),
    aura.Particula("lasca", lasca, periodo=10, vida=34, area=(-70, 0, 70, -6), vel=(0, -1.4),
                   vel_var=(0.8, 0.8), grav=(0, 0.08), giro=(0, 200), escala=(1.0, 0.6), semente=2),
])
```

O leque e o anel **não giram no motor**: giro do motor quebra a grade do pixel (o leque de 236 px virava mosaico
torto na tela de 1280). O giro é **assado** por `aura.girar_loop`, que roda o desenho na grade do jogo. Para o loop
fechar sem pedir a volta inteira, o leque tem de ser desenhado com 12 lâminas iguais (o loop cobre 1/12 de volta) e
o anel com 6 foices iguais (1/6 de volta). Os 8 desenhos da folha são o brilho correndo pelas lâminas e andam junto
com o giro. Os raios balançavam 20 graus pelo motor: agora são 8 desenhos próprios em `"dissolve"`.

Avisos: `mistura="soma"` **nunca rodou no motor**. A camada "lascas" foi para `plano="chao"` (fica no chão no pulo e
atrás do corpo): na frente ela não cabia no limite de altura e de alfa do E9. As partículas pedem 4 desenhos da
navalha e 4 da lasca (`fx_aura_pecas`). O arco entre as bobinas da cabeça (opcional) não entra: precisaria de
posição por desenho do corpo. O `girar_loop` com 48 quadros de 336 px pesa no `.sff`: medir quando a folha existir.

**Reações fora do `aura.py`:** no Vendaval as lâminas disparadas somem do leque e renascem uma a uma em 40 ticks; no
golpe forte a lâmina do lado do golpe estoca 12 px e volta; ao apanhar o leque estremece e 2 ou 3 lâminas caem; na
Fumaça Verde o leque some com ele e reabre em 12 ticks; no especial o leque gira 3x mais rápido e fecha 10% (o surto
do `aura.py` incha em vez de fechar: `surto_incha` negativo não foi testado). Tudo isso pede o leque **composto por
peças** (uma lâmina = um `Explod`), que é a decisão 23. A aura atrasando no pulo exigiria o primeiro Helper do kit.

### 5.4 Fluidez do corpo

Atrasa em todo golpe: barra rasgada do jaleco (1 a 2 desenhos atrás do quadril), mangueiras do braço, líquido dos
tanques (inclina contra o movimento e volta), hastes das bobinas, seringa e frasco do cinto. A tesoura abre na
antecipação e fecha no contato. Texto fixo para o MOTION: *"torn coat hem, arm hoses, the liquid in the tanks, coil
rods and the belt syringe arrive one frame late and keep swinging; the scissors open on the wind-up and close on
contact"*.

- **Golpes de comando** (x, y, ↓x, ↓y, cobaias): ele quase não sai do lugar; a fluidez vem do secundário e da
  corrente, desenhada por código com atraso de onda. Antecipação de 6 a 8 ticks, pose de ordem segurada, 3 poses de
  volta.
- **Golpes do corpo** (Pistão, Escape de Vapor, Machadada, Rasteira de Lâmina, Pisão): puff de vapor na
  antecipação, 1 ou 2 smears, contato ativo + 2, 3 poses de volta. Deslocamento em rampa (Pistão 0 → 4 → 2 → 0;
  Arrancada 0 → 7 → 5 → 2 → 0 com atrito 0,85), nunca `PosAdd`.
- **Cadeira de 3 Voltas e Serra Circular:** volta de 4 desenhos repetida fica dura; pedem folha `_b`.
- **Fumaça Verde:** único salto de posição; some em 10 ticks, 8 invisível, o jaleco chega depois.
- Sem fluxo óptico; braço direito sempre de aço com tesoura de 2 lâminas, luva preta na esquerda.

### 5.5 Folhas

Na fila (`fila_bosses.md`, 32): `e_ginga`, `e_anda`, `e_soco`, `e_chute_baixo`, `e_apanha`, `e_queda`, `e_levanta`,
`e_defesa`, `e_agachado`, `e_pulo`, `e_bola`, `e_martelo`, `e_cabecada`, `e_agarrao`, `e_rolamento`, `e_golaco`,
`e_corrente_parado`, `e_corrente_chicotada`, `e_corrente_mangual`, `e_corrente_puxao`, `e_corrente_giro`,
`e_chute_alto`, `e_baixo_soco`, `e_ar_soco`, `e_provoca`, `e_vitoria`, `e_derrota`, `despertar_boss`,
`fx_aura_leque`, `fx_aura_lascas`, `fx_tubo`, `fx_choque`. A própria fila avisa que as criaturas (`mulher_*`,
`cobaia_*`) e a `fila_clientes` ficaram de fora, esperando a decisão sobre a Cliente Zero.

**O kit pede e a fila não tem:**

| Pri | Folha | MOTION |
|---|---|---|
| 1 | `e_ginga_b` | frames 9-16 of the boss idle continuing `e_ginga`: he snips the scissors twice, the tank liquid sloshes the other way, the coat hem sways back, last frame flows into frame 1 of `e_ginga` |
| 1 | `e_anda_b` | frames 9-16 of the slow menacing walk continuing `e_anda`: the OTHER boot leads, hoses swing the opposite way, last frame flows into frame 1 of `e_anda` |
| 1 | `fx_aura_foices` | AURA, inner ring, seen from the front, centred, no figure: a circle of eight small steel sickle blades pointing clockwise, white-silver glints running around the ring from frame to frame |
| 1 | `fx_raios_prata` | AURA, eight different white-silver lightning webs, one per cell, each a thin jagged arc jumping between points on a wide circle, no blades, no figure |
| 1 | `fx_aura_pecas` | AURA parts, one object per cell, each centred and upright: 1 open scissors, 2 closed scissors, 3 straight razor, 4 steel comb, 5 a single blade shard, 6 a small sickle, 7 a floor shard cluster, 8 a spark |
| 1 | `e_afastar` | discharge shove: 1 stance, 2-3 both arms cross over the chest and the head coils light up, 4-5 arms thrown wide with the chest out, 6-8 arms lower in three steps, coat settling |
| 1 | `e_bicicleta` | flying side kick with the steel boot, all frames in the air: 1 tucked, 2-3 the leg chambers, 4-5 boot locked out, coat streaming, 6-8 legs fold for landing |
| 1 | `e_compasso` | barber-chair spin, first half: 1 stance, 2 he drops as if seated with the legs out, 3-8 spins one and a half turns, legs sweeping at waist height, coat flaring |
| 2 | `e_compasso_b` | barber-chair spin, second half: 1-5 one and a half more turns slowing down, 6 plants a boot, 7-8 stands with the coat wrapping around him and unwinding |
| 1 | `e_rasteira` | low blade sweep: 1 crouch, 2-3 the mechanical arm reaches back, 4-5 the scissors scrape a wide low arc along the floor, sparks, 6-8 arm returns and he rises |
| 1 | `e_rasteirinha` | quick steel-toe jab from the crouch: 1 crouch, 2 the boot chambers, 3-4 short low kick, 5-6 boot returns, 7-8 settles |
| 1 | `e_pistao` | piston punch: 1 stance, 2-3 the mechanical arm cocks back and vents steam, 4 the forearm shoots out (first contact), 5 the scissors snap shut at full reach (second contact), 6-8 the arm retracts in three steps |
| 1 | `e_borrifo` | tank spray while backing off, body only: 1 stance, 2 grabs the hose nozzle, 3-5 sprays forward leaning back, 6-8 hops back and re-hooks the hose |
| 1 | `e_ar_mergulho` | mid-air diving scissors stab, all frames in the air: 1 tucked, 2-3 turns head-down diagonal, 4-6 dives with the scissors leading, coat trailing, 7-8 landing crouch |
| 1 | `e_caneta` | sliding blade sweep along the floor: 1 stance, 2-3 drops low, 4-6 slides forward with the scissors skimming the ground, 7-8 pushes up to standing |
| 1 | `e_armada` | steam dash ending in a spin: 1 stance, 2 leans in venting steam behind, 3-5 lunges with the scissors forward, 6-7 spins once with the coat open, 8 stops facing right |
| 1 | `e_pisao` | seismic stomp: 1 stance, 2-4 raises the steel boot high and slowly, 5 slams it down, body sinking, 6-8 rises in three steps |
| 2 | `e_pente_combo` | arriving cuts after the vanish: 1 half-formed in smoke, 2-3 first horizontal cut, 4-5 backhand cut, 6 rising cut, 7-8 flicks the scissors clean and stands |
| 2 | `e_agarrao_baixo` | crouching grab of an unseen opponent, only him drawn: 1 crouch, 2-3 seizes low with the gloved hand, 4-6 pushes the unseen head down toward his back tank, 7-8 shoves it away |
| 2 | `e_golaco_b` | super, second half: 1-2 both arms raised, coils blazing, 3-6 he brings the arms down four times like a conductor, 7-8 arms drop and he laughs, shoulders shaking |
| 2 | `despertar_boss_b` | transformation, second part: 1-3 the barber coat flies off behind him, 4-6 the tanks swing onto his back and lock, 7-8 hoses snap into the arm |
| 2 | `despertar_boss_c` | transformation, third part: 1-3 the coils rise from the headset and spark, 4-5 the hair turns green from root to tip, 6-8 the mechanical arm unfolds and the scissors open |
| 2 | `despertar_boss_d` | transformation, last part: 1-4 he spreads both arms slowly, 5-6 throws the head back laughing, 7-8 settles into the boss idle |
| P | `mulher_parada` | Client Zero idle loop on a chain leash (see the content doubt, decision 21): crouched low on all fours, head down, swaying |
| P | `mulher_chicotada` | Client Zero lunges forward low and snaps back: 1 crouched, 2-3 springs, 4-5 fully stretched, 6-8 hauled back |
| P | `mulher_mangual` | Client Zero swung in a high arc on the chain and brought down: eight frames around the arc |
| P | `mulher_rasteja` | Client Zero crawling fast along the floor to the right, eight-frame crawl loop |
| P | `mulher_sobe` | Client Zero leaping straight up and dropping back: 1 crouch, 2-4 rising, 5 top, 6-8 falling |
| P | `mulher_agarra` | Client Zero clamps onto an unseen opponent and is hauled back with it: eight frames |
| P | `cobaia_gel` | test subject as a rolling ball of green gel: 1-5 rolls to the right, 6-8 bursts into a puddle (magenta background) |
| P | `cobaia_pescoco` | test subject whose neck stretches far to the right and snaps back: eight frames |
| P | `cobaia_avesso` | test subject that jumps in an arc and lands head-first: eight frames |
| P | `cobaia_tentaculo` | test subject whose hair shoots along the floor as a tentacle, wraps and retracts: eight frames |
| P | `fila_clientes` | a line of six different caped barber-shop clients running to the right in single file, eight-frame run loop |
| 2 | `fx_porta_fumaca` | a doorway of green smoke: 1-4 opens from a slit to a tall oval, 5-8 closes (magenta background) |

### 5.6 Ordem de ligação

1. Tirar de `retocar()` o que apaga `quadros/endiabrado` e sobrescreve `despertar_a/b`, e soltar `gp.FLUXO` da
   forma desperta.
2. Corrigir os comandos da base para os da ficha, ou a ficha para os do jogo (decisão 22), antes de mexer nos do boss.
3. Converter as 12 do grupo 1 e ligar ginga, andar, reações e defesa.
4. Aura: primeiro `leque` e `lascas` (folhas da fila), com `giro` testado num filme; depois `foices`, `raios`, peças.
5. `raiclaven_boss.py` com os golpes do corpo (os que não dependem da Cliente Zero): 3420 a 3423, 3431 a 3435, 3439.
6. Cliente Zero e cobaias, ou o Plano B, depois da decisão 20.
7. `movelist.dat` próprio (hoje é `replace` sobre o do Gutto).

## 6. Hazak, o Diabo Loiro

Fontes: `docs/fichas/hazaki.md`, `docs/arcade/hazak_gerador.md`, `docs/arcade/fila_hazak.md`,
`ferramentas/hazaki_golpes.py` (branch `hazak`) e a seção dele em `fila_bosses.md`. Tempos = projeto (soma da
notação `"folha d/tA"`), não medição.

**Estado hoje.** O gerador novo do Hazak tem a ficha inteira **menos o Despertar**: `var(20)` e `var(37)` estão
reservadas e sempre em 0. Na branch `bosses` existem `d_parado`, `d_anda`, `d_sapato_canela`, `d_levanta` (arte
bruta) e, sem commit, `d_agachado` e `d_defesa`. O conceito aprovado tem **sobretudo roxo nos ombros com forro
laranja-brasa, rabo de diabo com ponta de seta, chifres longos que atravessam a aba do chapéu**, corrente de ouro no
colete, polaina branca, bico dourado no sapato, maleta na mão de trás e pulseira teal no pulso de trás. Sobretudo e
rabo são corpo; asas, coroa e brasa são aura. O prompt `d_` da `fila_hazak.md` (branch `hazak`) está desatualizado
frente ao conceito; o da `fila_bosses.md` é o que vale.

Para não colidir com quem edita `gerar_hazaki.py`: os dados vão em `ferramentas/hazaki_diabo.py` (mesma dataclass
`Golpe`; listas `CORRENTES_D`, `NORMAIS_D`, `ANIM_D`, `AURA`), que o gerador importa depois.

Ritmo do Diabo (`hazak_gerador.md` §8): preparo fraco 5, forte 9, finalizador 12 a 14; pausetime 8 / 12 / 14, super 16.

### 6.1 Golpes do boss

P = próprio; B = versão boss de golpe da base; PROP = proposta.

**Correntes novas (P)**

Cada golpe tem o seu ritmo (C10): a primeira versão dava a mesma notação aos seis. Na corrente y a maleta abre
carregada (11 de início), volta no embalo (7) e fecha por cima, lenta e seca (16); na corrente b o sapato entra
rápido na canela (7), empurra segurando na barriga (10) e o coice de costas gira antes de sair (15). Números alvo.

| Nº | Nome | Comando | Folha (fila) | Notação sugerida | Tempos | Dano | Alc. | Propriedade |
|---|---|---|---|---|---|---|---|---|
| 3410 | Maletada de lado | y | `d_maletada_lado` | 1/4 2/5 3/2 4/3A 5/4 6/6 7/6 | 11/3/30 | 45 | 70 | forte, empurra -6 |
| 3411 | Maletada de volta | y, y | `d_maletada_volta` | 1/2 2/3 3/2 4/4A 5/6 6/5 7/4 | 7/4/26 | 50 | 68 | forte, -6 |
| 3412 | Maletada de cima | y, y, y | `d_maletada_cima` | 1/5 2/6 3/3 4/2 5/4A 6/7 7/7 | 16/4/34 | 55 | 60 | forte |
| 3413 | Negócio Fechado | y x4 (3 acertos) | `d_negocio_fechado` + **falta** `_b` | 1/4 2/5 3/4 4/5A 5/6 6/8 7/6 | 13/5/38 | 90 | 62 | final, derruba, tremida, cancela em especial e super |
| 3420 | Sapato na canela | b | `d_sapato_canela` | 1/2 2/3 3/2 4/3A 5/4 6/5 7/4 | 7/3/23 | 40 | 66 | forte, -6 |
| 3421 | Sapato na barriga | b, b | `d_sapato_barriga` | 1/3 2/5 3/2 4/5A 5/6 6/5 7/4 | 10/5/30 | 50 | 68 | forte, -7 |
| 3422 | Coice de costas | b, b, b | `d_coice_costas` | 1/4 2/4 3/5 4/2 5/4A 6/8 7/6 | 15/4/33 | 60 | 64 | forte |
| 3423 | Pisão de Chefe | b x4 (3 acertos) | `d_pisao_chefe` + **falta** `_b` | 1/4 2/5 3/4 4/5A 5/6 6/9 7/7 | 13/5/40 | 95 | 58 | final, derruba, tremida; arruma a gravata no fim |

**Normais novos (P)**

| Nº | Nome | Comando | Folha (fila) | Tempos | Dano | Alc. | Propriedade |
|---|---|---|---|---|---|---|---|
| 3431 | Tapa com anel | x | `d_tapa_anel` | 5/3/19 | 30 | 58 | fraco |
| 3430 | Maleta subindo | ↓ + y | `d_maleta_sobe` | 9/5/31 | 65 | 40 (topo -118) | antiaéreo, lança -2, -7 |
| 3432 | Chapelada | → + b | `d_chapelada` | 12/4/31 | 60 | 56 | por cima |
| 3433 | Dedo balançando | ← + x | `d_dedo` | 4/16/30 | 0 | 46 | anula projétil fraco |
| 3434 | Bico de sapato | ↓ + a | `d_bico_sapato` | 5/3/19 | 30 | 62 | baixo |
| 3435 | Pisão descendo | b no ar | `d_pisao_ar` | 9/8/pouso | 55 | 40 | por cima |
| 348 / 349 | Sociedade Fechada (kombo) | x, → + b, y | `d_chapelada` / `d_maletada_lado` | 10/4/29 e 9/4/29 | 60 / 70 | 56 / 70 | 348 por cima; 349 derruba |

**Especiais exclusivos e super (P)**

| Nº | Nome | Comando (como o gerador resolveu) | Folha | Tempos | Dano | Alcance | Propriedade |
|---|---|---|---|---|---|---|---|
| 3400/3401 | Chapéu Bumerangue | ↓ → + a / b | `d_chapeu_arremesso` + **falta** `_b` | solta no 14 / total 34 + espera sem chapéu | 50 / 60 | vai ~82 / ~128 px e volta | projétil novo |
| 3402/3403 | Maleta Giratória | → ← + a / b | `d_maleta_giro` + **falta** `_b` | 10 / 3 batidas / 44 e 12 / 4 batidas / 52 | 3x25 / 4x25 | anda ~90 / ~150 px | avanço; b derruba na última |
| 3404/3405 | Nota Falsa | ↓ ← + x / y (ficha: ↓ ↑) | `d_nota_falsa` | maço no 16 / total 34 | 70 / 80 | maço a 40 / 90 px, 120 ticks | armadilha |
| 3406/3407 → 3408 | Suborno | ↓ ← + a / b (ficha: ↓ ↑) | `d_suborno` + **falta** `_b` e vítima | 8 / pega 6 / erro 38 | 110 | 30 / 45 px | agarrão de comando |
| 3100 | Chuva de Dinheiro | ← → ↓ + x / y, desperto (ficha: + x + y) | `d_chuva_abre`, `d_estatueta_gigante` + **faltam** os dois `_b` | superpausa 30 + ~150 | 300 | tela | 1000 de barra |
| 2000 | Despertar | x + y, barra cheia | `despertar_virada` + **faltam** `_b`, `_c` | ~150, invencível | 0 | empurra -8 no tick 100 | transformação |

**Versão boss de golpes da base (B):** 11000/11001 Punho de Concreto com anel (`d_punho_anel`, lasca em brasa);
11600/11601 Estatueta desperta (`d_estatueta`, vira obstáculo 90 ticks); 11500/11501 Pega Bolado de sapato
(`d_corrida` + `d_voadora_sapato`, mais lento, quica); 11700/11701 Rolada que some na brasa (`d_fumaca`); normais
10230, 10400, 10440, 10600, 10601, 10610 (`d_chute_baixo`, `d_baixo_soco`, `d_rasteira_arco`, `d_ar_soco`,
`d_ar_cotovelo`, `d_ar_joelho`); 10216 e 10231 (`d_cotovelo_faixa`, `d_coice`); recuo, afastar, rolamento, parry; os
três agarrões (`d_agarrao_abraco`, `d_agarrao_cutucao`, `d_agarrao_perna`). Saem no boss: Giro de Garagem, Corte de
Base, Guarda de Aço, Ascensão, Rapidinho.

**Propostas (PROP), para usar o que só o conceito tem: sobretudo e rabo** (asas e coroa não podem ter caixa, regra
8.3):

| Nº | Nome | Comando | Folha nova | Tempos | Dano | Alc. | O que é |
|---|---|---|---|---|---|---|---|
| 3436 | Aba do Sobretudo | → + y (no lugar do 10216) | `d_sobretudo_aba` | 9/5/32 | 55 | 78 (o normal mais longo) | puxa a lapela e chicoteia a aba na horizontal; o forro laranja aparece |
| 3437 | Rabada | ← + a (no lugar do 10231) | `d_rabada` | 9/4/28 | 45 | 60 | meio giro, o rabo varre rente ao chão; baixo, não derruba |
| 3440/3441 | Sobretudo que Sobe | → ↓ + x / y | `d_sobretudo_sobe` + `_b` | 6/5/34 e 7/8/44 | 85 / 115 | 38, topo -124 | antiaéreo girando com o sobretudo como capa; as asas batem para cima junto |
| 3150 | Dívida Paga (super 2) | ← → ↓ + a / b, 2000 de barra | `d_divida_abre` + `d_divida_fecha` | superpausa 30 + ~170 | 360 | meia tela | as asas fecham para a frente, ele desliza, engole o oponente na maleta, a coroa derrete e cai, maletada final |

Com as propostas: 2 correntes + 8 normais + 5 especiais + 2 supers próprios. Sem elas, o kit da ficha já cumpre o
mínimo da regra 4.

### 6.2 Efeitos e como cada um se mexe

Todos `Explod` com `ownpal = 1`, folha própria em fundo verde, de 2 em 2 ticks ou mais devagar. Números livres pelo
grep em `gerar_hazaki.py` (não lido inteiro): 9220 a 9239 para efeitos, 3450 a 3453 e 11005/11006/11605 a 11607 para
projéteis.

| Efeito | Uso | Movimento |
|---|---|---|
| Nota em chamas estourando | acerto fraco | 6 desenhos: a nota dobra, rasga em 3 pedaços que voam em leque |
| Maço estourando em brasa | acerto forte (maletadas, sapato) | 8 desenhos: clarão quadrado, notas em anel, cinza subindo |
| Explosão de ouro derretido | finalizador, golpe final de super | 10 desenhos: respingo radial, gotas caem com gravidade |
| Rastro de brasa da maleta | preso à mão no ativo dos fortes | arco de 5 desenhos que segue o desenho de contato |
| Fumaça de brasa (`fx_fumaca_brasa`) | Rolada, rolamento, fim do Despertar | 8 desenhos implodindo + 8 explodindo |
| Chuva de notas (`fx_notas`) | Chuva de Dinheiro, transformação | 3 camadas com queda a 1,2 / 1,8 / 2,6 px por tick e deriva lateral diferente (paralaxe); a nota gira em 12 desenhos |
| Pilar e onda de brasa | transformação; onda no Pisão de Chefe e na maletada de cima | sobe em 8 desenhos e pulsa; a onda corre 40 px |
| Chapéu em voo e na volta | Chapéu Bumerangue | gira em 8 desenhos a 2 ticks, inclina na volta |
| Maço parado e estouro | Nota Falsa | o maço "respira" com um brilho passando |
| Lasca em brasa; estatueta em voo, pousada, quebrando | 11000, 11600 | a estatueta pousada solta fagulha e treme antes de sumir |

**Transformação (2000), em ordem:** bate o pé → a brasa acende no chão → patroa → pilar de brasa → o sobretudo cai
nos ombros e o rabo desenrola (corpo) → as asas brotam fechadas e abrem → a coroa desce de cima e assenta flutuando →
empurrão com onda de notas. Só então a aura liga.

### 6.3 Aura (dicionário para o `aura.py`)

No conceito as asas abertas têm perto de 290 px no jogo, quase a tela inteira. O dicionário usa o repouso reduzido
(cerca de 180 px de largura) e deixa a abertura total para a transformação, o super e a vitória (decisão 32).

```python
import aura
M = aura.Movimento
F = RAIZ / "sprites/hazaki/quadros/folhas_arcade"
# As asas, a coroa e a brasa saem do Blender já em laço (docs/arcade/aura_blender.md): quando a pasta de camadas
# existir, cada linha abaixo vira `aura.ler_quadros(PASTA / "asas")` etc. e o resto do dicionário não muda.
asas = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura_asas.png"), largura=184), total=32)
coroa = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura_coroa.png"), largura=40,
                                         ancora="centro"), total=20)
brasa = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura_brasa.png"), largura=170,
                                         ancora="centro"), total=24)
borda = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura_brasa_borda.png"), altura=12),
                          total=24)                                        # FOLHA NOVA: línguas baixas da borda da frente
nota = aura.enquadrar(aura.recortar_folha(F / "fx_notas.png"), altura=12, ancora="centro")          # 8 desenhos
gota = aura.enquadrar(aura.recortar_folha(F / "fx_gota_ouro.png"), altura=8, ancora="centro")       # folha que falta
fagulha = aura.pedra_procedural(3, cores=((255, 150, 40), (255, 230, 150)), contorno=(200, 70, 20))
AURA = aura.Aura("hazak", ligada="var(20) > 0", surto="StateNo = [3000, 3999] && Time = 1", base=9600, camadas=[
    aura.Camada("brasa", brasa, tempo=3, plano="chao", pos=(0, -2), surto_incha=0.2,
                mov=M(deriva=(3, 0), deriva_periodo=110, alfa=0.9, respira=0.25, respira_periodo=29)),
    aura.Camada("asas", asas, plano="tras", pos=(-6, -30), surto_incha=0.15, esconde="map(hazak_reacao) > 0",
                mov=M(deriva=(2, 4), deriva_periodo=128, alfa=0.92, respira=0.1)),
    aura.Camada("coroa", coroa, plano="tras", pos=(2, -128), surto_incha=0.1, surto_tremor=0.5,
                mov=M(deriva=(1, 2), deriva_periodo=90, alfa=1.0, respira=0.05)),
    aura.Camada("borda", borda, tempo=3, plano="frente", pos=(0, 3), surto_incha=0.0, surto_alfa=0.05,
                mov=M(deriva=(4, 0), alfa=0.45, respira=0.3)),
], particulas=[
    aura.Particula("nota", nota, periodo=20, vida=40, area=(-50, -10, 50, -110), vel=(-0.4, -1.2),
                   vel_var=(0.8, 0.6), grav=(0, 0.01), giro=(0, 200), semente=1),
    aura.Particula("fagulha", fagulha, periodo=6, vida=30, area=(-80, 0, 80, -8), vel=(0, -1.6),
                   vel_var=(1.0, 0.8), giro=(0, 180), escala=(1.0, 0.5), mistura="soma", semente=2),
    aura.Particula("gota", gota, periodo=26, vida=36, area=(-86, -70, 86, -120), vel=(0, 0.4), vel_var=(0.2, 0.2),
                   grav=(0, 0.25), escala=(1.0, 1.4), sai=0.2, semente=3),
    aura.Particula("pingo", gota, periodo=50, vida=30, area=(-6, -124, 10, -126), vel=(0, 0.3), grav=(0, 0.2),
                   sai=0.2, surto_extra=1, semente=4),
])
```

A coroa é camada `"tras"` com posição acima do chapéu: fica atrás do corpo por plano, mas acima da cabeça não há
corpo para cobrir. Se os chifres passarem na frente dela e ficar errado, a coroa precisa de `prioridade` própria. A
camada `brasa` em `"chao"` fica no chão no pulo. A "brasa_frente" da primeira versão era a brasa espelhada e
achatada por cima dos pés: saiu, e a borda da frente pede **folha própria** baixa (`fx_aura_brasa_borda`, 12 px). A
fagulha é farelo de 3 px por código, com giro e escala assados. A gota que estala ao tocar o chão não existe na
`Particula` (ela some por tempo, não por altura). A camada "asas" leva `esconde="map(hazak_reacao) > 0"`: o gerador
liga o map enquanto `fx_asas_bate`, `fx_asas_fecha` ou `fx_asas_abre` toca.

**Dois avisos do gerador do Hazak** (`gerar_hazaki.py`, branch `hazak`): ele não tem a classe `Sprites`, tem
`escrever_sff(destino, s, manter)` com os índices 1 a 15 da paleta presos ao corpo; `manter |= AURA.registrar(s)`
resolve (rodado no host com a aura de teste: cores exatas). E hoje o `var(20)` dele é sempre 0 (o Despertar não
entrou): a condição `ligada` só passa a valer quando o estado do Despertar existir.

**Reações fora do `aura.py`:**

- **Batida de asa** (`fx_asas_bate`): no 1º tick ativo dos finalizadores 3413 e 3423, do Sobretudo que Sobe (para
  cima) e do Pega Bolado (varre para trás).
- **Asas fechadas na frente, como escudo** (`fx_asas_fecha`): na guarda, no parry e na abertura do super 2; a faixa
  de brasa encolhe junto.
- **Asas abertas ao máximo** (`fx_asas_abre`, abre e segura tremendo): superpausa, tick 80 a 150 do 2000, vitória.
- **Coroa:** inclina e espirra 3 gotas em todo acerto forte; no 3100 sobe e derrama (vira a fonte da chuva).
- **Brasa:** onda no Pisão de Chefe; apaga 12 ticks ao tomar golpe e reacende; pegadas de brasa ao correr.
- As três reações de asa pedem esconder a camada "asas" enquanto tocam (decisão 6).

### 6.4 Fluidez do corpo

A fluidez vem de: antecipação em 2 poses; **recuperação em 3 poses que desaceleram** (5, 6, 5 ticks); secundário
desenhado 1 pose atrás: aba do sobretudo, juba, rabo (sempre para o lado oposto do golpe, de contrapeso), gravata,
corrente do colete, e a **maleta como pêndulo** (o braço chega, a maleta chega 1 pose depois); deslocamento por
`VelSet`/`VelMul`. Texto fixo para o MOTION: *"the overcoat hem, the mane, the devil tail (always swinging opposite
to the strike), the tie and the briefcase arrive one frame late and keep swinging"*.

Curva de velocidade padrão, no lugar do `avanco` fixo: entra em 3 ticks (0,4v, 0,8v, v), segura até o fim do ativo,
depois `VelMul x = 0.75` por tick.

- **Maletadas:** maleta atrás do quadril, quadril gira; maleta passa do alvo, puxa o ombro e volta. Passo de 3 px.
- **Negócio Fechado e Pisão de Chefe:** dois gestos cada (abrir e fechar; pisão e gravata): pedem `_b`.
- **Chapelada:** antecipação longa (tira o chapéu e ergue), que avisa o golpe por cima; a juba solta sem o chapéu.
- **Chapéu Bumerangue:** fica sem chapéu esperando, pega e recoloca: pede `_b`.
- **Maleta Giratória:** duas voltas = 16 desenhos; o sobretudo vira disco e o rabo enrola. Curva com v 3,5 / 5.
- **Rolada:** não teleporta em 1 tick: 6 ticks invisível com um rastro de brasa viajando a cerca de 12 px por tick
  até atrás do oponente; o sobretudo é o último a sumir e o primeiro a aparecer.
- **Parado, andar, correr, agarrões, super, Despertar:** abaixo do mínimo da 7.1 com 8 desenhos; pedem `_b`.

### 6.5 Folhas

Na fila (`fila_bosses.md`, 55): `d_parado`, `d_anda`, `d_tapa_anel`, `d_sapato_canela`, `d_apanha`, `d_queda`,
`d_levanta`, `d_defesa`, `d_agachado`, `d_pulo`, `d_maleta_giro`, `despertar_virada`, `d_vira`, `d_corrida`,
`d_defesa_baixa`, `d_vitoria`, `d_maletada_lado`, `d_maletada_volta`, `d_maletada_cima`, `d_negocio_fechado`,
`d_sapato_barriga`, `d_coice_costas`, `d_pisao_chefe`, `d_maleta_sobe`, `d_chapelada`, `d_dedo`, `d_pisao_ar`,
`d_bico_sapato`, `d_chapeu_arremesso`, `d_nota_falsa`, `d_suborno`, `d_estatueta`, `d_voadora_sapato`,
`d_punho_anel`, `d_fumaca`, `d_chuva_abre`, `d_estatueta_gigante`, `d_recuo`, `d_agarrao_abraco`,
`d_agarrao_perna`, `d_agarrao_cutucao`, `d_chute_baixo`, `d_chute_lateral`, `d_baixo_soco`, `d_rasteira_arco`,
`d_ar_soco`, `d_ar_cotovelo`, `d_ar_joelho`, `d_cotovelo_faixa`, `d_coice`, `fx_aura_asas`, `fx_aura_coroa`,
`fx_aura_brasa`, `fx_notas`, `fx_fumaca_brasa`.

Nomes do plano que mudam para bater com a fila: `fx_asas_a` → `fx_aura_asas`; `fx_coroa` → `fx_aura_coroa`;
`fx_brasa_chao` → `fx_aura_brasa`; `fx_nota_solta` → recorte de `fx_notas`. A fila avisa que não há `d_derrota` nem
`d_intro`; o kit não as usa, mas o boss fica sem derrota e entrada próprias.

**O kit pede e a fila não tem:**

| Pri | Folha | MOTION |
|---|---|---|
| 1 | `d_parado_b` | frames 9-16 of the standing guard continuing `d_parado`: he shifts the briefcase grip, the tail flicks to the other side, the overcoat hem sways back, last frame flows into frame 1 of `d_parado` |
| 1 | `d_anda_b` | frames 9-16 of the swaggering walk continuing `d_anda`: the OTHER dress shoe leads, the briefcase swings the opposite way, last frame flows into frame 1 of `d_anda` |
| 1 | `fx_aura_asas_b` | frames 9-16 of the wing loop continuing `fx_aura_asas`: the wings close a little and reopen like a breath, the burning banknotes flicker, wing tips trail one frame behind, last frame flows into frame 1 |
| 1 | `fx_asas_bate` | the pair of burning banknote wings beats once: 1 open, 2-3 they sweep forward and down hard, 4 fully forward, 5-8 they return to open, loose notes torn off and drifting |
| 1 | `fx_asas_abre` | the wings open to full span: 1 folded tight, 2-5 they unfurl wider and wider, 6-8 held at maximum span, trembling, flames higher |
| 2 | `fx_asas_fecha` | the wings fold forward like a shield: 1 open, 2-4 they swing around to the front and overlap, 5-8 held closed, flames low |
| 1 | `fx_gota_ouro` | a single drop of molten gold falling: 1-3 the drop stretches as it falls, 4 hits the ground, 5-8 a small splash that cools and fades |
| 2 | `d_corrida_b` | frames 9-16 of the heavy run continuing `d_corrida`: the opposite leg drives, one hand on the hat, overcoat streaming, last frame flows into frame 1 of `d_corrida` |
| 2 | `d_negocio_fechado_b` | second gesture of the finisher: 1-2 he snaps the briefcase shut on the unseen opponent, 3-4 locks the clasp with a thumb, 5-6 shakes it once, 7-8 swings it back to his side |
| 2 | `d_pisao_chefe_b` | after the boss stomp: 1-2 the sole grinds down, 3-4 he steps off, 5-6 straightens his tie with two fingers, 7-8 returns to the guard |
| 2 | `d_chapeu_arremesso_b` | waiting for the hat, bare-headed with the horns showing: 1-4 he stands with the hand out, mane loose, 5-6 catches the returning hat, 7-8 sets it back on his head |
| 2 | `d_maleta_giro_b` | second turn of the spinning briefcase: 1-5 one more full spin with the briefcase at arm's length, overcoat flat like a disc, 6 he brakes, 7-8 staggers half a step and recovers |
| 2 | `d_suborno_b` | bribe grab, second half, only him drawn: 1-2 he yanks the offered cash away, 3-5 smashes the briefcase across the unseen opponent, 6-8 dusts his hand on the lapel |
| 2 | `d_suborno_vitima` | the victim of the bribe grab, generic fighter silhouette, eight frames matched to `d_suborno`: reaches for the cash, freezes, is struck sideways |
| 2 | `d_chuva_abre_b` | super opening, second half: 1-3 he holds the open briefcase up to the sky, 4-6 banknotes pour upward out of it, 7-8 he snaps it shut and lowers it |
| 2 | `d_estatueta_gigante_b` | super ending, second half: 1-3 he watches the giant statuette fall, hand on the hat, 4-5 turns his back to the impact, 6-8 adjusts the hat and looks over his shoulder |
| 2 | `despertar_virada_b` | transformation, second part: 1-3 the purple overcoat drops onto his shoulders, 4-6 the devil tail uncoils behind him, 7-8 the horns push up through the hat brim |
| 2 | `despertar_virada_c` | transformation, last part: 1-3 he picks up the briefcase, 4-5 snaps the lapels, 6-8 lowers the hat brim and settles into the guard |
| 2 | `d_agarrao_abraco_b` | bear hug throw, second half, only him drawn: 1-3 he lifts the unseen opponent, 4-5 tosses it over his shoulder, 6-8 brushes off the overcoat |
| 2 | `d_agarrao_cutucao_b` | headlock, second half, only him drawn: 1-4 three more jabs to the ribs, 5-6 shoves the unseen opponent away, 7-8 fixes his cuff |
| 2 | `d_agarrao_perna_b` | leg grab, second half, only him drawn: 1-3 he hauls the unseen leg up, 4-5 dumps it backward, 6-8 stands and steps over |
| P | `d_sobretudo_aba` | overcoat whip: 1 guard, 2-3 he grabs the lapel and pulls it back, 4 smear, 5-6 the overcoat hem lashes out horizontally showing the ember-orange lining, 7-8 the hem falls in two steps |
| P | `d_rabada` | tail sweep: 1 guard, 2-3 half turn winding the tail, 4-5 the devil tail sweeps low along the floor in front of him, 6-8 the tail coils back and he faces right |
| P | `d_sobretudo_sobe` | rising overcoat anti-air, first half: 1 crouch turning, 2-4 he spins upward on the toes with the overcoat opening like a cape, 5-6 arm and coat at the top, 7-8 starts to come down |
| P | `d_sobretudo_sobe_b` | rising overcoat, second half: 1-4 he comes down spinning slower, 5-6 heels land, 7-8 the overcoat settles on the shoulders last |
| P | `d_divida_abre` | super 2, first half: 1 guard, 2-3 he opens the briefcase toward the right, 4-8 slides forward leaning in with the open briefcase held out |
| P | `d_divida_fecha` | super 2, second half: 1-2 he slams the briefcase shut, 3-5 holds it down with a foot on it, 6-8 a final overhead briefcase smash and he tips the hat |

Efeitos de acerto do Hazak (nota estourando, maço estourando, explosão de ouro, rastro e onda de brasa) também não
têm folha na fila; ficam para depois da decisão 5 (folha própria ou pixelfx recolorido).

### 6.6 Ordem de ligação

1. Reescrever o prompt `d_` da `fila_hazak.md` pelo conceito (ou apontar para a `fila_bosses.md`) e fechar a decisão
   29 (chifres e chapéu) antes de gerar `d_chapelada` e `d_chapeu_arremesso`.
2. `hazaki_diabo.py`: correntes 3410 a 3423 e normais 343x; estado 2000 e contagem do `var(20)`.
3. Aura com as três folhas da fila (`fx_aura_asas`, `fx_aura_coroa`, `fx_aura_brasa`) e `fx_notas`.
4. Especiais exclusivos 3400 a 3408, depois as versões +10000 (sem PalFX de quebra-galho).
5. Super 3100 e as reações de asa.
6. Propostas aprovadas.

## 7. CK, Modo Ratão

Fontes: `docs/fichas/ck.md`, `ferramentas/folhas_ck.py`, `ferramentas/converter_ck.py` (branch `ck`), o kit comum
(`gerar_pengaro.py`, `pengaro_extra.py`) e a seção dele em `fila_bosses.md`. **`gerar_ck.py` não existia em nenhum
checkout quando o plano foi lido** (outro agente está escrevendo): toda a numeração abaixo supõe a do kit comum, e
todos os tempos, danos e alcances são alvo.

**Estado hoje.** Convertido no checkout `ck` (sem commit na hora da leitura): 57 pastas em `quadros_arcade` e os
efeitos `aura`, `fumaca`, `garrafa`, `paredao`, `despertar_fumaca`, `bone`, `juliet`. As folhas `e_*` em disco são
do Ratão antigo. **A fila boss do CK usa o prefixo `b_`**, para não colidir com as `e_` do Ratão: onde o plano dizia
`e_soco`, a folha boss é `b_soco`. O conceito aprovado difere dos pedidos antigos: Juliet nos olhos (lente vermelha,
armação ouro), camisa roxo-escura com friso ouro e caveira de rato nas costas, chinelo dourado, pochete, cordões com
pingente de caveira de rato, tatuagens, anéis, grillz, garrafa reserva e penca de tampinhas no cós; o beck não
aparece.

A ficha e a tabela da seção 4 das regras ainda dizem "fumaça subindo dos pés": é uma coluna, a mesma forma do
Pengaró. No CK a forma principal é o **paredão e os anéis**; a fumaça dos pés vira névoa rasteira.

### 7.1 Golpes do boss

P = próprio (na ficha); V = versão boss de golpe da base; PROP = proposta. "sangra" = dano ao longo do tempo
(proposta: 2 de vida a cada 12 ticks por 120 ticks, sem acumular, sem matar; forte e finalizador: 180 ticks).

**Normais**

| Estado | Nome | Comando | Folha | i/a/t | Dano | Alc. | Propriedade | |
|---|---|---|---|---|---|---|---|---|
| 200 (+10000) | Corte Curto | x | `b_soco` | 4/3/17 | 38 | 62 | cancela, sangra leve | V |
| 3410 | Corte de Lado | y | **FOLHA NOVA** `b_corte_lado` | 7/4/26 | 58 | 80 | cancela, sangra | P |
| 230 (+10000) | Chinelada na Canela | a | `b_chute_baixo` | 5/3/19 | 40 | 64 | médio | V |
| 3420 | Chinelada Alta | b | `b_chute_alto` | 9/4/30 | 62 | 78 | alto | P |
| 400 (+10000) | Estocada Baixa | ↓ + x | **falta** `b_baixo_soco` | 4/3/16 | 35 | 56 | agachado | V |
| 3430 | Garrafa Subindo | ↓ + y | `b_cabecada` | 6/5/30 | 95 | 46, sobe até 128 | antiaéreo, lança, sangra | P |
| 430 (+10000) | Ponta de Chinelo | ↓ + a | **falta** `b_rasteirinha` | 5/3/18 | 35 | 60 | baixo | V |
| 3435 | Rasteira de Baile | ↓ + b | `b_rasteira` | 9/5/34 | 95 | 90 | baixo, derruba | PROP (5º normal novo) |
| 600 (+10000) | Corte Descendo | x no ar | `b_ar_soco` | 5/6/pouso | 55 | 62 | por cima, sangra | P |
| 601 / 610 / 611 | cotovelada / joelhada / chute duplo | y / a / b no ar | `b_ar_soco`; **falta** `b_bicicleta` | kit | 79 / 50 / 88 | kit | 611 cruza | V |
| 3431 | Garrafada por Cima | → + y | `b_martelo` | 12/4/36 | 85 | 74 | por cima, sangra | P |
| 3432 | Tropeção | → + b | **falta** `b_tropeco` | 10/4/34 | 70 | 70, avanço 2,4 | tropeça e cai num golpe baixo | PROP (6º normal novo) |
| 3433 | Assopro na Cara | ← + x | `b_beck` 3 a 6 + fumaça pequena | 8/6/30 | 20 | 60 | tonteia leve | P |
| 231 (+10000) | Calcanhar de Chinelo | ← + a | `b_chute_baixo` | kit | 57 | 62 | recua | V |
| 260 (+10000) | Afastar | y + b | **falta** `b_afastar` | 12/4/36 | 80 | 75 | lança | V |

**Correntes e kombos**

| Estado | Nome | Comando | Folha | i/a/t | Dano | Alc. | Propriedade | |
|---|---|---|---|---|---|---|---|---|
| 301 a 303 (+10000) | Uno-Dos de Caco | x x x x | `b_soco` | kit | 35 / 45 / 90 | 58 a 70 | 303 derruba | V |
| 3411 | Corte de Volta | y, y | **FOLHA NOVA** `b_corte_volta` | 6/3/24 | 60 | 78 | revés, sangra | P |
| 3412 | Estocada | y, y, y | **FOLHA NOVA** `b_estocada` | 8/4/28 | 70 | 86 | sangra | P |
| 3413 | Caco no Peito | y x4 | **falta** `b_caco_no_peito` | 12/5/44 | 120 | 88, avanço 2,2 | lança, sangra forte | P |
| 321 a 323 (+10000) | corrente a | a a a a | `b_chute_baixo` | kit | kit | kit | 323 joga longe | V |
| 3421 | Chute de Meia | b, b | **falta** `b_chute_meia` | 7/3/26 | 65 | 72 | médio | P |
| 3422 | Rasteira de Baile | b, b, b | `b_rasteira` 2 a 6 | 9/4/30 | 75 | 86 | baixo | P |
| 3423 | Passinho do Baile | b x4 | **falta** `b_passinho_baile` | 14/3+3/50 | 50 + 80 | 90, avanço 2,2 | gira e voadora de chinelo, derruba | P |
| 348 → 349 | Fim de Baile | x, → + y, b | `b_martelo`, `b_chute_alto` | 9/4/30 e 9/4/34 | 70 e 85 | - | por cima e depois derruba | P |

**Especiais, agarrões, supers**

| Estado | Nome | Comando | Folha | i/a/t | Dano | Alcance | Propriedade | |
|---|---|---|---|---|---|---|---|---|
| 3440 / 3441 | Garrafa Voadora | ↓ → + x / y | `b_bola` + `fx_garrafa` + `fx_cacos` | 14/-/42 e 16/-/46 | 70 + caco 3x15 | cai a ~110 / ~190 px | arco; estilhaça e deixa cacos 90 ticks (armadilha baixa, sangra) | P |
| 3450 / 3451 | Tragada de Beck | ↓ ↑ + x / y (recomendado ↓ ↓) | `b_beck` + fumaça | 18 / nuvem 150 ou 210 / 48 | 25 + tonteio | nasce a 50 px, segue a 0,6 / 0,9 px por tick | nuvem teleguiada lenta | P |
| 3460 / 3461 | Passinho Ratão | → ← + a / b | `b_caneta` + **falta** `b_caneta_b` | 10 / 3 ou 5 acertos / 52 ou 64 | 3x28 / 5x24 | 120 / 180 px a 4,5 | avanço de vários acertos; o último do b derruba | P |
| 3470 / 3471 | Grave do Paredão | ↓ ↑ + a / b (recomendado ↓ ↓) | `b_grave` + `fx_grave` | 8/6/40 e 12/8/50 | 30 / 45 | onda 140 / 220 px | empurra longe (vel -9); o b derruba | P |
| 3490 / 3491 | Tampinha no Olho | ← ↓ + x / y | **falta** `b_tampinha` | 9/-/34 | 3x18 | reto / leque | 3 tampinhas rápidas | PROP |
| - | Caixa Ligada | extensão do 3471 | paredão | - | - | - | depois do Grave forte o paredão fica 180 ticks soltando 1 anel por batida, que empurra sem dano | PROP |
| 1600 / 1601 (+10000) | Juliet Voadora | → ← + x / y | `b_juliet_voadora` | 12/-/40 | 60 | curto / tela | bumerangue; sem óculos até voltar | V |
| 1200 / 1201 (+10000) | Levanta, Comédia de caco | → ↓ + x / y | `b_cabecada` | 6/8/46 | 100 / 122 | 54, sobe | antiaéreo; y invencível no ativo | V |
| 1300 / 1301 (+10000) | Bote de caco | ↓ → + a / b | **falta** `b_bote` | 12/6/44 | 73 / 95 | meia tela a 6,5 | b derruba | V |
| 1700 / 1701 (+10000) | Rolê de Passinho | ← → + a / b | `b_rolamento` + **falta** `_b` | 6/-/34; b bate no 30 | 0 / 70 | passa para trás | chega virado | V |
| 800 (+10000) | Gola na Mão do Ratão | colado, → ou ← + y | `b_agarrao` + **falta** `_b` e vítima | kit | ~110 | colado | sopra fumaça, cabeçada, empurra | V |
| 3000 (+10000) | Rajada da Esquina | ← → ↓ + a / b, 1 estoque | montar com `b_soco` + `b_chute_alto` | 9/.../~90 | 245 | perto | invencível até o fim da superpausa | V |
| 3100 | Baile da Esquina | ← → ↓ + x+y, 1 estoque, só desperto | `b_golaco` + **falta** `_b`, `_c` | 6 / 5 cortes + garrafada / ~150 | 5x35 + 120 | perto | paredão gigante, dança em volta, quebra garrafa na cabeça | P |
| 3200 (+10000) | Nocaute de Rua | ← → ↓ + x / y, 2 estoques | sem folha boss | kit | 345 | kit | | V |
| 2000 | Modo Ratão | x + y, barra cheia | `despertar_boss` + **falta** `_b` | ~170 | 0 | empurra | invencível | P |

Notas:

- **Numeração:** o kit comum só tem 3400 a 3403 para especial exclusivo, um número por golpe, com código do Pengaró
  pendurado. Os especiais do CK têm fraco e forte, daí as dezenas 3440 a 3491 (abaixo de 4000, como o `efeitos_cns`
  exige).
- **Jeito chapado:** nada de sorteio (C11). Duas animações por normal, A limpa e B "tropeço", com **o mesmo frame
  data** (mesmo início, mesma caixa, mesmo alcance): a B só troca o desenho. Alternam pelo contador de uso do golpe
  (a cada terceira vez sai a B), então o replay sai igual e o robô testa uma tabela só. A versão anterior sorteava
  com `random < 300` e a B tinha +3 de início e +8 px de alcance: era frame data aleatório.
- **Cordão de Rato saiu** (3480/3481): era o quarto chicote que puxa do kit (decisão 48). O `↓ ←` do CK fica livre.
- **Contagem da regra 4:** a ficha conta "y em pé" e "b em pé" duas vezes (normal novo e 1º da corrente). Sem
  repetir são 4 normais novos (3430, 3431, 3433, 600); por isso as propostas 3432 e 3435.
- Bicuda Baixa (1400) e Pêndulo (1500): a ficha não diz se ficam; Contragolpe (1100) sai.

### 7.2 Efeitos e como cada um se mexe

| Uso | Efeito |
|---|---|
| Acerto de corte | **falta** `fx_estilhaco` (estouro de vidro verde) por cima de `hit-flash` verde e branco |
| Rastro de corte | **falta** `fx_corte` (arco verde de 5 a 6 desenhos), no elemento em que a caixa liga |
| Acerto de chinelada | `blunt-hit` cinza-esverdeado + tufo de fumaça |
| Finalizador | `crit-hit` verde + um anel de fumaça grande |
| Garrafa Voadora | `fx_garrafa` girando a 2 ticks por desenho; estilhaço + `ground-slam` pequeno; os cacos (`fx_cacos`) ficam no chão, piscam fora de fase e dão um pulinho quando o Grave bate |
| Tragada de Beck | fumaça a 3 ticks por desenho; depois ferve em loop nos desenhos 5 a 8 enquanto anda |
| Grave do Paredão | o `fx_paredao` preto aparece por dentro da fumaça 10 ticks, escala 1 → 1,25 em 6 ticks; sai o `fx_grave` rente ao chão a 9 px por tick |
| Super | paredão em escala 2 no fundo, batida em dobro, rajada de 6 anéis em leque, fundo escurecendo no compasso |
| Transformação | carga verde → `despertar_fumaca` cobrindo → paredão nascendo de baixo para cima → estilhaço na quebra da garrafa, que deixa os primeiros cacos |

### 7.3 Aura (dicionário para o `aura.py`)

```python
import aura
M = aura.Movimento
F = RAIZ / "sprites/ck/quadros/folhas_arcade"
paredao = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura_paredao.png"), altura=228), total=28)
fio = aura.ondular(aura.reduzir(aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura.png"), altura=150),
                                                  total=24), 0.6, 1.0), amplitude=3)   # mais fino: reduzido na arte
nevoa = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_nevoa_chao.png"), altura=13), total=20)  # falta
anel = aura.enquadrar(aura.recortar_folha(F / "fx_aura_aneis.png"), altura=26, ancora="centro")
brasa = aura.pedra_procedural(3, cores=((120, 200, 90), (220, 255, 190)))
AURA = aura.Aura("ck", ligada="var(20) > 0", surto="StateNo = [3000, 3999] && Time = 1", base=9600, camadas=[
    aura.Camada("paredao", paredao, plano="tras", pos=(-30, 0), surto_incha=0.08, surto_tremor=2.5,
                mov=M(deriva=(2, 2), deriva_periodo=160, alfa=0.9, respira=0.1, respira_periodo=28)),
    aura.Camada("fio", fio, tempo=3, plano="tras", pos=(-2, 2), mov=M(deriva=(3, 3), alfa=0.5)),
    aura.Camada("nevoa", nevoa, plano="frente", pos=(0, 3), surto_incha=0.0, surto_alfa=0.08,
                mov=M(deriva=(8, 0), deriva_periodo=120, alfa=0.4, respira=0.2)),
], particulas=[
    aura.Particula("anel_alto", anel, periodo=56, vida=48, area=(-44, -120, -30, -130), vel=(0.6, -0.15),
                   vel_var=(0.2, 0.1), escala=(0.6, 1.8), alfa=0.8, semente=1),
    aura.Particula("anel_baixo", anel, periodo=56, vida=48, area=(-44, -50, -30, -60), vel=(-0.6, -0.15),
                   vel_var=(0.2, 0.1), escala=(0.6, 1.8), alfa=0.8, semente=2),
    aura.Particula("brasa", brasa, periodo=8, vida=50, area=(-50, 0, 50, -20), vel=(0, -1.2), vel_var=(0.6, 0.8),
                   giro=(0, 180), escala=(1.0, 0.4), mistura="soma", semente=3),
])
```

O CK já usa os grupos de sprite 9300 a 9305 (`ck_fumaca`, `ck_garrafa`, `ck_bone`, `ck_paredao`, `ck_pod`,
`ck_dfum`): por isso a aura fica em `base=9600`. O paredão respira no alfa a cada 28 ticks, **uma batida a cerca de
128 BPM**; os dois anéis nascem a cada 56 (um por batida, alternando alto e baixo), os dois atrás do corpo. A
batida seca ("estufa em 2 ticks e volta em 5 desenhos") tem que estar **desenhada na folha** `fx_aura_paredao`: o
motor não escala a camada. Enquanto `fx_nevoa_chao` não existir, a névoa é `aura.nevoa_rasteira(124, 13, 24,
cores=((120, 132, 118), (190, 200, 186)), contorno=(60, 70, 60))`, a mesma do filme de teste (a `fx_aura` achatada
por cima dos pés saiu: escondia os pés). O "fio" é a `fx_aura` reduzida na arte (`aura.reduzir`), não pelo motor.
Esta aura é parente da "ck" que foi filmada (P1 do `gerar_teste_aura.py`).

**Reações fora do `aura.py`:** batida forte do paredão e um anel grande no congelamento de golpe forte ou
finalizador; anéis no dobro do ritmo durante especial (o surto já triplica as partículas); `fx_paredao` preto por
dentro no Grave; rastro de tufos de névoa ao andar; brasas paradas por 20 ticks ao apanhar; paredão a meia opacidade
caído; no fim do Despertar o paredão se desfaz para cima. Os cacos e tampinhas no chão não são aura: são do projétil.

### 7.4 Fluidez do corpo

Atrasa em toda folha, 1 a 2 quadros atrás do corpo: camisa aberta (abas e barra), cordões e pingente de rato (para o
lado oposto, depois assentam), alça da pochete, garrafa reserva e penca de tampinhas no cós, barra da bermuda,
chinelo quase saindo do pé nos chutes, Juliet pulando no rosto ao apanhar. O `ESTILO` do `folhas_ck.py` hoje só manda
atrasar "shorts, cap and polo collar": trocar. Texto fixo para o MOTION: *"the open shirt, the gold chains with the
rat-skull pendant, the pouch strap, the spare bottle and bottle caps at the waistband arrive one frame late and keep
swinging; the slide almost leaves the foot on kicks"*.

- **Cortes** (200, 3410 a 3412): ombro recua, corpo cambaleia para trás; 1 smear; o caco para e o cordão continua;
  braço cai pesado, um passo torto, volta à ginga.
- **Caco no Peito:** 12 ticks em 2 poses; 2 smears; avança 2,2 por 8 ticks e freia com `VelMul 0,8`; 3 poses de
  volta (quase cai para a frente, apoia, levanta).
- **Chineladas:** joelho sobe, tronco pende para trás; o chinelo "volta" um quadro depois.
- **Passinho Ratão:** `VelAdd` 0,75 por tick até 4,5, mantém, `VelMul 0,85` no fim; cada chinelada é um contato de 3.
- **Rolê:** 5 px por tick por 14 ticks sem empurrar o oponente (`PlayerPush = 0`), vira no fim; 8+ ticks de volta.
- **Grave:** levanta o pé em 2 poses, pisa, o corpo treme 2 desenhos; recuo de 1 px por tick por 6 ticks.
- Nenhum `PosAdd` maior que 2 px em nenhum golpe.

### 7.5 Folhas

Na fila (`fila_bosses.md`, 31): `b_ginga`, `b_anda`, `b_soco`, `b_chute_alto`, `b_apanha`, `b_queda`, `b_levanta`,
`b_defesa`, `b_agachado`, `b_pulo`, `b_grave`, `b_martelo`, `b_chute_baixo`, `b_cabecada`, `b_rasteira`, `b_ar_soco`,
`b_rolamento`, `b_agarrao`, `b_bola`, `b_beck`, `b_juliet_voadora`, `b_caneta`, `b_golaco`, `b_provoca`, `b_vitoria`,
`b_derrota`, `despertar_boss`, `fx_aura_paredao`, `fx_aura_aneis`, `fx_grave`, `fx_cacos`.

Nomes do plano que mudam para bater com a fila: todo `e_<nome>` do Ratão boss → `b_<nome>`; `fx_paredao_fumaca` →
`fx_aura_paredao`; `fx_anel_fumaca` → `fx_aura_aneis`; `fx_caco_chao` → `fx_cacos`; `e_grave` → `b_grave` (já na
fila); `despertar_c/d` → `despertar_boss_b`.

**O kit pede e a fila não tem:**

| Pri | Folha | MOTION |
|---|---|---|
| 1 | `b_ginga_b` | frames 9-16 of the low threatening guard continuing `b_ginga`: he bounces to the other foot, rolls the bottle wrist, the chains swing back, last frame flows into frame 1 of `b_ginga` |
| 1 | `b_anda_b` | frames 9-16 of the prowling walk continuing `b_anda`: the OTHER slide scuffs forward, shoulders roll the opposite way, last frame flows into frame 1 of `b_anda` |
| 1 | `fx_aura_paredao_b` | frames 9-16 of the smoke sound-wall loop continuing `fx_aura_paredao`: one more bass beat, the speaker cones punch out sharply in one frame and ease back over four, the smoke edges boiling, last frame flows into frame 1 |
| 1 | `fx_nevoa_chao` | AURA, ground layer: a low wide strip of grey-green smoke hugging the floor and rolling sideways, eight-frame loop, no figure |
| 1 | `b_caco_no_peito` | lunging bottle stab finisher: 1 guard, 2 sinks low, 3 pulls the elbow far back, 4 smear, 5-6 whole-body stab with the broken bottle at chest height, 7 nearly falls forward, 8 catches himself on the front foot |
| 1 | `b_passinho_baile` | funk spin into a flying slide kick: 1 guard, 2-4 a full dance spin on one foot with the shirt flaring, 5 first contact with the trailing leg, 6 flying kick with the slide (second contact), 7-8 lands in a squat and rises |
| 1 | `b_chute_meia` | mid-height side kick with the instep: 1 guard, 2 knee chambers, 3-4 leg snaps out at belly height, 5-6 leg folds, 7-8 lands with the feet crossed and uncrosses |
| 1 | `b_bote` | low lunge with the bottle: 1 guard, 2 drops the shoulder, 3-5 darts forward low with the bottle leading, 6 contact pose at full reach, 7-8 brakes on the front foot and rises |
| 1 | `b_baixo_soco` | short low stab from the squat: 1 squat, 2 the bottle hand draws back, 3-4 quick stab at shin height, 5-6 the hand returns, 7-8 settles in the squat |
| 1 | `b_rasteirinha` | quick toe poke from the squat: 1 squat, 2 the slide chambers, 3-4 the toes flick out low, 5-6 the foot returns, 7-8 settles |
| 1 | `b_bicicleta` | mid-air double slide kick, all frames in the air: 1 tucked, 2-3 first leg kicks, 4-5 second leg kicks through, 6-8 legs fold for landing, shirt up |
| 1 | `b_afastar` | shoulder barge that launches: 1 guard, 2-3 hunches and loads the shoulder, 4-5 explodes upward and forward shoulder first, 6-8 lands and staggers one step |
| 2 | `b_caneta_b` | second half of the Ratão Step dash continuing `b_caneta`: 1-5 three more slide slaps while still gliding forward, each a clear contact pose, 6 last high slap, 7-8 skids to a stop and bounces back to guard |
| 2 | `b_golaco_b` | super, second part: he dances a full circle around an unseen opponent, eight frames around the circle, slashing once per frame, seen always from the side |
| 2 | `b_golaco_c` | super, last part: 1-2 he pulls the spare bottle from his waistband, 3-4 raises it high, 5 smashes it down, 6-8 shakes the glass off his hand and nods to the beat |
| 2 | `b_rolamento_b` | second half of the dance roll: 1-3 comes out of the roll behind the opponent already turned, 4-5 short slide kick, 6-8 pops up to the guard |
| 2 | `b_agarrao_b` | street grab, second half, only him drawn: 1-2 blows smoke in the unseen face, 3-4 headbutt, 5-6 shoves it away, 7-8 fixes the Juliet on his face |
| 2 | `b_agarrao_vitima` | the victim of the street grab, generic fighter silhouette, eight frames matched to `b_agarrao`: held by the collar, head snapped back, pushed away |
| 2 | `despertar_boss_b` | transformation, second half: 1-3 the smoke sound-wall rises behind him as he flexes, 4-5 he breaks a bottle on his own forearm, 6-8 drops into the low guard, chains swinging |
| 2 | `fx_estilhaco` | hit effect: a burst of green glass: 1 white flash, 2-4 shards fly outward in a star, 5-8 shards fall and fade (magenta background) |
| 2 | `fx_corte` | slash trail: a thin green-white crescent arc: 1-2 the arc draws from top to bottom, 3 full arc, 4-6 it thins and fades (magenta background) |
| P | `b_tropeco` | stumbling attack: 1 guard, 2-3 he trips forward off balance, 4-5 falls into a low lunge with the bottle at shin height, 6-8 pushes himself back up in three steps |
| P | `b_cordao` | chain whip with the gold neck chain: 1 guard, 2-3 unhooks the long chain and swings it once, 4-5 lashes it forward at full length, pendant leading, 6-8 yanks it back and hangs it on his neck |
| P | `b_tampinha` | flicking bottle caps: 1 guard, 2 takes caps from the waistband, 3-5 three quick thumb flicks, one per frame, 6-8 hand returns to the bottle guard |

### 7.6 Ordem de ligação

1. Fechar o `gerar_ck.py` da forma base (outro agente) e confirmar a numeração suposta aqui.
2. Reescrever `CABECA_RATAO` e o `ESTILO` pelo conceito (é do agente da arte); converter as `b_` do grupo 1.
3. `ck_boss.py`: correntes y e b, normais novos, variantes A/B do "jeito chapado", sangramento no `[Statedef -2]`.
4. Aura: `paredao` e os anéis com as folhas da fila; névoa provisória pela `fx_aura`.
5. Especiais 3440 a 3471 com os comandos decididos (decisão 36); kombos da base com gatilhos novos (3433, 3431,
   3410 no lugar de 201, 216, 210), senão somem no Ratão.
6. Super 3100 antes do Nocaute no `[Statedef -1]`; a nuvem do Beck fora da conta de "um projétil por vez".
7. Vítima dos agarrões, retrato, movelist, verificador e robô, que ainda não existem.

## 8. Decisões para o dono/Breno

Tudo o que os cinco planos deixaram em aberto, numerado. Onde há recomendação do plano, ela vem depois da seta.

**Gerais**

1. **Fluidez contra a regra 7.** A regra manda golpe em pose segurada com troca seca; o dono pediu "nada duro". →
   Leitura proposta (seção 2): a fluidez vem de aura e efeitos em camadas, deslocamento em rampa, pano desenhado
   atrasado, 3 poses de recuperação e folhas `_b`; sem mexer no frame data e sem entremeio automático no corpo. Se o
   dono quer o corpo do golpe interpolado, a regra 7 muda para os bosses.
2. **"Boss final" é o quê?** O Despertar jogável e temporário, ou também um chefe do arcade sempre transformado
   (`var(20)` preso)? Muda a duração, a IA, o custo dos supers que encerram a forma e a perda de velocidade da ficha
   do Hazak.
3. **Duração do Despertar.** A regra 4 diz "até a barra drenar"; os geradores usam 600 ticks fixos e zeram a barra na
   entrada. No Pengaró a Saideira custa 1000 dentro do Despertar e não foi verificado se dá para juntar isso em 10 s.
4. **Faixa de estados.** A regra 5.1 manda exclusivos em 5000 a 5999, que é a faixa dos estados de dano do motor
   (o gerador tem `ACOES_VITIMA = (5001, 5030)`). → Corrigir a regra e ficar em 34xx.
5. **Efeito por folha ou por pixelfx.** A seção 8 diz que todo efeito vem do pixelfx; a seção 4 diz folha própria em
   fundo verde. Asas de notas, garanhão e leque não saem do pixelfx. → Aura e efeito de assinatura por folha; faísca
   genérica por pixelfx recolorido. E efeito verde (CK, Raiclaven) em fundo magenta.
6. **Reações da aura.** O `aura.py` só tem o surto. Coice do garanhão, asas-escudo, lâmina que estoca, onda do anel,
   órbita das ferraduras e aura que atrasa no pulo pedem recurso novo (esconder camada, animação de reação, troca de
   plano, talvez o primeiro Helper do kit). → Estender o `aura.py` uma vez, em vez de cada gerador improvisar.
7. **Tamanho e opacidade das auras.** Garanhão, asas, leque e paredão cobrem boa parte da tela de 320x240 e do
   adversário. Repouso reduzido com abertura total só em momentos-chave, ou sempre enormes como no conceito?
8. **Orçamento de arte.** Além das 154 folhas da `fila_bosses.md` e das 34 do Lote 7, o kit pede as da seção de
   folhas de cada lutador (contagem no fim desta seção). Quantas `_b` e quantas propostas o dono aceita pagar?
9. **Nomes e números.** Todos os nomes de golpe propostos e todos os tempos, danos e alcances "alvo": aprovar em
   bloco como ponto de partida, ou revisar um a um.

**Pengaró**

10. Aprovar ou não as seis propostas: Chicote de Elo, Pedra de Sombra, Algema, Véu do Mestre, Prisão do Quilombo,
    Elo de Cima.
11. O boss "de mãos vazias, sem garrafa" perde os golpes de bebida (lata, garrafada no agarrão 830/831, Chuva de
    Bebidas, fala de bebida) ou mantém?
12. Os kombos "Abertura" e "Empurrão" ficam inalcançáveis no Despertar (→ + y e ← + x viram golpes novos), e ← + b
    cai na corrente b da base. É de propósito?
13. Só a Latada muda de função entre os especiais da base que ficam; a regra 4 pede que todos mudem de pose ou
    função. Aceita com a troca de arte, ou cada um ganha função nova?
14. "Chicotes" na aura: no conceito há coluna, anel, elos, pedras e línguas de fumaça; chicote só aparece no prompt
    da coluna. A segunda camada de coluna espelhada serve como "chicotes"?

**Gutto**

15. Aprovar as propostas: Relincho de Guerra (no lugar do Laço da Corrente, decisão 48), Investida de Chifres, Empinada, Galope; e a Ferradura-Faísca entra?
16. O Estouro do Garanhão é o 3100 do Gutto (a 4.1 já tirou a Saideira herdada do Pengaró). Confirma, ou ele vira um terceiro super?
17. Tamanho do boss: 112 px, ou maior, como a ficha diz ("corpo maior")? Muda `CORPO` e as caixas.
18. O Beijinho continua existindo no demônio, ou tudo vira bufada? (o movelist diz "Beijo do Cavalo", a ficha diz
    bufada de fogo; a segunda variação do Beijinho segue "(confirmar)" na ficha)
19. A Investida forte pode aguentar um golpe (armadura)? E mãos: a ficha fala em "patadas de garra", o conceito tem
    punho fechado com atadura.

**Raiclaven**

20. A Cliente Zero e as cobaias continuam no boss? O conceito aprovado não mostra corrente nem ela; são cerca de 11
    folhas a mais. Se sim, de onde sai a corrente (→ de um carretel no braço mecânico)? Se não, vale o Plano B.
21. Conteúdo: mulher de coleira de ferro usada como mangual. A ficha veta piada com escravidão e estereótipo de
    mulher. Confirmar que o desenho passa no limite, ou trocar a figura.
22. Comandos: os do jogo não são os da ficha. Corrige o jogo ou a ficha? E as cobaias em ↓ ↓ + botão perdem a versão
    fraca/forte; o Mangual fica sem corrente; o kombo vira b, a, x. Aceita?
23. Leque composto por código a partir de peças soltas (`fx_aura_pecas`), ou a folha desenhada `fx_aura_leque`
    girando inteira? As reações (lâmina que estoca, lâminas que disparam) só existem com peças.
24. "Fica quase parado dando ordens" (ficha) contra "estilo de ataque com braço, tesoura, tanques e bobinas": a
    mistura proposta (x, y, ↓x, ↓y e ↓ ↓ de comando; a, b, direcionais, ar e especiais com o corpo) serve?
25. Fila de Clientes continua 2 estoques só no Despertar, com três supers na forma?
26. A ficha diz "o cabelo continua preto" e ainda traz o texto do "Surto de Tesoura"; atualizar para o cabelo verde e
    para o Cientista. Choque e fumaça ficam verdes (ficha) ou prata (aura aprovada)?

**Hazak**

27. Comandos trocados em relação à ficha: Nota Falsa e Suborno em ↓ ← (a ficha pede ↓ ↑, que bate no superpulo) e
    Chuva de Dinheiro em ← → ↓ + x/y (a ficha pede + x + y, que bate no Despertar). Falta o sim.
28. Saem no boss as correntes x e a, o Faixa no Asfalto e os 4 kombos da base? Se ficarem, são cerca de 9 folhas `d_`
    a mais.
29. **Chifres e chapéu.** No conceito os chifres atravessam a aba. A Chapelada e o Chapéu Bumerangue tiram o chapéu:
    os chifres ficam na cabeça (chapéu com dois furos), saem com o chapéu, ou o projétil vira outra coisa (maço ou
    nota bumerangue)?
30. Aprovar as quatro propostas: Aba do Sobretudo, Rabada, Sobretudo que Sobe, Dívida Paga.
31. A cena da patroa continua na transformação do boss?
32. Tamanho das asas: repouso reduzido (cerca de 180 px) e abertura total só em transformação, super e vitória, ou
    sempre enormes?
33. A Rolada desperta forte chuta com qual folha (`d_coice`, como dizia a spec, ou uma nova)?
34. Derrota e entrada despertas (`d_derrota`, `d_intro`) não estão em fila nenhuma; e a paleta de 15 cores do Diabo
    não prevê forro laranja, rabo, polaina e corrente (cabe reaproveitando índices, não testado). O sobretudo fica
    sempre nos ombros, mesmo em rolamento e queda?

**CK**

35. As folhas do Ratão antigo (`e_*`) serão todas refeitas no visual do conceito como `b_*`, e o prefixo `b_` fica?
36. ↓ ↑ ou ↓ ↓ na Tragada de Beck e no Grave do Paredão. → ↓ ↓: com ↓ ↑ o personagem pula antes do botão.
37. Aprovar ou não: Tropeção, Rasteira de Baile como normal novo, Tampinha no Olho, Caixa Ligada (o Cordão de Rato saiu).
38. Bicuda Baixa e Pêndulo ficam no Ratão? Com que pose?
39. O beck some no boss (o conceito não mostra)? Se some, a Tragada de Beck e o Assopro na Cara continuam?
40. A Juliet fica nos olhos (conceito)? Depois da Juliet Voadora ele luta sem óculos até ela voltar?
41. Sangramento: valores (proposta: 20 de vida em 120 ticks), cor (pingo vermelho ou só brilho de caco), se acumula.
42. O Grave do Paredão pode sair de dentro da defesa (guard cancel)? E "o grave treme a tela" contra a regra 8.3
    (tremida só em finalizador e super).
43. O paredão bate em ritmo fixo de 28 ticks, ou segue o áudio que ainda vai chegar?
44. Marcas: a estampa tipo Cyclone e o formato da Juliet seguem o risco já anotado na ficha. Tatuagens entram no
    prompt?

**Retoque de 2026-11-11 (revisão cética)**

45. **HUD na frente da luta.** Feito nesta rodada: o `gerar_layout.py` põe `layerno = 1` em vida, poder, retrato,
    nome, relógio, acertos e vitórias. Sem isso o motor desenha o HUD atrás dos lutadores e a aura de mais de 2x a
    altura cobria relógio e barras. Efeito colateral no jogo inteiro: lutador que pula alto passa **por trás** das
    barras. Desfazer é tirar a chamada `hud_por_cima` do `fight_def()`. Confirma?
46. **Golpe da base com arte trocada não é estilo próprio.** As linhas "V" (Raiclaven, CK), o bloco "B" (Hazak) e o
    "continuam da base" (Pengaró, Gutto) são o golpe da base com desenho novo. O pedido foi estilo de ataque só
    dele. O kit **não resolve isso**: resolve só os golpes "P". Decidir, por boss, quais normais e agarrões ganham
    dado próprio (como foi feito na 4.1 do Gutto) e quais podem ficar da base.
47. **Nome ou pose que lembra jogo comercial ou marca** (alerta por descrição; ninguém comparou com arte de jogo
    nenhum): Chapéu Bumerangue (ficha do Hazak: chapéu arremessado que volta), Juliet Voadora e a estampa tipo
    Cyclone (ficha do CK: marcas reais), Pescoço de Borracha (ficha do barbeiro: membro que estica a 190 px), e o
    garanhão gigante que atravessa a tela no super do Gutto. Os três primeiros vêm das fichas; trocar nome ou
    mecânica é decisão do dono.
48. **Puxar com corrente ou corda é só do Raiclaven** (a Cliente na coleira, que vem da ficha). A primeira versão
    dava o mesmo golpe novo a quatro bosses. Saíram: o puxão do Chicote de Elo (Pengaró: agora só bate), o Laço da
    Corrente (Gutto: virou Relincho de Guerra) e o Cordão de Rato (CK). Confirma, ou o Raiclaven também perde?
49. **Gutto com dado próprio.** A 4.1 agora é alvo dele (pesado, armadura em três golpes, um projétil só, coice
    único no finalizador b), não o herdado do Pengaró. Aprovar o perfil antes de alguém escrever o `gutto_boss.py`.

### Contagem das folhas que o kit pede e a fila não tem

| Lutador | Prioridade 1 | Prioridade 2 | Só com proposta aprovada | Total |
|---|---|---|---|---|
| Pengaró | 25 | 5 | 11 | 41 |
| Gutto | 7 | 7 | 12 | 26 |
| Raiclaven | 16 | 8 | 11 | 35 |
| Hazak | 6 | 15 | 6 | 27 |
| CK | 12 | 9 | 3 | 24 |
| **Total** | 66 | 44 | 43 | **153** |
| Retoque (folha própria por golpe e por camada) | +19 | 0 | 0 | **172** |

As 19 do retoque: Pengaró 2 (`fx_aura_chicotes`, `fx_aura_nevoa`), Gutto 8 (as seis de golpe da 4.1,
`fx_aura_garanhao_raios`, `fx_faisca_casco`), Raiclaven 5 (`e_corrente_bote2`, `e_corrente_salto`, `e_pescoco`,
`e_cabeca_virada`, `e_tentaculo`), Hazak 1 (`fx_aura_brasa_borda`), CK 3 (`b_corte_lado`, `b_corte_volta`,
`b_estocada`). Nas propostas, o Gutto troca `e_laco_a/b` por `e_relincho_a/b` e `fx_relincho`, e o CK perde
`b_cordao`: a conta da coluna fica igual.

Prioridade 1 = sem a folha o golpe ou a camada continua com arte emprestada ou não existe; 2 = fluidez (folhas `_b`,
cenas, vítimas); proposta = depende das decisões 10, 15, 20, 30 e 37.

## 9. O que foi conferido e o que não foi

- **Conferido lendo:** as cinco fichas, os dados de golpe e os comandos dos geradores (em trechos), as seções 4, 5,
  7, 8 e 9 das regras, os cinco conceitos (imagem), a `fila_bosses.md` inteira nas tabelas de folhas e os títulos do
  Lote 7.
- **Conferido no motor:** só o sistema de aura, com um lutador de teste (`chars/teste_aura`) e o HUD do jogo, na
  sandbox. Roteiro padrão (liga, loop, surto, vira, desliga) e roteiro extra (superpausa, estado custom, pulo, KO
  com pose de vitória, round 2); números no `aura_animada.md`.
- **Conferido no host:** os cinco dicionários de aura montam no `aura.py` com arte de mentira (limite da frente,
  teto de 30 Explods, partícula viva); os quadros da aura passam pelo `escrever_sff` do Hazak com as cores exatas.
- **Não verificado:** nenhum golpe, tempo ou caixa deste documento rodou em jogo; os números da 4.1 do Gutto e os
  ritmos do Hazak são alvo. Nenhum dicionário de aura rodou no motor nem com a arte de verdade; `mistura="soma"`
  nunca foi ao motor; `aura.girar_loop` só foi rodado no host.
  Os números de estado e de efeito dados como "livres" vieram de grep, não de leitura inteira dos geradores. As
  folhas boss já geradas não foram abertas, só listadas. Nenhum nome ou pose foi comparado com jogo comercial.
