#!/usr/bin/env python3
"""Golpe agachado feito do próprio desenho do agachado, com o tronco dobrando em volta da cintura (pedido do Breno na
#32, 22/11: golpe agachado não levanta e a perna não estica). As pernas ficam como no agachado; acima da cintura o
desenho gira e anda para a frente, com a rotação crescendo suave numa faixa (sem linha de corte). Serve para quadro de
arte própria (despertado) que não tem kit de peças; no Pengaró base o mesmo dobrar() roda no pengaro_todo.py.

    python3 ferramentas/dobra_agachado.py pengaro_desp_cabecada
    python3 ferramentas/dobra_agachado.py --lutador gbzin      (todas as receitas do lutador)

Quem refaz o lutador inteiro (gerar_<lutador>.py) tem de rodar isto de novo antes da aura e do encolher_sff: o gerador
escreve as ações velhas por cima (o gerar_gbzin.py já chama).

Cada receita (RECEITAS) diz: lutador, ação do .air, desenho do agachado (grupo, índice, já com a arte que o jogo mostra)
e a lista de quadros (graus para a frente, px para a frente na tela 3x, tiques, caixa de ataque ou None). Os desenhos
novos entram no .sff no grupo `grupo` e a ação é reescrita com eles (a Clsn2 padrão da ação fica; sem ela, vale a do
agachado, ação 11). Ação que o despertado também usa pelo [RemapPreset despertado] (o Hazak): `desp=(grupo, índice)`
é o agachado do despertado e `grupo_desp` recebe os mesmos quadros dobrados dele, com a troca escrita no remap. Depois rode
aura_no_corpo.py <lutador> (a aura e os MapSet por elemento saem dos desenhos) e encolher_sff.py <lutador>.
"""
import io
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conferir_sff as cs  # noqa: E402
import efeitos  # noqa: E402
import ligar_pecas as lp  # noqa: E402
from pengaro_todo import dobrar  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
CAIXA_CABECADA = (20, -220, 120, -110)  # testa e ombro do agachado dobrado (a mesma da 410 da base)

RECEITAS = {
    # Pengaró despertado (sombras): cabeçada agachada 10410 do agachado dele (801,0); mesmos tiques até o contato
    # (o efeito do golpe usa AnimElem = 3) e quadros do meio na volta
    "pengaro_desp_cabecada": dict(lutador="pengaro", acao=10410, base=(801, 0), grupo=41410, quadros=[
        (0, 0, 3, None), (-10, -6, 4, None), (20, 16, 2, CAIXA_CABECADA), (20, 16, 6, CAIXA_CABECADA),
        (18, 14, 2, None), (14, 11, 3, None), (11, 9, 3, None), (8, 6, 3, None), (6, 4, 3, None), (4, 3, 3, None),
        (2, 1, 3, None), (0, 0, 3, None), (0, 0, 4, None)]),
    # CK despertado (Ratão): o golpe agachado forte 10410 subia inteiro com a garrafa no alto; agora sai do agachado
    # dele (789,0): recua o tronco e joga o peito e a mão da garrafa para a frente e para cima, pernas paradas
    "ck_desp_agachado_forte": dict(lutador="ck", acao=10410, base=(789, 0), grupo=41410, quadros=[
        (0, 0, 3, None), (-10, -6, 4, None), (18, 16, 2, (10, -250, 96, -120)), (18, 16, 6, (10, -250, 96, -120)),
        (16, 14, 2, None), (13, 11, 3, None), (10, 8, 3, None), (8, 6, 3, None), (6, 4, 3, None), (4, 3, 3, None),
        (2, 1, 3, None), (0, 0, 3, None), (0, 0, 4, None)]),
}
# Hazak: a joelhada subindo (410, "y" agachado) levantava inteira com o joelho no alto; agora sai do agachado dele
# (48000,0; o despertado 21003,0): recua o tronco e entra de ombro e testa, pernas paradas. Mesmo tempo total (29
# tiques) e o contato no tique 7, como o HitDef (Time = 7) pede.
CAIXA_HAZAK = (22, -186, 122, -86)
# Diabo demônio (Hazak despertado): a Garra Subindo (4401, "y" agachado) levantava o corpo inteiro com a garra no
# alto; agora sai do agachado dele (21003,0): o tronco afunda para a frente e desenrola para trás e para cima, as garras
# varrem de baixo para cima, pernas paradas. Mesmos tiques (7, 4, 7, 9) e o contato nos elementos do meio.
CAIXA_GARRA = (-10, -300, 110, -150)
RECEITAS["diabo_garra_subindo"] = dict(lutador="hazaki", acao=4401, base=(21003, 0), grupo=41441, quadros=[
    (0, 0, 3, None), (10, 6, 4, None), (-16, 8, 4, CAIXA_GARRA), (-24, 10, 7, CAIXA_GARRA), (-14, 6, 4, None),
    (-6, 3, 3, None), (0, 0, 2, None)])
