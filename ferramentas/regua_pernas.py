#!/usr/bin/env python3
"""Régua das pernas (pedido do Breno, 22/11, #32): reprova perna esticando no agachado e perna fora da proporção.

  python ferramentas/regua_pernas.py                      todos os lutadores, base e despertado, e todos os kits
  python ferramentas/regua_pernas.py gutto ck             só esses
  opções: --relatorio ARQ.md   --so-agachado   --so-kit

Duas réguas, as duas olham o que o jogador vê ou o que monta o que ele vê:

1. AGACHADO (chars/<l>/<l>.sff + .air + .cns): todo estado do tipo agachado (`type = C` no .cns) tem que ficar
   agachado em todos os desenhos. Para cada desenho mede a altura do centro de massa da figura acima do chão e põe
   na escala do lutador: 0 = agachado parado (ação 11), 1 = em pé parado (ação 0). Braço que sobe mexe pouco no centro
   de massa; o corpo que levanta (pernas esticando) leva ele para perto de 1. A altura da figura entra na mesma escala
   (0 = altura do agachado, 1 = altura do em pé): só levanta o desenho em que as DUAS passam de LIMITE_SOBE. Sozinho,
   o centro de massa engana no lutador de agachado raso (CK: o agachado tem 83% da altura do em pé), onde o braço
   esticado na altura do peito já sobe o centro sem o corpo subir nada.
   Com --despertado (sempre feito) os desenhos passam pelo [RemapPreset despertado], como no jogo.

2. KIT (sprites/<kit>/pecas/kit.json): toda variante de perna (coxa_*, canela_*, perna_*) é comparada com a peça do
   parado do mesmo osso. Mede a grossura (2 x a mediana da distância até a borda, no eixo da peça) e a área. A
   variante que é a perna inteira (coxa e canela num desenho só) é comparada com a coxa e a canela do parado juntas.
   Grossura fora de LIMITE_GROSSURA ou área fora de LIMITE_AREA = reprovado: perna fina, gorda, comprida ou curta
   demais, que é o "perna besta" do Breno. Peça de agachado (`agachad`, `pernas_`) só mede a grossura, porque a
   perna dobrada esconde parte da área.

Sai com código 1 se algo reprovou.
"""
import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
RAIZ = AQUI.parent
LUTADORES = ["pengaro", "gutto", "ck", "hazaki", "raiclaven", "gbzin"]
DIAMETRO = 0.17          # abertura que tira os membros finos (fração da altura do parado)
LIMITE_SOBE = 0.45       # fração do caminho agachado -> em pé que o centro de massa pode subir num golpe agachado
LIMITE_TRANSICAO = 1.0   # 10 (agachando) e 12 (levantando) passam pelo meio do caminho: só não podem passar do em pé
TRANSICOES = (10, 12)
LIMITE_GROSSURA = 0.20   # perna esticada até 20% mais fina que a do parado
LIMITE_ROUPA = 0.60      # e até 60% mais grossa (calça larga balançando no chute; perna fina é o defeito)
LIMITE_AREA = 0.30       # +-30% na área (+-40% na perna dobrada): perna comprida, curta ou bolota
COMUNS = (10, 11, 12, 131, 141, 151)
PERNA = ("coxa_", "canela_", "perna_", "pernas_")


# ------------------------------------------------------------------ régua 1: agachado
def _sprites(lut, despertado):
    import verificar_pengaro as v
    import video_golpe as vg
    v.PERSONAGEM = lut
    v.PASTA = RAIZ / "chars" / lut
    sp, pal = v.ler_sff()
    if despertado:
        cns = (RAIZ / "chars" / lut / f"{lut}.cns").read_text(encoding="utf-8")
        bloco = re.search(r"^\[RemapPreset despertado\]\n(.*?)(?=^\[)", cns, re.M | re.S)
        if not bloco:
            return None
        orig = dict(sp)
        for g, i, g2, i2 in re.findall(r"^(\d+),\s*(\d+)\s*=\s*(\d+),\s*(\d+)", bloco.group(1), re.M):
            if (int(g2), int(i2)) in orig:
                sp[(int(g), int(i))] = orig[(int(g2), int(i2))]
    return vg.Desenhos(sp, pal), vg.ler_air(v.PASTA, lut)


