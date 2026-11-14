#!/usr/bin/env python3
"""Cena da transformação (Breno, issue #49): tudo preto, foco e zoom no lutador, entra a música, clarão e volta a luz.

  python3 ferramentas/cena_transformacao.py [lutador ...]      aplica em chars/<lutador>/ (pode rodar de novo)

Pós-passo sobre o [Statedef 2000] (o Despertar) do .cns, como o parry.py e o balanceamento.py. O gerar_<lutador>.py
chama `aplicar` no fim, para a cena não sumir quando o lutador for regerado. Não muda a regra de quando se pode despertar
nem a animação: só o que acontece em volta dela.

Linha do tempo (L = duração da animação 2000, lida do .air; no Pengaró L = 114 tiques):

  0 .. 14      a luz apaga: cenário vai a preto (BGPalFX), oponente some (AssertSpecial invisible), HUD e sombras somem
  0 .. L       a câmera fecha devagar no lutador (Zoom 1 -> ZOOM_FIM, ease in-out), oponente congelado (Pause)
  55 .. L      ele vai ganhando um brilho violeta (PalFX) enquanto as sombras o possuem
  L - 8 .. L   a câmera empurra (ZOOM_AUGE) e o chão treme
  L            o auge: clarão branco (EnvColor + AllPalFX que some), tremor forte, forma nova (var(20))
  L .. L + 36  a luz volta aos poucos, a câmera solta, HUD de volta, a luta continua com a música da forma

A música já estava ligada (issue #33, musica_despertar_cns do gerar): a do cenário baixa em 45 tiques a partir do
começo do estado 2000 e então entra a do boss em loop. A cena só cobre os olhos: o som não muda aqui.
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

APAGA = 14        # tiques para a luz apagar
VOLTA = 36        # tiques depois do auge até a luta voltar
ZOOM_FIM = 1.18   # zoom ao fim da animação (1 = câmera da luta)
ZOOM_AUGE = 1.30  # empurrão da câmera no auge
BRILHO_DESDE = 55  # quando o brilho violeta começa (garrafa quebra no Pengaró)
CENTRO_Y = -15    # mira vertical do zoom (negativo sobe a câmera); medido no motor para o corpo inteiro caber

# No IKEMEN v1.0, o tamanho na tela cresce com o quadrado do scale do Zoom e scale 1 mostra os lutadores a 0,65 da
# câmera da luta (medido no motor, cenários Cristo e Maria Fumaça). Por isso a cena usa ESCALA_MOTOR * raiz(zoom).
ESCALA_MOTOR = 1.24

LUTADORES = {
    "pengaro": {"brilho": (70, 10, 110)},
}

PREFIXO = "[State 2000, Cena"
COMENTARIO = "; Cena da transformação (issue #49): ferramentas/cena_transformacao.py\n"


def duracao_anim(air, numero):
    txt = air.read_text(encoding="utf-8", errors="replace")
    m = re.search(rf"(?ims)^\[Begin Action {numero}\]\s*$(.*?)(?=^\[Begin Action|\Z)", txt)
    if not m:
        raise SystemExit(f"{air.name}: não achei a ação {numero}")
    total = 0
    for linha in m.group(1).splitlines():
        partes = linha.split(";")[0].split(",")
        if len(partes) >= 5 and re.fullmatch(r"\s*-?\d+\s*", partes[0]) and re.fullmatch(r"\s*-?\d+\s*", partes[1]):
            total += max(int(partes[4]), 0)
    return total


def bloco(nome, corpo):
    return f"{PREFIXO}: {nome}]\n{corpo.strip()}\n\n"


def cena(L, brilho, som="F31,0"):
    fim = L + VOLTA
    luz = L + 6           # a luz começa a voltar logo depois do clarão
    sobe = VOLTA - 12     # em quantos tiques ela volta
    br, bg, bb = brilho
    ease = f"(Time / {L}.0) * (Time / {L}.0) * (3 - 2 * Time / {L}.0)"
    # escuro: 256 = normal, 0 = preto. Três fases (apaga, preto, volta) num ifelse só.
    escuro = (f"ifelse(Time < {APAGA}, 256 * ({APAGA} - Time) / {APAGA}, "
              f"ifelse(Time < {luz}, 0, min(256, 256 * (Time - {luz}) / {sobe})))")
    alvo = f"Pos X, Pos Y - {-CENTRO_Y}"  # Pos X já é em relação ao centro da câmera
    c = []
    c.append(bloco("congela o resto", f"""
type = Pause
trigger1 = Time = 0
time = {fim}
movetime = {fim}
"""))
    c.append(bloco("som de entrada", f"""
type = PlaySnd
trigger1 = Time = 0
value = {som}
"""))
    c.append(bloco("sem HUD e sem sombra", f"""
type = AssertSpecial
trigger1 = Time < {L + 20}
flag = nobardisplay
flag2 = globalnoshadow
flag3 = timerfreeze
ignorehitpause = 1
"""))
    c.append(bloco("cenário no escuro", f"""
type = BGPalFX
trigger1 = Time < {fim}
time = 2
mul = {escuro}, {escuro}, {escuro}
ignorehitpause = 1
"""))
    c.append(bloco("oponente no escuro", f"""
type = PalFX
trigger1 = Time < {fim} && NumEnemy > 0
redirectid = enemynear,id
time = 2
mul = {escuro}, {escuro}, {escuro}
ignorehitpause = 1
"""))
    c.append(bloco("oponente some", f"""
