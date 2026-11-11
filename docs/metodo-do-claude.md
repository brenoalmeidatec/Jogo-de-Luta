# Como o Claude trabalha neste projeto

> Pedido do Alisson (2026-11-11): todo jeito de trabalhar vira `.md` e vai para o git. Este arquivo é o índice do método.
> Ele não substitui [`como-trabalhar.md`](como-trabalhar.md) (regras do Breno, valem acima) nem o [`LOGBOOK.md`](../LOGBOOK.md)
> (o que foi feito, dia a dia). Aqui fica **como** o trabalho é feito, para o Alisson, o Breno ou outra IA repetirem.
> Quando um método mudar, edite a seção dele aqui no mesmo bloco de trabalho e dê push.

## 1. Regras que não mudam

- Testes do jogo (motor, robô, filme) **só dentro do Windows Sandbox**, com som desligado. Nunca abrir `Ikemen_GO.exe` na
  máquina. Só uma sandbox por vez (arquivo de trava): quem chega depois espera.
- Nada copiado de jogo comercial (personagem, pose assinatura, nome, som): só o estilo geral de luta 2D dos anos 90.
  Sem conteúdo sexual, sem pessoa real, sem marca em texto do jogo.
- Sem PR e sem Codex: o trabalho vai direto para a `mugen`. Frente grande ou arriscada roda numa branch própria e só
  entra na `mugen` depois de conferida (seção 2).
- O Claude não digita senha. O login no ChatGPT é do Alisson; se aparecer diálogo "Salvar", ele confirma.
- Parar tudo se o uso semanal do plano chegar a 80%.

## 2. Frentes em paralelo: uma branch e uma pasta por frente

Cada frente trabalha num *worktree* separado, para duas frentes nunca editarem a mesma pasta ao mesmo tempo. Arquivos
compartilhados (`quantizar_folha.py`, `animar_folha.py`, `testar_pengaro.py`, `gerar_pengaro.py`) só recebem mudança
aditiva e pequena dentro de uma branch de frente.

| Branch | Pasta na máquina do Alisson | O que é |
|---|---|---|
| `mugen` | `C:/Dev/Jogo-de-Luta-anatomia` | linha principal; Pengaró normal na arte arcade |
| `hazak` | `C:/Dev/Jogo-de-Luta` | Hazak recriado pela ficha do Breno (gerador novo, sem o Despertar ainda) |
| `ck` | `C:/Dev/Jogo-de-Luta-ck` | CK: pipeline arcade, `gerar_ck.py`, 4 folhas do Ratão refeitas |
| `endiabrado` | `C:/Dev/Jogo-de-Luta-endiabrado` | Pengaró endiabrado boss final: Lote 7 de folhas e ligação |
| `bosses` | `C:/Dev/Jogo-de-Luta-bosses` | folhas boss (endiabrado) de Hazak, Gutto, Raiclaven e CK |
| `efeitos` | `C:/Dev/Jogo-de-Luta-efeitos` | sistema de aura animada (`ferramentas/aura.py`) e kit dos bosses |
| `cenarios` | `C:/Dev/Jogo-de-Luta-cenarios` | cenários animados de Nazaré: gerador, cenário de teste e método |

Quem junta as branches na `mugen` é o Claude orquestrador, depois de olhar o resultado (folha de contato, tira de filme,
saída do robô). Relato de agente não vale como prova.

## 3. O ciclo de qualquer trabalho grande

1. **Olhar antes:** ler ficha, regras e o trecho do gerador; listar o que existe.
2. **Fila:** escrever no repositório o pedido de cada folha (prompt pronto) antes de gerar qualquer imagem.
3. **Fazer:** gerar, converter, ligar no gerador. Commits pequenos, com push.
4. **Provar na sandbox:** robô (`testar_pengaro.py --lutador X`) e filme curto de 5 a 10 s (`filmar_sandbox.py`),
   com tira de quadros olhada quadro a quadro.
