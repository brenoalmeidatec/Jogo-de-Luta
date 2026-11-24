#!/usr/bin/env python3
"""Vida no Diabo Loiro (Hazak despertado). Breno, #32, 24/11: "o Diabo Loiro tá muito estático e os movimentos dele
estão muito simples".

Os desenhos dos golpes do demônio são bons (4 por golpe), mas entravam no jogo como quatro fotos paradas, cada uma
segurada 3 a 12 ticks, com o corpo plantado no mesmo lugar. Aqui, sem mudar tempo, caixa nem o tick do contato
(o jogo não muda), cada golpe ganha pelas leis do estudo de anatomia (docs/estudo-anatomia-golpes.md):

  - antecipação: o corpo recua e afunda no preparo (o peso vai para trás antes do bote);
  - borrão no bote (Lei 10, e a ideia do Breno do soco rápido): o primeiro tick do contato traz o rastro de fogo do
    desenho do preparo por baixo do desenho do golpe, e o corpo inteiro dá um passo à frente (peso no golpe);
  - peso: golpe forte avança e afunda mais que o fraco;
  - volta mais lenta: o corpo volta ao lugar em dois tempos, não de uma vez.

E a ginga (parado) deixa de ser sete fotos trocando a cada 7 ticks: um desenho-chave do demônio respira (o tronco
sobe e desce em cima das pernas do desenho, com quadros do meio), alternando com a garra flexionando.

    python3 ferramentas/diabo_vida.py          grava sprites/diabo_vida/quadros_hd/<golpe>/ (tempos.json)
    python3 ferramentas/ligar_pecas.py hazaki --de diabo_vida --pasta quadros_hd --grupo 62000

Os quadros vão para o .sff em PNG (cores do demônio). O parado é a ação 0 da forma base: no despertado, cada desenho
novo do Hazak vira, pelo remap, o desenho novo do Diabo que está na tela naquele tick.
"""
import io
import json
import re
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import conferir_sff as cs  # noqa: E402
import diabo_demonio as dd  # noqa: E402

RAIZ = AQUI.parent
CHARS = RAIZ / "chars/hazaki"
SAIDA = RAIZ / "sprites/diabo_vida/quadros_hd"
EIXO = (540, 660)
TELA = (1080, 780)
FOGO = np.array([255, 110, 30])
# (recuo do preparo, avanço no bote) em px da tela 3x, por peso
PESO = {"Light": (7, 9), "Medium": (10, 13), "Heavy": (13, 18)}


# ------------------------------------------------------------------ leitura do jogo
def ler_sprites():
    pal, nos, _ = cs.ler(CHARS / "hazaki.sff")
    return pal, {(n["g"], n["i"]): n for n in nos}


def rgba(no, pal):
    px = no["px"]
    if no.get("png"):
        return np.array(Image.open(io.BytesIO(px[px.find(b"\x89PNG"):])).convert("RGBA"))
    p = np.frombuffer(pal, np.uint8).reshape(-1, 4)[:, :3]
    idx = np.frombuffer(px, np.uint8).reshape(no["h"], no["w"])
    out = np.zeros((no["h"], no["w"], 4), np.uint8)
    out[..., :3] = p[idx]
    out[..., 3] = (idx > 0) * 255
    return out


