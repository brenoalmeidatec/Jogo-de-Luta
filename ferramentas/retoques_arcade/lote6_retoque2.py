"""Retoque 2 do Lote 6 do Pengaró (2026-11-11), em cima dos quadros de sprites/pengaro/quadros_arcade/. Registro do que
foi feito à mão depois da revisão cética; rodar de novo não muda nada (cada passo confere se já foi aplicado).

    python ferramentas/retoques_arcade/lote6_retoque2.py

1. caneta 0, 1, 2, 6, 7: a figura terminava 4 ou 5 px acima do chão (linha 214/215 em vez de 219): desce até o chão.
2. defesa 3: 18 pixels lilás e roxo (cor da sombra da calça) no rosto, entre o olho e o antebraço: viram pele e contorno.
3. cabelo: compasso 1 a 5 e lata 4 saíram com o cabelo nos vinhos da pele. Dentro da caixa da cabeça, os vinhos
   ligados ao cabelo (oliva ou escuro) viram o escuro do cabelo.
4. agarrao 4 e 5 (de costas): espelhados, para a garrafa e a caneleira continuarem do lado de trás da TELA, como nas
   outras vistas de costas (armada 2 e 3, bola 3). Antes a garrafa pulava de lado por 12 ticks no meio do agarrão.
"""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

R = Path(__file__).resolve().parents[2] / "sprites/pengaro/quadros_arcade"
CHAO = 219  # última linha da figura com os pés no chão (EIXO_Y - 1)
VINHOS = ((0x8A, 0x32, 0x1C), (0x5F, 0x1A, 0x14))
ESCURO, OLIVA = (0x33, 0x2C, 0x20), (0x75, 0x6C, 0x4E)
PELE, CONTORNO = (0xDF, 0x7E, 0x3F), (0x4C, 0x14, 0x14)
LILAS, ROXO = (148, 146, 189), (53, 31, 92)


def eh(a, c):
    return (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & (a[..., 3] > 0)


def abre(rel):
    return np.array(Image.open(R / rel).convert("RGBA"))


def salva(rel, a):
    Image.fromarray(a).save(R / rel)


def no_chao(rel):
    a = abre(rel)
    ys = np.flatnonzero((a[..., 3] > 0).any(axis=1))
    d = CHAO - int(ys[-1])
    if d > 0:
        b = np.zeros_like(a)
        b[d:] = a[:-d]
        salva(rel, b)
    return d


def troca_na_caixa(rel, caixa, de_para):
    a = abre(rel)
    x0, y0, x1, y1 = caixa
    dentro = np.zeros(a.shape[:2], bool)
    dentro[y0:y1 + 1, x0:x1 + 1] = True
    n = 0
    for de, para in de_para:
        m = dentro & eh(a, de)
        a[m, :3] = para
        n += int(m.sum())
    salva(rel, a)
    return n


def cabelo(rel, caixa):
    """Vinhos da caixa ligados (8 vizinhos) a um pixel oliva ou escuro do cabelo viram o escuro."""
    a = abre(rel)
    x0, y0, x1, y1 = caixa
    dentro = np.zeros(a.shape[:2], bool)
    dentro[y0:y1 + 1, x0:x1 + 1] = True
    vinho = (eh(a, VINHOS[0]) | eh(a, VINHOS[1])) & dentro
    semente = (eh(a, ESCURO) | eh(a, OLIVA)) & dentro
    rot, _ = ndimage.label(vinho | semente, structure=np.ones((3, 3)))
    alvo = vinho & np.isin(rot, np.unique(rot[semente]))
    a[alvo, :3] = ESCURO
    salva(rel, a)
    return int(alvo.sum())


def espelha(rel):
    """Espelha a figura em torno do centro da própria caixa (a base não sai do lugar). Já espelhado = caneleira (oliva)
    do lado esquerdo da figura."""
    a = abre(rel)
    xs = np.flatnonzero((a[..., 3] > 0).any(axis=0))
    x0, x1 = int(xs[0]), int(xs[-1])
    ox = np.nonzero(eh(a, OLIVA)[190:])[1]
    if ox.mean() < (x0 + x1) / 2:
        return False
    a[:, x0:x1 + 1] = a[:, x0:x1 + 1][:, ::-1].copy()
    salva(rel, a)
    return True


CABELOS = {
    "compasso/01.png": (200, 146, 225, 157), "compasso/02.png": (194, 160, 214, 169),
    "compasso/03.png": (198, 150, 216, 162), "compasso/04.png": (146, 155, 164, 167),
    "compasso/05.png": (195, 133, 214, 144), "lata/04.png": (160, 108, 172, 128),
}

if __name__ == "__main__":
    for q in (0, 1, 2, 6, 7):
        print("caneta", q, "desce", no_chao(f"caneta/{q:02d}.png"))
    print("defesa 3:", troca_na_caixa("defesa/03.png", (195, 120, 203, 132), ((LILAS, PELE), (ROXO, CONTORNO))))
    for rel, caixa in CABELOS.items():
        print("cabelo", rel, cabelo(rel, caixa))
    for q in (4, 5):
        print("agarrao", q, "espelhado" if espelha(f"agarrao/{q:02d}.png") else "já estava")
