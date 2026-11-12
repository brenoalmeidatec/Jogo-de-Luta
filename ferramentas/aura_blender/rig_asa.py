"""Rig 2D das asas no Blender: recorte + malha em grade + ossos (ombro -> cotovelo -> punho com a garra -> dedos).
Uso: blender -b --python rig_asa.py -- <pasta> [so_pontos]
Unidade do Blender = 1 px do jogo. Render 4x (1440x800) em Cycles 1 amostra, filtro BOX 0.01, textura Closest.
v2: 48 quadros (2 tiques cada), chicote de verdade (a ponta gira mais e mais tarde que a raiz), ombro que sobe e
desce, membrana junto ao corpo com amplitude própria, tremor de pena por Displace em laço, coroa com mais vida."""
import bpy, sys, json, math, os, time
import numpy as np
from mathutils import Vector, Quaternion
args = sys.argv[sys.argv.index("--") + 1:]
P = args[0]; SO_PONTOS = len(args) > 1 and args[1] == "so_pontos"
S = 112 / 441.0; CX = 1313.0; CHAO = 697.0
CW, CH, AMP = 360, 200, 4
N = 48


def g(x, y):  # conceito -> (X,Z) do Blender
    return ((x - CX) * S, (CHAO - y) * S)


bpy.ops.wm.read_factory_settings(use_empty=True)
cena = bpy.context.scene
cena.render.engine = "CYCLES"; cena.cycles.device = "CPU"; cena.cycles.samples = 1
cena.cycles.use_adaptive_sampling = False; cena.cycles.use_denoising = False
cena.cycles.pixel_filter_type = "BOX"; cena.cycles.filter_width = 0.01
cena.cycles.transparent_max_bounces = 32
cena.render.film_transparent = True
cena.render.resolution_x = CW * AMP; cena.render.resolution_y = CH * AMP; cena.render.resolution_percentage = 100
cena.render.image_settings.file_format = "PNG"; cena.render.image_settings.color_mode = "RGBA"
cena.view_settings.view_transform = "Standard"; cena.view_settings.look = "None"
cena.render.dither_intensity = 0
cena.frame_start = 0; cena.frame_end = N - 1
cam = bpy.data.cameras.new("cam"); cam.type = "ORTHO"; cam.ortho_scale = CW
co = bpy.data.objects.new("cam", cam); cena.collection.objects.link(co); cena.camera = co
co.location = (0, -200, 190 - CH / 2); co.rotation_euler = (math.pi / 2, 0, 0)
cam.clip_start = 1; cam.clip_end = 1000


def material(nome, arq):
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


