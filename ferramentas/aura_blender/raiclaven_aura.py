"""Aura do Raiclaven endiabrado: LEQUE DUPLO DE LÂMINAS DE AÇO (docs/arcade/aura_blender.md).

Como no conceito aprovado (e_conceito.png): duas asas de lâminas abertas em leque, com a adaga no meio do alto, vão
aberto embaixo (onde ficam as pernas e as lascas do chão), um coração de foices em volta do corpo e uma moldura de
raio por fora das pontas. As lâminas são recortadas do conceito uma a uma, postas de pé e presas cada uma na sua casa:
  - asa (x2)        : 9 lâminas da frente (pente, tesoura, faca, navalha, tesoura grande, pente, adaga, navalha, tesoura
                      grande) de 13 a 127 graus a partir do alto, com 9 pontas de adaga atrás, nos vãos;
  - adaga do meio   : sozinha, no alto;
  - coração de foices: 6 foices de cada lado, de 16 a 146 graus;
  - miolo           : roseta de pontas atrás do corpo (remendo: só aparece se o corpo sair da frente).
NADA GIRA EM RODA. Cada asa abre e fecha em cascata (a casa de cima puxa, a de baixo chega depois), cada lâmina estoca
e recolhe em onda, as tesouras cortam (duas metades rígidas no parafuso), a navalha dobra no cabo e as foices abrem
como garras. Moldura de raio, reflexo correndo, lascas no chão e limalha são camadas em Python por cima.

    python ferramentas/aura_blender/raiclaven_aura.py <pasta de trabalho>                  # tudo
    python ferramentas/aura_blender/raiclaven_aura.py <pasta de trabalho> pontos chicote   # só o movimento
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import comum as C

ID = "raiclaven"
AURA = "leque_de_laminas"
SRC = os.path.join(C.RAIZ, "sprites", ID, "quadros", "folhas_arcade", "e_conceito.png")

# ---------------------------------------------------------------------------------------------------------------------
# Medidas do conceito (px da folha)
# ---------------------------------------------------------------------------------------------------------------------
CORPO_X = (10, 440)                  # vista 1: corpo sem aura
AURA_X = (900, 1840)                 # vista 3: corpo + aura
ALTURA_CORPO = 489.0                 # do topo do cabelo à sola na vista 1 (as bobinas passam disso)
CENTRO = (1375.0, 405.0)             # centro do leque na vista 3 (centro do anel de foices)
N = 96                               # quadros do laço (a 2 tiques = 3,2 s)
TIQ = 2

# Peças recortadas do conceito. poly: polígono folgado em volta (apertado onde encosta em vizinha);
# eixo: (ponta de dentro, ponta de fora) como a peça fica no leque; tampas: riscos que fecham o contorno onde a
# peça some debaixo de outra.
PECAS = {
    "tesoura_g": dict(poly=[(938, 192), (1015, 190), (1050, 226), (1100, 240), (1150, 288), (1148, 304), (1100, 293), (1042, 276),
                            (1000, 282), (940, 264), (930, 242)],
                      eixo=((1143, 297), (962, 228)), pivo=(1043, 251), argolas=((990, 215), (975, 248))),
    "tesoura_p": dict(poly=[(1212, 48), (1222, 38), (1290, 36), (1290, 92), (1290, 130), (1318, 205), (1314, 220), (1300, 220),
                            (1264, 142), (1240, 110), (1212, 88)],
                      eixo=((1307, 216), (1250, 60)), pivo=(1274, 129), argolas=((1232, 80), (1266, 65)),
                      tampas=[((1298, 219), (1316, 219))]),
    "adaga": dict(poly=[(1385, 6), (1404, 60), (1403, 116), (1398, 136), (1398, 238), (1375, 238), (1375, 136), (1367, 116), (1368, 60)],
                  eixo=((1386, 236), (1385.5, 12)), tampas=[((1375, 236), (1398, 236))]),
    "pente": dict(poly=[(1308, 58), (1345, 50), (1355, 60), (1359, 150), (1363, 214), (1344, 214), (1342, 166), (1318, 162), (1308, 100)],
                  eixo=((1353, 212), (1341, 58)), tampas=[((1344, 212), (1363, 212))],
                  inclui=[[(1343, 158), (1357, 158), (1358, 213), (1345, 213)], [(1314, 64), (1344, 61), (1350, 72), (1314, 74)]]),
    "faca": dict(poly=[(1135, 44), (1150, 50), (1216, 126), (1250, 186), (1253, 206), (1238, 211), (1222, 206), (1195, 160), (1160, 116),
                       (1139, 70)],
                 eixo=((1243, 205), (1141, 51)), tampas=[((1224, 207), (1252, 205))]),
    "foice": dict(poly=[(1542, 427), (1560, 430), (1585, 450), (1594, 470), (1598, 490), (1597, 512), (1592, 532), (1591, 546),
                        (1581, 546), (1578, 515), (1569, 480), (1557, 456), (1544, 438)],
                  eixo=((1586, 540), (1547, 431))),
}
PECAS["navalha"] = dict(poly=[(910, 507), (975, 477), (1005, 464), (1050, 456), (1085, 455), (1136, 444), (1138, 473), (1092, 483),
                              (1078, 501), (1000, 505), (925, 517), (910, 515)],
                        eixo=((1133, 460), (915, 510)), tampas=[((1135, 445), (1135, 473))])
# espinha de cada peça (px do conceito, de dentro para fora): um osso por trecho
ESPINHA = {
    "adaga": [(1386, 236), (1386, 180), (1386, 122), (1385.5, 65), (1385.5, 12)],
    "pente": [(1353, 212), (1349, 165), (1344, 112), (1341, 58)],
    "faca": [(1243, 205), (1212, 146), (1176, 98), (1141, 51)],
    "navalha": [(1133, 460), (1068, 470), (1003, 482), (958, 497), (915, 510)],
    "foice": [(1586, 540), (1588, 505), (1579, 468), (1548, 431)],
}
# raio de fora (px do conceito) por ângulo a partir do alto: mais largo que alto, com a fenda do coração ao lado da
# adaga do meio (medido no conceito: 925 px de largura, topo a 385 px do centro)
ANG_R = [0, 13, 27, 41, 55, 70, 85, 99, 113, 127, 140]
VAL_R = [385, 348, 388, 408, 428, 448, 460, 452, 432, 408, 390]
# uma asa, de cima para baixo: (ângulo de repouso, peça). A outra asa é o espelho.
ASA = [(13, "pente"), (27, "tesoura_p"), (41, "faca"), (55, "navalha"), (70, "tesoura_g"), (85, "pente"), (99, "adaga"),
       (113, "navalha"), (127, "tesoura_g")]
# em 1/4 a lâmina do tamanho do conceito fica um fiapo: engorda (o conceito tem tesouras e pentes GRANDES)
ESCALA = dict(tesoura_g=1.5, tesoura_p=1.6, pente=1.75, faca=1.35, navalha=1.35, adaga=1.35, ponta=1.35)
ABERTURA = 0.048                     # a asa abre e fecha 4,8% do ângulo de cada casa (6 graus na casa de baixo)
ATRASO_CASA = 0.33                   # rad de atraso por casa: a onda leva ~20 quadros para descer a asa
ESTOCADA = 23.0                      # px do conceito que cada lâmina avança e recolhe
BALANCO = 2.5                        # graus que a lâmina se inclina atrasada em relação à casa
ABRE = 15.0                          # cada metade da tesoura abre de 0 a ABRE graus (30 no total)
FOICES = [(16, 195), (42, 215), (68, 228), (94, 228), (120, 220), (146, 205)]   # (ângulo, raio do meio) de um lado
ESCALA_FOICE = 1.45                  # a foice do recorte é das menores do desenho
RESPIRA_F = 9.0
NH, RAIO_MIOLO = 10, 150.0           # roseta de pontas atrás do corpo
FOLGA = 160.0                        # histerese do encaixe na paleta
LASCAS_Y = 652                       # abaixo disto, fora do corpo, é lasca cravada no chão
ESCURA = (26, 28, 34)                # contorno: grafite quase preto, sem roxo
MARG = 14                            # margem do recorte posto de pé


def raio_fora(a):
    return float(np.interp(abs(a), ANG_R, VAL_R))


def tela(info):
    """Tela do jogo: eixo do corpo e chão na vista 3 saem do casamento do corpo (recortes/info.json)."""
    return C.Tela(cx=info["cx"], chao=info["chao"], escala=112.0 / ALTURA_CORPO)


TP = C.Tela(cx=0.0, chao=0.0, escala=112.0 / ALTURA_CORPO)   # tela das peças postas de pé (origem no canto do recorte)


def aco(rgb):
    """Tira o lilás: o aço fica cinza neutro, levemente frio (pedido: prata/branco/grafite, sem lilás nem violeta)."""
    R, G, B = C.canais(rgb)
    l = np.minimum(np.minimum(R, G), B) * 0.5 + (0.3 * R + 0.59 * G + 0.11 * B) * 0.5   # o derrame de magenta puxa R e B
    o = np.stack([l * 0.97, l * 0.99, l * 1.04 + 3], axis=-1)
    return np.clip(o, 0, 255).astype(np.uint8)


def extrai(im, fg, poly, tampas=(), inclui=(), limiar=105, fecha=4):
    """Peça dentro do polígono, sem o raio branco do desenho. Junta dois critérios:
    (1) o que o contorno escuro fecha, isto é, o que não está ligado ao magenta por pixels claros (pega argola, cabo e
        dente fino, mas vaza quando um raio CRUZA a peça);
    (2) o miolo: o que fica a mais de 4 px do magenta (raio é fino e some; lâmina larga fica), crescido de volta até
        o contorno.
    inclui: polígonos onde vale tudo o que não é magenta (cabo fino cruzado por raio)."""
    import cv2
    from scipy import ndimage as ndi
    def masc(pl):
        m = np.zeros(fg.shape, np.uint8); cv2.fillPoly(m, [np.array(pl, np.int32)], 1); return m.astype(bool)
    pm = masc(poly)
    luma = im.astype(int).sum(2) / 3
    esc = (luma < limiar) & pm & fg
    par = np.zeros(fg.shape, np.uint8)
    for a, b in tampas:
        cv2.line(par, tuple(int(v) for v in a), tuple(int(v) for v in b), 1, 2)
    fech = ndi.binary_closing(esc, iterations=fecha) | esc | par.astype(bool)
    lab, n = ndi.label(pm & ~fech)
    toca = np.unique(lab[pm & ~fg]); toca = toca[toca > 0]
    m1 = pm & fg & ~np.isin(lab, toca)
    miolo = pm & fg & (ndi.distance_transform_edt(fg) > 4.5)
    m2 = ndi.binary_dilation(miolo, iterations=3, mask=pm & fg & ~esc)
    m2 |= esc & ndi.binary_dilation(m2, iterations=4)
    m = m1 | m2
    for pl in inclui:
        m |= masc(pl) & fg
    ab = ndi.binary_opening(m, iterations=1)
    m = ab | (esc & ndi.binary_dilation(ab, iterations=2))
    return C.maior_componente(m, 8)


def arredonda(m, h=10):
    """Fecha em meia-lua a ponta de DENTRO (embaixo, no recorte de pé) de uma peça que o conceito cortava reto porque
    ela sumia debaixo de outra: sem isso a peça termina num toco serrilhado quando o corpo sai da frente."""
    ys = np.where(m.any(1))[0]; yb = int(ys.max()); y0 = yb - h
    xs = np.where(m[y0])[0]
    if len(xs) == 0:
        return m
    c = (xs.min() + xs.max()) / 2.0; w = (xs.max() - xs.min()) / 2.0 + 0.5
    o = m.copy(); XX = np.arange(m.shape[1])
    for y in range(y0, yb + 1):
        t = (y - y0) / float(h)
        o[y] &= np.abs(XX - c) <= w * math.sqrt(max(0.0, 1.0 - t * t))
    return o


def salva(arq, rgb, m, borda=2):
    """Salva o recorte com a casca de `borda` px pintada de escuro: em 1/4 o contorno do desenho clareia e as lâminas
    encavaladas viram uma massa só; assim cada uma guarda o seu risco."""
    from scipy import ndimage as ndi
    o = rgb.copy(); o[m & ~ndi.binary_erosion(m, iterations=borda)] = ESCURA
    C.salva_rgba(arq, o, m)


def de_pe(rgb, m, p_in, p_out):
    """Gira o recorte para o eixo ficar vertical (ponta de fora em cima). Devolve (rgb, máscara, função que leva
    pontos do conceito para o recorte)."""
    import cv2
    p_in = np.array(p_in, float); p_out = np.array(p_out, float)
    d = p_out - p_in; L = float(np.hypot(*d)); u = d / L                     # u: de dentro para fora
    v = np.array([-u[1], u[0]])                                              # perpendicular
    ys, xs = np.where(m); P = np.stack([xs, ys], 1) - p_in
    a = P @ u; b = P @ v
    a0, a1, b0, b1 = a.min(), a.max(), b.min(), b.max()
    Wc = int(math.ceil(b1 - b0)) + 2 * MARG; Hc = int(math.ceil(a1 - a0)) + 2 * MARG
    # ponto do conceito p -> recorte: x = MARG + (b - b0), y = Hc - MARG - (a - a0)
    M = np.array([[v[0], v[1], MARG - b0 - v @ p_in], [-u[0], -u[1], Hc - MARG + a0 + u @ p_in]])
    o = cv2.warpAffine(rgb, M, (Wc, Hc), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    mm = cv2.warpAffine((m * 255).astype(np.uint8), M, (Wc, Hc), flags=cv2.INTER_LINEAR) > 127
    return o, mm, (lambda p: [float(M[0, 0] * p[0] + M[0, 1] * p[1] + M[0, 2]), float(M[1, 0] * p[0] + M[1, 1] * p[1] + M[1, 2])])


def recortes(pasta):
    from scipy import ndimage as ndi
    from PIL import Image
    rec = os.path.join(pasta, "recortes"); os.makedirs(rec, exist_ok=True)
    im = C.le_rgb(SRC); H, W = im.shape[:2]
    fg = C.chave_magenta(im)
    corpo = C.recorta_corpo(fg, im, *CORPO_X)
    Image.fromarray(np.dstack([im, (corpo * 255).astype(np.uint8)])).save(f"{rec}/corpo.png")
    dx, dy, nota = C.casa_corpo(im, corpo, *AURA_X)
    ys, xs = np.where(corpo); sola = int(ys.max()) + 1
    pes = np.where(corpo[sola - 25:sola].any(0))[0]
    cx1 = (pes.min() + pes.max()) / 2.0
    # topo do cabelo: primeira linha com corpo na faixa da cabeça (as bobinas ficam à esquerda dela)
    cab = int(np.where(corpo[:, 292:330].any(1))[0].min())
    info = dict(dx=dx, dy=dy, nota=nota, cx=float(cx1 + dx), chao=float(sola + dy), topo_cabelo=cab, sola_v1=sola,
                altura_medida=int(sola - cab), topo_bobina=int(ys.min()), pecas={})
    print("corpo casado: dx", dx, "dy", dy, "nota", round(nota, 3), "| cabelo", cab, "sola", sola, "altura", sola - cab,
          "| eixo na vista 3:", info["cx"], "chao:", info["chao"])
    cinza = aco(im)
    for nome, p in PECAS.items():
        m = extrai(im, fg, p["poly"], p.get("tampas", ()), p.get("inclui", ()))
        o, mm, leva = de_pe(cinza, m, *p["eixo"])
        if nome in ("adaga", "navalha", "pente", "faca"):
            mm = arredonda(mm)
        d = dict(tam=[o.shape[1], o.shape[0]], dentro=leva(p["eixo"][0]), fora=leva(p["eixo"][1]), area=int(mm.sum()))
        if nome.startswith("tesoura"):
            # duas metades rígidas. Lado da lâmina (abaixo do parafuso): tudo vai para a metade A; a metade B leva o
            # ESPELHO da lâmina (fica escondido debaixo de A quando fechada). Lado do cabo: cada argola é de uma metade.
            pv = leva(p["pivo"]); g1, g2 = leva(p["argolas"][0]), leva(p["argolas"][1])
            gm = ((g1[0] + g2[0]) / 2, (g1[1] + g2[1]) / 2)
            YY, XX = np.mgrid[0:o.shape[0], 0:o.shape[1]]
            disco = ((XX - pv[0]) ** 2 + (YY - pv[1]) ** 2 <= 9 ** 2) & mm
            lam = mm & (YY > pv[1] - 2)
            lado = (XX - pv[0]) * (gm[1] - pv[1]) - (YY - pv[1]) * (gm[0] - pv[0])       # lado da linha parafuso -> meio das argolas
            s1 = np.sign((g1[0] - pv[0]) * (gm[1] - pv[1]) - (g1[1] - pv[1]) * (gm[0] - pv[0]))
            cabo1 = mm & (YY <= pv[1] - 2) & (np.sign(lado) == s1)
            cabo2 = mm & (YY <= pv[1] - 2) & ~cabo1
            # a lâmina de A abre para o lado da argola 1, então o cabo de A é o da argola 2 (as metades cruzam no parafuso)
            A = lam | cabo2 | disco
            xs_ = np.clip(np.round(2 * pv[0] - XX).astype(int), 0, o.shape[1] - 1)
            esp = lam[YY, xs_]; oe = o.copy(); oe[esp] = o[YY, xs_][esp]
            oe[cabo1 | disco] = o[cabo1 | disco]
            salva(f"{rec}/{nome}_a.png", o, A); salva(f"{rec}/{nome}_b.png", oe, esp | cabo1 | disco)
            d.update(pivo=pv, argola_a=g2, argola_b=g1)
        else:
            salva(f"{rec}/{nome}.png", o, mm)
        if nome == "adaga":          # a ponta do anel de trás: só a lâmina da adaga
            guarda = int(leva((1385, 122))[1])
            mp = mm.copy(); mp[guarda:] = False
            salva(f"{rec}/ponta.png", o[:guarda + MARG], mp[:guarda + MARG])
            info["pecas"]["ponta"] = dict(tam=[o.shape[1], guarda + MARG], dentro=[d["fora"][0], guarda - 1.0], fora=d["fora"],
                                          area=int(mp.sum()))
        if nome in ESPINHA:
            d["espinha"] = [leva(q) for q in ESPINHA[nome]]
        info["pecas"][nome] = d
    # lascas cravadas no chão: o que sobra abaixo de LASCAS_Y fora do corpo, na resolução do conceito
    corpo3 = ndi.binary_dilation(C.desloca(corpo, dx, dy), iterations=6)
    ls = fg.copy(); ls[:LASCAS_Y] = False; ls[:, :AURA_X[0]] = False; ls[:, 1700:] = False; ls &= ~corpo3
    luma = im.astype(int).sum(2) / 3
    ls &= ~((luma > 225) & (np.arange(H)[:, None] < 672))              # o rabo dos raios do desenho
    ls = ndi.binary_opening(ls, iterations=1)
    lab, comps = C.componentes(ls)
    lascas = np.zeros_like(ls); lista = []
    for c in comps:
        if c["area"] >= 110 and c["y1"] - c["y0"] >= 22:
            lascas |= lab == c["i"]; lista.append(c)
    lista.sort(key=lambda c: c["x0"])
    for k, c in enumerate(lista):        # um recorte por lasca, com a base, o meio e a ponta (para os 2 ossos)
        m = lab[c["y0"]:c["y1"], c["x0"]:c["x1"]] == c["i"]
        m = np.pad(m, MARG); rg = np.pad(cinza[c["y0"]:c["y1"], c["x0"]:c["x1"]], ((MARG, MARG), (MARG, MARG), (0, 0)))
        C.salva_rgba(f"{rec}/lasca_{k:02d}.png", rg, m)
        ys_ = np.where(m.any(1))[0]; ya, yb = int(ys_.min()), int(ys_.max())
        mx = lambda y0_, y1_: float(np.where(m[y0_:y1_ + 1].any(0))[0].mean())
        c["base"] = [mx(yb - 4, yb), float(yb)]; c["topo"] = [mx(ya, ya + 4), float(ya)]
        ym = (ya + yb) // 2; c["meio"] = [mx(ym - 2, ym + 2), float(ym)]
    C.salva_rgba(f"{rec}/lascas.png", cinza, lascas)
    info["lascas"] = lista
    json.dump(info, open(f"{rec}/info.json", "w"), indent=1)
    # prévia: todas as peças de pé lado a lado, 2x
    arqs = [a for a in sorted(os.listdir(rec)) if a.endswith(".png") and a not in ("corpo.png", "lascas.png") and not a.startswith("lasca_")]
    ims = [np.array(Image.open(f"{rec}/{a}").convert("RGBA")) for a in arqs]
    Hm = max(i.shape[0] for i in ims); Wt = sum(i.shape[1] + 6 for i in ims)
    pv_ = np.full((Hm, Wt, 3), (90, 40, 40), np.uint8); x = 0
    for i in ims:
        m = i[..., 3] > 0; pv_[:i.shape[0], x:x + i.shape[1]][m] = i[..., :3][m]; x += i.shape[1] + 6
    Image.fromarray(pv_).resize((Wt * 2, Hm * 2), Image.NEAREST).save(f"{pasta}/p_pecas.png")
    print("pecas:", {k: v["tam"] for k, v in info["pecas"].items()}, "| lascas:", len(lista), arqs)
    C.previa_recortes([f"{rec}/lascas.png"], f"{pasta}/p_lascas.png", (1000, 640, 1700, 815), (H, W))


# ---------------------------------------------------------------------------------------------------------------------
# Rig (roda dentro do Blender)
# ---------------------------------------------------------------------------------------------------------------------
# Nada gira em roda. Cada asa do leque abre e fecha como leque de verdade: o ângulo de cada casa é o de repouso vezes
# uma abertura que oscila, e a oscilação chega mais tarde quanto mais embaixo a casa está (a onda desce a asa: a casa
# de cima puxa, a de baixo chega depois). Por cima disso cada lâmina estoca para fora e recolhe (onda de teclas), as
# tesouras cortam (abrem devagar, fecham de estalo) e a navalha dobra no cabo. Todas as fases usam um número INTEIRO
# de ciclos por laço: o quadro N cai igual ao 0 sem conta de giro.
def wf(f, ciclos, atraso=0.0):
    return 2 * math.pi * ciclos * f / N - atraso


def fase_asa(sg, p, f):
    """Fase do abre-e-fecha da casa p (0 = em cima) da asa sg: 2 ciclos por laço, ATRASO_CASA rad de atraso por casa."""
    return wf(f, 2, ATRASO_CASA * p + (0.5 if sg < 0 else 0.0))


def angulo(sg, p, a0, f):
    """Ângulo (graus a partir do alto, + = direita) da casa p de ângulo de repouso a0 no quadro f."""
    ab = 1.0 + ABERTURA * math.sin(fase_asa(sg, p, f)) + 0.012 * math.sin(wf(f, 5, 0.9 * p - sg))
    return sg * a0 * ab + 1.2 * math.sin(wf(f, 1, 0.2 * p))


def estocada(sg, p, f):
    """Vai-e-vem no raio (px do conceito): 3 ciclos por laço, a onda desce a asa."""
    return ESTOCADA * math.sin(wf(f, 3, 0.7 * p + sg * 0.6))


def corte(sg, p, f):
    """Abertura da tesoura de 0 a 1: abre devagar e fecha de estalo, 3 cortes por laço, cada tesoura na sua vez."""
    x = wf(f, 3, 1.1 * p + sg)
    return 0.5 * (1.0 - math.cos(x + 0.6 * math.sin(x)))


# flexão por osso: (amplitude em graus, atraso em fração do ciclo), da raiz para a ponta: a ponta dobra mais e depois.
FLEXAO = {
    "adaga": [(0.6, 0.00), (1.2, 0.07), (2.2, 0.15), (3.6, 0.24)],
    "pente": [(0.8, 0.00), (2.4, 0.10), (4.2, 0.21)],
    "faca": [(0.6, 0.00), (2.0, 0.10), (3.4, 0.20)],
    "navalha": [(0.5, 0.00), (0.8, 0.05), (7.0, 0.12), (1.6, 0.21)],    # a lâmina dobra no cabo (abre e fecha)
    "ponta": [(1.0, 0.00), (2.4, 0.12)],
    "foice": [(9.0, 0.00), (5.0, 0.08), (8.0, 0.17)],                    # a foice abre como garra
}


def anima_ossos(ao, fns):
    """Rotação no plano da tela de cada osso: fns = {osso: função(f) -> graus (positivo = sentido horário na tela)}."""
    from mathutils import Vector, Quaternion
    for nm, fn in fns.items():
        pb = ao.pose.bones[nm]; pb.rotation_mode = "QUATERNION"
        eixo = (ao.data.bones[nm].matrix_local.to_3x3().inverted() @ Vector((0, 1, 0))).normalized()
        for f in range(N + 1):
            pb.rotation_quaternion = Quaternion(eixo, math.radians(fn(f))); pb.keyframe_insert("rotation_quaternion", frame=f)


def cauda(ao, osso, T):
    w = ao.matrix_world @ ao.pose.bones[osso].tail
    return [round(v, 3) for v in T.jogo(w.x, w.z)]


def rig(pasta, so_pontos=False):
    import bpy
    rec = os.path.join(pasta, "recortes"); info = json.load(open(f"{rec}/info.json")); T = tela(info)
    s = T.escala; P = info["pecas"]
    C.bl_cena(T, N)
    cena = bpy.context.scene
    cxb, czb = T.g(*CENTRO)

    def vazio(nome, pai=None):
        e = bpy.data.objects.new(nome, None); cena.collection.objects.link(e); e.rotation_mode = "XYZ"
        if pai:
            e.parent = pai
        return e

    # o leque inteiro sobe e desce um pouco, como quem respira
    raiz = vazio("leque")
    C.bl_anima_objeto(raiz, N, lambda t: dict(location=(cxb + 0.6 * math.sin(t + 1.0), 0, czb + 1.4 * math.sin(2 * t))))

    def cadeia(nome, tipo, pts):
        ossos = [(f"o{j}", f"o{j - 1}" if j else None, pts[j], pts[j + 1]) for j in range(len(pts) - 1)]
        return C.bl_malha_com_ossos(nome, f"{rec}/{tipo}.png", ossos, TP, N, celula=6, margem=6)

    def segura(e, alfa_fn, raio_fn, bal_fn, y, tangente=0.0, quarto=False):
        """Põe `e` (filho da raiz) na casa de ângulo alfa_fn(f): +Z local aponta para fora (ou +X, se quarto)."""
        def fn(t):
            f = t * N / (2 * math.pi)
            r = raio_fn(f); a = math.radians(alfa_fn(f))
            x, z = r * math.sin(a) + tangente * -math.cos(a), r * math.cos(a) + tangente * math.sin(a)
            return dict(location=(x, y, z), rotation_euler=(0, a - (math.pi / 2 if quarto else 0) + math.radians(bal_fn(f)), 0))
        C.bl_anima_objeto(e, N, fn)

    leque_a, leque_b, foices, lascas = [], [], [], []
    tips = []        # (chave, armação, osso)
    dp = P["ponta"]
    pts_ponta = [dp["dentro"], [(dp["dentro"][0] + dp["fora"][0]) / 2, (dp["dentro"][1] + dp["fora"][1]) / 2], dp["fora"]]
    comp_ponta = (dp["dentro"][1] - dp["fora"][1]) * s

    def poe_ponta(ch, sg, p, a0, R, esc, y):
        """Ponta de adaga de trás: acompanha a asa e estoca ao contrário das lâminas da frente."""
        pc = cadeia(ch, "ponta", pts_ponta); ao = pc["arm"]; ao.parent = raiz; ao.rotation_mode = "XYZ"; ao.scale = (esc, 1, esc)
        segura(ao, lambda f: angulo(sg, p, a0, f), lambda f: R * s - comp_ponta * esc - 0.7 * s * estocada(sg, p, f),
               lambda f: sg * 2.0 * math.sin(fase_asa(sg, p, f) - 1.1), y)
        anima_ossos(ao, {f"o{j}": (lambda f, a=a, l=l: sg * a * math.sin(fase_asa(sg, p, f) - 2 * math.pi * l))
                         for j, (a, l) in enumerate(FLEXAO["ponta"])})
        leque_b.append(pc["malha"]); tips.append((ch, ao, "o1"))

    def poe_lamina(ch, tipo, sg, p, a0, y):
        d = P[tipo]; esc = ESCALA[tipo]; R = raio_fora(a0)
        alfa = lambda f: angulo(sg, p, a0, f)
        bal = lambda f: sg * BALANCO * (a0 / 127.0 + 0.25) * math.sin(fase_asa(sg, p, f) - 1.1)   # a ponta chega depois da raiz
        if tipo.startswith("tesoura"):
            pv = d["pivo"]; comp = (pv[1] - d["fora"][1]) * s * esc
            e = vazio(ch, raiz); e.scale = (esc, 1, esc)
            segura(e, alfa, lambda f: R * s - comp + s * estocada(sg, p, f), bal, y)
            lado = 1.0 if d["argola_b"][0] > pv[0] else -1.0             # a lâmina de A abre para o lado da argola de B
            for m, arg, sn, dy in (("a", d["argola_a"], -lado, 0.0), ("b", d["argola_b"], lado, 0.05)):
                ossos = [("lam", None, pv, d["dentro"]), ("cabo", "lam", pv, arg)]
                pc = C.bl_malha_com_ossos(f"{ch}{m}", f"{rec}/{tipo}_{m}.png", ossos, TP, N, celula=6, margem=6)
                pc["arm"].parent = e; pc["arm"].location = (0, dy, 0)
                anima_ossos(pc["arm"], {"lam": lambda f, sn=sn: sn * ABRE * corte(sg, p, f)})   # o cabo é filho da lâmina
                leque_a.append(pc["malha"]); tips.append((ch + ("" if m == "a" else "x"), pc["arm"], "cabo"))
        else:
            pts = d["espinha"]; comp = (pts[0][1] - d["fora"][1]) * s * esc
            pc = cadeia(ch, tipo, pts); ao = pc["arm"]; ao.parent = raiz; ao.rotation_mode = "XYZ"; ao.scale = (esc, 1, esc)
            segura(ao, alfa, lambda f: R * s - comp + s * estocada(sg, p, f), bal, y)
            anima_ossos(ao, {f"o{j}": (lambda f, a=a, l=l: sg * a * math.sin(fase_asa(sg, p, f) - 2 * math.pi * l))
                             for j, (a, l) in enumerate(FLEXAO[tipo])})
            leque_a.append(pc["malha"]); tips.append((ch, ao, f"o{len(pts) - 2}"))

    # miolo atrás do corpo (remendo): roseta de pontas que pulsa; só aparece se o corpo sair da frente
    for i in range(NH):
        a0 = (i + 0.5) * 360.0 / NH
        pc = cadeia(f"h{i:02d}", "ponta", pts_ponta); ao = pc["arm"]; ao.parent = raiz; ao.rotation_mode = "XYZ"
        segura(ao, lambda f, a0=a0, i=i: a0 + 5.0 * math.sin(wf(f, 2, 2 * math.pi * i / NH)),
               lambda f, i=i: RAIO_MIOLO * s - comp_ponta + 16.0 * s * math.sin(wf(f, 3, 2 * math.pi * 2 * i / NH)), lambda f: 0.0, 6.0 + 0.01 * i)
        anima_ossos(ao, {"o1": lambda f, i=i: 3.0 * math.sin(wf(f, 3, i))})
        leque_b.append(pc["malha"]); tips.append((f"h{i:02d}", ao, "o1"))

    # as duas asas + a adaga do meio
    poe_lamina("a00", "adaga", 1, -0.5, 0.0, 1.0)
    k = 1
    for sg in (1, -1):
        am = ASA[0][0] * 0.5
        poe_ponta(f"b{k - 1:02d}", sg, -0.5, am, raio_fora(am) * 0.74, ESCALA["ponta"], 4.0 + 0.01 * k)
        for p, (a0, tipo) in enumerate(ASA):
            poe_lamina(f"a{k:02d}", tipo, sg, p, a0, 1.0 + 0.2 * (p % 2) + 0.02 * p)
            if p + 1 < len(ASA):
                am = (a0 + ASA[p + 1][0]) / 2.0
                poe_ponta(f"b{k:02d}", sg, p + 0.5, am, raio_fora(am) * 0.80, ESCALA["ponta"], 4.0 + 0.01 * k)
            k += 1

    # coração de foices: corda na tangente, barriga para fora; cada uma abre como garra, a de cima primeiro
    d = P["foice"]; pts = d["espinha"]; comp = (pts[0][1] - d["fora"][1]) * s
    k = 0
    for sg in (1, -1):
        for j, (a0, R) in enumerate(FOICES):
            pc = cadeia(f"f{k:02d}", "foice", pts); ao = pc["arm"]; ao.parent = raiz; ao.rotation_mode = "XYZ"
            ao.scale = (ESCALA_FOICE, 1, ESCALA_FOICE)
            fg_ = lambda f, j=j, sg=sg: wf(f, 2, 0.6 * j + (0.4 if sg < 0 else 0.0))
            segura(ao, lambda f, a0=a0, j=j, sg=sg: sg * a0 * (1.0 + 0.035 * math.sin(fase_asa(sg, j * 1.5, f) - 0.8)),
                   lambda f, R=R, j=j, sg=sg: (R - 22) * s + RESPIRA_F * s * math.sin(wf(f, 3, 0.8 * j + sg)), lambda f: 0.0,
                   0.0 + 0.03 * (k % 3), tangente=-comp * ESCALA_FOICE / 2, quarto=True)
            anima_ossos(ao, {f"o{n}": (lambda f, fg_=fg_, a=a, l=l, n=n: a * (math.sin(fg_(f) - 2 * math.pi * l) + (1.6 if n == 0 else 0.0)))
                             for n, (a, l) in enumerate(FLEXAO["foice"])})
            foices.append(pc["malha"]); tips.append((f"f{k:02d}", ao, "o2")); k += 1

    # lascas cravadas no chão: um recorte por lasca, 2 ossos da base à ponta, tremendo cada uma no seu ritmo
    for k, c in enumerate(info["lascas"]):
        TL = C.Tela(cx=T.cx - c["x0"] + MARG, chao=T.chao - c["y0"] + MARG, escala=s)
        b, m_, t = c["base"], c["meio"], c["topo"]
        pc = C.bl_malha_com_ossos(f"l{k:02d}", f"{rec}/lasca_{k:02d}.png", [("o0", None, b, m_), ("o1", "o0", m_, t)], TL, N,
                                  celula=5, margem=5)
        ao = pc["arm"]; ox, oz = pc["origem"]
        kk = 5 + (k * 3) % 4; ph = k * 2.399
        # a lasca inteira também treme no chão (senão o pé dela fica parado)
        C.bl_anima_objeto(ao, N, lambda t, ox=ox, oz=oz, kk=kk, ph=ph, k=k: dict(
            location=(ox + 0.55 * math.sin(kk * t + ph + 1.0), -1.0 + 0.01 * k, oz + 0.7 * math.sin((kk - 2) * t + ph * 1.3))))
        anima_ossos(ao, {"o0": lambda f, kk=kk, ph=ph: 2.0 * math.sin(2 * math.pi * kk * f / N + ph) + 1.0 * math.sin(2 * math.pi * f / N + ph * 1.7),
                         "o1": lambda f, kk=kk, ph=ph: 3.5 * math.sin(2 * math.pi * kk * f / N + ph - 1.1) + 1.2 * math.sin(2 * math.pi * 2 * kk * f / N + ph)})
        lascas.append(pc["malha"]); tips.append((f"l{k:02d}", ao, "o1"))

    def coleta(f):
        return {ch: cauda(ao, osso, T) for ch, ao, osso in tips}

    C.bl_renderiza(pasta, N, {"leque_b": leque_b, "leque_a": leque_a, "foices": foices, "lascas": lascas}, coleta, so_pontos=so_pontos,
                   extra=dict(centro=list(T.jogo(cxb, czb))), blend="rig.blend")


# ---------------------------------------------------------------------------------------------------------------------
# Camadas procedurais e saída
# ---------------------------------------------------------------------------------------------------------------------
LIMALHA = 80
HALO = (150, 196, 236)               # azul-gelo do clarão em volta do raio (separa o raio branco do aço branco)
ARCOS = dict(ff=14, ll=10)           # arcos soltos por laço: foice-foice e lasca-lasca (a moldura é à parte)
PERIODO = 12                         # cada trecho da moldura estala a cada 12 quadros: 9 aceso, 3 apagado


def brilho(idx, u, sobe, forte=1.2, fraco=3.6, piso=2):
    """Reflexo correndo pelo aço: u é a distância (em px ou graus) até a faixa de luz. Só clareia o que já é aço,
    andando na rampa de cinzas `sobe` (não cria pixel e não usa a cor do raio)."""
    m = idx >= piso
    out = idx.copy()
    a = m & (u >= forte) & (u < fraco); b = m & (u < forte)
    out[a] = sobe[1][idx[a]]; out[b] = sobe[2][idx[b]]
    return out


def zigue(p0, p1, rg, amp=0.24, nivel=3):
    """Raio entre p0 e p1 por deslocamento do ponto médio: quebra em 2**nivel trechos, cada quebra para um lado."""
    pts = [np.asarray(p0, float), np.asarray(p1, float)]
    for _ in range(nivel):
        novo = [pts[0]]
        for a, b in zip(pts[:-1], pts[1:]):
            d = b - a; L = float(np.hypot(*d)) + 1e-6
            novo += [(a + b) / 2 + np.array([-d[1], d[0]]) / L * rg.uniform(-1, 1) * amp * L, b]
        pts = novo
    return np.array(pts)


def traca(m, pts, esp=1, falha=None):
    import cv2
    q = np.round(pts).astype(np.int32)
    for j in range(len(q) - 1):
        if falha is not None and falha[j % len(falha)]:
            continue
        cv2.line(m, (int(q[j][0]), int(q[j][1])), (int(q[j + 1][0]), int(q[j + 1][1])), 1, esp)


def estalo(vivo, morto, p0, p1, semente, idade, vida, ramo=True):
    """Um raio de `vida` quadros entre p0 e p1 (que andam com as lâminas). O traçado troca a cada 3 quadros (o raio
    estala de novo), nasce grosso, e nos 2 últimos quadros fica falhado e sem brilho."""
    rg = np.random.default_rng(semente * 977 + idade // 3)
    pts = zigue(p0, p1, rg)
    if idade >= vida - 2:
        traca(morto, pts, 1, falha=rg.uniform(0, 1, 8) < 0.4)
        return
    traca(vivo, pts, 2 if idade < 2 else 1)
    if ramo:
        j = int(rg.integers(2, len(pts) - 2)); d = pts[j + 1] - pts[j - 1]
        ang = math.atan2(d[1], d[0]) + rg.choice([-1, 1]) * rg.uniform(0.6, 1.1); L = rg.uniform(6, 11)
        traca(vivo, zigue(pts[j], pts[j] + L * np.array([math.cos(ang), math.sin(ang)]), rg, nivel=2), 1)


def ponta_de_fora(pt, ch):
    """Ponta de fora da peça ch num quadro (na tesoura, o meio entre as duas argolas)."""
    p = np.array(pt[ch])
    return (p + np.array(pt[ch + "x"])) / 2 if ch + "x" in pt else p


def moldura(pt, sg, cxg, cyg):
    """Nós da moldura de raio de uma asa, do chão até a fenda do alto: 5 px para fora da ponta de cada lâmina."""
    na = len(ASA); k0 = 1 if sg > 0 else 1 + na
    nos = [np.array([cxg + sg * 58.0, 185.0])]
    for p in range(na - 1, -1, -1):
        q = ponta_de_fora(pt, f"a{k0 + p:02d}"); d = q - np.array([cxg, cyg])
        nos.append(q + 5.0 * d / (np.hypot(*d) + 1e-6))
    nos.append(np.array([cxg, pt["a00"][1] + 13.0]))            # a fenda do coração: a adaga do meio fura por ela
    return nos


def compor(pasta):
    from scipy import ndimage as ndi
    rec = os.path.join(pasta, "recortes"); cam = os.path.join(pasta, "camadas")
    info = json.load(open(f"{rec}/info.json")); T = tela(info)
    dados = json.load(open(f"{pasta}/render/pontos.json")); pontos = dados["pontos"]; cxg, cyg = dados["centro"]
    rng = np.random.default_rng(11)
    nomes_r = ("leque_b", "leque_a", "foices", "lascas")
    bru = {n: [C.le_render(f"{pasta}/render/{n}_{f:02d}.png", T.amp) for f in range(N)] for n in nomes_r}
    # paleta: 12 cinzas do próprio aço (sem a casca escura dos recortes, que cai no contorno) + contorno + branco e
    # azul-gelo do raio = 15
    amostras = np.concatenate([r[m] for n in nomes_r for r, m in bru[n][::12]]).astype(np.float32)
    amostras = amostras[np.abs(amostras - np.array(ESCURA, np.float32)).sum(1) > 60]
    pal0 = C.Paleta.do_desenho(amostras, n=12, escura=ESCURA)
    pal = C.Paleta(np.vstack([pal0.cores, [[250, 252, 255]], [list(HALO)]]))
    cl = pal.clara; ih = pal.mais_proxima(HALO)
    cinzas = [i for i in range(pal.n) if i != ih]                # rampa de aço: o brilho anda nela
    pos = {i: k for k, i in enumerate(cinzas)}
    sobe = {d: np.array([cinzas[min(pos[i] + 3 * d, len(cinzas) - 1)] if i in pos else i for i in range(pal.n)], np.int16) for d in (1, 2)}
    seca = {n: [C.contorno(C.limpa(a), pal.escura, poupa_cima=False) for a in pal.encaixa_seq(bru[n], folga=FOLGA)] for n in nomes_r}
    # lasca é fina (3-4 px): o contorno por dentro comeria a lasca inteira, então nela o contorno cresce para FORA
    seca["lascas"] = []
    for a in pal.encaixa_seq(bru["lascas"], folga=FOLGA):
        a = C.limpa(a); m = a >= 0; a[ndi.binary_dilation(m) & ~m] = pal.escura; seca["lascas"].append(a)
    YY, XX = T.grade(); RR = np.hypot(XX - cxg, YY - cyg); TH = np.abs(np.degrees(np.arctan2(XX - cxg, -(YY - cyg))))
    # reflexo: duas faixas de luz descem cada asa por laço (em graus, do alto para as pontas de baixo)
    leque = []
    for f in range(N):
        a = seca["leque_a"][f]; b = seca["leque_b"][f]; o = np.where(a >= 0, a, b).astype(np.int16)
        leque.append(brilho(o, (TH - 2 * 80.0 * f / N) % 80.0, sobe, forte=2.5, fraco=6.0))
    foices = [brilho(a, (TH + 3 * 60.0 * f / N) % 60.0, sobe, forte=3.0, fraco=7.0) for f, a in enumerate(seca["foices"])]
    lascas = []
    for f, a in enumerate(seca["lascas"]):
        lascas.append(brilho(a, (YY + 2 * 24.0 * f / N + XX * 0.35) % 24.0, sobe, forte=1.0, fraco=2.0, piso=1))

    # ---- raios ---------------------------------------------------------------------------------------------------
    # (1) moldura: um raio corre por fora das pontas de cada asa, do chão até a fenda do alto, como no conceito;
    #     cada trecho estala no seu tempo (9 quadros aceso em 12), então a moldura nunca apaga inteira.
    # (2) arcos soltos entre foices vizinhas e entre lascas, com nascimento e vida próprios.
    nf = len(FOICES); nl = len(info["lascas"])
    ev = []
    for k in range(ARCOS["ff"]):
        j = int(rng.integers(0, 2 * nf)); viz = j + 1 if (j % nf) < nf - 1 else j - 1
        ev.append(dict(a=f"f{j:02d}", z=f"f{viz:02d}", b=int((k * N / ARCOS["ff"] + rng.integers(0, 5)) % N), vida=int(rng.integers(7, 11)), id=1000 + k))
    for k in range(ARCOS["ll"]):
        a = int(rng.integers(0, nl)); pa = np.array(pontos[0][f"l{a:02d}"])
        viz = sorted((c for c in range(nl) if c != a), key=lambda c: np.hypot(*(np.array(pontos[0][f"l{c:02d}"]) - pa)))[:3]
        ev.append(dict(a=f"l{a:02d}", z=f"l{viz[int(rng.integers(0, len(viz)))]:02d}", b=int((k * N / ARCOS["ll"] + rng.integers(0, 5)) % N),
                       vida=int(rng.integers(6, 10)), id=2000 + k))
    raios = []
    for f in range(N):
        vivo = np.zeros((T.ch, T.cw), np.uint8); morto = np.zeros((T.ch, T.cw), np.uint8); pt = pontos[f]
        for si, sg in enumerate((1, -1)):
            nos = moldura(pt, sg, cxg, cyg)
            for k in range(len(nos) - 1):
                idade = (f + k * 5 + si * 7) % PERIODO
                if idade < PERIODO - 3:
                    estalo(vivo, morto, nos[k], nos[k + 1], 100 * si + k + 31 * ((f + k * 5 + si * 7) // PERIODO % (N // PERIODO)), idade, PERIODO - 3)
        for e in ev:
            idade = (f - e["b"]) % N
            if idade < e["vida"]:
                estalo(vivo, morto, np.array(pt[e["a"]]), np.array(pt[e["z"]]), e["id"], idade, e["vida"], ramo=e["id"] < 2000)
        vivo[:3] = 0; morto[:3] = 0                               # nada encosta no topo da tela
        vivo = vivo > 0; morto = (morto > 0) & ~vivo
        halo = ndi.binary_dilation(vivo) & ~vivo & ~morto
        tudo = vivo | morto | halo
        casca = ndi.binary_dilation(tudo, structure=np.ones((3, 3))) & ~tudo
        L = np.full((T.ch, T.cw), -1, np.int16)
        L[casca] = pal.escura; L[halo] = ih; L[morto] = ih; L[vivo] = cl
        raios.append(L)

    # ---- limalha: pó de aço subindo, piscando, nascendo nas lascas e ao longo do chão ----------------------------
    lim_s = C.semeia(rng, LIMALHA, dict(b=lambda i, r: int((i * N / LIMALHA + r.integers(0, 9)) % N), vida=("int", 42, 84), v=("uni", 0.35, 0.85),
                                        dx=("uni", -0.12, 0.12), amp=("uni", 0.8, 3.2), w=("uni", 0.08, 0.2), ph=("uni", 0, 6.28),
                                        onde=("int", 0, 10), k=("int", 0, nl), xr=("uni", cxg - 75, cxg + 75), yr=("uni", 176, 190)))
    for sd in lim_s:
        if sd["onde"] < 6:
            sd["x"], sd["y"] = pontos[sd["b"]][f"l{sd['k']:02d}"]
        else:
            sd["x"], sd["y"] = sd["xr"], sd["yr"]
    desce = lambda i, d: cinzas[max(pos.get(i, len(cinzas) - 1) - d, 1)]

    def des_lim(L, sd, a, f, i):
        x = sd["x"] + sd["dx"] * a + sd["amp"] * math.sin(sd["w"] * a + sd["ph"]) * min(1.0, a / 12.0); y = sd["y"] - sd["v"] * a
        t = a / sd["vida"]
        c = cl if t < 0.3 else (desce(cl, 2) if t < 0.6 else (desce(cl, 5) if t < 0.85 else desce(cl, 8)))
        if (a + i * 3) % 7 == 0:
            c = cl                                                          # pisca
        xi, yi = int(round(x)), int(round(y))
        if yi < 3:
            return True
        C.ponto(L, xi, yi, c)
        if sd["v"] > 0.6 and t < 0.6:
            C.ponto(L, xi, yi + 1, desce(c, 3))                             # rabicho de quem sobe depressa
        return True

    limalha = []
    for f in range(N):
        L = np.full((T.ch, T.cw), -1, np.int16); C.emite(L, f, N, lim_s, des_lim); limalha.append(L)

    # ---- saída: camadas NA ORDEM DE DESENHO ----------------------------------------------------------------------
    CAM = {"leque": leque, "foices": foices, "raios": raios, "lascas": lascas, "limalha": limalha}
    oq = dict(leque="leque duplo de lâminas, aberto embaixo: duas asas de 9 lâminas (tesouras cortando, pentes, facas, navalhas) e a adaga "
                    "do meio; cada asa abre e fecha em cascata, de cima para baixo, e as lâminas estocam em onda; atrás, pontas e o miolo",
              foices="coração de 12 foices em volta do corpo (6 de cada lado), cada uma abre como garra, a de cima primeiro",
              raios="moldura de raio branco com clarão azul-gelo por fora das pontas das duas asas, do chão à fenda do alto, mais arcos "
                    "entre as foices e entre as lascas",
              lascas="lascas de aço cravadas no chão, tremendo", limalha="limalha de aço subindo e piscando")
    C.exporta_camadas(cam, CAM, pal)
    C.escreve_aura_json(cam, ID, AURA, T, TIQ, [dict(nome=n, quadros=N, plano="atras", o_que=oq[n]) for n in CAM], pal,
                        extras=dict(gerado_por="ferramentas/aura_blender/" + os.path.basename(__file__), centro_do_leque=[round(cxg, 1), round(cyg, 1)],
                                    nota="Todas as camadas têm 96 quadros e rodam juntas (o raio acompanha as pontas das lâminas quadro a "
                                         "quadro): não rode uma camada em laço diferente das outras."))
    # ---- medidas -------------------------------------------------------------------------------------------------
    med = dict(C.mede_conjunto(CAM, pal, N))
    for n, lst in CAM.items():
        med[n] = C.mede_camada(lst, pal); med[n].update(miolo_e_silhueta(lst))
    med["leque_sem_brilho"] = miolo_e_silhueta([np.where(a >= 0, a, b).astype(np.int16) for a, b in zip(seca["leque_a"], seca["leque_b"])])
    med["raios"]["pixels_por_quadro_min_max"] = [int(min((r >= 0).sum() for r in raios)), int(max((r >= 0).sum() for r in raios))]
    med["raios"]["brancos_por_quadro_min"] = int(min((r == cl).sum() for r in raios))
    med["raios"]["y_min"] = int(min(np.where(r >= 0)[0].min() for r in raios))
    uni = np.any([np.stack(CAM[n]) >= 0 for n in ("leque", "foices")], axis=(0, 1)); ys, xs = np.where(uni)
    c_rgb, c_m = C.reduz(C.conceito_para_4x(f"{rec}/corpo.png", C.Tela(cx=info["cx"] - info["dx"], chao=info["sola_v1"], escala=T.escala)), T.amp)
    cy, cx_ = np.where(c_m)
    baixo = uni[150:, 150:211]                                   # o vão de baixo: entre as pernas, do joelho ao chão
    med["tamanho"] = dict(leque_largura_px=int(xs.max() - xs.min() + 1), leque_altura_px=int(ys.max() - ys.min() + 1), leque_topo_y=int(ys.min()),
                          leque_base_y=int(ys.max()), leque_x=[int(xs.min()), int(xs.max())],
                          corpo_altura_com_bobinas_px=int(cy.max() - cy.min() + 1), corpo_largura_px=int(cx_.max() - cx_.min() + 1),
                          corpo_altura_cabelo_sola_px=round(ALTURA_CORPO * T.escala, 1), escala=round(T.escala, 4),
                          leque_largura_sobre_altura_do_corpo=round((xs.max() - xs.min() + 1) / (ALTURA_CORPO * T.escala), 2),
                          pixels_de_lamina_no_vao_de_baixo=int(baixo.sum()))
    med["paleta_cores"] = pal.n; med["paleta_menor_distancia_entre_cores"] = round(float(min(
        np.abs(pal.cores[i].astype(int) - pal.cores[j].astype(int)).sum() for i in range(pal.n) for j in range(i))), 1)
    med["chicote"] = chicote(pasta, mostra=False)
    json.dump(med, open(f"{pasta}/medidas.json", "w"), indent=1)
    for k, v in med.items():
        print(k, v)
    # ---- tiras e vídeo (corpo na frente, fundo escuro neutro) ----------------------------------------------------
    corpo = np.dstack([np.clip(c_rgb, 0, 255).astype(np.uint8), (c_m * 255).astype(np.uint8)]); corpo[~c_m] = 0
    fundo = C.fundo_teste(T)
    Q = [C.compoe(fundo, f, CAM.values(), corpo, [], pal) for f in range(N)]
    S = [C.compoe(fundo, f, CAM.values(), None, [], pal) for f in range(N)]
    rot = lambda fs: [f"q{f % N:02d}" for f in fs]
    C.tira([Q[f] for f in range(16)], f"{pasta}/tira.png", rotulos=rot(range(16)))
    C.tira([Q[f % N] for f in range(0, N, 6)], f"{pasta}/tira_ciclo.png", rotulos=rot(range(0, N, 6)))
    za = (slice(0, 110), slice(180, 300)); zb = (slice(60, 170), slice(60, 180))
    C.tira([Q[f][za] for f in range(10, 18)], f"{pasta}/tira_zoom_a.png", cols=4, esc=4, rotulos=rot(range(10, 18)))
    C.tira([Q[f][zb] for f in range(10, 18)], f"{pasta}/tira_zoom_b.png", cols=4, esc=4, rotulos=rot(range(10, 18)))
    C.tira([Q[f % N][zb] for f in range(N - 4, N + 4)], f"{pasta}/tira_zoom_emenda.png", cols=4, esc=4, rotulos=rot(range(N - 4, N + 4)))
    C.tira([S[f] for f in (0, 12, 24, 36)], f"{pasta}/tira_sem_corpo.png", cols=2, esc=3, rotulos=rot((0, 12, 24, 36)))
    C.video_laco(f"{pasta}/aura_raiclaven.mp4", Q, TIQ)


def miolo_e_silhueta(lst):
    """As duas medidas do cético: % dos pixels de dentro (opacos nos dois quadros) que trocam de cor de um quadro
    para o outro, e % da silhueta que muda (entra ou sai) sobre a união. Médias no laço."""
    n = len(lst); mi = []; si = []
    for f in range(n):
        a, b = lst[f], lst[(f + 1) % n]; d = (a >= 0) & (b >= 0); u = (a >= 0) | (b >= 0)
        mi.append(float(((a != b) & d).sum() / max(d.sum(), 1))); si.append(float(((a >= 0) != (b >= 0)).sum() / max(u.sum(), 1)))
    return dict(miolo_muda_pct=round(100 * float(np.mean(mi)), 1), silhueta_muda_pct=round(100 * float(np.mean(si)), 1))


def instala(pasta):
    C.instala(os.path.join(pasta, "camadas"), os.path.join(C.RAIZ, "sprites", ID, "aura"))


def chicote(pasta, mostra=True):
    """Passo por quadro de cada ponta e a cascata das asas: a fase (em quadros) do abre-e-fecha de cada casa tem de
    CRESCER de cima para baixo (a casa de baixo chega depois)."""
    dados = json.load(open(f"{pasta}/render/pontos.json")); pontos = dados["pontos"]; cx, cy = dados["centro"]; res = {}
    for ch in pontos[0]:
        xy = np.array([pontos[F % N][ch] for F in range(N + 1)])
        st = np.hypot(*np.diff(xy, axis=0).T)
        res[ch] = dict(passo_max=round(float(st.max()), 2), passo_medio=round(float(st.mean()), 2), passo_emenda=round(float(st[-1]), 2),
                       passo_vizinho_da_emenda=round(float(st[-2]), 2), curso_x=round(float(np.ptp(xy[:, 0])), 1),
                       curso_y=round(float(np.ptp(xy[:, 1])), 1))
    resumo = {}
    for pre, nome in (("a", "laminas_da_frente"), ("b", "pontas_de_tras"), ("h", "miolo"), ("f", "foices"), ("l", "lascas")):
        v = [r for k, r in res.items() if k.startswith(pre)]
        resumo[nome] = dict(pontas=len(v), passo_max=max(r["passo_max"] for r in v), passo_medio=round(float(np.mean([r["passo_medio"] for r in v])), 2),
                            emenda_max=max(r["passo_emenda"] for r in v), curso_max_px=max(max(r["curso_x"], r["curso_y"]) for r in v))
    t = np.arange(N); na = len(ASA)
    for nome, k0 in (("asa_direita", 1), ("asa_esquerda", 1 + na)):
        fases = []; cursos = []
        for p in range(na):
            xy = np.array([ponta_de_fora(pontos[f], f"a{k0 + p:02d}") for f in range(N)])
            ang = np.degrees(np.unwrap(np.arctan2(xy[:, 0] - cx, -(xy[:, 1] - cy)))); ang = np.abs(ang)
            c = ((ang - ang.mean()) * np.exp(-2j * np.pi * 2 * t / N)).sum()
            fases.append(round(float((-np.angle(c) / (2 * np.pi) * (N / 2)) % (N / 2)), 1)); cursos.append(round(float(np.ptp(ang)), 1))
        resumo[nome] = dict(fase_do_abre_fecha_em_quadros_de_cima_para_baixo=fases, curso_em_graus=cursos)
    if mostra:
        for k, v in resumo.items():
            print(k, v)
    json.dump(dict(resumo=resumo, pontas=res), open(f"{pasta}/chicote.json", "w"), indent=1)
    return resumo


if __name__ == "__main__":
    import tempfile
    C.roda(__file__, {"recortes": recortes, "rig": rig, "chicote": chicote, "compor": compor, "instala": instala}, os.path.join(tempfile.gettempdir(), "aura_blender", ID))
