#!/usr/bin/env python3
"""Mede no quadro final as regras do estilo arcade (tabela de regras 1-12 da arte arcade) e imprime PASS/FAIL por regra e
por quadro. Mede o que dá por número; 8, 9 e 12 continuam no olho.

  python ferramentas/conferir_arte.py soco                    quadros_arcade/soco/ (desenhos e meio/)
  python ferramentas/conferir_arte.py soco --pasta quadros    outra pasta de sprites/<lutador>/ (ex.: a arte atual)
  opções: --relatorio ARQ.md (grava também em arquivo), --forte (regra 11 vale como golpe forte)

Regras medidas:
  1  cores únicas <= 15 e todas da paleta_arcade.json
  3  rampa da pele: sombra 5-15°, médio 21-26°, luz 30-40° (cores da paleta) e as três aparecem no quadro
  4  sombra da calça fria: matiz 220-270°, saturação >= 10%, e aparece no quadro
  5  borda externa: só cores de contorno, nenhum canal < 20; espessura 1 px (pixel logo atrás da borda que também é
     contorno em menos de 35% da borda)
  7  pixel isolado (diferente dos 4 vizinhos) < 2% da figura, fora da borda externa (o degrau do contorno de 1 px
     na diagonal não é chiado)
  10 punho no contato 10-20% maior que no quadro de guarda (altura da ponta do braço da frente; folha toda)
  11 antecipação no quadro 2 (silhueta muda > 5% do quadro 1) e recuperação >= 3 desenhos depois do ativo (folha toda)
"""
import colorsys
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quantizar_folha import PALETA, SPRITES, soltos, vizinhos4  # noqa: E402

RAMPA = {"pele_sombra": (5, 15), "pele_medio": (21, 26), "pele_luz": (30, 40)}
SOMBRA_CALCA = "calca_sombra"
LIMITE_SOLTO = 0.02
LIMITE_DOBRADO = 0.35
PUNHO = (0.10, 0.20)
GUARDA = 1  # quadro de guarda com o punho fechado (o 0 é a mão aberta da ginga)


def h_s(rgb):
    h, s, _ = colorsys.rgb_to_hsv(*(np.asarray(rgb) / 255))
    return h * 360, s


def indices(img, pal):
    """Imagem -> índice na paleta (-1 transparente, -2 cor fora da paleta)."""
    a = np.asarray(img.convert("RGBA"))
    opaco = a[..., 3] >= 128
    chave = a[..., 0].astype(int) << 16 | a[..., 1].astype(int) << 8 | a[..., 2].astype(int)
    tabela = {int(r) << 16 | int(g) << 8 | int(b): i for i, (r, g, b) in enumerate(pal)}
    idx = np.vectorize(lambda k: tabela.get(k, -2))(chave)
    return np.where(opaco, idx, -1), chave, opaco


def regras_do_quadro(img, dados, pal):
    ids = [c["id"] for c in dados["cores"]]
    idx, chave, opaco = indices(img, pal)
    r = {}
    unicas = len(np.unique(chave[opaco]))
    fora = int((idx == -2).sum())
    r[1] = (unicas <= 15 and fora == 0, f"{unicas} cores, {fora} px fora da paleta")
    usadas = set(np.unique(idx[idx >= 0]).tolist())
    falhas = []
    for papel, (h0, h1) in RAMPA.items():
        h, _ = h_s(pal[ids.index(papel)])
        if not h0 <= h <= h1:
            falhas.append(f"{papel} {h:.0f}°")
        if ids.index(papel) not in usadas:
            falhas.append(f"{papel} ausente")
    r[3] = (not falhas, "; ".join(falhas) or "sombra/médio/luz nas faixas e presentes")
    h, s = h_s(pal[ids.index(SOMBRA_CALCA)])
    presente = ids.index(SOMBRA_CALCA) in usadas
    r[4] = (220 <= h <= 270 and s >= 0.10 and presente, f"{h:.0f}° s={s:.0%}" + ("" if presente else " ausente"))
    viz = vizinhos4(idx)
    borda = opaco & (viz == -1).any(0)
    contornos = {ids.index(c) for c in dados["contorno_grupo"].values()}
    escuro = int((np.asarray(img.convert("RGB"))[borda] < 20).any(1).sum())
    nao_contorno = int((borda & ~np.isin(idx, list(contornos))).sum())
    # espessura: pixel da borda cujo vizinho de dentro (opaco e fora da borda) também é contorno
    dentro = opaco & ~borda
    p = np.pad(dentro, 1)
    pi = np.pad(np.where(np.isin(idx, list(contornos)), 1, 0), 1)
    dobrado = np.zeros_like(borda)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d = p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx]
        c = pi[1 + dy:pi.shape[0] - 1 + dy, 1 + dx:pi.shape[1] - 1 + dx]
        dobrado |= borda & (d == 1) & (c == 1)
    frac = dobrado.sum() / max(1, borda.sum())
    r[5] = (escuro == 0 and nao_contorno == 0 and frac < LIMITE_DOBRADO,
            f"{escuro} px escuros, {nao_contorno} px de borda sem contorno, {frac:.0%} dobrado")
    solto = soltos(np.where(idx == -2, -3, idx))  # cor fora da paleta conta como cor própria
    fs = solto.sum() / max(1, opaco.sum())
    r[7] = (fs < LIMITE_SOLTO, f"{fs:.2%} isolados ({int(solto.sum())} px)")
    return r


