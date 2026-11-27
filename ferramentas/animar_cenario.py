#!/usr/bin/env python3
"""Anima um figurante de cenário: corta a folha do ChatGPT (8 poses em fila, fundo magenta), põe no tamanho do cenário e
usa o Blender para os quadros do meio (o desenho só é entortado, nunca misturado: continua pixel, nada de 3D).

  python ferramentas/animar_cenario.py <folha.png> <saida.png> --largura 250 [--meios 3] [--n 8] [--anda]

A saída é uma folha horizontal com todos os quadros do loop (8 desenhos + meios entre cada par), pronta para o
"folha": {"imagem": ..., "n": ...} do cenario.json. --largura é a largura do grupo no cenário, em px da tela 1280x720.
--anda: figura que caminha (cada pose é alinhada pelos pés no centro da célula, não pela posição na folha).
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from animar_folha import BLENDER, PASSO, RAIZ, fluxo

AMPLIA = 4  # o Blender trabalha 4x maior que o quadro final


def sem_fundo(img):
    """Fundo magenta (com o degradê que o ChatGPT deixa) vira transparente; sobras pequenas saem."""
    a = np.array(img.convert("RGBA"))
    r, g, b = (a[..., i].astype(int) for i in range(3))
    fundo = (r > 190) & (b > 190) & (g < 120) & (np.abs(r - b) < 50)  # estreito: vestido rosa não pode sumir
    a[fundo, 3] = 0
    n, rot, dados, _ = cv2.connectedComponentsWithStats((a[..., 3] > 0).astype(np.uint8), connectivity=8)
    for i in range(1, n):
        if dados[i, cv2.CC_STAT_AREA] < 30:
            a[rot == i, 3] = 0
    return Image.fromarray(a)


def sem_rosa(img):
    """Franja rosa da borda (o magenta misturado no contorno): o pixel de borda puxado para o magenta sai."""
    a = np.array(img).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    opaco = a[..., 3] > 0
    borda = opaco & (cv2.erode(opaco.astype(np.uint8), np.ones((3, 3), np.uint8)) == 0)
    rosa = (r > 120) & (b > 90) & (g < 0.7 * np.minimum(r, b))
    a[(borda & rosa) | (opaco & rosa & (b > 150) & (g < 80)), 3] = 0
    return Image.fromarray(a.astype(np.uint8))


def poses(folha, n, anda):
    img = sem_fundo(Image.open(folha))
    lq = img.width / n
    cel = [img.crop((round(i * lq), 0, round((i + 1) * lq), img.height)) for i in range(n)]
    if anda:  # pés no centro de baixo de cada célula
        figs = [c.crop(c.getchannel("A").getbbox()) for c in cel]
        L, A = max(f.width for f in figs), max(f.height for f in figs)
        saida = []
        for f in figs:
            t = Image.new("RGBA", (L, A))
            t.paste(f, ((L - f.width) // 2, A - f.height))
            saida.append(t)
        return saida
    # parado no lugar: a mesma caixa para todas as células, para não tremer
    caixas = [c.getchannel("A").getbbox() for c in cel]
    caixa = (min(c[0] for c in caixas), min(c[1] for c in caixas), max(c[2] for c in caixas), max(c[3] for c in caixas))
    return [c.crop(caixa) for c in cel]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folha", type=Path)
    ap.add_argument("saida", type=Path)
    ap.add_argument("--largura", type=int, required=True)
    ap.add_argument("--meios", type=int, default=3)
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--anda", action="store_true")
    a = ap.parse_args()

    chaves = poses(a.folha, a.n, a.anda)
    fator = a.largura / chaves[0].width
    L, A = a.largura, round(chaves[0].height * fator)
    # o Blender enquadra a câmera pelo lado maior: figura alta vai numa tela larga (L2 >= A) e volta recortada no fim
    L2 = max(L, A)
    m = (L2 - L) // 2
    grandes = []
    for c in chaves:
        t = Image.new("RGBA", (L2 * AMPLIA, A * AMPLIA))
        t.paste(c.resize((L * AMPLIA, A * AMPLIA), Image.LANCZOS), (m * AMPLIA, 0))
        grandes.append(t)
    pares = list(zip(grandes, grandes[1:] + grandes[:1]))
    with tempfile.TemporaryDirectory(prefix="cenario_") as tmp:
        pasta = Path(tmp)
        quadros = []
        for i, (x, y) in enumerate(pares):
            x.save(pasta / f"chave{i}.png")
            np.save(pasta / f"ida{i}.npy", fluxo(x, y))
            np.save(pasta / f"volta{i}.npy", fluxo(y, x))
        for i in range(len(grandes)):
            j = (i + 1) % len(grandes)
            quadros.append({"imagem": f"chave{i}.png", "fluxo": None, "t": 0})
            for k in range(1, a.meios + 1):
                t = k / (a.meios + 1)
                ida = t <= 0.5
                quadros.append({"imagem": f"chave{i if ida else j}.png", "fluxo": f"{'ida' if ida else 'volta'}{i}.npy",
                                "t": t if ida else 1 - t})
        for k, q in enumerate(quadros):
            q["saida"] = f"saida{k:03d}.png"
            q["nome"] = f"{k:03d}"
        (pasta / "plano.json").write_text(json.dumps({"largura": L2 * AMPLIA, "altura": A * AMPLIA, "passo": PASSO,
                                                      "quadros": quadros}), encoding="utf-8")
        subprocess.run([str(BLENDER), "-b", "--python-exit-code", "1", "--python",
                        str(RAIZ / "ferramentas/blender_sprites.py"), "--", str(pasta)],
                       check=True, stdout=subprocess.DEVNULL)
        tira = Image.new("RGBA", (L * len(quadros), A))
        for k, q in enumerate(quadros):
            im = Image.open(pasta / q["saida"]).convert("RGBA").resize((L2, A), Image.LANCZOS).crop((m, 0, m + L, A))
            im.putalpha(im.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
            tira.paste(sem_rosa(im), (k * L, 0))
    a.saida.parent.mkdir(parents=True, exist_ok=True)
    tira.save(a.saida)
    print(f"{a.saida}: {len(quadros)} quadros de {L}x{A}")


if __name__ == "__main__":
    main()
