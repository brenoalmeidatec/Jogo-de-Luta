# Estudo: como o corpo dá socos e chutes

Pedido do Breno em 2026-11-17: estudar de verdade como o corpo se comporta num soco e num chute (anatomia,
biomecânica, livros de artes marciais, lutas, ensino de desenho e animação de jogo de luta) e transformar isso em regra
prática para posar cada golpe no [montador](montador.md) e no [método de peças](missao-alisson-boneco-de-pecas.md).

É lei pelo passo 5 da [`regra-de-criacao-de-personagem.md`](regra-de-criacao-de-personagem.md).

Este arquivo tem três partes: **as leis do corpo** (valem para todo golpe), **as camadas perto e longe** (a causa das
"duas pernas direitas") e **a receita de cada golpe, pose por pose**. No fim, o que conferir em cada pose e as fontes.

Os números de laboratório vêm de atletas reais filmados com captura de movimento. Os tempos do jogo continuam os das
[regras dos lutadores](regras-dos-lutadores.md) (seções 7 e 8.3): o jogo comprime o golpe real, mas a **ordem** e a
**forma** das poses têm que ser as do corpo de verdade.

## Parte 1: as leis do corpo

### Lei 1. A força sobe do chão: pé, perna, quadril, tronco, ombro, cotovelo, punho

