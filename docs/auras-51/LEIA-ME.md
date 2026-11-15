# Auras e asas seguindo o corpo (issue #51, item 1)

Pedido do Breno (2026-11-14, `docs/missao-alisson-estilo-melty.md`): o Hazak endiabrado agachava ou caía e as asas
ficavam no mesmo lugar, no ar. Toda aura tem de acompanhar o lutador em todo estado.

## O que estava errado

As camadas da aura (`ferramentas/aura.py`) nascem presas ao **eixo** do lutador, que é o ponto dos pés, numa posição
fixa. Quando ele agacha, apanha, cai ou deita, o eixo não sai do lugar: só o desenho muda. Então a asa ficava na altura
de quem está em pé, com o corpo no chão. No pulo ela já subia junto, porque aí o eixo sobe.

## O conserto

`ferramentas/aura_no_corpo.py`, um pós-passo como o `parry.py` (roda em cima de `chars/<l>/`, quantas vezes for):

1. **Mede o corpo em cada desenho** de cada ação do `.air`, já no sprite do despertado: onde está o peito, o centro e
   a altura, comparado com o parado.
2. **Escreve uma tabela no `[Statedef -4]`** (por ação e elemento) com o alvo daquele tique. Quatro maps correm atrás
   do alvo com um atraso curto: a asa chega um instante depois do corpo, que é o movimento secundário da missão.
3. **Troca a posição e a escala de cada camada:**

| Camada | Lutador | O que faz agora |
|---|---|---|
| asas e coroa | Hazak (Diabo Loiro) | seguem o peito; com ele deitado, recolhem (metade do tamanho, em volta do corpo) |
| garanhão, raios e ferraduras | Gutto | igual às asas |
| elos e pedras soltas | Pengaró | igual às asas |
| brasa, crateras, anel, névoa | todos | ficam no chão e andam em x com o corpo (não afundam mais na queda) |
| coluna de sombra | Pengaró | fica no chão e **baixa** quando ele cai |
| paredão | CK | fica no chão e **baixa** quando ele cai |

