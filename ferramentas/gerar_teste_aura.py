#!/usr/bin/env python3
"""Gera chars/teste_aura: lutador SÓ de teste do sistema de aura animada (ferramentas/aura.py).

  python ferramentas/gerar_teste_aura.py [--tiras PASTA]

Não é lutador do jogo: não entra no select.def, não tem ficha nem golpes. O corpo é a ginga do Pengaró arcade
(sprites/pengaro/quadros_arcade, só leitura). Ele tem duas auras de exemplo, uma por lado da luta, para filmar as
duas ao mesmo tempo com ferramentas/filmar_aura.py:
  - P1, aura "ck": paredão de som + coluna de fumaça cinza-esverdeada + névoa rente ao chão + nuvens subindo, feita
    das folhas sprites/ck/quadros/folhas_arcade/fx_paredao.png, fx_aura.png e fx_fumaca.png (fundo verde).
  - P2, aura "sombra": coluna de fumaça violeta-preta, anel de sombra girando no chão, névoa rente ao chão, pedras e
    elos flutuando, tudo feito por código (aura.fumaca_procedural etc.).
Nenhuma camada é escalada nem girada pelo motor: o que cresce, gira ou balança é assado em quadros (aura.reduzir,
aura.ondular, giro e escala das partículas). Só a névoa rasteira fica na frente do corpo.
O Despertar e os estados de teste são ligados por maps que o roteiro do filme escreve: t_desp (Despertar), t_surto
(especial 1000, dispara o surto), t_pos/t_posx (põe no lugar), t_super (1100: superpausa de 40 ticks), t_golpe
(1300: golpe que põe o outro no estado custom 1310 por 50 ticks) e t_pulo (pulo).
"""
import argparse
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aura  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "chars" / "teste_aura"
FOLHAS_CK = RAIZ / "sprites/ck/quadros/folhas_arcade"
CORPO = RAIZ / "sprites/pengaro/quadros_arcade"
EIXO = (180, 220)  # pés na tela de 360x260 dos quadros arcade
ALTURA_LUTADOR = 111  # da ginga arcade (bbox 109..220)


# ------------------------------------------------------------------ as duas auras de exemplo

def aura_ck():
    base = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(FOLHAS_CK / "fx_aura.png"), altura=236), total=28)
    coluna = aura.ondular(base, amplitude=3, ondas=1.2)
    coluna2 = aura.espelhar(aura.ondular(aura.reduzir(base, 0.62, 0.7), amplitude=4, ondas=0.8, voltas=-1))
    paredao = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(FOLHAS_CK / "fx_paredao.png"), altura=150),
                                total=16, metodo="mistura", vaivem=False)
    nuvem = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(FOLHAS_CK / "fx_fumaca.png"), altura=34,
                                             ancora="centro"), total=16, loop=False)
    nevoa = aura.nevoa_rasteira(124, 13, 24, cores=((120, 132, 118), (190, 200, 186)), contorno=(60, 70, 60), semente=4)
    M = aura.Movimento
    a = aura.Aura("ck", ligada="map(t_desp) > 0 && TeamSide = 1", surto="StateNo = 1000 && Time = 1", base=9600,
                  altura_lutador=ALTURA_LUTADOR, camadas=[
        aura.Camada("paredao", paredao, plano="tras", pos=(-6, 0), surto_incha=0.08, surto_tremor=2.5,
                    mov=M(deriva=(1.5, 1.5), deriva_periodo=64, alfa=0.8, respira=0.08, tremor=0.4)),
        aura.Camada("coluna", coluna, plano="tras", pos=(-4, 2), mov=M(deriva=(3, 4), alfa=0.86)),
        aura.Camada("coluna2", coluna2, plano="tras", pos=(14, 2), esconde="StateNo = 1000",
                    mov=M(deriva=(4, 3), deriva_periodo=110, alfa=0.6)),
        aura.Camada("nevoa", nevoa, plano="frente", pos=(2, 3), surto_incha=0.0, surto_alfa=0.08,
                    mov=M(deriva=(3, 0.5), deriva_periodo=90, alfa=0.4, respira=0.2)),
    ], particulas=[
        aura.Particula("nuvem", nuvem, periodo=10, vida=52, area=(-46, -30, 46, -150), vel=(0, -1.0),
                       vel_var=(0.9, 0.5), grav=(0, -0.012), escala=(0.7, 1.4), giro=(0, 25), alfa=0.8, semente=3),
        aura.Particula("anel", aura.anel_de_fumaca(26, 12), periodo=14, vida=46, area=(-30, -60, 30, -120),
                       vel=(0, -1.5), vel_var=(1.2, 0.4), alfa=0.75, semente=8),
    ])
    return a, {"coluna": coluna, "paredao": paredao, "nuvem": nuvem, "nevoa": nevoa}


