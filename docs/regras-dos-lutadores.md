# Regras de todo lutador

> **Este arquivo é lei.** Claude, Codex ou quem mais mexer em personagem segue estas regras. Personagem novo
> só entra na `mugen` quando passa no [checklist de aceite](#9-checklist-de-aceite). Personagem antigo que ainda
> não cumpre tudo ganha missão em `docs/missoes-codex.md` até cumprir.
>
> Se uma ficha de personagem ou outro documento disser o contrário, vale este arquivo. Só o Breno muda estas regras.

## Sumário

1. [A pegada do jogo](#1-a-pegada-do-jogo)
2. [Botões e notação](#2-botões-e-notação)
3. [O kit mínimo de todo lutador](#3-o-kit-mínimo-de-todo-lutador)
4. [Despertar: a transformação](#4-despertar-a-transformação)
5. [Como isso vira CMD e CNS no IKEMEN](#5-como-isso-vira-cmd-e-cns-no-ikemen)
6. [Regra das ferramentas: como se cria um lutador](#6-regra-das-ferramentas-como-se-cria-um-lutador)
7. [Regra da fluidez: quantos quadros cada animação tem](#7-regra-da-fluidez-quantos-quadros-cada-animação-tem)
8. [Regra dos efeitos: o estilo pixelfx](#8-regra-dos-efeitos-o-estilo-pixelfx)
9. [Checklist de aceite](#9-checklist-de-aceite)
10. [Modelo de ficha do lutador](#10-modelo-de-ficha-do-lutador)

---

## 1. A pegada do jogo

A base é **Mortal Kombat**, com pitadas de outros jogos de luta (KOF e Street Fighter entram em sistemas como
corrida, rolamento, parry e supers).

| | Como é aqui | Como **não** é |
|---|---|---|
| Especial | Toques secos de direção e um botão: **↓ → x**, **→ ← b** | Girar o analógico (meia-lua, 360°, "carregar" trás) |
| Normais | Apertar o mesmo botão 3 vezes faz uma sequência própria do botão | Só um golpe por botão |
| Combo | Correntes, kombos de assinatura e cancelamento em especial | Ficar apertando dois botões a luta toda |
| Poder | Barra cheia + dois botões = Despertar, com golpes novos | Despertar que só aumenta dano |

O que a gente pega dos outros jogos é **mecânica**. Nada de personagem, arte, nome de golpe, som ou música de jogo
existente. Cada lutador bate do seu jeito, e esse jeito vai na ficha dele (seção 10).

---

## 2. Botões e notação

| Botão | Nome | Tecla no IKEMEN |
|---|---|---|
| **x** | soco fraco | x |
| **y** | soco forte | y |
| **a** | chute fraco | a |
| **b** | chute forte | b |
| **c** | provocação / parry com → | c |

Direções são relativas ao oponente: **→** é frente, **←** é trás, **↑** cima, **↓** baixo.

| Escrita | Quer dizer | No `.cmd` |
|---|---|---|
| `↓ → x` | toca baixo, toca frente, aperta soco fraco | `~D, F, x` |
| `→ ← b` | toca frente, toca trás, aperta chute forte | `~F, B, b` |
| `← → ↓ y` | três toques e o botão (super) | `~B, F, D, y` |
| `→ + y` | segura frente e aperta | `/F, y` |
| `x + y` | dois botões juntos | `x+y` |
| `x, x, x` | aperta três vezes, uma em cada acerto | corrente (seção 5.3) |

**Regra de comando:** especial usa **só direções cardeais** (↑ ↓ ← →). Proibido no comando de especial: diagonal
(`DF`, `DB`…), `$` (aceitar diagonal como cardeal), meia-lua, 360° e carga (segurar trás por X tempo). Especial
tem 2 toques + botão; super tem 3 toques + botão. A janela (`time`) é de 15 a 18 ticks para especial e 20 a 24
para super. Isso deixa o comando "certinho", do jeito MK: baixo, frente, solta o soco.

---

## 3. O kit mínimo de todo lutador

Todo lutador tem **pelo menos** isto na forma base. É piso, não teto. O número grande é de propósito: a pessoa tem
que conseguir variar e montar combo, não ganhar apertando dois botões.

| # | Grupo | Mínimo | Golpes |
|---|---|---|---|
| A | Normais | 16 | 4 em pé, 4 agachado, 4 no ar, 4 direcionais |
| B | Correntes de botão | 4 correntes × (3 golpes + finalizador) | 16 |
| C | Kombos de assinatura | 4 | 4 |
| D | Especiais de comando | 8 | 8 |
| E | Projéteis (dentro dos especiais) | 2 | (contam no D) |
| F | Ir para trás do oponente | 1 | (conta no D) |
| G | Agarrões | 3 | 3 |
| H | Supers | 2 | 2 |
| I | Despertar | 1 | 1 |
| | **Total na forma base** | | **50 golpes** |
| | **Forma despertada** (seção 4) | +20 novos no mínimo | **70+ no total** |

Mais o sistema que todo lutador herda: andar, corrida (→ →), passo para trás (← ←), pulos, defesa alta e baixa,
rolamento (x + a), golpe de afastar (y + b), parry (→ + c), levantar rápido e provocação (c).

### A. Normais (16)

| Em pé | Agachado (↓ +) | No ar | Direcionais |
|---|---|---|---|
| x, y, a, b | x, y, a, b | x, y, a, b | → + y, → + b, ← + x, ← + a |

- **↓ + b** derruba (rasteira). **↓ + y** é antiaéreo.
- Um dos direcionais é **golpe por cima** (overhead): tem que ser defendido em pé.
- Pelo menos um aéreo acerta quem está agachado (cross-up / pulo por cima).

### B. Correntes de botão: 3 golpes + finalizador

A regra principal do Breno. Cada botão de ataque tem a **sua** sequência:

| Corrente | Entrada | O que acontece |
|---|---|---|
| Soco fraco | x, x, x → **x** | três socos rápidos; se os três acertarem, o 4º x solta o finalizador |
| Soco forte | y, y, y → **y** | três socos pesados, mais lentos e com mais alcance; 4º y finaliza |
| Chute fraco | a, a, a → **a** | três chutes rápidos, pode misturar alto e baixo; 4º a finaliza |
| Chute forte | b, b, b → **b** | três chutes pesados; 4º b finaliza |

Regras de toda corrente:

1. O golpe seguinte só sai se o anterior **encostou** (acertou ou foi defendido). No vazio a corrente para.
2. O **finalizador só sai se os três golpes acertaram de verdade**. Se algum foi defendido, a corrente acaba no 3º.
3. O finalizador **derruba** o oponente (o levantar rápido continua valendo) e tem efeito de impacto forte
   (seção 8).
4. O 1º e o 2º golpe podem cancelar em especial. O 3º cancela em especial só se acertou. O finalizador não cancela,
   a não ser no Despertar e para super.
5. Fraca é rápida e dá pouco dano; forte é lenta, alcança mais e empurra mais. O finalizador forte joga mais longe.
6. Cada golpe tem animação própria (preparação, contato, recuperação). Pode reaproveitar quadros do normal do
   mesmo botão no 1º golpe, mas o 2º, o 3º e o finalizador têm pose nova.
7. Cada lutador bate do seu jeito: a ficha diz o que é cada golpe (cotovelo, joelho, giro, cabeçada…).

### C. Kombos de assinatura (4)

Sequências fixas misturando botões e direção, do jeito das strings de MK. Exemplos de formato:

| Kombo | Entrada exemplo |
|---|---|
| Abertura | → + y, x, b |
| Alto e baixo | x, ↓ + a, y |
| Empurrão | ← + x, y, → + b |
| Lançador | a, b, ↓ + y (joga para cima para continuar no ar) |

Cada lutador tem 4, com nomes e golpes próprios. Pelo menos 1 tem golpe baixo, 1 tem golpe por cima e 1 lança.
Mesma regra das correntes: só avança se encostou.

### D. Especiais de comando (8)

Oito especiais com comando cardinal (seção 2), cada um com versão de soco/chute fraco e forte quando fizer
sentido (forte vai mais longe, sobe mais ou causa mais dano, e erra pior). Dos oito:

| Obrigatório | Mínimo | Observação |
|---|---|---|
| Projétil | 2 | ver E |
| Ir para trás do oponente | 1 | ver F |
| Antiaéreo | 1 | sai rápido, ganha de pulo |
| Avanço | 1 | atravessa meia tela, encerra combo |
| Golpe baixo ou de chão | 1 | pega quem fica agachado |
| Livres | 2 | a cara do lutador |

Comandos sugeridos (a ficha pode trocar, desde que não repita dentro do mesmo lutador):
`↓ → x/y`, `↓ ← x/y`, `→ ↓ x/y`, `← ↓ x/y`, `↓ → a/b`, `↓ ← a/b`, `→ ↓ a/b`, `← ↓ a/b`, e também
`→ ← x/y/a/b`, `← → x/y/a/b`, `↓ ↑ x/y/a/b`.

### E. Projéteis (pelo menos 2)

Os dois **não podem fazer a mesma coisa**. Escolha dois papéis diferentes:

- reto no chão (o clássico);
- em arco (passa por cima e cai);
- baixo (tem que defender agachado);
- no ar (soltado durante o pulo);
- lento ou parado (fica na tela como armadilha);
- teleguiado ou que volta (bumerangue).

Arte do projétil vem do pixelfx (seção 8). No máximo 1 projétil próprio na tela por vez, a não ser no super.

### F. Ir para trás do oponente (pelo menos 1)

Um especial que leva o lutador **para as costas do oponente, já virado para ele**, pronto para bater. Pode ser
teleporte, rolamento por baixo, salto por cima, mergulho no chão, sombra… do jeito do personagem.

- Chega virado (o lutador não fica de costas nem um quadro depois de chegar).
- No canto da tela, se não houver espaço atrás, chega colado na frente, virado, sem atravessar a parede.
- Erra feio se o oponente ler: tem recuperação visível no fim.
- Pode ter versão fraca (para trás) e forte (para trás e já ataca).

### G. Agarrões (3)

| Agarrão | Quando pega | Entrada padrão |
|---|---|---|
| Em pé (de cima) | oponente em pé, colado | colado, → ou ← + y |
| Agachado | oponente agachado, colado | colado, ↓ + y |
| De lore / especial | depende de quem é o oponente, ou agarrão de comando | ← → + y (ou o que a ficha disser) |

- Agarrão não pode ser defendido; escapa apertando y ou b no começo (como já é no Pengaró).
- Colado e com alvo agarrável, a entrada de agarrão tem prioridade sobre o normal (→ + y, ↓ + y).
- O terceiro agarrão é o espaço da **lore**: o Breno define depois, por oponente. Até lá, ele é um agarrão de
  comando genérico que funciona contra todo mundo. Quando a lore chegar, ele troca a animação e a fala conforme o
  nome do oponente (seção 5.5).

### H. Supers (2)

| Super | Custo | Comando |
|---|---|---|
| Super 1 | 1 estoque | `← → ↓` + chute |
| Super 2 | 2 estoques | `← → ↓` + soco |

### I. Despertar (1)

Ver a próxima seção.

---

## 4. Despertar: a transformação

### Como ativar

- **Só com a barra cheia** (`power = powermax`). Ativar gasta a barra inteira.
- **Padrão: x + y** (os dois socos juntos). A ficha do lutador pode trocar por outro par de botões livre
  (a + b, x + b, y + a) ou por um comando (exemplo: `↓ ↓` + x + y), desde que não bata com outro golpe dele.
- A ativação tem animação de transformação, com invencibilidade, e empurra o oponente para longe.
- O Despertar dura até a barra (que vai drenando) acabar, ou até o fim do round. Ao acabar, volta à forma base.

### Todo lutador tem a forma transformada, com arte própria

Não existe lutador sem Despertar. A forma despertada precisa de **arte redesenhada** (corpo, cores, olhos, efeitos
próprios, como o Diabo Loiro do Hazaki e o Pengaró endiabrado), e não só a mesma imagem com outra cor. Recolorir por
código serve no máximo como quebra-galho até a folha redesenhada ficar pronta, e o lutador só passa no checklist
com a arte nova.

### Toda forma despertada tem uma aura só dela

Regra do Breno (2026-11-11): no Despertar, todo lutador ganha uma **aura própria**, para mostrar que ficou mais forte.
Ela tem que ser diferente da aura de todos os outros lutadores na cor e na forma, e combinar com quem ele é. Não vale
só um brilho genérico.

- A aura é **efeito separado** do corpo: folha própria em fundo verde `#00FF00`, ligada por `Explod` em volta do lutador
  enquanto o Despertar dura. Ela não vai desenhada nas folhas do corpo. O `PalFX` pode reforçar a cor, mas sozinho não
  conta como aura.
- A ficha do lutador diz como é a aura dele (cor, forma, de onde sai) e confere que nenhum outro já usa.
- Auras de hoje, para não repetir:

| Lutador | Aura no Despertar |
|---|---|
| Pengaró | fumaça violeta-escura das sombras |
| Gutto | aura vermelha do demônio cara de cavalo |
| Raiclaven | brilho prateado de aço (o Cientista Louco ainda vai ganhar a dele) |
| Hazak | brasa laranja-ouro do Diabo Loiro |
| CK | fumaça cinza-esverdeada do baseado, subindo dos pés |

### O que muda: golpes **novos**, não só mais fortes

Transformou, ganhou coisa que não tinha. Pode reaproveitar parte do personagem base, mas o mínimo novo é:

| O que | Mínimo na forma despertada |
|---|---|
| Correntes | pelo menos **2 das 4** com golpes e finalizador novos (exemplo: o chute forte vira um chute que dá 3 voltas antes de bater) |
| Normais | pelo menos **6 dos 16** com animação e função novas |
| Especiais exclusivos | **4** que não existem na forma base |
| Projétil novo | **1** (é um dos 4 exclusivos) |
| Kombo novo | **1** |
| Super exclusivo | **1**, que só sai no Despertar |
| Especiais da base | os que ficam mudam de pose ou de função (não só cor e dano) |
| **Total novo** | **8 (correntes) + 6 + 4 + 1 + 1 = 20 golpes novos** |

Também muda o jeito de bater: ritmo, alcance, quais golpes cancelam em quê. A ficha diz o que é ganho e o que é
perda (exemplo do Pengaró de Juliete: mais potência, menos precisão).

---

## 5. Como isso vira CMD e CNS no IKEMEN

### 5.1 Faixas de estado (padrão para todo lutador)

| Faixa | Uso |
|---|---|
| 0–199 | básicos do motor (parado, andar, pulo, dano, vitória…) |
| 200–299 | normais em pé e direcionais |
| 300–339 | correntes: x = 300–303, y = 310–313, a = 320–323, b = 330–333 (o último é o finalizador) |
| 340–379 | kombos de assinatura |
| 400–499 | normais agachados |
| 600–699 | normais no ar |
| 700–799 | sistema (rolamento, afastar, parry, levantar rápido) |
| 800–899 | agarrões: 800 em pé, 810 agachado, 820 lore (e seus estados de vítima) |
| 1000–1999 | especiais, uma centena por família (1000, 1100…); projéteis e ida para trás aqui |
| 2000–2099 | ativação do Despertar |
| 3000–3999 | supers |
| 5000–5999 | golpes exclusivos do Despertar |

Animações da forma despertada usam o número da animação base **+ 10000** (convenção que o gerador do Pengaró já
usa). A variável que diz se está desperto é a mesma em todo lutador (hoje `var(20)` no Pengaró).

### 5.2 Ordem no `[Statedef -1]`

O IKEMEN pega o primeiro que bate, então a ordem de cima para baixo é: Despertar → supers → especiais
(do comando mais longo para o mais curto) → agarrões → kombos → continuação de corrente → normais direcionais →
normais.

### 5.3 Corrente em CNS

Use duas variáveis por lutador: passo da corrente e acertos da corrente. Exemplo da corrente de x:

```ini
; .cmd, dentro do [Statedef -1]
[State -1, Corrente x 2]
type = ChangeState
value = 301
triggerall = command = "x"
trigger1 = stateno = 300 && movecontact

[State -1, Corrente x 3]
type = ChangeState
value = 302
triggerall = command = "x"
trigger1 = stateno = 301 && movecontact

[State -1, Finalizador x]
type = ChangeState
value = 303
triggerall = command = "x"
trigger1 = stateno = 302 && movehit && var(6) >= 3   ; os 3 acertaram
```

```ini
; .cns, em cada golpe da corrente (300, 301, 302)
[State 300, Conta acerto]
type = VarAdd
trigger1 = movehit = 1 && numtarget
var(6) = 1
persistent = 0

; no finalizador (303): HitDef com fall = 1 para derrubar
[State 303, Golpe]
type = HitDef
trigger1 = AnimElem = 3
attr = S, NA
fall = 1
fall.recover = 1
pausetime = 10, 10
sparkno = -1
```

Zere `var(6)` ao entrar no 300 (e ao entrar em qualquer estado que não seja da corrente). O 1º golpe da corrente é
o mesmo comando do normal em pé; o normal x em pé **é** o estado 300.

### 5.4 Especial e projétil

```ini
[Command]
name = "proj_x"
command = ~D, F, x
time = 18
```

```ini
[State 1000, Projétil]
type = Projectile
trigger1 = AnimElem = 3
projid = 1000
projanim = 9100          ; animação montada a partir do PNG/JSON do pixelfx
projhitanim = 9101
velocity = 4, 0
attr = S, SP
pausetime = 6, 8
```

### 5.5 Ir para trás e agarrões

```ini
; chegada atrás do oponente, já virado
[State 1600, Atrás]
type = PosAdd
trigger1 = AnimElem = 4
x = p2dist x + 30
[State 1600, Vira]
type = Turn
trigger1 = AnimElem = 4
```

Confira o canto: se `p2bodydist x` + 30 passa da borda (`backedgedist`/`frontedgedist` do oponente), chegue na
frente dele em vez de atravessar a parede.

Agarrões usam `HitDef` com `attr = S, NT`, `p2stateno` e `p2getp1state = 1`:

| Agarrão | `hitflag` | Gatilho extra |
|---|---|---|
| Em pé (800) | `H-` (só em pé) | `p2bodydist x < 10` |
| Agachado (810) | `L-` (só agachado) | `p2statetype = C` |
| Lore (820) | `M-` | por oponente: `p2name = "hazaki"` troca animação e fala |

### 5.6 Despertar

```ini
[Command]
name = "despertar"
command = x+y
time = 1

[State -1, Despertar]
type = ChangeState
value = 2000
triggerall = command = "despertar" && power >= powermax && var(20) = 0
trigger1 = ctrl
```

No 2000: `PowerSet value = 0` só depois que a drenagem começar, `NotHitBy` durante a transformação, `var(20) = 1`.
Golpes exclusivos: `triggerall = var(20) > 0` na entrada deles.

### 5.7 Lista de golpes

Todo golpe do kit aparece no `movelist.dat` (menu de pausa) e na seção do lutador no `README.md`, com a mesma
notação deste arquivo. A lista tem que bater com o `.cmd`.

---

## 6. Regra das ferramentas: como se cria um lutador

Todo lutador sai deste processo, usando as ferramentas de código aberto do GitHub levantadas em
`animacao-pengaro/recursos-github.md` (pasta do projeto) e as ferramentas que já estão em `ferramentas/`. Não pule
etapa, e não use ferramenta "sem licença" no jogo: essas servem só de referência.

| Etapa | Ferramenta | Licença | O que fazer |
|---|---|---|---|
| 1. Ficha | este arquivo, seção 10 | | Escrever a ficha com o kit completo antes de desenhar |
| 2. Poses-chave | `ferramentas/gerar_sprites.py` + `ferramentas/personagens.json` | nossa | Gerar as folhas de poses do personagem |
| 3. Pixel art | `ferramentas/pixelizar.py` | nossa | Converter para 112 px de altura, paleta fechada (ver `docs/proporcoes.md`) |
| 4. Recorte | `ferramentas/recortar_quadros.py` | nossa | Cortar quadros com a âncora nos pés |
| 5. Girar membros | [rotsprite-js](https://github.com/spuuntries/rotsprite-js) / [rotsprite-webgl](https://github.com/adnanlah/rotsprite-webgl) | Apache-2.0 / MIT | Girar braço e perna sem serrilhar (portar o algoritmo para o gerador) |
| 6. Quadros do meio | [ToonCrafter](https://github.com/Doubiiu/ToonCrafter) ou [morphin](https://github.com/javierbyte/morphin) | Apache-2.0 (conferir modelo) / BSD-3 | Criar quadros intermediários entre poses; o resultado volta pelo `pixelizar.py` |
| 6b. Quadros do meio no Blender | `ferramentas/animar_folha.py` + `ferramentas/blender_sprites.py` | nossa ([Blender](https://www.blender.org) é GPL, só o programa) | Entorta o próprio sprite desenhado em malha 2D até a pose seguinte; o gerador usa um desenho por tick. Nunca modelo 3D |
| 7. Retoque | [LibreSprite](https://github.com/LibreSprite/LibreSprite) | GPL-2.0 (só o programa) | Limpar costuras, mão, quadril; o desenho é nosso |
| 8. Gerador | `ferramentas/gerar_<nome>.py` | nossa | Monta SFF, AIR, CMD, CNS e movelist; **não editar `chars/<nome>/` à mão** |
| 9. Caixas e quadros | [openkakutou/character-editor](https://github.com/openkakutou/character-editor), [CharFactory](https://github.com/eduardovbe/CharFactory) | MIT | Abrir SFF/AIR, conferir quadros e caixas de colisão; ajustes voltam para o gerador |
| 10. Combos | [ikemen-combo-finder](https://github.com/KiloTheLoser/ikemen-combo-finder) | MIT | Ler CMD/CNS e conferir que correntes, kombos e cancelamentos encaixam |
| 11. Buffer de comando | [Sakuga-Engine](https://github.com/NoisyChain/Sakuga-Engine) | MIT | Referência de buffer e cancelamento (não usar o motor) |
| 12. Verificação | `ferramentas/verificar_pengaro.py` (e o do lutador) | nossa | Rodar antes de todo commit |
| 13. Intro e vitória | [stage-intro](https://github.com/RealFoobs/stage-intro), [Extended-Intro-Winpose](https://github.com/RealFoobs/Extended-Intro-Winpose) | MIT | Intro e poses de vitória caprichadas |

Ferramenta MIT/Apache/BSD copiada para dentro do repositório leva junto o arquivo de licença (como
`assets/efeitos/LICENSE-pixelfx.txt`). Ferramenta nova que não está nesta lista só entra depois de anotada aqui
com link e licença.

---

## 7. Regra da fluidez: quantos quadros cada animação tem

O jogo roda a **60 ticks por segundo** e tem dois estilos de animação, cada um no seu lugar:

- **Movimento contínuo (ginga, andar, correr, pulo, virar, entrada e vitória): fluido.** Nenhum desenho fica mais
  de **2 ticks** na tela (nunca abaixo de 30 desenhos por segundo). A meta de 1 desenho novo por tick (60 por
  segundo) fica só na ginga, no andar e no corpo do Despertar fora da super.
- **Golpes, reações, defesa e queda: pose segurada.** É o que se mede quadro a quadro nos jogos de luta de arcade:
  o olho lê poses paradas e a troca entre elas é seca. A antecipação segura até 6 ticks; a pose de contato segura
  todo o ativo e mais 1–2 ticks (1 no fraco, 2 no forte); cada pose de recuperação segura 4–9 ticks; o tranco da
  reação segura o elemento inteiro e a pose da defesa segura enquanto dura. **Segurar é sprite parado**, sem
  vai-e-volta e sem quadros do meio. Entre as poses a troca é seca, com no máximo **2 quadros de smear a 1 tick**
  antes do contato.
- **Efeitos, projéteis e o começo da super** andam de 2 em 2 ticks.

**Anatomia vem antes da fluidez (2026-11-11).** Quadro do meio que inventa membro, troca a caneleira de perna, derrete
cabeça ou garrafa **sai**: desenho segurado é melhor que desenho errado. Entremeio só entre dois desenhos quase iguais
(respiração); onde a pose muda muito, a troca é seca. Por isso a ginga e o andar do Pengaró hoje são só desenhos da
folha arcade (8 a 6 ticks e 6 a 5-8 ticks), sem fluxo óptico, e a forma endiabrada dele não usa quadro do meio. A
tabela 7.1 continua sendo a meta, a ser cumprida com **desenho** (folha com mais quadros), não com deformação.

O estilo não muda o frame data (preparação, ativo, recuperação, seção 8.3): o tempo total, a caixa e o tick em que
ela liga ficam iguais. No Pengaró quem aplica isso é `SECO()` e `Air.seco` em `ferramentas/gerar_pengaro.py`, com
um assert que confere soma de ticks, caixa por tick e os `AnimElem` do .cns.

### 7.1 Desenhos por animação

| Animação | Mínimo (obrigatório) | Meta | Observação |
|---|---|---|---|
| Parado / ginga | 16–24 | **32–48** | loop sem emenda: o último quadro encaixa no primeiro |
| Andar, correr | 12–16 | | loop sem emenda, pé não desliza no chão |
| Pulo (subida, topo, queda) | 12–16 | | |
| Agachar, levantar do agachado | 1 desenho, 1–2 ticks | | troca seca |
| Virar | 4–6 | | transição fluida |
| Defesa (entrar, segurar, sair) | 6–8 | | |
| Soco ou chute fraco (normal e cada golpe de corrente) | 4–6 distintos | | antecipação 1, smear 1, contato 1, recuperação 2 |
| Soco ou chute forte (normal e cada golpe de corrente) | 6–9 distintos | | carga, tensão, smear 1–2, contato, 3 poses de recuperação |
| Finalizador de corrente, golpe de kombo | 6–9 distintos | | como o forte; vários acertos: cada contato segurado no seu ativo |
| Especial, projétil (o corpo) | 20–40 | **40–60** | o projétil em si tem animação própria em loop |
| Ir para trás do oponente | 20–40 | **40–60** | é especial: sumir, viajar e chegar virando |
| Agarrão (lutador e vítima) | 30–50 | | as duas animações casadas quadro a quadro |
| Super, ativação do Despertar | 40–80 | **90–150+** | aqui é cutscene de verdade |
| Tomar golpe, cair, levantar | 10–20 cada | | |
| Entrada, vitória, derrota | 30–60 | | |

### 7.2 O que todo golpe precisa ter

1. **Antecipação:** o corpo prepara antes (recua o braço, gira o quadril). É o que avisa o golpe.
2. **Smear (borrão) no movimento rápido:** no fim da antecipação, no máximo 2 ticks (1 ou 2 quadros do meio a 1
   tick cada), o membro estica ou deixa rastro, em vez de pular de uma pose para a outra.
3. **Continuação e movimento secundário:** depois do contato o corpo segue o embalo, e braço, cabelo, roupa e
   faixa chegam atrasados e balançam até parar.
4. **Easing:** começa devagar, acelera e freia. Nada de movimento em velocidade constante.
5. **Contato segurado:** o quadro de contato é o mais forte da animação (o de maior alcance), fica parado o ativo
   inteiro e mais 1–2 ticks, e é nele que entram a caixa de acerto, o efeito e o congelamento.

### 7.3 Como produzir isso sem desenhar um por um

Mesmo o mínimo é muito desenho para fazer na mão. Todo lutador é feito com **esqueleto / recorte (cutout)**: corpo separado em partes
(cabeça, tronco, braço, antebraço, mão, coxa, canela, pé, roupa), montado num esqueleto, com as poses-chave
desenhadas e o resto gerado por interpolação. As ferramentas são as da seção 6: RotSprite para girar as partes sem
serrilhar, ToonCrafter ou morphin para os quadros do meio, `pixelizar.py` para fechar o pixel art e LibreSprite
para retocar. O gerador do lutador (`ferramentas/gerar_<nome>.py`) é quem monta o esqueleto, interpola e exporta.

Estimativa: com o kit mínimo (forma base + Despertar), cada lutador fica com **cerca de 1.500 desenhos** no
mínimo, e chega perto de 3.000 se tudo que tem meta for feito na meta. O SFF aguenta; o cuidado é manter a paleta e a âncora nos pés iguais em todos.

---

## 8. Regra dos efeitos: o estilo pixelfx

Todo impacto, projétil e aura vem do [pixelfx](https://github.com/patch-gg/pixelfx) (MIT, Patch; partes de
Sprite Fusion, Hugo Duprez e Hollow Crown). Os efeitos prontos ficam em `assets/efeitos/` (veja o `LEIA-ME.md` e o
`LICENSE-pixelfx.txt` de lá). O gerador já sabe ler o PNG + JSON (`carregar_faiscas` em
`ferramentas/gerar_pengaro.py`); todo gerador novo reaproveita essa função.

### 8.1 Que efeito em cada golpe

| Situação | Efeito |
|---|---|
| Golpe fraco acertando (correntes x/a, normais fracos) | `hit-spark` |
| Golpe forte acertando | `blunt-hit` ou `hit-flash` |
| Finalizador de corrente, contra-ataque, super | `crit-hit` |
| Defesa | `shield-block` |
| Parry | `parry` |
| Queda no chão (finalizador, agarrão) | `heavy-landing` |
| Golpe no chão / pisão | `ground-slam` |
| Antiaéreo | `uppercut` |
| Projéteis | `fireball`, `energy-disc` ou efeito novo do pixelfx |
| Elétrico | `zap-hit` |
| Carregar / ativar Despertar | `charge-up` |

Use `sparkno = -1` no `HitDef` e solte o efeito com `Explod` no quadro de contato, para usar a arte do pixelfx e
não a faísca padrão do motor. Cada lutador pode recolorir o efeito com a `palette` do pixelfx para ficar com a cara
dele (fumaça roxa do Pengaró desperto, brasa do Hazaki Diabo Loiro).

### 8.2 Fazer efeito novo

Faltou efeito? Faça no pixelfx, não desenhe solto:

```bash
bash ferramentas/exportar_efeitos.sh fire/fireball impacts/crit-hit   # exportar um que já existe (244 no catálogo)
# efeito novo, no clone do pixelfx:
node tools/new.mjs impacts/meu-impacto
node tools/render.mjs impacts/meu-impacto       # olhar a folha de contato e corrigir
node tools/check.mjs impacts/meu-impacto
node tools/render.mjs impacts/meu-impacto --sheet --no-actor --bg none
```

Claude e Codex podem instalar a skill do pixelfx (`skills/pixelfx` do repositório) para criar e refinar efeitos
do jeito que o projeto ensina: desenhar, renderizar, olhar, corrigir. Todo efeito novo entra em `assets/efeitos/`
com PNG + JSON e uma linha na tabela do `LEIA-ME.md`.

### 8.3 Programar o golpe "no estilo pixelfx"

O pixelfx ensina que o que vende o golpe é o corpo: **preparação, congelamento no contato, o alvo balançando e a
recuperação**. Os efeitos com ator trazem esse tempo no JSON (`meta.pixelfx.act`: `windup`, `hits` com `t`,
`freeze`, `shake`, `push`). Todo golpe do jogo segue isso:

| No pixelfx | No CNS do IKEMEN | Piso por tipo de golpe |
|---|---|---|
| `windup` | quadros antes do quadro ativo no AIR | fraco 3–5, forte 7–10, finalizador 10–14 ticks |
| `freeze` (congelar no contato) | `pausetime = P1, P2` do `HitDef` | fraco 7–8, forte 11–12, finalizador/super 14+ |
| `shake` / `amp` | `envshake` no contato | só finalizador e super final; forte e super sem tremida (o peso vem do congelamento) |
| `push` | `ground.velocity` e `guard.velocity` | forte empurra mais que fraco |
| `recovery` | quadros depois do ativo | errar forte tem que doer |
| o alvo balançando | `animtype` do `HitDef` (`Light`, `Medium`, `Hard`, `Back`, `Up`) | casar com a força do golpe |

Efeito nunca aumenta alcance sozinho: a caixa de acerto acompanha o membro visível no quadro ativo.

---

## 9. Checklist de aceite

Copie para o PR do lutador e marque tudo:

```
Forma base
[ ] 16 normais (4 em pé, 4 agachado, 4 no ar, 4 direcionais), com 1 por cima e 1 antiaéreo
[ ] 4 correntes de 3 golpes; finalizador só sai com os 3 acertos e derruba
[ ] 4 kombos de assinatura (1 baixo, 1 por cima, 1 lançador)
[ ] 8 especiais com comando cardinal, sem diagonal, $, meia-lua ou carga
[ ] 2 projéteis com papéis diferentes
[ ] 1 golpe que vai para trás do oponente e chega virado (testado no canto)
[ ] 3 agarrões: em pé (H-), agachado (L-) e lore/comando
[ ] 2 supers (1 e 2 estoques)
[ ] Despertar com barra cheia + 2 botões (ou comando da ficha)
[ ] forma despertada com arte própria redesenhada (não só recolorida)
[ ] aura própria no Despertar, diferente da de todos os outros lutadores (efeito à parte, seção 4)

Forma despertada
[ ] 2 correntes novas, 6 normais novos, 4 especiais exclusivos, 1 projétil novo, 1 kombo novo, 1 super exclusivo
[ ] especiais da base que ficam mudam de pose ou função

Produção
[ ] arte passou pelo processo da seção 6; licenças anotadas
[ ] cada animação tem os desenhos da seção 7.1; no movimento contínuo nenhum desenho passa de 2 ticks
[ ] golpes, reações, defesa e queda em pose segurada (seção 7): contato no ativo + 1–2, recuperação 4–9 por pose,
    smear de no máximo 2 ticks, sem vai-e-volta
[ ] (desejável) ginga, andar e corpo do Despertar na meta de 1 desenho por tick
[ ] todo golpe tem antecipação, smear, contato segurado e recuperação legível (seção 7.2)
[ ] todo impacto usa efeito do pixelfx (seção 8.1), com pausetime/EnvShake pelo piso da 8.3
[ ] caixas conferidas no editor; combos conferidos no ikemen-combo-finder
[ ] gerador roda limpo e o verificador passa; nada editado à mão em chars/<nome>/
[ ] movelist.dat e README batem com o .cmd
[ ] testado no treino dos dois lados e no canto; uma luta CPU x CPU sem erro no log
```

---

## 10. Modelo de ficha do lutador

Toda criação de personagem começa preenchendo isto (em `docs/fichas/<nome>.md`). O "jeito de bater" de cada um
mora aqui.

```markdown
# <Nome>
Estilo de luta: …            Personalidade / falas: …
Cores e paleta: …            Efeitos (pixelfx e recolor): …

## Correntes
| Botão | 1º | 2º | 3º | Finalizador |
| x | | | | |
| y | | | | |
| a | | | | |
| b | | | | |

## Kombos de assinatura (4)
## Especiais (8): nome, comando, fraco/forte, papel (projétil, atrás, antiaéreo…)
## Agarrões (3): em pé, agachado, lore
## Supers (2)
## Despertar: nome, ativação, o que ganha, o que perde
### Correntes novas (2) · Normais novos (6) · Especiais exclusivos (4) · Projétil novo · Kombo novo · Super exclusivo
```
