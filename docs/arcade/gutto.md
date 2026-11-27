# Gutto: arte arcade e kit

> Síntese do estudo arcade de 2026-11-10 (nada testado no motor, nada commitado pela síntese). A fila de geração no
> ChatGPT, com os prompts prontos, fica em [`fila.md`](fila.md); estilo e regras em
> [`../biblia-de-arte.md`](../biblia-de-arte.md#estilo-arcade-anos-90). Folhas de contato e medições brutas ficaram no
> scratchpad da sessão, fora do repo.


## (a) Paleta fixa: 15 cores + transparente

A identidade fica: pele **marrom escura e avermelhada** (mais escura e mais quente que a do Pengaró), calção **preto**,
branco nas ataduras, cós, listras e prajioud. O que muda é que o preto vira azul-roxo muito escuro (com brilho de cetim
lilás), a sombra do branco esfria e a rampa da pele ganha matiz deslocado.

Distribuição (a regra 2 do Pengaró adaptada ao Gutto, que não tem listra colorida, faixa nem garrafa):
pele 5 + contorno de pele 1 + calção 3 + contorno de roupa 1 + branco 3 + cabelo 2 = **15**.

| # | Papel | Hex | H / S / V | Regra |
|---|---|---|---|---|
| 0 | transparente (magenta na folha crua) | `#FF00FF` | — | — |
| 1 | pele sombra funda (vinho; dobras, axila, entre as pernas, boca aberta) | `#4F2620` | 8° / 59% / 31% | 3: sombra 5–15° |
| 2 | pele sombra | `#6E3226` | 10° / 65% / 43% | 3 |
| 3 | pele média (o "tom do Gutto") | `#985630` | 22° / 68% / 60% | 3: médio 21–26° (fica no piso: é o mais vermelho do elenco) |
| 4 | pele luz | `#C4894C` | 30° / 61% / 77% | 3: luz 30–40° |
| 5 | pele brilho (creme; testa, ombro, peito, nó dos dedos, canela) | `#E8C08A` | 34° / 41% / 91% | 9: blocos de 1–3 px |
| 6 | contorno da pele (vinho escuro) | `#3B1A24` | 342° / 56% / 23% | 5: colorido, nenhum canal < 20 |
| 7 | calção sombra (preto do cetim) | `#24203A` | 249° / 45% / 23% | 5 |
| 8 | calção base | `#34304E` | 248° / 38% / 31% | — |
| 9 | calção brilho de cetim (faixa dura, lilás frio) | `#5E5A86` | 245° / 33% / 53% | 9 |
| 10 | contorno da roupa e do cabelo (azul-roxo escuro) | `#1C1830` | 250° / 50% / 19% | 5: nenhum canal < 20 (28,24,48) |
| 11 | branco sombra (fria) | `#9C98C4` | 245° / 22% / 77% | 4: 220–270°, S ≥ 10% |
| 12 | branco médio (frio) | `#CFCCE8` | 246° / 12% / 91% | 4 |
| 13 | branco luz (cós, ataduras, prajioud, olho, dente) | `#F6F3EA` | 45° / 5% / 96% | — |
| 14 | cabelo e bigode (barba só por fazer) | `#2E2229` | 325° / 26% / 18% | 5: nada de preto puro |
| 15 | brilho do cabelo (uma faixa) | `#5A4650` | 330° / 22% / 35% | 9 |

Notas de uso:

- Rampa de pele: a cor média medida hoje (17°) sobe para 22°; quem dá o "vermelho" do Gutto passa a ser a sombra vinho
  (8–10°), não a cor média. Isso mantém a leitura de pele escura avermelhada e deixa a rampa com matiz deslocado.
- O preto do calção nunca é `#000`: lê como preto pelo contraste com o branco do cós e o creme da pele.
- Prajioud (braçadeira de corda) em branco 11–13 com o enrolado em contorno 10; as pontas soltas também (regra 12: atrasam).
- Sel-out (regra 6): no lado da luz o contorno da pele vira a cor 2 e o da roupa vira a cor 7.
- O coração do Beijinho (`coracao()` em `gerar_gutto.py`) é efeito, fora destas 15; usa rampa própria rosa
  (`#ff5fa2`, `#ffc2dc`, `#5a0f2e`), que já não colide com nenhuma cor do corpo.
- Endiabrado (demônio cavalo, folhas `e_`): paleta própria de 15 no mesmo esquema. Sugestão a medir nas `e_`:
  pelo/pele quase preta em 4 tons (`#2A1A22` `#3E2430` `#5A3440` `#7A4A52`), rachadura e olho em brasa 3 (`#8E1E1E`
  `#D8402A` `#FFB45A`), crina 2 (`#22161E` `#4A3040`), casco e chifre 2 (`#4A3A34` `#8A7462`), calção rasgado = cores 7 e
  8 do normal, contorno vinho-preto `#24141C`, fumaça da bufada `#E8DCE0` (15). Não medido ainda; meça antes de fixar.

---

## (b) Prompt base e blocos MOTION

### Prompt base, forma normal (troque só o bloco MOTION; anexe `referencia_idle.png` em toda folha)

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, outfit. A muscular Muay Thai
fighter with dark reddish-brown skin, short tightly curled black hair, a thick black mustache and light stubble, narrow
intense eyes. Shirtless. Plain black satin Muay Thai shorts with a wide white waistband and white piping along the side
slits and the hem, no logo, no text. Short white hand wraps on both hands covering knuckles and wrists (not boxing
gloves). Twisted white-and-black rope armbands
on both biceps with two short hanging tails. Barefoot. No headband, nothing in the hands.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward deep wine red,
highlights toward warm cream; the black shorts are very dark blue-violet with one hard lilac satin sheen, never pure
black; the white wraps, waistband, stripes and armbands get cool lilac-blue shadows, never grey or beige. 1-pixel colored
outline (dark wine on skin, dark blue-purple on clothes and hair), never pure black, lighter or missing on the lit side.
Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair.
Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line, every limb fully inside its own frame. Flat solid magenta background
(#FF00FF) everywhere, no shadow, no ground, no text, no numbers, no borders, no effects.
MOTION: <bloco da folha>
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

### Prompt base, Endiabrado (folhas `e_<nome>` e `endiabrado`; anexe `demonio_modelo.png`)

Mesmo texto, trocando a descrição do personagem por: *"the same fighter turned into a horse demon: half-horse half-man
face (muzzle, ears, short horns, mane, red glowing eyes, the same thick mustache), bigger hunched hairy human body, near
black skin with glowing red cracks, claws, horse legs with hooves, a tail, only the torn black shorts with the white
waistband and the rope armbands"*; a sombra do corpo vai ao vinho e a luz à brasa; o MOTION é o da folha normal de mesmo
nome, lido como fera (soco vira patada de garra, chute vira coice/pisão, joelhada vira chifrada), nos **mesmos 8 tempos**
e com contato no **mesmo quadro** da normal (o `RemapSprite` troca desenho por desenho e as caixas de golpe não mudam).

### Folhas em ordem (MOTION como vai no prompt)

| Lote | Folha | Usada em | MOTION |
|---|---|---|---|
| 1 | `ginga` | ações 0 parado, 5 virar | standing tall in a high Muay Thai guard, hands at face height, weight on the rear leg, the lead foot light; rhythmic bounce: 1–4 sink and the lead heel lifts, 5–8 rise; frame 8 loops into frame 1; armband tails lag one frame behind the body; shorts hem sways. |
| 1 | `anda` | 20, 21 andar; 100 corre, hoje sem folha própria | guarded walk forward, two steps per cycle: 1 guard, 2 lead foot lifts (anticipation, body leans back a little), 3 lead foot reaches, 4 weight transfers, 5 rear foot passes, 6–8 back to guard; hands stay up but bob with each step; shorts fold at the knee of the stepping leg. |
| 1 | `defesa` | 120–152 guarda, 105 recuar, 760/761 parry | compact standing block: 1 guard, 2 forearms snap up to cover the face and ribs, elbows tight, chin down, 3–5 hold (5 = impact: body pushed back 2 px, feet slide), 6–8 back to guard. Both feet stay on the ground (no lifted shin). |
| 1 | `agachado` | 10–12 agachar, 131/141/151 guarda baixa, 841, 5025–5027 | 1 guard, 2 knees start to bend (anticipation), 3–5 drop into a low crouch, hands still high, 6 hold, 7 crouching guard with forearms in front of the face, 8 equal to 6. Shorts spread over the thighs. |
| 2 | `apanha` | 5000–5035, 5300 | hit reaction: 1 guard, 2 head snaps back, chin up, 3 torso twisted away, arms thrown open, 4 deepest recoil (stretch 10%), 5 starts recovering, 6–8 guard again (recovery longer than the hit); armband tails and shorts lag 1–2 frames. |
| 2 | `soco` | 200 jab, 201 trás+x, 301 corrente x 2º, 340, 3100, 3433 | ONE quick lead jab only: 1 guard, 2 lead shoulder loads and hips coil, 3 step-in, 4 fist travels, 5 contact: fist and forearm drawn 15% larger, shoulder thrust forward, torso turned showing the chest, 6 hold, 7–8 back to guard. No second punch in the sheet. |
| 2 | `chute_baixo` | 230 low kick, 231, 245 b perto, 312, 321, 1500/1501 Chute de Quina, 3411, 3434 | standing low roundhouse kick to the thigh: 1 guard, 2 rear hip turns, lead foot pivots (anticipation), 3 rear shin swings low, 4–5 contact (same drawing held): shin and foot 15% larger at knee height, hips fully turned forward, the shorts' leg flares open, 6–8 long recovery stepping back to guard. |
| 2 | `chute_alto` | 240 b longe, 246, 323, 331, 341, 346, 1701, 3100, 3401, 3420, 3432 | heavy high roundhouse: 1 guard, 2–3 big wind-up (lead foot pivots, arms counter-swing, torso coils away), 4 leg whips up, 5 contact: shin and foot stretched 15% at head height, hips through, rear arm thrown back, 6 hold, 7–8 long recovery; foot stays inside its frame. |
| 2 | `martelo` | 210/215 y forte, 216, 302, 311, 343/344, 1400/1401 Cotovelo Giratório, 3200, 3410, 3431 | horizontal elbow strike: 1 guard, 2 elbow cocked high and back (anticipation), 3 step-in, 4 elbow swings across, 5 contact: elbow point 15% larger at head height, shoulder rolled forward, torso turned, 6 hold, 7–8 back to guard. |
| 2 | `pulo` | 40–47 | 1 crouch to jump, 2 push-off, 3 rising, 4 apex with knees tucked and hands high, 5 starting to fall, 6 legs extend for landing, 7 landing crouch, 8 guard. Armband tails lag. |
| 2 | `queda` | 5040–5170 | knockdown: 1 hit hard, 2 lifted off the feet, body arching back, 3–4 flying back, 5 back hits the ground with legs up, 6 bounce, 7–8 lying flat. Shorts and tails lag. |
| 2 | `levanta` | 5120 | get up from lying on the back to guard: 1 lying, 2 rolls to the side, 3 sitting, 4 one knee, 5 pushing up, 6–7 rising, 8 guard. |
| 2 | `baixo_soco` | 400 | crouching jab; 1 and 8 equal the crouch pose of agachado 6; 2–3 shoulder loads, 4–5 contact with fist 15% larger (same drawing held), 6–8 back to crouch. |
| 2 | `rasteirinha` | 430 agachado a, 322, 342 | crouching low teep to the shin: 1 crouch, 2 knee chambers low, 3 foot pushes out, 4–5 contact (same drawing held): sole forward 15% larger at ankle height, 6–8 crouch again. |
| 2 | `cabecada` | 410 agachado y, 303, 347, 831 clinch, 3412, 3430 | rising knee from the crouch (anti-air shape): 1 crouch, 2 sinks deeper (anticipation), 3 drives up, 4 knee rising to chest, 5 contact: knee 15% larger above the head line, arms pulled down, 6 hold at the top, 7–8 back down to crouch. |
| 2 | `rasteira` | 440 agachado b, 841, 3100, 3435 | low sweep that knocks down: 1 crouch, 2 hands to the floor, 3 rear leg sweeps, 4–5 contact: leg fully stretched 15% along the floor, pants leg flared, 6 sweep ends, 7–8 crouch. |
| 2 | `afastar` | 260 teep, 332, 345, 831 | push kick: 1 guard, 2 knee chambers high (anticipation), 3 hips forward, 4 sole extends, 5 contact: sole 15% larger at belly height, torso leaning back, 6 hold, 7–8 recovery. |
| 3 | `armada` | 313, 1200/1201 Joelhada Voadora, 3100, 3422/3423 | 1 guard, 2 deep crouch turning the back (anticipation), 3 jumps up spinning, 4 rising, 5 contact at the top: lead leg stretched 15% at head height, 6 apex, 7 falling, 8 landing in guard. |
| 3 | `compasso` | 333, 348, 1100/1101 Chute Giratório, 3100, 3413 | spinning back kick: 1 guard, 2 step across, 3 turns showing the back, 4 head looks over the shoulder, 5 contact: heel and leg 15% longer straight to the front, 6 hold, 7–8 unwinds to guard; shorts and tails lag the spin. |
| 3 | `bola` | 1000/1001/1005 Beijinho, 1600/1601 Beijinho em Arco | blowing a kiss: 1 guard, 2 hand to the lips, 3 kiss, puckered lips, 4 arm throws forward, 5 release: open palm 15% larger toward the front, torso turned, 6 hold, 7–8 back to guard. NO heart, sparkle or effect drawn (the heart is a separate sprite). |
| 3 | `caneta` | 1300/1301 Carrinho, 349 | football slide tackle: 1 guard, 2 two quick steps, 3 drops to the side, 4–5 sliding with lead leg stretched 15% low, 6 slide ends, 7 gets up, 8 guard. |
| 3 | `rolamento` | 700/705 rolar, 1700/1701 Teleporte de Ginga, 3402, 5200/5210 | forward roll: 1 guard, 2 tuck, 3–5 roll as a tight ball, 6 coming out on one knee, 7 rising, 8 guard. |
| 2 | `bicicleta` | 610/611 chute no ar, 650, 3403 | air knee/kick: 1 jump pose, 2 knee chambers, 3 extends, 4–5 contact (same drawing held): flying knee and shin 15% larger diagonally down-forward, 6–8 tuck back. |
| 2 | `ar_soco` | 600/601 | air elbow down: 1 jump pose, 2 elbow raised high behind the head (anticipation), 3 swings down, 4–5 contact (same drawing held): elbow tip 15% larger in front of the chest, pointing down-forward, 6–8 tuck back. |
| 3 | `agarrao` | 800, 810, 830, 831, 840 | clinch grab and throw: 1 guard, 2 steps in, 3 both hands reach forward, 4 hands lock behind an (invisible) opponent's neck, elbows tight, 5 pulls the head down, 6 pivots on the lead foot turning the opponent, 7 throws him past the hip, arms opening, 8 follow-through held. |
| 3 | `golaco` | 3000 Chuva de Beijinhos, 3400, 13000 | super finisher: 1 guard, 2 deep crouch (anticipation), 3 rising knee, 4 high kick, 5 turn, 6 second high kick, 7 contact: leg stretched 15%, 8 victory roar still in side view. |
| 3 | `lata` | 190–192 entrada, 3011 | intro: walks in, removes nothing, cracks neck, slaps the armband, settles into guard; frame 8 equal to ginga frame 1. Same scale as ginga. |
| 3 | `provoca` | 195 | taunt: 1 guard, 2–4 opens arms wide inviting, 5 shakes the shoulders, 6 points at the opponent, 7–8 back to guard. |
| 3 | `vitoria` | 181 | 1 guard, 2–3 arms rise, 4 fists high, 5–6 flexes, 7 points forward, 8 hold. |
| 3 | `derrota` | 170 | falls to sitting, exhausted, head down; 1 standing hurt, 2–4 collapsing, 5–8 seated. Same scale as ginga. |

## (c) Kit na essência arcade 90

> **Atenção, conflito com as regras do projeto.** A seção 2 de `regras-dos-lutadores.md` proíbe diagonal, `$`,
> meia-lua, 360° e carga no comando de especial (especial = 2 toques cardeais + botão; super = 3 toques, `~B,F,D`
> + chute ou soco, seção 3.H), e a 3.G manda todo agarrão ter escape com y ou b. Os itens abaixo que pedem
> diagonal, meia-lua, meia-lua dupla ou agarrão sem escape seguem a convenção do gênero e **só entram se o Breno
> mudar a regra**. O resto (invencibilidade do antiaéreo, só o forte de perto cancela, tremor, contra-ataque,
> folhas novas) não depende disso.

Notação do `.cmd`: F frente, B trás, D baixo, DF diagonal; x/y socos fraco/forte, a/b chutes fraco/forte. Os nomes
internos do `.cmd` do Gutto ainda são os do Pengaró ("Bando da Várzea", "Mão de Chimpá", "Garrafada", "agarrao_whisky"):
o kit é o do Pengaró com outra arte.

### Já existe

| Item | Estado hoje | Folha |
|---|---|---|
| Normais em pé x/y/a/b, perto e longe | 200, 210 (y longe), 215 (y perto), 230, 240 (b longe), 245 (b perto) | soco, martelo, chute_baixo, chute_alto |
| Agachado x/y/a/b | 400, 410 (joelhada subindo), 430, 440 (rasteira derruba) | baixo_soco, cabecada, rasteirinha, rasteira |
| Comando de direção | 201 B+x, 216 F+y, 231 B+a, 246 F+b | soco, martelo, chute_baixo, chute_alto |
| No ar | 600/601 (x/y), 610/611 (a/b), 650 | ar_soco, bicicleta |
| Correntes de 4 | 300–333 (x, y, a, b) | várias |
| Kombos | 340–349 | várias |
| Projétil | Beijinho 1000/1001 `~D,F` + a/b; Beijinho em Arco 1600/1601 `~F,B` + x/y | bola (+ coração em código) |
| Antiaéreo especial | "Joelhada Voadora" 1200/1201 `~F,D` + x/y (Z); o desenho é chute giratório saltado | armada |
| Especiais | 1100/1101 Chute Giratório `~D,B` + a/b; 1300/1301 Carrinho `~D,B` + x/y; 1400/1401 Cotovelo `~D,F` + x/y; 1500/1501 Chute de Quina `~B,D` + a/b; 1700/1701 Teleporte `~F,B` + a/b | compasso, caneta, martelo, chute_baixo, rolamento |
| Forte de perto cancelável | 215 e 245 estão em "Pode cancelar" (movecontact ≤ 8) | martelo, chute_baixo |
| Agarrão normal / agachado | 800 (B/F+y), 840 (D+y) | agarrao |
| Agarrão de comando | Clinch 830–833 `~B,F` + y (joelhada 60 + teep 90) | agarrao, cabecada, afastar |
| Supers | Chuva de Beijinhos 3000 `~B,F,D` + a/b; Saideira 3100 (vida ≤ 200 ou Endiabrado); 3200 `~B,F,D` + x/y | golaco; mistura de folhas |
| Sistema | correr 100, recuar 105, rolar 700/705, afastar 260/720, parry 760, Despertar 2000 `x+y` | anda, defesa, rolamento, afastar |
| Endiabrado | 3400–3435 exclusivos e correntes `~D,D` | `e_*` |

### Diferente do gênero ou faltando (ordem por impacto)

| # | Mudança | Estado hoje (ação/estado) | Alvo | Folha nova? |
|---|---|---|---|---|
| 1 | **Antiaéreo de verdade.** O desenho (`armada`) é chute giratório saltado, não joelhada: não copia golpe-assinatura; só o nome "Joelhada Voadora" não bate com o que se vê. Opção A (barata): manter `armada`, corrigir a invencibilidade e renomear. Opção B: **Cotovelo de Torre** (cotovelo subindo, sai pouco do chão) | 1200/1201: `NotHitBy SCA` só com `Time < 5`, e o primeiro `Clsn1` do Action 1200 está no 7º elemento (6 ticks de 1): há ~1 tick vulnerável antes do ativo | `~F,D,DF` + x/y; x: startup 4, invencível a golpe aéreo 1–5; y: startup 3, invencível do 1 até o fim do ativo, recuperação ~28, lança | A: não; B: `cotovelo_sobe` (+ `e_cotovelo_sobe`, chifrada subindo) |
| 2 | Só o forte **de perto** cancela | "Pode cancelar" lista 210 (y de longe) junto de 215; 240 (b longe) fica fora, ok | tirar 210 da lista | não |
| 3 | Forte de longe e de perto com desenho diferente | 210 e 215 usam a mesma `martelo`; 245 (b perto) usa `chute_baixo` | y longe = cruzado longo; b perto = joelhada (folha `cabecada`, sem folha nova) | sim: `soco_forte` (cruzado de trás, longo) |
| 4 | Comandos com diagonal | tudo cardeal: `~D,F`, `~D,B`, `~F,D`, `~B,D`, `~F,B`, `~B,F,D` | meia-lua `~D,DF,F`, meia-lua de trás `~D,DB,B`, Z `~F,D,DF`; cardeais ficam como folga | não |
| 5 | **Agarrão de comando** no movimento do gênero | 830 sai de `~B,F` + y, com janela de escape | Clinch de Joelhadas: meia-volta `~B,DB,D,DF,F` + y, startup 1, alcance curto, sem escape, ~150 de dano, 30 ticks abertos se errar | sim: `clinch` (mãos travadas na nuca, 3 joelhadas; hoje `agarrao` q5–6 dá a joelhada sem segurar) |
| 6 | **Super com meia-lua dupla** | 3000 e 3200 em `~B,F,D` | Chuva de Beijinhos `~D,DF,F,D,DF,F` + a/b; Super de joelhadas e cotovelos `~D,DB,B,D,DB,B` + x/y; invencível do tick 1 ao fim do superpause | não para o comando; a 3200 hoje é colagem de folhas: `super_joelhos` (sequência de joelhada/cotovelo) |
| 7 | Saideira (vida baixa) com comando próprio | 3100 divide o comando com a 3000 | `~D,DF,F,D,DF,F` + x+y | não |
| 8 | Super máximo (2 estoques, 1,5x dano, termina lançando) | não existe | `~D,DF,F,D,DF,F` + a+b | sim: `super_final` (último quadro de lançar) |
| 9 | Especial no ar | todo especial exige `statetype != A` | Cotovelada Descendente: no ar `~D,DF,F` + x/y, startup 8, bate por cima, quica para trás no acerto | sim: `ar_cotovelo` (`ar_soco` refeita pode servir, ver (d)) |
| 10 | Correr de verdade | 100 usa os quadros de `anda` | ciclo de corrida de 8 quadros; no Endiabrado vira galope | sim: `corre` e `e_corre` (galope) |
| 11 | Impacto pesado | — | EnvShake 6–8 ticks nos fortes e no low kick que derruba; pausetime 8/6, 12/9, 16/10 | não (som próprio) |
| 12 | Contra-ataque | não existe | acerto no startup do outro: +4 de hitstop, "CONTRA!" | não |
| 13 | Low kick como ferramenta | 230 é chute fraco; 312/321 nas correntes | o low kick (230 e o 231 `B+a`) derruba quando acerta em contra-ataque; -6 na defesa | não (`chute_baixo`) |
| 14 | Conferências | — | passo para trás invencível ~4 ticks; pulinho ~30 ticks; rolamento 20–24, agarrável nos últimos ~6; Carrinho -10 na defesa | não |

Decisões para o Breno (não implementar sem resposta): correntes de 4 (o sabor do gênero é no máximo 2 + cancel), o
Beijinho no chute (no gênero o projétil costuma sair no soco; aqui é beijo, tanto faz, mas a 1600 em `~F,B` + soco
encosta no Teleporte `~F,B` + chute), e se o Teleporte vira meia-lua de trás para não disparar sem querer com o
Beijinho em Arco.

---

## (d) Problemas que já aparecem nas folhas

Visto na folha de contato e em ~30 quadros a 0,4–0,55x; nada conferido pixel a pixel em todos os 520 quadros. Quadros
contados de 1 a 8.

| Folha | Quadro | Problema |
|---|---|---|
| todas as normais | todos | pintura com milhares de cores (24.179 em `ginga` q1), abdômen e braço com gomos e veias, degradê: viola regras 1, 7, 8; calção e cabelo em preto puro; branco com sombra bege |
| todas | borda | franja de magenta escuro (`#951980`, `#4b142a`) no contorno: o recorte não limpa |
| `lata`, `derrota` | todos | folha 1672x941: figura ~12% maior (o `animar_folha.py` reduz); pele mais clara e amarela (23°/V67, 22°/V69) que `ginga` (18°/V56): o Gutto clareia entre folhas |
| `chute_baixo` | todos | folha 1916x821, outra escala; personagem menor na célula |
| `e_martelo`, `e_rasteirinha` | todos | folha 2508x627: demônio maior que nas outras `e_` |
| `soco` | 3 e 6 | dois socos (jab e cruzado, pedidos assim em `folhas_gutto.py`), com volta à guarda em 4–5: o jab "dobra"; o gerador usa q6 como pose de contato (`soco1/2`, `p["soco"]`), então a refeita precisa manter o braço esticado em q6; no contato o punho não alonga, o ombro não vem à frente; punho do q6 encosta na borda da célula |
| `ar_soco` | 3–4 | os dois punhos sobem junto da cabeça, nenhum membro estende: o golpe aéreo não mostra contato |
| `defesa` | 3–8 | joelho levantado (o "check" do Muay Thai, pedido de propósito em `folhas_gutto.py`): na guarda baixa lê como vulnerável; mão de trás e joelho trocam de altura entre 6 e 7. Tirar é decisão do Breno (muda a cara do personagem) |
| `bola` | 4–5 | coração e brilhos rosa desenhados na folha junto da mão, somados ao coração do código: projétil em dobro |
| `cabecada` | 5 | grão de pixels solto no chão à esquerda |
| `chute_alto`, `compasso`, `golaco` | 5, 5, 7 | pé na borda da célula de 1/8: risco de cortar o pé no recorte; conferir o quadro recortado |
| `golaco` | 7–8 | q7 tem pixels roxos na cintura; q8 vira o corpo de frente para a câmera (sai da vista de lado) |
| `agarrao` | 5–6 | a joelhada sai com as mãos em guarda, sem segurar o oponente: o agarrão não mostra a pegada |
| `anda` | 1–8 | braços congelados na mesma guarda nos 8 quadros (só as pernas andam) |
| `despertar_a` → `despertar_b` | a8 → b1 | troca de personagem entre quadros: termina cavalo, recomeça humano (já anotado na ficha) |
| `e_rasteirinha` | 1–8 | o demônio fica em pé bufando nos 8 quadros: não há chute baixo, e as ações 430/322/342 no Endiabrado batem baixo com desenho em pé |
| `e_chute_alto` | 4–5 | coice com o corpo deitado e as patas para trás; a caixa de golpe vem da ação normal (para a frente): conferir lado do `Clsn1` no vídeo |
| `e_chute_baixo` | 4–5 | vira pisão no lugar, com o pé quase no mesmo ponto: o alcance do low kick normal fica sem desenho |
| `endiabrado` | 7 | fogo laranja da bufada desenhado no corpo (efeito dentro da pose, fora da paleta) |

---

## Revisão do cético

Conferido contra as folhas (abertas `ginga` q1 ampliado, `armada`, `defesa`, `soco`, folha de contato), `folhas_gutto.py`,
`gerar_gutto.py`, `gerar_pengaro.py` (só leitura) e `chars/gutto/`. Hex da paleta recalculados: os 15 HSV batem, nenhum
canal < 20, sombra do branco 245–246° com S 22/12%. Mediana de pele recalculada: ginga 18°/V59, lata 23°/V71, derrota
22°/V72, soco 20°/V59 (confirma a variação). Tamanhos das folhas confirmados (2170x725; lata/derrota 1672x941;
chute_baixo 1916x821; e_martelo/e_rasteirinha 2508x627). 65 folhas = 62 de animação + 3 referências que o gerador não
usa (`referencia_idle`, `referencia_idle_v2_camisa`, `demonio_modelo`).

**Corrigido no texto:**
- Prompt base mudaria o personagem: "thin beard" e "big round eyes" não existem na folha (bigode + barba por fazer,
  olhos estreitos e bravos, como em `folhas_gutto.py`); o calção tem **friso branco na fenda lateral e na barra**, não
  "uma listra"; o prajioud é corda **trançada branco e preto**. Paleta 14 deixa de citar barba.
- `armada` não é joelhada: é **chute giratório saltado** (q5 perna esticada na altura da cabeça). O item 1 do kit dizia
  que a 1200 copiava golpe-assinatura comercial de joelhada subindo; o desenho não é isso, só o nome. Reescrito como
  opção A (manter `armada`, consertar invencibilidade, renomear) ou B (`cotovelo_sobe`).
- MOTION que mexeria no `.air`: o gerador lê quadros por índice fixo (`gerar_pengaro.py`, tabela ~l.866 e
  `folha_do_golpe` ~l.1391), quase sempre q5 (índice 4) como contato. `chute_baixo`, `baixo_soco`, `rasteirinha`,
  `bicicleta` e `ar_soco` pediam contato em q4 com "hold" em q5: virou "4–5 contato, mesmo desenho segurado".
- `agarrao`: o MOTION punha a joelhada em q6–7, mas `joga` = q7 e a 810 segura q8 por 10 ticks como arremesso; a joelhada
  do clinch já vem de `cabecada`. MOTION trocado para pegada + arremesso.
- `defesa`: o joelho levantado começa em q3 (não q4) e é o "check" do Muay Thai pedido de propósito; ficou como decisão
  do Breno, não defeito.
- `soco`: os dois socos foram pedidos (jab + cruzado) e o gerador usa q6 como pose de contato; anotado que a refeita
  precisa do braço esticado em q6.
- Preto puro: há `#000000` exato em `ginga` q1, não só `#070405`.

**Ficou em dúvida (não mexi):**
- Paleta do Endiabrado: o prompt manda "white waistband and rope armbands", mas os 15 sugeridos não têm branco (só a
  fumaça `#E8DCE0`, que teria de fazer as duas coisas). Medir as `e_` antes.
- NotHitBy da 1200: `Time < 5` com `time = 1` e `Clsn1` no tick 6: buraco de 1 a 2 ticks; confirmar no vídeo da sandbox.
- Itens 2–14 do kit (cancel do 210, diagonais, meia-volta, meia-lua dupla, super máximo, contra-ataque) conferidos no
  `.cmd` e coerentes, mas são decisão de jogo; nada testado no motor.
- Não conferi pixel a pixel `bola` (coração desenhado), `cabecada` q5 (grão), `golaco` q8 nem `e_chute_alto` (lado do
  coice); ficaram como o autor escreveu.

## Pendência de pipeline

`quantizar_folha.py` só conhece os papéis do Pengaró (`PAPEIS = {"pengaro": ...}`) e `conferir_arte.py` mede a regra 3
nas faixas do Pengaró. Antes da primeira folha deste lutador passar pelo pipeline: acrescentar os papéis dele em
`PAPEIS`, rodar `LUTADOR=gutto python ferramentas/quantizar_folha.py --montar-paleta <folha>` e conferir o JSON contra a
tabela de paleta acima.
