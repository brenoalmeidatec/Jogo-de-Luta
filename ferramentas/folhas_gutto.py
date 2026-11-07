"""Roteiro das folhas do Gutto (Muay Thai) para o ChatGPT. Mesmo formato do FOLHAS_PENGARO de gerar_folhas.py.

Cada folha: 8 quadros em fila, fundo magenta #FF00FF. O fluxo (navegador embutido, chat "Gutto") está em
docs/como-trabalhar.md. Este arquivo só guarda os textos; `python ferramentas/folhas_gutto.py nome` imprime o pedido
completo de uma folha para colar no chat, com a referência anexada.
"""
import sys

# aparência fixa: vem da folha-referência (sprites/gutto/quadros/folhas/referencia_idle.png, v3)
CABECA = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached sprite sheet shows the exact character and art style to keep: same man (Gutto), same face with thick mustache and light stubble, same short curly black hair, same deep dark brown skin, same strong muscular build, SHIRTLESS, black satin Muay Thai trunks with a wide white waistband and a white stripe down each side, white hand wraps, twisted white-and-black rope armbands (prajioud) on both biceps, barefoot. Same detailed 90s arcade pixel art. He is a Muay Thai fighter.

Style is a hand-drawn 16-bit SNES / 90s arcade sprite, clean dark outline, flat cel shading, never a 3D render.

Layout: one single row of 8 frames in 8 equal-width cells, wide image, side view, always facing right, same scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, with no shadow, no ground, no text, no numbers, no borders and no effects.

Consecutive frames differ by a small amount, so the motion looks smooth when played in sequence.

