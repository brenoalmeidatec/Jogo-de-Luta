"""Monta os onze normais em pé do CK com peças da forma base."""
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import conferir_sff
import efeitos
from agachamento_elenco import acao
from ck_combate_baixo import LINHA
from ck_guarda import EIXO, KIT
from ck_passada import montar_camadas
from ligar_pecas import ler_remap, por_remap
from pengaro_todo import dobrar

GRUPO = 57533
SOCOS = {200:"jab",201:"reves",210:"direto",215:"direto",216:"martelo"}
# Alvo do tornozelo no contato e ângulo do tênis (calcanhar, bicuda, pisão).
CHUTES = {230:(268,254,-9),231:(261,248,19),240:(262,176,-22),
          245:(249,190,-18),246:(259,270,13),260:(257,170,12)}
QUADRIL = np.array([166.,192.])
JOELHO = np.array([208.,253.])
TORNOZELO = np.array([213.,320.])


def girar(img, origem, destino, graus):
    matriz=cv2.getRotationMatrix2D(tuple(origem),graus,1)
    matriz[:,2]+=destino-origem
    return Image.fromarray(cv2.warpAffine(img,matriz,(340,370),flags=cv2.INTER_NEAREST))


def angulo(v):
    return math.degrees(math.atan2(v[1],v[0]))


def chutar(camadas, alvo, inclinacao, forca, quadril):
    # Cinemática inversa de dois segmentos; a coxa e a canela mantêm o comprimento.
    tornozelo=TORNOZELO+(alvo-TORNOZELO)*forca
    vetor=tornozelo-quadril
    coxa=JOELHO-QUADRIL
    canela=TORNOZELO-JOELHO
    dist=np.linalg.norm(vetor)
    normal=vetor/dist
    proj=(np.dot(coxa,coxa)-np.dot(canela,canela)+dist**2)/(2*dist)
    altura=math.sqrt(max(0,np.dot(coxa,coxa)-proj**2))
    joelho=quadril+normal*proj+np.array([normal[1],-normal[0]])*altura
    arte=np.array(camadas['quadril_perna_frente'])
    y,x=np.indices(arte.shape[:2])
    junta=((x-208)/16)**2+((y-253)/15)**2<1
    coxa_img=np.where(((y<=253)|junta)[...,None],arte,0)
    canela_img=np.where(((y>253)|junta)[...,None],arte,0)
    perto=girar(canela_img,JOELHO,joelho,angulo(canela)-angulo(tornozelo-joelho))
    perto.alpha_composite(girar(coxa_img,QUADRIL,quadril,angulo(coxa)-angulo(joelho-quadril)))
    perto.alpha_composite(girar(np.array(camadas['tenis_frente']),TORNOZELO,tornozelo,inclinacao*forca))
    return perto


