#!/usr/bin/env python3
"""Falas da tela de vitória (Alisson, 25/11/2026): cada lutador fala uma frase quando vence a luta.

  python3 ferramentas/falas_vitoria.py              aplica nos 6 lutadores
  python3 ferramentas/falas_vitoria.py hazaki ck    só nesses
  python3 ferramentas/falas_vitoria.py --mostrar    lista as falas

Fonte única das falas. victory1 a 8 são da forma normal, 9 a 16 do Despertar.

Por que não ficam no [Quotes] do .cns: o IKEMEN GO v1.0.0 ignora o VictoryQuote (testado na nuvem em 25/11 com
value = 13 fixo: a fala saía sorteada entre todas do [Quotes]), então não dava para escolher a fala pela forma. O
motor só usa o texto da tela (winquote.text do system.def) quando o lutador NÃO tem [Quotes]. Por isso:
  1. o [Quotes] sai dos .cns (os gerar_*.py ainda escrevem a lista antiga e este pós-passo tira);
  2. a tabela de falas vai para o motif/nazafight/nazafights.lua (bloco entre marcas), e o gancho
     "game.victory_init" (o motor chama antes de escolher a fala) vê quem venceu e se terminou despertado
     (var(20) > 0) e troca o winquote.text pela fala sorteada da lista certa (modifyMotif).
Quem desenha a tela é o motor ([Victory Screen] do system.def, feito por ferramentas/textos_ptbr.py dentro do
gerar_layout.py).

As oito falas da forma normal do Pengaró, CK, Gutto, Raiclaven e Gbzin são as que já estavam nos geradores; as do
Hazak e todas as do Despertar são novas (personalidade de docs/fichas/*.md).
Pode rodar quantas vezes quiser: o bloco do .lua fica entre as marcas e é trocado, não duplicado.
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LUTADORES = ["pengaro", "ck", "gutto", "hazaki", "raiclaven", "gbzin"]
INICIO = "; >>> falas_vitoria.py (fala da tela de vitória): gerado, nao edite a mao\n"
FIM = "; <<< falas_vitoria.py\n"
LUA = RAIZ / "motif" / "nazafight" / "nazafights.lua"
LUA_INICIO = "-- >>> falas_vitoria.py (fala da tela de vitoria): gerado, nao edite a mao\n"
LUA_FIM = "-- <<< falas_vitoria.py\n"
NOME_NO_JOGO = {"pengaro": "Pengaro", "ck": "CK", "gutto": "Gutto", "hazaki": "Hazak", "raiclaven": "Raiclaven",
                "gbzin": "Gbzin"}   # o name = do .def (o que o name() do Lua devolve)

FALAS = {
    "pengaro": {
        "base": [
            "F-f-foi de letra, filho da puta.",
            "T-t-tá achando que é bo-boteco de domingo, é, ca-caralho?",
            "V-v-vai lá contar pra tua mãe que tu a-a-apanhou do gago.",
            "Eu be-bebo... be-be-BATO melhor que tu, porra!",
            "T-tu ficou pa-parado igual cone. Ma-mas cone pelo menos fica de pé.",
            "D-d-demorei pra falar, mas tu de-de-demorou mais pra levantar.",
            "Es-essa vai na tua conta, pa-pa-parceiro. A do bar também.",
            "Olha só, falei inteiro! Agora chama tua irmã que eu vou ensinar ela a gingar, hein!",
        ],
        "despertado": [
            "A-a-as sombras gostaram de tu. Vão te levar pra casa.",
            "Q-q-quem bebe com o capeta não pa-paga a conta. Tu paga.",
            "O-o-olha pro chão, que a tua sombra já fugiu.",
            "Nem gaguejei. O ca-capeta fala por mim.",
            "Na Ma-maré das Correntes: entrou, não sai mais.",
            "E-e-escuro assim nem a tua mãe te acha.",
            "A roda de capoeira agora é no in-inferno, e tu entrou nela.",
            "B-b-bota mais uma dose. Pra mim, não pra tu.",
        ],
    },
    "ck": {
        "base": [
            "Tá achando que é quem, parça?",
            "Errou o soco, tomou o troco.",
            "Ajeita o boné que a aula acabou.",
            "Vem de novo, eu deixo.",
            "Nem suei a camisa.",
            "Na esquina é assim: piscou, dormiu.",
            "Avisa lá que o CK passou.",
            "Essa luva aqui não é enfeite.",
        ],
        "despertado": [
            "Liga o paredão que o Ratão ganhou!",
            "Garrafa quebrada, briga encerrada.",
            "No baile da esquina quem manda é o rato.",
            "Dancei na tua cara e tu nem viu o passo.",
            "Ratão não corre de gato. Ratão bate no gato.",
            "Aumenta o grave que eu tô comemorando.",
            "Sobe o som: hoje o rato saiu do bueiro.",
            "Varre os cacos, que a festa acabou pra você.",
        ],
    },
    "gutto": {
        "base": [
            "Foi na ginga do Muay Thai, parceiro!",
            "Quer outra? É só pedir.",
            "Chute baixo não perdoa, né?",
            "Beijinho de despedida!",
            "Tu caiu igual a cavalo de carrossel.",
            "Treino de verdade é na canela.",
            "Essa vai na conta do Gutto.",
            "Levanta que eu dou mais uma.",
        ],
        "despertado": [
            "Rrrrfff! Coice de cavalo não tem revanche.",
            "Galopei por cima e nem senti o calombo.",
            "Bufei uma vez. Na segunda tu já tava no chão.",
            "Ferradura nova, testada na tua cara.",
            "Relincha agora, vai. Relincha!",
            "Puro-sangue não perde pra pangaré.",
            "A pista é aqui, e tu ficou parado na largada.",
            "Arreio nenhum me segura.",
        ],
    },
    "hazaki": {
        "base": [
            "EU SOU GOSTOSO!",
            "Australopiteco mentiroso! Falou que aguentava.",
            "Nem viu a minha cara, só a sola do meu pé.",
            "Pisca não, que eu já chutei três vezes.",
            "Tá vendo esse dedinho? Não, não, não.",
            "Rapidinho, igual eu prometi.",
            "Faixa preta? Só se for a do teu olho roxo.",
            "Vai treinar mais, que hoje deu pra mim.",
        ],
        "despertado": [
            "Antigamente me chamavam de Diabo Loiro. Agora tu sabe o porquê.",
            "Essa surra entra na conta. Com juros.",
            "A maleta tá cheia. O teu respeito, nem tanto.",
            "Negócio fechado: eu bato, tu paga.",
            "Ajeita o chapéu do chefe e sai da frente.",
            "Meu terno nem amassou, e tu já tá no chão.",
            "O Diabo cobra caro, e tu tá devendo.",
            "Assina aqui que eu devolvo a tua alma... um dia.",
        ],
    },
    "raiclaven": {
        "base": [
            "Próximo!",
            "Vai querer na régua?",
            "Deixa que eu capricho.",
            "Ficou um degradê lindo, hein?",
            "A casa agradece a preferência.",
            "Não mexe a cabeça que eu corto a orelha.",
            "Cabelo e barba: pago na saída.",
            "Volta daqui a quinze dias pra manutenção.",
        ],
        "despertado": [
            "Experimento concluído: a cobaia não resistiu.",
            "A Cliente adorou o corte. Você, nem tanto.",
            "Hipótese confirmada: você apanha fácil.",
            "Tesoura, navalha e ciência. Próximo!",
            "Anota aí: dose dupla de surra, efeito imediato.",
            "A Cliente tá com fome, e você tá no ponto.",
            "Degradê na tua alma, cortesia da casa.",
            "Volta pro laboratório que eu ainda não terminei.",
        ],
    },
    "gbzin": {
        "base": [
            "Volta pro curral, cabrito.",
            "Bateu três vezes, acabou.",
            "Raspagem limpa, nem suei.",
            "O cajado avisou, você não ouviu.",
            "Pastor não corre, o rebanho que vem.",
            "Faixa marrom, mão pesada.",
            "Fica deitado aí, que dá menos trabalho.",
            "Tchau, cabrito!",
        ],
        "despertado": [
            "O dízimo de hoje foi pago em pancada.",
            "Grão-Pastor não prega: cobra.",
            "Junta as notas do chão, cabrito. É o teu troco.",
            "Tapa-olho de estrela, e mesmo assim te vi caindo.",
            "O rebanho cresce, e a tua moral diminui.",
            "Ajoelhou? Agora reza.",
            "Bateu três vezes... e eu cobrei as três.",
            "Bênção e porrada, tudo no mesmo pacote.",
        ],
    },
}


def _lua_texto(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def bloco_lua():
    linhas = [LUA_INICIO,
              "-- FALA DA TELA DE VITORIA (Alisson, 2026-11-25). O motor so usa o winquote.text quando o lutador nao tem\n",
              "-- [Quotes] (e ignora o VictoryQuote), entao a fala e escolhida aqui: forma normal ou Despertar (var(20) > 0).\n",
              "local FALAS = {\n"]
    for nome in LUTADORES:
        f = FALAS[nome]
        assert len(f["base"]) == 8 and len(f["despertado"]) == 8, nome
        linhas.append(f"\t[{_lua_texto(NOME_NO_JOGO[nome].lower())}] = {{\n")
        for forma in ("base", "despertado"):
            linhas.append(f"\t\t{forma} = {{\n")
            linhas += [f"\t\t\t{_lua_texto(x)},\n" for x in f[forma]]
            linhas.append("\t\t},\n")
        linhas.append("\t},\n")
    linhas += ["}\n",
               "hook.add(\"game.victory_init\", \"nazaFalaVitoria\", function()\n",
               "\tlocal ok, err = pcall(function()\n",
               "\t\tlocal lado = getWinnerTeam()\n",
               "\t\tif lado ~= 1 and lado ~= 2 then return end\n",
               "\t\tlocal antes = id()\n",
               "\t\tlocal nome, forma = nil, 'base'\n",
               "\t\tif player(lado) then\n",
               "\t\t\tnome = string.lower(name())\n",
               "\t\t\tif var(20) > 0 then forma = 'despertado' end\n",
               "\t\tend\n",
               "\t\tplayerId(antes)\n",
               "\t\tlocal lista = nome and FALAS[nome] and FALAS[nome][forma]\n",
               "\t\tif lista then\n",
               "\t\t\tmodifyMotif('victory_screen.winquote.text', lista[math.random(#lista)])\n",
               "\t\telse\n",
               "\t\t\tmodifyMotif('victory_screen.winquote.text', 'Venceu!')\n",
               "\t\tend\n",
               "\tend)\n",
               "\tif not ok then print('nazaFalaVitoria: ' .. tostring(err)) end\n",
               "end)\n",
               LUA_FIM]
    return "".join(linhas)


def aplicar_lua(arq=LUA):
    bruto = arq.read_bytes().decode("utf-8")
    crlf = "\r\n" in bruto
    txt = bruto.replace("\r\n", "\n")
    txt = re.sub(re.escape(LUA_INICIO) + r".*?" + re.escape(LUA_FIM), "", txt, flags=re.S).rstrip("\n")
    txt = txt + "\n\n\n" + bloco_lua()
    if crlf:
        txt = txt.replace("\n", "\r\n")
    arq.write_bytes(txt.encode("utf-8"))


def aplicar(nome, pasta=None):
    """Tira o [Quotes] (e o VictoryQuote de antes, se houver) do .cns: sem [Quotes] o motor usa a fala do Lua."""
    pasta = Path(pasta) if pasta else RAIZ / "chars" / nome
    arq = pasta / f"{nome}.cns"
    bruto = arq.read_bytes().decode("utf-8")
    crlf = "\r\n" in bruto
    txt = bruto.replace("\r\n", "\n")
    txt = re.sub(re.escape(INICIO) + r".*?" + re.escape(FIM) + r"\n?", "", txt, flags=re.S)
    txt, n = re.subn(r"(?m)^\[Quotes\][^\n]*\n(?:[^\n\[][^\n]*\n)*\n?", "", txt)
    assert n <= 1, f"{arq}: mais de um [Quotes]"
    if crlf:
        txt = txt.replace("\n", "\r\n")
    arq.write_bytes(txt.encode("utf-8"))


def main():
    args = sys.argv[1:]
    if "--mostrar" in args:
        args.remove("--mostrar")
        for n in args or LUTADORES:
            print(f"== {n}")
            for forma in ("base", "despertado"):
                for t in FALAS[n][forma]:
                    print(f"  {forma:10} {t}")
        return
    for n in args or LUTADORES:
        aplicar(n)
    aplicar_lua()
    print(f"falas de {len(LUTADORES)} lutadores (8 normais + 8 do Despertar cada) em {LUA.relative_to(RAIZ)}; "
          f"[Quotes] fora dos .cns: {', '.join(args or LUTADORES)}")


if __name__ == "__main__":
    main()
