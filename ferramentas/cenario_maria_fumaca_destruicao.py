#!/usr/bin/env python3
"""Destruição em dois níveis da Maria Fumaça (issue #35, missão dos cenários 4.2), sem regerar o cenário aprovado.

  cd ferramentas && python3 cenario_maria_fumaca_destruicao.py

O .sff aprovado da Maria Fumaça (2026-11-12) não bate mais com os PNG de cenarios/maria_fumaca, então o cenário não
pode passar de novo pelo gerar_cenario.py. Este script monta só as camadas novas (num cenário de rascunho, com o
gerar_cenario.py), e enxerta no stages/maria_fumaca.def/.sff:
  - sprites do rascunho com o grupo + 100 e ações + 600 (o cenário aprovado usa grupos 0 a 7 e ações 1001 a 1007);
  - os [BG] novos logo depois do último [BG] aprovado, e os [BGCtrlDef destruicao] no fim;
  - o povo do salão (banco, mesas) e o desfile lá fora (dioquevara, paredão, galera) passam para o grupo 909 (nível 0):
    somem quando a destruição começa (o banco e as mesas vazios já estão desenhados no salão).
Rodar de novo tira o enxerto anterior antes (o que fica entre as marcas e os grupos de 100 a 899 do .sff).
Arte do nível 2: sprites/cenarios/maria_fumaca/bruto/cena_destruida.png (ChatGPT, chat "Pixel Art Background Request",
conta do Alisson): o salão com o telhado furado, a locomotiva fora dos trilhos, pilares tortos, lustre no chão.
"""
import json
import random
import re
import shutil
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

from cenario_katiara import alfa_duro, sem_magenta
from cenario_passarela import com_1024, largura_1536
from gerar_cenario import gerar
from layout_sff import escrever_sff2_bruto, ler_sff2

RAIZ = Path(__file__).resolve().parent.parent
BRUTO = RAIZ / "sprites" / "cenarios" / "maria_fumaca" / "bruto"
SAIDA = RAIZ / "cenarios" / "maria_fumaca" / "destruicao"
STAGES = RAIZ / "stages"
LARGURA = 1672           # o salão aprovado tem 1672 x 941, começando em (-836, -173)
MARGEM = (LARGURA - 1280) // 2
TOPO_SALAO = -173
K = LARGURA / 1532       # a ruína (1532 de largura) cobre o mundo inteiro
TOPO_RUINA = 660 - round(860 * K)   # o piso de pedra das ruínas (y 860) fica no pé dos lutadores
GRUPO, ACAO = 100, 600
SAI_DO_NIVEL_0 = ("dioquevara", "paredao", "galera", "banco", "mesas")
INICIO, FIM = "; --- destruição do cenário (cenario_maria_fumaca_destruicao.py) ---", "; --- fim da destruição ---"


def S(x, y):
    """Ponto do salão aprovado (1672 x 941) na tela em repouso."""
    return x - MARGEM, TOPO_SALAO + y


def R(x, y):
    """Ponto da ruína (1532 x 1023) na tela em repouso."""
    return round(x * K) - MARGEM, TOPO_RUINA + round(y * K)


def noite(seed=9):
    """Céu da noite atrás dos furos do telhado e dos arcos: degradê azul escuro, estrelas e o vermelho do fogo embaixo."""
    w, h = 1280, 960
    img = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(0, h, 4):
        t = y / h
        if t < 0.7:
            c = tuple(round(a + (b - a) * t / 0.7) for a, b in zip((8, 10, 30), (26, 30, 72)))
        else:
            c = tuple(round(a + (b - a) * (t - 0.7) / 0.3) for a, b in zip((26, 30, 72), (90, 34, 30)))
        d.rectangle([0, y, w, y + 3], fill=c + (255,))
    rnd = random.Random(seed)
    for _ in range(140):
        x, y = rnd.randrange(0, w, 4), rnd.randrange(0, int(h * 0.6), 4)
        v = rnd.choice((150, 190, 235))
        d.rectangle([x, y, x + 3, y + 3], fill=(v, v, min(255, v + 20), 255))
    return img


