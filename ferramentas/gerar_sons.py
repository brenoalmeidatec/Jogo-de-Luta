"""Sons próprios do Nazafights: sintetiza tudo por código (numpy) e monta os .snd que o IKEMEN GO lê.

Uso:  python ferramentas/gerar_sons.py               gera os .snd e liga os sons nos lutadores (idempotente)
      python ferramentas/gerar_sons.py --wav PASTA   também solta cada som em .wav para ouvir
      python ferramentas/gerar_sons.py --narrador    refaz as falas do narrador com o Piper (pip install piper-tts)
      python ferramentas/gerar_sons.py --medir       mede volume (LUFS) e pico de cada som contra as músicas

Missão 2026-11-14, item 2 (pedido do Breno): sons novos para golpes, defesa, agarrão, queda, especiais, supers,
transformação, parry, menu, contagem do round e KO; cada lutador com o seu som; nada copiado de outro jogo; volume
parelho com as músicas (que estão em -14 LUFS).

Onde cada som mora (tabela completa em docs/sons.md):
  motif/nazafight/common.snd  sons "F" (de todo lutador): 5 acerto, 6 defesa, 7 queda, 20 super, 30 parry,
                              31 transformação, 35 agarrão, 36 projétil, 40 vento do golpe
  motif/nazafight/fight.snd   narrador (0 round, 1 luta, 2 KO/vitória) e 21 nível da barra de poder
  motif/nazafight/system.snd  menu (100,0 mover, 100,1 confirmar, 100,2 voltar) e 900 contagem do continue
  chars/<lutador>/<lutador>.snd  51 soco, 52 chute, 53 golpe endiabrado e 50 a assinatura do lutador

Tudo é síntese (osciladores, ruído filtrado, envelope), com um pouco de "8-bit" (bitcrush) para casar com a trilha.
As falas do narrador são do Piper TTS com a voz pt_BR "cadu" (dados CC0), tratadas aqui e guardadas em sons/narrador/.
"""
import argparse
import re
import struct
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
SR = 44100
MOTIF = RAIZ / "motif" / "nazafight"
NARRADOR = RAIZ / "sons" / "narrador"
LUTADORES = ("pengaro", "ck", "gutto", "hazaki", "raiclaven")
ALVO_MUSICA = -14.0  # LUFS integrado das músicas (medido com ffmpeg ebur128)


# ---------------------------------------------------------------- blocos de síntese

def _n(d):
    return max(1, int(round(d * SR)))


def tempo(d):
    return np.arange(_n(d)) / SR


def ruido(d, semente, cor=0.0):
    """Ruído branco (cor=0), rosa (cor=1) ou marrom (cor=2), pelo espectro."""
    r = np.random.default_rng(semente)
    x = r.standard_normal(_n(d))
    if cor:
        X = np.fft.rfft(x)
        f = np.fft.rfftfreq(len(x), 1 / SR)
        f[0] = f[1] if len(f) > 1 else 1
        X /= f ** (cor / 2)
        x = np.fft.irfft(X, len(x))
    return x / (np.abs(x).max() + 1e-9)


def filtro(x, baixo=None, alto=None, ordem=2, ganho_pico=None):
    """Passa-banda pelo FFT (curva de Butterworth). baixo = corta abaixo, alto = corta acima."""
    if len(x) < 4:
        return x
    pad = len(x) + _n(0.05)
    X = np.fft.rfft(x, pad)
    f = np.fft.rfftfreq(pad, 1 / SR) + 1e-6
    H = np.ones_like(f)
    if alto:
        H *= 1 / np.sqrt(1 + (f / alto) ** (2 * ordem))
    if baixo:
        H *= 1 / np.sqrt(1 + (baixo / f) ** (2 * ordem))
    if ganho_pico:  # (freq, q, ganho): sino ressonante
        fc, q, g = ganho_pico
        H *= 1 + g * np.exp(-0.5 * ((f - fc) / (fc / q)) ** 2)
    return np.fft.irfft(X * H, pad)[:len(x)]


def env(d, ataque=0.002, queda=0.1, sustentar=0.0, curva=1.0):
    """Envelope: sobe em `ataque`, cai exponencial com constante `queda` (e pode segurar `sustentar` antes)."""
    t = tempo(d)
    e = np.exp(-np.maximum(t - ataque - sustentar, 0) / queda)
    if ataque > 0:
        e *= np.clip(t / ataque, 0, 1) ** curva
    # fecha suave nos últimos 5 ms para não estalar
    k = min(len(t), _n(0.005))
    e[-k:] *= np.linspace(1, 0, k)
    return e


def tom(d, f0, f1=None, forma="seno", curva="exp", vibrato=(0, 0), fase=0.0):
    """Oscilador com glissando de f0 a f1 (exp ou linear) e vibrato (Hz, profundidade em semitons)."""
    t = tempo(d)
    f1 = f0 if f1 is None else f1
    if curva == "exp":
        f = f0 * (f1 / f0) ** (t / max(d, 1e-6))
    else:
        f = f0 + (f1 - f0) * t / max(d, 1e-6)
    if vibrato[1]:
        f = f * 2 ** (vibrato[1] / 12 * np.sin(2 * np.pi * vibrato[0] * t))
    ph = 2 * np.pi * np.cumsum(f) / SR + fase
    if forma == "seno":
        return np.sin(ph)
    if forma == "quadrada":
        return np.sign(np.sin(ph)) * 0.6
    if forma == "pulso":  # pulso 25%, timbre de chip
        return np.where((ph / (2 * np.pi)) % 1 < 0.25, 0.6, -0.6)
    if forma == "triangulo":
        return 2 / np.pi * np.arcsin(np.sin(ph))
    if forma == "serra":
        return 2 * ((ph / (2 * np.pi)) % 1) - 1
    raise ValueError(forma)


def crush(x, bits=8, divide=1):
    """Bitcrush: menos bits e taxa menor (amostra e segura), o tempero 8-bit."""
    if divide > 1:
        x = np.repeat(x[::divide], divide)[:len(x)]
    q = 2 ** (bits - 1)
    return np.round(x * q) / q


def sat(x, drive=2.0):
    return np.tanh(x * drive) / np.tanh(drive)


def reverb(x, cauda=0.4, mistura=0.25, brilho=4000, semente=7):
    """Reverb curto: convolução com ruído que decai (sala pequena de fliperama)."""
    n = _n(cauda)
    ir = ruido(cauda, semente) * np.exp(-tempo(cauda) / (cauda / 5))
    ir = filtro(ir, baixo=200, alto=brilho)
    ir /= np.sqrt((ir ** 2).sum()) + 1e-9
    m = len(x) + n
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)
    seco = np.concatenate([x, np.zeros(n)])
    return seco + mistura * y * 0.6


def mix(*partes):
    """Soma alinhando no começo; cada parte pode ser (sinal, atraso_em_s)."""
    sinais = []
    for p in partes:
        if isinstance(p, tuple):
            s, a = p
            s = np.concatenate([np.zeros(_n(a)), s])
        else:
            s = p
        sinais.append(s)
    n = max(len(s) for s in sinais)
    out = np.zeros(n)
    for s in sinais:
        out[:len(s)] += s
    return out


def junta(*partes, folga=0.0):
    """Um depois do outro."""
    out = []
    for p in partes:
        out += [p, np.zeros(_n(folga))]
    return np.concatenate(out)


def corpo(d, f0, f1, queda, drive=1.5):
    """O 'tum' de um impacto no corpo: seno com queda de pitch rápida, saturado."""
    return sat(tom(d, f0, f1) * env(d, 0.001, queda), drive)


def estalo(d, semente, baixo, alto, queda):
    """O 'tá' de um impacto: ruído filtrado com ataque seco."""
    return filtro(ruido(d, semente), baixo, alto) * env(d, 0.0005, queda)


def vento(d, semente, f0, f1, pico=0.6, largura=1.6):
    """Vento de golpe: ruído passando por uma banda que corre de f0 a f1, crescendo até `pico` (fração de d)."""
    n = _n(d)
    x = ruido(d, semente, cor=0.5)
    out = np.zeros(n)
    passos = 24
    t = np.linspace(0, 1, passos + 1)
    for i in range(passos):
        a, b = int(t[i] * n), int(t[i + 1] * n)
        fc = f0 * (f1 / f0) ** ((t[i] + t[i + 1]) / 2)
        seg = filtro(x, fc / largura, fc * largura)[a:b]
        out[a:b] = seg
    fr = np.linspace(0, 1, n)
    forma = np.where(fr < pico, (fr / pico) ** 2, np.exp(-(fr - pico) / (1 - pico) * 4))
    return out * forma


# ---------------------------------------------------------------- volume

def _kweight(x):
    """Peso K da ITU-R BS.1770 (aproximado: passa-alta 60 Hz + prateleira de +4 dB acima de 1,5 kHz)."""
    pad = len(x)
    X = np.fft.rfft(x, pad)
    f = np.fft.rfftfreq(pad, 1 / SR) + 1e-6
    H = 1 / np.sqrt(1 + (60 / f) ** 4)
    H *= 1 + (10 ** (4 / 20) - 1) / (1 + (1500 / f) ** 2)
    return np.fft.irfft(X * H, pad)


def lufs_max(x):
    """Maior loudness momentânea (janela de 400 ms), em LUFS: é o que o ouvido compara com a música."""
    y = _kweight(x) ** 2
    w = _n(0.4)
    if len(y) < w:
        y = np.concatenate([y, np.zeros(w - len(y))])
    c = np.concatenate([[0], np.cumsum(y)])
    ms = (c[w:] - c[:-w]) / w
    return -0.691 + 10 * np.log10(ms.max() + 1e-12)


