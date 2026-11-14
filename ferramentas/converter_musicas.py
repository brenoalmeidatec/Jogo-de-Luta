"""Converte as músicas do Suno (musicas/originais/*.m4a) para OGG Vorbis em loop sem emenda, que o IKEMEN GO toca.

    python3 ferramentas/converter_musicas.py            # todas
    python3 ferramentas/converter_musicas.py lobby      # só uma

Para cada faixa:
1. corta o silêncio do começo (gravação de tela) e iguala o volume em -14 LUFS (loudnorm em duas passadas);
2. acha o loop (pedido do Breno, issue #33): fim e começo do loop caem em batidas (librosa), longe do corte da
   gravação e antes de qualquer fade de saída, escolhidos onde os 8 s que levam a cada ponto soam mais parecidos
   (cromagrama + timbre), e acertados na amostra por correlação da onda;
3. assa um crossfade de 120 ms no próprio arquivo, entre o fim do loop e o trecho que leva ao começo dele, e corta o
   arquivo no fim do loop. Assim a volta do loop (fim do arquivo -> loopstart) é contínua;
4. grava OGG q5 (~160 kbps), 44,1 kHz estéreo, onde o launcher baixa (motif/, stages/, chars/);
5. escreve musicas/loops.json com o loopstart de cada faixa, em amostras de 44,1 kHz (o motor conta amostras do
   arquivo). Os geradores (gerar_layout.py, gerar_cenario.py, gerar_pengaro.py) leem esse arquivo.
Requer ffmpeg no PATH e pip install librosa soundfile numpy.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
ORIGEM = RAIZ / "musicas" / "originais"
LOOPS = RAIZ / "musicas" / "loops.json"

# faixa -> destino (relativo à raiz do jogo)
DESTINO = {
    "lobby": "motif/nazafight/musicas/lobby.ogg",
    "selecao": "motif/nazafight/musicas/selecao.ogg",
    "cenario_maria_fumaca": "stages/musicas/maria_fumaca.ogg",
    "cenario_cristo": "stages/musicas/cristo.ogg",
    "cenario_praca": "stages/musicas/praca.ogg",
    "cenario_passarela": "stages/musicas/passarela.ogg",
    "boss_pengaro_endiabrado": "chars/pengaro/despertar.ogg",
    "boss_hazak_diabo_loiro": "chars/hazaki/despertar.ogg",
    "boss_gutto_garanhao": "chars/gutto/despertar.ogg",
    "boss_ck_ratao": "chars/ck/despertar.ogg",
    "boss_raiclaven_cientista": "chars/raiclaven/despertar.ogg",
}
SR = 44100
LUFS = -14
XFADE = 0.12        # s, crossfade da emenda
JANELA = 8.0        # s de música comparados antes de cada ponto
FOLGA_FIM = 2.5     # s: o fim do loop fica pelo menos isso antes do corte/fade da gravação
FADE_IN = 0.03      # s, só para o primeiro toque não estalar


def rodar(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stderr


def inicio_do_som(arq):
    log = rodar(["ffmpeg", "-nostats", "-i", str(arq), "-af", "silencedetect=n=-45dB:d=0.4", "-f", "null", "-"])
    ini = re.findall(r"silence_start: ([0-9.]+)", log)
    fim = re.findall(r"silence_end: ([0-9.]+)", log)
    if ini and float(ini[0]) < 0.05 and fim:
        return max(0.0, float(fim[0]) - 0.05)
    return 0.0


def normalizado(arq, wav):
    """Corta o silêncio do começo, iguala em -14 LUFS e grava um WAV 44,1 kHz estéreo float."""
    corte = f"atrim=start={inicio_do_som(arq):.3f},asetpts=PTS-STARTPTS"
    medida = rodar(["ffmpeg", "-nostats", "-i", str(arq), "-af",
                    f"{corte},loudnorm=I={LUFS}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"])
    m = json.loads(medida[medida.rindex("{"):medida.rindex("}") + 1])
    norma = (f"loudnorm=I={LUFS}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
             f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    rodar(["ffmpeg", "-y", "-nostats", "-i", str(arq), "-af", f"{corte},{norma}", "-ar", str(SR), "-ac", "2",
           "-c:a", "pcm_f32le", str(wav)])


def fim_util(mono):
    """Até onde a música está "cheia": antes do corte seco ou do fade de saída da gravação."""
    rms = np.sqrt(np.convolve(mono ** 2, np.ones(SR // 2) / (SR // 2), mode="same"))
    alvo = np.median(rms[: len(rms) * 9 // 10]) * 0.6
    i = len(rms) - 1
    while i > 0 and rms[i] < alvo:
        i -= SR // 20
    return i / SR - FOLGA_FIM


def achar_loop(x):
    import librosa
    mono = x.mean(axis=1)
    dur = len(mono) / SR
    hop = 512
    _tempo, batidas = librosa.beat.beat_track(y=mono, sr=SR, hop_length=hop, units="time")
    croma = librosa.feature.chroma_cqt(y=mono, sr=SR, hop_length=hop)
    timbre = librosa.feature.mfcc(y=mono, sr=SR, hop_length=hop, n_mfcc=13)[1:]
    timbre = (timbre - timbre.mean(1, keepdims=True)) / (timbre.std(1, keepdims=True) + 1e-9)
    feat = np.vstack([croma * 3, timbre / 3])
    q = int(JANELA * SR / hop)

    def janela(t):
        f = int(t * SR / hop)
        v = feat[:, f - q:f].ravel()
        return (v - v.mean()) / (v.std() + 1e-9)

    limite = fim_util(mono)
    fins = [b for b in batidas if limite - 30 <= b <= limite]
    # o loop tem de ter pelo menos metade da música, e o começo precisa de 8 s de música antes dele
    comecos = [b for b in batidas if JANELA + 0.5 <= b]
    melhor = (-9.0, None, None)
    for e in fins:
        we = janela(e)
        for s in comecos:
            if e - s < max(25.0, dur * 0.45):
                continue
            nota = float(np.dot(we, janela(s)) / len(we))
            if nota > melhor[0]:
                melhor = (nota, s, e)
    nota, s, e = melhor
    # acerto fino na amostra: alinha a onda que leva ao começo com a que leva ao fim (±12 ms)
    S, E = int(s * SR), int(e * SR)
    n, r = int(0.05 * SR), int(0.012 * SR)
    ref = mono[E - n:E]
    melhor_d, melhor_c = 0, -9
    for d in range(-r, r + 1):
        seg = mono[S + d - n:S + d]
        c = float(np.dot(ref, seg) / (np.linalg.norm(ref) * np.linalg.norm(seg) + 1e-9))
        if c > melhor_c:
            melhor_d, melhor_c = d, c
    return S + melhor_d, E, nota, melhor_c


def assar(x, S, E):
    """Arquivo termina em E; os últimos XFADE s viram mistura do fim com o trecho que leva a S (curva de potência)."""
    y = x[:E].copy()
    n = int(XFADE * SR)
    t = np.linspace(0, np.pi / 2, n)[:, None]
    y[E - n:E] = x[E - n:E] * np.cos(t) + x[S - n:S] * np.sin(t)
    f = int(FADE_IN * SR)
    y[:f] *= np.linspace(0, 1, f)[:, None]
    return y


def converter(nome, destino, loops):
    import soundfile as sf
    with tempfile.TemporaryDirectory() as tmp:
        wav, saida_wav = Path(tmp) / "n.wav", Path(tmp) / "l.wav"
        normalizado(ORIGEM / f"{nome}.m4a", wav)
        x, sr = sf.read(wav, dtype="float32", always_2d=True)
        assert sr == SR
        S, E, nota, fase = achar_loop(x)
        y = assar(x, S, E)
        pico = np.abs(y).max()
        if pico > 0.98:
            y *= 0.98 / pico
        sf.write(saida_wav, y, SR, subtype="FLOAT")
        saida = RAIZ / destino
        saida.parent.mkdir(parents=True, exist_ok=True)
        rodar(["ffmpeg", "-y", "-nostats", "-i", str(saida_wav), "-c:a", "libvorbis", "-q:a", "5",
               "-map_metadata", "-1", "-metadata", f"title=Nazafights - {nome}", str(saida)])
    loops[nome] = {"arquivo": destino, "loopstart": S, "loopend": E, "amostras_por_segundo": SR}
    print(f"{nome:28s} loop {S / SR:6.2f}s -> {E / SR:6.2f}s (volta {(E - S) / SR:5.1f}s, parecido {nota:.2f}, "
          f"onda {fase:.2f})  {saida.stat().st_size / 1e6:.1f} MB", flush=True)


def main():
    nomes = sys.argv[1:] or list(DESTINO)
    loops = json.loads(LOOPS.read_text(encoding="utf-8")) if LOOPS.exists() else {}
    for nome in nomes:
        converter(nome, DESTINO[nome], loops)
        LOOPS.write_text(json.dumps(loops, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