def camadas_novas():
    from cenario_destruicao import Destruicao
    SAIDA.mkdir(parents=True, exist_ok=True)
    d = Destruicao(SAIDA)

    # ---- nível 1: por cima do salão de sempre ----
    d.rachaduras(-MARGEM, 0, LARGURA, 720, [(x + MARGEM, y, c, a) for (x, y), c, a in
                 [(S(300, 520), 120, 70), (S(1110, 470), 110, 110), (S(1500, 560), 110, 80)]], 1, seed=2,
                 torto=0.55, grosso=5)
    d.rachaduras(-MARGEM, 0, LARGURA, 720, [(x + MARGEM, y, c, a) for (x, y), c, a in
                 [(S(420, 800), 260, 5), (S(1240, 820), 240, 175)]], 1, seed=3, achata=0.4, torto=0.45, grosso=6)
    d.fogo_com_fumaca(*S(330, 150), 90, 1, seed=1)                  # o madeiramento do telhado
    d.fogo_com_fumaca(*S(1380, 150), 90, 1, seed=2, fase=3)
    d.fogo_com_fumaca(*S(1540, 690), 110, 1, seed=3, fase=5)        # as mesas largadas
    d.fogo_com_fumaca(*S(130, 690), 100, 1, seed=4, fase=2)         # a porta da esquerda
    d.peca("entulho_m", S(560, 0)[0], S(0, 724)[1], 100, 1)
    d.peca("entulho_p", S(1180, 0)[0], S(0, 718)[1], 64, 1)
    d.correndo(0, S(0, 712)[1], 250, 1, 6.5, -900, 2300)
    d.correndo(1, S(0, 718)[1], 250, 1, -5.5, 2400, 3100)
    d.fagulhas(80, 1, seed=5, quantas=30)
    d.clarao_do_fogo(1, (26, 9, 0))
    nivel1 = d.camadas
    d.camadas = []

    # ---- nível 2: o salão em ruínas ----
    noite().save(SAIDA / "noite.png")
    ceu2 = {"nome": "noite_ruina", "imagem": "noite.png", "delta": [0, 0], "x": 0, "y": -220, "nivel": "2"}
    ruina = com_1024(largura_1536(sem_magenta(Image.open(BRUTO / "cena_destruida.png"))))
    ruina = alfa_duro(ruina.crop((0, 0, 1532, 1024)).resize((LARGURA, round(1024 * K)), Image.LANCZOS))
    ruina.save(SAIDA / "salao_ruina.png")
    base2 = {"nome": "salao_ruina", "imagem": "salao_ruina.png", "delta": [1, 1], "x": -MARGEM, "y": TOPO_RUINA,
             "nivel": "2"}
    d.fogo_com_fumaca(*R(560, 330), 120, 2, seed=11)                # beira do furo do telhado
    d.fogo_com_fumaca(*R(1200, 300), 110, 2, seed=12, fase=4)
    d.fogo_com_fumaca(*R(900, 640), 150, 2, seed=13, fase=2)        # a locomotiva tombada
    d.fogo_com_fumaca(*R(200, 760), 90, 2, seed=14, fase=6)         # o banco partido
    d.fogo_com_fumaca(*R(1330, 790), 90, 2, seed=15, fase=1)        # as mesas
    d.peca("caido_velho", R(420, 0)[0], R(0, 818)[1], 64, 2)
    d.peca("caida_amarela", R(1060, 0)[0], R(0, 824)[1], 60, 2, espelha=True)
    d.correndo(0, R(0, 792)[1], 250, 2, 7.5, -700, 1700)
    d.correndo(1, R(0, 798)[1], 250, 2, -6, 2200, 2300)
    d.correndo(0, R(0, 788)[1], 250, 2, -8, 3600, 2900)
    d.fagulhas(40, 2, seed=6, quantas=70, alto=520)
    d.clarao_do_fogo(2, (44, 14, 0))
    d.peca("caida_sacola", 40, 718, 80, 2, frente=True)             # na frente dos lutadores, rente à tela
    nivel2 = d.camadas
    return (nivel1 + [ceu2, base2] + [c for c in nivel2 if not c.get("frente")] +
            [c for c in nivel2 if c.get("frente")])


def secoes(txt):
    """Divide o .def em [(cabeçalho, texto da seção inteira)], o que vem antes da 1ª seção fica com cabeçalho ''."""
    partes = re.split(r"(?m)^(?=\[)", txt)
    return [((re.match(r"\[([^\]]*)\]", p) or [None, ""])[1], p) for p in partes]


