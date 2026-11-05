#!/usr/bin/env python3
"""Confere chars/pengaro sem abrir o jogo: lê o SFF de volta e cruza AIR, CNS e CMD.

Uso: python ferramentas/verificar_pengaro.py [previa.png]
"""
import re
import struct
import sys
from pathlib import Path

from PIL import Image

PASTA = Path(__file__).resolve().parent.parent / "chars/pengaro"
# Ações que os estados comuns do motor procuram no personagem.
ACOES_DO_MOTOR = [0, 5, 6, 10, 11, 12, 20, 21, 40, 41, 42, 43, 47, 100, 105, 120, 121, 122, 130, 131, 132,
                  140, 141, 142, 150, 151, 152, 5000, 5001, 5002, 5005, 5006, 5007, 5010, 5011, 5012, 5015,
                  5016, 5017, 5020, 5021, 5022, 5025, 5026, 5027, 5030, 5035, 5040, 5050, 5051, 5061, 5070,
                  5080, 5090, 5100, 5101, 5110, 5120, 5150, 5160, 5170, 5200, 5210, 5300]
COMANDOS_DO_MOTOR = ["FF", "BB", "recovery", "holdfwd", "holdback", "holdup", "holddown"]
erros = []


def ler_sff():
    d = (PASTA / "pengaro.sff").read_bytes()
    assert d[:12] == b"ElecbyteSpr\x00" and list(d[12:16]) == [0, 1, 0, 2], "cabeçalho do SFF"
    ofs_s, n, ofs_p, n_p, ofs_l, len_l, ofs_t, _ = struct.unpack("<8I", d[36:68])
    assert ofs_l + len_l == len(d) == ofs_t, "tamanho do SFF"
    g, i, cols, link, po, pl = struct.unpack("<HHHHII", d[ofs_p:ofs_p + 16])
    assert n_p == 1 and cols == 256 and pl == 1024, "paleta"
    pal = d[ofs_l + po:ofs_l + po + pl]
    sprites = {}
    for k in range(n):
        s = struct.unpack("<HHHHhhHBBIIHH", d[ofs_s + 28 * k:ofs_s + 28 * k + 28])
        grupo, ind, w, h, ax, ay, _, fmt, prof, ofs, tam, _, _ = s
        assert fmt == 2 and prof == 8, f"formato do sprite {grupo},{ind}"
        dado = d[ofs_l + ofs:ofs_l + ofs + tam]
        total = struct.unpack("<I", dado[:4])[0]
        assert total == w * h, f"tamanho do sprite {grupo},{ind}"
        px = bytearray()
        j = 4
        while j < len(dado):
            b = dado[j]
            if b & 0xC0 == 0x40:
                px += bytes((dado[j + 1],)) * (b & 0x3F)
                j += 2
            else:
                px.append(b)
                j += 1
        assert len(px) == total, f"RLE do sprite {grupo},{ind}"
        sprites[(grupo, ind)] = (w, h, ax, ay, bytes(px))
    return sprites, pal


def imagem(sprite, pal):
    w, h, _, _, px = sprite
    rgba = bytearray()
    for v in px:
        rgba += pal[v * 4:v * 4 + 3] + (b"\x00" if v == 0 else b"\xff")
    return Image.frombytes("RGBA", (w, h), bytes(rgba))


def ler_air():
    acoes = {}
    atual = None
    for linha in (PASTA / "pengaro.air").read_text(encoding="utf-8").splitlines():
        linha = linha.split(";")[0].strip()
        m = re.match(r"\[Begin Action (\d+)\]", linha)
        if m:
            atual = int(m.group(1))
            if atual in acoes:
                erros.append(f"ação repetida: {atual}")
            acoes[atual] = []
        elif re.match(r"-?\d+,\s*-?\d+,", linha):
            p = [x.strip() for x in linha.split(",")]
            acoes[atual].append((int(p[0]), int(p[1]), int(p[4])))
    return acoes


def main():
    sprites, pal = ler_sff()
    acoes = ler_air()
    for numero, quadros in acoes.items():
        if not quadros:
            erros.append(f"ação vazia: {numero}")
        for g, i, _ in quadros:
            if (g, i) not in sprites:
                erros.append(f"ação {numero} usa o sprite {g},{i}, que não existe")
    for numero in ACOES_DO_MOTOR:
        if numero not in acoes:
            erros.append(f"falta a ação {numero}, exigida pelo motor")

    cns = (PASTA / "pengaro.cns").read_text(encoding="utf-8")
    cmd = (PASTA / "pengaro.cmd").read_text(encoding="utf-8")
    estados = {int(n) for n in re.findall(r"^\[Statedef (-?\d+)\]", cns, re.M)}
    comuns = {0, 10, 11, 12, 20, 50, 52, 100, 105, 5050, 5100}
    for texto in (cns, cmd):
        for destino in re.findall(r"type = ChangeState\n(?:.*\n)*?value = (\d+)", texto):
            if int(destino) not in estados | comuns:
                erros.append(f"ChangeState para o estado {destino}, que não existe")
    for chave in ("anim", "projanim", "projhitanim", "projremanim"):
        for n in re.findall(rf"^{chave} = (\d+)$", cns, re.M):
            if int(n) not in acoes and n != "100":
                erros.append(f"{chave} {n} não existe no AIR")
    definidos = set(re.findall(r'^name = "(\w+)"', cmd, re.M))
    usados = set(re.findall(r'command\s*!?=\s*"(\w+)"', cmd + cns))
    for nome in sorted(usados - definidos):
        erros.append(f'comando "{nome}" usado mas não definido')
    for nome in COMANDOS_DO_MOTOR:
        if nome not in definidos:
            erros.append(f'falta o comando "{nome}", exigido pelo motor')

    if len(sys.argv) > 1:
        escolha = [k for k in sorted(sprites) if k[0] != 9000][:80:2]
        folha = Image.new("RGBA", (8 * 170, 5 * 170), (58, 46, 66, 255))
        for n, k in enumerate(escolha):
            s = sprites[k]
            im = imagem(s, pal)
            x, y = (n % 8) * 170 + 85, (n // 8) * 170 + 150
            folha.alpha_composite(im, (max(0, x - s[2]), max(0, y - s[3])))
        folha.save(sys.argv[1])

    print(f"{len(sprites)} sprites, {len(acoes)} ações, {len(estados)} estados, {len(definidos)} comandos")
    for e in erros:
        print("ERRO:", e)
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
