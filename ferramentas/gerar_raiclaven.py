#!/usr/bin/env python3
"""Gera o Raiclaven, o Barbeiro (ficha em docs/fichas/barbeiro.md), sobre o gerador do Gutto/Pengaró.

A lógica do kit (estados, correntes, especiais, agarrões, Despertar) é a mesma; a arte é toda dele (folhas em
sprites/raiclaven/quadros, pedidos em folhas_raiclaven.py), o projétil é um pente e os textos são de barbeiro.
O Despertar (Surto de Tesoura) ainda não tem arte: por enquanto usa as poses normais escurecidas.

  LUTADOR=raiclaven python ferramentas/animar_folha.py --todas   corta as folhas
  python ferramentas/gerar_raiclaven.py --retocar                recorta as folhas arcade e refaz os retoques de anatomia
  python ferramentas/gerar_raiclaven.py                          monta chars/raiclaven
"""
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

import gerar_pengaro as gp

# O Raiclaven herda do Gutto o KIT (poses de base, agarrão de clinch), não a arte: os retoques de desenho e as ações
# que o gerar_gutto.py troca no gerador comum valem só para as folhas do Gutto. As funções do gerador comum são
# guardadas antes de importar o Gutto e devolvidas depois, menos as do kit.
KIT_DO_GUTTO = {"carregar_poses", "cns_agarrao_whisky"}
_COMUNS = {nome: f for nome, f in vars(gp).items() if callable(f) and getattr(f, "__module__", "") == gp.__name__}
_METODOS = {(classe, nome): f for classe in (gp.Sprites, gp.Air) for nome, f in vars(classe).items() if callable(f)}

import gerar_gutto as gg  # noqa: E402

for _nome, _f in _COMUNS.items():
    if _nome not in KIT_DO_GUTTO:
        setattr(gp, _nome, _f)
for (_classe, _nome), _f in _METODOS.items():
    setattr(_classe, _nome, _f)

RAIZ = gp.RAIZ
SAIDA = RAIZ / "chars/raiclaven"
QUADROS = RAIZ / "sprites/raiclaven/quadros"
gp.SAIDA = gg.SAIDA = SAIDA
gp.QUADROS = gg.QUADROS = QUADROS


def pente(escala=2):
    """Pente preto de 16x6 com dentes e brilho cinza: o Pente Voador."""
    img = Image.new("RGBA", (16, 7))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 15, 2], fill=(20, 20, 24, 255))
    d.line([1, 1, 14, 1], fill=(110, 110, 120, 255))
    for x in range(1, 16, 2):
        d.line([x, 3, x, 6], fill=(20, 20, 24, 255))
    return img.resize((img.width * escala, img.height * escala), Image.NEAREST)


class Itens:
    """No lugar do itens_pengaro: o Raiclaven lança pentes e não segura nada além da tesoura."""

    @staticmethod
    def lata():
        return pente(2)

    @staticmethod
    def garrafa():
        return pente(2)

    @staticmethod
    def latas_girando(escala=2):
        p = pente(escala)
        return [p, p.rotate(-90, expand=True), p.rotate(180, expand=True), p.rotate(90, expand=True)]

    @staticmethod
    def com_whisky(img):
        return img


gp.itens_pengaro = gg.Itens = Itens
gp.carregar_poses = lambda: (gg.carregar_poses()[0], Itens.lata())

# Toalha Quente: enrola a toalha (contato no índice 5), gira e joga (índice 10), arruma o pente no fim
gp.AGARRAO_WHISKY = [("agarrao", 1, 3), ("agarrao", 2, 3), ("agarrao", 2, 4), ("agarrao", 3, 4), ("agarrao", 3, 4),
                     ("agarrao", 3, 3), ("agarrao", 4, 4), ("agarrao", 4, 4), ("agarrao", 5, 4), ("agarrao", 5, 4),
                     ("agarrao", 6, 4), ("agarrao", 6, 4), ("agarrao", 7, 4), ("agarrao", 7, 4)]

