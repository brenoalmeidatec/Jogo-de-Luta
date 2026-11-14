#!/usr/bin/env python3
"""Gera o Gutto (lutador de Muay Thai) reaproveitando o gerador do Pengaró.

O kit é o mesmo da regra dos lutadores (estados, correntes, kombos, 8 especiais, agarrões, Despertar), então este
arquivo só troca o que é do Pengaró: a arte (folhas do Gutto em sprites/gutto/quadros), o projétil (o Beijinho é um
coração), o agarrão de comando, os textos e os nomes dos arquivos. Tudo o mais vem de gerar_pengaro.py.

  python ferramentas/animar_folha.py ... (com LUTADOR=gutto)   corta as folhas e faz os quadros do meio
  python ferramentas/gerar_gutto.py                            monta chars/gutto
"""
import agarrao_mk
import re
import shutil
from pathlib import Path

import cv2
import numpy as np
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


# ---------------------------------------------------------------- anatomia: o que sai do gerador comum e é trocado aqui
# Ginga e andar só com DESENHOS segurados, sem os quadros de fluxo óptico das pastas ginga_fluida e anda_fluida (um
# desenho-chave a cada 8 e a cada 6 arquivos). O fluxo não seguia braço nem perna: ficava parado e trocava de pose num
# quadro só, e no meio da troca a luva virava borrão (lia como mão a mais). Os sprites continuam com o mesmo nome e
# número (q_ginga_fluida<i>, q_anda_fluida<i>); o .air só usa os dos desenhos, e o .sff só leva o que o .air usa.
# Ginga: desenhos 1, 2, 6 e 5. Ficam fora o 0, o 4 e o 7 (antebraço de trás levantado: o braço piscava para cima e para
# baixo 3 vezes por ciclo) e o 3 (único com o pé da frente no ar: um tropeço solto no meio do loop).
GINGA = ((1, 2, 6, 5), (9, 9, 9, 9))
# Andar: junta o pé de trás (1), abre a passada (2), puxa o pé de trás (3), planta (4). Os desenhos 5 e 6 repetem o
# "pé de trás colado no calcanhar" sem avançar e o 7 e o 0 repetem o 4: com eles o segundo passo quase não se mexia.
ANDA = ((1, 2, 3, 4), (6, 6, 6, 6))
# Forma de cavalo, desenho a desenho da ginga normal: só as chaves coerentes de ginga_endiabrada (00, 16, 48, 56). As
# chaves 08 e 40 (bufando) são mais altas e marrons que as outras e a 24 e a 32 têm farelo rosa no chão.
GINGA_CAVALO = {8: 0, 16: 16, 48: 48, 40: 56}
PASSO_GINGA, PASSO_ANDA = 8, 6
# Folha de cavalo cujo movimento é outro golpe: usa os desenhos de uma folha de cavalo que faz o movimento certo.
#   chute_alto: e_chute_alto é um coice de quatro patas para TRÁS (as patas iam para longe do oponente); e_compasso gira
#               de costas e solta o coice para a frente, na altura do golpe.
#   rasteirinha: e_rasteirinha fica em pé os 8 desenhos; e_rasteira agacha e varre com a perna rente ao chão.
FOLHA_CAVALO = {"chute_alto": ("e_compasso", (0, 1, 2, 3, 4, 5, 6, 7)),
                "rasteirinha": ("e_rasteira", (0, 0, 3, 4, 4, 3, 5, 7))}
