#!/usr/bin/env python3
"""Régua do corpo todo (Breno, 24/11): a régua das pernas do Alisson (#32) levada para braço, cabeça e tronco.

  python ferramentas/regua_corpo.py                   pernas (regua_pernas inteira) + braços, cabeça e tronco de todos os kits
  python ferramentas/regua_corpo.py gutto ck          só esses lutadores (kits que começam com o nome)
  opções: --relatorio ARQ.md   --sem-pernas (só braço, cabeça e tronco)

A ideia do Alisson: toda peça variante do kit (o desenho a mais que entra num golpe) tem que ter a grossura e a área
da peça do parado do mesmo osso. Peça fina, comprida, curta ou gorda é o "membro besta" que o Breno viu no jogo. Na
perna ele mediu; aqui a mesma conta vale para o resto do corpo:

- BRAÇO (`braco_<lado>_*`, `antebraco_<lado>_*`) contra o braço do parado do mesmo lado (`braco_<lado>`, com o
  `antebraco_<lado>` junto quando o kit separa). Reprova grossura abaixo de 75% (braço fino, manga que some) ou área
  abaixo de 60% (braço curto ou sumido; punho fechado contra mão aberta dá uns 67%). Não há teto: o braço da guarda
  é visto em escorço (encurtado), então o braço esticado sempre sai maior que ele. Braço que já segura objeto
  fino no parado (a tesoura do Raiclaven, em OBJETO_PECA) não mede grossura, porque a lâmina puxa a mediana para baixo.
- CABEÇA (`cabeca_*`, as caras de dor, esforço, riso...) contra `cabeca`: a cabeça não muda de tamanho. Área e
  comprimento dentro de 15%.
- TRONCO e QUADRIL (`tronco_*`, `quadril_*`) contra `tronco` e `quadril`: área dentro de 30%, grossura acima de 80%.
  A peça agachada (`*_agachad*`), que já vem com as coxas dobradas, é comparada com quadril + pernas do parado.

Peça que reprova mas foi conferida no olho e está certa vai para ACEITAS, com o motivo.

As medidas são as de `regua_pernas.medir_peca` (grossura pelo esqueleto, área da maior mancha, comprimento no eixo
principal), com a peça posta na tela do parado. Sai com código 1 se algo reprovou.
"""
import json
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
RAIZ = AQUI.parent

import regua_pernas as rp  # noqa: E402

FINO_BRACO = 0.75    # braço: até 25% mais fino que o do parado
FINO = 0.80          # tronco e quadril: até 20% mais fino
AREA_MIN = 0.60      # braço: até 40% menor
CABECA = 0.15        # cabeça: área e comprimento dentro de 15%
TRONCO = 0.30        # tronco e quadril: área dentro de 30%
# Peças cujo braço já segura objeto no parado (o nome da variante não diz): "kit/pasta": (prefixos)
OBJETO_PECA = {"raiclaven/pecas": ("braco_tras", "antebraco_tras")}  # a tesoura do barbeiro
# Reprovou na conta, mas foi conferida no olho e está certa: "kit/pasta:peça": motivo
ACEITAS = {
    "hazaki/pecas:braco_tras_cruzado": "conferido em 24/11: braço inteiro visto de lado, na grossura certa; o do "
                                       "parado é o bíceps contraído em escorço, que puxa a régua para cima",
    # conferidos em 24/11 (tira em docs/boneco-pecas/regua_corpo_bracos.png): recortes do próprio desenho original do
    # golpe, braço nu e musculoso; o braço do parado leva a manga larga da camisa e o ombro, que puxam a régua para
    # cima. Engrossar por código foi tentado e é proibido pela regra do desenho original (Breno, 24/11).
    "ck/pecas:braco_tras_direto": "conferido em 24/11: recorte do desenho original do direto, braço nu; o do parado "
                                  "tem a manga larga da camisa",
    "ck/pecas:braco_tras_overhand": "conferido em 24/11: recorte do desenho original do overhand, braço nu; o do "
                                    "parado tem a manga larga da camisa",
    "ck_e/pecas:braco_tras_garrafa": "conferido em 24/11: recorte do desenho original (bola/03), antebraço nu com a "
                                     "garrafa; o do parado tem a manga da camisa aberta",
}
SOBRA = ("_vazio", "_furo", "_sobra")


def _pecas(kit):
    """O kit novo guarda as peças em "pecas"; o do Grão-Pastor é o dicionário das peças direto."""
    if isinstance(kit.get("pecas"), dict):
        return kit["pecas"]
    return {n: p for n, p in kit.items() if isinstance(p, dict) and "arquivo" in p}


def _mascaras(pasta, kit, nomes):
    k = {"pecas": _pecas(kit)}
    return {n: rp._mascara_no_parado(pasta, k, n) for n in nomes}


def _juntar(ms):
    ms = [m for m in ms if m is not None]
    if not ms or any(m.shape != ms[0].shape for m in ms):
        return ms[0] if ms else None
    return np.logical_or.reduce(ms)


