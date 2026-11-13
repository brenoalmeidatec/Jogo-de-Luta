"""Roteiro das folhas do Gbzin, o Pastor do Jiu-Jitsu, para o ChatGPT (ficha em docs/fichas/gbzin.md).

Mesmo molde do folhas_ck.py. Estilo arcade anos 90 (docs/biblia-de-arte.md#estilo-arcade-anos-90). Cada folha: 8
quadros em fila, fundo magenta #FF00FF, salva em sprites/gbzin/quadros/folhas_arcade/<nome>.png, com a referência
anexada: referencia_ginga.png na forma base, e_referencia_ginga.png no Deus Motoboy (folhas e_*). Efeitos (fx_*) vão em
fundo verde #00FF00 e sem o lutador. Os nomes são os espaços do kit no gerador (gerar_pengaro.FOLHAS) mais as folhas
próprias do Gbzin; o golpe é o do Gbzin, não o de outro lutador.

Ordem (ficha, "Para o Alisson criar"):
  1. conceito         com as 3 fotos anexadas (fora do git), sem folha de referência ainda
  2. referencia_ginga com o conceito aprovado anexado -> o Breno aprova
  3. folhas da base   com a referencia_ginga anexada
  4. e_conceito       com a referencia_ginga anexada -> aprovação
  5. e_referencia_ginga e as folhas e_*, com o e_conceito (e a folha normal do mesmo golpe) anexados
  6. fx_*             sem lutador

`python ferramentas/folhas_gbzin.py`        lista os nomes, na ordem
`python ferramentas/folhas_gbzin.py nome`   imprime o pedido completo
`python ferramentas/folhas_gbzin.py --md`   escreve docs/arcade/fila_gbzin.md (a fila com todos os prompts)
"""
import sys
from pathlib import Path

ESTILO = """Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, thick strong torso, big hands and feet; he is the heavy grappler of the cast, stocky and solid but not fat. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no noise, no texture. Shadows shift hue: skin shadows toward wine red, highlights toward warm cream; white clothes get cool lilac shadows; black clothes get blue-grey highlights. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter on the lit side. Small hard 1-3 pixel highlights. Limited palette look.

Layout: one single row of 8 frames in 8 equal-width cells, wide image, side view, always facing right, same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. The figure FILLS its cell (big and sharp, never a small figure). Each figure stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects unless the motion asks for them.

Consecutive frames differ by a small amount, so the motion looks smooth in sequence.

Anatomy check for every frame: exactly two arms and two legs, both hands always visible, elbows and knees bend the natural way, no extra or missing limbs, the body never twists into an impossible pose.

Fighting-game timing (attacks): a clear anticipation pose before the hit, at most one stretched smear pose right before contact, the contact pose with the striking limb (or the staff) fully extended and drawn about 15% bigger, then a recovery that is longer on heavy moves; the brown belt ends and the hair fringe lag 1-2 frames behind the body and settle.

MOTION: """

PERSONAGEM = """Gbzin, the jiu-jitsu goat shepherd: a young white man with light pinkish skin, short straight dark-brown hair with a fringe over the forehead, round face with a thin short beard, calm friendly half-smile. Strong stocky grappler build. Outfit: black sleeveless tank top, white gym shorts with a thin black side stripe, a brown jiu-jitsu belt tied around the waist over the shorts with the two ends hanging, black sneakers, a gold wristwatch on the left wrist. He carries a SHORT wooden shepherd's crook (about as long as his arm, with a curved hook at the top) in the BACK hand."""

CABECA = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached sprite sheet shows the exact character to keep: """ + PERSONAGEM + """ Same face, same colors and same size as the attached sheet. He fights like a jiu-jitsu grappler from the countryside: grabs, pulls, takes down and twists; his kicks push people away; he hooks people with the crook. STAFF RULE: the crook is always in the same hand (the back hand, the arm drawn behind the torso) in all 8 frames unless the motion says otherwise; it never changes hands and never disappears.

