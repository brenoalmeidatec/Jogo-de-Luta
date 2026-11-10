#!/usr/bin/env python3
"""Gera o Gutto (lutador de Muay Thai) reaproveitando o gerador do Pengaró.

O kit é o mesmo da regra dos lutadores (estados, correntes, kombos, 8 especiais, agarrões, Despertar), então este
arquivo só troca o que é do Pengaró: a arte (folhas do Gutto em sprites/gutto/quadros), o projétil (o Beijinho é um
coração), o agarrão de comando, os textos e os nomes dos arquivos. Tudo o mais vem de gerar_pengaro.py.

  python ferramentas/animar_folha.py ... (com LUTADOR=gutto)   corta as folhas e faz os quadros do meio
  python ferramentas/gerar_gutto.py                            monta chars/gutto
"""
import shutil

from PIL import Image, ImageDraw

import gerar_pengaro as gp

RAIZ = gp.RAIZ
SAIDA = RAIZ / "chars/gutto"
QUADROS = RAIZ / "sprites/gutto/quadros"

gp.SAIDA = SAIDA
gp.QUADROS = QUADROS


# ---------------------------------------------------------------- Beijinho: o projétil é um coração em pixel art
def coracao(escala=2, cor=("#ff5fa2", "#ffc2dc", "#5a0f2e")):
    """Coração de 13x11 pixels: miolo, brilho e contorno escuro."""
    fundo, brilho, contorno = (tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (255,) for c in cor)
    w, h = 13, 11
    mapa = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            u, v = (x - 6) / 5.6, (4.6 - y) / 4.4  # u para os lados, v para cima, mais ou menos de -1 a 1
            mapa[y][x] = (u * u + v * v - 1) ** 3 - u * u * v ** 3 <= 0
    img = Image.new("RGBA", (w + 2, h + 2))
    px = img.load()
    for y in range(h):
        for x in range(w):
            if mapa[y][x]:
                px[x + 1, y + 1] = fundo
    for y in range(h + 2):
        for x in range(w + 2):
            if px[x, y][3] == 0 and any(0 <= x + dx < w + 2 and 0 <= y + dy < h + 2 and px[x + dx, y + dy] in (fundo, brilho)
                                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = contorno
    for x, y in ((3, 3), (4, 3), (3, 4)):
        if px[x, y] == fundo:
            px[x, y] = brilho
    return img.resize((img.width * escala, img.height * escala), Image.NEAREST)


class Itens:
    """No lugar do itens_pengaro: nada de lata nem garrafa; o Gutto lança corações e não segura nada."""

    @staticmethod
    def lata():
        return coracao(2)

    @staticmethod
    def garrafa():
        return coracao(2, ("#ff3b7f", "#ffb3cf", "#4a0a26"))

    @staticmethod
    def latas_girando(escala=2):
        c = coracao(escala, ("#e8366c", "#ff9ec0", "#3d0820"))
        return [c, c.transpose(Image.ROTATE_270), c.transpose(Image.ROTATE_180), c.transpose(Image.ROTATE_90)]

    @staticmethod
    def com_whisky(img):
        return img


gp.itens_pengaro = Itens


# ---------------------------------------------------------------- poses-base, tiradas das folhas do Gutto
def carregar_poses():
    """As 9 poses que o gerador espera (parado, andando, defesa...), cada uma de um desenho das folhas."""
    def desenho(pasta, i):
        return gp.abrir_quadro(QUADROS / pasta / f"{i:02d}.png")

    p = {"parado": desenho("ginga", 0), "andando": desenho("anda", 2), "andando2": desenho("anda", 6),
         "defesa": desenho("defesa", 3), "apanhando": desenho("apanha", 3), "agachado": desenho("agachado", 6),
         "pulo": desenho("pulo", 3), "soco": desenho("soco", 5), "chute": desenho("chute_alto", 4),
         "rasteira": desenho("rasteira", 4), "especial": desenho("bola", 4)}
    return p, Itens.lata()


gp.carregar_poses = carregar_poses

# ---------------------------------------------------------------- Agarrão de comando: clinch, joelhada e empurrão
# (o do Pengaró é compasso + garrafa de whisky). Índices 5 e 10 são o contato e o empurrão final, como no do Pengaró.
gp.AGARRAO_WHISKY = [("agarrao", 2, 3), ("agarrao", 3, 3),
                     ("cabecada", 1, 4), ("cabecada", 2, 4), ("cabecada", 3, 4), ("cabecada", 4, 2), ("cabecada", 5, 3),
                     ("cabecada", 6, 4), ("cabecada", 7, 4),
                     ("afastar", 2, 5), ("afastar", 4, 4), ("afastar", 5, 4), ("afastar", 6, 4), ("afastar", 7, 4)]


def cns_agarrao_clinch():
    """Clinch de Muay Thai: pega, joelhada (60) e empurrão de teep que joga o oponente (90). Mesmos estados 830 a 833."""
    texto = gp.cns_agarrao_whisky_original()
    # sem garrafa: tira o Explod que fazia a garrafa cair
    inicio = texto.index("[State 831, Garrafa]")
    fim = texto.index("[State 831, Whisky dano]")
    return texto[:inicio] + texto[fim:]


gp.cns_agarrao_whisky_original = gp.cns_agarrao_whisky
gp.cns_agarrao_whisky = cns_agarrao_clinch

# ---------------------------------------------------------------- textos
gp.VITORIAS = [
    "Foi na ginga do Muay Thai, parceiro!",
    "Quer outra? É só pedir.",
    "Chute baixo não perdoa, né?",
    "Beijinho de despedida!",
    "Tu caiu igual a cavalo de carrossel.",
    "Treino de verdade é na canela.",
    "Essa vai na conta do Gutto.",
    "Levanta que eu dou mais uma.",
]

DEF = """; Gerado por ferramentas/gerar_gutto.py. Edite lá, não aqui.
[Info]
name = "Gutto"
displayname = "Gutto"
versiondate = 11,06,2026
mugenversion = 1.1
author = "Breno"
pal.defaults = 1
localcoord = 320,240

[Files]
cmd = gutto.cmd
cns = gutto.cns
st = gutto.cns
stcommon = common1.cns
sprite = gutto.sff
anim = gutto.air
movelist = movelist.dat

[Palette Keymap]
x = 1
"""

GOLPES = """<#f0f000>:Especiais:</>
Beijinho (reto) <#bebebe>(projétil)</>			_D_F^K
Chute Giratório (coice)				_D_B^K
Joelhada Voadora					_F_D^P
Carrinho							_D_B^P
Cotovelo Giratório / Cotovelada Pesada	_D_F^P
Chute de Quina / Pisão de Quina		_B_D^K
Beijinho em Arco <#bebebe>(projétil em arco)</>	_F_B^P
Teleporte de Ginga (a passa, b passa e chuta)	_F_B^K

<#f0f000>:Exclusivos do Endiabrado:</>
Beijo do Cavalo <#bebebe>(projétil)</>	_D_D^X
Coice da Corrente					_D_D^Y
Galope Atravessado					_D_D^A
Queda do Cavalo						_D_D^B
Corrente Y e B de 4 golpes			^Y^Y^Y^Y / ^B^B^B^B
Kombo do Cavalo						^B,^A,^X

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
Chuva de Beijinhos <#bebebe>(1000)</>	_B_F_D^K
Saideira do Cavalo (no Endiabrado)	_B_F_D^K
Bando de Chutes / Fúria do Cavalo	_B_F_D^P

<#f0f000>:Sistema:</>
Endiabrado <#bebebe>(barra cheia)</>	^X_+^Y
Rolamento							^X_+^A
Golpe de afastar (teep)				^Y_+^B
Agarrão								[_B/_F]_+^Y
Agarrão agachado <#bebebe>(oponente agachado)</>	_D_+^Y
Clinch e Joelhada <#bebebe>(colado)</>		_B_F^Y
Provocação							^C
Parry                              _F^C
"""

gp.DEF = DEF
gp.GOLPES = GOLPES


def provisorio_endiabrado():
    """PROVISÓRIO: as 8 poses da forma de cavalo ainda não foram desenhadas (o ChatGPT bloqueou imagens por hoje).
    Enquanto isso, as poses normais saem escurecidas e avermelhadas. Apague a pasta quando a folha `endiabrado` chegar
    e rode animar_folha com ela (pedido em folhas_gutto.py)."""
    destino = QUADROS / "endiabrado"
    destino.mkdir(parents=True)
    poses = [("ginga", 0), ("anda", 2), ("agachado", 6), ("soco", 5), ("chute_alto", 4), ("cabecada", 4), ("bola", 4),
             ("pulo", 3)]
    for i, (pasta, n) in enumerate(poses):
        img = Image.open(QUADROS / pasta / f"{n:02d}.png").convert("RGBA")
        r, g, b, a = img.split()
        img = Image.merge("RGBA", (r.point(lambda v: int(v * .78)), g.point(lambda v: int(v * .42)),
                                   b.point(lambda v: int(v * .5)), a))
        img.save(destino / f"{i:02d}.png")
    print("PROVISÓRIO: poses do Endiabrado escurecidas; falta a arte do cavalo")


def preparar_pastas():
    """Loops que o gerador lê e ainda não têm arte própria: a ginga do Endiabrado começa igual à normal."""
    destino = QUADROS / "ginga_endiabrada"
    origem = QUADROS / "ginga_fluida"
    if not destino.exists() and origem.exists():
        shutil.copytree(origem, destino)
    if not (QUADROS / "endiabrado").exists():
        provisorio_endiabrado()


def main():
    preparar_pastas()
    SAIDA.mkdir(parents=True, exist_ok=True)
    s = gp.montar_sprites()
    faiscas = gp.carregar_faiscas(s)
    a = gp.montar_air(s, faiscas, arte_despertada=gp.arte_endiabrada(s))
    preset = gp.preset_despertado(s)
    (SAIDA / "gutto.air").write_text("\n".join(a.txt), encoding="utf-8", newline="\n")
    cns = gp.remapear_animelem(gp.montar_cns(), a.mapas)
    # a aura do demônio cavalo pulsa em vermelho de brasa, não no violeta do Pengaró
    cns = cns.replace("add = 12, 0, 28", "add = 16, 0, 0").replace("sinadd = 10, 0, 18, 40", "sinadd = 14, 2, 0, 40")
    cns = cns.replace("[Data]", preset + "[Quotes]\n" + "".join(
        f'victory{i + 1} = "{v}"\n' for i, v in enumerate(gp.VITORIAS)) + "\n[Data]", 1)
    (SAIDA / "gutto.cns").write_text(cns, encoding="utf-8", newline="\n")
    gp.escrever_sff(SAIDA / "gutto.sff", s, manter=gp.sprites_mantidos("\n".join(a.txt), cns))
    (SAIDA / "gutto.cmd").write_text(gp.montar_cmd(), encoding="utf-8")
    (SAIDA / "gutto.def").write_text(DEF, encoding="utf-8", newline="\n")
    (SAIDA / "movelist.dat").write_text(GOLPES, encoding="utf-8", newline="\n")
    print(f"{len(s.lista)} sprites, {len(a.acoes)} ações em {SAIDA}")


if __name__ == "__main__":
    main()