# Próximo! forte (1701), pedido do Breno: joga o pente, some no talco, aparece nas costas e bate numa sequência própria
# (folha pente_combo) com 3 acertos, no lugar do rolê e chute do Pengaró.
_PROXIMO = gp.extra.N(1701, "Próximo, Cliente! (pente)",
                      "rolamento 1/3 2/3 3/3 4/3 5/3 6/3 pente_combo 1/3A 2/2 3/3A 4/2 5/3A 6/4A 7/8",
                      (6, -104, 76, -50), [70, 20, 20])
gp.FOLHAS = gp.FOLHAS + ("pente_combo",)
gp.extra.ESPECIAIS_A_MAO = tuple(_PROXIMO if m.estado == 1701 else m for m in gp.extra.ESPECIAIS_A_MAO)
_cns_especiais = gp.cns_especiais_extra


def cns_especiais_raiclaven():
    """Os acertos 2 e 3 da sequência do Próximo! forte (o 1º vem do gerador do Pengaró)."""
    txt = _cns_especiais()
    ini, _ = gp.inicios_extra(_PROXIMO)
    extras = "".join(gp.hitdef(1701, f"Time = {ini[a]}", "S, SA", dano, tipo="Light", pausa=(6, 6), hit=16, escorrega=4,
                               vel="-1", classe="especial")
                     for (a, _), dano in zip(gp._trechos_ativos(_PROXIMO)[1:], _PROXIMO.danos[1:]))
    marca = gp.fim(1701)
    return txt.replace(marca, extras + marca, 1)


gp.cns_especiais_extra = cns_especiais_raiclaven


# ================================================================ Pente fino de anatomia (2026-11-11)
# Regra 7: anatomia vem antes da fluidez. Ginga e andar deixam de usar fluxo óptico (64 e 48 quadros que seguravam um
# desenho e trocavam no meio, com o objeto da mão piscando) e as folhas com desenho errado na origem saem da folha
# arcade (quadros/folhas_arcade/<folha>.png), que foi olhada ampliada e medida: figura em pé com 118 px e base em
# y=219, igual às folhas antigas. Só os 8 desenhos, sem quadros do meio: a troca é seca.
ARCADE = ("ginga", "anda", "apanha", "queda", "levanta", "bicicleta", "ar_soco", "rasteirinha")
# loop -> (pasta em quadros/, ticks de cada desenho). O andar da folha é um passo arrastado em guarda (a mesma perna
# na frente nas duas passadas), então são 2 passos de 4 desenhos.
LOOPS_R = {"ginga_fluida": ("ginga", (7,) * 8), "anda_fluida": ("anda", (6,) * 8)}
# A forma despertada ainda não tem arte: ginga e andar aparecem com os desenhos normais.
gp.FLUXO = {nome: (pasta, 1) for nome, (pasta, _) in LOOPS_R.items()}
gp.quadros_do_loop = lambda pasta: len(LOOPS_R[pasta][1])
gp.tempos_do_loop = lambda pasta: LOOPS_R[pasta][1]
gp.quadro_loop = lambda pasta, i: gp.abrir_quadro(QUADROS / LOOPS_R[pasta][0] / f"{i % len(LOOPS_R[pasta][1]):02d}.png")
# Os loops de fluxo ocupavam 64 e 48 grupos do .sff e gp.SPRITES_VITIMA guarda números fixos: as vagas ficam
# reservadas depois do último desenho de cada loop, para nenhum sprite seguinte mudar de número.
VAGAS = {"q_ginga_fluida7": 56, "q_anda_fluida7": 40, "ginga_endiabrada7": 56}
_add = gp.Sprites.add


def _add_com_vagas(self, nome, img, *a, **k):
    if nome in DESENHO_TROCADO:
        img = gp.quadro_folha(*DESENHO_TROCADO[nome])
    saida = _add(self, nome, img, *a, **k)
    self.proximo += VAGAS.get(nome, 0)
    return saida


