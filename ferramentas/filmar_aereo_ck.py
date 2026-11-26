"""Registra a trajetória e os acertos do CK na mesma luta antes e depois."""
import json
import subprocess
import sys
from pathlib import Path
from PIL import Image,ImageDraw

from filmar_agachamento_gbzin import filmar
from testar_pengaro import injetar

NOMES = {'neutro':'Salto vertical','frente':'Salto para frente','tras':'Salto para trás',
         '600':'Soco no ar','601':'Cotovelo','610':'Chute no ar','611':'Tesoura','650':'Voadora'}
COMANDOS = dict(zip(('600','601','610','611','650'),('x','y','a','b','afastar')))

class Salto:
    tela_inteira = True
    def __init__(self, teste):
        self.teste = teste

    def configurar(self,copia,gancho,isolar):
        for nome in ('ck','hazaki'):
            injetar(copia/'chars'/nome/f'{nome}.cmd',nome=='hazaki')
        comando = COMANDOS.get(self.teste,'x')
        golpe = self.teste in COMANDOS
        codigo = f"""
  player(2)
  local hp = life()
  mapSet("t_pos", t <= 5 and 1 or 0)
  mapSet("t_posx", math.floor(1000+posX()+(p2BodyDistX()-{4 if golpe else 75})*facing()+0.5))
  player(1)
  mapSet("t_{comando}", t == {34 if golpe else -1} and 1 or 0)
"""
        gancho=gancho.replace('if t > 82 then return end','if t > 98 then return end\n'+codigo)
        gancho=gancho.replace('.. anim());','.. anim() .. " " .. posX() .. " " .. posY() .. " " .. hp .. " " .. moveHit() .. " " .. (ctrl() and 1 or 0));')
        return 98,gancho

    def teclas(self,t):
        lado = {'frente':'Right','tras':'Left'}.get(self.teste)
        if lado and t in (8,20):
            subprocess.run(['xdotool','keydown' if t==8 else 'keyup',lado],check=True)
        if t in (10,17):
            subprocess.run(['xdotool','keydown' if t==10 else 'keyup','Up'],check=True)

    def validar(self,es):
        print(self.teste,sorted(set(e[:2] for e in es)),min(e[3] for e in es),es[-1],flush=True)
        assert any(e[0]==40 and e[3]==0 for e in es)
        assert min(e[3] for e in es)<-15
        assert any(e[0]==52 and e[3]==0 for e in es)
        assert es[-1][0]==0 and es[-1][3]==0 and es[-1][6]
        if self.teste in COMANDOS:
            assert any(e[0]==int(self.teste) and e[5]>0 for e in es) and es[-1][4]<es[0][4]
        else:
            dx=es[-1][2]-es[0][2]
            assert {'neutro':abs(dx)<1,'frente':dx>5,'tras':dx<-5}[self.teste],dx

def main():
    antes,depois,destino=map(Path,sys.argv[1:4])
    destino.mkdir(exist_ok=True)
    for nome in sys.argv[4:]:
        roteiro=Salto(nome)
        a,ea=filmar(antes,'ck',False,roteiro=roteiro)
        b,eb=filmar(depois,'ck',False,roteiro=roteiro)
        assert ea==eb
        (destino/f'{nome}.json').write_text(json.dumps(eb))
        frames=[]
        fim=next(i for i,e in enumerate(eb) if i>20 and e[0]==0)
        for i in range(6,fim+6):
            tela=Image.new('RGB',(964,320),'#20232c')
            d=ImageDraw.Draw(tela)
            for x,img,l in [(0,a[i],'ANTES'),(484,b[i],'DEPOIS')]:
                tela.paste(img,(x,25))
                d.text((x+12,7),l+'    '+NOMES[nome],fill='white')
            frames.append(tela)
        frames[0].save(destino/f'{nome}.gif',save_all=True,append_images=frames[1:],duration=40,loop=0)

if __name__=='__main__':
    main()