5. **Céticos:** um ou dois conferentes que não escreveram o código tentam derrubar o resultado (um pelas regras e pela
   ficha, outro com os olhos na arte e no filme). Eles não editam nada.
6. **Retoque:** consertar pela causa o que os céticos provaram; o que não der vira pendência escrita, sem maquiar.
7. **Registrar:** entrada datada no fim do `LOGBOOK.md` (feito, pendente, próximo) e, se o método mudou, este arquivo.

Erro repetido: na segunda vez que o mesmo sintoma aparece, parar de variar e capturar evidência (log do motor, saída do
robô, arquivo gerado) antes de tentar de novo. Teto de uma hora por sintoma.

## 4. Arte no ChatGPT

- Um chat por personagem. A fila com os prompts fica em [`arcade/fila.md`](arcade/fila.md) (Pengaró; o Lote 7 do
  endiabrado está na branch `endiabrado`), `arcade/fila_hazak.md` (branch `hazak`) e `arcade/fila_bosses.md` (branch `bosses`).
- Cada pedido de folha leva anexos: o modelo do personagem (folha de referência ou o conceito aprovado) e, quando a
  folha é a versão endiabrada de um golpe, a folha normal do mesmo golpe, para sair com as mesmas poses e a mesma escala.
- Folha = 8 quadros numa linha, fundo magenta `#FF00FF` (efeitos em verde `#00FF00`), sem aura nem chão no corpo.
- Aceite por folha, olhando folha de contato: 8 quadros, modelo certo em todos, dois braços e duas pernas, objeto sempre
  na mesma mão, nada cortado na borda, mesma escala da referência. No máximo 3 tentativas; a correção é pedida em cima
  da imagem, citando os quadros. Se ficar com defeito, salva a melhor e anota o quadro.
- O passo a passo técnico da automação (botões da página, como anexar, como baixar, limites) e a tabela folha por folha
  estão em [`arcade/registro_fila.md`](arcade/registro_fila.md).

## 5. Da folha ao jogo (pipeline arcade)

`folhas_arcade/<folha>.png` → `quantizar_folha.py` (paleta fixa de 15 cores + transparente por lutador) →
`animar_folha.py --arcade` → `quantizar_folha.py --meio` → `conferir_arte.py` → `quadros_arcade/<folha>/NN.png`
(tela 360x260, pés em y=219) → `gerar_<lutador>.py` monta `chars/<lutador>`.

- Loops de corpo (ginga, andar) usam só os desenhos, com tempo por quadro. **Entremeio por fluxo óptico não entra em
  corpo**: foi ele que criou a "terceira mão" na ginga.
- Retoque pequeno de desenho (apagar objeto duplicado, copiar quadro vizinho) é script em `ferramentas/retoques_arcade/`,
  nunca edição manual sem registro.
- Depois de mexer num gerador, conferir que os outros lutadores não mudaram (md5 de `chars/`).

## 6. Endiabrado = modo de Despertar de cada lutador, com cara de boss final

Vocabulário do Alisson: **endiabrado é o modo de Despertar de qualquer lutador**, não um personagem. O Hazak endiabrado
é o Diabo Loiro, o Raiclaven é o Cientista, o Gutto é o cara de cavalo, o CK é o Ratão, e o Pengaró tem o dele.

Pedido dele (2026-11-11): todo endiabrado parece um boss final, mantendo a ideia da ficha, e tem **só dele** a aura,
os efeitos, os especiais e o estilo de ataque.

Fluxo: **folha de conceito** (frente sem aura, costas, frente com aura, rosto) → **aprovação do Alisson** → fila de
folhas → geração → ligação. Conceitos aprovados em 2026-11-11, guardados como `e_conceito.png` (Hazak: `d_conceito.png`)
em `sprites/<lutador>/quadros/folhas_arcade/` (branches `endiabrado` e `bosses`):

