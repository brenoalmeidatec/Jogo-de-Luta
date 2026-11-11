"""Hazak, retoque de pixel da pulseira verde-água (só no pulso de trás). Chamado por ferramentas/folhas_hazak_arcade.py
no fim da conversão de cada folha; pode rodar de novo à vontade (parte sempre do desenho recém-convertido).

Três regras:
 1. Uma pulseira só por desenho: fica a maior mancha verde-água; as outras (a duplicada no pulso da frente e os
    pixels soltos que a sombra azulada da atadura vira na quantização) viram sombra de atadura.
 2. PINTA: desenhos em que a pulseira faltou. Escolhe a atadura do pulso de trás (a mancha branca mais à esquerda, à
    direita, em cima ou embaixo) e pinta de verde-água a metade dela do lado do cotovelo.
 3. APAGA: desenhos em que a maior mancha é a do pulso errado e a regra 1 não resolve (hoje nenhum).
"""
import cv2
import numpy as np
from PIL import Image

VERDE = (0x2a, 0x9d, 0x9a)
BRANCO = (0xf4, 0xf1, 0xea)
SOMBRA = (0xa9, 0xa6, 0xcc)
DIRECAO = {"N": (0, -1), "S": (0, 1), "L": (1, 0), "O": (-1, 0),
           "NE": (1, -1), "NO": (-1, -1), "SE": (1, 1), "SO": (-1, 1)}

# (folha, desenho): (qual atadura, lado do cotovelo). qual: esq, dir, cima, baixo (pelo centro da mancha branca).
PINTA = {
    ("parado", 1): ("esq", "SO"), ("parado", 4): ("esq", "SO"),
    ("agarrao_perna", 0): ("esq", "SO"), ("agarrao_perna", 7): ("esq", "SO"),
    ("apanha", 2): ("esq", "O"), ("apanha", 7): ("baixo", "O"),
    ("chute_giratorio", 2): ("dir", "S"),
    ("corrida", 3): ("esq", "L"), ("corrida", 5): ("esq", "L"),
    ("derrota_sirene", 0): ("cima", "O"), ("derrota_sirene", 5): ("dir", "NE"),
    ("guarda_aco", 2): ("esq", "S"),
    ("rasteira", 1): ("baixo", "N"), ("rasteira_arco", 2): ("esq", "N"),
    ("vitima_agarrado", 1): ("dir", "O"),
    ("vitima_arremessado", 2): ("baixo", "O"), ("vitima_arremessado", 6): ("dir", "N"),
    ("vitoria", 1): ("esq", "NO"), ("vitoria", 2): ("esq", "NO"),
    ("defesa_baixa", 2): ("baixo", "NO"),
}
MINIMO = 8  # menos verde que isso num desenho conta como pulseira faltando (aviso)


def manchas(mascara, junta=1):
    """Manchas de uma máscara (as que ficam a até `junta` px uma da outra contam como uma), da maior para a menor."""
    m = mascara.astype(np.uint8)
    grossa = cv2.dilate(m, np.ones((2 * junta + 1, 2 * junta + 1), np.uint8)) if junta else m
    n, rot, _, _ = cv2.connectedComponentsWithStats(grossa, connectivity=8)
    saida = [mascara & (rot == i) for i in range(1, n)]
    return sorted((s for s in saida if s.any()), key=lambda s: -s.sum())


def cor(a, rgb):
    return (a[..., :3] == rgb).all(-1) & (a[..., 3] > 0)


def retocar(nome, i, img):
    """Devolve (imagem retocada, quantos pixels verdes ficaram)."""
    a = np.array(img.convert("RGBA"))
    verdes = manchas(cor(a, VERDE), junta=2)
    for sobra in verdes[1:]:
        a[sobra, :3] = SOMBRA
    if (nome, i) in PINTA:
        qual, lado = PINTA[(nome, i)]
        if verdes:
            a[verdes[0], :3] = SOMBRA  # o resto de verde que havia (poucos pixels) sai; a pulseira é a pintada
        brancas = [b for b in manchas(cor(a, BRANCO) | cor(a, SOMBRA), junta=1) if b.sum() >= 6]
        if brancas:
            centro = [np.argwhere(b).mean(0) for b in brancas]  # (y, x)
            chave = {"esq": lambda c: c[1], "dir": lambda c: -c[1], "cima": lambda c: c[0], "baixo": lambda c: -c[0]}
            alvo = brancas[min(range(len(brancas)), key=lambda k: chave[qual](centro[k]))]
            ys, xs = np.nonzero(alvo)
            dx, dy = DIRECAO[lado]
            proj = xs * dx + ys * dy
            corte = np.percentile(proj, 55)
            pega = proj >= corte
            a[ys[pega], xs[pega], :3] = VERDE
    return Image.fromarray(a), int(cor(a, VERDE).sum())


def aplicar(nome, pasta):
    """Retoca os 8 desenhos da pasta. Devolve a lista dos desenhos que ficaram sem pulseira (menos de MINIMO px)."""
    if nome.startswith(("obj_", "patroa_")):
        return []
    faltam = []
    for i, f in enumerate(sorted(pasta.glob("[0-9][0-9].png"))):
        img, n = retocar(nome, i, Image.open(f))
        img.save(f)
        if n < MINIMO:
            faltam.append((i, n))
    return faltam
