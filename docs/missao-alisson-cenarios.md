# Missão para o Alisson: cenários animados, Katiara e tela de escolha de mapa (2026-11-14)

Pedido do Breno. Siga as regras de sempre (`docs/como-trabalhar.md`, estilo arcade, Blender só anima o desenho, nada 3D).
Complementa as missões de 2026-11-13 e a issue #34 (tirar os cenários de exemplo do IKEMEN).

## 1. Cenário Katiara

O que o Breno descreveu do lugar:

- É uma **boca de fumo** da Katiara, um ponto de rua, onde **os caras ficam de guarda armados**.
- **Todo mundo faz o sinal do 7** com a mão. O 7 e a sigla "KT" são a marca do lugar.
- Da missão anterior: **muro cheio de números 7 e da sigla "KT" pichados**.

Como montar:

- Os figurantes ficam **no fundo**, parados de guarda ou fazendo o sinal do 7, animados em pixel (respirando, trocando
  o peso, mexendo a cabeça, um ou outro fazendo o 7 de tempo em tempo). Ninguém aponta arma para a luta nem atira: é
  ambientação, não tem violência acontecendo no fundo.
- Se o ChatGPT recusar desenhar gente armada, faça os figurantes em contraluz/silhueta ou com a arma baixa e pouco
  detalhada; o importante é o clima do lugar e o sinal do 7.
- **O resto do mapa você cria**, seguindo o padrão das fotos e da pesquisa de Nazaré que já estão em
  `docs/arcade/cenarios_nazare.md` (branch `cenarios`): casas de rua do Recôncavo, fios, laje, comércio pequeno,
  paleta e luz no mesmo estilo dos outros mapas. Escolha a hora do dia que não repete as dos outros (noite já é da
  Maria Fumaça; o projeto usa entardecer no Cristo, manhã na praça e amanhecer na passarela).
- Sem marca real (loja, bebida, time) em placa nem em parede.
- **Música:** `Nazafights - Cenario Katiara` está no Suno da conta do Breno (2 versões, instrumental, metal 8-bit com
  trap e pagodão sombrio, sirene ao longe). Quando o Breno escolher e gravar, entra em `musicas/originais/` como as
  outras, com as mesmas regras de loop da issue #33.

## 2. Todos os mapas animados

- **Todo cenário tem animação**, como a Maria Fumaça (`cenarios/maria_fumaca/`, `ferramentas/gerar_cenario.py`,
  `ferramentas/animar_cenario.py`).
- **Cada um com elementos próprios**, sem repetir os da Maria Fumaça. Exemplos: Cristo com nuvens, holofote, pássaros e
  gente subindo a escada; praça com pombos, feirante, carro passando; passarela com o rio, barco, gaivotas e neblina
  andando; Katiara com os figurantes do item 1, pipa no céu, roupa no varal, moto passando.
- Os figurantes são pixel animado; o Blender só deforma o desenho.

## 3. Tela de escolha de mapa (nada de mapa aleatório)

- Depois de escolher os lutadores, abre **uma tela para escolher o mapa**, em todos os modos.
- **O mapa nunca é sorteado.** Tire o aleatório da lista e não deixe o modo Arcade sortear.
- A tela segue o layout Nazafights (`motif/nazafight/`, `ferramentas/gerar_layout.py`): prévia do cenário, nome e a
  música dele. Entram só os mapas de Nazaré e o de teste azul (`stage0-720`, issue #34).
- No IKEMEN a escolha de cenário é ligada pelo `[Select Info]` do `system.def` (opções `stage.*`); confira no motor que
  ela aparece em Versus e no Arcade.

## Ao terminar

Rode o robô e abra cada mapa no jogo, filme uns segundos de cada um e confira a animação quadro a quadro. Suba na `mugen`
e anote no `LOGBOOK.md`.
