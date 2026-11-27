"""Monta, a partir do SFF final, cada golpe como aparece no Despertar, ao lado da forma normal."""
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

repo = Path(sys.argv[1])
saida = Path(sys.argv[2])
saida.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(repo / "ferramentas"))
import verificar_pengaro as v

v.PERSONAGEM = "pengaro"
v.PASTA = repo / "chars/pengaro"
sprites, pal = v.ler_sff()
acoes = v.ler_air()
cns = (v.PASTA / "pengaro.cns").read_text(encoding="utf-8")
secao = re.search(r"\[RemapPreset despertado\]\n((?:\d+,\d+ = \d+,\d+\n)+)", cns)[1]
remap = {(int(a), int(b)): (int(c), int(d)) for a, b, c, d in re.findall(r"(\d+),(\d+) = (\d+),(\d+)", secao)}
print("pares", len(remap))


def tela(chave):
    s = sprites[chave]
    t = Image.new("RGBA", (360, 260), (58, 46, 66, 255))
    t.alpha_composite(v.imagem(s, pal), (max(0, 180 - s[2]), max(0, 220 - s[3])))
    d = ImageDraw.Draw(t)
    d.line((60, 220, 300, 220), fill=(120, 120, 130, 255))
    return t.crop((60, 60, 320, 240))


linhas = [(20, "anda"), (240, "chute forte"), (210, "soco"), (41, "pulo"), (440, "rasteira"), (5050, "queda"), (1100, "compasso")]
cols = 8
o = Image.new("RGB", (cols * 130, len(linhas) * 2 * 90), (20, 20, 24))
sobra = []
for r, (n, nome) in enumerate(linhas):
    q = acoes[n]
    for c in range(cols):
        g, i, _ = q[c * (len(q) - 1) // (cols - 1)]
        o.paste(tela((g, i)).resize((130, 90)).convert("RGB"), (c * 130, r * 180))
        destino = remap.get((g, i))
        if destino:
            o.paste(tela(destino).resize((130, 90)).convert("RGB"), (c * 130, r * 180 + 90))
        else:
            sobra.append((n, g, i))
print("sem par nas amostras", sobra[:8])
o.save(saida / "remap.png")

# altura em pé: o endiabrado não pode ficar maior nem menor que o normal
for nome, chave in (("normal", (acoes[0][0][0], acoes[0][0][1])), ("endiabrado", (acoes[9203][0][0], acoes[9203][0][1]))):
    s = sprites[chave]
    print(nome, "altura", v.imagem(s, pal).getbbox())
