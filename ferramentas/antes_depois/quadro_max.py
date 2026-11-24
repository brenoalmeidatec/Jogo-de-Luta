"""quadro_max.py PASTA SAIDA.png acao ... : de cada par_<acao>.mp4 pega o instante em que antes e depois mais diferem."""
import subprocess, sys
import numpy as np
from PIL import Image
pasta, saida, acoes = sys.argv[1], sys.argv[2], sys.argv[3:]
linhas = []
for a in acoes:
    f = f"{pasta}/par_{a}.mp4"
    w, h = map(int, subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", f]).decode().split(","))
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-t", "2.5", "-i", f, "-vf", "fps=20", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    meio = (w - 8) // 2 + 4
    corpo = fr[:, 60:h - 70]
    dif = [np.abs(q[:, 4:meio - 4].astype(int)[:, :min(meio - 8, w - meio - 4)] - q[:, meio + 4:].astype(int)[:, :min(meio - 8, w - meio - 4)]).sum() for q in corpo]
    linhas.append(Image.fromarray(fr[int(np.argmax(dif))]))
alt = 420
linhas = [l.resize((int(l.width * alt / l.height), alt)) for l in linhas]
W = max(l.width for l in linhas)
col = 2 if len(linhas) > 2 else 1
rows = (len(linhas) + col - 1) // col
o = Image.new("RGB", (W * col, alt * rows))
for k, l in enumerate(linhas):
    o.paste(l, ((k % col) * W + (W - l.width) // 2, (k // col) * alt))
o.save(saida); print(saida, o.size)
