"""Encolhe o .sff de um lutador sem mudar o que aparece no jogo (pedido do coordenador, 17/11: gutto.sff em 87 MB,
raiclaven.sff em 82 MB, perto do limite de 100 MB do GitHub).

    python ferramentas/encolher_sff.py <lutador> [--indexar 49000-49099 ...] [--sem-podar] [--so-medir]

Rode por último, depois de ligar_pecas.py, aura_silhueta.py e luz.py (todos leem e regravam o .sff e mantêm o que esta
ferramenta fez: links, paletas a mais e o índice de paleta de cada sprite).

O que faz, nesta ordem:
  1. PODA   tira os desenhos que nada desenha: fica todo elemento do .air, o grupo 9000 (retratos), os
            SPRITES_VITIMA (o corpo do lutador nos agarrões dos outros) e o destino de toda troca de RemapPreset cuja
            origem fica. Os desenhos velhos que o boneco de peças substituiu saem aqui.
  2. INDEX  os grupos de --indexar (desenhos PNG RGBA do corpo firme, alfa só 0 ou 255) viram RLE de 8 bits numa paleta
            própria de 255 cores (corte pela mediana em cima de todos eles), uma paleta a mais no .sff com pi = 2 + n.
            É o método da thread do Raiclaven despertado (kit_raiclaven.paleta_pecas/indexar, 20 MB -> 6 MB sem
            diferença visível). A paleta fica em sprites/<lutador>/paleta_<grupo>.bin: na rodada seguinte a antiga é
            trocada em vez de empilhar outra. Desenho com alfa parcial (aura, luz, faísca) nunca é indexado.
  3. PNG    o resto dos PNG é recomprimido pelo Pillow (filtros adaptativos, sem perda: os pixels saem idênticos; o
            png_rgba antigo usava só o filtro 0) e PNG repetido vira link, como já acontecia com o RLE.

A ferramenta confere no fim: relê o .sff novo e compara cada desenho que ficou com o antigo (PNG e RLE pixel a pixel;
os indexados pela diferença de cor, que só aparece no resumo).
"""
import argparse
import io
import re
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conferir_sff as cs  # noqa: E402
import efeitos  # noqa: E402
import gerar_pengaro as gp  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
RE_REMAP = re.compile(r"^\s*(\d+)\s*,\s*(\d+)\s*=\s*(\d+)\s*,\s*(\d+)", re.M)


# ---------------------------------------------------------------- 1. poda
def trocas_de_remap(cns):
    """Pares (origem, destino) de todo [RemapPreset ...] do .cns."""
    out = []
    for bloco in re.finditer(r"^\[RemapPreset[^\]]*\]\n(.*?)(?=^\[|\Z)", cns, re.M | re.S | re.I):
        out += [((int(a), int(b)), (int(c), int(d))) for a, b, c, d in RE_REMAP.findall(bloco.group(1))]
    return out


def mantidos(air, cns):
    usados = {(int(g), int(i)) for g, i in gp.RE_ELEMENTO.findall(air)} | set(gp.SPRITES_VITIMA)
    trocas = trocas_de_remap(cns)
    while True:   # remap de remap (raro) também fica
        novos = {d for o, d in trocas if o in usados} - usados
        if not novos:
            return usados
        usados |= novos


# ---------------------------------------------------------------- 2. paleta própria
def paleta_de(quadros):
    """255 cores pelo corte da mediana em cima de todos os desenhos + o 0 transparente (kit_raiclaven.paleta_pecas)."""
    amostra = np.concatenate([q[q[..., 3] > 0][::3, :3] for q in quadros])
    lado = int(np.ceil(np.sqrt(len(amostra))))
    tira = np.zeros((lado * lado, 3), np.uint8)
    tira[:len(amostra)] = amostra
    tira[len(amostra):] = amostra[0]
    q = Image.fromarray(tira.reshape(lado, lado, 3)).quantize(255, method=Image.Quantize.MEDIANCUT,
                                                               dither=Image.Dither.NONE)
    cores = np.array(q.getpalette()[:255 * 3], np.uint8).reshape(-1, 3)
    pal = np.zeros((256, 4), np.uint8)
    pal[1:1 + len(cores), :3] = cores
    pal[1:, 3] = 255
    return pal


def indexar(rgba, pal):
    """Índices na paleta (cor mais próxima, sem pontilhado); transparente = 0 (kit_raiclaven.indexar)."""
    al = rgba[..., 3] > 0
    px = rgba[al][:, :3].astype(np.int32)
    cores = pal[1:, :3].astype(np.int32)
    idx = np.empty(len(px), np.uint8)
    for i in range(0, len(px), 20000):
        d = ((px[i:i + 20000, None, :] - cores[None]) ** 2).sum(-1)
        idx[i:i + 20000] = d.argmin(1) + 1
    out = np.zeros(rgba.shape[:2], np.uint8)
    out[al] = idx
    return out


# ---------------------------------------------------------------- 3. PNG
def rgba_do_no(n):
    cru = n["px"][n["px"].index(b"\x89PNG"):]
    return np.asarray(Image.open(io.BytesIO(cru)).convert("RGBA"))


def png_menor(a, atual=None):
    """O menor entre o PNG que já está no .sff e o do Pillow (filtros adaptativos). Na aura e na luz (alfa parcial,
    poucas cores) o filtro 0 do png_rgba sai menor; no desenho pintado, o Pillow. Os pixels são os mesmos."""
    o = io.BytesIO()
    Image.fromarray(a, "RGBA").save(o, "PNG", optimize=True)
    novo = struct.pack("<I", a.shape[0] * a.shape[1] * 4) + o.getvalue()
    return atual if atual is not None and len(atual) <= len(novo) else novo


