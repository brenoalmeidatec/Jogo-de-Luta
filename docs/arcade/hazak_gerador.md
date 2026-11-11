# Gerador novo do Hazak: especificação

> Projeto de 2026-11-11 para o pedido da [`ficha`](../fichas/hazaki.md#pedido-para-o-alisson-recriar-o-hazak). Nada
> daqui foi implementado nem testado. As folhas que ele lê estão em [`fila_hazak.md`](fila_hazak.md); paleta e
> problemas da arte antiga em [`hazaki.md`](hazaki.md). Linhas `gp:N` são de `ferramentas/gerar_pengaro.py` no HEAD de
> 2026-11-11, `af:N` de `animar_folha.py`, `qf:N` de `quantizar_folha.py`. O id técnico continua `hazaki`; o nome na
> tela vira **Hazak**. Teste só pela sandbox (`ferramentas/sandbox.py` e o que roda em cima dela): **nunca abrir o
> `Ikemen_GO.exe` nesta máquina**.

> **Estado em 2026-11-11 (o que foi implementado de verdade).** O gerador novo existe: `ferramentas/gerar_hazaki.py`
> + `ferramentas/hazaki_golpes.py`, lendo `sprites/hazaki/quadros_arcade` (convertido por
> `ferramentas/folhas_hazak_arcade.py`, não pelo `animar_folha.py`). Entrou a ficha inteira **menos o Despertar**.
> Onde este documento e o que foi feito divergem, vale o código:
>
> - **Despertar (Diabo Loiro) fora:** as folhas `d_*` não existem. Não há comando `despertar`, estado 2000, RemapSprite,
>   paleta `_d`, cena da patroa nem velocidade por `var(20)`; `var(20)` e `var(37)` ficam reservadas e sempre 0. As
>   seções 6 e 7 daqui continuam sendo o projeto dele. A paleta da patroa (`paleta_arcade_patroa.json`, 4 cores
>   próprias) ainda não tem lugar no `.sff`.
> - **Sem quadros do meio e sem o estilo seco do `gp.Air`:** o gerador tem um emissor de `.air` próprio e simples; cada
>   elemento mostra o desenho e os ticks escritos em `hazaki_golpes.py` (notação `"folha d/tA"`). Nada de
>   `animar_folha.py`/`quantizar_folha.py`/`meio/`. Fica abaixo dos mínimos de desenho da regra 7.1 (8 desenhos por folha).
> - **Gatilhos por `Time`**, calculados da própria notação (o tick do 1º desenho com `A`), nunca `AnimElem`.
> - **Paleta fixa no `.sff`:** índices 1 a 15 = `paleta_arcade.json` (o corpo sai com a cor exata, conferido lendo o
>   `.sff` de volta); as outras 240 cores são dos efeitos e retratos.
> - **Efeitos:** pixelfx sem recolorir, todos com mistura aditiva; o `ground-slam` é pintado de cinza (asfalto).
>   Projéteis provisórios: a lasca e a estatueta saem das folhas `obj_lasca`/`obj_estatueta`, não do pixelfx (regra 8).
> - **Vítima de arremesso:** todos os grupos de `gp.SPRITES_VITIMA` existem no `.sff` (o arremessado não some mais):
>   preso = `vitima_agarrado` 1, curvado = `vitima_agarrado` 0, apanhando = `apanha` 2 e 3. Os desenhos de voo
>   (`vitima_agarrado` 3-7, `vitima_arremessado`) não entram: os arremessos dos outros só pedem as ações 5001 e 5030.
> - **Provisório:** apanhar agachado (5020-5027) usa a folha `agachado`; sem som (nenhum `.snd`: falas e sirene são
>   áudio que o Breno manda); a fuga da sirene na derrota está escrita no `[Statedef -2]` mas **não foi vista rodando**.
> - **Rolada de Tatame b** chuta com a folha `chute`, não com o `coice` (depois de virar, o coice bateria para longe).
> - **Corrente x:** o jab duplo (301) só continua para o Cutucão depois do 2º jab, e o finalizador exige 4 acertos.
> - **Robô:** `python ferramentas/testar_pengaro.py --lutador hazaki` roda o roteiro próprio do Hazak (bloco no fim do
>   `robo.lua`); os roteiros dos outros três não mudaram. O escape dos agarrões não dá para conferir pelo robô (preso,
>   o oponente não roda o `[Statedef -1]` dele, onde o robô injeta o botão).
> - O `hazaki=True` continua no `gerar_pengaro.py` e no `repertorio.py` (ninguém mais chama): a retirada fica para
>   depois, porque outra frente está mexendo nesses arquivos.

## 1. Arquitetura

Hoje o `gerar_hazaki.py` (118 linhas) recorta `karate.png` e chama `montar_sprites/air/cns/cmd(hazaki=True)` do Pengaró.
O `hazaki=True` desliga as folhas, o estilo seco, as correntes, os kombos, o agarrão de comando e o impacto por classe
(tabela completa no mapa do gerador, `gp:507-2985`). Desligar parte por parte o kit do Pengaró, como fazem
`gerar_gutto.py` e `gerar_raiclaven.py`, não serve: o Hazak não herda nenhum golpe. A decisão é **remover em vez de
embrulhar**: o novo gerador importa o `gerar_pengaro` como biblioteca, não chama `montar_air`, `montar_cns`,
`montar_cmd` nem `montar_sprites`, e o parâmetro `hazaki=True` sai do `gerar_pengaro.py` (com o `repertorio.py`
`FAMILIAS_HAZAKI` e os `replace` de nome), depois de conferido que o Pengaró, o Gutto e o Raiclaven saem byte a byte
iguais.

**Arquivos:**

| Arquivo | Papel |
|---|---|
| `ferramentas/gerar_hazaki.py` (reescrito) | monta sprites, AIR, CNS, CMD, DEF, movelist e SFF do Hazak |
| `ferramentas/hazaki_golpes.py` (novo) | a tabela de golpes da ficha no formato `pengaro_extra.Novo` + `N()` (`"folha d/ticks[A]"`), números, comandos, dano, caixas, `FRACOS`, `DESPERTADOS`, `SUBSTITUTA` (placeholders) |
| `ferramentas/animar_folha.py` | `FOLHAS_HAZAKI`, entrada em `ESCALA_2172` (`af:54`, hoje dá KeyError), `apanha` no `POR_CELULA`, modo loop no `--arcade` (`af:188`) |
| `ferramentas/quantizar_folha.py` | `PAPEIS["hazaki"]` e `PAPEIS["hazaki_d"]` (`qf:61`), com os ids `pele_sombra`, `pele_medio`, `pele_luz` e `calca_sombra` (= gi escuro / terno escuro) que o `conferir_arte.py:31-32` procura |
| `sprites/hazaki/paleta_arcade.json` e `paleta_arcade_d.json` | as 15 cores da forma normal e do Diabo (seção 6) |
| `sprites/hazaki/quadros_arcade/<folha>/00..07.png` e `meio/II_K.png` | saída do pipeline (360x260, pés em 180,220) |
| `ferramentas/robo/robo.lua`, `ferramentas/testar_pengaro.py` | roteiro por lutador (seção 10) |

**Reaproveitado do `gerar_pengaro` sem mudança** (lê os globais na hora da chamada, então basta apontar `gp.QUADROS`,
`gp.FOLHAS`, `gp.TROCA_POR_FOLHA = {}`, `gp.SEGUINTE`, `gp.ULTIMO_DESENHO`, `gp.DESENHOS_NO_AR`, `gp.FRACOS`,
`gp.ATAQUES_DESPERTADOS` e `gp.PROJETEIS` antes de montar; o `PROJETEIS` de hoje, `{1005, 1006, 3005…}` em `gp:68`, é
o que o `ajustar_clsn1` pula, então ele recebe as anims de projétil do Hazak: 1005/1006, 1605/1606, chapéu, maço,
papel, 11005/11006, 11605/11606):

- sprites: `Sprites` (com `s.folhas` False e `s.proximo` levado para 1000), `abrir_quadro`, `limpar_borda`,
  `registra_meio`, `pe_no_chao`, `caminho_fluido`, `vai_e_volta`, `carregar_faiscas`, `sprites_mantidos`,
  `escrever_sff`/`gravar_sff`;
- animação: a classe `Air` com `hazaki=False` (traz `fluido`, `seco`, `conferir_seco`, RITMO, `mapas`, `ativos` e a
  variante +10000), `remapear_animelem`, `ajustar_sparkxy`, `ajustar_clsn1` (`gp:3175`);
- CNS: `estado`, `hitdef(classe=...)`, `normal`, `fim`, `projetil`, `superpausa`, `reversao`, `IMPACTO`, `CNS_TOPO`,
  `cns_intro`, `CNS_PULOS` (revisar o que é do Pengaró dentro deles: lata, Juliet, óculos);
- CMD: `comando`/`entrada`.

**Próprio do Hazak:** a tabela de ações (`montar_air` próprio, molde no esqueleto do mapa do gerador), todos os blocos
de golpe do CNS (gerados de `hazaki_golpes.TODOS`), o `[Statedef -1]` na ordem da 5.2, os estados 20/100/105
(velocidade que muda no Despertar), a cena do Despertar com a patroa, os projéteis, o `-2` sem resto do Pengaró, a
paleta fixa no SFF e o DEF escrito do zero (`name = "Hazak"`, `displayname = "Hazak"`).

**Paleta no SFF:** hoje `paleta_global` faz MEDIANCUT de 255 cores sobre tudo (`gp:219-232`) e não garante as 15 cores
exatas. O Hazak grava paleta fixa: índices 1-15 = `paleta_arcade.json`, 16-30 = `paleta_arcade_d.json`, o resto
(faíscas, efeitos do pixelfx, balões) quantizado no que sobra. Como o `.sff` tem uma paleta só, os sprites `d_` usam os
índices 16-30 direto (a cor vem no próprio sprite; a troca de *desenho* gi → terno é o `RemapSprite` da seção 7).

## 2. Numeração: a convenção do elenco, não a 5.1 literal

A 5.1 das regras diz correntes a partir de 300, agarrões 800/810/820 e exclusivos do Despertar em 5000-5999. Os três
lutadores prontos e o robô usam outra coisa: normal em pé 200/210/230/240 seguido de 301-333, agarrões 800-821 /
830-833 / 840-841, exclusivos em 3400-3435. Além disso, 5000-5999 é a faixa dos estados de tomar golpe do
`common1.cns` (5000-5210): um exclusivo lá colide com o motor. **O Hazak segue a convenção do elenco** (é o que o robô
confere e o que não quebra o common); a divergência fica anotada aqui e no LOGBOOK para o Breno decidir se a 5.1 muda.
Todos os números ficam num dicionário só em `hazaki_golpes.py`, então trocar depois é uma edição.

## 3. Tabela de estados

Folha e quadros: `folha a-b` são os arquivos `00..07` (o quadro 1 do MOTION é o `00`). `C` marca o quadro de contato.
Caixas em pixels do jogo (eixo nos pés, virado para a direita, y para cima negativo; em pé ~109 px). Clsn2 padrão: em
pé `-14,-106,16,0`, agachado `-16,-70,18,0`, no ar `-14,-92,16,-20`. A Clsn1 abaixo é o ponto de partida; o
`ajustar_clsn1` cola na arte quando a folha nova chegar. Dano para `attack = 100`. Hitstop é o `pausetime` (P1,P2).
"Cancela" usa a notação: `E` especial, `S` super, `C` próximo passo de corrente, `K` kombo; `/hit` só se acertou
(`movehit`), sem marca é `movecontact`.

### 3.1 Básicos e sistema

| Nº | Nome | Tipo | Folha / quadros | Observação |
|---|---|---|---|---|
| 0 | parado | S | `parado` 0-7 + meio (56 desenhos, 1 tick cada) | loop; regra 7.1 pede 16-24, meta 32-48 |
| 5 / 6 | virar em pé / agachado | S / C | `vira` 0-3 / 4-7 (+ meio, até 2 ticks por desenho) | regra 7.1: 4-6 desenhos; desperto `d_vira` |
| 10/11/12 | agachar / agachado / levantar | C | `agachado` 3 por 2 ticks / 4-7 loop / `agachado` 3 por 1 tick | troca seca (7.1: 1 desenho, 1-2 ticks); `gp.SEGUINTE` 10,11 → `f_agachado4` |
| 20 | andar (frente e trás) | S | `anda` 0-7 + meio (8 + 8×5 = 48 desenhos, como `LOOPS["anda_fluida"]`), loop; trás toca invertido | estado próprio: velocidade lê `var(20)` (seção 8) e a anim sai no cabeçalho, `anim = ifelse(var(20) > 0, 10020, 20)` |
| 40-47, 52 | pulo, pouso | A | `pulo` 0-7 + meio | `CNS_PULOS`; `DESENHOS_NO_AR = pulo 1-6, ar_* 0-7` |
| 100 | correr | S | `corrida` 0-7 + meio (8 + 8×3 = 32 desenhos), loop | estado próprio, velocidade por `var(20)`, `anim = ifelse(var(20) > 0, 10100, 100)` |
| 105 | passo para trás | A | `recuo` 0-7 | estado próprio, invencível nos 6 primeiros ticks como hoje; desperto `d_recuo` (10105) |
| 120-132 | guarda em pé | S | `defesa` 0-7 (entra 0-2, segura 3-5, sai 6-7) | 7.1: 6-8 desenhos |
| 131, 141, 152 | guarda agachada | C | `defesa_baixa` 0-7 (idem) | |
| 170 | derrota por tempo (sirene) | S | `derrota_sirene` 3-7 (ele está em pé, então pula os quadros deitado) → 171 | o 170 é a derrota por **tempo**; quem perde por nocaute fica no 5150 e nunca passa por aqui |
| 171 | fuga da sirene | S | `derrota_sirene` 0-7 + meio, depois `corrida` com flip H no AIR (desenhada para a direita, tocada para trás) | chamado pelo `[Statedef -2]` com `trigger1 = !Alive && StateNo = 5150 && RoundState >= 3` e uns 30 ticks deitado; `PlaySnd` sirene no tick 0; `PosAdd` para trás até sair da tela, **sem** `Turn` (os quadros 5-8 da folha já correm para a esquerda). Conferir na sandbox que o motor aceita o `ChangeState` com `!Alive` e que o round não corta a fuga |
| 180/181 | vitória | S | `vitoria` 0-7 + meio (≥ 30 desenhos, até 2 ticks cada; 7 segura) | 181 sorteia com `d_vitoria` se `var(20) > 0`; `PlaySnd` "EU SOU GOSTOSO!" (seção 7, sons reservados) |
| 191 | intro | S | `intro` 0-7 + meio (≥ 30 desenhos, até 2 ticks cada) | |
| 195 | provocação (c) | S | `provoca` 0-7 (2-5 em loop) | manter o "Tira barra" de hoje; desperto usa `d_dedo`; `PlaySnd` "Australopiteco mentiroso!" |
| 260 / 650 / 720 | afastar em pé / no ar / na defesa | S/A/S | `chute_lateral` / `ar_chute` / `defesa`+`chute_lateral` | herdado do sistema |
| 700 / 705 | rolar para a frente / para trás | S | `rolada_tatame` 1-5 | x + a, como hoje |
| 760/761/762 | parry | S | `defesa` 1-3 / `guarda_aco` 3-4 / (vítima) | → + c |
| 5000-5300 | tomar golpe, cair, levantar | S/C/A | `apanha` 0-6, `queda` 0-7, `levanta` 0-7 + meio (levantar é movimento contínuo: ≥ 16) | anims da faixa do common; molde em `gp:1354-1395`. `apanha` e `queda` ficam com 7-8 desenhos, abaixo dos 10-20 da 7.1: dúvida para o Breno (seção Revisão) |

### 3.2 Normais (16) e kombos (4)

Windup em ticks antes do primeiro tick ativo; base / Diabo.

| Nº | Nome | Tipo | Folha / quadros | Windup | Dano | Hitstop | Clsn1 | Guarda | Cancela |
|---|---|---|---|---|---|---|---|---|---|
| 200 | x jab | S | `soco` 0-2, C3, 4-7 | 3 | 22 | 7,7 | 16,-92,50,-80 | MA | C, K, E, S |
| 210 | y soco reto | S | `soco_reto` 0-3, C4, 5-7 | 7 | 55 | 11,11 | 18,-94,58,-80 | MA | C, K, E/hit, S/hit |
| 230 | a chute baixo | S | `chute_baixo` 0-2, C3, 4-7 | 4 | 25 | 7,7 | 14,-30,54,-12 | MA | C, K, E, S |
| 240 | b chute lateral | S | `chute_lateral` 0-3, C4, 5-7 | 8 | 60 | 11,11 | 20,-80,68,-62 | MA | C, K, E/hit, S/hit |
| 400 | ↓x jab baixo | C | `baixo_soco` 0-2, C3, 4-7 | 3 | 20 | 7,7 | 14,-56,46,-44 | L | K, E, S |
| 410 | ↓y joelhada (antiaéreo) | C→S | `joelhada_baixo` 0-3, C4, 5-7 | 7 | 58 | 11,11 | 6,-108,34,-70 | MA | E/hit, S/hit; `NotHitBy A` do tick 3 ao 8 |
| 430 | ↓a chute na canela | C | `chute_canela` 0-2, C3, 4-7 | 4 | 22 | 7,7 | 14,-14,56,0 | L | K, E, S |
| 440 | ↓b rasteira | C | `rasteira_arco` 0-3, C4, 5-7 | 8 | 55 | 11,11 | 10,-14,70,0 | L | derruba (`fall = 1`, `heavy-landing`) |
| 600 | ar x martelo | A | `ar_soco` 0-3, C4, 5-7 | 3 | 25 | 7,7 | 14,-70,44,-46 | HA | |
| 601 | ar y cotovelo descendo | A | `ar_cotovelo` 0-3, C4, 5-7 | 7 | 50 | 11,11 | 10,-60,40,-30 | HA | |
| 610 | ar a joelhada | A | `ar_joelho` 0-3, C4, 5-7 | 4 | 28 | 7,7 | 10,-66,40,-44 | HA | |
| 611 | ar b chute duplo (cross-up) | A | `ar_chute_duplo` 0-1, C2, 3, C4, 5-7 | 7 | 30+30 | 11,11 | -10,-40,46,-6 (cobre atrás do eixo até -10 para o cross-up) | HA | 2 HitDefs |
| 216 | → + y Cotovelo de Faixa | S | `cotovelo_faixa` 0-3, C4, 5-7 | 7 | 60 | 11,11 | 18,-88,52,-68 | MA | E/hit, S/hit |
| 246 | → + b Machado Curto (por cima) | S | `machado_curto` 0-3, C4, 5-7 | 12 | 55 | 11,11 | 16,-112,48,-56 (o fundo desce até -56 para pegar o agachado, cuja Clsn2 começa em -70; o calcanhar do quadro de contato tem de descer até lá) | **HA** | K |
| 201 | ← + x Cutucão de longe | S | `cutucao_recuo` 0-2, C3, 4-7 | 5 | 30 | 7,7 | 26,-66,70,-54 | MA | K |
| 231 | ← + a coice para trás | S | `coice` 0-2, C3, 4-7 | 6 | 50 | 11,11 | atrás: -70,-66,-20,-46 | MA | |
| 340/341 | Bom Dia, Vizinho (→b, **a**, **b**) | S | `chute_baixo` / `chute_lateral` | 4 / 8 | 30 / 65 | 8,8 / 12,12 | como 230/240 | MA | 341 derruba |
| 342/343 | Rasteira de Calçada (x, **↓a**, **b**) | C/S | `chute_canela` / `chute_lateral` | 4 / 8 | 28 / 65 | 8,8 / 12,12 | como 430/240 | L / MA | 343 derruba |
| 344/345 | Sai Daqui (←x, **y**, **→y**) | S | `soco_reto` / `cotovelo_faixa` | 7 / 8 | 50 / 70 | 11,11 / 12,12 | como 210/216 | MA | 345 empurra forte (`ground.velocity = -9`) |
| 346/347 | Sobe, Mentiroso (a, **b**, **↓y**) | S/C | `chute_lateral` / `joelhada_baixo` | 7 / 8 | 50 / 70 | 11,11 / 12,12 | como 240/410 | MA | 347 lança (`ground.velocity = -2,-8`, `fall = 1`) |

**Efeitos dos normais e kombos (8.1):** `hit-spark` nos fracos (200, 230, 400, 430, 600, 610, 201, 340, 342),
`blunt-hit` nos fortes, **`uppercut`** no antiaéreo 410, **`heavy-landing`** na queda de quem derruba (440, 341, 343,
347), poeira de `blunt-hit`/`ground-slam` recolorida **mais uma lasca pequena de `fx_lasca`** no contato dos chutes
fortes (240, 440 e os finalizadores de chute da 3.3/3.6), que é o "poeira e lasca de asfalto" da ficha.

**Mais rápido do jogo, sem furar a 8.3:** os fracos ficam no piso (windup 3-4, pausetime 7) e o que muda é a
recuperação curta (RITMO 1.5 do gp na recuperação, sem esticar o preparo) e o andar/correr.

### 3.3 Correntes (3 golpes + finalizador)

Cada passo só sai com `movecontact` do anterior; o finalizador só com os 3 acertos (`var(10) >= 3`, `var(6)` = passo,
molde do Pengaró). 1º e 2º cancelam em E/S; o 3º só `/hit`; o finalizador derruba e não cancela na base.

| Nº | Nome | Folha / quadros | Windup | Dano | Hitstop | Clsn1 | Efeito |
|---|---|---|---|---|---|---|---|
| 301 | x: jab duplo | `jab_duplo` 1, C2, 3-4, C5, 6-7 | 3 | 12+12 | 7,7 | 16,-94,52,-82 | hit-spark |
| 302 | x: Cutucão Sacana | `cutucao` 0-3, C4, 5-7 | 4 | 30 | 8,8 | 18,-70,52,-56 | hit-spark |
| 303 | x: **Tá Achando Ruim?** | `tapa_costas` 0-3, C4, 5-7 | 10 | 70 | 14,14 | 18,-96,62,-78 | crit-hit, EnvShake, `fall = 1`, `heavy-landing` |
| 311 | y: cruzado | `cruzado` 0-3, C4, 5-7 | 7 | 50 | 11,11 | 16,-96,52,-80 | blunt-hit |
| 312 | y: cotovelada descendo | `cotovelada` 0-3, C4, 5-7 | 7 | 55 | 11,11 | 14,-92,48,-70 | blunt-hit |
| 313 | y: **Calçada Levantada** | `calcada_levantada` 0-3, C4, 5-7 | 11 | 80 | 14,14 | 20,-24,66,0 (+ explod de asfalto) | crit-hit + ground-slam, lança `-2,-8` com `fall = 1`, `heavy-landing`, EnvShake |
| 321 | a: chute na cintura | `chute` 1-3, C4, 5-7 | 4 | 30 | 8,8 | 18,-66,62,-50 | hit-spark |
| 322 | a: chute alto sem descer o pé | `chute_alto_rajada` 0, C1, 2, 7 | 5 | 35 | 8,8 | 18,-106,64,-88 | hit-spark |
| 323 | a: **Tesoura de Bairro** | `tesoura` 0-4, C5, 6-7 (giro de 540° **no chão**, pé de apoio fixo: o `animar_folha` cola a base de toda figura no chão e o 323 é tipo S, então nada de desenho no ar) | 12 | 80 | 14,14 | 10,-110,66,-80 | crit-hit, EnvShake, `fall = 1`, `heavy-landing`, poeira + `fx_lasca` |
| 331 | b: chute giratório | `chute_giratorio` 0-3, C4, 5-7 | 8 | 60 | 11,11 | 20,-70,70,-52 | blunt-hit |
| 332 | b: chute de gancho | `chute_gancho` 0-3, C4, 5-7 | 8 | 60 | 11,11 | 14,-112,58,-92 | blunt-hit |
| 333 | b: **Machado de Dojô** | `machado` 0-3, C4, 5-7 | 13 | 85 | 14,14 | 14,-118,52,-80 | crit-hit, quica (`fall.yvelocity`, `ground-slam`), `heavy-landing`, EnvShake, `fx_lasca` |

Os chutes fortes 331 e 332 também soltam a poeira recolorida com uma lasca pequena de `fx_lasca` no contato.

### 3.4 Agarrões (3) e vítimas

Todos com `attr = S, NT`, `p2getp1state = 1`, sem defesa, escape com y ou b nos 6 primeiros ticks (molde do
`cns_agarrao_whisky` do gp), exigem `ctrl` (não disparam no meio do kombo Sai Daqui) e têm prioridade sobre o normal
colado (vêm antes no `-1`). Lutador e vítima casados quadro a quadro: 30-50 desenhos (7.1) com o `meio`.

| Nº | Nome | Entrada | hitflag | Folha | Dano | Vítima (anim no P2, `ChangeAnim2`) |
|---|---|---|---|---|---|---|
| 800 → 810 | Abraço de Quebrada | colado (`p2bodydist x < 8`), → ou ← + y | `H-` | `agarrao_abraco` 0-1 / 2-7 | 120 | 820 (segura), 821 (cai) |
| 840 → 841 | Puxa a Perna | colado, ↓ + y, P2 agachado | `L-` | `agarrao_perna` 0-2 / 3-7 | 100, derruba sentado | 845/846 |
| 830 → 831 | Cutucão Sacana (lore) | `~B,F,y`, dist 8 | `M-` | `agarrao_cutucao` 0-1 / 2-7 | 140 (3 cutucadas + soltura) | 832 (preso rindo), 833 (cai tonto) |

**As anims de vítima que o Hazak põe no oponente** só podem usar números de `SPRITES_VITIMA` (`gp:235`), porque o
`ChangeAnim2` desenha com o SFF do oponente. Ele reusa os 28 números avulsos de `SPRITES_VITIMA` (`gp:235-239`: 48,
49, 50 e alguns dentro de 382-394, 871-881 e 890-910, não as faixas inteiras), escolhidos pela pose que cada um tem
nos outros lutadores; nenhum número novo entra, para não obrigar a gerar de novo os outros três. **O verificador não
pega isso hoje:** `verificar_pengaro.py:237-244` só confere as ações `gp.ACOES_VITIMA = (5001, 5030)`, e as anims do
Hazak no P2 (820/821, 832/833, 845/846, 3409) passariam sem erro mesmo com sprite fora da lista (o oponente some).
O verificador passa a conferir, em cada `.air`, toda ação que o `.cns` do mesmo lutador põe no P2 por `ChangeAnim2`.

**Efeitos (8.1):** `heavy-landing` na queda de 810, 831 e 841 (e na do Suborno, 3408).

**O furo do Hazak arremessado pelos outros:** o `.sff` dele precisa ter os 28 números com a pose certa. O gerador lê as
ações 5001/5030 e as de vítima de `chars/{pengaro,gutto,raiclaven}/*.air`, descobre que pose cada grupo representa
naquela ordem (segurado, de ponta-cabeça, girando, impacto, sentado, deitado) e grava ali o desenho correspondente de
`vitima_agarrado` / `vitima_arremessado` / `apanha` / `queda`, com `s.add(nome, img, grupo=g, indice=0)`. Esse mapa
fica numa tabela `POSE_DA_VITIMA = {382: ("vitima_agarrado", 1), ...}` escrita uma vez à mão depois de olhar as tiras
do `video_golpe --sff-de`. Até as folhas `vitima_*` chegarem, todos os 28 recebem `apanha/03` e `queda/00`, que já
tira o "some". O Diabo usa os mesmos números (é arremessado de gi; aceito e anotado).

### 3.5 Especiais (8) e projéteis

Todos cardeais, 2 toques + botão, `time = 16`. x/a = fraco, y/b = forte. Corpo 20-40 desenhos (meta 40-60) com o
`meio`.

| Nº | Nome | Cmd | Tipo | Folha / quadros | Windup x/y | Dano x/y | Hitstop | Notas |
|---|---|---|---|---|---|---|---|---|
| 1000/1001 | Punho de Concreto | `df_x`/`df_y` | S | `punho_chao` 0-3, C4, 5-7 | 12 / 10 | 60 / 70 | 11,11 | **Projectile** 1005 (voo) / 1006 (acerto), `guardflag = L` (defende agachado), rente ao chão `offset 40,-6`; x vel 3.0 alcance 220 px (`projremovetime`), y vel 6.0 até sair da tela |
| 1600/1601 | Estatueta Dourada | `fb_x`/`fb_y` | S | `estatueta_arremesso` 0-3, C4, 5-7 | 14 / 14 | 70 / 80 | 11,11 | **Projectile** 1605/1606 em arco: x `velocity 2.5,-6 accel 0,0.35` (cai perto), y `4.5,-6.5` (cai longe); some no chão (`projheightbound`) |
| 1200/1201 | Ascensão de Faixa | `fd_x`/`fd_y` | S | `ascensao` 0-3, C4, 5-7 | 4 / 5 | 80 / 110 | 12,12 / 14,14 | pés no chão; x: `NotHitBy A` ticks 1-6; y: `NotHitBy SCA` do 1 ao fim do ativo, recuperação 28; efeito `uppercut`; lança `-2,-7` |
| 1300/1301 | Giro de Garagem | `df_a`/`df_b` | S | `giro_garagem` 0-3, C4, 5-7 (o contato é o quadro 5 do MOTION, arquivo `04`) | 10 / 12 | 65 / 85 | 11,11 / 12,12 | avanço de meia tela: `VelSet x` 5 / 7; b `fall = 1`. Desligado com `var(20) > 0` |
| 1400/1401 | Corte de Base | `db_a`/`db_b` | C | `rasteira` 1-2, C3-5, 6-7 | 9 / 11 | 55 / 75 | 11,11 | `guardflag = L`; desliza `VelSet 4 / 6`; b derruba. Desligado no Despertar |
| 1700/1701 | Rolada de Tatame | `bf_a`/`bf_b` | S | `rolada_tatame` 0-7 (+ `coice` 2-4 no b) | - / - | 0 / 50 | 11,11 | ir para trás (3.F): `PosAdd` pelo P2 e `Turn` do motor no tick em que cruza (molde `gp:2459-2465`); **todo quadro da folha é desenhado virado para a direita**, porque depois do `Turn` um desenho feito para a esquerda aparece de costas para o P2 (e no canto, sem `Turn`, também); no canto para na frente sem atravessar (`frontedgedist`); recuperação 14 visível; b chuta ao chegar |
| 1500/1501 | Pega Bolado | `bd_a`/`bd_b` | S→A | `corrida` (arranque 6 / 14 ticks) + `voadora` 1-3, C4, 5-7 | 14 / 18 | 70 / 100 | 12,12 / 14,14 | a curta; b atravessa a tela e derruba; defendido: recuperação 30 (erra feio) |
| 1100/1101 | Guarda de Aço | `db_x`/`db_y` | S | `guarda_aco` 0-3 (parada) / 4-7 (resposta 1102/1103) | 2 / 2 | 60 / 70 | 11,11 | `ReversalDef`: x `S,NA,SA`; **y `SCA,NA,SA`** (pega golpe baixo); resposta com chute |

**Um projétil próprio por vez (regra E):** todo especial que solta projétil (Punho, Estatueta, Chapéu, Nota Falsa)
tem `triggerall = NumProj = 0`. A armadilha da Nota Falsa é um `Projectile` de velocidade zero (`projremovetime`
120) e ocupa a vaga até sumir. A Estatueta desperta parada no chão **não** sai de um `Projectile` só: o
`projheightbound` remove o projétil ao tocar o chão e o `Projectile` não tem gancho de pouso. Como a trajetória é
balística, o tick de pouso `T` sai da conta (offset y, vy, accel); o `[Statedef -2]` conta com um var (o 11600 acaba
antes de `T`) e em `T` faz uma de duas coisas, a escolher na sandbox: `ModifyProjectile` com `velocity = 0,0`,
`accel = 0,0`, `removetime = 90` (controlador do IKEMEN; não confirmei que a versão instalada tem), ou, com o
primeiro já removido pelo chão, um segundo `Projectile` parado no x do pouso por 90 ticks. Nos dois casos fica um
projétil por vez. Só o super passa disso.

Arte dos projéteis e efeitos (regra 8): `fx_lasca` (de `obj_lasca`), `fx_estatueta`, `fx_chapeu`, `fx_maco`,
`fx_papel` e `fx_brasa` são efeitos novos no pixelfx (`new.mjs`, `render.mjs`, `check.mjs`, PNG + JSON em
`assets/efeitos/`, linha no `LEIA-ME.md`) e entram por `carregar_faiscas`, andando de 2 em 2 ticks. Lasca em brasa e a
rampa laranja-ouro do Diabo são `palette` do mesmo efeito. Poeira dos chutes fortes = `blunt-hit`/`ground-slam`
recolorido **mais uma lasca pequena de `fx_lasca`** (ficha: "poeira e lasca de asfalto"). O brilho dourado da
Estatueta vem desenhado no próprio `fx_estatueta` (realces duros que mudam de quadro), sem `PalFX`. Rastro de velocidade da corrida e da voadora: AfterImage de 2 ticks.

### 3.6 Supers (2)

Invencíveis do tick 1 ao fim da superpausa (`NotHitBy SCA`), 3 toques + botão, `time = 22`, `crit-hit` e EnvShake só
no golpe final, superpausa com `pose_super` e `charge-up`. Super 40-80 desenhos: só com as folhas a conta não fecha
(3000 ≈ 8 + 6 + 6 + 5 = 25; 3200 ≈ 23; 3100 ≈ 24), então a `pose_super` e a `d_chuva_abre` (o começo da super, que
anda de 2 em 2 ticks) entram com meio até ~24 desenhos, e os trechos de golpe repetem as poses seguradas da 7: cada
super passa de 40.

| Nº | Nome | Cmd | Custo | Folhas | Dano | Notas |
|---|---|---|---|---|---|---|
| 3000 (+3001-3003) | Faixa no Asfalto | `bfd_a`/`bfd_b` (o "golaco" do robô) | 1000 | `pose_super` → `chute_alto_rajada` 1-6 (3 acertos) → `sobe_chutando` 1-6 (3 acertos, no ar) → `machado` 5-7 (pouso) | 6 x 25 + 90 = 240 | combo travado por `TargetBind` depois do 1º acerto; erra se o 1º for defendido. A subida é física de verdade (o `animar_folha` cola a arte no chão): 3002 com `StateTypeSet statetype = A, physics = A`, `VelSet y ≈ -6` e gravidade; 3003 entra no pouso (`Pos Y >= 0` → `ChangeState`) com o `machado` 5-7; Clsn1 recalculadas sobre a arte em altura de jogo. Contato com `fx_lasca` + poeira no machado final |
| 3200 (+3201-3204) | Rapidinho da Quebrada | `bfd_x`/`bfd_y` | 2000 | `pose_super` → `passagem_rapida` x4 (atravessa a tela, `Turn` em cada borda) → `voadora` | 4 x 45 + 160 = 340 | P2 em `custom state` só a partir do 1º acerto; passa para o lado com `PosAdd`, nunca de costas |

### 3.7 Despertar e kit do Diabo Loiro

| Nº | Nome | Cmd | Tipo | Folha | Dano | Notas |
|---|---|---|---|---|---|---|
| 2000 | Despertar Diabo Loiro | `despertar` (x + y), `power >= powermax` | S | `despertar_pedido` 0-7 → (patroa) → `despertar_virada` 0-7 | 0 | seção 7 |
| 3410-3412 | corrente y: maletadas | y, y, y | S | `d_maletada_lado` / `d_maletada_volta` / `d_maletada_cima`, cada uma 0-3, C4, 5-7 | 45 / 50 / 55 | windup 9/9/9 (forte do Diabo, seção 8); `blunt-hit`; empurrão do Diabo (abaixo) |
| 3413 | **Negócio Fechado** | y (3 acertos) | S | `d_negocio_fechado` 0-3, C4, 5-7 | 90 | derruba, crit-hit, EnvShake; **cancela em E e S** (mudança de cancelamento do Despertar) |
| 3420-3422 | corrente b: sapato canela, barriga, coice | b, b, b | S | `d_sapato_canela` 0-3, C4, 5-7 / `d_sapato_barriga` 0-3, C4, 5-7 / `d_coice_costas` C4 | 40 / 50 / 60 | windup 9/9/9; `blunt-hit` + poeira e `fx_lasca`; empurrão e alcance do Diabo (abaixo) |
| 3423 | **Pisão de Chefe** | b (3 acertos) | S | `d_pisao_chefe` 0-3, C4, 5-7 | 95 | `fall = 1` (o coice do 3422 já tira o equilíbrio; o pisão bate e derruba, `heavy-landing`); cancela em E e S |
| 3431 | x tapa com anel | x | S | `d_tapa_anel` C3 | 30 | windup 5 (o fraco fica mais lento) |
| 3430 | ↓y maleta subindo (antiaéreo) | ↓ + y | C→S | `d_maleta_sobe` C4 | 65 | Clsn1 mais alta e larga que o 410; `uppercut` |
| 3432 | → + b chapelada (por cima) | → + b | S | `d_chapelada` C4 | 60 | `HA`; Clsn1 com fundo em -56 ou mais baixo, como o 246, para pegar o agachado |
| 3433 | ← + x dedo balançando | ← + x | S | `d_dedo` 1-5 | 0 | `ReversalDef` só contra projétil fraco (`reversal.attr = SCA,NP`, dano baixo) |
| 3435 | b no ar pisão | b no ar | A | `d_pisao_ar` C4 | 55 | |
| 3434 | ↓a bico de sapato | ↓ + a | C | `d_bico_sapato` C3 | 30 | `L` |
| 348/349 | Sociedade Fechada (x, **→b**, **y**) | | S | `d_chapelada` / `d_maletada_lado` C4 | 60 / 70 | 349 derruba, `heavy-landing` |
| 3400/3401 | Chapéu Bumerangue | `df_a`/`df_b` | S | `d_chapeu_arremesso` 0-4 / 6-7 | 50 / 60 | Projectile `fx_chapeu`: `velocity 6 / 7.5`, `accel -0.22` (vai e volta); some ao voltar (`projremovetime` = 2·v/a). Leitura afastada do chapéu de MK: arremesso por baixo, de lado, rasante na cintura, e o chapéu cai de volta na cabeça dele (risco anotado para o Breno) |
| 3402/3403 | Maleta Giratória | `fb_a`/`fb_b` | S | `d_maleta_giro` C3 / C5 | 3 x 25 / 4 x 25 | avanço `VelSet 3.5 / 5` |
| 3404/3405 | Nota Falsa | `db_x`/`db_y` | C | `d_nota_falsa` 0-7 | 70 / 80 | Projectile parado `fx_maco` a 40 / 90 px; estoura em `fx_papel` |
| 3406/3407 → 3408, vítima 3409 | Suborno | `db_a`/`db_b` | S | `d_suborno` 0-7 | 110 | agarrão de comando, dist 30 / 45, escape y/b; vítima em `apanha`-equivalente de `SPRITES_VITIMA` |
| 3100 | Chuva de Dinheiro | `bfd_x`/`bfd_y` com `var(20) > 0` | S | `d_chuva_abre` (+ meio) → `d_maletada_lado`/`_volta`/`_cima` → `d_estatueta_gigante` | 300 | 1000 de barra; não encerra o Despertar; `fx_papel` cobrindo a tela; `var(37) = 1` do começo ao fim |
| 11000/11001 | Punho de Concreto desperto | `df_x`/`df_y` | S | `d_punho_anel` | 65 / 75 | lasca em brasa (`fx_lasca` palette brasa), velocidade 2.2 / 4.5 |
| 11600/11601 | Estatueta desperta | `fb_x`/`fb_y` | S | `d_estatueta` | 80 / 90 | projétil maior; ao tocar o chão vira obstáculo (projétil parado 90 ticks) |
| 11500/11501 | Pega Bolado desperto | `bd_a`/`bd_b` | S→A | `d_corrida` + `d_voadora_sapato` | 80 / 110 | mais lento, quica (`fall.yvelocity -4`) |
| 11700/11701 | Rolada desperta | `bf_a`/`bf_b` | S | `d_fumaca` (no 11701, + `d_coice` 2-4 depois de reaparecer, como o b da base) | 0 / 50 | some na fumaça (`fx_brasa`) e reaparece atrás, sem rolar; todo quadro desenhado virado para a direita (o `Turn` é do motor) |

**Peso do Diabo (ficha: "alcance e peso", "chutes de sapato social empurram mais"):** maletadas, chutes de sapato
(3410-3423, 3434, 3435) e as +10000 de chute (10230, 10231, 10440) empurram mais que o golpe base equivalente (por
exemplo `ground.velocity` -6 contra -4) e ganham +6 a +10 px de alcance na Clsn1. O preparo mais lento está na seção 8.

Os especiais da base que ficam mudam de pose e função (regra 4) e os que não mudam **saem** no Despertar: Giro de
Garagem, Corte de Base, Guarda de Aço e Ascensão de Faixa; o Rapidinho dá lugar à Chuva (seção 5, item 4). Os
comandos que eles liberam vão para os exclusivos (mesmo padrão que a ficha usou no Chapéu). **Proposta que a ficha não
manda e precisa do sim do Breno** (seção 11): também saem no Despertar as correntes x e a, o super Faixa no Asfalto e
os 4 kombos da base (as aberturas deles viram outros golpes: → + b é a chapelada, ← + x o dedo, x o tapa com anel, b
abre a corrente de sapato); fica só a Sociedade Fechada. A regra 4 só exige 2 correntes novas e deixa reaproveitar a
base, então a alternativa é manter as correntes x/a e o Faixa no Asfalto com +10000, o que custa ~9 folhas `d_` a
mais (`d_jab_duplo`, `d_cutucao`, `d_tapa_costas`, `d_chute`, `d_chute_alto_rajada`, `d_tesoura`, `d_pose_super`,
`d_sobe_chutando`, `d_machado`) ou o quebra-galho de paleta até elas existirem.

No Despertar ganham +10000 com as folhas `d_` do lote 7: as normais que continuam (a em pé 10230, ↓x 10400, ↓b
10440, ar x/y/a 10600/10601/10610, →y 10216, ←a 10231), o passo para trás 10105 (`d_recuo`), os agarrões
10800/10810, 10830/10831, 10840/10841 (`d_agarrao_*`) e o afastar em pé e na defesa 10260/10720 (`d_chute_lateral`).
Reusam folha `d_` que já existe: o rolamento 700/705 (`d_fumaca`, o terno não rola), o parry 760 (`d_defesa`), o
afastar no ar 650 (`d_pisao_ar`) e o virar 5/6 (`d_vira`, lote 5). y e b em pé não têm +10000: abrem as correntes
3410 e 3420.

## 4. Comandos do `.cmd`

`command.time = 15`, `command.buffer.time = 3` como o Pengaró. Nomes pelo **toque**, não pelo golpe, porque o mesmo
toque solta golpes diferentes conforme `var(20)`; o robô lê o nome por tabela (seção 10). A linha `[Statedef -1]`
continua seguida de linha em branco (o robô injeta ali).

| Nome | Comando MUGEN | time | Base | Despertar |
|---|---|---|---|---|
| `despertar` | `x+y` | 3 | 2000 se `power >= powermax` | - |
| `bfd_x` / `bfd_y` | `~B, F, D, x` / `y` | 22 | 3200 (2000 de barra) | 3100 (1000) |
| `bfd_a` / `bfd_b` | `~B, F, D, a` / `b` | 22 | 3000 (1000) | - (proposta: Breno confirma; senão 3000 com +10000) |
| `df_x` / `df_y` | `~D, F, x` / `y` | 16 | 1000/1001 | 11000/11001 |
| `df_a` / `df_b` | `~D, F, a` / `b` | 16 | 1300/1301 | 3400/3401 |
| `fb_x` / `fb_y` | `~F, B, x` / `y` | 16 | 1600/1601 | 11600/11601 |
| `fb_a` / `fb_b` | `~F, B, a` / `b` | 16 | - | 3402/3403 |
| `fd_x` / `fd_y` | `~F, D, x` / `y` | 16 | 1200/1201 | - |
| `db_x` / `db_y` | `~D, B, x` / `y` | 16 | 1100/1101 | 3404/3405 |
| `db_a` / `db_b` | `~D, B, a` / `b` | 16 | 1400/1401 | 3406/3407 |
| `bf_a` / `bf_b` | `~B, F, a` / `b` | 16 | 1700/1701 | 11700/11701 |
| `bd_a` / `bd_b` | `~B, D, a` / `b` | 16 | 1500/1501 | 11500/11501 |
| `bf_y` | `~B, F, y` | 16 | 830 (colado) | 830 |
| `agarrao_y` | `/F, y` ou `/B, y` com `p2bodydist x < 8` | 1 | 800 | 800 |
| `agarrao_baixo` | `/D, y` com P2 agachado e colado | 1 | 840 | 840 |
| `golpe_216` / `golpe_246` / `golpe_201` / `golpe_231` | `/F, y` · `/F, b` · `/B, x` · `/B, a` | 1 | 216/246/201/231 | 10216 / 3432 / 3433 / 10231 |
| `FF` / `BB` | `F, F` / `B, B` | 10 | 100 / 105 | |
| `rolar` / `recovery` | `x+a` | 1 | 700/705 | |
| `afastar` | `y+b` | 1 | 260/650/720 | |
| `parry` | `/F, c` | 1 | 760 | |
| `superpulo` | `$D, $U` | 10 | 40 | |
| `x y a b c s`, `holdfwd/back/up/down` | padrão | 1 | | |

**Ordem no `[Statedef -1]` (5.2):** despertar → `bfd_*` → especiais de 2 toques → `bf_y` (lore) → `agarrao_baixo` →
`agarrao_y` → kombos → continuação de corrente → direcionais → normais. Prefixos aceitos e anotados: `bf_a/b` e `bd_a`
dentro de `bfd_a/b`, `bf_y` dentro de `bfd_y`; sem barra, o comando de super solta a Rolada ou o agarrão de lore, como a
5.2 permite. O `x+a+y` de hoje sai (ele colidia com o rolamento x + a), e o agarrão deixa de sair com b.

## 5. Conflitos com as regras e como ficaram

| # | Conflito | Solução neste projeto |
|---|---|---|
| 1 | Nota Falsa e Suborno em ↓↑ batem no superpulo `$D,$U` e repetiriam comando | Nota Falsa = `~D,B` x/y e Suborno = `~D,B` a/b, os toques que a Guarda de Aço e o Corte de Base liberam ao sair no Despertar. **Muda a ficha**: Breno confirma |
| 2 | Ascensão, Corte de Base e Guarda de Aço continuariam iguais no Despertar (regra 4) | saem no Despertar (alternativa da própria regra); os quatro que ficam têm folha e função novas |
| 3 | Mais de 1 projétil próprio (armadilha, obstáculo, chapéu, lasca) | todos são `Projectile` e todos exigem `NumProj = 0`; armadilha e obstáculo ocupam a vaga até sumir |
| 4 | Chuva de Dinheiro com x + y (super é 3 toques + **um** botão) e colisão com o Super 2 | Chuva = `~B,F,D` + x ou y só no Despertar, no lugar do Rapidinho (Proposta A, literal à regra). Custa 1000 e não encurta o Despertar (o tempo dele é `var(20)`, não a barra). **Muda a ficha** |
| 5 | Prefixos dos supers | supers acima no `-1`, agarrões com `ctrl` |
| 6 | Nomes repetidos e B.6 (pose nova no 2º, 3º e finalizador) | → + b = **Machado Curto** (`machado_curto`); finalizador b = Machado de Dojô completo (`machado`); finalizador y = **Calçada Levantada** (`calcada_levantada`, pose ajoelhada, diferente do `punho_chao`); ← + x = Cutucão de longe (`cutucao_recuo`) e 3º da corrente x = Cutucão Sacana colado (`cutucao`); agarrão de lore mantém o nome da ficha com folha própria (`agarrao_cutucao`). Breno pode renomear o agarrão |
| 7 | Negócio Fechado e Pisão de Chefe precisam derrubar | os dois com `fall = 1` |
| 8 | Cancelamento no Despertar | finalizadores despertos cancelam em E e S (B.4 permite); correntes x/a, Faixa no Asfalto e os 4 kombos da base saem (**não está na ficha**: proposta para o Breno, seção 3.7) |
| 9 | Projétil e efeito vêm do pixelfx | folhas `obj_` são referência; os efeitos `fx_*` nascem no pixelfx |
| 10 | "O mais rápido" contra os pisos da 8.3 | windup e pausetime no piso; a velocidade vem do andar/correr e da recuperação; loops de 48 (andar) e 32 (correr) desenhos para o pé não deslizar |
| 11 | Vítima no número errado | elenco: 800/810/820/821, 830-833, 840/841/845/846 (seção 2) |
| 12 | Numeração da 5.1 contra o elenco e o common (5000-5999) | convenção do elenco; decisão do Breno |
| 13 | `EnvShake` nos fortes (estudo antigo, item 11) | só finalizador e golpe final de super |
| 14 | Despertar em 8 desenhos (mínimo 40) | ~112 desenhos (`despertar_pedido` + `despertar_virada` com meio) + patroa como Helper |
| 15 | Conteúdo | patroa morena de roupa casual neutra (camiseta, jeans, tênis; sem toalha nem chinelo, que eram marca de serviço doméstico acrescentada), sem piada; estatueta atarracada em base de karatê sobre pedra, sem silhueta de troféu real (a figura lisa de pé sobre base quadrada lembrava o Oscar); chapéu sem a leitura de bumerangue de MK; terno sem logo nem caricatura; derrota sem viatura nem policial; notas sem moeda. "Australopiteco mentiroso!" e "Rapidinho" ficam para o Breno confirmar |

## 6. Paletas (15 cores + transparente)

Forma normal: a tabela de [`hazaki.md`](hazaki.md#a-paleta-fixa-15-cores--transparente), sem mudança.

Diabo Loiro de terno (substitui a paleta `d_` de gi): 1 contorno `#1c1832`; 2-6 pele (iguais à normal); 7 terno escuro
e chapéu `#2b2440`; 8 terno médio e risca `#47436a`; 9 brasa, gravata, faixa do chapéu, ouro do anel e do fecho
`#ffb02e`; 10 cabelo luz `#f2d27a`; 11 cabelo sombra `#c98a34`; 12 chifre, maleta e sapato `#5a3a2c`; 13 camisa
`#f4f1ea`; 14 pulseira teal `#2a9d9a`; 15 olho `#e3321e`. Papéis do `conferir_arte`: `calca_sombra` = 7.

## 7. Despertar e troca para o Diabo

**Estado 2000** (`power >= powermax`, `PowerSet 0`, `NotHitBy SCA` do começo ao fim, superpausa curta no tick 1):

1. ticks 0-55: `despertar_pedido` com meio (ele bate o pé e olha para trás). No tick ~20 (quadros 4-5) `PlaySnd` da
   fala "Ô vida, posso despertar?". No tick 20 nasce um **Helper "patroa"**
   (id 2050, `sprpriority -3`, atrás dele, `ownpal`, sem caixa, sem `HitDef`, `pausemovetime` alto): anim 2050
   (`patroa_chega_sim`, faz que sim) e 2051 (`patroa_sai`, sai da arena andando até a borda e `DestroySelf`). Os
   desenhos dela usam só as cores da paleta normal mais 4 cores próprias no fim da paleta (cabelo castanho, camiseta
   mostarda, jeans, tênis); se não couber, ela reusa pele/atadura/gi.
2. ticks 56-110: `despertar_virada` com meio; no tick 80 `var(20) = 600` (duração) e `var(37) = 1`; `charge-up`,
   `fx_brasa` e, do tick ~80 ao 110, `Explod fx_papel` (as notas de dinheiro voando que a ficha pede).

**Sons reservados:** as falas viram áudio que o Breno manda depois. O gerador reserva um número de `PlaySnd` para cada
uma, com arquivo provisório (silêncio) no `.snd`: "Ô vida, posso despertar?" (2000), "Australopiteco mentiroso!"
(195), "EU SOU GOSTOSO!" (180/181), a sirene (171), e a intro "Bora ver se aguenta o treino." (191). A tabela fica em
`hazaki_golpes.SONS`; trocar o áudio depois não mexe em estado.
3. tick 100: empurra o oponente (`HitDef` sem dano, `attr = SCA,NT`, `ground.velocity = -8`) como o Pengaró faz.
4. tick ~150: volta ao 0 desperto com controle.

**Como a arte troca:** pelo mecanismo que o Pengaró já usa. Hoje o `-2` faz `RemapSprite preset = "despertado"`
quando `var(20) > 0 && var(37) = 0` e `RemapSprite reset = 1` ao voltar (`gp:2788-2800`); o `ChangeAnim` +10000 só sai
em `Time = 0` dentro de cada estado de golpe próprio, pela função `estado()` (`gp:1839-1843`). Um `ChangeAnim` no
`-2` piscaria 1 tick de gi a cada troca de anim, porque o `-2` roda antes do estado no mesmo tick. Então:

- folhas `d_` que casam 1 para 1 com a base (mesmo número de desenhos, com o meio): o `[RemapPreset despertado]`
  mapeia cada sprite base no sprite `d_` (o `ajustar_clsn1` e o `verificar_pengaro.py:232` já tratam esse preset);
- golpes próprios com tempo ou caixa diferente no Diabo (lote 7, windup mais lento): anim `n + 10000` em
  `gp.ATAQUES_DESPERTADOS`, trocada pelo `estado()` em `Time = 0`;
- andar, correr e passo para trás (velocidade diferente): 20/100/105 são estados próprios e escolhem a anim no
  cabeçalho, `anim = ifelse(var(20) > 0, 10020, 20)`; essas três **não** seguem a regra de mesmos ticks, e a
  `d_anda`/`d_corrida` têm passada ~80% da base (2.7/3.4 e 5.6/7.2) para o pé não escorregar;
- o `-2` fica limpo dos restos do Pengaró (Juliet/9203, óculos, ressaca). Os exclusivos 34xx e o 3100 usam a folha
  `d_` direto na anim de mesmo número. Quando `var(20)` chega a 0 ou o Hazak toma KO, `fx_brasa` em fumaça e a arte volta ao gi (a
derrota é sempre de gi).

**Quebra-galho temporário** (só enquanto falta a folha `d_` de uma anim herdada, lote 7): a anim `n + 10000` usa os
sprites da base com `PalFX` brasa. É temporário pela regra 4 (recolorir é quebra-galho), e o verificador lista cada
anim nesse estado como aviso. Some sozinho quando a folha existe.

## 8. Velocidades e números

O elenco inteiro está em life 1000, defence 100, walk 2.7 / -2.2, run 5.6 / -5.2,-3.4, jump 0,-8.4.

| Constante | Hazak (base) | Diabo (por `var(20)` nos estados 20/100/105 próprios) |
|---|---|---|
| `life` | 900 | |
| `defence` | 90 | (aplica `DefenceMulSet 1.1` no Despertar: o terno aguenta mais) |
| `walk.fwd` / `walk.back` | 3.4 / -2.8 | 2.7 / -2.2 (média do elenco) |
| `run.fwd` | 7.2, 0 | 5.6, 0 |
| `run.back` (105) | -6.4, -3.6 | -5.2, -3.4 |
| `jump.neu` / `jump.fwd` / `jump.back` | 0,-8.6 / 3.0 / -2.8 | o do elenco |
| windup fraco / forte / finalizador | 3-4 / 7-8 / 10-13 | 5 / 9 / 12-14 |
| pausetime fraco / forte / finalizador / super | 7 / 11 / 14 / 16 | 8 / 12 / 14 / 16 |

O `walk`/`run` do common usa `const(velocity.*)`, que não muda com `var(20)`; por isso 20, 100 e 105 são estados
próprios no `.cns` do Hazak com `ifelse(var(20) > 0, ...)`. O pé não pode deslizar: na `anda.png` a figura tem ~340 px
e a abertura máxima dos pés ~230 px, o que dá ~74 px por passo e ~150 px por ciclo em jogo (medição de um revisor,
não refeita aqui). Com 3.4 px/tick isso pede ~48 desenhos no ciclo do `anda` (8 + 8×5, ~163 px), e com 7.2 px/tick
~32 na `corrida` (8 + 8×3, ~230 px). O `conferir_tempo`/`video_golpe` mede na arte final e o meio se ajusta.

## 9. O que dá para fazer já e o que espera folha

**Já, com as 15 folhas existentes e placeholders:**

- pipeline: `ESCALA_2172`/`FOLHAS_HAZAKI` no `animar_folha`, `apanha` no `POR_CELULA`, loop no `--arcade`,
  `PAPEIS["hazaki"]`, `paleta_arcade.json`; quantizar as 15 folhas e gerar `quadros_arcade/` (as 8 ok, mais `defesa`,
  `levanta` e `rasteira` com o retoque de pulseira);
- o gerador inteiro: `hazaki_golpes.py` com todos os números, comandos, dano, hitstop, caixas e cancelamentos; CNS,
  CMD, DEF, movelist e README; Despertar, projéteis (com faíscas existentes recoloridas como arte provisória),
  agarrões, supers, velocidades;
- os 28 desenhos de vítima com `apanha/03` e `queda/00` (fecha o "some");
- `SUBSTITUTA` em `hazaki_golpes.py`: cada folha que falta aponta para a existente mais próxima (`soco_reto`,
  `jab_duplo`, `cruzado`, `cutucao*`, `tapa_costas` → `soco`; `chute_baixo`, `chute_lateral`, `chute_*`, `tesoura`,
  `machado*`, `coice` → `chute`; `chute_canela`, `rasteira_arco` → `rasteira`; `joelhada_baixo`, `ascensao` →
  `agachado` 4-7 + `soco`; `ar_*` → `ar_chute`; `corrida`, `recuo` → `anda`; `queda` → `apanha` 6 + `levanta` 0;
  `d_*` → a base com o quebra-galho de paleta). O gerador imprime a lista de substitutas a cada execução e o
  verificador conta como aviso. A substituta some sozinha quando a pasta da folha nova existir;
- o roteiro do robô por lutador e o teste completo na sandbox com essa arte provisória.

**Depende das folhas novas:** toda a arte final (105 folhas novas, contagem em `fila_hazak.md`), a calibração das caixas (`ajustar_clsn1` sobre a arte),
os mínimos de desenho da 7.1 nos golpes que hoje usam substituta, a cena da patroa, o Diabo de terno, os efeitos
`fx_*` do pixelfx a partir das folhas `obj_`, e o `POSE_DA_VITIMA` definitivo (com `vitima_agarrado` e
`vitima_arremessado`).

## 10. Plano de teste (só sandbox)

1. **Arte**, folha por folha: `LUTADOR=hazaki python ferramentas/quantizar_folha.py <folha> --meio`, depois
   `animar_folha --arcade` e `conferir_arte.py` (R3 pele 5-15 / 21-26 / 30-40°, R4 gi 220-270° s ≥ 10%).
2. **Gerar e conferir estático:** `python ferramentas/gerar_hazaki.py`, `verificar_pengaro.py` apontado para o Hazak
   (precisa de `PERSONAGEM`/`--lutador`: conferir), `conferir_sff.py`, `conferir_tempo.py` (não lidos nesta fase: ver se
   aceitam o Hazak antes de confiar), e o aviso de `SPRITES_VITIMA` zerado.
3. **Robô** (`python ferramentas/testar_pengaro.py --lutador hazaki`, roda dentro do Windows Sandbox por padrão):
   `robo.lua` ganha uma tabela `ROTEIRO[lutador]` (comandos e estados esperados de correntes, kombos, agarrões,
   projéteis, ida para trás, Despertar, desperto e supers) escolhida pelo `--lutador`, e `testar_pengaro.py` troca a
   lista fixa `CMDS` pela do lutador. A tabela do Pengaró sai exatamente igual à de hoje (o roteiro do Pengaró tem que
   passar como antes). Para o Hazak: correntes 200→301→302→303 etc.; kombos 246→340→341, 200→342→343, 201→344→345,
   230→346→347; lore `bf_y`→831; agachado `agarrao_baixo`→841; projéteis `df_x/df_y`→1000/1001 e `fb_x/fb_y`→1600/1601
   com `numProj > 0`; segundo projétil recusado enquanto o primeiro voa; ida para trás `bf_a/bf_b`→1700/1701 no meio e
   no canto (P2 em x = 560); Despertar recusado com 2000 de barra, aceito com `powermax`, sai do 2000 em até 500 ticks
   com `var(20) > 0`, power = 0 e o oponente mais longe; desperto: `df_a`→3400, `fb_a`→3402, `db_x`→3404, `db_a`→3406,
   correntes 3410-3413 e 3420-3423, kombo 3431→348→349, `bfd_x`→3100 com `var(37) = 1`; supers `bfd_a`→3000 (1
   estoque, dano > 100) e `bfd_x`→3200 (2 estoques, dano > 150).
4. **O Hazak como P2 dos outros:** rodar o robô do Pengaró, do Gutto e do Raiclaven (`--lutador gutto` etc.), que
   usam o Hazak de boneco: estados 11/12, `holddown`, `holdfwd`, `y` escapando do agarrão.
5. **Vídeo golpe a golpe:** `python ferramentas/video_golpe.py chars/hazaki --todas` (tira de todos os ticks, borda
   vermelha onde a análise acusa), `--despertado` para as +10000, e `--sff-de` para as vítimas: as anims de vítima do
   Hazak desenhadas com o SFF do Pengaró, e as dos outros desenhadas com o SFF do Hazak (confere que ele não some).
6. **Filmar no motor:** `python ferramentas/filmar_sandbox.py --p1 hazaki --p2 pengaro --golpes "x,x,x,x,bf_a,df_y"`,
   uma filmagem por grupo (correntes, especiais, agarrões, supers, Despertar com `--despertar`), mais
   `--p1 pengaro --p2 hazaki --golpes "agarrao_whisky"` para o furo da vítima, e uma luta na IA 8.
7. **Itens do checklist da seção 9 que o robô não cobre:** caixas conferidas no editor de AIR (e o 246/3432 pegando
   agachado); combos conferidos no `ikemen-combo-finder`; treino dos **dois lados e no canto** para todo golpe que
   anda ou atravessa (Rolada, Giro, Pega Bolado, Rapidinho, agarrões), não só a Rolada; a derrota por nocaute e por
   tempo (171 e 170); licenças anotadas no README (arte gerada no ChatGPT, efeitos do pixelfx MIT); `ChangeAnim2` do
   Hazak conferido pelo verificador estendido (seção 3.4).
8. **Quem dá o aceite:** uma pessoa olhando os vídeos (o nível em que o problema é vivido), contra o checklist da seção
   9 das regras. O robô passar não prova que a tela pinta certo.

## 11. Riscos

- **Volume de arte:** 108 imagens no ChatGPT (105 novas + 3 refeitas). Se o lote 1 não convencer no estilo, parar antes de abrir o resto.
- **Consistência do Diabo:** rosto e tamanho iguais ao normal é o que mais falhou na `diabo-loiro.png` (cavanhaque,
  rosto mais velho, 115-131 px). A `d_parado` só é aprovada lado a lado com a `parado`.
- **Pulseira teal:** sumiu ou trocou de pulso em 6 das 15 folhas; conferir em toda folha antes de aceitar.
- **Tirar `hazaki=True` do `gerar_pengaro.py`** mexe no gerador dos outros três: só com os três saindo byte a byte iguais.
- **Paleta fixa no SFF** é caminho novo (`gravar_sff` aceita, mas ninguém usou assim): conferir faíscas e balões.
- **Mudanças na ficha** precisam do sim do Breno antes de virar código: comandos da Nota Falsa, do Suborno e da Chuva;
  Ascensão/Corte/Guarda saindo no Despertar; **correntes x/a, Faixa no Asfalto e os 4 kombos da base saindo no
  Despertar** (a ficha não manda; seção 3.7); numeração fora da 5.1; nomes trocados: **Calçada Levantada** (era "Punho
  de Concreto curto"), **Machado Curto** (era "Machado de Dojô (por cima)") e **Cutucão de longe** (← + x); a Tesoura
  de Bairro no chão (a ficha não diz se pula); o chapéu que cai na cabeça em vez de voltar para a mão.
- **`conferir_tempo.py`, `conferir_sff.py` e o caminho do `verificar_pengaro.py`** não foram lidos: podem não aceitar o
  Hazak sem ajuste.
- A vítima do Hazak no Despertar aparece de gi, e o Suborno não tem desenho do oponente "pegando o maço" (só a pose de
  vítima comum).

## Revisão

Revisão de 2026-11-11 (três revisores, cada apontamento conferido contra a ficha, as regras e o `gerar_pengaro.py`).

**Corrigido:** derrota no 170 (é derrota por tempo; o nocaute fica no 5150) → 170 + 171 chamado pelo `-2`; troca de
arte do Despertar (o `-2` usa `RemapSprite`, não `ChangeAnim`; a descrição antiga estava errada e piscaria); 20/100/105
com anim própria e passada ~80% no Diabo; loops de 48/32 desenhos no andar/correr; windups abaixo do piso da 8.3 (410,
601, 611, 344 → 7; 347 → 8 com hitstop 12; 3410-3412 e 3420-3422 → 9); `fall = 1`/`heavy-landing` explícitos em 303,
313, 323, 333; `uppercut` no 410/3430 e `heavy-landing` nos kombos que derrubam e nos agarrões; mínimos da 7.1 (virar
5/6 com `vira`, agachar/levantar em troca seca, guarda 0-7, intro/vitória/levantar com meio, supers com meio na
abertura); Clsn1 do 246 (não pegava agachado) e do 611 (x1 0 contradizia a nota); contato do Giro (C4, não C5);
Rolada com todo quadro virado para a direita; Tesoura no chão e subida física no 3002; Estatueta parada fora de um
`Projectile` só; `gp.PROJETEIS` na lista de globais; verificador conferindo os `ChangeAnim2`; "28 números" avulsos;
efeitos pedidos pela ficha (`fx_papel` no Despertar, lasca nos chutes fortes, brilho no `fx_estatueta`); peso e alcance
do Diabo; sons reservados para as falas; 11701 com `d_coice` 2-4; corrente y/b desperta com uma folha por golpe; arte
`d_` para recuo, agarrões e afastar; itens do checklist 9 no plano de teste; patroa, estatueta e chapéu (conteúdo/PI);
Riscos com todas as mudanças na ficha.

**Recusado:** nada inteiro. Em parte: o `[Statedef 5150]` próprio (revisor 1) ficou como `-2` chamando o 171, para não
reescrever o estado de nocaute do common; a 347 não virou finalizador (windup 10, hitstop 14), ficou igual aos outros
fechos de kombo (8 / 12).

**Dúvidas para o Breno:**

1. Correntes x/a, Faixa no Asfalto e os 4 kombos da base saem no Despertar (proposta) ou ficam com +10000 (~9 folhas
   `d_` a mais)?
2. `apanha` e `queda` com 7-8 desenhos contra os 10-20 da 7.1: aceitar como o elenco ou gerar `apanha_2`/`queda_2` (e
   as `d_`, 4 imagens)?
3. Tesoura de Bairro no chão (giro de 540° sem pular) está bom?
4. Chapéu Bumerangue que cai de volta na cabeça (para não ler como o chapéu de MK) está bom?
5. As mudanças de nome e de comando já listadas na seção 11.

**A conferir na sandbox (técnico):** `ModifyProjectile` na versão instalada (senão, segundo projétil parado);
`ChangeState` para o 171 com `!Alive`; a medição da passada na `anda.png`.
