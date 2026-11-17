"""Compara os ticks de cada ação com a versão da mugen, mede a regra de 2 ticks e monta GIFs a partir do SFF final."""
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

repo = Path(sys.argv[1])
saida = Path(sys.argv[2])
saida.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(repo / "ferramentas"))
import verificar_pengaro as v


def ler(texto):
    acoes, atual = {}, None
    for linha in texto.splitlines():
        linha = linha.split(";")[0].strip()
        m = re.match(r"\[Begin Action (\d+)\]", linha)
        if m:
            atual = int(m[1])
            acoes[atual] = []
        elif re.match(r"-?\d+,\s*-?\d+,", linha):
            p = [x.strip() for x in linha.split(",")]
            acoes[atual].append((int(p[0]), int(p[1]), int(p[4])))
    return acoes


novo = ler((repo / "chars/pengaro/pengaro.air").read_text(encoding="utf-8"))
velho = ler(subprocess.check_output(["git", "show", "origin/mugen:chars/pengaro/pengaro.air"], cwd=repo, text=True, encoding="utf-8"))
total = lambda q: sum(t for *_, t in q if t > 0)
mudou = [(n, total(velho[n]), total(novo[n])) for n in sorted(velho) if n in novo and total(velho[n]) != total(novo[n])]
print("ações com tempo diferente:", mudou)
longos = {n: max(t for *_, t in q) for n, q in novo.items() if n < 10000 and max(t for *_, t in q) > 2}
print("ações com desenho acima de 2 ticks:", len(longos), "de", len([n for n in novo if n < 10000]))
print(sorted(longos.items())[:40])
for n in (0, 20, 200, 210, 240, 260, 440, 1000, 1100, 2000, 3000):
    print(n, "elementos", len(velho.get(n, [])), "->", len(novo[n]), "ticks", total(novo[n]))

v.PERSONAGEM = "pengaro"
v.PASTA = repo / "chars/pengaro"
sprites, pal = v.ler_sff()
for n, nome, passo in ((2000, "despertar", 2), (240, "chute_forte", 1), (9203, "ginga_endiabrada", 1), (0, "ginga", 1), (10240, "chute_endiabrado", 1)):
    quadros = []
    for g, i, t in novo[n]:
        s = sprites[(g, i)]
        tela = Image.new("RGBA", (360, 260), (58, 46, 66, 255))
        tela.alpha_composite(v.imagem(s, pal), (max(0, 180 - s[2]), max(0, 220 - s[3])))
        quadros.append(tela.crop((60, 40, 320, 240)).resize((520, 400), Image.NEAREST).convert("P", palette=Image.ADAPTIVE))
    quadros = quadros[::passo]
    quadros[0].save(saida / f"{nome}.gif", save_all=True, append_images=quadros[1:], duration=20 * passo, loop=0)
    if n == 2000:
        k = 12
        tira = Image.new("RGB", (k * 200, 230))
        for j in range(k):
            tira.paste(quadros[j * (len(quadros) - 1) // (k - 1)].convert("RGB").resize((200, 154)), (j * 200, 38))
        tira.save(saida / "despertar_tira.png")
print("gifs prontos")
