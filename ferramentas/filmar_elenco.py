"""Compara duas lutas reais por golpe e identifica vazio, acerto e guarda por telemetria."""
import argparse
import json
import subprocess
from pathlib import Path
from PIL import Image,ImageDraw
from filmar_agachamento_gbzin import filmar
from testar_pengaro import injetar

GOLPES={'soco':'x','cotovelo':'y','chute':'a','duplo':'b','afastar':'afastar'}

class Roteiro:
    tela_inteira=True
    def __init__(self,nome,forma,teste):
        self.nome=nome
        self.forma=forma
        self.teste=teste
        self.aereo=teste in GOLPES

    def configurar(self,copia,gancho,isolar):
        rival='hazaki' if self.nome!='hazaki' else 'gbzin'
        for nome in (self.nome,rival):
            injetar(copia/'chars'/nome/f'{nome}.cmd',nome==rival)
        cmd=GOLPES.get(self.teste,'x')
        # Golpes aéreos entram na descida. O jab de controle parte de pé.
        distancia={'vazio':145,'mergulho':83}.get(self.teste,3)
        tick=34 if self.aereo else 22
        codigo=f"""
  player(2)
  local hp = life()
  mapSet("t_pos", t <= 5 and 1 or 0)
  mapSet("t_posx", math.floor(1000+posX()+(p2BodyDistX()-{distancia})*facing()+0.5))
  mapSet("t_defende", {1 if self.teste=='guarda' else 0})
  mapSet("t_holdback", {1 if self.teste=='guarda' else 0})
  player(1)
  mapSet("t_{cmd}", t == {tick} and 1 or 0)
"""
        if self.teste=='mergulho':
            codigo+='\n  mapSet("t_dd_a", t == 9 and 1 or 0)\n  mapSet("t_x", t == 40 and 1 or 0)\n'
        if self.teste=='rasgo':
            codigo+='\n  mapSet("t_x", 0)\n  mapSet("t_fd_x", t == 12 and 1 or 0)\n'
        if self.teste=='baixa':
            codigo+='\n  mapSet("t_x",0)\n  player(2)\n  mapSet("t_agacha", t>=17 and t<=33 and 1 or 0)\n  mapSet("t_holddown", t>=17 and t<=33 and 1 or 0)\n  mapSet("t_x", t==30 and 1 or 0)\n  player(1)\n'
        gancho=gancho.replace('if t > 82 then return end','if t > 104 then return end\n'+codigo)
        gancho=gancho.replace('.. anim());','.. anim() .. " " .. posX() .. " " .. posY() .. " " .. hp .. " " .. moveHit() .. " " .. moveGuarded() .. " " .. var(20));')
        return 104,gancho

    def teclas(self,t):
        if self.teste=='baixa':
            for tick,modo,tecla in ((10,'keydown','Down'),(18,'keydown','Left'),(59,'keyup','Left'),(78,'keyup','Down')):
                if t==tick:subprocess.run(['xdotool',modo,tecla],check=True)
        if self.aereo and t in (10,17):
            subprocess.run(['xdotool','keydown' if t==10 else 'keyup','Up'],check=True)

    def validar(self,es):
        eventos=sorted(set(e[:2] for e in es))
        print(self.nome,self.forma,self.teste,eventos,es[0][4]-es[-1][4],flush=True)
        assert all((e[7]>0)==self.forma for e in es)
        assert es[-1][0]==0
        if self.aereo:
            assert min(e[3] for e in es)<-15 and any(e[0]==52 and e[3]==0 for e in es)
        if self.teste=='baixa':
            assert any(e[1]==151 for e in es)
            return
        if self.teste in ('mergulho','rasgo'):
            assert min(e[3] for e in es)<-15 and es[-1][3]==0
        if self.teste=='vazio':
            assert any(200<=e[0]<400 or e[0] in (4200,20200) for e in es) and es[0][4]==es[-1][4] and not any(e[5] or e[6] for e in es)
        elif self.teste=='guarda':
            assert any(e[6]>0 for e in es) and not any(e[5]>0 for e in es)
        else:
            assert any(e[5]>0 for e in es) and es[0][4]>es[-1][4]

def main():
    ap=argparse.ArgumentParser()
    for arg in ('nome','forma','antes','depois','destino'):ap.add_argument(arg)
    ap.add_argument('testes',nargs='+')
    a=ap.parse_args()
    out=Path(a.destino);out.mkdir(exist_ok=True)
    testes=list(a.testes)
    if a.nome=='hazaki' and a.forma=='endiabrado':
        # O demônio tem Voo Infernal e Rasgo Ascendente no lugar dos normais do Hazak.
        testes=['mergulho','rasgo','vazio','guarda']
    if a.nome=='gbzin':
        testes.append('baixa')
    for teste in testes:
        roteiro=Roteiro(a.nome,a.forma=='endiabrado',teste)
        antigo,ea=filmar(Path(a.antes),a.nome,roteiro.forma,roteiro=roteiro)
        novo,en=filmar(Path(a.depois),a.nome,roteiro.forma,roteiro=roteiro)
        assert ea==en,(teste,'telemetria diferente')
        prefixo=f'{a.nome}-{a.forma}-{teste}'
        (out/(prefixo+'.json')).write_text(json.dumps(en))
        if teste in ('soco','afastar','chute','mergulho','rasgo','baixa'):
            frames=[]
            for t in range(7,86,2):
                tela=Image.new('RGB',(804,257),'#202631')
                d=ImageDraw.Draw(tela)
                for x,img,l in ((0,antigo[t],'ANTES'),(404,novo[t],'DEPOIS')):
                    tela.paste(img.resize((400,231),Image.Resampling.NEAREST),(x,25))
                    d.text((x+6,5),f'{l}  {a.nome} / {a.forma} / {teste}',fill='white')
                frames.append(tela)
            frames[0].save(out/(prefixo+'.gif'),save_all=True,append_images=frames[1:],duration=60,loop=0)

if __name__=='__main__':main()
