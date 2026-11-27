"""Folha de contato das ações finais lidas do .sff/.air, com as caixas (Clsn1 vermelho, Clsn2 azul).
python contato.py <pasta chars/pengaro> <saida.png> <z> <cols> acao..."""
import re, sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, "C:/Dev/Jogo-de-Luta-anatomia/ferramentas")
import verificar_pengaro as v
pasta, saida, z, cols = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
v.PERSONAGEM, v.PASTA = "pengaro", pasta
sprites, pal = v.ler_sff()
acoes = {}
atual = None
for linha in (pasta / "pengaro.air").read_text(encoding="utf-8").splitlines():
    linha = linha.split(";")[0].strip()
    m = re.match(r"\[Begin Action (\d+)\]", linha)
    if m:
        atual = int(m.group(1)); acoes[atual] = []; c1, c2d = [], []
        continue
    m = re.match(r"Clsn([12])(Default)?\[\d+\]\s*=\s*(.*)", linha)
    if m:
        cx = tuple(int(x) for x in m.group(3).split(","))
        if m.group(1) == "1": c1.append(cx)
        else: c2d.append(cx)
    elif atual is not None and re.match(r"-?\d+,\s*-?\d+,", linha):
        p = [x.strip() for x in linha.split(",")]
        acoes[atual].append(((int(p[0]), int(p[1])), int(p[4]), c1, c2d, len(p) > 5 and "H" in p[5]))
        c1 = []
X0, Y0, W, H = 70, 40, 220, 190   # recorte da tela 360x260 (eixo 180,220)
celas = []
for n in (int(a) for a in sys.argv[5:]):
    juntos = []
    for k, (spr, t, c1, c2, flip) in enumerate(acoes[n]):
        if juntos and juntos[-1][1] == spr and bool(juntos[-1][3]) == bool(c1):
            juntos[-1][2] += t if t > 0 else 0
            continue
        juntos.append([k + 1, spr, t, c1, c2, flip])
    for k, spr, t, c1, c2, flip in juntos:
        tela = Image.new("RGBA", (360, 260), (70, 90, 110, 255))
        if spr in sprites:
            s = sprites[spr]
            im = v.imagem(s, pal)
            if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
            tela.alpha_composite(im, (180 - (im.width - s[2] if flip else s[2]), 220 - s[3]))
        d = ImageDraw.Draw(tela)
        d.line((0, 220, 360, 220), fill=(40, 50, 60))
        tela = tela.crop((X0, Y0, X0 + W, Y0 + H)).resize((W * z, H * z), Image.NEAREST)
        d = ImageDraw.Draw(tela)
        for cs, cor in ((c2, (90, 160, 255)), (c1, (255, 40, 40))):
            for x1, y1, x2, y2 in cs:
                xa, xb = sorted((x1, x2)); ya, yb = sorted((y1, y2))
                d.rectangle(((180 + xa - X0) * z, (220 + ya - Y0) * z, (180 + xb - X0) * z, (220 + yb - Y0) * z), outline=cor)
        d.text((4, 2), f"{n} el{k} {t}t  spr {spr[0]},{spr[1]}", fill="white")
        celas.append(tela)
linhas = -(-len(celas) // cols)
folha = Image.new("RGB", (cols * W * z, linhas * H * z), (30, 30, 30))
for i, c in enumerate(celas):
    folha.paste(c, ((i % cols) * W * z, (i // cols) * H * z))
folha.save(saida)
print(saida, folha.size, len(celas))
