# Pedido para o Codex: sprite-base do Pengaró com a garrafa de whisky

**Por que:** hoje a garrafa é colada por código em cima dos desenhos antigos. Como nenhum desenho tem a mão
fechada em volta de um gargalo, o código só adivinha onde está a mão de trás: em vários quadros a garrafa fica
boiando do lado do corpo, no cotovelo ou some. O certo é a garrafa **desenhada junto** com a mão. Para isso
primeiro precisamos de uma folha-base que mostre como ele segura a garrafa, e depois todas as folhas usam ela de
referência.

**Regra fixa do Breno:** sprite desenhado estilo SNES / arcade dos anos 90, igual às folhas que já existem.
Nunca 3D pixelizado.

## Passo 1: gerar a folha-base

Use a ferramenta de imagem com a folha `sprites/pengaro/quadros/folhas/soco.png` anexada como referência, com
este prompt:

> Generate ONE image with your image generation tool. Do not write code and do not edit any file.
>
> The attached sprite sheet shows the exact character and art style to keep: same man, same face, hair, skin,
> muscles, white capoeira pants with green and yellow side stripes, yellow cord belt, teal sash, the same dark
> green shin guard on the same leg, barefoot. Same detailed hand-drawn 16-bit SNES / 90s arcade pixel art,
> never a 3D render.
>
> NEW: he is a heavy drinker and always holds a whisky bottle: amber glass, black screw cap, plain cream label
> with NO brand and NO text, about the size of his forearm. He grips it firmly BY THE NECK in his BACK hand
> (the hand farther from the viewer), fingers clearly wrapped around the neck, the bottle body pointing down
> and slightly back, so it is obviously in his hand and never floating.
>
> Layout: one single row of 8 frames in 8 equal-width cells, side view, always facing right, same scale as the
> attached sheet, feet on the same ground line. Each figure inside its own cell, never touching the next.
> Flat solid magenta background (#FF00FF), no shadow, no ground, no text, no numbers, no borders, no effects.
>
> The 8 frames are a model sheet of how he holds the bottle: 1 ginga guard stance, bottle low in the back hand;
> 2 walking forward; 3 throwing a straight punch with the FRONT hand while the back hand keeps the bottle at
> the hip; 4 high kick, bottle swung back for balance; 5 deep crouch, bottle hand resting on the knee;
> 6 blocking with the front forearm, bottle held behind; 7 taking a swig, bottle tilted up at the mouth;
> 8 jumping with knees tucked, bottle held tight.

Salve como `sprites/pengaro/quadros/folhas/base_whisky.png`. Confira: a garrafa está **na mão** (dedos em volta
do gargalo) nos 8 quadros, sem marca nem texto, mesma cara e roupa. Se não estiver, gere de novo.

## Passo 2: refazer as folhas usando a base

O `ferramentas/gerar_folhas.py` já usa `base_whisky.png` como referência quando ela existe.

```powershell
python ferramentas/gerar_folhas.py --todas
```

Depois recorte cada folha com `ferramentas/recortar_quadros.py` (âncora de `FOLHAS_PENGARO`) e refaça a que vier
com a garrafa solta, sem garrafa ou com figura cortada.

## Passo 3: avisar o Claude

Suba as folhas num PR para a `mugen` com `[para-claude]` na descrição: "folhas com whisky prontas, tirar a garrafa
colada por código". O Claude desliga a garrafa colada (`com_whisky` em `gerar_pengaro.py`), liga as folhas novas
e confere quadro a quadro.
