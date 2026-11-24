#!/usr/bin/env python3
"""Robô do "som faltando" (meta 1.0, revisão final): todo som que um lutador pede tem de existir no arquivo certo.

  python3 ferramentas/conferir_sons.py [lutador ...]     sem nome: todos os de chars/ (menos teste_*)

O que confere, em cada .cns do lutador (os arquivos do st/cns do .def):
  - PlaySnd value = G,N       -> o .snd do próprio lutador (o do .def)
  - PlaySnd value = FG,N      -> o common.snd do motif (motif/nazafight/common.snd)
  - hitsound/guardsound = SG,N -> o .snd do lutador
  - hitsound/guardsound = G,N  -> o common.snd do motif (regra do IKEMEN: sem prefixo toca do comum)
  - hitsound/guardsound = FG,N -> o common.snd do motif
Valor que não é número fixo (expressão, ifelse) entra na conta de "dinâmicos" e não é conferido.
Som que não existe no IKEMEN não dá erro: só fica mudo. Por isso este robô.

Sai com código 1 se faltar algum som.
"""
import re
import struct
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
COMUM = RAIZ / "motif" / "nazafight" / "common.snd"


def ler_snd(arq):
    """Conjunto de (grupo, número) de um .snd do Elecbyte (versão 1.01)."""
    dados = Path(arq).read_bytes()
    if not dados.startswith(b"ElecbyteSnd"):
        raise ValueError(f"{arq} não é um .snd do Elecbyte")
    total, pos = struct.unpack_from("<II", dados, 16)
    sons = set()
    for _ in range(total):
        if pos <= 0 or pos + 16 > len(dados):
            break
        prox, _tam, grupo, num = struct.unpack_from("<IIii", dados, pos)
        sons.add((grupo, num))
        pos = prox
    return sons


def arquivos_do_lutador(pasta):
    """(.snd, [.cns...]) pelo .def do lutador."""
    nome = pasta.name
    defs = [d for d in pasta.glob("*.def") if d.stem == nome] or list(pasta.glob("*.def"))
    txt = defs[0].read_text(encoding="utf-8", errors="replace")
    snd, cns = None, []
    for linha in txt.splitlines():
        linha = linha.split(";", 1)[0].strip()
        m = re.match(r"(?i)(sound|cns|st\d*|stcommon)\s*=\s*(.+)", linha)
        if not m:
            continue
        chave, valor = m.group(1).lower(), m.group(2).strip().strip('"')
        caminho = pasta / valor
        if chave == "sound":
            snd = caminho
        elif caminho.exists() and caminho.suffix.lower() == ".cns":
            cns.append(caminho)
    return snd, sorted(set(cns))


RE_BLOCO = re.compile(r"(?im)^\s*\[state\s+[^\]]*\]")
RE_TIPO = re.compile(r"(?im)^\s*type\s*=\s*(\w+)")
RE_PAR = re.compile(r"(?im)^\s*(value|hitsound|guardsound)\s*=\s*([^;\r\n]*)")
RE_FIXO = re.compile(r"^\s*([SF]?)\s*(-?\d+)\s*,\s*(-?\d+)\s*$", re.I)


def conferir(pasta, comum):
    snd, cnss = arquivos_do_lutador(pasta)
    proprio = ler_snd(snd) if snd and snd.exists() else set()
    faltas, dinamicos, total = [], 0, 0
    for cns in cnss:
        txt = cns.read_text(encoding="utf-8", errors="replace")
        partes = RE_BLOCO.split(txt)
        cabecas = RE_BLOCO.findall(txt)
        for cab, corpo in zip(cabecas, partes[1:]):
            m = RE_TIPO.search(corpo)
            tipo = m.group(1).lower() if m else ""
            if tipo not in ("playsnd", "hitdef", "reversaldef", "projectile"):
                continue
            for par, valor in RE_PAR.findall(corpo):
                par = par.lower()
                if par == "value" and tipo != "playsnd":
                    continue
                if par != "value" and tipo == "playsnd":
                    continue
                f = RE_FIXO.match(valor)
                if not f:
                    dinamicos += 1
                    continue
                total += 1
                pre, g, n = f.group(1).upper(), int(f.group(2)), int(f.group(3))
                if g < 0:
                    continue
                if par == "value":
                    banco = comum if pre == "F" else proprio
                    onde = "common.snd" if pre == "F" else snd.name
                else:
                    banco = proprio if pre == "S" else comum
                    onde = snd.name if pre == "S" else "common.snd"
                if (g, n) not in banco:
                    faltas.append(f"{cns.name} {cab.strip()} {par} = {valor.strip()} -> falta {g},{n} em {onde}")
    return total, dinamicos, faltas


def main():
    nomes = sys.argv[1:] or sorted(p.name for p in (RAIZ / "chars").iterdir()
                                   if p.is_dir() and not p.name.startswith("teste"))
    comum = ler_snd(COMUM)
    ruim = 0
    for nome in nomes:
        total, din, faltas = conferir(RAIZ / "chars" / nome, comum)
        unicas = sorted(set(faltas))
        print(f"{nome:<10} {total:4d} sons fixos conferidos, {din} dinâmicos, {len(unicas)} faltando")
        for f in unicas[:40]:
            print("   FALTA", f)
        ruim += len(unicas)
    print(f"\nRESUMO: {'nenhum som faltando' if not ruim else f'{ruim} sons faltando'}")
    sys.exit(1 if ruim else 0)


if __name__ == "__main__":
    main()
