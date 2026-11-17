"""Peças comuns das auras feitas pelo Blender (docs/arcade/aura_blender.md).

O desenho do conceito aprovado vira textura de uma malha com ossos; o Blender só entorta. Fogo, fumaça, gotas e
partículas entram por cima como camadas em laço. Saída: camadas PNG do tamanho do jogo, alfa 0/255, paleta fixa.

Este arquivo é importado dos DOIS lados:
  - pelo Python comum (numpy, cv2, scipy, PIL): recortes, redução, paleta, fogo, partículas, medidas, vídeo;
  - pelo Python do Blender (só numpy + bpy): tudo que começa com `bl_`, mais `grade_de_malha` e `pesos_por_osso`.
Por isso cv2/scipy/PIL são opcionais na importação e bpy só é importado dentro das funções `bl_`.

Convenções:
  - "conceito" = pixels da folha de conceito (grande); "jogo" = pixels da tela 360x200; "4x" = jogo ampliado AMP vezes.
  - máscara = array bool (H, W); rgb = uint8 (H, W, 3); idx = int16 (H, W) com índice da paleta e -1 = transparente.
  - um "quadro reduzido" é o par (rgb float32, máscara) que sai de `reduz`.
  - todo laço é função periódica do número do quadro: nada de aleatório por quadro.
"""
import json, math, os, subprocess, sys, time
import numpy as np

try:
    import cv2
except ImportError:          # dentro do Blender
    cv2 = None
try:
    from scipy import ndimage as ndi
except ImportError:
    ndi = None
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = ImageDraw = ImageFont = None

BLENDER = os.environ.get("BLENDER", "C:/Dev/Tools/Blender/blender-4.5.15-windows-x64/blender.exe")
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # raiz do repositório


# =====================================================================================================================
# 1. Tela: a ponte entre o conceito, o Blender e o jogo
# =====================================================================================================================
class Tela:
    """Geometria de uma aura.

    cx, chao : no conceito, o x do eixo do lutador e o y do chão (sola do pé) na vista que tem a aura.
    escala   : px do jogo por px do conceito (altura do corpo no jogo / altura do corpo no conceito).
    cw, ch   : tela do jogo (360x200). amp: ampliação do render (4). pe: onde o pé do lutador cai na tela (180,190).
    No Blender, 1 unidade = 1 px do jogo, X para a direita, Z para cima, origem no pé.
    """

    def __init__(self, cx, chao, escala, cw=360, ch=200, amp=4, pe=(180, 190)):
        self.cx, self.chao, self.escala = float(cx), float(chao), float(escala)
        self.cw, self.ch, self.amp, self.pe = int(cw), int(ch), int(amp), (pe[0], pe[1])

    def g(self, x, y):
        """conceito (x, y) -> Blender (X, Z)."""
        return ((x - self.cx) * self.escala, (self.chao - y) * self.escala)

    def jogo(self, X, Z):
        """Blender (X, Z) -> pixel do jogo (x, y)."""
        return (self.pe[0] + X, self.pe[1] - Z)

    def conceito_para_jogo(self, x, y):
        return self.jogo(*self.g(x, y))

    def grade(self):
        """(YY, XX) da tela do jogo."""
        return np.mgrid[0:self.ch, 0:self.cw]


# =====================================================================================================================
# 2. Recortes do conceito (resolução do conceito)
# =====================================================================================================================
def le_rgb(arq):
    return np.array(Image.open(arq).convert("RGB"))


def canais(rgb):
    """R, G, B como int (para fazer conta sem estourar uint8)."""
    I = rgb.astype(int)
    return I[..., 0], I[..., 1], I[..., 2]


def chave_magenta(rgb, r_min=170, b_min=170, g_max=110):
    """Máscara do desenho: tudo que NÃO é o fundo magenta (R e B altos, G baixo)."""
    R, G, B = canais(rgb)
    return ~((R > r_min) & (B > b_min) & (G < g_max))


def derrame_quente(rgb, folga=25, folga2=-20, b_min=120):
    """Derrame de magenta numa aura QUENTE (ouro, fogo, brasa): ali nenhum pixel legítimo tem azul acima do verde.
    Devolve a máscara do que é derrame. Não serve para aura fria (gelo, raio azul, roxo): use `derrame_de_borda`."""
    R, G, B = canais(rgb)
    return (B > G + folga) | ((B > G + folga2) & (B > b_min))


def tira_azul_acima_do_verde(rgb):
    """Cópia do rgb com B limitado a G: apaga o resto rosado das bordas de uma aura quente."""
    o = rgb.copy(); o[..., 2] = np.minimum(o[..., 2], o[..., 1])
    return o


def derrame_de_borda(mask, rgb, largura=3, dif=60, b_min=120):
    """Derrame de magenta só na casca de `largura` px da máscara (pixel rosado: R e B bem acima do G).
    Serve para qualquer cor de miolo, porque só olha a borda."""
    R, G, B = canais(rgb)
    borda = mask & ~ndi.binary_erosion(mask, iterations=largura)
    return borda & ((R - G) > dif) & ((B - G) > dif) & (B > b_min)


def maior_componente(mask, conect=4):
    st = np.ones((3, 3)) if conect == 8 else None
    lab, n = ndi.label(mask, structure=st)
    if n == 0:
        return np.zeros_like(mask)
    sz = ndi.sum(mask, lab, range(1, n + 1))
    return lab == (1 + int(np.argmax(sz)))


def componentes(mask, conect=8):
    """(lab, lista) com um dict por componente: i (rótulo), area, x0, y0, x1, y1 (x1/y1 exclusivos)."""
    st = np.ones((3, 3)) if conect == 8 else None
    lab, n = ndi.label(mask, structure=st)
    sz = ndi.sum(mask, lab, range(1, n + 1)) if n else []
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), start=1):
        out.append(dict(i=i, area=int(sz[i - 1]), x0=int(sl[1].start), y0=int(sl[0].start), x1=int(sl[1].stop), y1=int(sl[0].stop)))
    return lab, out


def separa_soltos(mask, area_min=120, area_frag=500, lado_frag=20, conect=8):
    """Separa a peça principal dos pedaços soltos em volta.
    Pedaço grande e gordo (área >= area_frag e menor lado >= lado_frag) é FRAGMENTO: fica na peça e mexe com ela.
    Pedaço fino é GOTA: sai do recorte e vira partícula desenhada em 1x. Menor que area_min é lixo.
    Devolve (peça com os fragmentos, lista de fragmentos, lista de gotas); cada item é dict(x0, y0, x1, y1, area)."""
    lab, comps = componentes(mask, conect)
    if not comps:
        return np.zeros_like(mask), [], []
    k = max(comps, key=lambda c: c["area"])["i"]
    peca = lab == k; frag = []; gotas = []
    for c in comps:
        if c["i"] == k or c["area"] < area_min:
            continue
        d = {q: c[q] for q in ("x0", "y0", "x1", "y1", "area")}
        if c["area"] >= area_frag and min(c["x1"] - c["x0"], c["y1"] - c["y0"]) >= lado_frag:
            frag.append(d); peca |= lab == c["i"]
        else:
            gotas.append(d)
    return peca, frag, gotas


def recorta_corpo(fg, rgb, x0, x1):
    """Máscara do corpo numa vista SEM aura (colunas x0..x1 do conceito): maior peça, sem furos, sem a casca rosada."""
    corpo = np.zeros(fg.shape, bool); corpo[:, x0:x1] = fg[:, x0:x1]
    corpo = ndi.binary_opening(corpo, iterations=1)
    corpo = maior_componente(corpo)
    corpo = ndi.binary_fill_holes(corpo) & fg
    corpo = ndi.binary_erosion(corpo, iterations=1)
    return corpo & ~derrame_de_borda(corpo, rgb)


