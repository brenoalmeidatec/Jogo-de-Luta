#!/usr/bin/env python3
"""Pengaró inteiro no boneco de peças (corpo firme + vida): todas as ações da forma básica.

  python ferramentas/pengaro_todo.py poses [desenho ...]   poses-chave de cada desenho de hoje (cache em
                                                            docs/boneco-pecas/todo/poses.json)
  python ferramentas/pengaro_todo.py animar [ação ...]      intermediários, respiração e atraso; grava
                                                            sprites/pengaro/quadros_pecas_hd/acoes/<ação>/ e o robô
  python ferramentas/pengaro_todo.py folha                  folha de contato de todas as ações (para olhar)

A lista de ações (desenho e ticks de cada elemento) vem de ferramentas/acoes_pengaro.py
(docs/boneco-pecas/acoes_pengaro.json). O corpo é achado no quadro de hoje em qualquer posição e ângulo (pulo,
queda, rolamento, de ponta-cabeça): o peito do kit é procurado girado de 15 em 15 graus. Com o corpo em pé e o pé
no chão, as pernas saem por IK (pé plantado); no ar ou deitado, cada osso é encaixado no desenho de hoje.
"""
import json
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import boneco_ajuste as b  # noqa: E402
import piloto_firme as pf  # noqa: E402
import vida_pecas as vida  # noqa: E402
import corrigir_cabeca as cc  # noqa: E402
import piloto_corrigido as pc  # noqa: E402

sys.path.insert(0, str(AQUI / "pixel"))
import cores  # noqa: E402

RAIZ = AQUI.parent
DOCS = RAIZ / "docs/boneco-pecas/todo"
ACOES = RAIZ / "docs/boneco-pecas/acoes_pengaro.json"
SPR = b.SPR
SAIDA = b.SPR / "quadros_pecas_hd/acoes"
SAIDA_1X = b.SPR / "quadros_pecas/acoes"
ANGULOS_CORPO = [0, 15, -15, 30, -30, 45, -45, 60, -60, 90, -90, 120, -120, 150, -150, 180]
GIRO_CUSTO = 0.0004  # preferência pelo corpo em pé quando o casamento empata
# expressões por tipo de ação
DOR = ("apanha", "queda", "derrota")
RISO = ("vitoria", "provoca", "golaco")
IOU_MINIMO = 0.65  # abaixo disso o quadro é "especial": desenho de hoje com o rosto do kit e a paleta do parado
LACOS = {0, 20, 21, 5, 6, 10, 11, 12, 120, 130, 140, 150, 121, 131, 141, 122, 132, 142, 151, 152, 100, 105}


# Golpes que hoje ficam confusos (lista mandada ao Alisson em 16/11): a pose-chave do encaixe ganha um ajuste à mão
# para o golpe ler de longe. Chave: desenho de hoje; valor: o que muda na pose (por osso).
AJUSTE = {
    # defesa: hoje o antebraço cruza na frente do rosto (escorço que a peça de lado não faz); no kit o punho sobe e
    # cobre o queixo, guarda alta, com cara de esforço
    **{f"defesa/0{i}": {"braco_frente": {"var": "punho", "ang": -45, "dx": -2, "dy": -4},
                        "cabeca": {"ang": -4, "var": "esforco"}} for i in range(2, 7)},
    "defesa/01": {"braco_frente": {"var": "punho", "ang": -25, "dx": -2, "dy": -4}},
    "defesa/07": {"braco_frente": {"var": "punho", "ang": -25, "dx": -2, "dy": -4}},
    # soco no ar: o braço da frente sai esticado para baixo, na diagonal (hoje ele fica encolhido em todos os quadros)
    "ar_soco/04": {"braco_frente": {"var": "esticado", "ang": 28, "dx": 0, "dy": 0}},
    "ar_soco/05": {"braco_frente": {"var": "esticado", "ang": 22, "dx": 0, "dy": 0}},
    # provocação: riso e a mão da frente chamando ("vem"), indo e voltando
    "provoca/02": {"braco_frente": {"ang": -35, "dx": 0, "dy": 0}, "cabeca": {"ang": 0, "var": "riso"}},
    "provoca/03": {"braco_frente": {"ang": -10, "dx": 0, "dy": 0}, "cabeca": {"ang": 0, "var": "riso"}},
    "provoca/04": {"braco_frente": {"ang": -35, "dx": 0, "dy": 0}, "cabeca": {"ang": 0, "var": "riso"}},
    "provoca/05": {"braco_frente": {"ang": -10, "dx": 0, "dy": 0}, "cabeca": {"ang": 0, "var": "riso"}},
    # chute alto: o encaixe punha a perna caída para trás no quadro em que ela sobe; vira a câmara com o joelho mais
    # alto, abrindo (estudo de anatomia, Lei 8: joelho primeiro, pé depois)
    "chute_alto/03": {"coxa_frente": {"var": "camara", "ang": -18, "dx": 0, "dy": 0}},
}


# Golpes refeitos inteiros à mão, com o corpo firme (os desenhos de hoje não servem de molde): pose por osso; as pernas
# plantam no chão por IK nos pés do parado.
# Golpe agachado não levanta (pedido do Breno, #32, 22/11; ferramentas/regua_pernas.py). O agachado do Pengaró é
# quadro especial (o desenho de hoje com o rosto do kit): o kit não dobra tão fundo. A cabeçada agachada sai desse
# mesmo desenho com o tronco dobrado em volta da cintura (dobrar(): a rotação cresce suave numa faixa, sem linha de
# corte); as pernas não mexem. Valor: (desenho de base, graus para a frente, px HD para a frente, expressão).
AGACHADO = "agachado/04"
DOBRA = {
    "cabecada/01": (AGACHADO, 0, 0, "foco"),
    # antecipação: o tronco vai para trás e o queixo desce olhando o alvo
    "cabecada/02": (AGACHADO, -10, -6, "foco"),
    # bate: o tronco dobra para a frente e a testa chega primeiro
    "cabecada/04": (AGACHADO, 20, 16, "esforco"),
    "cabecada/05": (AGACHADO, 17, 13, "esforco"),
    # volta para o agachado
    "cabecada/06": (AGACHADO, 8, 6, "foco"),
    "cabecada/07": (AGACHADO, 0, 0, "foco"),
    # soco agachado: o último quadro de hoje levantava meio corpo; volta para o agachado
    "baixo_soco/07": (AGACHADO, 0, 0, "foco"),
}
# soco agachado: o desenho de hoje agacha mais raso que o agachado (o corpo subia 48% do caminho para o em pé); as
# coxas encurtam (dobram mais) entre a cintura e o tornozelo, o pé fica onde está
# e o desenho dele é uns 4% maior que o do agachado (régua da cabeça, reguas.escala_cabeca): volta ao tamanho dele
MAIS_FUNDO = {q: (0.88, 0.96) for q in ("baixo_soco/03", "baixo_soco/04", "baixo_soco/06")}
# golpes agachados: o fim do golpe volta para o agachado, não para o parado em pé
AGACHADAS = {400, 410, 430, 440}
_POSES = {}


def agachado():
    if not _POSES:
        _POSES.update(todas_poses())
    return {k: dict(v) for k, v in _POSES[AGACHADO].items() if not k.startswith("_")}


