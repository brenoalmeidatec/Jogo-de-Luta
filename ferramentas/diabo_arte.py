#!/usr/bin/env python3
"""Arte do Diabo Loiro (o Hazak despertado) montada por código a partir de cada desenho 3x do Hazak (issue #44).

Quebra-galho aceito pelas regras dos lutadores (seção 4: recolorir por código até a folha redesenhada ficar pronta), mas
indo além da cor: o mesmo desenho ganha o que a ficha (docs/fichas/hazaki.md) e o estudo arcade (docs/arcade/hazaki.md
(a), paleta do Diabo) pedem para a forma:
  - juba loira comprida jogada para trás (o cabelo preto vira loiro e ganha mechas que descem pelas costas);
  - dois chifres escuros curvos saindo da testa, virados para trás;
  - olho vermelho aceso;
  - gi das trevas (roxo quase preto, sem luz) e o debrum laranja vira brasa acesa; faixa marrom-escura.
O corpo, a pose, o tamanho e as caixas não mudam: o RemapPreset troca desenho por desenho (diabo_loiro.py).

Entrada e saída por índice da paleta fixa do Hazak (sprites/hazaki/paleta_arcade.json, índices 1 a 15 no .sff):
  diabo(indices, eixo) -> RGBA (PIL) do mesmo tamanho, mais a margem para a juba e os chifres (devolve o eixo novo).
"""
import math

import numpy as np
from PIL import Image, ImageDraw

# índices da paleta do corpo
CONTORNO, PELE_CONT, PELE_SOMB, PELE_MED, PELE_LUZ, PELE_BRI = 1, 2, 3, 4, 5, 6
GI_ESC, GI_MED, GI_LUZ, DEB, DEB_SOMB, FAIXA, ATAD, ATAD_SOMB, PULSEIRA = 7, 8, 9, 10, 11, 12, 13, 14, 15
PELE = (PELE_CONT, PELE_SOMB, PELE_MED, PELE_LUZ, PELE_BRI)

HEX = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
CORES = {  # paleta do Diabo (docs/arcade/hazaki.md (a)), gi puxado para o roxo do conceito
    CONTORNO: "#160e1e", PELE_CONT: "#7a2e26", PELE_SOMB: "#b04f30", PELE_MED: "#de8448", PELE_LUZ: "#f6b468",
    PELE_BRI: "#fcd9a0", GI_ESC: "#1e1428", GI_MED: "#33224a", GI_LUZ: "#4c3468", DEB: "#ffb02e", DEB_SOMB: "#de6a20",
    FAIXA: "#5a3a2c", ATAD: "#f4f1ea", ATAD_SOMB: "#a9a6cc", PULSEIRA: "#2a9d9a",
}
LOIRO = [HEX(h) for h in ("#5e3414", "#a8662a", "#d89a3c", "#f2d27a", "#fff0b4")]  # contorno, sombra, médio, luz, brilho
CHIFRE = [HEX(h) for h in ("#1a0e10", "#3a2420", "#6a4030", "#a8704a")]
OLHO = HEX("#ff2a14")
MARGEM = 90  # px (3x) a mais em cada lado para a juba e os chifres


def _componentes(mask):
    """Rótulos 4-conexos (sem scipy)."""
    h, w = mask.shape
    rot = np.zeros((h, w), np.int32)
    n = 0
    for y, x in zip(*np.nonzero(mask)):
        if rot[y, x]:
            continue
        n += 1
        pilha = [(y, x)]
        rot[y, x] = n
        while pilha:
            cy, cx = pilha.pop()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = cy + dy, cx + dx
                if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not rot[yy, xx]:
                    rot[yy, xx] = n
                    pilha.append((yy, xx))
    return rot, n


def _dilata(m, r):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dy * dy + dx * dx > r * r:
                continue
            out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def achar_cabelo(ind):
    """Máscara do cabelo: a mancha do índice 12 (faixa e cabelo dividem a cor) mais encostada na pele e mais alta."""
    faixa = ind == FAIXA
    if not faixa.any():
        return None
    rot, n = _componentes(faixa)
    pele = np.isin(ind, PELE)
    viz_pele = _dilata(pele, 3)
    viz_gi = _dilata(np.isin(ind, (GI_ESC, GI_MED, GI_LUZ)), 3)
    cands = []
    for k in range(1, n + 1):
        m = rot == k
        tam = m.sum()
        if tam < 60:
            continue
        ys, xs = np.nonzero(m)
        p, g = (viz_pele & m).sum() / tam, (viz_gi & m).sum() / tam
        if p >= 0.3 and g <= 0.25:
            cands.append((ys.min(), m, (ys.min(), ys.max(), xs.min(), xs.max())))
    if not cands:
        return None
    cands.sort(key=lambda c: c[0])
    _, melhor, (y0, y1, x0, x1) = cands[0]
    # cabelo partido pela pele (franja, orelha): junta as manchas que encostam na caixa do de cima
    for _, m, (a0, a1, b0, b1) in cands[1:]:
        if a0 <= y1 + 8 and b1 >= x0 - 8 and b0 <= x1 + 8 and a1 - a0 < (y1 - y0) * 1.5:
            melhor = melhor | m
    return melhor