RECEITAS["hazak_agachado_forte"] = dict(lutador="hazaki", acao=410, base=(48000, 0), grupo=41410,
                                        desp=(21003, 0), grupo_desp=41411, quadros=[
    (0, 0, 3, None), (-10, -6, 4, None), (26, 22, 2, CAIXA_HAZAK), (26, 22, 6, CAIXA_HAZAK), (18, 14, 3, None),
    (10, 8, 3, None), (5, 4, 3, None), (2, 1, 3, None), (0, 0, 2, None)])


def rgba(n, pal):
    idx = np.frombuffer(n["px"], np.uint8).reshape(n["h"], n["w"])
    p = np.frombuffer(pal, np.uint8).reshape(256, 4)
    img = np.zeros((n["h"], n["w"], 4), np.uint8)
    img[..., :3] = p[idx][..., :3]
    img[..., 3] = np.where(idx == 0, 0, 255)
    return img


def dobrados(base, pal, unicos):
    """(ângulo, dx) -> (recorte RGBA, eixo x, eixo y) do desenho do agachado com o tronco dobrado."""
    if base.get("png"):
        img = np.asarray(Image.open(io.BytesIO(base["px"][4:])).convert("RGBA")).copy()
    else:
        assert base.get("pi", 0) == 0, "o desenho do agachado tem de estar na paleta do lutador ou em PNG"
        img = rgba(base, pal)
    # tela com folga para o tronco girar sem sair da imagem; o eixo do desenho vai junto
    folga = 120
    tela = np.zeros((img.shape[0] + 2 * folga, img.shape[1] + 2 * folga, 4), np.uint8)
    tela[folga:folga + img.shape[0], folga:folga + img.shape[1]] = img
    ax, ay = base["x"] + folga, base["y"] + folga
    saida = []
    for ang, dx in unicos:
        out = dobrar(tela, ang, dx)
        ys, xs = np.nonzero(out[..., 3] > 0)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        saida.append((Image.fromarray(out[y0:y1, x0:x1]), int(ax - x0), int(ay - y0)))
    return saida


