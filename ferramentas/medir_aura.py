#!/usr/bin/env python3
"""Mede a fluidez da aura no filme de ferramentas/filmar_aura.py e monta as tiras para olhar.

  python ferramentas/medir_aura.py PASTA_DO_FILME [--saida PASTA] [--inicio 160]     (roteiro padrao)
  python ferramentas/medir_aura.py PASTA_DO_FILME --extra                             (roteiro extra: só o log)

Lê PASTA_DO_FILME/luta.mp4 (60 fps, um tick por quadro) e aura_log.txt (o que o motor fez a cada tick). Grava em
--saida (padrão PASTA_DO_FILME/medida): todos os quadros de 2 s (quadros/NNNN.png, a partir do tick --inicio),
tiras tick a tick (liga, loop, surto, vira, desliga) e medidas.txt. Sai com código 1 se algum aceite falhar.

Aceite do roteiro padrao (docs/arcade/aura_animada.md):
  - nenhuma camada segura o mesmo quadro por mais de 3 ticks;
  - o motor não escala nem gira a aura em regime: escala 1 e ângulo 0 em todo o loop (a grade do pixel fica inteira);
  - a camada anda todo tick (posição) e sem tranco: no máximo 1 px por tick no loop (tremor incluído);
  - a escala só sai de 1 ligando, desligando e no surto, e anda no máximo 7% por tick;
  - no loop, a mudança entre quadros vizinhos do vídeo não salta: percentil 95 / mediana <= 2.5, maior / mediana
    <= 3.5 (o gravador da sandbox pula ticks: um pulo sem repetido ao lado dobra o passo), e nenhum quadro parado;
  - a volta do loop (último quadro -> primeiro) não muda mais que 2.5x a mediana;
  - as camadas não andam juntas: correlação da posição entre camadas < 0.9 em módulo e elementos diferentes;
  - zero pixel verde de fundo (#00FF00) a mais do que antes de a aura ligar;
  - o corpo fica legível, medido por faixa contra o mesmo desenho sem aura: tronco >= 97%, pernas >= 95% e pés
    >= 60% dos pixels do corpo iguais, no loop E no surto;
  - o HUD fica na frente da aura: nas caixas da vida, do retrato e do poder, no máximo 0,5% dos pixels muda;
  - a aura tem pelo menos 2x a altura do lutador; no pior tick, no máximo 30 Explods por lutador;
  - a virada não é um corte: as camadas apagam, trocam de lado alguns ticks depois do lutador e voltam;
  - a aura some inteira depois de desligar (nenhum Explod sobra).
Aceite do roteiro extra: a aura não para em superpausa nem com o lutador em estado custom; a camada de chão fica no
chão no pulo; o vencedor segue com a aura até a pose de vitória e o derrotado perde; antes da intro do round
seguinte não sobra Explod; na intro a aura volta.
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
from filmar_aura import (LIGA, SURTO1, VIRA, SURTO2, DESLIGA, SOCO_SEM_AURA,  # noqa: E402
                         X_LIGA, X_SUPER, X_GOLPE, X_PULO, X_KO, X_DESLIGA2)

PX = 4  # px do vídeo (1280x720) por px do jogo (320x180)
CHAO_Y = 640  # linha dos pés no vídeo (stage0-720)
ALTURA_LUTADOR = 111
TETO_EXPLODS = 30
# Caixas do HUD do jogo (motif/nazafight, tela de 1280x720) que a aura alcança: miolo das barras de vida, retratos, nomes
# e barras de poder. O relógio fica fora porque os dígitos mudam sozinhos.
HUD = {"vida P1": (170, 40, 540, 62), "vida P2": (735, 40, 1110, 62), "retrato P1": (20, 20, 108, 108),
       "retrato P2": (1172, 20, 1260, 108), "nome P1": (150, 86, 420, 118), "nome P2": (860, 86, 1130, 118),
       "poder P1": (30, 680, 440, 708), "poder P2": (840, 680, 1250, 708)}


def ler_log(caminho):
    """{tick: {"meta": {t, rs, rn}, jogador: {"f", "x", "y", "st", "ne", camadas: {id: {sx, sy, px, py, el, an, fa}
    ou None}}}}. No roteiro padrao a chave é o tick do round; no extra, o tick global."""
    ticks = {}
    for linha in caminho.read_text(encoding="utf-8", errors="replace").splitlines():
        partes = [p.strip() for p in linha.split("|")]
        if not partes[0].isdigit():
            continue
        t, atual = int(partes[0]), None
        ticks[t] = {"meta": {}}
        for p in partes[1:]:
            if p.startswith("t="):
                ticks[t]["meta"] = {k: int(v) for k, v in re.findall(r"(\w+)=(-?\d+)", p)}
                continue
            m = re.match(r"P(\d) f=(-?\d+) x=(-?[\d.]+) st=(\d+) ne=(\d+)(?: y=(-?[\d.]+))?(?: h=(-?[\d.]+))?", p)
            if m:
                atual = ticks[t][int(m[1])] = {"f": int(m[2]), "x": float(m[3]), "st": int(m[4]), "ne": int(m[5]),
                                               "y": float(m[6] or 0), "h": float(m[7] or 0), "camadas": {}}
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
    imgs = [Image.open(pasta / f"{t:04d}.png").convert("RGB").crop(caixa) for t in range(inicio, inicio + n * passo, passo)
            if (pasta / f"{t:04d}.png").exists()]
    w, h = imgs[0].size
    alt = round(h * largura / w)
    linhas = -(-len(imgs) // colunas)
    folha = Image.new("RGB", (largura * colunas, alt * linhas), (0, 0, 0))
    for i, im in enumerate(imgs):
        folha.paste(im.resize((largura, alt), Image.BILINEAR), ((i % colunas) * largura, (i // colunas) * alt))
    folha.save(saida / f"tira_{nome}.png")
    return saida / f"tira_{nome}.png"


class Notas:
    def __init__(self):
        self.linhas, self.falhas = [], []

    def __call__(self, texto, ok=None):
        self.linhas.append(("" if ok is None else ("OK    " if ok else "FALHA ")) + texto)
        if ok is not None and not ok:
            self.falhas.append(texto)

    def fechar(self, destino):
        destino.write_text("\n".join(self.linhas) + "\n", encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print("\n".join(self.linhas))
        print(f"\n{len(self.falhas)} falha(s)")
        sys.exit(1 if self.falhas else 0)


# ------------------------------------------------------------------ roteiro extra (só o log)

def andou(ticks, gs, j, c):
    """Fração dos ticks de `gs` em que a posição da camada mudou, e quantas vezes o elemento da animação andou."""
    v = [ticks[g][j]["camadas"].get(c) for g in gs]
    v = [x for x in v if x]
    if len(v) < 3:
        return 0.0, 0
    pos = sum((a["px"], a["py"]) != (b["px"], b["py"]) for a, b in zip(v, v[1:])) / (len(v) - 1)
    el = sum(a["el"] != b["el"] for a, b in zip(v, v[1:]))
    return pos, el


def medir_extra(filme, saida):
    nota = Notas()
    ticks = ler_log(filme / "aura_log.txt")
    gs = sorted(ticks)
    meta = {g: ticks[g]["meta"] for g in gs}
    camadas = {j: sorted(ticks[next(g for g in gs if ticks[g][j]["ne"] >= 4)][j]["camadas"]) for j in (1, 2)}
    nota(f"log: {len(gs)} ticks; rounds {sorted({m['rn'] for m in meta.values()})}; "
         f"RoundState visto: {sorted({m['rs'] for m in meta.values()})}")

    def trecho(cond):
        return [g for g in gs if cond(g)]

    # as camadas com deriva (todas menos o anel de chão, que só anima) têm de mudar de posição todo tick
    def confere(nome, alvo, j):
        if len(alvo) < 10:
            nota(f"{nome}: só {len(alvo)} ticks no log, não deu para medir", False)
            return
        for c in camadas[j]:
            pos, el = andou(ticks, alvo, j, c)
            parada = c == camadas[2][0] and j == 2  # anel de chão: sem deriva
            nota(f"{nome}, P{j} camada {c}: posição mudou em {pos * 100:.0f}% dos {len(alvo)} ticks, a animação "
                 f"andou {el} quadros" + (" (anel de chão: só anima)" if parada else ""),
                 el >= len(alvo) // 3 and (parada or pos >= 0.9))
        ne = [ticks[g][j]["ne"] for g in alvo]
        nota(f"{nome}, P{j}: explods vivos de {min(ne)} a {max(ne)}; a contagem mudou {sum(a != b for a, b in zip(ne, ne[1:]))} "
             f"vezes (partículas nascem e somem)", sum(a != b for a, b in zip(ne, ne[1:])) >= 3)

    pausa = trecho(lambda g: meta[g]["rn"] == 1 and meta[g]["rs"] == 2 and ticks[g][1]["st"] == 1100)
    pausa = pausa[6:38]  # a SuperPause entra no Time = 2 e dura 40 ticks
    nota(f"superpausa do P1 (estado 1100): ticks {pausa[0] if pausa else '-'} a {pausa[-1] if pausa else '-'} do log")
    confere("superpausa (P2 parado pelo motor)", pausa, 2)
    confere("superpausa (P1, dono da pausa, também parado: movetime 0)", pausa, 1)
    custom = trecho(lambda g: meta[g]["rn"] == 1 and ticks[g][2]["st"] == 1310)
    nota(f"estado custom: P2 ficou {len(custom)} ticks no estado 1310 (do P1)", len(custom) >= 40)
    confere("estado custom", custom[2:], 2)

    pulo = trecho(lambda g: meta[g]["rn"] == 1 and ticks[g][2]["y"] < -8 and meta[g]["t"] < X_KO)
    if pulo:
        chao = camadas[2][0]
        # o log dá a posição do Explod no cenário: o anel nasce em y = -3 e tem de ficar lá
        erro = max(abs(ticks[g][2]["camadas"][chao]["py"] + 3) for g in pulo if ticks[g][2]["camadas"].get(chao))
        nota(f"pulo: P2 sobe até {-min(ticks[g][2]['y'] for g in pulo):.0f} px; o anel de chão fica no chão "
             f"(desvio máximo {erro:.2f} px da linha do chão)", erro <= 1.5)
    else:
        nota("pulo: o P2 não saiu do chão no log", False)

    fim = trecho(lambda g: meta[g]["rn"] == 1 and meta[g]["rs"] >= 3)
    if fim:
        com = [g for g in fim if all(ticks[g][1]["camadas"].get(c) for c in camadas[1])]
        pose = [g for g in fim if ticks[g][1]["st"] in (180, 181)]
        pose_com = [g for g in pose if g in set(com)]
        nota(f"fim do round 1 (RoundState 3 e 4): {len(fim)} ticks; o vencedor (P1) tem todas as camadas em {len(com)} "
             f"deles; pose de vitória (estado 180/181) em {len(pose)} ticks, {len(pose_com)} com a aura inteira",
             len(com) == len(fim) and len(pose) > 0 and len(pose_com) == len(pose))
        ko = fim[0]
        sem = next((g for g in gs if g >= ko and all(not ticks[g][2]["camadas"].get(c) for c in camadas[2])), None)
        primeiro_ko = next(g for g in gs if meta[g]["rn"] == 1 and meta[g]["t"] >= X_KO)
        nota(f"derrotado (P2): camadas somem {sem - primeiro_ko if sem else '?'} ticks depois do KO", sem is not None
             and sem - primeiro_ko <= 60)
    else:
        nota("fim do round 1: o log não chegou ao RoundState 3", False)

    r2 = trecho(lambda g: meta[g]["rn"] == 2)
    if r2:
        zero = [g for g in r2 if meta[g]["rs"] == 0]
        intro = [g for g in r2 if meta[g]["rs"] == 1]
        sobra = max((ticks[g][j]["ne"] for g in zero[1:] for j in (1, 2)), default=0)
        nota(f"round 2, antes da intro (RoundState 0, {len(zero)} ticks): no máximo {sobra} Explod "
             f"(fora o primeiro tick, em que a limpeza ainda vai rodar)", len(zero) > 1 and sobra == 0)
        ligada = [g for g in intro if all(ticks[g][j]["camadas"].get(c) for j in (1, 2) for c in camadas[j])]
        nota(f"round 2, intro (RoundState 1, {len(intro)} ticks): a aura dos dois está inteira em {len(ligada)} deles "
             f"(o Despertar segue ligado do round 1)", len(intro) > 0 and len(ligada) >= len(intro) - 3)
        depois = [g for g in r2 if meta[g]["rs"] == 2 and meta[g]["t"] >= X_DESLIGA2 + 120]
        if depois:
            resto = max(ticks[g][j]["ne"] for g in depois[-5:] for j in (1, 2))
            nota(f"round 2, desligado no tick {X_DESLIGA2}: {resto} Explod no fim do log", resto == 0)
        else:
            nota("round 2: o filme acabou antes de desligar (sem medida do desligar no round 2)")
    else:
        nota("round 2: o log não chegou lá", False)
    pico = {j: max(ticks[g][j]["ne"] for g in gs) for j in (1, 2)}
    nota(f"explods no pior tick: P1 {pico[1]}, P2 {pico[2]} (teto {TETO_EXPLODS})", max(pico.values()) <= TETO_EXPLODS)
    nota.fechar(saida / "medidas_extra.txt")


# ------------------------------------------------------------------ roteiro padrao (vídeo + log)

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("filme", type=Path)
    ap.add_argument("--saida", type=Path)
    ap.add_argument("--inicio", type=int, default=160, help="primeiro tick dos 2 s guardados quadro a quadro")
    ap.add_argument("--extra", action="store_true", help="o filme é do roteiro extra (mede só o log)")
    a = ap.parse_args()
    saida = (a.saida or a.filme / "medida").resolve()
    saida.mkdir(parents=True, exist_ok=True)
    if a.extra:
        medir_extra(a.filme, saida)
    todos = saida / "todos"
    shutil.rmtree(todos, ignore_errors=True)
    todos.mkdir()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(a.filme / "luta.mp4"), "-start_number", "0",
                    str(todos / "%04d.png")], check=True)
    total = len(list(todos.glob("*.png")))
    ticks = ler_log(a.filme / "aura_log.txt")
    nota = Notas()

    # ---- o vídeo começa alguns ticks depois do round: acha o atraso pelo instante em que a aura aparece
    base = quadro(todos, 0)
    ceus = {1: (20, 140, 420, 190), 2: (580, 140, 1100, 190)}  # acima das cabeças e abaixo do HUD: só a aura mexe

    def rec(img, cx):
        x0, y0, x1, y1 = cx
        return img[y0:y1, x0:x1]

    ceu = ceus[2]
    liga_video = next(n for n in range(1, total) if np.abs(rec(quadro(todos, n), ceu) - rec(base, ceu)).mean() > 1.0)
    liga_log = next(t for t in sorted(ticks) if ticks[t][2]["camadas"] and
                    (ticks[t][2]["camadas"].get(min(ticks[t][2]["camadas"]) + 1) or {}).get("sy", 0) > 0.5)
    atraso = liga_log - liga_video  # tick do log = quadro do vídeo + atraso
    nota(f"vídeo: {total} quadros; a coluna chega à faixa acima da cabeça no quadro {liga_video} = tick {liga_log} "
         f"do log (atraso {atraso})")

    # segundo ponto de sincronia: o tick em que o P1 troca de lado (some da esquerda num quadro só). O motor na
    # sandbox não anda exatamente no passo do gravador; com dois pontos, tick -> quadro vira uma reta.
    t_vira = next(t for t in sorted(ticks) if t > VIRA - 5 and ticks[t][1]["x"] > 0)
    velho = (120, 200, 440, CHAO_Y)
    anterior, saltos = quadro(todos, t_vira - atraso - 31), {}
    for n in range(t_vira - atraso - 30, min(total, t_vira - atraso + 31)):
        atual = quadro(todos, n)
        saltos[n] = np.abs(rec(atual, velho) - rec(anterior, velho)).mean()
        anterior = atual
    vira_video = max(saltos, key=saltos.get)
    passo_video = (vira_video - liga_video) / (t_vira - liga_log)
    nota(f"sincronia: o P1 troca de lado no tick {t_vira} = quadro {vira_video}; o vídeo anda {passo_video:.4f} quadro "
         f"por tick (1 = passo certo)", 0.95 <= passo_video <= 1.05)

    def v(t):  # tick do log -> quadro do vídeo
        return int(round(liga_video + (t - liga_log) * passo_video))

    # ---- 2 s quadro a quadro
    pasta_q = saida / "quadros"
    shutil.rmtree(pasta_q, ignore_errors=True)
    pasta_q.mkdir()
    for k in range(120):
        shutil.copy2(todos / f"{v(a.inicio) + k:04d}.png", pasta_q / f"{a.inicio + k:04d}.png")
    nota(f"2 s quadro a quadro: {pasta_q} (ticks {a.inicio} a {a.inicio + 119})")

    # ---- log: o que o motor fez
    camadas = {j: sorted(ticks[LIGA + 40][j]["camadas"]) for j in (1, 2)}
    loop = (LIGA + 60, SURTO1 - 2)
    for j in (1, 2):
        for c in camadas[j]:
            el = serie(ticks, j, c, "el", *loop)
            espera = maior_espera(list(el))
            nota(f"P{j} camada {c}: {len(set(el))} quadros no loop, o mesmo quadro fica no máximo {espera} ticks", espera <= 3)
            sx, sy, an = (serie(ticks, j, c, k, *loop) for k in ("sx", "sy", "an"))
            fora_de_1 = max(np.abs(np.abs(sx) - 1).max(), np.abs(sy - 1).max())
            nota(f"P{j} camada {c}: no loop o motor não escala nem gira (maior desvio da escala {fora_de_1:.4f}, "
                 f"ângulo máximo {np.abs(an).max():.2f})", fora_de_1 < 0.001 and np.abs(an).max() < 0.01)
            px, py = (serie(ticks, j, c, k, *loop) for k in ("px", "py"))
            passo = np.hypot(np.diff(px), np.diff(py))
            deriva = px.max() - px.min() + py.max() - py.min() > 0.5
            nota(f"P{j} camada {c}: posição muda em {(passo > 0).mean() * 100:.0f}% dos ticks do loop, passo máximo "
                 f"{passo.max():.2f} px" + ("" if deriva else " (camada sem deriva: só anima)"),
                 passo.max() <= 1.0 and (not deriva or (passo > 0).mean() >= 0.9))
            for nome, (ta, tb) in (("surto", (SURTO1, SURTO1 + 70)), ("liga", (LIGA + 1, LIGA + 40)),
                                   ("desliga", (DESLIGA, DESLIGA + 34))):
                d = max(np.abs(np.diff(np.abs(serie(ticks, j, c, k, ta, tb)))).max() for k in ("sx", "sy"))
                nota(f"P{j} camada {c}: escala anda no máximo {d * 100:.2f}% por tick no trecho {nome}", d <= 0.07)
        px = {c: serie(ticks, j, c, "px", *loop) for c in camadas[j]}
        vivas = [c for c in camadas[j] if px[c].max() - px[c].min() > 0.5]
        for i, c1 in enumerate(vivas):
            for c2 in vivas[i + 1:]:
                co = float(np.corrcoef(px[c1], px[c2])[0, 1])
                nota(f"P{j} camadas {c1} x {c2}: correlação da posição {co:+.2f}", abs(co) < 0.9)
        juntos = np.mean([len({ticks[t][j]["camadas"][c]["el"] for c in camadas[j]}) for t in range(*loop)])
        nota(f"P{j}: em média {juntos:.1f} elementos diferentes ao mesmo tempo em {len(camadas[j])} camadas",
             juntos >= len(camadas[j]) - 1)
        pico = max(np.abs(serie(ticks, j, camadas[j][1], "sx", SURTO1, SURTO1 + 70)))
        nota(f"P{j} surto: a escala da camada {camadas[j][1]} vai de 1.000 a {pico:.3f} e volta a "
             f"{np.abs(serie(ticks, j, camadas[j][1], 'sx', VIRA - 12, VIRA - 2)).max():.3f}", pico > 1.05)
        el_surto = serie(ticks, j, camadas[j][1], "el", SURTO1 + 12, SURTO1 + 30)
        passo = np.mean(np.diff(el_surto) % len(set(serie(ticks, j, camadas[j][1], "el", *loop))))
        nota(f"P{j} surto: a animação anda {passo:.2f} quadro por tick (calma: 0.5)", passo > 0.8)
        antes, depois = ticks[VIRA - 5][j], ticks[VIRA + 20][j]
        fa = [depois["camadas"][c]["fa"] for c in camadas[j]]
        t_lut = next(t for t in range(VIRA - 5, VIRA + 20) if ticks[t][j]["f"] != antes["f"])
        t_cam = next(t for t in range(VIRA - 5, VIRA + 30) if ticks[t][j]["camadas"][camadas[j][1]]["fa"] != antes["f"])
        nota(f"P{j} virada: lutador de {antes['f']:+d} para {depois['f']:+d} no tick {t_lut}; as camadas trocam de lado "
             f"{t_cam - t_lut} ticks depois (apagando antes), camadas agora {fa}",
             depois["f"] == -antes["f"] and all(x == depois["f"] for x in fa) and 3 <= t_cam - t_lut <= 8)
        some = min(t for t in ticks if t > DESLIGA and all(ticks[t][j]["camadas"][c] is None for c in camadas[j]))
        ultimo = max(ticks)
        nota(f"P{j} desliga: camadas somem {some - DESLIGA} ticks depois; explods no fim do filme (tick {ultimo}): "
             f"{ticks[ultimo][j]['ne']}", ticks[ultimo][j]["ne"] == 0)
        h_surto = min(ticks[t][j]["h"] for t in range(SURTO2 + 14, SURTO2 + 38))
        h_calmo = max(ticks[t][j]["h"] for t in range(*loop))
        nota(f"P{j} esconde: a camada {camadas[j][2]} apaga enquanto o especial toca (fator {h_surto:.2f} no surto, "
             f"{h_calmo:.2f} no loop) e volta ({ticks[SURTO2 + 75][j]['h']:.2f} 75 ticks depois)",
             h_surto > 0.9 and h_calmo == 0 and ticks[SURTO2 + 75][j]["h"] == 0)
        ne_loop = max(ticks[t][j]["ne"] for t in range(*loop))
        ne_pico = max(ticks[t][j]["ne"] for t in ticks)
        nota(f"P{j} explods vivos: até {ne_loop} no loop calmo, {ne_pico} no pior tick do filme (teto {TETO_EXPLODS})",
             ne_pico <= TETO_EXPLODS)

    # ---- vídeo: mudança entre quadros vizinhos, medida acima das cabeças (embaixo o corpo de teste ginga)
    ceus[0] = (20, 140, 1260, 190)  # a faixa inteira: depois da virada as duas auras se cruzam
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
        return np.array([viz[j][v(t)] for t in range(ta, tb) if v(t) not in fora and 0 <= v(t) < total - 1])

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
             dl.max() / m <= 5.0)  # a coluna sobe dos pés: a borda dela cruza a faixa medida em poucos quadros
    antes_d, dd = trecho(0, DESLIGA - 60, DESLIGA), trecho(0, DESLIGA, min(DESLIGA + 60, total + atraso - 2))
    nota(f"vídeo, desligando (as duas auras, faixa inteira): maior mudança por quadro {dd.max():.2f} = "
         f"{dd.max() / np.median(antes_d):.2f}x a mediana dos 60 ticks de antes", dd.max() / np.median(antes_d) <= 3.0)

    # ---- franja verde, corpo legível por faixa, HUD na frente, tamanho
    def verde(img):
        return (img[..., 1] > 200) & (img[..., 0] < 90) & (img[..., 2] < 90)

    def corpo_de(img, x0, x1):
        """Pixels do corpo de teste na coluna x0..x1: tudo o que não é o azul do cenário, dos pés até a cabeça."""
        r_, g_, b_ = (img[..., i] for i in range(3))
        m = ~((b_ > r_ + 25) & (b_ > g_ + 5))
        m[:CHAO_Y - (ALTURA_LUTADOR + 4) * PX] = False
        m[CHAO_Y:] = False
        m[:, :x0] = False
        m[:, x1:] = False
        return m

    FAIXAS = (("tronco", ALTURA_LUTADOR + 4, 45, 0.97), ("pernas", 45, 10, 0.95), ("pés", 10, 0, 0.60))

    def legivel(nome, j, pares, x0, x1):
        """pares: [(quadro com aura, [quadros de referência sem aura])]. O pior par decide, faixa por faixa."""
        pior = {f[0]: (1.0, None) for f in FAIXAS}
        for n_com, refs in pares:
            com = quadro(todos, n_com)
            # a captura escorrega 1 ou 2 quadros: fica a referência em que o tronco mais bate
            melhor = None
            for n_ref in refs:
                ref = quadro(todos, n_ref)
                corpo = corpo_de(ref, x0, x1)
                igual = np.abs(com - ref).max(axis=2) <= 24
                tronco = corpo.copy()
                tronco[CHAO_Y - 45 * PX:] = False
                nota_t = igual[tronco].mean() if tronco.any() else 0
                if melhor is None or nota_t > melhor[0]:
                    melhor = (nota_t, corpo, igual)
            _, corpo, igual = melhor
            for nome_f, alto, baixo, _ in FAIXAS:
                m = corpo.copy()
                m[:CHAO_Y - alto * PX] = False
                m[CHAO_Y - baixo * PX:] = False
                if m.sum() > 200 and igual[m].mean() < pior[nome_f][0]:
                    pior[nome_f] = (float(igual[m].mean()), n_com)
        for nome_f, _, _, minimo in FAIXAS:
            valor, onde = pior[nome_f]
            nota(f"P{j} corpo legível, {nome} ({len(pares)} quadros): {nome_f} {valor * 100:.1f}% igual ao desenho sem "
                 f"aura no pior quadro ({onde})", valor >= minimo)

    n_sem = max(0, v(LIGA) - 30)
    sem = quadro(todos, n_sem)
    colunas = {1: (120, 440), 2: (560, 880)}                     # antes da virada: P1 em x=-90, P2 em x=20
    colunas_depois = {1: (880, 1280), 2: (480, 860)}             # depois: P1 à direita do P2 (o motor os afasta)
    for j in (1, 2):
        x0, x1 = colunas[j]
        antes = int(verde(sem[90:CHAO_Y, x0 - 100:x1 + 100]).sum())
        pior = max(int(verde(quadro(todos, v(t))[90:CHAO_Y, x0 - 100:x1 + 100]).sum()) for t in range(loop[0], loop[1], 3))
        nota(f"P{j} pixels de verde de fundo na região da aura: {antes} antes de ligar, {pior} no pior quadro do loop",
             pior <= antes)
        # loop: a ginga dá uma volta a cada 48 ticks; referência = o mesmo desenho antes de ligar
        pares = []
        for t in range(loop[0], loop[1], 7):
            n = v(t)
            k = (n - 2) // 48
            pares.append((n, [n - 48 * kk + d for kk in (k, k - 1) for d in (-2, -1, 0, 1, 2)
                              if 0 <= n - 48 * kk + d < v(LIGA) - 1]))
        legivel("loop", j, [p for p in pares if p[1]], x0, x1)
        # surto: o corpo está no soco do estado 1000; referência = o mesmo soco dado sem aura no fim do filme
        x0, x1 = colunas_depois[j]
        # (janela larga: no fim do filme o gravador pode estar alguns quadros fora do passo; vale o quadro do soco
        # sem aura em que o tronco mais bate, e pernas e pés são medidos nesse mesmo quadro)
        pares = [(v(SURTO2 + d), [v(SOCO_SEM_AURA + d) + e for e in range(-15, 16) if v(SOCO_SEM_AURA + d) + e < total])
                 for d in range(6, 40, 3)]
        legivel("surto", j, [p for p in pares if p[1]], x0, x1)
        com = quadro(todos, v(loop[0] + 20))
        mudou = np.abs(com - sem).max(axis=2) > 40
        mudou[:, :colunas[j][0] - 20] = False
        mudou[:, colunas[j][1] + 20:] = False
        ys = np.nonzero(mudou.any(axis=1))[0]
        visivel = (CHAO_Y - ys.min()) / PX
        nota(f"P{j} tamanho: a aura muda a tela dos pés até {visivel:.0f} px do jogo acima do chão "
             f"(topo da tela = {CHAO_Y / PX:.0f}); lutador = {ALTURA_LUTADOR} px", visivel >= 1.4 * ALTURA_LUTADOR)
    for nome, (x0, y0, x1, y1) in HUD.items():
        ref = sem[y0:y1, x0:x1]
        pior = max(float((np.abs(quadro(todos, v(t))[y0:y1, x0:x1] - ref).max(axis=2) > 24).mean())
                   for t in list(range(LIGA + 10, DESLIGA + 40, 4)))
        nota(f"HUD na frente, {nome}: no pior quadro com a aura ligada, {pior * 100:.2f}% dos pixels da caixa mudam",
             pior <= 0.005)

    # ---- tiras para olhar
    cx1, cx2 = (0, 0, 600, 720), (440, 0, 1040, 720)
    for nome, t0, n, passo, caixa in (("p1_liga", LIGA - 2, 30, 1, cx1), ("p2_liga", LIGA - 2, 30, 1, cx2),
                                      ("p1_loop", loop[0], 60, 1, cx1), ("p2_loop", loop[0], 60, 1, cx2),
                                      ("p1_surto", SURTO1 - 2, 45, 1, cx1), ("p2_surto", SURTO1 - 2, 45, 1, cx2),
                                      ("vira", VIRA - 3, 30, 1, (300, 0, 1280, 720)),
                                      ("desliga", DESLIGA - 2, 45, 1, (400, 0, 1280, 720)),
                                      ("pes", loop[0], 30, 2, (120, 520, 880, 700)),
                                      ("resumo", LIGA - 10, 30, 18, (0, 0, 1280, 720))):
        tira(todos, saida, nome, v(t0), n, caixa, passo, largura=256 if nome in ("resumo", "pes") else 180,
             colunas=6 if nome in ("resumo", "pes") else 15)
    nota(f"tiras: {saida}/tira_*.png")
    shutil.rmtree(todos, ignore_errors=True)
    nota.fechar(saida / "medidas.txt")


if __name__ == "__main__":
    main()
