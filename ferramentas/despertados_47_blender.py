#!/usr/bin/env python3
"""Efeitos do agarrão e do poder de longe de cada forma despertada (issue #47 do Breno, 2026-11-14), no Blender.

  bash ferramentas/efeitos_pixel/preparar_nuvem.sh && source ~/.nazafight/ambiente.sh
  "$NAZAFX_PY" ferramentas/despertados_47_blender.py                 Pengaró, Gutto e CK (uns 3 min na nuvem)
  "$NAZAFX_PY" ferramentas/despertados_47_blender.py gutto --efeitos poder

Mesmo caminho dos efeitos da #38 (ferramentas/efeitos_blender.py, de onde vêm a cena, os materiais e as peças): o
render sai em cinza, o brilho é a força, e o ferramentas/efeitos_pixel/pixelfx.py passa para pixel art na rampa da
forma (CORES em ferramentas/efeitos.py). Nada do ChatGPT. O Hazak (Diabo Loiro) e o Raiclaven (Cientista Louco) têm
os deles nas issues #44 e #43.

Quatro efeitos por lutador, todos com o tema da forma:
  agarrao   preso no oponente enquanto ele apanha (laço no fim): correntes de sombra subindo e enrolando (Pengaró),
            raios caindo em cima dele (Gutto), caixas de som estourando nele (CK)
  final     o golpe que solta: estouro com elos voando, ferraduras de raio ou estrondo de som
  poder     o projétil do poder de longe (laço): maré de sombra com correntes, garanhão de raio galopando, paredão de som
  carga     brilho na mão antes de soltar o poder

Saída (vai para o git; é o que ferramentas/despertados_47.py liga no jogo):
  sprites/efeitos_blender/<lutador>/d47_<efeito>/NN.png + meta.json (pivô, ticks, loop)
"""
import argparse
import json
import math
import sys
import tempfile
import time
from pathlib import Path

import bpy
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI / "efeitos_pixel"))
import efeitos_blender as eb  # noqa: E402
import pixelfx  # noqa: E402
from efeitos import CORES, ESCALA_BLENDER  # noqa: E402

SAIDA = eb.SAIDA
LUTADORES = ("pengaro", "gutto", "ck")
# rampa de cada lutador: o Gutto despertado é vermelho com miolo branco (aura do garanhão, bosses_kit.md)
FORMA = {"pengaro": "desperto", "gutto": "base", "ck": "desperto"}

# efeito -> (largura, altura no jogo), quadros, ticks por quadro, pivô no chão?, quadro onde o laço começa (-1 = sem laço)
EFEITOS = {
    "pengaro": {"agarrao": ((110, 170), 12, 3, True, 6), "final": ((170, 170), 12, 3, False, -1),
                "poder": ((150, 120), 12, 2, False, 0), "carga": ((84, 84), 10, 2, False, -1)},
    "gutto": {"agarrao": ((96, 190), 12, 2, True, 0), "final": ((170, 170), 12, 3, False, -1),
              "carga": ((84, 84), 10, 2, False, -1)},   # o poder do Gutto é a aura (compor_garanhao)
    "ck": {"agarrao": ((130, 150), 12, 2, False, 0), "final": ((180, 180), 12, 3, False, -1),
           "poder": ((120, 190), 12, 2, False, 0), "carga": ((84, 84), 10, 2, False, -1)},
}
# padrão novo do Breno (#47, 2026-11-14): poder grande e pesado, com rastro atrás (fantasmas do próprio desenho)
RASTRO = {"poder": (0.55, 3)}     # efeito -> (largura extra atrás, em fração da largura; quantos fantasmas)


def tau(t):
    return 2 * math.pi * t


