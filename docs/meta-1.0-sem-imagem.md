# Meta 1.0: o que dá para fechar sem imagem nova (thread de 24/11/2026)

Pedido do Alisson (24/11): fazer tudo da meta 1.0 (`docs/meta-1.0.md`) que não depende de gerar imagem no ChatGPT ou
no Gemini, e listar o que só sai com arte nova. Os testes rodam todos na nuvem (Xvfb + IKEMEN Linux), nada no PC.

## Feito e na `mugen`

| Item da meta | O que entrou | Como conferir |
|---|---|---|
| Asas e auras presas ao corpo (#51) | Nada a mudar: o robô da aura passou nos 4 despertados com aura em camadas (Hazak, Gutto, Pengaró, CK). As falhas que existiam em 16/11 sumiram com os religamentos | `python3 ferramentas/aura_no_corpo.py --robo <l>` |
| Cenário destruído em 2 níveis (#35) | Os 5 mapas passam (nível 0 → 1 → 2 e o round 2 começa no 2). O robô tropeçava no Cristo e na Maria Fumaça por causa da leitura do vídeo; agora lê quadro cru | `python3 ferramentas/testar_destruicao.py` |
| Revisão final: som faltando (#41) | Robô novo: todo som que os 6 lutadores pedem existe no arquivo certo (0 faltando em ~1.950 sons) | `python3 ferramentas/conferir_sons.py` |
| Revisão final: texto em inglês (#41) | Traduzidos os textos do motor que ainda apareciam: CARREGANDO..., "Parabéns!" no fim do Arcade, CRÉDITOS na tela de continuar e os avisos (controle não encontrado, tecla repetida, opção que pede reiniciar) | `ferramentas/textos_ptbr.py` |
| Trilha: loops sem estalo (#33) | Robô novo da emenda: as 12 faixas voltam sem estalo nem degrau de volume. Passarela e Garanhão voltam numa batida forte e ficam marcadas para ouvir | `python3 ferramentas/conferir_loops.py --ouvir PASTA` |
| Raiclaven despertado (#43) | Mordida Antiaérea (baixo + y) não acertava ninguém em pé: a caixa ficava 4 unidades acima da cabeça. Corrigida no `kit_cliente.py`; robô 216/0 | `testar_pengaro.py --linux --lutador raiclaven` |
| Proporção (#50) | Régua nova `ferramentas/proporcao.py`: os 6 lado a lado (base e despertado) e a escala de cada ação pela cabeça. Achou o Garanhão ~19% menor no parado e nos golpes novos do kit; ampliado 1,23 (`ESCALA_DE` no `ligar_pecas.py`). Os outros ficam perto da média da forma base (112): Endiabrado, Diabo Loiro e Grão-Pastor ficam um pouco maiores de propósito, e a Cientista é dupla (com a Cliente nas costas). Golpe a golpe (`escala_acoes.json`), CK, Ratão, Gbzin, Gutto e Raiclaven ficam com a mediana a ±3% do parado. Ficam para olhar quando a arte for refeita: a arte antiga do Garanhão varia de 86% a 116% entre ações (os agarrões 800-841 estão a 81%), o Grão-Pastor tem 14 ações a 82% (arte antiga, o kit dele espera imagem) e o Pengaró tem 41 ações fora (fica com a thread das pernas) | `docs/proporcao-1.0/fila_lado_a_lado.png`, `meta-1.0-sem-imagem/garanhao_antes_depois.png`, `proporcao-1.0/escala_acoes.json` |
| Luz juntando na mão (#51) | Fagulhas em espiral e miolo branco antes do poder sair, **sem** o anel tracejado (lia como a "rede de futebol" vetada). Entra no Gutto e no Raiclaven; Pengaró, CK e Hazak pegam sozinhos quando forem religados (vem pelo `aura_silhueta`) | `meta-1.0-sem-imagem/juncao_sem_anel.png` |
| Balanceamento | Torneio CPU x CPU com os 6 (10 rounds de cada lado): Gbzin 68%, Pengaró 58, Hazak 53, CK 44, Gutto 42, Raiclaven 35. O Gbzin tinha herdado attack 125 / defence 105 do CK: ficou 105 / 100. Raiclaven voltou para attack 100. Na confirmação o Gbzin caiu para 49% e o Raiclaven subiu para 42% (o torneio oscila uns ±10, é ruído) | `python3 ferramentas/torneio_cpu.py` |

## Só sai com imagem nova (esperando o upgrade do ChatGPT)

| O que | Imagem que precisa | Onde está o pedido |
|---|---|---|
| Diabo demônio: golpes do ar, direcionais e fins | 6 folhas: `ar_maos`, `ar_pes`, `direcionais_a`, `direcionais_b`, `fins_maos`, `fins_pes` | `docs/pausa-2026-11-17/diabo-demonio-motor.md` |
| Diabo Loiro com vida de verdade (#32) | 10 folhas de poses novas (ginga, mãos, pés, agachado, ar, direcionais, expressões) | project-files `hazak-32-24-11/diabo-loiro-poses-pendentes.md` |
| Grão-Pastor no kit de peças | peças/golpes que faltam no `kit_grao_pastor.py` | `docs/pausa-2026-11-17/grao-pastor.md` |
| Asa fechada do Diabo Loiro desenhada à mão | 1 desenho da asa fechada (troca a camada 9603; hoje é a aberta dobrada por código) | `docs/auras-51/LEIA-ME.md` |
| Paredão baixo do CK | 1 desenho do paredão baixo (hoje é o alto achatado pelo motor quando ele cai) | `docs/auras-51/LEIA-ME.md` |
| CK deitado e sentado no kit | kit de lado (como o `hazak_lado.py`) para pagar os quadros especiais | `docs/pausa-2026-11-17/ck-base-pecas.md` |

## Não é imagem, mas depende de gente

- **Música do Grão-Pastor e música de vitória** (Suno). Sem a do Grão-Pastor, o despertar do Gbzin baixa a música do
  cenário e fica mudo (o robô dos loops acusa `chars/gbzin/despertar.ogg` faltando).
- **Ouvir as emendas** marcadas (Passarela e Garanhão) e jogar o Arcade inteiro com cada um (revisão final).
- **Aval do Breno** nas issues abertas.