def ponta(img):
    """(x da ponta do braço da frente, altura do punho) na metade de cima da figura."""
    a = np.asarray(img.convert("RGBA"))[..., 3] >= 128
    ys = np.nonzero(a.any(1))[0]
    topo, base = ys.min(), ys.max()
    banda = a[topo:topo + (base - topo) // 2]
    xs = np.nonzero(banda.any(0))[0]
    xmax = xs.max()
    fatia = banda[:, xmax - 7:xmax + 1].any(1)
    linhas = np.nonzero(fatia)[0]
    # só o trecho contínuo que contém a ponta
    y0 = np.nonzero(banda[:, xmax])[0][0]
    ini = fim = y0
    while ini - 1 >= 0 and fatia[ini - 1]:
        ini -= 1
    while fim + 1 < len(fatia) and fatia[fim + 1]:
        fim += 1
    return int(xmax), int(fim - ini + 1) if len(linhas) else 0


def silhueta(img):
    return np.asarray(img.convert("RGBA"))[..., 3] >= 128


def regras_da_folha(desenhos, forte):
    r = {}
    pontas = [ponta(d) for d in desenhos]
    alcance = [p[0] for p in pontas]
    maximo = max(alcance)
    ativos = [i for i, x in enumerate(alcance) if x >= maximo - 2]
    contato = ativos[0]
    ganho = pontas[contato][1] / max(1, pontas[GUARDA][1]) - 1
    r[10] = (PUNHO[0] <= ganho <= PUNHO[1],
             f"punho {pontas[GUARDA][1]} px no quadro {GUARDA} -> {pontas[contato][1]} px no contato (quadro {contato}): "
             f"{ganho:+.0%}")
    a, b = silhueta(desenhos[0]), silhueta(desenhos[1])
    muda = 1 - (a & b).sum() / max(1, (a | b).sum())
    volta = len(desenhos) - 1 - ativos[-1]
    ok = muda > 0.05 and volta >= 3
    r[11] = (ok if forte else ok or volta >= 2,
             f"quadro 2 muda {muda:.0%} da silhueta; ativo nos quadros {ativos}, {volta} desenhos de volta"
             + ("" if forte else " (golpe fraco: volta >= 2 basta; >= 3 é a regra do forte)"))
    return r


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)

    def opcao(nome, padrao):
        if nome in args:
            i = args.index(nome)
            v = args[i + 1]
            del args[i:i + 2]
            return v
        return padrao

    pasta = opcao("--pasta", "quadros_arcade")
    relatorio = opcao("--relatorio", "")
    forte = "--forte" in args
    nome = [a for a in args if not a.startswith("--")][0]
    dados = json.loads(PALETA.read_text(encoding="utf-8"))
    pal = np.array([c["rgb"] for c in dados["cores"]], int)
    base = SPRITES / pasta / nome
    arquivos = sorted(base.glob("[0-9][0-9].png")) + sorted((base / "meio").glob("*.png"))
    linhas = [f"# conferir_arte: {nome} ({base})", "", "| quadro | " + " | ".join(f"R{n}" for n in (1, 3, 4, 5, 7)) + " |",
              "|---|" + "---|" * 5]
    total = {n: [0, 0] for n in (1, 3, 4, 5, 7)}
    falhas = []
    for f in arquivos:
        r = regras_do_quadro(Image.open(f), dados, pal)
        rot = f.relative_to(base).as_posix()
        linhas.append(f"| {rot} | " + " | ".join("PASS" if r[n][0] else "FAIL" for n in total) + " |")
        for n, (ok, txt) in r.items():
            total[n][0 if ok else 1] += 1
            if not ok:
                falhas.append(f"- {rot} R{n}: {txt}")
            elif f.stem in ("00", "04"):
                falhas.append(f"- {rot} R{n} (amostra, PASS): {txt}")
    desenhos = [Image.open(f) for f in sorted(base.glob("[0-9][0-9].png"))]
    folha = regras_da_folha(desenhos, forte) if len(desenhos) == 8 else {}
    linhas += ["", "## Por regra", ""]
    linhas += [f"- R{n}: {'PASS' if t[1] == 0 else 'FAIL'} ({t[0]} passam, {t[1]} falham de {sum(t)} quadros)"
               for n, t in total.items()]
    linhas += [f"- R{n}: {'PASS' if ok else 'FAIL'} ({txt})" for n, (ok, txt) in folha.items()]
    linhas += ["", "## Detalhes", ""] + falhas
    texto = "\n".join(linhas) + "\n"
    print(texto)
    if relatorio:
        Path(relatorio).write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    main()
