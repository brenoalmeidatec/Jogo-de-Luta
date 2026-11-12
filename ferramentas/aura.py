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
    if metodo == "fluxo" and min(chaves[0].shape[:2]) < 12:
        metodo = "mistura"  # desenho pequeno demais para o fluxo óptico (o OpenCV pede 12 px de lado)
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


# ------------------------------------------------------------------ movimento assado no desenho (na grade do pixel)
# O motor NÃO escala nem gira a aura em regime: escala e ângulo fora de 1 e 0 quebram a grade do pixel na tela de
# 1280 (vira mosaico de blocos tortos). O que cresce, gira ou balança é assado aqui, em quadros, na grade do jogo.

def reduzir(quadros, fx, fy=None, cores=32):
    """Os mesmos quadros em outro tamanho (fx, fy em fração), na grade do jogo e nas cores do desenho."""
    fy = fx if fy is None else fy
    pal = _paleta_dos_desenhos(quadros, cores)
    h, w = quadros[0].shape[:2]
    tam = (max(1, round(w * fx)), max(1, round(h * fy)))
    saida = []
    for q in quadros:
        red = cv2.resize(_pre(q), tam, interpolation=cv2.INTER_AREA if fx <= 1 and fy <= 1 else cv2.INTER_LINEAR)
        a = red[..., 3:]
        cor = np.where(a > 1, red[..., :3] * 255 / np.maximum(a, 1), 0)
        s = np.dstack([np.clip(cor, 0, 255), np.where(a[..., 0] >= 128, 255, 0)]).astype(np.uint8)
        saida.append(_na_paleta(s, pal))
    return saida


def espelhar(quadros):
    return [np.ascontiguousarray(q[:, ::-1]) for q in quadros]


def ondular(quadros, amplitude=3, ondas=1.0, voltas=1):
    """Balanço assado: cada linha do desenho escorrega de lado, numa onda que sobe e dá `voltas` inteiras no loop
    (fecha sem emenda). A base não sai do lugar; o topo anda até `amplitude` px. Só anda px inteiro."""
    n = len(quadros)
    h, w = quadros[0].shape[:2]
    m = int(math.ceil(amplitude))
    saida = []
    for k, q in enumerate(quadros):
        s = np.zeros((h, w + 2 * m, 4), np.uint8)
        for y in range(h):
            v = 1 - y / max(1, h - 1)
            dx = int(round(amplitude * v * math.sin(DOIS_PI * (ondas * v - voltas * k / n))))
            s[y, m + dx:m + dx + w] = q[y]
        saida.append(s)
    return saida