class Efeito47(eb.Efeito):
    """As peças novas; `quadro(t)` com t de 0 a 1. Nos efeitos em laço, t = 1 é igual a t = 0."""

    def __init__(self, receita, semente, meia_l, meia_a, chao):
        super().__init__([], "super", semente, meia_l, meia_a, chao)
        for p in receita:
            getattr(self, "p_" + p)()

    # ------------------------------------------------------------------ Pengaró: sombra e corrente
    def _elo(self, mat, grossura=0.22):
        bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=grossura, major_segments=20, minor_segments=6)
        o = bpy.context.active_object
        o.data.materials.append(mat)
        return o

    def p_correntes_sobem(self):
        """Três correntes de sombra saem do chão em espiral e enrolam o oponente; depois giram devagar (laço)."""
        mat, emis = eb.mat_luz("elo")
        n_elos, voltas = 26, 1.6
        cadeias = []
        for c in range(3):
            elos = [self._elo(mat) for _ in range(n_elos)]
            cadeias.append((c, elos))
        laco = EFEITOS["pengaro"]["agarrao"][4] / EFEITOS["pengaro"]["agarrao"][1]
        altura = self.A * 2 * 0.86
        raio = self.L * 0.62

        def f(t):
            sobe = min(1.0, t / laco)                  # 0 -> 1 na subida; 1 no laço
            giro = 0.0 if t < laco else (t - laco) / (1 - laco) * tau(1 / 3)  # 1/3 de volta: 3 correntes iguais
            for c, elos in cadeias:
                for k, o in enumerate(elos):
                    h = k / (n_elos - 1)
                    vivo = h <= sobe * 1.02
                    a = tau(c / 3) + h * tau(voltas) + giro
                    r = raio * (1.0 - 0.25 * h)
                    x, prof = math.cos(a) * r, math.sin(a) * r
                    o.location = (x, prof, self.chao + altura * h)
                    s = self.L * 0.1
                    o.scale = (s, s, s)
                    # elo alterna de lado, como corrente de verdade; segue a tangente da espiral
                    o.rotation_euler = (math.radians(90 if k % 2 else 0), math.radians(35), a)
                    o.hide_render = not vivo
            emis.inputs["Strength"].default_value = 0.8
        self.anim.append(f)

    def p_sombra_chao(self):
        """Poça de sombra no pé do oponente, viva (laço pela fase)."""
        pecas = []
        for i in range(5):
            m, ruido, calor, limiar = eb.mat_nuvem(f"poca{i}", 2.6)
            o, d = eb.nuvem_deformada(m, 0.3, 0.4)
            pecas.append((o, i, ruido, calor, limiar))

        def f(t):
            for o, i, ruido, calor, limiar in pecas:
                a = tau(i / 5) + tau(t) / 5 * (1 if i % 2 else -1)
                o.location = (math.cos(a) * self.L * 0.55, 0.8, self.chao + 0.05)
                s = self.L * (0.2 + 0.04 * math.sin(tau(t) + i))
                o.scale = (s * 1.4, s, s * 0.45)
                ruido.inputs["W"].default_value = 0.3 * math.sin(tau(t)) + i
                calor.outputs[0].default_value = 0.8
                limiar.outputs[0].default_value = 0.0
        self.anim.append(f)

    def p_elos_voando(self):
        mat, emis = eb.mat_luz("elo_voa")
        pecas = []
        for i in range(10):
            o = self._elo(mat, 0.25)
            ang = tau(i / 10) + self.rnd.uniform(-0.25, 0.25)
            pecas.append((o, ang, self.rnd.uniform(0.55, 1.0), self.rnd.uniform(-9, 9)))

        def f(t):
            for o, ang, v, giro in pecas:
                d = self.L * v * t
                o.location = (math.cos(ang) * d, -1.2, math.sin(ang) * d - self.L * 0.4 * t * t)
                s = self.L * 0.11 * max(0.0, 1 - t * 0.9)
                o.scale = (s, s, s)
                o.rotation_euler = (giro * t, 1.0, giro * t * 0.5)
                o.hide_render = t > 0.92
            emis.inputs["Strength"].default_value = 2.6 * (1 - 0.5 * t)
        self.anim.append(f)

    def p_mare(self):
        """Maré de sombra rolando para a frente: roda de nuvens (laço exato: cada nuvem vai para o lugar da próxima)."""
        n = 7
        pecas = []
        m, ruido, calor, limiar = eb.mat_nuvem("mare", 2.4)
        for i in range(n):
            o, d = eb.nuvem_deformada(m, 0.32, 0.5)
            pecas.append(o)
        calor.outputs[0].default_value = 1.05
        limiar.outputs[0].default_value = 0.0
        miolo, dm = eb.nuvem_deformada(m, 0.3, 0.5)

        def f(t):
            miolo.location = (-self.L * 0.1, 0.5, 0)
            sm = self.A * 0.5
            miolo.scale = (sm * 1.3, sm, sm)
            miolo.rotation_euler = (0, -tau(t / n), 0)
            for i, o in enumerate(pecas):
                a = tau((i + t) / n)                    # rola: a frente desce, a de trás sobe
                rx, rz = self.L * 0.42, self.A * 0.52
                x = -math.sin(a) * rx - self.L * 0.12
                z = math.cos(a) * rz * 0.9
                o.location = (x, 0.3, z)
                frente = 0.5 + 0.5 * math.cos(a - math.pi / 2)
                s = self.A * (0.34 + 0.12 * frente)
                o.scale = (s * 1.15, s, s)
                o.rotation_euler = (0, -a, 0)
        self.anim.append(f)

    def p_correntes_chicote(self):
        """Duas correntes chicoteando na frente da maré (onda que corre pelo elo; laço pela fase)."""
        mat, emis = eb.mat_luz("chicote")
        cadeias = [[self._elo(mat) for _ in range(9)] for _ in range(2)]

        def f(t):
            for c, elos in enumerate(cadeias):
                for k, o in enumerate(elos):
                    h = k / (len(elos) - 1)
                    x = -self.L * 0.2 + h * self.L * 1.12
                    z = (0.28 if c else -0.3) * self.A + math.sin(tau(t) * (1 if c else -1) + h * 5.5 + c) * self.A * 0.18 * h
                    o.location = (x, -1.0, z)
                    s = self.L * 0.085 * (1.1 - 0.4 * h)
                    o.scale = (s, s, s)
                    o.rotation_euler = (math.radians(90 if k % 2 else 0), 0, 0)
            emis.inputs["Strength"].default_value = 2.4
        self.anim.append(f)

    def p_converge(self):
        """Carga: fagulhas entrando no punho e uma bola pequena crescendo."""
        mat, emis = eb.mat_luz("converge")
        pecas = []
        for i in range(12):
            o = eb.esfera(1.0, 2, mat)
            pecas.append((o, tau(i / 12) + self.rnd.uniform(-0.2, 0.2), self.rnd.uniform(0.75, 1.0)))
        m, ruido, calor, limiar = eb.mat_nuvem("miolo_carga", 3.0)
        bola, d = eb.nuvem_deformada(m, 0.35, 0.35)

        def f(t):
            for o, ang, k in pecas:
                d_ = self.L * 0.9 * k * (1 - t)
                o.location = (math.cos(ang + t * 2) * d_, -1.2, math.sin(ang + t * 2) * d_)
                s = self.L * 0.05 * (0.5 + t)
                o.scale = (s * (2.4 - t), s, s)
                o.rotation_euler = (0, -(ang + t * 2), 0)
                o.hide_render = t > 0.9
            s = self.L * (0.1 + 0.32 * t)
            bola.scale = (s, s, s)
            ruido.inputs["W"].default_value = t * 2
            calor.outputs[0].default_value = 1.2 + 2.5 * t
            limiar.outputs[0].default_value = 0.0
            emis.inputs["Strength"].default_value = 3.0
        self.anim.append(f)

    # ------------------------------------------------------------------ Gutto: raio e cavalo
    def p_raios_caindo(self):
        """Raios caindo do alto em cima do oponente, piscando (laço: o pisca tem período de 12 quadros)."""
        mat, emis = eb.mat_luz("raio_cai")
        raios = []
        for i in range(5):
            pts = eb.zigue(self.rnd, 1.0, 9, 0.06)
            o = eb.curva(pts, mat, 0.006 if i else 0.011)
            raios.append((o, (i - 2) * 0.22 + self.rnd.uniform(-0.06, 0.06), i))

        def f(t):
            q = round(t * 12) % 12
            for o, dx, i in raios:
                o.hide_render = ((q + i * 5) % 4) == 3 if i else (q % 6 == 5)
                o.location = (dx * self.L, -1.3, self.chao + self.A * 2 * 0.98)
                o.rotation_euler = (0, math.radians(90 + dx * 25), 0)   # de cima para o chão
                s = self.A * 2 * 0.98
                o.scale = (s, s, s)
            emis.inputs["Strength"].default_value = 4.5
        self.anim.append(f)

    def p_brilho_chao(self):
        m, emis = eb.mat_luz("brilho_chao")
        o = eb.anel_obj(m, 1.0, 0.1)

        def f(t):
            s = self.L * (0.62 + 0.08 * math.sin(tau(t) * 2))
            o.location = (0, -0.6, self.chao + 0.04)
            o.scale = (s, s * 0.2, s)
            emis.inputs["Strength"].default_value = 3.0
        self.anim.append(f)

    def p_ferraduras(self):
        """Ferraduras de raio voando do coice (meia-argola grossa, girando)."""
        mat, emis = eb.mat_luz("ferradura")
        pecas = []
        for i in range(7):
            bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.26, major_segments=24, minor_segments=6)
            o = bpy.context.active_object
            o.data.materials.append(mat)
            # corta a argola: apaga a quarta parte de baixo (fica o U da ferradura)
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.object.mode_set(mode="OBJECT")
            for v in o.data.vertices:
                v.select = v.co.y < -0.55
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.delete(type="VERT")
            bpy.ops.object.mode_set(mode="OBJECT")
            ang = tau(i / 7) + self.rnd.uniform(-0.3, 0.3)
            pecas.append((o, ang, self.rnd.uniform(0.55, 0.95), self.rnd.uniform(-8, 8)))

        def f(t):
            for o, ang, v, giro in pecas:
                d = self.L * v * t
                o.location = (math.cos(ang) * d, -1.3, math.sin(ang) * d - self.L * 0.35 * t * t)
                s = self.L * 0.085 * max(0.0, 1 - t * 0.85)
                o.scale = (s, s, s)
                o.rotation_euler = (math.radians(90), giro * t, 0)
                o.hide_render = t > 0.92
            emis.inputs["Strength"].default_value = 3.6 * (1 - 0.4 * t)
        self.anim.append(f)

    def p_garanhao(self):
        """Garanhão de raio galopando para a frente (+x). Corpo de peças simples, energia com ruído; o galope é um
        ciclo de 8 quadros (pernas, pescoço e crina pela fase, laço exato)."""
        m, ruido, calor, limiar = eb.mat_nuvem("garanhao", 3.4)
        calor.outputs[0].default_value = 1.5
        limiar.outputs[0].default_value = 0.0
        U = self.A * 0.9                                   # medida do cavalo (altura do lombo ~ U)

        def peca(raio, esc, sub=3):
            o = eb.esfera(raio, sub, m)
            o.scale = esc
            return o

        corpo = peca(1.0, (U * 0.62, U * 0.3, U * 0.3))
        peito = peca(1.0, (U * 0.3, U * 0.28, U * 0.32))
        anca = peca(1.0, (U * 0.3, U * 0.28, U * 0.32))
        pescoco = peca(1.0, (U * 0.15, U * 0.15, U * 0.38))
        cabeca = peca(1.0, (U * 0.3, U * 0.13, U * 0.13))
        crina = [peca(1.0, (U * 0.1, U * 0.06, U * 0.16)) for _ in range(5)]
        rabo = [peca(1.0, (U * 0.12, U * 0.07, U * 0.07)) for _ in range(5)]
        # perna = coxa + canela + casco
        pernas = []
        for k in range(4):
            coxa = peca(1.0, (U * 0.08, U * 0.08, U * 0.25))
            canela = peca(1.0, (U * 0.055, U * 0.055, U * 0.24))
            casco = peca(1.0, (U * 0.07, U * 0.07, U * 0.05))
            pernas.append((coxa, canela, casco, k))
        mat_r, emis_r = eb.mat_luz("raio_cavalo")
        raios = []
        for i in range(4):
            o = eb.curva(eb.zigue(self.rnd, 1.0, 7, 0.14), mat_r, 0.022)
            raios.append((o, i))
        emis_r.inputs["Strength"].default_value = 4.5

        def junta(o, base, ang, comp):
            """Põe o osso (elipse de altura 2*comp no z) pendurado de `base`, girado `ang` no plano x-z."""
            cx = base[0] + math.sin(ang) * comp
            cz = base[1] - math.cos(ang) * comp
            o.location = (cx, 0, cz)
            o.rotation_euler = (0, -ang, 0)   # giro em y do Blender: +ang levaria o pé para trás
            return (base[0] + math.sin(ang) * 2 * comp, base[1] - math.cos(ang) * 2 * comp)

        def f(t):
            fase = tau(t)
            sobe = math.sin(fase * 2) * U * 0.05          # o corpo sobe duas vezes por passada
            z0 = -self.A * 0.05 + sobe
            inclina = math.sin(fase) * 0.06
            corpo.location = (0, 0, z0)
            corpo.rotation_euler = (0, inclina, 0)
            peito.location = (U * 0.45, 0, z0 + U * 0.04)
            anca.location = (-U * 0.45, 0, z0 + U * 0.02)
            ombro = (U * 0.5, z0 + U * 0.2)
            pescoco.location = (U * 0.78, 0, z0 + U * 0.42 + math.sin(fase) * U * 0.03)
            pescoco.rotation_euler = (0, math.radians(38) + math.sin(fase) * 0.12, 0)
            cabeca.location = (U * 1.08, 0, z0 + U * 0.62 + math.sin(fase) * U * 0.04)
            cabeca.rotation_euler = (0, math.radians(30) + math.sin(fase) * 0.1, 0)
            for i, o in enumerate(crina):
                h = i / 4
                o.location = (U * (0.95 - 0.3 * h) - math.sin(fase + h * 3) * U * 0.04, 0.1,
                              z0 + U * (0.7 - 0.38 * h) + math.cos(fase + h * 3) * U * 0.04)
                o.rotation_euler = (0, math.radians(-40) + math.sin(fase + h * 2) * 0.4, 0)
            for i, o in enumerate(rabo):
                h = i / 4
                o.location = (-U * (0.72 + 0.32 * h), 0.1, z0 + U * (0.18 - 0.1 * h) + math.sin(fase * 2 + h * 3) * U * 0.08 * h)
                o.rotation_euler = (0, math.radians(-20) + math.sin(fase * 2 + h * 2) * 0.35, 0)
            # galope: dianteiras e traseiras fora de fase, cada par com um pequeno atraso
            for coxa, canela, casco, k in pernas:
                frente = k < 2
                atraso = (0.0 if k % 2 == 0 else 0.12) + (0.0 if frente else 0.5)
                a = fase + tau(atraso)
                quadril = (U * (0.48 if frente else -0.48) + (0.04 if k % 2 else 0) * U, z0 - U * 0.05)
                ang_coxa = 0.55 * math.sin(a)
                joelho = junta(coxa, quadril, ang_coxa, U * 0.23)
                dobra = (0.9 if frente else -0.7) * max(0.0, math.sin(a + 1.2))
                pe = junta(canela, joelho, ang_coxa + dobra, U * 0.22)
                casco.location = (pe[0], 0, pe[1])
                for o in (coxa, canela, casco):
                    o.location = (o.location[0], 0.25 if k % 2 else -0.25, o.location[2])
            for o, i in raios:
                o.hide_render = ((round(t * 8) + i) % 3) == 2
                o.location = (U * (0.6 - 0.45 * i), -1.4, z0 + U * (0.25 if i % 2 else -0.05))
                o.rotation_euler = (0, math.radians(160 + 25 * i + (180 if i % 2 else 0)), 0)
                s = U * 0.55
                o.scale = (s, s, s)
            ruido.inputs["W"].default_value = 0.35 * math.sin(fase) + 0.35 * math.cos(fase)
        self.anim.append(f)

    def p_crepita(self):
        """Carga do Gutto: raios curtos estalando em volta do punho."""
        mat, emis = eb.mat_luz("crepita")
        raios = []
        for i in range(6):
            o = eb.curva(eb.zigue(self.rnd, 1.0, 5, 0.16), mat, 0.03)
            raios.append((o, tau(i / 6) + self.rnd.uniform(-0.3, 0.3), i))
        m, ruido, calor, limiar = eb.mat_nuvem("miolo_crepita", 3.0)
        bola, d = eb.nuvem_deformada(m, 0.35, 0.35)

        def f(t):
            for o, ang, i in raios:
                o.hide_render = ((round(t * 8) + i) % 3) == 0
                o.location = (math.cos(ang) * self.L * 0.15, -1.3, math.sin(ang) * self.L * 0.15)
                o.rotation_euler = (0, -ang, 0)
                s = self.L * (0.5 + 0.25 * t)
                o.scale = (s, s, s)
            s = self.L * (0.14 + 0.24 * t)
            bola.scale = (s, s, s)
            ruido.inputs["W"].default_value = t * 2
            calor.outputs[0].default_value = 1.5 + 2.5 * t
            limiar.outputs[0].default_value = 0.0
            emis.inputs["Strength"].default_value = 4.0
        self.anim.append(f)

    # ------------------------------------------------------------------ CK: paredão de som
    def _anel_som(self, m, grossura):
        o = eb.anel_obj(m, 1.0, grossura)
        tex = bpy.data.textures.new("som", type="CLOUDS")
        tex.noise_scale = 0.3
        d = o.modifiers.new("desloca", "DISPLACE")
        d.texture = tex
        d.texture_coords = "OBJECT"
        d.strength = 0.06
        return o

    def p_som_pulsa(self):
        """Anéis de som saindo do oponente sem parar (cada anel na fase seguinte: laço exato)."""
        m, ruido, calor, limiar = eb.mat_nuvem("som", 5.0)
        limiar.outputs[0].default_value = 0.0
        aneis = [self._anel_som(m, 0.08) for _ in range(3)]

        def f(t):
            for i, o in enumerate(aneis):
                u = (t + i / 3) % 1.0
                s = self.L * (0.18 + 0.78 * u)
                o.location = (0, -0.5, 0)
                o.rotation_euler = (math.radians(90), 0, 0)
                o.scale = (s, s * 0.6, s * 1.15)
                o.hide_render = u > 0.96
            calor.outputs[0].default_value = 2.4
        self.anim.append(f)

        # cone de caixa de som: o miolo que bate (pulsa duas vezes no ciclo)
        mm, emis = eb.mat_luz("cone")
        cone = eb.anel_obj(mm, 1.0, 0.35)

        def g(t):
            s = self.L * (0.16 + 0.05 * abs(math.sin(tau(t))))
            cone.location = (0, -0.9, 0)
            cone.rotation_euler = (math.radians(90), 0, 0)
            cone.scale = (s, s * 0.4, s)
            emis.inputs["Strength"].default_value = 3.2
        self.anim.append(g)

    def p_paredao(self):
        """Paredão de som andando para a frente (+x): arcos altos, um atrás do outro, abrindo (laço pela fase)."""
        m, ruido, calor, limiar = eb.mat_nuvem("paredao", 4.0)
        limiar.outputs[0].default_value = 0.0
        arcos = [self._anel_som(m, 0.2) for _ in range(4)]

        def f(t):
            for i, o in enumerate(arcos):
                u = (t + i / 4) % 1.0
                o.location = (-self.L * 0.75 + u * self.L * 1.35, -0.4, 0)
                # anel de lado: elipse alta e fina; cresce ao andar
                alt = self.A * (0.55 + 0.4 * u)
                o.rotation_euler = (math.radians(90), 0, 0)
                o.scale = (self.L * (0.08 + 0.12 * u), alt * 0.6, alt)
                o.hide_render = u > 0.94
            calor.outputs[0].default_value = 3.0
        self.anim.append(f)

    def p_fumaca_laco(self):
        """Fumaça atrás do paredão, rolando (laço pela fase)."""
        m, ruido, calor, limiar = eb.mat_nuvem("fumaca_laco", 2.8)
        calor.outputs[0].default_value = 0.7
        limiar.outputs[0].default_value = 0.05
        pecas = []
        for i in range(5):
            o, d = eb.nuvem_deformada(m, 0.3, 0.45)
            pecas.append(o)

        def f(t):
            for i, o in enumerate(pecas):
                u = (t + i / 5) % 1.0
                o.location = (-self.L * 0.85 + u * self.L * 0.6, 0.6, (i / 4 - 0.5) * self.A * 1.4)
                s = self.L * (0.3 * math.sin(math.pi * u) + 0.02)
                o.scale = (s, s, s)
        self.anim.append(f)

    # ------------------------------------------------------------------ peças do padrão novo (comuns)
    def p_fluxo(self):
        """Fagulhas correndo para trás (rastro de partículas do projétil; laço exato pela fase)."""
        mat, emis = eb.mat_luz("fluxo")
        pecas = []
        for i in range(22):
            o = eb.esfera(1.0, 2, mat)
            pecas.append((o, self.rnd.random(), self.rnd.uniform(-0.75, 0.75), self.rnd.uniform(0.6, 1.4)))

        def f(t):
            for o, fase, z, k in pecas:
                u = (fase + t) % 1.0
                o.location = (self.L * (0.55 - 1.5 * u), -1.4, z * self.A * (1 - 0.4 * u))
                s = self.L * 0.03 * k * (1 - u)
                o.scale = (s * 3.5, s, s)
                o.hide_render = u > 0.95
            emis.inputs["Strength"].default_value = 3.5
        self.anim.append(f)

    def p_coluna_sombra(self):
        """Coluna de fumaça escura subindo atrás do oponente preso (laço pela fase)."""
        m, ruido, calor, limiar = eb.mat_nuvem("coluna", 2.4)
        calor.outputs[0].default_value = 0.55
        limiar.outputs[0].default_value = 0.0
        pecas = []
        for i in range(6):
            o, d = eb.nuvem_deformada(m, 0.35, 0.45)
            pecas.append(o)

        def f(t):
            for i, o in enumerate(pecas):
                u = (t + i / 6) % 1.0
                o.location = (math.sin(tau(u) + i) * self.L * 0.12, 1.5, self.chao + self.A * 2 * (0.05 + 0.9 * u))
                s = self.L * (0.55 - 0.25 * u)
                o.scale = (s, s * 0.6, s * 0.9)
        self.anim.append(f)

    def p_brasas_sobem(self):
        """Fagulhas subindo em volta do preso (laço pela fase)."""
        mat, emis = eb.mat_luz("brasas_sobem")
        pecas = []
        for i in range(18):
            o = eb.esfera(1.0, 2, mat)
            pecas.append((o, self.rnd.random(), self.rnd.uniform(-0.9, 0.9), self.rnd.uniform(0.6, 1.3)))

        def f(t):
            for o, fase, x, k in pecas:
                u = (fase + t) % 1.0
                o.location = (x * self.L * 0.8, -1.4, self.chao + u * self.A * 1.9)
                s = self.L * 0.035 * k * (1 - u)
                o.scale = (s, s, s * 2.2)
                o.hide_render = u > 0.95
            emis.inputs["Strength"].default_value = 3.2
        self.anim.append(f)


