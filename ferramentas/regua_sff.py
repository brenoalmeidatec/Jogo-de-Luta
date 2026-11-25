#!/usr/bin/env python3
"""Régua do quadro final (auditoria do Breno, #32, 24/11, item 6): mede o que vai para a tela, o sprite do .sff
na ação do .air, e não só as peças do kit (essas são da regua_corpo.py / regua_pernas.py).

  python3 ferramentas/regua_sff.py                    os 6 lutadores
  python3 ferramentas/regua_sff.py pengaro gutto      só esses
  opções: --relatorio ARQ.md   --acoes 200-999 (padrão: 200-999 e 1000-4999, as de golpe)
          --ver PASTA          grava um recorte com zoom e marca vermelha de cada defeito
          --consertar          tapa as rachaduras de todo sprite das ações 0 a 7999 e regrava o .sff
                               (os gerar_<lutador>.py chamam consertar() no fim)

O que ela procura, ação por ação (só a forma base e o despertado que estão no .air; os efeitos 8000+ ficam fora):

- CONGELADO: quadros seguidos praticamente iguais (menos de 1,5% dos pixels mudam) somando 10 tiques ou mais no meio
  do golpe. Foi o que o Breno viu no chute de longe do Pengaró (240): a perna parada no ar por 3 quadros. O último
  quadro de uma ação (o que segura) não conta.
- RACHADURA: buraco transparente fino dentro do corpo (o corpo fechado por um disco de 7 px), de 6 a 300 px, a 3 px
  ou mais da borda. No jogo, o fundo do cenário aparece por dentro do boneco.
- PEDAÇO SOLTO: mancha de pixels separada do corpo (mais de 40 px, a mais de 6 px de distância) que não está no
  quadro anterior nem no seguinte da mesma ação. É o "pedaço de sprite voando junto" da regra 7.2.1.
- SALTO DE TAMANHO: a altura do boneco muda mais de 30% de um quadro para o seguinte, nos dois sentidos, com o
  quadro de antes e o de depois parecidos entre si (pisca um quadro maior ou menor).

Cada achado sai com lutador, ação, elemento e sprite. Achado conferido no olho e certo vai para ACEITOS, com o
motivo. Sai com código 1 se sobrar achado não aceito.
"""
import io
import re
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
RAIZ = AQUI.parent
import conferir_sff as cs  # noqa: E402

LUTADORES = ("pengaro", "hazaki", "ck", "gutto", "raiclaven", "gbzin")
CONGELA_TIQUES, CONGELA_DIF = 10, 0.015
RACHA_MIN, RACHA_MAX = 6, 300
SOLTO_MIN, SOLTO_DIST = 40, 6
SALTO = 0.30
CONTORNO_LUM = 70   # pixel de contorno do desenho (escuro)
RISCAS_RASTRO = 6   # tantas riscas horizontais no mesmo sprite = rastro em scanline
VOLTA_CHEIA = 0.90  # rachadura: 90% ou mais da volta (5 px) pintada
VOLTA_FUNDO = 0.0   # e nenhum pixel do fundo de fora do corpo nessa volta
MIN_ALTURA = 100    # sprite menor que isso é efeito ou projétil: fora do pedaço solto e do salto
# (lutador, ação, tipo, sprite "g,i" ou "*") -> motivo
ACEITOS = {}
# grupos que o --consertar não toca (o buraco é desenho faltando, não rachadura): lutador -> (de, até, motivo)
NAO_TAPAR = {
    "pengaro": [(589, 604, "despertar (ação 2000): as rachaduras violeta do peito saíram transparentes; precisam ser "
                           "pintadas de violeta com brilho, não tapadas com a pele (vai para a fila de imagens)")],
}


class Sprites:
    def __init__(self, sff):
        pal, nos, _ = cs.ler(sff)
        self.cores = np.array([[pal[4 * k], pal[4 * k + 1], pal[4 * k + 2]] for k in range(256)], np.uint8)
        self.nos = {}
        for n in nos:
            self.nos.setdefault((n["g"], n["i"]), n)
        self.cache = {}

    def rgba(self, g, i):
        """(rgba HxWx4, eixo x, eixo y) ou None."""
        k = (g, i)
        if k in self.cache:
            return self.cache[k]
        n = self.nos.get(k)
        out = None
        if n is not None and n["w"] > 0 and n["h"] > 0:
            if n.get("png"):
                raw = bytes(n["px"])
                p = raw.find(b"\x89PNG")
                if p >= 0:
                    im = np.array(Image.open(io.BytesIO(raw[p:])).convert("RGBA"))
                    out = (im, n["x"], n["y"])
            else:
                idx = np.frombuffer(bytes(n["px"]), np.uint8).reshape(n["h"], n["w"])
                rgb = self.cores[idx]
                a = np.where(idx != 0, 255, 0).astype(np.uint8)
                out = (np.dstack([rgb, a]), n["x"], n["y"])
        self.cache[k] = out
        return out


