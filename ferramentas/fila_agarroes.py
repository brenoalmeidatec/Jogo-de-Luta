#!/usr/bin/env python3
"""Fila das folhas dos agarrões com animação própria (issue #45, pedido do Breno de 2026-11-15) para o ChatGPT.

Cada lutador ganha 4 folhas por forma (base e despertado, prefixo e_):
  agarrao_pe       agarrão em pé (800 -> 810)
  agarrao_baixo    agarrão no oponente agachado (840 -> 841)
  agarrao_comando  agarrão de comando, colado (830 -> 831)
  vitima           ele sendo agarrado: preso, apanhando alto e baixo, arremessado e caindo (ações 5940 a 5944)

Formato fixo das folhas de agarrão (o ferramentas/agarrao_mk.py, `padrao`, conta com ele):
  1 alcança (em pé), 2 segura, 3 prepara a pancada A, 4 bate A, 5 prepara a pancada B, 6 bate B,
  7 prepara o arremesso, 8 arremessa. A sequência no jogo é A, B, A e o arremesso.
Folha de vítima: 1 guarda (em pé), 2 preso, 3 e 4 apanha em cima, 5 e 6 apanha embaixo, 7 arremessado, 8 caindo.
O oponente nunca aparece na folha: as mãos seguram um oponente invisível (ele é o outro sprite no jogo).

Saída: sprites/<l>/quadros/folhas_agarrao/<nome>.png (1536x1024, magenta). A referência anexada é a folha de
agarrão que o lutador já tem no jogo (folhas_arcade/agarrao.png ou e_agarrao.png), para manter cara, roupa e escala.

  python ferramentas/fila_agarroes.py                 lista a fila e o que já existe
  python ferramentas/fila_agarroes.py ck agarrao_pe   imprime o pedido de uma folha
  python ferramentas/fila_agarroes.py --json          a fila inteira em JSON (para a aba do ChatGPT)
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LUTADORES = ("ck", "gutto", "pengaro")

CABECA = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached sprite sheet shows the exact character and art style to keep: {quem} Keep the same face, hair, body, outfit, colors and the same size as in the attached sheet. Hand-drawn 1990s arcade fighting game pixel sprite (16-bit), clean colored outline, flat cel shading in 2-3 hard-edged tones, no gradients, never a 3D render.

Layout: one single row of 8 frames in 8 equal-width cells, wide image (1536x1024), side view, always facing right, feet on the same ground line, every figure at the same scale. Each figure stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, with no shadow, no ground, no text, no numbers, no borders and no effects.

This is a GRAB (throw) animation. Only HE is drawn: the opponent is INVISIBLE (he is another sprite in the game). His hands grip the invisible opponent in the empty space in front of him, as if a person of the same height were standing there. No second person, no silhouette, no ghost.

Anatomy check for every frame: exactly two arms and two legs, both hands visible, elbows and knees bend the natural way, no extra or missing limbs.

Fighting-game timing: each hit has a clear wind-up pose and then a contact pose with the striking limb fully extended; the grip hand keeps holding between hits.

ANIMATION: """

VITIMA = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached sprite sheet shows the exact character and art style to keep: {quem} Keep the same face, hair, body, outfit, colors and the same size as in the attached sheet. Hand-drawn 1990s arcade fighting game pixel sprite (16-bit), clean colored outline, flat cel shading in 2-3 hard-edged tones, no gradients, never a 3D render.

Layout: one single row of 8 frames in 8 equal-width cells, wide image (1536x1024), side view, always facing right, every figure at the same scale. Each figure stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, with no shadow, no ground, no text, no numbers, no borders and no effects.

This sheet shows HIM BEING GRABBED by an invisible opponent standing in front of him (to the right). Only he is drawn, no second person, no hands of the opponent.

