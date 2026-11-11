"""Aura do CK endiabrado: PAREDÃO DE SOM DE FUMAÇA (método do Blender, docs/arcade/aura_blender.md).

Uma parede de caixas de som feita de fumaça cinza-esverdeada atrás do CK. O desenho do conceito aprovado
(sprites/ck/quadros/folhas_arcade/e_conceito.png) é a textura de UMA malha com ossos:
  - 7 colunas de 5 ossos (do chão ao topo): a parede balança pouco embaixo e o topo desfia e chicoteia;
  - 1 osso por alto-falante, apontado para a câmera, animado em ESCALA: o cone incha e encolhe (deformação radial),
    os grandes no tempo (o 1º tempo mais forte), os pequenos no contratempo;
  - o objeto inteiro leva um tranco a cada batida.
Por cima, em Python e em laço: anéis de fumaça que nascem dos cones, névoa baixa, fagulhas em forma de folha,
cacos de vidro e tampinhas que pulam no grave.

    python ferramentas/aura_blender/ck_aura.py <pasta de trabalho>                  # tudo
    python ferramentas/aura_blender/ck_aura.py <pasta de trabalho> pontos chicote   # só o movimento (1 s)
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import comum as C

ID = "ck"
AURA = "paredao"
SRC = os.path.join(C.RAIZ, "sprites", ID, "quadros", "folhas_arcade", "e_conceito.png")
CORPO_X = (0, 360)                  # vista 1: só o corpo
AURA_X = (666, 1696)                # vista 3: corpo + paredão
TELA = C.Tela(cx=1178.0, chao=700.0, escala=112 / 569.0)     # corpo de 569 px no conceito vira 112 no jogo
N = 48                              # laço da parede: 4 tempos de 12 quadros (a 2 tiques: 0,4 s por tempo, 150 bpm)
TIQ = 2
NB = 12                             # quadros por tempo
F0 = 3                              # quadro do 1º tempo: a emenda do laço cai num momento calmo, não no golpe
NPART = 2 * N                       # laço dos anéis, da névoa e das fagulhas (dois compassos)
ESCURA = (20, 26, 20)               # contorno: o escuro dos lutadores puxado para o verde da fumaça

# ---- alto-falantes, medidos no conceito: caixa externa (x0, y0, x1, y1), centro do cone, raio do cone -------------
GRANDES = {
    "em": ((802, 220, 980, 372), (891, 297), 67), "eb": ((787, 372, 982, 572), (885, 477), 80),
    "dm": ((1375, 212, 1560, 362), (1475, 297), 63), "db": ((1387, 370, 1580, 570), (1485, 472), 75),
}
PEQUENOS = {"ep": (936, 180, 29), "dp": (1426, 180, 29), "cep": (1048, 165, 31), "cdp": (1290, 165, 31)}
# o miolo do paredão (atrás do corpo e dos anéis do conceito) é REMENDO: caixas limpas dos lados copiadas para cá
MIOLO = {"cem": ("dm", (990, 200, 1187, 372)), "ceb": ("db", (990, 372, 1187, 585)),
         "cdm": ("em", (1187, 200, 1384, 372)), "cdb": ("eb", (1187, 372, 1384, 585)),
         "ccp": ("ep", (1131, 120, 1249, 204))}          # atrás da cabeça: mais uma caixa pequena
CAIXA_EP = (887, 130, 992, 212)
GIRO_MIOLO = {"cem": 140.0, "ceb": -105.0, "cdm": 75.0, "cdb": 160.0, "ccp": -60.0}      # giro do cone de cada cópia (graus)
# braços de fumaça do conceito que saíam para fora da parede (eram os anéis parados): saem, os anéis são camada própria
BRACOS = [(666, 285, 792, 500), (1583, 268, 1696, 520)]
# cacos de vidro e tampinhas no chão: caixas no conceito (x0, y0, x1, y1)
CACOS = {"caco1": (786, 633, 847, 667), "caco2": (886, 625, 939, 655), "caco3": (1413, 637, 1472, 674),
         "caco4": (1555, 632, 1613, 666), "caquinho1": (996, 641, 1024, 661), "caquinho2": (1329, 648, 1365, 666), "caquinho3": (1298, 637, 1328, 657),
         "tampa1": (851, 656, 894, 684), "tampa2": (928, 663, 979, 694), "tampa3": (978, 617, 1022, 643),
         "tampa4": (1291, 617, 1327, 642), "tampa5": (1346, 627, 1394, 657), "tampa6": (1475, 622, 1513, 648),
         "tampa7": (1486, 661, 1534, 692), "tampa8": (1383, 671, 1422, 697)}


def _lum(rgb):
    return rgb.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)


def _polar(c, raios, na=96):
    a = np.arange(na) * 2 * np.pi / na
    xs = np.round(c[0] + np.outer(raios, np.cos(a))).astype(int); ys = np.round(c[1] + np.outer(raios, np.sin(a))).astype(int)
    return ys, xs


def _acha_centro(L, ok, c0, R, busca=8):
    """Centro do cone = onde a luminância fica mais igual ao longo de cada círculo (o cone é redondo)."""
    raios = np.arange(0.25 * R, 0.95 * R, 2.0); melhor = None
    for dy in range(-busca, busca + 1, 2):
        for dx in range(-busca, busca + 1, 2):
            ys, xs = _polar((c0[0] + dx, c0[1] + dy), raios)
            v = np.where(ok[ys, xs], L[ys, xs], np.nan)
            med = np.nanmedian(v, 1, keepdims=True); nota = float(np.nanmean(np.nanmedian(np.abs(v - med), 1)))
            if melhor is None or nota < melhor[0]:
                melhor = (nota, (c0[0] + dx, c0[1] + dy))
    return melhor[1]


def _cone_limpo(rgb, L, ok, c, R):
    """Limpa o cone SEM alisar: só o que passava por cima dele no conceito (rabo claro de fumaça, corpo, fagulha) é
    trocado, e por outro pedaço do MESMO cone no mesmo raio (espelhado ou girado em volta do centro), que traz a
    pincelada junto. A mediana por raio fica só para o que nenhum giro alcança (o miolo, de onde os rabos saíam).
    Devolve a máscara do disco e a fração dele que precisou de mediana."""
    from scipy import ndimage as ndi
    Rm = int(R * 1.04); raios = np.arange(0, Rm + 2, 1.0)
    ys, xs = _polar(c, raios, 180); okp = ok[ys, xs]
    with np.errstate(all="ignore"):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            perfil = np.nanmedian(np.where(okp[..., None], rgb[ys, xs].astype(np.float32), np.nan), 1)
            Lm = np.nanmedian(np.where(okp, L[ys, xs], np.nan), 1)
    tem = np.nonzero(~np.isnan(Lm))[0]
    for i in np.nonzero(np.isnan(Lm))[0]:                           # raio sem nenhum pixel bom: o raio bom mais perto
        j = tem[np.argmin(np.abs(tem - i))]; perfil[i] = perfil[j]; Lm[i] = Lm[j]
    H, W = ok.shape; yy, xx = np.mgrid[0:H, 0:W]; dx, dy = xx - c[0], yy - c[1]; r = np.hypot(dx, dy); d = r <= Rm
    ri = np.clip(np.round(r).astype(int), 0, len(raios) - 1)
    ruim = d & (~ok | (L > Lm[ri] + 20))
    ruim = ndi.binary_dilation(ndi.binary_opening(ruim, iterations=1) | (d & ~ok), iterations=3) & d
    bom = d & ~ruim; src = rgb.copy(); falta = ruim.copy(); ang = np.arctan2(dy, dx)
    pi = np.pi
    for T in (lambda a: pi - a, lambda a: -a, lambda a: a + pi, lambda a: a + pi / 2, lambda a: a - pi / 2,
              lambda a: a + pi / 4, lambda a: a - pi / 4, lambda a: a + 3 * pi / 4, lambda a: a - 3 * pi / 4):
        fy_, fx_ = np.nonzero(falta)
        if not len(fy_):
            break
        a2 = T(ang[fy_, fx_]); rr = r[fy_, fx_]
        sx = np.round(c[0] + rr * np.cos(a2)).astype(int); sy = np.round(c[1] + rr * np.sin(a2)).astype(int)
        serve = (sx >= 0) & (sx < W) & (sy >= 0) & (sy < H); serve[serve] = bom[sy[serve], sx[serve]]
        rgb[fy_[serve], fx_[serve]] = src[sy[serve], sx[serve]]; falta[fy_[serve], fx_[serve]] = False
    rgb[falta] = np.clip(perfil[ri[falta]], 0, 255).astype(np.uint8)
    return d, float(ruim.sum()) / d.sum(), float(falta.sum()) / d.sum()


def recortes(pasta):
    from scipy import ndimage as ndi
    from PIL import Image
    import cv2
    rec = os.path.join(pasta, "recortes"); os.makedirs(rec, exist_ok=True)
    im = C.le_rgb(SRC); H, W = im.shape[:2]
    fg = C.chave_magenta(im)
    corpo = C.recorta_corpo(fg, im, *CORPO_X)
    Image.fromarray(np.dstack([im, (corpo * 255).astype(np.uint8)])).save(f"{rec}/corpo.png")
    dx, dy, nota = C.casa_corpo(im, corpo, 960, 1400)
    print("corpo casado: dx", dx, "dy", dy, "nota", round(nota, 3))
    cna = ndi.binary_dilation(C.desloca(corpo, dx, dy), iterations=9)       # o corpo na vista com aura, com folga
    aura = fg.copy(); aura[:, :AURA_X[0]] = False; aura[:, AURA_X[1]:] = False
    aura &= ~C.derrame_de_borda(aura, im)
    rgb = im.copy(); R_, G_, B_ = C.canais(im); L = _lum(im)
    yy, xx = np.mgrid[0:H, 0:W]
    info = dict(dx=dx, dy=dy, nota=nota, cones={}, cacos={}, cones_remendo={})

    # (a) fagulhas laranja do desenho: saem (viram partícula) e o lugar é fechado com o vizinho
    lar = aura & (R_ > 170) & (R_ - G_ > 45) & (B_ < 110)
    lar = ndi.binary_dilation(lar, iterations=3)
    C.remenda_vizinho(rgb, aura & ~lar & ~cna, lar & ~cna)
    # (b) cacos e tampinhas: cada um vira um recorte próprio (pulam no grave) e saem da base
    pecas = np.zeros_like(aura)
    for nome, (x0, y0, x1, y1) in CACOS.items():
        cx_ = np.zeros_like(aura); cx_[y0:y1, x0:x1] = True
        verde = (G_ - R_ > 22) & (G_ - B_ > 45)
        cinza = (np.abs(R_ - G_) < 14) & (G_ - B_ < 22)
        m = cx_ & fg & ((L < 86) | verde | (cinza & (L < 175)))
        m = ndi.binary_closing(m, iterations=2) & cx_
        m = ndi.binary_fill_holes(m)
        m = ndi.binary_opening(m, iterations=1)
        m = C.maior_componente(m, conect=8)
        bx = C.caixa(m)
        C.salva_rgba(f"{rec}/{nome}.png", im, m)
        info["cacos"][nome] = dict(bbox=bx, area=int(m.sum()))
        pecas |= m
    pecas_d = ndi.binary_dilation(pecas, iterations=4)
    # (c) limpa: o que é corpo, fagulha ou caco deixa de ser fonte
    ok = aura & ~cna & ~lar & ~pecas_d
    # (d) cones: centro pela simetria, cone refeito redondo (tira os rabos de fumaça que passavam por cima)
    cones = {}
    for nome, (cxa, c0, R) in GRANDES.items():
        c = _acha_centro(L, ok, c0, R); cones[nome] = (c[0], c[1], R)
    for nome, (x, y, R) in PEQUENOS.items():
        c = _acha_centro(L, ok, (x, y), R, busca=6); cones[nome] = (c[0], c[1], R)
    print("cones", cones)
    feito = np.zeros_like(aura)
    for nome, (x, y, R) in cones.items():
        d_, trocado, mediana = _cone_limpo(rgb, L, ok, (x, y), R); feito |= d_
        info["cones_remendo"][nome] = dict(trocado=round(trocado, 3), mediana=round(mediana, 3))
    print("cones: fração trocada / por mediana", info["cones_remendo"])
    # (e) painel das caixas grandes: o que é claro dentro do painel escuro é rabo de fumaça do conceito -> vizinho
    for nome, (cxa, c0, R) in GRANDES.items():
        x0, y0, x1, y1 = cxa; dentro = np.zeros_like(aura); dentro[y0 + 20:y1 - 20, x0 + 20:x1 - 20] = True
        dentro &= ~feito
        rabo = ndi.binary_dilation(dentro & (_lum(rgb) > 128), iterations=4) & dentro
        C.remenda_vizinho(rgb, dentro & ~rabo & ok, rabo)
    ok = (ok | feito) & ~(cna & ~feito)
    # (f) miolo: caixas limpas copiadas para trás do corpo
    miolo = np.zeros_like(aura)
    for nome, (fonte, (x0, y0, x1, y1)) in MIOLO.items():
        sx0, sy0, sx1, sy1 = GRANDES[fonte][0] if fonte in GRANDES else CAIXA_EP
        # a cópia não fica igual à fonte: a caixa vai ESPELHADA e o cone (que é redondo) vai GIRADO em volta do centro
        fx, fy, fr = cones[fonte]; kx, ky = (x1 - x0) / (sx1 - sx0), (y1 - y0) / (sy1 - sy0)
        pat = rgb[sy0:sy1, sx0:sx1].copy(); ph, pw = pat.shape[:2]
        gir = cv2.warpAffine(pat, cv2.getRotationMatrix2D((float(fx - sx0), float(fy - sy0)), GIRO_MIOLO[nome], 1.0), (pw, ph),
                             flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_REFLECT)
        py_, px_ = np.mgrid[0:ph, 0:pw]; disco = np.hypot(px_ - (fx - sx0), py_ - (fy - sy0)) <= fr * 0.93
        pat[disco] = gir[disco]; pat = pat[:, ::-1]; fxe = (pw - 1) - (fx - sx0)
        rgb[y0:y1, x0:x1] = cv2.resize(np.ascontiguousarray(pat), (x1 - x0, y1 - y0), interpolation=cv2.INTER_NEAREST)
        miolo[y0:y1, x0:x1] = True
        cones[nome] = (x0 + fxe * kx, y0 + (fy - sy0) * ky, fr * min(kx, ky))
    # (g) o resto do buraco do corpo (cabeça em cima, pernas e pés embaixo) e os furos de fagulha/caco: vizinho
    alvo = (cna | lar | pecas_d) & ~miolo & ~feito
    base = alvo & (yy > 585) & (yy < 690) & (xx > 1010) & (xx < 1350)      # a base de fumaça passa por trás dos pés
    topo = alvo & (yy <= 585) & (yy > 100)
    furos = pecas & aura & ~cna & ~miolo & ~feito
    alvo = base | topo | furos
    valido = ok & ~alvo & ~miolo
    falta = C.remenda_clone(rgb, rgb.copy(), valido, base, (0, -330), vezes=1)
    falta = C.remenda_clone(rgb, rgb.copy(), valido, falta, (0, 330), vezes=1)
    C.remenda_vizinho(rgb, valido, falta | topo | furos)
    parede = (aura & ~cna) | miolo | feito | alvo
    parede = ndi.binary_opening(parede, iterations=1)
    for (x0, y0, x1, y1), rd in zip(BRACOS, (17, 26)):
        disco = np.hypot(*np.mgrid[-rd:rd + 1, -rd:rd + 1]) <= rd                       # some o que é fino (braço), fica o que é nuvem gorda
        sub = parede[y0 - 40:y1 + 40, x0:x1]; ab = ndi.binary_opening(sub, structure=disco)
        parede[y0:y1, x0:x1] = ab[40:-40]
    parede = C.maior_componente(parede, conect=8)
    R2, G2, B2 = C.canais(rgb)
    rosa = parede & (B2 > G2 + 4)                         # derrame de magenta na casca
    rosa = ndi.binary_dilation(rosa, iterations=1) & parede
    C.remenda_vizinho(rgb, parede & ~rosa, rosa)
    # (h) contraste que o conceito não tem: borda do cone escura, miolo claro; e a parede inteira um pouco mais dura
    f = rgb.astype(np.float32)
    f = np.clip((f - 118) * 1.18 + 118, 0, 255)
    for nome, (x, y, R) in cones.items():
        r = np.hypot(xx - x, yy - y) / R
        borda = np.clip(1 - np.abs(r - 0.96) / 0.10, 0, 1)                  # aro escuro
        f *= (1 - 0.55 * borda)[..., None]
        # miolo (a calota): uma meia-bola com luz de cima-esquerda e sombra embaixo à direita, não um disco de uma cor só
        u, v = (xx - x) / (0.30 * R), (yy - y) / (0.30 * R); rd = np.hypot(u, v)
        domo = np.clip((1 - rd) / 0.18, 0, 1)
        luzd = np.clip(0.52 - 0.50 * (u + v) / 1.414 - 0.25 * rd * rd, 0, 1)             # 1 = virado para a luz
        brilho = np.clip(1 - np.hypot(u + 0.34, v + 0.34) / 0.36, 0, 1)                  # o ponto de brilho
        cor = (np.array([58, 68, 46], np.float32)[None, None] * (1 - luzd[..., None]) + np.array([206, 212, 168], np.float32)[None, None] * luzd[..., None])
        cor += (np.array([236, 240, 204], np.float32) - cor) * brilho[..., None]
        f += (cor - f) * (0.88 * domo)[..., None]
        meio = np.clip(1 - np.abs(r - 0.62) / 0.07, 0, 1)                   # um friso claro no meio do cone (fraco: a pincelada manda)
        f += (np.array([170, 178, 140], np.float32) - f) * (0.22 * meio)[..., None]
        luz = np.clip((-(xx - x) - (yy - y)) / (1.4 * R), -1, 1) * ((r > 0.3) & (r < 0.9))   # luz de cima-esquerda
        f *= (1 + 0.16 * luz)[..., None]
    rgb = np.clip(f, 0, 255).astype(np.uint8)
    C.salva_rgba(f"{rec}/paredao.png", rgb, parede)
    info["cones"] = {k: [float(v[0]), float(v[1]), float(v[2])] for k, v in cones.items()}
    info["paredao_bbox"] = C.caixa(parede)
    json.dump(info, open(f"{rec}/info.json", "w"), indent=1)
    C.previa_recortes([f"{rec}/paredao.png"], f"{pasta}/p_recortes.png", (AURA_X[0] - 10, 0, AURA_X[1] + 10, H), (H, W))
    C.previa_recortes([f"{rec}/{n}.png" for n in CACOS], f"{pasta}/p_cacos.png", (770, 600, 1630, 710), (H, W))
    print("paredao", info["paredao_bbox"], "cacos", {k: v["area"] for k, v in info["cacos"].items()})


# =====================================================================================================================
# RIG (dentro do Blender)
# =====================================================================================================================
COL_X = [735, 880, 1030, 1185, 1340, 1490, 1640]                   # colunas de ossos, em px do conceito
COL_Y = [668, 520, 380, 240, 130, 42]                              # juntas de baixo para cima: a, b, c, d (topo), e (ponta)
COL_N = "abcde"
#          amplitude (graus), atraso (fração do ciclo), 2º harmônico, fase dele: embaixo pouco e cedo, em cima muito e tarde
COL_ANIM = {"a": (0.55, 0.00, 0.0, 0.0), "b": (1.10, 0.05, 0.25, 0.4), "c": (1.90, 0.11, 0.70, 0.9),
            "d": (4.0, 0.20, 1.8, 1.5), "e": (11.0, 0.32, 4.0, 2.2)}
ESTICA = 0.020                                                     # cada pilha de caixas estica/achata no grave (fração da altura)
COL_FASE = 5.0                                                     # quadros de atraso de uma coluna para a vizinha (onda de lado)
TEMPOS = [1.00, 0.62, 0.78, 0.62]                                  # força de cada um dos 4 tempos (o 1º bate mais forte)
#       cone: (quanto incha, atraso em quadros, contratempo?)
BATE = {"eb": (0.30, 0, False), "db": (0.30, 0, False), "ceb": (0.28, 1, False), "cdb": (0.28, 1, False),
        "em": (0.24, 1, False), "dm": (0.24, 1, False), "cem": (0.22, 2, False), "cdm": (0.22, 2, False),
        "ep": (0.24, 0, True), "dp": (0.24, 0, True), "cep": (0.22, 1, True), "cdp": (0.22, 1, True), "ccp": (0.20, 2, True)}
TREMOR = [dict(eixo="X", raio=14.0, fase=0.0, forca=8.0), dict(eixo="Z", raio=17.0, fase=2.1, forca=9.5)]
MIOLO_RET = (787, 115, 1580, 585)                                  # retângulo das caixas: lá dentro o tremor é fraco


def golpe(d, tau=3.2, per=9.0, ataque=0.0):
    """Resposta de um cone a uma batida, d quadros depois dela: vai para frente de uma vez, volta passando do ponto e
    assenta. Com `ataque` (quadros) a subida não é de um quadro só (coisa pesada: a pilha de caixas)."""
    g = math.exp(-d / tau) * math.cos(2 * math.pi * d / per)
    return g * min(1.0, (d + 0.5) / ataque) if ataque else g


def batida(f, atraso=0.0, contratempo=False, tau=3.2, per=9.0, ataque=0.0):
    """Soma das 4 batidas do compasso no quadro f (laço de N quadros). No contratempo bate no meio de cada tempo, igual."""
    t = 0.0
    for b in range(4):
        d = (f - F0 - b * NB - atraso - (NB / 2 if contratempo else 0)) % N
        t += (0.8 if contratempo else TEMPOS[b]) * golpe(d, tau, per, ataque)
    return t


def peso_cone(r):
    """Peso do osso do cone pelo raio (0..1 = centro..borda): miolo inteiro, caindo suave até a borda (que não sai do
    lugar). É isso que faz a escala do osso virar deformação radial: o miolo cresce e a borda aperta."""
    t = np.clip((r - 0.40) / (1.02 - 0.40), 0, 1)
    return 1 - t * t * (3 - 2 * t)


def rig(pasta, so_pontos=False):
    import bpy
    rec = os.path.join(pasta, "recortes"); info = json.load(open(f"{rec}/info.json"))
    cena = C.bl_cena(TELA, N)
    mat, img = C.bl_material("mat_paredao", f"{rec}/paredao.png"); W, H = img.size
    verts, faces = C.grade_de_malha(C.bl_alfa(img), 8, 8)
    ad = bpy.data.armatures.new("arm_paredao"); ao = bpy.data.objects.new("arm_paredao", ad); cena.collection.objects.link(ao)
    bpy.context.view_layer.objects.active = ao; bpy.ops.object.mode_set(mode="EDIT")
    cols = []                                                       # [(nome, cabeça, cauda)] em px do conceito
    for i, x in enumerate(COL_X):
        for j, l in enumerate(COL_N):
            nm = f"c{i}{l}"; b = ad.edit_bones.new(nm)
            (hx, hz), (tx, tz) = TELA.g(x, COL_Y[j]), TELA.g(x, COL_Y[j + 1])
            b.head = (hx, 0, hz); b.tail = (tx, 0, tz)
            if j:
                b.parent = ad.edit_bones[f"c{i}{COL_N[j - 1]}"]; b.use_connect = True
            cols.append((nm, (x, COL_Y[j]), (x, COL_Y[j + 1])))
    for nm, (x, y, R) in info["cones"].items():                     # osso do cone: aponta para a câmera, filho da coluna mais perto
        b = ad.edit_bones.new("k_" + nm); X, Z = TELA.g(x, y); b.head = (X, 0, Z); b.tail = (X, -4, Z)
        i = int(np.argmin([abs(x - cx) for cx in COL_X])); j = max(k for k in range(5) if COL_Y[k] >= y)
        b.parent = ad.edit_bones[f"c{i}{COL_N[j]}"]; b.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    P = np.array(verts, float); XZ = np.array([TELA.g(ix, iy) for ix, iy in verts])
    me = bpy.data.meshes.new("malha_paredao"); me.from_pydata([(X, 0.0, Z) for X, Z in XZ], [], faces); me.update()
    uvl = me.uv_layers.new(name="uv")
    for poly in me.polygons:
        for li in poly.loop_indices:
            ix, iy = verts[me.loops[li].vertex_index]; uvl.data[li].uv = (ix / W, 1 - iy / H)
    me.materials.append(mat)
    ob = bpy.data.objects.new("malha_paredao", me); cena.collection.objects.link(ob)
    # pesos: colunas (pano mole entre elas) vezes o que sobra do cone; o cone manda no miolo dele
    Wc, _ = C.pesos_por_osso(P, [(h, t) for _, h, t in cols], k=4, folga=30.0, pot=3)
    wk = {}; resto = np.ones(len(P))
    for nm, (x, y, R) in info["cones"].items():
        w = peso_cone(np.hypot(P[:, 0] - x, P[:, 1] - y) / R); wk[nm] = w; resto *= (1 - w)
    for j, (nm, _, _) in enumerate(cols):
        g = ob.vertex_groups.new(name=nm)
        for i in np.nonzero(Wc[:, j] * resto > 1e-4)[0]:
            g.add([int(i)], float(Wc[i, j] * resto[i]), "REPLACE")
    for nm, w in wk.items():
        g = ob.vertex_groups.new(name="k_" + nm)
        for i in np.nonzero(w > 1e-4)[0]:
            g.add([int(i)], float(w[i]), "REPLACE")
    # tremor: fumaça solta (fora das caixas) treme inteira; caixa treme pouco; cone não treme
    x0, y0, x1, y1 = MIOLO_RET
    fora = np.maximum.reduce([x0 - P[:, 0], P[:, 0] - x1, y0 - P[:, 1], P[:, 1] - y1, np.zeros(len(P))])
    wt = (0.34 + 0.66 * np.clip(fora / 45.0, 0, 1)) * resto
    gt = ob.vertex_groups.new(name="tremor")
    for i in range(len(P)):
        gt.add([i], float(wt[i]), "REPLACE")
    tex = C.bl_textura_ruido()
    for tr in TREMOR:
        md = ob.modifiers.new("tremor" + tr["eixo"], "DISPLACE"); md.texture = tex; md.direction = tr["eixo"]; md.space = "LOCAL"
        md.mid_level = 0.5; md.strength = tr["forca"]; md.vertex_group = "tremor"; md.texture_coords = "OBJECT"
        md.texture_coords_object = C.bl_vazio_em_laco("laco_" + tr["eixo"], N, tr["raio"], tr["fase"])
    md = ob.modifiers.new("arm", "ARMATURE"); md.object = ao
    ob.parent = ao                                                  # malha FILHA da armação: o tranco do objeto leva a parede
    print("MALHA paredao verts", len(P), "faces", len(faces))
    # colunas: onda que anda de lado (cada coluna atrasada da vizinha) e sobe em chicote
    for i in range(len(COL_X)):
        C.bl_anima_juntas(ao, {f"c{i}{l}": v for l, v in COL_ANIM.items()}, N, fase=i * COL_FASE)
    # cada pilha estica e achata no grave (a do meio primeiro, as de fora depois): as caixas pulam, não só os cones
    for i in range(len(COL_X)):
        pb = ao.pose.bones[f"c{i}a"]
        for f in range(N + 1):
            e = batida(f, 0.5 + 1.5 * abs(i - 3), False, tau=4.0, per=11.0, ataque=2.0)
            pb.scale = (1 - 0.35 * ESTICA * e, 1 + ESTICA * e, 1); pb.keyframe_insert("scale", frame=f)
    # cones: escala no plano da tela = deformação radial (o cone vem para frente e volta)
    for nm in info["cones"]:
        amp, atr, contra = BATE[nm]; pb = ao.pose.bones["k_" + nm]
        for f in range(N + 1):
            sc = 1 + amp * batida(f, atr, contra); pb.scale = (sc, 1, sc); pb.keyframe_insert("scale", frame=f)

    def tranco(t):                                                  # a parede inteira leva um tranco a cada batida
        f = t * N / (2 * math.pi); e = batida(f, 0, False, tau=2.4, per=6.0); e2 = batida(f, 1.5, False, tau=2.4, per=6.0)
        return dict(location=(0.55 * e2, 0, -1.1 * e), scale=(1 + 0.006 * e, 1, 1 + 0.012 * e))
    C.bl_anima_objeto(ao, N, tranco)
    peca = dict(arm=ao, malha=ob, nomes=[c[0] for c in cols])

    def coleta(f):
        d = C.bl_pontas(peca, TELA, "col")
        for nm in info["cones"]:
            pb = ao.pose.bones["k_" + nm]; w = ao.matrix_world @ pb.head
            d["k_" + nm] = list(TELA.jogo(w.x, w.z)) + [float(pb.scale.x)]
        return d
    C.bl_renderiza(pasta, N, {"paredao": [ob]}, coleta, so_pontos=so_pontos, blend="rig.blend")


def chicote(pasta, mostra=True):
    """Fase e passo das juntas das colunas (cauda de cada osso). A fase do vai-e-vem de LADO cresce de baixo para cima
    (numa parede o sobe-e-desce quase não existe); passo abaixo de 3 px."""
    pts = json.load(open(f"{pasta}/render/pontos.json"))["pontos"]
    ch = [k for k in pts[0] if k.startswith("col_c")]
    res = C.mede_pontos(pts, chaves=ch, mostra=False)
    t = np.arange(N)
    for k in ch:
        x = np.array([p[k][0] for p in pts]); x = x - x.mean()
        c = (x * np.exp(-2j * np.pi * t / N)).sum(); res[k]["fase_x_q"] = round(float((-np.angle(c) / (2 * np.pi) * N) % N), 1)
    if mostra:
        for i in range(len(COL_X)):
            print(f"coluna {i}: " + "  ".join("%s: fase %4.1f curso %4.1f passo %.2f" % (
                l, res[f"col_c{i}{l}"]["fase_x_q"], res[f"col_c{i}{l}"]["curso_x"], res[f"col_c{i}{l}"]["passo_max"]) for l in COL_N))
    json.dump(res, open(f"{pasta}/chicote.json", "w"), indent=1)
    return res


# =====================================================================================================================
# CAMADAS (Python comum): parede com paleta + realce dos cones + fumaça no topo, anéis, névoa, cacos, fagulhas
# =====================================================================================================================
# anéis: (tempo de nascimento dentro dos 8 tempos do laço de 96 quadros, cone). Cones diferentes em tempos diferentes;
# no 1º tempo de cada compasso (o mais forte) saem dois. Os pequenos soltam anel menor no contratempo.
ANEIS = [(0, "eb"), (0, "cdm"), (1, "dm"), (2, "ceb"), (3, "em"), (4, "db"), (4, "cem"), (5, "eb"), (6, "cdb"), (7, "dm"),
         (0.5, "dp"), (1.5, "cep"), (2.5, "ep"), (3.5, "cdp"), (4.5, "ccp"), (5.5, "ep"), (6.5, "dp"), (7.5, "cep")]
VIDA_ANEL = {True: 40, False: 26}        # grande, pequeno (quadros)
FOLHAS = ["011/112/200", "110/012/002", "000/112/000", "010/010/020", "001/011/120", "100/110/021", "0011/0112/1120/2200", "1100/2110/0211/0022"]   # 1 claro, 2 escuro
N_FAGULHAS = 46
AUMENTA_TAMPA, AUMENTA_CACO = 1.55, 1.25                            # no tamanho do conceito a tampinha tinha 8x5 px e lia como bolinha


def _paleta(rec, src):
    """15 cores: 1 de contorno + 9 da parede (do desenho reduzido) + 3 verdes dos cacos + 2 laranjas das fagulhas."""
    import cv2
    par = C.Paleta.de_recortes([f"{rec}/paredao.png"], TELA, n=9, escura=ESCURA)
    im = C.le_rgb(src); R_, G_, B_ = C.canais(im); fg = C.chave_magenta(im)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2); cv2.setRNGSeed(3)

    def km(m, n):
        return np.clip(np.round(cv2.kmeans(im[m].astype(np.float32), n, None, crit, 8, cv2.KMEANS_PP_CENTERS)[2]), 0, 255)
    verde = fg & (G_ - R_ > 22) & (G_ - B_ > 45); verde[:600] = False; verde[:, :AURA_X[0]] = False; verde[:, AURA_X[1]:] = False
    lar = fg & (R_ > 190) & (R_ - G_ > 60) & (G_ > 85) & (B_ < 75); lar[:, :AURA_X[0]] = False; lar[:, AURA_X[1]:] = False
    lar &= ~(C.desloca(C.recorta_corpo(fg, im, *CORPO_X), 994, 2))
    cv, cl = km(verde, 3), km(lar, 2)
    pal = C.Paleta(np.vstack([par.cores, cv, cl]))
    acha = lambda c: int(np.where((pal.cores == np.asarray(c, np.uint8)).all(1))[0][0])
    fum = sorted(acha(c) for c in par.cores)                        # escada da fumaça, do contorno ao mais claro
    return pal, par, fum, sorted(acha(c) for c in cv), sorted(acha(c) for c in cl)


def compor(pasta):
    from scipy import ndimage as ndi
    from PIL import Image
    import cv2
    rec = os.path.join(pasta, "recortes"); cam = os.path.join(pasta, "camadas")
    info = json.load(open(f"{rec}/info.json")); pontos = json.load(open(f"{pasta}/render/pontos.json"))["pontos"]
    rng = np.random.default_rng(11)
    pal, par, fum, verdes, laranjas = _paleta(rec, SRC)
    assert pal.n == 15, pal.n
    print("paleta", pal.lista(), "fumaça", fum, "verdes", verdes, "laranjas", laranjas)
    para_cheia = np.array([int(np.where((pal.cores == c).all(1))[0][0]) for c in par.cores], np.int16)   # idx da parede -> idx da paleta
    pos = np.array([int(np.argmin([abs(i - k) for k in fum])) for i in range(pal.n)])   # degrau de cada cor na escada da fumaça
    esc = np.array(fum, np.int16); TOPO = len(fum) - 1
    YY, XX = TELA.grade(); CH, CW = TELA.ch, TELA.cw
    campo = C.Campo(TELA, 96); R1, R2, R3, R4 = C.ladrilho(1), C.ladrilho(2, fmax=13), C.ladrilho(5, fmax=5), C.ladrilho(8, fmax=6)
    campo.fecha(N, 2, 4); campo.fecha(NPART, 1, 2)
    cones = {k: (v[0], v[1], v[2] * TELA.escala) for k, v in info["cones"].items()}      # raio em px do jogo

    def sobe(v, k):                                                 # k degraus acima (ou abaixo) na escada da fumaça
        return esc[np.clip(pos[v] + k, 1, TOPO)]

    # ---------------- parede: render -> 1x -> paleta com histerese -> contorno -> realce dos cones -> fumaça subindo do topo
    brutos = [C.le_render(f"{pasta}/render/paredao_{f:02d}.png", TELA.amp) for f in range(N)]
    seca = [para_cheia[np.clip(a, 0, None)] * (a >= 0) - (a < 0) for a in par.encaixa_seq(brutos)]
    seca = [C.contorno(C.limpa(a.astype(np.int16)), pal.escura) for a in seca]

    def veios(idx, f):
        """A parede é de fumaça: manchas claras e escuras sobem devagar por dentro dela (nada fica parado), menos nos cones."""
        n = 0.6 * campo.rola(R3, f, vy=2) + 0.4 * campo.rola(R4, f, vy=2, vx=2, ox=40)
        livre = (idx > 0)
        for nm, (_, _, Rg) in cones.items():
            px, py, _ = pontos[f]["k_" + nm]; livre &= np.hypot(XX - px, YY - py) > Rg * 1.02
        out = idx.copy()
        m = livre & (n > 0.63); out[m] = sobe(idx[m], 1)
        m = livre & (n < 0.37); out[m] = sobe(idx[m], -1)
        return out

    def reflexo(idx, f):
        """Dentro do cone nada fica parado nem liso: dois reflexos opostos giram devagar em volta do miolo (meia volta por
        laço, cada cone para um lado), um degrau acima; entre eles, duas sombras um degrau abaixo."""
        out = idx.copy()
        for j, (nm, (_, _, Rg)) in enumerate(cones.items()):
            px, py, _ = pontos[f]["k_" + nm]; dx, dy = XX - px, YY - py; r = np.hypot(dx, dy) / Rg
            s_ = np.cos(2 * (np.arctan2(dy, dx) - (1 if j % 2 else -1) * math.pi * f / N - 0.9 * j))
            faixa = (r > 0.36) & (r < 0.93) & (idx > 0)
            m = faixa & (s_ > 0.90); out[m] = sobe(idx[m], 1)
            m = faixa & (s_ < -0.94); out[m] = sobe(idx[m], -1)
        return out
    seca = [reflexo(veios(a, f), f) for f, a in enumerate(seca)]

    def realce(idx, f):
        """O miolo do cone acende no golpe e uma onda clara corre do miolo para a borda (contraste que faltava)."""
        out = idx.copy()
        for nm, (_, _, Rg) in cones.items():
            px, py, sc = pontos[f]["k_" + nm]; amp, atr, contra = BATE[nm]
            fo = (f - F0 - atr - (NB / 2 if contra else 0)) % N; d = fo % NB; forca = 0.8 if contra else TEMPOS[int(fo // NB) % 4]
            r = np.hypot(XX - px, YY - py); dentro = (r < Rg * 1.0) & (out >= 0)
            dur = 4 + 4 * forca
            if d < dur:
                m = dentro & (np.abs(r - Rg * (0.30 + 0.62 * d / dur)) < 0.8)
                out[m] = sobe(out[m], 2)
            # o miolo é uma meia-bola: no golpe só o lado da luz clareia (um degrau) e a sombra de baixo-direita fica,
            # então ele nunca vira um disco de uma cor só
            rd = Rg * 0.30 * sc; u = ((XX - px) + (YY - py)) / (1.414 * max(rd, 1e-3)); domo = dentro & (r < rd)
            k = 1 if sc > 1.05 else 0 if sc > 0.97 else -1
            if k:
                m = domo & (u < 0.12); out[m] = sobe(out[m], k)
            m = domo & (u > 0.42); out[m] = esc[np.minimum(pos[out[m]], TOPO - 3)]
            m = domo & (u > 0.12) & (u <= 0.42); out[m] = esc[np.minimum(pos[out[m]], TOPO - 1)]
        return out

    def ruido_sobe(f):
        return 0.5 * campo.rola(R1, f, vy=2) + 0.5 * campo.rola(R2, f, vy=4, ox=17)
    rampa_fumo = [esc[TOPO], esc[TOPO], esc[TOPO - 1], esc[TOPO - 1], esc[TOPO - 2], esc[TOPO - 3], esc[TOPO - 3], esc[TOPO - 4], esc[TOPO - 5]]
    parede = [C.linguas(realce(a, f), ruido_sobe(f), rampa_fumo, alt=8, forca=0.10) for f, a in enumerate(seca)]

    # ---------------- anéis de fumaça: nascem no cone, crescem, se afastam e se desfazem
    def anel(L, f, t0, nm):
        grande = nm in GRANDES or nm in ("cem", "ceb", "cdm", "cdb"); vida = VIDA_ANEL[grande]
        b = int(round(t0 * NB)) + F0 + BATE[nm][1]; a = (f - b) % NPART
        if a >= vida:
            return
        q = a / vida; cx, cy, _ = pontos[b % N]["k_" + nm]; Rg = cones[nm][2]
        e = 1 - (1 - q) ** 2.2                                      # cresce depressa e vai parando
        ax = Rg * (0.50 + (1.75 if grande else 1.45) * e); ay = ax * (0.62 - 0.10 * e)
        cx += (0.34 if cx > TELA.pe[0] else -0.34) * a * (0.5 + 0.5 * e) + 1.4 * math.sin(a * 0.21 + cy)
        cy += -0.20 * a + 0.9 * math.sin(a * 0.17 + cx * 0.1)
        dx, dy = XX - cx, YY - cy; ang = np.arctan2(dy, dx)
        ond = 1 + 0.07 * np.sin(3 * ang + 0.13 * a + b) + 0.05 * np.sin(5 * ang - 0.09 * a)
        rho = np.hypot(dx / ax, dy / ay) / ond
        dist = np.abs(rho - 1) * (ax * ay) / np.maximum(np.hypot(ax * np.sin(ang), ay * np.cos(ang)), 1e-3)    # ~px até a elipse
        n1 = campo.rola(R3, f, vy=1, ox=b * 7); n2 = campo.rola(R4, f, vx=1, oy=b * 5)
        g = np.abs(np.sin(4.5 * ang + 0.05 * a + b))                # a faixa é feita de gomos de fumaça
        # fim da vida: a faixa some primeiro ENTRE os gomos e cada gomo encolhe no lugar, como bafo de fumaça que se
        # desmancha (nem lasca solta roída pelo ruído, nem aro fino de arame)
        some = 1.7 * min(1.0, max(0.0, (q - 0.62) / 0.30)); fim = min(1.0, (1 - q) / 0.20)
        esp = (4.4 - 1.6 * q) * (0.72 + 0.50 * g - some * (1 - g)) * (0.62 + 0.7 * n1) * (0.45 + 0.55 * fim)
        m = (dist < esp) & (esp > 1.9) & (n2 > 0.45 * q ** 1.6 - 0.08)
        if not m.any():
            return
        luz = (rho < 1) == (dy > 0)                                 # a face de cima de cada gomo pega luz
        tom = np.where(dist < 0.5 * esp, TOPO, TOPO - 1) - np.where(luz, 0, 2) - (1 if q > 0.6 else 0) - (1 if q > 0.74 else 0) - (1 if q > 0.87 else 0)
        A = np.full((CH, CW), -1, np.int16); A[m] = esc[np.clip(tom, 3, TOPO)][m]
        A = C.limpa(A, int(12 + 16 * q))                        # pedaço pequeno some; quanto mais velho o anel, maior o corte
        if q < 0.64:
            A = C.contorno(A, pal.escura)                           # anel novo tem contorno; o velho perde e some na parede
        L[A >= 0] = A[A >= 0]
    aneis = []
    for f in range(NPART):
        L = np.full((CH, CW), -1, np.int16)
        for t0, nm in ANEIS:
            anel(L, f, t0, nm)
        aneis.append(L)

    # ---------------- névoa baixa: dois ruídos deslizando em sentidos opostos (a forma muda, não só anda)
    def nevoa(f):
        n = 0.55 * R3[(YY * 3) % 96, (XX + f) % 96] + 0.45 * R4[(YY * 3 + 31) % 96, (XX - f + 17) % 96]
        vert = np.where(YY < 186, 1 - (186 - YY) / 13.0, 1 - (YY - 186) / 8.0)
        lado = np.clip(np.minimum(XX - 40, 320 - XX) / 30.0, 0, 1)
        den = n + 0.75 * np.clip(vert, -1, 1) + 0.10 * np.sin(XX / 19.0 + 0.7 + 2 * math.pi * f / NPART) - (1 - lado) * 0.8
        m = (den > 1.02) & (YY <= TELA.pe[1] + 3)
        L = np.full((CH, CW), -1, np.int16)
        L[m] = esc[np.where(den > 1.30, TOPO, np.where(den > 1.14, TOPO - 1, TOPO - 2))][m]
        L = C.limpa(L, 8)
        cima = np.ones_like(m); cima[1:] = L[:-1] < 0; L[(L >= 0) & cima] = esc[TOPO]          # crista clara
        baixo = np.ones_like(m); baixo[:-1] = L[1:] < 0; L[(L >= 0) & baixo] = esc[TOPO - 4]   # barriga escura
        return C.contorno(L, pal.escura)                            # contorno embaixo e dos lados: lê como rolo de névoa na frente da base
    nevoas = [nevoa(f) for f in range(NPART)]

    # ---------------- cacos de vidro e tampinhas: pulam e giram a cada grave, os de perto do meio primeiro
    k4 = TELA.escala * TELA.amp
    pecas = []
    for i, nome in enumerate(CACOS):
        x0, y0, x1, y1 = info["cacos"][nome]["bbox"]
        spr = cv2.imread(f"{rec}/{nome}.png", cv2.IMREAD_UNCHANGED)[y0:y1, x0:x1][..., [2, 1, 0, 3]]
        ke = k4 * (AUMENTA_TAMPA if nome.startswith("tampa") else AUMENTA_CACO)
        spr = cv2.resize(spr, (max(4, round((x1 - x0) * ke)), max(4, round((y1 - y0) * ke))), interpolation=cv2.INTER_NEAREST)
        gx, gy = TELA.conceito_para_jogo((x0 + x1) / 2, (y0 + y1) / 2)
        gy -= (y1 - y0) * (ke - k4) / (2 * TELA.amp)                # cresce para cima: a base continua no chão
        leve = 1.0 if nome.startswith("tampa") else 0.9 if nome.startswith("caquinho") else 0.85
        pecas.append(dict(spr=spr, x=gx, y=gy, atraso=abs(gx - TELA.pe[0]) / 34.0 + float(rng.uniform(0, 1.2)), alt=leve * float(rng.uniform(2.6, 3.6)),
                          giro=float(rng.uniform(0.25, 0.5)) * (1 if i % 2 else -1), per=float(rng.uniform(4.2, 5.4)), cap=nome.startswith("tampa")))

    def cacos_q(f):
        L = np.full((CH, CW), -1, np.int16)
        for pc in pecas:
            pulo = giro = dxx = 0.0
            for b in range(4):
                d = (f - F0 - b * NB - pc["atraso"]) % N; e = TEMPOS[b] * math.exp(-d / 4.5)
                pulo += e * abs(math.sin(math.pi * d / pc["per"])); giro += e * math.sin(2 * math.pi * d / (1.7 * pc["per"]))
                dxx += e * math.sin(2 * math.pi * d / 3.1)
            rgb, m = C.reduz(C.carimbo_girado(pc["spr"], pc["giro"] * giro, amp=TELA.amp), TELA.amp)
            sub = pal.encaixa(rgb, m)
            if pc["cap"]:                                           # tampinha: metal -> tons da escada, com brilho em cima
                ok = sub >= 0; sub[ok] = sobe(sub[ok], 0)
            C.carimba(L, sub, pc["x"] + 0.8 * dxx, pc["y"] - pc["alt"] * pulo)
        return C.contorno(L, pal.escura, poupa_cima=False)
    cacos = [cacos_q(f) for f in range(N)]

    # ---------------- fagulhas laranja em forma de folhinha: poucas, sobem rodopiando, nascem no chão e nos cones
    folhas = [np.array([[int(c) for c in lin] for lin in fo.split("/")]) for fo in FOLHAS]
    nomes_cone = list(cones)

    def nasce(i, r):
        if r.uniform() < 0.55:
            return (float(r.uniform(74, 286)), float(r.uniform(176, 188)))
        return None
    sem = C.semeia(rng, N_FAGULHAS, dict(b=lambda i, r: (i * NPART // N_FAGULHAS + int(r.integers(0, 4))) % NPART, onde=nasce,
                                         k=("int", 0, len(nomes_cone)), dx=("uni", -0.30, 0.30), v=("uni", 0.55, 1.15),
                                         vida=("int", 34, 58), ph=("uni", 0, 6.28), gira=("int", 3, 6)))
    for sd in sem:
        if sd["onde"] is None:
            x, y, _ = pontos[sd["b"] % N]["k_" + nomes_cone[sd["k"]]]; sd["onde"] = (x + float(rng.uniform(-6, 6)), y + float(rng.uniform(-4, 4)))

    def des_folha(L, sd, a, f, i):
        q = a / sd["vida"]
        x = sd["onde"][0] + sd["dx"] * a + 2.6 * math.sin(a * 0.26 + sd["ph"]); y = sd["onde"][1] - sd["v"] * a - 0.004 * a * a
        fo = folhas[(a // sd["gira"] + i) % len(folhas)]
        if q > 0.82:                                                # no fim vira um ponto escuro e some
            fo = np.array([[2]])
        s = np.where(fo == 1, laranjas[-1], np.where(fo == 2, laranjas[0], -1)).astype(np.int16)
        if q < 0.12:
            s[s == laranjas[-1]] = esc[TOPO]                        # nasce clara
        C.carimba(L, s, x, y)
        return 0 <= y < CH and 0 <= x < CW
    fagulhas = []
    for f in range(NPART):
        L = np.full((CH, CW), -1, np.int16); C.emite(L, f, NPART, sem, des_folha); fagulhas.append(L)

    # ---------------- saída: camadas NA ORDEM DE DESENHO + aura.json
    CAM = {"paredao": parede, "aneis": aneis, "nevoa": nevoas, "cacos": cacos, "fagulhas": fagulhas}
    C.exporta_camadas(cam, CAM, pal)
    C.escreve_aura_json(cam, ID, AURA, TELA, TIQ, [
        dict(nome="paredao", quadros=N, plano="atras", o_que="parede de caixas de som de fumaça: cones pulsando no grave, topo desfiando"),
        dict(nome="aneis", quadros=NPART, plano="atras", o_que="anéis de fumaça que saem dos cones, crescem, se afastam e se desfazem"),
        dict(nome="nevoa", quadros=NPART, plano="atras", o_que="névoa baixa deslizando no chão"),
        dict(nome="cacos", quadros=N, plano="atras", o_que="cacos de vidro verde e tampinhas pulando a cada grave"),
        dict(nome="fagulhas", quadros=NPART, plano="atras", o_que="fagulhas laranja em forma de folha subindo")], pal,
        extras=dict(nota="Compasso de 4 tempos em 48 quadros (12 por tempo, 150 bpm a 2 tiques). Tudo atrás do corpo. "
                         "O miolo da parede (atrás do corpo) é remendo: caixas dos lados copiadas.",
                    gerado_por="ferramentas/aura_blender/" + os.path.basename(__file__)))

    # ---------------- medidas
    med = dict(C.mede_conjunto(CAM, pal, NPART))
    for nome, lst in list(CAM.items()) + [("paredao_sem_realce_nem_fumaca", seca)]:
        med[nome] = C.mede_camada(lst, pal)
    ch = chicote(pasta, mostra=False)
    med["passo_max_juntas_px"] = max(v["passo_max"] for v in ch.values())
    med["passo_max_raio_cone_px"] = round(max(abs(pontos[(f + 1) % N][k][2] - pontos[f][k][2]) * 0.62 * cones[k[2:]][2] * float(peso_cone(0.62))
                                              for f in range(N) for k in pontos[0] if k.startswith("k_")), 2)
    c_rgb, c_m = C.reduz(C.conceito_para_4x(f"{rec}/corpo.png", TELA, dx=info["dx"]), TELA.amp)
    cb = C.caixa(c_m); x0, x1, y0 = med["extensao_aura_x_min_max_y_min"]
    med["corpo_no_jogo"] = dict(caixa=cb, altura=cb[3] - cb[1], largura=cb[2] - cb[0])
    med["aura_sobre_corpo"] = dict(largura=round((x1 - x0 + 1) / (cb[2] - cb[0]), 2), altura=round((TELA.pe[1] - y0) / (cb[3] - cb[1]), 2),
                                   largura_px=x1 - x0 + 1, altura_px=TELA.pe[1] - y0)
    med["compasso"] = dict(quadros=N, tiques_por_quadro=TIQ, quadros_por_tempo=NB, bpm=round(3600 / (NB * TIQ)), laco_lento=NPART)
    json.dump(med, open(f"{pasta}/medidas.json", "w"), indent=1)
    for k, v in med.items():
        print(k, json.dumps(v))

    # ---------------- tiras e vídeo com o corpo na frente
    corpo = np.dstack([np.clip(c_rgb, 0, 255).astype(np.uint8), (c_m * 255).astype(np.uint8)]); corpo[~c_m] = 0
    fundo = C.fundo_teste(TELA)
    Q_ = [C.compoe(fundo, f, CAM.values(), corpo, [], pal) for f in range(NPART)]
    C.tira(Q_[:16], f"{pasta}/tira.png", rotulos=[f"q{f:02d}" for f in range(16)])                       # 16 quadros consecutivos
    C.tira([Q_[f] for f in range(0, NPART, 6)], f"{pasta}/tira_ciclo.png", rotulos=[f"q{f:02d}" for f in range(0, NPART, 6)])
    zoom = lambda q, x0, y0, x1, y1: q[y0:y1, x0:x1]
    C.tira([zoom(Q_[f], 76, 96, 166, 186) for f in range(44, 60)], f"{pasta}/tira_zoom_cones.png", cols=8, esc=4,
           rotulos=[f"q{f % N:02d}" for f in range(44, 60)])        # passa pela emenda (47 -> 0) e pelo 1º tempo
    C.tira([zoom(Q_[f], 190, 150, 300, 196) for f in range(0, 12)], f"{pasta}/tira_zoom_chao.png", cols=4, esc=4,
           rotulos=[f"q{f:02d}" for f in range(0, 12)])
    C.tira([zoom(Q_[f], 60, 40, 300, 110) for f in range(0, 48, 4)], f"{pasta}/tira_zoom_topo.png", cols=3, esc=2,
           rotulos=[f"q{f:02d}" for f in range(0, 48, 4)])
    C.tira([C.compoe(fundo, f, CAM.values(), None, [], pal) for f in (0, 6, 30, 54)], f"{pasta}/tira_sem_corpo.png", cols=2, esc=3)
    C.tira([zoom(C.compoe(fundo, f, [parede], None, [], pal), 60, 20, 300, 196) for f in range(0, 48, 6)], f"{pasta}/tira_parede_so.png", cols=4, esc=3,
           rotulos=[f"q{f:02d}" for f in range(0, 48, 6)])          # só a parede, de 6 em 6: o balanço das caixas
    C.tira([zoom(C.compoe(fundo, f, [parede, aneis], None, [], pal), 56, 60, 200, 190) for f in range(20, 44, 2)], f"{pasta}/tira_zoom_aneis.png", cols=4, esc=4,
           rotulos=[f"q{f:02d}" for f in range(20, 44, 2)])         # anéis nascendo e se desfazendo
    C.video_laco(f"{pasta}/aura_ck.mp4", Q_, TIQ)


def instala(pasta):
    C.instala(os.path.join(pasta, "camadas"), os.path.join(C.RAIZ, "sprites", ID, "aura"))


if __name__ == "__main__":
    import tempfile
    C.roda(__file__, {"recortes": recortes, "rig": rig, "chicote": chicote, "compor": compor, "instala": instala}, os.path.join(tempfile.gettempdir(), "aura_blender", ID))