def _girado(q, graus, escala, lado, pal=None):
    """Um quadro girado e escalado em volta do centro, numa tela quadrada de `lado` px, na grade do jogo."""
    h, w = q.shape[:2]
    m = cv2.getRotationMatrix2D(((w - 1) / 2, (h - 1) / 2), -graus, escala)
    m[0, 2] += (lado - 1) / 2 - (w - 1) / 2
    m[1, 2] += (lado - 1) / 2 - (h - 1) / 2
    if abs(escala - 1) < 1e-6:  # só gira: vizinho mais próximo, o pixel continua pixel
        s = cv2.warpAffine(np.ascontiguousarray(q), m, (lado, lado), flags=cv2.INTER_NEAREST, borderValue=(0, 0, 0, 0))
        s[s[..., 3] < 128] = 0
        return s
    red = cv2.warpAffine(_pre(q), m, (lado, lado), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    a = red[..., 3:]
    cor = np.where(a > 1, red[..., :3] * 255 / np.maximum(a, 1), 0)
    s = np.dstack([np.clip(cor, 0, 255), np.where(a[..., 0] >= 128, 255, 0)]).astype(np.uint8)
    return _na_paleta(s, pal)


def girar_loop(desenhos, quadros=24, volta=1.0, sentido=1):
    """Giro assado (anel de foices, leque): `quadros` quadros que somam `volta` de volta (1.0 = 360 graus; para uma
    peça com simetria de N pontas use 1/N e o loop fecha igual). `desenhos` pode ter 1 desenho ou vários (a
    animação própria da peça anda junto). Eixo no centro."""
    desenhos = [np.asarray(d) for d in desenhos]
    h, w = desenhos[0].shape[:2]
    lado = int(math.ceil(math.hypot(w, h))) + 2
    return [_girado(desenhos[(k * len(desenhos)) // quadros], sentido * 360.0 * volta * k / quadros, 1.0, lado)
            for k in range(quadros)]


def nevoa_rasteira(largura=120, altura=13, quadros=24, cores=((52, 24, 84), (110, 62, 160)), contorno=(18, 8, 30),
                   semente=5, cobre=0.4):
    """Névoa rente ao chão para a camada "frente": tufos baixos que correm de lado, em loop exato. `cobre` é a
    fração (aproximada) da faixa que fica pintada; o resto é buraco, para os pés aparecerem. Eixo no meio da base."""
    rng = np.random.default_rng(semente)
    ys, xs = np.mgrid[0:altura, 0:largura].astype(np.float32)
    u = xs / largura
    v = 1 - ys / max(1, altura - 1)
    ondas = [(rng.uniform(0.6, 1.3), int(rng.integers(2, 7)), int(rng.choice([-2, -1, 1, 2])), rng.uniform(0, DOIS_PI),
              rng.uniform(0.5, 2.0)) for _ in range(7)]
    soma = sum(o[0] for o in ondas)
    campos = []
    for k in range(quadros):
        t = k / quadros
        ruido = sum(a * np.cos(DOIS_PI * (fx * u - m * t) + f + fy * v) for a, fx, m, f, fy in ondas) / soma
        dens = ruido - 1.6 * np.abs(v - 0.35) - np.clip((np.abs(u - 0.5) - 0.38) / 0.1, 0, 1) * 2
        campos.append(cv2.GaussianBlur(dens, (0, 0), 0.8))
    corte = float(np.quantile(np.stack(campos)[:, :, largura // 6:-largura // 6], 1 - cobre))
    return [_tons(d - corte, (0.0, 0.22), cores, contorno) for d in campos]


# ------------------------------------------------------------------ descrição da aura

@dataclass
class Movimento:
    """O que o motor mexe na camada a cada tick, sem tocar na grade do pixel: posição (pode ser fração de px) e alfa.
    Amplitudes em px (deriva, tremor) e fração (alfa). Crescer, girar e balançar são assados no desenho
    (reduzir, girar_loop, ondular)."""
    deriva: tuple = (0.0, 3.0)       # vai e vem em x, y
    deriva_periodo: float = 150      # ticks
    tremor: float = 0.0              # tremor rápido em x
    tremor_periodo: float = 5
    alfa: float = 0.85               # opacidade com a aura cheia
    respira: float = 0.12            # o alfa respira (fração do alfa)
    respira_periodo: float = 74
    fase: float = None               # ticks de adiantamento; None = cada camada ganha a sua


@dataclass
class Camada:
    nome: str
    quadros: list                    # arrays RGBA (ou PIL) do mesmo tamanho
    tempo: int = 2                   # ticks por quadro (aceite: <= 3)
    plano: str = "tras"              # "tras" (atrás do corpo), "chao" (no chão, atrás) ou "frente" (só rente ao chão)
    pos: tuple = (0, 0)              # px a partir dos pés: x para a frente do lutador, y negativo para cima
    eixo: tuple = None               # (x, y) no quadro; None = meio da base ("chao": centro)
    mistura: str = "normal"          # "normal" ou "soma" (raio, brasa)
    mov: Movimento = field(default_factory=Movimento)
    inicio: int = None               # elemento em que a animação começa (1..n); None = cada camada num ponto
    surto_incha: float = 0.12        # quanto a escala cresce no surto (passageiro: única escala fora de 1 do motor)
    surto_alfa: float = 0.15
    surto_tremor: float = 1.5        # px a mais de tremor no surto
    prioridade: int = None           # sprpriority; None = pelo plano e pela ordem
    esconde: str = None              # expressão do .cns: enquanto for verdade a camada apaga (em ~8 ticks) e volta
                                     # depois; para a reação avulsa do gerador tocar no lugar dela, sem dobrar
    tique: int = None                # tique do passo (0..tempo-1) em que a camada troca de quadro; None = índice % tempo.
                                     # Camadas desenhadas juntas (as metades de um anel) trocam no mesmo tique; as que
                                     # dividem a mesma região da tela, em tiques diferentes (todo tique tem desenho novo)
    no_chao: bool = None             # fica no chão quando o lutador sai dele (pulo, queda); None = só o plano "chao".
                                     # Uma coluna que nasce do chão usa True com plano "tras": não sobe junto no pulo
                                     # e não apaga com a altura (só a camada de plano "chao" apaga)
    cresce: bool = True              # na entrada e na saída a camada cresce (escala do motor, passageira); False =
                                     # só o alfa (o paredão do CK achatado a 8% virava elipse, cético de 2026-11-12)
    res: int = 1                     # px do quadro por px do jogo. 3 = desenho em 3x (docs/regra-efeitos-proporcionais.md):
                                     # o Explod não usa a escala do lutador, então a escala dele vai a 1/res em tudo

    def troca(self, i):
        return (i if self.tique is None else self.tique) % self.tempo

    @property
    def presa_ao_chao(self):
        return self.plano == "chao" if self.no_chao is None else self.no_chao


@dataclass
class Particula:
    nome: str
    quadros: list                    # os desenhos da peça (2 ou mais), ou 1 desenho com giro/escala assados
    periodo: int = 9                 # nasce uma a cada tantos ticks
    vida: int = 44                   # ticks
    area: tuple = (-40, 0, 40, -80)  # onde nasce: x0, y0, x1, y1 a partir dos pés
    vel: tuple = (0.0, -1.2)         # px por tick
    vel_var: tuple = (0.8, 0.5)      # variação total em volta de vel
    grav: tuple = (0.0, 0.0)         # aceleração por tick (y positivo cai, negativo sobe mais)
    plano: str = "tras"              # "tras" ou "chao": partícula nunca passa na frente do corpo
    escala: tuple = (1.0, 1.0)       # do nascer ao sumir (assada em quadros, na grade do jogo)
    giro: tuple = (0.0, 0.0)         # graus do nascer ao sumir (assado em quadros)
    passo: int = 2                   # ticks por quadro assado
    alfa: float = 0.9
    entra: int = 4                   # ticks do fade de entrada
    sai: float = 0.45                # fração final da vida em que some
    mistura: str = "normal"
    surto_extra: int = 2             # no surto nascem tantas vezes mais
    semente: int = 0


def _n(x):
    """Número curto para o .cns."""
    s = f"{float(x):.4f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def _seno(amp, periodo, fase, t):
    return f"{_n(amp)} * sin({t} * {_n(DOIS_PI / periodo)} + {_n(fase)})"


# Espalhamento das partículas: sequência de baixa discrepância. A n-ésima peça nasce em (n * A) mod 1009 / 1008; com
# A/1009 perto de um irracional "ruim de aproximar", peças seguidas caem longe uma da outra (de 23% a 43% da área) e
# o conjunto cobre a área por igual, sem fila. Cada canal (x, y, vx, vy, lado) e cada partícula usa um A diferente.
PRIMO = 1009
_SALTOS = (624, 762, 575, 418, 739, 238, 328, 441, 683)  # 0.618, 0.755, 0.570, 0.414, 0.732, 0.236, 0.325, 0.437, 0.677


class Aura:
    """Uma aura: camadas + partículas, ligadas por uma condição do .cns.

    nome: curto, sem espaço (vira nome de map: au_<nome>_f...). ligada: expressão do .cns que é verdade enquanto o
    Despertar dura (ex. "var(20) > 0"); vale também na intro e na pose de vitória. surto: expressão que dispara o
    surto (ex. "StateNo = [3000, 3999] && Time = 1"), ou None e o gerador põe `disparo_surto()` dentro do estado.
    base: primeiro número de ação, de id de Explod e de grupo de sprite; a aura usa base .. base + nº de camadas +
    nº de partículas - 1 (confira com `conferir()` que o lutador não usa esses números).
    altura_lutador: px do jogo, para o limite da camada da frente. teto_explods: o máximo de Explods vivos da aura
    no pior caso (camadas + partículas no surto); a soma dos tetos das partículas tem de caber."""

    FRENTE_ALTURA = 0.13   # a camada "frente" sobe no máximo isto da altura do lutador acima dos pés (tornozelo)
    FRENTE_ALFA = 0.5

    def __init__(self, nome, camadas, particulas=(), ligada="var(20) > 0", surto=None, base=9600,
                 entra=26, sai=34, surto_ticks=30, surto_acel=1.6, surto_folga=90, altura_lutador=110,
                 teto_explods=30, virada_fundo=0.3, resta=None):
        assert re.fullmatch(r"[a-z0-9]+", nome), "nome da aura: só letras minúsculas e números"
        self.nome, self.camadas, self.particulas = nome, list(camadas), list(particulas)
        self.ligada, self.surto, self.base = ligada, surto, base
        # resta: expressão do .cns com os ticks que faltam para o corpo voltar (ex. "var(20)"). O fade nunca passa de
        # resta / sai: a saída anda junto com o contador do lutador, e não pelo relógio do -4 (o -4 roda em pausa,
        # superpausa e hitpause; o var(20) do -2 para nelas). None = fade pelo relógio, como antes.
        self.resta = resta
        self.entra, self.sai, self.surto_ticks, self.surto_acel = entra, sai, surto_ticks, surto_acel
        self.surto_folga, self.altura_lutador, self.teto_explods = surto_folga, altura_lutador, teto_explods
        # na virada a aura apaga até esta fração do alfa, troca de lado e volta (0,3: some quase toda; 1: nem apaga)
        assert 0 < virada_fundo <= 1, virada_fundo
        self.virada_fundo = virada_fundo
        for c in self.camadas:
            assert c.plano in ("tras", "chao", "frente"), c.plano
            assert c.tempo <= 3, f"camada {c.nome}: quadro parado por mais de 3 ticks não é fluido"
            assert len(c.quadros) >= 8, f"camada {c.nome}: {len(c.quadros)} quadros; camada parada ou curta não passa"
            if c.plano == "frente":
                sobe = self._eixo(c)[1] / c.res - c.pos[1]
                limite = self.FRENTE_ALTURA * altura_lutador
                assert sobe <= limite + 0.5, (f"camada {c.nome}: a frente sobe {sobe:.0f} px acima dos pés "
                                              f"(máximo {limite:.0f}): ela esconderia pernas e golpe baixo")
                assert c.mov.alfa + c.surto_alfa <= self.FRENTE_ALFA + 1e-6, \
                    f"camada {c.nome}: frente com alfa acima de {self.FRENTE_ALFA} (contando o surto)"
                assert not any(o.quadros is c.quadros for o in self.camadas if o is not c), \
                    f"camada {c.nome}: a frente não pode ser a cópia de outra camada"
        self._vidas = []
        for p in self.particulas:
            assert p.plano in ("tras", "chao"), f"partícula {p.nome}: partícula não passa na frente do corpo"
            vida = self._assar(p)
            assert any(a.shape != b.shape or diferenca(a, b) > 0 for a, b in zip(vida, vida[1:])), \
                f"partícula {p.nome}: um desenho só, sem giro nem escala, é imagem parada"
            self._vidas.append(vida)
        assert self.pico() <= teto_explods, (f"aura {nome}: {self.pico()} Explods no pior caso (teto {teto_explods}); "
                                             f"aumente o periodo ou encurte a vida das partículas")

    # ---- nomes e números
    def m(self, letra):
        return f"au_{self.nome}_{letra}"

    def id_camada(self, i):
        return self.base + i

    def id_particula(self, j):
        return self.base + len(self.camadas) + j

    def ids(self):
        return list(range(self.base, self.base + len(self.camadas) + len(self.particulas)))

    # Regra dos efeitos proporcionais (Breno, 2026-11-12): a aura do Despertar é discreta. Uma camada leve, atrás do
    # corpo, que não passa do peito, translúcida (o fundo aparece através dela) e desenhada em 3x.
    DISCRETA_CAMADAS = 1
    DISCRETA_ALTURA = 0.65   # fração da altura do lutador (o peito fica em ~0,7; a cabeça começa em ~0,85)
    DISCRETA_ALFA = 0.65     # alfa máximo, contando a respiração e o surto

    def conferir_discreta(self):
        """Falha se a aura não segue a regra dos efeitos proporcionais (docs/regra-efeitos-proporcionais.md)."""
        assert len(self.camadas) <= self.DISCRETA_CAMADAS and not self.particulas, \
            f"aura {self.nome}: {len(self.camadas)} camadas e {len(self.particulas)} partículas (a regra é uma só)"
        assert all(c.plano != "frente" for c in self.camadas), f"aura {self.nome}: camada na frente do corpo"
        assert all(c.res == 3 for c in self.camadas), f"aura {self.nome}: desenho fora de 3x"
        alt = self.altura()
        assert alt <= self.DISCRETA_ALTURA * self.altura_lutador, \
            f"aura {self.nome}: {alt:.0f} px de altura (máximo {self.DISCRETA_ALTURA * self.altura_lutador:.0f})"
        for c in self.camadas:
            pico = c.mov.alfa * (1 + c.mov.respira) + c.surto_alfa
            assert pico <= self.DISCRETA_ALFA + 1e-6, f"aura {self.nome}: alfa até {pico:.2f} (máximo {self.DISCRETA_ALFA})"

    def conferir(self, grupos=(), acoes=(), explods=()):
        """Falha se o lutador já usa algum número da aura (grupos de sprite, ações do .air, ids de Explod)."""
        meus = set(self.ids())
        for nome, usados in (("grupo de sprite", grupos), ("ação", acoes), ("id de Explod", explods)):
            bate = sorted(meus & {int(x) for x in usados})
            assert not bate, f"aura {self.nome}: {nome} {bate} já é do lutador; mude `base` (hoje {self.base})"

    @staticmethod
    def _img(q):
        return q if isinstance(q, Image.Image) else Image.fromarray(np.asarray(q), "RGBA")

    def _eixo(self, item):
        if getattr(item, "eixo", None):
            return item.eixo
        w, h = self._img(item.quadros[0]).size
        if item.plano == "chao":
            return (w // 2, h // 2)
        return (w // 2, h - 1)

    def _assar(self, p):
        """Os quadros da vida inteira da partícula, um a cada `passo` ticks: desenho, escala e giro já na grade."""
        desenhos = [np.asarray(self._img(q)) for q in p.quadros]
        passos = max(2, math.ceil(p.vida / p.passo))
        if tuple(p.escala) == (1.0, 1.0) and tuple(p.giro) == (0.0, 0.0):
            return [desenhos[min(len(desenhos) - 1, (i * len(desenhos)) // passos)] for i in range(passos)]
        h, w = desenhos[0].shape[:2]
        lado = int(math.ceil(math.hypot(w, h) * max(p.escala))) + 2
        pal = _paleta_dos_desenhos(desenhos, 32)
        saida = []
        for i in range(passos):
            u = i / (passos - 1)
            saida.append(_girado(desenhos[min(len(desenhos) - 1, (i * len(desenhos)) // passos)],
                                 p.giro[0] + (p.giro[1] - p.giro[0]) * u,
                                 p.escala[0] + (p.escala[1] - p.escala[0]) * u, lado, pal))
        return saida

    def _itens(self):
        """[(número, quadros, eixo)] de cada camada e de cada partícula (esta com a vida assada, eixo no centro)."""
        saida = [(self.id_camada(i), c.quadros, self._eixo(c)) for i, c in enumerate(self.camadas)]
        for j, vida in enumerate(self._vidas):
            h, w = vida[0].shape[:2]
            saida.append((self.id_particula(j), vida, (w // 2, h // 2)))
        return saida

    # ---- sprites
    def sprites(self):
        """[(grupo, índice, imagem PIL RGBA, eixo x, eixo y)]: um grupo por camada/partícula, a partir de `base`."""
        return [(numero, k, self._img(q), ex, ey) for numero, quadros, (ex, ey) in self._itens()
                for k, q in enumerate(quadros)]

    def registrar(self, sprites):
        """Põe os quadros no .sff do gerador e devolve o conjunto {(grupo, índice)} que entrou.

        Serve para os três jeitos que os geradores têm: objeto com `guardar(nome, img, grupo, indice, eixo)`
        (gerar_pengaro.py), com `add(nome, img, grupo=, indice=, eixo=)`, ou com a lista `lista` de
        (grupo, índice, imagem, eixo x, eixo y) (gerar_hazaki.py: some o conjunto devolvido ao `manter` do
        `escrever_sff`, senão a poda tira a aura). Também aceita uma lista pura. Confere antes que nenhum grupo
        da aura já existe."""
        lista = sprites if isinstance(sprites, list) else getattr(sprites, "lista", None)
        if lista is not None:
            self.conferir(grupos={t[0] for t in lista})
        entrou = set()
        for g, k, img, ex, ey in self.sprites():
            entrou.add((g, k))
            if hasattr(sprites, "guardar"):
                sprites.guardar(f"aura_{self.nome}_{g}_{k}", img, g, k, (ex, ey))
            elif hasattr(sprites, "add"):
                sprites.add(f"aura_{self.nome}_{g}_{k}", img, grupo=g, indice=k, eixo=(ex, ey))
            else:
                lista.append((g, k, img, ex, ey))
        return entrou

    def altura(self):
        """Altura da aura em px do jogo acima dos pés: do pé ao pixel opaco mais alto de todos os quadros (a camada
        mais alta)."""
        def topo(c):
            return min(int(np.argmax(np.asarray(self._img(q))[..., 3].any(axis=1))) for q in c.quadros)
        return max((self._eixo(c)[1] - topo(c)) / c.res - c.pos[1] for c in self.camadas)

    def teto_particula(self, p):
        """Máximo de peças vivas desta partícula: as do regime calmo mais as que um surto inteiro solta a mais."""
        return math.ceil(p.vida / p.periodo) + math.ceil(self.surto_ticks * (p.surto_extra - 1) / p.periodo) + 1

    def pico(self):
        """Explods vivos da aura no pior caso."""
        return len(self.camadas) + sum(self.teto_particula(p) for p in self.particulas)

    # ---- .air
    def air(self):
        t = []
        for i, c in enumerate(self.camadas):
            g = self.id_camada(i)
            t.append(f"; Aura {self.nome}, camada {c.nome} ({c.plano}): {len(c.quadros)} quadros de {c.tempo} ticks\n"
                     f"[Begin Action {g}]\n" + "".join(f"{g},{k}, 0,0, {c.tempo}\n" for k in range(len(c.quadros))))
        for j, p in enumerate(self.particulas):
            t.append(self._air_particula(self.id_particula(j), p, len(self._vidas[j])))
        return "\n".join(t) + "\n"

    @staticmethod
    def _mistura(alfa, mistura):
        s = max(0, min(256, round(256 * alfa)))
        return f"AS{s}D{256 if mistura == 'soma' else 256 - s}"

    def _air_particula(self, g, p, passos):
        """Vida inteira no .air: um quadro assado a cada `passo` ticks; o motor só interpola o alfa (Blend)."""

        def alfa(tk):
            if tk < p.entra:
                return p.alfa * tk / max(1, p.entra)
            ini = p.vida * (1 - p.sai)
            return p.alfa if tk <= ini else p.alfa * max(0.0, 1 - (tk - ini) / max(1, p.vida - 1 - ini))

        linhas = [f"; Aura {self.nome}, partícula {p.nome}: vive {p.vida} ticks, {passos} quadros assados\n"
                  f"[Begin Action {g}]\n"]
        for i in range(passos):
            a = i * p.passo
            dura = p.passo if i < passos - 1 else max(1, p.vida - a)
            if i:
                linhas.append("Interpolate Blend\n")
            linhas.append(f"{g},{i}, 0,0, {dura}, , {self._mistura(alfa(a), p.mistura)}\n")
        return "".join(linhas)

    # ---- .cns
    def _fases(self, i, c):
        """Período e fase de cada movimento da camada i: nada bate com as outras camadas."""
        mv = c.mov
        desvio = (1.0, 1.27, 0.79, 1.49, 0.67, 1.13, 0.9, 1.38)[i % 8]
        fase = mv.fase if mv.fase is not None else i * 37.7
        return desvio, fase

    def _mover(self, i, c):
        """Dois controladores por camada: o de sempre (posição, escala, alfa; vira junto com o lutador) e o da
        virada (só alfa, enquanto a camada apaga antes de trocar de lado)."""
        mv, e = c.mov, self.id_camada(i)
        desvio, fase = self._fases(i, c)
        t = f"(map({self.m('t')}) + {_n(fase)})"
        f, k, v = f"map({self.m('e')})", f"map({self.m('k')})", f"map({self.m('v')})"
        incha = f"(1 + {_n(c.surto_incha)} * {k})"
        if c.res != 1:         # desenho em 3x: a escala do motor é 1/res (o resto multiplica em cima)
            incha = f"{incha} * {_n(1 / c.res)}"
        if not c.cresce:       # entra e sai só pelo alfa (um muro achatado vira elipse: paredão do CK)
            sx = sy = incha
        elif c.plano == "chao":  # o anel abre do centro
            sx = sy = f"(0.3 + 0.7 * {f}) * {incha}"
        else:                  # a coluna cresce dos pés: nasce rente ao chão e sobe
            sx, sy = f"(0.7 + 0.3 * {f}) * {incha}", f"(0.08 + 0.92 * {f}) * {incha}"
        px = f"{_n(c.pos[0])}"
        if mv.deriva[0]:
            px += f" + {_seno(mv.deriva[0], mv.deriva_periodo * desvio, 1.3 + i, t)}"
        if mv.tremor or c.surto_tremor:
            px += (f" + ({_n(mv.tremor)} + {_n(c.surto_tremor)} * {k}) * "
                   f"sin({t} * {_n(DOIS_PI / mv.tremor_periodo)} + {_n(2.1 * i)})")
        py = f"{_n(c.pos[1])}"
        if mv.deriva[1]:
            py += f" + {_seno(mv.deriva[1], mv.deriva_periodo * desvio * 0.83, 2.9 + 1.7 * i, t)}"
        # o alfa chega antes da altura (a aura aparece baixa e sobe, em vez de surgir inteira e fraca)
        alfa = (f"({_n(mv.alfa)} * min(1, 1.6 * {f}) * (1 + "
                f"{_seno(mv.respira, mv.respira_periodo * desvio, 0.4 + 2.3 * i, t)})"
                f" + {_n(c.surto_alfa)} * {k} * {f})"
                f" * ({_n(self.virada_fundo)} + {_n(1 - self.virada_fundo)} * "
                f"ifelse({v} > 0.6, ({v} - 0.6) / 0.4, (0.6 - {v}) / 0.6))")
        if c.esconde:
            alfa += f" * (1 - map({self.m(f'h{i}')}))"
        if c.presa_ao_chao:  # fica no chão quando o lutador pula (a de plano "chao" também some com a altura)
            # A camada de chão NÃO é presa ao lutador (bindtime 0 no Explod E no ModifyExplod: o postype = p1 do
            # ModifyExplod volta a prender se o bindtime = 0 não vier junto; visto no filme). O ModifyExplod a põe na
            # posição do lutador no momento em que o -4 roda, já descontada a altura, e ela fica lá quando o motor
            # anda o lutador no resto do tick. Presa, com `Pos Y + Vel Y`, ela subia junto no tick da decolagem: o
            # -4 roda antes do estado que dá a velocidade do pulo, então nem Pos Y nem Vel Y avisam (anel 8,4 px
            # acima do chão num tick, filmes extra de 2026-11-11; solta: desvio 0,00 px no pulo inteiro).
            # Custo: em x ela segue o lutador com 1 tick de atraso (não filmado com o lutador andando).
            py += " - min(0, Pos Y)"
            if c.plano == "chao":
                alfa += " * max(0, 1 + min(0, Pos Y + Vel Y) / 90.0)"
        src = f"floor(255 * min(1, max(0, {alfa})))"
        trans = ["trans = addalpha", f"alpha = {src}, {'255' if c.mistura == 'soma' else f'255 - {src}'}",
                 "ignorehitpause = 1"]
        sempre = [f"[State -4, Aura {self.nome} {c.nome}: move]", "type = ModifyExplod",
                  f"trigger1 = NumExplod({e}) && {v} <= 0.6", f"id = {e}", "postype = p1", f"pos = {px}, {py}",
                  f"scale = {sx}, {sy}"] + (["bindtime = 0"] if c.presa_ao_chao else []) + trans
        virando = [f"[State -4, Aura {self.nome} {c.nome}: apaga para virar]", "type = ModifyExplod",
                   f"trigger1 = NumExplod({e}) && {v} > 0.6", f"id = {e}"] + trans
        # Limite conhecido: a camada presa ao chão (bindtime 0) só anda pelo postype, que este controlador não usa (o
        # postype refaz o lado): nos 5 ticks em que apaga para virar, ela fica onde estava. Com o lutador parado não
        # se vê; com o PosSet do filme (lutador teletransportado) a coluna ficou para trás 5 ticks (2026-11-12).
        # Tentado postype + facing = -1 aqui: no log a camada trocou de lado 0 a 1 tick depois e o P2 ficou com ela
        # do lado errado até o fim (o facing dado fica guardado). Voltou ao de antes.
        return "\n".join(sempre) + "\n\n" + "\n".join(virando) + "\n\n"

    def _prioridade(self, i, c):
        if c.prioridade is not None:
            return c.prioridade
        return {"chao": -9 + i, "tras": -6 + i, "frente": 5 + i}[c.plano]

    def _nascer(self, i, c):
        e = self.id_camada(i)
        n = len(c.quadros)
        # animelemtime: as camadas trocam de quadro em ticks alternados, para todo tick ter desenho novo
        inicio = c.inicio if c.inicio is not None else 1 + (i * max(1, round(n * 0.382))) % n
        return (f"[State -4, Aura {self.nome} {c.nome}: nasce]\ntype = Explod\n"
                f"trigger1 = map({self.m('f')}) > 0 && NumExplod({e}) = 0\n"
                f"anim = {e}\nid = {e}\nanimelem = {inicio}\nanimelemtime = {c.troca(i)}\npostype = p1\n"
                f"pos = {_n(c.pos[0])}, {_n(c.pos[1])}\n"
                f"facing = 1\nbindtime = {0 if c.presa_ao_chao else -1}\nremovetime = -1\n"
                f"sprpriority = {self._prioridade(i, c)}\nownpal = 1\n"
                f"scale = {_n(0.3 / c.res) if c.cresce else _n(1 / c.res)}, {_n(0.08 / c.res) if c.cresce else _n(1 / c.res)}"
                f"\ntrans = addalpha\nalpha = 0, 255\n"
                f"removeongethit = 0\nsupermovetime = -1\npausemovetime = -1\nignorehitpause = 1\n\n")

    def _acaso(self, j, p, canal):
        """0..1 da peça de número map(n): sequência de baixa discrepância (ver PRIMO). Sem Random: o replay sai igual."""
        salto = _SALTOS[(canal + 2 * j) % len(_SALTOS)]
        s = (p.semente * 131 + 17 * j + 61 * canal) % PRIMO
        return f"(floor((map({self.m(f'n{j}')}) + ID * 7) * {salto} + {s}) % {PRIMO}) / {PRIMO - 1}.0"

    def _quando(self, j, p):
        """(gatilho calmo, gatilho do surto) do nascimento, pelo relógio próprio da aura (anda até em pausa)."""
        rapido = max(1, p.periodo // max(1, p.surto_extra))
        s = p.semente + 17 * j
        rel = f"floor(map({self.m('c')}) + ID * 3)"
        return (f"({rel} % {p.periodo}) = {s % p.periodo}",
                f"map({self.m('k')}) > 0.25 && ({rel} % {rapido}) = 0")

    def _emitir(self, j, p):
        e = self.id_particula(j)
        x0, y0, x1, y1 = p.area
        calmo, surto = self._quando(j, p)
        vivo = f"map({self.m('e')}) > 0.3"
        pri = {"chao": -8, "tras": -4 + j % 2}[p.plano]
        return (f"[State -4, Aura {self.nome}: solta {p.nome}]\ntype = Explod\n"
                f"triggerall = {vivo} && NumExplod({e}) < {self.teto_particula(p)}\n"
                f"trigger1 = {calmo}\ntrigger2 = {surto}\n"
                f"anim = {e}\nid = {e}\npostype = p1\n"
                f"pos = {_n(x0)} + {_n(x1 - x0)} * {self._acaso(j, p, 0)}, {_n(y0)} + {_n(y1 - y0)} * {self._acaso(j, p, 1)}\n"
                f"vel = {_n(p.vel[0] - p.vel_var[0] / 2)} + {_n(p.vel_var[0])} * {self._acaso(j, p, 2)}, "
                f"{_n(p.vel[1] - p.vel_var[1] / 2)} + {_n(p.vel_var[1])} * {self._acaso(j, p, 3)}\n"
                f"accel = {_n(p.grav[0])}, {_n(p.grav[1])}\n"
                f"facing = ifelse({self._acaso(j, p, 4)} < 0.5, 1, -1)\nbindtime = 0\nremovetime = {p.vida}\n"
                f"sprpriority = {pri}\nownpal = 1\nremoveongethit = 0\n"
                f"supermovetime = -1\npausemovetime = -1\nignorehitpause = 1\n\n"
                f"[State -4, Aura {self.nome}: conta {p.nome}]\ntype = MapSet\ntriggerall = {vivo}\n"
                f"trigger1 = {calmo}\ntrigger2 = {surto}\nmap = \"{self.m(f'n{j}')}\"\n"
                f"value = floor(map({self.m(f'n{j}')}) + 1) % {PRIMO}\nignorehitpause = 1\n\n")

    def espalhamento(self, j, n=200):
        """As primeiras n posições de nascimento da partícula j, em fração da área: [(x, y)] (a conta do .cns)."""
        p = self.particulas[j]

        def u(canal, k):
            salto = _SALTOS[(canal + 2 * j) % len(_SALTOS)]
            return ((k * salto + (p.semente * 131 + 17 * j + 61 * canal) % PRIMO) % PRIMO) / (PRIMO - 1)

        return [(u(0, k), u(1, k)) for k in range(n)]

    def cns(self, cabecalho=False):
        """Controladores para o [Statedef -4] do lutador (com cabecalho=True, já com a linha [Statedef -4]).

        É -4 e não -2 porque o -2 para quando o lutador está em pausa ou superpausa de outro; o -4 roda sempre
        (inclusive em estado custom, agarrado). A aura não para nunca."""
        f, e, s, k, t, c_, r, v, l = (self.m(x) for x in "fesktcrvl")
        ligada = f"({self.ligada}) && Alive && RoundState > 0"
        todos = self.ids()
        contadores = [self.m(f"n{j}") for j in range(len(self.particulas))]
        contadores += [self.m(f"h{i}") for i, cam in enumerate(self.camadas) if cam.esconde]

        def mapa(nome, titulo, gatilho, valor):
            return (f"[State -4, Aura {self.nome}: {titulo}]\ntype = MapSet\ntrigger1 = {gatilho}\n"
                    f"map = \"{nome}\"\nvalue = {valor}\nignorehitpause = 1\n\n")

        c = [("[Statedef -4]\n\n" if cabecalho else "")
             + f"; ---- Aura animada '{self.nome}' (ferramentas/aura.py): {len(self.camadas)} camadas, "
             f"{len(self.particulas)} partículas, explods {todos[0]} a {todos[-1]}, no máximo {self.pico()} vivos\n"]
        # antes da intro de cada round (RoundState 0) não sobra nada: maps zerados e explods removidos. Na intro, na
        # luta e na pose de vitória (RoundState 1 a 4) a aura segue ligada enquanto `ligada` valer e o lutador viver.
        for nome in [f, e, s, k, t, c_, r, v] + contadores:
            c.append(mapa(nome, f"zera {nome} antes do round", "RoundState = 0", "0"))
        for i in todos:
            c.append(f"[State -4, Aura {self.nome}: limpa {i} antes do round]\ntype = RemoveExplod\n"
                     f"trigger1 = RoundState = 0 && NumExplod({i})\nid = {i}\nignorehitpause = 1\n\n")
        c.append(mapa(t, "tempo volta a zero ao ligar", f"map({f}) <= 0", "0"))
        fade = f"ifelse({ligada}, min(1, map({f}) + {_n(1 / self.entra)}), max(0, map({f}) - {_n(1 / self.sai)}))"
        if self.resta:
            fade = f"min({fade}, max(0, {self.resta}) / {self.sai})"
        c.append(mapa(f, "fade", "RoundState > 0", fade))
        c.append(mapa(e, "fade suave", "1", f"map({f}) * map({f}) * (3 - 2 * map({f}))"))
        # virada: a aura apaga um pouco (5 ticks), troca de lado e volta (7 ticks), em vez de espelhar num tick só
        c.append(mapa(v, "virada passa", f"map({v}) > 0", f"max(0, map({v}) - {_n(1 / 12)})"))
        c.append(mapa(v, "virou", f"map({f}) > 0 && map({l}) != Facing && map({l}) != 0 && map({v}) <= 0", "1"))
        c.append(mapa(l, "guarda o lado", f"map({v}) <= 0 || map({v}) = 1 || map({f}) <= 0", "Facing"))
        # surto: com folga, para especial atrás de especial não deixar a aura em surto o tempo todo
        c.append(mapa(r, "folga do surto anda", f"map({r}) > 0", f"map({r}) - 1"))
        if self.surto:
            c.append(mapa(s, "surto dispara", f"({self.surto}) && map({f}) > 0 && map({r}) <= 0", "1"))
        c.append(mapa(r, "surto abre a folga", f"map({s}) = 1", f"{self.surto_ticks + self.surto_folga}"))
        c.append(mapa(k, "surto sobe e desce macio", "1",
                      f"map({k}) + (ifelse(map({s}) > 0, 1, 0) - map({k})) * 0.14"))
        c.append(mapa(k, "surto acaba em zero exato (escala volta a 1)", f"map({s}) <= 0 && map({k}) < 0.004", "0"))
        c.append(mapa(s, "surto conta", f"map({s}) > 0", f"max(0, map({s}) - {_n(1 / self.surto_ticks)})"))
        c.append(f"[State -4, Aura {self.nome}: tempo anda (mais rápido no surto)]\ntype = MapAdd\n"
                 f"trigger1 = map({f}) > 0\nmap = \"{t}\"\nvalue = 1 + {_n(self.surto_acel)} * map({k})\n"
                 f"ignorehitpause = 1\n\n")
        c.append(f"[State -4, Aura {self.nome}: relógio das partículas]\ntype = MapAdd\n"
                 f"trigger1 = map({f}) > 0\nmap = \"{c_}\"\nvalue = 1\nignorehitpause = 1\n\n")
        for i, cam in enumerate(self.camadas):
            if cam.esconde:
                h = self.m(f"h{i}")
                c.append(mapa(h, f"{cam.nome} apaga enquanto a reação toca", "1",
                              f"map({h}) + (ifelse({cam.esconde}, 1, 0) - map({h})) * 0.3"))
                c.append(mapa(h, f"{cam.nome} volta inteira", f"!({cam.esconde}) && map({h}) < 0.01", "0"))
        for i, cam in enumerate(self.camadas):
            c.append(self._nascer(i, cam))
        for i, cam in enumerate(self.camadas):
            c.append(self._mover(i, cam))
        for i, cam in enumerate(self.camadas):
            n = self.id_camada(i)
            # no surto a animação também corre: um quadro por tick
            c.append(f"[State -4, Aura {self.nome} {cam.nome}: corre no surto]\ntype = ModifyExplod\n"
                     f"trigger1 = NumExplod({n}) && map({k}) > 0.5\nid = {n}\n"
                     f"animelem = ((ExplodVar({n}, 0, animelem) - {1 if cam.troca(i) == cam.tempo - 1 else 0}) "
                     f"% {len(cam.quadros)}) + 1\nanimelemtime = {cam.troca(i)}\nignorehitpause = 1\n\n")
            c.append(f"[State -4, Aura {self.nome} {cam.nome}: some]\ntype = RemoveExplod\n"
                     f"trigger1 = map({f}) <= 0 && NumExplod({n})\nid = {n}\nignorehitpause = 1\n\n")
        for j, p in enumerate(self.particulas):
            c.append(self._emitir(j, p))
        return "".join(c)

    def disparo_surto(self, gatilho="Time = 0", estado=""):
        """Controlador para pôr DENTRO do estado de um especial: dispara o surto da aura (respeita a folga)."""
        return (f"[State {estado}, Aura {self.nome}: surto]\ntype = MapSet\n"
                f"trigger1 = ({gatilho}) && map({self.m('r')}) <= 0\n"
                f"map = \"{self.m('s')}\"\nvalue = 1\nignorehitpause = 1\n\n")

    def resumo(self):
        linhas = [f"aura {self.nome}: altura {self.altura():.0f} px, explods {self.ids()[0]} a {self.ids()[-1]}, "
                  f"no máximo {self.pico()} vivos (teto {self.teto_explods}); por tick, {len(self.camadas)} "
                  f"ModifyExplod ({2 * len(self.camadas)} no surto)"]
        for i, c in enumerate(self.camadas):
            d, fa = self._fases(i, c)
            w, h = self._img(c.quadros[0]).size
            linhas.append(f"  camada {c.nome} ({c.plano}): {len(c.quadros)} quadros x {c.tempo} ticks, {w}x{h} px, "
                          f"deriva a cada {c.mov.deriva_periodo * d:.0f} ticks, fase {fa:.0f}")
        for j, p in enumerate(self.particulas):
            passo = np.abs(np.diff(np.array(self.espalhamento(j)), axis=0))
            passo = np.minimum(passo, 1 - passo)
            linhas.append(f"  partícula {p.nome}: 1 a cada {p.periodo} ticks, vive {p.vida}, {len(self._vidas[j])} quadros "
                          f"assados, até {self.teto_particula(p)} vivas; entre peças seguidas o nascimento anda no "
                          f"mínimo {passo[:, 0].min() * 100:.0f}% da área em x e {passo[:, 1].min() * 100:.0f}% em y")
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
