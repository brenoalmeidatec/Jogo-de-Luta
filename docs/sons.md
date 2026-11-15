# Sons do Nazafights

Missão 2026-11-14, item 2 (pedido do Breno): sons novos para golpes, defesa, agarrão, queda, especiais, supers,
transformação, parry, menu, contagem do round e KO, cada lutador com o seu som, nada copiado de outro jogo e volume
parelho com as músicas.

**Tudo é feito por código** em [`ferramentas/gerar_sons.py`](../ferramentas/gerar_sons.py): osciladores, ruído filtrado,
envelopes e um tempero 8-bit (bitcrush) para casar com a trilha. Não há amostra de outro jogo. A voz do narrador é o
Piper TTS com a voz pt_BR **cadu** (dados CC0), tratada no próprio script; as falas cruas ficam em `sons/narrador/`.

```bash
python ferramentas/gerar_sons.py             # gera os .snd e liga nos lutadores (pode rodar de novo à vontade)
python ferramentas/gerar_sons.py --wav PASTA # também solta cada som em .wav para ouvir
python ferramentas/gerar_sons.py --medir     # LUFS e pico de cada som
```

Os geradores dos lutadores (`gerar_pengaro.py`, `gerar_ck.py`, `gerar_gutto.py`, `gerar_hazaki.py`,
`gerar_raiclaven.py`) chamam `gerar_sons.ligar()` no fim, então regerar um lutador **não perde os sons**.

## Volume

As músicas estão em **-14 LUFS** integrado. Cada som é nivelado pela loudness momentânea máxima (janela de 400 ms, a
mesma medida do `ffmpeg -af ebur128`, conferida com ele), com pico no máximo em -1 dBFS:

| Tipo | LUFS máx | Exemplo |
|---|---|---|
| Golpe forte, fim de corrente, super, narrador | -13,5 a -12 | `F5,2`, `F5,4`, `0,1` |
| Golpe médio, agarrão, parry | -15,5 | `F5,1`, `F35,0`, `F30,0` |
| Golpe fraco, defesa, queda leve | -17 | `F5,0`, `F6,0` |
| Vento do golpe | -21 a -18 | `F40,x` |
| Menu | -20 a -18 | `100,x` |

## Onde mora cada som

### `motif/nazafight/common.snd` (sons "F", servem para qualquer lutador)

O IKEMEN acha este arquivo pelo `common.snd = common.snd` do `fight.def`; ele substitui o `data/common.snd` do motor.

| Som | O que é |
|---|---|
| `F5,0` `F5,1` `F5,2` `F5,3` `F5,4` | acerto: fraco, médio, forte, fim de corrente, fim de super |
| `F6,0` `F6,1` | defesa, defesa de golpe forte |
| `F7,0` `F7,1` `F7,2` | queda no chão (o `common1` do motor escolhe pela velocidade) |
| `F20,0` | início de super (SuperPause) |
| `F30,0` `F30,1` | **parry**: forma base (brilhante) e endiabrada (grave e rasgado) |
| `F31,0` `F31,1` | **transformação**: o poder carregando e o estouro quando vira endiabrado |
| `F35,0` `F35,1` `F35,2` | **agarrão**: pega (pano e tranco), arremesso (vento grande), escape |
| `F36,0` | projétil saindo |
| `F40,0` `F40,1` | vento de soco fraco e forte |
| `F40,2` `F40,3` | vento de chute fraco e forte |
| `F40,4` | vento de especial |

### `chars/<lutador>/<lutador>.snd`

Issue #46 (Breno, 2026-11-14): **cada golpe soa com o que o lutador usa nele.** O acerto com objeto é o acerto comum
(que diz o peso: fraco, médio, forte, fim de corrente, fim de super) com a camada do objeto por cima (`acerto_arma`).

| Som | O que é |
|---|---|
| `51,0..4` | acerto da **mão** (timbre do lutador, tabela abaixo) |
| `52,0..4` | acerto de **chute** |
| `53,0..4` | acerto dos golpes **endiabrados** (34xx), com o objeto da forma |
| `54,0..4` | acerto da **arma da mão** (tesoura, garrafa, cotovelo, pedra) |
| `55,0` `55,1` | "vento" da arma, fraco e forte (só Raiclaven: a tesoura abrindo) |
| `50,x` | assinaturas do lutador (abaixo) |