def aura_sombra():
    coluna = aura.ondular(aura.fumaca_procedural(150, 238, 24), amplitude=3, ondas=1.1)
    coluna2 = aura.espelhar(aura.fumaca_procedural(104, 186, 24, semente=13, base=0.33, topo=0.2,
                                                   cores=((40, 18, 66), (72, 36, 116), (116, 68, 168))))
    anel = aura.anel_procedural(176, 46, 24)
    nevoa = aura.nevoa_rasteira(124, 13, 24, semente=9)
    M = aura.Movimento
    a = aura.Aura("sombra", ligada="map(t_desp) > 0 && TeamSide = 2", surto="StateNo = 1000 && Time = 1", base=9640,
                  altura_lutador=ALTURA_LUTADOR, camadas=[
        aura.Camada("anel", anel, plano="chao", pos=(0, -3), surto_incha=0.25,
                    mov=M(deriva=(0, 0), alfa=0.9)),
        aura.Camada("coluna", coluna, plano="tras", pos=(-3, 2), mov=M(deriva=(3, 4), alfa=0.88)),
        aura.Camada("coluna2", coluna2, plano="tras", pos=(10, 2), esconde="StateNo = 1000",
                    mov=M(deriva=(5, 3), deriva_periodo=110, alfa=0.55)),
        aura.Camada("nevoa", nevoa, plano="frente", pos=(4, 3), surto_incha=0.0, surto_alfa=0.08,
                    mov=M(deriva=(3, 0.5), deriva_periodo=90, alfa=0.4, respira=0.25)),
    ], particulas=[
        aura.Particula("pedra", aura.pedra_procedural(9), periodo=10, vida=58, area=(-55, 0, 55, -30),
                       vel=(0, -0.9), vel_var=(0.5, 0.8), grav=(0, -0.01), giro=(0, 220), alfa=1.0, sai=0.3,
                       semente=5),
        aura.Particula("pedrao", aura.pedra_procedural(14, semente=11), periodo=19, vida=70, area=(-60, 0, 60, -20),
                       vel=(0, -0.7), vel_var=(0.4, 0.5), giro=(0, -150), alfa=1.0, sai=0.3, semente=2),
        aura.Particula("elo", aura.anel_de_fumaca(16, 1, cores=((90, 80, 110), (170, 160, 190)),
                                                  contorno=(24, 16, 36)), periodo=13, vida=50,
                       area=(-40, -20, 40, -90), vel=(0, -1.1), vel_var=(1.4, 0.6), giro=(0, 300), alfa=0.95,
                       sai=0.35, semente=9),
    ])
    return a, {"coluna": coluna, "coluna2": coluna2, "anel": anel, "nevoa": nevoa}


# ------------------------------------------------------------------ SFF (mesmo formato do jogo: v2.01, RLE8, 1 paleta)

def rle8(px):
    out = bytearray()
    i, n = 0, len(px)
    while i < n:
        v = px[i]
        run = 1
        while i + run < n and px[i + run] == v and run < 63:
            run += 1
        if run > 1 or (v & 0xC0) == 0x40:
            out += bytes((0x40 | run, v))
        else:
            out.append(v)
        i += run
    return bytes(out)


