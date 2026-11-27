"""Compara o quinto desenho da folha de origem à peça nova na mesma escala vertical."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[3]


def silhueta(imagem):
    rgb = np.asarray(imagem.convert("RGB"))
    fundo = (rgb[:, :, 0] > 195) & (rgb[:, :, 1] < 50) & (rgb[:, :, 2] > 190)
    imagem = imagem.convert("RGBA")
    imagem.putalpha(Image.fromarray((~fundo).astype("uint8") * 255))
    return imagem


def medir_pes(peca):
    alfa = np.asarray(peca.getchannel("A")) > 0
    # Cada metade da faixa inferior contém um único tênis nas duas imagens.
    inicio = int(peca.height * 0.78)
    meio = peca.width // 2
    pes = []
    centros = []
    for deslocamento, faixa in ((0, alfa[inicio:, :meio]), (meio, alfa[inicio:, meio:])):
        linhas = np.flatnonzero(faixa.any(axis=1))
        sola = int(linhas[-1])
        pes.append(inicio + sola)
        colunas = np.flatnonzero(faixa[max(0, sola - 5):sola + 1].any(axis=0))
        centros.append(deslocamento + (int(colunas[0]) + int(colunas[-1])) / 2)
    return pes, centros[1] - centros[0]


folha = Image.open(RAIZ / "sprites/gbzin/quadros/folhas_arcade/agachado.png")
quadro = silhueta(folha.crop((1086, 0, 1352, 724)))
# Corte horizontal na cintura. A mão e o cajado sobrepostos continuam visíveis no original.
original = quadro.crop((0, 444, quadro.width, 606))
original = original.crop(original.getbbox())
estudo = silhueta(Image.open(PASTA / "quadril-pernas-agachado-estudo-v01.png"))
estudo = estudo.crop(estudo.getbbox())
altura = original.height
estudo = estudo.resize((round(estudo.width * altura / estudo.height), altura), Image.Resampling.NEAREST)

painel = Image.new("RGB", (600, 235), "#22272e")
rotulo = ImageDraw.Draw(painel)
for i, (nome, peca) in enumerate((("Original (quadro 5)", original), ("Peca gerada", estudo))):
    pes, base = medir_pes(peca)
    delta = abs(pes[0] - pes[1])
    x = i * 300 + (300 - peca.width) // 2
    y = 185 - altura
    painel.paste(peca, (x, y), peca)
    rotulo.line((i * 300 + 12, 185, (i + 1) * 300 - 12, 185), fill="#83d8b0")
    rotulo.text((i * 300 + 12, 197), f"{nome} | desnivel das solas: {delta} px", fill="white")
    rotulo.text((i * 300 + 12, 214), f"Distancia entre centros das solas: {base:g} px", fill="white")
    print(nome, peca.size, pes, delta, base)
painel.save(PASTA / "comparativo.png")

# Ciclo da folha-fonte, a uma cadência de inspeção. Remove fragmentos da célula vizinha.
import cv2

quadros = []
for i in range(8):
    esquerda, direita = (round(folha.width * n / 8) for n in (i, i + 1))
    pose = silhueta(folha.crop((esquerda, 125, direita, 620)))
    mascara = np.asarray(pose.getchannel("A"))
    _, grupos, estatisticas, _ = cv2.connectedComponentsWithStats(mascara)
    corpo = 1 + estatisticas[1:, cv2.CC_STAT_AREA].argmax()
    pose.putalpha(Image.fromarray(((grupos == corpo) * 255).astype("uint8")))
    tela = Image.new("RGB", (280, 500), "#22272e")
    tela.paste(pose, (4, 0), pose)
    quadros.append(tela)
quadros[0].save(PASTA / "guarda-agacha-guarda.gif", save_all=True,
                append_images=quadros[1:] + quadros[-2:0:-1], duration=140, loop=0)