def acoes(air):
    txt = air.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    out = {}
    for m in re.finditer(r"(?ms)^\[Begin Action (\d+)\]\s*\n(.*?)(?=^\[Begin Action|\Z)", txt):
        els = []
        for e in re.finditer(r"(?m)^\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)", m.group(2)):
            g, i, x, y, t = (int(v) for v in e.groups())
            els.append((g, i, x, y, t))
        out[int(m.group(1))] = els
    return out


def _tela(sp, el, W=700, H=700, ox=350, oy=600):
    """Põe o sprite numa tela comum (eixo do lutador em ox, oy), como o motor desenha."""
    r = sp.rgba(el[0], el[1])
    tela = np.zeros((H, W), bool)
    if r is None:
        return tela
    im, ax, ay = r
    x0, y0 = ox - ax + el[2], oy - ay + el[3]
    h, w = im.shape[:2]
    xs, ys = max(0, x0), max(0, y0)
    xe, ye = min(W, x0 + w), min(H, y0 + h)
    if xe > xs and ye > ys:
        tela[ys:ye, xs:xe] = im[ys - y0:ye - y0, xs - x0:xe - x0, 3] > 0
    return tela


def rachaduras(im):
    """Buraco transparente dentro do corpo SEM contorno em volta: o desenho sempre contorna um vão de verdade (entre os
    dedos, entre o braço e o tronco); a rachadura é o fundo vazando no meio de uma área pintada (a calça, a pele).
    Sprite com rastro em scanline (6 ou mais riscas horizontais de até 4 px) fica de fora: os vãos são de propósito."""
    alfa = im[..., 3] > 0
    if alfa.sum() < 200:
        return np.zeros_like(alfa)
    corpo = cv2.morphologyEx(alfa.astype(np.uint8), cv2.MORPH_CLOSE,
                             cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))).astype(bool)
    miolo = cv2.erode(corpo.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=3).astype(bool)
    lum = im[..., :3].astype(np.int32).mean(2)
    # só o boneco: a maior mancha do sprite (o efeito solto, como a meia-lua do vento do jab, fica de fora)
    nb, rb, sb, _ = cv2.connectedComponentsWithStats(alfa.astype(np.uint8), 8)
    boneco = rb == 1 + int(np.argmax(sb[1:, cv2.CC_STAT_AREA])) if nb > 1 else alfa
    buraco = corpo & ~alfa
    n, rot, st, _ = cv2.connectedComponentsWithStats(buraco.astype(np.uint8), 8)
    out = np.zeros_like(alfa)
    riscas = sum(1 for k in range(1, n) if st[k, 3] <= 4 and st[k, 2] >= 3 * st[k, 3] and st[k, 4] >= RACHA_MIN)
    if riscas >= RISCAS_RASTRO:
        return out  # sprite com rastro em scanline (Diabo Loiro, agarrão do Hazak): os vãos entre as riscas são desenho
    for k in range(1, n):
        a = st[k, cv2.CC_STAT_AREA]
        if not RACHA_MIN <= a <= RACHA_MAX:
            continue
        x, y, w, h = st[k, :4]
        if h <= 2 and w >= 3 * h:
            continue  # risca horizontal fina solta: também é jeito de rastro
        m = rot == k
        if (m & miolo).sum() < max(3, a // 3):
            continue
        anel = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & alfa
        if anel.sum() < 4 or (anel & boneco).sum() < 0.8 * anel.sum():
            continue
        # no meio de uma área cheia: em volta (5 px) quase tudo pintado. Vão entre garras, dedos ou pontas de corda
        # tem fundo por perto e fica.
        volta = cv2.dilate(m.astype(np.uint8), np.ones((11, 11), np.uint8)).astype(bool) & ~corpo
        if volta.sum() > VOLTA_FUNDO * cv2.dilate(m.astype(np.uint8), np.ones((11, 11), np.uint8)).sum():
            continue
        volta = cv2.dilate(m.astype(np.uint8), np.ones((11, 11), np.uint8)).astype(bool) & ~m
        if alfa[volta].mean() < VOLTA_CHEIA:
            continue
        contorno = (lum[anel] < CONTORNO_LUM).mean()
        if contorno < 0.25:
            out |= m
    return out


def soltos(tela):
    n, rot, st, _ = cv2.connectedComponentsWithStats(tela.astype(np.uint8), 8)
    if n <= 2:
        return []
    maior = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    corpo = cv2.dilate((rot == maior).astype(np.uint8), np.ones((3, 3), np.uint8), iterations=SOLTO_DIST)
    out = []
    for k in range(1, n):
        if k == maior or st[k, cv2.CC_STAT_AREA] < SOLTO_MIN:
            continue
        m = rot == k
        if not (m & corpo.astype(bool)).any():
            out.append(m)
    return out


def _altura(tela):
    ys = np.nonzero(tela.any(1))[0]
    return int(ys[-1] - ys[0] + 1) if ys.size else 0


def medir(lutador, faixa=None):
    pasta = RAIZ / "chars" / lutador
    sp = Sprites(pasta / f"{lutador}.sff")
    achados = []
    racha_vista = set()
    for a, els in sorted(acoes(pasta / f"{lutador}.air").items()):
        if faixa:
            if not (faixa[0] <= a <= faixa[1]):
                continue
        elif not (200 <= a <= 4999):
            continue
        els = [e for e in els if e[0] >= 0 and e[0] < 8000]
        if len(els) < 2:
            continue
        telas = [_tela(sp, e) for e in els]
        # congelado
        k = 0
        while k < len(els) - 1:
            j, tiques = k, max(els[k][4], 0)
            while j + 1 < len(els) - 1:
                u = telas[j] | telas[j + 1]
                dif = (telas[j] ^ telas[j + 1]).sum() / max(u.sum(), 1)
                mesmo = (els[j][0], els[j][1]) == (els[j + 1][0], els[j + 1][1]) and els[j][2:4] == els[j + 1][2:4]
                if dif < CONGELA_DIF or mesmo:
                    j += 1
                    tiques += max(els[j][4], 0)
                else:
                    break
            if j > k and tiques >= CONGELA_TIQUES:
                achados.append((lutador, a, "congelado", f"{els[k][0]},{els[k][1]}",
                                f"elementos {k + 1} a {j + 1} quase iguais por {tiques} tiques"))
            k = j + 1
        # rachadura (uma vez por sprite)
        for n, e in enumerate(els):
            s = (e[0], e[1])
            if s in racha_vista:
                continue
            racha_vista.add(s)
            r = sp.rgba(*s)
            if r is None:
                continue
            m = rachaduras(r[0])
            if m.sum() >= 12:
                achados.append((lutador, a, "rachadura", f"{s[0]},{s[1]}",
                                f"{int(m.sum())} px de buraco dentro do corpo (elemento {n + 1})"))
        grandes = [_altura(tl) >= MIN_ALTURA for tl in telas]
        # pedaço solto que só existe num quadro
        for n in range(len(els)):
            if not grandes[n]:
                continue
            viz = [telas[v] for v in (n - 1, n + 1) if 0 <= v < len(els)]
            perto = [cv2.dilate(tv.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) for tv in viz]
            px = [int(m.sum()) for m in soltos(telas[n])
                  if perto and all((m & p).sum() < 0.3 * m.sum() for p in perto)]
            if px:
                achados.append((lutador, a, "pedaco_solto", f"{els[n][0]},{els[n][1]}",
                                f"{len(px)} pedaço(s), {sum(px)} px, soltos do corpo só no elemento {n + 1}"))
        # salto de tamanho num quadro só
        hs = [_altura(t) for t in telas]
        for n in range(1, len(els) - 1):
            a0, a1, a2 = hs[n - 1], hs[n], hs[n + 1]
            if min(a0, a1, a2) < MIN_ALTURA:
                continue
            if abs(a0 - a2) / max(a0, a2) < 0.10 and abs(a1 - a0) / a0 > SALTO:
                achados.append((lutador, a, "salto_tamanho", f"{els[n][0]},{els[n][1]}",
                                f"altura {a0} -> {a1} -> {a2} px (elemento {n + 1})"))
    return achados, sp


def _tapar(im, m):
    """Rachadura tapada com a cor de volta (inpaint do OpenCV, raio 3) e alfa cheio."""
    rgb = np.ascontiguousarray(im[..., :3])
    novo = cv2.inpaint(rgb, m.astype(np.uint8), 3, cv2.INPAINT_TELEA)
    out = im.copy()
    out[m, :3] = novo[m]
    out[m, 3] = 255
    return out


def consertar(lutador, pasta=None):
    """Tapa as rachaduras (buraco sem contorno dentro do corpo) de todo sprite usado nas ações 0 a 7999."""
    import efeitos
    import gerar_pengaro as gp
    pasta = Path(pasta) if pasta else RAIZ / "chars" / lutador
    sff = pasta / f"{lutador}.sff"
    pal, nos, _ = cs.ler(sff)
    usados = {(e[0], e[1]) for a, els in acoes(pasta / f"{lutador}.air").items() if 0 <= a < 8000 for e in els}
    sp = Sprites(sff)
    total, feitos = 0, 0
    trocados = {}
    for n in nos:
        k = (n["g"], n["i"])
        if n["link"] is not None or k not in usados or k in trocados:
            continue
        if any(a <= k[0] <= b for a, b, _ in NAO_TAPAR.get(lutador, ())):
            continue
        r = sp.rgba(*k)
        if r is None:
            continue
        m = rachaduras(r[0])
        if not m.any():
            continue
        if n.get("png"):
            n["px"] = efeitos.blob_png(Image.fromarray(_tapar(r[0], m), "RGBA"))
        else:
            idx = np.frombuffer(bytes(n["px"]), np.uint8).reshape(n["h"], n["w"]).copy()
            h, w = idx.shape
            for y, x in zip(*np.nonzero(m)):
                viz = idx[max(0, y - 3):y + 4, max(0, x - 3):x + 4]
                viz = viz[viz != 0]
                if viz.size:
                    v, c = np.unique(viz, return_counts=True)
                    idx[y, x] = v[np.argmax(c)]
            n["px"] = idx.tobytes()
        trocados[k] = n["px"]
        total += int(m.sum())
        feitos += 1
    if not feitos:
        print(f"{lutador}: nenhuma rachadura")
        return 0
    for n in nos:
        if n["link"] is not None and (nos[n["link"]]["g"], nos[n["link"]]["i"]) in trocados:
            n["px"] = nos[n["link"]]["px"]
    if any(n.get("png") for n in nos):
        cs._gravar_misto(sff, pal, nos, cs.EXTRAS[str(sff)])
    else:
        gp.gravar_sff(sff, pal, [cs._item(n) for n in nos], cs.EXTRAS[str(sff)])
    print(f"{lutador}: {feitos} sprites, {total} px de rachadura tapados")
    return feitos


def aceito(ach):
    l, a, tipo, s, _ = ach
    return ACEITOS.get((l, a, tipo, s)) or ACEITOS.get((l, a, tipo, "*"))


def ver(ach, sp, pasta):
    l, a, tipo, s, _ = ach
    g, i = (int(v) for v in s.split(","))
    r = sp.rgba(g, i)
    if r is None:
        return
    im = r[0].copy()
    base = np.zeros_like(im)
    base[...] = (60, 60, 120, 255)
    a_ = im[..., 3:4] / 255.0
    rgb = (im[..., :3] * a_ + base[..., :3] * (1 - a_)).astype(np.uint8)
    pil = Image.fromarray(rgb)
    if tipo == "rachadura":
        m = rachaduras(im)
        n, _, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
        d = ImageDraw.Draw(pil)
        for k in range(1, n):
            x, y, w, h = st[k, :4]
            d.rectangle((x - 4, y - 4, x + w + 4, y + h + 4), outline=(255, 0, 0), width=2)
    z = max(1, min(4, 600 // max(pil.width, pil.height)))
    pil = pil.resize((pil.width * z, pil.height * z), Image.NEAREST)
    pasta.mkdir(parents=True, exist_ok=True)
    pil.save(pasta / f"{l}_{a}_{tipo}_{g}_{i}.png")


def main():
    args = sys.argv[1:]
    rel = Path(args[args.index("--relatorio") + 1]) if "--relatorio" in args else None
    pver = Path(args[args.index("--ver") + 1]) if "--ver" in args else None
    faixa = None
    if "--acoes" in args:
        f = args[args.index("--acoes") + 1].split("-")
        faixa = (int(f[0]), int(f[1]))
    tira = {"--relatorio", "--ver", "--acoes"}
    nomes = [x for k, x in enumerate(args) if not x.startswith("--") and (k == 0 or args[k - 1] not in tira)]
    if "--consertar" in args:
        for l in nomes or LUTADORES:
            consertar(l)
        return
    linhas, ruins = ["# Régua do quadro final", "", "| lutador | ação | tipo | sprite | o que | aceito? |",
                     "|---|---|---|---|---|---|"], 0
    for l in nomes or LUTADORES:
        achados, sp = medir(l, faixa)
        cont = {}
        for ach in achados:
            ok = aceito(ach)
            ruins += 0 if ok else 1
            cont[ach[2]] = cont.get(ach[2], 0) + (0 if ok else 1)
            linhas.append("| " + " | ".join(str(v) for v in ach) + f" | {ok or 'não'} |")
            if pver and not ok:
                ver(ach, sp, pver)
        print(f"{l}: " + (", ".join(f"{k} {v}" for k, v in sorted(cont.items()) if v) or "ok"))
    if rel:
        rel.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    sys.exit(1 if ruins else 0)


if __name__ == "__main__":
    main()
