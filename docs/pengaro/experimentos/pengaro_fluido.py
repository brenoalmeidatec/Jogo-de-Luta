"""Quadros intermediários do Pengaró a partir das 9 poses (protótipo).

Uso: python pengaro_fluido.py PASTA_SAIDA PASTA_DO_REPO
Precisa de: pip install pillow numpy opencv-python-headless

- parado: respiração por deformação (tronco desce, mão da guarda atrasa meio passo)
- andando: pernas giram em volta do quadril, o pé mais baixo fica sempre no chão
- soco/chute: o membro sai da pose final, gira e encurta em volta da junta, com linhas de velocidade
- agachar: transição por fluxo óptico entre parado e agachado
"""
import json, math, numpy as np, cv2
from PIL import Image
import sys, os
R=os.path.join(sys.argv[2] if len(sys.argv)>2 else '.', 'sprites/pengaro/pixel/')
folha=Image.open(R+'pengaro.png').convert('RGBA'); info=json.load(open(R+'pengaro.json'))
px,py=info['meta']['pivot']['x'],info['meta']['pivot']['y']
W,H,EX,EY=320,190,150,170
def pose(n):
    r=info['frames'][n]['frame']; c=folha.crop((r['x'],r['y'],r['x']+r['w'],r['y']+r['h']))
    t=Image.new('RGBA',(W,H)); t.paste(c,(EX-px,EY-py)); return np.array(t)
P={n:pose(n) for n in info['frames']}
gx,gy=np.meshgrid(np.arange(W),np.arange(H)); gx=gx.astype(np.float32); gy=gy.astype(np.float32)
def remap(a,mx,my): return cv2.remap(a,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
def ss(e0,e1,x): t=np.clip((x-e0)/(e1-e0),0,1); return t*t*(3-2*t)
h=EY-gy  # altura acima do pé

def respira(a,d,dm,lean=0.0):
    """d: quanto o tronco desce (px); dm: quanto as mãos descem; lean: deslocamento horizontal do tronco."""
    s=ss(6,58,h)                         # 0 nos pés, 1 do quadril para cima
    maos=ss(EX+5,EX+30,gx)*ss(55,75,h)   # mão da frente (guarda)
    dy=d*s+(dm-d)*maos
    dx=lean*s
    return remap(a,gx-dx,gy-dy)

def gray(a):
    g=cv2.cvtColor(a[...,:3],cv2.COLOR_RGB2GRAY); g=g.copy(); g[a[...,3]<128]=0; return g
def fluxo(A,B): return cv2.calcOpticalFlowFarneback(gray(A),gray(B),None,0.5,5,25,10,7,1.5,0)
def morph(A,B,t):
    if t<=0: return A
    if t>=1: return B
    if t<0.5: f=fluxo(B,A); return remap(A,gx+t*f[...,0],gy+t*f[...,1])
    f=fluxo(A,B); return remap(B,gx+(1-t)*f[...,0],gy+(1-t)*f[...,1])

def membro(A,B):
    """Pixels do golpe: o que existe em B e não existe em A (o braço/perna esticado)."""
    a=cv2.dilate((A[...,3]>0).astype(np.uint8),np.ones((5,5),np.uint8))
    m=((B[...,3]>0)&(a==0)).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(m)
    if n<=1: return m.astype(bool)
    k=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); return lab==k

def smear(A,B,direcao=(1,0),passos=4,dist=7,cor=(255,244,214)):
    """Pose B com rastro de movimento atrás do membro que golpeia (estilo arcade)."""
    m=membro(A,B); out=B.copy(); rastro=np.zeros((H,W),bool)
    for k in range(1,passos+1):
        sh=np.roll(np.roll(m,-int(direcao[1]*dist*k),0),-int(direcao[0]*dist*k),1)
        if k>passos//2: sh&=((gx.astype(int)+gy.astype(int))%2==0)   # pontilhado no fim do rastro
        rastro|=sh
    rastro&=(B[...,3]==0)
    out[rastro]=(*cor,255)
    # contorno escuro só na borda do rastro, para não virar borrão
    return out

def bob(seq):
    return seq

def anim_parado():
    # 12 quadros, seno suave: tronco desce até 3 px, mãos atrasam meio passo
    fr=[]
    for i in range(12):
        f=i/12; d=round(1.5-1.5*math.cos(2*math.pi*f)); dm=round(1.5-1.5*math.cos(2*math.pi*(f-0.12)))
        fr.append((respira(P['parado'],d,dm),5))
    return fr

def anim_soco():
    A,B=P['parado'],P['soco']
    ante=respira(A,1,2,lean=-3)          # recolhe antes de bater
    return [(A,2),(ante,3),(morph(A,B,0.35),2),(smear(A,B),2),(B,5),(morph(A,B,0.7),3),(morph(A,B,0.4),3),(respira(A,1,1),3),(A,2)]

