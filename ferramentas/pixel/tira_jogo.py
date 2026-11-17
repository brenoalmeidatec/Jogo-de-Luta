"""Tira de cada ação como o jogo mostra: os sprites do .sff na ordem do .air (#51, conferência de anatomia com os olhos).

A régua olha as pastas de quadros; o jogo mostra o .sff, que também tem sprite montado por código, quadro do meio e
sobra de desenho antigo. Esta tira lê chars/<l>/<l>.air e .sff e desenha cada ação lado a lado, com o número da ação,
do elemento e do sprite embaixo de cada um, para achar membro sobrando, faltando ou cabeça dupla.

  python3 ferramentas/pixel/tira_jogo.py pengaro --saida /tmp/tiras            # ações do corpo (< 9000)
  python3 ferramentas/pixel/tira_jogo.py pengaro 200 210 --saida /tmp/tiras    # só essas
  python3 ferramentas/pixel/tira_jogo.py pengaro --despertado --saida ...      # com o RemapPreset do despertado
"""
import argparse
import io
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
from conferir_sff import ler  # noqa: E402

RAIZ = AQUI.parents[1]
RE_ACAO = re.compile(r"^\[Begin Action (\d+)\]", re.M | re.I)
RE_ELEM = re.compile(r"^\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)", re.M)


def acoes(air):
    partes = RE_ACAO.split(air)
    out = {}
    for k in range(1, len(partes), 2):
        corpo = re.split(r"^\s*\[", partes[k + 1], maxsplit=1, flags=re.M)[0]
        out[int(partes[k])] = [tuple(int(v) for v in m) for m in RE_ELEM.findall(corpo)]
    return out


def imagem(n, pal):
    if n.get("png"):
        return Image.open(io.BytesIO(n["px"][4:])).convert("RGBA")
    p = np.frombuffer(pal, np.uint8).reshape(-1, 4)[:, :3]
    ind = np.frombuffer(n["px"], np.uint8).reshape(n["h"], n["w"])
    a = np.zeros((n["h"], n["w"], 4), np.uint8)
    a[..., :3] = p[ind]
    a[..., 3] = np.where(ind == 0, 0, 255)
    return Image.fromarray(a)


def remap_despertado(cns):
    """{(g, i) de origem: (g, i) de destino} do [RemapPreset despertado]."""
    sys.path.insert(0, str(RAIZ / "ferramentas"))
    import gerar_pengaro as gp
    return dict(gp.trocas_do_remap(cns))


def tira(lutador, numeros=None, saida=Path("."), despertado=False, altura=220, minimo=1, maximo=8999):
    pasta = RAIZ / "chars" / lutador
    air = (pasta / f"{lutador}.air").read_text(encoding="utf-8", errors="replace")
    pal, nos, _ = ler(pasta / f"{lutador}.sff")
    sprites = {}
    for n in nos:
        sprites.setdefault((n["g"], n["i"]), n)
    troca = remap_despertado((pasta / f"{lutador}.cns").read_text(encoding="utf-8", errors="replace")) if despertado else {}
    tudo = acoes(air)
    alvo = numeros or [a for a in sorted(tudo) if minimo <= a <= maximo]
    saida.mkdir(parents=True, exist_ok=True)
    feitas, ja = [], {}
    for a in alvo:
        elems, vistos = [], set()
        for k, (g, i, x, y, t) in enumerate(tudo.get(a, [])):
            chave = troca.get((g, i), (g, i))
            if chave in vistos or chave not in sprites or g < 0:
                continue
            vistos.add(chave)
            elems.append((k, chave, x, y))
        if not elems:
            continue
        conjunto = frozenset(c for _, c, _, _ in elems)
        if conjunto in ja:  # mesma sequência de desenhos de outra ação (forte e fraco iguais): não repete
            continue
        ja[conjunto] = a
        ims = []
        for k, chave, x, y in elems:
            n = sprites[chave]
            im = imagem(n, pal)
            ims.append((k, chave, im, n["x"] - x, n["y"] - y))  # eixo do sprite + deslocamento do elemento
        # todos na mesma escala: o sprite HD (3x) e o 1x aparecem do tamanho do jogo
        topo = max(ay for *_, ay in ims)
        baixo = max(im.height - ay for _, _, im, _, ay in ims)
        h = topo + baixo
        f = altura / max(h, 1)
        celulas = []
        for k, chave, im, ax, ay in ims:
            c = Image.new("RGBA", (im.width, h), (205, 205, 210, 255))
            c.alpha_composite(im, (0, topo - ay))
            c = c.resize((max(1, round(c.width * f)), altura), Image.NEAREST)
            celulas.append((k, chave, c))
        W = sum(c.width for *_, c in celulas) + 6 * len(celulas)
        folha = Image.new("RGBA", (max(W, 200), altura + 30), (255, 255, 255, 255))
        d = ImageDraw.Draw(folha)
        x = 0
        for k, chave, c in celulas:
            folha.alpha_composite(c, (x, 18))
            d.text((x + 2, altura + 18), f"e{k} {chave[0]},{chave[1]}", fill=(0, 0, 0, 255))
            x += c.width + 6
        d.text((2, 2), f"{lutador} ação {a}" + (" (despertado)" if despertado else ""), fill=(180, 0, 0, 255))
        arq = saida / f"{lutador}{'_e' if despertado else ''}_{a:05d}.png"
        folha.convert("RGB").save(arq)
        feitas.append(arq)
    return feitas


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lutador")
    ap.add_argument("acoes", nargs="*", type=int)
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--despertado", action="store_true")
    ap.add_argument("--altura", type=int, default=220)
    ar = ap.parse_args()
    feitas = tira(ar.lutador, ar.acoes or None, ar.saida, ar.despertado, ar.altura)
    print(f"{len(feitas)} tiras em {ar.saida}")


if __name__ == "__main__":
    main()
