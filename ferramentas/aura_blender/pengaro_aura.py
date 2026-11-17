"""Aura do Pengaró despertado (endiabrado): COLUNA DE FUMAÇA violeta-preta, chicotes de sombra, anel de chão rachado
girando, elos de corrente partida e pedras flutuando. Método do Blender (docs/arcade/aura_blender.md).

    python ferramentas/aura_blender/pengaro_aura.py <pasta de trabalho>                  # tudo, na ordem
    python ferramentas/aura_blender/pengaro_aura.py <pasta de trabalho> pontos chicote   # só o movimento (1 s)
    etapas: recortes, rig (Blender), chicote, compor, instala (copia para sprites/pengaro/aura/)

O que é desta aura e não está no comum.py:
  - aura FRIA (roxa sobre fundo magenta): nada de `derrame_quente`; a chave é a `chave_magenta` e a casca rosada sai
    com `derrame_de_borda`;
  - a fumaça é UMA massa só no desenho: o miolo (coluna) fica numa malha com espinha vertical + ramos de base; o que
    sai do miolo vira chicote (uma malha por chicote, com uma faixa de sobra por cima da coluna para não abrir fresta);
  - o corpo tapava a coluna inteira: o buraco é remendado clonando a fumaça de cima e fica atrás do corpo;
  - o chão é desprojetado para vista de cima e girado no Blender como disco deitado (elipse em perspectiva);
  - a coluna "sobe": depois do render, o miolo é reamostrado de baixo para cima em duas fases (fluxo), em índices
    da paleta, sem cor nova.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import comum as C

ID = "pengaro"
AURA = "coluna_de_fumaca"
SRC = os.path.join(C.RAIZ, "sprites", ID, "quadros", "folhas_arcade", "e_conceito.png")
DESTINO = os.path.join(C.RAIZ, "sprites", ID, "aura")
# conceito: vista 1 (só o corpo) nas colunas 40..520; vista 3 (corpo + aura) nas colunas 1040..1840
V1 = (40, 520)
V3 = (1040, 1840)
X0 = 1020                                   # as medidas abaixo foram lidas num recorte que começa na coluna 1020
TELA = C.Tela(cx=X0 + 422.0, chao=690.0, escala=112 / 488.0)   # eixo entre os pés e sola na vista 3; corpo de 488 px vira 112
N = 48                                      # laço da coluna e dos chicotes
N2 = 96                                     # laço do anel, das pedras e das línguas soltas
TIQ = 2

# ---------------------------------------------------------------------------------------------------------- recortes
# chão rachado: elipse (centro, raios) em px do conceito
CHAO = dict(cx=X0 + 410.0, cy=669.0, rx=384.0, ry=46.0)
# miolo da fumaça (coluna): meia largura em função do y, em torno do eixo; fora dele a fumaça é chicote
EIXO_X = X0 + 440


def meia_largura(y, lado):
    """lado -1 = esquerda do eixo, +1 = direita (a massa do desenho não é simétrica)."""
    return np.where(lado < 0, np.interp(y, [0, 380, 560, 724], [212, 212, 430, 430]), np.interp(y, [0, 380, 560, 724], [195, 195, 430, 430]))


# pedras e elos soltos: (nome, x0, y0, x1, y1) no recorte (somar X0)
PEDRAS = [("pedra01", 70, 130, 147, 215), ("pedra02", 220, 33, 262, 77), ("pedra03", 57, 223, 87, 258), ("pedra04", 129, 252, 173, 303),
          ("pedra05", 33, 416, 85, 490), ("pedra06", 607, 88, 653, 140), ("pedra07", 596, 211, 637, 255), ("pedra08", 754, 344, 795, 388),
          ("pedra09", 597, 477, 641, 519), ("pedra10", 699, 442, 731, 472), ("pedra11", 707, 372, 740, 400), ("pedra12", 143, 546, 188, 593),
          ("pedra13", 36, 518, 65, 544), ("pedra14", 84, 493, 111, 525), ("pedra16", 560, 20, 630, 88)]
MIOLO_ACESO = (150, 40, 225)
ELOS = [("elo1", 165, 143, 240, 240), ("elo2", 170, 272, 237, 365), ("elo3", 655, 133, 757, 215), ("elo4", 607, 262, 677, 340)]

# ------------------------------------------------------------------------------------------------------------- ossos
# chicotes: polilinha da raiz (junto do miolo) à ponta, no recorte (somar X0)
CHICOTES = {
    "ea": [(300, 178), (245, 155), (195, 128), (162, 90), (160, 50), (200, 18), (245, 8)],        # esquerda alto
    "eb": [(250, 345), (205, 318), (150, 290), (95, 290), (50, 318), (35, 360)],                  # esquerda meio
    "ec": [(225, 470), (180, 440), (135, 420), (100, 400)],                                       # esquerda baixo
    "da": [(600, 178), (680, 185), (735, 215), (772, 265), (785, 320), (765, 370), (720, 400)],   # direita, arco grande
    "db": [(660, 470), (715, 430), (765, 425), (800, 450), (790, 480)],                           # direita meio
    "dc": [(600, 95), (640, 60), (680, 40), (690, 15)],                                           # direita alto
}
# espinha da coluna (de baixo para cima) e ramos da base, no recorte (somar X0)
ESPINHA = [("s1", None, (440, 650), (440, 560)), ("s2", "s1", (440, 560), (440, 470)), ("s3", "s2", (440, 470), (440, 380)),
           ("s4", "s3", (440, 380), (440, 290)), ("s5", "s4", (440, 290), (435, 200)), ("s6", "s5", (435, 200), (430, 120)),
           ("s7", "s6", (430, 120), (425, 55)), ("s8", "s7", (425, 55), (420, 0)),
           ("be1", "s1", (330, 620), (200, 600)), ("be2", "be1", (200, 600), (100, 585)), ("be3", "be2", (100, 585), (35, 560)),
           ("bd1", "s1", (540, 620), (660, 600)), ("bd2", "bd1", (660, 600), (740, 585)), ("bd3", "bd2", (740, 585), (800, 555))]


def _roxo(im, dr=35, dg=60):
    R, G, B = C.canais(im)
    return (B > R + dr) & (B > G + dg)


def brilho_comido(im, fg):
    """O violeta vivo do desenho (clarões dentro da fumaça, halo em volta do corpo, rachaduras do chão) tem R e B altos
    e G baixo: a chave de magenta levava junto e a aura saía escura, com furos, e o chão sem rachadura. Fundo é só o
    magenta PURO; o que a chave tirou e não é puro é brilho, menos a franja de 3 px em volta do fundo (mistura de
    borda, R quase igual a B). Devolve (máscara do brilho, imagem com o brilho puxado do rosa para o violeta)."""
    from scipy import ndimage as ndi
    R, G, B = [im[..., i].astype(int) for i in range(3)]
    puro = ~fg & (R > 225) & (B > 225) & (G < 32)
    franja = ndi.binary_dilation(puro, iterations=3) & (B - R < 25) & (G < 45)
    br = ~fg & ~puro & ~franja
    br[:, :V3[0]] = False; br[:, V3[1]:] = False
    lab, comps = C.componentes(br)
    viz = ndi.binary_dilation(fg, iterations=2)
    for c in comps:                                     # farelo, e ilha de brilho que não encosta em desenho nenhum
        if c["area"] < 6 or not (viz & (lab == c["i"])).any():
            br[lab == c["i"]] = False
    im2 = im.copy()
    im2[..., 0] = np.where(br, np.clip(R - 0.22 * (R - G), 0, 255), R).astype(np.uint8)
    return br, im2


def topo_em_lobos(coluna, YY, XX, semente=7):
    """O desenho encosta na borda de cima da folha (corte reto), então o topo da coluna tem de ser inventado. Em vez
    de serrilhado regular, a borda é uma fila de LOBOS desiguais como as escamas de fumaça do próprio desenho: cada um
    com largura, altura e tombo próprios (sorteio fixo), os vales entre eles em alturas diferentes."""
    r = np.random.default_rng(semente)
    H, W = coluna.shape
    xs = np.where(coluna.any(0))[0]; x = float(xs.min()) - 10
    y = YY.astype(np.float32); env = np.full((H, W), 1e9, np.float32)
    while x < xs.max() + 10:
        raio = float(r.uniform(15, 34)); topo = float(r.uniform(4, 44)); tombo = float(r.uniform(-0.5, 0.5))
        cx = x + raio * 0.8; cy = topo + raio
        d = (XX - cx - tombo * (cy - y)) / raio                     # o lobo tomba para um lado conforme sobe
        dentro = np.abs(d) < 1
        borda = cy - raio * np.sqrt(np.clip(1 - d * d, 0, 1))        # arco de cima do lobo
        env = np.where(dentro, np.minimum(env, borda), env)
        x += raio * float(r.uniform(1.0, 1.5))
    vale = 52 + 10 * np.sin(XX / 47.0 + 1.1)                          # onde nenhum lobo cobre
    return coluna & (y >= np.minimum(env, vale))


def recortes(pasta):
    from scipy import ndimage as ndi
    from PIL import Image
    import cv2
    rec = os.path.join(pasta, "recortes"); os.makedirs(rec, exist_ok=True)
    im = C.le_rgb(SRC); H, W = im.shape[:2]
    fg = C.chave_magenta(im)
    brilho, im_b = brilho_comido(im, fg)
    print("brilho devolvido ao desenho (px):", int(brilho.sum()))
    YY, XX = np.mgrid[0:H, 0:W]
    # --- corpo: a vista 1 inteira (o recorta_corpo do comum perdia o pé de trás, preso só pela tornozeleira)
    corpo = np.zeros_like(fg); corpo[:, V1[0]:V1[1]] = fg[:, V1[0]:V1[1]]
    lab, comps = C.componentes(corpo)
    for c in comps:
        if c["area"] < 40:
            corpo[lab == c["i"]] = False
    corpo = ndi.binary_erosion(corpo, iterations=1)
    corpo &= ~C.derrame_de_borda(corpo, im)
    C.salva_rgba(f"{rec}/corpo.png", im, corpo)
    dx, dy, nota = C.casa_corpo(im, corpo, *V3)
    print("corpo casado na vista 3: dx", dx, "dy", dy, "nota", round(nota, 3))
    c3 = C.desloca(corpo, dx, dy); c3d = ndi.binary_dilation(c3, iterations=6)
    # --- tudo que é aura na vista 3
    aura = fg.copy(); aura[:, :V3[0]] = False; aura[:, V3[1]:] = False
    aura &= ~c3d
    aura &= ~C.derrame_de_borda(aura, im, largura=2)
    aura = ndi.binary_opening(aura, iterations=1)
    aura |= brilho & ~c3d                               # depois da limpeza de borda: o brilho já foi triado por cor
    im = im_b
    # --- pedras e elos: sprite solto de cada um; o buraco que deixam na fumaça é remendado
    objetos = np.zeros_like(aura); lista = []
    labA, compsA = C.componentes(aura)
    naoroxo = aura & ~_roxo(im)
    for nome, x0, y0, x1, y1 in PEDRAS + ELOS:
        x0 += X0; x1 += X0
        cx_ = np.zeros_like(aura); cx_[y0:y1, x0:x1] = True
        soltos = [c for c in compsA if c["x0"] >= x0 - 4 and c["x1"] <= x1 + 4 and c["y0"] >= y0 - 4 and c["y1"] <= y1 + 4 and c["area"] > 150]
        if soltos and nome.startswith("pedra"):
            m = np.isin(labA, [c["i"] for c in soltos]); colado = False
        else:                                           # encostado na fumaça: separa pela cor (pedra e ferro não são roxo vivo)
            m = ndi.binary_opening(naoroxo & cx_, iterations=1)
            l2, c2 = C.componentes(m)
            m = np.isin(l2, [c["i"] for c in c2 if c["area"] > 60])
            m = ndi.binary_closing(m, iterations=3) & cx_ & aura
            m = C.maior_componente(m, conect=8)                    # o resto é fumaça escura que passou pela cor
            if nome.startswith("pedra"):                           # espigão de fumaça grudado na pedra: abre e fica o maior
                m = ndi.binary_fill_holes(m) & aura
                m = C.maior_componente(ndi.binary_opening(m, iterations=4), conect=8)
            colado = True
        if m.sum() < 80:
            print("  objeto vazio:", nome); continue
        bx = C.caixa(m)
        C.salva_rgba(f"{rec}/{nome}.png", im, m)                    # tela cheia: o Blender usa a resolução do conceito
        lista.append(dict(nome=nome, bbox=bx, centro=[(bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2], area=int(m.sum()), colado=colado))
        objetos |= m
    obj_d = ndi.binary_dilation(objetos, iterations=2)
    # --- chão: o que está dentro da elipse
    e = CHAO
    no_chao = ((XX - e["cx"]) / e["rx"]) ** 2 + ((YY - e["cy"]) / e["ry"]) ** 2 <= 1.0
    # --- fumaça = aura sem objetos e sem chão; buracos dos objetos colados e do corpo são remendo
    fum = aura & ~obj_d & ~(no_chao & (YY > e["cy"] - 10))
    fum[int(e["cy"] + 6):] = False
    lab, comps = C.componentes(fum)
    for c in comps:
        if c["area"] < 150:
            fum[lab == c["i"]] = False
    rgb = im.copy()
    fecho = ndi.binary_closing(fum, iterations=12)
    bur_obj = obj_d & fecho & ~fum                                  # onde pedra/elo tapava fumaça
    C.remenda_vizinho(rgb, fum, bur_obj)
    fum1 = fum | bur_obj
    # buraco do corpo: 10 px menor que o corpo onde ele sai da fumaça (o remendo nunca aparece em volta dele)
    base = np.pad(fum1 | ndi.binary_erosion(c3d, iterations=16), 30)
    sil = ndi.binary_closing(base, iterations=24)[30:-30, 30:-30]
    perto = ndi.binary_dilation(c3, iterations=14)
    bur = sil & perto & ~fum1
    bur |= ndi.binary_fill_holes(fum1 | bur) & perto & ~fum1        # o fecho em losango deixa ilhas: tapa
    bur[int(e["cy"] - 4):] = False
    full = rgb.copy()
    falta = C.remenda_clone(full, rgb, fum1, bur, (-215, 0), vezes=2)   # clona a fumaça de cima da cabeça
    falta2 = C.remenda_clone(full, rgb, fum1, falta, (0, -230), vezes=1)
    falta3 = C.remenda_clone(full, rgb, fum1, falta2, (0, 230), vezes=1)
    C.remenda_vizinho(full, (fum1 | bur) & ~falta3, falta3)
    # o remendo fica atrás do corpo e é rodeado pelo halo vivo do desenho: clareado para o violeta, vira miolo aceso
    # da coluna em vez de deixar o fantasma da pose (anel claro em volta de um vão escuro) quando o corpo sai dali
    full[bur] = np.clip(full[bur] + (np.array(MIOLO_ACESO) - full[bur]) * 0.42, 0, 255).astype(np.uint8)
    tudo = fum1 | bur
    print("fumaça px", int(tudo.sum()), "remendo do corpo", int(bur.sum()), "sem fonte", int(falta3.sum()), "buraco de objetos", int(bur_obj.sum()))
    # --- miolo (coluna) x chicotes
    miolo_reg = np.abs(XX - EIXO_X) <= meia_largura(YY, np.sign(XX - EIXO_X))
    fora = tudo & ~miolo_reg
    labF, compsF = C.componentes(fora)
    segs = {k: [((a[0] + X0, a[1]), (b[0] + X0, b[1])) for a, b in zip(pts, pts[1:])] for k, pts in CHICOTES.items()}
    nomes = list(CHICOTES)
    pecas = {k: np.zeros_like(tudo) for k in nomes}
    toca_miolo = ndi.binary_dilation(tudo & miolo_reg, iterations=4)
    for c in compsF:
        if c["area"] < 60:
            continue
        if c["area"] < 3000 and not (toca_miolo & (labF == c["i"])).any():
            # mecha que no desenho já se soltou da fumaça: presa a um osso ela flutuava como lasca rígida, sem ligação
            # com a coluna. Sai do recorte; quem faz esse papel são os fiapos, que nascem nas pontas e sobem sumindo.
            print("  mecha solta fora do recorte:", c["area"], "px em", (c["x0"] - X0, c["y0"]))
            continue
        ys, xs = np.where(labF == c["i"]); P = np.stack([xs, ys], 1)[:: max(1, len(xs) // 400)]
        d = [C.dist_segmentos(P, segs[k]).min(1).mean() for k in nomes]
        pecas[nomes[int(np.argmin(d))]] |= labF == c["i"]
    info = dict(dx=dx, dy=dy, nota=nota, objetos=lista, chicotes={})
    arqs = []
    coluna = tudo & miolo_reg
    coluna = topo_em_lobos(coluna, YY, XX)
    for k in nomes:
        m = pecas[k]
        if m.sum() == 0:
            print("  chicote vazio:", k); continue
        # sobra para dentro do miolo: 28 px de dilatação geodésica (a raiz do chicote fica por cima da coluna)
        raiz = ndi.binary_dilation(m, iterations=28, mask=tudo) & miolo_reg
        pm = m | raiz
        C.salva_rgba(f"{rec}/chicote_{k}.png", full, pm); arqs.append(f"{rec}/chicote_{k}.png")
        info["chicotes"][k] = dict(bbox=C.caixa(pm), area=int(pm.sum()), sobra=int(raiz.sum()))
    C.salva_rgba(f"{rec}/coluna.png", full, coluna)
    info["coluna_bbox"] = C.caixa(coluna)
    # --- chão: o próprio desenho, de frente (as rachaduras acesas voltaram com o brilho). O que o corpo e as pedras
    # tapavam é remendo com a cor vizinha e fica atrás dos pés.
    piso = aura & no_chao & ~ndi.binary_dilation(objetos, iterations=3)
    tapado = ndi.binary_fill_holes(ndi.binary_closing(piso | (c3d & no_chao), iterations=3)) & no_chao & ~piso
    chao_rgb = im.copy()
    esq = tapado & (XX < e["cx"]); dir_ = tapado & (XX >= e["cx"])   # cada pé copia as lajes limpas do vão entre os dois
    falta = C.remenda_clone(chao_rgb, im, piso, esq, (0, 135), vezes=1) | C.remenda_clone(chao_rgb, im, piso, dir_, (0, -135), vezes=1)
    falta = C.remenda_clone(chao_rgb, im, piso, falta, (28, 0), vezes=2)
    C.remenda_vizinho(chao_rgb, (piso | tapado) & ~falta, falta)
    C.salva_rgba(f"{rec}/chao_frente.png", chao_rgb, piso | tapado)
    info["chao"] = dict(e, remendo=int(tapado.sum()), remendo_sem_fonte=int(falta.sum()))
    json.dump(info, open(f"{rec}/info.json", "w"), indent=1)
    print({k: (v if not isinstance(v, (list, dict)) else len(v)) for k, v in info.items()})
    # --- prévias para OLHAR
    box = (X0, 0, X0 + 840, H)
    C.previa_recortes([f"{rec}/coluna.png"], f"{pasta}/p_coluna.png", box, (H, W))
    C.previa_recortes(arqs, f"{pasta}/p_chicotes.png", box, (H, W))
    cores = [(255, 80, 80), (80, 255, 80), (80, 160, 255), (255, 255, 80), (255, 80, 255), (80, 255, 255), (255, 160, 60), (200, 200, 200)]
    p = np.full((H, W, 3), 60, np.uint8); p[coluna] = (110, 60, 150); p[bur] = (60, 30, 90)
    for i, k in enumerate(nomes):
        p[pecas[k]] = cores[i % len(cores)]
        for a, b in segs[k]:
            cv2.line(p, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), (255, 255, 255), 2)
    p[objetos] = (240, 240, 240); p[piso] = (150, 110, 60)
    for _, _, (x_, y_), (x2, y2) in ESPINHA:
        cv2.line(p, (int(x_ + X0), int(y_)), (int(x2 + X0), int(y2)), (0, 0, 0), 2)
    Image.fromarray(p[:, box[0]:box[2]]).save(f"{pasta}/p_rotulos.png")
    fl = np.full((110, 110 * len(lista), 3), 70, np.uint8)          # folha dos objetos
    for i, o in enumerate(lista):
        b_ = o["bbox"]; s = np.array(Image.open(f"{rec}/{o['nome']}.png"))[b_[1]:b_[3], b_[0]:b_[2]]; h, w = min(s.shape[0], 108), min(s.shape[1], 108)
        sub = fl[1:1 + h, i * 110 + 1:i * 110 + 1 + w]; mm = s[:h, :w, 3] > 0; sub[mm] = s[:h, :w, :3][mm]
    Image.fromarray(fl).save(f"{pasta}/p_objetos.png")
    C.previa_recortes([f"{rec}/chao_frente.png"], f"{pasta}/p_chao.png", box, (H, W))


# ------------------------------------------------------------------------------------------------------------ animação
# Espinha da coluna: onda em S que SOBE. Cada junta gira mais e mais tarde que a de baixo; como os atrasos somam quase
# uma volta inteira ao longo da cadeia, as rotações se cancelam em parte e a coluna serpenteia em vez de tombar.
ANIM_COLUNA = {"s1": (0.5, 0.00, 0.0, 0), "s2": (1.2, 0.10, 0.0, 0), "s3": (2.0, 0.21, 0.3, 0.5), "s4": (2.8, 0.32, 0.5, 1.0),
               "s5": (3.6, 0.44, 0.8, 1.5), "s6": (4.4, 0.56, 1.0, 2.0), "s7": (5.4, 0.68, 1.4, 2.5), "s8": (7.0, 0.80, 2.0, 3.0),
               "be1": (1.2, 0.05, 0.0, 0), "be2": (2.4, 0.18, 0.6, 0.4), "be3": (4.5, 0.32, 1.2, 0.4),
               "bd1": (-1.2, 0.30, 0.0, 0), "bd2": (-2.4, 0.43, 0.6, 1.9), "bd3": (-4.5, 0.57, 1.2, 1.9)}
TREMOR_COLUNA = [dict(eixo="X", raio=9.0, fase=0.0, forca=7.0), dict(eixo="Z", raio=11.0, fase=2.1, forca=5.0)]
TREMOR_CHICOTE = [dict(eixo="X", raio=8.0, fase=1.0, forca=4.0), dict(eixo="Z", raio=10.0, fase=3.3, forca=4.0)]
# chicote: (fase em quadros, sinal, amplitude da ponta em graus). A raiz gira pouco e cedo; a ponta muito e tarde.
CHAO_ARFA = 3.2                     # força do tremor vertical das lajes (px de jogo, pico a pico ~1,5)
ESCALA_PEDRA, ESCALA_ELO = 1.35, 1.5
MOV_CHICOTE = {"ea": (0, 1, 13.0), "eb": (17, -1, 12.0), "ec": (31, 1, 10.0), "da": (9, -1, 11.0), "db": (26, 1, 13.0), "dc": (40, -1, 12.0)}
# elos: cadeia de 3 ossos ao longo da corrente (no recorte, somar X0): a corrente balança mole enquanto flutua
OSSOS_ELO = {"elo1": [(228, 152), (205, 176), (186, 206), (181, 238)], "elo2": [(231, 279), (205, 296), (186, 326), (185, 362)],
             "elo3": [(661, 141), (700, 151), (730, 171), (752, 211)], "elo4": [(672, 268), (650, 291), (630, 316), (612, 338)]}


def _cadeia(nome, pts):
    return [(f"{nome}{i}", f"{nome}{i - 1}" if i else None, (a[0] + X0, a[1]), (b[0] + X0, b[1])) for i, (a, b) in enumerate(zip(pts, pts[1:]))]


def _anim_cadeia(nome, n_ossos, amp_ponta, atraso_total=0.42):
    """Amplitude e atraso crescendo da raiz à ponta (cascata): raiz ~12% da ponta, ponta chega `atraso_total` do ciclo depois."""
    d = {}
    for i in range(n_ossos):
        q = i / max(n_ossos - 1, 1)
        d[f"{nome}{i}"] = (amp_ponta * (0.12 + 0.88 * q ** 1.5), atraso_total * q, amp_ponta * 0.22 * q, 0.7 * i)
    return d


def _orbita(i):
    """Órbita lenta própria de cada pedra/elo: voltas por laço em x e em y, raios, fases, balanço e virada."""
    r = np.random.default_rng(100 + i)
    return dict(kx=int(r.integers(1, 3)), ky=int(r.integers(1, 4)), ax=float(r.uniform(1.5, 4.0)), az=float(r.uniform(3.0, 6.5)),
                fx=float(r.uniform(0, 6.28)), fz=float(r.uniform(0, 6.28)), giro=float(r.uniform(14, 30)) * (1 if i % 2 else -1),
                kg=int(r.integers(1, 3)), vira=float(r.uniform(20, 45)), kv=int(r.integers(1, 3)), fv=float(r.uniform(0, 6.28)))


def rig(pasta, so_pontos=False):
    """Roda DENTRO do Blender."""
    import bpy
    C.bl_cena(TELA, N2)
    rec = os.path.join(pasta, "recortes"); info = json.load(open(f"{rec}/info.json"))
    # --- coluna: espinha de 8 ossos + 2 ramos de base, tremor forte de fumaça, respiração na largura
    col = C.bl_malha_com_ossos("coluna", f"{rec}/coluna.png", [(n, p, (h[0] + X0, h[1]), (t[0] + X0, t[1])) for n, p, h, t in ESPINHA],
                               TELA, N, folga=6.0, pot=2, tremor=TREMOR_COLUNA, tremor_folga=0.0, tremor_rampa=6.0)
    C.bl_anima_juntas(col["arm"], ANIM_COLUNA, N)
    ox, oz = col["origem"]
    C.bl_anima_objeto(col["arm"], N, lambda t: dict(location=(ox + 0.8 * math.sin(t + 0.4), 0, oz),
                                                    scale=(1 + 0.035 * math.sin(t), 1, 1 + 0.02 * math.sin(t + 1.3))))
    # --- chicotes: uma malha por chicote, cadeia da raiz à ponta
    chic = {}
    for j, (k, pts) in enumerate(CHICOTES.items()):
        if k not in info["chicotes"]:
            continue
        fase, sinal, amp = MOV_CHICOTE[k]
        pc = C.bl_malha_com_ossos(k, f"{rec}/chicote_{k}.png", _cadeia(k, pts), TELA, N, folga=3.0, pot=3,
                                  prof=lambda X, Z, j=j: -1.0 - 0.6 * j, tremor=TREMOR_CHICOTE, tremor_folga=0.0, tremor_rampa=5.0)
        C.bl_anima_juntas(pc["arm"], _anim_cadeia(k, len(pts) - 1, amp), N, fase=fase, sinal=sinal)
        ox_, oz_ = pc["origem"]
        C.bl_anima_objeto(pc["arm"], N, lambda t, ox_=ox_, oz_=oz_, j=j: dict(location=(ox_ + 1.0 * math.sin(t + j), 0, oz_ + 1.2 * math.sin(t + 1.7 * j))),
                          fase=fase)
        chic[k] = pc
    # --- chão: o desenho de frente numa malha presa a um osso curto no centro. As lajes ARFAM (tremor vertical em laço,
    # nulo debaixo dos pés e cheio na borda) e o chão inteiro respira; a luz das rachaduras é camada do compor.
    e = info["chao"]
    ch = C.bl_malha_com_ossos("chao", f"{rec}/chao_frente.png", [("c0", None, (e["cx"] - 30, e["cy"]), (e["cx"] + 30, e["cy"]))], TELA, N2,
                              celula=6, margem=6, prof=lambda X, Z: 4.0,
                              tremor=[dict(eixo="Z", raio=13.0, fase=0.6, forca=CHAO_ARFA), dict(eixo="X", raio=10.0, fase=2.4, forca=CHAO_ARFA * 0.5)],
                              tremor_folga=2.0, tremor_rampa=30.0)
    cox, coz = ch["origem"]
    C.bl_anima_objeto(ch["arm"], N2, lambda t: dict(location=(cox, 0, coz + 0.5 * math.sin(2 * t)),
                                                    scale=(1 + 0.02 * math.sin(2 * t + 0.9), 1, 1 + 0.05 * math.sin(2 * t))))
    disco = ch["malha"]
    # --- pedras (placa rígida) e elos (malha com 3 ossos): cada um na sua órbita lenta, girando
    soltos = []
    for i, o in enumerate(info["objetos"]):
        orb = _orbita(i); nome = o["nome"]
        if nome in OSSOS_ELO:
            pc = C.bl_malha_com_ossos(nome, f"{rec}/{nome}.png", _cadeia(nome, OSSOS_ELO[nome]), TELA, N2, celula=4, margem=4, folga=1.0, pot=4)
            C.bl_anima_juntas(pc["arm"], _anim_cadeia(nome, 3, 16.0, 0.30), N2, fase=7 * i, sinal=1 if i % 2 else -1, harmonico=2)
            ob = pc["arm"]; cx_, cz_ = pc["origem"]; soltos.append(pc["malha"])
        else:
            ob, (cx_, cz_) = C.bl_placa(nome, f"{rec}/{nome}.png", o["bbox"], TELA); soltos.append(ob)

        def mov(t, orb=orb, cx_=cx_, cz_=cz_, i=i, placa=nome not in OSSOS_ELO):
            d = dict(location=(cx_ + orb["ax"] * math.sin(orb["kx"] * t + orb["fx"]), -6.0 - 0.3 * i, cz_ + orb["az"] * math.sin(orb["ky"] * t + orb["fz"])))
            gy = math.radians(orb["giro"]) * math.sin(orb["kg"] * t + orb["fx"])          # balanço no plano da tela
            gz = math.radians(orb["vira"]) * math.sin(orb["kv"] * t + orb["fv"]) if placa else 0.0   # vira de lado (encurta)
            d["rotation_euler"] = (0, gy, gz)
            k = ESCALA_PEDRA if placa else ESCALA_ELO      # no tamanho do jogo o desenho dava pedra de 4 px e elo de 2 px
            d["scale"] = (k, k, k)
            return d
        C.bl_anima_objeto(ob, N2, mov)

    def coleta(f):
        d = C.bl_pontas(col, TELA, "col")
        for k, pc in chic.items():
            d.update(C.bl_pontas(pc, TELA, k))
        return d
    for o in [disco] + soltos:               # bl_renderiza só esconde o que está nas passadas dele: o resto tem de sair antes
        o.hide_render = True
    C.bl_renderiza(pasta, N, {"coluna": [col["malha"]], "chicotes": [pc["malha"] for pc in chic.values()]}, coleta, so_pontos=so_pontos,
                   blend="rig.blend")
    if so_pontos:
        return
    # passada lenta (N2 quadros): chão e soltos
    cena = bpy.context.scene; todos = [col["malha"], disco] + [pc["malha"] for pc in chic.values()] + soltos
    for f in range(N2):
        cena.frame_set(f)
        for nome, objs in (("chao", [disco]), ("soltos", soltos)):
            for o in todos:
                o.hide_render = o not in objs
            cena.render.filepath = os.path.join(pasta, "render", f"{nome}_{f:02d}.png"); bpy.ops.render.render(write_still=True)
    print("PASSADA_LENTA ok")


def chicote(pasta, mostra=True):
    """Fase e passo de cada junta: fase crescendo da raiz para a ponta; passo máximo abaixo de ~3 px."""
    res = C.mede_pontos(json.load(open(f"{pasta}/render/pontos.json"))["pontos"], mostra=mostra)
    json.dump(res, open(f"{pasta}/chicote.json", "w"), indent=1)
    return res


# ------------------------------------------------------------------------------------------------------------- camadas
ESCURA = (20, 8, 30)                # contorno: o preto dos lutadores puxado para o violeta
Y_CORTE = 190                       # linha da sola: o anel acima dela fica atrás dos pés, dali para baixo fica à frente
N_FIAPOS, N_FAISCAS, N_SOMBRAS = 34, 30, 7


def _uniforme(R):
    """Ruído com distribuição plana 0..1 (para o limiar virar fração de área)."""
    o = np.empty(R.size); o[np.argsort(R, axis=None)] = np.arange(R.size) / R.size
    return o.reshape(R.shape)


def escorre(arq, f, n, tela, amp=2.2, y_base=186.0):
    """A fumaça ESCORRE para cima sem trocar de desenho: o quadro do Blender (4x) é amostrado com um deslocamento
    pequeno e liso que é uma soma de ondas viajando para cima (frentes inclinadas, cada uma para um lado). Feito em 4x
    e ANTES da redução: o desenho desliza em quartos de pixel, sem costura, sem fase que recomeça. O deslocamento some
    na base (a coluna não descola do chão). Devolve (rgb, máscara) em 1x, como C.le_render.
    Passo por quadro: amp * 2*pi/n por onda (0,29 px com amp 2,2 e n 48)."""
    import cv2
    im = cv2.imread(arq, cv2.IMREAD_UNCHANGED)
    k = tela.amp; H, W = im.shape[:2]; YY, XX = np.mgrid[0:H, 0:W].astype(np.float32); y, x = YY / k, XX / k
    t = 2 * np.pi * f / n
    g = np.clip((y_base - y) / 50.0, 0, 1)
    dy = amp * g * (np.sin(2 * np.pi * (y / 40.0 + x / 95.0) + t) + 0.5 * np.sin(2 * np.pi * (y / 27.0 - x / 60.0) + 2 * t + 1.9))
    dx = amp * g * (0.7 * np.sin(2 * np.pi * (y / 52.0 - x / 130.0) + t + 2.0) + 0.3 * np.sin(2 * np.pi * (y / 23.0 + x / 75.0) + 2 * t + 0.4))
    out = cv2.remap(im, (XX + dx * k).astype(np.float32), (YY + dy * k).astype(np.float32), cv2.INTER_NEAREST,
                    borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return C.reduz(out[..., [2, 1, 0, 3]], k)


def reduz_fino(arq, amp=4, lim=95.0, minimo=3):
    """Redução que não apaga risco fino aceso (rachadura de 1 px): se o bloco amp x amp tem pelo menos `minimo`
    subpixels claros (luminância > lim), a cor do pixel é a média só deles; senão é a média normal."""
    from PIL import Image
    a4 = np.array(Image.open(arq).convert("RGBA")); rgb, m = C.reduz(a4, amp)
    h, w = m.shape
    cl = (a4[..., 3] > 127) & ((a4[..., :3].astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)) > lim)
    n = cl.reshape(h, amp, w, amp).sum((1, 3))
    soma = (a4[..., :3].astype(np.float32) * cl[..., None]).reshape(h, amp, w, amp, 3).sum((1, 3))
    fino = m & (n >= minimo)
    rgb[fino] = soma[fino] / n[fino][:, None]
    return rgb, m


class Rampa:
    """Degraus de luz DENTRO do violeta: clarear ou escurecer um pixel anda pela lista das cores violeta da paleta
    (da mais escura à mais clara), nunca pelo índice cru, que passaria pelo marrom da pedra e pelo cinza do ferro."""

    def __init__(self, pal):
        c = pal.cores.astype(int)
        self.idx = np.array([i for i in range(1, pal.n) if c[i][2] > c[i][1] + 40 and c[i][2] >= c[i][0]])
        self.pos = np.full(pal.n + 1, -1); self.pos[self.idx] = np.arange(len(self.idx))

    def anda(self, L, mask, k, piso=0, teto=None):
        """Anda k degraus (k > 0 clareia até `teto`, k < 0 escurece até `piso`); quem já passou do limite fica."""
        p = self.pos[L]; m = mask & (L >= 0) & (p >= 0)
        teto = len(self.idx) - 1 if teto is None else teto
        if k > 0:
            L[m] = self.idx[np.maximum(p[m], np.minimum(p[m] + k, teto))]
        else:
            L[m] = self.idx[np.minimum(p[m], np.maximum(p[m] + k, piso))]
        return L


def contorno_de_fora(idx, cor, fecha=2, **kw):
    """Contorno escuro só na borda EXTERNA: furos pequenos do miolo são tapados antes de procurar a borda."""
    from scipy import ndimage as ndi
    m = idx >= 0
    cheio = ndi.binary_fill_holes(ndi.binary_closing(np.pad(m, 4), iterations=fecha))[4:-4, 4:-4] | m
    tmp = np.where(m, idx, np.where(cheio, 1, -1)).astype(np.int16)
    return np.where(m, C.contorno(tmp, cor, **kw), -1).astype(np.int16)


def _fitas(seed, n=96):
    """Ruído ladrilhável de fitas em pé (estreitas em x, compridas em y): o clarão sobe como língua, não como mancha."""
    r = np.random.default_rng(seed); y, x = np.mgrid[0:n, 0:n] / n; t = np.zeros((n, n))
    for _ in range(40):
        fx = int(r.integers(-7, 8)); fy = int(r.integers(-2, 3))
        if fx == 0:
            continue
        t += np.sin(2 * np.pi * (fx * x + fy * y) + r.uniform(0, 6.28)) / (1 + 0.2 * abs(fx))
    return (t - t.min()) / (t.max() - t.min())


def _bolha(L, x, y, r, c_corpo, c_luz, c_borda, achat=1.0, y_min=0, y_max=None):
    """Bolha de fumaça desenhada em 1x: disco achatado com borda escura embaixo e um ponto de luz em cima."""
    H, W = L.shape; y_max = H if y_max is None else y_max
    x0, x1 = int(x - r - 2), int(x + r + 3); y0, y1 = int(y - r - 2), int(y + r + 3)
    for yy in range(max(y0, y_min), min(y1, y_max)):
        for xx in range(max(x0, 0), min(x1, W)):
            d = math.hypot(xx - x, (yy - y) / achat)
            if d <= r:
                L[yy, xx] = c_borda if (d > r - 1.0 and yy > y and r >= 2.0) else c_corpo
    if r >= 1.6:
        C.ponto(L, int(round(x - r * 0.35)), int(round(y - r * 0.45 * achat)), c_luz, y_max)


def compor(pasta):
    from scipy import ndimage as ndi
    from PIL import Image
    rec = os.path.join(pasta, "recortes"); cam = os.path.join(pasta, "camadas")
    info = json.load(open(f"{rec}/info.json")); pontos = json.load(open(f"{pasta}/render/pontos.json"))["pontos"]
    rng = np.random.default_rng(11)
    vazio = lambda: np.full((TELA.ch, TELA.cw), -1, np.int16)
    # --- paleta: 14 cores do próprio desenho (fumaça, chão, pedra, ferro) + 1 escura de contorno
    def amostra(arq, vezes=1):
        r, m = C.reduz(C.conceito_para_4x(arq, TELA), TELA.amp)
        return [r[m]] * vezes
    am = amostra(f"{rec}/coluna.png") + amostra(f"{rec}/chao_frente.png", 3)
    for k in info["chicotes"]:
        am += amostra(f"{rec}/chicote_{k}.png")
    for o in info["objetos"]:
        am += amostra(f"{rec}/{o['nome']}.png", 6)                    # pedra e ferro são poucos pixels: pesam mais
    pal = C.Paleta.do_desenho(np.concatenate(am), n=14, escura=ESCURA)
    lilas = pal.mais_proxima((215, 170, 255)); viol = pal.mais_proxima((165, 60, 235)); roxo = pal.mais_proxima((100, 28, 160))
    breu = pal.mais_proxima((48, 14, 78))
    print("paleta", pal.lista(), "lilas", lilas, "viol", viol, "roxo", roxo, "breu", breu)
    RAMPA = [viol, viol, roxo, roxo, roxo, breu, breu, breu]         # língua de sombra: da base violeta à ponta de breu
    campo = C.Campo(TELA, 48); R2 = C.ladrilho(2, n=48, fmax=6); R3 = C.ladrilho(5, n=48, fmax=5)
    campo.fecha(N, 1, 2); campo.fecha(N2, 1, 2)
    campo96 = C.Campo(TELA, 96); campo96.fecha(N, 2)
    R1 = _uniforme(_fitas(1)); rv = Rampa(pal); p_viol = int(rv.pos[viol]); p_lilas = int(rv.pos[lilas])
    print("rampa violeta", [pal.cores[i].tolist() for i in rv.idx], "viol", p_viol, "lilas", p_lilas)

    def r_clarao(f):                                                   # fitas de luz subindo 2 px por quadro
        return campo96.rola(R1, f, vy=2)

    def r_lingua(f, ox=0):
        return 0.5 * campo.rola(R2, f, vy=2, ox=ox) + 0.5 * campo.rola(R3, f, vy=1, ox=17 + ox)

    # --- coluna: render -> 1x -> paleta com histerese -> farelo fora -> FLUXO para cima
    le = lambda nome, n: [C.le_render(f"{pasta}/render/{nome}_{f:02d}.png", TELA.amp) for f in range(n)]
    col_seca = [C.limpa(a, 10) for a in pal.encaixa_seq(le("coluna", N))]            # só para medir: sem escorrer
    col_flux = [C.limpa(a, 10) for a in pal.encaixa_seq([escorre(f"{pasta}/render/coluna_{f:02d}.png", f, N, TELA) for f in range(N)])]
    for f in range(N):                                                 # clarões: fitas que sobem acendendo o violeta por onde passam
        g = r_clarao(f)
        rv.anda(col_flux[f], g > 0.80, 1, teto=p_viol); rv.anda(col_flux[f], g > 0.93, 1, teto=p_viol)
        rv.anda(col_flux[f], g < 0.10, -1, piso=1)
    chi_seca = [C.limpa(a, 8) for a in pal.encaixa_seq(le("chicotes", N))]
    coluna, chicotes = [], []
    for f in range(N):
        c, w = col_flux[f], chi_seca[f]
        # contorno do chicote só onde ele faz borda com o vazio (a sobra em cima da coluna não ganha risco)
        w = w.copy(); g = r_clarao((f + 13) % N)                       # a mesma luz que sobe pela coluna passa pelos chicotes
        rv.anda(w, g > 0.78, 1, teto=p_viol); rv.anda(w, g < 0.14, -1, piso=1)
        u = np.where(w >= 0, w, c); cu = contorno_de_fora(u, pal.escura)
        w2 = np.where(w >= 0, cu, -1).astype(np.int16)
        wl = C.linguas(w2, r_lingua(f, 9), RAMPA, alt=4, forca=0.04)
        wl[(wl >= 0) & (w2 < 0) & (c >= 0)] = -1                       # língua do chicote não nasce por cima da coluna
        chicotes.append(wl)
        coluna.append(C.linguas(contorno_de_fora(c, pal.escura), r_lingua(f), RAMPA, alt=8, forca=0.10))
    # --- chão: lajes arfando (Blender) -> redução que guarda a rachadura fina -> paleta -> luz correndo pelas
    # rachaduras do centro para a borda (degraus dentro do violeta, sem estouro branco) -> sombras em órbita
    chao = [C.limpa(a, 6) for a in pal.encaixa_seq([reduz_fino(f"{pasta}/render/chao_{f:02d}.png", TELA.amp) for f in range(N2)], folga=200.0)]
    e = info["chao"]; ecx, ecy = TELA.conceito_para_jogo(e["cx"], e["cy"]); erx, ery = e["rx"] * TELA.escala, e["ry"] * TELA.escala
    YY, XX = TELA.grade(); dist = np.hypot(XX - ecx, (YY - ecy) * erx / ery)
    lum = pal.cores.astype(int) @ np.array([299, 587, 114]) / 1000.0
    claro_min = int(np.searchsorted(lum, 70))                          # dali para cima é rachadura/aresta acesa
    sombras = C.semeia(rng, N_SOMBRAS, dict(th=("uni", 0, math.pi), rr=("uni", 0.90, 1.06), r=("uni", 2.2, 3.6), fi=("uni", 0, 6.28)))
    anel_t, anel_f = [], []
    for f in range(N2):
        a = chao[f].copy()
        pulso = 0.5 + 0.5 * np.sin(2 * np.pi * (2 * f / N2) - dist / 13.0)   # onda de 82 px saindo do centro, 1,7 px por quadro
        racha = a >= claro_min
        rv.anda(a, racha & (pulso > 0.66), 1, teto=p_lilas)           # a crista acende a rachadura um degrau...
        rv.anda(a, racha & (pulso < 0.30), -1, piso=max(p_viol - 1, 0))   # ...e o vale apaga um, sem sair do violeta vivo
        rv.anda(a, ~racha & (pulso > 0.74), 1, teto=max(p_viol - 1, 0))   # a laje pega um reflexo quando a crista passa
        a = C.contorno(a, pal.escura)
        t, fr = vazio(), vazio()
        t[:Y_CORTE] = a[:Y_CORTE]; fr[Y_CORTE:] = a[Y_CORTE:]
        for s in sombras:                                              # pares opostos: meia volta fecha o laço
            for k in (0, 1):
                th = s["th"] + k * math.pi + math.pi * f / N2
                x = ecx + erx * s["rr"] * math.cos(th); y = ecy + ery * s["rr"] * math.sin(th)
                r = s["r"] + 0.9 * math.sin(2 * th + s["fi"])
                if math.sin(th) < 0:
                    _bolha(t, x, y - 1, r, breu, roxo, pal.escura, achat=0.75, y_max=Y_CORTE)
                else:
                    _bolha(fr, x, y - 1, r, breu, roxo, pal.escura, achat=0.75)
        anel_t.append(C.linguas(t, r_lingua(f, 23), RAMPA[2:], alt=5, forca=0.07))
        fl = C.linguas(fr, r_lingua(f, 31), RAMPA[2:], alt=3, forca=0.02)
        anel_f.append(fl)
    # --- pedras e elos (Blender) -> paleta (o contorno é o do próprio desenho: risco por cima comia os elos)
    soltos = [C.limpa(a, 4) for a in pal.encaixa_seq(le("soltos", N2), folga=300.0)]
    # --- fiapos: línguas que se SOLTAM do topo da coluna e das pontas dos chicotes e sobem encolhendo; faíscas lilás do chão
    pontas = ["col_s8", "col_s7", "col_s6"] + [f"{k}_{k}{len(CHICOTES[k]) - 2}" for k in info["chicotes"]]

    def nasce(i, r_):
        b = (i * (N2 // N_FIAPOS + 1) * 5 + int(r_.integers(0, 4))) % N2
        nome = pontas[i % 3] if i % 5 < 3 else pontas[3 + (i // 5) % (len(pontas) - 3)]
        x, y = pontos[b % N][nome]; x += float(r_.uniform(-20, 20)) if nome.startswith("col") else float(r_.uniform(-3, 3))
        topo = np.where(coluna[b % N][:, int(np.clip(x, 0, TELA.cw - 1))] >= 0)[0]
        if nome.startswith("col") and len(topo):
            y = float(topo.min()) + 2
        return dict(b=b, x=x, y=y, dx=float(r_.uniform(-0.18, 0.18)), v=float(r_.uniform(0.30, 0.55)), vida=int(r_.integers(30, 46)),
                    r=float(r_.uniform(2.4, 3.8)) if nome.startswith("col") else float(r_.uniform(1.6, 2.4)), fi=float(r_.uniform(0, 6.28)))
    fiap = [nasce(i, rng) for i in range(N_FIAPOS)]

    def des_fiapo(L, s, a, f, i):
        q = a / s["vida"]; r = s["r"] * (1 - q) ** 0.8
        if r < 0.7:
            return False
        _bolha(L, s["x"] + s["dx"] * a + 1.8 * math.sin(a * 0.21 + s["fi"]), s["y"] - s["v"] * a, r,
               roxo if q < 0.35 else breu, viol if q < 0.35 else roxo, pal.escura, achat=1.15)
        return True
    fais = C.semeia(rng, N_FAISCAS, dict(b=lambda i, r_: (i * 7 + int(r_.integers(0, 5))) % N2, th=("uni", 0, 6.28), rr=("uni", 0.15, 0.95),
                                         dx=("uni", -0.25, 0.25), v=("uni", 0.5, 1.1), vida=("int", 20, 40)))
    for s in fais:
        s["x"] = ecx + erx * s["rr"] * math.cos(s["th"]); s["y0"] = ecy + ery * s["rr"] * math.sin(s["th"])
    cores_f = (lilas, lilas, viol, roxo)
    fiapos = []
    for f in range(N2):
        L = vazio()
        C.emite(L, f, N2, fiap, des_fiapo)
        C.emite(L, f, N2, fais, lambda L, s, a, f, i: C.desenha_fagulha(cores_f, y0=s["y0"], chao_y=TELA.pe[1])(L, s, a, f, i))
        fiapos.append(L)
    # --- saída NA ORDEM DE DESENHO
    CAM = {"coluna": coluna, "chicotes": chicotes, "anel_tras": anel_t, "fiapos": fiapos, "soltos": soltos, "anel_frente": anel_f}
    C.exporta_camadas(cam, CAM, pal)
    C.escreve_aura_json(cam, ID, AURA, TELA, TIQ, [
        dict(nome="coluna", quadros=N, plano="atras", o_que="coluna de fumaça violeta-preta serpenteando, o miolo escorrendo para cima com clarões violeta subindo"),
        dict(nome="chicotes", quadros=N, plano="atras", o_que="chicotes de sombra dos lados, em cascata da raiz à ponta"),
        dict(nome="anel_tras", quadros=N2, plano="atras", o_que="chão rachado (parte atrás dos pés): lajes arfando, luz correndo pelas rachaduras do centro para a borda, sombras em órbita"),
        dict(nome="fiapos", quadros=N2, plano="atras", o_que="línguas que se soltam do topo e das pontas; faíscas lilás do chão"),
        dict(nome="soltos", quadros=N2, plano="atras", o_que="pedras e elos de corrente partida flutuando em órbitas lentas"),
        dict(nome="anel_frente", quadros=N2, plano="frente", o_que="chão rachado e sombras em órbita à frente dos pés (da linha da sola para baixo)")],
        pal, extras=dict(gerado_por="ferramentas/aura_blender/" + os.path.basename(__file__),
                         nota="coluna e chicotes têm o mesmo laço (48) e foram contornados juntos: use os dois no mesmo quadro"))
    # --- medidas
    c_rgb, c_m = C.reduz(C.conceito_para_4x(f"{rec}/corpo.png", TELA, dx=info["dx"]), TELA.amp)
    cys, cxs = np.where(c_m); corpo_h = int(cys.max() - cys.min() + 1); corpo_w = int(cxs.max() - cxs.min() + 1)
    med = dict(C.mede_conjunto(CAM, pal, N2))
    x0, x1, y0 = med["extensao_aura_x_min_max_y_min"]
    y1 = int(max(np.where(l[f] >= 0)[0].max() for l in CAM.values() for f in range(len(l)) if (l[f] >= 0).any()))
    med["tamanho"] = dict(corpo_px=[corpo_w, corpo_h], aura_px=[x1 - x0 + 1, y1 - y0 + 1], aura_y=[y0, y1],
                          aura_sobre_corpo=[round((x1 - x0 + 1) / corpo_w, 2), round((y1 - y0 + 1) / corpo_h, 2)],
                          conceito_aura_sobre_corpo=[round(777 / 381.0, 2), round(713 / 488.0, 2)])
    for nome, lst in CAM.items():
        med[nome] = C.mede_camada(lst, pal)
    med["coluna_sem_fluxo"] = C.mede_camada(col_seca, pal)
    conj = [np.dstack([pal.rgba(l[f % len(l)]) for l in CAM.values()]) for f in range(N2)]
    dif = [float(np.abs(conj[f].astype(int) - conj[(f + 1) % N2].astype(int)).mean()) for f in range(N2)]
    med["conjunto"] = dict(dif_min=round(min(dif), 3), dif_max=round(max(dif), 3), emenda=round(dif[-1], 3),
                           vizinhos_da_emenda=[round(dif[-2], 3), round(dif[0], 3)])
    med["chicote"] = chicote(pasta, mostra=False)
    med["passo_max_px"] = dict(juntas=max(v["passo_max"] for v in med["chicote"].values()), escorrer_da_coluna=0.58, clarao=2.0,
                               luz_das_rachaduras=1.7, sombras_em_orbita=round(math.pi * erx / N2, 2), fiapo=0.55, faisca=1.1 + 0.012 * 2 * 40)
    json.dump(med, open(f"{pasta}/medidas.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in med.items() if k != "chicote"}, indent=0))
    # --- tiras e vídeo, corpo entre as camadas de trás e a da frente
    corpo = np.dstack([np.clip(c_rgb, 0, 255).astype(np.uint8), (c_m * 255).astype(np.uint8)]); corpo[~c_m] = 0
    fundo = C.fundo_teste(TELA)
    atras = [CAM[k] for k in ("coluna", "chicotes", "anel_tras", "fiapos", "soltos")]; frente = [CAM["anel_frente"]]
    Q_ = [C.compoe(fundo, f, atras, corpo, frente, pal) for f in range(N2)]
    C.tira([Q_[f] for f in range(16)], f"{pasta}/tira.png", rotulos=[f"q{f:02d}" for f in range(16)])
    C.tira([Q_[f] for f in range(0, N2, 6)], f"{pasta}/tira_ciclo.png", rotulos=[f"q{f:02d}" for f in range(0, N2, 6)])
    C.tira([Q_[f][18:108, 85:275] for f in range(8)], f"{pasta}/tira_zoom_topo.png", cols=4, esc=5, rotulos=[f"q{f:02d}" for f in range(8)])
    C.tira([Q_[f][140:200, 80:280] for f in range(0, 16, 2)], f"{pasta}/tira_zoom_chao.png", cols=2, esc=5, rotulos=[f"q{f:02d}" for f in range(0, 16, 2)])
    C.tira([Q_[f][60:170, 85:185] for f in range(0, 48, 6)], f"{pasta}/tira_zoom_esq.png", cols=4, esc=4, rotulos=[f"q{f:02d}" for f in range(0, 48, 6)])
    C.tira([C.compoe(fundo, f, atras, None, frente, pal) for f in (0, N // 2, N, N + N // 2)], f"{pasta}/tira_sem_corpo.png", cols=2, esc=3)
    C.video_laco(f"{pasta}/aura_pengaro.mp4", Q_, TIQ)


def instala(pasta):
    C.instala(os.path.join(pasta, "camadas"), DESTINO)


if __name__ == "__main__":
    import tempfile
    C.roda(__file__, {"recortes": recortes, "rig": rig, "chicote": chicote, "compor": compor, "instala": instala}, os.path.join(tempfile.gettempdir(), "aura_blender", ID))