def anim_chute():
    A,B=P['parado'],P['chute']
    ante=respira(A,2,2,lean=-4)
    return [(A,2),(ante,3),(morph(A,B,0.3),2),(morph(A,B,0.6),2),(smear(A,B,(1,-0.3)),2),(B,6),(morph(A,B,0.7),3),(morph(A,B,0.4),3),(respira(A,2,2),3),(A,2)]

def anim_agacha():
    A,B=P['parado'],P['agachado']
    return [(A,2),(morph(A,B,0.25),2),(morph(A,B,0.5),2),(morph(A,B,0.75),2),(B,6),(morph(A,B,0.6),2),(morph(A,B,0.3),2),(A,4)]

def anim_anda():
    A,B=P['parado'],P['andando']
    seq=[0,0.25,0.5,0.75,1,0.75,0.5,0.25]; out=[]
    for i,t in enumerate(seq):
        f=morph(A,B,t); d=[0,1,2,1,0,1,2,1][i]
        out.append((respira(f,d,d),4))
    return out

MEMBRO={
 'chute':dict(poly=[(163,97),(176,93),(202,84),(229,70),(242,70),(242,96),(200,104),(182,110),(167,117),(163,112)],piv=(165,106)),
 'soco':dict(poly=[(166,81),(197,82),(211,78),(217,88),(215,100),(197,96),(180,96),(166,94)],piv=(167,88)),
}
def mascara(n):
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array(MEMBRO[n]['poly'],np.int32)],1)
    m=(m.astype(bool)&(P[n][...,3]>0)).astype(np.uint8)
    k,lab,st,_=cv2.connectedComponentsWithStats(m,connectivity=4)
    return lab==1+np.argmax(st[1:,cv2.CC_STAT_AREA])
def limbo(n,ang,esc=1.0,base=None):
    """Pose n com o membro girado ang graus (positivo = desce) e encurtado por esc, em volta da junta."""
    B=P[n]; m=mascara(n); cx,cy=MEMBRO[n]['piv']
    lim=B.copy(); lim[~m]=0
    M=cv2.getRotationMatrix2D((cx,cy),-ang,1.0)
    # encurta só na direção do membro (antes de girar)
    S=np.array([[esc,0,cx*(1-esc)],[0,1,0]],np.float32)
    S3=np.vstack([S,[0,0,1]]); M3=np.vstack([M,[0,0,1]]); T=(M3@S3)[:2]
    rl=cv2.warpAffine(lim,T,(W,H),flags=cv2.INTER_NEAREST,borderValue=(0,0,0,0))
    corpo=B.copy(); corpo[m]=0
    k,lab,st,_=cv2.connectedComponentsWithStats((corpo[...,3]>0).astype(np.uint8),connectivity=8)
    if k>2: corpo[lab!=1+np.argmax(st[1:,cv2.CC_STAT_AREA])]=0
    if base is not None:
        fundo=base.copy(); fundo[corpo[...,3]>0]=corpo[corpo[...,3]>0]; corpo=fundo
    out=corpo.copy(); out[rl[...,3]>0]=rl[rl[...,3]>0]
    return out
def ponta(n):
    m=mascara(n); cx,cy=MEMBRO[n]['piv']; ys,xs=np.nonzero(m)
    k=np.argmax(np.hypot(xs-cx,ys-cy)); return xs[k]-cx, ys[k]-cy
def rastro(img,n,a0,a1,esc0=1.0,esc1=1.0,cor=(255,244,214)):
    """Linhas de velocidade: arco que a ponta do membro percorreu de a0 até a1 (graus, positivo = desce)."""
    cx,cy=MEMBRO[n]['piv']; vx,vy=ponta(n); L=np.zeros((H,W),np.uint8)
    for k,(rr,esp) in enumerate([(1.0,2),(0.86,1),(0.72,1)]):
        pts=[]
        for t in np.linspace(0,1,24):
            a=math.radians(a0+(a1-a0)*t); e=esc0+(esc1-esc0)*t
            x,y=vx*e*rr,vy*rr
            pts.append((cx+x*math.cos(a)-y*math.sin(a), cy+x*math.sin(a)+y*math.cos(a)))
        pts=np.array(pts,np.int32)
        n_=len(pts); cut=int(n_*(0.15+0.2*k))
        cv2.polylines(L,[pts[cut:]],False,1,esp)
        cv2.polylines(L,[pts[:cut+1]],False,2,1)
    out=img.copy(); livre=img[...,3]==0
    out[(L==1)&livre]=(*cor,255)
    out[(L==2)&livre&((gx.astype(int)+gy.astype(int))%2==0)]=(*cor,255)
    return out
