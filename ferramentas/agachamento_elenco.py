"""Conserva o apoio do agachado do kit e anima o tronco, nas duas formas."""
import math
import re
import sys
from pathlib import Path

import conferir_sff as cs
import efeitos
from dobra_agachado import dobrados
from ligar_pecas import ler_remap, por_remap


RAIZ = Path(__file__).resolve().parents[1]
GRUPO = 57520
ELEMENTO = re.compile(r"^(\d+),\s*(\d+),(\s*0,\s*0,\s*)(\d+)[ \t]*$", re.M)


def acao(texto, numero):
    return re.search(rf"(?ims)^\[Begin Action {numero}\][^\n]*\n.*?(?=^\[|\Z)", texto)


def aplicar(nome, pasta=None):
    pasta = pasta or RAIZ / "chars" / nome
    air, cns, sff = (pasta / f"{nome}.{ext}" for ext in ("air", "cns", "sff"))
    texto = air.read_text(encoding="utf-8")
    bloco = acao(texto, 11).group()
    elementos = list(ELEMENTO.finditer(bloco))
    primeira = elementos[0]
    origem = tuple(map(int, primeira.group(1, 2)))
    if origem[0] == GRUPO:
        return
    estados = cns.read_text(encoding="utf-8")
    desperto = ler_remap(estados)[origem]
    pal, nos, _ = cs.ler(sff)
    extras = cs.EXTRAS[str(sff.resolve())]
    indice = {(n["g"], n["i"]): n for n in nos}
    assert all(g not in (GRUPO, GRUPO + 1) for g, i in indice)
    rle, png = [], []
    for n in nos:
        item = tuple(n[k] for k in ("g", "i", "w", "h", "x", "y", "px"))
        if n.get("png"):
            png.append(item)
        else:
            rle.append((*item, n.get("pi", 0)))
    # O desenho de origem já está montado com as peças e os acessórios do lutador.
    # A dobra só afeta a metade superior. Conserva o eixo do SFF e os dois pés.
    for forma, chave in enumerate((origem, desperto)):
        n = indice[chave]
        pi = n.get("pi", 0)
        cores = extras[pi - 2] if pi >= 2 else pal
        for i, (im, x, y) in enumerate(dobrados(dict(n, pi=0), cores, [(a, 0) for a in range(5)])):
            png.append((GRUPO + forma, i, *im.size, x, y, efeitos.blob_png(im)))

    duracao = sum(int(e[4]) for e in elementos)
    tique = 0
    def respirar(e):
        nonlocal tique
        quadro = round(2 - 2 * math.cos(2 * math.pi * tique / duracao))
        tique += int(e[4])
        return f"{GRUPO},{quadro},{e[3]}{e[4]}"

    texto = texto.replace(bloco, ELEMENTO.sub(respirar, bloco), 1)
    for numero in (10, 12):
        bloco = acao(texto, numero).group()
        linhas = list(ELEMENTO.finditer(bloco))
        assert len(linhas) == 1 and re.search(r'^Clsn2(?:Default)?:', bloco, re.M), (nome, numero)
        linha = linhas[0]
        tempo = int(linha[4])
        assert tempo >= 2
        transicao = f"{linha[1]},{linha[2]},{linha[3]}{tempo - 1}"
        baixa = f"{GRUPO},0,{linha[3]}1"
        ordem = (transicao, baixa) if numero == 10 else (baixa, transicao)
        caixas = re.sub(r'^Clsn2:', 'Clsn2Default:', bloco[:linha.start()], flags=re.M)
        novo = caixas + "\n".join(ordem) + bloco[linha.end():]
        texto = texto.replace(bloco, novo, 1)
    efeitos.gravar(sff, pal, rle, png, extras)
    air.write_text(texto, encoding="utf-8", newline="\n")
    remap = {(GRUPO, i): (GRUPO + 1, i) for i in range(5)}
    cns.write_text(por_remap(estados, remap), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    for lutador in sys.argv[1:]:
        aplicar(lutador)
