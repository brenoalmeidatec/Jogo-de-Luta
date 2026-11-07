"""Teste automático do Pengaró dentro do IKEMEN GO (um robô aperta os botões e confere o resultado).

Uso:  python ferramentas/testar_pengaro.py            (usa o motor de %USERPROFILE%\\JogoDeLuta\\ikemen)
      python ferramentas/testar_pengaro.py CAMINHO    (outra pasta do motor)

Faz uma cópia do motor numa pasta temporária (o jogo instalado não é tocado), instala nela o Pengaró e o Hazaki da
pasta chars/, injeta no .cmd comandos que um script Lua aciona (AssertCommand, PosSet) e roda uma luta de
Pengaró contra um boneco parado, em velocidade acelerada. O roteiro (ferramentas/robo/robo.lua) testa correntes,
kombos, agarrões, projéteis, Rolê por Trás (inclusive no canto), Despertar e os golpes exclusivos. No fim imprime
PASS/FAIL e o dano de cada golpe. A janela do jogo abre sozinha e fecha no fim.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CMDS = ["x", "y", "a", "b", "c", "holdfwd", "holdback", "holdup", "holddown", "agarrao_whisky", "garrafa_x",
        "garrafa_y", "role_a", "role_b", "sombra_x", "sombra_y", "sombra_a", "sombra_b", "despertar", "FF", "rolar",
        "afastar", "golaco", "golpe_216", "golpe_246", "golpe_201", "golpe_231", "bola_fraca", "bola_forte", "parry"]


def injetar(arq, hazaki):
    """Põe no começo do [Statedef -1] os controladores que o script Lua aciona por Map."""
    txt = arq.read_text(encoding="utf-8").replace("\r\n", "\n")
    nomes = set(re.findall(r'^name = "([^"]+)"', txt, re.M))
    b = ""
    for c in CMDS:
        if c in nomes:
            b += f'[State -1, T_{c}]\ntype = AssertCommand\ntrigger1 = map(t_{c}) = 1\nname = "{c}"\nbuffer.time = 1\n\n'
    b += '[State -1, T_pos]\ntype = PosSet\ntrigger1 = map(t_pos) = 1\nx = map(t_posx) - 1000\n\n'
    b += '[State -1, T_v10]\ntype = VarSet\ntrigger1 = map(t_v10) = 1\nvar(10) = 2\n\n'
    b += '[State -1, T_desperto]\ntype = VarSet\ntrigger1 = map(t_desperto) = 1\nvar(20) = 600\n\n'
    if hazaki:
        b += ('[State -1, T_agacha]\ntype = ChangeState\nvalue = 11\ntriggerall = map(t_agacha) = 1\n'
              'trigger1 = statetype = S && ctrl\n\n')
    assert "[Statedef -1]\n\n" in txt, f"sem Statedef -1 em {arq}"
    arq.write_text(txt.replace("[Statedef -1]\n\n", "[Statedef -1]\n\n" + b, 1), encoding="utf-8", newline="\n")


def main():
    motor = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(os.environ["USERPROFILE"]) / "JogoDeLuta" / "ikemen"
    if not (motor / "Ikemen_GO.exe").exists():
        sys.exit(f"Não achei o Ikemen_GO.exe em {motor}. Abra o jogo uma vez pelo atalho para instalar o motor.")
    tmp = Path(tempfile.mkdtemp(prefix="teste_pengaro_"))
    try:
        copia = tmp / "motor"
        shutil.copytree(motor, copia)
        for nome in ("pengaro", "hazaki"):
            shutil.copytree(RAIZ / "chars" / nome, copia / "chars" / nome, dirs_exist_ok=True)
            injetar(copia / "chars" / nome / f"{nome}.cmd", nome == "hazaki")
        saida = tmp / "resultado.txt"
        debug = copia / "external/script/debug.lua"
        debug.write_text(debug.read_text(encoding="utf-8") + "\n" +
                         (RAIZ / "ferramentas/robo/robo.lua").read_text(encoding="utf-8").replace("@SAIDA@", saida.as_posix()),
                         encoding="utf-8")
        print("Rodando o robô (a janela do jogo abre sozinha)...")
        proc = subprocess.Popen([str(copia / "Ikemen_GO.exe"), "-p1", "pengaro", "-p2", "hazaki", "-s",
                                 "stages/stage0-720.def"], cwd=copia, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        limite = time.time() + 1200
        while time.time() < limite and proc.poll() is None:
            if saida.exists() and re.search(r"^FIM|ERRO NO ROBO", saida.read_text(encoding="utf-8"), re.M):
                break
            time.sleep(2)
        proc.kill()
        if not saida.exists():
            sys.exit("O robô não escreveu resultado: o motor fechou antes de começar.")
        texto = saida.read_text(encoding="utf-8")
        print(texto)
        passou, falhou = texto.count("  PASS "), texto.count("  FAIL ")
        print(f"\nRESUMO: {passou} verificações passaram, {falhou} falharam.")
        sys.exit(1 if falhou or "ERRO NO ROBO" in texto else 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
