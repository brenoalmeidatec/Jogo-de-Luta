"""compor_gemini_raiclaven.py NOME A.jpg B.jpg -> folhas_dupla/e_NOME.png (8 células de 392, escala pelo olho verde do braço)."""
import sys, os
sys.path.insert(0, '/home/user/Jogo-de-Luta/ferramentas')
os.environ['LUTADOR'] = 'raiclaven'
import cv2, numpy as np
from PIL import Image
from recortar_quadros import tira_fundo
CEL, ALTO, CHAO = 392, 560, 540
ALVO = 29.7  # raiz da área da lente verde do braço na folha do ChatGPT (a largura da folha entra no AJUSTE do gerador)

def lente(a):
    hsv = cv2.cvtColor(a[..., :3].astype(np.uint8), cv2.COLOR_RGB2HSV)
    m = ((hsv[..., 0] > 30) & (hsv[..., 0] < 55) & (hsv[..., 1] > 150) & (hsv[..., 2] > 150) & (a[..., 3] > 0)).astype(np.uint8)
    n, l, st, c = cv2.connectedComponentsWithStats(m, 8)
    return np.sqrt(st[1:, cv2.CC_STAT_AREA].max()) if n > 1 else None

def figuras(arq):
    img = Image.open(arq).convert('RGB').crop((0, 0, 1568, 662))
    a = np.array(img)
    branco = (a.min(axis=2) > 200).mean(axis=1) > 0.3  # faixas brancas da borda do print
    a[branco] = (255, 0, 255)
    img = Image.fromarray(a)
    limpa = np.array(tira_fundo(img))
    n, rot, st, cen = cv2.connectedComponentsWithStats((limpa[..., 3] > 0).astype(np.uint8), connectivity=8)
    cel = np.full(n, -1)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 40 and not (st[i, cv2.CC_STAT_HEIGHT] < 8 and st[i, cv2.CC_STAT_WIDTH] > 150):  # sem a faixa branca da borda do print
            cel[i] = min(3, int(cen[i][0] // CEL))
    out = []
    for k in range(4):
        m = cel[rot] == k
        f = np.where(m[..., None], limpa, 0).astype(np.uint8)
        out.append(f)
    return out

nome, a, b = sys.argv[1:4]
# b == '-': uma imagem só (4 quadros) vira 8 células na ordem ORDEM (ida e volta)
ORDEM = [int(c) for c in (sys.argv[4] if len(sys.argv) > 4 else '01233210')]
saida = Image.new('RGB', (8 * CEL, ALTO), (255, 0, 255))
lotes = []
for arq in ((a,) if b == '-' else (a, b)):
    figs = figuras(arq)
    ls = [x for x in (lente(f) for f in figs) if x]
    s = ALVO / float(np.median(ls))
    print(arq.split('/')[-1], 'lente', [round(x, 1) for x in ls], 'escala', round(s, 3))
    lotes.append((figs, s))
vagas = [(lotes[0], k, i) for i, k in enumerate(ORDEM)] if b == '-' else [(lotes[i // 4], i % 4, i) for i in range(8)]
for (figs, s), k, pos in vagas:
        f = figs[k]
        im = Image.fromarray(f)
        bb = im.getchannel('A').getbbox()
        q = im.crop(bb)
        q = q.resize((round(q.width * s), round(q.height * s)), Image.LANCZOS)
        cx = (bb[0] - k * CEL - CEL / 2) * s  # posição na célula, em relação ao centro
        x = round(pos * CEL + CEL / 2 + cx)
        y = CHAO - q.height if q.height < CHAO else 0
        fundo = Image.new('RGB', q.size, (255, 0, 255))
        fundo.paste(q, (0, 0), q.getchannel('A').point(lambda v: 255 if v >= 128 else 0))
        saida.paste(fundo, (x, y), q.getchannel('A').point(lambda v: 255 if v >= 128 else 0))
saida.save(f'/home/user/Jogo-de-Luta/sprites/raiclaven/quadros/folhas_dupla/e_{nome}.png')
print('ok', saida.size)
