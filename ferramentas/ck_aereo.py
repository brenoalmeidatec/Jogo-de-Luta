"""Poses aéreas do CK e preparação/aterrissagem sobre a sola da guarda."""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import conferir_sff
import efeitos
from agachamento_elenco import acao
from ck_combate_baixo import LINHA
from ck_guarda import KIT, EIXO
from ck_passada import montar_camadas
from ck_ataques_pe import montar as montar_em_pe
from ligar_pecas import ler_remap, por_remap

GRUPO = 57534
# Origem do recorte em relação ao eixo comum do personagem.
POSES = {
    'salto': (112, 75), 'soco': (57, 76), 'cotovelo': (99, 69),
    'chute': (20, 88), 'tesoura': (2, 106), 'voadora': (-8, 93),
}
GOLPES = {600:'soco', 601:'cotovelo', 610:'chute', 611:'tesoura', 650:'voadora'}

def voar(nome, graus, altura):
    im = Image.open(KIT/'aereo'/f'{nome}.png').convert('RGBA')
    x,y = POSES[nome]
    # Margem de armazenamento também comporta o pé de trás na voadora.
    centro = (150-x, 190-y)
    m = cv2.getRotationMatrix2D(centro, graus, 1)
    m[:,2] += [x+60, y+altura]
    return Image.fromarray(cv2.warpAffine(np.array(im),m,(440,370),flags=cv2.INTER_NEAREST))

def quadro(numero, i, total, ativos, guarda, flexao):
    fase = i/(total-1)
    if numero in (40,47):
        if (numero==40 and i==1) or (numero==47 and i==0):
            return Image.fromarray(flexao)
        y,x = np.indices((370,440),dtype=np.float32)
        # Da canela à sola a imagem permanece exatamente na posição do repouso.
        origem = y - 11*np.clip((319-y)/150,0,1)
        return Image.fromarray(cv2.remap(guarda,x,origem,cv2.INTER_NEAREST))
    if numero in GOLPES:
        contato = ativos[0]
        if i in (0,total-1):
            return voar('salto', -3 if i==0 else 3, 0)
        recuo = min(1, abs(i-contato)/max(1,contato))
        return voar(GOLPES[numero], -15*recuo, round(5*recuo))
    direcao = (0,1,-1)[(numero-41)%3]
    percurso = fase if numero<=43 else 1-fase
    if percurso < .32:
        # Recolhe a base ao sair do chão e estende as pernas antes do pouso.
        y,x=np.indices(flexao.shape[:2],dtype=np.float32)
        pernas=np.clip((y-199)/145,0,1)
        fechar=.20+.95*percurso
        mx=x+(x-210)*pernas*fechar
        my=y+pernas*(9+45*percurso)
        return Image.fromarray(cv2.remap(flexao,mx,my,cv2.INTER_NEAREST))
    return voar('salto', direcao*(2+12*percurso), round(12*(1-percurso)))

def aplicar(pasta):
    air,cns,sff = [pasta/f'ck.{ext}' for ext in ('air','cns','sff')]
    texto = air.read_text(encoding='utf8')
    estados = cns.read_text(encoding='utf8')
    remap = ler_remap(estados)
    pal,nos,_ = conferir_sff.ler(sff)
    rle,png,novos = [],[],{}
    for no in nos:
        g,i = no['g'],no['i']
        if g==GRUPO or (g==57533 and i//100==201):
            continue
        item = tuple(no[k] for k in ('g','i','w','h','x','y','px'))
        if no.get('png'):
            png.append(item)
        else:
            rle.append((*item,no.get('pi',0)))
    camadas = montar_camadas()
    base = Image.new('RGBA',(440,370))
    for nome in ('quadril_perna_tras','tenis_tras','quadril_perna_frente','tenis_frente','tronco_guarda'):
        base.alpha_composite(camadas[nome], (60,0))
    guarda = np.array(base)
    kit = json.loads((KIT/'kit.json').read_text(encoding='utf8'))
    flexao = Image.new('RGBA',base.size)
    for parte in kit['guarda_base']['poses']['transicao']:
        x,y = parte['origem']
        flexao.alpha_composite(Image.open(KIT/parte['arquivo']),(x+60,y))
    flexao = np.array(flexao)
    reverso = kit['ataques_em_pe']['reves']
    variante = Image.new('RGBA',(340,370))
    variante.alpha_composite(Image.open(KIT/reverso['arquivo']),tuple(reverso['origem']))
    for numero in (201,*range(40,48),*GOLPES):
        bloco = acao(texto,numero).group()
        linhas = list(LINHA.finditer(bloco))
        ativos = [i for i,l in enumerate(linhas) if 'Clsn1:' in bloco[linhas[i-1].end() if i else 0:l.start()]]
        partes,pos = [],0
        for i,l in enumerate(linhas):
            if numero==201:
                im = montar_em_pe(numero,i,ativos,len(linhas),camadas,{'reves':variante})
                eixo = EIXO
                chave = (57533,20100+i)
            else:
                im = quadro(numero,i,len(linhas),ativos,guarda,flexao)
                eixo = (EIXO[0]+60,EIXO[1])
                chave = (GRUPO,numero*100+i)
            caixa = im.getbbox()
            assert 0<caixa[0]<caixa[2]<im.width and 0<caixa[1]<caixa[3]<im.height,(numero,i,caixa)
            arte = im.crop(caixa)
            anterior = tuple(map(int,l.group(1,2)))
            novos[chave] = remap.get(anterior,anterior)
            png.append((*chave,*arte.size,eixo[0]-caixa[0],eixo[1]-caixa[1],efeitos.blob_png(arte)))
            partes.extend((bloco[pos:l.start()],f'{chave[0]},{chave[1]},{l[3]}'))
            pos=l.end()
        texto=texto.replace(bloco,''.join(partes)+bloco[pos:],1)
    efeitos.gravar(sff,pal,rle,png)
    air.write_text(texto,encoding='utf8',newline='\n')
    cns.write_text(por_remap(estados,novos),encoding='utf8',newline='\n')

if __name__=='__main__':
    aplicar(Path(__file__).resolve().parents[1]/'chars/ck')