""" + ESTILO

DEUS_MOTOBOY = """Gbzin awakened as the DELIVERY GOD (Deus Motoboy): same face and same stocky body as the base form, same short dark-brown hair with fringe and thin beard. An open-face GOLD motorcycle helmet with two small white wings on the sides (like a messenger god), a black eyepatch with a small gold star over the LEFT eye (a stylish costume piece), a black and neon-green motorcycle jacket with silver reflective stripes, black biker gloves, black leather pants, black boots, a bigger gold wristwatch. A square neon-green thermal delivery backpack on his back with a small ring of light above it like a halo. In the FRONT hand he always holds a closed square PIZZA BOX (he hits, blocks and throws with it); in the BACK hand a short motorbike HANDLEBAR with a curved hooked end (it replaced the shepherd's crook). No brand names, no text, no logos."""

CABECA_MOTOBOY = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached sprite sheet shows the exact character to keep: """ + DEUS_MOTOBOY + """ Same colors and same size as the attached sheet. He is much faster than the base form: a hyperactive delivery rider in a hurry, quick sharp moves, leaning forward. ITEM RULE: the pizza box is ALWAYS in the front hand (the arm closest to the viewer, drawn in front of the torso) and the handlebar ALWAYS in the back hand, in all 8 frames; they never swap hands, never merge and never disappear.

""" + ESTILO

CABECA_FX = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

A visual effect for a 1990s arcade fighting game, hand-pixeled, hard-edged flat shading in 2-3 tones, no gradients, no dithering, 1-pixel colored outline. One single row of 8 frames in 8 equal-width cells, wide image. Flat solid pure green background (#00FF00) everywhere (if the effect itself is green, use magenta #FF00FF instead). No fighter, no text, no ground.

MOTION: """

# os dois primeiros pedidos: das fotos ao modelo do personagem
CONCEITO = {
    "conceito": """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached photos show the real young man this character is based on (in the third photo, only the young man who appears in the other two photos; ignore the other person). Create an ORIGINAL 1990s arcade fighting game character concept sheet inspired by him: keep his face shape, hair and beard recognizable, but drawn as a heroic pixel-art fighter, not a photo. Character: """ + PERSONAGEM + """

Sheet layout, flat solid magenta background (#FF00FF), no text: 1) full body front view, standing, 2) full body side view facing right in a low grappler stance, crook in the back hand, 3) full body back view, 4) a big bust portrait of the face. Same scale for the three full bodies.

""" + ESTILO.split("Layout:")[0],
    "e_conceito": """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached sprite sheet shows Gbzin in his base form. Create the concept sheet of his awakened form, keeping the exact same face, body and height: """ + DEUS_MOTOBOY + """

Sheet layout, flat solid magenta background (#FF00FF), no text: 1) full body front view, standing, pizza box in the front hand, 2) full body side view facing right in his fighting stance, 3) full body back view showing the delivery backpack with its light halo, 4) a big bust portrait of the face with the winged gold helmet and the star eyepatch. Same scale for the three full bodies. No aura drawn (the aura is a separate effect).

""" + ESTILO.split("Layout:")[0],
}

# espaço do kit -> movimento do Gbzin (forma base)
FOLHAS_GB = {
    "referencia_ginga": "grappler idle loop, the base reference for every other sheet: wide low stance, knees bent, both open hands forward ready to grab, the crook held low in the back hand, calm half-smile, slow heavy breathing. Frames 1 to 4 he sinks slightly, 5 to 8 he rises; frame 8 flows back into frame 1. Standing tall.",
    "anda": "slow heavy walk forward, an 8-frame loop: short solid steps, hands forward ready to grab, crook in the back hand, belt ends swinging; the legs complete a full two-step cycle and frame 8 flows back into frame 1. Standing tall.",
    "corre": "the funny PENGUIN RUN, an 8-frame loop: very short fast waddling steps with the feet turned out, body rocking side to side, both arms held stiffly open to the sides and flapping, crook flapping in the back hand, the face proud and serious. Frame 8 flows back into frame 1.",
    "recuo": "a short hop backward: 1 stance, 2 knees bend, 3 and 4 small hop back with both feet off the ground, arms slightly open, 5 and 6 landing heavily, 7 and 8 stance.",
    "soco": "x chain, open-hand slap then short elbow: 1 stance, 2 the front open hand pulls back, 3 a big open-hand slap forward at face height, arm fully extended, 4 it returns, 5 he steps in, 6 a short front elbow strike forward at face height, 7 recovering, 8 stance. Standing tall.",
    "martelo": "y chain, the crook strikes: 1 stance, 2 the crook rises over the back shoulder, 3 and 4 a straight thrust with the crook forward at chest height, arm fully extended, 5 he spins the crook in a circle in front of him, 6 and 7 an overhead chop with the crook coming down at head height, 8 stance.",
    "chute_baixo": "a low front kick to the shin: 1 stance, 2 the front sneaker lifts, 3 chambers low, 4 and 5 the sole thrusts forward at shin height, hands stay forward, 6 and 7 back, 8 stance.",
    "chute_alto": "a front push kick to the chest: 1 stance, 2 and 3 the back knee rises to the chest, 4 and 5 the sole thrusts straight forward at chest height, leaning back, 6 and 7 the foot comes down, 8 stance.",
    "afastar": "a double-leg mule kick that launches the opponent (Coice): 1 stance, 2 he crouches and puts both hands on the ground, 3 and 4 both legs fire forward together at belly height like a goat kick, body almost horizontal, 5 holding, 6 and 7 he rolls back up, 8 stance.",
    "agachado": "going down into a low wrestler crouch. 1 to 4 he bends the knees deep, hands forward ready to grab, crook low; 5 to 8 he stays crouched rocking slightly, eyes up.",
    "baixo_soco": "a low crook poke from the crouch: 1 deep crouch, 2 and 3 loads the crook back, 4 and 5 jabs the crook tip straight forward at shin height, 6 to 8 back to the crouch.",
    "cabecada": "rising crook hook anti-air from the crouch: 1 deep crouch, 2 and 3 he dips lower and loads, 4 and 5 he springs up swinging the hooked crook straight up above his head, the hook pointing up and forward, 6 to 8 he settles back into the crouch.",
    "rasteirinha": "a quick low shin kick from the crouch: 1 deep crouch, 2 and 3 the front leg slides out, 4 and 5 the sneaker sole stretched just above the floor, 6 to 8 it pulls back.",
    "rasteira": "a jiu-jitsu sweep (Raspagem): 1 stance, 2 he drops to sit on the floor, 3 sitting, one hand on the ground, 4 and 5 both legs scissor forward along the floor, fully extended, 6 and 7 he rolls back up to his feet, 8 stance.",
    "pulo": "a heavy jump. 1 knees bent ready, 2 pushing off, 3 rising with the legs tucking, 4 tucked at the top, crook up, 5 still tucked, 6 falling with the legs opening, 7 reaching down, 8 landing heavily with knees bent.",
    "ar_soco": "a crook strike from above in mid air: all frames in the air, knees tucked. 1 to 3 the crook winds up over the head, 4 and 5 it chops down and forward diagonally, 6 to 8 back to the tucked pose.",
    "bicicleta": "a flying knee in mid air. All frames in the air. 1 tucked, 2 and 3 he grabs forward with both hands, 4 and 5 the front knee drives forward at head height, 6 to 8 back to tucked.",
    "defesa": "blocking: 1 stance, 2 and 3 he raises both forearms in front of the face, crook held across in front of the forearms like a bar, 4 and 5 he holds the block, 6 and 7 the impact pushes him back a little, 8 still blocking.",
    "apanha": "getting hit in the face: 1 stance, 2 and 3 the head snaps back, fringe flying, mouth open, 4 and 5 the torso bends back with the arms flung out, crook still in the back hand, 6 to 8 he shakes it off and returns to the stance, calm smile coming back.",
    "queda": "being knocked down, 8 clearly SEPARATED figures: 1 hit and bending back, standing, 2 feet leaving the ground, body tilted back, 3 and 4 flying backward in the air, body diagonal, 5 body horizontal in the air, face up, 6 landing on his back on the ground, legs up, 7 a small bounce, 8 lying flat on his back on the ground, head on the left, feet on the right. The crook stays in the hand.",
    "levanta": "getting up from the floor: 1 flat on his back, 2 and 3 he rolls to the side, 4 and 5 technical stand-up of jiu-jitsu (one hand and one foot on the floor, the other leg passing back), 6 and 7 standing and fixing the belt, 8 stance.",
    "rolamento": "Penguin Step that passes behind the opponent: 1 stance, 2 he starts the penguin waddle with arms open, 3 and 4 he waddles forward fast with tiny steps, 5 and 6 he spins around on one foot, 7 he faces left already in stance, 8 he turns back to face right in stance.",
    "agarrao": "Bye Bye Kid (bear hug): 1 stance, 2 both arms reach forward and wrap around an invisible opponent, 3 and 4 he lifts and shakes, leaning back, 5 and 6 he arches back throwing the invisible opponent over and behind him, 7 he stands up, 8 stance. No second person is shown.",
    "bola": "Loose Goat throw pose (the goat itself is a separate effect): 1 stance, 2 he whistles with two fingers in the mouth, 3 and 4 he points forward with the crook commanding, 5 and 6 he swings the crook forward low like herding, 7 he laughs, 8 stance. Nothing comes out of the crook.",
    "compasso": "Crook Hook (Gancho do Pastor): 1 stance, 2 and 3 he winds the crook back, 4 and 5 he lunges and extends the crook far forward at neck height with the hook at the tip, arm and crook fully extended, 6 and 7 he pulls the crook back toward himself strongly as if dragging someone in, 8 he catches with the front arm open. Standing tall.",
    "armada": "Closed Guard counter: 1 stance, 2 and 3 he drops on his back on the floor, legs up in a jiu-jitsu guard, 4 waiting with the legs raised, 5 and 6 the legs close and twist as if trapping an attack, 7 he scissors and sweeps, 8 he springs back up into stance.",
    "caneta": "Flying Arm-lock: 1 stance, 2 he crouches, 3 and 4 he jumps forward and up, arms reaching to grab, 5 and 6 in the air his legs wrap and his body twists sideways as if catching an arm, 7 and 8 he falls to the ground sitting in an arm-lock position, legs crossed, arms pulling.",
    "golaco": "a super move, Countryside Choke: 1 stance, 2 he waddles forward penguin style, 3 he jumps on the back of an invisible opponent and locks a rear choke, 4 he squeezes, 5 he switches to an arm-lock, 6 he drops sitting with a sweep, 7 he taps the floor three times laughing, 8 he stands in stance. No second person is shown.",
    "provoca": "a taunt: 1 stance, 2 and 3 he leans on the crook like a calm shepherd, 4 to 6 he waves the opponent in with the front hand, calm smile, 7 and 8 he checks the gold wristwatch with a shrug.",
    "vitoria": "a victory: 1 stance, 2 and 3 he ties the brown belt tighter, 4 to 6 he raises the crook overhead proudly, 7 and 8 he poses with the crook on the shoulder, smiling.",
    "lata": "an intro warm-up: 1 stance, 2 and 3 he stretches the neck side to side, 4 and 5 he slaps his own shoulders, 6 he spins the crook once, 7 he points at the opponent, 8 stance.",
    "derrota": "defeated: 1 and 2 he drops to sit on the floor, 3 to 8 sitting with legs out, crook across the lap, scratching his head, upset.",
    # transformação, parte 1, ainda na roupa da base
    "despertar_a": "the transformation, part one, still in the BASE FORM outfit: 1 stance, 2 he looks down at his pocket, 3 he takes out a smartphone that is ringing and answers it at the ear, 4 he nods listening to the boss, 5 he puts the phone away and looks up, 6 a pizza box falls from the sky into his front hand, 7 he holds the pizza box proudly with a determined face, 8 a bright neon-green light floods him from behind (no motorbike drawn), only the silhouette shows.",
    # folhas próprias do Gbzin (fora do kit do Pengaró)
    "cajado_chao": "Staff Strike on the ground: 1 stance, 2 and 3 he raises the crook high with both hands, 4 and 5 he slams the crook tip into the ground in front of him, crouching, 6 and 7 he pulls it out, 8 stance.",
    "rolo_feno": "Hay Bale Roll: 1 stance, 2 he tucks into a ball, 3 to 6 he rolls forward along the ground curled up like a hay bale (each frame rotated about 90 degrees more), 7 he unrolls, 8 he stands in stance.",
    "montada": "the Mount (crouch grab), always facing right: 1 low crouch, 2 he dives forward low and grabs, 3 he sits on top of an invisible opponent lying on the floor (mount position, knees on the floor), 4 and 5 a big punch down, 6 a second punch down, 7 a third punch down, 8 he gets up into stance. No second person is shown.",
    "ordenha": "Goat Milking (command grab): 1 stance, 2 both hands grab forward, 3 and 4 he spins around in place holding an invisible opponent, crook under the arm, 5 and 6 a full turn back to facing right, 7 he swings the crook forward hard to send the opponent away, 8 stance. No second person is shown.",
}

# a transformação, parte 2: já de Deus Motoboy (anexe a e_referencia_ginga)
DESPERTAR_B = "the transformation, part two, already transformed: 1 bright neon-green light still covering most of the body, 2 the light thins and reveals the Delivery God (winged gold helmet, star eyepatch, neon-green jacket, delivery backpack, pizza box in the front hand), 3 he stands as if he had just jumped off a motorbike (no motorbike drawn), knees bent from the landing, 4 he straightens, 5 he spins the handlebar in the back hand, 6 he raises the pizza box like a trophy, 7 he taps the helmet, 8 he settles into the stance of the attached sheet with a confident grin."

# folhas e_<nome> do Deus Motoboy (anexe o e_conceito / e_referencia_ginga e a folha normal do mesmo golpe)
FOLHAS_MOTOBOY = {
    "referencia_ginga": "idle loop, the reference for every Delivery God sheet: a hyperactive bouncing stance on the toes like a rider in a hurry, leaning forward, pizza box held forward in the front hand, handlebar low in the back hand, the backpack bouncing. Frames 1 to 4 he sinks, 5 to 8 he rises; frame 8 flows back into frame 1. Standing tall.",
    "anda": "quick walk forward, an 8-frame loop: fast hurried steps, leaning forward, pizza box forward, backpack bouncing; frame 8 flows back into frame 1.",
    "corre": "running fast like a delivery rider late for a delivery, an 8-frame loop: long fast strides, body leaning far forward, pizza box held forward, handlebar back; frame 8 flows back into frame 1.",
    "soco": "x chain with the handlebar: 1 stance, 2 the handlebar pulls back, 3 a straight thrust with the handlebar forward at chest height, fully extended, 4 it comes back, 5 he spins the handlebar in front of him, 6 a spinning handlebar strike at face height, 7 recovering, 8 stance.",
    "martelo": "overhead strike: 1 stance, 2 and 3 he raises the pizza box over the head, 4 and 5 he smashes the pizza box down and forward at head height, 6 and 7 he straightens, 8 stance.",
    "chute_baixo": "a boot kick to the shin: 1 stance, 2 the front boot lifts, 3 chambers low, 4 and 5 the boot stomps forward at shin height, 6 and 7 back, 8 stance.",
    "chute_alto": "a boot kick then knee: 1 stance, 2 the back knee rises, 3 and 4 a front boot kick at chest height, 5 he steps in, 6 a knee strike at belly height, 7 recovering, 8 stance.",
    "afastar": "Express Delivery headbutt: 1 stance, 2 he lowers the head, 3 and 4 he charges forward, 5 and 6 a headbutt forward with the winged gold helmet at chest height, body leaning, 7 recovering, 8 stance.",
    "agachado": "low crouch. 1 to 4 he squats low, pizza box forward; 5 to 8 he stays squatting, bouncing.",
    "cabecada": "Divine Horn anti-air: 1 deep squat, 2 and 3 he loads, 4 and 5 he springs up thrusting the handlebar straight up above the head like pressing a horn, mouth open shouting, 6 to 8 back to the squat.",
    "rasteira": "a low handlebar sweep: 1 deep squat, 2 and 3 he spins low, 4 and 5 the handlebar sweeps wide along the floor, 6 to 8 back to the squat.",
    "pulo": "a jump. 1 knees bent, 2 pushing off, 3 rising tucked, 4 top with the pizza box raised, 5 tucked, 6 falling with the legs opening, 7 reaching down, 8 landing.",
    "ar_soco": "a gloved punch in mid air: all frames in the air. 1 to 3 the front arm winds up with the pizza box, 4 and 5 it punches down diagonally, 6 to 8 tucked again.",
    "bicicleta": "a flying knee in mid air: all frames in the air. 1 tucked, 2 and 3 he pulls the arms back, 4 and 5 the front knee drives forward at head height, 6 to 8 back to tucked.",
    "defesa": "blocking with the pizza box held in front of the face like a shield: 1 stance, 2 and 3 he raises it, 4 and 5 holding, 6 and 7 pushed back a little, 8 still blocking.",
    "apanha": "getting hit: 1 stance, 2 and 3 the head snaps back, helmet wings shaking, 4 and 5 the torso bends back, pizza box still in the hand, 6 to 8 back to the stance.",
    "queda": "being knocked down, 8 clearly SEPARATED figures: 1 hit, 2 feet leaving the ground, 3 and 4 flying backward, 5 body horizontal, 6 landing on his back, 7 bouncing, 8 lying flat, head on the left. The pizza box stays in the hand.",
    "levanta": "getting up: 1 flat on his back, 2 and 3 he sits up and checks the pizza box, 4 and 5 he springs up, 6 and 7 standing and adjusting the helmet, 8 stance.",
    "rolamento": "Delivery Dash past the opponent: 1 stance, 2 he leans forward like on a motorbike, 3 and 4 he dashes forward very low and fast, 5 and 6 he spins around on one foot, 7 he faces left, 8 he turns back to face right in stance.",
    "agarrao": "grab: 1 stance, 2 the handlebar hook reaches forward and hooks an invisible neck, 3 and 4 he pulls it in, 5 and 6 he slams the pizza box on the invisible head, 7 and 8 stance. No second person is shown.",
    "bola": "Wrong Order throw: 1 stance, 2 he swings the delivery backpack off his back into the free hand, 3 and 4 he winds back, 5 and 6 he throws the backpack forward and it leaves the hand, 7 follow-through, 8 stance with the backpack gone (pizza box still in the front hand).",
    "caneta": "Flying Delivery throw: 1 stance, 2 and 3 he winds the pizza box back, 4 and 5 he throws the pizza box forward flat like a frisbee and it leaves the hand, 6 the hand stays open, 7 a NEW pizza box appears in the hand (a spare), 8 stance.",
    "compasso": "Handlebar Hook: 1 stance, 2 and 3 he winds the handlebar back, 4 and 5 he lunges and extends the handlebar far forward with the hook at neck height, 6 and 7 he pulls back hard as if dragging someone in, 8 stance.",
    "golaco": "super move, Holiday Rush finish: 1 stance, 2 he leaps forward, 3 he lands on the back of an invisible opponent and locks a rear choke, 4 he squeezes, 5 he switches to an arm-lock, 6 he drops sitting with a sweep, 7 he raises the pizza box laughing, 8 stance. No second person is shown.",
    "provoca": "a taunt: 1 stance, 2 and 3 he checks the big gold watch impatiently, 4 to 6 he taps the pizza box and points at the opponent (delivery is late), 7 and 8 he shrugs.",
    "vitoria": "a victory: 1 stance, 2 and 3 he opens the pizza box and takes a slice, 4 to 6 he eats it, 7 and 8 he poses with the slice raised and the box under the arm.",
    "derrota": "defeated: 1 and 2 he drops to sit, 3 to 8 sitting, helmet crooked, the pizza box open and empty on the floor, upset.",
}

FOLHAS_FX = {
    "fx_cabra": "a small white goat with little curved horns and a brown spot, running forward to the right along the ground: frames 1 to 6 a fast gallop cycle, frames 7 and 8 it lowers its head and headbutts forward.",
    "fx_cabra_salto": "a small white goat with little curved horns leaping in a high arc to the right: 1 crouching, 2 to 4 jumping up and forward with the head up and the horns forward, 5 and 6 at the top of the arc, 7 and 8 coming down.",
    "fx_onda_cajado": "a short shockwave along the ground: frame 1 a crack, frames 2 to 6 a low wave of dirt and brown dust rolling forward, frames 7 and 8 it fades.",
    "fx_feno": "a hay bale (straw, yellow-brown) rolling to the right: frames 1 to 8 rotating 45 degrees each, loose straws flying.",
    "fx_pizza": "(use magenta #FF00FF background) a closed square pizza box flying flat and spinning to the right: frames 1 to 6 rotating, frames 7 and 8 it breaks open with slices and cheese bursting.",
    "fx_mochila": "(use magenta #FF00FF background) a square neon-green thermal delivery backpack thrown in an arc: frames 1 to 5 spinning in the air, frames 6 to 8 it bursts open in a cartoon explosion of pizza slices and lunchboxes.",
    "fx_notas": "paper money bills (generic green and yellow banknotes with no text and no faces) lying on the floor and flying up: frames 1 to 3 a few bills land and lie flat, frames 4 to 8 they flutter up and fade.",
    "fx_buzina": "(use magenta #FF00FF background) a cartoon horn blast: concentric neon-green sound rings growing forward and up, frames 1 to 8 growing and fading.",
    "fx_giroflex": "(use magenta #FF00FF background) the awakened aura behind a fighter: a big neon-green rotating beacon light halo (like a police light but green) spinning, with exhaust smoke rising from the floor in flames and a few banknotes flying up; frames loop, frame 8 flows back into frame 1.",
    "fx_moto": "(use magenta #FF00FF background) a ghost motorbike made of neon-green light, side view facing right, speeding forward with light trails: frames 1 to 8 a speed loop.",
}

NOMES = [*CONCEITO.keys()][:1] + list(FOLHAS_GB) + ["e_conceito", "despertar_b"] + \
    ["e_" + n for n in FOLHAS_MOTOBOY] + list(FOLHAS_FX)


def anexos(nome):
    if nome == "conceito":
        return "as 3 fotos do Gbzin (fora do git)"
    if nome == "referencia_ginga":
        return "conceito.png"
    if nome == "e_conceito":
        return "referencia_ginga.png"
    if nome == "e_referencia_ginga":
        return "e_conceito.png + referencia_ginga.png"
    if nome == "despertar_b":
        return "e_referencia_ginga.png + despertar_a.png"
    if nome.startswith("e_"):
        normal = nome[2:]
        return "e_referencia_ginga.png" + (f" + {normal}.png" if normal in FOLHAS_GB else "")
    if nome.startswith("fx_"):
        return "nenhum"
    return "referencia_ginga.png"


def pedido(nome):
    if nome in CONCEITO:
        return CONCEITO[nome]
    if nome in FOLHAS_FX:
        return CABECA_FX + FOLHAS_FX[nome]
    if nome == "despertar_b":
        return CABECA_MOTOBOY + DESPERTAR_B
    if nome.startswith("e_"):
        return CABECA_MOTOBOY + FOLHAS_MOTOBOY[nome[2:]]
    return CABECA + FOLHAS_GB[nome]


def fila_md():
    linhas = ["# Fila de folhas do Gbzin", "",
              "Gerado por `python ferramentas/folhas_gbzin.py --md`. Edite lá, não aqui. Ficha em "
              "[`docs/fichas/gbzin.md`](../fichas/gbzin.md).", "",
              "Cada folha vai salva em `sprites/gbzin/quadros/folhas_arcade/<nome>.png`. **Reanexe a referência em "
              "toda folha** e espere uma terminar antes de pedir a próxima.", "",
              "| # | Folha | Anexar |", "|---|---|---|"]
    linhas += [f"| {i} | `{n}` | {anexos(n)} |" for i, n in enumerate(NOMES, 1)]
    for n in NOMES:
        linhas += ["", f"## `{n}`", "", f"Anexar: {anexos(n)}", "", "```text", pedido(n), "```"]
    return "\n".join(linhas) + "\n"


if __name__ == "__main__":
    if "--md" in sys.argv:
        destino = Path(__file__).resolve().parent.parent / "docs/arcade/fila_gbzin.md"
        destino.write_text(fila_md(), encoding="utf-8", newline="\n")
        print(f"{len(NOMES)} folhas em {destino}")
    else:
        print(pedido(sys.argv[1]) if len(sys.argv) > 1 else "\n".join(NOMES))