Animation: """

# nome: (âncora para o recorte, descrição do movimento)
FOLHAS_GUTTO = {
    "ginga": ("cabeca", "the Muay Thai ready-stance idle loop (já existe: referencia_idle.png, copiada como ginga.png)."),
    "anda": ("cabeca", "walking forward in the Muay Thai stance, an 8-frame loop. Guard stays up with both fists near the chin, he advances with small bouncy shuffle steps on the balls of his feet, knees slightly bent, front foot sliding forward then the back foot following, the torso bobbing a little. The legs complete a full two-step cycle and frame 8 flows back into frame 1."),
    "soco": ("pes", "a fast jab then a cross. Frame 1 Muay Thai guard, frame 2 the front shoulder loads, frame 3 the jab shoots straight forward at chin height, frame 4 the jab snaps back, frame 5 the hips and back shoulder rotate, frame 6 the cross is fully extended at chin height with the back heel lifted, frame 7 the arm returns, frame 8 guard."),
    "martelo": ("pes", "a horizontal elbow strike (sok tat). Frame 1 guard, frame 2 torso twists back, frame 3 the elbow rises to shoulder height with the fist near the ear, frames 4 and 5 the torso whips forward with the elbow leading at chin height, frames 6 and 7 he recovers, frame 8 guard."),
    "chute_baixo": ("pes", "a Muay Thai low kick to the thigh. Frame 1 guard, frame 2 he pivots on the front foot, frame 3 the back leg swings out low, frames 4 and 5 the shin whips through at thigh height with the hips turned over, frames 6 and 7 the leg comes back, frame 8 guard."),
    "chute_alto": ("pes", "a high Muay Thai roundhouse kick with the shin to the head. Frame 1 guard, frame 2 he pivots hard on the front foot, frame 3 the back leg swings up from the outside, frames 4 and 5 the shin whips across at head height with the standing leg fully pivoted and the arms balancing, frames 6 and 7 the leg comes down, frame 8 guard."),
    "afastar": ("pes", "a teep, the Muay Thai push kick that launches the opponent. Frame 1 guard, frames 2 and 3 the knee chambers high against the chest, frames 4 and 5 the foot thrusts straight forward at chest height with the torso leaning back, frames 6 and 7 the foot lands forward, frame 8 guard."),
    "agachado": ("pes", "going down into a low crouch with the guard up. Frames 1 to 4 he sinks from the Muay Thai guard into a deep crouch with both fists protecting the face and one knee almost touching the ground. Frames 5 to 8 he stays in the crouch, breathing with small movements."),
    "baixo_soco": ("pes", "a low jab from the crouch. Frame 1 deep crouch with guard up, frames 2 and 3 the shoulder loads, frames 4 and 5 the front fist punches straight forward at waist height, frames 6 to 8 back to the crouch."),
    "cabecada": ("pes", "a rising knee strike (khao) from the crouch, used as an anti-air. Frame 1 deep crouch, frames 2 and 3 the legs push up and the hands grab forward, frames 4 and 5 the whole body drives upward with the knee leading and fully driven up, frames 6 to 8 he lands back in the crouch."),
    "rasteirinha": ("pes", "a quick low shin kick from the crouch. Frame 1 deep crouch, frames 2 and 3 the leg slides out, frames 4 and 5 the shin is fully stretched just above the floor, frames 6 to 8 the leg pulls back."),
    "rasteira": ("pes", "a full low sweeping kick. Frame 1 deep crouch with both hands near the ground, frames 2 and 3 the body pivots low, frames 4 and 5 the straight leg sweeps wide along the floor, frames 6 to 8 he gathers back into the crouch."),
    "pulo": ("pes", "a jump. Frame 1 knees bent ready to jump, frame 2 pushing off the ground, frame 3 rising with legs starting to tuck, frame 4 tucked at the top with the fists up, frame 5 still tucked, frame 6 falling with legs opening, frame 7 reaching for the ground, frame 8 landing with knees bent."),
    "ar_soco": ("pes", "a downward elbow in mid air. All frames are in the air with knees tucked. Frames 1 to 3 the elbow winds up, frames 4 and 5 the elbow strikes down and forward, frames 6 to 8 he recovers the tucked pose."),
    "bicicleta": ("cabeca", "a flying knee in mid air (khao loi). All frames are in the air. Frame 1 tucked, frames 2 and 3 the body leans forward, frames 4 and 5 the knee shoots forward at head height, the fists up, fully stretched, frames 6 to 8 he returns to tucked."),
    "defesa": ("pes", "blocking. Frame 1 guard, frames 2 and 3 the forearms cross in front of the face and one knee lifts to shield the body, frames 4 and 5 he holds the block with a grimace, frames 6 and 7 the impact pushes him back a little, frame 8 still blocking."),
    "apanha": ("pes", "getting hit in the face. Frame 1 guard, frames 2 and 3 the head snaps back, mouth open, frames 4 and 5 the torso bends backward with arms flung, frames 6 to 8 he recovers to the guard."),
    "queda": ("cabeca", "being knocked down. Frame 1 hit and bending back, frame 2 feet leaving the ground, frames 3 and 4 flying backward horizontally in the air, frames 5 and 6 falling onto his back, frame 7 bouncing on the floor, frame 8 lying flat on his back."),
    "levanta": ("cabeca", "getting up from the floor. Frame 1 flat on his back, frames 2 and 3 he sits up fast and plants his hands, frames 4 and 5 he kips up onto his feet, frames 6 and 7 landing crouched, frame 8 guard."),
    "rolamento": ("cabeca", "a low rolling dodge. Frame 1 guard, frames 2 to 7 he ducks and rolls forward in a full somersault, close to the ground, frame 8 back up in a crouch with the guard up."),
    "agarrao": ("cabeca", "a Muay Thai clinch (plum). Frame 1 guard, frame 2 both hands reach forward, frames 3 and 4 the hands lock behind an invisible neck and pull it down, frames 5 and 6 the knee drives up twice into the clinch, frames 7 and 8 he shoves away with both arms. No second person is shown."),
    "bola": ("pes", "Beijinho, blowing a kiss that is thrown like a projectile. Frame 1 guard, frames 2 and 3 he brings the front hand to his lips, frames 4 and 5 he blows a kiss and flings the hand forward, palm open, at head height, with a small pink heart-shaped puff leaving the hand, frames 6 and 7 follow-through with the torso leaning forward and a cocky smirk, frame 8 guard."),
    "compasso": ("cabeca", "a spinning back kick that looks like a horse kick. Frame 1 guard, frames 2 and 3 he turns his back to the front and looks over his shoulder, frames 4 and 5 the straight leg shoots backward at chest height with the heel leading, frames 6 and 7 he spins back around, frame 8 guard."),
    "armada": ("cabeca", "a rising spinning hook kick. Frame 1 low stance, frames 2 and 3 he turns his back and starts to rise, frames 4 and 5 he spins in the air with the straight leg sweeping high, frames 6 and 7 falling, frame 8 landing."),
    "caneta": ("cabeca", "a low sliding tackle like in football (carrinho). Frame 1 guard, frames 2 and 3 he drops to the floor, frames 4 and 5 sliding on one hip with the leading leg stretched forward, frames 6 and 7 getting up, frame 8 guard."),
    "golaco": ("pes", "a super move, a flurry of kicks. Frame 1 guard, frame 2 he crouches and clenches his fists, frames 3 to 6 he unleashes a rapid flurry in place: alternating knee, high kick, knee, high kick with speed lines implied only by the pose, frames 7 and 8 a final big roundhouse kick and a pose."),
    "provoca": ("pes", "a taunt: the Muay Thai pre-fight dance. Frames 1 to 3 he bows with the hands together and then opens his arms wide, frames 4 to 6 he bounces on his feet and waves the opponent in with both hands, frames 7 and 8 a cocky smirk and a shoulder shrug."),
    "vitoria": ("pes", "a victory celebration. Frame 1 guard, frames 2 and 3 he raises both fists high, frames 4 to 6 he flexes his arms and laughs with the head thrown back, frames 7 and 8 he points at the screen."),
    "lata": ("pes", "a Muay Thai warm-up, an 8-frame loop. Frame 1 guard, frames 2 and 3 he rolls both shoulders backward, frames 4 and 5 he shakes out his arms and cracks his neck to each side, frames 6 and 7 he bounces on his toes twice, frame 8 guard."),
    "endiabrado": ("pes", "the AWAKENED HORSE FORM of the same man, an 8-pose sheet (not an animation loop, eight different poses, in this order): 1 power stance with both fists clenched low at his sides, chest out, snorting; 2 walking forward in a low menacing Muay Thai bounce; 3 deep crouch with the guard up; 4 straight punch with the front arm fully extended; 5 high roundhouse kick with the shin at head height; 6 rising knee strike with both fists up high; 7 blowing a big dark-red kiss forward with the open hand, torso leaning back; 8 mid-air flying knee with the knees tucked. In every pose the transformation is: his HEAD is a muscular black horse head (long snout, flaring nostrils with white steam puffing out, flowing dark mane down the back of the neck, glowing red eyes) on the same strong human body; skin a bit darker with faint glowing red veins; dark smoke and steam rising from the shoulders and hands; the black satin trunks with white waistband and the rope armbands and white hand wraps kept. Proud and fierce, not a monster. Keep the same size and scale as the attached sheet."),
    "despertar_a": ("pes", "the transformation, part one. Frames 1 to 3 he takes a deep breath with his chest out and clenches both fists at his sides, red veins glowing on his arms and neck, frames 4 to 6 his head begins to stretch forward into a horse muzzle while a dark mane sprouts along his neck, steam rising from his shoulders, frames 7 and 8 the horse head is half formed and his eyes glow red, he arches his back in pain and power."),
    "despertar_b": ("pes", "the transformation, part two. Frames 1 to 3 the horse head is fully formed with a long black snout, flowing mane and glowing red eyes, he throws his head back and neighs with his mouth open, frames 4 to 6 he rears his chest and stamps one foot hard on the ground with a puff of dust, steam pouring from his nostrils and shoulders, frames 7 and 8 he settles into the Muay Thai guard with the horse head, snorting a cloud of steam, menacing."),
    "derrota": ("cabeca", "complaining after losing. Frames 1 and 2 falling to sit on the floor, frames 3 to 8 sitting on the floor with legs out and arms wide open, complaining to the referee, mouth open."),
}


# ---------------------------------------------------------------- Endiabrado: o demônio cavalo (aprovado em 2026-11-07)
# Referência: folhas/demonio_modelo.png (anexada em todo pedido). Ele não luta Muay Thai: é fera, garra, coice e casco.
# Cada folha e_<golpe> tem os mesmos 8 tempos da normal (o golpe acerta no mesmo quadro), para a troca do Despertar.
CABECA_DEMONIO = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached sprite sheet shows the exact character and art style to keep: the DEMON HORSE (Gutto transformed). Same half-horse half-man head (horse muzzle with flaring steaming nostrils, horse ears, a man's brow and thick mustache, glowing red eyes, two short curved black horns, long wild black mane), same huge hunched hairy human body with almost black skin and glowing red ember cracks, black claws, horse legs with black hooves, long black tail, torn black Muay Thai trunks with white waistband, snapped rope armbands. Same colors and same size as the attached sheet. He fights like a wild beast, never like a Muay Thai fighter.

Style is a hand-drawn 16-bit SNES / 90s arcade sprite, clean dark outline, flat cel shading, never a 3D render.

Layout: one single row of 8 frames in 8 equal-width cells, wide image, side view, always facing right, same scale as the attached sheet, hooves on the same ground line unless the move leaves the ground. Each figure stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, with no shadow, no ground, no text, no numbers, no borders and no effects.

Consecutive frames differ by a small amount, so the motion looks smooth when played in sequence.

Animation: """

