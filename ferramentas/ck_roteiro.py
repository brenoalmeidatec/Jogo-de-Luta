"""Roteiro de captura: bloqueio de contato real do Hazak e contra-ataque do CK."""
import subprocess

import cv2
import numpy as np
from testar_pengaro import injetar


def configurar(copia, gancho):
    for nome in ("ck", "hazaki"):
        injetar(copia / "chars" / nome / f"{nome}.cmd", nome=="hazaki")
    codigo = """
  player(2)
  local d = p2BodyDistX()
  mapSet("t_pos", t < 5 and 1 or 0)
  mapSet("t_posx", math.floor(1000 + posX() + (d-3)*facing()))
  mapSet("t_agacha", t >= 17 and t <= 33 and 1 or 0)
  mapSet("t_holddown", t >= 17 and t <= 33 and 1 or 0)
  mapSet("t_x", t == 30 and 1 or 0)
  local p2st, hp2 = stateNo(), life()
  player(1)
  mapSet("t_x", t == 70 and 1 or 0)
"""
    gancho = gancho.replace("if t > 82 then return end","if t > 117 then return end\n"+codigo)
    gancho = gancho.replace('.. anim());', '.. anim() .. " " .. screenPosX() .. " " .. posX() .. " " .. life() .. " " .. p2st .. " " .. hp2);')
    return 117,gancho


def teclas(tick):
    for t,modo,tecla in ((10,"keydown","Down"),(18,"keydown","Left"),(59,"keyup","Left"),(103,"keyup","Down")):
        if t == tick:
            subprocess.run(["xdotool",modo,tecla],check=True)


def validar(estados):
    print("Sequência:", [(i+1,e[:2],e[4:]) for i,e in enumerate(estados) if not i or e[:2]!=estados[i-1][:2]],flush=True)
    bloqueio = next(i for i,e in enumerate(estados) if e[0] in (152,153) or e[1]==151)
    soco = next(i for i,e in enumerate(estados) if e[0]==400)
    assert any(e[0]==11 for e in estados[:bloqueio]) and bloqueio < soco
    assert min(e[4] for e in estados)==estados[0][4] and any(e[5]==400 for e in estados[:soco])
    assert any(e[0]==11 for e in estados[soco+1:]) and estados[-1][0]==0
    assert estados[-1][-1] < estados[0][-1], "O contra-ataque não atingiu o Hazak"
    print("Vida Hazak:", estados[0][-1], estados[-1][-1], flush=True)


def medir(quadros,estados):
    def branco(im):
        a=np.asarray(im,dtype=np.int16)
        return ((a.min(2)>145)&(a.max(2)-a.min(2)<75)).astype(np.uint8)
    inicio=9  # o adversário já se aproximou, antes da entrada em guarda
    base=branco(quadros[inicio])
    base[:int(base.shape[0]*.76)]=0
    stats=cv2.connectedComponentsWithStats(base)[2][1:]
    solas=sorted((x,y,w,h) for x,y,w,h,area in stats if area>55 and y+h>base.shape[0]*.84)
    print("Candidatos a tênis:",solas,flush=True)
    # O CK é o único lutador de tênis brancos; o Hazak está descalço.
    chao=max(y+h for x,y,w,h in solas)
    solas=[s for s in solas if s[1]+s[3]>=chao-3]
    assert len(solas)==2,solas
    trilhas=[]
    for x,y,w,h in solas:
        y=y+h-9
        modelo=base[y-2:y+12,x-3:x+w+3]
        ult=x-3
        trilha=[]
        for i,im in enumerate(quadros[inicio:],inicio):
            m=42
            a=max(0,ult-m)
            roi=branco(im)[y-8:y+18,a:ult+modelo.shape[1]+m]
            _,q,_,(dx,dy)=cv2.minMaxLoc(cv2.matchTemplate(roi,modelo,cv2.TM_CCORR_NORMED))
            assert q>.82,(i,q,dx,dy)
            ult=a+dx
            trilha.append((ult,dy))
        trilhas.append(np.array(trilha))
    afastamento=trilhas[1]-trilhas[0]
    print("Variação entre as solas (x,y):",np.ptp(afastamento,axis=0).tolist(),flush=True)
    assert np.ptp(afastamento,axis=0).max()<=2
    for lado,trilha in zip(("trás","frente"),trilhas):
        tela=np.array([e[2] for e in estados[inicio:]])
        # Uma câmera imóvel e um CK parado devem deixar a sola no mesmo lugar.
        mudou=np.abs(np.diff(tela))>.001
        # O hook registra o estado antes da apresentação do quadro no X11.
        # Exclui a vizinhança de uma mudança de eixo ao medir o repouso.
        parados=np.convolve(mudou.astype(int), np.ones(5,dtype=int), mode="same")==0
        deriva=np.abs(np.diff(trilha,axis=0))[parados].max(axis=0)
        print(lado,"máxima variação com eixo imóvel:",deriva.tolist(),"px; percurso X na tela:",int(np.ptp(trilha[:,0])),flush=True)
        assert deriva.max()<=1 and np.ptp(trilha[:,1])<=2
