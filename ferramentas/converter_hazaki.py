#!/usr/bin/env python3
"""Hazak (forma base) nítido, issue #36: converte as folhas grandes de sprites/hazaki/quadros/folhas_novas/ (boneco
com ~500 px, ChatGPT) direto nos desenhos do jogo, em 1x e em 3x, como o converter_pengaro.py. Sem o hd_guiado.py.

  python ferramentas/converter_hazaki.py                 todas as folhas novas
  python ferramentas/converter_hazaki.py soco chute      só essas
  python ferramentas/converter_hazaki.py --paleta        refaz sprites/hazaki/paleta_nitida.json com as folhas que há
  python ferramentas/converter_hazaki.py --cabeca         escala de cada folha pela cabeça contra o parado (escala_cabeca.json)
  python ferramentas/converter_hazaki.py --contato DIR   antes e depois de cada folha convertida (3x, lado a lado)
  python ferramentas/converter_hazaki.py --de PASTA ...  lê as folhas de outra pasta (teste)

Saída: quadros_arcade/<folha>/00..07.png (360x260, pés em 180,220) e quadros_arcade_hd/<folha>/00..07.png (1080x780,
pés em 540,660), os dois tirados da MESMA folha grande: o 3x tem o detalhe da folha, não é o 1x ampliado nem repintado.

O que garante que o jogo não muda (caixas, .air e .cns ficam como estão):
  - escala folha por folha: a mediana do tamanho de cada figura nova contra o desenho de antes da mesma pose (os
    desenhos de antes vêm do git, commit ANTES), respeitando as exceções por quadro do FATOR antigo;
  - posição quadro por quadro: a figura nova entra onde a silhueta dela mais cobre a silhueta de antes, com a base na
    mesma linha;
  - cor: toda folha é pintada com a mesma paleta (paleta_nitida.json): as 15 cores do Hazak mais os tons do meio que
    as folhas grandes trazem (olho, dente, sombra do músculo). Assim a cor não varia de folha para folha e o corpo
    continua nos primeiros índices da paleta do .sff, que é como o diabo_loiro.py reconhece o corpo.
Alfa seco (sem mistura na borda) e sem franja rosa.
"""
import io
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import folhas_hazak_arcade as fh  # noqa: E402
from recortar_quadros import tira_fundo  # noqa: E402

RAIZ = fh.RAIZ
SPRITES = fh.SPRITES
FOLHAS = SPRITES / "quadros/folhas_novas"
PALETA = SPRITES / "paleta_nitida.json"
ANTES = "6e7ff73a"   # último commit da mugen com os desenhos de antes (hd_guiado) em quadros_arcade/
CABECA = SPRITES / "escala_cabeca.json"   # correção de escala por folha, medida pela cabeça (--cabeca)
LIMITE_CABECA = 0.06  # a régua tem 4 a 5% de ruído em desenho novo: só corrige acima disso
EXTRAS = 25          # tons do meio além das 15 cores do Hazak (40 no total)
NAO_CORPO = ("d_conceito",)
E = 3


def fundo_magenta(img):
    """O fundo com degradê vira #FF00FF exato, para o tira_fundo levar também o vão entre braço e tronco."""
    a = np.array(img.convert("RGB"))
    r, g, b = (a[..., i].astype(int) for i in range(3))
    a[(r > 170) & (b > 170) & (g < 130) & (np.abs(r - b) < 60)] = (255, 0, 255)
    return Image.fromarray(a)


