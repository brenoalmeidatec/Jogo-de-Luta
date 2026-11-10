#!/usr/bin/env python3
"""Gera o Raiclaven, o Barbeiro (ficha em docs/fichas/barbeiro.md), sobre o gerador do Gutto/Pengaró.

A lógica do kit (estados, correntes, especiais, agarrões, Despertar) é a mesma; a arte é toda dele (folhas em
sprites/raiclaven/quadros, pedidos em folhas_raiclaven.py), o projétil é um pente e os textos são de barbeiro.
O Despertar (Surto de Tesoura) ainda não tem arte: por enquanto usa as poses normais escurecidas.

  LUTADOR=raiclaven python ferramentas/animar_folha.py --todas   corta as folhas
  python ferramentas/gerar_raiclaven.py                          monta chars/raiclaven
"""
import shutil

from PIL import Image, ImageDraw

import gerar_gutto as gg

gp = gg.gp
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
    gg.preparar_pastas()
    SAIDA.mkdir(parents=True, exist_ok=True)
    s = gp.montar_sprites()
    faiscas = gp.carregar_faiscas(s)
    a = gp.montar_air(s, faiscas, arte_despertada=gp.arte_endiabrada(s))
    preset = gp.preset_despertado(s)
    (SAIDA / "raiclaven.air").write_text("\n".join(a.txt), encoding="utf-8", newline="\n")
    cns = gp.remapear_animelem(gp.montar_cns(), a.mapas)
    cns = cns.replace("add = 12, 0, 28", "add = 14, 14, 18").replace("sinadd = 10, 0, 18, 40", "sinadd = 10, 10, 14, 40")
    cns = cns.replace("[Data]", preset + "[Quotes]\n" + "".join(
        f'victory{i + 1} = "{v}"\n' for i, v in enumerate(gp.VITORIAS)) + "\n[Data]", 1)
    (SAIDA / "raiclaven.cns").write_text(cns, encoding="utf-8", newline="\n")
    gp.escrever_sff(SAIDA / "raiclaven.sff", s, manter=gp.sprites_mantidos("\n".join(a.txt), cns))
    (SAIDA / "raiclaven.cmd").write_text(gp.montar_cmd(), encoding="utf-8")
    (SAIDA / "raiclaven.def").write_text(DEF, encoding="utf-8", newline="\n")
    (SAIDA / "movelist.dat").write_text(GOLPES, encoding="utf-8", newline="\n")
    print(f"{len(s.lista)} sprites, {len(a.acoes)} ações em {SAIDA}")


if __name__ == "__main__":
    main()
