#!/usr/bin/env python3
"""Arte arcade: recorta uma folha de 8 quadros, põe na escala do jogo e quantiza SEM dithering para a paleta fixa do
lutador (15 cores + transparente), com contorno colorido de 1 px. Estilo e regras: tabela do estilo arcade (regras 1-7).

  python ferramentas/quantizar_folha.py soco                  folhas_arcade/soco.png -> quadros_arcade/soco/00..07.png
  python ferramentas/quantizar_folha.py soco --meio           re-quantiza quadros_arcade/soco/meio/*.png (depois do Blender)
  python ferramentas/quantizar_folha.py --montar-paleta soco  mede a folha e escreve sprites/<lutador>/paleta_arcade.json

LUTADOR=<nome> escolhe o lutador, como no animar_folha.py. A saída tem a mesma tela (360x260, pés em 180,220) e a mesma
estrutura de quadros/<nome>/ (00..07.png e meio/II_K.png), numa pasta paralela quadros_arcade/<nome>/: o jogo não muda.
Depois: python ferramentas/animar_folha.py --arcade soco (quadros do meio pelo Blender), quantizar --meio, e
python ferramentas/conferir_arte.py soco.

A paleta é um arquivo de dados (paleta_arcade.json): cada cor tem um papel (pele, calça, faixa, cabelo, garrafa) e cada
papel diz qual contorno usa. --montar-paleta mede a mediana dos pixels de cada papel na folha e corrige o matiz para a
faixa da regra (rampa da pele, sombra fria da calça, contorno sem preto); o arquivo pode ser retocado à mão depois.
"""
import colorsys
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import animar_folha as af  # noqa: E402

LUTADOR = af.LUTADOR
SPRITES = af.RAIZ / "sprites" / LUTADOR
ENTRADA = SPRITES / "quadros/folhas_arcade"
SAIDA = SPRITES / "quadros_arcade"
# FORMA=endiabrado: outra forma do mesmo lutador, com paleta e papéis próprios (paleta_arcade_endiabrado.json). As
# folhas dela são as e_<golpe>.png da mesma pasta. Sem FORMA nada muda.
FORMA = os.environ.get("FORMA", "")
PALETA = SPRITES / (f"paleta_arcade_{FORMA}.json" if FORMA else "paleta_arcade.json")
MINIMO = 20  # nenhum canal abaixo disso (regra 5: nada de preto puro)