def na_tela(img, x, y, dx=0, dy=0):
    """Sprite com eixo (x, y) na tela 3x com o eixo em EIXO, deslocado dx, dy."""
    t = np.zeros((TELA[1], TELA[0], 4), np.uint8)
    h, w = img.shape[:2]
    x0, y0 = EIXO[0] - x + dx, EIXO[1] - y + dy
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(TELA[0], x0 + w), min(TELA[1], y0 + h)
    t[Y0:Y1, X0:X1] = img[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    return t


def acao(air, n):
    """[(grupo, índice, ticks, ativo)] da ação n do .air."""
    m = re.search(rf"^\[Begin Action {n}\][^\n]*\n(.*?)(?=^\[Begin Action|\Z)", air, re.M | re.S)
    if not m:
        return None
    out, clsn1 = [], False
    for ln in m.group(1).splitlines():
        s = ln.strip()
        if re.match(r"clsn1\s*:", s, re.I):
            clsn1 = True
        e = re.match(r"^\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)", ln)
        if e:
            g, i, x, y, t = (int(v) for v in e.groups())
            assert (x, y) == (0, 0), f"ação {n}: elemento com deslocamento ({x},{y}), não tratado"
            out.append((g, i, t, clsn1))
            clsn1 = False
    return out


# ------------------------------------------------------------------ desenho
def rastro(prev, cur, so_em_cima=False):
    """Rastro de fogo (afterimage) só do que se mexeu: a parte do desenho do preparo que não está no desenho do golpe
    (garra, braço, perna que bate), em brasa e em listras de 3 px (meio transparente na tela 1x), sem migalha."""
    import cv2
    m = (prev[..., 3] > 0) & (cur[..., 3] == 0)
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    m = np.isin(lab, [i for i in range(1, n) if st[i, 4] >= 300])
    ys = np.arange(m.shape[0])[:, None]
    m &= (ys // 3) % 2 == 0
    if so_em_cima:  # golpe de garra: o pé não deixa rastro (só o deslocamento do corpo)
        m[EIXO[1] - 90:] = False
    out = np.zeros_like(prev)
    out[m, :3] = np.clip(prev[m, :3].astype(int) * 0.3 + FOGO * 0.7, 0, 255).astype(np.uint8)
    out[m, 3] = 255
    return out


def por_baixo(cima, baixo):
    out = cima.copy()
    vazio = (out[..., 3] == 0) & (baixo[..., 3] > 0)
    out[vazio] = baixo[vazio]
    return out


def golpe(n, g, air, pal, spr):
    """Linha do tempo nova da ação n: [(imagem, ticks, ativo, de)] com o mesmo total e o contato no mesmo tick."""
    els = acao(air, n)
    if not els or not any(e[3] for e in els):
        return None
    recuo, avanco = PESO[g["peso"]]
    img = [na_tela(rgba(spr[(gg, i)], pal), spr[(gg, i)]["x"], spr[(gg, i)]["y"]) for gg, i, _, _ in els]
    dsl = lambda k, dx, dy=0: np.roll(np.roll(img[k], dy, 0), dx, 1)  # noqa: E731
    a = next(k for k, e in enumerate(els) if e[3])
    seq = []
    for k, (gg, i, t, at) in enumerate(els):
        de = f"{gg},{i}"
        if t < 0:  # segura até cair (golpe no ar): fica como está
            seq.append((img[k], t, at, de))
            continue
        if k < a:  # preparo: recua e afunda; o último preparo é o mais fundo
            if k == a - 1 and t >= 2:
                h = t // 2
                seq += [(dsl(k, -recuo // 2, 2), h, at, de), (dsl(k, -recuo, 4), t - h, at, de)]
            else:
                seq.append((dsl(k, -recuo // 2 if k else 0, 2 if k else 0), t, at, de))
        elif k == a:  # bote: 1º tick com o rastro de fogo do preparo e o corpo à frente; depois assenta
            # o rastro sai do desenho do preparo no mesmo lugar do golpe: o corpo coincide e só o membro deixa rastro
            prev = dsl(k - 1, avanco // 2) if k else img[k]
            bote = por_baixo(dsl(k, avanco), rastro(prev, dsl(k, avanco), so_em_cima="maos" in g["folha"]))
            if t >= 2:
                seq += [(bote, 1 if t <= 3 else 2, at, de), (dsl(k, avanco * 2 // 3), t - (1 if t <= 3 else 2), at, de)]
            else:
                seq.append((bote, t, at, de))
        elif at:  # ainda batendo
            seq.append((dsl(k, avanco * 2 // 3), t, at, de))
        else:  # volta mais lenta, em dois tempos
            primeiro = k == next((j for j in range(a + 1, len(els)) if not els[j][3]), None)
            if primeiro and t >= 2:
                h = (t + 1) // 2
                seq += [(dsl(k, avanco // 2), h, at, de), (dsl(k, avanco // 5), t - h, at, de)]
            else:
                seq.append((img[k], t, at, de))
    assert sum(e[1] for e in seq if e[1] > 0) == sum(e[2] for e in els if e[2] > 0)
    return seq


# ------------------------------------------------------------------ ginga
CHAVES = (0, 4, 5)   # desenhos do m_parado parecidos (garras baixas): o corpo respira entre eles
GARRA = 3            # garra flexionando (meio da ginga)
CINTO = 0.52         # altura do cinto na figura (fração da altura, de cima)


def ginga(pal, spr, total_ticks, n_el):
    """Ginga do Diabo: o tronco sobe e desce (respira) em cima das pernas do desenho, quadros do meio de 2-3 ticks."""
    base = [(21328 + c, 0) for c in range(7)]  # m_parado/00..06 (o 07 não está no .sff)
    imgs = [na_tela(rgba(spr[b], pal), spr[b]["x"], spr[b]["y"]) for b in base]
    # respiração: 0 -> -3 -> 0 (tronco), pernas fixas; chaves trocam no fundo do fôlego
    resp = [0, -1, -2, -3, -3, -2, -1]  # 1 px na tela do jogo: respira sem abrir costura nas garras
    seq = []
    ordem = [0, 0, 0, 4, 4, 4, 5, 5, 5, 3, 3, 3, 5, 5, 5, 4, 4, 4, 0, 0, 0][:n_el]
    for j, c in enumerate(ordem):
        im = imgs[c]
        ys = np.nonzero(im[..., 3].any(1))[0]
        cinto = int(ys.min() + CINTO * (ys.max() - ys.min()))
        dy = resp[j % len(resp)]
        out = im.copy()
        cima = np.zeros_like(im)
        cima[:cinto] = im[:cinto]
        out[:cinto] = 0
        out[cinto - 8:cinto] = im[cinto - 8:cinto]  # o paletó por baixo do tronco (sem vão quando ele sobe)
        cima = np.roll(cima, dy, 0)
        a = cima[..., 3] > 0
        out[a] = cima[a]
        seq.append((out, f"m_parado/{c:02d}"))
    return seq


def gravar(nome, acao_n, seq, caixa=None):
    for d in (SAIDA / nome,):
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
    els = []
    for k, (img, t, at, de) in enumerate(seq):
        Image.fromarray(img).save(SAIDA / nome / f"{k:02d}.png")
        els.append({"desenho": k, "ticks": t, "caixa": bool(at), "de": de})
    (SAIDA / nome / "tempos.json").write_text(json.dumps({"acao": acao_n, "caixa": caixa, "elementos": els},
                                                         indent=1, ensure_ascii=False), encoding="utf-8")


def main():
    air = (CHARS / "hazaki.air").read_text(encoding="utf-8")
    pal, spr = ler_sprites()
    shutil.rmtree(SAIDA, ignore_errors=True)
    feitos = 0
    for n, g in sorted(dd.GOLPES.items()):
        seq = golpe(n, g, air, pal, spr)
        if seq is None:
            continue
        gravar(f"g{n}", n, seq)
        feitos += 1
    # ginga: mesma linha do tempo do parado do Hazak (21 desenhos)
    t = json.loads((RAIZ / "sprites/hazaki/quadros_pecas_hd/parado/tempos.json").read_text(encoding="utf-8"))
    tk = [e["ticks"] for e in t["elementos"]]
    g = ginga(pal, spr, sum(tk), len(tk))
    gravar("parado", 0, [(img, tk[k], False, de) for k, (img, de) in enumerate(g)])
    print(f"{feitos} golpes do Diabo e a ginga em {SAIDA}")


if __name__ == "__main__":
    main()
