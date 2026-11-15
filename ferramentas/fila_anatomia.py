#!/usr/bin/env python3
"""Fila do redesenho de anatomia (#51): anexos reduzidos e o prompt de cada folha de revisar_anatomia.FIX.

  python ferramentas/fila_anatomia.py     grava docs/anatomia-51/anexos/<lutador>_<folha>.jpg, as referências
                                          <lutador>_ref.jpg e docs/anatomia-51/fila.json (folha, anexos, prompt)

Os anexos têm 1800x600 com fundo magenta para caberem inteiros na janela do navegador: no Chrome o anexo entra como
captura de tela da imagem aberta pelo endereço raw do GitHub. As folhas d_* do Diabo Loiro vêm da branch origin/bosses.
"""
import io
import json
import subprocess
from pathlib import Path

from PIL import Image

import revisar_anatomia as ra

RAIZ = ra.RAIZ
SAIDA = RAIZ / "docs/anatomia-51/anexos"
S = "sprites"
FOLHAS = {  # nome -> pastas onde procurar <folha>.png, na ordem
    "hazaki": [f"{S}/hazaki/quadros/folhas_arcade"],
    "diabo_loiro": [f"bosses:{S}/hazaki/quadros/folhas_arcade"],
    "ck": [f"{S}/ck/quadros/folhas_arcade"],
    "pengaro": [f"{S}/pengaro/quadros/folhas_novas", f"{S}/pengaro/quadros/folhas_arcade"],
    "gutto": [f"{S}/gutto/quadros/folhas"],
    "raiclaven": [f"{S}/raiclaven/quadros/folhas_arcade", f"{S}/raiclaven/quadros/folhas"],
}
REF = {  # (nome, é a forma despertada) -> folha de referência
    ("hazaki", False): f"{S}/hazaki/quadros/folhas_arcade/parado.png",
    ("diabo_loiro", False): f"bosses:{S}/hazaki/quadros/folhas_arcade/d_parado.png",
    ("ck", False): f"{S}/ck/quadros/folhas_arcade/referencia_ginga.png",
    ("pengaro", False): f"{S}/pengaro/quadros/folhas_novas/ginga.png",
    ("pengaro", True): f"{S}/pengaro/quadros/folhas_arcade/e_ginga.png",
    ("gutto", False): f"{S}/gutto/quadros/folhas/referencia_idle.png",
    ("gutto", True): f"{S}/gutto/quadros/folhas/demonio_modelo.png",
    ("raiclaven", False): f"{S}/raiclaven/quadros/folhas/referencia_ginga.png",
}
QUEM = {
    ("hazaki", False): "a muscular young karate fighter, short dark cropped hair, sleeveless navy gi with orange piping, dark belt, white wrist wraps, a teal wristband on the rear wrist only, barefoot",
    ("diabo_loiro", False): "the 'blond devil' mafia boss: long wild blond mane swept back, two short curved dark horns, wide-brimmed dark hat with an ember-orange band, dark purple pinstripe suit and long overcoat with orange lining, orange tie, gold watch chain, brown leather shoes, a thin devil tail, a brown leather briefcase with gold clasps in the rear hand unless the pose says otherwise",
    ("ck", False): "a slim young boxer in a dark cap with a small green logo patch, white polo shirt, black-and-white wavy patterned shorts, red boxing gloves, white sneakers",
    ("pengaro", False): "a very muscular shirtless capoeira fighter with dark brown skin and short curly black hair, white capoeira pants with green and yellow side stripes, a green cord belt with yellow tips, an olive green shin guard on the front shin only, barefoot, a whisky bottle with a blank cream label always in the rear hand",
    ("pengaro", True): "the possessed demon form: dark purple-brown skin, long wild dark hair with violet tips, two short smoke horns, a sleeveless black master coat with gold trim and purple lining torn at the hem, a braided gold and violet rope belt, black pants, broken chain shackles on both wrists and ankles, gold bracelets, no bottle",
    ("gutto", False): "a muscular Muay Thai fighter with dark reddish-brown skin, short curly black hair and a thick black mustache, shirtless, black satin shorts with a white waistband and white trim, white hand wraps, twisted rope armbands on both biceps, barefoot",
    ("gutto", True): "the demon stallion form: a massive hunched horse-headed beast with dark red skin, a long wild black mane, short horns, glowing eyes, huge clawed hands, black hooves, a black horse tail, a white rope armband and a white waistband on black shorts",
    ("raiclaven", False): "a stocky smiling barber with dark skin and a short flat-top haircut, black barber shirt with a small red-white-blue barber pole badge, a black apron with a cream logo over black pants and black shoes, a full metal armored rear arm with a big shoulder plate holding giant steel scissors, a small purple straight razor in the front hand",
}
ESTILO = (
    "Art style: hand-pixeled 1990s arcade fighting game sprite, exactly like the reference sheet: same pixel size, same "
    "palette, same shading in 2-3 hard-edged flat planes per form, same colored 1-pixel outline, no gradients, no noise. "
    "Layout: one single row of 8 frames, evenly spaced, wide 3:1 image, always facing right, same character size and scale "
    "as the reference sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta "
    "background (#FF00FF) everywhere, no black bars, no shadow, no ground, no text, no numbers, no borders, no effects "
    "(no fire, no sparks, no dust, no smoke, no speed lines, no motion trails)."
)
TRAVA = (
    "Anatomy lock: in all 8 frames the character has exactly the same head size, shoulder width, torso length, arm length "
    "and leg length as in the reference sheet. Arms and legs never stretch: an extended arm is as long as the arm at rest, "
    "an extended leg is as long as the standing leg. Only on the single contact frame the striking fist or foot may be up "
    "to 15% larger, never longer. When he turns his back or faces the camera, height, shoulder width and leg length stay "
    "the same as in side view. Clothes, wraps, accessories and props stay on the same limb and the same size in every "
    "frame. No extra limbs, no missing limbs, both feet fully drawn."
)


