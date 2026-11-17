#!/usr/bin/env python3
"""CK pelo boneco de peças, "corpo firme + vida" (método aprovado pelo Alisson no Pengaró, 16/11).

Tronco, rosto e pele saem de um desenho só (referencia_ginga/00), em cor cheia. Braços e pernas giram presos nas
juntas. Os desenhos de hoje servem só de guia de pose; nos quadros confusos (lista em GUIA) a pose vem de outro
desenho bom ou é escrita à mão, em vez de copiar o erro.

  python ferramentas/pecas_ck.py kit                  recorta o kit em sprites/ck/pecas/ (RGBA + kit.json)
  python ferramentas/pecas_ck.py ver                  folha com as peças coloridas por cima do parado (conferência)
  python ferramentas/pecas_ck.py poses [FOLHAS]       acha as poses-chave das folhas (sprites/ck/pecas/poses.json)
  python ferramentas/pecas_ck.py desenhos [FOLHAS]    monta os 8 desenhos de cada folha em quadros_pecas_hd/<folha>/
  python ferramentas/pecas_ck.py acoes                anima as ações (vida) em quadros_pecas_hd/acoes/<nome>/

Nada daqui entra no .sff nem no gerador: é a prova para o Breno.
"""
import functools
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

RAIZ = AQUI.parent
SPR = RAIZ / "sprites" / "ck"
b.SPR = SPR
b.HD = SPR / "quadros_arcade_hd"
b.PECAS = SPR / "pecas"
b.REF = REF = "referencia_ginga/00"
TELA = b.TELA

# ------------------------------------------------------------------ recorte do parado (3x, tela 1080x780)
CINTO = 462  # linha da cintura (barra da polo por cima do short)
CABECA = [(524, 312), (604, 312), (604, 352), (586, 357), (581, 378), (571, 390), (557, 394), (541, 389),
          (531, 374), (526, 352)]
PESCOCO = [(533, 368), (552, 384), (566, 392), (568, 404), (548, 406), (531, 398)]
BRACO_TRAS = [(486, 398), (491, 385), (504, 379), (518, 384), (525, 398), (527, 415), (540, 413), (544, 395),
              (555, 388), (571, 389), (580, 398), (580, 413), (571, 423), (560, 429), (548, 434), (531, 446),
              (516, 456), (500, 458), (491, 451), (487, 433), (485, 415)]
BRACO_FRENTE = [(578, 389), (590, 382), (606, 384), (613, 395), (611, 411), (602, 421), (600, 432), (596, 446),
                (590, 456), (580, 463), (567, 462), (561, 452), (565, 440), (576, 429), (578, 416)]
QUADRIL = [(484, 456), (600, 456), (600, 500), (560, 506), (540, 512), (515, 506), (484, 500)]
PERNA_TRAS = [(482, 486), (538, 486), (541, 526), (534, 553), (520, 557), (510, 590), (512, 618), (518, 662),
              (466, 662), (470, 622), (481, 590), (483, 556), (482, 520)]
PERNA_FRENTE = [(538, 486), (600, 486), (602, 520), (597, 553), (594, 585), (590, 614), (614, 638), (616, 662),
                (550, 662), (558, 622), (564, 585), (560, 557), (546, 553), (539, 526)]
JOELHO_TRAS, JOELHO_FRENTE = (500, 574), (577, 574)
TORNOZELO = {"canela_tras": (491, 626), "canela_frente": (571, 625)}
CHAO = 659

OSSOS = {  # junta no parado, peça mãe, ponta (régua)
    "quadril": ((540, 480), None, (540, 505)),
    "tronco": ((540, 462), "quadril", (548, 392)),
    "cabeca": ((552, 392), "tronco", (565, 330)),
    "braco_tras": ((506, 398), "tronco", (562, 408)),
    "braco_frente": ((556, 414), "tronco", (595, 400)),
    "coxa_tras": ((512, 498), "quadril", JOELHO_TRAS),
    "canela_tras": (JOELHO_TRAS, "coxa_tras", TORNOZELO["canela_tras"]),
    "coxa_frente": ((566, 498), "quadril", JOELHO_FRENTE),
    "canela_frente": (JOELHO_FRENTE, "coxa_frente", TORNOZELO["canela_frente"]),
}
CAMADAS = ["coxa_tras", "canela_tras", "canela_frente", "coxa_frente", "quadril", "tronco",
           "cabeca", "braco_tras", "braco_frente"]


def ver(saida):
    """Peças coloridas por cima do parado, para conferir os polígonos."""
    from PIL import ImageDraw
    ref = Image.open(b.HD / f"{REF}.png").convert("RGBA")
    bg = Image.new("RGBA", ref.size, (70, 90, 110, 255))
    bg.alpha_composite(ref)
    cores = [(255, 0, 0), (0, 255, 0), (0, 128, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 128, 0)]
    over = Image.new("RGBA", ref.size)
    d = ImageDraw.Draw(over)
    for i, poli in enumerate([CABECA, PESCOCO, BRACO_TRAS, BRACO_FRENTE, QUADRIL, PERNA_TRAS, PERNA_FRENTE]):
        c = cores[i % len(cores)]
        d.polygon(poli, outline=c + (255,), fill=c + (50,))
    for nome, (j, _, ponta) in OSSOS.items():
        d.ellipse([j[0] - 3, j[1] - 3, j[0] + 3, j[1] + 3], fill=(255, 255, 255, 255))
        d.line([j, ponta], fill=(255, 255, 255, 200))
    for t in TORNOZELO.values():
        d.ellipse([t[0] - 3, t[1] - 3, t[0] + 3, t[1] + 3], fill=(0, 0, 0, 255))
    bg.alpha_composite(over)
    c = bg.crop((440, 300, 640, 670))
    c.resize((c.width * 3, c.height * 3), Image.NEAREST).save(saida)


# corpo sem os braços: o que os braços tapam no parado é tapado no kit (peito, pescoço, lado do short)
CORPO_SEM_BRACO = [(487, 392), (500, 378), (522, 374), (533, 372), (552, 386), (564, 396), (567, 415), (568, 440),
                   (570, 462), (487, 462), (485, 430)]
SOBRA = b.SOBRA


