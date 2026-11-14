#!/usr/bin/env python3
"""Gera o Hazak (chars/hazaki): karatê de quebrada com perna de taekwondo, o mais rápido do elenco.

Gerador próprio. Importa o gerar_pengaro só como biblioteca (Sprites, gravar_sff, estado, hitdef, fim, superpausa,
reversao, comando, entrada, ajustar_clsn1, faíscas do pixelfx) e NÃO chama montar_sprites/air/cns/cmd: o Hazak não
herda nenhum golpe do Pengaró. A tabela de golpes está em ferramentas/hazaki_golpes.py; a arte vem de
sprites/hazaki/quadros_arcade/<folha>/00..07.png (ferramentas/folhas_hazak_arcade.py), 360x260, pés em (180, 220),
15 cores exatas (sprites/hazaki/paleta_arcade.json), que o .sff guarda nos índices 1 a 15 da paleta.

  python ferramentas/gerar_hazaki.py                 monta chars/hazaki
  python ferramentas/gerar_hazaki.py --contato DIR   e grava em DIR folhas de contato dos sprites lidos do .sff

O Despertar (Diabo Loiro) NÃO entra: as folhas d_* não existem. Não há comando `despertar` nem estado 2000; var(20)
fica sempre 0. Ficha: docs/fichas/hazaki.md. Especificação e pendências: docs/arcade/hazak_gerador.md.
"""
import agarrao_mk
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import gerar_pengaro as gp
import hazaki_golpes as hg

RAIZ = gp.RAIZ
SAIDA = RAIZ / "chars/hazaki"
QUADROS = RAIZ / "sprites/hazaki/quadros_arcade"
PALETA = RAIZ / "sprites/hazaki/paleta_arcade.json"
OBJETOS = ("obj_lasca", "obj_estatueta")
# folhas do corpo: tudo menos a patroa (só entra na cena do Despertar) e os objetos
FOLHAS = tuple(sorted(p.name for p in QUADROS.iterdir()
                      if p.is_dir() and not p.name.startswith(("patroa_", "obj_"))))

# ---------------------------------------------------------------- o que o gerar_pengaro lê na hora da chamada
gp.SAIDA = SAIDA
gp.QUADROS = QUADROS
gp.FOLHAS = FOLHAS
gp.TROCA_POR_FOLHA = {}
gp.SEGUINTE = {}
gp.ULTIMO_DESENHO = {}
gp.ATAQUES_DESPERTADOS = set()          # sem variante +10000 nem ChangeAnim de arte despertada
gp.PROJETEIS = {1005, 1605}
gp.RITMO = gp.RITMO_PREPARO = 1.0       # os ticks de hazaki_golpes.py são os ticks do jogo
gp.FRACOS = {g.n for g in hg.NORMAIS + hg.CORRENTES + hg.KOMBOS if g.classe == "fraco"}
gp.BALOES_LIGADOS = False
# efeitos do pixelfx (assets/efeitos): acerto fraco, crítico, parry, asfalto, soco seco, subida, poeira de pé no chão
# e defesa. O charge-up entra com o Despertar; o hit-flash não é usado.
gp.FAISCAS = {9200: "hit-spark", 9201: "crit-hit", 9205: "ground-slam", 9207: "blunt-hit",
              9208: "uppercut", 9209: "heavy-landing", 9216: "shield-block"}
# classe -> (pausetime, guard.pausetime, envshake, fall.envshake, faísca, sparkscale, hitsound)
gp.IMPACTO = {
    "fraco": ((7, 7), (6, 6), None, None, 9200, 1, "5,0"),
    "forte": ((11, 11), (9, 9), None, None, 9207, 1.1, "5,2"),
    "especial": ((12, 12), (9, 9), None, None, 9207, 1.15, "5,2"),
    "final": ((14, 14), (10, 10), (12, 150, -3), (8, 150, -2), 9201, 1.3, "5,3"),
    # contra-ataque (resposta da Guarda de Aço): crit-hit e congelamento de finalizador, sem tremida (regra 8.3:
    # tremida só no finalizador de corrente e no golpe final de super)
    "contra": ((14, 14), (10, 10), None, None, 9201, 1.3, "5,3"),
    "super": ((3, 6), (2, 6), None, None, 9207, 1, "5,1"),
    "super_final": ((16, 16), (12, 12), (20, 150, -3), (12, 150, -2), 9201, 1.5, "5,4"),
}
gp.faiscas = lambda n: (f"sparkno = S{n}", "guard.sparkno = S9216")   # a defesa é sempre o escudo (regra 8.1)
gp.FAISCA_POR_FORMA = False
gp.MODO_HAZAKI = False

CORPO = gp.CORPO
AGACHADO = [(-26, 0, 26, -64)]
NO_AR = gp.NO_AR
DEITADO = [(-54, 0, 54, -30)]
AREA = {"S": CORPO, "C": AGACHADO, "A": NO_AR}

# A conversão centra pela caixa (e não pelo tronco) a figura mais larga que 1,45 x a altura: nestes desenhos o corpo
# pulava 21 a 28 px para trás bem no contato. O gerador devolve o deslocamento ao registrar o sprite.
DESLOCA = {("rasteira", 3): 22, ("rasteira", 4): 28, ("rasteira", 5): 27, ("rasteira_arco", 4): 21,
           ("rasteira_arco", 5): 21}

# Desenhos que os OUTROS lutadores pedem ao arremessar o Hazak (ChangeAnim2 nas ações 5001 e 5030 do .air deles):
# grupo -> (folha, desenho). Todo grupo de gp.SPRITES_VITIMA tem de existir, senão o arremessado some.
VITIMA_PRESO = ("vitima_agarrado", 1)       # preso de pé, corpo para trás, braços abertos
VITIMA = {48: ("vitima_agarrado", 0), 49: VITIMA_PRESO, 50: ("apanha", 3),
          382: ("vitima_agarrado", 0), 390: ("vitima_agarrado", 0),
          384: VITIMA_PRESO, 392: VITIMA_PRESO, 385: ("apanha", 2), 393: ("apanha", 2),
          386: ("apanha", 3), 394: ("apanha", 3)}

# Desenhos de quem está no ar. A conversão assenta todo desenho no chão (o pixel mais baixo no eixo), então no pulo
# os pés ficavam presos e era a cabeça que descia 47 px quando ele encolhia as pernas. Aqui o desenho sobe até o meio
# do corpo ficar em CENTRO_NO_AR (o desenho esticado, de corpo inteiro, não sai do lugar). A caixa de golpe sobe junto.
NO_AR_CENTRADO = {"pulo": range(1, 7)}
CENTRO_NO_AR = 60


def subida_no_ar(folha, i, img):
    if not (folha.startswith("ar_") or i in NO_AR_CENTRADO.get(folha, ())):
        return 0
    caixa = img.getbbox()
    return max(0, round(CENTRO_NO_AR - (caixa[3] - caixa[1]) / 2)) if caixa else 0


# Estatueta Dourada em voo. Na mão (folha estatueta_arremesso) ela mede ~14 px e não tem base; a folha obj_estatueta
# traz a estatueta com ~26 px e uma base azul-marinho, e ela "crescia" ao sair da mão. O projétil perde a base, encolhe
# para o tamanho da mão e ganha o brilho dourado da ficha (um cintilar que troca de canto a cada desenho).
PELE_E_DEBRUM = ((122, 46, 38), (176, 79, 48), (222, 132, 72), (246, 180, 104), (252, 217, 160), (216, 102, 28),
                 (142, 58, 26))
ESCALA_ESTATUETA = .6
OURO, OURO_CLARO = (255, 214, 96), (255, 250, 214)


