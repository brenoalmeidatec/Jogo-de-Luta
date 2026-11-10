# Fila de geração arcade no ChatGPT

> Síntese do estudo arcade de 2026-11-10. Estilo, regras e pipeline em
> [`../biblia-de-arte.md`](../biblia-de-arte.md#estilo-arcade-anos-90); paleta, kit e problemas de cada lutador em
> `docs/arcade/<lutador>.md`. Nada aqui foi testado no motor.

## Como usar

1. **Um chat por personagem**, com o título indicado (`Pengaró — arcade`, `Gutto — arcade`, `Raiclaven — arcade`,
   `Hazaki — arcade`). Nunca misture dois lutadores no mesmo chat.
2. Em **toda** folha, anexe a referência do lutador (abaixo) e cole o prompt inteiro do bloco. Uma folha por mensagem.
3. Salve a imagem **exatamente** no caminho do título da folha (`sprites/<lutador>/quadros/folhas_arcade/<folha>.png`).
   Nada fica em Downloads. As folhas atuais em `quadros/folhas/` não são tocadas.
4. Antes de seguir para a próxima folha do mesmo lutador, a folha tem que passar no critério de aceite da
   [`biblia-de-arte.md`](../biblia-de-arte.md#estilo-arcade-anos-90): 8 quadros inteiros, magenta liso, mesmo chão,
   virado para a direita, personagem reconhecível ao lado da referência, matiz mediano da pele na faixa do lutador.
   Reprovou: gere de novo no mesmo chat, com a referência anexada.
5. Ordem: o lote 1 dos quatro lutadores, depois o lote 2, depois o 3. O lote 1 inteiro passa pelo pipeline
   (quantizar, Blender, `--meio`, `conferir_arte.py`, vídeo na sandbox, uma pessoa olhando) antes de abrir o lote 2: se o
   estilo não convencer nas 4 primeiras, o resto não vale a pena.
6. **Hazaki:** a linha dele só anda depois que o Breno decidir se ele vira rival com kit completo ou fica como boneco de
   teste, e o gerador dele precisa ler folhas (hoje recorta `karate.png`). Os prompts estão prontos para quando isso sair.

Referências:

| Lutador | Anexar em toda folha |
|---|---|
| Pengaró | a folha "Socos" da biblioteca do ChatGPT (forma normal) |
| Gutto | `sprites/gutto/quadros/folhas/referencia_idle.png` |
| Raiclaven | `sprites/raiclaven/quadros/folhas/referencia_ginga.png` |
| Hazaki | `sprites/hazaki/karate.png` só na 1ª folha (`parado`); aprovada, a `parado` nova vira a referência das outras |

Contagem:

| Lutador | Lote 1 | Lote 2 | Lote 3 | Total com prompt |
|---|---|---|---|---|
| Pengaró | 4 | 16 | 11 + fx_arco | 32 |
| Gutto | 4 | 15 | 11 | 30 |
| Raiclaven | 4 | 15 | 14 | 33 |
| Hazaki | 4 | 11 | 7 | 22 |
| **Total** | | | | **117** |

## Lote 1: as 4 folhas mais vistas de cada um

### Chat "Pengaró — arcade" — lote 1

#### `sprites/pengaro/quadros/folhas_arcade/parado.png`

Já existe em disco (10/11), ainda sem conferência. Gere de novo só se reprovar no critério.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: standing tall, capoeira ginga bounce, feet planted: frames 1 to 4 sink, frames 5 to 8 rise; frame 8 loops into frame 1. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/anda.png`

Já existe em disco (10/11), ainda sem conferência. Gere de novo só se reprovar no critério.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: guarded walk forward in the capoeira ginga, hands up in front of the chest, a full two-step cycle: frame 1 contact, front leg forward and rear leg back, 2 weight on the front leg, 3 rear leg passes under the body, 4 that leg reaches forward, 5 contact with legs swapped, 6 weight on the new front leg, 7 the other leg passes, 8 it reaches forward and flows back into frame 1; the body rises slightly on the passing frames, the pants fold at each step. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/soco.png`

**Refazer.** A versão em disco é a da piloto: falhou a regra 10 (punho -27%) e estala na volta. Este MOTION já corrige.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: standing tall, quick jab with the front fist: frame 1 stance with the same hands as the idle sheet, frame 2 the shoulder loads back, frame 3 small step in, frame 4 fist travels out, frame 5 contact: the fist is drawn 20% larger than in frame 1, shoulder thrust forward, torso turned showing the chest, frame 6 hold with the arm fully extended, frame 7 the arm halfway back with the elbow bent and the fist still closed, frame 8 back to the stance with exactly the same hand shape as frame 1. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/baixo_soco.png`

Já existe em disco (10/11), ainda sem conferência. Gere de novo só se reprovar no critério.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: a low jab from the cocorinha squat. Frame 1 deep squat with one hand on the ground, frames 2 and 3 the shoulder loads, frames 4 and 5 the free arm punches straight forward at waist height, frames 6 to 8 back to the squat. Frames 1 and 8 equal the squat pose of the crouch sheet. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### Chat "Gutto — arcade" — lote 1

#### `sprites/gutto/quadros/folhas_arcade/ginga.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: standing tall in a high Muay Thai guard, hands at face height, weight on the rear leg, the lead foot light; rhythmic bounce: 1–4 sink and the lead heel lifts, 5–8 rise; frame 8 loops into frame 1; armband tails lag one frame behind the body; shorts hem sways.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/anda.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: guarded walk forward, two steps per cycle: 1 guard, 2 lead foot lifts (anticipation, body leans back a little), 3 lead foot reaches, 4 weight transfers, 5 rear foot passes, 6–8 back to guard; hands stay up but bob with each step; shorts fold at the knee of the stepping leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/defesa.png`

**Decisão do Breno antes de gerar:** o joelho levantado da defesa atual é o bloqueio de canela do Muay Thai e foi pedido de propósito. Este prompt tira a canela; para manter, troque a última frase por "From frame 3 the lead shin lifts to block (Muay Thai shin check)."

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: compact standing block: 1 guard, 2 forearms snap up to cover the face and ribs, elbows tight, chin down, 3–5 hold (5 = impact: body pushed back 2 px, feet slide), 6–8 back to guard. Both feet stay on the ground (no lifted shin).
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/agachado.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: 1 guard, 2 knees start to bend (anticipation), 3–5 drop into a low crouch, hands still high, 6 hold, 7 crouching guard with forearms in front of the face, 8 equal to 6. Shorts spread over the thighs.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### Chat "Raiclaven — arcade" — lote 1

#### `sprites/raiclaven/quadros/folhas_arcade/ginga.png`

Esta folha é também a referência dele. Aprovada, ela passa a ser o anexo das próximas.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: standing guard, barber idle bounce, feet planted wide; 1–4 sink a little, 5–8 rise; the scissors open slowly on 1–4 and close on 5–8; the comb spins one full turn in the left hand across the 8 frames; apron hem and baggy pant legs settle one frame after the body; 8 loops into 1.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/anda.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: confident barber strut forward, full two-step cycle: 1 contact right foot, 2 down, 3 passing, 4 up, 5 contact left foot, 6 down, 7 passing, 8 up; shoulders sway opposite to the hips, the scissors snip once per step, comb spinning; the baggy pants fold behind each knee and the apron swings one frame late; 8 flows into 1.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/soco.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: comb jab (x is the comb, not the scissors): 1 stance, 2 the left shoulder loads back and the comb hand cocks by the cheek, 3 small step in, 4 jab extending, 5 contact: comb fist drawn 15% larger, left shoulder thrust forward, torso turned showing the chest, 6 hold, 7 pulling back, 8 stance; the scissors stay low and closed; apron flicks forward on 5.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/defesa.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: guard: 1 stance, 2 the flat side of the giant scissors comes up in front of the face, comb arm tucked behind it, 3–4 compact block, knees bent, head down behind the blade, 5 impact: pushed back a little, shoes slide, 6 hold, 7 recoil settles, 8 still blocking; apron and pants pushed back by the impact on 5–6.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### Chat "Hazaki — arcade" — lote 1

#### `sprites/hazaki/quadros/folhas_arcade/parado.png`

Primeira folha do Hazaki: anexe `sprites/hazaki/karate.png`. Aprovada, ela vira a referência de todas as outras.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: standing karate guard, fists up, weight on the back leg, breathing bounce: 1–4 sink slightly, 5–8 rise; 8 loops into 1; belt tails sway one frame behind the hips; feet never slide.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/anda.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: guarded forward walk, two-step cycle, fists stay up, 1 contact front foot, 2 down, 3 passing, 4 up, 5–8 same with the other leg; the wide pants fold and swing at each step, belt tails lag; 8 loops into 1.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/defesa.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: 1 stance, 2–3 forearms rise to cover the face, torso compacts, 4–5 hold the block with a small push back on impact, front foot braced, 6–8 back to stance; belt tails flick on the impact frame.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/soco.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: quick straight punch with the front fist: 1 stance, 2 shoulder loads back, 3 hips start turning, 4 fist out, 5 contact with the fist drawn 15% larger, shoulder thrust forward, torso turned showing the chest, 6 hold, 7–8 back to stance; gi top folds at the waist on contact.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

## Lote 2: base, reações e golpes normais

### Chat "Pengaró — arcade" — lote 2

#### `sprites/pengaro/quadros/folhas_arcade/ginga.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: the real capoeira ginga, an 8-frame loop, NOT a boxing guard. The body swings side to side in a low triangle step. Frame 1 both feet parallel and wide, knees bent, torso leaning slightly forward. Frames 2 and 3 the right leg steps far back on the ball of the foot, the torso leans forward and the left arm crosses in front of the face protecting it while the other arm swings low and back. Frame 4 he starts to return. Frame 5 feet parallel and wide again. Frames 6 and 7 the left leg steps far back and the arms swap, with the right arm now crossing in front of the face. Frame 8 returning to frame 1. Relaxed, swaying, rhythmic, arms always moving, always low on the legs. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/agachado.png`

Já existe em disco (10/11), ainda sem conferência. Gere de novo só se reprovar no critério.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: going down to the capoeira cocorinha squat. Frames 1 to 4 he sinks from ginga stance into a deep squat with one hand touching the ground and the other arm protecting the face. Frames 5 to 8 he stays in the deep squat, breathing with small movements. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/chute_baixo.png`

Já existe em disco (10/11), ainda sem conferência. Gere de novo só se reprovar no critério.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: a fast low front kick (chapa). Frame 1 ginga stance, frames 2 and 3 the knee lifts, frames 4 and 5 the leg snaps straight at knee height with the sole forward, frames 6 and 7 the leg folds back, frame 8 ginga stance. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/chute_alto.png`

Já existe em disco (10/11), ainda sem conferência. Gere de novo só se reprovar no critério.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: meia-lua de frente, a high crescent kick. Frame 1 ginga stance, frame 2 weight on the support leg, frame 3 the straight leg rises from the outside, frames 4 and 5 the leg sweeps across at head height, fully extended, frames 6 and 7 the leg comes down, frame 8 ginga stance. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/defesa.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: blocking. Frame 1 ginga stance, frames 2 and 3 forearms cross in front of the face, frames 4 and 5 he holds the block with a pained grimace, frames 6 and 7 the impact pushes him back a little, frame 8 still blocking. The forearms stay compact; the impact frames push the feet back a little. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/apanha.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: getting hit in the face. Frame 1 ginga stance, frames 2 and 3 the head snaps back, mouth open, frames 4 and 5 the torso bends backward with arms flung, frames 6 to 8 he recovers to the ginga stance. The recovery is longer than the hit. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/pulo.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: a jump. Frame 1 knees bent ready to jump, frame 2 pushing off the ground, frame 3 rising with legs starting to tuck, frame 4 tucked at the top like preparing a bicycle kick, frame 5 still tucked and turning, frame 6 falling with legs opening, frame 7 reaching for the ground, frame 8 landing with knees bent. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/ar_soco.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: a downward punch in mid air. All frames are in the air with legs tucked. Frames 1 to 3 the arm winds up, frames 4 and 5 the arm strikes down and forward, frames 6 to 8 he recovers the tucked pose. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/queda.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: being knocked down. Frame 1 hit and bending back, frame 2 feet leaving the ground, frames 3 and 4 flying backward horizontally in the air, frames 5 and 6 falling onto his back, frame 7 bouncing on the floor, frame 8 lying flat on his back. Same body size in every frame. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/levanta.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: getting up with a capoeira kip-up. Frame 1 flat on his back, frames 2 and 3 knees pull to the chest, hands by the head, frames 4 and 5 he kicks up off his hands, frames 6 and 7 landing crouched, frame 8 ginga stance. Frame 1 has the same body size as the last frame of the knockdown. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/martelo.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: a strong elbow strike (cotovelada). Frame 1 ginga stance, frame 2 torso twists back, frame 3 the elbow rises to shoulder height, frames 4 and 5 the torso whips forward with the elbow leading at chin height, frames 6 and 7 he recovers, frame 8 ginga stance. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/afastar.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: a heavy pushing kick that launches the opponent (bencao). Frame 1 ginga stance, frames 2 and 3 the knee chambers high against the chest, frames 4 and 5 the leg thrusts straight forward at chest height with the torso leaning back, frames 6 and 7 the foot lands forward, frame 8 ginga stance. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/cabecada.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: a rising anti-air head butt from the squat. Frame 1 deep squat, frames 2 and 3 the legs push up, frames 4 and 5 the whole body drives upward with the head first, fully stretched, frames 6 to 8 he falls back into the squat. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/rasteirinha.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: a quick low foot sweep from the squat. Frame 1 deep squat with a hand on the ground, frames 2 and 3 the leg slides out, frames 4 and 5 the leg is fully stretched just above the floor, frames 6 to 8 the leg pulls back. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/rasteira.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: a full capoeira rasteira sweep. Frame 1 deep squat with both hands on the ground, frames 2 and 3 the body pivots low, frames 4 and 5 the straight leg sweeps wide along the floor, frames 6 to 8 he gathers back into the squat. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/bicicleta.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: a mid-air bicycle kick like in football. All frames are in the air. Frame 1 tucked, frames 2 and 3 the body tilts backward, frames 4 and 5 lying back in the air, one leg kicks up and forward fully stretched, frames 6 to 8 he rotates back to tucked. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### Chat "Gutto — arcade" — lote 2

#### `sprites/gutto/quadros/folhas_arcade/apanha.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: hit reaction: 1 guard, 2 head snaps back, chin up, 3 torso twisted away, arms thrown open, 4 deepest recoil (stretch 10%), 5 starts recovering, 6–8 guard again (recovery longer than the hit); armband tails and shorts lag 1–2 frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/soco.png`

O gerador usa o quadro 6 como pose de contato: o braço tem que continuar esticado no 6. Jab único (decisão em aberto: a folha atual tem jab e cruzado de propósito).

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: ONE quick lead jab only: 1 guard, 2 lead shoulder loads and hips coil, 3 step-in, 4 fist travels, 5 contact: fist and forearm drawn 15% larger, shoulder thrust forward, torso turned showing the chest, 6 hold, 7–8 back to guard. No second punch in the sheet.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/chute_baixo.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: standing low roundhouse kick to the thigh: 1 guard, 2 rear hip turns, lead foot pivots (anticipation), 3 rear shin swings low, 4–5 contact (same drawing held): shin and foot 15% larger at knee height, hips fully turned forward, the shorts' leg flares open, 6–8 long recovery stepping back to guard.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/chute_alto.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: heavy high roundhouse: 1 guard, 2–3 big wind-up (lead foot pivots, arms counter-swing, torso coils away), 4 leg whips up, 5 contact: shin and foot stretched 15% at head height, hips through, rear arm thrown back, 6 hold, 7–8 long recovery; foot stays inside its frame.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/martelo.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: horizontal elbow strike: 1 guard, 2 elbow cocked high and back (anticipation), 3 step-in, 4 elbow swings across, 5 contact: elbow point 15% larger at head height, shoulder rolled forward, torso turned, 6 hold, 7–8 back to guard.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/pulo.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: 1 crouch to jump, 2 push-off, 3 rising, 4 apex with knees tucked and hands high, 5 starting to fall, 6 legs extend for landing, 7 landing crouch, 8 guard. Armband tails lag.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/queda.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: knockdown: 1 hit hard, 2 lifted off the feet, body arching back, 3–4 flying back, 5 back hits the ground with legs up, 6 bounce, 7–8 lying flat. Shorts and tails lag.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/levanta.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: get up from lying on the back to guard: 1 lying, 2 rolls to the side, 3 sitting, 4 one knee, 5 pushing up, 6–7 rising, 8 guard.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/baixo_soco.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: crouching jab; 1 and 8 equal the crouch pose of agachado 6; 2–3 shoulder loads, 4–5 contact with fist 15% larger (same drawing held), 6–8 back to crouch.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/rasteirinha.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: crouching low teep to the shin: 1 crouch, 2 knee chambers low, 3 foot pushes out, 4–5 contact (same drawing held): sole forward 15% larger at ankle height, 6–8 crouch again.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/cabecada.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: rising knee from the crouch (anti-air shape): 1 crouch, 2 sinks deeper (anticipation), 3 drives up, 4 knee rising to chest, 5 contact: knee 15% larger above the head line, arms pulled down, 6 hold at the top, 7–8 back down to crouch.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/rasteira.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: low sweep that knocks down: 1 crouch, 2 hands to the floor, 3 rear leg sweeps, 4–5 contact: leg fully stretched 15% along the floor, pants leg flared, 6 sweep ends, 7–8 crouch.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/afastar.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: push kick: 1 guard, 2 knee chambers high (anticipation), 3 hips forward, 4 sole extends, 5 contact: sole 15% larger at belly height, torso leaning back, 6 hold, 7–8 recovery.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/bicicleta.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: air knee/kick: 1 jump pose, 2 knee chambers, 3 extends, 4–5 contact (same drawing held): flying knee and shin 15% larger diagonally down-forward, 6–8 tuck back.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/ar_soco.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: air elbow down: 1 jump pose, 2 elbow raised high behind the head (anticipation), 3 swings down, 4–5 contact (same drawing held): elbow tip 15% larger in front of the chest, pointing down-forward, 6–8 tuck back.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### Chat "Raiclaven — arcade" — lote 2

#### `sprites/raiclaven/quadros/folhas_arcade/apanha.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: hit reaction: 1 stance, 2 head snapped back, mouth open, eyes wide, 3 torso twisted, scissors and comb flung out wide, 4 deeper bend back, 5 max bend, hair and apron lagging forward, 6 coming back, 7 grin returning, 8 stance.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/agachado.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: 1 stance, 2–3 sinking with knees opening wide, 4 deep crouch, scissors low and forward, comb up by the face, 5–8 crouched loop, the scissors snip once, the comb turns; pants bunch at the knees.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/pulo.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: 1 knees bent (anticipation), 2 push-off, legs straight, 3 rising, knees tucking, 4 tucked at apex, scissors open, 5 still tucked, 6 falling, legs opening, 7 reaching for the ground, 8 landing with knees bent; apron flies up on 2–3 and drops late on 6–7.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/chute_alto.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: high razor kick: 1 stance, 2–3 big wind-up, back knee chambers to the chest, torso coils away, scissors pulled back for balance, 4 snap, 5 contact: leg and shoe stretched 15% at head height, hips forward, pant leg flared open, 6 hold, 7–8 long recovery with the knee coming back down.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/martelo.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: overhead scissors chop: 1 stance, 2 the steel arm rises, 3 scissors high over the head, wide open, torso arched back (clear anticipation), 4 chop coming down, 5 contact: scissors closing at chest height, blade 15% larger, steel shoulder thrust forward, front knee bent, 6 hold, 7–8 slow pull back to stance; apron swings forward on 5.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/chute_baixo.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: pointy shoe to the shin: 1 stance, 2 front knee lifts, 3 chamber low, 4 snap, 5 contact: shoe tip stretched 15% at shin height, pant leg flaring, 6 hold, 7 back, 8 stance.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/baixo_soco.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: low comb jab: 1 crouch (= agachado 5), 2 comb hand cocks back, 3 pushing forward, 4 jab, 5 contact: comb fist 15% larger at knee height, shoulder forward, 6 hold, 7 back, 8 crouch (= agachado 5).
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/cabecada.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: rising scissors anti-air: 1 crouch, 2 deeper coil, steel shoulder dropped, 3 pushing up, 4 standing tall, scissors thrust straight up open, 5 contact: arm and scissors 15% longer above the head, heels off the ground, 6 hold, 7–8 coming back down to the crouch; apron and pants lifted on 4–5.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/rasteirinha.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: quick low shoe poke: 1 crouch, 2 leg slides out, 3 extending, 4 contact: shoe stretched 15% just above the floor, 5 hold, 6–7 pulling back, 8 crouch.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/rasteira.png`

Traz uma vassoura de barbeiro nova (objeto que ele não tem hoje). Conferir com o Breno se o objeto entra.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: broom sweep: 1 crouch, 2 left hand pulls a barber broom from behind the back, 3 broom cocked behind, torso coiled, 4 sweep starting, 5 contact: broom head 15% larger sliding along the floor at full reach, 6 follow-through, 7–8 long recovery tucking the broom away; pants twist with the hips.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/queda.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: 1 hit, bending back, 2 feet leaving the ground, 3 flying back horizontal, 4 falling, 5 hitting the floor on the back, 6 bounce, 7 settling, 8 flat on the back; the scissors and comb stay in place on the body (same size in every frame).
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/levanta.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: 1 flat on the back (same size as queda 8), 2 sits up, 3 plants the closed scissors on the floor, 4–5 pushes up on the scissors, 6 standing, 7 combs his hair once, 8 stance (= ginga 1).
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/ar_soco.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: diving scissors slash, all frames in the air with knees tucked: 1 tucked, 2–3 scissors rise behind the head, 4 slash starting down-forward, 5 contact: open blades 15% larger in a diagonal, 6 hold, 7–8 back to tucked.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/bicicleta.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: crossing flying kick, all frames in the air: 1 tucked, 2–3 body turns sideways, 4 both legs scissor forward, 5 contact: front shoe 15% larger at head height, pants flared, 6 hold, 7–8 tucked again.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/afastar.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: push kick that sends far (different from chute_alto: chest height, sole flat): 1 stance, 2 lean back, 3 knee to the chest, 4 thrust, 5 contact: flat sole 15% larger at chest height, hips forward, 6 hold, 7 foot lands forward, 8 stance.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### Chat "Hazaki — arcade" — lote 2

#### `sprites/hazaki/quadros/folhas_arcade/agachado.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: 1 standing guard, 2–4 lowers into a deep crouch, knees wide, fists up, 5–8 hold the crouch with a small breathing bounce; 8 loops into 5; the pants bunch at the knees.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/chute.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: heavy side kick at chest height: 1 stance, 2–3 big wind-up, knee chambers high, torso coils away, 4 snap, 5 contact with the leg and foot stretched 15%, hips forward, the pant leg flares open, 6 hold, 7–8 long recovery; belt tails lag two frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/apanha.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: hit reaction: 1 stance, 2 head snaps back, torso twists, hair and belt tails fly forward, 3–4 staggers back on the heels, 5–6 leans and starts falling backward, 7–8 airborne falling flat, arms loose (no rotated standing pose).
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/pulo.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: vertical jump: 1 crouch load, 2 push-off with legs extended, 3–4 rising with knees tucking, 5 apex fully tucked, 6–7 falling with legs opening, 8 landing reach; pants and belt tails trail the motion.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/baixo_soco.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: crouching jab: 1 crouch, equal to the crouch pose of the crouch sheet, 2–3 shoulder loads, 4–5 contact: front fist out 15% larger, rear fist at the chin, 6–8 back to the crouch; 8 equals 1.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/rasteira.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: crouching low sweep: 1 crouch, 2 hands drop toward the ground, body pivots low, 3–4 front leg sweeps in a wide arc close to the ground, 5 contact with the leg and foot stretched 15%, pant leg flared, 6 hold, 7–8 long recovery back to the crouch.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/ascensao.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: rising anti-air from a crouch, shoulder-first, feet stay on the ground line: 1 deep crouch, 2 coils with the front elbow tucked, 3 surges up onto the toes stepping forward, 4–5 front shoulder and elbow leading upward high above the head with the front knee raised, belt tails whipping up (contact on 4–5, arm and shoulder drawn 15% larger), 6 hold on the toes, 7–8 settles back down to stance. No single fist straight up, no jump: the feet stay on the ground.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/queda.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: 1 airborne falling flat, 2 back hits the floor, 3 bounces slightly, 4–8 lies still, head toward the back, belt tails settle.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/levanta.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: 1 lying flat, 2 rolls to the side, 3 hand pushes on the floor, 4 knee under, 5 kneeling, 6 rising, 7–8 stance.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/ar_soco.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: mid-air downward hammer fist: 1 tucked, 2 rears the fist overhead, 3–4 swings down, 5 contact angled down 45°, fist 15% larger, 6 hold, 7–8 tuck again
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/ar_chute.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: mid-air straight kick: 1 tucked, 2 chambers, 3–4 extends, 5 contact with leg stretched 15% pointing slightly down, pant leg flared, 6 hold, 7–8 tuck
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

## Lote 3: especiais, agarrão, super e cenas

### Chat "Pengaró — arcade" — lote 3

#### `sprites/pengaro/quadros/folhas_arcade/armada.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: armada, a rising spinning kick. Frame 1 low stance, frames 2 and 3 he turns his back and starts to rise, frames 4 and 5 he spins in the air with the straight leg sweeping high, frames 6 and 7 falling, frame 8 landing. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/compasso.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: meia-lua de compasso, a spinning kick with a hand on the floor. Frame 1 ginga stance, frames 2 and 3 he bends forward and plants both hands on the ground, frames 4 and 5 the straight leg swings in a big high circle over the head, frames 6 and 7 the leg comes around, frame 8 ginga stance. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/agarrao.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: a judo-like throw. Frame 1 ginga stance, frame 2 both hands reach forward and grab, frames 3 and 4 pulling the grabbed air toward him, frames 5 and 6 turning his back with the hip low, frames 7 and 8 throwing downward with both arms. No second person is shown. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/bola.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: Latada de Sombra, throwing a beer can. Frame 1 ginga stance with the whisky bottle in the back hand and a generic silver beer can (no brand, no text) in the front hand, frames 2 and 3 he winds the front arm back over the shoulder, frames 4 and 5 he whips the arm forward and releases the can at head height, the can leaves the hand, frames 6 and 7 follow-through with the torso leaning forward, frame 8 ginga stance. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/caneta.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: a low sliding tackle like football. Frame 1 ginga stance, frames 2 and 3 he drops to the floor, frames 4 and 5 sliding on one hip with the leading leg stretched forward, frames 6 and 7 getting up, frame 8 ginga stance. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/rolamento.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: a capoeira role, a low rolling dodge. Frame 1 ginga stance, frames 2 to 7 he drops one hand to the floor and spins his low body in a full turn, close to the ground like a cartwheel kept low, frame 8 back up in a crouch. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/golaco.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: Chuva de Bebidas, a super move. Frames 1 and 2 he takes a long swig from the whisky bottle, frame 3 he wipes his mouth, frames 4 and 5 he raises both arms to the sky shouting, frames 6 to 8 bottles and beer cans (no brands) rain down from above in front of him while he laughs with arms open. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/lata.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: drinking a can. A generic silver can with no brand and no text in his hand. Frame 1 ginga stance holding the can, frame 2 opens it, frames 3 to 5 tilts his head back and drinks it all, frame 6 crushes the can, frame 7 burps with his head back, frame 8 wide crazy smile, ready to fight. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/provoca.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: a drunk taunt. Frames 1 to 4 he sways, takes a swig from the whisky bottle and tries to say a word, frame 5 he burps, frames 6 to 8 he waves the opponent in with the bottle, staggering a little. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/vitoria.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: a drunk victory celebration. Frame 1 ginga stance, frames 2 and 3 he raises the whisky bottle high, frames 4 to 6 he drinks from it with the head thrown back, frames 7 and 8 he toasts toward the screen, laughing. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/derrota.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: complaining after losing. Frames 1 and 2 falling to sit on the floor, frames 3 to 8 sitting on the floor with legs out and arms wide open, complaining to the referee, mouth open. The sash tips and the pant legs lag 1-2 frames behind the body.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/fx_arco.png`

Efeito: fundo verde, anexe a folha `soco` aprovada só para a escala.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
Draw a motion arc trail effect only, for a 1990s arcade fighting game: no character, no hand, no body.
A crescent-shaped swoosh in 2-3 pale colors only (white, pale cream, pale amber), hard pixel edges, no glow,
no gradient, no dithering. One single row of 8 frames, evenly spaced, wide image: frames 1-2 a thin sliver,
3-5 the full crescent, 6-8 breaking up and fading into a few hard fragments. Same scale as the attached
sprite sheet. Flat solid green background (#00FF00) everywhere, no text, no numbers, no borders.
```

### Chat "Gutto — arcade" — lote 3

#### `sprites/gutto/quadros/folhas_arcade/armada.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: 1 guard, 2 deep crouch turning the back (anticipation), 3 jumps up spinning, 4 rising, 5 contact at the top: lead leg stretched 15% at head height, 6 apex, 7 falling, 8 landing in guard.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/compasso.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: spinning back kick: 1 guard, 2 step across, 3 turns showing the back, 4 head looks over the shoulder, 5 contact: heel and leg 15% longer straight to the front, 6 hold, 7–8 unwinds to guard; shorts and tails lag the spin.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/bola.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: blowing a kiss: 1 guard, 2 hand to the lips, 3 kiss, puckered lips, 4 arm throws forward, 5 release: open palm 15% larger toward the front, torso turned, 6 hold, 7–8 back to guard. NO heart, sparkle or effect drawn (the heart is a separate sprite).
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/caneta.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: football slide tackle: 1 guard, 2 two quick steps, 3 drops to the side, 4–5 sliding with lead leg stretched 15% low, 6 slide ends, 7 gets up, 8 guard.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/rolamento.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: forward roll: 1 guard, 2 tuck, 3–5 roll as a tight ball, 6 coming out on one knee, 7 rising, 8 guard.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/agarrao.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: clinch grab and throw: 1 guard, 2 steps in, 3 both hands reach forward, 4 hands lock behind an (invisible) opponent's neck, elbows tight, 5 pulls the head down, 6 pivots on the lead foot turning the opponent, 7 throws him past the hip, arms opening, 8 follow-through held.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/golaco.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: super finisher: 1 guard, 2 deep crouch (anticipation), 3 rising knee, 4 high kick, 5 turn, 6 second high kick, 7 contact: leg stretched 15%, 8 victory roar still in side view.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/lata.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: intro: walks in, removes nothing, cracks neck, slaps the armband, settles into guard; frame 8 equal to ginga frame 1. Same scale as ginga.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/provoca.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: taunt: 1 guard, 2–4 opens arms wide inviting, 5 shakes the shoulders, 6 points at the opponent, 7–8 back to guard.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/vitoria.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: 1 guard, 2–3 arms rise, 4 fists high, 5–6 flexes, 7 points forward, 8 hold.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/gutto/quadros/folhas_arcade/derrota.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: falls to sitting, exhausted, head down; 1 standing hurt, 2–4 collapsing, 5–8 seated. Same scale as ginga.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### Chat "Raiclaven — arcade" — lote 3

#### `sprites/raiclaven/quadros/folhas_arcade/armada.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: spinning barber-chair kick: 1 stance, 2 pivot on the front foot, 3 back turned, scissors tucked, 4 spinning, 5 contact: leg stretched 15% high, pant leg flared, 6 completing the turn, 7–8 recovery. Same scale as ginga.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/compasso.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: Scissor Helicopter: 1 stance, 2 steel shoulder winds back, 3 the arm starts circling at the shoulder in front of the body, 4–5 the arm is a horizontal blur-free blade at chest height, scissors open, shown at different angles each frame, torso leaning in, 6 still spinning, 7 slowing, 8 recovery: arm still out to the side, torso still leaning, not yet back to stance; apron whips around.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/caneta.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: scissors dash: 1 stance, 2 crouch and aim the scissors forward, 3 push off, 4 lunging low and fast, scissors open like a spear, 5 contact: blades snap shut 15% larger, 6 slide, 7 still low, 8 still low and overextended, scissors closed, about to rise. Same scale and cell size as ginga.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/bola.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: comb throw: 1 stance, 2 left arm cocks back with a big comb, 3 deep wind-up, torso turned away, 4 throw, 5 release: arm 15% longer, comb leaving the hand at chest height, 6 follow-through, 7–8 recovery.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/rolamento.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: disappearing step, body only (no talc): 1 stance, 2 comb cocks back, 3 flick of the comb forward, 4 body ducks low, 5 low crouch pose turned away, 6 low lunge forward, scissors forward, 7 catches the comb, 8 stance.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/pente_combo.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: sequence after reappearing, no cloud on the body: 1 low lunge (same as rolamento 6), 2 contact: comb jab to the face, comb hand 15% larger, 3 pulling the comb back while the scissors rise (no hit), 4 contact: scissors slash low, 5 turning the steel shoulder back to load (no hit, no spin line), 6 steel arm thrusts the open scissors forward, 7 contact: scissors snap shut 15% larger, shoulder forward, 8 combs his hair, grinning.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/agarrao.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: hot towel grab, the steel arm keeps the scissors in every frame: 1 stance, 2 left hand reaches with a white towel, 3 towel wraps an invisible head, scissors hooked behind it, 4 pull in, 5–6 pivot (side view, apron visible, never seen from the back), 7 throw: left arm 15% longer, towel flung forward, 8 fixes his hair with the comb. No second person.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/golaco.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: flurry of haircuts: 1 stance, 2 crouch and grin (anticipation), 3 scissors snip high, 4 comb jab, 5 scissors snip low, 6 scissors snip high, 7 contact: huge closing of the scissors 15% larger, 8 pose.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/provoca.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: 1–3 snips the scissors by his own ear, 4–6 points the comb at the opponent and waves him to the chair, 7–8 laughs with the head thrown back.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/lata.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: warm-up: 1 stance, 2–3 rubs the blades against each other, 4–5 checks the edge with the left thumb, 6–7 spins the comb, 8 stance.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/vitoria.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: 1 stance, 2–3 blows hair off the blades, 4–6 combs his own hair with the comb in the LEFT hand, 7–8 rests the open scissors (still on the steel arm) over his shoulder, crazy grin.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/derrota.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: 1 stance hurt, 2 drops to sit, 3–8 sitting, legs out, scissors bent and drooping, comb broken, sulking (same scale throughout).
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/despertar_a.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: 1 stance, 2 shoulders hunch, 3 head drops, 4 sparks implied by the pauldron pose, 5 muscles swell, 6 head snaps up, eyes bulging, 7–8 grin widens.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/raiclaven/quadros/folhas_arcade/despertar_b.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: 1 roars with the head back, 2–3 scissors open wide to the side, 4–5 the comb spins fast, 6–7 crouches forward, 8 ready stance, bigger and wilder.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### Chat "Hazaki — arcade" — lote 3

#### `sprites/hazaki/quadros/folhas_arcade/punho_concreto.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: one-handed lunging straight punch: 1 stance, 2–3 steps in and rears the front fist back at the hip, 4 drives forward, 5 contact at chest height with the fist 15% larger, shoulder thrust forward, 6 hold, 7–8 back to stance; no projectile drawn, no fire.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/machado.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: overhead axe kick: 1 stance, 2–3 front leg swings straight up high, torso leans back, 4 apex with the leg vertical, 5 heel chops down, contact at head height, foot 15% larger, 6 hold, 7–8 long recovery stepping down.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/giro_garagem.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: advancing turning back kick, grounded: 1 stance, 2 front foot steps across, 3 spins showing the back, 4 rear leg chambers, 5 contact, heel out, leg stretched 15%, 6 hold, 7–8 recovers facing right. Grounded spin, never floating.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/agarrao.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: 1 reaches with both hands, 2 grabs collar and arm, 3 pulls close, 4 turns the hips under, 5–6 hip throw over the shoulder, 7 releases, 8 back to stance.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/vitoria.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: ties the belt tight with a sharp pull, then fists on the hips, chin up, chest out (1–8, last frame holds)
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/provoca.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: points at the opponent, then flexes one arm and taps the biceps, grinning (1–8, loops into 1)
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/hazaki/quadros/folhas_arcade/despertar.png`

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: transformation: 1 stance, 2–3 clenches fists and bends forward, 4 belt piping starts glowing, 5 hair lightens and grows back, 6 horns push out, 7 straightens roaring, 8 final pose of the awakened form. Full body in frame 8.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

## Lote 4: esperando decisão (sem prompt ainda)

Nada daqui entra na fila antes da resposta do dono. As MOTION propostas estão nos documentos de cada lutador.

| Lutador | Folhas | Depende de |
|---|---|---|
| Pengaró | `endiabrado`, `despertar_a`, `despertar_b` e as 28 `e_` | troca de paleta x folha própria (`arte.md`: `e_` só onde o desenho muda) |
| Pengaró | `ar_bencao` (especial no ar), quadro final de lançar do super máximo, `arrastao` (se houver carga) | itens 10 e 11 do kit e decisão da carga |
| Gutto | `endiabrado`, `ginga_endiabrada`, `despertar_a`, `despertar_b` e as `e_` gêmeas (mesmo MOTION, prompt do demônio) | paleta do demônio medida (falta branco para cós e braçadeira) |
| Gutto | `cotovelo_sobe` (opção B do antiaéreo), `soco_forte`, `clinch`, `super_joelhos`, `super_final`, `ar_cotovelo`, `corre`, `e_corre` | itens 1, 3, 5, 6, 8, 9 e 10 do kit |
| Raiclaven | `tesoura_ascendente`, `cadeira`, `super_cortes`, `maquina`, `borrifada`, `pente_girando`, `super_final`, `ar_pente`, `e_` do Surto | itens 1, 4–12 e 15 do kit; Toalha x Cadeira |
| Raiclaven | `fx_corte`, `fx_talco`, `fx_borrifo`, `fx_maquina` (fundo verde) | junto com os golpes que usam |
| Hazaki | `d_parado`, `d_soco`, `d_chute`, `d_agachado`, `d_rasteira`, `d_pulo`, `d_ascensao`, `d_punho`, `d_defesa`, `d_apanha` | rival x boneco; prompt `d_` com juba para trás, sem cavanhaque |
| Hazaki | `vitima` (25 desenhos), `soco_perto`, `chute_perto`, `agarrao_faixa`, `agarrao_baixo`, `faixa_asfalto`, `pose_final`, `punho_chao`, `arremesso`, `rolada_tatame`, `ar_queda`, `fx_concreto`, `fx_cone`, `fx_brasa` | rival x boneco e mudanças de CNS |
