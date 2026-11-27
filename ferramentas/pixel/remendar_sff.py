"""Troca no .sff do jogo só os sprites de quadros que tiveram a cor consertada (#51, cor mudando entre os quadros).

Por que não gerar o lutador de novo: o `gerar_<l>.py` sozinho não refaz os pós-passos que já estão em chars/<l>/
(aura colada, sons, despertados...) e, no Gutto e no Raiclaven, o corpo do jogo é o HD do Blender (quadros_hd, fora do
git), que sai diferente em cada máquina. Então este remendo mexe só nos pixels dos sprites certos e deixa o resto do
.sff (e o .air, o .cns, as caixas e o tempo) como está.

Como acha os sprites: o lutador é gerado duas vezes nesta máquina, com os quadros de antes (A.sff) e com os
consertados (B.sff). O (grupo, índice) cujo desenho mudou entre A e B é sprite de quadro consertado. No .sff do jogo:
  - se o sprite é igual ao de A (Pengaró: o HD está no git), entra o de B, igual ao que o gerador gravaria;
  - se não é (Gutto: HD do Blender), o próprio sprite do jogo passa pelo mesmo conserto de tom (cores.RefCor.corrigir,
    com o parado da forma que der menos deriva) e volta para a paleta fixa do .sff.
O dado novo vai no fim do arquivo (tdata, flag 1); o nó aponta para ele. Paleta, eixos, tamanhos e links ficam.

  python3 ferramentas/pixel/remendar_sff.py gutto A.sff B.sff [--forca 1.0]
"""
import argparse
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
from cores import RefCor  # noqa: E402
from quadros import Endereco, PARADO, RAIZ  # noqa: E402


def rgba_de(n, pal):
    p = np.frombuffer(pal, np.uint8).reshape(-1, 4)[:, :3]
    ind = np.frombuffer(n["px"], np.uint8).reshape(n["h"], n["w"])
    out = np.zeros((n["h"], n["w"], 4), np.uint8)
    out[..., :3] = p[ind]
    out[..., 3] = np.where(ind == 0, 0, 255)
    return out


