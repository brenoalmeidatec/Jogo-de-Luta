#!/usr/bin/env python3
"""Efeitos de especial, super e transformação de cada lutador, feitos no Blender (issue #38 do Breno, 2026-11-14).

  bash ferramentas/efeitos_pixel/preparar_nuvem.sh && source ~/.nazafight/ambiente.sh
  "$NAZAFX_PY" ferramentas/efeitos_blender.py                  os 5 lutadores (uns 10 min na nuvem)
  "$NAZAFX_PY" ferramentas/efeitos_blender.py gutto ck         só esses
  "$NAZAFX_PY" ferramentas/efeitos_blender.py --amostras 8     mais rápido, para testar

Regra do Breno (#38): golpe normal usa pixelfx (ferramentas/efeitos.py); especial, super e transformação têm efeito
próprio, renderizado no Blender, na cor do lutador. Nada do ChatGPT.

Cada lutador tem uma receita com o tema dele (CORES e RECEITAS abaixo):
  Pengaró    whisky: gotas e cacos de garrafa voando, respingo; endiabrado em violeta
  Hazak      fogo laranja-ouro: chamas e brasas
  Gutto      onda de choque vermelha (o chute de Muay Thai) e brasas; brasa no despertado
  Raiclaven  aço: lascas de metal e faíscas; relâmpagos verdes no despertado (Cientista Louco)
  CK         paredão de som: anéis de som e fumaça cinza-esverdeada
Três efeitos por lutador:
  especial        estouro no acerto dos especiais (estados 1000-1999), 8 desenhos de 2 ticks, ~70 de largura
  super           explosão no acerto das supers (3000-3399), 12 desenhos de 3 ticks, ~130 de largura
  transformacao   pilar do Despertar (estado 2000, quando a forma troca), 14 desenhos de 3 ticks, ~110 x 190
O render sai em cinza (o brilho é a força) e vira pixel art pelo ferramentas/efeitos_pixel/pixelfx.py (rampa da cor do
lutador, contorno seco, alfa só 0/255). Um render serve para as duas formas: só a rampa muda.

Saída (vai para o git, é o que o efeitos.py liga no jogo): sprites/efeitos_blender/<lutador>/<efeito>_<forma>/NN.png
e meta.json (pivô e ticks). O desenho sai em "pixel de efeito"; no .air ele vai com a escala do efeito (0,75), a mesma
dos efeitos do pixelfx, para os dois terem o mesmo tamanho de pixel na tela.
"""
import argparse
import json
import math
import random
import sys
import time
from pathlib import Path

import bpy
from PIL import Image

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI / "efeitos_pixel"))
sys.path.insert(0, str(AQUI))
import pixelfx  # noqa: E402
from efeitos import CORES, ESCALA_BLENDER  # noqa: E402

SAIDA = RAIZ / "sprites/efeitos_blender"

# efeito -> (largura e altura no jogo, quadros, ticks por quadro, pivô no chão?)
EFEITOS = {
    "especial": ((72, 72), 8, 2, False),
    "super": ((136, 136), 12, 3, False),
    "transformacao": ((112, 196), 14, 3, True),
}
# o que entra em cada efeito de cada lutador
RECEITAS = {
    "pengaro": {"especial": ["miolo", "gotas", "cacos"], "super": ["bola", "anel", "gotas", "cacos", "raios"],
                "transformacao": ["pilar", "anel_chao", "cacos", "fumaca"]},
    "hazaki": {"especial": ["miolo", "chamas", "brasas"], "super": ["bola", "chamas", "anel", "brasas", "raios"]},
    # o Hazak não se transforma (não tem estado 2000): só especial e super
    "gutto": {"especial": ["miolo", "anel", "raios", "brasas"], "super": ["bola", "anel", "anel2", "raios", "brasas"],
              "transformacao": ["pilar", "anel_chao", "brasas"]},
    "raiclaven": {"especial": ["miolo", "raios", "cacos", "relampago"], "super": ["bola", "anel", "cacos", "relampago", "raios"],
                  "transformacao": ["pilar", "anel_chao", "relampago", "cacos"]},
    "ck": {"especial": ["miolo", "anel", "anel2", "fumaca"], "super": ["bola", "anel", "anel2", "anel3", "fumaca"],
           "transformacao": ["pilar", "anel_chao", "fumaca"]},
}


