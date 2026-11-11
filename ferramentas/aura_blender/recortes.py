"""Passo 1: recortes do conceito com alfa limpo. Saída em recortes/ (resolução do conceito).
v2: fragmentos soltos ficam NA asa (silhueta do conceito), ossos de ouro reforçados no próprio desenho, raiz
arredondada que passa do meio do corpo (sem corte reto nem vão), buraco dos pés na brasa fechado com clone da faixa."""
from PIL import Image
import numpy as np, cv2, json, os
from scipy import ndimage as ndi
SRC = "C:/Dev/Jogo-de-Luta-bosses/sprites/hazaki/quadros/folhas_arcade/d_conceito.png"
os.makedirs("recortes", exist_ok=True)
im = np.array(Image.open(SRC).convert("RGB"))
I = im.astype(int); R, G, B = I[..., 0], I[..., 1], I[..., 2]
H, W = R.shape
bg = (R > 170) & (B > 170) & (G < 110)
fg = ~bg
DX = 1113   # corpo da vista 1 -> vista 3
CXM = 1313  # eixo de espelho das asas
# --- corpo (vista 1)
corpo = np.zeros((H, W), bool); corpo[:, 28:353] = fg[:, 28:353]
corpo = ndi.binary_opening(corpo, iterations=1)
lab, n = ndi.label(corpo); sz = ndi.sum(corpo, lab, range(1, n + 1)); corpo = lab == (1 + int(np.argmax(sz)))
corpo = ndi.binary_fill_holes(corpo) & fg
corpo = ndi.binary_erosion(corpo, iterations=1)
borda = corpo & ~ndi.binary_erosion(corpo, iterations=3)
corpo &= ~(borda & ((R - G) > 60) & ((B - G) > 60) & (B > 120))
ys, xs = np.where(corpo); bb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1); print("corpo bbox", bb)
Image.fromarray(np.dstack([im, (corpo * 255).astype(np.uint8)])[:, :400]).save("recortes/corpo_v1.png")
corpo3 = np.zeros_like(corpo); corpo3[:, DX:] = corpo[:, :W - DX]
corpo3d = ndi.binary_dilation(corpo3, iterations=5)
# --- aura (vista 3): dourado nunca tem azul acima do verde
aura = fg.copy(); aura[:, :725] = False; aura[:, 1895:] = False
aura &= ~corpo3d
rosa = (B > G + 25) | ((B > G - 20) & (B > 120))
aura[540:, 1830:] = False; aura[:, 1816:][600:] = False
aura &= ~rosa
aura = ndi.binary_opening(aura, iterations=1)
rgbA = im.copy(); rgbA[..., 2] = np.minimum(rgbA[..., 2], rgbA[..., 1])   # tira o derrame de magenta


def salva(nome, mask, rgb=rgbA):
    o = np.dstack([rgb, (mask * 255).astype(np.uint8)]); o[~mask] = 0
    Image.fromarray(o).save(f"recortes/{nome}.png")


# ossos de ouro da asa esquerda lidos do desenho (x, y, largura em px do conceito); a direita é o espelho
OSSOS_DESENHO = [
    [(1146, 168, 17), (1170, 227, 17), (1193, 287, 18), (1240, 310, 17), (1262, 320, 16), (1300, 338, 15), (1330, 350, 14)],  # punho-cotovelo-ombro
    [(1143, 153, 13), (1113, 127, 12), (1083, 100, 12), (1063, 88, 11), (1023, 77, 10), (983, 68, 8), (955, 61, 6)],          # dedo 1 (borda de cima)
    [(1140, 156, 12), (1100, 155, 12), (1050, 158, 11), (1007, 160, 10), (960, 171, 8), (925, 178, 6)],                        # dedo 2
    [(1137, 166, 12), (1100, 187, 12), (1067, 213, 11), (1040, 240, 10), (1007, 273, 9), (983, 303, 7), (965, 328, 6)],        # dedo 3
    [(1140, 172, 12), (1127, 197, 12), (1117, 240, 11), (1112, 287, 10), (1113, 322, 8), (1110, 345, 6)],                      # dedo 4
    [(1150, 151, 15), (1173, 147, 14), (1190, 157, 11), (1197, 172, 7), (1199, 186, 4)],                                       # garra
]
# camadas do osso: (cor, quanto a largura encolhe, desvio para cima em fração da largura)
OURO = [((70, 20, 6), 0, 0.0), ((214, 100, 8), -4, 0.0), ((250, 176, 24), -7, -0.10), ((254, 226, 110), -11, -0.22)]