# Papéis do Pengaró: janela HSV (matiz em graus, s e v de 0 a 1) para medir a cor na folha, e a faixa de matiz da regra
# para onde a cor medida é puxada. "contorno" diz qual cor fecha a borda externa de cada grupo.
PAPEIS_PENGARO = {
    "contorno_grupo": {"pele": "pele_contorno", "garrafa": "pele_contorno", "cabelo": "pele_contorno",
                       "calca": "calca_contorno", "faixa": "calca_contorno"},
    "cores": [
        # id, grupo, janela (h0, h1, s0, s1, v0, v1), matiz alvo (h0, h1) ou None, ajuste extra
        ("pele_contorno", "pele", (340, 12, .55, 1, .18, .34), (345, 360), {"v": .30}),
        ("pele_sombra", "pele", (5, 16, .65, 1, .40, .66), (5, 15), {}),
        ("pele_medio", "pele", (14, 24, .55, .85, .72, .96), (21, 26), {}),
        ("pele_luz", "pele", (22, 34, .40, .66, .94, 1), (30, 40), {}),
        ("pele_brilho", "pele", (28, 45, .10, .30, .95, 1), (30, 40), {}),
        ("calca_contorno", "calca", (240, 290, .40, 1, .25, .45), (245, 265), {"v": .36}),
        ("calca_sombra", "calca", (220, 330, .12, .40, .50, .82), (230, 255), {"s": .22, "v": .74}),
        ("calca_branco", "calca", (0, 360, 0, .12, .93, 1), None, {}),
        ("faixa_escuro", "faixa", (150, 178, .60, 1, .22, .40), None, {}),
        ("faixa_verde", "faixa", (140, 170, .60, 1, .45, .78), None, {}),
        ("faixa_amarelo", "faixa", (40, 55, .80, 1, .85, 1), None, {}),
        ("cabelo_escuro", "cabelo", (20, 70, .15, .45, .10, .24), None, {}),
        ("cabelo_luz", "cabelo", (30, 60, .25, .45, .36, .62), None, {}),
        ("garrafa_escuro", "garrafa", (0, 12, .80, 1, .28, .44), (8, 14), {}),
        ("garrafa_ambar", "garrafa", (24, 40, .80, 1, .75, .96), None, {}),
    ],
}
# Pengaró Endiabrado (boss final, conceito e_conceito.png): pele marrom-arroxeada, casaco e calça pretos, violeta da
# sombra (forro, rachaduras, brasa, pontas do cabelo, chifres), ferro das algemas e ouro (friso, braceletes, corda).
# O preto do casaco fecha o contorno de tudo que não é pele; o cabelo usa o preto e o ferro escuro.
PAPEIS_PENGARO_ENDIABRADO = {
    "contorno_grupo": {"pele": "pele_contorno", "casaco": "casaco_contorno", "violeta": "casaco_contorno",
                       "ferro": "casaco_contorno", "ouro": "casaco_contorno"},
    "cores": [
        ("casaco_contorno", "casaco", (0, 360, 0, 1, 0, .13), None, {"v": .12}),
        ("pele_contorno", "pele", (320, 352, .45, 1, .17, .30), None, {}),
        ("pele_sombra", "pele", (335, 360, .50, 1, .34, .52), None, {}),
        ("pele_medio", "pele", (335, 360, .45, .80, .54, .70), None, {}),
        ("pele_luz", "pele", (340, 5, .35, .70, .72, .90), None, {}),
        ("violeta_fundo", "violeta", (270, 300, .60, 1, .14, .27), None, {}),
        ("violeta_sombra", "violeta", (270, 300, .60, 1, .30, .48), None, {}),
        ("violeta_medio", "violeta", (270, 300, .60, 1, .52, .72), None, {}),
        ("violeta_claro", "violeta", (280, 310, .40, .85, .75, .95), None, {}),
        ("violeta_brilho", "violeta", (0, 360, 0, .25, .82, 1), None, {}),
        ("ferro_escuro", "ferro", (270, 320, .20, .50, .22, .36), None, {}),
        ("ferro_claro", "ferro", (260, 320, .12, .38, .42, .66), None, {}),
        ("ouro_escuro", "ouro", (12, 28, .65, 1, .48, .72), None, {}),
        ("ouro_medio", "ouro", (28, 42, .65, 1, .82, 1), None, {}),
        ("ouro_claro", "ouro", (44, 58, .35, .75, .92, 1), None, {}),
    ],
}
# CK, forma base (polo branca, short preto e branco, boné, luva vermelha). A pele dele é mais escura que a do Pengaró:
# rampa sombra 2-10°, médio 11-19°, luz 20-30° (as mesmas faixas estão em conferir_arte.py). O vermelho escuro da luva
# cai nas sombras da pele (mesmo vinho), por isso a luva só tem a cor viva. "branco_sombra" é a sombra fria da regra 4.
PAPEIS_CK = {
    "contorno_grupo": {"pele": "pele_contorno", "luva": "pele_contorno", "roupa": "roupa_contorno",
                       "verde": "roupa_contorno"},
    "cores": [
        ("pele_contorno", "pele", (318, 352, .60, 1, .25, .48), (335, 350), {"v": .34}),
        ("pele_sombra", "pele", (354, 7, .62, .82, .48, .69), (2, 10), {}),
        ("pele_medio", "pele", (7, 15, .62, .82, .70, .87), (11, 19), {}),
        ("pele_luz", "pele", (12, 20, .55, .78, .88, 1), (20, 30), {}),
        ("luva_vermelho", "luva", (358, 7, .74, 1, .87, 1), None, {}),
        ("roupa_contorno", "roupa", (266, 284, .60, .88, .24, .33), (250, 275), {"v": .32}),
        ("roupa_preto", "roupa", (262, 282, .80, 1, .12, .26), None, {}),
        ("roupa_roxo", "roupa", (268, 288, .38, .62, .33, .47), None, {}),
        ("roupa_lilas_escuro", "roupa", (280, 296, .14, .36, .44, .63), None, {}),
        ("roupa_lilas", "roupa", (280, 312, .05, .19, .62, .79), None, {}),
        ("branco_sombra", "roupa", (262, 280, .28, .52, .72, .88), (240, 268), {}),
        ("branco_meio", "roupa", (270, 295, .09, .27, .84, .92), None, {}),
        ("branco", "roupa", (0, 360, 0, .08, .95, 1), None, {}),
        ("verde", "verde", (120, 145, .45, 1, .35, .62), None, {}),
        ("verde_luz", "verde", (135, 170, .14, .34, .52, .70), None, {}),
    ],
}
# CK, Modo Ratão (cabelo platinado, camisa e bermuda azul-marinho e branco, regata, cordão de ouro, caco de garrafa).
PAPEIS_CK_RATAO = {
    "contorno_grupo": {"pele": "pele_contorno", "ouro": "pele_contorno", "roupa": "roupa_contorno",
                       "garrafa": "roupa_contorno"},
    "cores": [
        ("pele_contorno", "pele", (318, 352, .60, 1, .22, .50), (335, 350), {"v": .34}),
        ("pele_sombra", "pele", (352, 7, .58, .82, .50, .68), (2, 10), {}),
        ("pele_medio", "pele", (8, 20, .62, .82, .70, .92), (11, 19), {}),
        ("pele_luz", "pele", (20, 28, .55, .80, .93, 1), (20, 30), {}),
        ("ouro", "ouro", (34, 52, .55, 1, .80, 1), None, {}),
        ("roupa_contorno", "roupa", (258, 270, .85, 1, .14, .27), (250, 275), {"v": .26}),
        ("roupa_marinho", "roupa", (266, 279, .66, .90, .27, .42), None, {}),
        ("roupa_roxo", "roupa", (273, 284, .44, .72, .42, .53), None, {}),
        ("roupa_lilas_escuro", "roupa", (279, 292, .22, .44, .52, .64), None, {}),
        ("roupa_lilas", "roupa", (290, 325, .07, .20, .60, .84), None, {}),
        ("branco_sombra", "roupa", (278, 288, .28, .42, .72, .84), (240, 268), {}),
        ("branco_meio", "roupa", (280, 330, .07, .30, .88, .96), None, {}),
        ("branco", "roupa", (0, 360, 0, .09, .95, 1), None, {}),
        ("garrafa_escuro", "garrafa", (65, 100, .30, .60, .25, .42), None, {}),
        ("garrafa_verde", "garrafa", (70, 100, .45, .80, .48, .70), None, {}),
    ],
}
PAPEIS = {"pengaro": PAPEIS_PENGARO, "pengaro_endiabrado": PAPEIS_PENGARO_ENDIABRADO, "ck": PAPEIS_CK,
          "ck_ratao": PAPEIS_CK_RATAO}