RECEITAS = {
    "pengaro": {"agarrao": ["coluna_sombra", "sombra_chao", "correntes_sobem"],
                "final": ["bola", "anel", "anel2", "elos_voando", "fumaca", "raios"],
                "poder": ["mare", "correntes_chicote", "fluxo"], "carga": ["converge", "anel"]},
    "gutto": {"agarrao": ["brilho_chao", "brasas_sobem", "raios_caindo"],
              "final": ["bola", "anel", "anel2", "ferraduras", "relampago", "raios"], "carga": ["crepita", "anel"]},
    "ck": {"agarrao": ["coluna_sombra", "som_pulsa"], "final": ["bola", "anel", "anel2", "anel3", "fumaca", "raios"],
           "poder": ["fumaca_laco", "paredao", "fluxo"], "carga": ["converge", "anel"]},
}


def renderizar(lutador, efeito, amostras, dir_render):
    (larg, alt), n, ticks, chao, laco = EFEITOS[lutador][efeito]
    sup = 4
    rx, ry = round(larg / ESCALA_BLENDER * sup), round(alt / ESCALA_BLENDER * sup)
    unid = 4.0
    meia_l = unid / 2 * larg / max(larg, alt)
    meia_a = unid / 2 * alt / max(larg, alt)
    cena = eb.cena_vazia(rx, ry, amostras, unid)
    ef = Efeito47(RECEITAS[lutador][efeito], sum(map(ord, lutador + efeito)) + 47, meia_l, meia_a, chao)
    dir_render.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        # laço: t = i/n (o quadro seguinte ao último seria t = 1, igual ao do começo do laço); sem laço vai até sumir
        t = i / n if laco >= 0 else i / (n - 1) * 0.97
        ef.quadro(t)
        cena.render.filepath = str(dir_render / f"{i:04d}.png")
        bpy.ops.render.render(write_still=True)
    return [Image.open(dir_render / f"{i:04d}.png").convert("RGBA") for i in range(n)], ticks, chao, laco


