#!/usr/bin/env python3
"""Prova da mudança: mede pixel a pixel o antes e o depois de cada ação e monta um painel que mostra ONDE mudou.

  python3 ferramentas/antes_depois/diferenca.py LUT REF SAIDA 0 200 810 [--despertado 0 4201]

REF é o commit do "antes". Para cada ação, tick a tick (mesma tela, mesmo eixo): quantos pixels mudaram (cor ou
forma). Painel de cada ação no tick que mais mudou: ANTES | DEPOIS | DIFERENÇA (vermelho = mudou), com um retângulo
vermelho na região que mudou e o zoom 2x dessa região embaixo. Tabela em SAIDA/diferenca.md.
"""
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
import verificar_pengaro as v  # noqa: E402
import video_golpe as vg  # noqa: E402

RAIZ = AQUI.parent.parent
vg.TELA = (1000, 560)
vg.CHAO = 520
FONTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def carregar(nome, despertado):
    v.PERSONAGEM, v.PASTA = nome, RAIZ / "chars" / nome
    sprites, pal = v.ler_sff()
    if despertado:
        cns = (v.PASTA / f"{nome}.cns").read_text(encoding="utf-8")
        bloco = re.search(r"^\[RemapPreset despertado\]\n(.*?)(?=^\[)", cns, re.M | re.S)
        orig, sprites = sprites, dict(sprites)
        for g, i, g2, i2 in re.findall(r"^(\d+),\s*(\d+)\s*=\s*(\d+),\s*(\d+)", bloco.group(1), re.M):
            if (int(g2), int(i2)) in orig:
                sprites[(int(g), int(i))] = orig[(int(g2), int(i2))]
    return vg.Desenhos(sprites, pal), vg.ler_air(v.PASTA, nome)


def ticks(des, acoes, n):
    els, loop = acoes[n]
    return [np.array(vg.montar(des, els[i])[0].convert("RGB")) for i, _ in vg.ticks_da_acao(els, loop)]


def painel(a, d, titulo, info):
    dif = np.abs(a.astype(int) - d.astype(int)).sum(-1) > 40
    ys, xs = np.nonzero(dif)
    cinza = (0.3 * d.mean(-1, keepdims=True) + 40).astype(np.uint8).repeat(3, -1)
    cinza[dif] = (255, 40, 40)
    H, W = a.shape[:2]
    caixa = None
    if len(xs):
        caixa = (max(0, xs.min() - 12), max(0, ys.min() - 12), min(W, xs.max() + 12), min(H, ys.max() + 12))
    ims = []
    for img, rot in ((a, "ANTES"), (d, "DEPOIS"), (cinza, "DIFERENÇA (vermelho = mudou)")):
        im = Image.fromarray(img.copy())
        dr = ImageDraw.Draw(im)
        if caixa:
            dr.rectangle(caixa, outline=(255, 30, 30), width=4)
        dr.text((14, 10), rot, font=ImageFont.truetype(FONTE, 30), fill=(255, 255, 0) if rot == "DEPOIS" else (255, 255, 255))
        ims.append(im)
    topo = Image.new("RGB", (W * 3 + 16, H), (0, 0, 0))
    for k, im in enumerate(ims):
        topo.paste(im, (k * (W + 8), 0))
    zooms = []
    if caixa:
        cw, ch = caixa[2] - caixa[0], caixa[3] - caixa[1]
        z = min(2.0, (W * 3 // 2 - 20) / max(1, cw), 520 / max(1, ch))
        for img in (a, d):
            zooms.append(Image.fromarray(img).crop(caixa).resize((int(cw * z), int(ch * z)), Image.NEAREST))
    zh = max([z.height for z in zooms] + [0])
    out = Image.new("RGB", (topo.width, H + zh + 110), (0, 0, 0))
    out.paste(topo, (0, 0))
    for k, z in enumerate(zooms):
        x = k * (topo.width // 2) + (topo.width // 2 - z.width) // 2
        out.paste(z, (x, H + 60))
        ImageDraw.Draw(out).rectangle((x, H + 60, x + z.width - 1, H + 60 + z.height - 1), outline=(255, 30, 30), width=3)
        ImageDraw.Draw(out).text((x, H + 22), ("ANTES" if k == 0 else "DEPOIS") + " (zoom na parte que mudou)",
                                 font=ImageFont.truetype(FONTE, 26), fill=(255, 255, 255) if k == 0 else (255, 255, 0))
    ImageDraw.Draw(out).text((14, out.height - 42), f"{titulo}  |  {info}", font=ImageFont.truetype(FONTE, 28),
                             fill=(255, 255, 255))
    return out


def main():
    args = sys.argv[1:]
    lut, ref, saida = args[:3]
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    resto = args[3:]
    desp = []
    if "--despertado" in resto:
        k = resto.index("--despertado")
        resto, desp = resto[:k], resto[k + 1:]
    titulos = {}
    for t in list(resto) + list(desp):
        if "|" in t:
            pass
    antes = RAIZ / "chars" / f"{lut}antes"
    antes.mkdir(exist_ok=True)
    for e in ("air", "cns", "sff"):
        (antes / f"{lut}antes.{e}").write_bytes(subprocess.check_output(["git", "show", f"{ref}:chars/{lut}/{lut}.{e}"],
                                                                        cwd=RAIZ))
    linhas = ["| ação | ticks | ticks que mudaram | pixels mudados (média / máximo) | painel |", "|---|---|---|---|---|"]
    try:
        for lista, d in ((resto, False), (desp, True)):
            if not lista:
                continue
            da, aa = carregar(f"{lut}antes", d)
            dd, ad = carregar(lut, d)
            for item in lista:
                n, _, titulo = item.partition("|")
                n = int(n)
                ta, td = ticks(da, aa, n), ticks(dd, ad, n)
                m = min(len(ta), len(td))
                cont = [int((np.abs(ta[k].astype(int) - td[k].astype(int)).sum(-1) > 40).sum()) for k in range(m)]
                k = int(np.argmax(cont))
                mudaram = sum(c > 50 for c in cont)
                nome = f"dif_{n}{'d' if d else ''}.png"
                info = f"tick {k} de {m}: {cont[k]} pixels mudaram; {mudaram} de {m} ticks diferentes"
                painel(ta[k], td[k], (titulo or f"ação {n}") + (" (despertado)" if d else ""), info).save(saida / nome)
                linhas.append(f"| {n}{' despertado' if d else ''} {titulo} | {m} | {mudaram} | "
                              f"{int(np.mean(cont))} / {max(cont)} | {nome} |")
                print(linhas[-1])
    finally:
        for f in antes.iterdir():
            f.unlink()
        antes.rmdir()
    (saida / "diferenca.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
