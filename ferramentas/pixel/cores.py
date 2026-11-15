"""Régua de cor: compara as cores de cada quadro com as do parado da mesma forma (#51, "cor mudando entre os quadros").

O parado vira K grupos de cor (k-means no espaço Lab: pele, pele na sombra, roupa, cabelo...). Cada quadro tem os pixels
postos no grupo mais perto; para cada grupo com pixel suficiente, a régua mede quanto a média do quadro foge da média do
parado (delta E). Pele mais vermelha, roupa mais clara, detalhe que trocou de tom: tudo aparece como deriva do grupo.

  deriva   média ponderada do delta E dos grupos (0 = mesmas cores do parado; acima de LIMITE_DERIVA = aviso)
  fora     fração dos pixels longe de qualquer cor do parado (cor nova: efeito, objeto, ou mancha)
  corrigir(a) puxa cada grupo de volta para a média do parado (troca de tom), sem mexer em forma, pose nem caixa.
"""
import numpy as np
import cv2

from quadros import abrir

K = 14
LIMITE_DERIVA = 6.0
LONGE = 22.0


def lab(rgb):
    return cv2.cvtColor(np.ascontiguousarray(rgb.reshape(-1, 1, 3).astype(np.uint8)), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32) * np.array([100 / 255, 1, 1], np.float32) - np.array([0, 128, 128], np.float32)


def rgb_de_lab(L):
    x = (L + np.array([0, 128, 128], np.float32)) / np.array([100 / 255, 1, 1], np.float32)
    x = np.clip(x, 0, 255).astype(np.uint8).reshape(-1, 1, 3)
    return cv2.cvtColor(x, cv2.COLOR_LAB2RGB).reshape(-1, 3)


