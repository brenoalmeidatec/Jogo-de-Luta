"""Defesa baixa com os braços da guarda e os apoios do agachamento aprovado."""
from pathlib import Path
import numpy as np
from PIL import Image

import conferir_sff as cs
import efeitos
from elenco_aereo import ELEMENTO,imagem,origem
from ligar_pecas import bloco,ler_remap,por_remap

GRUPO=57563
ACOES=(121,131,141,151)

def apoios(im):
    """Centros dos dois apoios nos últimos pixels do chão (sem o manto)."""
    alfa=np.asarray(im)[:,:,3]
    faixa=max(3,round(im.height*.018))
    xs=np.flatnonzero((alfa[-faixa:]>127).any(axis=0))
    trechos=np.split(xs,np.where(np.diff(xs)>1)[0]+1)
    pes=sorted(sorted(trechos,key=len,reverse=True)[:2],key=lambda p:p.mean())
    assert len(pes)==2 and min(map(len,pes))>5
    return np.array([p.mean() for p in pes])

def montar(baixa,forma):
    arquivo=Path(__file__).resolve().parents[1]/'sprites/gbzin/pecas/defesa_baixa'/f'{forma}.png'
    desenho=Image.open(arquivo).convert('RGBA')
    origens,alvos=apoios(desenho),apoios(baixa)
    escala=(alvos[1]-alvos[0])/(origens[1]-origens[0])
    im=desenho.resize((round(desenho.width*escala),round(desenho.height*escala)),Image.Resampling.NEAREST)
    return im,round(apoios(im)[0]-alvos[0]),im.height-baixa.height

def aplicar(pasta):
    air,cns,sff=[pasta/f'gbzin.{ext}' for ext in ('air','cns','sff')]
    txt=air.read_text(encoding='utf8')
    estados=cns.read_text(encoding='utf8')
    remap=ler_remap(estados)
    pal,nos,_=cs.ler(sff)
    extras=cs.EXTRAS[str(sff.resolve())]
    indice={(n['g'],n['i']):n for n in reversed(nos)}
    rle,png=[],[]
    for no in nos:
        if no['g']==GRUPO:continue
        item=tuple(no[k] for k in ('g','i','w','h','x','y','px'))
        if no.get('png'):png.append(item)
        else:rle.append((*item,no.get('pi',0)))
    for forma in (0,1):
        chave=origem(ELEMENTO.search(bloco(txt,11)[1]))
        no=indice[remap.get(chave,chave) if forma else chave]
        baixa=imagem(no,pal,extras)
        ex,ey=no['x'],no['y']
        im,dx,dy=montar(baixa,forma)
        caixa=im.getbbox()
        im=im.crop(caixa)
        png.append((GRUPO,forma,*im.size,ex+dx-caixa[0],ey+dy-caixa[1],efeitos.blob_png(im)))
    for acao in ACOES:
        m=bloco(txt,acao)
        novo=ELEMENTO.sub(lambda l:f'{GRUPO},0,{l[3]}',m[1])
        txt=txt[:m.start(1)]+novo+txt[m.end(1):]
    efeitos.gravar(sff,pal,rle,png,extras)
    air.write_text(txt,encoding='utf8',newline='\n')
    cns.write_text(por_remap(estados,{(GRUPO,0):(GRUPO,1)}),encoding='utf8',newline='\n')

if __name__=='__main__':aplicar(Path(__file__).resolve().parents[1]/'chars/gbzin')
