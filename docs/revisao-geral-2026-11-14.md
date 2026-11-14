# Revisão geral do jogo (missão 2026-11-14, item 6)

Feita na nuvem (IKEMEN GO v1.0.0 Linux, Xvfb), jogando de verdade pelos menus com `xdotool` e com o robô
(`ferramentas/testar_pengaro.py --linux`) nos cinco lutadores. Fotos em [`revisao-geral-2026-11-14/`](revisao-geral-2026-11-14/).

## Consertado

| O que estava errado | Onde | Conserto |
|---|---|---|
| **Golpes mudos:** o `hitsound` de soco, chute, endiabrado e assinatura estava sem o `S` na frente; sem ele o motor procura no `common.snd`, que não tem os grupos 50 a 53, e o acerto não tocava nada | `.cns` dos 5 lutadores | `gerar_sons.ligar()` escreve `S51,0` etc.; rodado de novo nos 5 (só as linhas de `hitsound` mudaram) |
| Menu de **opções** inteiro em inglês, fundo preto | `[Option Info]` | traduzido (sem acento, ver abaixo), fundo na cor do layout, itens de time, rede e língua escondidos |
| Menu de **pausa** e pausa do treino em inglês (Continue, Command List, Exit...) | `[Pause Menu]`, `[Training Pause Menu]` | PAUSA, Continuar, Controles, Lista de golpes, Trocar de lutador, Sair da luta (Open Sans do motor, com acento) |
| **Continuar?** em inglês (Continue? Yes No) na fonte do motor | `[Continue Screen]` | CONTINUAR? SIM NÃO nas tabuletas do layout |
| "VERSUS MODE", "WATCH MODE" no alto da seleção; "Random" | `[Select Info]` | VERSUS, ASSISTIR, TREINO... e ALEATÓRIO |
| Tela de configurar teclas em inglês | `keymenu` | Cima, Baixo, A chute fraco, X soco fraco, C parry... |
| **Lista de golpes** com os botões em cima das letras: depois de UM tab o motor centraliza o comando | `movelist.dat` dos 5 | `parry.alinhar_movelist()` põe sempre dois tabs (comando encostado à direita); 6 nomes de corrente encurtados para caber |
| Raiclaven: exclusivos do Surto com **nomes de cavalo** (Beijo do Cavalo, Galope, Kombo do Cavalo, Saideira do Cavalo) | `gerar_raiclaven.py`, `movelist.dat` | nomes provisórios de barbeiro: Navalha de Sombra, Corte da Corrente, Cadeira Atravessada, Queda da Cadeira, Kombo do Salão, Último Cliente |
| Demo da abertura escrevia **https://ikemen-engine.github.io** no pé da tela | `data/demo.zss` do motor | `motif/nazafight/demo.zss` sem o texto; o `.bat` aponta o `States` do `config.ini` para ele |
| Robô do Hazak: FAIL antigo "fuga da derrota não andou 100 px" | `ferramentas/robo/robo.lua` | o Hazak foge certo (anda 776 px e sai da tela); o robô media depois que o round seguinte já tinha começado. Agora guarda a última posição da fuga |

**Por que as opções ficaram sem acento:** a tela de configurar teclas herda fonte, escala e posição do `menu.item` das
opções. Qualquer troca de fonte ali (Open Sans, escala, localcoord, até a f-6x9 explícita) fazia as letras dela sumirem;
testei dez variações. A fonte do motor (f-6x9) só tem ASCII, então as opções ficam em português sem acento (OPCOES,
Video, Creditos). A pausa não tem esse problema e ficou com acento.

## Achado e não consertado (precisa do Breno ou de arte)

- **Nomes sem acento na tela:** o `.def` diz "Pengaro" e a fonte pequena do HUD (`naza_hud`) não tem acento. Para
  aparecer PENGARÓ é preciso ligar acento na `naza_hud` em `gerar_layout.py` e trocar o `displayname`.
- **Raiclaven endiabrado sem verde** na paleta (#38): a faísca dele sai prata.
- **Parry do endiabrado** usa a defesa redesenhada: faltam as folhas `e_parry_alto`/`e_parry_baixo` (ChatGPT).
- **Raiclaven, Surto de Tesoura:** os golpes ainda são o kit do Gutto com outro nome; o Despertar do Cientista Louco
  da ficha não entrou.
- **Treino e Sair** estão escondidos do menu principal (decisão do Breno em ca786230, "menu enxuto"). Sem o SAIR, o
  jeito de fechar é o Esc no título ou fechar a janela.
- **Risco no alto da tela de continuar:** um pedaço de texto cortado no canto de cima (já aparecia antes); não achei
  de onde vem.
- **SIM e NÃO** na tela de continuar quase não mudam de cor quando escolhidos (tabatinga x giz).
- Ninguém **ouviu** os golpes depois do conserto do `S` (na nuvem o motor roda mudo).

## Robô (nuvem, depois das correções)

Ver o `LOGBOOK.md` do dia.
