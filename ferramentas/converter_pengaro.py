#!/usr/bin/env python3
"""Pengaró (forma normal): converte as folhas do padrão novo (sprites/pengaro/quadros/folhas_novas/, 2026-11-13) nos
desenhos do jogo, direto da folha, em 1x e em 3x, como o CK (converter_ck.py com HD=3):

  python ferramentas/converter_pengaro.py              todas as folhas novas
  python ferramentas/converter_pengaro.py soco pulo    só essas

Saída: quadros_arcade/<folha>/00..07.png (tela 360x260, pés em 180,220) e quadros_arcade_hd/<folha>/00..07.png (o
mesmo desenho em 3x, 1080x780, pés em 540,660), tirados da MESMA folha grande: o 3x tem o detalhe da folha (não é o 1x
ampliado). Os dois saem sem misturar cor na borda (alfa seco). As e_<folha> (endiabrado) não são tocadas.
A escala é uma só para todas as folhas: a figura em pé da referencia_ginga fica com a altura do Pengaró de antes
(ALTURA_1X = 111 px em 1x), para o jogo, as caixas de golpe e o endiabrado não mudarem de tamanho.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("LUTADOR", "pengaro")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

import animar_folha as af  # noqa: E402
from animar_cenario import sem_rosa  # noqa: E402

SPRITES = af.RAIZ / "sprites/pengaro"
FOLHAS = SPRITES / "quadros/folhas_novas"
ALTURA_1X = 111
ANTES_DO_PADRAO_NOVO = "965f8013"   # o último commit com os desenhos antigos em quadros_arcade/
# folhas sem desenho antigo para medir a escala: o quadro (folha, i) fica da altura do quadro (modelo, j) já convertido,
# que tem a mesma pose (parry alto = guarda em pé da defesa; parry baixo = base agachada da rasteirinha)
MESMA_POSE = {"parry_alto": (0, "defesa", 0), "parry_baixo": (0, "rasteirinha", 0)}


def figuras(folha):
    img = af.fundo_ck(Image.open(folha))   # fundo magenta com degradê vira #FF00FF exato e separa figuras grudadas
    return img


def altura_referencia():
    """Altura (px da folha) da figura em pé da referência, a mediana dos 8 desenhos."""
    img = figuras(FOLHAS / "referencia_ginga.png")
    a = np.asarray(af.tira_fundo(img))[..., 3] > 0
    lq = a.shape[1] / 8
    alturas = []
    for i in range(8):
        ys = np.flatnonzero(a[:, round(i * lq):round((i + 1) * lq)].any(axis=1))
        alturas.append(ys[-1] - ys[0] + 1)
    return float(np.median(alturas))


def seco(q):
    q.putalpha(q.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    return sem_rosa(q)


def tamanho(q):
    """Maior lado da caixa da figura (px)."""
    caixa = q.getchannel("A").getbbox()
    return max(caixa[2] - caixa[0], caixa[3] - caixa[1]) if caixa else 0


def antigos(nome):
    """Os 8 desenhos 1x de antes (git, commit ANTES_DO_PADRAO_NOVO), na mesma pose: dão a escala certa de cada folha,
    porque o ChatGPT desenha cada folha num tamanho um pouco diferente e o alcance dos golpes depende dele."""
    import io
    import subprocess
    out = []
    for i in range(8):
        b = subprocess.run(["git", "show", f"{ANTES_DO_PADRAO_NOVO}:sprites/pengaro/quadros_arcade/{nome}/{i:02d}.png"],
                           cwd=af.RAIZ, capture_output=True).stdout
        out.append(Image.open(io.BytesIO(b)).convert("RGBA") if b else None)
    return out


def converter(nome, fator):
    img = figuras(FOLHAS / f"{nome}.png")
    velhos = antigos(nome)
    if all(velhos):
        novos = af.por_celula(img, fator, 1)
        razoes = [tamanho(v) / tamanho(n) for v, n in zip(velhos, novos) if tamanho(n)]
        fator *= float(np.median(razoes))
    elif nome in MESMA_POSE:
        i, modelo, j = MESMA_POSE[nome]
        alvo = Image.open(SPRITES / "quadros_arcade" / modelo / f"{j:02d}.png").getchannel("A").getbbox()
        meu = af.por_celula(img, fator, 1)[i].getchannel("A").getbbox()
        fator *= (alvo[3] - alvo[1]) / (meu[3] - meu[1])
    for k, pasta in ((1, "quadros_arcade"), (3, "quadros_arcade_hd")):
        destino = SPRITES / pasta / nome
        destino.mkdir(parents=True, exist_ok=True)
        for i, q in enumerate(af.por_celula(img, fator * k, k)):
            seco(q).save(destino / f"{i:02d}.png")
    print(f"{nome}: 8 desenhos em 1x e 3x (escala {fator:.4f})")


def main():
    alt = altura_referencia()
    fator = ALTURA_1X / alt
    print(f"referência: figura em pé com {alt:.0f} px na folha; escala 1x = {fator:.4f}")
    nomes = sys.argv[1:] or sorted(p.stem for p in FOLHAS.glob("*.png") if p.stem != "referencia_ginga")
    for n in nomes:
        converter(n, fator)


if __name__ == "__main__":
    main()