def dist_seg(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length


# ossos da asa esquerda em coordenadas do conceito: nome, pai, cabeça, cauda (a direita é o espelho em x=1313)
OSSOS = [
    ("braco", None, (1278, 330), (1193, 287)),
    ("antebraco", "braco", (1193, 287), (1143, 155)),
    ("garra", "antebraco", (1143, 155), (1197, 178)),
    ("d1a", "antebraco", (1143, 155), (1083, 100)), ("d1b", "d1a", (1083, 100), (1000, 72)), ("d1c", "d1b", (1000, 72), (880, 55)),
    ("d2a", "antebraco", (1143, 155), (1050, 158)), ("d2b", "d2a", (1050, 158), (930, 170)), ("d2c", "d2b", (930, 170), (780, 190)),
    ("d3a", "antebraco", (1143, 155), (1060, 220)), ("d3b", "d3a", (1060, 220), (985, 300)), ("d3c", "d3b", (985, 300), (860, 420)),
    ("d4a", "antebraco", (1143, 155), (1117, 250)), ("d4b", "d4a", (1117, 250), (1108, 350)), ("d4c", "d4b", (1108, 350), (1050, 480)),
    ("d5a", "braco", (1193, 287), (1200, 370)), ("d5b", "d5a", (1200, 370), (1175, 450)),
]
# animação: (amplitude em graus, atraso em fração do ciclo, ondulação 2x em graus, fase da ondulação)
# A raiz gira pouco e cedo; cada junta adiante gira MAIS e mais TARDE: é isso que faz o chicote na posição da ponta.
ANIM = {"braco": (4.0, 0.00, 0, 0), "antebraco": (3.2, 0.08, 0, 0), "garra": (-3.0, 0.14, 0, 0),
        "d1a": (3.2, 0.17, 0.0, 0), "d1b": (4.6, 0.27, 0.9, 0.0), "d1c": (7.5, 0.38, 2.0, 0.0),
        "d2a": (3.0, 0.17, 0.0, 0), "d2b": (5.0, 0.27, 0.9, 0.9), "d2c": (8.0, 0.38, 2.0, 0.9),
        "d3a": (1.6, 0.18, 0.0, 0), "d3b": (5.0, 0.28, 1.0, 1.8), "d3c": (8.0, 0.40, 2.2, 1.8),
        "d4a": (-1.5, 0.18, 0.6, 2.7), "d4b": (5.0, 0.29, 1.2, 2.7), "d4c": (8.0, 0.41, 2.4, 2.7),
        "d5a": (-4.0, 0.12, 1.0, 3.6), "d5b": (8.0, 0.26, 2.2, 3.6)}
CENTRO = -0.25      # a batida fica um pouco abaixo da pose do desenho (não cresce para cima da tela)


def onda(f):  # sobe devagar, respira, desce um pouco mais rápido; período N
    t = 2 * math.pi * f / N
    return math.sin(t) + 0.18 * math.sin(2 * t + 0.6)


def laco(nome, raio, fase):
    """Vazio que anda em círculo no plano Y-Z: ruído amostrado nele fecha o laço em N quadros."""
    e = bpy.data.objects.new(nome, None); cena.collection.objects.link(e)
    for f in range(N + 1):
        t = 2 * math.pi * f / N + fase
        e.location = (0, raio * math.cos(t), raio * math.sin(t)); e.keyframe_insert("location", frame=f)
    return e


tex = bpy.data.textures.new("tremor", "CLOUDS"); tex.noise_scale = 26.0; tex.noise_depth = 1
marc = {}


def asa(nome, lado, fase, prof):
    arq = os.path.join(P, "recortes", f"asa_{nome}.png")
    mat, img = material("mat_" + nome, arq); W, H = img.size
    A = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)[::-1, :, 3] > 0.5
    ys, xs = np.where(A); x0, x1, y0, y1 = xs.min() - 8, xs.max() + 9, ys.min() - 8, ys.max() + 9
    C = 8

    def mx(x):
        return x if lado < 0 else 2 * CX - x
    ossos = [(n, p, (mx(h[0]), h[1]), (mx(t[0]), t[1])) for n, p, h, t in OSSOS]
    ad = bpy.data.armatures.new("arm_" + nome); ao = bpy.data.objects.new("arm_" + nome, ad)
    cena.collection.objects.link(ao)
    ox, oz = g(*ossos[0][2])
    bpy.context.view_layer.objects.active = ao; bpy.ops.object.mode_set(mode="EDIT")
    for n, p, h, t in ossos:
        b = ad.edit_bones.new(n); hx, hz = g(*h); tx, tz = g(*t)
        b.head = (hx - ox, 0, hz - oz); b.tail = (tx - ox, 0, tz - oz)
        if p:
            b.parent = ad.edit_bones[p]; b.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    verts = {}; faces = []

    def v(ix, iy):
        k = (ix, iy)
        if k not in verts:
            verts[k] = len(verts)
        return verts[k]
    for iy in range(y0, y1, C):
        for ix in range(x0, x1, C):
            if A[max(iy, 0):iy + C, max(ix, 0):ix + C].any():
                faces.append((v(ix, iy + C), v(ix + C, iy + C), v(ix + C, iy), v(ix, iy)))
    punho = Vector(g(*ossos[1][3]))
    cov = [None] * len(verts)
    for (ix, iy), i in verts.items():
        X, Z = g(ix, iy); d = (Vector((X, Z)) - punho).length
        cov[i] = (X - ox, 0.004 * d, Z - oz)      # coordenadas locais do ombro: a malha é filha da armação
    me = bpy.data.meshes.new("asa_" + nome); me.from_pydata(cov, [], faces); me.update()
    uvl = me.uv_layers.new(name="uv"); inv = {i: k for k, i in verts.items()}
    for poly in me.polygons:
        for li in poly.loop_indices:
            ix, iy = inv[me.loops[li].vertex_index]; uvl.data[li].uv = (ix / W, 1 - iy / H)
    me.materials.append(mat)
    ob = bpy.data.objects.new("asa_" + nome, me); cena.collection.objects.link(ob)
    segs = [(n, Vector(g(*h)), Vector(g(*t))) for n, p, h, t in ossos]
    grupos = {n: ob.vertex_groups.new(name=n) for n, _, _, _ in ossos}
    gt = ob.vertex_groups.new(name="tremor")
    for i, c in enumerate(cov):
        p = Vector((c[0] + ox, c[2] + oz))
        ds = sorted((dist_seg(p, a, b), n) for n, a, b in segs)
        ws = [(1.0 / (d + 1.5) ** 3, n) for d, n in ds[:4]]
        tot = sum(w for w, _ in ws)
        for w, n in ws:
            grupos[n].add([i], w / tot, "REPLACE")
        gt.add([i], min(1.0, max(0.0, (ds[0][0] - 1.5) / 9.0)), "REPLACE")   # pena treme, osso não
    # tremor de pena: dois Displace (X e Z) com ruído amostrado num vazio que anda em círculo (fecha o laço)
    for eixo, raio, fz, forca in (("X", 9.0, 0.0 + fase, 5.0), ("Z", 11.0, 2.1 + fase, 6.5)):
        md = ob.modifiers.new("tremor" + eixo, "DISPLACE"); md.texture = tex; md.direction = eixo; md.space = "LOCAL"
        md.mid_level = 0.5; md.strength = forca; md.vertex_group = "tremor"
        md.texture_coords = "OBJECT"; md.texture_coords_object = laco(f"laco_{nome}_{eixo}", raio, fz)
    md = ob.modifiers.new("arm", "ARMATURE"); md.object = ao
    sn = 1 if lado < 0 else -1
    for n, _, _, _ in ossos:
        pb = ao.pose.bones[n]; pb.rotation_mode = "QUATERNION"
        eixo = (ad.bones[n].matrix_local.to_3x3().inverted() @ Vector((0, 1, 0))).normalized()
        amp, atr, amp2, f2 = ANIM[n]
        for f in range(N + 1):
            t = f - fase - atr * N
            ang = amp * (onda(t) + CENTRO) + amp2 * math.sin(2 * math.pi * 2 * t / N + f2)
            pb.rotation_quaternion = Quaternion(eixo, math.radians(ang) * sn)
            pb.keyframe_insert("rotation_quaternion", frame=f)
    for f in range(N + 1):
        t = 2 * math.pi * (f - fase) / N
        # respiração: a asa encurta quando desce (profundidade fingida); o ombro sobe quando a asa empurra para baixo
        ao.scale = (1 - 0.055 * (0.5 - 0.5 * math.sin(t - 0.2)), 1, 1)
        ao.location = (ox + 1.2 * sn * math.sin(t + 0.9), prof, oz - 3.0 * math.sin(t + 0.5) + 0.6 * math.sin(2 * t))
        ao.keyframe_insert("scale", frame=f); ao.keyframe_insert("location", frame=f)
    ob.parent = ao   # a malha acompanha o ombro (o modificador de armação sozinho ignora o movimento do objeto)
    marc[nome] = (ao, [n for n, _, _, _ in ossos])
    print("ASA", nome, "verts", len(cov), "faces", len(faces))
    return ob


