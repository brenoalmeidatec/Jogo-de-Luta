#!/usr/bin/env python3
"""Golpe agachado feito do próprio desenho do agachado, com o tronco dobrando em volta da cintura (pedido do Breno na
#32, 22/11: golpe agachado não levanta e a perna não estica). As pernas ficam como no agachado; acima da cintura o
desenho gira e anda para a frente, com a rotação crescendo suave numa faixa (sem linha de corte). Serve para quadro de
arte própria (despertado) que não tem kit de peças; no Pengaró base o mesmo dobrar() roda no pengaro_todo.py.

    python3 ferramentas/dobra_agachado.py pengaro_desp_cabecada

Cada receita (RECEITAS) diz: lutador, ação do .air, desenho do agachado (grupo, índice, já com a arte que o jogo mostra)
e a lista de quadros (graus para a frente, px para a frente na tela 3x, tiques, caixa de ataque ou None). Os desenhos
novos entram no .sff no grupo `grupo` e a ação é reescrita com eles (a Clsn2 padrão da ação fica). Depois rode
aura_no_corpo.py <lutador> (a aura e os MapSet por elemento saem dos desenhos) e encolher_sff.py <lutador>.
"""
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conferir_sff as cs  # noqa: E402
import efeitos  # noqa: E402
import ligar_pecas as lp  # noqa: E402
from pengaro_todo import dobrar  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
CAIXA_CABECADA = (20, -220, 120, -110)  # testa e ombro do agachado dobrado (a mesma da 410 da base)

RECEITAS = {
    # Pengaró despertado (sombras): cabeçada agachada 10410 do agachado dele (801,0); mesmos tiques até o contato
    # (o efeito do golpe usa AnimElem = 3) e quadros do meio na volta
    "pengaro_desp_cabecada": dict(lutador="pengaro", acao=10410, base=(801, 0), grupo=41410, quadros=[
        (0, 0, 3, None), (-10, -6, 4, None), (20, 16, 2, CAIXA_CABECADA), (20, 16, 6, CAIXA_CABECADA),
        (18, 14, 2, None), (14, 11, 3, None), (11, 9, 3, None), (8, 6, 3, None), (6, 4, 3, None), (4, 3, 3, None),
        (2, 1, 3, None), (0, 0, 3, None), (0, 0, 4, None)]),
    # CK despertado (Ratão): o golpe agachado forte 10410 subia inteiro com a garrafa no alto; agora sai do agachado
    # dele (789,0): recua o tronco e joga o peito e a mão da garrafa para a frente e para cima, pernas paradas
    "ck_desp_agachado_forte": dict(lutador="ck", acao=10410, base=(789, 0), grupo=41410, quadros=[
        (0, 0, 3, None), (-10, -6, 4, None), (18, 16, 2, (10, -250, 96, -120)), (18, 16, 6, (10, -250, 96, -120)),
        (16, 14, 2, None), (13, 11, 3, None), (10, 8, 3, None), (8, 6, 3, None), (6, 4, 3, None), (4, 3, 3, None),
        (2, 1, 3, None), (0, 0, 3, None), (0, 0, 4, None)]),
}


def rgba(n, pal):
    idx = np.frombuffer(n["px"], np.uint8).reshape(n["h"], n["w"])
    p = np.frombuffer(pal, np.uint8).reshape(256, 4)
    img = np.zeros((n["h"], n["w"], 4), np.uint8)
    img[..., :3] = p[idx][..., :3]
    img[..., 3] = np.where(idx == 0, 0, 255)
    return img


def fazer(r):
    lut = r["lutador"]
    sff = RAIZ / "chars" / lut / f"{lut}.sff"
    air = RAIZ / "chars" / lut / f"{lut}.air"
    pal, nos, _ = cs.ler(sff)
    extras = list(cs.EXTRAS.get(str(sff.resolve()), []))
    por_chave = {(n["g"], n["i"]): n for n in nos}
    base = por_chave[r["base"]]
    assert base.get("pi", 0) == 0 and not base.get("png"), "o desenho do agachado tem de estar na paleta do lutador"
    img = rgba(base, pal)
    # tela com folga para o tronco girar sem sair da imagem; o eixo do desenho vai junto
    folga = 120
    tela = np.zeros((img.shape[0] + 2 * folga, img.shape[1] + 2 * folga, 4), np.uint8)
    tela[folga:folga + img.shape[0], folga:folga + img.shape[1]] = img
    ax, ay = base["x"] + folga, base["y"] + folga
    prgb = lp.paleta_rgb(pal)
    unicos = list(dict.fromkeys((a, d) for a, d, _, _ in r["quadros"]))
    novos = []
    for k, (ang, dx) in enumerate(unicos):
        out = dobrar(tela, ang, dx)
        ys, xs = np.nonzero(out[..., 3] > 0)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rec = Image.fromarray(out[y0:y1, x0:x1])
        novos.append((r["grupo"], k, rec.width, rec.height, int(ax - x0), int(ay - y0),
                      lp.indexar(rec, prgb).tobytes(), 0))
    rle, png = [], []
    for n in nos:
        if n["g"] == r["grupo"]:
            continue  # rodada de novo: troca os desenhos do grupo
        if n.get("png"):
            png.append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
        else:
            rle.append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"], n.get("pi", 0)))
    efeitos.gravar(sff, pal, rle + novos, png, extras)
    # ação nova no .air: a Clsn2 padrão da ação antiga fica; a caixa de ataque vem da receita
    texto = air.read_text(encoding="utf-8")
    m = re.search(r"\[Begin Action %d\].*?(?=\n\[Begin Action|\Z)" % r["acao"], texto, re.I | re.S)
    assert m, f"ação {r['acao']} não achada"
    velha = m.group(0)
    padrao = re.search(r"Clsn2Default:[^\n]*\n(?:\s*Clsn2\[\d+\][^\n]*\n)+", velha)
    linhas = [f"[Begin Action {r['acao']}]", "; cabeçada agachada: o agachado com o tronco dobrando (dobra_agachado.py)"]
    if padrao:
        linhas.append(padrao.group(0).rstrip("\n"))
    for ang, dx, t, caixa in r["quadros"]:
        if caixa:
            linhas += ["Clsn1: 1", f" Clsn1[0] = {caixa[0]}, {caixa[1]}, {caixa[2]}, {caixa[3]}"]
        linhas.append(f"{r['grupo']},{unicos.index((ang, dx))}, 0,0, {t}")
    nova = "\n".join(linhas) + "\n"
    texto = texto[:m.start()] + nova + "\n" + texto[m.end():].lstrip("\n")
    air.write_text(texto, encoding="utf-8")
    print(f"{lut}: ação {r['acao']} com {len(r['quadros'])} elementos e {len(unicos)} desenhos no grupo {r['grupo']}")


if __name__ == "__main__":
    for nome in sys.argv[1:] or list(RECEITAS):
        fazer(RECEITAS[nome])
