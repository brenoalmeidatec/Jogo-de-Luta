#!/usr/bin/env python3
"""Proporção dos lutadores (meta 1.0, pedido do Breno no fechamento da #50): os 6 lado a lado e a escala de cada ação.

  python3 ferramentas/proporcao.py fila [--saida PASTA]            os 6 em pé, base e despertado, no tamanho do jogo
  python3 ferramentas/proporcao.py acoes [lutador ...] [--saida P]  cabeça de cada quadro de cada ação contra a do parado
  python3 ferramentas/proporcao.py tudo [--saida PASTA]             as duas coisas (é o que o robô da 1.0 roda)

Tudo sai do que o jogo mostra: os sprites do chars/<l>/<l>.sff na ordem do .air, na escala do [Size] do .cns
(xscale/yscale; o corpo é desenhado em 3x e mostrado em 1/3) e na tela de 320x240 do localcoord dos lutadores.
O despertado usa o [RemapPreset despertado], como o motor faz.

FILA: cada lutador em pé (ação 0, primeiro desenho), com linhas de 10 em 10 unidades de tela e a altura escrita
embaixo. A regra do Breno é a proporção de KOF: lutador comum em volta de 110 de 180 de altura de tela útil; aqui
anotamos a altura em unidades da tela de 240 e em % dela, para comparar um com o outro.

AÇÕES: a régua da cabeça da ferramenta de pixel (ferramentas/pixel/reguas.py) procura a cabeça do parado em cada
desenho, de 80% a 125%, e dá a escala. A missão da #51 manda manter a escala em toda ação (agachado só fica mais baixo,
nunca encolhe nem cresce) e corrigir o que passar de uns 3%. A régua tem uns 4-5% de incerteza em quadro redesenhado,
então: até 6% passa, de 6% a 10% é "olhar", acima de 10% numa ação inteira (mediana dos quadros) é defeito.
Quadro em que a cabeça não foi achada com nota boa (deitado, de costas, borrão) não conta.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI / "pixel"))
RAIZ = AQUI.parent

from conferir_sff import ler  # noqa: E402
import tira_jogo as tj  # noqa: E402

LUTADORES = ["pengaro", "hazaki", "ck", "gutto", "raiclaven", "gbzin"]
NOMES = {"pengaro": ("Pengaró", "Endiabrado"), "hazaki": ("Hazak", "Diabo Loiro"), "ck": ("CK", "Ratão"),
         "gutto": ("Gutto", "Garanhão"), "raiclaven": ("Raiclaven", "Cientista"), "gbzin": ("Gbzin", "Grão-Pastor")}
TELA_H = 240
PASSA, OLHAR, DEFEITO = 0.06, 0.10, 0.10
NOTA_MIN = 0.55
AMOSTRA = 4


def escala_do_cns(cns):
    m = re.search(r"(?ims)^\[Size\].*?^\s*xscale\s*=\s*([\d.]+).*?^\s*yscale\s*=\s*([\d.]+)", cns)
    return (float(m.group(1)), float(m.group(2))) if m else (1.0, 1.0)


class Lutador:
    def __init__(self, nome):
        self.nome = nome
        pasta = RAIZ / "chars" / nome
        self.cns = (pasta / f"{nome}.cns").read_text(encoding="utf-8", errors="replace")
        self.air = tj.acoes((pasta / f"{nome}.air").read_text(encoding="utf-8", errors="replace"))
        self.pal, nos, _ = ler(pasta / f"{nome}.sff")
        import conferir_sff as cs
        self.extras = cs.EXTRAS.get(str(pasta / f"{nome}.sff"), [])
        self.sprites = {}
        for n in nos:
            self.sprites.setdefault((n["g"], n["i"]), n)
        self.sx, self.sy = escala_do_cns(self.cns)
        try:
            self.remap = tj.remap_despertado(self.cns)
        except Exception:  # noqa: BLE001 - lutador sem RemapPreset
            self.remap = {}

    def desenho(self, g, i, despertado=False):
        chave = self.remap.get((g, i), (g, i)) if despertado else (g, i)
        n = self.sprites.get(chave)
        if n is None:
            return None
        pal = self.pal
        pi = n.get("pi") or 0
        if pi >= 2 and pi - 2 < len(self.extras):  # paleta própria do despertado (gerar_pengaro.escrever_sff)
            pal = self.extras[pi - 2]
        return np.array(tj.imagem(n, pal).convert("RGBA")), (n["x"], n["y"])

    def quadros(self, acao, despertado=False):
        out, vistos = [], set()
        for g, i, x, y, t in self.air.get(acao, []):
            if g < 0 or (g, i) in vistos:
                continue
            vistos.add((g, i))
            d = self.desenho(g, i, despertado)
            if d is not None:
                out.append(((g, i), d[0], d[1]))
        return out

    def parado(self, despertado=False):
        q = self.quadros(0, despertado)
        return q[0] if q else None


def recorte(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return ys.min(), ys.max(), xs.min(), xs.max()


# ------------------------------------------------------------------ FILA
def fila(saida, zoom=3):
    figuras = []
    for nome in LUTADORES:
        L = Lutador(nome)
        for desp in (False, True):
            p = L.parado(desp)
            if p is None:
                continue
            chave, a, (ex, ey) = p
            if desp and chave == L.parado(False)[0] and not L.remap:
                continue
            y0, y1, x0, x1 = recorte(a)
            alt = (ey - y0) * L.sy  # do topo da figura até o chão (eixo), em unidades de tela
            img = Image.fromarray(a[y0:y1 + 1, x0:x1 + 1])
            w = max(1, round(img.width * L.sx * zoom))
            h = max(1, round(img.height * L.sy * zoom))
            img = img.resize((w, h), Image.LANCZOS)
            pe = (ey - y1 - 1) * L.sy * zoom  # quanto o desenho passa (ou falta) do chão
            figuras.append({"lutador": nome, "forma": NOMES[nome][1 if desp else 0], "despertado": desp,
                            "altura": round(alt, 1), "pct": round(100 * alt / TELA_H, 1), "img": img, "pe": pe})
    gap = 14 * zoom
    W = sum(f["img"].width for f in figuras) + gap * (len(figuras) + 1)
    H = int(TELA_H * 0.75 * zoom) + 60
    chao = H - 50
    folha = Image.new("RGB", (W, H), (236, 236, 240))
    d = ImageDraw.Draw(folha)
    try:
        from PIL import ImageFont
        fonte = ImageFont.truetype("DejaVuSans.ttf", 11 * zoom // 2)
    except OSError:
        fonte = None
    for u in range(0, int(TELA_H * 0.75) + 1, 10):
        y = chao - u * zoom
        d.line([(0, y), (W, y)], fill=(200, 200, 206) if u % 50 else (150, 150, 160), width=1)
        if u % 50 == 0:
            d.text((2, y - 16), str(u), fill=(90, 90, 100), font=fonte)
    media = float(np.mean([f["altura"] for f in figuras if not f["despertado"]]))
    ym = chao - media * zoom
    d.line([(0, ym), (W, ym)], fill=(220, 30, 30), width=2)
    d.text((10, ym - 26), f"média da forma base: {media:.0f}", fill=(220, 30, 30), font=fonte)
    x = gap
    for f in figuras:
        im = f["img"]
        folha.paste(im, (x, int(round(chao - im.height + f["pe"]))), im)
        d.text((x, chao + 6), f"{NOMES[f['lutador']][0] if not f['despertado'] else f['forma']}", fill=(0, 0, 0), font=fonte)
        d.text((x, chao + 24), f"{f['altura']:.0f} ({f['pct']:.0f}%)", fill=(0, 0, 160), font=fonte)
        x += im.width + gap
    saida.mkdir(parents=True, exist_ok=True)
    folha.save(saida / "fila_lado_a_lado.png")
    dados = [{k: v for k, v in f.items() if k not in ("img", "pe")} for f in figuras]
    (saida / "fila.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{'lutador':<12}{'forma':<14}{'altura':>8}{'% tela':>8}{'vs média':>10}")
    for f in dados:
        print(f"{f['lutador']:<12}{f['forma']:<14}{f['altura']:>8.1f}{f['pct']:>7.1f}%{100 * f['altura'] / media - 100:>+9.1f}%")
    return dados


# ------------------------------------------------------------------ AÇÕES
def _reduz(a, f):
    """Desenho HD (3x) na grade do jogo: a régua roda rápido e mede o que o jogador vê."""
    if f >= 0.99:
        return a
    im = Image.fromarray(a)
    return np.array(im.resize((max(1, round(im.width * f)), max(1, round(im.height * f))), Image.NEAREST))


def _escala_rapida(R, a, tmpl):
    """A régua da cabeça só no alto da figura (sem a segunda busca girando até 90 graus, que leva 10x mais e só
    serve para deitado; quadro deitado fica de fora pela nota)."""
    m = R.mascara(a)
    if not m.any():
        return None
    ys, xs = np.nonzero(m)
    pad = int(tmpl.shape[0] * 0.8)
    x0, x1 = max(0, xs.min() - pad), min(a.shape[1], xs.max() + pad)
    y0 = max(0, ys.min() - pad)
    reg = a[y0:min(a.shape[0], ys.min() + int(tmpl.shape[0] * 2.6)), x0:x1]
    v, e, _ang, _p = R._busca(reg, tmpl, np.arange(R.FAIXA[0], R.FAIXA[1] + 1e-6, 0.01), range(-20, 21, 10))
    return float(e), float(v), None


def acoes(nomes, saida, maximo=8999):
    import reguas as R
    relatorio = {}
    ruins = []
    for nome in nomes:
        L = Lutador(nome)
        for desp in (False, True):
            if desp and not L.remap:
                continue
            p = L.parado(desp)
            if p is None:
                continue
            fator = 1.0  # no 3x do .sff: na grade do jogo (1/3) a cabeça vira um molde de ~14 px e a régua erra ±10%
            base = _reduz(p[1], fator)
            tmpl, _ = R.cabeca_do_parado(base)
            e0, _, _ = _escala_rapida(R, base, tmpl)
            forma = NOMES[nome][1 if desp else 0]
            vistos = set()
            linhas = {}
            for acao in sorted(L.air):
                if not (1 <= acao <= maximo) or acao in (5900, 5901):
                    continue
                qs = L.quadros(acao, desp)
                chave = frozenset(c for c, *_ in qs)
                if not qs or chave in vistos:
                    continue
                vistos.add(chave)
                med = []
                if len(qs) > AMOSTRA:  # até AMOSTRA quadros espalhados pela ação (a régua leva ~0,6 s por quadro)
                    qs = [qs[round(k * (len(qs) - 1) / (AMOSTRA - 1))] for k in range(AMOSTRA)]
                for c, a, _ in qs:
                    r = _escala_rapida(R, _reduz(a, fator), tmpl)
                    if r and r[1] >= NOTA_MIN:
                        med.append(r[0] / e0)
                if len(med) < max(1, len(qs) // 3):
                    continue
                mediana = float(np.median(med))
                linhas[acao] = {"mediana": round(mediana, 3), "min": round(min(med), 3), "max": round(max(med), 3),
                                "medidos": len(med), "quadros": len(qs)}
                desvio = abs(mediana - 1)
                if desvio > DEFEITO:
                    ruins.append((nome, forma, acao, mediana, "DEFEITO"))
                elif desvio > PASSA:
                    ruins.append((nome, forma, acao, mediana, "olhar"))
            relatorio[f"{nome}{'_e' if desp else ''}"] = linhas
            n_def = sum(1 for r in ruins if r[0] == nome and r[1] == forma and r[4] == "DEFEITO")
            n_olh = sum(1 for r in ruins if r[0] == nome and r[1] == forma and r[4] == "olhar")
            print(f"{nome:<10} {forma:<12} {len(linhas):4d} ações medidas, {n_def} defeito(s), {n_olh} para olhar",
                  flush=True)
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "escala_acoes.json").write_text(json.dumps(relatorio, indent=1), encoding="utf-8")
    for nome, forma, acao, m, tipo in ruins:
        print(f"   {tipo:<8}{nome:<10}{forma:<12} ação {acao:<6} cabeça a {100 * m:.0f}% da do parado")
    return ruins


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("modo", choices=["fila", "acoes", "tudo"])
    ap.add_argument("lutadores", nargs="*")
    ap.add_argument("--saida", type=Path, default=RAIZ / "docs" / "proporcao-1.0")
    a = ap.parse_args()
    ruins = []
    if a.modo in ("fila", "tudo"):
        fila(a.saida)
    if a.modo in ("acoes", "tudo"):
        ruins = acoes(a.lutadores or LUTADORES, a.saida)
        defeitos = [r for r in ruins if r[4] == "DEFEITO"]
        print(f"\nRESUMO: {len(defeitos)} ação(ões) com a escala fora (> {DEFEITO:.0%}), "
              f"{len(ruins) - len(defeitos)} para olhar")
        sys.exit(1 if defeitos else 0)


if __name__ == "__main__":
    main()
