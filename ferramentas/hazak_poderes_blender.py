#!/usr/bin/env python3
"""Efeitos dos golpes de longe do Hazak e do Diabo Loiro, feitos no Blender (issue #44 do Breno, 2026-11-14).

  bash ferramentas/efeitos_pixel/preparar_nuvem.sh && source ~/.nazafight/ambiente.sh
  "$NAZAFX_PY" ferramentas/hazak_poderes_blender.py              todos (uns 3 min na nuvem)
  "$NAZAFX_PY" ferramentas/hazak_poderes_blender.py ki_bola      só esse

O que sai (sprites/efeitos_blender/hazaki/<efeito>/NN.png + meta.json, ligado no jogo por ferramentas/diabo_loiro.py):
  pedra          a pedra que o Hazak levanta do chão e manda voando (gira, 8 desenhos)
  pedra_quebra   a pedra estourando no oponente: cacos e poeira
  ki_carga       o ki juntando nas mãos (pose de carga): faíscas vindo para o meio e o miolo crescendo
  ki_bola        a bola vermelha de ki em voo, com cauda (laço de 6 desenhos)
  ki_estouro     a bola de ki estourando no acerto
  rajada         a Rajadona de Ki das Trevas do Diabo Loiro: raio enorme e contínuo, preto, vermelho e ouro, com
                 fumaça e faíscas; sai da mão, cresce até atravessar a tela, segura e se desfaz (17 desenhos)
Como os efeitos do efeitos_blender.py (#38): render em cinza, o brilho é a força, e o pixelfx.py põe a rampa de cor,
o contorno seco e o alfa 0/255. A pedra é o único com luz de verdade (sol de cima), porque é objeto, não energia.
"""
import argparse
import json
import math
import random
import sys
import tempfile
import time
from pathlib import Path

import bpy
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI / "efeitos_pixel"))
sys.path.insert(0, str(AQUI))
import pixelfx  # noqa: E402
import efeitos_blender as eb  # noqa: E402
from efeitos import ESCALA_BLENDER  # noqa: E402

SAIDA = eb.SAIDA / "hazaki"

PEDRA = "#241c1a,#4a3c34,#6e5c50,#94806e,#b8a48e,#dccab0"
VERMELHO = "#2a0408,#6a0a10,#b0141a,#e83a26,#ff7a4a,#ffc8a0,#fff4e8"
TREVAS = "#120408,#2a080c,#4e0c10,#8a1610,#cc3a10,#f08a1c,#ffd250,#fff6c8"

# efeito -> (largura, altura em px de jogo, quadros, ticks, pivô "centro"/"esquerda", paleta)
EFEITOS = {
    "pedra": ((26, 26), 8, 2, "centro", PEDRA),
    "pedra_quebra": ((50, 50), 8, 2, "centro", PEDRA),
    "ki_carga": ((44, 44), 10, 2, "centro", VERMELHO),
    "ki_bola": ((40, 28), 6, 2, "bola", VERMELHO),
    "ki_estouro": ((60, 60), 8, 2, "centro", VERMELHO),
    "rajada": ((320, 76), 17, 3, "esquerda", TREVAS),
}


def mat_pedra():
    m = bpy.data.materials.new("pedra")
    if bpy.app.version < (5, 0):
        m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (.55, .55, .55, 1)
    b.inputs["Roughness"].default_value = 1.0
    return m


def sol():
    luz = bpy.data.objects.new("sol", bpy.data.lights.new("sol", "SUN"))
    luz.data.energy = 4.0
    luz.rotation_euler = (math.radians(55), math.radians(-35), 0)
    bpy.context.scene.collection.objects.link(luz)
    bpy.context.scene.world.color = (0.12, 0.12, 0.12)


def pedra_obj(raio, semente):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=raio)
    o = bpy.context.active_object
    o.data.materials.append(mat_pedra())
    tex = bpy.data.textures.new(f"rocha{semente}", type="VORONOI")
    tex.noise_scale = 0.6
    d = o.modifiers.new("desloca", "DISPLACE")
    d.texture = tex
    d.strength = raio * 0.35
    o.scale = (1.15, 0.9, 0.85)
    return o


# ---------------------------------------------------------------------------------------------------------------------
def cena_pedra(n, L, A):
    sol()
    o = pedra_obj(L * 0.62, 1)

    def f(i, t):
        o.rotation_euler = (0.4, -2 * math.pi * i / n, 0.2)
    return f


def cena_pedra_quebra(n, L, A):
    sol()
    rnd = random.Random(7)
    cacos = [(pedra_obj(L * rnd.uniform(.1, .17), k), math.radians(rnd.uniform(-160, 160)), rnd.uniform(.5, .95),
              rnd.uniform(-6, 6)) for k in range(7)]
    ef = eb.Efeito(["fumaca", "miolo"], "especial", 11, L, A, False)

    def f(i, t):
        ef.quadro(t)
        for o, ang, v, giro in cacos:
            d = L * v * t
            o.location = (math.cos(ang) * d, -1.5, math.sin(ang) * d - L * 0.5 * t * t)
            o.rotation_euler = (giro * t, giro * t * .5, 0)
            o.hide_render = t > 0.9
    return f


