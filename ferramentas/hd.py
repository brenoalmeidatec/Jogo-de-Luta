"""Lutador em alta resolução (HD): os sprites do corpo no triplo do tamanho e o lutador desenhado em 1/3.

Por que: os quadros do jogo têm o boneco com ~110 px e o IKEMEN estica 3x (localcoord 320x240 numa tela de 720):
cada pixel do desenho vira um bloco 3x3 e o rosto, os olhos e os músculos viram borrão. Com o sprite 3x maior e
[Size] xscale = yscale = 1/3, o motor desenha cada pixel do desenho num pixel da tela, sem esticar nada.

Como (sem mexer no resto do gerador): o gerador monta tudo em 1x, como sempre. No fim, `aplicar` troca cada sprite do
corpo pelo gêmeo HD do mesmo quadro (quadros_arcade_hd/<folha>/NN.png, cortado pelo converter com HD=3), achado pela
comparação de pixels com o quadro de 1x (aceita retoques pequenos e quadro espelhado). Sprite sem gêmeo (montado por
código, ou folha ainda sem HD) só é ampliado 3x sem misturar cor: fica igual a hoje.

O que o motor faz com a escala (IKEMEN v1.0.0, char.go): o corpo e as caixas (Clsn) usam size.xscale/yscale; Explod
não usa (só com syncid) e projétil só com size.proj.doscale (0 por padrão). Por isso:
  - sprite que só aparece em Explod, projétil ou faísca própria (S) continua em 1x, do jeito que está;
  - toda caixa Clsn do .air multiplica por 3 (as dos projéteis também: projétil usa a escala de caixa do dono);
  - no arremesso (ChangeAnim2) cada um é desenhado com a própria escala: lutador HD e lutador antigo se misturam bem.
"""
import os
import re

import numpy as np
from PIL import Image

E = 3

RE_ACAO = re.compile(r"^\[Begin Action (\d+)\]", re.M | re.I)
RE_ELEM = re.compile(r"^\s*(-?\d+)\s*,\s*(-?\d+)\s*,", re.M)
RE_CLSN = re.compile(r"^(\s*Clsn[12]\s*\[\s*\d+\s*\]\s*=\s*)(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)", re.M | re.I)


def acoes(air):
    """{ação: {(grupo, índice)}} do .air."""
    out = {}
    partes = RE_ACAO.split(air)
    for k in range(1, len(partes), 2):
        out[int(partes[k])] = {(int(g), int(i)) for g, i in RE_ELEM.findall(partes[k + 1])}
    return out


def acoes_de_efeito(cns):
    """Ações que o motor desenha sem a escala do lutador: anim de Explod/ModifyExplod (sem F), anim de projétil e
    faísca própria (sparkno/guard.sparkno com S). Expressão no lugar do número fica de fora (devolvida à parte)."""
    nums, duvida = set(), []
    for chave, valor in re.findall(r"^\s*(anim|projanim|projhitanim|projremanim|projcancelanim|sparkno|guard\.sparkno)"
                                   r"\s*=\s*([^;\n]+)", cns, re.M | re.I):
        valor = valor.strip()
        if chave.lower() == "anim":
            continue  # resolvido por bloco abaixo (anim também aparece em ChangeAnim)
        if re.match(r"[Ss]", valor):  # faísca própria: S9200 ou S(ifelse(var(20) > 0, 9230, 9200))
            nums.update(int(n) for n in re.findall(r"(?<![\w.])(\d{3,})(?![\w.])", valor[1:]))
        elif chave.lower().startswith("proj"):
            nums.update(int(n) for n in re.findall(r"(?<![\w.])(\d{3,})(?![\w.])", valor))
    for bloco in re.split(r"^\[State", cns, flags=re.M):
        if re.search(r"^\s*type\s*=\s*(Explod|ModifyExplod)\b", bloco, re.M | re.I):
            for valor in re.findall(r"^\s*anim\s*=\s*([^;\n]+)", bloco, re.M | re.I):
                valor = valor.strip()
                if re.fullmatch(r"\d+", valor):
                    nums.add(int(valor))
                elif not re.fullmatch(r"[Ff]\s*\d+", valor):
                    # expressão (ex.: ifelse(var(20) > 0, 9231, 9201)): os números de 3+ dígitos são as ações
                    achados = [int(n) for n in re.findall(r"(?<![\w.])(\d{3,})(?![\w.])", valor)]
                    nums.update(achados)
                    if not achados:
                        duvida.append(valor)
    return nums, duvida


def _caixa(a):
    m = a[..., 3] >= 128
    ys, xs = np.nonzero(m)
    if not len(xs):
        return None
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


