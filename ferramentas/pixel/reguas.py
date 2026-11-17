"""Réguas de anatomia: comparam cada quadro com a pose parada da mesma forma.

  escala da cabeça   acha a cabeça do parado (topo da figura) no quadro, testando tamanhos de 80% a 125% e giros de
                     -30 a 30 graus; o tamanho que casa melhor é a escala da cabeça. Passou de LIMITE (3%) = aviso.
                     De costas ou com o rosto escondido o casamento fica fraco e o quadro sai como "não medido".
  escala do corpo    raiz da área da figura (pixels pintados) dividida pela do parado. A área quase não muda com a pose
                     no desenho 2D; agachado ela cai um pouco (perna dobrada esconde perna), por isso o limite é largo.
  membros            manchas de pele separadas (mãos, antebraços, rosto). Mais manchas que o parado + 1 = aviso de
                     membro sobrando (o Diabo com a mão da maleta e outro punho). É um aviso para olhar, não uma prova.
  cores              pixels fora da paleta da forma.
"""
import numpy as np
import cv2

from quadros import abrir, paleta

LIMITE = 0.03
LIMITE_CORPO = 0.12
FAIXA = (0.80, 1.25)


def mascara(a):
    return a[..., 3] > 0


def cabeca_do_parado(a):
    """Recorte da cabeça no parado: a faixa de cima da figura, com 13% da altura dela (cabelo, testa, rosto; sem
    ombro, que muda com a pose)."""
    m = mascara(a)
    ys, xs = np.nonzero(m)
    y0, y1 = ys.min(), ys.max()
    alt = int(round((y1 - y0 + 1) * 0.13))
    faixa = m[y0:y0 + alt]
    cols = np.nonzero(faixa.any(0))[0]
    x0, x1 = cols.min(), cols.max()
    return a[y0:y0 + alt, x0:x1 + 1], (x0, y0, x1 + 1, y0 + alt)


def _cinza(a):
    """RGB float com o fundo cinza médio (o casamento não premia fundo com fundo)."""
    rgb = a[..., :3].astype(np.float32)
    rgb[a[..., 3] == 0] = 110.0
    return rgb


def _gira(t, ang):
    if ang == 0:
        return t
    h, w = t.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
    c, s = abs(M[0, 0]), abs(M[0, 1])
    nw, nh = int(h * s + w * c), int(h * c + w * s)
    M[0, 2] += nw / 2 - w / 2
    M[1, 2] += nh / 2 - h / 2
    return cv2.warpAffine(t, M, (nw, nh), flags=cv2.INTER_NEAREST, borderValue=(0, 0, 0, 0))


def _busca(img, tmpl, escalas, angulos):
    melhor = (-2, 1.0, 0, (0, 0))
    base = _cinza(img)
    for ang in angulos:
        tg = _gira(tmpl, ang)
        for e in escalas:
            w, h = max(4, round(tg.shape[1] * e)), max(4, round(tg.shape[0] * e))
            if h >= base.shape[0] or w >= base.shape[1]:
                continue
            t = cv2.resize(tg, (w, h), interpolation=cv2.INTER_NEAREST)
            r = cv2.matchTemplate(base, _cinza(t), cv2.TM_CCOEFF_NORMED)
            _, v, _, p = cv2.minMaxLoc(r)
            if v > melhor[0]:
                melhor = (v, e, ang, p)
    return melhor


def escala_cabeca(a, tmpl, fator=1):
    """(escala, nota 0-1, (x, y) do canto da cabeça achada). Procura primeiro no alto da figura (a cabeça quase sempre
    está lá) e, se o casamento for fraco (deitado, de ponta-cabeça), na figura inteira."""
    m = mascara(a)
    if not m.any():
        return None
    ys, xs = np.nonzero(m)
    pad = int(tmpl.shape[0] * 0.8)
    x0, x1 = max(0, xs.min() - pad), min(a.shape[1], xs.max() + pad)
    escalas = np.arange(FAIXA[0], FAIXA[1] + 1e-6, 0.01)
    y0 = max(0, ys.min() - pad)
    reg = a[y0:min(a.shape[0], ys.min() + int(tmpl.shape[0] * 2.6)), x0:x1]
    v, e, ang, p = _busca(reg, tmpl, escalas, range(-20, 21, 5))
    if v < 0.6:
        y0 = max(0, ys.min() - pad)
        reg = a[y0:min(a.shape[0], ys.max() + pad), x0:x1]
        v2, e2, ang2, p2 = _busca(reg, tmpl, escalas[::2], range(-90, 91, 15))
        if v2 > v:
            v, e, ang, p = v2, e2, ang2, p2
    return float(e), float(v), (p[0] + x0, p[1] + y0)


