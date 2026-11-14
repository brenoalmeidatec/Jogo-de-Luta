#!/usr/bin/env python3
"""Pós-passo do Hazak (issue #44 do Breno, 2026-11-14): golpes de longe novos e o Diabo Loiro.

  python ferramentas/diabo_loiro.py        reaplica em chars/hazaki (o gerar_hazaki.py já chama no fim)

Como o efeitos.py e o parry.py, trabalha em cima do que o gerador gravou em chars/hazaki (sff, air, cns): os efeitos
entram no .sff como PNG de 32 bits (fora da paleta do corpo) e as ações do .air são escritas aqui.

Golpes de longe (os estados estão no gerar_hazaki.py, cns_especiais; os efeitos, no hazak_poderes_blender.py):
  Pedra       7401 a pedra subindo do chão (Explod), 1005 a pedra em voo (projétil), 7402 a pedra quebrando
  Bola de ki  7410 o ki juntando nas mãos (Explod), 1605 a bola vermelha (projétil), 7411 a bola estourando
Grupos e ações 7400-7499: fora dos do efeitos.py (8200-8291, 9200-9272) e do parry (7690/7691, 8290/8291).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conferir_sff as cs  # noqa: E402
import efeitos  # noqa: E402
from PIL import Image  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "chars/hazaki"
BLENDER = RAIZ / "sprites/efeitos_blender/hazaki"
E = efeitos.ESCALA_BLENDER  # escala no .air dos efeitos do Blender (o mesmo pixel dos do efeitos.py)
HD = 3                      # caixas do .air do Hazak: em 3x (hd.py), o motor divide pela escala do dono


def render(nome):
    """[(RGBA, eixo x, eixo y)] e ticks do efeito do Blender, cada desenho cortado no que tem pixel."""
    pasta = BLENDER / nome
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))
    quadros = []
    for arq in sorted(pasta.glob("[0-9][0-9].png")):
        img = Image.open(arq).convert("RGBA")
        cx = img.getchannel("A").getbbox() or (0, 0, 1, 1)
        quadros.append((img.crop(cx), meta["pivo"][0] - cx[0], meta["pivo"][1] - cx[1]))
    return quadros, meta["ticks"]


def caixa(nome, x0, y0, x1, y1):
    return f"{nome}Default: 1\n{nome}[0] = {x0 * HD}, {y0 * HD}, {x1 * HD}, {y1 * HD}"


# ação -> (efeito do Blender, grupo dos sprites, ticks por desenho ou None (o do render), laço a partir do desenho,
#          caixa de golpe (Clsn1) e de projétil (Clsn2) em px do jogo)
ACOES = {
    7401: ("pedra", 7401, 2, 0, None),
    1005: ("pedra", 7405, 2, 0, (-11, -11, 11, 11)),
    7402: ("pedra_quebra", 7402, None, None, None),
    7410: ("ki_carga", 7410, None, 6, None),
    1605: ("ki_bola", 7406, None, 0, (-13, -10, 6, 10)),
    7411: ("ki_estouro", 7411, None, None, None),
}


def texto_acao(grupo, quadros, ticks, laco, clsn):
    linhas = []
    if clsn:
        linhas.append(caixa("Clsn2", *clsn))
        linhas.append(caixa("Clsn1", *clsn))
    for i in range(len(quadros)):
        if laco is not None and i == laco:
            linhas.append("LoopStart")
        linhas.append(f"{grupo},{i}, 0,0, {ticks}, , , {E:g}, {E:g}")
    return "\n".join(linhas)


def aplicar(pasta=SAIDA):
    pasta = Path(pasta)
    sff, arq_air, arq_cns = (pasta / f"hazaki.{e}" for e in ("sff", "air", "cns"))
    air = arq_air.read_text(encoding="utf-8")
    # os sprites antigos da lasca e da estatueta (o que as ações 1005 e 1605 mostravam antes): saem do .sff
    velhos = set()
    for n in (1005, 1605):
        m = re.search(rf"^\[Begin Action {n}\][^\n]*\n(.*?)(?=^\[Begin Action|\Z)", air, re.M | re.S)
        if m:
            velhos |= {int(g) for g, _ in efeitos.RE_ELEMENTO.findall(m.group(1))}
    novos = {}
    for acao, (nome, grupo, ticks, laco, clsn) in ACOES.items():
        quadros, t = render(nome)
        air = efeitos.por_acao(air, acao, texto_acao(grupo, quadros, ticks or t, laco, clsn))
        novos[grupo] = quadros
    air = re.sub(r"\n{3,}", "\n\n", air)
    usados = {(int(g), int(i)) for g, i in efeitos.RE_ELEMENTO.findall(air)}
    velhos = {g for g in velhos if not any(u[0] == g for u in usados)}
    pal, nos, _ = cs.ler(sff)
    rle, png, vistos = [], [], set()
    for n in nos:
        k = (n["g"], n["i"])
        if k in vistos or n["g"] in novos or n["g"] in velhos:
            continue
        vistos.add(k)
        (png if n.get("png") else rle).append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
    for g, quadros in novos.items():
        for i, (img, ex, ey) in enumerate(quadros):
            png.append((g, i, img.width, img.height, int(ex), int(ey), efeitos.blob_png(img)))
    efeitos.gravar(sff, pal, rle, png)
    arq_air.write_text(air, encoding="utf-8", newline="\n")
    print(f"hazaki: pedra e bola de ki ({len(novos)} efeitos do Blender), {len(rle) + len(png)} sprites no .sff")


if __name__ == "__main__":
    aplicar()
