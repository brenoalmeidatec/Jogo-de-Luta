"""Pinta com a cor do fundo (a do canto) as linhas e colunas da borda que o gerador de imagem às vezes entrega com
um risco claro (a b_soco do CK boss veio com a última linha rosa-clara, o que faz a folha "encostar na borda").

    python ferramentas/retoques_arcade/boss_borda.py ENTRADA SAIDA
"""
import sys, numpy as np
from PIL import Image
a = np.array(Image.open(sys.argv[1]).convert('RGB')); c = a[3, 3].copy(); n = 0
def ruim(v):
    d = np.abs(v.astype(int) - c.astype(int)).max(-1)
    return (d > 60).mean() > 0.5
for y in [0, 1, a.shape[0]-2, a.shape[0]-1]:
    if ruim(a[y]): a[y] = c; n += 1
for x in [0, 1, a.shape[1]-2, a.shape[1]-1]:
    if ruim(a[:, x]): a[:, x] = c; n += 1
Image.fromarray(a).save(sys.argv[2]); print('linhas pintadas', n)
