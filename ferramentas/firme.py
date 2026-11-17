#!/usr/bin/env python3
"""Boneco de peças "corpo firme" para qualquer lutador (o método que o Alisson aprovou no Pengaró, 16/11).

O tronco, o rosto e a pele saem de um desenho só (o parado do lutador), em cor cheia. Braços e pernas giram presos
nas juntas e seguem as poses que o jogo mostra hoje. Antes de casar as peças, cada quadro de hoje é levado ao tamanho
do parado pela régua da cabeça: o quadro que foi desenhado menor ou maior não muda mais o tamanho do boneco.

Os dados de cada lutador (polígonos, juntas, camadas, variantes e as animações) ficam em ferramentas/kit_<nome>.py.

  python ferramentas/firme.py hazak                 refaz o kit e todas as animações do kit_hazak.ANIMS
  python ferramentas/firme.py hazak soco parado     só essas
  python ferramentas/firme.py hazak --so-pose ...   usa o kit que já existe
  python ferramentas/firme.py hazak --video         e grava os vídeos antes e depois em docs/boneco-pecas/<nome>/

Saída: sprites/<lutador>/pecas/ (kit), quadros_pecas_hd/<anim>/ (3x) e quadros_pecas/<anim>/ (1x) com tempos.json,
e o relatório do robô de defeitos em docs/boneco-pecas/<nome>/robo_defeitos.md. Nada vai para o .sff.
"""
import importlib
import json
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI / "pixel"))
import boneco_ajuste as b  # noqa: E402
import reguas  # noqa: E402
import vida_pecas as vida  # noqa: E402
from boneco_pecas import scale2x  # noqa: E402

RAIZ = AQUI.parent
EIXO = (540, 660)
K = None  # módulo kit_<nome>


# ------------------------------------------------------------------ utilidades
def escalar(rgba, fator, pivo):
    """Muda o tamanho de um recorte RGBA sem misturar cor (Scale2x três vezes e amostragem), em volta de `pivo`.
    Devolve (recorte, pivô novo)."""
    if abs(fator - 1) < 0.005:
        return rgba.copy(), pivo
    h0, w0 = rgba.shape[:2]
    chave = rgba.reshape(-1, 4).view(np.uint32).reshape(h0, w0)
    cores, idx = np.unique(chave, return_inverse=True)
    big = idx.reshape(h0, w0)
    for _ in range(3):
        big = scale2x(big)
    w, h = int(round(w0 * fator)), int(round(h0 * fator))
    xs = np.clip(((np.arange(w) + 0.5) / fator * 8).astype(int), 0, w0 * 8 - 1)
    ys = np.clip(((np.arange(h) + 0.5) / fator * 8).astype(int), 0, h0 * 8 - 1)
    out = cores[big[ys[:, None], xs[None, :]]].view(np.uint8).reshape(h, w, 4).copy()
    return out, (pivo[0] * fator, pivo[1] * fator)


def na_tela(rgba, fator, pivo=EIXO):
    """O quadro inteiro (tela 3x) com o tamanho multiplicado por `fator` em volta dos pés."""
    if abs(fator - 1) < 0.005:
        return rgba.copy()
    ys, xs = np.nonzero(rgba[..., 3] > 0)
    x0, y0 = xs.min(), ys.min()
    r, piv = escalar(rgba[y0:ys.max() + 1, x0:xs.max() + 1], fator, (pivo[0] - x0, pivo[1] - y0))
    tela = np.zeros_like(rgba)
    b.colar(tela, r, int(round(pivo[0] - piv[0])), int(round(pivo[1] - piv[1])))
    return tela


def abrir(q):
    return np.array(Image.open(b.HD / f"{q}.png").convert("RGBA"))


_CAB = None
_ESC = {}


def escala(q):
    """Tamanho do quadro `q` contra o parado, medido pela cabeça (1.0 = igual)."""
    global _CAB
    if getattr(K, "ESCALA_FIXA", False) or getattr(K, "SEM_REGUA", False):  # desenhos já no tamanho do parado
        return 1.0
    if q not in _ESC:
        if _CAB is None:
            _CAB, _ = reguas.cabeca_do_parado(abrir(K.REF))
            _ESC["_ref"] = reguas.escala_cabeca(abrir(K.REF), _CAB)[0]
        e, nota, _ = reguas.escala_cabeca(abrir(q), _CAB)
        _ESC[q] = e / _ESC["_ref"] if nota >= 0.6 else 1.0
    return _ESC[q]


def normal(q):
    """O quadro de hoje levado ao tamanho do parado (só para achar a pose)."""
    return na_tela(abrir(q), 1 / escala(q))


# ------------------------------------------------------------------ configuração
def configurar(nome):
    global K
    K = importlib.import_module(f"kit_{nome}")
    b.SPR = RAIZ / "sprites" / K.LUTADOR
    b.HD = b.SPR / "quadros_arcade_hd"
    b.PECAS = b.SPR / "pecas"
    b.REF = K.REF
    b.OSSOS = K.OSSOS
    b.CAMADAS = K.CAMADAS
    b.VARIANTES = K.VARIANTES
    vars_bf = [None]
    vars_bt = [None]
    b.BUSCA = {
        "quadril": (range(-8, 9, 2), 30, [None]),
        "tronco": (range(-10, 11, 2), 3, [None]),
        "cabeca": (range(-10, 11, 2), 3, [None]),
        "braco_tras": (range(-110, 41, 3), 2, vars_bt),
        "antebraco_tras": (range(-60, 91, 3), 2, [None]),
        "braco_frente": (range(-50, 51, 3), 4, vars_bf),
        "coxa_tras": (range(-30, 31, 2), 2, [None]),
        "canela_tras": (range(-30, 31, 2), 2, [None]),
        "coxa_frente": (range(-30, 31, 2), 2, [None]),
        "canela_frente": (range(-30, 31, 2), 2, [None]),
    }
    b.BUSCA.update(getattr(K, "BUSCA", {}))  # faixa de ângulos própria do lutador (ex.: garras por cima da cabeça)
    return K


