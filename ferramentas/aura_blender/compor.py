"""Passos 3-7: reduz o render do Blender para o tamanho do jogo e a paleta fixa, soma fogo/notas/gotas/brasa em loop,
salva as camadas, monta os vídeos, a tira e as medidas.
v2: 48 quadros de asa (2 tiques), partículas com laço de 96 quadros (2 batidas), paleta com cor escura de contorno,
encaixe na paleta com histerese (menos fervura), contorno queimado, notas retangulares que planam, gotas grossas."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np, cv2, json, os, subprocess, math
from scipy import ndimage as ndi
S = 112 / 441.0; CX = 1313.0; CHAO = 697.0
CW, CH, AMP = 360, 200, 4
os.makedirs("camadas", exist_ok=True)
for a in os.listdir("camadas"): os.remove(os.path.join("camadas", a))
info = json.load(open("recortes/info.json"))
PT = json.load(open("render/pontos.json"))
pontos = PT["pontos"]; N = len(pontos)      # quadros da batida da asa
TIQ = 2                                     # tiques do jogo por quadro
NPART = 2 * N                               # laço das partículas e do chão: 2 batidas (não repete a cada batida)
T = 96                                      # lado do ruído ladrilhável (múltiplo de N e de NPART/… para fechar)
rng = np.random.default_rng(7)


def reduz(rgba4):
    """4x -> 1x: média só dos subpixels opacos, alfa por maioria. Devolve rgb float e máscara."""
    a = rgba4[..., 3].astype(np.float32) / 255.0
    h, w = a.shape[0] // AMP, a.shape[1] // AMP
    a4 = a.reshape(h, AMP, w, AMP)
    cob = a4.mean((1, 3))
    rgb = (rgba4[..., :3].astype(np.float32) * a[..., None]).reshape(h, AMP, w, AMP, 3).sum((1, 3))
    rgb /= np.maximum(a4.sum((1, 3)), 1e-6)[..., None]
    return rgb, cob >= 0.5


def conceito_para_4x(arq, dx=0.0):
    """Leva um recorte na resolução do conceito para o quadro 4x do jogo (vizinho mais próximo, escala ~1,016)."""
    im = cv2.imread(arq, cv2.IMREAD_UNCHANGED)[..., [2, 1, 0, 3]]
    k = S * AMP
    M = np.array([[k, 0, (CW / 2) * AMP - (CX - dx) * k], [0, k, 190 * AMP - CHAO * k]], np.float32)
    return cv2.warpAffine(im, M, (CW * AMP, CH * AMP), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


# ---------- paleta fixa de 15 cores: 14 tiradas do próprio desenho (asas + coroa + brasa) + 1 escura de contorno
partes = [reduz(conceito_para_4x(f"recortes/{n}.png")) for n in ("asa_esq", "asa_dir", "coroa", "chao")]
px = np.concatenate([r[m] for r, m in partes]).astype(np.float32)
crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
cv2.setRNGSeed(3)
_, _, cent = cv2.kmeans(px, 14, None, crit, 8, cv2.KMEANS_PP_CENTERS)
PAL = np.vstack([np.clip(np.round(cent), 0, 255), [[52, 14, 10]]]).astype(np.uint8)
PAL = PAL[np.argsort(PAL.astype(int) @ np.array([299, 587, 114]))]   # do mais escuro ao mais claro
json.dump(PAL.tolist(), open("camadas/paleta.json", "w"))
print("PALETA", PAL.tolist())
PALf = PAL.astype(np.float32)
PESO = np.array([2, 4, 1], np.float32)


def dist_pal(rgb):
    return ((rgb[..., None, :] - PALf[None, None]) ** 2 * PESO).sum(-1)


def na_paleta(rgb, m):
    """índices da paleta (-1 = transparente)."""
    idx = dist_pal(rgb).argmin(-1).astype(np.int16); idx[~m] = -1
    return idx


def na_paleta_seq(quadros, folga=420.0):
    """Encaixe na paleta com histerese: se a cor que o pixel tinha no quadro anterior ainda serve quase tão bem,
    fica com ela. Tira o pisca-pisca de pixel que está na fronteira entre duas cores. Duas voltas para fechar o laço."""
    ant = None; out = []
    for volta in range(2):
        out = []
        for rgb, m in quadros:
            d = dist_pal(rgb); best = d.argmin(-1).astype(np.int16)
            if ant is not None:
                ok = (ant >= 0) & m
                da = np.take_along_axis(d, np.clip(ant, 0, None)[..., None].astype(np.int64), -1)[..., 0]
                fica = ok & (da <= d.min(-1) + folga)
                best[fica] = ant[fica]
            best[~m] = -1; ant = best; out.append(best)
    return out


def rgba(idx):
    o = np.zeros(idx.shape + (4,), np.uint8); m = idx >= 0
    o[m, :3] = PAL[idx[m]]; o[m, 3] = 255
    return o


sat = PAL.max(1).astype(int) - PAL.min(1)
F_CLARO = 14
F_AMAR = max((i for i in range(15) if PAL[i][0] > 230 and PAL[i][1] > 170), key=lambda i: sat[i])
F_LAR = max((i for i in range(15) if PAL[i][0] > 200 and 90 < PAL[i][1] < 170), key=lambda i: sat[i], default=8)
F_VERM = max((i for i in range(15) if 120 < PAL[i][0] and PAL[i][1] < 95), key=lambda i: int(PAL[i][0]), default=4)
F_ESC = 0
RAMPA = [F_CLARO, F_CLARO, F_AMAR, F_AMAR, F_LAR, F_LAR, F_VERM, F_VERM, F_VERM]
print("FOGO", [PAL[i].tolist() for i in (F_CLARO, F_AMAR, F_LAR, F_VERM, F_ESC)])


# ---------- ruído que emenda (ladrilhável TxT, rola um número inteiro de voltas no loop)
def ladrilho(seed, n=T, fmax=8):
    r = np.random.default_rng(seed); y, x = np.mgrid[0:n, 0:n] / n
    t = np.zeros((n, n))
    for _ in range(48):
        fx, fy = r.integers(-fmax, fmax + 1, 2)
        if fx == 0 and fy == 0: continue
        t += np.sin(2 * np.pi * (fx * x + fy * y) + r.uniform(0, 6.28)) / (1 + 0.25 * math.hypot(fx, fy))
    return (t - t.min()) / (t.max() - t.min())


R1, R2, R3 = ladrilho(1), ladrilho(2, fmax=13), ladrilho(3, fmax=6)
YY, XX = np.mgrid[0:CH, 0:CW]


def ruido(f):
    """campo 0..1 que sobe (rola para cima); fecha em N quadros (2f e 4f são múltiplos de T quando f = N)."""
    return 0.5 * R1[(YY + 2 * f) % T, XX % T] + 0.5 * R2[(YY + 4 * f) % T, (XX + 17) % T]


def linguas(idx, f, alt=7, forca=0.0, lim=0.36):
    """língua de fogo subindo da borda de cima do que estiver desenhado em idx."""
    A = idx >= 0; n = ruido(f)
    out = idx.copy()
    livre = ~A
    for d in range(1, alt + 1):
        base = np.zeros_like(A); base[:-d] = A[d:]            # tem desenho d pixels abaixo
        if d > 1:
            mid = np.zeros_like(A); mid[:-(d - 1)] = A[d - 1:]; livre = livre & ~mid   # e nada no caminho
        m = base & livre & (n > lim + 0.085 * d - forca)
        out[m] = RAMPA[min(d, len(RAMPA) - 1)]
    return out


def contorno(idx):
    """contorno queimado (cor escura) na borda de baixo e dos lados; a borda de cima fica para o fogo."""
    m = idx >= 0
    dentro = ndi.binary_erosion(m, structure=ndi.generate_binary_structure(2, 1), border_value=0)
    cima_vazio = np.ones_like(m); cima_vazio[1:] = ~m[:-1]
    viz = ndi.uniform_filter(m.astype(np.float32), 3) * 9
    b = m & ~dentro & ~cima_vazio & (viz >= 4.5)
    out = idx.copy(); out[b] = F_ESC
    return out


def limpa(idx, minimo=6):
    lab, n = ndi.label(idx >= 0, structure=np.ones((3, 3)))
    if n:
        sz = ndi.sum(idx >= 0, lab, range(1, n + 1))
        for i in np.where(sz < minimo)[0]: idx[lab == i + 1] = -1
    return idx


# ---------- camadas base por quadro (render do Blender)
brutos = {"asas": [], "coroa": []}
for f in range(N):
    for nome in brutos:
        brutos[nome].append(reduz(np.array(Image.open(f"render/{nome}_{f:02d}.png").convert("RGBA"))))
asas_sem_fogo = [contorno(limpa(a)) for a in na_paleta_seq(brutos["asas"])]
asas = [linguas(a, f, alt=8, forca=0.08) for f, a in enumerate(asas_sem_fogo)]
coroas = []
for f, c in enumerate(na_paleta_seq(brutos["coroa"])):       # coroa: ouro derretido cintila e solta fogo
    c = contorno(c); n = ruido(f); m = c > F_ESC
    c[m & (n > 0.66)] = np.minimum(c[m & (n > 0.66)] + 2, 14)
    c[m & (n < 0.30)] = np.maximum(c[m & (n < 0.30)] - 1, 1)
    coroas.append(linguas(c, f, alt=5, forca=0.10))

# ---------- chão: brasa que ondula, cintila, solta línguas e fagulhas (laço de NPART quadros)
ch_idx = na_paleta(*reduz(conceito_para_4x("recortes/chao.png")))
fag = [dict(x=int(rng.integers(36, 324)), b=int(rng.integers(0, NPART)), dx=float(rng.uniform(-0.35, 0.35)), v=float(rng.uniform(0.8, 1.7)),
            vida=int(rng.integers(22, 40))) for _ in range(46)]
chaos = []
xs_ = np.arange(CW)
for f in range(NPART):
    w = 2 * math.pi * f / NPART
    # a faixa inteira ondula: cada coluna sobe/desce até 2 px numa onda que corre para os lados (a base no chão fica)
    dy = np.round(1.3 * np.sin(2 * w + xs_ / 9.0) + 1.0 * np.sin(3 * w - xs_ / 5.5 + 1.0)).astype(int)
    c = np.full_like(ch_idx, -1)
    for x in range(CW):
        col = ch_idx[:, x]
        if dy[x] > 0:   c[:-dy[x], x] = col[dy[x]:]; c[-dy[x] - 11:, x] = np.where(col[-dy[x] - 11:] >= 0, col[-dy[x] - 11:], c[-dy[x] - 11:, x])
        elif dy[x] < 0: c[-dy[x]:, x] = col[:dy[x]]
        else:           c[:, x] = col
    c[190:] = -1
    n = R3[(YY + 3 * f) % T, (XX + 2 * f) % T] * 0.6 + R2[(YY + 2 * f) % T, (XX - f) % T] * 0.4
    m = c >= 0
    c[m & (n > 0.60)] = np.minimum(c[m & (n > 0.60)] + 2, 14)
    c[m & (n < 0.38)] = np.maximum(c[m & (n < 0.38)] - 2, 1)
    c = linguas(c, f, alt=9, forca=0.16)
    for p in fag:
        a = (f - p["b"]) % NPART
        if a < p["vida"]:
            y = int(round(184 - p["v"] * a - 0.012 * a * a)); x = int(round(p["x"] + p["dx"] * a + 1.6 * math.sin(a * 0.45 + p["x"])))
            q = a / p["vida"]
            if 0 <= y < CH and 0 <= x < CW:
                c[y, x] = F_CLARO if q < 0.3 else F_AMAR if q < 0.6 else F_LAR if q < 0.85 else F_VERM
                if q < 0.3 and y + 1 < 190: c[y + 1, x] = F_AMAR
    chaos.append(c)

# ---------- partículas: notas que planam + gotas de ouro (laço de NPART quadros)
def nota_base():
    """nota de dinheiro 13x7 px (desenhada 4x): contorno queimado, papel claro, tarjas e medalhão."""
    w, h = 13, 7; a = np.full((h, w), 12, np.int16)
    a[0, :] = a[-1, :] = F_ESC; a[:, 0] = a[:, -1] = F_ESC
    a[1, 1:-1] = 13; a[-2, 1:-1] = F_AMAR
    a[1:-1, 2] = F_LAR; a[1:-1, -3] = F_LAR
    a[2:5, 5:8] = F_LAR; a[3, 6] = F_VERM; a[2, 5] = a[2, 7] = a[4, 5] = a[4, 7] = 12
    o = np.zeros((h, w, 4), np.uint8); o[..., :3] = PAL[a]; o[..., 3] = 255
    return np.repeat(np.repeat(o, AMP, 0), AMP, 1)


NOTA = nota_base()
PONTAS = ["esq_d1c", "dir_d2c", "esq_d3c", "dir_d1c", "esq_d2c", "dir_d4c", "esq_d4c", "dir_d3c"]
NN = 12; VIDA = 70


def nota_quadro(ang, achat, esc):
    h, w = NOTA.shape[:2]; Tm = int(math.hypot(h, w)) + 8; Tm += (-Tm) % AMP
    c, s_ = math.cos(ang), math.sin(ang)
    A = np.array([[c * esc, -s_ * esc * achat], [s_ * esc, c * esc * achat]])
    t = np.array([Tm / 2, Tm / 2]) - A @ np.array([w / 2, h / 2])
    o = cv2.warpAffine(NOTA, np.hstack([A, t[:, None]]).astype(np.float32), (Tm, Tm), flags=cv2.INTER_NEAREST, borderValue=0)
    return na_paleta(*reduz(o))


def carimba(dst, src, cx, cy):
    h, w = src.shape; x0 = int(round(cx - w / 2)); y0 = int(round(cy - h / 2))
    ya, yb = max(0, y0), min(CH, y0 + h); xa, xb = max(0, x0), min(CW, x0 + w)
    if ya >= yb or xa >= xb: return
    s = src[ya - y0:yb - y0, xa - x0:xb - x0]; d = dst[ya:yb, xa:xb]; d[s >= 0] = s[s >= 0]


def ponto(dst, x, y, c):
    if 0 <= y < 189 and 0 <= x < CW: dst[y, x] = c


# gotas: (âncora, nascimento, período). Engorda presa (fio + bolha), solta, cai acelerando, respinga.
GOTAS = [("esq_garra", 0, N), ("dir_garra", 29, N), ("esq_d4c", 14, NPART), ("dir_d4c", 61, NPART), ("esq_d3c", 40, NPART), ("dir_d3c", 5, NPART),
         ("esq_d5b", 70, NPART), ("dir_d5b", 22, NPART), ("esq_d2c", 52, NPART), ("dir_d2c", 84, NPART), ("esq_d4b", 33, NPART), ("dir_d4b", 77, NPART),
         ("esq_d3b", 88, NPART), ("dir_d3b", 46, NPART),
         ("coroa:-9:9", 6, N), ("coroa:1:11", 21, N), ("coroa:8:9", 37, N), ("coroa:-4:10", 60, NPART), ("coroa:5:10", 90, NPART)]
PRESA = 18


def ancora(nome, f):
    f %= N
    if nome.startswith("coroa"):
        _, ox, oy = nome.split(":"); cx, cy, rot, cz = pontos[f]["coroa"]
        ox, oy = float(ox) * cz, float(oy)
        return cx + ox * math.cos(rot) + oy * math.sin(rot), cy + oy * math.cos(rot) - ox * math.sin(rot)
    return pontos[f][nome]


def gota(L, nome, a, f):
    if a < PRESA:                                    # presa: fio que estica e bolha que engorda
        x, y = ancora(nome, f); x = int(round(x)); y = int(round(y))
        comp = 1 + a // 4
        for k in range(comp): ponto(L, x, y + k, F_AMAR)
        yb = y + comp
        ponto(L, x, yb, F_CLARO); ponto(L, x, yb + 1, F_AMAR)
        if a >= 6: ponto(L, x + 1, yb, F_AMAR); ponto(L, x + 1, yb + 1, F_LAR)
        if a >= 12: ponto(L, x, yb + 2, F_LAR); ponto(L, x - 1, yb + 1, F_AMAR); ponto(L, x + 1, yb + 2, F_VERM)
        return
    t = a - PRESA; x, y0 = ancora(nome, f - t); x = int(round(x))
    y = int(round(y0 + 6 + 0.45 * t + 0.075 * t * t))
    if y < 186:                                      # caindo: lágrima 2x5 com rabo
        ponto(L, x, y - 4, F_LAR); ponto(L, x, y - 3, F_AMAR); ponto(L, x, y - 2, F_AMAR)
        ponto(L, x, y - 1, F_CLARO); ponto(L, x + 1, y - 1, F_AMAR); ponto(L, x - 1, y - 1, F_AMAR)
        ponto(L, x, y, F_CLARO); ponto(L, x + 1, y, F_LAR); ponto(L, x - 1, y, F_LAR); ponto(L, x, y + 1, F_LAR)
    else:                                            # respingo: 5 quadros
        tq = next(k for k in range(200) if y0 + 6 + 0.45 * k + 0.075 * k * k >= 185.5); s = t - tq
        if s < 5:
            for dx in (-1 - s, 1 + s):
                ponto(L, x + dx, 187 - (2 if s in (1, 2) else 1 if s in (0, 3) else 0), F_CLARO if s < 2 else F_AMAR)
            if s < 3: ponto(L, x, 188, F_CLARO); ponto(L, x - 1, 188, F_AMAR); ponto(L, x + 1, 188, F_AMAR)


parts = []; viv = []
semente = [dict(ph=float(rng.uniform(0, 6.28)), ph2=float(rng.uniform(0, 6.28)), a0=float(rng.uniform(-0.5, 0.5)), vy=float(rng.uniform(0.75, 1.05)),
                amp=float(rng.uniform(5, 9)), b=(i * 8 + int(rng.integers(0, 5))) % NPART) for i in range(NN)]
for f in range(NPART):
    L = np.full((CH, CW), -1, np.int16); vivas = 0
    for i, sd in enumerate(semente):
        a = (f - sd["b"]) % NPART
        if a >= VIDA: continue
        tip = PONTAS[i % len(PONTAS)]; x0, y0 = pontos[sd["b"] % N][tip]
        lado = -1 if tip.startswith("esq") else 1
        bal = 2 * math.pi * a / 32 + sd["ph"]                     # balanço de folha caindo
        x = x0 + lado * 0.22 * a + sd["amp"] * math.sin(bal) * min(1, a / 10)
        y = y0 + sd["vy"] * a + 0.006 * a * a - 1.5 * abs(math.cos(bal)) * min(1, a / 10)
        if y > 183: continue
        ang = sd["a0"] + 0.55 * math.cos(bal)                     # inclina para o lado em que está indo
        achat = math.cos(2 * math.pi * a / 44 + sd["ph2"]); achat = math.copysign(max(abs(achat), 0.45), achat)
        im = nota_quadro(ang, achat, min(1.0, 0.55 + a * 0.09))
        fim = min(VIDA - a, (183 - y) / 1.2)                      # queima no fim da vida ou perto do chão
        m = im >= 0
        hh, ww = im.shape; nz = R2[:hh, (np.arange(ww) + 9 * i) % T]
        qm = 0.18 + 0.12 * math.sin(a * 0.2 + i)                  # canto sempre comido pelo fogo
        if fim < 14: qm = max(qm, (14 - fim) / 14 * 1.05)
        com = m & (nz < qm)
        im[com] = -1
        beira = (im >= 0) & ndi.binary_dilation(com)
        im[beira] = np.where(R1[:hh, (np.arange(ww) + 3 * f) % T][beira] > 0.5, F_CLARO, F_LAR)
        if fim < 7: im[im >= 0] = np.where(im[im >= 0] > 9, F_LAR, F_VERM)
        if (im >= 0).sum() > 3: vivas += 1
        carimba(L, im, x, y)
    viv.append(vivas)
    L = linguas(L, f, alt=4, forca=0.10)
    for nome, b, per in GOTAS:
        gota(L, nome, (f - b) % per, f)
    parts.append(L)
print("NOTAS vivas por quadro:", min(viv), "a", max(viv))

for nome, lst in (("asas", asas), ("coroa", coroas), ("chao", chaos), ("particulas", parts)):
    for f in range(len(lst)):
        Image.fromarray(rgba(lst[f])).save(f"camadas/{nome}_{f:02d}.png")

# ---------- corpo (vista 1) no tamanho do jogo, 15 cores próprias (só para o vídeo)
c_rgb, c_m = reduz(conceito_para_4x("recortes/corpo_v1.png", dx=info["DX"]))
cq = Image.fromarray(np.clip(c_rgb, 0, 255).astype(np.uint8)).quantize(15, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
corpo = np.dstack([np.array(cq), (c_m * 255).astype(np.uint8)]); corpo[~c_m] = 0
Image.fromarray(corpo).save("camadas/corpo_previa.png")
ys, xs = np.where(c_m); print("CORPO no jogo: altura", ys.max() - ys.min() + 1, "largura", xs.max() - xs.min() + 1)

# ---------- referência: o desenho parado (asas, coroa, notas soltas, gotas, brasa), só pulsando de escala
parada = rgba(na_paleta(*reduz(conceito_para_4x("recortes/aura_parada.png"))))


def antes_quadro(i):
    k = 1 + 0.03 * math.sin(2 * math.pi * i / 8)
    M = np.array([[k, 0, 180 * (1 - k)], [0, k, 190 * (1 - k)]], np.float32)
    return cv2.warpAffine(parada, M, (CW, CH), flags=cv2.INTER_NEAREST, borderValue=0)


ANTES = [antes_quadro(i) for i in range(8)]

# ---------- composição
fundo = np.zeros((CH, CW, 3), np.uint8)
for y in range(CH):
    t = y / 190
    fundo[y] = (26 + 16 * t, 28 + 15 * t, 40 + 14 * t) if y < 190 else (30, 28, 32)
fundo[190] = (58, 54, 60)
for x in range(0, CW, 45):                       # pilares discretos de cenário
    fundo[60:190, x:x + 14] = (fundo[60:190, x:x + 14].astype(int) * 0.86).astype(np.uint8)


def sobre(base, cam):
    m = cam[..., 3] > 0; base[m] = cam[..., :3][m]


def quadro_novo(f, com_corpo=True):
    o = fundo.copy()
    for lst in (chaos, asas, coroas, parts): sobre(o, rgba(lst[f % len(lst)]))
    if com_corpo: sobre(o, corpo)
    return o


def quadro_antes(i):
    o = fundo.copy(); sobre(o, ANTES[i]); sobre(o, corpo); return o


NOVOS = [quadro_novo(f) for f in range(NPART)]
VELHOS = [quadro_antes(i) for i in range(8)]

# ---------- medidas
CAM = (("chao", chaos), ("asas", asas), ("coroa", coroas), ("particulas", parts))
uni = [np.where(np.any([(l[f % len(l)] >= 0) for _, l in CAM], 0)) for f in range(NPART)]
med = {"quadros_asa": N, "tiques_por_quadro": TIQ, "quadros_particulas_e_chao": NPART, "duracao_batida_s": N * TIQ / 60}
med["extensao_aura_x_min_max_y_min"] = [int(min(u[1].min() for u in uni)), int(max(u[1].max() for u in uni)), int(min(u[0].min() for u in uni))]
print("EXTENSAO", med["extensao_aura_x_min_max_y_min"])
for nome, lst in (("asas", asas), ("asas_sem_fogo", asas_sem_fogo), ("coroa", coroas), ("chao", chaos), ("particulas", parts)):
    n = len(lst); difs = []; mud = []; iguais = 0
    for f in range(n):
        a, b = lst[f], lst[(f + 1) % n]
        uniao = (a >= 0) | (b >= 0)
        difs.append(float(np.abs(rgba(a).astype(int) - rgba(b).astype(int)).mean()))
        mud.append(float(((a != b) & uniao).sum() / max(uniao.sum(), 1))); iguais += int((a == b).all())
    pilha = np.stack(lst); sempre = (pilha >= 0).all(0); parado = sempre & (pilha == pilha[0]).all(0)
    cores = [int(len(np.unique(l[l >= 0]))) for l in lst]
    med[nome] = dict(quadros=n, emenda=round(difs[-1], 3), dif_min=round(min(difs), 3), dif_max=round(max(difs), 3),
                     vizinhos_da_emenda=[round(difs[-2], 3), round(difs[0], 3)],
                     frac_pixels_mudam_min=round(min(mud), 3), frac_pixels_mudam_max=round(max(mud), 3),
                     pares_consecutivos_iguais=iguais, pixels_que_nunca_mudam=int(parado.sum()), pixels_opacos_quadro0=int((lst[0] >= 0).sum()),
                     cores_min=min(cores), cores_max=max(cores))
tot_cores = [int(len(np.unique(np.concatenate([l[f % len(l)][l[f % len(l)] >= 0] for _, l in CAM])))) for f in range(NPART)]
med["cores_todas_as_camadas_por_quadro"] = [min(tot_cores), max(tot_cores)]
dn = [float(np.abs(NOVOS[f].astype(int) - NOVOS[(f + 1) % NPART].astype(int)).mean()) for f in range(NPART)]
med["composto_dif_min_max_emenda"] = [round(min(dn), 3), round(max(dn), 3), round(dn[-1], 3)]
A0 = [a >= 0 for a in asas_sem_fogo]
larg = [int(np.where(a.any(0))[0].max() - np.where(a.any(0))[0].min() + 1) for a in A0]
alt = [int(np.where(a.any(1))[0].max() - np.where(a.any(1))[0].min() + 1) for a in A0]
hc = int(ys.max() - ys.min() + 1); wc = int(xs.max() - xs.min() + 1)
med["corpo_px"] = [wc, hc]; med["envergadura_px_min_max"] = [min(larg), max(larg)]; med["altura_asas_px_min_max"] = [min(alt), max(alt)]
med["envergadura_sobre_altura_do_corpo"] = [round(min(larg) / hc, 2), round(max(larg) / hc, 2)]
med["topo_das_asas_y_min"] = int(min(np.where(a.any(1))[0].min() for a in A0)); med["pe_y"] = 190
# contornos das asas em 4 fases: quanto da silhueta fica igual
sil = np.stack(A0); med["asas_pixels_sempre_opacos_frac"] = round(float(sil.all(0).sum() / sil.any(0).sum()), 3)
# metade interna: fração de pixels que mudam por quadro só na faixa junto ao corpo (x 130..230)
mi = []
for f in range(N):
    a, b = asas_sem_fogo[f][:, 130:230], asas_sem_fogo[(f + 1) % N][:, 130:230]; u = (a >= 0) | (b >= 0)
    mi.append(float(((a != b) & u).sum() / max(u.sum(), 1)))
med["asas_junto_ao_corpo_frac_pixels_mudam_min_max"] = [round(min(mi), 3), round(max(mi), 3)]
med["notas_vivas_min_max"] = [min(viv), max(viv)]; med["gotas"] = len(GOTAS); med["fagulhas"] = len(fag)
med["azul_acima_do_verde_px"] = int(sum(((rgba(l[f])[..., 2].astype(int) > rgba(l[f])[..., 1]) & (l[f] >= 0)).sum() for _, l in CAM for f in range(len(l))))
med["tempo_render_blender_s"] = round(PT["tempo_render"], 1)
try: med["chicote"] = json.load(open("chicote.json"))
except OSError: pass
json.dump(med, open("medidas.json", "w"), indent=1)
print(json.dumps({k: v for k, v in med.items() if k != "chicote"}))

# ---------- tiras
X0 = 20; LW = 320
fnt = ImageFont.load_default()


def tira(quadros, arq, cols=4, esc=2):
    lin = (len(quadros) + cols - 1) // cols
    t = Image.new("RGB", (LW * cols, CH * lin))
    for k, f in enumerate(quadros):
        t.paste(Image.fromarray(NOVOS[f][:, X0:X0 + LW]), ((k % cols) * LW, (k // cols) * CH))
    t = t.resize((t.width * esc, t.height * esc), Image.NEAREST); d = ImageDraw.Draw(t)
    for k, f in enumerate(quadros): d.text(((k % cols) * LW * esc + 6, (k // cols) * CH * esc + 4), f"q{f:02d}", font=fnt, fill=(200, 200, 210))
    t.save(arq)


tira(list(range(0, N, 3)), "tira.png")                    # a batida inteira: 16 quadros, de 3 em 3
tira(list(range(0, 8)), "tira_consecutivos.png")          # 8 quadros seguidos (para julgar a fervura)
Image.fromarray(np.hstack([NOVOS[k][15:195, 20:190] for k in range(0, 6)])).resize((170 * 6 * 2, 360), Image.NEAREST).save("tira_zoom_esq.png")
Image.fromarray(np.hstack([NOVOS[k][0:200, 110:250] for k in (0, 12, 24, 36)])).resize((140 * 4 * 3, 600), Image.NEAREST).save("tira_zoom_meio.png")
sem = [quadro_novo(f, com_corpo=False) for f in (0, 24)]
Image.fromarray(np.hstack([s[40:195, 90:270] for s in sem])).resize((180 * 2 * 3, 155 * 3), Image.NEAREST).save("tira_sem_corpo.png")


# ---------- vídeos
def fonte(t):
    for n in ("arialbd.ttf", "arial.ttf"):
        try: return ImageFont.truetype(n, t)
        except OSError: pass
    return ImageFont.load_default()


def painel(q, titulo, sub, cor=(255, 214, 90)):
    p = Image.new("RGB", (640, 720), (18, 18, 24))
    p.paste(Image.fromarray(q[:, X0:X0 + LW]).resize((640, 400), Image.NEAREST), (0, 150))
    d = ImageDraw.Draw(p)
    d.text((320, 60), titulo, font=fonte(30), fill=cor, anchor="mm")
    for i, lin in enumerate(sub): d.text((320, 585 + i * 28), lin, font=fonte(17), fill=(210, 210, 220), anchor="mm")
    return p


def grava(arq, w, h, gera, total=600):
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", "60", "-i", "-",
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "14", "-preset", "medium", arq], stdin=subprocess.PIPE)
    cache = {}
    for t in range(total):
        k = gera(t, None)
        if k not in cache: cache[k] = gera(t, k)
        ff.stdin.write(cache[k])
    ff.stdin.close(); ff.wait()


PE = {i: painel(VELHOS[i], "DESENHO PARADO (só referência)",
                ["o conceito aprovado, parado, pulsando 3% de escala",
                 "NÃO é a folha de 8 quadros do ChatGPT: ela ainda não existe.",
                 "Este vídeo não compara Blender com ChatGPT."], cor=(200, 200, 210)) for i in range(8)}
PD = {f: painel(NOVOS[f], "BLENDER",
                [f"o mesmo desenho com ossos: {N} quadros, {TIQ} tiques cada ({N * TIQ / 60:.1f} s por batida)",
                 "notas, gotas, coroa, fogo na borda e brasa em camadas",
                 "ossos de ouro reforçados por cima do desenho"]) for f in range(NPART)}


def comp(t, k):
    key = ((t // 6) % 8, (t // TIQ) % NPART)
    if k is None: return key
    o = Image.new("RGB", (1280, 720)); o.paste(PE[key[0]], (0, 0)); o.paste(PD[key[1]], (640, 0))
    ImageDraw.Draw(o).line([(640, 0), (640, 720)], fill=(70, 70, 80), width=2)
    return o.tobytes()


def solo(t, k):
    key = (t // TIQ) % NPART
    if k is None: return key
    return Image.fromarray(NOVOS[key]).resize((CW * 3, CH * 3), Image.NEAREST).tobytes()


grava("asa_comparacao.mp4", 1280, 720, comp)
grava("asa_blender.mp4", CW * 3, CH * 3, solo)
print("OK")
