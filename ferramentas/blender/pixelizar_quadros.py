"""Dos renders grandes do Blender para pixel art: reduz, tira a meia transparência, usa UMA paleta para o lutador
inteiro (cores iguais em todos os quadros, sem cintilar) e põe o contorno escuro de 1 px.

Só precisa de pillow e numpy.
"""
from pathlib import Path

import numpy as np
from PIL import Image

TINTA = (22, 14, 26)


def reduzir(img, tamanho):
    img = img.convert("RGBA")
    # pré-multiplica para a borda não ficar clara/escura ao reduzir
    a = np.asarray(img).astype(np.float32)
    al = a[..., 3:4] / 255.0
    a[..., :3] *= al
    pre = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    pequeno = pre.resize(tamanho, Image.BOX)
    p = np.asarray(pequeno).astype(np.float32)
    alfa = p[..., 3:4] / 255.0
    rgb = np.where(alfa > 0, p[..., :3] / np.maximum(alfa, 1e-4), 0)
    out = np.concatenate([rgb, p[..., 3:4]], axis=-1).clip(0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def paleta(imagens, cores):
    pix = []
    for im in imagens:
        a = np.asarray(im)
        pix.append(a[a[..., 3] >= 128][:, :3])
    pix = np.concatenate(pix)
    # amostra para o quantizador ser rápido
    if len(pix) > 400000:
        pix = pix[np.random.RandomState(1).choice(len(pix), 400000, replace=False)]
    folha = Image.fromarray(pix.reshape(1, -1, 3).astype(np.uint8), "RGB")
    return folha.quantize(colors=cores, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)


def aplicar(im, pal, contorno=True):
    a = np.asarray(im)
    solido = a[..., 3] >= 128
    rgb = Image.fromarray(a[..., :3], "RGB").quantize(palette=pal, dither=Image.Dither.NONE).convert("RGB")
    saida = np.zeros_like(a)
    saida[..., :3] = np.asarray(rgb)
    saida[..., 3] = np.where(solido, 255, 0)
    saida[~solido, :3] = 0
    if contorno:
        s = solido
        viz = np.zeros_like(s)
        viz[1:, :] |= s[:-1, :]
        viz[:-1, :] |= s[1:, :]
        viz[:, 1:] |= s[:, :-1]
        viz[:, :-1] |= s[:, 1:]
        borda = viz & ~s
        saida[borda] = (*TINTA, 255)
    return Image.fromarray(saida, "RGBA")


def processar(pasta_renders, pasta_saida, tamanho=(224, 128), cores=40):
    """pasta_renders/<anim>/NN.png (grandes) -> pasta_saida/<anim>/NN.png (224x128, pixel art)."""
    pasta_renders, pasta_saida = Path(pasta_renders), Path(pasta_saida)
    arquivos = sorted(pasta_renders.glob("*/*.png"))
    pequenos = [reduzir(Image.open(f), tamanho) for f in arquivos]
    pal = paleta(pequenos, cores)
    saidas = []
    for f, im in zip(arquivos, pequenos):
        destino = pasta_saida / f.parent.name / f.name
        destino.parent.mkdir(parents=True, exist_ok=True)
        aplicar(im, pal).save(destino)
        saidas.append(destino)
    return saidas
