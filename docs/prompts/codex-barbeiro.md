# Prompt para o Codex: criar o lutador Barbeiro

> Copie tudo abaixo da linha e cole no Codex, dentro do repositório `jogo-de-luta`.

---

Você vai criar o lutador **Barbeiro** (id `barbeiro`) para o jogo de luta em IKEMEN GO, no repositório
`brenoalmeidatec/jogo-de-luta`. Trabalhe na branch `mugen` (`git pull` antes de começar). Não mexa na `main`.

## 0. Leia antes de mexer em qualquer coisa

1. `docs/regras-dos-lutadores.md` é lei: kit mínimo, comandos cardeais, correntes, Despertar, fluidez, pixelfx,
   checklist de aceite (seção 9). Siga **à risca**.
2. `docs/fichas/barbeiro.md` é a ficha dele, já pronta, com todos os golpes (50 na base + 20 novos no Despertar).
   Não invente golpe nem mude comando: se algo ficar impossível, ajuste e anote na ficha.
3. `sprites/barbeiro/referencia.png` é a arte de referência do personagem.
4. `AGENTS.md`, `ferramentas/gerar_pengaro.py`, `ferramentas/gerar_folhas.py`, `ferramentas/entremeio.py`,
   `ferramentas/recortar_quadros.py` e `ferramentas/verificar_pengaro.py`: o Barbeiro segue o mesmo padrão de gerador.

## 1. Quem é

Barbeiro musculoso e psicopata simpático, sorriso largo e olhos arregalados. **Braço direito mecânico com tesoura
gigante no lugar da mão. Braço esquerdo humano enorme, mão sempre rodando um pente.** Camisa e avental pretos com friso
prateado, distintivo de barbearia (tubo listrado) no bolso, pente e pincel de barba no avental, calça preta larga,
sapato preto, cabelo crespo curto com degradê, cavanhaque. Mantenha **exatamente** o rosto, corpo e roupa da referência
em todos os quadros. Ele olha para a direita nas folhas, 120 px de altura, pé na linha do chão.

Despertar (**Surto de Tesoura**): cabelo continua **preto**, ainda mais musculoso, veias saltadas, olhos esbugalhados,
sorriso insano, faísca na ombreira do braço mecânico. É arte **redesenhada**, não recolor. Não precisa de visual de
diabo: é o mesmo barbeiro, só que pior.

## 2. Estilo de arte (inegociável)

**Toda arte sai em pixel art desenhada no estilo sprite de SNES / arcade antigo (Neo Geo, Capcom CPS2).** Pode ter mais
quadros para ficar fluido, mas **nunca** visual 3D pixelizado (tipo personagem low-poly de PS1). Blender, se usado,
vale só como **referência de pose** e nunca entra no jogo.

Siga também o guia de direção de arte do KIKIU (`brenoalmeidatec/KIKIU-Survival`, `docs/DIRECAO_DE_ARTE.md`), seção 3 e
6.2 (gênero luta). O que vale aqui:

- Grade de **1 px** única no jogo inteiro. Escala só **inteira** (nada de 0,7x; refaça a folha na grade final).
- **Alfa binário** (0 ou 255) nos sprites. Sem meio-transparente, sem halo.
- **Paleta fechada**: no máximo **40 cores** por personagem (e no máximo 48 no Despertar), sem dithering. 3 a 5 tons por material.
- **Contorno escuro de 1 px** em pelo menos 90% da borda, sem pixel solto. Sprite nunca encosta na borda do quadro.
- **Nunca girar sprite com filtro**. Para girar membro use RotSprite (`regras-dos-lutadores.md`, seção 6); poses
  intermediárias pré-desenhadas valem mais.
- Impacto, projétil e aura vêm do **pixelfx** (`assets/efeitos/`, seção 8 das regras), escala inteira (2).
- "Reduzir piscadas": nenhum efeito pisca mais de ~3 trocas de luminância por segundo; flash de acerto com alfa fixo.
- Sem marca real, sem texto em imagem (o distintivo é só o tubo listrado, sem letra).
- Faça o conferidor de sprite do KIKIU rodar nas folhas (`ferramentas/conferir_objeto.py` de lá, ou porte a regra:
  alfa binário, <= 40 cores, contorno, sem pixel solto).

## 3. Processo (uma fase por commit)

**Fase 1: folha-modelo.** Cadastre o `barbeiro` em `ferramentas/personagens.json` (descrição da seção 1 em inglês,
`"altura": 120`). Gere a primeira folha (`soco`/`x1`) a partir de `sprites/barbeiro/referencia.png`. Ela vira a
**referência de personagem** de todas as outras, como o `soco.png` do Pengaró. Pare e confira com o Breno se ficou
idêntico à referência (rosto, tesoura, pente, avental).

