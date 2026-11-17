"""Aura do Hazak despertado (Diabo Loiro): asas de ouro e notas queimando, coroa, brasa no chão, notas e gotas.

Primeira aura feita pelo método do Blender; é a referência de nível. Tudo que é genérico está em comum.py;
aqui fica só o que é desta aura: onde cortar o conceito, os ossos, a batida, e as camadas procedurais.

    python ferramentas/aura_blender/hazak_asas.py <pasta de trabalho>            # tudo, na ordem
    python ferramentas/aura_blender/hazak_asas.py <pasta de trabalho> pontos chicote   # só o movimento (1 s), para afinar
    etapas: recortes, rig (Blender), chicote (mede as pontas), compor, instala (copia para sprites/hazaki/aura/)
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import comum as C

ID = "hazaki"
SRC = os.path.join(C.RAIZ, "sprites", ID, "quadros", "folhas_arcade", "d_conceito.png")
DESTINO = os.path.join(C.RAIZ, "sprites", ID, "aura")
# conceito: vista 1 (só o corpo) nas colunas 28..353; vista 3 (corpo + aura) nas colunas 725..1895
TELA = C.Tela(cx=1313.0, chao=697.0, escala=112 / 441.0)     # eixo do corpo e chão na vista 3; corpo de 441 px vira 112
CXM = 1313                                                    # eixo de espelho das asas
N = 48                                                        # quadros da batida
TIQ = 2                                                       # tiques do jogo por quadro
NPART = 2 * N                                                 # laço das partículas e do chão: 2 batidas

# ---------------------------------------------------------------------------------------------------------------- ossos
# asa ESQUERDA em px do conceito: nome, pai, cabeça, cauda (a direita é o espelho em x = CXM)
OSSOS = [
    ("braco", None, (1278, 330), (1193, 287)),
    ("antebraco", "braco", (1193, 287), (1143, 155)),
    ("garra", "antebraco", (1143, 155), (1197, 178)),
    ("d1a", "antebraco", (1143, 155), (1083, 100)), ("d1b", "d1a", (1083, 100), (1000, 72)), ("d1c", "d1b", (1000, 72), (880, 55)),
    ("d2a", "antebraco", (1143, 155), (1050, 158)), ("d2b", "d2a", (1050, 158), (930, 170)), ("d2c", "d2b", (930, 170), (780, 190)),
    ("d3a", "antebraco", (1143, 155), (1060, 220)), ("d3b", "d3a", (1060, 220), (985, 300)), ("d3c", "d3b", (985, 300), (860, 420)),
    ("d4a", "antebraco", (1143, 155), (1117, 250)), ("d4b", "d4a", (1117, 250), (1108, 350)), ("d4c", "d4b", (1108, 350), (1050, 480)),
    ("d5a", "braco", (1193, 287), (1200, 370)), ("d5b", "d5a", (1200, 370), (1175, 450)),
]
# animação por junta: (amplitude em graus, atraso em fração do ciclo, ondulação 2x em graus, fase da ondulação)
# A raiz gira pouco e cedo; cada junta adiante gira MAIS e mais TARDE: é isso que faz o chicote na posição da ponta.
ANIM = {"braco": (4.0, 0.00, 0, 0), "antebraco": (3.2, 0.08, 0, 0), "garra": (-3.0, 0.14, 0, 0),
        "d1a": (3.2, 0.17, 0.0, 0), "d1b": (4.6, 0.27, 0.9, 0.0), "d1c": (7.5, 0.38, 2.0, 0.0),
        "d2a": (3.0, 0.17, 0.0, 0), "d2b": (5.0, 0.27, 0.9, 0.9), "d2c": (8.0, 0.38, 2.0, 0.9),
        "d3a": (1.6, 0.18, 0.0, 0), "d3b": (5.0, 0.28, 1.0, 1.8), "d3c": (8.0, 0.40, 2.2, 1.8),
        "d4a": (-1.5, 0.18, 0.6, 2.7), "d4b": (5.0, 0.29, 1.2, 2.7), "d4c": (8.0, 0.41, 2.4, 2.7),
        "d5a": (-4.0, 0.12, 1.0, 3.6), "d5b": (8.0, 0.26, 2.2, 3.6)}
CENTRO = -0.25      # a batida fica um pouco abaixo da pose do desenho (não cresce para cima da tela)
# (nome, lado, fase em quadros, profundidade): a asa de trás bate 4 quadros depois
ASAS = (("esq", -1, 0.0, 0.0), ("dir", +1, 4.0, 3.0))

# ossos de ouro da asa esquerda lidos do desenho (x, y, largura em px do conceito), reforçados por cima do recorte
OSSOS_DESENHO = [
    [(1146, 168, 17), (1170, 227, 17), (1193, 287, 18), (1240, 310, 17), (1262, 320, 16), (1300, 338, 15), (1330, 350, 14)],  # punho-cotovelo-ombro
    [(1143, 153, 13), (1113, 127, 12), (1083, 100, 12), (1063, 88, 11), (1023, 77, 10), (983, 68, 8), (955, 61, 6)],          # dedo 1 (borda de cima)
    [(1140, 156, 12), (1100, 155, 12), (1050, 158, 11), (1007, 160, 10), (960, 171, 8), (925, 178, 6)],                        # dedo 2
    [(1137, 166, 12), (1100, 187, 12), (1067, 213, 11), (1040, 240, 10), (1007, 273, 9), (983, 303, 7), (965, 328, 6)],        # dedo 3
    [(1140, 172, 12), (1127, 197, 12), (1117, 240, 11), (1112, 287, 10), (1113, 322, 8), (1110, 345, 6)],                      # dedo 4
    [(1150, 151, 15), (1173, 147, 14), (1190, 157, 11), (1197, 172, 7), (1199, 186, 4)],                                       # garra
]
# camadas do osso: (cor, quanto a largura encolhe, desvio para cima em fração da largura)
OURO = [((70, 20, 6), 0, 0.0), ((214, 100, 8), -4, 0.0), ((250, 176, 24), -7, -0.10), ((254, 226, 110), -11, -0.22)]
NO_PUNHO = [((70, 20, 6), 13, 0), ((214, 100, 8), 11, 0), ((250, 176, 24), 9, -1), ((254, 226, 110), 5, -3)]


def espelha(x, lado):
    return x if lado < 0 else 2 * CXM - x


# ============================================================================================================ 1. recortes
def recortes(pasta):
    from scipy import ndimage as ndi
    from PIL import Image
    rec = os.path.join(pasta, "recortes"); os.makedirs(rec, exist_ok=True)
    im = C.le_rgb(SRC); H, W = im.shape[:2]
    fg = C.chave_magenta(im)
    # corpo na vista 1 e onde ele reaparece na vista 3 (para tirar o corpo de dentro da aura)
    corpo = C.recorta_corpo(fg, im, 28, 353)
    bb = C.caixa(corpo); print("corpo bbox", bb)
    Image.fromarray(np.dstack([im, (corpo * 255).astype(np.uint8)])[:, :400]).save(f"{rec}/corpo_v1.png")
    DX, DY, nota = C.casa_corpo(im, corpo, 1100, 1530)
    print("corpo casado na vista 3: dx", DX, "dy", DY, "nota", round(nota, 4))
    assert DY == 0 and nota > 0.9, "o corpo da vista 1 não casou com o da vista 3"
    corpo3d = ndi.binary_dilation(C.desloca(corpo, DX), iterations=5)
    # aura na vista 3: é dourada, então todo pixel com azul acima do verde é derrame de magenta
    aura = fg.copy(); aura[:, :725] = False; aura[:, 1895:] = False
    aura &= ~corpo3d
    aura[540:, 1830:] = False; aura[600:, 1816:] = False        # canto da folha (legenda)
    aura &= ~C.derrame_quente(im)
    aura = ndi.binary_opening(aura, iterations=1)
    rgbA = C.tira_azul_acima_do_verde(im)

    coroa = aura.copy(); coroa[:, :1235] = False; coroa[:, 1395:] = False; coroa[250:] = False
    coroa_m = C.maior_componente(coroa)
    chao = aura.copy(); chao[:625] = False
    resto = aura & ~coroa; resto[625:] = False
    info = {}
    for nome, sl, lado in (("asa_esq", slice(0, CXM), -1), ("asa_dir", slice(CXM, W), 1)):
        m = np.zeros_like(resto); m[:, sl] = resto[:, sl]
        # pedaço solto grande é nota queimando: fica na asa e mexe com a ponta do dedo; gota fina vira partícula
        asa, frag, gotas = C.separa_soltos(m)
        info[nome + "_fragmentos"] = frag; info[nome + "_gotas_do_desenho"] = gotas
        # raiz escondida: toco arredondado ao longo do osso do braço, só atrás do corpo, passando do meio
        # (as duas asas se cruzam atrás do corpo; é remendo e fica atrás dele)
        toco = C.discos((H, W), [(espelha(1215, lado), 335, 95), (espelha(1275, lado), 348, 70), (espelha(1335, lado), 358, 44)])
        faixa = toco & ndi.binary_dilation(corpo3d, iterations=2) & ~asa
        full = rgbA.copy()
        falta = C.remenda_clone(full, rgbA, asa, faixa, (14, lado * 96))      # clona as penas abaixo do braço (sem osso)
        C.remenda_vizinho(full, (asa | faixa) & ~falta, falta)
        tot = asa | faixa
        tot2 = ndi.binary_closing(tot, iterations=3) & (tot | corpo3d)
        C.remenda_vizinho(full, tot, tot2 & ~tot); tot = tot2
        # ossos de ouro reforçados: osso de 12 px do conceito some na redução para 1/4
        linhas = [[(espelha(x, lado), y, w) for x, y, w in ln] for ln in OSSOS_DESENHO]
        osso_m = C.reforca_linhas(full, tot, linhas, OURO, nos=[(espelha(1143, lado), 157, NO_PUNHO)])
        C.salva_rgba(f"{rec}/{nome}.png", full, tot)
        info[nome] = dict(bbox=C.caixa(tot), raiz_px=int(faixa.sum()), osso_px=int(osso_m.sum()))
    C.salva_rgba(f"{rec}/coroa.png", rgbA, coroa_m)
    # chão: fecha o buraco dos pés espelhando para dentro a própria faixa de cada lado (não por borrão)
    buraco = [x for x in range(CXM - 130, CXM + 130) if chao[625:, x].sum() < 5]
    bx0, bx1 = min(buraco) - 6, max(buraco) + 7; print("buraco do chao", bx0, bx1)
    full = rgbA.copy(); chm = chao.copy()
    C.espelha_faixa(full, rgbA, chm, bx0, bx1, 625)
    C.salva_rgba(f"{rec}/chao.png", full, chm)
    info["corpo_bbox"] = bb; info["DX"] = DX
    info["coroa_bbox"] = C.caixa(coroa_m); info["chao_bbox"] = C.caixa(chm)
    json.dump(info, open(f"{rec}/info.json", "w"), indent=1)
    print({k: (v if not isinstance(v, list) else len(v)) for k, v in info.items()})
    C.previa_recortes([f"{rec}/{n}.png" for n in ("asa_esq", "asa_dir", "coroa", "chao")], f"{pasta}/p_recortes.png",
                      (720, 20, 1900, 710), (H, W))


# ================================================================================================================= 2. rig
def rig(pasta, so_pontos=False):
    """Roda DENTRO do Blender."""
    C.bl_cena(TELA, N)
    rec = os.path.join(pasta, "recortes")
    pecas = {}
    for nome, lado, fase, prof in ASAS:
        ossos = [(n, p, (espelha(h[0], lado), h[1]), (espelha(t[0], lado), t[1])) for n, p, h, t in OSSOS]
        px, pz = TELA.g(*ossos[1][3])                                     # punho
        pc = C.bl_malha_com_ossos(nome, os.path.join(rec, f"asa_{nome}.png"), ossos, TELA, N,
                                  prof=lambda X, Z: 0.004 * math.hypot(X - px, Z - pz),   # longe do punho = mais ao fundo
                                  tremor=[dict(eixo="X", raio=9.0, fase=0.0 + fase, forca=5.0),
                                          dict(eixo="Z", raio=11.0, fase=2.1 + fase, forca=6.5)])
        sn = 1 if lado < 0 else -1
        C.bl_anima_juntas(pc["arm"], ANIM, N, fase=fase, centro=CENTRO, sinal=sn)
        ox, oz = pc["origem"]
        # respiração: a asa encurta quando desce (profundidade fingida); o ombro sobe quando a asa empurra para baixo
        C.bl_anima_objeto(pc["arm"], N, lambda t: dict(
            scale=(1 - 0.055 * (0.5 - 0.5 * math.sin(t - 0.2)), 1, 1),
            location=(ox + 1.2 * sn * math.sin(t + 0.9), prof, oz - 3.0 * math.sin(t + 0.5) + 0.6 * math.sin(2 * t))), fase=fase)
        pecas[nome] = pc
    info = json.load(open(os.path.join(rec, "info.json")))
    oc, (cxm, czm) = C.bl_placa("coroa", os.path.join(rec, "coroa.png"), info["coroa_bbox"], TELA)
    # coroa: flutua, balança e gira como se pairasse (o giro em Z encurta a largura)
    C.bl_anima_objeto(oc, N, lambda t: dict(
        location=(cxm + 2.2 * math.sin(t + 1.0), -3, czm + 1.5 + 4.0 * math.sin(t - 0.8) + 1.0 * math.sin(2 * t + 0.3)),
        rotation_euler=(0, math.radians(9.0 * math.sin(t + 0.4)), math.radians(32.0 * math.sin(t + 2.0))),
        scale=(1, 1, 1 + 0.07 * math.sin(2 * t + 1.0))))

    def coleta(f):
        d = {}
        for nome, pc in pecas.items():
            d.update(C.bl_pontas(pc, TELA, nome))
        w = oc.matrix_world.translation
        d["coroa"] = list(TELA.jogo(w.x, w.z)) + [oc.rotation_euler.y, math.cos(oc.rotation_euler.z)]
        return d
    C.bl_renderiza(pasta, N, {"asas": [pecas["esq"]["malha"], pecas["dir"]["malha"]], "coroa": [oc]}, coleta,
                   so_pontos=so_pontos, extra=dict(coroa_centro=list(TELA.jogo(cxm, czm))), blend="rig.blend")


CHICOTE = ["esq_raiz", "esq_braco", "esq_antebraco", "esq_garra", "esq_d5a", "esq_d5b", "esq_d4a", "esq_d4b", "esq_d4c", "esq_d3a", "esq_d3b",
           "esq_d3c", "esq_d2a", "esq_d2b", "esq_d2c", "esq_d1a", "esq_d1b", "esq_d1c", "coroa"]


def chicote(pasta, mostra=True):
    PT = json.load(open(f"{pasta}/render/pontos.json"))
    res = C.mede_pontos(PT["pontos"], CHICOTE, mostra)
    json.dump(res, open(f"{pasta}/chicote.json", "w"), indent=1)
    return res


# ============================================================================================================== 3. compor
PONTAS = ["esq_d1c", "dir_d2c", "esq_d3c", "dir_d1c", "esq_d2c", "dir_d4c", "esq_d4c", "dir_d3c"]      # onde as notas se soltam
NN = 12; VIDA = 70                                                                                    # notas no ar e quanto duram
# gotas de ouro: (âncora, nascimento, período). Âncora = ponta de osso ou ponto da coroa ("coroa:dx:dy")
GOTAS = [("esq_garra", 0, N), ("dir_garra", 29, N), ("esq_d4c", 14, NPART), ("dir_d4c", 61, NPART), ("esq_d3c", 40, NPART), ("dir_d3c", 5, NPART),
         ("esq_d5b", 70, NPART), ("dir_d5b", 22, NPART), ("esq_d2c", 52, NPART), ("dir_d2c", 84, NPART), ("esq_d4b", 33, NPART), ("dir_d4b", 77, NPART),
         ("esq_d3b", 88, NPART), ("dir_d3b", 46, NPART),
         ("coroa:-9:9", 6, N), ("coroa:1:11", 21, N), ("coroa:8:9", 37, N), ("coroa:-4:10", 60, NPART), ("coroa:5:10", 90, NPART)]


def compor(pasta):
    from scipy import ndimage as ndi
    from PIL import Image
    rec = os.path.join(pasta, "recortes"); cam = os.path.join(pasta, "camadas")
    CW, CH, AMP = TELA.cw, TELA.ch, TELA.amp
    info = json.load(open(f"{rec}/info.json"))
    PT = json.load(open(f"{pasta}/render/pontos.json")); pontos = PT["pontos"]
    assert len(pontos) == N
    rng = np.random.default_rng(7)

    # ---------- paleta fixa: 14 cores do próprio desenho (asas + coroa + brasa) + 1 escura de contorno
    pal = C.Paleta.de_recortes([f"{rec}/{n}.png" for n in ("asa_esq", "asa_dir", "coroa", "chao")], TELA, n=14, escura=(52, 14, 10))
    print("PALETA", pal.lista())
    Q = pal.rampa_quente(); F_CLARO, F_AMAR, F_LAR, F_VERM, F_ESC, RAMPA = Q["claro"], Q["amar"], Q["lar"], Q["verm"], Q["esc"], Q["rampa"]
    FOGO = (F_CLARO, F_AMAR, F_LAR, F_VERM)
    print("FOGO", [pal.cores[i].tolist() for i in (F_CLARO, F_AMAR, F_LAR, F_VERM, F_ESC)])

    # ---------- ruído que emenda: sobe 2 e 4 px por quadro, fecha em N = 48 (lado 96)
    campo = C.Campo(TELA, 96); T = campo.T
    R1, R2, R3 = C.ladrilho(1), C.ladrilho(2, fmax=13), C.ladrilho(3, fmax=6)
    campo.fecha(N, 2, 4); campo.fecha(NPART, 3, 2, 1)

    def ruido(f):
        return 0.5 * campo.rola(R1, f, vy=2) + 0.5 * campo.rola(R2, f, vy=4, ox=17)

    # ---------- camadas que vêm do Blender: asas e coroa
    brutos = {nome: [C.le_render(f"{pasta}/render/{nome}_{f:02d}.png", AMP) for f in range(N)] for nome in ("asas", "coroa")}
    asas_sem_fogo = [C.contorno(C.limpa(a), F_ESC) for a in pal.encaixa_seq(brutos["asas"])]
    asas = [C.linguas(a, ruido(f), RAMPA, alt=8, forca=0.08) for f, a in enumerate(asas_sem_fogo)]
    coroas = []
    for f, c in enumerate(pal.encaixa_seq(brutos["coroa"])):       # coroa: ouro derretido cintila e solta fogo
        c = C.contorno(c, F_ESC); n = ruido(f)
        C.cintila(c, n, 0.66, 0.30, sobe=2, desce=1, mask=c > F_ESC)
        coroas.append(C.linguas(c, n, RAMPA, alt=5, forca=0.10))

    # ---------- chão: brasa que ondula, cintila, solta línguas e fagulhas (laço de NPART quadros)
    ch_idx = pal.encaixa(*C.reduz(C.conceito_para_4x(f"{rec}/chao.png", TELA), AMP))
    fag = C.semeia(rng, 46, dict(x=("int", 36, 324), b=("int", 0, NPART), dx=("uni", -0.35, 0.35), v=("uni", 0.8, 1.7), vida=("int", 22, 40)))
    fagulha = C.desenha_fagulha(FOGO)
    chaos = []; xs_ = np.arange(CW)
    for f in range(NPART):
        w = 2 * math.pi * f / NPART
        # a faixa inteira ondula: cada coluna sobe/desce até 2 px numa onda que corre para os lados (a base no chão fica)
        dy = np.round(1.3 * np.sin(2 * w + xs_ / 9.0) + 1.0 * np.sin(3 * w - xs_ / 5.5 + 1.0)).astype(int)
        c = C.ondula_colunas(ch_idx, dy, base=11, y_corte=TELA.pe[1])
        n = campo.rola(R3, f, vy=3, vx=2) * 0.6 + campo.rola(R2, f, vy=2, vx=-1) * 0.4
        C.cintila(c, n, 0.60, 0.38, sobe=2, desce=2)
        c = C.linguas(c, ruido(f), RAMPA, alt=9, forca=0.16)
        C.emite(c, f, NPART, fag, fagulha)
        chaos.append(c)

    # ---------- partículas: notas que planam e queimam + gotas de ouro (laço de NPART quadros)
    def nota_base():
        """nota de dinheiro 13x7 px (desenhada 4x): contorno queimado, papel claro, tarjas e medalhão."""
        w, h = 13, 7; a = np.full((h, w), 12, np.int16)
        a[0, :] = a[-1, :] = F_ESC; a[:, 0] = a[:, -1] = F_ESC
        a[1, 1:-1] = 13; a[-2, 1:-1] = F_AMAR
        a[1:-1, 2] = F_LAR; a[1:-1, -3] = F_LAR
        a[2:5, 5:8] = F_LAR; a[3, 6] = F_VERM; a[2, 5] = a[2, 7] = a[4, 5] = a[4, 7] = 12
        o = np.zeros((h, w, 4), np.uint8); o[..., :3] = pal.cores[a]; o[..., 3] = 255
        return np.repeat(np.repeat(o, AMP, 0), AMP, 1)

    NOTA = nota_base()
    semente = C.semeia(rng, NN, dict(ph=("uni", 0, 6.28), ph2=("uni", 0, 6.28), a0=("uni", -0.5, 0.5), vy=("uni", 0.75, 1.05), amp=("uni", 5, 9),
                                     b=lambda i, r: (i * 8 + int(r.integers(0, 5))) % NPART))

    def nota(L, sd, a, f, i):
        tip = PONTAS[i % len(PONTAS)]; x0, y0 = pontos[sd["b"] % N][tip]          # nasce onde a ponta estava ao soltar
        lado = -1 if tip.startswith("esq") else 1
        bal = 2 * math.pi * a / 32 + sd["ph"]                     # balanço de folha caindo
        x = x0 + lado * 0.22 * a + sd["amp"] * math.sin(bal) * min(1, a / 10)
        y = y0 + sd["vy"] * a + 0.006 * a * a - 1.5 * abs(math.cos(bal)) * min(1, a / 10)
        if y > 183:
            return False
        ang = sd["a0"] + 0.55 * math.cos(bal)                     # inclina para o lado em que está indo
        achat = math.cos(2 * math.pi * a / 44 + sd["ph2"]); achat = math.copysign(max(abs(achat), 0.45), achat)
        im = pal.encaixa(*C.reduz(C.carimbo_girado(NOTA, ang, achat, min(1.0, 0.55 + a * 0.09), AMP), AMP))
        fim = min(VIDA - a, (183 - y) / 1.2)                      # queima no fim da vida ou perto do chão
        m = im >= 0
        hh, ww = im.shape; nz = R2[:hh, (np.arange(ww) + 9 * i) % T]
        qm = 0.18 + 0.12 * math.sin(a * 0.2 + i)                  # canto sempre comido pelo fogo
        if fim < 14:
            qm = max(qm, (14 - fim) / 14 * 1.05)
        com = m & (nz < qm)
        im[com] = -1
        beira = (im >= 0) & ndi.binary_dilation(com)
        im[beira] = np.where(R1[:hh, (np.arange(ww) + 3 * f) % T][beira] > 0.5, F_CLARO, F_LAR)
        if fim < 7:
            im[im >= 0] = np.where(im[im >= 0] > 9, F_LAR, F_VERM)
        C.carimba(L, im, x, y)
        return (im >= 0).sum() > 3

    def ancora(nome, f):
        f %= N
        if nome.startswith("coroa"):
            _, ox, oy = nome.split(":"); cx, cy, rot, cz = pontos[f]["coroa"]
            ox, oy = float(ox) * cz, float(oy)
            return cx + ox * math.cos(rot) + oy * math.sin(rot), cy + oy * math.cos(rot) - ox * math.sin(rot)
        return pontos[f][nome]

    gotas = [dict(ancora=a, b=b, per=per) for a, b, per in GOTAS]
    gota = C.desenha_gota(ancora, FOGO, presa=18, chao_y=TELA.pe[1])
    parts = []; viv = []
    for f in range(NPART):
        L = np.full((CH, CW), -1, np.int16)
        viv.append(C.emite(L, f, NPART, semente, nota, vida=VIDA))
        L = C.linguas(L, ruido(f), RAMPA, alt=4, forca=0.10)
        C.emite(L, f, NPART, gotas, gota)
        parts.append(L)
    print("NOTAS vivas por quadro:", min(viv), "a", max(viv))

    # ---------- saída: camadas na ordem de desenho (a primeira fica mais ao fundo); o corpo vai por cima de todas
    CAM = {"chao": chaos, "asas": asas, "coroa": coroas, "particulas": parts}
    C.exporta_camadas(cam, CAM, pal)
    json.dump(pal.lista(), open(f"{cam}/paleta.json", "w"))
    C.escreve_aura_json(cam, ID, "asas", TELA, TIQ, [
        dict(nome="chao", quadros=NPART, plano="atras", o_que="brasa no chão, de ponta a ponta, com línguas e fagulhas"),
        dict(nome="asas", quadros=N, plano="atras", o_que="as duas asas batendo (a raiz atrás do corpo é remendo)"),
        dict(nome="coroa", quadros=N, plano="atras", o_que="coroa de ouro derretido pairando acima da cabeça"),
        dict(nome="particulas", quadros=NPART, plano="atras", o_que="notas queimando que planam e gotas de ouro que pingam"),
    ], pal, extras=dict(
        nota="O pé do lutador fica em `pe`; cada PNG tem o tamanho de `tela`. Cada camada roda no seu laço "
             "(quadro = (tique // tiques_por_quadro) % quadros). Todas atrás do corpo, como no vídeo aprovado.",
        gerado_por="ferramentas/aura_blender/hazak_asas.py"))

    # ---------- corpo (vista 1) no tamanho do jogo, 15 cores próprias: só para o vídeo e as tiras
    c_rgb, c_m = C.reduz(C.conceito_para_4x(f"{rec}/corpo_v1.png", TELA, dx=info["DX"]), AMP)
    cq = Image.fromarray(np.clip(c_rgb, 0, 255).astype(np.uint8)).quantize(15, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    corpo = np.dstack([np.array(cq), (c_m * 255).astype(np.uint8)]); corpo[~c_m] = 0
    Image.fromarray(corpo).save(f"{cam}/corpo_previa.png")
    ys, xs = np.where(c_m); print("CORPO no jogo: altura", ys.max() - ys.min() + 1, "largura", xs.max() - xs.min() + 1)
    fundo = C.fundo_teste(TELA)
    NOVOS = [C.compoe(fundo, f, CAM.values(), corpo, [], pal) for f in range(NPART)]

    # ---------- medidas
    med = {"quadros_asa": N, "tiques_por_quadro": TIQ, "quadros_particulas_e_chao": NPART, "duracao_batida_s": N * TIQ / 60}
    med.update(C.mede_conjunto(CAM, pal, NPART))
    for nome, lst in (("asas", asas), ("asas_sem_fogo", asas_sem_fogo), ("coroa", coroas), ("chao", chaos), ("particulas", parts)):
        med[nome] = C.mede_camada(lst, pal)
    dn = [float(np.abs(NOVOS[f].astype(int) - NOVOS[(f + 1) % NPART].astype(int)).mean()) for f in range(NPART)]
    med["composto_dif_min_max_emenda"] = [round(min(dn), 3), round(max(dn), 3), round(dn[-1], 3)]
    A0 = [a >= 0 for a in asas_sem_fogo]
    larg = [int(np.where(a.any(0))[0].max() - np.where(a.any(0))[0].min() + 1) for a in A0]
    alt = [int(np.where(a.any(1))[0].max() - np.where(a.any(1))[0].min() + 1) for a in A0]
    hc = int(ys.max() - ys.min() + 1); wc = int(xs.max() - xs.min() + 1)
    med["corpo_px"] = [wc, hc]; med["envergadura_px_min_max"] = [min(larg), max(larg)]; med["altura_asas_px_min_max"] = [min(alt), max(alt)]
    med["envergadura_sobre_altura_do_corpo"] = [round(min(larg) / hc, 2), round(max(larg) / hc, 2)]
    med["topo_das_asas_y_min"] = int(min(np.where(a.any(1))[0].min() for a in A0)); med["pe_y"] = TELA.pe[1]
    sil = np.stack(A0); med["asas_pixels_sempre_opacos_frac"] = round(float(sil.all(0).sum() / sil.any(0).sum()), 3)
    mi = []                              # metade interna: fração de pixels que mudam só na faixa junto ao corpo
    for f in range(N):
        a, b = asas_sem_fogo[f][:, 130:230], asas_sem_fogo[(f + 1) % N][:, 130:230]; u = (a >= 0) | (b >= 0)
        mi.append(float(((a != b) & u).sum() / max(u.sum(), 1)))
    med["asas_junto_ao_corpo_frac_pixels_mudam_min_max"] = [round(min(mi), 3), round(max(mi), 3)]
    med["notas_vivas_min_max"] = [min(viv), max(viv)]; med["gotas"] = len(GOTAS); med["fagulhas"] = len(fag)
    med["tempo_render_blender_s"] = round(PT["tempo_render"], 1)
    med["chicote"] = chicote(pasta, mostra=False)
    json.dump(med, open(f"{pasta}/medidas.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in med.items() if k != "chicote"}))

    # ---------- tiras (olhar com os olhos) e vídeo
    X0, LW = 20, 320
    C.tira([NOVOS[f][:, X0:X0 + LW] for f in range(0, N, 3)], f"{pasta}/tira.png", rotulos=[f"q{f:02d}" for f in range(0, N, 3)])     # a batida inteira
    C.tira([NOVOS[f][:, X0:X0 + LW] for f in range(8)], f"{pasta}/tira_consecutivos.png", rotulos=[f"q{f:02d}" for f in range(8)])   # fervura
    C.tira([NOVOS[k][15:195, 20:190] for k in range(6)], f"{pasta}/tira_zoom_esq.png", cols=6)
    C.tira([NOVOS[k][0:200, 110:250] for k in (0, 12, 24, 36)], f"{pasta}/tira_zoom_meio.png", cols=4, esc=3)
    sem = [C.compoe(fundo, f, CAM.values(), None, [], pal) for f in (0, 24)]
    C.tira([s[40:195, 90:270] for s in sem], f"{pasta}/tira_sem_corpo.png", cols=2, esc=3)        # os remendos aparecem aqui
    C.video_laco(f"{pasta}/aura.mp4", NOVOS, TIQ)
    print("OK")


def instala(pasta):
    C.instala(os.path.join(pasta, "camadas"), DESTINO)


if __name__ == "__main__":
    import tempfile
    C.roda(__file__, {"recortes": recortes, "rig": rig, "chicote": chicote, "compor": compor, "instala": instala},
           os.path.join(tempfile.gettempdir(), "aura_blender", ID))