def abrir(caminho):
    if caminho.startswith("bosses:"):
        dados = subprocess.run(["git", "show", "origin/bosses:" + caminho[7:]], cwd=RAIZ, capture_output=True, check=True).stdout
        return Image.open(io.BytesIO(dados)).convert("RGBA")
    return Image.open(RAIZ / caminho).convert("RGBA")


def existe(caminho):
    if caminho.startswith("bosses:"):
        return subprocess.run(["git", "cat-file", "-e", "origin/bosses:" + caminho[7:]], cwd=RAIZ).returncode == 0
    return (RAIZ / caminho).exists()


def reduzir(img, destino):
    fundo = Image.new("RGBA", img.size, (255, 0, 255, 255))
    fundo.alpha_composite(img)
    s = min(1800 / img.width, 600 / img.height)
    pq = fundo.convert("RGB").resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    tela = Image.new("RGB", (1800, 600), (255, 0, 255))
    tela.paste(pq, ((1800 - pq.width) // 2, (600 - pq.height) // 2))
    tela.save(destino, quality=92)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    fila = []
    for (nome, desp), ref in REF.items():
        assert existe(ref), ref
        reduzir(abrir(ref), SAIDA / f"{nome}_{'e_' if desp else ''}ref.png")
    for nome, folhas in ra.FIX.items():
        for folha, fix in folhas.items():
            desp = folha.startswith("e_") and (nome, True) in REF and folha != "e_despertar"
            origem = next((f"{p}/{folha}.png" for p in FOLHAS[nome] if existe(f"{p}/{folha}.png")), None)
            assert origem, f"{nome}/{folha}: sem folha"
            reduzir(abrir(origem), SAIDA / f"{nome}_{folha}.jpg")
            prompt = (
                "Generate ONE image with your image generation tool. Do not write code and do not edit any file. "
                f"The FIRST attached image is the reference sprite sheet and shows the exact character to keep, with the same "
                f"face, body, outfit and colors: {QUEM[(nome, desp)]}. {ESTILO} "
                "MOTION: the same 8 poses, in the same order, as the SECOND attached image. "
                "This is a correction of the SECOND attached image: keep its 8 poses, timing and framing, and redraw it "
                f"fixing anatomy. {TRAVA} FIX: {fix}. "
                "Consecutive frames differ by a small amount, so the motion looks smooth in sequence."
            )
            fila.append(dict(lutador=nome, folha=folha, origem=origem, ref=f"{nome}_{'e_' if desp else ''}ref.png",
                             anexo=f"{nome}_{folha}.jpg", prompt=prompt))
    (RAIZ / "docs/anatomia-51/fila.json").write_text(json.dumps(fila, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(fila), "folhas na fila")


if __name__ == "__main__":
    main()
