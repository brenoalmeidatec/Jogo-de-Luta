#!/usr/bin/env python3
"""Mede a fluidez da aura no filme de ferramentas/filmar_aura.py e monta as tiras para olhar.

  python ferramentas/medir_aura.py PASTA_DO_FILME [--saida PASTA] [--inicio 160]

Lê PASTA_DO_FILME/luta.mp4 (60 fps, um tick por quadro) e aura_log.txt (o que o motor fez a cada tick). Grava em
--saida (padrão PASTA_DO_FILME/medida): todos os quadros de 2 s (quadros/NNNN.png, a partir do tick --inicio),
tiras tick a tick (liga, loop, surto, vira, desliga) e medidas.txt. Sai com código 1 se algum aceite falhar.

Aceite (docs/arcade/aura_animada.md):
  - nenhuma camada segura o mesmo quadro por mais de 3 ticks;
  - no loop, a mudança entre quadros vizinhos do vídeo não salta: percentil 95 / mediana <= 2.5, maior / mediana
    <= 3.5 (o gravador da sandbox pula ticks: um pulo sem repetido ao lado dobra o passo), e nenhum quadro parado;
  - a volta do loop (último quadro -> primeiro) não muda mais que 2.5x a mediana;
  - a escala de cada camada anda no máximo 3% por tick (6% no surto, 5% ligando e desligando): sem tranco;
  - as camadas não andam juntas: correlação da escala entre camadas < 0.9 em módulo e elementos diferentes;
  - zero pixel verde de fundo (#00FF00) a mais do que antes de a aura ligar;
  - o corpo fica na frente da aura de trás; a aura tem pelo menos 2x a altura do lutador;
  - a aura some inteira depois de desligar (nenhum Explod sobra).
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from filmar_aura import LIGA, SURTO1, VIRA, SURTO2, DESLIGA  # noqa: E402

PX = 4  # px do vídeo (1280x720) por px do jogo (320x180)
CHAO_Y = 640  # linha dos pés no vídeo (stage0-720)
ALTURA_LUTADOR = 111


def ler_log(caminho):
    """{tick: {jogador: {"f":, "x":, "st":, "ne":, camadas: {id: {sx, sy, px, py, el, an, fa} ou None}}}}"""
    ticks = {}
    for linha in caminho.read_text(encoding="utf-8", errors="replace").splitlines():
        partes = [p.strip() for p in linha.split("|")]
        if not partes[0].isdigit():
            continue
        t, atual = int(partes[0]), None
        ticks[t] = {}
        for p in partes[1:]:
            m = re.match(r"P(\d) f=(-?\d+) x=(-?[\d.]+) st=(\d+) ne=(\d+)", p)
            if m:
                atual = ticks[t][int(m[1])] = {"f": int(m[2]), "x": float(m[3]), "st": int(m[4]), "ne": int(m[5]),
                                               "camadas": {}}
                continue
            e = int(p.split()[0])
            atual["camadas"][e] = None if "fora" in p else {k: float(v) for k, v in re.findall(r"(\w\w)=(-?[\d.]+)", p)}
    return ticks


def serie(ticks, jogador, camada, chave, a, b):
    return np.array([ticks[t][jogador]["camadas"][camada][chave] for t in range(a, b)
                     if t in ticks and ticks[t][jogador]["camadas"].get(camada)])


def maior_espera(valores):
    """Maior número de ticks seguidos com o mesmo valor."""
    maior = atual = 1
    for x, y in zip(valores, valores[1:]):
        atual = atual + 1 if x == y else 1
        maior = max(maior, atual)
    return maior


def quadro(pasta, n):
    return np.asarray(Image.open(pasta / f"{n:04d}.png").convert("RGB")).astype(np.int16)


def tira(pasta, saida, nome, inicio, n, caixa, passo=1, colunas=15, largura=180):
    imgs = [Image.open(pasta / f"{t:04d}.png").convert("RGB").crop(caixa) for t in range(inicio, inicio + n * passo, passo)]
    w, h = imgs[0].size
    alt = round(h * largura / w)
    linhas = -(-len(imgs) // colunas)
    folha = Image.new("RGB", (largura * colunas, alt * linhas), (0, 0, 0))
    for i, im in enumerate(imgs):
        folha.paste(im.resize((largura, alt), Image.BILINEAR), ((i % colunas) * largura, (i // colunas) * alt))
    folha.save(saida / f"tira_{nome}.png")
    return saida / f"tira_{nome}.png"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("filme", type=Path)
    ap.add_argument("--saida", type=Path)
    ap.add_argument("--inicio", type=int, default=160, help="primeiro tick dos 2 s guardados quadro a quadro")
    a = ap.parse_args()
    saida = (a.saida or a.filme / "medida").resolve()
    saida.mkdir(parents=True, exist_ok=True)
    todos = saida / "todos"
    shutil.rmtree(todos, ignore_errors=True)
    todos.mkdir()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(a.filme / "luta.mp4"), "-start_number", "0",
                    str(todos / "%04d.png")], check=True)
    total = len(list(todos.glob("*.png")))
    ticks = ler_log(a.filme / "aura_log.txt")
    r, falhas = [], []

    def nota(texto, ok=None):
        r.append(("" if ok is None else ("OK    " if ok else "FALHA ")) + texto)
        if ok is not None and not ok:
            falhas.append(texto)

    # ---- o vídeo começa alguns ticks depois do round: acha o atraso pelo instante em que a aura aparece
    base = quadro(todos, 0)
    regioes = {1: (20, 90, 400, 640), 2: (760, 90, 1120, 640)}  # antes da virada: P1 à esquerda, P2 à direita
    ceus = {1: (20, 95, 420, 185), 2: (580, 95, 1100, 185)}  # acima das cabeças: só a aura mexe (o corpo ginga embaixo)

    def rec(img, cx):
        x0, y0, x1, y1 = cx
        return img[y0:y1, x0:x1]

    ceu = ceus[2]
    liga_video = next(n for n in range(1, total) if np.abs(rec(quadro(todos, n), ceu) - rec(base, ceu)).mean() > 1.0)
    liga_log = min(t for t in ticks if ticks[t][2]["ne"] > 0)
    atraso = liga_log - liga_video  # tick do log = quadro do vídeo + atraso
    nota(f"vídeo: {total} quadros; a aura aparece no quadro {liga_video} = tick {liga_log} do log (atraso {atraso})")

    def v(t):  # tick do log -> quadro do vídeo
        return t - atraso

    # ---- 2 s quadro a quadro
    pasta_q = saida / "quadros"
    shutil.rmtree(pasta_q, ignore_errors=True)
    pasta_q.mkdir()
    for k in range(120):
        shutil.copy2(todos / f"{v(a.inicio) + k:04d}.png", pasta_q / f"{a.inicio + k:04d}.png")
    nota(f"2 s quadro a quadro: {pasta_q} (ticks {a.inicio} a {a.inicio + 119})")

    # ---- log: o que o motor fez
    camadas = {j: sorted(ticks[liga_log + 30][j]["camadas"]) for j in (1, 2)}
    loop = (LIGA + 60, SURTO1 - 2)
    for j in (1, 2):
        for c in camadas[j]:
            el = serie(ticks, j, c, "el", *loop)
            espera = maior_espera(list(el))
            nota(f"P{j} camada {c}: {len(set(el))} quadros no loop, o mesmo quadro fica no máximo {espera} ticks", espera <= 3)
            for nome, (ta, tb), teto in (("loop", loop, 0.03), ("surto", (SURTO1, SURTO1 + 70), 0.06),
                                         ("liga", (LIGA + 1, LIGA + 40), 0.05), ("desliga", (DESLIGA, DESLIGA + 34), 0.05)):
                d = max((np.abs(np.diff(np.abs(serie(ticks, j, c, k, ta, tb)))) /
                         np.abs(serie(ticks, j, c, k, *loop)).mean()).max() for k in ("sx", "sy"))
                nota(f"P{j} camada {c}: escala anda no máximo {d * 100:.2f}% por tick no trecho {nome}", d <= teto)
        sx = {c: np.abs(serie(ticks, j, c, "sx", *loop)) for c in camadas[j]}
        for i, c1 in enumerate(camadas[j]):
            for c2 in camadas[j][i + 1:]:
                co = float(np.corrcoef(sx[c1], sx[c2])[0, 1])
                nota(f"P{j} camadas {c1} x {c2}: correlação da escala {co:+.2f}", abs(co) < 0.9)
        juntos = np.mean([len({ticks[t][j]["camadas"][c]["el"] for c in camadas[j]}) for t in range(*loop)])
        nota(f"P{j}: em média {juntos:.1f} elementos diferentes ao mesmo tempo em {len(camadas[j])} camadas",
             juntos >= len(camadas[j]) - 1)
        pico = max(np.abs(serie(ticks, j, camadas[j][1], "sx", SURTO1, SURTO1 + 70)))
        calmo = np.abs(serie(ticks, j, camadas[j][1], "sx", *loop)).max()
        nota(f"P{j} surto: a escala da camada {camadas[j][1]} vai de {calmo:.3f} (máximo calmo) a {pico:.3f}", pico > calmo * 1.08)
        el_surto = serie(ticks, j, camadas[j][1], "el", SURTO1 + 12, SURTO1 + 30)
        passo = np.mean(np.diff(el_surto) % len(set(serie(ticks, j, camadas[j][1], "el", *loop))))
        nota(f"P{j} surto: a animação anda {passo:.2f} quadro por tick (calma: 0.5)", passo > 0.8)
        antes, depois = ticks[VIRA - 5][j], ticks[VIRA + 20][j]
        fa = [depois["camadas"][c]["fa"] for c in camadas[j]]
        nota(f"P{j} virada: lutador de {antes['f']:+d} para {depois['f']:+d}, camadas agora {fa}",
             depois["f"] == -antes["f"] and all(x == depois["f"] for x in fa))
        some = min(t for t in ticks if t > DESLIGA and all(ticks[t][j]["camadas"][c] is None for c in camadas[j]))
        ultimo = max(ticks)
        nota(f"P{j} desliga: camadas somem {some - DESLIGA} ticks depois; explods no fim do filme (tick {ultimo}): "
             f"{ticks[ultimo][j]['ne']}", ticks[ultimo][j]["ne"] == 0)

    # ---- vídeo: mudança entre quadros vizinhos, medida acima das cabeças (embaixo o corpo de teste ginga)
    ceus[0] = (20, 95, 1260, 185)  # a faixa inteira: depois da virada as duas auras se cruzam
    viz = {j: np.zeros(total - 1) for j in (0, 1, 2)}
    anterior = quadro(todos, 0)
    for n in range(1, total):
        atual = quadro(todos, n)
        for j in (0, 1, 2):
            viz[j][n - 1] = np.abs(rec(atual, ceus[j]) - rec(anterior, ceus[j])).mean()
        anterior = atual
    med = {j: float(np.median(viz[j][v(loop[0]):v(loop[1])])) for j in (1, 2)}
    # quadro repetido pela CAPTURA (gdigrab na sandbox): as duas auras param no mesmo quadro do vídeo, enquanto o
    # log do motor mostra todas as camadas andando. O repetido e o anterior (que leva o passo dobrado) saem da conta.
    repetidos = {n for n in range(v(LIGA + 30), v(DESLIGA)) if all(viz[j][n] < 0.2 * med[j] for j in (1, 2))}
    fora = repetidos | {n - 1 for n in repetidos}
    nota(f"captura: {len(repetidos)} quadros repetidos pelo gravador entre os ticks {LIGA + 30} e {DESLIGA} "
         f"(fora da conta, com o quadro anterior)")

    def trecho(j, ta, tb):
        return np.array([viz[j][v(t)] for t in range(ta, tb) if v(t) not in fora])

    for j in (1, 2):
        d = trecho(j, *loop)
        m = float(np.median(d))
        parados = int((d < 0.2 * m).sum())
        nota(f"P{j} vídeo, loop (ticks {loop[0]} a {loop[1]}): mudança por quadro mediana {m:.2f}, menor {d.min():.2f}, "
             f"maior {d.max():.2f}; percentil 95/mediana {np.percentile(d, 95) / m:.2f}, maior/mediana {d.max() / m:.2f}; "
             f"quadros parados {parados}", np.percentile(d, 95) / m <= 2.5 and d.max() / m <= 3.5 and parados == 0)
        # emenda: ticks em que a camada principal volta do último elemento para o primeiro
        el = {t: ticks[t][j]["camadas"][camadas[j][1]]["el"] for t in range(loop[0], loop[1] + 1)}
        voltas = [t for t in range(loop[0], loop[1]) if el[t + 1] < el[t] and v(t) not in fora]
        if voltas:
            na_volta = max(viz[j][v(t)] for t in voltas)
            nota(f"P{j} vídeo, volta do loop nos ticks {voltas}: mudança {na_volta:.2f} = {na_volta / m:.2f}x a mediana",
                 na_volta / m <= 2.5)
        ds = trecho(j, SURTO1 - 2, SURTO1 + 70)
        nota(f"P{j} vídeo, surto: mudança por quadro mediana {np.median(ds):.2f}, maior {ds.max():.2f} "
             f"({ds.max() / np.median(ds):.2f}x a mediana do surto)", ds.max() / np.median(ds) <= 3.0)
        dl = trecho(j, LIGA, LIGA + 40)
        nota(f"P{j} vídeo, ligando: maior mudança por quadro {dl.max():.2f} ({dl.max() / m:.2f}x a mediana do loop)",
             dl.max() / m <= 3.0)
    antes_d, dd = trecho(0, DESLIGA - 60, DESLIGA), trecho(0, DESLIGA, min(DESLIGA + 115, total + atraso - 2))
    nota(f"vídeo, desligando (as duas auras, faixa inteira): maior mudança por quadro {dd.max():.2f} = "
         f"{dd.max() / np.median(antes_d):.2f}x a mediana dos 60 ticks de antes; último tick com mudança: "
         f"{DESLIGA + int(np.nonzero(dd > 0.3)[0].max()) if (dd > 0.3).any() else DESLIGA} (partículas ainda sobem)",
         dd.max() / np.median(antes_d) <= 3.0)

    # ---- franja verde, corpo na frente, tamanho (mesma fase da ginga: 48 ticks)
    def verde(img):
        return (img[..., 1] > 200) & (img[..., 0] < 90) & (img[..., 2] < 90)

    n_sem = max(0, v(LIGA) - 30)
    sem = quadro(todos, n_sem)
    for j in (1, 2):
        x0, y0, x1, y1 = regioes[j]
        antes = int(verde(sem[y0:y1, x0:x1]).sum())
        pior = max(int(verde(quadro(todos, v(t))[y0:y1, x0:x1]).sum()) for t in range(loop[0], loop[1], 3))
        nota(f"P{j} pixels de verde de fundo na região da aura: {antes} antes de ligar, {pior} no pior quadro do loop",
             pior <= antes)
        com = quadro(todos, n_sem + 144)  # 3 voltas da ginga depois: mesmo desenho do corpo
        r_, g_, b_ = (sem[..., i] for i in range(3))
        pele = (r_ > 150) & (g_ > 70) & (g_ < 170) & (b_ < 110) & (r_ - b_ > 70)  # tom da pele do corpo de teste
        pele[:y0] = False
        pele[:, :x0] = False
        pele[:, x1:] = False
        # a captura pode escorregar 1 ou 2 quadros em 144 ticks: fica o quadro em que o corpo mais bate
        igual, n_com = max(((np.abs(quadro(todos, n_sem + dn) - sem).max(axis=2) <= 24)[pele].mean(), n_sem + dn)
                           for dn in range(141, 148))
        com = quadro(todos, n_com)
        nota(f"P{j} corpo na frente: {igual * 100:.1f}% dos pixels de pele iguais com a aura ligada "
             f"(o resto é a camada da frente e as partículas)", igual >= 0.8)
        mudou = np.abs(com - sem).max(axis=2) > 40
        mudou[:, :x0 - 20] = False
        mudou[:, x1 + 20:] = False
        ys = np.nonzero(mudou.any(axis=1))[0]
        visivel = (CHAO_Y - ys.min()) / PX
        nota(f"P{j} tamanho: a aura muda a tela dos pés até {visivel:.0f} px do jogo acima do chão "
             f"(topo da tela = {CHAO_Y / PX:.0f}); lutador = {ALTURA_LUTADOR} px", visivel >= 1.4 * ALTURA_LUTADOR)

    # ---- tiras para olhar
    cx1, cx2 = (0, 60, 560, 690), (560, 60, 1180, 690)
    for nome, t0, n, passo, caixa in (("p1_liga", LIGA - 2, 30, 1, cx1), ("p2_liga", LIGA - 2, 30, 1, cx2),
                                      ("p1_loop", loop[0], 60, 1, cx1), ("p2_loop", loop[0], 60, 1, cx2),
                                      ("p1_surto", SURTO1 - 2, 45, 1, cx1), ("p2_surto", SURTO1 - 2, 45, 1, cx2),
                                      ("vira", VIRA - 3, 30, 1, (300, 60, 1280, 690)),
                                      ("desliga", DESLIGA - 2, 45, 1, (500, 60, 1280, 690)),
                                      ("resumo", LIGA - 10, 30, 18, (0, 0, 1280, 720))):
        tira(todos, saida, nome, v(t0), n, caixa, passo)
    nota(f"tiras: {saida}/tira_*.png")
    shutil.rmtree(todos, ignore_errors=True)
    (saida / "medidas.txt").write_text("\n".join(r) + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("\n".join(r))
    print(f"\n{len(falhas)} falha(s)")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
