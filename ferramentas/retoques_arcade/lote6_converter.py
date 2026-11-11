"""Lote 6 (2026-11-11), registro de como as 17 folhas novas do Pengaró viraram quadros_arcade/<folha>/00..07.png.
Converte folhas_arcade/<folha>.png -> <saida>/<folha>/ (tela 360x260, pés em 180,220, paleta arcade de 15 cores),
separando as 8 figuras por peça ligada (no compasso as figuras 6 e 7 se sobrepõem em coluna), tronco no eixo, base no
chão (só a folha corre guarda a altura dos quadros de voo), com um fator de escala por folha ou por quadro.
uso: lote6_converter.py <saida> folha[:fator[,fator x8]] ...   Imprime altura crua / base de cada figura.
Rodado assim: defesa chute_baixo rasteira bola compasso armada caneta rolamento agarrao:1.03 golaco:0.917 lata provoca
vitoria derrota anda corre recuo; depois lote6_cabelo.py <saida> <saida2> (cabelo que a quantização levou para os
vinhos da pele; sementes em lote6_sementes.json, lido da pasta atual como sementes.json) e cópia para quadros_arcade/.
Rodar quantizar_folha.py nessas folhas desfaz o cabelo e a escala de agarrao e golaco."""
import sys
from pathlib import Path
RAIZ = Path("C:/Dev/Jogo-de-Luta-anatomia")
sys.path.insert(0, str(RAIZ / "ferramentas"))
import numpy as np, cv2
import animar_folha as af
import quantizar_folha as qf
from PIL import Image

def figuras(img):
    limpa = np.array(af.tira_fundo(img))
    larg = limpa.shape[1] / 8
    n, rot, dados, cen = cv2.connectedComponentsWithStats((limpa[..., 3] > 0).astype(np.uint8), connectivity=8)
    cel = np.full(n, -1)
    for i in range(1, n):
        if dados[i, cv2.CC_STAT_AREA] >= 40:
            cel[i] = min(7, int(cen[i][0] // larg))
    out = []
    for i in range(8):
        m = cel[rot] == i
        fig = Image.fromarray(np.where(m[..., None], limpa, 0).astype(np.uint8))
        cx = fig.getchannel("A").getbbox()
        out.append((fig.crop(cx), cx))
    return out

AR = {"corre"}
def main():
    sai = Path(sys.argv[1])
    dados, pal = qf.ler_paleta()
    for item in sys.argv[2:]:
        nome, _, fs = item.partition(":")
        fat = [float(x) for x in fs.split(",")] if fs else [1.0]
        if len(fat) == 1: fat = fat * 8
        img = Image.open(qf.ENTRADA / f"{nome}.png")
        base = af.ESCALA_2172 * 2172 / img.width
        d = sai / nome; d.mkdir(parents=True, exist_ok=True)
        info = []
        figs = figuras(img)
        chao = max(cx[3] for _, cx in figs)
        for i, (q, cx) in enumerate(figs):
            f = base * fat[i]
            g = q.resize((round(q.width * f), round(q.height * f)), Image.LANCZOS)
            tela = Image.new("RGBA", (af.LARG, af.ALT))
            centro = round(af.tronco(q) * f)
            ar = round((chao - cx[3]) * f) if chao - cx[3] > 6 and nome in AR else 0
            tela.paste(g, (180 - centro, 220 - ar - g.height), g)
            qf.para_imagem(qf.quantizar(tela, dados, pal), pal).save(d / f"{i:02d}.png")
            info.append(f"{q.height}/{cx[3]}")
        print(nome, " ".join(info))
main()
