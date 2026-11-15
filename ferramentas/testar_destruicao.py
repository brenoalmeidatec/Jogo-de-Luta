#!/usr/bin/env python3
"""Robô da destruição do cenário (issue #35, missão dos cenários 4.2): confere no jogo de verdade, na nuvem (Xvfb), que

  - o nível 1 só liga quando um lutador desperta e o nível 2 só quando os dois despertaram;
  - nada volta atrás no fim do round (o P2 cai nocauteado depois de despertar e o round 2 começa ainda no nível 2).

  python3 ferramentas/testar_destruicao.py [--cenarios praca,passarela,...] [--p1 pengaro --p2 gutto]

Como vê: numa cópia de cada cenário entram cinco quadradinhos parados na beira da tela (metade de cima magenta, metade
de baixo verde, cores que o cenário não tem juntas), um em cada grupo de destruição (909 nível 0, 910 nível < 2,
911 nível >= 1, 912 nível 2, 913 nível 1), desenhados por último. O robô filma a luta e lê, quadro a quadro, quais
quadradinhos estão acesos (grupo que o cenário não usa não conta). Os quadros escuros (intro, cena da transformação,
troca de round) ficam de fora.
PASS quando a sequência é nível 0, nível 1, nível 2, com uma troca de round no meio do nível 2 e o nível 2 de novo depois.
"""
import argparse
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from testar_pengaro import RAIZ, INI_LINUX, ambiente_linux, motor_linux, ajustar_ini  # noqa: E402
from filmar_transformacao import forcar_despertar  # noqa: E402
from layout_sff import ler_sff2, escrever_sff2_bruto, png_pil  # noqa: E402

CENARIOS = ["praca", "passarela", "katiara", "cristo", "maria_fumaca"]
GRUPOS = [909, 910, 911, 912, 913]
CIMA, BAIXO = (255, 0, 255), (0, 255, 0)
LADO, X0, Y0, PASSO = 24, 2, 200, 30           # quadradinhos na tela 1280x720
ESPERADO = {0: (1, 1, 0, 0, 0), 1: (0, 1, 1, 0, 1), 2: (0, 0, 1, 1, 0)}


def marcar(stages, cenario):
    """Põe os cinco quadradinhos na cópia do cenário (grupo de sprite 8000+, camada da frente, delta 0, depois do
    último [BG]). Devolve os grupos que o cenário usa."""
    arq, sff = stages / f"{cenario}.def", stages / f"{cenario}.sff"
    itens = [(g, n, w, h, ax, ay, png) for (g, n), (w, h, ax, ay, _f, png) in ler_sff2(sff).items()]
    blocos = []
    img = Image.new("RGBA", (LADO, LADO), BAIXO + (255,))
    img.paste(Image.new("RGBA", (LADO, LADO // 2), CIMA + (255,)), (0, 0))
    for i, gid in enumerate(GRUPOS):
        itens.append((8000 + i, 0, LADO, LADO, 0, 0, png_pil(img)))
        blocos.append(f"[BG teste {gid}]\ntype = normal\nspriteno = {8000 + i}, 0\nid = {gid}\nlayerno = 1\n"
                      f"start = {X0 - 640}, {Y0 + PASSO * i}\ndelta = 0, 0\nmask = 0\n\n")
    escrever_sff2_bruto(sff, itens)
    txt = arq.read_text(encoding="utf-8").replace("\r\n", "\n")
    ultimo = list(re.finditer(r"(?m)^\[BG [^\]]*\]\n(?:[^\n\[][^\n]*\n)*", txt))[-1]
    txt = txt[:ultimo.end()].rstrip("\n") + "\n\n" + "".join(blocos) + txt[ultimo.end():]
    arq.write_text(txt, encoding="utf-8")
    return {g for g in GRUPOS if re.search(rf"(?m)^ctrlID\s*=\s*{g}\b", txt)}


def nocautear(cns, quando):
    """O lutador cai nocauteado aos `quando` tiques de luta do round 1 (o round 2 começa sozinho)."""
    txt = cns.read_text(encoding="utf-8")
    extra = (f"[State -2, Teste: nocaute]\ntype = LifeSet\n"
             f"trigger1 = RoundNo = 1 && RoundState = 2 && map(filma_t) >= {quando}\nvalue = 0\n\n")
    txt = re.sub(r"^\[Statedef -2\][^\n]*\n(?:[^\n\[][^\n]*\n)*\n?", lambda m: m.group(0) + extra, txt, count=1,
                 flags=re.M)
    cns.write_text(txt, encoding="utf-8", newline="\n")


def estado(quadro, k, usados):
    """Nível que os quadradinhos mostram no quadro (None se o quadro está escuro; tupla '?' se não bate com nenhum)."""
    a = np.asarray(quadro.convert("RGB")).astype(int)
    if a.mean() < 25:
        return None
    acesos = []
    for i in range(len(GRUPOS)):
        x = round((X0 + LADO / 2) * k)
        yc, yb = round((Y0 + PASSO * i + LADO / 4) * k), round((Y0 + PASSO * i + LADO * 3 / 4) * k)
        c, b = a[yc, x], a[yb, x]
        acesos.append(int(np.abs(c - CIMA).max() < 40 and np.abs(b - BAIXO).max() < 40))
    if not any(acesos):
        return None           # cenário não desenhado: cena da transformação (pausebg = 0) ou troca de round
    for nivel, esp in ESPERADO.items():
        if all(acesos[i] == esp[i] for i, g in enumerate(GRUPOS) if g in usados):
            return nivel
    return ("?",) + tuple(acesos)


def rodar(cenario, a, pasta):
    with tempfile.TemporaryDirectory() as td:
        copia = Path(td) / "motor"
        shutil.copytree(motor_linux(), copia, symlinks=True)
        for nome in (a.p1, a.p2):
            shutil.copytree(RAIZ / "chars" / nome, copia / "chars" / nome, dirs_exist_ok=True)
        shutil.copytree(RAIZ / "motif" / "nazafight", copia / "data" / "nazafight", dirs_exist_ok=True)
        (copia / "stages").mkdir(exist_ok=True)
        for ext in ("def", "sff"):
            shutil.copy(RAIZ / "stages" / f"{cenario}.{ext}", copia / "stages")
        for extra in (RAIZ / "stages").glob(f"{cenario}*"):
            if extra.suffix not in (".def", ".sff"):
                shutil.copy(extra, copia / "stages")
        usados = marcar(copia / "stages", cenario)
        larg, alt = a.tela.split("x")
        ini = {**INI_LINUX, "Motif": "data/nazafight/system.def", "GameWidth": larg, "GameHeight": alt}
        INI_LINUX.clear()
        INI_LINUX.update(ini)
        ajustar_ini(copia)
        forcar_despertar(copia / "chars" / a.p1 / f"{a.p1}.cns", a.primeiro)
        forcar_despertar(copia / "chars" / a.p2 / f"{a.p2}.cns", a.segundo)
        nocautear(copia / "chars" / a.p2 / f"{a.p2}.cns", a.segundo + a.nocaute)
        disp = f":{70 + os.getpid() % 9}"
        xvfb = subprocess.Popen(["Xvfb", disp, "-screen", "0", f"{a.tela}x24"], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(2)
        amb = {**ambiente_linux(copia), "DISPLAY": disp}
        jogo = subprocess.Popen(["./Ikemen_GO_Linux", "-p1", a.p1, "-p2", a.p2, "-s", f"stages/{cenario}.def",
                                 "-rounds", "2", "-time", "-1"], cwd=copia, env=amb,
                                stdout=open(pasta / f"{cenario}_log.txt", "w"), stderr=subprocess.STDOUT,
                                start_new_session=True)
        video = pasta / f"{cenario}_robo.mp4"
        try:
            time.sleep(a.espera)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "x11grab", "-draw_mouse", "0", "-framerate",
                            "10", "-video_size", a.tela, "-i", disp, "-t", str(a.segundos), "-c:v", "libx264rgb",
                            "-crf", "0", str(video)], env=amb, check=True)
        finally:
            try:
                os.killpg(jogo.pid, 9)
            except ProcessLookupError:
                pass
            xvfb.kill()
    bruto = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(video), "-f", "image2pipe", "-vcodec", "png",
                            "-"], capture_output=True, check=True).stdout
    k = int(a.tela.split("x")[0]) / 1280
    estados = []
    for parte in bruto.split(b"\x89PNG")[1:]:
        estados.append(estado(Image.open(io.BytesIO(b"\x89PNG" + parte)), k, usados))
    return estados


