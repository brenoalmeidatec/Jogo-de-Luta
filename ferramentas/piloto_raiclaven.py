#!/usr/bin/env python3
"""Raiclaven no boneco de peças, "corpo firme + vida" (o método aprovado pelo Alisson no Pengaró, 16/11).

Tronco, rosto e pele vêm sempre do mesmo desenho (o parado arcade, ginga/00) em cor cheia; braços, pente, tesoura e
pernas são as peças do kit (ferramentas/pecas_raiclaven.py) giradas nas juntas. Diferente do Pengaró, as poses aqui
são montadas à mão (ângulo por junta): o soco e o chute de hoje vêm de uma folha antiga com outro corpo e outro
tamanho, e o encaixe automático em cima deles saía torto. O desenho de hoje serve só de guia para a pose e o tempo
(regra do estudo: "o guia só dá a pose, o quadro final usa só as peças do kit").

  python ferramentas/piloto_raiclaven.py              refaz o kit e grava quadros_pecas_hd e quadros_pecas (1x)
  python ferramentas/piloto_raiclaven.py --so-pose    usa o kit que já existe
  python ferramentas/piloto_raiclaven.py parado soco  só essas animações

Cada animação mantém a soma de ticks e o elemento com caixa de acerto da [Begin Action] de hoje. Depois das poses
entram os quadros do meio, a respiração, o atraso da cabeça e do laço do avental (ferramentas/vida_pecas.py), e as
pernas no chão são refeitas por cinemática inversa em todo desenho (o pé não escorrega). O robô de defeitos
(fresta, mancha escura, pedaço solto, pé fora do chão) roda em todos e grava docs/boneco-pecas/raiclaven/robo_defeitos.md.
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
import piloto_firme as pf  # noqa: E402  (antes do kit: ele mexe nas variantes do Pengaró ao importar)
import pecas_raiclaven as pr  # noqa: E402
import boneco_ajuste as b  # noqa: E402
import vida_pecas as vida  # noqa: E402

pr.configurar()
SPR = pr.SPR
DOCS = pr.DOCS
# o que o jogo mostra hoje em cada elemento (sprite do .sff -> quadro de origem, conferido pela máscara: 86-93 são
# ginga/00-07; 81, 1100, 83, 84, 85 são soco/03-07; 422, 423, 883/884, 874, 426-428 são chute_alto/01-07)
ATUAL = {
    "parado": [(f"ginga/{i:02d}", 7) for i in range(8)],
    "soco": [("soco/03", 3), ("soco/04", 1), ("soco/05", 6), ("soco/06", 3), ("soco/07", 6)],
    "chute_alto": [("chute_alto/01", 5), ("chute_alto/02", 2), ("chute_alto/03", 2), ("chute_alto/04", 8),
                   ("chute_alto/05", 7), ("chute_alto/06", 9), ("chute_alto/07", 9)],
}
ACAO = {"parado": 0, "soco": 200, "chute_alto": 240}
CAIXA = {"soco": (2, (45, -276, 190, -192)), "chute_alto": (3, (36, -300, 171, -174))}

# variantes: o membro muda de desenho (não só de ângulo). Polígono medido no desenho de origem (3x); a peça é
# ampliada para a escala do kit e presa pelo avental (perna) ou pela cabeça (braço). Ver pecas_raiclaven.variante.
pr.VARIANTES.update({
    "braco_tras": {
        # braço mecânico à frente, tesoura aberta (soco/04)
        "frente": ("soco/04", [(488, 384), (560, 381), (596, 384), (612, 374), (642, 366), (670, 356), (692, 358),
                               (692, 373), (652, 386), (624, 398), (692, 401), (692, 416), (640, 423), (600, 426),
                               (560, 433), (520, 433), (488, 429)], "cabeca", None),
        # estocada: braço todo esticado, tesoura fechada lá na frente (soco/05)
        # martelo: braço erguido dobrado, tesoura aberta acima da cabeça (martelo/01), com a ombreira junto
        "armado": ("martelo/01", [(424, 372), (428, 340), (445, 315), (468, 300), (476, 262), (530, 240), (610, 236),
                                  (612, 262), (545, 288), (522, 318), (500, 330), (516, 360), (522, 404), (490, 412),
                                  (452, 410), (430, 396)], "cabeca", None),
        # martelo: braço todo erguido, tesoura lá em cima (martelo/02), com a ombreira junto
        "alto": ("martelo/02", [(422, 335), (428, 300), (445, 272), (462, 258), (466, 240), (470, 232), (492, 226),
                                (500, 200), (520, 175), (548, 158), (554, 166), (532, 192), (514, 226), (560, 204),
                                (594, 188), (598, 198), (562, 222), (522, 246), (516, 262), (494, 276), (482, 300),
                                (498, 330), (504, 368), (472, 394), (440, 394), (422, 372)], "cabeca", None),
        "estocada": ("soco/05", [(480, 372), (530, 368), (560, 372), (580, 366), (620, 368), (692, 374),
                                 (703, 388), (692, 401), (640, 407), (600, 415), (578, 421), (540, 415), (500, 414),
                                 (480, 413)], "cabeca", pr.colorido),
    },
    "braco_frente": {
        # rasteira: tira a vassoura e ergue ao lado da cabeça (rasteira/02)
        "vassoura": ("rasteira/02", [(566, 346), (630, 336), (634, 372), (614, 384), (618, 436), (636, 440),
                                     (640, 472), (628, 490), (640, 556), (662, 636), (650, 642), (628, 560),
                                     (614, 508), (590, 508), (578, 488), (582, 462), (598, 450), (596, 384),
                                     (568, 378)], "cabeca", pr.escuro_longe),
        # rasteira: braço para baixo varrendo, a vassoura no chão (rasteira/03)
        "varre": ("rasteira/03", [(575, 485), (600, 480), (625, 510), (627, 535), (615, 560), (627, 610),
                                  (640, 622), (655, 625), (667, 645), (665, 659), (595, 659), (592, 645),
                                  (602, 627), (620, 615), (602, 572), (592, 572), (582, 550), (582, 525),
                                  (575, 500)], "cabeca", pr.escuro_longe),
    },
    "quadril": {  # metade de baixo agachada inteira (avental, as duas pernas e os sapatos), do agachado/04
        "agachado": ("agachado/04", [(420, 556), (500, 552), (640, 556), (652, 600), (660, 680), (410, 680),
                                     (414, 600)], "agachado", pr.lamina_no_colo),
    },
    "coxa_frente": {  # perna da frente inteira levantada (coxa, canela e sapato), sem avental, lâmina e mão
        "baixa": ("chute_alto/01", [(572, 445), (600, 436), (633, 449), (637, 490), (626, 520), (613, 530),
                                    (629, 565), (631, 588), (608, 590), (588, 576), (566, 561), (565, 530),
                                    (572, 505)], "chao", pr.pele_ou_claro_perto_do_corpo),
        "camara": ("chute_alto/02", [(542, 415), (560, 403), (592, 403), (608, 420), (608, 452), (598, 472),
                                     (593, 496), (579, 502), (579, 543), (562, 551), (543, 538), (542, 505)],
                   "chao", pr.pele_ou_claro_perto_do_corpo),
        "esticada": ("chute_alto/04", [(528, 470), (526, 420), (545, 401), (575, 397), (600, 381), (625, 367),
                                       (640, 351), (650, 327), (678, 327), (681, 360), (675, 398), (650, 405),
                                       (625, 428), (600, 443), (570, 468), (547, 503), (539, 533), (528, 529)],
                     "chao", pr.pele_ou_claro_perto_do_corpo),
    },
})


COM_OMBREIRA = {"armado", "alto"}


def P(q=(0, 0), tronco=0, cabeca=0, bt=0, abt=0, bf=0, abf=0, pente=0, coxa=None, canela=None, pe_frente=0,
      pe_tras=0, lev=False, braco=None, perna=None, baixo=None, mao=None):
    """Pose por junta. q = deslocamento do quadril (x, y); ângulos em graus, horário na tela (para quem olha à
    direita, tronco > 0 inclina para a frente). braco/perna escolhem uma variante (o membro inteiro vem de outro
    desenho); as pernas no chão saem por cinemática inversa com o pé onde estava no parado (+ pe_frente/pe_tras)."""
    pose = {"quadril": {"ang": 0, "dx": q[0], "dy": q[1]}, "tronco": {"ang": tronco}, "cabeca": {"ang": cabeca},
            "braco_tras": {"ang": bt}, "antebraco_tras": {"ang": abt}, "braco_frente": {"ang": bf + abf / 2},
            "_pe": {"frente": pe_frente, "tras": pe_tras}}
    if mao:  # o braço do pente vem de outro desenho (com a vassoura)
        pose["braco_frente"]["var"] = mao
    if braco:  # o braço mecânico inteiro vem do desenho da variante
        pose["braco_tras"]["var"] = braco
        pose["antebraco_tras"]["var"] = "vazio"
        if braco in COM_OMBREIRA:  # a variante traz a ombreira levantada junto: a do kit sai
            pose["ombreira"] = {"ang": 0, "var": "vazio"}
    if baixo:  # metade de baixo agachada: um desenho só do cinto aos pés, o quadril desce junto
        pose["quadril"]["var"] = baixo
        pose["quadril"]["dx"] += pr.AGACHADO[0]
        pose["quadril"]["dy"] += pr.AGACHADO[1]
        for s_ in ("coxa_tras", "coxa_frente", "canela_tras", "canela_frente"):
            pose[s_] = {"ang": 0, "var": "vazio"}
        pose["_lev"] = {"frente": 1, "tras": 1}
        pose["_agachado"] = {"sim": 1}
        return pose
    if lev or perna:
        pose["coxa_frente"] = {"ang": coxa or 0}
        pose["canela_frente"] = {"ang": canela or 0}
        if perna:
            pose["coxa_frente"]["var"] = perna
            pose["canela_frente"]["var"] = "vazio"
        pose["_lev"] = {"frente": 1}
    return pose


# ------------------------------------------------------------------ poses-chave (guia: os desenhos de hoje)
POSES = {
    "parado": [  # ginga: sobe e desce o quadril, o pente gira entre os dedos, a tesoura acompanha
        P(),
        P(q=(-1, 3), tronco=1, bt=2, abt=-2, abf=-4, pente=-8),
        P(q=(-2, 7), tronco=2, cabeca=1, bt=4, abt=-4, bf=2, abf=-8, pente=-16),
        P(q=(-2, 9), tronco=2, cabeca=2, bt=5, abt=-5, bf=3, abf=-10, pente=-10),
        P(q=(-1, 6), tronco=1, cabeca=1, bt=3, abt=-3, bf=2, abf=-6, pente=2),
        P(q=(0, 3), tronco=0, bt=1, abt=-1, abf=-2, pente=10),
        P(q=(1, 1), tronco=-1, cabeca=-1, bt=-1, abt=1, abf=2, pente=14),
        P(q=(0, 0), tronco=0, bt=0, abt=0, abf=1, pente=6),
    ],
    "soco": [
        # regra do Alisson (17/11): soco não é só o braço esticando. O peso vai para trás, o pé da frente dá um passo,
        # o quadril desce e entra, o tronco inclina e o ombro leva o braço; a mão do pente volta para a guarda do queixo
        # preparo: peso atrás, ombro mecânico recolhido, tesoura junto do corpo
        P(q=(-8, 6), tronco=-4, cabeca=-2, bt=16, abt=-28, bf=-4, abf=-8),
        # passo: o pé da frente sai, o quadril entra, o braço vem à frente com a tesoura abrindo
        P(q=(10, 10), tronco=4, cabeca=2, braco="frente", bt=4, bf=-18, pe_frente=22),
        # contato: pé da frente plantado lá na frente, o de trás gira no lugar, quadril baixo, tronco inclinado, braço
        # todo esticado e tesoura fechando
        P(q=(24, 14), tronco=7, cabeca=3, braco="estocada", bt=-2, bf=-28, pe_frente=38, pe_tras=8),
        # recolhe: tesoura abre de novo, o corpo começa a voltar
        P(q=(16, 11), tronco=4, cabeca=2, braco="frente", bt=6, bf=-18, pe_frente=38, pe_tras=8),
        # volta para a guarda, o pé recua junto
        P(q=(1, 1), tronco=0, bt=-2, abt=2, bf=2),
    ],
    "chute_alto": [
        # o joelho sobe, o corpo deita um pouco para trás; o pente vai para a guarda alta
        P(q=(-4, -2), tronco=-3, cabeca=-1, bt=4, abt=-3, bf=6, abf=8, perna="baixa"),
        # câmara alta
        P(q=(-6, -4), tronco=-6, cabeca=-2, bt=6, abt=-4, bf=8, abf=10, perna="camara"),
        # esticando
        P(q=(-8, -4), tronco=-8, cabeca=-3, bt=8, abt=-5, bf=10, abf=12, perna="esticada", coxa=8),
        # contato: perna esticada na altura da cabeça, tronco para trás
        P(q=(-10, -4), tronco=-10, cabeca=-4, bt=10, abt=-6, bf=10, abf=12, pente=-6, perna="esticada"),
        # recolhe a perna
        P(q=(-7, -3), tronco=-6, cabeca=-2, bt=6, abt=-4, bf=8, abf=10, perna="camara"),
        # desce o joelho
        P(q=(-3, 0), tronco=-3, cabeca=-1, bt=3, abt=-2, bf=4, abf=6, perna="baixa"),
        # pé no chão, guarda
        P(q=(0, 2), tronco=0, bt=1, abt=0, abf=0),
    ],
}

pf.TORNOZELO = pr.TORNOZELO
pf.CHAO = pr.CHAO
pf.RAIZ_DOCS = DOCS


def separar(kit):
    """Sapatos separados da canela (ficam retos no chão; no pé levantado giram com a canela) e o laço do avental
    separado do quadril (balança atrasado, como as bolinhas do Pengaró)."""
    q = kit["pecas"]["quadril"]
    img = q["img"]
    ox, oy = q["origem"]
    m = b.mascara(pr.LACO)[oy:oy + img.shape[0], ox:ox + img.shape[1]] & (img[..., 3] > 0)
    laco = np.zeros_like(img)
    laco[m] = img[m]
    img = img.copy()
    img[m] = 0
    q["img"] = img
    kit["bolinhas"] = laco
    kit["no_bolinhas"] = (472.0, 486.0)
    kit["pes"] = {}
    for slot, (tx, ty) in pr.TORNOZELO.items():
        p = kit["pecas"][slot]
        im = p["img"].copy()
        ox, oy = p["origem"]
        corte = ty - oy
        pe = np.zeros_like(im)
        pe[corte - 6:] = im[corte - 6:]  # 6 linhas de barra da calça: tapam a emenda quando a canela gira
        im[corte + 3:] = 0
        p["img"] = im
        kit["pes"][slot] = {"img": pe, "origem": (ox, oy), "tornozelo": (tx, ty),
                            "fundo": int(np.nonzero(pe[..., 3].any(1))[0].max())}
    return kit


def plantar(pose):
    """Pernas no chão por cinemática inversa: o tornozelo fica onde está no parado (+ o passo da pose)."""
    pose = {k: dict(v) for k, v in pose.items()}
    pes = pose.get("_pe", {})
    lev = pose.get("_lev", {})
    w = b.mundo(pose)
    for lado, coxa, canela in (("tras", "coxa_tras", "canela_tras"), ("frente", "coxa_frente", "canela_frente")):
        if lev.get(lado):
            continue
        qr, jr = pr.OSSOS[coxa][0], pr.OSSOS[canela][0]
        tr = pr.TORNOZELO[canela]
        c1, c2 = pf.ik(w[coxa][0], (tr[0] + pes.get(lado, 0), tr[1]), jr, qr, tr)
        pose[coxa] = {"ang": c1}
        pose[canela] = {"ang": c2}
        w = b.mundo(pose)
    return pose


def desenhar(kit, pose):
    """As peças na ordem de camada, os sapatos (reto no chão; girando com a canela no pé levantado), o laço do
    avental e o fechamento de fresta perto das juntas."""
    tela = b.desenhar(kit, pose)
    w = b.mundo(pose)
    lev = pose.get("_lev", {})
    if pose.get("_agachado"):  # o desenho agachado já traz sapatos e laço
        return pf.sem_migalha(pf.fechar_frestas(tela, juntas=[w[sl][0] for sl in pr.OSSOS]))
    for slot in ("canela_tras", "canela_frente"):
        joelho, ang = w[slot]
        jr = pr.OSSOS[slot][0]
        pe = kit["pes"][slot]
        t = b.girar(pe["tornozelo"], jr, ang)
        tx, ty = t[0] + joelho[0] - jr[0], t[1] + joelho[1] - jr[1]
        if slot == "canela_frente" and pose.get("coxa_frente", {}).get("var"):
            continue  # a perna levantada da variante já traz o sapato
        if lev.get("frente") and slot == "canela_frente":
            piv = (pe["tornozelo"][0] - pe["origem"][0], pe["tornozelo"][1] - pe["origem"][1])
            r, piv2 = b.rotsprite(pe["img"], ang, piv)
            b.colar(tela, r, int(round(tx - piv2[0])), int(round(ty - piv2[1])))
            continue
        x0 = int(round(pe["origem"][0] + tx - pe["tornozelo"][0]))
        y0 = int(round(pe["origem"][1] + ty - pe["tornozelo"][1]))
        fundo = pe["fundo"] + y0
        if abs(fundo - pr.CHAO) <= 10:
            y0 += pr.CHAO - fundo
        b.colar(tela, pe["img"], x0, y0, so_vazio=True)
    bo = pose.get("_bolinhas", {})
    p = kit["pecas"]["quadril"]
    (qx, qy), qang = w["quadril"]
    jq = pr.OSSOS["quadril"][0]
    no = b.girar(kit["no_bolinhas"], jq, qang)
    no = (no[0] + qx - jq[0] + bo.get("dx", 0), no[1] + qy - jq[1] + bo.get("dy", 0))
    piv = (kit["no_bolinhas"][0] - p["origem"][0], kit["no_bolinhas"][1] - p["origem"][1])
    r, piv2 = b.rotsprite(kit["bolinhas"], qang + bo.get("ang", 0), piv)
    # o laço fica atrás da perna de trás e do braço: só pinta onde está vazio
    b.colar(tela, r, int(round(no[0] - piv2[0])), int(round(no[1] - piv2[1])), so_vazio=True)
    return pf.sem_migalha(pf.fechar_frestas(tela, juntas=[w[sl][0] for sl in pr.OSSOS]))


def mancha_maxima(kit):
    """Escuro grosso do corpo com os braços tirados: a camisa é preta, e o que o braço descobre não é defeito. O
    robô reprova o que passar disso (contorno solto, sombra de peça, buraco pintado de preto)."""
    vazio = {k: dict(v, img=np.zeros((1, 1, 4), np.uint8), sob=np.zeros((1, 1, 4), np.uint8))
             for k, v in kit["pecas"].items() if k.startswith(("braco", "antebraco", "ombreira"))}
    k2 = dict(kit, pecas={**kit["pecas"], **vazio})
    sem = desenhar(k2, plantar(P()))
    al = (sem[..., 3] > 0).astype(np.uint8)
    s = sem[..., :3].astype(int).sum(-1)
    grosso = cv2.erode(((s < 110) & (al > 0)).astype(np.uint8), np.ones((4, 4), np.uint8))
    ys = np.nonzero(al.any(1))[0]
    return max(pf.mancha_ref(), int(grosso[ys.min() + 80:].sum()))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    nomes = args or list(ATUAL)
    if "--so-pose" not in sys.argv:
        pr.montar_kit()
    kit = separar(b.ler_kit())
    pf.PES_REF = None
    pf.MANCHA_REF = mancha_maxima(kit)
    ref = b.abrir(b.REF)
    DOCS.mkdir(parents=True, exist_ok=True)
    relatorio = ["| quadro | guia de hoje | robô de defeitos |", "|---|---|---|"]
    for nome in nomes:
        elems = ATUAL[nome]
        chaves = POSES[nome]
        assert len(chaves) == len(elems), nome
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            shutil.rmtree(SPR / pasta / nome, ignore_errors=True)
            (SPR / pasta / nome).mkdir(parents=True)
        # cada elemento ganha um nome próprio para a pose (o mesmo desenho de hoje pode aparecer duas vezes)
        poses = {f"{q}#{k}": chaves[k] for k, (q, _) in enumerate(elems)}
        el = [(f"{q}#{k}", t) for k, (q, t) in enumerate(elems)]
        bate, cx = CAIXA.get(nome, (None, None))
        laco = nome == "parado"
        quadros = vida.animar(poses, el, bate=bate, laco=laco, guarda=None if laco else P())
        if laco:
            quadros = vida.respirar(quadros)
        quadros = vida.atrasar(quadros, laco=laco)
        for i, (pose, t, caixa_on, q) in enumerate(quadros):
            pose = plantar(pose)
            out = desenhar(kit, pose)
            erros = pf.conferir(out, ref, None)
            relatorio.append(f"| {nome}/{i:02d} | {q.split('#')[0]} | "
                             f"{'PASS' if not erros else 'FAIL ' + '; '.join(erros)} |")
            Image.fromarray(out).save(SPR / "quadros_pecas_hd" / nome / f"{i:02d}.png")
            Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(SPR / "quadros_pecas" / nome / f"{i:02d}.png")
        tempos = {"acao": ACAO[nome], "caixa": cx, "origem": [q for q, _ in elems],
                  "elementos": [{"desenho": i, "ticks": t, "caixa": c, "de": q.split("#")[0]}
                                for i, (_, t, c, q) in enumerate(quadros)]}
        assert sum(e["ticks"] for e in tempos["elementos"]) == sum(t for _, t in elems)
        for pasta in ("quadros_pecas_hd", "quadros_pecas"):
            (SPR / pasta / nome / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False),
                                                            encoding="utf-8")
        print(nome, len(elems), "poses-chave ->", len(quadros), "desenhos")
    Image.fromarray(desenhar(kit, plantar(P()))).save(SPR / "quadros_pecas_hd" / "guarda.png")
    falhas = sum("FAIL" in linha for linha in relatorio)
    texto = "\n".join(relatorio) + f"\n\n{falhas} quadro(s) com defeito.\n"
    print(texto)
    (DOCS / "robo_defeitos.md").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    main()