def casa_corpo(rgb, corpo, x_min, x_max, dy_max=12):
    """Acha onde o corpo (máscara de uma vista sem aura) reaparece na vista COM aura, para poder tirá-lo de lá.
    Procura o deslocamento (dx, dy) com dx tal que o corpo caia entre as colunas x_min..x_max.
    Casa por cor (correlação normalizada com máscara). Devolve (dx, dy, nota 0..1). Confira a nota e olhe a prévia:
    se a pose do corpo mudar entre as vistas (braço, capa), o casamento é só aproximado e a sobra tem de ser dilatada."""
    ys, xs = np.where(corpo); bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    molde = rgb[by0:by1, bx0:bx1]; mm = (corpo[by0:by1, bx0:bx1] * 255).astype(np.uint8)
    H, W = corpo.shape
    ya, yb = max(0, by0 - dy_max), min(H, by1 + dy_max)
    xa, xb = max(0, x_min), min(W, x_max)
    busca = rgb[ya:yb, xa:xb]
    r = cv2.matchTemplate(busca, molde, cv2.TM_CCORR_NORMED, mask=np.dstack([mm] * 3))
    r[~np.isfinite(r)] = 0
    _, nota, _, (px, py) = cv2.minMaxLoc(r)
    return int(xa + px - bx0), int(ya + py - by0), float(nota)


def desloca(mask, dx, dy=0):
    """Máscara deslocada (dx, dy), sem dar a volta."""
    H, W = mask.shape; o = np.zeros_like(mask)
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    o[yd, xd] = mask[ys, xs]
    return o


def discos(shape, pts, n=40):
    """Máscara de um tubo: polilinha [(x, y, raio), ...] carimbada com discos. Para tocos, remendos, ossos."""
    m = np.zeros(shape, np.uint8)
    for (x0, y0, r0), (x1, y1, r1) in zip(pts, pts[1:]):
        for t in np.linspace(0, 1, n):
            cv2.circle(m, (int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t)), int(r0 + (r1 - r0) * t), 1, -1)
    return m > 0


def remenda_clone(rgb, fonte_rgb, fonte_mask, alvo, passo, vezes=3):
    """Pinta `alvo` clonando o próprio desenho: cada pixel copia o que está a k*passo=(dy, dx) dali, k=1..vezes,
    enquanto a fonte cair dentro de `fonte_mask`. Mexe em `rgb` e devolve a máscara do que ficou sem fonte."""
    H, W = alvo.shape; yy, xx = np.where(alvo)
    for k in range(1, vezes + 1):
        if len(yy) == 0:
            break
        sy = yy + passo[0] * k; sx = xx + passo[1] * k
        ok = (sy >= 0) & (sy < H) & (sx >= 0) & (sx < W); ok[ok] &= fonte_mask[sy[ok], sx[ok]]
        rgb[yy[ok], xx[ok]] = fonte_rgb[sy[ok], sx[ok]]
        yy, xx = yy[~ok], xx[~ok]
    falta = np.zeros_like(alvo); falta[yy, xx] = True
    return falta


def remenda_vizinho(rgb, validos, alvo):
    """Pinta `alvo` com a cor do pixel válido mais próximo. Mexe em `rgb`."""
    idx = ndi.distance_transform_edt(~validos, return_distances=False, return_indices=True)
    rgb[alvo] = rgb[idx[0], idx[1]][alvo]


def espelha_faixa(rgb_dst, rgb_src, mask, x0, x1, y0):
    """Fecha um buraco vertical (colunas x0..x1, linhas y0 para baixo) espelhando para dentro a faixa de cada lado.
    Para o chão de brasa/água onde os pés do lutador abriam um vão. Mexe em rgb_dst e na máscara."""
    meio = (x0 + x1) // 2; m0 = mask.copy()
    for x in range(x0, x1):
        src = x0 - 1 - (x - x0) if x < meio else x1 + (x1 - 1 - x)
        rgb_dst[y0:, x] = rgb_src[y0:, src]; mask[y0:, x] = m0[y0:, src]


def reforca_linhas(rgb, mask, linhas, camadas, nos=(), amp=4, dil=2):
    """Redesenha por cima do recorte os traços finos que sumiriam na redução para 1/4 (ossos, varetas, correntes).
    linhas : [[(x, y, largura), ...], ...] em px do conceito.
    camadas: [(cor, quanto a largura encolhe, desvio vertical em fração da largura), ...] da mais escura à mais clara.
    nos    : [(x, y, [(cor, raio, dy), ...]), ...] bolas nas juntas.
    Desenha em amp x e reduz (borda limpa). Mexe em rgb e mask; devolve a máscara do que foi reforçado."""
    H, W = mask.shape
    big = np.ascontiguousarray(cv2.resize(rgb, (W * amp, H * amp), interpolation=cv2.INTER_NEAREST)); g0 = big.copy()
    for cor, dl, dv in camadas:
        for pts in linhas:
            for (x0, y0, w0), (x1, y1, w1) in zip(pts, pts[1:]):
                for t in np.linspace(0, 1, 16):
                    wb = w0 + (w1 - w0) * t; w = wb + dl
                    if w < 1.2:
                        continue
                    cv2.circle(big, (int(round((x0 + (x1 - x0) * t) * amp)), int(round((y0 + (y1 - y0) * t + dv * wb) * amp))),
                               int(round(w * amp / 2)), cor, -1)
    for x, y, bolas in nos:
        for cor, r, dy in bolas:
            cv2.circle(big, (int(x * amp), int((y + dy) * amp)), int(r * amp), cor, -1)
    mud = (big != g0).any(-1)
    osso = cv2.resize(mud.astype(np.uint8) * 255, (W, H), interpolation=cv2.INTER_AREA) > 127
    osso_rgb = cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA)
    osso &= ndi.binary_dilation(mask, iterations=dil)
    rgb[osso] = osso_rgb[osso]; mask |= osso
    return osso


def salva_rgba(arq, rgb, mask):
    """PNG com alfa 0/255; o que está fora da máscara sai zerado."""
    o = np.dstack([rgb, (mask * 255).astype(np.uint8)]); o[~mask] = 0
    Image.fromarray(o).save(arq)


def caixa(mask):
    """[x0, y0, x1, y1] da máscara (x1/y1 exclusivos)."""
    ys, xs = np.where(mask)
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def previa_recortes(arqs, arq_saida, box, shape, cinza=70):
    """Cola os recortes (mesma resolução do conceito) num fundo cinza e salva o pedaço `box` para olhar."""
    H, W = shape; c = np.full((H, W, 3), cinza, np.uint8)
    for a in arqs:
        im = np.array(Image.open(a).convert("RGBA")); m = im[..., 3] > 0; c[m] = im[..., :3][m]
    Image.fromarray(c[box[1]:box[3], box[0]:box[2]]).save(arq_saida)


# =====================================================================================================================
# 3. Malha e pesos (numpy puro: roda dentro e fora do Blender)
# =====================================================================================================================
def grade_de_malha(A, celula=8, margem=8):
    """Malha em grade só onde a máscara A (alfa do recorte, linha 0 em cima) tem desenho.
    Devolve (verts, faces): verts = [(ix, iy), ...] em px do recorte; faces = quádruplas de índices."""
    ys, xs = np.where(A)
    x0, x1, y0, y1 = xs.min() - margem, xs.max() + margem + 1, ys.min() - margem, ys.max() + margem + 1
    C = celula; ind = {}; faces = []

    def v(ix, iy):
        k = (int(ix), int(iy))
        if k not in ind:
            ind[k] = len(ind)
        return ind[k]
    for iy in range(y0, y1, C):
        for ix in range(x0, x1, C):
            if A[max(iy, 0):max(iy + C, 0), max(ix, 0):max(ix + C, 0)].any():
                faces.append((v(ix, iy + C), v(ix + C, iy + C), v(ix + C, iy), v(ix, iy)))
    return list(ind.keys()), faces