def com_rastro(quadros, frac, nf, escurece=0.62):
    """Rastro atrás (à esquerda: o projétil anda para +x): fantasmas dos quadros anteriores do laço, cada vez mais
    fracos e escuros. Devolve os quadros novos e onde fica o centro do corpo (fração da largura)."""
    w, h = quadros[0].size
    pad = round(w * frac)
    n = len(quadros)
    out = []
    for i in range(n):
        tela = Image.new("RGBA", (w + pad, h), (0, 0, 0, 0))
        for k in range(nf, 0, -1):
            g = quadros[(i - k) % n]
            r, gg, b, a = g.split()
            luz = escurece ** k
            fant = Image.merge("RGBA", [c.point(lambda v, l=luz: int(v * l)) for c in (r, gg, b)]
                               + [a.point(lambda v, k=k: int(v * 0.6 ** k))])
            camada = Image.new("RGBA", tela.size, (0, 0, 0, 0))
            camada.paste(fant, (pad - round(k * pad / nf), 0))
            tela.alpha_composite(camada)
        tela.alpha_composite(g if False else quadros[i], (pad, 0))
        out.append(tela)
    return out, (pad + w / 2) / (w + pad)


# "sombrio" (Breno, #47): massa escura com a borda acesa, em vez de bola clara. Só a sombra do Pengaró e a fumaça
# do CK; o raio do Gutto continua aceso.
SOMBRIO = {"pengaro": {"agarrao", "final", "poder", "carga"}, "ck": {"agarrao", "poder", "final"}}


