"""Roda dentro do Blender (bpy): caminho B do comparativo do boneco de peças.

As MESMAS peças do kit (sprites/pengaro/pecas/) viram malhas 2D com a própria imagem, presas a um esqueleto do Blender
(armature com pesos). A pose gira os ossos, o Blender entorta a malha (a cintura dobra aos poucos em vez de a peça
inteira andar) e renderiza ortográfico, sem filtro. Sem modelo 3D: só o desenho deformado.

  $NAZAFX_PY ferramentas/boneco_blender.py PLANO.json      (quem monta o plano é boneco_pecas.py --blender)
"""
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Quaternion, Vector

plano = json.loads(Path(sys.argv[-1]).read_text(encoding="utf-8"))
W, H = plano["tela"]
PASSO = plano.get("passo", 2)

bpy.ops.wm.read_factory_settings(use_empty=True)
cena = bpy.context.scene
cena.render.engine = "CYCLES"
cena.cycles.device = "CPU"
cena.cycles.samples = 1
cena.cycles.use_denoising = False
cena.cycles.pixel_filter_type = "BOX"
cena.cycles.filter_width = 0.01
cena.cycles.max_bounces = 0
cena.cycles.transparent_max_bounces = 16
cena.render.film_transparent = True
cena.render.resolution_x, cena.render.resolution_y = W, H
cena.render.image_settings.file_format = "PNG"
cena.render.image_settings.color_mode = "RGBA"
cena.view_settings.view_transform = "Standard"
cena.view_settings.look = "None"

camera = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
camera.data.type = "ORTHO"
camera.data.ortho_scale = W
camera.location = (W / 2, H / 2, 50)
cena.collection.objects.link(camera)
cena.camera = camera


def v(p):  # tela (y desce) -> Blender (y sobe)
    return Vector((p[0], H - p[1], 0))


# esqueleto
arm_dados = bpy.data.armatures.new("esqueleto")
arm = bpy.data.objects.new("esqueleto", arm_dados)
cena.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
for nome, o in plano["ossos"].items():
    b = arm_dados.edit_bones.new(nome)
    b.head, b.tail = v(o["de"]), v(o["para"])
    b.roll = 0
for nome, o in plano["ossos"].items():
    if o.get("mae"):
        arm_dados.edit_bones[nome].parent = arm_dados.edit_bones[o["mae"]]
        arm_dados.edit_bones[nome].use_connect = False
bpy.ops.object.mode_set(mode="OBJECT")


def material(caminho):
    m = bpy.data.materials.new(Path(caminho).stem)
    m.use_nodes = True
    nos = m.node_tree
    nos.nodes.clear()
    tex = nos.nodes.new("ShaderNodeTexImage")
    tex.interpolation = "Closest"
    tex.image = bpy.data.images.load(caminho)
    tex.image.colorspace_settings.name = "sRGB"
    emi = nos.nodes.new("ShaderNodeEmission")
    tra = nos.nodes.new("ShaderNodeBsdfTransparent")
    mix = nos.nodes.new("ShaderNodeMixShader")
    out = nos.nodes.new("ShaderNodeOutputMaterial")
    nos.links.new(tex.outputs["Color"], emi.inputs["Color"])
    nos.links.new(tex.outputs["Alpha"], mix.inputs["Fac"])
    nos.links.new(tra.outputs[0], mix.inputs[1])
    nos.links.new(emi.outputs[0], mix.inputs[2])
    nos.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


objetos = {}
for z, (nome, p) in enumerate(plano["pecas"].items()):
    x0, y0, x1, y1 = p["caixa"]  # caixa da peça na tela (a imagem é a tela inteira)
    xs = np.arange(x0, x1 + PASSO, PASSO, dtype=float)
    ys = np.arange(y0, y1 + PASSO, PASSO, dtype=float)
    gx, gy = len(xs), len(ys)
    X, Y = np.meshgrid(xs, ys)
    verts = np.stack([X, H - Y, np.full_like(X, z * 0.01)], -1).reshape(-1, 3)
    faces = [(j * gx + i, j * gx + i + 1, (j + 1) * gx + i + 1, (j + 1) * gx + i)
             for j in range(gy - 1) for i in range(gx - 1)]
    malha = bpy.data.meshes.new(nome)
    malha.from_pydata(verts.tolist(), [], faces)
    uv = malha.uv_layers.new(name="uv")
    co = np.stack([verts[:, 0] / W, verts[:, 1] / H], -1)
    li = np.zeros(len(malha.loops), dtype=np.int32)
    malha.loops.foreach_get("vertex_index", li)
    uv.data.foreach_set("uv", co[li].ravel())
    malha.materials.append(material(p["imagem"]))
    obj = bpy.data.objects.new(nome, malha)
    cena.collection.objects.link(obj)
    # pesos: cada osso com uma função do pixel da tela (y, ou distância ao longo da cadeia)
    pts = np.stack([X.ravel(), Y.ravel()], -1)
    for osso, regra in p["pesos"].items():
        g = obj.vertex_groups.new(name=osso)
        if regra["tipo"] == "fixo":
            w = np.full(len(pts), regra["valor"])
        elif regra["tipo"] == "y":  # 0 em y0, 1 em y1 (linear, preso entre 0 e 1)
            w = np.clip((pts[:, 1] - regra["y0"]) / (regra["y1"] - regra["y0"]), 0, 1)
            if regra.get("inverte"):
                w = 1 - w
        elif regra["tipo"] == "junta":  # perto da junta: mistura; além dela (ao longo do osso filho): 1
            a, b = np.array(regra["junta"], float), np.array(regra["rumo"], float)
            d = b - a
            t = ((pts - a) @ d) / (d @ d) * np.linalg.norm(d)
            w = np.clip(0.5 + t / (2 * regra["faixa"]), 0, 1)
            if regra.get("inverte"):
                w = 1 - w
        for i, wi in enumerate(w):
            if wi > 0:
                g.add([i], float(wi), "REPLACE")
    mod = obj.modifiers.new("esqueleto", "ARMATURE")
    mod.object = arm
    objetos[nome] = obj

for quadro in plano["quadros"]:
    for nome, obj in objetos.items():
        obj.hide_render = nome not in quadro["mostra"]
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        ang = quadro["ang"].get(pb.name, 0.0)
        desl = quadro.get("desl", {}).get(pb.name, [0, 0])
        rest = pb.bone.matrix_local.to_quaternion()
        qw = Quaternion((0, 0, 1), np.radians(-ang))  # positivo = horário na tela, como no caminho A
        pb.rotation_quaternion = rest.inverted() @ qw @ rest
        pb.location = pb.bone.matrix_local.to_3x3().inverted() @ Vector((desl[0], -desl[1], 0))
    bpy.context.view_layer.update()
    cena.render.filepath = quadro["saida"]
    bpy.ops.render.render(write_still=True)
    print("ok", quadro["saida"])
