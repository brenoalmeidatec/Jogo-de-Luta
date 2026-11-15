#!/usr/bin/env python3
"""Agarrões com animação própria (issue #45, pedido do Breno de 2026-11-15): liga no lutador as folhas de
sprites/<l>/quadros/folhas_agarrao/ (feitas pela fila de ferramentas/fila_agarroes.py).

  python ferramentas/agarrao_folhas.py [lutador ...]     (sem nome: ck, gutto e pengaro) reescreve chars/<l>/

Trabalha em cima do que já está em chars/<l>/, como o parry.py (o Gutto não regenera na nuvem). Pode rodar de novo.
O que faz, para cada folha que existe:
  - corta os 8 desenhos direto da folha em 3x (regra da alta resolução), na paleta do .sff, com o 1º desenho
    (em pé) da altura do parado do jogo, e grava nos grupos 7800 (em pé), 7810 (agachado), 7820 (comando) e
    7850 (vítima); as folhas e_ do despertado vão em 7860/7870/7880/7890 e entram no [RemapPreset despertado]
    (o Despertar troca os desenhos sozinho);
  - agarrao_mk.py monta os estados 810/841/831 com esses desenhos (roteiro `padrao`) e o oponente no 820;
  - folha de vítima: ações 5940 a 5944 (preso, apanha em cima, apanha embaixo, arremessado, caindo), que os
    estados do oponente do agarrao_mk.py usam quando existem.
Sem a folha, o agarrão fica como estava. Depois de rodar: gerar_sons.ligar (feito aqui no fim).
"""
import re
import sys
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))
import agarrao_mk as mk  # noqa: E402
import conferir_sff as cs  # noqa: E402
import parry  # noqa: E402

LUTADORES = ("ck", "gutto", "pengaro")
GRUPOS = {"agarrao_pe": 7800, "agarrao_baixo": 7810, "agarrao_comando": 7820, "vitima": 7850}
DESPERTO = 60  # e_<folha> vai no grupo + 60
TIPO = {"agarrao_pe": "pe", "agarrao_baixo": "baixo", "agarrao_comando": "comando"}

# Roteiro de cada lutador quando a folha existe (formato fixo da fila: ver fila_agarroes.py)
ROTEIROS = {
    "ck": {"pe": mk.padrao("Gola na Mão", altos=(True, False, True)),
           "baixo": mk.padrao("Abaixa Aí", altos=(False, False, False)),
           "comando": mk.padrao("Saideira", altos=(True, False, True), danos=(30, 30, 30, 60))},
    "gutto": {"pe": mk.padrao("Clinch de Muay Thai", altos=(False, True, False)),
              "baixo": mk.padrao("Agarrão agachado", altos=(False, False, False)),
              "comando": mk.padrao("Clinch e Joelhada", altos=(False, False, False), danos=(30, 30, 30, 60))},
    "pengaro": {"pe": mk.padrao("Roda de Capoeira com Garrafa", altos=(True, False, True)),
                "baixo": mk.padrao("Agarrão agachado", altos=(False, False, False)),
                "comando": mk.padrao("Martelo e Garrafada", altos=(False, True, False), danos=(30, 30, 30, 60))},
}
# vítima: ação -> [(desenho, ticks)] (-1 = segura)
VITIMA = {mk.V_PRESO: [(1, -1)], mk.V_ALTO: [(2, 4), (3, 6), (1, -1)], mk.V_BAIXO: [(4, 4), (5, 6), (1, -1)],
          mk.V_SOBE: [(6, -1)], mk.V_CAI: [(7, -1)]}


def folhas(lutador):
    pasta = RAIZ / f"sprites/{lutador}/quadros/folhas_agarrao"
    out = {}
    for nome, g in GRUPOS.items():
        for pre, soma in (("", 0), ("e_", DESPERTO)):
            f = pasta / f"{pre}{nome}.png"
            if f.exists():
                out[pre + nome] = (f, g + soma)
    return out