def indices_de(a, pal):
    """Como o escrever_sff do gerador: quantize na paleta fixa (sem o índice 0) e +1; alfa vazio vira 0."""
    rgb = np.frombuffer(pal, np.uint8).reshape(-1, 4)[1:256, :3].reshape(-1).tolist()
    q = Image.new("P", (1, 1))
    # 255 cores + 1 de enchimento: o enchimento repete a 1ª cor (com preto, o quase preto do contorno caía no índice
    # 255 -> +1 = 256 -> 0 = transparente e o contorno virava buraco)
    q.putpalette(rgb + rgb[:3] * ((768 - len(rgb)) // 3))
    ind = np.asarray(Image.fromarray(a[..., :3]).quantize(palette=q, dither=Image.NONE)).astype(np.uint16)
    ind = np.where(ind >= len(rgb) // 3, 0, ind) + 1
    return np.where(a[..., 3] < 128, 0, ind).astype(np.uint8).tobytes()


def compactar(b):
    """Regrava ldata e tdata só com o que os nós (paletas e sprites) ainda apontam: o remendo deixa o dado velho para
    trás. Mesmo conteúdo, mesmos nós; só os deslocamentos mudam."""
    ofs_spr, nspr, ofs_pal, npal, ofs_l, len_l, ofs_t, len_t = struct.unpack_from("<8I", b, 36)
    b = bytearray(b)
    ld, td = bytearray(), bytearray()
    vistos = {}
    for k in range(npal):
        g, n, c, link, off, ln = struct.unpack_from("<HHHHII", b, ofs_pal + 16 * k)
        if ln:
            chave = (0, off, ln)
            if chave not in vistos:
                vistos[chave] = len(ld)
                ld += b[ofs_l + off:ofs_l + off + ln]
            struct.pack_into("<HHHHII", b, ofs_pal + 16 * k, g, n, c, link, vistos[chave], ln)
    for k in range(nspr):
        campos = list(struct.unpack_from("<HHHHhhHBBIIHH", b, ofs_spr + 28 * k))
        off, ln, fl = campos[9], campos[10], campos[12]
        if not ln:
            continue
        t = fl & 1
        chave = (1 + t, off, ln)
        if chave not in vistos:
            dest = td if t else ld
            vistos[chave] = len(dest)
            dest += b[(ofs_t if t else ofs_l) + off:(ofs_t if t else ofs_l) + off + ln]
        campos[9] = vistos[chave]
        struct.pack_into("<HHHHhhHBBIIHH", b, ofs_spr + 28 * k, *campos)
    cab = bytearray(b[:ofs_l])
    struct.pack_into("<8I", cab, 36, ofs_spr, nspr, ofs_pal, npal, ofs_l, len(ld), ofs_l + len(ld), len(td))
    return bytes(cab) + bytes(ld) + bytes(td)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lutador")
    ap.add_argument("antes", type=Path)
    ap.add_argument("depois", type=Path)
    ap.add_argument("--forca", type=float, default=1.0)
    ap.add_argument("--saida", type=Path)
    ar = ap.parse_args()
    alvo = RAIZ / "chars" / ar.lutador / f"{ar.lutador}.sff"
    pa, A, _ = ler(ar.antes)
    pb, B, _ = ler(ar.depois)
    pc, C, _ = ler(alvo)
    assert pa == pb == pc, "paleta diferente entre A, B e o .sff do jogo (paleta_sff.act mudou?)"
    dA = {(n["g"], n["i"]): n for n in A}
    dB = {(n["g"], n["i"]): n for n in B}
    mud = {k for k in dA if k in dB and bool(dA[k].get("png")) == bool(dB[k].get("png")) and dA[k]["px"] != dB[k]["px"]}
    refs = {f: RefCor(Endereco(f"{ar.lutador}/{acao}/0")) for (l, f), acao in PARADO.items() if l == ar.lutador}

    b = bytearray(alvo.read_bytes())
    ofs_spr, nspr, ofs_pal, npal, ofs_l, len_l, ofs_t, len_t = struct.unpack_from("<8I", b, 36)
    assert ofs_t + len_t == len(b), "tdata não é o fim do arquivo"
    novos = bytearray()
    exatos = tom = recortes = 0
    trocados = set()
    pulados = []
    for k, n in enumerate(C):
        chave = (n["g"], n["i"])
        if chave not in mud or n["link"] is not None:
            continue
        novo_tam = None  # o conserto pode mudar o recorte (w, h) e o eixo: no exato vale o de B
        if n.get("png"):  # PNG de 32 bits (o Diabo, os efeitos): só troca se o do jogo é igual ao de antes
            if n["px"] != dA[chave]["px"]:
                pulados.append(chave)
                continue
            corpo = dB[chave]["px"]  # já vem com o tamanho descomprimido na frente
            novo_tam = dB[chave]
            exatos += 1
        elif (n["w"], n["h"], n["px"]) == (dA[chave]["w"], dA[chave]["h"], dA[chave]["px"]):
            px = dB[chave]["px"]
            novo_tam = dB[chave]
            exatos += 1
        else:
            a = rgba_de(n, pc)
            med = {f: r.medir(a)["deriva"] for f, r in refs.items()}
            f = min(med, key=med.get)
            px = indices_de(refs[f].corrigir(a, ar.forca), pc)
            tom += 1
        if not n.get("png"):
            corpo = struct.pack("<I", len(px)) + rle8(px)
        g, i, w, h, x, y, link, fmt, dep, off, ln, pi, fl = struct.unpack_from("<HHHHhhHBBIIHH", b, ofs_spr + 28 * k)
        if novo_tam is not None and (novo_tam["w"], novo_tam["h"]) != (w, h):
            # recorte novo: o eixo anda junto (x, y do jogo + o quanto o eixo de B andou em relação ao de A)
            a_ = dA[chave]
            w, h = novo_tam["w"], novo_tam["h"]
            x, y = x + novo_tam["x"] - a_["x"], y + novo_tam["y"] - a_["y"]
            recortes += 1
        struct.pack_into("<HHHHhhHBBIIHH", b, ofs_spr + 28 * k, g, i, w, h, x, y, link, fmt, dep,
                         len_t + len(novos), len(corpo), pi, fl | 1)
        novos += corpo
        trocados.add(k)
    # link para um nó trocado mostra o desenho novo: só pode se o sprite do link também é de quadro consertado
    estranhos = [(n["g"], n["i"]) for n in C if n["link"] in trocados and (n["g"], n["i"]) not in mud]
    struct.pack_into("<I", b, 36 + 28, len_t + len(novos))
    saida = ar.saida or alvo
    saida.write_bytes(compactar(bytes(b) + bytes(novos)))
    print(f"{saida}: {exatos} sprites trocados pelo gerado (iguais ao de antes), {tom} consertados no próprio sprite, "
          f"{len(mud) - exatos - tom} de {len(mud)} são link (seguem o nó trocado) ou não estão no jogo; +{len(novos) / 1e6:.2f} MB"
          + (f"; {recortes} com recorte/eixo novo" if recortes else "")
          + (f"; PULADOS (o do jogo não é o de antes): {pulados[:10]}" if pulados else "")
          + (f"; ATENÇÃO, links para sprites trocados fora da lista: {estranhos[:10]}" if estranhos else ""))


if __name__ == "__main__":
    main()