gp.Sprites.add = _add_com_vagas

# Desenhos errados na origem: o sprite fica com o desenho vizinho da mesma folha, em qualquer ação que o use (o
# estilo seco põe sozinho os desenhos intermediários na recuperação, então trocar só o nome na ação não bastava).
# rasteira 5 tem duas vassouras (uma cobre o pé de trás); martelo 6 ergue a tesoura de novo depois do corte, como um
# segundo golpe; compasso 1 e 6 têm a tesoura saindo do ombro, sem antebraço.
DESENHO_TROCADO = {"f_rasteira5": ("rasteira", 6), "f_martelo6": ("martelo", 7), "f_compasso1": ("compasso", 2),
                   "f_compasso6": ("compasso", 7)}
ACOES_R = {
    5: [("q_ginga_fluida0", 6)],                          # virar: a base da ginga, um desenho só
    100: [(f"q_anda_fluida{i}", 3) for i in range(8)],    # correr: os desenhos do andar na metade do tempo
    # vitória: nos desenhos 1 e 2 o braço de carne some (sobra uma mão no queixo) e o 3 fica a 3 desenhos da base,
    # o que faria o gerador atravessar 1 e 2. Fica base, penteia o cabelo (4, 5) e ergue a tesoura (6, 7), em corte seco.
    181: [("f_vitoria0", 6), ("f_vitoria0", 6), ("f_vitoria4", 6), ("f_vitoria5", 6), ("f_vitoria4", 6),
          ("f_vitoria5", 6), ("f_vitoria6", 6), ("f_vitoria7", -1)],
    # tesourada no ar: na folha arcade a tesoura sobe no desenho 2 (na antiga era no 3) e desce no 4
    600: [("f_ar_soco1", 2), ("f_ar_soco2", 3), ("f_ar_soco4", 8, (8, -86, 50, -62)), ("f_ar_soco6", -1)],
}
_acao = gp.Air.acao


def _acao_raiclaven(self, numero, quadros, *a, **k):
    return _acao(self, numero, ACOES_R.get(numero, quadros), *a, **k)


gp.Air.acao = _acao_raiclaven


def _hsv(a):
    import cv2
    hsv = cv2.cvtColor(np.ascontiguousarray(a[..., :3]), cv2.COLOR_RGB2HSV_FULL).astype(float)
    return hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255


def _rgb(h, s, v):
    import cv2
    hsv = np.stack([h * 255 / 360, s * 255, v * 255], axis=-1)
    return cv2.cvtColor(np.clip(hsv.round(), 0, 255).astype(np.uint8), cv2.COLOR_HSV2RGB_FULL)


def calca_das_folhas_antigas(img):
    """A folha arcade pinta a calça de roxo-azulado (matiz 277) e as antigas de marrom-escuro (326). Enquanto o
    lutador mistura as duas, a calça arcade vai para a cor antiga, senão ela troca de cor a cada golpe."""
    a = np.array(img)
    h, s, v = _hsv(a)
    m = (a[..., 3] >= 128) & (h >= 250) & (h < 300) & (s >= .25) & (s <= .75) & (v <= .45)
    a[..., :3] = np.where(m[..., None], _rgb(318 + (h - 250) * 17 / 50, s * .85, v * .8), a[..., :3])
    return Image.fromarray(a)


