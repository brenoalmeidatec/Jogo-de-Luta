"""Aura do Raiclaven endiabrado: LEQUE DE LÂMINAS DE AÇO (docs/arcade/aura_blender.md).

As lâminas do conceito aprovado (e_conceito.png) são recortadas uma a uma, postas de pé e redistribuídas em anéis
regulares em volta do centro do leque, para o giro fechar em laço sem emenda:
  - anel de fora  : 24 peças, 6 tipos x 4 voltas (tesoura grande, adaga, pente, faca, tesoura pequena, navalha);
                    gira +90 graus por laço (anda 6 casas: o quadro 96 é igual ao 0);
  - anel de trás  : 24 pontas de adaga nas meias-casas, mais curtas, gira +45 graus e pulsa mais fundo;
  - anel de foices: 10 foices, gira -180 graus por laço (o dobro e ao contrário).
Cada tesoura são DUAS metades rígidas (recorte das duas metades; a de baixo é o espelho da lâmina + a argola
do desenho) girando em torno do parafuso. Arcos elétricos, brilho correndo, lascas no chão e limalha são camadas
em Python por cima.

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
RAIO_FORA = dict(tesoura_g=368.0, adaga=388.0, pente=352.0, faca=384.0, tesoura_p=366.0, navalha=392.0, ponta=335.0)
ANEL_A = ["tesoura_g", "adaga", "pente", "faca", "tesoura_p", "navalha"]     # o padrão que se repete 4 vezes
NA, NB, NF = 24, 24, 10
GIRO_A, GIRO_B, GIRO_F = 90.0, 45.0, -180.0                                  # graus por laço
ESCALA_A, ESCALA_B = 1.2, 1.3          # em 1/4 a lâmina do tamanho do conceito fica um fiapo: engorda um pouco
ESCALA_FOICE = 1.45                  # a foice do recorte é das menores do desenho
RAIO_FOICE = 205.0                   # raio do meio da foice
LASCAS_Y = 652                       # abaixo disto, fora do corpo, é lasca cravada no chão
ESCURA = (26, 28, 34)                # contorno: grafite quase preto, sem roxo
MARG = 14                            # margem do recorte posto de pé


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
# Fase de cada peça. Um anel de n casas que anda d casas por laço só emenda se o estado da peça i no quadro N for o
# da peça i+d no quadro 0. Com fase = 2*pi*(m*f/N - w*i/n) isso pede m = k - w*d/n (k inteiro): a onda dá w voltas no
# anel e o número de ciclos por laço NÃO é inteiro; é o giro que fecha a conta.
PASSO_A, PASSO_B, PASSO_F = 6, 3, -5          # casas por laço (GIRO / (360 / n))


def ciclos(k, w, d, n):
    return k - w * d / n


def fase(i, f, k, w, d, n):
    return 2 * math.pi * (ciclos(k, w, d, n) * f / N - w * i / n)


# flexão por osso: (amplitude em graus, atraso em fração do ciclo). Aço vibra pouco; a cascata vem da onda no anel.
FLEXAO = {
    "adaga": [(0.5, 0.00), (1.0, 0.07), (1.8, 0.15), (3.0, 0.24)],
    "pente": [(0.8, 0.00), (2.2, 0.10), (3.8, 0.21)],
    "faca": [(0.6, 0.00), (2.6, 0.10), (2.0, 0.20)],
    "navalha": [(0.5, 0.00), (0.8, 0.05), (7.0, 0.12), (1.6, 0.21)],     # a lâmina dobra no cabo (abre e fecha um pouco)
    "ponta": [(1.0, 0.00), (2.2, 0.12)],
    "foice": [(7.0, 0.00), (4.0, 0.08), (6.0, 0.17)],                    # a foice abre como garra
}
RESPIRA_A, BALANCO_A = 9.0, 2.2      # px do conceito no raio; graus
RESPIRA_B = 22.0
RESPIRA_F = 7.0
ABRE = 6.5                           # cada metade da tesoura abre de 0 a 2*ABRE graus


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

    def anel(nome, giro):
        e = vazio(nome); e.location = (cxb, 0, czb)
        C.bl_anima_objeto(e, N, lambda t: dict(rotation_euler=(0, math.radians(giro) * t / (2 * math.pi), 0)))
        return e

    def cadeia(nome, tipo, pts):
        ossos = [(f"o{j}", f"o{j - 1}" if j else None, pts[j], pts[j + 1]) for j in range(len(pts) - 1)]
        return C.bl_malha_com_ossos(nome, f"{rec}/{tipo}.png", ossos, TP, N, celula=6, margem=6)

    def segura(e, alfa, raio_fn, bal_fn, y, tangente=0.0, quarto=False):
        """Põe o vazio `e` (filho do anel) na casa de ângulo alfa: +Z local aponta para fora (ou +X, se quarto)."""
        def fn(t):
            f = t * N / (2 * math.pi)
            r = raio_fn(f); a = math.radians(alfa)
            x, z = r * math.sin(a) + tangente * -math.cos(a), r * math.cos(a) + tangente * math.sin(a)
            return dict(location=(x, y, z), rotation_euler=(0, a - (math.pi / 2 if quarto else 0) + math.radians(bal_fn(f)), 0))
        C.bl_anima_objeto(e, N, fn)

    A = anel("anel_a", GIRO_A); B = anel("anel_b", GIRO_B); F = anel("anel_f", GIRO_F)
    leque_a, leque_b, foices, lascas = [], [], [], []
    tips = []        # (chave, armação, osso)

    # anel de trás: pontas de adaga nas meias-casas
    d = P["ponta"]; pts = [d["dentro"], [(d["dentro"][0] + d["fora"][0]) / 2, (d["dentro"][1] + d["fora"][1]) / 2], d["fora"]]
    comp = (d["dentro"][1] - d["fora"][1]) * s * ESCALA_B
    for i in range(NB):
        pc = cadeia(f"b{i:02d}", "ponta", pts); ao = pc["arm"]; ao.parent = B; ao.rotation_mode = "XYZ"
        ao.scale = (ESCALA_B, 1, ESCALA_B)
        r0 = RAIO_FORA["ponta"] * s - comp
        segura(ao, (i + 0.5) * 360.0 / NB, lambda f, i=i: r0 + RESPIRA_B * s * math.sin(fase(i, f, 2, 2, PASSO_B, NB)),
               lambda f, i=i: 1.5 * math.sin(fase(i, f, 2, 2, PASSO_B, NB) - 1.3), 4.0 + 0.01 * i)
        anima_ossos(ao, {f"o{j}": (lambda f, i=i, a=a, l=l: a * math.sin(fase(i, f, 2, 2, PASSO_B, NB) - 2 * math.pi * l))
                         for j, (a, l) in enumerate(FLEXAO["ponta"])})
        leque_b.append(pc["malha"]); tips.append((f"b{i:02d}", ao, "o1"))

    # anel de fora
    for i in range(NA):
        tipo = ANEL_A[i % len(ANEL_A)]; d = P[tipo]; alfa = i * 360.0 / NA
        fr = lambda f, i=i: fase(i, f, 2, 3, PASSO_A, NA)                 # respiração: 3 cristas no anel, 1,25 ciclo por laço
        ff = lambda f, i=i: fase(i, f, 2, 2, PASSO_A, NA)                 # flexão
        ft = lambda f, i=i: fase(i, f, 3, 5, PASSO_A, NA)                 # tesoura: 1,75 ciclo; vizinhas a 5/24 de ciclo
        bal = lambda f, fr=fr: BALANCO_A * math.sin(fr(f) - 1.2)
        y = 1.0 + 0.02 * (i % 6) + 0.2 * (i % 2)
        if tipo.startswith("tesoura"):
            pv = d["pivo"]; comp = (pv[1] - d["fora"][1]) * s * ESCALA_A; r0 = RAIO_FORA[tipo] * s - comp
            e = vazio(f"a{i:02d}", A); e.scale = (ESCALA_A, 1, ESCALA_A)
            segura(e, alfa, lambda f, r0=r0, fr=fr: r0 + RESPIRA_A * s * math.sin(fr(f)), bal, y)
            lado = 1.0 if d["argola_b"][0] > pv[0] else -1.0             # a lâmina de A abre para o lado da argola de B
            for m, arg, sg, dy in (("a", d["argola_a"], -lado, 0.0), ("b", d["argola_b"], lado, 0.05)):
                ossos = [("lam", None, pv, d["dentro"]), ("cabo", "lam", pv, arg)]
                pc = C.bl_malha_com_ossos(f"a{i:02d}{m}", f"{rec}/{tipo}_{m}.png", ossos, TP, N, celula=6, margem=6)
                pc["arm"].parent = e; pc["arm"].location = (0, dy, 0)
                ab = lambda f, ft=ft, sg=sg: sg * ABRE * (1 - math.cos(ft(f)))
                anima_ossos(pc["arm"], {"lam": ab})                      # o cabo é filho da lâmina: a metade gira inteira
                leque_a.append(pc["malha"]); tips.append((f"a{i:02d}" + ("" if m == "a" else "x"), pc["arm"], "cabo"))
        else:
            pts = d["espinha"]; comp = (pts[0][1] - d["fora"][1]) * s * ESCALA_A; r0 = RAIO_FORA[tipo] * s - comp
            pc = cadeia(f"a{i:02d}", tipo, pts); ao = pc["arm"]; ao.parent = A; ao.rotation_mode = "XYZ"
            ao.scale = (ESCALA_A, 1, ESCALA_A)
            segura(ao, alfa, lambda f, r0=r0, fr=fr: r0 + RESPIRA_A * s * math.sin(fr(f)), bal, y)
            anima_ossos(ao, {f"o{j}": (lambda f, ff=ff, a=a, l=l: a * math.sin(ff(f) - 2 * math.pi * l))
                             for j, (a, l) in enumerate(FLEXAO[tipo])})
            leque_a.append(pc["malha"]); tips.append((f"a{i:02d}", ao, f"o{len(pts) - 2}"))

    # anel de foices: corda na tangente, barriga para fora; cada uma abre como garra a partir da ponta de trás
    d = P["foice"]; pts = d["espinha"]; comp = (pts[0][1] - d["fora"][1]) * s
    for i in range(NF):
        pc = cadeia(f"f{i:02d}", "foice", pts); ao = pc["arm"]; ao.parent = F; ao.rotation_mode = "XYZ"
        ao.scale = (ESCALA_FOICE, 1, ESCALA_FOICE)
        fg_ = lambda f, i=i: fase(i, f, 2, 1, PASSO_F, NF)                # garra: 2,5 ciclos por laço, vizinhas a 1/10
        fr = lambda f, i=i: fase(i, f, 2, 2, PASSO_F, NF)
        segura(ao, i * 360.0 / NF, lambda f, fr=fr: (RAIO_FOICE - 22) * s + RESPIRA_F * s * math.sin(fr(f)), lambda f: 0.0,
               0.0 + 0.03 * (i % 3), tangente=-comp * ESCALA_FOICE / 2, quarto=True)
        anima_ossos(ao, {f"o{j}": (lambda f, fg_=fg_, a=a, l=l, j=j: a * (math.sin(fg_(f) - 2 * math.pi * l) + (2.2 if j == 0 else 0.0)))
                         for j, (a, l) in enumerate(FLEXAO["foice"])})
        foices.append(pc["malha"]); tips.append((f"f{i:02d}", ao, "o2"))

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
RAIOS = dict(aa=28, fa=10, ll=8)    # arcos por laço: ponta-ponta do anel de fora, foice-ponta, lasca-lasca
LIMALHA = 80


def brilho(idx, f, RR, TH, pal, L=44.0, bracos=3, voltas=2, sentido=1, piso=2):
    """Brilho especular correndo pelas lâminas: uma espiral clara que anda para fora `voltas` vezes por laço.
    Só mexe no que já é aço (não cria pixel) e fecha o laço porque voltas e bracos são inteiros."""
    u = (RR - voltas * L * f / N - sentido * L * bracos * TH / (2 * math.pi)) % L
    m = idx >= piso
    out = idx.copy()
    fraco = m & (u >= 1.2) & (u < 3.6); forte = m & (u < 1.2)
    out[fraco] = np.minimum(idx[fraco] + 3, pal.clara); out[forte] = np.minimum(idx[forte] + 6, pal.clara)
    return out


def tracado(p0, p1, sd, idade):
    """Pontos do arco entre p0 e p1 na idade dada: ondulação suave que escorre + tremida que troca a cada 3 quadros."""
    d = p1 - p0; L = float(np.hypot(*d)) + 1e-6; n = max(3, int(L / 5)); s = np.linspace(0, 1, n + 1)
    perp = np.array([-d[1], d[0]]) / L; env = np.sin(math.pi * s)
    A = min(5.0, 0.13 * L + 1.0)
    suave = sum(sd["c"][h] * np.sin(2 * math.pi * (h + 1) * s * sd["k"][h] + sd["ph"][h] + sd["w"][h] * idade) for h in range(3))
    jit = np.random.default_rng(sd["id"] * 131 + idade // 3).uniform(-1, 1, n + 1)
    off = env * A * (0.5 * suave + 0.8 * jit) + sd["barriga"] * env * 0.14 * L
    return p0 + s[:, None] * d + off[:, None] * perp


def risca(L, pts, miolo, casca, grosso=False, falha=None):
    """Desenha o arco em 1x: casca (contorno) por baixo, miolo claro por cima. falha: fração de trechos apagados."""
    import cv2
    q = np.round(pts).astype(np.int32)
    mc = np.zeros(L.shape, np.uint8); mm = np.zeros(L.shape, np.uint8)
    for j in range(len(q) - 1):
        if falha is not None and falha[j % len(falha)]:
            continue
        cv2.line(mc, tuple(int(v) for v in q[j]), tuple(int(v) for v in q[j + 1]), 1, 3)
        cv2.line(mm, tuple(int(v) for v in q[j]), tuple(int(v) for v in q[j + 1]), 1, 2 if grosso else 1)
    if casca is not None:
        L[(mc > 0) & (L < 0)] = casca
    L[mm > 0] = miolo


def compor(pasta):
    from scipy import ndimage as ndi
    rec = os.path.join(pasta, "recortes"); cam = os.path.join(pasta, "camadas")
    info = json.load(open(f"{rec}/info.json")); T = tela(info)
    dados = json.load(open(f"{pasta}/render/pontos.json")); pontos = dados["pontos"]; cxg, cyg = dados["centro"]
    rng = np.random.default_rng(11)
    nomes_r = ("leque_b", "leque_a", "foices", "lascas")
    bru = {n: [C.le_render(f"{pasta}/render/{n}_{f:02d}.png", T.amp) for f in range(N)] for n in nomes_r}
    # paleta: 13 cinzas do próprio aço + o contorno + um branco para o raio e o brilho = 15
    amostras = np.concatenate([r[m] for n in nomes_r for r, m in bru[n][::12]])
    pal0 = C.Paleta.do_desenho(amostras, n=13, escura=ESCURA)
    pal = C.Paleta(np.vstack([pal0.cores, [[250, 252, 255]]]))
    seca = {n: [C.contorno(C.limpa(a), pal.escura, poupa_cima=False) for a in pal.encaixa_seq(bru[n], folga=160.0)] for n in nomes_r}
    # lasca é fina (3-4 px): o contorno por dentro comeria a lasca inteira, então nela o contorno cresce para FORA
    seca["lascas"] = []
    for a in pal.encaixa_seq(bru["lascas"], folga=160.0):
        a = C.limpa(a); m = a >= 0; a[ndi.binary_dilation(m) & ~m] = pal.escura; seca["lascas"].append(a)
    YY, XX = T.grade(); RR = np.hypot(XX - cxg, YY - cyg); TH = np.arctan2(XX - cxg, -(YY - cyg))
    leque = []
    for f in range(N):
        a = seca["leque_a"][f]; b = seca["leque_b"][f]; o = np.where(a >= 0, a, b).astype(np.int16)
        leque.append(brilho(o, f, RR, TH, pal))
    foices = [brilho(a, f, RR, TH, pal, L=30.0, bracos=2, voltas=3, sentido=-1) for f, a in enumerate(seca["foices"])]
    # lascas: o brilho desce por elas (faixa horizontal que sobe 2 vezes por laço)
    lascas = []
    for f, a in enumerate(seca["lascas"]):
        u = (YY + 2 * 24.0 * f / N + XX * 0.35) % 24.0
        o = a.copy(); m = (a >= 1) & (u < 2.0); o[m] = np.minimum(a[m] + 4, pal.clara); lascas.append(o)

    # ---- raios: arcos entre pontas, cada um com nascimento, vida e traçado próprios -------------------------------
    cl = pal.clara; casca = 2; meio = cl - 3
    ach = lambda i: f"a{i:02d}"
    sem = []
    def nova(tipo, a, b_, k, tot):
        return dict(id=len(sem), tipo=tipo, a=a, z=b_, b=int((k * N / tot + rng.integers(0, 7)) % N), vida=int(rng.integers(7, 12)),
                    c=rng.uniform(0.4, 1.0, 3) * rng.choice([-1, 1], 3), k=rng.uniform(0.5, 1.4, 3), ph=rng.uniform(0, 6.28, 3),
                    w=rng.uniform(0.25, 0.7, 3) * rng.choice([-1, 1], 3), barriga=float(rng.uniform(-1, 1)),
                    ramo=float(rng.uniform(0.2, 0.8)), ramo_ang=float(rng.uniform(0.5, 1.1) * rng.choice([-1, 1])), ramo_l=float(rng.uniform(5, 11)))
    for k in range(RAIOS["aa"]):
        i = int(rng.integers(0, NA)); sem.append(nova("aa", ach(i), ach((i + int(rng.integers(1, 3))) % NA), k, RAIOS["aa"]))
    for k in range(RAIOS["fa"]):
        j = int(rng.integers(0, NF)); s0 = nova("fa", f"f{j:02d}", None, k, RAIOS["fa"])
        pf = np.array(pontos[s0["b"]][s0["a"]])
        s0["z"] = min((ach(i) for i in range(NA)), key=lambda c: np.hypot(*(np.array(pontos[s0["b"]][c]) - pf))); sem.append(s0)
    nl = len(info["lascas"])
    for k in range(RAIOS["ll"]):
        a = int(rng.integers(0, nl)); pa = np.array(pontos[0][f"l{a:02d}"])
        viz = sorted((c for c in range(nl) if c != a), key=lambda c: np.hypot(*(np.array(pontos[0][f"l{c:02d}"]) - pa)))[:3]
        sem.append(nova("ll", f"l{a:02d}", f"l{viz[int(rng.integers(0, len(viz)))]:02d}", k, RAIOS["ll"]))
    raios = [np.full((T.ch, T.cw), -1, np.int16) for _ in range(N)]
    for sd in sem:
        for idade in range(sd["vida"]):
            F = sd["b"] + idade
            p0 = np.array(ponto(pontos, sd["a"], F)); p1 = np.array(ponto(pontos, sd["z"], F))
            pts = tracado(p0, p1, sd, idade); L = raios[F % N]
            morre = idade >= sd["vida"] - 2
            falha = (np.random.default_rng(sd["id"] * 7 + idade).uniform(0, 1, 16) < 0.45) if morre else None
            j = int(sd["ramo"] * (len(pts) - 2)) + 1                    # ramo: sai de um nó do arco e treme junto
            if not morre:
                d = pts[j + 1] - pts[j - 1]; ang = math.atan2(d[1], d[0]) + sd["ramo_ang"]
                fim = pts[j] + sd["ramo_l"] * np.array([math.cos(ang), math.sin(ang)])
                risca(L, tracado(pts[j], fim, dict(sd, id=sd["id"] + 500, barriga=0.0), idade), meio, casca)
            risca(L, pts, meio if morre else cl, None if morre else casca, grosso=idade < 2, falha=falha)
    # ---- limalha: pó de aço subindo, piscando, nascendo nas lascas e ao longo do chão ----------------------------
    lim_s = C.semeia(rng, LIMALHA, dict(b=lambda i, r: int((i * N / LIMALHA + r.integers(0, 9)) % N), vida=("int", 42, 84), v=("uni", 0.35, 0.85),
                                        dx=("uni", -0.12, 0.12), amp=("uni", 0.8, 3.2), w=("uni", 0.08, 0.2), ph=("uni", 0, 6.28),
                                        onde=("int", 0, 10), k=("int", 0, nl), xr=("uni", cxg - 75, cxg + 75), yr=("uni", 176, 190)))
    for sd in lim_s:
        if sd["onde"] < 6:
            sd["x"], sd["y"] = pontos[sd["b"]][f"l{sd['k']:02d}"]
        else:
            sd["x"], sd["y"] = sd["xr"], sd["yr"]

    def des_lim(L, sd, a, f, i):
        x = sd["x"] + sd["dx"] * a + sd["amp"] * math.sin(sd["w"] * a + sd["ph"]) * min(1.0, a / 12.0); y = sd["y"] - sd["v"] * a
        t = a / sd["vida"]
        c = cl if t < 0.3 else (cl - 2 if t < 0.6 else (cl - 5 if t < 0.85 else cl - 8))
        if (a + i * 3) % 7 == 0:
            c = cl                                                          # pisca
        xi, yi = int(round(x)), int(round(y))
        C.ponto(L, xi, yi, c)
        if sd["v"] > 0.6 and t < 0.6:
            C.ponto(L, xi, yi + 1, max(c - 3, 1))                           # rabicho de quem sobe depressa
        return True

    limalha = []
    for f in range(N):
        L = np.full((T.ch, T.cw), -1, np.int16); C.emite(L, f, N, lim_s, des_lim); limalha.append(L)

    # ---- saída: camadas NA ORDEM DE DESENHO ----------------------------------------------------------------------
    CAM = {"leque": leque, "foices": foices, "raios": raios, "lascas": lascas, "limalha": limalha}
    oq = dict(leque="anel de fora (24 lâminas, gira 90 graus por laço) sobre o anel de trás (24 pontas, 45 graus); tesouras abrindo e fechando",
              foices="anel de 10 foices, gira 180 graus por laço no sentido contrário, cada foice abre como garra",
              raios="arcos elétricos branco-prata entre as pontas das lâminas, das foices e das lascas",
              lascas="lascas de aço cravadas no chão, tremendo", limalha="limalha de aço subindo e piscando")
    C.exporta_camadas(cam, CAM, pal)
    C.escreve_aura_json(cam, ID, AURA, T, TIQ, [dict(nome=n, quadros=N, plano="atras", o_que=oq[n]) for n in CAM], pal,
                        extras=dict(gerado_por="ferramentas/aura_blender/" + os.path.basename(__file__), centro_do_leque=[round(cxg, 1), round(cyg, 1)],
                                    nota="Todas as camadas têm 96 quadros e rodam juntas. O leque só emenda porque os anéis são simétricos: "
                                         "não troque o número de quadros de uma camada sem refazer o giro."))
    # ---- medidas -------------------------------------------------------------------------------------------------
    med = dict(C.mede_conjunto(CAM, pal, N))
    for n, lst in CAM.items():
        med[n] = C.mede_camada(lst, pal)
    med["leque_sem_brilho"] = C.mede_camada([np.where(a >= 0, a, b).astype(np.int16) for a, b in zip(seca["leque_a"], seca["leque_b"])], pal)
    uni = np.any([np.stack(CAM[n]) >= 0 for n in ("leque", "foices")], axis=(0, 1)); ys, xs = np.where(uni)
    c_rgb, c_m = C.reduz(C.conceito_para_4x(f"{rec}/corpo.png", C.Tela(cx=info["cx"] - info["dx"], chao=info["sola_v1"], escala=T.escala)), T.amp)
    cy, cx_ = np.where(c_m)
    med["tamanho"] = dict(leque_largura_px=int(xs.max() - xs.min() + 1), leque_altura_px=int(ys.max() - ys.min() + 1), leque_topo_y=int(ys.min()),
                          leque_base_y=int(ys.max()), leque_x=[int(xs.min()), int(xs.max())],
                          corpo_altura_com_bobinas_px=int(cy.max() - cy.min() + 1), corpo_largura_px=int(cx_.max() - cx_.min() + 1),
                          corpo_altura_cabelo_sola_px=round(ALTURA_CORPO * T.escala, 1), escala=round(T.escala, 4),
                          leque_sobre_altura_do_corpo=round((xs.max() - xs.min() + 1) / (ALTURA_CORPO * T.escala), 2))
    med["paleta_cores"] = pal.n; med["chicote"] = chicote(pasta, mostra=False)
    json.dump(med, open(f"{pasta}/medidas.json", "w"), indent=1)
    for k, v in med.items():
        print(k, v)
    # ---- tiras e vídeo (corpo na frente, fundo escuro neutro) ----------------------------------------------------
    corpo = np.dstack([np.clip(c_rgb, 0, 255).astype(np.uint8), (c_m * 255).astype(np.uint8)]); corpo[~c_m] = 0
    fundo = C.fundo_teste(T)
    Q = [C.compoe(fundo, f, CAM.values(), corpo, [], pal) for f in range(N)]
    rot = lambda fs: [f"q{f % N:02d}" for f in fs]
    C.tira([Q[f] for f in range(16)], f"{pasta}/tira.png", rotulos=rot(range(16)))
    C.tira([Q[f % N] for f in range(0, N, 6)], f"{pasta}/tira_ciclo.png", rotulos=rot(range(0, N, 6)))
    za = (slice(0, 100), slice(170, 290)); zb = (slice(100, 200), slice(60, 180))
    C.tira([Q[f][za] for f in range(20, 28)], f"{pasta}/tira_zoom_a.png", cols=4, esc=4, rotulos=rot(range(20, 28)))
    C.tira([Q[f % N][zb] for f in range(N - 4, N + 4)], f"{pasta}/tira_zoom_emenda.png", cols=4, esc=4, rotulos=rot(range(N - 4, N + 4)))
    C.tira([C.compoe(fundo, f, CAM.values(), None, [], pal) for f in (0, N // 2)], f"{pasta}/tira_sem_corpo.png", cols=2, esc=3)
    C.video_laco(f"{pasta}/aura_raiclaven.mp4", Q, TIQ)


def instala(pasta):
    C.instala(os.path.join(pasta, "camadas"), os.path.join(C.RAIZ, "sprites", ID, "aura"))


ANEIS = {"a": (NA, PASSO_A), "b": (NB, PASSO_B), "f": (NF, PASSO_F), "l": (1, 0)}


def irma(ch, voltas=1):
    """A peça que, `voltas` laços depois, está onde a peça `ch` estaria (o anel andou d casas por laço)."""
    n, d = ANEIS[ch[0]]
    if d == 0:
        return ch
    return f"{ch[0]}{(int(ch[1:3]) + d * voltas) % n:02d}{ch[3:]}"


def ponto(pontos, ch, F):
    """Posição da ponta `ch` no quadro F de uma linha do tempo sem fim (F pode passar de N)."""
    return pontos[F % N][irma(ch, F // N)]


def chicote(pasta, mostra=True):
    """Passo por quadro de cada ponta, contando a emenda (o quadro N da peça i é o quadro 0 da peça i+d)."""
    pontos = json.load(open(f"{pasta}/render/pontos.json"))["pontos"]; res = {}
    for ch in pontos[0]:
        xy = np.array([ponto(pontos, ch, F) for F in range(N + 1)])
        st = np.hypot(*np.diff(xy, axis=0).T)
        res[ch] = dict(passo_max=round(float(st.max()), 2), passo_medio=round(float(st.mean()), 2), passo_emenda=round(float(st[-1]), 2),
                       passo_vizinho_da_emenda=round(float(st[-2]), 2), curso_x=round(float(np.ptp(xy[:, 0])), 1),
                       curso_y=round(float(np.ptp(xy[:, 1])), 1))
    resumo = {}
    for pre, nome in (("a", "anel_de_fora"), ("b", "anel_de_tras"), ("f", "foices"), ("l", "lascas")):
        v = [r for k, r in res.items() if k.startswith(pre)]
        resumo[nome] = dict(pontas=len(v), passo_max=max(r["passo_max"] for r in v), passo_medio=round(float(np.mean([r["passo_medio"] for r in v])), 2),
                            emenda_max=max(r["passo_emenda"] for r in v), vizinho_da_emenda_max=max(r["passo_vizinho_da_emenda"] for r in v))
        if mostra:
            print(nome, resumo[nome])
    json.dump(dict(resumo=resumo, pontas=res), open(f"{pasta}/chicote.json", "w"), indent=1)
    return resumo


if __name__ == "__main__":
    import tempfile
    C.roda(__file__, {"recortes": recortes, "rig": rig, "chicote": chicote, "compor": compor, "instala": instala}, os.path.join(tempfile.gettempdir(), "aura_blender", ID))
