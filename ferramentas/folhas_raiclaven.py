"""Roteiro das folhas do Raiclaven, o Barbeiro, para o ChatGPT (ficha em docs/fichas/barbeiro.md).

Cada folha: 8 quadros em fila, fundo magenta #FF00FF, com a folha-referência (folhas/referencia_ginga.png) anexada.
Os golpes são do barbeiro (pente, tesoura, vassoura, talco, toalha), não de outro lutador: cada nome é o espaço do kit que
a folha ocupa no gerador. `python ferramentas/folhas_raiclaven.py nome` imprime o pedido completo.
"""
import sys

CABECA = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached sprite sheet shows the exact character and art style to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown skin, short black curly hair with a fade, goatee, huge psychopath grin and wide crazy eyes. Same black short-sleeve barber shirt with silver trim and buttons and the small red-white-blue barber pole badge, same black apron with comb and shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with riveted pauldron ending in GIANT silver scissors, same huge human LEFT arm with the hand holding a black comb. Same colors and same size as the attached sheet. He fights with the martial art of the barber, never like a boxer or karate fighter.

Style is a hand-drawn 16-bit SNES / 90s arcade sprite, clean dark outline, flat cel shading, never a 3D render.

Layout: one single row of 8 frames in 8 equal-width cells, wide image, side view, always facing right, same scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, with no shadow, no ground, no text, no numbers, no borders and no effects.

Consecutive frames differ by a small amount, so the motion looks smooth when played in sequence.

