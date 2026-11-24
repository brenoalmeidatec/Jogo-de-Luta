#!/usr/bin/env python3
"""Soco rápido "escondido pela velocidade" (ideia do Breno na #32, 24/11): em vez do desenho do braço indo e voltando,
um quadro de borrão (smear) ou só o vento do golpe, como se o soco fosse rápido demais para ver.

Funções de imagem (tela 3x 1080x780, RGBA, pés em 540,660), usadas pelo teste do jab do Hazak e pela rajada do
agarrão karatê:

  borrao(estendido, guarda, ombro_x, faixa_y)  o braço estendido vira riscos de velocidade, com o punho nítido na ponta
                                               e dois punhos-fantasma no caminho
  vento(img, x0, x1, y, alt)                    arco de vento (linhas brancas e azul-claras, de pixel) na frente do punho

  python3 ferramentas/borrao.py teste SAIDA     vídeo do teste do jab (antes | borrão | só vento) em SAIDA
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
BRANCO = np.array([248, 248, 240, 255], np.uint8)
CLARO = np.array([170, 214, 240, 255], np.uint8)
MEIO = np.array([110, 160, 210, 255], np.uint8)


def braco(img, ombro_x, faixa_y):
    """Máscara do braço estendido: o que passa da linha do ombro dentro da faixa de altura do braço."""
    y0, y1 = faixa_y
    m = np.zeros(img.shape[:2], bool)
    m[y0:y1, ombro_x:] = img[y0:y1, ombro_x:, 3] > 0
    return m


def borrao(estendido, guarda, ombro_x, faixa_y, punho=42, fantasmas=None):
    """Corpo da guarda; o braço do estendido vira um borrão de pixel: cunha cheia na cor de cada linha do braço
    (claro em cima, sombra embaixo, contorno escuro), que afina para trás e se desfaz em riscos de velocidade de
    comprimentos diferentes; punho nítido na ponta. (fantasmas: não usado, fica pela compatibilidade)"""
    out = guarda.copy()
    m = braco(estendido, ombro_x, faixa_y)
    ys, xs = np.nonzero(m)
    if not len(xs):
        return out
    x_ponta = xs.max()
    x_punho = x_ponta - punho
    # o braço da guarda (punho levantado na frente do peito) some: o braço está "no caminho"
    mg = braco(guarda, ombro_x + 8, (faixa_y[0] - 30, faixa_y[1]))
    out[mg] = 0
    y0, y1 = ys.min(), ys.max()
    yc = (y0 + y1) / 2
    meia = (y1 - y0) / 2
    comp = x_punho - ombro_x
    linhas = {}
    for y in range(y0, y1 + 1):
        lx = np.nonzero(m[y])[0]
        cores = estendido[y, lx] if len(lx) else np.zeros((0, 4), np.uint8)
        cores = cores[cores[:, 3] > 0]
        if len(cores):
            linhas[y] = np.median(cores[:, :3], 0).astype(np.uint8)
    escuro = np.array([60, 30, 30], np.uint8)
    for y, c in linhas.items():
        d = abs(y - yc) / max(1.0, meia)          # 0 no meio, 1 na borda
        # a cunha afina para trás: linha da borda começa perto do punho, a do meio perto do ombro
        ini = ombro_x + int(comp * (0.15 + 0.6 * d * d))
        # riscos de velocidade: algumas linhas começam bem mais atrás (comprimentos desencontrados)
        h = (y * 7919) % 5
        if h == 0:
            ini = max(ombro_x - 10, ini - int(comp * 0.35))
        cor = escuro if (y in (y0, y1)) else c
        out[y, ini:x_punho + 4, :3] = cor
        out[y, ini:x_punho + 4, 3] = 255
        if h == 0 and y not in (y0, y1):  # o risco comprido é claro (brilho do movimento)
            out[y, ini:ini + int(comp * 0.3), :3] = np.minimum(255, c.astype(int) + 60).astype(np.uint8)
    pun = np.zeros_like(m)
    pun[:, x_punho:] = m[:, x_punho:]
    py, px = np.nonzero(pun)
    out[py, px] = estendido[py, px]
    # dois riscos brancos de velocidade, acima e abaixo
    for y, a, b in ((y0 - 6, ombro_x + int(comp * .35), x_punho - 8), (y1 + 6, ombro_x + int(comp * .5), x_punho - 14)):
        out[y:y + 2, a:b] = BRANCO
    return out


def vento(img, x, y, alt=46, larg=30):
    """Arco de vento na frente do punho (meia-lua aberta para trás, linhas de 2 px), em x,y = centro do contato."""
    out = img.copy()
    for k, (r, cor) in enumerate(((alt / 2, BRANCO), (alt / 2 - 7, CLARO), (alt / 2 + 8, MEIO))):
        for t in np.linspace(-1.1, 1.1, 120):
            xx = int(round(x + larg * 0.5 * np.cos(t) - k * 6))
            yy = int(round(y + r * np.sin(t)))
            if 0 <= yy < out.shape[0] - 1 and 0 <= xx < out.shape[1] - 1:
                out[yy:yy + 2, xx:xx + 2] = cor
    for d, comp in ((-alt // 3, 60), (0, 90), (alt // 3, 60)):  # linhas de velocidade atrás do arco
        yy = int(y + d)
        faixa = out[yy:yy + 2, int(x - comp - 20):int(x - 20)]
        faixa[faixa[..., 3] == 0] = CLARO  # só no vazio: o risco passa por trás do punho
    return out


# ------------------------------------------------------------------ teste do jab
def _q(n, d):
    return np.array(Image.open(RAIZ / f"sprites/hazaki/quadros_pecas_hd/{n}/{d:02d}.png").convert("RGBA"))


def versoes():
    """(nome, [(imagem, ticks)]) do jab (ação 200) de hoje e das duas ideias, com os mesmos ticks e o mesmo contato."""
    g, prep, sai, est, volta, fim = (_q("soco", i) for i in (0, 1, 2, 2, 3, 5))
    est = _q("soco", 2)
    hoje = [(_q("soco", i), t) for i, t in zip(range(6), (1, 2, 3, 2, 2, 3))]
    ombro, faixa = 600, (420, 466)
    xs = np.nonzero(braco(est, ombro, faixa))[1]
    ponta = int(xs.max())
    b_ida = borrao(est, prep, ombro, faixa)
    b_volta = borrao(est, _q("soco", 3), ombro, faixa, fantasmas=(0.5,))
    com_borrao = [(g, 1), (b_ida, 2), (vento(est, ponta + 14, 444, alt=36), 3), (b_volta, 2), (_q("soco", 4), 2),
                  (_q("soco", 5), 3)]
    # só vento: o braço não aparece esticado; no contato o ombro está à frente e o vento estoura onde o punho chegaria
    so_vento = [(g, 1), (prep, 2), (vento(b_volta, ponta + 14, 444), 3), (vento(_q("soco", 3), ponta + 30, 444, alt=30), 2),
                (_q("soco", 4), 2), (_q("soco", 5), 3)]
    return [("HOJE", hoje), ("BORRAO", com_borrao), ("SO VENTO", so_vento)]


def teste(saida):
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    cols = versoes()
    caixa = (380, 300, 820, 670)
    w, h = caixa[2] - caixa[0], caixa[3] - caixa[1]
    fundo = (40, 52, 110)
    seqs = []
    for nome, els in cols:
        s = []
        for _ in range(6):  # 6 repetições com 20 ticks de guarda entre elas
            for img, t in els:
                s += [img] * t
            s += [els[0][0]] * 20
        seqs.append(s)
    n = min(len(s) for s in seqs)
    dirq = saida / "q"
    dirq.mkdir(exist_ok=True)
    for i in range(n):
        o = Image.new("RGB", (w * 3 + 16, h + 40), fundo)
        for k, s in enumerate(seqs):
            im = Image.fromarray(s[i]).crop(caixa)
            o.paste(im, (k * (w + 8), 40), im)
        o.save(dirq / f"{i:04d}.png")
    # tira quadro a quadro de cada versão
    for nome, els in cols:
        o = Image.new("RGB", (w * len(els), h), fundo)
        for k, (img, t) in enumerate(els):
            im = Image.fromarray(img).crop(caixa)
            o.paste(im, (k * w, 0), im)
        o.save(saida / f"tira_{nome.replace(' ', '_').lower()}.png")
    f = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    txt = ",".join(f"drawtext=fontfile={f}:text='{nome}':x={k * (w + 8) + 12}:y=8:fontsize=24:fontcolor=white"
                   for k, (nome, _) in enumerate(cols))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "60", "-i", str(dirq / "%04d.png"), "-vf",
                    txt + ",scale=-2:720:flags=neighbor,format=yuv420p", "-c:v", "libx264", "-crf", "20",
                    str(saida / "jab_borrao_teste.mp4")], check=True)
    # versão em câmera lenta (1/4) para ver quadro a quadro
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "15", "-i", str(dirq / "%04d.png"), "-vf",
                    txt + ",scale=-2:720:flags=neighbor,format=yuv420p", "-c:v", "libx264", "-crf", "20",
                    str(saida / "jab_borrao_teste_lento.mp4")], check=True)
    print(saida / "jab_borrao_teste.mp4")


if __name__ == "__main__":
    if sys.argv[1] == "teste":
        teste(sys.argv[2])