obE = asa("esq", -1, 0.0, 0.0)
obD = asa("dir", +1, 4.0, 3.0)  # a asa de trás, 4 quadros fora de fase
info = json.load(open(os.path.join(P, "recortes", "info.json")))
bx = info["coroa_bbox"]; matc, imgc = material("mat_coroa", os.path.join(P, "recortes", "coroa.png")); W, H = imgc.size
(xa, za), (xb, zb) = g(bx[0] - 4, bx[3] + 4), g(bx[2] + 4, bx[1] - 4)
cxm, czm = (xa + xb) / 2, (za + zb) / 2
me = bpy.data.meshes.new("coroa")
me.from_pydata([(xa - cxm, 0, za - czm), (xb - cxm, 0, za - czm), (xb - cxm, 0, zb - czm), (xa - cxm, 0, zb - czm)], [], [(0, 1, 2, 3)])
uvl = me.uv_layers.new(name="uv")
for li, (x, y) in zip(range(4), [(bx[0] - 4, bx[3] + 4), (bx[2] + 4, bx[3] + 4), (bx[2] + 4, bx[1] - 4), (bx[0] - 4, bx[1] - 4)]):
    uvl.data[li].uv = (x / W, 1 - y / H)
me.materials.append(matc); oc = bpy.data.objects.new("coroa", me); cena.collection.objects.link(oc)
oc.rotation_mode = "XYZ"
for f in range(N + 1):   # coroa: flutua, balança e gira como se pairasse (o giro em Z encurta a largura)
    t = 2 * math.pi * f / N
    oc.location = (cxm + 2.2 * math.sin(t + 1.0), -3, czm + 1.5 + 4.0 * math.sin(t - 0.8) + 1.0 * math.sin(2 * t + 0.3))
    oc.rotation_euler = (0, math.radians(9.0 * math.sin(t + 0.4)), math.radians(32.0 * math.sin(t + 2.0)))
    oc.scale = (1, 1, 1 + 0.07 * math.sin(2 * t + 1.0))
    oc.keyframe_insert("location", frame=f); oc.keyframe_insert("rotation_euler", frame=f); oc.keyframe_insert("scale", frame=f)
