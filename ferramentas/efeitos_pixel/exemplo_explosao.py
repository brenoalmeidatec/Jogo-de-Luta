#!/usr/bin/env python3
"""Exemplo mínimo de efeito no Blender virando sprite: uma explosão com faíscas, 8 quadros, fundo transparente.

Roda com o Python que tem o bpy (preparado por preparar_nuvem.sh), sem tela e sem abrir o Blender:

  source ~/.nazafight/ambiente.sh
  "$NAZAFX_PY" ferramentas/efeitos_pixel/exemplo_explosao.py                 saída em ferramentas/efeitos_pixel/saida/
  "$NAZAFX_PY" ferramentas/efeitos_pixel/exemplo_explosao.py --paletas fogo violeta eletrico --tam 64

Passos: (1) monta a cena por código (bola de fogo com ruído que se desfaz + faíscas em arco), (2) renderiza em Cycles
na CPU, em tons de cinza e 4x maior que a arte, (3) passa os quadros pelo pixelfx.py em cada paleta. A mesma
renderização serve para todas as cores, que é como um efeito é reaproveitado entre lutadores
(regra-efeitos-proporcionais.md). Tudo é determinístico: mesma semente, mesmos quadros.
"""
import argparse
import math
import random
import sys
import time
from pathlib import Path

import bpy
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import pixelfx  # noqa: E402


# ---------------------------------------------------------------------------------------------------------------------
# cena
# ---------------------------------------------------------------------------------------------------------------------
def no(arvore, tipo, **props):
    n = arvore.nodes.new(tipo)
    for k, v in props.items():
        setattr(n, k, v)
    return n


def material_fogo():
    """Emissão em cinza: claro no miolo, escuro na borda, com ruído; o 'limiar' abre buracos para a bola se desfazer."""
    m = bpy.data.materials.new("fogo")
    if bpy.app.version < (5, 0):
        m.use_nodes = True
    t = m.node_tree
    t.nodes.clear()
    L = t.links.new
    coord = no(t, "ShaderNodeTexCoord")
    ruido = no(t, "ShaderNodeTexNoise", noise_dimensions="4D")
    ruido.inputs["Scale"].default_value = 2.2
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
    calor = no(t, "ShaderNodeValue", name="calor", label="calor")
    forca = no(t, "ShaderNodeMath", operation="MULTIPLY")
    L(mist.outputs[0], forca.inputs[0])
    L(calor.outputs[0], forca.inputs[1])
    emis = no(t, "ShaderNodeEmission")
    emis.inputs["Color"].default_value = (1, 1, 1, 1)
    L(forca.outputs[0], emis.inputs["Strength"])
    limiar = no(t, "ShaderNodeValue", name="limiar", label="limiar")
    corte = no(t, "ShaderNodeMath", operation="GREATER_THAN")
    L(ruido.outputs["Fac"], corte.inputs[0])
    L(limiar.outputs[0], corte.inputs[1])
    mix = no(t, "ShaderNodeMixShader")
    L(corte.outputs[0], mix.inputs["Fac"])
    L(no(t, "ShaderNodeBsdfTransparent").outputs[0], mix.inputs[1])
    L(emis.outputs[0], mix.inputs[2])
    saida = no(t, "ShaderNodeOutputMaterial")
    L(mix.outputs[0], saida.inputs["Surface"])
    return m, ruido, t.nodes["calor"], t.nodes["limiar"]


def material_faisca():
    m = bpy.data.materials.new("faisca")
    if bpy.app.version < (5, 0):
        m.use_nodes = True
    t = m.node_tree
    t.nodes.clear()
    emis = no(t, "ShaderNodeEmission")
    emis.inputs["Color"].default_value = (1, 1, 1, 1)
    emis.inputs["Strength"].default_value = 4.0
    t.links.new(emis.outputs[0], no(t, "ShaderNodeOutputMaterial").inputs["Surface"])
    return m