Frames: 1 his normal fighting guard, standing. 2 grabbed by the collar and pulled forward off balance: torso leaning toward the right, arms flailing, feet dragging, surprised face. 3 hit in the face while held: head snapped back, eyes shut, mouth open, arms loose. 4 still held, dazed, head hanging, knees bending. 5 hit in the belly while held: doubled over forward, both hands on the stomach, mouth open. 6 still held, bent over in pain, one knee buckling. 7 thrown: his whole body flying backward through the air, horizontal, back toward the ground, arms and legs flung up. 8 falling: upside down, head toward the ground, about to crash, legs in the air. {extra}"""

QUEM = {
    "ck": ("CK, the cheeky street boxer: young Black man, slim athletic build, short black hair, thin mustache and goatee, white polo shirt with green collar, black cap, black-and-white wavy basketball shorts, white sneakers, red boxing gloves with white wraps.",
           "CK in RATAO MODE (awakened): same young Black man, short bleached platinum hair, mirrored sunglasses pushed up on the head, a lit joint between the lips, thick gold chain, patterned navy-and-white open shirt over a white tank top, board shorts, white socks with dark slides, white hand wraps, a broken green glass bottle always held by the neck in the near (front) hand."),
    "gutto": ("Gutto, the Muay Thai fighter: deep dark brown skin, thick mustache, short curly black hair, strong muscular build, shirtless, black satin Muay Thai trunks with a white waistband, white hand wraps, rope armbands on both biceps, barefoot.",
              "Gutto in his AWAKENED horse-beast form: a huge hunched horse-man, reddish-brown muscular body with dark stripe markings, a horse head with a long snout, small horns, glowing eyes and a wild long black mane down the back, a black horse tail, black satin Muay Thai trunks with a white waistband, rope armbands, dark furry hands and legs ending in black hooves."),
    "pengaro": ("Pengaró, the drunk capoeirista: young Black man with dark brown skin, short black high-top fade haircut with a shaved line, very muscular and shirtless, white capoeira pants with green and yellow side stripes, yellow cord belt, teal sash, dark green shin guard, barefoot. In EVERY frame he holds a whisky bottle (amber glass, black cap, plain cream label without text) by the neck in his back hand and never lets go.",
                "Pengaró in his ENDIABRADO (awakened demon) form: dark violet-brown skin, long wild black dreadlocks standing up like flames, glowing eyes, muscular and shirtless with a dark open vest, gold bands on the forearms and biceps, torn black-and-purple baggy pants with a gold-and-purple rope belt and hanging gold tassels, broken iron shackles with chain links on wrists and ankles, barefoot, both hands free (no bottle)."),
}

# nome -> movimento, por lutador. Formato das folhas de agarrão: ver o docstring.
MOVIMENTOS = {
    "ck": {
        "agarrao_pe": "Gola na Mao, a dirty-boxing collar grab. 1 standing upright in his boxing guard, the front glove reaching forward. 2 the front glove grips the invisible opponent's collar at chest height and pulls it in, the back glove up. 3 still gripping, the back glove cocks back by the ear. 4 a short hook punch to the face at head height, glove fully extended. 5 still gripping, he dips the knees and drops the back glove low. 6 a hook to the liver at belly height. 7 both gloves grip the collar and he leans back, loading. 8 he shoves the opponent away with both gloves fully extended forward at chest height, back leg pushing.",
        "agarrao_baixo": "Abaixa Ai, grabbing a CROUCHING opponent, so his hands work at waist height. 1 standing upright in his boxing guard, bending slightly forward. 2 the front glove grabs the invisible crouching opponent's head at waist height. 3 still holding the head down, the back knee chambers. 4 a knee strike down into the head at waist height. 5 still holding, the back glove raised high above his head. 6 a hammer fist chopping down at waist height. 7 both gloves pull the head up, leaning back. 8 a rising uppercut at chest height that lifts the opponent away, rising on his toes.",
        "agarrao_comando": "Saideira, a street neck grab. 1 standing upright in his boxing guard, the front glove reaching. 2 the front glove grabs the back of the invisible opponent's neck at chest height and pulls the head down. 3 still holding, the back glove raised. 4 a slap on the back of the neck at chest height. 5 still holding, the front foot pulls back, loading. 6 a toe kick (bicuda) to the belly at waist height. 7 he lets go and chambers the kicking leg high. 8 a big front push kick at chest height that launches the opponent, leaning back, gloves up.",
    },
    "gutto": {
        "agarrao_pe": "Muay Thai plum clinch. 1 standing upright in his Muay Thai guard, both hands reaching forward. 2 both hands lock behind the invisible opponent's neck at chest height and pull it down (plum clinch). 3 still in the clinch, the back knee pulls back. 4 a knee strike driving up into the belly at waist height. 5 still in the clinch, he pulls the head lower and chambers the knee again. 6 a knee strike into the face at chest height. 7 he lets go with both hands and pulls the knee to his chest. 8 a teep push kick, the sole thrusting straight forward at chest height, torso leaning back.",
        "agarrao_baixo": "grabbing a CROUCHING opponent, so his hands work at waist height. 1 standing upright in his Muay Thai guard, bending slightly forward. 2 both hands grab the invisible crouching opponent's head at waist height. 3 still holding, the back knee chambers. 4 a knee strike into the head at waist height. 5 still holding with one hand, the other elbow raised high. 6 a downward elbow chop at waist height. 7 both hands pull the head up. 8 he twists and hurls the opponent away to the front with both arms extended at chest height.",
        "agarrao_comando": "Clinch e Joelhada, a jumping clinch combo. 1 standing upright in his Muay Thai guard, both hands reaching. 2 plum clinch: both hands behind the invisible opponent's neck at chest height. 3 the right knee chambers. 4 a knee to the ribs at waist height. 5 he switches and chambers the left knee. 6 a knee to the ribs at waist height. 7 still clinching, he jumps up pulling the head down. 8 a flying knee into the face at chest height, his body in the air, both fists up.",
    },
    "pengaro": {
        "agarrao_pe": "a drunk capoeira collar grab. 1 standing upright in his capoeira ginga stance, the free front hand reaching forward. 2 the free hand grips the invisible opponent's collar at chest height. 3 still gripping, the whisky bottle is raised behind his head. 4 the bottle bonks down on the head at head height (the bottle does not break). 5 still gripping, he lifts the knee. 6 a knee strike to the belly at waist height. 7 he lets go and spins, loading the kick. 8 a meia-lua spinning kick, the straight leg sweeping at chest height, the bottle still in the back hand.",
        "agarrao_baixo": "grabbing a CROUCHING opponent, so his free hand works at waist height. 1 standing upright in his ginga stance, bending slightly forward. 2 the free hand grabs the invisible crouching opponent's head at waist height. 3 still holding, the whisky bottle raised high. 4 the bottle bonks the head at waist height (the bottle does not break). 5 still holding, he lifts the heel. 6 a heel stomp kick down at waist height. 7 he pulls the head up and leans back. 8 a front push kick (bencao) at chest height that sends the opponent away, the bottle still in the back hand.",
        "agarrao_comando": "Martelo e Garrafada. 1 standing upright in his ginga stance, the free hand reaching. 2 the free hand grips the invisible opponent's collar at chest height. 3 still gripping, the knee lifts. 4 a knee strike to the belly at waist height. 5 still gripping, the whisky bottle raised behind his head. 6 the bottle smashes on the head at head height. 7 he lets go and pivots, loading the kick. 8 a martelo roundhouse kick at head height, the leg fully extended, the bottle still in the back hand.",
    },
}

EXTRA_VITIMA = {
    "pengaro": "The whisky bottle stays in his back hand in all 8 frames.",
    "ck": "His red gloves stay on in all 8 frames." ,
    "gutto": "",
}

NOMES = ("agarrao_pe", "agarrao_baixo", "agarrao_comando", "vitima")


def referencia(lutador, desperto):
    # Pengaró: a folhas_arcade/agarrao.png é o desenho ANTIGO (o Breno barrou na #45); a referência é a faixa da arte
    # atual (quadros_arcade_hd), montada em docs/agarroes-45/ref/
    if lutador == "pengaro":
        return f"docs/agarroes-45/ref/pengaro{'_e' if desperto else ''}.png"
    return f"sprites/{lutador}/quadros/folhas_arcade/{'e_' if desperto else ''}agarrao.png"


SEM_GARRAFA = (  # o Pengaró endiabrado não leva a garrafa: as pancadas de garrafa viram pancadas de mão
    ("the whisky bottle is raised behind his head", "the back fist is raised behind his head"),
    ("the whisky bottle raised behind his head", "the back fist raised behind his head"),
    ("the whisky bottle raised high", "the back fist raised high"),
    ("the bottle bonks down on the head at head height (the bottle does not break)", "a hammer fist smashes down on the head at head height"),
    ("the bottle bonks the head at waist height (the bottle does not break)", "a hammer fist smashes the head at waist height"),
    ("the bottle smashes on the head at head height", "a clawed hammer fist smashes on the head at head height"),
    (", the bottle still in the back hand", ""),
)


def sem_garrafa(texto):
    for a, b in SEM_GARRAFA:
        texto = texto.replace(a, b)
    assert "bottle" not in texto, texto
    return texto


def pedido(lutador, nome):
    desperto = nome.startswith("e_")
    base = nome[2:] if desperto else nome
    quem = QUEM[lutador][desperto]
    if lutador == "ck" and desperto:
        quem += " He keeps the broken bottle in the near hand in every frame; the other hand does the grabbing."
    if base == "vitima":
        texto = VITIMA.format(quem=quem, extra=EXTRA_VITIMA[lutador])
    else:
        texto = CABECA.format(quem=quem) + MOVIMENTOS[lutador][base]
    return texto.replace("’", "'")


GEMINI = """Create ONE image. Do not write code.

