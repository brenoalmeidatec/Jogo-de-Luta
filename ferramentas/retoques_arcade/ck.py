"""Retoques por código nas folhas arcade do CK, aplicados por ferramentas/converter_ck.py ANTES de quantizar (o quadro
chega aqui já na tela do jogo, 360x260, em RGBA). Rodar o converter de novo refaz todos; nada aqui é retoque à mão.

COPIA: quadro inteiro trocado pelo vizinho certo. LIMPA: o que sai do quadro (faísca de impacto desenhada junto com o
corpo, projétil que no jogo é sprite separado). Índices de quadro começam em 0 (o quadro 8 da folha é o 7).
"""
import colorsys

import cv2
import numpy as np
from PIL import Image

# (folha, quadro) -> quadro da mesma folha que entra no lugar
COPIA = {
    ("e_derrota", 7): 6,   # o 8 da folha é cópia do 7 cortada pela borda direita da imagem
    ("e_agarrao", 6): 7,   # no 7 a garrafa passa para a mão de trás (a da frente vai à testa); entra a guarda do 8
    ("e_soco", 4): 3,      # folha refeita: no 5 a garrafa fica na mão de trás, junto do quadril; entra o 4
}


# (folha, quadro) -> projétil desenhado no ar junto com o corpo. Sai do quadro NA FOLHA (antes de reduzir, enquanto
# ainda está separado da mão) e, se tiver nome, vira sprites/ck/efeitos/<nome>/00.png. Os riscos de movimento em volta
# dele saem junto. A garrafa inteira do e_bola não vira efeito: o projétil dela é a folha fx_garrafa.
SOLTO = {("bone_voador", 5): "bone", ("e_juliet_voadora", 5): "juliet", ("e_bola", 5): None}


def sem_fiapo(q):
    """Modo Ratão: tira o fiapo de fumaça do cigarro (e o próprio cigarro). Na escala do jogo ele tem 1-2 px de
    largura, fica todo na borda e o contorno de 1 px o pintaria de azul-escuro: vira um rabisco preto em cima da
    cabeça. Sai o que é claro e mais fino que 3 px; a fumaça, se o jogo quiser, entra como efeito."""
    a = np.array(q)
    opaco = (a[..., 3] > 0).astype(np.uint8)
    fino = (opaco > 0) & (cv2.morphologyEx(opaco, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) == 0)
    r, g, b = (a[..., i].astype(int) for i in range(3))
    maior, menor = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    claro = (maior > 140) & (maior - menor < 0.24 * maior)
    a[fino & claro] = 0
    # o que sobra do fiapo fica solto em cima da cabeça: sai todo pedaço pequeno que não é o corpo
    n, rot, info, _ = cv2.connectedComponentsWithStats((a[..., 3] > 0).astype(np.uint8), connectivity=8)
    for i in range(1, n):
        if info[i, cv2.CC_STAT_AREA] < 25:
            a[rot == i] = 0
    return Image.fromarray(a)


def sem_faisca(q):
    """Tira a estrela amarela de impacto (amarelo vivo e o miolo creme colado nele): no jogo a faísca é do motor."""
    a = np.array(q)
    r, g, b = (a[..., i].astype(float) / 255 for i in range(3))
    h, s, v = np.vectorize(colorsys.rgb_to_hsv)(r, g, b)
    opaco = a[..., 3] > 0
    amarelo = opaco & (h * 360 >= 46) & (h * 360 <= 68) & (s > .35) & (v > .85)
    perto = cv2.dilate(amarelo.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    claro = opaco & (v > .9) & (s < .35) & (h * 360 > 30) & (h * 360 < 75)  # miolo creme da estrela, não o branco lilás
    a[amarelo | (perto & claro)] = 0
    # farelo que sobra da estrela
    n, rot, info, _ = cv2.connectedComponentsWithStats((a[..., 3] > 0).astype(np.uint8), connectivity=8)
    for i in range(1, n):
        if info[i, cv2.CC_STAT_AREA] < 6:
            a[rot == i] = 0
    return Image.fromarray(a)


# (folha, quadro) -> lista de limpezas no quadro já na escala do jogo
LIMPA = {
    ("e_queda", 0): ["faisca"], ("e_queda", 4): ["faisca"], ("e_queda", 5): ["faisca"],
}


def retocar(folha, i, q, ratao):
    """ratao: folhas e_* (o despertar_b fica com a fumaça e os cacos da garrafa)."""
    for passo in LIMPA.get((folha, i), ()):
        if passo == "faisca":
            q = sem_faisca(q)
    return sem_fiapo(q) if ratao else q
