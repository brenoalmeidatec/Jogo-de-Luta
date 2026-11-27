#!/usr/bin/env python3
"""Agarrões com animação própria (issue #45, pedido do Breno de 2026-11-15): liga no lutador as folhas de
sprites/<l>/quadros/folhas_agarrao/ (feitas pela fila de ferramentas/fila_agarroes.py).

  python ferramentas/agarrao_folhas.py [lutador ...]     (sem nome: ck, gutto e pengaro) reescreve chars/<l>/
  python ferramentas/agarrao_folhas.py --da-arte pengaro  monta as folhas com quadros da arte atual (DA_ARTE) e liga

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
    "pengaro": {"pe": mk.padrao("Roda de Capoeira com Garrafa", altos=(True, False, True), fim="por_cima"),
                "baixo": mk.padrao("Agarrão agachado", altos=(False, False, False)),
                "comando": mk.padrao("Martelo e Garrafada", altos=(False, True, False), danos=(30, 30, 30, 60))},
}
# vítima: ação -> [(desenho, ticks)] (-1 = segura)
VITIMA = {mk.V_PRESO: [(1, -1)], mk.V_ALTO: [(2, 4), (3, 6), (1, -1)], mk.V_BAIXO: [(4, 4), (5, 6), (1, -1)],
          mk.V_SOBE: [(6, -1)], mk.V_CAI: [(7, -1)]}


# Folhas montadas só com quadros da arte atual do lutador (sprites/<l>/quadros_arcade_hd/<folha>/<NN>.png), sem
# gerar imagem: o Breno pediu na #45 (2026-11-15) o Pengaró "na arte atual dele (base e Endiabrado, sem misturar
# roupa antiga)". A folha e_ usa os mesmos quadros com e_ na frente (o Endiabrado tem as mesmas poses).
# Formato da folha padrão: 1 alcança, 2 segura, 3/4 pancada A, 5/6 pancada B, 7/8 arremesso; vítima: 1 (escala),
# 2 preso, 3/4 apanha em cima, 5/6 apanha embaixo, 7 sobe, 8 cai.
DA_ARTE = {
    "pengaro": {
        # pega pelo braço, soco na cara, soco no estômago, soco na cara, vira de costas e joga por cima do ombro
        "agarrao_pe": "agarrao 1, agarrao 3, soco 3, soco 5, baixo_soco 3, baixo_soco 5, agarrao 4, agarrao 5",
        # agachado: mão no chão pegando, soco baixo, rasteira curta, e levanta puxando
        "agarrao_baixo": "rasteirinha 0, rasteirinha 1, baixo_soco 3, baixo_soco 5, rasteirinha 2, rasteirinha 4, "
                         "agarrao 6, agarrao 7",
        # colado: joelhada, cabeçada e o martelo que manda longe
        "agarrao_comando": "agarrao 1, agarrao 3, martelo 2, martelo 3, cabecada 1, cabecada 3, martelo 2, martelo 4",
        "vitima": "apanha 0, apanha 1, apanha 3, apanha 4, apanha 5, apanha 6, queda 1, queda 3",
    },
}


def montar_da_arte(lutador):
    """Grava as folhas de DA_ARTE (base e e_) em sprites/<l>/quadros/folhas_agarrao/, com fundo transparente e a
    altura do parado da arte no PNG (figuras usa para a escala)."""
    from PIL import PngImagePlugin
    arte = RAIZ / f"sprites/{lutador}/quadros_arcade_hd"
    bb = Image.open(arte / "parado/00.png").getchannel("A").getbbox()
    info = PngImagePlugin.PngInfo()
    info.add_text("altura_parado", str(bb[3] - bb[1]))
    destino = RAIZ / f"sprites/{lutador}/quadros/folhas_agarrao"
    destino.mkdir(parents=True, exist_ok=True)
    for nome, lista in DA_ARTE[lutador].items():
        for pre in ("", "e_"):
            quadros = [Image.open(arte / f"{pre}{q.split()[0]}/{int(q.split()[1]):02d}.png").convert("RGBA")
                       for q in lista.split(",")]
            assert len(quadros) == 8, f"{nome}: {len(quadros)} quadros"
            w, h = quadros[0].size
            folha = Image.new("RGBA", (w * 8, h), (0, 0, 0, 0))
            for i, q in enumerate(quadros):
                folha.paste(q, (i * w, 0))
            folha.save(destino / f"{pre}{nome}.png", pnginfo=info)
            print(f"{lutador}: {pre}{nome} da arte atual ({lista})")


def folhas(lutador):
    pasta = RAIZ / f"sprites/{lutador}/quadros/folhas_agarrao"
    out = {}
    for nome, g in GRUPOS.items():
        for pre, soma in (("", 0), ("e_", DESPERTO)):
            f = pasta / f"{pre}{nome}.png"
            if f.exists():
                out[pre + nome] = (f, g + soma)
    return out


def figuras_alfa(img):
    """Folha montada da arte atual (montar_da_arte): 8 telas lado a lado com fundo transparente. Mesmo eixo do
    parry.figuras (tronco do 1º quadro, o resto relativo a ele) e chão na mediana das bases."""
    import animar_folha as af
    import numpy as np
    img = img.convert("RGBA")
    larg = img.width // 8
    cortes = []
    for i in range(8):
        cel = img.crop((i * larg, 0, (i + 1) * larg, img.height))
        cortes.append((cel.getchannel("A").getbbox(), cel))
    chao = float(np.median([cx[3] for cx, _ in cortes]))
    cx0, c0 = cortes[0]
    desvio = cx0[0] + af.tronco(c0.crop(cx0)) - 0.5 * larg
    return [(c.crop(cx), 0.5 * larg + desvio - cx[0], chao - cx[1]) for cx, c in cortes]


def figuras(folha, altura):
    """Os 8 desenhos da folha em 3x [(img, eixo x, eixo y)], o 1º com `altura` px. Folha da arte atual (com
    `altura_parado` no PNG): a escala vem do parado da própria arte, não do 1º desenho."""
    ref = Image.open(folha).info.get("altura_parado")
    figs = figuras_alfa(Image.open(folha)) if ref else parry.figuras(folha)
    fator = altura / (float(ref) if ref else figs[0][0].height)
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
    # junta os pedaços de cada boneco, quase só na horizontal (pé de cima não gruda na cabeça de baixo); se dois
    # bonecos vizinhos se encostam (um casco esticado no arremesso), tenta uma junção mais fina
    for kx in (15, 7, 3, 1):
        junta = cv2.dilate(corpo, np.ones((5 if kx > 1 else 1, kx), np.uint8))
        n, rot, st, cen = cv2.connectedComponentsWithStats(junta, connectivity=8)
        figs = [k for k in range(1, n) if st[k, cv2.CC_STAT_AREA] > 0.004 * corpo.size]
        if len(figs) - len(tirar) >= 8:
            break
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
    if sys.argv[1:2] == ["--da-arte"]:  # monta as folhas da arte atual e liga
        for l in sys.argv[2:]:
            montar_da_arte(l)
            aplicar(l)
        return
    if sys.argv[1:2] == ["--salvar"]:
        salvar(*sys.argv[2:5], tirar=tuple(int(v) for v in sys.argv[5:]))
        return
    for l in sys.argv[1:] or LUTADORES:
        aplicar(l)


if __name__ == "__main__":
    main()