def dist_segmentos(pts, segs):
    """Distância de cada ponto (n, 2) a cada segmento [(a, b), ...]: matriz (n, m)."""
    P = np.asarray(pts, float); D = np.empty((len(P), len(segs)))
    for j, (a, b) in enumerate(segs):
        a = np.asarray(a, float); b = np.asarray(b, float); ab = b - a
        t = np.clip(((P - a) @ ab) / max(float(ab @ ab), 1e-9), 0.0, 1.0)
        D[:, j] = np.hypot(*(P - (a + t[:, None] * ab)).T)
    return D


def pesos_por_osso(pts, segs, k=4, folga=1.5, pot=3):
    """Peso de cada vértice nos k ossos mais próximos: 1 / (distância + folga) ** pot, normalizado.
    pts: (n, 2); segs: [(cabeça, cauda), ...] no mesmo sistema. Devolve (W (n, m) com zeros fora dos k, dmin (n,)).
    Folga maior ou potência menor = pano mais mole (membrana); potência maior = cada pedaço segue um osso só (placa)."""
    D = dist_segmentos(pts, segs); n, m = D.shape; k = min(k, m)
    ordem = np.argsort(D, axis=1, kind="stable")[:, :k]
    W = np.zeros((n, m)); lin = np.arange(n)[:, None]
    w = 1.0 / (D[lin, ordem] + folga) ** pot
    W[lin, ordem] = w / w.sum(1, keepdims=True)
    return W, D.min(1)


# =====================================================================================================================
# 4. Blender (bl_*): cena, material, malha com ossos, animação, render
# =====================================================================================================================
def onda_batida(f, n, h2=0.18, fase2=0.6):
    """Onda de período n com um pouco de 2º harmônico: sobe devagar, respira, desce um pouco mais rápido."""
    t = 2 * math.pi * f / n
    return math.sin(t) + h2 * math.sin(2 * t + fase2)


def bl_cena(tela, n):
    """Cena vazia: Cycles 1 amostra, sem filtro, fundo transparente, câmera ortográfica de frente, quadros 0..n-1."""
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cena = bpy.context.scene
    cena.render.engine = "CYCLES"; cena.cycles.device = "CPU"; cena.cycles.samples = 1
    cena.cycles.use_adaptive_sampling = False; cena.cycles.use_denoising = False
    cena.cycles.pixel_filter_type = "BOX"; cena.cycles.filter_width = 0.01
    cena.cycles.transparent_max_bounces = 32
    cena.render.film_transparent = True
    cena.render.resolution_x = tela.cw * tela.amp; cena.render.resolution_y = tela.ch * tela.amp
    cena.render.resolution_percentage = 100
    cena.render.image_settings.file_format = "PNG"; cena.render.image_settings.color_mode = "RGBA"
    cena.view_settings.view_transform = "Standard"; cena.view_settings.look = "None"
    cena.render.dither_intensity = 0
    cena.frame_start = 0; cena.frame_end = n - 1
    cam = bpy.data.cameras.new("cam"); cam.type = "ORTHO"; cam.ortho_scale = tela.cw
    co = bpy.data.objects.new("cam", cam); cena.collection.objects.link(co); cena.camera = co
    co.location = (tela.cw / 2 - tela.pe[0], -200, tela.pe[1] - tela.ch / 2); co.rotation_euler = (math.pi / 2, 0, 0)
    cam.clip_start = 1; cam.clip_end = 1000
    return cena


def bl_material(nome, arq):
    """Material que só emite a textura (sem luz), interpolação Closest, alfa cortado em 0,5. Devolve (material, imagem)."""
    import bpy
    img = bpy.data.images.load(arq); img.alpha_mode = "STRAIGHT"
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img; t.interpolation = "Closest"; t.extension = "CLIP"
    e = nt.nodes.new("ShaderNodeEmission"); tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader"); o = nt.nodes.new("ShaderNodeOutputMaterial")
    gt = nt.nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.5
    nt.links.new(t.outputs["Color"], e.inputs["Color"]); nt.links.new(t.outputs["Alpha"], gt.inputs[0])
    nt.links.new(gt.outputs[0], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(e.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], o.inputs["Surface"])
    return m, img


def bl_alfa(img):
    """Máscara (linha 0 em cima) do alfa de uma imagem carregada no Blender."""
    W, H = img.size
    return np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)[::-1, :, 3] > 0.5


def bl_vazio_em_laco(nome, n, raio, fase=0.0):
    """Vazio que anda em círculo no plano Y-Z: ruído amostrado nele fecha o laço em n quadros."""
    import bpy
    e = bpy.data.objects.new(nome, None); bpy.context.scene.collection.objects.link(e)
    for f in range(n + 1):
        t = 2 * math.pi * f / n + fase
        e.location = (0, raio * math.cos(t), raio * math.sin(t)); e.keyframe_insert("location", frame=f)
    return e


def bl_textura_ruido(nome="tremor", escala=26.0, profundidade=1):
    import bpy
    tex = bpy.data.textures.get(nome)
    if tex is None:
        tex = bpy.data.textures.new(nome, "CLOUDS"); tex.noise_scale = escala; tex.noise_depth = profundidade
    return tex


def bl_malha_com_ossos(nome, arq, ossos, tela, n, celula=8, margem=8, k=4, folga=1.5, pot=3, prof=None,
                       tremor=(), tremor_folga=1.5, tremor_rampa=9.0, textura=None):
    """Recorte -> malha em grade com ossos, já FILHA da armação (o modificador de armação sozinho ignora mover ou
    escalar o objeto armação: sem o parentesco a peça vira placa solta).

    nome  : sufixo dos objetos (arm_<nome>, malha_<nome>).
    arq   : PNG do recorte na resolução do conceito (o que está fora do alfa não ganha malha).
    ossos : [(nome, pai ou None, cabeça (x, y), cauda (x, y)), ...] em px do conceito; o primeiro é a raiz e a
            cabeça dele é a origem da armação (o "ombro": é ali que a peça gira e é isso que se anima como objeto).
    prof  : função (X, Z) -> Y (profundidade em unidades do Blender) para decidir quem cobre quem quando a malha
            dobra sobre si mesma; None = tudo no mesmo plano.
    tremor: [dict(eixo="X"|"Z", raio, fase, forca), ...] um Displace por item, com ruído Clouds amostrado num vazio
            em círculo (fecha o laço). O peso do tremor é 0 em cima do osso e sobe até 1 a `tremor_rampa` px dele:
            pena, pano e fumaça tremem, osso não.
    Devolve dict(arm, malha, origem=(ox, oz), nomes=[ossos], verts, faces).
    """
    import bpy
    cena = bpy.context.scene
    mat, img = bl_material("mat_" + nome, arq); W, H = img.size
    verts, faces = grade_de_malha(bl_alfa(img), celula, margem)
    ad = bpy.data.armatures.new("arm_" + nome); ao = bpy.data.objects.new("arm_" + nome, ad)
    cena.collection.objects.link(ao)
    ox, oz = tela.g(*ossos[0][2])
    bpy.context.view_layer.objects.active = ao; bpy.ops.object.mode_set(mode="EDIT")
    for nm, pai, h, t in ossos:
        b = ad.edit_bones.new(nm); hx, hz = tela.g(*h); tx, tz = tela.g(*t)
        b.head = (hx - ox, 0, hz - oz); b.tail = (tx - ox, 0, tz - oz)
        if pai:
            b.parent = ad.edit_bones[pai]; b.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    XZ = np.array([tela.g(ix, iy) for ix, iy in verts])
    cov = [(X - ox, prof(X, Z) if prof else 0.0, Z - oz) for X, Z in XZ]     # coordenadas locais da raiz
    me = bpy.data.meshes.new("malha_" + nome); me.from_pydata(cov, [], faces); me.update()
    uvl = me.uv_layers.new(name="uv")
    for poly in me.polygons:
        for li in poly.loop_indices:
            ix, iy = verts[me.loops[li].vertex_index]; uvl.data[li].uv = (ix / W, 1 - iy / H)
    me.materials.append(mat)
    ob = bpy.data.objects.new("malha_" + nome, me); cena.collection.objects.link(ob)
    nomes = [o[0] for o in ossos]
    Wp, dmin = pesos_por_osso(XZ, [(tela.g(*h), tela.g(*t)) for _, _, h, t in ossos], k, folga, pot)
    grupos = [ob.vertex_groups.new(name=nm) for nm in nomes]
    gt = ob.vertex_groups.new(name="tremor")
    for i in range(len(verts)):
        for j in np.nonzero(Wp[i])[0]:
            grupos[j].add([i], float(Wp[i, j]), "REPLACE")
        gt.add([i], float(min(1.0, max(0.0, (dmin[i] - tremor_folga) / tremor_rampa))), "REPLACE")
    tex = textura or bl_textura_ruido()
    for tr in tremor:        # o Displace vem ANTES da armação na pilha: treme na pose do desenho e depois dobra
        md = ob.modifiers.new("tremor" + tr["eixo"], "DISPLACE"); md.texture = tex; md.direction = tr["eixo"]; md.space = "LOCAL"
        md.mid_level = 0.5; md.strength = tr["forca"]; md.vertex_group = "tremor"
        md.texture_coords = "OBJECT"
        md.texture_coords_object = bl_vazio_em_laco(f"laco_{nome}_{tr['eixo']}", n, tr["raio"], tr.get("fase", 0.0))
    md = ob.modifiers.new("arm", "ARMATURE"); md.object = ao
    ob.parent = ao
    print("MALHA", nome, "verts", len(cov), "faces", len(faces))
    return dict(arm=ao, malha=ob, origem=(ox, oz), nomes=nomes, verts=len(cov), faces=len(faces))


