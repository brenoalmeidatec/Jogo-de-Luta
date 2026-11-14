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
from folhas_ck import NOMES as NOMES_CK
from folhas_gbzin import NOMES as NOMES_GBZIN
from folhas_raiclaven import FOLHAS_RAICLAVEN
from gerar_folhas import FOLHAS_PENGARO
from recortar_quadros import PE_DE_TRAS, PIVO, RAIZ, fatias, ponto_ancora, tira_fundo

# Qual lutador: LUTADOR=gutto python ferramentas/animar_folha.py ... (padrão: pengaro)
LUTADOR = os.environ.get("LUTADOR", "pengaro")
FOLHAS_LUTADOR = {"gutto": FOLHAS_GUTTO, "raiclaven": FOLHAS_RAICLAVEN}.get(LUTADOR, FOLHAS_PENGARO)
FOLHAS_CK = {n: ("pes", "") for n in NOMES_CK if not n.startswith("fx_")}  # base, despertar_a/b e as e_ do Modo Ratão
FOLHAS_GBZIN = {n: ("pes", "") for n in NOMES_GBZIN if not n.startswith("fx_") and "conceito" not in n}  # base, despertar e e_ do Deus Motoboy
if LUTADOR == "ck":
    FOLHAS_LUTADOR = FOLHAS_CK
if LUTADOR == "gbzin":
    FOLHAS_LUTADOR = FOLHAS_GBZIN
FOLHAS = RAIZ / "sprites" / LUTADOR / "quadros/folhas"
QUADROS = RAIZ / "sprites" / LUTADOR / "quadros"
QUADROS_ARCADE = RAIZ / "sprites" / LUTADOR / "quadros_arcade"  # arte arcade (quantizar_folha.py), fora do jogo por ora
def _achar_blender():
    """BLENDER do ambiente; senão o portátil 4.5 em ~/blender ou C:/Dev/Tools/Blender (o mais novo)."""
    if os.environ.get("BLENDER"):
        return Path(os.environ["BLENDER"])
    achados = sorted(p for raiz in (Path.home() / "blender", Path("C:/Dev/Tools/Blender")) if raiz.is_dir()
                     for p in raiz.glob("blender-4.5.*-windows-x64/blender.exe"))
    return achados[-1] if achados else Path.home() / "blender/blender-4.5.15-windows-x64/blender.exe"


BLENDER = _achar_blender()
AMPLIA = 4  # o Blender trabalha 4x maior que o quadro final
# HD=3: grava em quadros_hd/ os mesmos quadros (chaves e meio) em 3x, reduzidos da mesma renderização 4x do Blender;
# quadros/ de 1x não muda. O gerador troca cada sprite pelo gêmeo 3x (ferramentas/hd.py).
HD = int(os.environ.get("HD", "1"))
PASSO = 8  # um vértice a cada 2 pixels do quadro final
LARG, ALT = 360, 260  # mesma tela dos sprites do jogo, com folga para chute alto e salto
DESLOCA = (180 - PIVO[0], 220 - PIVO[1])  # do pivô antigo para os pés na tela do jogo
MEIOS = 6  # quadros do meio entre dois desenhos
ESCALA_2172 = {"pengaro": 0.40, "gutto": 0.33, "raiclaven": 0.33, "ck": 0.195, "gbzin": 0.288}[LUTADOR]  # a figura em pé dá ~111 px numa folha de 2172 de largura; a escala segue a largura da folha (o Gutto sai maior na folha, 340 px contra 278)
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
if LUTADOR == "ck":
    # CK: a figura ocupa quase a célula inteira da folha (~573 px em pé numa folha de 2172), por isso a escala 0.195;
    # sempre por célula (golpe que avança encosta na figura vizinha). AJUSTE: folhas em que a figura saiu de outro
    # tamanho, medido pela largura da cabeça contra a referência da forma (ferramentas/converter_ck.py --medir).
    POR_CELULA = POR_CELULA | set(FOLHAS_CK)
    AJUSTE = {"soco": 1.04, "martelo": 1.16, "chute_baixo": 1.16, "chute_alto": 1.03, "afastar": 1.04, "agachado": 1.04,
              "baixo_soco": 1.06, "rasteira": 1.04, "rasteirinha": 1.03, "ar_soco": 1.04, "pulo": 1.03, "queda": 1.20,
              "e_martelo": 1.08, "e_chute_baixo": 1.06, "e_chute_alto": 1.07, "e_golaco": 1.18, "e_caneta": 1.25, "e_soco": 1.14, "e_juliet_voadora": 1.06,
              "e_pulo": 1.05, "despertar_b": 1.07}
    # O magenta sai ANTES de quantizar (fundo_ck, na função poses): os quadros arcade já chegam ao Blender na paleta e
    # o sem_magenta apagaria o roxo do boné e da camisa do Ratão. Por isso o ck não entra em LIMPA_MAGENTA.
if LUTADOR == "gbzin":
    # Gbzin: mesmo caminho do CK (fundo_ck, sempre por célula). Em pé ele tem ~386 px numa folha de 2172 (o pedido de
    # folhas_gbzin.py fixa esse tamanho), por isso a escala 0.288 dá os mesmos ~111 px do jogo.
    POR_CELULA = POR_CELULA | set(FOLHAS_GBZIN)
    AJUSTE = {}


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


