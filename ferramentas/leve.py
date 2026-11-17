"""Deixa os trabalhos pesados do projeto fora do caminho de quem está usando o notebook.

Regra combinada em 2026-11-11 (método: docs/metodo-do-claude.md, seção 1): processo pesado (Windows Sandbox,
Blender, ffmpeg) roda com prioridade Idle e só nos núcleos de eficiência. Neste notebook (i5-1345U) os lógicos 0 a 3
são os 2 núcleos de desempenho com HT e ficam livres para o usuário; os lógicos 4 a 11 são os 8 núcleos E. A ideia e as
medidas vieram da sessão de edição de vídeo (Edições Otorrinos), que caiu de 80-99% de carga para ~3% com isso.

Uso em código:
    import leve
    p = subprocess.Popen([...], creationflags=leve.IDLE)   # já nasce em Idle
    leve.aliviar(p.pid)                                     # só núcleos E
    with leve.vigia(leve.SANDBOX):                          # aplica a regra nos processos da sandbox enquanto durar
        ...

Uso na linha de comando (para algo que já está rodando):
    python ferramentas/leve.py                  # aplica nos nomes conhecidos (sandbox, blender, ffmpeg)
    python ferramentas/leve.py --mostrar        # só lista o que acharia, sem mudar nada

Variáveis de ambiente: LEVE_NUCLEOS="4-11" muda os núcleos; LEVE=0 desliga tudo (volta ao comportamento antigo).
Em outra máquina sem núcleos E, use LEVE_NUCLEOS com a metade de cima dos núcleos ou LEVE=0.
"""
import os
import subprocess
import sys
import threading
import time
from contextlib import contextmanager

try:
    import psutil
except ImportError:  # sem psutil a regra vira só a prioridade Idle no Popen
    psutil = None

IDLE = getattr(subprocess, "IDLE_PRIORITY_CLASS", 0)
LIGADO = os.environ.get("LEVE", "1") != "0"
# LEVE_GPU=1: a sandbox recebe a GPU (vGPU) e o jogo desenha pelo Mesa d3d12 em vez do llvmpipe no processador
GPU = os.environ.get("LEVE_GPU", "1") == "1"
# a filmagem fica no processador: com a GPU o gdigrab grava tela preta (testado em 2026-11-11); ddagrab ainda não testado
GPU_FILME = os.environ.get("LEVE_GPU_FILME", "0") == "1"

# processos da Windows Sandbox vistos no host durante um teste (tasklist): WindowsSandbox.exe,
# WindowsSandboxServer.exe, WindowsSandboxRemoteSession.exe e a VM vmmemWindowsSandbox
SANDBOX = ("windowssandbox", "vmmemwindowssandbox")
PESADOS = SANDBOX + ("blender", "ffmpeg")


def nucleos():
    txt = os.environ.get("LEVE_NUCLEOS", "")
    total = os.cpu_count() or 1
    if txt:
        a, _, b = txt.partition("-")
        lista = list(range(int(a), int(b or a) + 1))
    elif total >= 12:
        lista = list(range(4, total))
    else:
        lista = list(range(total // 2, total))
    return [n for n in lista if n < total] or list(range(total))


def aliviar(pid):
    """Prioridade Idle e só núcleos E para um processo. Devolve o que conseguiu, sem levantar erro."""
    if not LIGADO or psutil is None:
        return "desligado"
    feito = []
    try:
        p = psutil.Process(pid)
        try:
            p.nice(psutil.IDLE_PRIORITY_CLASS)
            feito.append("idle")
        except (psutil.AccessDenied, OSError):
            feito.append("idle NEGADO")
        try:
            p.cpu_affinity(nucleos())
            feito.append("núcleos E")
        except (psutil.AccessDenied, OSError, ValueError):
            feito.append("afinidade NEGADA")
    except psutil.NoSuchProcess:
        return "sumiu"
    return ", ".join(feito)


def achar(prefixos=PESADOS):
    if psutil is None:
        return []
    achados = []
    for p in psutil.process_iter(["pid", "name"]):
        nome = (p.info["name"] or "").lower()
        if nome.startswith(prefixos):
            achados.append((p.info["pid"], p.info["name"]))
    return achados


@contextmanager
def vigia(prefixos=SANDBOX, intervalo=2.0, relatar=True):
    """Enquanto o bloco roda, aplica aliviar() em todo processo novo com esses nomes (a sandbox cria os dela aos poucos)."""
    if not LIGADO or psutil is None:
        yield
        return
    parar = threading.Event()
    vistos = {}

    def laco():
        while not parar.is_set():
            for pid, nome in achar(prefixos):
                if pid not in vistos:
                    vistos[pid] = (nome, aliviar(pid))
                    if relatar:
                        print(f"leve: {nome} ({pid}) -> {vistos[pid][1]}", flush=True)
            parar.wait(intervalo)

    t = threading.Thread(target=laco, daemon=True)
    t.start()
    try:
        yield vistos
    finally:
        parar.set()
        t.join(timeout=intervalo + 1)


if __name__ == "__main__":
    so_mostrar = "--mostrar" in sys.argv
    print(f"núcleos usados: {nucleos()} (ligado={LIGADO}, psutil={'sim' if psutil else 'não'})")
    for pid, nome in achar():
        print(f"{nome} ({pid})", "" if so_mostrar else f"-> {aliviar(pid)}")
