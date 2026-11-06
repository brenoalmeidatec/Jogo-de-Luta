"""Roda dentro do Blender: deforma os sprites desenhados para criar os quadros do meio.

Uso (quem chama é ferramentas/animar_folha.py):
  blender -b --python ferramentas/blender_sprites.py -- <pasta>

A pasta tem plano.json, os quadros-chave e o deslocamento de cada par. Cada sprite vira uma malha 2D com a própria
imagem: o desenho não muda, só é entortado na direção da pose seguinte. Sem modelo 3D.
"""
import json
import sys
from pathlib import Path

import bpy
import numpy as np

pasta = Path(sys.argv[sys.argv.index("--") + 1])
plano = json.loads((pasta / "plano.json").read_text(encoding="utf-8"))
W, H, PASSO = plano["largura"], plano["altura"], plano["passo"]
gx, gy = W // PASSO + 1, H // PASSO + 1

bpy.ops.wm.read_factory_settings(use_empty=True)
cena = bpy.context.scene
cena.render.engine = "CYCLES"
cena.cycles.device = "CPU"
cena.cycles.samples = 1
cena.cycles.use_denoising = False
cena.cycles.pixel_filter_type = "BOX"
cena.cycles.filter_width = 0.01
cena.render.film_transparent = True
cena.render.resolution_x, cena.render.resolution_y = W, H
cena.render.image_settings.file_format = "PNG"
cena.render.image_settings.color_mode = "RGBA"
cena.view_settings.view_transform = "Standard"
cena.view_settings.look = "None"

camera = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
camera.data.type = "ORTHO"
camera.data.ortho_scale = W
camera.location = (W / 2, H / 2, 10)
cena.collection.objects.link(camera)
cena.camera = camera

# malha em grade: o y da imagem desce e o do Blender sobe
xs = np.arange(gx, dtype=np.float32) * PASSO
ys = np.arange(gy, dtype=np.float32) * PASSO
malha_x, malha_y = np.meshgrid(xs, ys)
base = np.stack([malha_x, H - malha_y, np.zeros_like(malha_x)], axis=-1).reshape(-1, 3)
faces = [(y * gx + x, y * gx + x + 1, (y + 1) * gx + x + 1, (y + 1) * gx + x)
         for y in range(gy - 1) for x in range(gx - 1)]
malha = bpy.data.meshes.new("sprite")
malha.from_pydata(base.tolist(), [], faces)
uv = malha.uv_layers.new(name="uv")
coords = np.stack([base[:, 0] / W, base[:, 1] / H], axis=-1)
indices = np.zeros(len(malha.loops), dtype=np.int32)
malha.loops.foreach_get("vertex_index", indices)
uv.data.foreach_set("uv", coords[indices].ravel())
objeto = bpy.data.objects.new("sprite", malha)
cena.collection.objects.link(objeto)

material = bpy.data.materials.new("sprite")
material.use_nodes = True
nos = material.node_tree
nos.nodes.clear()
textura = nos.nodes.new("ShaderNodeTexImage")
textura.interpolation = "Closest"
emissao = nos.nodes.new("ShaderNodeEmission")
transparente = nos.nodes.new("ShaderNodeBsdfTransparent")
mistura = nos.nodes.new("ShaderNodeMixShader")
saida = nos.nodes.new("ShaderNodeOutputMaterial")
nos.links.new(textura.outputs["Color"], emissao.inputs["Color"])
nos.links.new(textura.outputs["Alpha"], mistura.inputs["Fac"])
nos.links.new(transparente.outputs[0], mistura.inputs[1])
nos.links.new(emissao.outputs[0], mistura.inputs[2])
nos.links.new(mistura.outputs[0], saida.inputs["Surface"])
malha.materials.append(material)

imagens = {}


def imagem(nome):
    if nome not in imagens:
        img = bpy.data.images.load(str(pasta / nome))
        img.colorspace_settings.name = "sRGB"
        imagens[nome] = img
    return imagens[nome]


def renderizar(quadro):
    deslocado = base.copy()
    if quadro["fluxo"]:
        d = np.load(pasta / quadro["fluxo"]).reshape(-1, 2) * quadro["t"]
        deslocado[:, 0] += d[:, 0]
        deslocado[:, 1] -= d[:, 1]
    malha.vertices.foreach_set("co", deslocado.ravel())
    malha.update()
    textura.image = imagem(quadro["imagem"])
    cena.render.filepath = str(pasta / quadro["saida"])
    bpy.ops.render.render(write_still=True)


for quadro in plano["quadros"]:
    renderizar(quadro)
