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
