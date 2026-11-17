#!/usr/bin/env python3
"""Folhas do Raiclaven despertado com "A Cliente", a criatura de terror (#43, aprovada pelo Breno em 2026-11-15 19:23Z).

  python3 ferramentas/folhas_criatura.py              lista as folhas, na ordem de pedir
  python3 ferramentas/folhas_criatura.py NOME         imprime o pedido de uma folha (8 quadros, ChatGPT)
  python3 ferramentas/folhas_criatura.py NOME --g4 H  pedido em 4 quadros para o Gemini (H = 0: quadros 1-4, 1: 5-8)

Regra da seção 4 das regras-dos-lutadores (Breno, #47): o despertado tem TODOS os golpes próprios. Nada do modo normal
entra. A lista de golpes aprovada está em docs/fichas/raiclaven-despertado-golpes.md. O conceito aprovado é a versão B
(docs/previas/raiclaven-dupla/conceito-criatura-b.jpg), que vai anexado em todo pedido junto de uma folha pronta para o
estilo.

As folhas saem em sprites/raiclaven/quadros/folhas_criatura/c_<nome>.png, em 8 células iguais, e o
gerar_raiclaven.py --criatura as corta como as da dupla.
"""
import sys

CABECA = """Generate ONE image with your image generation tool. Do not write code.

The FIRST attached image is the approved model sheet of the duo: keep exactly these two characters, colors and proportions. The SECOND attached image is a finished sprite sheet: copy its pixel-art style and scale exactly (ignore its content and layout).

RAICLAVEN, the MAD SCIENTIST barber: huge muscular man, brown skin, slicked-back bright GREEN hair, round green-glowing goggles, huge manic grin, torn rusty white lab coat, black barber shirt, black apron with tools and green test tubes, baggy black pants, steel boots, huge riveted dark steel mechanical RIGHT arm ending in GIANT silver scissors, a gloved human left hand. On his back a BARBER HARNESS: brown leather straps across his chest with a round barber-pole buckle, a small red barber-chair seat between two glass tanks of green liquid with tesla coils.

"THE CLIENT", his failed experiment, a HORROR CREATURE strapped into that seat: emaciated grey-green corpse flesh sewn from mismatched patches, thick black stitches and metal staples, exposed ribs, dripping green slime, a cluster of bulging mismatched eyes all over its head, a huge mouth splitting its head side to side full of crooked teeth, a SECOND mouth that opens vertically down its chest with a long toothed tongue, tufts of ripped green hair, THREE long spindly many-jointed arms: a straight RAZOR sewn in place of one hand, a chrome HAIR DRYER grafted into the second forearm, long hooked CLAWS on the third. Rubber tubes and wires run from its spine into the tanks and into the back of his neck. It is a monster, never a person. It stays strapped in the seat; its arms, neck and tongue can STRETCH far out of it.

How they fight: he is the vehicle, he twists, bows, spins and throws his weight to bring the creature to the target, laughing; the creature grabs, bites, stretches and shocks. Both look completely unhinged and creepy.

Style: hand-drawn 16-bit SNES / 90s arcade sprite, clean dark outline, flat cel shading, never a 3D render.

Layout: one single row of 8 frames in 8 equal-width cells, wide image, side view facing RIGHT, the duo at the same scale in every frame, his feet on the same ground line unless the move leaves the ground. The opponent is always to the RIGHT and is never drawn. Each figure stays inside its own cell. Flat solid magenta background (#FF00FF), no shadow, no ground, no text, no numbers, no borders, no effects (no sparks, no trails, no lightning bolts in the air, no impact marks). Consecutive frames differ by a small amount. He always has one steel arm and one human arm and two legs; the creature always has exactly three arms; nothing floats detached; no object is drawn twice.

Animation: """

G4 = """

Layout for THIS image: ONE single row of exactly 4 frames, wide 21:9, the duo drawn LARGE (about 80% of the image height), each figure inside its own quarter. """