def montar(numero,i,ativos,n,camadas,variantes):
    inicio,fim=ativos[0],ativos[-1]
    if i<inicio:
        fase=i/max(1,inicio)
    elif i>fim:
        fase=max(0,1-(i-fim)/min(5,n-fim-1))
    else:
        fase=1
    out=camadas['quadril_perna_tras'].copy()
    out.alpha_composite(camadas['tenis_tras'])
    tronco=camadas['tronco_guarda']
    if numero in CHUTES and fase>0:
        x,y,inc=CHUTES[numero]
        # Levanta o joelho antes de abrir o chute.
        alvo=np.array([x-44*(1-fase),y-72*(1-fase)])
        # O quadril passa sobre o tênis de trás antes da extensão.
        peso = np.array([-39., 9.])*fase
        ygrid,xgrid=np.indices((370,340),dtype=np.float32)
        influencia=np.clip((319-ygrid)/105,0,1)
        out=Image.fromarray(cv2.remap(np.array(out),xgrid-influencia*np.float32(peso[0]),
                                      ygrid-influencia*np.float32(peso[1]),cv2.INTER_NEAREST))
        out.alpha_composite(chutar(camadas,alvo,inc,fase,QUADRIL+peso))
        cintura=np.array(camadas['quadril_perna_frente'])
        cintura[((xgrid-162)/29)**2 + ((ygrid-186)/20)**2 > 1]=0
        offset=tuple(np.rint(peso).astype(int))
        out.alpha_composite(Image.fromarray(cintura),offset)
        reacao=Image.new('RGBA',out.size)
        reacao.alpha_composite(Image.fromarray(dobrar(np.array(tronco),-8*fase)),offset)
        tronco=reacao
    else:
        out.alpha_composite(camadas['quadril_perna_frente'])
        out.alpha_composite(camadas['tenis_frente'])
        if numero in SOCOS and fase>=.5:
            tronco=variantes[SOCOS[numero]]
            if fase<1 or numero==215:
                # Reduz a extensão na entrada, na recolhida e no direto de perto.
                fator=(.74+.26*fase)*(.90 if numero==215 else 1)
                y,x=np.indices((370,340),dtype=np.float32)
                puxar=np.maximum(0,x-190)*(1/fator-1)
                tronco=Image.fromarray(cv2.remap(np.array(tronco),x+puxar,y,cv2.INTER_NEAREST))
        elif numero in SOCOS:
            tronco=Image.fromarray(dobrar(np.array(tronco),-7*fase))
    out.alpha_composite(tronco)
    return out


def aplicar(pasta):
    air,cns,sff=(pasta/f'ck.{ext}' for ext in ('air','cns','sff'))
    texto=air.read_text(encoding='utf-8')
    if int(LINHA.search(acao(texto,200).group())[1])==GRUPO:
        return
    estados=cns.read_text(encoding='utf-8')
    remap=ler_remap(estados)
    pal,nos,_=conferir_sff.ler(sff)
    assert all(n['g']!=GRUPO for n in nos)
    rle,png,novos=[],[],{}
    for no in nos:
        item=tuple(no[k] for k in ('g','i','w','h','x','y','px'))
        if no.get('png'):
            png.append(item)
        else:
            rle.append((*item,no.get('pi',0)))
    camadas=montar_camadas()
    variantes={}
    for nome,p in json.loads((KIT/'kit.json').read_text(encoding='utf-8'))['ataques_em_pe'].items():
        im=Image.new('RGBA',(340,370))
        im.alpha_composite(Image.open(KIT/p['arquivo']),tuple(p['origem']))
        variantes[nome]=im
    for numero in (*SOCOS,*CHUTES):
        bloco=acao(texto,numero).group()
        linhas=list(LINHA.finditer(bloco))
        ativos=[i for i,l in enumerate(linhas) if 'Clsn1:' in bloco[linhas[i-1].end() if i else 0:l.start()]]
        assert ativos,numero
        partes=[]
        pos=0
        for i,l in enumerate(linhas):
            im=montar(numero,i,ativos,len(linhas),camadas,variantes)
            caixa=im.getbbox()
            arte=im.crop(caixa)
            chave=(GRUPO,numero*100+i)
            origem=tuple(map(int,l.group(1,2)))
            novos[chave]=remap.get(origem,origem)
            png.append((*chave,*arte.size,EIXO[0]-caixa[0],EIXO[1]-caixa[1],efeitos.blob_png(arte)))
            partes.extend((bloco[pos:l.start()],f'{chave[0]},{chave[1]},{l[3]}'))
            pos=l.end()
        texto=texto.replace(bloco,''.join(partes)+bloco[pos:],1)
    efeitos.gravar(sff,pal,rle,png)
    air.write_text(texto,encoding='utf-8',newline='\n')
    cns.write_text(por_remap(estados,novos),encoding='utf-8',newline='\n')


if __name__=='__main__':
    aplicar(Path(__file__).resolve().parents[1]/'chars/ck')
