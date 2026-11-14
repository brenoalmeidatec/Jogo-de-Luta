#!/usr/bin/env python3
"""Pengaró com o desenho de antes (folhas_arcade), só que nítido e com a pele bem escura.

  python ferramentas/nitidez_pengaro.py                 todas as folhas da forma normal (quadros_arcade/, sem e_)
  python ferramentas/nitidez_pengaro.py soco parado     só essas
  python ferramentas/nitidez_pengaro.py --contato DIR   folhas de contato (1x com a garrafa marcada e o 3x)

Por que o Pengaró antigo borrava: na folha antiga (2172x724) o boneco tem ~275 px de altura; o do CK, na mesma folha,
~550 px. O 3x do jogo precisa de ~330 px: o CK é REDUZIDO (nítido) e o Pengaró era AMPLIADO, e o hd_guiado.py ainda
repintava cada pixel só com as cores do quadro 1x numa vizinhança 3x3 (sumiam olho, boca e contorno do rosto).

O que este script faz, sem mudar desenho, pose, escala nem posição (o 1x continua sendo a autoridade):
  1. Folha ampliada: se existe quadros/folhas_arcade_sr/<folha>.png (a folha antiga passada num super-resolução, que
     só amplia, ver docs/arcade/pengaro-nitido.md), as figuras vêm dela; senão, da folha antiga mesmo.
  2. Para cada quadros_arcade/<folha>/NN.png acha a figura e a escala/posição em que ela foi colada (hd_guiado) e cola
     a figura em 3x. A figura grande é REDUZIDA para o 3x (como no CK), não ampliada.
  3. Pinta cada pixel 3x com a cor mais perto (em Lab) entre as cores do quadro 1x numa vizinhança 5x5 (não 3x3): o
     3x continua na paleta e nos papéis de cor do 1x, mas os detalhes finos da folha (olho, boca, dedos) sobrevivem.
  4. Pele bem escura (pedido do Breno, docs/arcade/pengaro.md): as 5 cores de pele da paleta viram as escuras, como
     troca de cor, nos dois tamanhos. A garrafa (que usa as mesmas cores no vidro e no rótulo) é achada em cada quadro
     e fica como era. O endiabrado (e_*) não é tocado.
Rodar de novo é seguro: o script clareia o 1x de volta antes de casar com a folha e escurece de novo no fim.
Depois: python ferramentas/gerar_pengaro.py && python ferramentas/trocar_retratos.py pengaro
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "ferramentas"))
import hd_guiado as hg  # noqa: E402

E = 3
BASE = RAIZ / "sprites/pengaro"
Q1, QHD = BASE / "quadros_arcade", BASE / "quadros_arcade_hd"
FOLHAS, FOLHAS_SR = BASE / "quadros/folhas_arcade", BASE / "quadros/folhas_arcade_sr"


def _c(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# papel: (cor de antes, cor nova). Proposta de docs/arcade/pengaro.md: mais escuro que o Gutto em cada tom.
PELE = {
    "pele_contorno": (_c("4C1414"), _c("3A1416")),
    "pele_sombra": (_c("8A321C"), _c("47201A")),
    "pele_medio": (_c("DF7E3F"), _c("723F1E")),
    "pele_luz": (_c("FDC372"), _c("A2753E")),
    "pele_brilho": (_c("FDECCF"), _c("D9A066")),
}
CLARA_ESCURA = {a: b for a, b in PELE.values()}
ESCURA_CLARA = {b: a for a, b in PELE.values()}
CONT, SOMBRA = PELE["pele_contorno"][0], PELE["pele_sombra"][0]
G_ESC, G_AMB, BRANCO = _c("5F1A14"), _c("DF7814"), _c("FDFAED")
CLAROS = (PELE["pele_brilho"][0], BRANCO, PELE["pele_luz"][0])


def _eq(rgb, c):
    return np.all(rgb == c, axis=2)


def trocar(a, mapa, poupar=None):
    """Troca as cores de `mapa` em `a` (RGBA), menos onde `poupar` é verdadeiro."""
    out = a.copy()
    rgb = a[..., :3]
    for de, para in mapa.items():
        m = _eq(rgb, de) & (a[..., 3] >= 128)
        if poupar is not None:
            m &= ~poupar
        out[m, :3] = para
    return out


# Cores que a folha antiga usa na pele E em outra coisa: o creme e o claro da pele sombreiam a calça branca, e o âmbar
# da garrafa (que também pinta a corda amarela) faz a luz da pele em algumas folhas (derrota). Cada mancha dessas cores
# vai para o lado (pele ou roupa) que mais encosta nela.
AMBIGUAS = (PELE["pele_brilho"][0], PELE["pele_luz"][0], G_AMB)
NUCLEO = (PELE["pele_medio"][0], PELE["pele_sombra"][0], _c("332C20"))  # + cabelo: o brilho do cabelo acompanha a pele
ROUPA = (BRANCO, _c("9492BD"), _c("351F5C"), _c("149C63"), _c("14503F"), _c("FDC514"), G_ESC)
AMBAR_PELE = PELE["pele_medio"][1]  # âmbar que é luz da pele vira o médio escuro


def pele_ambigua(a):
    """Máscara (1x) dos pixels de cor ambígua que são pele: cada mancha 4-conexa da cor vai para a pele quando a
    borda dela encosta mais em pele (médio, sombra) que em roupa, corda ou garrafa."""
    rgb = a[..., :3].astype(int)
    op = a[..., 3] >= 128
    nucleo = np.zeros(op.shape, bool)
    for c in NUCLEO:
        nucleo |= _eq(rgb, c)
    roupa = np.zeros(op.shape, bool)
    for c in ROUPA:
        roupa |= _eq(rgb, c)
    out = np.zeros(op.shape, bool)
    for c in AMBIGUAS:
        m = (_eq(rgb, c) & op).astype(np.uint8)
        n, rot = cv2.connectedComponents(m, connectivity=4)
        if n <= 1:
            continue
        borda = cv2.dilate(m, np.ones((3, 3), np.uint8)) > 0
        # conta por mancha os vizinhos de pele e de roupa (rótulo da mancha espalhado 1 px)
        esp = cv2.dilate(rot.astype(np.float32), np.ones((3, 3), np.uint8)).astype(int)
        esp = np.where(borda & (m == 0), esp, 0)
        pele_n = np.bincount(esp[nucleo], minlength=n)
        roupa_n = np.bincount(esp[roupa], minlength=n)
        sim = pele_n > roupa_n
        sim[0] = False
        out |= sim[rot] & (m > 0)
    return out


def escurecer(a, garrafa, pele=None):
    """Pele escura em `a` (RGBA claro), poupando `garrafa`. `pele`: máscara das cores ambíguas que são pele (a do 1x
    ampliada, no 3x); sem ela, calculada aqui."""
    pele = pele_ambigua(a) if pele is None else pele
    out = a.copy()
    rgb = a[..., :3]
    op = (a[..., 3] >= 128) & ~garrafa
    for de, para in CLARA_ESCURA.items():
        m = _eq(rgb, de) & op
        if de in AMBIGUAS:
            m &= pele
        out[m, :3] = para
    out[_eq(rgb, G_AMB) & op & pele, :3] = AMBAR_PELE
    return out


def ampliar_mascara(m, folga=1):
    return cv2.dilate(np.repeat(np.repeat(m, E, 0), E, 1).astype(np.uint8), np.ones((2 * folga + 1,) * 2, np.uint8)) > 0


# ---------------------------------------------------------------- garrafa
def candidatos(a, minimo_vidro=3, minimo_anel=0.4):
    """Rótulos possíveis num quadro 1x claro: mancha clara compacta cercada de vidro escuro, com cor da garrafa perto.
    Devolve [(nota, centro (x, y), máscara)]."""
    rgb = a[..., :3].astype(int)
    op = a[..., 3] >= 128
    vidro = (_eq(rgb, G_ESC) | _eq(rgb, G_AMB)) & op
    escuro = (_eq(rgb, CONT) | _eq(rgb, SOMBRA)) & op | vidro
    claro = np.zeros(op.shape, bool)
    for c in CLAROS:
        claro |= _eq(rgb, c)
    claro &= op
    n, rot, st, cen = cv2.connectedComponentsWithStats(claro.astype(np.uint8), connectivity=4)
    out = []
    for j in range(1, n):
        x, y, w, h, area = st[j]
        if area < 15 or area > 260:
            continue
        m = (rot == j).astype(np.uint8)
        anel = (cv2.dilate(m, np.ones((5, 5), np.uint8)) > 0) & (m == 0)
        f = (escuro & anel).sum() / max(1, (anel & op).sum())
        perto = (cv2.dilate(m, np.ones((9, 9), np.uint8)) > 0) & _eq(rgb, G_ESC) & op
        cheio = area / (w * h)
        if perto.sum() < minimo_vidro or f < minimo_anel or cheio < 0.4:
            continue
        # o rótulo é a maior mancha clara compacta da figura: área conta (brilho de músculo é pequeno)
        out.append((f * cheio * np.sqrt(area / 50), (cen[j][0], cen[j][1]), m > 0))
    return out


def garrafa_de(a, rotulo):
    """Rótulo + vidro: o que não é contorno, ligado ao rótulo, até 4 px dele."""
    rgb = a[..., :3].astype(int)
    op = a[..., 3] >= 128
    raio = cv2.dilate(rotulo.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    nao = op & ~_eq(rgb, CONT) & raio
    _, r2 = cv2.connectedComponents(nao.astype(np.uint8), connectivity=4)
    ids = np.unique(r2[rotulo])
    m = np.isin(r2, ids[ids > 0])
    # o contorno colado na garrafa também fica (senão a borda dela escurecia)
    borda = (cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & _eq(rgb, CONT) & op
    return m | borda


def garrafas(quadros, nome=""):
    """Máscara da garrafa em cada quadro da folha.

    1. Na maioria dos quadros a garrafa está na mão de trás, no mesmo lugar em relação à caixa do corpo: a posição
       mediana dos candidatos fortes da folha é a referência.
    2. Candidato (mesmo fraco) a menos de 0.15 da referência ganha; sem nenhum perto (o gole, a garrafa erguida),
       fica o candidato forte de maior nota.
    3. GARRAFA_MAO corrige à mão o que a regra erra: (folha, quadro) -> ponto (x, y) do rótulo no 1x, ou None."""
    cands, fracos, caixas = [], [], []
    for a in quadros:
        ys, xs = np.nonzero(a[..., 3] >= 128)
        caixas.append((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1) if len(xs) else (0, 0, 1, 1))
        cands.append(candidatos(a))
        fracos.append(candidatos(a, 1, 0.3))

    def rel(c, cx):
        return np.array(((c[0] - cx[0]) / max(1, cx[2] - cx[0]), (c[1] - cx[1]) / max(1, cx[3] - cx[1])))

    fortes = [rel(max(cs, key=lambda t: t[0])[1], cx) for cs, cx in zip(cands, caixas) if cs]
    ref = np.median(np.array(fortes), axis=0) if fortes else None
    out = []
    for k, (a, cs, fs, cx) in enumerate(zip(quadros, cands, fracos, caixas)):
        vazio = np.zeros(a.shape[:2], bool)
        if (nome, k) in GARRAFA_MAO:
            ponto = GARRAFA_MAO[nome, k]
            if ponto is None:
                out.append(vazio)
                continue
            dono = [m for _, _, m in fs if m[ponto[1], ponto[0]]]
            if not dono:  # ponto fora de qualquer rótulo: o rótulo é a mancha clara que contém o ponto
                claro = np.zeros(a.shape[:2], bool)
                for c in CLAROS:
                    claro |= _eq(a[..., :3].astype(int), c)
                _, rot = cv2.connectedComponents(claro.astype(np.uint8), connectivity=4)
                ys, xs = np.nonzero(claro[ponto[1] - 4:ponto[1] + 5, ponto[0] - 4:ponto[0] + 5])
                if len(xs):  # o ponto foi marcado à mão: vale a mancha clara mais perto dele (até 4 px)
                    k = np.argmin((xs - 4) ** 2 + (ys - 4) ** 2)
                    dono = [rot == rot[ponto[1] - 4 + ys[k], ponto[0] - 4 + xs[k]]]
                else:
                    dono = []
            out.append(garrafa_de(a, dono[0]) if dono else vazio)
            continue
        perto = [t for t in fs if ref is not None and np.hypot(*(rel(t[1], cx) - ref)) < 0.15]
        if perto:
            out.append(garrafa_de(a, max(perto, key=lambda t: t[0])[2]))
        elif cs:
            out.append(garrafa_de(a, max(cs, key=lambda t: t[0])[2]))
        else:
            out.append(vazio)
    return out


# Ajuste à mão (conferido na folha de contato): (folha, quadro) -> (x, y) de um ponto do rótulo no quadro 1x, ou None
# quando a garrafa não aparece. Preenchido depois de olhar `--garrafas`.
GARRAFA_MAO = {
    ("agarrao", 0): (148, 176), ("apanha", 1): (147, 177), ("armada", 0): (148, 181), ("bola", 5): (148, 179),
    ("cabecada", 5): (136, 153), ("chute_alto", 0): (146, 183), ("chute_baixo", 7): (150, 184),
    ("defesa", 3): (148, 181), ("derrota", 0): (143, 182), ("parado", 3): (148, 195), ("pulo", 3): (143, 195),
    ("recuo", 0): (146, 181), ("vitoria", 6): (189, 151), ("vitoria", 7): (178, 149),
    ("vitoria", 1): (150, 118), ("vitoria", 3): (202, 120), ("vitoria", 4): (198, 112), ("vitoria", 5): (197, 113),
    ("levanta", 2): (170, 213), ("rasteira", 1): (144, 210),
    ("rolamento", 2): None,  # no giro a garrafa some atrás do corpo; a mancha clara é pele
}


# ---------------------------------------------------------------- 3x
def _lab(rgb):
    return cv2.cvtColor(rgb.astype(np.uint8).reshape(-1, 1, 3), cv2.COLOR_RGB2LAB).reshape(rgb.shape).astype(np.int32)


def pintar(alta, q1, raio=2):
    """Cada pixel de `alta` (RGBA 3x) com a cor de `q1` (1x) mais perto em Lab, numa vizinhança (2*raio+1)^2; o vizinho
    mais longe paga um pouco a mais (empate fica com a cor do próprio ponto)."""
    H, W = alta.shape[:2]
    pad = np.pad(q1.astype(np.int32), ((raio, raio), (raio, raio), (0, 0)))
    L = _lab(alta[..., :3])
    melhor = np.full((H, W), 1 << 30, np.int64)
    cor = np.zeros((H, W, 3), np.int32)
    for dy in range(-raio, raio + 1):
        for dx in range(-raio, raio + 1):
            viz = pad[raio + dy:raio + dy + q1.shape[0], raio + dx:raio + dx + q1.shape[1]]
            viz = np.repeat(np.repeat(viz, E, axis=0), E, axis=1)[:H, :W]
            d = ((L - _lab(viz[..., :3])) ** 2).sum(axis=2).astype(np.int64) + 30 * (abs(dx) + abs(dy))
            d = np.where(viz[..., 3] >= 128, d, 1 << 30)
            t = d < melhor
            melhor = np.where(t, d, melhor)
            cor[t] = viz[..., :3][t]
    op = (alta[..., 3] >= 128) & (melhor < 1 << 30)
    out = np.zeros((H, W, 4), np.uint8)
    out[op, :3] = cor[op]
    out[op, 3] = 255
    return out


def figuras(nome):
    """Figuras da folha (da ampliada, se houver) e o fator dela sobre a folha antiga."""
    sr = FOLHAS_SR / f"{nome}.png"
    if sr.exists():
        return hg.figuras(Image.open(sr)), Image.open(sr).width / Image.open(FOLHAS / f"{nome}.png").width
    return hg.figuras(Image.open(FOLHAS / f"{nome}.png")), 1.0


def converter(nome):
    pasta = Q1 / nome
    arqs = sorted(pasta.glob("[0-9][0-9].png"))
    claros = [trocar(np.asarray(Image.open(p).convert("RGBA")), ESCURA_CLARA) for p in arqs]
    mascaras = garrafas(claros, nome)
    tem_folha = (FOLHAS / f"{nome}.png").exists()
    figs_alta, fator = figuras(nome) if tem_folha else ([], 1.0)
    figs_base = hg.figuras(Image.open(FOLHAS / f"{nome}.png")) if tem_folha and fator != 1.0 else figs_alta
    notas = []
    (QHD / nome).mkdir(parents=True, exist_ok=True)
    for p, q1, mg in zip(arqs, claros, mascaras):
        Image.fromarray(escurecer(q1, mg)).save(p)
        # 3x: registrar contra a folha antiga (mesma conta do hd_guiado) e colar a figura da folha ampliada
        alvo = q1[..., 3] >= 128
        i = int(p.stem)
        melhor = None
        for k in ([i] if 0 <= i < len(figs_base) else []) + [k for k in range(len(figs_base)) if k != i]:
            r = hg.registrar(alvo, figs_base[k])
            if r and (melhor is None or r[0] > melhor[0][0]):
                melhor = (r, k)
            if melhor and melhor[0][0] >= .9:
                break
        if not melhor or melhor[0][0] < .8 or len(figs_alta) != len(figs_base):
            (QHD / nome / p.name).unlink(missing_ok=True)
            notas.append(f"{p.stem}:sem")
            continue
        (iou, f, x, y), k = melhor
        fb, fa = figs_base[k], figs_alta[k]
        fig = Image.fromarray(fa)
        w, h = max(1, round(fb.shape[1] * f * E)), max(1, round(fb.shape[0] * f * E))
        g = fig.resize((w, h), Image.LANCZOS)
        tela = Image.new("RGBA", (q1.shape[1] * E, q1.shape[0] * E))
        tela.paste(g, (x * E, y * E), g)
        alta = pintar(np.asarray(tela), q1)
        # no 3x: a garrafa e a pele das cores ambíguas vêm do 1x (ampliadas com 1 px de folga)
        Image.fromarray(escurecer(alta, ampliar_mascara(mg), ampliar_mascara(pele_ambigua(q1)))).save(QHD / nome / p.name)
        notas.append(f"{p.stem}:{iou:.2f}{'' if mg.any() else '(sem garrafa)'}")
    # quadros do meio do Blender (quadros_arcade/<folha>/meio/): o gerador usa alguns (m_<folha>_NN_k), em 1x ampliado.
    # Ficam com o desenho de sempre; só a pele escurece, com a garrafa achada do mesmo jeito.
    meio = sorted((pasta / "meio").glob("*.png"))
    if meio:
        claros_m = [trocar(np.asarray(Image.open(p).convert("RGBA")), ESCURA_CLARA) for p in meio]
        for p, q, mg in zip(meio, claros_m, garrafas(claros_m)):
            Image.fromarray(escurecer(q, mg)).save(p)
    print(f"{nome}{' [folha ampliada x%.1f]' % fator if fator != 1 else ''}: {' '.join(notas)}"
          + (f" (+{len(meio)} do meio)" if meio else ""), flush=True)


# Linhas de sprites/pengaro/paleta_sff.act (255 cores fixas do .sff, todas ocupadas) que recebem as 5 cores escuras
# da pele: as de menos uso no .sff (medido em 2026-11-14), cada uma com uma vizinha quase igual que fica com os pixels
# dela. 144 #A62E6F: 0 pixels; 209 #391E5E: 30 px, vizinha a dE 2,2; 134 #984219: 117 px, dE 3,0; 115 #C152F8: 31 px,
# dE 4,4; 163 #6F2D69: 107 px, dE 6,9. Os pixels que mudam são de efeito (faísca e aura), por uma cor vizinha.
LINHAS_ACT = (144, 209, 134, 115, 163)


def paleta_sff():
    """Põe as cores escuras da pele na paleta fixa do .sff (sem elas o gerador as trocaria pela cor mais perto)."""
    arq = BASE / "paleta_sff.act"
    b = bytearray(arq.read_bytes())
    linhas = [tuple(b[k * 3:k * 3 + 3]) for k in range(256)]
    faltam = [c for _, c in PELE.values() if c not in linhas]
    if not faltam:
        return
    assert len(faltam) == len(LINHAS_ACT), "paleta_sff.act com só parte das cores escuras: confira à mão"
    for k, c in zip(LINHAS_ACT, faltam):
        b[k * 3:k * 3 + 3] = bytes(c)
    arq.write_bytes(bytes(b))
    print("paleta_sff.act: cores escuras da pele nas linhas", LINHAS_ACT)


def contato(destino, nomes):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    for nome in nomes:
        tiras = []
        for p in sorted((Q1 / nome).glob("[0-9][0-9].png")):
            a = np.asarray(Image.open(p).convert("RGBA"))
            hd = QHD / nome / p.name
            b = np.asarray(Image.open(hd).convert("RGBA")) if hd.exists() else np.repeat(np.repeat(a, E, 0), E, 1)
            tiras.append(Image.fromarray(b))
        if not tiras:
            continue
        cx = tiras[0].getbbox()
        for t in tiras[1:]:
            b = t.getbbox() or cx
            cx = (min(cx[0], b[0]), min(cx[1], b[1]), max(cx[2], b[2]), max(cx[3], b[3]))
        w, h = cx[2] - cx[0], cx[3] - cx[1]
        folha = Image.new("RGBA", (w * len(tiras), h), (48, 48, 56, 255))
        for k, t in enumerate(tiras):
            folha.alpha_composite(t.crop(cx), (k * w, 0))
        folha.save(destino / f"{nome}.png")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    todas = sorted(p.name for p in Q1.iterdir() if p.is_dir() and not p.name.startswith("e_"))
    if args[:1] == ["--contato"]:
        contato(args[1], args[2:] or todas)
    else:
        for n in args or todas:
            converter(n)
        paleta_sff()
