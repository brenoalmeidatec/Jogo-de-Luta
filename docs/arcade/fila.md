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

## Lote 5: desenhos pedidos pela auditoria de anatomia do Pengaró (2026-11-11)

Saíram do pente fino de anatomia (branch `anatomia`, entrada de 2026-11-11 no `LOGBOOK.md`). Cada item é uma folha de 8
quadros no chat "Pengaró — arcade", com a referência "Socos" anexada e o **prompt base do Pengaró** (o bloco inteiro das
folhas acima), trocando só a linha `MOTION:`. Regra fixa em todas: **a caneleira fica sempre na perna de trás (a mesma
em todos os quadros) e a garrafa fica sempre na mão de trás**; quando ele bebe, é a mão de trás que sobe. O que o jogo
usa hoje no lugar de cada uma está na coluna "paliativo".

| Folha (`sprites/pengaro/quadros/folhas_arcade/`) | Por quê | Paliativo no jogo hoje |
|---|---|---|
| `anda.png` (refazer) | os quadros 3 e 7 levantam a MESMA perna e 4-5-6 são quase iguais: falta a passagem da outra perna | 6 desenhos na ordem 0,2,3,4,1,5; a perna sem caneleira vai de trás para a frente sem quadro de passagem |
| `corre.png` | não existe corrida: o jogo acelera o andar | desenhos do andar a 3 ticks |
| `recuo.png` | o recuo é um desenho só deslizando | `defesa/06` parado |
| `compasso.png` | perna de apoio some, duas caneleiras, caneleira de outra cor | folha antiga com o magenta limpo |
| `chute_baixo.png` (refazer como chute em pé) | a folha arcade em disco é um chute rasteiro agachado, outro golpe | folha antiga com a caneleira da perna do chute repintada como calça |
| `bola.png` | a garrafa some em 2 quadros e a lata troca de braço | folha antiga |
| `provoca.png` | bebia com uma garrafa na boca e outra na mão | a garrafa da mão de trás foi apagada nos desenhos 2 e 3; a garrafa ainda muda de mão |
| `vitoria.png` | a garrafa muda de mão para beber | corte seco entre os desenhos |
| `caneta.png` | duas caneleiras e garrafa encolhida no quadro de contato | folha antiga |
| `rolamento.png` | é um giro agachado no lugar, com duas caneleiras de costas | folha antiga com a franja limpa |
| `queda.png` (refazer) | a folha arcade em disco tem o corpo em pé ~25% menor que o resto e o último quadro sem caneleira | folha antiga com o magenta limpo |
| `lata.png` | abre a lata com duas mãos sem soltar a garrafa (três mãos) | a intro começa com a lata já na mão |
| `ar_soco.png`, `bicicleta.png` (refazer) | no ar aparecem duas caneleiras (uma em cada canela); as folhas arcade em disco perdem a caneleira no meio | folhas antigas, sem retoque |
| `ginga_endiabrada.png`, `e_anda.png`, `e_levanta.png` (forma endiabrada, referência do endiabrado) | 8 poses soltas, algema em dois tornozelos, andar sem passada, parada de mão com pés no lugar das mãos | só os desenhos limpos, segurados |

`anda.png`:

```
MOTION: guarded walk forward, fists up, bottle hanging in the rear hand the whole time, a full two-step cycle where the two legs ALTERNATE: frame 1 contact, bare leg forward and shin-guard leg back; 2 weight sinks on the bare leg; 3 the shin-guard leg passes under the body with the knee high; 4 the shin-guard leg reaches forward; 5 contact with the legs swapped, shin-guard leg forward; 6 weight sinks on the shin-guard leg; 7 the BARE leg passes under the body with the knee high (never the shin-guard leg again); 8 the bare leg reaches forward and flows into frame 1. The shin guard stays on the same leg in all 8 frames. The sash tips and the pant legs lag 1-2 frames behind the body.
```

`corre.png`:

```
MOTION: run forward, torso leaning 20 degrees ahead, fists pumping, bottle in the rear hand; a full cycle with the legs alternating: 1 contact bare leg, 2 push-off, 3 both feet off the ground with the shin-guard leg passing, 4 shin-guard leg reaches, 5 contact shin-guard leg, 6 push-off, 7 both feet off the ground with the bare leg passing, 8 bare leg reaches and flows into frame 1. The shin guard stays on the same leg. The sash tips fly straight back.
```

`recuo.png`:

```
MOTION: short hop backward out of the ginga stance, always facing right: 1 stance; 2 knees bend and the weight goes to the rear leg; 3 both feet leave the ground, body leaning slightly back, guard up; 4 highest point of a low hop, legs tucked a little; 5 the rear foot reaches back for the ground; 6 landing on the rear foot, front foot still in the air; 7 both feet down, knees absorbing; 8 back to the stance of frame 1. Bottle in the rear hand and shin guard on the rear leg in every frame.
```

