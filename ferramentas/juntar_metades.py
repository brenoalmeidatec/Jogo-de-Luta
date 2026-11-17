# juntar2.py ESQ DIR SAIDA : capturas com moldura verde (canvas W+8 x 733); recorta pela moldura e volta a 1100x725
# acha a moldura pelas linhas/colunas quase todas verdes (o Grão-Pastor tem verde no desenho)
import sys; import numpy as np; from PIL import Image
def ab(p):
    a = np.asarray(Image.open(p).convert('RGB')).astype(int)
    v = (a[..., 1] > 200) & (a[..., 0] < 90) & (a[..., 2] < 90)
    rs = np.where(v.sum(1) > 0.6 * v.sum(1).max())[0]; cs = np.where(v.sum(0) > 0.6 * v.sum(0).max())[0]
    x0, x1, y0, y1 = cs.min(), cs.max(), rs.min(), rs.max()
    k = (x1 - x0 + 1) / 1108
    b = round(4 * k)
    assert abs((x1 - x0 + 1) / (y1 - y0 + 1) - 1108 / 733) < .02, ("moldura incompleta", x0, x1, y0, y1)
    im = Image.fromarray(a[y0 + b:y1 + 1 - b, x0 + b:x1 + 1 - b].astype(np.uint8))
    return im.resize((1100, 725), Image.LANCZOS)
a = ab(sys.argv[1]); b = ab(sys.argv[2]); x0 = 1072
o = Image.new('RGB', (2172, 724)); o.paste(a.crop((0, 0, 1100, 724)), (0, 0)); o.paste(b.crop((0, 0, 1100, 724)), (x0, 0))
o.save(sys.argv[3]); print(o.size)