def faixa(txt):
    a, _, b = txt.partition("-")
    return int(a), int(b or a)


def encolher(lutador, indexar_grupos=(), podar=True, so_medir=False):
    sff = RAIZ / "chars" / lutador / f"{lutador}.sff"
    air = (RAIZ / "chars" / lutador / f"{lutador}.air").read_text(encoding="utf-8", errors="ignore")
    cns = (RAIZ / "chars" / lutador / f"{lutador}.cns").read_text(encoding="utf-8", errors="ignore")
    antes = sff.stat().st_size
    pal, nos, _ = cs.ler(sff)
    extras = list(cs.EXTRAS.get(str(sff.resolve()), []))
    manter = mantidos(air, cns) if podar else None
    vistos, ficam = set(), []
    for n in nos:
        k = (n["g"], n["i"])
        if k in vistos:
            continue
        vistos.add(k)
        if manter is None or n["g"] == 9000 or k in manter:
            ficam.append(n)
    podados = len(vistos) - len(ficam)

    rle, png, resumo = [], [], {"podados": podados}
    a_indexar = []
    for n in ficam:
        if n.get("png"):
            a = rgba_do_no(n)
            binario = not ((a[..., 3] > 0) & (a[..., 3] < 255)).any()
            if binario and any(g0 <= n["g"] <= g1 for g0, g1 in indexar_grupos):
                a_indexar.append((n, a))
            else:
                png.append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], png_menor(a, n["px"]), a))
        else:
            rle.append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"], n.get("pi", 0)))

    # uma paleta por faixa de --indexar; a da rodada anterior (sprites/<l>/paleta_<g0>.bin) sai do .sff
    erro_cor = []
    for g0, g1 in indexar_grupos:
        lote = [(n, a) for n, a in a_indexar if g0 <= n["g"] <= g1]
        guardada = RAIZ / "sprites" / lutador / f"paleta_{g0}.bin"
        if guardada.exists() and guardada.read_bytes() in extras:
            j = extras.index(guardada.read_bytes())
            velha = np.frombuffer(extras[j], np.uint8).reshape(256, 4)
            # o que já estava nessa paleta volta a RGBA e entra no lote (senão ficaria apontando para paleta nenhuma)
            ficam = []
            for r in rle:
                if r[7] == 2 + j:
                    idx = np.frombuffer(r[6], np.uint8).reshape(r[3], r[2])
                    a = velha[idx].copy()
                    a[..., 3] = np.where(idx > 0, 255, 0)
                    lote.append((dict(g=r[0], i=r[1], x=r[4], y=r[5]), a))
                else:
                    ficam.append(r)
            if not lote:
                continue
            extras.pop(j)
            rle = [r[:7] + ((r[7] - 1 if r[7] > 2 + j else r[7]),) for r in ficam]
        if not lote:
            continue
        nova = paleta_de([a for _, a in lote])
        extras.append(nova.tobytes())
        pi = 2 + len(extras) - 1
        for n, a in lote:
            px = indexar(a, nova)
            volta = nova[px][..., :3].astype(int)
            al = a[..., 3] > 0
            erro_cor.append(np.abs(volta[al] - a[..., :3][al].astype(int)).mean() if al.any() else 0.0)
            rle.append((n["g"], n["i"], a.shape[1], a.shape[0], n["x"], n["y"], px.tobytes(), pi))
        if not so_medir:
            guardada.parent.mkdir(parents=True, exist_ok=True)
            guardada.write_bytes(nova.tobytes())
    resumo["indexados"] = len(a_indexar)
    resumo["erro_cor_medio"] = round(float(np.mean(erro_cor)), 2) if erro_cor else 0.0

    destino = sff if not so_medir else Path("/tmp") / f"{lutador}_encolhido.sff"
    efeitos.gravar(destino, pal, rle, [p[:7] for p in png], extras)
    depois = destino.stat().st_size

    # confere: todo desenho que ficou sai igual (PNG e RLE pixel a pixel)
    _, novos, _ = cs.ler(destino)
    por_chave = {(m["g"], m["i"]): m for m in novos}
    ruins = 0
    for g, i, w, h, x, y, _blob, a in png:
        m = por_chave[(g, i)]
        if not m.get("png") or not np.array_equal(rgba_do_no(m), a) or (m["x"], m["y"]) != (x, y):
            ruins += 1
    for g, i, w, h, x, y, px, pi in rle:
        m = por_chave[(g, i)]
        if m["px"] != px or (m["x"], m["y"]) != (x, y):
            ruins += 1
    resumo.update(antes_mb=round(antes / 1e6, 1), depois_mb=round(depois / 1e6, 1), sprites=len(novos),
                  diferentes=ruins, arquivo=str(destino))
    return resumo


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("lutador")
    ap.add_argument("--indexar", action="append", default=[], help="faixa de grupos PNG do corpo firme, ex. 49000-49099")
    ap.add_argument("--sem-podar", action="store_true")
    ap.add_argument("--so-medir", action="store_true", help="grava em /tmp e não mexe no .sff do lutador")
    a = ap.parse_args()
    r = encolher(a.lutador, [faixa(t) for t in a.indexar], podar=not a.sem_podar, so_medir=a.so_medir)
    print(r)
    if r["diferentes"]:
        sys.exit(f"ERRO: {r['diferentes']} desenhos saíram diferentes")


if __name__ == "__main__":
    main()