def estatueta_em_voo(img, i):
    a = np.array(img.convert("RGBA"))
    fica = np.zeros(a.shape[:2], bool)
    for c in PELE_E_DEBRUM:
        fica |= (a[..., :3] == c).all(-1)
    a[~fica] = 0
    fig = Image.fromarray(a)
    fig = fig.crop(fig.getbbox())
    fig = fig.resize((max(1, round(fig.width * ESCALA_ESTATUETA)), max(1, round(fig.height * ESCALA_ESTATUETA))),
                     Image.Resampling.NEAREST)
    tela = Image.new("RGBA", (gp.LARG, gp.ALT))
    cx, cy = gp.EIXO_X, gp.EIXO_Y - 10
    tela.alpha_composite(fig, (cx - fig.width // 2, cy - fig.height // 2))
    d = ImageDraw.Draw(tela)
    # cintilar de 4 pontas: grande num canto nos desenhos pares, pequeno no canto oposto nos ímpares
    lado, braco = ((1, -1), 3) if i % 2 == 0 else ((-1, 1), 2)
    sx, sy = cx + lado[0] * (fig.width // 2), cy + lado[1] * (fig.height // 2)
    d.line((sx - braco, sy, sx + braco, sy), fill=OURO + (255,))
    d.line((sx, sy - braco, sx, sy + braco), fill=OURO + (255,))
    d.point((sx, sy), fill=OURO_CLARO + (255,))
    return tela


VITIMA_PRESA, VITIMA_ENCOLHE = 5930, 5931  # ações do .air do Hazak que rodam no oponente agarrado

DEF = """; Gerado por ferramentas/gerar_hazaki.py. Edite lá, não aqui.
[Info]
name = "Hazak"
displayname = "Hazak"
versiondate = 11,11,2026
mugenversion = 1.1
author = "Breno"
pal.defaults = 1
localcoord = 320,240

[Files]
cmd = hazaki.cmd
cns = hazaki.cns
st = hazaki.cns
stcommon = common1.cns
sprite = hazaki.sff
anim = hazaki.air
movelist = movelist.dat

[Palette Keymap]
x = 1
"""


# ---------------------------------------------------------------- leitura da notação "folha d/t d/tA"
def ler(texto, clsn1=None):
    """[(nome do sprite, ticks, caixa de golpe ou None)]"""
    folha, saida = None, []
    for p in texto.split():
        if "/" not in p:
            folha = p
            continue
        d, t = p.split("/", 1)
        ativo = t.endswith("A")
        saida.append((f"f_{folha}{int(d)}", int(t.rstrip("A")), clsn1 if ativo else None))
    return saida


def ativos(quadros):
    """Trechos com caixa de golpe, em ticks: [(primeiro tick, tick seguinte ao último)]."""
    saida, t = [], 0
    for nome, ticks, caixa in quadros:
        if caixa:
            if saida and saida[-1][1] == t:
                saida[-1] = (saida[-1][0], t + ticks)
            else:
                saida.append((t, t + ticks))
        t += max(ticks, 0)
    return saida


def duracao(quadros):
    return sum(max(t, 0) for _, t, _ in quadros)


def anim(n):
    texto, caixa, area = hg.ANIM[n]
    return ler(texto, caixa), AREA[area]


def acerto(n, k=0):
    """Tick em que o k-ésimo trecho ativo da animação n começa."""
    return ativos(anim(n)[0])[k][0]


def fim_ativo(n):
    return ativos(anim(n)[0])[-1][1]


# ---------------------------------------------------------------- sprites
def carregar_paleta():
    return [tuple(c["rgb"]) for c in json.loads(PALETA.read_text(encoding="utf-8"))["cores"]]


def montar_sprites():
    s = gp.Sprites()
    s.folhas = False
    s.proximo = 1000
    s.subida = {}  # nome do sprite -> quantos px o desenho subiu (NO_AR_CENTRADO)
    desenho = lambda folha, i: Image.open(QUADROS / folha / f"{i:02d}.png").convert("RGBA")

    # retratos (menu e barras)
    retrato = RAIZ / "sprites/hazaki-selecao-kof.png"
    parado = desenho("parado", 0)
    rosto = parado.crop((gp.EIXO_X - 24, gp.EIXO_Y - 112, gp.EIXO_X + 32, gp.EIXO_Y - 56))
    busto = parado.crop((gp.EIXO_X - 60, gp.EIXO_Y - 118, gp.EIXO_X + 60, gp.EIXO_Y + 22))
    if retrato.exists():
        rosto = Image.open(retrato).convert("RGBA")
        rosto = rosto.crop(rosto.getbbox())
        busto = rosto.copy()
        busto.thumbnail((120, 140), Image.Resampling.LANCZOS)
        lado = min(rosto.size)
        x = (rosto.width - lado) // 2
        rosto = rosto.crop((x, 0, x + lado, lado))
    s.add("retrato_p", rosto.resize((25, 25), Image.Resampling.LANCZOS), 9000, 0, (0, 0))
    s.add("retrato_g", busto, 9000, 1, (0, 0))

    for folha in FOLHAS:
        for i in range(8):
            img = desenho(folha, i)
            if (folha, i) in DESLOCA:
                img = gp.move(img, DESLOCA[folha, i], 0)
            sobe = subida_no_ar(folha, i, img)
            if sobe:
                img = gp.move(img, 0, -sobe)
                s.subida[f"f_{folha}{i}"] = sobe
            s.add(f"f_{folha}{i}", img)
    s.add("f_agachado4r", gp.move(desenho("agachado", 4), -4, 0))  # apanhando agachado (provisório): recua 4 px

    # vítima de arremesso dos outros lutadores: grupos fixos
    for grupo, _ in sorted(gp.SPRITES_VITIMA):
        folha, i = VITIMA.get(grupo, VITIMA_PRESO)
        s.add(f"vit{grupo}", desenho(folha, i), grupo=grupo, indice=0)

    # projéteis (provisórios: saem das folhas obj_, não do pixelfx)
    for i in range(8):
        s.add(f"fx_lasca{i}", desenho("obj_lasca", i))
        s.add(f"fx_estatueta{i}", estatueta_em_voo(desenho("obj_estatueta", i), i))
    return s


CENTRADAS = (9200, 9201, 9207, 9216)  # faíscas de acerto, defesa e parry
DESENHOS_DA_POEIRA = 28
POEIRA = ((0, (14, 12, 10)), (.5, (118, 108, 98)), (1, (244, 236, 222)))  # asfalto: o ground-slam do pixelfx é azul


def carregar_faiscas(s):
    """Efeitos do pixelfx. Eles têm transparência suave e o SFF só guarda pixel cheio ou vazio: crus, o clarão vira
    um bloco branco e a fumaça vira pontilhado. Todos vão com a transparência embutida na cor e mistura aditiva
    (o escuro some), como o gerar_pengaro já faz com os efeitos grandes."""
    acoes = gp.carregar_faiscas(s)
    for k, (g, i, img, ex, ey) in enumerate(s.lista):
        if g not in gp.FAISCAS:
            continue
        if g not in gp.TRANS_FX:
            img = gp.efeito_aditivo(img)
        if g in (9205, 9209):
            img = gp.pintar(img, POEIRA)
        s.lista[k] = (g, i, img, ex, ey)
    for g in gp.FAISCAS:
        gp.TRANS_FX[g] = "A"
    # Faísca de acerto: o pivô do pixelfx fica embaixo do desenho e o clarão saía ~27 px acima do ponto do golpe
    # (um chute no peito faiscava na cabeça). O pivô passa a ser o centro do clarão do 1º desenho.
    for g in CENTRADAS:
        primeiro = next(img for gg, i, img, _, _ in sorted(s.lista, key=lambda e: e[:2])
                        if gg == g and img.getchannel("A").getbbox())
        luz = np.asarray(primeiro.convert("RGB")).sum(axis=2).astype(np.float64)
        ys, xs = np.indices(luz.shape)
        centro = (round(float((xs * luz).sum() / luz.sum())), round(float((ys * luz).sum() / luz.sum())))
        for k, (gg, i, img, _, _) in enumerate(s.lista):
            if gg == g:
                s.lista[k] = (gg, i, img, *centro)
    acoes[9205] = acoes[9205][:DESENHOS_DA_POEIRA]  # a poeira do pixelfx fica 3 s na tela: corta em ~1 s
    acoes[9209] = acoes[9209][:22]  # poeira do pé: só a nuvem subindo e abrindo
    # desenhos vazios no fim do efeito (o pixelfx termina em transparente): eram 4 a 18 ticks de nada na tela
    vazio = {(g, i) for g, i, img, _, _ in s.lista if g in gp.FAISCAS and not img.getchannel("A").getbbox()}
    for lista in acoes.values():
        while len(lista) > 1 and s.codigos[lista[-1][0]] in vazio:
            lista.pop()
    return acoes


def escrever_sff(destino, s, manter):
    """SFF com paleta fixa: os índices 1 a 15 são as 15 cores do Hazak (o corpo sai com a cor exata) e o resto da
    paleta (240 cores) é escolhido dos sprites que não são corpo (faíscas do pixelfx, retratos). Poda como o
    gp.escrever_sff: só ficam os sprites de `manter` e o grupo 9000."""
    fixas = carregar_paleta()
    assert len(fixas) == 15
    indice_fixo = {c: k + 1 for k, c in enumerate(fixas)}
    usados = [(g, i, img, ex, ey) for g, i, img, ex, ey in s.lista if g == 9000 or (g, i) in manter]

    def cores(img):
        a = np.asarray(img.convert("RGBA"))
        return a[a[..., 3] >= 128][:, :3]

    def e_corpo(img):
        c = cores(img)
        return len(c) > 0 and {tuple(v) for v in np.unique(c, axis=0)} <= set(fixas)

    livres = [cores(img) for _, _, img, _, _ in usados if not e_corpo(img)]
    resto = []
    if livres:
        amostra = np.concatenate(livres)
        passo = max(1, len(amostra) // gp.LIMITE_AMOSTRA_PALETA)
        tira = Image.fromarray(np.ascontiguousarray(amostra[::passo])[None, :, :], "RGB")
        q = tira.quantize(colors=240, method=Image.MEDIANCUT).getpalette()[:240 * 3]
        resto = [tuple(q[k:k + 3]) for k in range(0, len(q), 3)]
    pal = fixas + resto
    pal += [(0, 0, 0)] * (255 - len(pal))
    dados_pal = bytes((0, 0, 0, 0)) + b"".join(bytes((r, g, b, 255)) for r, g, b in pal)
    # O que não é corpo (efeito, retrato, estatueta em voo) só usa os índices 16 a 255: os 15 primeiros são do corpo
    # e vão trocar de cor com a paleta do Despertar.
    molde = Image.new("P", (1, 1))
    livre = resto + [resto[-1] if resto else (0, 0, 0)] * (256 - len(resto))
    molde.putpalette([v for c in livre for v in c])

    itens = []
    for grupo, indice, img, ex, ey in usados:
        caixa = img.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox() or (0, 0, 1, 1)
        rec = img.crop(caixa)
        a = np.asarray(rec.convert("RGBA"))
        opaco = a[..., 3] >= 128
        if e_corpo(img):
            px = np.zeros(opaco.shape, np.uint8)
            for cor, k in indice_fixo.items():
                px[opaco & (a[..., 0] == cor[0]) & (a[..., 1] == cor[1]) & (a[..., 2] == cor[2])] = k
        else:
            ind = np.asarray(rec.convert("RGB").quantize(palette=molde, dither=Image.NONE)).astype(np.int32)
            ind[ind >= len(resto)] = len(resto) - 1
            px = np.where(opaco, ind + 16, 0).astype(np.uint8)
        itens.append((grupo, indice, rec.width, rec.height, ex - caixa[0], ey - caixa[1], px.tobytes()))
    gp.gravar_sff(destino, dados_pal, itens)
    return len(itens)


# ---------------------------------------------------------------- AIR
MINIMO_DO_MEMBRO = 60  # pixels: menos que isso para fora do tronco (ponta de faixa, dedo) não ganha caixa de dano
SAIDA_DO_MEMBRO = 14   # px além do tronco: menos que isso (punho da guarda, pé da base) fica só com a caixa do tronco


def caixas_do_corpo(img, ex, ey):
    """Caixas de dano (Clsn2) medidas no desenho: uma no tronco (as colunas cheias: 45% ou mais da coluna mais alta)
    e uma em cada membro que sai dele 14 px ou mais para a frente ou para trás (perna do chute, braço do soco; o punho
    da guarda e o pé da base não contam: parado, a caixa fica quase igual à antiga de 48 px). Antes cada ação
    tinha uma caixa só, do tipo em pé / agachado / no ar: a joelhada subindo ficava com a cabeça e o tronco sem caixa
    e a perna esticada de qualquer chute nunca podia ser acertada."""
    ys, xs = np.nonzero(np.asarray(img.getchannel("A")) >= 128)
    if not len(xs):
        return []
    x, y = xs - ex, ys - ey
    cheias = np.bincount(x - x.min())
    fortes = np.nonzero(cheias >= .45 * cheias.max())[0] + x.min()
    x1, x2 = int(fortes.min()), int(fortes.max())
    meio = (x >= x1) & (x <= x2)
    caixas = [(x1, min(int(y[meio].max()) + 1, 0), x2, int(y[meio].min()) + 2)]
    for lado in (x > x2, x < x1):
        if lado.sum() >= MINIMO_DO_MEMBRO:
            mx, my = x[lado], y[lado]
            frente = mx.max() > x2
            if (mx.max() - x2 if frente else x1 - mx.min()) < SAIDA_DO_MEMBRO:
                continue
            ponta = int(mx.max()) - 2 if frente else int(mx.min()) + 2
            raiz = x2 if frente else x1
            caixas.append((min(raiz, ponta), min(int(my.max()) + 1, 0), max(raiz, ponta), int(my.min()) + 1))
    return caixas


ALTA = 48  # caixa de golpe mais alta que isso é encolhida até o membro (as dos supers cobriam 20 a 30% de desenho)


def caixa_no_membro(img, ex, ey, caixa, sobe):
    """Sobe a caixa de golpe junto com o desenho (NO_AR_CENTRADO) e, se ela é alta, corta o vazio de cima e de baixo:
    fica do pixel mais alto ao mais baixo que o desenho tem dentro dela, com 3 px de sobra."""
    x1, y1, x2, y2 = caixa[0], caixa[1] - sobe, caixa[2], caixa[3] - sobe
    if abs(y2 - y1) <= ALTA:
        return x1, y1, x2, y2
    ys, xs = np.nonzero(np.asarray(img.getchannel("A")) >= 128)
    x, y = xs - ex, ys - ey
    dentro = (x >= min(x1, x2)) & (x <= max(x1, x2)) & (y >= min(y1, y2)) & (y <= max(y1, y2))
    if not dentro.any():
        return x1, y1, x2, y2
    topo, base = max(min(y1, y2), int(y[dentro].min()) - 3), min(max(y1, y2), int(y[dentro].max()) + 3)
    return (x1, topo, x2, base) if y1 <= y2 else (x1, base, x2, topo)


class Air:
    """Emissor simples: cada elemento mostra o desenho escrito, pelos ticks escritos (sem quadros do meio).
    Ação de corpo (caixa = CORPO, AGACHADO, NO_AR, DEITADO): a caixa de dano é medida em cada desenho
    (caixas_do_corpo) e o argumento só diz que a ação tem corpo. Projétil e efeito usam a caixa passada."""

    def __init__(self, sprites):
        self.s = sprites
        self.imagens = {(g, i): (img, ex, ey) for g, i, img, ex, ey in sprites.lista}
        self.medidas = {}
        self.txt = ["; Gerado por ferramentas/gerar_hazaki.py. Edite lá, não aqui.\n"]
        self.acoes = set()
        self.ativos = {}  # ação -> (elemento em que a caixa de golpe liga, a caixa)

    def acao(self, numero, quadros, caixa=CORPO, loop=None):
        assert numero not in self.acoes, f"ação {numero} repetida"
        self.acoes.add(numero)
        t = [f"[Begin Action {numero}]"]
        corpo = bool(caixa) and numero not in gp.PROJETEIS
        if caixa and not corpo:
            t.append(f"Clsn2Default: {len(caixa)}")
            t += [f" Clsn2[{i}] = {c[0]},{c[1]},{c[2]},{c[3]}" for i, c in enumerate(caixa)]
        for i, q in enumerate(quadros):
            nome, ticks = q[0], q[1]
            golpe = q[2] if len(q) > 2 else None
            if loop == i:
                t.append("Loopstart")
            if corpo:
                if nome not in self.medidas:
                    self.medidas[nome] = caixas_do_corpo(*self.imagens[self.s.codigos[nome]])
                dano = self.medidas[nome]
                t.append(f"Clsn2: {len(dano)}")
                t += [f" Clsn2[{j}] = {c[0]},{c[1]},{c[2]},{c[3]}" for j, c in enumerate(dano)]
            if golpe:
                golpe = caixa_no_membro(*self.imagens[self.s.codigos[nome]], golpe, self.s.subida.get(nome, 0))
                self.ativos.setdefault(numero, (i + 1, golpe))
                t += ["Clsn1: 1", f" Clsn1[0] = {golpe[0]},{golpe[1]},{golpe[2]},{golpe[3]}"]
            elif numero in gp.PROJETEIS and caixa:  # projétil só acerta com Clsn1 em cada desenho
                t.append(f"Clsn1: {len(caixa)}")
                t += [f" Clsn1[{j}] = {c[0]},{c[1]},{c[2]},{c[3]}" for j, c in enumerate(caixa)]
            g, ind = self.s.codigos[nome]
            mistura = gp.TRANS_FX.get(numero)
            t.append(f"{g},{ind}, 0,0, {ticks}" + (f", , {mistura}" if mistura else ""))
        self.txt.append("\n".join(t) + "\n")


def montar_air(s, faiscas):
    a = Air(s)
    Q = a.acao
    F = lambda texto: ler(texto)

    Q(0, F("parado 0/7 1/7 2/7 3/7 4/7 5/7 6/7"))
    Q(5, F("vira 2/3 1/3"))
    Q(6, F("vira 6/3 5/3"), AGACHADO)
    Q(10, F("agachado 2/3"), AGACHADO)
    Q(11, F("agachado 3/8 4/8 5/8 6/8"), AGACHADO)
    Q(12, F("agachado 2/3"), AGACHADO)
    Q(20, F("anda 0/6 1/5 2/6 3/5 4/6 5/5 6/6 7/5"))
    Q(21, F("anda 7/7 6/7 5/7 4/6 3/7 2/7 1/7 0/6"))
    Q(40, F("pulo 0/4"))
    for n in (41, 42, 43):
        Q(n, F("pulo 1/3 2/5 3/6 4/-1"), NO_AR)
    for n in (44, 45, 46):
        Q(n, F("pulo 4/6 5/6 6/-1"), NO_AR)
    Q(47, F("pulo 7/3 parado 0/2"))
    Q(100, F("corrida 0/4 1/4 2/4 3/4 4/4 5/4 6/4 7/4"))
    Q(105, F("recuo 2/3 3/5 4/-1"), NO_AR)
    Q(120, F("defesa 1/2 2/2"))
    Q(130, F("defesa 3/10 4/10"))
    Q(140, F("defesa 5/2 6/2"))
    Q(150, F("defesa 4/3 3/-1"))
    Q(121, F("defesa_baixa 1/2 2/2"), AGACHADO)
    Q(131, F("defesa_baixa 3/10 4/10"), AGACHADO)
    Q(141, F("defesa_baixa 5/2 6/2"), AGACHADO)
    Q(151, F("defesa_baixa 4/-1"), AGACHADO)
    for n in (122, 132, 142, 152):
        Q(n, F("defesa 3/-1"), NO_AR)
    # derrota: toca a sirene (áudio pendente), ele levanta num pulo e foge correndo para fora da tela
    Q(170, F("derrota_sirene 3/8 4/8 5/4 6/4 7/4"), loop=2)
    Q(171, F("derrota_sirene 0/8 1/8 2/5 3/6 4/5 5/4 6/4 7/4"), DEITADO, loop=5)
    Q(181, F("vitoria 0/7 1/7 2/7 3/7 4/7 5/7 6/7 7/-1"))
    for n in (190, 191, 192):
        Q(n, F("intro 0/8 1/8 2/8 3/8 4/8 5/8 6/8 7/8 parado 0/6"))
    Q(195, F("provoca 0/5 1/6 2/6 3/5 4/5 5/5 3/5 4/5 5/5 6/8 7/5"))

    # apanhando
    for n in (5000, 5010):
        Q(n, F("apanha 1/7 0/6"))
    for n in (5002, 5012):
        Q(n, F("apanha 3/6 2/5 1/4 0/2"))
    Q(5001, F("apanha 2/5 1/5 0/6"))
    Q(5011, F("apanha 2/5 1/5 0/6"))
    for n in (5005, 5006, 5007, 5015, 5016, 5017):
        Q(n, F("apanha 1/4 0/4"))
    for n in (5020, 5021, 5022):  # provisório: não há folha de apanhar agachado
        Q(n, [("f_agachado4r", 5), ("f_agachado3", 6)], AGACHADO)
    for n in (5025, 5026, 5027):
        Q(n, F("agachado 3/8"), AGACHADO)
    Q(5030, F("apanha 3/4 4/-1"), NO_AR)  # lançado: sobe caindo para trás (antes mostrava a pose de "preso")
    Q(5035, F("apanha 4/6"), NO_AR)
    # O que as vítimas dos agarrões DELE mostram (ChangeAnim2: a ação é do Hazak, os desenhos são do oponente). Só
    # grupos de gp.SPRITES_VITIMA, que todo lutador tem. Ficam fora das ações 5001/5030, que são ele apanhando.
    Q(VITIMA_PRESA, [("vit49", -1)], NO_AR)
    Q(VITIMA_ENCOLHE, [("vit49", 5), ("vit50", 5), ("vit48", 6)])
    Q(5040, F("apanha 4/-1"), NO_AR)
    Q(5050, F("apanha 4/5 5/5 6/-1"), NO_AR)
    for n in (5051, 5061, 5070):
        Q(n, F("apanha 5/8 6/-1"), NO_AR)
    for n in (5080, 5090):
        Q(n, F("apanha 6/-1"), NO_AR)
    for n in (5100, 5101):
        Q(n, F("queda 1/3 2/3"), DEITADO)
    for n in (5110, 5150):
        Q(n, F("queda 3/-1"), DEITADO)
    Q(5160, F("queda 2/6 3/-1"), DEITADO)
    # 5170 (bateu no chão) tem de ACABAR: o 5110 do motor só manda o nocauteado para o 5150 quando AnimTime = 0, e com
    # o último desenho em -1 ele ficava no 5110 para sempre (a fuga da derrota, que espera o 5150, nunca começava)
    Q(5170, F("queda 2/5 3/5"), DEITADO)
    Q(5120, F("levanta 1/4 2/4 3/4 4/4 5/4 6/4 7/4"), AGACHADO)
    for n in (5200, 5210):
        Q(n, F("rolada_tatame 2/3 3/3 4/3 5/3"), AGACHADO)
    Q(5300, F("apanha 1/8 0/8"))

    # projéteis: a pedra e a bola de ki. Os desenhos daqui são trocados pelos do Blender no diabo_loiro.py (#44)
    Q(1005, [(f"fx_lasca{i}", 2) for i in range(8)], [(-12, -14, 12, 2)])
    Q(1605, [(f"fx_estatueta{i}", 3) for i in range(8)], [(-9, -20, 9, 0)])
    # Diabo Loiro (#44, estados e efeitos no diabo_loiro.py): a cena do "Ô vida, posso despertar?" (bate o pé, olha
    # para trás e pede; a patroa entra, faz que sim e sai) e a pose em que ele vira o Diabo (último desenho), e a
    # Rajadona de Ki das Trevas (carrega com as mãos abertas e segura o soco enquanto o raio sai)
    Q(2000, F(f"despertar_pedido 0/6 1/8 2/6 3/12 4/30 5/20 6/40 7/{DESPERTAR_POSE}"))
    Q(1650, F(f"pose_super 1/3 3/3 4/10 5/10 soco_reto 3/2 4/{RAJADA_SEGURA} 5/8 6/6 7/4"))

    # golpes
    for g in hg.NORMAIS + hg.CORRENTES + hg.KOMBOS:
        Q(g.n, ler(g.quadros, g.clsn1), AREA[g.tipo])
    for n in hg.ANIM:
        Q(n, *anim(n))

    for numero, lista in faiscas.items():
        Q(numero, lista, [])
    return a


# ---------------------------------------------------------------- CNS
def ctl(n, titulo, tipo, *linhas):
    return f"[State {n}, {titulo}]\ntype = {tipo}\n" + "\n".join(linhas) + "\n\n"


def ataque(n, tipo="S", fis="S", juggle=4, velset="0,0", mov="A"):
    return gp.estado(n, tipo, mov, fis, anim=n, juggle=juggle, velset=velset)


PADRAO = {  # classe -> (animtype, ground.hittime, slidetime, ground.velocity, air.velocity)
    "fraco": ("Light", 15, 5, "-2.5", "-1.4,-3"),
    "forte": ("Medium", 20, 6, "-4", "-2,-4"),
    "final": ("Heavy", 22, 8, "-4,-5", "-4,-5"),
}


def cns_golpe(g):
    """Normal, golpe de corrente ou de kombo: gatilho por Time (o tick do 1º desenho com caixa)."""
    q = ler(g.quadros, g.clsn1)
    trechos = ativos(q)
    no_ar = g.tipo == "A"
    t = gp.estado(g.n, g.tipo, "A", g.tipo, anim=g.n, juggle=5 if no_ar else 2, velset=None if no_ar else "0,0")
    if g.leve:
        t += ctl(g.n, "Corrente", "VarAdd", "trigger1 = Time = 0", "var(5) = 1")
    if g.avanco:
        t += ctl(g.n, "Avança", "VelSet", f"trigger1 = Time = [{max(0, trechos[0][0] - 3)},{trechos[-1][1] - 1}]",
                 f"x = {g.avanco}")
    animtype, hit, escorrega, vel, ar = PADRAO[g.classe]
    danos = g.dano if isinstance(g.dano, tuple) else (g.dano,) * len(trechos)
    assert len(danos) == len(trechos), g.n
    for (inicio, _), dano in zip(trechos, danos):
        t += gp.hitdef(g.n, f"Time = {inicio}", f"{g.tipo}, NA", dano, tipo=g.animtype or animtype, guarda=g.guarda,
                       hit=g.hit or hit, escorrega=escorrega, vel=g.vel or vel, ar=g.ar or ar, queda=g.queda,
                       recupera=g.recupera, chao=g.chao or ("Low" if g.guarda == "L" else "High"), classe=g.classe,
                       extra=g.no_hitdef and g.no_hitdef + "\n")
    for inicio, _ in trechos[1:]:
        # 2º acerto do mesmo golpe (jab duplo): o MoveHit do 1º ainda está ligado quando o 2º HitDef sai, e a trava da
        # contagem da corrente (var(11), no -2) nunca veria o intervalo. Solta a trava aqui, depois do HitDef.
        t += ctl(g.n, "Conta o 2º acerto", "VarSet", f"trigger1 = Time = {inicio}", "var(11) = 0")
    t += g.extra.replace("{n}", str(g.n))
    if not no_ar:
        t += gp.fim(g.n, 11 if g.tipo == "C" else 0)
    return t


def projetil(n, gatilho, pid, acao, ofs, vel, dano, guarda, faisca, chao="High", extra=()):
    return ctl(n, "Projétil", "Projectile", f"trigger1 = {gatilho}", f"projid = {pid}", f"projanim = {acao}",
               "projhitanim = 9200", "projremanim = 9200", "projhits = 1", "projpriority = 2", f"offset = {ofs}",
               f"velocity = {vel}", *extra, "attr = S, SP", f"damage = {dano}, 5", "animtype = Med",
               f"guardflag = {guarda}", "hitflag = MAF", "pausetime = 4, 10", "sparkxy = 0, 0",
               f"sparkno = S{faisca}", "guard.sparkno = S9216", "sparkscale = 1, 1", "hitsound = F5,1",
               "guardsound = F6,0", f"ground.type = {chao}", "ground.slidetime = 12", "ground.hittime = 18",
               "ground.velocity = -4", "air.velocity = -2,-3.5")


def rastro(n, gatilho, tempo):
    """Rastro de velocidade curto da ficha: só as 2 últimas posições (2 ticks), somado e cinza."""
    return ctl(n, "Rastro de velocidade", "AfterImage", f"trigger1 = {gatilho}", f"time = {tempo}", "length = 3",
               "timegap = 1", "framegap = 1", "trans = add", "palcolor = 0", "palbright = 40,40,40",
               "paladd = 0,0,0", "palmul = .6,.6,.6")


def corta_rastro(n, gatilho="Time = 0"):
    return ctl(n, "Fim do rastro", "AfterImageTime", f"trigger1 = {gatilho}", "time = 1")


def poeira(n, gatilho, x=0):
    """Poeira de asfalto no pé (heavy-landing do pixelfx, pintado de cinza): chutes fortes, arrancada e pouso."""
    return ctl(n, "Poeira", "Explod", f"trigger1 = {gatilho}", "anim = 9209", "postype = p1", f"pos = {x}, 0",
               "removetime = -2", "sprpriority = 4", "ownpal = 1")


TODOS_OS_GOLPES = "SCA, NA, SA, HA, NP, SP, HP"
NO_CHAO = "statetype = A && Pos Y >= 0 && Vel Y > 0"


def cns_sistema():
    c = []
    # golpe de afastar (y+b), no chão e no ar
    c.append(gp.normal(260, "S, HA", 80, f"Time = {acerto(260)}", tipo="Back", queda=True, vel="-7,-5", ar="-5,-5",
                       classe="forte"))
    c.append(gp.normal(650, "A, HA", 60, f"Time = {acerto(650)}", fis="A", tipo_st="A", guarda="HA", tipo="Back",
                       queda=True, vel="-5,-4", ar="-4,-4", classe="forte"))
    # rolamento (x+a): invencível do tick 1 ao 20, depois pode ser agarrado
    for n, v in ((700, 6), (705, -6)):
        c.append(gp.estado(n, "S", "I", "N", anim=n, velset=f"{v},0"))
        c.append(ctl(n, "Invencivel", "NotHitBy", "trigger1 = Time < ifelse(var(8), 24, 20)",
                     f"value = {TODOS_OS_GOLPES}", "time = 1"))
        c.append(ctl(n, "Atravessa", "PlayerPush", "trigger1 = Time < 20", "value = 0"))
        c.append(ctl(n, "Para", "VelSet", "trigger1 = Time = 20", "x = 0"))
        c.append(ctl(n, "Vira", "Turn", "trigger1 = AnimTime = 0", "trigger1 = p2dist x < 0"))
        c.append(ctl(n, "Limpa", "VarSet", "trigger1 = AnimTime = 0", "var(8) = 0"))
        c.append(gp.fim(n))
    # guard cancel com o golpe de afastar: invencível e sem dano
    c.append(gp.estado(720, "S", "A", "S", anim=260, juggle=0))
    c.append(ctl(720, "Invencivel", "NotHitBy", f"trigger1 = Time < {acerto(260)}", "value = SCA", "time = 1"))
    c.append(gp.hitdef(720, f"Time = {acerto(260)}", "S, HA", 0, tipo="Back", queda=True, vel="-7,-5", ar="-5,-5",
                       classe="forte"))
    c.append(gp.fim(720))
    # provocação: balança o dedo; tira 25 de barra (250 no motor) do oponente quando termina inteira
    c.append(gp.estado(195, "S", "I", "S", anim=195))
    c.append(ctl(195, "Tira barra", "PowerAdd", "trigger1 = AnimTime = 0", "value = -250",
                 "redirectid = enemynear,id"))
    c.append(gp.fim(195))
    # parry (frente + c)
    c.append(gp.estado(760, "S", "A", "N", anim=760))
    c.append(gp.reversao(760, 761, "SCA, NA, SA, HA", "Time < 4"))
    c.append(gp.fim(760))
    c.append(gp.estado(761, "S", "I", "N", anim=761))
    c.append(gp.fim(761))
    # quem teve o golpe aparado ou revertido (roda no oponente)
    c.append("[Statedef 762]\ntype = U\nmovetype = H\nphysics = N\nctrl = 0\n\n"
             "[State 762, Solo]\ntype = VelSet\ntrigger1 = statetype != A\nx = 0\ny = 0\n\n"
             "[State 762, Pose]\ntype = ChangeAnim\ntrigger1 = Time = 0\n"
             "value = ifelse(statetype = A, 5030, ifelse(statetype = C, 5020, 5000))\n\n"
             "[State 762, Gravidade]\ntype = VelAdd\ntrigger1 = statetype = A\ny = .44\n\n"
             "[State 762, Pouso]\ntype = PosSet\ntrigger1 = statetype = A && Pos Y >= 0 && Vel Y >= 0\ny = 0\n\n"
             "[State 762, Aterrissa]\ntype = StateTypeSet\ntrigger1 = statetype = A && Pos Y >= 0 && Vel Y >= 0\n"
             "statetype = S\n\n"
             "[State 762, Abertura no ar]\ntype = SelfState\ntrigger1 = Time >= 14 && statetype = A\nvalue = 50\n"
             "ctrl = 1\n\n"
             "[State 762, Abertura no chão]\ntype = SelfState\ntrigger1 = Time >= 14\nvalue = 0\nctrl = 1\n\n")
    # Tá Achando Ruim? (303): o tapa de costas de mão gira o oponente antes de derrubar. Roda no oponente, com a ação
    # 5030 dele mesmo: uma volta inteira em dois meios giros (o VelMul mantém o rumo: a velocidade é relativa ao lado
    # para onde ele olha) e depois a queda normal do motor (5050), com a derrubada do HitDef.
    c.append("[Statedef 304]\ntype = A\nmovetype = H\nphysics = N\nvelset = -3.5,-5.5\nctrl = 0\n\n")
    c.append(ctl(304, "Pose", "ChangeAnim", "trigger1 = Time = 0", "value = 5030"))
    c.append(ctl(304, "Gravidade", "VelAdd", "trigger1 = 1", "y = .45"))
    c.append(ctl(304, "Gira", "Turn", "trigger1 = Time = 5", "trigger2 = Time = 10"))
    c.append(ctl(304, "Mantém o rumo", "VelMul", "trigger1 = Time = 5", "trigger2 = Time = 10", "x = -1"))
    c.append(ctl(304, "Cai", "SelfState", "trigger1 = Time >= 15", "value = 5050"))
    return "".join(c)


def cns_agarroes():
    c = []
    agarra = lambda n, alvo, p1, p2: ctl(
        n, "Agarra", "HitDef", "trigger1 = Time = 0", "attr = S, NT", f"hitflag = {alvo}", "priority = 1, Miss",
        "sparkno = -1", "p1sprpriority = 1", "p1facing = 1", "p2facing = 1", f"p1stateno = {p1}",
        f"p2stateno = {p2}", "guard.dist = 0", "fall = 1")
    escapou = lambda n, ate, preso: ctl(n, "Escapou", "ChangeState", "trigger1 = Time > 1", f"trigger1 = Time < {ate}",
                                        f"trigger1 = enemynear,stateno != {preso}", "value = 0", "ctrl = 1")
    # sem tremida: a regra 8.3 só dá EnvShake ao finalizador de corrente e ao golpe final de super
    pancada = lambda n, t: ctl(n, f"Som {t}", "PlaySnd", f"trigger1 = Time = {t}", "value = F5, 2")

    # Abraço de Quebrada (colado, frente ou trás + y): abraça, levanta e joga por cima do ombro
    c.append(ataque(800, juggle=0))
    c.append(agarra(800, "H-", 810, 820))
    c.append(gp.fim(800))
    c.append("[Statedef 810]\ntype = S\nmovetype = A\nphysics = N\nanim = 810\nvelset = 0,0\nctrl = 0\n\n")
    c.append(ctl(810, "Lado", "VarSet", "trigger1 = Time = 0", 'var(2) = command = "holdback"'))
    c.append(ctl(810, "Segura", "TargetBind", "trigger1 = Time < 14", "pos = 30, 0"))
    c.append(escapou(810, 14, 820))
    c.append(ctl(810, "Vira", "Turn", "trigger1 = Time = 14", "trigger1 = var(2)"))
    c.append(ctl(810, "Dano", "TargetLifeAdd", "trigger1 = Time = 14", "trigger1 = NumTarget", "value = -120"))
    c.append(pancada(810, 14))
    c.append(ctl(810, "Solta", "TargetState", "trigger1 = Time = 14", "trigger1 = NumTarget", "value = 821"))
    c.append(gp.fim(810))

    # Puxa a Perna (colado, baixo + y, oponente agachado): puxa a perna e derruba sentado
    solta = 13
    c.append(ataque(840, juggle=0))
    c.append(agarra(840, "L-", 841, 820))
    c.append(gp.fim(840))
    c.append(gp.estado(841, "S", "A", "N", anim=841, juggle=0))
    c.append(ctl(841, "Segura", "TargetBind", f"trigger1 = Time < {solta}", "pos = 34, 0"))
    c.append(escapou(841, solta, 820))
    c.append(ctl(841, "Dano", "TargetLifeAdd", f"trigger1 = Time = {solta}", "trigger1 = NumTarget", "value = -100"))
    c.append(pancada(841, solta))
    c.append(ctl(841, "Derruba", "TargetState", f"trigger1 = Time = {solta}", "trigger1 = NumTarget",
                 "value = 846"))
    c.append(gp.fim(841))

    # Cutucão Sacana (← → + y, colado): prende pelo pescoço e cutuca as costelas 3 vezes; escapa só antes do 1º
    cutucoes, fim_cutucao = (13, 25, 37), 43  # 43 = o desenho 7 (solta)
    c.append(ataque(830, juggle=0))
    c.append(agarra(830, "M-", 831, 832))
    c.append(gp.fim(830))
    c.append(gp.estado(831, "S", "A", "N", anim=831, juggle=0))
    c.append(ctl(831, "Segura", "TargetBind", f"trigger1 = Time < {fim_cutucao}", "pos = 30, 0"))
    c.append(escapou(831, cutucoes[0], 832))
    for t in cutucoes:
        c.append(ctl(831, f"Cutucão {t}", "TargetLifeAdd", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                     "value = -30"))
        c.append(ctl(831, f"Faísca {t}", "Explod", f"trigger1 = Time = {t}", "anim = 9200", "postype = p1",
                     "pos = 40, -62", "removetime = -2", "sprpriority = 4", "ownpal = 1"))
        c.append(ctl(831, f"Som {t}", "PlaySnd", f"trigger1 = Time = {t}", "value = F5, 0"))
    c.append(ctl(831, "Encolhe", "TargetState", f"trigger1 = Time = {cutucoes[0]}", "trigger1 = NumTarget",
                 "value = 833"))
    c.append(ctl(831, "Dano final", "TargetLifeAdd", f"trigger1 = Time = {fim_cutucao}", "trigger1 = NumTarget",
                 "value = -50"))
    c.append(pancada(831, fim_cutucao))
    c.append(ctl(831, "Solta", "TargetState", f"trigger1 = Time = {fim_cutucao}", "trigger1 = NumTarget",
                 "value = 846"))
    c.append(gp.fim(831))

    # estados do oponente (rodam nele, com os desenhos dele e as ações VITIMA_PRESA / VITIMA_ENCOLHE do Hazak)
    escape = ('[State {n}, Escape]\ntype = SelfState\ntriggerall = Time <= 7\ntrigger1 = command = "y"\n'
              'trigger2 = command = "b"\nvalue = 0\nctrl = 1\n\n')
    solto = "[State {n}, Solto]\ntype = SelfState\ntrigger1 = !gethitvar(isbound)\nvalue = 5050\n\n"
    for n, pose, com_escape in ((820, VITIMA_PRESA, True), (832, VITIMA_PRESA, True), (833, VITIMA_ENCOLHE, False)):
        c.append(f"[Statedef {n}]\ntype = A\nmovetype = H\nphysics = N\nvelset = 0,0\n\n")
        c.append(ctl(n, "Pose", "ChangeAnim2", "trigger1 = Time = 0", f"value = {pose}"))
        if com_escape:
            c.append(escape.replace("{n}", str(n)))
        c.append(solto.replace("{n}", str(n)))
    # arremessado por cima do ombro
    c.append("[Statedef 821]\ntype = A\nmovetype = H\nphysics = N\nvelset = 3.2,-6\nctrl = 0\n\n")
    c.append(ctl(821, "Queda", "VelAdd", "trigger1 = 1", "y = .44"))
    c.append(ctl(821, "Chao", "SelfState", "trigger1 = Vel Y > 0", "trigger1 = Pos Y >= 0", "value = 5100"))
    # derrubado no lugar (perna puxada, tonto de rir)
    c.append("[Statedef 846]\ntype = A\nmovetype = H\nphysics = N\nvelset = -2,-4\nctrl = 0\n\n")
    c.append(ctl(846, "Queda", "VelAdd", "trigger1 = 1", "y = .44"))
    c.append(ctl(846, "Chao", "SelfState", "trigger1 = Vel Y > 0", "trigger1 = Pos Y >= 0", "value = 5100"))
    return "".join(c)


# Diabo Loiro: quanto dura a pose da transformação (último desenho da cena) e quanto ele segura o soco da Rajadona
DESPERTAR_POSE = 40
RAJADA_SEGURA = 72

# Pedra: tick em que ela pula do chão (pé no asfalto, chute_canela 3) e em que sai voando (soco_reto/chute 4), e o
# ponto de saída do projétil (na frente do punho ou do pé). A subida do Explod (vel -6, accel .18) leva os 17 ticks.
PEDRA = {"pula": 8, "sai": 25, "x": 58, "y": -80}
# Bola de ki: a carga começa no tick 3 (pose_super 3, mãos abrindo) nas duas mãos, e a bola sai do punho do soco.
KI = {"carga": 4, "maos": ((22, -46), (-30, -46)), "x": 52, "y": -80}


def cns_especiais():
    c = []
    H = lambda n, k=0, **kw: gp.hitdef(n, f"Time = {acerto(n, k)}", kw.pop("attr", "S, SA"), kw.pop("dano"),
                                       classe=kw.pop("classe", "especial"), **kw)

    # Pedra (↓ → x/y, issue #44): chuta o chão, a pedra pula do asfalto e sobe na frente dele (Explod que sobe e
    # desacelera, 7401) e, no tick 25, ele manda a pedra voando: x soca (mais lenta), y chuta de novo (mais rápida e
    # mais forte). A pedra em voo é o projétil 1005 e quebra em cacos no acerto (7402). Efeitos: diabo_loiro.py.
    for n, vel, dano in ((1000, 6.0, 65), (1001, 8.0, 80)):
        c.append(ataque(n))
        c.append(poeira(n, f"Time = {PEDRA['pula']}", 50))
        c.append(ctl(n, "Pedra sobe", "Explod", f"trigger1 = Time = {PEDRA['pula']}", "anim = 7401", "id = 7401",
                     "postype = p1", "pos = 54, -8", "vel = 0.15, -6", "accel = 0, .18", "bindtime = 0",
                     f"removetime = {PEDRA['sai'] - PEDRA['pula']}", "sprpriority = 4", "ownpal = 1"))
        c.append(ctl(n, "Pedra sai", "RemoveExplod", f"trigger1 = Time = {PEDRA['sai']}", "id = 7401"))
        c.append(ctl(n, "Projétil", "Projectile", f"trigger1 = Time = {PEDRA['sai']}", "projid = 1000",
                     "projanim = 1005", "projhitanim = 7402", "projremanim = 7402", "projcancelanim = 7402",
                     "projhits = 1", "projpriority = 2", f"offset = {PEDRA['x']}, {PEDRA['y']}",
                     f"velocity = {vel}, 0", "attr = S, SP", f"damage = {dano}, 5", "animtype = Med",
                     "guardflag = MA", "hitflag = MAF", "pausetime = 4, 10", "sparkno = -1",
                     "guard.sparkno = S9216", "hitsound = F5,2", "guardsound = F6,0", "ground.type = High",
                     "ground.slidetime = 12", "ground.hittime = 18", "ground.velocity = -4",
                     "air.velocity = -2,-3.5"))
        c.append(gp.fim(n))

    # Bola de ki (→ ← x/y, issue #44): carrega o ki com as mãos abertas (brilho vermelho nas duas mãos, 7410) e solta
    # a bola vermelha (1605) com o soco; estoura no acerto (7411). O y carrega mais: sai mais rápida e bate mais.
    for n, vel, dano in ((1600, 4.5, 70), (1601, 6.5, 90)):
        solta = duracao(anim(n)[0][:4]) + 2  # fim da carga (4 desenhos de pose_super) + o 1º do soco
        c.append(ataque(n))
        for k, (x, y) in enumerate(KI["maos"]):
            c.append(ctl(n, f"Carga {k + 1}", "Explod", f"trigger1 = Time = {KI['carga']}", "anim = 7410",
                         f"id = {7410 + k}", "postype = p1", f"pos = {x}, {y}", f"removetime = {solta - KI['carga']}",
                         "sprpriority = 4", "ownpal = 1"))
        c.append(ctl(n, "Projétil", "Projectile", f"trigger1 = Time = {solta}", "projid = 1001",
                     "projanim = 1605", "projhitanim = 7411", "projremanim = 7411", "projcancelanim = 7411",
                     "projhits = 1", "projpriority = 2", f"offset = {KI['x']}, {KI['y']}", f"velocity = {vel}, 0",
                     "attr = S, SP", f"damage = {dano}, 6", "animtype = Med", "guardflag = MA", "hitflag = MAF",
                     "pausetime = 4, 10", "sparkno = -1", "guard.sparkno = S9216", "hitsound = F5,2",
                     "guardsound = F6,0", "ground.type = High", "ground.slidetime = 12", "ground.hittime = 18",
                     "ground.velocity = -4", "air.velocity = -2,-3.5"))
        c.append(gp.fim(n))

    # Ascensão de Faixa (→ ↓ x/y): antiaéreo de joelho e ombro, pés no chão
    for n, dano, invencivel in ((1200, 80, f"trigger1 = Time < {acerto(1200) + 1}\nvalue = A"),
                                (1201, 110, f"trigger1 = Time < {fim_ativo(1201)}\nvalue = SCA")):
        c.append(ataque(n))
        c.append(ctl(n, "Invencivel", "NotHitBy", *invencivel.split("\n"), "time = 1"))
        c.append(ctl(n, "Avança", "VelSet", f"trigger1 = Time = [{acerto(n) - 3},{fim_ativo(n) - 1}]", "x = 1.5"))
        c.append(H(n, dano=dano, tipo="Up", queda=True, vel="-2,-7", ar="-2,-7", hit=20))
        c.append(ctl(n, "Subida", "Explod", "trigger1 = MoveHit = 1", "anim = 9208", "postype = p1",
                     "pos = 22, -80", "removetime = -2", "sprpriority = 4", "ownpal = 1"))
        c.append(gp.fim(n))

    # Giro de Garagem (↓ → a/b): chute girando que atravessa meia tela; o b vai mais longe e derruba
    # (a ficha pede meia tela = 160 px: 14 ticks a 10,5 no a ~ 150 px; 16 ticks a 12,5 no b ~ 200 px)
    for n, vx, dano, derruba in ((1300, 10.5, 65, False), (1301, 12.5, 85, True)):
        c.append(ataque(n))
        c.append(ctl(n, "Avança", "VelSet", f"trigger1 = Time = [3,{fim_ativo(n) - 1}]", f"x = {vx}"))
        if derruba:
            c.append(poeira(n, "Time = 3"))
        c.append(H(n, dano=dano, tipo="Heavy" if derruba else "Medium", queda=derruba, hit=20, escorrega=7,
                   vel="-5,-4" if derruba else "-5", ar="-4,-4"))
        c.append(gp.fim(n))

    # Corte de Base (↓ ← a/b): desliza com a perna esticada no chão; só defende agachado; o b derruba
    for n, vx, dano, derruba in ((1400, 4, 55, False), (1401, 6, 75, True)):
        c.append(ataque(n, "C", "C"))
        c.append(ctl(n, "Desliza", "VelSet", f"trigger1 = Time = [{acerto(n)},{fim_ativo(n) - 1}]", f"x = {vx}"))
        if derruba:
            c.append(poeira(n, f"Time = {acerto(n)}", 10))
        c.append(H(n, attr="C, SA", dano=dano, guarda="L", chao="Trip" if derruba else "Low",
                   tipo="Back" if derruba else "Medium", queda=derruba, recupera=False, hit=20,
                   vel="-3,-2" if derruba else "-3", ar="-3,-2"))
        c.append(gp.fim(n, 11))

    # Rolada de Tatame (← → a/b): rola por baixo, passa por dentro do oponente e chega virado nas costas dele.
    # É uma travessia (9 px por tick enquanto rola), não um salto de posição: rola até ficar 36 px atrás dele. Sem
    # espaço atrás (canto: var(15) = 0), rola até colar na frente. Oponente longe demais (mais de ~90 px): a rolada
    # acaba antes de passar. Invencível enquanto rola; a recuperação (o a) ou o chute (o b) ficam expostos.
    cabe = "p2dist x + 36 < frontedgebodydist"
    rolando = "ifelse(var(15), p2dist x > -36, p2dist x > 28)"
    for n, rola in ((1700, 16), (1701, 15)):  # ticks de rolamento (os 5 desenhos da rolada)
        c.append(ataque(n, fis="N", juggle=0))
        c.append(ctl(n, "Cabe atrás", "VarSet", "trigger1 = Time = 0", f"var(15) = ({cabe})"))
        c.append(ctl(n, "Invencivel", "NotHitBy", f"trigger1 = Time < {rola}", f"value = {TODOS_OS_GOLPES}",
                     "time = 1"))
        c.append(ctl(n, "Atravessa", "PlayerPush", f"trigger1 = Time < {rola + 2}", "value = 0"))
        c.append(ctl(n, "Rola", "VelSet", f"trigger1 = Time = [2,{rola - 1}]", f"trigger1 = {rolando}", "x = 9"))
        c.append(ctl(n, "Chegou", "VelSet", f"trigger1 = Time = [2,{rola - 1}]", f"trigger1 = !({rolando})",
                     "x = 0"))
        c.append(ctl(n, "Para", "VelSet", f"trigger1 = Time = {rola}", "x = 0"))
        c.append(ctl(n, "Vira", "Turn", f"trigger1 = Time = {rola}", "trigger1 = p2dist x < 0"))
        if n == 1701:
            c.append(H(n, dano=50, tipo="Medium", hit=20, escorrega=7, vel="-5"))
        c.append(gp.fim(n))

    # Pega Bolado (← ↓ a/b): sai correndo e dá a voadora de dois pés. O b atravessa a tela e derruba; defendido,
    # cai no 1503 e fica aberto (erra feio).
    for n, corre, vx, dano, derruba in ((1500, 6, 6, 70, False), (1501, 14, 9.5, 100, True)):
        c.append(ataque(n, fis="N", velset="7.2,0"))
        c.append(ctl(n, "Zera", "VarSet", "trigger1 = Time = 0", "var(12) = 0"))
        c.append(rastro(n, "Time = 0", 60))
        c.append(poeira(n, f"Time = {corre}"))
        c.append(ctl(n, "Salta", "VelSet", f"trigger1 = Time = {corre}", f"x = {vx}", "y = -4.5"))
        c.append(ctl(n, "No ar", "StateTypeSet", f"trigger1 = Time = {corre}", "statetype = A"))
        c.append(ctl(n, "Gravidade", "VelAdd", "trigger1 = statetype = A", "y = .45"))
        c.append(H(n, attr="A, SA", dano=dano, tipo="Heavy" if derruba else "Medium", queda=derruba, hit=20,
                   escorrega=7, vel="-6,-5" if derruba else "-5", ar="-5,-4"))
        c.append(ctl(n, "Defendido", "VarSet", "trigger1 = MoveGuarded", "var(12) = 1"))
        c.append(ctl(n, "Pouso aberto", "ChangeState", f"trigger1 = {NO_CHAO}", "trigger1 = var(12)",
                     "value = 1503"))
        c.append(ctl(n, "Pouso", "ChangeState", f"trigger1 = {NO_CHAO}", "value = 1502"))
    for n in (1502, 1503):
        c.append(gp.estado(n, "S", "I", "S", anim=n, velset="0,0"))
        c.append(ctl(n, "Chão", "PosSet", "trigger1 = Time = 0", "y = 0"))
        c.append(corta_rastro(n))
        c.append(poeira(n, "Time = 0"))
        c.append(gp.fim(n))

    # Guarda de Aço (↓ ← x/y): contra-ataque. Arma a guarda; se um golpe encostar na janela, responde com chute.
    # O x pega golpe de quem está em pé ou no ar; o y pega golpe baixo (de quem está agachado) também.
    for n, atributos, dano in ((1100, "SA, NA, SA", 60), (1101, "SCA, NA, SA", 70)):
        c.append(gp.estado(n, "S", "A", "N", anim=n))
        c.append(gp.reversao(n, n + 2, atributos, "Time = [2,17]"))
        c.append(gp.fim(n))
        c.append(ataque(n + 2))
        c.append(ctl(n + 2, "Invencivel", "NotHitBy", f"trigger1 = Time < {acerto(n + 2)}", "value = SCA",
                     "time = 1"))
        c.append(H(n + 2, dano=dano, classe="contra", tipo="Heavy", queda=True, vel="-5,-4", ar="-5,-4", hit=20))
        c.append(gp.fim(n + 2))
    return "".join(c)


def cns_supers():
    c = []
    S = lambda n, t, dano, **kw: gp.hitdef(n, t, kw.pop("attr", "S, HA"), dano, classe=kw.pop("classe", "super"),
                                           **kw)
    pose = duracao(anim(3000)[0])

    # ---- Faixa no Asfalto (← → ↓ + a/b, 1 estoque): rajada de chutes com a mesma perna, sobe chutando e fecha com
    # o Machado de Dojô. Invencível do tick 1 ao fim da pose (superpause).
    c.append(gp.estado(3000, "S", "A", "S", anim=3000, juggle=0))
    c.append(gp.superpausa(3000, "Time = 0"))
    c.append(ctl(3000, "Gasta", "PowerAdd", "trigger1 = Time = 0", "value = -1000"))
    c.append(ctl(3000, "Invencivel", "NotHitBy", "trigger1 = 1", "value = SCA", "time = 1"))
    c.append(ctl(3000, "Rajada", "ChangeState", f"trigger1 = Time >= {pose}", "value = 3001"))
    t1 = [acerto(3001, k) for k in range(3)]
    c.append(ataque(3001, juggle=0))
    c.append(ctl(3001, "Avança", "VelSet", f"trigger1 = Time < {fim_ativo(3001)}", "x = 3"))
    for k, t in enumerate(t1):
        c.append(S(3001, f"Time = {t}" + (" && MoveHit" if k else ""), 25, tipo="Medium", hit=22, escorrega=4,
                   vel="-1", ar="-1,-3"))
    c.append(ctl(3001, "Sobe chutando", "ChangeState", f"trigger1 = Time = {fim_ativo(3001) + 2} && MoveHit",
                 "value = 3002"))
    c.append(gp.fim(3001))
    t2 = [acerto(3002, k) for k in range(3)]
    c.append(ataque(3002, "A", "N", juggle=0, velset="1.5,-6"))
    c.append(ctl(3002, "Gravidade", "VelAdd", "trigger1 = 1", "y = .35"))
    for k, t in enumerate(t2):
        ultimo = k == 2
        c.append(S(3002, f"Time = {t}", 25, attr="A, HA", tipo="Up", hit=22, queda=True, recupera=False,
                   vel="-1.5,-3" if ultimo else "-1.5,-6", ar="-1.5,-3" if ultimo else "-1.5,-6"))
    c.append(ctl(3002, "Pousa", "ChangeState", "trigger1 = Time > 4 && Pos Y >= 0 && Vel Y > 0", "value = 3003"))
    c.append(ataque(3003, juggle=0))
    c.append(ctl(3003, "Chão", "PosSet", "trigger1 = Time = 0", "y = 0"))
    c.append(S(3003, f"Time = {acerto(3003)}", 90, classe="super_final", tipo="Heavy", queda=True, recupera=False,
               vel="-3,-4", ar="-2,7", extra=hg.QUIQUE + "\n"))
    c.append(ctl(3003, "Asfalto", "Explod", "trigger1 = MoveHit = 1", "anim = 9205", "postype = p1", "pos = 40, 0",
                 "removetime = -2", "sprpriority = 4", "ownpal = 1"))
    c.append(ctl(3003, "Clarão", "BGPalFX", "trigger1 = MoveHit = 1", "time = 4", "add = 128, 128, 128",
                 "ignorehitpause = 1"))
    c.append(gp.fim(3003))

    # ---- Rapidinho da Quebrada (← → ↓ + x/y, 2 estoques): atravessa a tela 4 vezes batendo a cada passagem e
    # fecha com o Pega Bolado. Passagem errada ou defendida encerra (3203). var(13) conta as passagens, var(14) = a
    # passagem acertou.
    passagem = duracao(anim(3201)[0]) - 1
    c.append(gp.estado(3200, "S", "A", "S", anim=3200, juggle=0))
    c.append(gp.superpausa(3200, "Time = 0"))
    c.append(ctl(3200, "Gasta", "PowerAdd", "trigger1 = Time = 0", "value = -2000"))
    c.append(ctl(3200, "Zera", "VarSet", "trigger1 = Time = 0", "var(13) = 0"))
    c.append(ctl(3200, "Invencivel", "NotHitBy", "trigger1 = 1", "value = SCA", "time = 1"))
    c.append(ctl(3200, "Passa", "ChangeState", f"trigger1 = Time >= {pose}", "value = 3201"))
    c.append(ataque(3201, fis="N", juggle=0, velset="12,0"))
    c.append(rastro(3201, "Time = 0", passagem + 1))
    c.append(ctl(3201, "Zera", "VarSet", "trigger1 = Time = 0", "var(14) = 0"))
    c.append(ctl(3201, "Atravessa", "PlayerPush", "trigger1 = 1", "value = 0"))
    c.append(S(3201, f"Time = {acerto(3201)}", 45, tipo="Medium", hit=30, escorrega=0, vel="0", ar="0,-2",
               pausa_classe=(2, 6)))
    c.append(ctl(3201, "Acertou", "VarSet", "trigger1 = MoveHit", "var(14) = 1"))
    c.append(ctl(3201, "Vira", "Turn", f"trigger1 = Time = {passagem}", "trigger1 = p2dist x < 0"))
    c.append(ctl(3201, "Conta", "VarAdd", f"trigger1 = Time = {passagem}", "var(13) = 1"))
    c.append(ctl(3201, "Errou", "ChangeState", f"trigger1 = Time = {passagem}", "trigger1 = !var(14)",
                 "value = 3203"))
    c.append(ctl(3201, "Fecha", "ChangeState", f"trigger1 = Time = {passagem}", "trigger1 = var(13) >= 4",
                 "value = 3202"))
    c.append(ctl(3201, "De novo", "ChangeState", f"trigger1 = Time = {passagem}", "value = 3201"))
    c.append(ataque(3202, fis="N", juggle=0, velset="7,-3.5"))
    c.append(rastro(3202, "Time = 0", 14))
    c.append(poeira(3202, "Time = 0"))
    c.append(ctl(3202, "No ar", "StateTypeSet", "trigger1 = Time = 0", "statetype = A"))
    c.append(ctl(3202, "Gravidade", "VelAdd", "trigger1 = statetype = A", "y = .45"))
    c.append(S(3202, f"Time = {acerto(3202)}", 160, attr="A, HA", classe="super_final", tipo="Heavy", queda=True,
               recupera=False, vel="-7,-6", ar="-7,-6"))
    c.append(ctl(3202, "Clarão", "BGPalFX", "trigger1 = MoveHit = 1", "time = 4", "add = 128, 128, 128",
                 "ignorehitpause = 1"))
    c.append(ctl(3202, "Chão", "PosSet", f"trigger1 = {NO_CHAO}", "y = 0"))
    c.append(ctl(3202, "Para", "VelSet", f"trigger1 = {NO_CHAO}", "x = 0", "y = 0"))
    c.append(ctl(3202, "Aterrissa", "StateTypeSet", f"trigger1 = {NO_CHAO}", "statetype = S"))
    c.append(gp.fim(3202))
    c.append(gp.estado(3203, "S", "I", "S", anim=3203, velset="4,0"))
    c.append(corta_rastro(3203))
    c.append(gp.fim(3203))
    return "".join(c)


MENOS_2 = """[Statedef -2]

[State -2, Zera fracos]
type = VarSet
trigger1 = ctrl
var(5) = 0

; corrente de 3 golpes: var(10) conta os acertos de verdade (defendido não conta); var(11) trava a contagem para o
; mesmo acerto não somar duas vezes durante a pausa do contato. O finalizador exige var(10) >= 3 (4 na corrente x).
[State -2, Zera corrente]
type = VarSet
trigger1 = ctrl
var(10) = 0

[State -2, Conta acerto da corrente]
type = VarAdd
trigger1 = MoveHit
trigger1 = var(11) = 0
trigger1 = stateno = [200,349]
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

; Rastro de velocidade da corrida (ficha): 2 ticks de rastro, renovado a cada 8 ticks; cortado ao sair da corrida
; (menos para a voadora e os supers, que têm o rastro deles). O -2 roda antes da troca de estado do tick: o 1º tick
; que ele vê do estado novo é o Time = 1 (com Time % 8 = 0 o rastro só nascia no 8º tick da corrida).
[State -2, Rastro da corrida]
type = AfterImage
trigger1 = stateno = 100
trigger1 = (Time % 8) = 1
time = 8
length = 3
timegap = 1
framegap = 1
trans = add
palcolor = 0
palbright = 40,40,40
paladd = 0,0,0
palmul = .6,.6,.6

[State -2, Fim do rastro da corrida]
type = AfterImageTime
trigger1 = prevstateno = 100
trigger1 = Time <= 1
trigger1 = stateno != 100
trigger1 = stateno != [1500,1501]
trigger1 = stateno != [3000,3299]
time = 1

[State -2, Passo para trás invencível]
type = NotHitBy
trigger1 = stateno = 105
trigger1 = Time < 6
value = SCA
time = 1

; Derrota: toca uma sirene (áudio pendente), ele levanta num pulo e foge correndo para fora da tela. Por nocaute o
; estado continua o 5150 do motor (a lógica do KO não muda): só a animação e a posição mudam. Os desenhos 4 a 7 da
; folha derrota_sirene foram desenhados olhando para TRÁS (para a esquerda da folha, de costas para o oponente): ele
; corre de frente para a saída. Por isso não há Turn nem flip no .air.
[State -2, Sirene: levanta]
type = ChangeAnim
trigger1 = !alive && stateno = 5150 && Time = 40
value = 171

[State -2, Sirene: foge]
type = PosAdd
trigger1 = anim = 171 && AnimElemNo(0) >= 6
trigger2 = stateno = 170 && AnimElemNo(0) >= 3
x = -5

; A tela só solta ele quando começa a correr. Solta desde o começo da animação, a câmera largava o caído e ia para
; o vencedor: ele saía do quadro ainda deitado e ninguém via o pulo nem a corrida (visto no filme).
[State -2, Sirene: sai da tela]
type = ScreenBound
trigger1 = anim = 171 && AnimElemNo(0) >= 6
trigger2 = stateno = 170 && AnimElemNo(0) >= 3
value = 0
movecamera = 0,0

"""


def montar_cns():
    topo = gp.CNS_TOPO
    for antigo, novo in (
            ("; Gerado por ferramentas/gerar_pengaro.py. Edite lá, não aqui.",
             "; Gerado por ferramentas/gerar_hazaki.py. Edite lá, não aqui."),
            ("; var(20) tempo de Despertar, var(21) ressaca",
             "; var(12) Pega Bolado defendido, var(13)/(14) passagens do Rapidinho,\n"
             "; var(20) tempo do Diabo Loiro (Despertar), var(37) arte do Diabo ligada (diabo_loiro.py)"),
            ("life = 1000", "life = 900"), ("defence = 100", "defence = 90"),
            ("walk.fwd = 2.7", "walk.fwd = 3.4"), ("walk.back = -2.2", "walk.back = -2.8"),
            ("run.fwd = 5.6, 0", "run.fwd = 7.2, 0"), ("run.back = -5.2,-3.4", "run.back = -6.4,-3.6")):
        assert topo.count(antigo) == 1, antigo
        topo = topo.replace(antigo, novo)
    c = [topo, gp.cns_intro(), gp.CNS_PULOS]
    c += [cns_golpe(g) for g in hg.NORMAIS + hg.CORRENTES + hg.KOMBOS]
    c += [cns_sistema(), cns_agarroes(), cns_especiais(), cns_supers(), MENOS_2]
    return "".join(c)


# ---------------------------------------------------------------- CMD
COMANDOS_DE_TOQUE = [  # (nome, comando, estado) na ordem de prioridade do [Statedef -1]
    ("fd_y", "~F, D, y", 1201), ("fd_x", "~F, D, x", 1200), ("bd_b", "~B, D, b", 1501), ("bd_a", "~B, D, a", 1500),
    ("bf_b", "~B, F, b", 1701), ("bf_a", "~B, F, a", 1700), ("df_y", "~D, F, y", 1001), ("df_x", "~D, F, x", 1000),
    ("fb_y", "~F, B, y", 1601), ("fb_x", "~F, B, x", 1600), ("df_b", "~D, F, b", 1301), ("df_a", "~D, F, a", 1300),
    ("db_y", "~D, B, y", 1101), ("db_x", "~D, B, x", 1100), ("db_b", "~D, B, b", 1401), ("db_a", "~D, B, a", 1400),
]
NOMES_DE_ESPECIAL = {1000: "Pedra", 1100: "Guarda de Aço", 1200: "Ascensão de Faixa",
                     1300: "Giro de Garagem", 1400: "Corte de Base", 1500: "Pega Bolado", 1600: "Bola de ki",
                     1700: "Rolada de Tatame"}


def montar_cmd():
    K, E = gp.comando, gp.entrada
    c = ["; Gerado por ferramentas/gerar_hazaki.py. Edite lá, não aqui.\n",
         "; x = soco fraco, y = soco forte, a = chute fraco, b = chute forte, c = provocação\n\n",
         "[Remap]\nx = x\ny = y\nz = z\na = a\nb = b\nc = c\ns = s\n\n",
         "[Defaults]\ncommand.time = 15\ncommand.buffer.time = 3\n\n"]
    for b in "abxy":
        c.append(K(f"bfd_{b}", f"~B, F, D, {b}", 22))
    for nome, cmd, _ in COMANDOS_DE_TOQUE:
        c.append(K(nome, cmd, 16))
    c.append(K("bf_y", "~B, F, y", 16))  # agarrão de comando
    for nome, cmd in (("golpe_216", "/F, y"), ("golpe_246", "/F, b"), ("golpe_201", "/B, x"), ("golpe_231", "/B, a")):
        c.append(K(nome, cmd, 1))
    c.append(K("parry", "/F, c", 1, 1))
    c.append(K("FF", "F, F", 10))
    c.append(K("BB", "B, B", 10))
    c.append(K("recovery", "x+a", 1))
    c.append(K("rolar", "x+a", 3))
    c.append(K("afastar", "y+b", 3))
    c.append(K("superpulo", "$D, $U", 10, 6))
    for nome in "xyabc":
        c.append(K(nome, nome, 1, 8 if nome in "xyab" else None))  # botão guardado 8 ticks: a corrente sai na pausa
    c.append(K("start", "s", 1))
    for nome, d in (("holdfwd", "/$F"), ("holdback", "/$B"), ("holdup", "/$U"), ("holddown", "/$D")):
        c.append(K(nome, d, 1))

    c.append("[Statedef -1]\n\n")  # o robô injeta os comandos de teste logo depois desta linha
    ou = lambda estados: " || ".join(f"stateno = {n}" for n in estados)
    # regra B.4: o 1º e o 2º golpe de corrente cancelam em especial no contato; o 3º só se acertou
    no_contato = (200, 210, 230, 240, 400, 430, 201, 301, 311, 321, 331, 340, 342, 344, 346)
    no_acerto = (410, 216, 302, 312, 322, 332)
    c.append("[State -1, Pode cancelar]\ntype = VarSet\ntrigger1 = 1\n"
             f"var(1) = ctrl || (({ou(no_contato)}) && movecontact && movecontact <= 8)"
             f" || (({ou(no_acerto)}) && movehit && movehit <= 8)\n\n")

    no_chao = ["statetype != A"]
    especial_em_super = "(stateno = [1000,1701]) && movehit && movehit <= 8"
    for b in "yx":
        c.append(E("Rapidinho da Quebrada", 3200, [f'command = "bfd_{b}"', "power >= 2000"] + no_chao,
                   ("var(1)", especial_em_super)))
    for b in "ba":
        c.append(E("Faixa no Asfalto", 3000, [f'command = "bfd_{b}"', "power >= 1000"] + no_chao,
                   ("var(1)", especial_em_super)))
    for nome, _, n in COMANDOS_DE_TOQUE:
        cond = [f'command = "{nome}"'] + no_chao
        if n in (1000, 1001, 1600, 1601):
            cond.append("numproj = 0")  # um projétil próprio por vez
        if n in (1700, 1701):
            cond.append("p2dist x > 0")
        c.append(E(NOMES_DE_ESPECIAL[n - n % 100], n, cond))
    c.append(E("Parry", 760, ['command = "parry"', "statetype = S"], ("ctrl",)))
    defendendo = "stateno = 150 || stateno = 152"
    # guard cancel: 1 estoque, depois do 3º quadro de defesa
    c.append('[State -1, Rolamento de defesa]\ntype = VarSet\ntriggerall = command = "rolar"\n'
             f"triggerall = power >= 1000\ntriggerall = time > 3\ntrigger1 = {defendendo}\nvar(8) = 1\n\n")
    c.append('[State -1, Gasta rolamento de defesa]\ntype = PowerAdd\ntriggerall = var(8) = 1\n'
             f'triggerall = command = "rolar"\ntrigger1 = {defendendo}\nvalue = -1000\n\n')
    c.append(E("Rolamento de defesa frente", 700, ["var(8) = 1", 'command = "rolar"', 'command != "holdback"'],
               (defendendo,)))
    c.append(E("Rolamento de defesa tras", 705, ["var(8) = 1", 'command = "rolar"'], (defendendo,)))
    c.append('[State -1, Gasta afastar de defesa]\ntype = PowerAdd\ntriggerall = command = "afastar"\n'
             f"triggerall = power >= 1000\ntriggerall = time > 3\ntrigger1 = {defendendo}\nvalue = -1000\n\n")
    c.append(E("Afastar de defesa", 720, ['command = "afastar"', "power >= 1000", "time > 3"], (defendendo,)))
    c.append(E("Rolar para tras", 705, ['command = "rolar"', 'command = "holdback"', "statetype = S"], ("ctrl",)))
    c.append(E("Rolar", 700, ['command = "rolar"', "statetype = S"], ("ctrl",)))
    c.append(E("Afastar no ar", 650, ['command = "afastar"', "statetype = A"], ("ctrl",)))
    c.append(E("Afastar", 260, ['command = "afastar"', "statetype = S"]))

    # agarrões: colado, oponente fora de stun. O de comando vem antes; o em pé só pega quem está em pé (H-).
    livre = ["stateno != 100", "p2statetype != A", "p2movetype != H"]
    c.append(E("Cutucao Sacana (agarrao)", 830, ['command = "bf_y"', "statetype = S", "p2bodydist x < 12"] + livre,
               ("ctrl",)))
    c.append(E("Puxa a Perna", 840, ['command = "y"', 'command = "holddown"', "statetype != A", "ctrl",
                                     "stateno != 100", "p2bodydist x < 8", "p2statetype = C", "p2movetype != H"],
               ("1",)))
    c.append(E("Abraco de Quebrada", 800, ['command = "y"', '(command = "holdfwd" || command = "holdback")',
                                           "statetype = S", "ctrl", "stateno != 100", "p2bodydist x < 8",
                                           "p2statetype = S", "p2movetype != H"], ("1",)))

    em_pe, sem_baixo = "statetype = S", 'command != "holddown"'
    # kombos de assinatura (o 1º golpe é um normal)
    for n, botao, segura, de in hg.ENTRADAS_KOMBO:
        cond = [f'command = "{botao}"']
        cond.append(f'command = "{segura}"' if segura else sem_baixo)
        if n == 344:
            cond.append('command != "holdfwd"')
        cond.append("statetype != A")
        c.append(E(f"Kombo {n}", n, cond, (f"stateno = {de} && movecontact",)))
    # correntes: 2º e 3º no contato; o finalizador só se o 3º acertou e os acertos contam
    golpe = {g.n: g for g in hg.CORRENTES}
    for botao, (primeiro, segundo, terceiro, final) in hg.CORRENTE_DO_BOTAO.items():
        cond = [f'command = "{botao}"', sem_baixo, em_pe]
        c.append(E(f"Corrente {botao}: final", final, cond,
                   (f"stateno = {terceiro} && movehit && var(10) >= {hg.ACERTOS_DO_FINAL[botao]}",)))
        # o jab duplo (301) só continua depois do 2º jab: os dois acertos contam para o finalizador
        # (time > N: no tick N o HitDef do 2º jab ainda não zerou o movecontact do 1º)
        espera = f" && time > {ativos(ler(golpe[segundo].quadros, 1))[-1][0]}" if segundo == 301 else ""
        c.append(E(f"Corrente {botao}: 3o", terceiro, cond, (f"stateno = {segundo} && movecontact{espera}",)))
        c.append(E(f"Corrente {botao}: 2o", segundo, cond, (f"stateno = {primeiro} && movecontact",)))
    # direcionais
    cancela_fraco = "(stateno = 200 || stateno = 230) && movehit && movehit <= 8"
    c.append(E("Cotovelo de Faixa", 216, ['command = "golpe_216"', em_pe], ("ctrl", cancela_fraco)))
    c.append(E("Machado de Dojo", 246, ['command = "golpe_246"', em_pe], ("ctrl",)))
    c.append(E("Cutucao Sacana", 201, ['command = "golpe_201"', em_pe], ("ctrl",)))
    c.append(E("Coice", 231, ['command = "golpe_231"', em_pe], ("ctrl",)))
    # corrida, passo para trás e provocação
    c.append(E("Corre", 100, ['command = "FF"', em_pe], ("ctrl",)))
    c.append(E("Recua", 105, ['command = "BB"', em_pe], ("ctrl",)))
    c.append(E("Provocacao", 195, ['command = "c"', "statetype != A"], ("ctrl",)))
    # corrente de fracos: até 4 em sequência, no contato
    fracos = "(stateno = 200 || stateno = 400 || stateno = 430 || stateno = 230) && movecontact && var(5) < 4"
    baixo = ['command = "holddown"', "statetype != A"]
    c.append(E("Jab baixo", 400, ['command = "x"'] + baixo, ("ctrl", fracos)))
    c.append(E("Chute na canela", 430, ['command = "a"'] + baixo, ("ctrl", "stateno = 430 && movecontact && var(5) < 4")))
    c.append(E("Joelhada subindo", 410, ['command = "y"'] + baixo, ("ctrl",)))
    c.append(E("Rasteira", 440, ['command = "b"'] + baixo, ("ctrl",)))
    c.append(E("Jab", 200, ['command = "x"', sem_baixo, em_pe], ("ctrl", fracos)))
    c.append(E("Chute baixo", 230, ['command = "a"', sem_baixo, em_pe], ("ctrl",)))
    c.append(E("Soco reto", 210, ['command = "y"', em_pe], ("ctrl",)))
    c.append(E("Chute lateral", 240, ['command = "b"', em_pe], ("ctrl",)))
    for botao, n in zip("xyab", (600, 601, 610, 611)):
        gatilhos = ("ctrl", "(stateno = 600 || stateno = 610) && movehit && movehit <= 8") if n in (601, 611) \
            else ("ctrl",)
        c.append(E("Golpe no ar", n, [f'command = "{botao}"', "statetype = A"], gatilhos))
    return "".join(c)


# ---------------------------------------------------------------- folhas de contato (lidas do .sff gravado)
def contato(pasta, s):
    sys.argv.append("--hazaki")
    import verificar_pengaro as v
    sprites, pal = v.ler_sff()
    pasta.mkdir(parents=True, exist_ok=True)
    fixas = set(carregar_paleta())
    cw, ch, por_pagina = 196, 150, 8

    def celula(tela, cod, x, y, nome):
        d = ImageDraw.Draw(tela)
        d.line((x, y + 130, x + cw - 1, y + 130), fill=(70, 120, 70))
        d.line((x + cw // 2, y + 4, x + cw // 2, y + 130), fill=(84, 84, 96))
        d.text((x + 3, y + 136), nome, fill=(220, 220, 220))
        if cod not in sprites:
            d.text((x + cw // 2 - 20, y + 60), "(podado)", fill=(150, 110, 110))
            return
        w, h, ax, ay, _ = sprites[cod]
        im = v.imagem(sprites[cod], pal)
        tela.alpha_composite(im, (max(0, x + cw // 2 - ax), max(0, y + 130 - ay)))

    paginas = [FOLHAS[i:i + por_pagina] for i in range(0, len(FOLHAS), por_pagina)]
    for p, folhas in enumerate(paginas):
        tela = Image.new("RGBA", (cw * 8, ch * len(folhas)), (58, 58, 66, 255))
        for linha, folha in enumerate(folhas):
            for i in range(8):
                celula(tela, s.codigos[f"f_{folha}{i}"], i * cw, linha * ch, f"{folha} {i}")
        tela.convert("RGB").save(pasta / f"corpo_{p + 1:02d}.png")
    # vítima, projéteis, retratos e faíscas
    outros = [(f"vit{g}", f"vitima {g}") for g, _ in sorted(gp.SPRITES_VITIMA)]
    outros += [(f"fx_lasca{i}", f"lasca {i}") for i in range(8)] + [(f"fx_estatueta{i}", f"estatueta {i}")
                                                                    for i in range(8)]
    outros += [("retrato_p", "retrato 9000,0"), ("retrato_g", "retrato 9000,1"), ("f_agachado4r", "agachado4 recuado")]
    efeitos = [(n, n) for n in s.codigos if n.startswith("fx_") and not n.startswith(("fx_lasca", "fx_estatueta"))]
    efeitos = efeitos[::2]  # um desenho sim, um não: são 2 ticks cada e mudam pouco
    listas = [("outros.png", outros)] + [(f"efeitos_{k // 64 + 1:02d}.png", efeitos[k:k + 64])
                                         for k in range(0, len(efeitos), 64)]
    for arquivo, lista in listas:
        linhas = -(-len(lista) // 8)
        tela = Image.new("RGBA", (cw * 8, ch * linhas), (58, 58, 66, 255))
        for k, (nome, rotulo) in enumerate(lista):
            cod = s.codigos[nome]
            x, y = (k % 8) * cw, (k // 8) * ch
            if cod[0] == 9000 and cod in sprites:
                tela.alpha_composite(v.imagem(sprites[cod], pal), (x + 4, y + 4))
                ImageDraw.Draw(tela).text((x + 3, y + 136), rotulo, fill=(220, 220, 220))
            else:
                celula(tela, cod, x, y, rotulo[:30])
        tela.convert("RGB").save(pasta / arquivo)
    # o corpo saiu com as 15 cores exatas?
    fora = 0
    for folha in FOLHAS:
        for i in range(8):
            cod = s.codigos[f"f_{folha}{i}"]
            if cod in sprites:
                a = np.asarray(v.imagem(sprites[cod], pal))
                fora += len({tuple(c) for c in a[a[..., 3] > 0][:, :3]} - fixas) > 0
    print(f"folhas de contato em {pasta}: {len(paginas)} páginas de corpo + outros.png; "
          f"sprites do corpo com cor fora das 15: {fora}")


def main():
    s = montar_sprites()
    a = montar_air(s, carregar_faiscas(s))
    SAIDA.mkdir(parents=True, exist_ok=True)
    a.txt = gp.ajustar_clsn1(a.txt, s, "")
    air = "\n".join(a.txt)
    for numero, (k, _) in list(a.ativos.items()):  # a faísca nasce na altura da caixa (já encurtada)
        bloco = next(b for b in a.txt if b.startswith(f"[Begin Action {numero}]"))
        caixa = re.search(r"Clsn1\[0\] = (-?\d+),(-?\d+),(-?\d+),(-?\d+)", bloco)
        a.ativos[numero] = (k, tuple(int(v) for v in caixa.groups()))
    cns = gp.ajustar_sparkxy(montar_cns(), a.ativos)
    cmd = montar_cmd()
    # corpo em alta resolução (ferramentas/hd.py): os desenhos 3x de quadros_arcade_hd (ferramentas/hd_guiado.py)
    if (QUADROS.parent / "quadros_arcade_hd").exists():
        import hd
        air, cns = hd.aplicar(s, air, cns, [(QUADROS, QUADROS.parent / "quadros_arcade_hd")], gp.SPRITES_VITIMA)
    # agarrão em pé segura-e-bate (ferramentas/agarrao_mk.py): montado dos golpes que ele já tem, depois do HD
    air, cns = agarrao_mk.aplicar("hazaki", air, cns)
    (SAIDA / "hazaki.cns").write_text(cns.rstrip() + "\n", encoding="utf-8", newline="\n")
    (SAIDA / "hazaki.cmd").write_text(cmd.rstrip() + "\n", encoding="utf-8", newline="\n")
    (SAIDA / "hazaki.air").write_text(air, encoding="utf-8", newline="\n")
    gravados = escrever_sff(SAIDA / "hazaki.sff", s, gp.sprites_mantidos(air, cns))
    (SAIDA / "hazaki.def").write_text(DEF, encoding="utf-8", newline="\n")
    import gerar_sons  # sons próprios: sound = hazaki.snd no .def e PlaySnd/hitsound no .cns (missão 2026-11-14)
    gerar_sons.ligar("hazaki", SAIDA)
    (SAIDA / "movelist.dat").write_text(hg.MOVELIST, encoding="utf-8", newline="\n")
    import parry  # parry em cima e embaixo, faísca própria e sem a "rede de futebol" (docs/parry.md)
    parry.aplicar("hazaki", SAIDA)
    gerar_sons.ligar("hazaki", SAIDA)  # depois do parry: os estados 761/765 dele também tocam o som (F30)
    import balanceamento  # números do item 7 (attack, defence, velocidade)
    balanceamento.aplicar("hazaki", SAIDA)
    import diabo_loiro  # issue #44: pedra, bola de ki e o Diabo Loiro (efeitos do Blender em PNG no .sff)
    diabo_loiro.aplicar(SAIDA)
    import legibilidade  # golpes legíveis (#45): caixa no membro, congelamento, tremida, reação e preparo
    legibilidade.aplicar("hazaki", SAIDA)
    import cena_transformacao  # issue #49: tudo preto, zoom e clarão no Despertar (sempre por último)
    cena_transformacao.aplicar("hazaki", SAIDA)
    print(f"{gravados} sprites no .sff (de {len(s.lista)} carregados), {len(a.acoes)} ações em {SAIDA}")
    if "--contato" in sys.argv:
        contato(Path(sys.argv[sys.argv.index("--contato") + 1]), s)


if __name__ == "__main__":
    main()
