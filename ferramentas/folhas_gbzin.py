"""Roteiro das folhas do Gbzin, o Pastor do Jiu-Jitsu, para o ChatGPT (ficha em docs/fichas/gbzin.md).

Mesmo molde do folhas_ck.py. Estilo arcade anos 90 (docs/biblia-de-arte.md#estilo-arcade-anos-90). Cada folha: 8
quadros em fila, fundo magenta #FF00FF, salva em sprites/gbzin/quadros/folhas_arcade/<nome>.png, com a referência
anexada: referencia_ginga.png na forma base, e_referencia_ginga.png no Grão-Pastor (folhas e_*). Efeitos (fx_*) vão em
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

PERSONAGEM = """Gbzin, the jiu-jitsu goat shepherd: a young man with light tanned skin (warm golden-tan, not pink), dark-brown WAVY MESSY hair (loose tousled waves, NOT curly, no ringlets) that is thick and voluminous on top with a heavy messy fringe falling over the forehead to near the eyebrows and a short fade on the sides, big round full face with full cheeks, thick dark eyebrows, heavy-lidded calm brown eyes, a thin sparse moustache and a small sparse goatee on the chin only (clean cheeks, no full beard), serious relaxed expression. Big heavy stocky build: wide soft-strong torso, thick arms, thick legs, heavy like a grappler (strong and bulky, not lean, not a bodybuilder with defined abs). Outfit: black sleeveless tank top, white gym shorts with a thin black side stripe, a brown jiu-jitsu belt tied around the waist over the shorts with the two ends hanging, black sneakers, a gold wristwatch on the left wrist. He carries a SHORT wooden shepherd's crook (about as long as his arm, with a curved hook at the top) in the BACK hand."""

CABECA = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached sprite sheet shows the exact character to keep: """ + PERSONAGEM + """ Same face, same colors and same size as the attached sheet. He fights like a jiu-jitsu grappler from the countryside: grabs, pulls, takes down and twists; his kicks push people away; he hooks people with the crook. STAFF RULE: the crook is always in the same hand (the back hand, the arm drawn behind the torso) in all 8 frames unless the motion says otherwise; it never changes hands and never disappears.

