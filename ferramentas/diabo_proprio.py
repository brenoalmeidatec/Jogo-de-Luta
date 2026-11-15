#!/usr/bin/env python3
"""Desenho próprio do Diabo Loiro para os golpes que usavam a folha mais parecida (issue #44, Breno 2026-11-15).

Até aqui 20 ações do Hazak não tinham folha `d_*` própria e o Diabo repetia o quadro de outro golpe (lista PARECIDA do
diabo_terno.py); a estatueta_arremesso usava a folha do Chapéu Bumerangue, que o Breno mandou tirar. O Breno pediu
desenho próprio para todas, na roupa do sobretudo, batendo com o movimento e a caixa do golpe do Hazak.

Processo (o mesmo do Hazak nítido, #36): a folha nítida do Hazak (sprites/hazaki/quadros/folhas_novas/<ação>.png, grade
4x2) e o conceito (d_conceito.png) vão anexos ao ChatGPT, que redesenha a MESMA grade com o Diabo. A folha volta para
sprites/hazaki/quadros/folhas_diabo/d_<ação>.png e este script corta as 8 figuras, põe na escala do 3x do Hazak (a mesma
razão folha -> 3x da folha nítida da ação), aplica o acabamento de chefão do diabo_terno.py e grava
sprites/hazaki/diabo_terno/d_<ação>/NN.png. O diabo_terno.FOLHA passa a apontar para ela sozinho (PROPRIAS).

  python ferramentas/diabo_proprio.py --fila          anexos em docs/diabo-44/anexos/ e pedidos em docs/diabo-44/fila.json
  python ferramentas/diabo_proprio.py                 converte todas as folhas que já existem em folhas_diabo/
  python ferramentas/diabo_proprio.py jab_duplo ...   só essas
  python ferramentas/diabo_proprio.py --contato DIR   Hazak (em cima) e Diabo (embaixo), 3x, para conferir

Não mexe nas 44 pastas d_* que vieram da branch bosses (essas são da thread da anatomia, #51).
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import converter_hazaki as ch  # noqa: E402
import diabo_terno as dt  # noqa: E402

RAIZ = ch.RAIZ
SPRITES = ch.SPRITES
FOLHAS_HAZAK = ch.FOLHAS
FOLHAS_DIABO = SPRITES / "quadros/folhas_diabo"
DOCS = RAIZ / "docs/diabo-44"
E = ch.E

ACOES = ["intro", "provoca", "jab_duplo", "cutucao", "tapa_costas", "chute_gancho", "chute_alto_rajada", "rasteira",
         "tesoura", "ar_chute", "ascensao", "sobe_chutando", "passagem_rapida", "guarda_aco", "parry_alto",
         "parry_baixo", "estatueta_arremesso", "despertar_pedido", "vitima_agarrado", "vitima_arremessado",
         "derrota_sirene"]

# o que muda da folha do Hazak para a do Diabo, golpe a golpe (o resto é a mesma pose)
NOTA = {
    "parry_alto": "In this sheet he holds the briefcase OPEN in front of his chest with both hands, like a shield, in "
                  "the frames where the first image raises the guard; the rest of the body keeps the same pose.",
    "parry_baixo": "In the last frames he touches the hat brim with the front hand.",
    "guarda_aco": "The briefcase stays in the rear hand, raised in front of the body as part of the guard.",
    "vitima_agarrado": "He is being grabbed and thrown: no briefcase in this sheet, both hands empty; the hat stays on.",
    "vitima_arremessado": "He is being thrown and falls: no briefcase in this sheet, both hands empty; the hat stays on.",
    "derrota_sirene": "No briefcase in this sheet, both hands empty; the hat stays on.",
    "estatueta_arremesso": "The FRONT hand throws (it is empty: the thrown object is a separate sprite); the briefcase "
                           "stays in the rear hand.",
    "despertar_pedido": "Keep the same gestures as the first image.",
}

QUEM = (
    "HAZAK in his awakened form, the Blond Devil: the same young clean-shaven man with the same body size and "
    "proportions, a long wild blond mane swept straight back over the head and down the back (never spiked up), "
    "glowing red eyes, a confident grin; two curved dark horns with ember-orange tips grow from his head and pass "
    "THROUGH two holes in the crown of a big wide-brimmed dark hat with an ember-orange band; a dark navy-purple "
    "double-breasted pinstripe suit with gold buttons and a gold watch chain, wide pinstripe trousers, white shirt, "
    "ember-orange tie; a long dark overcoat with an ember-orange lining resting on his shoulders like a cape, sleeves "
    "empty and hanging; a chunky gold ring on the front hand; dark brown leather dress shoes with white spats; a thin "
    "dark devil tail with a spade tip below the coat; the teal wristband over the shirt cuff of the REAR wrist only; a "
    "dark brown leather briefcase with gold clasps in the REAR hand")

PEDIDO = (
    "Generate ONE image with your image generation tool. Do not write code and do not edit any file. "
    "The FIRST attached image is a sprite sheet of my own original fighting game character in his normal karate gi: "
    "8 frames in a grid of 2 rows and 4 columns on a flat magenta background, read left to right, top row first. "
    "The SECOND attached image is the approved concept of his awakened form: copy the LEFTMOST figure (the one "
    "without wings). Redraw the FIRST image as the same sprite sheet with the character changed into {quem}. "
    "Keep exactly the same grid of 2 rows by 4 columns in a 3:2 landscape image, every figure in the same place, at "
    "the same size, in the same pose, with the same limb positions, the same body silhouette and the same facing "
    "(right) as in the first image: only the outfit, the hair, the horns, the hat, the tail and the briefcase change. "
    "Do not add or remove frames, do not reorder them. {nota}"
    "MODEL LOCK, true in all 8 frames: exactly two arms, two hands, two legs, one tail, two horns; the overcoat always "
    "stays on the shoulders as a cape and his arms never go into its sleeves; the cape, the tie and the tail lag one "
    "frame behind the body; hair blond, never dark; same head size, shoulder width, arm length and leg length in all "
    "8 frames. Art style: crisp hand-pixeled 1990s arcade fighting game sprite, hard pixel edges, no blur, no "
    "anti-aliasing, no gradients, no dithering, no noise; shading in 2-3 hard-edged flat planes per form; a clean "
    "1-pixel colored outline (dark wine on skin, dark blue-purple on clothes); a clearly drawn face in every frame. "
    "Each figure stays fully inside its own grid cell and does not touch its neighbors. Flat solid magenta background "
    "(#FF00FF) everywhere, no black bars, no white bars, no grid lines, no shadow, no ground, no text, no numbers, no "
    "borders, no logos, no effects (no wings, no crown, no fire, no embers, no smoke, no banknotes, no aura, no "
    "sparks, no speed lines).")


# golpe novo do Diabo (no lugar do Chapéu Bumerangue): não tem folha do Hazak; a da corrida dá o tamanho e a grade
NOVOS = {"cobranca": ("corrida",
    "MOTION (new poses, the first image only gives the figure size and the grid layout): a heavy shoulder-charge "
    "special move. 1 standing guard holding the briefcase in the rear hand; 2 he sinks a little and the front hand "
    "pulls the overcoat open, the ember lining showing; 3 he drives forward low, front shoulder first, body leaning "
    "forward, briefcase pulled back behind the hip, coat and tail streaming behind; 4 the same low charge, the other "
    "foot gliding; 5 the charge at full speed, shoulder and front elbow leading; 6 contact: the front shoulder and "
    "elbow slam forward, the shoulder drawn 15% larger, feet planted; 7 he straightens up, briefcase back at his side; "
    "8 he adjusts his tie with two fingers of the front hand, grinning. ")}


def fila():
    anexos = DOCS / "anexos"
    anexos.mkdir(parents=True, exist_ok=True)
    for nome in ACOES:
        Image.open(FOLHAS_HAZAK / f"{nome}.png").convert("RGB").save(anexos / f"{nome}.jpg", quality=92)
    conceito = SPRITES / "quadros/folhas_diabo/d_conceito.png"
    Image.open(conceito).convert("RGB").save(anexos / "conceito.jpg", quality=92)
    pedidos = [{"folha": f"d_{n}", "anexo": f"{n}.jpg",
                "prompt": PEDIDO.format(quem=QUEM, nota=(NOTA[n] + " ") if n in NOTA else "")} for n in ACOES]
    for n, (base, motion) in NOVOS.items():
        Image.open(FOLHAS_HAZAK / f"{base}.png").convert("RGB").save(anexos / f"{n}.jpg", quality=92)
        texto = PEDIDO.format(quem=QUEM, nota=motion).replace(
            "in the same pose, with the same limb positions, the same body silhouette and the same facing (right) as in "
            "the first image: only the outfit, the hair, the horns, the hat, the tail and the briefcase change.",
            "and with the same facing (right) as in the first image, but in the new poses of the MOTION below.")
        pedidos.append({"folha": f"d_{n}", "anexo": f"{n}.jpg", "prompt": texto})
    (DOCS / "fila.json").write_text(json.dumps(pedidos, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(pedidos)} pedidos em {(DOCS / 'fila.json').relative_to(RAIZ)}")


def escala_3x(nome):
    """Razão tamanho no 3x / tamanho na folha nítida do Hazak, mediana dos 8 quadros (mesma grade e mesmo tamanho
    de boneco na folha do Diabo)."""
    figs = ch.figuras(FOLHAS_HAZAK / f"{nome}.png")
    r = []
    for i, q in enumerate(figs):
        a = np.array(Image.open(SPRITES / "quadros_arcade_hd" / nome / f"{i:02d}.png"))[..., 3] > 0
        ys, xs = np.nonzero(a)
        r.append((ys.max() - ys.min() + 1) / q.height)
        r.append((xs.max() - xs.min() + 1) / q.width)
    return float(np.median(r))


# O Diabo das 44 folhas antigas tem 1,15 vez a altura do Hazak em pé (chapéu e chifres). Na folha nova o ChatGPT põe o
# Diabo inteiro (com chapéu) no tamanho do Hazak, então o corpo vem menor: a escala volta para esses 1,15 medidos nos
# quadros em pé; folha sem quadro em pé usa o lado maior (1,10). Golpe novo (sem Hazak): o 1º quadro (guarda) com a
# altura do d_parado.
DIABO_EM_PE, DIABO_LADO = 1.15, 1.10


def _tam(img):
    b = img.getbbox()
    return b[3] - b[1], b[2] - b[0]


def acerto_diabo(nome, figs, e):
    if nome in NOVOS:
        alvo = _tam(Image.open(dt.SAIDA / "d_parado/00.png"))[0]
        return alvo / (figs[0].height * e)
    hz = [_tam(Image.open(SPRITES / "quadros_arcade_hd" / nome / f"{i:02d}.png")) for i in range(8)]
    em_pe = [(q.height * e) / h for q, (h, w) in zip(figs, hz) if h > 1.1 * w]
    if len(em_pe) >= 3:
        return DIABO_EM_PE / float(np.median(em_pe))
    return DIABO_LADO / float(np.median([max(q.size) * e / max(h, w) for q, (h, w) in zip(figs, hz)]))


def converter(nome):
    folha = FOLHAS_DIABO / f"d_{nome}.png"
    figs = ch.figuras(folha)
    assert all(q is not None for q in figs), f"d_{nome}: figura faltando na folha"
    e = escala_3x(NOVOS[nome][0] if nome in NOVOS else nome)
    k = acerto_diabo(nome, figs, e)
    e *= k
    destino = dt.SAIDA / f"d_{nome}"
    destino.mkdir(parents=True, exist_ok=True)
    for i, q in enumerate(figs):
        tres = ch.seco(q.resize((max(1, round(q.width * e)), max(1, round(q.height * e))), Image.LANCZOS))
        red = np.array(tres)
        Image.fromarray(dt.quantizar(dt.chefao(red))).save(destino / f"{i:02d}.png", optimize=True)
    print(f"d_{nome}: escala {e:.4f} (acerto do Diabo {k:.3f}), figura {max(q.height for q in figs)} px na folha")


def contato(saida, nomes):
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    for nome in nomes:
        w, h = 300, 420
        tela = Image.new("RGB", (w * 8, h * 2), (110, 112, 118))
        for i in range(8):
            base = NOVOS[nome][0] if nome in NOVOS else nome
            hz = Image.open(SPRITES / "quadros_arcade_hd" / base / f"{i:02d}.png").convert("RGBA")
            c = hz.getbbox()
            hz = hz.crop(c)
            tela.paste(hz, (i * w + (w - hz.width) // 2, h - hz.height), hz)
            p = dt.SAIDA / f"d_{nome}" / f"{i:02d}.png"
            if p.exists():
                d = Image.open(p).convert("RGBA")
                tela.paste(d, (i * w + (w - d.width) // 2, 2 * h - d.height), d)
        tela.save(saida / f"{nome}.png")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--fila" in args:
        fila()
    elif "--contato" in args:
        k = args.index("--contato")
        resto = [a for a in args[:k] + args[k + 2:] if not a.startswith("--")]
        contato(args[k + 1], resto or [n for n in ACOES if (dt.SAIDA / f"d_{n}").exists()])
    else:
        for n in [a for a in args if not a.startswith("--")] or [n for n in ACOES + list(NOVOS)
                                                                  if (FOLHAS_DIABO / f"d_{n}.png").exists()]:
            converter(n)
