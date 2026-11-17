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
import os
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
    # agarrões (#45): quadro k no mesmo papel do quadro k das folhas agarrao_* do Hazak (agarrao_mk.PROPRIOS["hazaki"]);
    # pedidos da thread dos agarrões (project-files agarroes-45/diabo-demonio-agarroes.md); fogo vem do diabo_loiro
    "agarrao_abraco": ("Claws on the Neck: standing grab and overhead slam of an invisible opponent, no effects", [
        "hunched beast stance, both clawed hands reaching forward at chest height, fingers spread",
        "both claws clamp the invisible opponent's neck at chest height and pull him close, fangs bared",
        "still gripping with one claw, the other claw draws back by the ear, talons open",
        "the free claw rakes across at chest height, arm fully swept through",
        "he twists his whole body and heaves both claws up above his head, lifting the invisible opponent overhead, "
        "spine arched back, head visible above the shoulders",
        "he slams both claws down behind his back over his shoulder toward the ground, body bent forward, tail "
        "whipping up",
        "crouched low after the slam, claws on the ground, glancing back",
        "rising into his hunched beast stance, snarling, claws open at his sides"]),
    "agarrao_perna": ("Drag to Hell: low grab of a crouching invisible opponent by the ankle, no effects", [
        "hunched beast stance, looking down",
        "he drops low to one knee, one clawed hand reaching down to ground level in front of him",
        "the claw grips the invisible opponent's ankle at ground level, the other claw braced on the floor",
        "still gripping, he yanks the claw back toward his hip, dragging, body leaning back",
        "he springs up to full height and swings the claw high above his head, lifting the invisible leg",
        "he slams the claw down to the ground in front of him at ground level, bent over, the leg fully extended",
        "crouched, claws on the ground, panting, tail curled",
        "rising halfway, one claw on the knee, grinning"]),
    "agarrao_cutucao": ("Grip of Darkness: command grab, holds the invisible opponent by the throat and stabs, "
                        "no effects", [
        "hunched beast stance, the front claw reaching forward at chest height",
        "the front claw clamps the invisible opponent's throat at chest height, the arm locked, the other claw "
        "cocked low",
        "still holding the throat, the back claw draws back at waist height, talons together like a spear",
        "the back claw stabs forward into the belly at waist height, arm fully extended",
        "still holding, the back claw pulls back again, higher, by the shoulder",
        "the back claw stabs forward into the chest at chest height",
        "he lets go and blasts both open claws forward at chest height, palms out, shoving, body leaning in",
        "standing tall, one claw on his hip, the other pointing forward, laughing with his head thrown back"]),
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


# ---------------------------------------------------------------------------------------------------------------------
# parte 2: folha -> quadros do jogo (sprites/hazaki/diabo_terno/m_<folha>/NN.png)
# ---------------------------------------------------------------------------------------------------------------------
# O demônio é curvado e tem chifres: em pé (mediana do parado) ele fica com 1,08 da altura do Hazak em pé (324 px no
# 3x). O Gemini desenha todas as folhas na mesma escala (mesma grade, "same scale"), então a escala da folha do parado
# vale para todas.
ALTURA = 1.08
SAIDA = RAIZ / "sprites/hazaki/diabo_terno"


def _figuras(nome):
    sys.path.insert(0, str(RAIZ / "ferramentas"))
    import converter_hazaki as ch
    figs = ch.figuras(FOLHAS / f"{nome}.png")
    assert all(q is not None for q in figs), f"{nome}: figura faltando na folha"
    return figs