def _pinta(img, mask, cor):
    a = np.asarray(img).copy()
    a[mask] = (*cor, 255)
    return Image.fromarray(a, "RGBA")


def diabo(ind, eixo):
    """ind: matriz de índices (0 transparente). Devolve (RGBA com margem, eixo novo)."""
    h, w = ind.shape
    M = MARGEM
    base = np.zeros((h + 2 * M, w + 2 * M), np.uint8)
    base[M:M + h, M:M + w] = ind
    ind = base
    H, W = ind.shape
    rgba = np.zeros((H, W, 4), np.uint8)
    for k, c in CORES.items():
        rgba[ind == k] = (*HEX(c), 255)
    cabelo = achar_cabelo(ind)
    if cabelo is not None:
        rgba = _cabelo(ind, rgba, cabelo)
    return Image.fromarray(rgba, "RGBA"), (eixo[0] + M, eixo[1] + M)


def _cabelo(ind, rgba, cabelo):
    ys, xs = np.nonzero(cabelo)
    topo, base_y = ys.min(), ys.max()
    esq, dir_ = xs.min(), xs.max()
    alt, larg = base_y - topo + 1, dir_ - esq + 1
    cx, cy = xs.mean(), ys.mean()
    # rosto: pele logo abaixo do cabelo; o lado do rosto é a frente
    pele = np.isin(ind, PELE)
    perto = _dilata(cabelo, 12) & pele
    if perto.any():
        fy, fx = np.nonzero(perto)
        frente = 1 if fx.mean() >= cx else -1
    else:
        frente = 1
    s = max(18.0, max(alt, larg) * 1.0)  # tamanho da cabeça em px 3x
    # cabelo loiro: luz em cima, sombra embaixo e atrás
    rel = (ys - topo) / max(1, alt)
    tras = (xs - cx) * -frente / max(1, larg)
    tom = np.where(rel < 0.35, 3, np.where(rel < 0.7, 2, 1))
    tom = np.where(tras > 0.25, np.maximum(1, tom - 1), tom)
    for t in (1, 2, 3):
        sel = np.zeros_like(cabelo)
        sel[ys[tom == t], xs[tom == t]] = True
        rgba[sel] = (*LOIRO[t], 255)
    img = Image.fromarray(rgba, "RGBA")
    a = np.asarray(img).copy()
    # juba: mechas em ponta que saem da linha do cabelo e vão para trás (umas sobem um pouco, outras caem nas costas).
    # Cada mecha é um polígono afinando até a ponta; o lado de cima da mecha leva luz e o de baixo, sombra.
    rot = Image.new("L", img.size, 0)
    lado = Image.new("L", img.size, 0)
    dr, dl = ImageDraw.Draw(rot), ImageDraw.Draw(lado)
    frente_x = xs.max() if frente > 0 else xs.min()
    mechas = [  # (onde nasce na linha do cabelo: 0 = testa, 1 = nuca; ângulo para trás em graus, + desce; comp; grossura)
        (0.0, -22, 1.25, 0.30), (0.15, -8, 1.6, 0.34), (0.3, 6, 1.85, 0.36), (0.45, 22, 1.9, 0.36),
        (0.6, 40, 1.75, 0.34), (0.75, 58, 1.5, 0.3), (0.9, 72, 1.15, 0.26)]
    for k, (pos, graus, comp, grossura) in enumerate(mechas):
        x0 = frente_x - frente * larg * (0.25 + 0.7 * pos)
        y0 = topo + alt * (0.05 + 0.6 * pos ** 1.3)
        ang = math.radians(graus)
        centro = []
        for j in range(11):
            u = j / 10
            g = ang + u * math.radians(25)  # a ponta cai com o peso
            centro.append((x0 - frente * math.cos(g) * s * comp * u, y0 + math.sin(g) * s * comp * u))
        esq, dir_ = [], []
        for j, (x, y) in enumerate(centro):
            u = j / 10
            r = s * grossura * 0.5 * (1 - u) ** 0.9
            if j < 10:
                nx, ny = centro[j + 1][0] - x, centro[j + 1][1] - y
            else:
                nx, ny = x - centro[j - 1][0], y - centro[j - 1][1]
            n = math.hypot(nx, ny) or 1
            px, py = -ny / n, nx / n
            if py > 0:   # (px, py) aponta para cima: o lado "esq" é sempre o de cima
                px, py = -px, -py
            esq.append((x + px * r, y + py * r))
            dir_.append((x - px * r, y - py * r))
        dr.polygon(esq + dir_[::-1], fill=k + 1)
        dl.polygon(esq + centro[::-1], fill=k + 1)  # metade de cima da mecha
    rot, lado = np.asarray(rot), np.asarray(lado)
    jm = rot > 0
    vazio = a[..., 3] == 0
    pode = vazio | cabelo
    jm &= pode
    if jm.any():
        jys, jxs = np.nonzero(jm)
        cima = lado[jys, jxs] == rot[jys, jxs]
        perto = np.hypot(jxs - cx, jys - cy) < s * 0.9
        tom = np.where(cima, np.where(perto, 4, 3), np.where(perto, 2, 1))
        a[jys, jxs, :3] = np.array(LOIRO)[tom]
        a[jys, jxs, 3] = 255
        # risco escuro entre uma mecha e a outra (separa as pontas, como no desenho à mão)
        troca = np.zeros_like(jm)
        troca[:, 1:] |= (rot[:, 1:] != rot[:, :-1]) & jm[:, 1:] & jm[:, :-1]
        troca[1:, :] |= (rot[1:, :] != rot[:-1, :]) & jm[1:, :] & jm[:-1, :]
        a[troca] = (*LOIRO[1], 255)
        borda = _dilata(jm, 3) & ~jm & (a[..., 3] == 0)
        a[borda] = (*LOIRO[0], 255)
    # chifres: nascem na testa (frente do alto da cabeça), sobem e curvam para trás, afinando até a ponta
    img = Image.fromarray(a, "RGBA")
    d = ImageDraw.Draw(img)
    for k, (atras, esc) in enumerate(((0.32, 0.85), (0.0, 1.0))):  # o de trás primeiro (fica atrás do da frente)
        bx = frente_x - frente * (larg * 0.22 + s * atras)
        by = topo + alt * 0.12
        ctrl = [(0, 0), (frente * 0.12, -0.45), (-frente * 0.3, -0.78), (-frente * 0.78, -0.62)]
        pts = []
        for j in range(13):
            u = j / 12
            b = [(1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3]
            pts.append((bx + s * esc * sum(w * c[0] for w, c in zip(b, ctrl)),
                        by + s * esc * sum(w * c[1] for w, c in zip(b, ctrl))))
        esq, dir_ = [], []
        for j, (x, y) in enumerate(pts):
            u = j / 12
            r = s * esc * 0.12 * (1 - u) + 1.5
            nx, ny = (pts[min(j + 1, 12)][0] - pts[max(j - 1, 0)][0], pts[min(j + 1, 12)][1] - pts[max(j - 1, 0)][1])
            n = math.hypot(nx, ny) or 1
            px, py = -ny / n, nx / n
            esq.append((x + px * r, y + py * r))
            dir_.append((x - px * r, y - py * r))
        poli = esq + dir_[::-1]
        d.polygon(poli, fill=(*CHIFRE[0], 255), outline=(*CHIFRE[0], 255), width=6)
        cor = CHIFRE[2] if k else CHIFRE[1]
        d.polygon(poli, fill=(*cor, 255))
        meio = [((e[0] + c[0]) / 2, (e[1] + c[1]) / 2) for e, c in zip(esq, pts)]
        d.line(meio[1:9], fill=(*CHIFRE[3 if k else 2], 255), width=max(2, int(s * 0.05)))
        for j in (3, 6, 9):  # anéis do chifre
            d.line([esq[j], dir_[j]], fill=(*CHIFRE[0], 255), width=2)
    # olho: o pixel escuro da pele (contorno) no meio do rosto, logo abaixo do cabelo, na frente
    a = np.asarray(img).copy()
    if perto.any():
        caixa_y0, caixa_y1 = base_y - alt * 0.1, base_y + s * 0.45
        frente_x = fx.max() if frente > 0 else fx.min()
        caixa_x0, caixa_x1 = sorted((frente_x - frente * s * 0.55, frente_x - frente * s * 0.05))
        yy, xx = np.nonzero(np.isin(ind, (CONTORNO, PELE_CONT)))
        sel = (yy >= caixa_y0) & (yy <= caixa_y1) & (xx >= caixa_x0) & (xx <= caixa_x1)
        if sel.any():
            ey, ex = yy[sel], xx[sel]
            # o olho é o escuro mais alto dessa caixa (a sobrancelha/olho), não a boca
            top = ey <= ey.min() + 6
            gy, gx = int(ey[top].mean()), int(ex[top].mean())
            for dy in range(0, 3):
                for dx in range(-3, 3):
                    y, x = gy + dy, gx + dx
                    if 0 <= y < a.shape[0] and 0 <= x < a.shape[1] and a[y, x, 3]:
                        a[y, x] = (255, 236, 120, 255) if (dy, dx) == (1, 0) else (*OLHO, 255)
    return a
