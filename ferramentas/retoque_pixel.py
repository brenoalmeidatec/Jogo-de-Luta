"""Retoque de pixel nos desenhos de sprites/<lutador>/quadros (usado no pente fino de anatomia do Pengaro, 2026-11-11).

Funcoes: zoomg (zoom com regua de coordenadas), caneleiras / tirar_caneleira / recolorir (caneleira que aparece na perna
errada vira calca), apagar_regiao (objeto a mais), apagar (inpaint). Os retoques valem ate alguem rodar animar_folha.py
na mesma folha, que recorta tudo de novo da folha crua."""
import numpy as np, cv2
from PIL import Image

def canais(a):
    r, g, b = (a[..., i].astype(int) for i in range(3))
    return r, g, b, np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)

def apagar(arquivo, caixa, teste, dilata=1, transparente=False):
    im = Image.open(arquivo).convert("RGBA"); a = np.array(im)
    m = np.zeros(a.shape[:2], bool); x0, y0, x1, y1 = caixa
    m[y0:y1 + 1, x0:x1 + 1] = True
    m &= (a[..., 3] >= 128) & teste(*canais(a))
    if dilata and not transparente:
        m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=dilata).astype(bool) & (a[..., 3] >= 128)
        m[:y0] = m[y1 + 1:] = False; m[:, :x0] = m[:, x1 + 1:] = False
    if transparente:
        a[m] = 0
    else:
        a[..., :3] = cv2.inpaint(np.ascontiguousarray(a[..., :3]), m.astype(np.uint8) * 255, 3, cv2.INPAINT_TELEA)
    Image.fromarray(a).save(arquivo); print(arquivo, int(m.sum()), "px")

cinza = lambda r, g, b, mx, mn: (mx > 110) & (mx - mn < 60)

def oliva_mask(a):
    """Pixels da caneleira (verde-oliva escuro, pouco saturado) e os pontos vermelhos presos dentro dela."""
    r, g, b, mx, mn = canais(a)
    op = a[..., 3] >= 128
    ol = op & (g >= r - 6) & (g >= b) & (mx > 45) & (mx < 150) & (mx - mn < 60) & (mx - mn > 6)
    ol = cv2.morphologyEx(ol.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    n, rot, st, _ = cv2.connectedComponentsWithStats(ol, connectivity=8)
    m = np.zeros(ol.shape, bool)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 25:
            m |= rot == i
    fechado = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)).astype(bool) & op
    return fechado

def caneleiras(arquivo):
    a = np.array(Image.open(arquivo).convert("RGBA"))
    m = oliva_mask(a)
    n, rot, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    return [(tuple(int(v) for v in st[i, :4]), int(st[i, 4])) for i in range(1, n) if st[i, 4] >= 25]