def volta_dobrada(quadros, passo=3):
    """Depois do contato, cada quadro dobrado segurado 6 tiques ou mais vira quadros do meio de `passo` tiques, com o
    tronco indo do ângulo do quadro anterior ao dele (quadros do meio na volta, regra do Alisson 17/11).
    Devolve (quadros, {índice: (graus, dx)})."""
    ultimo = max((i for i, e in enumerate(quadros) if e[2]), default=None)
    if ultimo is None:
        return quadros, {}
    novos, giro, ant = [], {}, None
    for i, (pose, t, cx, ch) in enumerate(quadros):
        q = ch.split("|")[0]
        d = DOBRA.get(q)
        if d and ant and i > ultimo and t >= 2 * passo and (d[1], d[2]) != ant:
            partes = t // passo
            for k in range(partes):
                f = (k + 1) / partes
                giro[len(novos)] = (ant[0] + (d[1] - ant[0]) * f, ant[1] + (d[2] - ant[1]) * f)
                novos.append((pose, passo if k < partes - 1 else t - passo * (partes - 1), cx, ch))
        else:
            novos.append((pose, t, cx, ch))
        if d:
            ant = (d[1], d[2])
    return novos, giro


def mais_fundo(a, fator):
    """Agacha mais fundo: a faixa entre a cintura (55% da altura, de cima) e o tornozelo (88%) encolhe na altura por
    `fator`; o que está acima desce junto e o pé não mexe. Vizinho mais próximo (pixel art)."""
    al = a[..., 3] > 0
    ys = np.nonzero(al.any(1))[0]
    y0, y1 = ys.min(), ys.max()
    c = y0 + 0.55 * (y1 - y0)
    t = y0 + 0.88 * (y1 - y0)
    c2 = t - fator * (t - c)
    y = np.arange(a.shape[0], dtype=np.float32)
    src = np.where(y < c2, y + (c - c2), np.where(y <= t, t - (t - y) / fator, y))
    return a[np.clip(np.round(src).astype(int), 0, a.shape[0] - 1)]