# ---------------------------------------------------------------------------------------------------------------------
# materiais (emissão em cinza: a força do brilho escolhe o tom da rampa do lutador)
# ---------------------------------------------------------------------------------------------------------------------
def no(arvore, tipo, **props):
    n = arvore.nodes.new(tipo)
    for k, v in props.items():
        setattr(n, k, v)
    return n


def mat_nuvem(nome, escala=2.2):
    """Emissão com ruído 4D, clara no miolo e escura na borda; `limiar` abre buracos para a nuvem se desfazer."""
    m = bpy.data.materials.new(nome)
    if bpy.app.version < (5, 0):
        m.use_nodes = True
    t = m.node_tree
    t.nodes.clear()
    L = t.links.new
    coord = no(t, "ShaderNodeTexCoord")
    ruido = no(t, "ShaderNodeTexNoise", noise_dimensions="4D")
    ruido.inputs["Scale"].default_value = escala
    ruido.inputs["Detail"].default_value = 4.0
    L(coord.outputs["Object"], ruido.inputs["Vector"])
    face = no(t, "ShaderNodeLayerWeight")
    face.inputs["Blend"].default_value = 0.45
    centro = no(t, "ShaderNodeMath", operation="SUBTRACT")
    centro.inputs[0].default_value = 1.0
    L(face.outputs["Facing"], centro.inputs[1])
    mist = no(t, "ShaderNodeMath", operation="MULTIPLY")
    L(centro.outputs[0], mist.inputs[0])
    L(ruido.outputs["Fac"], mist.inputs[1])
    calor = no(t, "ShaderNodeValue", name="calor")
    forca = no(t, "ShaderNodeMath", operation="MULTIPLY")
    L(mist.outputs[0], forca.inputs[0])
    L(calor.outputs[0], forca.inputs[1])
    emis = no(t, "ShaderNodeEmission")
    emis.inputs["Color"].default_value = (1, 1, 1, 1)
    L(forca.outputs[0], emis.inputs["Strength"])
    limiar = no(t, "ShaderNodeValue", name="limiar")
    corte = no(t, "ShaderNodeMath", operation="GREATER_THAN")
    L(ruido.outputs["Fac"], corte.inputs[0])
    L(limiar.outputs[0], corte.inputs[1])
    mix = no(t, "ShaderNodeMixShader")
    L(corte.outputs[0], mix.inputs["Fac"])
    L(no(t, "ShaderNodeBsdfTransparent").outputs[0], mix.inputs[1])
    L(emis.outputs[0], mix.inputs[2])
    L(mix.outputs[0], no(t, "ShaderNodeOutputMaterial").inputs["Surface"])
    return m, ruido, t.nodes["calor"], t.nodes["limiar"]


def mat_luz(nome):
    """Emissão lisa; a força (nó 'forca') muda por quadro."""
    m = bpy.data.materials.new(nome)
    if bpy.app.version < (5, 0):
        m.use_nodes = True
    t = m.node_tree
    t.nodes.clear()
    emis = no(t, "ShaderNodeEmission")
    emis.inputs["Color"].default_value = (1, 1, 1, 1)
    emis.inputs["Strength"].default_value = 3.0
    t.links.new(emis.outputs[0], no(t, "ShaderNodeOutputMaterial").inputs["Surface"])
    return m, emis


# ---------------------------------------------------------------------------------------------------------------------
# cena
# ---------------------------------------------------------------------------------------------------------------------
def cena_vazia(rx, ry, amostras, largura):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cena = bpy.context.scene
    r = cena.render
    r.engine = "CYCLES"
    cena.cycles.device = "CPU"
    cena.cycles.samples = amostras
    cena.cycles.use_denoising = False
    r.resolution_x, r.resolution_y = rx, ry
    r.resolution_percentage = 100
    r.film_transparent = True
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGBA"
    cena.view_settings.view_transform = "Standard"
    cena.world = bpy.data.worlds.new("vazio")
    cena.world.color = (0, 0, 0)
    cam = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = largura  # unidades do Blender na largura (o lado maior)
    cam.location = (0, -10, 0)
    cam.rotation_euler = (math.radians(90), 0, 0)
    cena.collection.objects.link(cam)
    cena.camera = cam
    return cena