def bl_anima_juntas(ao, anim, n, onda=onda_batida, fase=0.0, centro=0.0, sinal=1, harmonico=2):
    """Rotação de cada osso no plano da tela, em laço de n quadros.
    anim  : {osso: (amplitude em graus, atraso em fração do ciclo, amplitude do harmônico, fase do harmônico)}.
            Chicote/cascata: a raiz gira POUCO e CEDO; cada junta adiante gira MAIS e mais TARDE (atraso crescente).
    onda  : função (f, n) de período n. centro: desloca a pose média (em "amplitudes"). fase: em quadros (defasar
            peças gêmeas). sinal: -1 para a peça espelhada. harmonico: múltiplo da ondulação (2 = duas por ciclo)."""
    from mathutils import Vector, Quaternion
    for nm, (amp, atr, amp2, f2) in anim.items():
        pb = ao.pose.bones[nm]; pb.rotation_mode = "QUATERNION"
        eixo = (ao.data.bones[nm].matrix_local.to_3x3().inverted() @ Vector((0, 1, 0))).normalized()
        for f in range(n + 1):
            t = f - fase - atr * n
            ang = amp * (onda(t, n) + centro) + amp2 * math.sin(2 * math.pi * harmonico * t / n + f2)
            pb.rotation_quaternion = Quaternion(eixo, math.radians(ang) * sinal)
            pb.keyframe_insert("rotation_quaternion", frame=f)


def bl_anima_objeto(ob, n, fn, fase=0.0):
    """Anima o objeto inteiro em laço: fn(t) com t = 2*pi*(f - fase)/n devolve {propriedade: valor}
    (location, scale, rotation_euler). Use só senos de múltiplos inteiros de t para o quadro n cair igual ao 0."""
    if "rotation_euler" in fn(0.0):
        ob.rotation_mode = "XYZ"
    for f in range(n + 1):
        for prop, val in fn(2 * math.pi * (f - fase) / n).items():
            setattr(ob, prop, val); ob.keyframe_insert(prop, frame=f)


def bl_placa(nome, arq, bbox, tela, margem=4):
    """Peça rígida (coroa, anel, selo): um retângulo com o recorte, origem no centro. bbox em px do conceito.
    Devolve (objeto, (X, Z) do centro). Dê vida com bl_anima_objeto (flutuar, balançar, girar em Z para encurtar)."""
    import bpy
    mat, img = bl_material("mat_" + nome, arq); W, H = img.size
    x0, y0, x1, y1 = bbox[0] - margem, bbox[1] - margem, bbox[2] + margem, bbox[3] + margem
    (xa, za), (xb, zb) = tela.g(x0, y1), tela.g(x1, y0)
    cx, cz = (xa + xb) / 2, (za + zb) / 2
    me = bpy.data.meshes.new(nome)
    me.from_pydata([(xa - cx, 0, za - cz), (xb - cx, 0, za - cz), (xb - cx, 0, zb - cz), (xa - cx, 0, zb - cz)], [], [(0, 1, 2, 3)])
    uvl = me.uv_layers.new(name="uv")
    for li, (x, y) in zip(range(4), [(x0, y1), (x1, y1), (x1, y0), (x0, y0)]):
        uvl.data[li].uv = (x / W, 1 - y / H)
    me.materials.append(mat); ob = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(ob)
    ob.location = (cx, 0, cz)
    return ob, (cx, cz)


def bl_lineariza():
    """Interpolação linear em todas as curvas: com uma chave por quadro, o quadro n é igual ao 0 e o laço fecha."""
    import bpy
    for o in list(bpy.data.objects):
        if o.animation_data and o.animation_data.action:
            for fc in o.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = "LINEAR"


def bl_pontas(peca, tela, prefixo):
    """Posição no jogo [x, y] da CAUDA de cada osso da peça no quadro atual: {prefixo_osso: [x, y]}.
    Mais {prefixo_raiz: [x, y]} com a cabeça do primeiro osso. É onde as partículas nascem e o que se mede."""
    ao = peca["arm"]; d = {}
    for nm in peca["nomes"]:
        w = ao.matrix_world @ ao.pose.bones[nm].tail; d[f"{prefixo}_{nm}"] = list(tela.jogo(w.x, w.z))
    w = ao.matrix_world @ ao.pose.bones[peca["nomes"][0]].head; d[f"{prefixo}_raiz"] = list(tela.jogo(w.x, w.z))
    return d


def bl_renderiza(pasta, n, passadas, coleta, so_pontos=False, extra=None, blend=None):
    """Renderiza cada passada (nome -> lista de objetos visíveis) em pasta/render/<nome>_NN.png e grava
    pasta/render/pontos.json = {pontos: [coleta(f) por quadro], N, tempo_render, **extra}.
    so_pontos=True pula o render (1 s): serve para afinar o movimento medindo só as pontas."""
    import bpy
    cena = bpy.context.scene
    bl_lineariza()
    os.makedirs(os.path.join(pasta, "render"), exist_ok=True)
    if blend and not so_pontos:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(pasta, blend))
    todos = [o for objs in passadas.values() for o in objs]
    pontos = []; t0 = time.time()
    for f in range(n):
        cena.frame_set(f); bpy.context.view_layer.update()
        pontos.append(coleta(f))
        if so_pontos:
            continue
        for nome, objs in passadas.items():
            for o in todos:
                o.hide_render = o not in objs
            cena.render.filepath = os.path.join(pasta, "render", f"{nome}_{f:02d}.png")
            bpy.ops.render.render(write_still=True)
    d = dict(pontos=pontos, N=n, tempo_render=time.time() - t0); d.update(extra or {})
    json.dump(d, open(os.path.join(pasta, "render", "pontos.json"), "w"))
    print("TEMPO_RENDER", d["tempo_render"])
    return pontos


