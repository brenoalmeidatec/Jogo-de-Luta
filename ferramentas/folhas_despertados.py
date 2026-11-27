#!/usr/bin/env python3
"""Pedidos das folhas dos golpes NOVOS dos despertados (#47, regra do Breno de 2026-11-15, listas aprovadas em
2026-11-15 19:23Z no comentário 6899928948): o despertado luta totalmente diferente e nada do normal entra.

  python ferramentas/folhas_despertados.py gutto              lista as folhas do Gutto e a referência a anexar
  python ferramentas/folhas_despertados.py gutto g_patada     imprime o pedido de uma folha para colar no chat

A lista aprovada está em docs/despertados-47/golpes-novos.md. Cada folha: 8 quadros em fila, fundo magenta, a
referência do despertado anexada SEMPRE (o tom de pele desvia em conversa longa). As folhas saem no ChatGPT (GO) ou no
Gemini (Pro) da conta do Alisson; somar +1 no /mnt/project-files/imagens/contador-gemini.md ANTES de cada pedido
(teto de 50 por dia no projeto todo) e apagar o chat de imagem depois de usar.

Os golpes 2 e 3 de cada corrente dividem uma folha (4 quadros cada); o finalizador tem folha própria. Os agarrões
agachado e colado e as reações de quem é agarrado ficam com a thread dos agarrões (#45).
"""
import sys

ESTILO = """Style is a hand-drawn 16-bit SNES / 90s arcade sprite, clean dark outline, flat cel shading, never a 3D render.

Layout: one single row of 8 frames in 8 equal-width cells, wide image, side view, always facing right, same scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, with no shadow, no ground, no text, no numbers, no borders and no effects (fire, smoke, chains of light and impacts are added later by the game, draw only what the body itself holds).

Consecutive frames differ by a small amount, so the motion looks smooth when played in sequence. Exactly the same body size in all 8 frames.

Animation: """

# ----------------------------------------------------------------------------------------- Gutto: Garanhão (minotauro)
REF_GUTTO = "sprites/gutto/quadros/folhas/ginga_endiabrada.png"
CAB_GUTTO = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached sprite sheet shows the exact character and art style to keep: the GARANHÃO, a demon horse-man (Gutto awakened). Same half-horse half-man head (long horse muzzle with flaring nostrils puffing white steam, horse ears, two short curved black horns, long wild black mane, glowing red eyes), same huge hunched hairy body with dark red-brown skin and glowing red ember cracks, black claws, horse legs with black hooves, long black tail, torn black loincloth with the white rope belt and rope armbands. Same colors and same size as the attached sheet.

He fights like a MINOTAUR, a raging bull-beast: the HEAD AND HORNS are his main weapon (gores, headbutts, charges), the arms are clawed paws, the legs are hooves that buck and stomp. He NEVER uses Muay Thai, boxing or any human martial-arts stance, never a clean straight punch or a side kick. Heavy, low, hunched, crushing.