`compasso.png`:

```
MOTION: capoeira meia-lua de compasso (spinning heel kick with one hand on the ground): 1 ginga stance; 2 the torso twists and drops, front hand going to the ground; 3 front hand planted on the ground, bottle held up and back in the rear hand, the front leg stays bent and planted and fully visible; 4 the rear leg (the one with the shin guard) lifts straight and sweeps around; 5 that leg at its highest point passing over, heel leading, supporting leg bent and fully visible from hip to foot; 6 the leg comes down on the other side; 7 the foot touches the ground and the hand leaves the floor; 8 back to the stance. Exactly two legs in every frame, the shin guard only on the spinning leg, same patterned shin guard as the attached sheet.
```

`chute_baixo.png`:

```
MOTION: standing front push kick at belly height with the FRONT leg: 1 stance; 2 weight shifts to the rear leg (the shin-guard leg, which stays planted and visible with its shin guard in every frame); 3 front knee lifts to the chest; 4 the front leg extends; 5 contact: leg fully extended, foot flexed, drawn 15% larger, hips thrust forward, torso leaning back; 6 hold; 7 the knee folds back; 8 foot down, stance. The kicking leg never has a shin guard. Bottle in the rear hand.
```

`bola.png`:

```
MOTION: overhand throw of a beer can with the FRONT arm, the whisky bottle staying in the rear hand next to the hip in all 8 frames: 1 stance holding the can in the front hand; 2 the front arm cocks back over the shoulder; 3 torso wound up, can behind the head; 4 the arm whips forward; 5 release: front arm fully extended, hand open, no can; 6 follow-through, torso bent forward; 7 recovering; 8 stance with the front hand empty.
```

`provoca.png`:

```
MOTION: taunt: 1 stance; 2 he leans back, front hand open and relaxed; 3 the REAR hand lifts the same bottle it was already holding up to the mouth, front hand resting on the hip; 4 head tilted back, drinking from that bottle, only ONE bottle in the image; 5 the bottle comes down, he exhales with the mouth open; 6 the front hand beckons the opponent; 7 beckons again; 8 stance. The bottle never changes hand and there is never a second bottle.
```

`vitoria.png`:

```
MOTION: victory pose: 1 stance; 2 the rear hand raises the bottle high; 3 bottle at the highest point, chest out; 4 the SAME rear arm brings the bottle down to the mouth, front arm resting at the side; 5 drinking, head back; 6 drinking; 7 bottle lowered to chest height, big grin; 8 front arm opens to the crowd. The bottle stays in the rear hand in all 8 frames.
```

`caneta.png`:

```
MOTION: low sliding sweep (chapa de chão): 1 stance; 2 he drops, front hand to the ground; 3 sitting low on the supporting leg; 4 the front leg shoots forward along the ground; 5 contact: leg fully extended along the ground, foot flexed, drawn 15% larger; 6 hold; 7 the leg folds back; 8 rising to the stance. One shin guard only, on the supporting (rear) leg, in every frame; the whisky bottle keeps its full shape (neck, label) in the rear hand in every frame.
```

`rolamento.png`:

```
MOTION: low side roll past the opponent: 1 stance; 2 he drops into a squat, front hand to the ground; 3 tucks the head and rolls over the front shoulder; 4 upside down, back to the camera, both legs tucked and visible; 5 coming out of the roll on the other side; 6 feet touch the ground, still tucked; 7 squat facing right, guard up; 8 stance. Bottle always in the rear hand, shin guard always on the same leg (never two shin guards).
```

`queda.png`:

```
MOTION: knocked down: same size and scale as the attached sheet in every frame, including the standing ones. 1 hit, head snapping back, still standing; 2 falling backward, feet leaving the ground; 3 body horizontal in the air; 4 the back hits the ground, legs up; 5 small bounce; 6 settling; 7 lying on the back, knees slightly bent; 8 lying flat. Shin guard on the same leg and bottle in the rear hand in all 8 frames, including the last one.
```

`lata.png`:

```
MOTION: he drinks a can of beer while the whisky bottle stays in the rear hand: 1 stance with a closed can in the front hand; 2 the thumb of that SAME front hand pops the tab, the other hand keeps holding the bottle down at the hip, exactly two hands in the image; 3 can raised to the mouth; 4 drinking, head back; 5 drinking; 6 he crushes the empty can in the front fist; 7 laughs with the crushed can; 8 front hand open, can gone.
```

`ar_soco.png` e `bicicleta.png`:

```
MOTION: jumping downward punch: 1 airborne, knees tucked; 2 the front arm loads up beside the head, elbow bent, fist visible; 3 the fist starts down; 4 contact: front arm fully extended diagonally down, fist 15% larger; 5 hold; 6 the arm folds back; 7 knees tucked, guard up; 8 legs reaching for the ground. Exactly ONE shin guard, on the rear leg, visible in all 8 frames; the other shin is bare. Bottle in the rear hand.
```

```
MOTION: airborne bicycle kick: 1 airborne, knees tucked; 2 the body leans back; 3 the front leg (bare shin, no shin guard) lifts; 4 that leg whips up; 5 contact: front leg fully extended upward, foot 15% larger, body almost horizontal; 6 hold; 7 the leg folds, body rotating upright; 8 knees tucked, ready to land. Exactly ONE shin guard, on the rear leg, visible in all 8 frames. Bottle in the rear hand.
```

Forma endiabrada (chat do endiabrado, referência do endiabrado, sem garrafa, algema em UM tornozelo só, o de trás):

```
MOTION: possessed capoeira ginga, one single cycle, side view the whole time (the chest never turns to the camera): 1 wide stance, claws up; 2 weight shifts to the front leg, rear heel lifts; 3 the rear leg steps far back, torso sinks, front hand guarding the face; 4 lowest point, rear leg stretched back; 5 the rear leg starts to come back, torso rising; 6 narrow stance, weight centered; 7 the rear foot steps out again; 8 wide stance that flows into frame 1. One ankle shackle only, on the rear ankle, in all 8 frames; no green, no magenta inside the figure.
```

```
MOTION: possessed stalking walk forward, torso low, claws out, hands never touch the ground, legs ALTERNATING: 1 contact, rear-shackle leg back; 2 weight sinks; 3 the shackled leg passes under the body; 4 it reaches forward; 5 contact with the legs swapped; 6 weight sinks; 7 the other leg passes; 8 it reaches forward and flows into frame 1. One ankle shackle only, always on the same leg; both arms attached to the shoulders and fully visible in every frame.
```

```
MOTION: possessed kip-up: 1 lying on the back; 2 knees pulled to the chest; 3 rolls onto the shoulders, both PALMS flat on the ground beside the head, fingers visible; 4 the legs go up together, feet pointing at the sky, the face visible between the arms; 5 the legs whip forward, body arching off the ground; 6 feet land, deep squat; 7 rising, guard up; 8 stance. Hands are hands with fingers in every frame, never feet; exactly two arms and two legs.
```

## Lote 6: Pengaró inteiro na arte arcade (2026-11-11)

> **Situação em 2026-11-11 (fim do dia):** grupos A a D gerados, convertidos e **ligados no jogo** (17 folhas em
> `sprites/pengaro/quadros_arcade/`; ver LOGBOOK, "Lote 6 ligado"). Na forma normal só a cena do Despertar (2000,
> `despertar_a/b`) ainda toca a arte antiga. Ficam por refazer, se alguém quiser os desenhos que hoje são repetidos:
> `golaco` quadro 2 e `vitoria` quadros 4 a 8 (bebe com a mão da frente). Grupo E segue opcional.

Fila do que ainda precisa ser **desenhado no ChatGPT** para o Pengaró normal ficar 100% na arte arcade (hoje só
ginga, andar e levantada tocam arcade; os golpes são a arte antiga e ele troca de cabelo, pele e caneleira a cada
golpe). Fora daqui: a forma Endiabrada (`e_*`, `endiabrado`, `ginga_endiabrada`, `despertar_a/b`), que será
redesenhada à parte, e os efeitos `fx_*`.

**Este lote substitui o Lote 5 para a forma normal** (os MOTION de lá foram fundidos aqui, já com o prompt inteiro) e
substitui os prompts dos lotes 2 e 3 das mesmas folhas. Do Lote 5 continuam valendo só os três pedidos da forma
endiabrada, parados até o redesenho. `ar_soco` saiu da fila: a folha arcade em disco foi aprovada.

**Não precisam de desenho** (folha arcade aprovada e já em `quadros_arcade/`, falta só ligar no gerador): `soco`,
`parado`, `chute_alto`, `martelo`, `afastar`, `apanha`, `pulo`, `baixo_soco`, `ar_soco`, `cabecada`, `levanta`,
`ginga`, e com ressalva `agachado`, `rasteirinha`, `queda`, `bicicleta` (grupo E) e o extra `chute_agachado`.

Como gerar (muda em relação aos lotes 1 a 3):

1. Chat "Pengaró — arcade", uma folha por mensagem, salvando em `sprites/pengaro/quadros/folhas_arcade/<folha>.png`.
2. **Referência anexada em toda mensagem:** `sprites/pengaro/quadros/folhas_arcade/soco.png` (a folha arcade
   aprovada, do disco). Não gerar sem anexo: foi assim que `defesa` saiu com outro homem, outra garrafa e outro cinto.