# nome -> (grupo, descrição dos 8 quadros). Ordem = ordem de pedir (o que mais aparece na luta primeiro).
FOLHAS = {
    # ---- básicos (estados do sistema)
    "ginga": ("base", "idle loop. He sways heavily from foot to foot, laughing, the scissors snapping slowly; the creature twitches in the seat, its eyes blinking out of rhythm, the claw arm flexing, the chest mouth opening and closing, drooling slime. Frame 8 flows back into frame 1."),
    "anda": ("base", "walking forward, 8-frame loop with alternating legs (frame 1 his left leg in front, frame 5 his right leg in front). He stomps hunched forward; the creature leans over his head reaching forward with the claw arm like it smells prey, the razor arm dragging behind. Frame 8 flows into frame 1."),
    "agachado": ("base", "going down into a crouch. Frames 1 to 4 he squats deep with the scissors on the floor and his back bent forward, the creature slides over his head and hangs upside down in front of his face, frames 5 to 8 they hold the crouch, the creature's eyes swivel around."),
    "pulo": ("base", "a jump. Frame 1 his knees bent, frame 2 pushing off, frames 3 to 5 in the air knees tucked, coat flying, the creature's three arms flailing up like a spider, frame 6 falling, frame 7 reaching down, frame 8 landing."),
    "defesa": ("base", "blocking. Frame 1 stance, frames 2 and 3 he raises the flat of the giant scissors like a shield and the creature wraps its three arms around his head and the tanks like a cage, frames 4 to 8 they hold the block, slightly pushed back on frames 6 and 7."),
    "apanha": ("base", "getting hit. Frame 1 stance, frames 2 and 3 his head snaps back and the creature's eyes all squeeze shut, frames 4 and 5 both bend backward, the creature shrieks with both mouths, frames 6 to 8 they recover, the creature hissing forward."),
    "queda": ("base", "knocked down. Frame 1 hit, frame 2 feet leaving the ground, frames 3 and 4 flying backward to the left, frames 5 and 6 he twists so he lands on his side, the creature clinging to the seat, frame 7 bounce, frame 8 lying on his side facing right, the creature limp."),
    "levanta": ("base", "getting up. Frame 1 lying on his side, frames 2 and 3 the creature's three arms push against the floor to lift him, frames 4 and 5 he rises to one knee on the steel arm, frames 6 and 7 standing, frame 8 stance."),
    "provoca": ("base", "taunt. Frames 1 to 3 he pats the creature's head like a pet, frames 4 to 6 the creature stretches its neck toward the opponent and licks the razor with the toothed tongue, frames 7 and 8 both laugh, his head thrown back."),
    "vitoria": ("base", "victory. Frame 1 stance, frames 2 and 3 he spreads both arms like a showman, frames 4 to 6 the creature rises tall over his head with all three arms spread and both mouths open in a scream, frames 7 and 8 final pose: scissors open over his head, creature screaming at the sky."),
    "derrota": ("base", "defeated. Frames 1 and 2 he drops to sit on the floor, frames 3 to 8 sitting with legs stretched forward, goggles cracked, head down; the creature hangs limp over his shoulder, one claw twitching."),
    "despertar": ("base", "second half of the transformation, he already is the mad scientist with the harness and the EMPTY red seat. Frames 1 and 2 he yanks a lever on the tank and the tubes light up, frames 3 and 4 the creature crawls up from behind him over the tanks, frames 5 and 6 it drops into the seat and the tubes plug into it, frames 7 and 8 both scream at the sky, arms spread."),
    # ---- normais (16): em pé, agachado, no ar, direcionais
    "x_pe": ("normal", "standing light punch: a fast claw slap. Frame 1 stance, frame 2 he dips his shoulder, frames 3 and 4 the creature's claw arm whips over his shoulder and slaps forward at face height, frame 5 it pulls back, frames 6 to 8 stance."),
    "y_pe": ("normal", "standing heavy punch: the razor arm stretches. Frame 1 stance, frames 2 and 3 he leans back and the creature cocks the razor arm, frames 4 and 5 he bows forward and the razor arm stretches REALLY far straight forward at chest height (twice his arm length), frames 6 and 7 the arm snaps back, frame 8 stance."),
    "a_pe": ("normal", "standing light kick: steel boot kick while the creature spits. Frames 1 to 3 his knee rises, frames 4 and 5 the steel boot kicks forward at shin height while the creature leans out and spits a glob of slime forward from the face mouth, frames 6 to 8 stance."),
    "b_pe": ("normal", "standing heavy kick: back-spin bash. Frame 1 stance, frames 2 and 3 he spins turning his back to the right, frames 4 and 5 his back faces the opponent and the creature swings all three arms forward at once (razor, dryer, claws) at head height, frames 6 and 7 he completes the turn, frame 8 stance."),
    "x_ag": ("normal", "crouching light punch: ankle pinch. Frame 1 deep crouch, frames 2 to 4 the creature slides over his head and its claw arm darts forward along the floor and pinches at ankle height, frames 5 to 8 back to the crouch."),
    "y_ag": ("normal", "crouching heavy punch, ANTI-AIR: neck stretch bite. Frame 1 deep crouch, frames 2 and 3 he pushes up arching his back, frames 4 and 5 the creature's neck stretches straight UP high above them and bites the air with the face mouth wide open, frames 6 to 8 the neck retracts and he crouches."),
    "a_ag": ("normal", "crouching light kick: tube whip. Frame 1 deep crouch, frames 2 to 4 a thick rubber tube from the tanks whips forward low along the floor like a tail, frames 5 to 8 it retracts, crouch."),
    "b_ag": ("normal", "crouching heavy kick, SWEEP: he drops on his side and the claw arm sweeps. Frame 1 deep crouch, frames 2 and 3 he drops low on his side, frames 4 and 5 the creature's claw arm sweeps wide along the floor far to the right, frames 6 to 8 he rolls back up to the crouch."),
    "x_ar": ("normal", "air light punch: a downward scratch. All frames in the air, knees tucked. Frames 1 to 3 the creature raises the claw arm, frames 4 and 5 it scratches down and forward, frames 6 to 8 tucked."),
    "y_ar": ("normal", "air heavy punch, crosses over: razor arc. All frames in the air. Frames 1 to 3 he leans back and the creature raises the razor arm high, frames 4 and 5 he curls forward and the razor slashes in a big downward arc in front of and below them, frames 6 to 8 tucked."),
    "a_ar": ("normal", "air light kick: his knee strike while the creature bites. All frames in the air. Frames 1 to 3 his knee rises, frames 4 and 5 knee forward and the creature leans over his head biting with the face mouth, frames 6 to 8 tucked."),
    "b_ar": ("normal", "air heavy kick: he falls back-first and the creature hangs below biting. All frames in the air. Frames 1 to 3 he flips so his back and the seat face down, frames 4 and 5 the creature hangs below him with the chest mouth open and the tongue stretched down and forward, frames 6 to 8 he flips back, tucked."),
    "f_y": ("normal", "forward + heavy punch, OVERHEAD: the neck comes down from above. Frame 1 stance, frames 2 and 3 the creature's neck stretches up high over both of them, frames 4 and 5 he bows forward and the neck slams DOWN in front of him, the face mouth biting at head height from above, frames 6 to 8 it retracts, stance."),
    "f_b": ("normal", "forward + heavy kick: steel boot stomp. Frames 1 to 3 he lifts the front steel boot high, frames 4 and 5 he stomps it down hard on the floor in front of him, kneeling slightly, while the creature slaps the tanks, frames 6 to 8 stance."),
    "t_x": ("normal", "back + light punch: dryer puff. Frame 1 stance, frames 2 and 3 the creature aims the grafted hair dryer forward over his shoulder, frames 4 and 5 the dryer kicks back as it fires a short puff (not drawn), his coat blowing back, frames 6 to 8 stance."),
    "t_a": ("normal", "back + light kick: collar pull. Frame 1 stance, frames 2 and 3 the claw arm stretches far forward at neck height, frames 4 and 5 the claws close on an invisible collar, frames 6 and 7 the arm yanks back toward them, frame 8 stance."),
    # ---- correntes (o 1º golpe é o normal do botão; aqui o 2º, o 3º e o finalizador)
    "corrente_x": ("corrente", "light chain 'Little Scissors', hits 2, 3 and finisher. Frames 1 and 2 claw slap backhand, frames 3 and 4 a quick bite with the face mouth over his shoulder, frames 5 to 7 FINISHER: the creature stretches its neck forward and clamps its teeth on an invisible opponent at head height and shakes its head violently, frame 8 it lets go, stance."),
    "corrente_y": ("corrente", "heavy chain 'Long Razor', hits 2, 3 and finisher. Frames 1 and 2 the razor arm stretches forward farther than before, frames 3 and 4 he steps in and the razor stretches even farther, frames 5 to 7 FINISHER: he bows deep and the creature slashes an X with the razor and the claws crossing, both arms fully stretched, frame 8 stance."),
    "corrente_a": ("corrente", "light kick chain 'Tube Whip', hits 2, 3 and finisher. Frames 1 and 2 a rubber tube whips high, frames 3 and 4 the tube whips low along the floor, frames 5 to 7 FINISHER: the tube lassoes an invisible ankle and he yanks backward with both arms, leaning back, frame 8 stance."),
    "corrente_b": ("corrente", "heavy kick chain 'Barber Chair Spin', hits 2, 3 and finisher. Frames 1 and 2 he spins (back view) and the creature's arms swing out, frames 3 and 4 a second faster spin, frames 5 to 7 FINISHER: he stops facing right, crouched, and the creature spreads all three arms wide with both mouths screaming (a shockwave, not drawn), frame 8 stance."),
    # ---- especiais
    "peruca": ("especial", "special 'Living Wig' (projectile, body only). Frame 1 stance, frames 2 and 3 he pulls a tuft of green hair with teeth out of the apron pocket, frames 4 and 5 he bowls it underhand along the floor forward, hand open and empty, frames 6 and 7 follow-through, frame 8 stance. The thrown wig is never drawn."),
    "pescoco": ("especial", "special 'Rubber Neck'. Frame 1 stance, frames 2 and 3 he braces and the creature's neck recoils back like a spring, frames 4 and 5 the neck shoots straight forward VERY far at head height (more than half the cell width beyond him) with the face mouth biting, frames 6 and 7 the neck snaps back pulling something invisible, frame 8 stance."),
    "tanque": ("especial", "special 'Burst Tank'. Frame 1 stance, frame 2 he jumps a little, frames 3 and 4 he falls back-first onto the floor, frames 5 and 6 lying on his back the tanks crack and the creature arches screaming with all arms spread, green slime splashing (a shock, no lightning drawn), frames 7 and 8 he springs back up to the stance."),
    "bigodes": ("especial", "special 'Carnivorous Moustaches' (body only). Frame 1 stance, frames 2 and 3 he opens his lab coat wide like a flasher, frames 4 and 5 the creature's chest mouth opens wide and they both lean forward as a swarm leaves (the swarm is not drawn), frames 6 and 7 he closes the coat laughing, frame 8 stance."),
    "secador": ("especial", "the ranged power 'Lightning Dryer'. Frame 1 stance, frame 2 he stabs the scissors into the floor to anchor himself, frames 3 and 4 he bows deep and the creature plugs a cable from the tesla coil into its grafted hair dryer and aims it forward over his head, frames 5 and 6 it fires: the dryer kicks back hard, both blown backward (the beam is not drawn), frames 7 and 8 recovery, stance."),
    # ---- super
    "cirurgia_a": ("super", "super 'Operating Room', first half, no third person is shown. Frame 1 stance, frame 2 he lunges and the giant scissors clamp an invisible opponent, frame 3 he lifts it high with the steel arm, frames 4 to 8 the creature climbs down out of the seat, still tied by the tubes, and 'operates' on the invisible opponent with the razor, the claws and the dryer, each frame a different stab and cut."),
    "cirurgia_b": ("super", "super 'Operating Room', second half. Frames 1 and 2 the creature climbs back into the seat, frames 3 and 4 he holds a glass jar with a wired head inside up high, frames 5 and 6 the tanks glow and crack, both scream, frames 7 and 8 he throws the invisible opponent forward and poses, the creature laughing with both mouths."),
    # ---- agarrões (sem o oponente desenhado: a reação dele vem da folha de vítima)
    "cadeira_a": ("agarrao", "grab 'Electric Chair', first half. Frame 1 stance, frame 2 the giant scissors clamp an invisible opponent, frame 3 he lifts it to shoulder height, frames 4 to 7 the creature works on it: razor slash, claw rake, chest-mouth bite, dryer jab, frame 8 holding it up laughing."),
    "cadeira_b": ("agarrao", "grab 'Electric Chair', second half. Frame 1 holding the invisible opponent up, frames 2 and 3 he spins once, frames 4 and 5 he slams the steel arm down to the floor in front of him, frame 6 he stomps, frames 7 and 8 both laugh, the creature's arms raised."),
    "lavagem": ("agarrao", "low grab 'Hair Wash'. Frame 1 crouch, frame 2 the claw arm grabs an invisible head low in front, frames 3 and 4 he stands and the creature drags the invisible head back over his shoulder, frames 5 to 7 it dunks the invisible head into the open green tank, slime splashing, frame 8 it tosses it forward."),
    "transplante": ("agarrao", "command grab 'Transplant'. Frame 1 stance, frame 2 the creature lunges and wraps all three arms around an invisible opponent in front, frames 3 to 5 he spins around fast with the creature hugging it, frames 6 and 7 the creature lets go and the dryer kicks back as it blasts, frame 8 stance."),
}


def pedido(nome, g4=None):
    texto = CABECA + FOLHAS[nome][1]
    if g4 is not None:
        texto += G4 + ("These 4 frames are FRAMES 1 TO 4 of the 8 described." if g4 == 0 else
                       "These 4 frames are FRAMES 5 TO 8 of the 8 described.")
    return texto


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(pedido(sys.argv[1], int(sys.argv[3]) if "--g4" in sys.argv else None))
    else:
        for n, (g, _) in FOLHAS.items():
            print(f"{g:9s} {n}")
        print(len(FOLHAS), "folhas")