class Indice:
    """Quadros de 1x com gêmeo HD, agrupados pelo tamanho do recorte (e também espelhados)."""

    def __init__(self, pares):
        self.por_tamanho = {}
        for pasta1, pastahd in pares:
            for arq in sorted(pasta1.glob("*/*.png")):
                gemeo = pastahd / arq.parent.name / arq.name
                if not gemeo.exists():
                    continue
                a = np.asarray(Image.open(arq).convert("RGBA"))
                for espelho in (False, True):
                    b = a[:, ::-1] if espelho else a
                    cx = _caixa(b)
                    if cx is None:
                        continue
                    x0, y0, x1, y1 = cx
                    rec = b[y0:y1, x0:x1]
                    self.por_tamanho.setdefault(rec.shape[:2], []).append((rec, (x0, y0), gemeo, espelho))

    def achar(self, rec):
        melhor, nota = None, 0.9
        for cand, origem, gemeo, espelho in self.por_tamanho.get(rec.shape[:2], ()):
            ma, mb = rec[..., 3] >= 128, cand[..., 3] >= 128
            perto = (np.abs(rec[..., :3].astype(int) - cand[..., :3].astype(int)).sum(axis=2) <= 24)
            n = ((ma == mb) & (~ma | perto)).mean()
            if n > nota:
                melhor, nota = (origem, gemeo, espelho), n
        return melhor


def aplicar(s, air, cns, pares, vitima=frozenset()):
    """Troca os sprites do corpo de `s.lista` pelos HD e devolve (air, cns) com as caixas x3 e [Size] em 1/3.
    `pares`: [(pasta de 1x, pasta HD)], cada uma com <folha>/NN.png. `vitima`: sprites que o arremesso de OUTRO
    lutador desenha com este .sff (e a escala deste lutador): são corpo mesmo fora do .air deste."""
    por_acao = acoes(air)
    efeito_n, duvida = acoes_de_efeito(cns)
    corpo_spr = set().union(*(v for k, v in por_acao.items() if k not in efeito_n)) | set(vitima)
    efeito_spr = set().union(*(v for k, v in por_acao.items() if k in efeito_n)) if efeito_n else set()
    dos_dois = efeito_spr & corpo_spr
    # sprite usado no corpo E num efeito: o efeito fica com o original (1x) e as ações do corpo passam a uma cópia num
    # grupo livre (grupo + 20000), que vira HD como qualquer sprite do corpo
    copia = {(g, i): (g + 20000, i) for g, i in dos_dois}
    assert not {c for c in copia.values()} & {(g, i) for g, i, *_ in s.lista}, "grupo da cópia HD já ocupado"
    if copia:
        partes = RE_ACAO.split(air)
        for k in range(1, len(partes), 2):
            if int(partes[k]) not in efeito_n:
                partes[k + 1] = RE_ELEM.sub(lambda m: (f"{copia[int(m.group(1)), int(m.group(2))][0]},{m.group(2)},"
                                                       if (int(m.group(1)), int(m.group(2))) in copia else m.group(0)),
                                            partes[k + 1])
        air = "".join(p if k % 2 == 0 else f"[Begin Action {p}]" for k, p in enumerate(partes))
        s.lista.extend((copia[g, i][0], i, img, ex, ey) for g, i, img, ex, ey in list(s.lista) if (g, i) in copia)
        corpo_spr = (corpo_spr - dos_dois) | set(copia.values())
    indice = Indice(pares)
    nova, hd, ampliado, sem_gemeo = [], 0, 0, []
    for grupo, numero, img, ex, ey in s.lista:
        if grupo == 9000 or (grupo, numero) not in corpo_spr:
            # retrato (o screenpack desenha sem a escala do lutador), efeito ou sprite fora do .air: fica em 1x
            nova.append((grupo, numero, img, ex, ey))
            continue
        a = np.asarray(img.convert("RGBA"))
        cx = _caixa(a)
        achado = indice.achar(a[cx[1]:cx[3], cx[0]:cx[2]]) if cx else None
        tela = Image.new("RGBA", (img.width * E, img.height * E))
        if achado:
            (fx0, fy0), gemeo, espelho = achado
            g = Image.open(gemeo).convert("RGBA")
            g = g.transpose(Image.FLIP_LEFT_RIGHT) if espelho else g
            tela.paste(g, (E * (cx[0] - fx0), E * (cx[1] - fy0)), g)
            hd += 1
        else:
            tela = img.convert("RGBA").resize(tela.size, Image.NEAREST)
            ampliado += 1
            sem_gemeo.append((grupo, numero))
        nova.append((grupo, numero, tela, ex * E, ey * E))
    s.lista[:] = nova
    air = RE_CLSN.sub(lambda m: m.group(1) + ", ".join(str(int(v) * E) for v in m.groups()[1:]), air)
    cns, k = re.subn(r"(\[Size\][^\[]*?^xscale\s*=\s*)([\d.]+)", lambda m: m.group(1) + f"{float(m.group(2)) / E:.6g}",
                     cns, count=1, flags=re.M | re.I)
    cns, k2 = re.subn(r"(\[Size\][^\[]*?^yscale\s*=\s*)([\d.]+)", lambda m: m.group(1) + f"{float(m.group(2)) / E:.6g}",
                      cns, count=1, flags=re.M | re.I)
    assert k == k2 == 1, "[Size] sem xscale/yscale no .cns"
    print(f"HD: {hd} sprites trocados pelo desenho 3x, {ampliado} só ampliados, {len(efeito_spr - corpo_spr)} de "
          f"efeito em 1x" + (f"; {len(dos_dois)} sprites em corpo E efeito (copiados: o efeito fica em 1x)" if dos_dois else "")
          + (f"; anim de Explod por expressão: {sorted(set(duvida))}" if duvida else ""))
    if os.environ.get("HD_LISTA"):
        print("  sem gêmeo:", sem_gemeo)
        print("  corpo e efeito:", sorted(dos_dois))
    return air, cns
