"""Benchmark Linux/Xvfb (llvmpipe), CK x Hazak, velocidade normal."""
import argparse
import csv
import os
import re
import shutil
import signal
import statistics
import subprocess
import tempfile
import time
from pathlib import Path

from testar_pengaro import RAIZ, ambiente_linux, injetar, motor_linux


def preparar(motor):
    for nome in ("ck", "hazaki"):
        shutil.copytree(RAIZ / "chars" / nome, motor / "chars" / nome, dirs_exist_ok=True)
        injetar(motor / f"chars/{nome}/{nome}.cmd", nome == "hazaki")
    shutil.copytree(RAIZ / "motif/nazafight", motor / "data/nazafight", dirs_exist_ok=True)
    shutil.copytree(RAIZ / "stages", motor / "stages", dirs_exist_ok=True)
    debug = motor / "external/script/debug.lua"
    with debug.open("ab") as arquivo:
        arquivo.write(b"\n" + (RAIZ / "ferramentas/robo/desempenho.lua").read_bytes())
    save = motor / "save"
    cfg = (save / "config.ini").read_text(encoding="utf-8-sig")
    for chave, valor in {"Motif": "data/nazafight/system.def", "WindowScaleMode": 0,
                         "VsScreenLoading": 1, "GameWidth": 1280, "GameHeight": 720,
                         "WindowWidth": 1280, "WindowHeight": 720, "Fullscreen": 0,
                         "VSync": 1, "Framerate": 60}.items():
        cfg = re.sub(rf"(?im)^({chave}\s*=)[^\r\n]*", rf"\g<1> {valor}", cfg)
    (save / "normal.ini").write_text(cfg)
    atalho = (RAIZ / "ferramentas/Jogo de Luta.bat").read_text(encoding="utf-8")
    funcoes = atalho[atalho.index("function Usar-PerfilLeve"):atalho.index("$opcoes = @{}")]
    # Mesma selecao e mesmo INI usados pelo atalho Windows.
    subprocess.run(["pwsh", "-NoProfile", "-Command", funcoes + """
$ErrorActionPreference = 'Stop'
if (!(Usar-PerfilLeve 'Intel(R) Core(TM) i5-3470 CPU' @('Intel(R) HD Graphics') 'auto')) { throw 'i5 legado' }
if (Usar-PerfilLeve 'Intel(R) Core(TM) i5-1345U' @('Intel(R) Iris Xe Graphics') 'auto') { throw 'i5 moderno' }
if (Usar-PerfilLeve 'i5-3470' @('Intel HD Graphics','NVIDIA GeForce') 'auto') { throw 'GPU dedicada' }
$t = Configurar-VideoLeve (Get-Content -Raw normal.ini)
[IO.File]::WriteAllText((Join-Path $pwd 'leve.ini'), $t)
"""], cwd=save, check=True)


def medir(motor, perfil, destino):
    fim = motor / "fps.csv"
    fim.unlink(missing_ok=True)
    env = {**ambiente_linux(motor), "LP_NUM_THREADS": "2", "ALSOFT_DRIVERS": "null"}
    args = ["./Ikemen_GO_Linux", "-config", f"save/{perfil}.ini", "-p1", "ck", "-p2", "hazaki",
            "-s", "stages/maria_fumaca.def"]
    with destino.with_suffix(".log").open("w") as log:
        jogo = subprocess.Popen(args, cwd=motor, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            limite = time.monotonic() + 120
            while not fim.exists() and jogo.poll() is None and time.monotonic() < limite:
                time.sleep(0.25)
            if not fim.exists():
                raise RuntimeError(destino.with_suffix(".log").read_text(errors="replace")[-3500:])
            shutil.copyfile(fim, destino)
        finally:
            if jogo.poll() is None:
                os.killpg(jogo.pid, signal.SIGTERM)
            jogo.wait(timeout=10)
    with destino.open() as arq:
        linhas = list(csv.DictReader(arq))
    assert len(linhas) == 550
    for fase in dict.fromkeys(l["fase"] for l in linhas):
        grupo = [l for l in linhas if l["fase"] == fase]
        print(destino.stem, fase, round(statistics.mean(float(l["fps"]) for l in grupo), 1),
              "P1", sorted(set(l["ck"] for l in grupo)), "P2", sorted(set(l["hazak"] for l in grupo)), flush=True)
    for fase, coluna, inicio, final in [("acerto","hazak",5000,5999), ("defesa","hazak",150,155),
                                        ("especial","ck",3000,3000), ("despertar","ck",2000,2000)]:
        assert any(l["fase"] == fase and inicio <= int(l[coluna]) <= final for l in linhas), fase


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("saida", type=Path)
    parser.add_argument("perfis", nargs="+", choices=["normal", "leve"])
    op = parser.parse_args()
    op.saida.mkdir(parents=True, exist_ok=True)
    base = motor_linux()
    with tempfile.TemporaryDirectory() as pasta:
        motor = Path(pasta) / "motor"
        shutil.copytree(base, motor, symlinks=True)
        preparar(motor)
        for i, perfil in enumerate(op.perfis):
            medir(motor, perfil, op.saida / f"{i+1}-{perfil}.csv")
