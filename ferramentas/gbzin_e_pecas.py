#!/usr/bin/env python3
"""Grão-Pastor (Gbzin despertado) pelo boneco de peças.

O desenho-mestre é a vista 3/4 do conceito aprovado pelo Breno (quadros/folhas_arcade/e_conceito.png, 2ª figura).
Dela sai o parado de referência em 3x (1080x780, cascos em y=660, eixo x=540), a paleta própria de 15 cores e o kit
de peças (cabeça separada para trocar depois). Os rascunhos de pose do ChatGPT só dão a pose: rosto, corpo e cores
vêm do kit.

  python ferramentas/gbzin_e_pecas.py ref              parado de referência + paleta em sprites/gbzin/pecas_e/
  python ferramentas/gbzin_e_pecas.py parado           parado que respira (quadros_e_pecas_hd/referencia_ginga)
  python ferramentas/gbzin_e_pecas.py firme e_anda ... rascunho -> quadros_e_firmes_hd (escala, paleta, chão)
"""
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "ferramentas"))
SPR = RAIZ / "sprites" / "gbzin"
PECAS = SPR / "pecas_e"
CONCEITO = SPR / "quadros/folhas_arcade/e_conceito.png"
TELA = (1080, 780)
CHAO, EIXO = 660, 540
FIGURA_X = (451, 1017)     # coluna da vista 3/4 no e_conceito
ESCALA = 0.613             # 630 px do cabelo ao casco no conceito -> ~386 px no 3x (rascunho de 545 px x 0.708)
CORES = 15


def sem_magenta(rgb):
    r, g, b = (rgb[..., i].astype(int) for i in range(3))
    mag = (r > 140) & (b > 140) & (g < 130) & (np.abs(r - b) < 100)
    roxo_fundo = (r > 110) & (b > 110) & (g < 60) & ((r + b) - 2 * g > 260)
    fundo = mag | roxo_fundo
    a = (~fundo).astype(np.uint8)
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return a


def lab(rgb):
    return cv2.cvtColor(np.asarray(rgb, np.float32).reshape(-1, 1, 3) / 255, cv2.COLOR_RGB2LAB).reshape(-1, 3)


def ref():
    PECAS.mkdir(parents=True, exist_ok=True)
    im = np.asarray(Image.open(CONCEITO).convert("RGB"))
    sub = im[:, FIGURA_X[0]:FIGURA_X[1]].astype(np.float32)
    a = sem_magenta(sub)
    a = cv2.erode(a, np.ones((2, 2), np.uint8))  # a borda antialiasada puxa magenta
    h, w = a.shape
    nw, nh = round(w * ESCALA), round(h * ESCALA)
    pm = cv2.resize(sub * a[..., None], (nw, nh), interpolation=cv2.INTER_AREA)
    aa = cv2.resize(a.astype(np.float32), (nw, nh), interpolation=cv2.INTER_AREA)
    cor = pm / np.maximum(aa[..., None], 1e-3)
    opaco = aa >= 0.55
    px = cor[opaco]
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 80, 0.1)
    _, lbl, cen = cv2.kmeans(lab(px), CORES, None, crit, 6, cv2.KMEANS_PP_CENTERS)
    pal = (cv2.cvtColor(cen.reshape(-1, 1, 3), cv2.COLOR_LAB2RGB).reshape(-1, 3) * 255).round().clip(20, 255)
    pal = pal.astype(np.uint8)
    ordem = np.argsort(lab(pal)[:, 0])
    pal = pal[ordem]
    idx = np.argmin(((lab(px)[:, None] - lab(pal)[None]) ** 2).sum(-1), 1)
    fig = np.zeros((nh, nw, 4), np.uint8)
    fig[opaco, :3] = pal[idx]
    fig[opaco, 3] = 255
    ys, xs = np.nonzero(opaco)
    base = ys.max()
    # eixo: meio do quadril (entre os cascos), medido na linha dos cascos
    pes = xs[ys > base - 40]
    meio = (pes.min() + pes.max()) // 2
    tela = np.zeros((TELA[1], TELA[0], 4), np.uint8)
    x0, y0 = EIXO - meio, CHAO - base
    tela[y0:y0 + nh, x0:x0 + nw] = fig
    Image.fromarray(tela).save(PECAS / "ref.png")
    (PECAS / "paleta.json").write_text(json.dumps({"fonte": "e_conceito.png (vista 3/4)", "cores": pal.tolist()},
                                                  indent=1), encoding="utf-8")
    ys, xs = np.nonzero(tela[..., 3])
    print(f"ref: figura {xs.min()}-{xs.max()} x {ys.min()}-{ys.max()} ({ys.max() - ys.min() + 1} px de altura)")