for o in list(bpy.data.objects):  # interpolação linear: o quadro N é igual ao 0 e o laço fecha
    if o.animation_data and o.animation_data.action:
        for fc in o.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
if not SO_PONTOS:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(P, "asa_rig.blend"))
os.makedirs(os.path.join(P, "render"), exist_ok=True)
pontos = []
t0 = time.time()
for f in range(N):
    cena.frame_set(f); bpy.context.view_layer.update()
    d = {}
    for nome, (ao, nomes) in marc.items():
        for n in nomes:
            w = ao.matrix_world @ ao.pose.bones[n].tail
            d[f"{nome}_{n}"] = [CW / 2 + w.x, 190 - w.z]
        w = ao.matrix_world @ ao.pose.bones["braco"].head; d[f"{nome}_ombro"] = [CW / 2 + w.x, 190 - w.z]
    w = oc.matrix_world.translation; d["coroa"] = [CW / 2 + w.x, 190 - w.z, oc.rotation_euler.y, math.cos(oc.rotation_euler.z)]
    pontos.append(d)
    if SO_PONTOS:
        continue
    for passada, objs in (("asas", (obE, obD)), ("coroa", (oc,))):
        for o in (obE, obD, oc):
            o.hide_render = o not in objs
        cena.render.filepath = os.path.join(P, "render", f"{passada}_{f:02d}.png")
        bpy.ops.render.render(write_still=True)
json.dump(dict(pontos=pontos, N=N, coroa_centro=[CW / 2 + cxm, 190 - czm], tempo_render=time.time() - t0),
          open(os.path.join(P, "render", "pontos.json"), "w"))
print("TEMPO_RENDER", time.time() - t0)
