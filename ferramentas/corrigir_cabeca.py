#!/usr/bin/env python3
"""Conserta o tamanho da cabeça nos quadros que já estão no jogo, sem redesenhar o resto (pedido do Alisson, 16/11).

O boneco de peças montado do zero mudava o movimento e chapava a cor. Aqui o quadro original fica como está (mesma
pose, mesmo contorno, mesmas cores) e só a cabeça, que é o que varia de um desenho para o outro, volta para o tamanho
do parado de referência:

  1. a régua (ferramentas/pixel/reguas.py) acha a cabeça do parado no quadro e dá a escala dela (ex.: 110%);
  2. a cabeça é recortada acima da linha do queixo e encolhida em volta do queixo, com Scale2x três vezes e
     amostragem (não borra e não vira escada);
  3. o pescoço que ficava atrás da cabeça é puxado para cima (o mesmo que `pixel.py estica`), para não abrir
     buraco entre a cabeça e os ombros;
  4. a régua mede de novo.

  python ferramentas/corrigir_cabeca.py ENTRADA.png SAIDA.png [--escala 1.10]
  python ferramentas/corrigir_cabeca.py --pasta ENTRADA_DIR SAIDA_DIR
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI / "pixel"))
import reguas  # noqa: E402
from pixel import scale2x  # noqa: E402

RAIZ = AQUI.parent
REF = RAIZ / "sprites/pengaro/quadros_arcade_hd/ginga/00.png"
QUEIXO_REF = 392      # linha do queixo no parado de referência (ginga/00, 3x)
LIMITE = 0.03         # abaixo disso a cabeça fica como está
PESCOCO = 14          # quantas linhas acima do queixo o pescoço é puxado para tapar a folga


def abrir(c):
    return np.asarray(Image.open(c).convert("RGBA")).copy()


def referencia():
    r = abrir(REF)
    tmpl, caixa = reguas.cabeca_do_parado(r)
    return tmpl, caixa


def encolher(pedaco, f, pivo):
    """Encolhe o RGBA f vezes em volta do pivô (x, y): Scale2x x3 e amostra o centro de cada célula."""
    H, W = pedaco.shape[:2]
    big = scale2x(scale2x(scale2x(pedaco)))
    px, py = pivo
    ys, xs = np.mgrid[0:H, 0:W]
    sx = np.floor((px + (xs + 0.5 - px) / f) * 8).astype(int)
    sy = np.floor((py + (ys + 0.5 - py) / f) * 8).astype(int)
    ok = (sx >= 0) & (sy >= 0) & (sx < W * 8) & (sy < H * 8)
    out = np.zeros_like(pedaco)
    out[ok] = big[sy[ok], sx[ok]]
    return out


def corrigir(a, tmpl, caixa, escala=None):
    e, nota, (x, y) = reguas.escala_cabeca(a, tmpl)
    if escala is not None:
        e = escala
    info = {"escala_antes": e, "nota": nota}
    if abs(e - 1) <= LIMITE:
        info["mexeu"] = False
        return a, info
    x0r, y0r, x1r, _ = caixa
    # linha do queixo e centro do rosto neste quadro, pela posição e escala achadas
    queixo = int(round(y + (QUEIXO_REF - y0r) * e))
    cx = int(round(x + (x1r - x0r) * e / 2))
    larg = int((x1r - x0r) * e * 0.7) + 4
    xa, xb = max(0, cx - larg), min(a.shape[1], cx + larg)
    topo = max(0, y - 6)
    m = np.zeros(a.shape[:2], bool)
    m[topo:queixo, xa:xb] = a[topo:queixo, xa:xb, 3] > 0
    # só o que está ligado à cabeça achada: mão levantada perto do rosto fica de fora
    n, lab = cv2.connectedComponents(m.astype(np.uint8), connectivity=4)
    cab = lab[y:y + int((caixa[3] - y0r) * e), x:x + int((x1r - x0r) * e)]
    manter = [v for v in np.unique(cab) if v and (cab == v).sum() > 30]
    m = np.isin(lab, manter)
    cabeca = np.zeros_like(a)
    cabeca[m] = a[m]
    nova = encolher(cabeca, 1 / e, (cx, queixo))
    out = a.copy()
    # some a borda velha da cabeça; na faixa do queixo, a parte de trás (nuca, ombro, trapézio) fica como está e
    # só a frente do queixo velho sai, para não sobrar um queixo fantasma
    sob = nova[..., 3] > 0
    faixa = np.zeros_like(m)
    faixa[max(0, queixo - PESCOCO):queixo] = True
    tras = np.zeros_like(m)
    tras[:, :cx] = True
    apaga = m & ~(faixa & tras)
    out[apaga & ~sob] = 0
    out[sob] = nova[sob]
    info["mexeu"] = True
    info["queixo"] = queixo
    return out, info


def achar(a, tmpl):
    """(escala, ângulo do casamento em graus cv2, centro da faixa do cabelo achada, canto) — o mesmo que
    reguas.escala_cabeca, devolvendo também o ângulo."""
    m = a[..., 3] > 0
    ys, xs = np.nonzero(m)
    pad = int(tmpl.shape[0] * 0.8)
    x0, x1 = max(0, xs.min() - pad), min(a.shape[1], xs.max() + pad)
    y0 = max(0, ys.min() - pad)
    reg = a[y0:min(a.shape[0], ys.min() + int(tmpl.shape[0] * 2.6)), x0:x1]
    v, e, ang, p = reguas._busca(reg, tmpl, np.arange(0.85, 1.15 + 1e-6, 0.01), range(-20, 21, 5))
    tg = reguas._gira(tmpl, ang)
    cx = p[0] + x0 + tg.shape[1] * e / 2
    cy = p[1] + y0 + tg.shape[0] * e / 2
    return e, ang, (cx, cy), (p[0] + x0, p[1] + y0), v


def mascara_cabeca(a, x, y, e, caixa, sem_nuca=False):
    """Pixels da cabeça acima do queixo, ligados à faixa do cabelo achada em (x, y) com escala e. `sem_nuca` tira a
    faixa de trás logo acima do queixo (trapézio e ombro), que no quadro de destino fica a do próprio quadro."""
    x0r, y0r, x1r, y1r = caixa
    queixo = int(round(y + (QUEIXO_REF - y0r) * e))
    cx = int(round(x + (x1r - x0r) * e / 2))
    larg = int((x1r - x0r) * e * 1.0) + 4
    xa, xb = max(0, cx - larg), min(a.shape[1], cx + larg)
    m = np.zeros(a.shape[:2], bool)
    topo = max(0, y - 6)
    m[topo:queixo, xa:xb] = a[topo:queixo, xa:xb, 3] > 0
    n, lab = cv2.connectedComponents(m.astype(np.uint8), connectivity=4)
    cab = lab[y:y + int((y1r - y0r) * e), x:x + int((x1r - x0r) * e)]
    manter = [v for v in np.unique(cab) if v and (cab == v).sum() > 30]
    m = np.isin(lab, manter)
    if sem_nuca:
        m[max(0, queixo - PESCOCO):queixo, :cx] = False
    return m, queixo, cx


def cabeca_da_referencia():
    """Recorte RGBA da cabeça do parado (ginga/00) e o centro da faixa do cabelo dentro dele."""
    r = abrir(REF)
    tmpl, caixa = reguas.cabeca_do_parado(r)
    m, queixo, _ = mascara_cabeca(r, caixa[0], caixa[1], 1.0, caixa, sem_nuca=True)
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rec = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    sub = m[y0:y1, x0:x1]
    rec[sub] = r[y0:y1, x0:x1][sub]
    centro = ((caixa[0] + caixa[2]) / 2 - x0, (caixa[1] + caixa[3]) / 2 - y0)
    return rec, centro


# Expressões do kit: cada uma é um desenho que já existe, levado ao tamanho do parado (régua 100%). O rosto é sempre o
# mesmo; muda só a expressão, e cada quadro escolhe a sua.
EXPRESSOES = {
    "guarda": "ginga/00",        # alerta, boca entreaberta (o parado de referência)
    "foco": "soco/05",           # boca fechada, olhar no alvo
    "esforco": "chute_alto/04",  # dentes cerrados, força no golpe
    "dor": "apanha/00",          # careta de quem apanhou
    "riso": "provoca/06",        # deboche (provocação e vitória)
}


def cabeca_do_kit(nome, tmpl, caixa):
    """Recorte RGBA da expressão `nome`, no tamanho do parado, e o centro da faixa do cabelo nele."""
    if nome == "guarda":
        return cabeca_da_referencia()
    a = abrir(RAIZ / "sprites/pengaro/quadros_arcade_hd" / f"{EXPRESSOES[nome]}.png")
    e, ang, (cx, cy), (x, y), _ = achar(a, tmpl)
    m, _, _ = mascara_cabeca(a, int(x), int(y), e, caixa, sem_nuca=True)
    so = np.zeros_like(a)
    so[m] = a[m]
    if abs(e - 1) > 0.005:
        so = encolher(so, 1 / e, (cx, cy))
    ys, xs = np.nonzero(so[..., 3] > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return so[y0:y1, x0:x1].copy(), (cx - x0, cy - y0)


def trocar(a, tmpl, caixa, cabeca_ref=None):
    """Põe a cabeça do parado (sempre o mesmo rosto) no lugar da cabeça do quadro, no mesmo ponto e no mesmo
    ângulo, com RotSprite. Nuca, ombro e trapézio do quadro ficam."""
    from boneco_ajuste import rotsprite
    rec, centro = cabeca_ref or cabeca_da_referencia()
    e, ang, (cx, cy), (x, y), nota = achar(a, tmpl)
    m, queixo, cxq = mascara_cabeca(a, int(x), int(y), e, caixa)
    nova_rec, piv = rotsprite(rec, -ang, centro)
    nova = np.zeros_like(a)
    ox, oy = int(round(cx - piv[0])), int(round(cy - piv[1]))
    h, w = nova_rec.shape[:2]
    ya, yb, xa, xb = max(0, oy), min(a.shape[0], oy + h), max(0, ox), min(a.shape[1], ox + w)
    nova[ya:yb, xa:xb] = nova_rec[ya - oy:yb - oy, xa - ox:xb - ox]
    sob = nova[..., 3] > 0
    out = a.copy()
    faixa = np.zeros_like(m)
    faixa[max(0, queixo - PESCOCO):queixo] = True
    tras = np.zeros_like(m)
    tras[:, :cxq] = True
    out[m & ~(faixa & tras) & ~sob] = 0
    out[sob] = nova[sob]
    # buraco que sobrou entre a cabeça nova e o pescoço do quadro: volta o pixel original
    cheio = cv2.morphologyEx((out[..., 3] > 0).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)) > 0
    buraco = cheio & (out[..., 3] == 0) & (a[..., 3] > 0)
    out[buraco] = a[buraco]
    # emenda: o contorno escuro do queixo velho que ficou no pescoço (fora da cabeça nova) some, e a pele em volta
    # fecha o lugar (inpaint só nesses pixels)
    zona = np.zeros_like(m)
    zona[max(0, queixo - PESCOCO - 6):min(a.shape[0], queixo + 4)] = True
    rgb = out[..., :3].astype(int)
    escuro = (rgb.sum(-1) < 200) & (out[..., 3] > 0)
    perto_cabeca = cv2.dilate(sob.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    pele_viz = cv2.dilate((~escuro & (out[..., 3] > 0)).astype(np.uint8), np.ones((1, 7), np.uint8)) > 0
    emenda = zona & escuro & ~sob & (m | perto_cabeca) & pele_viz
    # o contorno externo da figura fica: só tira escuro que tem corpo dos dois lados na horizontal
    corpo = out[..., 3] > 0
    esq = np.zeros_like(corpo); esq[:, 4:] = corpo[:, :-4]
    dir_ = np.zeros_like(corpo); dir_[:, :-4] = corpo[:, 4:]
    emenda &= esq & dir_
    if emenda.any():
        out[..., :3] = cv2.inpaint(np.ascontiguousarray(out[..., :3]), emenda.astype(np.uint8), 3, cv2.INPAINT_TELEA)
    return out, {"escala_antes": e, "angulo": ang, "nota": nota}


def main():
    args = sys.argv[1:]
    tmpl, caixa = referencia()
    if args and args[0] == "--pasta":
        ent, sai = Path(args[1]), Path(args[2])
        sai.mkdir(parents=True, exist_ok=True)
        for f in sorted(ent.glob("*.png")):
            out, info = corrigir(abrir(f), tmpl, caixa)
            Image.fromarray(out).save(sai / f.name)
            e2 = reguas.escala_cabeca(out, tmpl)[0]
            print(f"{f.name}: cabeça {info['escala_antes']:.0%} -> {e2:.0%}")
        return
    esc = None
    if "--escala" in args:
        i = args.index("--escala")
        esc = float(args[i + 1])
        del args[i:i + 2]
    out, info = corrigir(abrir(args[0]), tmpl, caixa, esc)
    Image.fromarray(out).save(args[1])
    print(info, "->", reguas.escala_cabeca(out, tmpl)[0])


if __name__ == "__main__":
    main()