def cortar_arcade():
    """quadros/folhas_arcade/<folha>.png -> quadros/<folha>/00..07.png, com o mesmo recorte das folhas antigas
    (animar_folha.poses) e sem quadros do meio. As pastas de fluxo óptico saem."""
    os.environ["LUTADOR"] = "raiclaven"
    import animar_folha as af
    for nome in ARCADE:
        destino = QUADROS / nome
        shutil.rmtree(destino / "meio", ignore_errors=True)
        for i, pose in enumerate(af.poses(QUADROS / "folhas_arcade" / f"{nome}.png", "pes", 1)):
            pose.putalpha(pose.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
            calca_das_folhas_antigas(af.sem_magenta(pose)).save(destino / f"{i:02d}.png")
        print(f"{nome}: 8 desenhos da folha arcade")
    for pasta in ("ginga_fluida", "anda_fluida", "ginga_endiabrada", "endiabrado"):  # endiabrado: refeito do desenho novo
        shutil.rmtree(QUADROS / pasta, ignore_errors=True)


def _quadros(folha, *nomes):
    """Arquivos de uma folha: '04' é o desenho, '03_5' o quadro do meio, '05_*' todos os do intervalo."""
    for nome in nomes:
        base = QUADROS / folha / ("meio" if "_" in nome else "")
        yield from sorted(base.glob(f"{nome}.png"))


def _retoque(arquivo, funcao):
    a = np.array(Image.open(arquivo).convert("RGBA"))
    n = funcao(a)
    Image.fromarray(a).save(arquivo)
    return n


def apagar_soltos(caixa):
    """Apaga os pedaços inteiros dentro da caixa (x0, y0, x1, y1) que não encostam no resto da figura."""
    def f(a):
        import cv2
        n, rot, st, _ = cv2.connectedComponentsWithStats((a[..., 3] >= 128).astype(np.uint8), connectivity=8)
        x0, y0, x1, y1 = caixa
        total = 0
        for i in range(1, n):
            x, y, w, h, area = st[i]
            if x >= x0 and y >= y0 and x + w - 1 <= x1 and y + h - 1 <= y1:
                a[rot == i] = 0
                total += int(area)
        return total
    return f


def fechar_furos(caixa, limite=40):
    """Furo transparente pequeno, todo cercado de corpo, dentro da caixa: pintado com a cor dos vizinhos."""
    def f(a):
        import cv2
        n, rot, st, _ = cv2.connectedComponentsWithStats((a[..., 3] < 128).astype(np.uint8), connectivity=4)
        x0, y0, x1, y1 = caixa
        m = np.zeros(a.shape[:2], np.uint8)
        for i in range(1, n):
            x, y, w, h, area = st[i]
            if area <= limite and x >= x0 and y >= y0 and x + w - 1 <= x1 and y + h - 1 <= y1:
                m[rot == i] = 255
        a[..., :3] = cv2.inpaint(np.ascontiguousarray(a[..., :3]), m, 3, cv2.INPAINT_TELEA)
        a[m > 0, 3] = 255
        return int((m > 0).sum())
    return f


def metal_vira_pele(caixa, sombra=(104, 44, 30), claro=(214, 124, 80)):
    """Dentro da caixa, o cinza do braço de metal é repintado com a rampa da pele (mesma luz relativa, em 4 blocos)."""
    def f(a):
        x0, y0, x1, y1 = caixa
        m = np.zeros(a.shape[:2], bool)
        m[y0:y1 + 1, x0:x1 + 1] = True
        rgb = a[..., :3].astype(int)
        mx, mn = rgb.max(-1), rgb.min(-1)
        m &= (a[..., 3] >= 128) & (mx - mn <= 45) & (mx >= 75)
        if m.any():
            lum = rgb.mean(-1)
            lo, hi = np.percentile(lum[m], 5), np.percentile(lum[m], 95)
            t = np.round(np.clip((lum - lo) / max(1, hi - lo), 0, 1) * 3) / 3
            cor = np.array(sombra) * (1 - t[..., None]) + np.array(claro) * t[..., None]
            a[m, :3] = cor[m].astype(np.uint8)
        return int(m.sum())
    return f


def pele_sem_estouro(caixa, teto=.78):
    """Braço de carne pintado mais vermelho e mais claro que o rosto: o brilho da pele volta para a faixa da base."""
    def f(a):
        x0, y0, x1, y1 = caixa
        h, s, v = _hsv(a)
        m = np.zeros(a.shape[:2], bool)
        m[y0:y1 + 1, x0:x1 + 1] = True
        m &= (a[..., 3] >= 128) & ((h < 25) | (h > 350)) & (s > .45) & (v > teto + .05)  # o que já passou fica
        a[..., :3] = np.where(m[..., None], _rgb(np.where(h > 350, 9, np.maximum(h, 9)), s, teto + (v - teto) * .2),
                              a[..., :3])
        return int(m.sum())
    return f


def retocar():
    """Refaz o pente fino nos desenhos de sprites/raiclaven/quadros. Pode rodar de novo: cada passo só mexe no que
    ainda está errado. Depois de rodar animar_folha.py numa dessas folhas, rode isto outra vez."""
    cortar_arcade()
    passos = [
        # bola (Pente Voador): no 4 o pente já voando está desenhado no corpo e o jogo solta o projétil no mesmo
        # quadro (dois pentes); no 2 o braço de carne levantado veio pintado de metal (dois braços de metal)
        ("bola", ("04", "03_[456]", "04_[123]"), apagar_soltos((200, 112, 250, 150))),
        ("bola", ("02", "01_[456]", "02_[123]"), metal_vira_pele((178, 100, 204, 132))),
        # rolamento (Próximo!): caco branco parado no ar à direita, do desenho 2 até o talco
        ("rolamento", ("02", "01_[456]", "02_*", "03_*", "04_[123]"), apagar_soltos((214, 170, 228, 186))),
        # compasso: ombreira furada pelo recorte (o fundo aparecia através dela)
        ("compasso", ("0[0-7]", "0[0-6]_*"), fechar_furos((138, 95, 182, 148))),
        # vitória: braço que penteia o cabelo mais vermelho e claro que o rosto
        ("vitoria", ("04", "05", "04_*"), pele_sem_estouro((185, 85, 240, 150))),
    ]
    for folha, nomes, funcao in passos:
        print(folha, nomes, sum(_retoque(arquivo, funcao) for arquivo in _quadros(folha, *nomes)), "px")
    # quadros do meio derretidos ou que atravessam desenho errado: saem, a troca fica seca
    #   rolamento 5->6: lâminas em onda e cabeça deformada; vitória 0->3: o braço de carne some; 5->6: pose inteira muda
    #   e os que nascem dos desenhos trocados em DESENHO_TROCADO (rasteira 5, martelo 6, compasso 1 e 6)
    for folha, nomes in (("rolamento", ("05_*",)), ("vitoria", ("00_*", "01_*", "02_*", "05_*")),
                         ("rasteira", ("04_*", "05_*")), ("martelo", ("05_*", "06_*")),
                         ("compasso", ("00_*", "01_*", "05_*", "06_*"))):
        for arquivo in _quadros(folha, *nomes):
            arquivo.unlink()
    # Despertar: as duas pastas eram a provocação recortada com resto de magenta entre o braço e o tronco. Sem arte
    # própria ainda, ficam com os desenhos limpos da provocação.
    for pasta in ("despertar_a", "despertar_b"):
        shutil.rmtree(QUADROS / pasta, ignore_errors=True)
        shutil.copytree(QUADROS / "provoca", QUADROS / pasta)


gp.VITORIAS = [
    "Próximo!",
    "Vai querer na régua?",
    "Deixa que eu capricho.",
    "Ficou um degradê lindo, hein?",
    "A casa agradece a preferência.",
    "Não mexe a cabeça que eu corto a orelha.",
    "Cabelo e barba: pago na saída.",
    "Volta daqui a quinze dias pra manutenção.",
]

DEF = """; Gerado por ferramentas/gerar_raiclaven.py. Edite lá, não aqui.
[Info]
name = "Raiclaven"
displayname = "Raiclaven"
versiondate = 11,10,2026
mugenversion = 1.1
author = "Breno"
pal.defaults = 1
localcoord = 320,240

[Files]
cmd = raiclaven.cmd
cns = raiclaven.cns
st = raiclaven.cns
stcommon = common1.cns
sprite = raiclaven.sff
anim = raiclaven.air
movelist = movelist.dat

[Palette Keymap]
x = 1
"""

# mesmos comandos do kit, com os nomes de barbeiro da ficha
GOLPES = (gg.GOLPES
          .replace("Beijinho (reto)", "Pente Voador").replace("Beijinho em Arco", "Borrifada")
          .replace("Chute Giratório (coice)", "Tesoura Helicóptero").replace("Joelhada Voadora", "Tesoura Voadora")
          .replace("Carrinho", "Varrida").replace("Cotovelo Giratório / Cotovelada Pesada", "Tesourão / Machadada de Tesoura")
          .replace("Chute de Quina / Pisão de Quina", "Cadeira Giratória").replace("Teleporte de Ginga", "Próximo!")
          .replace("Chuva de Beijinhos", "Próximo, Cliente!").replace("Bando de Chutes / Fúria do Cavalo", "Máquina Explosiva")
          .replace("Endiabrado", "Surto de Tesoura").replace("Agarrão agachado", "Cabeça na Pia")
          .replace("Clinch e Joelhada", "Toalha Quente"))


def main():
    if "--retocar" in sys.argv:
        return retocar()
    gg.preparar_pastas()
    SAIDA.mkdir(parents=True, exist_ok=True)
    s = gp.montar_sprites()
    faiscas = gp.carregar_faiscas(s)
    a = gp.montar_air(s, faiscas, arte_despertada=gp.arte_endiabrada(s))
    preset = gp.preset_despertado(s)
    (SAIDA / "raiclaven.air").write_text("\n".join(a.txt), encoding="utf-8", newline="\n")
    cns = gp.sem_ginga_9203(gp.remapear_animelem(gp.montar_cns(), a.mapas))
    cns = cns.replace("add = 12, 0, 28", "add = 14, 14, 18").replace("sinadd = 10, 0, 18, 40", "sinadd = 10, 10, 14, 40")
    cns = cns.replace("[Data]", preset + "[Quotes]\n" + "".join(
        f'victory{i + 1} = "{v}"\n' for i, v in enumerate(gp.VITORIAS)) + "\n[Data]", 1)
    air = "\n".join(a.txt)
    # corpo em alta resolução (ferramentas/hd.py): os mesmos quadros em 3x, de quadros_hd/ (animar_folha.py com HD=3)
    if (QUADROS.parent / "quadros_hd").exists():
        import hd
        air, cns = hd.aplicar(s, air, cns, [(QUADROS, QUADROS.parent / "quadros_hd")], gp.SPRITES_VITIMA)
        (SAIDA / "raiclaven.air").write_text(air, encoding="utf-8", newline="\n")
    else:
        print("ATENÇÃO: sem sprites/raiclaven/quadros_hd (fica fora do git: ~200-340 MB). O lutador sai em 1x, borrado. "
              "Gere com: python ferramentas/hd_blender.py raiclaven  (uns 20 min; depois rode este gerador de novo)")
    (SAIDA / "raiclaven.cns").write_text(cns, encoding="utf-8", newline="\n")
    gp.escrever_sff(SAIDA / "raiclaven.sff", s, manter=gp.sprites_mantidos(air, cns))
    (SAIDA / "raiclaven.cmd").write_text(gp.montar_cmd(), encoding="utf-8")
    (SAIDA / "raiclaven.def").write_text(DEF, encoding="utf-8", newline="\n")
    (SAIDA / "movelist.dat").write_text(GOLPES, encoding="utf-8", newline="\n")
    print(f"{len(s.lista)} sprites, {len(a.acoes)} ações em {SAIDA}")


if __name__ == "__main__":
    main()
