#!/usr/bin/env python3
"""Parry de cada lutador (docs/parry.md, missão do Alisson de 2026-11-14, item 4): em cima e embaixo, folha própria,
faísca própria na cor do lutador e o oponente aberto por 20 ticks.

  python ferramentas/parry.py                       aplica nos 5 lutadores de chars/
  python ferramentas/parry.py pengaro ck            só nesses
  python ferramentas/parry.py --contato PASTA       folhas de contato dos quadros e das faíscas (para olhar)

Trabalha em cima do que já está em chars/<l>/ (sff, air, cns, cmd, movelist), sem regerar o lutador: os outros sprites,
a paleta e as caixas ficam como estão (no Gutto e no Raiclaven o gerador nem roda igual nesta máquina, porque os
quadros 3x do Blender estão fora do git). Pode rodar de novo quantas vezes quiser: o que ele monta é substituído, não
duplicado. Os gerar_<lutador>.py chamam `aplicar` no fim, para o parry não se perder quando o lutador for regerado.

O que muda em cada lutador:
  - sprites 7600,0..7 (parry_alto) e 7640,0..7 (parry_baixo), cortados direto da folha grande em 3x (regra da alta
    resolução: o corpo vai em 3x e o lutador é desenhado em 1/3), na paleta do .sff, com a altura da defesa de hoje;
  - faísca própria 7690 (forma base) e 7691 (forma endiabrada), feita do crit-hit do pixelfx (só a estrela, sem o halo
    que virava o "círculo preto com raios"), pintada na cor do lutador e da forma (issue #38);
  - a faísca pronta do pixelfx (9204, a "rede de futebol") sai de todo lugar: parry, Contragolpe do CK, Guarda de Aço
    do Hazak, a ação 9204 do .air e os sprites do grupo 9204;
  - 760/761: parry em cima (→ + c), pega golpe em pé e aéreo; 764/765: parry embaixo (↓ + c), pega golpe agachado;
  - 761/765 (o acertou, quadros 4 a 8) começam com controle: qualquer golpe cancela a piada;
  - 762 (o oponente aberto): 20 ticks em vez de 14.
Forma endiabrada: enquanto as folhas e_parry_alto/e_parry_baixo não existem, ela usa as ações 10760/10761 de hoje (a
defesa redesenhada pelo [RemapPreset despertado]) também no parry de baixo, com a faísca da forma (7691).
"""
import re
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conferir_sff as cs  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
LUTADORES = ("pengaro", "hazaki", "ck", "gutto", "raiclaven")
E = 3  # o corpo vai em 3x (regra da alta resolução)
G_ALTO, G_BAIXO, G_FAISCA, G_FAISCA_E = 7600, 7640, 7690, 7691
REDE = 9204  # a faísca pronta do pixelfx (círculo com raios): proibida

