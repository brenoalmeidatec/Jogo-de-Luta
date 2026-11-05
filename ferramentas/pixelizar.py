"""
Transforma as imagens geradas (1024x1024) em pixel art no estilo do pixelfx:
pouca resolução, poucas cores, cores chapadas e um contorno escuro de 1 pixel.

  python ferramentas/pixelizar.py sprites/kaio            (todas as poses do personagem)
  python ferramentas/pixelizar.py sprites/kaio --altura 80 --cores 12

Saída em sprites/<personagem>/pixel/:
  <pose>.png             sprite pixelado em tamanho real (ex.: 64 px de altura)
  <pose>_x4.png          o mesmo ampliado 4x só para você visualizar
  <personagem>.png/.json folha com todas as poses (mesmo formato de JSON dos efeitos do pixelfx/Aseprite)
"""
import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Instale a biblioteca primeiro:  pip install pillow")


def pixelizar(img: Image.Image, altura: int, cores: int, contorno: bool) -> Image.Image:
    img = img.convert("RGBA")
    caixa = img.getchannel("A").point(lambda a: 255 if a > 40 else 0).getbbox()
    if caixa:
        img = img.crop(caixa)
    largura = max(1, round(img.width * altura / img.height))
    pequeno = img.resize((largura, altura), Image.BOX)

    # alfa binário: pixel art não tem meia transparência
    alfa = pequeno.getchannel("A").point(lambda a: 255 if a >= 128 else 0)

    # reduz a paleta (cores chapadas)
    rgb = Image.new("RGB", pequeno.size, (0, 0, 0))
    rgb.paste(pequeno.convert("RGB"), mask=alfa)
    rgb = rgb.quantize(colors=cores, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")

    saida = Image.new("RGBA", (largura + 2, altura + 2), (0, 0, 0, 0))
    saida.paste(rgb, (1, 1), mask=alfa)

    if contorno:
        # uma linha de tinta escura em volta da silhueta, como o boneco do pixelfx
        a = saida.getchannel("A").load()
        px = saida.load()
        tinta = (20, 16, 28, 255)
        w, h = saida.size
        borda = [(x, y) for y in range(h) for x in range(w) if a[x, y] == 0 and any(
            0 <= x + dx < w and 0 <= y + dy < h and a[x + dx, y + dy]
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in borda:
            px[x, y] = tinta
    return saida


def main():
    p = argparse.ArgumentParser(description="Converte sprites em pixel art")
    p.add_argument("pasta", help="pasta do personagem, ex.: sprites/kaio")
    p.add_argument("--altura", type=int, default=64, help="altura do personagem em pixels (padrão 64)")
    p.add_argument("--cores", type=int, default=16, help="número de cores da paleta (padrão 16)")
    p.add_argument("--sem-contorno", action="store_true")
    args = p.parse_args()

    pasta = Path(args.pasta)
    imagens = sorted(f for f in pasta.glob("*.png") if f.stem != "base")
    if not imagens:
        sys.exit(f"Nenhuma pose .png em {pasta}")
    destino = pasta / "pixel"
    destino.mkdir(exist_ok=True)

    quadros = []
    for f in imagens:
        s = pixelizar(Image.open(f), args.altura, args.cores, not args.sem_contorno)
        s.save(destino / f.name)
        s.resize((s.width * 4, s.height * 4), Image.NEAREST).save(destino / f"{f.stem}_x4.png")
        quadros.append((f.stem, s))
        print(f"  {f.name} -> {s.width}x{s.height}")

    # folha de sprites com células do mesmo tamanho, pés alinhados embaixo
    cw = max(s.width for _, s in quadros)
    ch = max(s.height for _, s in quadros)
    folha = Image.new("RGBA", (cw * len(quadros), ch), (0, 0, 0, 0))
    frames = {}
    for i, (nome, s) in enumerate(quadros):
        folha.paste(s, (i * cw + (cw - s.width) // 2, ch - s.height))
        frames[nome] = {"frame": {"x": i * cw, "y": 0, "w": cw, "h": ch}, "duration": 100}
    nome = pasta.name
    folha.save(destino / f"{nome}.png")
    meta = {"image": f"{nome}.png", "size": {"w": folha.width, "h": folha.height},
            "pivot": {"x": cw // 2, "y": ch - 1}}
    (destino / f"{nome}.json").write_text(json.dumps({"frames": frames, "meta": meta}, indent=1), encoding="utf-8")
    print(f"Folha: {destino / (nome + '.png')}")


if __name__ == "__main__":
    main()
