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

| Som | O que é |
|---|---|
| `51,0..4` | acerto de **soco** (CK com timbre de luva, Hazak de concreto) |
| `52,0..4` | acerto de **chute** (canela, mais grave, com chicote de pano) |
| `53,0..4` | acerto dos golpes **endiabrados** (34xx): grave rasgado com cauda escura |
| `50,x` | assinatura do lutador (abaixo) |

| Lutador | `50,0` | `50,1` | `50,2` | `50,3` | `50,4` |
|---|---|---|---|---|---|
| Pengaró | garrafa (tim de vidro) | vidro quebrando | gole | possessão das sombras | lata |
| CK | boné voador | tragada | grave do paredão | garrafa voadora quebrando | |
| Gutto | beijinho | joelhada | galope | relincho | |
| Hazak | concreto | estatueta dourada | guarda de aço | faixa | |
| Raiclaven | tesoura | borrifada | pente voador | cadeira giratória | |

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
- `.cns`: `hitsound = F5,k` vira `51,k` (soco), `52,k` (chute, pelo comando a/b no `.cmd`) ou `53,k` (endiabrado); os
  especiais com assinatura usam `50,x`. Cada troca leva o comentário `; som:F5,k` para poder desfazer.
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
