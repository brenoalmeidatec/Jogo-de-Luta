# Cenários de Nazaré: projeto dos quatro lugares e fila de arte

> Pedido do Alisson (2026-11-11): cenários de luta **animados** de Nazaré das Farinhas: o Cristo, a Maria Fumaça, a praça
> da prefeitura e a passarela. Este arquivo é o projeto de cada cenário (lugar real, camadas, hora do dia, o que se mexe)
> e a fila de imagens a pedir no ChatGPT, com o prompt pronto. As medidas e o gerador estão em
> [`cenarios.md`](cenarios.md). **Estado: só projeto.** Nenhuma imagem foi gerada, nada foi montado nem filmado; os
> números de posição são o ponto de partida e serão ajustados na prévia do gerador.

A pesquisa dos lugares foi feita no mesmo dia, olhando fotos e mapas públicos no navegador (Wikimedia Commons, Google
Maps e Street View, OpenStreetMap, blog e imprensa local). Foto e mapa são só referência do que existe; nenhuma foto
entrou no repositório. O que não foi visto está dito em cada seção.

## Para o Alisson confirmar

Projetei pela alternativa mais provável em cada caso. Se alguma resposta for outra, muda o desenho antes de gerar.

1. **O Cristo é o do Morro do Silêncio?** O projeto é o Monumento Jesus de Nazaré, de braços abertos e erguidos em "V"
   (não é a pose do Cristo do Rio). O Google Maps lista também um ponto "Cristo Redentor" na região, que não foi aberto.
2. **Como o Cristo está hoje?** As fotos são de 2008-2009 e sem data; as fontes de 2026 falam em abandono. Desenhei
   pedestal azul, terraço branco com faixas azuis e bar aceso embaixo. O que se vê **do mirante** (cidade e rio de que
   lado) não foi visto em foto: o cenário mostra a estátua de frente com a cidade e o rio ao fundo, por licença.
3. **Maria Fumaça: dentro do galpão ou na rua em frente ao arco?** Ela fica dentro da antiga estação (fotos de 2017 e
   2019), atrás de uma grade baixa branca. Projetei dentro do galpão, de perfil. Não sei se ela continua no mesmo ponto
   nem a pintura de hoje (2017: paredes ocre e branco; 2019: creme com pilares verdes e dourado, a que usei).
4. **A locomotiva "viva" pode?** Na vida real ela é peça de museu, apagada. No cenário solta fumaça e vapor, o sino
   balança e o farol acende. Rodas e biela girando no lugar ficaram de fora (máquina parada na grade); se quiser, é mais
   uma folha de 8 quadros.
5. **Praça da prefeitura é o largo em frente à Prefeitura e à Igreja Matriz** (Praça Alexandre Bittencourt)? Se a
   lembrança for de uma praça ajardinada maior ou de um **coreto**, pode ser a Praça José Bitencourt (ao lado do Sobrado
   dos Arcos e da ponte), que não foi pesquisada. Nenhuma foto desta praça mostra coreto.
6. **De que cor está a Prefeitura hoje?** Salmão em 2017, verde-esmeralda com branco em 2019. Usei o verde.
7. **A passarela é a branca coberta que vai para a Ilha das Cobras?** É a única passarela de pedestres no mapa. Se a
   lembrança for da antiga (amarela e azul, baixa, com quiosque no meio, foto de 2016), o desenho muda.
8. **Lutar na beira do rio ou em cima da passarela?** Projetei na calçada da margem do centro, com a passarela saindo
   dali e atravessando o rio. A alternativa é lutar dentro dela, com a treliça branca atrás e o rio pelos vãos.
9. **As horas do dia servem?** Cristo ao entardecer, Maria Fumaça de noite com os globos acesos, praça em manhã de sol,
   passarela ao amanhecer com neblina. Noite na estação e neblina no rio são escolha de cenário: não vi foto assim.
10. **Feira e caxixis:** não pus feira em nenhum cenário, porque não confirmei onde ela acontece (os mercados do mapa
    ficam perto da ponte do centro; a Feira dos Caxixis é da Semana Santa). Se quiser barraca de caxixi, diga em qual.
11. **Texto:** o único texto previsto é "PREFEITURA MUNICIPAL" no frontão, escrito à mão na conversão. A inscrição em
    latim da fachada da estação e as placas da locomotiva ficam de fora.

## 1. Regras comuns aos quatro

- **Malha e chão:** tela lógica 320x180, pés em y = 165, piso começando em y = 138, mundo de 768 px, câmera ±224 e sobe
  40 ([`cenarios.md`](cenarios.md), seções 1 e 2). As posições `x, y` das tabelas são o canto de cima-esquerda na tela
  com a câmera em repouso; x negativo ou maior que 320 fica fora da tela em repouso e aparece quando a câmera anda.
- **Escala do lugar:** monumento, locomotiva e fachada reais são grandes demais para a escala dos lutadores (110 px =
  1,8 m). Cada cenário diz a escala usada (60 a 65%, como se o lugar estivesse alguns metros atrás) e o que identifica o
  lugar fica acima de y = 100 ou no vão x = 120 a 200.
- **Peças, não um painel só:** o ChatGPT entrega no máximo cerca de 1536 px de largura. Uma camada de 768 px pedida de
  uma vez sairia a 2 px por pixel de arte, sem detalhe. Por isso o plano principal é montado com **peças** (o lugar no
  centro, uma peça em cada ponta do mundo) sobre **faixas que se repetem** (piso, cerca, guarda-corpo, módulo do galpão).
  As emendas caem em vão aberto, nunca no meio de um prédio. O céu (delta 0) cobre a tela toda, então não há furo; a
  prévia do gerador mostra se sobrou vão feio.
- **Fator de redução:** cada imagem é pedida com o desenho ocupando uma área de proporção exata; a conversão recorta
  pela cor de fundo, reduz para o tamanho final da tabela (fator de 2,4 a 10), quantiza sem dithering e endurece o alfa.
  Folha de animação: 8 quadros iguais (uma fileira, como as folhas dos lutadores, ou grade 2 x 4 para quadro largo).
- **O que é "código":** luz pequena (halo, farol, janela, brilho na água, reflexo), cata-vento, sino da torre, fio e
  mariposa são desenhados por programa no script de montagem do cenário, como o `ferramentas/cenario_teste.py` faz, em
  camadas de `mistura: "soma"`. Não entram na fila do ChatGPT.
- **Peças comuns:** urubu, garça, pombo, pombos no chão, cachorro e ciclista servem a mais de um cenário
  (`cenarios/comum/`); a cor é ajustada à paleta de cada um na conversão.
- **Pastas:** a imagem bruta do ChatGPT vai em `cenarios/<id>/folhas/<nome>.png` (ainda não existe); a camada convertida
  em `cenarios/<id>/<nome>.png`, ao lado do `cenario.json`.
- **Nada parado além de prédio e chão:** toda tabela de camadas diz, na última coluna, o que cada camada faz. "N
  quadros" é animação desenhada; "velocidade", "seno" e "VelSet" são movimento contínuo no motor; vários usam os dois.

## 2. O Cristo (Monumento Jesus de Nazaré, Morro do Silêncio)

Id do cenário: `cristo`.

### Lugar real

Monumento Jesus de Nazaré, no Morro do Silêncio (Morro da Fazenda Mercantil), R. Otávio Borges, 111, a noroeste do
centro, cerca de 1,3 km do rio (estimativa pelo mapa). Obra de Félix Sampaio, inaugurada por volta de 2000; 15 m de
altura e 9,20 m entre as mãos (blog local e Flickr do artista). **Não é cópia do Cristo do Rio:** os braços ficam abertos
e erguidos em "V" largo, um bem alto com a mão aberta, o outro mais baixo com a palma para cima; cabeça erguida, cabelo
comprido, barba, túnica com manto em diagonal e mangas largas. Branco fosco. Fica sobre um pedestal azul baixo, no
centro de um terraço branco com faixas azuis (laje de um pavilhão térreo com bar), com escadaria reta central e
guarda-corpo. Em volta: pasto verde-claro, grupo de árvores de copa redonda, uma palmeira, cerca de mourões, três ou
quatro torres de telecomunicação vermelhas e brancas na mesma crista. Ao longe, mar de morros do Recôncavo e, embaixo, a
cidade de telhado laranja com o rio Jaguaripe e ponte.

Fontes:

- https://atarde.com.br/colunistas/levivasconcelos/nazare-das-farinhas-quer-o-jesus-de-nazare-o-natal-1373684
- https://nazarebahia.blogspot.com/2008/01/monumento-jesus-de-nazar.html
- https://www.flickr.com/photos/felixsampaio/3886947855
- https://commons.wikimedia.org/wiki/File:Cristo_de_Nazar%C3%A9_das_Farinhas.jpg
- https://commons.wikimedia.org/wiki/File:Vista_do_Centro_de_Nazar%C3%A9_das_Farinhas.jpg
- https://pt.wikipedia.org/wiki/Nazaré_(Bahia)
- https://www.bahiaterra.com/posts/nazare-das-farinhas-bahia
- Google Maps, "Monumento Jesus De Nazaré" (-13.0227968, -39.0187859); OpenStreetMap na mesma coordenada

### Hora do dia e paleta

**Entardecer, do dourado ao rosado.** É o que a pesquisa justifica: uma avaliação do lugar fala em "espetacular pôr do
sol", o branco da estátua pega ouro de um lado e sombra azul-arroxeada do outro, e é a hora que dá mais luz para animar
(bar, cidade, torres). Paleta: céu em faixas âmbar `#F2A65A`, salmão `#E8746A`, rosa-roxo `#9C5A8C`, violeta `#4A3A78`;
estátua creme `#F6EBD2` com luz ouro `#F7C873` e sombra lilás `#8E86B8`; pedestal e faixas azul `#3A62B0`; pasto
verde-oliva `#7E9A4A` com sombra `#3F5A46`; morros distantes azul-violeta `#5B6A9A`; telhados laranja queimado `#C8623A`;
luzes amarelo quente `#FFD070` e vermelho de torre `#FF4A3A`.

### Composição, do fundo para a frente

O conjunto tem uns 20 m de altura; na escala dos lutadores (110 px = 1,8 m) daria mais de 1000 px. Por isso o monumento
fica **no plano médio** (delta 0,7), num topo de morro uns 60 m atrás, com a estátua de 72 px e gente de 8 px ao pé. Os
lutadores pisam num platô de calçada clara e grama na chegada da subida, com a cerca de mourões atrás. A estátua aparece
de frente e a cidade ao fundo, dos dois lados do morro: é licença de cenário (ver "Para o Alisson confirmar").

| # | Camada | Origem | Delta | Tamanho final (px) | Posição | Movimento |
|---|---|---|---|---|---|---|
| 1 | Céu | `ceu.png` | 0 | 320x180 | 0, 0 | parado (faixas do pôr do sol) |
| 2 | Sol e halo | código | 0 | 48x48 | x 36, y 86 | halo somado que pulsa (8 quadros por código, 8 ticks) |
| 3 | Nuvens longe | `nuvens_longe.png` | 0,05 | 384x36 repetida | y 62 | anda −0,03 px/tick |
| 4 | Nuvens perto | `nuvens_perto.png` | 0,15 | 384x52 repetida | y 14 | anda −0,09 px/tick |
| 5 | Longe: morros, cidade, rio | `longe.png` | 0,35 | 478x104 | y 58 (base em 162) | parado |
| 6 | Brilho do rio | código | 0,35 | ~90x16 | sobre o rio do `longe` | 8 quadros somados, 8 ticks |
| 7 | Luzes da cidade | código | 0,35 | ~200x40 | sobre o casario do `longe` | 16 quadros somados, 12 ticks: acendem aos poucos e piscam |
| 8 | Urubus (3) | `comum/urubu.png` | 0,3 | 32x24 cada | y 30 a 70 | 8 quadros, 6 ticks + seno_x [40, 420] e seno_y [10, 210] (planam em círculo), fases diferentes |
| 9 | Morro do monumento | `morro.png` | 0,7 | 634x64 | y 96 (base em 160) | parado |
| 10 | Torres de telecomunicação | `torres.png` | 0,7 | 72x112 | x 214, y 16 | paradas; farol por código |
| 11 | Farol das torres | código | 0,7 | 3x3 em cada topo | topo das torres | pisca: 2 quadros somados (40 ticks aceso, 20 apagado), fora de fase |
| 12 | Copas no morro | `arvores_morro.png` | 0,7 | 96x56 por quadro | x 40, y 74 | 8 quadros, 7 ticks (vento) |
| 13 | O Cristo (estátua, pedestal, terraço, escada) | `cristo.png` | 0,7 | 150x108 | x 85, y 22 (base em 130) | parado; holofote por código |
| 14 | Holofote e luzes do bar | código | 0,7 | 150x108 | sobre o `cristo` | 8 quadros somados, 6 ticks: vãos do bar oscilam, luz de baixo na túnica respira |
| 15 | Visitantes no terraço e na escada | `visitantes.png` | 0,7 | 128x20 por quadro | x 96, y 100 | 8 quadros, 10 ticks (4 poses ida e volta) |
| 16 | Cerca de mourões | `cerca.png` | 1 | 128x26 repetida | y 116 (base em 142) | parada |
| 17 | Palmeira (ponta esquerda do mundo) | `palmeira.png` | 1 | 96x144 por quadro | x −200, y −2 | 8 quadros, 6 ticks |
| 18 | Árvore de copa redonda (ponta direita) | `arvore.png` | 1 | 128x128 por quadro | x 410, y 14 | 8 quadros, 7 ticks |
| 19 | Chão: grama e calçada clara | `chao.png` | 1 | 256x54 repetida | y 138 | parado |
| 20 | Capim da frente | `capim.png` | 1,25 (frente) | 64x14 por quadro, repetido com vão de 40 | y 168 | 8 quadros, 6 ticks |

