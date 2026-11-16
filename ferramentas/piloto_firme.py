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
from video_pecas import ATUAL  # noqa: E402

SPR = b.SPR
ACAO = {"parado": 0, "soco": 200, "chute_alto": 240}
CAIXA = {"soco": (1, (45, -276, 153, -192)), "chute_alto": (2, (36, -300, 159, -174))}
EXPRESSAO = {"soco/03": "foco", "soco/05": "esforco", "soco/06": "esforco", "soco/07": "foco",
             "chute_alto/01": "foco", "chute_alto/02": "foco", "chute_alto/04": "esforco",
             "chute_alto/05": "esforco", "chute_alto/06": "foco"}
# perna levantada: desenho do chute de hoje de onde sai a perna inteira
PERNA = {"chute_alto/02": "camara", "chute_alto/04": "esticada", "chute_alto/05": "esticada",
         "chute_alto/06": "camara"}
FOLGA_CORPO = 40
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


def separar_pes(kit):
    """Tira o pé de cada canela do kit e guarda à parte (kit['pes'])."""
    kit["pes"] = {}
    for slot, (tx, ty) in TORNOZELO.items():
        p = kit["pecas"][slot]
        img = p["img"].copy()
        ox, oy = p["origem"]
        corte = ty - oy
        pe = np.zeros_like(img)
        pe[corte:] = img[corte:]
        img[corte + 3:] = 0  # 3 linhas de sobra: a canela cobre o começo do pé, sem fresta
        p["img"] = img
        kit["pes"][slot] = {"img": pe, "origem": (ox, oy), "tornozelo": (tx, ty)}
    return kit


def desenhar(kit, pose):
    """O desenho do boneco_ajuste, com os pés retos no chão presos no tornozelo de cada canela."""
    tela = b.desenhar(kit, pose)
    w = b.mundo(pose)
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
        b.colar(tela, pe["img"], x0, y0, so_vazio=(slot == "canela_tras"))
    return fechar_frestas(tela)


def fechar_frestas(tela, raio=5):
    """Fresta entre duas peças (o fundo aparecendo onde o braço ou o joelho girou): fecha com a cor de volta
    (inpaint), só em buraco estreito, cercado de corpo; a silhueta de fora não muda."""
    al = (tela[..., 3] > 0).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * raio + 1, 2 * raio + 1))
    fresta = (cv2.morphologyEx(al, cv2.MORPH_CLOSE, k) > 0) & (al == 0)
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
    perto = cv2.dilate(bracos.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    for nome in ("tronco", "quadril"):
        pe = kit["pecas"][nome]
        arq = b.PECAS / pe["arquivo"]
        im = np.asarray(Image.open(arq).convert("RGBA")).copy()
        ox, oy = pe["origem"]
        h, w = im.shape[:2]
        area = perto[oy:oy + h, ox:ox + w]
        al = (im[..., 3] > 0).astype(np.uint8)
        dentro = cv2.erode(al, np.ones((5, 5), np.uint8)) > 0
        escuro = (im[..., :3].astype(int).sum(-1) < 150) & dentro & area
        escuro = cv2.dilate(escuro.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & dentro
        if escuro.any():
            rgb = cv2.inpaint(np.ascontiguousarray(im[..., :3]), escuro.astype(np.uint8), 4, cv2.INPAINT_TELEA)
            im[escuro, :3] = rgb[escuro]
            Image.fromarray(im).save(arq)
            print(f"{nome}: {int(escuro.sum())} px de contorno de braço tirados")


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
        b.BUSCA["coxa_frente"] = (range(-30, 31, 2), 2, [PERNA[q]])
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
    for nome, elems in ATUAL.items():
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            shutil.rmtree(SPR / pasta / nome, ignore_errors=True)
            (SPR / pasta / nome).mkdir(parents=True)
        unicos = list(dict.fromkeys(q for q, _ in elems))
        for i, q in enumerate(unicos):
            pose = pose_de(kit, q)
            poses[q] = pose
            out = desenhar(kit, pose)
            Image.fromarray(out).save(SPR / "quadros_pecas_hd" / nome / f"{i:02d}.png")
            Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(SPR / "quadros_pecas" / nome / f"{i:02d}.png")
            print(nome, i, q, {s: (v.get("var"), v["ang"], v.get("custo")) for s, v in pose.items()})
        bate, cx = CAIXA.get(nome, (None, None))
        tempos = {"acao": ACAO[nome], "caixa": cx, "origem": unicos,
                  "elementos": [{"desenho": unicos.index(q), "ticks": t, "caixa": k == bate}
                                for k, (q, t) in enumerate(elems)]}
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            (SPR / pasta / nome / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False),
                                                            encoding="utf-8")
    (SPR / "quadros_pecas_hd" / "poses.json").write_text(json.dumps(poses, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
