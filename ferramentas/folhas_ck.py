"""Roteiro das folhas do CK, o Boxeador de Rua, para o ChatGPT (ficha em docs/fichas/ck.md).

Estilo arcade anos 90 (docs/biblia-de-arte.md#estilo-arcade-anos-90). Cada folha: 8 quadros em fila, fundo magenta
#FF00FF, salva em sprites/ck/quadros/folhas_arcade/<nome>.png, com a referência anexada: referencia_ginga.png na forma
base, e_referencia_ginga.png no Modo Ratão (folhas e_*). Efeitos (fx_*) vão em fundo verde #00FF00 e sem o lutador.
Os nomes são os espaços do kit no gerador (como no Raiclaven); o golpe é o do CK, não o de outro lutador.
`python ferramentas/folhas_ck.py nome` imprime o pedido completo.
"""
import sys

ESTILO = """Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and feet. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no noise, no texture. Shadows shift hue: skin shadows toward wine red, highlights toward warm cream; white clothes get cool lilac-blue shadows. 1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter on the lit side. Small hard 1-3 pixel highlights. Limited palette look.

Layout: one single row of 8 frames in 8 equal-width cells, wide image, side view, always facing right, same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects unless the motion asks for them.

Consecutive frames differ by a small amount, so the motion looks smooth in sequence.

MOTION: """

CABECA = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached sprite sheet shows the exact character to keep: CK, the cheeky street boxer. Same young Black man, slim athletic build, short black hair, thin mustache and chin goatee, small stud earrings, cocky grin. Same outfit: white Lacoste polo shirt with green collar trim and the small green crocodile on the left chest, black Lacoste cap with the small green crocodile, loose black-and-white wavy-pattern basketball shorts, plain white sneakers, red boxing gloves with white wrist wraps. Same colors and same size as the attached sheet. He fights like a street boxer: slips, weaves, counters, punches, and dirty street kicks.

""" + ESTILO

CABECA_RATAO = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached sprite sheet shows the exact character to keep: CK in RATAO MODE (awakened). Same young Black man and face, short bleached platinum white hair, mirrored wraparound sunglasses pushed up on the head, half-closed reddish stoned eyes, relaxed smirk, a lit hand-rolled joint between the lips with a thin smoke trail, thick gold chain. Patterned navy-and-white short-sleeve shirt worn open over a white tank top, matching patterned board shorts, white socks with dark rubber slides. No gloves: white hand wraps only, and a broken green glass bottle held by the neck in the front hand. Same colors and same size as the attached sheet. He fights loose and dirty like a street brawler dancing at a funk party, slashing with the broken bottle.

""" + ESTILO

CABECA_FX = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