def nivelar(x, alvo, pico_db=-1.0):
    """Leva a loudness momentânea máxima a `alvo` LUFS sem passar de `pico_db` (limitador suave)."""
    x = np.asarray(x, float)
    x = x - x.mean()
    for _ in range(3):
        x = x * 10 ** ((alvo - lufs_max(x)) / 20)
        teto = 10 ** (pico_db / 20)
        if np.abs(x).max() > teto:
            x = teto * np.tanh(x / teto)
    # corta a cauda que já não se ouve (abaixo de -60 dBFS): o .snd fica menor
    v = np.flatnonzero(np.abs(x) > 10 ** (-60 / 20))
    if len(v):
        x = x[:v[-1] + 1]
    k = min(len(x), _n(0.004))
    x[-k:] *= np.linspace(1, 0, k)
    return x


# ---------------------------------------------------------------- os sons

def acerto(peso, semente, tipo="soco"):
    """peso 0 fraco, 1 médio, 2 forte, 3 fim de corrente, 4 fim de super. tipo soco/chute/luva/sombra."""
    d = (0.16, 0.22, 0.32, 0.55, 0.95)[peso]
    f0 = {"soco": 190, "chute": 150, "luva": 210, "sombra": 120, "concreto": 170}[tipo] * (1 - 0.1 * peso)
    tum = corpo(d, f0, f0 * 0.35, (0.03, 0.045, 0.07, 0.11, 0.18)[peso], 1.6 + 0.5 * peso)
    if tipo == "chute":  # canela: estalo mais grave e "chicote" de pano
        ta = estalo(d, semente, 500, 3500, 0.02 + 0.006 * peso)
        chicote = estalo(0.05, semente + 1, 2500, 9000, 0.008) * 0.5
        s = mix(tum, ta * 0.9, chicote)
    elif tipo == "luva":  # couro: tapa abafado
        ta = estalo(d, semente, 400, 2500, 0.015 + 0.005 * peso)
        s = mix(tum * 1.2, ta * 0.8)
    elif tipo == "sombra":  # endiabrado: grave rasgado com cauda escura
        ta = estalo(d, semente, 300, 2500, 0.03 + 0.01 * peso)
        rugido = filtro(ruido(d, semente + 9, 1.5), 40, 500) * env(d, 0.01, 0.08 + 0.03 * peso)
        s = sat(mix(tum * 1.2, ta * 0.7, rugido * 0.8), 2.5)
        s = reverb(s, 0.5, 0.35, 2500)
    elif tipo == "concreto":  # Hazak: pedra que racha
        ta = estalo(d, semente, 800, 6000, 0.02 + 0.006 * peso)
        grao = filtro(ruido(d, semente + 3), 1500, 8000) * env(d, 0.001, 0.05) * \
            (np.random.default_rng(semente).random(_n(d)) < 0.08)
        s = mix(tum, ta * 0.8, grao * 0.6)
    else:  # soco: estalo médio-agudo
        ta = estalo(d, semente, 900, 5000, 0.012 + 0.006 * peso)
        s = mix(tum, ta * (0.9 - 0.08 * peso))
    if peso >= 2:  # forte: estrondo grave e um tico de 8-bit
        boom = corpo(d, 70, 38, 0.08 + 0.05 * peso, 2.0) * 0.8
        s = mix(s, boom)
        s = 0.7 * s + 0.3 * crush(s / (np.abs(s).max() + 1e-9), 6, 3) * np.abs(s).max()
    if peso >= 3:
        s = reverb(s, 0.3 + 0.2 * (peso - 3), 0.3)
    if peso == 4:  # fim de super: estouro com brilho de chip descendo
        brilho = tom(0.6, 1800, 220, "pulso") * env(0.6, 0.002, 0.15) * 0.25
        s = mix(s, crush(brilho, 5, 2))
    return s


def defesa(forte=False, semente=40):
    """Defesa: 'tock' de braço na guarda, abafado, sem o grave do acerto."""
    d = 0.18 if forte else 0.13
    a = estalo(d, semente, 700, 2600, 0.018 if forte else 0.012)
    b = sum(tom(d, f) * env(d, 0.001, 0.025) * g for f, g in ((520, 1), (870, 0.5), (1430, 0.3)))
    s = mix(a, b * 0.5, corpo(d, 230, 160, 0.02, 1.2) * 0.4)
    if forte:
        s = mix(s, reverb(crush(s, 7, 2), 0.2, 0.3) * 0.5)
    return s


def queda(peso, semente=60):
    """Corpo batendo no chão: thud grave + poeira (ruído rosa) + quique."""
    d = (0.25, 0.4, 0.6)[peso]
    thud = corpo(d, 110 - 15 * peso, 45, 0.05 + 0.03 * peso, 1.8)
    poeira = filtro(ruido(d, semente, 1), 150, 2500) * env(d, 0.004, 0.06 + 0.04 * peso)
    s = mix(thud, poeira * 0.6)
    if peso >= 1:
        s = mix(s, (mix(corpo(0.15, 90, 50, 0.03), filtro(ruido(0.15, semente + 1, 1), 200, 2000) *
                        env(0.15, 0.002, 0.03) * 0.5) * 0.4, 0.12 + 0.05 * peso))
    if peso == 2:
        s = reverb(s, 0.35, 0.25, 2500)
    return s


def super_flash(semente=80):
    """Início de super (SuperPause): clarão subindo com arpejo de chip e um 'chuum' de energia."""
    d = 0.75
    notas = [0, 4, 7, 12, 16, 19, 24]
    arpejo = np.concatenate([tom(0.045, 330 * 2 ** (n / 12), forma="pulso") * env(0.045, 0.001, 0.03)
                             for n in notas])
    sobe = vento(d, semente, 300, 6000, 0.5, 1.4)
    brilho = sum(tom(d, f, f * 1.5) * env(d, 0.25, 0.15) for f in (880, 1320, 1760)) / 3
    s = mix(sobe * 0.8, (crush(arpejo, 5, 2) * 0.55, 0.05), brilho * 0.35, corpo(d, 120, 40, 0.15) * 0.6)
    return reverb(s, 0.5, 0.3)


def whoosh(peso, chute=False, semente=100):
    """Vento do golpe: fraco é curtinho e agudo, forte é longo e grave. Chute desce mais."""
    d = (0.11, 0.2)[peso] + (0.04 if chute else 0)
    f0, f1 = ((2600, 4200), (1300, 2600))[peso]
    if chute:
        f0, f1 = f0 * 0.7, f1 * 0.7
    return vento(d, semente, f0, f1, 0.65, 1.3 + 0.3 * peso)


def whoosh_especial(semente=110):
    d = 0.32
    return mix(vento(d, semente, 600, 2600, 0.55, 1.8), tom(d, 180, 90, "triangulo") * env(d, 0.12, 0.08) * 0.25)


def parry(endiabrado=False, semente=120):
    """Parry: 'tsching' metálico brilhante com um eco subindo (base) ou o mesmo rasgado e grave (endiabrado)."""
    d = 0.6
    parciais = ((1760, 1), (2640, 0.6), (3960, 0.4), (5280, 0.25), (2217, 0.3))
    sino = sum(tom(d, f * (0.5 if endiabrado else 1)) * env(d, 0.001, 0.12 + 0.05 * i) * g
               for i, (f, g) in enumerate(parciais))
    raspa = estalo(d, semente, 3000, 12000, 0.015)
    sobe = tom(0.12, 880, 1760, "pulso") * env(0.12, 0.001, 0.05)
    s = mix(sino * 0.6, raspa * 0.8, (crush(sobe, 5, 2) * 0.35, 0.03))
    if endiabrado:
        s = sat(mix(s, corpo(d, 140, 50, 0.1) * 0.8, filtro(ruido(d, semente + 2, 1.5), 40, 400) *
                    env(d, 0.01, 0.15) * 0.8), 3)
        s = reverb(s, 0.7, 0.45, 2000)
    else:
        s = reverb(s, 0.4, 0.25, 6000)
    return s


def transformacao(semente=130):
    """Transformação (Despertar), parte 1: o poder carregando, grave subindo com rosnado."""
    d = 1.2
    ronco = filtro(ruido(d, semente, 2), 30, 400) * env(d, 0.6, 0.4)
    sobe = tom(d, 45, 140, "serra", vibrato=(7, 0.6)) * env(d, 0.8, 0.3)
    sobe = filtro(sobe, None, 900)
    vento_ = vento(d, semente + 1, 200, 3000, 0.85, 1.5)
    return sat(mix(ronco * 0.9, sobe * 0.7, vento_ * 0.5), 2.2)


def explosao_poder(semente=140):
    """Transformação, parte 2: estouro de poder (quando ele vira endiabrado)."""
    d = 1.4
    boom = corpo(d, 90, 28, 0.35, 3)
    rasgo = filtro(ruido(d, semente, 1), 100, 6000) * env(d, 0.002, 0.25)
    coro = sum(tom(d, f, f * 0.94, "serra", vibrato=(5, 0.15)) for f in (110, 131, 165)) / 3
    coro = filtro(coro, 80, 1500) * env(d, 0.05, 0.5)
    s = sat(mix(boom, rasgo * 0.7, coro * 0.45), 2)
    return reverb(s, 0.9, 0.4, 3000)


def agarra(semente=150):
    """Agarrão: pano agarrado (dois puxões de ruído) e um tranco abafado."""
    d = 0.28
    pano1 = filtro(ruido(0.07, semente, 0.5), 1500, 7000) * env(0.07, 0.002, 0.02)
    pano2 = filtro(ruido(0.09, semente + 1, 0.5), 1200, 6000) * env(0.09, 0.002, 0.03)
    tranco = corpo(d, 160, 80, 0.035, 1.5)
    return mix(pano1 * 0.8, (pano2 * 0.7, 0.06), (tranco * 0.9, 0.05))


def arremesso(semente=160):
    return mix(vento(0.45, semente, 400, 1800, 0.6, 1.8), corpo(0.45, 90, 50, 0.1) * 0.2)