def fazer(r):
    lut = r["lutador"]
    sff = RAIZ / "chars" / lut / f"{lut}.sff"
    air = RAIZ / "chars" / lut / f"{lut}.air"
    cns = RAIZ / "chars" / lut / f"{lut}.cns"
    pal, nos, _ = cs.ler(sff)
    extras = list(cs.EXTRAS.get(str(sff.resolve()), []))
    por_chave = {(n["g"], n["i"]): n for n in nos}
    prgb = lp.paleta_rgb(pal)
    unicos = list(dict.fromkeys((a, d) for a, d, _, _ in r["quadros"]))
    novos, novos_png = [], []
    base_png = bool(por_chave[r["base"]].get("png"))  # arte própria do despertado (PNG): os quadros novos também
    for k, (rec, ex, ey) in enumerate(dobrados(por_chave[r["base"]], pal, unicos)):
        if base_png:
            a = np.asarray(rec).copy()
            a[..., 3] = np.where(a[..., 3] > 127, 255, 0)
            novos_png.append((r["grupo"], k, rec.width, rec.height, ex, ey, efeitos.blob_png(Image.fromarray(a))))
        else:
            novos.append((r["grupo"], k, rec.width, rec.height, ex, ey, lp.indexar(rec, prgb).tobytes(), 0))
    grupos = {r["grupo"]}
    if r.get("desp"):
        grupos.add(r["grupo_desp"])
        for k, (rec, ex, ey) in enumerate(dobrados(por_chave[r["desp"]], pal, unicos)):
            a = np.asarray(rec).copy()
            a[..., 3] = np.where(a[..., 3] > 127, 255, 0)
            novos_png.append((r["grupo_desp"], k, rec.width, rec.height, ex, ey, efeitos.blob_png(Image.fromarray(a))))
    rle, png = [], []
    for n in nos:
        if n["g"] in grupos:
            continue  # rodada de novo: troca os desenhos do grupo
        if n.get("png"):
            png.append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
        else:
            rle.append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"], n.get("pi", 0)))
    efeitos.gravar(sff, pal, rle + novos, png + novos_png, extras)
    if r.get("desp"):
        # o despertado troca cada quadro novo pelo dele (RemapPreset), como os outros desenhos da base
        t = cns.read_text(encoding="utf-8")
        m = re.search(r"^\[RemapPreset despertado\]\n", t, re.M)
        assert m, "sem [RemapPreset despertado] no .cns"
        t = re.sub(r"^%d,\d+ = %d,\d+\n" % (r["grupo"], r["grupo_desp"]), "", t, flags=re.M)
        linhas_remap = "".join(f"{r['grupo']},{k} = {r['grupo_desp']},{k}\n" for k in range(len(unicos)))
        t = t[:m.end()] + linhas_remap + t[m.end():]
        cns.write_text(t, encoding="utf-8")
    # ação nova no .air: a Clsn2 padrão da ação antiga fica; a caixa de ataque vem da receita
    texto = air.read_text(encoding="utf-8")
    m = re.search(r"\[Begin Action %d\].*?(?=\n\[Begin Action|\Z)" % r["acao"], texto, re.I | re.S)
    assert m, f"ação {r['acao']} não achada"
    velha = m.group(0)
    padrao = re.search(r"Clsn2Default:[^\n]*\n(?:\s*Clsn2\[\d+\][^\n]*\n)+", velha)
    linhas = [f"[Begin Action {r['acao']}]", "; golpe agachado: o agachado com o tronco dobrando (dobra_agachado.py)"]
    if padrao:
        linhas.append(padrao.group(0).rstrip("\n"))
    else:  # sem caixa padrão (caixa por quadro do desenho velho): vale a do agachado (ação 11)
        m11 = re.search(r"\[Begin Action 11\].*?Clsn2:\s*(\d+)\s*\n((?:\s*Clsn2\[\d+\][^\n]*\n)+)", texto, re.I | re.S)
        assert m11, "sem Clsn2 no agachado (ação 11)"
        linhas.append(f"Clsn2Default: {m11.group(1)}\n" + m11.group(2).rstrip("\n"))
    for ang, dx, t, caixa in r["quadros"]:
        if caixa:
            linhas += ["Clsn1: 1", f" Clsn1[0] = {caixa[0]}, {caixa[1]}, {caixa[2]}, {caixa[3]}"]
        linhas.append(f"{r['grupo']},{unicos.index((ang, dx))}, 0,0, {t}")
    nova = "\n".join(linhas) + "\n"
    texto = texto[:m.start()] + nova + "\n" + texto[m.end():].lstrip("\n")
    air.write_text(texto, encoding="utf-8")
    print(f"{lut}: ação {r['acao']} com {len(r['quadros'])} elementos e {len(unicos)} desenhos no grupo {r['grupo']}")


# ------------------------------------------------------------------ refazer uma ação elemento a elemento
# Para ação de desenho próprio (sem kit) em que só alguns quadros levantam, ou em que o golpe foi desenhado maior que
# o agachado (Gbzin despertado: os golpes agachados têm 332 px e o agachado 267): cada elemento da ação continua com o
# mesmo tique e as mesmas caixas; o desenho dele pode ser trocado (`de`), encolhido em volta do pé (`esc`, as caixas
# encolhem junto) e ter o tronco dobrado (`ang`, `dx`). `caixa` troca a Clsn1 do elemento. Num despertado
# (`despertado=True`) o desenho de origem passa pelo [RemapPreset despertado], como o jogo mostra.
def remap_despertado(cns):
    t = cns.read_text(encoding="utf-8")
    bloco = re.search(r"^\[RemapPreset despertado\]\n(.*?)(?=^\[)", t, re.M | re.S)
    return {(int(g), int(i)): (int(g2), int(i2))
            for g, i, g2, i2 in re.findall(r"^(\d+),\s*(\d+)\s*=\s*(\d+),\s*(\d+)", bloco.group(1), re.M)}


def encolher(img, ax, ay, esc):
    if esc == 1:
        return img, ax, ay
    h, w = img.shape[:2]
    nw, nh = max(1, round(w * esc)), max(1, round(h * esc))
    return np.asarray(Image.fromarray(img).resize((nw, nh), Image.NEAREST)), round(ax * esc), round(ay * esc)


