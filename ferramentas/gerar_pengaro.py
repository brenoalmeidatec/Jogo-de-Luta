#!/usr/bin/env python3
"""Gera o personagem Pengaró no formato MUGEN/IKEMEN GO em chars/pengaro/.

Lê sprites/pengaro/pixel/pengaro.png (9 poses) e escreve:
  pengaro.sff  sprites (SFF v2), com as poses, as intermediárias e os balões de fala
  pengaro.air  animações e caixas de colisão
  pengaro.cmd  comandos
  pengaro.cns  constantes e estados
  pengaro.def  ficha do personagem

Para mudar golpe, dano ou fala, edite este arquivo e rode:
  python ferramentas/gerar_pengaro.py
"""
import json
import math
import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from repertorio import golpes, quadros as quadros_golpe

RAIZ = Path(__file__).resolve().parent.parent
FOLHA = RAIZ / "sprites/pengaro/pixel/pengaro.png"
INFO = RAIZ / "sprites/pengaro/pixel/pengaro.json"
SAIDA = RAIZ / "chars/pengaro"
EFEITOS = RAIZ / "assets/efeitos"
ATAQUES_DESPERTADOS = {200, 210, 215, 230, 240, 245, 260, 400, 410, 430, 440, 600, 610, 650,
                      760, 761, 1000, 1001, 1100, 1101, 1200, 1201, 1300, 1301}
ATAQUES_DESPERTADOS.update(g.estado for h in (False, True) for g in golpes(h))
FAISCAS = {9200: "hit-spark", 9201: "crit-hit", 9202: "shield-block", 9204: "parry",
           9205: "ground-slam", 9206: "fireball"}

# Tela de trabalho de cada sprite: pés em (EIXO_X, EIXO_Y).
LARG, ALT = 360, 260
EIXO_X, EIXO_Y = 180, 220


# ------------------------------------------------------------------ imagens

def carregar_poses():
    folha = Image.open(FOLHA).convert("RGBA")
    info = json.loads(INFO.read_text(encoding="utf-8"))
    px, py = info["meta"]["pivot"]["x"], info["meta"]["pivot"]["y"]
    poses = {}
    for nome, f in info["frames"].items():
        r = f["frame"]
        rec = folha.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"]))
        tela = Image.new("RGBA", (LARG, ALT))
        tela.paste(rec, (EIXO_X - px, EIXO_Y - py))
        poses[nome] = tela
    e = info["frames"]["especial"]["frame"]
    bola = folha.crop((e["x"] + 186, e["y"] + 55, e["x"] + 213, e["y"] + 74))
    return poses, bola


def mistura(a, b, t):
    """Quadro de passagem entre duas poses: fica na pose mais próxima, inclinada (antecipação).

    Misturar as duas imagens deixaria dois corpos na tela, porque a paleta só tem cheio ou vazio.
    """
    return gira(a, -4, 0, 0) if t <= 0.5 else gira(b, 3, 0, 0)


def gira(img, graus, cx=0, cy=-55):
    """Gira em volta de um ponto dado em relação aos pés. Graus positivos inclinam para frente."""
    return img.rotate(-graus, resample=Image.NEAREST, center=(EIXO_X + cx, EIXO_Y + cy))


def move(img, dx=0, dy=0):
    tela = Image.new("RGBA", img.size)
    tela.paste(img, (dx, dy))
    return tela


def estica(img, sy):
    """Estica na vertical mantendo os pés no lugar (respiração, pulo)."""
    return img.transform(img.size, Image.AFFINE, (1, 0, 0, 0, 1 / sy, EIXO_Y - EIXO_Y / sy), Image.NEAREST)


def espelha(img):
    return move(img.transpose(Image.FLIP_LEFT_RIGHT), 2 * EIXO_X - LARG)


def com_bola(img, bola, dx, dy):
    tela = img.copy()
    tela.alpha_composite(bola, (EIXO_X + dx, EIXO_Y + dy))
    return tela


def com_lata(img):
    """Lata genérica, sem marca, na mão erguida da pose de defesa."""
    tela = img.copy()
    d = ImageDraw.Draw(tela)
    x, y = EIXO_X + 32, EIXO_Y - 106
    d.rectangle((x, y, x + 9, y + 15), fill=(196, 202, 214, 255), outline=(40, 25, 37, 255))
    d.rectangle((x + 1, y + 4, x + 8, y + 10), fill=(201, 58, 46, 255))
    return tela


def fonte(tamanho):
    for caminho in ("C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if Path(caminho).exists():
            return ImageFont.truetype(caminho, tamanho)
    return ImageFont.load_default()


def balao(texto):
    """Balão de fala em imagem própria, centrado acima do eixo."""
    f = fonte(11)
    linhas = texto.split("\n")
    caixas = [f.getbbox(linha) for linha in linhas]
    w = max(c[2] for c in caixas) + 14
    h = 15 * len(linhas) + 8
    tela = Image.new("RGBA", (LARG, ALT))
    d = ImageDraw.Draw(tela)
    x0, y0 = EIXO_X - w // 2, EIXO_Y - h - 8
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 6, fill=(250, 246, 232, 255), outline=(30, 20, 30, 255), width=2)
    d.polygon([(EIXO_X - 5, y0 + h), (EIXO_X + 5, y0 + h), (EIXO_X, EIXO_Y)], fill=(250, 246, 232, 255), outline=(30, 20, 30, 255))
    for i, linha in enumerate(linhas):
        d.text((x0 + 7, y0 + 4 + i * 15), linha, font=f, fill=(30, 20, 30, 255))
    return tela


# ------------------------------------------------------------------ SFF v2

class Sprites:
    def __init__(self):
        self.lista = []  # (grupo, indice, imagem, eixo_x, eixo_y)
        self.codigos = {}
        self.proximo = 10

    def add(self, nome, img, grupo=None, indice=0, eixo=(EIXO_X, EIXO_Y)):
        if grupo is None:
            grupo = self.proximo
            self.proximo += 1
        self.lista.append((grupo, indice, img, eixo[0], eixo[1]))
        self.codigos[nome] = (grupo, indice)
        return nome


def rle8(px):
    """Formato 2 do SFF v2. Bytes 0x40-0x7F são contagem, então valor assim precisa ir como run."""
    out = bytearray()
    i, n = 0, len(px)
    while i < n:
        v = px[i]
        run = 1
        while i + run < n and px[i + run] == v and run < 63:
            run += 1
        if run > 1 or (v & 0xC0) == 0x40:
            out += bytes((0x40 | run, v))
        else:
            out.append(v)
        i += run
    return bytes(out)


def paleta_global(imagens):
    """Uma paleta para todos os sprites. O índice 0 é o transparente."""
    amostra = Image.new("RGB", (LARG, ALT * len(imagens)), (0, 0, 0))
    mascara = Image.new("L", amostra.size, 0)
    for i, im in enumerate(imagens):
        amostra.paste(im.convert("RGB"), (0, ALT * i))
        mascara.paste(im.split()[3].point(lambda a: 255 if a >= 128 else 0), (0, ALT * i))
    cores = [p for p, m in zip(amostra.get_flattened_data(), mascara.get_flattened_data()) if m]
    pedaco = Image.new("RGB", (len(cores), 1))
    pedaco.putdata(cores)
    q = pedaco.quantize(colors=255, method=Image.MEDIANCUT)
    return q


def escrever_sff(destino, sprites):
    imagens = [s[2] for s in sprites.lista]
    q = paleta_global(imagens)
    pal = q.getpalette()[: 255 * 3]
    pal += [0] * (255 * 3 - len(pal))
    dados_pal = bytes((0, 0, 0, 0))
    for i in range(255):
        dados_pal += bytes((pal[i * 3], pal[i * 3 + 1], pal[i * 3 + 2], 255))

    ldata = bytearray(dados_pal)
    nos = bytearray()
    for grupo, indice, img, ex, ey in sprites.lista:
        caixa = img.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox() or (0, 0, 1, 1)
        rec = img.crop(caixa)
        ind = rec.convert("RGB").quantize(palette=q, dither=Image.NONE)
        alfa = rec.getchannel("A").tobytes()
        px = bytes(0 if alfa[i] < 128 else v + 1 for i, v in enumerate(ind.tobytes()))
        corpo = struct.pack("<I", len(px)) + rle8(px)
        nos += struct.pack("<HHHHhhHBBIIHH", grupo, indice, rec.width, rec.height,
                           ex - caixa[0], ey - caixa[1], 0, 2, 8, len(ldata), len(corpo), 0, 0)
        ldata += corpo

    ofs_pal = 512
    ofs_spr = ofs_pal + 16
    ofs_l = ofs_spr + len(nos)
    cab = bytearray(512)
    cab[0:12] = b"ElecbyteSpr\x00"
    cab[12:16] = bytes((0, 1, 0, 2))
    cab[24:28] = bytes((0, 1, 0, 2))
    struct.pack_into("<8I", cab, 36, ofs_spr, len(sprites.lista), ofs_pal, 1, ofs_l, len(ldata), ofs_l + len(ldata), 0)
    no_pal = struct.pack("<HHHHII", 1, 1, 256, 0, 0, 1024)
    destino.write_bytes(bytes(cab) + no_pal + bytes(nos) + bytes(ldata))


# ------------------------------------------------------------------ animações

CORPO = [(-24, 0, 24, -104)]
BAIXO = [(-28, 0, 28, -70)]
NO_AR = [(-24, -24, 24, -100)]
DEITADO = [(-60, 0, 60, -24)]


