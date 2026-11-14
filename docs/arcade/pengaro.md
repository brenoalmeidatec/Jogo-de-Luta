# Pengaró: arte arcade e kit

> Síntese do estudo arcade de 2026-11-10 (nada testado no motor, nada commitado pela síntese). A fila de geração no
> ChatGPT, com os prompts prontos, fica em [`fila.md`](fila.md); estilo e regras em
> [`../biblia-de-arte.md`](../biblia-de-arte.md#estilo-arcade-anos-90). Folhas de contato e medições brutas ficaram no
> scratchpad da sessão, fora do repo.

## Pedido do Breno para o Alisson (2026-11-12): Pengaró com a pele bem mais escura

Na forma base o Pengaró tem que ser **bem mais escuro**: a pessoa de verdade é negra retinta. Ele tem que ser o lutador
**mais escuro do elenco, mais que o Gutto e mais que o CK**. Hoje ele está ao contrário: com a pele mais clara e mais
amarelada dos três (o próprio estudo abaixo já anotava "pele mais clara e amarelada que a atual").

**Não gere nada de novo no ChatGPT (decisão do Breno): troque a cor nos desenhos que já existem, como edição de imagem.**
A pose, o sombreado e o desenho continuam os mesmos; só muda o tom da pele. Só as folhas que ainda forem geradas daqui
para frente passam pelo ChatGPT, e com uma referência já escurecida por este mesmo processo.

O que fazer:

1. **Paleta da pele** (`sprites/pengaro/paleta_arcade.json` e a tabela abaixo). Proposta que mantém as faixas de matiz da
   regra 3, o contorno sem canal abaixo de 20 (regra 5) e fica abaixo do Gutto em cada tom:

   | Papel | Hoje | Proposta | H / S / V | Gutto, para comparar |
   |---|---|---|---|---|
   | `pele_contorno` | `#4C1414` | `#3A1416` | 357° / 66% / 23% | — |
   | `pele_sombra` | `#8A321C` | `#47201A` | 8° / 63% / 28% | `#6E3226` (V 43%) |
   | `pele_medio` | `#DF7E3F` | `#723F1E` | 24° / 74% / 45% | `#985630` (V 60%) |
   | `pele_luz` | `#FDC372` | `#A2753E` | 33° / 62% / 64% | `#C4894C` (V 77%) |
   | `pele_brilho` | `#FDECCF` | `#D9A066` | 30° / 53% / 85% | `#E8C08A` (V 91%) |

   O CK (`sprites/ck/paleta_arcade.json`) tem o médio em `#D05534` (V 82%), então ele já fica bem mais claro. Os valores
   são ponto de partida: confira no jogo, ao lado do Gutto e do CK, e ajuste à mão se precisar. Depois rode o
   `conferir_arte.py`.
2. **Folhas arcade que já existem** (`sprites/pengaro/quadros/folhas_arcade/`): re-quantizar com a paleta nova. Como a
   quantização é por papel, cada pixel de pele troca para o tom novo do mesmo papel, sem redesenhar.
3. **Arte atual que ainda não é arcade** (`sprites/pengaro/quadros/` e o que o gerador usa hoje): um script de recolor que
   acha os pixels de pele pelo matiz e pela saturação e leva cada um para o tom novo equivalente (sombra para sombra, luz
   para luz). Precisa **poupar a garrafa âmbar**, que tem um tom parecido (ver a nota "Âmbar da garrafa" abaixo):
   - restringir pelo papel no JSON quando houver;
   - ou excluir a região da garrafa, que fica sempre na mão de trás;
   - ou separar pela saturação, porque o âmbar é bem mais saturado que a pele.

   Depois é só rodar o `gerar_pengaro.py` de novo.
4. **Referência para as folhas futuras:** escurecer a folha "Socos" (a referência anexada nos pedidos) pelo mesmo recolor e
   anexar essa. No prompt, trocar "skin" por *"very dark brown skin, the darkest skin of the cast, exactly like the
   attached sheet"*.
5. **O endiabrado continua diferente da base.** Ele é a pele quase preta arroxeada com relevo roxo
   (`paleta_arcade_endiabrado.json`). Com a base mais escura, conferir que a troca ainda se nota: o endiabrado vai mais
   para o roxo e para o preto, e a base fica marrom.
6. Atualizar a frase "pele morena" em `docs/fichas/pengaro.md` (já trocada para "pele negra retinta").

## Paleta fixa (15 cores + transparente)

Arquivo de dados: `sprites/pengaro/paleta_arcade.json` (montado por `quantizar_folha.py --montar-paleta soco` e ajustado
para as faixas da regra). Distribuição: pele 5 (com o contorno da pele), calça 3 (com o contorno da roupa), faixa 3,
cabelo 2, garrafa 2. A pele e a garrafa usam `pele_contorno`; calça e faixa usam `calca_contorno`.

| # | Papel | Hex | H / S / V | Faixa da regra |
|---|---|---|---|---|
| 1 | `pele_contorno` | `#4C1414` | 0° / 74% / 30% | 345–360° |
| 2 | `pele_sombra` | `#8A321C` | 12° / 80% / 54% | 5–15° |
| 3 | `pele_medio` | `#DF7E3F` | 24° / 72% / 87% | 21–26° |
| 4 | `pele_luz` | `#FDC372` | 35° / 55% / 99% | 30–40° |
| 5 | `pele_brilho` | `#FDECCF` | 38° / 18% / 99% | 30–40° |
| 6 | `calca_contorno` | `#351F5C` | 262° / 66% / 36% | 245–265° |
| 7 | `calca_sombra` | `#9492BD` | 243° / 23% / 74% | 230–255° |
| 8 | `calca_branco` | `#FDFAED` | 49° / 6% / 99% | — |
| 9 | `faixa_escuro` | `#14503F` | 163° / 75% / 31% | — |
| 10 | `faixa_verde` | `#149C63` | 155° / 87% / 61% | — |
| 11 | `faixa_amarelo` | `#FDC514` | 46° / 92% / 99% | — |
| 12 | `cabelo_escuro` | `#332C20` | 38° / 37% / 20% | — |
| 13 | `cabelo_luz` | `#756C4E` | 46° / 33% / 46% | — |
| 14 | `garrafa_escuro` | `#5F1A14` | 5° / 79% / 37% | 8–14° |
| 15 | `garrafa_ambar` | `#DF7814` | 30° / 91% / 87% | — |

O que a piloto do soco mostrou na paleta (em aberto):

- **Caneleira sem papel.** A caneleira verde-escura se divide entre `cabelo_luz` e `faixa_escuro`, e o topo do cabelo
  virou uma faixa oliva porque `cabelo_luz` é a mesma cor da caneleira. Precisa de um papel próprio: ou vira a 16ª cor,
  ou sai uma (por exemplo `pele_brilho` fundido com `pele_luz`). Decisão de arte.
- **Pele mais clara e amarelada que a atual.** A folha nova é mais clara; o médio está em 24°, mas o conjunto lê mais
  amarelo. Medir de novo quando as 4 primeiras folhas estiverem prontas e, se for o caso, escurecer `pele_medio` e
  `pele_luz` à mão no JSON.
- **Âmbar da garrafa perto do médio da pele em Lab** (`#DF7814` x `#DF7E3F`): pode roubar pixel de pele. Só pesa na troca
  de paleta do endiabrado, mas convém separar antes.
- `garrafa_escuro` está a 5°, fora da faixa 8–14° que o próprio script pede.

## Prompt base

Troque só o bloco MOTION e anexe em toda folha a folha "Socos" da biblioteca do ChatGPT (forma normal).

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same man, face, hair, skin, white capoeira pants with green
and yellow side stripes, yellow cord belt, teal sash, dark green shin guard on the same leg, barefoot, amber bottle in the
rear hand.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the white pants get cool lilac-blue shadows, never grey or beige. 1-pixel colored outline (dark wine on
skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit side. Small hard 1-3 pixel specular
highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: <bloco da folha>
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

Endiabrado: decidido em 2026-11-11. É o boss final do conceito `sprites/pengaro/quadros/folhas_arcade/e_conceito.png`
(casaco de mestre preto, corda trançada, quatro algemas, braceletes, chifres de fumaça, sem garrafa). O desenho muda
inteiro, então troca de paleta não serve: cada golpe tem folha `e_` própria, com prompt base próprio. A fila está no
Lote 7 de `fila.md`. A aura não saiu das folhas `fx_aura_*`: veio do Blender (`sprites/pengaro/aura/`, ligada por
`ferramentas/aura_pengaro.py`, ver a ficha). A paleta do boss ainda não foi medida.

## Folhas em ordem (MOTION)

As MOTION de golpe vêm do roteiro atual (`FOLHAS_PENGARO` em `ferramentas/gerar_folhas.py`, que casa com os índices que o
gerador já usa) mais a regra de contato arcade (membro 15% maior, recuperação de 3 quadros). `parado`, `soco` e `anda`
seguem o `arte.md`; o `soco` já incorpora o que a piloto pediu (punho 20% maior no contato, quadro 7 de transição,
mesma mão no 1 e no 8).

| Lote | Folha | Usada em | MOTION |
|---|---|---|---|
| 1 | `parado` | 0 parado (q_parado), base de várias poses do gerador | standing tall, capoeira ginga bounce, feet planted: frames 1 to 4 sink, frames 5 to 8 rise; frame 8 loops into frame 1. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 1 | `anda` | 20 andar, 100 correr (q_anda / anda_fluida) | guarded walk forward in the capoeira ginga, hands up in front of the chest, a full two-step cycle: frame 1 contact, front leg forward and rear leg back, 2 weight on the front leg, 3 rear leg passes under the body, 4 that leg reaches forward, 5 contact with legs swapped, 6 weight on the new front leg, 7 the other leg passes, 8 it reaches forward and flows back into frame 1; the body rises slightly on the passing frames, the pants fold at each step. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 1 | `soco` | 200 soco fraco (16 elementos, 19 ticks), correntes e kombos | standing tall, quick jab with the front fist: frame 1 stance with the same hands as the idle sheet, frame 2 the shoulder loads back, frame 3 small step in, frame 4 fist travels out, frame 5 contact: the fist is drawn 20% larger than in frame 1, shoulder thrust forward, torso turned showing the chest, frame 6 hold with the arm fully extended, frame 7 the arm halfway back with the elbow bent and the fist still closed, frame 8 back to the stance with exactly the same hand shape as frame 1. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 1 | `baixo_soco` | 400 soco agachado | a low jab from the cocorinha squat. Frame 1 deep squat with one hand on the ground, frames 2 and 3 the shoulder loads, frames 4 and 5 the free arm punches straight forward at waist height, frames 6 to 8 back to the squat. Frames 1 and 8 equal the squat pose of the crouch sheet. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. |
| 2 | `ginga` | 0 parado e 5 virar via ginga_fluida (loop do Blender) | the real capoeira ginga, an 8-frame loop, NOT a boxing guard. The body swings side to side in a low triangle step. Frame 1 both feet parallel and wide, knees bent, torso leaning slightly forward. Frames 2 and 3 the right leg steps far back on the ball of the foot, the torso leans forward and the left arm crosses in front of the face protecting it while the other arm swings low and back. Frame 4 he starts to return. Frame 5 feet parallel and wide again. Frames 6 and 7 the left leg steps far back and the arms swap, with the right arm now crossing in front of the face. Frame 8 returning to frame 1. Relaxed, swaying, rhythmic, arms always moving, always low on the legs. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 2 | `agachado` | 10–12 agachar, defesa baixa, base dos golpes agachados | going down to the capoeira cocorinha squat. Frames 1 to 4 he sinks from ginga stance into a deep squat with one hand touching the ground and the other arm protecting the face. Frames 5 to 8 he stays in the deep squat, breathing with small movements. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 2 | `chute_baixo` | 230/231/245, correntes | a fast low front kick (chapa). Frame 1 ginga stance, frames 2 and 3 the knee lifts, frames 4 and 5 the leg snaps straight at knee height with the sole forward, frames 6 and 7 the leg folds back, frame 8 ginga stance. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. |
| 2 | `chute_alto` | 240/246, correntes e kombos | meia-lua de frente, a high crescent kick. Frame 1 ginga stance, frame 2 weight on the support leg, frame 3 the straight leg rises from the outside, frames 4 and 5 the leg sweeps across at head height, fully extended, frames 6 and 7 the leg comes down, frame 8 ginga stance. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. |
| 2 | `defesa` | 120–152 guarda, 760 aparar | blocking. Frame 1 ginga stance, frames 2 and 3 forearms cross in front of the face, frames 4 and 5 he holds the block with a pained grimace, frames 6 and 7 the impact pushes him back a little, frame 8 still blocking. The forearms stay compact; the impact frames push the feet back a little. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 2 | `apanha` | 5000–5035 apanhar | getting hit in the face. Frame 1 ginga stance, frames 2 and 3 the head snaps back, mouth open, frames 4 and 5 the torso bends backward with arms flung, frames 6 to 8 he recovers to the ginga stance. The recovery is longer than the hit. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 2 | `pulo` | 40–47 pulo | a jump. Frame 1 knees bent ready to jump, frame 2 pushing off the ground, frame 3 rising with legs starting to tuck, frame 4 tucked at the top like preparing a bicycle kick, frame 5 still tucked and turning, frame 6 falling with legs opening, frame 7 reaching for the ground, frame 8 landing with knees bent. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 2 | `ar_soco` | 600/601 soco no ar | a downward punch in mid air. All frames are in the air with legs tucked. Frames 1 to 3 the arm winds up, frames 4 and 5 the arm strikes down and forward, frames 6 to 8 he recovers the tucked pose. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. |
| 2 | `queda` | 5040–5170 cair | being knocked down. Frame 1 hit and bending back, frame 2 feet leaving the ground, frames 3 and 4 flying backward horizontally in the air, frames 5 and 6 falling onto his back, frame 7 bouncing on the floor, frame 8 lying flat on his back. Same body size in every frame. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 2 | `levanta` | 5120 levantar | getting up with a capoeira kip-up. Frame 1 flat on his back, frames 2 and 3 knees pull to the chest, hands by the head, frames 4 and 5 he kicks up off his hands, frames 6 and 7 landing crouched, frame 8 ginga stance. Frame 1 has the same body size as the last frame of the knockdown. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 2 | `martelo` | 210/215/216, 1400/1401 | a strong elbow strike (cotovelada). Frame 1 ginga stance, frame 2 torso twists back, frame 3 the elbow rises to shoulder height, frames 4 and 5 the torso whips forward with the elbow leading at chin height, frames 6 and 7 he recovers, frame 8 ginga stance. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. |
| 2 | `afastar` | 260 afastar | a heavy pushing kick that launches the opponent (bencao). Frame 1 ginga stance, frames 2 and 3 the knee chambers high against the chest, frames 4 and 5 the leg thrusts straight forward at chest height with the torso leaning back, frames 6 and 7 the foot lands forward, frame 8 ginga stance. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. |
| 2 | `cabecada` | 410 agachado y (antiaéreo normal) | a rising anti-air head butt from the squat. Frame 1 deep squat, frames 2 and 3 the legs push up, frames 4 and 5 the whole body drives upward with the head first, fully stretched, frames 6 to 8 he falls back into the squat. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. |
| 2 | `rasteirinha` | 430 agachado a | a quick low foot sweep from the squat. Frame 1 deep squat with a hand on the ground, frames 2 and 3 the leg slides out, frames 4 and 5 the leg is fully stretched just above the floor, frames 6 to 8 the leg pulls back. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. |
| 2 | `rasteira` | 440 agachado b (derruba) | a full capoeira rasteira sweep. Frame 1 deep squat with both hands on the ground, frames 2 and 3 the body pivots low, frames 4 and 5 the straight leg sweeps wide along the floor, frames 6 to 8 he gathers back into the squat. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. |
| 2 | `bicicleta` | 610/611 chute no ar, 650 | a mid-air bicycle kick like in football. All frames are in the air. Frame 1 tucked, frames 2 and 3 the body tilts backward, frames 4 and 5 lying back in the air, one leg kicks up and forward fully stretched, frames 6 to 8 he rotates back to tucked. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. |
| 3 | `armada` | 1200/1201 Armada do Quilombo (antiaéreo) | armada, a rising spinning kick. Frame 1 low stance, frames 2 and 3 he turns his back and starts to rise, frames 4 and 5 he spins in the air with the straight leg sweeping high, frames 6 and 7 falling, frame 8 landing. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. |
| 3 | `compasso` | 1100/1101 meia-lua de compasso | meia-lua de compasso, a spinning kick with a hand on the floor. Frame 1 ginga stance, frames 2 and 3 he bends forward and plants both hands on the ground, frames 4 and 5 the straight leg swings in a big high circle over the head, frames 6 and 7 the leg comes around, frame 8 ginga stance. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. |
| 3 | `agarrao` | 800/810 agarrão, agarrão de comando | a judo-like throw. Frame 1 ginga stance, frame 2 both hands reach forward and grab, frames 3 and 4 pulling the grabbed air toward him, frames 5 and 6 turning his back with the hip low, frames 7 and 8 throwing downward with both arms. No second person is shown. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 3 | `bola` | 1000/1001 Latada de Sombra | Latada de Sombra, throwing a beer can. Frame 1 ginga stance with the whisky bottle in the back hand and a generic silver beer can (no brand, no text) in the front hand, frames 2 and 3 he winds the front arm back over the shoulder, frames 4 and 5 he whips the arm forward and releases the can at head height, the can leaves the hand, frames 6 and 7 follow-through with the torso leaning forward, frame 8 ginga stance. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. |
| 3 | `caneta` | 1300/1301 carrinho | a low sliding tackle like football. Frame 1 ginga stance, frames 2 and 3 he drops to the floor, frames 4 and 5 sliding on one hip with the leading leg stretched forward, frames 6 and 7 getting up, frame 8 ginga stance. On the contact frames the striking hand or foot is drawn 15% larger than in frame 1, with the shoulder or hip thrust forward and the torso turned; the recovery takes at least 3 frames and the limb comes back gradually, never snapping back to the stance in one frame. The sash tips and the pant legs lag 1-2 frames. |
| 3 | `rolamento` | 700/705 rolamento | a capoeira role, a low rolling dodge. Frame 1 ginga stance, frames 2 to 7 he drops one hand to the floor and spins his low body in a full turn, close to the ground like a cartwheel kept low, frame 8 back up in a crouch. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 3 | `golaco` | 3000 Chuva de Bebidas | Chuva de Bebidas, a super move. Frames 1 and 2 he takes a long swig from the whisky bottle, frame 3 he wipes his mouth, frames 4 and 5 he raises both arms to the sky shouting, frames 6 to 8 bottles and beer cans (no brands) rain down from above in front of him while he laughs with arms open. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 3 | `lata` | 190–192 entrada | drinking a can. A generic silver can with no brand and no text in his hand. Frame 1 ginga stance holding the can, frame 2 opens it, frames 3 to 5 tilts his head back and drinks it all, frame 6 crushes the can, frame 7 burps with his head back, frame 8 wide crazy smile, ready to fight. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 3 | `provoca` | 195 provocação | a drunk taunt. Frames 1 to 4 he sways, takes a swig from the whisky bottle and tries to say a word, frame 5 he burps, frames 6 to 8 he waves the opponent in with the bottle, staggering a little. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 3 | `vitoria` | 181 vitória | a drunk victory celebration. Frame 1 ginga stance, frames 2 and 3 he raises the whisky bottle high, frames 4 to 6 he drinks from it with the head thrown back, frames 7 and 8 he toasts toward the screen, laughing. The sash tips and the pant legs lag 1-2 frames behind the body. |
| 3 | `derrota` | 170 derrota | complaining after losing. Frames 1 and 2 falling to sit on the floor, frames 3 to 8 sitting on the floor with legs out and arms wide open, complaining to the referee, mouth open. The sash tips and the pant legs lag 1-2 frames behind the body. |

Já existem em `sprites/pengaro/quadros/folhas_arcade/` (gravadas em 10/11, só o `soco` passou pelo pipeline):
`agachado`, `anda`, `baixo_soco`, `chute_alto`, `chute_baixo`, `parado`, `soco`. Confira cada uma contra o critério antes de gerar de novo.

Efeito: `fx_arco` (fundo verde `#00FF00`, rastro em meia-lua de 2–3 cores claras, nos fortes no quadro de contato). O
prompt está na fila.

## Piloto do soco: o que o pipeline mediu

50 quadros (8 desenhos + 42 do meio) em `sprites/pengaro/quadros_arcade/soco/`:

| Regra | Resultado |
|---|---|
| 1 paleta | PASS: no máximo 15 cores, todas da paleta (os 42 do meio falhavam 42/42 antes do `--meio`) |
| 3, 4, 5 | PASS nos 50: rampa da pele, sombra fria da calça, contorno sem canal < 20 e de 1 px |
| 7 chiado | PASS: no máximo 0,13% de pixel isolado |
| 10 contato | **FAIL**: punho 15 px no quadro 1 e 11 px no contato (-27%); a medida é grosseira porque o antebraço em guarda entra na altura |
| 11 antecipação/volta | PASS só como golpe fraco: o quadro 2 muda 30% da silhueta, mas a volta tem 2 desenhos (o forte pede 3) |

No vídeo lado a lado (60 fps, mesmos tempos da ação 200: 19 ticks, 16 elementos):

- **Estalo t7→t8:** o braço sai de esticado para a guarda em 1 tick, porque o desenho 07 da folha (índice 06) já é guarda
  e o meio passa por ele no t=0,5. O soco atual estala igual: a origem é a folha e o tempo, não a quantização. O
  `video_golpe.py` não acusa porque o limite de salto é 0,45.
- O ativo esticado aparece só em t6–t7.
- O golpe começa de punho fechado (desenho 01) e termina de mão aberta; a emenda com o parado não foi conferida.
- Ninguém viu o vídeo ainda e o golpe não foi testado na sandbox.

## Kit (plano de `essencia/jogo.md`)

Ticks a 60/s; comandos na sintaxe do `.cmd`. Cada item fecha com `verificar_pengaro.py`, `conferir_tempo.py`,
`testar_pengaro.py` e vídeo na sandbox, e segue o checklist da seção 9 de `regras-dos-lutadores.md`.

> **Atenção, conflito com as regras do projeto.** A seção 2 de `regras-dos-lutadores.md` proíbe diagonal, `$`,
> meia-lua, 360° e carga no comando de especial (especial = 2 toques cardeais + botão; super = 3 toques, `~B,F,D`
> + chute ou soco, seção 3.H), e a 3.G manda todo agarrão ter escape com y ou b. Os itens abaixo que pedem
> diagonal, meia-lua, meia-lua dupla ou agarrão sem escape seguem a convenção do gênero e **só entram se o Breno
> mudar a regra**. O resto (invencibilidade do antiaéreo, só o forte de perto cancela, tremor, contra-ataque,
> folhas novas) não depende disso.

| # | Mudança | Comando | Frame data alvo | Folha nova? |
|---|---|---|---|---|
| 1 | Antiaéreo de verdade (item 14): Armada do Quilombo com invencibilidade que cobre o ativo. Hoje o NotHitBy acaba no tick 5 e o ativo começa no 5 | `~D,DF,F` mantém; novo `~F,D,DF` + x/y | x: startup 4, invencível 1–5 só contra ar. y: startup 3, invencível 1 até o fim do ativo (6), recuperação ~28, 120 de dano, lança | não (`armada`) |
| 2 | Forte de perto cancela (item 7): y e b de perto entram na lista "Pode cancelar" para especial e super; os de longe não | — | cancel na janela de contato (movecontact) | não |
| 3 | Comandos com diagonal (item 11): meia-lua e Z aceitam a diagonal, cardeais ficam como folga | `~D,DF,F` e `~F,D,DF` (além de `~D,F` / `~F,D`) | buffer atual | não |
| 4 | Agarrão de comando (item 17): sai do `B,F y` com escape de 7 ticks | `~B,DB,D,DF,F, y` | startup 1, alcance curto, sem escape, 150 de dano, 30 ticks abertos se errar | não (`agarrao` + `martelo`) |
| 5 | Comando dos supers (item 19), os dois invencíveis no flash | Chuva de Bebidas `~D,DF,F,D,DF,F, a` (ou b); Bando da Várzea `~B,DB,D,DF,F,B,DB,D,DF,F, x` (ou y) | invencível do tick 1 ao fim do superpause | não |
| 6 | Saideira Sombria com comando próprio (vida baixa) | `~D,DF,F,D,DF,F, x+y` | mantém | não |
| 7 | Impacto mais pesado: tremor de tela nos fortes e som seco (item 19 do LOGBOOK) | — | EnvShake 6–8 ticks nos fortes; pausetime fica 8/6, 12/9, 16/10 | não (som próprio, gravado ou sintetizado, nada de jogo) |
| 8 | Contra-ataque (item 24, item 18 do LOGBOOK) | acerto durante o startup do outro | +4 ticks de hitstop, texto "CONTRA!", forte de longe derruba | não (texto no HUD) |
| 9 | Modo de poder "Roda Aberta" (item 22) | `x+y` com 1 estoque | ativa no meio do combo (cancel de normal que encostou, sem empurrão), dura 7 s, libera especial → especial e especial → super | talvez (`despertar_a` serve de flash) |
| 10 | Super máximo "Rodada Cheia" (item 20): Chuva de Bebidas com a+b | `~D,DF,F,D,DF,F, a+b` | 2 estoques (1 na Roda Aberta), 1,5x dano, termina lançando | sim: quadro final de lançar |
| 11 | Especial no ar "Bênção do Alto" (item 18); hoje todo especial exige statetype != A | no ar `~D,DF,F, a` (ou b) | startup 8, chute em diagonal para baixo, bate por cima, quica para trás no acerto | sim: `ar_bencao` |
| 12 | Conferências pequenas | — | passo para trás invencível nos ~4 primeiros ticks; hiper pulinho ~30 ticks no ar; rolamento 20–24 ticks, agarrável nos últimos ~6; investida fraca -2 e forte -10 na defesa; juggle curto, ~3 pontos por queda | não |

Decisões do Breno (não implementar sem resposta):
- **Correntes (item 8):** hoje vão até 4 fracos com cancel. O sabor arcade 90 é no máximo 2 golpes + cancel e Kombos curtos.
- **Carga (item 12):** recomendo não ter; é arquétipo de outro tipo de lutador. Se quiser: "Arrastão de Feira",
  `[carga B] F + a/b`, carrinho rasteiro, startup 10/14, derruba, -12 na defesa, folha nova `arrastao`.
- **Roda Aberta x Despertar:** convivem (dois recursos) ou a Roda Aberta vira a ativação do Despertar.

Regras que seguem valendo: `docs/regras-dos-lutadores.md` (checklist da seção 9) para todo item; caixas de golpe não
mudam com a troca de arte; folha nova só depois que a paleta fixa do `arte.md` estiver no pipeline, senão nasce no estilo
antigo e é refeita duas vezes.
