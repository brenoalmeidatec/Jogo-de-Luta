#!/usr/bin/env python3
"""Prova do piloto do boneco de peças: vídeo lado a lado (atual à esquerda, novo à direita) a 60 fps, tira com todos
os ticks e folha de contato antes/depois.

  python ferramentas/video_pecas.py SAIDA

Os dois lados usam a mesma tela 3x e o mesmo eixo do jogo; o atual é o sprite que o jogo mostra hoje (os quadros de
quadros_arcade_hd que o gerador liga em cada elemento da ação), o novo é quadros_pecas_hd com o tempos.json. O motor
não é aberto: os ticks são os da [Begin Action] (como o video_golpe.py faz), sem o movimento do CNS.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
SPR = RAIZ / "sprites/pengaro"
# o que o jogo mostra hoje em cada elemento (sprite do .sff -> quadro de origem, por achar_quadro.py)
ATUAL = {
    "parado": [("ginga/03", 6), ("ginga/07", 6), ("ginga/01", 5), ("ginga/06", 7), ("ginga/02", 7), ("ginga/01", 5)],
    "soco": [("soco/03", 4), ("soco/05", 6), ("soco/06", 3), ("soco/07", 6)],
    "chute_alto": [("chute_alto/01", 5), ("chute_alto/02", 4), ("chute_alto/04", 6), ("chute_alto/05", 3),
                   ("chute_alto/06", 12), ("chute_alto/07", 12)],
}
CORTE = (400, 280, 760, 670)
GUARDA = "ginga/00"  # desenho da guarda de hoje (o firme.py troca pelo do lutador)
K = 2
try:
    FONTE = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
except OSError:
    FONTE = ImageFont.load_default()


def quadro(caminho, caixa=None):
    f = Image.open(caminho).convert("RGBA")
    bg = Image.new("RGBA", f.size, (60, 60, 70, 255))
    bg.alpha_composite(f)
    if caixa:
        d = ImageDraw.Draw(bg)
        x0, y0, x1, y1 = caixa
        d.rectangle([540 + x0, 660 + y0, 540 + x1, 660 + y1], outline=(255, 60, 60, 255), width=2)
    c = bg.crop(CORTE)
    return c.resize((c.width * K, c.height * K), Image.NEAREST).convert("RGB")


def ticks_atual(nome):
    out = []
    for q, t in ATUAL[nome]:
        out += [SPR / "quadros_arcade_hd" / f"{q}.png"] * t
    return out


def ticks_novo(nome):
    tempos = json.loads((SPR / "quadros_pecas_hd" / nome / "tempos.json").read_text(encoding="utf-8"))
    out = []
    for e in tempos["elementos"]:
        out += [(SPR / "quadros_pecas_hd" / nome / f"{e['desenho']:02d}.png", tuple(tempos["caixa"]) if e["caixa"] else None)] \
            * e["ticks"]
    return out


def main():
    main_em(Path(sys.argv[1]))


def main_em(saida):
    saida.mkdir(parents=True, exist_ok=True)
    for nome in ATUAL:
        a = [(p, None) for p in ticks_atual(nome)]
        n = ticks_novo(nome)
        guarda_a = (SPR / f"quadros_arcade_hd/{GUARDA}.png", None)
        guarda_n = (SPR / "quadros_pecas_hd/guarda.png", None)
        if nome != "parado":  # o golpe sai da guarda e volta para ela, em loop
            a, n = [guarda_a] * 20 + a + [guarda_a] * 20, [guarda_n] * 20 + n + [guarda_n] * 20
        total = max(len(a), len(n))
        a += [a[-1]] * (total - len(a))
        n += [n[-1]] * (total - len(n))
        tmp = saida / f"_{nome}"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir()
        cache = {}
        w, h = (CORTE[2] - CORTE[0]) * K, (CORTE[3] - CORTE[1]) * K
        voltas = 4
        for k in range(total * voltas):
            ia, inn = a[k % total], n[k % total]
            chave = (ia, inn)
            if chave not in cache:
                img = Image.new("RGB", (w * 2, h + 44), (40, 40, 48))
                img.paste(quadro(*ia), (0, 44))
                img.paste(quadro(*inn), (w, 44))
                d = ImageDraw.Draw(img)
                d.text((12, 8), f"{nome}: atual (jogo hoje)", fill=(255, 230, 120), font=FONTE)
                d.text((w + 12, 8), f"{nome}: corpo firme", fill=(255, 230, 120), font=FONTE)
                cache[chave] = img
            cache[chave].save(tmp / f"{k:05d}.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "60", "-i", str(tmp / "%05d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", str(saida / f"{nome}_lado_a_lado.mp4")],
                       check=True)
        shutil.rmtree(tmp)
        # tira com todos os ticks do golpe novo (numerados), em 1/2
        tw, th = w // 2, h // 2
        por_linha = 12
        linhas = (len(n) + por_linha - 1) // por_linha
        tira = Image.new("RGB", (tw * por_linha, th * linhas), (40, 40, 48))
        d = ImageDraw.Draw(tira)
        for i, q in enumerate(n):
            tira.paste(quadro(*q).resize((tw, th)), ((i % por_linha) * tw, (i // por_linha) * th))
            d.text(((i % por_linha) * tw + 6, (i // por_linha) * th + 4), str(i), fill=(255, 255, 255), font=FONTE)
        tira.save(saida / f"{nome}_ticks.png")
        # folha de contato antes (em cima) e depois (embaixo), mesmo tamanho
        antes = sorted({p for p in ticks_atual(nome)}, key=lambda p: p.as_posix())
        depois = sorted((SPR / "quadros_pecas_hd" / nome).glob("[0-9][0-9].png"))
        col = max(len(antes), len(depois))
        folha = Image.new("RGB", (tw * col, th * 2 + 80), (40, 40, 48))
        d = ImageDraw.Draw(folha)
        d.text((8, 6), "antes (jogo hoje)", fill=(255, 230, 120), font=FONTE)
        d.text((8, th + 46), "depois (corpo firme)", fill=(255, 230, 120), font=FONTE)
        for i, p in enumerate(antes):
            folha.paste(quadro(p).resize((tw, th)), (i * tw, 36))
        for i, p in enumerate(depois):
            folha.paste(quadro(p).resize((tw, th)), (i * tw, th + 76))
        folha.save(saida / f"{nome}_antes_depois.png")
        print(nome, "ok")


if __name__ == "__main__":
    main()