def cena_ki_carga(n, L, A):
    rnd = random.Random(3)
    m, emis = eb.mat_luz("faisca")
    fag = []
    for k in range(14):
        o = eb.esfera(1.0, 2, m)
        fag.append((o, rnd.uniform(0, 2 * math.pi), rnd.uniform(.75, 1.0), rnd.uniform(0, .5)))
    mc, ruido, calor, limiar = eb.mat_nuvem("miolo", 3.0)
    miolo, d = eb.nuvem_deformada(mc, 0.4, 0.35)

    def f(i, t):
        for o, ang, raio, atraso in fag:
            u = ((t + atraso) % 1.0)
            r = L * raio * (1 - u)
            o.location = (math.cos(ang + u * 1.5) * r, -1.2, math.sin(ang + u * 1.5) * r)
            s = L * 0.045 * (0.5 + u)
            o.scale = (s, s, s)
        s = L * (0.16 + 0.22 * t)
        miolo.scale = (s, s, s)
        ruido.inputs["W"].default_value = t * 3
        calor.outputs[0].default_value = 1.0 + 1.0 * t
        limiar.outputs[0].default_value = 0.0
        emis.inputs["Strength"].default_value = 3.0
    return f


def cena_ki_bola(n, L, A):
    # bola à direita do quadro (o pivô é o centro dela) e a cauda saindo para trás (esquerda)
    mc, ruido, calor, limiar = eb.mat_nuvem("bola", 2.6)
    bola, d = eb.nuvem_deformada(mc, 0.3, 0.4)
    cx = L * 0.38
    bola.location = (cx, 0, 0)
    mt, ruido_t, calor_t, limiar_t = eb.mat_nuvem("cauda", 2.0)
    cauda, dt = eb.nuvem_deformada(mt, 0.35, 0.45)

    def f(i, t):
        s = A * 0.78
        bola.scale = (s, s, s)
        bola.rotation_euler = (0, 2 * math.pi * i / n, 0.6)
        ruido.inputs["W"].default_value = math.sin(2 * math.pi * i / n) * .4
        calor.outputs[0].default_value = 1.7
        limiar.outputs[0].default_value = 0.0
        cauda.location = (cx - L * 0.55, 0.3, 0)
        cauda.scale = (L * 0.55, A * 0.45, A * 0.45)
        cauda.rotation_euler = (2 * math.pi * i / n, 0, 0)
        ruido_t.inputs["W"].default_value = math.cos(2 * math.pi * i / n) * .4
        calor_t.outputs[0].default_value = 0.8
        limiar_t.outputs[0].default_value = 0.25
    return f


def cena_ki_estouro(n, L, A):
    ef = eb.Efeito(["bola", "raios", "brasas"], "especial", 5, L, A, False)
    return lambda i, t: ef.quadro(t)