def escape(semente=170):
    """Escapou do agarrão: puxão de pano e um 'fup' de ar."""
    return mix(filtro(ruido(0.12, semente, 0.5), 1500, 7000) * env(0.12, 0.002, 0.03),
               (vento(0.18, semente + 1, 3000, 1200, 0.3, 1.5) * 0.7, 0.03))


def projetil(semente=180):
    """Projétil saindo: 'fiu' de chip descendo com sopro."""
    d = 0.25
    chip = crush(tom(d, 1400, 500, "quadrada") * env(d, 0.002, 0.08), 5, 2)
    return mix(chip * 0.45, vento(d, semente, 2500, 900, 0.3, 1.4) * 0.7)


# sons de assinatura (grupo 50 do .snd do lutador)

def garrafa_tim(semente=200):
    """Garrafa de vidro batendo: 'tim' com parciais de vidro (não harmônicas) e o baque."""
    d = 0.5
    vidro = sum(tom(d, f) * env(d, 0.0005, q) * g for f, q, g in
                ((1180, 0.18, 1), (2950, 0.10, 0.6), (4870, 0.07, 0.4), (6900, 0.05, 0.25)))
    return mix(vidro * 0.5, acerto(1, semente) * 0.8)


def vidro_quebra(semente=210, d=0.9):
    """Vidro quebrando: estalo, cacos tilintando (grãos agudos aleatórios) e a chuva de cacos."""
    r = np.random.default_rng(semente)
    s = estalo(d, semente, 2000, 14000, 0.03) * 1.0
    for i in range(38):
        t0 = 0.005 + r.exponential(0.12)
        if t0 > d - 0.1:
            continue
        f = r.uniform(2500, 9000)
        g = r.uniform(0.15, 0.5) * np.exp(-t0 * 3)
        caco = tom(0.08, f) * env(0.08, 0.0003, r.uniform(0.008, 0.025)) * g
        s = mix(s, (caco, t0))
    s = mix(s, corpo(d, 200, 90, 0.02) * 0.5)
    return reverb(s[:_n(d)], 0.3, 0.2, 9000)


def gole(semente=220):
    """Gole de bebida: três 'glug' (bolhas com pitch subindo)."""
    s = np.zeros(1)
    for i in range(3):
        d = 0.13
        bolha = tom(d, 180 + 25 * i, 420 + 30 * i) * env(d, 0.004, 0.035)
        bolha = filtro(bolha, 120, 1800)
        s = mix(s, (bolha, 0.19 * i))
    return s


def bone(semente=230):
    """Boné voador: 'vuvuvu' girando (vento com tremolo)."""
    d = 0.5
    t = tempo(d)
    return vento(d, semente, 900, 1500, 0.3, 1.6) * (0.55 + 0.45 * np.sin(2 * np.pi * 14 * t))


def tragada(semente=240):
    """Tragada: chiado de brasa puxando o ar e o sopro da fumaça."""
    d = 0.7
    chiado = filtro(ruido(d, semente), 3000, 11000) * env(d, 0.25, 0.08, 0.1) * 0.5
    sopro = filtro(ruido(d, semente + 1, 1), 300, 2500) * env(d, 0.05, 0.2) * 0.9
    return junta(chiado[:_n(0.4)], sopro[:_n(0.5)])


def grave_paredao(semente=250):
    """Grave do Paredão: sub de caixa de som, três pancadas 'tuuum' com o ar empurrando."""
    s = np.zeros(1)
    for i in range(3):
        b = sat(tom(0.3, 75, 48) * env(0.3, 0.003, 0.12), 3) * (1 - 0.15 * i)
        s = mix(s, (b, 0.11 * i))
    return mix(s, vento(0.6, semente, 200, 900, 0.3, 2) * 0.5)


def beijinho(semente=260):
    """Beijinho do Gutto: estalo de beijo (sucção curtinha) e um brilho de chip."""
    smack = filtro(ruido(0.03, semente), 800, 5000) * env(0.03, 0.0005, 0.006)
    puxa = tom(0.05, 300, 900, "seno") * env(0.05, 0.01, 0.015) * 0.4
    brilho = crush(tom(0.25, 1568, 3136, "pulso") * env(0.25, 0.002, 0.08), 5, 2) * 0.35
    return mix(puxa, (smack, 0.04), (brilho, 0.05))


def joelhada(semente=270):
    """Joelhada de Muay Thai: osso seco no corpo, bem estalado."""
    return mix(acerto(2, semente, "soco"), estalo(0.08, semente + 2, 1800, 8000, 0.006) * 0.9)


def galope(semente=280):
    """Galope do cavalo: quatro cascos (taco de coco) em tercina."""
    s = np.zeros(1)
    for i, t0 in enumerate((0, 0.07, 0.2, 0.27, 0.4, 0.47)):
        c = filtro(ruido(0.06, semente + i), 500, 3000, ganho_pico=(1100, 3, 3)) * env(0.06, 0.0005, 0.012)
        s = mix(s, (c * (1 if i % 2 == 0 else 0.7), t0))
    return s


def relincho(semente=290):
    """Relincho de chip: pulso com vibrato largo, subindo e descendo (o cavalo do Gutto endiabrado)."""
    d = 0.9
    t = tempo(d)
    f = 700 + 500 * np.sin(np.pi * np.clip(t / 0.35, 0, 1)) - 300 * np.clip((t - 0.35) / 0.55, 0, 1)
    f *= 2 ** (0.5 / 12 * np.sin(2 * np.pi * 22 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.where((ph / (2 * np.pi)) % 1 < 0.3, 0.6, -0.6) * env(d, 0.03, 0.3)
    return reverb(crush(filtro(s, 300, 5000), 6, 2), 0.3, 0.2)


def metal(semente=300, d=0.7, base=620):
    """Metal (Estatueta Dourada, Guarda de Aço): sino inarmônico com ataque seco."""
    parc = ((1, 1), (2.76, 0.6), (5.40, 0.4), (8.93, 0.25), (1.51, 0.3))
    s = sum(tom(d, base * r) * env(d, 0.0005, 0.25 / (1 + i)) * g for i, (r, g) in enumerate(parc))
    return mix(s * 0.5, estalo(d, semente, 2000, 10000, 0.008) * 0.6)


def faixa(semente=310):
    """Faixa (de karatê) estalando no ar como chicote."""
    return mix(vento(0.12, semente, 1500, 4000, 0.8, 1.5) * 0.6,
               (estalo(0.06, semente + 1, 2500, 12000, 0.004), 0.1))


def tesoura(semente=320):
    """Tesoura do Raiclaven: dois 'tchic' metálicos de lâmina."""
    def tchic(s_):
        return mix(estalo(0.06, s_, 3500, 14000, 0.006),
                   sum(tom(0.06, f) * env(0.06, 0.0003, 0.01) for f in (4200, 6100)) * 0.3)
    return mix(tchic(semente), (tchic(semente + 1) * 0.8, 0.09))


def borrifada(semente=330):
    """Borrifador de barbeiro: dois 'pss' de spray."""
    pss = filtro(ruido(0.16, semente), 4000, 14000) * env(0.16, 0.01, 0.05)
    return mix(pss, (pss * 0.8, 0.22))


def cadeira(semente=340):
    """Cadeira giratória: rangido de mola girando (serra filtrada com vibrato)."""
    d = 0.6
    r = tom(d, 520, 760, "serra", vibrato=(9, 1.5)) * env(d, 0.05, 0.25)
    return mix(filtro(r, 400, 3000) * 0.5, vento(d, semente, 700, 1400, 0.5, 1.5) * 0.6)


def possessao(semente=350):
    """Sombras possuindo (Pengaró): sopro escuro com sussurro reverso."""
    d = 1.0
    sus = filtro(ruido(d, semente, 0.5), 1500, 6000) * env(d, 0.7, 0.1) * 0.5
    escuro = filtro(ruido(d, semente + 1, 2), 30, 300) * env(d, 0.3, 0.4)
    return reverb(sat(mix(sus, escuro), 2), 0.8, 0.4, 2500)


# ---------------------------------------------------------------- sons do objeto de cada lutador (issue #46)
# Pedido do Breno (2026-11-14): cada golpe soa com o que o lutador usa nele. Os acertos "com arma" saem de
# acerto_arma(): o corpo do acerto comum (o tum e o estalo, que dizem o peso) mais uma camada do objeto.

def _lamina(d, semente, f=(4200, 6100, 7900), q=0.012):
    """Lâmina de metal: estalo agudo com parciais que tilintam."""
    return mix(estalo(d, semente, 3500, 15000, 0.006),
               sum(tom(d, x) * env(d, 0.0003, q * (1 + 0.4 * i)) for i, x in enumerate(f)) * 0.35)


def tesoura_abre(semente=400, forte=False):
    """Tesoura abrindo: 'shhíng' de metal deslizando no metal (lâmina raspando subindo de tom)."""
    d = 0.22 if forte else 0.15
    raspa = filtro(ruido(d, semente), 3000, 13000, ganho_pico=(6500, 4, 2)) * env(d, 0.03, 0.05)
    canto = tom(d, 3600, 5200) * env(d, 0.02, 0.05) * 0.25
    return mix(raspa * 0.6, canto, vento(d, semente + 1, 1800, 3500, 0.5, 1.4) * (0.6 if forte else 0.4))


def tesoura_corte(semente=410, n=2):
    """Tesoura fechando: 'tchac' seco das lâminas (n cortes seguidos)."""
    s = np.zeros(1)
    for i in range(n):
        s = mix(s, (_lamina(0.07, semente + i) * (1 - 0.15 * i), 0.075 * i))
    return s


def tesoura_helice(semente=420):
    """Tesoura Helicóptero: o braço rodando como hélice, com cortes no ritmo da volta."""
    d = 0.75
    t = tempo(d)
    giro = vento(d, semente, 900, 1600, 0.4, 1.6) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t))
    s = giro * 0.8
    for i in range(4):
        s = mix(s, (_lamina(0.06, semente + 1 + i) * 0.55, 0.06 + 0.17 * i))
    return s