**Fase 2: folhas de animação.** Copie `ferramentas/gerar_folhas.py` para `ferramentas/gerar_folhas_barbeiro.py` com o
dicionário `FOLHAS_BARBEIRO` da seção 4 (cada folha: 8 quadros em fila, fundo magenta, virado para a direita). Gere com o
Codex (`codex exec`), recorte com `recortar_quadros.py` e refaça a que vier com figura cortada, rosto diferente, texto,
marca ou aparência 3D. Folha que já existe é pulada.

**Fase 3: fluidez.** Use `ferramentas/entremeio.py` (e o fluxo da seção 6/7.3 das regras) para chegar nos mínimos de
desenhos da tabela 7.1: fraco 8–12, forte 14–20, especial 20–40, super e transformação 40–80, ginga 16–24 (meta 32–48).
Nenhum desenho fica mais de 2 ticks no ar fora do `pausetime`. Todo golpe tem **antecipação, smear nos 1–3 quadros
rápidos, continuação (avental, tesoura, pente balançam) e easing**.

**Fase 4: gerador.** `ferramentas/gerar_barbeiro.py` monta `chars/barbeiro/` (SFF, AIR, CMD, CNS, `movelist.dat`,
`.def`). **Não edite `chars/barbeiro/` à mão.** Siga a seção 5 das regras (faixas de estado, ordem do
`[Statedef -1]`, correntes com `var(6)`, finalizador só com 3 acertos, Despertar com `var(20)`, animações do Despertar
= base + 10000). Efeitos com `Explod` do pixelfx, `pausetime` e `EnvShake` pelo piso da seção 8.3.

**Fase 5: Despertar.** Repita as fases 2–4 para a forma despertada (seção 5 deste prompt).

**Fase 6: verificação.** Crie `ferramentas/verificar_barbeiro.py` (modelo: `verificar_pengaro.py`). Rode:
gerador, verificador, treino dos dois lados e no canto, e uma luta CPU x CPU sem erro no log. Preencha o checklist da
seção 9 das regras no PR. Selecione-o na tela de seleção (retrato e `select.def`), como já está o Pengaró.

## 4. Folhas da forma base (`FOLHAS_BARBEIRO`)

Cada linha é uma folha de 8 quadros. Âncora: `pes` (padrão) ou `cabeca` (quando sai do chão). "forte" tem 2 folhas
encadeadas (`_a`, `_b`) para dar os quadros da tabela 7.1. Descrições são o texto em inglês que vai no prompt de imagem.

**Cabeçalho comum** (igual ao `CABECA` do Pengaró, trocando o personagem): *Generate ONE image with your image
generation tool. Do not write code and do not edit any file. The attached sprite sheet shows the exact character and art
style to keep: same muscular barber, same grinning psycho face with wide eyes, short curly black hair with fade and
goatee, black short-sleeve shirt with silver trim, striped barber-pole badge on the pocket, black apron with a comb and
shaving brush, loose black pants, black shiny shoes, huge muscular left arm spinning a comb in the hand, mechanical
right arm with dark steel shoulder plate and a giant pair of scissors instead of a hand. Hand-drawn 16-bit arcade pixel
art like a SNES or Neo Geo fighting game sprite, NOT 3D, NOT low-poly, clean 1 px dark outline, flat colors with 3 to
5 tones, magenta background. Layout: one single row of 8 frames in 8 equal-width cells, side view, always facing
right, same scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its cell and never touches the cell edge. Consecutive frames differ by a small amount so the motion looks
smooth. Include anticipation, a smear on the fastest frames and follow-through of the apron and scissors.*

### 4.1 Movimento e sistema