def sombrio(quadros, borda=0.035, miolo=0.42):
    """Escurece o miolo e acende a borda (alfa menos alfa erodido) e os pontos mais quentes do render."""
    import numpy as np
    from PIL import ImageFilter
    out = []
    for q in quadros:
        a = q.getchannel("A")
        k = max(3, round(q.width * borda) | 1)
        er = np.asarray(a.filter(ImageFilter.MinFilter(k)), np.float32) / 255
        al = np.asarray(a, np.float32) / 255
        rgb = np.asarray(q.convert("RGB"), np.float32) / 255
        lum = rgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        aro = np.clip((al - er) * 1.6, 0, 1)
        quente = np.clip((lum - 0.82) * 4, 0, 1)
        v = np.clip(lum * miolo + aro * 0.85 + quente * 0.6, 0, 1)
        img = np.dstack([v, v, v, al]) * 255
        out.append(Image.fromarray(img.astype(np.uint8), "RGBA"))
    return out


def combinado(pixel, liso, raio=3, forca=0.6, margem=6):
    """O escolhido: o desenho do pixelfx (pixel seco) por cima de um halo de brilho do caminho direto (desfocado,
    alfa suave). Fica pixel art, mas acende como energia."""
    from PIL import ImageFilter
    out = []
    for px, li in zip(pixel, liso):
        w, h = px.size
        tela = Image.new("RGBA", (w + 2 * margem, h + 2 * margem), (0, 0, 0, 0))
        halo = Image.new("RGBA", tela.size, (0, 0, 0, 0))
        halo.paste(li.resize((w, h)), (margem, margem))
        halo = halo.filter(ImageFilter.GaussianBlur(raio))
        halo.putalpha(halo.getchannel("A").point(lambda v: int(v * forca)))
        tela.alpha_composite(halo)
        tela.alpha_composite(px, (margem, margem))
        out.append(tela)
    return out