def pele(a, end):
    """Máscara de pele: o grupo 'pele' da paleta quando existe; senão a faixa de cor de pele clara (o Diabo)."""
    pal = paleta(end)
    nomes = [n for n, _ in pal if n.startswith("pele") and "contorno" not in n]
    if nomes:
        alvo = np.array([rgb for n, rgb in pal if n in nomes], np.int32)
        px = a[..., :3].astype(np.int32)
        d = np.min(np.abs(px[:, :, None, :] - alvo[None, None]).sum(-1), axis=-1)
        return (a[..., 3] > 0) & (d <= 24)
    if end.lutador != "diabo":
        return None
    hsv = cv2.cvtColor(np.ascontiguousarray(a[..., :3]), cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[..., 0] * 2, hsv[..., 1] / 255, hsv[..., 2] / 255
    return (a[..., 3] > 0) & (h >= 8) & (h <= 28) & (s > 0.2) & (s < 0.6) & (v > 0.6)


def manchas_de_pele(a, end, minimo=None):
    m = pele(a, end)
    if m is None:
        return None
    alt = np.ptp(np.nonzero(a[..., 3])[0]) + 1
    minimo = minimo or max(12, int((alt / 50) ** 2))
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, rot, st, cen = cv2.connectedComponentsWithStats(m, connectivity=8)
    return [(int(st[j, 4]), (int(cen[j, 0]), int(cen[j, 1])), tuple(int(v) for v in st[j, :4]))
            for j in range(1, n) if st[j, 4] >= minimo]


def fora_da_paleta(a, end):
    pal = np.array([rgb for _, rgb in paleta(end)], np.int32)
    px = a[a[..., 3] > 0][:, :3].astype(np.int32)
    if not len(px):
        return 0
    chaves = set(map(tuple, pal.tolist()))
    return int(sum(1 for p in map(tuple, px.tolist()) if p not in chaves))


class Regua:
    """Régua de uma forma de um lutador, montada a partir do parado."""

    def __init__(self, end):
        self.end = end
        par = end.parado()
        q = par.quadros()
        assert q, f"sem parado em {par.pasta}"
        self.parado = abrir(q[0])
        self.tmpl, self.caixa_cabeca = cabeca_do_parado(self.parado)
        self.area = float(mascara(self.parado).sum())
        # o parado respira: a base é a mediana dele, para o limite de 3% valer contra a pose e não contra um quadro
        cabs = [escala_cabeca(abrir(p), self.tmpl) for p in q]
        self.base_cabeca = float(np.median([c[0] for c in cabs if c and c[1] >= 0.55] or [1.0]))
        self.base_corpo = float(np.median([np.sqrt(mascara(abrir(p)).sum() / self.area) for p in q]))
        mp = [manchas_de_pele(abrir(p), end) for p in q]
        self.pele_parado = max((len(x) for x in mp if x is not None), default=None)

    def medir(self, a):
        r = {}
        if not mascara(a).any():
            return {"vazio": True}
        c = escala_cabeca(a, self.tmpl, self.end.fator)
        if c:
            r["cabeca"], r["nota"], r["onde"] = c
            r["cabeca"] /= self.base_cabeca
        r["corpo"] = float(np.sqrt(mascara(a).sum() / self.area)) / self.base_corpo
        mp = manchas_de_pele(a, self.end)
        if mp is not None:
            r["pele"] = len(mp)
            r["manchas"] = mp
        return r

    def avisos(self, r):
        av = []
        if r.get("vazio"):
            return av
        if r.get("nota", 0) >= 0.55:
            d = r["cabeca"] - 1
            if abs(d) > LIMITE:
                av.append(f"cabeça {d:+.0%}")
        else:
            av.append("cabeça não medida")
        if r.get("nota", 0) < 0.55 and abs(r["corpo"] - 1) > LIMITE_CORPO:
            av.append(f"corpo {r['corpo'] - 1:+.0%}")
        if self.pele_parado is not None and r.get("pele", 0) > self.pele_parado + 1:
            av.append(f"membro sobrando? {r['pele']} manchas de pele (parado {self.pele_parado})")
        return av
