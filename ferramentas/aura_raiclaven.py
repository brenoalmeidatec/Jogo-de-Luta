"""Aura do Raiclaven despertado (o Cientista Louco e a parceira) no jogo: as camadas do Blender ligadas pelo ferramentas/aura.py.

Camadas prontas em sprites/raiclaven/aura/ (ferramentas/aura_blender/raiclaven_aura.py): leque, foices, raios, lascas e
limalha, todas atrás, 96 quadros, 360x200 com o pé do lutador em (180, 190), 2 tiques por quadro. Até a issue #38
(2026-11-14) elas estavam prontas mas NÃO eram ligadas no gerar_raiclaven.py: por isso o Breno não via aura nenhuma.

No jogo viram 2 camadas (Explods 9600 e 9601, [Statedef -4]), atrás de qualquer lutador (o mais baixo de um lutador é o
-3 do caído morto, estado 5150 do common1):
  9600 leque   leque de lâminas + foices + raios num desenho só: o aura.json manda rodar as três juntas (o raio acompanha
               as pontas das lâminas quadro a quadro). Cor de aço com raio branco-prata, como pede a #43 (Breno,
               2026-11-14) e o docs/arcade/bosses_kit.md. Fica no chão no pulo (no_chao),
               como as auras do CK e do Pengaró: o leque nasce do chão, aberto embaixo (sprpriority -7)
  9601 chao    lascas de aço cravadas no chão + limalha subindo, na frente da base do leque (sprpriority -6)
Troca de quadro: o leque no tique ímpar e o chão no par.
Saída presa ao contador (resta), como no CK: o fade acaba no tique em que o var(20) chega a 0 e o corpo volta.

As cores das camadas vão para a paleta própria do despertado (Sprites.paleta_propria, 3ª paleta do .sff), junto com o
cientista e a parceira: a paleta fixa da forma base não tem verde.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

import aura

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "sprites/raiclaven/aura"
SAI = 34                     # tiques do fade de saída (o padrão do aura.py)
PRIORIDADE_MIN_LUTADOR = -3  # common1.cns.zss, estado 5150 (caído morto)
CIENTISTA = 56               # tique da cena do Despertar (estado 2000) em que começa a 2ª metade (o cientista pronto)

RESTA = (f"ifelse(StateNo = 2000, ifelse(Time >= {CIENTISTA}, 999, 0), "
         f"ifelse(StateNo = 3100 && var(37) = 1, max(var(20), -AnimTime), var(20)))")
LIGADA = f"({RESTA}) > 0"
SURTO = f"((StateNo = 3000 || StateNo = 3100 || StateNo = 3200) && Time = 1) || (StateNo = 2000 && Time = {CIENTISTA})"


def _ler(info, nome):
    n = next(c["quadros"] for c in info["camadas"] if c["nome"] == nome)
    return [np.asarray(Image.open(PASTA / info["arquivo"].format(nome=nome, quadro=q)).convert("RGBA")) for q in range(n)]


def _sobre(*camadas):
    n = max(len(c) for c in camadas)
    assert all(n % len(c) == 0 for c in camadas)
    saida = []
    for q in range(n):
        img = Image.fromarray(camadas[0][q % len(camadas[0])], "RGBA")
        for c in camadas[1:]:
            img.alpha_composite(Image.fromarray(c[q % len(c)], "RGBA"))
        saida.append(np.asarray(img))
    return saida


def montar():
    info = json.loads((PASTA / "aura.json").read_text(encoding="utf-8"))
    assert info["lutador"] == "raiclaven" and info["tela"] == [360, 200] and info["tiques_por_quadro"] == 2, info
    assert all(c["plano"] == "atras" for c in info["camadas"]), "camada do Raiclaven fora de 'atras': rever a montagem"
    pe = tuple(info["pe"])
    raios = _ler(info, "raios")  # aço com raio branco-prata (Breno, #43); o verde fica no corpo (cabelo, óculos, tanques)
    leque = _sobre(_ler(info, "leque"), _ler(info, "foices"), raios)
    chao = _sobre(_ler(info, "lascas"), _ler(info, "limalha"))
    camadas = [
        aura.Camada("leque", leque, plano="tras", no_chao=True, eixo=pe, tique=1, prioridade=-7, cresce=False,
                    mov=aura.Movimento(deriva=(0.8, 1.0), deriva_periodo=170, alfa=0.95, respira=0.06)),
        aura.Camada("chao", chao, plano="tras", no_chao=True, eixo=pe, tique=0, prioridade=-6, cresce=False,
                    mov=aura.Movimento(deriva=(1.0, 0), deriva_periodo=130, alfa=0.95, respira=0.05),
                    surto_tremor=1.0),
    ]
    assert all(c.prioridade < PRIORIDADE_MIN_LUTADOR for c in camadas), "camada da aura na frente de um lutador"
    return aura.Aura("raiclaven", camadas, ligada=LIGADA, surto=SURTO, base=9600, entra=44, sai=SAI, virada_fundo=0.6,
                     resta=RESTA)


def ligar(sprites):
    """Monta a aura, põe os quadros no .sff (fora da escolha da paleta) e devolve a Aura (para .air e .cns)."""
    a = montar()
    a.conferir(grupos={t[0] for t in sprites.lista})
    entrou = a.registrar(sprites)
    # na paleta própria do despertado (gerar_pengaro.escrever_sff), com o verde dos raios; não na da forma base
    sprites.paleta_propria = getattr(sprites, "paleta_propria", set()) | entrou
    return a


if __name__ == "__main__":
    print(montar().resumo())
