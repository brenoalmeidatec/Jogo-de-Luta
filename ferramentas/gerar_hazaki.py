#!/usr/bin/env python3
"""Monta os quadros e estados de Hazaki para o IKEMEN GO."""

from PIL import Image, ImageDraw

from gerar_pengaro import (
    ALT, BALAO_ACIMA_DOS_PES, BALOES, DEF, EIXO_X, EIXO_Y, LARG, RAIZ,
    carregar_faiscas, escrever_sff, gira, montar_air, montar_cmd,
    montar_cns, montar_sprites, move,
)
from repertorio import golpes


def recortar_folha(nome, colunas, linhas, alturas, ancoras):
    folha = Image.open(RAIZ / "sprites/hazaki" / nome).convert("RGBA")
    quadros = []
    for i, (altura, ancora) in enumerate(zip(alturas, ancoras)):
        x, y = i % colunas, i // colunas
        recorte = folha.crop((round(x * folha.width / colunas), round(y * folha.height / linhas),
                             round((x+1) * folha.width / colunas), round((y+1) * folha.height / linhas)))
        recorte = recorte.crop(recorte.getchannel("A").getbbox())
        escala = altura / recorte.height
        recorte = recorte.resize((round(recorte.width * escala), altura), Image.Resampling.LANCZOS)
        tela = Image.new("RGBA", (LARG, ALT))
        tela.alpha_composite(recorte, (EIXO_X - round(recorte.width * ancora), EIXO_Y - altura))
        quadros.append(tela)
    return quadros


def poses():
    base = recortar_folha("karate.png", 4, 3,
                          (109, 110, 105, 74, 92, 109, 106, 26, 108, 111, 127, 108),
                          (.51, .51, .51, .49, .52, .51, .59, .50, .42, .35, .48, .36))
    diabo = recortar_folha("diabo-loiro.png", 4, 2, (116, 116, 91, 116, 116, 131, 115, 82),
                           (.53, .50, .44, .36, .33, .43, .34, .43))
    parado, anda, anda2, agacha, pulo, guarda, dano, deitado, soco, chute, cima, especial = base
    origem = dict(parado=parado, andando=anda, andando2=anda2, agachado=agacha, pulo=move(pulo, 0, -10),
                  defesa=guarda, apanhando=dano, soco=soco, chute=chute,
                  rasteira=move(gira(chute, 40, 0, -55), 0, 19), especial=especial)
    return origem, diabo, cima, deitado


def substituir_sprite(s, nome, img):
    codigo = s.codigos[nome]
    for i, (g, ind, _, x, y) in enumerate(s.lista):
        if (g, ind) == codigo:
            s.lista[i] = (g, ind, img, x, y)
            return


def lista_de_golpes():
    direcoes = {"B": "_B", "D": "_D", "F": "_F"}
    linhas = ["<#f0f000>:Especiais e supers:</>"]
    nomes = set()
    for g in golpes(True):
        if g.estado < 1000 or g.nome in nomes:
            continue
        nomes.add(g.nome)
        partes = g.comando.removeprefix("~").split(", ")
        comando = "".join(direcoes[d] for d in partes[:-1])
        comando += "^P" if partes[-1] in "xy" else "^K"
        nome = f"{g.nome} / {g.nome_desperto}" if g.nome_desperto else g.nome
        custo = f" ({g.custo})" if g.custo else ""
        linhas.append(f"{nome}{custo}\t\t{comando}")
    linhas += ["", "<#f0f000>:Sistema:</>", "Diabo Loiro (1000)\t\t^X_+^A_+^Y",
               "Parry\t\t_F^C", "Agarrão\t\t[_B/_F]_+^Y", "Provocação\t\t^C"]
    return "\n".join(linhas) + "\n"


def main():
    origem, diabo, cima, deitado = poses()
    BALOES.update(golaco="DIABO LOIRO!", intro="Bora ver se aguenta o treino.",
                  intro_trava="Bora ver se aguenta o treino.")
    for chave in ("provoca", "vitoria0", "vitoria1", "vitoria2", "round", "primeiro", "derrota", "locutor_ko",
                  "ressaca", "locutor", "provoca_fim", "provoca_cai"):
        BALOES[chave] = "EU SOU GOSTOSO!"
    bola = Image.new("RGBA", (20, 20))
    ImageDraw.Draw(bola).ellipse((0, 0, 19, 19), fill="#de590e", outline="#ffdc6d", width=3)
    s = montar_sprites((origem, bola), RAIZ / "sprites/hazaki-selecao-kof.png", hazaki=True)
    substituir_sprite(s, "baixo_cima1", cima)
    substituir_sprite(s, "kick_alto", cima)
    substituir_sprite(s, "deitado", deitado)
    for i in range(4):
        substituir_sprite(s, f"juliet{i}", move(diabo[0], 0, (0, -1, -2, -1)[i]))
    substituir_sprite(s, "embaixada0", origem["defesa"])
    for i in range(1, 4):
        substituir_sprite(s, f"embaixada{i}", gira(cima, (-8, -4, -8)[i-1], 0, 0))
    arte = {}
    grupos = {
        0: ("parado0", "soco3", "chute3", "recua", "defesa", "parry", "pouso"),
        2: ("agacha0", "agacha1", "rasteira0", "rasteira1", "rasteira2", "rasteira3", "baixo_cima0", "baixo_soco"),
        3: ("soco1", "soco2", "ar_soco", "ar_cotovelo", "q_soco4", "q_soco5"),
        4: ("chute0", "chute1", "chute2", "ar_chute", "bicicleta", "pisa"),
        5: ("baixo_cima1", "kick_alto"),
        6: ("especial",),
        7: ("pulo_sobe", "pulo_topo", "pulo_desce"),
    }
    for indice, nomes in grupos.items():
        for j, nome in enumerate(nomes):
            arte[nome] = s.add(f"diabo_{nome}", move(diabo[indice], j % 3 - 1))
    a = montar_air(s, carregar_faiscas(s), hazaki=True, arte_despertada=arte)
    pasta = RAIZ / "chars/hazaki"
    pasta.mkdir(parents=True, exist_ok=True)
    escrever_sff(pasta / "hazaki.sff", s)
    cns = montar_cns(hazaki=True)
    # A transformação de Hazaki se encerra sem a penalidade de ressaca.
    cns = cns.replace("var(21) = 60", "var(21) = 0")
    # Hazaki ainda não entrou na escala 0.6 do Pengaró; o balão acompanha a altura dele.
    cns = cns.replace("xscale = 0.6\nyscale = 0.6", "xscale = 1\nyscale = 1")
    cns = cns.replace(f"ScreenPos Y - {BALAO_ACIMA_DOS_PES}", "ScreenPos Y - 125")
    (pasta / "hazaki.cns").write_text(cns.rstrip() + "\n", encoding="utf-8", newline="\n")
    (pasta / "hazaki.cmd").write_text(montar_cmd(hazaki=True).rstrip() + "\n", encoding="utf-8")
    (pasta / "hazaki.air").write_text("\n".join(a.txt), encoding="utf-8", newline="\n")
    (pasta / "hazaki.def").write_text(DEF.replace("Pengaró", "Hazaki").replace("Pengaro", "Hazaki")
                                    .replace("pengaro", "hazaki"), encoding="utf-8", newline="\n")
    (pasta / "movelist.dat").write_text(lista_de_golpes(), encoding="utf-8", newline="\n")
    print(f"{len(s.lista)} sprites, {len(a.acoes)} ações em {pasta}")


if __name__ == "__main__":
    main()
