"""Rig procedural de lutador para Blender (bpy). Reutilizável: cada lutador é só um dicionário de medidas e cores.

Eixos: o lutador olha para +X, a câmera olha de lado (de -Y para +Y). Tudo em metros, 1,75 m = 112 px.

Poses são dicionários de ângulos em graus. Convenção: positivo = para frente / para cima na tela (anti-horário
para quem olha o lutador virado para a direita). Chaves (todas opcionais, 0 por padrão):
  dx, dz               desloca o quadril (m)
  quadril              inclina a pelve (+ = joga o quadril para frente)
  tronco, pescoco, cabeca   inclinação do tronco, pescoço e cabeça (+ = inclina para frente)
  F = braço da frente (perto da câmera), T = braço de trás; ombro_F, cotovelo_F, mao_F, ombro_T...
  coxa_F, joelho_F, pe_F, coxa_T, joelho_T, pe_T  (joelho positivo dobra a canela para trás)
  giro                 giro do corpo todo em volta do próprio eixo vertical (graus, para a câmera ver o peito)
"""
import math

import bpy
from mathutils import Matrix, Vector

# ------------------------------------------------------------------ medidas

PENGARO = {
    "nome": "pengaro",
    "pele": (0.42, 0.20, 0.09),
    "pele_sombra": (0.34, 0.15, 0.065),
    "cabelo": (0.025, 0.02, 0.03),
    "calca": (0.80, 0.78, 0.84),
    "listra_verde": (0.07, 0.42, 0.18),
    "listra_amarela": (0.95, 0.74, 0.08),
    "faixa": (0.04, 0.30, 0.30),     # faixa verde-azulada na cintura
    "cordao": (0.95, 0.74, 0.08),
    "caneleira": (0.10, 0.17, 0.13),  # caneleira verde escura, perna de trás
    "torso_nu": True,
    "caneleira_em": "T",
    "musculo": 1.2,
}

QUADRIL_Z = 0.93
COXA, CANELA = 0.45, 0.43
BRACO, ANTEBRACO, MAO = 0.30, 0.26, 0.10
OMBRO_Z, OMBRO_Y = 1.42, 0.20
QUADRIL_Y = 0.09


def limpar():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def material(nome, cor, rugosidade=0.9):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*cor, 1)
    b.inputs["Roughness"].default_value = rugosidade
    for nome_entrada in ("Specular IOR Level", "Specular"):
        if nome_entrada in b.inputs:
            b.inputs[nome_entrada].default_value = 0.05
    return m