def _referencias(pecas, m):
    """{grupo: (medida, nome)} das peças do parado que servem de régua."""
    ref = {}
    for lado in ("frente", "tras"):
        b, a = f"braco_{lado}", f"antebraco_{lado}"
        if b in m:
            junto = _juntar([m[b], m.get(a)]) if a in m else m[b]
            ref[b] = (rp.medir_peca(junto), b + (f"+{a}" if a in m else ""))
        if a in m:
            ref[a] = (rp.medir_peca(m[a]), a)
    for n in ("cabeca", "tronco", "quadril"):
        if n in m:
            ref[n] = (rp.medir_peca(m[n]), n)
    return ref


def _grupo(nome):
    for g in ("antebraco_frente", "antebraco_tras", "braco_frente", "braco_tras", "cabeca", "tronco", "quadril"):
        if nome.startswith(g + "_"):
            return g
    return None


def julgar(nome, grupo, g, a, c, objeto=False):
    """Lista do que está fora; vazia = passa."""
    ruim = []
    if grupo == "cabeca":
        if abs(a - 1) > CABECA:
            ruim.append(f"área {a:.0%}")
        if abs(c - 1) > CABECA:
            ruim.append(f"comprimento {c:.0%}")
        return ruim
    if grupo in ("tronco", "quadril"):
        if g < FINO:
            ruim.append(f"grossura {g:.0%}")
        if abs(a - 1) > TRONCO:
            ruim.append(f"área {a:.0%}")
        return ruim
    if not objeto and g < FINO_BRACO:
        ruim.append(f"grossura {g:.0%}")
    if a < AREA_MIN:
        ruim.append(f"área {a:.0%}")
    return ruim


def regua_kit_corpo(kit_dir):
    pasta = RAIZ / "sprites" / kit_dir
    kit = json.loads((pasta / "kit.json").read_text(encoding="utf-8"))
    pecas = _pecas(kit)
    nomes = [n for n in pecas if _grupo(n) or n in ("cabeca", "tronco", "quadril") or n.startswith(("braco_", "antebraco_"))]
    m = _mascaras(pasta, kit, nomes)
    ref = _referencias(pecas, m)
    falhas, linhas = [], []
    for nome in nomes:
        grupo = _grupo(nome)
        if not grupo or nome.endswith(SOBRA) or grupo not in ref or not ref[grupo][0]:
            continue
        mv = rp.medir_peca(m[nome])
        if mv is None:
            continue
        r, comparado = ref[grupo]  # variante do braço inteiro: contra braço + antebraço do parado
        if grupo in ("quadril", "tronco") and "agachad" in nome:
            baixo = [n for n in ("quadril", "coxa_tras", "canela_tras", "coxa_frente", "canela_frente", "perna_tras",
                                 "perna_frente") if n in pecas]
            junto = _juntar(list(_mascaras(pasta, kit, baixo).values()))
            r = rp.medir_peca(junto) or r
            comparado = "quadril e pernas do parado"
        g, a, c = mv[0] / r[0], mv[1] / r[1], mv[2] / max(1.0, r[2])
        objeto = any(nome.startswith(o) for o in OBJETO_PECA.get(kit_dir, ()))
        ruim = julgar(nome, grupo, g, a, c, objeto)
        aceita = ACEITAS.get(f"{kit_dir}:{nome}")
        if ruim and aceita:
            ruim = []
            comparado += f" (aceita: {aceita})"
        linhas.append((kit_dir, nome, comparado, g, a, c, ruim))
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
    nomes = [a for a in args if not a.startswith("--")]
    falhas, texto = [], ["# Régua do corpo todo", ""]
    if "--sem-pernas" not in flags:
        import contextlib
        import io
        buf = io.StringIO()
        sys.argv = [sys.argv[0]] + nomes
        codigo = 0
        with contextlib.redirect_stdout(buf):
            try:
                rp.main()
            except SystemExit as e:
                codigo = e.code or 0
        pernas = buf.getvalue().replace("# Régua das pernas", "## Pernas (regua_pernas.py, do Alisson)")
        texto += [pernas]
        if codigo:
            falhas.append("régua das pernas reprovou (detalhes acima)")
    texto += ["## Braço, cabeça e tronco (variante do kit contra o parado)", "",
              "| kit | peça | comparada com | grossura | área | comprimento | resultado |",
              "|---|---|---|---|---|---|---|"]
    kits = sorted(p.parent.relative_to(RAIZ / "sprites") for p in (RAIZ / "sprites").glob("*/pecas*/kit.json"))
    for k in kits:
        if nomes and not any(str(k).startswith(n) for n in nomes):
            continue
        f, linhas = regua_kit_corpo(str(k))
        falhas += f
        texto += [f"| {a} | {n} | {cp} | {g:.0%} | {ar:.0%} | {c:.0%} | {'FAIL ' + ', '.join(r) if r else 'PASS'} |"
                  for a, n, cp, g, ar, c, r in linhas]
    texto += ["", f"**{len(falhas)} reprovação(ões).**", ""] + [f"- {f}" for f in falhas]
    saida = "\n".join(texto) + "\n"
    print(saida)
    if relatorio:
        Path(relatorio).write_text(saida, encoding="utf-8")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