def figuras(folha):
    """As 8 figuras da folha (RGBA recortadas), na ordem. A folha nova vem em grade de 2 fileiras por 4 colunas (ver
    fila_hazak_nitido.py); folha larga (uma fileira de 8) também serve. Cada pedaço vai para a célula onde está o
    centro dele. Faixa clara em cima ou embaixo vira fundo antes do recorte."""
    a = np.array(fundo_magenta(Image.open(folha)))
    magenta = (a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255)
    linhas = np.flatnonzero(magenta.mean(axis=1) > 0.2)
    if len(linhas) and (linhas[0] > 0 or linhas[-1] < a.shape[0] - 1):
        a[:linhas[0] + 4] = (255, 0, 255)
        a[max(0, linhas[-1] - 3):] = (255, 0, 255)
    limpa = fh.limpa_franja(np.array(tira_fundo(Image.fromarray(a))))
    cheio = limpa[..., 3] > 0
    col, fil = (8, 1) if a.shape[1] > 2.4 * a.shape[0] else (4, 2)
    cw, ch = a.shape[1] / col, a.shape[0] / fil
    n, rot, dados, centros = cv2.connectedComponentsWithStats(cheio.astype(np.uint8), connectivity=8)
    celula = np.full(n, -1)
    for i in range(1, n):
        if dados[i, cv2.CC_STAT_AREA] >= 30:
            celula[i] = min(fil - 1, int(centros[i][1] // ch)) * col + min(col - 1, int(centros[i][0] // cw))
        if dados[i, cv2.CC_STAT_WIDTH] > 1.5 * cw or (fil > 1 and dados[i, cv2.CC_STAT_HEIGHT] > 1.2 * ch):
            raise SystemExit(f"{Path(folha).stem}: duas figuras grudadas na folha (gere de novo)")
    saida = []
    for k in range(8):
        fig = Image.fromarray(np.where((celula[rot] == k)[..., None], limpa, 0).astype(np.uint8))
        caixa = fig.getchannel("A").getbbox()
        saida.append(fig.crop(caixa) if caixa else None)
    return saida


def antigos(nome):
    """Os 8 desenhos 1x de antes (git, commit ANTES): dão a escala e a posição de cada figura nova."""
    out = []
    for i in range(8):
        b = subprocess.run(["git", "show", f"{ANTES}:sprites/hazaki/quadros_arcade/{nome}/{i:02d}.png"],
                           cwd=RAIZ, capture_output=True).stdout
        out.append(Image.open(io.BytesIO(b)).convert("RGBA") if b else None)
    if not any(out) and nome.startswith("parry_"):
        out = antigos_parry(nome)
    return out


def antigos_parry(nome):
    """O parry não tinha quadros_arcade: o parry.py cortava a folha velha (quadros/folhas_arcade) direto em 3x, com o
    1º quadro da altura da guarda (1º desenho da defesa em pé). Refaz esse corte e põe na tela 1x de sempre."""
    import parry
    b = subprocess.run(["git", "show", f"{ANTES}:sprites/hazaki/quadros_arcade_hd/defesa/00.png"],
                       cwd=RAIZ, capture_output=True).stdout
    cx = Image.open(io.BytesIO(b)).getchannel("A").getbbox()
    out = []
    for q, ex, ey in parry.quadros_parry("hazaki", nome, cx[3] - cx[1]):
        tela = Image.new("RGBA", (fh.LARG * E, fh.ALT * E))
        tela.paste(q, (fh.LARG * E // 2 - ex, 220 * E - ey), q)
        out.append(tela.resize((fh.LARG, fh.ALT), Image.LANCZOS))
    return out


def lado(q):
    cx = q.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox()
    return max(cx[2] - cx[0], cx[3] - cx[1]) if cx else 0


# ---------------------------------------------------------------- cor
def lab(rgb):
    return cv2.cvtColor(np.asarray(rgb, np.uint8).reshape(1, -1, 3), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)


def base15():
    return [tuple(int(h[k:k + 2], 16) for k in (1, 3, 5)) for _, _, h in fh.CORES]


def fazer_paleta(pasta):
    """15 cores do Hazak + EXTRAS tons do meio: k-médias (em Lab) dos pixels das folhas que ficam longe das 15."""
    amostra = []
    for folha in sorted(pasta.glob("*.png")):
        if folha.stem.startswith(("patroa_", "obj_")) or folha.stem in NAO_CORPO:
            continue
        for q in acertar_cor(figuras(folha), antigos(folha.stem)):
            a = np.asarray(seco(q.resize((max(1, q.width // 2), max(1, q.height // 2)), Image.LANCZOS)))
            amostra.append(a[a[..., 3] > 0][:, :3])
    px = np.concatenate(amostra)
    px = px[:: max(1, len(px) // 400000)]
    pl, bl = lab(px), lab(base15())
    longe = np.linalg.norm(pl[:, None] - bl[None], axis=2).min(axis=1) > 9
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 60, 0.2)
    cv2.setRNGSeed(7)
    _, rot, centros = cv2.kmeans(pl[longe], EXTRAS, None, crit, 4, cv2.KMEANS_PP_CENTERS)
    conta = np.bincount(rot.ravel(), minlength=EXTRAS)
    extras = cv2.cvtColor(centros[np.argsort(-conta)].reshape(1, -1, 3).clip(0, 255).astype(np.uint8),
                          cv2.COLOR_LAB2RGB).reshape(-1, 3)
    cores = base15() + [tuple(int(v) for v in c) for c in extras]
    assert len(set(cores)) == len(cores), "cor repetida na paleta"
    PALETA.write_text(json.dumps({
        "lutador": "hazaki", "nota": "Hazak nítido (#36): as 15 cores de paleta_arcade.json e os tons do meio das "
        "folhas grandes. Escrito por ferramentas/converter_hazaki.py --paleta; o gerar_hazaki.py põe o corpo nestes "
        "índices do .sff.", "cores": [{"id": fh.CORES[i][0] if i < 15 else f"meio_{i - 14:02d}", "rgb": list(c)}
                                      for i, c in enumerate(cores)]}, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8")
    print(f"paleta: {len(cores)} cores ({longe.mean():.0%} dos pixels pediam tom do meio)")


def paleta():
    return np.array([c["rgb"] for c in json.loads(PALETA.read_text(encoding="utf-8"))["cores"]], np.uint8)


def pintar(q, pal):
    """Cada pixel opaco vai para a cor mais próxima da paleta (em Lab), sem pontilhado."""
    a = np.array(q)
    op = a[..., 3] > 0
    d = np.linalg.norm(lab(a[op][:, :3])[:, None] - lab(pal)[None], axis=2)
    a[op, :3] = pal[d.argmin(axis=1)]
    return Image.fromarray(a)


GRUPOS = sorted({g for _, g, _ in fh.CORES})


def grupo_de(px_lab):
    """Grupo (pele, roupa, debrum, faixa, atadura, pulseira) da cor do Hazak mais próxima de cada pixel."""
    d = np.linalg.norm(px_lab[:, None] - lab(base15())[None], axis=2).argmin(axis=1)
    return np.array([GRUPOS.index(g) for _, g, _ in fh.CORES])[d]


def acertar_cor(figs, velhos):
    """O ChatGPT devolve a mesma roupa um pouco mais viva (o gi puxa para o roxo). Aqui cada grupo de cor da folha
    nova (pele, roupa, debrum...) é levado para a média do mesmo grupo nos desenhos de antes, e o claro-escuro para a
    mesma abertura: a cor do jogo não muda e não varia de folha para folha."""
    def pixels(imgs):
        return np.concatenate([np.asarray(q)[np.asarray(q)[..., 3] >= 128][:, :3] for q in imgs])
    novo, velho = lab(pixels(figs)), lab(pixels(velhos))
    gn, gv = grupo_de(novo[:: max(1, len(novo) // 200000)]), grupo_de(velho[:: max(1, len(velho) // 200000)])
    novo, velho = novo[:: max(1, len(novo) // 200000)], velho[:: max(1, len(velho) // 200000)]
    ajuste = {}
    for g in range(len(GRUPOS)):
        a, b = novo[gn == g], velho[gv == g]
        if len(a) < 200 or len(b) < 200:
            continue
        escala = np.array([np.clip(b[:, 0].std() / max(1e-3, a[:, 0].std()), 0.8, 1.25), 1, 1], np.float32)
        ajuste[g] = (a.mean(axis=0), escala, b.mean(axis=0))
    saida = []
    for q in figs:
        a = np.array(q)
        op = a[..., 3] > 0
        px = lab(a[op][:, :3])
        gs = grupo_de(px)
        for g, (ma, escala, mb) in ajuste.items():
            m = gs == g
            px[m] = (px[m] - ma) * escala + mb
        a[op, :3] = cv2.cvtColor(px.clip(0, 255).astype(np.uint8).reshape(1, -1, 3), cv2.COLOR_LAB2RGB).reshape(-1, 3)
        saida.append(Image.fromarray(a))
    return saida


def seco(q):
    a = fh.limpa_franja(np.array(q))
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    # franja rosa que sobra na borda depois de reduzir: pixel de borda puxado para o magenta sai
    r, g, b = (a[..., i].astype(int) for i in range(3))
    op = a[..., 3] > 0
    borda = op & (cv2.erode(op.astype(np.uint8), np.ones((3, 3), np.uint8)) == 0)
    a[borda & (r > 120) & (b > 90) & (g < 0.7 * np.minimum(r, b))] = 0
    return Image.fromarray(a)


# ---------------------------------------------------------------- posição
def encaixe(nova, velha):
    """x da esquerda da figura nova (1x) na tela, onde a silhueta dela mais cobre a de antes; e a linha da base."""
    cx = velha.getchannel("A").getbbox()
    mv = np.asarray(velha)[..., 3] > 0
    mn = np.asarray(nova)[..., 3] > 0
    h, w = mn.shape
    base = cx[3]
    centro = (cx[0] + cx[2]) // 2 - w // 2
    melhor, nota = centro, -1
    for x in range(centro - 20, centro + 21):
        y = base - h
        if x < 0 or y < 0 or x + w > fh.LARG:
            continue
        inter = (mv[y:base, x:x + w] & mn).sum()
        iou = inter / (mv.sum() + mn.sum() - inter)
        if iou > nota:
            melhor, nota = x, iou
    return melhor, base, nota


def converter(nome, pal, pasta=FOLHAS):
    figs = figuras(pasta / f"{nome}.png")
    velhos = antigos(nome)
    assert all(q is not None for q in figs), f"{nome}: figura faltando na folha"
    assert all(velhos), f"{nome}: sem os desenhos de antes em {ANTES}"
    figs = acertar_cor(figs, velhos)
    excecao = fh.fatores(nome)
    razoes = [lado(v) / max(q.size) / f for v, q, f in zip(velhos, figs, excecao)]
    fator = float(np.median(razoes)) * correcoes().get(nome, 1.0)
    notas = []
    for i, (q, v, f) in enumerate(zip(figs, velhos, excecao)):
        e = fator * f
        um = seco(q.resize((max(1, round(q.width * e)), max(1, round(q.height * e))), Image.LANCZOS))
        x, base, nota = encaixe(um, v)
        notas.append(nota)
        tres = seco(q.resize((um.width * E, um.height * E), Image.LANCZOS))
        for k, fig, pasta_saida in ((1, um, "quadros_arcade"), (E, tres, "quadros_arcade_hd")):
            tela = Image.new("RGBA", (fh.LARG * k, fh.ALT * k))
            tela.paste(pintar(fig, pal), (x * k, base * k - fig.height))
            destino = SPRITES / pasta_saida / nome
            destino.mkdir(parents=True, exist_ok=True)
            tela.save(destino / f"{i:02d}.png")
    desvio = [r / fator for r in razoes]
    aviso = "" if min(notas) > 0.6 else f"  POSE DIFERENTE no quadro {int(np.argmin(notas))} (cobre {min(notas):.0%})"
    print(f"{nome}: escala {fator:.4f} (figura {max(q.height for q in figs)} px); tamanho por quadro "
          f"{min(desvio):.2f} a {max(desvio):.2f}; silhueta cobre {np.mean(notas):.0%}{aviso}")
    return min(notas)


# ---------------------------------------------------------------- proporção
def correcoes():
    return json.loads(CABECA.read_text(encoding="utf-8")) if CABECA.exists() else {}


_BASE_CABECA = {}
# Folhas em que a régua da cabeça engana (cabeça de lado, curvada ou deitada): a correção pela cabeça deixava o boneco
# maior que o parado (vira mais alta; derrota e vítimas com 1.25 ficavam enormes). Escolhidas no olho, lado a lado com o
# parado na mesma escala (docs/hazak-36/proporcao.png).
CABECA_FIXA = {"vira": 1.0, "derrota_sirene": 1.1, "vitima_agarrado": 1.1, "vitima_arremessado": 1.1}


def medir_cabeca(nome):
    """Mediana da escala da cabeça dos 8 quadros 3x da folha contra a cabeça do parado (régua da #51), ou None."""
    sys.path.insert(0, str(Path(__file__).resolve().parent / "pixel"))
    import reguas

    def quadros(acao):
        return [np.array(Image.open(SPRITES / "quadros_arcade_hd" / acao / f"{i:02d}.png").convert("RGBA"))
                for i in range(8)]
    if "parado" not in _BASE_CABECA:
        par = quadros("parado")
        tmpl, _ = reguas.cabeca_do_parado(par[0])
        _BASE_CABECA["parado"] = (tmpl, np.median([c[0] for c in (reguas.escala_cabeca(q, tmpl) for q in par)
                                                   if c and c[1] >= 0.55] or [1.0]))
    tmpl, base = _BASE_CABECA["parado"]
    vals = [c[0] for c in (reguas.escala_cabeca(q, tmpl) for q in quadros(nome)) if c and c[1] >= 0.55]
    return float(np.median(vals) / base) if len(vals) >= 3 else None


def acertar_cabecas(nomes, pal, pasta):
    """Folha a folha: converte sem correção, mede a cabeça contra o parado e, se passar de LIMITE_CABECA, corrige a
    escala da folha (até 2 voltas). A escala pelos desenhos de antes herdava a proporção errada deles (#51: rasteira,
    agachado...). Grava sprites/hazaki/escala_cabeca.json, que o converter() usa sempre."""
    corr = correcoes()
    for nome in nomes:
        if nome == "parado":
            continue
        if nome in CABECA_FIXA:
            corr[nome] = CABECA_FIXA[nome]
            converter(nome, pal, pasta)
            print(f"  {nome}: correção fixa {corr[nome]:.3f}")
            continue
        corr[nome] = 1.0
        CABECA.write_text(json.dumps(corr, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        converter(nome, pal, pasta)
        for _ in range(2):
            r = medir_cabeca(nome)
            if r is None or abs(r - 1) <= LIMITE_CABECA:
                break
            corr[nome] = round(float(np.clip(corr[nome] / r, 0.8, 1.25)), 4)
            CABECA.write_text(json.dumps(corr, indent=1, sort_keys=True) + "\n", encoding="utf-8")
            converter(nome, pal, pasta)
        print(f"  {nome}: cabeça {medir_cabeca(nome) or 0:.2f} do parado, correção {corr[nome]:.3f}")
    corr = {k: v for k, v in corr.items() if v != 1.0}
    CABECA.write_text(json.dumps(corr, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def contato(destino, nomes):
    """Antes (git ANTES, 3x do hd_guiado) em cima e depois embaixo, os 8 quadros, recorte da figura."""
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    x0, x1, y0, y1 = 80 * E, 280 * E, 70 * E, 232 * E
    for nome in nomes:
        tela = Image.new("RGB", ((x1 - x0) * 8, (y1 - y0) * 2), (120, 124, 120))
        for i in range(8):
            b = subprocess.run(["git", "show", f"{ANTES}:sprites/hazaki/quadros_arcade_hd/{nome}/{i:02d}.png"],
                               cwd=RAIZ, capture_output=True).stdout
            pares = [Image.open(io.BytesIO(b)).convert("RGBA") if b else None,
                     Image.open(SPRITES / "quadros_arcade_hd" / nome / f"{i:02d}.png").convert("RGBA")]
            for linha, q in enumerate(pares):
                if q is not None:
                    c = q.crop((x0, y0, x1, y1))
                    tela.paste(c, ((x1 - x0) * i, (y1 - y0) * linha), c)
        tela.save(destino / f"{nome}.png")


def main():
    args = sys.argv[1:]
    pasta = FOLHAS
    if "--de" in args:
        k = args.index("--de")
        pasta = Path(args[k + 1])
        del args[k:k + 2]
    if "--paleta" in args:
        fazer_paleta(pasta)
        return
    todas = sorted(p.stem for p in pasta.glob("*.png")
                   if not p.stem.startswith(("patroa_", "obj_")) and p.stem not in NAO_CORPO)
    if "--contato" in args:
        k = args.index("--contato")
        contato(args[k + 1], [a for a in args[:k] + args[k + 2:] if not a.startswith("--")] or todas)
        return
    if not PALETA.exists():
        fazer_paleta(pasta)
    pal = paleta()
    nomes = [a for a in args if not a.startswith("--")] or todas
    if "--cabeca" in args:
        acertar_cabecas(nomes, pal, pasta)
        return
    for nome in nomes:
        converter(nome, pal, pasta)


if __name__ == "__main__":
    main()