"""

GUTTO = {
    # 16 normais
    "g_patada": "standing light attack, a short clawed paw swipe. Frame 1 hunched beast stance, frame 2 the front paw pulls back with the claws spread, frames 3 and 4 the paw swipes down and forward at chest height, claws leading, frames 5 and 6 the paw comes back, frames 7 and 8 beast stance.",
    "g_gancho_chifre": "standing strong attack, an upward horn hook. Frame 1 beast stance, frames 2 and 3 he lowers the head with the horns pointing forward and bends the knees, frames 4 and 5 he jerks the head up and forward, the horns hooking upward at chin height, mane flying, frames 6 to 8 he settles back into the beast stance.",
    "g_casco_canela": "standing light kick, a short front hoof kick to the shin. Frame 1 beast stance, frame 2 the front hoof lifts a little, frames 3 and 4 the hoof snaps forward low, at shin height, frames 5 and 6 the hoof returns, frames 7 and 8 beast stance.",
    "g_coice": "standing strong kick, a horse buck. Frame 1 beast stance, frames 2 and 3 he turns his back to the right and drops both claws to the ground, frames 4 and 5 BOTH hind legs kick straight backward (to the right, toward the opponent) at chest height with the hooves leading, tail whipping, frames 6 and 7 the legs come down, frame 8 he turns back into the beast stance.",
    "g_garra_rasteira": "crouching light attack. Frame 1 low crouch on all fours, horns forward, frames 2 and 3 one front paw pulls back, frames 4 and 5 the claws rake forward along the floor at ankle height, frames 6 to 8 back to the crouch on all fours.",
    "g_chifrada_sobe": "crouching strong attack, an anti-air gore. Frame 1 crouch on all fours, frames 2 and 3 the hind legs push and the head lowers, frames 4 and 5 he drives upward head first, the horns thrusting up and slightly forward above his head, body stretched up, frames 6 to 8 he drops back to the crouch.",
    "g_casco_raspa": "crouching light kick, a low hoof scrape. Frame 1 crouch on all fours, frames 2 and 3 one hind hoof scrapes backward on the floor like an angry bull, frames 4 and 5 the same hoof kicks forward low along the floor, frames 6 to 8 back to the crouch.",
    "g_rabo_chicote": "crouching strong kick, a low tail sweep that knocks down. Frame 1 crouch on all fours, frames 2 and 3 he spins low on the claws, frames 4 and 5 the long tail and one stretched hind leg sweep wide along the floor in front of him, frames 6 to 8 he comes back into the crouch.",
    "g_ar_garras": "air light attack. All frames in the air with the hooves tucked. Frames 1 and 2 both paws rise with the claws open, frames 3 and 4 the claws slash down and forward crossing in an X, frames 5 to 8 he returns to the tucked air pose.",
    "g_ar_cabecada": "air strong attack, a diving headbutt. All frames in the air. Frame 1 tucked, frames 2 and 3 he arches back, frames 4 and 5 he dives head first down and forward, horns leading, arms back, frames 6 to 8 he tucks again.",
    "g_ar_joelho": "air light kick. All frames in the air. Frame 1 tucked, frames 2 and 3 one knee pulls up, frames 4 and 5 the knee drives forward and down hard, frames 6 to 8 he tucks again.",
    "g_ar_cascos": "air strong kick, a double hoof stomp. All frames in the air. Frame 1 tucked, frames 2 and 3 both legs pull up high, frames 4 and 5 both hooves stamp straight down and forward together, legs fully stretched, frames 6 to 8 he tucks again.",
    "g_cabecada_touro": "forward + strong punch, a charging overhead headbutt. Frame 1 beast stance, frames 2 and 3 he rears the head back and up, frames 4 and 5 he lunges a step forward and smashes the forehead and horns DOWN onto the opponent's head height, frames 6 to 8 he recovers into the beast stance.",
    "g_pisao": "forward + strong kick, a ground-cracking stomp. Frame 1 beast stance, frames 2 and 3 he lifts the front hoof very high with the knee at chest height, frames 4 and 5 he stamps it down hard on the ground in front of him, the whole body dropping with the weight, frames 6 to 8 he straightens back into the beast stance.",
    "g_bufada": "back + light punch, a close-range snort. Frame 1 beast stance, frames 2 and 3 he pulls the head back and the chest swells as he inhales, frames 4 and 5 he thrusts the muzzle forward with the nostrils flared wide and the mouth open, frames 6 to 8 back to the beast stance. Draw only the head motion, no fire.",
    "g_empinada": "back + light kick, rearing up. Frame 1 beast stance, frames 2 and 3 he rears up onto the hind legs with both front paws raised high, frames 4 and 5 standing tall on the hind hooves, paws up, frames 6 and 7 he crashes both front paws down forward, frame 8 beast stance.",
    # correntes: golpes 2 e 3 em uma folha, finalizador em outra
    "g_corrente_x": "two claw attacks in a row, 4 frames each. Frames 1 to 4: a backhand paw swipe coming back across the chest from the other side (frame 1 beast stance, frame 2 the paw crosses over, frame 3 the backhand swipe fully extended at chest height, frame 4 recovering). Frames 5 to 8: a rising claw uppercut from low to high (frame 5 the paw low near the knee, frames 6 and 7 the claws rip upward in front of the face, frame 8 recovering).",
    "g_rasga_couro": "finisher, the Rasga-Couro: both paws rip in an X. Frame 1 beast stance, frames 2 and 3 both paws rise high above the shoulders with the claws spread, frames 4 and 5 both paws slash down crossing in a big X in front of him, the body leaning into it, frames 6 and 7 the arms end low, crossed, frame 8 beast stance.",
    "g_corrente_y": "two horn attacks in a row, 4 frames each. Frames 1 to 4: a straight headbutt forward (frame 1 beast stance, frame 2 head pulled back, frame 3 forehead and horns thrust forward at chin height, frame 4 recovering). Frames 5 to 8: a sideways gore (frame 5 head turned to the side, frames 6 and 7 the head swings across sweeping the horns sideways at chest height, frame 8 recovering).",
    "g_chifre_ao_ceu": "finisher, the Chifre ao Céu: a launching gore. Frame 1 beast stance, frames 2 and 3 he crouches very low with the horns almost touching the ground, frames 4 and 5 he explodes upward, the horns thrusting high above his head, both hooves off the ground, frames 6 and 7 he comes down, frame 8 beast stance.",
    "g_corrente_a": "two low hoof kicks in a row, 4 frames each. Frames 1 to 4: a hoof kick to the knee (frame 1 beast stance, frame 2 hoof lifts, frame 3 hoof thrusts forward at knee height, frame 4 back). Frames 5 to 8: a scraping hoof (frame 5 hoof raised behind, frames 6 and 7 the hoof scrapes forward along the floor kicking dirt, frame 8 back to the stance).",
    "g_rabo_de_ferro": "finisher, the Rabo de Ferro: a full spin with the tail. Frame 1 beast stance, frames 2 and 3 he spins around showing his back, frames 4 and 5 the long tail whips in a wide low arc in front of him at ankle height, frames 6 and 7 he completes the spin, frame 8 beast stance.",
    "g_corrente_b": "two heavy kicks in a row, 4 frames each. Frames 1 to 4: a forward stomp (frame 1 beast stance, frame 2 knee high, frame 3 hoof stamping down in front, frame 4 back). Frames 5 to 8: a double buck (frame 5 he turns his back, frames 6 and 7 both hind legs kick backward toward the right at waist height, frame 8 he turns back).",
    "g_coice_do_diabo": "finisher, the Coice do Diabo: the biggest buck. Frame 1 beast stance, frames 2 and 3 he turns his back, plants both claws on the ground and gathers the hind legs under him, frames 4 and 5 both hind legs explode backward toward the right at chest height, fully stretched, hooves leading, mane and tail flying, frames 6 and 7 the legs drop, frame 8 he turns back into the beast stance.",
    # especiais
    "g_bufada_fogo": "special move, the fire snort projectile. Frame 1 beast stance, frames 2 and 3 he rears the head back, chest swelling, steam leaking from the nostrils, frames 4 and 5 he slams the head forward and down, nostrils flared at the ground in front of him, frames 6 and 7 he holds the pose snorting, frame 8 beast stance. Draw only the body, no fire.",
    "g_investida": "special move, the bull charge, an 8-frame sheet: frames 1 and 2 he scrapes a hoof on the ground with the head lowered, horns forward; frames 3 to 6 a running charge loop, body almost horizontal, head down, horns leading, hooves pounding in a gallop; frames 7 and 8 he skids to a stop and lifts the head.",
    "g_racha_chao": "special move, the ground-cracking double stomp. Frame 1 beast stance, frames 2 and 3 he rears up on the hind legs with both front hooves and paws high, frames 4 and 5 he crashes down with BOTH front paws and the front of the body slamming the ground, frames 6 and 7 he stays low with the claws on the ground, frame 8 he rises into the beast stance.",
    "g_chifrada_espiral": "special move, the rising spiral gore anti-air. Frame 1 low crouch, horns forward, frames 2 to 5 he spins upward head first like a drill, horns leading straight up, body stretched, rising higher each frame, frames 6 and 7 he falls with the hooves down, frame 8 landing in the crouch.",
    "g_poder": "special move pose for the long-range power (Estouro do Garanhão). Frame 1 beast stance, frames 2 and 3 he rears up onto the hind legs and neighs at the sky, both paws high, frames 4 and 5 he crashes down and throws both open paws forward at chest height, frames 6 and 7 he holds the pose, panting steam, frame 8 beast stance.",
    # super e agarrão em pé
    "g_furia_a": "super move, part one (the Fúria do Minotauro charge). Frames 1 and 2 he scrapes the hoof twice, head low; frames 3 to 6 a full-speed charge with the head down and the horns forward; frames 7 and 8 he jerks the head up hard, the horns lifting an invisible opponent above his head. No second person is shown.",
    "g_furia_b": "super move, part two. Frames 1 and 2 he holds the arms and head up as if carrying something on the horns; frames 3 and 4 he throws the head up, tossing it high; frames 5 and 6 he rears up on the hind legs; frames 7 and 8 he stamps both front hooves down hard on the ground in front of him.",
    "g_levanta_arremessa": "the standing grab, lift and throw. Frame 1 beast stance, frame 2 both claws reach forward and grab, frames 3 and 4 he lifts the (invisible) opponent overhead with both arms fully extended above the horns, frames 5 and 6 he arches back, frames 7 and 8 he hurls forward with both arms, roaring. No second person is shown.",
}

LUTADORES = {"gutto": (REF_GUTTO, CAB_GUTTO, GUTTO)}


def pedido(lutador, nome):
    _, cab, folhas = LUTADORES[lutador]
    return cab + ESTILO + folhas[nome]


if __name__ == "__main__":
    l = sys.argv[1] if len(sys.argv) > 1 else "gutto"
    if len(sys.argv) < 3:
        ref, _, folhas = LUTADORES[l]
        print(f"{l}: {len(folhas)} folhas, anexar {ref}")
        print("\n".join(folhas))
    else:
        print(pedido(l, sys.argv[2]))
