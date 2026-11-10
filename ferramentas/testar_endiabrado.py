"""Confere que a paleta 2 (botão y na seleção) faz o Pengaró começar endiabrado e ficar assim.
Uso: python ferramentas/testar_endiabrado.py [PAL]   (PAL = 1 ou 2; padrão 2). Usa uma cópia do motor, não toca o jogo instalado."""
import os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
pal = sys.argv[1] if len(sys.argv) > 1 else "2"
motor = Path(os.environ["USERPROFILE"]) / "JogoDeLuta" / "ikemen"
tmp = Path(tempfile.mkdtemp(prefix="teste_pal_"))
try:
    copia = tmp / "motor"
    shutil.copytree(motor, copia)
    for nome in ("pengaro", "hazaki"):
        shutil.copytree(RAIZ / "chars" / nome, copia / "chars" / nome, dirs_exist_ok=True)
    saida = tmp / "resultado.txt"
    dbg = copia / "external/script/debug.lua"
    dbg.write_text(dbg.read_text(encoding="utf-8") + "\n" + (RAIZ / "ferramentas/robo/paleta.lua").read_text(encoding="utf-8").replace("@SAIDA@", saida.as_posix()), encoding="utf-8")
    proc = subprocess.Popen([str(copia / "Ikemen_GO.exe"), "-p1", "pengaro", "-p1.pal", pal, "-p2", "hazaki", "-s", "stages/stage0-720.def"], cwd=copia, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    limite = time.time() + 300
    while time.time() < limite and proc.poll() is None:
        if saida.exists() and re.search(r"^FIM|ERRO NO ROBO", saida.read_text(encoding="utf-8"), re.M):
            break
        time.sleep(2)
    proc.kill()
    print(saida.read_text(encoding="utf-8") if saida.exists() else "sem resultado")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