### O que se mexe (11)

1. Nuvens em duas profundidades (motor: velocidades −0,03 e −0,09 px/tick).
2. Halo do sol pulsando (código, 8 quadros somados).
3. Brilho ondulando no rio lá embaixo (código, 8 quadros somados).
4. Luzes da cidade acendendo aos poucos e piscando (código, 16 quadros somados).
5. Três urubus planando em círculo (8 quadros de asa + seno em x e y no motor).
6. Farol vermelho piscando no topo das torres (código, 2 quadros com tempos diferentes).
7. Luzes do bar sob a laje e holofote na estátua respirando (código, 8 quadros somados).
8. Copas das árvores do morro ao vento (8 quadros).
9. Visitantes genéricos no guarda-corpo e na escada (8 quadros: acenam, sobem um degrau, apontam).
10. Palmeira e árvore de copa redonda nas pontas do mundo (8 quadros cada).
11. Capim da frente ondulando, rente ao chão (8 quadros, faixa repetida).

## 3. A Maria Fumaça (Locomotiva Visconde de São Lourenço, antiga Estação Alexandre Bittencourt)

Id do cenário: `maria_fumaca`.

### Lugar real

A "Maria Fumaça" é a Locomotiva Visconde de São Lourenço, nº 1 da antiga Estrada de Ferro de Nazaré (1873, rodagem
0-6-0). Fica **dentro** da antiga Estação Ferroviária Alexandre Bittencourt, hoje Centro Cultural e Artesanal, na Rua
Barão Homem de Melo, margem norte do Jaguaripe (-13.03346, -39.01127). A máquina é pequena e verde, com filetes
amarelos, **chaminé preta enorme em funil** com duas cintas de latão, farol de caixa verde, domo com cinta dourada, sino
de bronze, cabine de teto curvo com janelas ovais, sobre um trecho curto de trilho, atrás de uma grade baixa branca. O
galpão é a antiga plataforma coberta: telhado de duas águas com telha vista por baixo e madeiramento escuro, lustres de
ferro com globos brancos, pilares quadrados, painéis de veneziana escura e faixa de vidro em cima, portas e janelas de
arco ogival embaixo, piso de paralelepípedo, bancos de ripa e mesas de bar. Numa foto de 2017 há bandeirinhas amarelas
nos pilares. O rio fica a poucas dezenas de metros (só o mapa garante; nenhuma foto mostra os dois juntos).

Fontes:

- https://commons.wikimedia.org/wiki/Category:Locomotiva_Visconde_de_São_Lourenço
- https://commons.wikimedia.org/wiki/Category:Estação_Ferroviária_Alexandre_Bittencourt
- https://pt.wikipedia.org/wiki/Estação_Ferroviária_Alexandre_Bittencourt
- https://pt.wikipedia.org/wiki/Estrada_de_Ferro_de_Nazaré
- https://internationalsteam.co.uk/trains/brazil34.htm
- https://www.openstreetmap.org/#map=18/-13.03340/-39.01120

### Hora do dia e paleta

**Noite, com os globos acesos.** A pesquisa sugeria fim de tarde, mas o entardecer já é do Cristo; o galpão é escuro por
dentro e cheio de globos de vidro, então a noite é a hora em que ele mais se separa dos outros três e em que a luz vira
movimento (globos, farol, vapor iluminado). É escolha de cenário, não foto: nenhuma imagem noturna do lugar foi vista.
Paleta: madeira e sombra marrom-vinho `#3A2630` e `#5A3A34`; telha por baixo `#8A4A34`; paredes creme `#D8C49A` com
sombra `#7A6A78`; pilares verde-esmeralda `#2F8A6A` (pintura de 2019); locomotiva verde `#2E7A46` com luz `#6FB85A`,
filete amarelo `#E8C84A`, latão `#D8A038`, chaminé `#2A2430`; globos `#FFF2C0` com halo âmbar `#FFB850`; noite lá fora
azul-cobalto `#1E2C5A`, lua `#DDE6F2`; piso cinza-azulado `#5A6072` com poças de luz âmbar.

### Composição, do fundo para a frente

A locomotiva real tem uns 2,5 a 3 m de altura (estimativa de olho); na escala dos lutadores daria 170 px e taparia a
tela. Fica a **65%** (96 px de altura, 200 de comprimento), como se estivesse alguns metros atrás, de perfil, virada
para a esquerda, com a chaminé-funil entre x = 96 e x = 128 e o topo em y = 44. Perfil completo, rodas e bielas não foram
vistos em foto: o desenho completa com uma 0-6-0 de tanque genérica da época. A parede do galpão é um **módulo de 128 px
que se repete** (pilar + vão ogival aberto + veneziana + vidro + tesoura do telhado): assim não há emenda entre imagens.
Os vãos ogivais ficam abertos para a noite lá fora (rua, árvores, rio com a lua): o rio visto dali é licença.

| # | Camada | Origem | Delta | Tamanho final (px) | Posição | Movimento |
|---|---|---|---|---|---|---|
| 1 | Céu da noite | `ceu.png` | 0 | 320x180 | 0, 0 | parado (aparece pelos vãos) |
| 2 | Nuvens da noite | `nuvens.png` | 0,1 | 384x40 repetida | y 62 | anda −0,05 px/tick |
| 3 | Longe: outra margem e rio com a lua | `longe.png` | 0,35 | 478x96 | y 66 (base em 162) | parado |
| 4 | Reflexo da lua no rio | código | 0,35 | ~60x20 | sobre o rio do `longe` | 8 quadros somados, 8 ticks |
| 5 | Árvores da rua | `arvores_rua.png` | 0,7 | 128x84 por quadro, repetida com vão de 64 | y 58 (base em 142) | 8 quadros, 7 ticks |
| 6 | Galpão: módulo da parede e do telhado | `vao_galpao.png` | 1 | 128x182 repetido | y −40 (base em 142) | parado |
| 7 | Arandelas dos pilares | código | 1 | halo 24x24 em cada pilar | y 70 | 6 quadros somados, 9 ticks, fases diferentes |
| 8 | Locomotiva, trilho e grade branca | `locomotiva.png` | 1 | 200x96 | x 70, y 44 (base em 140) | parada |
| 9 | Farol e brilho do latão | código | 1 | sobre a `locomotiva` | farol em x ~92, y ~70 | farol pulsa (8 quadros somados, 6 ticks); brilho corre pelas cintas (12 quadros, 5 ticks, com pausa) |
| 10 | Fumaça da chaminé | `fumaca.png` | 1 | 96x64 por quadro | x 96, y −18 | 8 quadros, 6 ticks (sobe e deriva para a direita, sob o telhado) |
| 11 | Vapor nas rodas | `vapor.png` | 1 | 96x28 por quadro | x 70, y 112 | 8 quadros, 6 ticks |
| 12 | Sino de bronze | `sino.png` | 1 | 20x20 por quadro | x 134, y 52 | 8 quadros, 5 ticks (balança) |
| 13 | Bandeirolas amarelas | `bandeirolas.png` | 1 | 128x20 por quadro, repetida | y 48 | 8 quadros, 5 ticks |
| 14 | Lustres de globo (5) | `lustre.png` | 1 | 20x60 cada | y −16, a cada 150 px do mundo | seno_x [1,5; 180] com fases diferentes; halo por código que respira |
| 15 | Mariposas nos globos | código | 1 | pontos de 1 px | em volta de cada globo | seno_x e seno_y curtos, períodos diferentes |
| 16 | Pombos na viga | `comum/pombos_chao.png` | 1 | 64x12 por quadro | x 180, y 16 | 8 quadros, 8 ticks |
| 17 | Plateia no banco (ponta esquerda) | `plateia_banco.png` | 1 | 112x76 por quadro | x −190, y 66 | 8 quadros, 6 ticks (4 poses ida e volta) |
| 18 | Mesa de bar (ponta direita) | `mesa_bar.png` | 1 | 112x76 por quadro | x 400, y 66 | 8 quadros, 7 ticks |
| 19 | Cachorro deitado | `comum/cachorro.png` | 1 | 48x28 por quadro | x −70, y 114 | 8 quadros, 8 ticks |
| 20 | Chão de paralelepípedo | `chao.png` | 1 | 256x54 repetida | y 138 | parado; `reflexo` fraco do motor (piso úmido) |

### O que se mexe (11)

1. Nuvens da noite passando nos vãos (motor, −0,05 px/tick).
2. Reflexo da lua tremendo no rio ao longe (código, 8 quadros somados).
3. Copas das árvores da rua, vistas pelos vãos (8 quadros).
4. Fumaça saindo da chaminé-funil e derivando sob o telhado (8 quadros). Licença: a máquina real é apagada.
5. Vapor baixo junto às rodas (8 quadros).
6. Sino de bronze balançando (8 quadros).
7. Farol pulsando e brilho correndo nas cintas de latão (código).
8. Bandeirolas amarelas tremulando entre os pilares (8 quadros, repetidas).
9. Cinco lustres balançando de leve (seno no motor), com halo que respira e mariposas em volta (código).
10. Arandelas dos pilares oscilando (código).
11. Pombos na viga, plateia genérica no banco, gente na mesa de bar e cachorro abanando o rabo (8 quadros cada).

## 4. A praça da prefeitura (Praça Alexandre Bittencourt, Prefeitura Municipal e Igreja Matriz)

Id do cenário: `praca`.

### Lugar real

Praça Alexandre Bittencourt (a grafia varia: Bittencourt/Bitencourt), no centro histórico, a uns 100 m do rio, em frente
à Prefeitura Municipal (-13.03339, -39.00929). A prefeitura é um sobrado neoclássico de 2 pavimentos, largo e baixo
(fachada 2,5 a 3 vezes a altura), sobre embasamento de 1 m, simétrico, com 11 vãos por andar (contados em miniatura, erro
de ±1) e corpo central de 3 vãos. Em 2017 era salmão; em 2019, **verde-esmeralda com molduras brancas**. Portas-janela
altas com venezianas creme e sacadas de ferro dourado; platibanda de balaústres; frontão triangular baixo com o letreiro
do nome público e um brasão redondo; pináculos dourados e, em cada ponta, uma escultura dourada de animal alado; três
mastros com bandeiras (Bahia, Brasil, município); escadaria central de granito com 8 ou 9 degraus e dois lampiões de
bronze; antena de TV no telhado. A praça é um largo pequeno e seco: piso de blocos cinza-claro com faixas rosadas,
meio-fio azul-royal e branco, canteiros de mureta azul-royal com palmeiras pequenas e buganvília, um busto de bronze em
pedestal claro (homenageado não identificado), postes brancos altos. À direita de quem olha a prefeitura fica a Igreja
Matriz de N. Sra. de Nazaré (paredão creme muito alto, torres com coruchéu bulboso, relógio, sino à vista, cata-vento); à
esquerda, uma casa térrea azul. Em volta, casario comercial colorido de 2 pavimentos; ao longe, morros verdes com
palmeiras na crista. **Não há coreto em nenhuma foto** e o rio não aparece do chão da praça.

Fontes:

- https://commons.wikimedia.org/wiki/Category:Prefeitura_Municipal_(Nazaré,_Bahia)
- https://commons.wikimedia.org/wiki/File:Prefeitura_Municipal_Nazaré_2019-0890.jpg
- https://commons.wikimedia.org/wiki/File:Praça_Alexandre_Bittencourt_10_Nazaré_9022.jpg
- https://commons.wikimedia.org/wiki/Category:Igreja_Matriz_de_Nossa_Senhora_de_Nazaré
- https://commons.wikimedia.org/wiki/File:Vista_do_Centro_de_Nazaré_das_Farinhas.jpg
- https://www.openstreetmap.org/#map=19/-13.03325/-39.00930
- https://www.bahiaterra.com/posts/nazare-das-farinhas-bahia
- https://pt.wikipedia.org/wiki/Nazaré_(Bahia)

### Hora do dia e paleta

**Manhã de sol, céu azul forte com cúmulos brancos, praça em movimento.** É a cara das fotos de 2017 (a mais fiel ao que
foi fotografado) e a única das quatro em dia claro. A pesquisa preferia fim de tarde, que ficou com o Cristo. Não é
"dia de feira": a feira e a Feira dos Caxixis não foram confirmadas nesta praça; o movimento vem de um ambulante com
carrinho de mão e guarda-sol, ciclista e gente na mureta, que foram vistos nas fotos. Paleta: céu `#3F8FE0` a `#9CCBF2`,
nuvens `#FFFFFF` com sombra `#B8C8E8`; prefeitura verde-esmeralda `#2FA57A` com sombra `#1F6F6A`, molduras `#F4F0E0`,
dourado `#E0B040`, venezianas creme `#E6D6A8`; mureta e meio-fio azul-royal `#2A4FC0`; piso `#C8C4C0` com faixas
`#D89A8A`; buganvília `#D8408A`; igreja palha `#E8D8A0` com mancha `#B8A888`; telha `#C8623A`; morros `#4E8A4A`.

