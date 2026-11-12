"""Aura do Pengaró endiabrado (boss final) no jogo: as camadas do Blender ligadas pelo ferramentas/aura.py.

Camadas prontas em sprites/pengaro/aura/ (ferramentas/aura_blender/pengaro_aura.py, ver docs/arcade/aura_blender.md):
coluna 48, chicotes 48, anel_tras 96, fiapos 96, soltos 96 (atrás) e anel_frente 96 (à frente, da sola para baixo),
todas 360x200 com o pé do lutador em (180, 190), 2 tiques por quadro.

No jogo viram 4 camadas (Explods 9600 a 9603, [Statedef -4]):
  9600 anel_tras    chão rachado atrás dos pés; fica no chão no pulo (plano "chao")
  9601 coluna       coluna + chicotes + fiapos num desenho só: foram contornados juntos no Blender e as línguas saem
                    das pontas dos chicotes; separados, a deriva do motor e o início de cada camada os descolariam
  9602 anel_frente  a metade da frente do chão rachado: rasteira (no máximo 13% da altura do lutador acima dos pés),
                    alfa até 0,5 contando o surto; plano "chao" com prioridade de frente, para ficar no chão no pulo
                    junto com a metade de trás. Os dois anéis nascem no mesmo quadro, sem deriva e trocam de quadro
                    no mesmo tique (Camada.tique), senão as rachaduras não se encontram
  9603 soltos       pedras e elos de corrente em órbita, deriva própria (período curto: com a deriva lenta da coluna,
                    as duas andavam juntas, correlação -0,95 no filme de 2026-11-12)
Troca de quadro: anéis e pedras no tique par, coluna no ímpar. A coluna e as pedras dividem o alto da tela; trocando
juntas, um tique tinha desenho novo e o seguinte não (p95/mediana 2,6-2,7 no filme de 2026-11-12, limite 2,5).
Entrada em 44 tiques (o aura.py usa 26): a coluna é 1,5x mais alta que o lutador e densa; em 26 tiques a borda dela
cruzava o alto da tela num pulo (6,5x a mudança do laço, limite 5).
Nada vai na frente do corpo além do anel rasteiro.

As cores das camadas NÃO entram na escolha da paleta do .sff (Sprites.fora_da_paleta): a paleta da forma base sai
idêntica e a aura é levada para a cor mais perto dela.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

import aura

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "sprites/pengaro/aura"
FRENTE_ALTURA, FRENTE_ALFA = aura.Aura.FRENTE_ALTURA, aura.Aura.FRENTE_ALFA
ALTURA_LUTADOR = 110

# Liga junto com o boss: Despertar (var 20), o super exclusivo 3100 e a cena da transformação desde que ele aparece
# ajoelhado de casaco (estado 2000, Time 83), como a aura antiga (AURA_LIGADA de gerar_pengaro.py).
LIGADA = "var(20) > 0 || StateNo = 3100 || (StateNo = 2000 && Time >= 83)"
# Surto: os três supers e o instante em que o boss se levanta na transformação.
SURTO = "((StateNo = 3000 || StateNo = 3100 || StateNo = 3200) && Time = 1) || (StateNo = 2000 && Time = 86)"


def _ler(info, nome):
    n = next(c["quadros"] for c in info["camadas"] if c["nome"] == nome)
    return [np.asarray(Image.open(PASTA / info["arquivo"].format(nome=nome, quadro=q)).convert("RGBA")) for q in range(n)]


def _sobre(*camadas):
    """Uma camada só, desenhada na ordem dada, num laço do tamanho da mais longa (as de 48 repetem 2 vezes em 96)."""
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
    assert info["tela"] == [360, 200] and info["tiques_por_quadro"] == 2, info
    pe = tuple(info["pe"])
    coluna = _sobre(_ler(info, "coluna"), _ler(info, "chicotes"), _ler(info, "fiapos"))
    anel_tras, anel_frente, soltos = (_ler(info, n) for n in ("anel_tras", "anel_frente", "soltos"))

    # a metade da frente é rasteira: nada acima de 13% do lutador acima da sola
    topo = min(np.nonzero((q[..., 3] >= 128).any(axis=1))[0].min() for q in anel_frente)
    assert pe[1] - topo <= FRENTE_ALTURA * ALTURA_LUTADOR + 0.5, f"anel_frente sobe {pe[1] - topo} px acima dos pés"

    parado = aura.Movimento(deriva=(0, 0), alfa=0.92, respira=0.08, respira_periodo=96)
    frente = aura.Movimento(deriva=(0, 0), alfa=0.37, respira=0.1, respira_periodo=96)
    camadas = [
        aura.Camada("anel_tras", anel_tras, plano="chao", eixo=pe, inicio=1, tique=0, prioridade=-7, mov=parado),
        aura.Camada("coluna", coluna, plano="tras", eixo=pe, tique=1, prioridade=-6,
                    mov=aura.Movimento(deriva=(1.6, 1.4), deriva_periodo=170, alfa=0.9, respira=0.1)),
        aura.Camada("anel_frente", anel_frente, plano="chao", eixo=pe, inicio=1, tique=0, prioridade=5, mov=frente,
                    surto_alfa=0.08),
        aura.Camada("soltos", soltos, plano="tras", eixo=pe, tique=0, prioridade=-4,
                    mov=aura.Movimento(deriva=(2.4, 3.0), deriva_periodo=70, alfa=0.95, respira=0.06)),
    ]
    f = camadas[2]
    assert f.mov.alfa * (1 + f.mov.respira) + f.surto_alfa <= FRENTE_ALFA + 1e-6, "anel_frente opaco demais"
    assert camadas[0].troca(0) == camadas[2].troca(2), "as metades do anel trocam de quadro em tiques diferentes"
    return aura.Aura("pengaro", camadas, ligada=LIGADA, surto=SURTO, base=9600, entra=44,
                     altura_lutador=ALTURA_LUTADOR)


def ligar(sprites):
    """Monta a aura, põe os quadros no .sff (fora da escolha da paleta) e devolve a Aura (para .air e .cns)."""
    a = montar()
    a.conferir(grupos={t[0] for t in sprites.lista})
    entrou = a.registrar(sprites)
    sprites.fora_da_paleta = getattr(sprites, "fora_da_paleta", set()) | entrou
    return a


if __name__ == "__main__":
    print(montar().resumo())
