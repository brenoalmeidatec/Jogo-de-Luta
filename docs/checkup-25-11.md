# Checkup geral do jogo (thread de 25/11/2026)

Pedido do Alisson (25/11): "faça um checkup geral no jogo e melhore tudo que você achar que falta para ele ser um
jogo muito foda". A thread "Fechar todas as pendências sem imagem" já cuidava da mecânica dos golpes (defesa, parry,
combo, normais, régua do quadro final, explosão do Gutto, Raiclaven), então este checkup olhou o resto: a CPU, o
Arcade, as telas, o log do motor e o que aparece na tela. Tudo testado na nuvem (IKEMEN GO v1.0.0 Linux, Xvfb).

## O achado principal: a CPU não tinha IA

Nenhum dos 6 lutadores tinha código de IA. Sem isso, a CPU do IKEMEN só "amassa" botão e direção ao acaso
(`AiInput.Update` no código do motor) e, de vez em quando, solta um comando especial sorteado. Era por isso que a CPU
pulava e agachava à toa, soltava bola de longe sem motivo, nunca emendava combo e nunca despertava. No Arcade, que é
a 1.0, a CPU é o adversário de toda luta: era o maior buraco do jogo.

### O que entrou

- **`ferramentas/ia_cpu.py`** põe um bloco no fim do `[Statedef -2]` de cada `.cns` (só age com `AILevel > 0`, isto
  é, só na CPU; o jogador e o robô de teste não mudam). Ele:
  1. desliga o botão aleatório e o comando sorteado do motor (`AssertSpecial noaibuttonjam / noaicheat`);
  2. escolhe UMA ação por tique e "aperta" os comandos dela com `AssertCommand`, os mesmos nomes que o jogador
     aperta. Quem decide se o golpe sai é o próprio `.cmd` (barra, forma, cancelamento): a IA não ganha golpe
     nenhum que o jogador não tenha;
  3. anda, agacha e pula sozinha (o motor só faz isso com tecla de verdade);
  4. defende pela dificuldade, sorteando uma vez por golpe que vem (golpe baixo é mais difícil de ler).
- O que a IA faz, por ordem de urgência: escapa de agarrão, emenda combo quando acerta (corrente, especial, super),
  desperta com a barra cheia, antiaéreo em quem pula, pune golpe que errou e golpe defendido, ataca no ar, agarra de
  perto quem fica parado ou defendendo, solta projétil de longe, cutuca no alcance de cada golpe e provoca quem está
  no chão longe. Anda com um "plano" que muda a cada 0,2 a 0,8 s conforme a distância (aproxima, segura, recua,
  pula, agacha) e não recua encurralada.
- **A tabela de golpes sai sozinha** (`ferramentas/ia_analise.py`): do `.cmd` (que comando faz qual golpe, em que
  forma, quanto de barra), do `.cns` (golpe, agarrão, projétil, derruba) e do `.air` (quantos tiques até a caixa de
  ataque ligar e até onde ela alcança). Golpe novo entra sozinho: os 6 `gerar_<lutador>.py` chamam a IA por último.
- **A dificuldade (Opções > Dificuldade, 1 a 8) agora vale de verdade:** muda reflexo, chance de defender (de ~22%
  no 1 a ~78% no 8), de emendar combo, de punir e de fazer antiaéreo.
- **Chefe final do Arcade** (conceito do Breno de 11/11: "o endiabrado é o boss final"): na última luta do Arcade,
  `motif/nazafight/nazafights.lua` marca a CPU como chefe; ela enche a barra, desperta logo no começo (com a cena da
  transformação e o cenário quebrando) e luta sempre no nível 8. Como a forma fica até o fim da luta, o chefe luta
  despertado a partida inteira.

### Medido na nuvem

- **IA nova x CPU antiga** (`ferramentas/ia_duelo.py`, espelho: o mesmo lutador dos dois lados, nível 8, os dois
  lados da tela; medido antes da revisão de código, que só tirou vícios do andar e do combo): **38 de 38 rounds para a IA nova**, sobrando de 57% a 89% de vida, acertando 3 a 4 vezes mais.

| Lutador | Rounds | Vida que sobra | Golpes acertados (nova x antiga) |
|---|---|---|---|
| Pengaró | 8 de 8 | 80% | 54 x 15 |
| Hazak | 6 de 6 | 77% | 63 x 15 |
| CK | 6 de 6 | 61% | 62 x 27 |
| Gutto | 6 de 6 | 75% | 54 x 15 |
| Raiclaven | 6 de 6 | 89% | 58 x 13 |
| Gbzin | 6 de 6 | 57% | 75 x 36 |

