# Hazak: pedidos do Breno de 24/11 (#32)

Recado do Breno na #32 (24/11 16:14). O bug do despertado entre rounds foi feito por outra thread (`1bf18911`).

## O que entrou

| Pedido | O que foi feito | Ferramenta | Vídeo |
| --- | --- | --- | --- |
| Ginga (parado) entortando a perna | Os 7 desenhos originais da ginga voltam a ser a base (pernas e cintura como foram desenhadas). A cabeça é sempre a do kit (cara igual em todo quadro). Quadros do meio: só o tronco anda 1/3 e 2/3 do caminho até o desenho seguinte, por cima das pernas do desenho. Régua do corpo 0, robô de defeitos 0. | `ferramentas/hazak_do_original.py` | `hazak_parado.mp4` |
| Diabo Loiro estático e simples | Ginga do demônio respirando (tronco sobe 1 px do jogo por cima das pernas do desenho, trocando entre os desenhos parecidos, com a garra flexionando no meio). 14 golpes (em pé, agachado e correntes) com recuo e afundada no preparo, corpo avançando no bote (mais no forte), rastro de fogo do membro que bateu no 1º tick do contato e volta em dois tempos. Tempo, caixas e tick do contato iguais. | `ferramentas/diabo_vida.py` | `diabo_vida.mp4` |
| Agarrão do Hazak base incompreensível | Karatê: a mão da frente pega na gola e segura; o braço de perto solta uma rajada (três socos na tela a cada pancada de dano, rosto e estômago), com rastro dos socos anteriores e o punho nítido + vento no contato; no fim solta a gola, prepara e dá o soco reto inteiro, e o oponente voa para a frente (segurando ←, continua jogando por cima, para trás). O oponente fica preso na mão da gola (distância 60 em vez de 30). O Diabo continua com o agarrão dele. | `ferramentas/agarrao_karate.py` | `hazak_agarrao.mp4`, `agarrao_no_jogo.mp4` (no motor, com o oponente) |
| Ideia do soco rápido (borrão ou vento) | Testei no jab (200): hoje x borrão x só vento. **Opinião: vale o borrão** em soco fraco e rajada; "só vento" esconde o alcance e o jogador não entende o que bateu; golpe forte continua com o desenho inteiro. Entrou na regra (seção 7 da `regra-de-criacao-de-personagem.md`) e o jab do Hazak já está com borrão no jogo. | `ferramentas/borrao.py` | `jab_borrao_teste.mp4` (e `_lento`), `hazak_jab.mp4` |

Robô de luta do Hazak: 327/0 antes e 327/0 depois (inclui os dois agarrões segura-e-bate e os 7 golpes do demônio).

## Ordem para refazer (se o Hazak for regenerado)

```
python3 ferramentas/gerar_hazaki.py              (se precisar)
python3 ferramentas/ligar_pecas.py hazaki        (golpes do kit)
python3 ferramentas/hazak_do_original.py && python3 ferramentas/ligar_pecas.py hazaki parado
python3 ferramentas/borrao.py jab && python3 ferramentas/ligar_pecas.py hazaki soco
python3 ferramentas/agarrao_karate.py && python3 ferramentas/ligar_pecas.py hazaki agarrao_karate agarrao_karate_pega --pasta quadros_karate_hd --grupo 49000 && python3 ferramentas/agarrao_karate.py --binds
python3 ferramentas/diabo_vida.py && python3 ferramentas/ligar_pecas.py hazaki --de diabo_vida --pasta quadros_hd --grupo 62000
```

O `firme.py hazak parado` e o `firme.py hazak soco` refazem a ginga e o jab do jeito antigo: rode os passos acima
depois dele.

## Sugestões para depois

- **Expressões do Hazak:** o kit só tem uma cabeça. Dá para desenhar no ChatGPT (Browser 2) a cabeça do parado com
  foco, esforço (kiai), dor e riso, no mesmo tamanho, e usar no agarrão (kiai no soco final) e nos golpes do desenho.
- **Diabo:** os golpes no ar (4600) e os direcionais (4210) ainda não têm folha; quando chegarem, rode o
  `diabo_vida.py` de novo. Cabelo e rabo balançando de verdade pediriam o kit do demônio (`kit_diabo.py`) na paleta
  do jogo.
- **Borrão em outros lutadores:** jab do CK e do Gutto e as rajadas dos agarrões do Pengaró são bons candidatos.
- **Pernas nos golpes do kit:** o soco e o soco reto do Hazak ainda dobram a perna pela malha do kit (agachando mais
  que a ginga). Pela regra do desenho original, vale refazê-los como a ginga, se o Breno reclamar.
