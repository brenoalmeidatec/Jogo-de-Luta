# Missão para o Alisson: auras presas ao corpo, efeitos em pixelfx, anatomia e animação no nível do Melty Blood (2026-11-14)

Pedido do Breno, depois de ver as entregas de hoje (#44, #47 e efeitos no nível do Hazak). Siga as regras de sempre
(`docs/como-trabalhar.md`, `docs/regras-dos-lutadores.md`, estilo arcade). A issue desta missão é a de referência.

**Ordem:** 1, 2 e 3 primeiro (são erros), depois 4 (estilo de animação) e 5 (mecânicas). Poste vídeo antes de juntar.

## 1. Auras e asas têm de seguir o corpo

Hoje vários efeitos ficam parados no lugar enquanto o lutador se mexe. Exemplo do Breno: **o Hazak endiabrado agacha ou
cai e as asas continuam no mesmo lugar**, no ar.

- Toda aura, asa, coroa, garanhão do Gutto, correntes do Pengaró, paredão do CK e o que mais for preso ao corpo **acompanha
  o lutador em todo estado**: agachar, pular, cair, levar golpe, ser arremessado, levantar, andar, correr, agarrão,
  parry, vitória e derrota.
- Ancore cada camada num ponto do corpo (costas, ombros, cabeça) **por ação**, não numa posição fixa: a altura do ponto
  muda no agachado, no pulo e no chão. Onde precisar, uma tabela de deslocamento por ação/quadro.
- No chão (caído) as asas deitam ou recolhem; agachado elas descem junto; no ar seguem o corpo e a rotação.
- Robô: para cada lutador endiabrado, passe por todos os estados e confira que a aura fica dentro de uma distância do
  ponto de âncora. Filme o Hazak agachando, pulando, caindo e levantando.

## 2. Efeitos de acerto: refazer em pixelfx, nada de imagem do ChatGPT

Vários efeitos de ataque, principalmente **os de quando o golpe acerta**, ainda são **imagens geradas no ChatGPT**. O
Breno quer **todos refeitos com o pixelfx**:

- Faísca de acerto, faísca de defesa, estouro de especial, estouro de super, rastro de golpe, poeira, parry e agarrão.
- Feitos no pixelfx em pixel art de verdade, na cor de cada lutador e forma, com a animação curta e seca de jogo de
  luta. **Sem** a faísca pronta de círculo preto com raios (a "rede de futebol").
- Mantenha o tamanho, o peso, a tremida e o clarão que você fez hoje no nível do Hazak; muda a origem do desenho.
- Faça uma lista de todo efeito que hoje vem do ChatGPT e marque cada um quando trocar. Poste a lista na issue.

## 3. Erros de anatomia

O Breno viu **vários erros de anatomia** nos quadros (braço, mão, perna e tronco tortos ou trocando de tamanho no meio
do golpe). Revise **todos os quadros de todos os lutadores, nas duas formas**, contra a regra de anatomia de
`regras-dos-lutadores.md`, e redesenhe os que estiverem errados. Atenção especial aos quadros novos do Diabo Loiro e aos
20 golpes que usam folha aproximada. Poste uma folha de contato antes e depois.

**Proporção fora de controle (pedido do Breno, junto com este item):** em vários momentos o lutador **fica gigante ou
pequeno demais** de um quadro para outro, **principalmente ao agachar**. Cada lutador tem de manter a mesma escala em
toda ação (mesma altura de cabeça, largura de ombro e tamanho de mão e pé; agachado só fica mais baixo, nunca encolhe
nem cresce). Meça a altura da cabeça e dos ombros em todos os quadros de cada ação, nas duas formas, compare com o
parado e corrija o que passar de uns 3%. Ponha essa medida no robô para não voltar.

## Atualização do Breno: são DOIS jogos

Depois de ler esta missão, o Breno decidiu: ele quer **dois jogos**, com os mesmos lutadores, cenários e músicas:

| Jogo | Estilo | O que é |
|---|---|---|
| **Nazafights Arcade** | arcade igual KOF | o jogo de hoje (`chars/`, `motif/nazafight/`), polido: sprites, ritmo e mecânicas de arcade anos 90 |
| **Nazafights Moderno** | Melty Blood, mais moderno | jogo novo com a animação fluida e as mecânicas dos itens 4 e 5 |

- Os itens 1, 2 e 3 (auras, efeitos em pixelfx, anatomia) valem para **os dois**.
- Os itens 4 e 5 (animação e mecânicas do Melty Blood) são do **Moderno**. O Arcade fica no estilo KOF, com o parry
  de `docs/parry.md`.
- **Estrutura sugerida** (decida e explique na issue): tudo na `mugen`, o Moderno em pastas próprias
  (`moderno/chars/`, `moderno/motif/`) reaproveitando cenários e músicas; o launcher instala os dois e cria dois
  atalhos ("Nazafights Arcade" e "Nazafights Moderno"), ou um menu de escolha na abertura. O robô roda nos dois.
- Os desenhos do Moderno são novos, feitos para a animação fluida, mas são os nossos lutadores com a mesma cara.

## Os dois com qualidade de jogo premium (de R$ 300)

O Breno quer que **os dois** pareçam um jogo que se compra por R$ 300. Isso quer dizer, no mínimo:

- **Zero erro visível:** nada piscando, cortado, fora do lugar, travando ou em inglês; música e som sem cortes secos.
- **Acabamento em toda tela:** abertura animada, título, menus com animação e som, transições entre telas, seleção,
  VS, tela de mapa, vitória com pose e fala, tela de continue, créditos.
- **Modos completos:** Arcade com chefe e final de cada lutador (imagem e texto curto), Versus, Treino com opções
  (mostrar caixas de golpe, dano, barra infinita, gravar o boneco), Assistir, Opções (controle de cada botão, volume
  de música e efeitos, dificuldade, tempo, tela cheia) e lista de golpes no pause.
- **Controle:** teclado e controle (joystick) configuráveis, resposta imediata, 60 quadros por segundo sem cair.
- **Mistura de som** equilibrada entre música, golpes e narrador.
- **Instalador e atualização** limpos (padrão do Breno: instala, atualiza, desinstala e preserva os dados).
- Antes de cada entrega, jogue como cliente: do título até zerar o Arcade com um lutador, e anote o que achou.

## 4. Animação no estilo do Melty Blood (Nazafights Moderno)

O Breno pediu para você **pesquisar o jogo Melty Blood** (French-Bread; principalmente *Melty Blood: Type Lumina* e
*Actress Again Current Code*): ele acha a estética, o jeito de lutar e a animação incríveis, e quer o Nazafights nesse
nível. Assista partidas e combos, veja como a animação funciona e **refaça a nossa animação nesse estilo**.

O que pegar dele (o jeito de animar, não o desenho):

- **Muitos quadros e fluidez:** golpe com antecipação, quadro de impacto, seguimento e volta, em vez de poucas poses
  paradas. Quadros de "smear" (borrão do movimento) nos golpes rápidos.
- **Movimento secundário:** cabelo, sobretudo, faixas, roupa e asas balançando e atrasando um pouco em relação ao corpo.
- **Impacto:** quadro de congelamento curto no acerto, faísca estilizada e fina, tremida leve e cor forte.
- **Pose de luta com atitude:** parado, andar e guarda com personalidade de cada um.
- **Ritmo rápido:** jogo veloz, ações curtas e fáceis de encadear.

**Regra importante:** é só referência de estilo. **Não copie sprite, personagem, efeito, música, cenário nem nada do
Melty Blood** (é de outra empresa e o nosso repositório é público). Todos os desenhos continuam nossos, dos nossos
lutadores, de Nazaré. Não suba no git vídeo, imagem nem quadro do jogo deles.

Comece pelo **Hazak** (base e Diabo Loiro) como piloto: parado, andar, os três normais, um especial e o parry. Poste o
vídeo; com o OK do Breno, leve para os outros.

## 5. Mecânicas: o que o Breno aprovou para entrar (Nazafights Moderno)

Destas ideias do Melty Blood, o Breno mandou eu escolher o melhor para o jogo e aprovar. **Aprovado:**

1. **Parry no estilo do Shield do Melty Blood**, substituindo o visual atual mas mantendo os comandos de
   `docs/parry.md` (→ + c em cima, ↓ + c embaixo):
   - janela curta e apertada; acertou, os dois congelam um instante com um **clarão** na cor do lutador e um som seco;
   - quem deu o parry pode **cancelar em qualquer golpe** logo em seguida (contra-ataque), e o oponente fica aberto
     (os 20 ticks de hoje continuam);
   - errou, fica exposto um pouco mais que hoje (o parry vira aposta, não botão de pânico);
   - a piada da forma base e o poder da forma endiabrada continuam, como cancelável.
2. **Parry durante o Despertar vira super-cena:** na forma endiabrada, um parry certo com a barra cheia solta um golpe
   final cinematográfico do lutador (como o "Last Arc"), usando a cena de transformação (#49) como base: tela preta,
   zoom e golpe.
3. **Combo em corrente:** fraco → médio → forte encadeiam por cancelamento (e o forte cancela em especial), igual para
   todos, para o jogo ficar rápido e fácil de combar.
4. **Dash no ar** (uma vez por pulo) para todos.

**Ficou para depois da 1.0** (não fazer agora): vida vermelha que regenera, estilos/"luas" diferentes por lutador e
pulo duplo.

Todas as mecânicas: robô conferindo e nota no `LOGBOOK.md` do que mudou no balanceamento.

## Ao terminar

Robô em todos os lutadores, vídeo de cada item na issue, suba na `mugen` e anote no `LOGBOOK.md`.
