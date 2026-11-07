#!/usr/bin/env python3
"""Roda uma luta CPU contra CPU numa cópia do motor e filma a janela, para conferir as animações na tela de verdade.

  python ferramentas/filmar_luta.py PASTA_DE_SAIDA [--segundos 40] [--despertar 10]

O jogo instalado não é tocado: o motor é copiado para uma pasta temporária com o Pengaró e o Hazaki de chars/.
--despertar N ativa o Despertar do Pengaró uma vez só, aos N segundos de luta: enche a barra e entra no estado 2000,
como o jogador faria, para filmar a cutscene, a forma endiabrada e a volta ao normal quando o tempo acaba.
Grava quadro_NNNN.png e uma folha de contato.
"""
import ctypes
import ctypes.wintypes as wt
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageGrab

RAIZ = Path(__file__).resolve().parent.parent
u32 = ctypes.windll.user32


def janela_do_processo(pid):
    achada = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cada(hwnd, _):
        dono = wt.DWORD()
        u32.GetWindowThreadProcessId(hwnd, ctypes.byref(dono))
        if dono.value == pid and u32.IsWindowVisible(hwnd):
            achada.append(hwnd)
        return True

    u32.EnumWindows(cada, 0)
    return achada[0] if achada else None


def area_cliente(hwnd):
    r = wt.RECT()
    u32.GetClientRect(hwnd, ctypes.byref(r))
    p = wt.POINT(0, 0)
    u32.ClientToScreen(hwnd, ctypes.byref(p))
    return p.x, p.y, p.x + r.right, p.y + r.bottom


def main():
    args = sys.argv[1:]
    saida = Path(args[0])
    segundos = float(args[args.index("--segundos") + 1]) if "--segundos" in args else 40
    despertar = float(args[args.index("--despertar") + 1]) if "--despertar" in args else None
    saida.mkdir(parents=True, exist_ok=True)
    motor = Path(os.environ["USERPROFILE"]) / "JogoDeLuta" / "ikemen"
    tmp = Path(tempfile.mkdtemp(prefix="filme_"))
    try:
        copia = tmp / "motor"
        shutil.copytree(motor, copia)
        for nome in ("pengaro", "hazaki"):
            shutil.copytree(RAIZ / "chars" / nome, copia / "chars" / nome, dirs_exist_ok=True)
        if despertar is not None:
            cmd = copia / "chars/pengaro/pengaro.cmd"
            txt = cmd.read_text(encoding="utf-8").replace("\r\n", "\n")
            # var(50) não é usada pelo Pengaró: marca que a ativação do filme já aconteceu, para não religar.
            quando = (f"triggerall = roundstate = 2 && var(50) = 0 && var(20) = 0\n"
                      f"trigger1 = gametime >= {int(despertar * 60)} && statetype = S && ctrl\n")
            liga = ("[State -1, Filme marca o Despertar feito]\ntype = VarSet\ntrigger1 = stateno = 2000\nvar(50) = 1\n\n"
                    f"[State -1, Filme enche a barra]\ntype = PowerSet\n{quando}value = powermax\n\n"
                    f"[State -1, Filme ativa o Despertar]\ntype = ChangeState\n{quando}value = 2000\n\n")
            cmd.write_text(txt.replace("[Statedef -1]\n\n", "[Statedef -1]\n\n" + liga, 1), encoding="utf-8", newline="\n")
        proc = subprocess.Popen([str(copia / "Ikemen_GO.exe"), "-p1", "pengaro", "-p1.ai", "8", "-p2", "hazaki",
                                 "-p2.ai", "8", "-s", "stages/stage0-720.def", "-rounds", "1"],
                                cwd=copia, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        hwnd = None
        for _ in range(60):
            hwnd = janela_do_processo(proc.pid)
            if hwnd:
                break
            time.sleep(0.5)
        if not hwnd:
            sys.exit("a janela do jogo não apareceu")
        time.sleep(6)  # passa pela introdução
        quadros = []
        fim = time.time() + segundos
        while time.time() < fim and proc.poll() is None:
            img = ImageGrab.grab(area_cliente(hwnd))
            img.save(saida / f"quadro_{len(quadros):04d}.png")
            quadros.append(img)
            time.sleep(0.25)
        proc.kill()
        if quadros:
            colunas = 6
            w, h = 320, 180
            folha = Image.new("RGB", (colunas * w, ((len(quadros) + colunas - 1) // colunas) * h))
            for i, q in enumerate(quadros):
                folha.paste(q.resize((w, h)), ((i % colunas) * w, (i // colunas) * h))
            folha.save(saida / "contato.png")
        print(f"{len(quadros)} quadros em {saida}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
