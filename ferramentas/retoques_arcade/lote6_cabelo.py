"""cabelo2.py <ent> <sai> : repinta cabelo (como retoques_arcade/cabelo.py) em todas as folhas de <ent>; semente = topo da figura,
ou SEMENTES[(folha, quadro)] = (x, y) do topo-centro do cabelo. Tambem monta cabecas.png (antes/depois, 4x)."""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
PC, PS, PM, PL, PB = (0x4C,0x14,0x14), (0x8A,0x32,0x1C), (0xDF,0x7E,0x3F), (0xFD,0xC3,0x72), (0xFD,0xEC,0xCF)
GE, CE, CL = (0x5F,0x1A,0x14), (0x33,0x2C,0x20), (0x75,0x6C,0x4E)
def eh(a, c): return (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & (a[..., 3] > 0)
def retoca(img, semente=None, pula=False):
    a = np.array(img.convert("RGBA"))
    ys, xs = np.nonzero(a[..., 3] > 0)
    if semente: xc, y0 = semente
    else:
        y0 = ys.min(); xc = int(np.median(xs[ys < y0 + 6]))
    if pula: return Image.fromarray(a), 0, (xc, y0)
    yy, xx = np.mgrid[:a.shape[0], :a.shape[1]]
    dy, dx = yy - y0, xx - xc
    caixa = (dy >= 0) & (np.abs(dx) <= 14) & (((dx > 4) & (dy <= 6)) | ((dx >= -3) & (dx <= 4) & (dy <= 9)) | ((dx < -3) & (dy <= 13)))
    escuro = eh(a, PC) | eh(a, PS) | eh(a, GE) | eh(a, CE) | eh(a, CL)
    rot, n = ndimage.label(escuro & caixa)
    sem = np.unique(rot[(dy <= 3) & caixa & (rot > 0)])
    cabelo = np.isin(rot, sem) & (rot > 0)
    troca = cabelo & (eh(a, PS) | eh(a, GE))
    claro = eh(a, PL) | eh(a, PB) | eh(a, PM)
    perto = ndimage.binary_dilation(claro & caixa & (dy <= 5), iterations=1)
    a[troca & eh(a, GE)] = CE + (255,)
    luz = troca & eh(a, PS) & perto & (dy <= 5)
    a[luz] = CL + (255,)
    a[troca & eh(a, PS)] = CE + (255,)
    return Image.fromarray(a), int(troca.sum()), (xc, y0)
ent, sai = Path(sys.argv[1]), Path(sys.argv[2])
S = json.loads(Path("sementes.json").read_text()) if Path("sementes.json").exists() else {}
folhas = sorted(p.name for p in ent.iterdir() if p.is_dir())
Z = 4; W, H = 44, 36
painel = Image.new("RGB", (8 * 2 * W * Z + 8 * 6, len(folhas) * (H * Z + 14)), (90, 90, 100)); dr = ImageDraw.Draw(painel)
for r, folha in enumerate(folhas):
    (sai / folha).mkdir(parents=True, exist_ok=True)
    cont = []
    for q in range(8):
        orig = Image.open(ent / folha / f"{q:02d}.png")
        s = S.get(f"{folha}:{q}")
        img, n, (xc, y0) = retoca(orig, tuple(s) if isinstance(s, list) else None, pula=(s == "pula"))
        img.save(sai / folha / f"{q:02d}.png"); cont.append(n)
        cx = (xc - W // 2, y0 - 6, xc + W // 2, y0 - 6 + H)
        for k, im in enumerate((orig.convert("RGBA"), img)):
            c = im.crop(cx).resize((W * Z, H * Z), Image.NEAREST)
            painel.paste(c, (q * (2 * W * Z + 6) + k * W * Z, r * (H * Z + 14) + 12), c)
    dr.text((4, r * (H * Z + 14)), f"{folha}  trocados: {cont}", fill=(255, 255, 255))
    print(folha, cont)
painel.save("cabecas.png")