def dobrar(a, ang, dx=0, faixa=40):
    """O tronco do desenho dobra em volta da cintura (55% da altura, de cima): acima dela gira `ang` graus (+ = para a
    frente) e anda `dx`, crescendo suave na `faixa` (px) logo acima da cintura; abaixo nada muda. Vizinho mais próximo."""
    al = a[..., 3] > 0
    ys = np.nonzero(al.any(1))[0]
    cintura = int(ys.min() + 0.55 * (ys.max() - ys.min()))
    linha = np.nonzero(al[cintura])[0]
    cx = (linha.min() + linha.max()) / 2
    h, w = al.shape
    Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
    peso = np.clip((cintura - Y) / faixa, 0, 1)
    th = np.radians(-ang) * peso
    xs = X - dx * peso
    c, s_ = np.cos(th), np.sin(th)
    mx = (cx + (xs - cx) * c - (Y - cintura) * s_).astype(np.float32)
    my = (cintura + (xs - cx) * s_ + (Y - cintura) * c).astype(np.float32)
    return cv2.remap(np.ascontiguousarray(a), mx, my, cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


# Soco natural (regra do Alisson, 17/11) com a receita do estudo de anatomia (docs/estudo-anatomia-golpes.md, jab e
# direto): o quadril vai para a frente e o tronco inclina para o soco, o pé da frente dá um passo, o OMBRO anda para a
# frente (o alcance vem dele, nunca de esticar a peça), o braço da frente (lado longe) sai de trás do peito no contato
# ("_camada"), o calcanhar de trás levanta ("_ponta_tras", px) e o braço da garrafa vai para trás, longe do golpe.
# "_pes": quanto cada pé anda no chão (px HD, trás e frente) em relação ao parado.
ATRAS_BRACO = {"atras": "braco_frente"}
SOCO = {
    "soco/01": {"quadril": {"dx": 0, "dy": 2}, "cabeca": {"ang": 0, "var": "foco"},
                "braco_frente": {"ang": -8, "var": "punho"}, "_pes": (0, 0)},
    # antecipação: joelhos afundam, o peso vai para trás, o punho sai reto da guarda (sem descer)
    "soco/02": {"quadril": {"dx": -6, "dy": 6}, "tronco": {"ang": -5}, "cabeca": {"ang": -3, "var": "foco"},
                "braco_frente": {"ang": -24, "dx": -4, "var": "punho"}, "braco_tras": {"ang": 4}, "_pes": (0, 0)},
    "soco/03": {"quadril": {"dx": -4, "dy": 6}, "tronco": {"ang": -4}, "cabeca": {"ang": -3, "var": "foco"},
                "braco_frente": {"ang": -20, "dx": -4, "var": "punho"}, "braco_tras": {"ang": 4}, "_pes": (0, 0)},
    # contato: passo à frente, quadril e ombro entram (ombro anda 6 px; o resto vem do quadril e do tronco), braço esticado na altura do ombro saindo de
    # trás do peito, calcanhar de trás no ar, garrafa para trás, queixo atrás do ombro
    "soco/05": {"quadril": {"dx": 22, "dy": 8}, "tronco": {"ang": 8}, "cabeca": {"ang": 6, "dx": 2, "var": "esforco"},
                "braco_frente": {"ang": -8, "dx": 6, "dy": 1, "var": "esticado"}, "braco_tras": {"ang": -18},
                "_pes": (6, 30), "_camada": ATRAS_BRACO, "_ponta_tras": {"dy": 10}},
    # recolhe pelo mesmo caminho: o punho volta, o corpo ainda na frente
    "soco/06": {"quadril": {"dx": 14, "dy": 6}, "tronco": {"ang": 4}, "cabeca": {"ang": 3, "var": "foco"},
                "braco_frente": {"ang": -14, "dx": 3, "var": "punho"}, "braco_tras": {"ang": -8}, "_pes": (6, 30),
                "_ponta_tras": {"dy": 6}},
    # volta para a guarda trazendo o pé; o calcanhar assenta
    "soco/07": {"quadril": {"dx": 5, "dy": 2}, "tronco": {"ang": 1}, "cabeca": {"ang": 0, "var": "foco"},
                "braco_frente": {"ang": -8, "var": "punho"}, "braco_tras": {"ang": -2}, "_pes": (2, 12)},
}
# cabeçada em pé (303, 347, 3412, 3430): feita à mão, com o corpo firme; a agachada (410) sai do DOBRA
CABECADA = {
    # antecipação: puxa o tronco para trás, abaixa um pouco
    "cabecada/02": {"quadril": {"dx": -6, "dy": 6}, "tronco": {"ang": -8}, "cabeca": {"ang": -6, "var": "foco"},
                    "braco_frente": {"ang": -15, "var": "punho"}, "braco_tras": {"ang": -10}},
    "cabecada/03": {"quadril": {"dx": -10, "dy": 10}, "tronco": {"ang": -12}, "cabeca": {"ang": -10, "var": "foco"},
                    "braco_frente": {"ang": -5, "var": "punho"}, "braco_tras": {"ang": -15}},
    # bate: o corpo vai para a frente e a testa é o que chega primeiro; os braços ficam para trás
    "cabecada/04": {"quadril": {"dx": 16, "dy": 4}, "tronco": {"ang": 10}, "cabeca": {"ang": 12, "dx": 4, "var": "esforco"},
                    "braco_frente": {"ang": 30, "var": "punho"}, "braco_tras": {"ang": 12}},
    "cabecada/05": {"quadril": {"dx": 16, "dy": 4}, "tronco": {"ang": 10}, "cabeca": {"ang": 12, "dx": 4, "var": "esforco"},
                    "braco_frente": {"ang": 30, "var": "punho"}, "braco_tras": {"ang": 12}},
    # volta
    "cabecada/06": {"quadril": {"dx": 6, "dy": 2}, "tronco": {"ang": 5}, "cabeca": {"ang": 4, "var": "foco"},
                    "braco_frente": {"ang": 10, "var": "punho"}, "braco_tras": {"ang": 0}},
}


FEITAS = {**CABECADA, **SOCO}

# Chute com o corpo inteiro (regra 7.4): a perna do chute continua a do encaixe, mas o corpo acompanha. O quadril
# entra na direção do chute e sobe na ponta do pé de apoio, o tronco inclina para trás (contrapeso), a cabeça fica
# olhando o alvo, o braço de trás abre para equilibrar e o da frente guarda o rosto. Valores SOMADOS à pose encaixada
# (dx/dy em px HD, ang em graus); o pé de apoio volta a plantar por IK onde estava no desenho de hoje.
def _corpo(qdx, qdy, tronco, cabeca, btras, bfrente=0, bacia=0, atras=None):
    c = {"quadril": {"dx": qdx, "dy": qdy, "ang": bacia}, "tronco": {"ang": tronco}, "cabeca": {"ang": cabeca},
         "braco_tras": {"ang": btras}, "braco_frente": {"ang": bfrente}}
    if atras:
        c["_camada"] = {"atras": atras}
    return c


# estudo de anatomia (Parte 2): a perna do chute alto é a da frente, lado LONGE: a coxa nasce atrás da faixa e do
# tronco, e a mão da frente desce para trás da perna (a mão livre nunca tapa o golpe). Coxa acima da horizontal pede a
# bacia inclinada (o lado da perna sobe) e o tronco para trás.
LONGE = "braco_frente,perna_frente"


CORPO = {
    # chute alto: carrega (peso atrás), sobe o joelho, estica com o quadril entrando e o tronco deitando para trás
    "chute_alto/02": _corpo(-4, 2, -4, 2, -6, -6, atras=LONGE),
    "chute_alto/03": _corpo(4, 0, -6, 4, -14, 10, bacia=-2, atras=LONGE),
    "chute_alto/04": _corpo(12, -3, -7, 6, -20, 25, bacia=-5, atras=LONGE),
    "chute_alto/05": _corpo(9, -2, -6, 5, -16, 20, bacia=-4, atras=LONGE),
    "chute_alto/06": _corpo(3, 2, -5, 2, -8, -4, atras=LONGE),
    "chute_alto/07": _corpo(0, 0, -1, 0, -2),
    # chute baixo (de frente): o quadril empurra a perna, o tronco recua um pouco
    "chute_baixo/02": _corpo(8, -1, -7, 3, -14, -6),
    "chute_baixo/03": _corpo(2, 1, -3, 1, -6),
    "chute_baixo/04": _corpo(10, -2, -9, 4, -18, -8),
    "chute_baixo/05": _corpo(7, -1, -7, 3, -12, -6),
    "chute_baixo/06": _corpo(2, 1, -2, 0, -4),
}


def corpo_inteiro(p, q):
    """Soma o movimento do corpo (CORPO) na pose e planta de novo o pé de apoio."""
    for slot, d in CORPO[q].items():
        if slot.startswith("_"):
            p[slot] = dict(d)
            continue
        o = p.setdefault(slot, {"ang": 0})
        for k, v in d.items():
            o[k] = o.get(k, 0) + v
    return pf.pernas_no_chao(p, b.abrir(q), so_tras=True)


def plantar_pes(pose, dx_tras=0, dx_frente=0):
    """Pernas por IK com cada pé no chão, deslocado dx do pé do parado (o tornozelo de trás sobe com o calcanhar)."""
    w = b.mundo(pose)
    ponta = pose.get("_ponta_tras", {}).get("dy", 0)
    for coxa, canela, dx, dy in (("coxa_tras", "canela_tras", dx_tras, ponta), ("coxa_frente", "canela_frente", dx_frente, 0)):
        tr = pf.TORNOZELO[canela]
        c1, c2 = pf.ik(w[coxa][0], (tr[0] + dx, tr[1] - dy), b.OSSOS[canela][0], b.OSSOS[coxa][0], tr)
        pose[coxa] = {"ang": c1}
        pose[canela] = {"ang": c2}
    return pose


def feita(q):
    pose = {"quadril": {"ang": 0, "dx": 0, "dy": 0}}
    pes = FEITAS[q].get("_pes", (0, 0))
    for slot, v in FEITAS[q].items():
        if slot in ("_camada", "_ponta_tras"):
            pose[slot] = dict(v)
        elif not slot.startswith("_"):
            pose[slot] = dict({"ang": 0}, **v)
    return plantar_pes(pose, *pes)


def ajustar(pose, q):
    if q in FEITAS:
        return feita(q)
    p = {k: dict(v) for k, v in pose.items() if not k.startswith("_")}
    for slot, mud in AJUSTE.get(q, {}).items():
        p.setdefault(slot, {"ang": 0}).update(mud)
        if "var" in mud and mud["var"] is None:
            p[slot].pop("var")
    if q in CORPO:
        p = corpo_inteiro(p, q)
    return p


def acoes():
    a = json.loads(ACOES.read_text(encoding="utf-8"))
    out = {}
    for n, els in a.items():
        ds = [e for e in els if "desenho" in e]
        if ds and all(e["origem"] == "nova" for e in ds):
            out[int(n)] = [e for e in els if "desenho" in e]
    return out


def cinza(a):
    rgb = a[..., :3].astype(np.float32)
    rgb[a[..., 3] == 0] = 110.0
    return rgb


CORPO_FIRME_ATE = 10


def corpo_geral(kit, alvo):
    """(dx, dy, ang) do quadril para o peito do kit cair em cima do peito do desenho de hoje, em qualquer ângulo."""
    p = kit["pecas"]["tronco"]
    t = p["img"].copy()
    ox, oy = p["origem"]
    t[440 - oy:] = 0  # só ombro e peito
    jx, jy = b.OSSOS["tronco"][0]
    piv = (jx - ox, jy - oy)
    ys, xs = np.nonzero(alvo[..., 3] > 0)
    pad = 70
    X0, Y0 = max(0, xs.min() - pad), max(0, ys.min() - pad)
    X1, Y1 = min(alvo.shape[1], xs.max() + pad), min(alvo.shape[0], ys.max() + pad)
    base = cinza(alvo[Y0:Y1, X0:X1])
    melhor = None
    for ang in ANGULOS_CORPO:
        r, pv = b.rotsprite(t, ang, piv)
        m = (r[..., 3] > 0).astype(np.float32)
        if m.sum() < 50:
            continue
        res = cv2.matchTemplate(base, cinza(r), cv2.TM_SQDIFF, mask=np.repeat(m[..., None], 3, -1))
        res = res / (m.sum() * 3 * 255 * 255)
        v, _, loc, _ = cv2.minMaxLoc(res)
        v += GIRO_CUSTO * abs(ang) / 15
        if melhor is None or v < melhor[0]:
            melhor = (v, ang, (loc[0] + pv[0] + X0, loc[1] + pv[1] + Y0))
    v, ang, (px, py) = melhor
    # refino de 5 em 5 graus em volta do melhor
    for a2 in (ang - 10, ang - 5, ang + 5, ang + 10):
        r, pv = b.rotsprite(t, a2, piv)
        m = (r[..., 3] > 0).astype(np.float32)
        res = cv2.matchTemplate(base, cinza(r), cv2.TM_SQDIFF, mask=np.repeat(m[..., None], 3, -1))
        res = res / (m.sum() * 3 * 255 * 255)
        v2, _, loc, _ = cv2.minMaxLoc(res)
        v2 += GIRO_CUSTO * abs(a2) / 15
        if v2 < v:
            v, ang, (px, py) = v2, a2, (loc[0] + pv[0] + X0, loc[1] + pv[1] + Y0)
    if 0 < abs(ang) <= CORPO_FIRME_ATE:
        # corpo firme (escolha do Alisson): inclinação pequena não gira o tronco (girar abre fresta nas emendas do
        # quadril e do ombro); só translação
        r, pv = b.rotsprite(t, 0, piv)
        m = (r[..., 3] > 0).astype(np.float32)
        res = cv2.matchTemplate(base, cinza(r), cv2.TM_SQDIFF, mask=np.repeat(m[..., None], 3, -1))
        res = res / (m.sum() * 3 * 255 * 255)
        v, _, loc, _ = cv2.minMaxLoc(res)
        ang, (px, py) = 0, (loc[0] + pv[0] + X0, loc[1] + pv[1] + Y0)
    # quadril: o peito gira em volta da junta do tronco, que é filha do quadril
    qx, qy = b.OSSOS["quadril"][0]
    g = b.girar((jx, jy), (qx, qy), ang)
    return {"ang": ang, "dx": px - g[0], "dy": py - g[1]}, float(v)


def expressao(acao_nome, bate):
    if acao_nome in DOR:
        return "dor"
    if acao_nome in RISO:
        return "riso"
    if bate:
        return "esforco"
    if acao_nome in ("ginga", "anda", "corre", "recuo", "agachado", "defesa", "pulo"):
        return None
    return "foco"


def pose_de(kit, q, expr):
    alvo = b.abrir(q)
    quadril, nota = corpo_geral(kit, alvo)
    pose = {"quadril": quadril}
    if expr:
        pose["cabeca"] = {"ang": 0, "var": expr}
    angs, folga, _ = b.BUSCA["braco_frente"]
    b.BUSCA["braco_frente"] = (range(-60, 61, 3), 4, [None, "punho", "esticado"])
    b.BUSCA["braco_tras"] = (range(-60, 61, 3), 3, [None])
    pose = b.encaixar(kit, alvo, pose, ordem=["braco_tras", "braco_frente"])
    em_pe = abs(quadril["ang"]) <= 20
    no_chao = (alvo[..., 3] > 0).any(1).nonzero()[0].max() >= 655 and len(pf.pes(alvo)) >= 1
    if q in pf.PERNA:
        giro = range(-4, 5, 1) if pf.PERNA[q] == "agachada" else range(-30, 31, 2)
        b.BUSCA["coxa_frente"] = (giro, 2, [pf.PERNA[q]])
        b.ANGULOS_VARIANTE = giro
        pose = b.encaixar(kit, alvo, pose, ordem=["coxa_frente"])
        pose = pf.pernas_no_chao(pose, alvo, so_tras=True)
    elif em_pe and no_chao and len(pf.pes(alvo)) >= 2:
        pose = pf.pernas_no_chao(pose, alvo)
    else:
        for s in ("coxa_tras", "canela_tras", "coxa_frente", "canela_frente"):
            b.BUSCA[s] = (range(-70, 71, 3), 2, [None])
        if em_pe and no_chao:
            pose = pf.pernas_no_chao(pose, alvo, so_tras=True)
            pose = b.encaixar(kit, alvo, pose, ordem=["coxa_frente", "canela_frente"])
        else:
            pose = b.encaixar(kit, alvo, pose, ordem=["coxa_tras", "canela_tras", "coxa_frente", "canela_frente"])
    pose["_nota_corpo"] = round(nota, 4)
    # nota da montagem: quanto a silhueta do boneco cobre a do desenho de hoje (IoU). Abaixo do limite, a pose não
    # cabe no kit de frente (deitado, de cabeça para baixo, de costas) e o quadro vira "especial"
    m = pf.desenhar(kit, {k: v for k, v in pose.items() if not k.startswith("_")})[..., 3] > 0
    o = alvo[..., 3] > 0
    pose["_iou"] = round(float((m & o).sum() / max(1, (m | o).sum())), 3)
    return pose


def acertar_repouso(kit):
    """Calça e faixa entre a cintura e o joelho: o kit montado parado (todos os ossos no lugar) tem que ser o desenho
    ginga/00 de onde ele foi recortado. A separação das bolinhas e o tapa-buraco da coxa (separar_pes) deixavam na
    virilha um retângulo escuro, riscos e borrão verde (sobra do Pengaró, 24/11). Cada pixel dessa faixa que sai
    diferente vai para a peça que fica por cima nele, com a cor do desenho; o que falta entra no quadril."""
    import pele_pecas as pele
    orig = b.abrir("ginga/00")
    ys, xs = np.nonzero(orig[..., 3] > 0)
    y0 = ys.min()
    faixa = np.zeros(orig.shape[:2], bool)
    faixa[y0 + 120:y0 + 270] = True
    pose = {"quadril": {"ang": 0}}
    camadas = pele.CAMADAS
    dono = np.full(orig.shape[:2], "", dtype=object)
    sozinha = {}
    try:
        for cam in camadas:
            for slot, viz in cam[1]:
                pele.CAMADAS = [(cam[0], [(slot, viz)])]
                r = pele.desenhar(kit, pose)
                sozinha[slot] = r
                dono[r[..., 3] > 0] = slot
    finally:
        pele.CAMADAS = camadas
        kit.pop("_pontos", None)
    # contorno escuro de quem está por cima (mão, garrafa, outra perna) ficou pintado na calça de baixo: quando a peça
    # de cima sai do lugar ele aparece como risco preto. Na calça (quadril e coxas), escuro escondido vira a calça
    # clara mais perto da mesma peça
    for slot in ("quadril", "coxa_tras", "coxa_frente"):
        r = sozinha.get(slot)
        if r is None:
            continue
        rgb_r = r[..., :3].astype(int)
        al = r[..., 3] > 0
        clara = al & (rgb_r.min(-1) > 140) & (np.ptp(rgb_r, -1) < 100)
        escondido = al & (dono != slot) & faixa & (rgb_r.sum(-1) < 330)
        escondido &= cv2.erode(al.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0  # a beira da peça fica
        if not escondido.any() or not clara.any():
            continue
        _, lab = cv2.distanceTransformWithLabels((~clara).astype(np.uint8), cv2.DIST_L2, 5,
                                                 labelType=cv2.DIST_LABEL_PIXEL)
        fy, fx = np.nonzero(clara)
        idx = np.zeros(lab.max() + 1, int)
        idx[lab[fy, fx]] = np.arange(len(fy))
        p = kit["pecas"][slot]
        img = p["img"].copy()
        ox, oy = p["origem"]
        yy, xx = np.nonzero(escondido)
        k = idx[lab[yy, xx]]
        ly, lx = yy - oy, xx - ox
        ok = (ly >= 0) & (lx >= 0) & (ly < img.shape[0]) & (lx < img.shape[1])
        img[ly[ok], lx[ok], :3] = r[fy[k[ok]], fx[k[ok]], :3]
        p["img"] = img
    kit.pop("_pontos", None)
    q = kit["pecas"]["quadril"]
    bol = np.zeros(orig.shape[:2], bool)
    by, bx = np.nonzero(kit["bolinhas"][..., 3] > 0)
    bol[by + q["origem"][1], bx + q["origem"][0]] = True
    tem = orig[..., 3] > 0
    for slot in {d for d in dono[faixa & ~bol].ravel() if d}:
        p = kit["pecas"][slot]
        img = p["img"].copy()
        ox, oy = p["origem"]
        m = faixa & ~bol & (dono == slot)
        yy, xx = np.nonzero(m)
        ly, lx = yy - oy, xx - ox
        ok = (ly >= 0) & (lx >= 0) & (ly < img.shape[0]) & (lx < img.shape[1])
        yy, xx, ly, lx = yy[ok], xx[ok], ly[ok], lx[ok]
        dentro = tem[yy, xx]
        img[ly[dentro], lx[dentro]] = orig[yy[dentro], xx[dentro]]
        img[ly[~dentro], lx[~dentro], 3] = 0
        p["img"] = img
    # embaixo das bolinhas (quando elas balançam aparece): calça lisa, puxada só da calça clara em volta (o contorno
    # escuro não entra na pintura, senão vira o borrão cinza)
    kit.pop("_pontos", None)
    tela = pele.desenhar(kit, pose)
    kit.pop("_pontos", None)
    rgb = tela[..., :3].astype(int)
    escuro = rgb.sum(-1) < 330
    perto = cv2.dilate(bol.astype(np.uint8), np.ones((13, 13), np.uint8)) > 0
    sob = (cv2.dilate(bol.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) | (perto & escuro)
    sob &= (tela[..., 3] > 0) & (dono != "")
    if sob.any():
        # cor do pixel de calça clara mais perto (nada de verde da faixa nem contorno), depois um borrão leve só ali
        hsv = cv2.cvtColor(np.ascontiguousarray(tela[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
        verde = (hsv[..., 0] >= 40) & (hsv[..., 0] <= 95) & (hsv[..., 1] > 80) & (hsv[..., 2] > 70)
        clara = ((rgb.min(-1) > 140) & (np.ptp(rgb, -1) < 100) | verde) & (tela[..., 3] > 0) & ~sob
        _, lab = cv2.distanceTransformWithLabels((~clara).astype(np.uint8), cv2.DIST_L2, 5,
                                                 labelType=cv2.DIST_LABEL_PIXEL)
        fy, fx = np.nonzero(clara)
        idx = np.zeros(lab.max() + 1, int)
        idx[lab[fy, fx]] = np.arange(len(fy))
        pint = tela[..., :3].copy()
        yy, xx = np.nonzero(sob)
        k = idx[lab[yy, xx]]
        pint[yy, xx] = tela[fy[k], fx[k], :3]
        liso = cv2.GaussianBlur(pint, (5, 5), 0)
        pint[yy, xx] = liso[yy, xx]
        for slot in {d for d in dono[sob].ravel()}:
            p = kit["pecas"][slot]
            img = p["img"].copy()
            ox, oy = p["origem"]
            yy, xx = np.nonzero(sob & (dono == slot))
            ly, lx = yy - oy, xx - ox
            ok = (ly >= 0) & (lx >= 0) & (ly < img.shape[0]) & (lx < img.shape[1])
            img[ly[ok], lx[ok], :3] = pint[yy[ok], xx[ok]]
            p["img"] = img
    falta = faixa & ~bol & tem & (dono == "")
    if falta.any():
        img = q["img"].copy()
        yy, xx = np.nonzero(falta)
        ly, lx = yy - q["origem"][1], xx - q["origem"][0]
        ok = (ly >= 0) & (lx >= 0) & (ly < img.shape[0]) & (lx < img.shape[1])
        img[ly[ok], lx[ok]] = orig[yy[ok], xx[ok]]
        q["img"] = img
    return kit


def preparar():
    pf.PELE = True  # sem linha de corte entre as peças (regra 7.4)
    kit = acertar_repouso(pf.separar_pes(b.ler_kit()))
    b.FOLGA_VARIANTE = {"coxa_frente": 3}
    pf.MANCHA_REF = pf.mancha_ref()
    if pf.PELE:  # base do robô: o que o próprio desenho em pele dá no parado (contorno das juntas conta como sombra)
        t = pf.desenhar(kit, {"quadril": {"ang": 0}})
        al = t[..., 3] > 0
        g = cv2.erode(((t[..., :3].astype(int).sum(-1) < 110) & al).astype(np.uint8), np.ones((4, 4), np.uint8))
        pf.MANCHA_REF = max(pf.MANCHA_REF, int(g[np.nonzero(al.any(1))[0].min() + 80:].sum()))
    return kit


ESPECIAL = {}
# desenhos do chute baixo (430) e da rasteira (440): o corpo inteiro é ~1,3x o parado (o Alisson escolheu manter o
# tamanho, 24/11). A cabeça é achada numa faixa de escala mais larga e a do kit entra na escala do desenho, para o
# rosto ser sempre o do kit (Breno, 24/11: "o Pengaró muda muito a cara dele")
ROSTO_NA_ESCALA = ("rasteirinha/", "rasteira/")


# desenhos que saem sempre do próprio desenho (com o rosto do kit), mesmo quando o kit monta a pose
PELO_DESENHO = ()  # com o kit acertado no repouso (acertar_repouso) a ginga montada ficou limpa: segue no kit
PELE_PARADO = (179, 72, 50)   # medido no parado já na paleta travada (o quadro sai ~3 acima do alvo)


def pele_do_parado(a):
    """O chute baixo e a rasteira foram desenhados com a pele mais clara e alaranjada que o parado (peito ~181,84,61):
    a pele do quadro inteiro é levada para o tom do parado, para a cabeça do kit não destoar do corpo."""
    rgb = a[..., :3].astype(float)
    soma = rgb.sum(-1)
    pele = (a[..., 3] > 0) & (rgb[..., 0] > rgb[..., 2] + 30) & (soma > 150) & (soma < 600) & (rgb[..., 1] < rgb[..., 0] * 0.7)
    if pele.sum() < 500:
        return a
    f = np.array(PELE_PARADO) / rgb[pele].mean(0)
    out = a.copy()
    out[pele, :3] = np.clip(rgb[pele] * f, 0, 255).astype(np.uint8)
    return out


def especial(q, expr):
    """Quadro que não cabe no kit de frente: o desenho de hoje, com o rosto do kit (mesmo rosto e tamanho, na
    expressão do golpe) e a pele e a roupa puxadas para a paleta do parado (cor travada)."""
    if not ESPECIAL:
        tmpl, caixa = cc.referencia()
        ESPECIAL["tmpl"], ESPECIAL["caixa"] = tmpl, caixa
        ESPECIAL["cab"] = {n: cc.cabeca_do_kit(n, tmpl, caixa) for n in cc.EXPRESSOES}
        ESPECIAL["refcor"] = cores.RefCor([str(cc.REF)])
        ref = cc.abrir(cc.REF)
        ESPECIAL["pal"] = pc.paleta_do_parado(ref, [ref])
    a = b.abrir(q)
    try:
        larga = q.startswith(ROSTO_NA_ESCALA)
        if larga:
            a = pele_do_parado(a)
        out, info = cc.trocar(a, ESPECIAL["tmpl"], ESPECIAL["caixa"], ESPECIAL["cab"][expr or "guarda"],
                              escalas=cc.ESCALAS_LARGAS if larga else None, acompanhar=True)
        # a máscara da cabeça velha pega o que encosta nela (braço levantado, garrafa): o que sumiu longe da
        # cabeça nova volta como estava; migalha que ficou solta do cabelo velho sai
        perdido = ((a[..., 3] > 0) & (out[..., 3] == 0)).astype(np.uint8)
        if (cv2.erode(perdido, np.ones((7, 7), np.uint8)) > 0).sum() > 100:
            raise ValueError("a cabeça nova não cobre a velha (cabeça muito inclinada ou com braço na frente)")
        longe = cv2.dilate(info["cabeca"].astype(np.uint8), np.ones((25, 25), np.uint8)) == 0
        volta = longe & (a[..., 3] > 0) & (out[..., 3] == 0)
        out[volta] = a[volta]
        out = pf.sem_migalha(out, 150)
    except Exception:  # cabeça não achada (de costas, escondida): fica a do desenho
        out = a
    return cores.pintar_na_paleta(ESPECIAL["refcor"].corrigir(out), ESPECIAL["pal"])


def cmd_poses(so=None, parte=0, partes=1):
    """Pose-chave de cada desenho (uma vez por desenho; a expressão entra depois). Com partes > 1, cada processo faz
    uma fatia e grava poses_<parte>.json (cmd_animar junta)."""
    kit = preparar()
    DOCS.mkdir(parents=True, exist_ok=True)
    cache = DOCS / (f"poses_{parte}.json" if partes > 1 else "poses.json")
    poses = json.loads(cache.read_text()) if cache.exists() else {}
    desenhos = sorted({e["desenho"].removesuffix(".png") for els in acoes().values() for e in els})
    desenhos = [q for k, q in enumerate(desenhos) if k % partes == parte]
    for i, q in enumerate(desenhos):
        if so and q not in so:
            continue
        if q in poses and not so:
            continue
        poses[q] = pose_de(kit, q, None)
        cache.write_text(json.dumps(poses, indent=1), encoding="utf-8")
        print(f"[{i + 1}/{len(desenhos)}] {q} corpo ang {poses[q]['quadril']['ang']} "
              f"nota {poses[q]['_nota_corpo']} iou {poses[q]['_iou']}", flush=True)


def todas_poses():
    poses = {}
    for f in sorted(DOCS.glob("poses*.json")):
        poses.update(json.loads(f.read_text()))
    return poses


def juntar(els):
    """Elementos seguidos com o mesmo desenho e a mesma caixa viram um só (os ticks somam)."""
    out = []
    for e in els:
        if out and out[-1]["desenho"] == e["desenho"] and out[-1]["bate"] == e["bate"] and e["ticks"] > 0 \
                and out[-1]["ticks"] > 0:
            out[-1] = dict(out[-1], ticks=out[-1]["ticks"] + e["ticks"])
        else:
            out.append(dict(e))
    return out


# Andar: os desenhos de hoje trocam a perna da joelheira de lado a cada passo (o kit tem uma perna de trás e uma da
# frente fixas), então o andar sai por código: cada pé faz o ciclo apoio (desliza para trás no chão) e balanço (sobe e
# vai para a frente), as pernas por IK, o quadril desce um pouco quando os dois pés apoiam e os braços balançam.
PASSO_PX = 66      # tamanho do passo no HD (22 px do jogo); o andar do jogo usa ANDAR_JOGO
SOBE_PE = 30       # altura do pé no balanço
DESCE_QUADRIL = 6  # quanto o quadril desce no apoio duplo
ANDAR = {20: 1, 21: -1}  # ação -> sentido (1 frente, -1 trás)
# O pé de apoio não pode deslizar no chão: ele anda para trás na tela na mesma velocidade em que o lutador anda para a
# frente (walk.fwd 2.7 e walk.back 2.2 px do jogo por tique = 8.1 e 6.6 px no HD). O tempo da ação fica o de hoje
# (34 tiques, o jogo liga sem mudar tempo): são 2 passadas por volta, meio ciclo de 8,5 tiques, passo = velocidade x 8,5.
ANDAR_JOGO = {20: (8.1 * 8.5, 34, 2), 21: (6.6 * 8.5, 34, 2)}  # ação -> (passo HD, tiques, passadas por volta)


def andar(sentido, ticks_total, passo=None, passadas=1):
    passo = passo or PASSO_PX
    quadros = []
    n = ticks_total // 2
    qr = {c: b.OSSOS[c][0] for c in ("coxa_tras", "coxa_frente")}
    for i in range(n):
        fase = ((i / n) if sentido > 0 else (1 - i / n)) * passadas % 1
        dy = DESCE_QUADRIL * (0.5 + 0.5 * np.cos(4 * np.pi * fase))
        pose = {"quadril": {"ang": 0, "dx": 0, "dy": dy}}
        w = b.mundo(pose)
        for coxa, canela, desloc in (("coxa_tras", "canela_tras", 0.0), ("coxa_frente", "canela_frente", 0.5)):
            f = (fase + desloc) % 1
            if f < 0.5:  # apoio
                x, y = passo / 2 - passo * (f / 0.5), 0.0
            else:  # balanço
                u = (f - 0.5) / 0.5
                x = -passo / 2 + passo * vida.suave(u)
                y = -SOBE_PE * np.sin(np.pi * u)
            tr = pf.TORNOZELO[canela]
            c1, c2 = pf.ik(w[coxa][0], (tr[0] + x, tr[1] + y), b.OSSOS[canela][0], qr[coxa], tr)
            pose[coxa] = {"ang": c1}
            pose[canela] = {"ang": c2}
        balanco = 6 * np.sin(2 * np.pi * fase)
        pose["braco_tras"] = {"ang": balanco}
        pose["braco_frente"] = {"ang": -balanco * 0.6 - 8, "var": "punho"}
        quadros.append((pose, 2, False, "anda|None"))
    return quadros


def dobra_funda(pose):
    """Agachado fundo, pernas encolhidas: o joelho vem para a frente (na direção de quem olha) e as peças de lado do
    kit não encurtam; montado, a calça rasga e a perna dobra para trás. Esses quadros ficam especiais."""
    nz = lambda a: (a + 180) % 360 - 180
    coxas = [abs(nz(pose[s]["ang"])) for s in ("coxa_tras", "coxa_frente") if s in pose and not pose[s].get("var")]
    canelas = [abs(nz(pose[s]["ang"])) for s in ("canela_tras", "canela_frente") if s in pose]
    return any(a > 70 for a in coxas) or any(a > 100 for a in canelas)


MEMBRO_PERDIDO_PX = 800
PERDIDO_CACHE = {}


def membro_perdido(kit, q, pose):
    """Parte do desenho de hoje que a montagem não cobre nem de perto (15 px): é braço ou perna que o encaixe não
    alcançou (chute que vira pose parada, braço da bola que não sobe). Acima do limite o quadro fica especial."""
    if q not in PERDIDO_CACHE:
        o = b.abrir(q)[..., 3] > 0
        m = (pf.desenhar(kit, pose)[..., 3] > 0).astype(np.uint8)
        falta = o & (cv2.dilate(m, np.ones((15, 15), np.uint8)) == 0)
        n, _, st, _ = cv2.connectedComponentsWithStats(falta.astype(np.uint8))
        PERDIDO_CACHE[q] = int(st[1:, 4].max()) if n > 1 else 0
    return PERDIDO_CACHE[q] > MEMBRO_PERDIDO_PX


PLANTA_CACHE = {}


def plantar(kit, pose, q):
    """Confere a pose-chave montada. Pé fora do chão (hoje ele está no chão): as pernas saem por IK até o pé de hoje.
    Devolve False quando ainda sobra defeito (aí o quadro vira especial). Mexe na pose no lugar."""
    chave = (q, json.dumps(pose, sort_keys=True))
    if chave in PLANTA_CACHE:
        ok, nova = PLANTA_CACHE[chave]
        pose.clear(); pose.update(json.loads(nova))
        return ok
    alvo = b.abrir(q)
    limpa = lambda p: {k: v for k, v in p.items() if not k.startswith("_")}
    erros = pf.conferir(pf.desenhar(kit, limpa(pose)), alvo, None)
    if any(e.startswith("chão") for e in erros):
        tenta = json.loads(json.dumps(pose))
        pf.pernas_no_chao(tenta, alvo, so_tras=q in pf.PERNA)
        e2 = pf.conferir(pf.desenhar(kit, limpa(tenta)), alvo, None)
        if len(e2) < len(erros):
            pose.clear(); pose.update(tenta)
            erros = e2
    ok = not erros
    PLANTA_CACHE[chave] = (ok, json.dumps(pose))
    return ok


def cmd_animar(so=None):
    kit = preparar()
    poses = todas_poses()
    relatorio = ["| ação | desenhos | defeitos |", "|---|---|---|"]
    for n, els in sorted(acoes().items()):
        if so and n not in so:
            continue
        els = juntar(els)
        chaves = []
        pp = {}
        q_bate = None
        for e in els:
            q = e["desenho"].removesuffix(".png")
            ex = expressao(q.split('/')[0], e["bate"])
            if e["bate"]:
                q_bate = q
            elif q == q_bate and ex == "foco":
                ex = "esforco"  # o mesmo desenho do contato segurado mantém o esforço (rosto não pisca para o foco)
            else:
                q_bate = None
            ch = f"{q}|{ex}"
            pp[ch] = ajustar(dict(poses[q], **({"cabeca": {"ang": 0, "var": ex}} if ex else {})), q)
            chaves.append((ch, max(e["ticks"], 1) if e["ticks"] >= 0 else 1, e["bate"]))
        elems = [(c, t) for c, t, _ in chaves]
        fixos = {c for c, _, _ in chaves if PELO_DESENHO and c.split("|")[0].startswith(PELO_DESENHO)}
        fixos |= {c for c, _, _ in chaves if (poses[c.split("|")[0]].get("_iou", 1) < IOU_MINIMO
                 or dobra_funda(poses[c.split("|")[0]])) and c.split("|")[0] not in AJUSTE and c.split("|")[0] not in FEITAS}
        for c in {c for c, _, _ in chaves} - fixos:
            q0 = c.split("|")[0]
            if q0 not in AJUSTE and q0 not in FEITAS and q0 not in pf.PERNA and membro_perdido(kit, q0, pp[c] if q0 not in CORPO else {k: v for k, v in poses[q0].items() if not k.startswith("_")}):
                fixos.add(c)
                continue
            if not plantar(kit, pp[c], c.split("|")[0]):
                fixos.add(c)  # pose-chave que o kit não monta sem defeito vira quadro especial
        # o tronco dobrado e o agachar mais fundo são só dos golpes agachados: os golpes em pé que usam os mesmos
        # desenhos (cabeçada 303, 347, 3412, 3430) ficam como o desenho
        dobra = DOBRA if n in AGACHADAS else {}
        fundo = MAIS_FUNDO if n in AGACHADAS else {}
        fixos |= {c for c, _, _ in chaves if c.split("|")[0] in dobra}
        bate = next((k for k, (_, _, bt) in enumerate(chaves) if bt), None)
        laco = n in LACOS
        volta = agachado() if n in AGACHADAS else {}
        quadros = vida.animar(pp, elems, bate=bate, laco=laco, guarda=None if laco else volta, fixos=fixos)
        if n in ANDAR:
            fixos = set()
            quadros = andar(ANDAR[n], ANDAR_JOGO[n][1], ANDAR_JOGO[n][0], ANDAR_JOGO[n][2])
        if n in (0, 5):
            quadros = vida.respirar(quadros)
        quadros = vida.atrasar(quadros, laco=laco)
        quadros, giro = volta_dobrada(quadros) if dobra else (quadros, {})
        for pasta in (SAIDA / str(n), SAIDA_1X / str(n)):
            shutil.rmtree(pasta, ignore_errors=True)
            pasta.mkdir(parents=True)
        defeitos = []
        originais = {}
        for i, (pose, t, cx, ch) in enumerate(quadros):
            q, ex = ch.split("|")
            if q == "anda":
                q = "ginga/00"  # andar feito por código: o robô compara com o parado (pés no chão)
            if q in dobra:
                base, ang, dx, ex_ = dobra[q]
                ang, dx = giro.get(i, (ang, dx))
                out = dobrar(especial(base, ex_), ang, dx)
                originais.setdefault(q, b.abrir(base))
            elif ch in fixos:
                out = especial(q, None if ex == "None" else ex)
                if q in fundo:
                    from firme import na_tela
                    out = na_tela(mais_fundo(out, MAIS_FUNDO[q][0]), MAIS_FUNDO[q][1])
            else:
                out = pf.desenhar(kit, pose)
            originais.setdefault(q, b.abrir(q))
            erros = pf.conferir(out, originais[q], None)
            if ch not in fixos and any(e.startswith("chão") for e in erros):
                # intermediário com o pé fora do chão: as pernas plantam por IK no pé do desenho de onde ele sai
                p2 = json.loads(json.dumps(pose))
                pf.pernas_no_chao(p2, originais[q], so_tras=q in pf.PERNA)
                out2 = pf.desenhar(kit, p2)
                e2 = pf.conferir(out2, originais[q], None)
                if len(e2) < len(erros):
                    out, erros = out2, e2
            if ch not in fixos and erros and ch in pp:
                # intermediário que ainda tem defeito: fica a pose-chave de onde ele sai (segura um tique a mais)
                out2 = pf.desenhar(kit, pp[ch])
                e2 = pf.conferir(out2, originais[q], None)
                if not e2:
                    out, erros = out2, e2
            if ch in fixos:  # quadro especial é o desenho de hoje: só conta o que a troca de rosto e cor criou
                antes = pf.conferir(originais[q], originais[q], None)
                erros = [e for e in erros if not e.startswith("mancha")
                         and not (e.startswith("solta") and any(a.startswith("solta") for a in antes))]
            if erros:
                defeitos.append(f"{i:02d} ({q}): {'; '.join(erros)}")
            Image.fromarray(out).save(SAIDA / str(n) / f"{i:02d}.png")
            Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(SAIDA_1X / str(n) / f"{i:02d}.png")
        tempos = {"acao": n, "elementos": [{"desenho": i, "ticks": t, "caixa": c, "de": ch}
                                          for i, (_, t, c, ch) in enumerate(quadros)]}
        (SAIDA / str(n) / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False), encoding="utf-8")
        relatorio.append(f"| {n} | {len(quadros)} ({len(fixos)} especiais) | {'PASS' if not defeitos else '<br>'.join(defeitos)} |")
        print(n, len(quadros), "desenhos", "PASS" if not defeitos else f"{len(defeitos)} com defeito", flush=True)
    if so and (DOCS / "robo_defeitos.md").exists():
        # rodada parcial: as outras ações ficam com a linha da última rodada completa
        feitas = {l.split("|")[1].strip() for l in relatorio[2:]}
        velhas = [l for l in (DOCS / "robo_defeitos.md").read_text(encoding="utf-8").splitlines()[2:]
                  if l.startswith("| ") and l.split("|")[1].strip() not in feitas]
        relatorio = relatorio[:2] + sorted(relatorio[2:] + velhas, key=lambda l: int(l.split("|")[1]))
    falhas = sum("PASS" not in l for l in relatorio[2:])
    texto = "\n".join(relatorio) + f"\n\n{falhas} ação(ões) com defeito.\n"
    (DOCS / "robo_defeitos.md").write_text(texto, encoding="utf-8")
    print(f"{falhas} ação(ões) com defeito")


def cmd_folha():
    fonte = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    pastas = sorted((p for p in SAIDA.iterdir() if p.is_dir()), key=lambda p: int(p.name))
    W, H, col = 120, 110, 14
    for parte in range(0, len(pastas), 20):
        grupo = pastas[parte:parte + 20]
        im = Image.new("RGB", (60 + col * W, len(grupo) * H), (40, 40, 48))
        d = ImageDraw.Draw(im)
        for r, p in enumerate(grupo):
            d.text((4, r * H + 45), p.name, fill=(255, 230, 120), font=fonte)
            fs = sorted(p.glob("[0-9][0-9].png"))
            passo = max(1, len(fs) // col + (len(fs) % col > 0))
            for c, f in enumerate(fs[::passo][:col]):
                a = Image.open(f).convert("RGBA")
                bg = Image.new("RGBA", a.size, (60, 60, 70, 255))
                bg.alpha_composite(a)
                cr = bg.crop((300, 200, 780, 670))
                cr.thumbnail((W - 4, H - 4))
                im.paste(cr.convert("RGB"), (60 + c * W, r * H))
        im.save(DOCS / f"folha_{parte // 20:02d}.png")


def cmd_revisar():
    """Folha de revisão: cada desenho montado (IoU >= limite) ao lado do desenho de hoje, para olhar peça por peça."""
    kit = preparar()
    poses = todas_poses()
    qs = sorted(q for q, p in poses.items()
                if (p.get("_iou", 0) >= IOU_MINIMO and not dobra_funda(p)
                    and (q in pf.PERNA or not membro_perdido(kit, q, ajustar(p, q)))) or q in AJUSTE or q in FEITAS)
    fonte = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    W, H, col = 300, 240, 6
    for parte in range(0, len(qs), 24):
        grupo = qs[parte:parte + 24]
        im = Image.new("RGB", (col * W, ((len(grupo) + col - 1) // col) * H), (40, 40, 48))
        d = ImageDraw.Draw(im)
        for k, q in enumerate(grupo):
            x, y = (k % col) * W, (k // col) * H
            hoje = b.abrir(q)
            mont = pf.desenhar(kit, ajustar(poses[q], q))
            for j, a in enumerate((hoje, mont)):
                bg = Image.new("RGBA", (a.shape[1], a.shape[0]), (60, 60, 70, 255))
                bg.alpha_composite(Image.fromarray(a))
                cr = bg.crop((330, 220, 750, 680))
                cr.thumbnail((W // 2 - 2, H - 18))
                im.paste(cr.convert("RGB"), (x + j * (W // 2), y + 16))
            d.text((x + 4, y + 1), f"{q}  iou {poses[q].get('_iou')}", fill=(255, 230, 120), font=fonte)
        im.save(DOCS / f"revisao_{parte // 24:02d}.png")


VIDEO_ACOES = [(0, "parado"), (20, "andar (refeito por código)"), (200, "soco"), (240, "chute alto"),
               (410, "cabeçada (refeita à mão)"), (600, "soco no ar"), (130, "defesa"), (195, "provocação"),
               (1000, "bola"), (11, "agachar")]


def cmd_video(saida):
    """Vídeo lado a lado (hoje x boneco de peças) das ações da lista, uma atrás da outra, a 60 fps."""
    import subprocess
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    fonte = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    todas = acoes()
    corte = (380, 250, 760, 670)
    w, h = corte[2] - corte[0], corte[3] - corte[1]

    def q_img(arq):
        f = Image.open(arq).convert("RGBA")
        bg = Image.new("RGBA", f.size, (60, 60, 70, 255))
        bg.alpha_composite(f)
        return bg.crop(corte).convert("RGB")

    tmp = saida / "_quadros"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir()
    k = 0
    for n, nome in VIDEO_ACOES:
        if n not in todas or not (SAIDA / str(n) / "tempos.json").exists():
            continue
        hoje = []
        for e in todas[n]:
            hoje += [SPR / "quadros_arcade_hd" / e["desenho"]] * max(e["ticks"], 1)
        tempos = json.loads((SAIDA / str(n) / "tempos.json").read_text(encoding="utf-8"))
        novo = []
        for e in tempos["elementos"]:
            novo += [SAIDA / str(n) / f"{e['desenho']:02d}.png"] * e["ticks"]
        total = max(len(hoje), len(novo))
        hoje += [hoje[-1]] * (total - len(hoje))
        novo += [novo[-1]] * (total - len(novo))
        voltas = max(2, 150 // total)
        cache = {}
        for v in range(voltas):
            for a, b_ in zip(hoje, novo):
                if (a, b_) not in cache:
                    img = Image.new("RGB", (w * 2, h + 34), (40, 40, 48))
                    img.paste(q_img(a), (0, 34))
                    img.paste(q_img(b_), (w, 34))
                    d = ImageDraw.Draw(img)
                    d.text((8, 6), f"{nome}: hoje", fill=(255, 230, 120), font=fonte)
                    d.text((w + 8, 6), "boneco de peças", fill=(140, 255, 160), font=fonte)
                    cache[(a, b_)] = img
                cache[(a, b_)].save(tmp / f"{k:06d}.png")
                k += 1
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "60", "-i", str(tmp / "%06d.png"),
                    "-vf", "scale=iw*2:ih*2:flags=neighbor", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                    str(saida / "pengaro_lado_a_lado.mp4")], check=True)
    shutil.rmtree(tmp)


if __name__ == "__main__":
    cmd, resto = sys.argv[1], sys.argv[2:]
    if cmd == "poses":
        if resto and "/" in resto[0] and resto[0].replace("/", "").isdigit():
            i, n = map(int, resto[0].split("/"))
            cmd_poses(None, i, n)
        else:
            cmd_poses(set(resto) or None)
    elif cmd == "animar":
        cmd_animar({int(x) for x in resto} or None)
    elif cmd == "folha":
        cmd_folha()
    elif cmd == "revisar":
        cmd_revisar()
    elif cmd == "video":
        cmd_video(resto[0] if resto else DOCS)
