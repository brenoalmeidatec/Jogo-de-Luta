#!/usr/bin/env python3
"""Gera um cenário ANIMADO do IKEMEN GO v1.0.0 (stages/<id>.def + stages/<id>.sff) a partir de uma descrição.

  python ferramentas/gerar_cenario.py cenarios/<id>/cenario.json [--destino stages] [--previa PASTA] [--furo-magenta]

A descrição é um JSON (ou um dict, pela função gerar()) com as camadas em PNG com alfa, de trás para a frente. Todas as
medidas são em pixels de arte, na mesma malha dos lutadores: a tela lógica do jogo tem 320x180 e 1 px de arte = 1 px de
lutador = 4 px na janela 1280x720. O passo a passo, as medidas da arte e os critérios de aceite estão em
docs/arcade/cenarios.md. Resumo dos campos (os que têm padrão podem faltar):

  id, nome, autor
  largura_mundo (768)   largura da camada de delta 1; a câmera anda (largura_mundo - 320) / 2 para cada lado
  subida (40)           quanto a câmera sobe no pulo (boundhigh = -subida)
  chao_y (165)          linha do chão (pés) em px a partir do topo da tela em repouso
  camera {tensao 60, segue_vertical 0.6, tensao_chao 30}
  jogadores {p1x -70, p2x 70, margem_tela 15}
  sombra {intensidade 96, cor [0,0,0], escala_y 0.3}   reflexo (0 a 256; 0 desliga)
  suave (true)          roundpos = 0 no motor; false pede roundpos = 1 (no teste da sandbox não mudou nada visível:
                        o movimento já sai liso, de 1 em 1 px da janela)
  camadas [ ... ]       cada uma:
    nome, imagem "x.png"            camada parada de um desenho
    quadros ["a.png", ...] | folha {"imagem": "x.png", "n": 8}, ticks 6 | [6, 6, 8...]   camada animada em quadros
    delta [dx, dy] ([1, 1])         profundidade: 0 = não anda com a câmera (céu), 1 = anda junto com o chão
    x, y                            canto de cima-esquerda da imagem NA TELA com a câmera em repouso
                                    (padrão: x centralizado, y com a base da imagem na base da tela)
    frente (false)                  true = desenhada na frente dos lutadores (layerno 1)
    velocidade [vx, vy]             px por tick (60 ticks = 1 s), movimento contínuo
    repete [rx, ry]  vao [gx, gy]   1 = repete sem fim nesse eixo, com vão em px entre as cópias
    seno_x / seno_y [amplitude, periodo_em_ticks, fase_em_ticks]
    mistura "normal" | "soma" | "subtrai",  alfa [origem, destino] (0 a 256, liga addalpha)
    suave                           troca o padrão do cenário só nesta camada
    controles [{"tipo": "VelSet", "tempo": [0], "x": 0.3}, ...], ciclo 480   BGCtrl em loop (VelSet, VelAdd,
                                    PosSet, PosAdd, SinX, SinY, Visible, Enabled, Anim) com os parâmetros do motor

Antes de gravar, o gerador simula a câmera nos quatro cantos do curso e recusa cenário com furo (pixel sem nada
desenhado), que no jogo viraria faixa preta. --previa grava a simulação (três posições e um GIF) para olhar sem motor.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from layout_sff import escrever_sff2  # noqa: E402  (SFF v2 com PNG de 32 bits, o mesmo do layout Nazafights)

RAIZ = Path(__file__).resolve().parent.parent
TELA_L, TELA_A = 320, 180
MISTURAS = {"normal": "none", "soma": "add", "subtrai": "sub"}
TIPOS_CTRL = {"velset", "veladd", "posset", "posadd", "sinx", "siny", "visible", "enabled", "anim", "null"}


def num(v):
    """Número no formato do .def: inteiro sem ponto, fração com até 4 casas."""
    f = float(v)
    return str(int(f)) if f == int(f) else f"{f:.4f}".rstrip("0").rstrip(".")


def par(v, padrao):
    if v is None:
        return tuple(padrao)
    if isinstance(v, (int, float)):
        return (v, v)
    return tuple(v)


class Camada:
    def __init__(self, d, k, base, suave_padrao):
        self.k = k
        self.nome = d.get("nome", f"camada{k}")
        desconhecidos = set(d) - {"nome", "imagem", "quadros", "folha", "ticks", "delta", "x", "y", "frente",
                                  "velocidade", "repete", "vao", "seno_x", "seno_y", "mistura", "alfa", "suave",
                                  "controles", "ciclo"}
        if desconhecidos:
            raise ValueError(f"camada {self.nome}: campo desconhecido {sorted(desconhecidos)}")
        if "folha" in d:
            folha = Image.open(base / d["folha"]["imagem"]).convert("RGBA")
            n = int(d["folha"]["n"])
            if folha.width % n:
                raise ValueError(f"camada {self.nome}: folha de {folha.width} px não divide em {n} quadros")
            lq = folha.width // n
            self.quadros = [folha.crop((i * lq, 0, (i + 1) * lq, folha.height)) for i in range(n)]
        elif "quadros" in d:
            self.quadros = [Image.open(base / q).convert("RGBA") for q in d["quadros"]]
        elif "imagem" in d:
            self.quadros = [Image.open(base / d["imagem"]).convert("RGBA")]
        else:
            raise ValueError(f"camada {self.nome}: falta imagem, quadros ou folha")
        self.l, self.a = self.quadros[0].size
        if any(q.size != (self.l, self.a) for q in self.quadros):
            raise ValueError(f"camada {self.nome}: os quadros não têm todos o mesmo tamanho")
        t = d.get("ticks", 6)
        self.ticks = [int(t)] * len(self.quadros) if isinstance(t, (int, float)) else [int(v) for v in t]
        if len(self.ticks) != len(self.quadros) or min(self.ticks) < 1:
            raise ValueError(f"camada {self.nome}: ticks precisa de um valor >= 1 por quadro")
        self.animada = len(self.quadros) > 1
        self.delta = par(d.get("delta"), (1, 1))
        self.x = d.get("x", (TELA_L - self.l) // 2)
        self.y = d.get("y", TELA_A - self.a)
        self.frente = bool(d.get("frente", False))
        self.vel = par(d.get("velocidade"), (0, 0))
        self.repete = tuple(int(v) for v in par(d.get("repete"), (0, 0)))
        self.vao = tuple(int(v) for v in par(d.get("vao"), (0, 0)))
        self.seno_x = tuple(d["seno_x"]) if d.get("seno_x") else None
        self.seno_y = tuple(d["seno_y"]) if d.get("seno_y") else None
        self.mistura = d.get("mistura", "normal")
        if self.mistura not in MISTURAS:
            raise ValueError(f"camada {self.nome}: mistura {self.mistura!r} (use {', '.join(MISTURAS)})")
        self.alfa = tuple(d["alfa"]) if d.get("alfa") else None
        self.suave = bool(d.get("suave", suave_padrao))
        self.controles = d.get("controles", [])
        self.ciclo = d.get("ciclo")
        for c in self.controles:
            if c.get("tipo", "").lower() not in TIPOS_CTRL:
                raise ValueError(f"camada {self.nome}: controle {c.get('tipo')!r} desconhecido")
        if self.controles and not self.ciclo:
            raise ValueError(f"camada {self.nome}: controles pedem ciclo (ticks do loop)")

    # ---- simulação (a mesma conta do motor: tela = centro + start + movimento - câmera * delta) ----
    def quadro_no_tick(self, t):
        t %= sum(self.ticks)
        for q, d in zip(self.quadros, self.ticks):
            if t < d:
                return q
            t -= d
        return self.quadros[-1]

    def posicao(self, camx, camy, t):
        x = self.x + self.vel[0] * t - camx * self.delta[0]
        y = self.y + self.vel[1] * t - camy * self.delta[1]
        if self.seno_x:
            x += self.seno_x[0] * math.sin(2 * math.pi * (t + self.seno_x[2]) / self.seno_x[1])
        if self.seno_y:
            y += self.seno_y[0] * math.sin(2 * math.pi * (t + self.seno_y[2]) / self.seno_y[1])
        return (x, y) if self.suave else (math.floor(x), math.floor(y))

    def copias(self, camx, camy, t, caixa):
        """Posições (x, y) inteiras de cada cópia que encosta na caixa (x0, y0, x1, y1) da tela."""
        x, y = self.posicao(camx, camy, t)
        px, py = self.l + self.vao[0], self.a + self.vao[1]

        def eixo(p, tam, passo, rep, a, b):
            if rep == 1:
                k0 = math.floor((a - p - tam) / passo) + 1
                return [p + k * passo for k in range(k0, math.ceil((b - p) / passo) + 1)]
            return [p + k * passo for k in range(max(rep, 1))]

        return [(round(cx), round(cy)) for cx in eixo(x, self.l, px, self.repete[0], caixa[0], caixa[2])
                for cy in eixo(y, self.a, py, self.repete[1], caixa[1], caixa[3])]


class Cenario:
    def __init__(self, desc, base):
        global TELA_L, TELA_A
        TELA_L, TELA_A = desc.get("tela", (320, 180))  # 1280x720: arte na resolução da janela (localcoord do motor)
        self.id = desc["id"]
        self.nome = desc.get("nome", self.id)
        self.autor = desc.get("autor", "Nazafights")
        self.largura = int(desc.get("largura_mundo", 768))
        if self.largura < TELA_L or (self.largura - TELA_L) % 2:
            raise ValueError("largura_mundo precisa ser par e >= 320")
        self.curso = (self.largura - TELA_L) // 2
        self.subida = int(desc.get("subida", 40))
        self.chao_y = int(desc.get("chao_y", 165))
        cam = desc.get("camera", {})
        self.tensao = cam.get("tensao", 60)
        self.segue_vertical = cam.get("segue_vertical", 0.6)
        self.tensao_chao = cam.get("tensao_chao", 30)
        jog = desc.get("jogadores", {})
        self.p1x, self.p2x = jog.get("p1x", -70), jog.get("p2x", 70)
        self.margem_tela = jog.get("margem_tela", 15)
        so = desc.get("sombra", {})
        self.sombra = (so.get("intensidade", 96), tuple(so.get("cor", (0, 0, 0))), so.get("escala_y", 0.3))
        self.reflexo = int(desc.get("reflexo", 0))
        self.musica = desc.get("musica", "")
        self.suave = bool(desc.get("suave", True))
        self.camadas = [Camada(d, k, base, self.suave) for k, d in enumerate(desc["camadas"])]
        if not self.camadas:
            raise ValueError("cenário sem camadas")

    def compor(self, camx=0, camy=0, t=0, margem=0, fundo=(0, 0, 0, 0)):
        """Desenha a tela (320x180 mais a margem em volta) como o motor faria no tick t."""
        caixa = (-margem, -margem, TELA_L + margem, TELA_A + margem)
        tela = Image.new("RGBA", (TELA_L + 2 * margem, TELA_A + 2 * margem), fundo)
        for c in sorted(self.camadas, key=lambda c: c.frente):  # as de frente por último, na ordem da lista
            q = c.quadro_no_tick(t)
            for (x, y) in c.copias(camx, camy, t, caixa):
                _colar(tela, q, x + margem, y + margem)  # soma/subtrai entram na previa como sobreposicao simples
        return tela

    def furos(self):
        """Lista de (canto, pixels sem cobertura) nos quatro cantos do curso da câmera, só com camadas opacas."""
        ruins = []
        for nome, camx in (("esquerda", -self.curso), ("direita", self.curso)):
            for nv, camy in (("baixo", 0), ("alto", -self.subida)):
                pior = 0
                for t in (0, 97, 1201, 4999):  # camadas que se movem não podem ser a única cobertura
                    a = self.compor(camx, camy, t).getchannel("A")
                    pior = max(pior, int((np.asarray(a) < 255).sum()))
                if pior:
                    ruins.append((f"{nome}/{nv}", pior))
        return ruins

    # ---- saída para o motor ----
    def sprites(self):
        itens = []
        for c in self.camadas:
            for n, q in enumerate(c.quadros):
                itens.append((c.k, n, q, 0, 0))
        retrato = self.compor().convert("RGB").resize((240, 135), Image.NEAREST).crop((0, 17, 240, 117))
        itens.append((9000, 1, retrato.convert("RGBA"), 0, 0))
        return itens

    def texto_def(self):
        L = []
        L += ["; Gerado por ferramentas/gerar_cenario.py. Edite a descrição do cenário e gere de novo, não este arquivo.",
              "[Info]", f'name = "{self.nome}"', f'displayname = "{self.nome}"', "versiondate = 11,11,2026",
              "mugenversion = 1.1", "ikemenversion = 1.0", f'author = "{self.autor}"', "",
              "[Camera]", "startx = 0", "starty = 0", f"boundleft = {-self.curso}", f"boundright = {self.curso}",
              f"boundhigh = {-self.subida}", "boundlow = 0", f"verticalfollow = {num(self.segue_vertical)}",
              f"floortension = {num(self.tensao_chao)}", f"tension = {num(self.tensao)}",
              "zoomin = 1", "zoomout = 1", "startzoom = 1", "",
              "[PlayerInfo]", f"p1startx = {self.p1x}", "p1starty = 0", "p1facing = 1",
              f"p2startx = {self.p2x}", "p2starty = 0", "p2facing = -1",
              f"p3startx = {self.p1x - 30}", "p3starty = 0", "p3facing = 1",
              f"p4startx = {self.p2x + 30}", "p4starty = 0", "p4facing = -1",
              f"leftbound = {-self.largura // 2}", f"rightbound = {self.largura // 2}", "",
              "[Bound]", f"screenleft = {self.margem_tela}", f"screenright = {self.margem_tela}", "",
              "[StageInfo]", f"zoffset = {self.chao_y}", "autoturn = 1", "resetBG = 1",
              f"localcoord = {TELA_L}, {TELA_A}", "xscale = 1", "yscale = 1", "",
              "[Shadow]", f"intensity = {self.sombra[0]}", "color = " + ",".join(str(v) for v in self.sombra[1]),
              f"yscale = {num(self.sombra[2])}", "fade.range = 0,0", "",
              "[Reflection]", f"intensity = {self.reflexo}", "",
              "[Music]", f"bgmusic = {self.musica}", "bgmvolume = 100", "",
              "[BGdef]", f"spr = {self.id}.sff", "debugbg = 0", "",
              "[Begin Action 9000]", "9000,1, 0,0, -1", ""]
        for c in self.camadas:
            L.append(f"[BG {c.nome}]")
            if c.animada:
                L += ["type = anim", f"actionno = {1000 + c.k}"]
            else:
                L += ["type = normal", f"spriteno = {c.k}, 0"]
            L += [f"id = {100 + c.k}", f"layerno = {1 if c.frente else 0}",
                  f"start = {num(c.x - TELA_L // 2)}, {num(c.y)}",
                  f"delta = {num(c.delta[0])}, {num(c.delta[1])}", "mask = 1"]
            if c.alfa:
                L += ["trans = addalpha", f"alpha = {c.alfa[0]}, {c.alfa[1]}"]
            elif c.mistura != "normal":
                L.append(f"trans = {MISTURAS[c.mistura]}")
            if any(c.repete):
                # camada normal: vão entre as cópias; camada anim: o motor mede de origem a origem
                gx, gy = (c.vao[0] + c.l, c.vao[1] + c.a) if c.animada else c.vao
                L += [f"tile = {c.repete[0]}, {c.repete[1]}", f"tilespacing = {gx}, {gy}"]
            if any(c.vel):
                L.append(f"velocity = {num(c.vel[0])}, {num(c.vel[1])}")
            for eixo, s in (("x", c.seno_x), ("y", c.seno_y)):
                if s:
                    L.append(f"sin.{eixo} = {num(s[0])}, {num(s[1])}, {num(s[2])}")
            L += [f"roundpos = {0 if c.suave else 1}", ""]
        for c in self.camadas:
            if c.animada:
                L.append(f"[Begin Action {1000 + c.k}]")
                marca = ""
                if c.alfa:
                    marca = f",,AS{c.alfa[0]}D{c.alfa[1]}"
                elif c.mistura != "normal":
                    marca = ",,A" if c.mistura == "soma" else ",,S"
                L += [f"{c.k},{n}, 0,0, {d}{marca}" for n, d in enumerate(c.ticks)]
                L.append("")
        for c in self.camadas:
            if c.controles:
                L += [f"[BGCtrlDef {c.nome}]", f"looptime = {int(c.ciclo)}", f"ctrlID = {100 + c.k}", ""]
                for n, ct in enumerate(c.controles):
                    L += [f"[BGCtrl {c.nome} {n}]", f"type = {ct['tipo']}",
                          "time = " + ", ".join(num(v) for v in par(ct.get("tempo"), (0,)))]
                    L += [f"{k} = " + (", ".join(num(v) for v in v) if isinstance(v, (list, tuple)) else num(v))
                          for k, v in ct.items() if k not in ("tipo", "tempo")]
                    L.append("")
        return "\r\n".join(L)

    def gravar(self, destino, furo_magenta=False):
        destino = Path(destino)
        destino.mkdir(parents=True, exist_ok=True)
        txt = self.texto_def()
        if furo_magenta:
            txt = txt.replace("debugbg = 0", "debugbg = 1")
        (destino / f"{self.id}.def").write_text(txt, encoding="utf-8", newline="")
        escrever_sff2(destino / f"{self.id}.sff", self.sprites())
        return destino / f"{self.id}.def"

    def previa(self, pasta, zoom=2):
        pasta = Path(pasta)
        pasta.mkdir(parents=True, exist_ok=True)
        fundo = (255, 0, 255, 255)
        for nome, camx in (("esq", -self.curso), ("centro", 0), ("dir", self.curso)):
            im = self.compor(camx, 0, 0, fundo=fundo).convert("RGB")
            im.resize((TELA_L * zoom, TELA_A * zoom), Image.NEAREST).save(pasta / f"{self.id}_{nome}.png")
        quadros = []
        n = 120  # 8 s de jogo a 15 quadros por segundo; a câmera vai e volta de ponta a ponta
        for i in range(n):
            camx = -self.curso * math.sin(2 * math.pi * i / n)
            im = self.compor(camx, 0, i * 4, fundo=fundo).convert("RGB")
            quadros.append(im.resize((TELA_L * zoom, TELA_A * zoom), Image.NEAREST))
        quadros[0].save(pasta / f"{self.id}.gif", save_all=True, append_images=quadros[1:], duration=67, loop=0)


def _colar(tela, q, x, y):
    """alpha_composite com recorte (a cópia pode sair da tela)."""
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + q.width, tela.width), min(y + q.height, tela.height)
    if x1 > x0 and y1 > y0:
        tela.alpha_composite(q.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


def gerar(desc, base, destino=RAIZ / "stages", previa=None, furo_magenta=False, aceita_furo=False):
    """desc: dict da descrição; base: pasta dos PNG. Devolve o caminho do .def gravado."""
    c = Cenario(desc, Path(base))
    furos = c.furos()
    for canto, n in furos:
        print(f"FURO: câmera em {canto}: {n} px da tela sem nada desenhado (vira faixa preta no jogo)")
    if furos and not aceita_furo:
        raise SystemExit("cenário recusado: aumente a camada do fundo ou use repete; veja docs/arcade/cenarios.md")
    arq = c.gravar(destino, furo_magenta)
    if previa:
        c.previa(previa)
    print(f"{arq} e .sff: {len(c.camadas)} camadas, {sum(len(x.quadros) for x in c.camadas)} sprites, "
          f"câmera de {-c.curso} a {c.curso}, sobe {c.subida}, chão em y={c.chao_y}")
    return arq


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("descricao", type=Path, help="cenarios/<id>/cenario.json")
    ap.add_argument("--destino", type=Path, default=RAIZ / "stages")
    ap.add_argument("--previa", type=Path, help="pasta para a simulação (3 PNG e 1 GIF)")
    ap.add_argument("--furo-magenta", action="store_true", help="debugbg = 1: furo aparece magenta no jogo (só teste)")
    ap.add_argument("--aceita-furo", action="store_true", help="grava mesmo com furo (só para investigar)")
    a = ap.parse_args()
    desc = json.loads(a.descricao.read_text(encoding="utf-8"))
    gerar(desc, a.descricao.parent, a.destino, a.previa, a.furo_magenta, a.aceita_furo)


if __name__ == "__main__":
    main()