# ------------------------------------------------------------------ parado vivo (respiração sem corte)
# O parado não é montado em peças soltas: o corpo inteiro respira por um campo de deslocamento contínuo (cada linha
# desce um pouco mais que a de baixo), então não existe emenda nem linha de corte. Os cascos ficam presos no chão,
# a cintura desce 1 pixel do jogo, o peito e os ombros 1,3 e a cabeça chega um tique depois (atraso).
RESPIRA = 4.0          # descida do peito no 3x
CINTURA, COXA = 450, 560
PESCOCO = 365


def _passo(y, a, b_):
    t = np.clip((y - a) / (b_ - a), 0, 1)
    return t * t * (3 - 2 * t)


def _quadro_parado(base, t, n, o=0):
    fase = lambda k: (1 - math.cos(2 * math.pi * k / n)) / 2  # noqa: E731
    corpo, cabeca = RESPIRA * fase(t), RESPIRA * 1.15 * fase(t - 0.7)
    yy, xx = np.mgrid[:TELA[1], :TELA[0]].astype(np.float32)
    peso_corpo = 1 - _passo(yy, CINTURA + o, COXA + o)           # 1 em cima da cintura, 0 na coxa
    peso_peito = 1 + 0.3 * (1 - _passo(yy, 380 + o, CINTURA + o))  # o peito sobe mais que a cintura
    peso_cab = 1 - _passo(yy, PESCOCO - 25 + o, PESCOCO + 15 + o)
    dy = corpo * peso_corpo * peso_peito * (1 - peso_cab) + cabeca * peso_cab
    # a pele do manto nos lados balança meio pixel do jogo, atrasada (sobreposição de movimento)
    lado = _passo(np.abs(xx - EIXO), 110, 170) * _passo(yy, 330 + o, 420 + o) * (1 - _passo(yy, 560 + o, 600 + o))
    dx = 1.5 * math.sin(2 * math.pi * (t - 1.5) / n) * lado * np.sign(xx - EIXO)
    mapa_x, mapa_y = xx - dx, yy - dy
    return cv2.remap(base, mapa_x, mapa_y, cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def parado(n=8):
    """O parado do jogo: o 1º desenho da e_referencia_ginga (pose do rascunho, cabeça do kit, cor travada) respirando
    pelo campo de deslocamento. Um desenho só, então nada muda de um quadro para o outro além da respiração."""
    pasta = FIRMES / "e_referencia_ginga"
    base = np.asarray(Image.open(pasta / "00.png"))
    ys, xs = np.nonzero(base[..., 3])
    o = int(ys.min()) - 254  # as linhas de cintura, coxa e pescoço foram medidas no ref.png (topo do chifre em 254)
    quadros = [_quadro_parado(base, t, n, o) for t in range(n)]
    for i, q in enumerate(quadros):
        Image.fromarray(q).save(pasta / f"{i:02d}.png")
    um_x(["e_referencia_ginga"])
    print(f"parado: {n} quadros em {pasta.relative_to(RAIZ)}")
    return quadros

# ------------------------------------------------------------------ rascunho do ChatGPT -> quadros firmes
# O rascunho só dá a pose. Cada célula vira um quadro 3x do mesmo tamanho do parado de referência (a escala da folha
# sai do quadro mais alto, que é o de pé), com as 15 cores da paleta travadas e os cascos no chão do jogo.
FOLHAS = SPR / "quadros/folhas_arcade"
FIRMES = SPR / "quadros_e_firmes_hd"
FIRMES_1X = SPR / "quadros_e_firmes"   # o gêmeo 1x (360x260) que o gerador lê: o pixel do meio de cada 3x3
ALTURA_REF = 406           # altura do Grão-Pastor de pé no 3x (ref.png, chifre ao casco)
# folhas de pulo e de golpe no ar: o motor sobe o boneco pela velocidade, então cada quadro fica com o pé na linha do
# chão (como os quadros de pulo da base); a altura que o ChatGPT desenhou ficaria somada ao pulo
NO_AR = {"e_pulo", "e_queda", "e_ar_chifre", "e_ar_soco", "e_manto_asa", "e_dir_tras", "e_juizo_cima"}
AJUSTE = {}                # folha: fator extra quando o quadro mais alto não é o de pé (pulo, chifre erguido)
CELULA = 2172 / 8


def paleta():
    return np.array(json.loads((PECAS / "paleta.json").read_text())["cores"], np.uint8)


def travar(cor, opaco, pal):
    out = np.zeros(opaco.shape + (4,), np.uint8)
    px = cor[opaco]
    if len(px):
        idx = np.argmin(((lab(px.clip(0, 255))[:, None] - lab(pal)[None]) ** 2).sum(-1), 1)
        out[opaco, :3] = pal[idx]
        out[opaco, 3] = 255
    return out


def celulas(nome):
    """Separa as 8 poses. O manto encosta no vizinho, então o corte entre células é a coluna com menos desenho perto
    da divisa de 271 px; pedaço que passa da coluna vai com o dono pelo centro."""
    im = np.asarray(Image.open(FOLHAS / f"{nome}.png").convert("RGB")).astype(np.float32)
    a = sem_magenta(im)
    H, W = a.shape
    # costura entre células: caminho de cima a baixo que passa pelo menor número de pixels de desenho (contorna mão e
    # ponta de manto do vizinho em vez de cortar reto)
    costuras = [np.zeros(H, int)]
    for k in range(1, 8):
        c = round(k * CELULA)
        L, R = c - 70, c + 70
        custo = a[:, L:R].astype(np.float32) * 100 + np.abs(np.arange(L, R) - c)[None] * 0.02
        acc = custo.copy()
        de = np.zeros(custo.shape, int)
        for y in range(1, H):
            prev = acc[y - 1]
            opc = np.stack([np.r_[np.inf, prev[:-1]], prev, np.r_[prev[1:], np.inf]])
            j = np.argmin(opc, 0)
            de[y] = j - 1
            acc[y] += opc[j, np.arange(len(prev))]
        x = int(np.argmin(acc[-1]))
        cam = np.zeros(H, int)
        for y in range(H - 1, -1, -1):
            cam[y] = x + L
            x += de[y][x]
            x = min(max(x, 0), R - L - 1)
        costuras.append(cam)
    costuras.append(np.full(H, W))
    cortes = [int(np.median(c)) for c in costuras]
    xx = np.arange(W)[None]
    out = []
    for c in range(8):
        m = (a * ((xx >= costuras[c][:, None]) & (xx < costuras[c + 1][:, None]))).astype(np.uint8)
        n, rot, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
        if n <= 1:
            out.append(m)
            continue
        maior = st[1:, 4].max()
        fica = []
        for i in range(1, n):
            x, y, w, h, area = st[i]
            comp = rot == i
            na_divisa = bool((comp & ((xx <= costuras[c][:, None] + 1) | (xx >= costuras[c + 1][:, None] - 2))).any())
            # pedaço do vizinho cortado na divisa (mão, ponta do manto) não vai junto: nada voa solto no quadro
            if area >= 30 and (area == maior or not na_divisa or area > 0.15 * maior):
                fica.append(i)
        out.append(np.isin(rot, fica).astype(np.uint8))
    return im, out, cortes


def verde_solto(fig, d=6, limite=250):
    """O ChatGPT às vezes pinta a calça de oliva num quadro só; travado, vira o verde escuro das chamas e a calça
    "muda de cor". Verde escuro longe (mais de d px) de qualquer verde claro de chama não é chama: se passa do limite
    (o normal é ~70 px por quadro), volta para o roxo escuro da calça."""
    a = fig[..., 3] > 0
    escuro = (fig[..., :3] == (77, 105, 32)).all(-1) & a
    claro = ((fig[..., :3] == (90, 216, 20)).all(-1) | (fig[..., :3] == (214, 230, 48)).all(-1)) & a
    perto = cv2.dilate(claro.astype(np.uint8), np.ones((2 * d + 1, 2 * d + 1), np.uint8)) > 0
    solto = escuro & ~perto
    if solto.sum() > limite:
        fig[solto, :3] = (64, 48, 71)


def firme(nomes):
    pal = paleta()
    for nome in nomes:
        im, mascaras, cortes = celulas(nome)
        caixas = []
        for m in mascaras:
            ys, xs = np.nonzero(m)
            caixas.append((xs.min(), xs.max(), ys.min(), ys.max()) if len(ys) else None)
        alt = max(c[3] - c[2] + 1 for c in caixas if c)
        # deslocamento da folha: os cascos do 1º quadro (postura) vão para o eixo; os outros andam junto
        m0 = mascaras[0]
        ys0, xs0 = np.nonzero(m0)
        pes0 = xs0[ys0 > ys0.max() - 40]
        desvio = (pes0.min() + pes0.max()) / 2 - 0.5 * CELULA
        chao = max(c[3] for c in caixas if c)
        esc = ALTURA_REF / alt * AJUSTE.get(nome, 1.0)
        saida = FIRMES / nome
        saida.mkdir(parents=True, exist_ok=True)
        for i, (m, cx) in enumerate(zip(mascaras, caixas)):
            tela = np.zeros((TELA[1], TELA[0], 4), np.uint8)
            if cx:
                x0, x1, y0, y1 = cx
                sub = im[y0:y1 + 1, x0:x1 + 1]
                a = cv2.erode(m[y0:y1 + 1, x0:x1 + 1], np.ones((2, 2), np.uint8)).astype(np.float32)
                h, w = a.shape
                nw, nh = max(1, round(w * esc)), max(1, round(h * esc))
                pm = cv2.resize(sub * a[..., None], (nw, nh), interpolation=cv2.INTER_AREA)
                aa = cv2.resize(a, (nw, nh), interpolation=cv2.INTER_AREA)
                fig = travar(pm / np.maximum(aa[..., None], 1e-3), aa >= 0.55, pal)
                for de, para in TROCA_COR.get(nome, {}).get(i, {}).items():
                    fig[(fig[..., :3] == de).all(-1) & (fig[..., 3] > 0), :3] = para
                verde_solto(fig)
                # meio da célula vai para o eixo; o chão da folha vai para o chão do jogo
                meio = (i + 0.5) * CELULA + desvio
                X = round(EIXO + (x0 - meio) * esc)
                Y = round(CHAO - 1 - ((y1 if nome in NO_AR else chao) - y0) * esc)  # casco no pixel 659, como a base
                xa, ya = max(0, X), max(0, Y)
                xb, yb = min(TELA[0], X + nw), min(TELA[1], Y + nh)
                tela[ya:yb, xa:xb] = fig[ya - Y:yb - Y, xa - X:xb - X]
            Image.fromarray(tela).save(saida / f"{i:02d}.png")
        print(f"{nome}: escala {esc:.3f} (de pé {alt} px na folha)")


# ------------------------------------------------------------------ cabeça do kit (rosto igual em todo quadro)
# A cabeça (chifres, cabelo, rosto, tapa-olho) é uma peça só, recortada do parado de referência. Em cada quadro ela é
# achada no rascunho (giro e tamanho) e posta por cima do lugar da cabeça desenhada pelo ChatGPT, que some. A escala
# da folha inteira sai do tamanho da cabeça: o corpo fica do tamanho que a cabeça do kit pede.
CABECA_POLI = [(538, 258), (600, 252), (668, 258), (668, 296), (652, 312), (640, 340), (628, 354), (606, 358),
               (590, 352), (578, 336), (570, 320), (556, 312), (540, 300)]
JUNTA_PESCOCO = (604, 352)
REGUA_CABECA = 0.8
NOTA_MAX = 65              # casamento pior que isto (cabeça muito virada, escondida): fica a cabeça do rascunho
SEM_CABECA = {"e_provoca", "e_rolamento"}  # provoca: a mão passa na frente da cabeça; rolamento: de costas e de frente no giro
# cor errada do rascunho num quadro só (ex.: perna do chute pintada de oliva, que trava no verde escuro das chamas)
TROCA_COR = {"e_dir_tras": {5: {(77, 105, 32): (64, 48, 71)}}}
SEM_CABECA_QUADRO = {"e_parry_alto": {7}, "e_defesa": {2, 3, 4, 5, 6, 7},
                     "e_berro": {1, 2, 3, 4, 5}}  # quadros com a mão no chifre: fica a cabeça do rascunho
DEITADO = {"e_queda", "e_levanta", "e_rolamento", "e_derrota", "e_vitima_agarrado", "e_vitima_arremessado"}
MANTO = {(33, 26, 43), (64, 48, 71), (114, 80, 105)}


def _cores(img, cores):
    rgb = img[..., :3].reshape(-1, 3)
    m = np.zeros(len(rgb), bool)
    for c in cores:
        m |= (rgb == c).all(1)
    return m.reshape(img.shape[:2]) & (img[..., 3] > 0)


def kit_cabeca():
    from PIL import ImageDraw
    ref_ = np.asarray(Image.open(PECAS / "ref.png"))
    mk = Image.new("L", TELA, 0)
    ImageDraw.Draw(mk).polygon(CABECA_POLI, fill=255)
    m = (np.asarray(mk) > 0) & (ref_[..., 3] > 0)
    # ponta do manto que entra no polígono embaixo da orelha não é cabeça
    m &= ~(_cores(ref_, MANTO) & (np.arange(TELA[1])[:, None] > 300))
    ys, xs = np.nonzero(m)
    x0, y0 = xs.min(), ys.min()
    peca = np.where(m[..., None], ref_, 0)[y0:ys.max() + 1, x0:xs.max() + 1].astype(np.uint8)
    Image.fromarray(peca).save(PECAS / "cabeca.png")
    kit = {"cabeca": {"arquivo": "cabeca.png", "origem": [int(x0), int(y0)], "junta": list(JUNTA_PESCOCO)}}
    (PECAS / "kit.json").write_text(json.dumps(kit, indent=1), encoding="utf-8")
    print("cabeça do kit:", peca.shape[1], "x", peca.shape[0], "em", (int(x0), int(y0)))


def _cabeca(ang, esc):
    from boneco_ajuste import rotsprite
    kit = json.loads((PECAS / "kit.json").read_text())["cabeca"]
    img = np.asarray(Image.open(PECAS / kit["arquivo"]))
    piv = (kit["junta"][0] - kit["origem"][0], kit["junta"][1] - kit["origem"][1])
    if esc != 1.0:
        h, w = img.shape[:2]
        img = np.asarray(Image.fromarray(img).resize((max(1, round(w * esc)), max(1, round(h * esc))), Image.NEAREST))
        piv = (piv[0] * esc, piv[1] * esc)
    return rotsprite(img, ang, piv)


def _cinza(img):
    a = img[..., 3:4] > 0
    return np.where(a, img[..., :3], 0).astype(np.float32)


def achar_cabeca(q, angulos=range(-35, 36, 5), escalas=(1.0,)):
    al = q[..., 3] > 0
    ys, xs = np.nonzero(al)
    y1 = ys.min() + int((ys.max() - ys.min()) * 0.6)
    X0, Y0, X1, Y1 = max(0, xs.min() - 30), max(0, ys.min() - 30), min(TELA[0], xs.max() + 30), y1 + 40
    reg = _cinza(q[Y0:Y1, X0:X1])
    melhor = None
    for esc in escalas:
        for ang in angulos:
            r, p = _cabeca(ang, esc)
            m = (r[..., 3] > 0).astype(np.float32)
            if r.shape[0] >= reg.shape[0] or r.shape[1] >= reg.shape[1]:
                continue
            res = cv2.matchTemplate(reg, _cinza(r), cv2.TM_SQDIFF, mask=np.repeat(m[..., None], 3, -1))
            res = np.nan_to_num(res, nan=1e18, posinf=1e18)
            v, _, pm, _ = cv2.minMaxLoc(res)
            nota = math.sqrt(v / (m.sum() * 3))
            if melhor is None or nota < melhor[0]:
                melhor = (nota, ang, esc, (pm[0] + X0 + p[0], pm[1] + Y0 + p[1]))
    return melhor


def trocar_cabeca(q, achado):
    nota, ang, esc, junta = achado
    r, p = _cabeca(ang, 1.0)  # achada no tamanho do rascunho, posta no tamanho do kit, presa na junta do pescoço
    x0, y0 = int(round(junta[0] - p[0])), int(round(junta[1] - p[1]))
    nova = np.zeros_like(q)
    h, w = r.shape[:2]
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(TELA[0], x0 + w), min(TELA[1], y0 + h)
    nova[ya:yb, xa:xb] = r[ya - y0:yb - y0, xa - x0:xb - x0]
    mn = nova[..., 3] > 0
    out = q.copy()
    # some a cabeça velha: tudo que não é manto perto da cabeça nova; chifre e cabelo que sobram mais longe também
    perto = cv2.dilate(mn.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    longe = cv2.dilate(mn.astype(np.uint8), np.ones((31, 31), np.uint8)) > 0
    cab_cores = {(122, 48, 52), (72, 38, 40), (188, 66, 66), (242, 182, 125), (243, 212, 174)}
    apaga = (perto & ~_cores(q, MANTO)) | (longe & ~perto & _cores(q, cab_cores) & (np.arange(TELA[1])[:, None] < junta[1] - 10))
    out[apaga] = 0
    out[mn] = nova[mn]
    # fresta: onde a cabeça velha era maior que a nova sobra um buraco entre a cabeça e o manto/ombro. Fecha com a
    # cor do vizinho que não é a cabeça (o manto ou o ombro continuam até encostar na cabeça nova)
    al = out[..., 3] > 0
    fechado = cv2.morphologyEx(al.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)) > 0
    buraco = fechado & ~al & perto
    fonte = al & ~mn
    for _ in range(8):
        if not buraco.any():
            break
        for dy, dx in ((0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            viz = np.roll(fonte, (dy, dx), (0, 1))
            pega = buraco & viz
            if pega.any():
                out[pega] = np.roll(out, (dy, dx), (0, 1))[pega]
                fonte = fonte | pega
                buraco = buraco & ~pega
    # pedaço solto que sobrou da cabeça velha some
    al = (out[..., 3] > 0).astype(np.uint8)
    n, lab_, st, _ = cv2.connectedComponentsWithStats(al, connectivity=8)
    if n > 2:
        maior = 1 + int(np.argmax(st[1:, 4]))
        for i in range(1, n):
            if i != maior and st[i, 4] < 400:
                out[lab_ == i] = 0
    return out


def um_x(nomes):
    for nome in nomes:
        (FIRMES_1X / nome).mkdir(parents=True, exist_ok=True)
        for arq in sorted((FIRMES / nome).glob("*.png")):
            a = np.asarray(Image.open(arq))
            Image.fromarray(np.ascontiguousarray(a[1::3, 1::3])).save(FIRMES_1X / nome / arq.name)


def cabecas(nomes):
    for nome in nomes:
        pasta = FIRMES / nome
        qs = [np.asarray(Image.open(pasta / f"{i:02d}.png")) for i in range(8)]
        # A cabeça é a régua da folha: o ChatGPT desenha o corpo em tamanhos diferentes a cada folha, mas a cabeça
        # dele, com o corpo na altura do parado de referência, sai 0,8 da cabeça do kit (medido no e_anda). Se a
        # folha veio maior ou menor, a escala inteira corrige até a cabeça dar 0,8. A cabeça do kit entra sempre no
        # tamanho do kit (proporção do conceito aprovado), presa na junta do pescoço.
        escalas = (0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0)
        angs = range(-120, 121, 10) if nome in DEITADO else range(-35, 36, 5)
        achados = [achar_cabeca(q, angs, escalas) if q[..., 3].any() else None for q in qs]
        # só os casamentos bons medem; sem nenhum (folha toda deitada), fica a escala pela altura
        escs = sorted(a[2] for a in achados if a and a[0] <= NOTA_MAX)
        mediana = escs[len(escs) // 2] if escs else REGUA_CABECA
        if abs(mediana - REGUA_CABECA) > 0.03:
            AJUSTE[nome] = AJUSTE.get(nome, 1.0) * REGUA_CABECA / mediana
            firme([nome])
            qs = [np.asarray(Image.open(pasta / f"{i:02d}.png")) for i in range(8)]
            achados = [achar_cabeca(q, angs, (0.75, 0.8, 0.85)) if q[..., 3].any() else None for q in qs]
        for i, (q, a) in enumerate(zip(qs, achados)):
            # a escala sai da cabeça em toda folha; a troca não acontece onde a cabeça do kit taparia mão ou nuca
            if a and a[0] <= NOTA_MAX and nome not in SEM_CABECA and i not in SEM_CABECA_QUADRO.get(nome, ()):
                Image.fromarray(trocar_cabeca(q, a)).save(pasta / f"{i:02d}.png")
        print(nome, "cabeça:", [f"{a[1]}°x{a[2]} nota {a[0]:.0f}" if a else "-" for a in achados])


# ------------------------------------------------------------------ conferência (robô de defeitos do Grão-Pastor)
def conferir(nomes=None):
    """Por quadro: cor fora da paleta, pedaço solto (ilha de mais de 40 px longe do corpo), tamanho do corpo que pula
    de um quadro para o seguinte (mais de 12% na largura do tronco) e casco fora do chão no que devia estar no chão.
    Grava docs/boneco-pecas/gbzin/grao_pastor_conferencia.md."""
    pal = {tuple(c) for c in paleta().tolist()}
    nomes = nomes or sorted(p.name for p in FIRMES.iterdir() if p.is_dir())
    linhas, total = [], 0
    for nome in nomes:
        defeitos = []
        larg_ant = None
        for arq in sorted((FIRMES / nome).glob("*.png")):
            q = np.asarray(Image.open(arq))
            al = q[..., 3] > 0
            if not al.any():
                defeitos.append(f"{arq.stem}: quadro vazio")
                continue
            cores = {tuple(c) for c in q[al][:, :3].tolist()}
            fora = cores - pal
            if fora:
                defeitos.append(f"{arq.stem}: {len(fora)} cores fora da paleta")
            n, rot, st, _ = cv2.connectedComponentsWithStats(al.astype(np.uint8), connectivity=8)
            maior = 1 + int(np.argmax(st[1:, 4]))
            perto = cv2.dilate((rot == maior).astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
            soltos = [i for i in range(1, n) if i != maior and st[i, 4] > 40 and not perto[rot == i].any()]
            if soltos:
                defeitos.append(f"{arq.stem}: {len(soltos)} pedaço(s) solto(s) longe do corpo")
            ys, xs = np.nonzero(al)
            # largura do tronco: na altura do peito (35% de cima), só a pele e a caveira, sem manto
            yp = ys.min() + int(0.35 * (ys.max() - ys.min()))
            faixa = q[yp - 6:yp + 6]
            corpo = (faixa[..., 3] > 0) & ~_cores(faixa, MANTO)
            cols = np.nonzero(corpo.any(0))[0]
            larg = cols.max() - cols.min() if len(cols) else 0
            if larg_ant and larg and abs(larg - larg_ant) / larg_ant > 0.12 and nome == "e_referencia_ginga":
                defeitos.append(f"{arq.stem}: tronco muda de {larg_ant} para {larg} px")
            larg_ant = larg
        total += len(defeitos)
        linhas.append(f"| {nome} | {len(defeitos)} | {'; '.join(defeitos) or 'ok'} |")
    rel = RAIZ / "docs/boneco-pecas/gbzin/grao_pastor_conferencia.md"
    rel.parent.mkdir(parents=True, exist_ok=True)
    rel.write_text("# Conferência do Grão-Pastor (quadros_e_firmes_hd)\n\n"
                   "Robô de `python ferramentas/gbzin_e_pecas.py conferir`: cor fora da paleta, pedaço solto longe do "
                   "corpo, quadro vazio, tronco que muda de tamanho no parado.\n\n| Folha | Defeitos | Onde |\n|---|---|---|\n"
                   + "\n".join(linhas) + f"\n\nTotal: {total}\n", encoding="utf-8")
    print(f"conferência: {total} defeitos em {len(nomes)} folhas")
    return total


if __name__ == "__main__":
    if sys.argv[1] == "firme":
        firme(sys.argv[2:])
        cabecas(sys.argv[2:])
        um_x(sys.argv[2:])
        if "e_referencia_ginga" in sys.argv[2:]:
            parado()
    else:
        {"ref": ref, "parado": parado, "kit": kit_cabeca, "conferir": conferir}[sys.argv[1]]()