def refazer(r):
    lut = r["lutador"]
    pasta = RAIZ / "chars" / lut
    sff, air, cns = pasta / f"{lut}.sff", pasta / f"{lut}.air", pasta / f"{lut}.cns"
    pal, nos, _ = cs.ler(sff)
    extras = list(cs.EXTRAS.get(str(sff.resolve()), []))
    por_chave = {(n["g"], n["i"]): n for n in nos}
    remap = remap_despertado(cns) if r.get("despertado") else {}
    prgb = lp.paleta_rgb(pal)
    texto = air.read_text(encoding="utf-8")
    m = re.search(r"\[Begin Action %d\].*?(?=\n\[Begin Action|\Z)" % r["acao"], texto, re.I | re.S)
    assert m, f"ação {r['acao']} não achada"
    linhas = m.group(0).split("\n")
    esc0 = r.get("esc", 1.0)
    desenhos, novos, saida, k, pend_caixa = {}, [], [], 0, None
    for ln in linhas:
        el = re.match(r"^\s*(\d+)\s*,\s*(\d+)\s*,(.*)$", ln)
        cx = re.match(r"^(\s*Clsn([12])(?:Default)?(?:\[\d+\])?\s*=\s*)(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)(.*)$", ln)
        if ln.startswith("[Begin Action"):
            saida += [ln, f"; refeita por dobra_agachado.py ({r['nome']}): golpe agachado fica agachado (#32)"]
        elif cx:
            saida.append(ln)  # ajustada quando o elemento chega (a escala é a dele)
        elif el:
            g, i = int(el.group(1)), int(el.group(2))
            mud = dict(r.get("mudar", {}).get(k, {}))
            esc = mud.get("esc", esc0)
            de = mud.get("de", (g, i))
            de = remap.get(de, de)
            ang, dx = mud.get("ang", 0), mud.get("dx", 0)
            chave = (de, esc, ang, dx)
            if chave not in desenhos:
                n = por_chave[de]
                assert not n.get("png") and n.get("pi", 0) == 0, f"{de}: só desenho na paleta do lutador"
                img, ax, ay = encolher(rgba(n, pal), n["x"], n["y"], esc)
                if ang or dx:
                    folga = 120
                    tela = np.zeros((img.shape[0] + 2 * folga, img.shape[1] + 2 * folga, 4), np.uint8)
                    tela[folga:folga + img.shape[0], folga:folga + img.shape[1]] = img
                    out = dobrar(tela, ang, dx)
                    ys, xs = np.nonzero(out[..., 3] > 0)
                    y0, x0 = ys.min(), xs.min()
                    img, ax, ay = out[y0:ys.max() + 1, x0:xs.max() + 1], ax + folga - x0, ay + folga - y0
                rec = Image.fromarray(np.ascontiguousarray(img))
                desenhos[chave] = len(desenhos)
                novos.append((r["grupo"], desenhos[chave], rec.width, rec.height, int(ax), int(ay),
                              lp.indexar(rec, prgb).tobytes(), 0))
            # caixas deste elemento (as linhas Clsn logo acima dele): encolhe ou troca a Clsn1
            j = len(saida)
            while j > 0 and re.match(r"^\s*Clsn", saida[j - 1]):
                j -= 1
            bloco = saida[j:]
            del saida[j:]
            if "caixa" in mud:
                bloco = [b for b in bloco if not re.match(r"^\s*Clsn1", b)]
                if mud["caixa"]:
                    c = mud["caixa"]
                    bloco += ["Clsn1: 1", f" Clsn1[0] = {c[0]}, {c[1]}, {c[2]}, {c[3]}"]
            padrao = False  # linhas depois de "Clsn2Default:" valem para a ação toda: encolhem pela escala geral
            for b in bloco:
                if re.match(r"^\s*Clsn[12](Default)?\s*:", b):
                    padrao = "Default" in b
                cb = re.match(r"^(\s*Clsn[12](?:\[\d+\])?\s*=\s*)(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)(.*)$", b)
                e = esc0 if padrao else esc
                if cb and e != 1 and not (not padrao and mud.get("caixa") and "Clsn1" in b):
                    v = [round(int(cb.group(q)) * e) for q in range(2, 6)]
                    b = f"{cb.group(1)}{v[0]}, {v[1]}, {v[2]}, {v[3]}{cb.group(6)}"
                saida.append(b)
            saida.append(f"{r['grupo']},{desenhos[chave]},{el.group(3)}")
            k += 1
        else:
            saida.append(ln)
    rle, png = [], []
    for n in nos:
        if n["g"] == r["grupo"]:
            continue
        if n.get("png"):
            png.append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"]))
        else:
            rle.append((n["g"], n["i"], n["w"], n["h"], n["x"], n["y"], n["px"], n.get("pi", 0)))
    efeitos.gravar(sff, pal, rle + novos, png, extras)
    texto = texto[:m.start()] + "\n".join(saida) + texto[m.end():]
    air.write_text(texto, encoding="utf-8")
    print(f"{lut}: ação {r['acao']} refeita com {k} elementos e {len(desenhos)} desenhos no grupo {r['grupo']}")


