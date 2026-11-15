#!/usr/bin/env python3
"""Fila do Hazak nítido (#36): o anexo e o pedido de cada folha da forma base para o ChatGPT.

  python ferramentas/fila_hazak_nitido.py      grava docs/hazak-36/anexos/<folha>.jpg e docs/hazak-36/fila.json

O anexo é a própria folha de hoje, rearrumada em 2 fileiras de 4 quadros numa imagem 3:2 (1536x1024) com o boneco o
maior que cabe (até ~500 px em pé). Numa fileira só de 8 o Hazak em pé com 500 px não cabe na célula (a base dele é
larga), por isso a grade 4x2. O ChatGPT redesenha a mesma imagem, no mesmo lugar, e o converter_hazaki.py lê a grade.
"""
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import folhas_hazak_arcade as fh  # noqa: E402

SAIDA = fh.RAIZ / "docs/hazak-36"
LARG, ALT = 1536, 1024
CW, CH = LARG // 4, ALT // 2
MARGEM = 14
MAIOR = 500 / 344  # em pé com ~500 px
FORA = ("patroa_", "obj_", "d_")
# as que mais aparecem primeiro: se o limite do plano parar a fila, o que falta é o menos visto
PRIMEIRO = ["parado", "anda", "recuo", "agachado", "pulo", "defesa", "defesa_baixa", "soco", "chute", "baixo_soco",
            "chute_baixo", "ar_soco", "ar_chute", "apanha", "queda", "levanta", "vitoria", "intro", "corrida", "vira"]

QUEM = ("a muscular young karate fighter with warm tan skin, short dark cropped hair with a faded side, clean-shaven; "
        "sleeveless navy-indigo karate top with orange piping on the collar, lapels and hem, wide navy gi pants with "
        "one orange stripe down the outer side of each leg, dark near-black belt knotted at the front with two hanging "
        "tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear wrist only, barefoot")
PEDIDO = (
    "Generate ONE image with your image generation tool. Do not write code and do not edit any file. "
    "The attached image is a low-resolution, blurry sprite sheet of my own original fighting game character: {quem}. "
    "It has 8 frames in a grid of 2 rows and 4 columns on a flat magenta background, read left to right, top row "
    "first. Redraw this exact sprite sheet as a clean, sharp, high-resolution version: a 3:2 landscape image with the "
    "same grid of 2 rows by 4 columns, every figure in the same place, at the same size, in the same pose, with the "
    "same limb positions, the same silhouette and the same facing (right) as in the attached image. Do not change the "
    "character design, the outfit, the colors or the poses, do not add or remove frames, do not reorder them. "
    "What must improve is only the rendering: crisp hand-pixeled 1990s arcade fighting game sprite art with hard "
    "pixel edges, no blur, no anti-aliasing, no soft gradients, no noise; shading in 2-3 hard-edged flat planes per "
    "form; a clean 1-pixel dark colored outline (dark wine on skin, dark blue-purple on clothes); a clearly drawn "
    "face in every frame (eyes, eyebrows, nose, mouth, ear and hairline all readable); clean hands with fingers and "
    "clean bare feet with toes; the orange piping, the belt knot and the wrist wraps drawn sharply. Keep the same "
    "colors as the attached image: tan skin with wine-red shadows, navy-indigo gi, orange piping, white wraps with "
    "lilac shadows, teal wristband on the rear wrist only. "
    "Anatomy: same head size, shoulder width, arm length and leg length in all 8 frames; no extra limbs, no missing "
    "limbs. Each figure stays fully inside its own grid cell and does not touch its neighbors. "
    "Flat solid magenta background (#FF00FF) everywhere, no black bars, no white bars, no grid lines, no shadow, no "
    "ground, no text, no numbers, no borders, no effects (no fire, no sparks, no dust, no speed lines).{extra}")
# pedidos da revisão de anatomia (#51) que cabem sem mudar a pose: só onde a folha de hoje tem defeito grave
CONSERTO = {
    "agarrao_abraco": "In frame 6 keep the spine naturally arched, with the head clearly visible above the shoulders.",
    "ar_soco": "In frames 5 and 6 the punching arm has the same length as the other arm and a normal-sized fist.",
    "cutucao_recuo": "In frames 3 to 6 the extended arm keeps its normal length and thickness.",
    "estatueta_arremesso": "In frames 4 and 5 the raised arm keeps its normal length and thickness and the head stays fully visible.",
    "machado": "In frames 3 and 4 the raised leg keeps the same length and thickness as the standing leg and the torso stays visible.",
    "punho_chao": "In frames 5 and 6 the torso stays fully drawn and the rear leg keeps its normal length.",
    "rasteira": "In frames 3 to 6 the sweeping leg has the same length as the leg in frame 1.",
    "rasteira_arco": "In frames 2 and 7 the arms keep their normal size; in frames 5 and 6 the sweeping leg is a full leg with thigh, shin and foot.",
    "soco_reto": "In frames 4 to 6 the torso keeps its volume, with the shoulder and chest visible.",
    "tesoura": "In frame 5 the body seen from behind keeps the same height, shoulder width and leg length as the other frames, with a normal-sized fist.",
    "voadora": "In frames 4 to 6 the feet keep their normal size and the legs their normal length.",
}


def anexo(nome):
    figs, _ = fh.figuras(fh.ENTRADA / f"{nome}.png")
    assert all(figs), nome
    e = min(MAIOR, min((CW - 2 * MARGEM) / max(q.width for q in figs), (CH - 2 * MARGEM) / max(q.height for q in figs)))
    tela = Image.new("RGB", (LARG, ALT), (255, 0, 255))
    for i, q in enumerate(figs):
        g = q.resize((round(q.width * e), round(q.height * e)), Image.LANCZOS)
        x = (i % 4) * CW + (CW - g.width) // 2
        y = (i // 4) * CH + CH - MARGEM - g.height
        tela.paste(g, (x, y), g)
    tela.save(SAIDA / "anexos" / f"{nome}.jpg", quality=84)
    return e


def main():
    (SAIDA / "anexos").mkdir(parents=True, exist_ok=True)
    nomes = sorted(p.stem for p in fh.ENTRADA.glob("*.png") if not p.stem.startswith(FORA))
    nomes = [n for n in PRIMEIRO if n in nomes] + [n for n in nomes if n not in PRIMEIRO]
    fila = []
    for n in nomes:
        e = anexo(n)
        extra = " Fix while redrawing: " + CONSERTO[n] if n in CONSERTO else ""
        fila.append({"folha": n, "anexo": f"docs/hazak-36/anexos/{n}.jpg", "ampliacao": round(e, 3),
                     "em_pe_px": round(344 * e), "prompt": PEDIDO.format(quem=QUEM, extra=extra)})
    (SAIDA / "fila.json").write_text(json.dumps(fila, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(len(fila), "folhas; em pé de", min(f["em_pe_px"] for f in fila), "a", max(f["em_pe_px"] for f in fila), "px")
    for f in fila:
        if f["em_pe_px"] < 440:
            print("  menor:", f["folha"], f["em_pe_px"])


if __name__ == "__main__":
    main()
