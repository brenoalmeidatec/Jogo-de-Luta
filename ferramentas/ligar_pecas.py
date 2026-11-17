"""Liga no jogo os golpes feitos no boneco de peças (sprites/<lutador>/quadros_pecas_hd/<golpe>/).

Uso:  python3 ferramentas/ligar_pecas.py <lutador> [golpe ...] [--grupo 48000]

O jogo não muda de tempo nem de caixa: só o desenho. Para cada golpe:
- os quadros entram no .sff (indexados na paleta do lutador, grupo `--grupo` + n.º do golpe, índice = quadro);
- a ação do .air é reescrita com os quadros novos. Cada elemento novo cai dentro de um elemento antigo (os novos são
  partidos em toda fronteira antiga), e herda dele as caixas Clsn1/Clsn2, o deslocamento e as flags. Assim o golpe
  acerta no mesmo tick, com a mesma caixa, e o último elemento -1 continua -1;
- no .cns, AnimElem, AnimElemTime e `Anim = N && AnimElemNo(0) = k` que falam dessa ação passam a apontar para o
  elemento novo que começa no mesmo tick (com `ifelse(Anim = N, ...)`, porque o mesmo estado também roda a ação do
  despertado, que não muda);
- o despertado continua igual: cada sprite novo ganha no [RemapPreset despertado] o mesmo destino do sprite antigo que
  estava na tela naquele tick, e as ações da aura (30000 + ação e 40000 + ação, 6 elementos por elemento do corpo) são
  refeitas para a contagem nova.
Rode o robô de luta antes e depois (testar_pengaro.py --linux --lutador <lutador>): o resultado tem que ser igual.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conferir_sff as cs  # noqa: E402
import efeitos  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
EIXO = (540, 660)
RE_EL = re.compile(r"^\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*(.*)$")


# ------------------------------------------------------------------ .air
def bloco(air, n):
    m = re.search(rf"^\[Begin Action {n}\][^\n]*\n(.*?)(?=^\[Begin Action|\Z)", air, re.M | re.S)
    return m


def ler_acao(texto):
    """(cabeça, elementos). Cabeça = linhas antes do 1.º elemento que valem para todos (Clsn2Default...).
    Elemento = dict(g, i, x, y, t, resto, clsn=[linhas Clsn1:/Clsn2: só dele], loop=bool)."""
    cab, els, pend, loop = [], [], [], False
    linhas = texto.splitlines()
    k = 0
    while k < len(linhas):
        l = linhas[k]
        s = l.strip()
        if not s or s.startswith(";"):
            k += 1
            continue
        m = re.match(r"(?i)^(Clsn[12](Default)?)\s*:\s*(\d+)", s)
        if m:
            n = int(m.group(3))
            grupo = [l] + linhas[k + 1:k + 1 + n]
            k += 1 + n
            if m.group(2) and not els:
                cab += grupo
            elif m.group(2):
                pend += grupo  # Default no meio: vale dali em diante; trata como do elemento
            else:
                pend += grupo
            continue
        if s.lower() == "loopstart":
            loop = True
            k += 1
            continue
        m = RE_EL.match(l)
        assert m, f"linha estranha no .air: {l!r}"
        g, i, x, y, t = (int(v) for v in m.groups()[:5])
        els.append(dict(g=g, i=i, x=x, y=y, t=t, resto=m.group(6), clsn=pend, loop=loop))
        pend, loop = [], False
        k += 1
    return cab, els


def clsn_vigente(els, k):
    """Caixas que valem no elemento k: Clsn1/Clsn2 sem Default só valem para o próprio elemento; Default vale dali
    em diante. Devolve as linhas para repetir no elemento novo."""
    out = [l for l in els[k]["clsn"]]
    return out


# ------------------------------------------------------------------ .sff
def paleta_rgb(pal):
    a = np.frombuffer(pal, np.uint8).reshape(-1, 4)[:, :3].astype(int)
    return a


def indexar(img, pal):
    """RGBA → índices da paleta do lutador (0 = transparente; cor mais próxima entre 1..255)."""
    a = np.asarray(img)
    al = a[..., 3] > 127
    rgb = a[..., :3].reshape(-1, 3).astype(int)
    cores, inv = np.unique(rgb, axis=0, return_inverse=True)
    p = pal[1:]
    d = ((cores[:, None, :] - p[None, :, :]) ** 2).sum(-1)
    idx = d.argmin(1) + 1
    px = idx[inv.ravel()].reshape(al.shape).astype(np.uint8)
    px[~al] = 0
    return px


def recortar(img):
    a = np.asarray(img)
    ys, xs = np.nonzero(a[..., 3] > 127)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    return img.crop((x0, y0, x1, y1)), EIXO[0] - x0, EIXO[1] - y0


# ------------------------------------------------------------------ remap
def ler_remap(cns):
    m = re.search(r"^\[RemapPreset despertado\][^\n]*\n(.*?)(?=^\[|\Z)", cns, re.M | re.S)
    mapa = {}
    if not m:
        return mapa
    for l in m.group(1).splitlines():
        r = re.match(r"^\s*(\d+)\s*,\s*(\d+)\s*=\s*(\d+)\s*,\s*(\d+)", l)
        if r:
            mapa[(int(r[1]), int(r[2]))] = (int(r[3]), int(r[4]))
    return mapa


def por_remap(cns, novos):
    m = re.search(r"^\[RemapPreset despertado\][^\n]*\n(.*?)(?=^\[|\Z)", cns, re.M | re.S)
    corpo = m.group(1).rstrip("\n")
    chave = lambda l: tuple(int(v) for v in re.match(r"^\s*(\d+)\s*,\s*(\d+)\s*=", l).groups())
    # tira o que uma ligação anterior pôs para estes sprites e põe de novo
    corpo2 = "\n".join(l for l in corpo.splitlines() if not (re.match(r"^\s*\d+\s*,\s*\d+\s*=", l) and chave(l) in novos))
    linhas = [f"{g},{i} = {a},{b}" for (g, i), (a, b) in sorted(novos.items())]
    return cns[:m.start(1)] + corpo2 + "\n" + "\n".join(linhas) + "\n\n" + cns[m.end(1):].lstrip("\n")


# ------------------------------------------------------------------ .cns
def estados_da_acao(cns, n):
    """Trechos [Statedef ...] que usam a ação n (anim = n no cabeçalho ou ChangeAnim value = n)."""
    partes = [(m.start(), m.group(0)) for m in re.finditer(r"^\[Statedef [^\]]*\]", cns, re.M | re.I)]
    out = []
    for k, (ini, _) in enumerate(partes):
        fim = partes[k + 1][0] if k + 1 < len(partes) else len(cns)
        txt = cns[ini:fim]
        if re.search(rf"(?im)^\s*anim\s*=\s*{n}\s*(;.*)?$", txt) or \
                re.search(rf"(?ims)type\s*=\s*ChangeAnim\b[^\[]*?^\s*value\s*=\s*{n}\s*(;.*)?$", txt):
            out.append((ini, fim))
    return out


def trocar_elem(txt, n, mapa):
    """AnimElem = k → ifelse(Anim = n, AnimElemTime(m), AnimElemTime(k)) = 0; AnimElemTime(k) idem."""
    def t(m):  # uma passada só: o que já foi trocado não é trocado de novo
        if m.group(1) is not None:
            k = int(m.group(1))
            if k not in mapa or mapa[k] == k:
                return m.group(0)
            return f"(ifelse(Anim = {n}, AnimElemTime({mapa[k]}), AnimElemTime({k})) = 0)"
        k = int(m.group(2))
        if k not in mapa or mapa[k] == k:
            return m.group(0)
        return f"ifelse(Anim = {n}, AnimElemTime({mapa[k]}), AnimElemTime({k}))"
    linhas = []
    for l in txt.splitlines(keepends=True):
        if re.match(r"(?i)^\s*trigger", l) and "AnimElem" in l and "parent," not in l:
            corpo, _, coment = l.partition(";")
            corpo = re.sub(r"(?i)\bAnimElem\s*=\s*(\d+)\b(?!\s*,)|\bAnimElemTime\((\d+)\)", t, corpo)
            l = corpo + (";" + coment if coment else "")
        linhas.append(l)
    return "".join(linhas)


def trocar_elemno(cns, n, faixas):
    """`Anim = n && AnimElemNo(0) = k` (ou [a, b]) → faixa nova."""
    def t(m):
        a = int(m.group(2) or m.group(4))
        b = int(m.group(3) or a)
        return f"{m.group(1)}AnimElemNo(0) = [{faixas[a][0]}, {faixas[b][1]}]"
    return re.sub(rf"(Anim[ \t]*=[ \t]*{n}[ \t]*&&[ \t]*)AnimElemNo\(0\)[ \t]*=[ \t]*(?:\[[ \t]*(\d+)[ \t]*,[ \t]*(\d+)[ \t]*\]|(\d+))",
                  t, cns)


# ------------------------------------------------------------------ principal
def ligar(lutador, golpes, grupo_base=48000):
    chars = RAIZ / "chars" / lutador
    spr = RAIZ / "sprites" / lutador / "quadros_pecas_hd"
    air = (chars / f"{lutador}.air").read_text(encoding="utf-8", errors="replace")
    cns = (chars / f"{lutador}.cns").read_text(encoding="utf-8", errors="replace")
    pal, nos, _ = cs.ler(chars / f"{lutador}.sff")
    prgb = paleta_rgb(pal)
    remap = ler_remap(cns)
    todos = sorted(p.name for p in spr.iterdir() if (p / "tempos.json").exists())
    novos_spr, novo_remap, relatorio = {}, {}, []
    for golpe in golpes:
        tempos = json.loads((spr / golpe / "tempos.json").read_text(encoding="utf-8"))
        n = tempos["acao"]
        g_novo = grupo_base + todos.index(golpe)
        m = bloco(air, n)
        assert m, f"ação {n} não existe no .air"
        cab, velhos = ler_acao(m.group(1))
        assert not any(e["loop"] for e in velhos), f"ação {n} tem Loopstart (não tratado)"
        # linha do tempo antiga
        ini_v, t = [], 0
        for e in velhos:
            ini_v.append(t)
            t += max(e["t"], 0)
        infinito = velhos[-1]["t"] < 0
        total_v = t
        # novos: (desenho, ticks); o total novo tem que bater (último -1 conta como o que sobrou)
        novos = [(e["desenho"], e["ticks"]) for e in tempos["elementos"]]
        total_n = sum(tk for _, tk in novos)
        if infinito:
            assert total_n >= total_v, f"{golpe}: novo {total_n} < antigo {total_v}"
        else:
            assert total_n == total_v, f"{golpe}: tempo novo {total_n} != antigo {total_v}"
        # parte os novos em toda fronteira antiga
        partes, t = [], 0
        fronteiras = set(ini_v)
        for d, tk in novos:
            corte = [t] + sorted(b for b in fronteiras if t < b < t + tk) + [t + tk]
            for a, b in zip(corte, corte[1:]):
                partes.append([d, a, b - a])
            t += tk
        if infinito:  # o que passa do fim finito vira o último elemento -1
            while len(partes) > 1 and partes[-1][1] >= total_v and partes[-2][1] >= total_v:
                partes.pop(-2)
            ult = [p for p in partes if p[1] >= total_v]
            if not ult:
                partes.append([partes[-1][0], total_v, -1])
            else:
                partes = [p for p in partes if p[1] < total_v] + [[ult[-1][0], total_v, -1]]
        # elemento antigo de cada parte
        def velho_em(t0):
            k = max(j for j, s in enumerate(ini_v) if s <= t0)
            return k
        mapa, faixas = {}, {}
        linhas = list(cab)
        for j, (d, t0, tk) in enumerate(partes, 1):
            k = velho_em(t0)
            e = velhos[k]
            if t0 == ini_v[k]:
                mapa[k + 1] = j
                linhas += e["clsn"]
            elif e["clsn"]:
                linhas += e["clsn"]  # Clsn sem Default só vale no elemento: repete nas partes
            faixas.setdefault(k + 1, [j, j])[1] = j
            chave = (g_novo, d)
            linhas.append(f"{g_novo},{d}, {e['x']},{e['y']}, {tk}{e['resto']}")
            # despertado: mesmo destino do sprite antigo deste tick
            alvo = remap.get((e["g"], e["i"]))
            if alvo:
                novo_remap.setdefault(chave, alvo)
            novos_spr[chave] = spr / golpe / f"{d:02d}.png"
        assert sorted(mapa) == list(range(1, len(velhos) + 1)), f"{golpe}: fronteira antiga sem elemento novo"
        air = efeitos.por_acao(air, n, "\n".join(linhas))
        # aura do despertado (6 por elemento do corpo)
        for base in (30000, 40000):
            ma = bloco(air, base + n)
            if not ma:
                continue
            _, au = ler_acao(ma.group(1))
            if len(au) != 6 * len(velhos):
                print(f"  aviso: ação {base + n} tem {len(au)} elementos (esperado {6 * len(velhos)}); não mexi")
                continue
            la = []
            for j, (d, t0, tk) in enumerate(partes, 1):
                k = velho_em(t0)
                for e in au[6 * k:6 * k + 6]:
                    la.append(f"{e['g']},{e['i']}, {e['x']},{e['y']}, {e['t']}{e['resto']}")
            air = efeitos.por_acao(air, base + n, "\n".join(la))
        # .cns: AnimElem dos estados que usam a ação
        for ini, fim in reversed(estados_da_acao(cns, n)):
            cns = cns[:ini] + trocar_elem(cns[ini:fim], n, mapa) + cns[fim:]
        cns = trocar_elemno(cns, n, faixas)
        relatorio.append(f"{golpe}: ação {n}, {len(velhos)} → {len(partes)} elementos, grupo {g_novo}")
    # .sff: tira os grupos de ligação anterior destes golpes e põe os novos
    grupos = {k[0] for k in novos_spr}
    rle, png = [], []
    for no in nos:
        if no["g"] in grupos:
            continue
        (png if no.get("png") else rle).append((no["g"], no["i"], no["w"], no["h"], no["x"], no["y"], no["px"]))
    for (g, i), arq in sorted(novos_spr.items()):
        img, ex, ey = recortar(Image.open(arq).convert("RGBA"))
        px = indexar(img, prgb)
        rle.append((g, i, img.width, img.height, int(ex), int(ey), px.tobytes()))
    efeitos.gravar(chars / f"{lutador}.sff", pal, rle, png)
    if novo_remap:
        cns = por_remap(cns, novo_remap)
    (chars / f"{lutador}.air").write_text(air, encoding="utf-8")
    (chars / f"{lutador}.cns").write_text(cns, encoding="utf-8")
    print("\n".join(relatorio))
    print(f"{len(novos_spr)} sprites novos, {len(novo_remap)} remaps do despertado")


def main():
    args = sys.argv[1:]
    grupo = 48000
    if "--grupo" in args:
        k = args.index("--grupo")
        grupo = int(args[k + 1])
        del args[k:k + 2]
    lutador = args.pop(0)
    golpes = args or sorted(p.name for p in (RAIZ / "sprites" / lutador / "quadros_pecas_hd").iterdir()
                            if (p / "tempos.json").exists())
    ligar(lutador, golpes, grupo)


if __name__ == "__main__":
    main()
