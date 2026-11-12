"""Aura do CK no Modo Ratão ("dono do paredão") no jogo: a camada discreta do Blender ligada pelo ferramentas/aura.py.

Segue a regra dos efeitos proporcionais (docs/regra-efeitos-proporcionais.md, Breno, 2026-11-12): UMA camada leve,
baixa e translúcida, atrás do corpo, com o corpo sempre legível por cima. O boss se vê pela arte nova, não pela aura.

A camada está pronta em sprites/ck/aura/ (ferramentas/aura_blender/discreta.py): o paredão de som de fumaça
cinza-esverdeada em miniatura, atrás das pernas (do chão até a cintura), com os cones batendo no compasso de 4 tempos,
48 quadros em 3x (1080x600, pé em (540, 570)), 2 tiques por quadro. É o paredão do rig.blend da aura grande
(ck_aura.py) encolhido em volta do pé. Sem anéis, névoa, cacos nem fagulhas.

No jogo: um Explod (9600, [Statedef -4]) com scale 1/3 (o Explod não usa a escala do lutador), alfa 0,5, atrás de
qualquer lutador (sprpriority -6; o mais baixo de um lutador é o -3 do caído morto, estado 5150 do common1) e no
chão no pulo (no_chao: é um muro de caixas, não sobe com o CK). Entra e sai só pelo alfa (cresce=False: achatado a
8% o muro virava elipse).
Na cena (2000) ela começa quando a fumaça cobre tudo (tique 42) e a caixa preta da cena apaga no mesmo trecho
(gerar_ck.py); o Ratão sai da fumaça no tique 69 com o paredãozinho já tocando.
Virada a 60% (virada_fundo): com 30% o boss sumia a cada troca de lado (filme do Pengaró, 2026-11-12).
Saída presa ao contador (resta): o fade nunca passa de resta/34, então acaba no tique em que o var(20) chega a 0 e
o corpo volta, mesmo com pausa, superpausa ou hitpause no fim (o -4 anda nelas, o var(20) do -2 não). No Baile
(3100) o Ratão continua até o fim da animação: resta é o maior entre o var(20) e o AnimTime; Baile interrompido com
o var(20) já zerado corta a aura no mesmo tique em que o corpo volta.

As cores da camada NÃO entram na escolha da paleta do .sff (Sprites.fora_da_paleta): a paleta da forma base sai
idêntica e a aura é levada para a cor mais perto dela.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

import aura

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "sprites/ck/aura"
SAI = 34                     # tiques do fade de saída (o padrão do aura.py)
PRIORIDADE_MIN_LUTADOR = -3  # common1.cns.zss, estado 5150 (caído morto); nenhum lutador de chars/ desce disso
FUMACA = 42                  # tique da cena do Despertar (estado 2000) em que a fumaça cobre tudo (ação 2000: 6 x 7)
RATAO = 69                   # tique em que o Ratão sai da fumaça (fim dos 4 desenhos de fumaça: 7 + 6 + 7 + 7)
GRAVE = 10                   # tique do grave no Grave do Paredão (3403): o EnvShake e o golpe (conferido no gerar_ck.py)

# Ticks que faltam para o corpo voltar à forma base: na cena, a partir da fumaça, "muito" (o var(20) só liga no fim
# dela); no Baile, o maior entre o var(20) e o resto da animação (o Ratão segue até o fim do Baile); fora, o var(20).
RESTA = (f"ifelse(StateNo = 2000, ifelse(Time >= {FUMACA}, 999, 0), "
         f"ifelse(StateNo = 3100 && var(37) = 1, max(var(20), -AnimTime), var(20)))")
LIGADA = f"({RESTA}) > 0"
# Surto: os supers, o grave do Grave do Paredão e o instante em que ele quebra a garrafa na cena (despertar_b quadro 5, tique 90).
SURTO = (f"((StateNo = 3000 || StateNo = 3100 || StateNo = 3200) && Time = 1) || (StateNo = 3403 && Time = {GRAVE}) "
         f"|| (StateNo = 2000 && Time = 90)")


def montar():
    info = json.loads((PASTA / "aura.json").read_text(encoding="utf-8"))
    assert info["lutador"] == "ck" and info["formato"] == 2 and info["escala"] == 3, info
    assert info["tiques_por_quadro"] == 2 and [c["nome"] for c in info["camadas"]] == ["discreta"], info
    assert info["camadas"][0]["plano"] == "atras", info
    n = info["camadas"][0]["quadros"]
    quadros = [np.asarray(Image.open(PASTA / info["arquivo"].format(nome="discreta", quadro=q)).convert("RGBA"))
               for q in range(n)]
    camada = aura.Camada("discreta", quadros, plano="tras", no_chao=True, eixo=tuple(info["pe"]), res=info["escala"],
                         prioridade=-6, cresce=False, surto_alfa=0.1, surto_tremor=0.8,
                         mov=aura.Movimento(deriva=(1.0, 0), deriva_periodo=130, alfa=0.5, respira=0.08))
    assert camada.prioridade < PRIORIDADE_MIN_LUTADOR, "camada da aura na frente de um lutador"
    a = aura.Aura("ck", [camada], ligada=LIGADA, surto=SURTO, base=9600, entra=44, sai=SAI, virada_fundo=0.6,
                  resta=RESTA)
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