# ------------------------------------------------------------------ kit
def montar_kit():
    if b.PECAS.exists():
        shutil.rmtree(b.PECAS)
    b.PECAS.mkdir(parents=True)
    ref = abrir(K.REF)
    alfa = ref[..., 3] > 0
    yy, xx = np.mgrid[:b.TELA[1], :b.TELA[0]]
    baixo = yy >= K.CINTURA
    m_bt = b.mascara(K.BRACO_TRAS) & alfa
    m_bf = b.mascara(K.BRACO_FRENTE) & alfa & ~m_bt
    bracos = m_bt | m_bf
    m_cab = b.mascara(K.CABECA) & alfa & ~bracos
    # só o marrom do nó fica no quadril; a calça atrás dele é das pernas
    no = (b.mascara(K.NO_DA_FAIXA) & faixa_marrom(ref)) if hasattr(K, "NO_DA_FAIXA") else np.zeros_like(alfa)
    no = cv2.dilate(no.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & b.mascara(K.NO_DA_FAIXA)
    # rabo (demônio): peça própria presa no quadril, por cima das pernas
    m_cauda = np.zeros_like(alfa)
    cauda_falta = np.zeros_like(alfa)
    if hasattr(K, "CAUDA_LINHA"):
        faixa = np.zeros(alfa.shape, np.uint8)
        cv2.polylines(faixa, [np.int32(K.CAUDA_LINHA)], False, 1, K.CAUDA_LARG)
        faixa = (faixa > 0) | b.mascara(K.CAUDA_PONTA)
        R, G, B_ = (ref[..., i].astype(int) for i in range(3))
        cor = (R > B_ + 6) & (G < R * 0.66)
        m_cauda = faixa & alfa & cor & ~bracos
        m_cauda = limpar_ilhas(m_cauda, 40)
        # trecho da linha sem rabo à vista (escondido): completa com um traço da cor do rabo
        miolo = np.zeros(alfa.shape, np.uint8)
        cv2.polylines(miolo, [np.int32(K.CAUDA_LINHA)], False, 1, max(5, K.CAUDA_LARG // 2))
        cauda_falta = (miolo > 0) & ~m_cauda
    no |= m_cauda
    pt = b.mascara(K.PERNA_TRAS) & alfa & ~bracos & baixo & ~no
    pf = b.mascara(K.PERNA_FRENTE) & alfa & ~bracos & baixo & ~pt & ~no
    jt, jf = K.JOELHO_TRAS[1], K.JOELHO_FRENTE[1]
    m_ant = np.zeros_like(m_bt)
    if hasattr(K, "ANTEBRACO_LINHA"):
        (x1, y1), (x2, y2) = K.ANTEBRACO_LINHA
        abaixo = (yy - y1) * (x2 - x1) - (xx - x1) * (y2 - y1) > 0
        m_ant = m_bt & (abaixo | (xx >= K.PUNHO_X))
    partes = {
        "cabeca": m_cab,
        "braco_tras": m_bt & ~m_ant,
        "braco_frente": m_bf,
        **({"antebraco_tras": m_ant} if m_ant.any() else {}),
        "tronco": (yy < K.CINTURA + getattr(K, "TRONCO_SOBRA", 0)) & alfa & ~m_cab & ~bracos & ~m_cauda,
        "quadril": baixo & alfa & ~pt & ~pf & ~bracos & ~m_cauda,
        **({"cauda": m_cauda} if m_cauda.any() else {}),
        "coxa_tras": pt & (yy < jt),
        "canela_tras": pt & (yy >= jt - 12),  # 12 linhas por baixo da coxa: tapa a fresta quando o joelho dobra
        "coxa_frente": pf & (yy < jf),
        "canela_frente": pf & (yy >= jf - 12),
        "perna_tras": pt,
        "perna_frente": pf,
    }
    imgs = {k: np.where(m[..., None], ref, 0).astype(np.uint8) for k, m in partes.items()}
    if "cauda" in imgs and cauda_falta.any():
        c = imgs["cauda"]
        cores = ref[m_cauda][:, :3].astype(int)
        escuro = np.percentile(cores, 25, axis=0).astype(np.uint8)
        c[cauda_falta, :3] = escuro
        c[cauda_falta, 3] = 255
        borda = cv2.dilate(cauda_falta.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~cauda_falta \
            & (c[..., 3] == 0)
        c[borda, :3] = (np.percentile(cores, 5, axis=0)).astype(np.uint8)
        c[borda, 3] = 255
    # peito e lado do tronco que o braço de trás esconde
    esc = b.mascara(K.TRONCO_ESCONDIDO) & m_bt & ~baixo
    imgs["tronco"] = b.tapar(np.where((partes["tronco"] | esc)[..., None], ref, 0).astype(np.uint8), esc,
                             partes["tronco"])
    pintado = esc & ~partes["tronco"]
    if hasattr(K, "QUADRIL_ESCONDIDO"):  # barra do paletó e quadril que a mão de trás esconde
        escq = b.mascara(K.QUADRIL_ESCONDIDO) & m_bt & baixo
        imgs["quadril"] = b.tapar(np.where((partes["quadril"] | escq)[..., None], ref, 0).astype(np.uint8), escq,
                                  partes["quadril"])
    # cada peça fica só com o pedaço ligado a ela (sem lasca de outra peça que caiu dentro do polígono)
    imgs = {k: so_o_grosso(v) for k, v in imgs.items()}
    kit = {"ref": f"quadros_arcade_hd/{K.REF}.png", "pecas": {}}

    def guardar(nome, img, junta, mae, fonte_img, fonte):
        a = img[..., 3] > 0
        ys, xs = np.nonzero(a)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        Image.fromarray(img[y0:y1, x0:x1]).save(b.PECAS / f"{nome}.png")
        disco = np.zeros(b.TELA[::-1], np.uint8)
        cv2.circle(disco, (int(junta[0]), int(junta[1])), b.SOBRA, 1, -1)
        sob = np.where((disco.astype(bool) & (fonte_img[..., 3] > 0))[..., None], fonte_img, 0).astype(np.uint8)
        S = b.SOBRA
        Image.fromarray(sob[y0 - S:y1 + S, x0 - S:x1 + S]).save(b.PECAS / f"{nome}_sobra.png")
        kit["pecas"][nome] = {"arquivo": f"{nome}.png", "origem": [int(x0), int(y0)], "junta": list(junta),
                              "mae": mae, "fonte": fonte, "sobra": f"{nome}_sobra.png",
                              "origem_sobra": [int(x0 - S), int(y0 - S)]}

    for nome, img in imgs.items():
        junta, mae, _ = K.OSSOS[nome.replace("perna", "coxa")]
        guardar(nome, img, junta, mae, ref, K.REF)
    # onde o peito foi pintado por baixo do braço (o robô reprova se isso aparecer)
    o = kit["pecas"]["tronco"]["origem"]
    t_h, t_w = np.asarray(Image.open(b.PECAS / "tronco.png")).shape[:2]
    pm = np.zeros((t_h, t_w, 4), np.uint8)
    pm[pintado[o[1]:o[1] + t_h, o[0]:o[0] + t_w]] = 255
    Image.fromarray(pm).save(b.PECAS / "tronco_pintado.png")
    (b.PECAS / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")
    global _MOLDE
    _MOLDE = None
    base = b.ler_kit()
    if hasattr(K, "PEITO_DOADOR"):
        peito_de_outro_desenho(base, pintado)
    for nome, fonte in getattr(K, "PERNAS_VAR", {}).items():
        # metade de baixo inteira (faixa, quadril e pernas) de um desenho bom, levada ao corpo do kit
        dx, dy, giro = corpo(base, normal(fonte))
        d = normal(fonte)
        d = cv2.warpAffine(d, np.float32([[1, 0, -dx], [0, 1, -dy]]), b.TELA, flags=cv2.INTER_NEAREST)
        yy2 = np.mgrid[:b.TELA[1], :b.TELA[0]][0]
        # abaixo da faixa, e acima dela só o que fica fora do tronco, da cabeça e dos braços do kit (os joelhos
        # do agachado sobem ao lado do corpo); a peça vai atrás do tronco
        cima = np.zeros(yy2.shape, bool)
        for nome_p in ("tronco", "cabeca"):
            if nome_p in base["pecas"]:
                pp = base["pecas"][nome_p]
                hh, ww = pp["img"].shape[:2]
                ox, oy = pp["origem"]
                cima[oy:oy + hh, ox:ox + ww] |= pp["img"][..., 3] > 0
        cima = cv2.dilate(cima.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        m = (d[..., 3] > 0) & ((yy2 >= K.CINTURA) | (~cima & (yy2 >= K.CINTURA - 90)))
        img = so_o_grosso(np.where(m[..., None], d, 0).astype(np.uint8))
        junta = K.OSSOS["quadril"][0]
        guardar(f"pernas_{nome}", img, junta, None, d, fonte)
        kit["pecas"][f"pernas_{nome}"]["corpo"] = [int(dx), int(dy)]
        print(f"pernas_{nome}: de {fonte} (corpo {dx:+d},{dy:+d})")
    (b.PECAS / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")
    base = b.ler_kit()
    for slot, vs in K.VARIANTES.items():
        junta, mae, _ = K.OSSOS[slot]
        for var, (fonte, poli, _junta_fonte, *fixa) in vs.items():
            # a junta no desenho de onde a peça sai é a junta do kit levada pelo corpo daquele desenho (o corpo
            # firme casado nele): a peça fica presa no mesmo ponto do corpo em que ela sai no desenho de hoje
            dx, dy, giro = corpo(base, normal(fonte))
            jt = K.OSSOS["tronco"][0]
            jk = b.girar(junta, jt, giro) if mae == "tronco" else junta
            e0 = escala(fonte)
            junta_fonte = (EIXO[0] + (jk[0] + dx - EIXO[0]) * e0, EIXO[1] + (jk[1] + dy - EIXO[1]) * e0)
            if fixa:  # junta marcada à mão no desenho (o membro sai de outro ponto do corpo naquele desenho)
                junta_fonte = _junta_fonte
            f = abrir(fonte)
            m = b.mascara(poli) & (f[..., 3] > 0)
            if slot.startswith("coxa") and getattr(K, "TIRA_FAIXA", True):  # faixa do quimono (Hazak)
                m &= ~faixa_marrom(f)
                m = limpar_ilhas(m)
            rec = so_o_grosso(np.where(m[..., None], f, 0).astype(np.uint8))
            # leva ao tamanho do parado em volta da junta, e a junta para a junta do kit
            e = escala(fonte)
            r, piv = escalar(rec, 1 / e, junta_fonte)
            img = np.zeros_like(f)
            b.colar(img, r, int(round(junta[0] - piv[0])), int(round(junta[1] - piv[1])))
            fi, pv = escalar(f, 1 / e, junta_fonte)
            fonte_img = np.zeros_like(f)
            b.colar(fonte_img, fi, int(round(junta[0] - pv[0])), int(round(junta[1] - pv[1])))
            guardar(f"{slot}_{var}", img, junta, mae, fonte_img, fonte)
            print(f"{slot}_{var}: de {fonte} (escala {e:.3f})")
    (b.PECAS / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")


def peito_de_outro_desenho(base, pintado):
    """O peito escondido pelo braço vem de um desenho em que ele aparece (K.PEITO_DOADOR), levado ao corpo do kit,
    em vez de ficar só pintado por cima. O que sobra (fora do polígono do doador) continua pintado."""
    fonte, poli = K.PEITO_DOADOR
    dx, dy, giro = corpo(base, normal(fonte))
    d = normal(fonte)
    if giro:
        jt = K.OSSOS["tronco"][0]
        r, piv = b.rotsprite(d, -giro, jt)
        d2 = np.zeros_like(d)
        b.colar(d2, r, int(round(jt[0] - piv[0])), int(round(jt[1] - piv[1])))
        d = d2
    M = np.float32([[1, 0, -dx], [0, 1, -dy]])
    d = cv2.warpAffine(d, M, b.TELA, flags=cv2.INTER_NEAREST)
    usar = pintado & b.mascara(poli) & (d[..., 3] > 0)
    p = base["pecas"]["tronco"]
    ox, oy = p["origem"]
    img = np.asarray(Image.open(b.PECAS / p["arquivo"]).convert("RGBA")).copy()
    h, w = img.shape[:2]
    u = usar[oy:oy + h, ox:ox + w]
    img[u] = d[oy:oy + h, ox:ox + w][u]
    # o resto (beira do lado, embaixo do cotovelo) vira sombra do quimono: o tom mais escuro do pano do tronco,
    # como um desenhista preencheria o lado do corpo na sombra do braço (sem borrão de inpaint)
    resto = pintado[oy:oy + h, ox:ox + w] & ~u
    rgb = img[..., :3].astype(int)
    hsv = cv2.cvtColor(np.ascontiguousarray(img[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    pano = (img[..., 3] > 0) & ~resto & (hsv[..., 0] >= 105) & (hsv[..., 0] <= 140) & (hsv[..., 1] > 60)
    if pano.any() and resto.any():
        lum = rgb[pano].sum(-1)
        sombra = rgb[pano][(lum >= np.percentile(lum, 30)) & (lum <= np.percentile(lum, 50))]
        img[resto, :3] = np.median(sombra, 0).astype(np.uint8)
        # contorno escuro na beira nova (onde antes encostava o braço), como o resto do desenho
        al = (img[..., 3] > 0).astype(np.uint8)
        borda = (al > 0) & (cv2.erode(al, np.ones((3, 3), np.uint8)) == 0) & \
            (cv2.dilate(resto.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)
        img[borda, :3] = (40, 20, 40)
    Image.fromarray(img).save(b.PECAS / p["arquivo"])
    pm = np.asarray(Image.open(b.PECAS / "tronco_pintado.png")).copy()
    pm[u | resto] = 0
    Image.fromarray(pm).save(b.PECAS / "tronco_pintado.png")
    base["pecas"]["tronco"]["img"] = img
    print(f"peito: {int(usar.sum())} px do {fonte} (corpo {dx:+d},{dy:+d}, giro {giro})")


def faixa_marrom(a):
    hsv = cv2.cvtColor(np.ascontiguousarray(a[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    rgb = a[..., :3].astype(int)
    # marrom da faixa: matiz laranja/vermelho, pouco claro e não saturado como o friso laranja
    return (a[..., 3] > 0) & ((hsv[..., 0] <= 20) | (hsv[..., 0] >= 170)) & (hsv[..., 2] < 120) & \
        (rgb[..., 0] > rgb[..., 2])


def so_o_grosso(img):
    """Recorte só com o maior pedaço ligado (e os que tiverem pelo menos 1/4 dele)."""
    al = (img[..., 3] > 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(al, connectivity=8)
    if n <= 2:
        return img
    maior = st[1:, 4].max()
    fica = [i for i in range(1, n) if st[i, 4] * 4 >= maior]
    out = img.copy()
    out[~np.isin(lab, fica)] = 0
    return out


def limpar_ilhas(m, minimo=30):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    out = np.zeros_like(m)
    for i in range(1, n):
        if st[i, 4] >= minimo:
            out |= lab == i
    return out


def ler_kit():
    kit = separar_pes(b.ler_kit())
    kit["pecas"]["tronco"]["pintado"] = np.asarray(Image.open(b.PECAS / "tronco_pintado.png").convert("RGBA"))
    return kit


def separar_pes(kit):
    """Pé de cada canela vira peça à parte, presa no tornozelo; fica reto no chão quando a perna está plantada."""
    kit["pes"] = {}
    for slot, (tx, ty) in K.TORNOZELO.items():
        p = kit["pecas"][slot]
        img = p["img"].copy()
        ox, oy = p["origem"]
        corte = ty - oy
        pe = np.zeros_like(img)
        pe[corte:] = img[corte:]
        p["img_inteira"] = p["img"]
        img[corte + 4:] = 0  # 4 linhas de sobra: a canela cobre o começo do pé
        p["img"] = img
        ys = np.nonzero(pe[..., 3].any(1))[0]
        kit["pes"][slot] = {"img": pe, "origem": (ox, oy), "tornozelo": (tx, ty), "fundo": int(ys.max())}
    return kit


# ------------------------------------------------------------------ pose
def pes_no_chao(a):
    """Centro x de cada pé no chão (faixa de baixo da figura), da esquerda para a direita."""
    faixa = a[EIXO[1] - 22:EIXO[1] + 2, :, 3].any(0)
    xs = np.nonzero(faixa)[0]
    if not len(xs):
        return []
    runs = [r for r in np.split(xs, np.nonzero(np.diff(xs) > 3)[0] + 1) if len(r) > 10]
    if len(runs) == 1 and len(runs[0]) > LARGURA_PE * 1.6:  # pés encostados: os dois cabem no mesmo trecho
        r = runs[0]
        return [r.min() + LARGURA_PE / 2, r.max() - LARGURA_PE / 2]
    return [(r.min() + r.max()) / 2 for r in runs]


LARGURA_PE = 52  # largura de um pé no chão (3x)


def cinza(a):
    rgb = a[..., :3].astype(np.float32)
    rgb[a[..., 3] == 0] = 110.0
    return rgb


_MOLDE = None


def molde(kit):
    """Cabeça e tronco do parado, só os pixels que são do desenho (sem o peito pintado por baixo do braço)."""
    global _MOLDE
    if _MOLDE is None:
        ref = abrir(K.REF)
        m = np.zeros(ref.shape[:2], bool)
        for nome in ("cabeca", "tronco"):
            p = kit["pecas"][nome]
            t = p["img"]
            x0, y0 = p["origem"]
            h, w = t.shape[:2]
            igual = (t[..., 3] > 0) & (np.abs(t[..., :3].astype(int) - ref[y0:y0 + h, x0:x0 + w, :3]).sum(-1) == 0)
            m[y0:y0 + h, x0:x0 + w] |= igual
        ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        _MOLDE = (ref[y0:y1, x0:x1].copy(), m[y0:y1, x0:x1].astype(np.float32), (int(x0), int(y0)))
    return _MOLDE


GIRO_TRONCO = range(-9, 10, 3)


def corpo(kit, alvo, folga=60):
    """(dx, dy, giro) do corpo do kit no quadro. O desenho não muda (corpo firme): o tronco só anda e inclina em volta
    da cintura (golpe que joga o corpo para trás ou para a frente). Casa cabeça, ombros e peito do desenho."""
    t, m, (x0, y0) = molde(kit)
    jx, jy = K.OSSOS["tronco"][0]
    rgba = t.copy()
    rgba[..., 3] = (m > 0) * 255
    melhor = None
    for ang in GIRO_TRONCO:
        r, piv = b.rotsprite(rgba, ang, (jx - x0, jy - y0))
        rx0, ry0 = int(round(jx - piv[0])), int(round(jy - piv[1]))
        h, w = r.shape[:2]
        X0, Y0 = max(0, rx0 - folga), max(0, ry0 - folga)
        reg = alvo[Y0:ry0 + h + folga + 110, X0:rx0 + w + folga]  # agachado: o corpo desce até ~170 px
        mm = (r[..., 3] > 0).astype(np.float32)
        res = cv2.matchTemplate(cinza(reg), cinza(r), cv2.TM_SQDIFF, mask=np.repeat(mm[..., None], 3, -1))
        v, _, p_min, _ = cv2.minMaxLoc(res)
        v = v / mm.sum() + 40 * abs(ang)  # prefere o tronco reto quando empata
        if melhor is None or v < melhor[0]:
            melhor = (v, p_min[0] + X0 - rx0, p_min[1] + Y0 - ry0, ang)
    return melhor[1], melhor[2], melhor[3]


def ik(quadril, tornozelo, joelho_ref, quadril_ref, tornozelo_ref):
    q, t = np.array(quadril, float), np.array(tornozelo, float)
    qr, jr, tr = (np.array(v, float) for v in (quadril_ref, joelho_ref, tornozelo_ref))
    l1, l2 = np.linalg.norm(jr - qr), np.linalg.norm(tr - jr)
    d = t - q
    dist = min(np.linalg.norm(d), l1 + l2 - 0.5)
    u = d / np.linalg.norm(d)
    a = (l1 ** 2 - l2 ** 2 + dist ** 2) / (2 * dist)
    h = np.sqrt(max(l1 ** 2 - a ** 2, 0))
    n = np.array([-u[1], u[0]])
    cruz = lambda a_, b_: a_[0] * b_[1] - a_[1] * b_[0]
    lado = np.sign(cruz(tr - qr, jr - qr)) or 1
    j = q + u * a + n * h
    if np.sign(cruz(t - q, j - q)) != lado:
        j = q + u * a - n * h
    ang = lambda v: np.degrees(np.arctan2(v[1], v[0]))
    coxa = ang(j - q) - ang(jr - qr)
    canela = ang(t - j) - ang(tr - jr) - coxa
    return round(float(coxa), 1), round(float(canela), 1)


_PES_REF = None


_PASSO = {}


def pernas_no_chao(pose, alvo, quais=("tras", "frente")):
    """Pernas plantadas por IK: o tornozelo vai para cima do pé do quadro de hoje."""
    global _PES_REF
    if _PES_REF is None:
        _PES_REF = pes_no_chao(abrir(K.REF))
    agora = pes_no_chao(alvo)
    if "_pes" in pose:  # pés postos à mão: deslocamento (trás, frente) a partir dos pés do parado
        pt, pf_ = pose.pop("_pes")["d"]
        agora = [_PES_REF[0] + pt, _PES_REF[-1] + pf_]

    def alvo_tornozelo(lado):
        i = 0 if lado == "tras" else -1
        tr = K.TORNOZELO[f"canela_{lado}"]
        dx = _PASSO.get(lado, 0)
        if agora and (len(agora) > 1 or len(quais) == 1):
            dx += agora[i] - _PES_REF[i]
        return (tr[0] + dx, tr[1])

    # perna plantada não estica além do que ela mede: se o quadril subiu demais, o corpo desce até o pé alcançar
    descer = 0.0
    w = b.mundo(pose)
    for lado in quais:
        coxa, canela = f"coxa_{lado}", f"canela_{lado}"
        qr, jr = K.OSSOS[coxa][0], K.OSSOS[canela][0]
        tr = K.TORNOZELO[canela]
        L = np.linalg.norm(np.subtract(jr, qr)) + np.linalg.norm(np.subtract(tr, jr)) - 1.5
        q = w[coxa][0]
        t = alvo_tornozelo(lado)
        ddx = t[0] - q[0]
        if abs(ddx) < L:
            alto = t[1] - np.sqrt(L * L - ddx * ddx)  # quadril mais alto possível
            descer = max(descer, alto - q[1])
    if descer > 0:
        pose["quadril"] = dict(pose["quadril"], dy=pose["quadril"].get("dy", 0) + int(np.ceil(descer)))
    w = b.mundo(pose)
    for lado in quais:
        i = 0 if lado == "tras" else -1
        coxa, canela = f"coxa_{lado}", f"canela_{lado}"
        qr, jr = K.OSSOS[coxa][0], K.OSSOS[canela][0]
        tr = K.TORNOZELO[canela]
        dx = _PASSO.get(lado, 0)
        if agora and (len(agora) > 1 or len(quais) == 1):
            dx += agora[i] - _PES_REF[i]
        # o pé não vai além do que a perna alcança (perna não estica)
        L = np.linalg.norm(np.subtract(jr, qr)) + np.linalg.norm(np.subtract(tr, jr)) - 2
        hq = w[coxa][0]
        vy = tr[1] - hq[1]
        alcance = np.sqrt(max(1.0, L * L - vy * vy))
        tx = min(max(tr[0] + dx, hq[0] - alcance), hq[0] + alcance)
        c1, c2 = ik(hq, (tx, tr[1]), jr, qr, tr)
        pose[coxa] = {"ang": c1}
        pose[canela] = {"ang": c2}
    return pose


def iou(a, b_):
    x, y = a[..., 3] > 0, b_[..., 3] > 0
    return float((x & y).sum()) / max(1, int((x | y).sum()))


def pose_de(kit, q):
    """Pose do kit para o quadro `q`, ou {"_especial"} quando o corpo do kit não serve (de costas, de lado, deitado):
    aí fica o desenho de hoje, no tamanho do parado."""
    if q in getattr(K, "ESPECIAIS", ()):
        return {"_especial": {"var": q}}
    pose = _pose_kit(kit, q)
    folha = q.split("/")[0]
    if folha in getattr(K, "AUTO_ESPECIAL", ()) and q not in getattr(K, "FIRMES", ()) and \
            q not in getattr(K, "POSES", {}) and iou(desenhar(kit, pose), normal(q)) < LIMIAR_ESPECIAL:
        return {"_especial": {"var": q}}
    return pose


LIMIAR_ESPECIAL = 0.65
_ESP = {}


def especial(q):
    """Desenho de hoje (já na paleta travada) levado ao tamanho do parado, sem migalhas."""
    if q not in _ESP:
        # sem reescala: a régua da cabeça erra de lado e de costas (aumentaria o boneco); os desenhos de hoje já têm o
        # tamanho do parado (conferido no lote 4)
        lado = b.SPR / "pecas_lado" / f"{q}.png"  # kit de lado/costas (hazak_lado.py) vence o desenho de hoje
        a = sem_migalha(np.array(Image.open(lado).convert("RGBA")) if lado.exists() else abrir(q))
        # furinho de 1 a 40 px é erro do desenho; vão maior (entre o braço e o corpo) é desenhado de propósito
        fundo = (a[..., 3] == 0).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(fundo, connectivity=4)
        m = np.isin(lab, [i for i in range(1, n) if st[i, 4] <= 40]) & buracos(a)
        if m.any():
            rgb = cv2.inpaint(np.ascontiguousarray(a[..., :3]), m.astype(np.uint8), 3, cv2.INPAINT_TELEA)
            a[m, :3], a[m, 3] = rgb[m], 255
        _ESP[q] = a
    return _ESP[q].copy()


def _pose_kit(kit, q):
    alvo = normal(q)
    dx, dy, giro = corpo(kit, alvo)
    pose = {"quadril": {"ang": 0, "dx": dx, "dy": dy}, "tronco": {"ang": giro}}
    if q in K.EXPRESSOES:
        pose["cabeca"] = {"ang": 0, "var": K.EXPRESSOES[q]}
    vb = getattr(K, "BRACO_VAR", {}).get(q, [])
    b.BUSCA["braco_frente"] = (b.BUSCA["braco_frente"][0], 4, [None] + vb)
    ordem = ["braco_tras"] + (["antebraco_tras"] if "antebraco_tras" in K.OSSOS else []) + ["braco_frente"]
    pose = b.encaixar(kit, alvo, pose, ordem=ordem)
    # a cabeça fica de pé quando o tronco inclina (o olhar continua no oponente)
    if giro:
        pose["cabeca"] = dict(pose.get("cabeca", {}), ang=-round(giro * 0.7))
    pv = getattr(K, "PERNAS_DE", {}).get(q)
    if pv:  # a metade de baixo é rígida e fica no chão: o quadril fica onde ela foi recortada e o tronco respira
        pose["_pernas"] = {"var": pv}
        cx, cy = kit["pecas"][f"pernas_{pv}"]["corpo"]
        pose["quadril"] = {"ang": 0, "dx": cx, "dy": cy}
        lim = lambda v: max(-4, min(4, v))  # o tronco só balança um pouco em cima das pernas (sem abrir vão)
        pose["tronco"] = dict(pose.get("tronco", {}), dx=lim(dx - cx), dy=lim(dy - cy))
    mao = getattr(K, "POSES", {}).get(q, {})
    for slot, v in mao.items():
        if slot == "quadril" and v.get("so_dy"):
            pose["quadril"] = dict(pose["quadril"], dy=v["dy"])
        elif slot == "quadril" and v.get("abs"):  # corpo inteiro posto à mão (desenho de hoje confuso demais)
            pose["quadril"] = {"ang": 0, "dx": v.get("dx", 0), "dy": v.get("dy", 0)}
            pose["_pes"] = {"d": tuple(v.get("pes", (0, 0)))}
        elif slot != "coxa_frente" and slot != "_ar":
            pose[slot] = dict(v)
    if "tronco" in mao and "cabeca" not in mao:
        pose["cabeca"] = dict(pose.get("cabeca", {}), ang=-round(mao["tronco"]["ang"] * 0.7))
    # passo do golpe (regra do corpo inteiro): o quadril vai à frente, o tronco inclina e o pé da frente avança
    global _PASSO
    _PASSO = getattr(K, "PASSO", {}).get(q, {})
    if _PASSO:
        pose["quadril"] = dict(pose["quadril"], dx=pose["quadril"].get("dx", 0) + _PASSO.get("quadril", 0))
        ta = pose.get("tronco", {}).get("ang", 0) + _PASSO.get("tronco", 0)
        pose["tronco"] = dict(pose.get("tronco", {}), ang=ta)
        pose["cabeca"] = dict(pose.get("cabeca", {}), ang=-round(ta * 0.7))
    no_ar = getattr(K, "PERNA_NO_AR", {}).get(q)
    if "_ar" in mao:  # no ar: as duas pernas nos ângulos dados à mão, sem pé plantado
        pose.pop("_pes", None)
        pose["_ar"] = {"sim": 1}
        for slot in ("coxa_tras", "canela_tras", "coxa_frente", "canela_frente"):
            pose[slot] = dict(mao.get(slot, {"ang": 0}))
        return pose
    if pv:
        pass  # metade de baixo vem inteira do desenho dito no kit
    elif no_ar is None:
        pose = pernas_no_chao(pose, alvo)
    else:  # perna da frente no ar: a de trás fica plantada e a da frente é casada com o desenho dito no kit
        pose = pernas_no_chao(pose, alvo, quais=("tras",))
        vs = [None] if no_ar == "livre" else [no_ar]
        b.BUSCA["coxa_frente"] = (range(-60, 61, 2), 3, vs)
        b.ANGULOS_VARIANTE = range(-100, 51, 2)
        b.FOLGA_VARIANTE = {"coxa_frente": 4}
        pose = b.encaixar(kit, alvo, pose, ordem=["coxa_frente"])
        if "coxa_frente" in mao:
            pose["coxa_frente"] = dict(mao["coxa_frente"])
        if not pose["coxa_frente"].get("var"):
            pose = b.encaixar(kit, alvo, pose, ordem=["canela_frente"])
            pose["_chute_livre"] = {"sim": 1}
        b.BUSCA["coxa_frente"] = (range(-30, 31, 2), 2, [None])
    for slot in ("coxa_frente", "canela_frente"):  # perna dada à mão vence o encaixe
        if slot in mao and no_ar is not None:
            pose[slot] = dict(mao[slot])
    return pose


# ------------------------------------------------------------------ desenho
# ------------------------------------------------------------------ malha das pernas
def _indice_8x(rgba):
    h0, w0 = rgba.shape[:2]
    chave = rgba.reshape(-1, 4).view(np.uint32).reshape(h0, w0)
    cores, idx = np.unique(chave, return_inverse=True)
    big = idx.reshape(h0, w0)
    for _ in range(3):
        big = scale2x(big)
    return cores, big


def deformar(rgba, origem, tris_src, tris_dst, tela):
    """Deforma o recorte por uma malha de triângulos (cada um com o seu afim), sem misturar cor: o recorte vai a 8x
    por Scale2x e cada pixel de destino pega a cor do ponto de origem (como no RotSprite). Cola por cima da tela."""
    cores, big = _indice_8x(rgba)
    hb, wb = big.shape
    ox, oy = origem
    H, W = tela.shape[:2]
    for ts, td in zip(tris_src, tris_dst):
        S = np.float32(ts)
        D = np.float32(td)
        M = cv2.getAffineTransform(D, S)  # destino -> origem
        x0, y0 = np.floor(D.min(0)).astype(int)
        x1, y1 = np.ceil(D.max(0)).astype(int) + 1
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        if x1 <= x0 or y1 <= y0:
            continue
        X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        # dentro do triângulo (com a borda incluída)
        def lado(p, q):
            return (q[0] - p[0]) * (Y - p[1]) - (q[1] - p[1]) * (X - p[0])
        l1, l2, l3 = lado(D[0], D[1]), lado(D[1], D[2]), lado(D[2], D[0])
        dentro = ((l1 >= -0.01) & (l2 >= -0.01) & (l3 >= -0.01)) | ((l1 <= 0.01) & (l2 <= 0.01) & (l3 <= 0.01))
        sx = M[0, 0] * X + M[0, 1] * Y + M[0, 2] - ox
        sy = M[1, 0] * X + M[1, 1] * Y + M[1, 2] - oy
        bx, by = np.floor(sx * 8).astype(int), np.floor(sy * 8).astype(int)
        ok = dentro & (bx >= 0) & (by >= 0) & (bx < wb) & (by < hb)
        cor = np.zeros(X.shape, np.uint32)
        cor[ok] = cores[big[by[ok], bx[ok]]]
        px = cor.view(np.uint8).reshape(X.shape + (4,))
        m = px[..., 3] > 0
        sub = tela[y0:y1, x0:x1]
        sub[m] = px[m]


LARGURA_MALHA = 70


def malha_perna(lado, w):
    """Triângulos (origem no parado, destino na pose) da perna `lado`: quatro linhas (topo no quadril, joelho,
    tornozelo e chão). O topo anda com o quadril, o joelho gira pela média da coxa e da canela (dobra macia, sem
    emenda), e do tornozelo para baixo a barra da calça e o pé só andam (o pé fica reto no chão)."""
    coxa, canela = f"coxa_{lado}", f"canela_{lado}"
    qr, jr, tr = K.OSSOS[coxa][0], K.OSSOS[canela][0], K.TORNOZELO[canela]
    q, a1 = w[coxa]
    j, a2 = w[canela]
    t = b.girar(tr, jr, a2)
    t = (t[0] + j[0] - jr[0], t[1] + j[1] - jr[1])
    L = LARGURA_MALHA
    dq = (q[0] - qr[0], q[1] - qr[1])
    topo_y = qr[1] - 30
    # direção da perna no parado (para a linha do joelho ficar de través)
    d = np.array(tr, float) - np.array(qr, float)
    d /= np.linalg.norm(d)
    n = np.array([d[1], -d[0]]) * -1  # perpendicular apontando para a direita
    if n[0] < 0:
        n = -n
    meio = np.radians((a1 + a2) / 2)
    c, s_ = np.cos(meio), np.sin(meio)
    n2 = np.array([n[0] * c - n[1] * s_, n[0] * s_ + n[1] * c])
    src = [[(qr[0] - L, topo_y), (qr[0] + L, topo_y)],
           [tuple(np.array(jr) - n * L), tuple(np.array(jr) + n * L)],
           [(tr[0] - L, tr[1]), (tr[0] + L, tr[1])],
           [(tr[0] - L, EIXO[1] + 4), (tr[0] + L, EIXO[1] + 4)]]
    chao = EIXO[1] + 4
    dt = (t[0] - tr[0], t[1] - tr[1])
    if dt[1] >= -12:  # pé no chão (ou que afundaria no meio do caminho entre duas poses): assenta no chão
        dt = (dt[0], 0)
    dst = [[(qr[0] - L + dq[0], topo_y + dq[1]), (qr[0] + L + dq[0], topo_y + dq[1])],
           [tuple(np.array(j) - n2 * L), tuple(np.array(j) + n2 * L)],
           [(tr[0] - L + dt[0], tr[1] + dt[1]), (tr[0] + L + dt[0], tr[1] + dt[1])],
           [(tr[0] - L + dt[0], chao + dt[1]), (tr[0] + L + dt[0], chao + dt[1])]]
    ts, td = [], []
    for i in range(3):
        a, b2, c2, d2 = src[i][0], src[i][1], src[i + 1][1], src[i + 1][0]
        A, B, C, D = dst[i][0], dst[i][1], dst[i + 1][1], dst[i + 1][0]
        ts += [(a, b2, c2), (a, c2, d2)]
        td += [(A, B, C), (A, C, D)]
    return ts, td


def desenhar(kit, pose):
    """Peças rígidas giradas nas juntas; pernas no chão deformadas por malha (calça larga dobra sem emenda);
    perna levantada com o desenho de câmara ou esticada preso no quadril."""
    if pose.get("_especial", {}).get("var"):
        desenhar.pintado, desenhar.pint = 0, None
        return especial(pose["_especial"]["var"])
    pv = pose.get("_pernas", {}).get("var")
    if pv:  # metade de baixo rígida: o quadril fica sempre onde ela pisa no chão (também no meio do caminho)
        cx, cy = kit["pecas"][f"pernas_{pv}"]["corpo"]
        pose = dict(pose, quadril=dict(pose.get("quadril", {}), dx=cx, dy=cy))
    w = b.mundo(pose)
    tela = np.zeros((b.TELA[1], b.TELA[0], 4), np.uint8)
    pint = np.zeros(tela.shape[:2], bool)
    usados = []
    camadas = list(K.CAMADAS)
    cf = pose.get("coxa_frente", {})
    if cf.get("var") and w["coxa_frente"][1] < -40:  # perna lá no alto passa na frente do tronco (atrás do punho)
        camadas.remove("coxa_frente")
        camadas.insert(camadas.index("braco_tras"), "coxa_frente")

    def por(r, x0, y0):
        h, w_ = r.shape[:2]
        X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(tela.shape[1], x0 + w_), min(tela.shape[0], y0 + h)
        if X1 > X0 and Y1 > Y0:
            pint[Y0:Y1, X0:X1] &= ~(r[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0, 3] > 0)
        b.colar(tela, r, x0, y0)
    pernas = pose.get("_pernas", {}).get("var")
    for slot in camadas:
        lado = slot.split("_")[-1]
        if pernas and (slot.startswith("coxa") or slot.startswith("canela")):
            continue
        if pernas and slot == "quadril":
            p = kit["pecas"][f"pernas_{pernas}"]
            pos, ang = w["quadril"]
            r, x0, y0 = b.colocar(p, p["img"], p["origem"], pos, ang)
            por(r, x0, y0)
            continue
        if slot.startswith("canela"):
            continue
        if slot.startswith("coxa") and not pose.get(slot, {}).get("var"):
            if slot == "coxa_frente" and pose.get("_chute_livre", {}).get("sim"):
                for s2 in (slot, f"canela_{lado}"):
                    p = kit["pecas"][s2]
                    img = p.get("img_inteira", p["img"])
                    r, x0, y0 = b.colocar(p, img, p["origem"], *w[s2])
                    por(r, x0, y0)
                continue
            p = kit["pecas"][f"perna_{lado}"]
            ts, td = malha_perna(lado, w)
            antes = tela[..., 3].copy()
            deformar(p["img"], p["origem"], ts, td, tela)
            pint &= ~((tela[..., 3] > 0) & (antes == 0))
            continue
        if slot.startswith("antebraco") and pose.get(slot.replace("antebraco", "braco"), {}).get("var"):
            continue
        p = kit["pecas"][b.chave(slot, pose)]
        pos, ang = w[slot]
        r, x0, y0 = b.colocar(p, p["img"], p["origem"], pos, ang)
        por(r, x0, y0)
        if slot == "tronco":
            r2, x2, y2 = b.colocar(p, p["pintado"], p["origem"], pos, ang)
            h2, w2 = r2.shape[:2]
            X0, Y0 = max(0, x2), max(0, y2)
            X1, Y1 = min(tela.shape[1], x2 + w2), min(tela.shape[0], y2 + h2)
            pint[Y0:Y1, X0:X1] |= r2[Y0 - y2:Y1 - y2, X0 - x2:X1 - x2, 3] > 0
        usados.append((p, pos, ang))
    for p, pos, ang in usados:
        r, x0, y0 = b.colocar(p, p["sob"], p["origem_sobra"], pos, ang)
        b.colar(tela, r, x0, y0, so_vazio=True)
    desenhar.pintado = int(pint.sum())
    desenhar.pint = pint
    return tapar_buracos(sem_migalha(fechar_frestas(tela, [w[s][0] for s in K.OSSOS])))


def buracos(tela, maximo=900):
    """Buracos fechados dentro da figura (o fundo aparecendo no meio da calça ou do tronco)."""
    fundo = (tela[..., 3] == 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(fundo, connectivity=4)
    out = np.zeros(fundo.shape, bool)
    for i in range(1, n):
        x, y, w, h, area = st[i]
        if area <= maximo and x > 0 and y > 0 and x + w < fundo.shape[1] and y + h < fundo.shape[0]:
            out |= lab == i
    return out


def tapar_buracos(tela):
    m = buracos(tela, getattr(K, "BURACO_MAX", 900))
    if not m.any():
        return tela
    out = tela.copy()
    rgb = cv2.inpaint(np.ascontiguousarray(tela[..., :3]), m.astype(np.uint8), 3, cv2.INPAINT_TELEA)
    out[m, :3] = rgb[m]
    out[m, 3] = 255
    return out


def sem_migalha(tela, minimo=20):
    al = (tela[..., 3] > 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(al, connectivity=8)
    out = tela.copy()
    for i in range(1, n):
        if st[i, 4] < minimo:
            out[lab == i] = 0
    return out


def fechar_frestas(tela, juntas, raio=5, perto_px=22):
    al = (tela[..., 3] > 0).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * raio + 1, 2 * raio + 1))
    perto = np.zeros_like(al)
    for x, y in juntas:
        cv2.circle(perto, (int(round(x)), int(round(y))), perto_px, 1, -1)
    fresta = (cv2.morphologyEx(al, cv2.MORPH_CLOSE, k) > 0) & (al == 0) & (perto > 0)
    if not fresta.any():
        return tela
    out = tela.copy()
    rgb = cv2.inpaint(np.ascontiguousarray(tela[..., :3]), fresta.astype(np.uint8), 3, cv2.INPAINT_TELEA)
    out[fresta, :3] = rgb[fresta]
    out[fresta, 3] = 255
    return out


# ------------------------------------------------------------------ robô de defeitos
def ys_max(tela):
    return int(np.nonzero((tela[..., 3] > 0).any(1))[0].max())


def conferir(tela, juntas, no_chao=True, buraco_ok=0):
    """Defeitos do quadro montado (vazio = passou): pedaço solto, fresta na junta, pé enterrado ou flutuando perto do
    chão, peça fora da tela."""
    erros = []
    al = (tela[..., 3] > 0).astype(np.uint8)
    n, _, st, _ = cv2.connectedComponentsWithStats(al, connectivity=8)
    soltos = sorted(int(x) for x in st[1:, 4] if x >= 4)[:-1]
    if soltos:
        erros.append(f"solta {soltos}")
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    buraco = (cv2.morphologyEx(al, cv2.MORPH_CLOSE, k) > 0) & (al == 0)
    for x, y in juntas:
        m = np.zeros_like(al)
        cv2.circle(m, (int(round(x)), int(round(y))), 14, 1, -1)
        if (buraco & (m > 0)).sum() > 6:
            erros.append(f"fresta em {int(x)},{int(y)}")
    if no_chao and ys_max(tela) < EIXO[1] - 8:
        erros.append(f"pé flutuando (y={ys_max(tela)})")
    nb = int(buracos(tela, getattr(K, "BURACO_MAX", 900)).sum())
    if nb > buraco_ok:
        erros.append(f"buraco {nb} px")
    ys = np.nonzero(al.any(1))[0]
    if ys.max() >= EIXO[1]:
        erros.append(f"pé enterrado (y={ys.max()})")
    if al[:, :2].any() or al[:, -2:].any() or al[:2].any():
        erros.append("fora da tela")
    return erros


def mancha(tela, original):
    """Mancha escura grossa no corpo a mais que na guarda montada do kit (contorno de peça que sobrou por dentro)."""
    def grosso(a):
        al = a[..., 3] > 0
        s = a[..., :3].astype(int).sum(-1)
        g = cv2.erode(((s < 110) & al).astype(np.uint8), np.ones((4, 4), np.uint8))
        ys = np.nonzero(al.any(1))[0]
        return int(g[ys.min() + 70:].sum())
    return grosso(tela), grosso(original)


# ------------------------------------------------------------------ animações
def ler_quadros(texto):
    """'soco 3/3 5/3A' -> [(folha/NN, ticks, ativo)]"""
    out, folha = [], None
    for tok in texto.split():
        if "/" not in tok:
            folha = tok
            continue
        d, t = tok.split("/")
        ativo = t.endswith("A")
        out.append((f"{folha}/{int(d):02d}", int(t.rstrip("A")), ativo))
    return out


def gerar(nomes, so_pose=False):
    if not so_pose:
        montar_kit()
    kit = ler_kit()
    raiz_docs = RAIZ / "docs/boneco-pecas" / K.LUTADOR
    raiz_docs.mkdir(parents=True, exist_ok=True)
    rel = raiz_docs / "robo_defeitos.md"
    linhas = {}
    if rel.exists():
        for l in rel.read_text(encoding="utf-8").splitlines():
            if l.startswith("| ") and "/" in l.split("|")[1]:
                linhas[l.split("|")[1].strip()] = l
    poses = {}
    guarda = desenhar(kit, {})
    for nome in nomes:
        acao, texto, clsn = K.ANIMS[nome]
        elems = ler_quadros(texto)
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            shutil.rmtree(b.SPR / pasta / nome, ignore_errors=True)
            (b.SPR / pasta / nome).mkdir(parents=True)
        unicos = list(dict.fromkeys(q for q, _, _ in elems))
        for q in unicos:
            poses[q] = pose_de(kit, q)
        bate = next((i for i, e in enumerate(elems) if e[2]), None)
        laco = acao in getattr(K, "LACOS", {0})
        quadros = vida.animar(poses, [(q, t) for q, t, _ in elems], bate=bate, laco=laco,
                              guarda=None if laco else poses.get(K.REF) or pose_de(kit, K.REF))
        if laco:
            quadros = vida.respirar(quadros)
        quadros = vida.atrasar(quadros, laco=laco)
        for k_ in [k_ for k_ in linhas if k_.startswith(nome + "/")]:
            del linhas[k_]
        for i, (pose, t, caixa, q) in enumerate(quadros):
            out = desenhar(kit, pose)
            pintado = desenhar.pintado
            w = b.mundo(pose)
            esp = pose.get("_especial", {}).get("var")
            if esp:  # desenho de hoje: só pedaço solto, fora da tela e pé onde o desenho de hoje pisa
                erros = conferir(out, no_chao=ys_max(abrir(esp)) >= EIXO[1] - 8, juntas=[],
                                 buraco_ok=0 if (b.SPR / "pecas_lado" / f"{esp}.png").exists()
                                 else int(buracos(especial(esp)).sum()))
                linhas[f"{nome}/{i:02d}"] = f"| {nome}/{i:02d} | {q} ({'kit de lado' if (b.SPR / 'pecas_lado' / f'{esp}.png').exists() else 'desenho de hoje'}) | {'PASS' if not erros else 'FAIL ' + '; '.join(erros)} |"
                Image.fromarray(out).save(b.SPR / "quadros_pecas_hd" / nome / f"{i:02d}.png")
                Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(b.SPR / "quadros_pecas" / nome / f"{i:02d}.png")
                continue
            if "_ar" not in pose:  # ponta de dedo que o giro do pé empurrou 1-2 px para baixo do chão: some
                abaixo = out[EIXO[1]:, :, 3] > 0
                if 0 < abaixo.sum() <= 8:
                    out[EIXO[1]:] = 0
            erros = conferir(out, no_chao="_ar" not in pose, juntas=[w[s][0] for s in ("braco_tras", "braco_frente", *(("antebraco_tras",) if "antebraco_tras" in w else ()), "cabeca",
                                                     # metade de baixo inteira de um desenho: as juntas das pernas não valem
                                                     *(() if pose.get("_pernas") else ("coxa_tras", "coxa_frente", "canela_tras", "canela_frente")))])
            m_novo, m_hoje = mancha(out, guarda)
            if pintado > getattr(K, "PINTADO_MAX", 30):
                erros.append(f"peito pintado à vista {pintado} px")
            if m_novo > m_hoje + getattr(K, "MANCHA_FOLGA", 60):
                erros.append(f"mancha {m_novo} px (hoje {m_hoje})")
            linhas[f"{nome}/{i:02d}"] = f"| {nome}/{i:02d} | {q} | {'PASS' if not erros else 'FAIL ' + '; '.join(erros)} |"
            Image.fromarray(out).save(b.SPR / "quadros_pecas_hd" / nome / f"{i:02d}.png")
            Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(b.SPR / "quadros_pecas" / nome / f"{i:02d}.png")
        cx = tuple(v * 3 for v in clsn) if clsn else None
        tempos = {"acao": acao, "caixa": cx, "origem": unicos,
                  "elementos": [{"desenho": i, "ticks": t, "caixa": c, "de": q}
                                for i, (_, t, c, q) in enumerate(quadros)]}
        assert sum(e["ticks"] for e in tempos["elementos"]) == sum(t for _, t, _ in elems)
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            (b.SPR / pasta / nome / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False),
                                                              encoding="utf-8")
        print(nome, len(unicos), "poses-chave ->", len(quadros), "desenhos")
    Image.fromarray(desenhar(kit, {})).save(b.SPR / "quadros_pecas_hd" / "guarda.png")
    corpo_rel = sorted(linhas.values())
    falhas = sum("FAIL" in l for l in corpo_rel)
    texto = "| quadro | desenho de hoje | robô de defeitos |\n|---|---|---|\n" + "\n".join(corpo_rel) + \
        f"\n\n{falhas} de {len(corpo_rel)} desenho(s) com defeito.\n"
    rel.write_text(texto, encoding="utf-8")
    print(texto[-200:])
    (b.SPR / "quadros_pecas_hd" / "poses.json").write_text(json.dumps(poses, indent=1), encoding="utf-8")
    return falhas


def video(nomes):
    import video_pecas as vp
    vp.SPR = b.SPR
    vp.GUARDA = K.REF
    vp.ATUAL = {}
    for n in nomes:
        vp.ATUAL[n] = [(q, t) for q, t, _ in ler_quadros(K.ANIMS[n][1])]
    vp.main_em(RAIZ / "docs/boneco-pecas" / K.LUTADOR)


def main():
    args = sys.argv[1:]
    configurar(args.pop(0))
    so_pose = "--so-pose" in args
    vid = "--video" in args
    nomes = [a for a in args if not a.startswith("--")] or list(K.ANIMS)
    gerar(nomes, so_pose)
    if vid:
        video(nomes)


if __name__ == "__main__":
    main()
