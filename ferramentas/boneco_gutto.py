#!/usr/bin/env python3
"""Gutto pelo boneco de peças, método "corpo firme + vida" aprovado pelo Alisson no Pengaró (16/11).

Usa as mesmas ferramentas do piloto do Pengaró (boneco_ajuste.py, piloto_firme.py, vida_pecas.py), trocando só o que
é do desenho: os polígonos de cada peça e as juntas, medidos no parado do Gutto (sprite 94,0 do .sff, em 3x).

O Gutto não tem quadros_arcade_hd no git (o .sff dele vem do Blender), então os desenhos de hoje saem do próprio .sff
(ferramentas/extrair_hd_sff.py) numa tela 1080x780 com o eixo em (540, 660).

  python ferramentas/boneco_gutto.py kit            recorta o kit em sprites/gutto/pecas/ e grava a prova das peças
  python ferramentas/boneco_gutto.py animar [NOMES] monta parado, soco, chute_alto... em quadros_pecas_hd/quadros_pecas
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
import extrair_hd_sff as sff  # noqa: E402

RAIZ = AQUI.parent
SPR = RAIZ / "sprites" / "gutto"
HD = SPR / "quadros_sff_hd"
REF = "94_0"
PROVA = RAIZ / "docs" / "boneco-pecas" / "gutto"

# ------------------------------------------------------------------ medidas do parado do Gutto (94,0, 3x)
CABECA = [(526, 318), (610, 318), (612, 372), (602, 392), (584, 402), (566, 400), (548, 392), (536, 380), (526, 360)]
PESCOCO = [(540, 378), (556, 390), (572, 398), (588, 400), (588, 410), (560, 412), (536, 404)]
# braço de trás (o da esquerda, que cruza o peito com o punho na frente do abdome) com o cordão que pende
BRACO_TRAS = [(482, 388), (504, 384), (518, 396), (520, 420), (556, 422), (566, 438), (560, 462), (520, 466),
              (500, 470), (478, 474), (456, 470), (444, 470), (438, 452), (452, 428), (462, 404)]
BRACO_FRENTE = [(576, 410), (590, 402), (604, 398), (622, 392), (640, 386), (660, 396), (668, 420), (654, 446),
                (640, 470), (620, 484), (598, 482), (582, 474), (572, 452), (572, 430)]
PERNA_TRAS = [(478, 500), (520, 500), (548, 520), (546, 560), (532, 590), (510, 610), (490, 640), (488, 664),
              (430, 664), (440, 640), (462, 610), (476, 580), (480, 540)]
PERNA_FRENTE = [(548, 520), (560, 500), (590, 500), (612, 520), (632, 560), (626, 600), (616, 630), (640, 640),
                (666, 664), (575, 664), (586, 630), (596, 600), (590, 580), (560, 565)]
NO_DA_FAIXA = [(0, 0), (1, 0), (0, 1)]  # o Gutto não tem nó de faixa
# o que os braços tapam no tronco: o kit pinta por baixo para não abrir buraco quando o braço sai
PEITO_ESCONDIDO = [(500, 400), (580, 410), (600, 440), (596, 478), (500, 478), (488, 440)]
# o braço de trás do Gutto é a beira das costas (não tem tronco atrás dele): nada a tapar do lado
LADO_ESCONDIDO = [(0, 0), (1, 0), (0, 1)]
CALCA_ESCONDIDA = [(0, 0), (1, 0), (0, 1)]
JOELHO_TRAS, JOELHO_FRENTE = (516, 574), (612, 562)
TORNOZELO = {"canela_tras": (472, 636), "canela_frente": (606, 634)}
OSSOS = {
    "quadril": ((540, 500), None, (540, 530)),
    "tronco": ((540, 478), "quadril", (560, 400)),
    "cabeca": ((566, 396), "tronco", (568, 330)),
    "braco_tras": ((496, 400), "tronco", (520, 450)),
    "braco_frente": ((588, 418), "tronco", (630, 420)),
    "coxa_tras": ((514, 512), "quadril", JOELHO_TRAS),
    "canela_tras": (JOELHO_TRAS, "coxa_tras", TORNOZELO["canela_tras"]),
    "coxa_frente": ((574, 510), "quadril", JOELHO_FRENTE),
    "canela_frente": (JOELHO_FRENTE, "coxa_frente", TORNOZELO["canela_frente"]),
}
CAMADAS = ["coxa_tras", "canela_tras", "quadril", "tronco", "cabeca", "canela_frente", "coxa_frente", "braco_frente",
           "braco_tras"]


def cinto(x):
    return 474 + (x - 480) * 0.06


def configurar():
    """Aponta o boneco_ajuste para o Gutto (as funções de lá leem estes nomes do módulo)."""
    b.SPR, b.HD, b.PECAS, b.REF = SPR, HD, SPR / "pecas", REF
    for nome in ("CABECA", "PESCOCO", "BRACO_TRAS", "BRACO_FRENTE", "PERNA_TRAS", "PERNA_FRENTE", "NO_DA_FAIXA",
                 "PEITO_ESCONDIDO", "LADO_ESCONDIDO", "CALCA_ESCONDIDA", "JOELHO_TRAS", "JOELHO_FRENTE", "OSSOS",
                 "CAMADAS"):
        setattr(b, nome, globals()[nome])
    b.cinto = cinto
    b.VARIANTES = {"braco_frente": {}, "coxa_frente": {}}


def garantir_hd(nomes):
    """Grava em quadros_sff_hd os sprites que faltam (grupo_indice)."""
    falta = [n for n in nomes if not (HD / f"{n}.png").exists()]
    if not falta:
        return
    cores, sp = sff.sprites("gutto")
    HD.mkdir(parents=True, exist_ok=True)
    for n in falta:
        g, i = map(int, n.split("_"))
        Image.fromarray(sff.tela(cores, sp[(g, i)])).save(HD / f"{n}.png")


def prova_segmentos(saida):
    """Parado com cada peça pintada de uma cor e as juntas marcadas: confere os polígonos."""
    ref = b.abrir(REF)
    cores = {"cabeca": (255, 80, 80), "tronco": (80, 200, 255), "braco_tras": (255, 220, 0),
             "braco_frente": (0, 255, 120), "coxa_tras": (200, 120, 255), "canela_tras": (255, 140, 0),
             "coxa_frente": (255, 0, 200), "canela_frente": (0, 160, 255), "quadril": (160, 255, 160)}
    kit = b.ler_kit()
    tela = np.zeros_like(ref)
    tela[..., :3] = 40
    tela[..., 3] = 255
    out = tela.copy()
    for slot in CAMADAS:
        p = kit["pecas"][slot]
        im = p["img"]
        x0, y0 = p["origem"]
        h, w = im.shape[:2]
        m = im[..., 3] > 0
        sub = out[y0:y0 + h, x0:x0 + w]
        mix = (im[..., :3].astype(int) * 0.45 + np.array(cores[slot]) * 0.55).astype(np.uint8)
        sub[m, :3] = mix[m]
    for slot, (j, _, ponta) in OSSOS.items():
        cv2.circle(out, (int(j[0]), int(j[1])), 4, (255, 255, 255, 255), -1)
        cv2.line(out, (int(j[0]), int(j[1])), (int(ponta[0]), int(ponta[1])), (255, 255, 255, 255), 1)
    c = Image.fromarray(out).crop((400, 300, 700, 680))
    c.resize((c.width * 3, c.height * 3), Image.NEAREST).save(saida)


def kit():
    configurar()
    garantir_hd([REF])
    b.montar_kit()
    PROVA.mkdir(parents=True, exist_ok=True)
    prova_segmentos(PROVA / "kit_pecas.png")
    g = b.desenhar(b.ler_kit(), {})
    c = Image.fromarray(g).crop((400, 300, 700, 680))
    c.resize((c.width * 3, c.height * 3), Image.NEAREST).save(PROVA / "kit_montado.png")


# ------------------------------------------------------------------ variantes (peça que muda de desenho, não de ângulo)
# (desenho de onde sai, polígono, junta no desenho de origem: None = acha pelo tronco)
VARIANTES = {
    "braco_frente": {
        "esticado": ("1252_0", [(588, 384), (640, 382), (680, 384), (700, 387), (726, 390), (728, 422), (700, 420),
                                (660, 414), (626, 422), (600, 428), (588, 410)], (606, 404)),
    },
    "coxa_tras": {  # perna de apoio esticada (chute): desenho inteiro da perna do 957, preso no quadril de trás
        "apoio": ("957_0", [(500, 505), (556, 500), (556, 540), (546, 570), (527, 600), (517, 630), (540, 648),
                            (548, 664), (466, 664), (476, 635), (494, 600), (504, 560), (499, 530)], (522, 512)),
    },
    "coxa_frente": {
        "camara": ("965_0", [(538, 420), (560, 414), (600, 424), (617, 440), (616, 470), (590, 493), (556, 502),
                             (550, 522), (506, 527), (503, 505), (518, 490), (536, 470)], (544, 440)),
        "esticada": ("957_0", [(542, 422), (560, 404), (600, 394), (650, 374), (690, 348), (708, 352), (708, 382),
                               (680, 396), (650, 410), (620, 421), (586, 436), (562, 456), (546, 462)], (552, 436)),
    },
}

# as animações: (ação do .air, elementos [(sprite, ticks, caixa?)], caixa de golpe)
ANIM = {
    "parado": (0, [("94_0", 9, 0), ("102_0", 9, 0), ("134_0", 9, 0), ("126_0", 9, 0)], None),
    "soco": (200, [("81_0", 3, 0), ("1278_0", 1, 0), ("1252_0", 5, 1), ("1252_0", 1, 0), ("84_0", 3, 0),
                   ("85_0", 6, 0)], (45, -276, 222, -192)),
    "chute_alto": (240, [("422_0", 5, 0), ("423_0", 2, 0), ("965_0", 1, 0), ("966_0", 1, 0), ("957_0", 6, 1),
                         ("957_0", 2, 0), ("426_0", 7, 0), ("427_0", 9, 0), ("428_0", 9, 0)],
                   (36, -300, 208, -174)),
}
PERNA = {"423_0": "camara", "965_0": "camara", "966_0": "camara", "957_0": "esticada", "426_0": "camara"}


_MOLDE = None


def corpo(kit, alvo, folga_x=100, folga_y=(-50, 70)):
    """(dx, dy) do tronco do parado no quadro, só por translação (corpo firme). O molde é o tronco e a cabeça como
    aparecem no parado (sem os braços, sem o que eles tapam): o pedaço tapado do kit é chute, não serve de molde.
    Custo = diferença de cor, com fundo transparente contando como erro cheio (assim ele não "casa" no vazio)."""
    global _MOLDE
    if _MOLDE is None:
        ref = b.abrir(REF)
        yy, xx = np.mgrid[:ref.shape[0], :ref.shape[1]]
        m = (ref[..., 3] > 0) & (yy < cinto(xx)) & ~b.mascara(BRACO_TRAS) & ~b.mascara(BRACO_FRENTE)
        m = cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        sel = m[y0:y1, x0:x1]
        _MOLDE = (x0, y0, ref[y0:y1, x0:x1, :3].astype(np.int16)[sel], sel)
    x0, y0, cor, sel = _MOLDE
    h, w = sel.shape
    H, W = alvo.shape[:2]

    def custo(dx, dy):
        X, Y = x0 + dx, y0 + dy
        if X < 0 or Y < 0 or X + w > W or Y + h > H:
            return 1e9
        a = alvo[Y:Y + h, X:X + w][sel]
        d = np.minimum(np.abs(a[:, :3].astype(np.int16) - cor).mean(1), 120)
        d[a[:, 3] == 0] = 120
        return float(d.mean())

    melhor = min(((custo(dx, dy), dx, dy) for dy in range(folga_y[0], folga_y[1] + 1, 3)
                  for dx in range(-folga_x, folga_x + 1, 3)))
    _, bx, by = melhor
    melhor = min(((custo(dx, dy), dx, dy) for dy in range(by - 3, by + 4) for dx in range(bx - 3, bx + 4)))
    return melhor[1], melhor[2]


def configurar_piloto():
    import piloto_firme as pf
    pf.corpo = corpo
    pf.TORNOZELO = TORNOZELO
    pf.CHAO = 659
    pf.FOLGA_CORPO = 90
    pf.PES_REF = None
    pf.RAIZ_DOCS = PROVA
    return pf


def montar_com_variantes(pf):
    """Kit com as variantes presas na junta certa: a junta de origem sai do tronco achado no desenho de origem."""
    b.VARIANTES = {k: {v: (f, p, jf or OSSOS[k][0]) for v, (f, p, jf) in vs.items()} for k, vs in VARIANTES.items()}
    b.montar_kit()
    kit = b.ler_kit()
    for slot, vs in VARIANTES.items():
        for var, (fonte, poli, jf) in vs.items():
            garantir_hd([fonte])
            if jf is None:
                dx, dy = pf.corpo(kit, b.abrir(fonte))
                j = OSSOS[slot][0]
                jf = (j[0] + dx, j[1] + dy)
                print(f"{slot}_{var}: tronco em {fonte} a {dx:+d},{dy:+d}")
            b.VARIANTES[slot][var] = (fonte, poli, jf)
    b.montar_kit()
    kit = json.loads((b.PECAS / "kit.json").read_text(encoding="utf-8"))
    # a perna levantada é só a perna (pele e contorno): o calção e o pé de apoio do desenho de origem ficam de fora
    for slot in ("coxa_frente", "coxa_tras"):
        for var in VARIANTES[slot]:
            so_pele(b.PECAS / kit["pecas"][f"{slot}_{var}"]["arquivo"])
        calcao_no_quadril(kit, slot)
    limpar_contorno_dos_bracos(kit)


def calcao_no_quadril(kit, slot="coxa_frente"):
    """A boca do calção da perna da frente vai para o quadril: quando a perna levanta (ou troca pelo desenho do
    chute), o calção fica inteiro no lugar e a coxa sai de dentro dele, sem buraco preto."""
    cf, qd = kit["pecas"][slot], kit["pecas"]["quadril"]
    a = np.asarray(Image.open(b.PECAS / cf["arquivo"]).convert("RGBA")).copy()
    q = np.asarray(Image.open(b.PECAS / qd["arquivo"]).convert("RGBA"))
    hsv = cv2.cvtColor(np.ascontiguousarray(a[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    al = a[..., 3] > 0
    pele = al & (hsv[..., 0] <= 25) & (hsv[..., 1] > 70) & (hsv[..., 2] > 50)
    perto = cv2.dilate(pele.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    calcao = al & ~perto
    ox, oy = cf["origem"]
    qx, qy = qd["origem"]
    x0, y0 = min(ox, qx), min(oy, qy)
    x1 = max(ox + a.shape[1], qx + q.shape[1])
    y1 = max(oy + a.shape[0], qy + q.shape[0])
    novo = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    novo[qy - y0:qy - y0 + q.shape[0], qx - x0:qx - x0 + q.shape[1]] = q
    sub = novo[oy - y0:oy - y0 + a.shape[0], ox - x0:ox - x0 + a.shape[1]]
    sub[calcao] = a[calcao]
    # pele solta no meio do calção (resto da coxa que ficou no quadril) vira calção
    hq = cv2.cvtColor(np.ascontiguousarray(novo[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    yy = np.arange(novo.shape[0])[:, None] + y0
    pele_q = (novo[..., 3] > 0) & (hq[..., 0] <= 25) & (hq[..., 1] > 70) & (hq[..., 2] > 50) & (yy > 498)
    if pele_q.any():
        rgb = cv2.inpaint(np.ascontiguousarray(novo[..., :3]), pele_q.astype(np.uint8), 3, cv2.INPAINT_TELEA)
        novo[pele_q, :3] = rgb[pele_q]
    Image.fromarray(novo).save(b.PECAS / qd["arquivo"])
    qd["origem"] = [int(x0), int(y0)]
    a[calcao] = 0
    Image.fromarray(a).save(b.PECAS / cf["arquivo"])
    (b.PECAS / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")


def so_pele(arq):
    im = np.asarray(Image.open(arq).convert("RGBA")).copy()
    hsv = cv2.cvtColor(np.ascontiguousarray(im[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    al = im[..., 3] > 0
    pele = al & (hsv[..., 0] <= 25) & (hsv[..., 1] > 70) & (hsv[..., 2] > 50)
    n, lab, st, _ = cv2.connectedComponentsWithStats(pele.astype(np.uint8), connectivity=8)
    if n > 1:  # só o pedaço de pele maior (a perna); pele de outra parte que entrou no polígono sai
        pele = lab == (1 + int(np.argmax(st[1:, 4])))
    pele = cv2.morphologyEx(pele.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0
    contorno = (cv2.dilate(pele.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & al & \
        (im[..., :3].astype(int).sum(-1) < 200)
    # mancha escura grossa encostada na perna (sombra do calção do desenho de origem) não é contorno
    grosso = cv2.morphologyEx(contorno.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    contorno &= ~(cv2.dilate(grosso.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    manter = (pele & al) | contorno
    im[~manter] = 0
    Image.fromarray(im).save(arq)


def limpar_contorno_dos_bracos(kit):
    """Contorno escuro dos braços do parado que ficou no tronco: vira a cor de volta (só no tronco; o calção do Gutto
    é preto e não entra)."""
    ref = b.abrir(REF)
    bracos = (b.mascara(BRACO_TRAS) | b.mascara(BRACO_FRENTE)) & (ref[..., 3] > 0)
    perto = cv2.dilate(bracos.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    pe = kit["pecas"]["tronco"]
    arq = b.PECAS / pe["arquivo"]
    im = np.asarray(Image.open(arq).convert("RGBA")).copy()
    ox, oy = pe["origem"]
    h, w = im.shape[:2]
    dentro = cv2.erode((im[..., 3] > 0).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    escuro = (im[..., :3].astype(int).sum(-1) < 150) & dentro & perto[oy:oy + h, ox:ox + w]
    if escuro.any():
        rgb = cv2.inpaint(np.ascontiguousarray(im[..., :3]), escuro.astype(np.uint8), 4, cv2.INPAINT_TELEA)
        im[escuro, :3] = rgb[escuro]
        Image.fromarray(im).save(arq)
        print(f"tronco: {int(escuro.sum())} px de contorno de braço tirados")


def separar_pes(kit):
    """Pé separado da canela (fica reto no chão, preso no tornozelo). O Gutto luta descalço: o pé é só pele."""
    kit["pes"] = {}
    for slot, (tx, ty) in TORNOZELO.items():
        p = kit["pecas"][slot]
        img = p["img"].copy()
        ox, oy = p["origem"]
        corte = ty - oy
        pe = np.zeros_like(img)
        pe[corte:] = img[corte:]
        img[corte + 3:] = 0
        p["img"] = img
        kit["pes"][slot] = {"img": pe, "origem": (ox, oy), "tornozelo": (tx, ty),
                            "fundo": int(np.nonzero(pe[..., 3].any(1))[0].max())}
    return kit


def desenhar(pf, kit, pose):
    tela = b.desenhar(kit, pose)
    w = b.mundo(pose)
    for slot in ("canela_tras", "canela_frente"):
        if pose.get(slot.replace("canela", "coxa"), {}).get("var"):
            continue
        joelho, ang = w[slot]
        jr = OSSOS[slot][0]
        pe = kit["pes"][slot]
        t = b.girar(pe["tornozelo"], jr, ang)
        tx, ty = t[0] + joelho[0] - jr[0], t[1] + joelho[1] - jr[1]
        x0 = int(round(pe["origem"][0] + tx - pe["tornozelo"][0]))
        y0 = int(round(pe["origem"][1] + ty - pe["tornozelo"][1]))
        fundo = pe["fundo"] + y0
        if abs(fundo - pf.CHAO) <= 10:
            y0 += pf.CHAO - fundo
        b.colar(tela, pe["img"], x0, y0, so_vazio=(slot == "canela_tras"))
    return pf.sem_migalha(pf.fechar_frestas(tela, juntas=[w[sl][0] for sl in OSSOS]), minimo=80)


def pose_de(pf, kit, q, nome):
    alvo = b.abrir(q)
    dx, dy = pf.corpo(kit, alvo)
    pose = {"quadril": {"ang": 0, "dx": dx, "dy": dy}}
    if nome == "parado":  # respira, não pula: a respiração do vida_pecas cuida do peito
        pose["quadril"]["dy"] = max(-2, min(2, dy))
    # guarda de muay thai: o braço de trás fica na guarda e só balança; o da frente só estica no soco
    b.BUSCA["braco_tras"] = (range(-12, 13, 2), 3, [None])
    if nome == "soco":
        b.BUSCA["braco_frente"] = (range(-30, 31, 3), 4, [None, "esticado"])
    else:
        b.BUSCA["braco_frente"] = (range(-20, 21, 2), 3, [None])
    pose = b.encaixar(kit, alvo, pose, ordem=["braco_tras", "braco_frente"])
    if q in PERNA and nome == "chute_alto":
        giro = range(-6, 7, 2)  # a perna levantada fica no ângulo em que foi desenhada (joelho para cima)
        b.BUSCA["coxa_frente"] = (giro, 2, [PERNA[q]])
        b.ANGULOS_VARIANTE = giro
        pose = b.encaixar(kit, alvo, pose, ordem=["coxa_frente"])
        # perna de apoio: o desenho da perna esticada, no ângulo dele; o quadril fica na altura em que o pé
        # dela encosta no chão
        pose["coxa_tras"] = {"ang": 0, "var": "apoio"}
        pose["quadril"]["dy"] = 0
    elif nome == "chute_alto" and len(pf.pes(alvo)) < 2:
        pose = pf.pernas_no_chao(pose, alvo, so_tras=True)
        b.BUSCA["coxa_frente"] = (range(-40, 41, 2), 2, [None])
        b.BUSCA["canela_frente"] = (range(-40, 41, 2), 2, [None])
        pose = b.encaixar(kit, alvo, pose, ordem=["coxa_frente", "canela_frente"])
    else:
        pose = pf.pernas_no_chao(pose, alvo)
    return pose


def animar():
    import vida_pecas as vida
    configurar()
    pf = configurar_piloto()
    nomes = sys.argv[2:] or list(ANIM)
    garantir_hd([q for n in ANIM.values() for q, _, _ in n[1]])
    if "--so-pose" not in sys.argv:
        montar_com_variantes(pf)
    nomes = [n for n in nomes if not n.startswith("--")]
    kit = separar_pes(b.ler_kit())
    b.FOLGA_VARIANTE = {"coxa_frente": 3}
    b.BUSCA["coxa_tras"] = (range(-20, 21, 2), 2, [None])
    b.BUSCA["canela_tras"] = (range(-20, 21, 2), 2, [None])
    b.BUSCA["canela_tras"] = (range(-20, 21, 2), 2, [None])
    b.BUSCA["canela_frente"] = (range(-24, 25, 2), 2, [None])
    pf.MANCHA_REF = pf.mancha_ref()
    relatorio = ["| quadro | desenho de hoje | robô de defeitos |", "|---|---|---|"]
    poses = {}
    for nome in nomes:
        acao, elems, cx = ANIM[nome]
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            shutil.rmtree(SPR / pasta / nome, ignore_errors=True)
            (SPR / pasta / nome).mkdir(parents=True)
        for q in dict.fromkeys(q for q, _, _ in elems):
            poses[q] = pose_de(pf, kit, q, nome)
        bate = [k for k, (_, _, c) in enumerate(elems) if c]
        laco = nome == "parado"
        quadros = vida.animar(poses, [(q, t) for q, t, _ in elems], bate=bate or None, laco=laco, guarda={})
        if laco:
            quadros = vida.respirar(quadros)
        quadros = vida.atrasar(quadros, laco=laco)
        originais = {}
        for i, (pose, t, caixa_on, q) in enumerate(quadros):
            out = desenhar(pf, kit, pose)
            originais.setdefault(q, b.abrir(q))
            erros = pf.conferir(out, originais[q], None)
            relatorio.append(f"| {nome}/{i:02d} | {q} | {'PASS' if not erros else 'FAIL ' + '; '.join(erros)} |")
            Image.fromarray(out).save(SPR / "quadros_pecas_hd" / nome / f"{i:02d}.png")
            Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(SPR / "quadros_pecas" / nome / f"{i:02d}.png")
        tempos = {"acao": acao, "caixa": cx, "origem": list(dict.fromkeys(q for q, _, _ in elems)),
                  "elementos": [{"desenho": i, "ticks": t, "caixa": c, "de": q}
                                for i, (_, t, c, q) in enumerate(quadros)]}
        assert sum(e["ticks"] for e in tempos["elementos"]) == sum(t for _, t, _ in elems)
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            (SPR / pasta / nome / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False),
                                                            encoding="utf-8")
        print(nome, "->", len(quadros), "desenhos")
    Image.fromarray(desenhar(pf, kit, poses.get("94_0") or pose_de(pf, kit, "94_0", "parado"))).save(
        SPR / "quadros_pecas_hd" / "guarda.png")
    falhas = sum("FAIL" in linha for linha in relatorio)
    texto = "\n".join(relatorio) + f"\n\n{falhas} quadro(s) com defeito.\n"
    print(texto)
    PROVA.mkdir(parents=True, exist_ok=True)
    (PROVA / "robo_defeitos.md").write_text(texto, encoding="utf-8")
    (SPR / "quadros_pecas_hd" / "poses.json").write_text(json.dumps(poses, indent=1), encoding="utf-8")


def video():
    """Vídeo lado a lado, tira de ticks e antes/depois (video_pecas.py), com o atual tirado do .sff."""
    import tempfile
    import video_pecas as vp
    saida = PROVA / (sys.argv[2] if len(sys.argv) > 2 else "corpo_firme")
    tmp = Path(tempfile.mkdtemp())
    (tmp / "quadros_arcade_hd" / "ginga").mkdir(parents=True)
    (tmp / "quadros_arcade_hd" / "ginga" / "00.png").symlink_to(HD / f"{REF}.png")
    for _, elems, _ in ANIM.values():
        for q, _, _ in elems:
            alvo = tmp / "quadros_arcade_hd" / f"{q}.png"
            if not alvo.exists():
                alvo.symlink_to(HD / f"{q}.png")
    (tmp / "quadros_pecas_hd").symlink_to(SPR / "quadros_pecas_hd")
    vp.SPR = tmp
    nomes = [n for n in sys.argv[3:]] or [n for n in ANIM if (SPR / "quadros_pecas_hd" / n).exists()]
    vp.ATUAL = {n: [(q, t) for q, t, _ in ANIM[n][1]] for n in nomes}
    sys.argv = [sys.argv[0], str(saida)]
    vp.main()
    shutil.rmtree(tmp)


if __name__ == "__main__":
    {"kit": kit, "animar": animar, "video": video}[sys.argv[1]]()