def escrever_sff(destino, lista):
    """lista de (grupo, índice, imagem RGBA, eixo x, eixo y). Paleta global de 255 cores, alfa de 1 bit."""
    cores = np.concatenate([np.asarray(im)[np.asarray(im)[..., 3] >= 128][:, :3] for _, _, im, _, _ in lista])
    passo = max(1, len(cores) // 400000)
    q = Image.fromarray(np.ascontiguousarray(cores[::passo])[None], "RGB").quantize(colors=255, method=Image.MEDIANCUT)
    pal = q.getpalette()[:255 * 3]
    pal += [0] * (255 * 3 - len(pal))
    ldata = bytearray(bytes(4) + b"".join(bytes((pal[i * 3], pal[i * 3 + 1], pal[i * 3 + 2], 255)) for i in range(255)))
    nos = bytearray()
    for grupo, indice, img, ex, ey in lista:
        caixa = img.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox() or (0, 0, 1, 1)
        rec = img.crop(caixa)
        ind = np.asarray(rec.convert("RGB").quantize(palette=q, dither=Image.NONE)).astype(np.uint8) + 1
        ind[np.asarray(rec.getchannel("A")) < 128] = 0
        corpo = rle8(ind.tobytes())
        corpo = struct.pack("<I", ind.size) + corpo
        nos += struct.pack("<HHHHhhHBBIIHH", grupo, indice, rec.width, rec.height, ex - caixa[0], ey - caixa[1],
                           0, 2, 8, len(ldata), len(corpo), 0, 0)
        ldata += corpo
    ofs_pal, ofs_spr = 512, 512 + 16
    ofs_l = ofs_spr + len(nos)
    cab = bytearray(512)
    cab[0:12] = b"ElecbyteSpr\x00"
    cab[12:16] = bytes((0, 1, 0, 2))
    cab[24:28] = bytes((0, 1, 0, 2))
    struct.pack_into("<8I", cab, 36, ofs_spr, len(lista), ofs_pal, 1, ofs_l, len(ldata), ofs_l + len(ldata), 0)
    destino.write_bytes(bytes(cab) + struct.pack("<HHHHII", 1, 1, 256, 0, 0, 1024) + bytes(nos) + bytes(ldata))


# ------------------------------------------------------------------ o lutador

CAIXA = "Clsn2Default: 1\n Clsn2[0] = -20, -104, 20, 0\n"
ACOES_PADRAO = [5, 6, 10, 11, 12, 20, 21, 170, 175, 180, 181, 190, 191, 195, 40, 41, 42, 43, 44, 45, 46, 47, 100, 105, 120, 121, 122, 130, 131, 132,
                140, 141, 142, 150, 151, 152, 5000, 5001, 5002, 5005, 5006, 5007, 5010, 5011, 5012, 5015, 5016, 5017,
                5020, 5021, 5022, 5025, 5026, 5027, 5030, 5035, 5040, 5050, 5060, 5070, 5080, 5090, 5100, 5110, 5120,
                5160, 5170, 5200, 5210, 5300]

DEF = """; Gerado por ferramentas/gerar_teste_aura.py. Lutador SÓ de teste do sistema de aura: não entra no select.def.
[Info]
name = "TesteAura"
displayname = "Teste de aura"
versiondate = 11,11,2026
mugenversion = 1.1
author = "ferramentas/gerar_teste_aura.py"
pal.defaults = 1
localcoord = 320,240

[Files]
cmd = teste_aura.cmd
cns = teste_aura.cns
st = teste_aura.cns
stcommon = common1.cns
sprite = teste_aura.sff
anim = teste_aura.air
"""

CMD = """; Gerado por ferramentas/gerar_teste_aura.py.
[Remap]
x = x
y = y
z = z
a = a
b = b
c = c
s = s

[Defaults]
command.time = 15
command.buffer.time = 1

[Command]
name = "x"
command = x
time = 1

[Command]
name = "holdfwd"
command = /$F
time = 1

[Command]
name = "holdback"
command = /$B
time = 1

[Command]
name = "holdup"
command = /$U
time = 1

[Command]
name = "holddown"
command = /$D
time = 1

[Statedef -1]

[State -1, Especial de teste (dispara o surto da aura)]
type = ChangeState
value = 1000
triggerall = ctrl && statetype = S
trigger1 = map(t_surto) = 1
trigger2 = command = "x"

[State -1, Superpausa de teste (a aura do outro não pode parar)]
type = ChangeState
value = 1100
triggerall = ctrl && statetype = S
trigger1 = map(t_super) = 1

[State -1, Golpe de teste (põe o outro em estado custom)]
type = ChangeState
value = 1300
triggerall = ctrl && statetype = S
trigger1 = map(t_golpe) = 1

[State -1, Pulo de teste]
type = ChangeState
value = 40
triggerall = ctrl && statetype = S
trigger1 = map(t_pulo) = 1

[State -1, O roteiro do filme põe o lutador no lugar]
type = PosSet
trigger1 = map(t_pos) = 1
x = map(t_posx)
"""

CNS = """; Gerado por ferramentas/gerar_teste_aura.py. Lutador SÓ de teste do sistema de aura.
[Data]
life = 1000
attack = 100
defence = 100
fall.defence_up = 50
liedown.time = 60
airjuggle = 15
sparkno = 2
guard.sparkno = 40
KO.echo = 0
volume = 0
IntPersistIndex = 60
FloatPersistIndex = 40

[Size]
xscale = 1
yscale = 1
ground.back = 15
ground.front = 16
air.back = 12
air.front = 12
height = 100
attack.dist = 160
proj.attack.dist = 90
proj.doscale = 0
head.pos = -5, -90
mid.pos = -5, -60
shadowoffset = 0
draw.offset = 0,0

[Velocity]
walk.fwd = 2.4
walk.back = -2.2
run.fwd = 4.6, 0
run.back = -4.5,-3.8
jump.neu = 0,-8.4
jump.back = -2.55
jump.fwd = 2.5
runjump.back = -2.55,-8.1
runjump.fwd = 4,-8.1
airjump.neu = 0,-8.1
airjump.back = -2.55
airjump.fwd = 2.5

[Movement]
airjump.num = 0
airjump.height = 35
yaccel = .44
stand.friction = .85
crouch.friction = .82

[Statedef 1000]
type = S
movetype = I
physics = S
anim = 200
ctrl = 0
velset = 0,0

[State 1000, Fim]
type = ChangeState
trigger1 = AnimTime = 0
value = 0
ctrl = 1

; Superpausa de teste: 40 ticks em que o motor para os dois lutadores (o -2 deles não roda; o -4 roda).
[Statedef 1100]
type = S
movetype = I
physics = S
anim = 200
ctrl = 0
velset = 0,0

[State 1100, Pausa]
type = SuperPause
trigger1 = Time = 2
time = 40
movetime = 0
anim = -1
sound = -1
darken = 0
poweradd = 0

[State 1100, Fim]
type = ChangeState
trigger1 = AnimTime = 0
value = 0
ctrl = 1

; Golpe de teste: sem dano, põe o outro no estado custom 1310 (como um agarrão).
[Statedef 1300]
type = S
movetype = A
physics = S
anim = 210
ctrl = 0
velset = 0,0

[State 1300, Golpe]
type = HitDef
trigger1 = Time = 0
attr = S, NA
hitflag = MAF
guardflag =
animtype = Light
damage = 0, 0
pausetime = 0, 0
sparkno = -1
guard.sparkno = -1
hitsound = -1
guardsound = -1
ground.type = High
ground.slidetime = 0
ground.hittime = 10
ground.velocity = 0
p2stateno = 1310

[State 1300, Fim]
type = ChangeState
trigger1 = AnimTime = 0
value = 0
ctrl = 1

; Estado custom do golpe de teste: quem apanha fica 50 ticks aqui (estado do outro lutador).
[Statedef 1310]
type = S
movetype = H
physics = N
ctrl = 0
velset = 0,0

[State 1310, Volta]
type = SelfState
trigger1 = Time >= 50
value = 0
ctrl = 1

[Statedef -2]

[Statedef -3]

; A aura vai no -4: roda sempre, até com o lutador em pausa, superpausa ou estado custom.
[Statedef -4]

@AURAS@"""


def corpo(pasta, i):
    return Image.open(CORPO / pasta / f"{i:02d}.png").convert("RGBA")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tiras", type=Path, help="pasta onde gravar as tiras dos quadros das auras (para olhar)")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    lista = []
    for i in range(8):
        lista.append((0, i, corpo("ginga", i), *EIXO))
        lista.append((200, i, corpo("soco", i), *EIXO))
    rosto = corpo("ginga", 0).crop((150, 105, 210, 165))
    lista.append((9000, 0, rosto.resize((25, 25), Image.NEAREST), 0, 0))
    lista.append((9000, 1, rosto.resize((120, 140), Image.NEAREST), 0, 0))
    auras = []
    for faz in (aura_ck, aura_sombra):
        au, quadros = faz()
        auras.append(au)
        lista += au.sprites()
        print(au.resumo())
        print(f"  altura {au.altura():.0f} px = {au.altura() / ALTURA_LUTADOR:.2f}x o lutador ({ALTURA_LUTADOR} px)")
        for nome, q in quadros.items():
            m = aura.medir_loop(q, loop=nome != "nuvem")
            cobre = np.mean([(np.asarray(x)[..., 3] > 0).mean() for x in q])
            print(f"  quadros de {nome}: {m}; franja verde {max(aura.franja(x) for x in q):.4f}; "
                  f"pinta {cobre * 100:.0f}% do quadro")
            if a.tiras:
                a.tiras.mkdir(parents=True, exist_ok=True)
                aura.tira(q, colunas=8).save(a.tiras / f"quadros_{au.nome}_{nome}.png")
    DESTINO.mkdir(parents=True, exist_ok=True)
    escrever_sff(DESTINO / "teste_aura.sff", lista)
    air = ["; Gerado por ferramentas/gerar_teste_aura.py.\n[Begin Action 0]\n" + CAIXA
           + "".join(f"0,{i}, 0,0, 6\n" for i in range(8))]
    air += [f"[Begin Action {n}]\n{CAIXA}0,0, 0,0, 8\n" for n in ACOES_PADRAO]
    air.append("[Begin Action 200]\n" + CAIXA + "".join(f"200,{i}, 0,0, 5\n" for i in range(8)))
    air.append("[Begin Action 210]\n" + "".join(
        CAIXA + ("Clsn1: 1\n Clsn1[0] = 10, -95, 90, -35\n" if 2 <= i <= 4 else "") + f"200,{i}, 0,0, 5\n"
        for i in range(8)))
    air += [au.air() for au in auras]
    (DESTINO / "teste_aura.air").write_text("\n".join(air), encoding="utf-8", newline="\n")
    (DESTINO / "teste_aura.cns").write_text(CNS.replace("@AURAS@", "".join(au.cns() for au in auras)),
                                           encoding="utf-8", newline="\n")
    (DESTINO / "teste_aura.cmd").write_text(CMD, encoding="utf-8", newline="\n")
    (DESTINO / "teste_aura.def").write_text(DEF, encoding="utf-8", newline="\n")
    tam = (DESTINO / "teste_aura.sff").stat().st_size
    print(f"chars/teste_aura gravado: {len(lista)} sprites, .sff de {tam / 1024:.0f} KB")


if __name__ == "__main__":
    main()