### Composição, do fundo para a frente

A fachada real tem perto de 30 m; desenhada a **352 px de largura por 122 de altura** (cerca de 60% da escala dos
lutadores), cabe quase inteira na tela e mostra frontão, bandeiras e escadaria acima da cabeça dos lutadores. O corpo
central com as três bandeiras fica no vão x = 120 a 200. A igreja entra no plano médio (delta 0,7), à direita, com uma
torre só: do largo se vê a lateral, e o cenário "abre" o ângulo para mostrar a torre (licença). O letreiro do frontão
fica em branco na arte e é escrito à mão na conversão ("PREFEITURA MUNICIPAL", nome público do lugar), porque o ChatGPT
erra letra nesse tamanho.

| # | Camada | Origem | Delta | Tamanho final (px) | Posição | Movimento |
|---|---|---|---|---|---|---|
| 1 | Céu | `ceu.png` | 0 | 320x180 | 0, 0 | parado |
| 2 | Nuvens longe | `nuvens_longe.png` | 0,05 | 384x40 repetida | y 58 | anda −0,03 px/tick |
| 3 | Nuvens perto (cúmulos grandes) | `nuvens_perto.png` | 0,15 | 384x60 repetida | y 6 | anda −0,08 px/tick |
| 4 | Longe: morros verdes com palmeiras | `longe.png` | 0,35 | 478x90 | y 72 (base em 162) | parado |
| 5 | Urubus (2) | `comum/urubu.png` | 0,3 | 32x24 cada | y 40 a 66 | 8 quadros, 6 ticks + seno_x [50, 480] e seno_y [8, 240] |
| 6 | Meio: casario colorido e Igreja Matriz com uma torre | `casario.png` | 0,7 | 634x142 | y 10 (base em 152) | parado |
| 7 | Cata-vento, sino e fios | código | 0,7 | pequenos | topo e sineira da torre; fios entre os postes | cata-vento gira (4 quadros, 10 ticks); sino badala (6 quadros, 6 ticks); fio balança (3 quadros, 14 ticks) |
| 8 | Pombos voando (3) | `comum/pombo.png` | 0,8 | 24x20 cada | y 20 a 50 | 8 quadros, 4 ticks + velocidade 0,6 a 0,9 px/tick, repetidos com vão de 700 a 1100, seno_y [5, 90] |
| 9 | Prefeitura | `prefeitura.png` | 1 | 352x122 | x −16, y 20 (base em 142) | parada |
| 10 | Três bandeiras nos mastros | `bandeiras.png` | 1 | 96x56 por quadro | x 112, y 50 | 8 quadros, 5 ticks |
| 11 | Casa térrea azul e poste (ponta esquerda) | `lado_esq.png` | 1 | 176x100 | x −224, y 42 | parada |
| 12 | Ladeira, adro e gradil da igreja (ponta direita) | `lado_dir.png` | 1 | 176x130 | x 368, y 12 | parada |
| 13 | Canteiros com palmeira e buganvília (2) | `canteiro.png` | 1 | 80x100 por quadro | x −30 e x 270, y 42 | 8 quadros, 6 ticks, o segundo começa 4 quadros depois |
| 14 | Ambulante com carrinho e guarda-sol | `ambulante.png` | 1 | 88x88 por quadro | x −150, y 54 | 8 quadros, 7 ticks |
| 15 | Torcida sentada na mureta | `torcida_mureta.png` | 1 | 128x64 por quadro | x 372, y 78 | 8 quadros, 6 ticks |
| 16 | Ciclista passando atrás | `comum/ciclista.png` | 1 | 72x72 por quadro | y 72 (rodas em 144) | 8 quadros, 4 ticks + velocidade 0,9 px/tick, repetido com vão de 900 (passa a cada ~18 s) |
| 17 | Cachorro | `comum/cachorro.png` | 1 | 48x28 por quadro | x 290, y 114 | 8 quadros, 8 ticks |
| 18 | Chão: blocos cinza com faixas rosadas e meio-fio azul | `chao.png` | 1 | 256x54 repetida | y 138 | parado |
| 19 | Pombos ciscando na frente | `comum/pombos_chao.png` | 1,25 (frente) | 64x12 por quadro | x 30 e x 250, y 170 | 8 quadros, 8 ticks |

### O que se mexe (10)

1. Nuvens em duas profundidades, cúmulos grandes na frente (motor).
2. Dois urubus planando sobre os morros (8 quadros + seno).
3. Cata-vento girando e sino badalando na torre da Matriz; fios balançando (código).
4. Pombos cruzando o céu da praça (8 quadros + velocidade e seno).
5. As três bandeiras da fachada tremulando, bem no centro (8 quadros). É o melhor elemento animado do lugar.
6. Palmeiras pequenas e buganvília dos canteiros ao vento (8 quadros, duas cópias fora de fase).
7. Ambulante genérico com carrinho de mão de fruta amarela: abana o chapéu, o guarda-sol balança (8 quadros).
8. Gente sentada na mureta azul torcendo (8 quadros).
9. Ciclista com sacola passando atrás dos lutadores de tempos em tempos (8 quadros + velocidade).
10. Cachorro abanando o rabo e pombos ciscando rente ao chão, na frente (8 quadros cada).

## 5. A passarela (passarela de pedestres sobre o rio Jaguaripe, para a Ilha das Cobras)

Id do cenário: `passarela`.

### Lugar real

Passarela de pedestres sobre o rio Jaguaripe (-13.03394, -39.00425), a única ponte de pedestres mapeada na cidade, uns
550 m rio abaixo da praça da Prefeitura. Liga a beira-rio do centro (Av. Eurico Mata no Google, Rua Conselheiro Dantas
no OSM) à Praça da Ilha das Cobras. A atual (montada em fev-mar/2021, vista pronta no Street View de dez/2024) é de
**treliça metálica branca tipo Warren, coberta**, baixa sobre a água (2 a 3 m), em 2 ou 3 módulos retos sobre pilar de
concreto, com uns 60 a 70 m (estimativa pelo mapa); a entrada norte é uma escada de concreto de poucos degraus com
corrimão branco. A de antes (foto de out/2016) era baixa, amarela e azul, com um quiosque no meio. Na margem norte:
calçadão de concreto claro com **ciclofaixa vermelha** de bordas brancas, guarda-corpo cinza-escuro de barras verticais
sobre mureta, postes ornamentais escuros de lampião duplo, muro de cais manchado de limo. Na margem sul: casas e
sobrados de 1 a 2 andares de telha laranja, árvores de copa redonda podada, coqueiros, canoas de madeira coloridas
atracadas. O rio é largo, de água escura verde-acastanhada e calma, com manchas de baronesa. Ao fundo, morros baixos
verdes e uma chaminé alta de tijolo.

Fontes:

- https://www.openstreetmap.org/way/682335015
- Google Maps satélite e Street View de dez/2024 na cabeceira norte (-13.03370, -39.00428)
- https://pulsarimagens.com.br/foto/Ponte-de-pedestres-sobre-o-Rio-Jaguaripe----------------------------------------------?codigo=316770&codigo-imagem=27RC875 (passarela antiga, out/2016)
- https://www.youtube.com/watch?v=WiGeFnQui84 ("Nova passarela, Nazaré Bahia", fev/2021; só quadros estáticos vistos)
- https://www.youtube.com/watch?v=SoT04If66I8 (cobertura da passarela, mar/2021; só quadros estáticos vistos)

### Hora do dia e paleta

**Amanhecer com neblina sobre o rio.** A câmera fica na margem norte olhando o sul; o rio corre para leste, então o sol
nasce rio abaixo, à esquerda do quadro. A pesquisa recomendava fim de tarde, mas a água parada do estuário é o lugar
certo para a neblina e para o reflexo comprido do sol, e é a hora mais diferente das outras três. É escolha de cenário:
**nenhuma imagem de amanhecer ou de neblina no lugar foi vista.** Paleta fria com um ponto quente: céu do pêssego
`#F2C8A0` ao lilás-acinzentado `#8A8AB0` e azul-petróleo `#3F5F7A`; sol e reflexo `#FFD9A0`; neblina `#D8E0E8`; água
`#3E5A52` com brilho `#7FA08A`; treliça branca `#E8ECEC` com sombra azul `#8A9AB8`; ciclofaixa vermelho-tijolo
`#B8483A`; calçadão `#B0AEB0`; guarda-corpo `#3A3F4A`; telhados `#B86A4A`; morros `#4A6A6A`; lampião aceso `#FFC860`.

### Composição, do fundo para a frente

A passarela sai da calçada e atravessa o rio **para longe da câmera**: de lado puro ela não aparece. O desenho usa uma
vista de três quartos: a cabeceira (escada, corrimão branco, pórtico da treliça com a cobertura) fica no chão de luta,
entre x = 205 e x = 305, e o corpo recua em diagonal para a esquerda e para o fundo até a outra margem, mostrando a
lateral em zigue-zague e a faixa da cobertura. A cabeceira fica a **60% da escala dos lutadores** (pórtico de 100 px).
Corpo e cabeceira andam com o chão (delta 1) para não descolarem um do outro; o corpo é desenhado antes do guarda-corpo
e a cabeceira depois, para a grade passar na frente do rio mas não na frente da escada. Alternativa registrada em "Para
o Alisson confirmar": lutar em cima do tabuleiro.

| # | Camada | Origem | Delta | Tamanho final (px) | Posição | Movimento |
|---|---|---|---|---|---|---|
| 1 | Céu do amanhecer | `ceu.png` | 0 | 320x180 | 0, 0 | parado |
| 2 | Sol baixo e halo | código | 0 | 56x56 | x 20, y 52 | halo somado que cresce e encolhe (8 quadros, 10 ticks) |
| 3 | Nuvens finas | `nuvens.png` | 0,05 | 384x30 repetida | y 40 | anda −0,02 px/tick |
| 4 | Longe: morros, casario na encosta, chaminé de tijolo | `longe.png` | 0,35 | 478x76 | y 48 (base em 124) | parado |
| 5 | Garça voando | `comum/garca.png` | 0,6 | 40x32 por quadro | y 56 | 8 quadros, 5 ticks + velocidade −0,5 px/tick, repetida com vão de 1100, seno_y [6, 200] |
| 6 | Margem sul: casas, árvores podadas, canoas | `margem_sul.png` | 0,5 | 544x56 | y 66 (base em 122) | parada |
| 7 | Janelas da margem sul | código | 0,5 | pontos 2x2 | sobre a `margem_sul` | 16 quadros somados, 20 ticks: apagam uma a uma com o dia |
| 8 | Coqueiros da margem sul (2) | `coqueiros.png` | 0,5 | 56x56 por quadro | x 30 e x 250, y 44 | 8 quadros, 7 ticks, fora de fase |
| 9 | Água do rio | `agua.png` | 0,7 | 256x56 por quadro, repetida | y 98 (base em 154) | 8 quadros, 8 ticks |
| 10 | Reflexo do sol na água | código | 0,7 | 24x50 | x 26, y 100 | 8 quadros somados, 6 ticks (coluna de brilhos que tremem) |
| 11 | Neblina longe | `neblina.png` | 0,55 | 384x28 repetida | y 92 | soma; anda +0,04 px/tick |
| 12 | Canoa a remo passando | `canoa_remo.png` | 0,75 | 72x36 por quadro | y 100 | 8 quadros, 7 ticks + velocidade 0,25 px/tick, repetida com vão de 700 |
| 13 | Baronesas descendo o rio | `baronesa.png` | 0,8 | 40x10, repetida com vão de 260 | y 122 | velocidade −0,06 px/tick + seno_y [1, 180] |
| 14 | Neblina perto | `neblina.png` | 0,85 | 384x28 repetida | y 112 | soma; anda −0,07 px/tick + seno_y [1,5; 300] |
| 15 | Canoas atracadas (2) | `canoas_atracadas.png` | 0,9 | 96x28 | x 20 e x 380, y 114 | seno_y [1, 160] com fases diferentes (balançam na água) |
| 16 | Passarela: corpo sobre o rio e pilares | `passarela.png` | 1 | 230x100 | x 0, y 24 (base em 124) | parada |
| 17 | Pedestres atravessando | `pedestres.png` | 1 | 40x24 por quadro | sobre o tabuleiro do corpo | 8 quadros, 6 ticks + dois VelSet (6 s indo, 6 s voltando, velocidade em diagonal) |
| 18 | Guarda-corpo do calçadão | `guarda_corpo.png` | 1 | 128x46 repetida | y 96 (base em 142) | parado |
| 19 | Cabeceira: escada, corrimão e pórtico | `cabeceira.png` | 1 | 100x124 | x 205, y 18 (base em 142) | parada |
| 20 | Lampiões duplos (2) | `lampiao.png` | 1 | 28x104 cada | x −140 e x 440, y 38 | parados; halo por código (6 quadros somados, 9 ticks: falham e apagam com o dia) |
| 21 | Pescador de linha no guarda-corpo | `pescador.png` | 1 | 56x92 por quadro | x −60, y 50 | 8 quadros, 8 ticks |
| 22 | Ciclista na ciclofaixa | `comum/ciclista.png` | 1 | 72x72 por quadro | y 74 (rodas em 146) | 8 quadros, 4 ticks + velocidade −0,9 px/tick, repetido com vão de 1000 |
| 23 | Cachorro | `comum/cachorro.png` | 1 | 48x28 por quadro | x 330, y 114 | 8 quadros, 8 ticks |
| 24 | Chão: calçadão claro e ciclofaixa vermelha | `chao.png` | 1 | 256x54 repetida | y 138 | parado |
| 25 | Neblina rasteira da frente | `neblina.png` | 1,25 (frente) | 384x28 repetida | y 166 | soma; anda +0,1 px/tick |

