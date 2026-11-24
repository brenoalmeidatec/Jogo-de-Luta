#!/usr/bin/env python3
"""Robô da emenda dos loops (meta 1.0, item da trilha: "três voltas de cada loop sem estalo").

  python3 ferramentas/conferir_loops.py [--ouvir PASTA]

Para cada faixa do musicas/loops.json, decodifica o OGG do jogo (o arquivo termina no fim do loop e o motor volta para
o loopstart) e olha a emenda fim -> loopstart como o motor toca:

  - SALTO: diferença entre a última amostra e a do loopstart, comparada com o passo normal da própria música perto
    dali (percentil 99,9 de |x[n+1] - x[n]| em 1 s antes do fim). Estalo = salto bem acima do passo normal.
  - VOLUME: energia (RMS) de 100 ms antes do fim contra 100 ms depois do loopstart. Degrau grande = buraco ou pancada.
  - ESPECTRO: diferença entre o espectro de 200 ms antes do fim e 200 ms depois do loopstart, dividida pelo percentil
    95 das passagens naturais da própria faixa (1,0 = muda tanto quanto as 5% passagens mais bruscas da música).

PASS quando salto <= 3x o passo normal (sem estalo) e degrau de volume <= 3 dB (sem buraco). O espectro acima de 1,0
não reprova (a volta do loop cai numa batida forte, que é brusca de propósito): marca "ouvir", e o --ouvir faz o
trecho para alguém escutar. Também confere se cada lutador
que tem Despertar tem a sua música (chars/<l>/despertar.ogg) e se o arquivo do loops.json existe.
--ouvir grava, para cada faixa, um MP3 de 6 s em volta da emenda (para ouvir no celular).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
TAXA = 44100
LIM_SALTO, LIM_DB, LIM_ESPECTRO = 3.0, 3.0, 1.0


def decodificar(arq):
    bruto = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(arq), "-f", "f32le", "-ac", "2", "-ar",
                            str(TAXA), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(bruto, np.float32).reshape(-1, 2)


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-9)


def espectro(x):
    m = x.mean(1)
    m = m * np.hanning(len(m))
    s = np.abs(np.fft.rfft(m))
    bandas = np.array_split(s[: len(s) // 2], 48)
    e = np.log10(np.array([b.mean() for b in bandas]) + 1e-9)
    return e


def _dist(a, b):
    ea, eb = espectro(a), espectro(b)
    return float(np.linalg.norm(ea - eb) / (np.linalg.norm(ea - ea.mean()) + np.linalg.norm(eb - eb.mean()) + 1e-9))


def emenda(x, ini):
    """(salto / passo normal, degrau de volume em dB, espectro da emenda / percentil 95 das passagens da música).
    O espectro é calibrado na própria faixa: em 200 pontos ao acaso dentro do loop mede a diferença entre os 200 ms
    antes e os 200 ms depois (o quanto a música muda sozinha de um instante para o outro). A emenda só é ruim se mudar
    mais que 95% dessas passagens naturais."""
    fim = len(x)
    passos = np.abs(np.diff(x[fim - TAXA:], axis=0)).max(1)
    normal = float(np.percentile(passos, 99.9)) + 1e-6
    salto = float(np.abs(x[ini] - x[fim - 1]).max())
    d = TAXA // 10
    degrau = abs(rms_db(x[fim - d:]) - rms_db(x[ini:ini + d]))
    j = TAXA // 5
    rng = np.random.default_rng(7)
    naturais = [_dist(x[k - j:k], x[k:k + j]) for k in rng.integers(ini + j, fim - j, 200)]
    p95 = float(np.percentile(naturais, 95)) + 1e-9
    return salto / normal, degrau, _dist(x[fim - j:], x[ini:ini + j]) / p95


def ouvir(x, ini, destino):
    """3 s antes do fim emendados nos 3 s depois do loopstart, como o motor toca."""
    pedaco = np.concatenate([x[len(x) - 3 * TAXA:], x[ini:ini + 3 * TAXA]])
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", str(TAXA), "-i", "-",
                    "-b:a", "128k", str(destino)], input=pedaco.astype(np.float32).tobytes(), check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ouvir", type=Path)
    a = ap.parse_args()
    arq_loops = RAIZ / "musicas" / "loops.json"
    if not arq_loops.exists():
        sys.exit("Não achei musicas/loops.json (rode ferramentas/converter_musicas.py).")
    loops = json.loads(arq_loops.read_text(encoding="utf-8"))
    ruins = 0
    print(f"{'faixa':<26}{'salto':>7}{'volume':>9}{'espectro':>10}  (espectro: 1,0 = passagem mais brusca da faixa)")
    for nome, info in loops.items():
        arq = RAIZ / info["arquivo"]
        if not arq.exists():
            print(f"{nome:<26} FALTA o arquivo {info['arquivo']}")
            ruins += 1
            continue
        if int(info.get("amostras_por_segundo", TAXA)) != TAXA:
            print(f"{nome:<26} AVISO: loops.json em {info['amostras_por_segundo']} Hz, o robô decodifica em {TAXA}")
        x = decodificar(arq)
        ini = int(info["loopstart"])
        s, db, esp = emenda(x, ini)
        ok = s <= LIM_SALTO and db <= LIM_DB
        ruins += not ok
        selo = "FAIL" if not ok else ("PASS, ouvir" if esp > LIM_ESPECTRO else "PASS")
        print(f"{nome:<26}{s:>6.2f}x{db:>7.1f}dB{esp:>10.2f}  {selo:<12}"
              f"  (volta em {ini / TAXA:.1f} s, fim {len(x) / TAXA:.1f} s)")
        if a.ouvir:
            a.ouvir.mkdir(parents=True, exist_ok=True)
            ouvir(x, ini, a.ouvir / f"{nome}_emenda.mp3")
    # quem desperta precisa da própria música (regra: a do Despertar substitui a do cenário)
    for pasta in sorted((RAIZ / "chars").iterdir()):
        cns = pasta / f"{pasta.name}.cns"
        if not cns.exists() or pasta.name.startswith("teste"):
            continue
        if "despertar.ogg" in cns.read_text(encoding="utf-8", errors="replace") and not (pasta / "despertar.ogg").exists():
            print(f"{pasta.name:<26} FALTA chars/{pasta.name}/despertar.ogg (o .cns toca e fica mudo)")
            ruins += 1
    print(f"\nRESUMO: {'todas as emendas limpas' if not ruins else f'{ruins} problema(s)'}")
    sys.exit(1 if ruins else 0)


if __name__ == "__main__":
    main()
