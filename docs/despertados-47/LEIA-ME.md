# Agarrão e poder de longe dos despertados (issue #47)

Pedido do Breno em 2026-11-14: todo despertado ganha um **agarrão com a cara da forma** e um **poder foda de soltar de
longe**, com efeitos do Blender na cor da forma e sons próprios. Aqui estão o Pengaró, o Gutto e o CK. O Hazak (Diabo
Loiro, com a rajadona de ki das trevas) fica na issue #44 e o Raiclaven (a parceira ataca por ele) na #43.

## Terceira versão: o Diabo Loiro como régua (resposta do Breno na #44, 2026-11-14)

O Breno disse que o Hazak "ficou absurdo" e quer esse nível nos outros. O que mudou aqui, olhando a rajadona e o
agarrão de fogo do Diabo Loiro lado a lado com os nossos:

- **Cor com profundidade:** cada forma agora tem 8 tons, do preto ao branco passando pela cor dela, em vez de bola
  clara com contorno. Tudo passa pelo pixelfx puro (sem o halo borrado da versão anterior).
- **Poder de longe = torrente:** miolo branco quente, casca na cor da forma e fumaça preta borbulhando nas bordas,
  com faíscas. Ela **atravessa o oponente** e segue pela tela (3 acertos de 42, um estouro em cada), nasce curta
  na mão e estica.
  - Pengaró: bola de sombra violeta na ponta e três correntes correndo junto.
  - Gutto: **o garanhão da aura sai correndo** com a torrente de raio atrás. A aura some enquanto ele corre.
  - CK: arcos de som em fila na ponta da torrente verde.
- **Gutto ganhou a aura no jogo:** o garanhão gigante de raio vermelho (`sprites/gutto/aura`) estava desenhado mas
  não aparecia na luta. Agora fica atrás dele no Despertar, como as asas do Diabo Loiro, com as crateras em brasa no chão.
- **Agarrão:** cada pancada solta um estouro da forma no ponto do golpe (era só a tremida). Os raios do Gutto
  ficaram finos e vermelhos, como os da aura. O estouro final ficou menor, para não tapar os dois lutadores.

GIFs: `agarrao_<lutador>.gif` e `poder_<lutador>.gif`. Vídeos: `video_<lutador>.mp4`.

## Segunda versão (resposta do Breno de 2026-11-14 na #47)

O Breno achou a primeira versão fraca e pouco sombria, e o cavalo do Gutto feio. Dessa rodada continuam valendo: o
cavalo do poder é o garanhão da aura; na carga o mundo para e escurece (`SuperPause`), o lutador ganha rastro e a
tela treme; no acerto congela, o oponente pisca na cor da forma e a tela treme forte; no agarrão o fundo escurece e
o final congela com clarão. A comparação pixelfx x render direto (`comparacao.png`) é dessa rodada: na terceira
versão ficou o pixelfx puro com 8 tons, que é o caminho do Diabo Loiro.

## O que entrou

| Lutador | Agarrão da forma (y ou b com → ou ← colado, no Despertar) | Poder de longe (↓ → ↓ → + soco, no Despertar) |
|---|---|---|
| Pengaró endiabrado | **Algema das Sombras**: correntes de sombra sobem do chão e enrolam o oponente enquanto ele apanha (palma torta, revolta de corrente, mão de chão, roda da possessão); no final os elos voam | **Maré das Correntes**: torrente de sombra violeta com fumaça preta e três correntes, atravessa a tela |
| Gutto despertado | **Coice do Garanhão**: raios caem em cima do oponente preso; o coice final solta ferraduras de raio | **Estouro do Garanhão**: o garanhão de raio vermelho da aura sai correndo, com torrente de raio atrás |
| CK despertado | **Paredão na Cara**: as caixas de som estouram no oponente a cada pancada; o final é um estrondo | **Paredão no Talo**: arcos de som em fila na ponta de uma torrente verde de fumaça |

- Agarrão: 3 pancadas + final, 140 de dano (o básico tem 120), mesma pega e mesmo escape do agarrão segura-e-bate.
  Fora do Despertar o agarrão continua o básico.
- Poder: carga na mão, torrente grande que atravessa o oponente, 3 acertos de 42 que derrubam, um por vez na tela,
  sem custo de barra (é lento para sair, dá para punir de perto).
- Sons das formas (#46): corrente no Pengaró, relincho, galope e coice no Gutto, paredão no CK.
- Lista de golpes (`movelist.dat`) com as duas entradas novas em "Exclusivos do Despertar".

Folhas: `efeitos_<lutador>.png`. Vídeos: `video_<lutador>.mp4` (motor de verdade, na nuvem; cada lutador desperta,
dá o agarrão no Hazak e solta o poder). Tira: `luta.png`.

## Como refazer

```bash
bash ferramentas/efeitos_pixel/preparar_nuvem.sh && source ~/.nazafight/ambiente.sh
"$NAZAFX_PY" ferramentas/despertados_47_blender.py     # renderiza os efeitos (~5 min na nuvem; --comparar grava os caminhos puros)
python3 ferramentas/despertados_47.py                  # liga no .sff/.air/.cns/.cmd e no movelist (roda de novo sem duplicar)
python3 ferramentas/filmar_47.py saida.mp4 --p1 gutto  # filma o agarrão e o poder no motor
```

Ordem num lutador regerado: gerador, `parry.py`/`efeitos.py`, depois `despertados_47.py` (os outros regravam o `.sff`).
O `gerar_sons.py` não mexe nos estados 4700, 4710 e 4750; os sons deles vêm do `despertados_47.py`.

## Testado

- Robô na nuvem (`testar_pengaro.py --linux`) nos três: Pengaró 190, Gutto 185, CK 228 verificações, 0 falhas.
- Vídeo no motor: agarrão pega, segura, bate e arremessa com o efeito da forma; poder sai, acerta e derruba.

## Sugestões para depois

- Vapor da narina do garanhão (camada `vapor` da aura do Gutto, na frente): ficou de fora, porque é preso à pose
  parada; dá para ligar só quando ele está em pé.
- Cavalo correndo de verdade: o garanhão da aura está empinado (é o desenho aprovado); se o Breno quiser ele
  galopando, dá para dobrar as patas com o rig da aura (`aura_blender/gutto_aura.py`).
- Pose própria: hoje o poder usa a pose de lançar da Mão de Sombra (3400) e o agarrão usa quadros dos golpes da
  forma. Uma folha `e_poder` e `e_algema` por lutador deixaria mais marcante.
- Gbzin: quando ele entrar na `mugen`, o motoboy pede o mesmo par (CFG em `despertados_47.py`).
- A CPU quase não usa ↓ → ↓ →; dá para pôr uma chance na IA quando ela estiver longe.