FOLHAS_DEMONIO = {
    "endiabrado": "an 8-pose sheet (eight different poses, in this order): 1 hunched beast stance, claws open low; 2 walking forward on the hooves, hunched; 3 low crouch on all fours ready to pounce; 4 claw swipe with the front arm fully extended; 5 back kick (horse buck) with the hind leg shooting backward; 6 rearing up on the hind legs with both claws raised high; 7 snorting a burst of fire and steam forward from the nostrils; 8 mid-air leap with the hooves tucked.",
    "despertar_b": "the transformation, part two. Frames 1 and 2 the half-formed horse head throws back and neighs, frames 3 and 4 the body swells bigger, black hair bursts out on shoulders, chest and arms, horns grow, frames 5 and 6 the feet become hooves and he rears up and stamps both hooves with a puff of dust, frames 7 and 8 he drops into the hunched beast stance of the attached sheet, snorting steam.",
    "anda": "walking forward, an 8-frame loop. Hunched forward, heavy hoof steps, the shoulders rolling, claws hanging low, mane and tail swaying. The legs complete a full two-step cycle and frame 8 flows back into frame 1.",
    "soco": "two claw swipes. Frame 1 beast stance, frame 2 the front arm cocks back, frame 3 the front claw swipes forward at chest height, frame 4 it pulls back, frame 5 the back shoulder rolls forward, frame 6 a big overhead claw swipe from the back arm fully extended forward at chest height, frame 7 he recovers, frame 8 beast stance.",
    "martelo": "a downward hammer blow with both fists joined. Frame 1 beast stance, frame 2 both arms rise, frame 3 the joined fists high over the head, frames 4 and 5 he smashes them down and forward at chest height, frames 6 and 7 he straightens, frame 8 beast stance.",
    "chute_baixo": "a hoof stomp forward. Frame 1 beast stance, frame 2 the front hoof lifts, frame 3 the hoof raised at knee height, frames 4 and 5 it stamps down hard and forward low to the ground, frames 6 and 7 back, frame 8 beast stance.",
    "chute_alto": "a horse buck: back kick with both hind legs. Frame 1 beast stance, frame 2 he leans forward onto his hands, frame 3 the hind legs gather, frames 4 and 5 both hooves shoot backward high at head height, body almost horizontal, frames 6 and 7 he drops back onto the hooves, frame 8 beast stance.",
    "afastar": "a shoulder and horn ram that shoves the opponent away. Frame 1 beast stance, frames 2 and 3 he lowers the head and coils, frames 4 and 5 he lunges forward horns first with the shoulder at chest height, frames 6 and 7 he pulls back, frame 8 beast stance.",
    "agachado": "going down into a low crouch. Frames 1 to 4 he sinks from the beast stance onto all fours, claws on the ground, head low and horns forward. Frames 5 to 8 he stays crouched, breathing with small movements, steam from the nostrils.",
    "baixo_soco": "a low claw swipe from the crouch. Frame 1 on all fours, frames 2 and 3 the front arm cocks back, frames 4 and 5 the claw swipes forward along the ground at ankle height, frames 6 to 8 back to all fours.",
    "cabecada": "a rising horn uppercut from the crouch, used as an anti-air. Frame 1 on all fours, frames 2 and 3 he pushes up with the legs, frames 4 and 5 he drives straight upward horns first with both claws up, fully stretched, frames 6 to 8 he lands back on all fours.",
    "rasteirinha": "a quick low hoof jab from the crouch. Frame 1 on all fours, frames 2 and 3 the front hoof slides out, frames 4 and 5 the leg is stretched just above the floor, frames 6 to 8 it pulls back.",
    "rasteira": "a low tail-and-leg sweep. Frame 1 on all fours, frames 2 and 3 he spins low, frames 4 and 5 the straight hind leg and the tail sweep wide along the floor, frames 6 to 8 back to all fours.",
    "pulo": "a jump. Frame 1 hooves bent ready, frame 2 pushing off, frame 3 rising with legs tucking, frame 4 tucked at the top with claws up, frame 5 still tucked, frame 6 falling with legs opening, frame 7 reaching down with the hooves, frame 8 landing hunched.",
    "ar_soco": "a downward claw slash in mid air. All frames in the air, legs tucked. Frames 1 to 3 the arm winds up, frames 4 and 5 the claw slashes down and forward, frames 6 to 8 he recovers the tucked pose.",
    "bicicleta": "a mid-air double hoof kick. All frames in the air. Frame 1 tucked, frames 2 and 3 he leans back, frames 4 and 5 both hooves stomp forward at head height, fully stretched, frames 6 to 8 back to tucked.",
    "defesa": "blocking. Frame 1 beast stance, frames 2 and 3 he hunches and crosses both hairy forearms in front of the face, frames 4 and 5 he holds the block, snarling, frames 6 and 7 the impact pushes him back a little, frame 8 still blocking.",
    "apanha": "getting hit in the face. Frame 1 beast stance, frames 2 and 3 the horse head snaps back with the mouth open, frames 4 and 5 the torso bends backward, mane flying, frames 6 to 8 he recovers to the beast stance.",
    "queda": "being knocked down. Frame 1 hit and bending back, frame 2 hooves leaving the ground, frames 3 and 4 flying backward horizontally, frames 5 and 6 falling onto his back, frame 7 bouncing on the floor, frame 8 lying flat on his back.",
    "levanta": "getting up from the floor. Frame 1 flat on his back, frames 2 and 3 he rolls over onto all fours, frames 4 and 5 he pushes up on the hooves, frames 6 and 7 rising hunched and shaking the mane, frame 8 beast stance.",
    "rolamento": "a low rolling dodge. Frame 1 beast stance, frames 2 to 7 he tucks and rolls forward in a full somersault close to the ground, frame 8 back on all fours.",
    "agarrao": "a bite throw. Frame 1 beast stance, frame 2 both claws reach forward, frames 3 and 4 the claws grab an invisible opponent and the horse mouth bites forward, frames 5 and 6 he lifts and swings around, frames 7 and 8 he hurls forward with both arms. No second person is shown.",
    "bola": "snorting a fireball. Frame 1 beast stance, frames 2 and 3 he rears the head back and inhales, chest swelling, frames 4 and 5 he thrusts the head forward and blasts a burst of red fire and steam from the nostrils at head height, frames 6 and 7 follow-through with smoke trailing, frame 8 beast stance.",
    "compasso": "a spinning horse buck. Frame 1 beast stance, frames 2 and 3 he turns his back and looks over the shoulder, frames 4 and 5 one hind leg kicks straight backward at chest height with the hoof leading, frames 6 and 7 he spins back around, frame 8 beast stance.",
    "armada": "rearing up and smashing down with both hooves. Frame 1 beast stance, frames 2 and 3 he rears up on the hind legs, front arms high, frames 4 and 5 at full height, frames 6 and 7 he slams both front claws and hooves down to the ground, frame 8 crouched.",
    "caneta": "a sliding tackle like in football, demonic. Frame 1 beast stance, frames 2 and 3 he dives low, frames 4 and 5 sliding on one hip with the leading hoof stretched forward and sparks from the hoof, frames 6 and 7 getting up, frame 8 beast stance.",
    "golaco": "a super move, a wild frenzy. Frame 1 beast stance, frame 2 he crouches and roars, frames 3 to 6 a frenzy in place: claw, buck, claw, stomp, frames 7 and 8 a final huge rearing double hoof stomp and a roar.",
    "provoca": "a taunt. Frames 1 to 3 he scrapes a hoof on the ground twice like a bull, frames 4 to 6 he rears his head and neighs at the sky, frames 7 and 8 he snorts steam and grins with big horse teeth.",
    "vitoria": "a victory. Frame 1 beast stance, frames 2 and 3 he rears up on the hind legs, frames 4 to 6 he neighs loudly with the claws raised, frames 7 and 8 he lands and pounds his chest.",
    "derrota": "defeated. Frames 1 and 2 he drops to his knees, frames 3 to 8 sitting on the floor with the hooves out, head hanging, steam fading, panting.",
}


def pedido(nome):
    if nome.startswith("e_"):
        return CABECA_DEMONIO + FOLHAS_DEMONIO[nome[2:]]
    if nome in ("endiabrado", "despertar_b"):
        return CABECA_DEMONIO + FOLHAS_DEMONIO[nome]
    return CABECA + FOLHAS_GUTTO[nome][1]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n".join(FOLHAS_GUTTO))
    else:
        print(pedido(sys.argv[1]))