def linhas(img,n,comp=26,cor=(255,244,214)):
    """Linhas retas atrás do punho (soco)."""
    cx,cy=MEMBRO[n]['piv']; vx,vy=ponta(n); x,y=cx+vx,cy+vy-3
    L=np.zeros((H,W),np.uint8)
    for dy,c in [(-13,comp),(-9,comp+8),(5,comp-4)]:
        cv2.line(L,(x-c,y+dy),(x-4,y+dy),1,1)
    out=img.copy(); out[(L==1)&(img[...,3]==0)]=(*cor,255); return out

def anim_soco():
    A=P['parado']; B=P['soco']
    return [(respira(A,1,2,lean=-2),3),(limbo('soco',25,0.55),2),(linhas(limbo('soco',8,0.8),'soco',16),2),
            (linhas(B,'soco'),3),(B,5),(limbo('soco',6,0.8),3),(limbo('soco',22,0.6),3),(respira(A,1,1),3),(A,2)]
def anim_chute():
    A=P['parado']; B=P['chute']
    return [(respira(A,2,2,lean=-3),3),(limbo('chute',75,0.75),3),(limbo('chute',45,0.88),2),
            (rastro(limbo('chute',18,1),'chute',70,18,0.78,1),2),(rastro(B,'chute',55,0),3),(B,6),
            (limbo('chute',20,1),3),(limbo('chute',50,0.85),3),(limbo('chute',75,0.75),3),(respira(A,2,2),3),(A,2)]

PERNAS={'tras':dict(poly=[(113,124),(148,124),(148,172),(98,172),(98,140),(112,134)],piv=(134,122)),
        'frente':dict(poly=[(148,124),(186,120),(208,172),(148,172)],piv=(158,122))}
def _msk(img,poly):
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array(poly,np.int32)],1); return m.astype(bool)&(img[...,3]>0)
def _gira(img,m,piv,ang):
    l=img.copy(); l[~m]=0
    M=cv2.getRotationMatrix2D(piv,-ang,1.0)
    return cv2.warpAffine(l,M,(W,H),flags=cv2.INTER_NEAREST,borderValue=(0,0,0,0))
def passo(a_tras,a_frente,img=None,lean=0):
    img=P['parado'] if img is None else img
    mt=_msk(img,PERNAS['tras']['poly']); mf=_msk(img,PERNAS['frente']['poly'])
    lt=_gira(img,mt,PERNAS['tras']['piv'],a_tras); lf=_gira(img,mf,PERNAS['frente']['piv'],a_frente)
    corpo=img.copy(); corpo[mt|mf]=0
    if lean: corpo=respira(corpo,0,0,lean=lean)
    out=np.zeros_like(img)
    for c in (lt,lf,corpo): out[c[...,3]>0]=c[c[...,3]>0]
    # mantém o pé mais baixo no chão
    ys=np.nonzero(out[...,3].any(1))[0]; d=EY-ys.max()
    if d: out=np.roll(out,d,0)
    return out
def anim_anda():
    fr=[]
    for i in range(10):
        f=2*math.pi*i/10
        fr.append((passo(7*math.sin(f), -7*math.sin(f), lean=round(1*math.cos(2*f))),5))
    return fr

ANIMS={'parado':anim_parado(),'andando':anim_anda(),'soco':anim_soco(),'chute':anim_chute(),'agachar':anim_agacha()}

def antes(n):
    """Como está hoje no jogo, para comparar."""
    return None

# ---------- saída
FUNDO=(58,44,72,255); CHAO=(36,28,46,255)
def quadro(a,esc=3,crop=(40,10,300,185)):
    bg=np.zeros((H,W,4),np.uint8); bg[...]=FUNDO; bg[EY+1:]=CHAO
    im=Image.alpha_composite(Image.fromarray(bg),Image.fromarray(a)).crop(crop)
    return im.resize((im.width*esc,im.height*esc),Image.NEAREST)
import sys
saida=sys.argv[1]
for nome,seq in ANIMS.items():
    frames=[];durs=[]
    for _ in range(3 if nome in('soco','chute','agachar') else 2):
        for a,t in seq: frames.append(quadro(a).convert('P',palette=Image.ADAPTIVE,colors=255)); durs.append(int(t*1000/60))
        if nome in('soco','chute','agachar'):
            frames.append(quadro(P['parado']).convert('P',palette=Image.ADAPTIVE,colors=255)); durs.append(400)
    frames[0].save(f'{saida}/{nome}.gif',save_all=True,append_images=frames[1:],duration=durs,loop=0,disposal=2)
    # folha de quadros
    tiles=[Image.fromarray(a).crop((40,10,300,185)) for a,_ in seq]
    sheet=Image.new('RGBA',(260*len(tiles),175))
    for i,t in enumerate(tiles): sheet.paste(t,(i*260,0))
    sheet.save(f'{saida}/{nome}_quadros.png')
print('ok')
