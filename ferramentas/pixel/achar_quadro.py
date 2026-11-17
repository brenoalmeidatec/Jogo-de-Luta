"""De qual quadro (pasta/ação/NN.png) saiu um sprite do .sff do jogo (#51: consertar o que a tira do jogo mostrou).

  python3 ferramentas/pixel/achar_quadro.py pengaro 91,0 578,0 471,0

Compara o sprite (recortado pelo alfa) com todo quadro das pastas do lutador (grande e 1x, desenhos e meio/),
também espelhado, e mostra os 3 mais parecidos com a diferença média por pixel (0 = igual; até ~6 é o mesmo desenho
depois da paleta do .sff).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))
from conferir_sff import ler  # noqa: E402
from tira_jogo import imagem  # noqa: E402
from quadros import PASTAS, SPRITES, RAIZ  # noqa: E402

PASTAS_EXTRA = {"hazaki": ["hazaki/diabo_terno"], "gutto": ["gutto/quadros_hd"], "raiclaven": ["raiclaven/quadros_hd"]}


def recorte(a):
    m = a[..., 3] > 127
    if not m.any():
        return None
    ys, xs = np.nonzero(m)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def candidatos(lutador):
    grande, pequeno, _ = PASTAS[lutador]
    pastas = [grande] + ([pequeno] if pequeno else []) + PASTAS_EXTRA.get(lutador, [])
    for p in pastas:
        base = SPRITES / p
        if base.exists():
            yield from base.glob("*/[0-9][0-9].png")
            yield from base.glob("*/meio/*.png")


def achar(lutador, chaves):
    pal, nos, _ = ler(RAIZ / "chars" / lutador / f"{lutador}.sff")
    sprites = {}
    for n in nos:
        sprites.setdefault((n["g"], n["i"]), n)
    alvos = {}
    for c in chaves:
        g, i = (int(v) for v in c.split(","))
        alvos[c] = recorte(np.array(imagem(sprites[(g, i)], pal)))
    melhores = {c: [] for c in chaves}
    for arq in candidatos(lutador):
        a = recorte(np.array(Image.open(arq).convert("RGBA")))
        if a is None:
            continue
        for c, s0 in alvos.items():
            s = s0
            for esp, b in ((False, a), (True, a[:, ::-1])):
                if b.shape[:2] != s.shape[:2]:
                    # sprite HD do Blender (Gutto, Raiclaven): 3x do quadro de 1x, compara reduzido
                    if abs(b.shape[0] * 3 - s.shape[0]) > 4 or abs(b.shape[1] * 3 - s.shape[1]) > 4:
                        continue
                    import cv2
                    s = cv2.resize(alvos[c], (b.shape[1], b.shape[0]), interpolation=cv2.INTER_AREA)
                m = (b[..., 3] > 127) | (s[..., 3] > 127)
                d = float(np.abs(b[..., :3].astype(int) - s[..., :3].astype(int))[m].mean())
                d += 255 * float(((b[..., 3] > 127) != (s[..., 3] > 127)).mean())
                melhores[c].append((d, str(arq.relative_to(SPRITES)), esp))
    for c in chaves:
        top = sorted(melhores[c])[:3]
        print(c, " | ".join(f"{p}{' (espelhado)' if e else ''} d={d:.1f}" for d, p, e in top) or "nada do mesmo tamanho")
    return {c: sorted(melhores[c])[:3] for c in chaves}


if __name__ == "__main__":
    achar(sys.argv[1], sys.argv[2:])