def esfera(raio=1.0, sub=4, mat=None, local=(0, 0, 0)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=raio, location=local)
    o = bpy.context.active_object
    if mat:
        o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o


def nuvem_deformada(mat, forca=0.35, escala=0.55):
    o = esfera(mat=mat, sub=5)
    tex = bpy.data.textures.new("nuvem", type="CLOUDS")
    tex.noise_scale = escala
    d = o.modifiers.new("desloca", "DISPLACE")
    d.texture = tex
    d.texture_coords = "OBJECT"
    d.strength = forca
    return o, d


def anel_obj(mat, maior=1.0, menor=0.06):
    bpy.ops.mesh.primitive_torus_add(major_radius=maior, minor_radius=menor, major_segments=64, minor_segments=8,
                                     rotation=(math.radians(90), 0, 0))
    o = bpy.context.active_object
    o.data.materials.append(mat)
    return o


def zigue(rnd, comprimento, passos, desvio):
    """Pontos de um relâmpago, de (0, 0) para +x, com desvio aleatório em z."""
    pts = [(0.0, 0.0)]
    for i in range(1, passos + 1):
        pts.append((comprimento * i / passos, rnd.uniform(-desvio, desvio) if i < passos else 0.0))
    return pts


def curva(pontos, mat, espessura=0.03):
    dados = bpy.data.curves.new("raio", "CURVE")
    dados.dimensions = "3D"
    dados.bevel_depth = espessura
    sp = dados.splines.new("POLY")
    sp.points.add(len(pontos) - 1)
    for p, (x, z) in zip(sp.points, pontos):
        p.co = (x, 0, z, 1)
    o = bpy.data.objects.new("raio", dados)
    o.data.materials.append(mat)
    bpy.context.scene.collection.objects.link(o)
    return o