Todo golpe forte é uma corrente (a "cadeia cinética"): o pé empurra o chão, o quadril gira, o tronco vem atrás, o
ombro solta o braço e o punho chega por último, o mais rápido de todos. Nos boxeadores filmados, o pico de velocidade
do direto aparece no ombro e no quadril, depois no cotovelo e por fim no punho; o quadril é o que leva mais força e o
punho o que vai mais rápido ([Piorkowski 2011](https://knowledge.lancashire.ac.uk/id/eprint/3757/1/piorkowski-et-al-2011-punch-kinematics.pdf);
[Liu 2022](https://www.frontiersin.org/articles/10.3389/fphys.2022.1015154/pdf)). No chute é igual: a maior parte da
energia do chute circular sai do **quadril da perna de apoio**, não da perna que chuta
([Kinoshita e Fujii, ISBS 2014](https://ojs.ub.uni-konstanz.de/cpa/article/view/6038)). O Bruce Lee ensinava que o soco
"começa no pé de trás, não no ombro" ([JKD, via Bob Bremer](https://jkdwednite.com/jkd-straight-lead-punch/)).

**Na pose:** nunca mexa só o braço. Na antecipação, o quadril e o tronco já começam a virar enquanto o punho ainda
está na guarda. O membro que bate é **o último a sair e o último a chegar**. Se no quadro de contato o tronco está igual
ao do parado, o golpe sai "de boneco de posto".

Para a animação, isso é o "overlapping action": o tronco e a cabeça puxam, o braço dobrado vem atrasado e estica de uma
vez pouco antes do contato. O erro de iniciante é fazer tudo sair e chegar junto
([Game Developer, 12 princípios](https://www.gamedeveloper.com/production/the-12-principles-of-animation-in-video-games)).

### Lei 2. O peso vai para onde o punho aponta

O Jack Dempsey (*Championship Fighting*, 1950) resume: o peso do corpo tem que andar na mesma direção dos nós dos dedos;
por isso o direto com passo ("falling step", o passo de cair para a frente) bate mais que o direto só girando
([8 Limbs](https://8limbsus.com/muay-thai-thailand/jack-dempseys-body-weight-explosion-falling-step)). No laboratório,
no direto de trás os boxeadores de elite estão com **cerca de 60% do peso no pé da frente** no impacto
([Dinu e Louis 2020](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2020.598861/full)).
O mesmo estudo resume a diferença entre golpes: **o direto é o corpo andando para a frente; o gancho e o uppercut são o
corpo girando.**

**Na pose:** no contato, a linha do centro do corpo (do pescoço ao meio dos pés) se inclina para o lado do golpe. No
direto o quadril avança e passa da metade da base; no gancho ele gira no lugar; no uppercut ele sobe.

### Lei 3. Base: o centro do corpo fica em cima dos pés

O lutador só fica de pé se o centro de massa (mais ou menos no umbigo, um pouco acima da faixa) estiver em cima da área
entre os pés. Quando um pé sai do chão (chute), **o corpo todo tem que se deslocar para cima do pé que ficou**: o
quadril passa por cima do pé de apoio e o tronco se inclina para o lado contrário da perna que sobe, como contrapeso.

**Na pose:** trace uma linha vertical do umbigo até o chão. Com os dois pés no chão, ela cai entre eles. Num chute, ela
cai **no pé de apoio**, ou no máximo um palmo para fora dele. Fora disso o boneco cai.

### Lei 4. Joelhos sempre um pouco dobrados

No instante do impacto, mesmo no soco mais forte, os joelhos dos boxeadores estão dobrados (ângulo de uns 140 a 145°,
onde 180° é a perna reta) ([Dinu e Louis 2020](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2020.598861/full)).
A guarda de luta tem "uma leve dobra no joelho que deixa o lutador leve"
([Slynyrd, guarda de luta](https://slynyrd.com/blog/2024/9/26/pixelblog-52-idle-fighting-stance)). No chute, a perna de
apoio também fica levemente dobrada; perna de apoio travada reta só nos chutes altos, e mesmo assim é o que mais força o
joelho ([Chang 2021](https://www.jssm.org/jssm-20-457.xml-Fulltext)).

**Na pose:** perna de apoio reta como um poste só aparece no chute alto, e por pouco tempo. Em todo o resto, joelho
dobrado.

### Lei 5. A mão que não bate protege o rosto

Em todo golpe de verdade, a outra mão fica na guarda, perto do queixo, e o queixo fica baixo, escondido atrás do ombro
do braço que bate ([Muay Thai Guy](https://www.muay-thai-guy.com/blog/muay-thai-roundhouse-kick);
[My Boxing Coach](https://myboxingcoach.com/punching-mid-right-uppercut)). A exceção é o chute circular de muay thai,
em que o braço do mesmo lado da perna que chuta **desce e vai para trás** para ajudar o quadril a abrir, enquanto a
outra mão continua na frente do rosto.

**Na pose:** a mão livre nunca fica solta no meio do caminho. Ou ela está na guarda (perto do queixo), ou foi
deliberadamente jogada para trás como contrapeso (chute circular, chute alto, giros). **E a mão livre nunca fica na
frente do golpe**, tapando o soco ou o chute: isso é o erro da "mão solta" que o Breno viu no chute do montador.

### Lei 6. O ombro sobe e protege o queixo no soco

Quando o braço estica, a escápula (o osso da omoplata) desliza para a frente e o ombro sobe, cobrindo o queixo do lado
do soco. O braço "fica mais comprido" por isso, e não porque o braço estica. No método de peças o braço é sempre o mesmo
desenho; o alcance a mais vem de **mover a junta do ombro para a frente e para cima** (uns 10 a 20 px no 3x) e de girar
o tronco, nunca de esticar a peça.

### Lei 7. O braço chega esticado, mas não travado

No impacto do direto, o cotovelo ainda não está travado: o punho encosta antes da extensão total e continua entrando
uns 5 cm ("2 polegadas de penetração", no ensino do Bruce Lee) ([JKD](https://jkdwednite.com/jkd-straight-lead-punch/);
[Dinu e Louis 2020](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2020.598861/full)).
O punho vira de lado (palma para baixo) no direto e no jab, e fica com a palma para dentro, virada para o próprio
rosto, no gancho.

**Na pose:** no quadro de contato o braço está quase reto. A variante "esticado" do kit serve, mas o cotovelo não pode
dobrar para o lado errado. O exagero (braço 10 a 15% mais longo) só vale num quadro, decidido à mão (regra da
[revisão #51](anatomia-51/LEIA-ME.md)).

### Lei 8. Joelho primeiro, pé depois (a "câmara")

Em todo chute de perna dobrada (frontal, circular, lateral), a coxa sobe primeiro com o joelho bem dobrado e o pé
recolhido perto da bunda; só depois a canela abre como um chicote
([Wikipédia, chute circular](https://en.wikipedia.org/wiki/Roundhouse_kick);
[Frontiers 2026, chute lateral](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2025.1708748/full)).
A volta faz o caminho contrário: a canela dobra de volta para a câmara e só então o pé desce.

Exceções: o chute de muay thai (a perna vai quase reta como um taco de beisebol) e os chutes de capoeira em arco
(armada, meia-lua, queixada), que vão de perna esticada.

### Lei 9. O pé de apoio gira no chute circular

No chute circular, o pé que fica no chão gira na ponta (no "ball" do pé) até os dedos apontarem para longe do oponente
e o calcanhar apontar para ele. É esse giro que deixa o quadril virar por cima
([Wikipédia](https://en.wikipedia.org/wiki/Roundhouse_kick); [Muay Thai Guy](https://www.muay-thai-guy.com/blog/muay-thai-roundhouse-kick);
[Dendê Arts, martelo](https://dendearts.com/blog/a-comprehensive-list-of-capoeira-kicks/)).

**Na pose:** no contato do chute circular, o pé de apoio aparece **de calcanhar para a frente** (para o oponente). Se o
pé de apoio está igual ao do parado, o quadril não virou e o chute fica sem força. No jogo de peças isso pede uma
variante de pé ("pé girado", visto de trás ou de calcanhar).

### Lei 10. Antecipação curta, contato segurado, volta mais lenta

Na luta real, preparar demais é "telegrafar" o golpe; no jogo, a antecipação é o que deixa o golpe legível. Basta um
quadro de antecipação para o golpe ler muito melhor ([80.lv, Skullgirls](https://80.lv/articles/tips-on-making-fluid-and-powerful-animations)).
O ritmo do corpo é "começa devagar, vai muito rápido, para, volta devagar"
([Jay's guide](https://jayts.neocities.org/guide/smooth.html)). Quadro a mais entre a antecipação e o contato faz o
cérebro achar que o golpe veio devagar: **entre a antecipação e o contato não vai quadro do meio** (no máximo o borrão).

Os tempos reais servem de régua para não exagerar: o jab e o direto duram uns 175 ms (cerca de 10 ticks) do começo ao
fim e ficam encostados só 24 a 30 ms (2 ticks) ([Mosler 2024](https://www.mdpi.com/2076-3417/14/17/7785)); o gancho
leva mais tempo para chegar que o direto (477 contra 357 ms) ([Piorkowski 2011](https://knowledge.lancashire.ac.uk/id/eprint/3757/1/piorkowski-et-al-2011-punch-kinematics.pdf)).
O jogo usa os tempos da seção 8.3 das regras: fraco 3 a 5 ticks até encostar, forte 7 a 10, finalizador 10 a 14.

### Lei 11. A cabeça atrasa e assenta depois

"A cabeça muitas vezes dá um tranco depois que o resto do corpo para, depois do soco"
([Game Developer](https://www.gamedeveloper.com/production/the-12-principles-of-animation-in-video-games)). O
`vida_pecas.py` já faz o atraso da cabeça quando o montador grava "com vida". Na pose-chave, a cabeça fica **olhando
para o alvo** o golpe inteiro, inclusive nos giros (no giro ela vira antes do corpo e chega antes).

### Lei 12. Silhueta e linha de ação

Num jogo rápido, a silhueta é a ferramenta principal: o punho tem que ser reconhecido na hora só pelo contorno
([80.lv](https://80.lv/articles/tips-on-making-fluid-and-powerful-animations)). Cada pose-chave tem uma **linha de
ação**: uma curva em C ou uma reta, do pé de apoio até o punho ou o pé que bate. Jab tem linha curta; chute alto e
gancho forte têm linha longa e curva ([Jay's guide](https://jayts.neocities.org/guide/smooth.html);
[Proko, gesto](https://www.proko.com/course-lesson/how-to-draw-gesture/notes)). Cabeça, caixa torácica e bacia nunca
ficam paralelas: alterne os ângulos, porque simetria endurece o boneco.

**Teste:** pinte a pose de preto. Se não dá para saber qual golpe é e qual membro bate, a pose não está pronta.

## Parte 2: perto e longe, frente e trás (a causa das "duas pernas direitas")

### Dois eixos diferentes

O kit usa "frente" e "trás", e isso quer dizer **o lado do oponente**: braço da frente é o que está mais perto do
oponente. Mas para desenhar existe outro eixo, **perto e longe da câmera**, e é ele que decide quem passa por cima de
quem. Confundir os dois dá o erro que o Breno viu.

Os nossos lutadores, virados para a direita, ficam na guarda aberta para a câmera (peito de três quartos, como no
`parado` do Pengaró). Nessa vista:

| Lado do corpo | No Pengaró | Em relação ao oponente | Em relação à câmera | Camada na raiz (ombro ou quadril) |
| --- | --- | --- | --- | --- |
| esquerdo | punho erguido, perna de calça branca | **frente** | **longe** | **atrás** do tronco e da bacia |
| direito | garrafa, perna da caneleira verde | **trás** | **perto** | **na frente** do tronco e da bacia |

Ou seja: **o lado da frente é o lado longe**. O ombro e o quadril da frente ficam escondidos atrás do peito e da faixa.
O braço da frente e a perna da frente só aparecem a partir de onde saem da silhueta do tronco.

A roupa ajuda a não errar: no Pengaró, **a caneleira verde está só na perna de trás (direita)** e a garrafa só na mão de
trás. Cada lutador deve ter uma marca assim de cada lado, anotada na ficha.

### O que deu errado no chute do montador

No `chute_alto` (tanto no desenho antigo da IA quanto nas peças), a perna que chuta é a da frente (calça branca, lado
esquerdo, **longe**), mas ela foi desenhada **por cima** da faixa e do tronco, cruzando a barriga a partir do quadril de
trás. O olho lê que ela nasce do quadril **perto**, que é o mesmo da perna de apoio com a caneleira. Resultado: duas
pernas saindo do mesmo lado, "duas pernas direitas". O braço da frente, com a mão aberta, ficou por cima da perna, na
frente do chute, e tapa o golpe.

Os dois jeitos certos de posar esse chute:

1. **Chute com a perna da frente (longe), como está hoje:** a coxa nasce **atrás** da faixa, do lado do oponente (o
   quadril da frente fica uns 50 px à direita do de trás no 3x do Pengaró: `QUADRIL_FRENTE` 572 contra `QUADRIL_TRAS`
   522). A raiz da coxa fica escondida pela faixa e pela barriga; a coxa aparece saindo pela frente da silhueta, e a
   canela e o pé ficam livres no ar. Camadas: perna da frente **abaixo** do quadril e do tronco. O braço da frente
   desce para trás da perna (ou vai para trás do corpo) e o braço de trás (garrafa) sobe para a guarda ou abre para
   trás como contrapeso.
2. **Chute com a perna de trás (perto):** aí sim a perna passa **por cima** do corpo, e quem sobe é a perna da
   caneleira; a perna de apoio passa a ser a de calça branca, com o pé de apoio girado. É o chute alto mais forte (o
   quadril vira por cima) e o mais natural de desenhar cruzando a frente do corpo.

Em qualquer dos dois: **a perna que chuta e a perna de apoio saem de quadris diferentes**, separados pela largura da
bacia, e as marcas da roupa conferem com o lado.

### Regra de camadas para cada pose

A ordem de camadas de cada lutador (`CAMADAS` no kit) é a do parado e serve para a guarda. Em golpe, ela muda conforme
o membro cruza o corpo. A regra:

1. **Raiz manda:** a peça do lado longe começa **atrás** do tronco (e a coxa longe, atrás da bacia); a do lado perto,
   **na frente**.
2. **Cruzou a linha do peito, troca:** um membro longe que passa para o lado da câmera (raro: giros, armada, meia-lua)
   passa para cima na pose em que cruza. Um membro perto que vai para trás do corpo (braço jogado para trás no chute
   circular) passa para baixo do tronco.
3. **O membro que bate nunca fica escondido no contato:** se a raiz dele é longe, o que aparece é a parte que saiu da
   silhueta (antebraço e punho, canela e pé). Se nem isso aparece, a pose está no ângulo errado; gire o tronco.
4. **A mão livre fica atrás do golpe, nunca na frente dele.**

Hoje o Pengaró desenha o braço da frente por cima de tudo (`CAMADAS` de `boneco_pecas.py`), o que só funciona enquanto
o braço da frente não cruza o tronco; o Gutto desenha o braço de trás por cima (`boneco_gutto.py`), que é o certo pela
regra 1. O montador precisa de **ordem de camadas por pose** (mandar uma peça para trás ou para a frente do tronco só
naquela pose) para cumprir as regras 2 a 4; é o que o Breno pediu na conversa do montador.

### Pé esquerdo não é pé direito

Pé e mão são espelhados: o dedão fica sempre do lado de dentro (do lado do outro pé). Quando a perna longe chuta, o
pé dela não pode ser uma cópia do pé da perna de apoio, porque aí os dois pés viram "o mesmo pé". No chute com a perna
da frente, o pé que chuta mostra o peito do pé ou a sola com o dedão **para cima ou para a câmera** conforme o giro,
nunca o mesmo contorno do pé que está no chão. Com as mãos vale o mesmo: punho fechado da frente e de trás têm o dedão
de lados opostos.

### Limites das juntas (para a régua do montador)

Valores clássicos de amplitude articular de adulto (goniometria), com folga para lutador treinado. Passou disso, o
boneco "quebrou":

| Junta | Dobra | Abre ou estica | Nunca |
| --- | --- | --- | --- |
| cotovelo | até ~145° de dobra | reto (0°), no máximo 5 a 10° além | dobrar para o lado de fora |
| joelho | até ~140° de dobra (calcanhar quase na bunda) | reto, nunca além | dobrar para a frente |
| quadril, coxa para a frente | ~120° com o joelho dobrado; ~90° com a perna esticada (o resto do chute alto vem da bacia inclinando e do tronco indo para trás) | ~20 a 30° para trás | coxa esticada passando de 90° sem a bacia girar |
| quadril, abrir para o lado | ~45° normal; lutador treinado chega a 90° girando a bacia | | |
| ombro | ~180° para cima e para a frente | ~50° para trás | braço passando por dentro do tronco |
| pescoço | ~45° para baixo, ~60° de giro | ~45° para trás | cabeça girando sem o ombro acompanhar no giro do corpo |
| coluna (tronco sobre a bacia) | ~30 a 45° de giro, ~30° de inclinação para a frente | ~20° para trás | tronco girando sozinho com a bacia parada no golpe forte |

O chute na altura da cabeça só é possível porque a bacia vira e se inclina junto com a coxa e o tronco vai para trás.
No montador: **coxa acima da horizontal pede quadril inclinado e tronco para trás**, senão a coxa "sai" da bacia.

## Parte 3: a receita de cada golpe

Como ler: cada linha é uma pose-chave do montador. "Ticks" segue as regras do jogo (fraco 3 a 5 ticks até encostar,
forte 7 a 10; contato segura o ativo mais 1 ou 2 ticks; cada pose de volta segura 4 a 9). "Camadas" fala só do que
muda em relação ao parado. Graus são em relação ao parado (0° = como no parado). "Para a frente" é na direção do
oponente.

### Guarda (o ponto de partida de tudo)

- Pés afastados mais ou menos na largura dos ombros, pé da frente apontando para o oponente, pé de trás meio de lado,
  **calcanhar de trás levantado** (o peso na ponta do pé de trás) ([JKD](https://jkdwednite.com/punching-power/);
  [Black Belt](https://www.blackbeltmag.com/post/the-well-heeled-martial-artist-the-debate-in-karate)).
- Peso dividido, um pouco mais na frente. Joelhos dobrados. Queixo baixo, "pescoço afundado nos ombros"
  ([Slynyrd](https://slynyrd.com/blog/2024/9/26/pixelblog-52-idle-fighting-stance)).
- Cotovelos fechados cobrindo as costelas. Punho da frente na altura do nariz do oponente.
- Na ginga, tudo segue o tronco: sobe ao esticar as pernas e desce um pouco mais rápido (a descida mais rápida "vende" a
  gravidade). A mão de dentro (longe) mexe mais que a de fora.

### Jab (soco fraco, braço da frente, longe)

O golpe mais rápido e de linha mais curta. Quase não gira o corpo; o ombro é que leva.

| Pose | Ticks | O que muda |
| --- | --- | --- |
| 1. Guarda | | parado |
| 2. Antecipação | 1 a 2 | joelhos afundam 2 a 4 px; ombro da frente recua só um pouco; punho da frente sai da guarda **reto para a frente**, sem ir para trás nem para baixo |
| 3. Contato | 2 a 3 (o ativo +1) | braço da frente na variante esticado, punho de lado (palma para baixo) na altura do queixo do oponente; junta do ombro da frente 10 a 15 px para a frente; tronco gira 10 a 15° para a frente; pé da frente pode dar um passinho (o soco chega um pouco antes do pé tocar o chão, como ensinava o Bruce Lee); mão de trás colada no queixo; queixo atrás do ombro da frente |
| 4. Volta | 4 a 6 | braço volta **pelo mesmo caminho**, reto, direto para a guarda |

Camadas: o braço da frente nasce atrás do peito; no contato o ombro fica escondido e o braço sai da silhueta já no
bíceps. Erros comuns: punho que desce antes de sair, braço que sai pelo lado (vira gancho), corpo parado.

### Direto (soco forte, braço de trás, perto)

O soco de mais peso. O corpo inteiro anda para a frente.

| Pose | Ticks | O que muda |
| --- | --- | --- |
| 1. Guarda | | parado |
| 2. Antecipação | 3 a 5 | joelhos afundam 4 a 8 px; quadril e ombro de trás recuam 5 a 10° (enrola); punho de trás ainda na guarda; peso no pé de trás |
| 3. Borrão (opcional) | 1 a 2 | braço meio esticado com rastro, ombro já virando |
| 4. Contato | ativo +2 | **calcanhar de trás gira para fora** (pé de trás na ponta, girado); quadril gira 30 a 45° para a frente e avança; tronco gira 45 a 60° (o peito passa a olhar mais para a câmera e para o oponente); ombro de trás vai para a frente e sobe, cobrindo o queixo; braço de trás esticado (não travado), punho de lado na altura do queixo do oponente; **60% do peso no pé da frente**; joelho da frente dobra mais; braço da frente volta para o rosto (o "whirl": recolher um braço puxa o outro para a frente) |
| 5. Volta 1 | 4 a 6 | braço recolhe pela mesma linha; quadril começa a desvirar |
| 6. Volta 2 | 5 a 8 | guarda, calcanhar de trás levanta de novo |

Camadas: braço de trás **por cima** do tronco do começo ao fim. O braço da frente, recolhido, fica por baixo do braço
de trás e por cima do tronco só onde sair da silhueta. Erros comuns: pé de trás chapado e parado (quadril não virou),
tronco reto, braço da frente esquecido esticado.

### Gancho (braço da frente, longe)

Golpe de giro, não de avanço. O braço é uma peça rígida e quem bate é o corpo girando.

| Pose | Ticks | O que muda |
| --- | --- | --- |
| 1. Guarda | | parado |
| 2. Antecipação | 4 a 7 | joelhos afundam ("sudden drop" do JKD); peso passa um pouco para o pé da frente; tronco enrola 10 a 20° para o lado do braço da frente; cotovelo da frente sobe até a altura do ombro |
| 3. Contato | ativo +2 | **pé da frente gira na ponta** (calcanhar para fora); quadril e tronco giram 45 a 60° para o lado do braço de trás; braço da frente dobrado em **90 a 110°**, antebraço paralelo ao chão, cotovelo na altura do punho; punho com a palma virada para o rosto ou para baixo; o punho chega ao alvo **de lado**, vindo de fora; mão de trás no queixo |
| 4. Volta | 5 a 8 | tronco desvira, braço desce para a guarda |

Camadas: no contato o braço da frente passa **na frente do rosto e do peito** (o punho cruza a linha do corpo), então a
partir do contato o antebraço da frente vai **por cima** da cabeça e do tronco, enquanto o ombro da frente continua
escondido. Erros comuns: cotovelo baixo (vira uppercut torto), braço esticado (vira tapa), corpo sem girar.

### Uppercut (braço de trás, perto)

O soco que sobe. O corpo afunda e levanta girando; o peso **fica no pé de trás**
([My Boxing Coach](https://myboxingcoach.com/punching-mid-right-uppercut)).

| Pose | Ticks | O que muda |
| --- | --- | --- |
| 1. Guarda | | parado |
| 2. Antecipação | 5 a 8 | joelhos afundam bem (8 a 15 px no 3x); tronco inclina para o lado do braço de trás e um pouco para a frente; punho de trás desce **só até a altura do peito**, sem ir para trás |
| 3. Contato | ativo +2 | pernas esticam empurrando o chão (o corpo sobe 10 a 20 px); quadril de trás gira para a frente e **para cima**; braço em **L** (cotovelo dobrado uns 90°), punho de palma para o próprio rosto, subindo na frente do peito até a altura do queixo do oponente; queixo colado no peito; mão da frente no rosto |
| 4. Volta | 5 a 8 | punho volta direto para a guarda |

Versão de jogo ("plusing"): o uppercut que lança o oponente pode terminar com o corpo nas pontas dos pés e o braço mais
alto que a cabeça, exagerado de propósito para ler como antiaéreo
([Game Developer](https://www.gamedeveloper.com/production/the-12-principles-of-animation-in-video-games)).

Erros comuns: punho que mergulha para baixo antes de subir (telegrafa), cabeça levantando junto, corpo sem afundar.

### Chute frontal (ponteira ou benção, perna de trás ou da frente)

Chute em linha reta, empurrando com a ponta ou com a sola.

| Pose | Ticks | O que muda |
| --- | --- | --- |
| 1. Guarda | | parado |
| 2. Câmara | 3 a 6 | joelho sobe na frente do corpo até a altura da cintura ou mais, canela dobrada e pé recolhido (calcanhar perto da bunda); quadril de apoio fica em cima do pé que ficou no chão; tronco inclina uns 5 a 10° para trás |
| 3. Contato | ativo +1 ou +2 | quadril empurra para a frente e a canela estica: perna quase reta, ponta do pé (ponteira) ou sola e calcanhar (benção) no alvo; tronco **ereto** ou um pouco para trás, nunca muito deitado ([Preuschl 2016](https://jssm.org/jssm-15-92.xml-Fulltext)); braços na guarda, ou o braço do lado da perna desce um pouco |
| 4. Recolhe | 3 a 5 | canela dobra de volta para a câmara (não desce esticada) |
| 5. Pousa | 4 a 6 | pé desce na frente ou volta para trás, guarda |

Camadas: perna de trás (perto) chutando vai **por cima** da coxa de apoio e da bacia; perna da frente (longe) chutando
nasce **atrás** da faixa. Erros comuns: chute frontal sem câmara (a perna sobe reta como um poste), tronco deitado para
trás demais, perna de apoio reta.

### Chute circular (martelo, perna de trás, perto)

O chute de capoeira e de muay thai que vem de lado. Quem bate é o quadril virando por cima.

| Pose | Ticks | O que muda |
| --- | --- | --- |
| 1. Guarda | | parado |
| 2. Câmara | 4 a 7 | joelho de trás sobe na frente do peito (o "joelho alto" do martelo, que também engana); pé de apoio começa a girar na ponta; braço do lado da perna começa a descer |
| 3. Contato | ativo +2 | **pé de apoio girado, calcanhar para o oponente**, joelho de apoio levemente dobrado; **quadril virado por cima** (a coxa que chuta fica quase horizontal, o joelho apontando para a frente ou já virado para baixo); canela esticada batendo com a canela (muay thai) ou com o peito do pé (capoeira, taekwondo); tronco inclina para o lado contrário (contrapeso) e gira; **braço do lado da perna desce e vai para trás**; a outra mão fica na frente do rosto; cabeça e olhos no alvo |
| 4. Atravessa ou recolhe | 3 a 5 | no estilo muay thai o corpo continua girando (follow-through); no estilo capoeira a canela dobra de volta para a câmara |
| 5. Pousa | 5 a 8 | pé volta pelo mesmo caminho para trás, guarda |

Camadas: a perna que chuta é a perto, então vai **por cima** de tudo no contato. O braço jogado para trás passa para
**baixo** do tronco (regra 2). Erros comuns: pé de apoio igual ao do parado, quadril que não vira (a perna sobe "de
frente" e vira chute frontal torto), braço solto na frente do chute.

### Chute alto (a perna sobe até a cabeça)

É um circular ou um frontal na altura da cabeça. Tudo o que vale para eles, mais isto:

- A coxa acima da horizontal só existe com a **bacia inclinada** (o quadril do lado da perna sobe) e o **tronco indo
  para trás e para o lado contrário**. Sem isso a coxa "sai" da bacia.
- A perna de apoio estica mais (é o único golpe em que ela pode ficar quase reta) e o pé de apoio gira.
- O braço do lado da perna vai para trás e para baixo; o outro fica no rosto.
- Com a perna da frente (longe): coxa nasce **atrás** da faixa, como explicado na Parte 2; é o chute alto rápido, mais
  fraco. Com a perna de trás (perto): passa **por cima** do corpo; é o forte.
- Volta: o joelho dobra **antes** de descer. Perna esticada caindo do alto lê como boneco de pano.

### Chute baixo e rasteira

- Chute baixo na coxa (low kick): circular curto, câmara baixa, a canela bate na altura do joelho do oponente; o tronco
  quase não inclina e a guarda fica alta.
- Rasteira: o corpo agacha (quadril desce até perto do joelho de apoio), uma ou as duas mãos podem tocar o chão, a perna
  que varre vai esticada rente ao chão girando a partir do quadril; o pé de apoio gira na ponta; a cabeça fica alta,
  olhando o oponente.

### Giros de capoeira (meia-lua de compasso, armada, queixada)

Chutes em arco, de perna esticada, em que o corpo gira e a perna vem "como o taco de golfe"
([Lalaue](https://www.lalaue.com/moves/meia-lua-de-compasso/); [Dendê Arts](https://dendearts.com/blog/a-comprehensive-list-of-capoeira-kicks/)).

- **Meia-lua de compasso:** o peito vira para a perna de trás, o corpo agacha sobre a perna mais perto do alvo, a mão
  (uma, na versão rápida; duas, no rabo de arraia) vai ao chão entre as pernas, a cabeça olha o oponente por entre as
  pernas, e a perna de trás sobe esticada e gira, batendo com o **calcanhar** ([Bristol Capoeira](https://bristol.ac.uk/depts/union/capoeira/moves.html)).
  Poses: guarda, giro com a mão descendo (4 a 6 ticks), mão no chão e perna subindo, contato com o calcanhar no alto
  (ativo +2), perna descendo pelo arco, volta para a ginga.
- **Armada:** de pé, sem mão no chão. Um pé cruza na diagonal na frente do outro, o corpo torce, a cabeça vira primeiro
  e olha o oponente, e a outra perna sobe esticada em arco, batendo com a borda de fora do pé ou o calcanhar. Braços
  abertos para fora.
- **Queixada:** de lado para o alvo, a perna sobe esticada de dentro para fora, mirando o queixo.

Camadas nos giros: durante o giro o corpo fica de costas para a câmera ou para o oponente por um ou dois quadros. **Use
a vista de costas da folha-modelo** (mesma altura e largura) e troque a ordem de camadas no quadro em que cada membro
cruza a linha do peito. A cabeça vira antes do corpo e chega antes (Lei 11).

### Cabeçada

Golpe de curta distância. Na rua quem recua antes telegrafa; no jogo a antecipação é pequena e para a frente.

| Pose | Ticks | O que muda |
| --- | --- | --- |
| 1. Guarda | | parado |
| 2. Antecipação | 3 a 5 | queixo desce para o peito, pescoço duro, ombros sobem; tronco recua só um pouco (2 a 5°) ou nem recua; as mãos sobem para agarrar ou para a frente do peito |
| 3. Contato | ativo +2 | passo curto com o pé da frente; o tronco **dobra no meio das costas** (não só na cintura) e vai para a frente uns 20 a 30°; o pescoço fica rígido e quem bate é o **alto da testa** contra o rosto do oponente, com o peso do corpo indo junto; as mãos seguram o oponente ou protegem ([TKD Tutor](https://tkdtutor.blogspot.com/p/martial-arts-taekwondo-head-butts.html); [Fight Encyclopedia](https://fightencyclopedia.com/videos/1982/strike/headbutt/forward-headbutt/standard-forward-headbutt/standard-forward-headbutt-technique)) |
| 4. Volta | 5 a 8 | tronco desdobra, guarda |

Erros comuns: a cabeça indo sozinha (só o pescoço dobra, o corpo parado), batendo com a cara ou com o topo da cabeça,
olhos fechados apontando para o chão.

### Cotovelada e joelhada (curta distância)

- **Cotovelada:** é um gancho com o braço todo dobrado (punho perto da orelha), batendo com a ponta do cotovelo; o
  corpo gira igual ao gancho. A de cima para baixo afunda os joelhos no contato.
- **Joelhada:** o quadril empurra para a frente, a coxa sobe com o joelho bem dobrado e a ponta do pé para baixo, o
  tronco vai para trás para o quadril passar, as mãos puxam a cabeça ou o ombro do oponente para baixo.

### Golpes no ar

Sem chão não existe cadeia que começa no pé: o golpe vem do **tronco dobrando** (encolhe e abre). Soco no ar: tronco
inclina para a frente, pernas encolhidas. Chute no ar: a perna que bate estica e a outra encolhe (as duas esticadas
juntas parece ginástica). O centro de massa segue o arco do pulo; a pose não muda a trajetória.

## Parte 4: o que conferir em cada pose

Antes de gravar uma pose no montador, passe por esta lista. Os itens com (régua) dá para o montador acusar sozinho no
futuro.

1. **Qual membro bate?** Está escrito na ficha (frente ou trás) e a marca da roupa confere (no Pengaró: caneleira e
   garrafa são de trás).
2. **Raiz no lado certo:** membro longe nasce atrás do tronco e da faixa; membro perto, na frente. Perna que chuta e
   perna de apoio saem de quadris diferentes. (régua: distância entre as raízes das coxas igual à do parado)
3. **Mão livre:** na guarda ou jogada para trás. Nunca na frente do golpe.
4. **Base:** a vertical do umbigo cai entre os pés, ou no pé de apoio no chute. (régua)
5. **Pé de apoio:** girado no circular e no direto; calcanhar levantado na guarda e no direto.
6. **Joelhos dobrados**, menos no apoio do chute alto.
7. **Juntas dentro do limite** da tabela da Parte 2. Cotovelo e joelho nunca dobram para o lado errado. (régua)
8. **Corpo antes do braço:** na antecipação o quadril e o tronco já se mexeram; no contato o tronco girou (jab 10 a 15°,
   direto 45 a 60°, gancho 45 a 60° para o outro lado).
9. **Cabeça olhando o alvo**, queixo baixo atrás do ombro.
10. **Pé e mão espelhados:** o pé que chuta não é cópia do pé de apoio; dedão do lado de dentro.
11. **Silhueta em preto** lê o golpe.
12. **Volta pelo mesmo caminho** e câmara antes de baixar a perna.

## O que o montador ganharia com isto

Sugestões para quem mexer no [montador](montador.md), sem prioridade imposta:

- **Ordem de camadas por pose** (mandar a peça para trás ou para a frente do tronco naquela pose). É o que resolve a
  mão solta e o chute com a perna longe.
- **Variantes de pé:** pé girado (visto de calcanhar) para o apoio do circular e do direto, e pé que chuta espelhado.
- **Régua de juntas** com a tabela de limites, e uma **régua de base** (vertical do centro de massa contra os pés).
- **Marca de lado** no osso (perto ou longe) para a casca de cebola pintar o lado longe mais escuro, como os desenhos de
  animação fazem para não confundir.

## Fontes

Biomecânica (laboratório):

- [Dinu e Louis (2020), cinemática do direto, gancho e uppercut em boxeadores de elite e juniores, Frontiers](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2020.598861/full)
- [Piorkowski, Lees e Barton (2011), soco único contra combinação, Universidade de Central Lancashire (PDF)](https://knowledge.lancashire.ac.uk/id/eprint/3757/1/piorkowski-et-al-2011-punch-kinematics.pdf)
- [Mosler, Kacprzak e Wąsik (2024), jab contra direto, força e massa efetiva, Applied Sciences](https://www.mdpi.com/2076-3417/14/17/7785)
- [Liu e outros (2022), soco reto da frente em elite e juniores, Frontiers (PDF)](https://www.frontiersin.org/articles/10.3389/fphys.2022.1015154/pdf)
- [Kinoshita e Fujii (2014), chute circular de taekwondo antes de o pé sair do chão, ISBS](https://ojs.ub.uni-konstanz.de/cpa/article/view/6038)
- [Chang e outros (2021), perna de apoio no chute circular em três alturas, JSSM](https://www.jssm.org/jssm-20-457.xml-Fulltext)
- [Preuschl e outros (2016), chute de machado com salto, JSSM](https://jssm.org/jssm-15-92.xml-Fulltext)
- [Frontiers in Physiology (2026), chute lateral em iniciantes e experientes](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2025.1708748/full)

Ensino de artes marciais:

- Jack Dempsey, *Championship Fighting: Explosive Punching and Aggressive Defense* (1950), trechos em
  [8 Limbs](https://8limbsus.com/muay-thai-thailand/jack-dempseys-body-weight-explosion-falling-step) e
  [JKD Wednesday Night Group](https://jkdwednite.com/punching-power/)
- Bruce Lee, soco reto da frente ensinado a Bob Bremer, em [JKD Wednesday Night Group](https://jkdwednite.com/jkd-straight-lead-punch/)
- [George Chung, o calcanhar de trás no caratê, Black Belt Magazine](https://www.blackbeltmag.com/post/the-well-heeled-martial-artist-the-debate-in-karate)
- [Chute circular (Wikipédia)](https://en.wikipedia.org/wiki/Roundhouse_kick),
  [Muay Thai Guy](https://www.muay-thai-guy.com/blog/muay-thai-roundhouse-kick),
  [Martial Theory, dois jeitos de dar o mesmo chute](https://martialtheory.substack.com/p/a-tale-of-two-kicks)
- [My Boxing Coach, uppercut de trás](https://myboxingcoach.com/punching-mid-right-uppercut)
- Capoeira: [Dendê Arts](https://dendearts.com/blog/a-comprehensive-list-of-capoeira-kicks/),
  [Lalaue, meia-lua de compasso](https://www.lalaue.com/moves/meia-lua-de-compasso/),
  [Capoeira da Universidade de Bristol](https://bristol.ac.uk/depts/union/capoeira/moves.html)
- Cabeçada: [TKD Tutor](https://tkdtutor.blogspot.com/p/martial-arts-taekwondo-head-butts.html),
  [Fight Encyclopedia](https://fightencyclopedia.com/videos/1982/strike/headbutt/forward-headbutt/standard-forward-headbutt/standard-forward-headbutt-technique)

Desenho e animação:

- [Mariel Cartwright, animação fluida e forte no Skullgirls (80.lv, palestra da GDC 2014)](https://80.lv/articles/tips-on-making-fluid-and-powerful-animations)
- [Os 12 princípios da animação em jogos, Game Developer](https://www.gamedeveloper.com/production/the-12-principles-of-animation-in-video-games)
- [Jay's guide: o que deixa um jogo de luta "liso"](https://jayts.neocities.org/guide/smooth.html)
- [12 princípios para animação de jogo de luta, SBGames 2020 (PDF)](https://www.sbgames.org/proceedings2020/ArtesDesignFull/209727.pdf)
- [Slynyrd, guarda de luta em pixel art](https://slynyrd.com/blog/2024/9/26/pixelblog-52-idle-fighting-stance)
- [Proko, desenho de gesto e linha de ação](https://www.proko.com/course-lesson/how-to-draw-gesture/notes)
- Richard Williams, *The Animator's Survival Kit* (antecipação, peso e sobreposição), referência clássica de animação

Os limites das juntas são os valores clássicos de goniometria de adultos, arredondados; não vêm de um estudo de
lutadores. Os graus de giro do tronco por golpe são estimativa de desenho a partir das fontes acima (os estudos medem
velocidade e força, quase nunca o ângulo do tronco no impacto).
