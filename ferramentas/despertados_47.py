#!/usr/bin/env python3
"""Agarrão da forma e poder de longe de cada despertado (issue #47 do Breno, 2026-11-14): Pengaró, Gutto e CK.

  python ferramentas/despertados_47.py [lutador ...]      (sem nome: os três) reescreve chars/<l>/ .sff .air .cns .cmd
                                                          e o movelist.dat. Roda de novo sem duplicar nada.

O Hazak (Diabo Loiro, #44) tem o dele no diabo_loiro.py. O Raiclaven (Cientista Louco, #43) entrou aqui depois
(Cadeira Elétrica e Secador de Raio); o gerar_raiclaven.py chama `aplicar` no fim.

Agarrão da forma (estado 4700 -> 4710), no lugar do agarrão da forma básica enquanto var(20) > 0 (o Despertar):
  mesmo comando (y ou b com → ou ← colado), mesma pega e mesmo escape do agarrão segura-e-bate
  (ferramentas/agarrao_mk.py, de onde vem a montagem), mas as pancadas são golpes da forma desperta e o efeito
  da forma fica preso no oponente o tempo todo (ação 47000), com um estouro próprio no golpe que solta (47001):
    Pengaró  Algema das Sombras: correntes de sombra sobem do chão e enrolam o oponente; elos voam no final
    Gutto    Coice do Garanhão: raios caem em cima dele; o final solta ferraduras de raio
    CK       Paredão na Cara: as caixas de som estouram nele; o final é um estrondo
Poder de longe (estado 4750, ↓ → ↓ → + x ou y, só no Despertar, um por vez na tela):
  brilho de carga na mão (47003) e a torrente da forma (47002), que atravessa o oponente (projremove = 0) com
  3 acertos que derrubam e um estouro (47004) em cada acerto. O rastro nasce curto e estica (sprites 100+):
    Pengaró  Maré das Correntes: bola de sombra violeta com rastro de miolo branco, fumaça preta e três correntes
    Gutto    Estouro do Garanhão: o garanhão da aura sai correndo, com torrente de raio vermelho atrás
    CK       Paredão no Talo: arcos de som em fila na ponta de uma torrente verde de fumaça
Régua: o Diabo Loiro do Hazak (#44), que o Breno aprovou em 2026-11-14: 8 tons do preto ao branco passando pela cor
da forma, torrente em camadas, fumaça preta nas bordas, estouro em cada pancada do agarrão (47004).
Gutto: a aura do garanhão (sprites/gutto/aura) entra no jogo por aqui (aura_gutto, [Statedef -4], Explods 9600 e
9601), como as asas do Diabo Loiro. O cavalo some da aura enquanto o poder corre: é ele que saiu.

Os desenhos saem do Blender (ferramentas/despertados_47_blender.py), em sprites/efeitos_blender/<l>/d47_*/. Vão
para o .sff como PNG de 32 bits (grupos 47000 a 47004), igual aos efeitos da #38, pelo efeitos.gravar. Rode depois do
gerador, do parry.py e do efeitos.py (eles regravam o .sff).
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))
import agarrao_mk as mk  # noqa: E402
import conferir_sff as cs  # noqa: E402
import efeitos  # noqa: E402

LUTADORES = ("pengaro", "gutto", "ck", "raiclaven")
GRUPOS = {"agarrao": 47000, "final": 47001, "poder": 47002, "carga": 47003, "pancada": 47004}
NASCE = 5        # quadros em que o rastro do poder cresce atrás dele ao sair da mão (sprites 100+ do grupo do poder)
AURA_GUTTO = "garanhao"   # nome da aura do Gutto no aura.py (Explods e grupos 9600 e 9601)
MARCA = "(despertados_47.py)"
ESCALA = efeitos.ESCALA_BLENDER  # o mesmo tamanho de pixel dos outros efeitos do Blender


class Cfg:
    def __init__(self, nome_agarrao, golpes, final, prio_agarrao, nome_poder, solta, offset, vel, som_carga,
                 som_solta, som_acerto, som_final=None, mao=None, prio_poder=4):
        self.nome_agarrao, self.golpes, self.final = nome_agarrao, golpes, final
        self.prio_agarrao = prio_agarrao          # sprpriority do efeito preso no oponente (CK atrás dele)
        self.nome_poder, self.solta, self.offset, self.vel = nome_poder, solta, offset, vel
        # sons das formas da issue #46 (docs/sons.md): corrente do Pengaró 50,7; paredão do CK 50,5/50,2;
        # coice/galope/relincho do Gutto 50,5/50,2/50,3; 53,k é o acerto endiabrado. O gerar_sons.py não mexe
        # nestes estados (4700, 4710, 4750): os sons vêm daqui.
        self.som_carga, self.som_solta, self.som_acerto = som_carga, som_solta, som_acerto
        self.som_final = som_final or som_solta
        self.prio_poder = prio_poder            # sprpriority do projétil (o do Gutto nasce em cima dele: vai atrás)
        self.mao = mao or offset                  # onde a carga brilha (no Gutto o projétil nasce no pé da aura)


# padrão do Breno (#47): tela escurece e tinge na cor da forma enquanto o golpe da forma acontece; clarão no impacto
TINTA = {"pengaro": ("120,96,150", "70,20,110"), "gutto": ("150,90,90", "120,20,20"),
         "ck": ("110,130,115", "40,90,60"), "raiclaven": ("95,125,100", "40,120,20")}   # (BGPalFX mul do fundo, PalFX add no oponente atingido)

# Desenhos próprios do despertado, feitos pelo boneco de peças (firme.py + kit_<lutador>_e, 2026-11-17): o agarrão
# e o poder param de emprestar golpes do modo antigo (regra do Breno: o despertado não reaproveita nada).
#   agarrao: pasta em sprites/<pecas>/quadros_pecas_hd/ com os desenhos e o tempos.json; vira o grupo grupo_agarrao
#            (só os desenhos-chave, na ordem da folha), e o roteiro do agarrão é o `proprio` (agarrao_mk.Proprio)
#   poder:   a animação inteira (com os quadros do meio) vira o grupo grupo_poder e a ação dele; a torrente sai no
#            tick em que começa o desenho-chave `solta_chave`
B = mk.Batida
PECAS47 = {
    "pengaro": {
        "pecas": "pengaro_e", "agarrao": "algema", "grupo_agarrao": 47100, "poder": "mare", "grupo_poder": 47150,
        "solta_chave": "mare/03",
        # 0 guarda, 1 a mão aberta avança, 2 alcança o pescoço, 3 aperta (corrente enrola), 4 ergue no alto,
        # 5 bate no chão, 6 e 7 volta
        "proprio": mk.Proprio("Algema das Sombras", segura=3,
                              batidas=(B(prep=(3,), bate=4, dano=34, alto=True, som="S53,2"),),
                              final=B(prep=(4,), bate=5, dano=62, alto=False, som="S53,2"),
                              solta=(6, 7), alcanca=(1, 2), bind=50, fim="derruba"),
    },
    "ck": {
        "pecas": "ck_e", "agarrao": "paredao", "grupo_agarrao": 47100, "poder": "talo", "grupo_poder": 47150,
        "solta_chave": "talo/03",
        # 0 guarda, 1 dá o passo com a mão aberta, 2 alcança a gola, 3 fecha o punho e puxa, 4 empurra a cara na
        # caixa de som, 5 puxa de novo com o corpo todo, 6 afunda a cara na caixa, 7 volta
        "proprio": mk.Proprio("Paredão na Cara", segura=3,
                              batidas=(B(prep=(3,), bate=4, dano=34, alto=True, som="S53,0"),),
                              final=B(prep=(5,), bate=6, dano=62, alto=True, som="S53,0"),
                              solta=(7,), alcanca=(1, 2), bind=50, fim="derruba"),
    },
}
EIXO_HD = (540, 660)  # pés na tela 3x do boneco de peças


def pecas_tempos(lutador, anim):
    c = PECAS47[lutador]
    pasta = RAIZ / "sprites" / c["pecas"] / "quadros_pecas_hd" / anim
    return pasta, json.loads((pasta / "tempos.json").read_text(encoding="utf-8"))


def pecas_chaves(lutador):
    """Índice do primeiro desenho de cada desenho-chave do agarrão, na ordem da folha."""
    pasta, t = pecas_tempos(lutador, PECAS47[lutador]["agarrao"])
    vistos = {}
    for e in t["elementos"]:
        vistos.setdefault(e["de"], e["desenho"])
    return pasta, [vistos[k] for k in sorted(vistos)]


def pecas_sprites(lutador):
    """[(grupo, índice, Image, eixo x, eixo y)] dos desenhos do boneco de peças (tela 3x, pés em 540,660)."""
    if lutador not in PECAS47:
        return []
    c = PECAS47[lutador]
    out = []
    pasta, chaves = pecas_chaves(lutador)
    pp, tp = pecas_tempos(lutador, c["poder"])
    lista = [(c["grupo_agarrao"], k, pasta / f"{d:02d}.png") for k, d in enumerate(chaves)]
    lista += [(c["grupo_poder"], e["desenho"], pp / f"{e['desenho']:02d}.png") for e in tp["elementos"]]
    for g, i, arq in lista:
        im = Image.open(arq).convert("RGBA")
        x0, y0, x1, y1 = im.getbbox()
        out.append((g, i, im.crop((x0, y0, x1, y1)), EIXO_HD[0] - x0, EIXO_HD[1] - y0))
    return out


def acao_poder_corpo(lutador):
    """Ação do corpo no poder (os desenhos do boneco de peças, com os quadros do meio, no tempo do kit)."""
    c = PECAS47[lutador]
    _, t = pecas_tempos(lutador, c["poder"])
    linhas = [f"; {CFG[lutador].nome_poder}: corpo do boneco de peças {MARCA}", "Clsn2Default: 1",
              " Clsn2[0] = -72, 0, 72, -312"]
    linhas += [f"{c['grupo_poder']},{e['desenho']}, 0,0, {e['ticks']}" for e in t["elementos"]]
    return "\n".join(linhas)


def solta_poder(lutador):
    """Tick em que a torrente sai: o começo do desenho-chave da mão empurrando."""
    if lutador not in PECAS47:
        return CFG[lutador].solta
    c = PECAS47[lutador]
    _, t = pecas_tempos(lutador, c["poder"])
    tick = 0
    for e in t["elementos"]:
        if e["de"] == c["solta_chave"]:
            return tick
        tick += e["ticks"]
    raise SystemExit(f"{lutador}: {c['solta_chave']} não está no {c['poder']}")


G = mk.Golpe
CFG = {
    "pengaro": Cfg("Algema das Sombras", (G(3433, 26, "palma torta"), G(3410, 26, "revolta de corrente"),
                                          G(3430, 26, "mão de chão possuída")), G(3413, 62, "roda da possessão"), -1,
                   "Maré das Correntes", 25, (60, -52), 3.0, "F40,4", "50,7", "S53,2"),
    "gutto": Cfg("Coice do Garanhão", (G(3433, 26, "palma"), G(3420, 26, "calcanhar"), G(3410, 26, "revolta")),
                 G(3423, 62, "coice final"), 4, "Estouro do Garanhão", 25, (0, 0), 3.6, "50,3", "50,2", "S53,2", "50,5", mao=(40, -56), prio_poder=-2),
    "ck": Cfg("Paredão na Cara", (G(3433, 26, "palma"), G(3410, 26, "revolta"), G(3421, 26, "afastar pesado")),
              G(3413, 62, "roda"), -1, "Paredão no Talo", 22, (50, -78), 3.2, "50,2", "50,5", "S53,0"),
    # Cientista Louco (#43): ele segura, ela corta; raio verde dos tanques no agarrado, lascas de aço no final.
    # O poder sai do secador dela, lá no alto das costas dele. Sons do .snd dele: 50,7 máquina zumbindo,
    # 50,8 máquina explodindo, 50,9 navalha (gerar_sons.ESPECIAIS)
    # Os golpes são os do kit próprio dele (kit_raiclaven.py, regra da seção 4): rode o kit antes.
    "raiclaven": Cfg("Cadeira Elétrica", (G(20210, 26, "navalhada"), G(20270, 26, "secador na cara"),
                                          G(20301, 26, "garra")), G(20303, 62, "dentes e chacoalha"), 4,
                     "Secador de Raio", 25, (45, -92), 3.4, "50,7", "50,9", "S53,2", "50,8"),
}


# ---------------------------------------------------------------------------------------------------------------- .sff
def desenhos(lutador, efeito):
    pasta = efeitos.BLENDER / lutador / f"d47_{efeito}"
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    ims = [Image.open(pasta / f"{i:02d}.png").convert("RGBA") for i in range(meta["quadros"])]
    return ims, meta


def gravar_sff(sff, lutador, aura=None):
    pal, nos, _ = cs.ler(sff)
    rle, png, vistos = [], [], set()
    for n in nos:
        k = (n["g"], n["i"])
        proprios = {PECAS47[lutador][x] for x in ("grupo_agarrao", "grupo_poder")} if lutador in PECAS47 else set()
        if k in vistos or n["g"] in GRUPOS.values() or n["g"] in proprios or (aura and n["g"] in aura.ids()):
            continue
        vistos.add(k)
        (png if n.get("png") else rle).append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
    for efeito, g in GRUPOS.items():
        ims, meta = desenhos(lutador, efeito)
        px, py = meta["pivo"]
        for i, img in enumerate(ims):
            png.append((g, i, img.width, img.height, int(px), int(py), efeitos.blob_png(img)))
        if efeito == "poder":
            for j, img in enumerate(nascendo(lutador)):
                png.append((g, 100 + j, img.width, img.height, int(px), int(py), efeitos.blob_png(img)))
    for g, k, img, ex, ey in pecas_sprites(lutador):
        png.append((g, k, img.width, img.height, int(ex), int(ey), efeitos.blob_png(img)))
    if aura:
        for g, k, img, ex, ey in aura.sprites():
            png.append((g, k, img.width, img.height, int(ex), int(ey), efeitos.blob_png(img)))
    efeitos.gravar(sff, pal, rle, png)


def nascendo(lutador):
    """Os primeiros quadros do poder com o rastro cortado, crescendo: ele sai da mão curto e estica para trás, em vez
    de nascer já com o rastro inteiro atravessando as costas do lutador."""
    ims, meta = desenhos(lutador, "poder")
    px = int(meta["pivo"][0])
    corpo = int(meta.get("corpo", ims[0].height // 2))     # daqui para a frente nunca corta (a cabeça, o cavalo)
    saida = []
    for j in range(NASCE):
        img = ims[j % len(ims)].copy()
        corte = max(0, round((px - corpo) * (1 - (j + 1) / (NASCE + 1))))
        if corte:
            img.paste((0, 0, 0, 0), (0, 0, corte, img.height))
        saida.append(img)
    return saida


def acao_poder(lutador):
    g = GRUPOS["poder"]
    _, meta = desenhos(lutador, "poder")
    linhas = [f"[Begin Action {g}]", f"; poder do despertado, issue #47 {MARCA}", "Clsn2Default: 1",
              f" Clsn2[0] = {clsn_projetil(lutador)}", "Clsn1Default: 1", f" Clsn1[0] = {clsn_projetil(lutador)}"]
    linhas += [f"{g},{100 + j}, 0,0, 2" for j in range(NASCE)]
    linhas.append("Loopstart")
    linhas += [f"{g},{i}, 0,0, {meta['ticks']}" for i in range(meta["quadros"])]
    return "\n".join(linhas)


# --------------------------------------------------------------------------------------------------------------- aura
def aura_gutto():
    """A aura do Gutto despertado (o garanhão de raio vermelho, sprites/gutto/aura) ligada no jogo pelo aura.py, como
    as asas do Diabo Loiro (diabo_loiro.montar_aura): o cavalo, os raios e as ferraduras atrás dele, as crateras em
    brasa no chão. Enquanto o Estouro do Garanhão está na tela o cavalo some da aura: é ele que saiu correndo."""
    import numpy as np
    import aura
    pasta = RAIZ / "sprites/gutto/aura"
    info = json.loads((pasta / "aura.json").read_text(encoding="utf-8"))
    assert info["tela"] == [360, 200] and info["tiques_por_quadro"] == 2, info

    def ler(nome):
        n = next(c["quadros"] for c in info["camadas"] if c["nome"] == nome)
        return [Image.open(pasta / info["arquivo"].format(nome=nome, quadro=k)).convert("RGBA") for k in range(n)]

    def sobre(*camadas):
        n = max(len(c) for c in camadas)
        out = []
        for k in range(n):
            img = camadas[0][k % len(camadas[0])].copy()
            for c in camadas[1:]:
                img.alpha_composite(c[k % len(c)])
            out.append(np.asarray(img))
        return out
    pe = tuple(info["pe"])
    camadas = [
        aura.Camada("garanhao", sobre(ler("raios"), ler("garanhao"), ler("ferraduras")), plano="tras", eixo=pe,
                    tique=1, prioridade=-6, cresce=False, esconde="NumProjID(4750) > 0 || StateNo = 4750",
                    mov=aura.Movimento(deriva=(0.6, 1.5), deriva_periodo=120, alfa=0.95, respira=0.06)),
        aura.Camada("crateras", sobre(ler("crateras")), plano="tras", no_chao=True, eixo=pe, tique=0, prioridade=-5,
                    cresce=False, mov=aura.Movimento(deriva=(1.0, 0), deriva_periodo=130, alfa=0.92, respira=0.06)),
    ]
    surto = "((StateNo = 3000 || StateNo = 3100 || StateNo = 3200) && Time = 1) || (StateNo = 4710 && Time = 1)"
    return aura.Aura(AURA_GUTTO, camadas, ligada="var(20) > 0", surto=surto, base=9600, entra=30, sai=34,
                     virada_fundo=0.6, resta="var(20)")


def ligar_aura(a, air, cns):
    """Põe (ou troca) as ações e o [Statedef -4] da aura. Falha se o lutador já tiver outro -4."""
    for g in a.ids():
        air = re.sub(rf"(?:^; Aura {a.nome},[^\n]*\n)?^\[Begin Action {g}\]\n.*?(?=^\[Begin Action|^; Aura |\Z)", "", air,
                     flags=re.M | re.S)
    air = air.rstrip() + "\n\n" + a.air()
    m = re.search(r"^\[Statedef -4\]\n.*\Z", cns, re.M | re.S)
    if m:
        assert f"Aura animada '{a.nome}'" in m.group(0), "o lutador já tem um [Statedef -4] que não é desta aura"
        cns = cns[:m.start()]
    return air, cns.rstrip() + "\n\n" + a.cns(cabecalho=True)


# ---------------------------------------------------------------------------------------------------------------- .air
def acao_efeito(lutador, efeito, escala=ESCALA, clsn=None):
    g = GRUPOS[efeito]
    ims, meta = desenhos(lutador, efeito)
    linhas = [f"[Begin Action {g}]", f"; {efeito} do despertado, issue #47 {MARCA}"]
    if clsn:
        linhas += ["Clsn2Default: 1", f" Clsn2[0] = {clsn}", "Clsn1Default: 1", f" Clsn1[0] = {clsn}"]
    for i in range(meta["quadros"]):
        if i == meta["laco"] and meta["laco"] >= 0:
            linhas.append("Loopstart")
        esc = f", , , {escala:g}, {escala:g}" if escala != 1 else ""
        linhas.append(f"{g},{i}, 0,0, {meta['ticks']}{esc}")
    return "\n".join(linhas)


def clsn_projetil(lutador):
    """Caixa do projétil: 80% do desenho. O motor desenha o projétil no projscale, mas mede a caixa na escala do
    lutador ([Size] 1/3), então a caixa vai em 3x."""
    ims, meta = desenhos(lutador, "poder")
    if "clsn" in meta:
        return ", ".join(str(round(v * 3)) for v in meta["clsn"])
    w, h = ims[0].size
    esc = escala_poder(lutador)
    mx = round((w - meta["pivo"][0]) * esc * 0.8 * 3)       # o corpo vai do pivô para a frente; o rastro não bate
    my = round(h * esc * 0.36 * 3)
    return f"-{mx}, -{my}, {mx}, {my}"


def escala_poder(lutador):
    """Escala do projétil na tela: a dos efeitos do Blender, ou a do desenho (o garanhão da aura do Gutto)."""
    return desenhos(lutador, "poder")[1].get("escala", ESCALA)


# ---------------------------------------------------------------------------------------------------------------- .cns
def ctl(n, nome, tipo, *linhas):
    return mk.ctl(n, f"{nome} {MARCA}", tipo, *linhas)


def statedef(cns, n):
    m = re.search(rf"^\[Statedef {n}\]\n.*?(?=^\[Statedef|^; ---- |\Z)", cns, re.M | re.S)
    return m.group(0) if m else None


def tirar_estados(cns, numeros):
    for n in numeros:
        # para também nos marcadores de bloco de outras ferramentas (o "; >>> aura_silhueta.py estado" logo depois do
        # 4750 ia junto, e a aura de silhueta duplicava o helper 9610)
        m = re.search(rf"^\[Statedef {n}\]\n.*?(?=^\[Statedef|^; ---- |^; >>> |^; <<< |\Z)", cns, re.M | re.S)
        if m:
            cns = cns[:m.start()] + cns[m.end():]
    return cns


def estados_agarrao(lutador, air, cns):
    c = CFG[lutador]
    alcance = None
    if lutador in PECAS47:  # desenhos próprios (boneco de peças): roteiro Proprio, como os agarrões da #45
        r = PECAS47[lutador]["proprio"]
        g = PECAS47[lutador]["grupo_agarrao"]
        refs = [f"{g},{k}" for k in range(len(pecas_chaves(lutador)[1]))]
        tabela = mk.acoes(air)
        els = mk.elementos(tabela[800])
        pega_el = next((e for e in els if e[4]), els[0])
        quadros, contatos = mk.montar_proprio(r, refs, pega_el[3])
        # a tentativa (4700) com os desenhos da mão avançando, na caixa de acerto da 800 de hoje
        cx = pega_el[4]
        alcance = ("[Begin Action 4700]\n" + f"; {r.nome}: a mão avança (boneco de peças) {MARCA}\n"
                   + "Clsn2Default: 1\n" + "".join(f" {b}\n" for b in pega_el[3])
                   + f"{refs[r.alcanca[0]]}, 0,0, 3\n"
                   + ("Clsn1: 1\n" + f" Clsn1[0] = {cx[0]}, {cx[1]}, {cx[2]}, {cx[3]}\n" if cx else "")
                   + f"{refs[r.alcanca[-1]]}, 0,0, 6\n\n")
        texto, _ = mk.estados(r, contatos, None, 820, r.fim)
    else:
        chave = f"{lutador}_47"
        base = mk.ROTEIROS[lutador]
        mk.ROTEIROS[chave] = mk.Roteiro(c.nome_agarrao, c.golpes, c.final, base.pega, base.bind)
        try:
            r, quadros, contatos, _ = mk.montar(chave, air, cns)
        finally:
            del mk.ROTEIROS[chave]
        texto, _ = mk.estados(r, contatos, None, 820)  # só o 810; os estados do oponente são os do agarrão básico
    acao = mk.acao_810(quadros, r).replace("[Begin Action 810]", "[Begin Action 4710]")
    texto = (texto.replace("[Statedef 810]", "[Statedef 4710]").replace("anim = 810", "anim = 4710")
             .replace("[State 810,", "[State 4710,"))
    fim = contatos[-1][0]
    primeiro = contatos[0][0]
    xf, yf = contatos[-1][4], contatos[-1][5]
    extra = (
        ctl(4710, "Efeito da forma no oponente", "Explod", f"trigger1 = Time = {max(1, primeiro - 6)}",
            "trigger1 = NumTarget", f"anim = {GRUPOS['agarrao']}", f"id = {GRUPOS['agarrao']}", "postype = p1",
            f"pos = {r.bind}, 0", "bindtime = -1", "removetime = -1", f"sprpriority = {c.prio_agarrao}",
            "ownpal = 1", "ignorehitpause = 1")
        + ctl(4710, "Tira o efeito", "RemoveExplod", f"trigger1 = Time = {fim}", f"trigger2 = !NumTarget",
              f"id = {GRUPOS['agarrao']}")
        + ctl(4710, "Estouro do final", "Explod", f"trigger1 = Time = {fim}", "trigger1 = NumTarget",
              f"anim = {GRUPOS['final']}", "postype = p1", f"pos = {xf}, {yf}", "removetime = -2",
              "sprpriority = 6", "ownpal = 1", "pausemovetime = 12", "scale = .8, .8")
        + ctl(4710, "Fundo escurece na cor da forma", "BGPalFX", "trigger1 = Time = 1", "trigger1 = NumTarget",
              f"time = {fim + 20}", f"mul = {TINTA[lutador][0]}", "sinadd = 0,0,0,0")
        + "".join(ctl(4710, f"Pancada {k + 1}: tremida", "EnvShake", f"trigger1 = Time = {t}", "trigger1 = NumTarget",
                      "time = 8", "freq = 140", "ampl = -4") for k, (t, *_r) in enumerate(contatos[:-1]))
        + "".join(ctl(4710, f"Pancada {k + 1}: oponente pisca", "PalFX", f"trigger1 = Time = {t}",
                      "trigger1 = NumTarget", "redirectid = target,id", "time = 6", f"add = {TINTA[lutador][1]}")
                  for k, (t, *_r) in enumerate(contatos))
        + "".join(ctl(4710, f"Pancada {k + 1}: estouro da forma", "Explod", f"trigger1 = Time = {t}",
                      "trigger1 = NumTarget", f"anim = {GRUPOS['pancada']}", "postype = p1",
                      f"pos = {_r[3]}, {_r[4]}", "removetime = -2", "sprpriority = 6", "ownpal = 1",
                      "scale = 1.5, 1.5", "ignorehitpause = 1") for k, (t, *_r) in enumerate(contatos[:-1]))
        + ctl(4710, "Final: congela no impacto", "Pause", f"trigger1 = Time = {fim}", "trigger1 = NumTarget",
              "time = 12", "movetime = 0")
        + ctl(4710, "Final: clarão", "BGPalFX", f"trigger1 = Time = {fim}", "time = 6", "add = 120,120,120",
              f"mul = {TINTA[lutador][0]}")
        + ctl(4710, "Final: tremida forte", "EnvShake", f"trigger1 = Time = {fim}", "time = 30", "freq = 90",
              "ampl = -11")
        + ctl(4710, "Som do final", "PlaySnd", f"trigger1 = Time = {fim}", f"value = {c.som_final}")
        + ctl(4710, "Som de pegar", "PlaySnd", "trigger1 = Time = 0", "value = F35,0")
        + ctl(4710, "Som da forma", "PlaySnd", f"trigger1 = Time = {max(1, primeiro - 6)}", "trigger1 = NumTarget",
              f"value = {c.som_solta}", "channel = 3")
    )
    # entra antes do "Fim" do 4710
    texto = texto.replace("[State 4710, Fim]", extra + "[State 4710, Fim]", 1)
    pega = statedef(cns, 800)
    assert pega and "p1stateno = 810" in pega, f"{lutador}: [Statedef 800] sem p1stateno = 810"
    pega = (pega.replace("[Statedef 800]", "[Statedef 4700]").replace("[State 800,", "[State 4700,")
            .replace("p1stateno = 810", "p1stateno = 4710"))
    if alcance:
        pega = re.sub(r"(?m)^anim\s*=\s*800\b", "anim = 4700", pega)
        acao = alcance + acao
    pega = f"; Agarrão do despertado: {c.nome_agarrao} (issue #47) {MARCA}\n" + pega
    return acao, pega.rstrip() + "\n\n" + texto, r, contatos


def estado_poder(lutador):
    c = CFG[lutador]
    s = solta_poder(lutador)
    ox, oy = c.offset
    anim = PECAS47[lutador]["grupo_poder"] if lutador in PECAS47 else 3400
    t = [f"; Poder de longe do despertado: {c.nome_poder} (issue #47) {MARCA}\n",
         "[Statedef 4750]\ntype = S\nmovetype = A\nphysics = S\nctrl = 0\nsprpriority = 2\n" f"anim = {anim}\n"
         "juggle = 4\nvelset = 0,0\npoweradd = 0\n\n"]
    esc = escala_poder(lutador)
    t.append(ctl(4750, "Som da carga", "PlaySnd", "trigger1 = Time = 0", f"value = {c.som_carga}"))
    # carga: o mundo para e escurece, só ele se mexe (SuperPause), com rastro do corpo e a carga crescendo na mão
    t.append(ctl(4750, "Carga: tudo para e escurece", "SuperPause", "trigger1 = Time = 0", f"time = {s}",
                 f"movetime = {s}", "anim = -1", "darken = 1", "poweradd = 0", "unhittable = 0"))
    t.append(ctl(4750, "Carga: rastro do corpo", "AfterImage", "trigger1 = Time = 0", f"time = {s + 14}",
                 "length = 8", "timegap = 2", "framegap = 2", "trans = add", f"palcolor = 0",
                 f"paladd = {TINTA[lutador][1]}", "palmul = .55,.55,.55"))
    t.append(ctl(4750, "Carga na mão", "Explod", f"trigger1 = Time = {max(0, s - 20)}",
                 f"anim = {GRUPOS['carga']}", "postype = p1", f"pos = {c.mao[0] - 6}, {c.mao[1]}", "bindtime = -1",
                 "removetime = -2", "sprpriority = 5", "ownpal = 1", "supermovetime = 30"))
    t.append(ctl(4750, "Carga: treme de leve", "EnvShake", f"trigger1 = Time = {max(0, s - 14)}", "time = 14",
                 "freq = 180", "ampl = -2"))
    t.append(ctl(4750, "Som de soltar", "PlaySnd", f"trigger1 = Time = {s}", f"value = {c.som_solta}"))
    t.append(ctl(4750, "Solta: tremida forte", "EnvShake", f"trigger1 = Time = {s}", "time = 26", "freq = 100",
                 "ampl = -7"))
    t.append(ctl(4750, "Solta: fundo na cor da forma", "BGPalFX", f"trigger1 = Time = {s}", "time = 70",
                 f"mul = {TINTA[lutador][0]}"))
    t.append(ctl(4750, "Solta: recuo", "VelSet", f"trigger1 = Time = {s}", "x = -2.2"))
    t.append(ctl(4750, "Solta: freia", "VelMul", f"trigger1 = Time > {s}", "x = .8"))
    t.append(ctl(4750, c.nome_poder, "Projectile", f"trigger1 = Time = {s}",
                 "projid = 4750", f"projanim = {GRUPOS['poder']}", f"projhitanim = {GRUPOS['pancada']}",
                 f"projremanim = {GRUPOS['pancada']}", f"projscale = {esc:g}, {esc:g}", "projhits = 3", "projremove = 0", "projremovetime = 170",
                 "projmisstime = 7", "projpriority = 5", f"projsprpriority = {c.prio_poder}", f"offset = {ox}, {oy}",
                 f"velocity = {c.vel}, 0", "attr = S, SP", "damage = 42, 6", "animtype = Heavy",
                 "guardflag = MA", "hitflag = MAFD", "pausetime = 14, 18", "sparkno = -1", "guard.sparkno = S9202",
                 "envshake.time = 24", "envshake.freq = 90", "envshake.ampl = -9", f"hitsound = {c.som_acerto}",
                 "guardsound = F6,0", "ground.type = High", "ground.slidetime = 14", "ground.hittime = 18",
                 "ground.velocity = -3.5, -4", "air.velocity = -3, -4", "fall = 1", "fall.recover = 0",
                 "air.fall = 1", "down.velocity = -3, -4", "down.hittime = 18", "palfx.time = 14",
                 f"palfx.add = {TINTA[lutador][1]}", "palfx.sinadd = 30,30,30,4"))
    t.append(ctl(4750, "Fim", "ChangeState", "trigger1 = AnimTime = 0", "value = 0", "ctrl = 1"))
    return "".join(t)


def ligar_cns(lutador, air, cns):
    cns = tirar_estados(cns, (4700, 4710, 4750))
    # conserto: uma rodada antiga levou o marcador de início do helper da aura de silhueta (9610) junto com o 4750;
    # sem ele o aura_silhueta.py não acha o bloco e põe outro 9610. Tira o bloco órfão (o aura_silhueta.py refaz)
    if "; >>> aura_silhueta.py estado" not in cns:
        cns = re.sub(r"^\[Statedef 9610\]\n.*?^; <<< aura_silhueta\.py[^\n]*\n", "", cns, count=1, flags=re.M | re.S)
    cns = re.sub(rf"^; (Agarrão|Poder de longe) do despertado:[^\n]*{re.escape(MARCA)}\n", "", cns, flags=re.M)
    acao, texto, r, contatos = estados_agarrao(lutador, air, cns)
    bloco = texto + "\n" + estado_poder(lutador)
    # antes dos estados do oponente do agarrão (bloco do agarrao_mk, no fim do .cns)
    i = cns.index(mk.MARCA)
    cns = cns[:i].rstrip() + "\n\n" + bloco.rstrip() + "\n\n" + cns[i:]
    return acao, cns, r, contatos


# ---------------------------------------------------------------------------------------------------------------- .cmd
CMD_PODER = '[Command]\r\nname = "poder47"\r\ncommand = ~D, F, D, F, {b}\r\ntime = 30\r\n\r\n'


def ligar_cmd(lutador, cmd):
    cmd = re.sub(rf"\[State -1, [^\]]*{re.escape(MARCA)}\]\r?\n.*?\r?\n\r?\n", "", cmd, flags=re.S)
    cmd = re.sub(r'\[Command\]\r?\nname = "poder47"\r?\n.*?\r?\n\r?\n', "", cmd, flags=re.S)
    nl = "\r\n" if "\r\n" in cmd else "\n"
    # comando: antes do primeiro [Command] (vem antes de "bola_fraca" ~D, F, x)
    i = cmd.index("[Command]")
    cmd = cmd[:i] + (CMD_PODER.format(b="x") + CMD_PODER.format(b="y")).replace("\r\n", nl) + cmd[i:]
    # agarrão do despertado: uma cópia de cada entrada do agarrão básico, antes dela, com var(20) > 0
    partes = re.split(r"(?=\[State -1, Agarrao\])", cmd)
    out = [partes[0]]
    for p in partes[1:]:
        bloco = re.match(r"\[State -1, Agarrao\].*?(?:\r?\n){2}", p, re.S)
        if bloco and re.search(r"^value = 800\r?$", bloco.group(0), re.M):
            novo = (bloco.group(0).replace("[State -1, Agarrao]", f"[State -1, Agarrao do despertado {MARCA}]")
                    .replace("value = 800", "value = 4700"))
            novo = re.sub(r"(value = 4700\r?\n)", rf"\1triggerall = var(20) > 0{nl}", novo, count=1)
            novo = re.sub(r"(?m)^[^\n]*\(kit_raiclaven\.py\)[^\n]*\n", "", novo)  # a trava do modo normal não vem junto
            out.append(novo)
        out.append(p)
    cmd = "".join(out)
    # poder: logo no começo do [Statedef -1], antes dos especiais de meia-lua
    poder = (f"[State -1, Poder de longe do despertado {MARCA}]{nl}type = ChangeState{nl}value = 4750{nl}"
             f'triggerall = command = "poder47"{nl}triggerall = var(20) > 0{nl}triggerall = statetype != A{nl}'
             f"triggerall = NumProjID(4750) = 0{nl}trigger1 = ctrl{nl}{nl}")
    m = re.search(r"^\[Statedef -1\][^\n]*\n(?:[^\[\n][^\n]*\n)*\r?\n?", cmd, re.M)
    cmd = cmd[:m.end()] + poder + cmd[m.end():]
    assert cmd.count("value = 4700") >= 1, f"{lutador}: não achei o agarrão básico no .cmd"
    return cmd


# ---------------------------------------------------------------------------------------------------------------- movelist
def ligar_movelist(lutador, texto):
    c = CFG[lutador]
    texto = re.sub(rf"^.*\(#47\).*\n", "", texto, flags=re.M)
    linhas = (f"{c.nome_poder} <#bebebe>(poder de longe) (#47)</>\t\t_D_F_D_F^P\n"
              f"{c.nome_agarrao} <#bebebe>(agarrão da forma) (#47)</>\t\t_F/_B+^Y\n")
    chave = ":Exclusivos do Despertar:</>\n"
    if chave in texto:
        return texto.replace(chave, chave + linhas, 1)
    return texto.rstrip("\n") + "\n" + linhas


# ---------------------------------------------------------------------------------------------------------------- tudo
def aplicar(lutador, pasta=None):
    pasta = Path(pasta) if pasta else RAIZ / "chars" / lutador
    arq = {e: pasta / f"{lutador}.{e}" for e in ("sff", "air", "cns", "cmd")}
    air = arq["air"].read_text(encoding="utf-8")
    cns = arq["cns"].read_text(encoding="utf-8")
    cmd = arq["cmd"].read_bytes().decode("utf-8")
    acao, cns, r, contatos = ligar_cns(lutador, air, cns)
    if acao.startswith("[Begin Action 4700]"):
        a4700, acao = acao.split("[Begin Action 4710]", 1)
        acao = "[Begin Action 4710]" + acao
        air = efeitos.por_acao(air, 4700, a4700.split("\n", 1)[1])
    air = efeitos.por_acao(air, 4710, acao.split("\n", 1)[1])
    if lutador in PECAS47:
        air = efeitos.por_acao(air, PECAS47[lutador]["grupo_poder"], acao_poder_corpo(lutador))
    for efeito in ("agarrao", "final", "carga", "pancada"):
        air = efeitos.por_acao(air, GRUPOS[efeito], acao_efeito(lutador, efeito).split("\n", 1)[1])
    air = efeitos.por_acao(air, GRUPOS["poder"], acao_poder(lutador).split("\n", 1)[1])
    aura = aura_gutto() if lutador == "gutto" else None
    if aura:
        air, cns = ligar_aura(aura, air, cns)
    air = re.sub(r"\n{3,}", "\n\n", air)
    cmd = ligar_cmd(lutador, cmd)
    gravar_sff(arq["sff"], lutador, aura)
    arq["air"].write_text(air, encoding="utf-8", newline="\n")
    arq["cns"].write_text(cns, encoding="utf-8", newline="\n")
    arq["cmd"].write_bytes(cmd.encode("utf-8"))
    mv = pasta / "movelist.dat"
    if mv.exists():
        mv.write_text(ligar_movelist(lutador, mv.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    if aura:
        import aura_no_corpo  # o garanhão segue o corpo (issue #51): refaz a tabela no [Statedef -4] que a aura regravou
        aura_no_corpo.aplicar(lutador, pasta)
    print(f"{lutador}: {r.nome} ({len(contatos) - 1} pancadas + final, dano {sum(x[1] for x in contatos)}, "
          f"solta no tick {contatos[-1][0]}); {CFG[lutador].nome_poder} (3 x 42)")


def main():
    for l in sys.argv[1:] or LUTADORES:
        aplicar(l)


if __name__ == "__main__":
    main()