### O que se mexe (11)

1. Halo do sol nascendo e coluna de reflexo tremendo na água (código, somados).
2. Nuvens finas (motor) e garça cruzando o rio (8 quadros + velocidade e seno).
3. Água do rio em 8 quadros, faixa repetida: ondulação lenta com o reflexo das casas.
4. Três faixas de neblina em profundidades e sentidos diferentes (motor, somadas), uma delas na frente rente ao chão.
5. Canoa a remo cruzando por trás da passarela (8 quadros + velocidade) e canoas atracadas balançando (seno).
6. Baronesas descendo o rio devagar (velocidade + seno).
7. Coqueiros da outra margem (8 quadros) e janelas apagando com o dia (código).
8. Pedestres genéricos atravessando a passarela, ida e volta (8 quadros + VelSet).
9. Lampiões duplos falhando e apagando (código).
10. Pescador genérico de linha no guarda-corpo (8 quadros). Plausível, não visto em foto.
11. Ciclista na ciclofaixa vermelha e cachorro (8 quadros cada).

## 6. Fila de arte

**64 imagens:** 14 de `cristo`, 14 de `maria_fumaca`, 13 de `praca`, 17 de `passarela` e 6 comuns. Nada foi gerado ainda.

### Como usar

1. **Um chat por cenário**, com o título indicado, mais um chat para as peças comuns. Uma imagem por mensagem.
2. Em toda mensagem, anexe `sprites/pengaro/quadros/folhas_arcade/soco.png` (referência de estilo: tamanho do pixel,
   contorno, sombra) e cole o prompt inteiro. Depois que a peça do lugar for aprovada, anexe-a também nas outras peças do
   mesmo cenário, para a luz e a paleta baterem.
3. Salve a imagem exatamente no caminho do título (`cenarios/<id>/folhas/<nome>.png`). Nada fica em Downloads.
4. **Ordem:** primeiro o lote piloto, que são as **quatro primeiras imagens de cada cenário** (céu, piso, o lugar e a
   peça seguinte). Converta, monte e filme **um** cenário inteiro com o piloto (sugestão: a praça, que é o mais simples)
   antes de pedir o resto: se o estilo ou a redução não convencerem, o resto não vale a pena.
5. Critério de aceite de cada imagem: fundo liso da cor pedida, sem sombra nem brilho no fundo; nada de texto, logo ou
   lutador; vista reta; linha de base reta; nas folhas, 8 quadros inteiros do mesmo tamanho, com a base no mesmo lugar;
   nas faixas que repetem, as duas bordas iguais (a emenda é retocada à mão se sobrar degrau). Reprovou: gere de novo no
   mesmo chat.
6. A coluna "pedir" diz o tamanho da imagem e a área do desenho. Se o ChatGPT devolver outro tamanho, vale a
   **proporção** da área desenhada: a conversão recorta pela cor de fundo.

### Contagem e ordem

| Chat | Imagens, na ordem |
|---|---|
| Cenário Cristo — arcade | `ceu`, `chao`, `cristo`, `morro`, `torres`, `longe`, `nuvens_longe`, `nuvens_perto`, `cerca`, `arvores_morro`, `visitantes`, `palmeira`, `arvore`, `capim` |
| Cenário Maria Fumaça — arcade | `ceu`, `chao`, `locomotiva`, `vao_galpao`, `longe`, `nuvens`, `lustre`, `fumaca`, `vapor`, `sino`, `bandeirolas`, `arvores_rua`, `plateia_banco`, `mesa_bar` |
| Cenário Praça — arcade | `ceu`, `chao`, `prefeitura`, `casario`, `longe`, `nuvens_longe`, `nuvens_perto`, `lado_esq`, `lado_dir`, `bandeiras`, `canteiro`, `ambulante`, `torcida_mureta` |
| Cenário Passarela — arcade | `ceu`, `chao`, `cabeceira`, `passarela`, `guarda_corpo`, `margem_sul`, `longe`, `nuvens`, `neblina`, `canoas_atracadas`, `baronesa`, `lampiao`, `agua`, `coqueiros`, `canoa_remo`, `pedestres`, `pescador` |
| Cenários — peças comuns | `urubu`, `garca`, `pombo`, `pombos_chao`, `cachorro`, `ciclista` |

### Chat "Cenário Cristo — arcade"

#### 1. `cenarios/cristo/folhas/ceu.png`

Céu do pôr do sol, sem transparência.
Tamanho final: **320x180**. Pedir: 1536x1024, pintada inteira; usa-se o miolo 16:9. Fundo: sem transparência.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background layer for a 2D fighting game stage. A sunset sky only, for a fighting game stage: horizontal flat
color bands, from deep violet at the top, through rose-purple and salmon, to bright amber at the bottom third. No sun
disc, no clouds, no land, no horizon line, no objects at all. 5 to 7 flat bands with hard, slightly wavy pixel edges
between them, no smooth gradient.
Format: 1536x1024 image, fully painted edge to edge, no magenta, no transparency. Only the central 16:9 area will be
used, so keep the bands running straight across the full width.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: golden-hour sunset coming from the left. Warm gold/orange light on left-facing surfaces, cool violet-blue
shadows on the right side. Dusk palette: amber, salmon, rose-violet; nothing is lit by white noon light.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 2. `cenarios/cristo/folhas/chao.png`