3. O prompt abaixo é o prompt base do Pengaró com um parágrafo a mais (`MODEL LOCK`), que fixa o que os avaliadores
   mais reprovaram: garrafa na mão de trás, uma caneleira só na perna de trás, dois braços e duas pernas, faixa verde
   curta com pontas amarelas, cabelo escuro, mesma escala. Só estilo geral de luta 2D dos anos 90, nada copiado de
   jogo comercial; garrafa e lata sem marca.
4. Conferir antes de aceitar, quadro a quadro: 8 quadros inteiros; UMA garrafa, na mão de trás; UMA caneleira oliva,
   na canela da perna de trás; dois braços e duas pernas; cabelo escuro; figura em pé da altura da de `soco.png`
   (~111 px depois de convertida). Reprovou: gerar de novo no mesmo chat, com a referência.
5. Depois: `quantizar_folha.py` -> `animar_folha.py --arcade` -> `quantizar_folha.py --meio` -> `conferir_arte.py`
   (ver `pengaro.md`), e pôr a folha em `ARCADE` no `gerar_pengaro.py`.

Os números de desenho nas notas contam de 0 (desenho 0 = quadro 1 do MOTION) e são os que o gerador usa hoje: a ordem
dos quadros de cada MOTION foi escrita para a folha nova entrar sem mexer em tempos nem caixas.

### A. Reprovadas na conversão: refazer (3)

#### `sprites/pengaro/quadros/folhas_arcade/defesa.png`

Refazer (reprovada: a folha em disco é de outro modelo, com long neck marrom, cordão amarelo e tornozeleira azul, e a garrafa sobe para o rosto). O gerador usa os desenhos 1 a 7: 120/140 entra e sai com 1 e 3, 130 segura com 3 e 4, 150 apanha na defesa com 5, 6, 7, 760 apara com 3 e 4, `recua` = 6, `parry` = 2/3. A ordem abaixo não pode mudar.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: standing block with the FRONT forearm. The bottle stays low in the rear hand, next to the rear hip, in all 8 frames: it never rises to the face and never goes between the arms. Frame 1 ginga guard; 2 the front forearm rises, chin drops, rear shoulder pulled back; 3 front forearm vertical covering the face, closed fist at forehead height (the hold pose); 4 same pose, wincing, shoulders hunched; 5 same pose, torso rocked slightly back by an impact; 6 bigger impact, both feet slide a little backward, knees more bent; 7 leaning back, weight on the rear leg, forearm still high; 8 firm block again, same as frame 3. The sash tips lag 1-2 frames. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/chute_baixo.png`

Refazer (reprovada: a folha em disco é um chute rasteiro agachado, outro golpe; a conversão dela ficou guardada como `quadros_arcade/chute_agachado/`). Substitui o MOTION de `chute_baixo` do Lote 5: este segue os índices do gerador (230/245 pela `sequencia`: liga 1 e 2, caixa nos desenhos 3 e 4, volta 5, 6, 7; 231 = 1, 4, 6; 1500/1501 = 2, 4, 6; sprite `pisa` = 4). O desenho 5 já tem de estar dobrando: é a volta, sem caixa.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: standing front push kick at belly height with the FRONT leg (the bare one). Frame 1 ginga stance; 2 weight shifts onto the rear leg, which stays planted and visible with its shin guard in all 8 frames; 3 the front knee lifts to the chest; 4 the front leg shoots out, almost straight, sole forward, at belly height; 5 contact: leg fully straight, foot flexed, hips thrust forward, torso leaning slightly back; 6 the knee folds back, foot pulled in; 7 the foot comes down, knee still bent; 8 foot on the ground, ginga stance. The kicking leg never has a shin guard. On the contact frame the striking hand or foot is drawn 15% larger than in frame 1; the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/rasteira.png`

Refazer (reprovada: duas garrafas nos desenhos 0, 1 e 7, joelheira verde-água no lugar da caneleira, pano pendurado na cintura). Gerador: 440 pela `sequencia` (liga 1 e 2, caixa nos desenhos 3 e 4, volta 5, 6, 7); `rasteira0..3` = desenhos 2, 4, 4, 6 (usados em 1100, 1300, 1400, 3100). Enquanto não chega, o paliativo arcade é `quadros_arcade/chute_agachado/`.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: capoeira rasteira, a full low leg sweep with both hands on the ground. Frame 1 deep squat, both hands going to the ground, the bottle lying along the ground gripped in the rear hand, the front hand EMPTY; 2 the body turns low, weight on the hands; 3 the front leg (bare shin) starts to sweep forward close to the ground; 4 that leg straight and low, halfway through the arc; 5 contact: the leg fully stretched along the ground, hips turned; 6 the leg starts to fold back; 7 almost folded; 8 deep squat, same as frame 1. The shin guard is on the SHIN of the bent supporting rear leg, same olive color as the attached sheet. No cloth hanging between the legs. On the contact frame the striking hand or foot is drawn 15% larger than in frame 1; the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### B. Especiais e agarrão: folhas novas (6)