def pente_acerto(peso, semente):
    """Pente de plástico batendo: 'tlac' oco e curto em cima do soco."""
    d = 0.06
    tlac = filtro(ruido(d, semente), 1200, 6000, ganho_pico=(2400, 5, 3)) * env(d, 0.0003, 0.008)
    dentes = sum(tom(d, f) * env(d, 0.0003, 0.006) for f in (1900, 2950)) * 0.2
    return mix(tlac, dentes)


def vassourada(semente=430):
    """Vassoura varrendo: palha arrastando no chão, 'chhh-chhh'."""
    d = 0.45
    t = tempo(d)
    palha = filtro(ruido(d, semente), 2500, 11000) * env(d, 0.05, 0.12) * (0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 4.5 * t)))
    return mix(palha * 0.8, vento(d, semente + 1, 700, 1500, 0.5, 1.6) * 0.5)


def talco(semente=440):
    """Talco: 'puf' de pó (sopro rosa com estalinho de frasco)."""
    d = 0.4
    puf = filtro(ruido(d, semente, 1), 300, 5000) * env(d, 0.004, 0.09)
    frasco = filtro(ruido(0.02, semente + 1), 1500, 6000) * env(0.02, 0.0003, 0.004)
    return mix(frasco * 0.6, (puf, 0.01))


def maquina_zumbido(semente=450):
    """Máquina de cortar cabelo: zumbido elétrico que esquenta (sobe) e chia."""
    d = 1.1
    z = tom(d, 118, 150, "serra", vibrato=(50, 0.15)) + 0.5 * tom(d, 236, 300, "quadrada")
    z = filtro(z, 150, 5000) * env(d, 0.05, 0.6, 0.5)
    chia = filtro(ruido(d, semente), 4000, 12000) * env(d, 0.6, 0.15) * 0.3
    return sat(mix(z * 0.6, chia), 1.8)


def maquina_explode(semente=460):
    """Máquina Explosiva estourando: faísca, estouro e caquinhos de plástico."""
    faisca = filtro(ruido(0.12, semente), 5000, 15000) * env(0.12, 0.001, 0.02)
    boom = mix(acerto(4, semente + 1), corpo(1.0, 80, 30, 0.3, 3))
    return mix(faisca * 0.6, (boom, 0.08), (vidro_quebra(semente + 2, 0.6) * 0.25, 0.1))


def navalha(semente=470):
    """Navalha de Sombra saindo: 'shiiing' longo de lâmina com sopro escuro."""
    d = 0.5
    canto = sum(tom(d, f, f * 1.08) * env(d, 0.005, 0.12) * g for f, g in ((3100, 1), (4700, 0.5), (6900, 0.3)))
    raspa = filtro(ruido(d, semente), 4000, 13000) * env(d, 0.002, 0.04)
    escuro = filtro(ruido(d, semente + 1, 2), 40, 400) * env(d, 0.05, 0.2)
    return mix(canto * 0.4, raspa * 0.6, escuro * 0.6, vento(d, semente + 2, 3500, 1200, 0.3, 1.5) * 0.5)


def toalha(semente=480):
    """Toalha Quente: pano molhado estalando ('flap') e o vapor chiando."""
    flap = mix(filtro(ruido(0.08, semente, 0.5), 600, 5000) * env(0.08, 0.001, 0.02),
               corpo(0.08, 200, 120, 0.015) * 0.4)
    vapor = filtro(ruido(0.5, semente + 1), 5000, 14000) * env(0.5, 0.08, 0.15) * 0.25
    return mix(flap, (vapor, 0.05))


def agua_pia(semente=490):
    """Cabeça na Pia: 'splash' de água com bolhas."""
    d = 0.6
    splash = filtro(ruido(d, semente, 0.5), 400, 9000) * env(d, 0.002, 0.08)
    s = mix(splash * 0.8, corpo(d, 160, 70, 0.03) * 0.6)
    r = np.random.default_rng(semente)
    for i in range(7):
        t0 = 0.08 + r.uniform(0, 0.35)
        f = r.uniform(500, 1300)
        s = mix(s, (tom(0.05, f, f * 1.8) * env(0.05, 0.002, 0.012) * 0.3, t0))
    return s


def garrafa_acerto(peso, semente):
    """Garrafa batendo (sem quebrar): 'tónc' de vidro grosso."""
    d = 0.3 + 0.1 * peso
    vidro = sum(tom(d, f * (1 - 0.04 * peso)) * env(d, 0.0005, q) * g for f, q, g in
                ((980, 0.12, 1), (2470, 0.07, 0.5), (4210, 0.05, 0.3)))
    return vidro * 0.6


def lata_voando(semente=500):
    """Latinha arremessada: lata girando no ar (vento com chacoalho do líquido)."""
    d = 0.4
    t = tempo(d)
    giro = vento(d, semente, 1500, 2600, 0.4, 1.5) * (0.6 + 0.4 * np.sin(2 * np.pi * 16 * t))
    chacoalha = filtro(ruido(d, semente + 1), 800, 4000) * env(d, 0.05, 0.12) * \
        (0.5 + 0.5 * np.sin(2 * np.pi * 8 * t)) * 0.35
    return mix(giro, chacoalha)


def lata_bate(semente=510):
    """Latinha batendo: alumínio amassando ('crónc' metálico fino) e quicando."""
    d = 0.45
    amassa = filtro(ruido(0.09, semente), 1500, 9000, ganho_pico=(3200, 3, 2)) * env(0.09, 0.0005, 0.025)
    oco = metal(semente + 1, 0.3, 1450) * 0.35
    quique = mix(metal(semente + 2, 0.15, 1600) * 0.2, filtro(ruido(0.05, semente + 3), 2000, 8000) *
                 env(0.05, 0.0005, 0.01) * 0.3)
    return mix(amassa, oco, acerto(1, semente + 4) * 0.5, (quique, 0.18), (quique * 0.5, 0.29))[:_n(d)]


def chimpa(semente=520):
    """Mão de Chimpá: 'hu-hu-ha-ha' de chimpanzé em chip (pulso com vibrato subindo)."""
    s = np.zeros(1)
    for i, (f0, f1, dd) in enumerate(((380, 520, 0.09), (420, 600, 0.09), (650, 980, 0.11), (720, 1100, 0.13))):
        v = tom(dd, f0, f1, "pulso", vibrato=(30, 0.4)) * env(dd, 0.01, 0.05)
        v = filtro(v, 250, 4000) + filtro(ruido(dd, semente + i), 1000, 5000) * env(dd, 0.005, 0.03) * 0.3
        s = mix(s, (v, 0.1 * i + 0.02 * max(0, i - 1)))
    return crush(s, 7, 2)


def corrente(semente=530, d=0.55):
    """Corrente: elos de ferro chacoalhando (vários clinques inarmônicos)."""
    r = np.random.default_rng(semente)
    s = np.zeros(_n(d))
    for i in range(14):
        t0 = r.uniform(0, d * 0.6)
        b = r.uniform(900, 1700)
        elo = sum(tom(0.08, b * k) * env(0.08, 0.0003, 0.02 / (1 + j)) for j, k in enumerate((1, 2.7, 4.9)))
        s = mix(s, (elo * r.uniform(0.2, 0.45), t0))
    return mix(s, estalo(d, semente + 1, 2000, 9000, 0.01) * 0.4)[:_n(d)]


def bone_acerto(semente=540):
    """Boné acertando: aba batendo ('tchap' de pano duro) em cima de um acerto médio leve."""
    tchap = filtro(ruido(0.05, semente, 0.5), 900, 6000) * env(0.05, 0.0005, 0.01)
    return mix(acerto(1, semente + 1) * 0.6, tchap)


def caco_acerto(peso, semente):
    """Caco de garrafa cortando (Modo Ratão): raspão de vidro afiado e tilintar."""
    d = 0.2 + 0.08 * peso
    risca = filtro(ruido(d, semente), 3000, 14000) * env(d, 0.002, 0.03 + 0.01 * peso)
    tlin = sum(tom(d, f) * env(d, 0.0005, 0.04) for f in (2950, 4870)) * 0.2
    return mix(risca * 0.6, tlin)


def paredao_batida(semente=550):
    """Paredão tocando: dois compassos de batida grave (bumbo, palma de chip), som original."""
    s = np.zeros(1)
    bpm = 130
    b = 60 / bpm
    for i in range(8):
        if i % 2 == 0:
            s = mix(s, (sat(tom(0.25, 90, 45) * env(0.25, 0.002, 0.09), 2.5), i * b / 2))
        else:
            s = mix(s, (filtro(ruido(0.1, semente + i), 900, 6000) * env(0.1, 0.001, 0.03) * 0.5, i * b / 2))
        if i in (3, 7):
            s = mix(s, (crush(chip_nota(0.12, 196 * (1.5 if i == 7 else 1), "pulso", 0.06), 6, 2) * 0.3, i * b / 2))
    return s


def osso_acerto(peso, semente):
    """Cotovelo e joelho de Muay Thai: estalo seco de osso em cima do acerto."""
    return estalo(0.06, semente, 1800, 8000, 0.005 + 0.002 * peso) * (0.8 + 0.1 * peso)


def canela_acerto(peso, semente):
    """Canela de Muay Thai: 'tchá' largo de tapa (estalo de pele) com chicote."""
    d = 0.1
    tapa = filtro(ruido(d, semente), 700, 7000, ganho_pico=(1800, 2, 1.5)) * env(d, 0.0005, 0.014 + 0.004 * peso)
    return tapa * 0.9


def casco_acerto(peso, semente):
    """Casco de cavalo: 'clóc' de taco de coco bem pesado."""
    d = 0.12
    return filtro(ruido(d, semente), 400, 3000, ganho_pico=(900, 3, 4)) * env(d, 0.0005, 0.015 + 0.004 * peso)