| Lutador | 51 mão | 52 chute | 53 endiabrado | 54 arma |
|---|---|---|---|---|
| Pengaró | soco | chute | sombra com **corrente** | **garrafa** (vidro grosso, sem quebrar) |
| CK | **luva** | chute | **caco de garrafa** (Modo Ratão) | luva |
| Gutto | soco | **canela de Muay Thai** (tapa largo) | **casco** de cavalo | **cotovelo e joelho** (osso seco) |
| Hazak | **concreto** | chute | **brasa das trevas** (Diabo Loiro) | **pedra** que racha |
| Raiclaven | **pente** de plástico | chute | **serra** (tesoura do Surto) | **tesoura** fechando ("tchac") |

| Lutador | Assinaturas `50,x` |
|---|---|
| Pengaró | 0 garrafa (tim) · 1 vidro quebrando · 2 gole · 3 possessão · 4 **latinha voando** · 5 **latinha batendo** · 6 **chimpanzé** · 7 **corrente** · 8 garrafa girando no ar |
| CK | 0 boné voador · 1 tragada · 2 grave do paredão · 3 garrafa voadora quebrando · 4 **boné acertando** · 5 **paredão tocando** · 6 **garrafa quebrando no chão** |
| Gutto | 0 beijinho · 1 joelhada · 2 galope · 3 relincho · 4 **bufada** · 5 **coice** |
| Hazak | 0 concreto · 1 estatueta dourada · 2 guarda de aço · 3 faixa · 4 **pedra levantando do chão** · 5 **pedra voando** · 6 **carga de ki** · 7 **bola de ki** · 8 **rajada de ki das trevas** · 9 **pedra batendo** |
| Raiclaven | 0 tesoura · 1 borrifada · 2 pente voador · 3 cadeira giratória · 4 **tesoura helicóptero** · 5 **vassoura** · 6 **talco** · 7 **máquina zumbindo** · 8 **máquina explodindo** · 9 **navalha de sombra** · 10 **toalha quente** · 11 **cabeça na pia** |

### Golpe por golpe (o que mudou na #46)

- **Números dos estados:** o Gutto e o Raiclaven usam o molde do Pengaró, então os números são os mesmos e os nomes
  de verdade estão no `movelist.dat` de cada um (1000 ↓→K, 1100 ↓←K, 1200 →↓P, 1300 ↓←P, 1400 ↓→P, 1500 ←↓K,
  1600 →←P, 1700 →←K, 3000/3100/3200 supers, 34xx despertado).
- **Raiclaven:** o **y é a tesoura** (normais, correntes e kombos de y): sai com a tesoura abrindo (`55,x`) e acerta
  com o corte (`54,k`); o **x é o pente** (`51`). Tesoura Helicóptero roda com cortes no ritmo (`50,4` + `54`),
  Tesoura Voadora e Tesourão cortam (`54`), Varrida é vassoura, Próximo! some no talco, Próximo, Cliente! são 8 cortes
  de tesoura, Máquina Explosiva zumbe e explode no último acerto, Navalha de Sombra tem o "shiiing" dela, Toalha
  Quente estala o pano e Cabeça na Pia faz splash. No Surto, os cortes são de serra (`53`).
- **Pengaró:** Latada de Sombra é a **latinha** (voa chacoalhando e amassa no acerto); Garrafada em Arco é **vidro**;
  Chuva de Bebidas alterna lata e garrafa e estoura vidro no fim; Mão de Chimpá e Bando da Várzea têm o grito do
  chimpanzé; agarrões batem com a garrafa; no endiabrado, as algemas: **corrente** nos golpes (`53`) e nos especiais.
- **CK:** luva em tudo de mão, Boné Voador acerta com a aba do boné, Despertar com o **paredão tocando** e a garrafa
  quebrando no chão (tick 42), Modo Ratão corta com o **caco** (`53`), Baile da Esquina com o paredão.
- **Gutto:** chute é **canela** de Muay Thai, o y é **cotovelo e joelhada** (`54`), Cotovelo Giratório também, clinch
  do agarrão é de joelhada; endiabrado: **casco**, coice, galope, relincho e a **bufada** no Despertar.