O Raiclaven ainda não tem aura em camadas na `mugen` (a da dupla está na conversa da #43); quando entrar, basta rodar
`python3 ferramentas/aura_no_corpo.py raiclaven`.

Os geradores já chamam o pós-passo no fim (`diabo_loiro.py`, `despertados_47.py`, `gerar_pengaro.py`, `gerar_ck.py`).

## Robô e filme

```bash
python3 ferramentas/aura_no_corpo.py --robo            # roda o roteiro no motor (sem filme) e confere os 4
python3 ferramentas/filmar_aura_corpo.py hazaki --saida PASTA    # filme em tempo real + aura_log.txt
```

O roteiro passa o endiabrado por 30 estados: parado, agachado, pulo, andar, correr, golpe em pé, derrubado (voa, cai,
chão, levanta), agarrado e arremessado, defesa e pose de vitória. A cada tique o robô compara o ponto do peito da
camada com o peito do desenho que está na tela.

| Lutador | Camada | Antes (95% dos tiques a até) | Depois | Maior tempo solta (mais de 20 px) antes → depois |
|---|---|---|---|---|
| Hazak | asas | 31,5 px | 7,2 px | 100 tiques → 1 |
| Gutto | garanhão | 41,6 px | 7,8 px | 121 tiques → 1 |
| Pengaró | elos soltos | 40,2 px | 11,2 px | 181 tiques → 2 |
| todos | camadas de chão | afundavam 26 px na queda | 0 a 3 px | |

Vídeos lado a lado (antes e depois, o mesmo roteiro): `hazaki_antes_depois.mp4`, `gutto_antes_depois.mp4`,
`pengaro_antes_depois.mp4`, `ck_antes_depois.mp4`.

## O que não foi feito e sugestões

- **Girar** a asa junto com o corpo no ar. Hoje ela segue e recolhe; não gira (o giro do motor quebra a grade do pixel).
  Dá para fazer com desenhos da asa inclinada, se o Breno quiser.
- O paredão do CK e a coluna do Pengaró **não sobem no pulo**: são coisas que nascem do chão. Se o Breno preferir que
  subam junto, é trocar uma linha (`presa_ao_chao`) e filmar de novo.
- O paredão baixando é o desenho achatado pelo motor. Um desenho próprio de "paredão baixo" ficaria melhor.
- Lutador novo ou golpe novo: nada a fazer à mão, a tabela é medida de novo a cada geração.

## Segunda volta (Breno, 2026-11-15): grudada nas costas, girando e fechando

O Breno viu a primeira versão e pediu mais: deitado, a asa continuava em pé e aberta; ela tem de ficar grudada nas
costas, inclinar no ângulo do corpo e fechar quando ele cai, reabrindo ao levantar. Feito:

- **Âncora nas costas, não no peito.** O ponto é o centro da metade do corpo que tem a cabeça. Deitado, essa metade é
  a ponta mais pesada do eixo comprido do desenho (a cabeça e o tronco pesam mais que as pernas).
- **Ângulo do tronco em cada quadro de cada ação**, guardado numa segunda tabela no `[Statedef -4]` (`au_<nome>_th`, em
  degraus de 7,5 graus). A camada gira nesse ângulo com o `angle` do Explod, em volta das costas (o motor gira em volta
  dos pés da camada, e a posição compensa). Em pé o tronco inclina no máximo 50 graus; deitado chega a 85.
- **Asas fechando do Hazak:** dois desenhos novos, `asas_meio` e `asas_fechada` (camadas 9602 e 9603), feitos dobrando
  os 48 quadros das asas como um leque em volta da raiz (`aura.dobrar_asas`; o pixel continua o do desenho). O alfa troca
  aberta → meio → fechada conforme o corpo deita, e volta ao levantar.
- **Garanhão do Gutto e elos do Pengaró** giram e grudam do mesmo jeito; como não têm desenho fechado, recolhem
  (encolhem pela metade em volta das costas) deitados.
- `python3 ferramentas/diabo_loiro.py --aura` refaz só a aura do Hazak em cima do `chars/hazaki` pronto.

Robô da aura (`aura_no_corpo.py --robo`), agora também com o ângulo:

| Camada | Distância às costas (95% dos tiques) | Ângulo contra o tronco (95%) | Maior tempo solta |
|---|---|---|---|
| asas do Hazak (aberta, meio, fechada) | 6,5 a 7,1 px | 6 graus | 2 tiques |
| garanhão do Gutto | 7,5 px | 12 graus | 2 tiques |
| elos do Pengaró | 11,0 px | 11 graus | 2 tiques |

O pior tique de todas é o pouso de quem foi arremessado (60 px por 2 tiques): o desenho passa de em pé para deitado num
tique só, e o `-4` vê a ação nova um tique depois.

Vídeos (o mesmo roteiro, a versão de antes desta volta contra a de agora): `hazaki_v2_antes_agora.mp4`,
`gutto_v2_antes_agora.mp4`, `pengaro_v2_antes_agora.mp4`, `ck_v2_antes_agora.mp4`. Quadro a quadro do Hazak:
`v2_hazak_queda_quadro_a_quadro.jpg` e `v2_hazak_golpes_quadro_a_quadro.jpg`.

**Ainda não feito:** a coroa vai junto com as asas (é o mesmo desenho), então deitado ela também deita; uma asa fechada
desenhada à mão ficaria melhor que a dobrada por código; no pouso brusco há o tranco de 2 tiques descrito acima.

## Terceira volta (2026-11-15): os três pontos que ficaram em aberto

O Breno liberou na #51 (01:37Z) decidir e juntar sem esperar aval, com robô passando e antes/depois quadro a quadro.
Decidido assim:

- **Pouso brusco: de 2 tiques soltos para 1.** Quando o alvo pula mais que um limite (24 px, 40 graus ou meia deitada),
  a camada não corre atrás: pula junto com o corpo no mesmo tique. Sobra 1 tique, que é o atraso do próprio motor (o
  `-4` vê a ação nova um tique depois) e não dá para tirar sem mexer no motor.
- **No quique do chão a asa continua fechada.** Antes o corpo meio levantado no quique (deitado 0,6) acendia a asa meio
  aberta por uns quadros; agora a fechada vale de 0,5 para cima e a meio só aparece entre 0,15 e 0,5, que é o levantar
  de verdade. Quadro a quadro: `v3_pouso_quadro_a_quadro.jpg` (em cima antes, embaixo agora).
- **A coroa fica com as asas.** O Breno pôs a coroa na lista do que gruda no corpo, então ela deita e gira junto.
- **Asa fechada continua a dobrada por código.** Uma desenhada à mão entra quando a ferramenta de pixel da anatomia
  (#51 item 3) estiver pronta; é só trocar o desenho da camada 9603.

Robôs: aura nos 4 passa (asas 6,3 a 6,8 px e 6 graus em 95% dos tiques, garanhão 6,6 px, elos 8,0 px, no máximo 1 tique
solto); `testar_pengaro.py --linux` hazaki 238, gutto 186, pengaro 189, ck 226, 0 falhas.
