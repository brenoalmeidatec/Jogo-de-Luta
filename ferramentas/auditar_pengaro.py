#!/usr/bin/env python3
"""Pente fino nos quadros do Pengaró, sem abrir o jogo.

  python ferramentas/auditar_pengaro.py [pasta_de_saida]

Monta os sprites e as animações como o gerador (sem gravar nada) e mede cada quadro de cada ação:
pés fora do chão, corpo escorregando ou pulando de lugar, tamanho mudando de um quadro para o outro, figura cortada na
borda, sujeira solta, magenta que sobrou do fundo, arte antiga (feita girando as 9 poses) e quadro endiabrado sem par ou
desalinhado. Escreve auditoria.txt e uma folha de contato por ação suspeita.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_pengaro as g  # noqa: E402

NOVOS = ("f_", "m_", "q_soco", "q_ginga_fluida", "q_anda_fluida", "ginga_endiabrada", "e_", "endiabrado_",
         "balao_", "fx_", "bola", "bolao", "quica", "retrato", "chuva", "despertado_")
NO_AR = set(range(40, 48)) | set(range(600, 700)) | set(range(5030, 5100)) | {105, 122, 132, 142, 152, 1200, 1201}
LIVRES = {1005, 1006, 3005, 3006, 3010, 3011}  # projéteis e efeitos


def medir(img):
    a = np.asarray(img.convert("RGBA"))
    alfa = a[..., 3] >= 128
    if not alfa.any():
        return None
    ys, xs = np.nonzero(alfa)
    base, topo = ys.max(), ys.min()
    magenta = (alfa & (a[..., 0] > 180) & (a[..., 2] > 180) & (a[..., 1] < 90)).sum()
    return {"caixa": (xs.min(), topo, xs.max(), base), "pes_x": centro_tronco(alfa, topo, base), "altura": base - topo,
            "magenta": int(magenta), "sujeira": sujeira(alfa)}


def centro_tronco(alfa, topo, base):
    """Meio do maior trecho cheio de cada linha, do peito à barriga: só anda se o corpo inteiro andar."""
    meios = []
    for y in range(topo + int((base - topo) * 0.3), topo + max(1, int((base - topo) * 0.6))):
        linha = np.flatnonzero(alfa[y])
        if not len(linha):
            continue
        quebras = np.flatnonzero(np.diff(linha) > 1)
        inicios, fins = np.r_[linha[0], linha[quebras + 1]], np.r_[linha[quebras], linha[-1]]
        k = int(np.argmax(fins - inicios))
        meios.append((inicios[k] + fins[k]) / 2)
    return float(np.median(meios)) if meios else 0.0


def sujeira(alfa):
    """Pedacinhos soltos longe do corpo (fumaça cortada, pixel perdido)."""
    import cv2
    n, rot, dados, _ = cv2.connectedComponentsWithStats(alfa.astype(np.uint8), connectivity=8)
    if n <= 2:
        return 0
    maior = 1 + int(np.argmax(dados[1:, cv2.CC_STAT_AREA]))
    x0, y0 = dados[maior, 0], dados[maior, 1]
    x1, y1 = x0 + dados[maior, 2], y0 + dados[maior, 3]
    soltos = 0
    for i in range(1, n):
        if i == maior or dados[i, cv2.CC_STAT_AREA] >= 25:
            continue
        cx, cy = dados[i, 0] + dados[i, 2] / 2, dados[i, 1] + dados[i, 3] / 2
        if cx < x0 - 4 or cx > x1 + 4 or cy < y0 - 4 or cy > y1 + 4:
            soltos += 1
    return soltos


def ler_air(txt):
    acoes, atual = {}, None
    for linha in txt.splitlines():
        m = re.match(r"\[Begin Action (\d+)\]", linha)
        if m:
            atual = int(m[1])
            acoes[atual] = []
        elif atual is not None and re.match(r"-?\d+,\s*-?\d+,", linha):
            p = [x.strip() for x in linha.split(",")]
            acoes[atual].append((int(p[0]), int(p[1]), int(p[4])))
    return acoes


def main():
    saida = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    saida.mkdir(parents=True, exist_ok=True)
    s = g.montar_sprites(retrato=g.RAIZ / "sprites/pengaro-selecao-kof.png")
    faiscas = g.carregar_faiscas(s)
    a = g.montar_air(s, faiscas, arte_despertada=g.arte_endiabrada(s))
    preset = g.preset_despertado(s)
    nomes = {cod: nome for nome, cod in s.codigos.items()}
    imagens = {(gr, ind): (img, ex, ey) for gr, ind, img, ex, ey in s.lista}
    remap = {(int(x), int(y)): (int(z), int(w)) for x, y, z, w in re.findall(r"(\d+),(\d+) = (\d+),(\d+)", preset)}
    acoes = ler_air("\n".join(a.txt))
    cache = {}

    def m(cod):
        if cod not in cache:
            img, ex, ey = imagens[cod]
            r = medir(img)
            if r:
                r["chao"] = r["caixa"][3] - ey
                r["borda"] = r["caixa"][0] <= 0 or r["caixa"][1] <= 0 or r["caixa"][2] >= img.width - 1
            cache[cod] = r
        return cache[cod]

    problemas = defaultdict(list)
    antigos = defaultdict(set)
    for n, quadros in sorted(acoes.items()):
        if n >= 9000 or n in LIVRES:
            continue
        anterior = None
        for k, (gr, ind, ticks) in enumerate(quadros):
            cod = (gr, ind)
            nome = nomes.get(cod, "?")
            r = m(cod)
            if r is None:
                problemas[n].append(f"q{k} {nome}: sprite vazio")
                continue
            if not nome.startswith(NOVOS):
                antigos[n].add(nome)
            if n not in NO_AR and abs(r["chao"]) > 4 and not nome.startswith(("f_queda", "m_queda", "f_levanta", "m_levanta")):
                problemas[n].append(f"q{k} {nome}: pés {r['chao']:+d} px do chão")
            if r["borda"]:
                problemas[n].append(f"q{k} {nome}: cortado na borda da tela")
            if r["magenta"] > 5:
                problemas[n].append(f"q{k} {nome}: {r['magenta']} px de magenta do fundo")
            if r["sujeira"]:
                problemas[n].append(f"q{k} {nome}: {r['sujeira']} pedaços soltos")
            if anterior and ticks > 0:
                ra, na = anterior
                salto = abs(r["pes_x"] - ra["pes_x"])
                if salto > 12 and ticks <= 3 and n not in NO_AR:
                    problemas[n].append(f"q{k} {na} -> {nome}: corpo pula {salto:.0f} px para o lado")
                razao = r["altura"] / max(1, ra["altura"])
                if (razao < 0.75 or razao > 1.33) and n not in NO_AR:
                    problemas[n].append(f"q{k} {na} -> {nome}: altura muda {ra['altura']} -> {r['altura']}")
            anterior = (r, nome)
            destino = remap.get(cod)
            if destino and not nomes.get(cod, "").startswith(("balao_", "fx_")):
                rd = m(destino)
                if rd and (abs(rd["pes_x"] - r["pes_x"]) > 12 or abs(rd["chao"] - r["chao"]) > 6):
                    problemas[n].append(f"q{k} {nome}: endiabrado desalinhado ({rd['pes_x'] - r['pes_x']:+.0f} x, "
                                        f"{rd['chao'] - r['chao']:+d} y)")

    linhas = [f"{len(acoes)} ações, {len(cache)} sprites medidos", ""]
    pontuacao = sorted(problemas, key=lambda n: -len(problemas[n]))
    for n in pontuacao:
        linhas.append(f"ação {n}: {len(problemas[n])} problemas")
        vistos = set()
        for p in problemas[n]:
            chave = p.split(": ", 1)[1].split(" (")[0]
            if chave not in vistos or len(vistos) < 6:
                linhas.append("   " + p)
                vistos.add(chave)
    linhas += ["", "ações com arte antiga (feita girando as 9 poses):"]
    for n in sorted(antigos):
        linhas.append(f"   {n}: {', '.join(sorted(antigos[n]))}")
    (saida / "auditoria.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")

    for n in pontuacao[:40] + sorted(antigos)[:20]:
        quadros = acoes[n]
        passo = max(1, len(quadros) // 16)
        mostra = quadros[::passo][:16]
        folha = Image.new("RGB", (len(mostra) * 140, 2 * 130 + 16), (24, 22, 30))
        d = ImageDraw.Draw(folha)
        d.text((4, 2), f"ação {n} ({len(quadros)} elementos)", fill="white")
        for j, (gr, ind, _) in enumerate(mostra):
            for linha, cod in enumerate(((gr, ind), remap.get((gr, ind)))):
                if not cod or cod not in imagens:
                    continue
                img, ex, ey = imagens[cod]
                t = Image.new("RGBA", (360, 260), (58, 46, 66, 255))
                t.alpha_composite(img, (180 - ex, 220 - ey))
                ImageDraw.Draw(t).line((40, 220, 320, 220), fill=(140, 140, 150, 255))
                folha.paste(t.crop((40, 50, 320, 250)).resize((140, 100)).convert("RGB"), (j * 140, 16 + linha * 130))
                ImageDraw.Draw(folha).text((j * 140 + 2, 16 + linha * 130 + 102), nomes.get(cod, "?")[:20], fill="#ccc")
        folha.save(saida / f"acao_{n}.png")
    print("\n".join(linhas[:60]))


if __name__ == "__main__":
    main()