Animation: """

# espaço do kit -> (âncora, movimento do barbeiro)
FOLHAS_RAICLAVEN = {
    "ginga": ("pes", "idle loop: the scissors open and close slowly, the comb spins in the hand (é a referencia_ginga.png)."),
    "anda": ("pes", "walking forward, an 8-frame loop. Wide confident barber strut, the scissors held forward snipping open and closed, the comb spinning in the left hand, shoulders swaying, the crazy grin. The legs complete a full two-step cycle and frame 8 flows back into frame 1."),
    "soco": ("pes", "comb jab then scissor snip. Frame 1 stance, frame 2 the left hand pulls back with the comb, frame 3 a fast jab forward with the comb at face height, frame 4 it pulls back, frame 5 the mechanical arm swings forward with the scissors wide open, frame 6 the scissors snap shut at neck height, fully extended, frame 7 he recovers, frame 8 stance."),
    "martelo": ("pes", "an overhead scissors chop. Frame 1 stance, frame 2 the mechanical arm rises, frame 3 the scissors high over the head, wide open, frames 4 and 5 he chops down hard and forward with the open scissors at chest height, leaning in, frames 6 and 7 he pulls the scissors back up, frame 8 stance."),
    "chute_baixo": ("pes", "a pointy shoe kick to the shin. Frame 1 stance, frame 2 the front foot lifts, frame 3 chambers low, frames 4 and 5 the shiny shoe tip kicks forward at shin height, frames 6 and 7 back, frame 8 stance."),
    "chute_alto": ("pes", "a high straight front kick like a razor. Frame 1 stance, frame 2 the back knee rises, frame 3 chambered high, frames 4 and 5 the leg snaps straight up and forward at head height with the shoe sole leading, scissors held back for balance, frames 6 and 7 the leg comes down, frame 8 stance."),
    "afastar": ("pes", "a big push kick that launches the opponent (end of the shift). Frame 1 stance, frames 2 and 3 he leans back and chambers the knee to the chest, frames 4 and 5 the foot thrusts straight forward at chest height, frames 6 and 7 the foot lands forward, frame 8 stance."),
    "agachado": ("pes", "going down into a low crouch. Frames 1 to 4 he sinks into a deep crouch, scissors held forward low, comb up near the face. Frames 5 to 8 he stays crouched, snipping the scissors slowly, grinning."),
    "baixo_soco": ("pes", "a low comb jab from the crouch. Frame 1 deep crouch, frames 2 and 3 the left hand pulls back, frames 4 and 5 the comb jabs straight forward at knee height, frames 6 to 8 back to the crouch."),
    "cabecada": ("pes", "rising scissors anti-air from the crouch. Frame 1 deep crouch, frames 2 and 3 he pushes up, frames 4 and 5 he stands tall and thrusts the open scissors straight up above his head, frames 6 to 8 he lands back in the crouch."),
    "rasteirinha": ("pes", "a quick low shoe kick from the crouch. Frame 1 deep crouch, frames 2 and 3 the leg slides out, frames 4 and 5 the shoe is stretched just above the floor, frames 6 to 8 the leg pulls back."),
    "rasteira": ("pes", "a low sweep with a barber broom. Frame 1 deep crouch, frames 2 and 3 he pulls a long barber broom from behind his back, frames 4 and 5 he sweeps the broom wide along the floor, frames 6 to 8 he tucks the broom away and returns to the crouch."),
    "pulo": ("pes", "a jump. Frame 1 knees bent ready, frame 2 pushing off, frame 3 rising with legs tucking, frame 4 tucked at the top with scissors open, frame 5 still tucked, frame 6 falling with legs opening, frame 7 reaching down, frame 8 landing with knees bent."),
    "ar_soco": ("pes", "a diving scissors slash in mid air. All frames in the air with knees tucked. Frames 1 to 3 the scissors rise, frames 4 and 5 the open scissors slash down and forward in a diagonal, frames 6 to 8 he recovers the tucked pose."),
    "bicicleta": ("pes", "a crossing flying kick in mid air. All frames in the air. Frame 1 tucked, frames 2 and 3 he turns sideways, frames 4 and 5 both legs scissor-kick forward at head height, fully stretched, frames 6 to 8 back to tucked."),
    "defesa": ("pes", "blocking. Frame 1 stance, frames 2 and 3 he raises the flat side of the giant scissors in front of his face like a shield, comb hand behind it, frames 4 and 5 he holds the block, frames 6 and 7 the impact pushes him back a little, frame 8 still blocking."),
    "apanha": ("pes", "getting hit in the face. Frame 1 stance, frames 2 and 3 the head snaps back, mouth open, frames 4 and 5 the torso bends backward with the scissors and comb flung out, frames 6 to 8 he recovers to the stance, grin coming back."),
    "queda": ("pes", "being knocked down. Frame 1 hit and bending back, frame 2 feet leaving the ground, frames 3 and 4 flying backward horizontally, frames 5 and 6 falling onto his back, frame 7 bouncing on the floor, frame 8 lying flat on his back."),
    "levanta": ("pes", "getting up from the floor. Frame 1 flat on his back, frames 2 and 3 he sits up and plants the scissors on the floor, frames 4 and 5 he pushes himself up on the scissors, frames 6 and 7 standing and combing his hair, frame 8 stance."),
    "rolamento": ("pes", "Next! comb teleport. Frame 1 stance, frame 2 he pulls back the comb in the left hand, frame 3 he flicks the comb forward spinning through the air, frame 4 he bursts into a puff of white talcum powder, frame 5 only the white talc cloud remains where he stood, frame 6 he reappears out of a talc cloud in a low lunge with the scissors forward, frame 7 he catches the spinning comb, frame 8 back up in the stance."),
    # pedido do Breno: joga o pente, some e aparece batendo numa sequência própria (Próximo! forte, estado 1701)
    "pente_combo": ("pes", "Next, Client! a fast sequence of barber strikes right after reappearing. Frame 1 he appears out of a white talc cloud already lunging, frame 2 comb jab to the face, frame 3 scissors slash high, frame 4 scissors slash low, frame 5 spinning backhand with the comb, frame 6 the mechanical arm thrusts the open scissors forward, frame 7 the scissors snap shut with a big final cut, frame 8 he poses combing his hair, grinning."),
    "agarrao": ("pes", "Hot Towel grab. Frame 1 stance, frame 2 the left hand reaches forward with a white hot towel, frames 3 and 4 he wraps the towel around an invisible opponent's face and pulls, frames 5 and 6 he spins around and throws, frames 7 and 8 he calmly fixes his hair with the comb, posing. No second person is shown."),
    "bola": ("pes", "Flying Comb. Frame 1 stance, frames 2 and 3 he pulls back a big comb in the left hand, frames 4 and 5 he hurls it forward like a throwing knife at chest height, a big comb leaving the hand, frames 6 and 7 follow-through, frame 8 stance."),
    "compasso": ("pes", "Scissor Helicopter. Frame 1 stance, frames 2 and 3 the mechanical arm starts spinning at the shoulder, frames 4 and 5 the arm spins like a helicopter blade with the open scissors, motion implied by the pose, frames 6 and 7 it slows down, frame 8 stance."),
    "armada": ("pes", "Spinning Barber Chair kick. Frame 1 stance, frames 2 and 3 he spins on one foot turning his back, frames 4 and 5 he spins with the leg stretched out high like a spinning barber chair, frames 6 and 7 he completes the turn, frame 8 stance."),
    "caneta": ("pes", "Scissors dash. Frame 1 stance, frames 2 and 3 he crouches and aims the scissors forward, frames 4 and 5 he lunges forward low and fast with the scissors open in front like a spear, frames 6 and 7 the scissors snap shut, frame 8 stance."),
    "golaco": ("pes", "a super move, a flurry of haircuts. Frame 1 stance, frame 2 he crouches and grins, frames 3 to 6 a frenzy in place: scissors snip high, comb jab, scissors snip low, scissors snip high, frames 7 and 8 a final huge scissors closing with both arms and a pose."),
    "provoca": ("pes", "a taunt. Frames 1 to 3 he snips the scissors next to his own ear, frames 4 to 6 he points the comb at the opponent and waves him over to the barber chair, frames 7 and 8 he laughs with the head thrown back."),
    "vitoria": ("pes", "a victory. Frame 1 stance, frames 2 and 3 he blows hair off the scissors blades, frames 4 to 6 he combs his own hair proudly with the comb, frames 7 and 8 he poses with the scissors open over his shoulder and the crazy grin."),
    "lata": ("pes", "a warm-up. Frame 1 stance, frames 2 and 3 he sharpens the scissors blades against each other with sparks implied by the pose, frames 4 and 5 he checks the edge with the thumb, frames 6 and 7 he spins the comb, frame 8 stance."),
    "derrota": ("pes", "defeated. Frames 1 and 2 he drops to sit on the floor, frames 3 to 8 sitting on the floor with legs out, the scissors bent and drooping, the comb broken, sulking."),
}


# ---------------------------------------------------------------- Despertar: o CIENTISTA LOUCO (pedido do Breno, 2026-11-10)
# Referência: folhas/cientista_modelo.png (anexada em todo pedido). Ele penteia o cabelo, põe os óculos, grita e o jaleco vem
# voando e gruda nele. No Despertar ele luta parado, fazendo pose e dando ordens, e quem ataca são as cobaias e a Cliente Zero.
# O estranho delas vem do experimento dele: nunca pessoas reais nem pessoas com deficiência (regra de conteúdo do jogo).
CIENTISTA = {
    "despertar_a": "penteia o cabelo para trás, põe os óculos de lente verde, sorri e começa a gritar",
    "despertar_b": "grita, o jaleco vem voando, enrola e gruda nele, tubos e luvas encaixam, termina na pose de cientista",
    "endiabrado": "8 poses: parado esfregando as luvas, andando, agachado examinando, apontando a tesoura (ordem), rindo de braços "
                  "para cima, jogando tubo de ensaio, estalando os dedos, pulinho com o jaleco abrindo",
    "e_anda": "andar de cientista na ponta dos pés", "e_agachado": "agacha e anota numa prancheta",
    "e_pulo": "pulo com o jaleco abrindo como asa", "e_defesa": "defende com a prancheta e a tesoura",
    "e_apanha": "apanha e os óculos entortam", "e_queda": "cai e os tubos se espalham", "e_levanta": "levanta ajeitando os óculos",
    "e_soco": "estala os dedos (faísca verde), aponta e dá uma tesourada rápida",
    "e_martelo": "ergue a tesoura como batuta de maestro e manda o ataque pesado",
    "e_bola": "joga um tubo de ensaio verde (granada)", "e_cabecada": "tesoura para cima com choque verde (antiaéreo)",
    "e_agarrao": "agarra e aplica uma seringa gigante de líquido verde", "e_rolamento": "some numa fumaça verde e reaparece",
    "e_golaco": "super: raios verdes de laboratório em volta enquanto ri", "e_provoca": "anota na prancheta e balança a cabeça",
    "e_vitoria": "ergue o tubo, ri e faz reverência", "e_derrota": "senta no chão com óculos quebrados",
    # quem luta por ele (2ª versão): clientes comuns que saíram errados da máquina e a Cliente Zero na corrente
    "mulher_parada": "Cliente Zero: magra, cinzenta, cabelo vivo até o joelho, olhos verdes, coleira e corrente; agachada como aranha",
    "mulher_chicotada": "Cliente Zero dá o bote com as duas garras, a corrente estica",
    "mulher_mangual": "Cliente Zero voa em arco puxada pela corrente e cai de cabeça e garras",
    "mulher_agarra": "Cliente Zero salta e gruda no oponente com braços, pernas e cabelo",
    "mulher_rasteja": "Cliente Zero corre rente ao chão como aranha (loop)",
    "mulher_sobe": "Cliente Zero salta e arranha para cima (antiaéreo)",
    "e_corrente_parado": "cientista parado segurando a corrente (loop)",
    "e_corrente_chicotada": "cientista estala a corrente para a frente",
    "e_corrente_mangual": "cientista gira a corrente acima da cabeça e desce",
    "e_corrente_puxao": "cientista puxa a corrente de volta, mão sobre mão",
    "e_corrente_giro": "super: cientista gira em volta de si como arremesso de martelo",
    "cobaia_pescoco": "cliente de pescoço de borracha: estica e dá cabeçada de longe",
    "cobaia_tentaculo": "cliente de cabelo tentáculo: varre o chão e prende o tornozelo",
    "cobaia_avesso": "cliente de cabeça virada: anda de costas, pula em arco e chuta caindo",
    "cobaia_gel": "cliente inchado de gel: rola até o oponente e estoura numa poça de gel",
    "fila_clientes": "cliente hipnotizado de olhos de coração e capa de barbeiro, andando (Fila de Clientes)",
}


# ---------------------------------------------------------------- Pente fino de anatomia (2026-11-11): desenhos a refazer
# O que o gerador não conserta sozinho (gerar_raiclaven.py só troca, corta ou retoca). `python ferramentas/folhas_raiclaven.py
# nome` imprime o pedido com este MOTION no lugar do antigo. FIXO vai no fim de todos.
FIXO = (" Anatomy rules for every frame: exactly two arms and two legs; the dark steel RIGHT arm always ends in the same giant"
        " scissors, with exactly two straight blades and one pivot, always the same size as in the attached sheet; the human"
        " LEFT arm is always fully visible, with the same brown skin tone as the face, and its hand always holds the same"
        " black comb unless the motion says otherwise; nothing floats detached from the body; no object is drawn twice.")
REDESENHAR = {
    # derrota: a tesoura virava corrente com 3 garras e as pernas eram um volume só com uma sola gigante
    "derrota": "defeated. Frame 1 stance with the knees giving way, frame 2 he drops down, frame 3 he lands sitting on the floor, frames 4 to 8 he stays sitting with BOTH legs stretched forward, clearly separated and readable, the closed scissors resting on the floor beside him, the comb hand hanging low, head down, sulking.",
    # vitória: braço de carne sumia nos quadros 2-3, pele vermelha nos 4-6 e tesoura a 60% do tamanho nos 7-8
    "vitoria": "a victory. Frame 1 stance, frames 2 and 3 he raises the scissors near his mouth and blows hair off the blades while the left hand keeps holding the comb at chest height, frames 4 to 6 he combs his own hair proudly with the comb, frames 7 and 8 he poses with the scissors open and raised over his shoulder, full size, the left fist on his hip, crazy grin.",
    # agarrão: nos quadros 3-4 a tesoura sumia e a mão de metal segurava a toalha como mão comum
    "agarrao": "Hot Towel grab. Frame 1 stance, frame 2 the LEFT human hand tucks the comb in the apron pocket and pulls out a white hot towel, frames 3 and 4 the LEFT hand alone wraps the towel around an invisible opponent's face and pulls, the scissors closed and held back on the steel arm, frames 5 and 6 he spins around and throws, frames 7 and 8 he takes the comb back out and calmly fixes his hair, posing. No second person is shown.",
    # armada e caneta: o pente sumia da mão durante o golpe inteiro; na armada, 2 quadros de costas com corte seco
    "armada": "Spinning Barber Chair kick. Frame 1 stance, frames 2 and 3 he pivots on the front foot and turns sideways, never showing his full back, frames 4 and 5 the back leg swings around stretched out high, frames 6 and 7 the leg comes down and he completes the turn, frame 8 stance.",
    "caneta": "Scissors dash. Frame 1 stance, frames 2 and 3 he crouches and aims the scissors forward, frames 4 and 5 he lunges forward low and fast with the scissors open in front like a spear, frames 6 and 7 the scissors snap shut, frame 8 stance.",
    # bola: braço de carne pintado de metal no quadro 3 e o pente já voando desenhado no corpo (o jogo solta o projétil)
    "bola": "Flying Comb throw, body only. Frame 1 stance, frames 2 and 3 the human LEFT arm pulls the comb back behind the ear, frame 4 the arm whips forward, frame 5 the arm is fully stretched forward at chest height with the hand OPEN AND EMPTY, frames 6 and 7 follow-through with the empty hand, frame 8 stance with the comb back in the hand. The thrown comb is never drawn in the air.",
    # rolamento: lâmina a mais em 3 quadros, caco branco solto, pente voando desenhado no corpo
    "rolamento": "Next! talc teleport. Frame 1 stance, frame 2 he raises a handful of white talcum powder in the left hand, frame 3 he throws the talc down at his feet, frame 4 the white talc cloud covers him up to the chest, frame 5 only the white cloud remains, frame 6 he reappears out of a thin cloud in a low crouch with the scissors forward, frame 7 he rises, frame 8 stance.",
    # compasso: tesoura saindo direto do ombro, sem antebraço, nos quadros 2 e 7; corpo imóvel
    "compasso": "Scissor Helicopter. Frame 1 stance, frame 2 the steel arm rises with the elbow clearly bent and the forearm visible, frame 3 the arm is straight up over the head, frames 4 to 6 the arm spins the open scissors above the head like a helicopter blade while the torso leans with the spin, frame 7 the arm comes down with the elbow bent, frame 8 stance.",
    # rasteira: duas vassouras no quadro 6
    "rasteira": "a low sweep with ONE barber broom. Frame 1 deep crouch, frames 2 and 3 the left hand pulls one long barber broom from behind his back, frames 4 and 5 he sweeps the broom wide along the floor in front of him, frames 6 and 7 he lifts the same broom back up, frame 8 crouch with the broom gone. Both feet are always visible.",
    # andar: a folha arcade serve, mas é um passo arrastado (a mesma perna na frente nas duas passadas)
    "anda": "walking forward, an 8-frame loop with ALTERNATING legs. Frame 1 contact with the left leg in front, frame 2 the weight goes down on it, frame 3 the right leg passes under the body, frame 4 the body rises, frame 5 contact with the RIGHT leg in front, frame 6 the weight goes down on it, frame 7 the left leg passes under the body, frame 8 the body rises and flows back into frame 1. The scissors and the comb barely move.",
    # ginga: a folha arcade serve, mas as pernas ficam paradas (só a mão e a tesoura mexem)
    "ginga": "idle loop with weight transfer. Frames 1 to 4 the knees bend and the hips sink a little while the weight shifts to the back leg, frames 5 to 8 the hips rise and the weight comes back to the front leg, flowing into frame 1. The scissors open and close slowly. The comb stays still in the left hand, always seen from the same side.",
    # Despertar: as duas pastas são a provocação repetida; falta a transformação (ficha: Surto de Tesoura / cientista)
    "despertar_a": "the start of his transformation. Frames 1 and 2 he tucks the comb in the apron pocket, frames 3 and 4 he combs his hair back with the bare left hand, frames 5 and 6 the scissors lock wide open with a jolt, frames 7 and 8 he hunches forward, grinning wider, shoulders shaking.",
    "despertar_b": "the end of his transformation. Frames 1 and 2 hunched forward, shaking, frames 3 and 4 the torso arches back, frames 5 and 6 he screams at the sky with both arms thrown wide and the scissors blades fully open, frames 7 and 8 he snaps back into the stance, laughing.",
}


def pedido(nome):
    return CABECA + (REDESENHAR[nome] + FIXO if nome in REDESENHAR else FOLHAS_RAICLAVEN[nome][1])


if __name__ == "__main__":
    print(pedido(sys.argv[1]) if len(sys.argv) > 1 else "\n".join(FOLHAS_RAICLAVEN))
