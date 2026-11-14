"""Retoques por código nas folhas arcade do Gbzin, aplicados por ferramentas/converter_gbzin.py ANTES de quantizar (o
quadro chega já na tela do jogo, 360x260, RGBA). Mesmo contrato de retoques_arcade/ck.py: COPIA troca um quadro inteiro
pelo vizinho, SOLTO tira projétil desenhado junto com o corpo, retocar() mexe no quadro. Quadros contam de 0.

Os defeitos abaixo foram anotados nas folhas do primeiro conceito (reprovado pelo Breno em 2026-11-14, issue #30). Ao
refazer as folhas com o conceito novo, confira de novo cada um: quadro bom não precisa de cópia.
"""
E = 1  # escala da tela (HD=3 põe 3)

# (folha, quadro) -> quadro da mesma folha que entra no lugar
COPIA = {
    ("afastar", 3): 4,  # o 4 da folha saiu com cabeça dupla
}

# (folha, quadro) -> nome do efeito (ou None) do projétil desenhado no ar junto com o corpo
SOLTO = {}


def retocar(folha, i, q, motoboy):
    """motoboy: folhas e_* do Deus Motoboy. Por ora nenhum retoque além de COPIA."""
    return q