def hsv(rgb):
    """rgb (N,3) 0-255 -> h em graus, s, v."""
    h, s, v = np.vectorize(colorsys.rgb_to_hsv)(*(rgb.T / 255))
    return h * 360, s, v


def na_janela(h, s, v, j):
    h0, h1, s0, s1, v0, v1 = j
    no_h = (h >= h0) & (h <= h1) if h0 <= h1 else (h >= h0) | (h <= h1)  # janela que passa do 360
    return no_h & (s >= s0) & (s <= s1) & (v >= v0) & (v <= v1)


def para_faixa(h, faixa):
    """Matiz fora da faixa vai para o meio dela (a rampa fica com a cara da regra, não na beirada)."""
    if faixa is None:
        return h
    h0, h1 = faixa
    dentro = h0 <= h <= h1 if h0 <= h1 else (h >= h0 or h <= h1)
    return h if dentro else ((h0 + h1) / 2) % 360


def pixels(quadros):
    a = np.concatenate([np.asarray(q).reshape(-1, 4) for q in quadros])
    return a[a[:, 3] >= 128][:, :3]


def montar_paleta(nome):
    papeis = PAPEIS[f"{LUTADOR}_{FORMA}" if FORMA else LUTADOR]
    px = pixels(af.poses(ENTRADA / f"{nome}.png", "pes", 1)).astype(float)
    h, s, v = hsv(px)
    cores = []
    for ident, grupo, janela, faixa, ajuste in papeis["cores"]:
        m = na_janela(h, s, v, janela)
        if m.sum() < 20:
            raise SystemExit(f"{ident}: só {m.sum()} pixels na janela {janela}; ajuste PAPEIS")
        medido = np.median(px[m], axis=0)
        hh, ss, vv = colorsys.rgb_to_hsv(*(medido / 255))
        hh = para_faixa(hh * 360, faixa) / 360
        ss = max(ss, ajuste.get("s", 0))
        vv = ajuste.get("v", vv)
        rgb = np.round(np.array(colorsys.hsv_to_rgb(hh, ss, vv)) * 255)
        rgb = np.maximum(rgb, MINIMO).astype(int)
        cores.append({"id": ident, "grupo": grupo, "rgb": rgb.tolist(), "medido": medido.round().astype(int).tolist(),
                      "pixels": int(m.sum()), "matiz_alvo": faixa})
    rgbs = {tuple(c["rgb"]) for c in cores}
    assert len(rgbs) == len(cores) == 15, f"paleta com {len(rgbs)} cores distintas"
    dados = {"lutador": LUTADOR, **({"forma": FORMA} if FORMA else {}), "fonte": f"quadros/folhas_arcade/{nome}.png",
             "nota": "15 cores + transparente. rgb é o que vale; medido é a mediana do papel na folha, antes do ajuste "
                     "de matiz. Retoque à mão se precisar e rode conferir_arte.py.",
             "contorno_grupo": papeis["contorno_grupo"], "cores": cores}
    PALETA.write_text(json.dumps(dados, indent=1, ensure_ascii=False), encoding="utf-8")
    for c in cores:
        print(f"{c['id']:15s} {c['medido']} -> {c['rgb']}  ({c['pixels']} px)")
    print(f"paleta em {PALETA}")