# Intervalos (folha, desenho) sem quadro do meio, corte seco: derrota (os braços pulavam mão no peito -> abertos -> mão
# no peito no meio de cada intervalo; é pose segurada de fim de luta).
SEM_MEIO = {("derrota", i) for i in range(7)}
# Retoques por desenho, na tela do jogo (360x260): (x0, y0, x1, y1, modo). "pinta" cobre o pixel claro/rosado da caixa
# com a cor dos vizinhos (mancha em cima do corpo; "pinta_cinza" leva junto o risco cinza); "apaga" tira o pixel claro/rosado; "apaga_rosa" tira o que não é pele; "tudo" esvazia a caixa; "limpa" tira todo pixel de
# vermelho acima de 140 (farelo solto no chão, ao lado de casco escuro).
RETOQUES = {
    ("martelo", "05"): [(178, 146, 204, 160, "pinta")],  # rastro rosado do golpe pintado no abdômen
    ("martelo", "06"): [(160, 149, 194, 160, "pinta")],
    ("rolamento", "01"): [(181, 193, 193, 204, "apaga_rosa")],  # borrão rosa entre as mãos e embaixo do tronco
    ("rolamento", "02"): [(152, 194, 174, 210, "apaga_rosa"), (159, 197, 174, 211, "tudo")],
    ("ar_soco", "04"): [(175, 158, 193, 173, "pinta_cinza")],  # rabisco cinza no flanco, embaixo da braçadeira
    ("e_queda", "02"): [(180, 188, 200, 203, "pinta")],  # placa rosa no quadril
    ("e_levanta", "01"): [(208, 203, 222, 217, "pinta")],  # mancha creme junto aos cascos
    ("e_chute_baixo", "04"): [(186, 212, 221, 221, "limpa")],  # farelo rosa no chão
    ("e_provoca", "01"): [(205, 213, 221, 221, "limpa")],
    ("e_provoca", "02"): [(186, 211, 222, 221, "limpa")],
    ("endiabrado", "06"): [(200, 153, 213, 160, "apaga")],  # zigue-zague rosa acima do fogo
}


def _claro(a):
    r, g, b = (a[..., i].astype(int) for i in range(3))
    return (a[..., 3] >= 128) & ((r > 170) & (b > 115) & (r - g > 20) | (g > 150) & (b > 140))


def retocar(img, caixas):
    a = np.array(img)
    cheio = a[..., 3] >= 128
    for x0, y0, x1, y1, modo in caixas:
        dentro = np.zeros(a.shape[:2], bool)
        dentro[y0:y1, x0:x1] = True
        alvo = dentro & _claro(a)
        if modo == "limpa":
            a[dentro & (a[..., 0] > 140), 3] = 0
        elif modo == "tudo":  # caixa só com resto, sem corpo dentro
            a[dentro, 3] = 0
        elif modo == "apaga_rosa":  # tudo que não é pele (azul chegando no verde): borrão rosa e o contorno roxo dele
            a[dentro & cheio & (a[..., 2].astype(int) >= a[..., 1].astype(int) - 5), 3] = 0
        elif modo == "apaga":
            a[alvo, 3] = 0
        else:
            if modo == "pinta_cinza":  # risco cinza (sem cor) em cima da pele
                rgb = a[..., :3].astype(int)
                alvo |= dentro & cheio & (rgb.max(axis=2) > 100) & (rgb.max(axis=2) - rgb.min(axis=2) < 45)
            # só o corpo serve de fonte da cor: o vazio em volta ainda guarda o magenta da folha por baixo do alfa
            m = 8
            ys, xs = slice(max(0, y0 - m), y1 + m), slice(max(0, x0 - m), x1 + m)
            mascara = (cv2.dilate(alvo.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) | ~cheio)[ys, xs]
            a[ys, xs, :3] = cv2.inpaint(np.ascontiguousarray(a[ys, xs, :3]), mascara.astype(np.uint8) * 255, 3,
                                        cv2.INPAINT_TELEA)
    return Image.fromarray(a)


def _pasta_e_desenho(arquivo):
    """('queda', '04') para quadros/queda/04.png; ('queda', '03_4') para quadros/queda/meio/03_4.png."""
    meio = arquivo.parent.name == "meio"
    return (arquivo.parent.parent.name if meio else arquivo.parent.name), arquivo.stem


def _de_cavalo(pasta):
    return pasta.startswith("e_") or pasta in ("endiabrado", "ginga_endiabrada", "despertar_b")


_abrir_quadro = gp.abrir_quadro


