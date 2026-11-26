"""Filma cada normal em pé através do CMD do CK, valida contato e lê a sola no SFF."""
import io
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import conferir_sff
from filmar_agachamento_gbzin import filmar
from testar_pengaro import injetar

GOLPES={200:('x','Jab'),201:('golpe_201','Tapa de luva'),210:('y','Direto de longe'),
        215:('y','Direto de perto'),216:('golpe_216','Overhand'),230:('a','Chute fraco'),
        231:('golpe_231','Calcanhar'),240:('b','Chute forte de longe'),245:('b','Chute forte de perto'),
        246:('golpe_246','Pisão'),260:('afastar','Afastar')}


class Roteiro:
    def __init__(self,numero):
        self.numero=numero

    def configurar(self,copia,gancho,isolar):
        for nome in ('ck','hazaki'):
            injetar(copia/'chars'/nome/f'{nome}.cmd',nome=='hazaki')
        comando=GOLPES[self.numero][0]
        distancia=31 if self.numero in (210,240) else 5
        codigo=f"""
  player(2)
  local hp, rival = life(), stateNo()
  local prepara = (t <= 5 or (t >= 25 and t <= 32))
  local alvo = {distancia} + (t <= 5 and 51 or 0)
  mapSet("t_pos", prepara and 1 or 0)
  mapSet("t_posx", math.floor(1000+posX()+(p2BodyDistX()-alvo)*facing()+0.5))
  player(1)
  mapSet("t_{comando}", t == 36 and 1 or 0)
"""
        gancho=gancho.replace('if t > 82 then return end','if t > 125 then return end\n'+codigo)
        gancho=gancho.replace('.. anim());','.. anim() .. " " .. posX() .. " " .. hp .. " " .. rival .. " " .. moveHit() .. " " .. animElemNo(0));')
        return 125,gancho

    def teclas(self,tick):
        if tick in (8,20):
            subprocess.run(['xdotool','keydown' if tick==8 else 'keyup','Right'],check=True)

    def validar(self,es):
        print(self.numero,'estados',sorted({e[0] for e in es}),'vida',es[0][3],es[-1][3],flush=True)
        assert any(e[1]==20 for e in es[:35])
        self.acertos=[i for i,e in enumerate(es) if e[0]==self.numero and e[5]>0]
        assert self.acertos and es[-1][3]<es[0][3] and es[-1][0]==0,(self.numero,es[35:45])
        self.volta=next(i for i in range(self.acertos[-1]+1,len(es)) if es[i][0]==0)


def sola(pasta,numero,es):
    air=(pasta/'ck.air').read_text(encoding='utf-8')
    _,nos,_=conferir_sff.ler(pasta/'ck.sff')
    indice={(n['g'],n['i']):n for n in nos}
    def elementos(anim):
        bloco=re.search(rf'(?ims)^\[Begin Action {anim}\][^\n]*\n(.*?)(?=^\[|\Z)',air)[1]
        return [tuple(map(int,k)) for k in re.findall(r'(?m)^(\d+),\s*(\d+),',bloco)]
    def apoios(chave):
        n=indice[chave]
        img=Image.open(io.BytesIO(n['px'][4:])).convert('RGBA')
        return np.asarray(img.crop((n['x']-100,n['y']-5,n['x']+120,n['y']+1)))
    padrao=apoios(elementos(0)[0])
    elems=elementos(numero)
    ataque=[e for e in es if e[0]==numero]
    for e in ataque:
        atual=apoios(elems[int(e[-1])-1])
        assert np.array_equal(atual[:,:100],padrao[:,:100]),(numero,'pé de apoio',e)
        if numero in (200,201,210,215,216):
            assert np.array_equal(atual,padrao),(numero,'pé dianteiro',e)
    if numero not in (200,201,210,215,216):
        assert any(not np.any(apoios(elems[int(e[-1])-1])[:,100:,3]) for e in ataque if e[5]>0),numero
    return round(max(e[2] for e in ataque)-min(e[2] for e in ataque),2)


def main():
    antes,depois,destino=map(Path,sys.argv[1:4])
    destino.mkdir(exist_ok=True)
    for numero in map(int,sys.argv[4:]):
        roteiro=Roteiro(numero)
        original,ea=filmar(antes,'ck',False,roteiro=roteiro)
        novo,en=filmar(depois,'ck',False,roteiro=roteiro)
        assert ea==en,(numero,'a telemetria das duas lutas divergiu')
        deslocamento=sola(depois/'ck',numero,en)
        resultado={'estado':numero,'golpe':GOLPES[numero][1],'dano':int(en[0][3]-en[-1][3]),
                   'primeiro_contato':roteiro.acertos[0]+1,'volta':roteiro.volta+1,'deslocamento_corpo':deslocamento}
        print(resultado,flush=True)
        (destino/f'{numero}.json').write_text(json.dumps(resultado,ensure_ascii=False),encoding='utf-8')
        frames=[]
        for i in (*range(6,25),*range(32,min(len(en),roteiro.volta+7))):
            tela=Image.new('RGB',(764,302),'#20232c')
            d=ImageDraw.Draw(tela)
            for x,img,titulo in ((0,original[i],'ANTES'),(384,novo[i],'DEPOIS')):
                tela.paste(img.crop((22,0,402,276)),(x,26))
                d.text((x+10,6),titulo+'    '+GOLPES[numero][1],fill='white')
            frames.append(tela)
        frames[0].save(destino/f'{numero}.gif',save_all=True,append_images=frames[1:],duration=40,loop=0)


if __name__=='__main__':
    main()
