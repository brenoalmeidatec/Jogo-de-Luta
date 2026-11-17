#!/usr/bin/env python3
"""Filma um cenário na Windows Sandbox (passeio pelas duas pontas) e monta as tiras de quadros para olhar.

  python ferramentas/filmar_cenario.py teste [--p1 pengaro] [--p2 hazaki] [--segundos 8] [--saida PASTA]

Espera a vez da sandbox (a mesma trava do sandbox.py: só cabe uma), chama o filmar_sandbox.py com
--cenario stages/<id>.def --passeio e, do luta.mp4, tira:
  tira_geral.png      1 quadro a cada 20 ticks (3 por segundo), 6 por linha, para ver a paralaxe e as bordas
  tira_fluidez.png    30 ticks seguidos a partir do segundo 0,2 (câmera parada), para ver animação sem salto
  quadro_esq.png, quadro_alto.png, quadro_dir.png   tela cheia nas pontas e com a câmera no alto
O roteiro do passeio é ferramentas/robo/passeio.lua. Critérios de aceite em docs/arcade/cenarios.md.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sandbox  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent


def tiras(video, saida):
    ff = shutil.which("ffmpeg")

    def roda(*args):
        subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-y", *args], check=True)

    roda("-i", str(video), "-vf", r"select=not(mod(n\,20)),scale=426:-1,tile=6x4", "-frames:v", "1",
         str(saida / "tira_geral.png"))
    roda("-ss", "0.2", "-i", str(video), "-vf", "scale=426:-1,tile=6x5", "-frames:v", "1",
         str(saida / "tira_fluidez.png"))
    for nome, seg in (("quadro_esq", 1.75), ("quadro_alto", 2.3), ("quadro_dir", 5.35)):
        roda("-ss", str(seg), "-i", str(video), "-frames:v", "1", str(saida / f"{nome}.png"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cenario", help="id do cenário (stages/<id>.def)")
    ap.add_argument("--p1", default="pengaro")
    ap.add_argument("--p2", default="hazaki")
    ap.add_argument("--segundos", type=float, default=8)
    ap.add_argument("--saida", type=Path)
    ap.add_argument("--so-tiras", action="store_true", help="não filma: refaz as tiras do luta.mp4 que já está em --saida")
    a = ap.parse_args()
    if not (RAIZ / "stages" / f"{a.cenario}.def").exists():
        sys.exit(f"stages/{a.cenario}.def não existe: rode o gerar_cenario.py antes")
    saida = (a.saida or sandbox.CASA / "filmagens" / f"cenario_{a.cenario}").resolve()
    saida.mkdir(parents=True, exist_ok=True)
    if not a.so_tiras:
        trava = sandbox.esperar_vez()
        try:
            r = subprocess.run([sys.executable, str(RAIZ / "ferramentas/filmar_sandbox.py"), "--p1", a.p1, "--p2", a.p2,
                                "--segundos", str(a.segundos), "--cenario", f"stages/{a.cenario}.def", "--passeio",
                                "--saida", str(saida)])
        finally:
            trava.unlink(missing_ok=True)
        if r.returncode:
            sys.exit(r.returncode)
    tiras(saida / "luta.mp4", saida)
    print(f"tiras em {saida}")


if __name__ == "__main__":
    main()
