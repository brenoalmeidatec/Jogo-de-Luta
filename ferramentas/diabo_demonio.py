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

# Cada golpe: folha e quadros (de 0 a 7), ticks por quadro, quadros com caixa de golpe, de onde sai a ponta (frente,
# cima), dano, peso, guarda (MA, L, H), tipo do chão (High, Low, Trip), avanço [(tick, vel x)], cai (derruba).
GOLPES = {
    4200: dict(nome="Arranhão", folha="pe_maos", q=[0, 1, 2, 3], t=[3, 3, 4, 5], ativo=[1], dano=25, peso="Light"),
    4201: dict(nome="Garra Cruzada", folha="pe_maos", q=[4, 5, 6, 7], t=[6, 4, 6, 10], ativo=[1], dano=62,
               peso="Medium", avanca=[(2, 1.5), (10, 0)]),
    4202: dict(nome="Joelhada Selvagem", folha="pe_pes", q=[0, 1, 2, 3], t=[4, 4, 5, 7], ativo=[1], dano=32,
               peso="Light"),
    4203: dict(nome="Coice com Garra", folha="pe_pes", q=[4, 5, 6, 7], t=[6, 5, 6, 10], ativo=[1], dano=72,
               peso="Heavy"),
    4400: dict(nome="Arranhão Baixo", folha="agachado_maos", q=[0, 1, 2, 3], t=[3, 3, 4, 5], ativo=[1], dano=22,
               peso="Light", tipo="C", chao="Low"),
    4401: dict(nome="Garra Subindo", folha="agachado_maos", q=[4, 5, 6, 7], t=[4, 4, 7, 9], ativo=[1, 2], dano=60,
               peso="Medium", tipo="C", ponta="cima", sobe=True),
    4402: dict(nome="Rabo Rasteiro", folha="agachado_pes", q=[0, 1, 2, 3], t=[4, 4, 5, 7], ativo=[1], dano=30,
               peso="Light", tipo="C", guarda="L", chao="Low"),
    4403: dict(nome="Varrida de Garras", folha="agachado_pes", q=[4, 5, 6, 7], t=[6, 4, 8, 10], ativo=[1, 2], dano=65,
               peso="Heavy", tipo="C", guarda="L", chao="Trip", cai=True),
}
LEVES = (4200, 4202, 4400, 4402)
# rota: estado -> (botão, segurando para baixo?, de quais estados cancela no contato)
ROTAS = {4400: ("x", True, LEVES), 4401: ("y", True, ()), 4200: ("x", False, LEVES), 4201: ("y", False, ()),
         4202: ("a", False, ()), 4203: ("b", False, ()), 4402: ("a", True, ()), 4403: ("b", True, ())}


def disponiveis():
    return {n: g for n, g in GOLPES.items() if (SAIDA / f"m_{g['folha']}" / "07.png").exists()}


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
        img = Image.open(SAIDA / f"m_{g['folha']}" / f"{k:02d}.png").convert("RGBA")
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
        linhas.append(f"{GRUPO + n},{j}, 0,0, {t}")
    return quadros, "\n".join(linhas), faisca


def _ctl(n, titulo, tipo, *linhas):
    return f"[State {n}, {titulo}]\ntype = {tipo}\n" + "".join(f"{x}\n" for x in linhas) + "\n"


def cns(n, g, faisca):
    tipo = g.get("tipo", "S")
    fis = {"S": "S", "C": "C", "A": "A"}[tipo]
    pausa, spark, som, desl, atord, emp = PESO[g["peso"]]
    if ROTAS.get(n, ("",))[0] in ("a", "b"):
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
    queda = ["fall = 1", "fall.recover = 0", "ground.velocity = -4, -4", "air.velocity = -3, -4"] if g.get("cai") \
        else [f"ground.velocity = {emp}", "air.velocity = -2, -4" if g.get("sobe") else "air.velocity = -1.4, -3"]
    fx, fy = faisca or (-10, -70)
    c.append(_ctl(n, g["nome"], "HitDef", f"trigger1 = Time = {sai}", f"attr = {'S' if g.get('sobe') else tipo}, NA",
                  f"damage = {g['dano']}, 0", f"animtype = {g['peso']}", f"guardflag = {g.get('guarda', 'MA')}",
                  "hitflag = MAF", f"priority = {5 if g.get('sobe') else 4}, Hit", f"pausetime = {pausa}, {pausa}",
                  f"guard.pausetime = {pausa - 1}, {pausa - 1}", f"sparkxy = {fx}, {fy}", f"sparkno = {spark}",
                  "guard.sparkno = S9216", f"hitsound = {som}", "guardsound = F6,0",
                  f"ground.type = {g.get('chao', 'High')}", f"ground.slidetime = {desl}",
                  f"ground.hittime = {atord}", *queda))
    if tipo != "A":
        volta = 11 if tipo == "C" and not g.get("sobe") else 0
        c.append(_ctl(n, "Fim", "ChangeState", "trigger1 = AnimTime = 0", f"value = {volta}", "ctrl = 1"))
    return "".join(c)


def rotas(n_ok):
    """Rotas do .cmd do demônio (no fim do [Statedef -1]): cancelamento dos golpes dele e os botões."""
    lista = " || ".join(f"stateno = {n}" for n in sorted(n_ok))
    r = [f"[State -1, Demônio: pode cancelar]\ntype = VarSet\ntriggerall = var(20) > 0\n"
         f"trigger1 = ({lista}) && movecontact && movecontact <= 8\nvar(1) = 1\n\n"]
    for n, (botao, baixo, de) in ROTAS.items():
        if n not in n_ok:
            continue
        tipo = GOLPES[n].get("tipo", "S")
        r.append(f"[State -1, Demônio: {GOLPES[n]['nome']}]\ntype = ChangeState\nvalue = {n}\n"
                 f"triggerall = var(20) > 0\ntriggerall = command = \"{botao}\"\n"
                 f"triggerall = command {'=' if baixo else '!='} \"holddown\"\n"
                 f"trigger1 = ctrl\ntrigger1 = statetype {'!= A' if tipo == 'C' else '= S'}\n")
        de = [d for d in de if d in n_ok]
        if de:
            r.append("trigger2 = (" + " || ".join(f"stateno = {d}" for d in de) + ") && movecontact && var(5) < 4\n")
        r.append("\n")
    return "".join(r)


MENOS_2 = """[State -2, Demônio: conta acerto da corrente]
type = VarAdd
trigger1 = MoveHit
trigger1 = var(11) = 0
trigger1 = stateno = [4200,4349]
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


def ligar(air, cmd):
    """-> (air, cmd, cns dos estados, linhas do [Statedef -2], {grupo: quadros}) com os golpes que já têm folha."""
    import efeitos
    ok = disponiveis()
    if not ok:
        return air, cmd, "", "", {}
    sprites, estados = {}, []
    for n, g in ok.items():
        quadros, texto, faisca = acao(n, g)
        air = efeitos.por_acao(air, n, texto)
        sprites[GRUPO + n] = quadros
        estados.append(cns(n, g, faisca))
    # no fim do [Statedef -1]: depois do "Pode cancelar" (que reescreve o var(1)) e dos agarrões (frente + y colado
    # continua sendo agarrão); os golpes do Hazak que viriam antes estão travados na forma
    cmd = bloquear_base(cmd).rstrip() + "\n\n" + rotas(set(ok))
    print(f"demônio: {len(ok)} golpes próprios ({', '.join(g['nome'] for g in ok.values())})")
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
