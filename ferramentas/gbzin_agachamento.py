"""Monta a guarda baixa do Gbzin com a cabeça do kit e o conjunto de pernas da pose baixa."""
import re
from pathlib import Path

from PIL import Image

import conferir_sff as sff
import efeitos
import gbzin_pecas as boneco
import ligar_pecas as ligar
from pengaro_todo import dobrar


CHAR = Path(__file__).resolve().parents[1] / "chars/gbzin"
GRUPO = 57510


def aplicar():
    kit = boneco.ler_kit()
    poses = []
    for indice in (1, 2, 4):
        original = boneco.abrir(f"agachado/{indice:02d}")
        cabeca = boneco.achar_cabeca(kit, original, angulos=range(-15, 26, 5))
        quadro, _ = boneco.trocar_cabeca(kit, original, cabeca)
        poses.append(quadro)
    # A respiração da guarda baixa só move o que está acima da cintura.
    baixa = poses[-1]
    for graus in (2, 4, 6):
        poses.append(dobrar(baixa, graus))

    arquivo = CHAR / "gbzin.sff"
    paleta, nos, _ = sff.ler(arquivo)
    rle, png = [], []
    for n in nos:
        if n["g"] == GRUPO:
            continue
        item = (n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"])
        if n.get("png"):
            png.append(item)
        else:
            rle.append((*item, n.get("pi", 0)))
    for i, quadro in enumerate(poses):
        img, x, y = ligar.recortar(Image.fromarray(quadro))
        png.append((GRUPO, i, *img.size, x, y, efeitos.blob_png(img)))
    efeitos.gravar(arquivo, paleta, rle, png)

    air = CHAR / "gbzin.air"
    texto = air.read_text(encoding="utf-8")
    for acao, elementos in ((10, [(0, 1), (1, 1)]), (11, [(i, 8) for i in (2, 3, 4, 5, 4, 3)]),
                            (12, [(1, 1), (0, 1)])):
        padrao = rf"(?im)(^\[Begin Action {acao}\]\n(?:[^\n]*Clsn[^\n]*\n)+)(?:^\d+,[^\n]*\n)+"
        linhas = "".join(f"{GRUPO},{i}, 0,0, {tiques}\n" for i, tiques in elementos)
        texto, total = re.subn(padrao, lambda m: m[1] + linhas, texto)
        assert total == 1, acao
    air.write_text(texto, encoding="utf-8", newline="\n")
    cns = CHAR / "gbzin.cns"
    texto = cns.read_text(encoding="utf-8")
    remap = ligar.ler_remap(texto)
    novos = {(GRUPO, i): remap[g, 0] for i, g in enumerate((359, 359, 361, 362, 363, 364))}
    cns.write_text(ligar.por_remap(texto, novos), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    aplicar()
