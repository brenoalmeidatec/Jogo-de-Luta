# Fila das folhas boss (forma despertada dos quatro lutadores)

> Montada em 2026-11-11, na branch `bosses`. **Nenhuma imagem desta fila foi gerada**, nada foi cortado, quantizado nem
> testado no motor. Só os quatro conceitos existem em disco. Esta fila não troca a [`fila.md`](fila.md) (forma normal)
> nem a `fila_hazak.md` da branch `hazak`; ela cobre só a forma despertada.

## Regra do dono (2026-11-11)

O Breno aprovou os conceitos de **boss final** da forma despertada de cada lutador. **Cada boss tem, só dele, a aura,
os efeitos, os especiais e o estilo de ataque.** Nada disso se repete entre lutadores. No mesmo dia ele confirmou:
"gostei de todos, mas deixe o cabelo do Raiclaven verde". O conceito do Raiclaven em disco já está de cabelo verde, e o
MODEL LOCK dele trava isso em toda folha.

Vale junto a [seção 4 das regras](../regras-dos-lutadores.md#4-despertar-a-transformação): aura e efeito são **folhas à
parte em fundo verde `#00FF00`**, ligadas por `Explod`, nunca desenhadas nas folhas de corpo. O corpo vai em fundo
magenta `#FF00FF`.

## As cinco auras

| Lutador | Cor | Forma | Folhas |
|---|---|---|---|
| Pengaró | violeta-preto | coluna de fumaça das sombras com anel de sombra no chão | fora desta fila (branch do Endiabrado) |
| Gutto | vermelho-carmesim, miolo branco | garanhão gigante de raio, empinado atrás dele, e crateras de casco em brasa no chão | `fx_aura_garanhao`, `fx_aura_crateras` |
| Raiclaven | aço prata com raio branco-prata, **sem lilás** | leque radial de tesouras, navalhas e pentes de aço atrás dele, e lascas de aço cravadas no chão | `fx_aura_leque`, `fx_aura_lascas` |
| Hazak | laranja-ouro | par de asas de diabo feitas de notas em chamas, coroa de ouro derretido sobre a cabeça e faixa de brasa no chão | `fx_aura_asas`, `fx_aura_coroa`, `fx_aura_brasa` |
| CK | cinza-esverdeado | paredão de som feito de fumaça, soltando anéis de fumaça | `fx_aura_paredao`, `fx_aura_aneis` |

A linha do Pengaró vem do conceito dele, aprovado no mesmo dia; não conferi a folha dele nesta rodada.

## Contagem

| Lutador | Grupo 1 | Grupo 2 | Total |
|---|---|---|---|
| Hazak | 12 | 43 | 55 |
| Gutto | 12 | 24 | 36 |
| Raiclaven | 12 | 20 | 32 |
| CK | 12 | 19 | 31 |
| **Total** | 48 | 106 | **154** |

## Como usar

1. **Um chat por boss**, com o título indicado em cada seção. Uma folha por mensagem.
2. **Anexos em toda folha de corpo:** o conceito do lutador e a folha da coluna "Base de referência" (ela dá a escala e
   os tempos). Depois que a ginga do boss (`e_ginga`, `d_parado`, `b_ginga`) for aprovada, ela entra como terceiro
   anexo e passa a mandar no modelo. Nunca anexe imagem de jogo comercial.
3. **Prompt de corpo:** o bloco "Prompt base do boss" do lutador, trocando só a linha `MOTION`.
4. **Prompt de efeito** (`fx_*`): o bloco abaixo, com o conceito anexado, trocando só a linha `MOTION`. Efeito verde
   (tubo e choque do Raiclaven, cacos do CK) vai em **fundo magenta**, como já é o `fx_garrafa` do CK; a coluna da base
   avisa.
5. Salve exatamente em `sprites/<lutador>/quadros/folhas_arcade/<folha>.png`. Nada fica em Downloads.
6. **Ordem:** o Grupo 1 dos quatro primeiro (são as 12 folhas que mais aparecem na tela), depois o Grupo 2. Dentro do
   grupo, a ordem da tabela.
7. Aceite de cada folha: o da [bíblia de arte](../biblia-de-arte.md#estilo-arcade-anos-90) mais o MODEL LOCK do
   lutador, conferido quadro a quadro. Reprovou: gere de novo no mesmo chat.
8. Limites de conteúdo, valem para todas: estilo de luta 2D de fliperama dos anos 90; nada copiado de jogo comercial
   (personagem, pose-assinatura, nome); nenhuma pessoa real; nada sexual; sem logo, marca ou texto; garrafa sem rótulo.
   Hazak: sem o estereótipo da mulher loira e sem piada de escravidão.

### Prompt base dos efeitos (aura e especiais, fundo verde)

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
A visual effect for a 1990s arcade fighting game, hand-pixeled, hard-edged flat shading in 2-3 tones, no gradients, no
dithering, 1-pixel colored outline. The attached concept image shows the look of this effect in its THIRD figure (the
one with the aura): copy the colours and the shapes of the effect, and do NOT draw the character.
One single row of 8 frames in 8 equal-width cells, wide image, the effect the same size in every cell. Flat solid pure
green background (#00FF00) everywhere. No character, no body parts, no text, no numbers, no borders, no ground.
MOTION: <linha da folha>
Consecutive frames differ by a small amount, so the loop looks smooth.
```

Para efeito verde, troque "pure green background (#00FF00)" por "magenta background (#FF00FF)".

## Hazak, o Diabo Loiro chefão (`hazaki`, prefixo `d_`)

Chat: **Hazak — boss**. Pasta: `sprites/hazaki/quadros/folhas_arcade/`. Conceito aprovado: `sprites/hazaki/quadros/folhas_arcade/d_conceito.png`.

Estilo de ataque (ficha, "Despertar: Diabo Loiro"): **alcance e peso, sem a pressa do rapidinho**. A maleta bate como
porrete, o sapato social empurra, o chapéu vira arma e o dinheiro vira golpe (notas fictícias). Prefixo `d_`. A lista e
os números de estado são os da `docs/arcade/fila_hazak.md` da branch `hazak` (lotes 5, 6 e 7), e as linhas de MOTION
vêm de lá, com três ajustes para o conceito de boss: o sobretudo nos ombros como capa, o rabo, e os chifres que furam o
chapelão. As folhas da coluna "Base de referência" estão na branch `hazak` (`sprites/hazaki/quadros/folhas_arcade/`);
na `bosses` só existem 15 delas. A base das correntes novas é a folha do golpe que ocupa o mesmo lugar na forma normal,
escolhida por mim só para dar a escala. Os objetos `obj_chapeu`, `obj_maco` e `obj_papel` continuam na fila do Hazak.

### Prompt base do boss (corpo, fundo magenta)

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached concept image shows the exact character to keep (the LEFTMOST figure, the one without aura): HAZAK in his
final-boss awakened form, the Blond Devil, boss of the bosses. The same young clean-shaven man (no beard, no goatee, no
moustache), the same body size and proportions; a long wild blond mane swept straight back over the head and down the
back (never spiked upward), glowing red eyes, a confident grin. Two curved dark horns with ember-orange tips grow from
his head and pass THROUGH two holes in the crown of a big wide-brimmed dark hat with an ember-orange band. A dark
navy-purple double-breasted pinstripe suit with gold buttons and a gold watch chain, wide pinstripe trousers, white
shirt, ember-orange tie. A long dark overcoat with an ember-orange lining rests on his shoulders like a cape, sleeves
empty and hanging. A chunky gold ring on the front hand. Dark brown leather dress shoes with white spats. A thin dark
devil tail with a spade tip hangs below the coat. The same teal wristband over the shirt cuff of the REAR wrist only. He
carries a dark brown leather briefcase with gold clasps in the REAR hand unless the motion says otherwise.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs, one tail. Exactly two horns; the horns
belong to his head, not to the hat: when a motion takes the hat off, the horns stay on the head and the hat shows two
holes in the crown. The overcoat always stays on the shoulders as a cape, his arms never go into its sleeves. The teal
wristband is ONLY on the rear wrist, never on the front one, never missing. Exactly ONE briefcase, in the rear hand
unless the motion says otherwise. Hair blond, never dark. No wings, no crown, no fire, no embers, no smoke, no flying
banknotes, no aura: all of those are separate effect sheets. No logos, no flags, no real brand, no real money printed
anywhere. The body has the same size and proportions as the leftmost figure of the concept in every frame.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture. 1-pixel colored outline, never pure black, lighter or missing on the lit side. Small hard 1-3 pixel
specular highlights. Limited palette look.
Shadows shift hue: tan skin goes toward wine red in shadow and warm cream in light; the navy-purple suit and coat get
cool blue light and deep violet shadow, the pinstripes are thin and regular; the ember-orange lining, tie and hat band
are the only hot colour on the body; the blond hair is three flat tones from pale cream to orange-gold; gold gets a hard
orange shadow and a white glint. Outline dark wine on skin, dark blue-purple on clothes. The overcoat cape, the tie and
the devil tail lag one frame behind the body in every motion.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, feet on the same ground
line, every limb fully inside its own frame. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects (no fire, no sparks, no dust, no smoke, no speed lines, no motion trails).
On every attack, the striking limb or weapon on the contact frame is drawn 15% larger.
MOTION: <linha da folha>
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### Grupo 1: as 12 que mais aparecem (12 folhas)

| # | Folha | Base de referência | MOTION |
|---|---|---|---|
| 1 | `d_parado` | `parado` · 10000 parado desperto (referência de todas as `d_`) | standing guard with the briefcase held low in the rear hand, front fist up wearing the gold ring, hat brim low, weight on the back leg, slow confident breathing bounce: 1-4 sink slightly, 5-8 rise; overcoat cape and devil tail sway one frame behind the hips; 8 loops into 1; feet never slide. |
| 2 | `d_anda` | `anda` · 10020 andar desperto | slow swaggering forward walk, stride about 80% as long as the base walk, briefcase swinging in the rear hand, front fist up, two-step cycle: 1 front foot contact, 2 down, 3 passing, 4 up, 5-8 the same with the other leg; overcoat cape and devil tail and tie swing; 8 loops into 1. |
| 3 | `d_tapa_anel` | `soco` · 3431 x em pé desperto (tapa com anel), abertura da Sociedade Fechada | open backhand slap with the ringed front hand: 1 guard, 2 front hand rises across the chest, 3 whips out, 4 contact at face height with the back of the hand 15% larger, gold ring forward, 5 hold, 6-8 back to guard. |
| 4 | `d_sapato_canela` | `chute_baixo` · 3420 corrente b desperta, 1º (sapato na canela) | heavy dress-shoe kick to the shin with the front leg: 1 stance, 2 weight shifts back, 3 front knee lifts, 4 the shin snaps out low, 5 contact at shin height with the shoe 15% larger, standing leg bent, 6 hold, 7 knee recoils, 8 stance. |
| 5 | `d_apanha` | `apanha` · 15000-15030 tomar golpe desperto | hit reaction: 1 stance, 2 head snaps back, the hat tilts, 3-4 staggers back, briefcase swinging, 5-6 leans and starts falling backward, 7-8 airborne falling flat, holding the hat. |
| 6 | `d_queda` | `queda` · 15050-15100 cair desperto | 1 airborne falling flat, 2 back hits the floor, 3 bounces, the hat pops up a little, 4-8 lies still, hat back on the chest, briefcase beside him; same body length as the attached sheet lying down. |
| 7 | `d_levanta` | `levanta` · 15120 levantar desperto | 1 lying flat, 2 rolls to the side, 3 hand pushes on the floor, 4 knee under, 5 kneeling, puts the hat back on, 6 rising, grabbing the briefcase, 7 straightens the tie, 8 stance. The horns never leave the head; the hat goes back on over them. |
| 8 | `d_defesa` | `defesa` · 10120-10132 guarda em pé desperto | blocks with the briefcase: 1 stance, 2-3 raises the briefcase flat in front of the face and chest with both hands, 4-5 holds the block with a small push back on impact, 6-8 back to stance. |
| 9 | `d_agachado` | `agachado` · 10010-10012 agachar desperto | 1 standing guard with the briefcase, 2-4 lowers into a crouch holding the briefcase in front of the shins like a shield, 5-8 holds the crouch with a small breathing bounce; 8 loops into 5. |
| 10 | `d_pulo` | `pulo` · 10040-10047 pulo desperto | jump holding the hat with the front hand and the briefcase in the rear: 1 crouch load, 2 push-off, 3-4 rising with knees tucking, 5 apex tucked, 6-7 falling with legs opening, 8 landing reach; overcoat cape and devil tail trail the motion. |
| 11 | `d_maleta_giro` | `giro_garagem` · 3402/3403 Maleta Giratória (avanço, várias batidas) | advancing spin swinging the briefcase at arm's length, grounded: 1 stance, 2 steps forward, briefcase out wide, 3 spins showing the back, 4 briefcase comes around at chest height, contact briefcase 15% larger, 5 spins again, 6 second contact, briefcase 15% larger, 7 slows, 8 stance facing right. OWN SPECIAL (Maleta Giratória). |
| 12 | `fx_aura_asas` | terceira figura do conceito | AURA, main layer, drawn behind the fighter: a pair of big devil bat wings spread wide, each about as tall as a man and twice as wide, built from burning banknotes layered like feathers over thin gold bones with a claw at the top joint; 1-4 the wings rise and spread, the paper edges curl and glow, drops of molten gold fall from the lower tips, 5-8 the wings lower a little and loose burning notes peel off and drift down; 8 loops into 1. Orange-gold with a white-hot core, dark ember edges; the notes are blank paper, no numbers, no faces, no symbols. The centre of each cell, where the fighter stands, is left empty. |

### Grupo 2: o resto do kit, a transformação e os efeitos (43 folhas)

| # | Folha | Base de referência | MOTION |
|---|---|---|---|
| 1 | `despertar_virada` | `despertar_pedido (e parado)` · 2000, transformação (gi vira terno) | the karate fighter turns into the blond devil in a mafia suit: 1 bent forward in the gi, fists clenched, 2 hair starts growing longer and lighter, 3 hair turns blond and sweeps back, two horns push out of the forehead, 4 eyes glow red, the gi darkens, 5 the gi turns into the pinstripe suit from the shoulders down, 6 the hat drops onto the head and the two horns pierce its crown, the overcoat settles on the shoulders as a cape, 7 straightens up, the devil tail uncurls, the briefcase appears in the rear hand, 8 final pose of the suited form, full body, exactly like the leftmost figure of the attached concept. Same body size in every frame. |
| 2 | `d_vira` | `vira` · 10005/10006 virar desperto | turning around in place in the suit, briefcase in the rear hand, the same body size in every frame: 1 guard facing right, 2 turning toward the viewer, 3 almost facing the viewer, 4 guard facing left; 5 crouching guard facing right, 6 turning low, 7 almost facing the viewer, 8 crouching guard facing left. |
| 3 | `d_corrida` | `corrida` · 10100 correr desperto, arranque do Pega Bolado desperto | heavy running, stride about 80% as long as the base run, one hand holding the hat on the head, briefcase pumping in the rear hand, torso leaning forward: 1 push-off, 2 airborne stride, 3 landing, 4 passing, 5-8 the same with the other leg; tie flies back over the shoulder; 8 loops into 1. |
| 4 | `d_defesa_baixa` | `defesa_baixa` · 10131/10141/10152 guarda agachada desperta | crouching block with the briefcase held vertical in front of the knees: 1 crouch, 2-3 briefcase comes down, 4-5 holds with a small slide back, 6-8 back to the crouch. |
| 5 | `d_vitoria` | `vitoria` · 10181 vitória desperto | 1 relaxed stance, 2 straightens the tie, 3 tips the hat brim with two fingers, 4 opens the briefcase toward the viewer, 5 snaps it shut, 6 points the ringed index finger forward, 7 wags the finger, 8 hat tipped low, grinning; 8 holds. |
| 6 | `d_maletada_lado` | `soco_reto` · 3410 corrente y desperta, 1º (maletada de lado); 349 Sociedade Fechada; 3100 | forehand briefcase swing: 1 guard, briefcase low in the rear hand, 2 briefcase pulled back behind the hip, 3 hips turn, the arm starts around, 4 briefcase swings in flat, 5 contact at head height with the briefcase 15% larger, arm extended, 6 hold, 7 follow-through across the body, 8 back to guard. |
| 7 | `d_maletada_volta` | `cruzado` · 3411 corrente y desperta, 2º (maletada de volta); 3100 | backhand briefcase swing coming back: 1 briefcase across the body after a swing, 2 shoulders coil the other way, 3 elbow leads back, 4 briefcase swings back flat, 5 contact at head height with the briefcase 15% larger, back of the hand forward, 6 hold, 7 the briefcase drifts down, 8 back to guard. |
| 8 | `d_maletada_cima` | `cotovelada` · 3412 corrente y desperta, 3º (maletada de cima); 3100 | overhead briefcase chop: 1 guard, 2 grabs the briefcase with both hands, 3 raises it high over the head, up on the toes, 4 starts down, body weight dropping, 5 contact at head height with the briefcase 15% larger, knees bent, 6 hold, 7 briefcase at knee height, 8 back to guard. |
| 9 | `d_negocio_fechado` | `calcada_levantada` · 3413 corrente y desperta, finalizador (Negócio Fechado, derruba) | 1 guard, 2 holds the briefcase in front with both hands, 3 snaps it open toward the opponent at face height, 4 leans in, 5 slams it shut forward, contact with the briefcase 15% larger at head height, 6 shoves forward, 7 hold, 8 tucks the briefcase under the arm, stance. |
| 10 | `d_sapato_barriga` | `chute` · 3421 corrente b desperta, 2º (sapato na barriga) | heavy push kick to the stomach with the front leg: 1 stance, 2 front knee chambers high, 3 hips lean back, 4 the leg drives straight out, 5 contact at stomach height with the shoe sole 15% larger, 6 hold, 7 knee recoils, 8 stance. |
| 11 | `d_coice_costas` | `chute_giratorio` · 3422 corrente b desperta, 3º (coice de costas) | turns and mule-kicks: 1 guard, 2 turns showing the back of the jacket, 3 bends forward, hat held with one hand, 4 rear leg shoots straight back toward the opponent, 5 contact with the shoe sole 15% larger at stomach height, 6 hold, 7 turns back, 8 guard facing right. |
| 12 | `d_pisao_chefe` | `machado` · 3423 corrente b desperta, finalizador (Pisão de Chefe, derruba) | 1 guard, 2 front knee rises high, 3 holds the knee up looking down, 4 stomps down forward, 5 contact with the shoe sole 15% larger at knee height driving down to the floor, 6 weight on the stomping leg, 7 straightens the tie with both hands, 8 stance. |
| 13 | `d_maleta_sobe` | `joelhada_baixo` · 3430 ↓ + y desperto (maleta subindo, antiaéreo) | from a crouch, swings the briefcase straight up: 1 crouch, briefcase low, 2 coils, 3 rises onto the toes, 4 briefcase swings up in front of the face, 5 contact above the head with the briefcase 15% larger, arm straight up holding the handle, 6 hold, 7-8 back to the crouch. Feet stay on the ground. |
| 14 | `d_chapelada` | `machado_curto` · 3432 → + b desperto (chapelada por cima), 348 Sociedade Fechada | overhead hat strike: 1 stance, 2 takes off the hat with the front hand, 3 raises it high, up on the toes, 4 swings it down, 5 contact at head height with the hat brim 15% larger, 6 hold, 7 puts the hat back on, 8 stance. The two horns stay on his head while the hat is off; the hat shows two holes in the crown. |
| 15 | `d_dedo` | `cutucao_recuo` · 3433 ← + x desperto (dedo balançando, anula projétil fraco); provocação c desperta | 1 stance, 2 front arm extends forward, ringed index finger up, 3 wags left, 4 wags right, 5 wags left, 6 wags right, 7 lowers the hand smirking, 8 stance. |
| 16 | `d_pisao_ar` | `ar_chute_duplo` · 3435 b no ar desperto (pisão de sapato descendo) | mid-air dropping stomp: 1 tucked jump pose holding the hat, 2 front knee pulls up, 3 leg drives down, 4 sole pointing down-forward at 60 degrees, 5 contact with the shoe sole 15% larger, 6 hold, 7-8 tuck. |
| 17 | `d_bico_sapato` | `chute_canela` · 3434 ↓ + a desperto (chute de bico de sapato) | crouching toe kick: 1 crouch, 2 front foot lifts, 3 snaps out low, 4 contact at ankle height with the shoe tip 15% larger, 5 hold, 6-8 back to the crouch. |
| 18 | `d_chapeu_arremesso` | `estatueta_arremesso` · 3400/3401 Chapéu Bumerangue | low sidearm hat throw at waist height: 1 stance, 2 takes off the hat and lowers it to the hip, 3 crouches slightly, the arm swings back low beside the body, 4 swings forward low and flat, 5 releases at waist height, hand open forward 15% larger, hat gone (not drawn), 6 waits, hand on the hip, 7 looks up, bare head, 8 the hat lands back on his head by itself (hat drawn on the head), stance. Never thrown from the head with a flick, no blade on the brim. The two horns stay on his head while the hat is away; in frame 8 the hat drops back over the horns. |
| 19 | `d_nota_falsa` | `agachado` · 3404/3405 Nota Falsa (armadilha) | crouches and leaves a bundle of cash on the floor: 1 stance, 2 takes a bundle out of the inner jacket pocket, 3 crouches, 4 sets the bundle on the floor in front of him, 5 pats it, 6 rises, hand empty, 7 winks, 8 stance. The bundle is plain paper with a paper band, no printed money. |
| 20 | `d_suborno` | `agarrao_cutucao` · 3406/3407 Suborno (agarrão de comando: oferece o maço e bate) | 1 stance, 2 holds a cash bundle forward at chest height with the front hand, friendly grin, 3 holds still as if someone takes it, 4 the empty hand pulls back, 5 the briefcase swings up from below with the rear hand, 6 contact at chin height with the briefcase 15% larger, 7 follow-through, 8 stance. |
| 21 | `d_estatueta` | `estatueta_arremesso` · 11600/11601 Estatueta Dourada desperta (maior, vira obstáculo) | two-handed heavy lob throw: 1 stance, holding a big stocky golden figure in a wide karate stance with both fists up, on a rough round rock base, against the chest with both hands, 2 squats down, 3 heaves it up over the head, 4 leans back, 5 throws it forward and up at 45 degrees, both hands open 15% larger, 6 follow-through, 7-8 back to stance. Figurine drawn only in frames 1-4. |
| 22 | `d_voadora_sapato` | `voadora` · 11500/11501 Pega Bolado desperto (voadora de sapato, quica) | running two-footed dropkick in the suit: 1 last stride holding the hat, 2 jumps forward, knees tucked, 3 airborne leaning back, 4 both shoes shoot forward, 5 contact with both soles 15% larger at chest height, 6 hold, 7 lands on the back, 8 rolls up to a crouch fixing the hat. |
| 23 | `d_punho_anel` | `punho_chao` · 11000/11001 Punho de Concreto desperto (soco com anel, lasca em brasa) | lunging low punch with the ringed hand scraping the floor: 1 stance, 2 long step in, front fist drawn back, ring shining, 3 drops low, 4 drives the fist forward and down, 5 contact with the ringed knuckles 15% larger at the ground line one step ahead, 6 hold low, 7-8 rises to stance. |
| 24 | `d_fumaca` | `rolada_tatame` · 11700/11701 Rolada de Tatame desperta (some e reaparece atrás) | vanishing and reappearing, the body shrinks into a crouch and pops back: 1 stance, 2 crouches holding the hat, 3 crouched smaller, 4 curled tight, smallest, 5 still curled tight, 6 opening up, 7 rising, 8 guard stance; every frame faces right (the game turns him around). No smoke drawn. |
| 25 | `d_chuva_abre` | `pose_super` · 3100 Chuva de Dinheiro, abertura e superpausa | 1 stance, 2 lifts the briefcase in front with both hands, 3 grins, 4 snaps it open toward the sky, 5 holds it open overhead, 6 shakes it, 7 snaps the briefcase shut and grips it by the handle, ready to swing, 8 drops into a low stance, briefcase in the rear hand. No money drawn. |
| 26 | `d_estatueta_gigante` | `estatueta_arremesso` · 3100 Chuva de Dinheiro, fecho (Estatueta Dourada gigante) | 1 stance, 2 reaches up, 3 holds a huge stocky golden figure in a wide karate stance with both fists up, on a rough round rock base, taller than himself, over the head with both hands, knees bent, 4 leans back, 5 slams it forward and down, contact at head height with the figurine 15% larger, 6 it hits the ground line, 7 lets go, 8 dusts off the hands, stance. |
| 27 | `d_recuo` | `recuo` · 10105 passo para trás desperto | quick backward hop in the suit, one hand holding the hat, briefcase in the rear hand: 1 stance, 2 knees bend, 3 pushes off the front foot, 4-5 low hop backward, overcoat cape and devil tail and tie swing forward, 6 rear foot lands first, 7 front foot lands, 8 stance. |
| 28 | `d_agarrao_abraco` | `agarrao_abraco` · 10800/10810 Abraço de Quebrada desperto | bear hug and over-the-shoulder throw of an unseen opponent in the suit, briefcase dropped at his feet in frame 1 and picked up in frame 8, only him drawn: 1 reaches forward with both arms open, 2 wraps both arms around an invisible torso at chest height, 3 squeezes, leaning back, 4 lifts, knees bent, 5 turns the hips under, 6 heaves over the right shoulder, 7 arms open, releasing, 8 picks up the briefcase, stance. |
| 29 | `d_agarrao_perna` | `agarrao_perna` · 10840/10841 Puxa a Perna desperto | low leg grab of an unseen crouching opponent in the suit, only him drawn: 1 crouch with the briefcase, 2 lunges low, the free hand forward at ankle height, 3 grabs an invisible ankle, 4 pulls back hard, 5 yanks upward, 6 steps back still pulling, 7 lets go, 8 back to the crouch. |
| 30 | `d_agarrao_cutucao` | `agarrao_cutucao` · 10830/10831 Cutucão Sacana desperto | headlock and rib tickle of an unseen opponent in the suit, only him drawn: 1 steps in, 2 front arm wraps around an invisible neck, 3 locks the headlock, grinning, 4 the ringed hand pokes forward at rib height with two fingers, 5 pokes lower, 6 pokes higher, laughing, 7 releases with a push, 8 stance wagging the ringed index finger. |
| 31 | `d_chute_baixo` | `chute_baixo` · 10230 a em pé desperto | low dress-shoe kick to the shin with the front leg: 1 stance, 2 knee lifts, 3 snaps out, 4 contact at shin height with the shoe 15% larger, 5 hold, 6-8 back to stance. |
| 32 | `d_chute_lateral` | `chute_lateral` · 10260/10720 afastar em pé e na defesa desperto (y + b) | side kick at chest height in the suit, hat held with the front hand: 1 stance, 2 rear foot slides in, 3 knee chambers, hips sideways, 4 drives out, 5 contact with the shoe sole 15% larger, 6 hold, 7 recoils, 8 stance. |
| 33 | `d_baixo_soco` | `baixo_soco` · 10400 ↓ + x desperto | crouching jab with the ringed hand: 1 crouch with the briefcase, 2-3 shoulder loads, 4-5 contact, fist 15% larger, 6-8 back to the crouch. |
| 34 | `d_rasteira_arco` | `rasteira_arco` · 10440 ↓ + b desperto | crouching sweep with the briefcase planted on the floor as support: 1 crouch, 2 leans on the briefcase, 3 pivots low, 4 rear leg sweeps in an arc, 5 contact at ankle height with the shoe 15% larger, 6 hold, 7-8 back to the crouch. |
| 35 | `d_ar_soco` | `ar_soco` · 10600 x no ar desperto | mid-air downward hammer fist with the ringed front hand, briefcase in the rear hand: 1 tucked, 2 fist above the head, 3-4 swings down, 5 contact angled down 45 degrees, fist 15% larger, 6 hold, 7-8 tuck. |
| 36 | `d_ar_cotovelo` | `ar_cotovelo` · 10601 y no ar desperto | mid-air briefcase drop: 1 tucked, 2 briefcase raised high, 3-4 swings down, 5 contact angled down 60 degrees with the briefcase 15% larger, 6 hold, 7-8 tuck. |
| 37 | `d_ar_joelho` | `ar_joelho` · 10610 a no ar desperto | mid-air knee in the suit, hat held: 1 tucked, 2 knee pulls up, 3-4 drives forward, 5 contact with the knee 15% larger at chest height, 6 hold, 7-8 tuck. |
| 38 | `d_cotovelo_faixa` | `cotovelo_faixa` · 10216 → + y desperto | stepping horizontal elbow in the suit, jacket flaring: 1 stance, 2 big step, 3 hips turn, 4 drives the elbow, 5 contact with the elbow 15% larger at chest height, 6 hold, 7-8 stance. |
| 39 | `d_coice` | `coice` · 10231 ← + a desperto | backward heel kick without turning, hat held with one hand: 1 stance, 2 leans forward, 3 rear leg extends straight back, 4 contact behind with the heel 15% larger at stomach height, 5 hold, 6 recoils, 7-8 stance facing right. |
| 40 | `fx_aura_coroa` | terceira figura do conceito | AURA, top layer, floating above the fighter's head: a small crown of molten gold with five points; 1-4 it bobs up slowly and one thick drop of molten gold stretches from its rim, 5-8 it bobs down and the drop falls and vanishes; 8 loops into 1. About as wide as a hat, drawn in the upper centre of each cell. |
| 41 | `fx_aura_brasa` | terceira figura do conceito | AURA, ground layer: a low wide strip of embers and short flames on a flat ground line, about three body widths wide; 1-8 the flames flicker left to right, small sparks jump up and die, scraps of burning paper glow in the strip; 8 loops into 1. Nothing taller than a man's knee. |
| 42 | `fx_notas` | nenhuma (o `obj_papel` da fila do Hazak serve de forma) | OWN SUPER effect, Money Rain: a curtain of blank banknotes with burning edges falling across the whole cell; 1-8 the notes tumble down at different speeds, some flat, some edge-on, a few catching fire; frame 8 flows into frame 1 so the rain can loop. Blank paper with a plain band, no numbers, no faces, no symbols. |
| 43 | `fx_fumaca_brasa` | nenhuma | OWN SPECIAL effect, the ember smoke of the vanish: 1 a small burst of orange sparks at ground level, 2-4 a column of dark smoke with glowing orange embers swells to the height of a man, 5-6 it holds, hollow in the middle, 7-8 it thins and the last embers drift up. |

### Dúvidas que a ficha deixa em aberto

- **Chapéu furado pelos chifres contra golpes de chapéu:** a ficha tem a chapelada por cima e o Chapéu Bumerangue, e no conceito os chifres atravessam a copa. Escrevi que os chifres ficam na cabeça e o chapéu sai com dois furos. Se o dono preferir que o chapéu nunca saia, esses dois golpes precisam de outra arma.
- **Sobretudo como capa:** em rolamento, queda e voadora ele pode cair. Travei que fica sempre nos ombros; se puder voar longe na queda, a regra muda.
- **Asas e coroa são só aura.** A ficha não tem golpe com asa, voo nem coroa. Se o dono quiser que as asas de notas entrem em algum golpe (por exemplo no Chuva de Dinheiro), falta dizer.
- **Derrota e entrada despertas:** a fila do Hazak não tem `d_derrota` nem `d_intro`; a derrota da ficha (sirene, ele foge) é da forma normal. Não criei folha.
- **Provocação desperta:** usa a `d_dedo`, a mesma do ← + x, como a fila do Hazak já define.
- **Duas filas para as mesmas folhas:** a `fila_hazak.md` da branch `hazak` já tem estas `d_` com o modelo de terno sem capa, sem rabo e sem chapéu furado. Quando as branches se juntarem, o prompt `d_` de lá tem de ser trocado pelo desta fila, senão saem dois modelos.
- **Pulseira teal:** no conceito ela aparece no pulso de trás, sobre o punho da camisa, junto da maleta. Não medi a cor.

## Gutto, o senhor da guerra garanhão (`gutto`, prefixo `e_`)

Chat: **Gutto — boss**. Pasta: `sprites/gutto/quadros/folhas_arcade/`. Conceito aprovado: `sprites/gutto/quadros/folhas_arcade/e_conceito.png`.

Estilo de ataque (ficha, "Como o demônio luta"): **fera, não Muay Thai**. Postura baixa raspando o casco, pancadas de
bracelete com espinho, coices e pisões, empinada, o Carrinho de Satanás, agarrão com mordida, bufada de fogo como
projétil e o galope. O vapor do nariz que aparece no conceito é efeito (`fx_vapor`) e fica fora do corpo. As folhas
`e_` do demônio antigo em `quadros/folhas/` são de outro modelo e de outra arte: servem só de referência de tempo.

### Prompt base do boss (corpo, fundo magenta)

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached concept image shows the exact character to keep (the LEFTMOST figure, the one without aura): GUTTO in
his final-boss awakened form, the stallion warlord. A huge muscular horse-headed demon with a human torso and arms: dark
red-brown skin, long horse muzzle, glowing red eyes, a thick black mustache under the nostrils, two big curved horns
whose tips glow ember red, a long wild black mane streaked with crimson falling down the back, a red braided rope
headband with a short tail behind the head. Iron collar with a short broken chain hanging on the chest, thin glowing red
cracks on the chest. ONE riveted iron pauldron with spikes on the REAR shoulder (the shoulder away from the opponent),
held by a leather strap across the chest. Spiked iron bracers on both forearms, red hand wraps on both fists. Wide white
waistband over a tattered black war skirt with red trim. Iron shin guards, horse hooves with ember-glowing horseshoes, a
black horse tail with crimson strands. No weapon.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs ending in hooves, one tail. Exactly two
horns, always the same size. Exactly ONE pauldron, always on the REAR shoulder, never on both, never on the front one.
The chain on the collar is short and broken, never long, never held in the hand. Both fists wrapped in red, never claws,
never gloves, nothing in the hands. The headband is red rope, never a crown or helmet. The body has the same size and
proportions as the leftmost figure of the concept in every frame. Draw NO steam from the nostrils, NO fire, NO
lightning, NO aura, NO dust, NO cracks on the ground: all of those are separate effect sheets.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture. 1-pixel colored outline, never pure black, lighter or missing on the lit side. Small hard 1-3 pixel
specular highlights. Limited palette look.
Shadows shift hue: the dark red-brown skin goes toward deep wine in shadow and warm orange-cream in light; the iron
gets cool blue-grey shadows and one hard white glint; black hair and skirt are very dark blue-violet with crimson
streaks, never pure black; the white waistband gets cool lilac shadows. Outline dark wine on skin, dark blue-purple on
iron, hair and cloth.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, feet on the same ground
line, every limb fully inside its own frame. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects (no fire, no sparks, no dust, no smoke, no speed lines, no motion trails).
On every attack, the striking limb or weapon on the contact frame is drawn 15% larger.
MOTION: <linha da folha>
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### Grupo 1: as 12 que mais aparecem (12 folhas)

| # | Folha | Base de referência | MOTION |
|---|---|---|---|
| 1 | `e_ginga` | folhas_arcade/ginga | war stance loop: knees bent on the hooves, torso leaning forward, both wrapped fists up at chest height with the spiked bracers forward, head low so the horns point at the opponent; 1-4 he sinks and the front hoof scrapes the ground backward once like a bull, 5-8 he rises and the chest swells; mane, headband tail, skirt and horse tail lag one frame behind the body; 8 loops into 1; the rear hoof never slides. |
| 2 | `e_anda` | folhas_arcade/anda | heavy forward march on the hooves, hunched, shoulders rolling, fists up, two-step cycle: 1 front hoof contact, 2 weight down, 3 passing, 4 up, 5-8 the same with the other leg; mane, skirt and tail sway one frame late; 8 loops into 1. |
| 3 | `e_soco` | folhas_arcade/soco | two blows with the spiked bracers: 1 stance, 2 the front arm cocks back, 3 front backfist fully extended at chest height, the bracer spikes leading, fist 15% larger, 4 it pulls back, 5 the rear shoulder rolls forward, 6 big rear overhand hammer fist fully extended forward at chest height, fist and bracer 15% larger, 7 recovers, 8 stance. |
| 4 | `e_chute_alto` | folhas_arcade/chute_alto | high front hoof kick that hits IN FRONT of him, to the right: 1 stance, 2 weight goes onto the rear hoof, 3 the front knee chambers high, 4-5 standing upright on one hoof, the other leg fully stretched to the right at head height, hoof and glowing horseshoe 15% larger, torso leaning back, 6 the knee folds, 7 the hoof comes down, 8 stance. He never turns his back. |
| 5 | `e_apanha` | folhas_arcade/apanha | hit in the face: 1 stance, 2-3 the horse head snaps back with the mouth open, 4-5 the torso bends backward, mane flying forward, chain swinging, 6-8 he recovers to the stance, snarling. |
| 6 | `e_queda` | folhas_arcade/queda | knocked down: 1 hit and bending back, 2 hooves leave the ground, 3-4 flying backward horizontally, 5-6 falling onto his back, 7 bounces on the floor, 8 lying flat on his back, horns and pauldron clear of the floor line; same body length in every frame. |
| 7 | `e_levanta` | folhas_arcade/levanta | getting up: 1 flat on his back, 2-3 rolls over onto hands and knees, 4-5 pushes up on the hooves, 6-7 rises hunched and shakes the mane, 8 stance. |
| 8 | `e_defesa` | folhas_arcade/defesa | block: 1 stance, 2-3 he hunches behind both crossed forearms, bracers in front of the face, the rear pauldron raised, 4-5 holds the block, snarling, 6-7 the impact slides him back a little, 8 still blocking. |
| 9 | `e_agachado` | folhas_arcade/agachado | 1 stance, 2-4 he sinks into a deep low crouch, one fist on the ground, head low and horns forward, 5-8 he stays crouched breathing with a small bounce; 8 loops into 5. |
| 10 | `e_pulo` | folhas_arcade/pulo | jump: 1 hooves bent ready, 2 push-off, 3 rising with the legs tucking, 4 tucked at the top with the fists up, 5 still tucked, 6 falling with the legs opening, 7 reaching down with the hooves, 8 landing hunched; mane and skirt trail the motion. |
| 11 | `e_compasso` | folhas/e_compasso (arte antiga, so o tempo) | OWN SPECIAL, Stallion Buck (Coice de Garanhão): 1 stance, 2-3 he plants both fists toward the ground, turns his back and looks over the shoulder, 4-5 the hind leg shoots straight backward toward the opponent at chest height, hoof and glowing horseshoe 15% larger, the other hoof planted, 6-7 he spins back around, 8 stance facing right. |
| 12 | `fx_aura_garanhao` | terceira figura do conceito | AURA, main layer, drawn behind the fighter: a giant stallion made only of crimson-red lightning with a white-hot core, rearing on its hind legs, about twice the height of a man, front hooves pawing the air; 1-4 the stallion rears higher and its mane of lightning flares, 5-8 it settles and the bolts flicker along a different path; small lightning horseshoes spark off and fade; 8 loops into 1. The lower centre of each cell, where the fighter stands, is left empty. |

### Grupo 2: o resto do kit, a transformação e os efeitos (24 folhas)

| # | Folha | Base de referência | MOTION |
|---|---|---|---|
| 1 | `e_chute_baixo` | folhas_arcade/chute_baixo | hoof stomp forward: 1 stance, 2 the front hoof lifts, 3 raised at knee height, 4-5 it stamps down and forward low to the ground, hoof 15% larger, 6-7 back, 8 stance. |
| 2 | `e_martelo` | folhas_arcade/martelo | he rears up and drops both fists: 1 stance, 2 both arms rise as he rears up on the hind legs, 3 joined fists high over the head, 4-5 he smashes them down and forward at chest height, fists and bracers 15% larger, 6-7 he straightens, 8 stance. |
| 3 | `e_afastar` | folhas_arcade/afastar | push kick that shoves the opponent away: 1 stance, 2-3 one knee chambers high against the chest, 4-5 that leg thrusts straight forward to the right at chest height, hoof leading and 15% larger, torso leaning back, 6-7 the leg folds and lands, 8 stance. |
| 4 | `e_baixo_soco` | folhas_arcade/baixo_soco | low bracer swipe from the crouch: 1 deep crouch, 2-3 the front arm cocks back, 4-5 the fist and spiked bracer sweep forward along the ground at ankle height, 15% larger, 6-8 back to the crouch. |
| 5 | `e_cabecada` | folhas_arcade/cabecada | rising anti-air from the crouch, knee first and horns up: 1 deep crouch, 2-3 the legs push up, 4-5 the whole body drives upward with one knee leading and fully driven up, head thrown up so the horns point at the sky, 6-8 he lands back in the crouch. |
| 6 | `e_rasteirinha` | folhas_arcade/rasteirinha | quick low hoof kick from the crouch: 1 deep crouch, 2-3 one hind leg slides out to the right along the floor, 4-5 that leg fully stretched to the right just above the floor, body still crouched low, 6-8 the leg pulls back. |
| 7 | `e_rasteira` | folhas_arcade/rasteira | low tail-and-leg sweep: 1 deep crouch, 2-3 he spins low on one fist, 4-5 the straight hind leg and the horse tail sweep wide along the floor, 6-8 back to the crouch. |
| 8 | `e_ar_soco` | folhas_arcade/ar_soco | mid-air downward hammer fist, all frames in the air with the legs tucked: 1-3 the fist winds up over the head, 4-5 fist and bracer come down and forward at 45 degrees, 15% larger, 6-8 back to the tucked pose. |
| 9 | `e_bicicleta` | folhas_arcade/bicicleta | mid-air double hoof kick, all frames in the air: 1 tucked, 2-3 he leans back, 4-5 both hooves stomp forward at head height, fully stretched, horseshoes 15% larger, 6-8 back to tucked. |
| 10 | `e_rolamento` | folhas/e_rolamento (arte antiga) | low charge that passes behind the opponent: 1 stance, 2 drops the head and horns low, 3-6 a low tucked shoulder roll close to the ground, the same body size in every frame, 7 comes up on one knee, 8 crouch; every frame faces right (the game turns him). |
| 11 | `e_agarrao` | folhas/e_agarrao (arte antiga) | bite throw of an unseen opponent, only him drawn: 1 stance, 2 both hands reach forward, 3-4 the hands clamp an invisible opponent and the horse mouth bites forward, 5-6 he lifts and swings around, 7-8 he hurls forward with both arms. |
| 12 | `e_bola` | folhas/e_bola (arte antiga) | OWN PROJECTILE, body only (the fire is the separate fx_bufada sheet): 1 stance, 2-3 he rears the head back and inhales, chest swelling, 4-5 he thrusts the head forward with flared nostrils and open mouth at head height, neck stretched, 6-7 follow-through, 8 stance. Nothing comes out of the nose or mouth in the drawing. |
| 13 | `e_armada` | folhas/armada (arte antiga) | rising spinning hook kick: 1 low stance, 2-3 he turns sideways and starts to rise with one knee tucked, 4-5 he spins in the air with one straight leg sweeping high to the right, hoof leading and 15% larger, 6-7 falling with the leg folding, 8 landing hunched; the same body size in every frame. |
| 14 | `e_caneta` | folhas/e_caneta (arte antiga) | OWN SPECIAL, Satan's Slide Tackle (Carrinho de Satanás): 1 stance, 2-3 he dives low, 4-5 sliding on one hip with the leading hoof stretched forward along the floor, horseshoe 15% larger, the other leg folded, 6-7 getting up, 8 stance. No sparks drawn. |
| 15 | `e_golaco` | folhas/golaco (arte antiga) | super, a flurry of hooves: 1 stance, 2 crouches and clenches the fists, 3 knee strike with the knee high, 4 high kick with the leg fully stretched to the right at head height, 5 the knee folded back, 6 spinning back kick fully stretched to the right, 7 he rears up with both fists raised, 8 lands in the stance. Exactly two legs in every frame. |
| 16 | `e_galope` | folhas_arcade/anda (so a escala) | run in horse mode: a fast gallop leaning far forward, fists pumping, 1 push-off from both hind hooves, 2 airborne stretched, 3 front hoof lands, 4 gathers, 5-8 the same cycle with the other lead; mane and tail stream straight back; 8 loops into 1. |
| 17 | `e_provoca` | folhas/e_provoca (arte antiga) | taunt: 1-3 he scrapes a hoof on the ground twice like a bull, 4-6 he throws the head back and neighs at the sky, chest out, 7-8 he lowers the horns at the opponent and grins with big horse teeth. |
| 18 | `e_vitoria` | folhas/e_vitoria (arte antiga) | victory: 1 stance, 2-3 he rears up on the hind legs, 4-6 he neighs with both fists raised, 7-8 he lands and pounds his chest once; 8 holds. |
| 19 | `e_derrota` | folhas/e_derrota (arte antiga) | defeated: 1-2 he drops to his knees, 3-8 sitting on the floor with the hooves out, head and horns hanging, shoulders heaving slowly. |
| 20 | `despertar_boss` | folhas_arcade/ginga + conceito | transformation from the base Muay Thai fighter (first attached sheet) into the stallion warlord (concept): 1 the human fighter hunched, fists clenched, 2 the face lengthens into a muzzle, hair grows into a mane, 3 horns push out, skin darkens to red-brown, 4 the body swells, feet become hooves, the tail appears, 5 he rears up, collar and broken chain snap around the neck, 6 pauldron, bracers and shin guards clamp on, the shorts tear into the war skirt, 7 both hooves come down, 8 the war stance of the concept. Same ground line; the body grows only up to the size of the concept figure. |
| 21 | `fx_aura_crateras` | terceira figura do conceito | AURA, ground layer, drawn under the fighter's hooves: two round hoof-shaped craters side by side with glowing crimson cracks spreading outward on a flat ground line, short red sparks jumping from the cracks; 1-4 the cracks brighten and spread a little, 5-8 they dim and pull back; 8 loops into 1. Low and wide, nothing taller than a man's knee. |
| 22 | `fx_bufada` | nenhuma (escala: a cabeça do conceito) | OWN PROJECTILE effect: a snorted burst of red-orange fire: 1 a small twin jet as if from two nostrils on the left edge, 2-3 the jets merge into a fireball with a white-hot core, 4-6 the fireball travels as a loop of three frames with a short tail of flame, 7 it hits and splashes, 8 a fading ring of embers. |
| 23 | `fx_ferradura` | nenhuma | impact of the Stallion Buck: a horseshoe-shaped shockwave of crimson lightning opening toward the right: 1 a small white-hot horseshoe, 2-4 it grows and thins, bolts forking from its two tips, 5-6 it breaks into sparks, 7-8 the sparks fade. |
| 24 | `fx_vapor` | nenhuma (escala: a cabeça do conceito) | nostril steam, the effect that replaces the steam of the concept: two small white puffs side by side: 1 two tiny jets, 2-4 they puff out to the right and round up, 5-6 they drift up, 7-8 they thin out and vanish; 8 loops into 1. |

### Dúvidas que a ficha deixa em aberto

- **Mãos:** a ficha fala em "patadas de garra"; o conceito aprovado tem punho fechado com atadura vermelha e bracelete de espinhos. Segui o conceito (pancada de bracelete). Se o dono quiser garra, mudam `e_soco`, `e_baixo_soco`, `e_ar_soco` e o MODEL LOCK.
- **Especiais exclusivos e super exclusivo sem nome nem comando:** a ficha só cita a regra (4 especiais, 1 projétil, 1 kombo, 1 super) e os pedidos do áudio (coice, carrinho, galope). Usei os espaços que o gerador já tem (`compasso` = coice, `caneta` = carrinho, `bola` = bufada, `golaco` = super). Falta o dono dizer qual é o 4º especial e como é o super do boss; o garanhão de raio da aura atropelando a tela seria a escolha óbvia, mas não está na ficha e não entrou na fila.
- **Galope:** a ficha pede "corre no modo cavalo". Pus `e_galope`, mas não conferi se o gerador do Gutto tem estado de corrida que leia essa folha.
- **Chifrada:** a ficha fala em chifrada subindo como antiaéreo; o pente fino de anatomia diz que o golpe do `cabecada` é joelhada subindo. A linha da `e_cabecada` sobe de joelho com os chifres para cima. Confirmar qual membro bate.
- **Tamanho:** a ficha diz corpo "maior" no demônio. Mandei manter o tamanho da figura do conceito; se o boss tiver de ficar com a mesma altura da forma normal (caixas de colisão), isso tem de ser dito antes da ginga.
- **Transformação:** hoje são `despertar_a` (base) e `despertar_b` (vira o demônio). Pus uma só, `despertar_boss`. Se continuar em duas partes, a `despertar_a` da base também precisa de versão arcade.
- **Lata** (aquecimento) não tem versão despertada e ficou fora.

## Raiclaven, o Cientista Louco chefe de laboratório (`raiclaven`, prefixo `e_`)

Chat: **Raiclaven — boss**. Pasta: `sprites/raiclaven/quadros/folhas_arcade/`. Conceito aprovado: `sprites/raiclaven/quadros/folhas_arcade/e_conceito.png`.

Estilo de ataque (ficha, "Despertar novo: o Cientista Louco"): **ele fica quase parado, fazendo pose e dando ordens**;
estala os dedos, rege com a tesoura, e quem bate são as criaturas do laboratório. Golpes dele mesmo: tubo de ensaio
(projétil), seringa (agarrão), choque para cima (antiaéreo), fumaça (teleporte), o super de raios e as cinco folhas da
corrente da Cliente Zero. **Cabelo verde em toda folha** (pedido do dono). No conceito o braço mecânico fica do lado de
trás e segura a tesoura gigante; a mão da frente é a da luva de borracha preta, vazia. As folhas `e_` antigas em
`quadros/folhas/` são do cientista de cabelo preto e servem só de referência de tempo.

### Prompt base do boss (corpo, fundo magenta)

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached concept image shows the exact character to keep (the LEFTMOST figure, the one without aura): RAICLAVEN in
his final-boss awakened form, the Mad Scientist, chief of the laboratory. The same man: muscular, brown skin, goatee,
huge mad grin. His hair is bright GREEN, short and slicked back. Round goggles with glowing green lenses. A torn, stained
off-white lab overcoat with a ragged hem and rolled sleeves, a riveted steel plate on the chest of the coat, worn open
over a black barber shirt with a small red-white-blue striped barber pole badge. Black tool belt and apron with a green
test tube, a shaving brush and small tools. Baggy black pants, heavy riveted steel boots. A huge riveted steel
mechanical arm on the REAR side (the arm away from the opponent) with a round glowing green gauge, its steel hand
holding GIANT silver scissors. The FRONT arm is human, in a long black rubber glove, hand empty. On his back a steel
backpack with two glass tanks of glowing green liquid and two ringed coil towers with a ball on top, hoses running to
the mechanical arm.
MODEL LOCK, true in all 8 frames: the hair is GREEN, never black, never brown, never grey. Exactly two arms and two
legs: ONE mechanical arm, always the REAR one, always holding the same ONE pair of giant scissors (the scissors never
change hand, never multiply, never disappear unless the motion says so); ONE human arm, always the FRONT one, always in
the black rubber glove. Exactly two green tanks and two coil towers on the backpack. Goggles always on the eyes. No
comb in the hand. The body has the same size and proportions as the leftmost figure of the concept in every frame. Draw
NO lightning, NO floating blades, NO aura, NO smoke, NO liquid splash, NO sparks: all of those are separate effect
sheets. No lilac or purple light anywhere on him.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture. 1-pixel colored outline, never pure black, lighter or missing on the lit side. Small hard 1-3 pixel
specular highlights. Limited palette look.
Shadows shift hue: brown skin goes toward deep wine in shadow and warm cream in light; the off-white coat gets cool
blue-grey shadows and rust-brown stains, never beige mud; steel gets cool blue shadows and one hard white glint; the
black shirt, glove and pants are very dark blue, never pure black; the green of hair, lenses, gauge and tanks is the
only saturated colour. Outline dark wine on skin, dark blue on steel and cloth.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, feet on the same ground
line, every limb fully inside its own frame. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects (no fire, no sparks, no dust, no smoke, no speed lines, no motion trails).
On every attack, the striking limb or weapon on the contact frame is drawn 15% larger.
MOTION: <linha da folha>
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### Grupo 1: as 12 que mais aparecem (12 folhas)

| # | Folha | Base de referência | MOTION |
|---|---|---|---|
| 1 | `e_ginga` | folhas_arcade/ginga | boss idle loop, almost still and posing: feet wide, torso upright, the front gloved hand raised with the fingers curled like a conductor, the giant scissors held low by the mechanical arm; 1-4 the knees sink slightly while the scissors open slowly, 5-8 he rises and the scissors close with a snap; the coat hem and the hoses sway one frame late; the green liquid level in the tanks tilts with the body; 8 loops into 1; feet never slide. |
| 2 | `e_anda` | folhas_arcade/anda | slow menacing walk forward, heavy boots, torso upright, gloved hand raised, scissors low, two-step cycle with ALTERNATING legs: 1 front boot contact, 2 weight down, 3 passing, 4 up, 5-8 the same with the other leg; coat hem swings; 8 loops into 1. |
| 3 | `e_soco` | folhas_arcade/soco | he gives an order and snips: 1 stance, 2 the gloved hand rises, 3 he snaps the gloved fingers at face height, arm stretched forward, hand 15% larger, 4 the hand pulls back, 5 the mechanical arm swings forward, 6 the giant scissors thrust forward at chest height and shut, fully extended, blades 15% larger, 7 the arm recoils, 8 stance. |
| 4 | `e_chute_baixo` | folhas_arcade/chute_baixo | heavy steel-boot shove, he barely moves the torso: 1 stance, 2 the front boot lifts, 3 knee chambers low, 4-5 the boot sole pushes straight forward at shin height, boot 15% larger, hands unchanged, 6-7 the boot comes back, 8 stance. |
| 5 | `e_apanha` | folhas_arcade/apanha | hit in the face: 1 stance, 2-3 the head snaps back and the goggles go crooked, grin gone, 4-5 the torso bends back, the backpack tanks slosh, coat flying forward, 6-8 he straightens and pushes the goggles back with the gloved hand. |
| 6 | `e_queda` | folhas_arcade/queda | knocked down: 1 hit and bending back, 2 boots leave the ground, 3-4 flying backward horizontally, 5-6 falling onto his side with the backpack behind him, 7 bounces, 8 lying flat, scissors still in the mechanical hand resting on the floor; same body length in every frame. |
| 7 | `e_levanta` | folhas_arcade/levanta | getting up: 1 lying flat, 2-3 he rolls and pushes up with the mechanical arm, 4-5 one knee under, 6 rising, 7 he straightens the goggles with the gloved hand, 8 stance. |
| 8 | `e_defesa` | folhas_arcade/defesa | block with the machine: 1 stance, 2-3 he brings the mechanical forearm and the closed scissors up flat in front of face and chest like a shield, gloved hand behind it, 4-5 holds the block, 6-7 the impact slides him back a little, 8 still blocking. |
| 9 | `e_agachado` | folhas_arcade/agachado | 1 stance, 2-4 he lowers into a crouch examining the floor, gloved hand on the knee, scissors point resting on the ground, 5-8 he stays crouched with a small breathing bounce; 8 loops into 5. |
| 10 | `e_pulo` | folhas_arcade/pulo | jump with the coat opening like wings: 1 knees bent, 2 push-off, 3 rising with the legs tucking, 4-5 tucked at the top, coat spread wide behind, 6 falling with the legs opening, 7 reaching down, 8 landing with the knees bent. |
| 11 | `e_bola` | folhas/e_bola (arte antiga) | OWN PROJECTILE, test-tube throw, body only: 1 stance, 2 the gloved hand takes a green test tube from the belt, 3 the arm draws back behind the ear, 4 the arm whips forward, 5 the arm fully stretched forward at chest height with the gloved hand OPEN AND EMPTY, 15% larger (the flying tube is a separate effect), 6-7 follow-through, 8 stance. |
| 12 | `fx_aura_leque` | terceira figura do conceito | AURA, main layer, drawn behind the fighter: a radial fan of floating polished steel barber tools (scissors, straight razors, combs and blades), all pointing outward from the centre like a peacock tail, about twice the height of a man, with thin white-silver lightning jumping between the tools; 1-4 the fan opens a little wider and every tool rotates a few degrees clockwise, 5-8 it closes back and the lightning takes a different path; 8 loops into 1. Only steel greys and white, no lilac, no purple, no green. The lower centre of each cell, where the fighter stands, is left empty. |

### Grupo 2: o resto do kit, a transformação e os efeitos (20 folhas)

| # | Folha | Base de referência | MOTION |
|---|---|---|---|
| 1 | `e_martelo` | folhas_arcade/martelo | the heavy order, scissors as a conductor's baton: 1 stance, 2-3 the mechanical arm raises the giant scissors high over the head, blades open, 4-5 he swings them down and forward at head height, fully extended, blades 15% larger, 6-7 he straightens, 8 stance. |
| 2 | `e_cabecada` | folhas_arcade/cabecada | OWN SPECIAL, anti-air: 1 crouch, 2-3 he loads the mechanical arm low, 4-5 he rises and drives the giant scissors straight up above the head, arm fully stretched, blades open, 6-8 back to the crouch. No shock drawn (it is the separate fx_choque sheet). |
| 3 | `e_agarrao` | folhas/e_agarrao (arte antiga) | OWN GRAB, the giant syringe, only him drawn: 1 stance, 2 the gloved hand reaches forward and grips an invisible collar, 3 the mechanical arm tucks the scissors behind his back, 4 the gloved hand pulls the victim in while the steel hand brings up a giant syringe of green liquid, 5 he stabs the syringe forward at chest height, 6 pushes the plunger, laughing, 7 shoves away with the gloved hand, 8 stance with the scissors back in the steel hand. |
| 4 | `e_rolamento` | folhas/e_rolamento (arte antiga) | OWN SPECIAL, vanishing (the green smoke is a separate effect): 1 stance, 2 he raises the gloved hand, 3 throws it down, 4 crouches pulling the coat around himself, 5 curled tight, smallest, 6 opens up in a low crouch, 7 rises, 8 stance; every frame faces right (the game turns him). |
| 5 | `e_golaco` | folhas/e_golaco (arte antiga) | super pose: 1 stance, 2 he plants the feet, 3-4 both arms open wide, head thrown back laughing, 5-6 the coil towers on the backpack stretch taller and the scissors point at the sky, 7 he swings the scissors down pointing forward, 8 holds the pointing pose. No lightning drawn. |
| 6 | `e_corrente_parado` | folhas/e_corrente_parado (arte antiga) | idle loop holding a chain leash: the gloved front hand holds an iron chain that leaves the frame to the right at knee height, scissors low; 1-4 he sinks slightly, 5-8 rises; the chain sags and swings a little; 8 loops into 1. |
| 7 | `e_corrente_chicotada` | folhas/e_corrente_chicotada (arte antiga) | cracks the chain forward: 1 chain stance, 2 the gloved hand draws back to the shoulder, 3 hip turns, 4 the arm whips forward, 5 arm fully stretched at chest height, chain straight to the right edge, hand 15% larger, 6 hold, 7 the chain goes slack, 8 chain stance. |
| 8 | `e_corrente_mangual` | folhas/e_corrente_mangual (arte antiga) | flail swing: 1 chain stance, 2-3 the gloved hand swings the chain up in a circle over the head, 4 the arm at the top, 5 he brings it down hard forward, arm stretched at head height, 6 follow-through to the floor, 7 recovers, 8 chain stance. |
| 9 | `e_corrente_puxao` | folhas/e_corrente_puxao (arte antiga) | hauls the chain back: 1 chain stance, 2 leans back, 3-6 pulls the chain toward himself with the gloved hand and the steel hand alternating, body leaning further back each frame (the scissors hang from a hook on the belt in this sheet), 7 a last yank, 8 chain stance. |
| 10 | `e_corrente_giro` | folhas/e_corrente_giro (arte antiga) | super, hammer-throw spin with the chain: 1 chain stance, 2 grips the chain with both hands, 3-6 he turns on the spot leaning back against the pull, one quarter turn per frame (facing right, toward the viewer, left, away), coat flaring, 7 slows down facing right, 8 chain stance. |
| 11 | `e_chute_alto` | folhas_arcade/chute_alto | contemptuous side kick, torso leaning away: 1 stance, 2 the rear boot steps in, 3 the front knee chambers, 4-5 the leg drives out to the right at chest height, boot sole 15% larger, coat hem flying, 6-7 recoils, 8 stance. |
| 12 | `e_baixo_soco` | folhas_arcade/baixo_soco | low snip from the crouch: 1 crouch, 2-3 the mechanical arm draws the scissors back, 4-5 the open scissors thrust forward along the floor at ankle height and shut, blades 15% larger, 6-8 back to the crouch. |
| 13 | `e_ar_soco` | folhas_arcade/ar_soco | mid-air downward scissors stab, all frames in the air with the legs tucked and the coat spread: 1-3 the mechanical arm raises the scissors, 4-5 the closed scissors stab down and forward at 45 degrees, blades 15% larger, 6-8 back to the tucked pose. |
| 14 | `e_provoca` | folhas/e_provoca (arte antiga) | taunt: 1-3 he looks the opponent up and down, 4-6 he wags the gloved index finger and shakes his head, 7-8 he snips the scissors twice in the air, grinning. |
| 15 | `e_vitoria` | folhas/e_vitoria (arte antiga) | victory: 1 stance, 2-3 he raises a green test tube from the belt in the gloved hand, 4-6 he laughs with the head back, 7-8 he bows with the scissors arm folded across the chest; 8 holds. |
| 16 | `e_derrota` | folhas/e_derrota (arte antiga) | defeated: 1 knees give way, 2-3 he drops to sit on the floor, 4-8 sitting with BOTH legs stretched forward and clearly separated, goggles crooked, scissors lying on the floor beside him, head down. |
| 17 | `despertar_boss` | folhas_arcade/ginga + conceito | transformation from the base barber (first attached sheet: black hair, apron, steel right arm ending in scissors) into the Mad Scientist (concept): 1 the barber hunched, grinning, 2 he combs the hair back with the bare hand and it turns GREEN, 3 the green goggles snap onto the eyes, 4 he screams with the arms open, 5 the torn lab coat wraps around him from behind, 6 the backpack with the two green tanks and two coils clamps on, the steel arm grows a hand and grips the giant scissors, 7 the black rubber glove is on the front hand, 8 the stance of the concept. Same ground line, same body size. |
| 18 | `fx_aura_lascas` | terceira figura do conceito | AURA, ground layer: a row of small steel shards, razor blades and scissor tips stuck upright in a flat ground line around the place where the fighter stands; 1-4 new shards drop in and stick while the oldest ones tremble, 5-8 a thin white-silver spark runs along the row from left to right; 8 loops into 1. Low and wide, nothing taller than a man's knee, only steel greys and white. |
| 19 | `fx_tubo` | nenhuma (escala: a mão do conceito). FUNDO MAGENTA #FF00FF, porque o líquido é verde | OWN PROJECTILE effect: a glass test tube of glowing green liquid, corked: 1-5 it tumbles end over end through the air, one fifth of a turn per frame, 6 it shatters on impact, 7 a splash of green liquid and glass bits, 8 a small bubbling green puddle on a flat ground line. |
| 20 | `fx_choque` | nenhuma. FUNDO MAGENTA #FF00FF, porque o choque é verde | OWN SPECIAL effect: a vertical column of green electric shock rising from a point at the bottom, as tall as a man: 1 a small crackling knot, 2-4 the column shoots up and forks, white-hot core, 5-6 it holds and flickers, 7-8 it thins and breaks into sparks. |

### Dúvidas que a ficha deixa em aberto

- **As criaturas não estão nesta fila.** Cliente Zero (`mulher_*`, 6 folhas), as quatro cobaias (`cobaia_*`) e a `fila_clientes` existem só na arte antiga. A ficha diz que elas são o ataque principal, então o boss depende delas; precisam de fila arcade própria ou de o dono dizer que o boss luta sozinho.
- **Corrente no boss?** O conceito aprovado não mostra corrente nem a Cliente Zero. Mantive as cinco `e_corrente_*` porque a ficha manda; se o boss não usar a corrente, elas saem e os botões x, y, ↓+x e ↓+y ficam sem golpe definido.
- **Aura de lâminas contra ficha de criaturas:** a aura aprovada é um leque de tesouras, navalhas e pentes; a ficha não tem nenhum golpe que use essas lâminas flutuantes. Se o dono quiser um especial ou super com o leque (lâminas disparando), falta definir nome, comando e papel.
- **Botões a e b no Despertar:** a ficha não diz o que o cientista faz nos chutes. Pus `e_chute_baixo` e `e_chute_alto` como empurrão de bota e chute lateral, de segurança. Também não define golpe no ar (`e_ar_soco` é estocada de tesoura, por minha conta) nem ↓ + a/b.
- **Choque e fumaça verdes ou prata?** A ficha fala em choque verde e fumaça verde; a aura aprovada é só aço e raio branco-prata. Mantive verde nos efeitos de golpe (combina com os tanques) e prata só na aura. Confirmar.
- **Prancheta:** as folhas antigas usam prancheta (agachar, defender, provocar). O conceito não tem prancheta, então tirei: ele defende com o braço mecânico e a tesoura.
- **Qual Despertar vale:** a ficha ainda tem o texto do "Surto de Tesoura" (cabelo preto, Disco de Máquina etc.) no fim. Segui o Cientista Louco, que a própria ficha diz que substitui o Surto.
- **Efeito da porta de fumaça** das cobaias e os raios do super (`e_golaco`) não têm folha de efeito nesta fila; ficam para quando as criaturas entrarem.

## CK, o Ratão dono do paredão (`ck`, prefixo `b_`)

Chat: **CK — boss**. Pasta: `sprites/ck/quadros/folhas_arcade/`. Conceito aprovado: `sprites/ck/quadros/folhas_arcade/e_conceito.png`.

Estilo de ataque (ficha, "Modo Ratão"): **todo golpe é instável e louco**, cambaleia, quase cai e bate de ângulo
estranho, lento e de repente explosivo, sempre com o caco de garrafa. Nas folhas boss ele fica em **guarda baixa e
ameaçadora**, não parado. As folhas `e_` do Ratão que o Breno já fez **continuam valendo como a forma atual**; as boss
são novas e levam o prefixo `b_`, para não escrever por cima delas (o conceito chama `e_conceito.png` porque veio com
esse nome). Regras que mais reprovaram no Ratão e valem aqui: a garrafa sempre na mão da frente (a mais à direita na
imagem), uma garrafa só, o braço de cima passando na frente do rosto. O ChatGPT recusa desenhar o ato de fumar: nada na
boca, e a tragada é só pose de soprar; a fumaça entra como efeito.

### Prompt base do boss (corpo, fundo magenta)

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached concept image shows the exact character to keep (the LEFTMOST figure, the one without aura): CK in his
final-boss awakened form, the big boss of the street sound-system party. The same young Black man: short bleached
platinum-white curly hair with faded sides, thin moustache and goatee, a small stud earring, cocky half smile. Mirrored
wraparound sunglasses with orange-red lenses worn ON THE EYES. Three gold chains, the largest one carrying a gold
rat-skull medallion. A short-sleeve shirt worn open over a white tank top: dark navy with a pattern of plain white waves
and flames and gold piping on the collar, sleeves and hem; matching navy board shorts with the same white waves and a
gold side stripe. A small black waist bag strapped across the chest. White hand wraps on both hands and wrists. White
crew socks and slides with a gold strap. A broken green glass bottle, held by the neck, in the FRONT hand.
MODEL LOCK, true in all 8 frames: exactly two arms, two hands and two legs. Exactly ONE broken green bottle, ALWAYS in
the FRONT hand, the hand furthest to the RIGHT in the picture; it never changes hand, never disappears, never becomes a
whole bottle, and there is never a second bottle. The other hand is always empty, only the white wrap. The rear arm
never comes out from behind the back. The sunglasses stay ON THE EYES, never pushed up on the head. Exactly three gold
chains and one rat-skull medallion. The pattern on shirt and shorts is only plain waves and flames: no swirl emblem, no
logo, no letters, no brand mark anywhere; the bottle has no label. Nothing in the mouth: no cigarette, no joint. Draw NO
smoke, NO speakers, NO glass shards on the ground, NO aura: all of those are separate effect sheets. The body has the
same size and proportions as the leftmost figure of the concept in every frame.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture. 1-pixel colored outline, never pure black, lighter or missing on the lit side. Small hard 1-3 pixel
specular highlights. Limited palette look.
He is unstable and dangerous: every move wobbles, stumbles, sways off balance and then strikes from a strange angle,
lazy and suddenly explosive. Shadows shift hue: brown skin goes toward deep wine in shadow and warm cream in light; the
navy cloth gets cool blue light and violet shadow; the whites get cool lilac-blue shadows, never grey; gold gets a hard
orange shadow and a white glint; the green glass has one hard white highlight. Outline dark wine on skin, dark
blue-purple on clothes and hair.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, feet on the same ground
line, every limb fully inside its own frame. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects (no fire, no sparks, no dust, no smoke, no speed lines, no motion trails).
On every attack, the striking limb or weapon on the contact frame is drawn 15% larger.
MOTION: <linha da folha>
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### Grupo 1: as 12 que mais aparecem (12 folhas)

| # | Folha | Base de referência | MOTION |
|---|---|---|---|
| 1 | `b_ginga` | folhas_arcade/e_referencia_ginga | low threatening guard loop, never standing relaxed: knees bent, weight forward, chin down behind the front shoulder, the broken bottle held forward at belly height pointing at the opponent, the empty rear hand open near the chin; 1-4 he sinks and sways to one side, the bottle tip draws a small circle, 5-8 he rises and sways back; chains and shirt tails lag one frame; 8 loops into 1; the rear foot never slides. |
| 2 | `b_anda` | folhas_arcade/e_anda | prowling walk forward in the low guard, shoulders rolling, slides scuffing, the bottle kept forward, two-step cycle: 1 front foot contact, 2 down, 3 passing, 4 up, 5-8 the same with the other leg; 8 loops into 1. |
| 3 | `b_soco` | folhas_arcade/e_soco | two bottle slashes and a stab: 1 guard, 2 the bottle hand cocks back across the chest, 3 a horizontal slash at chest height, arm stretched, bottle 15% larger, 4 the backhand slash coming back, 5 he stumbles one step in, 6 a straight stab with the broken bottle fully extended at chest height, 15% larger, 7 he wobbles recovering, 8 guard. |
| 4 | `b_chute_alto` | folhas_arcade/e_chute_alto | high slide kick out of a dance step: 1 guard, 2-3 he turns sideways into a funk dance step, never showing his full back, 4-5 the leg kicks high to the right at head height, the sole of the slide 15% larger, torso leaning back, bottle arm out for balance, 6-7 the leg comes down and he staggers, 8 guard. |
| 5 | `b_apanha` | folhas_arcade/e_apanha | hit in the face: 1 guard, 2-3 the head snaps back, chains flying up, sunglasses still on, 4-5 the torso bends back, the bottle arm flung out, 6-8 he shakes his head and comes back to the low guard, grin returning. |
| 6 | `b_queda` | folhas_arcade/e_queda | knocked down: 1 hit and bending back, 2 feet leave the ground, 3-4 flying backward horizontally, 5-6 falling onto his back, 7 bounces, 8 lying flat on his back, bottle still in the front hand; same body length in every frame. |
| 7 | `b_levanta` | folhas_arcade/e_levanta | getting up: 1 flat on his back, 2-3 he sits up slowly, 4-5 pushes up with the empty hand, 6-7 on his feet, he straightens the gold chains with the empty hand, 8 low guard. |
| 8 | `b_defesa` | folhas_arcade/e_defesa | block: 1 guard, 2-3 he raises both forearms, the bottle forearm crossed in front of the face, 4-5 holds, 6-7 the impact slides him back a little, 8 still blocking. |
| 9 | `b_agachado` | folhas_arcade/e_agachado | 1 guard, 2-4 he squats down low like a funk dancer, bottle forward at shin height, 5-8 he stays squatting with a small bounce; 8 loops into 5. |
| 10 | `b_pulo` | folhas_arcade/e_pulo | jump: 1 knees bent, 2 push-off, 3 rising tucked, 4 top with the bottle raised in front, 5 tucked, 6 falling with the legs opening, 7 reaching down, 8 landing. |
| 11 | `b_grave` | folha nova (ref: b_ginga aprovada) | OWN SPECIAL, Sound-Wall Bass (Grave do Paredão): 1 low guard, 2 he lifts the front knee high, 3 holds it up, grinning, 4 stomps the slide down hard, 5 both arms thrown wide open and chest out at the moment of the stomp, bottle pointing up, 6 holds the open pose leaning back as if pushed by the bass, 7 arms come in, 8 low guard. No speakers and no wave drawn. |
| 12 | `fx_aura_paredao` | terceira figura do conceito (e folhas_arcade/fx_paredao só para a forma) | AURA, main layer, drawn behind the fighter: a wall of stacked loudspeakers made entirely of thick grey-green smoke, about twice the height of a man and three times as wide, the round speaker cones clearly readable in the smoke; 1-4 the smoke cones push out with the beat and the edges of the wall curl outward, 5-8 the cones pull back in and the top of the wall rolls like a slow cloud; a few tiny orange embers drift up; 8 loops into 1. Only smoke: no solid black boxes, no chrome, no lights, no text. The lower centre of each cell, where the fighter stands, is left empty. |

### Grupo 2: o resto do kit, a transformação e os efeitos (19 folhas)

| # | Folha | Base de referência | MOTION |
|---|---|---|---|
| 1 | `b_martelo` | folhas_arcade/e_martelo | overhead bottle smash: 1 guard, 2-3 the bottle rises high, the bottle arm passing IN FRONT of the face, never behind the head, 4-5 he brings it down and forward at head height, body weight falling into it, bottle 15% larger, 6-7 he straightens, wobbling, 8 guard. |
| 2 | `b_chute_baixo` | folhas_arcade/e_chute_baixo | slide slap to the shin: 1 guard, 2 the front foot lifts, 3 chambers low, 4-5 the slide slaps forward at shin height, 15% larger, 6-7 back, 8 guard. |
| 3 | `b_cabecada` | folhas_arcade/e_cabecada | rising bottle slash, anti-air: 1 deep squat, 2-3 he loads, 4-5 he springs up slashing the bottle straight up above the head, arm in front of the face, 6-8 back to the squat. |
| 4 | `b_rasteira` | folhas_arcade/e_rasteira | funk-dance leg sweep: 1 deep squat, 2-3 the empty hand on the floor, he spins low, 4-5 the straight leg sweeps wide along the floor, 6-8 back to the squat. |
| 5 | `b_ar_soco` | folhas_arcade/e_ar_soco | mid-air downward bottle slash, all frames in the air with the knees tucked: 1-3 the bottle winds up in front of the head, 4-5 it slashes down and forward at 45 degrees, 15% larger, 6-8 tucked again. |
| 6 | `b_rolamento` | folhas_arcade/e_rolamento | dance roll that goes behind the opponent: 1 guard, 2 he spins into a low dance step, 3-4 rolls forward over one shoulder, bottle hand held away from the body, 5-6 springs up, 7 lands low, 8 guard; every frame faces right (the game turns him). |
| 7 | `b_agarrao` | folhas_arcade/e_agarrao | street grab of an unseen opponent, only him drawn: 1 guard, 2 the EMPTY hand grabs an invisible collar, 3-4 he pulls in and leans his face close, grinning, 5 headbutts, 6 shoves away with the empty hand, 7-8 he straightens the sunglasses with the empty hand. |
| 8 | `b_bola` | folhas_arcade/e_bola | OWN PROJECTILE, Flying Bottle, body only: 1 guard, 2 the EMPTY rear hand reaches behind the waist bag, 3-4 that arm winds back over the shoulder, hand closed as if holding something not drawn, 5-6 an overhand lob forward, the hand opening EMPTY, 15% larger, 7 follow-through, stumbling, 8 guard. The thrown bottle is a separate effect; the broken bottle stays in the front hand. |
| 9 | `b_beck` | folhas_arcade/e_beck | big breath pose (also used for the puff in the face): 1 guard, 2 he leans back lazily, 3-4 inhales deeply, chest swelling, 5-6 leans forward off balance and blows a strong breath forward with puffed cheeks and pursed lips, 7 stumbles a step, 8 guard. Nothing in the mouth, no smoke drawn. |
| 10 | `b_juliet_voadora` | folhas_arcade/e_juliet_voadora | boomerang throw with the EMPTY hand, body only: 1 guard, 2 the empty hand goes to the hip, 3-4 winds back sideways, hand closed as if holding something not drawn, 5-6 a flat sidearm flick forward at chest height, hand opening EMPTY, 15% larger, 7 the open hand waits, 8 the hand closes as if catching, guard. Sunglasses stay on the eyes, bottle stays in the front hand. |
| 11 | `b_caneta` | folhas_arcade/e_caneta | OWN SPECIAL, Ratão Step dash: 1 guard, 2-3 fast funk footwork on the spot, 4-5 he dashes forward dancing with a slide kick fully extended to the right at waist height, sole 15% larger, 6-7 spins out of it, 8 guard. |
| 12 | `b_golaco` | folhas_arcade/e_golaco | super, Corner Party: 1 guard, 2 he raises the bottle in front of the face and grins, 3 slash, 4 slide kick, 5 backhand slash, 6 a dancing spin, 7 a big overhead smash, the bottle arm passing in front of the face, 8 pose with the bottle held out. One bottle only, always the front hand. |
| 13 | `b_provoca` | folhas_arcade/e_provoca | taunt: 1-3 a short funk step in place, 4-6 he taps the frame of the sunglasses with the empty hand and waves the opponent in, 7-8 he laughs, shoulders bouncing. |
| 14 | `b_vitoria` | folhas_arcade/e_vitoria | victory: 1 guard, 2-3 he flicks the gold medallion with the empty hand, 4-6 he dances, 7-8 poses with the broken bottle resting on the front shoulder; 8 holds. |
| 15 | `b_derrota` | folhas_arcade/e_derrota | defeated: 1-2 he drops to sit, 3-8 sitting with the legs out, sunglasses crooked, chains tangled, dazed, the bottle on the floor beside the front hand. |
| 16 | `despertar_boss` | folhas_arcade/e_referencia_ginga + conceito | from the current Ratão form (first attached sheet) to the boss (concept): 1 the Ratão stance hunched, 2 he pulls the sunglasses from the head down onto the eyes, 3 the plain shirt and shorts darken to navy, 4 white waves and flames spread over the cloth, gold piping appears, 5 the second and third gold chains and the rat-skull medallion drop onto the chest, 6 the waist bag strap snaps across the chest, 7 he sinks into the low guard, 8 the low threatening guard of the concept. Same body size, bottle always in the front hand. |
| 17 | `fx_aura_aneis` | terceira figura do conceito | AURA, second layer, drawn in front of the wall: rings of grey-green smoke blown out of the speaker cones, seen at an angle as flat ovals; 1-8 each ring leaves the centre, grows wider, thins and breaks, three rings at different stages in every frame so the loop never empties; 8 loops into 1. |
| 18 | `fx_grave` | nenhuma | OWN SPECIAL effect, the bass shove: a vertical arc of compressed grey-green smoke travelling to the right like a pressure wave: 1 a thin bright arc, 2-5 it widens and moves right, the smoke behind it torn into streaks, 6-7 it breaks up, 8 wisps. |
| 19 | `fx_cacos` | nenhuma. FUNDO MAGENTA #FF00FF, porque o vidro é verde | OWN PROJECTILE effect, what the Flying Bottle leaves: green glass shards on a flat ground line: 1 the bottle bursts, 2-3 shards fly outward low, 4 they land, 5-8 a small patch of upright glinting shards stays on the floor, one white glint moving across them. |

### Dúvidas que a ficha deixa em aberto

- **Prefixo `b_`:** foi escolha minha para não colidir com as `e_` do Ratão. Se o dono quiser que o boss tome o lugar das `e_`, é só renomear; a fila não muda.
- **Transformação:** a ficha descreve base → Ratão (`despertar_a`, `despertar_b`). Não diz quando o Ratão vira o boss. Pus `despertar_boss` saindo do Ratão atual; se o boss for a única forma despertada, a `despertar_b` é que tem de ser refeita com o modelo novo.
- **Juliet Voadora:** a ficha joga o óculos como bumerangue, e o boss usa o óculos nos olhos o tempo todo. Deixei a `b_juliet_voadora` só com o gesto da mão vazia; falta decidir o que voa (o medalhão? um segundo óculos?) ou se o golpe sai.
- **Garrafa Voadora contra "uma garrafa só":** a `e_bola` atual puxa uma garrafa inteira nova. Na boss o arremesso é só o gesto com a mão vazia e a garrafa vem do `fx_garrafa`, para a regra não quebrar. O mesmo vale para a segunda garrafa do fecho do Baile da Esquina (`b_golaco`).
- **Folhas que o Ratão não tem:** não existem `e_afastar`, `e_baixo_soco`, `e_rasteirinha`, `e_bicicleta`, `e_compasso` nem `e_armada`, e o `gerar_ck.py` ainda não existe para dizer o que o jogo usa nesses espaços. Não criei as `b_` correspondentes; a ficha também não desenha a corrente b inteira (chute de meia, rasteira de baile, Passinho do Baile) nem o assopro (usei a pose da `b_beck`).
- **Grave do Paredão:** é especial da ficha sem folha no Ratão. A `b_grave` é nova, sem base de tempo.
- **Estampa e marcas:** a ficha tem a exceção de marca pedida pelo Breno (Lacoste na base, estilo Cyclone no Ratão). Para o boss a ordem desta rodada é ondas e chamas genéricas, sem redemoinho nem símbolo de marca, e foi isso que o prompt trava. No conceito, as costas da camisa têm uma caveira de rato com duas garrafas cruzadas; em folha de lado ela quase não aparece e não pedi.
- **Tatuagens:** o conceito mostra tatuagem no antebraço e na panturrilha. Não pus no prompt, porque tatuagem pequena muda de quadro para quadro; se o dono fizer questão, entra no MODEL LOCK.
- **Fundo dos efeitos de fumaça:** a fumaça é cinza-esverdeada e o fundo é verde puro. A `fx_aura` atual do CK foi feita assim, mas não conferi como ela recorta.

