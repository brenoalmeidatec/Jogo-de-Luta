"""Troca só os desenhos de golpes que já estão no jogo (ligados pelo ligar_pecas.py), quando a pose mudou e o tempo não.

    python3 ferramentas/trocar_desenhos.py <lutador> <golpe ...> [--de <pasta>] [--grupo 48000]

O ligar_pecas.py reescreve a ação do .air e os AnimElem do .cns: rodá-lo de novo em cima de um golpe já ligado parte
os elementos outra vez. Quando a pose muda e o tempos.json fica igual (mesmos desenhos, mesmos ticks; ex.: estudo de
anatomia do Breno, 17/11, que mudou camada e ângulo), basta trocar os desenhos do grupo no .sff, no mesmo (grupo,
índice): a ação, as caixas, os AnimElem e o remap do despertado continuam valendo.

Cada desenho sai como o ligar_pecas grava: recortado no eixo (540, 660). Grupo do lutador: indexado na paleta dele.
Grupo de outra pasta (`--de`, o despertado): se o grupo já está indexado numa paleta própria (encolher_sff.py), o
desenho novo entra nessa mesma paleta; senão vai em PNG RGBA, como no ligar_pecas.

Depois rode aura_silhueta.py <lutador> (a aura é tirada do contorno dos desenhos) e encolher_sff.py.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conferir_sff as cs  # noqa: E402
import efeitos  # noqa: E402
import encolher_sff as enc  # noqa: E402
import ligar_pecas as lp  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent


def trocar(lutador, golpes, grupo_base=48000, de=None):
    chars = RAIZ / "chars" / lutador
    sff = chars / f"{lutador}.sff"
    spr = RAIZ / "sprites" / (de or lutador) / "quadros_pecas_hd"
    todos = sorted(p.name for p in spr.iterdir() if (p / "tempos.json").exists())
    pal, nos, _ = cs.ler(sff)
    extras = list(cs.EXTRAS.get(str(sff.resolve()), []))
    prgb = lp.paleta_rgb(pal)
    por_chave = {}
    for n in nos:
        por_chave.setdefault((n["g"], n["i"]), n)
    novos = {}
    for golpe in golpes:
        g = grupo_base + todos.index(golpe)
        tempos = json.loads((spr / golpe / "tempos.json").read_text(encoding="utf-8"))
        desenhos = sorted({e["desenho"] for e in tempos["elementos"]})
        tem = sorted(i for (gg, i) in por_chave if gg == g)
        # com --ajustar o ligar_pecas tira o quadro que ficou com 0 tick: o .sff pode ter menos desenhos que a pasta
        assert tem and set(tem) <= set(desenhos), f"{golpe}: o .sff tem os desenhos {tem} no grupo {g} e a pasta " \
                                                  f"{desenhos}; o tempo mudou, use o ligar_pecas.py"
        for i in tem:
            novos[(g, i)] = spr / golpe / f"{i:02d}.png"
    rle, png = [], []
    for k, n in por_chave.items():
        if k in novos:
            continue
        if n.get("png"):
            png.append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
        else:
            rle.append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"], n.get("pi", 0)))
    for (g, i), arq in sorted(novos.items()):
        img, ex, ey = lp.recortar(Image.open(arq).convert("RGBA"))
        velho = por_chave[(g, i)]
        a = np.asarray(img).copy()
        a[..., 3] = np.where(a[..., 3] > 127, 255, 0)
        if de and not velho.get("png") and velho.get("pi", 0) >= 2:
            p = np.frombuffer(extras[velho["pi"] - 2], np.uint8).reshape(256, 4)
            rle.append((g, i, img.width, img.height, int(ex), int(ey), enc.indexar(a, p).tobytes(), velho["pi"]))
        elif de:
            png.append((g, i, img.width, img.height, int(ex), int(ey), efeitos.blob_png(img)))
        else:
            rle.append((g, i, img.width, img.height, int(ex), int(ey), lp.indexar(img, prgb).tobytes(),
                        velho.get("pi", 0)))
    efeitos.gravar(sff, pal, rle, png, extras)
    print(f"{len(novos)} desenhos trocados em {', '.join(golpes)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lutador")
    ap.add_argument("golpes", nargs="+")
    ap.add_argument("--de")
    ap.add_argument("--grupo", type=int, default=48000)
    a = ap.parse_args()
    trocar(a.lutador, a.golpes, a.grupo, a.de)


if __name__ == "__main__":
    main()