def renumerar(sec):
    nome, t = sec
    t = re.sub(r"(?m)^(actionno\s*=\s*)(\d+)", lambda m: f"{m[1]}{int(m[2]) + ACAO}", t)
    t = re.sub(r"(?m)^(spriteno\s*=\s*)(\d+)", lambda m: f"{m[1]}{int(m[2]) + GRUPO}", t)
    if nome.lower().startswith("begin action"):
        n = int(nome.split()[-1])
        t = t.replace(f"[{nome}]", f"[Begin Action {n + ACAO}]", 1)
        t = re.sub(r"(?m)^(\d+)(\s*,)", lambda m: f"{int(m[1]) + GRUPO}{m[2]}", t)
    return t.rstrip("\n") + "\n\n"


def main():
    camadas = camadas_novas()
    desc = {"id": "maria_fumaca", "nome": "Maria Fumaça", "musica": "", "tela": [1280, 720],
            "largura_mundo": LARGURA, "subida": 160, "chao_y": 660,
            "camera": {"tensao": 200, "segue_vertical": 0.6, "tensao_chao": 120},
            "jogadores": {"p1x": -280, "p2x": 280, "margem_tela": 60}, "reflexo": 0, "camadas": camadas}
    (SAIDA / "destruicao.json").write_text(json.dumps(desc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    with tempfile.TemporaryDirectory() as tmp:
        gerar(desc, SAIDA, Path(tmp), aceita_furo=True)
        novo_def = (Path(tmp) / "maria_fumaca.def").read_text(encoding="utf-8")
        novo_sff = ler_sff2(Path(tmp) / "maria_fumaca.sff")

    arq_def, arq_sff = STAGES / "maria_fumaca.def", STAGES / "maria_fumaca.sff"
    txt = arq_def.read_text(encoding="utf-8")
    nl = "\r\n" if "\r\n" in txt else "\n"
    txt = txt.replace("\r\n", "\n")
    # tira o enxerto anterior
    txt = re.sub(re.escape(INICIO) + r".*?" + re.escape(FIM) + r"\n*", "", txt, flags=re.S)
    velhos = secoes(txt)
    # povo e desfile: id do grupo 909 (nível 0)
    for i, (nome, t) in enumerate(velhos):
        if nome.startswith("BG ") and nome[3:] in SAI_DO_NIVEL_0:
            velhos[i] = (nome, re.sub(r"(?m)^id\s*=\s*\d+", "id = 909", t))
    novos = [s for s in secoes(novo_def.replace("\r\n", "\n")) if s[0]]
    bgs = [renumerar(s) for s in novos if s[0].startswith("BG ")]
    acoes = [renumerar(s) for s in novos if s[0].lower().startswith("begin action") and s[0].split()[-1] != "9000"]
    ctrls = [s[1].rstrip("\n") + "\n\n" for s in novos if s[0].startswith("BGCtrl")]
    if not any("ctrlID = 909" in c for c in ctrls):
        ctrls += ["[BGCtrlDef destruicao 909]\nlooptime = -1\nctrlID = 909\n\n",
                  "[BGCtrl destruicao 909]\ntype = Visible\ntime = 0, 2000000000\nvalue = 1\nsctrlid = 909\n\n"]
    ultimo_bg = max(i for i, (n, _) in enumerate(velhos) if n.startswith("BG "))
    bloco_bg = INICIO + "\n" + "".join(bgs) + FIM + "\n\n"
    bloco_fim = INICIO + "\n" + "".join(acoes) + "".join(ctrls) + FIM + "\n"
    saida = "".join(t for _, t in velhos[:ultimo_bg + 1]) + bloco_bg + \
        "".join(t for _, t in velhos[ultimo_bg + 1:]).rstrip("\n") + "\n\n" + bloco_fim
    arq_def.write_text(saida.replace("\n", nl), encoding="utf-8", newline="")

    sff = {k: v for k, v in ler_sff2(arq_sff).items() if not (GRUPO <= k[0] < 900)}
    itens = [(g, n, w, h, ax, ay, png) for (g, n), (w, h, ax, ay, _f, png) in sff.items()]
    itens += [(g + GRUPO, n, w, h, ax, ay, png) for (g, n), (w, h, ax, ay, _f, png) in novo_sff.items()
              if g < 9000]
    escrever_sff2_bruto(arq_sff, itens)
    print(f"{arq_def}: {len(bgs)} camadas novas, {len(itens) - len(sff)} sprites novos; "
          f"{', '.join(SAI_DO_NIVEL_0)} no nível 0")


if __name__ == "__main__":
    main()
