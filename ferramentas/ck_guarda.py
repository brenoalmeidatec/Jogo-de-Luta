"""Monta a guarda base do CK das peças do kit. --recortar importa a folha aprovada."""
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import conferir_sff
import efeitos
from agachamento_elenco import ELEMENTO, acao
from ligar_pecas import ler_remap, por_remap
from pengaro_todo import dobrar

RAIZ = Path(__file__).resolve().parents[1]
KIT = RAIZ / "sprites/ck/pecas"
GRUPO = 57530
# Tela HD do IKEMEN, com espaço para o tronco respirar.
EIXO = (150, 352)
TAMANHO = (300, 360)


def recortar():
    fonte = RAIZ / "docs/boneco-pecas/ck/redesenho/ck-corpo-base.png"
    folha = np.array(Image.open(fonte).convert("RGBA"))
    destino = KIT / "guarda"
    destino.mkdir(exist_ok=True)
    dados = json.loads((KIT / "kit.json").read_text(encoding="utf-8"))
    poses = {}
    # Coordenadas dos tornozelos na folha original e centro do quadril.
    for nome, centro, tras, frente in (("parado", 492, 366, 611), ("agachado", 1160, 915, 1372),
                                      ("transicao", 1160, 915, 1372)):
        base = nome == "parado"
        xs, ys = np.meshgrid(np.arange(TAMANHO[0]), np.arange(TAMANHO[1]))
        x = (xs - EIXO[0]) / .414
        y = (ys - EIXO[1]) / .414 + 849
        # A transição ergue o quadril só até metade do caminho, com tornozelos ancorados.
        if nome == "transicao":
            y = np.interp(y, [-100, 445, 767, 849, 900], [4, 549, 767, 849, 900])
        peso = np.clip((y - (480 if base else 550)) / (767 - (480 if base else 550)), 0, 1)
        peso = peso * peso * (3 - 2 * peso)
        lado = np.clip((x + 75) / 150, 0, 1)
        correcao = (tras - centro + 148) * (1 - lado) + (frente - centro - 155) * lado
        mx = (x + centro + peso * correcao).astype(np.float32)
        my = y.astype(np.float32)
        img = cv2.remap(folha, mx, my, cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT)
        img[(y > 849) | (img[..., 3] < 180)] = 0
        img[..., 3] = np.where(img[..., 3], 255, 0)
        pes = y >= 768
        tronco = y < (433 if base else 550)
        mascaras = {"tronco_guarda": tronco, "quadril_perna_tras": ~tronco & ~pes & (x < 0),
                    "quadril_perna_frente": ~tronco & ~pes & (x >= 0),
                    "tenis_tras": pes & (x < 0), "tenis_frente": pes & (x >= 0)}
        partes = []
        for chave, mascara in mascaras.items():
            if chave.startswith("tenis") and not base:
                partes.append(next(p for p in poses["parado"] if p["nome"] == chave))
                continue
            camada = Image.fromarray(np.where(mascara[..., None], img, 0))
            caixa = camada.getbbox()
            arq = f"guarda/{nome}-{chave}.png"
            camada.crop(caixa).save(KIT / arq)
            partes.append(dict(nome=chave, arquivo=arq, origem=list(caixa[:2])))
        poses[nome] = partes
    dados["guarda_base"] = dict(eixo=EIXO, tamanho=TAMANHO, poses=poses)
    (KIT / "kit.json").write_text(json.dumps(dados, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def aplicar(pasta):
    kit = json.loads((KIT / "kit.json").read_text(encoding="utf-8"))["guarda_base"]
    poses = {}
    for nome, camadas in kit["poses"].items():
        im = Image.new("RGBA", tuple(kit["tamanho"]))
        for camada in camadas:
            im.alpha_composite(Image.open(KIT / camada["arquivo"]), tuple(camada["origem"]))
        poses[nome] = np.array(im)
    air, cns, sff = (pasta / f"ck.{ext}" for ext in ("air", "cns", "sff"))
    texto = air.read_text(encoding="utf-8")
    estados = cns.read_text(encoding="utf-8")
    remap = ler_remap(estados)
    pal, nos, _ = conferir_sff.ler(sff)
    png, rle = [], []
    for n in nos:
        if n["g"] == GRUPO:
            continue
        item = tuple(n[k] for k in ("g", "i", "w", "h", "x", "y", "px"))
        if n.get("png"):
            png.append(item)
        else:
            rle.append((*item, n.get("pi", 0)))
    novos = {}
    for numero in (0, 10, 11, 12):
        bloco = acao(texto, numero).group()
        linhas = list(ELEMENTO.finditer(bloco))
        total = sum(int(l[4]) for l in linhas)
        tempo = 0
        it = iter(range(len(linhas)))
        def elemento(linha):
            nonlocal tempo
            i = next(it)
            chave = (GRUPO, numero * 100 + i)
            origem = tuple(map(int, linha.group(1, 2)))
            novos[chave] = remap[origem]
            pose = {0: "parado", 11: "agachado"}.get(numero, "transicao")
            if (numero == 10 and i == len(linhas)-1) or (numero == 12 and i == 0):
                pose = "agachado"
            graus = (1 - math.cos(2 * math.pi * tempo / total)) if numero in (0, 11) else 0
            tempo += int(linha[4])
            im = Image.fromarray(dobrar(poses[pose], graus))
            caixa = im.getbbox()
            arte = im.crop(caixa)
            x, y = kit["eixo"]
            png.append((*chave, *arte.size, x-caixa[0], y-caixa[1], efeitos.blob_png(arte)))
            return f"{chave[0]},{chave[1]},{linha[3]}{linha[4]}"
        texto = texto.replace(bloco, ELEMENTO.sub(elemento, bloco), 1)
    efeitos.gravar(sff, pal, rle, png)
    air.write_text(texto, encoding="utf-8", newline="\n")
    cns.write_text(por_remap(estados, novos), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    if "--recortar" in sys.argv:
        recortar()
    aplicar(RAIZ / "chars/ck")
