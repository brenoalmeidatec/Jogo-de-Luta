#!/usr/bin/env python3
"""Diabo Loiro demônio (#47, aprovado pelo Breno em 2026-11-15 19:23Z): o despertado do Hazak com TODOS os golpes
próprios, sem maleta, sem chapéu e sem sobretudo. Garras, investidas, voo e fogo das trevas; as asas são a aura.

Conceito: docs/diabo-44/conceito_demonio.png (também sprites/hazaki/quadros/folhas_diabo/d_conceito_demonio.png).

Este arquivo tem duas partes:
  1. As FOLHAS do demônio (8 quadros cada, grade 4x2) e os pedidos para o gerador de imagem:
       python3 ferramentas/diabo_demonio.py --fila            -> docs/diabo-44/demonio/fila.json + pedidos .txt
       python3 ferramentas/diabo_demonio.py --pedido NOME     -> imprime o pedido de uma folha
  2. A conversão das folhas e a ligação no jogo (estados próprios), mais abaixo.

As folhas ficam em sprites/hazaki/quadros/folhas_demonio/<nome>.png; os quadros convertidos (3x, RGBA, paleta do
Diabo) em sprites/hazaki/demonio/<nome>/NN.png.
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FOLHAS = RAIZ / "sprites/hazaki/quadros/folhas_demonio"
QUADROS = RAIZ / "sprites/hazaki/demonio"
DOCS = RAIZ / "docs/diabo-44/demonio"

QUEM = (
    "the BLOND DEMON from the attached concept (copy the front view): a young clean-shaven man turned into a wild "
    "demon, long wild blond mane swept back, glowing red eyes, a mad grin with sharp teeth, two big curved dark horns "
    "with ember-orange tips growing free from his head (NO hat), glowing ember cracks on the skin of the arms, chest "
    "and face, a torn sleeveless dark navy-purple pinstripe jacket open on a bare muscular chest, dark navy-purple "
    "pinstripe trousers ripped below the knees, a broken gold watch chain hanging at the waist, long arms ending in big "
    "BLACK CLAWS with ember-glowing tips, bare clawed demon feet, a thin dark devil tail with a spade tip")

MODELO = (
    "MODEL LOCK, true in all 8 frames: exactly two arms, two clawed hands, two legs, two clawed feet, one tail, two "
    "horns; NO hat, NO briefcase, NO coat, NO tie, NO shoes, NO wings (the wings are a separate effect, never draw "
    "them); hair always blond; same head size, shoulder width, arm length and leg length in all 8 frames; the jacket "
    "rags and the tail lag one frame behind the body. Art style: crisp hand-pixeled 1990s arcade fighting game sprite "
    "like the attached concept, hard pixel edges, no blur, no anti-aliasing, no gradients, no dithering, no noise; "
    "shading in 2-3 hard-edged flat planes per form; a clean 1-pixel colored outline; a clearly drawn face in every "
    "frame. Each figure stays fully inside its own grid cell, with a wide gap of magenta around it, and does not "
    "touch its neighbors. Flat solid magenta background (#FF00FF) everywhere, no black bars, no white bars, no grid "
    "lines, no shadow, no ground, no text, no numbers, no borders, no logos. No effects unless a frame asks for them "
    "(no wings, no aura, no speed lines, no sparks).")

PEDIDO = (
    "Generate ONE image with your image generation tool. Do not write code and do not edit any file. The attached "
    "picture is the approved concept of my own original fighting game character. Draw a SPRITE SHEET of {quem}: 8 "
    "frames in a grid of 2 rows and 4 columns on a flat magenta background, in a 3:2 landscape image, read left to "
    "right, top row first, every figure FACING RIGHT (toward the opponent), all at the same scale, a standing figure "
    "filling about 85% of the cell height, the feet of grounded frames on the same baseline of each row. {jeito} "
    "The 8 frames: {quadros} {modelo}")

JEITO = ("He never stands in a karate guard: he is hunched forward like a beast, shoulders high, claws open and "
         "ready.")

# nome -> (o que é, [8 quadros]). Cada quadro: a pose, curta e concreta. Ordem = prioridade de desenho.
FOLHAS_DEMONIO = {
    "parado": ("idle, swaying like a beast about to pounce (loop)", [
        "hunched forward, knees bent, claws open at hip height, weight on the back foot",
        "the body sways forward a little, shoulders rise, claws flex",
        "leans further forward, head low, grin wide, claws spread",
        "weight shifts to the front foot, front claw twitches up",
        "sways back to center, shoulders drop, tail curls",
        "leans back slightly, head tilts, claws loose",
        "shoulders rise again, breath out, front claw half closed",
        "back to the same pose as frame 1"]),
    "pe_maos": ("standing light claw swipe (frames 1-4) and standing heavy double X-claw (frames 5-8)", [
        "winds the front claw back at shoulder height",
        "swipes the front claw horizontally forward at chest height, arm fully stretched",
        "follow-through: the claw passes across the body, the shoulder turns",
        "returns to the hunched ready pose",
        "both arms raised high and crossed back behind the head, chest open",
        "both claws slash down and forward in an X in front of the chest, arms stretched",
        "the arms end crossed low in front of the hips, body leaning forward",
        "returns to the hunched ready pose"]),
    "pe_pes": ("standing knee strike (frames 1-4) and standing clawed-foot kick (frames 5-8)", [
        "lifts the front knee, leaning back",
        "drives the front knee forward and up at stomach height, claws pulled back",
        "the knee comes down, body leaning forward",
        "returns to the hunched ready pose",
        "chambers the front leg high, clawed toes spread",
        "kicks the front leg straight forward at chest height, clawed foot first, body leaning back",
        "the leg starts to come back, tail swings",
        "returns to the hunched ready pose"]),
    "cobranca_garras": ("Claw Charge: a fast forward dash with both claws stretched in front", [
        "crouches low, both claws pulled back, coiling like a spring",
        "explodes forward, body almost horizontal, mane flying back",
        "dashing: both claws stretched forward together, body low and horizontal",
        "dashing: same pose, the claws a bit higher",
        "the claws rake forward and up, end of the dash",
        "brakes, the back foot sliding, body upright",
        "turns the shoulders back, claws open",
        "back to the hunched ready pose"]),
    "agachado_maos": ("crouching light claw (frames 1-4) and crouching rising anti-air claw (frames 5-8)", [
        "crouched low, front claw pulled back near the floor",
        "swipes the front claw forward low, close to the floor",
        "follow-through low",
        "back to the crouch",
        "crouched, both claws down near the floor",
        "rises fast tearing upward with the front claw, arm stretched straight up above the head",
        "at the top, standing on the toes, claw high",
        "drops back into the crouch"]),
    "agachado_pes": ("crouching low tail sweep (frames 1-4) and crouching sliding claw sweep (frames 5-8)", [
        "crouched low, turning the hips, tail behind",
        "the tail whips forward along the floor in front of him",
        "the tail returns, body still low",
        "back to the crouch",
        "crouched, leaning back on the hands",
        "slides the front leg forward along the floor, clawed foot first",
        "the leg fully stretched along the floor, body low",
        "pulls back into the crouch"]),
    "ar_maos": ("jumping claw (frames 1-4) and jumping dive with both claws down (frames 5-8)", [
        "in the air, knees tucked, front claw back",
        "in the air, swipes the front claw forward",
        "in the air, follow-through",
        "in the air, knees tucked again",
        "in the air, both claws raised over the head",
        "in the air, body tilting down, both claws slashing down and forward",
        "in the air, diving down at an angle, claws first",
        "in the air, pulling up the knees"]),
    "ar_pes": ("jumping knee (frames 1-4) and jumping stomp with both clawed feet down (frames 5-8)", [
        "in the air, front knee pulled up",
        "in the air, knee driven forward",
        "in the air, legs relaxing",
        "in the air, knees tucked",
        "in the air, both knees pulled up high",
        "in the air, both clawed feet stomping down and forward together",
        "in the air, legs straight down, claws spread",
        "in the air, knees tucked again"]),
    "direcionais_a": ("Hell Hammer overhead (frames 1-4) and claw thrust forward (frames 5-8)", [
        "small hop, both claws joined high over the head",
        "at the top of the hop, claws behind the head",
        "lands, smashing both joined claws down in front of him",
        "recovers into the hunched ready pose",
        "leans back, front claw pulled back by the ear",
        "lunges half a step forward, front claw thrust straight ahead like a spear",
        "arm fully stretched, body low and forward",
        "back to the hunched ready pose"]),
    "direcionais_b": ("tail whip at long range (frames 1-4) and quick bite (frames 5-8)", [
        "turns the hips, the tail coiled behind",
        "spins half way, the tail whipping forward at chest height, very long",
        "the tail at full length in front, body turned",
        "back to the hunched ready pose",
        "pulls the head back, mouth closed",
        "snaps the head forward biting, mouth wide open with sharp teeth",
        "head forward, grin",
        "back to the hunched ready pose"]),
    "fins_maos": ("chain finishers: big upward rip that sends far (frames 1-4) and rip with dark fire (frames 5-8)", [
        "low, both claws down by the knees",
        "rips upward with both claws, body rising on the toes",
        "both arms high, body stretched",
        "back to the hunched ready pose",
        "front claw pulled back, the claw covered in black-red flames",
        "rips across with the flaming claw, black-red fire trail",
        "follow-through, flames on the claw",
        "back to the hunched ready pose"]),
    "fins_pes": ("chain finishers: spinning tail lash that knocks down (frames 1-4) and short flying double stomp "
                 "(frames 5-8)", [
        "spins with the back turned, tail out",
        "full spin, the tail lashing low and wide",
        "spin ends, tail in front",
        "back to the hunched ready pose",
        "jumps low and forward, knees up",
        "in the air, both clawed feet out in front",
        "lands stomping with both feet, knees bent",
        "back to the hunched ready pose"]),
    "bola_trevas": ("Ball of Darkness: throws a ball of dark fire from the claw (no ball drawn: it is a separate "
                    "sprite)", [
        "pulls the front claw back to the hip, body turned",
        "the claw cupped at the hip, gathering",
        "pushes the open claw forward at chest height",
        "arm fully stretched forward, open claw, body leaning in",
        "same, holding",
        "pulls the arm back",
        "half-way back to the ready pose",
        "back to the hunched ready pose"]),
    "voo": ("Infernal Flight: crouch, leap up and hover, then dive with the claws", [
        "crouches deep, claws on the floor",
        "leaps straight up, arms down",
        "rising in the air, knees up, claws open",
        "hovering in the air, legs hanging, claws open",
        "hovering, body tilting forward",
        "diving down and forward, both claws first, body straight",
        "diving, claws first",
        "lands in a crouch, claws on the floor"]),
    "rasgo": ("Rising Rip: anti-air that spins upward tearing with the claws", [
        "crouches, front claw low and back",
        "launches upward, front claw tearing up",
        "rising and spinning, back turned, claws out",
        "rising, facing front again, claw high above the head",
        "at the top, both claws high",
        "falling, knees up",
        "landing, knees bent",
        "back to the hunched ready pose"]),
    # básicos: 8 quadros cada, no MESMO papel quadro a quadro dos básicos do Hazak (o motor troca o quadro k do Hazak
    # pelo quadro k do demônio), mas com o corpo e o jeito do demônio, nunca a pose de karatê
    "anda": ("walking forward like a prowling beast (loop of 8)", [
        "hunched, front foot forward, claws low", "back foot passing, shoulders rolling",
        "back foot forward, claws low", "front foot passing", "front foot forward again, head low",
        "back foot passing, tail swaying", "back foot forward", "front foot passing"]),
    "recuo": ("quick hop backward, still facing right", [
        "hunched ready", "leans back", "crouches to hop back", "hopping back low, feet off the floor",
        "in the air going back, claws in front", "lands on the toes", "hunched ready", "hunched ready, breathing"]),
    "corrida": ("running forward on all fours like a beast (loop of 8)", [
        "low lunge, front claw reaching forward", "both feet off the floor, body stretched",
        "landing on the front foot, claws low", "back leg swinging forward", "low lunge again",
        "both feet off the floor, body stretched", "landing, tail whipping", "back leg swinging forward"]),
    "vira": ("turn around", [
        "facing right, hunched", "turning, shoulder toward the viewer", "facing the viewer, hunched",
        "facing the viewer", "facing the viewer, wide crouch, claws open", "same, breathing",
        "same, claws flex", "same"]),
    "pulo": ("jump, frame by frame", [
        "deep crouch to take off", "taking off, legs stretched down", "rising, knees bent, claws open",
        "top of the jump, tucked", "tucked, starting to fall", "falling, legs opening down",
        "legs straight down, about to land", "landing in a crouch"]),
    "agachado": ("crouch: standing then going down, then a crouch loop", [
        "hunched ready, standing", "bending the knees", "deep crouch on the toes, claws near the floor",
        "deep crouch, claws flex", "deep crouch, head low", "deep crouch, shoulders rise",
        "deep crouch, claws flex", "deep crouch"]),
    "defesa": ("standing block", [
        "hunched ready", "forearms coming up", "both forearms crossed in front of the face, claws up",
        "braced, pushed back", "leaning back, braced harder", "arms starting to lower", "hunched ready",
        "hunched ready"]),
    "defesa_baixa": ("crouching block", [
        "deep crouch", "forearms coming up, crouched", "crouched, forearms crossed low in front",
        "crouched, braced", "crouched, pushed back", "crouched, arms lowering", "deep crouch", "deep crouch"]),
    "apanha": ("getting hit hard and knocked down", [
        "hunched ready", "hit: head snapped back, mouth open", "staggering back, claws flailing",
        "falling backward", "falling diagonally", "almost horizontal in the air",
        "lying on the back on the floor", "lying flat on the back"]),
    "queda": ("lying on the floor after a knockdown", [
        "lying flat on the back", "bounce, body a bit off the floor", "lying on the back, tail flicks",
        "lying flat", "lying flat", "lying flat, claws twitch", "lying flat", "lying flat"]),
    "levanta": ("getting up from the floor", [
        "lying flat on the back", "rolling to the side, on an elbow", "sitting up, one claw on the floor",
        "on one knee, both claws on the floor, head low", "kneeling, rising", "half up, hunched",
        "up, hunched", "hunched ready"]),
    "vitoria": ("victory, mad laughter", [
        "stands tall, claws spread wide", "throws the head back roaring", "laughing, shoulders shaking",
        "claws raised high", "points at the viewer with a claw, grin", "licks a claw",
        "arms crossed, grin", "same, mane blowing"]),
    "provoca": ("taunt: beckons with a claw and laughs", [
        "hunched, front claw extended palm up", "curls the claw beckoning", "beckons again",
        "laughs with the head back", "laughs", "tongue out, grin", "shakes the head", "hunched ready"]),
    "intro": ("intro before the fight", [
        "crouched, claws on the floor, head down", "slowly rising, mane falling forward",
        "head up, red eyes glowing", "stands, cracks his neck", "slashes the air with a claw",
        "kicks the air with a clawed foot", "laughs", "hunched ready"]),
    "derrota_sirene": ("defeated", [
        "lying flat on the back", "lying, head turned", "on the knees, arms up in rage",
        "deep crouch, panting", "standing, head down, angry", "turning away", "running away, looking back",
        "running away"]),
    "parry_alto": ("high parry: deflects with a claw", [
        "hunched ready", "front claw snaps up", "front claw high, deflecting", "front claw high, flash of the claw tip",
        "claw coming down", "pointing up with a claw, grin", "flicking the claw", "hunched ready"]),
    "parry_baixo": ("low parry: deflects with a claw low", [
        "hunched ready", "drops low", "deep crouch, front claw low deflecting", "small hop, knees up",
        "lands wide, claws open", "claw low, flicking", "claw swipes the floor", "hunched ready"]),
    "juizo_a": ("super move part 1: launches flying, sinks the claws in and rises", [
        "crouches low, flames on both claws",
        "launches forward flying low, claws first",
        "flying forward horizontal, claws stretched",
        "both claws thrust forward hooking (the victim is a separate sprite)",
        "rising straight up, claws hooked in front of the chest",
        "rising, body turning",
        "high, spinning, claws in front",
        "spinning, upside down"]),
    "juizo_b": ("super move part 2: throws the victim down and lands roaring", [
        "upside down high, both claws throwing down",
        "follow-through of the throw, arms down",
        "falling feet first",
        "lands in a deep crouch, claws on the floor",
        "rises roaring, arms wide",
        "roaring, head back",
        "laughing",
        "back to the hunched ready pose"]),
}


SEGUINTE = (
    "Generate ONE new image with your image generation tool: another sprite sheet of the SAME demon, same model, same "
    "style, same scale and same layout as the previous sheet (8 frames, 2 rows by 4 columns, 3:2 landscape, flat solid "
    "magenta #FF00FF, every figure facing right, wide magenta gaps between figures, NO wings, no hat, no briefcase, "
    "no effects unless a frame asks for them, the same MODEL LOCK). IMPORTANT: the poses must be clearly DIFFERENT from "
    "frame to frame, big readable poses like a 1990s arcade fighting game, the limbs must change a lot. This sheet is "
    "the {o_que}. {jeito} The 8 frames: "
    "{quadros}")


def pedido_seguinte(nome):
    """Pedido curto para o mesmo chat (o modelo e o estilo já estão na conversa)."""
    o_que, quadros = FOLHAS_DEMONIO[nome]
    texto = " ".join(f"{i + 1}) {q}." for i, q in enumerate(quadros))
    return SEGUINTE.format(o_que=o_que, jeito=JEITO, quadros=texto)


def pedido(nome):
    o_que, quadros = FOLHAS_DEMONIO[nome]
    texto = " ".join(f"{i + 1}) {q}." for i, q in enumerate(quadros))
    return PEDIDO.format(quem=QUEM, jeito=f"This sheet is the {o_que}. {JEITO}", quadros=texto, modelo=MODELO)


def fila():
    DOCS.mkdir(parents=True, exist_ok=True)
    pedidos = [{"folha": n, "pronta": (FOLHAS / f"{n}.png").exists(), "prompt": pedido(n)} for n in FOLHAS_DEMONIO]
    (DOCS / "fila.json").write_text(json.dumps(pedidos, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(pedidos)} folhas, {sum(p['pronta'] for p in pedidos)} prontas")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--fila" in args:
        fila()
    elif "--pedido" in args:
        print(pedido(args[args.index("--pedido") + 1]))
    elif "--seguinte" in args:
        print(pedido_seguinte(args[args.index("--seguinte") + 1]))
