"""Arte do ChatGPT (sprites/gutto/arte_braco/*_grande.png) na escala do kit (0,8, pé no chão) e com a pele do Gutto
(transferência de média e desvio em Lab só na pele). Rode da raiz: python3 ferramentas/arte_braco_gutto_cor.py"""
import cv2, numpy as np
from PIL import Image
A='sprites/gutto/arte_braco/'
def pele(a):
    hsv=cv2.cvtColor(np.ascontiguousarray(a[...,:3]),cv2.COLOR_RGB2HSV)
    return (a[...,3]>0)&(hsv[...,0]<=25)&(hsv[...,1]>70)&(hsv[...,2]>40)
ref=np.asarray(Image.open('sprites/gutto/quadros_sff_hd/94_0.png').convert('RGBA'))
lr=cv2.cvtColor(np.ascontiguousarray(ref[...,:3]),cv2.COLOR_RGB2LAB).astype(float)[pele(ref)]
for n in ('9901_0','9902_0'):
    src=np.asarray(Image.open(A+n+'_grande.png').convert('RGBA'))
    s=0.8; h,w=src.shape[:2]
    im=Image.fromarray(src).resize((round(w*s),round(h*s)),Image.LANCZOS)
    c=Image.new('RGBA',(w,h)); c.paste(im,(round(540-540*s),round(659-659*s)))
    a=np.asarray(c).copy(); a[...,3]=np.where(a[...,3]>127,255,0)
    m=pele(a); lab=cv2.cvtColor(np.ascontiguousarray(a[...,:3]),cv2.COLOR_RGB2LAB).astype(float)
    ls=lab[m]
    new=(ls-ls.mean(0))/ls.std(0)*lr.std(0)+lr.mean(0)
    lab[m]=new
    rgb=cv2.cvtColor(np.clip(lab,0,255).astype(np.uint8),cv2.COLOR_LAB2RGB)
    a[...,:3]=rgb; a[a[...,3]==0]=0
    Image.fromarray(a).save(A+n+'.png'); Image.fromarray(a).save('sprites/gutto/quadros_sff_hd/'+n+'.png')
    print(n, ls.mean(0).round(), lr.mean(0).round())