# Faísca de cada um (docs/parry.md) e da forma endiabrada (issue #38): rampa do escuro (0) ao claro (1).
RAMPAS = {
    "pengaro": (((0, (40, 14, 0)), (.4, (160, 75, 10)), (.75, (240, 170, 45)), (1, (255, 240, 190))),     # âmbar
                ((0, (12, 0, 22)), (.4, (75, 12, 125)), (.8, (155, 65, 235)), (1, (230, 200, 255)))),    # violeta
    "hazaki": (((0, (70, 25, 0)), (.4, (235, 115, 20)), (.75, (255, 195, 100)), (1, (255, 255, 255))),   # branco e laranja
               ((0, (60, 25, 0)), (.4, (220, 120, 0)), (.8, (255, 200, 40)), (1, (255, 245, 180)))),     # laranja-ouro
    "ck": (((0, (55, 0, 0)), (.4, (185, 20, 20)), (.8, (255, 75, 60)), (1, (255, 225, 215))),             # vermelho da luva
           ((0, (20, 28, 22)), (.45, (90, 110, 90)), (.8, (160, 185, 150)), (1, (225, 240, 215)))),       # fumaça
    "gutto": (((0, (45, 15, 0)), (.4, (165, 45, 15)), (.75, (250, 110, 45)), (1, (255, 225, 175))),      # poeira e brasa
              ((0, (35, 0, 0)), (.4, (205, 20, 0)), (.75, (255, 90, 20)), (1, (255, 230, 120)))),        # brasa
    "raiclaven": (((0, (30, 32, 40)), (.45, (125, 130, 145)), (.8, (210, 215, 225)), (1, (255, 255, 255))),  # prata
                  ((0, (0, 30, 12)), (.4, (40, 150, 70)), (.75, (150, 230, 150)), (1, (235, 255, 235)))),    # verde
}
FAISCA_FONTE = "crit-hit"
# (quadro do pixelfx, ticks, escala). Só os dois primeiros quadros, a estrela: do 3º em diante o crit-hit abre o anel
# com raios, que é o mesmo desenho da faísca proibida.
FAISCA_QUADROS = ((0, 2, .42), (1, 2, .5), (1, 2, .38), (1, 2, .26))

# Tempos (ticks). A postura (quadros 1–3) tem a janela de 4 ticks de sempre e o resto é a recuperação de quem errou,
# com a mesma duração de hoje (36). O acertou (quadros 4–8) dura mais que os 20 da abertura do oponente: quem não bate
# perde a vez, e a piada termina com o oponente já de volta.
POSTURA = (3, 3, 30)
ACERTOU = (5, 5, 6, 8, 12)
ABERTURA = 20