def estados_agachados(lut, despertado=False):
    """{ação: estado} das animações dos estados do tipo agachado (type = C). Na forma despertada vale a arte própria
    do estado (`ChangeAnim` com `var(20) > 0`, a "Arte despertada"), que é o que o jogo mostra."""
    texto = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in (RAIZ / "chars" / lut).glob("*.cns"))
    out = {}
    for m in re.finditer(r"^\[Statedef\s+(-?\d+)[^\]]*\](.*?)(?=^\[Statedef|\Z)", texto, re.M | re.S | re.I):
        corpo = m.group(2)
        cab = corpo.split("\n[", 1)[0]
        tipo = re.search(r"^\s*type\s*=\s*(\w)", cab, re.M | re.I)
        anim = re.search(r"^\s*anim\s*=\s*(\d+)\s*$", cab, re.M | re.I)
        if not (tipo and tipo.group(1).upper() == "C" and anim):
            continue
        acao = int(anim.group(1))
        if despertado:
            for bloco in re.split(r"^\[State ", corpo, flags=re.M)[1:]:
                if re.search(r"^\s*type\s*=\s*ChangeAnim\s*$", bloco, re.M | re.I) and \
                        re.search(r"var\(20\)\s*>\s*0", bloco) and \
                        (v := re.search(r"^\s*value\s*=\s*(\d+)\s*$", bloco, re.M)):
                    acao = int(v.group(1))
                    break
        out.setdefault(acao, int(m.group(1)))
    for a in COMUNS:  # agachar, levantar e defesa baixa (estados comuns do motor, sem Statedef no .cns do lutador)
        out.setdefault(a, a)
    return out


def basico(estado):
    """O que o Breno mandou conferir (22/11): agachar, golpes agachados, defesa baixa e apanhar agachado. Golpe
    especial do tipo agachado (sobe de propósito, como um gancho que sai do chão) só vira aviso."""
    e = estado % 10000 if estado >= 10000 else estado
    e = e % 1000 if 4000 <= e < 5000 else e
    return e in (10, 11, 12, 131, 141, 151, 152) or 400 <= e <= 449 or 5020 <= e <= 5029


def centro(desenhos, el, diametro=None):
    """Altura do centro de massa do corpo acima do chão (px do sprite). Com `diametro`, os membros finos (braço
    esticado, perna do chute) saem antes por abertura morfológica: fica o tronco, a cabeça e as pernas dobradas."""
    if (el[0], el[1]) not in desenhos.sprites:
        return None
    img, ax, ay = desenhos.rgba((el[0], el[1]), el[5])
    a = np.asarray(img)[..., 3] > 127
    if not a.any():
        return None
    if diametro:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (diametro, diametro))
        b = cv2.morphologyEx(a.astype(np.uint8), cv2.MORPH_OPEN, k).astype(bool)
        if b.sum() > a.sum() * 0.25:
            a = b
    ys, _ = np.nonzero(a)
    return float(ay - el[3] - ys.mean())


def altura(desenhos, el):
    if (el[0], el[1]) not in desenhos.sprites:
        return None
    img, _, _ = desenhos.rgba((el[0], el[1]), el[5])
    ys = np.nonzero(np.asarray(img)[..., 3] > 127)[0]
    return int(ys.max() - ys.min() + 1) if len(ys) else None


