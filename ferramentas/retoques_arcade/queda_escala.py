"""Reconverte folhas_arcade/queda.png com um fator de escala por quadro (a folha veio menor que as outras)."""
import sys
from pathlib import Path
RAIZ = Path("C:/Dev/Jogo-de-Luta-anatomia")
sys.path.insert(0, str(RAIZ / "ferramentas"))
import animar_folha as af
import quantizar_folha as qf
from PIL import Image
fatores = [float(x) for x in sys.argv[2].split(",")]
CENTRA = {int(x) for x in sys.argv[3].split(',')} if len(sys.argv) > 3 else set()  # quadros centrados pela caixa (corpo deitado)
sai = Path(sys.argv[1]); sai.mkdir(parents=True, exist_ok=True)
img = Image.open(qf.ENTRADA / "queda.png")
base = af.ESCALA_2172 * 2172 / img.width
dados, pal = qf.ler_paleta()
for i, q in enumerate(af.fatias(af.tira_fundo(img), 8)):
    q = q.crop(q.getchannel("A").getbbox())
    f = base * fatores[i]
    grande = q.resize((round(q.width * f), round(q.height * f)), Image.LANCZOS)
    tela = Image.new("RGBA", (af.LARG, af.ALT))
    centro = grande.width // 2 if i in CENTRA else round(af.tronco(q) * f)
    tela.paste(grande, (af.PIVO[0] + af.DESLOCA[0] - centro, af.PIVO[1] + af.DESLOCA[1] - grande.height), grande)
    qf.para_imagem(qf.quantizar(tela, dados, pal), pal).save(sai / f"{i:02d}.png")
