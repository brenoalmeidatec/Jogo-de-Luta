#!/usr/bin/env python3
"""Sistema de aura animada: a aura do Despertar de qualquer lutador, em camadas que se mexem no motor.

Um gerador (gerar_<lutador>.py) usa assim (detalhes e números de aceite em docs/arcade/aura_animada.md):

    import aura
    q = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(FOLHAS / "fx_aura.png"), altura=230), total=24)
    AURA = aura.Aura("ck", ligada="var(20) > 0", surto="StateNo = [1000, 3999] && Time = 1", base=9300, camadas=[
        aura.Camada("coluna", q, plano="tras", mov=aura.Movimento(pulso=(0.05, 0.07), deriva=(2, 4))),
        aura.Camada("pes", q, plano="frente", escala=(0.45, 0.3), inicio=9, mov=aura.Movimento(alfa=0.55)),
    ], particulas=[aura.Particula("anel", aneis, periodo=9, vida=48, area=(-40, -10, 40, -90), vel=(0, -1.2))])
    AURA.registrar(sprites)                  # põe os quadros no .sff do lutador (grupos base, base+1, ...)
    air += AURA.air()                        # [Begin Action base...]
    cns_menos_2 += AURA.cns()                # controladores para o [Statedef -2]

O que o módulo faz:
  1. recortar_folha: folha de 8 quadros em fundo verde #00FF00 (ou magenta) vira quadros RGBA de alfa limpo, sem
     franja da cor do fundo (borda corroída 1 px e repintada com a cor de dentro).
  2. alongar_loop: 8 desenhos viram 16 a 32 quadros, com entremeio próprio para efeito (fluxo óptico + mistura
     ponderada, ou dissolve por manchas para raio). Os quadros do meio são distribuídos pelo tamanho de cada
     mudança, para a velocidade aparente ficar igual o loop inteiro; a volta do último para o primeiro ganha
     entremeio também (loop sem emenda) e, se a folha não fecha, vira vai-e-vem. SÓ para fumaça, fogo, raio: nunca
     em corpo.
  3. Aura/Camada/Movimento: cada camada é um Explod preso ao lutador, que nasce quando `ligada` vira verdade, entra
     e sai com fade, e é movido a cada tick por um ModifyExplod (escala pulsando em seno, deriva, tremor, giro, alfa
     respirando), cada camada com período e fase próprios. `surto` acelera e incha tudo por alguns ticks.
  4. Particula: Explods curtos que nascem em posições variadas (derivadas do GameTime, sem Random) com velocidade,
     gravidade, e fade/escala/giro interpolados pelo próprio .air (Interpolate Blend/Scale/Angle).
  5. fumaca_procedural, anel_procedural, pedra_procedural, anel_de_fumaca: arte de teste feita por código.

Limites do motor que moldaram o desenho (IKEMEN GO v1.0.0, lutador com mugenversion 1.1 e sem ikemenversion; lido no
fonte src/bytecode.go e src/char.go da tag v1.0.0):
  - ModifyExplod só mexe em pos/vel/accel/facing se o `postype` vier junto, e o postype zera vel/accel e refaz a
    posição pelo lutador. Bom para a aura: cada ModifyExplod leva `postype = p1`, e com isso o Explod vira junto
    quando o lutador vira (o facing do Explod só é lido de novo nesse momento).
  - trans/alpha no ModifyExplod valem de 0 a 255 (o motor corta) e `alpha` sem `trans` é ignorado.
  - interpolation.alpha do Explod multiplica o alfa de partida, então não serve para sumir em mistura normal
    (o destino nunca chega a 255). O fade das partículas vai no .air, elemento por elemento.
  - O facing do Explod preso não acompanha a virada sozinho, e `anim` não troca por ModifyExplod sem ikemenversion.
"""
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

DOIS_PI = 2 * math.pi


# ------------------------------------------------------------------ recorte

def _sobra_do_fundo(rgb, fundo):
    """Quanto cada pixel puxa para a cor do fundo (0 = nada, 255 = fundo puro)."""
    r, g, b = (rgb[..., i].astype(np.int16) for i in range(3))
    if fundo == "verde":
        return g - np.maximum(r, b)
    return np.minimum(r, b) - g


def cor_do_fundo(rgb):
    """'verde' ou 'magenta', pelos cantos da folha."""
    cantos = np.concatenate([rgb[:6, :6].reshape(-1, 3), rgb[:6, -6:].reshape(-1, 3),
                             rgb[-6:, :6].reshape(-1, 3), rgb[-6:, -6:].reshape(-1, 3)]).astype(int)
    r, g, b = np.median(cantos, axis=0)
    return "verde" if g > r and g > b else "magenta"