def figuras(folha, altura):
    """Os 8 desenhos da folha em 3x [(img, eixo x, eixo y)], o 1º com `altura` px."""
    figs = parry.figuras(folha)
    fator = altura / figs[0][0].height
    saida = []
    for q, ex, ey in figs:
        g = q.resize((max(1, round(q.width * fator)), max(1, round(q.height * fator))), Image.LANCZOS)
        g = parry.sem_halo(g)
        cx = g.getchannel("A").getbbox()
        saida.append((g.crop(cx), round(ex * fator) - cx[0], round(ey * fator) - cx[1]))
    return saida


def altura_parado(air, nos):
    prim = re.search(r"^\s*(\d+)\s*,\s*(\d+)\s*,", parry.acao(air, 0) or "", re.M)
    ref = next((n for n in nos if (n["g"], n["i"]) == (int(prim.group(1)), int(prim.group(2)))), None)
    return ref["h"] if ref else 330


def gravar_sff(lutador, pasta, air, achadas):
    import efeitos
    sff = pasta / f"{lutador}.sff"
    pal, nos, _ = cs.ler(sff)
    nossos = {g for _, g in achadas.values()}
    todos = set(GRUPOS.values()) | {g + DESPERTO for g in GRUPOS.values()}
    altura = altura_parado(air, nos)
    rle, png, vistos = [], [], set()
    for n in nos:
        k = (n["g"], n["i"])
        if k in vistos or n["g"] in todos:
            continue
        vistos.add(k)
        (png if n.get("png") else rle).append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
    for nome, (f, g) in sorted(achadas.items()):
        for i, (q, ex, ey) in enumerate(figuras(f, altura)):
            rle.append((g, i, q.width, q.height, ex, ey, parry.quantizar(q, pal)))
    efeitos.gravar(sff, pal, rle, png)
    return altura, nossos


def remap(cns, achadas):
    """Linhas base -> despertado no [RemapPreset despertado] para cada folha com as duas formas."""
    m = re.search(r"^\[RemapPreset despertado\]\n(.*?)(?=^\[)", cns, re.M | re.S)
    if not m:
        return cns
    linhas = [ln for ln in m.group(1).rstrip("\n").split("\n")
              if not re.match(r"^78[0-9]{2},\d+\s*=", ln)]
    for nome, (_, g) in sorted(achadas.items()):
        if nome.startswith("e_") or f"e_{nome}" not in achadas:
            continue
        linhas += [f"{g},{i} = {g + DESPERTO},{i}" for i in range(8)]
    corpo = "\n".join(linhas).rstrip("\n") + "\n\n"
    return cns[:m.start(1)] + corpo + cns[m.end(1):]


def acoes_vitima(air, grupo):
    corpo = re.search(r"Clsn2(?:Default)?:\s*\d+\s*\n((?:\s*Clsn2\[\d+\][^\n]*\n)+)", parry.acao(air, 5000) or "")
    caixa = "Clsn2Default: " + str(corpo.group(1).count("Clsn2[")) + "\n" + corpo.group(1) if corpo else ""
    for n, quadros in VITIMA.items():
        texto = caixa + "\n".join(f"{grupo},{i}, 0,0, {t}" for i, t in quadros)
        air = parry.por_acao(air, n, texto)
    return air


def tirar_arte_despertada(cns, n):
    """A tentativa (800/830/840) com folha própria não troca mais para a ação 10xxx no Despertar (o remap troca)."""
    m = re.search(rf"^\[Statedef {n}\]\n.*?(?=^\[Statedef|\Z)", cns, re.M | re.S)
    bloco = re.sub(r"^\[State \d+, Arte despertada\]\n.*?\n\n", "", m.group(0), flags=re.M | re.S)
    return cns[:m.start()] + bloco + cns[m.end():]