- **Hazak:** soco de concreto; Punho de Concreto agora é a **pedra**: chuta o chão (`50,4`), a pedra voa (`50,5`) e
  bate rachando (`50,9`). **Carga de ki, bola de ki e a rajadona de ki das trevas** (`50,6` a `50,8`) e os acertos
  do Diabo Loiro (`53`) estão prontos no `.snd`, esperando os estados novos da issue #44: quem ligar esses golpes
  só precisa pôr o estado em `ESPECIAIS["hazaki"]` (ex.: `("T0", "50,6")` na carga, `("proj", "50,7")` na bola).
- **Agarrões** (`AGARROES`): cada pancada toca o som do que bate, em ordem (`; som:F5,k` guarda o original).

### `motif/nazafight/fight.snd` (narrador e barra)

| Som | Fala |
|---|---|
| `0,1`..`0,9` | Primeiro round! ... Nono round! |
| `0,10` `0,11` | Round final! / Round único! |
| `1,0` | Luta! |
| `2,0` `2,1` `2,2` | Nocaute! / Nocaute duplo! / Acabou o tempo! |
| `2,3` `2,4` `2,5` `2,6` `2,7` | Você venceu! / Você perdeu! / Empate! / Perfeito! / Foi por pouco! |
| `21,0` `21,1` | barra de poder subiu um nível / chegou no máximo (arpejo de chip) |

### `motif/nazafight/system.snd` (menu)

`100,0` mover, `100,1` confirmar, `100,2` voltar; `900,0..10` contagem do continue (Zero! ... Dez!).

## Como os sons entram no lutador (`gerar_sons.ligar`)

- `.def`: `sound = <lutador>.snd`.
- `.cns`: `hitsound = F5,k` vira `S51,k` (soco), `S52,k` (chute, pelo comando a/b no `.cmd`), `S53,k` (endiabrado)
  ou `S54,k` (botão da arma, `BOTAO_ARMA`); os especiais e supers seguem `ESPECIAIS` (um grupo, um som fixo `50,x` ou
  uma lista, um por acerto). Cada troca leva o comentário `; som:F5,k` para poder desfazer.
- Todo golpe que bate ganha um `PlaySnd` de vento no `Time = 0` (`F40,x`); projéteis tocam a assinatura junto do
  `Projectile`/`Helper`. Os controladores novos se chamam `[State N, som ...]` e terminam em `; som: fim`.
- Despertar (2000): a pausa toca `F31,0` no lugar do som de super e `F31,1` no tick 55 (quando vira endiabrado). No
  Pengaró: gole no tick 9, garrafa quebrando no 42 (desenho 6 do `despertar_a`) e possessão no 55.
- Parry que acertou (761 em cima, 765 embaixo): `F30,0` na forma base e `F30,1` no endiabrado. Agarrão que pegou
  (810, 831, 841): `F35,0` no `Time = 0`; as pancadas e o final seguem com os `F5,x` que a frente dos agarrões pôs.
  `F35,1` (arremesso) e `F35,2` (escape) estão prontos para quem quiser usar.

## Falta e ideias

- **Ninguém ouviu ainda** (na nuvem o som sai mudo). O Alisson precisa ouvir e dizer o que trocar.
- Golpes normais no endiabrado (200 a 699 com `var(20) > 0`) usam o mesmo acerto da forma base; dá para trocar por
  `53,k` com um `hitsound` por expressão, se o motor aceitar.
- Gbzin ainda não tem pasta em `chars/`: quando entrar, ganha a assinatura do cajado (`50,x`) em `ASSINATURAS`.
- Falas por lutador (bordões, grito no especial) esperam o áudio do Breno.
- **#46, o que depende de outras frentes:** a pedra levantando e a bola de ki do Hazak ganham estados novos na #44,
  e o Diabo Loiro ainda não está ligado: os sons já estão no `.snd` (`50,4` a `50,9`, `53`), falta pôr os estados em
  `ESPECIAIS["hazaki"]`. O kit próprio do Cientista Louco (#43) e os agarrões e poderes dos despertados (#47) vão
  mudar estados do 34xx: quem mexer atualiza `ESPECIAIS`/`AGARROES` e roda `gerar_sons.py` (o gerador do lutador já
  chama `ligar()` no fim).
- O tick da garrafa quebrando no Despertar do CK (42) foi escolhido pelo momento em que o paredão vira fumaça; se a
  folha nova mostrar a quebra em outro quadro, é só mudar o `T42` em `ESPECIAIS["ck"][2000]`.
