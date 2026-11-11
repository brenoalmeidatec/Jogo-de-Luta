# Fila de folhas do Hazak (ChatGPT, estilo arcade)

> Fila da recriação pedida na [`ficha`](../fichas/hazaki.md#pedido-para-o-alisson-recriar-o-hazak), montada em
> 2026-11-11. Ela substitui, para o Hazak, a tabela "Folhas em ordem" de [`hazaki.md`](hazaki.md#folhas-em-ordem-motion-como-vai-no-prompt),
> que era do kit antigo. A paleta e os problemas da arte antiga continuam valendo lá. A especificação do gerador que vai
> ler estas folhas fica em [`hazak_gerador.md`](hazak_gerador.md). Nada daqui foi gerado nem testado no motor.

## Como usar

1. **Um chat só:** "Hazak — arcade". Uma folha por mensagem, com o prompt inteiro (base + MOTION da linha).
2. **Anexe a folha-referência aprovada em toda mensagem:**
   - forma normal, vítima e objetos: `sprites/hazaki/quadros/folhas_arcade/parado.png` (já aprovada);
   - Diabo Loiro (`d_`): a `d_parado.png` depois de aprovada; para gerar a própria `d_parado`, anexe a `parado.png`;
   - patroa: a `patroa_parada.png` depois de aprovada; para gerar a própria, anexe a `parado.png` só como escala.
   Nunca anexe imagem de jogo comercial.
3. Salve exatamente em `sprites/hazaki/quadros/folhas_arcade/<folha>.png`. Nada fica em Downloads.
4. Aceite de cada folha (bíblia, Estilo arcade): 8 quadros inteiros, magenta liso, mesmo chão, virado para a direita,
   reconhecível ao lado da referência, **pulseira teal só no pulso de trás** em todos os quadros (o defeito que mais
   se repetiu), mesma escala da `parado` (em pé ~335–346 px na folha). Reprovou: gere de novo no mesmo chat.
5. Um lote inteiro passa pelo pipeline (`quantizar_folha` → Blender → `--meio` → `conferir_arte` → `video_golpe` na
   sandbox → uma pessoa olhando) antes de abrir o próximo.
6. Os objetos (`obj_`) são a **referência de desenho** para o efeito no pixelfx (regra 8: projétil e efeito saem do
   pixelfx, com PNG + JSON em `assets/efeitos/`). A folha não entra crua no `.sff`.

Toda linha de MOTION segue: 8 quadros numerados 1–8, virado para a direita, membro de contato 15% maior nos golpes, sem
efeito desenhado (fogo, brasa, poeira, rastro, faísca, dinheiro voando: tudo vira efeito à parte), sem texto. Nenhum
golpe copia pose-assinatura de jogo comercial (nada de palmas juntas soltando bola, nada de punho único reto para cima
saltando, nada de giro flutuando no ar várias voltas).

## Prompt base (forma normal)

Troque só o bloco MOTION.

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only (never on the front wrist, never missing), barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects (no fire, no sparks, no dust, no speed lines, no motion trails).
On every attack, the striking limb on the contact frame is drawn 15% larger.
MOTION: <bloco da folha>
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

## Prompt `d_` (Diabo Loiro de terno)

Mesmo prompt base, trocando o parágrafo do corpo (de "The attached sprite sheet" até "barefoot.") por este, e anexando
a `d_parado` aprovada:

```
The attached sprite sheet shows the exact man to keep, now in his transformed "blond devil" form: the same young
clean-shaven face (no beard, no goatee, no moustache), the same body size, height and proportions as the attached sheet;
long wild blond mane combed and swept straight back over the head and down the nape (never spiked upward), two short
curved dark horns growing from the forehead, glowing red eyes. He wears a flashy mafia boss suit: dark navy-purple
double-breasted pinstripe jacket and wide pinstripe trousers, white shirt, ember-orange tie, a big wide-brimmed dark hat
with an ember-orange band, a chunky gold ring on the front hand, dark brown leather dress shoes, the same teal wristband visible over
the shirt cuff of the rear wrist only. He carries a dark brown leather briefcase with gold clasps in the rear hand unless
the motion says otherwise. No logos, no flags, no real brand, no real money printed anywhere.
```

Para a `d_parado` em si, anexe a `parado.png` e acrescente ao fim do parágrafo: *"The attached sheet shows him before
the transformation, in the karate gi: keep exactly that face and body size."*

## Prompt da patroa

Mesmo prompt base, trocando o parágrafo do corpo por este (só para as folhas `patroa_`):

```
A different character: an ordinary adult Brazilian woman in her thirties, the fighter's partner, calm and confident.
Shoulder-length curly dark brown hair tied loosely, warm brown skin, plain casual clothes: a plain mustard t-shirt,
jeans, simple sneakers. Average build, realistic proportions, dignified
posture, the same pixel scale as the attached sheet (she is about 92% of his height). Not sexualized, not a caricature,
no blond hair, no makeup emphasis, no jewellery, no logos.
```

## Folhas em ordem

**Lote 1: o que o jogo precisa para lutar com o kit base** (estados básicos, 16 normais, vítima).

| Lote | Folha | Usada em (estado/golpe da ficha) | MOTION |
|---|---|---|---|
| 1 | `parado` | 0 parado (referência de tudo) | JÁ EXISTE, ok |
| 1 | `anda` | 20 andar e recuar andando | JÁ EXISTE, ok (o 100 correr ganha folha própria) |
| 1 | `corrida` | 100 correr, arranque do Pega Bolado e do Rapidinho, fuga da derrota | sprint run, the fastest runner in the game: torso leans far forward, fists low and pumping, 1 push-off with the rear leg, 2 airborne stride, 3 front foot lands, 4 passing, 5-8 the same with the other leg; long strides, belt tails stream straight back, the pant legs flap; 8 loops into 1. |
| 1 | `vira` | 5 virar em pé (quadros 1-4), 6 virar agachado (5-8) | turning around in place, seen from the side, the same body size in every frame: 1 guard facing right, 2 hips and shoulders start turning toward the viewer, chest shown, 3 almost facing the viewer, 4 guard facing left; 5 crouching guard facing right, 6 turning low toward the viewer, 7 almost facing the viewer, 8 crouching guard facing left. |
| 1 | `recuo` | 105 passo para trás (← ←) | quick backward hop in guard: 1 stance, 2 knees bend, 3 pushes off the front foot, 4-5 low hop backward with fists up, chin down, belt tails swing forward, 6 rear foot lands first, 7 front foot lands, 8 stance. |
| 1 | `agachado` | 10-12, guarda baixa, pouso | JÁ EXISTE, ok |
| 1 | `pulo` | 40-47, pulo para a frente e para trás | JÁ EXISTE, ok |
| 1 | `defesa` | 120-132 guarda em pé, parte da Guarda de Aço | JÁ EXISTE, retoque: tirar a teal do pulso da frente nos quadros 2-6 |
| 1 | `defesa_baixa` | 131/141/152 guarda agachada | crouching block: 1 deep crouch, 2-3 forearms cross low in front of the knees and chest, torso compacts, 4-5 holds the block with a small slide back on impact, 6-8 back to the crouch; 8 equals the crouch; belt tails flick on frame 4. |
| 1 | `apanha` | 5000-5030 tomar golpe em pé, tonto | JÁ EXISTE, ok (no pipeline vai no `POR_CELULA`: quadros 5 e 6 encostam) |
| 1 | `queda` | 5050-5100 cair, quicar, deitado | 1 airborne falling flat on the back, body horizontal, arms loose, 2 back hits the floor, 3 bounces slightly with the belt tails flying up, 4-8 lies still on the back, head toward the left, belt tails settling; same body length and scale as the attached sheet lying down (about as long as he is tall). |
| 1 | `levanta` | 5120 levantar | JÁ EXISTE, retoque: tirar a teal do pulso da frente nos quadros 3 e 4 |
| 1 | `vitima_agarrado` | vítima dos agarrões dos outros (números avulsos de `SPRITES_VITIMA` dentro de 48-50, 382-394 e 871-881) | being grabbed and thrown by an unseen opponent, no other character drawn: 1 standing hit, torso doubled forward, 2 lifted with feet off the ground, arms flailing, 3 tilted backward 45 degrees in the air, 4 upside down, head toward the ground, legs up, 5 horizontal face up in the air, 6 horizontal face down in the air, 7 curled and spinning, knees to chest, 8 stretched out face down just above the ground; belt tails always follow the motion. |
| 1 | `vitima_arremessado` | vítima: impacto e rolagem dos agarrões dos outros (890-910) | thrown victim hitting the floor: 1 falling head first at 45 degrees, 2 shoulder hits the floor, 3 back slams flat, legs up, 4 bounce with the whole body off the ground, 5 face down flat, 6 seated on the floor dazed, legs out, hands behind, 7 lying on the side, 8 lying flat face up. |
| 1 | `soco` | 200 x em pé (jab), 1º da corrente x | JÁ EXISTE, ok |
| 1 | `soco_reto` | 210 y em pé (soco reto), 1º da corrente y, 2º do Sai Daqui | heavy straight punch with the rear fist: 1 stance, 2 rear shoulder pulls back, hips coil, 3 front foot steps in, 4 hips and shoulders turn hard, 5 contact at head height with the rear fist 15% larger, rear shoulder fully forward, front fist back at the chin, 6 hold, 7-8 long recovery back to stance; gi top twists at the waist. |
| 1 | `chute_baixo` | 230 a em pé (chute baixo na canela), 1º da corrente a, 2º do Bom Dia, Vizinho | quick low kick with the front leg to the opponent's shin: 1 stance, 2 front knee lifts a little, 3 snaps the shin and instep out low, 4 contact at shin height with the foot 15% larger, standing leg bent, fists stay up, 5 hold, 6 knee recoils, 7-8 foot back down to stance. |
| 1 | `chute_lateral` | 240 b em pé (chute lateral), 1º da corrente b, 3º do Bom Dia, Vizinho | taekwondo side kick at chest height with the front leg: 1 stance, 2 rear foot slides in, 3 front knee chambers high across the body, hips turn sideways, 4 the leg drives out, 5 contact with the blade of the foot 15% larger, body fully sideways in one straight line from head to heel, 6 hold, 7 knee recoils, 8 back to stance; the pant leg flares open. |
| 1 | `baixo_soco` | 400 ↓ + x (jab baixo), 2º da Rasteira de Calçada | JÁ EXISTE, ok |
| 1 | `joelhada_baixo` | 410 ↓ + y (joelhada subindo, antiaéreo), fecho do Sobe, Mentiroso | rising knee from a crouch: 1 deep crouch, 2 coils, rear knee drops, 3 springs up onto the standing foot, 4 rear knee drives up and forward above chest height, both forearms guarding the head, 5 contact with the knee 15% larger at head height, 6 hold on the toes, 7-8 drops back into the crouch; feet never leave the ground line; belt tails whip up. |
| 1 | `chute_canela` | 430 ↓ + a (chute na canela) | crouching short kick: 1 deep crouch, 2 front knee lifts slightly, 3 snaps the front foot out flat along the floor, 4 contact at ankle height with the foot 15% larger, torso stays low and upright, fists up, 5 hold, 6-8 foot pulls back to the crouch. |
| 1 | `rasteira_arco` | 440 ↓ + b (rasteira que derruba) | crouching sweep: 1 deep crouch, 2 both hands drop to the floor beside the front foot, 3 body pivots low on the front foot, the rear leg starts a wide arc along the floor, 4 the leg sweeps forward close to the ground, 5 contact at ankle height with the leg and heel 15% larger, the pant leg flared, 6 hold, 7-8 long recovery back to the crouch. |
| 1 | `ar_soco` | 600 x no ar (soco de martelo) | REFAZER: mid-air downward hammer fist with the FRONT arm only: 1 tucked jump pose, 2 the front fist rises above the head, rear fist stays at the chest with the teal band, 3 the front fist starts down, 4 swings down and forward, 5 contact angled down 45 degrees, front fist 15% larger, 6 hold, 7-8 tuck again; the rear arm never swaps with the front arm. |
| 1 | `ar_cotovelo` | 601 y no ar (cotovelo descendo) | mid-air dropping elbow: 1 tucked jump pose, 2 front arm folds high, elbow pointing up, 3 torso turns, 4 elbow drives down and forward, 5 contact with the front elbow 15% larger pointing down 60 degrees, knees tucked, 6 hold, 7-8 tuck again. |
| 1 | `ar_joelho` | 610 a no ar (joelhada) | mid-air knee strike: 1 tucked jump pose, 2 front knee pulls up, 3 hips thrust forward, 4 knee drives forward at chest height, both fists pull down, 5 contact with the knee 15% larger, rear leg trailing straight, 6 hold, 7-8 tuck again. |
| 1 | `ar_chute` | 650 afastar no ar, chute aéreo neutro | JÁ EXISTE, ok |
| 1 | `ar_chute_duplo` | 611 b no ar (chute duplo, cross-up) | mid-air double kick, two quick kicks with alternating legs pointing down: 1 tucked jump pose, 2 front leg chambers, 3 first contact, front foot 15% larger kicking down-forward at 45 degrees, 4 front leg pulls back while the rear leg chambers, 5 second contact, rear foot 15% larger kicking down-forward, 6 hold, 7-8 tuck again. |

**Lote 2: correntes, direcionais e kombos.**

| Lote | Folha | Usada em | MOTION |
|---|---|---|---|
| 2 | `jab_duplo` | 301 corrente x, 2º (jab duplo) | double jab with the front fist: 1 guard after a jab, 2 first jab out, 3 first contact, fist 15% larger, 4 half retract, 5 second jab out, slightly higher, 6 second contact, fist 15% larger, 7-8 back to guard. |
| 2 | `cutucao` | 302 corrente x, 3º (Cutucão Sacana) | sneaky two-finger poke to the ribs, close range: 1 guard, 2 steps in with a cheeky grin, 3 front hand drops low with index and middle fingers extended, 4 jabs the fingers forward at rib height, 5 contact with the hand 15% larger, wrist twisting, 6 hold with a mocking smile, 7-8 hops back to guard. |
| 2 | `tapa_costas` | 303 corrente x, finalizador (Tá Achando Ruim?) | spinning backhand slap that knocks down: 1 guard, 2 front arm folds across the chest, 3 hips turn away, back partly shown, 4 spins back around, arm whipping out, 5 contact with the back of the front hand 15% larger at head height, arm fully extended, 6 hold, 7 follow-through, 8 stance with chin up. |
| 2 | `cruzado` | 311 corrente y, 2º (cruzado) | hook punch with the front fist: 1 guard, 2 front elbow lifts to shoulder height, 3 hips turn, 4 fist curves in horizontally, 5 contact at jaw height with the fist 15% larger, elbow bent 90 degrees, 6 hold, 7-8 back to guard. |
| 2 | `cotovelada` | 312 corrente y, 3º (cotovelada descendo) | downward elbow: 1 guard, 2 rear elbow rises high above the head, up on the toes, 3 torso leans forward, 4 drops the elbow and the body weight down, 5 contact at collarbone height with the elbow 15% larger, knees bent, 6 hold, 7-8 back to guard. |
| 2 | `calcada_levantada` | 313 corrente y, finalizador (Calçada Levantada, ex-"Punho de Concreto curto"; lança) | drops to one knee and hammers the floor right at the opponent's feet: 1 guard, 2 steps in and raises the rear fist high, 3 drops onto the rear knee, 4 fist comes down, 5 contact with the rear fist 15% larger driven into the ground line just in front of the front foot, 6 hold, 7 pushes up from the knee, 8 stance. No upward punch. |
| 2 | `chute` | 321 corrente a, 2º (chute na cintura com a mesma perna) | JÁ EXISTE, ok |
| 2 | `chute_alto_rajada` | 322 corrente a, 3º (chute alto sem descer o pé); rajada do Super Faixa no Asfalto | rapid same-leg kicks without putting the foot down, standing leg fixed: 1 front knee chambered high on one leg, 2 high kick contact at head height, foot 15% larger, 3 re-chambers without lowering, 4 middle kick contact at chest height, foot 15% larger, 5 re-chambers, 6 high kick contact again, foot 15% larger, 7 re-chambers, 8 foot comes down to stance. |
| 2 | `tesoura` | 323 corrente a, finalizador (Tesoura de Bairro, giro 540°) | grounded 540 spin kick, pivoting on the standing foot, never leaving the ground: 1 stance, 2 steps across and loads, 3 pivots showing the back, 4 keeps turning, chest toward the viewer, rear leg chambered, 5 back shown again, the rear leg whips around, 6 contact with the rear foot 15% larger at head height after one and a half turns (540 degrees), torso upright, 7 the kicking leg comes down in front, 8 stance facing right. Close to the ground, never hovering, no jump. |
| 2 | `chute_giratorio` | 331 corrente b, 2º (chute giratório) | spinning back kick: 1 guard, 2 front foot pivots, 3 turns showing the back, looking over the shoulder, 4 rear knee chambers, 5 contact with the rear heel 15% larger at stomach height, leg straight back toward the opponent, 6 hold, 7 recovers turning, 8 guard facing right. |
| 2 | `chute_gancho` | 332 corrente b, 3º (chute de gancho na cabeça) | hook kick to the head with the front leg: 1 guard, 2 front knee chambers high, 3 leg extends past the target, 4 snaps back in a hooking arc, 5 contact with the heel 15% larger at head height, leg bent, 6 hold, 7 knee recoils, 8 stance. |
| 2 | `machado` | 333 corrente b, finalizador (Machado de Dojô completo, quica); fecho do Super Faixa no Asfalto | full axe kick from very high: 1 stance, 2 front leg swings straight up, 3 leg vertical above the head, torso leaning back, up on the toes, 4 apex, heel above the head, 5 heel chops down, contact at head height with the foot 15% larger, 6 heel drives to the floor, knees bent, 7 hold low, 8 stance. |
| 2 | `machado_curto` | 246 → + b (Machado Curto, por cima), abertura do Bom Dia, Vizinho | short quick axe kick (overhead): 1 stance, 2 front leg lifts bent to chest height, 3 the leg straightens up to head height, 4 heel starts down, 5 contact at head height with the heel 15% larger, 6 hold, 7-8 steps down into stance; smaller arc and faster than a full axe kick. |
| 2 | `cotovelo_faixa` | 216 → + y (Cotovelo de Faixa), fecho do Sai Daqui | stepping horizontal elbow: 1 stance, 2 big step forward, front arm folds, 3 hips turn, 4 front elbow drives forward at chest height, 5 contact with the elbow 15% larger, body weight fully forward, belt tails flung back, 6 hold, 7-8 back to stance. |
| 2 | `cutucao_recuo` | 201 ← + x (Cutucão Sacana de longe), abertura do Sai Daqui | mocking long poke while stepping back: 1 stance, 2 leans the torso back, 3 the front arm stretches far forward with two fingers extended, 4 contact at belly height with the hand 15% larger, body leaning away, 5 wiggles the fingers, 6 hold, 7-8 back to stance grinning. |
| 2 | `coice` | 231 ← + a (coice de calcanhar para trás) | backward heel kick without turning around: 1 stance, 2 leans forward, rear knee lifts, 3 rear leg extends straight back behind him, 4 contact behind with the heel 15% larger at stomach height, torso low, looking back over the shoulder, 5 hold, 6 knee recoils, 7-8 stance facing right. |

Os kombos usam as folhas dos golpes que encadeiam (Bom Dia, Vizinho: `machado_curto`, `chute_baixo`,
`chute_lateral`; Rasteira de Calçada: `soco`, `chute_canela`, `chute_lateral`; Sai Daqui: `cutucao_recuo`,
`soco_reto`, `cotovelo_faixa`; Sobe, Mentiroso: `chute_baixo`, `chute_lateral`, `joelhada_baixo`), cada um com o
próprio ritmo e caixa no gerador.

**Lote 3: especiais, agarrões, supers e os objetos da forma base.**

| Lote | Folha | Usada em | MOTION |
|---|---|---|---|
| 3 | `punho_chao` | 1000/1001 Punho de Concreto (projétil baixo) | lunging low punch that scrapes the floor: 1 stance, 2 long step in, rear fist drawn back at the hip, 3 drops low into a wide stance, 4 the rear fist drives forward and down, 5 contact: knuckles 15% larger striking the ground line one step ahead of the front foot, arm straight, 6 hold low, 7-8 rises back to stance. No projectile drawn. |
| 3 | `estatueta_arremesso` | 1600/1601 Estatueta Dourada (projétil em arco) | underhand-to-overhand lob throw holding a small object in the rear hand: 1 stance, rear hand holding a small stocky golden figure in a wide karate stance with both fists up, thick limbs, on a rough round rock base, at the hip, 2 rear arm swings back low, 3 swings up behind the head, 4 body leans forward, 5 releases the figurine upward and forward at 45 degrees, hand open 15% larger, 6 follow-through, 7-8 back to stance. Draw the figurine only in frames 1-4. |
| 3 | `ascensao` | 1200/1201 Ascensão de Faixa (antiaéreo) | REFAZER: rising knee-and-shoulder anti-air, feet stay on the ground line: 1 deep crouch, 2 coils, front shoulder tucked, 3 surges up onto the toes of the rear foot, 4 front knee drives up to chest height while the front shoulder and forearm rise in front of the face, belt tails whipping up, 5 contact with knee and shoulder 15% larger at head height, 6 hold on the toes, 7-8 settles back to stance. No fist straight up, no jump. Same navy gi colors and line thickness as the attached sheet. |
| 3 | `giro_garagem` | 1300/1301 Giro de Garagem (avanço de meia tela) | advancing grounded spinning kick: 1 stance, 2 front foot steps across, 3 spins on the ball of the foot showing the back, 4 the rear leg swings around low and wide, 5 contact with the rear heel 15% larger at waist height, leg straight, 6 hold, 7 second step forward, 8 recovers facing right. Always grounded. |
| 3 | `rasteira` | 1400/1401 Corte de Base (golpe baixo, desliza com a perna esticada) | JÁ EXISTE, retoque: pintar a teal no pulso de trás nos quadros 2-6 |
| 3 | `rolada_tatame` | 1700/1701 Rolada de Tatame (vai para trás do oponente, chega virado) | forward shoulder roll that ends facing the other way: 1 stance, 2 dives low forward tucking the chin, 3 shoulder touches the floor, 4 rolling over the back, legs over, 5 coming up on one knee, 6 rising, 7-8 guard stance; every frame faces right (the game turns him around) and keeps the same body size. |
| 3 | `voadora` | 1500/1501 Pega Bolado (voadora de dois pés), fecho do Rapidinho | running two-footed dropkick: 1 last running stride, 2 jumps forward, both knees tuck, 3 airborne leaning back, 4 both legs shoot forward together, 5 contact with both soles 15% larger at chest height, body horizontal, 6 hold, 7 falls onto the back, 8 rolls up to a crouch. |
| 3 | `guarda_aco` | 1100/1101 Guarda de Aço (defende e responde com chute) | parry and counter: 1 stance, 2 forearms snap up into a high block, 3 holds the block, body braced, 4 pushes the blocked arm away with the front forearm, 5 the front knee lifts, 6 front snap kick contact at stomach height with the foot 15% larger, 7 knee recoils, 8 stance. |
| 3 | `agarrao_abraco` | 800/810 Abraço de Quebrada (agarrão em pé) | bear hug and over-the-shoulder throw of an unseen opponent, only him drawn: 1 reaches forward with both arms open, 2 wraps both arms around an invisible torso at chest height, 3 squeezes, leaning back, 4 lifts, knees bent, chest out, 5 turns the hips under, 6 heaves over the right shoulder, arms up and back, 7 arms open, releasing, 8 stance, dusting off the hands. |
| 3 | `agarrao_perna` | 840/841 Puxa a Perna (agarrão agachado) | low leg grab of an unseen crouching opponent, only him drawn: 1 crouch, 2 lunges low, both hands forward at ankle height, 3 grabs an invisible ankle, 4 pulls back hard, leaning away, 5 yanks upward, 6 steps back still pulling, 7 lets go, 8 back to the crouch. |
| 3 | `agarrao_cutucao` | 830/831 Cutucão Sacana (agarrão de comando, lore) | headlock and rib tickle of an unseen opponent, only him drawn: 1 steps in, 2 front arm wraps around an invisible neck at shoulder height, 3 locks the headlock, grinning, 4 rear hand pokes forward at rib height with two fingers, 5 pokes again lower, 6 pokes again higher, laughing, 7 releases the headlock with a push, 8 stance wagging the index finger. |
| 3 | `pose_super` | começo do 3000 e do 3200 (superpausa) | super move activation pose: 1 stance, 2 stomps the front foot, 3 pulls the belt tight with both hands, 4 chin down, eyes hard, 5 shoots both fists down to the sides, chest out, 6 holds, 7 drops into a low fighting stance, 8 holds; no glow drawn. |
| 3 | `sobe_chutando` | 3000 Faixa no Asfalto (sobe chutando) | rising kicks off one leg, climbing upward: 1 low stance, 2 jumps up kicking with the front leg at chest height, contact foot 15% larger, 3 still rising, the same front leg re-chambers and kicks at head height, foot 15% larger, the rear leg stays folded under the body, 4 the same front leg kicks again higher, foot 15% larger, 5 apex, knee chambered, 6 axe kick starting, 7 heel coming down, 8 landing in a deep stance. |
| 3 | `passagem_rapida` | 3200 Rapidinho da Quebrada (passagens pela tela) | dash-through strike at full speed: 1 sprint stride, body almost horizontal, 2 lowers the front shoulder, 3 passes striking with a low front palm at stomach height, palm 15% larger, 4 keeps running past, 5 plants the front foot to brake, 6 skids turning, 7 crouched low, 8 explodes into the next sprint. |
| 3 | `obj_lasca` | projétil do Punho de Concreto (referência para o pixelfx) | a single chunk of broken grey asphalt the size of his forearm, flat and jagged, rolling and bouncing along the ground line from left to right: 1-8 the same chunk rotating a quarter turn at a time, with small loose pebbles that change position; no dust, no glow. |
| 3 | `obj_estatueta` | projétil da Estatueta Dourada (referência para o pixelfx) | a small golden figure as tall as his forearm: a stocky golden figure in a wide karate stance with both fists up, thick limbs, simple blank face, on a rough round rock base; it must not look like any award or trophy; 1-8 the figurine tumbling end over end one eighth of a turn per frame; gold with hard flat highlights. |

**Lote 4: personalidade e a parte normal da cena do Despertar.**

| Lote | Folha | Usada em | MOTION |
|---|---|---|---|
| 4 | `intro` | 191 intro ("Bora ver se aguenta o treino.") | 1 stance looking at the camera, 2 cracks the knuckles, 3 rolls the neck, 4 bounces on the toes, 5 shadow-boxes a quick jab, 6 quick low kick in the air, 7 smirks, 8 drops into the fighting guard. |
| 4 | `vitoria` | 180/181 vitória ("EU SOU GOSTOSO!") | 1 relaxed stance, 2 grabs both belt tails, 3 ties the belt with a sharp pull, 4 chest out, chin up, 5 points the index finger forward, 6 wags the finger to the left, 7 wags to the right, 8 fists on the hips grinning; 8 holds. |
| 4 | `provoca` | 195 provocação c ("Australopiteco mentiroso!") | 1 stance, 2 leans forward with a mocking face, 3 raises the front hand, index finger up, 4 wags the finger left, 5 wags right, 6 wags left, 7 rear hand on the hip laughing, 8 back to stance; loops 3-6. |
| 4 | `derrota_sirene` | 171 derrota por nocaute (quadros 1-8) e 170 por tempo (4-8): ouve a sirene, levanta num pulo e foge | 1 lying flat face up, 2 eyes snap open, head lifts, startled, 3 springs up off the floor in one jump, arms flailing, 4 lands crouched, looking left over the shoulder, panicked, 5 turns his body to face left, 6 first running stride to the left, 7-8 running away to the left in full sprint; no police, no car drawn. |
| 4 | `despertar_pedido` | 2000, começo (bate o pé, olha para trás e pergunta) | 1 stance, 2 lifts the front foot, 3 stomps the floor, 4 looks back over the rear shoulder toward the left, 5 hands together in a pleading gesture, eyebrows up, 6 holds the pleading look, 7 hears the answer, a huge grin, 8 turns back to face right, fists clenched, bending forward ready to transform. |
| 4 | `patroa_parada` | referência da patroa; helper do 2000 | (prompt da patroa) standing idle, arms crossed, weight on one leg, facing right, calm face, small breathing motion: 1-4 shoulders sink slightly, 5-8 rise; 8 loops into 1. |
| 4 | `patroa_chega_sim` | helper do 2000 (aparece no fundo e faz que sim) | (prompt da patroa) 1 walking in from the left, 2 next step, 3 stops, 4 hands on the hips, eyebrows raised, 5 nods once, chin down, 6 nods again with a small smile, 7 waves one hand toward the arena as "go ahead", 8 holds the wave. |
| 4 | `patroa_sai` | helper do 2000 (sai da arena) | (prompt da patroa) 1 standing facing right, 2 turns around to face left, 3-8 walks away to the left at a calm pace, two-step cycle, hair bouncing. |

**Lote 5: Diabo Loiro, estados básicos e a virada.** Todas com o prompt `d_`.

| Lote | Folha | Usada em | MOTION |
|---|---|---|---|
| 5 | `d_parado` | 10000 parado desperto (referência de todas as `d_`) | standing guard with the briefcase held low in the rear hand, front fist up wearing the gold ring, hat brim low, weight on the back leg, slow confident breathing bounce: 1-4 sink slightly, 5-8 rise; jacket tails sway one frame behind the hips; 8 loops into 1; feet never slide. |
| 5 | `despertar_virada` | 2000, transformação (gi vira terno) | (prompt base normal, anexando `parado.png` e `d_parado.png`) the karate fighter turns into the blond devil in a mafia suit: 1 bent forward in the gi, fists clenched, 2 hair starts growing longer and lighter, 3 hair turns blond and sweeps back, two horns push out of the forehead, 4 eyes glow red, the gi darkens, 5 the gi turns into the pinstripe suit from the shoulders down, 6 the hat appears on the head, 7 straightens up, the briefcase appears in the rear hand, 8 final pose of the suited form, full body, exactly like the second attached sheet. Same body size in every frame. |
| 5 | `d_vira` | 10005/10006 virar desperto | turning around in place in the suit, briefcase in the rear hand, the same body size in every frame: 1 guard facing right, 2 turning toward the viewer, 3 almost facing the viewer, 4 guard facing left; 5 crouching guard facing right, 6 turning low, 7 almost facing the viewer, 8 crouching guard facing left. |
| 5 | `d_anda` | 10020 andar desperto | slow swaggering forward walk, stride about 80% as long as the base walk, briefcase swinging in the rear hand, front fist up, two-step cycle: 1 front foot contact, 2 down, 3 passing, 4 up, 5-8 the same with the other leg; jacket tails and tie swing; 8 loops into 1. |
| 5 | `d_corrida` | 10100 correr desperto, arranque do Pega Bolado desperto | heavy running, stride about 80% as long as the base run, one hand holding the hat on the head, briefcase pumping in the rear hand, torso leaning forward: 1 push-off, 2 airborne stride, 3 landing, 4 passing, 5-8 the same with the other leg; tie flies back over the shoulder; 8 loops into 1. |
| 5 | `d_agachado` | 10010-10012 agachar desperto | 1 standing guard with the briefcase, 2-4 lowers into a crouch holding the briefcase in front of the shins like a shield, 5-8 holds the crouch with a small breathing bounce; 8 loops into 5. |
| 5 | `d_pulo` | 10040-10047 pulo desperto | jump holding the hat with the front hand and the briefcase in the rear: 1 crouch load, 2 push-off, 3-4 rising with knees tucking, 5 apex tucked, 6-7 falling with legs opening, 8 landing reach; jacket tails trail the motion. |
| 5 | `d_defesa` | 10120-10132 guarda em pé desperto | blocks with the briefcase: 1 stance, 2-3 raises the briefcase flat in front of the face and chest with both hands, 4-5 holds the block with a small push back on impact, 6-8 back to stance. |
| 5 | `d_defesa_baixa` | 10131/10141/10152 guarda agachada desperta | crouching block with the briefcase held vertical in front of the knees: 1 crouch, 2-3 briefcase comes down, 4-5 holds with a small slide back, 6-8 back to the crouch. |
| 5 | `d_apanha` | 15000-15030 tomar golpe desperto | hit reaction: 1 stance, 2 head snaps back, the hat tilts, 3-4 staggers back, briefcase swinging, 5-6 leans and starts falling backward, 7-8 airborne falling flat, holding the hat. |
| 5 | `d_queda` | 15050-15100 cair desperto | 1 airborne falling flat, 2 back hits the floor, 3 bounces, the hat pops up a little, 4-8 lies still, hat back on the chest, briefcase beside him; same body length as the attached sheet lying down. |
| 5 | `d_levanta` | 15120 levantar desperto | 1 lying flat, 2 rolls to the side, 3 hand pushes on the floor, 4 knee under, 5 kneeling, puts the hat back on, 6 rising, grabbing the briefcase, 7 straightens the tie, 8 stance. |
| 5 | `d_vitoria` | 10181 vitória desperto | 1 relaxed stance, 2 straightens the tie, 3 tips the hat brim with two fingers, 4 opens the briefcase toward the viewer, 5 snaps it shut, 6 points the ringed index finger forward, 7 wags the finger, 8 hat tipped low, grinning; 8 holds. |

**Lote 6: kit novo do Diabo Loiro e os objetos dele.** Prompt `d_`.

| Lote | Folha | Usada em | MOTION |
|---|---|---|---|
| 6 | `d_maletada_lado` | 3410 corrente y desperta, 1º (maletada de lado); 349 Sociedade Fechada; 3100 | forehand briefcase swing: 1 guard, briefcase low in the rear hand, 2 briefcase pulled back behind the hip, 3 hips turn, the arm starts around, 4 briefcase swings in flat, 5 contact at head height with the briefcase 15% larger, arm extended, 6 hold, 7 follow-through across the body, 8 back to guard. |
| 6 | `d_maletada_volta` | 3411 corrente y desperta, 2º (maletada de volta); 3100 | backhand briefcase swing coming back: 1 briefcase across the body after a swing, 2 shoulders coil the other way, 3 elbow leads back, 4 briefcase swings back flat, 5 contact at head height with the briefcase 15% larger, back of the hand forward, 6 hold, 7 the briefcase drifts down, 8 back to guard. |
| 6 | `d_maletada_cima` | 3412 corrente y desperta, 3º (maletada de cima); 3100 | overhead briefcase chop: 1 guard, 2 grabs the briefcase with both hands, 3 raises it high over the head, up on the toes, 4 starts down, body weight dropping, 5 contact at head height with the briefcase 15% larger, knees bent, 6 hold, 7 briefcase at knee height, 8 back to guard. |
| 6 | `d_negocio_fechado` | 3413 corrente y desperta, finalizador (Negócio Fechado, derruba) | 1 guard, 2 holds the briefcase in front with both hands, 3 snaps it open toward the opponent at face height, 4 leans in, 5 slams it shut forward, contact with the briefcase 15% larger at head height, 6 shoves forward, 7 hold, 8 tucks the briefcase under the arm, stance. |
| 6 | `d_sapato_canela` | 3420 corrente b desperta, 1º (sapato na canela) | heavy dress-shoe kick to the shin with the front leg: 1 stance, 2 weight shifts back, 3 front knee lifts, 4 the shin snaps out low, 5 contact at shin height with the shoe 15% larger, standing leg bent, 6 hold, 7 knee recoils, 8 stance. |
| 6 | `d_sapato_barriga` | 3421 corrente b desperta, 2º (sapato na barriga) | heavy push kick to the stomach with the front leg: 1 stance, 2 front knee chambers high, 3 hips lean back, 4 the leg drives straight out, 5 contact at stomach height with the shoe sole 15% larger, 6 hold, 7 knee recoils, 8 stance. |
| 6 | `d_coice_costas` | 3422 corrente b desperta, 3º (coice de costas) | turns and mule-kicks: 1 guard, 2 turns showing the back of the jacket, 3 bends forward, hat held with one hand, 4 rear leg shoots straight back toward the opponent, 5 contact with the shoe sole 15% larger at stomach height, 6 hold, 7 turns back, 8 guard facing right. |
| 6 | `d_pisao_chefe` | 3423 corrente b desperta, finalizador (Pisão de Chefe, derruba) | 1 guard, 2 front knee rises high, 3 holds the knee up looking down, 4 stomps down forward, 5 contact with the shoe sole 15% larger at knee height driving down to the floor, 6 weight on the stomping leg, 7 straightens the tie with both hands, 8 stance. |
| 6 | `d_maleta_sobe` | 3430 ↓ + y desperto (maleta subindo, antiaéreo) | from a crouch, swings the briefcase straight up: 1 crouch, briefcase low, 2 coils, 3 rises onto the toes, 4 briefcase swings up in front of the face, 5 contact above the head with the briefcase 15% larger, arm straight up holding the handle, 6 hold, 7-8 back to the crouch. Feet stay on the ground. |
| 6 | `d_chapelada` | 3432 → + b desperto (chapelada por cima), 348 Sociedade Fechada | overhead hat strike: 1 stance, 2 takes off the hat with the front hand, 3 raises it high, up on the toes, 4 swings it down, 5 contact at head height with the hat brim 15% larger, 6 hold, 7 puts the hat back on, 8 stance. |
| 6 | `d_tapa_anel` | 3431 x em pé desperto (tapa com anel), abertura da Sociedade Fechada | open backhand slap with the ringed front hand: 1 guard, 2 front hand rises across the chest, 3 whips out, 4 contact at face height with the back of the hand 15% larger, gold ring forward, 5 hold, 6-8 back to guard. |
| 6 | `d_dedo` | 3433 ← + x desperto (dedo balançando, anula projétil fraco); provocação c desperta | 1 stance, 2 front arm extends forward, ringed index finger up, 3 wags left, 4 wags right, 5 wags left, 6 wags right, 7 lowers the hand smirking, 8 stance. |
| 6 | `d_pisao_ar` | 3435 b no ar desperto (pisão de sapato descendo) | mid-air dropping stomp: 1 tucked jump pose holding the hat, 2 front knee pulls up, 3 leg drives down, 4 sole pointing down-forward at 60 degrees, 5 contact with the shoe sole 15% larger, 6 hold, 7-8 tuck. |
| 6 | `d_bico_sapato` | 3434 ↓ + a desperto (chute de bico de sapato) | crouching toe kick: 1 crouch, 2 front foot lifts, 3 snaps out low, 4 contact at ankle height with the shoe tip 15% larger, 5 hold, 6-8 back to the crouch. |
| 6 | `d_chapeu_arremesso` | 3400/3401 Chapéu Bumerangue | low sidearm hat throw at waist height: 1 stance, 2 takes off the hat and lowers it to the hip, 3 crouches slightly, the arm swings back low beside the body, 4 swings forward low and flat, 5 releases at waist height, hand open forward 15% larger, hat gone (not drawn), 6 waits, hand on the hip, 7 looks up, bare head, 8 the hat lands back on his head by itself (hat drawn on the head), stance. Never thrown from the head with a flick, no blade on the brim. |
| 6 | `d_maleta_giro` | 3402/3403 Maleta Giratória (avanço, várias batidas) | advancing spin swinging the briefcase at arm's length, grounded: 1 stance, 2 steps forward, briefcase out wide, 3 spins showing the back, 4 briefcase comes around at chest height, contact briefcase 15% larger, 5 spins again, 6 second contact, briefcase 15% larger, 7 slows, 8 stance facing right. |
| 6 | `d_nota_falsa` | 3404/3405 Nota Falsa (armadilha) | crouches and leaves a bundle of cash on the floor: 1 stance, 2 takes a bundle out of the inner jacket pocket, 3 crouches, 4 sets the bundle on the floor in front of him, 5 pats it, 6 rises, hand empty, 7 winks, 8 stance. The bundle is plain paper with a paper band, no printed money. |
| 6 | `d_suborno` | 3406/3407 Suborno (agarrão de comando: oferece o maço e bate) | 1 stance, 2 holds a cash bundle forward at chest height with the front hand, friendly grin, 3 holds still as if someone takes it, 4 the empty hand pulls back, 5 the briefcase swings up from below with the rear hand, 6 contact at chin height with the briefcase 15% larger, 7 follow-through, 8 stance. |
| 6 | `d_estatueta` | 11600/11601 Estatueta Dourada desperta (maior, vira obstáculo) | two-handed heavy lob throw: 1 stance, holding a big stocky golden figure in a wide karate stance with both fists up, on a rough round rock base, against the chest with both hands, 2 squats down, 3 heaves it up over the head, 4 leans back, 5 throws it forward and up at 45 degrees, both hands open 15% larger, 6 follow-through, 7-8 back to stance. Figurine drawn only in frames 1-4. |
| 6 | `d_voadora_sapato` | 11500/11501 Pega Bolado desperto (voadora de sapato, quica) | running two-footed dropkick in the suit: 1 last stride holding the hat, 2 jumps forward, knees tucked, 3 airborne leaning back, 4 both shoes shoot forward, 5 contact with both soles 15% larger at chest height, 6 hold, 7 lands on the back, 8 rolls up to a crouch fixing the hat. |
| 6 | `d_punho_anel` | 11000/11001 Punho de Concreto desperto (soco com anel, lasca em brasa) | lunging low punch with the ringed hand scraping the floor: 1 stance, 2 long step in, front fist drawn back, ring shining, 3 drops low, 4 drives the fist forward and down, 5 contact with the ringed knuckles 15% larger at the ground line one step ahead, 6 hold low, 7-8 rises to stance. |
| 6 | `d_fumaca` | 11700/11701 Rolada de Tatame desperta (some e reaparece atrás) | vanishing and reappearing, the body shrinks into a crouch and pops back: 1 stance, 2 crouches holding the hat, 3 crouched smaller, 4 curled tight, smallest, 5 still curled tight, 6 opening up, 7 rising, 8 guard stance; every frame faces right (the game turns him around). No smoke drawn. |
| 6 | `d_chuva_abre` | 3100 Chuva de Dinheiro, abertura e superpausa | 1 stance, 2 lifts the briefcase in front with both hands, 3 grins, 4 snaps it open toward the sky, 5 holds it open overhead, 6 shakes it, 7 snaps the briefcase shut and grips it by the handle, ready to swing, 8 drops into a low stance, briefcase in the rear hand. No money drawn. |
| 6 | `d_estatueta_gigante` | 3100 Chuva de Dinheiro, fecho (Estatueta Dourada gigante) | 1 stance, 2 reaches up, 3 holds a huge stocky golden figure in a wide karate stance with both fists up, on a rough round rock base, taller than himself, over the head with both hands, knees bent, 4 leans back, 5 slams it forward and down, contact at head height with the figurine 15% larger, 6 it hits the ground line, 7 lets go, 8 dusts off the hands, stance. |
| 6 | `obj_chapeu` | projétil do Chapéu Bumerangue (referência para o pixelfx) | the same wide-brimmed dark hat with an ember-orange band, flying flat and spinning: 1-8 the hat seen from the side rotating one eighth of a turn per frame, brim tilting slightly. |
| 6 | `obj_maco` | Nota Falsa (maço no chão e estouro) | 1-4 a plain bundle of rectangular paper notes with a paper band, lying on the floor, a tiny bounce, 5 the band snaps, 6 the notes burst upward, 7 notes scatter, 8 the last notes fly away. Plain paper with no numbers, no faces, no symbols. |
| 6 | `obj_papel` | estouro da Nota Falsa e chuva do 3100 | eight small loose blank paper notes and scraps falling and fluttering, each frame the same set rotated and slightly lower, light cream paper with a cool shadow, no printing. |

**Lote 7: Diabo Loiro, o que ele herda da base** (normais que continuam, passo para trás, agarrões e afastar; até a
folha existir, a ação desperta usa o quebra-galho de paleta descrito em `hazak_gerador.md`). y e b em pé não têm
folha aqui: no Despertar eles abrem as correntes novas (`d_maletada_lado`, `d_sapato_canela`).

| Lote | Folha | Usada em | MOTION |
|---|---|---|---|
| 7 | `d_recuo` | 10105 passo para trás desperto | quick backward hop in the suit, one hand holding the hat, briefcase in the rear hand: 1 stance, 2 knees bend, 3 pushes off the front foot, 4-5 low hop backward, jacket tails and tie swing forward, 6 rear foot lands first, 7 front foot lands, 8 stance. |
| 7 | `d_agarrao_abraco` | 10800/10810 Abraço de Quebrada desperto | bear hug and over-the-shoulder throw of an unseen opponent in the suit, briefcase dropped at his feet in frame 1 and picked up in frame 8, only him drawn: 1 reaches forward with both arms open, 2 wraps both arms around an invisible torso at chest height, 3 squeezes, leaning back, 4 lifts, knees bent, 5 turns the hips under, 6 heaves over the right shoulder, 7 arms open, releasing, 8 picks up the briefcase, stance. |
| 7 | `d_agarrao_perna` | 10840/10841 Puxa a Perna desperto | low leg grab of an unseen crouching opponent in the suit, only him drawn: 1 crouch with the briefcase, 2 lunges low, the free hand forward at ankle height, 3 grabs an invisible ankle, 4 pulls back hard, 5 yanks upward, 6 steps back still pulling, 7 lets go, 8 back to the crouch. |
| 7 | `d_agarrao_cutucao` | 10830/10831 Cutucão Sacana desperto | headlock and rib tickle of an unseen opponent in the suit, only him drawn: 1 steps in, 2 front arm wraps around an invisible neck, 3 locks the headlock, grinning, 4 the ringed hand pokes forward at rib height with two fingers, 5 pokes lower, 6 pokes higher, laughing, 7 releases with a push, 8 stance wagging the ringed index finger. |
| 7 | `d_chute_baixo` | 10230 a em pé desperto | low dress-shoe kick to the shin with the front leg: 1 stance, 2 knee lifts, 3 snaps out, 4 contact at shin height with the shoe 15% larger, 5 hold, 6-8 back to stance. |
| 7 | `d_chute_lateral` | 10260/10720 afastar em pé e na defesa desperto (y + b) | side kick at chest height in the suit, hat held with the front hand: 1 stance, 2 rear foot slides in, 3 knee chambers, hips sideways, 4 drives out, 5 contact with the shoe sole 15% larger, 6 hold, 7 recoils, 8 stance. |
| 7 | `d_baixo_soco` | 10400 ↓ + x desperto | crouching jab with the ringed hand: 1 crouch with the briefcase, 2-3 shoulder loads, 4-5 contact, fist 15% larger, 6-8 back to the crouch. |
| 7 | `d_rasteira_arco` | 10440 ↓ + b desperto | crouching sweep with the briefcase planted on the floor as support: 1 crouch, 2 leans on the briefcase, 3 pivots low, 4 rear leg sweeps in an arc, 5 contact at ankle height with the shoe 15% larger, 6 hold, 7-8 back to the crouch. |
| 7 | `d_ar_soco` | 10600 x no ar desperto | mid-air downward hammer fist with the ringed front hand, briefcase in the rear hand: 1 tucked, 2 fist above the head, 3-4 swings down, 5 contact angled down 45 degrees, fist 15% larger, 6 hold, 7-8 tuck. |
| 7 | `d_ar_cotovelo` | 10601 y no ar desperto | mid-air briefcase drop: 1 tucked, 2 briefcase raised high, 3-4 swings down, 5 contact angled down 60 degrees with the briefcase 15% larger, 6 hold, 7-8 tuck. |
| 7 | `d_ar_joelho` | 10610 a no ar desperto | mid-air knee in the suit, hat held: 1 tucked, 2 knee pulls up, 3-4 drives forward, 5 contact with the knee 15% larger at chest height, 6 hold, 7-8 tuck. |
| 7 | `d_cotovelo_faixa` | 10216 → + y desperto | stepping horizontal elbow in the suit, jacket flaring: 1 stance, 2 big step, 3 hips turn, 4 drives the elbow, 5 contact with the elbow 15% larger at chest height, 6 hold, 7-8 stance. |
| 7 | `d_coice` | 10231 ← + a desperto | backward heel kick without turning, hat held with one hand: 1 stance, 2 leans forward, 3 rear leg extends straight back, 4 contact behind with the heel 15% larger at stomach height, 5 hold, 6 recoils, 7-8 stance facing right. |

## Contagem

| Lote | Folhas | Já existem ok | Retoque | Refazer | Novas |
|---|---|---|---|---|---|
| 1 | 27 | 8 | 2 (`defesa`, `levanta`) | 2 (`queda`, `ar_soco`) | 15 |
| 2 | 16 | 1 (`chute`) | 0 | 0 | 15 |
| 3 | 16 | 0 | 1 (`rasteira`) | 1 (`ascensao`) | 14 |
| 4 | 8 | 0 | 0 | 0 | 8 |
| 5 | 13 | 0 | 0 | 0 | 13 |
| 6 | 27 | 0 | 0 | 0 | 27 |
| 7 | 13 | 0 | 0 | 0 | 13 |
| **total** | **120** | **9** | **3** | **3** | **105** |

São **108 imagens para gerar** (105 novas + 3 refeitas) e 3 retoques de pulseira à mão. As folhas antigas `punho_concreto`,
`agarrao`, `giro_garagem` (versão antiga), `despertar` e as `d_` de gi da tabela antiga de `hazaki.md` **não** devem ser
geradas: o kit mudou.

## Revisão

Revisão de 2026-11-11 (três revisores, cada apontamento conferido contra a ficha, as regras e o código; detalhe técnico
na seção Revisão de [`hazak_gerador.md`](hazak_gerador.md#revisão)).

**Corrigido:**

- Folhas novas: `vira` (lote 1) e `d_vira` (lote 5), para os 4-6 desenhos de virar da 7.1. Do lote 7 entram
  `d_recuo`, `d_agarrao_abraco`, `d_agarrao_perna` e `d_agarrao_cutucao`, porque desperto ele voltava a aparecer de
  gi nessas ações.
- Corrente desperta com uma folha por golpe: `d_maletadas` vira `d_maletada_lado`, `d_maletada_volta` e
  `d_maletada_cima`, e `d_chutes_sapato` vira `d_sapato_canela` e `d_sapato_barriga`. Com 3 golpes fortes numa folha
  de 8 quadros não sobravam preparo, contato e recuperação (B.6, 7.1).
- `d_soco_reto` saiu: o y em pé desperto abre a corrente de maletadas e não toca o 10210. `d_chute_lateral` ficou para
  o afastar desperto (10260/10720), e não para o 10240, que pelo mesmo motivo nunca tocava.
- Tesoura de Bairro: agora é uma volta e meia (540°) no chão. Antes era uma volta só, e no ar, o que o pipeline cola
  no chão.
- Faixa no Asfalto: o `sobe_chutando` chuta sempre com a mesma perna.
- Rolada e `d_fumaca`: todo quadro virado para a direita. Depois do `Turn`, um desenho virado para a esquerda fica de
  costas para o oponente.
- `d_chuva_abre`: ele fecha a maleta e segura em vez de jogar fora, porque logo depois usa a maleta.
- `d_anda` e `d_corrida` com passada ~80% da base.
- Sapato `d_` marrom, para bater com o índice 12 da paleta.
- `derrota_sirene` liga ao 171 (nocaute) e ao 170 (tempo).
- Números de `SPRITES_VITIMA` corrigidos: são avulsos, não faixas inteiras.
- Conteúdo:
  - a estatueta (figura lisa de pé sobre base, silhueta de troféu real) virou figura atarracada em base de karatê
    sobre pedra;
  - a patroa trocou roupa de casa, chinelo e toalha por camiseta, jeans e tênis;
  - o Chapéu Bumerangue sai rasante por baixo e cai na cabeça dele, para não ler como o chapéu de MK.

**Recusado:** nada.

**Dúvidas para o Breno:**

1. As correntes x/a, o Faixa no Asfalto e os kombos da base saem no Despertar? Se ficarem, entram ~9 folhas `d_` no
   lote 7.
2. Para cumprir os 10-20 desenhos da 7.1 em `apanha` e `queda`, gerar uma segunda folha (mais 4 imagens com as `d_`)?
3. A Tesoura no chão e o chapéu que cai na cabeça mudam a leitura da ficha: está bom assim?
