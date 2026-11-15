"""Teste automático do Pengaró dentro do IKEMEN GO (um robô aperta os botões e confere o resultado).

Uso:  python ferramentas/testar_pengaro.py [--lutador gutto]          (roda DENTRO do Windows Sandbox: padrão)
      python ferramentas/testar_pengaro.py --local [CAMINHO_DO_MOTOR]  (abre o motor nesta máquina; só no PC do Breno)
      python3 ferramentas/testar_pengaro.py --linux [CAMINHO_DO_MOTOR]  (Linux sem tela: Xvfb + Mesa llvmpipe; padrão
              quando o sistema é Linux. Sem caminho, usa ~/.cache/nazafight/ikemen e baixa o IKEMEN GO Linux se faltar.
              Precisa de xvfb-run e do Mesa: apt install xvfb libgl1-mesa-dri. Assim o teste roda na nuvem, sem o PC.)

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
import urllib.request
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
IKEMEN_LINUX = "https://github.com/ikemen-engine/Ikemen-GO/releases/download/v1.0.0/Ikemen_GO-v1.0.0-linux.zip"
INI_LINUX = {"MasterVolume": "0", "PauseMasterVolume": "0", "Fullscreen": "0", "VSync": "0"}  # = sandbox.INI_PADRAO
CMDS = ["x", "y", "a", "b", "c", "holdfwd", "holdback", "holdup", "holddown", "agarrao_whisky", "garrafa_x",
        "garrafa_y", "role_a", "role_b", "sombra_x", "sombra_y", "sombra_a", "sombra_b", "despertar", "FF", "rolar",
        "afastar", "golaco", "golpe_216", "golpe_246", "golpe_201", "golpe_231", "golpe_1400", "golpe_1401",
        "golpe_1500", "golpe_1501", "golpe_3200", "bola_fraca", "bola_forte", "parry", "parry_baixo"]
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
    linux = "--linux" in args or (sys.platform.startswith("linux") and not local)
    if "--linux" in args:
        args.remove("--linux")
    if linux:
        motor = Path(args[0]) if args else motor_linux()
        if not (motor / "Ikemen_GO_Linux").exists():
            sys.exit(f"Não achei o Ikemen_GO_Linux em {motor}.")
    else:
        motor = Path(args[0]) if args else Path(os.environ["USERPROFILE"]) / "JogoDeLuta" / "ikemen"
        if not (motor / "Ikemen_GO.exe").exists():
            sys.exit(f"Não achei o Ikemen_GO.exe em {motor}. Abra o jogo uma vez pelo atalho para instalar o motor.")
    tmp = Path(tempfile.mkdtemp(prefix="teste_pengaro_"))
    try:
        if linux:
            texto = rodar_linux(motor, lutador, tmp)
        else:
            texto = rodar_local(motor, lutador, tmp) if local else rodar_sandbox(motor, lutador, tmp)
        print(texto)
        passou, falhou = texto.count("  PASS "), texto.count("  FAIL ")
        print(f"\nRESUMO: {passou} verificações passaram, {falhou} falharam.")
        sys.exit(1 if falhou or "ERRO NO ROBO" in texto else 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def preparar(destino, motor, lutador, saida_lua, filtro="", acelera=4):
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
                     .replace("@LUTADOR@", lutador)
                     .replace("@FILTRO@", filtro).replace("@ACCEL@", str(acelera)),
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
    preparar(copia, motor, lutador, saida.as_posix(), filtro=os.environ.get("NAZA_FILTRO", ""))  # NAZA_FILTRO: só os roteiros com esse texto no nome
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


def motor_linux():
    """IKEMEN GO Linux em ~/.cache/nazafight/ikemen (baixa o v1.0.0 na primeira vez, o mesmo do atalho do Windows)."""
    motor = Path.home() / ".cache" / "nazafight" / "ikemen"
    if not (motor / "Ikemen_GO_Linux").exists():
        print(f"Baixando o IKEMEN GO Linux para {motor}...", flush=True)
        motor.parent.mkdir(parents=True, exist_ok=True)
        zipado = motor.parent / "ikemen-linux.zip"
        urllib.request.urlretrieve(IKEMEN_LINUX, zipado)
        with zipfile.ZipFile(zipado) as z:
            z.extractall(motor)
        zipado.unlink()
        (motor / "Ikemen_GO_Linux").chmod(0o755)
    if not (motor / "save" / "config.ini").exists() and shutil.which("xvfb-run"):
        # o config.ini só nasce na 1ª abertura: abre o motor uns segundos para ele existir (ajustar_ini depende dele)
        print("Primeira abertura do motor para criar o save/config.ini...", flush=True)
        subprocess.run(["timeout", "20", "xvfb-run", "-a", "./Ikemen_GO_Linux"], cwd=motor, env=ambiente_linux(motor),
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return motor


def ambiente_linux(motor):
    return {**os.environ, "LIBGL_ALWAYS_SOFTWARE": "1", "GALLIUM_DRIVER": "llvmpipe", "SDL_AUDIODRIVER": "dummy",
            "LD_LIBRARY_PATH": f"{motor / 'lib'}:{os.environ.get('LD_LIBRARY_PATH', '')}"}


def ajustar_ini(copia):
    """Som mudo, janela e sem VSync (a luta corre o mais rápido que o llvmpipe deixa). O config.ini nasce na 1ª abertura."""
    ini = copia / "save" / "config.ini"
    if not ini.exists():
        return
    t = ini.read_text(encoding="utf-8")
    for k, v in INI_LINUX.items():
        t = re.sub(rf"(?m)^({re.escape(k)}\s*=\s*)[^\r\n]*", lambda m: m.group(1) + v, t)
    ini.write_text(t, encoding="utf-8")


def rodar_linux(motor, lutador, tmp):
    """Igual ao --local, mas no Linux sem monitor: tela virtual do Xvfb e OpenGL por software (Mesa llvmpipe)."""
    if not shutil.which("xvfb-run"):
        sys.exit("falta o xvfb-run (apt install xvfb libgl1-mesa-dri)")
    copia = tmp / "motor"
    shutil.copytree(motor, copia, symlinks=True)
    for nome in (lutador, "hazaki"):
        shutil.copytree(RAIZ / "chars" / nome, copia / "chars" / nome, dirs_exist_ok=True)
    # layout Nazafights como o .bat instala (motif/INSTALAR.md): sem ele o HUD do motor puro mostra o retrato HD gigante
    if (RAIZ / "motif" / "nazafight" / "system.def").exists():
        shutil.copytree(RAIZ / "motif" / "nazafight", copia / "data" / "nazafight", dirs_exist_ok=True)
        INI_LINUX["Motif"] = "data/nazafight/system.def"
    saida = tmp / "resultado.txt"
    preparar(copia, motor, lutador, saida.as_posix(), filtro=os.environ.get("NAZA_FILTRO", ""))  # NAZA_FILTRO: só os roteiros com esse texto no nome
    ajustar_ini(copia)
    amb = ambiente_linux(copia)
    print("Rodando o robô no Linux (Xvfb + llvmpipe; leva alguns minutos)...", flush=True)
    t0 = time.time()
    proc = subprocess.Popen(["xvfb-run", "-a", "-s", "-screen 0 1280x720x24", "./Ikemen_GO_Linux"] + argumentos(lutador),
                            cwd=copia, env=amb, stdout=open(tmp / "motor_log.txt", "w"), stderr=subprocess.STDOUT,
                            start_new_session=True)
    limite = time.time() + 2400
    while time.time() < limite and proc.poll() is None:
        if saida.exists() and re.search(r"^FIM|ERRO NO ROBO", saida.read_text(encoding="utf-8"), re.M):
            break
        time.sleep(2)
    try:
        os.killpg(proc.pid, 9)  # leva junto o Xvfb que o xvfb-run abriu
    except ProcessLookupError:
        pass
    print(f"motor parou em {time.time() - t0:.0f} s", flush=True)
    if not saida.exists():
        sys.exit("O robô não escreveu resultado: o motor fechou antes de começar.\n" +
                 (tmp / "motor_log.txt").read_text(errors="replace")[-3000:])
    return saida.read_text(encoding="utf-8")


if __name__ == "__main__":
    main()
