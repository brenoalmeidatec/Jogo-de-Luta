# Meta da versão 1.0 do Nazafights (proposta de 2026-11-14)

Proposta do Alisson para o Breno aprovar ou ajustar. A ideia é ter uma linha de chegada: o que entra na 1.0, como
saber que cada coisa está pronta, em que ordem e até quando. Enquanto o Breno não aprovar, isto é só proposta.

**Data-alvo sugerida: domingo, 20/12/2026.**

## 1. Escopo fechado da 1.0

| Parte | O que entra na 1.0 | Como está hoje (mugen `73c5427f`) |
|---|---|---|
| Lutadores | **6**, cada um com forma base e despertada: Pengaró (Endiabrado), Hazak (Diabo Loiro), CK (Ratão do Paredão), Gutto (Senhor da Guerra Garanhão), Raiclaven (Cientista Louco) e Gbzin (Deus Motoboy) | 5 no jogo. Raiclaven despertado esperando aval do conceito (#43). Gbzin parado esperando a foto (#30) |
| Cenários | **5** de Nazaré: Cristo, Maria Fumaça, praça, passarela e Katiara, com tela de escolha de mapa | Os 5 no jogo (#34, #35), esperando aval |
| Modos | Arcade, Versus, Modo Super, Treino, Assistir e Opções, tudo em português | No jogo (#41) |
| Trilha | 12 músicas ligadas com loop limpo, mais **2 novas**: Deus Motoboy e vitória | 12 ligadas; ninguém ouviu as voltas do loop no PC ainda (#33). Faltam as 2 novas |
| Telas e sons | Título animado, HUD simples, VS, seleção; sons próprios de cada lutador | No jogo (#39, #40, #46), esperando aval |
| Golpes | Kit completo das regras em todo lutador: agarrão de segurar e bater, parry, cena da transformação, agarrão e poder de longe do despertado | No jogo nos 5 (#44, #45, #47, #48, #49), esperando aval. Falta no Gbzin |

**Fica para depois da 1.0** (a não ser que troque por algo de dentro):

- cenário destruído depois da transformação;
- falas e balões gravados pelo Breno;
- abertura animada antes do menu (o título já é animado);
- folhas próprias para os 20 golpes do Diabo Loiro que hoje usam a folha mais parecida;
- qualquer lutador, cenário ou modo além dos listados acima.

## 2. Checklist com critério de pronto

Um item só conta como pronto quando cumpre as três coisas: **está na `mugen`**, **o robô passa com 0 falha** e
**o Breno jogou e fechou a issue**.

- [ ] **Pengaró** (#32, #42): Breno joga base e Endiabrado e fecha as duas issues.
- [ ] **Hazak** (#36, #44): nitidez conferida, roupa do Diabo Loiro aprovada, issues fechadas.
- [ ] **CK e Gutto** (#47): agarrão e poder do despertado aprovados.
- [ ] **Raiclaven** (#43): conceito da parceira aprovado, kit do Cientista Louco na mugen, robô 0 falha.
- [ ] **Gbzin** (#30): foto entregue, conceito aprovado, base e Deus Motoboy na mugen com kit completo, robô 0 falha.
- [ ] **Cenários** (#34, #35): os 5 jogados, cada um com a sua música; issues fechadas.
- [ ] **Trilha** (#33): Breno ouviu três voltas de cada loop sem estalo; Deus Motoboy e vitória ligadas.
- [ ] **Telas e sons** (#39, #40, #46): aprovados e issues fechadas.
- [ ] **Golpes e efeitos** (#38, #45, #48, #49): aprovados e issues fechadas.
- [ ] **Revisão final** (#41): uma pessoa joga o Arcade inteiro com cada um dos 6 lutadores sem travar, sem texto em inglês e sem som faltando.
- [ ] **Balanceamento**: torneio CPU x CPU sem lutador acima de 60% nem abaixo de 40% de vitórias, e a duração da transformação conferida com gente jogando.
- [ ] **Fechamento**: tag `v1.0` na `mugen` e o atalho baixando essa versão.

## 3. Ordem de prioridade

1. **Fechar o que já está no jogo esperando aval.** São 15 issues abertas com trabalho entregue. Aqui é o Breno jogar e dizer "ok" ou listar os ajustes.
2. **Raiclaven despertado** (#43), que só depende do aval do conceito.
3. **Gbzin** (#30), que só depende da foto.
4. **Trilha**: ouvir os loops e gerar as 2 músicas que faltam.
5. **Revisão final e balanceamento** com gente jogando.
6. **Tag `v1.0`.**

## 4. Datas

| Até | O que acontece |
|---|---|
| dom 22/11 | Breno aprova ou ajusta este escopo e a data, manda a foto do Gbzin e responde os avais pendentes |
| dom 06/12 | Conteúdo completo: tudo do escopo está na `mugen`. A partir daqui não entra nada novo |
| dom 13/12 | Semana de jogar e corrigir erro |
| dom 20/12 | Versão 1.0 marcada |

Se a foto do Gbzin não chegar até 22/11, a proposta é a 1.0 sair com 5 lutadores e o Gbzin virar a primeira novidade da 1.1.

## 5. Regras para o jogo não ficar infinito

1. **Ideia nova vai para a lista "Depois da 1.0"** (uma issue só para isso). Nenhuma ideia se perde, só espera a vez.
2. **Para entrar na 1.0, troca.** A ideia nova entra se sair do escopo um item de tamanho parecido, escolhido pelo Breno.
3. **Até duas rodadas de ajuste por item.** Depois da segunda, o item fica como está e o que sobrar vai para a lista.
4. **Aval em até 3 dias.** Item entregue que passar 3 dias sem resposta conta como aprovado do jeito que está.
5. **Depois de 06/12, só correção de erro.**

## 6. O que o Breno precisa responder

1. O escopo da seção 1 está certo? O que tira, o que troca?
2. A data de 20/12 serve?
3. Aceita as cinco regras da seção 5?
4. O cenário destruído pode ficar para depois da 1.0?
