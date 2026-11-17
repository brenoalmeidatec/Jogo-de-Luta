# Montador do boneco de peças

Pedido do Breno em 2026-11-17. Página no navegador para montar as poses-chave de um golpe com as peças do kit, no olho,
em vez de digitar ângulos no código. É o passo 4 da [missão do boneco de peças](missao-alisson-boneco-de-pecas.md) com
interface.

```bash
python ferramentas/montador.py                  # Pengaró
python ferramentas/montador.py --lutador gbzin  # Gbzin
python ferramentas/montador.py --lutador gutto  # Gutto
```

Abre `http://127.0.0.1:8765` no navegador. Precisa só de `pillow numpy opencv-python-headless`, os mesmos de sempre.

## Como funciona

- Cada quadro é desenhado pelo **mesmo código do piloto** (`piloto_firme.desenhar` no Pengaró, `gbzin_pecas.desenhar`
  no Gbzin, `boneco_gutto.desenhar` no Gutto): RotSprite em cor cheia, sobra nas juntas, pés retos no chão. O que aparece na página é o que vai para a
  pasta. Conferido: as poses-chave do chute alto do piloto saem pixel a pixel iguais.
- **Abrir…** carrega um golpe que o piloto já montou (`quadros_pecas_hd/poses.json` + `tempos.json`) para ajustar, um
  projeto gravado antes, ou um golpe novo partindo da guarda.
- **Arrastar um osso** gira a peça na junta. `Shift` + arrastar move (no quadril, o corpo todo). Setas `←` `→` giram
  0,5° (com `Shift`, 5°), `↑` `↓` trocam de osso, `PageUp` `PageDown` trocam de pose, `Ctrl+Z` desfaz, `Ctrl+S` grava,
  espaço toca.
- **Desenho** troca a variante da peça (punho, braço esticado, perna em câmara ou esticada, cabeça de esforço).
- **Casca de cebola:** a pose anterior em azul e a próxima em laranja, por baixo.
- **Esconder e camada (por pose):** no painel do osso, "esconder nesta pose" tira a peça (a canela leva o pé junto) e
  "camada" manda a peça para trás do corpo ou para a frente de tudo. Ex.: no chute, a mão da frente vai para trás.
- **Pintar, apagar e pegar cor** (`B`, `E`, `I`; `[` `]` mudam o pincel): pintam **na peça do osso escolhido**, antes
  de girar, então a pintura gira e anda junto com a peça e vai para os quadros do meio daquela pose. Fica guardada na
  pose (`"ret"`), só para aquele desenho da peça; "Limpar pintura" desfaz. O pincel 3 é 1 pixel do jogo.
- **Régua:** acusa a junta que escorregou mais de 5% do osso. As peças são sempre o mesmo desenho, então o osso em si
  não estica.
- **Caixa de golpe:** o `Clsn1` do golpe no 3x, relativo aos pés, aparece em vermelho na pose marcada como "bate".
- **Ticks** de cada pose e **tocar** a 60 por segundo. **Ver 1x** mostra como o jogo mostra.
- **Com vida** grava com os quadros do meio, o impacto segurado e o atraso da cabeça (`vida_pecas.py`, igual ao piloto).

## O que grava

Nada no jogo. Os quadros vão para `sprites/<lutador>/quadros_montador_hd/<golpe>/` (3x, 1080x780, pés em 540,660) e
`sprites/<lutador>/quadros_montador/<golpe>/` (1x), com `poses.json` e `tempos.json` no formato do piloto. O projeto
editável fica em `sprites/<lutador>/montador/<golpe>.json`. Ligar no gerador continua com o Alisson.

## Lutador novo

O montador lê `OSSOS`, `CAMADAS` e a função de desenho de cada lutador na classe `Lutador` de
`ferramentas/montador.py`. Lutador novo com kit de peças ganha ali um `elif` com o leitor de kit e o `desenhar` dele.

## Primeiro uso: chute alto do Pengaró (2026-11-17)

`sprites/pengaro/montador/chute_alto.json`, gravado em `quadros_montador_hd/chute_alto/`. Correção pedida pelo Breno:
nas duas poses de perna esticada a mão da frente ficava solta na frente da perna (foi para trás do corpo) e a perna de
apoio tinha a mesma listra verde e amarela da perna que chuta, parecendo duas pernas direitas (a listra saiu da coxa de
trás e do quadril abaixo da faixa, como no desenho original). Antes e depois: original, piloto e consertado em
`docs/boneco-pecas/montador_chute_antes_depois.png`.