#### `sprites/pengaro/quadros/folhas_arcade/bola.png`

Folha nova (Latada de Sombra). Funde o pedido do Lote 5 (na antiga a garrafa some em 2 quadros e a lata troca de braço). Gerador: 1000/1001 = desenhos 2 (8 ticks), 4 (é o que solta a lata), 5, 7; agarrão de comando 831 usa 2, 4, 5, 6, 7; sprite `especial` = 4. A lata no ar é sprite à parte: do quadro 5 em diante não há lata na folha.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: overhand throw of a plain beer can (no brand) with the FRONT arm, the whisky bottle staying in the rear hand next to the hip in all 8 frames. Frame 1 stance holding the can in the front hand; 2 the front arm cocks back over the shoulder; 3 torso wound up, can behind the head; 4 the arm whips forward, can still in the hand; 5 release: front arm fully extended forward, hand open, NO can anywhere in the image; 6 follow-through, torso bent forward; 7 recovering; 8 stance with the front hand empty. The sash tips and the pant legs lag 1-2 frames. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/compasso.png`

Folha nova. Funde o pedido do Lote 5 (na antiga a perna de apoio some e há duas caneleiras de cores diferentes). Gerador: 1100/1101 = desenho 1 (8 ticks), 2, 3, 4, 5 com a caixa do giro, 7; `gira0..3` = 2 a 5; agarrão de comando 831 usa 1 a 7 com o contato no desenho 4.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: capoeira meia-lua de compasso, a spinning heel kick with one hand on the ground. Frame 1 ginga stance; 2 the torso twists and drops, front hand going to the ground; 3 front hand planted on the ground, bottle held up and back in the rear hand, the front leg bent, planted and fully visible; 4 the rear leg (the one with the shin guard) lifts straight and sweeps around; 5 contact: that leg at its highest point passing over, heel leading, the supporting leg bent and fully visible from hip to foot; 6 the leg comes down on the other side; 7 the foot touches the ground and the hand leaves the floor; 8 back to the stance. The shin guard is only on the spinning leg, same olive shin guard as the attached sheet; the supporting leg is bare. On the contact frame the striking hand or foot is drawn 15% larger than in frame 1; the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/armada.png`

Folha nova (na antiga a caneleira some no ar). Gerador: 1200/1201 = desenhos 2 (4 ticks), 4 com a caixa, 5, 6 segurado até pousar; `kick_alto` = 4; `DESENHOS_NO_AR` = 3 a 5.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: armada, a rising spinning kick. Frame 1 ginga stance; 2 he dips, knees bent, gathering; 3 he jumps turning his back to the camera, the rear leg (shin guard) tucked under the body, the front knee lifting; 4 airborne, the front leg (bare shin) starts to swing out; 5 contact: front leg straight and high at head height, hips turned; 6 the leg sweeps past and lowers, still airborne; 7 falling, both legs tucked, facing right again; 8 landing in the ginga stance. The shin guard stays visible on the tucked rear leg in the airborne frames; the kicking leg is bare. On the contact frame the striking hand or foot is drawn 15% larger than in frame 1; the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/caneta.png`

Folha nova. Funde o pedido do Lote 5 (na antiga: duas caneleiras e garrafa encolhida no contato). Gerador: 1300/1301 = desenhos 2 (10 ticks), 4 com a caixa rasteira, 7.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: low sliding sweep (chapa de chao). Frame 1 stance; 2 he drops, front hand to the ground; 3 sitting low on the supporting rear leg; 4 the front leg (bare shin) shoots forward along the ground; 5 contact: leg fully extended along the ground, foot flexed; 6 hold, same pose; 7 the leg folds back; 8 rising to the stance. The shin guard is on the supporting rear leg in every frame; the bottle keeps its full shape in the rear hand, held off the ground. On the contact frame the striking hand or foot is drawn 15% larger than in frame 1; the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/rolamento.png`

