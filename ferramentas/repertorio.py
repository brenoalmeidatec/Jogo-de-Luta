"""Golpes adicionais, compartilhando os formatos de animação e estado."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Golpe:
    estado: int
    nome: str
    comando: str
    poses: tuple
    tempo: tuple
    caixa: tuple
    dano: int
    tipo: str = "S"
    guarda: str = "MA"
    avanco: float = 0
    queda: bool = False
    custo: int = 0
    nome_desperto: str = ""
    lancamento: str = "-2,-3"


NORMAIS = (
    Golpe(216, "Tranco de Ombro", "/F, y", ("defesa", "soco2", "soco3"), (8, 3, 14), (12,-88,64,-49), 76, avanco=2),
    Golpe(246, "Passo de Letra", "/F, b", ("chute0", "kick_alto", "chute3"), (17, 4, 20), (9,-114,67,-34), 90, guarda="HA"),
    Golpe(201, "Mão de Ginga", "/B, x", ("recua", "soco1", "defesa"), (6, 3, 12), (8,-95,56,-60), 47, avanco=-1.5),
    Golpe(231, "Puxada de Sola", "/B, a", ("recua", "chute1", "chute3"), (8, 3, 14), (10,-78,62,-44), 57, avanco=-1.5),
    Golpe(601, "Cotovelo de Saída", "y", ("pulo_topo", "ar_cotovelo", "pulo_desce"), (7, 5, -1), (12,-76,62,-40), 79, "A", "HA"),
    Golpe(611, "Calcanhar de Volta", "b", ("pulo_topo", "bicicleta", "pulo_desce"), (9, 6, -1), (10,-79,68,-27), 88, "A", "HA"),
)

FAMILIAS_PENGARO = (
    (1400, "Mão de Chimpá", "Mão Pesada", "~D, F", "xy", ("defesa","soco2","recua"), (9,-98,73,-48), 73, 2.5, "MA", False),
    (1500, "Sola de Várzea", "Pisão de Bar", "~B, D", "ab", ("kick_alto","pisa","agacha0"), (8,-37,64,-2), 88, 1.2, "L", True),
)

FAMILIAS_HAZAKI = (
    (1000, "Punho de Concreto", "Punho de Brasa", "~D, F", "xy", ("defesa","especial","soco3"), (14,-96,78,-52), 82, 2.6, "MA", False),
    (1100, "Guarda de Aço", "Revide do Inferno", "~D, B", "xy", ("defesa","ar_cotovelo","recua"), (7,-99,52,-48), 95, 0, "MA", False),
    (1200, "Ascensão de Faixa", "Coroa de Cinzas", "~F, D", "xy", ("baixo_cima0","baixo_cima1","defesa"), (5,-130,54,-58), 100, 1.2, "MA", True),
    (1300, "Giro de Garagem", "Queima de Pneu", "~D, F", "ab", ("chute0","chute2","chute3"), (13,-89,86,-48), 90, 4.1, "MA", False),
    (1400, "Corte de Base", "Rasteira de Fornalha", "~D, B", "ab", ("rasteira0","rasteira2","rasteira3"), (10,-33,76,-2), 78, 2.8, "L", True),
    (1500, "Salto de Dojô", "Queda do Capeta", "~B, D", "ab", ("pulo_sobe","bicicleta","pouso"), (7,-88,71,-28), 91, 3.1, "HA", False),
)


def golpes(hazaki=False):
    nomes = ("Cotovelo de Faixa", "Machado de Dojô", "Mão de Checagem", "Bico de Recuo",
             "Martelo no Voo", "Chute de Queda")
    if hazaki:
        from dataclasses import replace
        yield from (replace(g, nome=nome) for g, nome in zip(NORMAIS, nomes))
    else:
        yield from NORMAIS
    for n, nome, desperto, direcao, botoes, poses, caixa, dano, avanco, guarda, queda in (
            FAMILIAS_HAZAKI if hazaki else FAMILIAS_PENGARO):
        for i, botao in enumerate(botoes):
            yield Golpe(n+i, nome, f"{direcao}, {botao}", poses, (8+i*3, 4+i*2, 16+i*7),
                        caixa, dano+i*22, guarda=guarda, avanco=avanco*(1+i*.35),
                        queda=queda and (i == 1 or n == 1200), nome_desperto=desperto,
                        lancamento="-2,-7" if hazaki and n == 1200 else "-3,-3.5")
    if hazaki:
        yield Golpe(3000, "Faixa no Asfalto", "~B, F, D, a", ("chute0","chute2","soco2","rasteira2","defesa"),
                    (9, 5, 5, 5, 23), (9,-93,82,-16), 245, avanco=4, queda=True, custo=1000)
    yield Golpe(3200, "Pose Final" if hazaki else "Bando da Várzea", "~B, F, D, x",
                ("defesa","soco2","chute2","kick_alto","recua"), (11, 5, 5, 6, 26),
                (6,-109,87,-26), 345, avanco=4, queda=True, custo=2000,
                nome_desperto="Academia do Inferno" if hazaki else "Apagão da Várzea")


def quadros(golpe):
    return [(pose, tempo, golpe.caixa) if i in range(1, len(golpe.poses)-1) else (pose, tempo)
            for i, (pose, tempo) in enumerate(zip(golpe.poses, golpe.tempo))]
