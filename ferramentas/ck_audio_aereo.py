"""Foley sintetizado para tecido, solas e acertos aéreos do CK."""
import re
from pathlib import Path

import gerar_sons as som

GOLPES=(600,601,610,611,650)
GRUPO=56

def amostras():
    sola=som.estalo(.11,726,700,3700,.025)
    pano=som.vento(.14,733,950,2750,.45)
    toque=som.corpo(.18,148,61,.041)
    sinais={
        0:(som.mix(.32*toque,.46*sola,(.32*pano,.021)),-23),
        1:(som.mix(toque,.42*sola,(.48*toque,.037),(.15*pano,.06)),-18),
    }
    for i,(duracao,grave,agudo,peso,tipo) in enumerate((
            (.11,650,3600,0,'luva'),(.12,480,2150,1,'soco'),(.17,430,3000,1,'chute'),
            (.21,620,2600,1,'chute'),(.24,370,1900,2,'chute'))):
        vento=som.vento(duracao,740+i,grave,agudo,.56)
        roupa=som.estalo(.12,762+i,1400,6100,.022)
        ar=som.mix(vento,(.19*roupa,.027))
        if i==3:
            ar=som.mix(ar,(.56*vento,.055))
        sinais[2+i]=(ar,-23+i*.65)
        impacto=som.acerto(peso,811+i,tipo)
        sinais[7+i]=(som.mix(impacto,(.26*roupa,.009),(.27*toque,.016)),-17+i*.75)
    return {(GRUPO,i):som.nivelar(x,volume,-1.5) for i,(x,volume) in sinais.items()}

def ligar(texto):
    partes=re.split(r'(?m)^(?=\[Statedef )',texto)
    for i,p in enumerate(partes):
        m=re.match(r'\[Statedef (-?\d+)\]',p)
        if not m:
            continue
        n=int(m[1])
        if n in GOLPES:
            j=GOLPES.index(n)
            p=re.sub(r'(\[State \d+, som vento\]\ntype = PlaySnd\ntrigger1 = Time = 0\nvalue = )\S+',lambda m:m[1]+f'{GRUPO},{2+j}',p)
            p=re.sub(r'^hitsound = S\d+,\s*\d+',f'hitsound = S{GRUPO},{7+j}',p,flags=re.M)
        if n==-2 and '[State -2, som sola' not in p:
            ponto=p.index('\n[State ')+1
            sons=''.join(som._playsnd(-2,'sola '+nome,f'trigger1 = StateNo = {estado} && Time = 0',f'{GRUPO},{j}') for j,(nome,estado) in enumerate((('salto',40),('pouso',52))))
            p=p[:ponto]+sons+p[ponto:]
        partes[i]=p
    return ''.join(partes)

def atualizar(pasta):
    snd=pasta/'ck.snd'
    banco=(som.ler_snd(snd) if snd.is_file() else
           som.sons_lutador('ck',1000+100*som.LUTADORES.index('ck')))
    banco.update(amostras())
    som.gravar_snd(snd,banco)
    c=pasta/'ck.cns'
    c.write_text(ligar(c.read_text(encoding='utf8')),encoding='utf8',newline='\n')

if __name__=='__main__':
    atualizar(Path(__file__).resolve().parents[1]/'chars/ck')