| Lutador | Endiabrado | Aura (cor e forma, nenhuma repete) |
|---|---|---|
| Pengaró | mestre das sombras: casaco preto com friso dourado, corda ouro e violeta, algemas partidas, sem garrafa | coluna de fumaça violeta-preta + anel de sombra girando no chão, elos e pedras |
| Gutto | senhor da guerra garanhão: chifres em brasa, ombreira, corrente de cabresto, saiote, ferraduras acesas | garanhão gigante de raio vermelho empinado + crateras de casco |
| Raiclaven | Cientista chefe de laboratório, **cabelo verde**, braço mecânico, tanques e bobinas, tesoura gigante | leque de tesouras, navalhas e pentes de aço com raio branco-prata |
| Hazak | Diabo Loiro chefão: terno risca de giz, chapelão com chifres, sobretudo como capa, maleta | asas de diabo de notas em chamas laranja-ouro + coroa de ouro derretido |
| CK | Ratão dono do paredão: ouro, óculos espelhado, caco de garrafa na mão da frente | paredão de som de fumaça cinza-esverdeada soltando anéis |

A aura é sempre efeito à parte, nunca pintada no corpo (seção 4 de [`regras-dos-lutadores.md`](regras-dos-lutadores.md)).

## 7. Nada estático: aura e efeitos animados, movimento fluido

Pedido do Alisson (2026-11-11): "não quero nada estático... não quero um movimento todo duro, quero fluidez".

- **Aura em camadas** (atrás do corpo, no chão, à frente), cada uma em loop e com movimento próprio no motor: pulsa,
  gira, sobe, respira, fora de sincronia com as outras; reage a golpe (incha no especial) e some com fade. Partículas
  soltas (elos, pedras, notas, lascas, anéis) nascem em pontos variados. A ferramenta comum é `ferramentas/aura.py`
  (branch `efeitos`; a documentação dela entra em `docs/arcade/aura_animada.md` quando a frente fechar).
- **Quadros dos efeitos pelo Blender** (em teste com a asa do Hazak): em vez de uma folha de 8 quadros redesenhada, o
  próprio desenho aprovado é recortado em peças e animado com ossos e deformação (a asa bate, o leque gira), mais
  simulação para fumaça, fogo e raio. Loop de 24 a 32 quadros sem emenda, render pequeno sem suavização, paleta fixa.
  Se o teste for aprovado, vira o padrão das cinco auras e este parágrafo ganha o passo a passo.
- **Corpo continua desenhado.** A fluidez vem de antecipação, recuperação gradual (3 quadros ou mais), pano, cabelo,
  rabo e corrente atrasando 1 a 2 quadros, e deslocamento por velocidade em vez de salto. Onde 8 desenhos não bastam,
  pede-se uma segunda folha para ter 16.
- Fluidez só é dada como boa depois de vídeo curto olhado quadro a quadro.

## 8. Cenários animados

Pedido do Alisson (2026-11-11): cenários de Nazaré das Farinhas (o Cristo, a Maria Fumaça, a praça da prefeitura, a
passarela), animados. O método inteiro está em [`arcade/cenarios.md`](arcade/cenarios.md): a arte é feita em camadas PNG
na malha do jogo (tela lógica 320x180, chão em y = 165), descrita num `cenarios/<id>/cenario.json`; o
`ferramentas/gerar_cenario.py` simula a câmera, recusa cenário com furo e grava `stages/<id>.def` + `.sff`; o
`ferramentas/filmar_cenario.py` filma o passeio pelas duas pontas na sandbox e monta as tiras. Foto e mapa dos lugares
são só referência: desenho original, sem pessoa real, sem marca, foto fora do repositório.

## 9. Como retomar

Ler, nesta ordem: `docs/como-trabalhar.md`, este arquivo, as últimas entradas do `LOGBOOK.md` de cada branch da tabela
da seção 2, e o `docs/arcade/registro_fila.md`. O estado de cada frente está no LOGBOOK da branch dela.
