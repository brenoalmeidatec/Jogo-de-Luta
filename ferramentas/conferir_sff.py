#!/usr/bin/env python3
"""Prova de que os pixels mostrados de um .sff não mudaram (SFF v2, formato 2 = RLE8, como o escrever_sff grava).

  python ferramentas/conferir_sff.py gravar chars/pengaro/pengaro.sff base_pengaro.json
  python ferramentas/conferir_sff.py comparar base_pengaro.json novo_pengaro.json [--podado]
  python ferramentas/conferir_sff.py religar velho.sff novo.sff   (regrava com links, sem requantizar)
  python ferramentas/conferir_sff.py religar velho.sff novo.sff --podar chars/pengaro   (e poda como o gerador)
  python ferramentas/conferir_sff.py paleta chars/ck/ck.sff sprites/ck/paleta_sff.act   (a paleta fixa do gerador)
  python ferramentas/conferir_sff.py transplantar base.sff chars/gutto   (só o despertado vem do gerado)

`transplantar` existe porque os quadros_hd do Gutto e do Raiclaven (hd_blender.py, fora do git) não saem iguais em
outra máquina: o Blender daqui desenha diferente do Blender do Breno, e regenerar o lutador mudaria a forma base
inteira. Com a paleta fixa (a mesma do base.sff), ele regrava chars/<l>/<l>.sff com o nó do base.sff em todo sprite que
existe lá, menos os destinos do [RemapPreset despertado], que vêm do .sff que o gerador acabou de gravar.

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
    # paletas a mais (grupo 2: a paleta própria do despertado, gerar_pengaro.escrever_sff), na ordem do arquivo
    extras = []
    for j in range(2, npal):
        _, _, _, _, eoff, elen = struct.unpack_from("<HHHHII", b, ofs_pal + 16 * j)
        extras.append(b[ofs_l + eoff:ofs_l + eoff + elen])
    EXTRAS[str(caminho)] = extras
    nos = []
    for k in range(nspr):
        g, i, w, h, x, y, link, fmt, dep, off, ln, pi, fl = struct.unpack_from("<HHHHhhHBBIIHH", b, ofs_spr + 28 * k)
        if ln == 0:
            assert link < k, f"{caminho}: sprite {g},{i} linka para frente ({link} >= {k})"
            src = nos[link]
            nos.append(dict(g=g, i=i, w=src["w"], h=src["h"], x=x, y=y, link=link, px=src["px"], hw=(w, h), pi=pi))
            continue
        base = ofs_l if fl == 0 else ofs_t
        raw = b[base + off:base + off + ln]
        if fmt in (10, 11, 12) and g == 9000:
            # retrato em PNG (trocar_retratos.py, fora da paleta): px guarda o PNG cru, png=True
            nos.append(dict(g=g, i=i, w=w, h=h, x=x, y=y, link=None, px=raw, hw=(w, h), png=True))
            continue
        assert fmt == 2 and dep == 8, f"{caminho}: formato do sprite {g},{i}"
        n = struct.unpack_from("<I", raw, 0)[0]
        assert n == w * h, f"{caminho}: tamanho do sprite {g},{i}"
        px = unrle8(raw[4:], n)
        assert len(px) == n, f"{caminho}: RLE do sprite {g},{i}"
        nos.append(dict(g=g, i=i, w=w, h=h, x=x, y=y, link=None, px=px, hw=(w, h), pi=pi))
    return pal, nos, len(b)


EXTRAS = {}  # caminho -> paletas a mais do último ler()


def _item(n):
    return (n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]) + ((n["pi"],) if n.get("pi") else ())


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


def religar(origem, destino, manter=None):
    """Regrava um .sff já gerado com o mesmo gravar_sff do gerador (duplicata vira link), sem requantizar: paleta
    e pixels saem idênticos. Com `manter`, só os (grupo, índice) do conjunto ficam."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import gerar_pengaro as gp
    pal, nos, _ = ler(origem)
    itens = [_item(n) for n in nos if manter is None or n["g"] == 9000 or (n["g"], n["i"]) in manter]
    gp.gravar_sff(Path(destino), pal, itens, EXTRAS[str(origem)])


def paleta(origem, destino):
    """Grava a paleta do .sff como .act (768 bytes RGB, o índice 0 é o transparente): a paleta fixa do gerador."""
    pal, _, _ = ler(origem)
    Path(destino).write_bytes(b"".join(pal[k:k + 3] for k in range(0, 256 * 4, 4)))


def transplantar(base, pasta):
    """Regrava chars/<l>/<l>.sff (o que o gerador gravou) com o nó de `base` em todo sprite que existe lá, menos o
    despertado (destinos do [RemapPreset despertado] do .cns). A paleta tem que ser a mesma (paleta_sff.act)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import gerar_pengaro as gp
    pasta = Path(pasta)
    novo = pasta / f"{pasta.name}.sff"
    pal_b, nos_b, _ = ler(base)
    pal_n, nos_n, _ = ler(novo)
    assert pal_b == pal_n, "paleta diferente: grave sprites/<l>/paleta_sff.act da base e gere o lutador de novo"
    desp = {d for _, d in gp.trocas_do_remap((pasta / f"{pasta.name}.cns").read_text(encoding="utf-8"))}
    da_base = {(n["g"], n["i"]): n for n in nos_b}
    itens, trocados = [], 0
    for n in nos_n:
        k = (n["g"], n["i"])
        if k in da_base and k not in desp and not da_base[k].get("png"):  # retrato PNG: o trocar_retratos.py repõe
            trocados += (n["w"], n["h"], n["x"], n["y"], n["px"]) != tuple(da_base[k][c] for c in "whxy") + (da_base[k]["px"],)
            n = da_base[k]
        itens.append(_item(n))
    gp.gravar_sff(novo, pal_n, itens, EXTRAS[str(novo)])
    print(f"{novo}: {len(itens)} sprites, {sum(k in desp for k in (tuple(i[:2]) for i in itens))} do despertado "
          f"(do gerador), {sum(1 for i in itens if tuple(i[:2]) in da_base and tuple(i[:2]) not in desp)} da base "
          f"({trocados} diferiam do gerado), {sum(1 for i in itens if tuple(i[:2]) not in da_base)} novos"
          + ("; retratos em PNG na base: rode python ferramentas/trocar_retratos.py " + pasta.name
             if any(n.get("png") for n in nos_b) else ""))


def main():
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == "gravar":
        r = resumo(args[1])
        Path(args[2]).write_text(json.dumps(r, indent=0, sort_keys=True), encoding="utf-8")
        print(f"{args[1]}: {r['bytes'] / 1e6:.2f} MB, {r['nos']} nós ({r['linkados']} linkados), "
              f"{len(r['sprites'])} sprites, {r['pixels_textura'] / 1e6:.2f} Mpx de textura")
    elif len(args) in (3, 5) and args[0] == "religar":
        manter = None
        if len(args) == 5 and args[3] == "--podar":
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import gerar_pengaro as gp
            pasta = Path(args[4])
            manter = gp.sprites_mantidos((pasta / f"{pasta.name}.air").read_text(encoding="utf-8"),
                                         (pasta / f"{pasta.name}.cns").read_text(encoding="utf-8"))
        religar(args[1], args[2], manter)
    elif len(args) == 3 and args[0] == "paleta":
        paleta(args[1], args[2])
    elif len(args) == 3 and args[0] == "transplantar":
        transplantar(args[1], args[2])
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
