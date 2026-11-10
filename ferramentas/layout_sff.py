"""SFF v2 (v2.01) com sprites PNG de 32 bits (formato 12) e zero paletas, para o IKEMEN GO v1.0.0.

E o formato de todos os SFF oficiais do v1.0.0 (system.sff, fight.sff, fontes). Usado pelo layout Nazafights
(motif/nazafight). Para lutador continua valendo o escritor SFF v1 de cada gerar_<lutador>.py.

Layout (conferido no image.go readV2 do v1.0.0 e aceito pelo motor):
  cabecalho de 512 B: "ElecbyteSpr\\0", versao 00 01 00 02, 0x02000100 em @24;
  em @36 sete uint32: ofs_nos, n_sprites, ofs_paletas, n_paletas (0), ldata_ofs, ldata_len, tdata_ofs; @64 tdata_len;
  no de sprite de 28 B "<HHHHhhHBBIIHH": grupo, numero, w, h, eixo_x, eixo_y, link, formato=12, depth=32,
  ofs (relativo a ldata), tamanho, palidx=0, flags=0;
  dado de cada sprite = uint32 LE com o tamanho descomprimido + PNG (o motor faz Seek(ofs + 4)).
"""
import struct
import zlib
from pathlib import Path

ASSINATURA = b"ElecbyteSpr\x00"


def png_rgba(w, h, pix):
    """PNG 8 bits/canal, tipo de cor 6 (RGBA), filtro 0 em toda linha. Deterministico."""
    linha = w * 4
    raw = b"".join(b"\x00" + pix[y * linha:(y + 1) * linha] for y in range(h))

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def escrever_sff2(caminho, sprites):
    """sprites: lista de (grupo, numero, imagem_PIL_RGBA, eixo_x, eixo_y). Grupo/numero repetido e erro."""
    vistos = set()
    nos, dados = bytearray(), bytearray()
    for (g, n, img, ax, ay) in sprites:
        if (g, n) in vistos:
            raise ValueError(f"sprite repetido {g},{n} em {caminho}")
        vistos.add((g, n))
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        w, h = img.size
        blob = struct.pack("<I", w * h * 4) + png_rgba(w, h, img.tobytes())
        nos += struct.pack("<HHHHhhHBBIIHH", g, n, w, h, ax, ay, 0, 12, 32, len(dados), len(blob), 0, 0)
        dados += blob
    qtd = len(sprites)
    nos_ofs = 512
    ldata_ofs = nos_ofs + 28 * qtd
    cab = bytearray(512)
    cab[0:12] = ASSINATURA
    cab[12:16] = bytes([0, 1, 0, 2])
    struct.pack_into("<I", cab, 24, 0x02000100)
    struct.pack_into("<7I", cab, 36, nos_ofs, qtd, nos_ofs, 0, ldata_ofs, len(dados), ldata_ofs + len(dados))
    struct.pack_into("<I", cab, 64, 0)
    Path(caminho).write_bytes(bytes(cab) + bytes(nos) + bytes(dados))


def ler_sff2(caminho):
    """Le de volta um SFF v2 escrito acima (ou qualquer v2 com PNG). Devolve {(g, n): (w, h, ax, ay, fmt, png)}.
    Levanta ValueError se o cabecalho, a contagem ou algum no estiver errado."""
    b = Path(caminho).read_bytes()
    if b[:12] != ASSINATURA:
        raise ValueError(f"{caminho}: assinatura errada")
    if b[12:16] != bytes([0, 1, 0, 2]):
        raise ValueError(f"{caminho}: versao {list(b[12:16])} (esperado 0 1 0 2)")
    nos_ofs, qtd, _pal_ofs, n_pal, ldata_ofs, ldata_len, _tdata_ofs = struct.unpack_from("<7I", b, 36)
    if n_pal != 0:
        raise ValueError(f"{caminho}: {n_pal} paletas (esperado 0)")
    if ldata_ofs + ldata_len != len(b):
        raise ValueError(f"{caminho}: tamanho {len(b)} nao bate com ldata {ldata_ofs}+{ldata_len}")
    out = {}
    for k in range(qtd):
        g, n, w, h, ax, ay, _link, fmt, depth, ofs, tam, _pal, _fl = struct.unpack_from(
            "<HHHHhhHBBIIHH", b, nos_ofs + 28 * k)
        if (g, n) in out:
            raise ValueError(f"{caminho}: sprite {g},{n} repetido")
        if fmt != 12 or depth != 32:
            raise ValueError(f"{caminho}: sprite {g},{n} formato {fmt}/{depth}")
        blob = b[ldata_ofs + ofs: ldata_ofs + ofs + tam]
        (descomp,) = struct.unpack_from("<I", blob, 0)
        if descomp != w * h * 4:
            raise ValueError(f"{caminho}: sprite {g},{n} tamanho descomprimido {descomp} != {w * h * 4}")
        out[(g, n)] = (w, h, ax, ay, fmt, blob[4:])
    return out