class Efeito:
    """Monta as peças da receita; `quadro(t)` posiciona tudo para t de 0 (contato) a 1 (sumiu)."""

    def __init__(self, pecas, tipo, semente, meia_l, meia_a, chao):
        self.rnd = random.Random(semente)
        self.anim = []
        self.tipo = tipo
        self.L, self.A = meia_l, meia_a  # meia largura e meia altura do quadro, em unidades do Blender
        self.chao = -meia_a + 0.08 if chao else 0.0
        for p in pecas:
            getattr(self, "p_" + p)()

    def quadro(self, t):
        for f in self.anim:
            f(t)

    # -- peças -------------------------------------------------------------------------------------------------------
    def p_miolo(self):
        """Clarão curto no ponto do golpe (o estalo do especial)."""
        m, ruido, calor, limiar = mat_nuvem("miolo", 3.0)
        o, d = nuvem_deformada(m, 0.5, 0.3)

        def f(t):
            u = min(1.0, t / 0.55)
            s = self.L * (0.14 + 0.2 * (1 - (1 - u) ** 2))
            o.location = (0, 0, self.chao)
            o.scale = (s, s, s)
            ruido.inputs["W"].default_value = t * 2
            calor.outputs[0].default_value = 4.0 * (1 - u) ** 1.5 + 0.2
            limiar.outputs[0].default_value = max(0.0, u - 0.25) * 1.2
            o.hide_render = u >= 0.99
        self.anim.append(f)

    def p_bola(self):
        m, ruido, calor, limiar = mat_nuvem("bola")
        o, d = nuvem_deformada(m)
        grande = 0.42 if self.tipo == "super" else 0.3
        o.location = (0, 0, self.chao)

        def f(t):
            e = 1 - (1 - t) ** 2
            s = self.L * (0.18 + grande * e)
            o.scale = (s, s, s * 0.92)
            d.strength = 0.15 + 0.35 * e
            ruido.inputs["W"].default_value = t * 1.5
            calor.outputs[0].default_value = 2.8 * (1 - t) ** 1.6 + 0.25
            limiar.outputs[0].default_value = max(0.0, t - 0.35) * 1.0
        self.anim.append(f)

    def _anel(self, atraso, alcance, grossura, achatado=1.0):
        """Onda de choque: anel grosso que abre, afina e se parte (ruído), não um círculo de régua."""
        m, ruido, calor, limiar = mat_nuvem("anel", 5.0)
        o = anel_obj(m, 1.0, grossura)
        tex = bpy.data.textures.new("anel", type="CLOUDS")
        tex.noise_scale = 0.25
        d = o.modifiers.new("desloca", "DISPLACE")
        d.texture = tex
        d.texture_coords = "OBJECT"
        d.strength = 0.08

        def f(t):
            u = max(0.0, (t - atraso) / (1 - atraso))
            e = 1 - (1 - u) ** 2.5
            s = self.L * (0.12 + alcance * e) if u > 0 else 0.0001
            o.location = (0, -0.5, self.chao)
            o.rotation_euler = (math.radians(90), 0, 0)
            o.scale = (s, s * achatado, s)  # o eixo y do toro é o vertical depois do giro
            ruido.inputs["W"].default_value = u * 2.0 + atraso * 5
            calor.outputs[0].default_value = 3.4 * (1 - u) ** 1.2 + 0.4
            limiar.outputs[0].default_value = max(0.0, u - 0.3) * 0.9
            o.hide_render = u <= 0 or u >= 0.97
        self.anim.append(f)

    def p_anel(self):
        self._anel(0.0, 0.8, 0.07)

    def p_anel2(self):
        self._anel(0.18, 0.7, 0.05)

    def p_anel3(self):
        self._anel(0.36, 0.6, 0.045)

    def p_anel_chao(self):
        """Anel no chão visto de frente: elipse achatada que abre dos pés."""
        m, emis = mat_luz("anel_chao")
        o = anel_obj(m, 1.0, 0.06)

        def f(t):
            e = 1 - (1 - t) ** 2
            s = self.L * (0.25 + 0.7 * e)
            o.location = (0, -0.6, self.chao + 0.05)
            o.scale = (s, s * 0.22, s)  # elipse no chão (y local = vertical)
            emis.inputs["Strength"].default_value = 3.0 * (1 - t) ** 1.2
            o.hide_render = t >= 0.95
        self.anim.append(f)

    def _particulas(self, n, forma, vel, gravidade, tam, luz, so_cima=False):
        mat, emis = mat_luz(forma)
        pecas = []
        for i in range(n):
            ang = (i / n) * 2 * math.pi + self.rnd.uniform(-0.3, 0.3)
            if so_cima:
                ang = math.radians(self.rnd.uniform(25, 155))
            v = self.rnd.uniform(*vel)
            if forma == "caco":
                bpy.ops.mesh.primitive_cube_add(size=1)
                o = bpy.context.active_object
                o.data.materials.append(mat)
            else:
                o = esfera(1.0, 2, mat)
            giro = self.rnd.uniform(-8, 8)
            pecas.append((o, ang, v, giro, self.rnd.uniform(.7, 1.3)))
        base = self.chao if so_cima else 0.0

        def f(t):
            for o, ang, v, giro, k in pecas:
                d = self.L * v * t
                x = math.cos(ang) * d
                z = base + math.sin(ang) * d - self.L * gravidade * t * t
                o.location = (x, -1.2, z)
                vx, vz = math.cos(ang) * v, math.sin(ang) * v - 2 * gravidade * t
                r = max(0.0, 1 - t * 1.15) * k
                s = self.L * tam * r + 0.0001
                if forma == "caco":
                    o.rotation_euler = (giro * t, 0.3, giro * t * 0.7)
                    o.scale = (s * 1.4, s * 0.25, s * 0.8)
                elif forma == "raio":
                    o.rotation_euler = (0, -math.atan2(vz, vx), 0)
                    o.scale = (s * 3.2, s * 0.6, s * 0.6)
                elif forma == "gota":
                    o.rotation_euler = (0, -math.atan2(vz, vx), 0)
                    o.scale = (s * 1.6, s, s)
                else:
                    o.scale = (s, s, s)
                o.hide_render = r <= 0.02
            emis.inputs["Strength"].default_value = luz * (1 - 0.5 * t)
        self.anim.append(f)

    def p_raios(self):
        self._particulas(12, "raio", (0.75, 1.1), 0.0, 0.07, 4.0)

    def p_gotas(self):
        self._particulas(14, "gota", (0.4, 0.9), 0.45, 0.085, 2.6)

    def p_cacos(self):
        self._particulas(9, "caco", (0.45, 0.85), 0.4, 0.11, 1.8, so_cima=self.chao != 0)

    def p_brasas(self):
        self._particulas(16, "brasa", (0.3, 0.95), -0.15, 0.05, 3.5, so_cima=self.chao != 0)

    def p_fumaca(self):
        pecas = []
        for i in range(6):
            m, ruido, calor, limiar = mat_nuvem(f"fumaca{i}", 3.0)
            o, d = nuvem_deformada(m, 0.3, 0.4)
            ang = (i / 6) * 2 * math.pi + self.rnd.uniform(-0.4, 0.4)
            if self.chao:
                ang = math.radians(self.rnd.choice([10, 30, 150, 170, 60, 120]))
            pecas.append((o, ang, ruido, calor, limiar, self.rnd.uniform(.8, 1.2)))

        def f(t):
            for o, ang, ruido, calor, limiar, k in pecas:
                e = 1 - (1 - t) ** 2
                d = self.L * (0.15 + 0.5 * e) * k
                o.location = (math.cos(ang) * d, 0.5, self.chao + math.sin(ang) * d * (0.6 if self.chao else 1))
                s = self.L * (0.1 + 0.16 * e) * k
                o.scale = (s, s, s)
                ruido.inputs["W"].default_value = t * 1.2 + k
                calor.outputs[0].default_value = 0.85 * (1 - t) + 0.2  # fumaça: tons do meio da rampa
                limiar.outputs[0].default_value = max(0.0, t - 0.45) * 1.1
        self.anim.append(f)

    def p_chamas(self):
        """Línguas de fogo: cones com ruído que sobem, balançam e se desfazem pela ponta."""
        pecas = []
        n = 7
        for i in range(n):
            m, ruido, calor, limiar = mat_nuvem(f"chama{i}", 2.6)
            bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=1.0, radius2=0.0, depth=2.0)
            o = bpy.context.active_object
            o.data.materials.append(m)
            o.modifiers.new("sub", "SUBSURF").levels = 2
            tex = bpy.data.textures.new("chama", type="CLOUDS")
            tex.noise_scale = 0.35
            d = o.modifiers.new("desloca", "DISPLACE")
            d.texture = tex
            d.texture_coords = "OBJECT"
            d.strength = 0.35
            bpy.ops.object.shade_smooth()
            x = (i / (n - 1) - 0.5) * (1.1 if self.chao else 0.9)
            pecas.append((o, x, ruido, calor, limiar, self.rnd.uniform(.6, 1.3), self.rnd.uniform(0, 6.28)))

        def f(t):
            for o, x, ruido, calor, limiar, k, fase in pecas:
                sobe = math.sin(min(1.0, t * 1.8) * math.pi / 2)
                altura = self.L * (0.25 + 0.6 * sobe) * k * (1.3 if self.chao else 0.75)
                base = self.chao if self.chao else -self.L * 0.3
                o.location = (x * self.L, 0.2, base + altura * 0.5)
                larg = self.L * 0.09 * (1.2 - 0.6 * t)
                o.scale = (larg, larg, altura * 0.5)
                o.rotation_euler = (0, 0.25 * math.sin(fase + t * 9), 0)
                ruido.inputs["W"].default_value = t * 2.0 + k
                calor.outputs[0].default_value = 2.4 * (1 - t) ** 1.2 + 0.3
                limiar.outputs[0].default_value = max(0.0, t - 0.35) * 1.15
        self.anim.append(f)

    def p_relampago(self):
        mat, emis = mat_luz("relampago")
        raios = []
        for i in range(4):
            ang = (i / 4) * 2 * math.pi + self.rnd.uniform(-0.5, 0.5)
            if self.chao:
                ang = math.radians(self.rnd.uniform(60, 120))
            pts = zigue(self.rnd, 1.0, 7, 0.12)
            o = curva(pts, mat, 0.025)
            raios.append((o, ang))

        def f(t):
            for k, (o, ang) in enumerate(raios):
                vivo = ((int(t * 12) + k) % 3) != 0 and t < 0.85  # pisca, como relâmpago
                o.hide_render = not vivo
                s = self.L * (0.55 + 0.4 * t)
                o.scale = (s, s, s)
                o.location = (0, -1.3, self.chao)
                o.rotation_euler = (0, -ang, 0)
            emis.inputs["Strength"].default_value = 4.0
        self.anim.append(f)

    def p_pilar(self):
        """Coluna de energia que sobe do chão em nuvens empilhadas, abre em cima e se desfaz (a forma trocando)."""
        pecas = []
        n = 7
        for i in range(n):
            m, ruido, calor, limiar = mat_nuvem(f"pilar{i}", 2.0)
            o, d = nuvem_deformada(m, 0.45, 0.45)
            pecas.append((o, i / (n - 1), ruido, calor, limiar, d, self.rnd.uniform(-.12, .12)))

        def f(t):
            for o, h, ruido, calor, limiar, d, dx in pecas:
                atraso = h * 0.25
                u = max(0.0, min(1.0, (t - atraso) / 0.35))
                e = 1 - (1 - u) ** 2
                z = self.chao + self.A * 2 * (0.08 + 0.78 * h) * e
                larg = self.L * (0.26 + 0.22 * h) * (0.6 + 0.4 * e) * (1 + 0.25 * max(0.0, t - 0.5))
                o.location = (dx * self.L, 0.3 + h * 0.1, z)
                o.scale = (larg, larg, larg * 1.25) if u > 0 else (0.0001,) * 3
                d.strength = 0.3 + 0.3 * t
                ruido.inputs["W"].default_value = t * 1.8 + h * 3
                calor.outputs[0].default_value = (3.0 - 1.4 * h) * (1 - t) ** 1.1 + 0.3
                limiar.outputs[0].default_value = max(0.0, t - 0.42 - 0.1 * (1 - h)) * 1.2
        self.anim.append(f)


