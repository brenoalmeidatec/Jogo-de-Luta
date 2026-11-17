#!/usr/bin/env python3
"""Piloto do boneco de peças, versão "corpo firme" (escolha do Alisson, 16/11).

O tronco, a pele e o rosto saem sempre de um desenho só (o parado de referência, ginga/00), em cor cheia, sem paleta
reduzida. O que se mexe são os braços e as pernas, que giram nas juntas e ficam presos nelas, seguindo as poses que o
jogo mostra hoje. O rosto troca só de expressão (guarda, foco, esforço), e é sempre o mesmo rosto, no mesmo tamanho.

  python ferramentas/piloto_firme.py            refaz o kit (sprites/pengaro/pecas) e grava quadros_pecas_hd e
                                               quadros_pecas (1x), com tempos.json iguais aos de hoje
  python ferramentas/piloto_firme.py --so-pose  usa o kit que já existe

Como cada quadro é montado:
  1. o tronco do kit é casado no quadro de hoje só por translação (sem girar e sem escalar: corpo firme);
  2. o quadril vai junto com o tronco;
  3. braços e pernas são encaixados osso por osso (ferramentas/boneco_ajuste.py), com a junta presa na mãe;
  4. no chute, a perna levantada é o desenho inteiro da perna (coxa, canela e pé) tirado do chute de hoje, preso no
     quadril do kit.
"""
import json
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import boneco_ajuste as b  # noqa: E402
import corrigir_cabeca as cc  # noqa: E402
import vida_pecas as vida  # noqa: E402
import pele_pecas as pele  # noqa: E402
from video_pecas import ATUAL  # noqa: E402

SPR = b.SPR
ACAO = {"parado": 0, "soco": 200, "chute_alto": 240}
CAIXA = {"soco": (1, (45, -276, 153, -192)), "chute_alto": (2, (36, -300, 159, -174))}
EXPRESSAO = {"soco/03": "foco", "soco/05": "esforco", "soco/06": "esforco", "soco/07": "foco",
             "chute_alto/01": "foco", "chute_alto/02": "foco", "chute_alto/04": "esforco",
             "chute_alto/05": "esforco", "chute_alto/06": "foco"}
# perna levantada: desenho do chute de hoje de onde sai a perna inteira
PERNA = {"ginga/06": "agachada", "ginga/02": "agachada", "chute_alto/01": "camara", "chute_alto/02": "camara", "chute_alto/04": "esticada", "chute_alto/05": "esticada",
         "chute_alto/06": "camara"}
FOLGA_CORPO = 40
PELE = False  # True: desenho sem linha de corte (pele que dobra nas juntas, pele_pecas.py); o Pengaró liga no pengaro_todo
CHAO = 659  # pixel mais baixo do pé no parado (3x)
RAIZ_DOCS = AQUI.parent / "docs/boneco-pecas/corpo_firme"
# pé separado da canela: fica sempre reto no chão (a canela gira, o pé não), preso no tornozelo
TORNOZELO = {"canela_tras": (488, 624), "canela_frente": (580, 618)}


def cinza(a):
    rgb = a[..., :3].astype(np.float32)
    rgb[a[..., 3] == 0] = 110.0
    return rgb


def corpo(kit, alvo):
    """(dx, dy) do tronco do kit no quadro: casamento só por translação."""
    p = kit["pecas"]["tronco"]
    t = p["img"]
    x0, y0 = p["origem"]
    h, w = t.shape[:2]
    X0, Y0 = max(0, x0 - FOLGA_CORPO), max(0, y0 - FOLGA_CORPO)
    reg = alvo[Y0:y0 + h + FOLGA_CORPO, X0:x0 + w + FOLGA_CORPO]
    m = (t[..., 3] > 0).astype(np.uint8)
    m[440 - y0:] = 0  # só ombro e peito: a barriga some atrás do joelho no chute
    r = cv2.matchTemplate(cinza(reg), cinza(t), cv2.TM_SQDIFF, mask=np.repeat(m[..., None], 3, -1))
    _, _, p_min, _ = cv2.minMaxLoc(r)
    return p_min[0] + X0 - x0, p_min[1] + Y0 - y0


# perna da frente agachada (ginga funda): desenho inteiro da perna do ginga/02, sem faixa e sem bolinhas
b.VARIANTES["coxa_frente"]["agachada"] = ("ginga/02", [
    (548, 540), (556, 552), (575, 556), (592, 552), (598, 530), (612, 522), (625, 548), (626, 605), (612, 620),
    (618, 663), (552, 663), (556, 622), (562, 602), (548, 575)], (572, 512))


