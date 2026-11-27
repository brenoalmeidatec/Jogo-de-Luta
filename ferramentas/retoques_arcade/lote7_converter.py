"""Lote 7 (2026-11-11): as folhas do Pengaró Endiabrado (boss final) viram quadros_arcade/e_<golpe>/00..07.png e as
três camadas da aura viram sprites/pengaro/efeitos/aura_<camada>/00..07.png.

  python ferramentas/retoques_arcade/lote7_converter.py --medir      altura crua de cada figura, boss x normal
  python ferramentas/retoques_arcade/lote7_converter.py [folha ...]  converte (padrão: todas as e_*.png)
  python ferramentas/retoques_arcade/lote7_converter.py --aura       recorta as fx_aura_*

Corpo: tela 360x260, tronco em x=180, base em y=219, paleta paleta_arcade_endiabrado.json (15 cores), só os 8
desenhos (sem quadro do meio). A escala é a da folha normal (0,40 numa folha de 2172 px, vezes o fator que a normal
usou no lote6_converter.py) vezes a correção de FATOR, para as folhas em que o ChatGPT desenhou o boss maior ou menor
que a normal. O boss é mais alto que o normal só pelo cabelo e pelos chifres (~28 px na folha); o corpo tem o mesmo
tamanho. Quem põe cada desenho em cima do desenho normal no jogo (pés e tronco) é o gerar_pengaro.py.
e_despertar começa com o Pengaró normal e termina no boss: usa as duas paletas juntas (30 cores).
Aura: recorte do verde como efeito (regra de efeitos_folha.py), sem paleta de corpo e sem quadro de fluxo; as oito
células ficam na mesma tela, na escala do corpo (0,40), com a base de cada camada no mesmo lugar em todos os quadros.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("FORMA", "endiabrado")
RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "ferramentas"))
import numpy as np, cv2  # noqa: E402
import animar_folha as af  # noqa: E402
import quantizar_folha as qf  # noqa: E402
import efeitos_folha as ef  # noqa: E402
from PIL import Image  # noqa: E402

LARG, ALT, EIXO, CHAO = 360, 260, 180, 220
CABELO = 28  # px de folha que o cabelo comprido e os chifres somam à altura do normal
# fator que a folha NORMAL usou (lote6_converter.py); o boss foi desenhado em cima da folha normal crua
NORMAL = {"golaco": 0.917, "agachado": 0.85,  # agarrao (1.03 na normal) não: o boss já veio com 306 px em pé
          "queda": (1.30, 1.30, 1.295, 1.25, 1.20, 1.20, 1.20, 1.20)}  # medido nos quadros_arcade/queda (queda_escala.py)
# correção por folha (ou por desenho), medida com --medir e conferida no olho
# (boss em pé na folha: ~306-313 px com cabelo; fora disso a folha ganha fator)
FATOR = {"soco": 1.03, "provoca": 1.04, "vitoria": 1.07, "compasso": 1.05, "caneta": 1.10, "levanta": 1.05,
         "pulo": 0.93, "despertar": 0.97}
FOLHAS = sorted(f.stem[2:] for f in qf.ENTRADA.glob("e_*.png") if f.stem != "e_conceito")


def sem_franja(a):
    """Tira a franja rosa que sobra do fundo magenta na borda da figura (até 2 px)."""
    a = a.copy()
    for _ in range(2):
        r, g, b, al = (a[..., i].astype(int) for i in range(4))
        cheio = al > 0
        borda = cheio & ~cv2.erode(cheio.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        rosa = (r > 120) & (b > 120) & (g < .6 * np.minimum(r, b)) & (np.abs(r - b) < 60)
        a[borda & rosa] = 0
    return a


def colunas(alfa):
    """Trechos de colunas ocupadas com mais de 20 px (uma figura cada)."""
    grupos, ini = [], None
    for x, c in enumerate(list(alfa.any(axis=0)) + [False]):
        if c and ini is None:
            ini = x
        elif not c and ini is not None:
            grupos.append((ini, x))
            ini = None
    return [g for g in grupos if g[1] - g[0] > 20]


def figuras(img):
    """As 8 figuras da folha, pelas colunas vazias entre elas: [(recorte RGBA, caixa na folha)]."""
    limpa = sem_franja(np.array(af.tira_fundo(img)))
    grupos = colunas(limpa[..., 3] > 0)
    assert len(grupos) == 8, f"{len(grupos)} figuras"
    out = []
    for x0, x1 in grupos:
        fig = Image.fromarray(limpa[:, x0:x1])
        cx = fig.getchannel("A").getbbox()
        out.append((fig.crop(cx), (x0 + cx[0], cx[1], x0 + cx[2], cx[3])))
    return out


def alturas_normal(img):
    """Altura de cada figura da folha normal, por peça ligada (como o lote6_converter.py separa)."""
    n = np.array(af.tira_fundo(img))
    larg = n.shape[1] / 8
    num, _, st, cen = cv2.connectedComponentsWithStats((n[..., 3] > 0).astype(np.uint8), connectivity=8)
    hn = []
    for i in range(8):
        ys = [(st[j, 1], st[j, 1] + st[j, 3]) for j in range(1, num)
              if st[j, 4] >= 40 and min(7, int(cen[j][0] // larg)) == i]
        hn.append(max(b for _, b in ys) - min(a for a, _ in ys) if ys else 0)
    return hn


def paleta_do_despertar():
    dados, _ = qf.ler_paleta()
    normal = json.loads((qf.SPRITES / "paleta_arcade.json").read_text(encoding="utf-8"))
    juntos = {"contorno_grupo": {**normal["contorno_grupo"], **dados["contorno_grupo"]},
              "cores": normal["cores"] + dados["cores"]}
    return juntos, np.array([c["rgb"] for c in juntos["cores"]], np.uint8)


def medir():
    for nome in FOLHAS:
        eimg = Image.open(qf.ENTRADA / f"e_{nome}.png")
        he = [round(q.height * 2172 / eimg.width) for q, _ in figuras(eimg)]
        arq = qf.ENTRADA / f"{nome}.png"
        if not arq.exists():
            print(f"{nome:13s} boss   {he} (sem folha normal)")
            continue
        img = Image.open(arq)
        hn = [round(h * 2172 / img.width) for h in alturas_normal(img)]
        r = [round((a + CABELO) / b, 2) if a and b else 0 for a, b in zip(hn, he)]
        print(f"{nome:13s} normal {hn}")
        print(f"{'':13s} boss   {he}")
        print(f"{'':13s} razao  {r} mediana {np.median(r):.3f}")


# Desenhos em que o ChatGPT acendeu a pele do tronco e dos braços inteira de violeta (o clarão do golpe pintado no
# corpo). A pele do boss não muda de cor: na faixa do tronco (dos ombros à corda) o violeta volta para a rampa da pele.
PELE_ACESA = {"soco": (4, 5, 6)}
VIOLETA_PARA_PELE = {"violeta_brilho": "pele_luz", "violeta_claro": "pele_luz", "violeta_medio": "pele_medio",
                     "violeta_sombra": "pele_sombra"}


def pele_apagada(idx, dados):
    ids = [c["id"] for c in dados["cores"]]
    ys = np.flatnonzero((idx >= 0).any(axis=1))
    topo, alt = ys[0], ys[-1] - ys[0]
    faixa = slice(topo + round(alt * .20), topo + round(alt * .50))
    for de, para in VIOLETA_PARA_PELE.items():
        idx[faixa][idx[faixa] == ids.index(de)] = ids.index(para)


def converter(nomes):
    dados, pal = qf.ler_paleta()
    d2, p2 = paleta_do_despertar()
    for nome in nomes:
        img = Image.open(qf.ENTRADA / f"e_{nome}.png")
        fat = FATOR.get(nome, 1.0)
        fat = list(fat) if isinstance(fat, (tuple, list)) else [fat] * 8
        base = af.ESCALA_2172 * 2172 / img.width
        nor = NORMAL.get(nome, 1.0)
        fat = [a * b for a, b in zip(fat, nor if isinstance(nor, tuple) else [nor] * 8)]
        d = qf.SAIDA / f"e_{nome}"
        d.mkdir(parents=True, exist_ok=True)
        info = []
        for i, (q, cx) in enumerate(figuras(img)):
            f = base * fat[i]
            g = q.resize((max(1, round(q.width * f)), max(1, round(q.height * f))), Image.LANCZOS)
            tela = Image.new("RGBA", (LARG, ALT))
            tela.paste(g, (EIXO - round(af.tronco(q) * f), CHAO - g.height), g)
            # e_despertar: até o 4 ainda é o Pengaró (pele e calça dele); do 5 em diante já é o boss, na paleta do boss
            # (com as duas paletas a pele do boss em pé saía laranja e trocava de cor ao entrar na ginga)
            dd, pp = (d2, p2) if nome == "despertar" and i < 5 else (dados, pal)
            idx = qf.quantizar(tela, dd, pp)
            if i in PELE_ACESA.get(nome, ()):
                pele_apagada(idx, dd)
            qf.para_imagem(idx, pp).save(d / f"{i:02d}.png")
            info.append(g.height)
        print(f"e_{nome}: alturas no jogo {info}")


AURA = ("coluna", "anel", "detritos")


ESPALHA = 2.0  # os detritos vieram todos em cima do corpo (191 px de largura na folha): cada peça vai para fora


def espalhar(cel):
    """Afasta cada pedra e cada pedaço de corrente do eixo, sem mudar o tamanho da peça: a peça é o bloco que ela
    ocupa somando os 8 quadros (elas pairam no lugar), e o bloco inteiro anda (ESPALHA - 1) vezes a distância ao eixo."""
    h, w = cel[0].shape[:2]
    juntos = np.max([c[..., 3] for c in cel], axis=0) > 0
    n, rot, st, cen = cv2.connectedComponentsWithStats(cv2.dilate(juntos.astype(np.uint8), np.ones((5, 5), np.uint8)), 8)
    xs = np.nonzero(juntos)[1]
    eixo = (xs.min() + xs.max()) / 2
    margem = round((xs.max() - xs.min()) / 2 * (ESPALHA - 1)) + 4
    saida = []
    for c in cel:
        novo = np.zeros((h, w + 2 * margem, 4), np.uint8)
        for k in range(1, n):
            m = (rot == k) & (c[..., 3] > 0)
            if m.any():
                dx = margem + round((cen[k][0] - eixo) * (ESPALHA - 1))
                yy, xx = np.nonzero(m)
                novo[yy, xx + dx] = c[yy, xx]
        saida.append(novo)
    return saida


def aura():
    for nome in AURA:
        cel = ef.recortar(RAIZ / "sprites/pengaro/quadros/folhas" / f"fx_aura_{nome}.png")
        for c in cel:
            # verde que sobra dentro da fumaça e nos furos dos elos: o vivo vira transparente, o escuro perde o verde
            r, g, b = (c[..., i].astype(int) for i in range(3))
            verde = (g > r + 25) & (g > b + 25)
            c[verde & (g > 110), 3] = 0
            resto = (c[..., 3] > 0) & (g > r + 10)  # e o esverdeado que mistura com a fumaça fica azul-violeta
            c[..., 1][resto] = np.minimum(r, b)[resto]
        if nome == "detritos":
            cel = espalhar(cel)
        juntos = np.max([c[..., 3] for c in cel], axis=0)
        ys, xs = np.nonzero(juntos)
        f = af.ESCALA_2172
        pasta = RAIZ / "sprites/pengaro/efeitos" / f"aura_{nome}"
        pasta.mkdir(parents=True, exist_ok=True)
        for arq in pasta.glob("*.png"):
            arq.unlink()
        for i, c in enumerate(cel):
            if nome == "anel":  # o disco anda até 7 px dentro da célula: cada quadro centrado em si mesmo
                yy, xx = np.nonzero(c[..., 3])
                meia = (xs.max() - xs.min()) // 2 + 4
                meio = (xx.min() + xx.max() + 1) // 2
                caixa = (meio - meia, yy.max() + 1 - (ys.max() - ys.min()) - 6, meio + meia, yy.max() + 1)
            else:
                caixa = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 1)
            q = Image.fromarray(c).crop(caixa)
            q = q.resize((round(q.width * f), round(q.height * f)), Image.LANCZOS)
            a = np.array(q)
            a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
            a[a[..., 3] == 0] = 0
            Image.fromarray(a).save(pasta / f"{i:02d}.png")
        print(f"aura_{nome}: 8 quadros {q.size}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if args[:1] == ["--medir"]:
        medir()
    elif args[:1] == ["--aura"]:
        aura()
    else:
        converter(args or FOLHAS)