A visual effect for a 1990s arcade fighting game, hand-pixeled, hard-edged flat shading in 2-3 tones, no gradients, no dithering, 1-pixel colored outline. One single row of 8 frames in 8 equal-width cells, wide image. Flat solid pure green background (#00FF00) everywhere. No character, no text, no ground.

MOTION: """

# espaço do kit -> movimento do CK
FOLHAS_CK = {
    "referencia_ginga": "boxer idle bounce loop, the base reference for every other sheet: light on the toes, gloves up at the chin in a peek-a-boo guard, shoulders rolling, small head movement side to side, cocky grin. Frames 1 to 4 he sinks slightly, 5 to 8 he rises; frame 8 flows back into frame 1.",
    "anda": "boxer shuffle walking forward, an 8-frame loop: short quick steps on the balls of the feet, gloves up, shoulders swaying, the shorts swinging; the legs complete a full two-step cycle and frame 8 flows back into frame 1.",
    "soco": "jab then cross. 1 guard, 2 the front glove snaps forward, 3 jab fully extended at face height with the shoulder covering the chin, 4 it returns, 5 the hips turn, 6 straight right cross fully extended with the glove drawn 15% bigger, back heel lifted, 7 recovering, 8 guard.",
    "martelo": "looping overhand right that comes down from above. 1 guard, 2 he dips and loads the back hand, 3 the arm loops up high, 4 and 5 the glove crashes down and forward at head height, torso rolling over, 6 and 7 he rolls back to guard, 8 guard.",
    "chute_baixo": "a dirty street toe kick to the shin. 1 guard, 2 the front sneaker lifts, 3 chambers low, 4 and 5 the sneaker tip pokes forward at shin height, gloves stay up, 6 and 7 back, 8 guard.",
    "chute_alto": "a street front push kick to the belly. 1 guard, 2 and 3 the back knee rises to the chest, 4 and 5 the sole thrusts straight forward at belly height, leaning back, gloves up, 6 and 7 the foot comes down, 8 guard.",
    "afastar": "a two-glove shove followed by a push kick that launches the opponent. 1 guard, 2 and 3 both gloves shove forward at chest height, 4 and 5 the front sole thrusts forward at chest height, 6 and 7 he lands the foot forward, 8 guard.",
    "agachado": "going down into a low boxer crouch. 1 to 4 he bends the knees deep and tucks behind the gloves, head low; 5 to 8 he stays crouched bobbing slightly, eyes up.",
    "baixo_soco": "a low jab to the body from the crouch. 1 deep crouch, 2 and 3 loads the front glove, 4 and 5 jab straight forward at belly height, glove 15% bigger, 6 to 8 back to the crouch.",
    "cabecada": "rising uppercut anti-air from the crouch. 1 deep crouch, 2 and 3 he dips lower and loads, 4 and 5 he explodes upward with a huge uppercut, glove high above his head, rising on the toes, 6 to 8 he settles back down into the crouch.",
    "rasteirinha": "a quick low sneaker tap to the ankle from the crouch. 1 deep crouch, 2 and 3 the front leg slides out, 4 and 5 the sneaker tip stretched just above the floor, 6 to 8 it pulls back.",
    "rasteira": "a street leg sweep from the crouch. 1 deep crouch, 2 and 3 one glove touches the ground and he spins low, 4 and 5 the straight back leg sweeps wide along the floor, 6 to 8 back to the crouch.",
    "pulo": "a jump. 1 knees bent ready, 2 pushing off, 3 rising with the legs tucking, 4 tucked at the top with gloves up, 5 still tucked, 6 falling with the legs opening, 7 reaching down, 8 landing with knees bent.",
    "ar_soco": "a downward punch in mid air. All frames in the air with the knees tucked. 1 to 3 the back glove winds up, 4 and 5 it punches down and forward diagonally, 6 to 8 back to the tucked pose.",
    "bicicleta": "a flying knee in mid air. All frames in the air. 1 tucked, 2 and 3 he pulls the gloves down, 4 and 5 the front knee drives forward at head height, 6 to 8 back to tucked.",
    "defesa": "blocking, high peek-a-boo guard. 1 guard, 2 and 3 he tucks both gloves tight on the face and elbows on the ribs, 4 and 5 he holds the block, 6 and 7 the impact pushes him back a little, 8 still blocking.",
    "apanha": "getting hit in the face. 1 guard, 2 and 3 the head snaps back, cap tilting, mouth open, 4 and 5 the torso bends back with the gloves flung out, 6 to 8 he shakes it off and returns to guard, grin coming back.",
    "queda": "being knocked down. 1 hit and bending back, 2 feet leaving the ground, 3 and 4 flying backward horizontally, 5 and 6 falling onto his back, 7 bouncing on the floor, 8 lying flat on his back.",
    "levanta": "getting up from the floor. 1 flat on his back, 2 and 3 he rolls to the side, 4 and 5 kip-up springing off the shoulders, 6 and 7 landing on his feet and fixing the cap, 8 guard.",
    "rolamento": "the Slip Dodge, going past the opponent: 1 guard, 2 he ducks low under an invisible punch, 3 and 4 he weaves sideways in a deep U motion stepping forward, 5 and 6 he pivots on the front foot turning around, 7 he comes up facing left already in guard, 8 he turns back to face right in guard.",
    "agarrao": "collar grab. 1 guard, 2 the front glove reaches forward and grabs an invisible collar, 3 and 4 he pulls in and hits three short back-hand punches, 5 and 6 he shoves forward with both gloves, 7 and 8 he fixes the cap, grinning. No second person is shown.",
    "bola": "Vape Puff: 1 guard, 2 he pulls a small vape pen from the shorts pocket with the front glove, 3 and 4 he takes a long drag, chest swelling, eyes closed, 5 and 6 he blows a thick white cloud forward at face height, 7 he pockets the vape, 8 guard.",
    "bone_voador": "Flying Cap: 1 guard, 2 he grabs the black cap off his head, 3 and 4 he winds it back sideways like a frisbee, 5 and 6 he flicks it forward spinning flat at chest height and the cap leaves the hand, 7 his hand stays open waiting, bare head, 8 guard without the cap.",
    "compasso": "spinning backfist. 1 guard, 2 and 3 he steps across and spins showing the back, 4 and 5 the back of the glove whips around at head height, fully extended, 6 and 7 he completes the turn, 8 guard.",
    "armada": "Counter stance: 1 guard, 2 and 3 he drops the gloves low and taunts with a smirk, 4 he slips sideways as if dodging, 5 and 6 he fires a hard counter cross fully extended, glove 15% bigger, 7 recovering, 8 guard.",
    "caneta": "the Lunge: 1 guard, 2 and 3 he crouches low and leans forward, 4 and 5 he lunges forward fast and low with a long straight punch, back leg stretched behind, 6 and 7 he pulls back up, 8 guard.",
    "golaco": "a super move, a boxing flurry. 1 guard, 2 he bobs low and grins, 3 to 6 a frenzy in place: jab, hook, uppercut, hook, 7 and 8 a final huge cross and a pose with the glove held out.",
    "provoca": "a taunt. 1 to 3 he taps the gloves together twice, 4 to 6 he drops his guard and waves the opponent in with the front glove, chin up, 7 and 8 he laughs, shoulders bouncing.",
    "vitoria": "a victory. 1 guard, 2 and 3 he fixes the cap with a smirk, 4 to 6 he pulls one glove off with his teeth, 7 and 8 he poses with the bare fist raised, laughing.",
    "lata": "a warm-up. 1 guard, 2 to 5 quick shadowboxing, jab, jab, cross, hook, 6 and 7 he rolls his neck and shoulders, 8 guard.",
    "derrota": "defeated. 1 and 2 he drops to sit on the floor, 3 to 8 sitting with legs out, cap in hand, scratching his head, upset.",
}

FOLHAS_RATAO = {
    "e_referencia_ginga": "idle loop, the reference for every Ratao Mode sheet: loose funk-party sway in place, knees bouncing to the beat, the broken bottle held low in the front hand, the back hand relaxed, the joint smoking. Frames 1 to 4 he sinks, 5 to 8 he rises; frame 8 flows back into frame 1.",
    "despertar_a": "the transformation, part one, still in the BASE FORM outfit of CK with the white Lacoste polo and red gloves: 1 guard, 2 he lowers the guard and nods to an unseen beat, 3 and 4 he does a little dance, shoulders rolling, 5 a hip-swinging ginga step, 6 he tosses the cap backward over his shoulder, 7 his hair starts turning platinum white, 8 he pulls the gloves off.",
    "despertar_b": "the transformation, part two: 1 his clothes swap to the patterned open shirt, tank top, board shorts and slides, sunglasses on the head, 2 he crouches and puts one hand on the ground, 3 he picks up a whole green glass bottle from the floor, 4 he smashes it on the ground with shards flying, 5 he rises holding the broken neck, 6 he lights a joint with the other hand, 7 he takes a drag, 8 he blows smoke and settles into the stance of the attached sheet.",
    "anda": "walking forward, an 8-frame loop: relaxed funk-party swagger, rolling shoulders, slides scuffing, bottle swinging low; frame 8 flows back into frame 1.",
    "soco": "two bottle slashes. 1 stance, 2 the bottle hand cocks back, 3 a horizontal slash at chest height, 4 the backhand slash returning, 5 he steps in, 6 a straight stab with the broken bottle fully extended, 7 recovering, 8 stance.",
    "martelo": "an overhead bottle smash. 1 stance, 2 and 3 the bottle rises high over the head, 4 and 5 he smashes it down and forward at head height, 6 and 7 he straightens, 8 stance.",
    "chute_baixo": "a slide slap kick to the shin. 1 stance, 2 the front foot lifts with the rubber slide, 3 chambers low, 4 and 5 the slide slaps forward at shin height, 6 and 7 back, 8 stance.",
    "chute_alto": "a high funk-dance kick with the slide. 1 stance, 2 and 3 he spins into a dance step, 4 and 5 the leg kicks high at head height, slide almost flying off, 6 and 7 back down, 8 stance.",
    "agachado": "low crouch. 1 to 4 he squats down low like a funk dancer, bottle forward; 5 to 8 he stays squatting, bouncing, smoking.",
    "cabecada": "rising bottle slash anti-air from the crouch. 1 deep squat, 2 and 3 he loads, 4 and 5 he springs up slashing the bottle straight up above the head, 6 to 8 back to the squat.",
    "rasteira": "a funk-dance leg sweep. 1 deep squat, 2 and 3 one hand on the floor, he spins low, 4 and 5 the straight leg sweeps wide along the floor, 6 to 8 back to the squat.",
    "pulo": "a jump. 1 knees bent, 2 pushing off, 3 rising tucked, 4 top with the bottle raised, 5 tucked, 6 falling with the legs opening, 7 reaching down, 8 landing.",
    "ar_soco": "a downward bottle slash in mid air. All frames in the air. 1 to 3 the bottle winds up, 4 and 5 it slashes down diagonally, 6 to 8 tucked again.",
    "defesa": "blocking. 1 stance, 2 and 3 he raises both forearms with the bottle hand crossed in front of the face, 4 and 5 holding, 6 and 7 pushed back a little, 8 still blocking.",
    "apanha": "getting hit. 1 stance, 2 and 3 the head snaps back, sunglasses flying up, the joint still in the mouth, 4 and 5 the torso bends back, 6 to 8 back to the stance.",
    "queda": "being knocked down. 1 hit, 2 feet leaving the ground, 3 and 4 flying backward, 5 and 6 falling on his back, 7 bouncing, 8 lying flat.",
    "levanta": "getting up. 1 flat on his back, 2 and 3 he sits up and takes a drag, 4 and 5 he pushes up with the bottle hand, 6 and 7 standing and adjusting the gold chain, 8 stance.",
    "rolamento": "funk-dance roll behind the opponent: 1 stance, 2 he spins into a low dance step, 3 and 4 he rolls forward on one shoulder, 5 and 6 he springs up turning around, 7 he faces left, 8 he turns back to face right in the stance.",
    "agarrao": "street grab. 1 stance, 2 the free hand grabs an invisible collar, 3 and 4 he blows smoke in the face, 5 and 6 he headbutts and shoves, 7 and 8 he fixes the sunglasses. No second person is shown.",
    "bola": "Flying Bottle: 1 stance, 2 he pulls a new whole green bottle from behind his back with the free hand, 3 and 4 he winds back, 5 and 6 he lobs it forward high in an arc and it leaves the hand, 7 follow-through, 8 stance.",
    "beck": "Joint Drag: 1 stance, 2 he takes the joint from his lips, 3 and 4 he inhales long, chest swelling, eyes rolling up, 5 and 6 he blows a huge thick grey-green cloud forward, 7 the joint back in the mouth, 8 stance.",
    "juliet_voadora": "Flying Sunglasses: 1 stance, 2 he grabs the sunglasses from his head, 3 and 4 winds back sideways, 5 and 6 throws them spinning flat at chest height and they leave the hand, 7 open hand waiting, 8 stance without sunglasses.",
    "caneta": "Ratao Step dash: 1 stance, 2 and 3 he starts a fast funk footwork step, 4 and 5 he dashes forward dancing with a slide kick fully extended, 6 and 7 he spins out of it, 8 stance.",
    "golaco": "a super move, Street Party: 1 stance, 2 he raises the bottle and grins, 3 to 6 a frenzy dancing in place: slash, slide kick, slash, spin, 7 and 8 a final big overhead smash with a second bottle shattering and a pose.",
    "provoca": "a taunt. 1 to 3 he dances a short funk step, 4 to 6 he blows a smoke ring toward the opponent, 7 and 8 he laughs lazily.",
    "vitoria": "a victory. 1 stance, 2 and 3 he lowers the sunglasses over his eyes, 4 to 6 he dances, 7 and 8 he poses with the bottle on the shoulder blowing smoke up.",
    "derrota": "defeated. 1 and 2 he drops to sit, 3 to 8 sitting with legs out, sunglasses crooked, joint gone out, dazed.",
}

FOLHAS_FX = {
    "fx_aura": "Ratao Mode aura that rises from a fighter's feet: thick slow grey-green smoke swirling upward from the ground in a column about as tall as a man, with a few tiny orange ember sparks. Frames loop: the smoke curls rise and fade at the top, frame 8 flows back into frame 1.",
    "fx_fumaca": "a puff of thick vape smoke blown forward: frame 1 a small burst, frames 2 to 5 it grows into a big round white cloud with a soft lilac tint, frames 6 to 8 it lingers and slowly thins.",
    "fx_garrafa": "a thrown green glass bottle spinning in the air, frames 1 to 6 rotating 60 degrees each, frames 7 and 8 it shatters into green glass shards on impact.",
    "fx_paredao": "a big Brazilian street sound system (paredao): a wall of stacked black speaker boxes with chrome rims and small colored lights, frames 1 to 8 the speaker cones pump with the bass and the lights blink. No brand names, no text.",
}


def pedido(nome):
    if nome in FOLHAS_FX:
        return CABECA_FX + FOLHAS_FX[nome]
    if nome in FOLHAS_RATAO:
        return (CABECA if nome == "despertar_a" else CABECA_RATAO) + FOLHAS_RATAO[nome]
    return CABECA + FOLHAS_CK[nome]


if __name__ == "__main__":
    print(pedido(sys.argv[1]) if len(sys.argv) > 1 else "\n".join([*FOLHAS_CK, *FOLHAS_RATAO, *FOLHAS_FX]))