class RefCor:
    def __init__(self, end, k=K):
        from quadros import PARADO
        if isinstance(end, (list, tuple)):  # lista de arquivos do parado
            qs = list(end)
        else:  # a pose parada passada direto vale como ela mesma (ginga_endiabrada não começa com e_)
            qs = (end if end.acao in PARADO.values() else end.parado()).quadros()
        px = np.concatenate([abrir(p)[..., :3][abrir(p)[..., 3] > 0] for p in qs])
        rng = np.random.default_rng(0)
        if len(px) > 60000:
            px = px[rng.choice(len(px), 60000, replace=False)]
        L = lab(px)
        crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.2)
        _, rot, cen = cv2.kmeans(L, k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
        self.cen = cen
        self.peso = np.bincount(rot.ravel(), minlength=k) / len(rot)
        # cor do parado mais perto de cada pixel (para medir o "fora")
        self.todas = np.unique(L.round(1), axis=0)

    def grupos(self, L):
        d = ((L[:, None, :] - self.cen[None]) ** 2).sum(-1)
        g = d.argmin(1)
        return g, np.sqrt(d[np.arange(len(L)), g])

    def medir(self, a):
        m = a[..., 3] > 0
        if not m.any():
            return None
        L = lab(a[..., :3][m])
        g, dist = self.grupos(L)
        n = len(L)
        der, pes = [], []
        for j in range(len(self.cen)):
            s = g == j
            if s.sum() < max(30, 0.02 * n):
                continue
            der.append(float(np.linalg.norm(L[s].mean(0) - self.cen[j])))
            pes.append(s.sum())
        deriva = float(np.average(der, weights=pes)) if der else 0.0
        return {"deriva": deriva, "fora": float((dist > LONGE).mean()), "grupos": {int(j): round(d, 1) for j, d in zip(
            [j for j in range(len(self.cen)) if (g == j).sum() >= max(30, 0.02 * n)], der)}}

    def corrigir(self, a, forca=1.0, minimo=30):
        """Puxa a média de cada grupo de cor de volta para a do parado (mudança suave: peso pela distância aos grupos)."""
        m = a[..., 3] > 0
        L = lab(a[..., :3][m])
        g, dist = self.grupos(L)
        desvio = np.zeros_like(self.cen)
        conta = np.bincount(g, minlength=len(self.cen))
        for j in range(len(self.cen)):
            if conta[j] >= minimo:
                desvio[j] = L[g == j].mean(0) - self.cen[j]
        d = ((L[:, None, :] - self.cen[None]) ** 2).sum(-1)
        w = np.exp(-(d - d.min(1, keepdims=True)) / (2 * 6.0 ** 2))
        w[:, conta < minimo] = 0
        w /= np.maximum(w.sum(1, keepdims=True), 1e-6)
        corr = w @ desvio
        longe = dist > LONGE  # cor nova (efeito, objeto): não mexe
        corr[longe] = 0
        novo = L - forca * corr
        out = a.copy()
        out[..., :3][m] = rgb_de_lab(novo)
        return out


def perfil(ref, a, minimo=30):
    """Média Lab de cada grupo do parado neste quadro: {grupo: (média, n)}."""
    m = a[..., 3] > 0
    if not m.any():
        return {}
    L = lab(a[..., :3][m])
    g, _ = ref.grupos(L)
    n = len(L)
    return {int(j): (L[g == j].mean(0), int((g == j).sum())) for j in np.unique(g)
            if (g == j).sum() >= max(minimo, 0.02 * n)}


def salto(p, q):
    """Quanto as cores pulam entre dois quadros (delta E médio dos grupos que os dois têm)."""
    comuns = [j for j in p if j in q]
    if not comuns:
        return 0.0
    d = [np.linalg.norm(p[j][0] - q[j][0]) for j in comuns]
    w = [min(p[j][1], q[j][1]) for j in comuns]
    return float(np.average(d, weights=w))


def relatorio(lutador, acoes=None, um_x=False):
    """Mede todas as ações de um lutador: deriva/fora por quadro, salto entre quadros vizinhos e a troca com o parado
    (parado -> 1º quadro e último quadro -> parado)."""
    from quadros import Endereco
    base = Endereco(f"{lutador}/x", um_x).pasta.parent
    nomes = acoes or sorted(p.name for p in base.iterdir() if p.is_dir() and any(p.glob("[0-9][0-9].png")))
    refs, saida = {}, {}
    for acao in nomes:
        e = Endereco(f"{lutador}/{acao}", um_x)
        par = e.parado()
        chave = par.acao
        if chave not in refs:
            r = RefCor(par)
            pqs = [perfil(r, abrir(p)) for p in par.quadros()]
            refs[chave] = (r, pqs)
        r, pqs = refs[chave]
        qs = e.quadros()
        linhas, perf = [], []
        for p in qs:
            a = abrir(p)
            med = r.medir(a) or {"deriva": 0, "fora": 0, "grupos": {}}
            perf.append(perfil(r, a))
            linhas.append({"q": int(p.stem), "deriva": round(med["deriva"], 2), "fora": round(med["fora"], 3),
                           "grupos": med["grupos"]})
        for i in range(1, len(perf)):
            linhas[i]["salto"] = round(salto(perf[i - 1], perf[i]), 2)
        entra = min(salto(pp, perf[0]) for pp in pqs) if perf else 0
        sai = min(salto(perf[-1], pp) for pp in pqs) if perf else 0
        saida[acao] = {"parado": chave, "quadros": linhas, "entra": round(entra, 2), "sai": round(sai, 2)}
    return saida


def consertar_tom(lutador, acoes, forca=1.0):
    """Só o tom (lutador de cor cheia: Pengaró, Gutto, Raiclaven): puxa cada grupo de cor ao do parado da forma, nos
    desenhos (NN.png) e nos quadros do meio (meio/*.png), no desenho grande e no 1x quando os dois existem."""
    from PIL import Image
    from quadros import Endereco, PASTAS
    for um_x in ([False, True] if PASTAS[lutador][1] else [False]):
        refs = {}
        for acao in acoes:
            e = Endereco(f"{lutador}/{acao}", um_x)
            par = e.parado()
            if par.acao not in refs:
                refs[par.acao] = RefCor(par)
            arqs = e.quadros() + sorted((e.pasta / "meio").glob("*.png"))
            for p in arqs:
                a = abrir(p)
                Image.fromarray(refs[par.acao].corrigir(a, forca)).save(p, optimize=True)
            print("tom", "1x" if um_x else "grande", acao, len(arqs))


def consertar(lutador, acoes=None, um_x=False, forca=1.0):
    """Conserta a cor das ações: puxa cada grupo ao tom do parado (o parado não) e pinta na paleta única da forma."""
    import json
    from PIL import Image
    from quadros import Endereco, SPRITES, PALETA_JSON
    base = Endereco(f"{lutador}/x", um_x).pasta.parent
    nomes = acoes or sorted(p.name for p in base.iterdir() if p.is_dir() and any(p.glob("[0-9][0-9].png")))
    feitos = {}
    for acao in nomes:
        e = Endereco(f"{lutador}/{acao}", um_x)
        par = e.parado()
        if par.acao not in feitos:
            js = PALETA_JSON.get((lutador, e.forma))
            if js and (SPRITES / js).exists():
                pal = np.array([c["rgb"] for c in json.loads((SPRITES / js).read_text())["cores"]], np.uint8)
            else:
                todos = sorted(base.glob("*/[0-9][0-9].png"))
                pal = fazer_paleta(par, todos[::3])
                if js:
                    (SPRITES / js).write_text(json.dumps({"lutador": lutador, "nota": (
                        "Paleta única da forma (#51, cor mudando entre os quadros): cores do parado e dos efeitos. "
                        "Escrita por ferramentas/pixel/cores.py --consertar; todo quadro novo deve usar só estas cores."),
                        "cores": [{"id": f"c{i:02d}", "rgb": [int(v) for v in c]} for i, c in enumerate(pal)]},
                        indent=1, ensure_ascii=False))
            feitos[par.acao] = (RefCor(par), pal)
        ref, pal = feitos[par.acao]
        for p in e.quadros():
            a = abrir(p)
            if acao != par.acao:
                a = ref.corrigir(a, forca)
            Image.fromarray(pintar_na_paleta(a, pal)).save(p, optimize=True)
        print("consertado", acao)


def fazer_paleta(ref_end, extras_de=(), n=64, n_extra=16):
    """Paleta única de uma forma: n cores do parado (k-means em Lab, pesado pelo uso) e n_extra para o que o parado não
    tem (efeito, objeto: pixels longe de qualquer cor do parado nos quadros extras_de)."""
    qs = ref_end.quadros()
    px = np.concatenate([abrir(p)[..., :3][abrir(p)[..., 3] > 0] for p in qs])
    L = lab(px)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 80, 0.1)
    _, _, cen = cv2.kmeans(L, n, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    cen = cen.astype(np.float32)
    longe = []
    rng = np.random.default_rng(0)
    for p in extras_de:
        a = abrir(p)
        Lq = lab(a[..., :3][a[..., 3] > 0])
        d = np.sqrt(((Lq[:, None] - cen[None]) ** 2).sum(-1)).min(1)
        if (d > LONGE).any():
            longe.append(Lq[d > LONGE])
    if longe and n_extra:
        lo = np.concatenate(longe)
        if len(lo) > 40000:
            lo = lo[rng.choice(len(lo), 40000, replace=False)]
        _, _, ce = cv2.kmeans(lo, min(n_extra, len(lo)), None, crit, 3, cv2.KMEANS_PP_CENTERS)
        cen = np.concatenate([cen, ce.astype(np.float32)])
    rgb = np.unique(rgb_de_lab(cen), axis=0)
    return rgb  # (N, 3) uint8


def pintar_na_paleta(a, rgb):
    """Troca cada pixel pela cor da paleta mais perto (em Lab). Só mexe na cor: forma, alfa e tamanho ficam."""
    m = a[..., 3] > 0
    out = a.copy()
    if not m.any():
        return out
    P = lab(rgb)
    px = a[..., :3][m]
    u, inv = np.unique(px.reshape(-1, 3), axis=0, return_inverse=True)
    Lu = lab(u)
    idx = ((Lu[:, None] - P[None]) ** 2).sum(-1).argmin(1)
    out[..., :3][m] = rgb[idx][inv.ravel()]
    out[..., 3][m] = 255
    return out


if __name__ == "__main__":
    import argparse, json
    from pathlib import Path
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lutador")
    ap.add_argument("acoes", nargs="*")
    ap.add_argument("--1x", dest="um_x", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--consertar", action="store_true",
                    help="grava: puxa cada grupo de cor ao tom do parado e pinta na paleta da forma (cria a paleta se faltar)")
    ap.add_argument("--forca", type=float, default=1.0)
    ap.add_argument("--tom", action="store_true", help="grava: só puxa o tom ao do parado (cor cheia, sem paleta única)")
    ar = ap.parse_args()
    if ar.consertar:
        consertar(ar.lutador, ar.acoes or None, ar.um_x, ar.forca)
    if ar.tom:
        consertar_tom(ar.lutador, ar.acoes, ar.forca)
    rel = relatorio(ar.lutador, ar.acoes or None, ar.um_x)
    for acao, d in rel.items():
        der = [l["deriva"] for l in d["quadros"]]
        sal = [l.get("salto", 0) for l in d["quadros"]]
        fora = [l["fora"] for l in d["quadros"]]
        aviso = "AVISO" if max(der) > LIMITE_DERIVA or max(sal) > LIMITE_DERIVA or max(d["entra"], d["sai"]) > LIMITE_DERIVA else ""
        print(f"{acao:24s} deriva {min(der):4.1f}-{max(der):4.1f}  salto máx {max(sal):4.1f}  entra {d['entra']:4.1f} sai {d['sai']:4.1f}  fora máx {max(fora):.2f} {aviso}")
    if ar.json:
        Path(ar.json).write_text(json.dumps(rel, indent=1, ensure_ascii=False))
