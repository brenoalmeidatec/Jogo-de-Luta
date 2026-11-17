# juntar_metades.py ESQ DIR SAIDA: junta as duas capturas (com moldura verde) de uma folha do ChatGPT em 2172x724. Ver ferramentas/chatgpt_helpers.js
import sys; import numpy as np; from PIL import Image
def ab(p):
    a = np.asarray(Image.open(p).convert('RGB')).astype(int)
    v = (a[..., 1] > 200) & (a[..., 0] < 90) & (a[..., 2] < 90)
    ys, xs = np.where(v)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    # a moldura tem 4 px do canvas: na captura vale 4 * (largura capturada / 1108)
    k = (x1 - x0 + 1) / 1108
    b = round(4 * k)
    im = Image.fromarray(a[y0 + b:y1 + 1 - b, x0 + b:x1 + 1 - b].astype(np.uint8))
    assert abs((x1 - x0 + 1) / (y1 - y0 + 1) - 1108 / 733) < .02, ("moldura incompleta", x0, x1, y0, y1)
    return im.resize((1100, 725), Image.LANCZOS)
a = ab(sys.argv[1]); b = ab(sys.argv[2]); x0 = 1072
o = Image.new('RGB', (2172, 724)); o.paste(a.crop((0, 0, 1100, 724)), (0, 0)); o.paste(b.crop((0, 0, 1100, 724)), (x0, 0))
o.save(sys.argv[3]); print(o.size)
