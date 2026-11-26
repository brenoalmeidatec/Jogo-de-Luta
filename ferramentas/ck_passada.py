"""Passada do CK base: o pé em apoio compensa a velocidade do estado comum 20."""
import json
import math
import re
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import conferir_sff
import efeitos
from agachamento_elenco import acao
from ck_combate_baixo import LINHA
from ck_guarda import KIT, EIXO
from ligar_pecas import ler_remap, por_remap

GRUPO = 57532
ANDAR = (20, 21)
DEFESA = (120, 130, 140, 150)


def passada(t, velocidade):
    # Três passos de cada pé nos 40 tiques da animação original.
    for duracao in (14, 12, 14):
        if t < duracao:
            break
        t -= duracao
    t = (t + 2) % duracao
    metade = duracao // 2
    fase = t % metade / metade
    primeiro = t < metade
    # Passo de boxe: abre a base com o pé que lidera e recolhe o outro.
    dx = abs(velocidade) * ((t if primeiro else duracao-t)-2)
    altura = -round(15 * math.sin(math.pi * fase))
    move_frente = primeiro == (velocidade > 0)
    return ((-round(dx), 0 if move_frente else altura),
            (round(dx), altura if move_frente else 0))


def montar_camadas():
    kit = json.loads((KIT / 'kit.json').read_text(encoding='utf-8'))['guarda_base']
    camadas = {}
    for p in kit['poses']['parado']:
        tela = Image.new('RGBA', (340, 370))
        tela.alpha_composite(Image.open(KIT / p['arquivo']), tuple(p['origem']))
        camadas[p['nome']] = tela
    pernas = np.array(Image.alpha_composite(camadas['quadril_perna_tras'],camadas['quadril_perna_frente']))
    y,x = np.indices(pernas.shape[:2])
    perto = x >= np.interp(y,(180,232,250), (149,159,163))
    for lado,mascara in (('frente',perto),('tras',~perto)):
        camadas['quadril_perna_'+lado] = Image.fromarray(np.where(mascara[...,None],pernas,0))
    return camadas


def montar(camadas, numero, t, velocidade):
    if numero in DEFESA:
        pernas = ((0, 0), (0, 0))
        molejo = 0
    else:
        pernas = passada(t, velocidade)
        molejo = round(max(abs(dx) for dx, _ in pernas)*.33)
    out = Image.new('RGBA', (340, 370))
    y, x = np.indices((370, 340), dtype=np.float32)
    for lado, (dx, dy) in zip(('tras', 'frente'), pernas):
        # Inverse mapping por altura. A boca da bermuda acompanha o quadril;
        # a canela termina no tornozelo que acompanha o tênis inteiro.
        peso = np.clip((y-227-molejo)/(319+dy-227-molejo), 0, 1)
        joelho = np.sin(math.pi*peso)
        mx = (x - dx*peso - joelho*(-dy*.8)).astype(np.float32)
        my = (y - dy*peso - molejo*(1-peso)).astype(np.float32)
        perna = np.array(camadas['quadril_perna_'+lado])
        out.alpha_composite(Image.fromarray(cv2.remap(perna,mx,my,cv2.INTER_NEAREST)))
        out.alpha_composite(camadas['tenis_'+lado], (dx,dy))
    if numero in DEFESA:
        defesa = Image.open(KIT/'guarda/agachado-bloqueio.png')
        out.alpha_composite(defesa,(112,181-defesa.height))
    else:
        out.alpha_composite(camadas['tronco_guarda'], (0,molejo))
    return out


def aplicar(pasta):
    air, cns, sff = (pasta / f'ck.{ext}' for ext in ('air','cns','sff'))
    texto = air.read_text(encoding='utf-8')
    if LINHA.search(acao(texto,20).group())[1] == str(GRUPO):
        return
    estados = cns.read_text(encoding='utf-8')
    remap = ler_remap(estados)
    pal, nos, _ = conferir_sff.ler(sff)
    assert all(n['g'] != GRUPO for n in nos)
    rle, png, novos = [], [], {}
    for n in nos:
        item = tuple(n[k] for k in ('g','i','w','h','x','y','px'))
        if n.get('png'):
            png.append(item)
        else:
            rle.append((*item,n.get('pi',0)))
    camadas = montar_camadas()
    for numero in (*ANDAR,*DEFESA):
        bloco = acao(texto,numero).group()
        linhas = list(LINHA.finditer(bloco))
        duracoes = [int(l[3].split(',')[-1]) for l in linhas]
        velocidade = 0
        if numero in ANDAR:
            assert sum(duracoes)==40
            direcao = 'fwd' if numero==20 else 'back'
            valor = re.search(rf'(?m)^walk\.{direcao} = ([-.\d]+)', estados)
            escala = re.search(r'(?m)^xscale = ([.\d]+)', estados)
            velocidade = float(valor[1])/float(escala[1])
            # Preserva as janelas dos efeitos da aura despertada ao dividir cada elemento em tiques.
            cortes = np.cumsum([0,*duracoes])
            padrao = rf'(Anim = {numero} && AnimElemNo\(0\) = )\[(\d+), (\d+)\]'
            estados = re.sub(padrao,lambda m: f'{m[1]}[{cortes[int(m[2])-1]+1}, {cortes[int(m[3])]}]',estados)
        t = 0
        partes = []
        inicio = 0
        for l,dur in zip(linhas,duracoes):
            partes.append(bloco[inicio:l.start()])
            elems = []
            origem = tuple(map(int,l.group(1,2)))
            for _ in range(dur if numero in ANDAR else 1):
                chave = (GRUPO,numero*100+t)
                novos[chave] = remap.get(origem,origem)
                im = montar(camadas,numero,t,velocidade)
                caixa = im.getbbox()
                arte = im.crop(caixa)
                png.append((*chave,*arte.size,EIXO[0]-caixa[0],EIXO[1]-caixa[1],efeitos.blob_png(arte)))
                elems.append(f'{chave[0]},{chave[1]}, 0,0, {1 if numero in ANDAR else dur}')
                t+=1
            partes.append('\n'.join(elems))
            inicio = l.end()
        texto = texto.replace(bloco,''.join(partes)+bloco[inicio:],1)
    efeitos.gravar(sff,pal,rle,png)
    air.write_text(texto,encoding='utf-8',newline='\n')
    cns.write_text(por_remap(estados,novos),encoding='utf-8',newline='\n')


if __name__=='__main__':
    aplicar(Path(__file__).resolve().parents[1]/'chars/ck')
