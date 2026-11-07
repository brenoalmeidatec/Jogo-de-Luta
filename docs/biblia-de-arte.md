# Bíblia de arte

O que mantém os lutadores com cara de um jogo só. Vale para todo lutador novo e para qualquer folha refeita. As regras de
jogo ficam em [`regras-dos-lutadores.md`](regras-dos-lutadores.md); o jeito de produzir, em
[`como-trabalhar.md`](como-trabalhar.md).

## Estilo

- Sprite desenhado de SNES/arcade dos anos 90, com contorno escuro e sombreado em blocos. Nunca 3D pixelizado nem
  render suave.
- Proporção de KOF: escala 1 no `.cns`, figura em pé com cerca de 110 de 180 de altura de tela.
- Vista de lado, virado para a direita, pés no chão quando o golpe não sai do chão.
- Folha de 8 quadros em fila, células iguais, figura inteira dentro da célula, fundo magenta `#FF00FF` liso, sem faixa
  branca ou cinza, sem texto e sem sombra no chão.
- Toda folha alinhada pelo **centro do tronco** no eixo do lutador (`animar_folha.py`). As caixas de golpe são centradas
  no eixo, então o tronco no eixo faz golpe e desenho baterem.
- Marca e texto proibidos em garrafa, lata ou roupa.

## Pengaró

| | Normal | Endiabrado (Despertar) |
|---|---|---|
| Pele | morena, tom médio (matiz perto de 23°) | quase preta, relevo roxo escuro; corpo inteiro, sem fumaça no corpo |
| Olhos | normais | violeta brilhante |
| Calça | branca, listras verde e amarela | carvão, barra rasgada, brasas violeta |
| Faixa | teal, cordão amarelo | cordão amarelo brilhando |
| Perna | caneleira verde escura | algema de corrente partida no tornozelo |
| Mão de trás | garrafa de whisky âmbar, rótulo creme | livre, garra; algemas nos pulsos |
| Efeitos | whisky: âmbar e dourado (`WHISKY` em `gerar_pengaro.py`) | sombra: violeta e preto (`SOMBRA`, `SOMBRA_ESCURA`) |

Referências na biblioteca do ChatGPT: "Socos" (normal) e "Oito Movimentos" (endiabrado). Meça o matiz da pele das folhas
novas: acima de 26° ele está desviando para o amarelo.

## Efeitos

- **Sem pixelfx no Pengaró** (o Breno não gostou). Efeito é desenhado como lutador: folha de 8 quadros no ChatGPT, estilo
  pixel art de arcade, **fundo verde `#00FF00`** (o roxo da sombra some no magenta), salva como
  `sprites/<lutador>/quadros/folhas/fx_<nome>.png`. `python ferramentas/efeitos_folha.py <lutador>` recorta, põe na escala
  do jogo e cria 2 quadros do meio por intervalo (fluxo óptico): 8 desenhos viram 22, bem animados.
- Pixel opaco, sem mistura de cor: soma de dourado sobre o palco azul vira rosa.
- Cada forma tem a sua cor e o seu efeito (`FX_PENGARO` em `gerar_pengaro.py`). A faísca de acerto é do motor e não passa
  pela troca do Despertar: o HitDef escolhe a do endiabrado pelo `var(20)` (ação + 30).
- O efeito de golpe nasce no elemento em que a caixa de golpe liga, na caixa do golpe. Nada de efeito solto no meio da tela.
- Nada de escudo em grade: parece rede de futebol.
- Endiabrado com corpo inteiro, sem buraco nem membro solto; a sombra que se mexe é a aura (efeito à parte). Anexe a
  referência em **toda** folha: sem isso, em 30 folhas seguidas ele virou marrom.

## Lutador novo

1. Defina na ficha a tabela de cima: pele, roupa, objeto, cor dos efeitos de cada forma.
2. Gere a folha-referência e guarde na biblioteca do ChatGPT com um nome fácil de buscar.
3. Escolha a rampa de cor dos efeitos dele, diferente das que já existem.
