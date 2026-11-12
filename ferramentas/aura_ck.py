"""Aura do CK no Modo Ratão (boss final, "dono do paredão") no jogo: as camadas do Blender ligadas pelo ferramentas/aura.py.

Camadas prontas em sprites/ck/aura/ (ferramentas/aura_blender/ck_aura.py, ver docs/arcade/aura_blender.md):
paredao 48, aneis 96, nevoa 96, cacos 48, fagulhas 96, todas atrás, 360x200 com o pé do lutador em (180, 190),
2 tiques por quadro (compasso de 4 tempos em 48 quadros).

No jogo viram 3 camadas (Explods 9600 a 9602, [Statedef -4]), todas ATRÁS de qualquer lutador (o mais baixo de um
lutador é o -3 do caído morto, estado 5150 do common1) e todas no chão no pulo (no_chao: o paredão é um muro de
caixas, não sobe com o CK; a base reta dele no ar virava um prato solto, como a coluna do Pengaró):
  9600 paredao   paredão + anéis num desenho só: os anéis saem dos cones, e com deriva e início próprios descolariam
                 deles. Some (em ~8 tiques) enquanto o paredão de cena do gerador (Explod 9250: cena do Despertar,
                 Baile 3100, Grave 3403) está na tela, e volta depois: dois paredões não se dobram (sprpriority -7)
  9601 chao      névoa rasteira + cacos e tampinhas, na frente da base do paredão (sprpriority -6)
  9602 fagulhas  folhinhas de brasa subindo, deriva própria e curta (sprpriority -5)
Troca de quadro: o paredão no tique ímpar, chão e fagulhas no par. O paredão e as fagulhas dividem o alto da tela;
trocando em tiques diferentes, todo tique tem desenho novo lá em cima (o Pengaró falhou nisso com uma camada só).
Entrada em 44 tiques (como o Pengaró): o paredão é largo e denso, em 26 ele brotava de uma vez.
Virada a 60% (virada_fundo): com 30% o boss sumia a cada troca de lado (filme do Pengaró, 2026-11-12).
Desliga ANTES de o corpo voltar: o fade de saída (34 tiques) acaba no tique em que o var(20) chega a 0, quando o
"Endiabrado desligado" do -2 volta o corpo à forma base. No Baile (3100) o Ratão continua (gerar_ck.py tira o "Fim
Despertar" dele); se o var(20) acabar dentro do Baile, o corpo só volta quando ele acaba: a aura segue até o fim
pelo AnimTime.

As cores das camadas NÃO entram na escolha da paleta do .sff (Sprites.fora_da_paleta): a paleta da forma base sai
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
SURGE = 69                   # tique da cena do Despertar (estado 2000) em que o Ratão sai da fumaça (ação 2000 do .air)

# Liga quando o Ratão sai da fumaça na cena da transformação e segue no Despertar (var 20); desliga SAI tiques antes
# do fim, para o fade acabar junto com a forma. No Baile com o var(20) já no fim, o Ratão segue até o AnimTime 0.
LIGADA = (f"var(20) > {SAI} || (StateNo = 3100 && var(37) = 1 && AnimTime < -{SAI}) "
          f"|| (StateNo = 2000 && Time >= {SURGE})")
# Surto: os supers, o Grave do Paredão e o instante em que ele quebra a garrafa no chão na cena (despertar_b quadro 5, tique 90).
SURTO = "((StateNo = 3000 || StateNo = 3100 || StateNo = 3200 || StateNo = 3403) && Time = 1) || (StateNo = 2000 && Time = 90)"
# o paredão de cena (ação 9250, id 9250) do gerador: enquanto ele toca, o paredão da aura sai da frente
PAREDAO_DE_CENA = "NumExplod(9250) > 0"


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
    assert info["lutador"] == "ck" and info["tela"] == [360, 200] and info["tiques_por_quadro"] == 2, info
    assert all(c["plano"] == "atras" for c in info["camadas"]), "camada do CK fora de 'atras': rever a montagem"
    pe = tuple(info["pe"])
    paredao = _sobre(_ler(info, "paredao"), _ler(info, "aneis"))
    chao = _sobre(_ler(info, "nevoa"), _ler(info, "cacos"))
    fagulhas = _ler(info, "fagulhas")

    camadas = [
        aura.Camada("paredao", paredao, plano="tras", no_chao=True, eixo=pe, tique=1, prioridade=-7,
                    esconde=PAREDAO_DE_CENA,
                    mov=aura.Movimento(deriva=(1.2, 0.8), deriva_periodo=170, alfa=0.92, respira=0.08)),
        aura.Camada("chao", chao, plano="tras", no_chao=True, eixo=pe, tique=0, prioridade=-6,
                    mov=aura.Movimento(deriva=(1.0, 0), deriva_periodo=130, alfa=0.9, respira=0.06),
                    surto_tremor=0.8),
        aura.Camada("fagulhas", fagulhas, plano="tras", no_chao=True, eixo=pe, tique=0, prioridade=-5,
                    mov=aura.Movimento(deriva=(2.4, 3.0), deriva_periodo=70, alfa=0.95, respira=0.06)),
    ]
    assert all(c.prioridade < PRIORIDADE_MIN_LUTADOR for c in camadas), "camada da aura na frente de um lutador"
    assert camadas[0].troca(0) != camadas[2].troca(2), "paredão e fagulhas trocam de quadro no mesmo tique"
    return aura.Aura("ck", camadas, ligada=LIGADA, surto=SURTO, base=9600, entra=44, sai=SAI, virada_fundo=0.6)


def ligar(sprites):
    """Monta a aura, põe os quadros no .sff (fora da escolha da paleta) e devolve a Aura (para .air e .cns)."""
    a = montar()
    a.conferir(grupos={t[0] for t in sprites.lista})
    entrou = a.registrar(sprites)
    sprites.fora_da_paleta = getattr(sprites, "fora_da_paleta", set()) | entrou
    return a


if __name__ == "__main__":
    print(montar().resumo())
