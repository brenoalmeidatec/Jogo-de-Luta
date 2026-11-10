#!/usr/bin/env python3
"""Prova de que os pixels mostrados de um .sff não mudaram (SFF v2, formato 2 = RLE8, como o escrever_sff grava).

  python ferramentas/conferir_sff.py gravar chars/pengaro/pengaro.sff base_pengaro.json
  python ferramentas/conferir_sff.py comparar base_pengaro.json novo_pengaro.json [--podado]

`gravar` lê o .sff seguindo os sprites linkados (len = 0: os pixels e o tamanho vêm do sprite `link`, como o
shareCopy do IKEMEN faz) e grava, para cada (grupo, índice), o sha1 de largura, altura, eixo e pixels, mais o sha1
da paleta. `comparar` falha (código 1) se a paleta ou qualquer sprite mudou, se sumiu um sprite ou se apareceu um.
Com --podado, sprite que sumiu é permitido (item de poda), mas todo sprite que ficou tem que ser igual.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path


def unrle8(d, n):
    out = bytearray()
    i = 0
    while i < len(d) and len(out) < n:
        b = d[i]
        i += 1
        if (b & 0xC0) == 0x40:
            out += bytes((d[i],)) * (b & 0x3F)
            i += 1
        else:
            out.append(b)
    return bytes(out)


def ler(caminho):
    """Lista de nós na ordem do arquivo: dict(g, i, w, h, x, y, link, px). Link é resolvido para os pixels."""
    b = Path(caminho).read_bytes()
    assert b[:12] == b"ElecbyteSpr\x00" and list(b[12:16]) == [0, 1, 0, 2], f"{caminho}: não é SFF v2.01"
    ofs_spr, nspr, ofs_pal, npal, ofs_l, len_l, ofs_t, len_t = struct.unpack_from("<8I", b, 36)
    pg, pn, pc, plink, poff, plen = struct.unpack_from("<HHHHII", b, ofs_pal)
    pal = b[ofs_l + poff:ofs_l + poff + plen]
    nos = []
    for k in range(nspr):
        g, i, w, h, x, y, link, fmt, dep, off, ln, pi, fl = struct.unpack_from("<HHHHhhHBBIIHH", b, ofs_spr + 28 * k)
        if ln == 0:
            assert link < k, f"{caminho}: sprite {g},{i} linka para frente ({link} >= {k})"
            src = nos[link]
            nos.append(dict(g=g, i=i, w=src["w"], h=src["h"], x=x, y=y, link=link, px=src["px"], hw=(w, h)))
            continue
        assert fmt == 2 and dep == 8, f"{caminho}: formato do sprite {g},{i}"
        base = ofs_l if fl == 0 else ofs_t
        raw = b[base + off:base + off + ln]
        n = struct.unpack_from("<I", raw, 0)[0]
        assert n == w * h, f"{caminho}: tamanho do sprite {g},{i}"
        px = unrle8(raw[4:], n)
        assert len(px) == n, f"{caminho}: RLE do sprite {g},{i}"
        nos.append(dict(g=g, i=i, w=w, h=h, x=x, y=y, link=None, px=px, hw=(w, h)))
    return pal, nos, len(b)


def resumo(caminho):
    pal, nos, tamanho = ler(caminho)
    sprites = {}
    for n in nos:
        chave = f"{n['g']},{n['i']}"
        if chave in sprites:
            continue  # o motor usa o primeiro nó de cada (grupo, índice)
        h = hashlib.sha1(struct.pack("<HHhh", n["w"], n["h"], n["x"], n["y"]) + n["px"]).hexdigest()
        sprites[chave] = h
    return dict(arquivo=str(caminho), bytes=tamanho, nos=len(nos), linkados=sum(n["link"] is not None for n in nos),
                pixels_textura=sum(n["w"] * n["h"] for n in nos if n["link"] is None),
                paleta=hashlib.sha1(pal).hexdigest(), sprites=sprites)


def comparar(a, b, podado=False):
    erros = []
    if a["paleta"] != b["paleta"]:
        erros.append("paleta mudou")
    for k, h in a["sprites"].items():
        if k not in b["sprites"]:
            if not podado:
                erros.append(f"sumiu {k}")
        elif b["sprites"][k] != h:
            erros.append(f"mudou {k}")
    for k in b["sprites"]:
        if k not in a["sprites"]:
            erros.append(f"apareceu {k}")
    return erros


def main():
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == "gravar":
        r = resumo(args[1])
        Path(args[2]).write_text(json.dumps(r, indent=0, sort_keys=True), encoding="utf-8")
        print(f"{args[1]}: {r['bytes'] / 1e6:.2f} MB, {r['nos']} nós ({r['linkados']} linkados), "
              f"{len(r['sprites'])} sprites, {r['pixels_textura'] / 1e6:.2f} Mpx de textura")
    elif len(args) >= 3 and args[0] == "comparar":
        a = json.loads(Path(args[1]).read_text(encoding="utf-8"))
        b = json.loads(Path(args[2]).read_text(encoding="utf-8"))
        erros = comparar(a, b, "--podado" in args)
        mantidos = len(set(a["sprites"]) & set(b["sprites"]))
        print(f"{Path(args[1]).name} -> {Path(args[2]).name}: {a['nos']} -> {b['nos']} nós, "
              f"{a['bytes'] / 1e6:.2f} -> {b['bytes'] / 1e6:.2f} MB, {mantidos} sprites conferidos, "
              f"{len(erros)} diferenças")
        for e in erros[:20]:
            print("  " + e)
        sys.exit(1 if erros else 0)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
