"""Câmera, luz e render em PNG transparente. Cycles porque roda em qualquer máquina, até sem placa de vídeo."""
import math

import bpy
from mathutils import Vector

# Quadro final igual ao do jogo (veja ferramentas/recortar_quadros.py): 224x128, pés em (104, 119), 64 px por metro.
LARG, ALT = 224, 128
PIVO = (104, 119)
PX_POR_M = 64
ESCALA_RENDER = 4  # renderiza grande e reduz depois: pixel art limpa


def montar(guinada=38, amostras=24):
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = amostras
    s.cycles.use_denoising = False
    s.cycles.filter_width = 1.0
    s.render.film_transparent = True
    s.render.resolution_x = LARG * ESCALA_RENDER
    s.render.resolution_y = ALT * ESCALA_RENDER
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.color_mode = "RGBA"
    s.view_settings.view_transform = "Standard"
    s.view_settings.look = "None"

    # fundo: luz ambiente fraca e neutra
    mundo = bpy.data.worlds.new("mundo")
    mundo.use_nodes = True
    mundo.node_tree.nodes["Background"].inputs["Color"].default_value = (0.75, 0.75, 0.8, 1)
    mundo.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.22
    s.world = mundo

    # câmera ortográfica: o pé do lutador cai em PIVO, com 64 px por metro
    g = math.radians(guinada)
    direita = Vector((math.cos(g), math.sin(g), 0))
    frente = Vector((-math.sin(g), math.cos(g), 0))  # direção em que a câmera olha
    alvo = Vector((0, 0, ALT / 2 / PX_POR_M)) + direita * 0
    centro_z = (PIVO[1] / PX_POR_M) - (ALT / 2 / PX_POR_M)
    alvo = Vector((0, 0, centro_z)) + direita * ((LARG / 2 - PIVO[0]) / PX_POR_M)
    cam_dados = bpy.data.cameras.new("cam")
    cam_dados.type = "ORTHO"
    cam_dados.ortho_scale = LARG / PX_POR_M
    cam = bpy.data.objects.new("cam", cam_dados)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = alvo - frente * 8
    direcao = alvo - cam.location
    cam.rotation_euler = direcao.to_track_quat("-Z", "Y").to_euler()
    s.camera = cam

    # luz principal vinda de cima e da frente-esquerda de quem olha, mais uma de contra-luz suave
    def sol(nome, energia, euler, cor=(1, 1, 1)):
        d = bpy.data.lights.new(nome, "SUN")
        d.energy = energia
        d.color = cor
        d.angle = math.radians(8)
        o = bpy.data.objects.new(nome, d)
        bpy.context.scene.collection.objects.link(o)
        o.rotation_euler = [math.radians(a) for a in euler]

    sol("principal", 3.6, (48, 8, 30), (1.0, 0.96, 0.9))
    sol("contra", 1.2, (62, 0, -150), (0.7, 0.75, 1.0))
    return cam


def renderizar(caminho):
    bpy.context.scene.render.filepath = str(caminho)
    bpy.ops.render.render(write_still=True)