def resumo(estados):
    seq = []
    for e in estados:
        if not seq or seq[-1][0] != e:
            seq.append([e, 1])
        else:
            seq[-1][1] += 1
    return seq


def julgar(seq):
    """PASS: nível 0, 1, 2 nessa ordem (sem voltar), e o nível 2 aparece de novo depois de uma tela escura (round 2)."""
    so = [e for e, n in seq if e is not None and n >= 2]
    limpo = [e for i, e in enumerate(so) if i == 0 or so[i - 1] != e]
    if any(isinstance(e, tuple) for e in limpo):
        return False, f"quadradinhos misturados: {[e for e in limpo if isinstance(e, tuple)]}"
    if limpo[:3] != [0, 1, 2] or any(e != 2 for e in limpo[3:]):
        return False, f"ordem dos níveis {limpo} (esperado [0, 1, 2])"
    i2 = next(i for i, (e, n) in enumerate(seq) if e == 2)
    depois = [e for e, n in seq[i2:]]
    if None not in depois or depois[-1] != 2 or depois.index(None) == len(depois) - 1:
        return False, "não deu para ver o round 2 começar no nível 2 (aumente --segundos)"
    return True, "nível 0 → 1 → 2, e o round 2 começou no nível 2"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cenarios", default=",".join(CENARIOS))
    ap.add_argument("--p1", default="pengaro")
    ap.add_argument("--p2", default="gutto")
    ap.add_argument("--primeiro", type=int, default=200)
    ap.add_argument("--segundo", type=int, default=600)
    ap.add_argument("--nocaute", type=int, default=300, help="tiques depois do 2º Despertar até o P2 cair")
    ap.add_argument("--segundos", type=float, default=60)
    ap.add_argument("--espera", type=float, default=6)
    ap.add_argument("--tela", default="640x360")
    ap.add_argument("--pasta", type=Path, help="onde guardar os vídeos do robô (padrão: pasta temporária)")
    a = ap.parse_args()
    pasta = a.pasta or Path(tempfile.mkdtemp(prefix="robo_destruicao_"))
    pasta.mkdir(parents=True, exist_ok=True)
    falhas = 0
    for c in a.cenarios.split(","):
        seq = resumo(rodar(c, a, pasta))
        ok, msg = julgar(seq)
        falhas += not ok
        print(f"{'PASS' if ok else 'FAIL'} {c}: {msg}")
        print("   sequência:", " ".join(f"{'-' if e is None else e}x{n}" for e, n in seq), flush=True)
    print("FIM:", "tudo PASS" if not falhas else f"{falhas} FAIL", f"(vídeos em {pasta})")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
