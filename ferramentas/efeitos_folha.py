#!/usr/bin/env python3
"""Recorta as folhas de efeito do ChatGPT (8 quadros, fundo verde #00FF00) e cria os quadros do meio por fluxo óptico.

  python ferramentas/efeitos_folha.py pengaro            # todas as folhas fx_*.png
  python ferramentas/efeitos_folha.py pengaro fx_poeira  # só algumas

Entrada: sprites/<lutador>/quadros/folhas/fx_<nome>.png. Saída: sprites/<lutador>/efeitos/<nome>/NN.png, já na escala do
jogo, todos os quadros na mesma tela (o pivô é o centro da tela; nos efeitos de chão, o meio da borda de baixo).
O fundo é verde porque o roxo da sombra se confunde com o magenta das folhas dos lutadores.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
MEIO = 2  # quadros do meio por intervalo: 8 desenhos viram 22 (ou 24 nos loops)
# nome -> (largura no jogo em px do lutador, loop, efeito de chão)
EFEITOS = {
    "whisky_acerto": (60, False, False), "whisky_forte": (80, False, False), "whisky_rastro": (80, False, False),
    "poeira": (100, False, True), "defesa": (50, False, False),
    "sombra_aura": (85, True, True), "sombra_acerto": (60, False, False), "sombra_forte": (80, False, False),
    "sombra_rastro": (80, False, False), "sombra_chao": (100, True, True),
}


def recortar(caminho):
    a = np.array(Image.open(caminho).convert("RGB")).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    verde = (g > 140) & (g > r + 50) & (g > b + 50)
    alfa = np.where(verde, 0, 255).astype(np.uint8)
    alfa = cv2.morphologyEx(alfa, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    g2 = np.minimum(g, np.maximum(r, b) + 20)  # tira o verde que vaza na borda
    rgba = np.dstack([r, g2, b, alfa]).astype(np.uint8)
    largura = rgba.shape[1] / 8
    celulas = [rgba[:, round(i * largura) + 3:round((i + 1) * largura) - 3] for i in range(8)]
    menor = min(c.shape[1] for c in celulas)
    celulas = [c[:, :menor] for c in celulas]
    # sujeira solta: some com pedaços muito pequenos
    for c in celulas:
        n, rot, info, _ = cv2.connectedComponentsWithStats((c[..., 3] > 0).astype(np.uint8), 8)
        for k in range(1, n):
            if info[k, 4] < 6:
                c[rot == k, 3] = 0
    return celulas


def enquadrar(celulas, largura_jogo, chao):
    juntos = np.max([c[..., 3] for c in celulas], axis=0)
    ys, xs = np.nonzero(juntos)
    cx = celulas[0].shape[1] // 2
    meia = max(cx - xs.min(), xs.max() - cx) + 2
    if chao:
        y0, y1 = ys.min() - 2, ys.max() + 1
    else:
        cy = celulas[0].shape[0] // 2
        meia_y = max(cy - ys.min(), ys.max() - cy) + 2
        y0, y1 = cy - meia_y, cy + meia_y
    caixa = (cx - meia, max(0, y0), cx + meia, min(juntos.shape[0], y1))
    fator = largura_jogo / (2 * meia)
    saida = []
    for c in celulas:
        img = Image.fromarray(c).crop(caixa)
        img = img.resize((max(1, round(img.width * fator)), max(1, round(img.height * fator))), Image.LANCZOS)
        q = np.array(img)
        q[..., 3] = np.where(q[..., 3] >= 128, 255, 0)
        saida.append(q)
    return saida


def entre(a, b, t):
    """Quadro do meio entre a e b no instante t, deformando os dois pelo fluxo óptico."""
    def cinza(q):
        return cv2.cvtColor(np.ascontiguousarray(q[..., :3]), cv2.COLOR_RGB2GRAY) // 2 + q[..., 3] // 2
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    fab = dis.calc(cinza(a), cinza(b), None)
    fba = dis.calc(cinza(b), cinza(a), None)
    h, w = a.shape[:2]
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))

    def deforma(q, f, s):
        pre = q.astype(np.float32)
        pre[..., :3] *= pre[..., 3:] / 255
        return cv2.remap(pre, gx + s * f[..., 0], gy + s * f[..., 1], cv2.INTER_LINEAR, borderValue=0)
    m = (1 - t) * deforma(a, fba, t) + t * deforma(b, fab, 1 - t)
    alfa = m[..., 3]
    rgb = np.where(alfa[..., None] > 1, m[..., :3] * 255 / np.maximum(alfa[..., None], 1), 0)
    return np.dstack([np.clip(rgb, 0, 255), np.where(alfa >= 128, 255, 0)]).astype(np.uint8)


def main():
    lutador = sys.argv[1]
    pedidos = sys.argv[2:] or [f.stem for f in (RAIZ / "sprites" / lutador / "quadros/folhas").glob("fx_*.png")]
    for pedido in pedidos:
        nome = pedido.removeprefix("fx_")
        largura, loop, chao = EFEITOS[nome]
        quadros = enquadrar(recortar(RAIZ / "sprites" / lutador / "quadros/folhas" / f"fx_{nome}.png"), largura, chao)
        pares = list(zip(quadros, quadros[1:] + ([quadros[0]] if loop else [])))
        todos = []
        for a, b in pares:
            todos.append(a)
            todos += [entre(a, b, k / (MEIO + 1)) for k in range(1, MEIO + 1)]
        if not loop:
            todos.append(quadros[-1])
        pasta = RAIZ / "sprites" / lutador / "efeitos" / nome
        pasta.mkdir(parents=True, exist_ok=True)
        for f in pasta.glob("*.png"):
            f.unlink()
        for i, q in enumerate(todos):
            Image.fromarray(q).save(pasta / f"{i:02d}.png")
        print(f"{nome}: {len(todos)} quadros {todos[0].shape[1]}x{todos[0].shape[0]}")


if __name__ == "__main__":
    main()