def discos(pts, n=40):
    m = np.zeros((H, W), np.uint8)
    for (x0, y0, r0), (x1, y1, r1) in zip(pts, pts[1:]):
        for t in np.linspace(0, 1, n):
            cv2.circle(m, (int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t)), int(r0 + (r1 - r0) * t), 1, -1)
    return m > 0


coroa = aura.copy(); coroa[:, :1235] = False; coroa[:, 1395:] = False; coroa[250:] = False
lab, n = ndi.label(coroa); sz = ndi.sum(coroa, lab, range(1, n + 1)); coroa_m = lab == (1 + int(np.argmax(sz)))
chao = aura.copy(); chao[:625] = False
resto = aura & ~coroa; resto[625:] = False
info = {}
for nome, sl, lado in (("asa_esq", slice(0, CXM), -1), ("asa_dir", slice(CXM, W), 1)):
    def X(x):
        return x if lado < 0 else 2 * CXM - x
    m = np.zeros_like(resto); m[:, sl] = resto[:, sl]
    lab, n = ndi.label(m, structure=np.ones((3, 3))); sz = ndi.sum(m, lab, range(1, n + 1))
    k = 1 + int(np.argmax(sz)); asa = lab == k
    frag = []; gotas = []
    for i in range(1, n + 1):
        if i == k or sz[i - 1] < 120: continue
        ys, xs = np.where(lab == i)
        d = dict(x0=int(xs.min()), y0=int(ys.min()), x1=int(xs.max()) + 1, y1=int(ys.max()) + 1, area=int(sz[i - 1]))
        if sz[i - 1] >= 500 and min(d["x1"] - d["x0"], d["y1"] - d["y0"]) >= 20:
            frag.append(d); asa |= lab == i          # pedaço de nota queimando: fica na asa, mexe com a ponta do dedo
        else:
            gotas.append(d)                          # gota comprida: vira partícula
    info[nome + "_fragmentos"] = frag; info[nome + "_gotas_do_desenho"] = gotas
    # raiz escondida: toco arredondado ao longo do osso do braço, só atrás do corpo, passando do meio (as asas se cruzam)
    toco = discos([(X(1215), 335, 95), (X(1275), 348, 70), (X(1335), 358, 44)])
    faixa = toco & ndi.binary_dilation(corpo3d, iterations=2) & ~asa
    full = rgbA.copy()
    yy, xx = np.where(faixa)
    for kk in range(1, 4):     # clona penas da própria asa para trás do corpo
        if len(yy) == 0: break
        sy = yy + 14 * kk; sx = xx + lado * 96 * kk      # fonte: as penas abaixo do braço (sem osso)
        ok = (sy >= 0) & (sx >= 0) & (sx < W); ok[ok] &= asa[sy[ok], sx[ok]]
        full[yy[ok], xx[ok]] = rgbA[sy[ok], sx[ok]]
        yy, xx = yy[~ok], xx[~ok]
    falta = np.zeros_like(asa); falta[yy, xx] = True           # o que não achou fonte: vizinho mais próximo
    idx = ndi.distance_transform_edt(~((asa | faixa) & ~falta), return_distances=False, return_indices=True)
    full[falta] = full[idx[0], idx[1]][falta]
    tot = asa | faixa
    tot2 = ndi.binary_closing(tot, iterations=3) & (tot | corpo3d)
    idx = ndi.distance_transform_edt(~tot, return_distances=False, return_indices=True)
    novo = tot2 & ~tot; full[novo] = full[idx[0], idx[1]][novo]; tot = tot2
    # ossos reforçados (desenhados 4x e reduzidos, para a borda sair limpa)
    big = np.ascontiguousarray(cv2.resize(full, (W * 4, H * 4), interpolation=cv2.INTER_NEAREST)); g0 = big.copy()
    for cor, dl, dv in OURO:
        for linha in OSSOS_DESENHO:
            pts = [(X(x), y, w) for x, y, w in linha]
            for (x0, y0, w0), (x1, y1, w1) in zip(pts, pts[1:]):
                for t in np.linspace(0, 1, 16):
                    wb = w0 + (w1 - w0) * t; w = wb + dl
                    if w < 1.2: continue
                    cv2.circle(big, (int(round((x0 + (x1 - x0) * t) * 4)), int(round((y0 + (y1 - y0) * t + dv * wb) * 4))), int(round(w * 2)), cor, -1)
    for cor, r, dy in (((70, 20, 6), 13, 0), ((214, 100, 8), 11, 0), ((250, 176, 24), 9, -1), ((254, 226, 110), 5, -3)):
        cv2.circle(big, (X(1143) * 4, (157 + dy) * 4), r * 4, cor, -1)   # nó do punho
    mud = (big != g0).any(-1)
    osso_m = cv2.resize(mud.astype(np.uint8) * 255, (W, H), interpolation=cv2.INTER_AREA) > 127
    osso_rgb = cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA)
    osso_m &= ndi.binary_dilation(tot, iterations=2)
    full[osso_m] = osso_rgb[osso_m]; tot |= osso_m
    salva(nome, tot, full)
    ys, xs = np.where(tot)
    info[nome] = dict(bbox=[int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1], raiz_px=int(faixa.sum()), osso_px=int(osso_m.sum()))
