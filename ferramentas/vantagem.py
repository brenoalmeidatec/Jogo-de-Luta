#!/usr/bin/env python3
"""Tabela de vantagem golpe a golpe (auditoria do Breno, #32, 24/11, item 7), medida no motor, na nuvem.

  python3 ferramentas/vantagem.py pengaro [hazaki ck ...]   [--json SAIDA.json] [--estados 200,210]

Para cada golpe em pé ou agachado que tem HitDef (200 a 4999, fora agarrão), o P1 entra direto no estado (sem
comando, sem cancelar em nada) colado no Hazak parado (P2). Uma vez o Hazak defende e outra apanha. O robô
(ferramentas/robo/vantagem.lua) anota o tique do contato e o tique em que cada um volta a ter controle:
vantagem = quando o P2 se solta - quando o P1 se solta. Positivo: quem bateu age primeiro.

Mesma cópia do motor do robô de luta (~/.cache/nazafight/ikemen, Xvfb + llvmpipe). Nada roda no PC.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from testar_pengaro import RAIZ, INI_LINUX, ambiente_linux, motor_linux, ajustar_ini, injetar  # noqa: E402

RE_EST = re.compile(r"^EST (\d+) (def|hit) (.*)$", re.M)


def golpes(lutador):
    """Estados de golpe no chão (S/C, movetype A) com HitDef que não é agarrão, de 200 a 4999."""
    txt = (RAIZ / "chars" / lutador / f"{lutador}.cns").read_text(encoding="utf-8", errors="replace")
    blocos = re.split(r"(?m)^\[Statedef ", txt)[1:]
    saida = {}
    for b in blocos:
        m = re.match(r"(-?\d+)\]", b)
        n = int(m.group(1))
        cab = b.split("\n[State", 1)[0].lower()
        if not 200 <= n <= 4999 or "movetype = a" not in cab or not re.search(r"type = [sc]\b", cab):
            continue
        hds = re.findall(r"(?ms)^type\s*=\s*HitDef\s*$(.*?)(?=^\[|\Z)", b)
        if not hds:
            continue
        if any(re.search(r"(?m)^attr\s*=\s*[SCA]+\s*,\s*\w*T", h, re.I) for h in hds):
            continue  # agarrão
        h = hds[0]
        num = lambda k: (re.search(rf"(?m)^{re.escape(k)}\s*=\s*(-?\d+)", h) or [None, None])[1]
        saida[n] = {"hittime": num("ground.hittime"), "guard_hittime": num("guard.hittime"),
                    "dano": num("damage"), "anim": (re.search(r"(?m)^animtype\s*=\s*(\w+)", h) or [None, ""])[1],
                    "guardflag": (re.search(r"(?m)^guardflag\s*=\s*(\w+)", h) or [None, "MA"])[1]}
    return saida


def medir(lutador, estados, motor, tmp, baixos=()):
    copia = tmp / f"motor_{lutador}"
    shutil.copytree(motor, copia, symlinks=True)
    for nome in (lutador, "hazaki"):
        shutil.copytree(RAIZ / "chars" / nome, copia / "chars" / nome, dirs_exist_ok=True)
        arq = copia / "chars" / nome / f"{nome}.cmd"
        injetar(arq, nome == "hazaki")
        t = arq.read_text(encoding="utf-8")
        bloco = ('[State -1, T_st]\ntype = ChangeState\nvalue = map(t_st)\ntriggerall = map(t_st) > 0\n'
                 'trigger1 = ctrl && statetype != A\n\n')
        # defesa segura antes do golpe (como quem já está segurando para trás): fica na guarda 130/131 do motor
        bloco += ('[State -1, T_guarda]\ntype = ChangeState\nvalue = ifelse(map(t_agacha) = 1, 131, 130)\n'
                  'triggerall = map(t_guarda) = 1\ntriggerall = statetype != A\n'
                  'triggerall = stateno != [130, 131] && stateno != [150, 155]\ntrigger1 = ctrl || stateno = 140\n\n')
        arq.write_text(t.replace("[Statedef -1]\n\n", "[Statedef -1]\n\n" + bloco, 1), encoding="utf-8", newline="\n")
    # golpe baixo: na cópia de teste ele vira defensável em pé (a trava da defesa é a mesma em pé e agachado; o robô
    # não consegue segurar a guarda agachada sem controle de verdade)
    cns = copia / "chars" / lutador / f"{lutador}.cns"
    cns.write_text(re.sub(r"(?m)^guardflag\s*=\s*L\s*$", "guardflag = MA", cns.read_text(encoding="utf-8", errors="replace")),
                   encoding="utf-8")
    if (RAIZ / "motif" / "nazafight" / "system.def").exists():
        shutil.copytree(RAIZ / "motif" / "nazafight", copia / "data" / "nazafight", dirs_exist_ok=True)
        INI_LINUX["Motif"] = "data/nazafight/system.def"
    saida = tmp / f"vantagem_{lutador}.txt"
    debug = copia / "external/script/debug.lua"
    debug.write_text(debug.read_text(encoding="utf-8") + "\n" + (RAIZ / "ferramentas/robo/vantagem.lua").read_text(
        encoding="utf-8").replace("@SAIDA@", saida.as_posix()).replace("@ESTADOS@", ", ".join(map(str, estados)))
        .replace("@BAIXOS@", ", ".join(map(str, baixos))).replace("@ACCEL@", "4"), encoding="utf-8")
    ajustar_ini(copia)
    args = ["-p1", lutador, "-p2", "hazaki", "-s", "stages/stage0-720.def", "-rounds", "99"]
    proc = subprocess.Popen(["xvfb-run", "-a", "-s", "-screen 0 1280x720x24", "./Ikemen_GO_Linux"] + args, cwd=copia,
                            env=ambiente_linux(copia), stdout=open(tmp / f"log_{lutador}.txt", "w"),
                            stderr=subprocess.STDOUT, start_new_session=True)
    limite = time.time() + 60 + 6 * len(estados)
    while time.time() < limite and proc.poll() is None:
        if saida.exists() and re.search(r"^FIM|ERRO NO ROBO", saida.read_text(encoding="utf-8"), re.M):
            break
        time.sleep(2)
    try:
        os.killpg(proc.pid, 9)
    except ProcessLookupError:
        pass
    shutil.rmtree(copia, ignore_errors=True)
    return saida.read_text(encoding="utf-8") if saida.exists() else ""


def main():
    args = sys.argv[1:]
    js = None
    if "--json" in args:
        k = args.index("--json"); js = Path(args[k + 1]); del args[k:k + 2]
    so = None
    if "--estados" in args:
        k = args.index("--estados"); so = {int(x) for x in args[k + 1].split(",")}; del args[k:k + 2]
    lutadores = args or ["pengaro", "hazaki", "ck", "gutto", "raiclaven", "gbzin"]
    motor = motor_linux()
    tudo = {}
    tmp = Path(tempfile.mkdtemp(prefix="vantagem_"))
    try:
        for l in lutadores:
            info = golpes(l)
            estados = sorted(e for e in info if so is None or e in so)
            texto = medir(l, estados, motor, tmp)
            if "ERRO NO ROBO" in texto or os.environ.get("VANT_DEBUG"):
                print(texto[-2000:])
            res = {}
            for n, lado, resto in RE_EST.findall(texto):
                kv = dict(re.findall(r"(\w+)=(\S+)", resto))
                kv["nota"] = resto.split()[0] if "=" not in resto.split()[0] else ""
                res.setdefault(int(n), {})[lado] = kv
            tudo[l] = {str(e): {**info[e], **res.get(e, {})} for e in estados}
            print(f"\n== {l}: {len(estados)} golpes")
            print(f"{'estado':>6} {'anim':>7} {'dano':>5} {'hittime':>7} | {'acerto':>14} | {'defendido':>14}")
            for e in estados:
                r = tudo[l][str(e)]
                def cel(lado):
                    x = r.get(lado)
                    if not x:
                        return "-"
                    if "vantagem" in x:
                        v = int(x["vantagem"])
                        return f"{v:+d}" + (" caiu" if x.get("caiu") == "sim" else "") + ("" if x.get("res") == lado else f" ({x.get('res')})")
                    return x.get("nota") or "?"
                print(f"{e:>6} {r['anim'] or '':>7} {r['dano'] or '':>5} {r['hittime'] or '':>7} | {cel('hit'):>14} | {cel('def'):>14}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if js:
        js.parent.mkdir(parents=True, exist_ok=True)
        js.write_text(json.dumps(tudo, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
