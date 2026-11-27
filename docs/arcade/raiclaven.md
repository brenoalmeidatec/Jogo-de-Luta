# Raiclaven: arte arcade e kit

> Síntese do estudo arcade de 2026-11-10 (nada testado no motor, nada commitado pela síntese). A fila de geração no
> ChatGPT, com os prompts prontos, fica em [`fila.md`](fila.md); estilo e regras em
> [`../biblia-de-arte.md`](../biblia-de-arte.md#estilo-arcade-anos-90). Folhas de contato e medições brutas ficaram no
> scratchpad da sessão, fora do repo.


## (a) Paleta fixa: 15 cores + transparente

Distribuição (análogo da regra 2 para o barbeiro, soma 15): contorno 1, preto da roupa/cabelo/sapato/pente 3, pele 5,
aço do braço mecânico 2, prata das lâminas 2, distintivo de barbearia 2.

| # | Papel | Hex | Matiz / sat / valor | Onde |
|---|---|---|---|---|
| 0 | transparente | `#FF00FF` na folha | — | fundo (vira alfa 0 no corte) |
| 1 | contorno compartilhado | `#24182C` | 276° / 45% / 17% | borda externa de tudo; nenhum canal < 20 nos três ao mesmo tempo (36,24,44) |
| 2 | preto: sombra | `#34284A` | 261° / 46% / 29% | dobras da calça larga, lado da sombra do avental, cabelo, sapato |
| 3 | preto: base | `#4A3D66` | 259° / 40% / 40% | camisa, avental, calça, pente, cabelo crespo (massa) |
| 4 | preto: luz fria | `#776A9C` | 256° / 32% / 61% | faixa de brilho no cabelo, vinco da calça, bico do sapato, borda do avental no lado da luz |
| 5 | pele: sombra vinho | `#5E1F1C` | 3° / 70% / 37% | sombra profunda, boca, contorno interno da pele (sel-out na sombra) |
| 6 | pele: escura | `#8A3424` | 9° / 74% / 54% | plano de sombra dos músculos |
| 7 | pele: média | `#B65A38` | 16° / 69% / 71% | tom-base (matiz real do personagem) |
| 8 | pele: luz | `#DC9466` | 23° / 54% / 86% | plano de luz: ombro esquerdo, antebraço, testa |
| 9 | brilho creme | `#F6DCB4` | 36° / 27% / 96% | brilho duro 1–3 px (testa, nó dos dedos, peito); também cabo do pincel e o pente no bolso |
| 10 | aço: escuro | `#565A76` | 232° / 27% / 46% | ombreira, braço mecânico, rebites na sombra, pino da tesoura |
| 11 | aço: médio | `#9097B4` | 228° / 20% / 71% | plano de luz do aço, friso prateado da camisa e do avental, sombra da toalha/talco |
| 12 | prata: lâmina | `#C9CFE0` | 224° / 10% / 88% | corpo das lâminas, branco dos olhos arregalados, dentes, toalha e talco |
| 13 | prata: brilho | `#F4F6FC` | 225° / 3% / 99% | fio da lâmina e brilho duro de 1–3 px; faixa branca do tubo de barbearia |
| 14 | distintivo: vermelho | `#C42A2E` | 358° / 79% / 77% | faixa vermelha do tubo de barbearia; serve também de língua no sorriso |
| 15 | distintivo: azul | `#2F5CC4` | 222° / 76% / 77% | faixa azul do tubo de barbearia |

Regras do `arte.md` aplicadas ao Raiclaven (mesmos números, faixas deslocadas para a pele dele):

1. **Paleta fixa:** <= 15 cores por quadro, todas da tabela, depois de quantizar e depois do Blender.
2. **Soma 15:** a tabela acima; a pele tem 5 tons como no Pengaró, o preto faz o papel da calça (3).
3. **Rampa com matiz deslocado (pele):** sombra 0–10° (vinho; os tons 5 e 6 estão em 2,7° e 9,4°), média 13–18°, luz
   21–26°, brilho 32–40° (creme). Mesma lógica do Pengaró (a faixa "luz 30–40°" do `arte.md` corresponde aqui ao brilho
   creme), centrada no matiz real 12–16° dele.
   Critério de desvio na folha crua: pele mediana acima de **18°** ou abaixo de **8°** = refazer com a referência.
4. **Preto com sombra e luz frias:** os três pretos e o aço entre **225–275°**, saturação >= 20%; nunca cinza neutro nem
   o roxo-magenta da folha crua (matiz 300–340° proibido no corpo, porque é a cor do fundo).
5. **Contorno colorido de 1 px:** `#24182C` em tudo; na pele, o contorno do lado da sombra pode ser o tom 5 (vinho),
   como sel-out. Nenhum pixel com R, G e B < 20. Lado da luz (frente-cima): contorno some ou vira o tom 3/6.

Identidade preservada: pele marrom, cabelo crespo curto preto com degradê, cavanhaque, sorriso largo e olhos
arregalados, camisa e avental pretos com friso prateado, tubo de barbearia vermelho-branco-azul no peito, braço direito
de aço com ombreira rebitada e tesoura gigante, braço esquerdo humano enorme com o pente, calça larga, sapato brilhoso.
Recolor do Despertar (Surto de Tesoura) por troca de paleta onde der: pele mais fechada (5–8 escurecidos). Olhos e
faísca **não** saem por troca de paleta: o 12 também é lâmina, dentes, toalha e talco, e o 13 é fio da lâmina e faixa
branca do tubo; trocar o índice pinta tudo isso junto. Olho amarelo e faísca vão desenhados nas folhas `e_` (ou como
sobreposição de efeito); o resto é arte redesenhada, como manda a ficha.

---

## (b) Prompt base e blocos MOTION

### Prompt base (troque só o bloco MOTION; anexe `referencia_ginga.png` em toda folha)

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: RAICLAVEN, the psycho barber. Same man: muscular, brown
skin, short black curly hair with a fade, goatee, huge grin and wide staring eyes. Same black short-sleeve barber shirt
with silver trim and buttons and a small red-white-blue striped barber pole badge on the chest, same black apron with a
comb and a shaving brush in the pocket, baggy black pants, shiny black shoes. Same dark steel mechanical RIGHT arm with
a riveted pauldron, ending in GIANT silver scissors (no hand on that arm, ever). Same huge human LEFT arm, the hand
always holding a black comb. Same size and scale as the attached sheet. He fights with the martial art of the barber.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the black clothes are dark blue-violet with cool lilac highlights, never grey, never purple-magenta;
the steel arm is cool blue-grey, the blades bright silver. 1-pixel colored outline (very dark violet), never pure black,
lighter or missing on the lit side. Small hard 1-3 pixel specular highlights on forehead, knuckles, steel pauldron and
the blade edges, one highlight band on the hair. Limited palette look.
Layout: one single row of 8 frames in 8 equal-width cells, evenly spaced, wide image, side view, always facing right,
same size and scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure
stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, no
shadow, no ground, no text, no numbers, no borders, no effects, no smoke, no motion lines.
MOTION: <bloco da folha>
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

Notas: (1) "no effects, no smoke" vale também para `rolamento` e `pente_combo`: o talco sai do corpo e vira `fx_talco`
(fundo verde), senão o corte por célula e o quantizador comem a nuvem junto com o corpo. (2) Mão direita **não existe**:
o braço de aço termina na tesoura em todo quadro (ver problemas em `agarrao` e `vitoria`). (3) Contato: quem bate fica
**10–20% maior** que no quadro 1 (lâmina, pente, sapato).

### Folhas em ordem (MOTION como vai no prompt)

| Lote | Folha | Usada em | MOTION |
|---|---|---|---|
| 1 | `ginga` | 0 parado (via `ginga_fluida`), 5 virar, pose-base do gerador | standing guard, barber idle bounce, feet planted wide; 1–4 sink a little, 5–8 rise; the scissors open slowly on 1–4 and close on 5–8; the comb spins one full turn in the left hand across the 8 frames; apron hem and baggy pant legs settle one frame after the body; 8 loops into 1. |
| 1 | `anda` | 20 andar, 100 correr (via `anda_fluida`) | confident barber strut forward, full two-step cycle: 1 contact right foot, 2 down, 3 passing, 4 up, 5 contact left foot, 6 down, 7 passing, 8 up; shoulders sway opposite to the hips, the scissors snip once per step, comb spinning; the baggy pants fold behind each knee and the apron swings one frame late; 8 flows into 1. |
| 1 | `soco` | 200 x em pé, 301 (corrente x 2º), 340, 3433; parado0 | comb jab (x is the comb, not the scissors): 1 stance, 2 the left shoulder loads back and the comb hand cocks by the cheek, 3 small step in, 4 jab extending, 5 contact: comb fist drawn 15% larger, left shoulder thrust forward, torso turned showing the chest, 6 hold, 7 pulling back, 8 stance; the scissors stay low and closed; apron flicks forward on 5. |
| 1 | `defesa` | 120/130/140/150 defesa, 760 aparar | guard: 1 stance, 2 the flat side of the giant scissors comes up in front of the face, comb arm tucked behind it, 3–4 compact block, knees bent, head down behind the blade, 5 impact: pushed back a little, shoes slide, 6 hold, 7 recoil settles, 8 still blocking; apron and pants pushed back by the impact on 5–6. |
| 2 | `apanha` | 5000–5015 apanhar (leve/médio/pesado), tonto | hit reaction: 1 stance, 2 head snapped back, mouth open, eyes wide, 3 torso twisted, scissors and comb flung out wide, 4 deeper bend back, 5 max bend, hair and apron lagging forward, 6 coming back, 7 grin returning, 8 stance. |
| 2 | `agachado` | 10/11/12 agachar, 6, defesa baixa | 1 stance, 2–3 sinking with knees opening wide, 4 deep crouch, scissors low and forward, comb up by the face, 5–8 crouched loop, the scissors snip once, the comb turns; pants bunch at the knees. |
| 2 | `pulo` | 40–47 pulo | 1 knees bent (anticipation), 2 push-off, legs straight, 3 rising, knees tucking, 4 tucked at apex, scissors open, 5 still tucked, 6 falling, legs opening, 7 reaching for the ground, 8 landing with knees bent; apron flies up on 2–3 and drops late on 6–7. |
| 2 | `chute_alto` | 240 b longe, 246 (→b), 323, 331, 341, 346, 3401, 3420, 3432 | high razor kick: 1 stance, 2–3 big wind-up, back knee chambers to the chest, torso coils away, scissors pulled back for balance, 4 snap, 5 contact: leg and shoe stretched 15% at head height, hips forward, pant leg flared open, 6 hold, 7–8 long recovery with the knee coming back down. |
| 2 | `martelo` | 210/215 y em pé, 216 (→y), 302, 311, 343, 344, 1400/1401, 3200, 3405–3431 | overhead scissors chop: 1 stance, 2 the steel arm rises, 3 scissors high over the head, wide open, torso arched back (clear anticipation), 4 chop coming down, 5 contact: scissors closing at chest height, blade 15% larger, steel shoulder thrust forward, front knee bent, 6 hold, 7–8 slow pull back to stance; apron swings forward on 5. |
| 2 | `chute_baixo` | 230 a em pé, 231 (←a), 245 b perto, 312, 321, 3411, 3434, 1500/1501 | pointy shoe to the shin: 1 stance, 2 front knee lifts, 3 chamber low, 4 snap, 5 contact: shoe tip stretched 15% at shin height, pant leg flaring, 6 hold, 7 back, 8 stance. |
| 2 | `baixo_soco` | 400 ↓x | low comb jab: 1 crouch (= agachado 5), 2 comb hand cocks back, 3 pushing forward, 4 jab, 5 contact: comb fist 15% larger at knee height, shoulder forward, 6 hold, 7 back, 8 crouch (= agachado 5). |
| 2 | `cabecada` | 410 ↓y (antiaéreo normal), 303, 347, 3412, 3430 | rising scissors anti-air: 1 crouch, 2 deeper coil, steel shoulder dropped, 3 pushing up, 4 standing tall, scissors thrust straight up open, 5 contact: arm and scissors 15% longer above the head, heels off the ground, 6 hold, 7–8 coming back down to the crouch; apron and pants lifted on 4–5. |
| 2 | `rasteirinha` | 430 ↓a, 322, 342 | quick low shoe poke: 1 crouch, 2 leg slides out, 3 extending, 4 contact: shoe stretched 15% just above the floor, 5 hold, 6–7 pulling back, 8 crouch. |
| 2 | `rasteira` | 440 ↓b (derruba), 841, 3435 | broom sweep: 1 crouch, 2 left hand pulls a barber broom from behind the back, 3 broom cocked behind, torso coiled, 4 sweep starting, 5 contact: broom head 15% larger sliding along the floor at full reach, 6 follow-through, 7–8 long recovery tucking the broom away; pants twist with the hips. |
| 2 | `queda` | 5050–5170 cair | 1 hit, bending back, 2 feet leaving the ground, 3 flying back horizontal, 4 falling, 5 hitting the floor on the back, 6 bounce, 7 settling, 8 flat on the back; the scissors and comb stay in place on the body (same size in every frame). |
| 2 | `levanta` | 5120 levantar | 1 flat on the back (same size as queda 8), 2 sits up, 3 plants the closed scissors on the floor, 4–5 pushes up on the scissors, 6 standing, 7 combs his hair once, 8 stance (= ginga 1). |
| 2 | `ar_soco` | 600 x no ar, 601 y no ar | diving scissors slash, all frames in the air with knees tucked: 1 tucked, 2–3 scissors rise behind the head, 4 slash starting down-forward, 5 contact: open blades 15% larger in a diagonal, 6 hold, 7–8 back to tucked. |
| 2 | `bicicleta` | 610 a no ar, 611 b no ar, 650, 3403 | crossing flying kick, all frames in the air: 1 tucked, 2–3 body turns sideways, 4 both legs scissor forward, 5 contact: front shoe 15% larger at head height, pants flared, 6 hold, 7–8 tucked again. |
| 2 | `afastar` | 260 (y+b), 332, 345, 3421 | push kick that sends far (different from chute_alto: chest height, sole flat): 1 stance, 2 lean back, 3 knee to the chest, 4 thrust, 5 contact: flat sole 15% larger at chest height, hips forward, 6 hold, 7 foot lands forward, 8 stance. |
| 3 | `armada` | 1200/1201 especial →↓, 313, 3422, 3423 | spinning barber-chair kick: 1 stance, 2 pivot on the front foot, 3 back turned, scissors tucked, 4 spinning, 5 contact: leg stretched 15% high, pant leg flared, 6 completing the turn, 7–8 recovery. Same scale as ginga. |
| 3 | `compasso` | 1100/1101 especial ↓← a/b, 333, 348, 3413 | Scissor Helicopter: 1 stance, 2 steel shoulder winds back, 3 the arm starts circling at the shoulder in front of the body, 4–5 the arm is a horizontal blur-free blade at chest height, scissors open, shown at different angles each frame, torso leaning in, 6 still spinning, 7 slowing, 8 recovery: arm still out to the side, torso still leaning, not yet back to stance; apron whips around. |
| 3 | `caneta` | 1300/1301 especial ↓← x/y, 349 | scissors dash: 1 stance, 2 crouch and aim the scissors forward, 3 push off, 4 lunging low and fast, scissors open like a spear, 5 contact: blades snap shut 15% larger, 6 slide, 7 still low, 8 still low and overextended, scissors closed, about to rise. Same scale and cell size as ginga. |
| 3 | `bola` | 1000/1001 Pente Voador, 1600/1601 (provisório) | comb throw: 1 stance, 2 left arm cocks back with a big comb, 3 deep wind-up, torso turned away, 4 throw, 5 release: arm 15% longer, comb leaving the hand at chest height, 6 follow-through, 7–8 recovery. |
| 3 | `rolamento` | 1700/1701 Próximo!, 700/705 rolamento, 3402 | disappearing step, body only (no talc): 1 stance, 2 comb cocks back, 3 flick of the comb forward, 4 body ducks low, 5 low crouch pose turned away, 6 low lunge forward, scissors forward, 7 catches the comb, 8 stance. |
| 3 | `pente_combo` | 1701 Próximo! forte (3 acertos) | sequence after reappearing, no cloud on the body: 1 low lunge (same as rolamento 6), 2 contact: comb jab to the face, comb hand 15% larger, 3 pulling the comb back while the scissors rise (no hit), 4 contact: scissors slash low, 5 turning the steel shoulder back to load (no hit, no spin line), 6 steel arm thrusts the open scissors forward, 7 contact: scissors snap shut 15% larger, shoulder forward, 8 combs his hair, grinning. |
| 3 | `agarrao` | 800 agarrão, 830 Toalha Quente, 840 | hot towel grab, the steel arm keeps the scissors in every frame: 1 stance, 2 left hand reaches with a white towel, 3 towel wraps an invisible head, scissors hooked behind it, 4 pull in, 5–6 pivot (side view, apron visible, never seen from the back), 7 throw: left arm 15% longer, towel flung forward, 8 fixes his hair with the comb. No second person. |
| 3 | `golaco` | 3000 super, 3100 | flurry of haircuts: 1 stance, 2 crouch and grin (anticipation), 3 scissors snip high, 4 comb jab, 5 scissors snip low, 6 scissors snip high, 7 contact: huge closing of the scissors 15% larger, 8 pose. |
| 3 | `provoca` | 195 provocação | 1–3 snips the scissors by his own ear, 4–6 points the comb at the opponent and waves him to the chair, 7–8 laughs with the head thrown back. |
| 3 | `lata` | intro, embaixada | warm-up: 1 stance, 2–3 rubs the blades against each other, 4–5 checks the edge with the left thumb, 6–7 spins the comb, 8 stance. |
| 3 | `vitoria` | 181 vitória | 1 stance, 2–3 blows hair off the blades, 4–6 combs his own hair with the comb in the LEFT hand, 7–8 rests the open scissors (still on the steel arm) over his shoulder, crazy grin. |
| 3 | `derrota` | 170 derrota | 1 stance hurt, 2 drops to sit, 3–8 sitting, legs out, scissors bent and drooping, comb broken, sulking (same scale throughout). |
| 3 | `despertar_a` | 2000 Surto de Tesoura (ativação, 1ª metade) | 1 stance, 2 shoulders hunch, 3 head drops, 4 sparks implied by the pauldron pose, 5 muscles swell, 6 head snaps up, eyes bulging, 7–8 grin widens. |
| 3 | `despertar_b` | 2000 (2ª metade, pose de poder) | 1 roars with the head back, 2–3 scissors open wide to the side, 4–5 the comb spins fast, 6–7 crouches forward, 8 ready stance, bigger and wilder. |

## (c) Kit na essência de luta arcade 90

> **Atenção, conflito com as regras do projeto.** A seção 2 de `regras-dos-lutadores.md` proíbe diagonal, `$`,
> meia-lua, 360° e carga no comando de especial (especial = 2 toques cardeais + botão; super = 3 toques, `~B,F,D`
> + chute ou soco, seção 3.H), e a 3.G manda todo agarrão ter escape com y ou b. Os itens abaixo que pedem
> diagonal, meia-lua, meia-lua dupla ou agarrão sem escape seguem a convenção do gênero e **só entram se o Breno
> mudar a regra**. O resto (invencibilidade do antiaéreo, só o forte de perto cancela, tremor, contra-ataque,
> folhas novas) não depende disso.

### O que já existe (estado no jogo atual)

| Item | Comando hoje (`raiclaven.cmd`) | Estado / ação | Folha |
|---|---|---|---|
| Normais em pé x, y perto/longe, a, b perto/longe | x / y / a / b | 200, 215/210, 230, 245/240 | soco, martelo, chute_baixo, chute_alto |
| Agachados x, y (antiaéreo normal), a, b (derruba) | ↓ + botão | 400, 410, 430, 440 | baixo_soco, cabecada, rasteirinha, rasteira |
| No ar x, y, a, b | botão no ar | 600, 601, 610, 611 | ar_soco, bicicleta |
| Direcionais →y, →b, ←x, ←a | `/F,y` etc. | 216, 246, 201, 231 | martelo, chute_alto, soco, chute_baixo |
| Correntes x/y/a/b (3 + finalizador) | botão repetido | 301–303, 311–313, 321–323, 331–333 | várias (`pengaro_extra.py`) |
| Kombos de assinatura (4) | sequência | 340–347 | várias |
| Pente Voador (projétil reto) | `~D,F,a` / `~D,F,b` | 1000 / 1001 | bola |
| Golpe em arco (Borrifada, sem arte) | `~F,B,x` / `~F,B,y` | 1600 / 1601 | bola (reaproveitada) |
| Especial →↓ (deveria ser a Tesoura Ascendente) | `~F,D,x` / `~F,D,y` | 1200 / 1201 | armada (chute giratório) |
| Investida (Tesoura Voadora) | `~D,B,x` / `~D,B,y` | 1300 / 1301 | caneta |
| Giro (Tesoura Helicóptero) | `~D,B,a` / `~D,B,b` | 1100 / 1101 | compasso |
| Próximo! fraco / forte | `~F,B,a` / `~F,B,b` | 1700 / 1701 | rolamento, pente_combo |
| ↓→ x/y (repertório) | `~D,F,x/y` | 1400 / 1401 | martelo |
| Golpe baixo ←↓ a/b (deveria ser Varrida) | `~B,D,a/b` | 1500 / 1501 | chute_baixo |
| Agarrão normal / agachado / de comando | →/← + y ou b; ↓y; `~B,F,y` | 800, 840, 830 (Toalha Quente) | agarrao |
| Supers | `~B,F,D,a/b`; `~B,F,D,x/y` | 3000 (Próximo, Cliente!), 3200 (Máquina Explosiva), 3100 | golaco; martelo (sem arte) |
| Despertar Surto de Tesoura (+ exclusivos ↓↓ x/y/a/b) | x+y; `~D,D,x/y/a/b` | 2000; 3400–3403; golpes 3405–3435 | despertar_a/b (= provoca), poses escurecidas |
| Defensivas: aparar, rolamento, afastar, corrida, recuo, superpulo | F+c; x+a; y+b; FF; BB; ↓↑ | 760, 700/705, 720/260/650, 100, 105 | defesa, rolamento, afastar, anda |

### Diferenças entre ficha e jogo (antes de qualquer item novo)

- **x em pé mostra a tesoura, não o pente:** 200 usa `soco0..3` = quadros 4, 6, 6, 7 de `soco`, e o 6 é a tesoura
  fechando. Na ficha x é Pentada (pente). Refazer `soco` só com pente (bloco acima) resolve.
- **→ + b é golpe por cima na ficha (Machadada de Tesoura)**, no jogo 246 usa `chute_alto`. Desenho errado para a
  função (overhead tem que ler como "de cima"). Trocar para `martelo` ou folha nova `machadada`.
- **Comandos da tabela de especiais não batem:** Pente Voador está em `↓→ a/b` (ficha: x/y); Tesoura Ascendente
  (ficha →↓ x/y) toca a arte do chute giratório; Tesoura Helicóptero em `↓← a/b` (ficha →← x/y); Varrida em `←↓ a/b`
  com arte de bico de sapato; Pente Girando não existe. É o que a ficha já admite ("ainda não foram ligados um a um").
  Também: Tesoura Voadora (ficha ↓→ a/b) está em `~D,B,x/y` (1300, `caneta`).
- **O `movelist.dat` do jogo dá outros nomes aos mesmos estados** (renomeação por texto em `gerar_raiclaven.py`
  sobre a lista do Gutto): "Tesoura Voadora" = →↓ P (1200, armada), "Varrida" = ↓← P (1300, caneta), "Tesourão /
  Machadada" = ↓→ P (1400), **"Cadeira Giratória" = ←↓ K (1500/1501)**. Os exclusivos do Surto (↓↓ x/y/a/b, 3400–3403)
  ainda aparecem como "Beijo do Cavalo", "Coice da Corrente", "Galope Atravessado", "Queda do Cavalo" (nomes do
  Pengaró), e o Próximo! diz "b passa e chuta" (hoje é a sequência do `pente_combo`).
- **Pente Voador desenhado em código** (`pente()` em `gerar_raiclaven.py`): preto (20,20,24) e cinza neutro
  (110,110,120), fora da paleta e contra a regra 4. Trocar pelos tons 2/3/4 quando a paleta entrar.

### O que falta ou muda (ordem por impacto)

| # | Mudança | Comando alvo | Estado | Frame data alvo | Folha nova? |
|---|---|---|---|---|---|
| 1 | **Antiaéreo especial de verdade: Tesoura Ascendente** com invencibilidade que cobre o ativo (hoje 1200 é a arte de chute giratório e herda do Pengaró `NotHitBy` com `Time < 5`, que cobre só o 1º tick do ativo: ativo 4–9) | `~F,D,DF, x/y` (aceita `~F,D,x`) | 1200/1201 | x: startup 4, invencível 1–5 só contra ar; y: startup 3, invencível 1 até o fim do ativo, recuperação ~28, lança | **sim** `tesoura_ascendente` (sobe girando o corpo, lâmina aberta acima; diferente de `cabecada`, que fica para o ↓y) |
| 2 | **Forte de perto cancelável** em especial e super: 215 (y perto) e 245 (b perto) entram em "Pode cancelar"; 210/240 de longe não | — | 215, 245 | cancel na janela de contato | não |
| 3 | **Comandos com diagonal** em todos os especiais (meia-lua, Z, meia-lua para trás), cardeais como folga | `~D,DF,F` / `~F,D,DF` / `~D,DB,B` | todos 1000–1701 | buffer atual | não |
| 4 | **Agarrão de comando "Cadeira Giratória"** (o nome hoje está no `movelist.dat` para o 1500/1501 ←↓ a/b; renomear lá antes) (senta o oponente numa cadeira imaginária, gira, despeja): startup 1, sem escape; a Toalha Quente vira o agarrão normal | `~F,DF,D,DB,B,F, y` (meia-volta + frente) | 830 (novo comando) | startup 1, alcance curto, 150 de dano, 30 ticks abertos no erro | **sim** `cadeira` (gira o oponente invisível, pose de barbeiro, empurra) |
| 5 | **Super com meia-lua dupla:** Próximo, Cliente! (some no talco, aparece e solta 8 cortes) | `~D,DF,F,D,DF,F, a/b` | 3000 | invencível do tick 1 ao fim do superpause; 1 estoque | **sim** `super_cortes` (8 cortes de 8 ângulos) + `fx_talco` |
| 6 | **Máquina Explosiva** com arte própria e meia-lua para trás dupla | `~B,DB,D,DF,F,B,DB,D,DF,F, x/y` | 3200 | 2 estoques; projétil lento que explode; invencível no flash | **sim** `maquina` (liga a máquina, ela vibra, arremesso por baixo) + `fx_maquina` (máquina, faísca amarela, explosão) |
| 7 | **Projétil em arco (Borrifada)** com desenho próprio; só 1 projétil na tela | `~D,DB,B, x/y` | 1600/1601 | fraco: arco curto; forte: arco longo, passa por cima do agachado | **sim** `borrifada` (borrifador na mão esquerda, bombeia 2 vezes) + `fx_borrifo` |
| 8 | **Tesoura Helicóptero** com o braço girando de verdade (hoje `compasso` é tesoura subindo, lê igual ao `martelo`) | `~F,B, x/y` (→← da ficha; livre depois que a Borrifada sair de `~F,B,x/y`) | 1100/1101 | 3–4 acertos, empurra; -6 na defesa | sim: refazer `compasso` (bloco 21) |
| 9 | **Golpe baixo de chão (Varrida)** com a vassoura | `~D,DB,B, a/b` | 1500/1501 | forte avança e derruba; bate baixo | não: usa `rasteira` em vez de `chute_baixo` |
| 10 | **Especial de leitura: Pente Girando** (postura que rebate golpe alto/médio e responde com corte) | `~B,DB,D, x/y` | novo (ex. 1800/1801) | ativa 2–20, falha deixa 20 ticks abertos; não pega baixo | **sim** `pente_girando` (pente girando à frente como escudo + resposta de tesoura) |
| 11 | **Super máximo** (Próximo, Cliente! cheio) | `~D,DF,F,D,DF,F, a+b` | novo (3010) | 2 estoques (1 no Surto), 1,5x dano, termina lançando | sim: `super_final` (fecha a tesoura com as duas mãos e posa) |
| 12 | **Especial no ar:** Pente no Voo em diagonal para baixo | no ar `~D,DF,F, x/y` | novo (1050) | startup 8, quica no acerto | **sim** `ar_pente` |
| 13 | **Impacto pesado:** tremor 6–8 ticks nos fortes de tesoura, som seco de "tchac" sintetizado | — | 210/215/240/245, finalizadores | pausetime 8/6, 12/9, 16/10 | não (efeito `fx_corte`, som próprio) |
| 14 | **Contra-ataque** (acerto no startup do outro): +4 ticks de hitstop, texto "CONTRA!" | — | todos os HitDef | — | não |
| 15 | **Despertar com arte própria** e ativação no meio do combo (cancel de normal que encostou) | x+y | 2000 | dura até a barra drenar | **sim**: `despertar_a`, `despertar_b` (blocos 32–33) e as `e_` do Surto (ginga, anda, soco, martelo, cabecada, apanha) |
| 16 | **Conferências pequenas:** recuo invencível nos ~4 primeiros ticks; rolamento 20–24 ticks, agarrável nos últimos ~6; investida fraca -2, forte -10 na defesa; Próximo! fraco com recuperação visível (≥ 18 ticks) | — | 105, 700/705, 1300/1301, 1700 | — | não |

Decisões do Breno (não implementar sem resposta): correntes de 4 golpes (o sabor arcade 90 é no máximo 2 golpes +
cancel); se a Toalha Quente fica como agarrão normal e a Cadeira Giratória vira o de comando; se o super máximo existe
para ele ou só para o Pengaró. Tudo segue o checklist da seção 9 de `regras-dos-lutadores.md`; caixas de golpe não mudam
com a troca de arte; folha nova só depois que a paleta fixa estiver no pipeline (quantizar depois de `animar_folha.py`).

---

## (d) Problemas de animação e anatomia já visíveis nas folhas

| Folha | Quadro(s) | Problema |
|---|---|---|
| `provoca`, `despertar_a`, `despertar_b` | todos | **Arquivo idêntico** (mesmo md5). O Despertar não tem arte: liga a provocação. |
| `soco` | 5–7 | Golpe de x vira tesoura no meio; o gerador usa os quadros 4, 6, 6, 7, então o x em pé mostra a tesoura fechando. Quadros 1–4 e 5–8 são dois golpes diferentes numa folha só. |
| `agarrao` | 3–4 | O braço de aço some: **duas mãos humanas** segurando a toalha (membro trocado; a direita não tem mão). |
| `agarrao` | 5 | Figura girada de costas, avental e tubo somem, toalha acima da cabeça; troca de leitura do personagem entre 4 e 6. |
| `vitoria` | 5–6 | Braço erguido com pele mais clara/rosada que o resto (tom fora da pele); bíceps inflado de outra proporção. |
| `vitoria` | 7–8 | Braço de aço ergue a tesoura atrás da cabeça (continua no lado certo) e a mão humana da frente vira punho fechado: **o pente desaparece**. Não há troca de braços (conferido pelo cético). |
| `agarrao` | 7 | O gerador solta o oponente neste quadro, mas a folha já mostra ele penteando o cabelo: o arremesso fica sem pose de arremesso. |
| `armada` | todos | Folha 1672x941: figura a **77% da escala** (274 px contra ~356) e células estreitas; o quadro 2–3 dá as costas e perde o avental. |
| `caneta` | todos | Folha 2508x627, só 5 figuras separáveis (as outras se encostam); escala ~89%. |
| `compasso` | 3–6 | Não é "helicóptero": a tesoura sobe por cima da cabeça como no `martelo`; o golpe-cara do lutador lê igual ao corte de cima. |
| `afastar` x `chute_alto` | 4–5 | Mesma pose de chute alto nas duas folhas (sola na altura do peito/cabeça igual); o empurrão não se distingue do chute de navalha. |
| `ar_soco` | 1, 7, 8 | Figura em pé no ar (pernas esticadas como na ginga), não encolhida; transição seca para o 4 (salto de 286 para 365 px de altura). |
| `bicicleta` | 1, 7, 8 | Idem: pose de ginga solta no ar; o chute cruzado (5) é horizontal e baixo, não pega na altura da cabeça. |
| `queda` | 1–8 | Escala cai ao longo da folha: deitado nos quadros 5–8 fica visivelmente menor que o corpo em pé (altura do corpo deitado 111–158 px para um homem de ~356). |
| `levanta` | 1 → 2 | Quadro 1 deitado pequeno e magro (155 px de comprimento) e o 2 já sentado em tamanho cheio: salto de escala. |
| `derrota` | 1 | Pose de pé diferente da ginga (outro ombro, outro ângulo) antes de sentar. |
| `rolamento` | 4–6 | Nuvem de talco desenhada junto com o corpo: o quadro 5 é **só nuvem**, sem personagem; o 4 tem a figura dentro do talco (some no corte e no quantizador). |
| `pente_combo` | 1, 5, 7 | Efeitos no corpo: nuvem no 1, linha de giro no 5, brilho no 7 (proibido na folha de corpo). Quadro 2 e 4 trocam a altura do ombro de aço (ombreira sobe e desce sem motivo). |
| `golaco` | 2, 5 | Agachamento muito baixo e torcido no 5 (perde o avental); só 7 figuras separáveis. |
| `cabecada` | 5 | Braço de aço esticado acima da cabeça com 567 px de altura total (+60%): exagero maior que os 10–20% de contato; a tesoura passa do topo da célula na escala do jogo. |
| `martelo`, `bola`, `chute_baixo`, `soco`, `rasteirinha`, `baixo_soco`, `rasteira` | vizinhos | Só 5–7 figuras separáveis por coluna livre: figuras encostando na célula vizinha (o corte por célula pode levar pedaço do quadro do lado). Conferir os recortes em `quadros/<folha>/`. |
| todas | todos | 83–134 mil cores por folha; roupa preta saindo roxo-magenta (323–332°), perto da cor do fundo; contorno preto puro em **todas** as folhas (24 mil a 81 mil pixels com R, G e B < 20 por folha). Nenhuma passa nas regras 1, 4 e 5 sem quantizar. |
| todas | — | Pele estável (10–16°), sem troca de personagem entre folhas: rosto, cavanhaque, tubo e avental se mantêm. A identidade está boa; o problema é escala, membro trocado e efeito no corpo. |

---

## Revisão do cético

Conferido contra as 34 folhas (md5, tamanho, matiz medido por script), `folhas_raiclaven.py`, `gerar_raiclaven.py`,
`gerar_pengaro.py` (índices `f_<folha><i>` são 0-based), `chars/raiclaven/raiclaven.cmd`, `.cns` e `movelist.dat`.
Nada no repo foi editado.

**Confirmado:** `provoca` = `despertar_a` = `despertar_b` (md5 `ddf430b6`); `ginga` = `referencia_ginga`; `armada`
1672x941 com 277 px de altura; `caneta` 2508x627; `cabecada` 569 px; `soco0..3` = quadros 4, 6, 6, 7 (6 = tesoura);
246 usa `chute_alto`; 1200 toca `armada`; hex da paleta batem com os HSV da tabela; `agarrao` 5 de costas;
`pente_combo` com nuvem no 1, linha de giro no 5 e brilho no 7; todas as folhas listadas existem e todas estão em
`FOLHAS` do gerador (+ `pente_combo`). Nenhuma folha órfã nem faltando.

**Corrigido:**
1. Pele: faixa medida 8,8–15,7° (não 10–16); roupa crua 325–345° (não 323–332).
2. Regra 3: o tom 6 (`#8A3424`, 9,4°) caía fora das faixas da própria ficha (sombra 0–8, médio 13–18). Sombra vira 0–10°.
3. Recolor do Despertar: os índices 12 e 13 são compartilhados (lâmina, dentes, toalha, talco, faixa do tubo). Trocar
   o 12 para amarelo pintaria tudo. Olho e faísca vão desenhados.
4. MOTION `agarrao`: o gerador solta no quadro 7, não no 6. O 7 passa a ser o arremesso e o 8 o pente no cabelo.
5. MOTION `pente_combo`: os ativos do gerador são os quadros 2, 4 e 6–7. Os quadros 3 e 5 eram golpes que não batem e
   viraram transição.
6. MOTION `compasso` 8 e `caneta` 8: o gerador segura esses quadros por 14–26 ticks de recuperação. Eles não podem ser
   a pose base.
7. `vitoria` 7–8: os braços **não** trocam (o aço ergue a tesoura do lado certo). Só o pente some.
8. Kit: o `movelist.dat` já usa "Cadeira Giratória" para o 1500/1501 (colide com o item 4). Os exclusivos ↓↓ do Surto
   ainda têm nome de cavalo e faltavam na tabela. Tesoura Voadora está em ↓← x/y. O Pente Voador em código sai fora da
   paleta. O 1200 é invencível até o 1º tick do ativo, não "antes".
9. Contorno preto puro: em todas as folhas, não em "vários quadros".

**Em dúvida (não mexi):**
- `agarrao` 3–4 "duas mãos humanas": na redução parece o antebraço de aço chegando na toalha. Conferir em zoom.
- `ar_soco`/`bicicleta` 1, 7, 8 "em pé no ar": na redução parecem a base agachada da ginga, de pernas dobradas, e não
  esticadas. O problema real é a pose de chão no ar.
- Aço médio `#9097B4` passa na regra 4 no limite exato (saturação 20,0%). Preto luz `#776A9C` (valor 61%) pode ler
  lilás demais para "roupa preta".
- Contorno `#24182C` a 276°, fora dos 225–275° da regra 4 (que não cobre contorno). Contorno e preto sombra estão
  próximos (17% x 29% de valor): risco de a silhueta fundir na roupa.
- A ordem de prioridade dos MOTION continua uma estimativa (sem medir o uso real).

## Pendência de pipeline

`quantizar_folha.py` só conhece os papéis do Pengaró (`PAPEIS = {"pengaro": ...}`) e `conferir_arte.py` mede a regra 3
nas faixas do Pengaró. Antes da primeira folha deste lutador passar pelo pipeline: acrescentar os papéis dele em
`PAPEIS`, rodar `LUTADOR=raiclaven python ferramentas/quantizar_folha.py --montar-paleta <folha>` e conferir o JSON contra a
tabela de paleta acima. A regra 3 dele usa faixas deslocadas (sombra 0–10°, médio 13–18°, luz 21–26°, brilho 32–40°): o `conferir_arte.py` precisa ler as faixas do lutador, senão reprova a pele certa.