def montar_cena(res, amostras, semente):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cena = bpy.context.scene
    r = cena.render
    r.engine = "CYCLES"
    cena.cycles.device = "CPU"
    cena.cycles.samples = amostras
    cena.cycles.use_denoising = False          # a redução 4x já limpa o ruído
    r.resolution_x = r.resolution_y = res
    r.resolution_percentage = 100
    r.film_transparent = True
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGBA"
    cena.view_settings.view_transform = "Standard"   # brilho do render = brilho que escolhe a cor da rampa
    cena.world = bpy.data.worlds.new("vazio")
    cena.world.color = (0, 0, 0)

    cam = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 4.4
    cam.location = (0, -10, 0)
    cam.rotation_euler = (math.radians(90), 0, 0)
    cena.collection.objects.link(cam)
    cena.camera = cam

    mat, ruido, calor, limiar = material_fogo()
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=1.0)
    bola = bpy.context.active_object
    bola.data.materials.append(mat)
    tex = bpy.data.textures.new("nuvem", type="CLOUDS")
    tex.noise_scale = 0.55
    desloc = bola.modifiers.new("desloca", "DISPLACE")
    desloc.texture = tex
    desloc.texture_coords = "OBJECT"
    bpy.ops.object.shade_smooth()

    rnd = random.Random(semente)
    mat_f = material_faisca()
    faiscas = []
    for i in range(10):
        ang = (i / 10) * 2 * math.pi + rnd.uniform(-0.2, 0.2)
        vel = rnd.uniform(1.3, 2.1)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=1.0)
        f = bpy.context.active_object
        f.data.materials.append(mat_f)
        faiscas.append((f, ang, vel))
    return bola, desloc, ruido, calor, limiar, faiscas


def animar(t, bola, desloc, ruido, calor, limiar, faiscas):
    """t vai de 0 (contato) a 1 (sumiu). Nada aleatório por quadro: tudo é função de t."""
    e = 1 - (1 - t) ** 2
    s = 0.3 + 1.15 * e
    bola.scale = (s, s, s * 0.92)
    desloc.strength = 0.15 + 0.35 * e
    ruido.inputs["W"].default_value = t * 1.5
    calor.outputs[0].default_value = 2.6 * (1 - t) ** 1.8 + 0.3
    limiar.outputs[0].default_value = max(0.0, t - 0.4) * 0.95
    for f, ang, vel in faiscas:
        d = 0.55 + vel * (t * 1.25)
        x, z = math.cos(ang) * d, math.sin(ang) * d - 0.9 * t * t
        vx, vz = math.cos(ang) * vel, math.sin(ang) * vel - 1.8 * t
        f.location = (x, -1.5, z)                 # na frente da bola
        f.rotation_euler = (0, -math.atan2(vz, vx), 0)
        k = max(0.0, 1 - t * 1.25)
        f.scale = (0.08 + 0.3 * k, 0.1 * k + 0.001, 0.1 * k + 0.001)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saida", default=str(AQUI / "saida"))
    ap.add_argument("--quadros", type=int, default=8)
    ap.add_argument("--tam", type=int, default=48, help="lado da arte em pixels de jogo")
    ap.add_argument("--bloco", type=int, default=3, help="ampliação final (3 = padrão 3x do projeto)")
    ap.add_argument("--amostras", type=int, default=24)
    ap.add_argument("--semente", type=int, default=7)
    ap.add_argument("--paletas", nargs="+", default=["fogo", "violeta"])
    a = ap.parse_args()

    saida = Path(a.saida)
    bruto = saida / "render"
    bruto.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    pecas = montar_cena(a.tam * 4, a.amostras, a.semente)
    cena = bpy.context.scene
    for i in range(a.quadros):
        animar(i / (a.quadros - 1), *pecas)
        cena.render.filepath = str(bruto / f"{i:04d}.png")
        bpy.ops.render.render(write_still=True)
    print(f"render: {a.quadros} quadros {a.tam * 4}px em {time.time() - t0:.1f} s (bpy {bpy.app.version_string})")

    quadros = [Image.open(p).convert("RGBA") for p in sorted(bruto.glob("*.png"))]
    linhas = []
    for nome in a.paletas:
        sprites = pixelfx.processar(quadros, saida / f"explosao_{nome}", pixelfx.ler_paleta(nome),
                                    tam=a.tam, bloco=a.bloco)
        linhas.append(sprites)
        print(f"pixel: explosao_{nome}/ ({len(sprites)} quadros {sprites[0].width}x{sprites[0].height})")

    # comparação: render bruto em cima, uma linha por paleta embaixo, fundo escuro
    w, h = linhas[0][0].size
    folha = Image.new("RGBA", (w * a.quadros, h * (1 + len(linhas))), (34, 30, 46, 255))
    for i, q in enumerate(quadros):
        folha.alpha_composite(q.resize((w, h), Image.LANCZOS), (i * w, 0))
    for j, sprites in enumerate(linhas, 1):
        for i, s in enumerate(sprites):
            folha.alpha_composite(s, (i * w, j * h))
    folha.convert("RGB").save(saida / "comparacao.png")
    print(f"comparação: {saida / 'comparacao.png'} ({time.time() - t0:.1f} s no total)")


if __name__ == "__main__":
    main()
