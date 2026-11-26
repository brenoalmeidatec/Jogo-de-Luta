"""Monta os saltos e contatos do elenco sem alterar elementos, duração ou caixas do AIR."""
import io
import re
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import conferir_sff as cs
import efeitos
from dobra_agachado import rgba
from ligar_pecas import bloco,ler_remap,por_remap

RAIZ=Path(__file__).resolve().parents[1]
GOLPES={600:'mao',601:'cotovelo',610:'lateral',611:'duplo',650:'duplo',3436:'mao'}
GRUPOS=(57560,57561,57562)
ELEMENTO=re.compile(r'(?m)^(\d+),\s*(\d+),(.*)$')
ORIGINAL=re.compile(r' ; desenho anterior (\d+),(\d+)$')

def origem(linha):
    anterior=ORIGINAL.search(linha[3])
    return tuple(map(int,(anterior or linha).group(1,2)))

def imagem(no,paleta,extras):
    if no.get('png'):
        return Image.open(io.BytesIO(no['px'][4:])).convert('RGBA')
    pi=no.get('pi',0)
    return Image.fromarray(rgba(no,extras[pi-2] if pi>=2 else paleta))

def preparar(nome,forma,numero,i,total,ativos,limites,refs,pasta_poses):
    repouso,voo,antigo=refs
    if numero in (40,47):
        im,ex,ey=repouso
        arr=np.asarray(im)
        y,x=np.indices(arr.shape[:2],dtype=np.float32)
        # Flexão leve do tronco e do tecido acima dos joelhos. Solas e canelas
        # conservam as coordenadas da guarda até o último tique no chão.
        peso=np.clip((.71*im.height-y)/(.40*im.height),0,1)
        compressao=(.043 if total==1 else .025+.03*(i if numero==40 else total-1-i)/max(1,total-1))
        img=Image.fromarray(cv2.remap(arr,x,y-im.height*compressao*peso,cv2.INTER_NEAREST))
        return img,ex,ey
    neutra,nx,ny=voo
    if 41<=numero<=46:
        progresso=i/max(total-1,1)
        if numero>=44:progresso=1-progresso
        lado=(0,1,-1)[(numero-41)%3]
        return girar(neutra,nx,ny,lado*(2+6*progresso),round(7*(1-progresso)))
    contato=ativos[0]
    if i==0 and i not in ativos or i==total-1 and i not in ativos:
        return voo
    arquivo=pasta_poses/(GOLPES[numero]+'.png')
    # O cajado do Gbzin e a joelhada do Hazak já têm quadros próprios aprovados.
    if not arquivo.exists() or (nome=='hazaki' and not forma and numero==610):
        return antigo
    im=Image.open(arquivo).convert('RGBA')
    x1,y1,x2,y2=limites
    # O ponto que toca o rival é a ponta da arma, cotovelo, luva ou sola.
    a=np.asarray(im)[:,:,3]
    yy,xx=np.where(a>0)
    ponta=xx>=xx.max()-max(4,int(im.width*.045))
    px,py=int(np.median(xx[ponta])),int(np.median(yy[ponta]))
    ex=px-(max(x1,x2)-5)
    ey=py-round((min(y1,y2)+max(y1,y2))*.5)
    recuo=min(1,abs(i-contato)/max(1,contato))
    angulo=-9*recuo+(12 if numero==650 else 0)
    return girar(im,ex,ey,angulo,round(5*recuo))

def girar(im,ex,ey,angulo,dy):
    margem=80
    tela=Image.new('RGBA',(im.width+2*margem,im.height+2*margem))
    tela.alpha_composite(im,(margem,margem))
    tela=tela.rotate(angulo,Image.Resampling.NEAREST,center=(margem+im.width*.5,margem+im.height*.55))
    box=tela.getbbox()
    assert box[0]>0 and box[1]>0 and box[2]<tela.width and box[3]<tela.height
    return tela.crop(box),ex+margem-box[0],ey+margem-box[1]-dy