def elipsoide(nome, centro, raios, mat, rot=(0, 0, 0), segmentos=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segmentos, ring_count=segmentos // 2, location=centro)
    o = bpy.context.object
    o.name = nome
    o.scale = raios
    o.rotation_euler = rot
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o


def cilindro(nome, centro, raios, mat, segmentos=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segmentos, location=centro)
    o = bpy.context.object
    o.name = nome
    o.scale = raios
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o


class Lutador:
    """Cria armature + malhas e sabe posar por cinemática direta em 2D (plano XZ)."""

    def __init__(self, medidas=PENGARO, oculos=False):
        self.m = medidas
        self.oculos = oculos
        self.ossos = {}      # nome -> dict(pos_repouso, dir_repouso, comprimento, pai)
        self.partes = []     # (objeto, osso, matriz_repouso_mundo)
        self._construir()

    # -------------------------------------------------------------- esqueleto
    def _definir_ossos(self):
        o = {}

        def osso(nome, pai, cabeca, comprimento, direcao):
            o[nome] = {"pai": pai, "cabeca": Vector(cabeca), "comp": comprimento, "dir": Vector(direcao)}

        osso("quadril", None, (0, 0, QUADRIL_Z), 0.10, (0, 0, 1))
        osso("tronco", "quadril", (0, 0, 1.03), 0.47, (0, 0, 1))
        osso("pescoco", "tronco", (0, 0, 1.50), 0.08, (0, 0, 1))
        osso("cabeca", "pescoco", (0, 0, 1.58), 0.17, (0, 0, 1))
        for lado, sinal in (("F", -1), ("T", 1)):
            osso(f"ombro_{lado}", "tronco", (0, sinal * OMBRO_Y, OMBRO_Z), BRACO, (0, 0, -1))
            osso(f"cotovelo_{lado}", f"ombro_{lado}", (0, sinal * OMBRO_Y, OMBRO_Z - BRACO), ANTEBRACO, (0, 0, -1))
            osso(f"mao_{lado}", f"cotovelo_{lado}", (0, sinal * OMBRO_Y, OMBRO_Z - BRACO - ANTEBRACO), MAO, (0, 0, -1))
            osso(f"coxa_{lado}", "quadril", (0, sinal * QUADRIL_Y, QUADRIL_Z), COXA, (0, 0, -1))
            osso(f"joelho_{lado}", f"coxa_{lado}", (0, sinal * QUADRIL_Y, QUADRIL_Z - COXA), CANELA, (0, 0, -1))
            osso(f"pe_{lado}", f"joelho_{lado}", (0, sinal * QUADRIL_Y, QUADRIL_Z - COXA - CANELA), 0.2, (1, 0, 0))
        self.ossos = o

    def _construir(self):
        limpar()
        self._definir_ossos()
        bpy.ops.object.armature_add(location=(0, 0, 0))
        self.arm = bpy.context.object
        self.arm.name = f"rig_{self.m['nome']}"
        bpy.ops.object.mode_set(mode="EDIT")
        eb = self.arm.data.edit_bones
        for e in list(eb):
            eb.remove(e)
        for nome, d in self.ossos.items():
            b = eb.new(nome)
            b.head = d["cabeca"]
            b.tail = d["cabeca"] + d["dir"] * d["comp"]
            if d["pai"]:
                b.parent = eb[d["pai"]]
        bpy.ops.object.mode_set(mode="OBJECT")
        self._malhas()
        for nome, pb in self.arm.pose.bones.items():
            pb.rotation_mode = "QUATERNION"

    # -------------------------------------------------------------- malhas
    def _parte(self, obj, osso):
        self.partes.append((obj, osso, obj.matrix_world.copy()))

    def _malhas(self):
        m = self.m
        k = m["musculo"]
        pele = material("pele", m["pele"])
        pele_s = material("pele_sombra", m["pele_sombra"])
        cabelo = material("cabelo", m["cabelo"])
        calca = material("calca", m["calca"])
        verde = material("listra_verde", m["listra_verde"])
        amar = material("listra_amarela", m["listra_amarela"])
        faixa = material("faixa", m["faixa"])
        cordao = material("cordao", m["cordao"])
        canel = material("caneleira", m["caneleira"], 0.6)
        P = self._parte

        # tronco
        P(elipsoide("peito", (0.0, 0, 1.31), (0.150 * k, 0.205 * k, 0.170), pele), "tronco")
        P(elipsoide("abdomen", (0.0, 0, 1.12), (0.125, 0.155, 0.150), pele), "quadril")
        for lado in (-1, 1):
            P(elipsoide("peitoral", (0.095, lado * 0.085, 1.355), (0.075, 0.085, 0.065), pele_s), "tronco")
            P(elipsoide("trapezio", (-0.01, lado * 0.09, 1.465), (0.07, 0.08, 0.055), pele), "tronco")
            for z in (1.19, 1.115, 1.045):
                P(elipsoide("abs", (0.112, lado * 0.036, z), (0.03, 0.04, 0.034), pele_s), "quadril")
        P(elipsoide("pelve", (0.0, 0, 0.95), (0.135, 0.175, 0.115), calca), "quadril")
        # faixa verde-azulada, cordão amarelo e pontas penduradas
        P(cilindro("faixa", (0, 0, 1.005), (0.142, 0.182, 0.032), faixa), "quadril")
        P(cilindro("cordao", (0, 0, 0.965), (0.147, 0.187, 0.011), cordao), "quadril")
        P(elipsoide("no", (0.13, -0.03, 0.99), (0.04, 0.05, 0.05), faixa), "quadril")
        P(elipsoide("ponta_faixa", (0.10, -0.06, 0.90), (0.014, 0.05, 0.10), faixa, rot=(0, math.radians(-8), 0)), "quadril")
        P(elipsoide("pingente", (0.06, -0.19, 0.87), (0.016, 0.016, 0.085), cordao), "quadril")
        P(elipsoide("pingente2", (0.095, -0.17, 0.86), (0.016, 0.016, 0.075), cordao), "quadril")
        # pescoço, cabeça, cabelo
        P(elipsoide("pescoco", (0.0, 0, 1.53), (0.058, 0.058, 0.075), pele), "pescoco")
        P(elipsoide("cabeca", (0.012, 0, 1.64), (0.098, 0.088, 0.118), pele), "cabeca")
        P(elipsoide("maxilar", (0.035, 0, 1.585), (0.07, 0.07, 0.06), pele), "cabeca")
        P(elipsoide("nariz", (0.105, 0, 1.625), (0.02, 0.016, 0.025), pele_s), "cabeca")
        for lado in (-1, 1):
            P(elipsoide("sobrancelha", (0.088, lado * 0.036, 1.662), (0.016, 0.03, 0.009), cabelo, rot=(0, 0, 0)), "cabeca")
            P(elipsoide("olho", (0.092, lado * 0.036, 1.644), (0.012, 0.016, 0.01), cabelo), "cabeca")
        P(elipsoide("cabelo", (-0.018, 0, 1.685), (0.108, 0.094, 0.085), cabelo), "cabeca")
        for lado in (-1, 1):
            P(elipsoide("orelha", (0.0, lado * 0.088, 1.635), (0.018, 0.012, 0.03), pele_s), "cabeca")
        if self.oculos:
            ar = material("armacao", (0.75, 0.78, 0.82), 0.3)
            lente = material("lente", (0.20, 0.08, 0.32), 0.2)
            P(elipsoide("lente", (0.095, 0, 1.652), (0.025, 0.082, 0.022), lente), "cabeca")
            P(elipsoide("armacao", (0.06, 0, 1.655), (0.05, 0.092, 0.006), ar), "cabeca")

        for lado, y in (("F", -1), ("T", 1)):
            # braços
            P(elipsoide("deltoide", (0, y * OMBRO_Y, OMBRO_Z - 0.02), (0.072 * k, 0.072 * k, 0.085), pele), f"ombro_{lado}")
            P(elipsoide("braco", (0, y * OMBRO_Y, OMBRO_Z - 0.16), (0.066 * k, 0.062 * k, 0.17), pele), f"ombro_{lado}")
            P(elipsoide("biceps", (0.012, y * OMBRO_Y, OMBRO_Z - 0.14), (0.062 * k, 0.05, 0.10), pele_s), f"ombro_{lado}")
            P(elipsoide("antebraco", (0, y * OMBRO_Y, OMBRO_Z - BRACO - 0.12), (0.058 * k, 0.054 * k, 0.15), pele), f"cotovelo_{lado}")
            P(elipsoide("cotovelo", (0, y * OMBRO_Y, OMBRO_Z - BRACO), (0.052, 0.05, 0.05), pele), f"cotovelo_{lado}")
            P(elipsoide("punho", (0.012, y * OMBRO_Y, OMBRO_Z - BRACO - ANTEBRACO - 0.055), (0.066, 0.06, 0.075), pele), f"mao_{lado}")
            # pernas (calça branca com listras laterais)
            yy = y * QUADRIL_Y
            P(elipsoide("coxa", (0, yy, QUADRIL_Z - 0.23), (0.125, 0.115, 0.27), calca), f"coxa_{lado}")
            for dx, mat in ((-0.016, verde), (0.016, amar)):
                P(elipsoide("listra_coxa", (dx, yy + y * 0.098, QUADRIL_Z - 0.23), (0.011, 0.014, 0.25), mat), f"coxa_{lado}")
            zj = QUADRIL_Z - COXA
            P(elipsoide("joelho", (0, yy, zj), (0.09, 0.088, 0.09), calca), f"joelho_{lado}")
            P(elipsoide("canela_calca", (0.0, yy, zj - 0.12), (0.1, 0.095, 0.155), calca), f"joelho_{lado}")
            for dx, mat in ((-0.016, verde), (0.016, amar)):
                P(elipsoide("listra_canela", (dx, yy + y * 0.082, zj - 0.12), (0.01, 0.014, 0.13), mat), f"joelho_{lado}")
            za = zj - CANELA
            P(elipsoide("canela", (0.0, yy, za + 0.115), (0.052, 0.050, 0.125), pele), f"joelho_{lado}")
            if m["caneleira_em"] == lado:
                P(elipsoide("caneleira", (0.004, yy, za + 0.12), (0.066, 0.064, 0.105), canel), f"joelho_{lado}")
            P(elipsoide("tornozelo", (0, yy, za + 0.01), (0.05, 0.048, 0.05), pele), f"pe_{lado}")
            P(elipsoide("pe", (0.07, yy, za - 0.015), (0.115, 0.05, 0.04), pele), f"pe_{lado}")
            P(elipsoide("dedos", (0.155, yy, za - 0.018), (0.04, 0.05, 0.028), pele), f"pe_{lado}")
            P(elipsoide("calcanhar", (-0.04, yy, za - 0.01), (0.045, 0.045, 0.04), pele), f"pe_{lado}")

        # parenta cada malha ao osso (ela é movida direto, sem pesos)
        for obj, osso, _ in self.partes:
            obj.parent = self.arm
            obj.parent_type = "BONE"
            obj.parent_bone = osso
        bpy.context.view_layer.update()
        # corrige o deslocamento da ponta do osso
        for obj, osso, mundo in self.partes:
            pb = self.arm.pose.bones[osso]
            pai = self.arm.matrix_world @ pb.matrix @ Matrix.Translation((0, pb.bone.length, 0))
            obj.matrix_parent_inverse = pai.inverted()

    # -------------------------------------------------------------- pose
    def posar(self, pose):
        """Aplica uma pose (dict em graus) por cinemática direta no plano XZ."""
        g = lambda k: float(pose.get(k, 0.0))
        giro = math.radians(g("giro"))
        # ângulo anti-horário na tela acumulado e posição da cabeça de cada osso
        ccw = {}
        pos = {}
        q = {
            "quadril": -g("quadril"),
            "tronco": -g("tronco"),
            "pescoco": -g("pescoco"),
            "cabeca": -g("cabeca"),
        }
        for lado in ("F", "T"):
            q[f"ombro_{lado}"] = g(f"ombro_{lado}")
            q[f"cotovelo_{lado}"] = g(f"cotovelo_{lado}")
            q[f"mao_{lado}"] = g(f"mao_{lado}")
            q[f"coxa_{lado}"] = g(f"coxa_{lado}")
            q[f"joelho_{lado}"] = -g(f"joelho_{lado}")
            q[f"pe_{lado}"] = g(f"pe_{lado}")
        for lado in ("F", "T"):
            if f"pe_{lado}" not in pose:  # pé chato no chão, a menos que a pose mande
                q[f"pe_{lado}"] = g(f"joelho_{lado}") - g(f"coxa_{lado}") + g("quadril")
        deslocamento = Vector((g("dx"), 0, 0))

        def rot2(v, graus):
            a = math.radians(graus)
            return Vector((v.x * math.cos(a) - v.z * math.sin(a), v.y, v.x * math.sin(a) + v.z * math.cos(a)))

        for nome, d in self.ossos.items():
            pai = d["pai"]
            if pai is None:
                ccw[nome] = q[nome]
                pos[nome] = d["cabeca"] + deslocamento
            else:
                ccw[nome] = ccw[pai] + q[nome]
                # a cabeça do osso fica a uma distância fixa da cabeça do pai (no repouso), girada com o pai
                off = d["cabeca"] - self.ossos[pai]["cabeca"]
                pos[nome] = pos[pai] + rot2(off, ccw[pai])
        # trava no chão: o ponto mais baixo dos pés encosta em z = 0 (mais "altura" quando a pose está no ar)
        baixo = 9.0
        for lado in ("F", "T"):
            n = f"pe_{lado}"
            for ponto in ((-0.05, 0, -0.055), (0.17, 0, -0.065)):
                baixo = min(baixo, (pos[n] + rot2(Vector(ponto), ccw[n])).z)
        subir = -baixo + g("altura") if not pose.get("sem_chao") else g("dz")
        for n in pos:
            pos[n] = pos[n] + Vector((0, 0, subir))
        centro = Vector((0, 0, QUADRIL_Z + subir)) + deslocamento
        Ms = {}
        for nome, d in self.ossos.items():
            bone = self.arm.data.bones[nome]
            rest = bone.matrix_local.to_3x3().to_4x4()
            rot = Matrix.Rotation(-math.radians(ccw[nome]), 4, "Y")
            M = Matrix.Translation(pos[nome]) @ rot @ rest
            if giro:
                R = Matrix.Rotation(giro, 4, "Z")
                M = Matrix.Translation(centro) @ R @ Matrix.Translation(-centro) @ M
            Ms[nome] = M
            if d["pai"] is None:
                basis = bone.matrix_local.inverted() @ M
            else:
                rel = self.arm.data.bones[d["pai"]].matrix_local.inverted() @ bone.matrix_local
                basis = rel.inverted() @ Ms[d["pai"]].inverted() @ M
            self.arm.pose.bones[nome].matrix_basis = basis
        bpy.context.view_layer.update()