Piso de luta (repete na horizontal): borda de grama em cima, calçada de pedra clara embaixo.
Tamanho final: **256x54**. Pedir: 1536x1024, desenho em 1536x324 no centro (6.0x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A seamless horizontally tiling ground strip, strict side view:
the top fifth is a low lip of short olive-green grass with a slightly irregular top edge; below it a flat pale cream
stone pavement (large worn slabs seen edge-on, a few cracks, warm sunset tint, violet shadows in the joints) down to
the bottom. The left and right edges must match so the strip can repeat forever: same colors and same slab joints at
both edges. No objects, no plants taller than the grass lip.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x324 px (aspect 256:54), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: golden-hour sunset coming from the left. Warm gold/orange light on left-facing surfaces, cool violet-blue
shadows on the right side. Dusk palette: amber, salmon, rose-violet; nothing is lit by white noon light.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 3. `cenarios/cristo/folhas/cristo.png`

O monumento: estátua, pedestal azul, terraço branco e azul com bar embaixo, escadaria central. É o desenho que identifica o lugar.
Tamanho final: **150x108**. Pedir: 1536x1024, desenho em 1422x1024 no centro (9.5x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A hilltop monument seen straight from the front, strict
elevation view. A tall slender white statue of Jesus that is NOT the Rio de Janeiro pose: both arms are raised and
open in a wide V greeting gesture, the left arm (viewer's left) raised high, almost diagonal, open hand with spread
fingers, the right arm opened to the side, lower, palm up; head slightly lifted looking far away, long wavy hair to
the shoulders, full beard, long robe to the ground with a mantle crossing the chest diagonally, deep sinuous folds,
wide hanging sleeves like cloth wings, no visible feet. Matte white stone. The statue stands on a low blue polygonal
pedestal about one fifth of the statue's height. The pedestal sits in the middle of a white terrace with blue stripes
and a thin railing: the terrace is the flat roof of a low one-storey pavilion with open bays glowing warm yellow
underneath (a small bar, no signs). A wide straight central staircase with metal handrails rises from the ground to
the terrace, on the statue's axis. Pavilion plus pedestal are about one third of the statue's height. The bottom edge
of the pavilion is a straight horizontal line. No people, no trees, no ground.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1422x1024 px (aspect 150:108); nothing else
in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: golden-hour sunset coming from the left. Warm gold/orange light on left-facing surfaces, cool violet-blue
shadows on the right side. Dusk palette: amber, salmon, rose-violet; nothing is lit by white noon light.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 4. `cenarios/cristo/folhas/morro.png`

Topo de morro onde o monumento assenta: pasto, estradinha, casinhas brancas ao pé das torres.
Tamanho final: **634x64**. Pedir: 1536x1024, desenho em 1536x155 no centro (2.4x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A wide rounded hilltop silhouette, strict side view, filling
the whole width: light olive-green pasture, the crest almost flat in the central third and gently falling toward both
sides, a pale dirt track along the crest, a few fence posts going downhill, two tiny white utility huts on the right
third of the crest, a few dark bushes. The bottom half is plain darker pasture down to a straight bottom edge. No
statue, no towers, no tall trees, no people: those are separate pieces.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x155 px (aspect 634:64), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: golden-hour sunset coming from the left. Warm gold/orange light on left-facing surfaces, cool violet-blue
shadows on the right side. Dusk palette: amber, salmon, rose-violet; nothing is lit by white noon light.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 5. `cenarios/cristo/folhas/torres.png`

Três torres de telecomunicação treliçadas, vermelhas e brancas.
Tamanho final: **72x112**. Pedir: 1024x1536, desenho em 987x1536 no centro (13.7x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. Three tall thin lattice telecommunication towers side by side
at slightly different heights, strict side view, painted in alternating red and white sections, thin steel truss
pattern, small antennas near the tops, no lights drawn, no dishes with logos. Their feet are on one straight
horizontal line at the bottom. Nothing else.
Format: 1024x1536 image. The drawing fills a centered rectangle of exactly 987x1536 px (aspect 72:112); nothing else
in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: golden-hour sunset coming from the left. Warm gold/orange light on left-facing surfaces, cool violet-blue
shadows on the right side. Dusk palette: amber, salmon, rose-violet; nothing is lit by white noon light.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 6. `cenarios/cristo/folhas/longe.png`

Fundo distante: mar de morros azulados e, embaixo, a cidade de telhado laranja com o rio e uma ponte.
Tamanho final: **478x104**. Pedir: 1536x1024, desenho em 1536x334 no centro (3.2x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A distant landscape strip seen from a hilltop, strict side
view, filling the whole width: the upper part is a sea of low rounded hills in 4 overlapping layers that get bluer and
paler toward the horizon (patches of dark forest, light pasture, a few spots of red-orange bare earth). In the lower
half, down in the valley, a small old Brazilian town: low houses of one to three storeys with orange-red clay tile
roofs and white, blue, yellow and pink walls, one tall lone brick chimney, a wide dark river crossing the town with
green banks and one pale concrete bridge. Everything small and far away, low contrast. The top edge is the hill
skyline (magenta above it); the bottom 20% is plain dark green slope down to a straight bottom edge. No statue, no
people, no text.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x334 px (aspect 478:104), as wide as
the image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: golden-hour sunset coming from the left. Warm gold/orange light on left-facing surfaces, cool violet-blue
shadows on the right side. Dusk palette: amber, salmon, rose-violet; nothing is lit by white noon light.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 7. `cenarios/cristo/folhas/nuvens_longe.png`

Faixa de nuvens distantes (repete).
Tamanho final: **384x36**. Pedir: 1536x1024, desenho em 1536x144 no centro (4.0x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A horizontal strip of 4 or 5 small thin distant clouds,
separated from each other, lit from below by sunset: rose and salmon bellies, violet tops. Hard pixel edges, 3 flat
tones each. Nothing touches the left or right edge of the strip (magenta gap at both ends) so the strip can repeat.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x144 px (aspect 384:36), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: golden-hour sunset coming from the left. Warm gold/orange light on left-facing surfaces, cool violet-blue
shadows on the right side. Dusk palette: amber, salmon, rose-violet; nothing is lit by white noon light.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 8. `cenarios/cristo/folhas/nuvens_perto.png`

Faixa de nuvens próximas, maiores (repete).
Tamanho final: **384x52**. Pedir: 1536x1024, desenho em 1536x208 no centro (4.0x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A horizontal strip of 3 larger cumulus clouds, separated from
each other, sunset lit: bright amber-gold rims on the lower left, rose body, deep violet shadow on top right. Hard
pixel edges, 4 flat tones each. Nothing touches the left or right edge of the strip (magenta gap at both ends) so the
strip can repeat.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x208 px (aspect 384:52), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: golden-hour sunset coming from the left. Warm gold/orange light on left-facing surfaces, cool violet-blue
shadows on the right side. Dusk palette: amber, salmon, rose-violet; nothing is lit by white noon light.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 9. `cenarios/cristo/folhas/cerca.png`

Cerca de mourões com dois fios (repete), atrás dos lutadores.
Tamanho final: **128x26**. Pedir: 1536x1024, desenho em 1536x312 no centro (12.0x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A seamless horizontally tiling rural fence, strict side view:
3 rough wooden posts evenly spaced, two thin wires between them, a few tufts of grass at the feet. Warm light on the
left side of each post, violet shadow on the right. The wires meet the left and right edges at the same heights so the
strip can repeat. Bottom edge straight.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x312 px (aspect 128:26), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: golden-hour sunset coming from the left. Warm gold/orange light on left-facing surfaces, cool violet-blue
shadows on the right side. Dusk palette: amber, salmon, rose-violet; nothing is lit by white noon light.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 10. `cenarios/cristo/folhas/arvores_morro.png`

Grupo de árvores de copa redonda no morro, ao vento.
Tamanho final: **96x56 por quadro, 8 quadros**. Pedir: 1536x1024, grade 2 colunas x 4 linhas. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. A small group of three
round-crowned dark green trees with short trunks, seen far away, swaying in the wind: the crowns lean and ripple
slightly to the right and come back, leaves shifting. Trunk bases fixed on the same line in every frame.
Format: a grid of 2 columns x 4 rows on a 1536x1024 image, reading order left to right, top to bottom. 8 frames in
equal invisible cells (each cell has aspect 96:56), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: golden-hour sunset coming from the left. Warm gold/orange light on left-facing surfaces, cool violet-blue
shadows on the right side. Dusk palette: amber, salmon, rose-violet; nothing is lit by white noon light.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 11. `cenarios/cristo/folhas/visitantes.png`

Visitantes minúsculos (8 px de altura) no terraço e na escada.
Tamanho final: **128x20 por quadro, 8 quadros**. Pedir: 1536x1024, grade 2 colunas x 4 linhas. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. A row of six tiny generic
visitors seen from far away (each only a few pixels tall, simple colored shirts, no faces): two leaning on a railing,
one pointing at the view, one waving, two walking up one step and back. Small readable movements only; feet stay on
the same line. No real persons, no text.
Format: a grid of 2 columns x 4 rows on a 1536x1024 image, reading order left to right, top to bottom. 8 frames in
equal invisible cells (each cell has aspect 128:20), no cell borders, no numbers. The element has the same size and
the same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: golden-hour sunset coming from the left. Warm gold/orange light on left-facing surfaces, cool violet-blue
shadows on the right side. Dusk palette: amber, salmon, rose-violet; nothing is lit by white noon light.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 12. `cenarios/cristo/folhas/palmeira.png`

Palmeira isolada, de perto, balançando.
Tamanho final: **96x144 por quadro, 8 quadros**. Pedir: imagem larga 3:1, 1 fileira de 8 quadros. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. One tall palm tree seen
from close, slender curved trunk, big fronds swaying in a steady hilltop wind: fronds lift, bend to the right and fall
back, tips lagging one frame behind. Trunk base fixed at the bottom center in every frame.
Format: one single row of 8 frames, evenly spaced, on a wide image (about 3:1, like the attached sheet). 8 frames in
equal invisible cells (each cell has aspect 96:144), no cell borders, no numbers. The element has the same size and
the same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: golden-hour sunset coming from the left. Warm gold/orange light on left-facing surfaces, cool violet-blue
shadows on the right side. Dusk palette: amber, salmon, rose-violet; nothing is lit by white noon light.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 13. `cenarios/cristo/folhas/arvore.png`

Árvore de copa redonda, de perto, ao vento.
Tamanho final: **128x128 por quadro, 8 quadros**. Pedir: imagem larga 3:1, 1 fileira de 8 quadros. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. One sturdy tree with a
short thick trunk and a big round dark green crown, seen from close, in the wind: the crown mass shifts slightly to
the right and back, leaf clumps rippling, a few leaves flying off in two frames. Trunk base fixed at the bottom center
in every frame.
Format: one single row of 8 frames, evenly spaced, on a wide image (about 3:1, like the attached sheet). 8 frames in
equal invisible cells (each cell has aspect 128:128), no cell borders, no numbers. The element has the same size and
the same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: golden-hour sunset coming from the left. Warm gold/orange light on left-facing surfaces, cool violet-blue
shadows on the right side. Dusk palette: amber, salmon, rose-violet; nothing is lit by white noon light.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 14. `cenarios/cristo/folhas/capim.png`

Tufo de capim rente ao chão, na frente dos lutadores.
Tamanho final: **64x14 por quadro, 8 quadros**. Pedir: 1536x1024, grade 2 colunas x 4 linhas. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. A low tuft of tall grass
blades seen from very close, dark olive with gold tips, waving: blades bend right and come back in a soft wave. The
base is fixed on the bottom edge in every frame. Very low and wide shape.
Format: a grid of 2 columns x 4 rows on a 1536x1024 image, reading order left to right, top to bottom. 8 frames in
equal invisible cells (each cell has aspect 64:14), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: golden-hour sunset coming from the left. Warm gold/orange light on left-facing surfaces, cool violet-blue
shadows on the right side. Dusk palette: amber, salmon, rose-violet; nothing is lit by white noon light.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

### Chat "Cenário Maria Fumaça — arcade"

#### 1. `cenarios/maria_fumaca/folhas/ceu.png`

Céu da noite, sem transparência.
Tamanho final: **320x180**. Pedir: 1536x1024, pintada inteira; usa-se o miolo 16:9. Fundo: sem transparência.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background layer for a 2D fighting game stage. A night sky only: flat horizontal bands from near-black indigo
at the top to cobalt blue at the bottom, a small pale full moon in the right third at mid height, about 25
single-pixel stars scattered in the upper half. No clouds, no land, no objects.
Format: 1536x1024 image, fully painted edge to edge, no magenta, no transparency. Only the central 16:9 area will be
used, so keep the bands running straight across the full width.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: night interior lit by warm amber glass-globe lamps from above; warm amber highlights on top-facing surfaces,
deep wine-brown and violet shadows. Dark, cozy palette; outside the building is cobalt-blue night.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 2. `cenarios/maria_fumaca/folhas/chao.png`

Piso de paralelepípedo (repete na horizontal), com poças de luz âmbar.
Tamanho final: **256x54**. Pedir: 1536x1024, desenho em 1536x324 no centro (6.0x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A seamless horizontally tiling floor strip, strict side view
of a cobblestone station platform: grey-blue rounded cobblestones in regular rows seen at a low angle, rows getting
slightly taller toward the bottom, dark joints, soft pools of warm amber lamplight as flat lighter patches, one small
damp darker patch. The left and right edges must match so the strip repeats: same rows and same colors at both edges.
No objects.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x324 px (aspect 256:54), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: night interior lit by warm amber glass-globe lamps from above; warm amber highlights on top-facing surfaces,
deep wine-brown and violet shadows. Dark, cozy palette; outside the building is cobalt-blue night.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 3. `cenarios/maria_fumaca/folhas/locomotiva.png`

A locomotiva de perfil, virada para a esquerda, no trilho curto, com a grade branca na frente. É o desenho que identifica o lugar.
Tamanho final: **200x96**. Pedir: 1536x1024, desenho em 1536x737 no centro (7.7x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A small 19th-century narrow-gauge 0-6-0 tank steam locomotive
in exact side profile, facing LEFT, standing still on a short piece of track. Its most striking feature: a huge black
funnel-shaped balloon smokestack near the front, much wider at the top than at the base, with two polished brass bands
and a slightly domed cap, almost half the height of the engine. In front of the smokestack a square green lantern box
with a milky white glass. Round black riveted smokebox door, black buffer beam. Body in medium flag green with thin
yellow pinstripe rectangles with rounded corners and rows of rivets; green side tank along the boiler; a green
cylindrical steam dome with a gold band; a small bracket for a bell just behind the smokestack (do NOT draw the bell,
it is a separate animated piece). Green cab at the right end with a curved roof with eaves and upright oval
pill-shaped windows, open at the back. Three dark coupled wheels with connecting rods, dark and understated. The short
track has thick pale stone sleepers. In front of the engine, along the whole width, a low white wrought-iron fence of
thin vertical bars with small scrolls on top, waist high, through which the wheels are visible. No smoke, no steam, no
people, no plaques with text, no numbers. Bottom edge straight.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x737 px (aspect 200:96), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: night interior lit by warm amber glass-globe lamps from above; warm amber highlights on top-facing surfaces,
deep wine-brown and violet shadows. Dark, cozy palette; outside the building is cobalt-blue night.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 4. `cenarios/maria_fumaca/folhas/vao_galpao.png`

Um módulo da parede e do telhado do galpão (repete na horizontal): pilar, vão ogival aberto, veneziana, vidro, tesoura.
Tamanho final: **128x182**. Pedir: 1024x1536, desenho em 1024x1456 no centro (8.0x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. One repeating bay of the long side wall of an old covered
railway platform hall, strict front elevation, designed to tile horizontally. From the top: the upper 38% is the
underside of a gabled roof (orange-brown clay tiles seen from below, very dark wooden rafters and one dark wooden
tie-beam running horizontally at 36% from the top, straight across both edges); then a band of dark wooden louvered
panels; then a narrow band of milky white glass panes; then, in the lower 45%, a cream plaster wall with one tall
pointed gothic (ogival) arch doorway that is OPEN: the inside of the arch is flat magenta (it will be transparent). On
the left edge, a square pillar painted emerald green, about one fifth of the width, running from the floor to the
tie-beam, with a small wall lamp with a white glass globe at two thirds of its height. Wall base in darker tone. The
left edge and the right edge must match (the right edge of the wall meets the next pillar): same band heights and
colors at both edges. The bottom edge is the straight floor line. No people, no furniture, no text.
Format: 1024x1536 image. The drawing fills a centered rectangle of exactly 1024x1456 px (aspect 128:182), as wide as
the image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: night interior lit by warm amber glass-globe lamps from above; warm amber highlights on top-facing surfaces,
deep wine-brown and violet shadows. Dark, cozy palette; outside the building is cobalt-blue night.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 5. `cenarios/maria_fumaca/folhas/longe.png`

Lá fora ao longe: a outra margem em silhueta e o rio com o caminho da lua.
Tamanho final: **478x96**. Pedir: 1536x1024, desenho em 1536x308 no centro (3.2x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A distant night riverside strip, strict side view, filling the
whole width: at the top a skyline of low rounded hills and a few low houses with clay roofs and round trees on the far
bank, all as dark blue silhouettes with 3 or 4 tiny warm lit windows; below it a wide calm dark river with flat
horizontal bands of slightly lighter blue and a pale broken moonlight path in the right third; the bottom 25% is the
dark near bank down to a straight bottom edge. Magenta above the skyline. No boats, no people, no text.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x308 px (aspect 478:96), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: night interior lit by warm amber glass-globe lamps from above; warm amber highlights on top-facing surfaces,
deep wine-brown and violet shadows. Dark, cozy palette; outside the building is cobalt-blue night.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 6. `cenarios/maria_fumaca/folhas/nuvens.png`

Faixa de nuvens da noite (repete).
Tamanho final: **384x40**. Pedir: 1536x1024, desenho em 1536x160 no centro (4.0x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A horizontal strip of 4 thin night clouds, separated from each
other, dark slate-blue with a pale moonlit rim on the upper right. Hard pixel edges, 3 flat tones. Nothing touches the
left or right edge of the strip (magenta gap at both ends) so the strip can repeat.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x160 px (aspect 384:40), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: night interior lit by warm amber glass-globe lamps from above; warm amber highlights on top-facing surfaces,
deep wine-brown and violet shadows. Dark, cozy palette; outside the building is cobalt-blue night.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 7. `cenarios/maria_fumaca/folhas/lustre.png`

Um lustre de ferro com globos brancos, pendurado por uma haste.
Tamanho final: **20x60**. Pedir: 1024x1536, desenho em 512x1536 no centro (25.6x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. One old hanging iron ceiling lamp, strict side view: a long
thin dark iron rod coming from the top edge, a small iron scroll frame, and three round milky white glass globes
glowing warm cream at the bottom (one center, two at the sides). Tall narrow shape. No glow halo drawn around it.
Format: 1024x1536 image. The drawing fills a centered rectangle of exactly 512x1536 px (aspect 20:60); nothing else in
the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: night interior lit by warm amber glass-globe lamps from above; warm amber highlights on top-facing surfaces,
deep wine-brown and violet shadows. Dark, cozy palette; outside the building is cobalt-blue night.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 8. `cenarios/maria_fumaca/folhas/fumaca.png`

Fumaça saindo da chaminé (a boca fica embaixo, à esquerda).
Tamanho final: **96x64 por quadro, 8 quadros**. Pedir: imagem larga 3:1, 1 fileira de 8 quadros. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. Smoke only, no
locomotive: a soft column of pale grey-cream smoke rising from a point at the bottom left corner, curling up and
drifting to the right as it flattens under a roof. 3 flat tones, warm amber-lit underside, hard pixel edges, puffs
separating and dissolving into a few hard fragments at the right. Each frame advances the same puffs a little so the
loop is continuous.
Format: one single row of 8 frames, evenly spaced, on a wide image (about 3:1, like the attached sheet). 8 frames in
equal invisible cells (each cell has aspect 96:64), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: night interior lit by warm amber glass-globe lamps from above; warm amber highlights on top-facing surfaces,
deep wine-brown and violet shadows. Dark, cozy palette; outside the building is cobalt-blue night.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 9. `cenarios/maria_fumaca/folhas/vapor.png`

Vapor baixo junto às rodas.
Tamanho final: **96x28 por quadro, 8 quadros**. Pedir: 1536x1024, grade 2 colunas x 4 linhas. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. Low steam only, no
machine: a thin white-cream steam cloud hugging the ground, leaking from a point at the left and spreading to the
right, rolling and thinning. 3 flat tones, hard pixel edges. Bottom edge on the same line in every frame. Wide and low
shape.
Format: a grid of 2 columns x 4 rows on a 1536x1024 image, reading order left to right, top to bottom. 8 frames in
equal invisible cells (each cell has aspect 96:28), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: night interior lit by warm amber glass-globe lamps from above; warm amber highlights on top-facing surfaces,
deep wine-brown and violet shadows. Dark, cozy palette; outside the building is cobalt-blue night.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 10. `cenarios/maria_fumaca/folhas/sino.png`

Sino de bronze balançando.
Tamanho final: **20x20 por quadro, 8 quadros**. Pedir: imagem larga 3:1, 1 fileira de 8 quadros. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. One small bronze bell
hanging from a fixed pivot at the top center, swinging: center, right, far right, right, center, left, far left, left.
The clapper lags one frame behind. Bronze with one hard highlight. Very small and simple.
Format: one single row of 8 frames, evenly spaced, on a wide image (about 3:1, like the attached sheet). 8 frames in
equal invisible cells (each cell has aspect 20:20), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: night interior lit by warm amber glass-globe lamps from above; warm amber highlights on top-facing surfaces,
deep wine-brown and violet shadows. Dark, cozy palette; outside the building is cobalt-blue night.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 11. `cenarios/maria_fumaca/folhas/bandeirolas.png`

Varal de bandeirolas amarelas (repete).
Tamanho final: **128x20 por quadro, 8 quadros**. Pedir: 1536x1024, grade 2 colunas x 4 linhas. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. A string of small yellow
triangular festival pennants hanging on a thin cord that sags slightly, fluttering in a light draft: a wave travels
along the pennants from left to right. The cord meets the left and right edges at the same height in every frame so
the strip can repeat. Plain yellow and gold pennants, no text, no symbols.
Format: a grid of 2 columns x 4 rows on a 1536x1024 image, reading order left to right, top to bottom. 8 frames in
equal invisible cells (each cell has aspect 128:20), no cell borders, no numbers. The element has the same size and
the same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: night interior lit by warm amber glass-globe lamps from above; warm amber highlights on top-facing surfaces,
deep wine-brown and violet shadows. Dark, cozy palette; outside the building is cobalt-blue night.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 12. `cenarios/maria_fumaca/folhas/arvores_rua.png`

Árvores baixas de copa redonda na rua, à noite.
Tamanho final: **128x84 por quadro, 8 quadros**. Pedir: imagem larga 3:1, 1 fileira de 8 quadros. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. Two low street trees with
round crowns and short trunks, seen at night from a distance as dark blue-green shapes with a pale moonlit rim, crowns
swaying gently to the right and back. Trunk bases fixed on the bottom edge in every frame. Nothing touches the left or
right edges.
Format: one single row of 8 frames, evenly spaced, on a wide image (about 3:1, like the attached sheet). 8 frames in
equal invisible cells (each cell has aspect 128:84), no cell borders, no numbers. The element has the same size and
the same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: night interior lit by warm amber glass-globe lamps from above; warm amber highlights on top-facing surfaces,
deep wine-brown and violet shadows. Dark, cozy palette; outside the building is cobalt-blue night.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 13. `cenarios/maria_fumaca/folhas/plateia_banco.png`

Três figurantes genéricos num banco de ripas, torcendo.
Tamanho final: **112x76 por quadro, 8 quadros**. Pedir: imagem larga 3:1, 1 fileira de 8 quadros. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. Three generic spectators
sitting on an old slatted park bench with iron legs, seen from the front, cheering a fight: one raises a fist, one
claps, one leans forward and points. 4 poses played forward and back. Everyday small-town clothes in muted colors,
simple faces with no likeness to any real person, no text or logos on clothes. The bench and their feet stay fixed on
the bottom edge.
Format: one single row of 8 frames, evenly spaced, on a wide image (about 3:1, like the attached sheet). 8 frames in
equal invisible cells (each cell has aspect 112:76), no cell borders, no numbers. The element has the same size and
the same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: night interior lit by warm amber glass-globe lamps from above; warm amber highlights on top-facing surfaces,
deep wine-brown and violet shadows. Dark, cozy palette; outside the building is cobalt-blue night.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 14. `cenarios/maria_fumaca/folhas/mesa_bar.png`

Dois figurantes numa mesa de bar de madeira.
Tamanho final: **112x76 por quadro, 8 quadros**. Pedir: imagem larga 3:1, 1 fileira de 8 quadros. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. Two generic people
sitting at a small wooden bar table on wooden chairs, seen from the front: one lifts a plain glass and puts it down,
the other slaps the table and laughs, then both turn their heads to watch. Muted everyday clothes, simple faces with
no likeness to any real person, plain unlabeled bottle and glasses, no text or logos. Table, chairs and feet fixed on
the bottom edge.
Format: one single row of 8 frames, evenly spaced, on a wide image (about 3:1, like the attached sheet). 8 frames in
equal invisible cells (each cell has aspect 112:76), no cell borders, no numbers. The element has the same size and
the same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: night interior lit by warm amber glass-globe lamps from above; warm amber highlights on top-facing surfaces,
deep wine-brown and violet shadows. Dark, cozy palette; outside the building is cobalt-blue night.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

### Chat "Cenário Praça — arcade"

#### 1. `cenarios/praca/folhas/ceu.png`

Céu azul da manhã, sem transparência.
Tamanho final: **320x180**. Pedir: 1536x1024, pintada inteira; usa-se o miolo 16:9. Fundo: sem transparência.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background layer for a 2D fighting game stage. A clear morning sky only: flat horizontal bands from strong
medium blue at the top to pale light blue at the bottom. 4 or 5 flat bands with hard pixel edges, no smooth gradient.
No sun, no clouds, no land, no objects.
Format: 1536x1024 image, fully painted edge to edge, no magenta, no transparency. Only the central 16:9 area will be
used, so keep the bands running straight across the full width.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: bright clear morning sun from the upper left, strong blue sky. Clean saturated local colors, short cool
blue-violet shadows falling to the right. Cheerful postcard daylight.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 2. `cenarios/praca/folhas/chao.png`

Piso da praça (repete na horizontal): meio-fio azul e branco em cima, blocos cinza com faixas rosadas.
Tamanho final: **256x54**. Pedir: 1536x1024, desenho em 1536x324 no centro (6.0x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A seamless horizontally tiling ground strip of a small
Brazilian town square, strict side view: at the very top a thin curb painted in alternating royal blue and white
segments; below it interlocking concrete pavers in light grey with two horizontal bands of pinkish-red pavers, rows
getting slightly taller toward the bottom, thin dark joints, short cool shadows. The left and right edges must match
so the strip repeats: same rows, same curb segment pattern and same colors at both edges. No objects.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x324 px (aspect 256:54), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: bright clear morning sun from the upper left, strong blue sky. Clean saturated local colors, short cool
blue-violet shadows falling to the right. Cheerful postcard daylight.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 3. `cenarios/praca/folhas/prefeitura.png`

A fachada da Prefeitura com escadaria, terraço, lampiões e o busto. É o desenho que identifica o lugar. O letreiro fica em branco.
Tamanho final: **352x122**. Pedir: 1536x1024, desenho em 1536x532 no centro (4.4x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. The front facade of a small-town Brazilian neoclassical town
hall, strict front elevation, perfectly symmetric, wide and low (about 2.9 times wider than tall), two storeys on a
raised base about one meter high. Walls in vivid emerald green with white mouldings, white corner pilasters
(rusticated blocks on the ground floor, fluted above) and white friezes. Eleven openings per floor: a slightly
projecting central body of three openings and four on each side. Upper floor: tall rectangular French doors with cream
louvered wooden shutters, white frames with a small straight cornice, each with its own small wrought-iron balcony
painted gold; the central balcony is wider and curved, with a white stucco laurel ornament under it. Ground floor:
cream paneled double doors and shuttered windows. On top: a strong cornice and a balustrade parapet along the whole
width; in the center a low triangular pediment with a BLANK white plaque (no letters at all) and white scrollwork at
the sides, a small round generic emblem above it; repeated golden urn pinnacles on the parapet; at each end of the
parapet a golden statue of a winged lion; one fishbone TV antenna on the roof. Three slanted flagpoles come out of the
central balconies WITHOUT flags (flags are a separate animated piece). In the center a wide grey-brown granite
staircase of 8 steps, flaring outward at the bottom, with a metal handrail in the middle; on both sides of the stair a
terrace with a low white balustrade, and on the two posts next to the stair two old bronze street lanterns with glass
domes. On the ground just right of the staircase, a dark bronze bust of a generic man in a suit on a tall pale stone
pedestal (no likeness to any real person, blank plaque). The bottom edge is a straight horizontal ground line. No
people, no cars, no text, no letters anywhere.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x532 px (aspect 352:122), as wide as
the image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: bright clear morning sun from the upper left, strong blue sky. Clean saturated local colors, short cool
blue-violet shadows falling to the right. Cheerful postcard daylight.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 4. `cenarios/praca/folhas/casario.png`

Plano médio: casario comercial colorido à esquerda e no centro; lateral da Igreja Matriz com uma torre à direita.
Tamanho final: **634x142**. Pedir: 1536x1024, desenho em 1536x344 no centro (2.4x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A wide strip of old Brazilian small-town buildings seen from a
distance, strict front elevation, filling the whole width. Left two thirds: a continuous row of two-storey colonial
and eclectic commercial townhouses in golden yellow, light blue, white with blue trims, pink; clay tile roofs, cut-out
decorative parapets, small iron balconies, plain striped awnings and blank shop bands with no text; a few white lamp
posts and sagging overhead wires. Right third: the very tall plain side wall of a baroque church in pale straw-cream
with damp stains, curved-top windows and round oculi, a clay tile roof, and ONE square bell tower rising well above
everything else, with an open belfry arch (no bell drawn), an octagonal clock face without readable numbers, and a
bulbous pyramidal spire covered in grey-blue ceramic shards with small corner pinnacles (no weather vane drawn). The
lower 25% of the whole strip is plain walls and doors down to a straight bottom edge. Magenta above the roofline. No
people, no cars, no text, no signs, no logos.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x344 px (aspect 634:142), as wide as
the image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: bright clear morning sun from the upper left, strong blue sky. Clean saturated local colors, short cool
blue-violet shadows falling to the right. Cheerful postcard daylight.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 5. `cenarios/praca/folhas/longe.png`

Fundo distante: morros verdes arredondados com palmeiras na crista.
Tamanho final: **478x90**. Pedir: 1536x1024, desenho em 1536x289 no centro (3.2x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A distant strip of low rounded green hills, strict side view,
filling the whole width: 3 overlapping hill layers, patches of dark forest and lighter pasture, scattered palms and
coconut trees on the crests, a few tiny houses with clay roofs climbing the nearest slope. Slightly hazy, low
contrast, bluer toward the back. Magenta above the skyline; the bottom 30% is plain green slope down to a straight
bottom edge. No text, no people.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x289 px (aspect 478:90), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: bright clear morning sun from the upper left, strong blue sky. Clean saturated local colors, short cool
blue-violet shadows falling to the right. Cheerful postcard daylight.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 6. `cenarios/praca/folhas/nuvens_longe.png`

Faixa de nuvens distantes (repete).
Tamanho final: **384x40**. Pedir: 1536x1024, desenho em 1536x160 no centro (4.0x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A horizontal strip of 5 small white distant cumulus clouds,
separated from each other, flat bottoms, pale blue-lilac shadow underneath. Hard pixel edges, 3 flat tones. Nothing
touches the left or right edge of the strip (magenta gap at both ends) so the strip can repeat.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x160 px (aspect 384:40), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: bright clear morning sun from the upper left, strong blue sky. Clean saturated local colors, short cool
blue-violet shadows falling to the right. Cheerful postcard daylight.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 7. `cenarios/praca/folhas/nuvens_perto.png`

Faixa de cúmulos grandes (repete).
Tamanho final: **384x60**. Pedir: 1536x1024, desenho em 1536x240 no centro (4.0x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A horizontal strip of 3 big puffy white cumulus clouds,
separated from each other, bright white tops lit from the upper left, flat blue-lilac shaded bottoms. Hard pixel
edges, 4 flat tones. Nothing touches the left or right edge of the strip (magenta gap at both ends) so the strip can
repeat.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x240 px (aspect 384:60), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: bright clear morning sun from the upper left, strong blue sky. Clean saturated local colors, short cool
blue-violet shadows falling to the right. Cheerful postcard daylight.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 8. `cenarios/praca/folhas/lado_esq.png`

Ponta esquerda do mundo: casa térrea azul-clara e um poste branco alto.
Tamanho final: **176x100**. Pedir: 1536x1024, desenho em 1536x873 no centro (8.7x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A simple one-storey old Brazilian house, strict front
elevation: light blue walls, white frames, two shuttered windows and one door, clay tile roof with eaves, a small air
conditioner box on the wall. At its right side a tall modern white lamp post with a double gull-wing lamp head. A thin
curb at the base. Bottom edge is a straight ground line. No people, no text, no signs.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x873 px (aspect 176:100), as wide as
the image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: bright clear morning sun from the upper left, strong blue sky. Clean saturated local colors, short cool
blue-violet shadows falling to the right. Cheerful postcard daylight.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 9. `cenarios/praca/folhas/lado_dir.png`

Ponta direita do mundo: ladeira de paralelepípedo, adro elevado da igreja com gradil e escadinha.
Tamanho final: **176x130**. Pedir: 1536x1024, desenho em 1386x1024 no centro (7.9x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. The corner of an old church yard beside a town square, strict
front elevation: on the left a narrow cobblestone side street going slightly uphill; on the right a raised stone
churchyard platform about one meter high with a wrought-iron railing on top and a short side stair of five steps, and
behind it the lower part of a very tall pale straw-cream church wall with damp stains and one curved-top window. One
tall modern white lamp post with a double gull-wing lamp head. Bottom edge is a straight ground line. No people, no
text.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1386x1024 px (aspect 176:130); nothing else
in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: bright clear morning sun from the upper left, strong blue sky. Clean saturated local colors, short cool
blue-violet shadows falling to the right. Cheerful postcard daylight.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 10. `cenarios/praca/folhas/bandeiras.png`

Três bandeiras tremulando nos mastros inclinados (só os panos e a ponta dos mastros).
Tamanho final: **96x56 por quadro, 8 quadros**. Pedir: 1536x1024, grade 2 colunas x 4 linhas. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. Three flags waving on
three short slanted flagpoles that fan out (left pole leaning left, center pole upright, right pole leaning right),
pole bases fixed on the bottom edge in every frame. Left flag: the flag of the Brazilian state of Bahia (red and white
horizontal stripes, blue canton with a white triangle). Center flag: the flag of Brazil (green field, yellow rhombus,
blue disc, a plain white band with NO letters). Right flag: a plain white and blue municipal flag with a small generic
round emblem. A soft wave travels along each cloth from the pole to the free end, the three flags slightly out of
phase.
Format: a grid of 2 columns x 4 rows on a 1536x1024 image, reading order left to right, top to bottom. 8 frames in
equal invisible cells (each cell has aspect 96:56), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: bright clear morning sun from the upper left, strong blue sky. Clean saturated local colors, short cool
blue-violet shadows falling to the right. Cheerful postcard daylight.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 11. `cenarios/praca/folhas/canteiro.png`

Canteiro de mureta azul-royal com palmeira pequena e buganvília, ao vento.
Tamanho final: **80x100 por quadro, 8 quadros**. Pedir: imagem larga 3:1, 1 fileira de 8 quadros. Fundo: ciano #00FFFF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. A low curved planter with
a royal blue painted low wall (bench height), grass and a border of small white pebbles, holding one small feathery
palm about three times the height of the wall and one bougainvillea bush with vivid magenta-pink flowers (deep pink
#D8408A; the background of this sheet is cyan, not magenta). The palm fronds and the bush sway gently to the right and
back, a few petals drifting in two frames. The planter is fixed on the bottom edge in every frame.
Format: one single row of 8 frames, evenly spaced, on a wide image (about 3:1, like the attached sheet). 8 frames in
equal invisible cells (each cell has aspect 80:100), no cell borders, no numbers. The element has the same size and
the same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure cyan (#00FFFF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on the
background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: bright clear morning sun from the upper left, strong blue sky. Clean saturated local colors, short cool
blue-violet shadows falling to the right. Cheerful postcard daylight.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 12. `cenarios/praca/folhas/ambulante.png`

Ambulante genérico com carrinho de mão de fruta amarela e guarda-sol.
Tamanho final: **88x88 por quadro, 8 quadros**. Pedir: imagem larga 3:1, 1 fileira de 8 quadros. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. A generic street vendor
standing beside a wheelbarrow full of yellow fruit under a plain striped beach umbrella with no text: he fans himself
with a straw hat, wipes his forehead, waves to call customers, and the umbrella rim sways. 4 poses played forward and
back. Simple everyday clothes, simple face with no likeness to any real person, no text, no logos. Feet, wheelbarrow
and umbrella pole fixed on the bottom edge.
Format: one single row of 8 frames, evenly spaced, on a wide image (about 3:1, like the attached sheet). 8 frames in
equal invisible cells (each cell has aspect 88:88), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: bright clear morning sun from the upper left, strong blue sky. Clean saturated local colors, short cool
blue-violet shadows falling to the right. Cheerful postcard daylight.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 13. `cenarios/praca/folhas/torcida_mureta.png`

Quatro figurantes genéricos sentados numa mureta azul, torcendo.
Tamanho final: **128x64 por quadro, 8 quadros**. Pedir: 1536x1024, grade 2 colunas x 4 linhas. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. Four generic townspeople
of different ages sitting side by side on a low royal blue painted wall, seen from the front, cheering a street fight:
one raises both arms, one claps, one cups hands around the mouth to shout, one holds a plain shopping bag and nods. 4
poses played forward and back. Bright everyday clothes, simple faces with no likeness to any real person, no text or
logos. The wall and their feet stay fixed on the bottom edge.
Format: a grid of 2 columns x 4 rows on a 1536x1024 image, reading order left to right, top to bottom. 8 frames in
equal invisible cells (each cell has aspect 128:64), no cell borders, no numbers. The element has the same size and
the same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: bright clear morning sun from the upper left, strong blue sky. Clean saturated local colors, short cool
blue-violet shadows falling to the right. Cheerful postcard daylight.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

### Chat "Cenário Passarela — arcade"

#### 1. `cenarios/passarela/folhas/ceu.png`

Céu do amanhecer, sem transparência.
Tamanho final: **320x180**. Pedir: 1536x1024, pintada inteira; usa-se o miolo 16:9. Fundo: sem transparência.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background layer for a 2D fighting game stage. A dawn sky only: flat horizontal bands from muted blue-teal at
the top, through grey-lilac, to soft peach at the bottom third. 5 or 6 flat bands with hard, slightly wavy pixel
edges, no smooth gradient. No sun disc, no clouds, no land, no objects.
Format: 1536x1024 image, fully painted edge to edge, no magenta, no transparency. Only the central 16:9 area will be
used, so keep the bands running straight across the full width.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 2. `cenarios/passarela/folhas/chao.png`

Calçadão (repete na horizontal): concreto claro e ciclofaixa vermelha de bordas brancas.
Tamanho final: **256x54**. Pedir: 1536x1024, desenho em 1536x324 no centro (6.0x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A seamless horizontally tiling ground strip of a riverside
promenade, strict side view: the top quarter is pale grey concrete paving; below it a brick-red bicycle lane running
horizontally with a thin white line along its top and bottom borders, taking the middle half of the strip; below it
pale concrete again down to the bottom. Slight dawn dampness, faint expansion joints. The left and right edges must
match so the strip repeats: same band heights and same colors at both edges. No bicycle symbols, no arrows, no text,
no objects.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x324 px (aspect 256:54), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 3. `cenarios/passarela/folhas/cabeceira.png`

Cabeceira da passarela: escada de concreto, corrimão branco e o pórtico da treliça com a cobertura. Identifica o lugar junto com o corpo.
Tamanho final: **100x124**. Pedir: 1024x1024, desenho em 826x1024 no centro (8.3x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. The entrance of a covered white steel truss footbridge, seen
in three-quarter view from the left front: a short pale concrete stair of four steps with white tubular handrails
leads up to a deck; over the deck stands the first portal frame of the bridge: two white steel side trusses about one
and a half times a person's height with a diagonal Warren zig-zag web and thin vertical posts, and a thin, almost flat
light grey metal roof with a small overhang on top. The bridge continues away to the upper left (cut off cleanly at
the left edge, it is a separate piece). The stair foot is on a straight horizontal ground line at the bottom edge. No
people, no signs, no text.
Format: 1024x1024 image. The drawing fills a centered rectangle of exactly 826x1024 px (aspect 100:124); nothing else
in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 4. `cenarios/passarela/folhas/passarela.png`

Corpo da passarela recuando em diagonal sobre o rio, com os pilares de concreto.
Tamanho final: **230x100**. Pedir: 1536x1024, desenho em 1536x668 no centro (6.7x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. The body of a long covered white steel truss footbridge
crossing a river, seen in three-quarter view receding from the lower right corner to the upper left: it starts large
at the right edge (where it will join the entrance piece, cut off cleanly) and gets smaller toward the far bank at the
upper left. Visible side truss in white with a continuous Warren zig-zag of diagonals and thin vertical posts; a thin,
almost flat light grey metal roof strip with a small overhang along the top; the deck inside between the two trusses.
It rests low over the water on two plain concrete piers with a wider cap block on top, going down to a straight bottom
edge (the water is a separate layer). Soft peach light on the left faces, blue shadow under the roof. No people, no
boats, no water, no banks, no text.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x668 px (aspect 230:100), as wide as
the image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 5. `cenarios/passarela/folhas/guarda_corpo.png`

Guarda-corpo do calçadão (repete): barras verticais cinza-escuras com corrimão, sobre mureta clara.
Tamanho final: **128x46**. Pedir: 1536x1024, desenho em 1536x552 no centro (12.0x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A seamless horizontally tiling riverside guard rail, strict
front elevation: a low pale concrete base wall (one quarter of the height) and on top a dark grey metal railing of
thin evenly spaced vertical bars with a round handrail on top and one thicker post in the middle. The space between
the bars is flat magenta (transparent). The handrail, the bars spacing and the base wall meet the left and right edges
identically so the strip can repeat. Bottom edge straight.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x552 px (aspect 128:46), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 6. `cenarios/passarela/folhas/margem_sul.png`

A outra margem: casas e sobrados de telha laranja, árvores podadas, canoas atracadas, muro de cais.
Tamanho final: **544x56**. Pedir: 1536x1024, desenho em 1536x158 no centro (2.8x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. The far bank of a river seen from across the water at dawn,
strict side view, filling the whole width: a row of one and two storey old Brazilian houses with white, cream and
pastel walls and orange clay tile roofs, some with small verandas and blue water tanks on the roof, a few tiny warm
lit windows; a line of round pruned trees along the waterfront, a small bare-earth football field with two tiny
goalposts at the left; a stained stone and concrete quay wall darkened by algae near the waterline; five small wooden
canoes moored along the wall, painted in bright colors (yellow with blue, blue, white, green), two with a small canvas
awning. Hazy, low contrast. Magenta above the roofline. The bottom 30% is the quay wall and a dark water band down to
a straight bottom edge. No coconut palms (separate piece), no people, no text.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x158 px (aspect 544:56), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 7. `cenarios/passarela/folhas/longe.png`

Fundo distante: morros baixos verdes na névoa, casario subindo a encosta, uma chaminé alta de tijolo.
Tamanho final: **478x76**. Pedir: 1536x1024, desenho em 1536x244 no centro (3.2x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A distant strip of low rounded hills at dawn, strict side
view, filling the whole width: 3 overlapping hill layers in hazy blue-green getting paler toward the back, small
houses with clay roofs climbing the nearest slope, scattered palms on the crest, and at the right third one tall lone
red brick factory chimney (no smoke). Very low contrast, misty. Magenta above the skyline; the bottom 35% is plain
hazy slope down to a straight bottom edge. No text.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x244 px (aspect 478:76), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 8. `cenarios/passarela/folhas/nuvens.png`

Faixa de nuvens finas do amanhecer (repete).
Tamanho final: **384x30**. Pedir: 1536x1024, desenho em 1536x120 no centro (4.0x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A horizontal strip of 4 long thin stratus clouds, separated
from each other, peach-pink underside, grey-lilac top. Hard pixel edges, 3 flat tones. Nothing touches the left or
right edge of the strip (magenta gap at both ends) so the strip can repeat.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x120 px (aspect 384:30), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 9. `cenarios/passarela/folhas/neblina.png`

Faixa de neblina (repete). Vai ser SOMADA à imagem no motor: desenhada escura, sobre preto.
Tamanho final: **384x28**. Pedir: 1536x1024, desenho em 1536x112 no centro (4.0x). Fundo: preto #000000 (camada somada).

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. A horizontal strip of low river mist, drawn for additive
blending: on a flat pure BLACK background (#000000, not magenta), 4 long soft-looking but hard-edged horizontal mist
banks in 3 flat dark tones of blue-grey (#141A20, #26303A, #3A4854), wispy ends, the densest part along the middle.
Nothing brighter than #3A4854. Nothing touches the left or right edge (black gap at both ends) so the strip can
repeat. No other objects.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x112 px (aspect 384:28), as wide as the
image; nothing else in the image.
Background: flat pure black (#000000) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 10. `cenarios/passarela/folhas/canoas_atracadas.png`

Duas canoas de madeira atracadas, de lado.
Tamanho final: **96x28**. Pedir: 1536x1024, desenho em 1536x448 no centro (16.0x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. Two small wooden canoes moored side by side, strict side view,
hulls only down to the waterline (flat cut at the bottom): one yellow with a blue stripe, one green with a small plain
canvas awning on thin poles; a rope going up from each bow. Bright but slightly muted dawn colors. No people, no
names, no text.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x448 px (aspect 96:28), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 11. `cenarios/passarela/folhas/baronesa.png`

Tufo de baronesa (aguapé) flutuando.
Tamanho final: **40x10**. Pedir: 1536x1024, desenho em 1536x384 no centro (38.4x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. One small floating clump of water hyacinth seen from the side
at water level: round glossy green leaves, two tiny lilac flowers, flat cut at the waterline. Very small, wide and
low.
Format: 1536x1024 image. The drawing fills a centered rectangle of exactly 1536x384 px (aspect 40:10), as wide as the
image; nothing else in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 12. `cenarios/passarela/folhas/lampiao.png`

Poste ornamental escuro de lampião duplo.
Tamanho final: **28x104**. Pedir: 1024x1536, desenho em 414x1536 no centro (14.8x). Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw ONE background piece for a 2D fighting game stage. One ornamental dark cast-iron street lamp post, strict front
elevation: a slender fluted post on a small base, a short crossarm at the top holding two old-style lantern heads with
glass panes (glass drawn pale warm yellow, no glow halo). Tall narrow shape, base on the bottom edge.
Format: 1024x1536 image. The drawing fills a centered rectangle of exactly 414x1536 px (aspect 28:104); nothing else
in the image.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 13. `cenarios/passarela/folhas/agua.png`

Água do rio em 8 quadros (cada quadro repete na horizontal).
Tamanho final: **256x56 por quadro, 8 quadros**. Pedir: 1536x1024, grade 2 colunas x 4 linhas. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. Calm dark river water
seen from the bank, strict side view, as a strip that tiles horizontally: dark green-brown water in flat horizontal
bands, slow gentle ripples, broken horizontal reflections of pale houses and of a white bridge as short light dashes,
a few peach sparkles of dawn light. From frame to frame the ripple dashes slide slowly and the sparkles blink, with
small changes only. In every frame the left and right edges match so each frame can repeat sideways. The strip is
fully painted (no magenta inside it).
Format: a grid of 2 columns x 4 rows on a 1536x1024 image, reading order left to right, top to bottom. 8 frames in
equal invisible cells (each cell has aspect 256:56), no cell borders, no numbers. The element has the same size and
the same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 14. `cenarios/passarela/folhas/coqueiros.png`

Dois coqueiros distantes balançando.
Tamanho final: **56x56 por quadro, 8 quadros**. Pedir: imagem larga 3:1, 1 fileira de 8 quadros. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. Two coconut palms seen
from far away, thin curved trunks, crowns of fronds swaying slowly to the right and back in a light dawn breeze, hazy
blue-green with a peach rim on the left. Trunk bases fixed on the bottom edge in every frame.
Format: one single row of 8 frames, evenly spaced, on a wide image (about 3:1, like the attached sheet). 8 frames in
equal invisible cells (each cell has aspect 56:56), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 15. `cenarios/passarela/folhas/canoa_remo.png`

Canoa a remo com um remador genérico, andando para a direita.
Tamanho final: **72x36 por quadro, 8 quadros**. Pedir: 1536x1024, grade 2 colunas x 4 linhas. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. A small wooden canoe
moving to the right on calm water, strict side view, hull cut flat at the waterline, with one generic rower sitting at
the back (straw hat, plain shirt, no face detail) paddling: paddle forward, dip, pull, lift. A small white wake dash
at the stern and two ripple dashes under the hull that change every frame. The hull stays at the same place in every
frame.
Format: a grid of 2 columns x 4 rows on a 1536x1024 image, reading order left to right, top to bottom. 8 frames in
equal invisible cells (each cell has aspect 72:36), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 16. `cenarios/passarela/folhas/pedestres.png`

Dois pedestres minúsculos andando, um empurrando bicicleta.
Tamanho final: **40x24 por quadro, 8 quadros**. Pedir: 1536x1024, grade 2 colunas x 4 linhas. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. Two tiny generic
pedestrians seen from far away, walking to the left in a walk cycle: one adult with a plain bag, one person pushing a
bicycle. Each only about 10 pixels tall, simple flat colors, no faces. Feet on the same line in every frame; the
figures stay at the same place in the cell (walking in place).
Format: a grid of 2 columns x 4 rows on a 1536x1024 image, reading order left to right, top to bottom. 8 frames in
equal invisible cells (each cell has aspect 40:24), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 17. `cenarios/passarela/folhas/pescador.png`

Pescador genérico de linha, de costas, encostado no guarda-corpo.
Tamanho final: **56x92 por quadro, 8 quadros**. Pedir: imagem larga 3:1, 1 fileira de 8 quadros. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. A generic fisherman seen
from behind, standing and leaning on an invisible railing at waist height, holding a simple hand line / thin bamboo
rod over the river: he waits, gives two small tugs, looks to the side over his shoulder, scratches his head under a
straw hat, settles again. Plain worn clothes, no likeness to any real person, no text or logos. A small bucket at his
feet. Feet fixed on the bottom edge.
Format: one single row of 8 frames, evenly spaced, on a wide image (about 3:1, like the attached sheet). 8 frames in
equal invisible cells (each cell has aspect 56:92), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: dawn, the sun just risen low on the left. Cool misty palette (blue-teal, grey-lilac) with soft peach light on
left-facing surfaces and long cool shadows to the right. Low contrast, quiet morning haze.
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

### Chat "Cenários — peças comuns"

#### 1. `cenarios/comum/folhas/urubu.png`

Urubu planando (Cristo e praça).
Tamanho final: **32x24 por quadro, 8 quadros**. Pedir: imagem larga 3:1, 1 fileira de 8 quadros. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. One black vulture
soaring, seen from below and from the side, far away: long broad wings with fingered tips held in a shallow V, small
bare head. The wings tilt slowly (banking left, level, banking right, level) with one lazy flap in frames 5 and 6.
Dark charcoal with a dark blue-violet outline, no pure black. The body stays at the center of the cell.
Format: one single row of 8 frames, evenly spaced, on a wide image (about 3:1, like the attached sheet). 8 frames in
equal invisible cells (each cell has aspect 32:24), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: neutral soft daylight from the upper left, medium contrast (the piece will be re-tinted for each stage).
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 2. `cenarios/comum/folhas/garca.png`

Garça branca voando para a esquerda (passarela).
Tamanho final: **40x32 por quadro, 8 quadros**. Pedir: imagem larga 3:1, 1 fileira de 8 quadros. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. One white egret flying to
the left, strict side view: neck folded in an S, long dark legs trailing behind, yellow bill, slow full wing beat
cycle (wings up, mid, down, mid). The body stays at the center of the cell.
Format: one single row of 8 frames, evenly spaced, on a wide image (about 3:1, like the attached sheet). 8 frames in
equal invisible cells (each cell has aspect 40:32), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: neutral soft daylight from the upper left, medium contrast (the piece will be re-tinted for each stage).
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 3. `cenarios/comum/folhas/pombo.png`

Pombo voando para a direita (praça).
Tamanho final: **24x20 por quadro, 8 quadros**. Pedir: imagem larga 3:1, 1 fileira de 8 quadros. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. One grey pigeon flying to
the right, strict side view, fast wing beat cycle (up, mid, down, mid, twice). Grey-blue body, darker wing bars, tiny
hard highlight. The body stays at the center of the cell.
Format: one single row of 8 frames, evenly spaced, on a wide image (about 3:1, like the attached sheet). 8 frames in
equal invisible cells (each cell has aspect 24:20), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: neutral soft daylight from the upper left, medium contrast (the piece will be re-tinted for each stage).
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 4. `cenarios/comum/folhas/pombos_chao.png`

Três pombos ciscando (praça, na frente; Maria Fumaça, na viga).
Tamanho final: **64x12 por quadro, 8 quadros**. Pedir: 1536x1024, grade 2 colunas x 4 linhas. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. Three small pigeons
standing on a straight line, strict side view: one pecks the ground twice, one bobs its head and takes one step and
steps back, one ruffles its wings. Grey-blue bodies, very small and simple. Feet on the bottom edge in every frame.
Format: a grid of 2 columns x 4 rows on a 1536x1024 image, reading order left to right, top to bottom. 8 frames in
equal invisible cells (each cell has aspect 64:12), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: neutral soft daylight from the upper left, medium contrast (the piece will be re-tinted for each stage).
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 5. `cenarios/comum/folhas/cachorro.png`

Vira-lata caramelo deitado, abanando o rabo.
Tamanho final: **48x28 por quadro, 8 quadros**. Pedir: 1536x1024, grade 2 colunas x 4 linhas. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. One generic
caramel-colored mixed-breed street dog lying on the ground like a sphinx, strict side view, facing right: it wags its
tail left and right, lifts its head, twitches one ear, pants with the tongue out, lowers the head again. Belly fixed
on the bottom edge in every frame.
Format: a grid of 2 columns x 4 rows on a 1536x1024 image, reading order left to right, top to bottom. 8 frames in
equal invisible cells (each cell has aspect 48:28), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: neutral soft daylight from the upper left, medium contrast (the piece will be re-tinted for each stage).
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

#### 6. `cenarios/comum/folhas/ciclista.png`

Ciclista genérico pedalando para a direita, com sacola no guidão.
Tamanho final: **72x72 por quadro, 8 quadros**. Pedir: imagem larga 3:1, 1 fileira de 8 quadros. Fundo: magenta #FF00FF.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw an animation sheet of ONE stage element for a 2D fighting game, no characters fighting. One generic cyclist
riding an old plain bicycle to the right, strict side view, full pedaling cycle over the 8 frames (legs alternate,
wheels show rotating spokes), a plain shopping bag hanging from the handlebar swinging slightly. Cap, plain t-shirt,
shorts, flip-flops; simple face with no likeness to any real person; no brand, no text. Both wheels touch the bottom
edge and the bicycle stays at the same place in every frame (riding in place).
Format: one single row of 8 frames, evenly spaced, on a wide image (about 3:1, like the attached sheet). 8 frames in
equal invisible cells (each cell has aspect 72:72), no cell borders, no numbers. The element has the same size and the
same anchor position in every cell and never leaves its cell. Seamless loop: frame 8 flows back into frame 1, with
small smooth changes between neighboring frames.
Background: flat pure magenta (#FF00FF) everywhere outside the drawing, hard edge, no shadow, no glow, no gradient on
the background, and that background color is not used inside the drawing.
Art style: hand-pixeled 1990s arcade fighting game background art, the same visual family as the attached character
sprite sheet (the attachment is ONLY a style reference for pixel size, outline and shading: do not draw that
character). Big chunky square pixels on a regular grid, hard edges, no anti-aliasing, no blur, no dithering, no noise,
no photo texture, no smooth gradients (a gradient is 3 to 5 flat bands). Forms shaded in 2-3 large flat planes. Short
color ramps with shifted hue. 1-pixel colored outlines, never pure black. Slightly lower contrast and saturation than
the character sprite, so the fighters stand out in front.
Light: neutral soft daylight from the upper left, medium contrast (the piece will be re-tinted for each stage).
Original drawing, not copied from any existing game or photo. No fighters, no characters other than what is described,
no text, no letters, no numbers, no logos, no brand names, no signs, no watermark, no border, no frame, no UI.
```

## 7. O que não foi verificado e o que vem depois

- **Nenhuma imagem foi gerada.** Não se sabe ainda se o ChatGPT respeita a área pedida, a vista reta, as bordas que
  repetem e os 8 quadros no mesmo lugar; o lote piloto existe para medir isso.
- **A conversão não existe.** Falta escrever a ferramenta que recorta pela cor de fundo, reduz para o tamanho final,
  quantiza e fatia as folhas (sugestão: `ferramentas/arte_cenario.py`), e o script de cada cenário que desenha as luzes
  por código e grava o `cenario.json`. Quando existirem, o passo a passo entra em [`cenarios.md`](cenarios.md).
- **Posições e tamanhos são de prancheta:** foram calculados pelas medidas do `cenarios.md`, sem prévia nem motor. A
  prévia do gerador (`--previa`) e o filme na sandbox decidem os ajustes.
- **Recursos do motor ainda não provados que este projeto usa:** camada somada com velocidade e repetição ao mesmo tempo
  (neblina), `VelSet` em diagonal com ida e volta (pedestres), várias cópias da mesma folha fora de fase, `reflexo` fraco
  no piso. Se algum falhar, o elemento vira folha de quadros ou sai.
- **Lugares:** tudo o que está em "Para o Alisson confirmar". Além disso: perfil, rodas e traseira da locomotiva não
  foram vistos (desenho completado com máquina genérica da época); a margem sul da passarela só foi vista de longe e por
  satélite; a vista do rio a partir da estação e a partir do Cristo vem do mapa, não de foto; fotos de 2026 de nenhum
  dos quatro lugares foram encontradas.