def abrir_quadro(arquivo):
    """O Gutto normal não tem rosa nem magenta em lugar nenhum (pele, calção preto, faixa branca): tudo que aparece
    assim é resto do fundo magenta da folha (bloco preso entre o rosto e o punho no chute alto, dedos rosa na queda,
    borrão no rolamento) ou efeito pintado no corpo (o coração do Beijinho, que o jogo já solta como projétil)."""
    arquivo = Path(arquivo)
    img = _abrir_quadro(arquivo)
    pasta, desenho = _pasta_e_desenho(arquivo)
    if QUADROS in arquivo.parents and not _de_cavalo(pasta) and pasta != "despertar_a":
        img = gp.sem_rosa(img)
    caixas = RETOQUES.get((pasta, desenho))
    return gp.marcar_origem(retocar(img, caixas), arquivo) if caixas else gp.marcar_origem(img, arquivo)


gp.abrir_quadro = abrir_quadro

_arquivo_loop, _pasta_endiabrada = gp.arquivo_loop_endiabrado, gp.pasta_endiabrada
_chave_endiabrada, _par, _registra_meio, _caminho = (gp.arquivo_endiabrado_da_chave, gp.par_endiabrado,
                                                     gp.registra_meio, gp.caminho_fluido)


def arquivo_loop_endiabrado(pasta, i):
    if pasta == "ginga_fluida" and i in GINGA_CAVALO:
        return QUADROS / "ginga_endiabrada" / f"{GINGA_CAVALO[i]:02d}.png"
    return _arquivo_loop(pasta, i)


def pasta_endiabrada(pasta):
    return (FOLHA_CAVALO[pasta][0], 1) if pasta in FOLHA_CAVALO else _pasta_endiabrada(pasta)


def arquivo_endiabrado_da_chave(pasta, n):
    if pasta in FOLHA_CAVALO:
        outra, desenhos = FOLHA_CAVALO[pasta]
        return QUADROS / outra / f"{desenhos[n]:02d}.png"
    return _chave_endiabrada(pasta, n)


def par_endiabrado(nome):
    """Nas folhas trocadas o quadro do meio do cavalo vira o desenho-chave mais próximo (corte seco)."""
    meio = re.fullmatch(r"m_([a-z_]+?)_(\d+)_(\d+)", nome)
    if meio and meio[1] in FOLHA_CAVALO:
        n = int(meio[2]) + (1 if int(meio[3]) >= 4 else 0)
        return arquivo_endiabrado_da_chave(meio[1], n), meio[1], n
    return _par(nome)


def registra_meio(s, folha, intervalo, k):
    return None if (folha, intervalo) in SEM_MEIO else _registra_meio(s, folha, intervalo, k)


def caminho_fluido(s, atual, proximo):
    return [q for q in _caminho(s, atual, proximo) if q is not None]


gp.arquivo_loop_endiabrado, gp.pasta_endiabrada = arquivo_loop_endiabrado, pasta_endiabrada
gp.arquivo_endiabrado_da_chave, gp.par_endiabrado = arquivo_endiabrado_da_chave, par_endiabrado
gp.registra_meio, gp.caminho_fluido = registra_meio, caminho_fluido

_acoes_folhas = gp.acoes_folhas


