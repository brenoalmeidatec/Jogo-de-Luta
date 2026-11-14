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
import agarrao_mk
import json
import math
import random
import re
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from repertorio import golpes, quadros as quadros_golpe
import pengaro_extra as extra

import itens_pengaro
import aura_pengaro

RAIZ = Path(__file__).resolve().parent.parent
FOLHA = RAIZ / "sprites/pengaro/pixel/pengaro.png"
INFO = RAIZ / "sprites/pengaro/pixel/pengaro.json"
SAIDA = RAIZ / "chars/pengaro"
EFEITOS = RAIZ / "assets/efeitos"
ATAQUES_DESPERTADOS = {200, 210, 215, 230, 240, 245, 260, 400, 410, 430, 440, 600, 610, 650,
                      760, 761, 830, 831, 1000, 1001, 1100, 1101, 1200, 1201, 1300, 1301}
ATAQUES_DESPERTADOS.update(g.estado for h in (False, True) for g in golpes(h))

# Agarrão de comando (← → + y): agarra, dá o martelo de capoeira e joga o whisky em cima do inimigo.
# Quadros (folha, desenho, ticks antes do RITMO). O .cns usa os mesmos tempos, por isso ficam aqui juntos.
AGARRAO_WHISKY = [("agarrao", 2, 3), ("agarrao", 3, 3),
                  ("compasso", 1, 4), ("compasso", 2, 4), ("compasso", 3, 4), ("compasso", 4, 2), ("compasso", 5, 3),
                  ("compasso", 6, 4), ("compasso", 7, 4),
                  ("bola", 2, 5), ("bola", 4, 4), ("bola", 5, 4), ("bola", 6, 4), ("bola", 7, 4)]


def tempos_agarrao_whisky():
    """Ticks (já com o RITMO) em que a capoeira acerta e em que a garrafa sai da mão."""
    t, inicio = 0, []
    for _, _, n in AGARRAO_WHISKY:
        inicio.append(t)
        t += round(n * RITMO)
    return inicio[5], inicio[10]  # 5 = compasso 4 (chute no contato); 10 = bola 4 (solta a garrafa)
FAISCAS = {9200: "hit-spark", 9201: "crit-hit", 9202: "hit-flash",  # 9204 ("parry") saiu: parecia rede de futebol
           9205: "ground-slam", 9206: "fireball"}

# Tela de trabalho de cada sprite: pés em (EIXO_X, EIXO_Y).
LARG, ALT = 360, 260
EIXO_X, EIXO_Y = 180, 220
LIMITE_AMOSTRA_PALETA = 4_000_000  # pixels usados para escolher as 255 cores

# Balões, em unidades do lutador (a tela da luta em 16:9 é 320 x 180).
BALOES_LIGADOS = False  # o Breno vai gravar as falas em áudio; os textos de BALOES ficam como roteiro
BALAO_ACIMA_DOS_PES = 125  # ponta do balão, logo acima da cabeça
RITMO = 1.5  # os golpes mostram o movimento inteiro; no tempo antigo pareciam acelerados
# O preparo (os elementos antes daquele em que a caixa de golpe liga) não é esticado: com RITMO ele fazia o golpe forte
# levar 10 a 26 ticks até encostar (a regra 8.3 pede 7 a 10) e dava a sensação de golpe mole. Só vale no Pengaró; a
# recuperação e o resto seguem com RITMO, e é o preparo sem esticar que volta a casar com os `Time = N` do CNS.
RITMO_PREPARO = 1.0
PROJETEIS = {1005, 1006, 3005, 3006, 3010, 3011, 3012}
# Estilo de pose segurada (regra 7, medido quadro a quadro em jogo de luta de arcade: só tempo e técnica). Nos golpes,
# reações, defesa e queda o olho lê poses paradas e a troca entre elas é seca; o movimento contínuo (ginga, andar,
# correr, pulo, entrada, vitória) continua fluido. Rolamento (700/705) é deslocamento e o Despertar (2000) é cena.
FRACOS = {200, 230, 301, 321, 322, 340, 342, 400, 430, 600}  # = os golpes com hitsound F5,0 (main confere)
SECO_FORA = {700, 705, 2000}


def SECO(numero):
    n = numero % 10000
    return (200 <= n < 4000 and n not in PROJETEIS and n not in SECO_FORA or 5000 <= n <= 5017
            or n in (10, 12, 130, 150, 5100, 5120))
BALAO_TOPO_MINIMO = 40    # abaixo do relógio e dos nomes da HUD
BALAO_MARGEM = 4          # folga até a borda da tela


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
    par = GEMEOS_HD.get(id(img))
    if par is not None and par[0] is img:  # o gêmeo 3x anda junto (GEMEOS_HD, mais abaixo)
        g = Image.new("RGBA", par[1].size)
        g.paste(par[1], (dx * HD_E, dy * HD_E))
        GEMEOS_HD[id(tela)] = (tela, g)
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


def medida_balao(texto):
    """Largura e altura da caixa do balão, sem a ponta."""
    f = fonte(11)
    linhas = texto.split("\n")
    return max(f.getbbox(linha)[2] for linha in linhas) + 14, 15 * len(linhas) + 8


def balao(texto):
    """Balão de fala em imagem própria, centrado acima do eixo."""
    f = fonte(11)
    linhas = texto.split("\n")
    w, h = medida_balao(texto)
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
        if getattr(self, "folhas", False) and nome in TROCA_POR_FOLHA:
            folha, i = TROCA_POR_FOLHA[nome]
            desenho = quadro_folha(folha, i)
            if desenho is not None:
                return self.guardar(nome, desenho, grupo, indice, eixo)  # a garrafa já vem desenhada
        if getattr(self, "folhas", False) and img.size == (LARG, ALT) and not nome.startswith(SEM_WHISKY):
            img = itens_pengaro.com_whisky(img)  # o Pengaró luta com a garrafa de whisky na mão de trás
        return self.guardar(nome, img, grupo, indice, eixo)

    def guardar(self, nome, img, grupo, indice, eixo):
        if grupo is None:
            grupo = self.proximo
            self.proximo += 1
        self.lista.append((grupo, indice, img, eixo[0], eixo[1]))
        self.codigos[nome] = (grupo, indice)
        return nome


def rle8(px):
    """Formato 2 do SFF v2. Bytes 0x40-0x7F são contagem, então valor assim precisa ir como run.
    Em numpy (os sprites HD têm 9x mais pixels): mesmo resultado do laço antigo, run de no máximo 63."""
    a = np.frombuffer(bytes(px), np.uint8)
    if not len(a):
        return b""
    inicio = np.flatnonzero(np.r_[True, a[1:] != a[:-1]])
    comp = np.diff(np.r_[inicio, len(a)])
    pedacos = (comp + 62) // 63                        # cada run vira pedaços de até 63
    v = np.repeat(a[inicio], pedacos)
    tam = np.full(pedacos.sum(), 63)
    fim = np.cumsum(pedacos) - 1
    tam[fim] = comp - (pedacos - 1) * 63               # o último pedaço de cada run fica com o resto
    par = (tam > 1) | ((v & 0xC0) == 0x40)
    out = np.zeros(len(v) * 2, np.uint8)
    pos = np.cumsum(np.where(par, 2, 1)) - np.where(par, 2, 1)
    out[pos[par]] = (0x40 | tam[par]).astype(np.uint8)
    out[pos[par] + 1] = v[par]
    out[pos[~par]] = v[~par]
    return out[:pos[-1] + (2 if par[-1] else 1)].tobytes()