def bufada(semente=560):
    """Bufada de cavalo: sopro forte pelo focinho com vibração dos lábios."""
    d = 0.6
    t = tempo(d)
    sopro = filtro(ruido(d, semente, 1), 200, 4000) * env(d, 0.03, 0.15)
    labio = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 28 * t)) * np.exp(-t / 0.2)
    return sopro * labio


def pedra_sobe(semente=570):
    """Chute no chão levantando a pedra: raspão de terra, estalo de pedra soltando e cascalho."""
    d = 0.4
    raspa = filtro(ruido(0.15, semente, 1), 300, 4000) * env(0.15, 0.005, 0.05)
    solta = acerto(1, semente + 1, "concreto") * 0.7
    r = np.random.default_rng(semente)
    cascalho = np.zeros(_n(d))
    for i in range(12):
        t0 = r.uniform(0.05, 0.3)
        g = filtro(ruido(0.02, semente + 10 + i), 1500, 7000) * env(0.02, 0.0003, 0.004) * r.uniform(0.2, 0.5)
        cascalho = mix(cascalho, (g, t0))
    return mix(raspa, (solta, 0.04), cascalho)


def pedra_voando(semente=580):
    """Pedra saindo: 'vuum' grave e pesado (pedra girando no ar)."""
    d = 0.45
    t = tempo(d)
    return mix(vento(d, semente, 500, 1000, 0.3, 1.8) * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * t)),
               corpo(0.12, 140, 70, 0.03) * 0.4)


def pedra_acerto(peso, semente):
    """Pedra batendo: pancada de rocha que racha, com cascalho espalhando."""
    d = 0.25
    racha = estalo(d, semente, 600, 7000, 0.02 + 0.01 * peso)
    r = np.random.default_rng(semente)
    s = racha
    for i in range(6 + 2 * peso):
        s = mix(s, (filtro(ruido(0.02, semente + 20 + i), 1500, 8000) * env(0.02, 0.0003, 0.004) *
                    r.uniform(0.15, 0.4), r.uniform(0.02, 0.2)))
    return s


def ki_carga(semente=590):
    """Carga de ki: zumbido de energia subindo com faíscas de chip (pose de carga, brilho nas mãos)."""
    d = 1.0
    zum = sum(tom(d, f, f * 2.2, "serra", vibrato=(9, 0.3)) for f in (110, 165)) / 2
    zum = filtro(zum, 100, 3000) * env(d, 0.7, 0.15)
    ar = vento(d, semente, 300, 3500, 0.9, 1.4) * 0.6
    r = np.random.default_rng(semente)
    s = mix(zum * 0.6, ar)
    for i in range(8):
        t0 = 0.3 + r.uniform(0, 0.6)
        s = mix(s, (crush(chip_nota(0.04, r.uniform(1500, 3000), "pulso", 0.015), 5, 2) * 0.25, t0))
    return s


def ki_bola(semente=600):
    """Bola de ki saindo: estouro de energia ('vchuuu') com o zumbido indo embora."""
    d = 0.55
    estouro = mix(corpo(d, 180, 60, 0.06, 2), filtro(ruido(d, semente, 0.5), 400, 8000) * env(d, 0.002, 0.06))
    zum = tom(d, 520, 260, "serra", vibrato=(14, 0.4)) * env(d, 0.01, 0.2)
    zum = filtro(zum, 200, 4000)
    return mix(estouro * 0.8, zum * 0.45, vento(d, semente + 1, 3000, 800, 0.2, 1.5) * 0.6)


def ki_acerto(peso, semente):
    """Ki acertando: estalo elétrico e um 'zap' descendo."""
    d = 0.25
    zap = crush(tom(d, 2400, 300, "quadrada") * env(d, 0.001, 0.05), 5, 2) * 0.3
    return mix(estalo(d, semente, 2000, 12000, 0.015) * 0.6, zap)


def ki_trevas(semente=610):
    """Rajadona de ki das trevas (Diabo Loiro): carga curta e um raio contínuo, grave, rasgado e sinistro."""
    d = 2.4
    t = tempo(d)
    carga = ki_carga(semente)[:_n(0.6)] * np.linspace(0.6, 1, _n(0.6))
    raio = sat(filtro(ruido(d, semente + 1, 1.2), 60, 3500) * (0.8 + 0.2 * np.sin(2 * np.pi * 7 * t)), 2.5)
    coro = sum(tom(d, f, f * 0.97, "serra", vibrato=(6, 0.25)) for f in (55, 82, 98, 147)) / 4
    coro = filtro(coro, 40, 1800)
    crepita = filtro(ruido(d, semente + 2), 3000, 12000) * (np.random.default_rng(semente).random(_n(d)) < 0.02) * 2
    corpo_raio = mix(raio * 0.6, coro * 0.7, crepita * 0.3) * env(d, 0.05, 0.5, 1.5)
    s = mix(carga, (corpo_raio, 0.5), (corpo(1.0, 90, 30, 0.3, 3) * 0.8, 0.5))
    return reverb(s, 0.8, 0.35, 2500)


def maleta_acerto(peso, semente):
    """Maletada do Diabo Loiro: couro duro batendo e o fecho de metal tilintando."""
    d = 0.2
    couro = filtro(ruido(d, semente, 0.5), 300, 3000) * env(d, 0.0005, 0.02 + 0.005 * peso)
    fecho = metal(semente + 1, 0.15, 1900) * 0.25
    return mix(couro, fecho)


def trevas_acerto(peso, semente):
    """Acerto do Diabo Loiro: brasa estalando (fogo e ouro) por cima do grave escuro."""
    d = 0.3
    brasa = filtro(ruido(d, semente), 1500, 9000) * env(d, 0.002, 0.05) * \
        (np.random.default_rng(semente).random(_n(d)) < 0.15)
    return brasa * 1.5


ARMAS = {  # tipo do acerto com objeto: (acerto base por baixo, camada do objeto, ganho da camada)
    "tesoura": ("soco", lambda p, s: tesoura_corte(s, 1 + (p >= 2)), 1.0),
    "pente": ("soco", pente_acerto, 0.8),
    "garrafa": ("soco", garrafa_acerto, 0.9),
    "osso": ("soco", osso_acerto, 1.0),
    "canela": ("chute", canela_acerto, 1.0),
    "casco": ("sombra", casco_acerto, 1.0),
    "corrente": ("sombra", lambda p, s: corrente(s, 0.3 + 0.08 * p) * 0.8, 1.0),
    "caco": ("sombra", caco_acerto, 1.0),
    "serra": ("sombra", lambda p, s: mix(tesoura_corte(s, 2), filtro(ruido(0.25, s + 5), 2000, 9000) *
                                          env(0.25, 0.002, 0.06) * 0.4), 1.0),
    "pedra": ("concreto", pedra_acerto, 0.9),
    "ki": ("soco", ki_acerto, 1.0),
    "trevas": ("sombra", trevas_acerto, 1.0),
    "maleta": ("luva", maleta_acerto, 1.0),
}


def acerto_arma(peso, semente, tipo):
    base, camada, g = ARMAS[tipo]
    return mix(acerto(peso, semente, base), camada(peso, semente + 50) * g)


# ---------------------------------------------------------------- menu e barra

def chip_nota(d, f, forma="pulso", queda=0.05):
    return tom(d, f, forma=forma) * env(d, 0.001, queda)


def menu_mover():
    return crush(chip_nota(0.05, 1046, "pulso", 0.02), 6, 2)


def menu_confirmar():
    s = junta(chip_nota(0.06, 784, "quadrada", 0.04), chip_nota(0.06, 1046, "quadrada", 0.04),
              chip_nota(0.18, 1568, "quadrada", 0.08))
    return mix(crush(s, 6, 2), acerto(0, 900) * 0.25)


def menu_voltar():
    return crush(junta(chip_nota(0.06, 784, "quadrada", 0.04), chip_nota(0.14, 523, "quadrada", 0.06)), 6, 2)


def nivel_barra(maximo=False):
    notas = [0, 7, 12] + ([16, 19, 24] if maximo else [])
    s = np.concatenate([chip_nota(0.05, 523 * 2 ** (n / 12), "pulso", 0.04) for n in notas])
    s = mix(crush(s, 6, 2), (chip_nota(0.4 if maximo else 0.25, 523 * 2 ** ((notas[-1] + 12) / 12), "triangulo",
                                       0.12) * 0.5, len(notas) * 0.05))
    return reverb(s, 0.3, 0.2)


# ---------------------------------------------------------------- narrador

FALAS = {  # (grupo, número) do fight.snd: texto escrito do jeito que a voz pronuncia certo ("ráund", "nocáuti")
    (0, 1): "Primeiro ráund!", (0, 2): "Segundo ráund!", (0, 3): "Terceiro ráund!", (0, 4): "Quarto ráund!",
    (0, 5): "Quinto ráund!", (0, 6): "Sexto ráund!", (0, 7): "Sétimo ráund!", (0, 8): "Oitavo ráund!",
    (0, 9): "Nono ráund!", (0, 10): "Ráund final!", (0, 11): "Ráund único!",
    (1, 0): "Lúta!",
    (2, 0): "No-cáute!", (2, 1): "Nocáuti duplo!", (2, 2): "Acabou o tempo!", (2, 3): "Você venceu!",
    (2, 4): "Você perdeu!", (2, 5): "Empate!", (2, 6): "Perfeito!", (2, 7): "Foi por pouco!",
}
CONTAGEM = ["Zero", "Um", "Dois", "Trêis", "Quatro", "Cínco", "Seis", "Sete", "Oito", "Nove", "Dez"]
VOZ = "pt_BR-cadu-medium"