type = AssertSpecial
trigger1 = Time >= {APAGA // 2} && Time < {luz + sobe // 2} && NumEnemy > 0
redirectid = enemynear,id
flag = invisible
ignorehitpause = 1
"""))
    c.append(bloco("brilho das sombras", f"""
type = PalFX
trigger1 = Time >= {BRILHO_DESDE} && Time < {L}
time = 2
add = {br} * (Time - {BRILHO_DESDE}) / {L - BRILHO_DESDE}, {bg} * (Time - {BRILHO_DESDE}) / {L - BRILHO_DESDE}, {bb} * (Time - {BRILHO_DESDE}) / {L - BRILHO_DESDE}
ignorehitpause = 1
"""))
    c.append(bloco("câmera fecha", f"""
type = Zoom
trigger1 = Time < {L - 8}
time = 2
pos = {alvo}
scale = {ESCALA_MOTOR} * (1 + {ZOOM_FIM - 1:.2f} * {ease}) ** 0.5
lag = 0
endlag = 0.9
camerabound = 0
stagebound = 0
ignorehitpause = 1
"""))
    c.append(bloco("câmera empurra", f"""
type = Zoom
trigger1 = Time >= {L - 8} && Time < {L + 12}
time = 2
pos = {alvo}
scale = {ESCALA_MOTOR * ZOOM_AUGE ** 0.5:.3f}
lag = 0.8
endlag = 0.9
camerabound = 0
stagebound = 0
ignorehitpause = 1
"""))
    c.append(bloco("garrafa quebra treme", f"""
type = EnvShake
trigger1 = Time = {BRILHO_DESDE}
time = 10
ampl = 2
freq = 90
"""))
    c.append(bloco("auge: clarão", f"""
type = EnvColor
trigger1 = Time = {L}
value = 255, 255, 255
time = 3
ignorehitpause = 1
"""))
    c.append(bloco("auge: clarão some", f"""
type = AllPalFX
trigger1 = Time >= {L + 3} && Time < {L + 21}
time = 2
add = 255 * ({L + 21} - Time) / 18, 255 * ({L + 21} - Time) / 18, 255 * ({L + 21} - Time) / 18
ignorehitpause = 1
"""))
    c.append(bloco("auge: tremor", f"""
type = EnvShake
trigger1 = Time = {L}
time = 28
ampl = 7
freq = 60
"""))
    return "".join(c)


# Vai depois do [State 2000, Liga], que liga a forma no último tique da animação 2000.
PARADA = bloco("forma nova parada", """
type = ChangeAnim
trigger1 = Anim = 2000 && AnimTime = 0
value = 0
""")


def aplicar(lutador, pasta=None):
    pasta = Path(pasta or RAIZ / "chars" / lutador)
    arq = pasta / f"{lutador}.cns"
    txt = arq.read_text(encoding="utf-8")
    m = re.search(r"(?ms)^\[Statedef 2000\][^\n]*\n(.*?)(?=^\[Statedef )", txt)
    if not m:
        print(f"{lutador}: sem Despertar (estado 2000), cena não aplicada")
        return
    L = duracao_anim(pasta / f"{lutador}.air", 2000)
    corpo = m.group(1)
    cab, resto = re.split(r"(?m)^(?=\[State )", corpo, maxsplit=1) if "[State " in corpo else (corpo, "")
    blocos = re.split(r"(?m)^(?=\[State )", resto)
    novos = []
    som = None
    antigo = re.search(r"(?ms)^\[State 2000, Cena: som de entrada\].*?^value\s*=\s*([^;\n]+?)\s*$", corpo)
    if antigo:
        som = antigo.group(1)
    for b in blocos:
        titulo = b.split("\n", 1)[0]
        tipo = re.search(r"(?mi)^type\s*=\s*(\w+)", b)
        tipo = tipo.group(1).lower() if tipo else ""
        if b.startswith(PREFIXO):
            continue  # cena antiga: refeita abaixo
        if tipo == "superpause":
            m_som = re.search(r"(?mi)^sound\s*=\s*([^;\n]+?)\s*(;|$)", b)
            if m_som:
                som = m_som.group(1)
            continue  # a pausa curta dá lugar à cena; o som dela toca no começo da cena
        if ("Clarão da super" in titulo and tipo == "bgpalfx"):
            continue  # a pausa curta e o clarão de entrada dão lugar à cena
        # a cena segue 36 tiques depois da animação, com a anim 0 em loop: o que disparava no fim da 2000
        # (forma nova, pilar dos efeitos) só pode disparar no fim da 2000
        b = re.sub(r"(?mi)^(trigger\w*\s*=\s*)AnimTime\s*=\s*0\s*$", r"\1Anim = 2000 && AnimTime = 0", b)
        if titulo.startswith("[State 2000, Fim]"):
            b = re.sub(r"(?m)^trigger1\s*=.*$", f"trigger1 = Time >= {L + VOLTA}", b, count=1)
        novos.append(b)
    cab = cab.replace(COMENTARIO, "")
    if not cab.endswith("\n\n"):
        cab = cab.rstrip("\n") + "\n\n"
    corpo_novo = (cab + COMENTARIO + cena(L, LUTADORES.get(lutador, LUTADORES["pengaro"])["brilho"], som or "F31,0") + "".join(novos).rstrip("\n")
                  + "\n\n" + PARADA)
    novo = txt[:m.start(1)] + corpo_novo + txt[m.end(1):]
    if novo != txt:
        arq.write_text(novo, encoding="utf-8", newline="\n")
    print(f"{lutador}: cena da transformação no estado 2000 ({L} + {VOLTA} tiques)")


if __name__ == "__main__":
    for nome in sys.argv[1:] or LUTADORES:
        aplicar(nome)