- Vídeo antes/depois: [`checkup-25-11/ia_antes_depois.gif`](checkup-25-11/ia_antes_depois.gif) (em cima a CPU
  antiga, embaixo a IA nova; Gutto x Raiclaven no Cristo).
- Torneio entre os 6 com a IA nova (CPU x CPU, nível 8, 6 rounds de cada lado em cada par, 60 rounds por lutador):

| Lutador | % de vitória | Vida que sobra | Acertos por round |
|---|---|---|---|
| Gutto | 62 | 39% | 14,3 |
| Pengaró | 53 | 35% | 13,4 |
| Hazak | 53 | 37% | 13,7 |
| Raiclaven | 52 | 28% | 14,4 |
| Gbzin | 50 | 29% | 15,2 |
| CK | 30 → **40** | 23% | 15,5 |

  O CK ficou abaixo da faixa da meta (40 a 60%). Ele tem o menor alcance do elenco (luva curta, ~31 px de alcance
  típico) e a IA jogava com ele de longe como joga com os outros. Agora, para lutador de alcance curto, o plano de
  andar entra bem mais para dentro, recua menos e agarra mais de perto (`ia_cpu.py`, só a IA; dano e quadros não
  mudaram, que são da thread de pendências). Mini torneio do CK contra os 5 depois do ajuste: **24 de 60 = 40%**.
  O Gutto em 62% fica dentro do ruído conhecido do torneio (±15 entre rodadas, ver `nazafight-balanceamento`).
- **Despertar no torneio = 0:** não é defeito. O torneio reinicia o round com `resetRound()`, que zera a barra, e um
  round só enche ~1.000 a 1.400 de 3.000. Numa luta de verdade a barra passa de um round para o outro e a CPU
  desperta quando enche (visto no teste do chefe final).

### Revisão da IA (subagente)

Uma revisão de código achou e já ficou consertado: o andar e o agachar brigavam tique a tique (andava e parava em
seguida), o pulo saía para o lado errado em alguns planos, o combo sempre escolhia o primeiro golpe da lista e o
Despertar olhava 3.000 fixo em vez da barra cheia de cada lutador.

## Outros consertos do checkup

- **Gbzin sem retrato:** na grade de seleção, na tela de VS e no HUD aparecia um bonequinho minúsculo no lugar do
  rosto (ele nunca ganhou `sprites/retratos/gbzin_*.png`). Agora tem rosto e busto, recortados do desenho de
  conceito dele que já existia (`sprites/gbzin/quadros/folhas_arcade/conceito.png`), sem imagem nova; o
  `gerar_gbzin.py` troca os retratos no fim. Provisório: o retrato pintado de verdade vai para a fila de imagens.
- **Diabo demônio, orbe forte:** o `HitDef` tinha `ground.velocity` duas vezes e o motor ignora a segunda (aviso no
  log): o orbe forte não jogava o adversário para cima. Conserto no `diabo_demonio.py` e no `.cns`.
- **Log do motor limpo:** com os 6 carregados, o único aviso que sobra é o de compatibilidade do `holdfwd` etc. (o
  motor força o buffer em 1; não muda nada no jogo).
- `ferramentas/testar_mapas.py` agora instala o Gbzin também (o `.bat` já instalava).
- `ferramentas/filmar_luta_linux.py` ganhou `--sem-ia` (filma a CPU antiga, para comparar) e `--chefe` (P2 como chefe
  final).

## Fila de imagens (quando o ChatGPT voltar)

- **Retrato pintado do Gbzin** (bruto em `sprites/retratos/brutos/gbzin.png`, busto em fundo magenta como os outros;
  depois `preparar_retratos.py gbzin` e `trocar_retratos.py gbzin`). O provisório está em
  `sprites/retratos/provisorios/gbzin_conceito.png` (o rosto do conceito, espelhado).

## Sugestões para depois

- **Versão 1.1 (premium, já combinada):** tela de vitória com fala de cada lutador, final de cada um no Arcade,
  continue animado, créditos. A IA nova deixa tudo pronto para isso.
- **Cor alternativa no espelho:** P1 e P2 com o mesmo lutador ficam da mesma cor. Os corpos misturam paleta (RLE8) e
  PNG de cor cheia, então só a troca de paleta não resolve; dá para fazer com `PalFX` leve no P2 do espelho, mas ele
  briga com os brilhos de golpe e de aura. Precisa decidir o jeito.
- **IA:** contar no torneio também a barra que passa entre rounds (hoje `resetRound()` zera), para medir o
  Despertar da CPU no balanceamento.
- **IA:** ensinar o parry (hoje ela não usa) e o rolamento contra projétil nos níveis altos.
