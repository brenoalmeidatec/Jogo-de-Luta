"""Vento no preparo, pancada no HitDef, dois toques secos na guarda. Grupos locais 57–61."""
import re
from pathlib import Path
import numpy as np
import gerar_sons as s

NOMES=('pengaro','ck','gutto','hazaki','raiclaven','gbzin')
SEMENTE={nome:1800+i*120 for i,nome in enumerate(NOMES)}

def amostras(nome):
    banco={}
    seed=SEMENTE[nome]
    perfil=s.PERFIL[nome]
    for forma in (0,1):
        offset=32*forma
        for classe in range(5):
            chute=classe in (2,3)
            d=(.115,.15,.17,.20,.23)[classe]
            pano=s.vento(d,seed+classe,410 if chute else 800,2300 if chute else 3800,.60)
            if forma:
                pano=s.mix(pano,.30*s.vento(d,seed+9+classe,330,1000,.42))
            banco[57,offset+classe]=s.nivelar(pano,-23.5+classe*.6)
        for slot in range(4):
            material=perfil.get(51+slot,perfil[51])
            if forma and slot in (0,2,3):material=perfil[53]
            for peso in range(5):
                k=slot*5+peso
                fonte=s.acerto_arma if material in s.ARMAS else s.acerto
                textura=fonte(peso,seed+k,material)
                grave=s.corpo(.15+.018*peso,132-4*peso,52,.044+.004*peso)
                v=s.mix(textura,(grave*.36,.009))
                if forma:v=s.mix(v,(.24*s.corpo(.16,92,46,.055),.025))
                banco[58,offset+k]=s.nivelar(v,-16.8+.95*peso,-1.5)
        # O mesmo ritmo de bloqueio em todo o elenco permite reconhecê-lo em um combo.
        for forte in (0,1):
            madeira=s.estalo(.095,seed+67,850,5200,.014)
            aro=s.tom(.12,1180+120*forte,880)*s.env(.12,.001,.027)
            bloqueio=s.mix(.68*madeira,.42*aro,(.80*madeira,.047+.009*forte))
            banco[59,offset+forte]=s.nivelar(bloqueio,-17.9+forte,-1.5)
        sola=s.estalo(.11,seed+80,520,2600,.025)
        peso=s.corpo(.17,140,59,.041)
        casco=forma and nome in ('gbzin','gutto')
        if casco:sola=s.mix(sola,s.tom(.08,820,480)*s.env(.08,.001,.024))
        banco[60,offset]=s.nivelar(s.mix(sola,.3*peso),-23)
        banco[60,offset+1]=s.nivelar(s.mix(peso,.55*sola,(.45*sola,.035)),-18)
    if nome=='ck':
        # O índice baixo continua tocando o foley aprovado do CK base.
        for i in range(2):
            banco[56,32+i]=banco[60,32+i]
        for i in range(5):
            banco[56,34+i]=banco[57,32+i]
            banco[56,39+i]=banco[58,32+10+min(i,4)]
    return banco

def selecionar(grupo,indice):
    return f'{grupo},{indice} + 32 * (var(20) > 0)'

def ligar(nome,texto):
    # Restaura o valor anterior antes de religar, inclusive comentários dos geradores de som.
    texto=re.sub(r'(?m)^(hitsound|guardsound|value) = [^\n]*? ; leitura: ([^\n]+)$',r'\1 = \2',texto)
    partes=re.split(r'(?m)^(?=\[Statedef )',texto)
    for i,p in enumerate(partes):
        estado=re.match(r'\[Statedef (-?\d+)\]',p)
        if not estado:continue
        n=int(estado[1])
        def impacto(m):
            grupo,k=int(m[2]),int(m[3])
            if grupo==56:
                return 'hitsound = S'+selecionar(56,k)+' ; leitura: '+m[1]
            return 'hitsound = S'+selecionar(58,(grupo-51)*5+k)+' ; leitura: '+m[1]
        p=re.sub(r'(?m)^hitsound = (S(5[1-46]),\s*(\d+)[^\n]*)$',impacto,p)
        def guarda(m):
            k=int(m[2])
            return 'guardsound = S'+selecionar(59,min(k,1))+' ; leitura: '+m[1]
        p=re.sub(r'(?m)^guardsound = (F6,\s*(\d+)[^\n]*)$',guarda,p)
        def vento(m):
            return m[1]+selecionar(57,int(m[3]))+' ; leitura: '+m[2]
        p=re.sub(r'(\[State [^\]]+, som vento\]\ntype = PlaySnd\ntrigger1 = Time = 0\nvalue = )(F40,([0-4]))(?=\n)',vento,p)
        if nome=='ck':
            p=re.sub(r'(?m)^(value = )(56,(\d+))$',lambda m:m[1]+selecionar(56,int(m[3]))+' ; leitura: '+m[2],p)
        if n==-2 and nome!='ck' and '[State -2, som apoio' not in p:
            ponto=p.index('\n[State ')+1
            apoio=''.join(s._playsnd(-2,'apoio '+str(k),f'trigger1 = StateNo = {estado} && Time = 0',selecionar(60,k)) for k,estado in enumerate((40,52)))
            p=p[:ponto]+apoio+p[ponto:]
        partes[i]=p
    return ''.join(partes)

def atualizar(nome,pasta):
    snd=pasta/f'{nome}.snd'
    banco=s.ler_snd(snd) if snd.exists() else s.sons_lutador(nome,1000+100*NOMES.index(nome))
    banco.update(amostras(nome))
    s.gravar_snd(snd,banco)
    cns=pasta/f'{nome}.cns'
    cns.write_text(ligar(nome,cns.read_text(encoding='utf8')),encoding='utf8',newline='\n')

if __name__=='__main__':
    import sys
    for nome in sys.argv[1:]:
        atualizar(nome,Path(__file__).resolve().parents[1]/'chars'/nome)
