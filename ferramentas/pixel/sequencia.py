"""Régua de quadro intruso: acha o quadro que veio de outro desenho no meio de uma ação (#51, Pengaró de três braços).

O jab do Pengaró (soco/05) tinha três braços porque era um quadro de outra geração de desenho enfiado na sequência:
sem a joelheira, com as pernas em outra pose, e o braço do soco saindo do ombro da garrafa. A régua de manchas de pele
não pega isso (o tronco nu e os braços viram uma mancha só). Esta régua olha a sequência, que é onde o erro aparece:

  peça some/volta   um grupo de cor do parado (joelheira, cabelo, faixa, luva...) está nos dois vizinhos e some neste
                    quadro, ou aparece só nele. Joelheira que pisca, cabeça de outro desenho (cabelo de outra cor),
                    luva pintada de outra cor, mão a mais segurando objeto.
  intruso           o contorno deste quadro foge dos dois vizinhos bem mais do que os vizinhos fogem um do outro
                    (1 - IoU das silhuetas; os quadros têm o mesmo eixo na tela).

AVISO = peça some/volta com intruso > LIMITE_PECA (pegou o jab, a lata, a ginga e o anda do Pengaró, todos do mesmo
desenho sem joelheira). "olhar" = só o contorno foge (intruso > LIMITE_FORMA): chute rápido e ginga que balança também
dão isso, então é para conferir com tira_jogo.py / pixel.py ver, não prova.

  python3 ferramentas/pixel/sequencia.py pengaro            # todas as ações (base e e_)
  python3 ferramentas/pixel/sequencia.py ck rasteira caneta # só essas
  python3 ferramentas/pixel/sequencia.py --todos --json A.json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from quadros import abrir, Endereco, SPRITES, PASTAS, PARADO  # noqa: E402
from cores import RefCor, lab  # noqa: E402

MINIMO = 0.012       # fração da figura para um grupo de cor contar como "peça"
SOME = 0.3           # o quadro tem menos que isto da peça dos vizinhos = sumiu
LIMITE_PECA = 0.05
LIMITE_FORMA = 0.30


def _alinha(m, h, w):
    """Põe a máscara numa tela h x w com os pés embaixo e o meio no meio (o Diabo tem quadro de tamanho variável)."""
    if m.shape == (h, w):
        return m
    out = np.zeros((h, w), bool)
    x = (w - m.shape[1]) // 2
    out[h - m.shape[0]:, x:x + m.shape[1]] = m
    return out


def fuga(a, b):
    ma, mb = a[..., 3] > 0, b[..., 3] > 0
    h, w = max(ma.shape[0], mb.shape[0]), max(ma.shape[1], mb.shape[1])
    ma, mb = _alinha(ma, h, w), _alinha(mb, h, w)
    return 1 - (ma & mb).sum() / max((ma | mb).sum(), 1)


def fracoes(ref, a):
    m = a[..., 3] > 0
    if not m.any():
        return np.zeros(len(ref.cen))
    g, _ = ref.grupos(lab(a[..., :3][m]))
    return np.bincount(g, minlength=len(ref.cen)) / m.sum()


def medir_acao(end, ref, arquivos=None):
    """[(quadro, intruso, [peças], aviso)] dos quadros do meio da ação (o 1º e o último não têm dois vizinhos)."""
    qs = arquivos or end.quadros()
    if len(qs) < 3:
        return []
    ims = [abrir(p) for p in qs]
    fr = [fracoes(ref, a) for a in ims]
    out = []
    for k in range(1, len(ims) - 1):
        a, b, c = ims[k - 1], ims[k], ims[k + 1]
        intruso = min(fuga(a, b), fuga(b, c)) - fuga(a, c)
        pecas = []
        for j in range(len(ref.cen)):
            lo, hi = min(fr[k - 1][j], fr[k + 1][j]), max(fr[k - 1][j], fr[k + 1][j])
            if lo >= MINIMO and fr[k][j] < SOME * lo:
                pecas.append(f"grupo {j} some ({lo:.1%} -> {fr[k][j]:.1%})")
            if fr[k][j] >= MINIMO and hi < SOME * fr[k][j]:
                pecas.append(f"grupo {j} aparece ({fr[k][j]:.1%})")
        aviso = bool(pecas) and intruso > LIMITE_PECA  # forma sozinha (intruso > LIMITE_FORMA) só vira 'olhar'
        out.append((Path(qs[k]).stem, round(float(intruso), 3), pecas, bool(aviso)))
    return out


def acoes_do(lutador):
    base = SPRITES / PASTAS[lutador][0]
    return sorted(d.name for d in base.iterdir() if d.is_dir() and any(d.glob("[0-9][0-9].png")))


def medir(lutador, acoes=None):
    refs, res = {}, {}
    for acao in acoes or acoes_do(lutador):
        end = Endereco(f"{lutador}/{acao}")
        forma = end.forma
        if forma not in refs:
            refs[forma] = RefCor(end)
        res[acao] = medir_acao(end, refs[forma])
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lutador", nargs="?")
    ap.add_argument("acoes", nargs="*")
    ap.add_argument("--todos", action="store_true", help="todos os lutadores")
    ap.add_argument("--json", type=Path)
    ap.add_argument("--tudo", action="store_true", help="mostra também os quadros sem aviso que têm peça some/volta")
    ar = ap.parse_args()
    lutadores = list(PASTAS) if ar.todos else [ar.lutador]
    geral, n = {}, 0
    for l in lutadores:
        r = medir(l, ar.acoes or None)
        geral[l] = r
        for acao, linhas in r.items():
            for q, intr, pecas, aviso in linhas:
                olhar = not aviso and intr > LIMITE_FORMA
                if aviso or olhar or (ar.tudo and pecas):
                    n += aviso
                    rot = "AVISO " if aviso else "olhar " if olhar else "      "
                    print(f"{rot}{l}/{acao}/{q}  intruso {intr:+.2f}  {'; '.join(pecas)}")
    if ar.json:
        ar.json.write_text(json.dumps(geral, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{n} avisos de quadro intruso")


if __name__ == "__main__":
    main()