def aplicar(lutador, pasta=None):
    pasta = Path(pasta) if pasta else RAIZ / "chars" / lutador
    achadas = folhas(lutador)
    if not achadas:
        print(f"{lutador}: sem folhas de agarrão próprias")
        return
    pa, pc = pasta / f"{lutador}.air", pasta / f"{lutador}.cns"
    air, cns = pa.read_text(encoding="utf-8"), pc.read_text(encoding="utf-8")
    altura, _ = gravar_sff(lutador, pasta, air, achadas)
    cns = remap(cns, achadas)
    desenhos = {}
    for nome, (_, g) in achadas.items():
        if nome in TIPO:
            desenhos[TIPO[nome]] = [f"{g},{i}" for i in range(8)]
        elif nome == "vitima":
            air = acoes_vitima(air, g)
    mk.PROPRIOS[lutador] = ROTEIROS[lutador]
    air, cns = mk.aplicar(lutador, air, cns, desenhos)
    for tipo in desenhos:
        cns = tirar_arte_despertada(cns, mk.TIPOS[tipo][0])
    pa.write_text(re.sub(r"\n{3,}", "\n\n", air), encoding="utf-8", newline="\n")
    pc.write_text(cns, encoding="utf-8", newline="\n")
    import gerar_sons
    gerar_sons.ligar(lutador, pasta)
    print(f"{lutador}: folhas próprias {sorted(achadas)} (parado com {altura} px em 3x)")


def salvar(captura, lutador, nome, tirar=()):
    """Guarda a captura da imagem gerada (zoom do Chrome, a imagem no canto e preto em volta) como a folha de 8
    desenhos numa fileira, um por célula. Acha cada boneco pelo recorte (o Gemini nem sempre respeita a grade 2x4),
    ordena por fileira e da esquerda para a direita; `tirar` = índices (0..) de bonecos a jogar fora (quadro a mais)."""
    import cv2
    import numpy as np
    a = np.asarray(Image.open(captura).convert("RGB")).astype(int)
    cheio = a.max(axis=2) > 40
    ys, xs = np.nonzero(cheio)
    a = a[:ys.max() + 1, :xs.max() + 1]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    fundo = (r > 170) & (b > 170) & (g < 130)
    corpo = (~fundo).astype(np.uint8)
    junta = cv2.dilate(corpo, np.ones((5, 15), np.uint8))  # quase só na horizontal: pé de cima não gruda na cabeça de baixo
    n, rot, st, cen = cv2.connectedComponentsWithStats(junta, connectivity=8)
    figs = [k for k in range(1, n) if st[k, cv2.CC_STAT_AREA] > 0.004 * corpo.size]
    meio = a.shape[0] / 2
    figs.sort(key=lambda k: (cen[k][1] > meio, cen[k][0]))
    figs = [k for i, k in enumerate(figs) if i not in tirar]
    assert len(figs) == 8, f"{len(figs)} bonecos na imagem (precisa de 8; use tirar)"
    caixas = [(st[k, 0], st[k, 1], st[k, 0] + st[k, 2], st[k, 1] + st[k, 3]) for k in figs]
    cel = max(x1 - x0 for x0, _, x1, _ in caixas) + 24
    alto = max(y1 for *_, y1 in caixas[:4]) - min(y0 for _, y0, *_ in caixas[:4])
    alto = max(alto, max(y1 for *_, y1 in caixas[4:]) - min(y0 for _, y0, *_ in caixas[4:])) + 24
    fila = Image.new("RGB", (cel * 8, alto), (255, 0, 255))
    rgb = a.astype(np.uint8)
    for i, (k, (x0, y0, x1, y1)) in enumerate(zip(figs, caixas)):
        linha = caixas[:4] if i < 4 else caixas[4:]
        chao = max(c[3] for c in linha)  # pés de cada fileira na mesma linha
        m = (rot[y0:y1, x0:x1] == k) & (corpo[y0:y1, x0:x1] > 0)
        pedaco = np.where(m[..., None], rgb[y0:y1, x0:x1], np.array([255, 0, 255], np.uint8))
        fila.paste(Image.fromarray(pedaco), (i * cel + (cel - (x1 - x0)) // 2, alto - 12 - (chao - y0)))
    destino = RAIZ / f"sprites/{lutador}/quadros/folhas_agarrao/{nome}.png"
    destino.parent.mkdir(parents=True, exist_ok=True)
    fila.save(destino)
    print(f"{destino.relative_to(RAIZ)}: {fila.width}x{fila.height}")


def main():
    if sys.argv[1:2] == ["--salvar"]:
        salvar(*sys.argv[2:5], tirar=tuple(int(v) for v in sys.argv[5:]))
        return
    for l in sys.argv[1:] or LUTADORES:
        aplicar(l)


if __name__ == "__main__":
    main()