| id | âncora | Movimento |
|---|---|---|
| `ginga` (2 folhas, loop) | cabeca | Barber fighting stance loop: weight rocking side to side, left hand spinning the comb between the fingers, scissors blades slowly opening and closing, apron swaying, breathing in the shoulders. Last frame matches the first. |
| `anda` (2 folhas, loop) | cabeca | Heavy confident walk forward, torso upright, scissors held forward and snipping, comb spinning in the other hand, feet do not slide. |
| `corre` | pes | Fast run forward with the torso leaning, scissors held back and open, apron streaming behind. |
| `passo_tras` | pes | Quick backstep hop, scissors guard raised, comb hand spinning faster. |
| `pulo` | pes | Jump: crouch, push off, rise with knees up, scissors out to the side, apex, fall, landing crouch. |
| `agachar` / `levantar` | pes | Going down into a squat with the scissors arm resting on the knee / standing back up. |
| `agachado` | pes | Idle in the squat, scissors in front, comb hand spinning on the knee, breathing. |
| `virar` | pes | Turning around to face the other way. |
| `defesa_alta` / `defesa_baixa` | pes | Crossing the closed scissors and the forearm in front of the face / low guard behind the scissors, pained grin. |
| `apanha_alto` / `apanha_baixo` | pes | Head snapping back with wide eyes and the grin breaking / folding at the waist from a low hit. |
| `queda` | cabeca | Knocked down: hit, feet leave the ground, flying back, landing flat on the back, bounce. |
| `levanta` | cabeca | Quick get-up: roll to the knees, scissors planted on the floor, stand up with a grin. |
| `rolamento` | cabeca | Low roll forward, scissors arm tucked in, comb arm leading. |
| `afastar` | pes | Heavy shove: knee chamber and a two-hand push with the closed scissors that launches the opponent. |
| `parry` | pes | Open palm of the comb hand deflects, heel digs in, scissors snap shut as the counter pose. |
| `provoca` | pes | Taunt: snips the scissors twice next to the ear like a barber saying "next!", then spins the comb and grins. |
| `intro` (2 folhas) | pes | Entrance: steps in from the side, snaps the apron straight, spins the comb, "who is next?" pose with the scissors opened wide. |
| `vitoria` (2 folhas) | pes | Victory: combs his hair in the mirror, snips the scissors at the camera and laughs wide-eyed. |
| `derrota` | cabeca | Sits down dazed on the floor, scissors dropped, comb fallen, still smiling. |
| `ko` | cabeca | Flies back, lands flat, scissors twitch open and shut once, then lie still. |

### 4.2 Normais (16)

| id | âncora | Movimento |
|---|---|---|
| `x` | pes | Quick comb jab with the left hand, fast, short reach. |
| `y` | pes | Open scissors slash at chest height, reach medium. |
| `a` | pes | Short front kick with the toe of the shoe. |
| `b` | pes | High front kick, blade-like, fully extended. |
| `baixo_x` | pes | Low comb jab from the squat. |
| `baixo_y` | pes | Rising scissor upper-cut from the squat (anti-air), blades opening upward. |
| `baixo_a` | pes | Fast low shin kick from the squat. |
| `baixo_b` | pes | Wide low broom sweep with the leg, knocks down. |
| `ar_x` | cabeca | Midair comb jab, knees tucked. |
| `ar_y` | cabeca | Midair diagonal downward scissor stab. |
| `ar_a` | cabeca | Short midair knee thrust. |
| `ar_b` | cabeca | Midair crossing kick with the leg stretched, the body above the opponent. |
| `dir_f_y` | pes | Forward elbow with the shoulder, close range. |
| `dir_f_b` | pes | Overhead axe: scissors raised high and brought down in a chop (overhead, must be blocked standing). |
| `dir_t_x` | pes | Open palm push with the back hand while leaning away. |
| `dir_t_a` | pes | Sole kick that pushes away while stepping back. |

### 4.3 Correntes (4 × (3 + finalizador))

| id | âncora | Movimento |
|---|---|---|
| `x1` / `x2` / `x3` | pes | Chain x: comb jab / backhand comb flick / brush swipe pulled from the apron pocket, each faster and tighter. |
| `x_fim` | pes | **Finisher "Degradê"**: step in, scissors close shut with a "snip" at neck height, hits hard, knocks down. |
| `y1` / `y2` / `y3` | pes | Chain y: wide horizontal scissor slash with the blades open / bite closing the blades / diagonal X cut. Slower, heavier. |
| `y_fim` | pes | **Finisher "Tesourão"**: scissors raised open over the head and driven down like a guillotine, sticks in the ground, knocks down. |
| `a1` / `a2` / `a3` | pes | Chain a: shoe-toe kick / stomp on a pedal / high knee. |
| `a_fim` | pes | **Finisher "Cadeira Giratória"**: spinning kick on one foot like a barber chair, apron flaring out. |
| `b1` / `b2` / `b3` | pes | Chain b: high front kick / curved heel kick / half-turn sweep. |
| `b_fim` | cabeca | **Finisher "Fim de Expediente"**: wide spinning back kick that sends the opponent far. |

### 4.4 Especiais, agarrões e supers (base)