# =====================================================================================================================
# 5. Do render para o jogo: redução, paleta fixa, histerese
# =====================================================================================================================
def reduz(rgba4, amp=4):
    """amp x -> 1x: cor = média só dos subpixels opacos; alfa por maioria. Devolve (rgb float32, máscara)."""
    a = rgba4[..., 3].astype(np.float32) / 255.0
    h, w = a.shape[0] // amp, a.shape[1] // amp
    a4 = a.reshape(h, amp, w, amp)
    cob = a4.mean((1, 3))
    rgb = (rgba4[..., :3].astype(np.float32) * a[..., None]).reshape(h, amp, w, amp, 3).sum((1, 3))
    rgb /= np.maximum(a4.sum((1, 3)), 1e-6)[..., None]
    return rgb, cob >= 0.5


def le_render(arq, amp=4):
    """Quadro do Blender (RGBA amp x) já reduzido."""
    return reduz(np.array(Image.open(arq).convert("RGBA")), amp)


def conceito_para_4x(arq, tela, dx=0.0):
    """Leva um recorte na resolução do conceito para o quadro amp x do jogo (vizinho mais próximo), parado.
    dx: quanto o recorte está à esquerda da vista com aura (ex.: o corpo recortado de outra vista)."""
    im = cv2.imread(arq, cv2.IMREAD_UNCHANGED)[..., [2, 1, 0, 3]]
    k = tela.escala * tela.amp
    M = np.array([[k, 0, tela.pe[0] * tela.amp - (tela.cx - dx) * k], [0, k, tela.pe[1] * tela.amp - tela.chao * k]], np.float32)
    return cv2.warpAffine(im, M, (tela.cw * tela.amp, tela.ch * tela.amp), flags=cv2.INTER_NEAREST,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=0)


