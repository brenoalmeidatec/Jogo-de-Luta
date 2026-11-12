"""Teste automático do Pengaró dentro do IKEMEN GO (um robô aperta os botões e confere o resultado).

Uso:  python ferramentas/testar_pengaro.py [--lutador gutto]          (roda DENTRO do Windows Sandbox: padrão)
      python ferramentas/testar_pengaro.py --local [CAMINHO_DO_MOTOR]  (abre o motor nesta máquina; só no PC do Breno)

Regra do dono (2026-11-10): no PC de teste o robô roda só na sandbox (ferramentas/sandbox.py), nunca na máquina local.

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
        "afastar", "golaco", "golpe_216", "golpe_246", "golpe_201", "golpe_231", "golpe_1400", "golpe_1401",
        "golpe_1500", "golpe_1501", "golpe_3200", "bola_fraca", "bola_forte", "parry"]
# comandos de toque do Hazak (ferramentas/gerar_hazaki.py). Só são injetados no .cmd que os define: os outros não mudam.
CMDS += ["bfd_a", "bfd_b", "bfd_x", "bfd_y", "df_x", "df_y", "fb_x", "fb_y", "fd_x", "fd_y", "df_a", "df_b", "db_a",
         "db_b", "bf_a", "bf_b", "bd_a", "bd_b", "db_x", "db_y", "bf_y"]
CMDS += ["baile", "caneta_x", "compasso_a"]  # CK: super do Ratão, Contragolpe e Pêndulo


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
    # fim natural do Despertar: o var(20) desce até 0 sozinho (a aura tem de apagar junto com a forma endiabrada)
    b += '[State -1, T_fimdesp]\ntype = VarSet\ntrigger1 = map(t_fimdesp) = 1 && var(20) > 40\nvar(20) = 40\n\n'
    if hazaki:
        b += ('[State -1, T_agacha]\ntype = ChangeState\nvalue = 11\ntriggerall = map(t_agacha) = 1\n'
              'trigger1 = statetype = S && ctrl\n\n')
        # defesa de verdade: com um golpe vindo (inguarddist) entra na guarda do motor (120) e o robô segura
        # "holdback"; com t_agacha, defende agachado
        b += ('[State -1, T_defende]\ntype = ChangeState\nvalue = 120\ntriggerall = map(t_defende) = 1\n'
              'triggerall = statetype != A\ntriggerall = stateno != [120,155]\n'
              'triggerall = map(t_agacha) = 0 || statetype = C\ntrigger1 = ctrl && inguarddist\n\n')
    assert "[Statedef -1]\n\n" in txt, f"sem Statedef -1 em {arq}"
    arq.write_text(txt.replace("[Statedef -1]\n\n", "[Statedef -1]\n\n" + b, 1), encoding="utf-8", newline="\n")


def main():
    args = sys.argv[1:]
    lutador = "pengaro"
    if "--lutador" in args:
        i = args.index("--lutador")
        lutador = args[i + 1]
        del args[i:i + 2]
    local = "--local" in args
    if local:
        args.remove("--local")
    motor = Path(args[0]) if args else Path(os.environ["USERPROFILE"]) / "JogoDeLuta" / "ikemen"
    if not (motor / "Ikemen_GO.exe").exists():
        sys.exit(f"Não achei o Ikemen_GO.exe em {motor}. Abra o jogo uma vez pelo atalho para instalar o motor.")
    tmp = Path(tempfile.mkdtemp(prefix="teste_pengaro_"))
    try:
        texto = rodar_local(motor, lutador, tmp) if local else rodar_sandbox(motor, lutador, tmp)
        print(texto)
        passou, falhou = texto.count("  PASS "), texto.count("  FAIL ")
        print(f"\nRESUMO: {passou} verificações passaram, {falhou} falharam.")
        sys.exit(1 if falhou or "ERRO NO ROBO" in texto else 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def preparar(destino, motor, lutador, saida_lua):
    """Escreve em destino/ o que substitui o motor: os .cmd injetados e o debug.lua com o robô."""
    for nome in (lutador, "hazaki"):
        arq = destino / "chars" / nome / f"{nome}.cmd"
        arq.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(RAIZ / "chars" / nome / f"{nome}.cmd", arq)
        injetar(arq, nome == "hazaki")
    debug = destino / "external/script/debug.lua"
    debug.parent.mkdir(parents=True, exist_ok=True)
    debug.write_text((motor / "external/script/debug.lua").read_text(encoding="utf-8") + "\n" +
                     (RAIZ / "ferramentas/robo/robo.lua").read_text(encoding="utf-8").replace("@SAIDA@", saida_lua)
                     .replace("@LUTADOR@", lutador),
                     encoding="utf-8")


def argumentos(lutador):
    return ["-p1", lutador, "-p2", "hazaki", "-s", "stages/stage0-720.def"]


def rodar_sandbox(motor, lutador, tmp):
    import sandbox
    if motor.resolve() != sandbox.MOTOR.resolve():
        sys.exit(f"na sandbox o motor é sempre {sandbox.MOTOR}")
    por_cima, saida = tmp / "por_cima", tmp / "saida"
    preparar(por_cima, motor, lutador, "C:/nf/saida/resultado.txt")
    print("Rodando o robô dentro do Windows Sandbox (OpenGL por software; leva vários minutos)...", flush=True)
    sandbox.rodar([lutador, "hazaki"], argumentos(lutador), saida, por_cima=por_cima,
                  fim_arquivo="resultado.txt", fim_regex="^FIM|ERRO NO ROBO", espera=2400)
    res = saida / "resultado.txt"
    if not res.exists():
        log = saida / "log_sandbox.txt"
        sys.exit("O robô não escreveu resultado na sandbox.\n" + (log.read_text(errors="replace") if log.exists() else ""))
    return res.read_text(encoding="utf-8")


def rodar_local(motor, lutador, tmp):
    copia = tmp / "motor"
    shutil.copytree(motor, copia)
    for nome in (lutador, "hazaki"):
        shutil.copytree(RAIZ / "chars" / nome, copia / "chars" / nome, dirs_exist_ok=True)
    saida = tmp / "resultado.txt"
    preparar(copia, motor, lutador, saida.as_posix())
    print("Rodando o robô (a janela do jogo abre sozinha)...")
    proc = subprocess.Popen([str(copia / "Ikemen_GO.exe")] + argumentos(lutador), cwd=copia,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    limite = time.time() + 1200
    while time.time() < limite and proc.poll() is None:
        if saida.exists() and re.search(r"^FIM|ERRO NO ROBO", saida.read_text(encoding="utf-8"), re.M):
            break
        time.sleep(2)
    proc.kill()
    if not saida.exists():
        sys.exit("O robô não escreveu resultado: o motor fechou antes de começar.")
    return saida.read_text(encoding="utf-8")


if __name__ == "__main__":
    main()