Folha nova. Funde o pedido do Lote 5 (a antiga é um giro agachado no lugar, com duas caneleiras de costas). Gerador: 700 e variações tocam 0 a 7; 705 toca de trás para a frente; `rola0..7`.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: low forward roll past the opponent. Frame 1 stance; 2 he drops into a squat, front hand to the ground; 3 tucks the head and rolls over the front shoulder; 4 upside down, back to the camera, both legs tucked and visible; 5 coming out of the roll; 6 feet touch the ground, still tucked; 7 squat facing right, guard up; 8 stance. The bottle is hugged to the body in the rear hand through the roll. The sash tips lag 1-2 frames. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/agarrao.png`

Folha nova (na antiga os desenhos 4 e 5, de costas, têm defeito de caneleira). Gerador: 810 = desenhos 2 a 7; 830 = 2 com a caixa do agarrão, depois 3, 4, 5; 831 começa com 2 e 3; `agarra` = 2, `joga` = 6. A vítima é sprite à parte: não desenhar oponente.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: standing grab and hip throw using only the FRONT arm; the opponent is NOT drawn. Frame 1 stance; 2 the front arm reaches forward, hand open; 3 grab: the front hand closes into a fist at chest height, arm extended; 4 he pulls that fist in to his chest, torso turning; 5 he pivots, back turning to the camera, hips loaded, knees bent; 6 mid-pivot, low, back to the camera; 7 throw: facing right again, torso bent forward, the front arm swung down and forward, hand opening; 8 follow-through, low, front hand near the floor. With his back to the camera there is still only one shin guard, on the same leg. The sash tips lag 1-2 frames. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### C. Super e cenas: folhas novas (5)

#### `sprites/pengaro/quadros/folhas_arcade/golaco.png`

Folha nova (Chuva de Bebidas, 3000). O gerador só mostra os desenhos 0 a 4 e segura o 4 (`ULTIMO_DESENHO`): garrafas e latas da chuva são sprites à parte, então a folha nova NÃO desenha chuva (na antiga ela vinha pintada no corpo do 5 em diante e a garrafa ia à boca na mão errada).

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: super move wind-up, no objects in the air in any frame. Frame 1 the REAR hand has lifted its bottle to the mouth, drinking, front arm relaxed at the side; 2 long swig, head tilted back, same rear hand; 3 the bottle is back down at the hip in the rear hand and he wipes his mouth with the back of the FRONT hand; 4 both arms rising, chest filling; 5 both arms thrown up to the sky, shouting, bottle held high in the rear hand, front hand open; 6 to 8 he holds the arms up laughing, with a small sway. The sash tips and the pant legs lag 1-2 frames. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/lata.png`

Folha nova (intro 190-192 e Despertar antigo). Funde o pedido do Lote 5 (na antiga abre a lata com uma terceira mão). Gerador: `embaixada0..3` = desenhos 0, 2, 3, 4; `lata0/1/2` = 2, 4, 7. Com a folha nova o `DESENHO_PROIBIDO` e o `MEIO_PROIBIDO` da lata podem sair.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: he drinks a plain can of beer (no brand) while the whisky bottle stays down at the hip in the rear hand. Frame 1 stance with a closed can in the front hand; 2 the thumb of that SAME front hand pops the tab, exactly two hands in the image; 3 can raised to the mouth; 4 drinking, head back; 5 drinking, head further back; 6 he crushes the empty can in the front fist; 7 laughs, crushed can in the fist; 8 front hand open and empty, can gone. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/provoca.png`

Folha nova (195, desenhos 0 a 7 a 7 ticks). Funde o pedido do Lote 5 (na antiga bebe com uma garrafa na boca e outra na mão).

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: taunt. Frame 1 stance; 2 he leans back, front hand open and relaxed; 3 the REAR hand lifts the same bottle it was already holding up to the mouth, front hand resting on the hip; 4 head tilted back, drinking from that bottle, only ONE bottle in the image; 5 the bottle comes back down to the hip, he exhales with the mouth open; 6 the front hand beckons the opponent; 7 beckons again; 8 stance. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/vitoria.png`

