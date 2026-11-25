"""python3 ferramentas/antes_depois/tira.py SAIDA  (antes = commit e21ea13b do hazaki)

Tira ANTES (linha de cima) x DEPOIS (linha de baixo) + SOBREPOSIÇÃO (antes ciano, depois vermelho), quadros grandes."""
import sys, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "ferramentas/antes_depois"); sys.path.insert(0, "ferramentas")
import diferenca as df
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
RAIZ = Path(".").resolve(); lut, ref = "hazaki", "e21ea13b"; old = "hazakiold"
SAI = Path(sys.argv[1]); SAI.mkdir(parents=True, exist_ok=True)
pasta = RAIZ/"chars"/old; pasta.mkdir(exist_ok=True)
for e in ("air","cns","sff"):
    (pasta/f"{old}.{e}").write_bytes(subprocess.check_output(["git","show",f"{ref}:chars/{lut}/{lut}.{e}"]))
def masc(x):
    return np.abs(x.astype(int)-x[2,2].astype(int)).sum(-1) > 30
def caixa(lst):
    m = np.zeros(lst[0].shape[:2], bool)
    for x in lst: m |= masc(x)
    ys, xs = np.nonzero(m)
    return xs.min()-10, ys.min()-10, xs.max()+10, ys.max()+10
def sobrepor(a, d):
    ma, md = masc(a), masc(d)
    o = np.full(a.shape, 245, np.uint8)
    o[ma & md] = (150,150,150)
    o[ma & ~md] = (0,170,230)
    o[md & ~ma] = (235,30,30)
    return o
def fazer(n, titulo, d, idx):
    da,aa = df.carregar(old, d); dd,ad = df.carregar(lut, d)
    ta,td = df.ticks(da,aa,n), df.ticks(dd,ad,n)
    m=min(len(ta),len(td)); idx=[k for k in idx if k<m]
    bx = caixa([ta[k] for k in idx]+[td[k] for k in idx])
    linhas = [("ANTES", (255,255,255), [ta[k] for k in idx]), ("DEPOIS", (255,230,0), [td[k] for k in idx]),
              ("JUNTOS: azul = só no antes, vermelho = só no depois, cinza = igual", (255,255,255), [sobrepor(ta[k],td[k]) for k in idx])]
    cw, ch = bx[2]-bx[0], bx[3]-bx[1]
    z = min(1.6, 2400/(cw*len(idx)))
    W, H = int(cw*z), int(ch*z)
    out = Image.new("RGB", (W*len(idx)+10*(len(idx)+1), 70+3*(H+50)), (20,20,20))
    dr = ImageDraw.Draw(out)
    dr.text((12,14), titulo, font=ImageFont.truetype(F,34), fill=(255,255,255))
    for r,(rot,cor,ims) in enumerate(linhas):
        y = 70 + r*(H+50)
        dr.text((12,y+4), rot, font=ImageFont.truetype(F,26), fill=cor)
        for c,im in enumerate(ims):
            x = 10 + c*(W+10)
            out.paste(Image.fromarray(im).crop(bx).resize((W,H), Image.NEAREST), (x, y+40))
            if r==0: dr.text((x+6,y+44), f"quadro {idx[c]}", font=ImageFont.truetype(F,20), fill=(200,200,200))
    out.save(SAI/f"tira_{n}{'d' if d else ''}.png")
    print("ok", n, d, m, flush=True)
try:
    for n,t,d,idx in [(0,"Hazak ginga (parado)",False,[0,8,16,24,32,40]),
                      (200,"Hazak jab (borrão no quadro 2, risquinhos de vento depois)",False,[0,2,3,4,5,8]),
                      (800,"Hazak agarrão: a pegada",False,[0,3,6,9,11]),
                      (810,"Hazak agarrão karatê",False,[0,20,40,60,90,110,125]),
                      (4201,"Diabo Loiro: garra cruzada",False,[0,4,8,10,12,16,22]),
                      (4203,"Diabo Loiro: coice",False,[0,4,8,11,13,18,25]),
                      (0,"Diabo Loiro: ginga (parado)",True,[0,8,16,24,32,40])]:
        fazer(n,t,d,idx)
finally:
    for f in pasta.iterdir(): f.unlink()
    pasta.rmdir()