def ler_wav(p):
    with wave.open(str(p)) as w:
        sr, n, ch, larg = w.getframerate(), w.getnframes(), w.getnchannels(), w.getsampwidth()
        x = np.frombuffer(w.readframes(n), {2: np.int16, 4: np.int32}[larg]).astype(float)
    x = x.reshape(-1, ch).mean(1) / (2 ** (8 * larg - 1))
    if sr != SR:
        x = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x)
    return x


def gravar_wav(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(_pcm16(x))


def _pcm16(x):
    return (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()


def fazer_narrador(pasta_voz):
    """Gera as falas com o Piper (voz pt_BR cadu, CC0) e grava cruas em sons/narrador/ (o tratamento é aqui)."""
    modelo = Path(pasta_voz) / f"{VOZ}.onnx"
    if not modelo.exists():
        sys.exit(f"falta {modelo}: baixe de huggingface.co/rhasspy/piper-voices (pt/pt_BR/cadu/medium)")
    textos = {f"f{g}_{n}": t for (g, n), t in FALAS.items()}
    textos.update({f"c900_{i}": t + "!" for i, t in enumerate(CONTAGEM)})
    for nome, texto in textos.items():
        destino = NARRADOR / f"{nome}.wav"
        destino.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, "-m", "piper", "-m", str(modelo), "-f", str(destino),
                        "--length-scale", "1.1", "--noise-scale", "0.55", "--sentence-silence", "0"],
                       input=texto.encode(), check=True, capture_output=True)
        print("fala", nome, texto)


def tratar_voz(x, grave=1.0):
    """Voz de narrador de fliperama: um tom mais grave, compressão, brilho e um eco de arena."""
    x = x / (np.abs(x).max() + 1e-9)
    # corta o silêncio das pontas
    v = np.flatnonzero(np.abs(x) > 0.02)
    if len(v):
        x = x[max(0, v[0] - _n(0.01)):v[-1] + _n(0.03)]
    # mais grave: reamostra (muda tom e duração juntos, a voz fica mais pesada)
    fator = 2 ** (-grave / 12)
    x = np.interp(np.arange(0, len(x) - 1, fator), np.arange(len(x)), x)
    x = filtro(x, 80, 9000, ganho_pico=(2800, 2, 0.5))
    x = sat(x * 1.3, 1.2)  # compressão por saturação suave (mais que isso a fala embola)
    x = reverb(x, 0.6, 0.18, 6000, semente=99)
    return x


# ---------------------------------------------------------------- arquivo .snd (formato do MUGEN 1.0)

def wav_bytes(x):
    pcm = _pcm16(x)
    return (b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVEfmt " +
            struct.pack("<IHHIIHH", 16, 1, 1, SR, SR * 2, 2, 16) + b"data" + struct.pack("<I", len(pcm)) + pcm)


def gravar_snd(caminho, sons):
    """sons: {(grupo, número): sinal}. Cabeçalho ElecbyteSnd v1.0 + subarquivos encadeados."""
    itens = sorted(sons.items())
    cab = bytearray(512)
    cab[:12] = b"ElecbyteSnd\0"
    struct.pack_into("<HHII", cab, 12, 0, 1, len(itens), 512)
    corpo_ = bytearray()
    pos = 512
    for i, ((g, n), x) in enumerate(itens):
        w = wav_bytes(x)
        prox = pos + 16 + len(w) if i < len(itens) - 1 else 0
        corpo_ += struct.pack("<IIII", prox, len(w), g, n) + w
        pos += 16 + len(w)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(bytes(cab) + bytes(corpo_))


def ler_snd(caminho):
    b = Path(caminho).read_bytes()
    assert b[:12] == b"ElecbyteSnd\0", caminho
    n, pos = struct.unpack_from("<II", b, 16)
    out = {}
    for _ in range(n):
        prox, ln, g, s = struct.unpack_from("<IIII", b, pos)
        out[(g, s)] = b[pos + 16:pos + 16 + ln]
        if not prox:
            break
        pos = prox
    return out


# ---------------------------------------------------------------- o que vai em cada .snd

# Volume (LUFS momentâneo máximo). A música está em -14 integrado: golpe forte chega nela, fraco fica abaixo,
# menu bem abaixo; narrador um pouco acima, como num fliperama.
V_FRACO, V_MEDIO, V_FORTE, V_ENORME = -17.0, -15.5, -13.5, -12.0
V_VENTO, V_MENU, V_VOZ = -21.0, -20.0, -12.0


def sons_comuns():
    s = {}
    for p, v in zip(range(5), (V_FRACO, V_MEDIO, V_FORTE, V_ENORME, V_ENORME)):
        s[(5, p)] = nivelar(acerto(p, 500 + p), v)
    s[(6, 0)] = nivelar(defesa(), V_FRACO)
    s[(6, 1)] = nivelar(defesa(True), V_MEDIO)
    # 7: o common1 do motor toca F7,0 / F7,1 / F7,2 conforme a velocidade da queda
    for p, v in zip(range(3), (V_FRACO, V_MEDIO, V_FORTE)):
        s[(7, p)] = nivelar(queda(p), v)
    s[(20, 0)] = nivelar(super_flash(), V_FORTE)
    s[(30, 0)] = nivelar(parry(), V_MEDIO)
    s[(30, 1)] = nivelar(parry(True), V_FORTE)
    s[(31, 0)] = nivelar(transformacao(), V_FORTE)
    s[(31, 1)] = nivelar(explosao_poder(), V_ENORME)
    s[(35, 0)] = nivelar(agarra(), V_MEDIO)
    s[(35, 1)] = nivelar(arremesso(), V_MEDIO)
    s[(35, 2)] = nivelar(escape(), V_FRACO)
    s[(36, 0)] = nivelar(projetil(), V_MEDIO)
    s[(40, 0)] = nivelar(whoosh(0), V_VENTO)
    s[(40, 1)] = nivelar(whoosh(1), V_VENTO + 2)
    s[(40, 2)] = nivelar(whoosh(0, True), V_VENTO)
    s[(40, 3)] = nivelar(whoosh(1, True), V_VENTO + 2)
    s[(40, 4)] = nivelar(whoosh_especial(), V_VENTO + 3)
    return s


ASSINATURAS = {
    # grupo 50 do .snd de cada lutador: (número, nome, função, volume). 0 a 3 são da missão de 14/11; de 4 em
    # diante, os objetos da issue #46 (o que o lutador usa em cada golpe).
    "pengaro": [(0, "garrafa", garrafa_tim, V_FORTE), (1, "vidro quebrando", vidro_quebra, V_FORTE),
                (2, "gole", gole, V_MEDIO), (3, "possessão", possessao, V_FORTE),
                (4, "latinha voando", lata_voando, V_MEDIO), (5, "latinha batendo", lata_bate, V_FORTE),
                (6, "chimpanzé", chimpa, V_MEDIO), (7, "corrente", corrente, V_MEDIO),
                (8, "garrafa girando no ar", lambda: mix(lata_voando(505) * 0.7, garrafa_acerto(0, 506) * 0.15),
                 V_FRACO)],
    "ck": [(0, "boné voador", bone, V_MEDIO), (1, "tragada", tragada, V_MEDIO),
           (2, "grave do paredão", grave_paredao, V_ENORME), (3, "garrafa voadora quebrando", vidro_quebra, V_FORTE),
           (4, "boné acertando", bone_acerto, V_MEDIO), (5, "paredão tocando", paredao_batida, V_FORTE),
           (6, "garrafa quebrando no chão", lambda: vidro_quebra(215, 1.0), V_FORTE)],
    "gutto": [(0, "beijinho", beijinho, V_MEDIO), (1, "joelhada", joelhada, V_FORTE), (2, "galope", galope, V_MEDIO),
              (3, "relincho", relincho, V_FORTE), (4, "bufada", bufada, V_MEDIO),
              (5, "coice", lambda: mix(acerto_arma(3, 281, "casco"), galope(282)[:_n(0.12)] * 0.6), V_ENORME)],
    "hazaki": [(0, "concreto", lambda: acerto(3, 301, "concreto"), V_FORTE),
               (1, "estatueta dourada", lambda: metal(302, 0.7, 880), V_FORTE),
               (2, "guarda de aço", lambda: metal(303, 0.5, 520), V_FORTE), (3, "faixa", faixa, V_MEDIO),
               (4, "pedra levantando do chão", pedra_sobe, V_MEDIO), (5, "pedra voando", pedra_voando, V_MEDIO),
               (6, "carga de ki", ki_carga, V_MEDIO), (7, "bola de ki", ki_bola, V_FORTE),
               (8, "rajada de ki das trevas", ki_trevas, V_ENORME),
               (9, "pedra batendo", lambda: acerto_arma(3, 304, "pedra"), V_FORTE)],
    "raiclaven": [(0, "tesoura", tesoura, V_MEDIO), (1, "borrifada", borrifada, V_MEDIO),
                  (2, "pente voador", lambda: mix(projetil(321), tesoura(322) * 0.4), V_MEDIO),
                  (3, "cadeira giratória", cadeira, V_MEDIO), (4, "tesoura helicóptero", tesoura_helice, V_MEDIO),
                  (5, "vassoura", vassourada, V_MEDIO), (6, "talco", talco, V_FRACO),
                  (7, "máquina zumbindo", maquina_zumbido, V_MEDIO), (8, "máquina explodindo", maquina_explode,
                                                                        V_ENORME),
                  (9, "navalha de sombra", navalha, V_FORTE), (10, "toalha quente", toalha, V_MEDIO),
                  (11, "cabeça na pia", agua_pia, V_FORTE)],
}

