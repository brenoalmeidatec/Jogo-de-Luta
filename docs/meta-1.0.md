# Meta da versão 1.0 do Nazafights (aprovada pelo Breno em 2026-11-15)

Proposta do Alisson (2026-11-14), **aprovada pelo Breno na issue #50 em 2026-11-15**, com os ajustes dele já incluídos
abaixo. É a linha de chegada: o que entra na 1.0, como saber que cada coisa está pronta, em que ordem e até quando.

**Data combinada: domingo, 20/12/2026. A 1.0 é o Nazafights Arcade.**

## 1. Escopo fechado da 1.0

| Parte | O que entra na 1.0 | Como está hoje (mugen `73c5427f`) |
|---|---|---|
| Lutadores | **6**, cada um com forma base e despertada: Pengaró (Endiabrado), Hazak (Diabo Loiro), CK (Ratão do Paredão), Gutto (Senhor da Guerra Garanhão), Raiclaven (Cientista Louco) e Gbzin (Grão-Pastor) | 5 no jogo. Raiclaven despertado esperando aval do conceito (#43). Gbzin com as fotos entregues em 15/11, esperando o conceito novo (#30) |
| Cenários | **5** de Nazaré: Cristo, Maria Fumaça, praça, passarela e Katiara, com tela de escolha de mapa | Os 5 no jogo (#34, #35), esperando aval |
| Modos | Arcade, Versus, Modo Super, Treino, Assistir e Opções, tudo em português | No jogo (#41) |
| Trilha | 12 músicas ligadas com loop limpo, mais **2 novas**: Grão-Pastor e vitória | 12 ligadas; ninguém ouviu as voltas do loop no PC ainda (#33). Faltam as 2 novas |
| Telas e sons | Título animado, HUD simples, VS, seleção; sons próprios de cada lutador | No jogo (#39, #40, #46), esperando aval |
| Golpes | Kit completo das regras em todo lutador: agarrão de segurar e bater, parry, cena da transformação, agarrão e poder de longe do despertado | No jogo nos 5 (#44, #45, #47, #48, #49), esperando aval. Falta no Gbzin |

**Fica para depois da 1.0** (a não ser que troque por algo de dentro):

- falas e balões gravados pelo Breno;
- abertura animada antes do menu (o título já é animado);
- folhas próprias para os 20 golpes do Diabo Loiro que hoje usam a folha mais parecida;
- qualquer lutador, cenário ou modo além dos listados acima.

### Atualização de 2026-11-15: os dois jogos da issue #51

O Breno pediu na #51 dois jogos (Nazafights Arcade e Nazafights Moderno), os dois com acabamento premium. Resposta do
Alisson: **a data de 20/12 fica, e a 1.0 é o Nazafights Arcade.**

- **Entram na 1.0** as três correções da #51, porque são erros: auras e asas seguindo o corpo, efeitos de acerto
  refeitos no pixelfx e revisão de anatomia.
- **Versão 1.1 (Arcade premium):** abertura animada, transições, vitória com pose e fala, continue, créditos, final de
  cada lutador, Treino completo, lista de golpes no pause e instalador completo. Começa logo depois da 1.0.
- **Nazafights Moderno** (estilo Melty Blood): começa depois da 1.0 do Arcade, pelo piloto do Hazak. Ele reaproveita
  lutadores, cenários, músicas e telas do Arcade pronto. A data dele se combina depois do piloto aprovado.

### Fechamento do Breno (issue #50, 2026-11-15)

- **Fechado:** 1.0 é o Nazafights Arcade em 20/12, o premium vai na 1.1 e o Moderno vem depois. Nada do premium troca
  de lugar agora.
- **Entram na 1.0 a pedido dele**, por já estarem em andamento: endiabrado até o fim da luta (feito, mugen `0d4f3b06`),
  **cenário destruído em dois níveis** (#35, seção 4.2 da missão dos cenários), a **proporção** dos lutadores e as
  **asas fechando e inclinando com o corpo**, além das três correções da #51.
- **As cinco regras estão aceitas.** Na regra 4, o Breno é avisado no item antes de ele contar como aprovado.
- **Gbzin (2026-11-15, #30):** o Breno trocou a forma despertada. Sai o Deus Motoboy e entra o **Grão-Pastor**. As fotos
  chegaram no mesmo dia, então o Gbzin segue dentro da 1.0.
- Se o redesenho da anatomia ameaçar o 06/12, avisar na #50 com antecedência quais quadros ficam para depois.

## 2. Checklist com critério de pronto

Um item só conta como pronto quando cumpre as três coisas: **está na `mugen`**, **o robô passa com 0 falha** e
**o Breno jogou e fechou a issue**.

- [ ] **Pengaró** (#32, #42): Breno joga base e Endiabrado e fecha as duas issues.
- [ ] **Hazak** (#36, #44): nitidez conferida, roupa do Diabo Loiro aprovada, issues fechadas.
- [ ] **CK e Gutto** (#47): agarrão e poder do despertado aprovados.
- [ ] **Raiclaven** (#43): conceito da parceira aprovado, kit do Cientista Louco na mugen, robô 0 falha.
- [ ] **Gbzin** (#30): conceito da base e do Grão-Pastor aprovados, base e Grão-Pastor na mugen com kit completo, robô 0 falha.
- [ ] **Cenários** (#34, #35): os 5 jogados, cada um com a sua música; issues fechadas.
- [ ] **Trilha** (#33): Breno ouviu três voltas de cada loop sem estalo; Grão-Pastor e vitória ligadas.
- [ ] **Telas e sons** (#39, #40, #46): aprovados e issues fechadas.
- [ ] **Golpes e efeitos** (#38, #45, #48, #49): aprovados e issues fechadas.
- [ ] **Correções da #51**: auras, asas, garanhão, correntes e paredão seguem o corpo em todo estado (robô confere); todo efeito de acerto feito no pixelfx, com a lista do que foi trocado; anatomia revisada nos 6 lutadores e nas duas formas, com folha de contato antes e depois.
- [ ] **Pedidos do fechamento**: endiabrado até o fim da luta (na mugen); cenário destruído em dois níveis nos 5 cenários (#35); proporção dos lutadores conferida lado a lado; asas fechando e inclinando com o corpo.
- [ ] **Revisão final** (#41): uma pessoa joga o Arcade inteiro com cada um dos 6 lutadores sem travar, sem texto em inglês e sem som faltando.
- [ ] **Balanceamento**: torneio CPU x CPU sem lutador acima de 60% nem abaixo de 40% de vitórias, e a duração da transformação conferida com gente jogando.
- [ ] **Fechamento**: tag `v1.0` na `mugen` e o atalho baixando essa versão.

## 3. Ordem de prioridade

1. **Fechar o que já está no jogo esperando aval.** São 15 issues abertas com trabalho entregue. Aqui é o Breno jogar e dizer "ok" ou listar os ajustes.
2. **Raiclaven despertado** (#43), que só depende do aval do conceito.
3. **Gbzin** (#30), que só depende da foto.
4. **Correções da #51** (auras, pixelfx, anatomia) e os pedidos do fechamento (cenário destruído, proporção, asas).
5. **Trilha**: ouvir os loops e gerar as 2 músicas que faltam.
6. **Revisão final e balanceamento** com gente jogando.
7. **Tag `v1.0`.** Depois dela: 1.1 premium e Nazafights Moderno.

## 4. Datas

| Até | O que acontece |
|---|---|
| dom 22/11 | Breno responde os avais pendentes (escopo e data já aprovados em 15/11) |
| dom 06/12 | Conteúdo completo: tudo do escopo está na `mugen`. A partir daqui não entra nada novo |
| dom 13/12 | Semana de jogar e corrigir erro |
| dom 20/12 | Versão 1.0 marcada |

Se o Gbzin não estiver completo na `mugen` em 06/12, a 1.0 sai com 5 lutadores e ele vira a primeira novidade da 1.1.

## 5. Regras para o jogo não ficar infinito

1. **Ideia nova vai para a lista "Depois da 1.0"** (uma issue só para isso). Nenhuma ideia se perde, só espera a vez.
2. **Para entrar na 1.0, troca.** A ideia nova entra se sair do escopo um item de tamanho parecido, escolhido pelo Breno.
3. **Até duas rodadas de ajuste por item.** Depois da segunda, o item fica como está e o que sobrar vai para a lista.
4. **Aval em até 3 dias.** Item entregue que passar 3 dias sem resposta conta como aprovado do jeito que está. Antes de contar, o Breno recebe um aviso no próprio item.
5. **Depois de 06/12, só correção de erro.**

## 6. Lista "Depois da 1.0"

As ideias que esperam a vez ficam na issue #52.
