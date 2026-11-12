#!/usr/bin/env python3
"""CK: converte as folhas de sprites/ck/quadros/folhas_arcade/ para a arte arcade do jogo.

  python ferramentas/converter_ck.py                 todas as folhas (corpo e efeitos)
  python ferramentas/converter_ck.py soco e_soco     só essas
  python ferramentas/converter_ck.py --contato DIR   folhas de contato do resultado (para olhar)
  python ferramentas/converter_ck.py --medir         altura e largura de cada quadro convertido

Corpo: sprites/ck/quadros_arcade/<folha>/00..07.png, tela 360x260, base em y=219, 15 cores + transparente. A forma
base usa paleta_arcade.json; as folhas e_* e o despertar_b usam paleta_arcade_ratao.json. É o mesmo corte e a mesma
quantização de `LUTADOR=ck python ferramentas/quantizar_folha.py <folha>` (FORMA=ratao para as e_*), mais:
  - cada pedaço solto vai para a figura mais perto dele (não para a célula onde cai o centro) e as figuras são
    realinhadas numa folha com folga antes do corte;
  - escala por quadro nas folhas de queda e levantada (o corpo deitado não cabe na célula da folha e veio menor);
  - os retoques de ferramentas/retoques_arcade/ck.py (quadro copiado do vizinho, faísca e projétil fora do corpo).
Não gera quadro do meio: as folhas de loop (referencia_ginga, anda e as e_) entram só com os 8 desenhos; nas outras,
quem quiser smear roda animar_folha.py --arcade <folha> e quantizar_folha.py <folha> --meio depois.

Efeitos (fx_*): sprites/ck/efeitos/<nome>/00..07.png, todos os quadros na mesma tela, sem paleta de corpo (até 15 cores
próprias do efeito, sem dithering). Pivô: meio da borda de baixo nos efeitos de chão (aura, paredao), centro da tela nos
outros. O boné e o óculos que voam saem das folhas bone_voador e e_juliet_voadora (efeitos/bone e efeitos/juliet).
"""
import json
import os
import sys
from pathlib import Path

os.environ["LUTADOR"] = "ck"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "retoques_arcade"))

import cv2  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import animar_folha as af  # noqa: E402
import quantizar_folha as qf  # noqa: E402
import ck as retoques  # noqa: E402

SPRITES = af.RAIZ / "sprites/ck"
ENTRADA = SPRITES / "quadros/folhas_arcade"
# HD=3: os mesmos desenhos no triplo da resolução, em quadros_arcade_hd/ (tela 1080x780, pés em 540,660). O gerador
# troca cada sprite do jogo pelo gêmeo HD e desenha o lutador em 1/3 (gerar_pengaro.HD); os efeitos ficam como estão.
HD = int(os.environ.get("HD", "1"))
retoques.E = HD
SAIDA = SPRITES / ("quadros_arcade_hd" if HD > 1 else "quadros_arcade")
EFEITOS_SAIDA = SPRITES / "efeitos"
BASE_Y = (af.PIVO[1] + af.DESLOCA[1]) * HD  # 220: a figura ocupa até a linha 219
EIXO_X = (af.PIVO[0] + af.DESLOCA[0]) * HD  # 180

# Escala por quadro (vezes a escala da folha). Deitado, o corpo tem ~65 px de comprido na célula; em pé tem 112.
ESCALA_QUADRO = {
    "levanta": [1.5, 1.5, 1.3, 1.25, 1.3, 1.15, 1.15, 1.28],
    "e_queda": [1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.45],
    "e_levanta": [1.4, 1.1, 1, 1, 1, 1, 1, 1],
}
# efeito -> (escala sobre a do corpo, ou None com a largura final em px; efeito de chão)
EFEITOS = {"aura": (1.25, None, True), "fumaca": (1.3, None, False), "garrafa": (1.0, None, False),
           "paredao": (None, 120, True)}


# (folha, quadro) -> nº do quadro em efeitos/despertar_fumaca/
FUMACA_DO_DESPERTAR = {("despertar_a", 6): 0, ("despertar_a", 7): 1, ("despertar_b", 0): 2, ("despertar_b", 1): 3}