salva("coroa", coroa_m)
# chão: fecha o buraco dos pés espelhando para dentro a própria faixa de cada lado (não por borrão)
cols = np.where(chao.any(0))[0]
buraco = [x for x in range(CXM - 130, CXM + 130) if chao[625:, x].sum() < 5]
bx0, bx1 = min(buraco) - 6, max(buraco) + 7; print("buraco do chao", bx0, bx1)
full = rgbA.copy(); chm = chao.copy(); meio = (bx0 + bx1) // 2
for x in range(bx0, bx1):
    src = bx0 - 1 - (x - bx0) if x < meio else bx1 + (bx1 - 1 - x)
    full[625:, x] = rgbA[625:, src]; chm[625:, x] = chao[625:, src]
salva("chao", chm, full)
salva("aura_parada", aura)     # aura inteira parada (para o painel de referência), sem retoque
info["corpo_bbox"] = [int(v) for v in bb]; info["DX"] = DX
ys, xs = np.where(coroa_m); info["coroa_bbox"] = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
ys, xs = np.where(chm); info["chao_bbox"] = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
json.dump(info, open("recortes/info.json", "w"), indent=1)
print({k: (v if not isinstance(v, list) else len(v)) for k, v in info.items()})


def prev(nomes, arq, box):
    c = np.full((H, W, 3), 70, np.uint8)
    for nn in nomes:
        a = np.array(Image.open(f"recortes/{nn}.png"))
        if a.shape[1] < W: a = np.pad(a, ((0, 0), (0, W - a.shape[1]), (0, 0)))
        if nn == "corpo_v1": a = np.roll(a, DX, axis=1)
        mm = a[..., 3] > 0; c[mm] = a[..., :3][mm]
    Image.fromarray(c[box[1]:box[3], box[0]:box[2]]).save(arq)


prev(["asa_esq", "asa_dir", "coroa", "chao"], "p_aura.png", (720, 20, 1900, 710))