def tapar_buracos(img):
    """Os desenhos de hoje têm furinhos transparentes por dentro do boneco (o fundo aparece no jogo): fecha com a cor
    mais escura em volta (eram pixels do contorno)."""
    al = (img[..., 3] > 0).astype(np.uint8)
    fechado = cv2.morphologyEx(al, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0
    buraco = fechado & (al == 0)
    if not buraco.any():
        return img
    out = img.copy()
    soma = img[..., :3].astype(int).sum(-1)
    soma[al == 0] = 10 ** 6
    for _ in range(4):
        ys, xs = np.nonzero(buraco & (out[..., 3] == 0))
        if not len(ys):
            break
        for y, x in zip(ys, xs):
            viz = [(y + dy, x + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if out[y + dy, x + dx, 3] > 0]
            if viz:
                vy, vx = min(viz, key=lambda q: soma[q])
                out[y, x] = out[vy, vx]
        soma = out[..., :3].astype(int).sum(-1)
        soma[out[..., 3] == 0] = 10 ** 6
    return out


def pintar_camisa(img, alvo):
    """Peito escondido atrás das luvas no parado: pintado em faixas chapadas com as cores claras da própria camisa
    (branco, lilás claro, lilás), seguindo a luz de volta. Contorno de 1 px onde a beirada é nova."""
    rgb = img[..., :3].astype(int)
    hsv = cv2.cvtColor(np.ascontiguousarray(img[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
    claro = (img[..., 3] > 0) & (rgb.sum(-1) > 330)
    claro &= ~(((hsv[..., 0] <= 25) | (hsv[..., 0] >= 165)) & (hsv[..., 1] > 90))
    claro &= ~((hsv[..., 0] >= 35) & (hsv[..., 0] <= 95) & (hsv[..., 1] > 60))
    pint = cv2.inpaint(np.ascontiguousarray(img[..., :3]), np.uint8(~claro) * 255, 8, cv2.INPAINT_TELEA)
    pint = cv2.GaussianBlur(pint, (0, 0), 3)
    u, c = np.unique(img[claro][:, :3], axis=0, return_counts=True)
    pal = u[np.argsort(-c)[:3]].astype(int)
    d = ((pint[alvo][:, None, :].astype(int) - pal[None]) ** 2).sum(-1)
    out = img.copy()
    out[alvo, :3] = pal[d.argmin(1)]
    out[alvo, 3] = 255
    # contorno escuro na beirada nova (onde antes encostava o braço e agora é fora do corpo)
    a = out[..., 3] > 0
    borda = a & ~(cv2.erode(np.uint8(a), np.ones((3, 3), np.uint8)) > 0) & cv2.dilate(np.uint8(alvo), np.ones((3, 3), np.uint8)).astype(bool)
    out[borda, :3] = (56, 23, 82)
    return out


def texturizar(base, alvo, semente=7, B=6):
    """O peito pintado em faixas fica liso demais perto do resto da camisa (que é cheia de dobra e risco). Aqui ele
    ganha a textura de verdade da camisa: blocos 6x6 tirados de pedaços da camisa de desenhos de hoje do CK (só
    branco, lilás e risco, sem logo, gola, pele ou luva), escolhidos para emendar com o vizinho já pintado e para ter
    a mesma luz da faixa chapada embaixo (a sombra continua no lugar). O contorno da beirada fica."""
    rng = np.random.default_rng(semente)
    yy = np.mgrid[:TELA[1], :TELA[0]][0]
    banco = []
    for f in ("soco/02", "soco/05", "provoca/03", "despertar_a/01", "golaco/02", "vitoria/06", "provoca/02",
              "bola/02", "lata/04", REF):
        R = tapar_buracos(b.abrir(f))
        hsv = cv2.cvtColor(np.ascontiguousarray(R[..., :3]), cv2.COLOR_RGB2HSV).astype(int)
        ruim = ((hsv[..., 0] >= 35) & (hsv[..., 0] <= 95) & (hsv[..., 1] > 60)) | \
               (((hsv[..., 0] <= 25) | (hsv[..., 0] >= 165)) & (hsv[..., 1] > 90))
        k = (R[..., 3] > 0) & ~cv2.dilate(np.uint8(ruim), np.ones((5, 5), np.uint8)).astype(bool)
        k &= cv2.erode(np.uint8(R[..., 3] > 0), np.ones((11, 11), np.uint8)).astype(bool) & (yy >= 360) & (yy < 465)
        for y in range(360, 465, 2):
            for x in range(440, 640, 2):
                if k[y:y + B, x:x + B].all():
                    banco.append(R[y:y + B, x:x + B, :3].astype(np.float32))
    C = np.array(banco)
    a = base[..., 3] > 0
    dentro = alvo & (cv2.erode(np.uint8(a), np.ones((3, 3), np.uint8)) > 0)
    out = base.astype(np.float32)
    feito = ~dentro
    ys, xs = np.nonzero(dentro)
    for y in range(ys.min(), ys.max() + 1, B - 1):
        for x in range(xs.min(), xs.max() + 1, B - 1):
            m = dentro[y:y + B, x:x + B]
            if not m.any() or m.shape != (B, B):
                continue
            kn = feito[y:y + B, x:x + B] & a[y:y + B, x:x + B]
            tgt = out[y:y + B, x:x + B, :3]
            sel = C[rng.choice(len(C), min(500, len(C)), replace=False)]
            custo = (((sel - tgt[None]) ** 2).sum(-1) * kn[None]).sum((1, 2)) + \
                0.5 * ((sel.mean((1, 2)) - base[y:y + B, x:x + B, :3][m].astype(np.float32).mean(0)) ** 2).sum(-1) * B * B
            melhor = sel[custo.argmin()]
            novo = m & ~feito[y:y + B, x:x + B]
            out[y:y + B, x:x + B, :3][novo] = melhor[novo]
            feito[y:y + B, x:x + B] |= m
    return out.astype(np.uint8)


def aparar_lado(img):
    """Lado do tronco debaixo do braço da frente: sobravam pontas do antebraço e do punho (marrom, verde, vermelho)
    que viravam um espinho quando o braço sai para o soco. Corta reto e repinta com a sombra da camisa + contorno."""
    out = img.copy()
    yy, xx = np.mgrid[:TELA[1], :TELA[0]]
    out[(xx > 569 + (yy - 412) * 0.2) & (yy > 412) & (yy < 456)] = 0  # borda inclinada, como o lado do corpo
    c = out[..., :3].astype(int)
    zona = (xx > 548) & (yy > 412) & (yy < 456) & (out[..., 3] > 0)
    estranho = zona & (((c[..., 0] > c[..., 2] + 20) & (c[..., 0] > 90)) | (c[..., 1] > c[..., 0] + 20))
    out[estranho] = (150, 128, 205, 255)
    a = out[..., 3] > 0
    borda = a & ~(cv2.erode(np.uint8(a), np.ones((3, 3), np.uint8)) > 0) & (xx > 555) & (yy > 412) & (yy < 456)
    out[borda] = (56, 23, 82, 255)
    return out


def pintar_pescoco(img, regiao, dono):
    """Pescoço que as luvas tapavam: pele em sombra (debaixo do queixo é escuro), em dois tons tirados da própria
    cabeça e com o contorno do desenho por fora. Nada de borrão: o soco esticado deixa o pescoço à mostra."""
    alvo = regiao & ~dono
    if not alvo.any():
        return img
    out = img.copy()
    px = img[dono & (img[..., 3] > 0)][:, :3].astype(int)
    pele = px[(px[:, 0] > px[:, 1] + 25) & (px[:, 1] > px[:, 2]) & (px[:, 0] > 90)]
    lum = pele.sum(1)
    escuro = np.median(pele[lum <= np.percentile(lum, 20)], 0)
    medio = np.median(pele[(lum > np.percentile(lum, 15)) & (lum <= np.percentile(lum, 32))], 0)
    ys, xs = np.nonzero(alvo)
    meio = ys.min() + 0.7 * (ys.max() - ys.min())
    for y, x in zip(ys, xs):
        out[y, x, :3] = escuro if y < meio else medio
        out[y, x, 3] = 255
    a = out[..., 3] > 0
    borda = alvo & ~(cv2.erode(np.uint8(a), np.ones((3, 3), np.uint8)) > 0)
    out[borda] = (56, 23, 82, 255)
    return out


def tapar(img, regiao, dono, raio=4):
    """Pinta (inpaint) a parte de `regiao` que não é do `dono`, com as cores de volta (sem o fundo transparente)."""
    alvo = regiao & ~dono
    if not alvo.any():
        return img
    vazio = (img[..., 3] == 0) & (cv2.dilate(np.uint8(alvo), np.ones((25, 25), np.uint8)) > 0)
    pint = cv2.inpaint(np.ascontiguousarray(img[..., :3]), np.uint8(alvo | vazio) * 255, raio, cv2.INPAINT_TELEA)
    out = img.copy()
    out[alvo, :3] = pint[alvo]
    out[alvo, 3] = 255
    return out


def disco(c, r):
    m = np.zeros(TELA[::-1], np.uint8)
    cv2.circle(m, (int(c[0]), int(c[1])), r, 1, -1)
    return m.astype(bool)


def partes_do_parado():
    ref = tapar_buracos(b.abrir(REF))
    alfa = ref[..., 3] > 0
    yy, xx = np.mgrid[:TELA[1], :TELA[0]]
    baixo = yy >= CINTO
    m = b.mascara
    m_bt = m(BRACO_TRAS) & alfa
    m_bf = m(BRACO_FRENTE) & alfa & ~m_bt
    m_cab = (m(CABECA) | m(PESCOCO)) & alfa & ~m_bt & ~m_bf
    quad = m(QUADRIL) & alfa & baixo & ~m_bt & ~m_bf
    pt = m(PERNA_TRAS) & alfa & ~m_bt & ~m_bf
    pf = m(PERNA_FRENTE) & alfa & ~m_bt & ~m_bf & ~pt
    partes = {
        "cabeca": m_cab,
        "braco_tras": m_bt,
        "braco_frente": m_bf,
        "tronco": ~baixo & alfa & ~m_cab & ~m_bt & ~m_bf,
        "quadril": quad,
        "coxa_tras": pt & (yy < JOELHO_TRAS[1] + 4),
        "canela_tras": pt & ((yy >= JOELHO_TRAS[1]) | disco(JOELHO_TRAS, 14)),
        "coxa_frente": pf & (yy < JOELHO_FRENTE[1] + 4),
        "canela_frente": pf & ((yy >= JOELHO_FRENTE[1]) | disco(JOELHO_FRENTE, 14)),
    }
    resto = alfa & ~np.logical_or.reduce(list(partes.values()))
    # sobras entre as pernas: vão para a perna mais perto
    dt = cv2.distanceTransform(np.uint8(~pt), cv2.DIST_L2, 3)
    df = cv2.distanceTransform(np.uint8(~pf), cv2.DIST_L2, 3)
    for perna, mais_perto in (("tras", dt <= df), ("frente", df < dt)):
        r = resto & mais_perto & (yy >= CINTO)
        j = JOELHO_TRAS if perna == "tras" else JOELHO_FRENTE
        partes[f"coxa_{perna}"] |= r & (yy < j[1] + 4)
        partes[f"canela_{perna}"] |= r & (yy >= j[1] - 12)
    resto = alfa & ~np.logical_or.reduce(list(partes.values()))
    return ref, partes, resto


def montar_kit():
    if b.PECAS.exists():
        shutil.rmtree(b.PECAS)
    b.PECAS.mkdir(parents=True)
    ref, partes, resto = partes_do_parado()
    if resto.sum() > 20:
        ys, xs = np.nonzero(resto)
        print(f"aviso: {int(resto.sum())} px do parado sem peça (x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()})")
    imgs = {k: np.where(v[..., None], ref, 0).astype(np.uint8) for k, v in partes.items()}
    bracos = partes["braco_tras"] | partes["braco_frente"]
    # peito, pescoço e lado do corpo que os braços tapam
    corpo = b.mascara(CORPO_SEM_BRACO)
    peito = corpo & bracos & (np.mgrid[:TELA[1], :TELA[0]][0] < CINTO) & ~partes["tronco"]
    imgs["tronco"] = texturizar(pintar_camisa(imgs["tronco"], peito), peito)
    imgs["tronco"] = aparar_lado(imgs["tronco"])
    pesc = b.mascara(PESCOCO) & bracos
    imgs["cabeca"] = pintar_pescoco(imgs["cabeca"], pesc, partes["cabeca"])
    kit = {"ref": f"quadros_arcade_hd/{REF}.png", "pecas": {}}
    for nome, img in imgs.items():
        junta, mae, _ = OSSOS[nome]
        guardar(kit, nome, img, junta, mae, REF, ref)
    for slot, vs in VARIANTES.items():
        junta, mae, _ = OSSOS[slot]
        for var, (fonte, poli, junta_fonte) in vs.items():
            f = b.abrir(fonte)
            mm = b.mascara(poli) & (f[..., 3] > 0)
            M = np.float32([[1, 0, junta[0] - junta_fonte[0]], [0, 1, junta[1] - junta_fonte[1]]])
            img = cv2.warpAffine(np.where(mm[..., None], f, 0).astype(np.uint8), M, TELA, flags=cv2.INTER_NEAREST)
            if var in SOB_CABECA:  # raiz do braço: tira a barba e a sombra do pescoço que vieram junto (mancha escura)
                escuro = (img[..., :3].astype(int).sum(-1) < 230) & disco(junta, 18) & (img[..., 3] > 0)
                img[escuro] = 0
            guardar(kit, f"{slot}_{var}", img, junta, mae, fonte, cv2.warpAffine(f, M, TELA, flags=cv2.INTER_NEAREST))
    (b.PECAS / "kit.json").write_text(json.dumps(kit, indent=1, ensure_ascii=False), encoding="utf-8")
    return kit


def guardar(kit, nome, img, junta, mae, fonte, fonte_img):
    a = img[..., 3] > 0
    ys, xs = np.nonzero(a)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    Image.fromarray(img[y0:y1, x0:x1]).save(b.PECAS / f"{nome}.png")
    disco = np.zeros(TELA[::-1], np.uint8)
    cv2.circle(disco, (int(junta[0]), int(junta[1])), SOBRA, 1, -1)
    sob = np.where((disco.astype(bool) & (fonte_img[..., 3] > 0))[..., None], fonte_img, 0).astype(np.uint8)
    Image.fromarray(sob[y0 - SOBRA:y1 + SOBRA, x0 - SOBRA:x1 + SOBRA]).save(b.PECAS / f"{nome}_sobra.png")
    kit["pecas"][nome] = {"arquivo": f"{nome}.png", "origem": [int(x0), int(y0)], "junta": list(junta), "mae": mae,
                          "fonte": f"quadros_arcade_hd/{fonte}.png", "sobra": f"{nome}_sobra.png",
                          "origem_sobra": [int(x0 - SOBRA), int(y0 - SOBRA)]}


# variantes: a peça muda de desenho (não de ângulo). Desenho de onde sai, polígono nele e a junta nele.
VARIANTES = {
    "braco_frente": {
        # braço esticado saindo de baixo do queixo (jab e direto de hoje); a raiz fica por baixo da cabeça
        "jab": ("soco/02", [(522, 388), (538, 380), (560, 382), (578, 377), (596, 372), (614, 377), (623, 388),
                            (621, 403), (608, 411), (590, 411), (575, 409), (555, 410), (538, 414), (524, 408)],
                (533, 398)),
        "direto": ("soco/05", [(538, 392), (552, 385), (575, 388), (590, 386), (602, 382), (618, 380), (640, 384),
                               (648, 396), (646, 410), (632, 418), (612, 418), (600, 410), (585, 408), (565, 410),
                               (548, 412), (538, 405)], (546, 398)),
    },
}
SOB_CABECA = {"jab", "direto"}  # variantes de braço que passam por baixo da cabeça


# ------------------------------------------------------------------ poses (encaixe em cima do desenho-guia)
def configurar():
    b.OSSOS = OSSOS
    b.CAMADAS = CAMADAS
    b.ORDEM = ["quadril", "tronco", "cabeca", "braco_tras", "braco_frente", "coxa_tras", "canela_tras",
               "coxa_frente", "canela_frente"]
    b.BUSCA = {
        "quadril": (range(-8, 9, 2), 30, [None]),
        "tronco": (range(-10, 11, 2), 3, [None]),
        "cabeca": (range(-6, 7, 2), 3, [None]),
        "braco_tras": (range(-30, 46, 3), 4, [None]),  # variante de braço só por pose escrita (POSES)
        "braco_frente": (range(-45, 46, 3), 4, [None]),
        "coxa_tras": (range(-30, 31, 2), 3, [None]),
        "canela_tras": (range(-30, 31, 2), 3, [None]),
        "coxa_frente": (range(-40, 41, 2), 3, [None] + list(VARIANTES.get("coxa_frente", {}))),
        "canela_frente": (range(-40, 41, 2), 3, [None]),
    }
    b.ANGULOS_VARIANTE = range(-30, 31, 3)
    b.PESO_GIRO = 0.35
    b.FOLGA_VARIANTE = {"coxa_frente": 4, "braco_tras": 5, "braco_frente": 5}


def cinza(a):
    rgb = a[..., :3].astype(np.float32)
    rgb[a[..., 3] == 0] = 110.0
    return rgb


def corpo(kit, alvo, folga=80, pecas=("cabeca",)):
    """(dx, dy) do corpo do kit no desenho, pela cabeça (boné e rosto mudam pouco de um desenho para outro; o tronco
    gira e enganava o casamento). Só translação: corpo firme."""
    t = np.zeros((TELA[1], TELA[0], 4), np.uint8)
    for nome in pecas:
        p = kit["pecas"][nome]
        x0, y0 = p["origem"]
        h, w = p["img"].shape[:2]
        sub = t[y0:y0 + h, x0:x0 + w]
        m = p["img"][..., 3] > 0
        sub[m] = p["img"][m]
    ref = b.abrir(REF)
    t[..., 3] = np.where((t[..., 3] > 0) & (ref[..., 3] > 0) & (np.abs(t.astype(int) - ref.astype(int)).sum(-1) == 0),
                         255, 0)  # só o que é desenho de verdade (sem o peito pintado)
    ys, xs = np.nonzero(t[..., 3] > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    tm = t[y0:y1, x0:x1]
    X0, Y0 = max(0, x0 - folga), max(0, y0 - folga)
    reg = alvo[Y0:y1 + folga, X0:x1 + folga]
    m = (tm[..., 3] > 0).astype(np.uint8)
    r = cv2.matchTemplate(cinza(reg), cinza(tm), cv2.TM_SQDIFF, mask=np.repeat(m[..., None], 3, -1))
    _, _, p_min, _ = cv2.minMaxLoc(r)
    return p_min[0] + X0 - x0, p_min[1] + Y0 - y0


def pes(a):
    faixa = a[CHAO - 22:CHAO + 3, :, 3].any(0)
    xs = np.nonzero(faixa)[0]
    if not len(xs):
        return []
    runs = np.split(xs, np.nonzero(np.diff(xs) > 3)[0] + 1)
    return [(r.min() + r.max()) / 2 for r in runs if len(r) > 6]


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
    j1, j2 = q + u * a + n * h, q + u * a - n * h
    j = j1 if j1[0] >= j2[0] else j2  # o joelho dobra para a frente (o CK olha para a direita)
    ang = lambda v: np.degrees(np.arctan2(v[1], v[0]))
    coxa = ang(j - q) - ang(jr - qr)
    canela = ang(t - j) - ang(tr - jr) - coxa
    return round(float(coxa), 1), round(float(canela), 1)


PES_REF = None


def pernas_no_chao(pose, alvo, quais=("tras", "frente"), sob_quadril=False, passo=None):
    """Pé plantado onde o pé do desenho-guia está; joelho por IK (o osso não muda de tamanho)."""
    global PES_REF
    if PES_REF is None:
        PES_REF = pes(b.abrir(REF))
    agora = pes(alvo)
    w = b.mundo(pose)
    for perna in quais:
        coxa, canela = f"coxa_{perna}", f"canela_{perna}"
        i = 0 if perna == "tras" else -1
        qr, jr = OSSOS[coxa][0], OSSOS[canela][0]
        tr = TORNOZELO[canela]
        dx = (agora[i] - PES_REF[i]) if agora and (i == 0 or len(agora) > 1) else 0
        if sob_quadril:  # pé de apoio do chute: embaixo do quadril, como no parado
            dx = pose["quadril"].get("dx", 0) - 4
        if passo and perna in passo:  # passo escrito à mão: o pé anda junto com o corpo (soco de boxe)
            dx = passo[perna] + (pose["quadril"].get("dx", 0) if passo.get("com_corpo") else 0)
        c1, c2 = ik(w[coxa][0], (tr[0] + dx, tr[1]), jr, qr, tr)
        pose[coxa] = {"ang": round(c1 - w["quadril"][1], 1)}  # relativo ao quadril (que pode estar inclinado)
        pose[canela] = {"ang": c2}
    return pose


DOBRA_MAX = 0.88  # quadril até o tornozelo: no mínimo 88% da perna esticada (o CK tem canela curta: mais que isso o joelho quebra)

# poses escritas à mão por cima do encaixe (quadro confuso ou golpe que precisa de exatidão). Cada entrada:
#   "guia": outro desenho para o encaixe; slots com {"ang", "var", "dx", "dy"} fixos; "corpo": (dx, dy) somado
G = {"braco_tras": {"ang": 0}, "braco_frente": {"ang": 0}}  # guarda


def chute(coxa, canela, lean=None, bt=0, bf=0, corpo=(0, 0)):
    p = {"braco_tras": {"ang": bt}, "braco_frente": {"ang": bf}, "coxa_frente": {"ang": coxa},
         "canela_frente": {"ang": canela}, "corpo": corpo}
    if lean is not None:
        p["lean"] = lean
    return p


def soco(corpo, passo, giro, bf=None, bt=None, cab=0):
    """Soco de boxe: o corpo vai junto (corpo_abs), o pé da frente dá o passo, o quadril gira para a frente (giro
    inclina o tronco por cima do pé da frente) e o pé de trás fica plantado."""
    p = {"corpo_abs": corpo, "passo": {"frente": passo, "tras": 0}, "quadril_ang": giro,
         "braco_frente": bf or {"ang": 0}, "braco_tras": bt or {"ang": 0}, "cabeca": {"ang": cab}}
    return p


SOCOS = {
    # jab: meio passo, ombro da frente entra, braço sai de baixo do queixo
    "soco/00": soco((0, 0), 0, 0),
    "soco/01": soco((8, 3), 12, 4, bf={"ang": -6}, cab=2),
    "soco/02": soco((24, 6), 30, 10, bf={"ang": -3, "var": "jab", "dy": -10}, cab=4),
    "soco/03": soco((12, 3), 18, 4, bf={"ang": -4}, cab=2),
    # direto (cruzado): o quadril gira inteiro, o pé da frente avança mais e o corpo cai por cima dele
    "soco/04": soco((2, 3), 6, -3, bt={"ang": -6}, bf={"ang": -10}, cab=-2),
    "soco/05": soco((40, 9), 44, 15, bf={"ang": -3, "var": "direto", "dy": -10}, bt={"ang": 10}, cab=6),
    "soco/06": soco((18, 4), 22, 6, bf={"ang": -6}, bt={"ang": 4}, cab=2),
    "soco/07": soco((3, 1), 4, 1),
}


AGACHA = (-80, 96, -84, 98, 4)  # postura do agachado (coxas quase deitadas, canelas em pé)


def baixo(qa=8, bf=None, bt=None, cab=0, pp=AGACHA):
    return {"postura": pp, "quadril_ang": qa, "braco_frente": bf or {"ang": 0}, "braco_tras": bt or {"ang": 0},
            "cabeca": {"ang": cab}}


BAIXOS = {
    # chute baixo de rua: joelho sobe, canela estala na altura do joelho do outro, volta pelo mesmo caminho
    "chute_baixo/01": chute(-20, 30, lean=-2),
    "chute_baixo/02": chute(-60, 85, lean=-5, bt=2, bf=3),
    "chute_baixo/03": chute(-55, 20, lean=-8, bt=4, bf=5),
    "chute_baixo/04": chute(-62, 4, lean=-10, bt=5, bf=6),
    "chute_baixo/05": chute(-55, 80, lean=-6, bt=3, bf=4),
    "chute_baixo/06": chute(-25, 40, lean=-2, bt=1, bf=1),
    # soco agachado: agacha, o ombro entra e a mão sai reta na altura da cintura do outro
    **{f"baixo_soco/{i:02d}": baixo() for i in (0, 1, 7)},
    "baixo_soco/02": baixo(qa=11, bf={"ang": -8}, cab=2),
    "baixo_soco/03": baixo(qa=16, bf={"ang": -3, "var": "jab", "dy": -10}, cab=4),
    "baixo_soco/04": baixo(qa=18, bf={"ang": 2, "var": "direto", "dy": -10}, bt={"ang": 6}, cab=5),
    "baixo_soco/05": baixo(qa=13, bf={"ang": -6}, cab=3),
    "baixo_soco/06": baixo(qa=10, bf={"ang": -3}, cab=1),
    # rasteira: agacha fundo, a perna da frente sai varrendo rente ao chão e volta
    "rasteira/00": baixo(),
    "rasteira/01": baixo(qa=14, pp=(-86, 104, -86, 100, 0)),
    "rasteira/02": baixo(qa=16, pp=(-88, 106, -60, 50, -4, 0.8)),
    "rasteira/03": baixo(qa=18, pp=(-90, 108, -50, 10, -8, 0.95), cab=2),
    "rasteira/04": baixo(qa=20, pp=(-90, 108, -50, 4, -10, 0.99), bt={"ang": 4}, bf={"ang": 4}, cab=3),
    "rasteira/05": baixo(qa=16, pp=(-88, 106, -60, 50, -6, 0.85)),
    "rasteira/06": baixo(qa=10, pp=(-82, 98, -84, 98, 0)),
    "rasteira/07": baixo(),
}


POSES = {
    # Chute alto (Bicuda de Pedreiro / chute frontal): joelho sobe, perna estica na altura do peito, recolhe
    "chute_alto/01": chute(-45, 60, lean=-4, bt=4, bf=6),
    "chute_alto/02": chute(-88, 105, lean=-8, bt=6, bf=8),
    "chute_alto/03": chute(-95, 50, lean=-14, bt=8, bf=10),
    "chute_alto/04": chute(-98, 8, lean=-18, bt=10, bf=12),
    "chute_alto/05": chute(-88, 100, lean=-10, bt=6, bf=8),
    "chute_alto/06": chute(-40, 55, lean=-4, bt=3, bf=4),
    # Chute alto de rua / pisão (afastar): avança a mão para medir, chuta reto
    "afastar/01": {"braco_tras": {"ang": 0}, "braco_frente": {"ang": -6}},
    "afastar/02": chute(-20, 25, lean=-2, bt=0, bf=-10),
    "afastar/03": chute(-85, 100, lean=-8, bt=4, bf=-6),
    "afastar/04": chute(-92, 6, lean=-16, bt=8, bf=0),
    "afastar/05": chute(-60, 70, lean=-8, bt=4, bf=4),
    # socos: o corpo entra junto com a mão (passo de boxe), o braço é o desenho esticado de hoje no tamanho do kit
    # agachado: agachamento de verdade (coxa quase deitada, canela em pé), tronco inclinado para a frente
    "agachado/01": {"postura": (-45, 55, -50, 55), "quadril_ang": 4},
    **{f"agachado/{i:02d}": {"postura": AGACHA, "quadril_ang": 8} for i in range(2, 8)},
    # defesa: luvas sobem na frente do rosto, queixo baixo
    **{f"defesa/{i:02d}": {"braco_tras": {"ang": -22}, "braco_frente": {"ang": -26, "dx": -6}, "cabeca": {"ang": 6},
                           "quadril_ang": 3} for i in range(2, 7)},
    **SOCOS,
    **BAIXOS,
}


def limitar_agachada(pose, alvo, quais=("tras", "frente")):
    """Sobe o quadril se o desenho-guia agacha mais do que as pernas do kit deixam sem dobrar o joelho demais."""
    agora = pes(alvo)
    if not agora:
        return pose
    pr = PES_REF or pes(b.abrir(REF))
    for _ in range(80):
        w = b.mundo(pose)
        ok = True
        for perna, i in (("tras", 0), ("frente", -1)):
            if perna not in quais or (perna == "frente" and len(agora) < 2):
                continue
            coxa, canela = f"coxa_{perna}", f"canela_{perna}"
            qr, jr, tr = OSSOS[coxa][0], OSSOS[canela][0], TORNOZELO[canela]
            l = np.hypot(jr[0] - qr[0], jr[1] - qr[1]) + np.hypot(tr[0] - jr[0], tr[1] - jr[1])
            t = (tr[0] + agora[i] - pr[i], tr[1])
            q = w[coxa][0]
            if np.hypot(t[0] - q[0], t[1] - q[1]) < DOBRA_MAX * l:
                ok = False
        if ok:
            break
        pose["quadril"]["dy"] -= 1
    return pose


QUADRIL_CABECA = 130  # do quadril ao meio da cabeça no parado (3x)
# folhas de chute: a perna da frente sobe (coxa até 120°, canela solta)
CHUTE = {"chute_alto", "afastar", "chute_baixo"}
# folhas em que os braços ficam na guarda e só balançam (o desenho de hoje encolhe e o encaixe girava demais)
GUARDA = {"referencia_ginga", "anda", "agachado", "pulo", "queda"}


def pose_de(kit, guia, no_chao=True):
    """Pose-chave das peças em cima do desenho-guia (nome 'folha/NN')."""
    configurar()
    if guia.split("/")[0] in GUARDA:
        for s_ in ("braco_tras", "braco_frente"):
            b.BUSCA[s_] = (range(-8, 9, 2), 3, [None])
    if guia.split("/")[0] in CHUTE:
        b.BUSCA["coxa_frente"] = (range(-120, 21, 3), 4, [None])
        b.BUSCA["canela_frente"] = (range(-100, 101, 3), 4, [None])
    fixo = POSES.get(guia, {})
    alvo = b.abrir(fixo.get("guia", guia))
    dx, dy = fixo["corpo_abs"] if "corpo_abs" in fixo else corpo(kit, alvo)
    cdx, cdy = fixo.get("corpo", (0, 0))
    ang = 0
    if "lean" in fixo:
        dx = 0.3 * dx
        ang = fixo["lean"]
    elif guia.split("/")[0] in CHUTE:  # no chute o quadril fica em cima do pé de apoio e o tronco inclina para trás
        fica = 0.3 * dx
        ang = float(np.degrees(np.arcsin(np.clip((dx - fica) / QUADRIL_CABECA, -0.6, 0.6))))
        dx = fica
    ang += fixo.get("quadril_ang", 0)
    pose = {"quadril": {"ang": round(ang, 1), "dx": int(round(dx + cdx)), "dy": int(dy + cdy)}}
    perna_fixa = "coxa_frente" in fixo
    if no_chao and perna_fixa:  # apoio quase esticado: o quadril fica na altura do parado (só a inclinação muda)
        pose["quadril"]["dy"] = min(pose["quadril"]["dy"], 4)
    elif no_chao and pes(alvo):
        pose["quadril"]["dy"] = max(pose["quadril"]["dy"], 0)  # de pé no chão não fica mais alto que o parado
        pose = limitar_agachada(pose, alvo)
    livres = [s_ for s_ in ("cabeca", "braco_tras", "braco_frente") if s_ not in fixo]
    for s_ in ("cabeca", "braco_tras", "braco_frente"):
        if s_ in fixo:
            pose[s_] = dict(fixo[s_])
    pose = b.encaixar(kit, alvo, pose, ordem=livres)
    n_pes = len(pes(alvo))
    if perna_fixa:
        pose["coxa_frente"] = {"ang": fixo["coxa_frente"]["ang"] - pose["quadril"]["ang"]}
        pose["canela_frente"] = dict(fixo["canela_frente"])
        pose = pernas_no_chao(pose, alvo, ("tras",), sob_quadril=True)
    elif no_chao and "passo" in fixo:
        pose = pernas_no_chao(pose, alvo, passo=fixo["passo"])
    elif no_chao and n_pes >= 2:
        pose = pernas_no_chao(pose, alvo)
    elif no_chao and n_pes == 1:
        pose = pernas_no_chao(pose, alvo, ("tras",))
        pose = b.encaixar(kit, alvo, pose, ordem=["coxa_frente", "canela_frente"])
    else:
        pose = b.encaixar(kit, alvo, pose, ordem=["coxa_tras", "canela_tras", "coxa_frente", "canela_frente"])
    for s_ in ("coxa_tras", "canela_tras", "coxa_frente", "canela_frente"):
        if s_ in fixo and not (perna_fixa and s_.endswith("_frente")):
            pose[s_] = dict(fixo[s_])
    if "postura" in fixo:
        pose = postura(pose, fixo["postura"])
    return pose


def postura(pose, pp):
    """Pernas escritas à mão (agachado, rasteira...): pp = (coxa_tras, canela_tras, coxa_frente, canela_frente),
    ângulos no mundo da coxa e relativos da canela. O corpo desce até o pé de trás encostar no chão (no x do parado
    + pe_dx) e a perna da frente acha o chão por IK, então os dois pés ficam no chão e nenhum osso estica."""
    ct, kt, cf, kf = pp[:4]
    pe_dx = pp[4] if len(pp) > 4 else 0
    qa = pose["quadril"]["ang"]
    pose["coxa_tras"], pose["canela_tras"] = {"ang": ct - qa}, {"ang": kt}
    pose["coxa_frente"], pose["canela_frente"] = {"ang": cf - qa}, {"ang": kf}
    def tornozelo(perna):
        w = b.mundo(pose)
        c = f"canela_{perna}"
        pos, ang = w[c]
        jr = OSSOS[c][0]
        t = b.girar(TORNOZELO[c], jr, ang)
        return t[0] + pos[0] - jr[0], t[1] + pos[1] - jr[1]
    tx, ty = tornozelo("tras")
    pose["quadril"]["dx"] += int(round(TORNOZELO["canela_tras"][0] + pe_dx - tx))
    pose["quadril"]["dy"] += int(round(TORNOZELO["canela_tras"][1] - ty))
    fx, _ = tornozelo("frente")
    w = b.mundo(pose)
    qr, jr, tr = OSSOS["coxa_frente"][0], OSSOS["canela_frente"][0], TORNOZELO["canela_frente"]
    if len(pp) > 5 and pp[5]:  # rasteira: a perna da frente vai quase esticada varrendo o chão
        l = np.hypot(jr[0] - qr[0], jr[1] - qr[1]) + np.hypot(tr[0] - jr[0], tr[1] - jr[1])
        q = w["coxa_frente"][0]
        fx = q[0] + np.sqrt(max((pp[5] * l) ** 2 - (tr[1] - q[1]) ** 2, 0))
    c1, c2 = ik(w["coxa_frente"][0], (fx, tr[1]), jr, qr, tr)
    pose["coxa_frente"], pose["canela_frente"] = {"ang": round(c1 - w["quadril"][1], 1)}, {"ang": c2}
    return pose


# ------------------------------------------------------------------ desenho
def separar_pes(kit):
    """Tira o pé (tênis) de cada canela e guarda à parte: o pé fica reto no chão e preso no tornozelo."""
    kit["pes"] = {}
    for slot, (tx, ty) in TORNOZELO.items():
        p = kit["pecas"][slot]
        img = p["img"].copy()
        ox, oy = p["origem"]
        corte = ty - oy
        pe = np.zeros_like(img)
        pe[corte:] = img[corte:]
        img[corte + 4:] = 0  # 4 linhas de sobra: a canela cobre o começo do pé, sem fresta
        p["img"] = img
        kit["pes"][slot] = {"img": pe, "origem": (ox, oy), "tornozelo": (tx, ty),
                            "fundo": int(np.nonzero(pe[..., 3].any(1))[0].max())}
    return kit


PELE = True  # pele que dobra nas juntas (ferramentas/pele_pecas.py): sem linha de corte entre as peças


def colar_pe(tela, kit, slot, pos, ang):
    """Pé no chão fica reto e apoiado (sem afundar); pé no ar gira junto com a canela."""
    pe = kit["pes"][slot]
    jr = OSSOS[slot][0]
    t = b.girar(pe["tornozelo"], jr, ang)
    tx, ty = t[0] + pos[0] - jr[0], t[1] + pos[1] - jr[1]
    x0 = int(round(pe["origem"][0] + tx - pe["tornozelo"][0]))
    y0 = int(round(pe["origem"][1] + ty - pe["tornozelo"][1]))
    fundo = pe["fundo"] + y0
    r, x1, y1 = b.colocar({"junta": pe["tornozelo"]}, pe["img"], pe["origem"], (tx, ty), ang)
    fundo_girado = y1 + int(np.nonzero(r[..., 3].any(1))[0].max())
    if abs(fundo - CHAO) <= 3 or fundo_girado > CHAO or fundo > CHAO:
        b.colar(tela, pe["img"], x0, y0 + CHAO - fundo)
    else:
        b.colar(tela, r, x1, y1)


def desenhar(kit, pose):
    if PELE:
        import pele_pecas as pele
        w = b.mundo(pose)
        tela = pele.desenhar(kit, pose)
        if "pes" in kit:
            for slot in ("canela_tras", "canela_frente"):
                if not (slot == "canela_frente" and pose.get("coxa_frente", {}).get("var")):
                    colar_pe(tela, kit, slot, *w[slot])
        if pose.get("braco_frente", {}).get("var") in SOB_CABECA:  # raiz do braço esticado fica debaixo do queixo
            cab = kit["pecas"][b.chave("cabeca", pose)]
            r, x0, y0 = b.colocar(cab, cab["img"], cab["origem"], *w["cabeca"])
            b.colar(tela, r, x0, y0)
        return tela
    w = b.mundo(pose)
    tela = np.zeros((TELA[1], TELA[0], 4), np.uint8)
    ordem = list(CAMADAS)
    if pose.get("braco_frente", {}).get("var") in SOB_CABECA:
        ordem.remove("braco_frente")
        ordem.insert(ordem.index("cabeca"), "braco_frente")
    usados = []
    for slot in ordem:
        if slot == "canela_frente" and pose.get("coxa_frente", {}).get("var"):
            continue
        p = kit["pecas"][b.chave(slot, pose)]
        pos, ang = w[slot]
        r, x0, y0 = b.colocar(p, p["img"], p["origem"], pos, ang)
        b.colar(tela, r, x0, y0)
        usados.append((p, pos, ang))
        if slot.startswith("canela") and "pes" in kit:
            pe = kit["pes"][slot]
            jr = OSSOS[slot][0]
            t = b.girar(pe["tornozelo"], jr, ang)
            tx, ty = t[0] + pos[0] - jr[0], t[1] + pos[1] - jr[1]
            x0 = int(round(pe["origem"][0] + tx - pe["tornozelo"][0]))
            y0 = int(round(pe["origem"][1] + ty - pe["tornozelo"][1]))
            fundo = pe["fundo"] + y0
            r, x1, y1 = b.colocar({"junta": pe["tornozelo"]}, pe["img"], pe["origem"], (tx, ty), ang)
            fundo_girado = y1 + int(np.nonzero(r[..., 3].any(1))[0].max())
            if abs(fundo - CHAO) <= 3 or fundo_girado > CHAO or fundo > CHAO:  # pé no chão: reto, apoiado, sem afundar
                y0 += CHAO - fundo
                b.colar(tela, pe["img"], x0, y0)
            else:  # pé no ar: gira junto com a canela (o chute leva o pé)
                b.colar(tela, r, x1, y1)
    for p, pos, ang in usados:
        r, x0, y0 = b.colocar(p, p["sob"], p["origem_sobra"], pos, ang)
        b.colar(tela, r, x0, y0, so_vazio=True)
    return tela


# ------------------------------------------------------------------ limpeza, robô de defeitos e saída
def rachas(tela):
    """Transparente cercado pela figura cuja beirada não é contorno escuro: racha entre duas peças."""
    al = (tela[..., 3] > 0).astype(np.uint8)
    fora = np.pad(1 - al, 1, constant_values=1)
    _, labf = cv2.connectedComponents(fora.astype(np.uint8), connectivity=4)
    cercado = ((labf != labf[0, 0]) & (fora > 0))[1:-1, 1:-1]
    nb, labb, stb, _ = cv2.connectedComponentsWithStats(cercado.astype(np.uint8), connectivity=4)
    escuro = tela[..., :3].astype(int).sum(-1) < 260
    out = np.zeros(al.shape, bool)
    for i in range(1, nb):
        m = labb == i
        borda = (cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & ~m & (al > 0)
        if stb[i, 4] > 2 and escuro[borda].mean() < 0.6:
            out |= m
    return out


def limpar(tela, pose):
    import piloto_firme as pf
    juntas = [w[0] for w in b.mundo(pose).values()]
    tela = pf.fechar_frestas(tela, juntas=juntas)
    r = rachas(tela)
    if r.any():  # fecha a racha com a cor de volta
        rgb = cv2.inpaint(np.ascontiguousarray(tela[..., :3]), r.astype(np.uint8), 3, cv2.INPAINT_TELEA)
        tela = tela.copy()
        tela[r, :3] = rgb[r]
        tela[r, 3] = 255
    return pf.sem_migalha(tela)


def conferir(tela, guia):
    """Defeitos do desenho montado. Vazio = passou.
      solta   pedaço da figura separado do resto (peça desgrudou)
      buraco  furo transparente por dentro do boneco (o fundo apareceria no jogo)
      chão    o desenho de hoje tem o pé no chão e o montado não (ou afundou)
      tamanho a figura ficou mais alta que o parado (osso esticou)"""
    erros = []
    al = (tela[..., 3] > 0).astype(np.uint8)
    n, _, st, _ = cv2.connectedComponentsWithStats(al, connectivity=8)
    soltos = sorted(int(x) for x in st[1:, 4])[:-1]
    if soltos:
        erros.append(f"solta {soltos}")
    fora = np.pad(1 - al, 1, constant_values=1)
    nf, labf = cv2.connectedComponents(fora.astype(np.uint8), connectivity=4)
    cercado = ((labf != labf[0, 0]) & (fora > 0))[1:-1, 1:-1]  # transparente cercado pela figura
    nb, labb, stb, _ = cv2.connectedComponentsWithStats(cercado.astype(np.uint8), connectivity=4)
    escuro = tela[..., :3].astype(int).sum(-1) < 260
    ruins = []
    for i in range(1, nb):
        m = labb == i
        borda = (cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & ~m & (al > 0)
        # vão de ar desenhado (luva perto do queixo, entre braço e corpo) tem contorno escuro em volta; racha de peça
        # que soltou mostra a cor de dentro da peça cortada
        if stb[i, 4] > 2 and escuro[borda].mean() < 0.6:
            ruins.append(int(stb[i, 4]))
    if ruins:
        erros.append(f"racha {ruins} px")
    ys = np.nonzero(al.any(1))[0]
    g = b.abrir(guia)
    yg = np.nonzero((g[..., 3] > 0).any(1))[0]
    if yg.max() >= CHAO - 4 and not (CHAO - 4 <= ys.max() <= CHAO + 2):
        erros.append(f"chão: pé em y={ys.max()} (hoje {yg.max()})")
    ref = np.nonzero((b.abrir(REF)[..., 3] > 0).any(1))[0]
    if ys.max() - ys.min() > (ref.max() - ref.min()) * 1.02 and yg.max() >= CHAO - 4:
        erros.append(f"tamanho {ys.max() - ys.min()} px (parado {ref.max() - ref.min()})")
    return erros


# ações para a prova (mesmos desenhos, ticks e elementos de acerto do gerar_ck.py)
ACOES = {
    "parado": ("referencia_ginga", tuple(range(8)), (5,) * 8, None, 0),
    "jab": ("soco", (0, 1, 1, 2, 2, 3, 7), (1, 1, 2, 1, 2, 3, 4), (3, 4), 200),
    "cruzado": ("soco", (3, 4, 5, 5, 6, 6, 7), (4, 3, 1, 3, 6, 5, 5), (2, 3), 210),
    "chute_alto": ("chute_alto", (1, 2, 3, 4, 5, 6, 7), (5, 4, 1, 3, 2, 8, 8), (2, 3), 240),
    "chute_de_rua": ("afastar", (1, 2, 3, 4, 4, 5, 6, 7), (4, 4, 4, 1, 3, 8, 6, 6), (3, 4), 260),
    "agachando": ("agachado", (2,), (2,), None, 10),
    "agachado": ("agachado", (4, 5, 6, 7, 6, 5), (8,) * 6, None, 11),
    "levantando": ("agachado", (2,), (2,), None, 12),
    "cruzado_rapido": ("soco", (3, 4, 5, 5, 6, 6, 7), (2, 2, 1, 2, 6, 4, 4), (2, 3), 215),
    "chute_alto_rapido": ("chute_alto", (1, 2, 3, 4, 5, 6, 7), (3, 2, 1, 2, 6, 5, 5), (2, 3), 245),
    "chute_baixo": ("chute_baixo", (1, 2, 3, 4, 5, 6, 7), (3, 2, 1, 2, 3, 3, 3), (2, 3), 230),
    "soco_agachado": ("baixo_soco", (1, 2, 3, 4, 4, 5, 6), (2, 1, 1, 1, 2, 4, 3), (3, 4), 400),
    "rasteira": ("rasteira", (1, 2, 3, 4, 5, 6, 7), (5, 5, 1, 3, 8, 7, 7), (2, 3), 440),
}
OUT_HD, OUT_1X = SPR / "quadros_pecas_hd", SPR / "quadros_pecas"  # <ação>/ (o ligar_pecas.py lê) e chaves/<folha>/
LACOS = {"parado", "agachado"}  # ações em laço: respiram


@functools.lru_cache(None)
def _sff_ck():
    import conferir_sff as cs
    _, nos, _ = cs.ler(RAIZ / "chars/ck/ck.sff")
    return {(n["g"], n["i"]): n for n in nos}


def do_jogo(acao, folha):
    """Elementos da ação como estão hoje no chars/ck (o .air já passou pela pose segurada e pelos ajustes de tempo):
    [(desenho da folha, ticks)] e os índices com Clsn1. O desenho é achado pelo formato (alfa) do sprite HD."""
    import re as _re
    air = (RAIZ / "chars/ck/ck.air").read_text(encoding="utf-8", errors="replace")
    m = _re.search(rf"^\[Begin Action {acao}\][^\n]*\n(.*?)(?=^\[Begin Action|\Z)", air, _re.M | _re.S)
    sff = _sff_ck()
    def recorte(a):
        ys, xs = np.nonzero(a)
        return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

    def iou_(a, m):  # formato contra formato, alinhados pelo canto da caixa (o jogo desloca o desenho: ANCORA)
        H, W = max(a.shape[0], m.shape[0]), max(a.shape[1], m.shape[1])
        A, M = np.zeros((H, W), bool), np.zeros((H, W), bool)
        A[:a.shape[0], :a.shape[1]], M[:m.shape[0], :m.shape[1]] = a, m
        return (A & M).sum() / (A | M).sum()

    cands = {k: recorte(b.abrir(f"{folha}/{k:02d}")[..., 3] > 0) for k in range(8)}
    des, ticks, ativos, clsn1 = [], [], [], False
    for linha in m.group(1).splitlines():
        t = linha.strip()
        if t.lower().startswith("clsn1:"):
            clsn1 = True
            continue
        el = _re.match(r"^(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)", t)
        if not el:
            continue
        g, i, _, _, tk = map(int, el.groups())
        n = sff[(g, i)]
        mask = recorte(np.frombuffer(n["px"], np.uint8).reshape(n["h"], n["w"]) != 0)
        iou = {k: iou_(c, mask) for k, c in cands.items()}
        best = max(iou, key=iou.get)
        assert iou[best] > 0.6, f"ação {acao}: sprite {g},{i} não é da folha {folha} ({iou[best]:.2f})"
        if clsn1:
            ativos.append(len(des))
        des.append(best)
        ticks.append(max(tk, 0) if tk >= 0 else 8)
        clsn1 = False
    return tuple(des), tuple(ticks), tuple(ativos) or None


SECO = False  # True liga a regra 7 seca nos golpes (o Alisson pediu fluidez; o Breno decide na #45)


def segurado(poses, elems, bate):
    """Golpes, reações, defesa e agachar (regras-dos-lutadores, seção 7): pose segurada e troca seca. Só antes do
    contato entram no máximo 2 quadros de smear a 1 tick, tirados do fim da antecipação (o tempo total não muda)."""
    import vida_pecas as vida
    saida = []
    for k, (q, t) in enumerate(elems):
        a = poses[q]
        if bate is not None and k == bate - 1 and t >= 3:
            c = poses[elems[bate][0]]
            saida.append((dict(a), t - 2, False, q))
            saida += [(vida.misturar(a, c, f), 1, False, q) for f in (0.4, 0.75)]
        else:
            saida.append((dict(a), t, k == bate, q))
    return saida


def gerar(nomes=None):
    import vida_pecas as vida
    configurar()
    kit = separar_pes(b.ler_kit())
    nomes = nomes or list(ACOES)
    poses, relatorio = {}, ["| desenho | guia de hoje | robô de defeitos |", "|---|---|---|"]
    falhas = 0
    for nome in nomes:
        folha, des, ticks, ativos, acao = ACOES[nome]
        if (RAIZ / "chars/ck/ck.air").exists():  # tempos e quadros ativos do jogo de hoje (têm de bater no ligar_pecas.py)
            des, ticks, ativos = do_jogo(acao, folha)
        elems = [(f"{folha}/{d:02d}", t) for d, t in zip(des, ticks)]
        for q, _ in elems:
            if q not in poses:
                poses[q] = pose_de(kit, q)
        laco = nome in LACOS
        bate = ativos[0] if ativos else None
        if SECO and not laco:  # regra 7 ao pé da letra: pose segurada e troca seca
            quadros = segurado(poses, elems, bate)
        else:  # pedido do Alisson (fluidez e vida): quadros do meio, mesmo tempo total e caixa no mesmo tick
            quadros = vida.animar(poses, elems, bate=bate, laco=laco, guarda=poses.get(f"{folha}/00"))
            if laco:
                quadros = vida.respirar(quadros)
            quadros = vida.atrasar(quadros, laco=laco)
        for pasta in (OUT_HD, OUT_1X):
            shutil.rmtree(pasta / nome, ignore_errors=True)
            (pasta / nome).mkdir(parents=True)
        caixa_k = set(ativos or ())
        elementos, k_el, tick = [], 0, 0
        lim = np.cumsum(ticks)
        for i, (pose, t, _, q) in enumerate(quadros):
            out = limpar(desenhar(kit, pose), pose)
            erros = conferir(out, q)
            falhas += bool(erros)
            relatorio.append(f"| {nome}/{i:02d} | {q} | {'PASS' if not erros else 'FAIL ' + '; '.join(erros)} |")
            Image.fromarray(out).save(OUT_HD / nome / f"{i:02d}.png")
            Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(OUT_1X / nome / f"{i:02d}.png")
            while tick >= lim[k_el]:
                k_el += 1
            elementos.append({"desenho": i, "ticks": t, "caixa": k_el in caixa_k, "de": q})
            tick += t
        assert sum(e["ticks"] for e in elementos) == sum(ticks)
        tempos = {"acao": acao, "folha": folha, "elementos": elementos,
                  "hoje": [{"de": q, "ticks": t, "caixa": k in caixa_k} for k, (q, t) in enumerate(elems)]}
        for pasta in (OUT_HD, OUT_1X):
            (pasta / nome / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False),
                                                               encoding="utf-8")
        print(nome, len(set(q for q, _ in elems)), "poses-chave ->", len(quadros), "desenhos")
    # os 8 desenhos-chave de cada folha usada, no mesmo índice que o gerador lê hoje (o jogo troca a folha inteira)
    for folha in sorted({q.split("/")[0] for q in poses}):
        for i in range(8):
            q = f"{folha}/{i:02d}"
            if q not in poses:
                poses[q] = pose_de(kit, q)
                erros = conferir(limpar(desenhar(kit, poses[q]), poses[q]), q)
                falhas += bool(erros)
                relatorio.append(f"| {q} (folha) | {q} | {'PASS' if not erros else 'FAIL ' + '; '.join(erros)} |")
    for q, pose in poses.items():
        folha, i = q.split("/")
        for pasta in (OUT_HD, OUT_1X):
            (pasta / "chaves" / folha).mkdir(parents=True, exist_ok=True)
        out = limpar(desenhar(kit, pose), pose)
        Image.fromarray(out).save(OUT_HD / "chaves" / folha / f"{i}.png")
        Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(OUT_1X / "chaves" / folha / f"{i}.png")
    guarda = limpar(desenhar(kit, {}), {})
    Image.fromarray(guarda).save(OUT_HD / "guarda.png")
    (b.PECAS / "poses.json").write_text(json.dumps(poses, indent=1, default=float), encoding="utf-8")
    texto = "\n".join(relatorio) + f"\n\n{falhas} desenho(s) com defeito.\n"
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "robo_defeitos.md").write_text(texto, encoding="utf-8")
    print(f"robô: {falhas} desenho(s) com defeito de {len(relatorio) - 2}")
    return falhas


DOCS = RAIZ / "docs" / "boneco-pecas" / "ck"


def video(saida=None):
    """Lado a lado (hoje x peças) a 60 fps, tira de ticks e folha antes/depois, de cada ação em ACOES."""
    import subprocess
    from PIL import ImageDraw, ImageFont
    saida = Path(saida or DOCS)
    saida.mkdir(parents=True, exist_ok=True)
    try:
        fonte = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except OSError:
        fonte = ImageFont.load_default()
    corte, k = (400, 290, 740, 670), 2

    def quadro(caminho):
        f = Image.open(caminho).convert("RGBA")
        bg = Image.new("RGBA", f.size, (60, 60, 70, 255))
        bg.alpha_composite(f)
        c = bg.crop(corte)
        return c.resize((c.width * k, c.height * k), Image.NEAREST).convert("RGB")

    w, h = (corte[2] - corte[0]) * k, (corte[3] - corte[1]) * k
    for nome in ACOES:
        tempos = json.loads((OUT_HD / nome / "tempos.json").read_text(encoding="utf-8"))
        a = [b.HD / f"{e['de']}.png" for e in tempos["hoje"] for _ in range(e["ticks"])]
        n = [OUT_HD / nome / f"{e['desenho']:02d}.png" for e in tempos["elementos"] for _ in range(e["ticks"])]
        if nome != "parado":
            ga, gn = b.HD / f"{REF}.png", OUT_HD / "guarda.png"
            a, n = [ga] * 20 + a + [ga] * 20, [gn] * 20 + n + [gn] * 20
        tmp = saida / f"_{nome}"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir()
        cache = {}
        total = len(a)
        for i in range(total * (6 if nome == "parado" else 4)):
            par = (a[i % total], n[i % total])
            if par not in cache:
                img = Image.new("RGB", (w * 2, h + 44), (40, 40, 48))
                img.paste(quadro(par[0]), (0, 44))
                img.paste(quadro(par[1]), (w, 44))
                d = ImageDraw.Draw(img)
                d.text((12, 8), f"{nome}: hoje no jogo", fill=(255, 230, 120), font=fonte)
                d.text((w + 12, 8), f"{nome}: boneco de peças", fill=(255, 230, 120), font=fonte)
                cache[par] = img
            cache[par].save(tmp / f"{i:05d}.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "60", "-i", str(tmp / "%05d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16",
                        str(saida / f"{nome}_lado_a_lado.mp4")], check=True)
        shutil.rmtree(tmp)
        # antes (desenhos de hoje, sem repetir) em cima e depois (todos os desenhos novos) embaixo
        antes = list(dict.fromkeys(e["de"] for e in tempos["hoje"]))
        depois = sorted((OUT_HD / nome).glob("[0-9][0-9].png"))
        tw, th = w // 2, h // 2
        col = max(len(antes), len(depois))
        folha = Image.new("RGB", (tw * col, th * 2 + 80), (40, 40, 48))
        d = ImageDraw.Draw(folha)
        d.text((8, 6), "antes (jogo hoje)", fill=(255, 230, 120), font=fonte)
        d.text((8, th + 46), "depois (boneco de peças, com os quadros do meio)", fill=(255, 230, 120), font=fonte)
        for i, q in enumerate(antes):
            folha.paste(quadro(b.HD / f"{q}.png").resize((tw, th)), (i * tw, 36))
        for i, q in enumerate(depois):
            folha.paste(quadro(q).resize((tw, th)), (i * tw, th + 76))
        folha.save(saida / f"{nome}_antes_depois.png")
        print(nome, "ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "acoes"
    if cmd == "kit":
        montar_kit()
    elif cmd == "ver":
        ver(DOCS / "kit_sobre_parado.png")
    elif cmd == "acoes":
        gerar(sys.argv[2:] or None)
    elif cmd == "video":
        video()