class Air:
    def __init__(self, sprites, arte_despertada=None):
        self.s = sprites
        self.txt = ["; Gerado por ferramentas/gerar_pengaro.py. Edite lá, não aqui.\n"]
        self.acoes = set()
        self.arte_despertada = arte_despertada or {}

    def acao(self, numero, quadros, caixa=CORPO, loop=None):
        """quadros: lista de (nome_sprite, ticks) ou (nome_sprite, ticks, caixa_de_golpe) ou com flip 'H'."""
        self.acoes.add(numero)
        t = [f"[Begin Action {numero}]"]
        if caixa:
            t.append(f"Clsn2Default: {len(caixa)}")
            for i, c in enumerate(caixa):
                t.append(f" Clsn2[{i}] = {c[0]},{c[1]},{c[2]},{c[3]}")
        for i, q in enumerate(quadros):
            nome, ticks = q[0], q[1]
            golpe = q[2] if len(q) > 2 else None
            flip = q[3] if len(q) > 3 else ""
            if loop == i:
                t.append("Loopstart")
            if golpe:
                t.append("Clsn1: 1")
                t.append(f" Clsn1[0] = {golpe[0]},{golpe[1]},{golpe[2]},{golpe[3]}")
            g, ind = self.s.codigos[nome]
            t.append(f"{g},{ind}, 0,0, {ticks}" + (f", {flip}" if flip else ""))
        self.txt.append("\n".join(t) + "\n")
        if numero in ATAQUES_DESPERTADOS or numero == 3100:
            variantes = []
            for i, (nome, ticks, *resto) in enumerate(quadros):
                if nome not in self.arte_despertada:
                    grupo, indice = self.s.codigos[nome]
                    original = next(img for g, i, img, _, _ in self.s.lista if (g, i) == (grupo, indice))
                    aura = Image.new("RGBA", original.size)
                    sombra = Image.new("RGBA", original.size, (92, 39, 138))
                    sombra.putalpha(original.getchannel("A"))
                    aura.alpha_composite(sombra, (-5, 2))
                    aura.alpha_composite(original)
                    self.arte_despertada[nome] = self.s.add(f"despertado_{nome}", aura)
                if resto and resto[0] and numero != 3100:
                    x1, y1, x2, y2 = resto[0]
                    recuo = min(8, (x2 - x1) // 4)
                    resto[0] = (x1 + recuo, y1, x2 - recuo, y2)
                if i == len(quadros) - 1 and ticks > 0 and 1000 <= numero < 1600:
                    ticks += 6
                variantes.append((self.arte_despertada[nome], ticks, *resto))
            self.acao(numero + 10000, variantes, caixa, loop)



def carregar_faiscas(sprites):
    acoes = {}
    for numero, nome in FAISCAS.items():
        dados = json.loads((EFEITOS / f"{nome}.json").read_text(encoding="utf-8"))
        pivo = tuple(dados["meta"]["pixelfx"]["pivot"])
        quadros = []
        with Image.open(EFEITOS / dados["meta"]["image"]) as imagem:
            folha = imagem.convert("RGBA")
            for indice, quadro in enumerate(dados["frames"]):
                r = quadro["frame"]
                sprite = folha.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"]))
                chave = f"fx_{nome}_{indice}"
                sprites.add(chave, sprite, numero, indice, pivo)
                quadros.append((chave, max(1, round(quadro["duration"] * 60 / 1000))))
        acoes[numero] = quadros
    return acoes


def montar_sprites(dados=None, retrato=None, hazaki=False):
    p, bola = dados if dados is not None else carregar_poses()
    s = Sprites()
    A = s.add

    # retratos que o IKEMEN usa no menu e nas barras
    rosto = p["parado"].crop((EIXO_X - 24, EIXO_Y - 112, EIXO_X + 32, EIXO_Y - 56))
    busto = p["parado"].crop((EIXO_X - 60, EIXO_Y - 118, EIXO_X + 60, EIXO_Y + 22))
    if retrato and retrato.exists():
        rosto = Image.open(retrato).convert("RGBA")
        rosto = rosto.crop(rosto.getbbox())
        busto = rosto.copy()
        busto.thumbnail((120, 140), Image.Resampling.LANCZOS)
        lado = min(rosto.size)
        x = (rosto.width - lado) // 2
        rosto = rosto.crop((x, 0, x + lado, lado))
    A("retrato_p", rosto.resize((25, 25), Image.Resampling.LANCZOS), 9000, 0, (0, 0))
    A("retrato_g", busto, 9000, 1, (0, 0))

    # em pé: respiração
    for i, sy in enumerate((1.0, 1.008, 1.016, 1.022, 1.016, 1.008)):
        A(f"parado{i}", estica(p["parado"], sy))
    # andando: balanço do passo
    for i, (g, y) in enumerate(((-2, 0), (0, -2), (2, -1), (0, -3))):
        A(f"anda{i}", move(gira(p["andando"], g, 0, 0), 0, y))
    # correndo: corpo jogado para frente
    for i, (g, y) in enumerate(((12, 0), (15, -3), (12, -1), (9, -3))):
        A(f"corre{i}", move(gira(p["andando"], g, 0, 0), 0, y))
    A("recua", gira(p["defesa"], -8, 0, 0))
    # agachar
    A("agacha0", mistura(p["parado"], p["agachado"], 0.5))
    A("agacha1", p["agachado"])
    A("agacha2", estica(p["agachado"], 1.015))
    # pulo
    A("prepulo", estica(mistura(p["parado"], p["agachado"], 0.6), 0.97))
    # Mortal visual: a rotação não altera a trajetória nem as caixas do salto.
    for i in range(12):
        A(f"mortal{i}", gira(p["pulo"], i * 30))
    A("pulo_sobe", estica(p["pulo"], 1.05))
    A("pulo_topo", p["pulo"])
    A("pulo_desce", gira(p["pulo"], 6))
    A("pouso", mistura(p["agachado"], p["parado"], 0.35))
    # defesa
    A("defesa", p["defesa"])
    A("defesa_ai", move(gira(p["defesa"], -4, 0, 0), -3))
    A("defesa_baixa", p["agachado"])
    # apanhando
    A("apanha0", mistura(p["parado"], p["apanhando"], 0.6))
    A("apanha1", p["apanhando"])
    A("apanha2", gira(p["apanhando"], -8, 0, 0))
    for i, g in enumerate((-25, -50, -75)):
        A(f"cai{i}", gira(p["apanhando"], g))
    deitado = move(gira(p["apanhando"], -90, 0, 0), 50, -47)
    A("deitado", deitado)
    A("levanta0", mistura(deitado, p["agachado"], 0.5))
    A("levanta1", p["agachado"])
    A("levanta2", mistura(p["agachado"], p["parado"], 0.5))
    for i, g in enumerate((-4, 0, 4, 0)):
        A(f"tonto{i}", gira(p["apanhando"], g, 0, 0))
    # rolamento: a pose agachada dando a volta
    for i in range(8):
        A(f"rola{i}", gira(p["agachado"], 45 * i, 0, -42))
    # golpes
    # quadros desenhados de novo, um por um (veja ferramentas/recortar_quadros.py)
    for nome in ("parado", "anda", "soco"):
        if hazaki:
            origens = {"parado": p["parado"], "anda": p["andando"], "soco": p["soco"]}
            for i in range(8):
                if nome == "soco":
                    origem = p["defesa"] if i < 3 or i > 5 else p["soco"]
                    quadro = move(gira(origem, (-3, -6, -2, 3, 0, 1, -4, 0)[i], 0, 0), (0, -2, -1, 0, 4, 2, 1, 0)[i])
                elif nome == "anda":
                    origem = p["andando"] if i % 4 < 2 else p["andando2"]
                    quadro = move(origem, 0, (0, -2, -3, -1)[i % 4])
                else:
                    quadro = estica(origens[nome], 1 + .012 * math.sin(i * math.tau / 8))
                A(f"q_{nome}{i}", quadro)
            continue
        for i, arquivo in enumerate(sorted((RAIZ / "sprites/pengaro/quadros" / nome).glob("*.png"))):
            tela = Image.new("RGBA", (LARG, ALT))
            tela.alpha_composite(Image.open(arquivo).convert("RGBA"), (EIXO_X - 104, EIXO_Y - 119))
            A(f"q_{nome}{i}", tela)
    A("soco0", mistura(p["parado"], p["soco"], 0.5))
    A("soco1", p["soco"])
    A("soco2", move(p["soco"], 6))
    A("soco3", mistura(p["soco"], p["parado"], 0.5))
    A("chute0", mistura(p["parado"], p["chute"], 0.5))
    A("chute1", p["chute"])
    A("chute2", move(p["chute"], 5))
    A("chute3", mistura(p["chute"], p["parado"], 0.5))
    A("baixo_soco", move(p["agachado"], 8))
    A("baixo_cima0", mistura(p["agachado"], p["soco"], 0.5))
    A("baixo_cima1", gira(p["soco"], -35, 0, -30))
    A("rasteira0", mistura(p["agachado"], p["rasteira"], 0.5))
    A("rasteira1", p["rasteira"])
    A("rasteira2", move(p["rasteira"], 6))
    A("rasteira3", mistura(p["rasteira"], p["agachado"], 0.5))
    A("ar_soco", gira(p["soco"], 8))
    A("ar_chute", gira(p["chute"], 14))
    A("ar_cotovelo", gira(p["soco"], 28, 0, -65))
    A("pisa", move(gira(p["chute"], 43, 0, -45), 0, 6))
    A("parry", move(gira(p["defesa"], 8 if hazaki else -8, 0, 0), 3))
    A("bicicleta", gira(p["chute"], -40))
    A("agarra", move(p["soco"], 4))
    A("joga", espelha(mistura(p["soco"], p["parado"], 0.3)))
    # compasso e armada: giros
    for i, g in enumerate((0, 90, 180, 270)):
        A(f"gira{i}", gira(p["chute"], g))
    A("kick_alto", gira(p["chute"], -55, 0, -30))
    A("especial", p["especial"])
    # bola: quadros do projétil, grande e pequena
    for i, g in enumerate((0, 90, 180, 270)):
        b = bola.rotate(g, resample=Image.NEAREST, expand=True)
        A(f"bola{i}", b, eixo=(b.width // 2, b.height // 2))
        g2 = b.resize((b.width * 3, b.height * 3), Image.NEAREST)
        A(f"bolao{i}", g2, eixo=(g2.width // 2, g2.height // 2))
    # bola quicando: o eixo sobe e desce, então a bola pula sem mudar a trajetória
    for i in range(8):
        b = bola.rotate(90 * (i % 4), resample=Image.NEAREST, expand=True)
        altura = round(30 * abs(math.sin(math.pi * i / 8)))
        A(f"quica{i}", b, eixo=(b.width // 2, b.height // 2 + altura))
    # embaixadinha (provocação, intro e vitória)
    for i, y in enumerate((-30, -52, -68, -52)):
        A(f"embaixada{i}", com_bola(p["parado"], bola, 40, y))
    # despertar: bebe a lata
    A("lata0", p["defesa"] if hazaki else com_lata(p["defesa"]))
    A("lata1", gira(p["defesa"] if hazaki else com_lata(p["defesa"]), -10, 0, 0))
    for i, angulo in enumerate((-6, 2, 7, 1)):
        tela = p["parado"].copy()
        d = ImageDraw.Draw(tela)
        x, y = EIXO_X, EIXO_Y
        # Armação esportiva e lente roxa na altura dos olhos.
        d.line((x - 6, y - 98, x + 17, y - 99), fill="#d2d8df", width=2)
        d.polygon([(x + 3, y - 99), (x + 19, y - 100),
                   (x + 16, y - 94), (x + 7, y - 93)], fill="#35224e")
        d.line((x + 7, y - 98, x + 16, y - 99), fill="#b378d1")
        A(f"juliet{i}", gira(tela, angulo, 0, 0))
    A("lata2", estica(p["parado"], 1.03))
    # balões
    for chave, texto in BALOES.items():
        A(f"balao_{chave}", balao(texto))
    return s


# As falas ficam aqui para o Breno editar. A gagueira é só texto, nunca muda o tempo do golpe.
BALOES = {
    "intro": "B-b-bora jogar? Ca-capoeira ou\npe-pelada, que eu de-de-dou conta!",
    "intro_trava": "P-p-p-p-p...",
    "locutor": "FIGHT, CARALHO, A GENTE\nNÃO TEM O DIA TODO!",
    "round": "H-h-hoje tem resenha, ca-caralho.",
    "primeiro": "I-ih, já co-co-começou na sacanagem?",
    "provoca": "F-f-f-f-f-f...",
    "provoca_fim": "...ah, vai se foder, porra.",
    "provoca_cai": "Ai, ca-caralho! A bo-bola!",
    "bola_trava": "Bo-bo-bo-bo...",
    "bola_ok": "...BOLA DE SOMBRA!",
    "compasso_trava": "Co-co-co-co...",
    "compasso_ok": "...COMPASSO, PORRA!",
    "armada_trava": "A-a-a-a...",
    "armada_ok": "...ARMADA!",
    "caneta_trava": "Ca-ca-ca-ca...",
    "caneta_ok": "...CANETA, FILHO DA PUTA!",
    "errou": "...deixa pra lá, porra.",
    "bola_liso": "BOLA DE SOMBRA, CARALHO!",
    "compasso_liso": "COMPASSO NA TUA CARA!",
    "armada_liso": "ARMADA, VEM QUE TEM!",
    "caneta_liso": "CANETA, PASSOU POR BAIXO!",
    "derrota": "F-f-f-foi falta, porra!\nCa-cadê o VAR, ca-caralho?",
    "locutor_ko": "K.O.! ...ou, no caso dele,\nK-k-k-k-K.O.!",
    "vitoria0": "F-f-foi de letra,\nfilho da puta.",
    "vitoria1": "V-v-vai lá contar pra tua mãe\nque tu a-a-apanhou do gago.",
    "vitoria2": "Mi-minhas bolas... MINHA BOLA\ntá sempre no pé, pa-pa-parceiro.",
    "golaco": "O-o-o-olha o... GOLAÇOOOO, CARALHO!",
    "lata": "A-a-a-agora sim, porra!\nSegura que eu vou me-me-meter!",
    "pelada": "CHAMA A RAPAZIADA, CARALHO! TÁ LISO AGORA!",
    "ressaca": "...e-e-e aí, cadê a-a-a porra da outra lata?",
    "escapou": "A-a-achou que ia me pe-pegar?",
}
ID_BALAO = {chave: 9100 + i for i, chave in enumerate(BALOES)}

VITORIAS = [
    "F-f-foi de letra, filho da puta.",
    "T-t-tá achando que é pe-pelada de domingo, é, ca-caralho?",
    "V-v-vai lá contar pra tua mãe que tu a-a-apanhou do gago.",
    "Eu chu-chupo... chu-chu-CHUTO melhor que tu, porra!",
    "T-tu ficou pa-parado igual cone. Ma-mas cone pelo menos fica de pé.",
    "D-d-demorei pra falar, mas tu de-de-demorou mais pra levantar.",
    "Mi-minhas bolas... MINHA BOLA tá sempre no pé, pa-pa-parceiro.",
    "Olha só, falei inteiro! Agora chama tua irmã que eu vou ensinar ela a gingar, hein!",
]


def montar_air(s, faiscas, hazaki=False, arte_despertada=None):
    a = Air(s, arte_despertada)
    Q = a.acao
    Q(0, [(f"q_parado{i}", 6) for i in range(8)])
    Q(9203, [(f"juliet{i}", 6) for i in range(4)])
    Q(5, [("parado0", 3), ("anda0", 3)])
    Q(6, [("agacha0", 3), ("parado0", 3)], BAIXO)
    Q(10, [("agacha0", 3)], BAIXO)
    Q(11, [("agacha1", 12), ("agacha2", 12)], BAIXO)
    Q(12, [("agacha0", 3)], BAIXO)
    Q(20, [(f"q_anda{i}", 5) for i in range(8)])
    Q(21, [(f"q_anda{i}", 5) for i in range(7, -1, -1)])
    Q(40, [("prepulo", 4)])
    for n in (41, 42, 43):
        Q(n, [("pulo_sobe", 8), ("pulo_topo", -1)] if hazaki else
          [(f"mortal{i}", 2) for i in range(12)] + [("pulo_topo", -1)], NO_AR)
    for n in (44, 45, 46):
        Q(n, [("pulo_topo", 8), ("pulo_desce", -1)], NO_AR)
    Q(47, [("pouso", 3), ("parado0", 2)])
    Q(100, [(f"corre{i}", 4) for i in range(4)])
    Q(105, [("recua", -1)], NO_AR)
    for n in (120, 130, 140):
        Q(n, [("defesa", -1)])
    for n in (121, 131, 141):
        Q(n, [("defesa_baixa", -1)], BAIXO)
    for n in (122, 132, 142):
        Q(n, [("defesa", -1)], NO_AR)
    Q(150, [("defesa_ai", -1)])
    Q(151, [("defesa_baixa", -1)], BAIXO)
    Q(152, [("defesa_ai", -1)], NO_AR)
    Q(170, [("apanha1", 40), ("levanta1", -1)])
    Q(181, [(f"embaixada{i}", 7) for i in range(4)])
    Q(190, [(f"embaixada{i}", 7) for i in (0, 1, 2, 3, 0, 1, 2, 3)] + [("parado0", 6)])
    Q(191, [(f"embaixada{i}", 7) for i in range(4)])
    Q(192, [(f"embaixada{i}", 7) for i in range(4)])
    Q(195, [(f"embaixada{i}", 6) for i in (0, 1, 2, 3, 0, 1, 2, 3, 0, 1)])

    # normais: caixa de golpe em (x1, y1, x2, y2), x para frente, y negativo para cima
    def soco(n, lig, ativo, rec, caixa):
        um = max(1, lig // 3)
        Q(n, [("q_soco1", um), ("q_soco2", um), ("q_soco3", lig - 2 * um), ("q_soco4", 1, caixa),
              ("q_soco5", ativo - 1, caixa), ("q_soco6", rec // 2), ("q_soco7", rec - rec // 2)])

    def chute(n, lig, ativo, rec, caixa):
        Q(n, [("chute0", lig), ("chute1", 1, caixa), ("chute2", ativo - 1, caixa), ("chute3", rec)])

    soco(200, 4, 3, 7, (15, -92, 74, -64))
    soco(210, 7, 4, 16, (15, -92, 78, -64))
    soco(215, 4, 3, 14, (12, -94, 66, -62))
    chute(230, 5, 3, 9, (12, -56, 58, -42))
    chute(240, 9, 4, 18, (12, -80, 80, -58))
    chute(245, 5, 3, 16, (10, -76, 50, -50))
    Q(260, [("chute0", 12), ("chute1", 1, (15, -96, 75, -60)), ("chute2", 3, (15, -96, 75, -60)), ("chute3", 20)])
    Q(400, [("agacha1", 4), ("baixo_soco", 3, (15, -56, 54, -42)), ("agacha1", 7)], BAIXO)
    Q(410, [("baixo_cima0", 6), ("baixo_cima1", 5, (5, -122, 42, -60)), ("agacha0", 18)], BAIXO)
    Q(430, [("rasteira0", 5), ("rasteira1", 3, (12, -18, 62, -4)), ("rasteira3", 10)], BAIXO)
    Q(440, [("rasteira0", 10), ("rasteira1", 1, (12, -18, 78, -2)), ("rasteira2", 3, (12, -18, 78, -2)), ("rasteira3", 22)], BAIXO)
    Q(600, [("pulo_topo", 5), ("ar_soco", 8, (8, -86, 50, -62)), ("pulo_topo", -1)], NO_AR)
    Q(610, [("pulo_topo", 6), ("ar_chute", 10, (6, -60, 62, -30)), ("pulo_topo", -1)], NO_AR)
    Q(650, [("pulo_topo", 7), ("bicicleta", 6, (6, -70, 70, -20)), ("pulo_topo", -1)], NO_AR)
    Q(700, [(f"rola{i}", 4) for i in range(8)], [])
    Q(705, [(f"rola{i}", 4) for i in (7, 6, 5, 4, 3, 2, 1, 0)], [])
    Q(800, [("agarra", 3, (10, -90, 42, -50))])
    Q(810, [("agarra", 14), ("joga", 16)])
    # especiais
    if not hazaki:
        Q(1000, [("rasteira0", 8), ("especial", 5), ("rasteira1", 6), ("rasteira3", 22)], BAIXO)
        Q(1001, [("rasteira0", 8), ("especial", 5), ("rasteira1", 6), ("rasteira3", 26)], BAIXO)
    Q(1005, [(f"quica{i}", 4) for i in range(8)], [(-12, -40, 12, 10)])
    Q(1006, [("bola0", 3), ("bola2", 3)], [])
    giro = (-40, -80, 90, -20)
    if not hazaki:
        for i in (0, 1):
            Q(1100+i, [("rasteira0", 8)] + [(f"gira{j}", 4, giro) for j in range(4)] + [("rasteira3", 14+6*i)])
            Q(1200+i, [("baixo_cima0", 4), ("kick_alto", 6, (0, -130, 60+8*i, -30)), ("gira1", 8), ("pulo_topo", -1)], NO_AR)
            Q(1300+i, [("rasteira0", 10), ("rasteira1", 8, (10, -20, 70, -4)), ("rasteira3", 20+6*i)], BAIXO)
    # super e despertar
    Q(2000, [("lata0", 14), ("lata1", 18), ("juliet0" if hazaki else "lata2", 8)])
    if not hazaki:
        Q(3000, [("embaixada0", 6), ("embaixada1", 6), ("embaixada2", 6), ("rasteira0", 6), ("especial", 6), ("rasteira1", 8), ("rasteira3", 20)], BAIXO)
    Q(3005, [(f"bolao{i}", 3) for i in range(4)], [(-40, -30, 40, 30)])
    Q(3006, [("bolao0", 3), ("bolao2", 3)], [])
    caixa_p = (0, -110, 90, -10)
    Q(3100, [("chute0", 4)] + [(n, 4, caixa_p) for n in ("soco1", "chute1", "rasteira1", "soco2", "chute2", "gira1", "rasteira2", "kick_alto")] + [("chute3", 20)])
    for g in golpes(hazaki):
        Q(g.estado, quadros_golpe(g), NO_AR if g.tipo == "A" else CORPO)
    Q(760, [("parry", 4, (-8, -105, 46, -12)), ("recua", 10), ("defesa", 10)])
    Q(761, [("parry", 3)])

    # apanhando (nomes de ação fixos do motor)
    leve = [("apanha0", 3), ("apanha1", 8)]
    pesado = [("apanha0", 3), ("apanha1", 6), ("apanha2", 6)]
    for base in (5000, 5010):
        for n, q in ((0, leve), (1, pesado), (2, pesado)):
            Q(base + n, q)
            Q(base + 5 + n, [("apanha0", 4), ("parado0", 4)])
    for base in (5020,):
        for n, q in ((0, leve), (1, pesado), (2, pesado)):
            Q(base + n, q, BAIXO)
            Q(base + 5 + n, [("agacha0", 8)], BAIXO)
    Q(5030, [("apanha1", -1)], NO_AR)
    Q(5035, [("apanha1", 6)], NO_AR)
    Q(5040, [("cai0", -1)], NO_AR)
    Q(5050, [("cai0", 8), ("cai1", 8), ("cai2", -1)], NO_AR)
    Q(5051, [("cai0", 8), ("cai1", -1)], NO_AR)
    Q(5061, [("cai1", -1)], NO_AR)
    Q(5070, [("cai0", 8), ("cai1", -1)], NO_AR)
    Q(5080, [("cai1", 8), ("cai2", -1)], NO_AR)
    Q(5090, [("cai2", -1)], NO_AR)
    Q(5100, [("cai2", 3), ("deitado", 3)], DEITADO)
    Q(5101, [("cai2", 3), ("deitado", 3)], DEITADO)
    Q(5110, [("deitado", -1)], DEITADO)
    Q(5120, [("levanta0", 8), ("levanta1", 8), ("levanta2", 8)], BAIXO)
    Q(5150, [("deitado", -1)], DEITADO)
    Q(5160, [("cai2", 6), ("deitado", -1)], DEITADO)
    Q(5170, [("cai2", 6), ("deitado", -1)], DEITADO)
    Q(5200, [(f"rola{i}", 3) for i in range(8)], [])
    Q(5210, [(f"rola{i}", 3) for i in range(8)], [])
    Q(5300, [(f"tonto{i}", 8) for i in range(4)])

    for chave, numero in ID_BALAO.items():
        Q(numero, [(f"balao_{chave}", -1)], [])
    for numero, quadros in faiscas.items():
        Q(numero, quadros, [])
    return a


# ------------------------------------------------------------------ CNS

def estado(numero, tipo="S", mov="A", fis="S", anim=None, juggle=None, velset="0,0", extra=""):
    t = [f"[Statedef {numero}]", f"type = {tipo}", f"movetype = {mov}", f"physics = {fis}", "ctrl = 0",
         "sprpriority = 2"]
    if anim is not None:
        t.append(f"anim = {anim}")
    if juggle is not None:
        t.append(f"juggle = {juggle}")
    if velset:
        t.append(f"velset = {velset}")
    resultado = "\n".join(t) + extra + "\n\n"
    if anim in ATAQUES_DESPERTADOS or anim == 3100:
        gatilho = "" if anim == 3100 else "trigger1 = var(20) > 0\n"
        resultado += (f"[State {numero}, Arte despertada]\ntype = ChangeAnim\n"
                      f"trigger1 = Time = 0\n{gatilho}value = {anim + 10000}\n\n")
    return resultado


def hitdef(numero, trigger, attr, dano, tipo="Light", guarda="MA", alvo="MAF", pausa=(8, 8), hit=12, escorrega=5,
           vel="-4", ar="-1.4,-3", queda=False, recupera=True, chao="High", pesado=False, extra=""):
    t = [f"[State {numero}, Golpe]", "type = HitDef", f"trigger1 = {trigger}", f"attr = {attr}",
         f"damage = {dano}, 0", f"animtype = {tipo}", f"guardflag = {guarda}", f"hitflag = {alvo}",
         "priority = 4, Hit", f"pausetime = {pausa[0]}, {pausa[1]}", "sparkxy = -10, -70",
         f"sparkno = S{9201 if pesado else 9200}", "guard.sparkno = S9202",
         f"hitsound = F{'5,2' if pesado else '5,0'}", "guardsound = F6,0", f"ground.type = {chao}",
         f"ground.slidetime = {escorrega}", f"ground.hittime = {hit}", f"ground.velocity = {vel}",
         f"air.velocity = {ar}"]
    if queda:
        t += ["fall = 1", f"fall.recover = {1 if recupera else 0}"]
    return "\n".join(t) + "\n" + extra + "\n"


def fim(numero, destino=0):
    return (f"[State {numero}, Fim]\ntype = ChangeState\ntrigger1 = AnimTime = 0\nvalue = {destino}\nctrl = 1\n\n")


def fala(numero, chave, trigger="Time = 0"):
    gatilhos = "\n".join(f"trigger1 = {g.strip()}" for g in trigger.split(" & "))
    return (f"[State {numero}, Fala]\ntype = Explod\n{gatilhos}\nanim = {ID_BALAO[chave]}\n"
            "id = 700\nownpal = 1\npostype = p1\npos = 0, -125\nbindtime = -1\nremovetime = 70\n"
            "sprpriority = 6\nfacing = Facing\nignorehitpause = 1\n\n")


def nome_travado(numero, golpe, fim_sem_acerto="AnimTime = 0"):
    """O nome do golpe trava na gagueira e só sai inteiro se acertar. No Despertar ele fala liso.

    É só balão: nada aqui muda o tempo do golpe.
    """
    return (fala(numero, f"{golpe}_trava", "Time = 0 & var(20) = 0")
            + fala(numero, f"{golpe}_liso", "Time = 0 & var(20) > 0")
            + f"[State {numero}, Limpa fala]\ntype = RemoveExplod\ntrigger1 = MoveHit = 1\ntrigger1 = var(20) = 0\n"
              "id = 700\n\n"
            + fala(numero, f"{golpe}_ok", "MoveHit = 1 & var(20) = 0")
            + fala(numero, "errou", f"{fim_sem_acerto} & !MoveContact & var(20) = 0"))


def normal(numero, attr, dano, trigger, *, fis="S", tipo_st="S", leve=False, **k):
    t = estado(numero, tipo_st, "A", fis, anim=numero, juggle=5 if tipo_st == "A" else 2,
               velset=None if tipo_st == "A" else "0,0")
    if leve:
        t += f"[State {numero}, Corrente]\ntype = VarAdd\ntrigger1 = Time = 0\nvar(5) = 1\n\n"
    t += hitdef(numero, trigger, attr, dano, **k)
    if tipo_st == "A":
        return t
    t += fim(numero, 11 if tipo_st == "C" else 0)
    return t


CNS_TOPO = """; Gerado por ferramentas/gerar_pengaro.py. Edite lá, não aqui.
; var(1) condição de cancelar, var(5) fracos em sequência, var(6) lado do pulo,
; var(7) super pulo, var(20) tempo de Despertar, var(21) ressaca

[Data]
life = 1000
power = 3000
attack = 100
defence = 100
fall.defence_up = 50
liedown.time = 45
airjuggle = 15
sparkno = 2
guard.sparkno = 40
KO.echo = 0
volume = 0
IntPersistIndex = 60
FloatPersistIndex = 40

[Size]
xscale = 1
yscale = 1
ground.back = 16
ground.front = 18
air.back = 14
air.front = 14
height = 70
attack.dist = 160
proj.attack.dist = 90
proj.doscale = 0
head.pos = 6, -104
mid.pos = 0, -62
shadowoffset = 0
draw.offset = 0,0

[Velocity]
walk.fwd = 2.7
walk.back = -2.2
run.fwd = 5.6, 0
run.back = -5.2,-3.4
jump.neu = 0,-8.4
jump.back = -2.8
jump.fwd = 2.8
runjump.back = -2.8,-8.1
runjump.fwd = 4.4,-8.1
airjump.neu = 0,-8.1
airjump.back = -2.55
airjump.fwd = 2.5
air.gethit.groundrecover = -.15,-3.5
air.gethit.airrecover.mul = .5,.2
air.gethit.airrecover.add = 0,-4.5
air.gethit.airrecover.back = -1
air.gethit.airrecover.fwd = 0
air.gethit.airrecover.up = -2
air.gethit.airrecover.down = 1.5

[Movement]
airjump.num = 0
airjump.height = 35
yaccel = .44
stand.friction = .85
crouch.friction = .82
stand.friction.threshold = 2
crouch.friction.threshold = .05
air.gethit.groundlevel = 25
air.gethit.groundrecover.ground.threshold = -20
air.gethit.groundrecover.groundlevel = 10
air.gethit.airrecover.threshold = -1
air.gethit.airrecover.yaccel = .35
air.gethit.trip.groundlevel = 15
down.bounce.offset = 0, 20
down.bounce.yaccel = .4
down.bounce.groundlevel = 12
down.friction.threshold = .05

"""

# Pré-pulo com os 4 pulos do KOF: pulinho (toca), normal (segura),
# hiper pulinho (baixo antes, toca) e super pulo (baixo antes, segura).
CNS_PULOS = """[Statedef 40]
type = S
physics = S
anim = 40
ctrl = 0
sprpriority = 1

[State 40, Lado]
type = VarSet
trigger1 = Time = 0
var(6) = (command = "holdfwd") - (command = "holdback")

[State 40, Super]
type = VarSet
trigger1 = Time = 0
var(7) = (command = "superpulo") || (prevstateno = 100)

[State 40, Sobe]
type = VelSet
trigger1 = AnimTime = 0
x = var(6) * ifelse(var(7), 4.4, 2.8)
y = ifelse(command = "holdup", ifelse(var(7), -9.3, -8.4), -6.6)

[State 40, Fim]
type = ChangeState
trigger1 = AnimTime = 0
value = 50
ctrl = 1

"""

CNS_INTRO_BASE = """[Statedef 170]
type = S
ctrl = 0
anim = 170
velset = 0,0

[State 170, 1]
type = NotHitBy
trigger1 = 1
value = SCA
time = 1

[Statedef 180]
type = S

[State 180, 1]
type = ChangeState
trigger1 = Time = 0
value = 181

[Statedef 181]
type = S
ctrl = 0
anim = 181
velset = 0,0

[State 181, 1]
type = NotHitBy
trigger1 = 1
value = SCA
time = 1

[Statedef 191]
type = S
ctrl = 0
anim = 190
velset = 0,0

[State 191, Fala]
type = Explod
trigger1 = Time = 4
anim = %d
ownpal = 1
postype = p1
pos = 0, -125
bindtime = -1
removetime = 70
sprpriority = 6
facing = Facing

[State 191, Fim]
type = AssertSpecial
trigger1 = AnimTime < 0
flag = Intro

[State 191, Volta]
type = ChangeState
trigger1 = AnimTime = 0
value = 0

""" % ID_BALAO["intro"]

CNS_INTRO = CNS_INTRO_BASE.replace(
    "[State 191, Fala]\ntype = Explod\ntrigger1 = Time = 4\n",
    "[State 191, Sorteio]\ntype = VarSet\ntrigger1 = Time = 0\nvar(34) = Random < 250\n\n"
    + fala(191, "intro_trava", "Time = 4 & var(34) = 1")
    + fala(191, "locutor", "Time = 44 & var(34) = 1")
    + "[State 191, Fala]\ntype = Explod\ntrigger1 = Time = 4\ntrigger1 = var(34) = 0\n",
).replace(
    "[Statedef 191]",
    "[State 181, Sorteio]\ntype = VarSet\ntrigger1 = Time = 0\nvar(35) = Random % 3\n\n"
    + fala(181, "vitoria0", "Time = 20 & var(35) = 0")
    + fala(181, "vitoria1", "Time = 20 & var(35) = 1")
    + fala(181, "vitoria2", "Time = 20 & var(35) = 2")
    + "[Statedef 191]",
)


def projetil(numero, trigger, anim, hit_anim, vel, dano, attr, hits=1, intervalo=0, id_=1000, ofs="70, -32", queda=False):
    t = [f"[State {numero}, Bola]", "type = Projectile", f"trigger1 = {trigger}", f"projid = {id_}",
         f"projanim = {anim}", f"projhitanim = {hit_anim}", f"projremanim = {hit_anim}",
         f"projhits = {hits}", f"projmisstime = {intervalo}", "projpriority = 2", f"offset = {ofs}",
         f"velocity = {vel}, 0", f"attr = {attr}", f"damage = {dano}, 4", "animtype = Med", "guardflag = MA",
         "hitflag = MAF", "pausetime = 2, 10", "sparkxy = 0, 0", "hitsound = F5,1", "guardsound = F6,0",
         "ground.type = High", "ground.slidetime = 12", "ground.hittime = 18", "ground.velocity = -4",
         "air.velocity = -2,-3.5"]
    if queda:
        t += ["fall = 1", "fall.recover = 0"]
    return "\n".join(t) + "\n\n"


def superpausa(numero, trigger):
    return (f"[State {numero}, Pausa]\ntype = SuperPause\ntrigger1 = {trigger}\ntime = 30\nanim = 100\n"
            "pos = 10, -60\nsound = F20,0\nmovetime = 0\ndarken = 1\n\n"
            f"[State {numero}, Rastro]\ntype = AfterImage\ntrigger1 = {trigger}\ntime = 40\nlength = 8\n\n")


def cns_repertorio(hazaki):
    c = []
    for g in golpes(hazaki):
        n = g.estado
        tipo = g.tipo
        fisica = "A" if tipo == "A" else "N"
        classe = "HA" if g.custo else "SA" if n >= 1000 else "NA"
        if hazaki and n in (1100, 1101):
            c.append(estado(n, "S", "A", "N", anim=760))
            atributos = "SCA, NA, SA" if n == 1101 else "S, NA, SA"
            c.append(reversao(n, n + 2, atributos, "Time < 4"))
            c.append(fim(n))
            n += 2
        c.append(estado(n, tipo, "A", fisica, anim=g.estado, juggle=5,
                        velset=None if tipo == "A" else "0,0"))
        if g.custo:
            c.append(superpausa(n, "Time = 0"))
            c.append(f"[State {n}, Estoque]\ntype = PowerAdd\ntrigger1 = Time = 0\nvalue = -{g.custo}\n\n")
        if g.avanco:
            c.append(f"[State {n}, Avanço]\ntype = VelSet\ntrigger1 = AnimElem = 2\n"
                     f"x = {g.avanco} * ifelse(var(20) > 0, 1.22, 1)\n\n")
            c.append(f"[State {n}, Freia]\ntype = VelSet\ntrigger1 = AnimElem = {len(g.poses)}\nx = 0\n\n")
        if hazaki and n in (1500, 1501):
            c.append(f"[State {n}, Salta]\ntype = VelSet\ntrigger1 = Time = 1\ny = -4.5\n\n"
                     f"[State {n}, No ar]\ntype = StateTypeSet\ntrigger1 = Time = 1\nstatetype = A\n\n"
                     f"[State {n}, Gravidade]\ntype = VelAdd\ntrigger1 = statetype = A\ny = .43\n\n"
                     f"[State {n}, Chão]\ntype = PosSet\ntrigger1 = statetype = A && Pos Y >= 0 && Vel Y > 0\ny = 0\n\n"
                     f"[State {n}, Aterrissa]\ntype = StateTypeSet\ntrigger1 = statetype = A && Pos Y >= 0 && Vel Y > 0\nstatetype = S\n\n"
                     f"[State {n}, Firma os pés]\ntype = VelSet\ntrigger1 = statetype = S && Time > 1\ny = 0\n\n")
        impactos = len(g.poses) - 2 if g.custo else 1
        for i in range(impactos):
            final = i == impactos - 1
            condicao = f"AnimElem = {i+2}"
            if i:
                condicao += " && MoveHit"
            c.append(hitdef(n, condicao, f"{tipo}, {classe}", g.dano // impactos,
                            tipo="Heavy" if final else "Medium", guarda=g.guarda,
                            pausa=(6, 8), hit=19 if final else 21,
                            vel=g.lancamento if g.queda and final else "-3" if final else "-1", ar=g.lancamento,
                            queda=g.queda and final, pesado=final and g.dano >= 75,
                            chao="Low" if g.guarda == "L" else "High"))
        if tipo != "A":
            if 1500 <= n <= 1501 or (hazaki and n in (1300, 1301, 3200)):
                efeito = 9206 if hazaki else 9205
                c.append(f"[State {n}, Impacto visual]\ntype = Explod\ntrigger1 = AnimElem = 2\n"
                         f"trigger1 = var(20) > 0\nanim = {efeito}\npostype = p1\npos = 30, -15\n"
                         "removetime = -2\nsprpriority = 4\nownpal = 1\n\n")
            if not hazaki and n == 1501:
                c.append(f"[State {n}, Quique]\ntype = TargetState\n"
                         "trigger1 = MoveHit = 1 && NumTarget > 0 && var(20) > 0 && !var(24)\nvalue = 763\n\n"
                         f"[State {n}, Registra quique]\ntype = VarSet\n"
                         "trigger1 = MoveHit = 1 && NumTarget > 0 && var(20) > 0\nvar(24) = 1\n\n")
            c.append(fim(n))
    c.append(estado(760, "S", "A", "N", anim=760))
    c.append(reversao(760, 761, "SCA, NA, SA, HA", "Time < 4"))
    c.append(fim(760))
    c.append(estado(761, "S", "I", "N", anim=761))
    c.append(fim(761))
    c.append("""[Statedef 762]
type = U
movetype = H
physics = N
ctrl = 0

[State 762, Solo]
type = VelSet
trigger1 = statetype != A
x = 0
y = 0

[State 762, Pose]
type = ChangeAnim
trigger1 = Time = 0
value = ifelse(statetype = A, 5030, ifelse(statetype = C, 5020, 5000))

[State 762, Gravidade]
type = VelAdd
trigger1 = statetype = A
y = .44

[State 762, Pouso]
type = PosSet
trigger1 = statetype = A && Pos Y >= 0 && Vel Y >= 0
y = 0

[State 762, Aterrissa]
type = StateTypeSet
trigger1 = statetype = A && Pos Y >= 0 && Vel Y >= 0
statetype = S

[State 762, Abertura no ar]
type = SelfState
trigger1 = Time >= 14 && statetype = A
value = 50
ctrl = 1

[State 762, Abertura no chão]
type = SelfState
trigger1 = Time >= 14
value = 0
ctrl = 1

""")
    if not hazaki:
        c.append("""[Statedef 763]
type = A
movetype = H
physics = N
ctrl = 0
velset = 2,-3

[State 763, Pose]
type = ChangeAnim
trigger1 = Time = 0
value = 5050

[State 763, Gravidade]
type = VelAdd
trigger1 = 1
y = .44

[State 763, Quica uma vez]
type = VelSet
trigger1 = Time < 22 && Pos Y >= 0 && Vel Y > 0
y = -4.8

[State 763, Fim]
type = SelfState
trigger1 = Time >= 22 && Pos Y >= 0 && Vel Y > 0
value = 5100

""")
    return "".join(c)


def reversao(numero, sucesso, atributos, gatilho):
    return (f"[State {numero}, Desvia]\ntype = ReversalDef\ntrigger1 = {gatilho}\n"
            f"reversal.attr = {atributos}\npausetime = 0,0\nsparkno = S9204\n"
            f"p1stateno = {sucesso}\np2stateno = 762\n\n")


def montar_cns(hazaki=False):
    c = [CNS_TOPO, CNS_INTRO, CNS_PULOS]

    # golpes em pé, de perto e de longe
    c.append(normal(200, "S, NA", 40, "Time = 4", leve=True, hit=14, vel="-4"))
    c.append(normal(210, "S, NA", 85, "Time = 7", tipo="Medium", hit=20, escorrega=7, vel="-6", pausa=(10, 10), pesado=True))
    c.append(normal(215, "S, NA", 80, "Time = 4", tipo="Medium", hit=20, escorrega=7, vel="-5", pausa=(10, 10), pesado=True))
    c.append(normal(230, "S, NA", 45, "Time = 5", leve=True, hit=14, vel="-4"))
    c.append(normal(240, "S, NA", 95, "Time = 9", tipo="Heavy", hit=21, escorrega=8, vel="-7", pausa=(11, 11), pesado=True))
    c.append(normal(245, "S, NA", 85, "Time = 5", tipo="Medium", hit=20, escorrega=7, vel="-5", pausa=(10, 10), pesado=True))
    # golpe de afastar
    c.append(normal(260, "S, HA", 90, "Time = 12", tipo="Back", queda=True, vel="-7,-5", ar="-5,-5", pausa=(12, 12), pesado=True))
    # agachado
    c.append(normal(400, "C, NA", 35, "Time = 4", fis="C", tipo_st="C", leve=True, hit=13, vel="-4", chao="Low"))
    c.append(normal(410, "C, NA", 90, "Time = 6", fis="C", tipo_st="C", tipo="Up", hit=20, vel="-3", ar="-2,-7", pausa=(10, 10), pesado=True))
    c.append(normal(430, "C, NA", 35, "Time = 5", fis="C", tipo_st="C", leve=True, guarda="L", hit=14, vel="-4", chao="Low"))
    c.append(normal(440, "C, NA", 80, "Time = 10", fis="C", tipo_st="C", guarda="L", tipo="Back", queda=True, recupera=False, chao="Trip", vel="-3,-2", ar="-3,-2", pausa=(10, 10), pesado=True))
    # no ar: overhead
    c.append(normal(600, "A, NA", 60, "Time = 5", fis="A", tipo_st="A", guarda="HA", hit=16))
    c.append(normal(610, "A, NA", 75, "Time = 6", fis="A", tipo_st="A", guarda="HA", tipo="Medium", hit=18, pesado=True))
    c.append(normal(650, "A, HA", 80, "Time = 7", fis="A", tipo_st="A", guarda="HA", tipo="Back", queda=True, vel="-5,-4", ar="-4,-4", pesado=True))

    # rolamento: invencível do quadro 1 ao 20, depois pode ser agarrado
    for n, v, anim in ((700, 6, 700), (705, -6, 705)):
        c.append(estado(n, "S", "I", "N", anim=anim, velset=f"{v},0"))
        c.append(f"[State {n}, Invencivel]\ntype = NotHitBy\ntrigger1 = Time < ifelse(var(8), 24, 20)\n"
                 "value = SCA, NA, SA, HA, NP, SP, HP\ntime = 1\n\n")
        c.append(f"[State {n}, Atravessa]\ntype = PlayerPush\ntrigger1 = Time < 20\nvalue = 0\n\n")
        c.append(f"[State {n}, Para]\ntype = VelSet\ntrigger1 = Time = 20\nx = 0\n\n")
        c.append(f"[State {n}, Vira]\ntype = Turn\ntrigger1 = AnimTime = 0\ntrigger1 = p2dist x < 0\n\n")
        c.append(f"[State {n}, Limpa]\ntype = VarSet\ntrigger1 = AnimTime = 0\nvar(8) = 0\n\n")
        c.append(fim(n))

    # guard cancel com golpe de afastar: invencível e sem dano
    c.append(estado(720, "S", "A", "S", anim=260, juggle=0))
    c.append("[State 720, Invencivel]\ntype = NotHitBy\ntrigger1 = Time < 12\nvalue = SCA\ntime = 1\n\n")
    c.append(hitdef(720, "Time = 12", "S, HA", 0, tipo="Back", queda=True, vel="-7,-5", ar="-5,-5", pausa=(12, 12)))
    c.append(fim(720))

    # provocação: tira 25 de barra (250 no motor) do oponente quando termina inteira
    c.append(estado(195, "S", "I", "S", anim=195))
    c.append("[State 195, Sorteio]\ntype = VarSet\ntrigger1 = Time = 0\nvar(36) = Random < 200\n\n")
    c.append(fala(195, "provoca", "Time = 2"))
    c.append("[State 195, Limpa fala]\ntype = RemoveExplod\ntrigger1 = AnimTime = 0\nid = 700\n\n")
    c.append(fala(195, "provoca_fim", "AnimTime = 0 & var(36) = 0"))
    c.append(fala(195, "provoca_cai", "AnimTime = 0 & var(36) = 1"))
    c.append("[State 195, Tira barra]\ntype = PowerAdd\ntrigger1 = AnimTime = 0\nvalue = -250\nredirectid = enemynear,id\n\n")
    c.append(fim(195))

    # agarrão
    c.append(estado(800, "S", "A", "S", anim=800, juggle=0))
    c.append("[State 800, Agarra]\ntype = HitDef\ntrigger1 = Time = 0\nattr = S, NT\nhitflag = M-\n"
             "priority = 1, Miss\nsparkno = -1\np1sprpriority = 1\np1facing = 1\np2facing = 1\n"
             "p1stateno = 810\np2stateno = 820\nguard.dist = 0\nfall = 1\n\n")
    c.append(fim(800))
    c.append("[Statedef 810]\ntype = S\nmovetype = A\nphysics = N\nanim = 810\nvelset = 0,0\nctrl = 0\n\n")
    c.append('[State 810, Lado]\ntype = VarSet\ntrigger1 = Time = 0\nvar(2) = command = "holdback"\n\n')
    c.append("[State 810, Segura]\ntype = TargetBind\ntrigger1 = Time < 14\npos = 34, 0\n\n")
    # escape: quem foi agarrado saiu do estado 820 dentro da janela
    c.append("[State 810, Escapou]\ntype = ChangeState\ntrigger1 = Time > 1\ntrigger1 = Time < 14\n"
             "trigger1 = enemynear,stateno != 820\nvalue = 0\nctrl = 1\n\n")
    c.append("[State 810, Vira]\ntype = Turn\ntrigger1 = Time = 14\ntrigger1 = var(2)\n\n")
    c.append("[State 810, Dano]\ntype = TargetLifeAdd\ntrigger1 = Time = 14\nvalue = -100\n\n")
    c.append("[State 810, Solta]\ntype = TargetState\ntrigger1 = Time = 14\nvalue = 821\n\n")
    c.append(fim(810))
    c.append("[Statedef 820]\ntype = A\nmovetype = H\nphysics = N\nvelset = 0,0\n\n")
    c.append("[State 820, Pose]\ntype = ChangeAnim2\ntrigger1 = Time = 0\nvalue = 5030\n\n")
    c.append('[State 820, Escape]\ntype = SelfState\ntriggerall = Time <= 7\ntrigger1 = command = "y"\n'
             'trigger2 = command = "b"\nvalue = 0\nctrl = 1\n\n')
    c.append("[State 820, Solto]\ntype = SelfState\ntrigger1 = !gethitvar(isbound)\nvalue = 5050\n\n")
    c.append("[Statedef 821]\ntype = A\nmovetype = H\nphysics = N\nvelset = 3.2,-6\nctrl = 0\n\n")
    c.append("[State 821, Queda]\ntype = VelAdd\ntrigger1 = 1\ny = .44\n\n")
    c.append("[State 821, Chao]\ntype = SelfState\ntrigger1 = Vel Y > 0\ntrigger1 = Pos Y >= 0\nvalue = 5100\n\n")

    # Bola de Sombra: fraca lenta, forte rápida, no Despertar sai dobrada
    for n, vel in ((1000, 3.2), (1001, 5.4)):
        c.append(estado(n, "S", "A", "S", anim=n, juggle=4))
        c.append(fala(n, "bola_trava", "Time = 0 & var(20) = 0"))
        c.append(fala(n, "bola_liso", "Time = 0 & var(20) > 0"))
        c.append(projetil(n, "AnimElem = 2", 1005, 1006, vel, 70, "S, SP", ofs="70, -12"))
        c.append(f"[State {n}, Dobrada]\ntype = Projectile\ntrigger1 = AnimElem = 3\ntrigger1 = var(20) > 0\n"
                 f"projid = 1001\nprojanim = 1005\nprojhitanim = 1006\nprojremanim = 1006\noffset = 70, -12\n"
                 f"velocity = {vel + 1.2}, 0\nattr = S, SP\ndamage = 50, 4\nanimtype = Med\nguardflag = MA\n"
                 "hitflag = MAF\npausetime = 2, 10\nhitsound = F5,1\nguardsound = F6,0\nground.type = High\n"
                 "ground.slidetime = 12\nground.hittime = 18\nground.velocity = -4\nair.velocity = -2,-3.5\n\n")
        c.append(fim(n))

    # Meia-lua de Compasso Sombria: avança girando e derruba
    c.append(estado(1100, "S", "A", "S", anim=1100, juggle=4))
    c.append(nome_travado(1100, "compasso"))
    c.append("[State 1100, Avança]\ntype = VelSet\ntrigger1 = AnimElem = 2\nx = 4\n\n")
    c.append("[State 1100, Para]\ntype = VelSet\ntrigger1 = AnimElem = 6\nx = 0\n\n")
    c.append(hitdef(1100, "AnimElem = 2", "S, SA", 110, tipo="Heavy", queda=True, vel="-5,-4", ar="-4,-4", pausa=(10, 10), pesado=True))
    c.append(fim(1100))

    # Armada do Quilombo: anti-aéreo, invencível nos 5 primeiros quadros
    c.append(estado(1200, "S", "A", "S", anim=1200, juggle=4))
    c.append(nome_travado(1200, "armada", "Vel Y > 0 & Pos Y >= 0"))
    c.append("[State 1200, Invencivel]\ntype = NotHitBy\ntrigger1 = Time < 5\nvalue = SCA\ntime = 1\n\n")
    c.append("[State 1200, Sobe]\ntype = VelSet\ntrigger1 = Time = 4\nx = 2\ny = -7.5\n\n")
    c.append("[State 1200, Ar]\ntype = StateTypeSet\ntrigger1 = Time = 4\nstatetype = A\nphysics = A\n\n")
    c.append(hitdef(1200, "Time = 4", "S, SA", 120, tipo="Up", queda=True, vel="-2,-7", ar="-2,-7", pausa=(11, 11), pesado=True))
    c.append("[State 1200, Pouso]\ntype = ChangeState\ntrigger1 = Vel Y > 0\ntrigger1 = Pos Y >= 0\nvalue = 52\n\n")

    # Caneta: desliza por baixo do projétil e troca de lado no acerto
    c.append(estado(1300, "C", "A", "S", anim=1300, juggle=4))
    c.append(nome_travado(1300, "caneta"))
    c.append("[State 1300, Por baixo]\ntype = NotHitBy\ntrigger1 = Time < 18\nvalue = , NP, SP, HP\ntime = 1\n\n")
    c.append("[State 1300, Desliza]\ntype = VelSet\ntrigger1 = AnimElem = 2\nx = 7\n\n")
    c.append("[State 1300, Para]\ntype = VelSet\ntrigger1 = AnimElem = 3\nx = 0\n\n")
    c.append("[State 1300, Passa]\ntype = PlayerPush\ntrigger1 = MoveHit\nvalue = 0\n\n")
    c.append("[State 1300, Troca]\ntype = PosAdd\ntrigger1 = MoveHit = 1\nx = 60\n\n")
    c.append(hitdef(1300, "AnimElem = 2", "C, SA", 70, tipo="Back", guarda="L", queda=True, chao="Trip", vel="-2,-2", ar="-2,-2", pausa=(8, 8)))
    c.append(fim(1300, 11))

    # Despertar: bebe a lata, 600 quadros turbinado
    c.append(estado(2000, "S", "I", "S", anim=2000))
    c.append(superpausa(2000, "Time = 0"))
    c.append("[State 2000, Gasta]\ntype = PowerAdd\ntrigger1 = Time = 0\nvalue = -1000\n\n")
    c.append("[State 2000, Invencivel]\ntype = NotHitBy\ntrigger1 = 1\nvalue = SCA\ntime = 1\n\n")
    c.append(fala(2000, "lata", "Time = 2"))
    c.append("[State 2000, Liga]\ntype = VarSet\ntrigger1 = AnimTime = 0\nvar(20) = 600\n\n")
    c.append(fim(2000))

    # Golaço da Noite (1 estoque)
    c.append(estado(3000, "S", "A", "S", anim=3000, juggle=0))
    c.append(superpausa(3000, "Time = 0"))
    c.append("[State 3000, Gasta]\ntype = PowerAdd\ntrigger1 = Time = 0\nvalue = -1000\n\n")
    c.append("[State 3000, Invencivel]\ntype = NotHitBy\ntrigger1 = AnimElemTime(5) < 0\nvalue = SCA\ntime = 1\n\n")
    c.append(fala(3000, "golaco", "Time = 2"))
    c.append(projetil(3000, "AnimElem = 5", 3005, 3006, 7, 60, "S, HP", hits=5, intervalo=5, id_=3000, ofs="90, -46", queda=True))
    c.append(fim(3000))

    # Pelada Sombria (Super Despertado): 8 acertos e acaba o Despertar
    c.append(estado(3100, "S", "A", "S", anim=3100, juggle=0))
    c.append(superpausa(3100, "Time = 0"))
    c.append("[State 3100, Gasta]\ntype = PowerAdd\ntrigger1 = Time = 0\nvalue = ifelse(var(20) > 0, -1000, -2000)\n\n")
    c.append("[State 3100, Fim Despertar]\ntype = VarSet\ntrigger1 = Time = 0\nvar(20) = 0\n\n")
    c.append("[State 3100, Invencivel]\ntype = NotHitBy\ntrigger1 = Time < 4\nvalue = SCA\ntime = 1\n\n")
    c.append(fala(3100, "pelada", "Time = 2"))
    c.append("[State 3100, Avança]\ntype = VelSet\ntrigger1 = Time = 4\nx = 2\n\n")
    c.append(hitdef(3100, "(Time >= 4) && (Time <= 32) && (Time % 4 = 0)", "S, HA", 47, tipo="Medium", hit=16, escorrega=4, vel="-1", ar="-1,-3", pausa=(2, 6), pesado=True))
    c.append(hitdef(3100, "Time = 36", "S, HA", 60, tipo="Back", queda=True, recupera=False, vel="-7,-6", ar="-7,-6", pausa=(14, 14), pesado=True))
    c.append("[State 3100, Trava]\ntype = VelSet\ntrigger1 = Time = 36\nx = 0\n\n")
    c.append(fim(3100))

    if hazaki:
        inicio = next(i for i, trecho in enumerate(c) if trecho.startswith("[Statedef 1000]"))
        fim_especiais = next(i for i, trecho in enumerate(c) if trecho.startswith("[Statedef 2000]"))
        del c[inicio:fim_especiais]
        inicio = next(i for i, trecho in enumerate(c) if trecho.startswith("[Statedef 3000]"))
        del c[inicio:]
    else:
        for n, dano, novo in ((1100, 110, 132), (1200, 120, 144), (1300, 70, 92)):
            inicio = next(i for i, trecho in enumerate(c) if trecho.startswith(f"[Statedef {n}]"))
            fim_estado = next(i for i in range(inicio+1, len(c)) if c[i].startswith("[Statedef"))
            variante = "".join(c[inicio:fim_estado]).replace(str(n), str(n+1))
            c.append(variante.replace(f"damage = {dano},", f"damage = {novo},"))
    c.append(cns_repertorio(hazaki))
    # roda sempre, mesmo sem controle
    c.append("""[Statedef -2]

[State -2, Zera fracos]
type = VarSet
trigger1 = ctrl
var(5) = 0

[State -2, Zera quique]
type = VarSet
trigger1 = NumEnemy > 0 && p2movetype != H
var(24) = 0

[State -2, Passo para trás invencível]
type = NotHitBy
trigger1 = stateno = 105
trigger1 = Time < 6
value = SCA
time = 1

[State -2, Conta Despertar]
type = VarAdd
trigger1 = var(20) > 0
var(20) = -1

[State -2, Ressaca começa]
type = VarSet
trigger1 = var(20) = 1
var(21) = 60

[State -2, Ressaca conta]
type = VarAdd
trigger1 = var(21) > 0
var(21) = -1

[State -2, Bônus de dano]
type = AttackMulSet
trigger1 = 1
value = ifelse(var(20) > 0, 1.45, 1)

[State -2, Ginga de Juliet]
type = ChangeAnim
trigger1 = stateno = 0
trigger1 = var(20) > 0
trigger1 = anim != 9203
value = 9203

[State -2, Tira os oculos]
type = ChangeAnim
trigger1 = stateno = 0
trigger1 = var(20) <= 0
trigger1 = anim = 9203
value = 0

[State -2, Aura]
type = PalFX
trigger1 = var(20) > 0
time = 2
add = 40, 0, 70
sinadd = 30, 0, 40, 40

[State -2, Rastro]
type = AfterImageTime
trigger1 = var(20) > 0
time = 2

""")
    c.append(fala(-2, "ressaca", "var(21) = 59"))
    c.append("[State -2, Ressaca anda devagar]\ntype = PosAdd\ntrigger1 = stateno = 20\ntrigger1 = var(21) > 0\n"
             "x = -vel x * .2\n\n")
    c.append(fala(-2, "bola_ok", "ProjHitTime(1000) = 0 & var(20) = 0"))
    c.append(fala(-2, "round", "roundstate = 2 & roundno > 1 & var(31) = 0"))
    c.append("[State -2, Round falado]\ntype = VarSet\ntrigger1 = roundstate = 2\nvar(31) = 1\n\n")
    c.append(fala(-2, "primeiro", "movetype = H & roundstate = 2 & alive & var(30) = 0"))
    c.append("[State -2, Primeiro golpe falado]\ntype = VarSet\ntrigger1 = movetype = H\ntrigger1 = roundstate = 2\nvar(30) = 1\n\n")
    c.append(fala(-2, "derrota", "!alive & var(32) = 0"))
    c.append("[State -2, Conta derrota]\ntype = VarAdd\ntrigger1 = !alive\nvar(32) = 1\n\n")
    c.append(fala(-2, "locutor_ko", "var(32) = 75"))
    resultado = "".join(c)
    if hazaki:
        resultado = resultado.replace(f"anim = {ID_BALAO['lata']}", f"anim = {ID_BALAO['golaco']}")
        resultado = resultado.replace("add = 40, 0, 70", "add = 42, 16, 0").replace("sinadd = 30, 0, 40, 40", "sinadd = 24, 8, 0, 40")
    return resultado


# ------------------------------------------------------------------ CMD

def comando(nome, cmd, tempo=None, buffer=None):
    t = f'[Command]\nname = "{nome}"\ncommand = {cmd}\n'
    if tempo:
        t += f"time = {tempo}\n"
    if buffer:
        t += f"buffer.time = {buffer}\n"
    return t + "\n"


def entrada(nome, valor, condicoes, gatilhos=("var(1)",)):
    t = [f"[State -1, {nome}]", "type = ChangeState", f"value = {valor}"]
    t += [f"triggerall = {c}" for c in condicoes]
    t += [f"trigger{i + 1} = {g}" for i, g in enumerate(gatilhos)]
    return "\n".join(t) + "\n\n"


def montar_cmd(hazaki=False):
    c = ["; Gerado por ferramentas/gerar_pengaro.py. Edite lá, não aqui.\n",
         "; x = soco fraco, y = soco forte, a = chute fraco, b = chute forte, c = provocação\n\n",
         "[Remap]\nx = x\ny = y\nz = z\na = a\nb = b\nc = c\ns = s\n\n",
         "[Defaults]\ncommand.time = 15\ncommand.buffer.time = 3\n\n"]
    for b in ("" if hazaki else "ab"):
        c.append(comando("golaco", f"~B, F, D, {b}", 24))
        c.append(comando("bola_fraca" if b == "a" else "bola_forte", f"~D, F, {b}", 18))
        c.append(comando(f"compasso_{b}", f"~D, B, {b}", 18))
    for b in ("" if hazaki else "xy"):
        c.append(comando(f"armada_{b}", f"~F, D, {b}", 18))
        c.append(comando(f"caneta_{b}", f"~D, B, {b}", 18))
    lista_golpes = list(golpes(hazaki))
    for g in lista_golpes:
        if g.estado not in (601, 611):
            c.append(comando(f"golpe_{g.estado}", g.comando, 24 if g.custo else 18))
        if g.custo:
            c.append(comando(f"golpe_{g.estado}", g.comando[:-1] + ("b" if g.estado == 3000 else "y"), 24))
    c.append(comando("parry", "/F, c", 1, 1))
    c.append(comando("FF", "F, F", 10))
    c.append(comando("BB", "B, B", 10))
    c.append(comando("recovery", "x+a", 1))
    c.append(comando("rolar", "x+a", 3))
    c.append(comando("afastar", "y+b", 3))
    c.append(comando("despertar", "x+a+y", 3))
    c.append(comando("superpulo", "$D, $U", 10, 6))
    for nome in "xyabc":
        c.append(comando(nome, nome, 1))
    c.append(comando("start", "s", 1))
    for nome, d in (("holdfwd", "/$F"), ("holdback", "/$B"), ("holdup", "/$U"), ("holddown", "/$D")):
        c.append(comando(nome, d, 1))

    c.append("[Statedef -1]\n\n")
    cancela = "stateno = 200 || stateno = 210 || stateno = 215 || stateno = 216 || stateno = 230 || stateno = 245 || stateno = 400 || stateno = 410 || stateno = 430 || stateno = 260"
    c.append("[State -1, Pode cancelar]\ntype = VarSet\ntrigger1 = 1\n"
             f"var(1) = ctrl || (({cancela}) && movecontact && movecontact <= 8)\n\n")

    no_chao = ["statetype != A"]
    especial_em_super = "(stateno = [1000,1501]) && movehit && movehit <= 8"
    for g in sorted(lista_golpes, key=lambda g: -g.custo):
        if g.estado >= 1000:
            condicoes = [f'command = "golpe_{g.estado}"'] + no_chao
            if g.custo:
                condicoes.append(f"power >= {g.custo}")
            c.append(entrada(g.nome, g.estado, condicoes, ("var(1)", especial_em_super) if g.custo else ("var(1)",)))
    forte = "(var(20) > 0) || (life <= 200 && power >= 2000)"
    if not hazaki:
        c.append(entrada("Pelada Sombria", 3100, ['command = "golaco"', "power >= 1000", f"({forte})"] + no_chao, ("var(1)", especial_em_super)))
        c.append(entrada("Golaco da Noite", 3000, ['command = "golaco"', "power >= 1000"] + no_chao, ("var(1)", especial_em_super)))
    c.append(entrada("Despertar", 2000, ['command = "despertar"', "power >= 1000", "var(20) = 0", "statetype = S"], ("ctrl",)))
    if not hazaki:
        for nome, n, botoes in (("armada", 1200, "xy"), ("caneta", 1300, "xy"), ("compasso", 1100, "ab")):
            for i, b in enumerate(botoes):
                c.append(entrada(nome, n+i, [f'command = "{nome}_{b}"'] + no_chao))
        bola = ["numprojid(1000) = 0"] + no_chao
        c.append(entrada("Bola forte", 1001, ['command = "bola_forte"'] + bola))
        c.append(entrada("Bola fraca", 1000, ['command = "bola_fraca"'] + bola))
    c.append(entrada("Parry", 760, ['command = "parry"', "statetype = S"], ("ctrl",)))
    defendendo = "stateno = 150 || stateno = 152"
    # guard cancel: 1 estoque, depois do 3º quadro de defesa
    c.append("[State -1, Rolamento de defesa]\ntype = VarSet\ntriggerall = command = \"rolar\"\n"
             f"triggerall = power >= 1000\ntriggerall = time > 3\ntrigger1 = {defendendo}\nvar(8) = 1\n\n")
    c.append("[State -1, Gasta rolamento de defesa]\ntype = PowerAdd\ntriggerall = var(8) = 1\ntriggerall = command = \"rolar\"\n"
             f"trigger1 = {defendendo}\nvalue = -1000\n\n")
    c.append(entrada("Rolamento de defesa frente", 700, ['var(8) = 1', 'command = "rolar"', 'command != "holdback"'], (defendendo,)))
    c.append(entrada("Rolamento de defesa tras", 705, ['var(8) = 1', 'command = "rolar"'], (defendendo,)))
    c.append("[State -1, Gasta afastar de defesa]\ntype = PowerAdd\ntriggerall = command = \"afastar\"\n"
             f"triggerall = power >= 1000\ntriggerall = time > 3\ntrigger1 = {defendendo}\nvalue = -1000\n\n")
    c.append(entrada("Afastar de defesa", 720, ['command = "afastar"', "time > 3"], (defendendo,)))
    # rolamento e golpe de afastar
    c.append(entrada("Rolar para tras", 705, ['command = "rolar"', 'command = "holdback"', "statetype = S"], ("ctrl",)))
    c.append(entrada("Rolar", 700, ['command = "rolar"', "statetype = S"], ("ctrl",)))
    c.append(entrada("Afastar no ar", 650, ['command = "afastar"', "statetype = A"], ("ctrl",)))
    c.append(entrada("Afastar", 260, ['command = "afastar"', "statetype = S"], ("var(1)",)))
    # agarrão: colado, em pé, oponente fora de stun
    pega = ['command = "y"', "statetype = S", "ctrl", "stateno != 100", "p2bodydist x < 8", "p2statetype != A", "p2movetype != H"]
    pega_k = ['command = "b"'] + pega[1:]
    for lista in (pega, pega_k):
        c.append(entrada("Agarrao", 800, lista + ['(command = "holdfwd" || command = "holdback")'], ("1",)))
    for g in lista_golpes:
        if g.estado < 300:
            gatilhos = ("ctrl", "(stateno = 200 || stateno = 230) && movehit && movehit <= 8") if g.estado == 216 else ("ctrl",)
            c.append(entrada(g.nome, g.estado, [f'command = "golpe_{g.estado}"', "statetype = S"], gatilhos))
    # corrida e passo para trás
    c.append(entrada("Corre", 100, ['command = "FF"', "statetype = S"], ("ctrl",)))
    c.append(entrada("Recua", 105, ['command = "BB"', "statetype = S"], ("ctrl",)))
    c.append(entrada("Provocacao", 195, ['command = "c"', "statetype != A"], ("ctrl",)))

    # corrente de fracos: até 4 em sequência, no contato
    corrente_soco = "(stateno = 200 || stateno = 400 || stateno = 430 || stateno = 230) && movecontact && var(5) < 4"
    corrente_chute = "stateno = 430 && movecontact && var(5) < 4"
    c.append(entrada("Agachado soco fraco", 400, ['command = "x"', 'command = "holddown"', "statetype != A"], ("ctrl", corrente_soco)))
    c.append(entrada("Agachado chute fraco", 430, ['command = "a"', 'command = "holddown"', "statetype != A"], ("ctrl", corrente_chute)))
    c.append(entrada("Agachado soco forte", 410, ['command = "y"', 'command = "holddown"', "statetype != A"], ("ctrl",)))
    c.append(entrada("Agachado chute forte", 440, ['command = "b"', 'command = "holddown"', "statetype != A"], ("ctrl",)))
    # em pé: de perto ou de longe
    c.append(entrada("Soco fraco", 200, ['command = "x"', 'command != "holddown"', "statetype = S"], ("ctrl", corrente_soco)))
    c.append(entrada("Chute fraco", 230, ['command = "a"', 'command != "holddown"', "statetype = S"], ("ctrl",)))
    perto = "p2bodydist x < 30"
    c.append(entrada("Soco forte perto", 215, ['command = "y"', "statetype = S", perto], ("ctrl",)))
    c.append(entrada("Soco forte longe", 210, ['command = "y"', "statetype = S"], ("ctrl",)))
    c.append(entrada("Chute forte perto", 245, ['command = "b"', "statetype = S", perto], ("ctrl",)))
    c.append(entrada("Chute forte longe", 240, ['command = "b"', "statetype = S"], ("ctrl",)))
    # no ar
    for botao, n in zip("xyab", (600, 601, 610, 611)):
        gatilhos = ("ctrl", "(stateno = 600 || stateno = 610) && movehit && movehit <= 8") if n in (601, 611) else ("ctrl",)
        c.append(entrada("Golpe no ar", n, [f'command = "{botao}"', "statetype = A"], gatilhos))
    return "".join(c)


DEF = """; Gerado por ferramentas/gerar_pengaro.py. Edite lá, não aqui.
[Info]
name = "Pengaro"
displayname = "Pengaró"
versiondate = 11,05,2026
mugenversion = 1.1
author = "Breno"
pal.defaults = 1
localcoord = 320,240

[Files]
cmd = pengaro.cmd
cns = pengaro.cns
st = pengaro.cns
stcommon = common1.cns
sprite = pengaro.sff
anim = pengaro.air
movelist = movelist.dat

[Palette Keymap]
x = 1
"""


GOLPES = """<#f0f000>:Especiais:</>
Bola de Sombra						_D_F^K
Meia-lua de Compasso Sombria		_D_B^K
Armada do Quilombo					_F_D^P
Caneta								_D_B^P
Mão de Chimpá / Mão Pesada          _D_F^P
Sola de Várzea / Pisão de Bar       _B_D^K

<#f0f000>:Supers:</>
Golaço da Noite <#bebebe>(1000)</>	_B_F_D^K
Pelada Sombria (no Despertar)		_B_F_D^K
Bando da Várzea / Apagão da Várzea  _B_F_D^P

<#f0f000>:Sistema:</>
Despertar: Lata Gelada <#bebebe>(1000)</>	^X_+^A_+^Y
Rolamento							^X_+^A
Golpe de afastar					^Y_+^B
Agarrão								[_B/_F]_+^Y
Provocação							^C
Parry                              _F^C
"""


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    s = montar_sprites(retrato=RAIZ / "sprites/pengaro-selecao-kof.png")
    faiscas = carregar_faiscas(s)
    a = montar_air(s, faiscas)
    escrever_sff(SAIDA / "pengaro.sff", s)
    (SAIDA / "pengaro.air").write_text("\n".join(a.txt), encoding="utf-8", newline="\n")
    cns = montar_cns()
    cns = cns.replace("[Data]", "[Quotes]\n" + "".join(f'victory{i + 1} = "{v}"\n' for i, v in enumerate(VITORIAS)) + "\n[Data]", 1)
    (SAIDA / "pengaro.cns").write_text(cns, encoding="utf-8", newline="\n")
    (SAIDA / "pengaro.cmd").write_text(montar_cmd(), encoding="utf-8")
    (SAIDA / "pengaro.def").write_text(DEF, encoding="utf-8", newline="\n")
    (SAIDA / "movelist.dat").write_text(GOLPES, encoding="utf-8", newline="\n")
    print(f"{len(s.lista)} sprites, {len(a.acoes)} ações em {SAIDA}")


if __name__ == "__main__":
    main()