CAIXA_GBZIN = (10, -228, 124, -110)
REFAZER = {
    # Gbzin: a bengalada agachada (410) levantava e erguia a bengala acima da cabeça; agora fica agachado e entra de
    # tronco com a bengala na mão (do 443, o agachado de bengala na cintura). Contato nos mesmos tiques.
    "gbzin_410": dict(lutador="gbzin", acao=410, grupo=41410, mudar={
        2: dict(de=(443, 0), ang=22, dx=18, caixa=CAIXA_GBZIN), 3: dict(de=(443, 0), ang=22, dx=18, caixa=CAIXA_GBZIN),
        4: dict(de=(443, 0), ang=22, dx=18), 5: dict(de=(443, 0), ang=11, dx=9)}),
    # rasteira (440): o último quadro saía em pé; agora volta para o agachado
    "gbzin_440": dict(lutador="gbzin", acao=440, grupo=41440, mudar={7: dict(de=(362, 0))}),
    # despertado: os golpes agachados foram desenhados ~23% maiores que o agachado dele (332 px contra 267): encolhem em
    # volta do pé para o tamanho do agachado; a bengalada é a mesma troca da base
    "gbzin_desp_10400": dict(lutador="gbzin", acao=10400, grupo=41400, despertado=True, esc=0.82),
    "gbzin_desp_10430": dict(lutador="gbzin", acao=10430, grupo=41430, despertado=True, esc=0.82),
    "gbzin_desp_10440": dict(lutador="gbzin", acao=10440, grupo=41444, despertado=True, esc=0.82,
                             mudar={7: dict(de=(362, 0), esc=1.0)}),
    "gbzin_desp_10410": dict(lutador="gbzin", acao=10410, grupo=41411, despertado=True, mudar={
        1: dict(esc=0.9),
        2: dict(de=(443, 0), ang=22, dx=18, caixa=CAIXA_GBZIN), 3: dict(de=(443, 0), ang=22, dx=18, caixa=CAIXA_GBZIN),
        4: dict(de=(443, 0), ang=22, dx=18), 5: dict(de=(443, 0), ang=11, dx=9)}),
}
for _n, _r in REFAZER.items():
    _r["nome"] = _n

# golpe da base refeito em grupo novo cuja forma despertada usa a mesma ação (quando a arte própria do despertado não
# entra, o [RemapPreset despertado] tem que trocar os grupos novos também): grupo da base -> grupo do despertado
REMAP_NOVO = {"gbzin": {41410: 41411, 41440: 41444}}


def ligar_remap(lut):
    cns = RAIZ / "chars" / lut / f"{lut}.cns"
    t = cns.read_text(encoding="utf-8")
    bloco = re.search(r"^\[RemapPreset despertado\]\n(.*?)(?=^\[)", t, re.M | re.S)
    air = (RAIZ / "chars" / lut / f"{lut}.air").read_text(encoding="utf-8")
    novas = []
    for g, g2 in REMAP_NOVO.get(lut, {}).items():
        for i in sorted({int(x) for x in re.findall(rf"^{g},\s*(\d+)", air, re.M)}):
            if not re.search(rf"^{g},\s*{i}\s*=", bloco.group(1), re.M):
                novas.append(f"{g},{i} = {g2},{i}\n")
    if novas:
        fim = bloco.end(1)
        t = t[:fim] + "".join(novas) + t[fim:]
        cns.write_text(t, encoding="utf-8")
    print(f"{lut}: {len(novas)} remaps novos do despertado")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--lutador"]:  # todas as receitas de um lutador (gerador que refaz o lutador inteiro chama isto)
        args = [n for n, r in {**RECEITAS, **REFAZER}.items() if r["lutador"] == args[1]]
    for nome in args or list(RECEITAS) + list(REFAZER):
        refazer(REFAZER[nome]) if nome in REFAZER else fazer(RECEITAS[nome])
    for lut in sorted({(REFAZER.get(n) or RECEITAS.get(n))["lutador"] for n in (args or list(RECEITAS) + list(REFAZER))}):
        if lut in REMAP_NOVO:
            ligar_remap(lut)
