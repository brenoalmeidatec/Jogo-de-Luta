#!/usr/bin/env python3
"""Hazak, arte arcade: converte sprites/hazaki/quadros/folhas_arcade/<folha>.png (8 quadros, fundo magenta, 2172x724)
em sprites/hazaki/quadros_arcade/<folha>/00..07.png (tela 360x260, pés em 180,220, 15 cores + transparente).

  python ferramentas/folhas_hazak_arcade.py                 converte todas as folhas e aplica os retoques
  python ferramentas/folhas_hazak_arcade.py soco chute      só essas
  python ferramentas/folhas_hazak_arcade.py --medir         imprime largura x altura de cada figura (na folha crua)
  python ferramentas/folhas_hazak_arcade.py --contato DIR   folhas de contato (2x, fundo cinza, linha do chão e eixo)

Arquivo próprio do Hazak: não mexe em animar_folha.py nem em quantizar_folha.py (só usa as funções de quantizar deles,
com a paleta do Hazak em sprites/hazaki/paleta_arcade.json). Uma escala só para todas as folhas (ESCALA, medida na
`parado`: figura em pé com 109 px); as exceções estão em FATOR. Os retoques de pixel (pulseira) ficam em
ferramentas/retoques_arcade/hazak_pulseira.py e rodam no fim da conversão de cada folha.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quantizar_folha as qf  # noqa: E402  (só quantizar/limpar/para_imagem; a paleta é a do Hazak)
from recortar_quadros import tira_fundo  # noqa: E402
from retoques_arcade import hazak_pulseira  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SPRITES = RAIZ / "sprites/hazaki"
ENTRADA = SPRITES / "quadros/folhas_arcade"
SAIDA = SPRITES / "quadros_arcade"
PALETA = SPRITES / "paleta_arcade.json"
LARG, ALT = 360, 260
EIXO, CHAO = 180, 220
ALTURA_EM_PE = 109  # ficha: ~109 px em pé (o Pengaró tem 110)
ESCALA = 109 / 344  # 0,3169: a figura em pé tem 344 px na folha crua (`parado` 0 e o 1º quadro de quase toda folha; ver --medir)

# 15 cores + transparente (docs/arcade/hazaki.md, seção (a)). O grupo diz qual contorno fecha a borda externa.
CORES = [
    ("roupa_contorno", "roupa", "#1c1832"),
    ("pele_contorno", "pele", "#7a2e26"),
    ("pele_sombra", "pele", "#b04f30"),
    ("pele_medio", "pele", "#de8448"),
    ("pele_luz", "pele", "#f6b468"),
    ("pele_brilho", "pele", "#fcd9a0"),
    ("gi_escuro", "roupa", "#2b2650"),
    ("gi_medio", "roupa", "#47436a"),
    ("gi_luz", "roupa", "#6c6e9c"),
    ("debrum_laranja", "debrum", "#d8661c"),
    ("debrum_sombra", "debrum", "#8e3a1a"),
    ("faixa_cabelo", "faixa", "#3a2a30"),
    ("atadura_branca", "atadura", "#f4f1ea"),
    ("atadura_sombra", "atadura", "#a9a6cc"),
    ("pulseira", "pulseira", "#2a9d9a"),
]
CONTORNO_GRUPO = {"pele": "pele_contorno", "roupa": "roupa_contorno", "debrum": "roupa_contorno",
                  "faixa": "roupa_contorno", "atadura": "roupa_contorno", "pulseira": "roupa_contorno"}

# A patroa (helper do Despertar) usa as cores do Hazak mais 4 próprias (hazak_gerador.md, seção 7); sem a pulseira.
CORES_PATROA = [c for c in CORES if c[0] != "pulseira"] + [
    ("patroa_cabelo", "patroa", "#5a3424"),
    ("patroa_mostarda", "patroa", "#e9a51f"),
    ("patroa_jeans", "patroa", "#3f6cae"),
    ("patroa_jeans_sombra", "patroa", "#2b4884"),
]
PALETA_PATROA = SPRITES / "paleta_arcade_patroa.json"

# Exceções à escala única: folha -> fator para as 8 figuras, ou lista de 8 fatores.
#  - corpo deitado/horizontal que a folha trouxe menor que o corpo em pé: ampliado até o comprimento do corpo em pé;
#  - objetos (vieram com o dobro do tamanho): reduzidos para o tamanho de um antebraço (~30 px);
#  - patroa: 92% da altura dele (330 px na folha crua -> 100 px).
FATOR = {
    "queda": [1.25, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3],
    "vitima_arremessado": 1.2,
    "voadora": [1, 1.12, 1.25, 1.25, 1.25, 1.25, 1.25, 1],
    "apanha": [1, 1, 1, 1, 1, 1.08, 1.1, 1.12],
    "derrota_sirene": [1.15, 1.1, 1, 1, 1, 1, 1, 1],
    "obj_lasca": 0.5,
    "obj_estatueta": 0.5,
    "patroa_parada": 0.92 * 344 / 330,
    "patroa_chega_sim": 0.92 * 344 / 330,
    "patroa_sai": 0.92 * 344 / 330,
}
CENTRADO = {"obj_lasca": "todos", "obj_estatueta": "todos"}  # centrados pela caixa, em vez do tronco


def escrever_paleta(patroa=False):
    lista = CORES_PATROA if patroa else CORES
    cores = [{"id": i, "grupo": g, "rgb": [int(h[k:k + 2], 16) for k in (1, 3, 5)]} for i, g, h in lista]
    nota = ("patroa (helper do Despertar): as cores do Hazak sem a pulseira, mais 4 próprias no fim."
            if patroa else "15 cores + transparente, forma normal.")
    dados = {"lutador": "hazaki", "fonte": "docs/arcade/hazaki.md (a)",
             "nota": nota + " Escrito por ferramentas/folhas_hazak_arcade.py.",
             "contorno_grupo": dict(CONTORNO_GRUPO, patroa="roupa_contorno"), "cores": cores}
    destino = PALETA_PATROA if patroa else PALETA
    destino.write_text(json.dumps(dados, indent=1, ensure_ascii=False) + chr(10), encoding="utf-8")
    return dados, np.array([c["rgb"] for c in cores], np.uint8)


def limpa_franja(a):
    """Tira o resto de magenta que sobra na borda da figura (rosa/roxo vivo que não existe no Hazak)."""
    a = a.copy()
    r, g, b = (a[..., i].astype(int) for i in range(3))
    rosa = (a[..., 3] > 0) & (r > 120) & (b > 110) & (g < 0.62 * np.minimum(r, b))
    a[rosa] = 0
    return a


def figuras(folha):
    """As 8 figuras da folha, recortadas (RGBA, sem fundo), na ordem. Cada pedaço vai para a célula onde está o centro
    dele; se alguma célula ficar vazia (duas figuras coladas), corta nas colunas de menor ocupação perto da divisa."""
    limpa = limpa_franja(np.array(tira_fundo(Image.open(folha))))
    cheio = limpa[..., 3] > 0
    largura = limpa.shape[1] / 8
    n, rot, dados, centros = cv2.connectedComponentsWithStats(cheio.astype(np.uint8), connectivity=8)
    celula = np.full(n, -1)
    for i in range(1, n):
        if dados[i, cv2.CC_STAT_AREA] >= 12:
            celula[i] = min(7, int(centros[i][0] // largura))
    areas = dados[:, cv2.CC_STAT_AREA]
    grandes = [int(areas[celula == k].max(initial=0)) for k in range(8)]
    colado = min(grandes) < 0.25 * max(grandes)
    cortes = None
    if colado:
        ocupa = cheio.sum(axis=0)
        cortes = [0]
        for k in range(1, 8):
            ini, fim = int(k * largura - largura * .3), int(k * largura + largura * .3)
            cortes.append(ini + int(np.argmin(ocupa[ini:fim])))
        cortes.append(limpa.shape[1])
    saida = []
    for k in range(8):
        if cortes:
            m = np.zeros(cheio.shape, bool)
            m[:, cortes[k]:cortes[k + 1]] = True
        else:
            m = celula[rot] == k
        fig = Image.fromarray(np.where(m[..., None], limpa, 0).astype(np.uint8))
        caixa = fig.getchannel("A").getbbox()
        saida.append(fig.crop(caixa) if caixa else None)
    return saida, colado


def tronco(q):
    """Centro do tronco: em cada linha entre 30% e 60% da altura, o meio do maior trecho cheio (igual ao do Pengaró)."""
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


def fatores(nome):
    f = FATOR.get(nome, 1.0)
    return list(f) if isinstance(f, (list, tuple)) else [f] * 8


def converter(nome, dados, pal):
    figs, _ = figuras(ENTRADA / f"{nome}.png")
    destino = SAIDA / nome
    destino.mkdir(parents=True, exist_ok=True)
    centrados = CENTRADO.get(nome, ())
    for i, (q, f) in enumerate(zip(figs, fatores(nome))):
        tela = Image.new("RGBA", (LARG, ALT))
        if q is not None:
            e = ESCALA * f
            g = q.resize((max(1, round(q.width * e)), max(1, round(q.height * e))), Image.LANCZOS)
            deitado = centrados == "todos" or i in centrados or g.width > 1.45 * g.height
            centro = g.width // 2 if deitado else round(tronco(q) * e)
            tela.paste(g, (EIXO - centro, CHAO - g.height), g)
        qf.para_imagem(qf.quantizar(tela, dados, pal), pal).save(destino / f"{i:02d}.png")
    faltam = hazak_pulseira.aplicar(nome, destino)
    return f"{len(figs)} desenhos" + (f"; pulseira escondida ou faltando em {faltam}" if faltam else "")


def contato(pasta_saida, nomes):
    """Uma folha de contato por pasta: os 8 desenhos a 2x sobre cinza, com a linha do chão, a dos 109 px e o eixo."""
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    x0, x1, y0, y1 = 80, 280, 70, 232  # recorte da tela que aparece (200x162)
    for nome in nomes:
        arquivos = sorted((SAIDA / nome).glob("[0-9][0-9].png"))
        folha = Image.new("RGB", ((x1 - x0) * len(arquivos), y1 - y0), (120, 124, 120))
        for i, f in enumerate(arquivos):
            q = Image.open(f).convert("RGBA")
            cx = (x1 - x0) * i
            for y in range(y1 - y0):
                folha.putpixel((cx + EIXO - x0, y), (100, 104, 100))
            for x in range(x1 - x0):
                folha.putpixel((cx + x, CHAO - y0), (90, 150, 90))
                folha.putpixel((cx + x, CHAO - ALTURA_EM_PE - y0), (150, 120, 120))
            c = q.crop((x0, y0, x1, y1))
            folha.paste(c, (cx, 0), c)
        folha = folha.resize((folha.width * 2, folha.height * 2), Image.NEAREST)
        folha.save(pasta_saida / f"{nome}.png")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    todas = sorted(p.stem for p in ENTRADA.glob("*.png"))
    pedidas = [a for a in args if not a.startswith("--") and a in todas]
    nomes = pedidas or todas
    if "--medir" in args:
        for nome in nomes:
            figs, colado = figuras(ENTRADA / f"{nome}.png")
            print(f"{nome:22s}", " ".join(f"{q.width:3d}x{q.height:3d}" if q else "  vazio" for q in figs),
                  "COLADO" if colado else "")
        return
    if "--contato" in args:
        prontas = sorted(p.name for p in SAIDA.iterdir() if p.is_dir() and (not pedidas or p.name in pedidas))
        contato(args[args.index("--contato") + 1], prontas)
        return
    normal, patroa = escrever_paleta(), escrever_paleta(patroa=True)
    for nome in nomes:
        print(f"{nome}: {converter(nome, *(patroa if nome.startswith('patroa_') else normal))}")


if __name__ == "__main__":
    main()