def paleta_global(imagens):
    """Uma paleta para todos os sprites. O índice 0 é o transparente."""
    cores = []
    for im in imagens:
        a = np.asarray(im.convert("RGBA"))
        cores.append(a[a[..., 3] >= 128][:, :3])
    cores = np.concatenate(cores)
    passo = max(1, len(cores) // LIMITE_AMOSTRA_PALETA)  # com milhares de sprites, uma amostra já dá as mesmas cores
    pedaco = Image.fromarray(np.ascontiguousarray(cores[::passo])[None, :, :], "RGB")
    return pedaco.quantize(colors=255, method=Image.MEDIANCUT)


# O ChangeAnim2 desenha a vítima do arremesso com o SFF DELA e os números de sprite das ações 5001 e 5030 do .air do
# arremessador. Por isso todo lutador guarda no .sff a união desses desenhos de todos os lutadores, mesmo sem usá-los.
# verificar_pengaro.py falha se algum .air de chars/ pedir, nessas ações, um sprite fora daqui.
ACOES_VITIMA = (5001, 5030)
SPRITES_VITIMA = frozenset({
    (48, 0), (49, 0), (50, 0), (382, 0), (384, 0), (385, 0), (386, 0), (390, 0), (392, 0), (393, 0), (394, 0),
    (871, 0), (873, 0), (875, 0), (877, 0), (878, 0), (880, 0), (881, 0), (890, 0), (897, 0), (899, 0), (901, 0),
    (903, 0), (904, 0), (906, 0), (907, 0), (909, 0), (910, 0),
})
RE_ELEMENTO = re.compile(r"^\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+", re.M)
RE_REMAP = re.compile(r"^(\d+),\s*(\d+)\s*=\s*(\d+),\s*(\d+)", re.M)


def trocas_do_remap(cns):
    """Pares (origem, destino) do [RemapPreset despertado] do .cns."""
    bloco = re.search(r"^\[RemapPreset despertado\]\n(.*?)(?=^\[)", cns, re.M | re.S)
    if not bloco:
        return []
    return [((int(a), int(b)), (int(c), int(d))) for a, b, c, d in RE_REMAP.findall(bloco.group(1))]


def sprites_mantidos(air, cns):
    """Os (grupo, índice) que o jogo pode desenhar: todo elemento do .air, o grupo 9000 (retratos), SPRITES_VITIMA e o
    destino do RemapPreset despertado de cada um desses. O resto do .sff não aparece em lugar nenhum."""
    usados = {(int(g), int(i)) for g, i in RE_ELEMENTO.findall(air)} | set(SPRITES_VITIMA)
    return usados | {destino for origem, destino in trocas_do_remap(cns) if origem in usados}


def escrever_sff(destino, sprites, manter=None):
    """Com `manter`, só grava os (grupo, índice) do conjunto (todo o resto é pulado, e o grupo 9000 sempre fica).
    A paleta sai antes da poda e da lista inteira: podar antes mudaria o MEDIANCUT e todos os pixels.
    Os (grupo, índice) de `sprites.fora_da_paleta` (a aura animada) não entram na escolha das cores: vão para a cor
    mais perto da paleta do resto, que sai igual com ou sem eles. `sprites.paleta_de` troca, só na escolha das cores, um
    sprite pelo desenho dele em 1x (o despertado do hd.py).

    Paleta fixa: com sprites/<lutador>/paleta_sff.act (768 bytes RGB: o índice 0 é o transparente, depois as 255
    cores do .sff), as cores vêm dele e não da lista. Sem ela, qualquer sprite novo ou trocado (um desenho 3x a mais no
    despertado, um efeito a menos) refazia o MEDIANCUT e mudava a cor de todo pixel da forma base. Para escolher as
    cores de novo (arte nova do lutador), apague o arquivo, gere e regrave-o com `python ferramentas/conferir_sff.py
    paleta chars/<l>/<l>.sff sprites/<l>/paleta_sff.act`."""
    fixa = RAIZ / "sprites" / Path(destino).stem / "paleta_sff.act"
    if fixa.exists():
        pal = list(fixa.read_bytes()[3:256 * 3])
        q = Image.new("P", (1, 1))
        q.putpalette(pal)
    else:
        fora = getattr(sprites, "fora_da_paleta", set())
        de = getattr(sprites, "paleta_de", {})
        q = paleta_global([de.get((s[0], s[1]), s[2]) for s in sprites.lista if (s[0], s[1]) not in fora])
        pal = q.getpalette()[: 255 * 3]
        pal += [0] * (255 * 3 - len(pal))
    dados_pal = bytes((0, 0, 0, 0))
    for i in range(255):
        dados_pal += bytes((pal[i * 3], pal[i * 3 + 1], pal[i * 3 + 2], 255))

    itens = []
    for grupo, indice, img, ex, ey in sprites.lista:
        if manter is not None and grupo != 9000 and (grupo, indice) not in manter:
            continue
        caixa = img.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox() or (0, 0, 1, 1)
        rec = img.crop(caixa)
        ind = rec.convert("RGB").quantize(palette=q, dither=Image.NONE)
        alfa = np.asarray(rec.getchannel("A"))
        px = np.where(alfa < 128, 0, np.asarray(ind).astype(np.uint16) + 1).astype(np.uint8).tobytes()
        itens.append((grupo, indice, rec.width, rec.height, ex - caixa[0], ey - caixa[1], px))
    gravar_sff(destino, dados_pal, itens)


def gravar_sff(destino, dados_pal, itens):
    """Grava o SFF v2.01 de itens (grupo, índice, largura, altura, eixo x, eixo y, pixels já quantizados).

    Sprite com a mesma largura, altura e pixels de um anterior vira link (len = 0, link = número do nó do primeiro):
    o IKEMEN (loadSff, shareCopy) reaproveita a textura e o eixo continua sendo o do próprio nó. O original sempre vem
    antes, que é a única condição do motor. Também é usado por ferramentas/conferir_sff.py religar."""
    ldata = bytearray(dados_pal)
    nos = bytearray()
    vistos = {}
    for k, (grupo, indice, w, h, ax, ay, px) in enumerate(itens):
        chave = (w, h, px)
        if chave in vistos:
            nos += struct.pack("<HHHHhhHBBIIHH", grupo, indice, w, h, ax, ay, vistos[chave], 2, 8, 0, 0, 0, 0)
            continue
        vistos[chave] = k
        corpo = struct.pack("<I", len(px)) + rle8(px)
        nos += struct.pack("<HHHHhhHBBIIHH", grupo, indice, w, h, ax, ay, 0, 2, 8, len(ldata), len(corpo), 0, 0)
        ldata += corpo

    ofs_pal = 512
    ofs_spr = ofs_pal + 32  # duas paletas iguais: a 2 é a do Endiabrado na seleção (cópia da 1)
    ofs_l = ofs_spr + len(nos)
    cab = bytearray(512)
    cab[0:12] = b"ElecbyteSpr\x00"
    cab[12:16] = bytes((0, 1, 0, 2))
    cab[24:28] = bytes((0, 1, 0, 2))
    struct.pack_into("<8I", cab, 36, ofs_spr, len(itens), ofs_pal, 2, ofs_l, len(ldata), ofs_l + len(ldata), 0)
    no_pal = struct.pack("<HHHHII", 1, 1, 256, 0, 0, 1024) + struct.pack("<HHHHII", 1, 2, 256, 0, 0, 1024)
    destino.write_bytes(bytes(cab) + no_pal + bytes(nos) + bytes(ldata))


# ------------------------------------------------------------------ animações

CORPO = [(-24, 0, 24, -104)]
BAIXO = [(-28, 0, 28, -70)]
ROLANDO = [(-28, 0, 28, -70)]  # rolamento, caneta e levantada: não acompanha o BAIXO do Pengaró arcade (veja main)
NO_AR = [(-24, -24, 24, -100)]
DEITADO = [(-60, 0, 60, -24)]


def conferir_seco(numero, antes, depois, mapa):
    """O estilo de pose segurada não mexe em frame data: mesma soma de ticks, mesma caixa em cada tick (e portanto o
    mesmo 1º tick com caixa) e cada AnimElem do .cns começando no mesmo tick de antes."""
    def por_tick(q):
        saida = []
        for e in q:
            saida += [e[2] if len(e) > 2 and e[2] else None] * max(0, e[1])
        return saida
    inicio = lambda q, k: sum(max(1, e[1]) for e in q[:k])
    a, b = por_tick(antes), por_tick(depois)
    if antes[-1][1] < 0:  # pose final sem fim (golpe no ar): o contato segurado só adia o começo dela
        assert b[:len(a)] == a and not any(b[len(a):]), f"ação {numero}: caixa mudou no estilo seco"
    else:
        assert a == b, f"ação {numero}: caixa ou tempo mudou no estilo seco"
    assert (antes[-1][1] < 0) == (depois[-1][1] < 0), numero
    assert all(inicio(antes, k) == inicio(depois, m - 1) for k, m in enumerate(mapa)), f"ação {numero}: AnimElem"


class Air:
    def __init__(self, sprites, arte_despertada=None, hazaki=False):
        self.s = sprites
        self.hazaki = hazaki
        self.txt = ["; Gerado por ferramentas/gerar_pengaro.py. Edite lá, não aqui.\n"]
        self.acoes = set()
        self.mapas = {}
        self.ativos = {}  # ação -> (elemento em que a caixa de golpe liga, a caixa)
        self.arte_despertada = arte_despertada or {}

    def fluido(self, numero, quadros):
        """Preenche cada elemento com os quadros do meio do Blender, sem mudar o tempo total nem a caixa de golpe.
        Guarda em self.mapas onde cada elemento foi parar, porque o .cns usa AnimElem."""
        if SECO(numero):
            if numero >= 10000:  # variante do Despertar: vem pronta da ação normal, com os mesmos elementos
                self.mapas[numero] = list(range(1, len(quadros) + 1))
                return quadros
            novos = self.seco(numero, quadros)
            conferir_seco(numero, quadros, novos, self.mapas[numero])
            return novos
        novos, mapa = [], []
        for i, q in enumerate(quadros):
            mapa.append(len(novos) + 1)
            ticks = q[1]
            ultimo = i + 1 >= len(quadros)
            proximo = quadros[i + 1][0] if not ultimo else SEGUINTE.get(numero) or fim_da_folha(q[0])
            caminho = caminho_fluido(self.s, q[0], proximo) if ticks > 1 else [q[0]]
            sem_caixa = not (len(q) > 2 and q[2])
            if len(caminho) == 1 and ticks > 2 and sem_caixa:
                # desenho parado por mais de 2 ticks (regra 7): vai-e-volta curto com os quadros do meio vizinhos
                parado = vai_e_volta(self.s, q[0], ticks)
                if parado:
                    novos.extend((nome, tk, *q[2:]) for nome, tk in parado)
                    continue
            if ticks > 0 and sem_caixa and len(caminho) > 1 and ticks > 2 * len(caminho):
                # recuperação longa: dividida por igual, cada desenho passaria de 2 ticks. O excesso vira um vai-e-volta
                # no começo e o caminho segue a 2 ticks por quadro, chegando ao próximo desenho no tempo certo.
                inicio = vai_e_volta(self.s, q[0], ticks - 2 * (len(caminho) - 1))
                if inicio:
                    novos.extend((nome, tk, *q[2:]) for nome, tk in inicio)
                    novos.extend((nome, 2, *q[2:]) for nome in caminho[1:])
                    continue
            n = min(len(caminho), ticks) if ticks > 0 else 1
            for j in range(n):
                t = ticks if ticks <= 0 else ticks // n + (1 if j < ticks % n else 0)
                novos.append((caminho[j * len(caminho) // n], t, *q[2:]))
        self.mapas[numero] = mapa
        return novos

    def frente(self, nome, caixa):
        """Até onde o desenho vai para a frente na faixa de altura da caixa de golpe (para escolher a pose de contato)."""
        if not hasattr(self, "_mascaras"):
            self._mascaras = {}
        if nome not in self._mascaras:
            g, i = self.s.codigos[nome]
            img, ex, ey = next((im, x, y) for gg, ii, im, x, y in self.s.lista if (gg, ii) == (g, i))
            self._mascaras[nome] = (np.asarray(img.getchannel("A")) >= 128, ex, ey)
        a, ex, ey = self._mascaras[nome]
        y1, y2 = sorted((caixa[1], caixa[3]))
        faixa = a[max(0, ey + y1):max(0, ey + y2 + 1)]
        xs = np.nonzero(faixa.any(axis=0))[0]
        return int(xs.max()) - ex if len(xs) else -999

    def seco(self, numero, quadros):
        """Pose segurada (regra 7): cada elemento mostra um desenho parado, sem vai-e-volta nem quadros do meio, salvo
        o smear de até 2 ticks no fim da antecipação. O contato é um desenho só e fica h ticks a mais na tela (h = 1 no
        fraco, 2 no forte), tirados do 1º elemento da recuperação: o tempo total, as caixas e os AnimElem do .cns não
        mudam (o AnimElem desse elemento passa a apontar para o elemento novo, que começa no mesmo tick)."""
        fraco = numero in FRACOS
        h = 1 if fraco else 2
        nomes = [q[0] for q in quadros]
        com = [k for k, q in enumerate(quadros) if len(q) > 2 and q[2]]
        k0 = com[0] if com else None
        k1 = com[-1] if com else None
        if com:
            blocos = []
            for k in com:
                if blocos and blocos[-1][-1] == k - 1:
                    blocos[-1].append(k)
                else:
                    blocos.append([k])

            def candidatos(k):  # o que o elemento mostrava no fluido: o desenho e os quadros do meio até o seguinte
                prox = quadros[k + 1][0] if k + 1 < len(quadros) else SEGUINTE.get(numero) or fim_da_folha(quadros[k][0])
                return caminho_fluido(self.s, quadros[k][0], prox)

            def mais_esticado(ks):  # a pose de maior alcance segura o contato: o alcance máximo não encolhe
                caixa = quadros[ks[0]][2]
                caixa = caixa[0] if isinstance(caixa[0], tuple) else caixa
                return max((n for k in ks for n in candidatos(k)), key=lambda n: self.frente(n, caixa))
            for bloco in blocos:
                if len(bloco) <= 2:  # contato de um acerto: um desenho só segura o ativo inteiro
                    melhor = mais_esticado(bloco)
                    for k in bloco:
                        nomes[k] = melhor
                else:  # vários desenhos com caixa (giro, varrida): cada um segura o seu elemento
                    for k in bloco:
                        nomes[k] = mais_esticado([k])
            pre = list(range(k0))
            if fraco and pre:  # fraco: a antecipação é um desenho só, o da tensão
                for k in pre:
                    nomes[k] = nomes[pre[-1]]
            elif len(pre) > 2:  # forte: carga e tensão
                for k in pre[:-1]:
                    nomes[k] = nomes[pre[-2]]
            rec = [k for k in range(k1 + 1, len(quadros))]
            if fraco and len(rec) > 2:  # fraco: a recuperação usa 2 poses
                meio = (len(rec) + 1) // 2
                for k in rec[:meio]:
                    nomes[k] = nomes[rec[0]]
                for k in rec[meio:]:
                    nomes[k] = nomes[rec[-1]]
        extra = None
        if com and k1 + 1 < len(quadros):
            t = quadros[k1 + 1][1]
            if t == -1 or t >= h + 3:
                extra = k1 + 1
        novos, mapa = [], []
        for i, q in enumerate(quadros):
            mapa.append(len(novos) + 1)
            ticks, resto = q[1], list(q[2:])
            if i == extra:  # o contato fica h ticks a mais, sem caixa
                flip = quadros[k1][3:4]
                novos.append((nomes[k1], h, None, *flip))
                ticks = ticks if ticks < 0 else ticks - h
            if com and i == k0 - 1 and ticks >= 2:  # smear: os últimos quadros do meio antes do contato, a 1 tick
                s = 1 if fraco else max(1, min(2, ticks - 2))
                caminho = caminho_fluido(self.s, nomes[i], quadros[k0][0])[1:]
                if caminho:
                    s = min(s, len(caminho))
                    novos.append((nomes[i], ticks - s, *resto))
                    novos.extend((m, 1, *resto) for m in caminho[-s:])
                    continue
            if com and i > k1 and ticks > 9 and nomes[i] == q[0]:
                # recuperação longa num desenho só (golpe de 3 desenhos, especial): vira poses de até ~9 ticks com troca
                # seca. As poses são os desenhos da folha no caminho: do contato até este (só no 1º elemento da
                # recuperação, que antes atravessava esse trecho) e deste até o seguinte (no último, até o fim da folha).
                ultimo = i + 1 >= len(quadros)
                prox = quadros[i + 1][0] if not ultimo else SEGUINTE.get(numero) or fim_da_folha(q[0])
                seq = caminho_fluido(self.s, q[0], prox)
                if ultimo and prox and prox != q[0] and desenho_de(prox):
                    seq.append(prox)
                if i == k1 + 1:
                    seq = caminho_fluido(self.s, quadros[k1][0], q[0])[1:] + seq
                chaves = list(dict.fromkeys(n for n in seq if desenho_de(n) and not n.startswith("m_")))
                if len(chaves) >= 2:
                    poses = chaves[-max(2, -(-ticks // 10)):]
                else:
                    n = min(len(seq), -(-ticks // 9))
                    poses = [seq[round(j * (len(seq) - 1) / (n - 1)) if ultimo else j * len(seq) // n]
                             for j in range(n)] if n > 1 else []
                if len(poses) > 1:
                    n = len(poses)
                    for j, nome in enumerate(poses):
                        novos.append((nome, ticks // n + (1 if j < ticks % n else 0), *resto))
                    continue
            novos.append((nomes[i], ticks, *resto))
        self.mapas[numero] = mapa
        return novos

    def acao(self, numero, quadros, caixa=CORPO, loop=None):
        """quadros: lista de (nome_sprite, ticks) ou (nome_sprite, ticks, caixa_de_golpe) ou com flip 'H'.
        Se a ação já foi definida, a primeira definição vale (as das folhas desenhadas vêm antes)."""
        if numero in self.acoes:
            return
        self.acoes.add(numero)
        if 200 <= numero < 4000 and numero != 2000 and numero not in PROJETEIS:
            k0 = None if self.hazaki else next((k for k, q in enumerate(quadros) if len(q) > 2 and q[2]), None)
            quadros = [(q[0], round(q[1] * (RITMO_PREPARO if k0 is not None and k < k0 else RITMO)) if q[1] > 0 else q[1],
                        *q[2:]) for k, q in enumerate(quadros)]
        if not self.hazaki:
            quadros = self.fluido(numero, quadros)
            loop = self.mapas[numero][loop] - 1 if loop is not None else None
            ativo = next((k for k, q in enumerate(quadros) if len(q) > 2 and q[2]), None)
            if ativo is not None:
                caixa_golpe = quadros[ativo][2]
                self.ativos[numero] = (ativo + 1, caixa_golpe[0] if isinstance(caixa_golpe[0], tuple) else caixa_golpe)
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
            elif numero in PROJETEIS and caixa:
                # o projétil só acerta se a animação tiver caixa de ataque (Clsn1) em cada desenho
                t.append(f"Clsn1: {len(caixa)}")
                for j, cx in enumerate(caixa):
                    t.append(f" Clsn1[{j}] = {cx[0]},{cx[1]},{cx[2]},{cx[3]}")
            g, ind = self.s.codigos[nome]
            mistura = TRANS_FX.get(numero)
            t.append(f"{g},{ind}, 0,0, {ticks}" + (f", {flip}, {mistura}" if mistura else f", {flip}" if flip else ""))
        self.txt.append("\n".join(t) + "\n")
        if numero in ATAQUES_DESPERTADOS or numero == 3100:
            variantes = []
            for i, (nome, ticks, *resto) in enumerate(quadros):
                if not self.hazaki:
                    self.arte_despertada[nome] = nome  # quem troca pelo desenho endiabrado é o RemapSprite
                elif nome not in self.arte_despertada:
                    grupo, indice = self.s.codigos[nome]
                    original = next(img for g, i, img, _, _ in self.s.lista if (g, i) == (grupo, indice))
                    aura = None if self.hazaki else endiabrar(original, i)
                    if aura is None:
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
                    if not self.hazaki and desenhado():
                        resto[0] = CAIXA_DESPERTADA.get(numero, resto[0])
                if i == len(quadros) - 1 and ticks > 0 and 1000 <= numero < 1600:
                    ticks += 6
                variantes.append((self.arte_despertada[nome], ticks, *resto))
            self.acao(numero + 10000, variantes, caixa, loop)



# ------------------------------------------------------------------ efeitos (pixelfx recolorido)
# Os efeitos do pixelfx têm transparência suave, e o SFF só guarda pixel opaco ou vazio. Por isso eles vão com a
# transparência embutida na cor e desenhados com mistura (A = soma, brilho; S = subtração, sombra), marcada no AIR.
# Cada forma do Pengaró tem a sua cor, por mapa de gradiente (o brilho do efeito escolhe a cor da rampa):
WHISKY = ((0, (30, 10, 0)), (.35, (140, 60, 8)), (.7, (235, 155, 35)), (1, (255, 240, 190)))       # Pengaró normal
SOMBRA = ((0, (15, 0, 25)), (.35, (85, 15, 140)), (.75, (175, 85, 255)), (1, (240, 215, 255)))      # endiabrado
SOMBRA_ESCURA = ((0, (0, 0, 0)), (.5, (70, 100, 45)), (1, (120, 160, 85)))  # cor tirada do fundo: escurece puxando o roxo
RECOLORIDOS = {"hit-spark", "crit-hit", "ground-slam"}  # whisky no normal; a versão sombra entra no Despertar (RemapSprite)
METADE = {"ground-slam", "charge-up"}  # efeitos grandes demais para o tamanho do lutador
# Soma de dourado sobre o palco azul vira rosa. Faísca de acerto vai em pixel opaco, cortada pela transparência.
OPACOS = {"hit-spark", "crit-hit"}
# Efeitos próprios do Pengaró: ação -> (efeito, quadros usados, rampa, mistura)
EFEITOS_ENDIABRADO = {
    9210: ("charge-up", range(18, 70), SOMBRA, "A"),           # endiabrado: aura que pulsa em volta do corpo
    9211: ("heavy-landing", range(4, 44), SOMBRA_ESCURA, "S"),  # endiabrado: sombra que gira nos pés
    9212: ("uppercut", range(0, 27), SOMBRA, "A"),              # endiabrado: corte de sombra no membro que bate
    9213: ("hit-flash", range(0, 16), WHISKY, None),            # normal: brilho de whisky no membro que bate
    9214: ("heavy-landing", range(0, 30), WHISKY, None),        # normal: poeira dourada na rasteira
    9215: ("heavy-landing", range(0, 30), SOMBRA, "A"),         # endiabrado: poeira violeta na rasteira
}
TRANS_FX = {}  # ação -> mistura


def pintar(sprite, rampa):
    a = np.asarray(sprite).astype(np.float32)
    luz = a[..., :3].max(axis=2) / 255
    pontos = [p for p, _ in rampa]
    cor = np.stack([np.interp(luz, pontos, [c[k] for _, c in rampa]) for k in range(3)], axis=-1)
    return Image.fromarray(np.dstack([cor, a[..., 3]]).astype(np.uint8), "RGBA")


def efeito_aditivo(sprite):
    a = np.asarray(sprite).astype(np.float32)
    rgb = a[..., :3] * (a[..., 3:] / 255)
    alfa = np.where(a[..., 3] > 8, 255, 0)
    return Image.fromarray(np.dstack([rgb, alfa]).astype(np.uint8), "RGBA")


def efeito_opaco(sprite):
    a = np.array(sprite)
    a[..., 3] = np.where(a[..., 3] >= 110, 255, 0)
    return Image.fromarray(a, "RGBA")


def ler_efeito(nome):
    dados = json.loads((EFEITOS / f"{nome}.json").read_text(encoding="utf-8"))
    pivo = tuple(dados["meta"]["pixelfx"]["pivot"])
    metade = nome in METADE
    quadros = []
    with Image.open(EFEITOS / dados["meta"]["image"]) as imagem:
        folha = imagem.convert("RGBA")
        for quadro in dados["frames"]:
            r = quadro["frame"]
            sprite = folha.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"]))
            if metade:
                sprite = sprite.resize((sprite.width // 2, sprite.height // 2), Image.LANCZOS)
            quadros.append((sprite, max(1, round(quadro["duration"] * 60 / 1000))))
    return ((pivo[0] // 2, pivo[1] // 2) if metade else pivo), quadros


# Pengaró: efeitos desenhados no ChatGPT como os lutadores (ferramentas/efeitos_folha.py), em vez do pixelfx.
# ação -> (efeito do normal, efeito do endiabrado, ticks por quadro ou sequência). Com efeito do normal, só ele entra
# no jogo (as duas formas usam a mesma faísca, regra dos efeitos proporcionais); o do endiabrado só vale sem o normal.
# Sequência de faísca (estilo KOF): (índice do quadro | "F" = clarão gerado do quadro de pico, ticks, escala).
# Medido em jogo de arcade (só o tempo): a faísca vive 8 ticks, 4 desenhos de 2 ticks, com o pico (o clarão) no 3º e
# 4º tick, e o pico tem ~1/3 da altura do lutador (~40 de ~120 unidades, já com o sparkscale do IMPACTO). Some antes do
# fim do congelamento. O finalizador fica maior e mais longo, como sotaque; todo efeito anda de 2 em 2 ticks.
EFEITOS_PROPRIOS = Path(__file__).resolve().parent.parent / "sprites/pengaro/efeitos"
FAISCA_FRACA = [(3, 2, .5), ("F", 2, .5), (14, 2, .5), (19, 2, .5)]
FAISCA_FORTE = [(2, 2, .4), ("F", 2, .45), (12, 2, .4), (18, 2, .4)]
FAISCA_FINAL = [("F", 2, 1), ("F", 2, 1.25), (4, 2, 1), (8, 2, 1), (13, 2, 1), (18, 2, 1)]
FAISCA_DEFESA = [(3, 2, 1), (9, 2, 1), (15, 2, 1)]
FX_PENGARO = {
    9200: ("whisky_acerto", "sombra_acerto", FAISCA_FRACA), 9201: ("whisky_forte", "sombra_forte", FAISCA_FORTE),
    9202: ("defesa", "defesa", FAISCA_DEFESA),
    9205: ("whisky_forte", "sombra_forte", FAISCA_FINAL),
    9210: (None, "sombra_aura", 2), 9211: (None, "sombra_chao", 2), 9212: (None, "sombra_rastro", 1),
    9213: ("whisky_rastro", None, 1), 9214: ("poeira", None, 1), 9215: (None, "sombra_chao", 1),
}
CHAO = {"poeira", "sombra_aura", "sombra_chao"}
FAISCA_POR_FORMA = False


def quadros_proprios(nome):
    pasta = EFEITOS_PROPRIOS / nome
    quadros = [Image.open(f).convert("RGBA") for f in sorted(pasta.glob("*.png"))]
    return [(q, (q.width // 2, q.height - 1 if nome in CHAO else q.height // 2)) for q in quadros]


NEUTRA = ((0, (40, 40, 50)), (.5, (170, 170, 185)), (1, (255, 252, 240)))  # defesa: a mesma nas duas formas
CLARAO = {"whisky": ((255, 215, 120), (60, 25, 5)), "sombra": ((235, 200, 255), (25, 0, 40))}


def quadro_flash(q, cor_clara, contorno):
    """Clarão do 1º tick: a silhueta do quadro de pico, creme onde ele é claro e na cor clara no resto, com contorno."""
    a = np.asarray(q).astype(np.float32)
    dentro = a[..., 3] >= 110
    luz = a[..., :3].max(axis=2) / 255
    cor = np.where((luz > .5)[..., None], np.array((255, 250, 232), np.float32), np.array(cor_clara, np.float32))
    borda = dentro & ~(np.roll(dentro, 1, 0) & np.roll(dentro, -1, 0) & np.roll(dentro, 1, 1) & np.roll(dentro, -1, 1))
    cor[borda] = contorno
    return Image.fromarray(np.dstack([cor, np.where(dentro, 255, 0)]).astype(np.uint8), "RGBA")


def sequencia_faisca(sprites, numero, nome, sequencia, prefixo):
    quadros = quadros_proprios(nome)
    if nome == "defesa":
        quadros = [(pintar(q, NEUTRA), pivo) for q, pivo in quadros]
    pico, pivo_pico = max(quadros, key=lambda qp: int((np.asarray(qp[0])[..., 3] >= 110).sum()))
    lista = []
    for k, (indice, ticks, escala) in enumerate(sequencia):
        if indice == "F":
            q, pivo = quadro_flash(pico, *CLARAO["sombra" if nome.startswith("sombra") else "whisky"]), pivo_pico
        else:
            q, pivo = quadros[min(indice, len(quadros) - 1)]
        if escala != 1:
            w, h = max(1, round(q.width * escala)), max(1, round(q.height * escala))
            q, pivo = q.resize((w, h), Image.NEAREST), (round(pivo[0] * escala), round(pivo[1] * escala))
        chave = f"{prefixo}_{numero}_{k}"
        sprites.add(chave, q, numero, k, pivo)
        lista.append((chave, ticks))
    return lista


def carregar_proprios(sprites):
    acoes = {}
    for numero, (normal, endiabrado, ticks) in FX_PENGARO.items():
        if isinstance(ticks, list):
            acoes[numero] = sequencia_faisca(sprites, numero, normal, ticks, "fx")
            acoes[numero + 30] = sequencia_faisca(sprites, numero + 30, endiabrado, ticks, "dfx")
            continue
        principal = normal or endiabrado
        lista = []
        passo = 2 if ticks == 1 else 1  # efeito anda de 2 em 2 ticks: metade dos desenhos, a mesma duração
        for i, (q, pivo) in enumerate(quadros_proprios(principal)):
            chave = f"fx_{principal}_{i}"
            sprites.add(chave, q, numero, i, pivo)
            if i % passo == 0:
                lista.append((chave, ticks * passo))
        if normal and endiabrado:
            par = quadros_proprios(endiabrado)
            sombra = []
            for i in range(len(lista)):
                q, pivo = par[round(i * (len(par) - 1) / max(1, len(lista) - 1))]
                sprites.add(f"dfx_{principal}_{i}", q, numero + 30, i, pivo)
                sombra.append((f"dfx_{principal}_{i}", ticks))
            acoes[numero + 30] = sombra  # faísca do endiabrado, escolhida no HitDef (faiscas)
        acoes[numero] = lista
    global FAISCA_POR_FORMA
    FAISCA_POR_FORMA = True
    return acoes


def carregar_faiscas(sprites):
    pengaro = getattr(sprites, "folhas", False)
    if pengaro and all((EFEITOS_PROPRIOS / n).exists() for v in FX_PENGARO.values() for n in v[:2] if n):
        return carregar_proprios(sprites)
    acoes = {}
    for numero, nome in FAISCAS.items():
        pivo, quadros = ler_efeito(nome)
        recolor = pengaro and nome in RECOLORIDOS
        opaco = recolor and nome in OPACOS
        mistura = (recolor or nome in METADE) and not opaco
        acabar = efeito_opaco if opaco else efeito_aditivo if mistura else (lambda s: s)
        lista = []
        for indice, (sprite, ticks) in enumerate(quadros):
            base = pintar(sprite, WHISKY) if recolor else sprite
            chave = f"fx_{nome}_{indice}"
            sprites.add(chave, acabar(base), numero, indice, pivo)
            if recolor:
                sprites.add(f"dfx_{nome}_{indice}", acabar(pintar(sprite, SOMBRA)), numero + 30, indice, pivo)
            lista.append((chave, ticks))
        if mistura:
            TRANS_FX[numero] = "A"
        acoes[numero] = lista
    if pengaro:
        for numero, (nome, faixa, rampa, modo) in EFEITOS_ENDIABRADO.items():
            pivo, quadros = ler_efeito(nome)
            lista = []
            for i in faixa:
                sprite, ticks = quadros[i]
                chave = f"sfx_{numero}_{i}"
                pintado = pintar(sprite, rampa)
                sprites.add(chave, efeito_aditivo(pintado) if modo else efeito_opaco(pintado), numero + 40, i, pivo)
                lista.append((chave, ticks))
            if modo:
                TRANS_FX[numero] = modo
            acoes[numero] = lista
    return acoes


FUMACA = ("#150d1d", "#22162e", "#33224a")
ELO = ("#e4e0ea", "#8f879c", "#1a1220")


def _achar_pulso(alfa, ponta, raio, comprimento):
    """Do bico de uma mão ou pé até a junta: anda `comprimento` px na direção em que a massa do membro está.
    Devolve (x, y, dx, dy), com (dx, dy) apontando da ponta para o corpo."""
    px = alfa.load()
    tx, ty = ponta
    sx = sy = n = 0
    for y in range(max(0, ty - raio), min(ALT, ty + raio + 1)):
        for x in range(max(0, tx - raio), min(LARG, tx + raio + 1)):
            if px[x, y] >= 128 and (x - tx) ** 2 + (y - ty) ** 2 <= raio * raio:
                sx += x
                sy += y
                n += 1
    if not n:
        return None
    dx, dy = sx / n - tx, sy / n - ty
    norma = math.hypot(dx, dy) or 1
    dx, dy = dx / norma, dy / norma
    return (tx + dx * comprimento, ty + dy * comprimento, dx, dy)


def pontas(alfa):
    """Mãos e pé de trás de um lutador virado para a direita. Devolve {nome: (x, y, dx, dy)}, com a junta (pulso ou
    tornozelo) e a direção do membro, ou {} se não achar."""
    px = alfa.load()
    caixa = alfa.getbbox()
    if not caixa:
        return {}
    x0, y0, x1, y1 = caixa
    alt = y1 - y0

    def extremo(ya, yb, maior):
        melhor = None
        for y in range(y0 + int(alt * ya), y0 + int(alt * yb)):
            for x in range(x0, x1):
                if px[x, y] >= 128 and (melhor is None or (x > melhor[0] if maior else x < melhor[0])):
                    melhor = (x, y)
        return melhor

    def mais_baixo_a_esquerda():
        melhor = None
        meio = (x0 + x1) // 2
        for y in range(y1 - 1, y0 + int(alt * .6), -1):
            for x in range(x0, meio):
                if px[x, y] >= 128:
                    return (x + 6, y)
        return melhor
    pontas_ = {"mao_f": (extremo(.18, .55, True), 12, 11), "mao_t": (extremo(.25, .75, False), 12, 11),
               "pe_t": (mais_baixo_a_esquerda(), 16, 12)}
    achadas = {}
    for nome, (ponta, raio, comp) in pontas_.items():
        if ponta:
            r = _achar_pulso(alfa, ponta, raio, comp)
            if r:
                achadas[nome] = r
    return achadas


def fumaca_solida(tela, ponto, i, tamanho=1.0, sentido=-1):
    """Rastro de fumaça escura e opaca (a paleta do jogo não tem meio-tom) que sai de um ponto e sobe para trás."""
    d = ImageDraw.Draw(tela)
    x, y = ponto
    sorte = random.Random(int(i) // 2 * 7919 + int(x) % 17)
    for k in range(11):
        t = k / 10
        onda = math.sin(i * .30 + k * .8)
        cx = x + sentido * (3 + 8 * k) * tamanho + onda * 3 + sorte.uniform(-1.5, 1.5)
        cy = y - 2.2 * k * tamanho - abs(onda) * 4 + sorte.uniform(-2, 2)
        r = max(1.2, (7.5 - 6 * t) * tamanho * sorte.uniform(.75, 1.2))
        cor = FUMACA[min(2, int(t * 3.2))]
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=cor)
        if k % 3 == 1:
            d.ellipse((cx - r * .5, cy - r * .9, cx + r * .2, cy - r * .2), fill=FUMACA[min(2, int(t * 3.2) + 1)])
        if k % 4 == 3:
            px_, py_ = cx + sorte.uniform(-6, 6), cy - sorte.uniform(6, 12)
            d.rectangle((px_, py_, px_ + 1, py_ + 1), fill=FUMACA[2])


def elos(tela, junta):
    """Algema com corrente partida: três elos claros, com contorno escuro, em volta do pulso ou do tornozelo,
    atravessados no membro (perpendiculares à direção dele)."""
    x, y, dx, dy = junta
    d = ImageDraw.Draw(tela)
    px_, py_ = -dy, dx
    for k in (-1, 0, 1):
        ex, ey = x + px_ * k * 3.2, y + py_ * k * 3.2
        d.ellipse((ex - 2.6, ey - 2.2, ex + 2.6, ey + 2.2), fill=ELO[2])
        d.ellipse((ex - 1.6, ey - 1.2, ex + 1.6, ey + 1.2), outline=ELO[0], fill=ELO[1])


def endiabrar(original, i):
    """Forma despertada (referência em sprites/pengaro/quadros/endiabrado_referencia.png): o corpo vira uma sombra
    quase preta com o relevo em roxo escuro, olhos violeta, algemas de corrente partida nos pulsos e no tornozelo
    e fumaça escura e sólida saindo do braço e da perna de trás."""
    if original.size != (LARG, ALT):
        return None
    tela = Image.new("RGBA", original.size)
    alfa = original.getchannel("A").point(lambda a: 255 if a >= 128 else 0)
    ref = pontas(alfa)
    if "mao_t" in ref:
        fumaca_solida(tela, (ref["mao_t"][0], ref["mao_t"][1] - 2), i, 1.0)
    if "pe_t" in ref:
        fumaca_solida(tela, (ref["pe_t"][0], ref["pe_t"][1] - 2), i + 3, .8)
    contorno = Image.new("RGBA", original.size, (14, 8, 20))
    contorno.putalpha(alfa)
    tela.alpha_composite(contorno, (-2, 1))
    cinza = ImageOps.autocontrast(original.convert("RGB").convert("L"), cutoff=2).point(lambda v: int(255 * (v / 255) ** 1.5))
    corpo = ImageOps.colorize(cinza, black="#08060b", mid="#17111f", white="#4a3c58").convert("RGBA")
    corpo.putalpha(alfa)
    tela.alpha_composite(corpo)
    olhos_roxos(tela, alfa)
    for nome in ("mao_f", "mao_t", "pe_t"):
        if nome in ref:
            elos(tela, ref[nome])
    return tela


def olhos_roxos(tela, alfa):
    """Olhos violeta brilhantes, achando a cabeça pelo ponto mais alto do corpo (só se for mesmo uma cabeça)."""
    caixa = alfa.getbbox()
    if not caixa:
        return
    topo = caixa[1]
    faixa = alfa.crop((0, topo, LARG, topo + 6)).getbbox()
    if not faixa or faixa[2] - faixa[0] > 36:
        return
    cx = (faixa[0] + faixa[2]) // 2
    d = ImageDraw.Draw(tela)
    y = topo + 14
    for x in (cx + 6, cx + 11):
        d.rectangle((x - 1, y - 1, x + 2, y + 2), fill="#5a1aa8")
        d.rectangle((x, y, x + 1, y + 1), fill="#e6b3ff")


# ------------------------------------------------------------------ folhas desenhadas (estilo arcade)
# Quadros recortados das folhas de 8 desenhos (sprites/pengaro/folhas -> ferramentas/recortar_quadros.py),
# em sprites/pengaro/quadros/<folha>/00..07.png. Só o Pengaró usa; o Hazaki continua com as poses dele.
FOLHAS = ("agachado", "pulo", "defesa", "apanha", "queda", "levanta", "rolamento", "chute_baixo", "chute_alto",
          "baixo_soco", "cabecada", "rasteirinha", "rasteira", "ar_soco", "bicicleta", "agarrao", "lata",
          "vitoria", "derrota", "provoca", "bola", "compasso", "armada", "caneta", "afastar", "martelo", "soco",
          "golaco", "despertar_a", "despertar_b", "corre", "recuo")  # corre e recuo no fim: não mudam os números dos outros

# Sprites antigos (feitos girando/esticando as 9 poses) trocados por um desenho da folha: nome -> (folha, quadro).
# Assim todo golpe que ainda usa esses nomes (especiais, super, Despertar) já aparece com a arte desenhada.
TROCA_POR_FOLHA = {
    "agacha0": ("agachado", 2), "agacha1": ("agachado", 4), "agacha2": ("agachado", 6),
    "prepulo": ("pulo", 0), "pulo_sobe": ("pulo", 2), "pulo_topo": ("pulo", 3), "pulo_desce": ("pulo", 5),
    "pouso": ("pulo", 7), "defesa": ("defesa", 3), "defesa_ai": ("defesa", 5), "recua": ("defesa", 6),
    "parry": ("defesa", 2), "apanha0": ("apanha", 1), "apanha1": ("apanha", 3), "apanha2": ("apanha", 4),
    "cai0": ("queda", 1), "cai1": ("queda", 2), "cai2": ("queda", 4), "deitado": ("queda", 7),
    "levanta0": ("levanta", 2), "levanta1": ("levanta", 5), "levanta2": ("levanta", 6),
    "chute0": ("chute_alto", 2), "chute1": ("chute_alto", 3), "chute2": ("chute_alto", 4), "chute3": ("chute_alto", 5),
    "baixo_soco": ("baixo_soco", 4), "baixo_cima0": ("cabecada", 2), "baixo_cima1": ("cabecada", 4),
    "rasteira0": ("rasteira", 2), "rasteira1": ("rasteira", 4), "rasteira2": ("rasteira", 4), "rasteira3": ("rasteira", 6),
    "ar_soco": ("ar_soco", 4), "bicicleta": ("bicicleta", 4), "agarra": ("agarrao", 2), "joga": ("agarrao", 6),
    "especial": ("bola", 4), "kick_alto": ("armada", 4),
    "gira0": ("compasso", 2), "gira1": ("compasso", 3), "gira2": ("compasso", 4), "gira3": ("compasso", 5),
    "lata0": ("lata", 2), "lata1": ("lata", 4), "lata2": ("lata", 7),
    "soco0": ("soco", 3), "soco1": ("soco", 5), "soco2": ("soco", 5), "soco3": ("soco", 6),
    "parado0": ("ginga_fluida", 0), "anda0": ("anda_fluida", 0), "ar_chute": ("bicicleta", 3), "ar_cotovelo": ("ar_soco", 4),
    "pisa": ("chute_baixo", 4), "defesa_baixa": ("agachado", 7),
    **{f"corre{i}": ("anda_fluida", i) for i in range(4)},
    **{f"tonto{i}": ("apanha", 3 + i % 2) for i in range(4)},
    **{f"rola{i}": ("rolamento", i) for i in range(8)},
    # sem bola: na intro, na provocação e na vitória ele dá um gole
    **{f"embaixada{i}": ("lata", i + 1) for i in range(4)},
}


# Sprites que não são o corpo do Pengaró (balões, faíscas, projétil) não ganham a garrafa.
# Os quadros desenhados já têm a garrafa.
SEM_WHISKY = ("balao_", "fx_", "bola", "bolao", "quica", "retrato", "chuva", "f_", "m_", "q_soco", "q_ginga_fluida",
              "q_anda_fluida", "ginga_endiabrada", "e_", "endiabrado_")
QUADROS = RAIZ / "sprites/pengaro/quadros"


def limpar_borda(img, tinta=True):
    """Tira a franja roxa que sobra do fundo magenta no contorno e os pontinhos soltos em volta da figura.
    tinta=False (endiabrado): o roxo e o relevo magenta do endiabrado são o próprio corpo, então só os pontinhos saem."""
    import cv2
    a = np.array(img)
    if tinta:
        r, g_, b = (a[..., i].astype(int) for i in range(3))
        tinta = (r > g_ + 30) & (b > g_ + 30) & (np.abs(r - b) < 45)  # magenta misturado
        for _ in range(2):
            cheio = a[..., 3] >= 128
            borda = cheio & ~cv2.erode(cheio.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
            a[borda & tinta, 3] = 0
    cheio = (a[..., 3] >= 128).astype(np.uint8)
    n, rotulos, dados, _ = cv2.connectedComponentsWithStats(cheio, connectivity=8)
    for i in range(1, n):
        if dados[i, cv2.CC_STAT_AREA] < 6:
            a[rotulos == i, 3] = 0
    return Image.fromarray(a)


def sem_rosa(img, miolo_branco=False):
    """Forma normal do Pengaró: ele não tem rosa nem magenta em lugar nenhum, então todo pixel assim é resto do fundo
    da folha (mancha no quadril, ponto na boca, franja no cordão). Mancha que encosta no vazio some; a que está
    fechada dentro do corpo é pintada com a cor dos vizinhos."""
    import cv2
    a = np.array(img)
    r, g_, b = (a[..., i].astype(int) for i in range(3))
    cheio = a[..., 3] >= 128
    forte = cheio & (r > g_ + 40) & (b > g_ + 40)
    if not forte.any():
        return img
    claro = cheio & (r > g_ + 18) & (b > g_ + 18) & (np.maximum(r, b) > 150)  # o halo lilás em volta da mancha
    claro |= cheio & (r > g_ + 8) & (b > g_ + 8) & (np.minimum(r, b) > 225)  # e a parte quase branca dele
    n, rotulos = cv2.connectedComponents((forte | claro).astype(np.uint8), connectivity=8)
    rosa = np.isin(rotulos, np.unique(rotulos[forte])) & (forte | claro)
    n, rotulos, dados, _ = cv2.connectedComponentsWithStats(rosa.astype(np.uint8), connectivity=8)
    vazio = cv2.dilate((~cheio).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    pintar = np.zeros(rosa.shape, bool)
    fora = np.zeros(rosa.shape, bool)
    for i in range(1, n):
        pedaco = rotulos == i
        if (pedaco & vazio).any():
            a[pedaco, 3] = 0
            fora |= pedaco
        else:
            pintar |= pedaco
    # o miolo do clarão é branco puro (a calça é creme, puxa para o amarelo): sai junto com o rosa que o cercava,
    # senão sobra uma tira branca serrilhada atrás da coxa (chute alto)
    miolo = cheio & (r >= 248) & (b >= 248) & (g_ >= 230)
    for _ in range(12 if miolo_branco else 0):
        mais = miolo & ~fora & cv2.dilate(fora.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        if not mais.any():
            break
        a[mais, 3] = 0
        fora |= mais
    if pintar.any():
        a[..., :3] = cv2.inpaint(np.ascontiguousarray(a[..., :3]), pintar.astype(np.uint8) * 255, 3, cv2.INPAINT_TELEA)
    return limpar_borda(Image.fromarray(a), tinta=False)


def sem_fundo_endiabrado(img):
    """Folhas endiabradas do Pengaró: bloco de magenta vivo (a cor do fundo da folha) preso no vão entre braço, peito
    e coxa. Só bloco de 8 px para cima e abaixo da cabeça: o brilho do olho é pequeno e fica. O que encosta no vazio
    some; o que está fechado no corpo ganha a cor dos vizinhos."""
    import cv2
    a = np.array(img)
    r, g_, b = (a[..., i].astype(int) for i in range(3))
    cheio = a[..., 3] >= 128
    ys = np.flatnonzero(cheio.any(axis=1))
    if not len(ys):
        return img
    vivo = cheio & (r > 190) & (b > 190) & (g_ < 110)
    n, rotulos, dados, _ = cv2.connectedComponentsWithStats(vivo.astype(np.uint8), connectivity=8)
    vazio = cv2.dilate((~cheio).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    pintar = np.zeros(vivo.shape, bool)
    for i in range(1, n):
        if dados[i, cv2.CC_STAT_AREA] < 8 or dados[i, cv2.CC_STAT_TOP] < ys[0] + 30 and dados[i, cv2.CC_STAT_AREA] < 40:
            continue
        pedaco = rotulos == i
        if (pedaco & vazio).any():
            a[pedaco, 3] = 0
        else:
            pintar |= pedaco
    if pintar.any():
        a[..., :3] = cv2.inpaint(np.ascontiguousarray(a[..., :3]), pintar.astype(np.uint8) * 255, 3, cv2.INPAINT_TELEA)
    return Image.fromarray(a)


def calca_roxa(img):
    """Folhas endiabradas: em metade delas (andar, agachar...) a calça veio marrom-acinzentada e nas outras (ginga,
    soco) roxa como o corpo; ele trocava de cor ao andar. O marrom vai para o roxo da ginga, no mesmo claro-escuro."""
    a = np.array(img)
    r, g_, b = (a[..., i].astype(float) for i in range(3))
    marrom = (a[..., 3] >= 128) & (r > 40) & (g_ > 0.56 * r) & (g_ < 0.85 * r) & (b >= 0.9 * g_) & (r >= b)
    a[marrom, 0] = np.round(r[marrom] * 0.97)
    a[marrom, 1] = np.round(r[marrom] * 0.50)
    a[marrom, 2] = np.round(r[marrom] * 0.92)
    return Image.fromarray(a)


RELEVO_ENDIABRADO = (190, 39, 168)  # cor mediana do relevo que o recorte antigo apagava das folhas endiabradas


def fechar_furos(img, limite=40):
    """Os quadros do meio das folhas endiabradas vieram do Blender já furados (o recorte antigo apagou o relevo magenta
    como se fosse fundo). Fecha só buraco pequeno, todo cercado de corpo, com a cor do relevo. Vão de verdade entre
    braço e tronco é maior que isso e fica aberto."""
    import cv2
    a = np.array(img)
    vazio = (a[..., 3] < 128).astype(np.uint8)
    n, rotulos, dados, _ = cv2.connectedComponentsWithStats(vazio, connectivity=4)
    h, w = vazio.shape
    for i in range(1, n):
        x, y, ww, hh, area = dados[i]
        if area <= limite and x > 0 and y > 0 and x + ww < w and y + hh < h:
            furo = rotulos == i
            if QUADROS != QUADROS_PENGARO:
                a[furo] = (*RELEVO_ENDIABRADO, 255)
                continue
            # Pengaró: o furo ganha a cor de quem está em volta dele, não o magenta vivo do relevo (ficava mancha de
            # fundo no meio da figura); elo de corrente (borda cinza ou branca) é vão de verdade e fica aberto.
            borda = cv2.dilate(furo.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~furo & (a[..., 3] >= 128)
            em_volta = a[borda][:, :3].astype(int)
            cor = np.median(em_volta, axis=0)
            if cor.max() - cor.min() >= 40 and (em_volta.min(axis=1) > 100).mean() < 0.3:
                a[furo] = (*(int(v) for v in cor), 255)
    return Image.fromarray(a)


# Folhas endiabradas em que a algema do tornozelo veio desenhada nos DOIS pés; na ginga, no andar e nos golpes só o
# pé de trás tem. A do pé da frente é pintada com o roxo da perna.
ALGEMA_SO_ATRAS = {"e_agachado"}


def sem_algema_da_frente(img):
    a = np.array(img)
    cheio = a[..., 3] >= 128
    ys, xs = np.flatnonzero(cheio.any(axis=1)), np.flatnonzero(cheio.any(axis=0))
    if not len(ys):
        return img
    rgb = a[..., :3].astype(int)
    cinza = cheio & (rgb.max(axis=2) - rgb.min(axis=2) < 40) & (rgb.max(axis=2) > 95)
    regiao = np.zeros(cheio.shape, bool)
    regiao[ys[-1] - int((ys[-1] - ys[0]) * 0.25):, (xs[0] + xs[-1]) // 2 + 8:] = True
    alvo = cinza & regiao
    claro = rgb.max(axis=2)[alvo] / 255
    a[alvo, 0] = np.round(40 + 95 * claro)
    a[alvo, 1] = np.round(18 + 45 * claro)
    a[alvo, 2] = np.round(38 + 90 * claro)
    return Image.fromarray(a)


def sem_farelo(img):
    """Transformação (despertar_b): pedaço pequeno solto, longe do corpo e da aura, é farelo do recorte e some."""
    import cv2
    a = np.array(img)
    n, rotulos, dados, _ = cv2.connectedComponentsWithStats((a[..., 3] >= 128).astype(np.uint8), connectivity=8)
    if n < 3:
        return img
    maior = 1 + int(np.argmax(dados[1:, cv2.CC_STAT_AREA]))
    perto = cv2.dilate((rotulos == maior).astype(np.uint8), np.ones((17, 17), np.uint8)).astype(bool)
    for i in range(1, n):
        if i != maior and dados[i, cv2.CC_STAT_AREA] < 60 and not (perto & (rotulos == i)).any():
            a[rotulos == i, 3] = 0
    return Image.fromarray(a)


def forma_do_quadro(arquivo):
    """'endiabrado' para as folhas endiabradas (e_*, endiabrado, ginga_endiabrada), 'despertar_b' para a parte
    endiabrada da transformação e None para o resto."""
    arquivo = Path(arquivo)
    if RAIZ / "sprites/pengaro/quadros" not in arquivo.parents:  # só as folhas do Pengaró (o Gutto reusa esta função)
        return None
    pasta = arquivo.parent.parent.name if arquivo.parent.name == "meio" else arquivo.parent.name
    if pasta.startswith("e_") or pasta in ("endiabrado", "ginga_endiabrada"):
        return "endiabrado"
    return "despertar_b" if pasta == "despertar_b" else None


def eh_boss(arquivo):
    """Desenho do Endiabrado na arte arcade (quadros_arcade/e_<folha>/NN.png, Lote 7)."""
    arquivo = Path(arquivo)
    return arquivo.parent.name.startswith("e_") and arquivo.parent.parent == QUADROS_ARCADE


def abrir_quadro(arquivo):
    """Quadro do Blender já vem na tela do jogo; os antigos, de 224x128, são colados com os pés no eixo."""
    img = Image.open(arquivo).convert("RGBA")
    if eh_boss(arquivo):  # Lote 7: já vem na tela do jogo, na paleta do boss; o violeta é do desenho, não franja
        return limpar_borda(img, tinta=False)
    forma = forma_do_quadro(arquivo)
    if img.size != (LARG, ALT):
        tela = Image.new("RGBA", (LARG, ALT))
        tela.alpha_composite(img, (EIXO_X - 104, EIXO_Y - 119))
        img = tela
    img = limpar_borda(img, tinta=forma is None)
    if forma is None and RAIZ / "sprites/pengaro/quadros" in Path(arquivo).parents:
        img = sem_rosa(img, miolo_branco=True)
    elif forma == "endiabrado":  # forma_do_quadro só devolve isso para as folhas do Pengaró
        img = calca_roxa(sem_fundo_endiabrado(img))
        pasta = Path(arquivo).parent.parent.name if Path(arquivo).parent.name == "meio" else Path(arquivo).parent.name
        if pasta in ALGEMA_SO_ATRAS:
            img = sem_algema_da_frente(img)
    img = fechar_furos(img) if forma == "endiabrado" else img
    if forma == "despertar_b":
        img = sem_farelo(img)
    if RAIZ / "sprites/pengaro/quadros" in Path(arquivo).parents:
        pasta = Path(arquivo).parent.parent.name if Path(arquivo).parent.name == "meio" else Path(arquivo).parent.name
        if pasta in CANELEIRA_NO_APOIO:
            img = canela_creme(img)
            nome = Path(arquivo).stem
            desenhos = CANELEIRA_NO_APOIO[pasta]
            n = int(nome.split("_")[0])
            if (n in desenhos and n + 1 in desenhos) if Path(arquivo).parent.name == "meio" else n in desenhos:
                img = caneleira_no_apoio(img)
        base = base_figura(img)
        if pasta in PES_NO_CHAO and base is not None and 0 < abs(EIXO_Y - 1 - base) <= 3:
            img = move(img, 0, EIXO_Y - 1 - base)
    return marcar_origem(img, arquivo)


def marcar_origem(img, arquivo):
    """Guarda no quadro o arquivo de onde ele veio: o colar_endiabrado usa para montar o gêmeo 3x (gemeo_hd)."""
    img.origem_quadro = Path(arquivo)
    return img


# Chutes em pé: nos desenhos do golpe a caneleira não estava em perna nenhuma (ou estava na que chuta) e voltava de
# estalo no último desenho. A perna de apoio é a de trás, a da caneleira: ela é pintada na canela de apoio, do
# tornozelo para cima, com a luz da própria calça. folha -> desenhos (e os quadros do meio entre eles).
CANELEIRA_NO_APOIO = {"chute_baixo": range(2, 7), "chute_alto": range(1, 7), "afastar": (5,)}


# O retoque que tirou a caneleira da perna que chuta pintou a canela com quatro tons de lilás frio, e a calça é creme:
# ficava uma placa de outra cor. Os quatro tons vão para o creme da calça, do claro à sombra.
PLACA_DA_CANELA = {(246, 242, 238): (254, 250, 228), (230, 224, 228): (252, 236, 208),
                   (215, 207, 218): (238, 216, 190), (200, 190, 208): (208, 188, 172)}


def canela_creme(img):
    a = np.array(img)
    for de, para in PLACA_DA_CANELA.items():
        a[(a[..., :3] == de).all(axis=2) & (a[..., 3] >= 128), :3] = para
    return Image.fromarray(a)


def caneleira_no_apoio(img):
    import cv2
    a = np.array(img)
    cheio = a[..., 3] >= 128
    base = base_figura(img)
    if base is None:
        return img
    rgb = a[..., :3].astype(int)
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    pe = np.flatnonzero(cheio[base - 3:base + 1].any(axis=0))
    quebra = np.flatnonzero(np.diff(pe) > 3)
    pe = pe[:quebra[0] + 1] if len(quebra) else pe  # o pé mais atrás que pisa
    calca = cheio & (mn > 105) & (mx - mn < 75) & (rgb[..., 0] - rgb[..., 2] < 70)
    faixa = np.zeros(cheio.shape, bool)
    faixa[base - 36:base - 6, max(0, pe[0] - 14):pe[-1] + 12] = True
    n, rotulos, dados, _ = cv2.connectedComponentsWithStats((calca & faixa).astype(np.uint8), connectivity=4)
    if n < 2:
        return img
    # o pedaço de calça logo acima do pé de apoio
    perto = [i for i in range(1, n) if dados[i, cv2.CC_STAT_AREA] >= 60
             and dados[i, cv2.CC_STAT_LEFT] <= pe[-1] and dados[i, cv2.CC_STAT_LEFT] + dados[i, cv2.CC_STAT_WIDTH] >= pe[0]]
    if not perto:
        return img
    alvo = rotulos == max(perto, key=lambda i: dados[i, cv2.CC_STAT_AREA])
    fechado = cv2.morphologyEx(alvo.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)).astype(bool)
    alvo |= fechado & cheio & faixa & (mn > 80) & (rgb[..., 0] - rgb[..., 2] < 70)  # pontos claros soltos no meio
    luz = np.clip((mx - 150) / 100, 0, 1)
    ys, xs = np.nonzero(alvo)
    trama = ((xs + ys) % 5 == 0) | ((xs - ys) % 5 == 0)
    cor = np.stack([40 + 45 * luz[alvo], 52 + 45 * luz[alvo], 40 + 30 * luz[alvo]], axis=1)
    cor[trama] *= 0.75
    a[ys, xs, :3] = np.round(cor).astype(np.uint8)
    return Image.fromarray(a)


# Folhas em que ele está sempre com os pés no chão: desenho ou quadro do meio que veio 1 a 3 px acima ou abaixo da
# linha do chão é assentado nela (agachado parado: a figura inteira subia 1 px, os pés junto, a cada respiração).
PES_NO_CHAO = {"agachado", "e_agachado"}


def centro_tronco(img):
    """Meio do tronco (do peito à barriga) de um quadro na tela do jogo."""
    alfa = np.asarray(img)[..., 3] >= 128
    ys = np.flatnonzero(alfa.any(axis=1))
    if not len(ys):
        return None
    topo, base = ys[0], ys[-1]
    meios = []
    for y in range(topo + int((base - topo) * 0.3), topo + max(1, int((base - topo) * 0.6))):
        linha = np.flatnonzero(alfa[y])
        if len(linha):
            quebras = np.flatnonzero(np.diff(linha) > 1)
            inicios, fins = np.r_[linha[0], linha[quebras + 1]], np.r_[linha[quebras], linha[-1]]
            k = int(np.argmax(fins - inicios))
            meios.append((inicios[k] + fins[k]) / 2)
    return float(np.median(meios)) if meios else None


def base_figura(img):
    """Última linha com pixel opaco (onde o pé pisa), ou None."""
    ys = np.flatnonzero((np.asarray(img)[..., 3] >= 128).any(axis=1))
    return int(ys[-1]) if len(ys) else None


def altura_corpo(img):
    """Altura do maior pedaço da figura (fumaça e cacos soltos não contam)."""
    import cv2
    n, _, dados, _ = cv2.connectedComponentsWithStats((np.asarray(img)[..., 3] >= 128).astype(np.uint8), connectivity=8)
    return int(dados[1 + int(np.argmax(dados[1:, cv2.CC_STAT_AREA])), cv2.CC_STAT_HEIGHT]) if n > 1 else 0


# Ginga e andar são SÓ desenhos, segurados (estilo arcade): nenhum quadro de fluxo óptico. Os quadros do meio que
# existiam aqui (ginga_fluida, anda_fluida, 64 e 48 quadros) eram um desenho entortado até a metade e trocado pelo
# seguinte; onde o braço mudava de lugar aparecia uma terceira mão e a caneleira trocava de perna. Os nomes dos
# sprites (q_ginga_fluida<i>, q_anda_fluida<i>) ficaram, porque o resto do gerador e as ferramentas os conhecem.
# nome do loop -> (folha em quadros_arcade/, desenhos na ordem em que tocam, ticks de cada um)
QUADROS_ARCADE = RAIZ / "sprites/pengaro/quadros_arcade"
QUADROS_ARCADE_HD = RAIZ / "sprites/pengaro/quadros_arcade_hd"  # os mesmos desenhos em 3x (hd_guiado.py)
LOOPS = {
    # Um vai-e-volta só do pé de trás, com o da frente cravado: em pé (3, 7), pé de trás na ponta (5), afundo atrás
    # (6, 2), volta na ponta do pé (1). Os desenhos 0 e 4 da folha (base aberta, tronco jogado para trás) ficam fora:
    # entre eles e os vizinhos a cabeça andava 23 px e o pé de trás fazia zigue-zague (-45, -31, -57, -24...).
    "ginga_fluida": ("ginga", (3, 7, 5, 6, 2, 1), (6, 6, 5, 7, 7, 5)),
    # contato, passagem e contato da perna da caneleira (0, 2, 3); peso desce, impulso e saída da outra (4, 1, 5).
    # Os desenhos 6 e 7 da folha ficam fora: o 6 repete o 2 (levanta a MESMA perna) e o 7 repete o 0.
    # As duas metades da passada duram o mesmo (16 e 18 ticks): antes eram 16 e 21 e o passo mancava.
    # (folha arcade do Lote 6, 2026-11-11: base aberta como a da ginga e as duas pernas alternando de verdade; na
    # folha anterior a perna da caneleira subia duas vezes e a outra nunca passava.) Contato com a caneleira atrás (0),
    # a perna da caneleira passa (2) e pisa na frente (3, 4); a outra passa (6) e pisa na frente (7). O 1 e o 5 da
    # folha ficam fora: são o "peso desce" com a caneleira na perna de trás nos dois, o que desfazia a troca de pernas.
    # As duas metades da passada duram o mesmo (17 e 17 ticks; o total de 34 é o de antes).
    "anda_fluida": ("anda", (0, 2, 3, 4, 6, 7), (6, 6, 5, 6, 6, 5)),
}
# Forma endiabrada, desenho a desenho do loop normal: (pasta em quadros/, desenhos). Só os desenhos limpos da folha:
# na ginga ficam fora o 3 e o 5 (algema nos dois tornozelos) e o 4 (mancha verde na coxa); em pé (0, 7), passo (1),
# afundo (2, duas vezes: no 6 o pé da frente abre e o tronco pulava 40 px), passo (1), como a ginga normal. No andar só as poses de bote (1, 5, 3): alternar com a guarda em pé
# (0, 4, 7) fazia a cabeça subir e descer 10 px e os braços trocarem de pose a cada desenho.
# (Lote 7, 2026-11-11: o Endiabrado virou o boss final na arte arcade e as folhas e_ginga e e_anda seguem a folha
# normal desenho a desenho; o loop toca os MESMOS desenhos, na mesma ordem e nos mesmos tempos do normal. As pastas
# antigas quadros/ginga_endiabrada e quadros/e_anda saíram do jogo.)
LOOPS_ENDIABRADOS = {"ginga_fluida": ("e_ginga", LOOPS["ginga_fluida"][1]),
                     "anda_fluida": ("e_anda", LOOPS["anda_fluida"][1])}
# Os grupos do .sff são dados em sequência e SPRITES_VITIMA (os desenhos que a vítima de um arremesso empresta, iguais
# em todos os lutadores) guarda números fixos. Os loops de fluxo ocupavam 64 e 48 grupos; essas vagas ficam
# reservadas (vazias) para nenhum sprite depois deles mudar de número.
VAGAS_DO_FLUXO = {"ginga_fluida": 64, "anda_fluida": 48}
PE_DA_FRENTE_ENDIABRADO = 205  # o mesmo para a ginga endiabrada (a base dela é mais fechada)
PE_DA_FRENTE = 219  # x da ponta do pé da frente em todos os desenhos da ginga: o pé plantado não escorrega
# Gutto e Raiclaven usam este módulo trocando QUADROS e ainda têm os loops de fluxo deles (pastas ginga_fluida,
# anda_fluida, ginga_endiabrada, e_anda_fluida, com um desenho-chave a cada 8 ou 6 quadros): para eles nada muda.
QUADROS_PENGARO = QUADROS
FLUXO = {"ginga_fluida": ("ginga_endiabrada", 8), "anda_fluida": ("e_anda_fluida", 6)}
_FATOR, _DX_CHAVE = {}, {}


def desenhado():
    """True no Pengaró: ginga e andar só com desenhos. False em quem ainda usa as pastas de fluxo."""
    return QUADROS == QUADROS_PENGARO


def passo_do_loop(pasta):
    """De quantos em quantos quadros do loop há um desenho-chave."""
    return 1 if desenhado() else FLUXO[pasta][1]


def quadros_do_loop(pasta):
    return len(LOOPS[pasta][1]) if desenhado() else len(list((QUADROS / pasta).glob("*.png")))


def tempos_do_loop(pasta):
    return LOOPS[pasta][2] if desenhado() else (2,) * quadros_do_loop(pasta)


def quadro_loop(pasta, i):
    """Desenho i do loop normal, na tela do jogo. Na ginga o pé da frente fica cravado no mesmo x (quem balança é o
    tronco); no andar o tronco fica no eixo, porque quem anda é o jogo."""
    if not desenhado():
        return abrir_quadro(QUADROS / pasta / f"{i:02d}.png")
    folha, ordem, _ = LOOPS[pasta]
    img = Image.open(QUADROS_ARCADE / folha / f"{ordem[i]:02d}.png").convert("RGBA")
    if pasta != "ginga_fluida":
        return img
    img = mao_sem_cordao(img)
    chao = np.flatnonzero((np.asarray(img)[EIXO_Y - 6:EIXO_Y, :, 3] >= 128).any(axis=0))
    return move(img, PE_DA_FRENTE - int(chao[-1])) if len(chao) else img


def mao_sem_cordao(img):
    """Ginga arcade: a quantização deixou pontos da cor do cordão (amarelo, laranja) e da sombra da calça (lilás, roxo)
    nas pontas dos dedos da mão aberta. Acima da faixa só existe pele: esses pontos viram pele ou contorno."""
    a = np.array(img)
    rgb = a[..., :3].astype(int)
    eh = lambda cor: (np.abs(rgb - np.array(cor)).sum(axis=2) < 12) & (a[..., 3] >= 128)
    faixa = np.flatnonzero((eh((20, 156, 99)) | eh((20, 80, 63))).any(axis=1))
    if not len(faixa):
        return img
    acima = np.zeros(a.shape[:2], bool)
    acima[:faixa[0] - 2] = True
    for cores, nova in ((((253, 197, 20), (223, 120, 20), (148, 146, 189)), (253, 195, 114)), (((53, 31, 92),), (76, 20, 20))):
        for cor in cores:
            a[acima & eh(cor), :3] = nova
    return Image.fromarray(a)


def perna_de_tras_na_sombra(img):
    """Andar arcade, desenho 0: a perna sem caneleira (a de trás, lilás de sombra nos outros desenhos) está à frente e
    veio clara da canela para baixo; a cor da mesma perna piscava na volta do ciclo. Fica na sombra como nos outros."""
    a = np.array(img)
    rgb = a[..., :3].astype(int)
    eh = lambda cor: np.abs(rgb - np.array(cor)).sum(axis=2) < 12
    regiao = np.zeros(a.shape[:2], bool)
    regiao[174:, 184:] = True
    regiao &= a[..., 3] >= 128
    creme, branco = eh((253, 236, 207)) & regiao, eh((253, 250, 237)) & regiao
    a[creme, :3] = (148, 146, 189)
    a[branco, :3] = (253, 236, 207)
    return Image.fromarray(a)


def arquivo_loop_endiabrado(pasta, i):
    if not desenhado():
        return QUADROS / FLUXO[pasta][0] / f"{i:02d}.png"
    outra, ordem = LOOPS_ENDIABRADOS[pasta]
    return QUADROS_ARCADE / outra / f"{ordem[i]:02d}.png"


def pasta_endiabrada(pasta):
    return (f"e_{pasta}", 1)


def fator_endiabrado(pasta):
    """Um fator de escala por folha: altura mediana do normal / do endiabrado nos 8 desenhos-chave, entre 0,75 e 1,3.
    Um fator por quadro faria a respiração da ginga tremer. 'endiabrado' (as poses do fallback) mede a pose parada
    contra a ginga."""
    if desenhado() and (pasta in LOOPS or pasta in BOSS):
        return 1.0  # Lote 7: a escala do boss já vem certa do lote7_converter.py
    if pasta not in _FATOR:
        if pasta == "endiabrado":
            p = passo_do_loop("ginga_fluida")
            hn = [altura_corpo(quadro_loop("ginga_fluida", p * n)) for n in range(quadros_do_loop("ginga_fluida") // p)]
            endiabrados = [QUADROS / "endiabrado/00.png"]
        elif pasta in LOOPS and pasta != "ginga_fluida" and desenhado():
            # andar: os desenhos endiabrados usados são quase todos agachados e a mediana enganaria. A pose em pé do
            # andar (a mais alta) fica do tamanho da pose em pé da ginga endiabrada.
            # (a mais alta da FOLHA, a guarda em pé, mesmo quando o loop só usa as poses curvadas: senão o bote
            # era esticado até a altura da guarda e o corpo engordava 18% ao sair da ginga)
            alto = lambda p: max(altura_corpo(abrir_quadro(a))
                                 for a in sorted((QUADROS / LOOPS_ENDIABRADOS[p][0]).glob("*.png")))
            _FATOR[pasta] = fator_endiabrado("ginga_fluida") * alto("ginga_fluida") / alto(pasta)
            return _FATOR[pasta]
        elif pasta in LOOPS:
            p = passo_do_loop(pasta)
            hn = [altura_corpo(quadro_loop(pasta, p * n)) for n in range(quadros_do_loop(pasta) // p)]
            endiabrados = [arquivo_loop_endiabrado(pasta, p * n) for n in range(quadros_do_loop(pasta) // p)]
        else:
            outra, passo = pasta_endiabrada(pasta)
            normais = [pasta_da_folha(pasta) / f"{passo * n:02d}.png" for n in range(8)]
            endiabrados = [QUADROS / outra / f"{passo * n:02d}.png" for n in range(8)]
            hn = [altura_corpo(abrir_quadro(a)) for a in normais if a.exists()]
        he = [altura_corpo(abrir_quadro(a)) for a in endiabrados if a.exists()]
        _FATOR[pasta] = max(0.75, min(1.3, float(np.median(hn)) / float(np.median(he)))) if hn and he else 1.0
    return _FATOR[pasta]


def colar_endiabrado(normal, endiabrado, fator=1.0, dx=None):
    """Põe o desenho endiabrado no tamanho e no lugar do normal, num só paste: escala da folha (ancorada no chão e no
    tronco), pés na altura dos pés do normal quando o normal está no chão (até 12 px) e tronco no tronco do normal
    (dx dado pelos desenhos-chave ou, sem ele, medido aqui; até 24 px). normal=None só escala."""
    caixa = endiabrado.getchannel("A").getbbox()
    if caixa is None:
        return endiabrado
    figura = endiabrado.crop(caixa)
    cx = centro_tronco(endiabrado)
    cx = EIXO_X if cx is None else cx
    chao = EIXO_Y - 1
    x0, y0 = caixa[0], caixa[1]
    if abs(fator - 1) > 0.005:
        figura = figura.resize((max(1, round(figura.width * fator)), max(1, round(figura.height * fator))),
                               Image.Resampling.NEAREST)
        x0 = round(cx + (caixa[0] - cx) * fator)
        y0 = round(chao + 1 - (chao + 1 - caixa[3]) * fator) - figura.height
    dy = 0
    if normal is not None:
        bn, be = base_figura(normal), y0 + figura.height - 1
        if bn is not None and abs(bn - chao) <= 3:
            dy = max(-12, min(12, bn - be))
        if dx is None:
            a = centro_tronco(normal)
            dx = 0 if a is None else max(-24, min(24, round(a - cx)))
    tela = Image.new("RGBA", endiabrado.size)
    tela.paste(figura, (x0 + (dx or 0), y0 + dy), figura)
    gemeo = gemeo_endiabrado(endiabrado, caixa, figura.size, (x0 + (dx or 0), y0 + dy), tela)
    if gemeo is not None:
        GEMEOS_HD[id(tela)] = (tela, gemeo)
    return tela


# Gêmeos 3x montados junto com o desenho de 1x: {id(sprite de 1x): (sprite de 1x, sprite 3x)}. O hd.py acha o gêmeo
# comparando pixels com o quadro de quadros_hd/, e isso falha quando o colar_endiabrado reescala a figura pelo
# fator_endiabrado (Gutto: 442 de 474 sprites do despertado ficavam só ampliados e 3 ações piscavam entre 3x e 1x).
# Aqui o 3x passa pela MESMA conta (recorte, escala, lugar), em 3x; o hd.aplicar usa quando a comparação não acha.
GEMEOS_HD = {}
HD_E = 3


def gemeo_endiabrado(endiabrado, caixa, tamanho, lugar, tela):
    origem = getattr(endiabrado, "origem_quadro", None)
    if origem is None or QUADROS not in origem.parents:
        return None
    arq = QUADROS.parent / "quadros_hd" / origem.relative_to(QUADROS)
    if not arq.exists():
        return None
    hd = Image.open(arq).convert("RGBA")
    if hd.size != (endiabrado.width * HD_E, endiabrado.height * HD_E):
        return None
    E = HD_E
    fig = hd.crop(tuple(v * E for v in caixa))
    if fig.size != (tamanho[0] * E, tamanho[1] * E):
        fig = fig.resize((tamanho[0] * E, tamanho[1] * E), Image.Resampling.LANCZOS)
    g = Image.new("RGBA", (tela.width * E, tela.height * E))
    g.paste(fig, (lugar[0] * E, lugar[1] * E), fig)
    # o 3x só fica onde o 1x tem corpo (com 1 pixel de folga): o que o gerador apagou no 1x (retoque, cisco, borda
    # limpa) some também no 3x; o contorno continua o do desenho 3x, sem degrau
    a = np.array(g)
    corpo = np.asarray(tela)[..., 3] >= 128
    folga = np.zeros_like(corpo)
    folga[1:-1, 1:-1] = corpo[1:-1, 1:-1] | corpo[:-2, 1:-1] | corpo[2:, 1:-1] | corpo[1:-1, :-2] | corpo[1:-1, 2:]
    folga |= corpo
    a[..., 3] = np.where(np.repeat(np.repeat(folga, E, 0), E, 1) & (a[..., 3] >= 128), 255, 0).astype(np.uint8)
    return Image.fromarray(a)


def colar_boss(normal, boss):
    """Lote 7: põe o desenho do boss em cima do desenho normal que ele substitui. Os dois já estão na mesma escala e
    com a base no chão; aqui a base do boss vai para a base do normal e o corpo desliza em x até 30 px para o lugar em
    que as duas silhuetas mais se cobrem (pés e tronco no mesmo lugar, mesmo com o casaco e o cabelo sobrando)."""
    a = np.asarray(normal)[..., 3] >= 128
    b = np.asarray(boss)[..., 3] >= 128
    if not a.any() or not b.any():
        return boss
    dy = base_figura(normal) - base_figura(boss)
    b = np.roll(b, dy, axis=0)
    cobre = {dx: int((a & np.roll(b, dx, axis=1)).sum()) for dx in range(-30, 31)}
    melhor = max(cobre.values())
    dx = min((d for d, c in cobre.items() if c >= melhor * .99), key=abs)
    return move(boss, dx, dy)


def dx_chave(pasta, n):
    """dx do tronco medido só no desenho-chave n: os quadros do meio vêm entortados e enganam a medida."""
    if (pasta, n) not in _DX_CHAVE:
        if pasta == "ginga_fluida" and desenhado():
            # ginga: o pé da frente do endiabrado fica cravado no mesmo x em todos os desenhos, como no normal
            # (alinhado pelo tronco, os dois pés pulavam 20 a 38 px a cada desenho)
            e = abrir_quadro(arquivo_loop_endiabrado(pasta, n))
            alfa = np.asarray(e)[..., 3] >= 128
            base, cx, f = base_figura(e), centro_tronco(e), fator_endiabrado(pasta)
            chao = np.flatnonzero(alfa[base - 12:base + 1].any(axis=0))  # 12 px: no afundo o pé da frente pisa mais alto
            _DX_CHAVE[(pasta, n)] = round(PE_DA_FRENTE_ENDIABRADO - (cx + (int(chao[-1]) - cx) * f))
            return _DX_CHAVE[(pasta, n)]
        if pasta in LOOPS:
            a = centro_tronco(quadro_loop(pasta, passo_do_loop(pasta) * n))
            b = centro_tronco(abrir_quadro(arquivo_loop_endiabrado(pasta, passo_do_loop(pasta) * n)))
        else:
            outra, passo = pasta_endiabrada(pasta)
            a = centro_tronco(abrir_quadro(pasta_da_folha(pasta) / f"{passo * n:02d}.png"))
            b = centro_tronco(abrir_quadro(arquivo_endiabrado_da_chave(pasta, n)))
        _DX_CHAVE[(pasta, n)] = 0 if a is None or b is None else max(-24, min(24, round(a - b)))
    return _DX_CHAVE[(pasta, n)]


# Folhas normais do Pengaró que já saem da arte arcade (quadros_arcade/<folha>, só os 8 desenhos, sem quadros do meio).
# levanta: a folha antiga tinha duas caneleiras, braço terminando em pé e resto de magenta.
# 2026-11-11: os golpes também. O lutador trocava de cabelo, tom de pele e caneleira a cada golpe (ginga arcade de 16
# cores, golpe na arte antiga de milhares de cores e contorno mole). Só ficam na arte antiga as folhas sem desenho
# arcade aprovado: chute_baixo e defesa (a folha arcade é de outro golpe / outro modelo) e as que ainda não foram
# desenhadas (agarrao, armada, bola, caneta, compasso, derrota, golaco, lata, provoca, rolamento, vitoria, despertar).
ARCADE = {"levanta", "soco", "chute_alto", "martelo", "afastar", "apanha", "queda", "pulo", "agachado", "baixo_soco",
          "rasteirinha", "rasteira", "ar_soco", "bicicleta", "cabecada",
          # Lote 6 (2026-11-11): o resto da forma normal. Só despertar_a/b (a cena do Despertar) segue na arte antiga.
          "chute_baixo", "defesa", "bola", "compasso", "armada", "caneta", "rolamento", "agarrao", "golaco", "lata",
          "provoca", "vitoria", "derrota", "corre", "recuo"}
# Folha do gerador -> pasta em quadros_arcade/, quando o nome não é o mesmo. rasteira: a folha arcade da rasteira foi
# reprovada (duas garrafas, joelheira verde no lugar da caneleira); no lugar dela entra o chute rasteiro dado da base
# agachada (a folha que veio como "chute_baixo" e era outro golpe). O nome "rasteira" fica no gerador para os sprites
# f_rasteira<i>, as ações e os desenhos endiabrados (e_rasteira) não mudarem de número.
# Lote 6: a rasteira ganhou folha arcade própria (giro com as mãos no chão, como o golpe sempre foi); a pasta
# chute_agachado (o paliativo) ficou em disco, sem uso.
PASTA_ARCADE = {}
# Desenho arcade com defeito na origem, trocado por outro da MESMA folha: (folha, desenho) -> desenho.
# golaco 1: bebe com a mão da FRENTE e a de trás fica vazia; repete o 0 (gole com a mão de trás).
# vitoria 3 a 7: bebe com a mão da frente (3, 4, 5) e segura a garrafa no peito (6, 7). A comemoração fica nos três
# desenhos bons: ginga (0), garrafa subindo (1) e garrafa erguida (2), com um segundo brinde (1, 2) e a pose final no 2.
# bola 2 (retoque 2): os dois braços saem do ombro de trás (um ergue a lata, o outro segura a garrafa) e o ombro da
# frente fica sem braço; repete o 3 (o braço da lata já armado no alto), que é para onde o 2 ia.
REPETE_ARCADE = {}  # desenhos do padrão novo (2026-11-13, folhas_novas): os defeitos antigos não existem mais
# Forma endiabrada das folhas novas que não têm e_<folha>: empresta o desenho endiabrado que a ação já usava
# (correr = andar endiabrado; recuo = e_defesa 6), para o Despertar não mudar.
ENDIABRADO_EMPRESTADO = {"corre": lambda i: ("anda_fluida", (0, 1, 2, 2, 3, 4, 5, 5)[i]), "recuo": lambda i: ("pulo", 3) if i >= 2 else ("defesa", 6)}  # Lote 7: no ar, o boss encolhido do pulo
# Desenho arcade deslocado em x (px). afastar 6: o pé de apoio (o de trás, plantado em x=-41 no 5 e -39 no 7) aparecia
# em -29: o corpo dava um tranco para a frente e voltava.
DESLOCA_ARCADE = {}  # padrão novo (2026-11-13)


# Golpes de pengaro_extra.py com desenho trocado no Pengaró arcade: estado -> {elemento (de 0): (folha, desenho)}.
# 322 e 342 (rasteirinha do combo): o contato era o desenho 4, que troca a pose do braço (DESENHO_PROIBIDO); fica no 3,
# como no 430. 1701 (rolê por trás e chute): os 15 ticks do rolê eram um desenho da folha antiga (rolamento, sem
# folha arcade) e o chute era arcade; o rolê passa a ser a bola no chão da levantada arcade (levanta 2). É um desenho
# só porque a regra da pose segurada (seco) já mostrava um só: a antecipação inteira fica no penúltimo desenho.
# (Lote 6: o rolamento tem folha arcade e o 1701 voltou a usar os desenhos dele; o improviso com levanta 2 saiu.)
DESENHOS_ARCADE_DO_GOLPE = {
    322: {3: ("rasteirinha", 3)}, 342: {3: ("rasteirinha", 3)},
}
# Clsn1 do golpe no Pengaró arcade, quando o membro do desenho novo não fica onde a caixa do golpe antigo estava.
# 322/342: o pé passa em x 76, y -24..-16 (a caixa estava embaixo da canela, 22 px atrás do pé). 601: a mão da frente
# está em y -39..-24, abaixo da caixa (12,-76,56,-40).
# 1500/1501 (Lote 6): a caixa do pisão (8,-37,64,-2) ficava abaixo da perna do chute_baixo arcade, que bate na altura
# da barriga; sem pixel do membro na faixa dela, o contato segurado caía no desenho da perna já dobrada (5) e o alcance
# encolhia para 23. Sobe para a perna; o golpe continua sendo defendido embaixo (guarda L do repertório).
CAIXA_ARCADE = {322: (12, -26, 78, -10), 342: (12, -26, 78, -10), 601: (12, -76, 56, -24),
                1500: (8, -68, 60, -44), 1501: (8, -68, 60, -44)}
# Clsn1 da variante despertada (1xxxx) quando o desenho endiabrado bate em outra altura: (ação normal) -> caixa.
# 240: o chute endiabrado é mais alto (pé em x 61, y -114..-101); a caixa herdada ficava embaixo do pé, 19 px atrás.
# 230, 1500, 1501 (retoque 2 do Lote 6): o chute endiabrado (e_chute_baixo 3) também bate na altura da barriga (perna em
# y -78..-60, pé em x 58). A caixa antiga ficava abaixo da perna: 0 pixel do desenho dentro dela no pisão (11500/11501,
# alcance 20) e 20 px aquém do pé no 10230. Fica na perna, com o recuo de 8 px que toda variante despertada tem.
CAIXA_DESPERTADA_ANTIGA = {240: (20, -116, 72, -58), 230: (20, -78, 54, -58), 1500: (16, -78, 52, -58),
                    1501: (16, -78, 52, -58)}
# Lote 7: o boss bate com o mesmo desenho do normal (mesma pose, mesmo alcance); a caixa despertada volta a ser a do
# normal com o recuo de 8 px, e o ajustar_clsn1 a encurta até o membro.
CAIXA_DESPERTADA = {}


# Lote 7 (2026-11-11): folhas do Endiabrado (boss final, conceito e_conceito.png) na arte arcade, em
# quadros_arcade/e_<folha>/00..07.png (ferramentas/retoques_arcade/lote7_converter.py). Seguem a folha normal desenho a
# desenho; o RemapPreset troca cada desenho normal pelo do boss com colar_boss. Não têm quadro do meio.
BOSS = {"afastar", "agachado", "agarrao", "apanha", "ar_soco", "armada", "baixo_soco", "bicicleta", "bola", "cabecada",
        "caneta", "chute_alto", "chute_baixo", "compasso", "defesa", "derrota", "golaco", "lata", "levanta", "martelo",
        "provoca", "pulo", "queda", "rasteira", "rasteirinha", "rolamento", "soco", "vitoria"}
# Desenho do boss com defeito na origem, trocado por outro da mesma folha: (folha normal, desenho) -> desenho.
TROCA_BOSS = {}
# Sprite antigo sem folha (os das 9 poses que nenhuma TROCA_POR_FOLHA cobre): pose de POSES_ENDIABRADO -> desenho do boss.
POSE_BOSS = {0: ("ginga_fluida", 0), 1: ("anda_fluida", 0), 2: ("agachado", 0), 3: ("soco", 5), 4: ("chute_alto", 4),
             5: ("cabecada", 4), 6: ("bola", 4), 7: ("pulo", 3)}


def pasta_da_folha(folha):
    if desenhado() and folha in ARCADE:
        return QUADROS_ARCADE / PASTA_ARCADE.get(folha, folha)
    return QUADROS / folha


def quadro_folha(folha, i):
    if folha in LOOPS:
        return quadro_loop(folha, i)
    if desenhado() and folha == "despertar_b":
        # Lote 7: a segunda metade da cena do Despertar é a folha e_despertar (o Pengaró de mãos vazias cai de joelhos,
        # a roupa do boss aparece e ele se levanta na guarda). O nome f_despertar_b<i> ficou para os números não mudarem.
        return abrir_quadro(QUADROS_ARCADE / "e_despertar" / f"{i:02d}.png")
    if desenhado() and folha in ARCADE:
        i = REPETE_ARCADE.get((folha, i), i)
    arquivo = pasta_da_folha(folha) / f"{i:02d}.png"
    if not arquivo.exists():
        return None
    img = abrir_quadro(arquivo)
    if desenhado() and folha in ARCADE and (folha, i) in DESLOCA_ARCADE:
        img = move(img, DESLOCA_ARCADE[(folha, i)])
    return img


def desenho_de(nome):
    """(folha, desenho) de um sprite que tem quadros do meio, ou None."""
    if nome in TROCA_POR_FOLHA:
        return TROCA_POR_FOLHA[nome]
    m = re.fullmatch(r"(?:f_|q_)([a-z_]+?)(\d+)", nome)
    return (m[1], int(m[2])) if m and ((QUADROS / m[1] / "meio").exists() or desenhado() and m[1] in ARCADE) else None


# Último desenho que cada folha pode mostrar: no golaço, do 5º em diante a chuva está desenhada no corpo.
ULTIMO_DESENHO = {"golaco": 4}
# Para onde o último elemento de uma ação caminha (a ação que vem depois, ou o começo dela mesma se ela repete).
# Sem isso o último elemento seguiria até o desenho 7 da folha, que não é para onde a ação vai.
SEGUINTE = {10: "f_agachado4", 11: "f_agachado4", 40: "f_pulo1", 120: "f_defesa3", 130: "f_defesa3"}


# Intervalos (folha, desenho) em que o quadro do meio NÃO é usado no Pengaró: os dois desenhos são poses distantes
# (a garrafa muda de mão, o braço troca) e a malha do Blender derrete cabeça, tronco ou garrafa. Vira corte seco.
MEIO_PROIBIDO = {("vitoria", 2), ("vitoria", 5), ("despertar_a", 0), ("despertar_a", 4),
                 ("provoca", 1), ("provoca", 2), ("provoca", 3), ("defesa", 1), ("defesa", 2),
                 ("lata", 0), ("lata", 1),
                 *(("despertar_b", i) for i in range(7))}  # Lote 7: e_despertar não tem quadro do meio
# Desenhos que não entram no caminho entre dois outros. lata 1 (abrir o lacre): uma mão segura a garrafa, outra a
# lata e uma TERCEIRA abre o lacre. A lata já está aberta na mão e ele vai direto para o gole.
# rasteirinha 4 (arcade): no contato a mão da frente sai do chão e vira punho no peito, e no 5 volta ao chão; o
# contato fica no desenho 3 (perna esticada, mão no chão).
DESENHO_PROIBIDO = {("lata", 1), ("rasteirinha", 4)}
# Desenhos endiabrados errados na origem, trocados pelo vizinho bom da mesma folha: (folha normal, desenho) -> desenho
# de e_<folha>. e_levanta 3 e 4: parada de mão com pés no lugar das mãos. e_rolamento 4: massa ilegível.
# e_baixo_soco 2 e e_rasteira 1-2: pose de outra família no meio da folha.
TROCA_ENDIABRADA = {("levanta", 3): 2, ("levanta", 4): 5, ("rolamento", 4): 3, ("baixo_soco", 2): 1,
                    ("rasteira", 1): 0, ("rasteira", 2): 3}


def arquivo_endiabrado_da_chave(pasta, n):
    if desenhado() and pasta in BOSS:
        return QUADROS_ARCADE / f"e_{pasta}" / f"{TROCA_BOSS.get((pasta, n), n):02d}.png"
    if desenhado():
        n = TROCA_ENDIABRADA.get((pasta, n), n)
    return QUADROS / f"e_{pasta}" / f"{n:02d}.png"


def registra_meio(s, folha, intervalo, k):
    """Quadro do meio `k` entre os desenhos `intervalo` e `intervalo + 1`, já no sprite do jogo; None se não existe."""
    arquivo = pasta_da_folha(folha) / "meio" / f"{intervalo:02d}_{k}.png"
    if not arquivo.exists() or desenhado() and (folha, intervalo) in MEIO_PROIBIDO:
        return None
    nome = f"m_{folha}_{intervalo:02d}_{k}"
    if nome not in s.codigos:
        s.add(nome, pe_no_chao(abrir_quadro(arquivo), folha, intervalo, k))
    return nome


def vai_e_volta(s, sprite, ticks):
    """Desenho parado por mais de 2 ticks (regra 7) vira um vai-e-volta de 2 ticks com os quadros do meio ao lado dele.
    Do desenho 0 ao 6, usa os 3 primeiros quadros do meio entre ele e o seguinte; o desenho 7 (a cauda parada do fim da
    folha) usa os 3 últimos do meio entre o 6 e ele. Devolve [(sprite, ticks)] ou None se a folha não tem os quadros."""
    d = desenho_de(sprite)
    if not d:
        return None
    folha, n = d
    if n < 7:
        intervalo, ks = n, (1, 2, 3)
    elif folha in FOLHAS:
        intervalo, ks = 6, (6, 5, 4)
    else:
        return None
    meios = [registra_meio(s, folha, intervalo, k) for k in ks]
    if None in meios:
        return None
    ciclo = [sprite, *meios, *meios[-2::-1]]
    saida, resto, i = [], ticks, 0
    while resto > 0:
        t = min(2, resto)
        saida.append((ciclo[i % len(ciclo)], t))
        resto -= t
        i += 1
    return saida


def fim_da_folha(nome):
    """No último elemento de um golpe, a recuperação segue até o último desenho da folha em vez de ficar parada."""
    desenho = desenho_de(nome) if nome.startswith(("f_", "q_soco")) else None
    if desenho and desenho[0] in ULTIMO_DESENHO and desenho[1] >= ULTIMO_DESENHO[desenho[0]]:
        return None
    return f"f_{desenho[0]}7" if desenho and desenho[0] in FOLHAS and desenho[1] < 7 else None


def par_endiabrado(nome):
    """(arquivo endiabrado, pasta normal, posição em desenhos-chave) de um sprite do Pengaró, ou None se a folha não
    tem versão endiabrada. A posição é fracionária nos quadros do meio e nos loops (m_soco_03_2 fica em 3 + 2/7)."""
    meio = re.fullmatch(r"m_([a-z_]+?)_(\d+)_(\d+)", nome)
    if meio and desenhado():
        # No Pengaró a forma endiabrada não usa quadro do meio: os das folhas e_* vieram furados (olho e relevo
        # apagados) e com cabeça e pernas esticadas pela malha. Cada um vira o desenho-chave mais próximo.
        n = int(meio[2]) + (1 if int(meio[3]) >= 4 else 0)
        return arquivo_endiabrado_da_chave(meio[1], n), meio[1], n
    if meio:
        return QUADROS / f"e_{meio[1]}/meio/{meio[2]}_{meio[3]}.png", meio[1], int(meio[2]) + int(meio[3]) / 7
    fluido = re.fullmatch(r"q_(ginga|anda)_fluida(\d+)", nome)
    if fluido:
        pasta = f"{fluido[1]}_fluida"
        return arquivo_loop_endiabrado(pasta, int(fluido[2])), pasta, int(fluido[2]) / passo_do_loop(pasta)
    desenho = desenho_de(nome)
    if not desenho:
        return None
    if desenhado() and desenho[0] in ENDIABRADO_EMPRESTADO:
        desenho = ENDIABRADO_EMPRESTADO[desenho[0]](desenho[1])
    if desenho[0] in LOOPS:
        return arquivo_loop_endiabrado(desenho[0], desenho[1]), desenho[0], desenho[1] / passo_do_loop(desenho[0])
    outra, passo = pasta_endiabrada(desenho[0])
    return arquivo_endiabrado_da_chave(desenho[0], desenho[1]), desenho[0], desenho[1] / passo


def arquivo_endiabrado(nome):
    """Desenho endiabrado equivalente a um sprite do Pengaró, ou None se a folha não tem versão endiabrada."""
    par = par_endiabrado(nome)
    return par[0] if par else None


SEM_FOLHA_BOSS = []  # sprites do jogo que caíram numa pose emprestada do boss (para o relatório do gerador)


def preset_despertado(s):
    """[RemapPreset despertado]: no Despertar, cada desenho do Pengaró vira o endiabrado, em qualquer animação.
    Sprite antigo sem folha endiabrada (corrida, tontura) cai numa pose parada, para a garrafa nunca aparecer."""
    pose = {nome: i for i, nomes in POSES_ENDIABRADO.items() for nome in nomes}
    linhas = ["[RemapPreset despertado]"]
    normais = {(gr, ind): img for gr, ind, img, _, _ in s.lista}
    for nome, (grupo, indice) in list(s.codigos.items()):
        if nome.startswith(("balao_", "fx_", "bola", "bolao", "quica", "retrato", "chuva", "ginga_endiabrada",
                            "endiabrado_", "despertado_", "e_")) or grupo >= 9000:
            continue
        par = par_endiabrado(nome)
        destino = f"e_{nome}"
        normal = normais[(grupo, indice)]
        if par and par[0].exists():
            arquivo, pasta, pos = par
            n = int(pos)
            seguinte = (n + 1) % (quadros_do_loop(pasta) // passo_do_loop(pasta)) if pasta in LOOPS else min(7, n + 1)
            if eh_boss(arquivo):
                s.add(destino, colar_boss(normal, abrir_quadro(arquivo)))
            else:
                dx = round(dx_chave(pasta, n) + (dx_chave(pasta, seguinte) - dx_chave(pasta, n)) * (pos - n))
                s.add(destino, colar_endiabrado(normal, abrir_quadro(arquivo), fator_endiabrado(pasta), dx))
        elif nome.startswith(("m_despertar", "f_despertar", "f_lata", "m_lata")):
            continue
        elif desenhado():  # Lote 7: sem folha, cai numa pose do boss (a arte antiga de quadros/endiabrado saiu do jogo)
            folha, n = POSE_BOSS[pose.get(nome, 0)]
            arquivo = arquivo_loop_endiabrado(folha, n) if folha in LOOPS else arquivo_endiabrado_da_chave(folha, n)
            SEM_FOLHA_BOSS.append(nome)
            s.add(destino, colar_boss(normal, abrir_quadro(arquivo)))
        else:
            s.add(destino, colar_endiabrado(normal, abrir_quadro(QUADROS / f"endiabrado/{pose.get(nome, 0):02d}.png"),
                                            fator_endiabrado("endiabrado")))
        g, i = s.codigos[destino]
        linhas.append(f"{grupo},{indice} = {g},{i}")
    for nome, (grupo, indice) in s.codigos.items():  # faíscas: whisky no normal, sombra no Despertar
        if nome.startswith("fx_") and f"d{nome}" in s.codigos:
            g, i = s.codigos[f"d{nome}"]
            linhas.append(f"{grupo},{indice} = {g},{i}")
    return "\n".join(linhas) + "\n\n"


# Lote 7: a aura antiga do boss (fx_aura_anel, fx_aura_coluna e fx_aura_detritos nas ações 9211, 9210 e 9218) não
# nasce mais no jogo: a aura do endiabrado é a do Blender (a aura grande, que o Breno quer de volta no
# Despertar, 2026-11-13), ligada por ferramentas/aura_pengaro.py ([Statedef -4], Explods 9600 a 9603). Os desenhos antigos seguem carregados só porque entram na escolha da paleta do .sff: tirá-los
# da lista mudaria as 255 cores e todos os pixels da forma base. As ações deles NÃO vão para o .air: a paleta sai
# antes da poda (escrever_sff), então a poda tira os 24 desenhos do .sff e a paleta não muda.
AURA_BOSS = {9211: "aura_anel", 9210: "aura_coluna", 9218: "aura_detritos"}


def sem_tinta_do_despertar(cns):
    """Lote 7: o PalFX que somava violeta ao corpo do Endiabrado (recoloração do desenho antigo) sai: o boss já vem
    pintado na paleta dele, e a aura é efeito à parte."""
    bloco = re.compile(r"\[State -2, Aura\]\ntype = PalFX\n(?:[^\n]+\n)+\n")
    cns, n = bloco.subn("", cns)
    assert n == 1, "PalFX da aura não encontrado"
    return cns


# ações que já têm o próprio Impacto/Estouro (9205/9235) ou não são golpe de membro: sem rastro por cima
SEM_RASTRO = {760, 800, 830, 840, 1500, 1501, 3403}


def efeitos_cns(ativos, fracos=frozenset()):
    """[Statedef -3] com o rastro que acompanha cada golpe médio para cima, que nasce no elemento em que a caixa de
    golpe liga, na ponta da caixa (onde está o punho ou o pé). Golpe fraco não ganha rastro: errar não parece acerto."""
    t = ["[Statedef -3]\n"]
    for anim, (elemento, caixa) in sorted(ativos.items()):
        base = anim - 10000 if anim >= 10000 else anim
        if not 200 <= base < 4000 or base == 2000 or base in SEM_RASTRO or base in fracos:
            continue
        x1, y1, x2, y2 = caixa
        aereo = 600 <= base < 700
        chao = max(y1, y2) >= -25 and abs(y2 - y1) <= 30 and not aereo  # rasteira: poeira no chão
        x = max(x1, x2) - 8
        pos = f"{x}, 0" if chao else f"{x}, {(y1 + y2) // 2}"
        # Alguns golpes do endiabrado usam a ação normal com os sprites trocados: a forma decide pelo var(20).
        if anim >= 10000:
            formas = [(True, "var(20) > 0")]
        elif anim + 10000 in ativos:
            formas = [(False, "var(20) <= 0")]
        else:
            formas = [(False, "var(20) <= 0"), (True, "var(20) > 0")]
        for endiabrado, forma in formas:
            efeito = (9215 if endiabrado else 9214) if chao else (9212 if endiabrado else 9213)
            t.append(f"[State -3, Efeito do golpe {anim}]\ntype = Explod\n"
                     f"trigger1 = Anim = {anim} && AnimElem = {elemento} && {forma}\n"
                     f"anim = {efeito}\npostype = p1\npos = {pos}\nbindtime = 3\nremovetime = 8\nsprpriority = 3\n"
                     f"ownpal = 1\nscale = .75, .75\nignorehitpause = 1\n\n")
    return "".join(t)


def caminho_fluido(s, atual, proximo):
    """Sprites para ir de um desenho até o seguinte, sem incluir o seguinte. Registra só os quadros do meio usados."""
    de, para = desenho_de(atual), desenho_de(proximo) if proximo else None
    # Desenhos distantes são cortes de propósito: atravessar tudo no meio faz o corpo se debater.
    if not de or not para or de[0] != para[0] or de[1] == para[1] or abs(para[1] - de[1]) > 3:
        return [atual]
    folha = de[0]
    if folha in ULTIMO_DESENHO and max(de[1], para[1]) > ULTIMO_DESENHO[folha]:
        return [atual]
    passo = 1 if para[1] > de[1] else -1
    caminho = []
    for i in range(de[1], para[1], passo):
        if i == de[1] or not (desenhado() and (folha, i) in DESENHO_PROIBIDO):
            caminho.append(atual if i == de[1] else f"f_{folha}{i}")
        intervalo = min(i, i + passo)
        arquivos = sorted((pasta_da_folha(folha) / "meio").glob(f"{intervalo:02d}_*.png"),
                          key=lambda a: int(a.stem.split("_")[1]), reverse=passo < 0)
        if desenhado() and (folha, intervalo) in MEIO_PROIBIDO:
            arquivos = []  # corte seco: aqui o quadro do meio derrete
        for arquivo in arquivos:
            caminho.append(registra_meio(s, folha, intervalo, int(arquivo.stem.split("_")[1])))
    return caminho


# Trechos de folha desenhados no ar (folha, primeiro desenho, último desenho): ali o pé não precisa tocar o chão.
DESENHOS_NO_AR = (("bicicleta", 0, 7), ("ar_soco", 0, 7), ("pulo", 1, 6), ("armada", 3, 5))
_BASE_CHAVE = {}


def pe_no_chao(img, folha, n, k):
    """Quadro do meio entre os desenhos n e n+1: o Blender às vezes afunda ou levanta o pé alguns pixels. Se as duas
    chaves estão no chão, a base vai para a reta entre as bases delas (até 10 px, só em y)."""
    if any(f == folha and (a <= n <= b or a <= n + 1 <= b) for f, a, b in DESENHOS_NO_AR):
        return img
    for j in (n, n + 1):
        if (folha, j) not in _BASE_CHAVE:
            _BASE_CHAVE[(folha, j)] = base_figura(abrir_quadro(pasta_da_folha(folha) / f"{j:02d}.png"))
    bases = [_BASE_CHAVE[(folha, n)], _BASE_CHAVE[(folha, n + 1)]]
    base = base_figura(img)
    if base is None or None in bases or any(abs(b - (EIXO_Y - 1)) > 3 for b in bases):
        return img
    alvo = round(bases[0] + (bases[1] - bases[0]) * k / 7)
    dy = max(-10, min(10, alvo - base))
    if abs(alvo - base) <= 3 or not dy:
        return img
    tela = Image.new("RGBA", img.size)
    tela.paste(img, (0, dy), img)
    return tela


def ajustar_sparkxy(cns, ativos):
    """A faísca nasce na altura da caixa de golpe ativa do estado (golpe baixo faísca rente ao chão), não em -70."""
    def troca(m):
        n = int(m[2])
        caixa = ativos.get(n, ativos.get(n + 10000, (None, None)))[1]
        if not caixa:
            return m[0]
        y = max(-95, min(-10, (caixa[1] + caixa[3]) // 2))
        return f"{m[1]}sparkxy = -10, {y}"
    return re.sub(r"(\[State (\d+), Golpe\]\n(?:[^\n]+\n)*?)sparkxy = -10, -70", troca, cns)


def remapear_animelem(cns, mapas):
    """O .cns conta elementos da animação; os quadros do meio mudam essa contagem."""
    linhas = cns.split("\n")
    acao, cabecalho = None, False
    for n, linha in enumerate(linhas):
        estado = re.match(r"\[Statedef (-?\d+)\]", linha)
        if estado:
            acao, cabecalho = int(estado[1]), True
        elif linha.startswith("[State "):
            cabecalho = False
        elif cabecalho and (troca := re.match(r"anim = (\d+)$", linha)):
            acao = int(troca[1])
        mapa = mapas.get(acao)
        if mapa and "AnimElem" in linha:
            novo = lambda m: m[1] + str(mapa[int(m[2]) - 1] if int(m[2]) <= len(mapa) else m[2]) + m[3]
            linhas[n] = re.sub(r"(AnimElem\s*=\s*)(\d+)()", novo, re.sub(r"(AnimElemTime\()(\d+)(\))", novo, linha))
    return "\n".join(linhas)


def sprites_folhas(s):
    """Registra cada quadro das folhas como f_<folha><i>."""
    for folha in FOLHAS:
        for i in range(8):
            img = quadro_folha(folha, i)
            if img is not None:
                s.add(f"f_{folha}{i}", img)


def acoes_folhas(Q):
    """Ações do Pengaró com a sequência inteira desenhada. Vêm antes das antigas, que então são ignoradas.
    Quantidade de quadros e tempos seguem os golpes antigos onde o .cns depende de AnimElem."""
    f = lambda folha, i: f"f_{folha}{i}"
    arcade = desenhado()  # Pengaró: golpes na arte arcade (ARCADE); Gutto e Raiclaven seguem como estavam
    Q(5, [("q_ginga_fluida0", 6)] if desenhado() else [(f"q_ginga_fluida{i}", 2) for i in range(3)])  # virar
    Q(6, [(f("agachado", 4), 3), (f("agachado", 5), 3)], BAIXO)
    # correr: os mesmos desenhos do andar, sem o "peso desce", em menos da metade do tempo
    # Pengaró (Lote 6): corrida com desenho próprio, os 8 da folha corre a 2 ticks (ciclo de 16; era o andar em 15).
    Q(100, [(f("corre", i), 2) for i in range(8)] if desenhado() else
      [(f"q_anda_fluida{i}", 1) for i in range(0, quadros_do_loop("anda_fluida"), 3)])
    if desenhado():  # recuo (pulinho para trás): sai do chão (2) e fica encolhido no ar (3); era a defesa inclinada
        Q(105, [(f("recuo", 2), 3), (f("recuo", 3), -1)], NO_AR)
    # em pé <-> agachado: troca seca de 2 ticks com um desenho só (eram 6 e 4; o estado já é C desde o tick 0)
    # Pengaró redesenhado (folha de 2026-11-13): a folha agachado é a descida inteira (0 em pé, 1-2 descendo, 3-5 no
    # fundo, 6-7 subindo); a troca usa o 2 (meio da descida) e a base agachada respira só entre 4 e 5, os dois mais
    # baixos, sem o boneco subir até o 7 (meio em pé) no meio do agachado.
    Q(10, [(f("agachado", 2), 2)], BAIXO)
    Q(11, [(f("agachado", i), 10) for i in (4, 5)], BAIXO)
    Q(12, [(f("agachado", 2), 2)], BAIXO)
    Q(40, [(f("pulo", 0), 4)])
    for n in (41, 42, 43):
        Q(n, [(f("pulo", 1), 3), (f("pulo", 2), 5), (f("pulo", 3), 6), (f("pulo", 4), -1)], NO_AR)
    for n in (44, 45, 46):
        Q(n, [(f("pulo", 4), 6), (f("pulo", 5), 6), (f("pulo", 6), -1)], NO_AR)
    Q(47, [(f("pulo", 6), 2), (f("pulo", 7), 3)])
    # no desenho 2 da defesa a garrafa aparece do outro lado dos braços cruzados: o Pengaró entra direto no 3
    d2 = 3 if desenhado() else 2
    Q(120, [(f("defesa", 1), 2), (f("defesa", d2), 2)])
    Q(130, [(f("defesa", 3), 10), (f("defesa", 4), 10)])
    Q(140, [(f("defesa", d2), 2), (f("defesa", 1), 2)])
    Q(150, [(f("defesa", 5), 3), (f("defesa", 6), 3), (f("defesa", 7), -1)])
    # (Lote 6: a derrota arcade vai até o 7, cabeça baixa; o corte no 6 era por um punho solto no 7 da folha antiga.)
    Q(170, [(f("derrota", i), 6) for i in range(7)] + [(f("derrota", 7), -1)])
    Q(181, [(f("vitoria", i), 6) for i in range(7)] + [(f("vitoria", 7), -1)])
    Q(195, [(f("provoca", i), 7) for i in range(8)])
    # o 1º elemento é o que congela no shaketime: já é a pose do tranco, maior quanto mais forte o golpe
    leve = [(f("apanha", 2), 4), (f("apanha", 3), 3), (f("apanha", 1), 6)]
    medio = [(f("apanha", 3), 4), (f("apanha", 4), 5), (f("apanha", 5), 5), (f("apanha", 1), 3)]
    pesado = [(f("apanha", 4), 6), (f("apanha", 5), 5), (f("apanha", 3), 4), (f("apanha", 1), 2)]
    for base in (5000, 5010):
        for n, q in ((0, leve), (1, medio), (2, pesado)):
            Q(base + n, q)
            Q(base + 5 + n, [(f("apanha", 6), 4), (f("apanha", 7), 4)])
    Q(5050, [(f("queda", 1), 5), (f("queda", 2), 5), (f("queda", 3), -1)], NO_AR)
    Q(5100, [(f("queda", 4), 3), (f("queda", 5), 3), (f("queda", 6), 3)], DEITADO)
    Q(5101, [(f("queda", 5), 3), (f("queda", 6), 3)], DEITADO)
    Q(5110, [(f("queda", 7), -1)], DEITADO)
    Q(5160, [(f("queda", 6), 6), (f("queda", 7), -1)], DEITADO)
    Q(5170, [(f("queda", 6), 6), (f("queda", 7), 10)], DEITADO)  # 5170 (bateu no chão) tem de ACABAR: o 5110 do motor só manda o nocauteado para o 5150 quando AnimTime = 0;
    # com -1 no fim o motor esperava 900 ticks (over.forcewintime) para mostrar a vitória.
    Q(5120, [(f("levanta", i), 4) for i in range(1, 8)], ROLANDO)
    for n, t in ((700, 4), (5200, 3), (5210, 3)):
        Q(n, [(f("rolamento", i), t) for i in range(8)], ROLANDO if n == 700 else [])
    Q(705, [(f("rolamento", i), 4) for i in range(7, -1, -1)], ROLANDO)

    def sequencia(n, folha, lig, ativo, rec, caixa, quadro_ativo=3, area=CORPO):
        """Liga, golpe e volta com os 8 desenhos, no mesmo tempo total do golpe antigo."""
        a = quadro_ativo
        pre = list(range(1, a))
        pos = list(range(a + 2, 8))
        q = [(f(folha, i), max(1, lig // len(pre)) + (lig % len(pre) if j == 0 else 0)) for j, i in enumerate(pre)]
        q += [(f(folha, a), 1, caixa), (f(folha, a + 1), max(1, ativo - 1), caixa)]
        q += [(f(folha, i), max(1, rec // len(pos)) + (rec % len(pos) if j == 0 else 0)) for j, i in enumerate(pos)]
        Q(n, q, area)

    # chute_baixo arcade (Lote 6): chute de sola na altura da barriga; a perna passa em y de -64 a -48 e o pé vai até
    # x 70. A caixa antiga (12,-56,58,-42) ficava metade abaixo da perna.
    sequencia(230, "chute_baixo", 5, 3, 9, (12, -66, 62, -46) if arcade else (12, -56, 58, -42))
    if arcade:
        # chute alto arcade: os desenhos 4 e 5 são os dois de perna esticada. O 5 abria a volta com 6 ticks sem caixa:
        # fica com 2 e o resto vai para o joelho recolhendo (6) e o pé no chão (7). Mesmo total (18), mesmos elementos.
        cx = (12, -100, 80, -58)
        Q(240, [(f("chute_alto", 1), 5), (f("chute_alto", 2), 4), (f("chute_alto", 3), 1, cx),
                (f("chute_alto", 4), 3, cx), (f("chute_alto", 5), 2), (f("chute_alto", 6), 8), (f("chute_alto", 7), 8)])
        # cotovelada arcade: o desenho 3 ainda é a armação (cotovelo junto do rosto) e o contato é o 4. Mesmos tempos e
        # a mesma quantidade de elementos (2 + 2 + 3) de sequencia(): o .cns usa AnimElem.
        for n, t, cx in ((210, (4, 3, 1, 3, 6, 5, 5), (15, -92, 78, -64)), (215, (2, 2, 1, 2, 6, 4, 4), (12, -94, 66, -62))):
            Q(n, [(f("martelo", d), tk, cx) if d == 4 else (f("martelo", d), tk)
                  for d, tk in zip((2, 3, 4, 4, 5, 6, 7), t)])
    sequencia(240, "chute_alto", 9, 4, 18, (12, -100, 80, -58))
    # capoeira: cotovelada no soco forte, bênção no chute longo
    sequencia(210, "martelo", 7, 4, 16, (15, -92, 78, -64))
    sequencia(215, "martelo", 4, 3, 14, (12, -94, 66, -62))
    sequencia(245, "chute_baixo", 5, 3, 16, (10, -76, 50, -50))
    sequencia(260, "afastar", 12, 4, 20, (15, -100, 75, -60))
    giro = (-40, -80, 90, -20)
    for i in (0, 1):
        Q(1100 + i, [(f("compasso", 1), 8)] + [(f("compasso", j), 4, giro) for j in (2, 3, 4, 5)]
          + [(f("compasso", 7), 14 + 6 * i)])
        Q(1200 + i, [(f("armada", 2), 4), (f("armada", 4), 6, (0, -130, 60 + 8 * i, -30)), (f("armada", 5), 8),
                     (f("armada", 6), -1)], NO_AR)
        Q(1300 + i, [(f("caneta", 2), 10), (f("caneta", 4), 8, (10, -20, 70, -4)), (f("caneta", 7), 20 + 6 * i)], ROLANDO)
    # (no arcade o punho do soco agachado fica 10 px mais alto: y de -66 a -55; o alcance é o mesmo)
    sequencia(400, "baixo_soco", 4, 3, 7, (15, -66, 54, -52) if arcade else (15, -56, 54, -42), quadro_ativo=4,
              area=BAIXO)
    sequencia(410, "cabecada", 6, 5, 18, (5, -122, 42, -60), area=BAIXO)
    if arcade:
        # rasteirinha arcade: o desenho 3 segura o contato (o 4 troca a pose do braço, veja DESENHO_PROIBIDO); o pé
        # passa 8 px mais alto (y de -24 a -14). Mesmos 7 elementos e tempos de sequencia(430, ..., 5, 3, 10).
        # A caixa vai até o pé (x 76): com 62 o pé passava 14 px além dela.
        cx = (12, -26, 78, -10)
        Q(430, [(f("rasteirinha", 1), 3), (f("rasteirinha", 2), 2), (f("rasteirinha", 3), 1, cx),
                (f("rasteirinha", 3), 2, cx), (f("rasteirinha", 5), 4), (f("rasteirinha", 6), 3),
                (f("rasteirinha", 7), 3)], BAIXO)
        # (440: a rasteira arcade do Lote 6 segue os índices da sequencia() abaixo, sem ação escrita à mão.)
    sequencia(430, "rasteirinha", 5, 3, 10, (12, -18, 62, -4), area=BAIXO)
    sequencia(440, "rasteira", 10, 4, 22, (12, -18, 78, -2), area=BAIXO)
    Q(600, [(f("ar_soco", 2), 2), (f("ar_soco", 3), 3), (f("ar_soco", 4), 8, (8, -86, 50, -46 if arcade else -62)),
            (f("ar_soco", 6), -1)], NO_AR)
    Q(650, [(f("bicicleta", 2), 3), (f("bicicleta", 3), 4), (f("bicicleta", 4), 6, (6, -70, 70, -20)),
            (f("bicicleta", 6), -1)], NO_AR)
    Q(810, [(f("agarrao", i), 4) for i in range(2, 7)] + [(f("agarrao", 7), 10)])
    # golpes do repertório (repertorio.py, o Hazaki também usa): no Pengaró cada um fica com os desenhos de uma folha só
    # (antes eram poses soltas de folhas diferentes, com corte seco entre elas). Mesmos tempos, mesma caixa, mesma
    # quantidade de elementos: o CNS liga o golpe e o avanço por AnimElem.
    folha_do_golpe = {216: ("martelo", (1, 4, 6)), 201: ("soco", (1, 4, 6)), 231: ("chute_baixo", (1, 4, 6)),
                      246: ("chute_alto", (1, 4, 6)), 601: ("ar_soco", (1, 4, 6)), 611: ("bicicleta", (1, 4, 6)),
                      1400: ("martelo", (1, 4, 6)), 1401: ("martelo", (1, 4, 6)),
                      1500: ("chute_baixo", (2, 4, 6)), 1501: ("chute_baixo", (2, 4, 6)),
                      3200: ("martelo", (1, 3, 4, 5, 6))}
    for g in golpes(False):
        if g.estado in folha_do_golpe:
            folha, desenhos = folha_do_golpe[g.estado]
            assert len(g.poses) == len(desenhos), g.estado
            cx = CAIXA_ARCADE.get(g.estado, g.caixa) if arcade else g.caixa
            quadros = [(f(folha, d), tempo, cx) if 0 < k < len(desenhos) - 1 else (f(folha, d), tempo)
                       for k, (d, tempo) in enumerate(zip(desenhos, g.tempo))]
            Q(g.estado, quadros, NO_AR if g.tipo == "A" else CORPO)
    # (a Saideira Sombria, 3100, fica como está: com desenhos de uma folha só a caixa acompanha o punho e o super de perto
    # deixa de alcançar; mexer nisso muda o equilíbrio e precisa de teste de jogo)
    # aparar (760): defesa 2 -> 3 -> 4 em vez de pular entre poses soltas
    Q(760, [(f("defesa", d2), 4, (-8, -105, 46, -12)), (f("defesa", 3), 10), (f("defesa", 4), 10)])
    Q(610, [(f("bicicleta", 1), 6), (f("bicicleta", 4), 10, (6, -60, 62, -30)), (f("bicicleta", 6), -1)], NO_AR)
    # correntes, kombos, golpes do Despertar e especiais novos (dados em pengaro_extra.py)
    for m in extra.TODOS + extra.ESPECIAIS_A_MAO:
        quadros, caixa = m.quadros, m.caixa
        if arcade and m.estado in DESENHOS_ARCADE_DO_GOLPE:
            troca = DESENHOS_ARCADE_DO_GOLPE[m.estado]
            quadros = [(*troca.get(k, (fl, d)), n, ativo) for k, (fl, d, n, ativo) in enumerate(quadros)]
        if arcade:
            caixa = CAIXA_ARCADE.get(m.estado, caixa)
        Q(m.estado, [(f(fl, d), n, caixa) if ativo else (f(fl, d), n) for fl, d, n, ativo in quadros],
          BAIXO if m.area == "BAIXO" else CORPO)
    # agarrão de comando: errou, fica aberto; acertou, capoeira e whisky
    Q(830, [(f("agarrao", 2), 3, (10, -90, 42, -50)), (f("agarrao", 3), 4), (f("agarrao", 4), 4),
            (f("agarrao", 5), 4)])
    Q(831, [(f(folha, i), n) for folha, i, n in AGARRAO_WHISKY])
    # Despertar: bebe, vê a garrafa vazia, joga no chão e é possuído pelas sombras (regra 7.1: cutscene)
    Q(2000, [(f("despertar_a", i), 7) for i in range(7)] + [(f("despertar_a", 7), 6)]
          + [(f("despertar_b", i), 7) for i in range(7)] + [(f("despertar_b", 7), 10)])
    Q(1005, [(f"bola{i}", 3) for i in range(4)], [(-6, -8, 6, 8)])  # lata de cerveja girando reto
    # Latada de Sombra: arremesso de braço (4 quadros, o 2º solta a lata, como antes)
    for n, fim_ in ((1000, 22), (1001, 26)):
        Q(n, [(f("bola", 2), 8), (f("bola", 4), 5), (f("bola", 5), 6), (f("bola", 7), fim_)])


def montar_sprites(dados=None, retrato=None, hazaki=False):
    p, bola = dados if dados is not None else carregar_poses()
    if not hazaki:
        bola = itens_pengaro.lata()  # o projétil do Pengaró é uma lata de cerveja
    s = Sprites()
    s.folhas = not hazaki
    A = s.add
    # parado e corrida saem do loop desenhado; em quem ainda tem as pastas de fluxo, dos desenhos de sempre
    TROCA_POR_FOLHA["parado0"] = ("ginga_fluida", 0) if desenhado() else ("soco", 0)
    if desenhado():
        # lata: no desenho 1 ele abre a lata com duas mãos sem soltar a garrafa (três mãos); começa do 0, lata na mão
        TROCA_POR_FOLHA.update({"embaixada0": ("lata", 0), "parry": ("defesa", 3)})
        # agachado redesenhado: a folha é a descida (0 em pé, 4 o mais baixo); agachar usa o meio da descida e o fundo
        TROCA_POR_FOLHA.update({"agacha0": ("agachado", 2), "agacha1": ("agachado", 4), "agacha2": ("agachado", 5),
                                "defesa_baixa": ("agachado", 4)})
    TROCA_POR_FOLHA.update({f"corre{i}": ("anda_fluida", i if desenhado() else i * 12) for i in range(4)})

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
    # quadros do meio entre os desenhos (ferramentas/entremeio.py): ginga e andar a 2 ticks por desenho
    fluidas = () if hazaki else ("ginga_fluida", "anda_fluida")
    for nome in ("parado", "anda", "soco") + fluidas:
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
        if nome in LOOPS:
            for i in range(quadros_do_loop(nome)):
                A(f"q_{nome}{i}", quadro_loop(nome, i))
            if desenhado():
                s.proximo += VAGAS_DO_FLUXO[nome] - quadros_do_loop(nome)
            continue
        # soco: a pasta arcade no Pengaró (o soco fraco 200 usa q_soco<i>); parado e anda não têm ação no Pengaró
        for i, arquivo in enumerate(sorted((pasta_da_folha(nome) if nome == "soco" else QUADROS / nome).glob("*.png"))):
            A(f"q_{nome}{i}", abrir_quadro(arquivo))
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
    if not hazaki:
        # chuva de bebidas: garrafa e lata caindo girando (giro de 90°, sem borrar)
        g = itens_pengaro.garrafa()
        g = g.resize((g.width * 2, g.height * 2), Image.NEAREST)  # escala inteira: lê melhor caindo do céu
        for i, q in enumerate((g, g.transpose(Image.ROTATE_270), g.transpose(Image.ROTATE_180), g.transpose(Image.ROTATE_90))):
            A(f"chuva_garrafa{i}", q, eixo=(q.width // 2, q.height // 2))
        for i, q in enumerate(itens_pengaro.latas_girando(escala=2)):
            A(f"chuva_lata{i}", q, eixo=(q.width // 2, q.height // 2))
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
    if not hazaki:
        # ginga da forma despertada: a mesma ginga, de óculos, com as chamas por trás
        for i in range(quadros_do_loop("ginga_fluida")):  # o mesmo sprite que o remap do Despertar põe na ação 0
            e = abrir_quadro(arquivo_loop_endiabrado("ginga_fluida", i))
            A(f"ginga_endiabrada{i}", colar_boss(quadro_loop("ginga_fluida", i), e) if desenhado() else
              colar_endiabrado(None, e, fator_endiabrado("ginga_fluida")))
        if desenhado():
            s.proximo += VAGAS_DO_FLUXO["ginga_fluida"] - quadros_do_loop("ginga_fluida")
    # balões
    for chave, texto in BALOES.items():
        A(f"balao_{chave}", balao(texto))
    if not hazaki:
        sprites_folhas(s)
    return s


# As falas ficam aqui para o Breno editar. A gagueira é só texto, nunca muda o tempo do golpe.
BALOES = {
    "intro": "S-s-saideira? Que sa-saideira,\na no-noite tá só co-começando!",
    "intro_trava": "P-p-p-p-p...",
    "locutor": "FIGHT, CARALHO, A GENTE\nNÃO TEM O DIA TODO!",
    "round": "H-h-hoje tem resenha, ca-caralho.",
    "primeiro": "I-ih, já co-co-começou na sacanagem?",
    "provoca": "F-f-f-f-f-f...",
    "provoca_fim": "...ah, vai se foder, porra.",
    "provoca_cai": "Ai, ca-caralho! De-derramei o whisky!",
    "bola_trava": "La-la-la-la...",
    "bola_ok": "...LATADA DE SOMBRA!",
    "compasso_trava": "Co-co-co-co...",
    "compasso_ok": "...COMPASSO, PORRA!",
    "armada_trava": "A-a-a-a...",
    "armada_ok": "...ARMADA!",
    "caneta_trava": "Ca-ca-ca-ca...",
    "caneta_ok": "...CANETA, FILHO DA PUTA!",
    "errou": "...deixa pra lá, porra.",
    "bola_liso": "LATADA DE SOMBRA, CARALHO!",
    "compasso_liso": "COMPASSO NA TUA CARA!",
    "armada_liso": "ARMADA, VEM QUE TEM!",
    "caneta_liso": "CANETA, PASSOU POR BAIXO!",
    "derrota": "F-f-f-foi falta, porra!\nCa-cadê o VAR, ca-caralho?",
    "locutor_ko": "K.O.! ...ou, no caso dele,\nK-k-k-k-K.O.!",
    "vitoria0": "F-f-foi de letra,\nfilho da puta.",
    "vitoria1": "V-v-vai lá contar pra tua mãe\nque tu a-a-apanhou do gago.",
    "vitoria2": "Es-essa vai na tua conta,\npa-pa-parceiro. A do bar também.",
    "golaco": "O-o-o-olha a... CHUVA DE BEBIDA, CARALHO!",
    "lata": "A-a-a-agora sim, porra!\nSegura que eu vou me-me-meter!",
    "pelada": "SAIDEIRA, CARALHO!\nA RODADA É POR MINHA CONTA!",
    "ressaca": "...e-e-e aí, cadê a-a-a porra da outra lata?",
    "escapou": "A-a-achou que ia me pe-pegar?",
}
ID_BALAO = {chave: 9100 + i for i, chave in enumerate(BALOES)}

VITORIAS = [
    "F-f-foi de letra, filho da puta.",
    "T-t-tá achando que é bo-boteco de domingo, é, ca-caralho?",
    "V-v-vai lá contar pra tua mãe que tu a-a-apanhou do gago.",
    "Eu be-bebo... be-be-BATO melhor que tu, porra!",
    "T-tu ficou pa-parado igual cone. Ma-mas cone pelo menos fica de pé.",
    "D-d-demorei pra falar, mas tu de-de-demorou mais pra levantar.",
    "Es-essa vai na tua conta, pa-pa-parceiro. A do bar também.",
    "Olha só, falei inteiro! Agora chama tua irmã que eu vou ensinar ela a gingar, hein!",
]


def montar_air(s, faiscas, hazaki=False, arte_despertada=None):
    a = Air(s, arte_despertada, hazaki)
    Q = a.acao
    if not hazaki:
        acoes_folhas(Q)
    if hazaki:
        Q(0, [(f"q_parado{i}", 6) for i in range(8)])
    else:
        Q(0, [(f"q_ginga_fluida{i}", t) for i, t in enumerate(tempos_do_loop("ginga_fluida"))])
    if hazaki:
        Q(9203, [(f"juliet{i}", 6) for i in range(4)])
    else:
        Q(9203, [(f"ginga_endiabrada{i}", t) for i, t in enumerate(tempos_do_loop("ginga_fluida"))])
    Q(5, [("parado0", 3), ("anda0", 3)])
    Q(6, [("agacha0", 3), ("parado0", 3)], BAIXO)
    Q(10, [("agacha0", 3)], BAIXO)
    Q(11, [("agacha1", 12), ("agacha2", 12)], BAIXO)
    Q(12, [("agacha0", 3)], BAIXO)
    if hazaki:
        Q(20, [(f"q_anda{i}", 5) for i in range(8)])
        Q(21, [(f"q_anda{i}", 5) for i in range(7, -1, -1)])
    else:
        Q(20, [(f"q_anda_fluida{i}", t) for i, t in enumerate(tempos_do_loop("anda_fluida"))])
        Q(21, [(f"q_anda_fluida{i}", t) for i, t in reversed(list(enumerate(tempos_do_loop("anda_fluida"))))])
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
    if not hazaki:
        Q(830, [("agarra", 3, (10, -90, 42, -50)), ("agarra", 12)])
        Q(831, [("agarra", 14), ("gira1", 14), ("joga", 16)])
    # especiais
    if not hazaki:
        Q(1000, [("rasteira0", 8), ("especial", 5), ("rasteira1", 6), ("rasteira3", 22)], BAIXO)
        Q(1001, [("rasteira0", 8), ("especial", 5), ("rasteira1", 6), ("rasteira3", 26)], BAIXO)
    Q(1005, [(f"quica{i}", 4) for i in range(8)], [(-12, -40, 12, 10)])
    if hazaki:  # no Pengaró a lata acerta e some na faísca
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
        # Chuva de Bebidas: bebe, ergue os braços e chama a chuva (o 5º quadro solta as bebidas)
        Q(3000, [("f_golaco0", 6), ("f_golaco1", 6), ("f_golaco2", 6), ("f_golaco3", 6), ("f_golaco4", 6),
                 ("f_golaco4", 10), ("f_golaco4", 24)])
        Q(3010, [(f"chuva_garrafa{i}", 3) for i in range(4)], [(-12, -22, 12, 22)])
        Q(3011, [(f"chuva_lata{i}", 3) for i in range(4)], [(-10, -15, 10, 15)])
    if hazaki:
        Q(3005, [(f"bolao{i}", 3) for i in range(4)], [(-40, -30, 40, 30)])
        Q(3006, [("bolao0", 3), ("bolao2", 3)], [])
    else:
        # Mão de Sombra: uma massa de sombra (o rastro do endiabrado no auge), não o bolão da lata
        Q(3012, [(f"fx_sombra_rastro_{i}", 2) for i in range(6, 14)], [(-40, -30, 40, 30)], loop=0)
    caixa_p = (0, -110, 90, -10)
    # (Lote 6: compasso e armada têm folha arcade; o super voltou a usar o giro e o chute da armada. No Pengaró o giro
    # é o compasso 4, perna esticada na frente: no 3 da folha arcade a perna ainda está armada atrás e a caixa do
    # super, que fica na frente, não tinha membro dentro.)
    gira, alto = ("gira2" if desenhado() and not hazaki else "gira1"), "kick_alto"
    Q(3100, [("chute0", 4)] + [(n, 4, caixa_p) for n in ("soco1", "chute1", "rasteira1", "soco2", "chute2", gira, "rasteira2", alto)] + [("chute3", 20)])
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
    Q(5170, [("cai2", 6), ("deitado", 10)], DEITADO)
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


def fx_forma(numero):
    """Explod de efeito: no Despertar usa o par do endiabrado (numero + 30), quando os efeitos próprios existem."""
    return f"ifelse(var(20) > 0, {numero + 30}, {numero})" if FAISCA_POR_FORMA else str(numero)


def faiscas(numero):
    """O motor desenha a faísca de acerto sem a troca de sprites do Despertar: com os efeitos próprios do Pengaró,
    o golpe escolhe pelo var(20) entre a faísca do normal (92xx) e a do endiabrado (92xx + 30)."""
    if not FAISCA_POR_FORMA:
        return f"sparkno = S{numero}", "guard.sparkno = S9202"
    # a defesa usa a mesma faísca neutra nas duas formas: no endiabrado ela tem que parecer diferente do acerto
    return f"sparkno = S(ifelse(var(20) > 0, {numero + 30}, {numero}))", "guard.sparkno = S9202"


# Impacto estilo KOF por classe de golpe (só a mecânica: congelamento, tremida, faísca e som do motor).
# classe -> (pausetime P1,P2, guard.pausetime, envshake (t, freq, ampl), fall.envshake, faísca, sparkscale, hitsound)
IMPACTO = {
    "fraco": ((8, 8), (6, 6), None, None, 9200, 1, "5,0"),
    "medio": ((10, 10), (8, 8), None, None, 9201, .9, "5,1"),
    # Sem tremida no forte, no especial e no super (medida: zero; o peso vem do congelamento). O finalizador e o super
    # final ficam com ela como sotaque, com metade da amplitude.
    "forte": ((12, 12), (9, 9), None, None, 9201, 1.15, "5,2"),
    "especial": ((12, 12), (9, 9), None, None, 9201, 1.15, "5,2"),
    "final": ((16, 16), (10, 10), (12, 150, -3), (8, 150, -2), 9205, 1.3, "5,3"),
    "super": ((3, 6), (2, 6), None, None, 9201, 1, "5,1"),
    "super_final": ((20, 20), (12, 12), (20, 150, -3), (12, 150, -2), 9205, 1.5, "5,4"),
}
MODO_HAZAKI = False  # o Hazaki herda o CNS comum e tem que sair byte a byte igual: ele ignora a classe


def tremida(prefixo, t):
    return [f"{prefixo}.time = {t[0]}", f"{prefixo}.freq = {t[1]}", f"{prefixo}.ampl = {t[2]}"]


def hitdef(numero, trigger, attr, dano, tipo="Light", guarda="MA", alvo="MAF", pausa=(8, 8), hit=12, escorrega=5,
           vel="-4", ar="-1.4,-3", queda=False, recupera=True, chao="High", pesado=False, extra="",
           classe=None, pausa_classe=None):
    t = [f"[State {numero}, Golpe]", "type = HitDef", f"trigger1 = {trigger}", f"attr = {attr}",
         f"damage = {dano}, 0", f"animtype = {tipo}", f"guardflag = {guarda}", f"hitflag = {alvo}",
         "priority = 4, Hit", f"pausetime = {pausa[0]}, {pausa[1]}", "sparkxy = -10, -70",
         *faiscas(9201 if pesado else 9200),
         f"hitsound = F{'5,2' if pesado else '5,0'}", "guardsound = F6,0", f"ground.type = {chao}",
         f"ground.slidetime = {escorrega}", f"ground.hittime = {hit}", f"ground.velocity = {vel}",
         f"air.velocity = {ar}"]
    if classe and not MODO_HAZAKI:
        p, gp, shake, fshake, fx, esc, som = IMPACTO[classe]
        p = pausa_classe or p
        t[9:14] = [f"pausetime = {p[0]}, {p[1]}", f"guard.pausetime = {gp[0]}, {gp[1]}", "sparkxy = -10, -70",
                   *faiscas(fx), f"sparkscale = {esc}, {esc}", "guard.sparkscale = .9, .9", f"hitsound = F{som}"]
        if shake:
            t += tremida("envshake", shake)
    if queda:
        t += ["fall = 1", f"fall.recover = {1 if recupera else 0}"]
        if classe and not MODO_HAZAKI:
            if fshake:
                t += tremida("fall.envshake", fshake)
            if recupera and classe == "final":
                t.append("fall.recovertime = 30")
    return "\n".join(t) + "\n" + extra + "\n"


def fim(numero, destino=0):
    return (f"[State {numero}, Fim]\ntype = ChangeState\ntrigger1 = AnimTime = 0\nvalue = {destino}\nctrl = 1\n\n")


def fala(numero, chave, trigger="Time = 0"):
    """Troca o balão do lutador. Ele nasce acima da cabeça e fica parado na tela, sempre inteiro e abaixo da HUD."""
    if not BALOES_LIGADOS:
        return ""
    gatilhos ="\n".join(f"trigger1 = {g.strip()}" for g in trigger.split(" & "))
    w, h = medida_balao(BALOES[chave])
    meia = w // 2 + BALAO_MARGEM
    ponta_minima = BALAO_TOPO_MINIMO + h + 8
    return (f"[State {numero}, Troca fala]\ntype = RemoveExplod\n{gatilhos}\nid = 700\n\n"
            f"[State {numero}, Fala]\ntype = Explod\n{gatilhos}\nanim = {ID_BALAO[chave]}\n"
            "id = 700\nownpal = 1\npostype = left\n"
            f"pos = clamp(ScreenPos X, {meia}, ScreenWidth - {meia}), "
            f"max(ScreenPos Y - {BALAO_ACIMA_DOS_PES}, {ponta_minima})\n"
            "removetime = 70\nsprpriority = 6\nignorehitpause = 1\n\n")


def nome_travado(numero, golpe, fim_sem_acerto="AnimTime = 0"):
    """O nome do golpe trava na gagueira e só sai inteiro se acertar. No Despertar ele fala liso.

    É só balão: nada aqui muda o tempo do golpe.
    """
    return (fala(numero, f"{golpe}_trava", "Time = 0 & var(20) = 0")
            + fala(numero, f"{golpe}_liso", "Time = 0 & var(20) > 0")
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
; var(7) super pulo, var(10) acertos da corrente, var(11) trava da contagem,
; var(20) tempo de Despertar, var(21) ressaca

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

[State 191, Fim]
type = AssertSpecial
trigger1 = AnimTime < 0
flag = Intro

[State 191, Volta]
type = ChangeState
trigger1 = AnimTime = 0
value = 0

"""

def cns_intro():
    return CNS_INTRO_BASE.replace(
        "[State 191, Fim]\n",
        "[State 191, Sorteio]\ntype = VarSet\ntrigger1 = Time = 0\nvar(34) = Random < 250\n\n"
        + fala(191, "intro_trava", "Time = 4 & var(34) = 1")
        + fala(191, "locutor", "Time = 44 & var(34) = 1")
        + fala(191, "intro", "Time = 4 & var(34) = 0")
        + "[State 191, Fim]\n",
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
    if not MODO_HAZAKI:
        t = [l.replace("pausetime = 2, 10", "pausetime = 4, 10") for l in t]
        t[t.index("sparkxy = 0, 0") + 1:t.index("sparkxy = 0, 0") + 1] = [*faiscas(9200), "sparkscale = 1, 1"]
    if queda:
        t += ["fall = 1", "fall.recover = 0"]
    return "\n".join(t) + "\n\n"


def chuva_de_bebidas(numero):
    """Super do Pengaró: seis garrafas e latas caem do céu em cima do oponente, uma a cada 6 ticks.
    A última derruba. Defende-se em pé (vem de cima)."""
    t = []
    for i, dx in enumerate((-30, 24, -8, 36, -40, 6)):
        ultima = i == 5
        t += [f"[State {numero}, Bebida {i + 1}]", "type = Projectile", f"trigger1 = AnimElemTime(5) = {i * 6}",
              "projid = 3000", f"projanim = {3010 + i % 2}", f"projhitanim = {fx_forma(9200)}",
              f"projremanim = {fx_forma(9200)}",
              "postype = p2", f"offset = {dx}, {-210 - 18 * (i % 3)}", f"velocity = 0, {7 + i % 2}",
              "projpriority = 3", "projremovetime = 80", "projheightbound = -400, 1", "attr = S, HP",
              f"damage = {60 if ultima else 42}, 6", "animtype = Heavy" if ultima else "animtype = Med",
              "guardflag = H", "hitflag = MAF", "pausetime = 12, 14" if ultima else "pausetime = 4, 10",
              *faiscas(9205 if ultima else 9200), f"sparkscale = {1.3 if ultima else 1}, {1.3 if ultima else 1}",
              f"hitsound = F5,{3 if ultima else 2}", "guardsound = F6,0", "ground.type = High", "ground.slidetime = 10", "ground.hittime = 16",
              "ground.velocity = -2", "air.velocity = -2,-3"]
        if ultima:
            t += ["fall = 1", "fall.recover = 0", *tremida("envshake", (8, 150, -4)),
                  *tremida("fall.envshake", (8, 150, -3))]
        t.append("")
    return "\n".join(t) + "\n"


def superpausa(numero, trigger):
    # Pengaró: clarão branco de 4 ticks na entrada da super (medido), depois o escurecido da pausa
    clarao = ("" if MODO_HAZAKI else
              f"[State {numero}, Clarão da super]\ntype = BGPalFX\ntrigger1 = {trigger}\ntime = 4\n"
              "add = 255,255,255\nmul = 256,256,256\nignorehitpause = 1\n\n")
    return (f"[State {numero}, Pausa]\ntype = SuperPause\ntrigger1 = {trigger}\ntime = 30\nanim = 100\n"
            "pos = 10, -60\nsound = F20,0\nmovetime = 0\ndarken = 1\n\n" + clarao +
            f"[State {numero}, Rastro]\ntype = AfterImage\ntrigger1 = {trigger}\ntime = 40\n"
            # sem trans o motor desenha as cópias escurecidas por cima: no Despertar virava uma mancha preta no corpo
            + ("length = 8\ntrans = add\npalmul = .45,.25,.65\npaladd = 20,0,40\ntimegap = 2\nframegap = 3\n\n"
               if MODO_HAZAKI else  # Pengaró: rastro cinza (o roxo somado ao palco azul ficava rosa), de 2 em 2 ticks
               "length = 6\ntrans = add\npalcolor = 0\npalbright = 40,40,40\npaladd = 0,0,0\npalmul = .6,.6,.6\n"
               "timegap = 2\nframegap = 2\n\n"))


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
                            pausa=(6, 8), hit=19 if final else 21 if hazaki or g.custo else 23,
                            vel=g.lancamento if g.queda and final else "-3" if final else "-1", ar=g.lancamento,
                            queda=g.queda and final, pesado=final and g.dano >= 75,
                            chao="Low" if g.guarda == "L" else "High",
                            classe=("super_final" if final else "super") if g.custo else "especial"))
        if g.custo and not hazaki:
            c.append(f"[State {n}, Clarão]\ntype = BGPalFX\ntrigger1 = AnimElemTime({impactos + 1}) >= 0 && MoveHit = 1\n"
                     "time = 4\nadd = 128, 128, 128\nignorehitpause = 1\n\n")
        if tipo != "A":
            if 1500 <= n <= 1501 or (hazaki and n in (1300, 1301, 3200)):
                efeito = 9206 if hazaki else fx_forma(9205)
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
            f"reversal.attr = {atributos}\npausetime = 0,0\nsparkno = S(ifelse(var(20) > 0, 7691, 7690))\n"  # faísca do parry.py
            f"p1stateno = {sucesso}\np2stateno = 762\n\n")


def cns_agarrao_whisky():
    """Agarrão de comando do Pengaró. 830 agarra (errou = 12 ticks abertos), 831 é ele batendo, 832 e 833 são
    o oponente preso. Capoeira tira 60, o whisky cai em cima e tira 90, e o oponente é jogado como no agarrão comum."""
    contato, solta = tempos_agarrao_whisky()
    lanca = solta + 13  # a garrafa leva 13 ticks caindo sobre a cabeça do oponente
    t = [estado(830, "S", "A", "S", anim=830, juggle=0),
         "[State 830, Agarra]\ntype = HitDef\ntrigger1 = Time = 0\nattr = S, NT\nhitflag = M-\n"
         "priority = 1, Miss\nsparkno = -1\np1sprpriority = 1\np1facing = 1\np2facing = 1\n"
         "p1stateno = 831\np2stateno = 832\nguard.dist = 0\nfall = 1\n\n",
         fim(830),
         estado(831, "S", "A", "N", anim=831, juggle=0),
         "[State 831, Segura]\ntype = TargetBind\n"
         f"trigger1 = Time < {lanca}\npos = 34, 0\n\n",
         # escape: o oponente saiu do 832 antes da capoeira acertar
         f"[State 831, Escapou]\ntype = ChangeState\ntrigger1 = Time > 1\ntrigger1 = Time < {contato}\n"
         "trigger1 = enemynear,stateno != 832\nvalue = 0\nctrl = 1\n\n",
         # capoeira: 60 de dano, tremida e faísca forte
         f"[State 831, Capoeira dano]\ntype = TargetLifeAdd\ntrigger1 = Time = {contato}\ntrigger1 = NumTarget\nvalue = -60\n\n",
         f"[State 831, Capoeira acerta]\ntype = TargetState\ntrigger1 = Time = {contato}\ntrigger1 = NumTarget\nvalue = 833\n\n",
         f"[State 831, Capoeira treme]\ntype = EnvShake\ntrigger1 = Time = {contato}\ntime = 8\nfreq = 60\nampl = -4\n\n",
         f"[State 831, Capoeira faisca]\ntype = Explod\ntrigger1 = Time = {contato}\nanim = {fx_forma(9201)}\npostype = p1\n"
         "pos = 62, -80\nremovetime = -2\nsprpriority = 4\nownpal = 1\n\n",
         f"[State 831, Capoeira som]\ntype = PlaySnd\ntrigger1 = Time = {contato}\nvalue = F5, 2\n\n",
         # whisky: sai da mão no desenho da bola e cai girando em cima do oponente
         f"[State 831, Garrafa]\ntype = Explod\ntrigger1 = Time = {solta}\nanim = 3010\npostype = p1\n"
         "pos = 38, -150\nvel = 0, 4\naccel = 0, .55\nremovetime = 13\nsprpriority = 5\nownpal = 1\n\n",
         f"[State 831, Whisky dano]\ntype = TargetLifeAdd\ntrigger1 = Time = {lanca}\ntrigger1 = NumTarget\nvalue = -90\n\n",
         f"[State 831, Whisky estoura]\ntype = Explod\ntrigger1 = Time = {lanca}\nanim = {fx_forma(9201)}\npostype = p1\n"
         "pos = 38, -60\nremovetime = -2\nsprpriority = 5\nownpal = 1\n\n",
         f"[State 831, Whisky treme]\ntype = EnvShake\ntrigger1 = Time = {lanca}\ntime = 12\nfreq = 60\nampl = -5\n\n",
         f"[State 831, Whisky som]\ntype = PlaySnd\ntrigger1 = Time = {lanca}\nvalue = F5, 2\n\n",
         f"[State 831, Joga]\ntype = TargetState\ntrigger1 = Time = {lanca}\ntrigger1 = NumTarget\nvalue = 821\n\n",
         fim(831),
         # oponente preso: pode escapar com y ou b só nos primeiros 7 ticks
         "[Statedef 832]\ntype = A\nmovetype = H\nphysics = N\nvelset = 0,0\n\n",
         "[State 832, Pose]\ntype = ChangeAnim2\ntrigger1 = Time = 0\nvalue = 5030\n\n",
         '[State 832, Escape]\ntype = SelfState\ntriggerall = Time <= 7\ntrigger1 = command = "y"\n'
         'trigger2 = command = "b"\nvalue = 0\nctrl = 1\n\n',
         "[State 832, Solto]\ntype = SelfState\ntrigger1 = !gethitvar(isbound)\nvalue = 5050\n\n",
         # oponente apanhando da capoeira e do whisky: sem escape
         "[Statedef 833]\ntype = A\nmovetype = H\nphysics = N\nvelset = 0,0\n\n",
         "[State 833, Pose]\ntype = ChangeAnim2\ntrigger1 = Time = 0\nvalue = 5001\n\n",
         "[State 833, Solto]\ntype = SelfState\ntrigger1 = !gethitvar(isbound)\nvalue = 5050\n\n"]
    return "".join(t)


def inicios_extra(m):
    """Tick de início de cada desenho (já com o RITMO, igual ao AIR) e duração total do golpe."""
    t, ini = 0, []
    ativos = _trechos_ativos(m)
    k0 = ativos[0][0] if ativos else None  # o preparo vem antes do 1º trecho com caixa de golpe (RITMO_PREPARO)
    for k, (_, _, n, _) in enumerate(m.quadros):
        ini.append(t)
        t += round(n * (RITMO_PREPARO if k0 is not None and k < k0 else RITMO)) if n > 0 else n
    return ini, t


def _trechos_ativos(m):
    """(primeiro desenho, desenho seguinte ao último) de cada trecho com caixa de golpe."""
    saida, i, q = [], 0, m.quadros
    while i < len(q):
        if q[i][3]:
            j = i
            while j < len(q) and q[j][3]:
                j += 1
            saida.append((i, j))
            i = j
        else:
            i += 1
    return saida


def cns_novo(m):
    """Golpe simples de pengaro_extra: anda, bate no(s) desenho(s) ativo(s) e volta."""
    ini, _ = inicios_extra(m)
    trechos = _trechos_ativos(m)
    assert len(trechos) == len(m.danos), f"golpe {m.estado}: {len(trechos)} trechos e {len(m.danos)} danos"
    agachado = m.tipo_st == "C"
    t = [estado(m.estado, m.tipo_st, "A", "C" if agachado else "N", anim=m.estado, juggle=3, velset="0,0")]
    if m.avanco:
        inicio = max(1, ini[trechos[0][0]] - 3)
        t.append(f"[State {m.estado}, Avanço]\ntype = VelSet\ntrigger1 = Time = {inicio}\nx = {m.avanco}\n\n")
        fim_av = ini[trechos[-1][1]] if trechos[-1][1] < len(ini) else ini[-1]
        t.append(f"[State {m.estado}, Freia]\ntype = VelSet\ntrigger1 = Time = {fim_av}\nx = 0\n\n")
    for i, ((a, _), dano) in enumerate(zip(trechos, m.danos)):
        ultimo = i == len(trechos) - 1
        final = m.final and ultimo
        forte = dano >= 85 or final
        medio = dano >= 45
        gatilho = f"Time = {ini[a]}" + (" && MoveHit" if i else "")
        queda_aqui = m.queda and ultimo
        t.append(hitdef(m.estado, gatilho, m.attr, dano,
                        tipo="Heavy" if forte else "Medium" if medio else "Light", guarda=m.guarda,
                        hit=21 if forte else 20 if medio else 14, escorrega=8 if forte else 7 if medio else 5,
                        vel=m.vel or ("-7" if forte else "-3.5" if medio else "-2.5"),
                        ar=m.ar or ("-3,-4" if queda_aqui else "-1.4,-3"),
                        queda=queda_aqui, chao=m.chao,
                        classe="final" if final else "forte" if forte else "medio" if medio else "fraco"))
    t.append(fim(m.estado, 11 if agachado else 0))
    return "".join(t)


def cns_especiais_extra():
    """Garrafada em Arco, Rolê por Trás, os especiais exclusivos do Despertar e o agarrão agachado."""
    t = []
    ai = {m.estado: m for m in extra.ESPECIAIS_A_MAO}

    # Garrafada em Arco: o segundo projétil. Sobe, passa por cima de golpe baixo e cai no chão do outro lado
    for n, vx, vy in ((1600, 3.6, -2.6), (1601, 5.0, -3.0)):
        ini, _ = inicios_extra(ai[n])
        t.append(estado(n, "S", "A", "S", anim=n, juggle=4))
        t.append(f"[State {n}, Garrafa]\ntype = Projectile\ntrigger1 = Time = {ini[3]}\nprojid = 1002\n"
                 f"projanim = 3010\nprojhitanim = {fx_forma(9200)}\nprojremanim = {fx_forma(9200)}\nprojhits = 1\nprojpriority = 2\n"
                 f"offset = 52, -96\nvelocity = {vx}, {vy}\naccel = 0, {0.20 if n == 1600 else 0.26}\n"
                 "projheightbound = -400, 0\nattr = S, SP\ndamage = 75, 5\nanimtype = Med\nguardflag = MA\n"
                 f"hitflag = MAF\npausetime = 4, 10\nsparkxy = 0, 0\n{chr(10).join(faiscas(9200))}\nsparkscale = 1, 1\n"
                 "hitsound = F5,1\nguardsound = F6,0\n"
                 "ground.type = High\nground.slidetime = 12\nground.hittime = 18\nground.velocity = -4\n"
                 "air.velocity = -2,-3.5\n\n")
        t.append(fim(n))

    # Rolê por Trás: passa por dentro do oponente (invencível) e chega nas costas dele, já virado.
    # Sem espaço atrás (canto), chega colado na frente, também virado para ele.
    for n in (1700, 1701, 3402):
        ini, _ = inicios_extra(ai[n])
        cruza = ini[3] if n != 3402 else ini[4]
        t.append(estado(n, "S", "A", "N", anim=n, juggle=0))
        t.append(f"[State {n}, Invencivel]\ntype = NotHitBy\ntrigger1 = Time < {cruza + 4}\n"
                 "value = SCA, NA, SA, HA, NP, SP, HP\ntime = 1\n\n")
        t.append(f"[State {n}, Atravessa]\ntype = PlayerPush\ntrigger1 = Time < {cruza + 6}\nvalue = 0\n\n")
        cabe = "p2dist x + 36 < frontedgebodydist"
        t.append(f"[State {n}, Atras]\ntype = PosAdd\ntrigger1 = Time = {cruza}\ntrigger1 = p2dist x > 0\n"
                 f"trigger1 = {cabe}\nx = p2dist x + 36\n\n")
        t.append(f"[State {n}, Vira]\ntype = Turn\ntrigger1 = Time = {cruza}\ntrigger1 = p2dist x > 0\n"
                 f"trigger1 = {cabe}\n\n")
        t.append(f"[State {n}, Canto]\ntype = PosAdd\ntrigger1 = Time = {cruza}\ntrigger1 = p2dist x > 0\n"
                 f"trigger1 = !({cabe})\nx = max(p2dist x - 28, 0)\n\n")
        if n == 1701:
            a = _trechos_ativos(ai[n])[0][0]
            t.append(hitdef(n, f"Time = {ini[a]}", "S, SA", 70, tipo="Medium", pausa=(10, 10), hit=20, escorrega=7,
                            vel="-5", pesado=True, classe="especial"))
        if n == 3402:
            a = _trechos_ativos(ai[n])[0][0]
            t.append(hitdef(n, f"Time = {ini[a]}", "S, SA", 75, tipo="Medium", pausa=(8, 8), hit=22, escorrega=7,
                            vel="-1", ar="-1,-3", pesado=True, classe="especial"))
        t.append(fim(n))

    # Mão de Sombra (Despertar): projétil novo, lento no começo, acelera e acerta duas vezes
    ini, _ = inicios_extra(ai[3400])
    t.append(estado(3400, "S", "A", "S", anim=3400, juggle=4))
    t.append(f"[State 3400, Mão]\ntype = Projectile\ntrigger1 = Time = {ini[3]}\nprojid = 1003\nprojanim = 3012\n"
             "projhitanim = 9231\nprojremanim = 9231\nprojhits = 2\nprojmisstime = 8\nprojpriority = 3\n"
             "offset = 60, -80\nvelocity = 1.8, 0\naccel = 0.07, 0\nattr = S, SP\ndamage = 50, 5\n"
             "animtype = Med\nguardflag = MA\nhitflag = MAF\npausetime = 8, 10\nsparkxy = 0, 0\n"
             f"{chr(10).join(faiscas(9201))}\nsparkscale = 1.15, 1.15\nenvshake.time = 6\nenvshake.freq = 150\n"
             "envshake.ampl = -3\nhitsound = F5,2\n"
             "guardsound = F6,0\nground.type = High\nground.slidetime = 14\nground.hittime = 20\n"
             "ground.velocity = -3\nair.velocity = -2,-3.5\n\n")
    t.append(fim(3400))

    # Queda Escura (Despertar): salta para a frente e mergulha; bate de cima e racha o chão
    ini, _ = inicios_extra(ai[3403])
    a = _trechos_ativos(ai[3403])[0][0]
    t.append(estado(3403, "S", "A", "S", anim=3403, juggle=4))
    t.append("[State 3403, Sobe]\ntype = VelSet\ntrigger1 = Time = 4\nx = 3.4\ny = -8.6\n\n")
    t.append("[State 3403, Ar]\ntype = StateTypeSet\ntrigger1 = Time = 4\nstatetype = A\nphysics = A\n\n")
    t.append("[State 3403, Mergulho]\ntype = VelSet\ntrigger1 = Time >= 8 && Vel Y > 0\npersistent = 0\n"
             "x = 4\ny = 9\n\n")
    t.append(hitdef(3403, "Time >= 8 && Vel Y > 0", "A, SA", 105, tipo="Heavy", queda=True, vel="-4,-6",
                    ar="-4,-6", pausa=(12, 12), hit=22, escorrega=8, pesado=True, extra="persistent = 0\n",
                    classe="especial"))
    t.append(f"[State 3403, Estouro]\ntype = Explod\ntrigger1 = Pos Y >= 0 && Vel Y > 0\nanim = {fx_forma(9205)}\n"
             "postype = p1\npos = 40, -15\nremovetime = -2\nsprpriority = 4\nownpal = 1\n\n")
    t.append("[State 3403, Treme]\ntype = EnvShake\ntrigger1 = Pos Y >= 0 && Vel Y > 0 && MoveHit\ntime = 10\n"
             "freq = 150\nampl = -4\n\n")
    t.append("[State 3403, Pouso]\ntype = ChangeState\ntrigger1 = Vel Y > 0\ntrigger1 = Pos Y >= 0\nvalue = 52\n\n")

    # Agarrão agachado: pega a perna de quem está agachado e arremessa de rasteira
    ini, _ = inicios_extra(ai[841])
    arremesso = ini[4]
    t.append(estado(840, "S", "A", "S", anim=840, juggle=0))
    t.append("[State 840, Agarra]\ntype = HitDef\ntrigger1 = Time = 0\nattr = S, NT\nhitflag = L-\n"
             "priority = 1, Miss\nsparkno = -1\np1sprpriority = 1\np1facing = 1\np2facing = 1\n"
             "p1stateno = 841\np2stateno = 820\nguard.dist = 0\nfall = 1\n\n")
    t.append(fim(840))
    t.append(estado(841, "S", "A", "N", anim=841, juggle=0))
    t.append(f"[State 841, Segura]\ntype = TargetBind\ntrigger1 = Time < {arremesso}\npos = 34, 0\n\n")
    t.append(f"[State 841, Escapou]\ntype = ChangeState\ntrigger1 = Time > 1\ntrigger1 = Time < {arremesso}\n"
             "trigger1 = enemynear,stateno != 820\nvalue = 0\nctrl = 1\n\n")
    t.append(f"[State 841, Dano]\ntype = TargetLifeAdd\ntrigger1 = Time = {arremesso}\ntrigger1 = NumTarget\nvalue = -110\n\n")
    t.append(f"[State 841, Treme]\ntype = EnvShake\ntrigger1 = Time = {arremesso}\ntime = 10\nfreq = 60\nampl = -4\n\n")
    t.append(f"[State 841, Som]\ntype = PlaySnd\ntrigger1 = Time = {arremesso}\nvalue = F5, 2\n\n")
    t.append(f"[State 841, Joga]\ntype = TargetState\ntrigger1 = Time = {arremesso}\ntrigger1 = NumTarget\nvalue = 821\n\n")
    t.append(fim(841))
    return "".join(t)


def cns_extra():
    return "".join(cns_novo(m) for m in extra.TODOS) + cns_especiais_extra()



# Música do Despertar (Breno, issue #33). A faixa do lutador (chars/<lutador>/despertar.ogg, feita por
# converter_musicas.py) substitui a do cenário enquanto a forma dura: na cena da transformação a música do cenário
# vai baixando até sumir (ModifyBGM a cada tique) e só então entra a do boss (PlayBGM), em loop sem emenda a partir do
# loopstart de musicas/loops.json ("stagedef." = prefixo vazio do [Music] do cenário). Quando o Despertar acaba, a do cenário volta (se o oponente não estiver desperto).
# var(51): 0 sem música própria, 2 baixando a do cenário, 1 a do boss tocando. var(52) conta os tiques do fade.
# var(50) fica para os filmes (filmar_luta.py).
FADE_MUSICA = 45  # tiques (0,75 s)


def musica_despertar_cns():
    loops = RAIZ / "musicas" / "loops.json"
    loopstart = 0
    if loops.exists():
        for faixa in json.loads(loops.read_text(encoding="utf-8")).values():
            if faixa["arquivo"] == f"chars/{SAIDA.name}/despertar.ogg":
                loopstart = int(faixa["loopstart"])
    f = FADE_MUSICA
    return f"""; Musica do Despertar (Breno, issue #33): a do cenario baixa ate sumir, entra a do lutador em loop; volta ao fim.
[State -2, Zera musica na intro]
type = VarSet
trigger1 = roundstate < 2
var(51) = 0

[State -2, Musica do cenario comeca a baixar]
type = VarSet
trigger1 = roundstate = 2 && var(51) = 0 && (var(20) > 0 || stateno = 2000)
var(52) = 0

[State -2, Marca fade da musica]
type = VarSet
trigger1 = roundstate = 2 && var(51) = 0 && (var(20) > 0 || stateno = 2000)
var(51) = 2

[State -2, Musica do cenario baixando]
type = ModifyBGM
trigger1 = var(51) = 2 && var(52) < {f}
volume = 100 - (var(52) + 1) * 100 / {f}

[State -2, Conta fade da musica]
type = VarAdd
trigger1 = var(51) = 2 && var(52) < {f}
var(52) = 1

[State -2, Musica do Despertar entra]
type = PlayBGM
trigger1 = var(51) = 2 && var(52) >= {f}
bgm = "despertar.ogg"
volume = 100
loop = 1
loopstart = {loopstart}

[State -2, Marca musica do Despertar]
type = VarSet
trigger1 = var(51) = 2 && var(52) >= {f}
var(51) = 1

[State -2, Musica do cenario volta]
type = PlayBGM
trigger1 = var(51) != 0 && var(20) <= 0 && stateno != 2000
trigger1 = NumEnemy = 0 || enemy,var(51) != 1
source = "stagedef."

[State -2, Desmarca musica do Despertar]
type = VarSet
trigger1 = var(51) != 0 && var(20) <= 0 && stateno != 2000
var(51) = 0

"""


def montar_cns(hazaki=False):
    global MODO_HAZAKI
    MODO_HAZAKI = hazaki
    c = [CNS_TOPO, cns_intro(), CNS_PULOS]

    # golpes em pé, de perto e de longe
    c.append(normal(200, "S, NA", 40, "Time = 4", leve=True, hit=14, vel="-4", classe="fraco"))
    c.append(normal(210, "S, NA", 85, "Time = 7", tipo="Medium", hit=20, escorrega=7, vel="-6", pausa=(10, 10), pesado=True, classe="forte"))
    c.append(normal(215, "S, NA", 80, "Time = 4", tipo="Medium", hit=20, escorrega=7, vel="-5", pausa=(10, 10), pesado=True, classe="forte"))
    c.append(normal(230, "S, NA", 45, "Time = 5", leve=True, hit=14, vel="-4", classe="fraco"))
    c.append(normal(240, "S, NA", 95, "Time = 9", tipo="Heavy", hit=21, escorrega=8, vel="-7", pausa=(11, 11), pesado=True, classe="forte"))
    c.append(normal(245, "S, NA", 85, "Time = 5", tipo="Medium", hit=20, escorrega=7, vel="-5", pausa=(10, 10), pesado=True, classe="forte"))
    # golpe de afastar
    c.append(normal(260, "S, HA", 90, "Time = 12", tipo="Back", queda=True, vel="-7,-5", ar="-5,-5", pausa=(12, 12), pesado=True, classe="forte"))
    # agachado
    c.append(normal(400, "C, NA", 35, "Time = 4", fis="C", tipo_st="C", leve=True, hit=13, vel="-4", chao="Low", classe="fraco"))
    c.append(normal(410, "C, NA", 90, "Time = 6", fis="C", tipo_st="C", tipo="Up", hit=20, vel="-3", ar="-2,-7", pausa=(10, 10), pesado=True, classe="forte"))
    c.append(normal(430, "C, NA", 35, "Time = 5", fis="C", tipo_st="C", leve=True, guarda="L", hit=14, vel="-4", chao="Low", classe="fraco"))
    c.append(normal(440, "C, NA", 80, "Time = 10", fis="C", tipo_st="C", guarda="L", tipo="Back", queda=True, recupera=False, chao="Trip", vel="-3,-2", ar="-3,-2", pausa=(10, 10), pesado=True, classe="forte"))
    # no ar: overhead
    c.append(normal(600, "A, NA", 60, "Time = 5", fis="A", tipo_st="A", guarda="HA", hit=16, classe="fraco"))
    c.append(normal(610, "A, NA", 75, "Time = 6", fis="A", tipo_st="A", guarda="HA", tipo="Medium", hit=18, pesado=True, classe="forte"))
    c.append(normal(650, "A, HA", 80, "Time = 7", fis="A", tipo_st="A", guarda="HA", tipo="Back", queda=True, vel="-5,-4", ar="-4,-4", pesado=True, classe="forte"))

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
    c.append(hitdef(720, "Time = 12", "S, HA", 0, tipo="Back", queda=True, vel="-7,-5", ar="-5,-5", pausa=(12, 12), classe="forte"))
    c.append(fim(720))

    # provocação: tira 25 de barra (250 no motor) do oponente quando termina inteira
    c.append(estado(195, "S", "I", "S", anim=195))
    c.append("[State 195, Sorteio]\ntype = VarSet\ntrigger1 = Time = 0\nvar(36) = Random < 200\n\n")
    c.append(fala(195, "provoca", "Time = 2"))
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
    if not hazaki:
        c.append("[State 810, Treme]\ntype = EnvShake\ntrigger1 = Time = 14\ntime = 8\nfreq = 150\nampl = -3\n\n"
                 "[State 810, Som]\ntype = PlaySnd\ntrigger1 = Time = 14\nvalue = F5, 2\n\n")
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

    if not hazaki:
        c.append(cns_agarrao_whisky())
        c.append(cns_extra())

    # Latada de Sombra: arremessa uma lata de cerveja; fraca lenta, forte rápida, no Despertar sai dobrada
    for n, vel in ((1000, 3.2), (1001, 5.4)):
        c.append(estado(n, "S", "A", "S", anim=n, juggle=4))
        c.append(fala(n, "bola_trava", "Time = 0 & var(20) = 0"))
        c.append(fala(n, "bola_liso", "Time = 0 & var(20) > 0"))
        c.append(projetil(n, "AnimElem = 2", 1005, 1006 if hazaki else fx_forma(9200), vel, 70, "S, SP", ofs="62, -86" if not hazaki else "70, -12"))
        c.append(f"[State {n}, Dobrada]\ntype = Projectile\ntrigger1 = AnimElem = 3\ntrigger1 = var(20) > 0\n"
                 f"projid = 1001\nprojanim = 1005\nprojhitanim = {fx_forma(9200)}\nprojremanim = {fx_forma(9200)}\noffset = {'70, -12' if hazaki else '62, -86'}\n"
                 f"velocity = {vel + 1.2}, 0\nattr = S, SP\ndamage = 50, 4\nanimtype = Med\nguardflag = MA\n"
                 f"hitflag = MAF\npausetime = 4, 10\n{chr(10).join(faiscas(9200))}\nsparkscale = 1, 1\n"
                 "hitsound = F5,1\nguardsound = F6,0\nground.type = High\n"
                 "ground.slidetime = 12\nground.hittime = 18\nground.velocity = -4\nair.velocity = -2,-3.5\n\n")
        c.append(fim(n))

    # Meia-lua de Compasso Sombria: avança girando e derruba
    c.append(estado(1100, "S", "A", "S", anim=1100, juggle=4))
    c.append(nome_travado(1100, "compasso"))
    c.append("[State 1100, Avança]\ntype = VelSet\ntrigger1 = AnimElem = 2\nx = 4\n\n")
    c.append("[State 1100, Para]\ntype = VelSet\ntrigger1 = AnimElem = 6\nx = 0\n\n")
    c.append(hitdef(1100, "AnimElem = 2", "S, SA", 110, tipo="Heavy", queda=True, vel="-5,-4", ar="-4,-4", pausa=(10, 10), pesado=True, classe="especial"))
    c.append(fim(1100))

    # Armada do Quilombo: anti-aéreo, invencível nos 5 primeiros quadros
    c.append(estado(1200, "S", "A", "S", anim=1200, juggle=4))
    c.append(nome_travado(1200, "armada", "Vel Y > 0 & Pos Y >= 0"))
    c.append("[State 1200, Invencivel]\ntype = NotHitBy\ntrigger1 = Time < 5\nvalue = SCA\ntime = 1\n\n")
    c.append("[State 1200, Sobe]\ntype = VelSet\ntrigger1 = Time = 4\nx = 2\ny = -7.5\n\n")
    c.append("[State 1200, Ar]\ntype = StateTypeSet\ntrigger1 = Time = 4\nstatetype = A\nphysics = A\n\n")
    c.append(hitdef(1200, "Time = 4", "S, SA", 120, tipo="Up", queda=True, vel="-2,-7", ar="-2,-7", pausa=(11, 11), pesado=True, classe="especial"))
    c.append("[State 1200, Pouso]\ntype = ChangeState\ntrigger1 = Vel Y > 0\ntrigger1 = Pos Y >= 0\nvalue = 52\n\n")

    # Caneta: desliza por baixo do projétil e troca de lado no acerto
    c.append(estado(1300, "C", "A", "S", anim=1300, juggle=4))
    c.append(nome_travado(1300, "caneta"))
    c.append("[State 1300, Por baixo]\ntype = NotHitBy\ntrigger1 = Time < 18\nvalue = , NP, SP, HP\ntime = 1\n\n")
    c.append("[State 1300, Desliza]\ntype = VelSet\ntrigger1 = AnimElem = 2\nx = 7\n\n")
    c.append("[State 1300, Para]\ntype = VelSet\ntrigger1 = AnimElem = 3\nx = 0\n\n")
    c.append("[State 1300, Passa]\ntype = PlayerPush\ntrigger1 = MoveHit\nvalue = 0\n\n")
    c.append("[State 1300, Troca]\ntype = PosAdd\ntrigger1 = MoveHit = 1\nx = 60\n\n")
    c.append(hitdef(1300, "AnimElem = 2", "C, SA", 70, tipo="Back", guarda="L", queda=True, chao="Trip", vel="-2,-2", ar="-2,-2", pausa=(8, 8), classe="especial"))
    c.append(fim(1300, 11))

    # Despertar: bebe a lata, 600 quadros turbinado
    c.append(estado(2000, "S", "I", "S", anim=2000))
    c.append(superpausa(2000, "Time = 0"))
    # Pengaró: o Despertar só sai com a barra cheia e gasta tudo (regra 4); o Hazaki segue com 1 estoque
    c.append(f"[State 2000, Gasta]\ntype = PowerAdd\ntrigger1 = Time = 0\nvalue = -{1000 if hazaki else 3000}\n\n")
    c.append("[State 2000, Invencivel]\ntype = NotHitBy\ntrigger1 = 1\nvalue = SCA\ntime = 1\n\n")
    if not hazaki:
        # a transformação empurra o oponente para longe
        c.append("[State 2000, Afasta]\ntype = PosAdd\ntrigger1 = Time >= 14\ntrigger1 = Time <= 60\n"
                 "trigger1 = p2bodydist x < 90\nx = -1.8\nredirectid = enemynear,id\n\n")
    c.append(fala(2000, "lata", "Time = 2"))
    c.append("[State 2000, Liga]\ntype = VarSet\ntrigger1 = AnimTime = 0\nvar(20) = 600\n\n")
    c.append(fim(2000))

    # Chuva de Bebidas (1 estoque): o super antes do Despertar
    c.append(estado(3000, "S", "A", "S", anim=3000, juggle=0))
    c.append(superpausa(3000, "Time = 0"))
    c.append("[State 3000, Gasta]\ntype = PowerAdd\ntrigger1 = Time = 0\nvalue = -1000\n\n")
    c.append("[State 3000, Invencivel]\ntype = NotHitBy\ntrigger1 = AnimElemTime(5) < 0\nvalue = SCA\ntime = 1\n\n")
    c.append(fala(3000, "golaco", "Time = 2"))
    if hazaki:
        c.append(projetil(3000, "AnimElem = 5", 3005, 3006, 7, 60, "S, HP", hits=5, intervalo=5, id_=3000, ofs="90, -46", queda=True))
    else:
        c.append(chuva_de_bebidas(3000))
    c.append(fim(3000))

    # Saideira Sombria (Super Despertado): 8 acertos e acaba o Despertar
    c.append(estado(3100, "S", "A", "S", anim=3100, juggle=0))
    c.append(superpausa(3100, "Time = 0"))
    c.append("[State 3100, Gasta]\ntype = PowerAdd\ntrigger1 = Time = 0\nvalue = ifelse(var(20) > 0, -1000, -2000)\n\n")
    c.append("[State 3100, Fim Despertar]\ntype = VarSet\ntrigger1 = Time = 0\nvar(20) = 0\n\n")
    c.append("[State 3100, Invencivel]\ntype = NotHitBy\ntrigger1 = Time < 4\nvalue = SCA\ntime = 1\n\n")
    c.append(fala(3100, "pelada", "Time = 2"))
    c.append("[State 3100, Avança]\ntype = VelSet\ntrigger1 = Time = 4\nx = 2\n\n")
    c.append(hitdef(3100, "(Time >= 4) && (Time <= 32) && (Time % 4 = 0)", "S, HA", 47, tipo="Medium", hit=16, escorrega=4, vel="-1", ar="-1,-3", pausa=(2, 6), pesado=True, classe="super"))
    c.append(hitdef(3100, "Time = 36", "S, HA", 60, tipo="Back", queda=True, recupera=False, vel="-7,-6", ar="-7,-6", pausa=(14, 14), pesado=True, classe="super_final"))
    c.append("[State 3100, Clarão]\ntype = BGPalFX\ntrigger1 = MoveHit = 1 && Time >= 36\ntime = 4\n"
             "add = 128, 128, 128\nignorehitpause = 1\n\n")
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

; corrente de 3 golpes: var(10) conta os acertos de verdade (defendido não conta); var(11) trava a contagem
; para o mesmo acerto não somar duas vezes durante a pausa do contato. O finalizador exige var(10) >= 3.
[State -2, Zera corrente]
type = VarSet
trigger1 = ctrl
var(10) = 0

[State -2, Conta acerto da corrente]
type = VarAdd
trigger1 = MoveHit
trigger1 = var(11) = 0
trigger1 = (stateno = [200,349]) || (stateno = [3410,3423])
var(10) = 1

[State -2, Trava contagem]
type = VarSet
trigger1 = MoveHit
trigger1 = var(11) = 0
var(11) = 1

[State -2, Libera contagem]
type = VarSet
trigger1 = !MoveHit
var(11) = 0

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

""" + musica_despertar_cns() + """[State -2, Ressaca começa]
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

[State -2, Vira endiabrado]
type = RemapSprite
trigger1 = var(20) > 0 && var(37) = 0
preset = "despertado"

[State -2, Endiabrado ligado]
type = VarSet
trigger1 = var(20) > 0
var(37) = 1

[State -2, Volta ao normal]
type = RemapSprite
trigger1 = var(20) <= 0 && var(37) = 1
trigger2 = roundstate < 2
reset = 1

[State -2, Endiabrado desligado]
type = VarSet
trigger1 = var(20) <= 0
var(37) = 0

[State -2, Aura]
type = PalFX
trigger1 = var(20) > 0 && alive
time = 2
add = 12, 0, 28
sinadd = 10, 0, 18, 40

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
    # o golpe ficou mais longo: o atordoamento acompanha, para as correntes continuarem encaixando
    resultado = re.sub(r"(?m)^((?:ground|guard|air)\.hittime = )(\d+)", lambda m: f"{m[1]}{round(int(m[2]) * RITMO)}", resultado)
    if hazaki:
        # a contagem de acertos das correntes de 3 golpes é só do Pengaró
        resultado = re.sub(r"; corrente de 3 golpes:.*?\[State -2, Libera contagem\]\ntype = VarSet\n"
                           r"trigger1 = !MoveHit\nvar\(11\) = 0\n\n", "", resultado, flags=re.S)
        resultado = resultado.replace(f"anim = {ID_BALAO['lata']}", f"anim = {ID_BALAO['golaco']}")
        resultado = resultado.replace("add = 12, 0, 28", "add = 42, 16, 0").replace("sinadd = 10, 0, 18, 40", "sinadd = 24, 8, 0, 40")
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


def entradas_extra():
    """Entradas de correntes, kombos e golpes do Despertar. Vêm antes dos normais; as que dependem de estado
    (continuação de corrente e de kombo) só valem enquanto o golpe anterior encostou."""
    c = []
    em_pe, sem_baixo = "statetype = S", 'command != "holddown"'
    sem_frente = 'command != "holdfwd"'
    desperto = "var(20) > 0"
    cancela_fraco = "(stateno = 200 || stateno = 230) && movehit && movehit <= 8"

    # --- Despertar: normais com função nova no lugar dos normais base
    c.append(entrada("Desp: Mao de Chao Possuida", 3430, ['command = "y"', 'command = "holddown"', "statetype != A", desperto], ("ctrl",)))
    c.append(entrada("Desp: Foice Escura", 3435, ['command = "b"', 'command = "holddown"', "statetype != A", desperto], ("ctrl",)))
    c.append(entrada("Desp: Tranco Possuido", 3431, ['command = "y"', 'command = "holdfwd"', em_pe, desperto],
                     ("ctrl", cancela_fraco)))
    c.append(entrada("Desp: Passo de Sombra", 3432, ['command = "b"', 'command = "holdfwd"', em_pe, desperto], ("ctrl",)))
    c.append(entrada("Desp: Palma Torta", 3433, ['command = "x"', 'command = "holdback"', em_pe, desperto], ("ctrl",)))
    c.append(entrada("Desp: Puxada Sombria", 3434, ['command = "a"', 'command = "holdback"', em_pe, desperto], ("ctrl",)))
    # --- Despertar: kombo novo (b, a, x) e as duas correntes novas (y e b, 4 golpes cada)
    c.append(entrada("Desp: Kombo 3", 349, ['command = "x"', em_pe, desperto], ("stateno = 348 && movecontact",)))
    c.append(entrada("Desp: Kombo 2", 348, ['command = "a"', sem_baixo, em_pe, desperto],
                     ("stateno = 3420 && movecontact",)))
    for botao, base, hits in (("y", 3410, "stateno = 3410"), ("b", 3420, "stateno = 3420")):
        c.append(entrada(f"Desp: corrente {botao} final", base + 3, [f'command = "{botao}"', sem_baixo, em_pe, desperto],
                         (f"stateno = {base + 2} && movehit && var(10) >= 3",)))
        c.append(entrada(f"Desp: corrente {botao} 3", base + 2, [f'command = "{botao}"', sem_baixo, em_pe, desperto],
                         (f"stateno = {base + 1} && movecontact",)))
        c.append(entrada(f"Desp: corrente {botao} 2", base + 1, [f'command = "{botao}"', sem_baixo, em_pe, desperto],
                         (f"stateno = {base} && movecontact",)))
        c.append(entrada(f"Desp: corrente {botao} 1", base, [f'command = "{botao}"', sem_baixo, sem_frente,
                                                              'command != "holdback"', em_pe, desperto], ("ctrl",)))

    # --- kombos de assinatura (o 1º golpe é um normal que já existe)
    c.append(entrada("Kombo 1: x", 340, ['command = "x"', sem_baixo, em_pe], ("stateno = 216 && movecontact",)))
    c.append(entrada("Kombo 1: b", 341, ['command = "b"', sem_baixo, em_pe], ("stateno = 340 && movecontact",)))
    c.append(entrada("Kombo 2: baixo a", 342, ['command = "a"', 'command = "holddown"', "statetype != A"],
                     ("stateno = 200 && movecontact",)))
    c.append(entrada("Kombo 2: y", 343, ['command = "y"', sem_baixo, "statetype != A"], ("stateno = 342 && movecontact",)))
    c.append(entrada("Kombo 3: y", 344, ['command = "y"', sem_baixo, em_pe, 'command != "holdfwd"'],
                     ("stateno = 201 && movecontact",)))
    c.append(entrada("Kombo 3: frente b", 345, ['command = "b"', 'command = "holdfwd"', em_pe],
                     ("stateno = 344 && movecontact",)))
    c.append(entrada("Kombo 4: b", 346, ['command = "b"', sem_baixo, em_pe], ("stateno = 230 && movecontact",)))
    c.append(entrada("Kombo 4: baixo y", 347, ['command = "y"', 'command = "holddown"', "statetype != A"],
                     ("stateno = 346 && movecontact",)))

    # --- correntes de 3 golpes + finalizador (o 1º golpe é o normal do botão)
    for botao, base, primeiros in (("x", 300, "stateno = 200"), ("y", 310, "stateno = 210 || stateno = 215"),
                                   ("a", 320, "stateno = 230"), ("b", 330, "stateno = 240 || stateno = 245")):
        cond = [f'command = "{botao}"', sem_baixo, em_pe]
        c.append(entrada(f"Corrente {botao}: final", base + 3, cond, (f"stateno = {base + 2} && movehit && var(10) >= 3",)))
        c.append(entrada(f"Corrente {botao}: 3o", base + 2, cond, (f"stateno = {base + 1} && movecontact",)))
        c.append(entrada(f"Corrente {botao}: 2o", base + 1, cond, (f"({primeiros}) && movecontact",)))
    return "".join(c)


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
    if not hazaki:
        c.append(comando("agarrao_whisky", "~B, F, y", 18))  # ← → + y: o agarrão de comando (regra G)
        for b in "xy":
            c.append(comando(f"garrafa_{b}", f"~F, B, {b}", 18))  # → ← + x/y: Garrafada em Arco
        for b in "ab":
            c.append(comando(f"role_{b}", f"~F, B, {b}", 18))  # → ← + a/b: Rolê por Trás
        for b in "xyab":
            c.append(comando(f"sombra_{b}", f"~D, D, {b}", 18))  # ↓ ↓ + botão: exclusivos do Despertar
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
    c.append(comando("despertar", "x+a+y" if hazaki else "x+y", 3))
    c.append(comando("superpulo", "$D, $U", 10, 6))
    for nome in "xyabc":
        # Pengaró: botão de ataque fica guardado 8 ticks; apertado durante a pausa do contato, a corrente sai
        c.append(comando(nome, nome, 1, 8 if not hazaki and nome in "xyab" else None))
    c.append(comando("start", "s", 1))
    for nome, d in (("holdfwd", "/$F"), ("holdback", "/$B"), ("holdup", "/$U"), ("holddown", "/$D")):
        c.append(comando(nome, d, 1))

    c.append("[Statedef -1]\n\n")
    cancela = "stateno = 200 || stateno = 210 || stateno = 215 || stateno = 216 || stateno = 230 || stateno = 245 || stateno = 400 || stateno = 410 || stateno = 430 || stateno = 260"
    if not hazaki:
        # corrente: 1º e 2º golpes cancelam em especial; o 3º cancela se acertou; o finalizador não cancela
        cancela += "".join(f" || stateno = {n}" for n in (301, 311, 321, 331, 340, 342, 344, 346, 3410, 3420, 3431,
                                                          3433, 3434, 348))
    so_se_acertou = ""
    if not hazaki:
        so_se_acertou = (" || ((stateno = 302 || stateno = 312 || stateno = 322 || stateno = 332 || stateno = 3411 "
                         "|| stateno = 3421) && movehit && movehit <= 8)")
    c.append("[State -1, Pode cancelar]\ntype = VarSet\ntrigger1 = 1\n"
             f"var(1) = ctrl || (({cancela}) && movecontact && movecontact <= 8){so_se_acertou}\n\n")

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
        c.append(entrada("Saideira Sombria", 3100, ['command = "golaco"', "power >= 1000", f"({forte})"] + no_chao, ("var(1)", especial_em_super)))
        c.append(entrada("Chuva de Bebidas", 3000, ['command = "golaco"', "power >= 1000"] + no_chao, ("var(1)", especial_em_super)))
    c.append(entrada("Despertar", 2000, ['command = "despertar"', "power >= 1000" if hazaki else "power >= powermax",
                                          "var(20) = 0", "statetype = S"], ("ctrl",)))
    if not hazaki:
        for nome, n, botoes in (("armada", 1200, "xy"), ("caneta", 1300, "xy"), ("compasso", 1100, "ab")):
            for i, b in enumerate(botoes):
                c.append(entrada(nome, n+i, [f'command = "{nome}_{b}"'] + no_chao))
        # um projétil próprio por vez na tela (a Dobrada sai dentro do mesmo golpe; a chuva não conta)
        um_projetil = "numprojid(1000) + numprojid(1001) + numprojid(1002) + numprojid(1003) = 0"
        bola = [um_projetil] + no_chao
        c.append(entrada("Bola forte", 1001, ['command = "bola_forte"'] + bola))
        c.append(entrada("Bola fraca", 1000, ['command = "bola_fraca"'] + bola))
        # segundo projétil (em arco), ida para trás do oponente e os exclusivos do Despertar
        garrafa = [um_projetil, "var(20) = 0"] + no_chao  # no Despertar a garrafa não tem forma endiabrada
        c.append(entrada("Garrafada forte", 1601, ['command = "garrafa_y"'] + garrafa))
        c.append(entrada("Garrafada fraca", 1600, ['command = "garrafa_x"'] + garrafa))
        c.append(entrada("Role por tras e chute", 1701, ['command = "role_b"', "p2dist x > 0"] + no_chao))
        c.append(entrada("Role por tras", 1700, ['command = "role_a"', "p2dist x > 0"] + no_chao))
        desperto = ["var(20) > 0"] + no_chao
        c.append(entrada("Mao de Sombra", 3400, ['command = "sombra_x"', um_projetil] + desperto))
        c.append(entrada("Chute da Corrente", 3401, ['command = "sombra_y"'] + desperto))
        c.append(entrada("Sombra Atravessada", 3402, ['command = "sombra_a"', "p2dist x > 0"] + desperto))
        c.append(entrada("Queda Escura", 3403, ['command = "sombra_b"'] + desperto))
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
    if not hazaki:
        # agarrão de comando: de perto (12), antes do agarrão comum e dos normais
        c.append(entrada("Agarrao whisky", 830, ['command = "agarrao_whisky"', "statetype = S", "stateno != 100",
                                                "p2bodydist x < 12", "p2statetype != A", "p2movetype != H"], ("ctrl",)))
        c.append(entrada("Agarrao agachado", 840, ['command = "y"', 'command = "holddown"', "statetype != A", "ctrl",
                                                  "stateno != 100", "p2bodydist x < 8", "p2statetype = C",
                                                  "p2movetype != H"], ("1",)))
    for lista in (pega, pega_k):
        c.append(entrada("Agarrao", 800, lista + ['(command = "holdfwd" || command = "holdback")'], ("1",)))
    if not hazaki:
        c.append(entradas_extra())  # depois dos agarrões (colado, o agarrão tem prioridade) e antes dos normais
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
Latada de Sombra					_D_F^K
Meia-lua de Compasso Sombria		_D_B^K
Armada do Quilombo					_F_D^P
Caneta								_D_B^P
Mão de Chimpá / Mão Pesada          _D_F^P
Sola de Várzea / Pisão de Bar       _B_D^K
Garrafada em Arco <#bebebe>(projétil em arco)</>	_F_B^P
Rolê por Trás / Rolê e Chute		_F_B^K

<#f0f000>:Exclusivos do Despertar:</>
Mão de Sombra <#bebebe>(projétil)</>	_D_D^X
Chute da Corrente					_D_D^Y
Sombra Atravessada					_D_D^A
Queda Escura						_D_D^B
Y: Revolta, Sola de Ferro, Cabeçada, Roda	^Y^Y^Y^Y
B: Calcanhar, Afastar, Armada, Chute Partido	^B^B^B^B
Kombo Possessão						^B,^A,^X

<#f0f000>:Correntes (acertando os 3, o 4º derruba):</>
Soco fraco							^X^X^X^X
Soco forte							^Y^Y^Y^Y
Chute fraco							^A^A^A^A
Chute forte							^B^B^B^B

<#f0f000>:Kombos:</>
Abertura							_F+^Y, ^X, ^B
Alto e Baixo						^X, _D+^A, ^Y
Empurrão							_B+^X, ^Y, _F+^B
Lançador							^A, ^B, _D+^Y

<#f0f000>:Supers:</>
Chuva de Bebidas <#bebebe>(1000)</>	_B_F_D^K
Saideira Sombria (no Despertar)	_B_F_D^K
Bando da Várzea / Apagão da Várzea  _B_F_D^P

<#f0f000>:Sistema:</>
Despertar: Lata Gelada <#bebebe>(barra cheia)</>	^X_+^Y
Rolamento							^X_+^A
Golpe de afastar					^Y_+^B
Agarrão								[_B/_F]_+^Y
Agarrão agachado <#bebebe>(oponente agachado)</>	_D_+^Y
Martelo e Garrafada <#bebebe>(colado)</>		_B_F^Y
Provocação							^C
Parry                              _F^C
"""


# Poses da folha "endiabrado" (sprites/pengaro/quadros/endiabrado/00..07.png, recortadas com recortar_quadros.py) e
# os desenhos do jogo que cada uma substitui na forma despertada, como no Diabo Loiro do Hazaki.
POSES_ENDIABRADO = {
    0: ("parado0", "soco3", "chute3", "recua", "defesa", "parry", "pouso"),
    1: ("anda0",),
    2: ("agacha0", "agacha1", "rasteira0", "rasteira1", "rasteira2", "rasteira3", "baixo_cima0", "baixo_soco"),
    3: ("soco1", "soco2", "ar_soco", "q_soco4", "q_soco5"),
    4: ("chute0", "chute1", "chute2", "ar_chute", "bicicleta"),
    5: ("baixo_cima1", "kick_alto"),
    6: ("especial",),
    7: ("pulo_sobe", "pulo_topo", "pulo_desce"),
}


def arte_endiabrada(s):
    """Se a folha da forma endiabrada já foi gerada, devolve {sprite do jogo: sprite despertado}; senão, vazio
    (e o gerador cai no corpo escurecido com chamas do pixelfx)."""
    pasta = QUADROS / "endiabrado"  # o Gutto troca QUADROS e usa a forma de cavalo dele
    arquivos = sorted(pasta.glob("[0-9][0-9].png"))
    if len(arquivos) != 8:
        return {}
    arte = {}
    for indice in range(8):
        arte[f"pose{indice}"] = s.add(f"endiabrado_pose{indice}",
                                      colar_endiabrado(None, abrir_quadro(arquivos[indice]), fator_endiabrado("endiabrado")))
    for indice, nomes in POSES_ENDIABRADO.items():
        tela = colar_endiabrado(None, abrir_quadro(arquivos[indice]), fator_endiabrado("endiabrado"))
        for j, nome in enumerate(nomes):
            arte[nome] = s.add(f"endiabrado_{nome}", move(tela, j % 3 - 1))
    return arte


SOBRA_CLSN1 = 4  # px de caixa de golpe além do membro visível (a regra 8.3 aceita até 12)
LARGURA_MINIMA_CLSN1 = 12
SOBRA_MAXIMA_CLSN1 = 12  # regra 8.3: teto de caixa além do membro da forma normal


def ajustar_clsn1(blocos, s, preset):
    """A caixa de golpe acompanha o membro. Os quadros do meio herdavam a caixa do desenho de contato, então a caixa
    ficava esticada (alcance fantasma) depois que o braço ou a perna já tinha recuado. Aqui cada caixa é encurtada até
    o pixel opaco mais à frente na faixa vertical dela (o maior entre o normal e o endiabrado, que o RemapSprite põe no
    lugar) mais SOBRA_CLSN1. Nunca aumenta a caixa e nunca deixa menos de LARGURA_MINIMA_CLSN1."""
    pares = {(int(a), int(b)): (int(c), int(d)) for a, b, c, d in re.findall(r"(\d+),(\d+) = (\d+),(\d+)", preset)}
    imagens = {(g, i): (img, ex, ey) for g, i, img, ex, ey in s.lista}
    mascaras = {}

    def frente(cod, y1, y2):
        if cod not in imagens:
            return None
        if cod not in mascaras:
            img, ex, ey = imagens[cod]
            ys, xs = np.nonzero(np.asarray(img.getchannel("A")) >= 128)
            mascaras[cod] = (xs - ex, ys - ey)
        x, y = mascaras[cod]
        faixa = (y >= min(y1, y2)) & (y <= max(y1, y2))
        return int(x[faixa].max()) if faixa.any() else None

    saida = []
    for bloco in blocos:
        m = re.match(r"\[Begin Action (\d+)\]", bloco)
        numero = int(m[1]) if m else -1
        if not m or numero in PROJETEIS or not 200 <= numero % 10000 < 4000 and numero % 10000 >= 1000:
            saida.append(bloco)
            continue
        linhas, pendente = bloco.split("\n"), None
        for k, linha in enumerate(linhas):
            caixa = re.match(r"\s*Clsn1\[0\] = (-?\d+),(-?\d+),(-?\d+),(-?\d+)$", linha)
            if caixa and k and linhas[k - 1].startswith("Clsn1: 1"):
                pendente = (k, tuple(int(v) for v in caixa.groups()))
            elif pendente and re.match(r"-?\d+,\s*-?\d+,", linha):
                g, i = (int(v) for v in linha.split(",")[:2])
                x1, y1, x2, y2 = pendente[1]
                # a ação 1xxxx é a do Despertar (o endiabrado); a normal que tem a sua 1xxxx fica só com o normal; as
                # que não têm 1xxxx aparecem nas duas formas e usam a maior medida
                tem_variante = numero in ATAQUES_DESPERTADOS
                usa = []
                if numero < 10000:
                    usa.append((g, i))
                if numero >= 10000 or not tem_variante:
                    usa.append(pares.get((g, i)))
                medidas = [frente(c, y1, y2) for c in usa if c]
                medidas = [v for v in medidas if v is not None]
                alvo = max(medidas) + SOBRA_CLSN1 if medidas else None
                # ação sem variante 1xxxx serve às duas formas e usa a maior; mas nunca mais de SOBRA_MAXIMA_CLSN1
                # além do membro da forma normal (a cabeçada 303 ficava 17 px à frente da cabeça)
                normal = frente((g, i), y1, y2) if numero < 10000 and desenhado() else None
                if medidas and normal is not None:
                    alvo = min(alvo, normal + SOBRA_MAXIMA_CLSN1)
                if medidas and max(x1, x2) > alvo:
                    ponta = max(alvo, min(x1, x2) + LARGURA_MINIMA_CLSN1)
                    if x2 >= x1:
                        x2 = min(x2, ponta)
                    else:
                        x1 = min(x1, ponta)
                    linhas[pendente[0]] = f" Clsn1[0] = {x1},{y1},{x2},{y2}"
                pendente = None
            elif re.match(r"-?\d+,\s*-?\d+,", linha):
                pendente = None
        saida.append("\n".join(linhas))
    return saida


TROCAS_SUPER_3100 = (
    ("trigger1 = var(20) > 0 && var(37) = 0", "trigger1 = (var(20) > 0 || stateno = 3100) && var(37) = 0"),
    ("trigger1 = var(20) > 0\nvar(37) = 1", "trigger1 = var(20) > 0 || stateno = 3100\nvar(37) = 1"),
    ("trigger1 = var(20) <= 0 && var(37) = 1", "trigger1 = var(20) <= 0 && stateno != 3100 && var(37) = 1"),
    ("trigger1 = var(20) <= 0\nvar(37) = 0", "trigger1 = var(20) <= 0 && stateno != 3100\nvar(37) = 0"),
)


def super_3100_endiabrado(cns):
    """O super 3100 zera var(20) no primeiro tick (custo e dano), mas o corpo segue despertado do começo ao fim:
    var(37) e o RemapSprite olham também o stateno = 3100. Vale para todo lutador do gerador comum (Pengaró, CK,
    Gutto, Raiclaven); o robô cobra no teste "var(37) = 1 no meio do 3100"."""
    for velho, novo in TROCAS_SUPER_3100:
        if cns.count(velho) != 1:
            raise SystemExit(f"super_3100_endiabrado: {velho!r} aparece {cns.count(velho)} vezes (esperado 1)")
        cns = cns.replace(velho, novo, 1)
    return cns


def despertar_do_pengaro(cns):
    """Lógica do Despertar que só o Pengaró tem (o Hazaki usa o mesmo bloco `-2` e não pode mudar).
    1. O super 3100 zera var(20) no primeiro tick (custo e dano), mas continua endiabrado do começo ao fim.
    2. O motor só zera as variáveis no primeiro round (IntPersistIndex = 60): na introdução de cada round o Despertar
       e a ressaca do round anterior são zerados.
    3. A saída do Despertar (var(20) = 12) solta uma fumaça violeta (a 9215) em volta do corpo.
       Uma só: com ignorehitpause, um hitpause no tick 12 soltaria uma por tick, daí o NumExplod(9215) = 0."""
    trocas = (
        ("[State -2, Conta Despertar]\ntype = VarAdd",
         "[State -2, Zera Despertar na intro]\ntype = VarSet\ntrigger1 = roundstate < 2\nvar(20) = 0\n\n"
         "[State -2, Zera ressaca na intro]\ntype = VarSet\ntrigger1 = roundstate < 2\nvar(21) = 0\n\n"
         "[State -2, Conta Despertar]\ntype = VarAdd"),
        ("[State -2, Ressaca começa]",
         "[State -2, Endiabrado pela seleção]\ntype = VarSet\ntrigger1 = palno = 2 && roundstate >= 2\nvar(20) = 600\n\n"
         "[State -2, Ressaca começa]"),
        ("[State -2, Bônus de dano]",
         "[State -2, Fumaça na saída do Despertar]\ntype = Explod\ntrigger1 = var(20) = 12 && NumExplod(9215) = 0\n"
         "anim = 9215\nid = 9215\n"
         "postype = p1\npos = 0, 0\nremovetime = 20\nsprpriority = 4\nownpal = 1\nscale = 1, 1\n"
         "ignorehitpause = 1\nsupermovetime = -1\n\n[State -2, Bônus de dano]"),
    )
    for velho, novo in trocas:
        assert cns.count(velho) == 1, velho
        cns = cns.replace(velho, novo, 1)
    return super_3100_endiabrado(cns)


def sem_ginga_9203(cns):
    """A ginga do Despertar já sai da ação 0 pelo RemapPreset. O ChangeAnim para a 9203 brigava com o estado 0 do
    motor (common1.cns.zss: `anim != 0` volta para a ação 0 todo tick): a animação recomeçava a cada tick e ele ficava
    congelado no 1º desenho. Vale para o Pengaró, o Gutto e o Raiclaven (os três têm o preset)."""
    bloco = re.compile(r"\[State -2, Ginga de Juliet\]\n(?:[^\n]+\n)+\n\[State -2, Tira os oculos\]\n(?:[^\n]+\n)+\n")
    cns, n = bloco.subn("", cns)
    assert n == 1, "bloco da ginga 9203 não encontrado"
    return cns


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    # Caixas de colisão do desenho arcade, só no Pengaró (Gutto, Raiclaven e Hazaki não passam por aqui): agachado de
    # 77 a 85 px de altura (o antigo tinha 72) e deitado de 138 x 34 px (o antigo cabia em 120 x 24). Rolamento, caneta
    # e levantada (ROLANDO) ficam como eram: a caneta passa por baixo de projétil.
    BAIXO[0] = (-28, 0, 28, -80)
    DEITADO[0] = (-70, 0, 70, -34)
    # Lote 7: os desenhos da aura antiga seguem no .sff só pela paleta (veja AURA_BOSS); a aura do jogo é a 9600
    for anim, nome in AURA_BOSS.items():
        FX_PENGARO[anim] = (None, nome, 5)
        CHAO.add(nome)
    s = montar_sprites(retrato=RAIZ / "sprites/pengaro-selecao-kof.png")
    faiscas = carregar_faiscas(s)
    for anim in AURA_BOSS:  # só pela paleta: fora do .air, e a poda os tira do .sff
        del faiscas[anim]
    a = montar_air(s, faiscas, arte_despertada=arte_endiabrada(s))
    preset = preset_despertado(s)
    aura = aura_pengaro.ligar(s)  # aura do endiabrado (Blender): grupos e ações 9600 a 9603, fora da paleta
    (SAIDA / "pengaro.air").write_text("\n".join(ajustar_clsn1(a.txt, s, preset)) + "\n" + aura.air(),
                                       encoding="utf-8", newline="\n")
    cns = despertar_do_pengaro(ajustar_sparkxy(remapear_animelem(montar_cns(), a.mapas), a.ativos))
    cns = sem_ginga_9203(cns)
    fracos = {int(n) for n in re.findall(r"\[State (\d+), Golpe\]\n(?:[^\n]+\n)*?hitsound = F5,0\n", cns)}
    assert fracos == FRACOS, f"FRACOS (estilo seco) fora de dia: {sorted(fracos ^ FRACOS)}"
    cns = sem_tinta_do_despertar(cns)
    cns = cns.rstrip() + "\n\n" + efeitos_cns(a.ativos, fracos)
    assert "[Statedef -4]" not in cns, "o Pengaró ganhou um -4: a aura entra nele com cabecalho=False"
    aura.conferir(acoes=a.acoes, explods=re.findall(r"^\s*id\s*=\s*(\d+)", cns, re.M))
    cns = cns.rstrip() + "\n\n" + aura.cns(cabecalho=True)
    cns = cns.replace("[Data]", preset + "[Quotes]\n" + "".join(f'victory{i + 1} = "{v}"\n' for i, v in enumerate(VITORIAS)) + "\n[Data]", 1)
    (SAIDA / "pengaro.cns").write_text(cns, encoding="utf-8", newline="\n")
    air = (SAIDA / "pengaro.air").read_text(encoding="utf-8")
    # corpo em alta resolução (ferramentas/hd.py): os desenhos 3x de quadros_arcade_hd (ferramentas/hd_guiado.py)
    if QUADROS_ARCADE_HD.exists():
        import hd
        air, cns = hd.aplicar(s, air, cns, [(QUADROS_ARCADE, QUADROS_ARCADE_HD)], SPRITES_VITIMA)
        (SAIDA / "pengaro.air").write_text(air, encoding="utf-8", newline="\n")
        (SAIDA / "pengaro.cns").write_text(cns, encoding="utf-8", newline="\n")
    # agarrão em pé segura-e-bate (ferramentas/agarrao_mk.py): montado dos golpes que ele já tem, depois do HD
    air, cns = agarrao_mk.aplicar("pengaro", air, cns)
    (SAIDA / "pengaro.air").write_text(air, encoding="utf-8", newline="\n")
    (SAIDA / "pengaro.cns").write_text(cns, encoding="utf-8", newline="\n")
    escrever_sff(SAIDA / "pengaro.sff", s, manter=sprites_mantidos(air, cns))
    (SAIDA / "pengaro.cmd").write_text(montar_cmd(), encoding="utf-8")
    (SAIDA / "pengaro.def").write_text(DEF, encoding="utf-8", newline="\n")
    (SAIDA / "movelist.dat").write_text(GOLPES, encoding="utf-8", newline="\n")
    import parry  # parry em cima e embaixo, faísca própria e sem a "rede de futebol" (docs/parry.md)
    parry.aplicar("pengaro", SAIDA)
    import gerar_sons  # sons próprios: sound = pengaro.snd no .def e PlaySnd/hitsound no .cns (missão 2026-11-14)
    gerar_sons.ligar("pengaro", SAIDA)  # depois do parry: os estados 761/765 dele também tocam o som (F30)
    import balanceamento  # números do item 7 (attack, defence, velocidade)
    balanceamento.aplicar("pengaro", SAIDA)
    print(f"{len(s.lista)} sprites, {len(a.acoes)} ações em {SAIDA}")
    if SEM_FOLHA_BOSS:
        print("Endiabrado sem folha própria (pose emprestada do boss):", " ".join(sorted(SEM_FOLHA_BOSS)))


if __name__ == "__main__":
    main()