def escala():
    from PIL import Image
    hz = Image.open(RAIZ / "sprites/hazaki/quadros_arcade_hd/parado/00.png").getbbox()
    alvo = ALTURA * (hz[3] - hz[1])
    alturas = sorted(q.height for q in _figuras("parado"))
    return alvo / alturas[len(alturas) // 2]


def converter(nome, e=None):
    import subprocess
    import numpy as np
    from PIL import Image
    import converter_hazaki as ch
    import diabo_terno as dt
    e = e or escala()
    destino = SAIDA / f"m_{nome}"
    destino.mkdir(parents=True, exist_ok=True)
    for i, q in enumerate(_figuras(nome)):
        tres = ch.seco(q.resize((max(1, round(q.width * e)), max(1, round(q.height * e))), Image.LANCZOS))
        Image.fromarray(dt.quantizar(dt.chefao(np.array(tres)))).save(destino / f"{i:02d}.png", optimize=True)
    subprocess.run([sys.executable, str(RAIZ / "ferramentas/pixel/cores.py"), "diabo", f"m_{nome}", "--consertar"],
                   cwd=RAIZ, check=True, capture_output=True)
    print(f"m_{nome}: escala {e:.4f}")


def contato(saida, nomes):
    """Hazak (em cima, só nas folhas que existem no Hazak) e demônio (embaixo), no tamanho do jogo 3x."""
    from PIL import Image
    w, h = 340, 420
    tela = Image.new("RGB", (w * 8, h * 2 * len(nomes)), (110, 112, 118))
    for j, nome in enumerate(nomes):
        for i in range(8):
            hz = RAIZ / "sprites/hazaki/quadros_arcade_hd" / nome / f"{i:02d}.png"
            if hz.exists():
                a = Image.open(hz).convert("RGBA")
                a = a.crop(a.getbbox())
                tela.paste(a, (i * w + (w - a.width) // 2, (2 * j + 1) * h - a.height), a)
            d = SAIDA / f"m_{nome}" / f"{i:02d}.png"
            if d.exists():
                b = Image.open(d).convert("RGBA")
                tela.paste(b, (i * w + (w - b.width) // 2, (2 * j + 2) * h - b.height), b)
    tela.save(saida)
    print(saida)


# ---------------------------------------------------------------------------------------------------------------------
# parte 3: golpes próprios no jogo (estados 4200-4699, sprites no grupo 60000 + estado)
# ---------------------------------------------------------------------------------------------------------------------
# Básicos do Hazak -> folha do demônio de mesmo papel (o diabo_terno troca o quadro k pelo quadro k da pasta m_*).
BASICOS = {"parado": "parado", "anda": "anda", "recuo": "recuo", "corrida": "corrida", "vira": "vira", "pulo": "pulo",
           "agachado": "agachado", "defesa": "defesa", "defesa_baixa": "defesa_baixa", "apanha": "apanha",
           "queda": "queda", "levanta": "levanta", "vitoria": "vitoria", "provoca": "provoca", "intro": "intro",
           "derrota_sirene": "derrota_sirene", "parry_alto": "parry_alto", "parry_baixo": "parry_baixo",
           "despertar_pedido": "parado", "vitima_agarrado": "apanha", "vitima_arremessado": "queda",
           "agarrao_abraco": "agarrao_abraco", "agarrao_perna": "agarrao_perna", "agarrao_cutucao": "agarrao_cutucao"}
# Pancadas extras da porrada dos agarrões (agarrao_mk.HAZAK_EXTRAS): desenhos de golpes do Hazak que, na forma, saem
# como um quadro de preparo ou de batida de uma folha do demônio. Só os agarrões mostram esses desenhos na forma (os
# golpes do Hazak estão travados pelo bloquear_base). (folha do Hazak, quadro) -> (folha do demônio, quadro).
QUADROS_EXTRAS = {
    ("jab_duplo", 1): ("pe_maos", 0), ("jab_duplo", 2): ("pe_maos", 1),        # arranhão
    ("jab_duplo", 4): ("pe_maos", 0), ("jab_duplo", 5): ("pe_maos", 1),        # arranhão de novo
    ("cruzado", 2): ("pe_pes", 0), ("cruzado", 5): ("pe_pes", 1),              # joelhada
    ("cotovelada", 2): ("pe_maos", 4), ("cotovelada", 5): ("pe_maos", 5),      # garra cruzada (de cima)
    ("soco_reto", 2): ("pe_pes", 4), ("soco_reto", 4): ("pe_pes", 5),          # coice com garra
    ("baixo_soco", 2): ("agachado_maos", 0), ("baixo_soco", 3): ("agachado_maos", 1),
    ("baixo_soco", 4): ("agachado_maos", 2),                                   # arranhão baixo e o embalo
    ("tapa_costas", 3): ("pe_maos", 4), ("tapa_costas", 5): ("pe_maos", 5),    # garra cruzada
}
GRUPO = 60000

# peso -> (pausa, faísca, som do acerto, deslize, tempo de atordoado, empurrão)
PESO = {"Light": (7, "S9200", "S51,0", 5, 15, -2.5), "Medium": (11, "S9207", "S51,1", 8, 18, -4),
        "Heavy": (13, "S9207", "S51,2", 10, 20, -6)}

# Tempos pela seção 8.3 das regras (docs/regras-dos-lutadores.md): até encostar, fraco 3-5 ticks, forte 7-10,
# finalizador 10-14; congela 7, 11 e 14 no contato.
# Cada golpe: folha e quadros (de 0 a 7), ticks por quadro (-1 = segura até cair no chão), quadros com caixa de golpe,
# de onde sai a ponta (frente, cima, baixo), dano, peso, guarda (MA, L, HA), tipo do chão (High, Low, Trip), avanço
# [(tick, vel x)], cai (derruba), voa (vel x, y de quem cai longe), fogo (fica queimando) e sobe (antiaéreo).
# A lista é a proposta aprovada pelo Breno na #47 (comentário 6898251397).
GOLPES = {
    # 16 normais: em pé
    4200: dict(nome="Arranhão", folha="pe_maos", q=[0, 1, 2, 3], t=[3, 3, 4, 5], ativo=[1], dano=25, peso="Light"),
    4201: dict(nome="Garra Cruzada", folha="pe_maos", q=[4, 5, 6, 7], t=[7, 4, 6, 10], ativo=[1], dano=62,
               peso="Medium", avanca=[(2, 1.5), (10, 0)]),
    4202: dict(nome="Joelhada Selvagem", folha="pe_pes", q=[0, 1, 2, 3], t=[4, 4, 5, 7], ativo=[1], dano=32,
               peso="Light"),
    4203: dict(nome="Coice com Garra", folha="pe_pes", q=[4, 5, 6, 7], t=[8, 5, 6, 10], ativo=[1], dano=72,
               peso="Heavy"),
    # agachado
    4400: dict(nome="Arranhão Baixo", folha="agachado_maos", q=[0, 1, 2, 3], t=[3, 3, 4, 5], ativo=[1], dano=22,
               peso="Light", tipo="C", chao="Low"),
    4401: dict(nome="Garra Subindo", folha="agachado_maos", q=[4, 5, 6, 7], t=[7, 4, 7, 9], ativo=[1, 2], dano=60,
               peso="Medium", tipo="C", ponta="cima", sobe=True),
    4402: dict(nome="Rabo Rasteiro", folha="agachado_pes", q=[0, 1, 2, 3], t=[4, 4, 5, 7], ativo=[1], dano=30,
               peso="Light", tipo="C", guarda="L", chao="Low"),
    4403: dict(nome="Varrida de Garras", folha="agachado_pes", q=[4, 5, 6, 7], t=[8, 4, 8, 10], ativo=[1, 2], dano=65,
               peso="Heavy", tipo="C", guarda="L", chao="Trip", cai=True),
    # no ar (o último quadro segura até cair no chão; quem pousa é o motor, estado 52)
    4600: dict(nome="Garra no Ar", folha="ar_maos", q=[0, 1, 2, 3], t=[3, 4, 5, -1], ativo=[1], dano=28,
               peso="Light", tipo="A", guarda="HA"),
    4601: dict(nome="Mergulho de Garras", folha="ar_maos", q=[4, 5, 6, 7], t=[7, 4, 6, -1], ativo=[1, 2], dano=55,
               peso="Medium", tipo="A", guarda="HA"),
    4602: dict(nome="Joelhada Aérea", folha="ar_pes", q=[0, 1, 2, 3], t=[3, 4, 5, -1], ativo=[1], dano=30,
               peso="Light", tipo="A", guarda="HA"),
    4603: dict(nome="Pisão de Garras", folha="ar_pes", q=[4, 5, 6, 7], t=[7, 4, 6, -1], ativo=[1, 2], dano=58,
               peso="Medium", tipo="A", guarda="HA", ponta="baixo"),
    # direcionais
    4210: dict(nome="Martelo Infernal", folha="direcionais_a", q=[0, 1, 2, 3], t=[5, 5, 4, 10], ativo=[2], dano=55,
               peso="Medium", guarda="HA", avanca=[(2, 1.2), (11, 0)]),
    4211: dict(nome="Estocada de Garra", folha="direcionais_a", q=[4, 5, 6, 7], t=[7, 3, 5, 9], ativo=[1, 2], dano=50,
               peso="Medium", avanca=[(2, 5), (8, 0)]),
    4212: dict(nome="Chicote de Rabo", folha="direcionais_b", q=[0, 1, 2, 3], t=[7, 4, 6, 10], ativo=[1, 2], dano=48,
               peso="Medium"),
    4213: dict(nome="Mordida", folha="direcionais_b", q=[4, 5, 6, 7], t=[3, 3, 4, 6], ativo=[1], dano=30,
               peso="Light"),
    # 4 correntes: o 2º e o 3º saem no contato do anterior, o finalizador só com os 3 primeiros acertando de verdade
    4301: dict(nome="Fúria das Garras 2", folha="pe_maos", q=[2, 1, 3], t=[3, 3, 5], ativo=[1], dano=26,
               peso="Light", avanca=[(1, 2.5), (7, 0)]),
    4302: dict(nome="Fúria das Garras 3", folha="pe_maos", q=[0, 1, 2, 3], t=[3, 3, 4, 6], ativo=[1], dano=28,
               peso="Light", avanca=[(1, 2.5), (7, 0)]),
    4303: dict(nome="Fúria das Garras: rasgo", folha="fins_maos", q=[0, 1, 2, 3], t=[10, 4, 6, 12], ativo=[1, 2],
               dano=70, peso="Heavy", cai=True, voa=(-8, -7), avanca=[(1, 2.5), (7, 0)]),
    4311: dict(nome="Dilacerar 2", folha="pe_maos", q=[4, 5, 6, 7], t=[7, 4, 5, 8], ativo=[1], dano=40,
               peso="Medium", avanca=[(1, 2.5), (7, 0)]),
    4312: dict(nome="Dilacerar 3", folha="pe_pes", q=[0, 1, 2, 3], t=[4, 4, 5, 7], ativo=[1], dano=34,
               peso="Light", avanca=[(1, 4), (8, 0)]),
    4313: dict(nome="Dilacerar: rasgo de fogo", folha="fins_maos", q=[4, 5, 6, 7], t=[11, 4, 6, 12], ativo=[1, 2],
               dano=75, peso="Heavy", cai=True, fogo=True, avanca=[(1, 2.5), (7, 0)]),
    4321: dict(nome="Dança do Rabo 2", folha="direcionais_b", q=[0, 1, 2, 3], t=[7, 4, 5, 8], ativo=[1], dano=32,
               peso="Medium", avanca=[(1, 4), (8, 0)]),
    4322: dict(nome="Dança do Rabo 3", folha="fins_pes", q=[0, 1, 2], t=[3, 4, 6], ativo=[1], dano=30,
               peso="Light", guarda="L", chao="Low", avanca=[(1, 2.5), (7, 0)]),
    4323: dict(nome="Dança do Rabo: chicotada", folha="fins_pes", q=[0, 1, 2, 3], t=[10, 4, 6, 12], ativo=[1],
               dano=68, peso="Heavy", guarda="L", chao="Trip", cai=True, avanca=[(1, 2.5), (7, 0)]),
    4331: dict(nome="Pisoteio 2", folha="pe_pes", q=[4, 5, 6, 7], t=[7, 4, 5, 8], ativo=[1], dano=40,
               peso="Medium", avanca=[(1, 2.5), (7, 0)]),
    4332: dict(nome="Pisoteio 3", folha="pe_pes", q=[0, 1, 2, 3], t=[4, 4, 5, 7], ativo=[1], dano=32,
               peso="Light", avanca=[(1, 4), (8, 0)]),
    4333: dict(nome="Pisoteio: pisão voador", folha="fins_pes", q=[4, 5, 6, 7], t=[10, 6, 5, 12], ativo=[1, 2],
               dano=70, peso="Heavy", guarda="HA", cai=True, avanca=[(5, 3.5), (16, 0)]),
}
LEVES = (4200, 4202, 4400, 4402)
# rota: estado -> (botão, direção, de quais estados sai no contato). Direção: None (sem baixo), "baixo", "frente",
# "tras" ou "ar". Os normais em pé e agachados saem também de um fraco (var(5) < 4).
ROTAS = {4400: ("x", "baixo", LEVES), 4401: ("y", "baixo", ()), 4402: ("a", "baixo", ()), 4403: ("b", "baixo", ()),
         4200: ("x", None, LEVES), 4201: ("y", None, ()), 4202: ("a", None, ()), 4203: ("b", None, ()),
         4210: ("x", "frente", ()), 4211: ("y", "frente", (4301,)),  # Banquete do Diabo: x, x, → y, ↘ b
         4212: ("b", "frente", ()), 4213: ("y", "tras", ()),
         4600: ("x", "ar", ()), 4601: ("y", "ar", ()), 4602: ("a", "ar", ()), 4603: ("b", "ar", ())}
# correntes: estado -> (botão, de quais estados, finalizador?)
CORRENTES = {4301: ("x", (4200,), False), 4302: ("x", (4301,), False), 4303: ("x", (4302,), True),
             4311: ("y", (4201,), False), 4312: ("y", (4311,), False), 4313: ("y", (4312,), True),
             4321: ("a", (4202, 4402), False), 4322: ("a", (4321,), False), 4323: ("a", (4322,), True),
             4331: ("b", (4203,), False), 4332: ("b", (4331,), False), 4333: ("b", (4332,), True)}

# Especiais e super: as animações (sem dano na ação; o dano está nos estados de ESPECIAIS_CNS), {ação: desenho}.
ANIMS = {
    4500: dict(folha="bola_trevas", q=[0, 1, 2, 3, 4, 5, 6, 7], t=[4, 4, 3, 3, 10, 5, 5, 6], ativo=[]),
    4510: dict(folha="voo", q=[0, 1, 2], t=[6, 4, -1], ativo=[]),
    4512: dict(folha="voo", q=[3, 4], t=[6, 6], ativo=[], laco=0),
    4513: dict(folha="voo", q=[5, 6], t=[4, -1], ativo=[0, 1]),
    4514: dict(folha="voo", q=[7], t=[12], ativo=[]),
    4520: dict(folha="rasgo", q=[0, 1, 2, 3, 4, 5], t=[3, 4, 4, 4, 5, -1], ativo=[1, 2, 3], ponta="cima"),
    4522: dict(folha="rasgo", q=[6, 7], t=[8, 12], ativo=[]),
    4650: dict(folha="juizo_a", q=[0, 1, 2], t=[10, 4, -1], ativo=[1, 2]),
    4651: dict(folha="juizo_a", q=[3, 4, 5, 6, 7], t=[4, 6, 6, 6, -1], ativo=[]),
    4652: dict(folha="juizo_b", q=[0, 1, 2], t=[5, 5, -1], ativo=[]),
    4653: dict(folha="juizo_b", q=[3, 4, 5, 6, 7], t=[8, 10, 8, 10, 10], ativo=[]),
    4654: dict(folha="juizo_b", q=[3, 7], t=[12, 10], ativo=[]),
}
# especial -> as folhas que ele precisa (só entra no jogo com todas prontas)
ESPECIAIS = {"bola": ("bola_trevas",), "voo": ("voo",), "rasgo": ("rasgo",), "juizo": ("juizo_a", "juizo_b")}
BOLA = {"projanim": 4580, "carga": 4582, "grupo": 7480, "grupo_carga": 7481, "escala": 0.5,
        "clsn": (-22, -16, 12, 16), "sai": 11}


# Só para testar o motor antes da arte do boneco de peças chegar (NAZA_DEMONIO_PROVISORIO=1): a folha que ainda não
# existe usa uma que já existe, do mesmo jeito de corpo. Nunca vai para a mugen: o vídeo e o merge usam só arte de verdade.
PROVISORIO = {"ar_maos": "pulo", "ar_pes": "pulo", "direcionais_a": "pe_maos", "direcionais_b": "pe_pes",
              "fins_maos": "pe_maos", "fins_pes": "pe_pes", "bola_trevas": "pe_maos", "voo": "pulo",
              "rasgo": "agachado_maos", "juizo_a": "cobranca_garras", "juizo_b": "pulo"}


def pasta(folha):
    """Pasta m_ da folha (Path) ou None se ainda não existe."""
    if (SAIDA / f"m_{folha}" / "07.png").exists():
        return SAIDA / f"m_{folha}"
    if os.environ.get("NAZA_DEMONIO_PROVISORIO") and folha in PROVISORIO:
        return SAIDA / f"m_{PROVISORIO[folha]}"
    return None


def disponiveis():
    """Golpes com folha pronta; um golpe de corrente só entra se o anterior também entrou."""
    ok = {n: g for n, g in GOLPES.items() if pasta(g["folha"])}
    for n in sorted(CORRENTES):
        if n in ok and not any(d in ok for d in CORRENTES[n][1]):
            del ok[n]
    return ok


def especiais():
    """Especiais e super com todas as folhas prontas: {'bola', 'voo', 'rasgo', 'juizo'}."""
    return {e for e, folhas in ESPECIAIS.items() if all(pasta(f) for f in folhas)}


def _caixas(m, ex, ey, ponta, ativo):
    """Caixas em px 3x em relação ao eixo: corpo (colunas com tinta >= 35% da mais cheia), a ponta do golpe nos quadros
    ativos (só a parte ligada ao pixel mais à frente, ou mais alto, na faixa de 75 px) e a caixa de dano do membro, do
    fim do corpo até a ponta (quem bate também pode apanhar no braço esticado). -> (corpo, golpe, membro)."""
    import cv2
    import numpy as np
    ys, xs = np.nonzero(m)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    col = m.sum(axis=0)
    cheias = np.flatnonzero(col >= 0.35 * col.max())
    topo = y0 + round(0.06 * (y1 - y0))
    corpo = (int(cheias.min()) - ex, topo - ey, int(cheias.max()) - ex, 0)
    if not ativo:
        return corpo, None, None
    if ponta == "cima":
        # antiaéreo: da garra lá em cima até o peito (pega também quem está colado em pé)
        a, b = y0, y0 + 150
        faixa = m[a:b].astype(np.uint8)
        _, rot = cv2.connectedComponents(faixa, connectivity=8)
        alvo = rot[0, int(np.flatnonzero(faixa[0])[0])]
        fy, fx = np.nonzero(rot == alvo)
        golpe = (int(fx.min()) - 6 - ex, a - 6 - ey, int(fx.max()) + 6 - ex, a + int(fy.max()) + 6 - ey)
        return corpo, golpe, golpe
    if ponta == "baixo":
        # pisão: a parte ligada ao pixel mais baixo, na faixa de 75 px de baixo (os pés em garra)
        a = max(0, y1 - 75)
        faixa = m[a:y1 + 1].astype(np.uint8)
        _, rot = cv2.connectedComponents(faixa, connectivity=8)
        alvo = rot[faixa.shape[0] - 1, int(np.flatnonzero(faixa[-1])[-1])]
        fy, fx = np.nonzero(rot == alvo)
        golpe = (int(fx.min()) - 6 - ex, a + int(fy.min()) - 6 - ey, int(fx.max()) + 6 - ex, y1 + 6 - ey)
        return corpo, golpe, golpe
    a = max(0, x1 - 75)
    faixa = m[:, a:x1 + 1].astype(np.uint8)
    _, rot = cv2.connectedComponents(faixa, connectivity=8)
    alvo = rot[int(np.flatnonzero(faixa[:, -1])[0]), faixa.shape[1] - 1]
    fy, fx = np.nonzero(rot == alvo)
    golpe = (a + int(fx.min()) - 6 - ex, int(fy.min()) - 6 - ey, x1 + 6 - ex, int(fy.max()) + 6 - ey)
    membro = (min(corpo[2], golpe[0]), golpe[1], golpe[2], golpe[3])
    return corpo, golpe, membro


def acao(n, g):
    """(quadros [(RGBA, eixo x, eixo y)], texto da ação n, centro da ponta em px do jogo para a faísca)."""
    import numpy as np
    from PIL import Image
    import diabo_terno as dt
    quadros, linhas, faisca = [], [], None
    for j, (k, t) in enumerate(zip(g["q"], g["t"])):
        img = Image.open(pasta(g["folha"]) / f"{k:02d}.png").convert("RGBA")
        m = np.array(img)[..., 3] > 0
        ax, ay = dt.ancora_demonio(m)
        ex, ey = round(ax), int(ay)
        quadros.append((img, ex, ey))
        corpo, golpe, membro = _caixas(m, ex, ey, g.get("ponta", "frente"), j in g["ativo"])
        cx2 = [corpo] + ([membro] if membro else [])
        linhas.append(f"Clsn2: {len(cx2)}")
        linhas += [f" Clsn2[{i}] = {a}, {b}, {c}, {d}" for i, (a, b, c, d) in enumerate(cx2)]
        if golpe:
            linhas += ["Clsn1: 1", f" Clsn1[0] = {golpe[0]}, {golpe[1]}, {golpe[2]}, {golpe[3]}"]
            if faisca is None:
                # x da faísca conta da frente do P2 (negativo entra nele), como os -10 do resto do Hazak
                faisca = (-10, max(-95, min(-10, round((golpe[1] + golpe[3]) / 6))))
        if g.get("laco") == j:
            linhas.append("LoopStart")
        linhas.append(f"{GRUPO + n},{j}, 0,0, {t}")
    return quadros, "\n".join(linhas), faisca


def _ctl(n, titulo, tipo, *linhas):
    return f"[State {n}, {titulo}]\ntype = {tipo}\n" + "".join(f"{x}\n" for x in linhas) + "\n"


def cns(n, g, faisca):
    tipo = g.get("tipo", "S")
    fis = {"S": "S", "C": "C", "A": "A"}[tipo]
    pausa, spark, som, desl, atord, emp = PESO[g["peso"]]
    final = n in CORRENTES and CORRENTES[n][2]
    if final:
        pausa = 14  # regra 8.3: finalizador congela 14+ e é o único normal que treme a tela
    if (ROTAS.get(n) or CORRENTES.get(n) or ("",))[0] in ("a", "b"):
        som = som.replace("S51,", "S52,")  # chute: o som de acerto dos chutes do Hazak
    sai = sum(g["t"][:g["ativo"][0]])
    c = [f"[Statedef {n}]\ntype = {tipo}\nmovetype = A\nphysics = {fis}\nctrl = 0\nsprpriority = 2\n"
         f"anim = {n}\njuggle = {3 if g['peso'] == 'Light' else 4}\n" + ("velset = 0,0\n" if tipo != "A" else "") +
         "\n"]
    c.append(_ctl(n, "Vento", "PlaySnd", "trigger1 = Time = 0",
                  f"value = F40,{ {'Light': 0, 'Medium': 1, 'Heavy': 2}[g['peso']] }"))
    if n in LEVES:
        c.append(_ctl(n, "Fracos em sequência", "VarAdd", "trigger1 = Time = 0", "var(5) = 1"))
    for k, (tick, vx) in enumerate(g.get("avanca", [])):
        c.append(_ctl(n, f"Avanço {k + 1}", "VelSet", f"trigger1 = Time = {tick}", f"x = {vx}"))
    if g.get("sobe"):
        fim = sum(g["t"][:g["ativo"][-1] + 1])
        c.append(_ctl(n, "Antiaéreo: ganha de quem vem do ar", "NotHitBy", f"trigger1 = Time = [2,{fim}]", "value = A",
                      "time = 1"))
        c.append(_ctl(n, "Sobe: muda para em pé", "StateTypeSet", f"trigger1 = Time = {sai}", "statetype = S",
                      "physics = S"))
    if n in CORRENTES and not CORRENTES[n][2] or n in (4201, 4203, 4202, 4402):
        emp = max(emp, -2)  # golpe que abre ou continua corrente: o oponente fica no alcance do próximo
    vx, vy = g.get("voa", (-4, -4))
    queda = ["fall = 1", "fall.recover = 0", f"ground.velocity = {vx}, {vy}", f"air.velocity = {min(vx, -3)}, {vy}"] \
        if g.get("cai") else [f"ground.velocity = {emp}", "air.velocity = -2, -4" if g.get("sobe") else "air.velocity = -1.4, -3"]
    fx, fy = faisca or (-10, -70)
    c.append(_ctl(n, g["nome"], "HitDef", f"trigger1 = Time = {sai}", f"attr = {'S' if g.get('sobe') else tipo}, NA",
                  f"damage = {g['dano']}, 0", f"animtype = {g['peso']}", f"guardflag = {g.get('guarda', 'MA')}",
                  "hitflag = MAF", f"priority = {5 if g.get('sobe') else 4}, Hit", f"pausetime = {pausa}, {pausa}",
                  f"guard.pausetime = {pausa - 1}, {pausa - 1}", f"sparkxy = {fx}, {fy}", f"sparkno = {spark}",
                  "guard.sparkno = S9216", f"hitsound = {som}", "guardsound = F6,0",
                  f"ground.type = {g.get('chao', 'High')}", f"ground.slidetime = {desl}",
                  f"ground.hittime = {atord}", *queda,
                  *(["palfx.time = 70", "palfx.add = 150, 40, 0", "palfx.sinadd = 60, 20, 0, 6"] if g.get("fogo")
                    else [])))
    if final:
        c.append(_ctl(n, "Finalizador: tremida", "EnvShake", "trigger1 = MoveHit = 1", "time = 12", "freq = 120",
                      "ampl = -5"))
    if g.get("fogo"):  # fica queimando: o fogo das trevas do agarrão (#45) preso no corpo de quem apanhou
        c.append(_ctl(n, "Fogo das trevas no oponente", "Explod", "trigger1 = MoveHit = 1", "anim = 7470",
                      "id = 4313", "postype = p2", "pos = 0, -55", "bindtime = 70", "removetime = 70",
                      "sprpriority = 5", "ownpal = 1"))
        c.append(_ctl(n, "Estouro do fogo", "Explod", "trigger1 = MoveHit = 1", "anim = 7472", "postype = p2",
                      "pos = -10, -60", "sprpriority = 6", "ownpal = 1", "removetime = -2"))
    if tipo != "A":
        volta = 11 if tipo == "C" and not g.get("sobe") else 0
        c.append(_ctl(n, "Fim", "ChangeState", "trigger1 = AnimTime = 0", f"value = {volta}", "ctrl = 1"))
    return "".join(c)


def _rota(titulo, valor, *linhas):
    return (f"[State -1, Demônio: {titulo}]\ntype = ChangeState\nvalue = {valor}\ntriggerall = var(20) > 0\n"
            + "".join(f"{x}\n" for x in linhas) + "\n")


DIRECAO = {None: ['triggerall = command != "holddown"'], "baixo": ['triggerall = command = "holddown"'],
           "frente": ['triggerall = command = "holdfwd"', 'triggerall = command != "holddown"'],
           "tras": ['triggerall = command = "holdback"', 'triggerall = command != "holddown"'], "ar": []}


def rotas(n_ok, esp=()):
    """Rotas do .cmd do demônio (no fim do [Statedef -1]): cancelamento, super, especiais, correntes, direcionais,
    agachados, em pé e no ar, nessa ordem (o primeiro que vale ganha: o toque do especial antes do botão sozinho)."""
    lista = " || ".join(f"stateno = {n}" for n in sorted(n_ok)) or "0"
    r = [f"[State -1, Demônio: pode cancelar]\ntype = VarSet\ntriggerall = var(20) > 0\n"
         f"trigger1 = ({lista}) && movecontact && movecontact <= 8\nvar(1) = 1\n\n"]
    chao = ["triggerall = statetype != A", "trigger1 = ctrl || var(1)"]
    if "juizo" in esp:
        r.append(_rota("Juízo Infernal (super)", 4650, 'triggerall = command = "dfdf_x" || command = "dfdf_y"',
                       "triggerall = power >= 1000", *chao))
    if "rasgo" in esp:
        r.append(_rota("Rasgo Ascendente", 'ifelse(command = "fd_y", 4521, 4520)',
                       'triggerall = command = "fd_x" || command = "fd_y"', *chao))
    if "bola" in esp:
        r.append(_rota("Bola das Trevas", 'ifelse(command = "df_y", 4501, 4500)',
                       'triggerall = command = "df_x" || command = "df_y"',
                       "triggerall = numprojid(4500) = 0 && numprojid(4501) = 0", *chao))
    if "voo" in esp:
        r.append(_rota("Voo Infernal", 'ifelse(command = "dd_b", 4511, 4510)',
                       'triggerall = command = "dd_a" || command = "dd_b"', *chao))
    # correntes: finalizadores, 3º e 2º (do fim para o começo: o 3º não pode cair na rota do 2º)
    for final in (True, False):
        for n in sorted(CORRENTES, reverse=True):
            botao, de, fin = CORRENTES[n]
            de = [d for d in de if d in n_ok]
            if fin != final or n not in n_ok or not de:
                continue
            quando = "movehit && var(10) >= 3" if fin else "movecontact"
            r.append(_rota(GOLPES[n]["nome"], n, f'triggerall = command = "{botao}"',
                           'triggerall = command != "holddown"',
                           "trigger1 = (" + " || ".join(f"stateno = {d}" for d in de) + f") && {quando}"))
    ordem = {"frente": 0, "tras": 0, "baixo": 1, None: 2, "ar": 3}
    for n, (botao, direcao, de) in sorted(ROTAS.items(), key=lambda kv: (ordem[kv[1][1]], kv[0])):
        if n not in n_ok:
            continue
        tipo = GOLPES[n].get("tipo", "S")
        quando = {"C": "statetype != A", "A": "statetype = A"}.get(tipo, "statetype = S")
        linhas = [f'triggerall = command = "{botao}"', *DIRECAO[direcao], "trigger1 = ctrl", f"trigger1 = {quando}"]
        de = [d for d in de if d in n_ok]
        if de:
            linhas.append("trigger2 = (" + " || ".join(f"stateno = {d}" for d in de) + ") && movecontact"
                          + (" && var(5) < 4" if set(de) <= set(LEVES) else ""))
        r.append(_rota(GOLPES[n]["nome"], n, *linhas))
    return "".join(r)


COMANDOS = [("dd_a", "~D, >D, a"), ("dd_b", "~D, >D, b"), ("dfdf_x", "~D, F, D, F, x"), ("dfdf_y", "~D, F, D, F, y")]


def comandos(cmd):
    """Os toques novos do demônio (Voo Infernal ↓↓ e Juízo Infernal ↓↘→↓↘→), antes do [Statedef -1]."""
    cab = "[Statedef -1]\n\n"
    novos = "".join(f'[Command]\nname = "{n}"\ncommand = {c}\ntime = {25 if n.startswith("dfdf") else 15}\n\n'
                    for n, c in COMANDOS if f'name = "{n}"' not in cmd)
    assert cmd.count(cab) == 1
    return cmd.replace(cab, novos + cab, 1)


def _st(n, tipo, fis, anim, *extra, mov="A"):
    return (f"[Statedef {n}]\ntype = {tipo}\nmovetype = {mov}\nphysics = {fis}\nctrl = 0\nsprpriority = 2\n"
            f"anim = {anim}\n" + "".join(f"{x}\n" for x in extra) + "\n")


def _hit(n, titulo, quando, dano, peso, *extra, attr="S, SA", guarda="MA"):
    pausa, spark, _, desl, atord, _ = PESO[peso]
    pausas = [] if any(x.startswith("pausetime") for x in extra) else [f"pausetime = {pausa}, {pausa}",
                                                                      f"guard.pausetime = {pausa - 1}, {pausa - 1}"]
    return _ctl(n, titulo, "HitDef", quando, f"attr = {attr}", f"damage = {dano}, 4", f"animtype = {peso}",
                f"guardflag = {guarda}", "hitflag = MAF", "priority = 5, Hit", *pausas, "sparkxy = -10, -70", f"sparkno = {spark}",
                "guard.sparkno = S9216", "hitsound = S53,0", "guardsound = F6,0", f"ground.slidetime = {desl}",
                f"ground.hittime = {atord}", *extra)


def _fim(n, valor=0, quando="trigger1 = AnimTime = 0"):
    return _ctl(n, "Fim", "ChangeState", quando, f"value = {valor}", "ctrl = 1")


def cns_bola(n, forte, boca):
    """Bola das Trevas (↓↘→ soco): a fraca vai reta, a forte faz arco. boca = (x, y) da garra em px do jogo."""
    b = BOLA
    c = [_st(n, "S", "S", 4500, "velset = 0,0", "juggle = 0")]
    c.append(_ctl(n, "Vento", "PlaySnd", "trigger1 = Time = 0", "value = F40,1"))
    c.append(_ctl(n, "Carga na garra", "Explod", "trigger1 = Time = 2", f"anim = {b['carga']}", "id = 4582",
                  "postype = p1", f"pos = {boca[0] - 30}, {boca[1] + 10}", f"removetime = {b['sai'] - 2}",
                  "bindtime = -1", "sprpriority = 4", "ownpal = 1"))
    c.append(_ctl(n, "Carga: treme de leve", "EnvShake", "trigger1 = Time = 4", f"time = {b['sai'] - 4}",
                  "freq = 180", "ampl = -2"))
    c.append(_ctl(n, "Solta: tremida", "EnvShake", f"trigger1 = Time = {b['sai']}", "time = 10", "freq = 100",
                  "ampl = -5"))
    vel = ["velocity = 4.6, -4.4", "accel = 0, .2"] if forte else ["velocity = 5, 0"]
    c.append(_ctl(n, "Projétil", "Projectile", f"trigger1 = Time = {b['sai']}", f"projid = {4500 + forte}",
                  f"projanim = {b['projanim']}", "projhitanim = 7472", "projremanim = 7472", "projcancelanim = 7472",
                  "projremovetime = 160", "projpriority = 2", f"offset = {boca[0]}, {boca[1]}", *vel,
                  "attr = S, SP", f"damage = {80 if forte else 70}, 8", "animtype = Heavy", "guardflag = MA",
                  "hitflag = MAF", "pausetime = 0, 14", "sparkno = -1", "guard.sparkno = S9216",
                  "hitsound = S53,0", "guardsound = F6,0", "ground.type = High", "ground.slidetime = 10",
                  "ground.hittime = 18", "ground.velocity = -5", "air.velocity = -3, -4",
                  *(["fall = 1", "fall.recover = 0", "ground.velocity = -4, -5"] if forte else []),
                  "palfx.time = 14", "palfx.add = 150, 30, 0", "palfx.sinadd = 40, 20, 0, 4"))
    c.append(_fim(n))
    return "".join(c)


def cns_voo():
    """Voo Infernal (↓↓ chute): sobe com as asas e paira; soco no ar mergulha de garras. a sobe menos, b mais alto
    e paira mais tempo."""
    c = []
    for n, vy in ((4510, -8), (4511, -10)):
        c.append(_st(n, "S", "N", 4510, "velset = 0,0", "juggle = 4"))
        c.append(_ctl(n, "Vento", "PlaySnd", "trigger1 = Time = 0", "value = F40,2"))
        c.append(_ctl(n, "Sobe", "VelSet", "trigger1 = Time = 6", f"y = {vy}", "x = 1"))
        c.append(_ctl(n, "No ar", "StateTypeSet", "trigger1 = Time = 6", "statetype = A", "movetype = I"))
        c.append(_ctl(n, "Gravidade", "VelAdd", "trigger1 = Time > 6", "y = .45"))
        c.append(_ctl(n, "Paira no alto", "ChangeState", "trigger1 = Time > 6 && Vel Y >= -.5", "value = 4512"))
    n = 4512
    c.append(_st(n, "A", "N", 4512, "velset = 0,0", mov="I"))
    c.append(_ctl(n, "Asas batendo: sobe e desce de leve", "VelSet", "trigger1 = 1", "y = .35 * sin(Time * .3)"))
    c.append(_ctl(n, "Mergulho", "ChangeState", "trigger1 = Time > 3", 'trigger1 = command = "x" || command = "y"',
                  "value = 4513"))
    c.append(_ctl(n, "Cansou de pairar", "ChangeState", "trigger1 = Time >= ifelse(PrevStateNo = 4511, 46, 28)",
                  "value = 50", "ctrl = 1"))
    n = 4513
    c.append(_st(n, "A", "N", 4513, "velset = 6.5, 8", "juggle = 4"))
    c.append(_ctl(n, "Vento", "PlaySnd", "trigger1 = Time = 0", "value = F40,2"))
    c.append(_ctl(n, "Rastro", "AfterImage", "trigger1 = Time = 0", "time = 20", "length = 6", "timegap = 2",
                  "framegap = 2", "trans = add", "paladd = 120, 40, 0", "palmul = .5, .5, .5"))
    c.append(_hit(n, "Mergulho de garras", "trigger1 = Time = 0", 75, "Heavy", "ground.type = High", "fall = 1",
                  "fall.recover = 0", "ground.velocity = -5, -4", "air.velocity = -4, -4", attr="A, SA",
                  guarda="HA"))
    c.append(_ctl(n, "Chão", "ChangeState", "trigger1 = Vel Y > 0 && Pos Y >= 0", "value = 4514"))
    n = 4514
    c.append(_st(n, "S", "S", 4514, "velset = 0,0"))
    c.append(_ctl(n, "No chão", "PosSet", "trigger1 = Time = 0", "y = 0"))
    c.append(_ctl(n, "Pouso", "EnvShake", "trigger1 = Time = 0", "time = 6", "ampl = -3", "freq = 120"))
    c.append(_fim(n))
    return "".join(c)


def cns_rasgo():
    """Rasgo Ascendente (→↓↘ soco): antiaéreo que sobe girando com as garras em chamas, 2 acertos. Invencível no
    começo (a fraca só contra quem vem do ar; a forte contra tudo, por menos tempo)."""
    c = []
    for n, (vx, vy, inv, d1, d2) in ((4520, (1.6, -8.5, "A", 45, 40)), (4521, (2, -10.5, "SCA", 55, 50))):
        c.append(_st(n, "S", "N", 4520, "velset = 0,0", "juggle = 4"))
        c.append(_ctl(n, "Vento", "PlaySnd", "trigger1 = Time = 0", "value = F40,2"))
        c.append(_ctl(n, "Invencível no começo", "NotHitBy", f"trigger1 = Time <= {10 if inv == 'A' else 7}",
                      f"value = {inv}", "time = 1"))
        c.append(_ctl(n, "Sobe", "VelSet", "trigger1 = Time = 3", f"x = {vx}", f"y = {vy}"))
        c.append(_ctl(n, "No ar", "StateTypeSet", "trigger1 = Time = 3", "statetype = A"))
        c.append(_ctl(n, "Gravidade", "VelAdd", "trigger1 = Time > 3", "y = .5"))
        c.append(_ctl(n, "Garras em chamas", "AfterImage", "trigger1 = Time = 2", "time = 16", "length = 5",
                      "timegap = 2", "framegap = 2", "trans = add", "paladd = 130, 40, 0", "palmul = .5, .5, .5"))
        c.append(_hit(n, "Rasgo 1", "trigger1 = Time = 3", d1, "Medium", "ground.type = High",
                      "ground.velocity = -1.5, -6", "air.velocity = -1.5, -6", "air.juggle = 2"))
        c.append(_hit(n, "Rasgo 2", "trigger1 = Time = 11", d2, "Heavy", "ground.type = High", "fall = 1",
                      "fall.recover = 0", "ground.velocity = -3, -7", "air.velocity = -3, -7"))
        c.append(_ctl(n, "Chão", "ChangeState", "trigger1 = Time > 5 && Vel Y > 0 && Pos Y >= 0", "value = 4522"))
    n = 4522
    c.append(_st(n, "S", "S", 4522, "velset = 0,0"))
    c.append(_ctl(n, "No chão", "PosSet", "trigger1 = Time = 0", "y = 0"))
    c.append(_fim(n))
    return "".join(c)


def cns_juizo():
    """Juízo Infernal (↓↘→↓↘→ soco, 1 estoque): voa para cima do oponente, crava as garras e sobe com ele, gira lá
    em cima e o atira no chão, que explode em fogo das trevas. Quem apanha usa os estados 4660 e 4661 do Hazak."""
    c = []
    n = 4650
    c.append(_st(n, "S", "N", 4650, "velset = 0,0", "juggle = 0", "poweradd = 0"))
    c.append(_ctl(n, "Pausa", "SuperPause", "trigger1 = Time = 0", "time = 25", "anim = S9271", "pos = 10, -60",
                  "movetime = 0", "darken = 1"))
    c.append(_ctl(n, "Gasta", "PowerAdd", "trigger1 = Time = 0", "value = -1000"))
    c.append(_ctl(n, "Chão ainda não explodiu", "MapSet", "trigger1 = Time = 0", 'map = "dj_chao"', "value = 0"))
    c.append(_ctl(n, "Invencível na saída", "NotHitBy", "trigger1 = Time < 14", "value = SCA", "time = 1"))
    c.append(_ctl(n, "Rastro", "AfterImage", "trigger1 = Time = 0", "time = 60", "length = 8", "timegap = 2",
                  "framegap = 2", "trans = add", "paladd = 120, 50, 0", "palmul = .55, .55, .55"))
    c.append(_ctl(n, "Fundo escurece em vermelho", "BGPalFX", "trigger1 = Time = 1", "time = 100",
                  "mul = 120, 55, 50"))
    c.append(_ctl(n, "Voa", "VelSet", "trigger1 = Time = 10", "x = 11"))
    c.append(_ctl(n, "Vento", "PlaySnd", "trigger1 = Time = 10", "value = F40,2"))
    c.append(_hit(n, "Crava as garras", "trigger1 = Time = 10", 30, "Heavy", "ground.type = High", "pausetime = 4, 4",
                  "p2stateno = 4660", "p2getp1state = 1", "air.velocity = 0, 0", "ground.velocity = 0, 0",
                  attr="S, HA"))
    c.append(_ctl(n, "Pegou: já segura na pausa do acerto", "TargetBind", "trigger1 = MoveHit", "pos = 42, -24",
                  "time = 1", "ignorehitpause = 1"))
    c.append(_ctl(n, "Pegou", "ChangeState", "trigger1 = MoveHit", "value = 4651"))
    c.append(_ctl(n, "Errou ou defendeu", "ChangeState", "trigger1 = MoveGuarded || Time >= 32", "value = 4654"))
    n = 4651
    c.append(_st(n, "A", "N", 4651, "velset = 0, -6"))
    c.append(_ctl(n, "Sobe", "VelAdd", "trigger1 = 1", "y = .18"))
    c.append(_ctl(n, "Segura", "TargetBind", "trigger1 = 1", "pos = 42, -24", "time = 1"))
    for k, t in enumerate((6, 14, 22)):
        c.append(_ctl(n, f"Garra {k + 1}", "TargetLifeAdd", f"trigger1 = Time = {t}", "value = -20", "kill = 0"))
        c.append(_ctl(n, f"Garra {k + 1}: estouro", "Explod", f"trigger1 = Time = {t}", "anim = 7472",
                      "postype = p2", "pos = 0, -50", "sprpriority = 6", "ownpal = 1", "removetime = -2"))
        c.append(_ctl(n, f"Garra {k + 1}: som", "PlaySnd", f"trigger1 = Time = {t}", "value = S53,0"))
        c.append(_ctl(n, f"Garra {k + 1}: tremida", "EnvShake", f"trigger1 = Time = {t}", "time = 5", "ampl = -3",
                      "freq = 140"))
    c.append(_ctl(n, "Lá em cima", "ChangeState", "trigger1 = Time >= 30", "value = 4652"))
    n = 4652
    c.append(_st(n, "A", "N", 4652, "velset = 0, -1"))
    c.append(_ctl(n, "Segura", "TargetBind", "trigger1 = Time < 5", "pos = 30, -10", "time = 1"))
    c.append(_ctl(n, "Atira no chão", "TargetState", "trigger1 = Time = 5", "value = 4661"))
    c.append(_ctl(n, "Atira no chão: velocidade", "TargetVelSet", "trigger1 = Time = 5", "x = -2", "y = 12"))
    c.append(_ctl(n, "Atira no chão: dano", "TargetLifeAdd", "trigger1 = Time = 5", "value = -50", "kill = 0"))
    c.append(_ctl(n, "Cai", "VelAdd", "trigger1 = Time > 5", "y = .4"))
    # uma vez só, travada no map dj_chao (zerado no 4650): a luz que o luz_efeitos copia do Explod, logo depois dele,
    # copia o gatilho; com NumExplod(4670) = 0 ela nunca nascia (o Explod já conta no mesmo tique)
    explosao = [("O chão explode: dano", "TargetLifeAdd", "value = -120"),
                ("O chão explode: tremida", "EnvShake", "time = 30", "ampl = -10", "freq = 100"),
                ("O chão explode: clarão", "BGPalFX", "time = 20", "add = 130, 40, 0"),
                ("O chão explode: som", "PlaySnd", "value = S53,0"),
                ("O chão explode", "Explod", "anim = 7471", "id = 4670", "postype = p2", "pos = 0, 0",
                 "scale = 1.5, 1.5", "sprpriority = 6", "ownpal = 1", "removetime = -2")]
    explosao.append(("O chão explode: uma vez só", "MapSet", 'map = "dj_chao"', "value = 1"))
    for titulo, tipo, *linhas in explosao:
        c.append(_ctl(n, titulo, tipo, "trigger1 = Time > 5 && NumTarget > 0 && map(dj_chao) = 0",
                      "trigger1 = target, Pos Y >= -10", *linhas))
    c.append(_ctl(n, "Chão", "ChangeState", "trigger1 = Time > 5 && Vel Y > 0 && Pos Y >= 0", "value = 4653"))
    n = 4653
    c.append(_st(n, "S", "S", 4653, "velset = 0,0"))
    c.append(_ctl(n, "No chão", "PosSet", "trigger1 = Time = 0", "y = 0"))
    for titulo, tipo, *linhas in explosao:  # se ele chegou antes de quem foi atirado, explode na hora
        c.append(_ctl(n, titulo, tipo, "trigger1 = Time = 0 && NumTarget > 0 && map(dj_chao) = 0", *linhas))
    c.append(_fim(n))
    n = 4654
    c.append(_st(n, "S", "S", 4654, "velset = 0,0"))
    c.append(_fim(n))
    # quem apanha (estados do Hazak, p2getp1state)
    n = 4660
    c.append(_st(n, "A", "N", 5000, "velset = 0,0", mov="H"))
    for anim, cond in ((5943, "SelfAnimExist(5943)"), (5940, "!SelfAnimExist(5943) && SelfAnimExist(5940)")):
        c.append(_ctl(n, "Preso: pose própria", "ChangeAnim", "trigger1 = Time = 0", f"trigger1 = {cond}",
                      f"value = {anim}"))
    c.append(_ctl(n, "Solto", "HitFallSet", "trigger1 = Time > 6 && !gethitvar(isbound)", "value = 1"))
    c.append(_ctl(n, "Solto", "SelfState", "trigger1 = Time > 6 && !gethitvar(isbound)", "value = 5050"))
    n = 4661
    c.append(_st(n, "A", "N", 5030, mov="H"))
    c.append(_ctl(n, "Caindo", "ChangeAnim", "trigger1 = Time = 0 && SelfAnimExist(5944)", "value = 5944"))
    c.append(_ctl(n, "Cai de verdade", "HitFallSet", "trigger1 = Time = 0", "value = 1"))
    c.append(_ctl(n, "Queda", "VelAdd", "trigger1 = 1", "y = .5"))
    c.append(_ctl(n, "Chão", "SelfState", "trigger1 = Vel Y > 0 && Pos Y >= 0", "value = 5100"))
    return "".join(c)


MENOS_2 = """[State -2, Demônio: Bola das Trevas acertou (tremida)]
type = EnvShake
trigger1 = ProjHitTime(4500) = 0 || ProjHitTime(4501) = 0
time = 14
freq = 100
ampl = -7

[State -2, Demônio: Bola das Trevas acertou (fundo pisca)]
type = BGPalFX
trigger1 = ProjHitTime(4500) = 0 || ProjHitTime(4501) = 0
time = 6
add = 100, 20, 0

[State -2, Demônio: conta acerto da corrente]
type = VarAdd
trigger1 = MoveHit
trigger1 = var(11) = 0
trigger1 = stateno = [4200,4449]
var(10) = 1

"""


def bloquear_base(cmd):
    """Na forma do demônio nenhum golpe do Hazak sai (normais, correntes, kombos, Afastar 260/650/720, especiais e
    supers); ficam o movimento, a defesa, os agarrões (800-899, thread dos agarrões) e os especiais do Diabo (1650,
    1660, 1661)."""
    import re

    def golpe(v):
        return (200 <= v <= 249 or 260 <= v <= 349 or 400 <= v <= 449 or 600 <= v <= 699 or v == 720
                or (1000 <= v <= 1999 and v not in (1650, 1660, 1661)) or 3000 <= v <= 3999)

    def troca(m):
        bloco = m.group(0)
        if "var(20)" in bloco:
            return bloco
        if bloco.startswith("[State -1, Gasta afastar de defesa]"):  # o 720 não sai: a barra também não some
            return re.sub(r"^(type = \w+\n)", r"\1triggerall = var(20) <= 0\n", bloco, count=1, flags=re.M)
        v = re.search(r"^value = \D*?(\d+)", bloco, re.M)
        if "type = ChangeState" not in bloco or not v or not golpe(int(v.group(1))):
            return bloco
        return bloco.replace("type = ChangeState\n", "type = ChangeState\ntriggerall = var(20) <= 0\n", 1)

    return re.sub(r"^\[State -1, [^\n]*\n(?:[^\n]+\n)*", troca, cmd, flags=re.M)


def _boca(quadros, j=3):
    """(x, y) em px do jogo, do eixo do quadro j até a ponta da garra (pixel mais à frente, na altura dele)."""
    import numpy as np
    img, ex, ey = quadros[j]
    m = np.array(img)[..., 3] > 0
    ys, xs = np.nonzero(m)
    x1 = xs.max()
    y = int(np.median(ys[xs >= x1 - 6]))
    return round((x1 - ex) / 3), round((y - ey) / 3)


def acoes_da_bola():
    """{ação: texto}, {grupo: quadros} da bola de fogo das trevas (Blender, d47_poder) e da carga na garra (d47_carga)."""
    import diabo_loiro as dl
    b, texto, sprites = BOLA, {}, {}
    s = dl.E * b["escala"]
    for acao, grupo, nome, clsn in ((b["projanim"], b["grupo"], "d47_poder", b["clsn"]),
                                    (b["carga"], b["grupo_carga"], "d47_carga", None)):
        quadros, ticks = dl.render(nome)
        linhas = [dl.caixa("Clsn2", *clsn), dl.caixa("Clsn1", *clsn)] if clsn else []
        for i in range(len(quadros)):
            if clsn and i == 0:
                linhas.append("LoopStart")
            linhas.append(f"{grupo},{i}, 0,0, {ticks}, , , {s:g}, {s:g}")
        texto[acao], sprites[grupo] = "\n".join(linhas), quadros
    return texto, sprites


def ligar(air, cmd):
    """-> (air, cmd, cns dos estados, linhas do [Statedef -2], {grupo: quadros}) com os golpes que já têm folha."""
    import efeitos
    ok, esp = disponiveis(), especiais()
    if not ok and not esp:
        return air, cmd, "", "", {}
    sprites, estados = {}, []
    for n, g in ok.items():
        quadros, texto, faisca = acao(n, g)
        air = efeitos.por_acao(air, n, texto)
        sprites[GRUPO + n] = quadros
        estados.append(cns(n, g, faisca))
    precisa = {"bola": (4500,), "voo": (4510, 4512, 4513, 4514), "rasgo": (4520, 4522),
               "juizo": (4650, 4651, 4652, 4653, 4654)}
    feitos = {}
    for e in sorted(esp):
        for n in precisa[e]:
            quadros, texto, _ = acao(n, ANIMS[n])
            air = efeitos.por_acao(air, n, texto)
            sprites[GRUPO + n] = feitos[n] = quadros
    if "bola" in esp:
        textos, spr = acoes_da_bola()
        for a, t in textos.items():
            air = efeitos.por_acao(air, a, t)
        sprites.update(spr)
        boca = _boca(feitos[4500])
        estados += [cns_bola(4500, 0, boca), cns_bola(4501, 1, boca)]
    if "voo" in esp:
        estados.append(cns_voo())
    if "rasgo" in esp:
        estados.append(cns_rasgo())
    if "juizo" in esp:
        estados.append(cns_juizo())
    # no fim do [Statedef -1]: depois do "Pode cancelar" (que reescreve o var(1)) e dos agarrões (frente + y colado
    # continua sendo agarrão); os golpes do Hazak que viriam antes estão travados na forma
    cmd = comandos(bloquear_base(cmd)).rstrip() + "\n\n" + rotas(set(ok), esp)
    print(f"demônio: {len(ok)} golpes próprios ({', '.join(g['nome'] for g in ok.values())}); especiais: "
          f"{', '.join(sorted(esp)) or 'nenhum'}")
    return air, cmd, "".join(estados), MENOS_2, sprites


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--fila" in args:
        fila()
    elif "--pedido" in args:
        print(pedido(args[args.index("--pedido") + 1]))
    elif "--seguinte" in args:
        print(pedido_seguinte(args[args.index("--seguinte") + 1]))
    elif "--contato" in args:
        i = args.index("--contato")
        contato(args[i + 1], args[i + 2:])
    else:
        e = escala()
        # o m_parado primeiro: ele é a referência de cor (e a paleta) da forma m_ no cores.py
        for nome in args or sorted((p.stem for p in FOLHAS.glob("*.png")), key=lambda n: (n != "parado", n)):
            converter(nome, e)
