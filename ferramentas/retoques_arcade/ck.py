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


# Rasteira da base, desenhos 1 a 5: o pé de apoio (o de trás, plantado) veio com o tênis na cor da luva (vermelho);
# a canela e a meia branca mostram que é pé, não mão no chão. O tênis do CK é o da outra perna: contorno roxo-escuro,
# lilás e branco. No levanta (kip-up) o vermelho no chão são as luvas, de mãos no chão: fica como está.
TENIS_VERMELHO = {("rasteira", i) for i in range(1, 6)}
TENIS = ((56, 23, 82), (150, 132, 209), (174, 156, 177), (212, 184, 227))  # do escuro ao claro, o tênis da frente


def tenis_da_cor_certa(q):
    """Repinta de tênis a mancha vermelha que toca o chão (as 14 linhas de baixo da figura): o vermelho vivo e o vinho e
    o vermelho-escuro ligados a ele, até 2 px do vivo (a pele da canela, laranja, não entra). Funciona antes de
    quantizar (converter_ck) e depois (quadro já na paleta): a cor sai pela luminância, sempre uma das de TENIS."""
    a = np.array(q.convert("RGBA"))
    op = a[..., 3] >= 128
    linhas = np.flatnonzero(op.any(axis=1))
    if not len(linhas):
        return q
    faixa = np.zeros_like(op)
    faixa[max(0, linhas[-1] - 13):linhas[-1] + 1] = True
    r, g, b = (a[..., k].astype(int) for k in range(3))
    vivo = op & faixa & (r >= 200) & (g < 90) & (b < 90)
    if not vivo.any():
        return q
    perto = cv2.dilate(vivo.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    vermelho = op & faixa & perto & (r >= 60) & (g < 0.45 * r) & (b < 0.6 * r)
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    cor = np.select([lum < 50, lum < 95, vivo], [0, 1, 3], 2)
    tinta = np.array(TENIS, np.uint8)[cor]
    a[vermelho, :3] = tinta[vermelho]
    # brilho laranja no tênis (3 ou mais dos 8 vizinhos repintados): vira o lilás claro; a canela, acima da meia branca,
    # não encosta no tênis repintado
    vizinhos = cv2.filter2D(vermelho.astype(np.float32), -1, np.ones((3, 3), np.float32), borderType=cv2.BORDER_CONSTANT)
    dentro = op & faixa & ~vermelho & (vizinhos >= 3) & (r > g) & (g > b)
    a[dentro, :3] = TENIS[3]
    return Image.fromarray(a)


def retocar(folha, i, q, ratao):
    """ratao: folhas e_* (o despertar_b fica com a fumaça e os cacos da garrafa)."""
    if (folha, i) in TENIS_VERMELHO:
        q = tenis_da_cor_certa(q)
    for passo in LIMPA.get((folha, i), ()):
        if passo == "faisca":
            q = sem_faisca(q)
    return sem_fiapo(q) if ratao else q


if __name__ == "__main__":
    # aplica o retoque do tênis direto nos quadros já convertidos (sem rodar o converter_ck inteiro, ~15 min); rodar
    # de novo não muda nada (não sobra vermelho vivo no tênis)
    from pathlib import Path
    pasta = Path(__file__).resolve().parents[2] / "sprites/ck/quadros_arcade"
    for folha, i in sorted(TENIS_VERMELHO):
        arquivo = pasta / folha / f"{i:02d}.png"
        antes = Image.open(arquivo).convert("RGBA")
        depois = tenis_da_cor_certa(antes)
        muda = int((np.asarray(antes) != np.asarray(depois)).any(axis=2).sum())
        if muda:
            depois.save(arquivo)
        print(f"{folha} {i}: {muda} px repintados")