def regua_agachado(lut, despertado):
    r = _sprites(lut, despertado)
    if r is None:
        return [], [], []
    desenhos, acoes = r
    if 0 not in acoes or 11 not in acoes:
        return [], [f"{lut}: sem ação 0 ou 11, régua do agachado não roda"], []
    alt = np.median([h for el in acoes[0][0] if (h := altura(desenhos, el))])
    diam = max(5, int(alt * DIAMETRO))
    em_pe = np.median([c for el in acoes[0][0] if (c := centro(desenhos, el, diam)) is not None])
    agach = np.median([c for el in acoes[11][0] if (c := centro(desenhos, el, diam)) is not None])
    alt_ag = np.median([h for el in acoes[11][0] if (h := altura(desenhos, el))])
    falhas, avisos, linhas = [], [], []
    forma = "despertado" if despertado else "base"
    for acao, estado in sorted(estados_agachados(lut, despertado).items()):
        if acao not in acoes:
            continue
        if not despertado and (4000 <= estado < 5000 or estado >= 6000):
            continue  # golpe próprio do despertado: só existe na forma despertada
        piores = []
        limite = LIMITE_TRANSICAO if estado in TRANSICOES else LIMITE_SOBE
        for k, el in enumerate(acoes[acao][0]):
            c = centro(desenhos, el, diam)
            if c is None:
                continue
            f = (c - agach) / max(1.0, em_pe - agach)
            fh = (altura(desenhos, el) - alt_ag) / max(1.0, alt - alt_ag)
            if f > limite and fh > limite:
                piores.append((min(f, fh), k, el[0], el[1]))
        if piores:
            pior = max(piores)
            msg = (f"{lut} {forma}: ação {acao} (estado {estado}, agachado) levanta em {len(piores)} de "
                   f"{len(acoes[acao][0])} elementos; o pior sobe {pior[0]:.0%} do agachado ao em pé (centro e altura) "
                   f"(elemento {pior[1]}, sprite {pior[2]},{pior[3]})")
            (falhas if basico(estado) else avisos).append(msg)
        linhas.append((acao, estado, len(piores)))
    return falhas, avisos, linhas


# ------------------------------------------------------------------ régua 2: kit
def _mascara_no_parado(pasta, kit, nome):
    """Máscara da peça na tela do parado (posta na origem gravada no kit)."""
    p = kit["pecas"][nome]
    img = cv2.imread(str(pasta / p["arquivo"]), cv2.IMREAD_UNCHANGED)
    if img is None or img.ndim < 3 or img.shape[2] < 4:
        return None
    m = img[..., 3] > 0
    ox, oy = p.get("origem", [0, 0])
    tela = np.zeros((1400, 1600), bool)
    x0, y0 = int(ox) + 200, int(oy) + 300
    h, w = m.shape
    if x0 < 0 or y0 < 0 or y0 + h > tela.shape[0] or x0 + w > tela.shape[1]:
        return m
    tela[y0:y0 + h, x0:x0 + w] = m
    return tela


