"""MOLDE de uma aura nova pelo método do Blender. Copie para <lutador>_<aura>.py e preencha o bloco DECLARE.

O exemplo completo e aprovado é hazak_asas.py (asas + coroa + brasa + notas + gotas). Este molde é o mínimo que já
sai certo: UMA peça com ossos em cadeia (chicote), fogo subindo da borda dela e fagulhas nascendo nas juntas.
Passo a passo em docs/arcade/aura_blender.md.

    python ferramentas/aura_blender/<arquivo>.py <pasta de trabalho>                  # tudo
    python ferramentas/aura_blender/<arquivo>.py <pasta de trabalho> pontos chicote   # só o movimento (1 s)

O que uma aura declara: (1) recortes, (2) ossos, (3) animação, (4) camadas procedurais, (5) paleta.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import comum as C

# >>> DECLARE ----------------------------------------------------------------------------------------------------------
ID = "lutador"                      # pasta em sprites/
AURA = "nome_da_aura"
SRC = os.path.join(C.RAIZ, "sprites", ID, "quadros", "folhas_arcade", "d_conceito.png")   # conceito APROVADO, fundo magenta

# (1) RECORTES. Abra o conceito num editor e anote, em px do conceito:
CORPO_X = (0, 0)                    # colunas de uma vista só com o corpo (sem aura), para poder tirar o corpo da aura
AURA_X = (0, 0)                     # colunas da vista com corpo + aura
CAIXA = (0, 0, 0, 0)                # x0, y0, x1, y1 da peça dentro da vista com aura
# eixo do corpo (x) e chão (y da sola) na vista com aura; escala = altura do corpo no jogo / altura no conceito
TELA = C.Tela(cx=0.0, chao=0.0, escala=112 / 441.0)
QUENTE = True                       # aura de fogo/ouro/brasa: todo azul acima do verde é derrame de magenta.
#                                     Aura fria (gelo, raio, roxo): False, e confira a borda na prévia.

# (2) OSSOS em px do conceito: (nome, pai, cabeça, cauda). O primeiro é a raiz: a cabeça dele é o pivô da peça.
# Uma cadeia por "dedo"; quanto mais comprida a peça, mais juntas (3 a 5) para a ponta poder atrasar.
OSSOS = [
    ("a", None, (0, 0), (0, 0)),
    ("b", "a", (0, 0), (0, 0)),
    ("c", "b", (0, 0), (0, 0)),
]

# (3) ANIMAÇÃO por junta: (amplitude em graus, atraso em fração do ciclo, amplitude do 2º harmônico, fase dele).
# Regra do chicote: raiz gira POUCO e CEDO, cada junta adiante gira MAIS e mais TARDE. Nunca a mesma amplitude e
# atraso zero em todas: isso é placa rígida girando.
ANIM = {"a": (3.0, 0.00, 0.0, 0.0), "b": (5.0, 0.12, 0.8, 0.0), "c": (8.0, 0.26, 2.0, 0.0)}
N = 48                              # quadros do laço (48 a 2 tiques = 1,6 s). Passo da ponta > 3 px? Aumente N.
TIQ = 2                             # tiques do jogo por quadro
CENTRO = 0.0                        # desloca a pose média (em amplitudes); negativo = bate mais para baixo
TREMOR = [dict(eixo="X", raio=9.0, fase=0.0, forca=5.0), dict(eixo="Z", raio=11.0, fase=2.1, forca=6.5)]   # pano/pena/fumaça


def respira(t, ox, oz):
    """A peça inteira também se mexe (t = 0..2*pi no laço): só senos de múltiplos inteiros de t."""
    return dict(location=(ox + 1.0 * math.sin(t + 0.9), 0, oz - 2.5 * math.sin(t + 0.5)),
                scale=(1 - 0.04 * (0.5 - 0.5 * math.sin(t - 0.2)), 1, 1))


# (4) CAMADAS PROCEDURAIS (em compor): fogo na borda e fagulhas. NPART = laço das partículas (2 ciclos da peça,
# para não repetirem a cada batida). Nascem nas juntas listadas, em quadros espalhados.
NPART = 2 * N
FAGULHAS = 40
NASCE_EM = ["peca_b", "peca_c"]     # pontos exportados pelo Blender: "peca_<osso>" (a cauda do osso) e "peca_raiz"

# (5) PALETA: 14 cores tiradas do próprio desenho + 1 escura de contorno (a dos lutadores puxada para o tom da aura)
ESCURA = (52, 14, 10)
PLANO = "atras"                     # a peça fica atrás ou à frente do corpo no jogo
# <<< DECLARE ----------------------------------------------------------------------------------------------------------


def recortes(pasta):
    from scipy import ndimage as ndi
    from PIL import Image
    rec = os.path.join(pasta, "recortes"); os.makedirs(rec, exist_ok=True)
    im = C.le_rgb(SRC); H, W = im.shape[:2]
    fg = C.chave_magenta(im)
    corpo = C.recorta_corpo(fg, im, *CORPO_X)
    Image.fromarray(np.dstack([im, (corpo * 255).astype(np.uint8)])).save(f"{rec}/corpo.png")
    dx, dy, nota = C.casa_corpo(im, corpo, *AURA_X)              # onde o corpo reaparece na vista com aura
    print("corpo casado: dx", dx, "dy", dy, "nota", round(nota, 3), "(abaixo de ~0,9 a pose mudou: confira a prévia)")
    corpo_na_aura = ndi.binary_dilation(C.desloca(corpo, dx, dy), iterations=5)
    aura = fg.copy(); aura[:, :AURA_X[0]] = False; aura[:, AURA_X[1]:] = False
    aura &= ~corpo_na_aura
    if QUENTE:
        aura &= ~C.derrame_quente(im); rgb = C.tira_azul_acima_do_verde(im)
    else:
        aura &= ~C.derrame_de_borda(aura, im); rgb = im
    aura = ndi.binary_opening(aura, iterations=1)
    m = np.zeros_like(aura); m[CAIXA[1]:CAIXA[3], CAIXA[0]:CAIXA[2]] = aura[CAIXA[1]:CAIXA[3], CAIXA[0]:CAIXA[2]]
    peca, frag, gotas = C.separa_soltos(m)                       # fragmento gordo fica na peça; gota fina vira partícula
    # O que o corpo escondia (a raiz da peça) é REMENDO e fica atrás do corpo: feche aqui com C.discos +
    # C.remenda_clone / C.remenda_vizinho (veja a raiz das asas em hazak_asas.py). Traço fino que some em 1/4
    # (osso, vareta, corrente): C.reforca_linhas.
    C.salva_rgba(f"{rec}/peca.png", rgb, peca)
    json.dump(dict(dx=dx, dy=dy, peca_bbox=C.caixa(peca), fragmentos=frag, gotas_do_desenho=gotas), open(f"{rec}/info.json", "w"), indent=1)
    C.previa_recortes([f"{rec}/peca.png"], f"{pasta}/p_recortes.png", (AURA_X[0], 0, AURA_X[1], H), (H, W))      # OLHE esta prévia


def rig(pasta, so_pontos=False):
    """Roda dentro do Blender (o `rig`/`pontos` da linha de comando abre o Blender sozinho)."""
    C.bl_cena(TELA, N)
    pc = C.bl_malha_com_ossos("peca", os.path.join(pasta, "recortes", "peca.png"), OSSOS, TELA, N, tremor=TREMOR)
    C.bl_anima_juntas(pc["arm"], ANIM, N, centro=CENTRO)
    ox, oz = pc["origem"]
    C.bl_anima_objeto(pc["arm"], N, lambda t: respira(t, ox, oz))
    # mais peças: repita o bloco (peça gêmea = ossos espelhados, sinal=-1 e fase de alguns quadros);
    # peça rígida (coroa, selo): C.bl_placa + C.bl_anima_objeto. Uma passada de render por camada.
    C.bl_renderiza(pasta, N, {"peca": [pc["malha"]]}, lambda f: C.bl_pontas(pc, TELA, "peca"), so_pontos=so_pontos, blend="rig.blend")


def chicote(pasta, mostra=True):
    """Fase e passo de cada junta. Olhe: fase_q crescendo da raiz para a ponta; passo_max abaixo de ~3 px."""
    res = C.mede_pontos(json.load(open(f"{pasta}/render/pontos.json"))["pontos"], mostra=mostra)
    json.dump(res, open(f"{pasta}/chicote.json", "w"), indent=1)
    return res


def compor(pasta):
    rec = os.path.join(pasta, "recortes"); cam = os.path.join(pasta, "camadas")
    pontos = json.load(open(f"{pasta}/render/pontos.json"))["pontos"]
    rng = np.random.default_rng(7)
    pal = C.Paleta.de_recortes([f"{rec}/peca.png"], TELA, n=14, escura=ESCURA)
    if QUENTE:
        Q = pal.rampa_quente()
    else:       # aura fria: monte a rampa à mão, da base (clara) à ponta (escura), com as cores que a paleta tem
        c = pal.clara; Q = dict(claro=c, amar=c - 1, lar=c - 3, verm=c - 5, rampa=[c, c, c - 1, c - 1, c - 3, c - 3, c - 5, c - 5])
    campo = C.Campo(TELA, 96); R1, R2 = C.ladrilho(1), C.ladrilho(2, fmax=13)
    campo.fecha(N, 2, 4)                                         # o ruído tem de fechar junto com o laço

    def ruido(f):
        return 0.5 * campo.rola(R1, f, vy=2) + 0.5 * campo.rola(R2, f, vy=4, ox=17)

    # peça: render -> 1x -> paleta com histerese -> farelo fora -> contorno escuro -> fogo subindo da borda
    brutos = [C.le_render(f"{pasta}/render/peca_{f:02d}.png", TELA.amp) for f in range(N)]
    seca = [C.contorno(C.limpa(a), pal.escura) for a in pal.encaixa_seq(brutos)]
    peca = [C.linguas(a, ruido(f), Q["rampa"], alt=8, forca=0.08) for f, a in enumerate(seca)]
    # fagulhas: nascem na posição da junta no quadro em que soltam, em juntas e quadros variados
    sem = C.semeia(rng, FAGULHAS, dict(b=("int", 0, NPART), k=("int", 0, len(NASCE_EM)), dx=("uni", -0.35, 0.35), v=("uni", 0.5, 1.2),
                                       vida=("int", 22, 40)))
    for s in sem:
        s["x"], s["y0"] = pontos[s["b"] % N][NASCE_EM[s["k"]]]
    cores = (Q["claro"], Q["amar"], Q["lar"], Q["verm"])
    parts = []
    for f in range(NPART):
        L = np.full((TELA.ch, TELA.cw), -1, np.int16)
        C.emite(L, f, NPART, sem, lambda L, s, a, f, i: C.desenha_fagulha(cores, y0=s["y0"], chao_y=TELA.pe[1])(L, s, a, f, i))
        parts.append(L)
    # saída: camadas NA ORDEM DE DESENHO (a primeira mais ao fundo) + aura.json
    CAM = {"peca": peca, "particulas": parts}
    C.exporta_camadas(cam, CAM, pal)
    C.escreve_aura_json(cam, ID, AURA, TELA, TIQ, [dict(nome="peca", quadros=N, plano=PLANO),
                                                   dict(nome="particulas", quadros=NPART, plano=PLANO)], pal,
                        extras=dict(gerado_por="ferramentas/aura_blender/" + os.path.basename(__file__)))
    # medidas: nada parado, emenda do tamanho das vizinhas, sem quadro repetido
    med = dict(C.mede_conjunto(CAM, pal, NPART), peca=C.mede_camada(peca, pal), peca_sem_fogo=C.mede_camada(seca, pal),
               particulas=C.mede_camada(parts, pal), chicote=chicote(pasta, mostra=False))
    json.dump(med, open(f"{pasta}/medidas.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in med.items() if k != "chicote"}))
    # tiras e vídeo, com o corpo por cima (ou por baixo, se PLANO == "frente"): é isto que se olha antes de dizer que ficou bom
    info = json.load(open(f"{rec}/info.json"))
    c_rgb, c_m = C.reduz(C.conceito_para_4x(f"{rec}/corpo.png", TELA, dx=info["dx"]), TELA.amp)
    corpo = np.dstack([np.clip(c_rgb, 0, 255).astype(np.uint8), (c_m * 255).astype(np.uint8)]); corpo[~c_m] = 0
    fundo = C.fundo_teste(TELA)
    atras, frente = (CAM.values(), []) if PLANO == "atras" else ([], CAM.values())
    Q_ = [C.compoe(fundo, f, atras, corpo, frente, pal) for f in range(NPART)]
    C.tira([Q_[f] for f in range(0, N, 3)], f"{pasta}/tira.png", rotulos=[f"q{f:02d}" for f in range(0, N, 3)])
    C.tira([Q_[f] for f in range(8)], f"{pasta}/tira_consecutivos.png", rotulos=[f"q{f:02d}" for f in range(8)])
    C.tira([C.compoe(fundo, f, CAM.values(), None, [], pal) for f in (0, N // 2)], f"{pasta}/tira_sem_corpo.png", cols=2, esc=3)
    C.video_laco(f"{pasta}/aura.mp4", Q_, TIQ)


def instala(pasta):
    C.instala(os.path.join(pasta, "camadas"), os.path.join(C.RAIZ, "sprites", ID, "aura"))


if __name__ == "__main__":
    import tempfile
    C.roda(__file__, {"recortes": recortes, "rig": rig, "chicote": chicote, "compor": compor, "instala": instala},
           os.path.join(tempfile.gettempdir(), "aura_blender", ID))
