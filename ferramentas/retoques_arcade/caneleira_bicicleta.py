import sys, json
import numpy as np
from PIL import Image
S=sys.argv[1]
pal={c['id']:tuple(c['rgb']) for c in json.load(open('sprites/pengaro/paleta_arcade.json',encoding='utf-8'))['cores']}
P=lambda n: np.array(pal[n],np.uint8)
# quadro: (joelho, tornozelo, t0, t1, meia_largura_cima, meia_largura_baixo)
CFG={3:((203,160),(224,148),0.05,1.0,9,8), 4:((206,155),(227,140),0.05,1.0,9,9), 5:((202,150),(216,166),0.1,1.0,8,8)}
for i,(K,A,t0,t1,wu,wd) in CFG.items():
    a=np.array(Image.open(S+'/bic_orig/%02d.png'%i).convert('RGBA'))
    h,w=a.shape[:2]
    ys,xs=np.mgrid[0:h,0:w]
    d=np.array(A,float)-np.array(K,float); L=np.hypot(*d); u=d/L
    t=((xs-K[0])*u[0]+(ys-K[1])*u[1])/L
    perp=(xs-K[0])*(-u[1])+(ys-K[1])*u[0]   # + = um lado
    rgb=a[...,:3]
    eh=lambda n:(rgb==P(n)).all(-1)
    calca=(a[...,3]>0)&(eh('calca_branco')|eh('calca_sombra')|eh('faixa_verde')|eh('faixa_amarelo')|eh('faixa_escuro')|eh('pele_brilho')|eh('cabelo_luz')|eh('calca_contorno'))
    m=calca&(t>=t0)&(t<=t1)&(perp>=-wu)&(perp<=wd)
    claro=m&(eh('calca_branco')|eh('pele_brilho')|eh('faixa_amarelo')|eh('faixa_verde')|eh('cabelo_luz'))
    escuro=m&(eh('calca_sombra')|eh('faixa_escuro'))
    a[claro,:3]=P('cabelo_luz'); a[escuro,:3]=P('cabelo_escuro')
    abaixo=np.zeros_like(m); abaixo[:-3]=m[3:]
    a[m&~abaixo&~eh('calca_contorno')&~eh('pele_contorno'),:3]=P('cabelo_escuro')
    # tira de cima da caneleira (lado do joelho) e de baixo (tornozelo) em escuro, mais uma faixa verde no meio
    borda=m&~eh('calca_contorno')&((t<t0+1.6/L)|(t>t1-1.6/L))
    a[borda,:3]=P('cabelo_escuro')
    meio=claro&(np.abs(t-(t0+t1)/2)<0.9/L)
    a[meio,:3]=P('faixa_escuro')
    print(i,int(m.sum()))
    Image.fromarray(a).save('sprites/pengaro/quadros_arcade/bicicleta/%02d.png'%i)
