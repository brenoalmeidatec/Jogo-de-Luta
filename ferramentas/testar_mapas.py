#!/usr/bin/env python3
"""Abre o jogo de verdade no Linux sem tela (Xvfb + Mesa) e passa pela tela de escolha de mapa, tirando fotos.

  python3 ferramentas/testar_mapas.py [--saida PASTA] [--modo arcade|assistir|versus] [--direita N] [--filmar S]

Monta uma cópia do IKEMEN GO v1.0.0 Linux (o mesmo do robô, ~/.cache/nazafight/ikemen) do jeito que o
"Jogo de Luta.bat" monta no Windows: lutadores, cenários (stages/), layout Nazafights e o data/select.def com os
lutadores, os cenários de Nazaré em [ExtraStages] e os cenários de exemplo do IKEMEN comentados (issue #34).
Depois aperta as teclas pelo xdotool (Enter confirma, setas andam) e tira fotos de cada passo:
  1_titulo.png, 2_selecao.png, 3_mapa.png, 4_mapa_N.png (depois de N vezes para a direita), 5_luta.png
--filmar S grava S segundos da luta em luta.mp4 (ffmpeg x11grab), para conferir a animação do cenário.
Requisitos: xvfb-run, xdotool, imagemagick (import) e ffmpeg (só para --filmar).
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from testar_pengaro import RAIZ, INI_LINUX, ambiente_linux, motor_linux  # noqa: E402

LUTADORES = ["pengaro", "hazaki", "gutto", "raiclaven", "ck"]
EXEMPLOS = r"stages/(?:stage0|stage1|stage3d|stage3d_outline|stageZ|interactivestage|kfm)\.def"
ITENS_MENU = {"arcade": 0, "versus": 1, "treino": 3, "assistir": 4}


def cenarios_do_jogo():
    """Os cenários Nazafights que vão para a escolha (o mesmo critério do .bat): stages/*.def menos o de teste."""
    return sorted(p.name for p in (RAIZ / "stages").glob("*.def") if p.stem != "teste")


def montar_select(texto, cenarios):
    """O que o passo 3 do .bat faz no data/select.def, em Python."""
    fixo = "stages/maria_fumaca.def" if "maria_fumaca.def" in cenarios else "stages/stage0-720.def"
    for lut in LUTADORES:
        if (RAIZ / "chars" / lut / f"{lut}.def").exists() and not re.search(rf"(?m)^\s*{lut}\s*(,|$)", texto):
            texto = re.sub(r"(?m)^randomselect", f"{lut}, {fixo}\nrandomselect", texto, count=1)
    for c in reversed(cenarios):  # cada um entra logo abaixo do [ExtraStages]: de trás para frente
        if not re.search(rf"(?m)^\s*stages/{re.escape(c)}", texto):
            texto = re.sub(r"(?im)^\[ExtraStages\][^\r\n]*\r?\n", lambda m: m.group(0) + f"stages/{c}\n", texto, count=1)
    texto = re.sub(r"(?m)^([ \t]*kfm\w*[ \t]*,)", r";\1", texto)
    texto = re.sub(rf"(?m)^([ \t]*{EXEMPLOS}[ \t]*(?:,|$))", r";\1", texto)
    return texto


def patch_lua(copia):
    """Enter escolhe o lutador (como o .bat faz no main.lua), para o teste andar só com Enter e setas."""
    lua = copia / "external/script/main.lua"
    t = lua.read_text(encoding="utf-8")
    novo = ("function main.f_btnPalNo(p)\n\tif commandGetState(p, 's') then return 1 end\n"
            "\tif commandGetState(p, 'y') then return 2 end\n\treturn 0\nend")
    t2 = re.sub(r"(?s)function main\.f_btnPalNo\(p\).*?\r?\nend", lambda m: novo, t, count=1)
    lua.write_text(t2, encoding="utf-8")


def montar(tmp):
    motor = motor_linux()
    copia = tmp / "motor"
    shutil.copytree(motor, copia, symlinks=True)
    for lut in LUTADORES:
        if (RAIZ / "chars" / lut).exists():
            shutil.copytree(RAIZ / "chars" / lut, copia / "chars" / lut, dirs_exist_ok=True)
    shutil.copytree(RAIZ / "stages", copia / "stages", dirs_exist_ok=True)
    shutil.copytree(RAIZ / "motif" / "nazafight", copia / "data" / "nazafight", dirs_exist_ok=True)
    sel = copia / "data" / "select.def"
    sel.write_text(montar_select(sel.read_text(encoding="utf-8"), cenarios_do_jogo()), encoding="utf-8")
    patch_lua(copia)
    ini = copia / "save" / "config.ini"
    t = ini.read_text(encoding="utf-8")
    for k, v in {**INI_LINUX, "Motif": "data/nazafight/system.def"}.items():
        t = re.sub(rf"(?m)^({re.escape(k)}\s*=\s*)[^\r\n]*", lambda m: m.group(1) + v, t)
    t = t.replace("data/demo.zss", "data/nazafight/demo.zss")   # como o .bat: demo sem o link do motor
    ini.write_text(t, encoding="utf-8")
    return copia


class Tela:
    def __init__(self, copia, saida):
        self.saida = saida
        self.disp = ":77"
        self.xvfb = subprocess.Popen(["Xvfb", self.disp, "-screen", "0", "1280x720x24"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.5)
        amb = {**ambiente_linux(copia), "DISPLAY": self.disp}
        self.amb = amb
        self.log = open(saida / "motor_log.txt", "w")
        self.jogo = subprocess.Popen(["./Ikemen_GO_Linux"], cwd=copia, env=amb, stdout=self.log, stderr=subprocess.STDOUT)

    def janela(self):
        r = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", ""], env=self.amb, capture_output=True,
                           text=True)
        ids = r.stdout.split()
        return ids[-1] if ids else None

    def tecla(self, k, vezes=1, pausa=0.35):
        for _ in range(vezes):
            subprocess.run(["xdotool", "keydown", k], env=self.amb)
            time.sleep(0.08)
            subprocess.run(["xdotool", "keyup", k], env=self.amb)
            time.sleep(pausa)

    def foto(self, nome):
        subprocess.run(["import", "-display", self.disp, "-window", "root", str(self.saida / nome)], env=self.amb)
        print("foto", self.saida / nome, flush=True)

    def filmar(self, segundos, nome="luta.mp4"):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "x11grab", "-video_size", "1280x720", "-framerate",
                        "30", "-i", self.disp, "-t", str(segundos), "-pix_fmt", "yuv420p", str(self.saida / nome)],
                       env=self.amb)
        print("filme", self.saida / nome, flush=True)

    def fechar(self):
        for p in (self.jogo, self.xvfb):
            p.kill()
        self.log.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", type=Path, default=RAIZ / "saida_mapas")
    ap.add_argument("--modo", choices=list(ITENS_MENU), default="arcade")
    ap.add_argument("--direita", type=int, default=1, help="quantas vezes trocar de mapa antes de confirmar")
    ap.add_argument("--filmar", type=float, default=0)
    ap.add_argument("--espera-titulo", type=float, default=25)
    ap.add_argument("--filmar-titulo", type=float, default=0, help="grava S segundos da abertura em titulo.mp4")
    ap.add_argument("--titulo-quadros", type=int, default=0, help="fotos extras da abertura animada")
    a = ap.parse_args()
    a.saida.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        copia = montar(Path(td))
        t = Tela(copia, a.saida)
        try:
            time.sleep(a.espera_titulo)
            t.tecla("Return")   # pula a abertura / tela de "aperte start"
            time.sleep(3)
            t.foto("1_titulo.png")
            if a.filmar_titulo:
                t.filmar(a.filmar_titulo, "titulo.mp4")
            if a.titulo_quadros:
                for i in range(a.titulo_quadros):   # o titulo e animado: varias fotos seguidas
                    time.sleep(0.25)
                    t.foto(f"1_titulo_{i}.png")
            t.tecla("Down", ITENS_MENU[a.modo])
            t.tecla("Return")
            time.sleep(4)
            t.foto("2_selecao.png")
            t.tecla("Return")   # P1 escolhe o lutador da 1a casa
            time.sleep(1.5)
            if a.modo in ("versus", "assistir"):
                t.tecla("Right")
                t.tecla("Return")   # o 2o lutador (no Versus a vez passa para o P1 só se o P2 não estiver jogando)
                time.sleep(1.5)
            time.sleep(2)
            t.foto("3_mapa.png")
            for i in range(a.direita):
                t.tecla("Right", pausa=1.0)
                t.foto(f"4_mapa_{i + 1}.png")
            t.tecla("Return")
            time.sleep(1.2)
            t.foto("4v_vs.png")   # tela de VS (o motor mostra uns 2,5 s)
            time.sleep(12.8)
            t.foto("5_luta.png")
            if a.filmar:
                t.filmar(a.filmar)
        finally:
            t.fechar()
    print("pronto:", a.saida)


if __name__ == "__main__":
    main()