Folha nova (181, desenhos 0 a 6 a 6 ticks e segura o 7). Funde o pedido do Lote 5 (na antiga a garrafa muda de mão para beber).

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: victory pose. Frame 1 stance; 2 the rear hand raises the bottle high; 3 bottle at the highest point, chest out; 4 the SAME rear arm brings the bottle down to the mouth, front arm resting at the side; 5 drinking, head back; 6 drinking; 7 bottle lowered to chest height in the rear hand, big grin; 8 the front arm opens to the crowd (final hold pose). Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/derrota.png`

Folha nova (170: hoje toca 0 a 5 e segura o 6, porque o 7 antigo tem um punho solto; a folha nova pode voltar a tocar 0 a 6 e segurar o 7). Na antiga ele senta e a caneleira some.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: defeat by time over. Frame 1 stance, shoulders dropping; 2 the legs give way and he falls back onto his seat; 3 sitting on the ground, legs stretched forward, the rear hand standing the bottle upright on the ground beside the hip, still gripping it; 4 the front arm thrown out, palm up, protesting, mouth open; 5 shouting, head pushed forward; 6 the front hand points forward, complaining; 7 he shrugs, front arm open, shaking his head; 8 slumped, head down, front hand on the knee (final hold pose). The shin guard stays visible on the same leg while he sits. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### D. Movimento (pedidos do Lote 5) (3)

#### `sprites/pengaro/quadros/folhas_arcade/anda.png`

Refazer (já é arcade, mas os quadros 3 e 7 levantam a MESMA perna). Mesmo MOTION do Lote 5. Com a folha nova o `LOOPS["anda_fluida"]` passa a usar os 8 desenhos.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: guarded walk forward, fists up, bottle hanging in the rear hand the whole time, a full two-step cycle where the two legs ALTERNATE: frame 1 contact, bare leg forward and shin-guard leg back; 2 weight sinks on the bare leg; 3 the shin-guard leg passes under the body with the knee high; 4 the shin-guard leg reaches forward; 5 contact with the legs swapped, shin-guard leg forward; 6 weight sinks on the shin-guard leg; 7 the BARE leg passes under the body with the knee high (never the shin-guard leg again); 8 the bare leg reaches forward and flows into frame 1. The shin guard stays on the same leg in all 8 frames, even when that leg is in front. The sash tips and the pant legs lag 1-2 frames behind the body. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/corre.png`

Folha nova (não existe corrida: `corre0..3` usam os desenhos do andar). Mesmo MOTION do Lote 5.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: run forward, torso leaning 20 degrees ahead, front fist pumping, bottle in the rear hand; a full cycle with the legs alternating: 1 contact on the bare leg; 2 push-off; 3 both feet off the ground with the shin-guard leg passing; 4 the shin-guard leg reaches; 5 contact on the shin-guard leg; 6 push-off; 7 both feet off the ground with the bare leg passing; 8 the bare leg reaches and flows into frame 1. The shin guard stays on the same leg in all 8 frames, even when that leg is in front. The sash tips fly straight back. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/recuo.png`

Folha nova (o recuo hoje é `defesa/06` deslizando). Mesmo MOTION do Lote 5.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: short hop backward out of the ginga stance, always facing right: 1 stance; 2 knees bend and the weight goes to the rear leg; 3 both feet leave the ground, body leaning slightly back, guard up; 4 highest point of a low hop, legs tucked a little; 5 the rear foot reaches back for the ground; 6 landing on the rear foot, front foot still in the air; 7 both feet down, knees absorbing; 8 back to the stance of frame 1. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### E. Opcionais: a folha em disco já entra, a nova só melhora (4)

#### `sprites/pengaro/quadros/folhas_arcade/agachado.png`

Opcional. A folha arcade em disco serve (convertida a 0,85), mas são 8 desenhos da mesma base respirando: não tem a descida. Guarda alta, sem mão no chão, porque `baixo_soco` e `chute_agachado` arcade saem e voltam dessa pose. Gerador: `agacha0..2` = 2, 4, 6; ação 11 = 4, 5, 6, 7, 6, 5; `defesa_baixa` = 7.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: crouching down and crouch idle. Frame 1 ginga stance; 2 knees bending, torso lowering, guard up; 3 halfway down; 4 deep crouch, heels down, front fist up guarding the chin, bottle in the rear hand beside the hip, head about 75% of the standing height; 5 to 8 the same deep crouch breathing, the head moving only 1-2 pixels, feet planted in exactly the same place. The crouching body keeps the same head and torso size as the standing frame. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/rasteirinha.png`

