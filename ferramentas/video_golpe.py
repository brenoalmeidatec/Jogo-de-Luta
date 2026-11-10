#!/usr/bin/env python3
"""Vídeo curto de cada golpe, montado tick a tick do SFF e do AIR finais, com análise quadro a quadro.

  python ferramentas/video_golpe.py PASTA 200 210 1100      (ações escolhidas)
  python ferramentas/video_golpe.py PASTA --suspeitas       (só as que a análise acusar)
  python ferramentas/video_golpe.py PASTA --todas
  opções: --segundos 6 (5 a 10), --escala 2, --hazaki, --lutador gutto, --sff-de VITIMA (ação de arremesso
          desenhada com o SFF da vítima, como o ChangeAnim2 faz), --despertado (aplica o [RemapPreset despertado]),
          --sem-video

Não abre o jogo: lê chars/<lutador>/<lutador>.sff e .air e mostra cada tick como o motor mostraria a animação
(60 ticks por segundo, com o deslocamento x,y e o espelhamento de cada elemento). O movimento do corpo pela tela
(velocidade do CNS) não entra: para isso use ferramentas/filmar_luta.py. Para cada ação grava:

  acao_N.mp4      vídeo de 5 a 10 s a 60 fps, repetindo o golpe (precisa do ffmpeg no PATH)
  acao_N.png      tira com TODOS os ticks, numerados; borda vermelha onde a análise acusou algo
  relatorio.md    tabela por ação e a lista de cada tick acusado

A análise compara cada desenho com o anterior, no lugar em que ele aparece na tela:
  parado   o mesmo desenho fica mais de 2 ticks (regra 7: movimento contínuo); nas ações de pose segurada do Pengaró
           (gerar_pengaro.SECO: golpes, reações, defesa, queda) o limite é 9 ticks
  salto    a silhueta muda demais de um tick para o outro (1 - IoU acima de 0,45): pose que estala
  pés      o pé apoiado sobe ou afunda mais de 4 px entre dois desenhos no chão
  deslize  o centro do corpo anda mais de 10 px de um tick para o outro
  tamanho  a altura da figura muda mais de 15% de um tick para o outro
Ação com loop é conferida também na emenda (último quadro -> quadro do loop).
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verificar_pengaro as v  # noqa: E402

LIMITE_PARADO = 2
LIMITE_SECO = 9  # pose segurada (regra 7): cada pose de recuperação fica 4 a 9 ticks
LUTADOR = "pengaro"
LIMITE_SALTO = 0.45
LIMITE_PES = 4
LIMITE_DESLIZE = 10
LIMITE_TAMANHO = 0.15
TELA = (420, 300)
CHAO = 250  # y do chão na tela de trabalho
FUNDO = (40, 52, 110)
NO_AR = set(range(40, 48)) | set(range(600, 700)) | set(range(5030, 5100)) | {105, 122, 132, 142, 152}
ESPERA_FIM = 30  # ticks mostrados de um elemento com tempo -1 (parado para sempre)


def ler_air(pasta, nome):
    """{ação: (elementos, loopstart)}; elemento = (grupo, índice, x, y, ticks, flip)."""
    acoes, atual = {}, None
    for linha in (pasta / f"{nome}.air").read_text(encoding="utf-8").splitlines():
        linha = linha.split(";")[0].strip()
        m = re.match(r"\[Begin Action (\d+)\]", linha, re.I)
        if m:
            atual = int(m.group(1))
            acoes[atual] = ([], None)
        elif atual is not None and linha.lower().startswith("loopstart"):
            acoes[atual] = (acoes[atual][0], len(acoes[atual][0]))
        elif atual is not None and re.match(r"-?\d+\s*,\s*-?\d+\s*,", linha):
            p = [x.strip() for x in linha.split(",")]
            flip = p[5].upper() if len(p) > 5 else ""
            acoes[atual][0].append((int(p[0]), int(p[1]), int(p[2]), int(p[3]), int(p[4]), flip))
    return acoes


class Desenhos:
    def __init__(self, sprites, pal):
        self.sprites = sprites
        self.pal = np.frombuffer(pal, np.uint8).reshape(256, 4)[:, :3]
        self.cache = {}

    def rgba(self, chave, flip):
        k = (chave, flip)
        if k not in self.cache:
            w, h, ax, ay, px = self.sprites[chave]
            idx = np.frombuffer(px, np.uint8).reshape(h, w)
            img = np.zeros((h, w, 4), np.uint8)
            img[..., :3] = self.pal[idx]
            img[..., 3] = np.where(idx == 0, 0, 255)
            if "H" in flip:
                img, ax = img[:, ::-1], w - 1 - ax
            if "V" in flip:
                img, ay = img[::-1], h - 1 - ay
            self.cache[k] = (Image.fromarray(img, "RGBA"), ax, ay)
        return self.cache[k]


def ticks_da_acao(elementos, loop):
    """Lista de (índice do elemento, tick dentro dele) para uma passada; e a emenda do loop, se houver."""
    seq = []
    for i, el in enumerate(elementos):
        t = el[4] if el[4] > 0 else ESPERA_FIM
        seq += [(i, k) for k in range(t)]
    return seq


def montar(desenhos, el):
    tela = Image.new("RGBA", TELA, FUNDO + (255,))
    if (el[0], el[1]) not in desenhos.sprites:
        return tela, None
    img, ax, ay = desenhos.rgba((el[0], el[1]), el[5])
    tela.alpha_composite(img, (TELA[0] // 2 - ax + el[2], CHAO - ay + el[3]))
    return tela, mascara(img, TELA[0] // 2 - ax + el[2], CHAO - ay + el[3])


def mascara(img, x, y):
    m = np.zeros((TELA[1], TELA[0]), bool)
    a = np.asarray(img)[..., 3] > 127
    h, w = a.shape
    x0, y0, x1, y1 = max(0, x), max(0, y), min(TELA[0], x + w), min(TELA[1], y + h)
    if x1 > x0 and y1 > y0:
        m[y0:y1, x0:x1] = a[y0 - y:y1 - y, x0 - x:x1 - x]
    return m


def medida(m):
    if m is None or not m.any():
        return None
    ys, xs = np.nonzero(m)
    return {"base": int(ys.max()), "topo": int(ys.min()), "cx": float(xs.mean()), "alt": int(ys.max() - ys.min())}


def comparar(acao, a, b, ma, mb, tick):
    """Problemas na troca de desenho a -> b (máscaras ma, mb) no tick indicado."""
    probs = []
    if ma is None or mb is None:
        return probs
    uniao = (ma | mb).sum()
    if uniao:
        dif = 1 - (ma & mb).sum() / uniao
        if dif > LIMITE_SALTO:
            probs.append(f"salto {dif:.2f}")
    if a and b:
        no_chao = acao not in NO_AR and abs(a["base"] - CHAO) <= 6 and abs(b["base"] - CHAO) <= 6
        if no_chao and abs(a["base"] - b["base"]) > LIMITE_PES:
            probs.append(f"pés {b['base'] - a['base']:+d} px")
        if abs(a["cx"] - b["cx"]) > LIMITE_DESLIZE:
            probs.append(f"deslize {b['cx'] - a['cx']:+.0f} px")
        if a["alt"] and abs(b["alt"] - a["alt"]) / a["alt"] > LIMITE_TAMANHO:
            probs.append(f"tamanho {a['alt']}->{b['alt']}")
    return probs


def analisar(acao, elementos, loop, desenhos):
    seq = ticks_da_acao(elementos, loop)
    quadros, acusados = [], {}
    ant_el = ant_m = ant_med = None
    parado = 0
    limite = LIMITE_PARADO
    if LUTADOR == "pengaro":
        from gerar_pengaro import SECO
        limite = LIMITE_SECO if SECO(acao) else LIMITE_PARADO
    for n, (i, _) in enumerate(seq):
        el = elementos[i]
        tela, m = montar(desenhos, el)
        quadros.append(tela)
        mesmo = ant_el is not None and (el[0], el[1], el[2], el[3], el[5]) == ant_el
        if mesmo:
            parado += 1
            if parado == limite + 1 and el[4] > 0:
                acusados.setdefault(n, []).append(f"parado {sum(1 for j, _ in seq if j == i)}t")
        else:
            parado = 1
            med = medida(m)
            if ant_el is not None:
                for p in comparar(acao, ant_med, med, ant_m, m, n):
                    acusados.setdefault(n, []).append(p)
            ant_m, ant_med = m, med
        ant_el = (el[0], el[1], el[2], el[3], el[5])
    if loop is not None and elementos:
        tela, m = montar(desenhos, elementos[loop])
        for p in comparar(acao, ant_med, medida(m), ant_m, m, len(seq)):
            acusados.setdefault(len(seq) - 1, []).append(f"emenda do loop: {p}")
    return quadros, acusados


def recortar(quadros):
    """Caixa comum a todos os quadros (com margem), para o vídeo não ficar cheio de fundo."""
    caixa = None
    for q in quadros:
        b = Image.fromarray((np.asarray(q)[..., :3] != FUNDO).any(axis=2).astype(np.uint8) * 255).getbbox()
        if b:
            caixa = b if caixa is None else (min(caixa[0], b[0]), min(caixa[1], b[1]), max(caixa[2], b[2]), max(caixa[3], b[3]))
    if caixa is None:
        return (0, 0) + TELA
    m = 12
    x0, y0, x1, y1 = max(0, caixa[0] - m), max(0, caixa[1] - m), min(TELA[0], caixa[2] + m), min(TELA[1], CHAO + 8)
    return x0, y0, x1 + (x1 - x0) % 2, y1 + (y1 - y0) % 2


def tira(quadros, acusados, caixa, destino, colunas=12):
    w, h = caixa[2] - caixa[0], caixa[3] - caixa[1]
    linhas = (len(quadros) + colunas - 1) // colunas
    folha = Image.new("RGB", (colunas * (w + 4), linhas * (h + 16)), (20, 20, 20))
    d = ImageDraw.Draw(folha)
    for n, q in enumerate(quadros):
        x, y = (n % colunas) * (w + 4), (n // colunas) * (h + 16)
        folha.paste(q.crop(caixa).convert("RGB"), (x + 2, y + 14))
        cor = (255, 60, 60) if n in acusados else (200, 200, 200)
        d.text((x + 3, y + 1), f"t{n}", fill=cor)
        if n in acusados:
            d.rectangle((x + 1, y + 13, x + w + 2, y + h + 14), outline=cor, width=2)
    folha.save(destino)


def video(quadros, caixa, destino, segundos, escala):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return False
    w, h = (caixa[2] - caixa[0]) * escala, (caixa[3] - caixa[1]) * escala
    voltas = max(1, round(segundos * 60 / max(1, len(quadros) + 20)))
    proc = subprocess.Popen([ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                             "-r", "60", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", str(destino)],
                            stdin=subprocess.PIPE)
    pausa = quadros[-1].crop(caixa).convert("RGB").resize((w, h), Image.NEAREST).tobytes()
    corpo = [q.crop(caixa).convert("RGB").resize((w, h), Image.NEAREST).tobytes() for q in quadros]
    for _ in range(voltas):
        for b in corpo:
            proc.stdin.write(b)
        for _ in range(20):  # 1/3 s parado no fim de cada volta, para ver onde o golpe termina
            proc.stdin.write(pausa)
    proc.stdin.close()
    return proc.wait() == 0


def main():
    args = [a for a in sys.argv[1:]]
    if not args or args[0].startswith("-"):
        sys.exit(__doc__)
    saida = Path(args.pop(0))
    saida.mkdir(parents=True, exist_ok=True)

    def opcao(nome, padrao):
        if nome in args:
            i = args.index(nome)
            valor = args[i + 1]
            del args[i:i + 2]
            return type(padrao)(valor)
        return padrao

    segundos = min(10, max(5, opcao("--segundos", 6)))
    escala = opcao("--escala", 2)
    lutador = opcao("--lutador", "")
    sff_de = opcao("--sff-de", "")
    flags = {a for a in args if a.startswith("--")}
    pedidas = [int(a) for a in args if not a.startswith("--")]

    v.PERSONAGEM = lutador or ("hazaki" if "--hazaki" in flags else "pengaro")
    global LUTADOR
    LUTADOR = v.PERSONAGEM
    chars = Path(__file__).resolve().parent.parent / "chars"
    # --sff-de VITIMA: arremesso. O ChangeAnim2 desenha a vítima com o SFF dela e as ações do arremessador.
    dono, v.PERSONAGEM = v.PERSONAGEM, sff_de or v.PERSONAGEM
    v.PASTA = chars / v.PERSONAGEM
    sprites, pal = v.ler_sff()
    v.PERSONAGEM, v.PASTA = dono, chars / dono
    if "--despertado" in flags:
        # Como o RemapSprite do Despertar: cada desenho vira o destino do [RemapPreset despertado] do dono do SFF.
        cns = (chars / (sff_de or dono) / f"{sff_de or dono}.cns").read_text(encoding="utf-8")
        bloco = re.search(r"^\[RemapPreset despertado\]\n(.*?)(?=^\[)", cns, re.M | re.S)
        assert bloco, "sem [RemapPreset despertado] no .cns"
        trocas = re.findall(r"^(\d+),\s*(\d+)\s*=\s*(\d+),\s*(\d+)", bloco.group(1), re.M)
        originais, sprites = sprites, dict(sprites)
        for g, i, g2, i2 in trocas:
            if (int(g2), int(i2)) in originais:  # linha morta (origem nunca desenhada): o destino foi podado do .sff
                sprites[(int(g), int(i))] = originais[(int(g2), int(i2))]
        print(f"{len(trocas)} desenhos trocados pelo RemapPreset despertado")
    desenhos = Desenhos(sprites, pal)
    acoes = ler_air(v.PASTA, v.PERSONAGEM)
    alvo = pedidas or sorted(acoes)

    linhas, detalhes, gravados = [], [], 0
    for n in alvo:
        if n not in acoes or not acoes[n][0]:
            print(f"ação {n} não existe")
            continue
        elementos, loop = acoes[n]
        quadros, acusados = analisar(n, elementos, loop, desenhos)
        desenhos_unicos = len({(e[0], e[1]) for e in elementos})
        resumo = {}
        for ps in acusados.values():
            for p in ps:
                k = p.split()[0] if not p.startswith("emenda") else "emenda"
                resumo[k] = resumo.get(k, 0) + 1
        linhas.append(f"| {n} | {len(quadros)} | {desenhos_unicos} | {len(acusados)} | "
                      + ", ".join(f"{k} {c}" for k, c in sorted(resumo.items())) + " |")
        if acusados:
            detalhes.append(f"\n### Ação {n}\n")
            detalhes += [f"- t{t}: " + "; ".join(ps) for t, ps in sorted(acusados.items())]
        if "--suspeitas" in flags and not acusados:
            continue
        caixa = recortar(quadros)
        tira(quadros, acusados, caixa, saida / f"acao_{n}.png")
        if "--sem-video" not in flags and video(quadros, caixa, saida / f"acao_{n}.mp4", segundos, escala):
            gravados += 1

    (saida / "relatorio.md").write_text(
        f"# Análise quadro a quadro ({v.PERSONAGEM})\n\n"
        "Limites: parado > 2 ticks (pose segurada do Pengaró: > 9), salto 1-IoU > 0,45, pés > 4 px, deslize > 10 px, tamanho > 15%.\n\n"
        "| Ação | Ticks | Desenhos | Ticks acusados | Tipos |\n|---|---|---|---|---|\n"
        + "\n".join(linhas) + "\n\n## Ticks acusados\n" + "\n".join(detalhes) + "\n", encoding="utf-8")
    acusadas = sum(1 for l in linhas if not l.split("|")[4].strip() == "0")
    print(f"{len(linhas)} ações analisadas, {acusadas} com algo acusado, {gravados} vídeos em {saida}")


if __name__ == "__main__":
    main()