class Paleta:
    """Paleta fixa da aura, da cor mais escura (índice 0 = contorno) à mais clara (último índice)."""

    def __init__(self, cores, peso=(2, 4, 1)):
        c = np.asarray(cores).astype(np.uint8)
        self.cores = c[np.argsort(c.astype(int) @ np.array([299, 587, 114]), kind="stable")]
        self.f = self.cores.astype(np.float32); self.peso = np.array(peso, np.float32)
        self.n = len(self.cores); self.escura = 0; self.clara = self.n - 1

    @classmethod
    def do_desenho(cls, amostras, n=14, escura=(52, 14, 10), semente=3):
        """n cores tiradas do próprio desenho (k-médias sobre `amostras`, array (N, 3)) + 1 escura de contorno.
        A escura é a cor do contorno dos lutadores puxada para o tom da aura; total n + 1 (15 no jogo)."""
        crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        cv2.setRNGSeed(semente)
        _, _, cent = cv2.kmeans(np.asarray(amostras, np.float32), n, None, crit, 8, cv2.KMEANS_PP_CENTERS)
        return cls(np.vstack([np.clip(np.round(cent), 0, 255), [list(escura)]]))

    @classmethod
    def de_recortes(cls, arqs, tela, **kw):
        """Paleta tirada dos recortes já reduzidos para o tamanho do jogo (as cores que de fato vão aparecer)."""
        partes = [reduz(conceito_para_4x(a, tela), tela.amp) for a in arqs]
        return cls.do_desenho(np.concatenate([r[m] for r, m in partes]), **kw)

    def dist(self, rgb):
        return ((rgb[..., None, :] - self.f[None, None]) ** 2 * self.peso).sum(-1)

    def encaixa(self, rgb, m):
        """Um quadro reduzido -> idx (-1 = transparente). Para coisa parada ou carimbo; em sequência use encaixa_seq."""
        idx = self.dist(rgb).argmin(-1).astype(np.int16); idx[~m] = -1
        return idx

    def encaixa_seq(self, quadros, folga=420.0):
        """Encaixe com histerese numa sequência em laço de quadros reduzidos: se a cor que o pixel tinha no quadro
        anterior ainda serve quase tão bem (distância até `folga` acima da melhor), ele fica com ela. Tira a fervura
        do miolo quando a malha desliza meio pixel. Duas voltas para o último quadro emendar no primeiro.
        folga 0 = sem histerese; folga alta demais borra o movimento (a cor gruda na tela em vez de andar com a peça)."""
        ant = None; out = []
        for _ in range(2):
            out = []
            for rgb, m in quadros:
                d = self.dist(rgb); best = d.argmin(-1).astype(np.int16)
                if ant is not None:
                    ok = (ant >= 0) & m
                    da = np.take_along_axis(d, np.clip(ant, 0, None)[..., None].astype(np.int64), -1)[..., 0]
                    fica = ok & (da <= d.min(-1) + folga)
                    best[fica] = ant[fica]
                best[~m] = -1; ant = best; out.append(best)
        return out

    def rgba(self, idx):
        o = np.zeros(idx.shape + (4,), np.uint8); m = idx >= 0
        o[m, :3] = self.cores[idx[m]]; o[m, 3] = 255
        return o

    def mais_proxima(self, cor):
        return int(self.dist(np.array(cor, np.float32)[None, None])[0, 0].argmin())

    def rampa_quente(self):
        """Índices para fogo/ouro: dict(claro, amar, lar, verm, esc) + rampa (do miolo claro à ponta vermelha).
        Para aura fria monte a rampa à mão com `mais_proxima`."""
        P = self.cores; sat = P.max(1).astype(int) - P.min(1); r = range(self.n)
        amar = max((i for i in r if P[i][0] > 230 and P[i][1] > 170), key=lambda i: sat[i], default=self.clara)
        lar = max((i for i in r if P[i][0] > 200 and 90 < P[i][1] < 170), key=lambda i: sat[i], default=self.n // 2 + 1)
        verm = max((i for i in r if 120 < P[i][0] and P[i][1] < 95), key=lambda i: int(P[i][0]), default=self.n // 4 + 1)
        c = self.clara
        return dict(claro=c, amar=amar, lar=lar, verm=verm, esc=self.escura,
                    rampa=[c, c, amar, amar, lar, lar, verm, verm, verm])

    def lista(self):
        return self.cores.tolist()


def contorno(idx, cor=0, poupa_cima=True):
    """Contorno escuro (como o dos lutadores) na borda de baixo e dos lados; a borda de cima fica livre para o
    fogo/fumaça subir (poupa_cima=False contorna tudo). Não contorna pixel solto (precisa de vizinhança)."""
    m = idx >= 0
    dentro = ndi.binary_erosion(m, structure=ndi.generate_binary_structure(2, 1), border_value=0)
    cima_vazio = np.ones_like(m); cima_vazio[1:] = ~m[:-1]
    viz = ndi.uniform_filter(m.astype(np.float32), 3) * 9
    b = m & ~dentro & (viz >= 4.5)
    if poupa_cima:
        b &= ~cima_vazio
    out = idx.copy(); out[b] = cor
    return out


def limpa(idx, minimo=6):
    """Apaga ilhas com menos de `minimo` pixels (farelo do render). Mexe em idx e devolve."""
    lab, n = ndi.label(idx >= 0, structure=np.ones((3, 3)))
    if n:
        sz = ndi.sum(idx >= 0, lab, range(1, n + 1))
        for i in np.where(sz < minimo)[0]:
            idx[lab == i + 1] = -1
    return idx


# =====================================================================================================================
# 6. Camadas procedurais em laço: ruído ladrilhável, fogo, cintilação, partículas
# =====================================================================================================================
def ladrilho(seed, n=96, fmax=8):
    """Ruído 0..1 de lado n que emenda nas quatro bordas (soma de senos de frequência inteira)."""
    r = np.random.default_rng(seed); y, x = np.mgrid[0:n, 0:n] / n
    t = np.zeros((n, n))
    for _ in range(48):
        fx, fy = r.integers(-fmax, fmax + 1, 2)
        if fx == 0 and fy == 0:
            continue
        t += np.sin(2 * np.pi * (fx * x + fy * y) + r.uniform(0, 6.28)) / (1 + 0.25 * math.hypot(fx, fy))
    return (t - t.min()) / (t.max() - t.min())


class Campo:
    """Ruído ladrilhável rolando sobre a tela. O laço fecha quando velocidade * quadros_do_laço é múltiplo do lado:
    com lado 96, vy=2 fecha em 48 quadros; vy=1 só em 96. `fecha` confere isso."""

    def __init__(self, tela, lado=96):
        self.T = lado; self.YY, self.XX = tela.grade()

    def rola(self, R, f, vy=0, vx=0, oy=0, ox=0):
        """R amostrado na tela, andando vy px/quadro para cima (e vx para a esquerda), com deslocamento fixo oy/ox."""
        return R[(self.YY + vy * f + oy) % self.T, (self.XX + vx * f + ox) % self.T]

    def fecha(self, n, *vels):
        for v in vels:
            assert (v * n) % self.T == 0, f"ruído com velocidade {v} não fecha em {n} quadros (lado {self.T})"


def linguas(idx, n, rampa, alt=7, forca=0.0, lim=0.36):
    """Línguas (fogo, fumaça, vapor) subindo da borda de cima do que estiver desenhado em idx.
    n: campo 0..1 do quadro (Campo.rola subindo). rampa: índices da paleta da base à ponta.
    alt: altura máxima em px; forca: quanto mais, mais língua; lim: limiar base do ruído."""
    A = idx >= 0
    out = idx.copy()
    livre = ~A
    for d in range(1, alt + 1):
        base = np.zeros_like(A); base[:-d] = A[d:]            # tem desenho d pixels abaixo
        if d > 1:
            mid = np.zeros_like(A); mid[:-(d - 1)] = A[d - 1:]; livre = livre & ~mid   # e nada no caminho
        m = base & livre & (n > lim + 0.085 * d - forca)
        out[m] = rampa[min(d, len(rampa) - 1)]
    return out


def cintila(idx, n, alto, baixo, sobe=2, desce=1, piso=1, teto=14, mask=None):
    """Miolo que cintila: onde o ruído n passa de `alto` o pixel clareia `sobe` degraus da paleta; abaixo de `baixo`
    escurece `desce` (sem cair abaixo de `piso`, para não virar contorno). Mexe em idx."""
    m = (idx >= 0) if mask is None else mask
    a = m & (n > alto); idx[a] = np.minimum(idx[a] + sobe, teto)
    b = m & (n < baixo); idx[b] = np.maximum(idx[b] - desce, piso)
    return idx


def ondula_colunas(idx, dy, base=11, y_corte=None):
    """Faixa de chão que ondula: cada coluna x sobe/desce dy[x] px; os `base` px de baixo não descolam do chão."""
    c = np.full_like(idx, -1)
    for x in range(idx.shape[1]):
        col = idx[:, x]; d = int(dy[x])
        if d > 0:
            c[:-d, x] = col[d:]; c[-d - base:, x] = np.where(col[-d - base:] >= 0, col[-d - base:], c[-d - base:, x])
        elif d < 0:
            c[-d:, x] = col[:d]
        else:
            c[:, x] = col
    if y_corte is not None:
        c[y_corte:] = -1
    return c


def carimba(dst, src, cx, cy):
    """Cola src (idx) em dst centrado em (cx, cy), recortando na borda."""
    CH, CW = dst.shape
    h, w = src.shape; x0 = int(round(cx - w / 2)); y0 = int(round(cy - h / 2))
    ya, yb = max(0, y0), min(CH, y0 + h); xa, xb = max(0, x0), min(CW, x0 + w)
    if ya >= yb or xa >= xb:
        return
    s = src[ya - y0:yb - y0, xa - x0:xb - x0]; d = dst[ya:yb, xa:xb]; d[s >= 0] = s[s >= 0]


def ponto(dst, x, y, c, y_max=None):
    """Um pixel, se couber (y abaixo de y_max, padrão a altura da camada)."""
    if 0 <= y < (dst.shape[0] if y_max is None else y_max) and 0 <= x < dst.shape[1]:
        dst[y, x] = c


def carimbo_girado(spr, ang, achat=1.0, esc=1.0, amp=4):
    """Gira (ang, rad), achata (achat -1..1: papel virando no ar) e escala um sprite RGBA amp x. Devolve RGBA amp x
    num quadrado; passe por `reduz` e `Paleta.encaixa` para carimbar."""
    h, w = spr.shape[:2]; Tm = int(math.hypot(h, w)) + 8; Tm += (-Tm) % amp
    c, s_ = math.cos(ang), math.sin(ang)
    A = np.array([[c * esc, -s_ * esc * achat], [s_ * esc, c * esc * achat]])
    t = np.array([Tm / 2, Tm / 2]) - A @ np.array([w / 2, h / 2])
    return cv2.warpAffine(spr, np.hstack([A, t[:, None]]).astype(np.float32), (Tm, Tm), flags=cv2.INTER_NEAREST, borderValue=0)


def semeia(rng, qtd, campos):
    """Sementes de partícula: lista de dicts. campos = {nome: ("int", lo, hi) | ("uni", lo, hi) | função(i, rng)},
    sorteados nessa ordem para cada partícula. O campo "b" é o quadro de nascimento dentro do laço: espalhe
    (ex.: lambda i, r: (i * passo + int(r.integers(0, 5))) % n_laco) para nunca nascerem todas juntas."""
    out = []
    for i in range(qtd):
        d = {}
        for nome, c in campos.items():
            if callable(c):
                d[nome] = c(i, rng)
            elif c[0] == "int":
                d[nome] = int(rng.integers(c[1], c[2]))
            else:
                d[nome] = float(rng.uniform(c[1], c[2]))
        out.append(d)
    return out


def emite(L, f, n, sementes, desenha, vida=None):
    """Emissor em laço: desenha no quadro f (camada L) toda partícula viva.
    Cada semente tem "b" (nascimento) e, se quiser, "per" (período próprio, divisor de n; padrão n) e "vida".
    A idade é a = (f - b) % per: a partícula renasce a cada período e o laço fecha sozinho.
    desenha(L, semente, a, f, i) desenha e devolve True se sobrou algo visível. Devolve quantas estão vivas."""
    vivas = 0
    for i, sd in enumerate(sementes):
        a = (f - sd["b"]) % sd.get("per", n)
        v = sd.get("vida", vida)
        if v is not None and a >= v:
            continue
        if desenha(L, sd, a, f, i):
            vivas += 1
    return vivas


def desenha_fagulha(cores, y0=184, chao_y=190):
    """Fagulha que sobe do chão: semente com x, dx, v, vida. cores = (claro, amar, lar, verm): esfria ao subir."""
    claro, amar, lar, verm = cores

    def des(L, p, a, f, i):
        y = int(round(y0 - p["v"] * a - 0.012 * a * a)); x = int(round(p["x"] + p["dx"] * a + 1.6 * math.sin(a * 0.45 + p["x"])))
        q = a / p["vida"]
        if 0 <= y < L.shape[0] and 0 <= x < L.shape[1]:
            L[y, x] = claro if q < 0.3 else amar if q < 0.6 else lar if q < 0.85 else verm
            if q < 0.3 and y + 1 < chao_y:
                L[y + 1, x] = amar
            return True
        return False
    return des


def desenha_gota(ancora, cores, presa=18, chao_y=190):
    """Gota grossa que pinga de um ponto que se mexe: engorda presa (fio + bolha) por `presa` quadros, solta, cai
    acelerando e respinga no chão. Semente com "ancora" (nome), "b" e "per". ancora(nome, f) -> (x, y) no jogo.
    cores = (claro, amar, lar, verm). Desenhada direto em 1x porque gota do conceito some na redução."""
    claro, amar, lar, verm = cores; ym = chao_y - 1

    def des(L, sd, a, f, i):
        nome = sd["ancora"]
        if a < presa:                                    # presa: fio que estica e bolha que engorda
            x, y = ancora(nome, f); x = int(round(x)); y = int(round(y))
            comp = 1 + a // 4
            for k in range(comp):
                ponto(L, x, y + k, amar, ym)
            yb = y + comp
            ponto(L, x, yb, claro, ym); ponto(L, x, yb + 1, amar, ym)
            if a >= 6:
                ponto(L, x + 1, yb, amar, ym); ponto(L, x + 1, yb + 1, lar, ym)
            if a >= 12:
                ponto(L, x, yb + 2, lar, ym); ponto(L, x - 1, yb + 1, amar, ym); ponto(L, x + 1, yb + 2, verm, ym)
            return True
        t = a - presa; x, y0 = ancora(nome, f - t); x = int(round(x))
        y = int(round(y0 + 6 + 0.45 * t + 0.075 * t * t))
        if y < chao_y - 4:                               # caindo: lágrima com rabo
            ponto(L, x, y - 4, lar, ym); ponto(L, x, y - 3, amar, ym); ponto(L, x, y - 2, amar, ym)
            ponto(L, x, y - 1, claro, ym); ponto(L, x + 1, y - 1, amar, ym); ponto(L, x - 1, y - 1, amar, ym)
            ponto(L, x, y, claro, ym); ponto(L, x + 1, y, lar, ym); ponto(L, x - 1, y, lar, ym); ponto(L, x, y + 1, lar, ym)
            return True
        tq = next(k for k in range(400) if y0 + 6 + 0.45 * k + 0.075 * k * k >= chao_y - 4.5); s = t - tq
        if s < 5:                                        # respingo: 5 quadros
            for dx in (-1 - s, 1 + s):
                ponto(L, x + dx, chao_y - 3 - (2 if s in (1, 2) else 1 if s in (0, 3) else 0), claro if s < 2 else amar, ym)
            if s < 3:
                ponto(L, x, chao_y - 2, claro, ym); ponto(L, x - 1, chao_y - 2, amar, ym); ponto(L, x + 1, chao_y - 2, amar, ym)
            return True
        return False
    return des


# =====================================================================================================================
# 7. Saída: camadas, aura.json, tiras, vídeo
# =====================================================================================================================
def exporta_camadas(pasta, camadas, pal, limpar=True):
    """Grava pasta/<nome>_NN.png (RGBA, alfa 0/255) para cada camada {nome: [idx por quadro]}.
    limpar=True apaga antes os PNG/JSON que estavam na pasta (para não sobrar quadro de uma versão mais longa)."""
    os.makedirs(pasta, exist_ok=True)
    if limpar:
        for a in os.listdir(pasta):
            if a.endswith((".png", ".json")):
                os.remove(os.path.join(pasta, a))
    for nome, lst in camadas.items():
        for f, idx in enumerate(lst):
            Image.fromarray(pal.rgba(idx)).save(os.path.join(pasta, f"{nome}_{f:02d}.png"))


def escreve_aura_json(pasta, lutador, aura, tela, tiques, camadas, pal, extras=None):
    """pasta/aura.json: o contrato com quem liga a aura no jogo.
    camadas: lista NA ORDEM DE DESENHO (a primeira fica mais ao fundo) de
             dict(nome, quadros, plano="atras"|"frente" do corpo, e o que mais quiser documentar)."""
    d = dict(formato=1, lutador=lutador, aura=aura,
             tela=[tela.cw, tela.ch], pe=[tela.pe[0], tela.pe[1]], tiques_por_quadro=tiques, alfa="0 ou 255",
             arquivo="{nome}_{quadro:02d}.png",
             camadas=list(camadas),
             paleta=pal.lista())
    d.update(extras or {})
    with open(os.path.join(pasta, "aura.json"), "w", encoding="utf-8") as fo:
        json.dump(d, fo, indent=1, ensure_ascii=False)
    return d


def fundo_teste(tela):
    """Cenário escuro neutro com linha de chão e pilares, só para vídeo e tira."""
    CH, CW = tela.ch, tela.cw; py = tela.pe[1]
    fundo = np.zeros((CH, CW, 3), np.uint8)
    for y in range(CH):
        t = y / py
        fundo[y] = (26 + 16 * t, 28 + 15 * t, 40 + 14 * t) if y < py else (30, 28, 32)
    fundo[py] = (58, 54, 60)
    for x in range(0, CW, 45):
        fundo[60:py, x:x + 14] = (fundo[60:py, x:x + 14].astype(int) * 0.86).astype(np.uint8)
    return fundo


def sobre(base, cam):
    """Cola uma camada RGBA em cima de base RGB (mexe em base)."""
    m = cam[..., 3] > 0; base[m] = cam[..., :3][m]


def compoe(fundo, f, atras, corpo, frente, pal):
    """Quadro f do conjunto: fundo, camadas de trás (listas de idx, cada uma com o seu laço), corpo RGBA (ou None),
    camadas da frente."""
    o = fundo.copy()
    for lst in atras:
        sobre(o, pal.rgba(lst[f % len(lst)]))
    if corpo is not None:
        sobre(o, corpo)
    for lst in frente:
        sobre(o, pal.rgba(lst[f % len(lst)]))
    return o


def tira(quadros, arq, cols=4, esc=2, rotulos=None):
    """Folha de contato: lista de imagens RGB do mesmo tamanho, `cols` por linha, ampliadas `esc` vezes sem borrar."""
    h, w = quadros[0].shape[:2]; lin = (len(quadros) + cols - 1) // cols
    t = Image.new("RGB", (w * cols, h * lin))
    for k, q in enumerate(quadros):
        t.paste(Image.fromarray(q), ((k % cols) * w, (k // cols) * h))
    t = t.resize((t.width * esc, t.height * esc), Image.NEAREST)
    if rotulos:
        d = ImageDraw.Draw(t); fnt = ImageFont.load_default()
        for k, r in enumerate(rotulos):
            d.text(((k % cols) * w * esc + 6, (k // cols) * h * esc + 4), r, font=fnt, fill=(200, 200, 210))
    t.save(arq)


def grava_video(arq, w, h, gera, total=600, fps=60):
    """MP4 (ffmpeg, x264) de `total` quadros a `fps`. gera(t, None) devolve a chave do quadro t; gera(t, chave)
    devolve os bytes RGB (w*h*3). Quadros com a mesma chave são gerados uma vez só."""
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
                           "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "14", "-preset", "medium", arq], stdin=subprocess.PIPE)
    cache = {}
    for t in range(total):
        k = gera(t, None)
        if k not in cache:
            cache[k] = gera(t, k)
        ff.stdin.write(cache[k])
    ff.stdin.close(); ff.wait()


def video_laco(arq, quadros, tiques, esc=3, total=600):
    """Vídeo do laço como o jogo mostraria: cada quadro RGB fica `tiques` tiques de 1/60 s, ampliado `esc` vezes."""
    h, w = quadros[0].shape[:2]; n = len(quadros)

    def gera(t, k):
        key = (t // tiques) % n
        if k is None:
            return key
        return Image.fromarray(quadros[key]).resize((w * esc, h * esc), Image.NEAREST).tobytes()
    grava_video(arq, w * esc, h * esc, gera, total)


# =====================================================================================================================
# 8. Medidas de fluidez
# =====================================================================================================================
def mede_camada(lst, pal):
    """Números de uma camada em laço (lista de idx). O que olhar:
      pixels_que_nunca_mudam    -> tem de dar ~0 (nada parado);
      pares_consecutivos_iguais -> 0 (nenhum quadro repetido);
      emenda x vizinhos_da_emenda -> a diferença do último para o primeiro quadro tem de ser do tamanho das vizinhas;
      frac_pixels_mudam         -> perto de 1 em peça que só se desloca é fervura (afine a folga da histerese)."""
    n = len(lst); difs = []; mud = []; iguais = 0
    for f in range(n):
        a, b = lst[f], lst[(f + 1) % n]
        uniao = (a >= 0) | (b >= 0)
        difs.append(float(np.abs(pal.rgba(a).astype(int) - pal.rgba(b).astype(int)).mean()))
        mud.append(float(((a != b) & uniao).sum() / max(uniao.sum(), 1))); iguais += int((a == b).all())
    pilha = np.stack(lst); sempre = (pilha >= 0).all(0); parado = sempre & (pilha == pilha[0]).all(0)
    cores = [int(len(np.unique(l[l >= 0]))) for l in lst]
    return dict(quadros=n, emenda=round(difs[-1], 3), dif_min=round(min(difs), 3), dif_max=round(max(difs), 3),
                vizinhos_da_emenda=[round(difs[-2], 3), round(difs[0], 3)],
                frac_pixels_mudam_min=round(min(mud), 3), frac_pixels_mudam_max=round(max(mud), 3),
                pares_consecutivos_iguais=iguais, pixels_que_nunca_mudam=int(parado.sum()), pixels_opacos_quadro0=int((lst[0] >= 0).sum()),
                cores_min=min(cores), cores_max=max(cores))


def mede_pontos(pontos, chaves=None, mostra=True):
    """Chicote/cascata: para cada ponto exportado pelo Blender (lista de dicts por quadro), a fase do 1º harmônico
    do sobe-e-desce (em quadros), o curso pico a pico em x e y e o maior passo entre quadros vizinhos (px).
    O que olhar: fase_q CRESCENDO da raiz para a ponta (a ponta chega depois) e passo_max abaixo de ~3 px."""
    N = len(pontos); t = np.arange(N); res = {}
    for k in (chaves or list(pontos[0].keys())):
        xy = np.array([p[k][:2] for p in pontos]); y = xy[:, 1] - xy[:, 1].mean()
        c = (y * np.exp(-2j * np.pi * t / N)).sum()
        fase = (-np.angle(c) / (2 * np.pi) * N) % N
        passo = max(float(np.hypot(*(xy[(i + 1) % N] - xy[i]))) for i in range(N))
        res[k] = dict(fase_q=round(float(fase), 1), curso_x=round(float(np.ptp(xy[:, 0])), 1), curso_y=round(float(np.ptp(xy[:, 1])), 1),
                      passo_max=round(passo, 2))
        if mostra:
            print(f"{k:16s} fase {fase:5.1f} q   curso x {np.ptp(xy[:, 0]):5.1f}  y {np.ptp(xy[:, 1]):5.1f}   passo max {passo:4.2f}")
    return res


def mede_conjunto(camadas, pal, n_total):
    """Medidas do conjunto {nome: [idx]}: extensão na tela, cores por quadro e pixels com azul acima do verde
    (derrame de magenta que escapou; só faz sentido em aura quente)."""
    L = list(camadas.values())
    uni = [np.where(np.any([(l[f % len(l)] >= 0) for l in L], 0)) for f in range(n_total)]
    cores = [int(len(np.unique(np.concatenate([l[f % len(l)][l[f % len(l)] >= 0] for l in L])))) for f in range(n_total)]
    azul = int(sum(((pal.rgba(q)[..., 2].astype(int) > pal.rgba(q)[..., 1]) & (q >= 0)).sum() for l in L for q in l))
    return dict(extensao_aura_x_min_max_y_min=[int(min(u[1].min() for u in uni)), int(max(u[1].max() for u in uni)), int(min(u[0].min() for u in uni))],
                cores_todas_as_camadas_por_quadro=[min(cores), max(cores)], azul_acima_do_verde_px=azul)


# =====================================================================================================================
# 9. Linha de comando comum a toda aura
# =====================================================================================================================
def roda(arquivo, etapas, padrao_pasta):
    """Ponto de entrada de um script de aura.
    Fora do Blender:  python <aura>.py [pasta_de_trabalho] [etapa ...]     (sem etapa = todas, na ordem do dict)
    A etapa "rig" e a etapa "pontos" abrem o Blender em segundo plano com este mesmo arquivo (saída em
    pasta/blender.log); dentro do Blender roda etapas["rig"](pasta, so_pontos). As outras são etapas[nome](pasta).
    """
    try:
        import bpy  # noqa: F401
        dentro = True
    except ImportError:
        dentro = False
    if dentro:
        args = sys.argv[sys.argv.index("--") + 1:]
        etapas["rig"](args[0], len(args) > 1 and args[1] == "so_pontos")
        return
    args = sys.argv[1:]
    nomes = list(etapas) + ["pontos"]
    pasta = padrao_pasta
    if args and args[0] not in nomes:
        pasta = args.pop(0)
    pasta = os.path.abspath(pasta).replace("\\", "/"); os.makedirs(pasta, exist_ok=True)
    for e in (args or list(etapas)):
        if e not in nomes:
            sys.exit(f"etapa desconhecida: {e} (use {', '.join(nomes)})")
        t0 = time.time(); print(f"== {e} ==", flush=True)
        if e in ("rig", "pontos"):
            cmd = [BLENDER, "-b", "--python", os.path.abspath(arquivo), "--", pasta] + (["so_pontos"] if e == "pontos" else [])
            log = os.path.join(pasta, "blender.log")
            with open(log, "w", encoding="utf-8", errors="replace") as fo:
                r = subprocess.run(cmd, stdout=fo, stderr=subprocess.STDOUT)
            saida = open(log, encoding="utf-8", errors="replace").read()
            if r.returncode != 0 or "Traceback" in saida or "TEMPO_RENDER" not in saida:
                print(saida[-3000:]); sys.exit(f"Blender falhou (veja {log})")
            print("\n".join(l for l in saida.splitlines() if l.startswith(("MALHA", "TEMPO_RENDER"))))
        else:
            etapas[e](pasta)
        print(f"== {e}: {time.time() - t0:.1f} s ==", flush=True)


def instala(origem, destino):
    """Copia para `destino` (sprites/<id>/aura/) as camadas listadas em origem/aura.json e o próprio aura.json.
    Apaga antes os PNG/JSON que estavam lá."""
    import shutil
    d = json.load(open(os.path.join(origem, "aura.json"), encoding="utf-8"))
    os.makedirs(destino, exist_ok=True)
    for a in os.listdir(destino):
        if a.endswith((".png", ".json")):
            os.remove(os.path.join(destino, a))
    n = 0
    for c in d["camadas"]:
        for a in (d["arquivo"].format(nome=c["nome"], quadro=f) for f in range(c["quadros"])):
            shutil.copyfile(os.path.join(origem, a), os.path.join(destino, a)); n += 1
    shutil.copyfile(os.path.join(origem, "aura.json"), os.path.join(destino, "aura.json"))
    print("instalado em", destino, ":", n, "PNG + aura.json")
