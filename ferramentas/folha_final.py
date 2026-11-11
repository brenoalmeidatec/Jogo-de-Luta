"""Folha de contato da animação FINAL: um desenho por elemento do .air, lido do .sff gerado, todos na mesma caixa.

  python ferramentas/folha_final.py saida.png 0 20 [--e] [--z 3] [--cols 8]

--e aplica o [RemapPreset despertado] (forma endiabrada). O rótulo de cada desenho é acao/elemento e os ticks; o risco
vermelho marca o eixo do lutador. Serve para OLHAR anatomia (mãos, pernas, caneleira, garrafa) sem abrir o motor."""
import sys, re
from pathlib import Path
a = sys.argv[1:]; out = a.pop(0); z = 3; cols = 8; desp = False; raiz = Path(__file__).resolve().parent.parent
acoes_p = []
while a:
    o = a.pop(0)
    if o == "--z": z = int(a.pop(0))
    elif o == "--cols": cols = int(a.pop(0))
    elif o == "--e": desp = True
    elif o == "--raiz": raiz = Path(a.pop(0))
    else: acoes_p.append(int(o))
sys.path.insert(0, str(raiz / "ferramentas"))
import verificar_pengaro as v, video_golpe as vg
from PIL import Image, ImageDraw
v.PERSONAGEM = "pengaro"; v.PASTA = raiz / "chars/pengaro"
sprites, pal = v.ler_sff()
if desp:
    cns = (v.PASTA / "pengaro.cns").read_text(encoding="utf-8")
    bloco = re.search(r"^\[RemapPreset despertado\]\n(.*?)(?=^\[)", cns, re.M | re.S)
    orig, sprites = sprites, dict(sprites)
    for g, i, g2, i2 in re.findall(r"^(\d+),\s*(\d+)\s*=\s*(\d+),\s*(\d+)", bloco.group(1), re.M):
        if (int(g2), int(i2)) in orig: sprites[(int(g), int(i))] = orig[(int(g2), int(i2))]
d = vg.Desenhos(sprites, pal); air = vg.ler_air(v.PASTA, "pengaro")
W, H, CX, CY = 360, 260, 180, 220
ims = []
for n in acoes_p:
    for k, el in enumerate(air[n][0]):
        t = Image.new("RGBA", (W, H))
        if (el[0], el[1]) in d.sprites:
            img, ax, ay = d.rgba((el[0], el[1]), el[5]); t.alpha_composite(img, (CX - ax + el[2], CY - ay + el[3]))
        ims.append((f"{n}/{k} {el[4]}t", t))
bb = None
for _, im in ims:
    b = im.getchannel("A").getbbox()
    if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
w = (bb[2] - bb[0]) * z + 6; h = (bb[3] - bb[1]) * z + 14; rows = (len(ims) + cols - 1) // cols
tela = Image.new("RGB", (w * cols, h * rows), (70, 90, 110)); dr = ImageDraw.Draw(tela)
for n, (rot, im) in enumerate(ims):
    g = im.crop(bb); g = g.resize((g.width * z, g.height * z), Image.NEAREST)
    x, y = (n % cols) * w + 3, (n // cols) * h + 12
    tela.paste(g, (x, y), g); dr.text((x, (n // cols) * h), rot, fill=(255, 255, 0))
    dr.line((x + (CX - bb[0]) * z, y, x + (CX - bb[0]) * z, y + 6), fill=(255, 0, 0))
tela.save(out); print(out, tela.size)
