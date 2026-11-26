"""Defesa e quatro normais agachados da forma base do CK, montados no kit de guarda."""
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
from ck_guarda import KIT
from ligar_pecas import ler_remap, por_remap
from pengaro_todo import dobrar

GRUPO = 57531
DEFESA = (121, 131, 141, 151)
LINHA = re.compile(r"^(\d+),\s*(\d+),(\s*0,\s*0,\s*-?\d+)[ \t]*$", re.M)


def poses():
    kit = json.loads((KIT / "kit.json").read_text(encoding="utf-8"))["guarda_base"]
    corpo = Image.new("RGBA", (340, 360))
    perna = Image.new("RGBA", corpo.size)
    guarda = None
    for parte in kit["poses"]["agachado"]:
        img = Image.open(KIT / parte["arquivo"])
        origem = tuple(parte["origem"])
        if parte["nome"] == "tronco_guarda":
            guarda = Image.new("RGBA", corpo.size)
            guarda.alpha_composite(img, origem)
        elif parte["nome"] in ("quadril_perna_frente", "tenis_frente"):
            perna.alpha_composite(img, origem)
        else:
            corpo.alpha_composite(img, origem)
    variantes = {}
    for nome, parte in kit["troncos_combate"].items():
        variante = Image.new("RGBA", corpo.size)
        img = Image.open(KIT / parte["arquivo"])
        x, cintura = parte["cintura"]
        variante.alpha_composite(img, (x, cintura-img.height))
        variantes[nome] = variante
    return corpo, perna, guarda, variantes


def chute(perna, angulo):
    # Rotação progressiva da canela a partir do joelho, com o quadril fixo.
    a = np.array(perna)
    cx, cy = 232, 250
    y, x = np.indices(a.shape[:2], dtype=np.float32)
    raio = np.hypot(x-cx, y-cy)
    peso = np.clip(raio/32, 0, 1) * np.clip((x-159)/42, 0, 1)
    theta = np.radians(angulo * peso)
    mx = cx + np.cos(theta)*(x-cx) - np.sin(theta)*(y-cy)
    my = cy + np.sin(theta)*(x-cx) + np.cos(theta)*(y-cy)
    alterada = cv2.remap(a, mx, my, cv2.INTER_NEAREST)
    # Conserva a coxa acima da articulação.
    alterada[:cy-5] = a[:cy-5]
    return Image.fromarray(alterada)


def aplicar(pasta):
    corpo, perna, guarda, variantes = poses()
    air, cns, sff = (pasta / f"ck.{ext}" for ext in ("air","cns","sff"))
    texto = air.read_text(encoding="utf-8")
    estados = cns.read_text(encoding="utf-8")
    remap = ler_remap(estados)
    pal, nos, _ = conferir_sff.ler(sff)
    rle, png, novos = [], [], {}
    for n in nos:
        if n["g"] == GRUPO:
            continue
        item = tuple(n[k] for k in ("g","i","w","h","x","y","px"))
        if n.get("png"):
            png.append(item)
        else:
            rle.append((*item,n.get("pi",0)))
    for numero in (*DEFESA, 400,410,430,440):
        bloco = acao(texto, numero).group()
        linhas = list(LINHA.finditer(bloco))
        assert linhas, numero
        ativos = [i for i,l in enumerate(linhas) if "Clsn1:" in bloco[linhas[i-1].end() if i else 0:l.start()]]
        assert ativos or numero in DEFESA
        partes = []
        inicio = 0
        for i,l in enumerate(linhas):
            pose = guarda
            apoio = perna
            if numero in DEFESA:
                pose = variantes["bloqueio"]
            elif numero in (400,410) and i in ativos:
                pose = variantes["jab" if numero == 400 else "upper"]
            elif numero in (430,440):
                dist = min(abs(i-j) for j in ativos)
                apoio = chute(perna, (24 if numero == 430 else 48)*max(0,1-dist/3))
            im = corpo.copy()
            im.alpha_composite(apoio)
            im.alpha_composite(pose)
            # Antecipa e recolhe o tronco mantendo os solados em seu eixo.
            if numero not in DEFESA and i not in ativos:
                im = Image.fromarray(dobrar(np.array(im), 3*math.sin(math.pi*i/(len(linhas)-1))))
            caixa = im.getbbox()
            arte = im.crop(caixa)
            chave = (GRUPO,numero*100+i)
            origem = tuple(map(int,l.group(1,2)))
            novos[chave] = remap.get(origem,origem)
            png.append((*chave,*arte.size,150-caixa[0],352-caixa[1],efeitos.blob_png(arte)))
            partes.extend((bloco[inicio:l.start()],f"{chave[0]},{chave[1]},{l[3]}"))
            inicio = l.end()
        texto = texto.replace(bloco,"".join(partes)+bloco[inicio:],1)
    efeitos.gravar(sff,pal,rle,png)
    air.write_text(texto,encoding="utf-8",newline="\n")
    cns.write_text(por_remap(estados,novos),encoding="utf-8",newline="\n")


if __name__ == "__main__":
    aplicar(Path(__file__).resolve().parents[1]/"chars/ck")