def direto(quadros, cores, tam):
    """O caminho "feito direto": o render reduzido sem o pixelfx, cor contínua na rampa e alfa suave (brilho)."""
    import numpy as np
    rampa = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in cores[1:]], np.float32)
    out = []
    for q in quadros:
        rgba = pixelfx.reduzir(q, tam)
        lum = rgba[..., 0] * 0.2126 + rgba[..., 1] * 0.7152 + rgba[..., 2] * 0.0722
        v = np.clip(lum, 0, 1) ** 1.15 * (len(rampa) - 1)
        i0 = np.floor(v).astype(int).clip(0, len(rampa) - 2)
        f = (v - i0)[..., None]
        cor = rampa[i0] * (1 - f) + rampa[i0 + 1] * f
        a = rgba[..., 3]
        a = np.where(a < 0.04, 0, a)
        img = np.dstack([cor, a * 255]).clip(0, 255).astype(np.uint8)
        out.append(Image.fromarray(img, "RGBA"))
    return out


def gravar(destino, sprites, centro_x, chao, ticks, laco, lutador, efeito, escala=None):
    destino.mkdir(parents=True, exist_ok=True)
    for velho in destino.glob("*.png"):
        velho.unlink()
    for i, sp in enumerate(sprites):
        sp.save(destino / f"{i:02d}.png")
    w, h = sprites[0].size
    pivo = (round(w * centro_x), h - 2) if chao else (round(w * centro_x), h // 2)
    meta = {"pivo": pivo, "ticks": ticks, "quadros": len(sprites), "laco": laco, "efeito": efeito, "lutador": lutador}
    if escala:
        meta["escala"] = escala
    (destino / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    return w, h


# ----------------------------------------------------------------------------------------- Gutto: o garanhão da aura
AURA_GUTTO = eb.RAIZ / "sprites/gutto/aura"


def compor_garanhao():
    """Poder do Gutto: o MESMO garanhão de raio vermelho da aura do despertado (sprites/gutto/aura, desenho, raio e cor
    da aura aprovada), agora avançando pela tela: raios da aura, ferraduras, fantasmas do galope atrás e um rastro de
    raio. É pixel art já pronto (a aura), então não passa pelo pixelfx; vai no jogo em escala 0,8."""
    import numpy as np
    from PIL import ImageDraw
    import random
    rnd = random.Random(47)
    n = 24
    ab = lambda nome, k: Image.open(AURA_GUTTO / f"{nome}_{k:02d}.png").convert("RGBA")
    W, H = 360, 200
    pad = 170
    # as cores do rastro são as do próprio garanhão (do escuro ao claro), para o raio bater com o cavalo
    amostra = np.array(ab("garanhao", 0))
    unicas = np.unique(amostra[amostra[..., 3] > 0][:, :3], axis=0)
    unicas = unicas[np.argsort(unicas @ np.array([0.2126, 0.7152, 0.0722]))]
    cores = [tuple(int(v) for v in unicas[round(i * (len(unicas) - 1) / 6)]) for i in range(7)]
    quadros = []
    for q in range(n):
        k = 2 * q
        tela = Image.new("RGBA", (W + pad, H), (0, 0, 0, 0))
        # rastro de raio: zigue-zagues saindo da garupa para trás, piscando
        d = ImageDraw.Draw(tela)
        for j in range(4):
            if (q + j) % 3 == 2:
                continue
            y0 = 70 + j * 22 + rnd.randint(-6, 6)
            x, y = pad + 120, y0
            pts = [(x, y)]
            while x > 30 + j * 12:
                x -= rnd.randint(12, 22)
                y += rnd.randint(-10, 10)
                pts.append((x, y))
            d.line(pts, fill=cores[1] + (255,), width=7)
            d.line(pts, fill=cores[3] + (255,), width=5)
            d.line(pts, fill=cores[6] + (255,), width=2)
        # fantasmas do galope (quadros anteriores), escuros e quadriculados (alfa só 0/255, como o pixelfx)
        for g, desl in ((3, 150), (2, 100), (1, 50)):
            img = ab("garanhao", (k - 2 * g) % 48)
            a = np.array(img)
            m = a[..., 3] > 0
            yy, xx = np.mgrid[0:H, 0:W]
            xadrez = ((xx + yy + q) % (g + 1)) == 0 if g > 1 else ((xx + yy) % 2) == 0
            a[..., :3] = (a[..., :3] * (0.55 ** g)).astype(np.uint8)
            a[..., 3] = np.where(m & xadrez, 255, 0)
            tela.alpha_composite(Image.fromarray(a, "RGBA"), (pad - desl, 0))
        for nome in ("raios", "garanhao", "ferraduras"):
            tela.alpha_composite(ab(nome, k if nome == "garanhao" else (2 * k) % 96), (pad, 0))
        quadros.append(tela)
    caixa = None
    for t in quadros:
        b = t.getbbox()
        caixa = b if caixa is None else (min(caixa[0], b[0]), min(caixa[1], b[1]), max(caixa[2], b[2]), max(caixa[3], b[3]))
    quadros = [t.crop(caixa) for t in quadros]
    centro = (pad + 180 - caixa[0]) / (caixa[2] - caixa[0])
    w, h = gravar(SAIDA / "gutto" / "d47_poder", quadros, centro, False, 2, 0, "gutto", "poder", escala=0.8)
    print(f"gutto poder (garanhão da aura): {n} quadros {w}x{h}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lutadores", nargs="*", default=list(LUTADORES))
    ap.add_argument("--efeitos", nargs="+", default=["agarrao", "final", "poder", "carga"])
    ap.add_argument("--amostras", type=int, default=16)
    ap.add_argument("--comparar", action="store_true",
                    help="grava também os dois caminhos puros (d47_<efeito>_pixelfx e _direto), fora do git")
    a = ap.parse_args()
    for lutador in a.lutadores:
        for efeito in a.efeitos:
            if lutador == "gutto" and efeito == "poder":
                compor_garanhao()
                continue
            t0 = time.time()
            with tempfile.TemporaryDirectory() as td:
                quadros, ticks, chao, laco = renderizar(lutador, efeito, a.amostras, Path(td))
            (larg, alt) = EFEITOS[lutador][efeito][0]
            centro = 0.5
            if efeito in RASTRO:
                frac, nf = RASTRO[efeito]
                quadros, centro = com_rastro(quadros, frac, nf)
                larg = larg * (1 + frac)
            tam = round(max(larg, alt) / ESCALA_BLENDER)
            cores = CORES[lutador][FORMA[lutador]]
            if efeito in SOMBRIO.get(lutador, ()):
                quadros = sombrio(quadros)
            with tempfile.TemporaryDirectory() as td:
                pixel = pixelfx.processar(quadros, td, pixelfx.ler_paleta(",".join(cores)), tam=tam, bloco=1,
                                          previa=False, gama=1.15)
            liso = direto(quadros, cores, tam)
            # no jogo vai o combinado; os dois caminhos puros ficam para a comparação (--comparar)
            w, h = gravar(SAIDA / lutador / f"d47_{efeito}", combinado(pixel, liso), centro, chao, ticks, laco,
                          lutador, efeito)
            if a.comparar:
                gravar(SAIDA / lutador / f"d47_{efeito}_pixelfx", pixel, centro, chao, ticks, laco, lutador, efeito)
                gravar(SAIDA / lutador / f"d47_{efeito}_direto", liso, centro, chao, ticks, laco, lutador, efeito)
            print(f"{lutador} {efeito}: {len(quadros)} quadros {w}x{h} ({time.time() - t0:.0f} s)", flush=True)


if __name__ == "__main__":
    main()
