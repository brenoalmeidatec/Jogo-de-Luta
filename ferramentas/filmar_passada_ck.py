"""Filma a caminhada, o recuo e o bloqueio em pé e mede os contatos no piso."""
import io
import itertools
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import conferir_sff
from filmar_agachamento_gbzin import filmar
from testar_pengaro import injetar


def configurar(copia, gancho, isolar):
    for nome in ('ck','hazaki'):
        cmd = copia/'chars'/nome/f'{nome}.cmd'
        injetar(cmd,nome=='hazaki')
        cab = '[Statedef -1]\n'
        extra = """
[State -1, Instrumento de leitura]
type = MapSet
trigger1 = 1
map = "filme_elem"
value = AnimElemNo(0)
ignorehitpause = 1
"""
        if nome=='hazaki':
            extra += """
[State -1, Aproximar para o jab]
type = AssertInput
trigger1 = map(f_andar) && facing = -1
flag = L
"""
        txt = cmd.read_text(encoding='utf-8')
        cmd.write_text(txt.replace(cab,cab+extra,1),encoding='utf-8')
    codigo = """
  player(2)
  local d = p2BodyDistX()
  mapSet("f_andar", t >= 35 and t < 88 and d > 4 and 1 or 0)
  mapSet("t_x", t == 73 and 1 or 0)
  local rival = stateNo()
  player(1)
"""
    gancho = gancho.replace('if t > 82 then return end','if t > 108 then return end\n'+codigo)
    gancho = gancho.replace('.. anim());','.. anim() .. " " .. posX() .. " " .. screenPosX() .. " " .. life() .. " " .. rival .. " " .. (animElemNo and animElemNo(0) or map("filme_elem")));')
    return 108,gancho


def teclas(t):
    for tick,op,key in ((10,'keydown','Right'),(33,'keyup','Right'),(39,'keydown','Left'),(92,'keyup','Left')):
        if t==tick:
            subprocess.run(['xdotool',op,key],check=True)


def validar(es):
    print('Transições:',[(i+1,e[:2],e[2],e[5]) for i,e in enumerate(es) if i==0 or e[:2]!=es[i-1][:2]],flush=True)
    fases = [e[1] for e in es]
    a,b,c = (fases.index(f) for f in (20,21,150))
    assert a < b < c and es[-1][0]==0 and min(e[4] for e in es)==es[0][4]
    assert any(e[5]==200 for e in es[b:c+1])


def medir(es, pasta):
    """Ponto de contato = origem real do lutador + sola do sprite mostrado no tique."""
    air = (pasta/'ck.air').read_text(encoding='utf-8')
    escala = float(re.search(r'(?m)^xscale = ([.\d]+)',(pasta/'ck.cns').read_text(encoding='utf-8'))[1])
    _,nos,_ = conferir_sff.ler(pasta/'ck.sff')
    sprites = {(n['g'],n['i']):n for n in nos}
    for anim in (20,21):
        bloco = re.search(rf'(?ims)^\[Begin Action {anim}\][^\n]*\n(.*?)(?=^\[|\Z)',air)[1]
        elementos = [tuple(map(int,chave)) for chave in re.findall(r'(?m)^(\d+),\s*(\d+),',bloco)]
        contatos = []
        for el in elementos:
            n = sprites[el]
            rgba = np.asarray(Image.open(io.BytesIO(n['px'][4:])).convert('RGBA'))
            # Lê na fileira que efetivamente toca o piso; a sombra não está no sprite.
            sola = np.where(rgba[n['y'],:,3]>127)[0]-n['x']
            grupos = [g for g in np.split(sola,np.where(np.diff(sola)>1)[0]+1) if len(g)]
            pes = {}
            for g in grupos:
                lado = 'trás' if g.mean()<0 else 'frente'
                pes.setdefault(lado,[]).extend(g.tolist())
            contatos.append({k:min(v) for k,v in pes.items()})
        for lado in ('trás','frente'):
            serie=[]
            for e in es:
                k=int(e[-1])-1
                ativo = e[1]==anim and 0<=k<len(contatos) and lado in contatos[k]
                serie.append(e[2]+escala*contatos[k][lado] if ativo else None)
            amplitudes=[max(g)-min(g) for tem,grupo in itertools.groupby(serie,key=lambda p:p is not None)
                        if tem and len(g:=list(grupo))>=3]
            assert len(amplitudes)>=2,(anim,lado,amplitudes)
            pior=max(amplitudes)
            print(f'Ação {anim}, pé {lado}: {len(amplitudes)} apoios, deriva máxima {pior:.3f} unidades do piso',flush=True)
            assert pior<=.35,(anim,lado,amplitudes)


def main():
    antes,depois,saida=map(Path,sys.argv[1:])
    imagens_a,es_a=filmar(antes,'ck',False,roteiro=sys.modules[__name__])
    imagens_b,es_b=filmar(depois,'ck',False,roteiro=sys.modules[__name__])
    assert [e[:-1] for e in es_a]==[e[:-1] for e in es_b], 'O movimento ou o contato mudou'
    quadros=[]
    for a,b,e in zip(imagens_a,imagens_b,es_b):
        tela=Image.new('RGB',(964,316),'#20232c')
        estado='Avanço' if e[1]==20 else 'Recuo' if e[1]==21 else 'Bloqueio' if 120<=e[0]<=155 else 'Guarda'
        d=ImageDraw.Draw(tela)
        for x,im,lbl in ((0,a,'ANTES'),(484,b,'DEPOIS')):
            tela.paste(im,(x,26))
            d.text((x+12,6),f'{lbl}   {estado}',fill='white')
        quadros.append(tela)
    quadros[0].save(saida,save_all=True,append_images=quadros[1:],duration=50,loop=0)
    medir(es_b,depois/'ck')


if __name__=='__main__':
    main()
