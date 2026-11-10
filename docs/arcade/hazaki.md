# Hazaki: arte arcade e kit

> Síntese do estudo arcade de 2026-11-10 (nada testado no motor, nada commitado pela síntese). A fila de geração no
> ChatGPT, com os prompts prontos, fica em [`fila.md`](fila.md); estilo e regras em
> [`../biblia-de-arte.md`](../biblia-de-arte.md#estilo-arcade-anos-90). Folhas de contato e medições brutas ficaram no
> scratchpad da sessão, fora do repo.


## Quem ele é no jogo

O Hazaki é o segundo lutador, o **rival de treino** do Pengaró: karateca de academia de bairro ("Giro de Garagem",
"Faixa no Asfalto", "Salto de Dojô", "Academia do Inferno"), intro "Bora ver se aguenta o treino.", bordão "EU SOU
GOSTOSO!" em todas as falas. No código ele tem um gerador fino, `gerar_hazaki.py` (118 linhas): recorta 12 poses de
`karate.png` e 8 de `diabo-loiro.png`, troca alguns sprites e chama `montar_sprites/air/cns/cmd` do `gerar_pengaro.py`
com `hazaki=True`; as poses são deformadas por `gira`/`move`/`mistura`/`estica`. Das 8 do Diabo, a D2 não é usada. Na prática
virou **boneco de teste**: é o oponente de toda filmagem e do robô (Pengaró x Hazaki, Raiclaven x Hazaki), e o LOGBOOK o
deixa de fora de propósito em cada fase ("Hazaki byte a byte igual"). Ele já tem um furo conhecido: arremessado pelos
outros, some (o `.sff` dele não tem os 25 desenhos de vítima).

**Vale virar folhas do ChatGPT?** Sim, mas depois do Pengaró e em duas etapas. Ele aparece em todo vídeo de conferência,
então a cara dele pesa no jogo inteiro; hoje cada golpe é uma pose estática girada, abaixo do mínimo da seção 7 das
regras. Ordem sensata: (1) primeiro o passo de quantização da paleta fixa entrar no pipeline (senão as folhas nascem no
estilo antigo); (2) as 8 primeiras folhas da lista (b), que cobrem ~80% do tempo de tela; (3) o resto e o Diabo Loiro.
Antes de gerar qualquer folha, resolver os dois pontos de conteúdo abaixo. O `gerar_hazaki.py` precisa ler folhas
próprias em vez de recortar `karate.png`, e o `montar_sprites(hazaki=True)` hoje desliga folhas (`s.folhas = not hazaki`):
trabalho de código fora desta ficha.

**Conteúdo e originalidade (resolver antes):**
- `karate.png` K12 e `diabo-loiro.png` D7 mostram as **duas palmas juntas à frente soltando bola de fogo**: é pose-
  assinatura de jogo comercial. Some. O Punho de Concreto vira soco único no chão/à frente que solta lasca de asfalto
  (proposta em (c)). De quebra resolve a incoerência atual: o desenho mostra fogo, mas o 1000/1001 no `hazaki.cns` é um
  soco de avanço na altura do peito, **sem projétil nenhum** (a ação 1005, bola quicando, está no `.air` e nenhum estado a
  solta).
- K11 (punho único para cima, boca aberta, uma perna de apoio) beira o gancho-assinatura do mesmo gênero; a
  Ascensão de Faixa ganha pose própria (ombro e joelho subindo juntos, faixa chicoteando).
- Diabo Loiro: o arquétipo "karateca que vira demônio de olho vermelho" é convenção; o que aproxima de obra comercial é
  a **juba loira espetada para cima**. Manter loiro (é o nome), mas juba longa jogada para trás, chifres como leitura
  principal. Ele é homem e o bordão é dele: nada de piada de "loira" (regra de conteúdo do `como-trabalhar.md`).
- `sprites/hazaki-selecao-kof.png` (e `pengaro-selecao-kof.png`): o arquivo leva nome de jogo comercial; renomear quando
  mexer no retrato (o nome está em `gerar_hazaki.py` linha 79).

## (a) Paleta fixa: 15 cores + transparente

Medida nas folhas atuais (quantização em 20 tons): pele laranja-bronze h 21–30°, gi índigo h 246–254° com saturação
baixa (~26%), debrum laranja h 24° s 82%, faixa quase preta (#151116, h 288°), ataduras brancas, pulseira teal. A pele real
está saturada e sem matiz deslocado (claro em 28–30°, sombra em 21–23°); a rampa abaixo corrige para as regras 3–5. O
`#0a0609` e o `#151116` das folhas violam a regra 5 (preto puro) e saem.

**Forma normal** (pele 5, gi 3, debrum 2, faixa/cabelo 1, ataduras 2, pulseira 1, contorno de roupa 1 = 15):

| # | Papel | Hex | HSV (h°, s%, v%) | Nota |
|---|---|---|---|---|
| 0 | transparente | — | — | magenta `#FF00FF` na folha |
| 1 | contorno da roupa, cabelo no escuro | `#1c1832` | 249, 52, 20 | azul-roxo; mín. RGB 24 (regra 5) |
| 2 | pele sombra profunda = contorno da pele | `#7a2e26` | 6, 69, 48 | vinho (regra 3: 5–15°) |
| 3 | pele sombra | `#b04f30` | 15, 73, 69 | |
| 4 | pele médio | `#de8448` | 24, 68, 87 | regra 3: 21–26° |
| 5 | pele claro | `#f6b468` | 32, 58, 96 | regra 3: 30–40° |
| 6 | pele brilho duro (testa, ombro, nó dos dedos) | `#fcd9a0` | 37, 37, 99 | creme |
| 7 | gi escuro | `#2b2650` | 247, 52, 31 | |
| 8 | gi médio | `#47436a` | 246, 37, 42 | tom dominante da roupa |
| 9 | gi luz | `#6c6e9c` | 238, 31, 61 | luz desloca para o azul frio |
| 10 | debrum laranja | `#d8661c` | 24, 87, 85 | mais saturado que a pele, para separar |
| 11 | debrum sombra | `#8e3a1a` | 17, 82, 56 | |
| 12 | faixa preta e cabelo | `#3a2a30` | 338, 28, 23 | quase preto quente, nunca `#000` |
| 13 | atadura branca | `#f4f1ea` | 42, 4, 96 | |
| 14 | atadura sombra | `#a9a6cc` | 245, 19, 80 | sombra fria lilás (análogo da regra 4) |
| 15 | pulseira teal (pulso de trás) | `#2a9d9a` | 178, 73, 62 | marca de identidade |

**Diabo Loiro** (troca de paleta + folhas `d_` próprias; pele 5, gi 2, brasa 1 nova, cabelo loiro 2, chifre/faixa 1,
atadura 1, pulseira 1, olho 1, contorno 1 = 15): mantém 1–6 (as rachaduras usam o #2), gi vira `#2b2440` / `#47436a` (sem
luz, roupa mais sombria), debrum vira brasa `#ffb02e` com sombra no pele médio `#de8448` (mesmo matiz 24° do debrum
antigo), cabelo `#f2d27a` (luz) / `#c98a34` (sombra, matiz desce a 35°), chifre e faixa `#5a3a2c`, atadura só `#f4f1ea`,
pulseira teal `#2a9d9a` (a `diabo-loiro.png` mantém a pulseira em D2–D6 e D8), olho `#e3321e`. As brasas soltas dos punhos (D1, D2, D6) **não** são do
corpo: viram efeito `fx_brasa` em fundo verde, com a rampa de efeito própria do Hazaki (laranja-ouro, diferente do
âmbar do whisky e do violeta do Pengaró).

## (b) Prompt base e folhas

### Prompt base (troque só o bloco MOTION; anexe a folha-referência aprovada em toda folha)

```
Generate ONE image with your image generation tool. Do not write code and do not edit any file.
The attached sprite sheet shows the exact character to keep: same young man, same face, short dark cropped hair with a
faded side, warm tan skin, clean-shaven, muscular; sleeveless navy-indigo karate top with orange piping on the collar,
lapels and hem, matching wide navy gi pants with one orange stripe down the outer side of each leg, dark near-black belt
knotted at the front with two hanging tails, white cloth wraps on both wrists, a teal wristband over the wrap on the rear
wrist only, barefoot.
Art style: hand-pixeled 1990s arcade fighting game sprite. Heroic anatomy: broad shoulders, narrow waist, big hands and
feet, thick forearms and calves. Shading in 2-3 large hard-edged flat planes per form, no gradients, no dithering, no
noise, no texture, no veins, abdomen as 6 simple blocks. Shadows shift hue: skin shadows go toward wine red, highlights
toward warm cream; the navy gi gets cool blue light, the white wraps get cool lilac shadows, never grey or beige.
1-pixel colored outline (dark wine on skin, dark blue-purple on clothes), never pure black, lighter or missing on the lit
side. Small hard 1-3 pixel specular highlights on forehead, shoulder, chest, knuckles and shin, one highlight band on the
hair. Limited palette look.
Layout: one single row of 8 frames, evenly spaced, wide image, side view, always facing right, same size and scale as the
attached sheet, feet on the same ground line. Flat solid magenta background (#FF00FF) everywhere, no shadow, no ground,
no text, no numbers, no borders, no effects.
MOTION: <bloco da folha>
Consecutive frames differ by a small amount, so the motion looks smooth in sequence.
```

Para as folhas `d_` troque a descrição do corpo por: *"the same man transformed: long wild blond mane swept back (not
spiked upward), two curved dark horns from the forehead, glowing red eyes, thin glowing ember cracks on the skin, the same
navy gi torn ragged at the hem and armholes with glowing ember-orange piping, belt tails frayed, white wrist wraps, the
same teal wristband on the rear wrist only, same clean-shaven face and same body size as the normal form"* e anexe a `d_parado` aprovada. Brasa solta e fogo saem do desenho (viram `fx_brasa`).

### Folhas em ordem (MOTION como vai no prompt)

| Lote | Folha | Usada em | MOTION |
|---|---|---|---|
| 1 | `parado` | 0 parado (hoje K1) | standing karate guard, fists up, weight on the back leg, breathing bounce: 1–4 sink slightly, 5–8 rise; 8 loops into 1; belt tails sway one frame behind the hips; feet never slide. |
| 1 | `anda` | 20 andar, 100 correr (K2/K3) | guarded forward walk, two-step cycle, fists stay up, 1 contact front foot, 2 down, 3 passing, 4 up, 5–8 same with the other leg; the wide pants fold and swing at each step, belt tails lag; 8 loops into 1. |
| 1 | `defesa` | guarda, recuar, aparar, partes de 1000/1100/1200/3200 (K6) | 1 stance, 2–3 forearms rise to cover the face, torso compacts, 4–5 hold the block with a small push back on impact, front foot braced, 6–8 back to stance; belt tails flick on the impact frame. |
| 1 | `soco` | 200, 201, 210/215, 216, agarrão (K9) | quick straight punch with the front fist: 1 stance, 2 shoulder loads back, 3 hips start turning, 4 fist out, 5 contact with the fist drawn 15% larger, shoulder thrust forward, torso turned showing the chest, 6 hold, 7–8 back to stance; gi top folds at the waist on contact. |
| 2 | `agachado` | 10–12, defesa baixa, pouso (K4) | 1 standing guard, 2–4 lowers into a deep crouch, knees wide, fists up, 5–8 hold the crouch with a small breathing bounce; 8 loops into 5; the pants bunch at the knees. |
| 2 | `chute` | 230/240/245/260, 1300, 231 (K10) | heavy side kick at chest height: 1 stance, 2–3 big wind-up, knee chambers high, torso coils away, 4 snap, 5 contact with the leg and foot stretched 15%, hips forward, the pant leg flares open, 6 hold, 7–8 long recovery; belt tails lag two frames. |
| 2 | `apanha` | 5000–5090, 5300, tonto (K7) | hit reaction: 1 stance, 2 head snaps back, torso twists, hair and belt tails fly forward, 3–4 staggers back on the heels, 5–6 leans and starts falling backward, 7–8 airborne falling flat, arms loose (no rotated standing pose). |
| 2 | `pulo` | 40–47, mortal (K5) | vertical jump: 1 crouch load, 2 push-off with legs extended, 3–4 rising with knees tucking, 5 apex fully tucked, 6–7 falling with legs opening, 8 landing reach; pants and belt tails trail the motion. |
| 2 | `baixo_soco` | 400 (K4 deslocado) | crouching jab: 1 crouch, equal to the crouch pose of the crouch sheet, 2–3 shoulder loads, 4–5 contact: front fist out 15% larger, rear fist at the chin, 6–8 back to the crouch; 8 equals 1. |
| 2 | `rasteira` | 430/440, 1400, 3000 (K10 girado) | crouching low sweep: 1 crouch, 2 hands drop toward the ground, body pivots low, 3–4 front leg sweeps in a wide arc close to the ground, 5 contact with the leg and foot stretched 15%, pant leg flared, 6 hold, 7–8 long recovery back to the crouch. |
| 2 | `ascensao` | 1200/1201 Ascensão de Faixa, 410 (K11) | rising anti-air from a crouch, shoulder-first, feet stay on the ground line: 1 deep crouch, 2 coils with the front elbow tucked, 3 surges up onto the toes stepping forward, 4–5 front shoulder and elbow leading upward high above the head with the front knee raised, belt tails whipping up (contact on 4–5, arm and shoulder drawn 15% larger), 6 hold on the toes, 7–8 settles back down to stance. No single fist straight up, no jump: the feet stay on the ground. |
| 3 | `punho_concreto` | 1000/1001 Punho de Concreto, soco de avanço (K12) | one-handed lunging straight punch: 1 stance, 2–3 steps in and rears the front fist back at the hip, 4 drives forward, 5 contact at chest height with the fist 15% larger, shoulder thrust forward, 6 hold, 7–8 back to stance; no projectile drawn, no fire. |
| 2 | `queda` | cair (K8) | 1 airborne falling flat, 2 back hits the floor, 3 bounces slightly, 4–8 lies still, head toward the back, belt tails settle. |
| 2 | `levanta` | 5120 (K8+K4) | 1 lying flat, 2 rolls to the side, 3 hand pushes on the floor, 4 knee under, 5 kneeling, 6 rising, 7–8 stance. |
| 2 | `ar_soco` | 600/601 (soco girado) | mid-air downward hammer fist: 1 tucked, 2 rears the fist overhead, 3–4 swings down, 5 contact angled down 45°, fist 15% larger, 6 hold, 7–8 tuck again |
| 2 | `ar_chute` | 610/611/650 (chute girado) | mid-air straight kick: 1 tucked, 2 chambers, 3–4 extends, 5 contact with leg stretched 15% pointing slightly down, pant leg flared, 6 hold, 7–8 tuck |
| 3 | `machado` | 246 Machado de Dojô, 3200 (K11) | overhead axe kick: 1 stance, 2–3 front leg swings straight up high, torso leans back, 4 apex with the leg vertical, 5 heel chops down, contact at head height, foot 15% larger, 6 hold, 7–8 long recovery stepping down. |
| 3 | `giro_garagem` | 1300/1301 Giro de Garagem | advancing turning back kick, grounded: 1 stance, 2 front foot steps across, 3 spins showing the back, 4 rear leg chambers, 5 contact, heel out, leg stretched 15%, 6 hold, 7–8 recovers facing right. Grounded spin, never floating. |
| 3 | `agarrao` | 800/810 (K9 espelhado) | 1 reaches with both hands, 2 grabs collar and arm, 3 pulls close, 4 turns the hips under, 5–6 hip throw over the shoulder, 7 releases, 8 back to stance. |
| 3 | `vitoria` | 181 (K6+K11) | ties the belt tight with a sharp pull, then fists on the hips, chin up, chest out (1–8, last frame holds) |
| 3 | `provoca` | 190–195 (K6+K11) | points at the opponent, then flexes one arm and taps the biceps, grinning (1–8, loops into 1) |
| 3 | `despertar` | 2000 (K6 girado + D1) | transformation: 1 stance, 2–3 clenches fists and bends forward, 4 belt piping starts glowing, 5 hair lightens and grows back, 6 horns push out, 7 straightens roaring, 8 final pose of the awakened form. Full body in frame 8. |

## (c) Kit na essência de luta arcade 90

**O que já existe** (estado no `.cns`/`.cmd` atual): normais em pé 200/210/230/240 e 215/245/260, com perto/longe já
separado (y e b colados, `p2bodydist x < 30`, viram 215 e 245); agachados 400, 410
(↓y), 430, 440 (rasteira); aéreos 600/610/650 e 601/611; direcionais 216 (→y Cotovelo de Faixa), 246 (→b Machado de
Dojô, por cima, `HA`), 201 (←x), 231 (←a); correntes curtas (cancel de 200/230/400/430 por `movecontact`, linhas 440–525
do `.cmd`); especiais 1000–1501 (seis famílias, x/y ou a/b); contra-ataque 1100/1101 Guarda de Aço (`ReversalDef`);
cancel de especial para super (`movehit <= 8`, linhas 223/232); supers 3000 (`~B,F,D` + a ou b, 1 estoque) e 3200
(`~B,F,D` + x ou y, 2 estoques), comando e botões já iguais à seção 3.H; Despertar 2000 (`x+a+y`, 1000 de energia, sem
ressaca); nenhum `Projectile` no `.cns`; agarrão 800/810; parry 760–762; rolamento 700/705;
passo para trás invencível (-2).

| # | Item | Estado hoje | Proposta | Folhas novas |
|---|---|---|---|---|
| 1 | Antiaéreo de verdade | 1200/1201 Ascensão de Faixa (`~F,D` x/y), golpe de chão (`type = S`) que lança a vítima (`-2,-7`), **sem `NotHitBy`** | x: invencível só contra ar no começo; y: invencível do tick 1 ao fim do ativo, recuperação longa (~28) | `ascensao`, `d_ascensao` |
| 2 | Só o forte de perto cancela | perto/longe já existe (215/245 perto, 210/240 longe); 215 e 245 já cancelam, mas o **210 (y longe) também cancela** (linha 214) e o 240 não | tirar o 210 da lista do `var(1)`; perto ganha arte própria (hoje 215 usa a arte do soco) | `soco_perto`, `chute_perto` |
| 3 | Despertar fora da regra | `power >= 1000` e gasta 1000 (seção 4 pede barra cheia, gasta tudo) | `power >= powermax`, gasta tudo; `x+a+y` pode ficar se a ficha declarar | não |
| 4 | Agarrão de comando (3º, de lore) | não existe (só 800/810; 820/821 são estados de vítima) | "Nó de Faixa": colado, `~B,F, y` (entrada padrão da seção 3.G), prende com a faixa preta e projeta; escapa com y/b no começo como todo agarrão | `agarrao_faixa` (+ `vitima`) |
| 5 | Agarrão agachado | não existe (kit G pede 3) | colado, ↓+y: puxa a perna e derruba | `agarrao_baixo` |
| 6 | Supers sem invencibilidade | `~B,F,D` (já é o da regra), **sem `NotHitBy`** no 3000/3200 | manter o comando; invencível do tick 1 ao fim do superpause | `faixa_asfalto`, `pose_final` (+ `d_` de cada) |
| 7 | Projéteis (regra E pede 2) | **nenhum**: 1000/1001 é soco de avanço; a ação 1005 (bola) está órfã no `.air` | Punho de Concreto vira soco no chão que solta lasca rasteira (baixo; caixa e `Projectile` novos no CNS); novo "Cone de Obra" `~F,B` x/y em arco (`~D,B` x/y já é a Guarda de Aço), cai na frente | `punho_chao`, `arremesso`, `fx_concreto`, `fx_cone` |
| 8 | Ir para trás do oponente | não existe | "Rolada de Tatame" `~B,F, a/b` (o `~D,U` bateria no superpulo `$D,$U`): rola por baixo e chega virado; recuperação visível | `rolada_tatame` |
| 9 | Golpe por cima com arte certa | 246 existe, mas desenhado com o soco para cima (K11) | só arte | `machado` |
| 10 | Especial no ar | nenhum (1500 sai do chão) | "Queda de Faixa" no ar `~D,F, a/b`: calcanhar descendo em diagonal | `ar_queda` |
| 11 | Impacto e contra-ataque | sem tremor nos fortes, sem bônus de contra | EnvShake 6–8 ticks nos fortes; +4 de hitstop e "CONTRA!" no acerto durante o startup do outro | não |
| 12 | Despertar com animação própria | 2000 usa a pose de defesa sem lata e corta para D1 | transformação em 8 desenhos (`despertar`), golpes novos de verdade no Diabo Loiro (regra da seção 4) | `despertar` + todas as `d_` |

Comandos acima são só cardeais, 2 toques no especial e 3 no super (seção 2). Repetições conscientes: a Queda de Faixa no
ar usa o `~D,F` a/b do Giro de Garagem (separa por `statetype = A`); `~B,F` + botão é prefixo dos supers `~B,F,D`, então
no `[Statedef -1]` os supers vêm antes (seção 5.2). Os nomes são próprios (dojô de garagem, faixa, asfalto). Decisão do Breno: se o Hazaki segue como rival de treino com kit completo (50 golpes) ou fica enxuto como
boneco de teste; a lista acima assume a primeira.

## (d) Problemas que já aparecem nas folhas atuais

| Folha / quadro | Problema |
|---|---|
| `karate.png` K12, `diabo-loiro.png` D7 | pose-assinatura de jogo comercial (palmas juntas + bola de fogo); e o desenho promete projétil, mas o 1000/1001 é soco de avanço sem projétil |
| `karate.png` K11 | usado como `kick_alto` (Machado de Dojô, super 3200): **chute desenhado como soco**; usado como `baixo_cima1` (↓y agachado) com o corpo em pé; pulseira teal **troca para o braço da frente** |
| `karate.png` K3, K5, K6, K7, K9, K10, K12 | pulseira teal some (as duas ataduras brancas); só aparece em K1, K2, K4, K8 e K11: detalhe de identidade pisca entre quadros |
| `karate.png` K9 | punho de contato do mesmo tamanho da guarda, tronco não gira, quadril não avança (regra 10 falha) |
| `karate.png` K10 | faixa sem pontas soltas, calça não abre no chute (regra 12); o mesmo desenho serve chute fraco, forte, Giro de Garagem e aéreos |
| `karate.png` K10 girado 40° (`rasteira0–3`), −40° (`bicicleta`), 43° (`pisa`), 90/180/270° (`gira0–3`) | anatomia impossível: corpo inteiro inclinado, pé de apoio fora do chão, personagem de cabeça para baixo |
| `karate.png` K7 girado (`cai0–2`, `tonto`), K4 girado (`rola0–7`), K5 girado (`mortal0–11`) | queda e rolamento são a pose em pé/agachada rodando, sem desenho de queda |
| `karate.png` K8 + K4 (`levanta0`), K1 + K4 (`agacha0`), K9 + K1 (`soco0`, `soco3`) | `mistura` funde dois desenhos: dupla exposição (dois braços, dois corpos) e cores fora da paleta |
| `karate.png` K2/K3 | só 2 desenhos no ciclo de andar (mínimo 12); K3 é passo na ponta do pé, o salto entre os dois aparece como trepidação |
| `karate.png` K5 | um desenho só para subida, topo e queda do pulo |
| `karate.png` K4 | escala do gerador 74 px, contra 109 em pé; o agachado tem a cabeça proporcionalmente maior que no K1 (o desenho veio em outra escala) |
| `diabo-loiro.png` D1–D8 | **troca de personagem**: rosto mais velho e largo, maxilar maior, cavanhaque que o normal não tem, braços mais grossos que o K1; altura no gerador 115–131 px em pé (D3 91, D8 82) contra 109 do normal, então a troca de arte no meio da ação dá salto de tamanho |
| `diabo-loiro.png` D1 | usado como `defesa`, `parry`, `recua`, recuperação de soco e chute e `juliet0–3`: braços abertos rugindo, sem guarda; a D2, que tem guarda, fica sem uso |
| `diabo-loiro.png` D3 | é uma investida inclinada, usada como agachado, rasteira e soco baixo: rasteira despertada sem perna esticada |
| `diabo-loiro.png` D5 | chute em pé usado no ar (`ar_chute`, `bicicleta`, `pisa`) |
| `diabo-loiro.png` D8 | corpo horizontal em mergulho, usado como pulo vertical inteiro |
| `diabo-loiro.png` D1–D4, D6–D8 | fogo e brasa colados no desenho (deveriam ser efeito à parte); D8 com as duas mãos em brasa e pulseira teal nos **dois** pulsos |
| `diabo-loiro.png` D2–D7 | buracos da calça rasgada mudam de lugar e de forma entre quadros (visto a olho na contato, não medido) |
| ambas | contorno em preto puro (`#0a0609`, `#151116`), pele sem matiz deslocado (claro em 28–30°, regra 3 pede 30–40°), dezenas de tons por quadro (regra 1) |

## Revisão do cético

Conferido contra `karate.png` e `diabo-loiro.png` (abertas e quantizadas em 20 tons), `gerar_hazaki.py`, `repertorio.py`
(`FAMILIAS_HAZAKI`, `NORMAIS`), `gerar_pengaro.py` (ramos `hazaki`) e `chars/hazaki/*.cmd/.cns/.air`. Nada rodado no motor.

**Corrigido no texto:**
- **Gerador:** existe `gerar_hazaki.py` próprio (fino, chama o `gerar_pengaro.py`); a ficha dizia que não. A D2 nunca é
  usada (grupos 0, 2–7 e `juliet` = D1).
- **Projétil:** o `hazaki.cns` não tem nenhum `Projectile`. O 1000/1001 é soco de avanço com caixa no peito; a ação 1005
  (bola) está órfã. Item 7 virou "nenhum projétil" (a regra E pede 2).
- **MOTION que mudaria caixa/física:** `ascensao` mandava pular, mas o 1200 é `type = S` e não sai do chão (o `-2,-7` é o
  lançamento da vítima); agora fica na ponta dos pés. `punho_concreto` mandava socar o chão, mas a caixa é no peito
  (14,-96,78,-52); agora casa com a caixa de hoje, e o soco no chão foi para o item 7 como `punho_chao` (muda o CNS).
- **Regras violadas no kit:** o item 3 (diagonal) e o item 6 (meia-lua dupla) feriam a regra de comando da seção 2, e o
  `~B,F,D` dos supers já é o comando da seção 3.H. O item 6 virou só invencibilidade e o item 3 virou o Despertar fora da
  regra (gasta 1000 em vez da barra cheia). O agarrão de comando "sem escape" feria a 3.G: agora é `~B,F,y` com escape.
- **Conflitos e perto/longe:** a Rolada `~D,U` batia no superpulo `$D,$U` e virou `~B,F` a/b. Perto/longe já existe
  (215/245 com `p2bodydist < 30`); o defeito real é só o 210 (y longe) cancelar.
- **Detalhes:** supers aceitam a/b e x/y, não só a/x. O 216 do Hazaki chama "Cotovelo de Faixa" ("Tranco" é do Pengaró).
- **Pulseira:** some também em K3, K5, K6 e K7. O Diabo **tem** a pulseira teal (D2–D6, e D8 nos dois pulsos), então o
  prompt `d_` mantém a pulseira (antes dizia "no teal band"), e ela entra na paleta do Diabo no lugar do 2º tom da brasa,
  que reusa o `#de8448`. O prompt `d_` também fixa o rosto sem barba e o tamanho do normal (a folha tem cavanhaque).
- **`pengaro-selecao-kof.png`:** tem o mesmo problema de nome de jogo comercial.

**Conferido e mantido:**
- Os hex e HSV da tabela batem (recalculados). Só `#0a0609` e `#151116` têm canal abaixo de 20.
- A medição das folhas confirma a pele em 22–31°, o gi em 247–254° com s 26–30% e o debrum em 24°/82%.
- Mapa K1–K12 / D1–D8 → sprites e alturas (109, 74, 26, 116–131), K11 em `kick_alto` e `baixo_cima1`, ausência de `NotHitBy`
  no 1200/3000/3200.

**Ficou em dúvida:**
- O `#de8448` faz o debrum-brasa do Diabo encostar na pele. Pode faltar separação no olho.
- Na paleta normal, o debrum `#d8661c` e a pele média estão no mesmo matiz (24°).
- O 410 (↓y agachado) e o 1200 (em pé) dividem a folha `ascensao`. Talvez o 410 precise de folha própria agachada.
- Não medi os buracos da calça do Diabo.
- A lateralidade exata da pulseira (braço de trás ou da frente) em K11 foi vista a olho.
- O `gerar_pengaro.py` está modificado no working tree pelo outro workflow. Li o `HEAD` e os `chars/` gerados em 7/11.

## Pendência de pipeline

`quantizar_folha.py` só conhece os papéis do Pengaró (`PAPEIS = {"pengaro": ...}`) e `conferir_arte.py` mede a regra 3
nas faixas do Pengaró. Antes da primeira folha deste lutador passar pelo pipeline: acrescentar os papéis dele em
`PAPEIS`, rodar `LUTADOR=hazaki python ferramentas/quantizar_folha.py --montar-paleta <folha>` e conferir o JSON contra a
tabela de paleta acima. Além disso, o `gerar_hazaki.py` ainda recorta `karate.png` e o `montar_sprites(hazaki=True)` desliga as folhas (`s.folhas = not hazaki`): folha nova dele só entra no jogo depois dessa mudança de código, e `animar_folha.py` não tem `FOLHAS_HAZAKI`.