def medir_peca(m):
    """(grossura, área, comprimento) da maior mancha. Grossura = mediana de 2 x a distância até a borda no esqueleto
    da peça (sem as pontinhas do esqueleto): não depende do ângulo nem de a perna estar dobrada."""
    from skimage.morphology import skeletonize
    if m is None or not m.any():
        return None
    u8 = m.astype(np.uint8)
    n, rot, st, _ = cv2.connectedComponentsWithStats(u8, 8)
    if n > 2:  # só a mancha maior (sobra de recorte não conta)
        u8 = (rot == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    if u8.sum() < 50:
        return None
    u8 = cv2.morphologyEx(u8, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    dt = cv2.distanceTransform(u8, cv2.DIST_L2, 5)
    v = dt[skeletonize(u8 > 0)]
    v = v[v > 0.3 * v.max()]
    ys, xs = np.nonzero(u8)
    pts = np.stack([xs, ys], 1).astype(np.float64)
    pts -= pts.mean(0)
    _, _, vt = np.linalg.svd(pts, full_matrices=False)
    t = pts @ vt[0]
    return 2 * float(np.median(v)), int(u8.sum()), float(t.max() - t.min())


BASE = {"coxa_frente", "coxa_tras", "canela_frente", "canela_tras", "perna_frente", "perna_tras"}
DOBRADA = ("agachad", "pernas_", "camara", "baixa", "apoio")  # joelho dobrado: a largura no eixo não é a da perna


def regua_kit(kit_dir):
    """Cada variante de perna contra a perna inteira do parado do mesmo lado (coxa + canela, ou perna_)."""
    pasta = RAIZ / "sprites" / kit_dir
    kit = json.loads((pasta / "kit.json").read_text(encoding="utf-8"))
    pecas = kit.get("pecas", {})
    m = {n: _mascara_no_parado(pasta, kit, n) for n in pecas if n.startswith(PERNA)}
    ref = {}
    for lado in ("frente", "tras"):
        if f"coxa_{lado}" in m and f"canela_{lado}" in m and m[f"coxa_{lado}"].shape == m[f"canela_{lado}"].shape:
            ref[lado] = (medir_peca(m[f"coxa_{lado}"] | m[f"canela_{lado}"]), f"coxa_{lado}+canela_{lado}")
        elif f"perna_{lado}" in m:
            ref[lado] = (medir_peca(m[f"perna_{lado}"]), f"perna_{lado}")
    falhas, linhas = [], []
    for nome in pecas:
        if not nome.startswith(PERNA) or nome in BASE or nome.endswith(("_vazio", "_furo", "_sobra")):
            continue
        lado = "tras" if "_tras" in nome else "frente"
        if lado not in ref or not ref[lado][0]:
            continue
        mv = medir_peca(m[nome])
        if mv is None:
            continue
        r, comparado = ref[lado]
        if nome.startswith("pernas_"):  # o de baixo inteiro num desenho só: área contra quadril + as duas pernas
            baixo = [n for n in ("quadril", "coxa_tras", "canela_tras", "coxa_frente", "canela_frente", "perna_tras",
                                 "perna_frente") if n in pecas]
            ms = [_mascara_no_parado(pasta, kit, n) for n in baixo]
            if not all(x is not None and x.shape == ms[0].shape for x in ms):
                continue
            junto = np.logical_or.reduce(ms)
            r = (r[0], int(junto.sum()), r[2])
            comparado = "quadril e pernas do parado"
        g, a = mv[0] / r[0], mv[1] / r[1]
        dobrada = any(d in nome for d in DOBRADA)
        ruim = []
        if not dobrada and not (1 - LIMITE_GROSSURA <= g <= 1 + LIMITE_ROUPA):
            ruim.append(f"grossura {g:.0%}")
        # perna esticada: só a área que falta reprova (calça larga pendurada aumenta a área sem a perna crescer)
        if (dobrada and abs(a - 1) > LIMITE_AREA + 0.1) or (not dobrada and a < 1 - LIMITE_AREA):
            ruim.append(f"área {a:.0%}")
        linhas.append((kit_dir, nome, comparado, g, a, ruim))
        if ruim:
            falhas.append(f"kit {kit_dir}: {nome} contra {comparado}: " + ", ".join(ruim))
    return falhas, linhas


def main():
    args = sys.argv[1:]
    relatorio = ""
    if "--relatorio" in args:
        i = args.index("--relatorio")
        relatorio = args[i + 1]
        del args[i:i + 2]
    flags = {a for a in args if a.startswith("--")}
    nomes = [a for a in args if not a.startswith("--")] or LUTADORES
    falhas, avisos, texto = [], [], ["# Régua das pernas", ""]
    if "--so-kit" not in flags:
        texto += ["## Agachado (golpe do tipo agachado não pode levantar)", "",
                  "| lutador | forma | ações agachadas | elementos que levantam |", "|---|---|---|---|"]
        for lut in nomes:
            if not (RAIZ / "chars" / lut).is_dir():
                continue
            for desp in (False, True):
                f, av, linhas = regua_agachado(lut, desp)
                falhas += f
                avisos += av
                if linhas:
                    texto.append(f"| {lut} | {'despertado' if desp else 'base'} | {len(linhas)} | "
                                 + (", ".join(f"{a}: {n}" for a, _, n in linhas if n) or "nenhum") + " |")
    if "--so-agachado" not in flags:
        texto += ["", "## Kit (variante de perna contra o parado)", "",
                  "| kit | peça | comparada com | grossura | área | resultado |", "|---|---|---|---|---|---|"]
        kits = sorted(p.parent.relative_to(RAIZ / "sprites") for p in (RAIZ / "sprites").glob("*/pecas*/kit.json"))
        for k in kits:
            if args and not any(str(k).startswith(n) for n in nomes):
                continue
            f, linhas = regua_kit(str(k))
            falhas += f
            texto += [f"| {a} | {n} | {c} | {g:.0%} | {ar:.0%} | {'FAIL ' + ', '.join(r) if r else 'PASS'} |"
                      for a, n, c, g, ar, r in linhas]
    texto += ["", f"**{len(falhas)} reprovação(ões).**", ""] + [f"- {f}" for f in falhas]
    if avisos:
        texto += ["", "Avisos (especial do tipo agachado que sobe; olhar no vídeo):", ""] + [f"- {a}" for a in avisos]
    saida = "\n".join(texto) + "\n"
    print(saida)
    if relatorio:
        Path(relatorio).write_text(saida, encoding="utf-8")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
