import sys
from pathlib import Path
import numpy as np
from PIL import Image
PS, PM, GE, CE, CL = (0x8A,0x32,0x1C), (0xDF,0x7E,0x3F), (0x5F,0x1A,0x14), (0x33,0x2C,0x20), (0x75,0x6C,0x4E)
# quadro -> x0 da grade, lista de (linha_ini, linha_fim, col_ini, col_fim) relativos a x0 (inclusive)
REG = {2: (147, [(109, 123, 0, 8), (124, 126, 0, 4), (107, 110, 10, 15)]),
       3: (129, [(106, 113, 0, 6), (114, 120, 0, 8), (121, 127, 0, 5)]),
       4: (129, [(106, 114, 0, 6), (115, 120, 0, 7), (121, 127, 0, 5), (123, 124, 11, 11)])}
ent, sai = Path(sys.argv[1]), Path(sys.argv[2])
for q, (x0, regs) in REG.items():
    a = np.array(Image.open(ent / f"{q:02d}.png").convert("RGBA"))
    m = np.zeros(a.shape[:2], bool)
    for y1, y2, c1, c2 in regs:
        m[y1:y2 + 1, x0 + c1:x0 + c2 + 1] = True
    eh = lambda c: (a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & (a[..., 3] > 0) & m
    escuro, medio = eh(PS) | eh(GE), eh(PM)
    a[escuro] = CE + (255,)
    a[medio] = CL + (255,)
    Image.fromarray(a).save(sai / f"{q:02d}.png")
    print(q, int(escuro.sum()), int(medio.sum()))