def recortar_folha(caminho, quadros=8, fundo=None, limiar=90, farelo=6):
    """Folha de `quadros` células em fila -> lista de arrays RGBA (todas do mesmo tamanho, alfa 0 ou 255).

    Sem franja: o que puxa mais de `limiar` para o fundo sai; a borda é corroída 1 px; e a borda que sobra, se ainda
    puxar para o fundo mais que o miolo, recebe a cor do pixel de dentro mais próximo."""
    rgb = np.array(Image.open(caminho).convert("RGB"))
    fundo = fundo or cor_do_fundo(rgb)
    sobra = _sobra_do_fundo(rgb, fundo)
    dentro = (sobra < limiar).astype(np.uint8)
    dentro = cv2.morphologyEx(dentro, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    dentro = cv2.erode(dentro, np.ones((3, 3), np.uint8))
    miolo = cv2.erode(dentro, np.ones((5, 5), np.uint8))
    # a borda (2 px) que puxa para o fundo mais que o miolo copia a cor do pixel do miolo mais próximo
    if miolo.any():
        teto = max(25, int(np.percentile(sobra[miolo > 0], 90)) + 8)
        suja = (dentro > 0) & (miolo == 0) & (sobra > teto)
        _, rotulos = cv2.distanceTransformWithLabels(1 - miolo, cv2.DIST_L2, 3, labelType=cv2.DIST_LABEL_PIXEL)
        ys, xs = np.nonzero(miolo)
        tabela = np.zeros((rotulos.max() + 1, 2), np.int32)
        tabela[rotulos[ys, xs]] = np.stack([ys, xs], 1)
        de = tabela[rotulos[suja]]
        rgb[suja] = rgb[de[:, 0], de[:, 1]]
    rgba = np.dstack([rgb, dentro * 255]).astype(np.uint8)
    passo = rgba.shape[1] / quadros
    celulas = [rgba[:, round(i * passo) + 2:round((i + 1) * passo) - 2].copy() for i in range(quadros)]
    menor = min(c.shape[1] for c in celulas)
    celulas = [c[:, :menor] for c in celulas]
    for c in celulas:
        n, rot, info, _ = cv2.connectedComponentsWithStats((c[..., 3] > 0).astype(np.uint8), 8)
        for k in range(1, n):
            if info[k, 4] < farelo:
                c[rot == k, 3] = 0
        c[c[..., 3] == 0] = 0
    return celulas


def enquadrar(celulas, altura=None, largura=None, ancora="base", margem=2):
    """Corta todas as células na mesma caixa (a união do desenho) e põe na escala do jogo.

    ancora "base": o eixo fica no meio da borda de baixo (aura que sai dos pés); "centro": no centro da caixa.
    Passe `altura` OU `largura` em px do jogo. Devolve arrays RGBA do mesmo tamanho, alfa 0/255."""
    juntos = np.max([c[..., 3] for c in celulas], axis=0)
    ys, xs = np.nonzero(juntos)
    cx = celulas[0].shape[1] // 2
    meia = max(cx - xs.min(), xs.max() - cx) + margem
    if ancora == "base":
        y0, y1 = ys.min() - margem, ys.max() + 1
    else:
        cy = (ys.min() + ys.max()) // 2
        meia_y = max(cy - ys.min(), ys.max() - cy) + margem
        y0, y1 = cy - meia_y, cy + meia_y
    caixa = (max(0, cx - meia), max(0, y0), min(juntos.shape[1], cx + meia), min(juntos.shape[0], y1))
    fator = (altura / (caixa[3] - caixa[1])) if altura else (largura / (caixa[2] - caixa[0]))
    tam = (max(1, round((caixa[2] - caixa[0]) * fator)), max(1, round((caixa[3] - caixa[1]) * fator)))
    saida = []
    for c in celulas:
        rec = c[caixa[1]:caixa[3], caixa[0]:caixa[2]].astype(np.float32)
        rec[..., :3] *= rec[..., 3:] / 255  # pré-multiplica: o transparente não escurece a borda
        red = cv2.resize(rec, tam, interpolation=cv2.INTER_AREA if fator < 1 else cv2.INTER_NEAREST)
        a = red[..., 3:]
        cor = np.where(a > 1, red[..., :3] * 255 / np.maximum(a, 1), 0)
        q = np.dstack([np.clip(cor, 0, 255), np.where(a[..., 0] >= 128, 255, 0)]).astype(np.uint8)
        q[q[..., 3] == 0] = 0
        saida.append(q)
    return saida


def franja(quadro, fundo="verde"):
    """Fração dos pixels opacos que ainda são da cor do fundo (aceite: 0)."""
    q = np.asarray(quadro)
    r, g, b = (q[..., i].astype(int) for i in range(3))
    if fundo == "verde":
        ruim = (g > 180) & (r < 100) & (b < 100)
    else:
        ruim = (r > 180) & (b > 180) & (g < 100)
    opaco = q[..., 3] > 0 if q.shape[-1] == 4 else np.ones(q.shape[:2], bool)
    return float((ruim & opaco).sum()) / max(1, int(opaco.sum()))


# ------------------------------------------------------------------ entremeio de efeito

def _pre(q):
    p = q.astype(np.float32)
    p[..., :3] *= p[..., 3:] / 255
    return p


def diferenca(a, b):
    """Quanto muda de a para b: soma do |a - b| pré-multiplicado, sobre a área que algum dos dois ocupa (0 a 1)."""
    area = max(1, int(((a[..., 3] > 0) | (b[..., 3] > 0)).sum()))
    return float(np.abs(_pre(a) - _pre(b)).sum()) / (255 * 4 * area)


def _cinza(q):
    return (cv2.cvtColor(np.ascontiguousarray(q[..., :3]), cv2.COLOR_RGB2GRAY) // 2 + q[..., 3] // 2).astype(np.uint8)


def _fluxos(a, b):
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    return dis.calc(_cinza(a), _cinza(b), None), dis.calc(_cinza(b), _cinza(a), None)


def _manchas(forma, semente, grao=9):
    """Ruído de manchas grandes, 0 a 1 (para o dissolve: não é pontilhado, cada mancha troca de uma vez)."""
    rng = np.random.default_rng(semente)
    h, w = forma
    m = rng.random((h // grao + 2, w // grao + 2)).astype(np.float32)
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_CUBIC)
    m = (m - m.min()) / max(1e-6, m.max() - m.min())
    return m


def entre(a, b, t, metodo="fluxo", fluxos=None, semente=0):
    """Quadro do meio entre a e b no instante t (0 a 1). Só para efeito (fumaça, fogo, raio), nunca para corpo.

    "fluxo": deforma os dois pelo fluxo óptico e mistura com peso (1 - t, t).
    "mistura": mistura com peso, sem deformar. "dissolve": cada mancha troca de a para b num instante diferente."""
    t = float(t)
    if metodo == "dissolve":
        m = _manchas(a.shape[:2], semente)
        q = np.where((m < t)[..., None], b, a)
        return q.copy()
    pa, pb = _pre(a), _pre(b)
    if metodo == "fluxo":
        fab, fba = fluxos or _fluxos(a, b)
        h, w = a.shape[:2]
        gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
        pa = cv2.remap(pa, (gx + t * fba[..., 0]).astype(np.float32), (gy + t * fba[..., 1]).astype(np.float32),
                       cv2.INTER_LINEAR, borderValue=0)
        pb = cv2.remap(pb, (gx + (1 - t) * fab[..., 0]).astype(np.float32),
                       (gy + (1 - t) * fab[..., 1]).astype(np.float32), cv2.INTER_LINEAR, borderValue=0)
    m = (1 - t) * pa + t * pb
    alfa = m[..., 3]
    cor = np.where(alfa[..., None] > 1, m[..., :3] * 255 / np.maximum(alfa[..., None], 1), 0)
    q = np.dstack([np.clip(cor, 0, 255), np.where(alfa >= 128, 255, 0)]).astype(np.uint8)
    q[q[..., 3] == 0] = 0
    return q


def _paleta_dos_desenhos(desenhos, cores):
    pix = np.concatenate([d[d[..., 3] > 0][:, :3] for d in desenhos])
    if len(pix) == 0:
        return None
    passo = max(1, len(pix) // 200000)
    return Image.fromarray(np.ascontiguousarray(pix[::passo])[None], "RGB").quantize(colors=cores, method=Image.MEDIANCUT)


def _na_paleta(q, pal):
    """Leva as cores do quadro do meio para as cores dos desenhos (sem degradê novo, sem pontilhado)."""
    if pal is None:
        return q
    ind = Image.fromarray(q[..., :3], "RGB").quantize(palette=pal, dither=Image.NONE).convert("RGB")
    s = np.dstack([np.asarray(ind), q[..., 3]]).astype(np.uint8)
    s[s[..., 3] == 0] = 0
    return s


def alongar_loop(desenhos, total=24, loop=True, metodo="fluxo", cores=32, vaivem=None, limite_emenda=2.2):
    """8 desenhos -> `total` quadros (16 a 32), com os quadros do meio repartidos pelo tamanho de cada mudança.

    loop=True fecha do último para o primeiro. Se essa volta for mais de `limite_emenda` vezes a mudança mediana
    (a folha não foi desenhada para fechar), a sequência vira vai-e-vem (vaivem=True força, False proíbe).
    cores: os quadros do meio são levados para a paleta dos desenhos (0 desliga). Devolve a lista de quadros."""
    chaves = [np.asarray(d) for d in desenhos]
    if loop:
        d = [diferenca(a, b) for a, b in zip(chaves, chaves[1:])]
        emenda = diferenca(chaves[-1], chaves[0])
        if vaivem is None:
            vaivem = emenda > limite_emenda * float(np.median(d))
        if vaivem:
            chaves = chaves + chaves[-2:0:-1]
    pares = list(zip(chaves, chaves[1:] + ([chaves[0]] if loop else [])))
    if not loop:
        total -= 1  # o último desenho entra no fim
    total = max(total, len(pares))
    d = np.array([max(1e-4, diferenca(a, b)) for a, b in pares])
    ideal = d / d.sum() * total
    n = np.maximum(1, np.floor(ideal)).astype(int)
    while n.sum() < total:
        n[np.argmax(ideal - n)] += 1
    while n.sum() > total:
        n[np.argmax(np.where(n > 1, n - ideal, -1e9))] -= 1
    pal = _paleta_dos_desenhos(chaves, cores) if cores else None
    saida = []
    for i, (a, b) in enumerate(pares):
        saida.append(a)
        fl = _fluxos(a, b) if metodo == "fluxo" and n[i] > 1 else None
        for k in range(1, n[i]):
            saida.append(_na_paleta(entre(a, b, k / n[i], metodo, fl, semente=i), pal))
    if not loop:
        saida.append(chaves[-1])
    return saida


def medir_loop(quadros, loop=True):
    """Fluidez dos quadros: mudança entre vizinhos. Aceite do loop: maior/mediana <= 2.5 e emenda/mediana <= 2.5."""
    q = [np.asarray(x) for x in quadros]
    pares = list(zip(q, q[1:] + ([q[0]] if loop else [])))
    d = np.array([diferenca(a, b) for a, b in pares])
    med = float(np.median(d))
    return {"quadros": len(q), "mediana": round(med, 4), "maior": round(float(d.max()), 4),
            "menor": round(float(d.min()), 4), "maior_sobre_mediana": round(float(d.max()) / max(med, 1e-6), 2),
            "emenda_sobre_mediana": round(float(d[-1]) / max(med, 1e-6), 2) if loop else None,
            "repetidos": int((d < 1e-4).sum())}


# ------------------------------------------------------------------ arte por código (para teste)

def _tons(dens, limites, cores, contorno):
    """Campo de densidade -> RGBA em planos chapados (um tom por faixa) com contorno de 1 px."""
    h, w = dens.shape
    q = np.zeros((h, w, 4), np.uint8)
    for lim, cor in zip(limites, cores):
        m = dens >= lim
        q[m, :3] = cor
        q[m, 3] = 255
    cheio = (q[..., 3] > 0).astype(np.uint8)
    borda = cheio - cv2.erode(cheio, np.ones((3, 3), np.uint8))
    q[borda > 0, :3] = contorno
    return q


def fumaca_procedural(largura=150, altura=230, quadros=24, cores=((52, 24, 84), (88, 44, 138), (140, 84, 196)),
                      contorno=(18, 8, 30), semente=7, base=0.36, topo=0.16):
    """Coluna de fumaça que sobe dos pés, em loop exato (cada onda dá voltas inteiras no loop). Eixo no meio da base."""
    rng = np.random.default_rng(semente)
    ys, xs = np.mgrid[0:altura, 0:largura].astype(np.float32)
    u = xs / largura - 0.5
    v = 1 - ys / altura
    ondas = [(rng.uniform(0.6, 1.4) / (1 + 0.35 * i), rng.integers(1, 5) * rng.choice([-1, 1]) * (1 + i // 3),
              int(rng.integers(1, 4 + i // 2)), int(rng.integers(1, 3)), rng.uniform(0, DOIS_PI)) for i in range(9)]
    soma = sum(o[0] for o in ondas)
    saida = []
    for k in range(quadros):
        t = k / quadros
        ruido = sum(a * np.cos(DOIS_PI * (fx * u + fy * v - m * t) + f) for a, fx, fy, m, f in ondas) / soma
        centro = 0.07 * v * np.sin(DOIS_PI * (1.3 * v - t)) + 0.035 * np.sin(DOIS_PI * (2.6 * v - 2 * t) + 1.1)
        meia = base * (1 - v) ** 0.8 + topo * v * (1 - v) * 4 * 0.5 + 0.03
        dens = 1 - np.abs(u - centro) / meia + 0.55 * ruido - np.clip((v - 0.72) / 0.28, 0, 1) * 0.9
        dens -= np.clip((np.abs(u) - 0.4) / 0.08, 0, 1) * 2.5  # não encosta nas bordas do quadro
        dens = cv2.GaussianBlur(dens, (0, 0), 1.2)
        saida.append(_tons(dens, (0.0, 0.42, 0.85), cores, contorno))
    return saida


def anel_procedural(largura=170, altura=44, quadros=24, tracos=10, cores=((36, 14, 60), (96, 48, 150)),
                    contorno=(14, 6, 24), espessura=0.2):
    """Anel no chão visto de lado (elipse), com traços que giram: um traço de avanço por loop, sem emenda."""
    ys, xs = np.mgrid[0:altura, 0:largura].astype(np.float32)
    x = (xs - largura / 2 + 0.5) / (largura / 2 - 2)
    y = (ys - altura / 2 + 0.5) / (altura / 2 - 2)
    r = np.sqrt(x * x + y * y)
    ang = np.arctan2(y, x)
    grosso = espessura * (1 + 0.35 * y)  # mais grosso na frente
    saida = []
    for k in range(quadros):
        t = k / quadros
        traco = np.cos(tracos * ang - DOIS_PI * t)
        dens = 1 - np.abs(r - (1 - espessura)) / grosso + 0.35 * traco - 0.25
        saida.append(_tons(dens, (0.0, 0.5), cores, contorno))
    return saida


def pedra_procedural(tamanho=9, cores=((60, 44, 78), (112, 92, 134)), contorno=(20, 12, 30), semente=3):
    """Uma pedrinha facetada (um quadro)."""
    rng = np.random.default_rng(semente)
    img = Image.new("RGBA", (tamanho + 2, tamanho + 2))
    d = ImageDraw.Draw(img)
    c = (tamanho + 1) / 2
    pts = [(c + math.cos(a) * rr, c + math.sin(a) * rr)
           for a, rr in ((DOIS_PI * i / 7, tamanho / 2 * rng.uniform(0.65, 1.0)) for i in range(7))]
    d.polygon(pts, fill=cores[0] + (255,), outline=contorno + (255,))
    d.polygon([pts[0], pts[1], pts[2], (c, c)], fill=cores[1] + (255,))
    d.line(pts + [pts[0]], fill=contorno + (255,))
    return [np.array(img)]


def anel_de_fumaca(tamanho=22, quadros=6, cores=((150, 160, 150), (206, 214, 204)), contorno=(70, 80, 70)):
    """Anel de fumaça que abre e afina (quadros de uma partícula)."""
    saida = []
    for k in range(quadros):
        s = tamanho + 2
        ys, xs = np.mgrid[0:s, 0:s].astype(np.float32)
        x = (xs - s / 2 + 0.5) / (tamanho / 2)
        y = (ys - s / 2 + 0.5) / (tamanho / 2 * 0.55)
        r = np.sqrt(x * x + y * y)
        raio = 0.45 + 0.45 * k / max(1, quadros - 1)
        grosso = 0.3 - 0.17 * k / max(1, quadros - 1)
        saida.append(_tons(1 - np.abs(r - raio) / grosso, (0.0, 0.55), cores, contorno))
    return saida


# ------------------------------------------------------------------ descrição da aura

@dataclass
class Movimento:
    """Como a camada se mexe no motor. Amplitudes em fração (escala, alfa), px (deriva, tremor) e graus."""
    pulso: tuple = (0.04, 0.06)      # escala x, y pulsando em seno
    pulso_periodo: float = 96        # ticks
    contrafase: bool = True          # x incha quando y encolhe (respira como fumaça); False: incha tudo junto
    deriva: tuple = (0.0, 3.0)       # vai e vem em x, y
    deriva_periodo: float = 150
    tremor: float = 0.0              # tremor rápido em x
    tremor_periodo: float = 5
    giro: float = 0.0                # graus por tick (anel de foices)
    balanco: float = 0.0             # graus, em seno
    balanco_periodo: float = 130
    alfa: float = 0.85               # opacidade com a aura cheia
    respira: float = 0.12            # o alfa respira (fração do alfa)
    respira_periodo: float = 74
    fase: float = None               # ticks de adiantamento; None = cada camada ganha a sua


@dataclass
class Camada:
    nome: str
    quadros: list                    # arrays RGBA (ou PIL) do mesmo tamanho
    tempo: int = 2                   # ticks por quadro (aceite: <= 3)
    plano: str = "tras"              # "tras" (atrás do corpo), "chao" (no chão, atrás) ou "frente"
    pos: tuple = (0, 0)              # px a partir dos pés: x para a frente do lutador, y negativo para cima
    escala: tuple = (1.0, 1.0)
    eixo: tuple = None               # (x, y) no quadro; None = meio da base ("chao": centro)
    mistura: str = "normal"          # "normal" ou "soma" (raio, brasa)
    mov: Movimento = field(default_factory=Movimento)
    inicio: int = None               # elemento em que a animação começa (1..n); None = cada camada num ponto
    surto_incha: float = 0.22        # quanto a escala cresce no surto
    surto_alfa: float = 0.15
    surto_tremor: float = 1.5        # px a mais de tremor no surto
    prioridade: int = None           # sprpriority; None = pelo plano e pela ordem


@dataclass
class Particula:
    nome: str
    quadros: list                    # 1 quadro (pedra, elo) ou vários (anel de fumaça que abre)
    periodo: int = 9                 # nasce uma a cada tantos ticks
    vida: int = 44                   # ticks
    area: tuple = (-40, 0, 40, -80)  # onde nasce: x0, y0, x1, y1 a partir dos pés
    vel: tuple = (0.0, -1.2)         # px por tick
    vel_var: tuple = (0.8, 0.5)      # variação total em volta de vel
    grav: tuple = (0.0, 0.0)         # aceleração por tick (y positivo cai, negativo sobe mais)
    plano: str = "tras"
    escala: tuple = (1.0, 1.0)       # do nascer ao sumir
    tamanho_var: float = 0.3         # cada uma nasce de 1 - var/2 a 1 + var/2
    giro: tuple = (0.0, 0.0)         # graus do nascer ao sumir
    alfa: float = 0.9
    entra: int = 4                   # ticks do fade de entrada
    sai: float = 0.45                # fração final da vida em que some
    mistura: str = "normal"
    surto_extra: int = 3             # no surto nascem tantas vezes mais
    semente: int = 0


def _n(x):
    """Número curto para o .cns."""
    s = f"{float(x):.4f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def _seno(amp, periodo, fase, t):
    return f"{_n(amp)} * sin({t} * {_n(DOIS_PI / periodo)} + {_n(fase)})"


class Aura:
    """Uma aura: camadas + partículas, ligadas por uma condição do .cns.

    nome: curto, sem espaço (vira nome de map: au_<nome>_f...). ligada: expressão do .cns que é verdade enquanto o
    Despertar dura (ex. "var(20) > 0"). surto: expressão que dispara o surto (ex. "StateNo = 1000 && Time = 1"),
    ou None e o gerador põe `disparo_surto()` dentro do estado do especial. base: primeiro número de ação, de id
    de Explod e de grupo de sprite; a aura usa base .. base + nº de camadas + nº de partículas - 1."""

    def __init__(self, nome, camadas, particulas=(), ligada="var(20) > 0", surto=None, base=9300,
                 entra=26, sai=34, surto_ticks=30, surto_acel=1.6):
        assert re.fullmatch(r"[a-z0-9]+", nome), "nome da aura: só letras minúsculas e números"
        self.nome, self.camadas, self.particulas = nome, list(camadas), list(particulas)
        self.ligada, self.surto, self.base = ligada, surto, base
        self.entra, self.sai, self.surto_ticks, self.surto_acel = entra, sai, surto_ticks, surto_acel
        for c in self.camadas:
            assert c.plano in ("tras", "chao", "frente"), c.plano
            assert c.tempo <= 3, f"camada {c.nome}: quadro parado por mais de 3 ticks não é fluido"

    # ---- nomes e números
    def m(self, letra):
        return f"au_{self.nome}_{letra}"

    def id_camada(self, i):
        return self.base + i

    def id_particula(self, j):
        return self.base + len(self.camadas) + j

    def ids(self):
        return list(range(self.base, self.base + len(self.camadas) + len(self.particulas)))

    @staticmethod
    def _img(q):
        return q if isinstance(q, Image.Image) else Image.fromarray(np.asarray(q), "RGBA")

    def _eixo(self, item):
        w, h = self._img(item.quadros[0]).size
        if getattr(item, "eixo", None):
            return item.eixo
        if isinstance(item, Particula) or item.plano == "chao":
            return (w // 2, h // 2)
        return (w // 2, h - 1)

    def _itens(self):
        return [(self.id_camada(i), c) for i, c in enumerate(self.camadas)] + \
               [(self.id_particula(j), p) for j, p in enumerate(self.particulas)]

    # ---- sprites
    def sprites(self):
        """[(grupo, índice, imagem PIL RGBA, eixo x, eixo y)]: um grupo por camada/partícula, a partir de `base`."""
        saida = []
        for numero, item in self._itens():
            ex, ey = self._eixo(item)
            for k, q in enumerate(item.quadros):
                saida.append((numero, k, self._img(q), ex, ey))
        return saida

    def registrar(self, sprites):
        """Põe os quadros no objeto Sprites do gerador (o de gerar_pengaro.py: guardar(nome, img, grupo, indice, eixo))."""
        por = getattr(sprites, "guardar", None)
        for g, k, img, ex, ey in self.sprites():
            if por:
                por(f"aura_{self.nome}_{g}_{k}", img, g, k, (ex, ey))
            else:
                sprites.add(f"aura_{self.nome}_{g}_{k}", img, grupo=g, indice=k, eixo=(ex, ey))

    def altura(self):
        """Altura da aura em px do jogo (a camada mais alta, com escala e pulso)."""
        return max(self._img(c.quadros[0]).size[1] * c.escala[1] * (1 + abs(c.mov.pulso[1])) - c.pos[1]
                   for c in self.camadas)

    # ---- .air
    def air(self):
        t = []
        for i, c in enumerate(self.camadas):
            g = self.id_camada(i)
            t.append(f"; Aura {self.nome}, camada {c.nome} ({c.plano}): {len(c.quadros)} quadros de {c.tempo} ticks\n"
                     f"[Begin Action {g}]\n" + "".join(f"{g},{k}, 0,0, {c.tempo}\n" for k in range(len(c.quadros))))
        for j, p in enumerate(self.particulas):
            t.append(self._air_particula(self.id_particula(j), p))
        return "\n".join(t) + "\n"

    @staticmethod
    def _mistura(alfa, mistura):
        s = max(0, min(256, round(256 * alfa)))
        return f"AS{s}D{256 if mistura == 'soma' else 256 - s}"

    def _air_particula(self, g, p):
        """Vida inteira no .air: fade de entrada e de saída, escala e giro interpolados pelo motor a cada tick."""
        n = len(p.quadros)
        cortes = sorted({0, min(p.entra, p.vida - 2), max(p.entra + 1, round(p.vida * (1 - p.sai))), p.vida - 1}
                        | {round(k * (p.vida - 1) / n) for k in range(1, n)})

        def alfa(tk):
            if tk < p.entra:
                return p.alfa * tk / max(1, p.entra)
            ini = p.vida * (1 - p.sai)
            return p.alfa if tk <= ini else p.alfa * max(0.0, 1 - (tk - ini) / max(1, p.vida - 1 - ini))

        linhas = [f"; Aura {self.nome}, partícula {p.nome}: vive {p.vida} ticks\n[Begin Action {g}]\n"]
        for a, b in zip(cortes, cortes[1:] + [p.vida]):
            u = a / max(1, p.vida - 1)
            k = min(n - 1, int(a * n / p.vida))
            e = p.escala[0] + (p.escala[1] - p.escala[0]) * u
            ang = p.giro[0] + (p.giro[1] - p.giro[0]) * u
            if a:
                linhas.append("Interpolate Blend\nInterpolate Scale\nInterpolate Angle\n")
            linhas.append(f"{g},{k}, 0,0, {b - a}, , {self._mistura(alfa(a), p.mistura)}, {_n(e)},{_n(e)}, {_n(ang)}\n")
        return "".join(linhas)

    # ---- .cns
    def _fases(self, i, c):
        """Período e fase de cada movimento da camada i: nada bate com as outras camadas."""
        mv = c.mov
        desvio = (1.0, 1.27, 0.79, 1.49, 0.67, 1.13, 0.9, 1.38)[i % 8]
        fase = mv.fase if mv.fase is not None else i * 37.7
        return desvio, fase

    def _mover(self, i, c):
        mv, e = c.mov, self.id_camada(i)
        desvio, fase = self._fases(i, c)
        t = f"(map({self.m('t')}) + {_n(fase)})"
        f, k = f"map({self.m('e')})", f"map({self.m('k')})"
        cresce = f"(0.55 + 0.45 * {f}) * (1 + {_n(c.surto_incha)} * {k})"
        sx = f"{_n(c.escala[0])} * {cresce} * (1 + {_seno(mv.pulso[0], mv.pulso_periodo * desvio, 2.4 * i, t)})"
        sy = (f"{_n(c.escala[1])} * {cresce} * (1 + "
              f"{_seno(mv.pulso[1], mv.pulso_periodo * desvio, 2.4 * i + (math.pi if mv.contrafase else 0), t)})")
        px = f"{_n(c.pos[0])}"
        if mv.deriva[0]:
            px += f" + {_seno(mv.deriva[0], mv.deriva_periodo * desvio, 1.3 + i, t)}"
        if mv.tremor or c.surto_tremor:
            px += (f" + ({_n(mv.tremor)} + {_n(c.surto_tremor)} * {k}) * "
                   f"sin({t} * {_n(DOIS_PI / mv.tremor_periodo)} + {_n(2.1 * i)})")
        py = f"{_n(c.pos[1])}"
        if mv.deriva[1]:
            py += f" + {_seno(mv.deriva[1], mv.deriva_periodo * desvio * 0.83, 2.9 + 1.7 * i, t)}"
        alfa = (f"({_n(mv.alfa)} * {f} * (1 + {_seno(mv.respira, mv.respira_periodo * desvio, 0.4 + 2.3 * i, t)})"
                f" + {_n(c.surto_alfa)} * {k} * {f})")
        if c.plano == "chao":  # fica no chão quando o lutador pula, e some com a altura
            py += " - Pos Y"
            alfa += " * max(0, 1 + Pos Y / 90.0)"
        src = f"floor(255 * min(1, max(0, {alfa})))"
        linhas = [f"[State -2, Aura {self.nome} {c.nome}: move]", "type = ModifyExplod",
                  f"trigger1 = NumExplod({e})", f"id = {e}", "postype = p1", f"pos = {px}, {py}",
                  f"scale = {sx}, {sy}"]
        if mv.giro or mv.balanco:
            ang = f"{_n(mv.giro)} * {t}" if mv.giro else "0"
            if mv.balanco:
                ang += f" + {_seno(mv.balanco, mv.balanco_periodo * desvio, 0.9 * i, t)}"
            linhas.append(f"angle = {ang}")
        linhas += ["trans = addalpha", f"alpha = {src}, {'255' if c.mistura == 'soma' else f'255 - {src}'}",
                   "ignorehitpause = 1"]
        return "\n".join(linhas) + "\n\n"

    def _prioridade(self, i, c):
        if c.prioridade is not None:
            return c.prioridade
        return {"chao": -9 + i, "tras": -6 + i, "frente": 5 + i}[c.plano]

    def _nascer(self, i, c):
        e = self.id_camada(i)
        n = len(c.quadros)
        # animelemtime: as camadas trocam de quadro em ticks alternados, para todo tick ter desenho novo
        inicio = c.inicio if c.inicio is not None else 1 + (i * max(1, round(n * 0.382))) % n
        return (f"[State -2, Aura {self.nome} {c.nome}: nasce]\ntype = Explod\n"
                f"trigger1 = map({self.m('f')}) > 0 && NumExplod({e}) = 0\n"
                f"anim = {e}\nid = {e}\nanimelem = {inicio}\nanimelemtime = {i % c.tempo}\npostype = p1\npos = {_n(c.pos[0])}, {_n(c.pos[1])}\n"
                f"facing = 1\nbindtime = -1\nremovetime = -1\nsprpriority = {self._prioridade(i, c)}\nownpal = 1\n"
                f"scale = {_n(c.escala[0] * 0.55)}, {_n(c.escala[1] * 0.55)}\ntrans = addalpha\nalpha = 0, 255\n"
                f"removeongethit = 0\nsupermovetime = -1\npausemovetime = -1\nignorehitpause = 1\n\n")

    def _emitir(self, j, p):
        e = self.id_particula(j)
        s = p.semente + 17 * j
        x0, y0, x1, y1 = p.area

        def acaso(mult, mod, k):
            """0..1 que muda a cada nascimento, derivado do GameTime (sem Random: o replay sai igual)."""
            return f"((GameTime * {mult} + {s + k}) % {mod}) / {mod - 1}.0"

        rapido = max(1, p.periodo // max(1, p.surto_extra))
        tam = f"({_n(1 - p.tamanho_var / 2)} + {_n(p.tamanho_var)} * {acaso(29, 53, 5)})"
        pri = {"chao": -8, "tras": -4 + j % 2, "frente": 7 + j % 2}[p.plano]
        return (f"[State -2, Aura {self.nome}: solta {p.nome}]\ntype = Explod\n"
                f"triggerall = map({self.m('e')}) > 0.3 && NumExplod({e}) < {max(4, 3 * p.vida // max(1, rapido))}\n"
                f"trigger1 = (GameTime % {p.periodo}) = {s % p.periodo}\n"
                f"trigger2 = map({self.m('k')}) > 0.25 && (GameTime % {rapido}) = 0\n"
                f"anim = {e}\nid = {e}\npostype = p1\n"
                f"pos = {_n(x0)} + {_n(x1 - x0)} * {acaso(37, 101, 0)}, {_n(y0)} + {_n(y1 - y0)} * {acaso(53, 89, 1)}\n"
                f"vel = {_n(p.vel[0] - p.vel_var[0] / 2)} + {_n(p.vel_var[0])} * {acaso(41, 97, 2)}, "
                f"{_n(p.vel[1] - p.vel_var[1] / 2)} + {_n(p.vel_var[1])} * {acaso(61, 83, 3)}\n"
                f"accel = {_n(p.grav[0])}, {_n(p.grav[1])}\n"
                f"facing = ifelse(((GameTime * 7 + {s}) % 13) < 6, 1, -1)\nbindtime = 0\nremovetime = {p.vida}\n"
                f"scale = {tam}, {tam}\nsprpriority = {pri}\nownpal = 1\nremoveongethit = 0\n"
                f"supermovetime = -1\npausemovetime = -1\nignorehitpause = 1\n\n")

    def cns(self):
        """Controladores para o [Statedef -2] do lutador (cole depois da contagem do Despertar)."""
        f, e, s, k, t = (self.m(x) for x in "feskt")
        ligada = f"({self.ligada}) && alive && RoundState = 2"
        todos = self.ids()

        def mapa(nome, titulo, gatilho, valor):
            return (f"[State -2, Aura {self.nome}: {titulo}]\ntype = MapSet\ntrigger1 = {gatilho}\n"
                    f"map = \"{nome}\"\nvalue = {valor}\nignorehitpause = 1\n\n")

        c = [f"; ---- Aura animada '{self.nome}' (ferramentas/aura.py): {len(self.camadas)} camadas, "
             f"{len(self.particulas)} partículas, explods {todos[0]} a {todos[-1]}\n"]
        # entre rounds não sobra nada: maps zerados e explods removidos
        for nome in (f, e, s, k, t):
            c.append(mapa(nome, f"zera {nome} fora do round", "RoundState < 2", "0"))
        for i in todos:
            c.append(f"[State -2, Aura {self.nome}: limpa {i} fora do round]\ntype = RemoveExplod\n"
                     f"trigger1 = RoundState < 2 && NumExplod({i})\nid = {i}\nignorehitpause = 1\n\n")
        c.append(mapa(t, "tempo volta a zero ao ligar", f"map({f}) <= 0", "0"))
        c.append(mapa(f, "fade", "RoundState >= 2",
                      f"ifelse({ligada}, min(1, map({f}) + {_n(1 / self.entra)}), max(0, map({f}) - {_n(1 / self.sai)}))"))
        c.append(mapa(e, "fade suave", "1", f"map({f}) * map({f}) * (3 - 2 * map({f}))"))
        if self.surto:
            c.append(mapa(s, "surto dispara", f"({self.surto}) && map({f}) > 0", "1"))
        c.append(mapa(k, "surto sobe e desce macio", "1",
                      f"map({k}) + (ifelse(map({s}) > 0, 1, 0) - map({k})) * 0.14"))
        c.append(mapa(s, "surto conta", f"map({s}) > 0", f"max(0, map({s}) - {_n(1 / self.surto_ticks)})"))
        c.append(f"[State -2, Aura {self.nome}: tempo anda (mais rápido no surto)]\ntype = MapAdd\n"
                 f"trigger1 = map({f}) > 0\nmap = \"{t}\"\nvalue = 1 + {_n(self.surto_acel)} * map({k})\n"
                 f"ignorehitpause = 1\n\n")
        for i, cam in enumerate(self.camadas):
            c.append(self._nascer(i, cam))
        for i, cam in enumerate(self.camadas):
            c.append(self._mover(i, cam))
        for i, cam in enumerate(self.camadas):
            n = self.id_camada(i)
            # no surto a animação também corre: um quadro por tick
            c.append(f"[State -2, Aura {self.nome} {cam.nome}: corre no surto]\ntype = ModifyExplod\n"
                     f"trigger1 = NumExplod({n}) && map({k}) > 0.5\nid = {n}\n"
                     f"animelem = ((ExplodVar({n}, 0, animelem) - {1 if i % cam.tempo == cam.tempo - 1 else 0}) "
                     f"% {len(cam.quadros)}) + 1\nanimelemtime = {i % cam.tempo}\nignorehitpause = 1\n\n")
            c.append(f"[State -2, Aura {self.nome} {cam.nome}: some]\ntype = RemoveExplod\n"
                     f"trigger1 = map({f}) <= 0 && NumExplod({n})\nid = {n}\nignorehitpause = 1\n\n")
        for j, p in enumerate(self.particulas):
            c.append(self._emitir(j, p))
        return "".join(c)

    def disparo_surto(self, gatilho="Time = 0", estado=""):
        """Controlador para pôr DENTRO do estado de um especial: dispara o surto da aura."""
        return (f"[State {estado}, Aura {self.nome}: surto]\ntype = MapSet\ntrigger1 = {gatilho}\n"
                f"map = \"{self.m('s')}\"\nvalue = 1\nignorehitpause = 1\n\n")

    def resumo(self):
        linhas = [f"aura {self.nome}: altura {self.altura():.0f} px, explods {self.ids()[0]} a {self.ids()[-1]}"]
        for i, c in enumerate(self.camadas):
            d, fa = self._fases(i, c)
            w, h = self._img(c.quadros[0]).size
            linhas.append(f"  camada {c.nome} ({c.plano}): {len(c.quadros)} quadros x {c.tempo} ticks, {w}x{h} px, "
                          f"pulso a cada {c.mov.pulso_periodo * d:.0f} ticks, fase {fa:.0f}")
        for p in self.particulas:
            linhas.append(f"  partícula {p.nome}: 1 a cada {p.periodo} ticks, vive {p.vida}")
        return "\n".join(linhas)


def salvar_quadros(quadros, pasta):
    """Grava os quadros em pasta/NN.png (para olhar ou para o gerador ler depois sem refazer o fluxo óptico)."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    for f in pasta.glob("*.png"):
        f.unlink()
    for i, q in enumerate(quadros):
        Aura._img(q).save(pasta / f"{i:02d}.png")


def ler_quadros(pasta):
    return [np.array(Image.open(f).convert("RGBA")) for f in sorted(Path(pasta).glob("*.png"))]


def tira(quadros, fundo=(40, 40, 48), colunas=None):
    """Folha de contato dos quadros (para conferir com os olhos)."""
    imgs = [Aura._img(q) for q in quadros]
    colunas = colunas or len(imgs)
    w, h = imgs[0].size
    t = Image.new("RGB", (w * colunas, h * math.ceil(len(imgs) / colunas)), fundo)
    for i, im in enumerate(imgs):
        t.paste(im, ((i % colunas) * w, (i // colunas) * h), im)
    return t
