"""Kit de lado e de costas do Hazak (giros): um só desenho de lado e um só de costas para todos os giros.

O kit de frente (kit_hazak.py) não vira de lado. Nos giros (tesoura, chute giratório, giro da garagem) cada desenho
de hoje tinha um corpo diferente; aqui o corpo de lado sai sempre do chute_giratorio/04 e a perna que chuta é peça
(esticada do 04, dobrada do 03) girada no quadril com RotSprite. De costas é sempre o chute_giratorio/02.

Saída: sprites/hazaki/pecas_lado/<folha>/<NN>.png (tela 3x), que o firme.py usa no lugar do desenho de hoje.
    python ferramentas/hazak_lado.py            # monta tudo e grava a folha de contato em docs/boneco-pecas/hazaki
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import boneco_ajuste as ba  # noqa: E402  (RotSprite em RGBA)

RAIZ = Path(__file__).resolve().parent.parent
HD = RAIZ / "sprites/hazaki/quadros_arcade_hd"
SAIDA = RAIZ / "sprites/hazaki/pecas_lado"
REF = "chute_giratorio/04"
COSTAS = "chute_giratorio/02"
QUADRIL = (530, 485)  # junta da perna que chuta no REF
CHAO = 659

# perna que chuta: (desenho de onde sai, polígono nele)
PERNAS = {
    "esticada": ("chute_giratorio/04", [(528, 452), (600, 451), (660, 449), (675, 439), (700, 437), (717, 444),
                                        (717, 502), (700, 507), (675, 502), (640, 503), (600, 506), (565, 509),
                                        (545, 513), (528, 506)]),
    "dobrada": ("chute_giratorio/03", [(526, 450), (560, 447), (600, 449), (616, 457), (622, 475), (614, 493),
                                       (597, 511), (582, 523), (574, 541), (567, 561), (556, 569), (538, 567),
                                       (536, 545), (540, 520), (546, 505), (538, 495), (526, 490)]),
}
# quadro -> (perna, giro em graus no quadril: + desce o pé), ou "costas"
POSES = {
    "chute_giratorio/02": "costas", "giro_garagem/02": "costas", "tesoura/02": "costas",
    "chute_giratorio/03": ("dobrada", 0), "tesoura/04": ("dobrada", 0),
    "chute_giratorio/04": ("esticada", 0), "chute_giratorio/05": ("esticada", 0),
    "giro_garagem/03": ("esticada", 34), "giro_garagem/04": ("esticada", 0), "giro_garagem/05": ("esticada", -2),
    "tesoura/05": ("esticada", -14),
}


def abrir(q):
    return np.array(Image.open(HD / f"{q}.png").convert("RGBA"))


def mascara(shape, poli):
    m = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(m).polygon(poli, fill=255)
    return np.array(m) > 0


def peca(a, m):
    out = np.zeros_like(a)
    out[m] = a[m]
    return out


def deslocamento(fonte, alvo, caixa=(470, 335, 560, 450)):
    """Quanto o tronco de `fonte` está deslocado em `alvo` (casamento da cabeça e do ombro)."""
    x0, y0, x1, y1 = caixa
    t = fonte[y0:y1, x0:x1]
    tg = cv2.cvtColor(np.ascontiguousarray(t[..., :3]), cv2.COLOR_RGB2GRAY)
    ag = cv2.cvtColor(np.ascontiguousarray(alvo[..., :3]), cv2.COLOR_RGB2GRAY)
    ag[alvo[..., 3] == 0] = 0
    tg[t[..., 3] == 0] = 0
    r = cv2.matchTemplate(ag, tg, cv2.TM_SQDIFF, mask=(t[..., 3] > 0).astype(np.uint8))
    _, _, (mx, my), _ = cv2.minMaxLoc(r)
    return mx - x0, my - y0


def colar(tela, img, dx=0, dy=0):
    h, w = tela.shape[:2]
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    mov = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_NEAREST, borderValue=(0, 0, 0, 0))
    m = (mov[..., 3] > 0) & (tela[..., 3] == 0)
    tela[m] = mov[m]


def girar(img, ang, pivo):
    """RotSprite em volta do pivô (ângulo horário na tela)."""
    if not ang:
        return img
    r, x0, y0 = ba.colocar({"junta": pivo}, img, (0, 0), pivo, ang)
    out = np.zeros_like(img)
    ba.colar(out, r, x0, y0)
    return out


def kit():
    ref = abrir(REF)
    # tira a perna com folga de 4 px (o contorno escuro da calça ficaria como um risco no ar) e as migalhas
    perna_ref = cv2.dilate(mascara(ref.shape, PERNAS["esticada"][1]).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    perna_ref &= np.arange(ref.shape[1])[None, :] >= 556  # sem comer a perna de apoio nem a saia
    perna_ref &= np.arange(ref.shape[0])[:, None] >= 490  # só embaixo da perna (em cima é o cinto)
    perna_ref |= mascara(ref.shape, PERNAS["esticada"][1])
    corpo = peca(ref, ~perna_ref)
    al = (corpo[..., 3] > 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(al, connectivity=8)
    for i in range(1, n):
        if st[i, 4] < 200:
            corpo[lab == i] = 0
    pernas = {}
    for nome, (q, poli) in PERNAS.items():
        a = abrir(q)
        p = peca(a, mascara(a.shape, poli) & (a[..., 3] > 0))
        dx, dy = (0, 0) if q == REF else deslocamento(ref, a)
        M = np.float32([[1, 0, -dx], [0, 1, -dy]])  # leva a perna para o lugar do REF
        pernas[nome] = cv2.warpAffine(p, M, (a.shape[1], a.shape[0]), flags=cv2.INTER_NEAREST,
                                      borderValue=(0, 0, 0, 0))
    # raiz da perna (calça logo abaixo da saia): vai por baixo de tudo e tapa o vão quando a perna gira ou dobra
    raiz = peca(ref, mascara(ref.shape, [(526, 452), (566, 452), (566, 514), (526, 514)]) & (ref[..., 3] > 0))
    pernas["_raiz"] = raiz
    return corpo, pernas


def no_chao(tela):
    ys = np.nonzero((tela[..., 3] > 0).any(1))[0]
    return tela if ys.max() == CHAO else np.roll(tela, CHAO - ys.max(), axis=0)


def montar(q, corpo, pernas):
    alvo = abrir(q)
    pose = POSES[q]
    if pose == "costas":
        c = abrir(COSTAS)
        tela = np.zeros_like(c)
        # mesmo meio que o desenho de hoje (o boneco não pula de lugar)
        cx = lambda a: np.nonzero(a[..., 3] > 0)[1].mean()
        colar(tela, c, int(round(cx(alvo) - cx(c))), 0)
        return no_chao(tela)
    nome, ang = pose
    dx, dy = deslocamento(corpo, alvo)
    tela = np.zeros_like(alvo)
    colar(tela, corpo, dx, dy)  # corpo por cima: a perna sai de baixo da saia do quimono
    colar(tela, girar(pernas[nome], ang, QUADRIL), dx, dy)
    colar(tela, pernas["_raiz"], dx, dy)
    return no_chao(tela)


def main():
    corpo, pernas = kit()
    for q in POSES:
        if q.startswith("_"):
            continue
        out = montar(q, corpo, pernas)
        d = SAIDA / q.split("/")[0]
        d.mkdir(parents=True, exist_ok=True)
        Image.fromarray(out).save(SAIDA / f"{q}.png")
        print(q, "ok")
    # folha de contato: hoje x kit de lado
    qs = list(POSES)
    W, H = 300, 340
    F = Image.new("RGB", (W * len(qs), H * 2 + 20), (60, 60, 70))
    dr = ImageDraw.Draw(F)
    for i, q in enumerate(qs):
        for r, a in enumerate((abrir(q), np.array(Image.open(SAIDA / f"{q}.png")))):
            im = Image.fromarray(a).crop((430, 325, 730, 665))
            bg = Image.new("RGBA", im.size, (60, 60, 70, 255))
            bg.alpha_composite(im)
            F.paste(bg.convert("RGB"), (i * W, 20 + r * H))
        dr.text((i * W + 4, 4), q, fill=(255, 255, 0))
    docs = RAIZ / "docs/boneco-pecas/hazaki"
    docs.mkdir(parents=True, exist_ok=True)
    F.save(docs / "kit_lado_contato.png")


if __name__ == "__main__":
    main()