Opcional. A folha em disco serve pulando o desenho 4 (nele a mão da frente sai do chão e volta: o braço teletransporta) e descansa com a mão no chão, pose diferente do agachado arcade. Gerador: 430 pela `sequencia` (liga 1 e 2, caixa nos desenhos 3 e 4, volta 5, 6, 7).

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: short crouching sweep. Frame 1 deep crouch with the guard up, bottle in the rear hand beside the hip; 2 the front hand goes to the ground; 3 the front leg (bare shin) slides out along the ground; 4 that leg almost straight, low; 5 contact: leg fully extended close to the ground, the front hand STILL planted on the ground; 6 the leg folds back; 7 the front hand leaves the ground; 8 deep crouch with the guard up, same as frame 1. The shin guard is on the bent supporting rear leg. On the contact frame the striking hand or foot is drawn 15% larger than in frame 1; the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/queda.png`

Opcional. A folha em disco veio ~25% menor e foi reconvertida com fator por quadro (não reproduzível por `quantizar_folha.py`); no último desenho a caneleira não aparece. Mesmo MOTION do Lote 5. Gerador: 5050 = 1, 2, 3; 5100 = 4, 5, 6; 5110 = 6, 7; `deitado` = 7.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: knocked down, the body at the same size and scale as the attached sheet in every frame, including the standing ones. Frame 1 hit, head snapping back, still standing; 2 falling backward, feet leaving the ground; 3 body horizontal in the air; 4 the back hits the ground, legs up; 5 small bounce; 6 settling; 7 lying on the back, knees slightly bent; 8 lying flat on the back, head to the left. The shin guard and the bottle stay visible in all 8 frames, including the last one. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

#### `sprites/pengaro/quadros/folhas_arcade/bicicleta.png`

Opcional. A folha em disco serve com a caneleira pintada à mão nos desenhos 3, 4 e 5, mas a caneleira está na perna que chuta. Mesmo MOTION do Lote 5. Gerador: 650 = 2, 3, 4, 6; 610/611 = 1, 4, 6; `ar_chute` = 3, `bicicleta` = 4.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, same face, same dark hair, same skin tone, white
capoeira pants with green and yellow side stripes, short green waist sash with yellow tips, barefoot, olive-green shin
guard on one shin, amber whisky bottle with a plain white label in the rear hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE bottle, always held in the REAR
hand (the hand away from the opponent); it never changes hand and keeps its full shape (neck, body, white label). Exactly
ONE shin guard, olive green, on the shin of the REAR leg, the same leg as in the attached sheet; never on the other leg,
never on both, never a knee pad, never an ankle band. The sash is short, green with yellow tips, never a long hanging
cloth. Hair dark brown-black, never red or auburn. The body has the same size and proportions as in the attached sheet in
every frame: a standing frame is exactly as tall as the standing figure of the attached sheet.
Art style: generic hand-pixeled 1990s arcade 2D fighting game sprite, original character, not copied from any existing
game. Heroic anatomy: broad shoulders, narrow waist, big hands and feet, thick forearms and calves. Shading in 2-3 large
hard-edged flat planes per form, no gradients, no dithering, no noise, no texture, no veins, abdomen as 6 simple blocks.
Shadows shift hue: skin shadows go toward wine red, highlights toward warm cream; the white pants get cool lilac-blue
shadows, never grey or beige. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and
shin, one highlight band on the hair. Limited palette look. No brand, logo or text on the bottle or on any can.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects. Only this one man in the image, no opponent.
MOTION: airborne bicycle kick, no ground contact in any frame. Frame 1 airborne, knees tucked; 2 the body leans back; 3 the front leg (bare shin, no shin guard) lifts; 4 that leg whips up; 5 contact: front leg fully extended upward, body almost horizontal; 6 hold, same pose; 7 the leg folds, body rotating upright; 8 knees tucked, ready to land. The shin guard stays visible on the tucked rear leg in all 8 frames. On the contact frame the striking hand or foot is drawn 15% larger than in frame 1; the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. Exactly two arms and two legs in every frame; the bottle stays in the rear hand; one shin guard only, on the rear leg.
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### Contagem e ordem sugerida

| Grupo | Folhas | Quantas | Bloqueia o "100% arcade"? |
|---|---|---|---|
| A. Refazer (reprovadas) | `defesa`, `chute_baixo`, `rasteira` | 3 | sim |
| B. Especiais e agarrão | `bola`, `compasso`, `armada`, `caneta`, `rolamento`, `agarrao` | 6 | sim |
| C. Super e cenas | `golaco`, `lata`, `provoca`, `vitoria`, `derrota` | 5 | sim |
| D. Movimento | `anda`, `corre`, `recuo` | 3 | não (`anda` já é arcade; `corre` e `recuo` são desenho que falta) |
| E. Opcionais | `agachado`, `rasteirinha`, `queda`, `bicicleta` | 4 | não |
| **Total** | | **21** | **14 obrigatórias** |

Ordem sugerida (primeiro o que mais aparece numa luta):

1. `defesa`, `chute_baixo`, `rasteira`: golpes e defesa básicos, vistos em toda luta; sem eles o lutador continua
   trocando de arte.
2. `bola`, `compasso`, `armada`, `caneta`: os quatro especiais.
3. `rolamento`, `agarrao`.
4. `golaco`, `lata`, `provoca`, `vitoria`, `derrota`: super e cenas (uma vez por round ou menos).
5. `anda`, `corre`, `recuo`.
6. Se sobrar fôlego: `agachado`, `rasteirinha`, `queda`, `bicicleta`.

Cada grupo passa inteiro pelo pipeline e por um vídeo na sandbox antes de abrir o próximo: se `defesa`,
`chute_baixo` e `rasteira` não saírem no modelo com este prompt, ajustar o `MODEL LOCK` antes de gastar as outras.