def cena_rajada(n, L, A):
    """O raio sai da esquerda (a mão) para a direita. Quadros 0-5 crescem, 6-11 seguram (laço), 12-16 se desfazem."""
    rnd = random.Random(13)
    x0 = -L + A * 0.9                                     # centro da bola da mão
    pecas = {}

    def cilindro(nome, calor_base, escala_ruido):
        m, ruido, calor, limiar = eb.mat_nuvem(nome, escala_ruido)
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.0, depth=2.0, rotation=(0, math.radians(90), 0))
        o = bpy.context.active_object
        bpy.ops.object.transform_apply(rotation=True)
        o.data.materials.append(m)
        sub = o.modifiers.new("sub", "SUBSURF")
        sub.levels = 2
        tex = bpy.data.textures.new(nome, type="CLOUDS")
        tex.noise_scale = 0.3
        dsp = o.modifiers.new("desloca", "DISPLACE")
        dsp.texture = tex
        dsp.texture_coords = "OBJECT"
        dsp.strength = 0.12
        pecas[nome] = (o, ruido, calor, limiar, calor_base)
        return o

    miolo = cilindro("miolo", 2.0, 3.0)
    casca = cilindro("casca", 0.7, 2.2)
    fumaca = cilindro("fumaca", 0.3, 1.6)
    mb, rb, cb, lb = eb.mat_nuvem("boca", 2.4)
    boca, db = eb.nuvem_deformada(mb, 0.4, 0.4)
    mp, rp, cp, lp = eb.mat_nuvem("ponta", 2.4)
    ponta, dp = eb.nuvem_deformada(mp, 0.5, 0.35)
    mf, emis = eb.mat_luz("faiscas")
    faiscas = []
    for k in range(26):
        bpy.ops.mesh.primitive_cube_add(size=1)
        o = bpy.context.active_object
        o.data.materials.append(mf)
        faiscas.append(o)

    def f(i, t):
        if i <= 5:
            comp, forca = (i + 1) / 6, 1.0
        elif i <= 11:
            comp, forca = 1.0, 1.0
        else:
            comp, forca = 1.0, 1 - (i - 11) / 6
        fim = x0 + (L - x0 - A * 0.62) * comp
        meio, meia = (x0 + fim) / 2, max(0.01, (fim - x0) / 2)
        raio = A * 0.5 * (0.55 + 0.45 * forca)
        pulso = 1 + 0.08 * math.sin(i * 2.1)
        for nome, k_raio in (("miolo", 0.45), ("casca", 0.8), ("fumaca", 1.35)):
            o, ruido, calor, limiar, c0 = pecas[nome]
            o.location = (meio, {"miolo": -0.6, "casca": 0.0, "fumaca": 0.6}[nome], 0)
            o.scale = (meia, raio * k_raio * pulso, raio * k_raio * pulso)
            ruido.inputs["W"].default_value = i * 0.37 + len(nome)
            calor.outputs[0].default_value = c0 * (0.35 + 0.65 * forca)
            limiar.outputs[0].default_value = {"miolo": 0.0, "casca": 0.18, "fumaca": 0.42}[nome] + (1 - forca) * 0.5
            o.hide_render = forca <= 0.05
        s = A * 0.62 * pulso * (0.6 + 0.4 * forca)
        boca.location = (x0, -0.8, 0)
        boca.scale = (s, s, s)
        boca.rotation_euler = (i * 0.9, 0, 0)
        rb.inputs["W"].default_value = i * 0.3
        cb.outputs[0].default_value = 1.9 * forca + 0.15
        lb.outputs[0].default_value = (1 - forca) * 0.6
        sp = A * 0.5 * (0.7 + 0.3 * math.sin(i * 1.7) ** 2) * forca
        ponta.location = (fim, -0.8, 0)
        ponta.scale = (sp, sp * 1.1, sp * 1.1)
        rp.inputs["W"].default_value = i * 0.41
        cp.outputs[0].default_value = 1.6 * forca
        lp.outputs[0].default_value = 0.1 + (1 - forca) * 0.6
        ponta.hide_render = forca <= 0.05
        r2 = random.Random(100 + i)
        for o in faiscas:
            x = r2.uniform(x0, fim)
            z = r2.choice((-1, 1)) * raio * r2.uniform(0.9, 1.5)
            o.location = (x, -1.4, z)
            ang = r2.uniform(-0.7, 0.7)
            tam = A * r2.uniform(0.03, 0.06)
            o.rotation_euler = (0, ang, 0)
            o.scale = (tam * 4, tam * 0.4, tam * 0.7)
            o.hide_render = forca < 0.3 and r2.random() < 0.6
        emis.inputs["Strength"].default_value = 2.5
    return f


GAMA = {"ki_bola": 1.5, "ki_carga": 1.3, "ki_estouro": 1.4, "rajada": 1.35}  # >1 puxa para o vermelho e o escuro
CENAS = {"pedra": cena_pedra, "pedra_quebra": cena_pedra_quebra, "ki_carga": cena_ki_carga, "ki_bola": cena_ki_bola,
         "ki_estouro": cena_ki_estouro, "rajada": cena_rajada}


def renderizar(efeito, amostras, pasta):
    (larg, alt), n, ticks, pivo, cores = EFEITOS[efeito]
    sup = 4
    rx, ry = round(larg / ESCALA_BLENDER * sup), round(alt / ESCALA_BLENDER * sup)
    unid = 4.0
    L = unid / 2 * larg / max(larg, alt)
    A = unid / 2 * alt / max(larg, alt)
    cena = eb.cena_vazia(rx, ry, amostras, unid)
    f = CENAS[efeito](n, L, A)
    quadros = []
    for i in range(n):
        f(i, i / max(1, n - 1) * 0.97)
        cena.render.filepath = str(pasta / f"{i:04d}.png")
        bpy.ops.render.render(write_still=True)
        quadros.append(Image.open(pasta / f"{i:04d}.png").convert("RGBA"))
    return quadros, round(max(larg, alt) / ESCALA_BLENDER), ticks, pivo, cores


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("efeitos", nargs="*", default=list(EFEITOS))
    ap.add_argument("--amostras", type=int, default=16)
    a = ap.parse_args()
    for efeito in a.efeitos:
        t0 = time.time()
        with tempfile.TemporaryDirectory() as td:
            quadros, tam, ticks, pivo, cores = renderizar(efeito, a.amostras, Path(td))
            destino = SAIDA / efeito
            sprites = pixelfx.processar(quadros, destino, pixelfx.ler_paleta(cores), tam=tam, bloco=1, previa=False,
                                        gama=GAMA.get(efeito, 1.1))
            (destino / "folha.png").unlink(missing_ok=True)
            w, h = sprites[0].size
            px = {"centro": (w // 2, h // 2), "esquerda": (round(h * 0.45), h // 2),
                  "bola": (round(w * 0.88), h // 2)}[pivo]
            (destino / "meta.json").write_text(json.dumps(
                {"pivo": px, "ticks": ticks, "quadros": len(sprites), "efeito": efeito, "lutador": "hazaki",
                 "feito_por": "ferramentas/hazak_poderes_blender.py"}, indent=1), encoding="utf-8")
        print(f"{efeito}: {len(quadros)} quadros, {tam} px ({time.time() - t0:.0f} s)", flush=True)


if __name__ == "__main__":
    main()