def acoes_folhas(Q):
    """As ações que mudam no Gutto vêm antes das do gerador comum: a primeira definição de cada ação é a que vale."""
    ginga = [(f"q_ginga_fluida{PASSO_GINGA * d}", t) for d, t in zip(*GINGA)]
    anda = [(f"q_anda_fluida{PASSO_ANDA * d}", t) for d, t in zip(*ANDA)]
    Q(0, ginga)
    Q(9203, [(nome.replace("q_ginga_fluida", "ginga_endiabrada"), t) for nome, t in ginga])
    Q(5, [(ginga[0][0], 6)])  # virar
    Q(20, anda)
    Q(21, anda[::-1])
    Q(100, [(nome, 3) for nome, _ in anda])  # correr: os mesmos desenhos na metade do tempo
    # Despertar: despertar_a termina com a cabeça de cavalo pronta e despertar_b recomeçava do humano de bigode (0) e
    # de um cavalo claro (1): a cabeça virava cavalo, voltava a ser gente e virava cavalo de novo. Emenda o a7 no b2
    # (já cavalo, ainda de pés humanos). Mesma duração de antes (114 ticks).
    f = lambda folha, i: f"f_{folha}{i}"
    Q(2000, [(f("despertar_a", i), 7) for i in range(7)] + [(f("despertar_a", 7), 6)]
          + [(f("despertar_b", i), t) for i, t in ((2, 10), (3, 10), (4, 10), (5, 10), (6, 9), (7, 10))])
    _acoes_folhas(Q)


gp.acoes_folhas = acoes_folhas


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
    cns = gp.super_3100_endiabrado(gp.sem_ginga_9203(gp.remapear_animelem(gp.montar_cns(), a.mapas)))
    # a aura do demônio cavalo pulsa em vermelho de brasa, não no violeta do Pengaró
    cns = cns.replace("add = 12, 0, 28", "add = 16, 0, 0").replace("sinadd = 10, 0, 18, 40", "sinadd = 14, 2, 0, 40")
    cns = cns.replace("[Data]", preset + "[Quotes]\n" + "".join(
        f'victory{i + 1} = "{v}"\n' for i, v in enumerate(gp.VITORIAS)) + "\n[Data]", 1)
    air = "\n".join(a.txt)
    # corpo em alta resolução (ferramentas/hd.py): os mesmos quadros em 3x, de quadros_hd/ (animar_folha.py com HD=3)
    if (QUADROS.parent / "quadros_hd").exists():
        import hd
        air, cns = hd.aplicar(s, air, cns, [(QUADROS, QUADROS.parent / "quadros_hd")], gp.SPRITES_VITIMA,
                              gemeos=gp.GEMEOS_HD)
        (SAIDA / "gutto.air").write_text(air, encoding="utf-8", newline="\n")
    else:
        print("ATENÇÃO: sem sprites/gutto/quadros_hd (fica fora do git: ~200-340 MB). O lutador sai em 1x, borrado. "
              "Gere com: python ferramentas/hd_blender.py gutto  (uns 20 min; depois rode este gerador de novo)")
    # agarrão em pé segura-e-bate (ferramentas/agarrao_mk.py): montado dos golpes que ele já tem, depois do HD
    air, cns = agarrao_mk.aplicar("gutto", air, cns)
    (SAIDA / "gutto.air").write_text(air, encoding="utf-8", newline="\n")
    (SAIDA / "gutto.cns").write_text(cns, encoding="utf-8", newline="\n")
    gp.escrever_sff(SAIDA / "gutto.sff", s, manter=gp.sprites_mantidos(air, cns))
    (SAIDA / "gutto.cmd").write_text(gp.montar_cmd(), encoding="utf-8")
    (SAIDA / "gutto.def").write_text(DEF, encoding="utf-8", newline="\n")
    import gerar_sons  # sons próprios: sound = gutto.snd no .def e PlaySnd/hitsound no .cns (missão 2026-11-14)
    gerar_sons.ligar("gutto", SAIDA)
    (SAIDA / "movelist.dat").write_text(GOLPES, encoding="utf-8", newline="\n")
    import parry  # parry em cima e embaixo, faísca própria e sem a "rede de futebol" (docs/parry.md)
    parry.aplicar("gutto", SAIDA)
    import legibilidade  # golpes legíveis (#45): caixa no membro, congelamento, tremida, reação e preparo
    legibilidade.aplicar("gutto", SAIDA)
    import balanceamento  # números do item 7 (attack, defence, velocidade)
    balanceamento.aplicar("gutto", SAIDA)
    print(f"{len(s.lista)} sprites, {len(a.acoes)} ações em {SAIDA}")


if __name__ == "__main__":
    main()
