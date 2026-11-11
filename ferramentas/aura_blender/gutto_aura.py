"""Aura do Gutto despertado: GARANHÃO DE RAIO VERMELHO empinado atrás e acima dele.

Camadas (ordem de desenho): crateras de casco em brasa no chão, garanhão (malha com ossos no Blender, textura = o
conceito aprovado), raios soltos que se refazem, ferraduras-faísca girando e, à FRENTE do corpo, o vapor do nariz.
Tudo que é genérico vem de comum.py; passo a passo em docs/arcade/aura_blender.md.

    python ferramentas/aura_blender/gutto_aura.py <pasta de trabalho>                  # tudo, na ordem
    python ferramentas/aura_blender/gutto_aura.py <pasta de trabalho> pontos chicote   # só o movimento (1 s)
    etapas: recortes, rig (Blender), chicote, compor, instala (copia para sprites/gutto/aura/)
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import comum as C

ID = "gutto"
AURA = "garanhao"
SRC = os.path.join(C.RAIZ, "sprites", ID, "quadros", "folhas_arcade", "e_conceito.png")
DESTINO = os.path.join(C.RAIZ, "sprites", ID, "aura")
# conceito 2172x724: vista 1 (só o corpo) nas colunas 0..420; vista 3 (corpo + aura) nas colunas 790..1665.
# Corpo de 450 px (do chifre à sola) vira 112 no jogo; eixo entre os dois cascos, chão na sola.
TELA = C.Tela(cx=1240.0, chao=705.0, escala=112 / 450.0)
CORPO_X = (0, 420)
AURA_X = (790, 1665)
N = 48                  # quadros do garanhão (empina e desce uma vez, um coice de cada pata)
TIQ = 2                 # tiques do jogo por quadro
NPART = 2 * N           # laço dos raios, das crateras, das ferraduras e do vapor

# ------------------------------------------------------------------------------------------------------------- recortes
# contorno do cavalo (cabeça, pescoço, tronco, patas, crina) em px do conceito; o que fica fora são os raios soltos
# do desenho, que NÃO entram na malha: a camada `raios` os refaz mudando de traçado
POLIGONO = [(792, 8), (1428, 8), (1428, 150), (1470, 104), (1540, 112), (1632, 186), (1632, 432), (1505, 432), (1440, 372),
            (1425, 470), (1130, 470), (1118, 318), (1050, 308), (960, 300), (880, 246), (792, 196)]
FERRADURAS = [(1575, 78, 1652, 148), (838, 342, 902, 418), (925, 528, 992, 602), (1488, 472, 1562, 548)]
Y_CHAO = 640            # daqui para baixo, fora do corpo, é cratera
CHAO_X = (940, 1560)
CASCOS = (90, 348)      # x do meio de cada casco do Gutto na vista 1 (a cratera fecha embaixo dele)
NARINA = (1318, 383)    # de onde sai o vapor, na vista com aura
# tronco que o corpo escondia (x, y, raio): remendo, fica atrás do corpo
TRONCO = [(1345, 235, 70), (1300, 330, 82), (1262, 415, 62)]
GARUPA = [(1250, 250, 60), (1215, 330, 66), (1200, 410, 50)]
# rabo de raio: o tronco não acaba num corte, afina num chicote de raio que desce até o chão entre os cascos do Gutto
# (remendo, atrás do corpo; textura = o próprio tronco do desenho, espelhado para baixo e espremido para a ponta)
RABO_Y = (400, 672)     # da linha em que o tronco passa a ser rabo até a ponta
RABO_PONTA_X = 1240
RABO_FONTE = (1250, 80, 385, 235)   # faixa do tronco que vira textura: x do meio, meia largura, y de baixo, altura

# ---------------------------------------------------------------------------------------------------------------- ossos
# (nome, pai, cabeça, cauda) em px do conceito. A raiz é o dorso: a cabeça dele (escondida atrás do Gutto) é o pivô
# em que o cavalo empina.
OSSOS = [
    ("dorso", None, (1262, 425), (1335, 245)),
    ("pescoco", "dorso", (1322, 222), (1300, 92)),
    ("cabeca", "pescoco", (1300, 92), (1402, 42)),
    ("queixo", "cabeca", (1338, 104), (1400, 134)),
    ("p1a", "dorso", (1378, 222), (1488, 132)), ("p1b", "p1a", (1488, 132), (1560, 165)), ("p1c", "p1b", (1560, 165), (1590, 242)),
    ("p2a", "dorso", (1378, 296), (1494, 250)), ("p2b", "p2a", (1494, 250), (1562, 310)), ("p2c", "p2b", (1562, 310), (1585, 396)),
    ("c1a", "pescoco", (1272, 66), (1172, 60)), ("c1b", "c1a", (1172, 60), (1072, 62)), ("c1c", "c1b", (1072, 62), (972, 82)),
    ("c1d", "c1c", (972, 82), (872, 98)),
    ("c2a", "pescoco", (1255, 132), (1155, 142)), ("c2b", "c2a", (1155, 142), (1055, 160)), ("c2c", "c2b", (1055, 160), (960, 152)),
    ("c2d", "c2c", (960, 152), (872, 162)),
    ("c3a", "dorso", (1232, 202), (1132, 216)), ("c3b", "c3a", (1132, 216), (1040, 236)), ("c3c", "c3b", (1040, 236), (950, 252)),
    ("c3d", "c3c", (950, 252), (862, 284)),
    ("r1", "dorso", (1262, 440), (1254, 515)), ("r2", "r1", (1254, 515), (1245, 592)), ("r3", "r2", (1245, 592), (1240, 668)),
]
# famílias de ossos: um vértice só pesa nos ossos da família do osso mais próximo (e nos "abertos" a todas).
# Sem isso a borda de uma pata, que fica a 30 px da outra, sairia puxada pelas duas.
FAMILIA = {"dorso": "t", "pescoco": "t", "cabeca": "t", "queixo": "q", "p1a": "1", "p1b": "1", "p1c": "1",
           "p2a": "2", "p2b": "2", "p2c": "2", "r1": "r", "r2": "r", "r3": "r"}


def familia(nome):
    return FAMILIA.get(nome, "c")


def recortes(pasta):
    import cv2
    from scipy import ndimage as ndi
    from PIL import Image, ImageDraw
    rec = os.path.join(pasta, "recortes"); os.makedirs(rec, exist_ok=True)
    im = C.le_rgb(SRC); H, W = im.shape[:2]
    R, G, B = C.canais(im)
    fg = C.chave_magenta(im)
    # ---- corpo na vista 1; o vapor do nariz sai do corpo (vira camada à parte, em laço)
    corpo = C.recorta_corpo(fg, im, *CORPO_X)
    DX, DY, nota = C.casa_corpo(im, corpo, 1000, 1500)
    print("corpo bbox", C.caixa(corpo), "casado na vista 3: dx", DX, "dy", DY, "nota", round(nota, 3))
    assert DY == 0 and nota > 0.9, "o corpo da vista 1 não casou com o da vista 3"
    nx, ny = NARINA[0] - DX, NARINA[1]
    branco = (R > 185) & (G > 165) & (B > 165)
    cx_ = np.zeros_like(fg); cx_[ny - 22:ny + 34, nx:nx + 75] = True
    vapor = ndi.binary_dilation(ndi.binary_opening(branco & cx_ & corpo, iterations=2), iterations=4) & cx_
    print("vapor do desenho: px", int(vapor.sum()), "caixa", C.caixa(vapor))
    corpo_sv = C.maior_componente(corpo & ~vapor)
    Image.fromarray(np.dstack([im, (corpo_sv * 255).astype(np.uint8)])[:, :CORPO_X[1]]).save(f"{rec}/corpo_v1.png")
    corpo3d = ndi.binary_dilation(C.desloca(corpo, DX), iterations=5)
    # ---- aura na vista 3. Carmesim FRIO: o azul fica, mas limitado (o véu rosa-choque e a casca de magenta viram
    # carmesim), e nada de laranja (o verde nunca passa do azul)
    rgbA = im.copy()
    rgbA[..., 2] = np.minimum(B, G + 45).astype(np.uint8)
    rgbA[..., 1] = np.minimum(G, rgbA[..., 2]).astype(np.uint8)
    aura = fg.copy(); aura[:, :AURA_X[0]] = False; aura[:, AURA_X[1]:] = False
    aura &= ~corpo3d
    aura = ndi.binary_opening(aura, iterations=1)
    info = dict(DX=DX, corpo_bbox=C.caixa(corpo_sv), narina=list(NARINA))
    # ---- ferraduras: uma peça por caixa
    usados = np.zeros_like(aura)
    for k, (x0, y0, x1, y1) in enumerate(FERRADURAS):
        m = np.zeros_like(aura); m[y0:y1, x0:x1] = aura[y0:y1, x0:x1]
        m = C.maior_componente(m, conect=8)
        C.salva_rgba(f"{rec}/ferradura_{k}.png", rgbA, m); info[f"ferradura_{k}"] = C.caixa(m)
        usados[y0:y1, x0:x1] = True
    # ---- crateras: o buraco de cada casco fecha com a cor vizinha (fica embaixo do casco)
    chao = aura.copy(); chao[:Y_CHAO] = False; chao[:, :CHAO_X[0]] = False; chao[:, CHAO_X[1]:] = False
    chao = ndi.binary_opening(chao, iterations=1)
    full = rgbA.copy(); cheio = chao.copy()
    for xm in CASCOS:
        tampa = np.zeros((H, W), np.uint8)
        cv2.ellipse(tampa, (xm + DX, 699), (66, 15), 0, 0, 360, 1, -1)
        tampa = (tampa > 0) & ~chao
        C.remenda_vizinho(full, chao, tampa); cheio |= tampa
    cheio[708:] = False
    C.salva_rgba(f"{rec}/chao.png", full, cheio); info["chao_bbox"] = C.caixa(cheio)
    # ---- cavalo: o que cai dentro do polígono; pedaço solto fino sai (a camada de raios cuida)
    pol = np.zeros((H, W), np.uint8); cv2.fillPoly(pol, [np.array(POLIGONO, np.int32)], 1)
    m = aura & (pol > 0) & ~usados
    cav, frag, gotas = C.separa_soltos(m, area_frag=900, lado_frag=24)
    # tronco que o corpo escondia: tubo ao longo do dorso, só atrás do corpo, clonado da crina acima dele
    toco = (C.discos((H, W), TRONCO) | C.discos((H, W), GARUPA)) & ndi.binary_dilation(corpo3d, iterations=2) & ~cav
    full = rgbA.copy()
    falta = C.remenda_clone(full, rgbA, cav, toco, (-112, -14), vezes=3)
    C.remenda_vizinho(full, (cav | toco) & ~falta, falta)
    tot = cav | toco
    tot2 = ndi.binary_fill_holes(ndi.binary_closing(tot, iterations=4)) & (tot | corpo3d)
    furos = ndi.binary_fill_holes(tot2) & ~tot2                      # furo pequeno é sobra do véu rosa: fecha
    lab, comps = C.componentes(furos)
    for cpt in comps:
        if cpt["area"] < 1500:
            tot2 |= lab == cpt["i"]
    C.remenda_vizinho(full, tot, tot2 & ~tot); tot = tot2
    # rabo de raio no lugar do corte: abaixo de RABO_Y[0] o tronco afina até a ponta, com a borda em dentes de raio
    y0r, y1r = RABO_Y; xs = np.arange(W)[None, :].astype(float); yy = np.arange(H)[:, None].astype(float)
    lin = tot[y0r - 6:y0r + 1].any(0); xl = xr = 1262                # o trecho do tronco (a pata de baixo fica fora)
    while lin[xl - 1]:
        xl -= 1
    while lin[xr + 1]:
        xr += 1
    xl, xr = float(xl), float(xr)
    t = np.clip((yy - y0r) / (y1r - y0r), 0, 1)
    meio = (xl + xr) / 2 + (RABO_PONTA_X - (xl + xr) / 2) * t ** 0.8 + 16 * np.sin(2.3 * math.pi * t) * t * (1 - t) * 4 * 0.5
    larg = (xr - xl) / 2 * (1 - t) ** 1.35 + 2.5

    def dente(fase, passo):
        return np.abs(((yy + fase) / passo) % 2 - 1)
    le = larg * (0.80 + 0.30 * dente(0, 15) + 0.12 * dente(5, 6.5)); ld = larg * (0.80 + 0.30 * dente(9, 13) + 0.12 * dente(2, 7.5))
    u = (xs - meio) / np.where(xs < meio, le, ld)
    rabo = (np.abs(u) <= 1) & (yy >= y0r) & (yy <= y1r)
    fx, fw, fy, fh = RABO_FONTE
    sx = np.clip(np.round(fx + u * fw), 0, W - 1).astype(int); sy = np.clip(np.round(fy - t * fh + 0 * xs), 0, H - 1).astype(int)
    tinha = tot.copy(); tot[y0r:, :1445] &= rabo[y0r:, :1445]
    novo = rabo & ~tot
    cor_rabo = full[sy, sx]; ok = tinha[sy, sx]
    full[novo & ok] = cor_rabo[novo & ok]
    tot |= novo
    C.remenda_vizinho(full, tot & ~(novo & ~ok), novo & ~ok)
    info.update(rabo_px=int(novo.sum()), rabo_sem_fonte_px=int((novo & ~ok).sum()), rabo_larg_no_topo=[xl, xr])
    C.salva_rgba(f"{rec}/cavalo.png", full, tot)
    info.update(cavalo_bbox=C.caixa(tot), remendo_px=int(toco.sum()), fragmentos=frag, soltos_fora=len(gotas))
    # ---- o que sobrou (raios soltos do desenho): só referência para posicionar a camada procedural
    resto = aura & ~tot & ~usados & ~chao
    C.salva_rgba(f"{rec}/raios_ref.png", rgbA, resto)
    json.dump(info, open(f"{rec}/info.json", "w"), indent=1)
    print({k: (v if not isinstance(v, list) or len(v) < 6 else len(v)) for k, v in info.items()})
    C.previa_recortes([f"{rec}/chao.png", f"{rec}/cavalo.png"] + [f"{rec}/ferradura_{k}.png" for k in range(len(FERRADURAS))],
                      f"{pasta}/p_recortes.png", (780, 0, 1670, 724), (H, W))
    # prévia dos ossos em cima do recorte (cor = família de peso)
    pv = Image.open(f"{pasta}/p_recortes.png").convert("RGB"); d = ImageDraw.Draw(pv)
    cor = {"r": (255, 120, 255), "t": (255, 255, 0), "q": (255, 160, 0), "1": (0, 255, 120), "2": (0, 200, 255), "c": (120, 160, 255)}
    for nm, pai, h, t in OSSOS:
        d.line([(h[0] - 780, h[1]), (t[0] - 780, t[1])], fill=cor[familia(nm)], width=3)
        d.ellipse([h[0] - 784, h[1] - 4, h[0] - 776, h[1] + 4], outline=(255, 255, 255))
    pv.save(f"{pasta}/p_ossos.png")
    C.previa_recortes([f"{rec}/raios_ref.png"], f"{pasta}/p_raios_ref.png", (780, 0, 1670, 724), (H, W))


# ================================================================================================================= 2. rig
# animação por junta: (amplitude em graus, atraso em fração do ciclo, amplitude do harmônico, fase do harmônico).
# Ângulo positivo = horário na tela. O cavalo olha para a direita: empinar é anti-horário (negativo).
# Cascata: o dorso gira pouco e cedo; pescoço, cabeça e queixo vêm depois; cada pata é um chicote de três juntas e a
# segunda pata dá o coice meio ciclo depois da primeira; a crina é a que mais atrasa e a que mais gira na ponta.
ANIM = {"dorso": (-3.0, 0.00, 0.0, 0.0), "pescoco": (-3.5, 0.07, 1.0, 0.4),
        "p1a": (-7.0, 0.04, 0.0, 0.0), "p1b": (-12.0, 0.12, 2.0, 0.3), "p1c": (-13.0, 0.21, 3.0, 0.9),
        "p2a": (-7.0, 0.54, 0.0, 0.0), "p2b": (-10.5, 0.62, 2.0, 3.4), "p2c": (-11.0, 0.71, 2.6, 4.0),
        "c1a": (2.5, 0.12, 0.6, 0.0), "c1b": (4.0, 0.22, 1.2, 0.5), "c1c": (6.0, 0.33, 2.0, 1.0), "c1d": (9.0, 0.45, 3.0, 1.5),
        "c2a": (2.5, 0.15, 0.6, 1.3), "c2b": (4.5, 0.26, 1.3, 1.8), "c2c": (6.5, 0.37, 2.2, 2.3), "c2d": (9.5, 0.49, 3.2, 2.8),
        "r1": (3.0, 0.10, 0.8, 0.5), "r2": (5.0, 0.24, 1.5, 1.2), "r3": (8.0, 0.40, 2.4, 2.0),
        "c3a": (2.5, 0.18, 0.7, 2.6), "c3b": (4.5, 0.30, 1.4, 3.1), "c3c": (7.0, 0.41, 2.4, 3.6), "c3d": (10.0, 0.53, 3.4, 4.1)}
# cabeça e queixo: o harmônico é o 3º (sacode a cabeça três vezes por ciclo, relinchando: o queixo abre e fecha)
ANIM_CABECA = {"cabeca": (-5.0, 0.14, 3.2, 0.0), "queixo": (6.0, 0.22, 4.0, 1.2)}
CENTRO = 0.0
PROF = {"t": 0.0, "q": -0.5, "1": 1.5, "2": -1.5, "c": 1.0, "r": -2.5}       # quem cobre quem: a pata de baixo passa na frente


def _segs():
    return [(TELA.g(*h), TELA.g(*t)) for _, _, h, t in OSSOS]


def pesos_por_familia(XZ, k=4, folga=1.5, pot=3):
    """Como C.pesos_por_osso, mas cada vértice só enxerga os ossos que a família do osso mais próximo permite."""
    nomes = [o[0] for o in OSSOS]; fam = [familia(n) for n in nomes]
    D = C.dist_segmentos(XZ, _segs()); perto = D.argmin(1)

    def pode(f, j):
        g = fam[j]
        if f == "1" or f == "2":
            return g == f or nomes[j] == "dorso"
        if f == "q":
            return g == "q" or nomes[j] in ("cabeca", "pescoco")
        if f == "c":
            return g in ("c", "t")
        if f == "r":
            return g == "r" or nomes[j] == "dorso"
        return g in ("t", "c") or nomes[j] in ("p1a", "p2a", "r1")  # tronco, pescoço e cabeça
    M = np.array([[pode(fam[perto[i]], j) for j in range(len(nomes))] for i in range(len(XZ))])
    D2 = np.where(M, D, 1e9)
    ordem = np.argsort(D2, axis=1, kind="stable")[:, :k]; lin = np.arange(len(XZ))[:, None]
    w = np.where(D2[lin, ordem] < 1e8, 1.0 / (D2[lin, ordem] + folga) ** pot, 0.0)
    W = np.zeros_like(D); W[lin, ordem] = w / w.sum(1, keepdims=True)
    return W, perto


def rig(pasta, so_pontos=False):
    """Roda DENTRO do Blender."""
    C.bl_cena(TELA, N)
    rec = os.path.join(pasta, "recortes")
    segs = _segs(); fam = [familia(o[0]) for o in OSSOS]

    def prof(X, Z):
        return PROF[fam[int(C.dist_segmentos([(X, Z)], segs).argmin())]]
    pc = C.bl_malha_com_ossos("cav", os.path.join(rec, "cavalo.png"), OSSOS, TELA, N, prof=prof,
                              tremor=[dict(eixo="X", raio=9.0, fase=0.0, forca=5.0), dict(eixo="Z", raio=11.0, fase=2.1, forca=6.0)])
    # pesos refeitos por família (o comum reparte só por distância)
    ob = pc["malha"]; ox, oz = pc["origem"]
    XZ = np.array([(v.co.x + ox, v.co.z + oz) for v in ob.data.vertices])
    W, _ = pesos_por_familia(XZ)
    for j, nm in enumerate(pc["nomes"]):
        g = ob.vertex_groups[nm]
        g.remove(list(range(len(XZ))))
        for i in np.nonzero(W[:, j])[0]:
            g.add([int(i)], float(W[i, j]), "REPLACE")
    C.bl_anima_juntas(pc["arm"], ANIM, N, centro=CENTRO)
    C.bl_anima_juntas(pc["arm"], ANIM_CABECA, N, centro=CENTRO, harmonico=3)
    # o cavalo inteiro sobe quando empina e desce quando cai; estica um pouco para cima na subida
    C.bl_anima_objeto(pc["arm"], N, lambda t: dict(
        location=(ox + 1.2 * math.sin(t + 0.8), 0, oz + 3.2 * math.sin(t - 0.1) + 0.7 * math.sin(2 * t + 0.5)),
        scale=(1 + 0.02 * math.sin(t + 2.0), 1, 1 + 0.035 * math.sin(t - 0.3))))
    C.bl_renderiza(pasta, N, {"garanhao": [pc["malha"]]}, lambda f: C.bl_pontas(pc, TELA, "cav"), so_pontos=so_pontos, blend="rig.blend")


CHICOTE = ["cav_raiz", "cav_dorso", "cav_pescoco", "cav_cabeca", "cav_queixo", "cav_p1a", "cav_p1b", "cav_p1c", "cav_p2a", "cav_p2b", "cav_p2c",
           "cav_c1a", "cav_c1b", "cav_c1c", "cav_c1d", "cav_c2a", "cav_c2b", "cav_c2c", "cav_c2d", "cav_c3a", "cav_c3b", "cav_c3c", "cav_c3d", "cav_r1", "cav_r2", "cav_r3"]


def chicote(pasta, mostra=True):
    PT = json.load(open(f"{pasta}/render/pontos.json"))
    res = C.mede_pontos(PT["pontos"], CHICOTE, mostra)
    json.dump(res, open(f"{pasta}/chicote.json", "w"), indent=1)
    return res


# ============================================================================================================== 3. compor
# raios soltos: cada um nasce numa junta do cavalo (ponto que o Blender exporta, então a raiz do raio ANDA com ele; a
# cada renascimento sorteia uma das juntas de "a") e vai até um ponto sorteado numa caixa da tela (x0, x1, y0, y1).
# g = porte: 2 = raio grande (miolo branco de 3 px na raiz, afinando até 1 px na ponta), 1 = médio, 0 = fio.
# Todos renascem a cada 24 quadros com outro traçado; os nascimentos são escalonados (b), então há sempre raio aceso
# dos dois lados, como no desenho, e nunca "um raio enorme / nada".
PER_RAIO = 24
RAIOS = [
    dict(g=2, a=("cav_c3d", "cav_c3c"), cx=(92, 128, 160, 188)),      # esquerda: da crina de baixo ao chão
    dict(g=2, a=("cav_p2c", "cav_p2b"), cx=(226, 258, 160, 188)),     # direita: do casco de baixo ao chão
    dict(g=2, a=("cav_c2d", "cav_c3d"), cx=(44, 78, 118, 160)),
    dict(g=2, a=("cav_p1c", "cav_p2c"), cx=(286, 318, 96, 150)),
    dict(g=2, a=("cav_c3c", "cav_c3b"), cx=(112, 146, 150, 186)),
    dict(g=2, a=("cav_p2c",), cx=(250, 290, 150, 186)),
    dict(g=1, a=("cav_c1d", "cav_c2d"), cx=(34, 70, 22, 60)),
    dict(g=1, a=("cav_p1c",), cx=(288, 322, 14, 50)),
    dict(g=1, a=("cav_c2d", "cav_c2c"), cx=(40, 76, 70, 110)),
    dict(g=1, a=("cav_cabeca", "cav_queixo"), cx=(262, 300, 8, 40)),
    dict(g=1, a=("cav_c3d",), cx=(60, 96, 126, 170)),
    dict(g=1, a=("cav_p1b", "cav_p1c"), cx=(292, 326, 50, 92)),
    dict(g=1, a=("cav_c1c", "cav_c1d"), cx=(70, 120, 6, 18)),
    dict(g=1, a=("cav_p2b", "cav_p2c"), cx=(262, 300, 120, 170)),
    dict(g=0, a=("cav_c1d",), cx=(40, 66, 40, 70)),
    dict(g=0, a=("cav_queixo",), cx=(276, 306, 44, 70)),
    dict(g=0, a=("cav_c2c", "cav_c1c"), cx=(86, 120, 60, 96)),
    dict(g=0, a=("cav_p1c",), cx=(296, 330, 76, 112)),
    dict(g=0, a=("cav_c3d",), cx=(52, 84, 140, 176)),
    dict(g=0, a=("cav_p2c",), cx=(276, 312, 132, 176)),
]
for _i, _r in enumerate(RAIOS):       # grandes: um nasce a cada 4 quadros alternando de lado; os outros nos intervalos
    _r["per"] = PER_RAIO
    _r["b"] = (4 * _i) % PER_RAIO if _r["g"] == 2 else (2 + 5 * _i + (_i % 3)) % PER_RAIO
    _r["vida"] = 9 if _r["g"] == 2 else 7
# idade -> (de onde, até onde do traçado se desenha, porte a menos, aceso?, traçado refeito?, falhado?)
# o raio CRESCE da raiz, acende, treme, baixa, reacende com o traçado refeito e some da raiz para a ponta
FASES = {9: [(0.0, 0.50, 0, 1, 0, 0), (0.0, 1.0, 0, 1, 0, 0), (0.0, 1.0, 0, 1, 0, 0), (0.0, 1.0, 0, 0, 0, 0), (0.0, 1.0, 0, 1, 1, 0),
             (0.0, 1.0, 1, 1, 1, 0), (0.15, 1.0, 2, 1, 1, 0), (0.40, 1.0, 2, 0, 1, 1), (0.65, 1.0, 2, 0, 1, 1)],
         7: [(0.0, 0.60, 0, 1, 0, 0), (0.0, 1.0, 0, 1, 0, 0), (0.0, 1.0, 0, 0, 0, 0), (0.0, 1.0, 0, 1, 1, 0), (0.0, 1.0, 0, 1, 1, 0),
             (0.30, 1.0, 2, 0, 1, 1), (0.60, 1.0, 2, 0, 1, 1)]}
N_FAISCAS = 22
FER_ESC = 1.4           # ferradura 1,4x o tamanho do conceito: com 11 px ela virava um anel ilegível


def traco(p0, p1, rs_grosso, rs_fino, passo=11.0, amp=(0.07, 0.17), treme=0.8):
    """Traçado de raio de p0 a p1: trechos de tamanho DESIGUAL com quinas vivas, quase sempre alternando de lado, e o
    desvio diminuindo para a ponta (rs_grosso decide o desenho; rs_fino treme cada quina: o raio rasteja)."""
    p0 = np.array(p0, float); p1 = np.array(p1, float); d = p1 - p0; comp = float(np.hypot(*d))
    K = max(2, int(round(comp / passo))); nrm = np.array([-d[1], d[0]]) / max(comp, 1e-6)
    ts = np.cumsum(rs_grosso.uniform(0.45, 1.6, K)); ts = ts[:-1] / ts[-1]
    sn = 1.0 if rs_grosso.uniform() < 0.5 else -1.0; pts = [p0]
    for t in ts:
        des = min(comp * rs_grosso.uniform(*amp), 11.0) * (1.15 - 0.6 * t)
        pts.append(p0 + d * t + nrm * sn * des + rs_fino.uniform(-treme, treme, 2))
        if rs_grosso.uniform() < 0.82:
            sn = -sn
    return pts + [p1]


def amostra(pts, passo=0.5):
    """Pontos a cada `passo` px ao longo da polilinha, com s = fração do comprimento (0 na raiz, 1 na ponta)."""
    pts = np.array(pts, float); seg = np.hypot(*np.diff(pts, axis=0).T); tot = max(float(seg.sum()), 1e-6)
    out = []; ac = 0.0
    for a, b, l in zip(pts, pts[1:], seg):
        for u in np.arange(0, 1, passo / max(l, passo)):
            out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, (ac + l * u) / tot))
        ac += l
    out.append((pts[-1][0], pts[-1][1], 1.0))
    return out


def pinta_raio(M, pts, g, s0=0.0, s1=1.0, t0=0.0):
    """Carimba o traçado nas três máscaras M = (casca, halo, miolo), AFINANDO da raiz para a ponta.
    Só o trecho s0..s1 é desenhado (raio crescendo / sumindo); t0 = quão "ponta" o traçado já nasce (ramo)."""
    import cv2
    for x, y, s in amostra(pts):
        if s < s0 or s > s1:
            continue
        t = t0 + (1 - t0) * (s / max(s1, 1e-6))
        c = (int(round(x)), int(round(y)))
        if g >= 2:
            if t < 0.38:
                cv2.circle(M[0], c, 2, 1, -1)
            cv2.circle(M[1], c, 1 if t < 0.86 else 0, 1, -1)
            if t < 0.72:
                cv2.circle(M[2], c, 1 if t < 0.20 else 0, 1, -1)
        elif g == 1:
            cv2.circle(M[1], c, 1 if t < 0.80 else 0, 1, -1)
            if t < 0.50:
                cv2.circle(M[2], c, 0, 1, -1)
        else:
            cv2.circle(M[1 if t < 0.6 else 0], c, 0, 1, -1)       # fio: esfria para a ponta
            if t < 0.34:
                cv2.circle(M[2], c, 0, 1, -1)


def compor(pasta):
    import cv2
    from scipy import ndimage as ndi
    from PIL import Image
    rec = os.path.join(pasta, "recortes"); cam = os.path.join(pasta, "camadas")
    CW, CH, AMP = TELA.cw, TELA.ch, TELA.amp
    info = json.load(open(f"{rec}/info.json"))
    PT = json.load(open(f"{pasta}/render/pontos.json")); pontos = PT["pontos"]
    assert len(pontos) == N
    rng = np.random.default_rng(11)
    NF = len(FERRADURAS)

    # ---------- paleta fixa de 15: 14 do próprio desenho (a mais clara já é o branco do miolo do raio) + escura de contorno
    pal = C.Paleta.de_recortes([f"{rec}/cavalo.png", f"{rec}/chao.png"] + [f"{rec}/ferradura_{k}.png" for k in range(NF)],
                              TELA, n=14, escura=(44, 8, 18))
    assert pal.n == 15
    ESC, BR = pal.escura, pal.clara
    ROSA = pal.mais_proxima((255, 176, 190)); VIVO = pal.mais_proxima((246, 22, 60))
    MEDIO = pal.mais_proxima((176, 8, 36)); FUNDO = pal.mais_proxima((104, 6, 24))
    if ROSA == BR:
        ROSA = BR - 1
    print("PALETA", pal.lista())
    print("RAMPA fria", [(n, pal.cores[i].tolist()) for n, i in (("br", BR), ("rosa", ROSA), ("vivo", VIVO), ("medio", MEDIO), ("fundo", FUNDO), ("esc", ESC))])
    RAMPA = [BR, BR, ROSA, VIVO, VIVO, MEDIO]
    FRIO = (BR, ROSA, VIVO, MEDIO)

    # ---------- ruído que emenda (lado 96): velocidades pares fecham em 48, qualquer inteira em 96
    campo = C.Campo(TELA, 96)
    R1, R2, R3 = C.ladrilho(1), C.ladrilho(2, fmax=13), C.ladrilho(3, fmax=6)
    campo.fecha(N, 2, 4, 6); campo.fecha(NPART, 1, 2, 3)

    def ruido(f):               # rápido e de lado: eletricidade, não fogo subindo
        return 0.5 * campo.rola(R1, f, vy=2, vx=4) + 0.5 * campo.rola(R2, f, vy=4, vx=-6, ox=17)

    # ---------- garanhão: render -> 1x -> paleta com histerese -> contorno -> veias que faíscam -> eriçado na borda de cima
    brutos = [C.le_render(f"{pasta}/render/garanhao_{f:02d}.png", AMP) for f in range(N)]
    seco = [C.contorno(C.limpa(a), ESC) for a in pal.encaixa_seq(brutos)]
    garanhao = []
    for f, a in enumerate(seco):
        c = a.copy(); n = ruido(f)
        C.cintila(c, n, 0.68, 0.30, sobe=2, desce=1, mask=c > ESC)
        c = C.linguas(c, n, RAMPA, alt=5, forca=0.05)
        c[TELA.pe[1] + 1:] = -1                                  # a ponta do rabo não passa do chão
        garanhao.append(c)

    # ---------- crateras de casco. O recorte do desenho reduzido 4x virava um salpicado; a cratera é redesenhada com a
    # forma do conceito e leitura de pixel art: cova elíptica de borda escura, brasa em anéis que respira (uma cratera
    # defasada da outra), lascas de raio saindo da borda para os lados e para cima, fagulha subindo
    ROSA2 = pal.mais_proxima((252, 192, 214)); ROSA3 = pal.mais_proxima((251, 150, 183))
    xc = [TELA.conceito_para_jogo(x + info["DX"], 700)[0] for x in CASCOS]
    YY, XX = TELA.grade(); CY = TELA.pe[1] - 5.0
    fag = C.semeia(rng, 30, dict(k=("int", 0, 2), ox=("uni", -24, 24), b=("int", 0, NPART), dx=("uni", -0.3, 0.3), v=("uni", 0.6, 1.3),
                                 vida=("int", 16, 30)))
    for s in fag:
        s["x"] = int(round(xc[s["k"]] + s["ox"]))
    fagulha = C.desenha_fagulha(FRIO, y0=185, chao_y=TELA.pe[1])
    rl = np.random.default_rng(23)
    LASCAS = [[dict(th=math.radians(th + rl.uniform(-6, 6)), comp=cp * rl.uniform(0.85, 1.2), ph=rl.uniform(0, 6.28), h=int(rl.choice([2, 3, 4])))
               for th, cp in ((4, 17), (176, 17), (20, 15), (160, 15), (42, 14), (138, 14), (66, 12), (114, 12), (90, 9), (-6, 11), (186, 11))]
              for _ in (0, 1)]
    crateras = []
    for f in range(NPART):
        w = 2 * math.pi * f / NPART
        c = np.full((CH, CW), -1, np.int16)
        n = campo.rola(R3, f, vy=1, vx=2) * 0.6 + campo.rola(R2, f, vy=-1, vx=-3) * 0.4
        for k in (0, 1):
            p_ = math.sin(2 * w + 2.4 * k); q = 0.5 + 0.5 * p_
            rx, ry = 24.0 + 3.0 * p_, 4.3 + 0.6 * p_
            ex = (XX - xc[k]) / rx; ey = (YY - CY) / ry
            d = np.sqrt(ex * ex + ey * ey) * (1 + 0.34 * (n - 0.5))
            for lim, cor in ((1.0, FUNDO), (0.84, MEDIO), (0.66, VIVO), (0.36 + 0.16 * q, ROSA3), (0.20 + 0.16 * q, ROSA), (0.04 + 0.18 * q, BR)):
                c[d < lim] = cor
            for ls in LASCAS[k]:                                 # lasca: triângulo fino que estica e encolhe, miolo claro
                cs, sn = math.cos(ls["th"]), math.sin(ls["th"])
                bx, by = xc[k] + 0.78 * rx * cs, CY - 0.78 * ry * sn
                cp = ls["comp"] * (0.72 + 0.34 * math.sin(ls["h"] * w + ls["ph"]) + 0.16 * p_)
                tx, ty = bx + cp * cs, by - cp * sn * 0.8
                tx += 1.2 * math.sin(3 * w + ls["ph"]); px_, py_ = -sn * 1.5, -cs * 0.9
                m = np.zeros((CH, CW), np.uint8)
                cv2.fillPoly(m, [np.round(np.array([[bx + px_, by + py_], [bx - px_, by - py_], [tx, ty]])).astype(np.int32)], 1)
                cv2.line(m, (int(round(bx)), int(round(by))), (int(round(tx)), int(round(ty))), 1, 1)
                c[(m > 0) & (c < VIVO)] = VIVO
                m2 = np.zeros((CH, CW), np.uint8)
                cv2.line(m2, (int(round(bx)), int(round(by))), (int(round(bx + 0.55 * (tx - bx))), int(round(by + 0.55 * (ty - by)))), 1, 1)
                c[(m2 > 0) & (c <= VIVO)] = ROSA if q > 0.35 else ROSA3
        c[TELA.pe[1] + 1:] = -1
        c = C.contorno(c, ESC)
        C.emite(c, f, NPART, fag, fagulha)
        crateras.append(c)

    # ---------- raios soltos: muitos, finos, ramificados, dos dois lados; crescem da raiz, tremem, reacendem com o
    # traçado refeito e somem para a ponta. Sem contorno escuro (como no desenho: miolo branco, casca carmesim)
    def ponta(nome, f):
        return np.array(pontos[f % N][nome][:2], float)
    Y_TOPO = 5; LIM0 = (4, Y_TOPO); LIM1 = (CW - 5, TELA.pe[1] - 1)

    def raio(L, sd, a, f, i):
        k = ((f - sd["b"]) % NPART) // sd["per"]                # encarnação: cada renascimento tem outro traçado e outra junta
        s0, s1, menos, aceso, v, falha = FASES[sd["vida"]][a]
        rg = np.random.default_rng([91, i, k])
        x0, x1, y0, y1 = sd["cx"]; fim = np.array([rg.uniform(x0, x1), rg.uniform(y0, y1)])
        ini = ponta(sd["a"][int(rg.integers(0, len(sd["a"])))], f)
        g = sd["g"]; comp = float(np.hypot(*(fim - ini)))
        if g == 0 and comp > 26:                                # fio é curto: comprido ele vira arame
            fim = ini + (fim - ini) * 26 / comp; comp = 26.0
        pts = traco(ini, fim, np.random.default_rng([92, i, k]), np.random.default_rng([93, i, k, a]), treme=0.8 + 1.4 * v)
        pts = [np.clip(p_, LIM0, LIM1) for p_ in pts]
        rr = np.random.default_rng([94, i, k]); rj = np.random.default_rng([96, i, k, a])
        cum = np.concatenate([[0], np.cumsum([np.hypot(*(b_ - a_)) for a_, b_ in zip(pts, pts[1:])])]); cum = cum / max(cum[-1], 1e-6)
        ramos = []                                              # ramo: segue reto por onde o raio vinha quando ele quebra
        quinas = list(rr.permutation(np.arange(1, len(pts) - 1)))[:(1, 2, 3)[g]]
        for j in quinas:
            d = pts[j] - pts[j - 1]; d = d / max(float(np.hypot(*d)), 1e-6); ang = rr.uniform(0.12, 0.55) * rr.choice([-1, 1])
            d = np.array([d[0] * math.cos(ang) - d[1] * math.sin(ang), d[0] * math.sin(ang) + d[1] * math.cos(ang)])
            cr = max(5.0, comp * rr.uniform(0.22, 0.45) * (1 - 0.5 * cum[j]) * (1.0 if g == 2 else 0.6))
            fr = np.clip(pts[j] + d * cr, LIM0, LIM1)
            ramos.append((cum[j], traco(pts[j], fr, rr, rj, passo=7.0, amp=(0.10, 0.22), treme=0.7)))
            if g == 2 and cr > 14:                              # raminho do ramo
                rp = ramos[-1][1]; q_ = rp[len(rp) // 2]; d2 = np.array([d[1], -d[0]]) * rr.choice([-1, 1]) * 0.8 + d * 0.6
                ramos.append((cum[j] + 0.01, [q_, np.clip(q_ + d2 * rr.uniform(4, 8), LIM0, LIM1)]))
        M = [np.zeros((CH, CW), np.uint8) for _ in range(3)]
        ge = max(g - menos, 0)
        pinta_raio(M, pts, ge, s0, s1)
        for sf, rp in ramos:
            if s0 <= sf <= s1:
                pinta_raio(M, rp, max(ge - 1, 0), 0.0, 1.0 if s1 >= 1 else 0.5, t0=max(sf, 0.45))
        if aceso and s1 >= 1 and fim[1] > TELA.pe[1] - 9 and g >= 1:     # bateu no chão: estilhaço
            for dx_, dy_ in ((-5, -2), (5, -2), (-2, -5), (3, -4)):
                e = fim + np.array([dx_, dy_]) * rj.uniform(0.6, 1.2)
                cv2.line(M[1], (int(fim[0]), int(fim[1])), (int(e[0]), int(e[1])), 1, 1)
            cv2.circle(M[2], (int(fim[0]), int(fim[1])), 1, 1, -1)
        if falha:                                               # resto: fio falhado pelo ruído
            buraco = R2[(YY + 3 * i) % 96, (XX + 5 * f) % 96] < 0.42
            for m_ in M:
                m_[buraco] = 0
        casca, halo, miolo = (FUNDO, MEDIO, ROSA3) if not aceso else (MEDIO, VIVO, BR)
        if aceso and ge == 0:
            miolo = ROSA
        T = np.full((CH, CW), -1, np.int16)
        T[M[0] > 0] = casca; T[M[1] > 0] = halo; T[M[2] > 0] = miolo
        T[:Y_TOPO - 2] = -1
        L[T >= 0] = T[T >= 0]
        return bool((T >= 0).any())

    fs_sem = C.semeia(rng, N_FAISCAS, dict(b=("int", 0, NPART), per=lambda i, r: int(r.choice([24, 32, 48])), dx=("uni", -0.4, 0.4)))
    ZONAS = [(60, 130, 22, 180), (228, 300, 16, 185), (130, 228, 14, 32), (96, 150, 110, 186), (215, 262, 100, 186)]

    def faisca(L, sd, a, f, i):
        k = ((f - sd["b"]) % NPART) // sd["per"]
        rg = np.random.default_rng([95, i, k]); x0, x1, y0, y1 = ZONAS[int(rg.integers(0, len(ZONAS)))]
        x = int(round(rg.uniform(x0, x1) + sd["dx"] * a)); y = int(round(rg.uniform(y0, y1) - 0.5 * a))
        s = (1, 2, 3, 4, 3, 3, 2, 2, 1)[a]                      # estrela de 4 pontas inclinada que abre e fecha
        for t in range(-s, s + 1):
            cor = BR if abs(t) <= s // 3 else ROSA if abs(t) <= (2 * s) // 3 else VIVO
            C.ponto(L, x + (t + 1) // 2, y - t, cor)            # haste comprida inclinada
        for t in range(-(s // 2), s // 2 + 1):
            C.ponto(L, x + t, y + (t + 1) // 2, ROSA if t else BR)
        return True

    raios = []; viv = []
    for f in range(NPART):
        L = np.full((CH, CW), -1, np.int16)
        viv.append(C.emite(L, f, NPART, RAIOS, raio))
        C.emite(L, f, NPART, fs_sem, faisca, vida=9)
        raios.append(L)
    print("RAIOS vivos por quadro:", min(viv), "a", max(viv), "| px por quadro:", min(int((r >= 0).sum()) for r in raios), "a",
          max(int((r >= 0).sum()) for r in raios))

    # ---------- ferraduras-faísca: flutuam, giram como moeda (achatam em x), balançam e soltam brilho e rastro
    fer = []
    for k in range(NF):
        x0, y0, x1, y1 = info[f"ferradura_{k}"]
        g4 = C.conceito_para_4x(f"{rec}/ferradura_{k}.png", TELA)
        ys, xs = np.where(g4[..., 3] > 0)
        spr = np.ascontiguousarray(g4[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
        gx, gy = TELA.conceito_para_jogo((x0 + x1) / 2, (y0 + y1) / 2)
        fer.append(dict(spr=spr, x=gx, y=gy, ph=1.7 * k, sent=1 if k % 2 == 0 else -1, ax=4.0 + k % 3, ay=5.0 + (k * 2) % 3))

    def fer_pos(d, f):
        w = 2 * math.pi * f / NPART
        return (d["x"] + d["ax"] * math.sin(w + d["ph"]) + 1.5 * math.sin(2 * w + 2 * d["ph"]),
                d["y"] + d["ay"] * math.sin(w + d["ph"] + 1.3) + 1.5 * math.sin(3 * w + d["ph"]))

    def fer_carimbo(d, f):
        w = 2 * math.pi * f / NPART
        gira = math.cos(2 * w * d["sent"] + d["ph"]); sx = math.copysign(max(abs(gira), 0.24), gira)
        ang = 0.5 * math.sin(2 * w + d["ph"] * 1.3) + 0.25 * math.sin(3 * w + d["ph"])
        spr = d["spr"]; h, w_ = spr.shape[:2]; Tm = int(math.hypot(h, w_) * FER_ESC) + 8; Tm += (-Tm) % AMP
        c_, s_ = math.cos(ang), math.sin(ang)
        A = np.array([[c_ * sx, -s_], [s_ * sx, c_]]) * FER_ESC
        t = np.array([Tm / 2, Tm / 2]) - A @ np.array([w_ / 2, h / 2])
        im4 = cv2.warpAffine(spr, np.hstack([A, t[:, None]]).astype(np.float32), (Tm, Tm), flags=cv2.INTER_NEAREST, borderValue=0)
        return pal.encaixa(*C.reduz(im4, AMP)), gira

    ferraduras = []
    for f in range(NPART):
        L = np.full((CH, CW), -1, np.int16)
        for k, d in enumerate(fer):
            for atras_, cor in ((9, MEDIO), (6, VIVO), (3, ROSA)):         # rastro de faísca por onde ela passou
                px, py = fer_pos(d, f - atras_)
                C.ponto(L, int(round(px + 2 * math.sin(0.9 * f + k))), int(round(py + 5)), cor)
            idx, gira = fer_carimbo(d, f)
            x, y = fer_pos(d, f)
            C.carimba(L, idx, x, y)
            if abs(gira) > 0.86:                                           # de frente: brilho de 4 pontas num canto
                bx, by = int(round(x + 4 * (1 if gira > 0 else -1))), int(round(y - 5)); s = 2 if abs(gira) > 0.95 else 1
                for t in range(-s, s + 1):
                    C.ponto(L, bx + t, by, BR if t == 0 else ROSA); C.ponto(L, bx, by + t, BR if t == 0 else ROSA)
        ferraduras.append(L)

    # ---------- vapor do nariz (À FRENTE do corpo): dois bufos fortes por laço e um fio de respiração entre eles.
    # Cada baforada é um gomo sombreado (claro em cima, rosa embaixo); juntas formam um penacho que abre e se desfaz
    nxg, nyg = TELA.conceito_para_jogo(*NARINA)
    vap = []
    for j in (0, 1):
        for q in range(12):
            vap.append(dict(b=int(48 * j + q * 1.5 + rng.integers(0, 2)), ang=rng.uniform(-0.10, 0.42), v0=rng.uniform(1.7, 2.5),
                            vida=int(rng.integers(16, 24)), cr=rng.uniform(0.17, 0.25), ph=rng.uniform(0, 6.28)))
        for q in range(7):
            vap.append(dict(b=int(48 * j + 19 + q * 4.2 + rng.integers(0, 3)), ang=rng.uniform(0.0, 0.5), v0=rng.uniform(0.8, 1.3),
                            vida=int(rng.integers(13, 18)), cr=rng.uniform(0.11, 0.16), ph=rng.uniform(0, 6.28)))

    def baforada(L, sd, a, f, i):
        dist = sd["v0"] * 8.5 * (1 - math.exp(-a / 7.0))
        x = nxg + 2 + math.cos(sd["ang"]) * dist + 0.6 * math.sin(0.5 * a + sd["ph"])
        y = nyg + 1 + math.sin(sd["ang"]) * dist - 0.016 * a * a
        r = 1.2 + sd["cr"] * a
        m = (XX - x) ** 2 + ((YY - y) * 1.12) ** 2 <= r * r
        fim = sd["vida"] - a
        if fim < 7:                                              # desfaz comida pelo ruído
            m &= R1[(YY + 2 * f) % 96, (XX + 7 * i) % 96] > (7 - fim) / 7.5
        luz = ((XX - x) * 0.4 + (YY - y)) / r                    # luz de cima e da esquerda
        L[m] = BR if fim >= 4 else ROSA2
        L[m & (luz > 0.18)] = ROSA2 if fim >= 4 else ROSA3
        L[m & (luz > 0.62)] = ROSA3
        return bool(m.any())

    vapor = []; vv = []
    for f in range(NPART):
        L = np.full((CH, CW), -1, np.int16)
        vv.append(C.emite(L, f, NPART, vap, baforada))
        m = L >= 0; b = np.zeros_like(m)                         # contorno por FORA, embaixo e dos lados (em cima fica livre)
        b[1:] |= m[:-1]; b[:, 1:] |= m[:, :-1]; b[:, :-1] |= m[:, 1:]
        L[b & ~m] = FUNDO
        vapor.append(L)
    print("VAPOR baforadas por quadro:", min(vv), "a", max(vv), "| px:", min(int((v >= 0).sum()) for v in vapor), "a",
          max(int((v >= 0).sum()) for v in vapor))

    # ---------- saída: camadas NA ORDEM DE DESENHO
    CAM = {"crateras": crateras, "garanhao": garanhao, "raios": raios, "ferraduras": ferraduras, "vapor": vapor}
    PLANO = {"crateras": "atras", "garanhao": "atras", "raios": "atras", "ferraduras": "atras", "vapor": "frente"}
    C.exporta_camadas(cam, CAM, pal)
    C.escreve_aura_json(cam, ID, AURA, TELA, TIQ, [
        dict(nome="crateras", quadros=NPART, plano="atras", o_que="duas crateras de casco em brasa pulsando embaixo dos cascos do Gutto, com fagulhas"),
        dict(nome="garanhao", quadros=N, plano="atras", o_que="o cavalo de raio empinando, coice alternado, cabeça sacudindo, crina chicoteando "
                                                              "(o tronco atrás do corpo é remendo)"),
        dict(nome="raios", quadros=NPART, plano="atras", o_que="raios em zigue-zague que saem das juntas do cavalo, piscam e se refazem; faíscas de 4 pontas"),
        dict(nome="ferraduras", quadros=NPART, plano="atras", o_que="quatro ferraduras-faísca flutuando e girando"),
        dict(nome="vapor", quadros=NPART, plano="frente", o_que="jato de vapor branco do nariz; ancorado na narina da pose parada",
             ancora=[round(nxg, 1), round(nyg, 1)]),
    ], pal, extras=dict(
        nota="O pé do lutador fica em 'pe'; cada PNG tem o tamanho de 'tela'. Cada camada roda no seu laço "
             "(quadro = (tique // tiques_por_quadro) % quadros). O vapor é a única camada à frente do corpo e sai da narina "
             "da pose parada ('ancora'): em golpe ou pulo ele precisa seguir a cabeça ou ser desligado.",
        gerado_por="ferramentas/aura_blender/gutto_aura.py"))

    # ---------- corpo (vista 1, sem o vapor desenhado) no tamanho do jogo: só para o vídeo e as tiras
    c_rgb, c_m = C.reduz(C.conceito_para_4x(f"{rec}/corpo_v1.png", TELA, dx=info["DX"]), AMP)
    cq = Image.fromarray(np.clip(c_rgb, 0, 255).astype(np.uint8)).quantize(15, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    corpo = np.dstack([np.array(cq), (c_m * 255).astype(np.uint8)]); corpo[~c_m] = 0
    Image.fromarray(corpo).save(f"{pasta}/corpo_previa.png")
    ys, xs = np.where(c_m); hc = int(ys.max() - ys.min() + 1); wc = int(xs.max() - xs.min() + 1)
    fundo = C.fundo_teste(TELA)
    atras = [CAM[n] for n in CAM if PLANO[n] == "atras"]; frente = [CAM[n] for n in CAM if PLANO[n] == "frente"]
    NOVOS = [C.compoe(fundo, f, atras, corpo, frente, pal) for f in range(NPART)]

    # ---------- medidas
    med = {"quadros_garanhao": N, "quadros_outras_camadas": NPART, "tiques_por_quadro": TIQ, "duracao_do_ciclo_s": N * TIQ / 60}
    med.update(C.mede_conjunto(CAM, pal, NPART))
    for nome, lst in list(CAM.items()) + [("garanhao_sem_efeito", seco)]:
        med[nome] = C.mede_camada(lst, pal)
    dn = [float(np.abs(NOVOS[f].astype(int) - NOVOS[(f + 1) % NPART].astype(int)).mean()) for f in range(NPART)]
    med["composto_dif_min_max_emenda"] = [round(min(dn), 3), round(max(dn), 3), round(dn[-1], 3)]
    med["composto_pares_iguais"] = int(sum((NOVOS[f] == NOVOS[(f + 1) % NPART]).all() for f in range(NPART)))
    A0 = [a >= 0 for a in seco]
    larg = [int(np.where(a.any(0))[0].max() - np.where(a.any(0))[0].min() + 1) for a in A0]
    alt = [int(np.where(a.any(1))[0].max() - np.where(a.any(1))[0].min() + 1) for a in A0]
    topo = [int(np.where(a.any(1))[0].min()) for a in A0]
    med["corpo_px_larg_alt"] = [wc, hc]
    med["garanhao_px_larg_min_max"] = [min(larg), max(larg)]; med["garanhao_px_alt_min_max"] = [min(alt), max(alt)]
    med["garanhao_topo_y_min_max"] = [min(topo), max(topo)]
    med["garanhao_x_min_max"] = [int(min(np.where(a.any(0))[0].min() for a in A0)), int(max(np.where(a.any(0))[0].max() for a in A0))]
    med["topo_do_cavalo_acima_do_pe_sobre_altura_do_corpo"] = [round((TELA.pe[1] - max(topo)) / hc, 2), round((TELA.pe[1] - min(topo)) / hc, 2)]
    med["largura_do_cavalo_sobre_altura_do_corpo"] = [round(min(larg) / hc, 2), round(max(larg) / hc, 2)]
    sil = np.stack(A0); med["garanhao_pixels_sempre_opacos_frac"] = round(float(sil.all(0).sum() / sil.any(0).sum()), 3)
    med["raios_vivos_min_max"] = [min(viv), max(viv)]; med["baforadas_min_max"] = [min(vv), max(vv)]
    med["raios_px_min_max"] = [min(int((r >= 0).sum()) for r in raios), max(int((r >= 0).sum()) for r in raios)]
    med["vapor_px_min_max"] = [min(int((v >= 0).sum()) for v in vapor), max(int((v >= 0).sum()) for v in vapor)]
    med["y_min_por_camada"] = {nm: int(min(np.where((q >= 0).any(1))[0].min() for q in lst if (q >= 0).any())) for nm, lst in CAM.items()}
    med["quadros_sem_raio_nem_faisca"] = int(sum(not (r >= 0).any() for r in raios))
    med["escala_px_jogo_por_px_conceito"] = round(TELA.escala, 4); med["reducao_para_caber"] = "nenhuma"; med["ferradura_ampliada"] = FER_ESC
    med["tempo_render_blender_s"] = round(PT["tempo_render"], 1)
    med["chicote"] = chicote(pasta, mostra=False)
    med["passo_max_px"] = max(v["passo_max"] for v in med["chicote"].values())
    json.dump(med, open(f"{pasta}/medidas.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in med.items() if k != "chicote"}))

    # ---------- tiras (olhar com os olhos) e vídeo
    X0, X1 = 50, 310
    C.tira([NOVOS[f][:, X0:X1] for f in range(16)], f"{pasta}/tira.png", rotulos=[f"q{f:02d}" for f in range(16)])          # 16 consecutivos
    C.tira([NOVOS[f][:, X0:X1] for f in range(0, N, 3)], f"{pasta}/tira_ciclo.png", rotulos=[f"q{f:02d}" for f in range(0, N, 3)])
    C.tira([NOVOS[f][2:122, 185:305] for f in range(8)], f"{pasta}/tira_zoom_cabeca.png", cols=4, esc=4, rotulos=[f"q{f:02d}" for f in range(8)])
    C.tira([NOVOS[f][2:122, 55:205] for f in range(20, 28)], f"{pasta}/tira_zoom_crina.png", cols=4, esc=4, rotulos=[f"q{f:02d}" for f in range(20, 28)])
    C.tira([NOVOS[f][96:198, 96:276] for f in range(0, 16, 2)], f"{pasta}/tira_zoom_chao.png", cols=4, esc=4, rotulos=[f"q{f:02d}" for f in range(0, 16, 2)])
    sem = [C.compoe(fundo, f, atras, None, frente, pal) for f in (0, 12, 24, 36)]
    C.tira([s[:, X0:X1] for s in sem], f"{pasta}/tira_sem_corpo.png", cols=2, esc=3)                 # os remendos aparecem aqui
    C.video_laco(f"{pasta}/aura_gutto.mp4", NOVOS, TIQ)
    print("OK")


def instala(pasta):
    C.instala(os.path.join(pasta, "camadas"), DESTINO)


if __name__ == "__main__":
    import tempfile
    C.roda(__file__, {"recortes": recortes, "rig": rig, "chicote": chicote, "compor": compor, "instala": instala}, os.path.join(tempfile.gettempdir(), "aura_blender", ID))
