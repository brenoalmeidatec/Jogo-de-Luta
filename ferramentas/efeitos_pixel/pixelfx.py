#!/usr/bin/env python3
"""Pixel FX: transforma quadros renderizados (PNG RGBA, ex.: do Blender) em sprites de pixel art.

É a técnica, não a biblioteca pixelfx antiga de assets/efeitos/: o render 3D vira poucos pixels, com paleta curta,
sem anti-aliasing, alfa só 0/255, contorno seco de 1 px e um pouco de dithering ordenado (Bayer) nas transições.
Só usa Pillow + numpy, então roda fora do Blender também.

  python pixelfx.py ENTRADA/ SAIDA/ --tam 48 --bloco 3 --paleta fogo
  python pixelfx.py ENTRADA/ SAIDA/ --paleta "#3c1422,#8a2414,#d8481a,#f89a2c,#ffe27a,#fffbe0"

ENTRADA tem os quadros em ordem alfabética (0000.png, 0001.png...). Na SAIDA ficam 00.png.., folha.png (fila, fundo
transparente), previa.png e previa.gif (fundo escuro, ampliados, só para olhar).

Como a cor sai (--modo):
  rampa  (padrão) o brilho do render escolhe a cor numa rampa escura->clara. Bom para fogo, faísca, energia, fumaça:
         renderize em branco/cinza e troque a cor de cada lutador só trocando a paleta.
  cores  cada pixel vai para a cor mais próxima da paleta. Para renders que já têm cor.
A primeira cor da paleta é sempre o contorno (nunca preto puro: regra 5 do estilo arcade).

Escala: --tam é o tamanho da arte em pixels de jogo; --bloco multiplica no fim (vizinho mais próximo). Com --bloco 3 o
quadro sai no padrão 3x do projeto (regra-alta-resolucao.md) e o Explod usa scale = 1/3.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

PALETAS = {
    # contorno, sombra ... luz. Todo canal >= 20 (sem preto puro).
    "fogo": ["#3c1422", "#8a2414", "#d8481a", "#f89a2c", "#ffe27a", "#fffbe0"],
    "violeta": ["#1e1432", "#4a1e6e", "#7e32b4", "#b45ae6", "#e0a8ff", "#fbf0ff"],   # sombra do endiabrado
    "eletrico": ["#141e3c", "#1e4a96", "#2e8ce6", "#6cd2ff", "#c8f4ff", "#ffffff"],
    "faisca": ["#3a2a1e", "#a0702a", "#e8b43c", "#fff08c", "#ffffff"],
    "poeira": ["#2e2420", "#5e4c3c", "#8c7660", "#bca486", "#e6d6bc"],
}

BAYER4 = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) + 0.5) / 16.0


def ler_paleta(texto):
    cores = PALETAS.get(texto, texto.split(",") if "," in texto else None)
    if cores is None:
        raise SystemExit(f"paleta desconhecida: {texto} (use {', '.join(PALETAS)} ou uma lista #hex,#hex,...)")
    rgb = np.array([[int(c.strip().lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)] for c in cores], np.uint8)
    if len(rgb) < 3:
        raise SystemExit("a paleta precisa de pelo menos 3 cores (contorno + 2)")
    return rgb


def bayer(h, w):
    return np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w] - 0.5          # -0.5 .. 0.5


def reduzir(img, tam):
    """RGBA grande -> RGBA pequeno (tam = lado maior), média com alfa pré-multiplicado (sem halo escuro)."""
    w, h = img.size
    k = tam / max(w, h)
    novo = (max(1, round(w * k)), max(1, round(h * k)))
    return np.asarray(img.convert("RGBa").resize(novo, Image.BOX).convert("RGBA"), np.float32) / 255.0


def pixelar(rgba, paleta, modo="rampa", dither=0.5, dither_alfa=0.35, corte=0.5, contorno=True, limpar=True,
            brilho=1.0, gama=1.0):
    """rgba float (H, W, 4) 0..1 -> índice da paleta (H, W) int16, -1 = transparente."""
    h, w = rgba.shape[:2]
    b = bayer(h, w)
    alfa = rgba[..., 3]
    opaco = (alfa + b * dither_alfa) > corte
    n = len(paleta)
    if modo == "rampa":
        lum = rgba[..., 0] * 0.2126 + rgba[..., 1] * 0.7152 + rgba[..., 2] * 0.0722
        v = np.clip(lum * brilho, 0, 1) ** gama
        # índices 1..n-1 (o 0 é do contorno); o Bayer mexe só na fronteira entre dois tons
        idx = np.clip(np.floor(v * (n - 1) + 0.5 + b * dither), 1, n - 1).astype(np.int16)
    else:
        cor = rgba[..., :3] * 255 + (b * dither * 48)[..., None]
        dist = ((cor[:, :, None, :] - paleta[None, None, 1:, :].astype(np.float32)) ** 2).sum(-1)
        idx = (dist.argmin(-1) + 1).astype(np.int16)
    idx[~opaco] = -1
    if limpar:                     # pixel solto (sem vizinho em cruz) é sujeira de render
        o = idx >= 0
        p = np.pad(o, 1)
        viz = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
        idx[o & (viz == 0)] = -1
    if contorno:                   # 1 px seco por fora, em cruz (sem diagonal fica mais arcade)
        o = np.pad(idx >= 0, 1)
        borda = (o[:-2, 1:-1] | o[2:, 1:-1] | o[1:-1, :-2] | o[1:-1, 2:]) & ~o[1:-1, 1:-1]
        idx[borda] = 0
    return idx


def para_imagem(idx, paleta, bloco=1):
    h, w = idx.shape
    out = np.zeros((h, w, 4), np.uint8)
    m = idx >= 0
    out[m, :3] = paleta[idx[m]]
    out[m, 3] = 255
    if bloco > 1:
        out = out.repeat(bloco, 0).repeat(bloco, 1)
    return Image.fromarray(out, "RGBA")


def processar(quadros, saida, paleta, tam=48, bloco=3, previa=True, **kw):
    """quadros: lista de PIL RGBA. Escreve 00.png.., folha.png, previa.png/gif. Devolve a lista de sprites."""
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    for velho in saida.glob("[0-9][0-9].png"):
        velho.unlink()
    margem = 1 if kw.get("contorno", True) else 0
    sprites = []
    for i, q in enumerate(quadros):
        rgba = reduzir(q, tam - 2 * margem)
        rgba = np.pad(rgba, ((margem, margem), (margem, margem), (0, 0)))   # espaço para o contorno
        s = para_imagem(pixelar(rgba, paleta, **kw), paleta, bloco)
        s.save(saida / f"{i:02d}.png")
        sprites.append(s)
    w, h = sprites[0].size
    folha = Image.new("RGBA", (w * len(sprites), h), (0, 0, 0, 0))
    for i, s in enumerate(sprites):
        folha.paste(s, (i * w, 0))
    folha.save(saida / "folha.png")
    if previa:
        fundo = Image.new("RGBA", folha.size, (34, 30, 46, 255))
        fundo.alpha_composite(folha)
        z = max(1, 4 // bloco)
        fundo.resize((fundo.width * z, fundo.height * z), Image.NEAREST).save(saida / "previa.png")
        gif = []
        for s in sprites:
            f = Image.new("RGBA", s.size, (34, 30, 46, 255))
            f.alpha_composite(s)
            gif.append(f.resize((w * z, h * z), Image.NEAREST).convert("P", palette=Image.ADAPTIVE))
        gif[0].save(saida / "previa.gif", save_all=True, append_images=gif[1:], duration=70, loop=0, disposal=2)
    return sprites


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("saida")
    ap.add_argument("--paleta", default="fogo")
    ap.add_argument("--modo", choices=["rampa", "cores"], default="rampa")
    ap.add_argument("--tam", type=int, default=48, help="lado maior da arte, em pixels de jogo (48)")
    ap.add_argument("--bloco", type=int, default=3, help="ampliação final, vizinho mais próximo (3 = padrão 3x)")
    ap.add_argument("--dither", type=float, default=0.5, help="0 = sem dithering de cor; 1 = forte")
    ap.add_argument("--dither-alfa", type=float, default=0.35, help="dithering na borda que some")
    ap.add_argument("--corte", type=float, default=0.5, help="alfa mínimo para virar pixel")
    ap.add_argument("--brilho", type=float, default=1.0)
    ap.add_argument("--gama", type=float, default=1.0, help="<1 clareia os tons médios, >1 escurece")
    ap.add_argument("--sem-contorno", action="store_true")
    a = ap.parse_args(argv)
    arquivos = sorted(Path(a.entrada).glob("*.png"))
    if not arquivos:
        raise SystemExit(f"nenhum PNG em {a.entrada}")
    quadros = [Image.open(p).convert("RGBA") for p in arquivos]
    processar(quadros, a.saida, ler_paleta(a.paleta), tam=a.tam, bloco=a.bloco, modo=a.modo, dither=a.dither,
              dither_alfa=a.dither_alfa, corte=a.corte, contorno=not a.sem_contorno, brilho=a.brilho, gama=a.gama)
    print(f"{len(quadros)} quadros -> {a.saida}")


if __name__ == "__main__":
    sys.exit(main())
