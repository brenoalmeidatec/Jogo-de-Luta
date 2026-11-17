"""Tira um sprite do .sff do jogo para PNG e põe de volta depois de consertado (#51, anatomia).

Serve para o Gutto e o Raiclaven, cujo corpo no jogo é o HD do Blender (quadros_hd, fora do git): o conserto é feito
no próprio sprite do jogo. O sprite volta com o mesmo tamanho e o mesmo eixo, na paleta fixa do .sff (ou em PNG de 32
bits, se ele já era assim). Todo nó que linkava para ele passa a mostrar o novo.

  python3 ferramentas/pixel/sprite_sff.py extrair gutto 467,0 /tmp/s467.png
  python3 ferramentas/pixel/sprite_sff.py repor   gutto 467,0 /tmp/s467.png
  python3 ferramentas/pixel/sprite_sff.py tapar   gutto ANTES.sff   # devolve contorno que virou buraco num remendo
"""
import io
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))
from conferir_sff import ler  # noqa: E402
from gerar_pengaro import rle8  # noqa: E402
from remendar_sff import indices_de, compactar  # noqa: E402
from tira_jogo import imagem  # noqa: E402

RAIZ = AQUI.parents[1]


def achar(lutador, chave):
    alvo = RAIZ / "chars" / lutador / f"{lutador}.sff"
    pal, nos, _ = ler(alvo)
    g, i = (int(v) for v in chave.split(","))
    for k, n in enumerate(nos):
        if (n["g"], n["i"]) == (g, i):
            while n["link"] is not None:  # o pixel mora no nó de origem
                k = n["link"]
                n = nos[k]
            return alvo, pal, nos, k, n
    raise SystemExit(f"{lutador}: sprite {chave} não existe")


def extrair(lutador, chave, saida):
    _, pal, _, _, n = achar(lutador, chave)
    imagem(n, pal).save(saida)
    print(f"{saida}: {n['w']}x{n['h']}, eixo {n['x']},{n['y']}")


def gravar_corpos(alvo, corpos):
    """{índice do nó: corpo (tamanho descomprimido + dado)}: o dado novo vai no fim (tdata, flag 1) e o arquivo é
    compactado uma vez só."""
    b = bytearray(alvo.read_bytes())
    ofs_spr, nspr, ofs_pal, npal, ofs_l, len_l, ofs_t, len_t = struct.unpack_from("<8I", b, 36)
    assert ofs_t + len_t == len(b)
    novos = bytearray()
    for k, corpo in corpos.items():
        campos = list(struct.unpack_from("<HHHHhhHBBIIHH", b, ofs_spr + 28 * k))
        campos[9], campos[10], campos[12] = len_t + len(novos), len(corpo), campos[12] | 1
        struct.pack_into("<HHHHhhHBBIIHH", b, ofs_spr + 28 * k, *campos)
        novos += corpo
    struct.pack_into("<I", b, 36 + 28, len_t + len(novos))
    alvo.write_bytes(compactar(bytes(b) + bytes(novos)))


def repor(lutador, chave, entrada):
    alvo, pal, nos, k, n = achar(lutador, chave)
    a = np.array(Image.open(entrada).convert("RGBA"))
    assert a.shape[:2] == (n["h"], n["w"]), f"o PNG tem que ter {n['w']}x{n['h']} (o tamanho do sprite)"
    if n.get("png"):
        buf = io.BytesIO()
        Image.fromarray(a).save(buf, "PNG", optimize=True)
        corpo = struct.pack("<I", n["w"] * n["h"] * 4) + buf.getvalue()
    else:
        px = indices_de(a, pal)
        corpo = struct.pack("<I", len(px)) + rle8(px)
    gravar_corpos(alvo, {k: corpo})
    print(f"{alvo}: sprite {chave} trocado (nó {k})")


def tapar(lutador, antes):
    """Devolve os pixels que eram opacos no .sff ANTES e viraram transparentes no .sff do jogo, com o índice de antes.
    Conserta o buraco no contorno que o indices_de antigo abria (quase preto caía no índice 0) nos sprites do remendo
    de cor da #51. Só mexe em sprite indexado de mesmo tamanho; o resto fica."""
    alvo = RAIZ / "chars" / lutador / f"{lutador}.sff"
    _, A, _ = ler(Path(antes))
    _, C, _ = ler(alvo)
    dA = {(n["g"], n["i"]): n for n in A}
    corpos, pix = {}, 0
    for k, n in enumerate(C):
        m = dA.get((n["g"], n["i"]))
        if n["link"] is not None or m is None or n.get("png") or m.get("png") or (m["w"], m["h"]) != (n["w"], n["h"]):
            continue
        a, c = np.frombuffer(m["px"], np.uint8), np.frombuffer(n["px"], np.uint8)
        buraco = (a > 0) & (c == 0)
        if buraco.any():
            px = np.where(buraco, a, c).astype(np.uint8).tobytes()
            corpos[k] = struct.pack("<I", len(px)) + rle8(px)
            pix += int(buraco.sum())
    if corpos:
        gravar_corpos(alvo, corpos)
    print(f"{alvo}: {len(corpos)} sprites tapados, {pix} pixels devolvidos")


if __name__ == "__main__":
    if sys.argv[1] == "tapar":
        tapar(sys.argv[2], sys.argv[3])
    else:
        cmd, lutador, chave, arq = sys.argv[1:5]
        {"extrair": extrair, "repor": repor}[cmd](lutador, chave, arq)
