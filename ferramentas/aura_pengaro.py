"""Aura do Pengaró endiabrado no jogo: a camada discreta do Blender ligada pelo ferramentas/aura.py.

Segue a regra dos efeitos proporcionais (docs/regra-efeitos-proporcionais.md, Breno, 2026-11-12): UMA camada leve,
baixa e translúcida, atrás do corpo, com o corpo sempre legível por cima. O boss se vê pela arte nova, não pela aura.

A camada está pronta em sprites/pengaro/aura/ (ferramentas/aura_blender/discreta.py): fumaça violeta-preta das
sombras saindo de um chão rachado pequeno, do chão até o peito, 192 quadros em 3x (1080x600, pé em (540, 570)),
1 tique por quadro (desenho novo todo tique: com uma camada só, trocar a cada 2 deixava o tique do meio parado). É a coluna e o chão do rig.blend da aura grande (pengaro_aura.py) encolhidos em volta do pé.

No jogo: um Explod (9600, [Statedef -4]) com scale 1/3 (o Explod não usa a escala do lutador), alfa 0,5, atrás de
qualquer lutador (sprpriority -6; o mais baixo de um lutador é o -3 do caído morto, estado 5150 do common1) e no
chão no pulo e na queda (no_chao: a fumaça sai do chão rachado, não sobe com ele).
Virada: a aura apaga só até 60% do alfa (virada_fundo) antes de trocar de lado.
Desliga ANTES de o corpo voltar: o fade de saída (34 tiques) acaba no tique em que o var(20) chega a 0 (o corpo volta
à forma base nesse tique, pelo RemapSprite do -2). O mesmo no fim do super 3100 (que zera o var(20) no começo):
pelo AnimTime.

As cores da camada NÃO entram na escolha da paleta do .sff (Sprites.fora_da_paleta): a paleta da forma base sai
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


def montar():
    info = json.loads((PASTA / "aura.json").read_text(encoding="utf-8"))
    assert info["formato"] == 2 and info["escala"] == 3 and info["tiques_por_quadro"] == 1, info
    assert [c["nome"] for c in info["camadas"]] == ["discreta"] and info["camadas"][0]["plano"] == "atras", info
    n = info["camadas"][0]["quadros"]
    quadros = [np.asarray(Image.open(PASTA / info["arquivo"].format(nome="discreta", quadro=q)).convert("RGBA"))
               for q in range(n)]
    camada = aura.Camada("discreta", quadros, tempo=info["tiques_por_quadro"], plano="tras", no_chao=True,
                         eixo=tuple(info["pe"]), res=info["escala"],
                         prioridade=-6, surto_alfa=0.1, surto_tremor=1.0,
                         mov=aura.Movimento(deriva=(1.0, 0.6), deriva_periodo=170, alfa=0.5, respira=0.08))
    assert camada.prioridade < PRIORIDADE_MIN_LUTADOR, "camada da aura na frente de um lutador"
    a = aura.Aura("pengaro", [camada], ligada=LIGADA, surto=SURTO, base=9600, sai=SAI,
                  altura_lutador=ALTURA_LUTADOR, virada_fundo=0.6)
    a.conferir_discreta()
    return a


def ligar(sprites):
    """Monta a aura, põe os quadros no .sff (fora da escolha da paleta) e devolve a Aura (para .air e .cns)."""
    a = montar()
    a.conferir(grupos={t[0] for t in sprites.lista})
    entrou = a.registrar(sprites)
    sprites.fora_da_paleta = getattr(sprites, "fora_da_paleta", set()) | entrou
    return a


if __name__ == "__main__":
    print(montar().resumo())