def forma(nome):
    return "ratao" if nome.startswith("e_") or nome == "despertar_b" else ""


def paleta(nome):
    arq = SPRITES / (f"paleta_arcade_{forma(nome)}.json" if forma(nome) else "paleta_arcade.json")
    dados = json.loads(arq.read_text(encoding="utf-8"))
    return dados, np.array([c["rgb"] for c in dados["cores"]], np.uint8)


def separar(nome):
    """Folha -> (8 figuras RGBA no tamanho da folha, {efeito: RGBA solto}). Cada célula fica com o maior pedaço cujo
    centro cai nela (o corpo); pedaço pequeno vai para o corpo mais PERTO, não para a célula onde está o centro dele
    (a cabeça do deitado e o risco embaixo do pé caíam no quadro vizinho). Projétil de retoques.SOLTO sai aqui."""
    limpa = np.array(af.tira_fundo(af.fundo_ck(Image.open(ENTRADA / f"{nome}.png"))))
    n, rot, info, centros = cv2.connectedComponentsWithStats((limpa[..., 3] > 0).astype(np.uint8), connectivity=8)
    largura = limpa.shape[1] / 8
    corpo = {}
    for j in range(1, n):
        c = min(7, int(centros[j][0] // largura))
        if c not in corpo or info[j, cv2.CC_STAT_AREA] > info[corpo[c], cv2.CC_STAT_AREA]:
            corpo[c] = j
    assert len(corpo) == 8, f"{nome}: só achei corpo nas células {sorted(corpo)}"
    longe = np.stack([cv2.distanceTransform((rot != corpo[c]).astype(np.uint8), cv2.DIST_L2, 3) for c in range(8)])
    dono = np.full(n, -1)
    candidatos = {}  # efeito -> maior pedaço solto do quadro
    for c in range(8):
        dono[corpo[c]] = c
    for j in range(1, n):
        if dono[j] >= 0 or info[j, cv2.CC_STAT_AREA] < 12:
            continue
        x, y, w, h, _ = info[j]
        d = longe[:, y:y + h, x:x + w][:, rot[y:y + h, x:x + w] == j].min(axis=1)
        c = int(d.argmin())
        no_centro = min(7, int(centros[j][0] // largura))
        if (nome, no_centro) in retoques.SOLTO and info[j, cv2.CC_STAT_AREA] >= 400:
            c = no_centro  # o projétil já perto do quadro seguinte ainda é do quadro em que foi desenhado
        if (nome, c) in retoques.SOLTO:
            efeito_solto = retoques.SOLTO[nome, c]
            if efeito_solto and (efeito_solto not in candidatos
                                 or info[j, cv2.CC_STAT_AREA] > info[candidatos[efeito_solto], cv2.CC_STAT_AREA]):
                candidatos[efeito_solto] = j
            if info[j, cv2.CC_STAT_AREA] >= 400 or d[c] > 30:
                continue  # o projétil e os riscos de movimento dele não ficam no corpo
        dono[j] = c
    soltos = {}
    for efeito_solto, j in candidatos.items():
        x, y, w, h, area = info[j]
        if area >= 400:
            soltos[efeito_solto] = Image.fromarray(
                np.where((rot == j)[..., None], limpa, 0).astype(np.uint8)).crop((x, y, x + w, y + h))
    return [np.where((dono[rot] == c)[..., None], limpa, 0).astype(np.uint8) for c in range(8)], soltos


def cortar(nome):
    """(as 8 figuras na tela do jogo, RGBA, antes de quantizar; {efeito: RGBA solto na escala do jogo})."""
    figuras, soltos = separar(nome)
    alt, larg = figuras[0].shape[:2]
    # folha com células 3x mais largas: nenhuma figura encosta na vizinha e o por_celula de sempre (centro da célula
    # no eixo, base no chão) recebe cada uma inteira
    passo = 3 * larg // 8
    folga = np.zeros((alt, 8 * passo, 4), np.uint8)
    for c, f in enumerate(figuras):
        dx = round((c + .5) * passo - (c + .5) * larg / 8)
        xs = np.nonzero(f[..., 3].any(axis=0))[0]
        x0, x1 = xs.min(), xs.max() + 1
        folga[:, x0 + dx:x1 + dx] = np.maximum(folga[:, x0 + dx:x1 + dx], f[:, x0:x1])
    folha = Image.new("RGB", (folga.shape[1], alt), (255, 0, 255))
    folha.paste(Image.fromarray(folga), (0, 0), Image.fromarray(folga[..., 3]))
    fator = af.ESCALA_2172 * 2172 / larg * af.AJUSTE.get(nome, 1)
    for efeito_solto, img in soltos.items():
        g = img.resize((max(1, round(img.width * fator)), max(1, round(img.height * fator))), Image.LANCZOS)
        g.putalpha(g.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
        soltos[efeito_solto] = g
    if nome not in ESCALA_QUADRO:
        return af.por_celula(folha, fator * HD, HD), soltos
    saida = []
    eixo1 = EIXO_X // HD  # eixo na tela de 1x; a tela de 4x tem o eixo em 4 * eixo1
    for q, k in zip(af.por_celula(folha, fator * 4, 4), ESCALA_QUADRO[nome]):
        x0, y0, x1, y1 = q.getbbox()
        fig = q.crop((x0, y0, x1, y1))
        fig = fig.resize((max(1, round(fig.width * k * HD / 4)), max(1, round(fig.height * k * HD / 4))), Image.LANCZOS)
        tela = Image.new("RGBA", (af.LARG * HD, af.ALT * HD))
        centro = EIXO_X + ((x0 + x1) / 2 - eixo1 * 4) * k * HD / 4
        tela.paste(fig, (round(centro - fig.width / 2), BASE_Y - fig.height), fig)
        saida.append(tela)
    return saida, soltos


def fumaca_do_despertar(i, q):
    """Os 4 quadros em que a fumaça cobre o corpo, também em cores próprias (a paleta do corpo não tem o cinza-
    esverdeado da fumaça e ela sai lilás): efeitos/despertar_fumaca/0i.png, na mesma tela 360x260 do corpo."""
    pasta = EFEITOS_SAIDA / "despertar_fumaca"
    pasta.mkdir(parents=True, exist_ok=True)
    cor = q.convert("RGB").quantize(15, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGBA")
    cor.putalpha(q.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    cor.save(pasta / f"{i:02d}.png")


def no_chao(q):
    """Depois de um retoque que tira coisa do quadro, a figura volta a encostar na linha do chão."""
    caixa = q.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox()  # o quantizador corta em 128
    if caixa is None or caixa[3] == BASE_Y:
        return q
    tela = Image.new("RGBA", q.size)
    tela.paste(q, (0, BASE_Y - caixa[3]))
    return tela


def solto_como_efeito(nome, img, dados, pal):
    """Projétil que saiu de um quadro do corpo: recortado justo, na paleta da forma, em efeitos/<nome>/00.png."""
    tela = Image.new("RGBA", (img.width + 4, img.height + 4))
    tela.paste(img, (2, 2))
    q = qf.para_imagem(qf.quantizar(tela, dados, pal), pal)
    q = q.crop(q.getbbox())
    pasta = EFEITOS_SAIDA / nome
    pasta.mkdir(parents=True, exist_ok=True)
    q.save(pasta / "00.png")
    print(f"  efeitos/{nome}: 1 quadro {q.width}x{q.height}")


def corpo(nome):
    dados, pal = paleta(nome)
    quadros, soltos = cortar(nome)
    for efeito_solto, img in soltos.items() if HD == 1 else ():  # no HD só o corpo: os efeitos ficam os de 1x
        solto_como_efeito(efeito_solto, img, dados, pal)
    destino = SAIDA / nome
    destino.mkdir(parents=True, exist_ok=True)
    prontos = []
    for i, q in enumerate(quadros):
        q = no_chao(retoques.retocar(nome, i, q, nome.startswith("e_")))
        if (nome, i) in FUMACA_DO_DESPERTAR and HD == 1:
            fumaca_do_despertar(FUMACA_DO_DESPERTAR[nome, i], q)
        prontos.append(qf.para_imagem(qf.quantizar(q, dados, pal), pal))
    for (folha, i), origem in retoques.COPIA.items():
        if folha == nome:
            prontos[i] = prontos[origem].copy()
    for i, q in enumerate(prontos):
        q.save(destino / f"{i:02d}.png")
    print(f"{nome}: {len(prontos)} desenhos ({forma(nome) or 'base'})", flush=True)


def recortar_efeito(nome):
    """Folha fx_<nome> -> 8 células RGBA no tamanho da folha, cada pedaço na célula onde está o centro dele."""
    a = np.array(Image.open(ENTRADA / f"fx_{nome}.png").convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if nome == "garrafa":  # fundo magenta: a garrafa é verde
        fundo = (r > 170) & (b > 170) & (g < 130)
    else:
        fundo = (g > 170) & (r < 130) & (b < 130) & (g - np.maximum(r, b) > 80)
        beira = cv2.dilate(fundo.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        g = np.where(beira, np.minimum(g, np.maximum(r, b) + 25), g)  # verde do fundo que vaza na borda
    rgba = np.dstack([r, g, b, np.where(fundo, 0, 255)]).astype(np.uint8)
    n, rot, info, centros = cv2.connectedComponentsWithStats((~fundo).astype(np.uint8), connectivity=8)
    largura = rgba.shape[1] / 8
    celula = np.full(n, -1)
    for i in range(1, n):
        if info[i, cv2.CC_STAT_AREA] >= 12:
            celula[i] = min(7, int(centros[i][0] // largura))
    return [np.where((celula[rot] == i)[..., None], rgba, 0).astype(np.uint8) for i in range(8)], largura


def efeito(nome):
    escala, largura_final, chao = EFEITOS[nome]
    celulas, largura = recortar_efeito(nome)
    # caixa comum, medida a partir do centro de cada célula
    esq = dir_ = 0
    topo, base = 10 ** 6, 0
    for i, c in enumerate(celulas):
        ys, xs = np.nonzero(c[..., 3])
        cx = (i + .5) * largura
        esq, dir_ = max(esq, cx - xs.min()), max(dir_, xs.max() + 1 - cx)
        topo, base = min(topo, ys.min()), max(base, ys.max() + 1)
    meia = int(np.ceil(max(esq, dir_)))
    if not chao:  # pivô no centro: a caixa fica simétrica em volta da linha do meio da folha
        cy = celulas[0].shape[0] // 2
        m = max(cy - topo, base - cy)
        topo, base = cy - m, cy + m
    fator = af.ESCALA_2172 * 2172 / celulas[0].shape[1] * escala if escala else largura_final / (2 * meia)
    quadros = []
    for i, c in enumerate(celulas):
        cx = round((i + .5) * largura)
        tela = Image.new("RGBA", (2 * meia, base - topo))
        tela.paste(Image.fromarray(c), (meia - cx, -topo))
        q = tela.resize((max(1, round(tela.width * fator)), max(1, round(tela.height * fator))), Image.LANCZOS)
        q.putalpha(q.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
        quadros.append(q)
    # até 15 cores para o efeito inteiro, sem dithering (pixel seco, como o corpo)
    opacos = np.concatenate([np.asarray(q)[..., :3][np.asarray(q)[..., 3] > 0] for q in quadros])
    # paleta por k-médias em Lab: o corte pela mediana só olha a quantidade e apagava as luzes coloridas do paredão
    unicas, vezes = np.unique(opacos, axis=0, return_counts=True)
    lab = cv2.cvtColor(unicas.reshape(-1, 1, 3), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)
    peso = np.minimum(vezes, 40)  # cor rara mas presente também disputa lugar
    amostra = np.repeat(lab, peso, axis=0)
    cv2.setRNGSeed(7)
    _, _, centros = cv2.kmeans(amostra, min(15, len(unicas)), None,
                               (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 60, .2), 4, cv2.KMEANS_PP_CENTERS)
    cores = cv2.cvtColor(np.clip(centros, 0, 255).astype(np.uint8).reshape(-1, 1, 3), cv2.COLOR_LAB2RGB).reshape(-1, 3)
    pal = Image.new("P", (1, 1))
    pal.putpalette(cores.astype(np.uint8).tobytes() + bytes(cores[0].astype(np.uint8)) * (256 - len(cores)))
    pasta = EFEITOS_SAIDA / nome
    pasta.mkdir(parents=True, exist_ok=True)
    for i, q in enumerate(quadros):
        cor = q.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE).convert("RGBA")
        cor.putalpha(q.getchannel("A"))
        cor.save(pasta / f"{i:02d}.png")
    print(f"efeitos/{nome}: 8 quadros {quadros[0].width}x{quadros[0].height} "
          f"(pivô {'no meio da base' if chao else 'no centro'})", flush=True)


def contato(destino):
    """Folhas de contato do resultado: 6 folhas por imagem, cada quadro com a linha do chão e o eixo marcados."""
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    pastas = sorted(p for p in SAIDA.iterdir() if p.is_dir())
    caixa = (95, 75, 265, 228)
    w, h = caixa[2] - caixa[0], caixa[3] - caixa[1]
    for k in range(0, len(pastas), 6):
        tela = Image.new("RGB", (8 * w, 6 * h), (70, 110, 90))
        d = ImageDraw.Draw(tela)
        for j, pasta in enumerate(pastas[k:k + 6]):
            for i in range(8):
                q = Image.open(pasta / f"{i:02d}.png").convert("RGBA").crop(caixa)
                d.line([(i * w, j * h + BASE_Y - caixa[1]), ((i + 1) * w, j * h + BASE_Y - caixa[1])], fill=(40, 70, 55))
                d.line([(i * w + EIXO_X - caixa[0], j * h), (i * w + EIXO_X - caixa[0], (j + 1) * h)], fill=(60, 95, 78))
                tela.paste(q, (i * w, j * h), q)
                d.text((i * w + 3, j * h + 2), f"{pasta.name} {i}" if i == 0 else str(i), fill=(255, 255, 0))
        tela.save(destino / f"arcade_{k // 6:02d}.png")
    fx = sorted(p for p in EFEITOS_SAIDA.iterdir() if p.is_dir()) if EFEITOS_SAIDA.exists() else []
    if fx:
        alt = [max(Image.open(f).height for f in p.glob("*.png")) for p in fx]
        tela = Image.new("RGB", (8 * 130, sum(alt) + 4 * len(fx)), (70, 70, 110))
        y = 0
        for p, a in zip(fx, alt):
            for i, f in enumerate(sorted(p.glob("*.png"))):
                q = Image.open(f).convert("RGBA")
                tela.paste(q, (i * 130, y), q)
            ImageDraw.Draw(tela).text((3, y + 2), p.name, fill=(255, 255, 0))
            y += a + 4
        tela.save(destino / "arcade_efeitos.png")
    print(f"contato em {destino}")


def medir():
    for pasta in sorted(p for p in SAIDA.iterdir() if p.is_dir()):
        caixas = [Image.open(pasta / f"{i:02d}.png").getbbox() for i in range(8)]
        print(f"{pasta.name:20s} alt {[c[3] - c[1] for c in caixas]}  larg {[c[2] - c[0] for c in caixas]}  "
              f"base {sorted({c[3] - 1 for c in caixas})}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if args[:1] == ["--contato"]:
        return contato(args[1])
    if args[:1] == ["--medir"]:
        return medir()
    nomes = args or [*af.FOLHAS_CK, *((f"fx_{n}" for n in EFEITOS) if HD == 1 else ())]
    for nome in nomes:
        if nome.startswith("fx_"):
            efeito(nome.removeprefix("fx_"))
        else:
            corpo(nome)


if __name__ == "__main__":
    main()