def fundo_ck(img):
    """CK: o fundo magenta das folhas vem com degradê (verde até ~40) e tira_fundo só apaga bolsão fechado de magenta
    puro. Aqui tudo o que é fundo vira #FF00FF exato, para o tira_fundo levar também o vão entre braço e tronco."""
    a = np.array(img.convert("RGB"))
    r, g, b = (a[..., i].astype(int) for i in range(3))
    fundo = (r > 170) & (b > 170) & (g < 130) & (np.abs(r - b) < 60)
    a[fundo] = (255, 0, 255)
    # Duas figuras vizinhas que se encostam (o pé de um chute no corpo do quadro seguinte) viram um pedaço só e o
    # por_celula cairia no corte reto por coluna, que decepa o membro. Aqui o pedaço grudado é separado no ponto fino:
    # desgasta até partir em dois corpos de células diferentes, cresce de volta e abre um fio de fundo na emenda.
    largura = a.shape[1] / 8
    for _ in range(4):  # três figuras grudadas saem em duas passadas
        mudou = False
        n, rotulos, dados, _ = cv2.connectedComponentsWithStats((~fundo).astype(np.uint8), connectivity=8)
        for i in range(1, n):
            x, y, w, h, area = dados[i]
            if w < 1.2 * largura or area < 4000:
                continue
            pedaco = (rotulos[y:y + h, x:x + w] == i).astype(np.uint8)
            emenda = np.zeros(pedaco.shape, bool)
            for voltas in range(1, 17):
                gasto = cv2.erode(pedaco, np.ones((3, 3), np.uint8), iterations=voltas)
                m, rot, info, centros = cv2.connectedComponentsWithStats(gasto, connectivity=8)
                grandes = [j for j in range(1, m) if info[j, cv2.CC_STAT_AREA] >= 0.2 * max(1, gasto.sum())]
                xs = sorted(centros[j][0] for j in grandes)
                # corpos de figuras diferentes ficam a quase uma célula um do outro (cabeça e tronco do deitado, não)
                if len(xs) >= 2 and xs[-1] - xs[0] >= 0.75 * largura:
                    break
            else:
                if w >= 1.8 * largura:  # emenda grossa: corte reto na coluna mais vazia do terço do meio
                    corte = w // 3 + int(np.argmin(pedaco[:, w // 3:2 * w // 3].sum(axis=0)))
                    emenda[:, corte:corte + 2] = pedaco[:, corte:corte + 2] > 0
                    fundo[y:y + h, x:x + w] |= emenda
                    mudou = True
                continue
            dono = np.where(np.isin(rot, grandes), rot, 0).astype(np.int32)
            while True:  # cresce cada corpo de volta dentro do pedaço, um pixel por vez
                livre = (pedaco > 0) & (dono == 0)
                if not livre.any():
                    break
                novo = dono.copy()
                for j in grandes:
                    perto = cv2.dilate((dono == j).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
                    novo[livre & perto & (novo == 0)] = j
                if (novo == dono).all():
                    break
                dono = novo
            for j in grandes:
                outros = cv2.dilate(((dono > 0) & (dono != j)).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
                emenda |= (dono == j) & outros
            fundo[y:y + h, x:x + w] |= emenda
            mudou = True
        if not mudou:
            break
    a[fundo] = (255, 0, 255)
    return Image.fromarray(a)


def poses(folha, ancora, amplia=AMPLIA):
    """Corta a folha e devolve as poses alinhadas no chão, `amplia` vezes maiores que o quadro final (4 para o Blender,
    1 para a escala do jogo, que é o que quantizar_folha.py usa)."""
    img = Image.open(folha)
    if LUTADOR in ("ck", "gbzin"):
        img = fundo_ck(img)
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


def sem_magenta(img, minimo=15):
    """Tira a fumaça que o ChatGPT misturou com o fundo magenta (fiapos rosa) e as sobras de menos de 15 pixels."""
    a = np.array(img).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    a[(a[..., 3] > 0) & (r > 110) & (b > 90) & (g < 0.75 * np.minimum(r, b)), 3] = 0
    n, rotulos, dados, _ = cv2.connectedComponentsWithStats((a[..., 3] > 0).astype(np.uint8), connectivity=8)
    for i in range(1, n):
        if dados[i, cv2.CC_STAT_AREA] < minimo:
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
        destino = (QUADROS_ARCADE if arcade else QUADROS.parent / "quadros_hd" if HD > 1 else QUADROS) / nome
        apagar = destino / "meio" if arcade else destino  # no arcade os desenhos 00..07 ficam como estão
        if apagar.exists():
            shutil.rmtree(apagar)
        (destino / "meio").mkdir(parents=True)
        for n, q in enumerate(quadros):
            if arcade and not q["nome"].startswith("meio/"):
                continue
            img = Image.open(pasta / q["saida"]).convert("RGBA").resize((LARG * HD, ALT * HD), Image.LANCZOS)
            img.putalpha(img.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
            if nome in LIMPA_MAGENTA or (LUTADOR == "gutto" and nome.startswith("e_")):
                img = sem_magenta(img, 15 * HD * HD)
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