# Timbre dos acertos por lutador: 51 soco (mão), 52 chute, 53 golpe endiabrado, 54 a arma da mão (quando tem).
# Os tipos simples são os do acerto(); os com objeto estão em ARMAS (acerto_arma).
PERFIL = {
    "pengaro": {51: "soco", 52: "chute", 53: "corrente", 54: "garrafa"},
    "ck": {51: "luva", 52: "chute", 53: "caco", 54: "luva"},
    "gutto": {51: "soco", 52: "canela", 53: "casco", 54: "osso"},
    "hazaki": {51: "concreto", 52: "chute", 53: "trevas", 54: "pedra"},
    "raiclaven": {51: "pente", 52: "chute", 53: "serra", 54: "tesoura"},
}
VENTO_ARMA = {"raiclaven": lambda forte: tesoura_abre(400 + forte, forte)}  # 55,0 e 55,1: o "vento" da arma


def sons_lutador(nome, semente):
    s = {}
    perfil = PERFIL[nome]
    vols = (V_FRACO, V_MEDIO, V_FORTE, V_ENORME, V_ENORME)
    for g, tipo in perfil.items():
        for p, v in zip(range(5), vols):
            x = acerto_arma(p, semente + 10 * (g - 51) + p, tipo) if tipo in ARMAS else \
                acerto(p, semente + 10 * (g - 51) + p, tipo)
            s[(g, p)] = nivelar(x, v + (0.5 if g == 53 else 0))
    if nome in VENTO_ARMA:
        s[(55, 0)] = nivelar(VENTO_ARMA[nome](0), V_VENTO + 2)
        s[(55, 1)] = nivelar(VENTO_ARMA[nome](1), V_VENTO + 4)
    for n, _, f, v in ASSINATURAS[nome]:
        s[(50, n)] = nivelar(f(), v)
    return s


def sons_fight():
    s = {}
    for (g, n) in FALAS:
        p = NARRADOR / f"f{g}_{n}.wav"
        if p.exists():
            s[(g, n)] = nivelar(tratar_voz(ler_wav(p)), V_VOZ)
    s[(21, 0)] = nivelar(nivel_barra(), V_MEDIO)
    s[(21, 1)] = nivelar(nivel_barra(True), V_FORTE)
    return s


def sons_sistema():
    s = {(100, 0): nivelar(menu_mover(), V_MENU), (100, 1): nivelar(menu_confirmar(), V_MENU + 2),
         (100, 2): nivelar(menu_voltar(), V_MENU)}
    for i in range(len(CONTAGEM)):
        p = NARRADOR / f"c900_{i}.wav"
        if p.exists():
            s[(900, i)] = nivelar(tratar_voz(ler_wav(p), 1.0), V_VOZ - 2)
    return s


# ---------------------------------------------------------------- ligar nos lutadores (.def e .cns)

MARCA = "; som:"  # tudo que este script põe ou troca no .cns leva esta marca, para poder refazer


def _kicks(cmd):
    """Estados que saem de a/b (chute) e de x/y (soco), lidos do .cmd."""
    chute, soco = set(), set()
    for blk in re.split(r"\n(?=\[State -1)", cmd):
        v = re.search(r"^value\s*=\s*(\d+)\s*$", blk, re.M)
        if not v or not blk.startswith("[State -1"):
            continue
        cm = set(re.findall(r'command\s*=\s*"([^"]+)"', blk))
        n = int(v.group(1))
        if cm & {"a", "b"}:
            chute.add(n)
        if cm & {"x", "y"}:
            soco.add(n)
    return chute - soco, soco


def _do_botao(cmd, letra):
    """Estados (normais e kombos, abaixo de 700) que saem só do botão `letra`, lidos do .cmd."""
    out = set()
    for blk in re.split(r"\n(?=\[State -1)", cmd):
        v = re.search(r"^value\s*=\s*(\d+)\s*$", blk, re.M)
        if not v or not blk.startswith("[State -1") or int(v.group(1)) >= 700:
            continue
        cm = set(re.findall(r'command\s*=\s*"([^"]+)"', blk)) & {"x", "y", "a", "b"}
        if cm == {letra}:
            out.add(int(v.group(1)))
    return out


# especiais: estado -> (acerto, [(gatilho, som do PlaySnd)])
#   acerto: None mantém o de soco/chute; "54" usa o grupo 54 com o peso do golpe; "50,5" fixo; uma lista dá um por
#   hitsound do estado, na ordem (supers com vários acertos).
#   gatilho "proj" = o mesmo gatilho do 1º Projectile/Helper; "T<n>" = Time = n; "vento" troca o vento do golpe.
# Os números de estado são os do molde do Pengaró, que o Gutto e o Raiclaven também usam (nomes no movelist.dat).
CHUTES_ESPECIAIS = {1100, 1101, 1500, 1501, 1701, 3401, 3420, 3421, 3422, 3423, 3432, 3435}
_LATA_E_VIDRO = ["50,5", "54,2", "50,5", "54,2", "50,5", "50,1"]  # Chuva de Bebidas: lata, garrafa ... estoura
ESPECIAIS = {
    "pengaro": {
        1000: ("50,5", [("proj", "50,4")]), 1001: ("50,5", [("proj", "50,4")]),  # Latada: lata voa e bate
        1600: ("50,0", [("proj", "50,8")]), 1601: ("50,0", [("proj", "50,8")]),  # Garrafada em Arco: vidro
        1400: (None, [("T0", "50,6")]), 1401: (None, [("T0", "50,6")]),  # Mão de Chimpá
        3000: (_LATA_E_VIDRO, [("T0", "50,6")]), 3100: (["53,1", "50,1"], [("T0", "50,3")]),
        3200: (None, [("T0", "50,6")]),  # Bando da Várzea: o bando de chimpanzé
        3401: (None, [("T0", "50,7")]), 3400: (None, [("proj", "50,3")]),  # Chute da Corrente, Mão de Sombra
        3402: (None, [("T0", "50,7")]), 3403: (None, [("T0", "50,7")]),
        2000: (None, [("T9", "50,2"), ("T42", "50,1"), ("T55", "50,3"), ("T55", "F31,1")])},
    "ck": {
        1600: ("50,4", [("proj", "50,0")]), 1601: ("50,4", [("proj", "50,0")]),  # Boné Voador
        1000: (None, [("proj", "50,1")]), 1001: (None, [("proj", "50,1")]), 3400: (None, [("proj", "50,1")]),
        3402: ("50,3", [("proj", "F36,0")]), 3403: (None, [("T0", "50,2")]),
        3100: (["53,2", "53,4"], [("T0", "50,5")]),  # Baile da Esquina: o paredão toca e ele corta com o caco
        2000: (None, [("T2", "50,5"), ("T42", "50,6"), ("T55", "F31,1")])},
    "gutto": {
        1000: (None, [("proj", "50,0")]), 1001: (None, [("proj", "50,0")]),
        1600: (None, [("proj", "50,0")]), 1601: (None, [("proj", "50,0")]),
        1200: ("50,1", []), 1201: ("50,1", []),  # Joelhada Voadora
        1400: ("54", []), 1401: ("54", []),  # Cotovelo Giratório
        3000: (None, [("T0", "50,0")]),
        3100: ("53", [("T0", "50,3"), ("T20", "50,2")]),  # Saideira do Cavalo
        3200: ("52", []),  # Bando de Chutes: canela
        3400: (None, [("proj", "50,3")]), 3401: ("50,5", [("T0", "50,4")]),  # Beijo e Coice do Cavalo
        3402: (None, [("T0", "50,2")]), 3403: (None, [("T0", "50,4")]),
        2000: (None, [("T20", "50,4"), ("T55", "F31,1"), ("T60", "50,3")])},
    "hazaki": {
        1000: ("50,9", [("T0", "50,4"), ("proj", "50,5")]), 1001: ("50,9", [("T0", "50,4"), ("proj", "50,5")]),
        1600: ("50,1", [("proj", "F36,0")]), 1601: ("50,1", [("proj", "F36,0")]),
        1100: (None, [("T0", "50,2")]), 1101: (None, [("T0", "50,2")]),
        1200: (None, [("T0", "50,3")]), 1201: (None, [("T0", "50,3")]),
        3000: (None, [("T0", "50,3")])},
    "raiclaven": {
        1000: (None, [("proj", "50,2")]), 1001: (None, [("proj", "50,2")]),  # Pente Voador (acerto de pente)
        1100: ("54", [("T0", "50,4")]), 1101: ("54", [("T0", "50,4")]),  # Tesoura Helicóptero
        1200: ("54", [("vento", "55,1"), ("T0", "50,0")]), 1201: ("54", [("vento", "55,1"), ("T0", "50,0")]),
        1300: (None, [("T0", "50,5")]), 1301: (None, [("T0", "50,5")]),  # Varrida
        1400: ("54", [("vento", "55,1")]), 1401: ("54", [("vento", "55,1")]),  # Tesourão
        1500: (None, [("T0", "50,3")]), 1501: (None, [("T0", "50,3")]),  # Cadeira Giratória
        1600: (None, [("proj", "50,1")]), 1601: (None, [("proj", "50,1")]),  # Borrifada
        1700: (None, [("T0", "50,6")]), 1701: ("51", [("T0", "50,6")]),  # Próximo!: some no talco
        3000: ("54", [("T0", "50,6")]),  # Próximo, Cliente!: 8 cortes
        3100: ("53", [("T0", "50,4")]),  # Último Cliente
        3200: (["54,1", "54,1", "50,8"], [("T0", "50,7")]),  # Máquina Explosiva: zumbe, esquenta e explode
        3400: (None, [("proj", "50,9")]), 3401: ("53", [("vento", "55,1")]),  # Navalha, Corte da Corrente
        3402: (None, [("T0", "50,3")]), 3403: (None, [("T0", "50,3")]),  # Cadeira Atravessada, Queda da Cadeira
        2000: (None, [("T30", "50,4"), ("T55", "F31,1")])},
}

# botão da mão que segura a arma: normais (200 a 699) e kombos que saem dele usam o acerto 54 e o vento 55
BOTAO_ARMA = {"raiclaven": "y", "gutto": "y"}  # Raiclaven: y é a tesoura; Gutto: y é cotovelo e joelhada

