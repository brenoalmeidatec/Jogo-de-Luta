#!/usr/bin/env python3
"""Recria as animações a partir das folhas desenhadas: corta as poses e usa o Blender para os quadros do meio.

  python ferramentas/animar_folha.py soco chute_alto      só essas
  python ferramentas/animar_folha.py --todas              todas, 4 de cada vez
  python ferramentas/animar_folha.py --arcade soco        arte arcade: lê os desenhos já quantizados de
                                                          quadros_arcade/soco/00..07.png e grava só quadros_arcade/soco/meio/
                                                          (depois: quantizar_folha.py soco --meio)

Saída em sprites/<lutador>/quadros/<nome>/ (LUTADOR=gutto para o Gutto): 00..07.png são os desenhos e meio/03_2.png é o 2º quadro do meio entre os
desenhos 3 e 4. O gerador escolhe quantos usar pelos ticks de cada golpe (regra 7 de docs/regras-dos-lutadores.md).
ginga_fluida e anda_fluida são loops prontos, numerados em sequência. Um quadro do meio é sempre um desenho entortado,
nunca duas imagens misturadas.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from folhas_gutto import FOLHAS_GUTTO
from folhas_raiclaven import FOLHAS_RAICLAVEN
from gerar_folhas import FOLHAS_PENGARO
from recortar_quadros import PE_DE_TRAS, PIVO, RAIZ, fatias, ponto_ancora, tira_fundo

# Qual lutador: LUTADOR=gutto python ferramentas/animar_folha.py ... (padrão: pengaro)
LUTADOR = os.environ.get("LUTADOR", "pengaro")
FOLHAS_LUTADOR = {"gutto": FOLHAS_GUTTO, "raiclaven": FOLHAS_RAICLAVEN}.get(LUTADOR, FOLHAS_PENGARO)
FOLHAS = RAIZ / "sprites" / LUTADOR / "quadros/folhas"
QUADROS = RAIZ / "sprites" / LUTADOR / "quadros"
QUADROS_ARCADE = RAIZ / "sprites" / LUTADOR / "quadros_arcade"  # arte arcade (quantizar_folha.py), fora do jogo por ora
BLENDER = Path(os.environ.get("BLENDER", Path.home() / "blender/blender-4.5.15-windows-x64/blender.exe"))
AMPLIA = 4  # o Blender trabalha 4x maior que o quadro final
PASSO = 8  # um vértice a cada 2 pixels do quadro final
LARG, ALT = 360, 260  # mesma tela dos sprites do jogo, com folga para chute alto e salto
DESLOCA = (180 - PIVO[0], 220 - PIVO[1])  # do pivô antigo para os pés na tela do jogo
MEIOS = 6  # quadros do meio entre dois desenhos
ESCALA_2172 = {"pengaro": 0.40, "gutto": 0.33, "raiclaven": 0.33}[LUTADOR]  # a figura em pé dá ~111 px numa folha de 2172 de largura; a escala segue a largura da folha (o Gutto sai maior na folha, 340 px contra 278)
# Ginga: 8 desenhos + 8 x 7 = 64 quadros, um ciclo em cerca de 2 segundos. Andar: 8 + 8 x 5 = 48 quadros.
LOOPS = {"ginga_fluida": ("ginga", 7), "anda_fluida": ("anda", 5), "ginga_endiabrada": ("ginga_endiabrada", 7),
         "e_anda_fluida": ("e_anda", 5)}
# Com fumaça em volta, âncora nos pés ou na cabeça pula de quadro para quadro: usa o centro de cada célula.
# Folhas em que o ChatGPT desenhou a figura maior que na referência: guarda medida contra a ginga (113 px).
AJUSTE = {"lata": 0.89, "derrota": 0.89} if LUTADOR == "gutto" else {}
LIMPA_MAGENTA = {"endiabrado", "despertar_a", "despertar_b", "ginga_endiabrada"} if LUTADOR == "gutto" else set()
if LUTADOR == "raiclaven":  # tesoura e camisa escuras: o magenta vaza na borda de todas as folhas
    LIMPA_MAGENTA = set(FOLHAS_RAICLAVEN) | {"ginga_fluida", "anda_fluida"}
POR_CELULA = {"despertar_b", "ginga_endiabrada", "endiabrado"}  # e todas as folhas e_<golpe>, as versões endiabradas


# Pengaró: toda folha (normal e endiabrada) alinhada pelo centro do tronco no eixo do lutador. Alinhar pelo pé de trás
# ou pelo centro da célula deixava a forma endiabrada 20 a 40 px fora do lugar e fazia o corpo pular entre folhas.
PELO_TRONCO = LUTADOR == "pengaro"


def tronco(q):
    """Centro do tronco (faixa do peito à barriga) numa figura recortada: em cada linha, o meio do maior trecho cheio."""
    a = np.asarray(q)[..., 3] > 0
    h = a.shape[0]
    meios = []
    for y in range(int(h * 0.3), max(int(h * 0.3) + 1, int(h * 0.6))):
        linha = np.flatnonzero(a[y])
        if not len(linha):
            continue
        quebras = np.flatnonzero(np.diff(linha) > 1)
        inicios = np.r_[linha[0], linha[quebras + 1]]
        fins = np.r_[linha[quebras], linha[-1]]
        k = int(np.argmax(fins - inicios))
        meios.append((inicios[k] + fins[k]) / 2)
    return float(np.median(meios)) if meios else q.width / 2


def por_celula(img, fator, amplia=AMPLIA):
    """Separa as 8 figuras pela célula onde cada pedaço está, sem cortar perna que passa da célula.
    Cada figura fica com o centro da célula no eixo e a base no chão: quem faz o pulo subir é o jogo, não o desenho."""
    limpa = np.array(tira_fundo(img))
    largura = limpa.shape[1] / 8
    n, rotulos, dados, centros = cv2.connectedComponentsWithStats((limpa[..., 3] > 0).astype(np.uint8), connectivity=8)
    celula = np.full(n, -1)
    for i in range(1, n):
        if dados[i, cv2.CC_STAT_AREA] >= 40:
            celula[i] = min(7, int(centros[i][0] // largura))
    por_coluna = None
    if any(not (celula[rotulos] == i).any() for i in range(8)):
        # duas figuras coladas viraram um pedaço só: corta cada borda no vão de menor ocupação perto da divisa da célula
        ocupa = (limpa[..., 3] > 0).sum(axis=0)
        cortes = [0]
        for k in range(1, 8):
            ini, fim = int(k * largura - largura * .3), int(k * largura + largura * .3)
            cortes.append(ini + int(np.argmin(ocupa[ini:fim])))
        cortes.append(limpa.shape[1])
        por_coluna = cortes
    saida = []
    for i in range(8):
        if por_coluna:
            mascara = np.zeros(limpa.shape[:2], bool)
            mascara[:, por_coluna[i]:por_coluna[i + 1]] = True
        else:
            mascara = celula[rotulos] == i
        figura = Image.fromarray(np.where(mascara[..., None], limpa, 0).astype(np.uint8))
        caixa = figura.getchannel("A").getbbox()
        q = figura.crop(caixa)
        grande = q.resize((round(q.width * fator), round(q.height * fator)), Image.LANCZOS)
        tela = Image.new("RGBA", (LARG * amplia, ALT * amplia))
        if PELO_TRONCO:
            centro = round(tronco(q) * fator)
        else:
            centro = round(((i + 0.5) * largura - caixa[0]) * fator)
        tela.paste(grande, ((PIVO[0] + DESLOCA[0]) * amplia - centro,
                            (PIVO[1] + DESLOCA[1]) * amplia - grande.height), grande)
        saida.append(tela)
    return saida


def poses(folha, ancora, amplia=AMPLIA):
    """Corta a folha e devolve as poses alinhadas no chão, `amplia` vezes maiores que o quadro final (4 para o Blender,
    1 para a escala do jogo, que é o que quantizar_folha.py usa)."""
    img = Image.open(folha)
    fator = ESCALA_2172 * 2172 / img.width * amplia * AJUSTE.get(Path(folha).stem, 1)
    if Path(folha).stem in POR_CELULA or Path(folha).stem.startswith("e_") or LUTADOR in ("gutto", "raiclaven"):  # Gutto e Raiclaven: sempre por célula (golpes que avançam encostam nas figuras vizinhas)
        return por_celula(img, fator, amplia)
    saida = []
    for q in fatias(tira_fundo(img), 8):
        q = q.crop(q.getchannel("A").getbbox())
        ponto = tronco(q) if PELO_TRONCO else ponto_ancora(q, ancora)
        grande = q.resize((round(q.width * fator), round(q.height * fator)), Image.LANCZOS)
        tela = Image.new("RGBA", (LARG * amplia, ALT * amplia))
        referencia = (PIVO[0] if PELO_TRONCO else PE_DE_TRAS if ancora == "pes" else PIVO[0]) + DESLOCA[0]
        y = (PIVO[1] + DESLOCA[1]) * amplia - grande.height
        tela.paste(grande, (referencia * amplia - round(ponto * fator), y), grande)
        saida.append(tela)
    return saida


def sem_magenta(img):
    """Tira a fumaça que o ChatGPT misturou com o fundo magenta (fiapos rosa) e as sobras de menos de 15 pixels."""
    a = np.array(img).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    a[(a[..., 3] > 0) & (r > 110) & (b > 90) & (g < 0.75 * np.minimum(r, b)), 3] = 0
    n, rotulos, dados, _ = cv2.connectedComponentsWithStats((a[..., 3] > 0).astype(np.uint8), connectivity=8)
    for i in range(1, n):
        if dados[i, cv2.CC_STAT_AREA] < 15:
            a[rotulos == i, 3] = 0
    return Image.fromarray(a.astype(np.uint8))


def cinza(img):
    """Figura sobre fundo preto, para o cálculo do movimento não seguir o fundo."""
    a = np.asarray(img).astype(np.float32)
    return cv2.cvtColor((a[..., :3] * (a[..., 3:] / 255)).astype(np.uint8), cv2.COLOR_RGB2GRAY)


def fluxo(a, b):
    """Para onde cada ponto da figura a vai na figura b, medido na grade da malha."""
    calculo = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    campo = calculo.calc(cinza(a), cinza(b), None)
    peso = (np.asarray(a)[..., 3] > 128).astype(np.float32)
    # fora da figura o campo não vale nada: espalha o movimento da borda e suaviza para a malha não dobrar
    borrado = cv2.GaussianBlur(campo * peso[..., None], (0, 0), 10)
    peso_borrado = cv2.GaussianBlur(peso, (0, 0), 10)[..., None]
    campo = borrado / np.maximum(peso_borrado, 1e-3)
    h, w = peso.shape
    return campo[np.minimum(np.arange(0, h + 1, PASSO), h - 1)][:, np.minimum(np.arange(0, w + 1, PASSO), w - 1)]


def animar(nome, arcade=False):
    folha, meios = LOOPS.get(nome, (nome, MEIOS))
    ancora = FOLHAS_LUTADOR.get(folha, ("pes",))[0]
    loop = nome in LOOPS
    if arcade:
        # desenhos já na escala do jogo e na paleta: amplia sem misturar cor, o Blender só entorta
        assert not loop, "--arcade ainda não faz loops"
        chaves = [Image.open(QUADROS_ARCADE / nome / f"{i:02d}.png").convert("RGBA")
                  .resize((LARG * AMPLIA, ALT * AMPLIA), Image.NEAREST) for i in range(8)]
    else:
        chaves = poses(FOLHAS / f"{folha}.png", ancora)
    pares = list(zip(chaves, chaves[1:] + chaves[:1])) if loop else list(zip(chaves, chaves[1:]))
    with tempfile.TemporaryDirectory(prefix="animar_") as tmp:
        pasta = Path(tmp)
        for i, c in enumerate(chaves):
            c.save(pasta / f"chave{i}.png")
        quadros = []
        for i, (x, y) in enumerate(pares):
            np.save(pasta / f"ida{i}.npy", fluxo(x, y))
            np.save(pasta / f"volta{i}.npy", fluxo(y, x))
            j = (i + 1) % len(chaves)
            quadros.append({"imagem": f"chave{i}.png", "fluxo": None, "t": 0, "nome": f"{i:02d}"})
            for k in range(1, meios + 1):
                t = k / (meios + 1)
                ida = t <= 0.5
                quadros.append({"imagem": f"chave{i if ida else j}.png", "fluxo": f"{'ida' if ida else 'volta'}{i}.npy",
                                "t": t if ida else 1 - t, "nome": f"meio/{i:02d}_{k}"})
        if not loop:
            quadros.append({"imagem": f"chave{len(chaves) - 1}.png", "fluxo": None, "t": 0, "nome": f"{len(chaves) - 1:02d}"})
        for n, q in enumerate(quadros):
            q["saida"] = f"saida{n:03d}.png"
        (pasta / "plano.json").write_text(json.dumps({"largura": LARG * AMPLIA, "altura": ALT * AMPLIA,
                                                      "passo": PASSO, "quadros": quadros}), encoding="utf-8")
        subprocess.run([str(BLENDER), "-b", "--python-exit-code", "1", "--python",
                        str(RAIZ / "ferramentas/blender_sprites.py"), "--", str(pasta)],
                       check=True, stdout=subprocess.DEVNULL)
        destino = (QUADROS_ARCADE if arcade else QUADROS) / nome
        apagar = destino / "meio" if arcade else destino  # no arcade os desenhos 00..07 ficam como estão
        if apagar.exists():
            shutil.rmtree(apagar)
        (destino / "meio").mkdir(parents=True)
        for n, q in enumerate(quadros):
            if arcade and not q["nome"].startswith("meio/"):
                continue
            img = Image.open(pasta / q["saida"]).convert("RGBA").resize((LARG, ALT), Image.LANCZOS)
            img.putalpha(img.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
            if nome in LIMPA_MAGENTA or (LUTADOR == "gutto" and nome.startswith("e_")):
                img = sem_magenta(img)
            img.save(destino / (f"{n:02d}.png" if loop else f"{q['nome']}.png"))
        if loop:
            (destino / "meio").rmdir()
    print(f"{nome}: {len(quadros)} quadros", flush=True)


def main():
    pedidas = sys.argv[1:]
    arcade = "--arcade" in pedidas
    if arcade:
        pedidas = [p for p in pedidas if p != "--arcade"]
        with ThreadPoolExecutor(4) as trabalho:
            list(trabalho.map(lambda n: animar(n, True), pedidas))
        return
    if pedidas == ["--todas"]:
        ignorar = {"endiabrado", "ginga", "anda"}
        pedidas = ["soco", "despertar_a", "despertar_b", *LOOPS, *(n for n in FOLHAS_LUTADOR if n not in ignorar),
                   *(f.stem for f in FOLHAS.glob("e_*.png") if f.stem != "e_anda")]
    with ThreadPoolExecutor(4) as trabalho:
        list(trabalho.map(animar, pedidas))


if __name__ == "__main__":
    main()