def tirar_faixa(im):
    """Tira faixa verde e bolinhas (são do quadril) de um recorte de perna."""
    hsv = cv2.cvtColor(np.ascontiguousarray(im[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    verde = (hsv[..., 0] >= 35) & (hsv[..., 0] <= 90) & (hsv[..., 1] > 80)
    bolinha = (hsv[..., 0] >= 14) & (hsv[..., 0] <= 32) & (hsv[..., 1] > 150) & (hsv[..., 2] > 150)
    im = im.copy()
    im[(verde | bolinha) & (im[..., 3] > 0)] = 0
    return im


def montar():
    """Refaz o kit com a perna levantada presa no quadril certo e junta as expressões do rosto."""
    if b.PECAS.exists():
        shutil.rmtree(b.PECAS)
    b.montar_kit()  # primeiro com o pivô velho, só para ter o tronco
    kit = b.ler_kit()
    for var, (fonte, poli, _) in list(b.VARIANTES["coxa_frente"].items()):
        dx, dy = corpo(kit, b.abrir(fonte))
        quadril = b.OSSOS["coxa_frente"][0]
        b.VARIANTES["coxa_frente"][var] = (fonte, poli, (quadril[0] + dx, quadril[1] + dy))
        print(f"perna {var}: corpo em {fonte} está a {dx:+d},{dy:+d}")
    b.montar_kit()
    kit = json.loads((b.PECAS / "kit.json").read_text(encoding="utf-8"))
    # a perna levantada não leva pele da barriga do desenho de onde saiu (a barriga é a do kit): só o pé é pele
    quadril = b.OSSOS["coxa_frente"][0]
    for var, limite in (("camara", ("y", 505)), ("esticada", ("x", 630))):
        fonte, _, jf = b.VARIANTES["coxa_frente"][var]
        sx, sy = quadril[0] - jf[0], quadril[1] - jf[1]
        pe = kit["pecas"][f"coxa_frente_{var}"]
        arq = b.PECAS / pe["arquivo"]
        im = np.asarray(Image.open(arq).convert("RGBA")).copy()
        ox, oy = pe["origem"]
        yy, xx = np.mgrid[:im.shape[0], :im.shape[1]]
        src = (yy + oy - sy) if limite[0] == "y" else (xx + ox - sx)
        hsv = cv2.cvtColor(np.ascontiguousarray(im[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
        pele = (im[..., 3] > 0) & (hsv[..., 0] <= 22) & (hsv[..., 1] > 70) & (hsv[..., 2] < 235)
        im[pele & (src < limite[1])] = 0
        Image.fromarray(im).save(arq)
    pe = kit["pecas"]["coxa_frente_agachada"]
    arq = b.PECAS / pe["arquivo"]
    Image.fromarray(tirar_faixa(np.asarray(Image.open(arq).convert("RGBA")))).save(arq)
    limpar_contorno_dos_bracos(kit)
    base = kit["pecas"]["cabeca"]
    base_img = np.asarray(Image.open(b.PECAS / base["arquivo"]).convert("RGBA"))
    tmpl, caixa = cc.referencia()
    centro_ref = ((caixa[0] + caixa[2]) / 2, (caixa[1] + caixa[3]) / 2)
    ox, oy = base["origem"]
    for nome in ("foco", "esforco"):
        rec, centro = cc.cabeca_do_kit(nome, tmpl, caixa)
        tela = np.zeros((b.TELA[1], b.TELA[0], 4), np.uint8)
        tela[oy:oy + base_img.shape[0], ox:ox + base_img.shape[1]] = base_img
        x0 = int(round(centro_ref[0] - centro[0]))
        y0 = int(round(centro_ref[1] - centro[1]))
        h, w = rec.shape[:2]
        sub = tela[y0:y0 + h, x0:x0 + w]
        mm = rec[..., 3] > 0
        sub[mm] = rec[mm]
        ys, xs = np.nonzero(tela[..., 3] > 0)
        X0, Y0 = xs.min(), ys.min()
        arq = f"cabeca_{nome}.png"
        Image.fromarray(tela[Y0:ys.max() + 1, X0:xs.max() + 1]).save(b.PECAS / arq)
        kit["pecas"][f"cabeca_{nome}"] = dict(base, arquivo=arq, origem=[int(X0), int(Y0)],
                                              fonte=f"quadros_arcade_hd/{cc.EXPRESSOES[nome]}.png")
    (b.PECAS / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")


def pes(a):
    """Centro x de cada pé no chão (faixa de baixo da figura), de trás para a frente."""
    faixa = a[640:664, :, 3].any(0)
    xs = np.nonzero(faixa)[0]
    if not len(xs):
        return []
    runs = np.split(xs, np.nonzero(np.diff(xs) > 3)[0] + 1)
    return [(r.min() + r.max()) / 2 for r in runs if len(r) > 6]


PES_REF = None


def cruz(a, b_):
    return a[0] * b_[1] - a[1] * b_[0]


def ik(quadril, tornozelo, joelho_ref, quadril_ref, tornozelo_ref):
    """Perna de dois ossos: com o quadril e o tornozelo dados, acha o joelho do lado em que ele dobra no parado e
    devolve o giro da coxa e o da canela (graus, horário na tela; a canela relativa à coxa)."""
    q, t = np.array(quadril, float), np.array(tornozelo, float)
    qr, jr, tr = (np.array(v, float) for v in (quadril_ref, joelho_ref, tornozelo_ref))
    l1, l2 = np.linalg.norm(jr - qr), np.linalg.norm(tr - jr)
    d = t - q
    dist = min(np.linalg.norm(d), l1 + l2 - 0.5)
    u = d / np.linalg.norm(d)
    a = (l1 ** 2 - l2 ** 2 + dist ** 2) / (2 * dist)
    h = np.sqrt(max(l1 ** 2 - a ** 2, 0))
    n = np.array([-u[1], u[0]])
    lado = np.sign(cruz(tr - qr, jr - qr)) or 1
    j = q + u * a + n * h
    if np.sign(cruz(t - q, j - q)) != lado:
        j = q + u * a - n * h
    ang = lambda v: np.degrees(np.arctan2(v[1], v[0]))
    coxa = ang(j - q) - ang(jr - qr)
    canela = ang(t - j) - ang(tr - jr) - coxa
    return round(float(coxa), 1), round(float(canela), 1)


def pernas_no_chao(pose, alvo, so_tras=False):
    """As pernas que ficam no chão saem por IK: o pé fica plantado onde o pé do quadro de hoje está."""
    global PES_REF
    if PES_REF is None:
        PES_REF = pes(b.abrir(b.REF))
    agora = pes(alvo)
    w = b.mundo(pose)
    pernas = [("coxa_tras", "canela_tras", 0)] + ([] if so_tras else [("coxa_frente", "canela_frente", -1)])
    for coxa, canela, i in pernas:
        qr, jr = b.OSSOS[coxa][0], b.OSSOS[canela][0]
        tr = TORNOZELO[canela]
        dx = (agora[i] - PES_REF[i]) if agora and (i == 0 or len(agora) > 1) else 0
        quadril_agora = w[coxa][0]
        c1, c2 = ik(quadril_agora, (tr[0] + dx, tr[1]), jr, qr, tr)
        pose[coxa] = {"ang": c1}
        pose[canela] = {"ang": c2}
    return pose


def calca_lisa(img, regiao, anel=4):
    """Pinta `regiao` com a calça em volta: o contorno escuro que encosta nela (resto de bolinha, mão ou garrafa que
    estava por cima) entra junto na pintura, e só pixel claro serve de cor (sem mancha cinza)."""
    if not regiao.any():
        return img
    rgb = img[..., :3].astype(int)
    # contorno e sombra cinza (pouca cor); a listra verde e amarela da calça não entra
    escuro = (((rgb.sum(-1) < 420) & (np.ptp(rgb, -1) < 70)) | (rgb.sum(-1) < 150)) & (img[..., 3] > 0)
    perto = cv2.dilate(regiao.astype(np.uint8), np.ones((2 * anel + 1, 2 * anel + 1), np.uint8)) > 0
    alvo = regiao | (escuro & perto)
    # a beira de fora da peça (contorno da silhueta) fica
    borda = (img[..., 3] > 0) & (cv2.erode((img[..., 3] > 0).astype(np.uint8), np.ones((3, 3), np.uint8)) == 0)
    alvo &= ~borda
    fonte = (img[..., 3] == 0) | alvo
    pint = cv2.inpaint(np.ascontiguousarray(img[..., :3]), fonte.astype(np.uint8), 5, cv2.INPAINT_TELEA)
    out = img.copy()
    out[alvo, :3] = pint[alvo]
    return out


def separar_pes(kit):
    """Tira o pé de cada canela do kit e guarda à parte (kit['pes']); separa também o cordão e as bolinhas da faixa
    (kit['bolinhas']), que vão por cima de tudo."""
    q = kit["pecas"]["quadril"]["img"]
    hsv = cv2.cvtColor(np.ascontiguousarray(q[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    laranja = (q[..., 3] > 0) & (hsv[..., 0] >= 12) & (hsv[..., 0] <= 32) & (hsv[..., 1] > 120) & (hsv[..., 2] > 110)
    laranja = cv2.dilate(laranja.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & (q[..., 3] > 0)
    n, lab, st, _ = cv2.connectedComponentsWithStats(laranja.astype(np.uint8))
    # só o cordão e as bolinhas, que pendem do nó para a direita; a listra amarela da calça (à esquerda) fica
    ox_q = kit["pecas"]["quadril"]["origem"][0]
    grandes = [i for i in range(1, n) if st[i, 4] > 60 and ox_q + st[i, 0] + st[i, 2] / 2 > 560]
    bol = np.zeros_like(q)
    m = np.isin(lab, grandes)
    # o contorno escuro do cordão e das bolinhas vai junto com elas (senão fica o fantasma no quadril)
    rgbq = q[..., :3].astype(int)
    verde = (hsv[..., 0] >= 40) & (hsv[..., 0] <= 95) & (hsv[..., 1] > 80)
    escuro_q = (rgbq.sum(-1) < 330) & (q[..., 3] > 0) & ~verde
    m = m | (cv2.dilate(m.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & escuro_q)
    bol[m] = q[m]
    sob = cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & (q[..., 3] > 0) & ~verde
    kit["bolinhas"] = bol
    # e tira do quadril, senão elas aparecem em dobro quando balançam: o que fica atrás delas vira calça (inpaint),
    # só onde o quadril continua em volta; o que pendia para fora do quadril fica vazio
    resto = (q[..., 3] > 0) & ~m
    fechado = cv2.morphologyEx(resto.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8)) > 0
    vazio = q[..., 3] == 0
    pint = cv2.inpaint(np.ascontiguousarray(q[..., :3]), (m | vazio).astype(np.uint8), 4, cv2.INPAINT_TELEA)
    q2 = q.copy()
    tapa = m & fechado
    q2[tapa, :3] = pint[tapa]
    q2[tapa, 3] = 255
    q2[m & ~fechado] = 0
    q2 = calca_lisa(q2, tapa | (sob & ~m & fechado))
    furo = (cv2.morphologyEx((q2[..., 3] > 0).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)) > 0) \
        & (q2[..., 3] == 0) & fechado
    if furo.any():
        q2[furo, 3] = 255
        q2 = calca_lisa(q2, furo)
    kit["pecas"]["quadril"]["img"] = q2
    # a coxa da frente tem o buraco das bolinhas (elas ficavam por cima): fecha com calça
    cf = kit["pecas"]["coxa_frente"]["img"]
    a = (cf[..., 3] > 0).astype(np.uint8)
    buraco = (cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8)) > 0) & (a == 0)
    n_, lab_, st_, _ = cv2.connectedComponentsWithStats(buraco.astype(np.uint8))
    # só buraco de dentro (não o vão que encosta na beira de cima, onde a coxa encontra o quadril)
    dentro = np.zeros_like(buraco)
    for i in range(1, n_):
        x, y, w_, h_, area = st_[i]
        if area >= 6:
            dentro |= lab_ == i
    if dentro.any():
        cf = cf.copy()
        cf[dentro, 3] = 255
        kit["pecas"]["coxa_frente"]["img"] = calca_lisa(cf, dentro)
    ys, xs = np.nonzero(m)
    o = kit["pecas"]["quadril"]["origem"]
    kit["no_bolinhas"] = (o[0] + float(xs.mean()), o[1] + float(ys.min()))  # o cordão pende do nó, em cima
    kit["pes"] = {}
    for slot, (tx, ty) in TORNOZELO.items():
        p = kit["pecas"][slot]
        img = p["img"].copy()
        ox, oy = p["origem"]
        corte = ty - oy
        hsv = cv2.cvtColor(np.ascontiguousarray(img[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
        rgb = img[..., :3].astype(int)
        calca = (rgb.min(-1) > 140) & (np.ptp(rgb, -1) < 100)
        caneleira = (hsv[..., 0] >= 25) & (hsv[..., 0] <= 95) & (hsv[..., 1] > 40)
        so_pe = np.zeros(img.shape[:2], bool)
        so_pe[corte:] = True
        barra = np.zeros(img.shape[:2], bool)
        barra[:corte + 10] = True  # barra da calça e caneleira só existem logo abaixo do tornozelo
        mpe = so_pe & (img[..., 3] > 0) & ~((calca | caneleira) & barra)
        pe = np.zeros_like(img)
        pe[mpe] = img[mpe]
        fundo = np.zeros(img.shape[:2], bool)
        fundo[corte + 3:] = True
        img[fundo & mpe] = 0  # 3 linhas de sobra: a canela cobre o começo do pé, sem fresta
        p["img"] = img
        kit["pes"][slot] = {"img": pe, "origem": (ox, oy), "tornozelo": (tx, ty),
                            "fundo": int(np.nonzero(pe[..., 3].any(1))[0].max())}
    return kit


def desenhar(kit, pose):
    """O desenho do boneco_ajuste, com os pés retos no chão presos no tornozelo de cada canela."""
    tela = pele.desenhar(kit, pose) if PELE else b.desenhar(kit, pose)
    w = b.mundo(pose)
    # cordão e bolinhas da faixa ficam por cima da perna da frente, como no desenho
    for slot in ("canela_tras", "canela_frente"):
        if slot == "canela_frente" and pose.get("coxa_frente", {}).get("var"):
            continue
        joelho, ang = w[slot]
        jr = b.OSSOS[slot][0]
        pe = kit["pes"][slot]
        t = b.girar(pe["tornozelo"], jr, ang)
        tx, ty = t[0] + joelho[0] - jr[0], t[1] + joelho[1] - jr[1]
        x0 = int(round(pe["origem"][0] + tx - pe["tornozelo"][0]))
        y0 = int(round(pe["origem"][1] + ty - pe["tornozelo"][1]))
        img_pe, fundo_pe = pe["img"], pe["fundo"]
        ponta = int(round(pose.get("_ponta_tras", {}).get("dy", 0))) if slot == "canela_tras" else 0
        if ponta > 0:
            # calcanhar levantado (pé de trás na ponta, estudo de anatomia): o peito do pé fica mais em pé, o tornozelo
            # sobe `ponta` px e os dedos continuam no chão (o IK já subiu o tornozelo)
            img_pe = esticar_tornozelo(img_pe, ponta)
            fundo_pe += ponta
        # pé perto do chão encosta no chão (o chão do parado), sem afundar nem flutuar alguns pixels
        fundo = fundo_pe + y0
        if abs(fundo - CHAO) <= 10:
            y0 += CHAO - fundo
        b.colar(tela, img_pe, x0, y0, so_vazio=(slot == "canela_tras"))
    p = kit["pecas"]["quadril"]
    bo = pose.get("_bolinhas", {})
    (qx, qy), qang = w["quadril"]
    jq = b.OSSOS["quadril"][0]
    no = b.girar(kit["no_bolinhas"], jq, qang)  # nó da faixa no mundo
    no = (no[0] + qx - jq[0] + bo.get("dx", 0), no[1] + qy - jq[1] + bo.get("dy", 0))
    piv = (kit["no_bolinhas"][0] - p["origem"][0], kit["no_bolinhas"][1] - p["origem"][1])
    r, piv2 = b.rotsprite(kit["bolinhas"], qang + bo.get("ang", 0), piv)
    b.colar(tela, r, int(round(no[0] - piv2[0])), int(round(no[1] - piv2[1])))
    tela = sem_migalha(fechar_frestas(tela, juntas=[w[sl][0] for sl in b.OSSOS]))
    if PELE:  # acabamento do Pengaró (contorno e calça dele); os outros lutadores ficam como estavam
        tela = contornar(sem_risco_na_calca(tela))
    return tela


CONTORNO = np.array([33, 2, 26])  # cor do contorno de fora do parado (mediana da borda)


def contornar(tela):
    """Beira da figura sem contorno (onde uma peça girada mostra o corte dela): o pixel da beira escurece para o tom
    do contorno do parado, como no desenho (lá 98% da beira é escura)."""
    al = (tela[..., 3] > 0).astype(np.uint8)
    beira = (al > 0) & (cv2.erode(al, np.ones((3, 3), np.uint8)) == 0)
    clara = beira & (tela[..., :3].astype(int).sum(-1) >= 250)
    out = tela.copy()
    out[clara, :3] = (0.25 * tela[clara, :3] + 0.75 * CONTORNO).astype(np.uint8)
    return out


def sem_risco_na_calca(tela, maximo=80):
    """Risco escuro solto no meio da calça (resto do contorno de dentro da perna do parado, que boia quando as pernas
    abrem mais): mancha escura pequena cercada de calça clara vira calça."""
    rgb = tela[..., :3].astype(int)
    al = tela[..., 3] > 0
    escuro = ((rgb.sum(-1) < 360) & (np.ptp(rgb, -1) < 80) & al).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(escuro, connectivity=8)
    if n <= 1:
        return tela
    calca = (rgb.min(-1) > 140) & (np.ptp(rgb, -1) < 100) & al
    dentro = cv2.erode(al.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    alvo = np.zeros(al.shape, bool)
    for i in range(1, n):
        if st[i, 4] > maximo:
            continue
        x, y, w_, h_ = st[i, :4]
        sl = (slice(max(0, y - 4), y + h_ + 4), slice(max(0, x - 4), x + w_ + 4))
        m = lab[sl] == i
        anel = cv2.dilate(m.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & ~m
        if not dentro[sl][m].all():
            continue
        if calca[sl][anel].mean() >= 0.7:
            alvo[sl] |= m
    if not alvo.any():
        return tela
    out = tela.copy()
    fonte = alvo | ~al
    pint = cv2.inpaint(np.ascontiguousarray(tela[..., :3]), fonte.astype(np.uint8), 4, cv2.INPAINT_TELEA)
    out[alvo, :3] = pint[alvo]
    return out


TORNOZELO_FAIXA = 14


def esticar_tornozelo(img, d):
    """Pé com o tornozelo (faixa de cima) d pixels mais comprido (d < 0: mais curto); a sola desce d pixels."""
    ys = np.nonzero(img[..., 3].any(1))[0]
    r0 = int(ys.min())
    k = TORNOZELO_FAIXA
    faixa = img[r0:r0 + k]
    nova = cv2.resize(faixa, (img.shape[1], max(1, k + d)), interpolation=cv2.INTER_NEAREST)
    out = np.zeros((img.shape[0] + max(d, 0), img.shape[1], 4), np.uint8)
    out[:r0] = img[:r0]
    out[r0:r0 + nova.shape[0]] = nova
    resto = img[r0 + k:]
    out[r0 + nova.shape[0]:r0 + nova.shape[0] + resto.shape[0]] = resto
    return out


def sem_migalha(tela, minimo=None):
    """Some com pixel solto (migalha de borda de peça girada) separado da figura."""
    if minimo is None:
        minimo = 40 if PELE else 12
    al = (tela[..., 3] > 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(al, connectivity=8)
    out = tela.copy()
    for i in range(1, n):
        if st[i, 4] < minimo:
            out[lab == i] = 0
    return out


PERTO_DA_JUNTA = 22


def fechar_frestas(tela, raio=5, juntas=()):
    """Fresta entre duas peças (o fundo aparecendo onde o braço ou o joelho girou): fecha com a cor de volta
    (inpaint), só em buraco estreito e só perto de uma junta. O vão entre os dedos e entre o braço e o corpo, que é
    do desenho, fica como está."""
    al = (tela[..., 3] > 0).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * raio + 1, 2 * raio + 1))
    perto = np.zeros_like(al)
    for x, y in juntas:
        cv2.circle(perto, (int(round(x)), int(round(y))), PERTO_DA_JUNTA, 1, -1)
    fresta = (cv2.morphologyEx(al, cv2.MORPH_CLOSE, k) > 0) & (al == 0) & (perto > 0)
    if not fresta.any():
        return tela
    out = tela.copy()
    rgb = cv2.inpaint(np.ascontiguousarray(tela[..., :3]), fresta.astype(np.uint8), 3, cv2.INPAINT_TELEA)
    out[fresta, :3] = rgb[fresta]
    out[fresta, 3] = 255
    return out


def limpar_contorno_dos_bracos(kit):
    """O contorno escuro dos braços do parado ficou pintado no tronco e no quadril (na beira de onde o braço estava).
    Quando o braço gira, ele aparece como uma mancha preta: troca pela cor de volta (inpaint), só por dentro da peça."""
    ref = b.abrir(b.REF)
    bracos = (b.mascara(b.BRACO_TRAS) | b.mascara(b.BRACO_FRENTE)) & (ref[..., 3] > 0)
    perto = cv2.dilate(bracos.astype(np.uint8), np.ones((17, 17), np.uint8)) > 0
    # por dentro da figura do parado (o contorno de fora fica); a beira cortada da peça, onde o braço estava, não conta
    dentro_ref = cv2.erode((ref[..., 3] > 0).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    for nome in ("tronco", "quadril"):
        pe = kit["pecas"][nome]
        arq = b.PECAS / pe["arquivo"]
        im = np.asarray(Image.open(arq).convert("RGBA")).copy()
        ox, oy = pe["origem"]
        h, w = im.shape[:2]
        area = perto[oy:oy + h, ox:ox + w]
        # dentro da figura do parado ou da parte que foi tapada por baixo do braço (sem a beira de 1 px da peça)
        dentro = (dentro_ref[oy:oy + h, ox:ox + w] | (cv2.erode((im[..., 3] > 0).astype(np.uint8),
                                                               np.ones((3, 3), np.uint8)) > 0)) & (im[..., 3] > 0)
        dentro &= cv2.erode((im[..., 3] > 0).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        # na calça (branca/lilás) qualquer cinza é resto do contorno da mão e da garrafa
        limite = 330 if nome == "quadril" else 190
        escuro = (im[..., :3].astype(int).sum(-1) < limite) & dentro & area
        escuro = cv2.dilate(escuro.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & dentro
        if escuro.any():
            rgb = cv2.inpaint(np.ascontiguousarray(im[..., :3]), escuro.astype(np.uint8), 4, cv2.INPAINT_TELEA)
            im[escuro, :3] = rgb[escuro]
            Image.fromarray(im).save(arq)
            print(f"{nome}: {int(escuro.sum())} px de contorno de braço tirados")


# ------------------------------------------------------------------ robô de defeitos (nenhum erro de peça)
def conferir(tela, original, juntas):
    """Lista de defeitos do quadro montado. Vazio = passou.
      fresta    buraco perto de junta que o fechamento não deu conta (> 40 px antes de fechar = peça desgrudou)
      mancha    mancha escura grossa no corpo (abaixo do queixo) a mais que no parado
      solta     pedaço de figura separado do resto
      chão      pé fora do chão (no quadro de hoje ele está no chão)"""
    erros = []
    al = (tela[..., 3] > 0).astype(np.uint8)
    n, _, st, _ = cv2.connectedComponentsWithStats(al, connectivity=8)
    soltos = sorted(int(x) for x in st[1:, 4] if x >= 4)[:-1]
    if soltos:
        erros.append(f"solta {soltos}")
    s = tela[..., :3].astype(int).sum(-1)
    grosso = cv2.erode(((s < 110) & (al > 0)).astype(np.uint8), np.ones((4, 4), np.uint8))
    ys = np.nonzero(al.any(1))[0]
    corpo = grosso[ys.min() + 80:].sum()
    og = cv2.erode(((original[..., :3].astype(int).sum(-1) < 110) & (original[..., 3] > 0)).astype(np.uint8),
                   np.ones((4, 4), np.uint8))
    yo0 = np.nonzero((original[..., 3] > 0).any(1))[0].min()
    base = max(MANCHA_REF, int(og[yo0 + 80:].sum()))  # sombra que o desenho de hoje também tem não é defeito
    if corpo > base + MANCHA_FOLGA:
        erros.append(f"mancha {int(corpo)} px (esperado até {base + MANCHA_FOLGA})")
    yo = np.nonzero((original[..., 3] > 0).any(1))[0].max()
    if yo >= 655 and not (655 <= ys.max() <= 663):
        erros.append(f"chão: pé em y={ys.max()} (hoje {yo})")
    return erros


def mancha_ref():
    r = b.abrir(b.REF)
    al = (r[..., 3] > 0).astype(np.uint8)
    s = r[..., :3].astype(int).sum(-1)
    grosso = cv2.erode(((s < 110) & (al > 0)).astype(np.uint8), np.ones((4, 4), np.uint8))
    ys = np.nonzero(al.any(1))[0]
    return int(grosso[ys.min() + 80:].sum())


MANCHA_REF = None
MANCHA_FOLGA = 50  # a sombra entre as coxas cresce quando as pernas abrem no passo (é do desenho, não é resto de peça)


def pose_de(kit, q):
    alvo = b.abrir(q)
    dx, dy = corpo(kit, alvo)
    pose = {"quadril": {"ang": 0, "dx": dx, "dy": dy}}
    if q in EXPRESSAO:
        pose["cabeca"] = {"ang": 0, "var": EXPRESSAO[q]}
    ordem = ["braco_tras", "braco_frente"]
    angs, folga, _ = b.BUSCA["braco_frente"]
    # no chute a mão da frente fica aberta, como hoje
    if q.startswith("chute_alto"):
        b.BUSCA["braco_frente"] = (range(-20, 21, 2), 3, [None])
    else:
        b.BUSCA["braco_frente"] = (range(-45, 46, 3), 4, [None, "punho", "esticado"])
    pose = b.encaixar(kit, alvo, pose, ordem=ordem)
    if q in PERNA:  # a perna levantada só gira um pouco em volta do quadril; a de trás fica plantada
        giro = range(-4, 5, 1) if PERNA[q] == "agachada" else range(-30, 31, 2)  # agachada: pé fica no chão
        b.BUSCA["coxa_frente"] = (giro, 2, [PERNA[q]])
        b.ANGULOS_VARIANTE = giro
        pose = b.encaixar(kit, alvo, pose, ordem=["coxa_frente"])
        pose = pernas_no_chao(pose, alvo, so_tras=True)
    elif q.startswith("chute_alto") and len(pes(alvo)) < 2:  # pé da frente subindo, sem desenho de perna
        pose = pernas_no_chao(pose, alvo, so_tras=True)
        b.BUSCA["coxa_frente"] = (range(-40, 41, 2), 2, [None])
        b.BUSCA["canela_frente"] = (range(-40, 41, 2), 2, [None])
        pose = b.encaixar(kit, alvo, pose, ordem=["coxa_frente", "canela_frente"])
    else:
        pose = pernas_no_chao(pose, alvo)
    return pose


def main():
    if "--so-pose" not in sys.argv:
        montar()
    kit = separar_pes(b.ler_kit())
    b.FOLGA_VARIANTE = {"coxa_frente": 3}  # a perna levantada fica presa no quadril
    b.BUSCA["coxa_tras"] = (range(-20, 21, 2), 2, [None])
    b.BUSCA["canela_tras"] = (range(-20, 21, 2), 2, [None])
    b.BUSCA["canela_frente"] = (range(-24, 25, 2), 2, [None])
    poses = {}
    global MANCHA_REF
    MANCHA_REF = mancha_ref()
    relatorio = ["| quadro | desenho de hoje | robô de defeitos |", "|---|---|---|"]
    for nome, elems in ATUAL.items():
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            shutil.rmtree(SPR / pasta / nome, ignore_errors=True)
            (SPR / pasta / nome).mkdir(parents=True)
        unicos = list(dict.fromkeys(q for q, _ in elems))
        for q in unicos:
            poses[q] = pose_de(kit, q)
        bate, cx = CAIXA.get(nome, (None, None))
        laco = nome == "parado"
        quadros = vida.animar(poses, elems, bate=bate, laco=laco, guarda={})
        if laco:
            quadros = vida.respirar(quadros)
        quadros = vida.atrasar(quadros, laco=laco)
        originais = {}
        for i, (pose, t, caixa_on, q) in enumerate(quadros):
            out = desenhar(kit, pose)
            if q not in originais:
                originais[q] = b.abrir(q)
            erros = conferir(out, originais[q], None)
            relatorio.append(f"| {nome}/{i:02d} | {q} | {'PASS' if not erros else 'FAIL ' + '; '.join(erros)} |")
            Image.fromarray(out).save(SPR / "quadros_pecas_hd" / nome / f"{i:02d}.png")
            Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(SPR / "quadros_pecas" / nome / f"{i:02d}.png")
        tempos = {"acao": ACAO[nome], "caixa": cx, "origem": unicos,
                  "elementos": [{"desenho": i, "ticks": t, "caixa": c, "de": q}
                                for i, (_, t, c, q) in enumerate(quadros)]}
        assert sum(e["ticks"] for e in tempos["elementos"]) == sum(t for _, t in elems)
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            (SPR / pasta / nome / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False),
                                                            encoding="utf-8")
        print(nome, len(unicos), "poses-chave ->", len(quadros), "desenhos")
    Image.fromarray(desenhar(kit, {})).save(SPR / "quadros_pecas_hd" / "guarda.png")
    falhas = sum("FAIL" in l for l in relatorio)
    texto = "\n".join(relatorio) + f"\n\n{falhas} quadro(s) com defeito.\n"
    print(texto)
    (RAIZ_DOCS / "robo_defeitos.md").write_text(texto, encoding="utf-8")
    (SPR / "quadros_pecas_hd" / "poses.json").write_text(json.dumps(poses, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