# ---------------------------------------------------------------------------------------------------------------------
def renderizar(lutador, efeito, amostras, dir_render):
    (larg, alt), n, ticks, chao = EFEITOS[efeito]
    tam = max(larg, alt) / ESCALA_BLENDER          # lado maior em pixels de efeito
    sup = 4                                        # render 4x maior que a arte (a redução limpa o ruído)
    rx, ry = round(larg / ESCALA_BLENDER * sup), round(alt / ESCALA_BLENDER * sup)
    unid = 4.0 * max(larg, alt) / max(larg, alt)
    meia_l = unid / 2 * larg / max(larg, alt)
    meia_a = unid / 2 * alt / max(larg, alt)
    cena = cena_vazia(rx, ry, amostras, unid)
    semente = sum(map(ord, lutador + efeito))
    ef = Efeito(RECEITAS[lutador][efeito], efeito, semente, meia_l, meia_a, chao)
    dir_render.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        ef.quadro(i / (n - 1) * 0.97)
        cena.render.filepath = str(dir_render / f"{i:04d}.png")
        bpy.ops.render.render(write_still=True)
    return [Image.open(dir_render / f"{i:04d}.png").convert("RGBA") for i in range(n)], round(tam), ticks, chao


def paleta(lutador, forma):
    cores = CORES[lutador][forma]
    # contorno: o tom mais escuro da rampa; o resto, do 2º ao mais claro
    return pixelfx.ler_paleta(",".join(cores))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lutadores", nargs="*", default=list(RECEITAS))
    ap.add_argument("--efeitos", nargs="+", default=list(EFEITOS))
    ap.add_argument("--amostras", type=int, default=16)
    a = ap.parse_args()
    import tempfile
    for lutador in a.lutadores:
        for efeito in a.efeitos:
            if efeito not in RECEITAS[lutador]:
                continue
            t0 = time.time()
            with tempfile.TemporaryDirectory() as td:
                quadros, tam, ticks, chao = renderizar(lutador, efeito, a.amostras, Path(td))
                formas = ("desperto",) if efeito == "transformacao" else ("base", "desperto")
                for forma in formas:
                    destino = SAIDA / lutador / f"{efeito}_{forma}"
                    sprites = pixelfx.processar(quadros, destino, paleta(lutador, forma), tam=tam, bloco=1,
                                                previa=False, gama=1.15)
                    for velho in ("folha.png",):
                        (destino / velho).unlink(missing_ok=True)
                    w, h = sprites[0].size
                    pivo = (w // 2, h - 2) if chao else (w // 2, h // 2)
                    (destino / "meta.json").write_text(json.dumps(
                        {"pivo": pivo, "ticks": ticks, "quadros": len(sprites), "efeito": efeito, "forma": forma,
                         "lutador": lutador}, indent=1), encoding="utf-8")
            print(f"{lutador} {efeito}: {len(quadros)} quadros, {tam} px ({time.time() - t0:.0f} s)", flush=True)


if __name__ == "__main__":
    main()