def aplicar(nome,pasta=None):
    pasta=pasta or RAIZ/'chars'/nome
    air,cns,sff=(pasta/f'{nome}.{ext}' for ext in ('air','cns','sff'))
    texto=air.read_text(encoding='utf8')
    estados=cns.read_text(encoding='utf8')
    remap=ler_remap(estados)
    pal,nos,_=cs.ler(sff)
    extras=cs.EXTRAS[str(sff.resolve())]
    indice={(n['g'],n['i']):n for n in reversed(nos)}
    rle,png,novos=[],[],{}
    for no in nos:
        if no['g'] in GRUPOS:continue
        item=tuple(no[k] for k in ('g','i','w','h','x','y','px'))
        if no.get('png'):png.append(item)
        else:rle.append((*item,no.get('pi',0)))
    def ler(chave,forma):
        if forma:
            destino=remap.get(chave,chave)
            if destino[0] not in GRUPOS:chave=destino
            elif nome=='ck' and chave[0]==57534:
                # A forma base já usa o salto novo do CK. Reutilize a pose compacta
                # do kit endiabrado quando seu remap já tiver sido instalado.
                im=Image.open(RAIZ/'sprites/ck/aereo/endiabrado/cotovelo.png').convert('RGBA')
                return im,im.width//2,int(im.height*.97)
        n=indice[chave]
        return imagem(n,pal,extras),n['x'],n['y']
    inicial=origem(ELEMENTO.search(bloco(texto,0)[1]))
    saltos=list(ELEMENTO.finditer(bloco(texto,41)[1]))
    topo=origem(saltos[len(saltos)//2])
    referencias={}
    for forma in (0,1):
        diretorio=RAIZ/'sprites'/nome/'aereo'/('endiabrado' if forma else 'base')
        neutra=ler(topo,forma)
        if forma and nome in ('ck','raiclaven','hazaki'):
            im=Image.open(diretorio/'cotovelo.png').convert('RGBA')
            neutra=im,round(im.width*.49),round(im.height*.94)
        referencias[forma]=(ler(inicial,forma),neutra,diretorio)
    for numero in (*range(40,48),*GOLPES):
        for exclusiva in (False,True):
            anim=numero+(10000 if exclusiva else 0)
            m=bloco(texto,anim)
            if not m or (numero==3436 and nome not in ('ck','gbzin')):continue
            b=m[1]
            els=list(ELEMENTO.finditer(b))
            if not els:continue
            caixas=[]
            for j,l in enumerate(els):
                trecho=b[els[j-1].end() if j else 0:l.start()]
                hit=re.search(r'(?i)Clsn1\[\d+\]\s*=\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)',trecho)
                if hit:caixas.append((j,tuple(map(int,hit.groups()))))
            if numero in GOLPES and not caixas:continue
            ativos=[k for k,_ in caixas]
            anterior=0
            partes=[]
            for i,l in enumerate(els):
                chave=origem(l)
                base=chave
                for forma in ((1,) if exclusiva or numero==3436 else (0,1)):
                    if nome=='ck' and not forma:continue
                    repouso,voo,diretorio=referencias[forma]
                    arte,ex,ey=preparar(nome,forma,numero,i,len(els),ativos,caixas[0][1] if caixas else (), (repouso,voo,ler(chave,forma)),diretorio)
                    grupo=GRUPOS[2 if exclusiva else forma]
                    idx=(numero if numero!=3436 else 660)*64+i
                    assert i<64 and idx<65536
                    nova=(grupo,idx)
                    png.append((*nova,*arte.size,ex,ey,efeitos.blob_png(arte)))
                    if forma and not exclusiva and numero!=3436:novos[base]=nova
                    else:base=nova
                cauda=ORIGINAL.sub('',l[3])
                registro=f'{base[0]},{base[1]},{cauda}'
                if base!=chave:registro+=f' ; desenho anterior {chave[0]},{chave[1]}'
                partes.extend((b[anterior:l.start()],registro));anterior=l.end()
            texto=texto[:m.start(1)]+''.join(partes)+b[anterior:]+texto[m.end(1):]
    efeitos.gravar(sff,pal,rle,png,extras)
    air.write_text(texto,encoding='utf8',newline='\n')
    cns.write_text(por_remap(estados,novos),encoding='utf8',newline='\n')

if __name__=='__main__':
    import sys
    for nome in sys.argv[1:]:aplicar(nome)