Use the attached sprite sheet as the exact character and art style: {quem} Same face, outfit, colors and proportions, hard-edged 1990s arcade pixel art with flat colors.

Exactly 8 figures of him, no more, no less, arranged in a grid of 2 rows x 4 columns (frames 1-4 on the top row, 5-8 on the bottom row), each figure centered in its own cell, all at the same scale, full body, side view facing right, flat magenta background (#FF00FF), no text, no numbers, no ground, no effects. Only he is drawn: {papel}

Each frame must show a clearly DIFFERENT pose: {movimento}"""

PAPEL_AGARRA = ("the opponent he grabs is INVISIBLE, so his hands grip empty space right in front of him, at the height said "
                "in each frame. No second person.")
PAPEL_VITIMA = "he is being grabbed by an INVISIBLE opponent standing in front of him (to the right). No second person."


def pedido_gemini(lutador, nome):
    """Pedido curto para o Gemini, que prefere grade 2x4 (agarrao_folhas.py --salvar transforma em fileira)."""
    desperto = nome.startswith("e_")
    base = nome[2:] if desperto else nome
    quem = QUEM[lutador][desperto]
    sem = lutador == "pengaro" and desperto
    if base == "vitima":
        mov = VITIMA.split("Frames: ", 1)[1].split(" {extra}")[0] + " " + ("" if sem else EXTRA_VITIMA[lutador])
        return GEMINI.format(quem=quem, papel=PAPEL_VITIMA, movimento=mov.strip())
    mov = MOVIMENTOS[lutador][base]
    return GEMINI.format(quem=quem, papel=PAPEL_AGARRA, movimento=sem_garrafa(mov) if sem else mov)


def destino(lutador, nome):
    return RAIZ / f"sprites/{lutador}/quadros/folhas_agarrao/{nome}.png"


def fila():
    out = []
    for desperto in (False, True):
        for l in LUTADORES:
            for n in NOMES:
                nome = ("e_" if desperto else "") + n
                out.append({"lutador": l, "nome": nome, "referencia": referencia(l, desperto),
                            "destino": str(destino(l, nome).relative_to(RAIZ)), "prompt": pedido(l, nome),
                            "feita": destino(l, nome).exists()})
    return out


def main():
    a = sys.argv[1:]
    if a == ["--json"]:
        print(json.dumps(fila(), ensure_ascii=False, indent=1))
    elif len(a) == 2:
        print(pedido(*a))
    elif len(a) == 3 and a[0] == "--gemini":
        print(json.dumps(pedido_gemini(a[1], a[2]), ensure_ascii=False))
    else:
        for f in fila():
            print(("ok   " if f["feita"] else "falta") + f"  {f['lutador']:8} {f['nome']}")


if __name__ == "__main__":
    main()