def ler_paleta():
    dados = json.loads(PALETA.read_text(encoding="utf-8"))
    return dados, np.array([c["rgb"] for c in dados["cores"]], np.uint8)


def lab(rgb):
    return cv2.cvtColor(np.asarray(rgb, np.uint8).reshape(-1, 1, 3), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(float)


def vizinhos4(idx):
    """Os 4 vizinhos de cada pixel (-1 fora da tela)."""
    p = np.pad(idx, 1, constant_values=-1)
    return np.stack([p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]])


def quantizar(img, dados, pal):
    """RGBA -> índice na paleta (-1 transparente), sem dithering: cada pixel vai para a cor mais próxima em Lab."""
    a = np.asarray(img.convert("RGBA"))
    opaco = a[..., 3] >= 128
    alvo = lab(pal)
    cor = lab(a[..., :3].reshape(-1, 3))
    dist = ((cor[:, None, :] - alvo[None]) ** 2).sum(-1)
    idx = np.where(opaco, dist.argmin(1).reshape(opaco.shape), -1)
    return limpar(idx, dados)


def limpar(idx, dados):
    """Tira o chiado (pixel diferente dos 4 vizinhos vira a cor mais comum entre eles) e fecha a borda externa com o
    contorno de 1 px do grupo de cada pixel: vinho na pele, azul-roxo na roupa."""
    ids = [c["id"] for c in dados["cores"]]
    grupo = [c["grupo"] for c in dados["cores"]]
    contorno = {g: ids.index(c) for g, c in dados["contorno_grupo"].items()}
    contornos = set(contorno.values())
    tirar_chiado(idx, False)
    borda = (idx >= 0) & (vizinhos4(idx) == -1).any(0)
    for y, x in zip(*np.nonzero(borda)):
        if idx[y, x] not in contornos:
            idx[y, x] = contorno[grupo[idx[y, x]]]
    # 1 px: o anel logo atrás da borda não repete o contorno (o traço escuro do desenho vira 2-3 px na escala do jogo)
    viz = vizinhos4(idx)
    anel = (idx >= 0) & ~borda & np.isin(idx, list(contornos)) & np.isin(vizinhos4(np.where(borda, -9, idx)), -9).any(0)
    for y, x in zip(*np.nonzero(anel)):
        v = viz[:, y, x]
        v = v[(v >= 0) & ~np.isin(v, list(contornos))]
        if len(v):
            valores, n = np.unique(v, return_counts=True)
            idx[y, x] = valores[n.argmax()]
    tirar_chiado(idx, True)  # o contorno cria pixel solto do lado de dentro
    return idx


def soltos(idx, so_dentro=True):
    """Pixel diferente dos 4 vizinhos. so_dentro: fora da borda externa (o degrau do contorno de 1 px na diagonal é
    sempre diferente dos 4 vizinhos e não é chiado)."""
    viz = vizinhos4(idx)
    solto = (idx >= 0) & (viz != idx).all(0)
    return solto & ~(viz == -1).any(0) if so_dentro else solto


def tirar_chiado(idx, so_dentro):
    """Cada pixel solto vira a cor mais comum entre os 4 vizinhos opacos; repete até parar (no máximo 4 voltas)."""
    for _ in range(4):
        alvo = soltos(idx, so_dentro)
        if not alvo.any():
            return
        viz = vizinhos4(idx)
        for y, x in zip(*np.nonzero(alvo)):
            v = viz[:, y, x]
            v = v[v >= 0]
            if len(v):
                valores, n = np.unique(v, return_counts=True)
                idx[y, x] = valores[n.argmax()]


def para_imagem(idx, pal):
    a = np.zeros(idx.shape + (4,), np.uint8)
    a[idx >= 0, :3] = pal[idx[idx >= 0]]
    a[idx >= 0, 3] = 255
    return Image.fromarray(a, "RGBA")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--montar-paleta":
        montar_paleta(args[1])
        return
    meio = "--meio" in args
    nomes = [a for a in args if not a.startswith("--")]
    dados, pal = ler_paleta()
    for nome in nomes:
        destino = SAIDA / nome
        if meio:
            arquivos = sorted((destino / "meio").glob("*.png"))
            for f in arquivos:
                para_imagem(quantizar(Image.open(f), dados, pal), pal).save(f)
            print(f"{nome}: {len(arquivos)} quadros do meio re-quantizados")
            continue
        quadros = af.poses(ENTRADA / f"{nome}.png", af.FOLHAS_LUTADOR.get(nome, ("pes",))[0], 1)
        destino.mkdir(parents=True, exist_ok=True)
        for i, q in enumerate(quadros):
            para_imagem(quantizar(q, dados, pal), pal).save(destino / f"{i:02d}.png")
        print(f"{nome}: {len(quadros)} desenhos em {destino}")


if __name__ == "__main__":
    main()