# agarrões: estado -> grupo de cada PlaySnd de pancada (os "F5,k" do agarrao_mk e da frente de agarrões), em ordem
AGARROES = {
    "pengaro": {810: ["52", "54", "52", "54"], 831: ["51", "54"], 841: ["51"]},  # roda de capoeira com garrafa
    "ck": {810: ["51", "51", "51", "52", "51"], 831: ["51", "52"], 841: ["52"]},  # boxe sujo de luva
    "gutto": {810: ["54", "54", "54", "52"], 831: ["54", "50,1"], 841: ["54"]},  # clinch: joelhadas
    "hazaki": {810: ["51", "51", "54", "52", "52"], 831: ["51", "51", "51", "51"], 841: ["52"]},
    "raiclaven": {810: ["54", "54", "54", "52"], 831: ["50,10", "51"], 841: ["50,11"]},  # corte à força, toalha, pia
}


_PARRY = [("trigger1 = Time = 0\ntrigger1 = var(20) <= 0", "F30,0"), ("trigger1 = Time = 0\ntrigger1 = var(20) > 0", "F30,1")]
COMUNS = {  # estado -> [(gatilho, som)] para todo lutador
    761: _PARRY, 765: _PARRY,  # parry em cima / embaixo acertou (docs/parry.md): base brilhante, endiabrado rasgado
    810: [("trigger1 = Time = 0", "F35,0")], 831: [("trigger1 = Time = 0", "F35,0")],  # agarrão pegou
    841: [("trigger1 = Time = 0", "F35,0")],
}


def _desfazer(cns):
    cns = re.sub(r"^\[State -?\d+, som[^\]]*\]\n(?:(?!\n\[)[^\n]*\n)*?" + re.escape(MARCA) + r" fim\n\n", "", cns,
                 flags=re.M)
    cns = re.sub(r"^((?:hit|guard)sound|sound|value) = [^\n;]*" + re.escape(MARCA) + r"(F?\d+,\s*\d+)$", r"\1 = \2", cns,
                 flags=re.M)
    return cns


def _playsnd(estado, nome, gatilho, valor):
    return (f"[State {estado}, som {nome}]\ntype = PlaySnd\n{gatilho}\nvalue = {valor}\n{MARCA} fim\n\n")


def ligar(nome, pasta=None):
    """Põe `sound = <nome>.snd` no .def e liga os sons no .cns: chute com acerto de chute, a arma no botão dela,
    vento no começo de cada golpe, os objetos nos especiais, supers e agarrões (issue #46), transformação no
    Despertar. Pode rodar de novo (desfaz e refaz)."""
    pasta = Path(pasta or RAIZ / "chars" / nome)
    d = pasta / f"{nome}.def"
    txt = d.read_text(encoding="utf-8")
    if not re.search(r"^sound\s*=", txt, re.M):
        txt = re.sub(r"^(anim\s*=.*)$", rf"\1\nsound = {nome}.snd", txt, count=1, flags=re.M)
        d.write_text(txt, encoding="utf-8", newline="\n")
    c = pasta / f"{nome}.cns"
    cns = _desfazer(c.read_text(encoding="utf-8").replace("\r\n", "\n"))
    cmd = (pasta / f"{nome}.cmd").read_text(encoding="utf-8").replace("\r\n", "\n")
    chutes, socos = _kicks(cmd)
    chutes |= CHUTES_ESPECIAIS
    arma = _do_botao(cmd, BOTAO_ARMA[nome]) if nome in BOTAO_ARMA else set()
    vento_arma = nome in VENTO_ARMA
    esp = ESPECIAIS.get(nome, {})
    agarroes = AGARROES.get(nome, {})
    partes = re.split(r"(?m)^(?=\[Statedef )", cns)
    out = []
    for p in partes:
        m = re.match(r"\[Statedef (-?\d+)", p)
        if not m:
            out.append(p)
            continue
        n = int(m.group(1))
        grupo_hit, extras = esp.get(n, (None, []))
        if n not in esp and n in arma:
            grupo_hit = "54"
        tem_hit = re.search(r"^hitsound = F5,\s*(\d)", p, re.M)
        endiabrado = 3400 <= n < 3500 or 10000 <= n < 20000
        conta = [0]

        def troca(mm):
            k = int(mm.group(2))
            g = grupo_hit[min(conta[0], len(grupo_hit) - 1)] if isinstance(grupo_hit, list) else grupo_hit
            conta[0] += 1
            if g:
                novo = g if "," in g else f"{g},{k}"
            elif endiabrado:
                novo = f"53,{k}"
            elif n in chutes:
                novo = f"52,{k}"
            else:
                novo = f"51,{k}"
            # "S" na frente: sem prefixo o hitsound toca do common.snd (regra do MUGEN/IKEMEN), que não tem os
            # grupos 50 a 55, e o acerto ficava mudo (achado na revisão geral, 2026-11-14)
            return f"hitsound = S{novo} {MARCA}F5,{k}"
        if tem_hit and (200 <= n < 4000 or n >= 10000) and not 750 <= n < 900:
            p = re.sub(r"^hitsound = (F)5,\s*(\d)$", troca, p, flags=re.M)
        # agarrão: cada pancada com o som do que bate (joelho, garrafa, tesoura, toalha...)
        if n in agarroes:
            lista = agarroes[n]
            conta[0] = 0

            def troca_ag(mm):
                g = lista[min(conta[0], len(lista) - 1)]
                conta[0] += 1
                novo = g if "," in g else f"{g},{mm.group(3)}"
                return f"type = PlaySnd\n{mm.group(1)}value = {novo} {MARCA}{mm.group(2)}"
            p = re.sub(r"type = PlaySnd\n((?:trigger[^\n]*\n)+)value = (F5,\s*(\d))$", troca_ag, p, flags=re.M)
        # Despertar: a pausa toca a transformação no lugar do som de super
        if n == 2000:
            p = re.sub(r"^sound = F20,\s*0$", f"sound = F31,0 {MARCA}F20,0", p, flags=re.M)
        novos = []
        troca_vento = dict(extras).get("vento")
        # vento: golpe que bate e não é agarrão nem parry
        if tem_hit and not 750 <= n < 900 and not 3000 <= n < 3300:
            forte = int(tem_hit.group(1)) >= 2
            if troca_vento:
                v = troca_vento
            elif n in arma and vento_arma:
                v = f"55,{int(forte)}"
            else:
                k = (2 if n in chutes else 0) + (1 if forte else 0)
                if 1000 <= n < 2000 or 3400 <= n < 3500:
                    k = 4
                v = f"F40,{k}"
            novos.append(_playsnd(n, "vento", "trigger1 = Time = 0", v))
        for gat, valor in COMUNS.get(n, []):  # parry e agarrão (estados das frentes de parry e agarrão)
            novos.append(_playsnd(n, "comum", gat, valor))
        for gat, valor in extras:
            if gat == "vento":
                continue
            if gat == "proj":
                pm = re.search(r"^type = (?:Projectile|Helper)\n((?:trigger\w* = [^\n]*\n)+)", p, re.M | re.I)
                if not pm:
                    continue
                g = pm.group(1).rstrip("\n")
            else:
                g = f"trigger1 = Time = {gat[1:]}"
            novos.append(_playsnd(n, "assinatura", g, valor))
        if novos:
            # entra logo depois do cabeçalho do Statedef (antes do primeiro [State])
            i = p.find("\n[State ")
            i = len(p) if i < 0 else i + 1
            p = p[:i] + "".join(novos) + p[i:]
        out.append(p)
    c.write_text("".join(out), encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- medir

def medir():
    print(f"{'arquivo':38} {'som':>8} {'s':>5} {'LUFS máx':>9} {'pico dB':>8}")
    for arq in [MOTIF / "common.snd", MOTIF / "fight.snd", MOTIF / "system.snd",
                *(RAIZ / "chars" / n / f"{n}.snd" for n in LUTADORES)]:
        if not arq.exists():
            continue
        for (g, n), w in sorted(ler_snd(arq).items()):
            x = np.frombuffer(w[44:], "<i2") / 32768
            print(f"{str(arq.relative_to(RAIZ)):38} {g:>4},{n:<3} {len(x) / SR:5.2f} {lufs_max(x):9.1f} "
                  f"{20 * np.log10(np.abs(x).max() + 1e-9):8.1f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", help="pasta para soltar cada som em .wav")
    ap.add_argument("--narrador", metavar="PASTA_DA_VOZ", help="refaz as falas com o Piper (pasta do .onnx)")
    ap.add_argument("--medir", action="store_true")
    ap.add_argument("--sem-ligar", action="store_true", help="só gera os .snd, sem mexer no .def/.cns")
    a = ap.parse_args()
    if a.medir:
        medir()
        return
    if a.narrador:
        fazer_narrador(a.narrador)
    arquivos = {MOTIF / "common.snd": sons_comuns(), MOTIF / "fight.snd": sons_fight(),
                MOTIF / "system.snd": sons_sistema()}
    for i, nome in enumerate(LUTADORES):
        if (RAIZ / "chars" / nome).exists():
            arquivos[RAIZ / "chars" / nome / f"{nome}.snd"] = sons_lutador(nome, 1000 + 100 * i)
    for arq, sons in arquivos.items():
        gravar_snd(arq, sons)
        print(f"{arq.relative_to(RAIZ)}: {len(sons)} sons, {arq.stat().st_size // 1024} KB")
        if a.wav:
            for (g, n), x in sons.items():
                gravar_wav(Path(a.wav) / arq.stem / f"{g}_{n}.wav", x)
    if not a.sem_ligar:
        for nome in LUTADORES:
            if (RAIZ / "chars" / nome / f"{nome}.cns").exists():
                ligar(nome)
                print("ligado:", nome)


if __name__ == "__main__":
    main()
