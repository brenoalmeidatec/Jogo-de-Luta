#!/usr/bin/env python3
"""Leitura dos golpes de um lutador para a IA da CPU (ferramentas/ia_cpu.py).

  python3 ferramentas/ia_analise.py pengaro        mostra a tabela de golpes que a IA enxerga

Para cada [State -1] do .cmd que troca de estado por comando, descobre:
  - que comandos precisam estar apertados (o que a IA tem de "apertar" para sair aquele golpe);
  - em que forma vale (base, despertado ou as duas), se é no chão ou no ar, quanto de barra pede;
e, no .cns e no .air, o que o golpe é: tipo (S/C/A), se é golpe (HitDef), agarrão (p2stateno), projétil
(Projectile ou Helper que bate), dano, quantos tiques até a caixa de ataque ligar (início) e até onde a caixa
alcança (frente e altura, já na escala do lutador).
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def ler(p):
    return Path(p).read_bytes().decode("utf-8", "replace").replace("\r\n", "\n")


def statedefs(txt):
    """{numero: texto do bloco} de cada [Statedef N]."""
    marcas = [(m.start(), int(m.group(1))) for m in re.finditer(r"(?mi)^\[Statedef\s+(-?\d+)\s*\]", txt)]
    out = {}
    for k, (ini, n) in enumerate(marcas):
        fim = marcas[k + 1][0] if k + 1 < len(marcas) else len(txt)
        out.setdefault(n, txt[ini:fim])
    return out


def controladores(bloco):
    """[(titulo, {chave: [valores]}, linhas cruas)] de cada [State ...] dentro de um statedef."""
    partes = re.split(r"(?m)^(\[State[^\]]*\])", bloco)
    out = []
    for i in range(1, len(partes), 2):
        corpo = partes[i + 1]
        kv = {}
        for ln in corpo.split("\n"):
            s = ln.split(";")[0].strip()
            if "=" not in s:
                continue
            k, v = s.split("=", 1)
            kv.setdefault(k.strip().lower(), []).append(v.strip())
        out.append((partes[i], kv, corpo))
    return out


def cabecalho(bloco):
    kv = {}
    for ln in bloco.split("\n")[1:]:
        if ln.startswith("[State"):
            break
        s = ln.split(";")[0].strip()
        if "=" in s:
            k, v = s.split("=", 1)
            kv[k.strip().lower()] = v.strip()
    return kv


def acoes_air(txt):
    """{acao: [(tempo, [clsn1 caixas])]} do .air (só o que a IA precisa)."""
    out = {}
    for m in re.finditer(r"(?mi)^\[Begin Action\s+(\d+)\s*\]\s*\n(.*?)(?=^\[Begin Action|\Z)", txt, re.S):
        n = int(m.group(1))
        elems = []
        caixas_pend = []
        caixas_def = []
        modo = None
        for ln in m.group(2).split("\n"):
            s = ln.split(";")[0].strip()
            if not s:
                continue
            low = s.lower()
            if low.startswith("clsn1default"):
                modo = "def1"
                caixas_def = []
                continue
            if low.startswith("clsn1:") or low.startswith("clsn1 :"):
                modo = "c1"
                caixas_pend = []
                continue
            if low.startswith("clsn2"):
                modo = "c2"
                continue
            if low.startswith("clsn1["):
                nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", s.split("=", 1)[1])]
                if len(nums) >= 4:
                    (caixas_def if modo == "def1" else caixas_pend).append(nums[:4])
                continue
            if low.startswith("clsn") or low.startswith("loopstart") or low.startswith("interpolate"):
                continue
            nums = s.split(",")
            if len(nums) >= 5 and re.match(r"^-?\d+$", nums[0].strip()):
                try:
                    t = int(nums[4].strip())
                except ValueError:
                    t = 1
                cx = caixas_pend if caixas_pend else caixas_def
                elems.append((t, list(cx)))
                caixas_pend = []
        out[n] = elems
    return out


def escala(cns):
    xs = re.search(r"(?mi)^xscale\s*=\s*([\d.]+)", cns)
    ys = re.search(r"(?mi)^yscale\s*=\s*([\d.]+)", cns)
    fr = re.search(r"(?mi)^ground\.front\s*=\s*([\d.]+)", cns)
    return float(xs.group(1)) if xs else 1.0, float(ys.group(1)) if ys else 1.0, float(fr.group(1)) if fr else 16


def medir_anim(elems, sx, sy):
    """(inicio, ativo, total, alcance_x, topo_y, base_y) da animação; None se não tem caixa de ataque."""
    t = 0
    ini = None
    x2 = -1e9
    topo = 1e9
    base = -1e9
    ativo = 0
    total = 0
    for dur, cx in elems:
        d = dur if dur > 0 else 1
        if cx:
            if ini is None:
                ini = t
            ativo += d
            for c in cx:
                xa, ya, xb, yb = c
                x2 = max(x2, max(xa, xb) * sx)
                topo = min(topo, min(ya, yb) * sy)
                base = max(base, max(ya, yb) * sy)
        t += d
        total += d if dur > 0 else 0
    if ini is None:
        return None
    return ini, ativo, total, x2, topo, base


def analisar(nome, pasta=None):
    pasta = Path(pasta) if pasta else RAIZ / "chars" / nome
    cmd = ler(pasta / f"{nome}.cmd")
    cns = ler(pasta / f"{nome}.cns")
    air = acoes_air(ler(pasta / f"{nome}.air"))
    sds = statedefs(cns)
    sx, sy, frente = escala(cns)
    nomes_cmd = []
    for m in re.finditer(r'(?mi)^\s*name\s*=\s*"([^"]+)"', cmd.split("[Statedef -1]")[0]):
        if m.group(1) not in nomes_cmd:
            nomes_cmd.append(m.group(1))
    menos1 = statedefs(cmd).get(-1, "")
    golpes = []
    for titulo, kv, corpo in controladores(menos1):
        if kv.get("type", [""])[0].lower() != "changestate":
            continue
        trig = "\n".join(ln for ln in corpo.split("\n") if ln.strip().lower().startswith("trigger"))
        pos = re.findall(r'command\s*=\s*"([^"]+)"', trig)
        if not pos:
            continue
        try:
            alvo = int(kv["value"][0])
        except (ValueError, KeyError):
            continue
        g = {"titulo": titulo.strip("[]").split(",", 1)[-1].strip(), "estado": alvo, "cmds": sorted(set(pos)),
             "forma": "as duas", "chao": True, "ar": False, "barra": 0, "trig": trig}
        tl = trig.lower().replace(" ", "")
        if "var(20)>0" in tl:
            g["forma"] = "despertado"
        elif "var(20)=0" in tl:
            g["forma"] = "base"
        if "statetype=a" in tl and "statetype!=a" not in tl:
            g["chao"], g["ar"] = False, True
        m = re.search(r"power>=(\d+)", tl)
        if m:
            g["barra"] = int(m.group(1))
        elif "power>=powermax" in tl:
            g["barra"] = 3000
        g.update(descrever_estado(alvo, sds, air, sx, sy))
        g["alcance"] = round(g["x2"] - frente, 1) if g.get("x2") is not None else None
        golpes.append(g)
    return {"nome": nome, "comandos": nomes_cmd, "golpes": golpes, "frente": frente}


def descrever_estado(n, sds, air, sx, sy, fundo=0):
    """Propriedades do estado n (segue ChangeState de 1º passo sem caixa e Helper que bate)."""
    bloco = sds.get(n)
    info = {"tipo": None, "hitdef": False, "agarrao": False, "projetil": False, "dano": 0, "inicio": None,
            "total": None, "x2": None, "topo": None, "base": None, "attr": "", "derruba": False}
    if not bloco:
        return info
    cab = cabecalho(bloco)
    info["tipo"] = cab.get("type", "S").upper()[:1]
    anim = cab.get("anim")
    ctls = controladores(bloco)
    for titulo, kv, corpo in ctls:
        tp = kv.get("type", [""])[0].lower()
        if tp == "hitdef":
            info["hitdef"] = True
            attr = kv.get("attr", [""])[0].replace(" ", "").upper()
            info["attr"] = info["attr"] or attr
            if "p2stateno" in kv or "T" in attr.split(",", 1)[-1]:
                info["agarrao"] = True
            try:
                dmg = int(re.findall(r"-?\d+", kv.get("damage", ["0"])[0])[0])
            except (IndexError, ValueError):
                dmg = 0
            info["dano"] = max(info["dano"], dmg)
            if kv.get("fall", ["0"])[0].strip() in ("1",) or "trip" in kv.get("ground.type", [""])[0].lower():
                info["derruba"] = True
        elif tp == "projectile":
            info["projetil"] = True
            info["hitdef"] = True
        elif tp == "helper" and fundo < 2:
            try:
                hs = int(re.findall(r"\d+", kv.get("stateno", ["0"])[0])[0])
            except (IndexError, ValueError):
                hs = 0
            h = descrever_estado(hs, sds, air, sx, sy, fundo + 1)
            if h["hitdef"]:
                info["projetil"] = True
                info["hitdef"] = True
                info["dano"] = max(info["dano"], h["dano"])
        elif tp == "changeanim" and anim is None:
            anim = kv.get("value", [None])[0]
    if anim is not None:
        try:
            a = int(re.findall(r"-?\d+", str(anim))[0])
        except (IndexError, ValueError):
            a = None
        if a is not None and a in air:
            med = medir_anim(air[a], sx, sy)
            if med:
                info["inicio"], _, info["total"], info["x2"], info["topo"], info["base"] = med
            else:
                info["total"] = sum(max(d, 0) for d, _ in air[a])
    if not info["hitdef"] and fundo == 0:
        # golpe que entra num estado de preparo e troca para o de verdade (ex.: corrida que vira chute)
        for titulo, kv, corpo in ctls:
            if kv.get("type", [""])[0].lower() == "changestate":
                try:
                    prox = int(kv["value"][0])
                except (ValueError, KeyError):
                    continue
                if prox not in (0, 11, 51, 52) and prox != n:
                    h = descrever_estado(prox, sds, air, sx, sy, fundo + 1)
                    if h["hitdef"]:
                        for k in ("hitdef", "agarrao", "projetil", "dano", "attr", "derruba", "x2", "topo", "base"):
                            info[k] = h[k]
                        if h["inicio"] is not None:
                            info["inicio"] = (info["total"] or 0) + h["inicio"]
                        break
    return info


def mostrar(nome):
    a = analisar(nome)
    print(f"== {nome}: {len(a['golpes'])} golpes por comando; comandos {len(a['comandos'])}")
    for g in a["golpes"]:
        print(f"{g['estado']:>5} {g['titulo'][:26]:26} {'+'.join(g['cmds'])[:22]:22} {g['forma'][:5]:5} "
              f"{'ar ' if g['ar'] else 'chao'} b{g['barra']:<4} t{g['tipo']} {g['attr'][:6]:6} "
              f"{'AGR' if g['agarrao'] else '   '}{'PRJ' if g['projetil'] else '   '}{'DER' if g['derruba'] else '   '} "
              f"d{g['dano']:<4} ini{g['inicio']} tot{g['total']} alc{g['alcance']} topo{None if g['topo'] is None else round(g['topo'])}"
              f" base{None if g['base'] is None else round(g['base'])}")


if __name__ == "__main__":
    for n in sys.argv[1:] or ["pengaro"]:
        mostrar(n)