""" + ESTILO

# Forma despertada: o Grão-Pastor, roupa "Senhor do Rebanho" (aprovada pelo Breno na issue #30, 2026-11-15).
GRAO_PASTOR = """Gbzin awakened as the GRAND SHEPHERD (Grao-Pastor), the Lord of the Herd, an overwhelmingly powerful dark shepherd warlord: exact same face, same hair, same heavy stocky body and same height as the base form. Nothing of the base outfit remains (no tank top, no white shorts, no sneakers). KEEP from the first awakened sheet: two ENORMOUS goat horns curled in a spiral growing from his forehead; eye glowing solid green with no pupil; a black eyepatch over the LEFT eye with a small glowing green star; a bigger gold wristwatch on the left wrist; a RED jiu-jitsu belt (the grand master's belt) tied at the waist over the pants, burning with GREEN flames at its two hanging ends; in the BACK hand a short shepherd's crook made of BONE with a curved hook and a small green flame at the tip. NEW OUTFIT: a CHEST PLATE MADE OF A GOAT SKULL, yellowed cracked bone, covering the chest, with the skull's eye sockets glowing green; SHOULDER GUARDS made of curved goat horns on both shoulders; BONE BRACERS on both forearms; two iron CHAINS crossed over the chest, fastened to the skull; bare muscular arms and bare belly sides; ripped BLACK LEATHER PANTS with green embers glowing inside the rips; GOAT HOOVES instead of feet, black and cracked, with green ember light in the cracks; a CAPE OF BLACK FUR with a tall thick fur collar around the neck, its hem in tatters. The skull chest plate and the hooves must read clearly in the side view. No motorcycle items of any kind. No text, no logos."""

CABECA_GP = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached sprite sheet shows the exact character to keep: """ + GRAO_PASTOR + """ Same face, same colors and same size as the attached sheet. He is the final boss version of the jiu-jitsu shepherd: slow, heavy and overwhelming, every move must look far too powerful; he grabs, lifts and slams. CROOK RULE: the bone crook is always in the same hand (the back hand, the arm drawn behind the torso) in all 8 frames unless the motion says otherwise; it never changes hands and never disappears. The goat-skull chest plate and the hooves stay visible in every frame; the fur cape follows the motion and never hides the chest plate. Do NOT draw the aura, the goat shadow or the giant green hands: they are separate effects.

""" + ESTILO

CABECA_FX = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

A visual effect for a 1990s arcade fighting game, hand-pixeled, hard-edged flat shading in 2-3 tones, no gradients, no dithering, 1-pixel colored outline. One single row of 8 frames in 8 equal-width cells, wide image. Flat solid pure green background (#00FF00) everywhere (if the effect itself is green, use magenta #FF00FF instead). No fighter, no text, no ground.

MOTION: """

# os dois primeiros pedidos: das fotos ao modelo do personagem
CONCEITO = {
    "conceito": """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached photos show the real young man this character is based on. LIKENESS IS THE PRIORITY: anyone who knows him must recognize him at once. Copy from the photos, as faithfully as pixel art allows: the shape of his face (round, full cheeks), his hair (cut, volume, wave, fringe and fade), his eyebrows and eyes, his thin moustache and small goatee, his skin tone and his real body shape and proportions (big, heavy and stocky, as in the full-body photos; do not slim him down and do not turn him into a lean muscular hero). Only the art style (1990s arcade fighting game pixel art) and the outfit below are invented. Character: """ + PERSONAGEM + """

Sheet layout, flat solid magenta background (#FF00FF), no text: 1) full body front view, standing, 2) full body side view facing right in a low grappler stance, crook in the back hand, 3) full body back view, 4) a big bust portrait of the face. Same scale for the three full bodies.

""" + ESTILO.split("Layout:")[0],
    "e_conceito": """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The first attached sheet shows Gbzin in his base form and the second one his first awakened design. Create the NEW concept sheet of his awakened form in the same art style, keeping the exact same face, hair, body and height, with a much more powerful outfit: """ + GRAO_PASTOR + """

Sheet layout, flat solid magenta background (#FF00FF), no text: 1) full body front view, standing, bone crook in the back hand, 2) full body side view facing right in his low grappler fighting stance (the goat-skull chest plate and the hooves clearly visible in profile), 3) full body back view showing the black fur cape, 4) a big bust portrait of the face with the spiral goat horns, the glowing green eye, the green-star eyepatch and the tall fur collar. Same scale for the three full bodies. No aura, no giant shadow and no giant hands drawn (the aura is a separate effect); only the green flames on the belt ends and crook tip and the green embers of the outfit.

""" + ESTILO.split("Layout:")[0],
}

# espaço do kit -> movimento do Gbzin (forma base). Agarrões com folha própria e cada pancada com preparo e contato
# (receita, seção 4); quem é agarrado tem as folhas vitima_* (para qualquer um agarrar o Gbzin).
FOLHAS_GB = {
    "referencia_ginga": "grappler idle loop, the base reference for every other sheet: wide low stance, knees bent, both open hands forward ready to grab, the crook held low in the back hand, calm half-smile, slow heavy breathing. Frames 1 to 4 he sinks slightly, 5 to 8 he rises; frame 8 flows back into frame 1. Standing tall, the figure fills the cell height as described below.",
    "anda": "slow heavy walk forward, an 8-frame loop: short solid steps, hands forward ready to grab, crook in the back hand, belt ends swinging; the legs complete a full two-step cycle and frame 8 flows back into frame 1. Standing tall.",
    "soco": "x chain, open-hand slap then short elbow: 1 stance, 2 the front open hand pulls back, 3 a big open-hand slap forward at face height, arm fully extended, 4 it returns, 5 he steps in, 6 a short front elbow strike forward at face height, 7 recovering, 8 stance. Standing tall.",
    "martelo": "y chain, the crook strikes: 1 stance, 2 the crook rises over the back shoulder, 3 and 4 a straight thrust with the crook forward at chest height, arm fully extended, 5 he spins the crook in a circle in front of him, 6 and 7 an overhead chop with the crook coming down at head height, 8 stance.",
    "chute_baixo": "a low front kick to the shin: 1 stance, 2 the front sneaker lifts, 3 chambers low, 4 and 5 the sole thrusts forward at shin height, hands stay forward, 6 and 7 back, 8 stance.",
    "chute_alto": "a front push kick to the chest: 1 stance, 2 and 3 the back knee rises to the chest, 4 and 5 the sole thrusts straight forward at chest height, leaning back, 6 and 7 the foot comes down, 8 stance.",
    "afastar": "a double-leg mule kick that launches the opponent (Coice): 1 stance, 2 he crouches and puts both hands on the ground, 3 and 4 both legs fire forward together at belly height like a goat kick, body almost horizontal, 5 holding, 6 and 7 he rolls back up, 8 stance.",
    "agachado": "going down into a low wrestler crouch: he only bends the knees and lowers the hips, the body keeps exactly the same size. 1 to 4 he bends the knees deep, hands forward ready to grab, crook low; 5 to 8 he stays crouched rocking slightly, eyes up.",
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
    "rolamento": "Penguin Step that passes behind the opponent: 1 stance, 2 he starts the penguin waddle with arms stiffly open to the sides and the feet turned out, 3 and 4 he waddles forward fast with tiny steps, body rocking, face proud and serious, 5 and 6 he spins around on one foot, 7 he faces left already in stance, 8 he turns back to face right in stance.",
    "agarrao": "the standing grab Bye Bye Kid (bear hug), always facing right, each blow with a wind-up and a clear contact: 1 both arms reach forward and wrap around an invisible opponent at chest height (the grab), 2 he squeezes and lifts, leaning back, 3 wind-up: he shakes to the left, 4 contact: a hard squeeze-shake to the right, 5 wind-up again, 6 contact: a second shake, stronger, 7 he arches far back throwing the invisible opponent over and behind him (the throw, a clear backward direction), 8 he stands up and dusts off his hands. No second person is shown.",
    "bola": "Loose Goat throw pose (the goat itself is a separate effect): 1 stance, 2 he whistles with two fingers in the mouth, 3 and 4 he points forward with the crook commanding, 5 and 6 he swings the crook forward low like herding, 7 he laughs, 8 stance. Nothing comes out of the crook.",
    "compasso": "Crook Hook (Gancho do Pastor): 1 stance, 2 and 3 he winds the crook back, 4 and 5 he lunges and extends the crook far forward at neck height with the hook at the tip, arm and crook fully extended, 6 and 7 he pulls the crook back toward himself strongly as if dragging someone in, 8 he catches with the front arm open. Standing tall.",
    "armada": "Closed Guard counter: 1 stance, 2 and 3 he drops on his back on the floor, legs up in a jiu-jitsu guard, 4 waiting with the legs raised, 5 and 6 the legs close and twist as if trapping an attack, 7 he scissors and sweeps, 8 he springs back up into stance.",
    "caneta": "Flying Arm-lock: 1 stance, 2 he crouches, 3 and 4 he jumps forward and up, arms reaching to grab, 5 and 6 in the air his legs wrap and his body twists sideways as if catching an arm, 7 and 8 he falls to the ground sitting in an arm-lock position, legs crossed, arms pulling.",
    "golaco": "a super move, Countryside Choke: 1 stance, 2 he waddles forward penguin style, 3 he jumps on the back of an invisible opponent and locks a rear choke, 4 he squeezes, 5 he switches to an arm-lock, 6 he drops sitting with a sweep, 7 he taps the floor three times laughing, 8 he stands in stance. No second person is shown.",
    "provoca": "a taunt: 1 stance, 2 and 3 he leans on the crook like a calm shepherd, 4 to 6 he waves the opponent in with the front hand, calm smile, 7 and 8 he checks the gold wristwatch with a shrug.",
    "vitoria": "a victory: 1 stance, 2 and 3 he ties the brown belt tighter, 4 to 6 he raises the crook overhead proudly, 7 and 8 he poses with the crook on the shoulder, smiling.",
    "lata": "an intro warm-up: 1 stance, 2 and 3 he stretches the neck side to side, 4 and 5 he slaps his own shoulders, 6 he spins the crook once, 7 he points at the opponent, 8 stance.",
    "derrota": "defeated: 1 and 2 he drops to sit on the floor, 3 to 8 sitting with legs out, crook across the lap, scratching his head, upset.",
    # parry próprio (docs/parry.md): quadros 1-3 a postura, 4-8 o acertou, que na base é a piada
    "parry_alto": "PARRY HIGH, funny: 1 to 3 he holds the crook up in front of him with the hook open at face height, waiting, eyes half closed; 4 the hook catches an invisible fist at face height, 5 he yawns while holding it, 6 and 7 with the front hand he gives two calm pats on the invisible opponent's head like calming a goat, 8 he lets go and smiles.",
    "parry_baixo": "PARRY LOW, funny: 1 to 3 he crouches low with the knees bent and the hands down, watching the floor; 4 he does a jiu-jitsu backward shoulder roll over an invisible sweep, 5 he is upside down mid roll, 6 he lands back on his feet, 7 he checks the gold wristwatch with a bored face, 8 he taps the watch as if to say the opponent is late.",
    # reações de quem é agarrado (servem para qualquer lutador agarrar o Gbzin)
    "vitima_agarrado": "being grabbed and thrown by an unseen opponent, no other character drawn: 1 standing hit, torso doubled forward, 2 lifted with feet off the ground, arms flailing, 3 tilted backward 45 degrees in the air, 4 upside down, head toward the ground, legs up, 5 horizontal face up in the air, 6 horizontal face down in the air, 7 curled and spinning, knees to chest, 8 stretched out face down just above the ground; the belt ends always follow the motion and the crook stays in the hand.",
    "vitima_arremessado": "thrown victim hitting the floor: 1 falling head first at 45 degrees, 2 shoulder hits the floor, 3 back slams flat, legs up, 4 bounce with the whole body off the ground, 5 face down flat, 6 seated on the floor dazed, legs out, hands behind, 7 lying on the side, 8 lying flat face up. The crook stays in the hand.",
    # transformação, parte 1, ainda na roupa da base: bate o cajado três vezes no chão (ficha, Despertar)
    "despertar_a": "the transformation, part one, still in the BASE FORM outfit, he strikes the ground three times with the crook: 1 stance, 2 he raises the crook with both hands, 3 first strike: the crook tip slams into the ground in front of him, 4 he raises it again, angrier, 5 second strike, harder, crouching lower, 6 he raises the crook high over his head with both hands, shouting, 7 third strike with the whole body, down on one knee, 8 head down, a bright green light floods him from behind, only the dark silhouette shows. Do not draw cracks or money (separate effects).",
    # folhas próprias do Gbzin (fora do kit do Pengaró)
    "cajado_chao": "Staff Strike on the ground: 1 stance, 2 and 3 he raises the crook high with both hands, 4 and 5 he slams the crook tip into the ground in front of him, crouching, 6 and 7 he pulls it out, 8 stance.",
    "rolo_feno": "Hay Bale Roll: 1 stance, 2 he tucks into a ball, 3 to 6 he rolls forward along the ground curled up like a hay bale (each frame rotated about 90 degrees more), 7 he unrolls, 8 he stands in stance.",
    "montada": "the Mount (crouch grab), always facing right, each punch with a wind-up and a clear contact: 1 low crouch, he dives forward low and grabs (the grab), 2 he sits on top of an invisible opponent lying on the floor (mount position, knees on the floor), 3 wind-up: the front fist rises high, 4 contact: a big punch down to the floor level, 5 wind-up with the other fist, 6 contact: a second punch down, 7 a third big punch down with both fists together, 8 he gets up into stance. No second person is shown.",
    "ordenha": "Goat Milking (command grab), always facing right, each blow with a wind-up and a clear contact: 1 both hands grab forward at chest height (the grab), 2 and 3 he spins around in place holding an invisible opponent, crook under the arm, 4 a full turn back to facing right, 5 wind-up: the crook swings far back over the back shoulder, 6 contact: he swings the crook forward hard at belly height, 7 follow-through sending the opponent far forward (the throw, a clear forward direction), 8 stance. No second person is shown.",
}

# a transformação, parte 2: já de Grão-Pastor (anexe a e_referencia_ginga e a despertar_a)
DESPERTAR_B = "the transformation, part two, already transformed: 1 down on one knee, a bright green light still covering most of the body, 2 the light thins and reveals the Grand Shepherd kneeling, the spiral horns growing, 3 he starts to rise slowly, the bone crook still planted in the ground, 4 he stands, the fur cape billowing, 5 he lifts his head and the eye glows green, 6 he pulls the bone crook out of the ground, 7 he spreads his arms like a lord of the herd, 8 he settles into the stance of the attached sheet with a cold grin."

# folhas e_<nome> do Grão-Pastor. Como a forma dura até o fim da luta, todo espaço do kit tem a sua (nada da roupa da
# base aparece). Anexe a e_referencia_ginga e a folha normal do mesmo golpe. Exclusivos aprovados pelo Breno na #30.
FOLHAS_GP = {
    "referencia_ginga": "idle loop, the reference for every Grand Shepherd sheet: a wide heavy boss stance, chest forward showing the goat skull, the front open hand forward ready to grab, the bone crook held low in the back hand, the cape moving slightly. Frames 1 to 4 he sinks with a heavy breath, 5 to 8 he rises; frame 8 flows back into frame 1. Standing tall, the figure fills the cell height as described below.",
    "anda": "slow heavy walk forward of a boss, an 8-frame loop: each hoof lands heavily, the front hand open forward, the bone crook in the back hand, the cape and the belt flames swinging; the legs complete a full two-step cycle and frame 8 flows back into frame 1.",
    "soco": "x chain with the bone crook: 1 stance, 2 the crook pulls back, 3 a straight thrust with the bone crook forward at chest height, fully extended, 4 it comes back, 5 he spins the crook in a full circle in front of him, 6 a spinning crook strike at face height, 7 recovering, 8 stance.",
    "martelo": "overhead bone crook smash: 1 stance, 2 and 3 he raises the bone crook high over his head with both hands, 4 and 5 he smashes it down and forward at head height, body bending forward, 6 and 7 he straightens, 8 stance.",
    "chute_baixo": "a hoof stomp kick to the shin: 1 stance, 2 the front hoof lifts, 3 chambers low, 4 and 5 the hoof sole stomps forward at shin height, 6 and 7 back, 8 stance.",
    "chute_alto": "b chain, front kick then knee: 1 stance, 2 the back knee rises, 3 and 4 a front hoof kick at chest height, 5 he steps in, 6 a knee strike at belly height, 7 recovering, 8 stance.",
    "tosquia": "the Shearing finisher: 1 stance, 2 and 3 he opens both arms wide to the sides, 4 and 5 he claps both hands together hard in front of him at chest height, 6 he holds the clap, 7 he opens the hands, 8 stance. (The giant green hands that copy the clap are a separate effect.)",
    "estouro": "the Stampede horn charge, an 8-frame loop for a charge across the screen: he runs forward heavily with the head lowered and the spiral horns pointing forward like a ram, the bone crook held back, the cape flying behind, hooves pounding; frame 8 flows back into frame 1.",
    "agachado": "going down into a low crouch: he only bends the knees and lowers the hips, the body keeps exactly the same size. 1 to 4 he crouches low like a beast ready to charge, horns forward; 5 to 8 he stays crouched breathing, eye up.",
    "baixo_soco": "a low bone crook sweep from the crouch: 1 deep crouch, 2 and 3 he loads the crook back, 4 and 5 the crook sweeps forward along the floor at ankle height, 6 to 8 back to the crouch.",
    "cabecada": "rising horn butt anti-air from the crouch: 1 deep crouch, 2 and 3 he dips lower, 4 and 5 he springs up driving the spiral horns straight up above him, 6 to 8 he settles back into the crouch.",
    "rasteira": "a low sweep: 1 stance, 2 he drops low, 3 one hand on the floor, 4 and 5 the front leg and hoof sweep wide along the floor, fully extended, 6 and 7 he rises, 8 stance.",
    "pulo": "a heavy jump. 1 knees bent, 2 pushing off with the hooves, 3 rising tucked, the cape flying, 4 top, crook raised, 5 tucked, 6 falling with the legs opening, 7 reaching down with the hooves, 8 landing very heavily, knees bent.",
    "ar_soco": "a bone crook smash in mid air: all frames in the air. 1 to 3 the crook winds up over the head, 4 and 5 it smashes down and forward diagonally, 6 to 8 back to the tucked pose.",
    "bicicleta": "a flying knee in mid air: all frames in the air. 1 tucked, 2 and 3 he pulls the arms back, 4 and 5 the front knee drives forward at head height, 6 to 8 back to tucked.",
    "defesa": "blocking: 1 stance, 2 and 3 he crosses the bone bracers in front of the face, 4 and 5 holding, 6 and 7 pushed back a little, hooves sliding, 8 still blocking.",
    "apanha": "getting hit: 1 stance, 2 and 3 the head snaps back, horns tilting, 4 and 5 the torso bends back, crook still in the back hand, 6 to 8 he straightens, angry, back to the stance.",
    "queda": "being knocked down, 8 clearly SEPARATED figures: 1 hit, 2 hooves leaving the ground, 3 and 4 flying backward, 5 body horizontal, 6 landing on his back on the cape, 7 bouncing, 8 lying flat, head on the left. The crook stays in the hand.",
    "levanta": "getting up: 1 flat on his back, 2 and 3 he rolls to the side, 4 and 5 he pushes up with the crook planted, 6 and 7 standing and throwing the cape back, 8 stance.",
    "rolamento": "a heavy dash that passes behind the opponent: 1 stance, 2 he lowers the horns, 3 and 4 he dashes forward low and fast, the cape flying, 5 and 6 he spins around on one hoof, 7 he faces left in stance, 8 he turns back to face right in stance.",
    "agarrao": "the awakened standing grab, always facing right, each blow with a wind-up and a clear contact, huge and brutal: 1 the front hand grabs an invisible opponent by the throat at head height (the grab), 2 he lifts him high off the ground with one arm, 3 wind-up: the crook rises behind, 4 contact: a crook blow at chest height, 5 wind-up again, 6 contact: a horn butt at face height, 7 he slams the invisible opponent down to the floor in front of him (the throw, straight down), 8 he stands over him, stance. No second person is shown.",
    "montada": "the awakened crouch grab, always facing right, each blow with a wind-up and a clear contact: 1 he dives low and pins an invisible opponent to the floor with one hoof (the grab), 2 he stands on him, 3 wind-up: he raises the bone crook high, 4 contact: the crook smashes down to floor level, 5 wind-up again, 6 contact: a second smash, 7 he stomps the hoof down hard, 8 stance. No second person is shown.",
    "ordenha": "the awakened command grab, always facing right, each blow with a wind-up and a clear contact: 1 both hands grab forward at chest height (the grab), 2 and 3 he spins around in place holding an invisible opponent, the cape swirling, 4 a full turn back to facing right, 5 wind-up: the bone crook swings far back, 6 contact: a huge crook swing at belly height, 7 follow-through sending the opponent far forward (the throw, a clear forward direction), 8 stance. No second person is shown.",
    "bola": "Ghost Goat throw pose (the burning goat is a separate effect): 1 stance, 2 he raises the bone crook, 3 and 4 he points the crook forward commanding, 5 and 6 he sweeps the crook forward low like herding, 7 he laughs coldly, 8 stance. Nothing comes out of the crook.",
    "compasso": "Shepherd's Pull (the giant hands that pull are a separate effect): 1 stance, 2 and 3 he reaches both open hands far forward, 4 and 5 he closes both fists as if catching something far away, 6 and 7 he pulls both fists back to his chest strongly, leaning back, 8 stance.",
    "mao_pastor": "Shepherd's Hand projectile pose (the flying giant green hand is a separate effect): 1 stance, 2 and 3 he pulls the front open hand back to the shoulder, 4 and 5 he thrusts the open palm straight forward at chest height, arm fully extended, 6 holding, 7 recovering, 8 stance.",
    "berro": "the Goat Scream anti-air (the scream rings are a separate effect): 1 stance, 2 he leans back and fills the chest, 3 and 4 he throws the head up and screams to the sky with the mouth wide open, horns up, arms spread down and back, 5 and 6 holding the scream, 7 he lowers the head, 8 stance.",
    "armada": "awakened guard counter: 1 stance, 2 and 3 he drops on his back on the cape, hooves up in a jiu-jitsu guard, 4 waiting, 5 and 6 the legs close and twist as if trapping an attack, 7 he sweeps with the hooves, 8 he springs up into stance.",
    "caneta": "awakened Flying Arm-lock: 1 stance, 2 he crouches, 3 and 4 he jumps forward and up, arms reaching, the cape flying, 5 and 6 in the air his legs wrap and his body twists sideways catching an arm, 7 and 8 he falls to the ground sitting in an arm-lock, arms pulling.",
    "cajado_chao": "awakened Staff Strike: 1 stance, 2 and 3 he raises the bone crook high with both hands, 4 and 5 he slams the crook tip into the ground in front of him, crouching, 6 and 7 he pulls it out, 8 stance.",
    "rolo_feno": "awakened roll: 1 stance, 2 he tucks into a ball wrapped in the fur cape, horns out, 3 to 6 he rolls forward along the ground (each frame rotated about 90 degrees more), 7 he unrolls, 8 he stands in stance.",
    "golaco": "super move Herd Stampede pose: 1 stance, 2 and 3 he raises the bone crook high over his head, 4 and 5 he slams the crook down and points forward commanding the herd, 6 and 7 he holds the pose, the cape blown back, 8 stance.",
    "juizo": "super move Judgment of the Herd: 1 stance, 2 he leaps forward, 3 he lands behind an invisible opponent and locks a rear choke, 4 he squeezes, lifting the opponent, 5 he squeezes harder, horns lowered, 6 he drops sitting with the choke locked, 7 he hits the floor three times with the bone crook, 8 he stands in stance. No second person is shown.",
    "provoca": "a taunt: 1 stance, 2 and 3 he checks the big gold watch, 4 to 6 he waves the opponent in with two fingers, 7 and 8 he strokes one of his horns, smiling coldly.",
    "vitoria": "a victory: 1 stance, 2 and 3 he raises the bone crook over his head, 4 to 6 he plants it in the ground and opens the arms like a lord, 7 and 8 he crosses the arms on the skull chest plate, the cape flowing.",
    "derrota": "defeated: 1 and 2 he drops to one knee, 3 to 8 kneeling, leaning on the bone crook, head down, the horns heavy, panting.",
    "parry_alto": "PARRY HIGH, too powerful: 1 to 3 he waits with the front open hand raised at face height, not even looking; 4 the hand catches an invisible fist at face height and holds it still, 5 he slowly turns his glowing eye to the opponent, 6 and 7 he squeezes and twists the invisible fist down, 8 he lets go and strokes one horn.",
    "parry_baixo": "PARRY LOW, too powerful: 1 to 3 he plants both hooves wide and lowers the horns toward the floor; 4 an invisible sweep hits his hooves and he does not move at all, 5 he traps the invisible leg between the two spiral horns, 6 and 7 he shakes the head and tosses it to the side, 8 he throws the cape back, stance.",
    "vitima_agarrado": "being grabbed and thrown by an unseen opponent, no other character drawn: 1 standing hit, torso doubled forward, 2 lifted with the hooves off the ground, arms flailing, 3 tilted backward 45 degrees in the air, 4 upside down, horns toward the ground, 5 horizontal face up in the air, 6 horizontal face down in the air, 7 curled and spinning, knees to chest, 8 stretched out face down just above the ground; the cape and the belt flames follow the motion and the crook stays in the hand.",
    "vitima_arremessado": "thrown victim hitting the floor: 1 falling head first at 45 degrees, 2 shoulder hits the floor, 3 back slams flat on the cape, hooves up, 4 bounce with the whole body off the ground, 5 face down flat, 6 seated on the floor dazed, legs out, hands behind, 7 lying on the side, 8 lying flat face up. The crook stays in the hand.",
}

# Objetos que viram projétil (o resto dos efeitos sai do pixelfx e do Blender: receita, seção 7)
FOLHAS_FX = {
    "fx_cabra": "a small white goat with little curved horns and a brown spot, running forward to the right along the ground: frames 1 to 6 a fast gallop cycle, frames 7 and 8 it lowers its head and headbutts forward.",
    "fx_cabra_salto": "a small white goat with little curved horns leaping in a high arc to the right: 1 crouching, 2 to 4 jumping up and forward with the head up and the horns forward, 5 and 6 at the top of the arc, 7 and 8 coming down.",
    "fx_feno": "a hay bale (straw, yellow-brown) rolling to the right: frames 1 to 8 rotating 45 degrees each, loose straws flying.",
    "fx_cabra_fantasma": "(use magenta #FF00FF background) a GHOST GOAT made of green flames (dark green body, bright green fire, glowing eyes, big curved horns) running forward to the right along the ground: frames 1 to 6 a fast gallop cycle with the flames trailing back, frames 7 and 8 it lowers its head and headbutts forward.",
    "fx_cabra_fantasma_salto": "(use magenta #FF00FF background) a GHOST GOAT made of green flames (glowing eyes, big curved horns) leaping in a high arc to the right: 1 crouching, 2 to 4 jumping up and forward with the horns forward, 5 and 6 at the top of the arc, 7 and 8 coming down, flames trailing.",
    "fx_mao": "(use magenta #FF00FF background) a GIANT open hand made of translucent green energy (bright green edges, darker green inside, no arm, flame wisps at the wrist) flying straight to the right, palm forward: frames 1 and 2 it forms, frames 3 to 6 flying with the fingers spread, frames 7 and 8 it closes into a fist.",
    "fx_notas": "paper money bills (generic green and yellow banknotes with no text and no faces) lying on the floor and flying up: frames 1 to 3 a few bills land and lie flat, frames 4 to 8 they flutter up and fade.",
}

# ordem da fila: base, transformação, Grão-Pastor, objetos
NOMES = [*CONCEITO.keys()][:1] + list(FOLHAS_GB) + ["e_conceito", "despertar_b"] + \
    ["e_" + n for n in FOLHAS_GP] + list(FOLHAS_FX)


def anexos(nome):
    if nome == "conceito":
        return "as 6 fotos do Gbzin (branch gbzin-fotos, fora da mugen)"
    if nome == "referencia_ginga":
        return "conceito_v3.png"
    if nome == "e_conceito":
        return "conceito_v3.png + e_conceito_v1.png"
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


# Receita, seção 3: boneco grande na folha (~545 px como o CK), para o 3x sair nítido direto da folha.
TAMANHO = "\n\nSIZE: the image is 2172x724 pixels, 8 cells of 271 pixels each. Draw the figure BIG, at exactly the same pixel size as the attached sheet: standing, about 545 pixels from the soles to the top of the hair, soles at about y=655. Head, torso and limbs keep the same proportions in every frame. Every frame sits in its own column with at least 20 pixels of empty magenta between neighbours; when a pose is wide (kicks, lying down, rolls) bend the knees or lean so it fits in its cell without shrinking the body. Do NOT draw motion lines, speed lines, impact flashes, dust or any other effect: only the character and what he holds."
TAMANHO_REF = TAMANHO.replace("at exactly the same pixel size as the attached sheet: ", "")
TAMANHO_GP = TAMANHO.replace("top of the hair", "top of the hair (the horns go above that)")


def pedido(nome):
    if nome in CONCEITO:
        return CONCEITO[nome]
    if nome in FOLHAS_FX:
        return CABECA_FX + FOLHAS_FX[nome]
    if nome == "referencia_ginga":
        return CABECA + FOLHAS_GB[nome] + TAMANHO_REF
    if nome == "despertar_b":
        return CABECA_GP + DESPERTAR_B + TAMANHO_GP
    if nome.startswith("e_"):
        return CABECA_GP + FOLHAS_GP[nome[2:]] + TAMANHO_GP
    return CABECA + FOLHAS_GB[nome] + TAMANHO


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