def virar_calca(arquivo, caixa, sombra=(176, 170, 200), claro=(244, 240, 236)):
    """Caneleira dentro da caixa (x0,y0,x1,y1) vira calça: mesma luz relativa, nas cores da calça. O contorno fica."""
    im = Image.open(arquivo).convert("RGBA"); a = np.array(im)
    m = oliva_mask(a); x0, y0, x1, y1 = caixa
    fora = np.ones(m.shape, bool); fora[y0:y1 + 1, x0:x1 + 1] = False; m[fora] = False
    transp = a[..., 3] < 128
    borda = cv2.dilate(transp.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    m &= ~borda
    lum = a[..., :3].astype(float).mean(-1)
    if m.sum():
        lo, hi = np.percentile(lum[m], 5), np.percentile(lum[m], 95)
        t = np.clip((lum - lo) / max(1, hi - lo), 0, 1)
        t = np.round(t * 3) / 3  # blocos, sem degradê
        cor = np.array(sombra)[None, None] * (1 - t[..., None]) + np.array(claro)[None, None] * t[..., None]
        a[m, :3] = cor[m].astype(np.uint8)
    Image.fromarray(a).save(arquivo); print(arquivo, int(m.sum()), "px viraram calça")

def escuro_nao_pele(a):
    r, g, b, mx, mn = canais(a)
    return (a[..., 3] >= 128) & (mx < 165) & ~((r > 125) & (r - b > 45)) | ((a[..., 3] >= 128) & (r > g + 40) & (mx < 150) & (g < 80))

def recolorir(arquivo, caixa, sombra=(176, 170, 200), claro=(244, 240, 236), niveis=3, teste=escuro_nao_pele, manter_borda=True):
    """Dentro da caixa, o que passa no teste é repintado entre `sombra` e `claro` pela luz relativa (em blocos)."""
    im = Image.open(arquivo).convert("RGBA"); a = np.array(im)
    x0, y0, x1, y1 = caixa
    m = np.zeros(a.shape[:2], bool); m[y0:y1 + 1, x0:x1 + 1] = True
    m &= teste(a)
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)).astype(bool) & (a[..., 3] >= 128)
    if manter_borda:
        m &= ~cv2.dilate((a[..., 3] < 128).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    lum = a[..., :3].astype(float).mean(-1)
    if m.sum():
        lo, hi = np.percentile(lum[m], 10), np.percentile(lum[m], 90)
        t = np.clip((lum - lo) / max(1, hi - lo), 0, 1)
        t = np.round(t * niveis) / niveis
        cor = np.array(sombra)[None, None] * (1 - t[..., None]) + np.array(claro)[None, None] * t[..., None]
        a[m, :3] = cor[m].astype(np.uint8)
    Image.fromarray(a).save(arquivo); print(arquivo, int(m.sum()), "px repintados")

def zoom(arquivos, saida, caixa, z=8):
    ims = []
    for f in arquivos:
        im = Image.open(f).convert("RGBA").crop(caixa)
        t = Image.new("RGB", im.size, (70, 90, 110)); t.paste(im, (0, 0), im)
        ims.append(t.resize((im.width * z, im.height * z), Image.NEAREST))
    tela = Image.new("RGB", (sum(i.width + 4 for i in ims), ims[0].height))
    x = 0
    for i in ims: tela.paste(i, (x, 0)); x += i.width + 4
    tela.save(saida); print(saida, tela.size)

def tirar_caneleira(arquivo, perto, raio=16, margem=7, **k):
    """Acha a caneleira mais perto do ponto (x, y) e repinta como calça. Devolve False se não achou."""
    achadas = [(c, n) for c, n in caneleiras(arquivo)
               if abs(c[0] + c[2] / 2 - perto[0]) <= raio and abs(c[1] + c[3] / 2 - perto[1]) <= raio]
    if not achadas:
        return False
    (x, y, w, h), _ = max(achadas, key=lambda t: t[1])
    recolorir(arquivo, (x - margem, y - margem, x + w + margem, y + h + margem), **k)
    return True

def zoomg(arquivo, saida, caixa, z=8, passo=10):
    """Zoom com régua: linhas a cada `passo` px e as coordenadas reais nas bordas."""
    from PIL import ImageDraw
    im = Image.open(arquivo).convert("RGBA").crop(caixa)
    t = Image.new("RGB", im.size, (70, 90, 110)); t.paste(im, (0, 0), im)
    t = t.resize((im.width * z, im.height * z), Image.NEAREST)
    tela = Image.new("RGB", (t.width + 30, t.height + 14), (0, 0, 0)); tela.paste(t, (30, 14)); d = ImageDraw.Draw(tela)
    for x in range(caixa[0] - caixa[0] % passo + passo, caixa[2], passo):
        X = 30 + (x - caixa[0]) * z; d.line((X, 14, X, tela.height), fill=(255, 255, 0)); d.text((X + 1, 1), str(x), fill=(255, 255, 0))
    for y in range(caixa[1] - caixa[1] % passo + passo, caixa[3], passo):
        Y = 14 + (y - caixa[1]) * z; d.line((30, Y, tela.width, Y), fill=(255, 255, 0)); d.text((1, Y + 1), str(y), fill=(255, 255, 0))
    tela.save(saida); print(saida, tela.size)

def apagar_regiao(arquivo, dentro):
    """Torna transparente todo pixel (x, y) em que dentro(x, y) é verdadeiro (arrays numpy)."""
    a = np.array(Image.open(arquivo).convert("RGBA"))
    ys, xs = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    m = dentro(xs, ys) & (a[..., 3] >= 128)
    a[m] = 0
    Image.fromarray(a).save(arquivo); print(arquivo, int(m.sum()), "px apagados")