# ---------------------------------------------------------------- arte
def figuras(folha):
    """Os 8 desenhos da folha, na resolução dela: [(recorte RGBA, eixo x no recorte, pé y no recorte)].
    O eixo de cada quadro fica no mesmo lugar da célula em que está o tronco do 1º quadro (o corpo não pula de um quadro
    para o outro e o movimento desenhado continua); o chão é a mediana das bases (o pulo do Hazak fica no ar)."""
    import animar_folha as af
    img = af.fundo_ck(Image.open(folha))
    limpa = np.array(af.tira_fundo(img))
    largura = limpa.shape[1] / 8
    n, rotulos, dados, centros = cv2.connectedComponentsWithStats((limpa[..., 3] > 0).astype(np.uint8), connectivity=8)
    celula = np.full(n, -1)
    for i in range(1, n):
        if dados[i, cv2.CC_STAT_AREA] >= 40:
            celula[i] = min(7, int(centros[i][0] // largura))
    cortes = []
    for i in range(8):
        mascara = celula[rotulos] == i
        assert mascara.any(), f"{folha}: quadro {i + 1} vazio"
        figura = Image.fromarray(np.where(mascara[..., None], limpa, 0).astype(np.uint8))
        cortes.append((figura.getchannel("A").getbbox(), figura))
    chao = float(np.median([cx[3] for cx, _ in cortes]))
    cx0, fig0 = cortes[0]
    desvio = cx0[0] + af.tronco(fig0.crop(cx0)) - 0.5 * largura  # tronco do 1º quadro em relação ao meio da célula
    saida = []
    for i, (cx, figura) in enumerate(cortes):
        eixo = (i + .5) * largura + desvio
        saida.append((figura.crop(cx), eixo - cx[0], chao - cx[1]))
    return saida


def sem_halo(q):
    """Alfa seco (sem mistura com o fundo) e sem as franjas rosadas do magenta."""
    from animar_cenario import sem_rosa
    q = q.copy()
    q.putalpha(q.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    return sem_rosa(q)


def quadros_parry(lutador, nome, altura):
    """[(imagem 3x RGBA cortada, eixo x, eixo y)] dos 8 quadros, com o 1º quadro da altura `altura` (px no 3x)."""
    hd = RAIZ / f"sprites/{lutador}/quadros_arcade_hd/{nome}"
    if lutador == "pengaro" and hd.exists():
        # o Pengaró já tem os quadros convertidos (converter_ck/converter_pengaro: tela 1080x780, pés em 540,660)
        saida = []
        for i in range(8):
            q = sem_halo(Image.open(hd / f"{i:02d}.png").convert("RGBA"))
            cx = q.getchannel("A").getbbox()
            saida.append((q.crop(cx), 540 - cx[0], 660 - cx[1]))
        return saida
    figs = figuras(RAIZ / f"sprites/{lutador}/quadros/folhas_arcade/{nome}.png")
    fator = altura / figs[0][0].height
    saida = []
    for q, ex, ey in figs:
        g = q.resize((max(1, round(q.width * fator)), max(1, round(q.height * fator))), Image.LANCZOS)
        g = sem_halo(g)
        cx = g.getchannel("A").getbbox()
        saida.append((g.crop(cx), round(ex * fator) - cx[0], round(ey * fator) - cx[1]))
    return saida


def quadros_faisca(rampa):
    """A estrela do crit-hit do pixelfx, sem o halo cinza (era ele que virava o círculo escuro), na cor da rampa."""
    import json
    fx = RAIZ / "assets/efeitos"
    dados = json.loads((fx / f"{FAISCA_FONTE}.json").read_text(encoding="utf-8"))
    folha = Image.open(fx / dados["meta"]["image"]).convert("RGBA")
    saida = []
    for quadro, ticks, escala in FAISCA_QUADROS:
        r = dados["frames"][quadro]["frame"]
        q = np.asarray(folha.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"]))).astype(np.float32)
        luz = q[..., :3].max(axis=2) / 255
        forte = (q[..., 3] >= 200) & (luz >= .75)  # só o miolo e os raios; o halo é translúcido e apagado
        # o miolo do pixelfx é todo branco: a cor vai pela distância do centro (miolo claro, ponta dos raios escura)
        yy, xx = np.nonzero(forte)
        cy, cx0 = np.average(yy, weights=luz[forte]), np.average(xx, weights=luz[forte])
        dist = np.hypot(*np.mgrid[:q.shape[0], :q.shape[1]] - np.array([cy, cx0])[:, None, None])
        tom = np.clip(1 - dist / max(1, dist[forte].max()), 0, 1) ** 1.6 * .85 + .15
        cor = np.stack([np.interp(tom, [p for p, _ in rampa], [c[k] for _, c in rampa]) for k in range(3)], axis=-1)
        img = Image.fromarray(np.dstack([cor, np.where(forte, 255, 0)]).astype(np.uint8), "RGBA")
        img = img.resize((max(1, round(img.width * escala)), max(1, round(img.height * escala))), Image.LANCZOS)
        img.putalpha(img.getchannel("A").point(lambda v: 255 if v >= 90 else 0))  # raio fino não some na redução
        cx = img.getchannel("A").getbbox()
        meio = (img.width / 2, img.height / 2)
        saida.append((img.crop(cx), round(meio[0] - cx[0]), round(meio[1] - cx[1]), ticks))
    return saida


def quantizar(img, pal):
    """Pixels do .sff (índices da paleta do lutador; 0 é o transparente), pela cor mais perto."""
    cores = np.frombuffer(pal, np.uint8).reshape(-1, 4)[:256, :3].astype(np.int32)
    a = np.asarray(img.convert("RGBA")).astype(np.int32)
    rgb = a[..., :3].reshape(-1, 3)
    unicas, inv = np.unique(rgb, axis=0, return_inverse=True)
    d = ((unicas[:, None, :] - cores[None, 1:, :]) ** 2).sum(axis=2)
    idx = (d.argmin(axis=1) + 1).astype(np.uint8)[inv.reshape(-1)]
    idx[a[..., 3].reshape(-1) < 128] = 0
    return bytes(idx)


# ---------------------------------------------------------------- .air
RE_ACAO = re.compile(r"^\[Begin Action (\d+)\][^\n]*\n(.*?)(?=^\[Begin Action|\Z)", re.M | re.S)


def acao(air, numero):
    m = re.search(rf"^\[Begin Action {numero}\][^\n]*\n(.*?)(?=^\[Begin Action|\Z)", air, re.M | re.S)
    return m.group(1) if m else None


def tirar_acao(air, numero):
    return re.sub(rf"^\[Begin Action {numero}\][^\n]*\n.*?(?=^\[Begin Action|\Z)", "", air, flags=re.M | re.S)


def por_acao(air, numero, texto):
    """Troca a ação (ou põe no fim, se não existe)."""
    bloco = f"[Begin Action {numero}]\n{texto.rstrip()}\n\n"
    if acao(air, numero) is None:
        return air.rstrip() + "\n\n" + bloco
    return re.sub(rf"^\[Begin Action {numero}\][^\n]*\n.*?(?=^\[Begin Action|\Z)", lambda m: bloco, air,
                  count=1, flags=re.M | re.S)


def caixas_da_defesa(air):
    """(Clsn2 do corpo, Clsn1 que apara) da ação 760 de hoje, em unidades do .air (já 3x)."""
    a = acao(air, 760)
    clsn2 = re.search(r"Clsn2(?:Default)?:\s*\d+\s*\n\s*Clsn2\[0\]\s*=\s*([-\d, ]+)", a)
    clsn1 = re.search(r"Clsn1(?:Default)?:\s*\d+\s*\n\s*Clsn1\[0\]\s*=\s*([-\d, ]+)", a)
    corpo = [int(v) for v in clsn2.group(1).split(",")]
    apara = [int(v) for v in clsn1.group(1).split(",")]
    return corpo, apara


def texto_acao(grupo, quadros, ticks, corpo, apara=None):
    linhas = ["Clsn2Default: 1", f" Clsn2[0] = {', '.join(map(str, corpo))}"]
    if apara:
        linhas += ["Clsn1Default: 1", f" Clsn1[0] = {', '.join(map(str, apara))}"]
    linhas += [f"{grupo},{q}, 0,0, {t}" for q, t in zip(quadros, ticks)]
    return "\n".join(linhas)


def montar_air(air, tem_despertado):
    corpo, apara = caixas_da_defesa(air)
    x0, y_topo, x1, y_pe = apara
    # embaixo: a mesma largura, só a metade de baixo do corpo (onde a rasteira e o chute agachado chegam)
    apara_baixo = [x0, round(corpo[3] * .45), x1, 0]
    air = por_acao(air, 760, texto_acao(G_ALTO, (0, 1, 2), POSTURA, corpo, apara))
    air = por_acao(air, 761, texto_acao(G_ALTO, (3, 4, 5, 6, 7), ACERTOU, corpo))
    air = por_acao(air, 764, texto_acao(G_BAIXO, (0, 1, 2), POSTURA, corpo, apara_baixo))
    air = por_acao(air, 765, texto_acao(G_BAIXO, (3, 4, 5, 6, 7), ACERTOU, corpo))
    if tem_despertado:
        # endiabrado sem folha própria ainda: a mesma defesa redesenhada de hoje, com a caixa de baixo no 10764
        e760 = acao(air, 10760)
        e760_baixo = re.sub(r"(Clsn1\[0\]\s*=\s*)[-\d, ]+", lambda m: m.group(1) + ", ".join(map(str, apara_baixo)),
                            e760)
        air = por_acao(air, 10764, e760_baixo)
        air = por_acao(air, 10765, acao(air, 10761))
    for g in (G_FAISCA, G_FAISCA_E):
        ticks = [t for *_, t in FAISCA_QUADROS]
        air = por_acao(air, g, "\n".join(f"{g},{i}, 0,0, {t}" for i, t in enumerate(ticks)))
    air = tirar_acao(air, REDE)
    return re.sub(r"\n{3,}", "\n\n", air)


# ---------------------------------------------------------------- .cns
FAISCA = f"S(ifelse(var(20) > 0, {G_FAISCA_E}, {G_FAISCA}))"


def estado_parry(postura, acertou, atributos, tipo, despertado, nome):
    arte = (lambda n: f"[State {n}, Arte despertada]\ntype = ChangeAnim\ntrigger1 = Time = 0\ntrigger1 = var(20) > 0\n"
                      f"value = {10000 + n}\n\n") if despertado else (lambda n: "")
    return (f"; parry {nome} (docs/parry.md): {postura} é a postura (quadros 1-3, janela de 4 ticks), {acertou} é o "
            f"acertou (quadros 4-8, com controle: qualquer golpe cancela a piada)\n"
            f"[Statedef {postura}]\ntype = {tipo}\nmovetype = A\nphysics = N\nctrl = 0\nsprpriority = 2\n"
            f"anim = {postura}\nvelset = 0,0\n\n"
            + arte(postura) +
            f"[State {postura}, Desvia]\ntype = ReversalDef\ntrigger1 = Time < 4\nreversal.attr = {atributos}\n"
            f"pausetime = 0,0\nsparkno = {FAISCA}\np1stateno = {acertou}\np2stateno = 762\n\n"
            f"[State {postura}, Fim]\ntype = ChangeState\ntrigger1 = AnimTime = 0\nvalue = {0 if tipo == 'S' else 11}\n"
            f"ctrl = 1\n\n"
            f"[Statedef {acertou}]\ntype = S\nmovetype = I\nphysics = N\nctrl = 1\nsprpriority = 2\n"
            f"anim = {acertou}\nvelset = 0,0\n\n"
            + arte(acertou) +
            f"[State {acertou}, Fim]\ntype = ChangeState\ntrigger1 = AnimTime = 0\nvalue = 0\nctrl = 1\n\n")


def montar_cns(cns, despertado):
    m = re.search(r"^(?:; parry em cima[^\n]*\n)?\[Statedef 760\].*?(?=^\[Statedef 762\])", cns, re.M | re.S)
    assert m, "sem Statedef 760..762 no .cns"
    novo = (estado_parry(760, 761, "SA, NA, SA, HA", "S", despertado, "em cima")
            + estado_parry(764, 765, "C, NA, SA, HA", "C", despertado, "embaixo"))
    cns = cns[:m.start()] + novo + cns[m.end():]
    # oponente aberto: 20 ticks
    m = re.search(r"^\[Statedef 762\].*?(?=^\[Statedef)", cns, re.M | re.S)
    bloco = re.sub(r"Time >= \d+", f"Time >= {ABERTURA}", m.group(0))
    cns = cns[:m.start()] + bloco + cns[m.end():]
    return cns.replace(f"sparkno = S{REDE}", f"sparkno = {FAISCA}")


# ---------------------------------------------------------------- .cmd e lista de golpes
CMD_BAIXO = '[Command]\nname = "parry_baixo"\ncommand = /$D, c\ntime = 1\nbuffer.time = 1\n\n'
ENTRADA_BAIXO = ("[State -1, Parry embaixo]\ntype = ChangeState\nvalue = 764\ntriggerall = command = \"parry_baixo\"\n"
                 "triggerall = statetype != A\ntrigger1 = ctrl\n\n")


def montar_cmd(cmd):
    crlf = "\r\n" in cmd
    cmd = cmd.replace("\r\n", "\n")
    if 'name = "parry_baixo"' not in cmd:
        cmd = re.sub(r'(?=^\[Command\]\nname = "parry"\n)', lambda m: CMD_BAIXO, cmd, count=1, flags=re.M)
        cmd = re.sub(r"(?=^\[State -1, Parry\]\n)", lambda m: ENTRADA_BAIXO, cmd, count=1, flags=re.M)
    assert cmd.count('name = "parry_baixo"') == 1 and cmd.count("[State -1, Parry embaixo]") == 1, "parry no .cmd"
    return cmd.replace("\n", "\r\n") if crlf else cmd


def alinhar_movelist(txt):
    """Comando sempre encostado à direita: o IKEMEN centraliza o pedaço que vem depois de UM tab e só alinha à
    direita depois de dois ou mais; com espaço ele cola no nome. Nome comprido com um tab só ficava com os botões
    em cima das letras (revisão geral 2026-11-14). Separador = o primeiro tab ou 2+ espaços depois do nome."""
    linhas = []
    for ln in txt.split("\n"):
        m = re.match(r"^(?!<#)(\S.*?\S|\S)(?:\t+| {2,})(\S.*)$", ln)
        linhas.append(f"{m.group(1)}\t\t{m.group(2).rstrip()}" if m else ln)
    return "\n".join(linhas)


def montar_movelist(txt):
    if "Parry embaixo" in txt:
        return alinhar_movelist(txt)
    m = re.search(r"^Parry([ \t]+)(\S+)[ \t]*$", txt, re.M)
    if not m:
        return txt
    esp, cmd = m.group(1), m.group(2)
    esp = esp[:-2] if esp.count("\t") > 2 else esp if "\t" in esp else " " * max(1, len(esp) - 8)  # "em cima " tem 8 letras: a coluna do comando não anda
    return alinhar_movelist(txt[:m.start()] + f"Parry em cima{esp}{cmd}\n"
                            + f"Parry embaixo{esp}{cmd.replace('_F', '_D', 1)}" + txt[m.end():])


# ---------------------------------------------------------------- .sff
def montar_sff(lutador, pasta, air):
    import gerar_pengaro as gp
    sff = pasta / f"{lutador}.sff"
    pal, nos, _ = cs.ler(sff)
    nossos = {G_ALTO, G_BAIXO, G_FAISCA, G_FAISCA_E, REDE}
    vistos, itens, retratos = set(), [], {}
    for n in nos:
        k = (n["g"], n["i"])
        if n["g"] in nossos or k in vistos:
            continue
        vistos.add(k)
        if n.get("png"):
            retratos[k] = n["px"]
            # o trocar_retratos.py põe o PNG de volta. O marcador tem pixels que nenhum sprite tem: um igual viraria link
            # para ele (gravar_sff) e passaria a mostrar o retrato (aconteceu com o 9208,0 do Hazak, de 1x1)
            itens.append((n["g"], n["i"], 7, 3, 0, 0, bytes(range(231 + 3 * n["i"], 252 + 3 * n["i"]))))
            continue
        itens.append(cs._item(n))  # com o índice de paleta (a paleta própria do despertado do Raiclaven)
    # altura do 1º quadro do parry (a guarda) = a do 1º desenho da defesa em pé (ação 130)
    prim = re.search(r"^\s*(\d+)\s*,\s*(\d+)\s*,", acao(air, 130) or "", re.M)
    ref = next((n for n in nos if (n["g"], n["i"]) == (int(prim.group(1)), int(prim.group(2)))), None) if prim else None
    altura = ref["h"] if ref else 330
    novos = []
    for grupo, nome in ((G_ALTO, "parry_alto"), (G_BAIXO, "parry_baixo")):
        for i, (q, ex, ey) in enumerate(quadros_parry(lutador, nome, altura)):
            novos.append((grupo, i, q.width, q.height, ex, ey, quantizar(q, pal)))
    base, endiabrado = RAMPAS[lutador]
    for grupo, rampa in ((G_FAISCA, base), (G_FAISCA_E, endiabrado)):
        for i, (q, ex, ey, _) in enumerate(quadros_faisca(rampa)):
            novos.append((grupo, i, q.width, q.height, ex, ey, quantizar(q, pal)))
    gp.gravar_sff(sff, pal, itens + novos, cs.EXTRAS.get(str(sff), []))
    if retratos:
        subprocess.run([sys.executable, str(RAIZ / "ferramentas/trocar_retratos.py"), lutador], check=True,
                       capture_output=True)
        _, depois, _ = cs.ler(sff)
        for n in depois:
            if (n["g"], n["i"]) in retratos:
                assert n.get("png") and n["px"] == retratos[(n["g"], n["i"])], f"{lutador}: retrato {n['g']},{n['i']} mudou"
    return altura, len(novos)


# ---------------------------------------------------------------- tudo
def aplicar(lutador, pasta=None):
    pasta = Path(pasta) if pasta else RAIZ / "chars" / lutador
    arq = {ext: pasta / f"{lutador}.{ext}" for ext in ("air", "cns", "cmd")}
    txt = {ext: p.read_bytes().decode("utf-8") for ext, p in arq.items()}  # sem traduzir o CRLF do .cmd
    despertado = acao(txt["air"], 10760) is not None
    altura, n = montar_sff(lutador, pasta, txt["air"])
    arq["air"].write_text(montar_air(txt["air"], despertado), encoding="utf-8", newline="\n")
    arq["cns"].write_text(montar_cns(txt["cns"], despertado), encoding="utf-8", newline="\n")
    arq["cmd"].write_bytes(montar_cmd(txt["cmd"]).encode("utf-8"))
    mov = pasta / "movelist.dat"
    if mov.exists():
        mov.write_text(montar_movelist(mov.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    print(f"{lutador}: parry em cima e embaixo, {n} sprites novos (1º quadro com {altura} px em 3x)"
          + ("; endiabrado com a defesa redesenhada" if despertado else ""))


def contato(destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    for lutador in LUTADORES:
        if f"{G_ALTO}," not in (RAIZ / f"chars/{lutador}/{lutador}.air").read_text(encoding="utf-8"):
            continue
        pal, nos, _ = cs.ler(RAIZ / f"chars/{lutador}/{lutador}.sff")
        cores = np.frombuffer(pal, np.uint8).reshape(-1, 4)[:256, :3]
        linhas = []
        for g in (G_ALTO, G_BAIXO, G_FAISCA, G_FAISCA_E):
            qs = sorted((n for n in nos if n["g"] == g), key=lambda n: n["i"])
            esc = 1 if g < G_FAISCA else 4
            larg, alt = max(n["w"] for n in qs) * esc + 40, 380 if g < G_FAISCA else 4 * max(n["h"] for n in qs) + 20
            tira = Image.new("RGB", (larg * len(qs), alt), (70, 90, 120))
            for k, n in enumerate(qs):
                idx = np.frombuffer(n["px"], np.uint8).reshape(n["h"], n["w"])
                rgb = cores[idx]
                alfa = np.where(idx > 0, 255, 0).astype(np.uint8)
                img = Image.fromarray(np.dstack([rgb, alfa]).astype(np.uint8), "RGBA")
                img = img.resize((n["w"] * esc, n["h"] * esc), Image.NEAREST)
                if g < G_FAISCA:
                    px, py = k * larg + larg // 2 - n["x"], alt - 20 - n["y"]
                else:
                    px, py = k * larg + larg // 2 - n["x"] * esc, alt // 2 - n["y"] * esc
                tira.paste(img, (px, py), img)
            linhas.append(tira)
        w = max(t.width for t in linhas)
        folha = Image.new("RGB", (w, sum(t.height for t in linhas)), (40, 40, 40))
        y = 0
        for t in linhas:
            folha.paste(t, (0, y))
            y += t.height
        folha.save(destino / f"parry_{lutador}.png")
        print(destino / f"parry_{lutador}.png")


def main():
    args = sys.argv[1:]
    if args[:1] == ["--contato"]:
        contato(args[1])
        return
    for lutador in args or LUTADORES:
        aplicar(lutador)


if __name__ == "__main__":
    main()