| id | âncora | Movimento |
|---|---|---|
| `pente_voador` | pes | Barber pulls a giant comb from the apron and throws it flat along the ground with the left arm. (Projectile art: giant comb, 4-frame spin loop, own sheet.) |
| `borrifada` | pes | Pulls a spray bottle from the apron, aims up and squirts an arc of water. (Projectile: arc of water with droplets, 6 frames.) |
| `tesoura_asc` (2 folhas) | cabeca | Crouch then rise with the scissors blades swept up, opening wide over the head, feet leaving the ground. |
| `tesoura_voadora` (2 folhas) | cabeca | Lunge forward at low height with the scissors snapping open and shut in front, torso horizontal. |
| `proximo` (3 folhas) | pes | **"Next!"**: scissors snip next to the ear, he vanishes in a cloud of white talc, reappears behind with a spin, grinning. Last frames: three quick scissor cuts (strong version). |
| `varrida` | pes | Pulls out a broom and sweeps it very low along the floor, body leaning. |
| `pente_girando` (2 folhas) | pes | Left hand spins the comb as a fast shield in front, deflects a hit, then the scissors snip as a counter. |
| `helicoptero` (2 folhas) | cabeca | The mechanical arm whirls like a propeller with the blades open while the body advances. |
| `agarrao_pe` (3 folhas) | pes | Grab: throws a hot towel around the face, spins the opponent and throws; then fixes his own hair with the comb in a pose. |
| `agarrao_agachado` (2 folhas) | pes | Grabs a crouching opponent by the scruff and slams the head down into the floor. |
| `agarrao_lore` (3 folhas) | pes | Holds the opponent, scissors snip through locks of hair, lets go; a mean grin. |
| `super1` (6 folhas) | pes | **"Next, Customer!"**: poof of talc, appears at the opponent and fires 8 fast scissor cuts in a flurry, ends with a big snip and a bow. |
| `super2` (6 folhas) | pes | **"Explosive Machine"**: throws a giant electric hair clipper onto the opponent. Shaking, heating, sparks rising, it explodes. He pulls out the comb and fixes his hair while the smoke clears. |
| `ativa` (8 folhas) | pes | **Awakening**: pose with the scissors arm raised, muscles swelling, veins popping, eyes widening, shoulder plate sparking, a scream with a crazy grin. |

## 5. Folhas da forma despertada (arte nova, `+10000` nos números de animação)

Redesenhe o corpo todo em pixel art (SNES): mesmo cabelo preto, **mais musculoso e inchado**, veias, olhos arregalados
e esbugalhados, sorriso louco, faísca na ombreira. Pelo menos **20 golpes novos**, conforme `docs/fichas/barbeiro.md`:

- **Folhas de movimento da forma despertada**: `d_ginga`, `d_anda`, `d_corre`, `d_pulo`, `d_agachado`, `d_defesa`, `d_apanha`, `d_queda`.
- **Correntes novas** (y e b): `dy1`..`dy3` + `dy_fim` (Corte Raso), `db1`..`db3` + `db_fim` (Cadeira de 3 Voltas).
- **Normais novos (6)**: `d_x` (Pente Serra), `d_y` (Tesoura Estendida), `d_baixo_y` (Tesoura Cravada), `d_ar_y` (Mergulho Serra), `d_dir_f_b` (Machadada Serrada), `d_baixo_b` (Rasteira de Lâmina).
- **Especiais exclusivos (4)**: `d_disco` (Disco de Máquina; arremessa um disco serrilhado que volta, projétil novo), `d_mergulho`, `d_corte_chao`, `d_espelho`.
- **Kombo novo**: reaproveita as folhas de `dy1`, `d_dir_y`/`dy2` e `d_baixo_y`, sem folha própria.
- **Super exclusivo**: `d_fila_clientes` (6 folhas) + clientes da fila, com os clientes de olho de coração andando torto e se arrastando rente ao chão (`cliente_anda`, 8 quadros, e o moleque da frente com a senha, `cliente_moleque`, 8 quadros). Eles passam pelo oponente e ele fica com o cabelo cortado.
- **Especiais da base que ficam**: versões despertadas de cada um dos 8 com pose ou função nova (veja o fim da ficha).

Despertar gera até 48 cores de paleta, mantendo o contorno de 1 px.

## 6. Efeitos e extras

Use o pixelfx (`assets/efeitos/`, escala 2) conforme a seção 8.1 das regras: `hit-spark` prata nos cortes, `blunt-hit` nos
chutes fortes, `crit-hit` nos finalizadores e supers, `uppercut` no antiaéreo, `shield-block` na defesa, `parry` no parry,
`heavy-landing` na queda do agarrão, `zap-hit` amarelo na Máquina Explosiva, `charge-up` na ativação.
Efeitos novos (nuvem de talco do Próximo!, explosão da máquina, disco serrilhado) saem do pixelfx
(`ferramentas/exportar_efeitos.sh` e as skills do pixelfx) e entram em `assets/efeitos/` com PNG, JSON e uma linha no
`LEIA-ME.md`.

## 7. Pronto quando

- O checklist da seção 9 de `docs/regras-dos-lutadores.md` está **todo marcado** no PR (copie para o corpo).
- Todas as folhas, base e Despertar, são **pixel art desenhada no estilo SNES**, na paleta fechada, sem 3D pixelizado.
- `python ferramentas/gerar_barbeiro.py` e `python ferramentas/verificar_barbeiro.py` passam sem erro e `chars/barbeiro/`
  não tem edição à mão.
- Ele aparece na seleção, luta nos dois lados e no canto, e uma CPU x CPU roda sem erro no log.
- O PR vai para a `mugen` (nunca para a `main`).
