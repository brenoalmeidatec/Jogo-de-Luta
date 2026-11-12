"""Aura do Pengaró endiabrado (boss final) no jogo: as camadas do Blender ligadas pelo ferramentas/aura.py.

Camadas prontas em sprites/pengaro/aura/ (ferramentas/aura_blender/pengaro_aura.py, ver docs/arcade/aura_blender.md):
coluna 48, chicotes 48, anel_tras 96, fiapos 96, soltos 96 (atrás) e anel_frente 96 (à frente, da sola para baixo),
todas 360x200 com o pé do lutador em (180, 190), 2 tiques por quadro.

No jogo viram 4 camadas (Explods 9600 a 9603, [Statedef -4]), todas ATRÁS de qualquer lutador:
  9600 anel_tras    chão rachado atrás dos pés; fica no chão no pulo (plano "chao", sprpriority -7)
  9601 coluna       coluna + chicotes + fiapos num desenho só: foram contornados juntos no Blender e as línguas saem
                    das pontas dos chicotes; separados, a deriva do motor e o início de cada camada os descolariam.
                    Nasce do chão e FICA no chão no pulo e na queda (no_chao): presa ao corpo, a base reta dela
                    virava um prato solto no ar (filme de 2026-11-12). Não apaga com a altura (sprpriority -6)
  9602 anel_frente  a metade da frente do chão rachado, na frente da coluna e ATRÁS dos lutadores (sprpriority -5:
                    o mais baixo de um lutador é o -3 do caído morto, estado 5150 do common1). Com prioridade 5 ela
                    tingia os pés dos dois lutadores e o Pengaró caído. Mesmo alfa, mesma escala e mesma posição da
                    metade de trás (sem respirar e sem tremor, que têm fase por camada): as duas metades nunca
                    descolam. Os dois anéis nascem no mesmo quadro, sem deriva e trocam de quadro no mesmo tique
                    (Camada.tique), senão as rachaduras não se encontram
  9603 soltos       pedras e elos de corrente em órbita, deriva própria (período curto: com a deriva lenta da coluna,
                    as duas andavam juntas, correlação -0,95 no filme de 2026-11-12); acompanham o corpo
Troca de quadro: anéis e pedras no tique par, coluna no ímpar. A coluna e as pedras dividem o alto da tela; trocando
juntas, um tique tinha desenho novo e o seguinte não (p95/mediana 2,6-2,7 no filme de 2026-11-12, limite 2,5).
Entrada em 44 tiques (o aura.py usa 26): a coluna é 1,5x mais alta que o lutador e densa; em 26 tiques a borda dela
cruzava o alto da tela num pulo (6,5x a mudança do laço, limite 5).
Nada vai na frente de corpo nenhum.
Virada: a aura apaga só até 60% do alfa (virada_fundo) antes de trocar de lado; com os 30% do aura.py o boss sumia
a cada troca de lado (pixels roxos de 52 mil para 5 mil no filme de 2026-11-12). O espelho de um desenho destes muda
~3,5x o passo de um quadro, então a 60% ele não vira corte.
Desliga ANTES de o corpo voltar: o fade de saída (34 tiques) acaba no tique em que o var(20) chega a 0 (o corpo volta
à forma base nesse tique, pelo RemapSprite do -2). Desligando no 0, a aura do endiabrado ficava cheia em volta do corpo
de calça branca por uns 15 tiques. O mesmo no fim do super 3100 (que zera o var(20) no começo): pelo AnimTime.

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
ALTURA_LUTADOR = 110
SAI = 34          # tiques do fade de saída (o padrão do aura.py)
PRIORIDADE_MIN_LUTADOR = -3  # common1.cns.zss, estado 5150 (caído morto); nenhum lutador de chars/ desce disso

# Liga junto com o boss: Despertar (var 20), o super exclusivo 3100 e a cena da transformação desde que ele aparece
# ajoelhado de casaco (estado 2000, Time 83), como a aura antiga do gerador. Desliga SAI tiques antes do fim, para o
# fade acabar junto com a forma endiabrada: o var(20) conta 1 por tique até 0 (-2) e o 3100 acaba no AnimTime 0.
LIGADA = (f"var(20) > {SAI} || (StateNo = 3100 && AnimTime < -{SAI}) || (StateNo = 2000 && Time >= 83)")
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

    # as duas metades do anel: o mesmo movimento (sem respiração nem tremor, que andam com fase por camada)
    def anel(nome, quadros, prioridade):
        return aura.Camada(nome, quadros, plano="chao", eixo=pe, inicio=1, tique=0, prioridade=prioridade,
                           mov=aura.Movimento(deriva=(0, 0), alfa=0.92, respira=0), surto_alfa=0.08, surto_tremor=0)

    camadas = [
        anel("anel_tras", anel_tras, -7),
        aura.Camada("coluna", coluna, plano="tras", no_chao=True, eixo=pe, tique=1, prioridade=-6,
                    mov=aura.Movimento(deriva=(1.6, 1.4), deriva_periodo=170, alfa=0.9, respira=0.1)),
        anel("anel_frente", anel_frente, -5),
        aura.Camada("soltos", soltos, plano="tras", eixo=pe, tique=0, prioridade=-4,
                    mov=aura.Movimento(deriva=(2.4, 3.0), deriva_periodo=70, alfa=0.95, respira=0.06)),
    ]
    assert all(c.prioridade < PRIORIDADE_MIN_LUTADOR for c in camadas), "camada da aura na frente de um lutador"
    assert camadas[0].troca(0) == camadas[2].troca(2), "as metades do anel trocam de quadro em tiques diferentes"
    return aura.Aura("pengaro", camadas, ligada=LIGADA, surto=SURTO, base=9600, entra=44, sai=SAI,
                     altura_lutador=ALTURA_LUTADOR, virada_fundo=0.6)


def ligar(sprites):
    """Monta a aura, põe os quadros no .sff (fora da escolha da paleta) e devolve a Aura (para .air e .cns)."""
    a = montar()
    a.conferir(grupos={t[0] for t in sprites.lista})
    entrou = a.registrar(sprites)
    sprites.fora_da_paleta = getattr(sprites, "fora_da_paleta", set()) | entrou
    return a


if __name__ == "__main__":
    print(montar().resumo())
