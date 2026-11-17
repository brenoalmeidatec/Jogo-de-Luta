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

## Quarta volta (Breno, 2026-11-15 02:07Z): aura como nos animes, colada na silhueta

O Breno pediu o passo seguinte: a aura com o formato do corpo em todo quadro, correndo pelo braço no soco e pela perna
no chute, com inércia e labaredas vivas, sem cara de adesivo. A aura grande de cada um (asas, garanhão, elos, paredão)
continua; esta é uma camada a mais, colada no corpo. Ferramenta: `ferramentas/aura_silhueta.py` (pós-passo idempotente,
roda depois do `aura_no_corpo.py`).

- **Silhueta de cada quadro.** Para cada desenho que o despertado mostra, a ferramenta tira o contorno do alfa, reduz
  pela metade (o pixel da aura fica com o grão do pixelfx) e gera duas camadas:
  - a **pele**, um brilho somado colado no corpo, quebrado pelo ruído para não virar contorno;
  - a **chama**, labaredas em línguas que sobem. A distância "sobe mais barato que desce", e a borda é cortada por um
    ruído que corre para cima em 6 fases (laço de 12 tiques). Ela fica por trás do corpo também, então não sobra fresta.
- **Membro que bate.** Nos quadros com caixa de golpe, o pedaço do corpo dentro da caixa ganha labareda maior e mais
  clara, e a ponta (punho ou pé) solta um estouro pequeno, do tamanho do golpe.
- **Cor de cada um,** tirada da aura grande dele numa rampa de energia: brasa laranja-ouro no Hazak, vermelho no Gutto,
  violeta no Pengaró e fumaça cinza-esverdeada no CK, que é pouco saturada como a dele.
- **Inércia.** Uma mola segue a velocidade (maps `au_sil_x`, `au_sil_v`). A chama inclina com `xshear` em volta dos pés,
  então a parte de cima arrasta mais que a de baixo. Quando ele para, ela passa um pouco do ponto e assenta. Na queda,
  a chama estica.
- **Sincronia.** Um Explod nascido no `[Statedef -4]` vê a ação nova um tique atrasado. Por isso a pele é um helper
  (estado 9610), que roda depois do lutador no mesmo tique e mostra o mesmo elemento do corpo (`ChangeAnim` com `elem`).
  O helper também solta a chama (Explod 9611 de um tique). No roteiro de 1.120 tiques, 99,6% batem exatos; os 5 que
  escapam são da câmera lenta do KO.
- Grupos do .sff: 9710 (pele) e 9711 (chama). Ações espelho: 30000 + N (pele) e 40000 + N (chama).
  `--previa PASTA lutador --acoes 0,240` faz uma folha sem o motor, e `--tirar` desfaz.

**Custo:** o .sff cresce de 5 a 16 MB por lutador (3.363 desenhos da aura no Hazak). O Raiclaven ainda não tem aura em
camadas na `mugen` (a da dupla está na #43); quando tiver, é só rodar a ferramenta nele.

Robôs depois da mudança: `testar_pengaro.py --linux` com Hazak 238, Gutto 186, Pengaró 189 e CK 226, sem nenhuma falha.
`aura_no_corpo.py --robo` nos 4 também passou ("a aura segue o corpo em todos").

Vídeos: `hazaki_v4_antes_agora.mp4`, `gutto_v4_antes_agora.mp4`, `pengaro_v4_antes_agora.mp4` e
`ck_v4_antes_agora.mp4`. É o mesmo roteiro dos outros: parado, agachado, pulo, andar, correr, golpes (soco e chute),
derrubado, agarrado, defesa e vitória. À esquerda fica a versão anterior e à direita a de agora. A folha
`v4_<lutador>_quadros.jpg` tem um quadro a cada 1,3 s do lado "agora".

## Quinta volta (Breno, 2026-11-15 03:51Z, item 2): luz e brilho do KIKIU

O pedido foi trazer a base de luz do KIKIU para as auras e os poderes. O repositório do KIKIU não foi tocado. A ideia
foi lida dos trechos citados por ele e adaptada para o IKEMEN em `ferramentas/luz.py`. Piloto no Hazak.

- **Curva de luz do KIKIU:** `GRAD_OFF = [0, 0.22, 0.55, 1]` e `GRAD_VAL = [1, 0.5, 0.1, 0]`. O miolo é forte e a luz
  cai rápido. Os desenhos de luz saem em degraus com pontilhado 4x4 e grão de 2 pixels do jogo, para casar com o
  pixel da aura.
- **Mundo escurece.** Um Explod preto bem grande fica por trás do lutador e na frente do cenário. Com `addalpha
  (0, 256 - k)`, o cenário perde cerca de 16% no Despertar e chega a 31% com poder no ar (medido no canto do cenário:
  173, depois 146, depois 120). Não usei o BGPalFX porque ele é um só para a luta e apagaria os clarões das supers.
- **Halo e poça.** Em volta do corpo do despertado fica um brilho na cor da forma, e no chão embaixo dele uma poça de
  luz achatada, que some conforme ele sobe no pulo. Os dois seguem o centro do corpo pelos maps do `aura_no_corpo.py`.
- **Poderes.** A bola de ki (projid 1001) e a rajadona (1650) ganham um orbe somado no miolo, um halo e uma poça que
  correm com o projétil (mesma posição e velocidade) e somem quando ele some. A pedra não acende, porque é pedra.
- **Oponente perto clareia** na cor da luz, de leve e pela distância (PalFX com `redirectid`). Não clareia quando ele
  está apanhando, preso num estado do Hazak ou despertado (o Gutto e o Raiclaven têm tom próprio na forma).
- **Tremor** de 2,2 Hz com 1,3 Hz por cima, sem passar de 2,5 Hz.

**O que mudou do primeiro filme.** Primeiro a luz era somada pura e pequena, e sumia atrás da aura grande. No fundo
azul, a soma do laranja também puxava para o rosa. Agora o halo e a poça são brilho por alfa de pixel (`addalpha`):
a curva do KIKIU vai no alfa e a cor fica cheia. Os raios cresceram (halo 170, poça 120, halo do poder 115). O orbe
continua somado, porque ali o branco quente é o que se quer.

**Conserto de passagem:** o `aura_silhueta.py` só tirava as ações que começavam com "30000" e "40000". Ao rodar de
novo, ele duplicava as outras ações espelho. Agora tira a faixa toda, e o `aura_no_corpo.py` não mede mais as ações
de luz (9720 a 9739). Rodar duas vezes dá o mesmo arquivo.

Robôs depois da mudança: `testar_pengaro.py --linux --lutador hazaki` com 238 verificações e nenhuma falha.
`aura_no_corpo.py --robo hazaki` também passou ("a aura segue o corpo em todos").

Vídeo: `hazaki_luz_antes_agora.mp4` (20 s). É o roteiro de sempre com a bola de ki no começo e a rajadona no fim. À
esquerda fica a mugen de antes e à direita a de agora. A folha `hazaki_luz_quadros.jpg` mostra três momentos: parado
despertado, carregando o ki e a rajadona.

**Próximos passos:** a aura juntando na mão antes do especial (a luz nos outros veio na sexta volta).

## Sexta volta (Alisson, 2026-11-16): luz em todo efeito que brilha, nos 5 lutadores

O Alisson gostou da luz do Hazak e pediu para pôr em todos os efeitos que têm luz. Agora a luz está no Hazak, no
Gutto, no Pengaró, no CK e no Raiclaven, feita pela `ferramentas/luz.py` com a `ferramentas/luz_efeitos.py`.

- **A luz sai do próprio efeito.** Cada efeito que brilha (fogo, ki, raio, faísca, clarão de carga) ganha um Explod
  irmão logo atrás dele, com os mesmos gatilhos, posição, ligação e id. A luz dele tem a cor média dos pixels que
  brilham. Cada quadro do efeito vira um quadro de luz com a força (5 degraus) e o tamanho (3 tamanhos) do brilho
  daquele quadro, no mesmo centro e com o mesmo tempo. Ela acende, pisca, cresce e apaga junto com o efeito.
- **O que acende foi revisado.** O automático olha pixel claro e saturado, mas erra em objeto colorido (a Cliente de
  camiseta amarela, os corações do Gutto) e em faísca branca. Cinco revisores, cada um com a folha de um lutador e
  um segundo revisor contestando, fecharam a lista em `ferramentas/luz_classes.json`. Pedra, poeira, fumaça, garrafa,
  latinha, coração, pente, boné, caixa de som e gente ficam apagados.
- **Clarão do golpe.** Todo golpe que o lutador acerta solta um clarão de uns 12 tiques no ponto do impacto, na cor
  da faísca daquele golpe (normal, forma despertada), maior no especial e na super. Na defesa, um clarão menor. Vai
  pelo [Statedef -4] (HitCount e MoveGuarded), conferido no motor pelo log (Explod 9640).
- **Poderes.** Bola de energia: orbe somado por cima (o miolo quente), halo e poça que andam com ela, com a mesma
  aceleração. Raio: a luz do próprio desenho, quadro a quadro, e um orbe parado na mão.
- **Despertado** do Gutto, do Pengaró e do CK: halo na cor da forma, poça no chão e o cenário escurecendo, como no
  Hazak. O Raiclaven não tem aura em camadas e fica só com a luz dos efeitos e dos golpes.

**Conferência.** Foram quatro rodadas de filme dos 5, cada uma conferida quadro a quadro por um revisor e
contestada por outro. O que apareceu e foi consertado:
- quadriculado de quadrados grandes no clarão da super (grão e raio limitados);
- luz solta na frente dos raios (agora a luz é do desenho do raio);
- luz da lâmina do Pengaró ficando para trás (faltava a aceleração);
- oponente do CK pintado de verde-oliva (o PalFX ficou bem mais leve e meio branco);
- clarão branco lavando a tela na super do Raiclaven (efeito ampliado fica com a luz no tamanho 1);
- clarão do golpe faltando em quatro lutadores (a faísca deles é uma expressão);
- a bola de fogo do Hazak sem o miolo quente.

**Robôs:** `testar_pengaro.py --linux` sem falha nova nos 5. O que falha (o teste do raio do Hazak, que oscila, e
asas/peças soltas no `aura_no_corpo.py --robo` do Hazak, do Gutto e do Pengaró) falha igual na `mugen` de antes.

Vídeos: `<lutador>_luz_todos_antes_agora.mp4` (os 5), com a `mugen` de antes à esquerda e a de agora à direita. Cada
um força dois poderes e um golpe que acerta. Na última rodada os 5 foram aprovados pelos revisores.

**Ficou de detalhe (não quebra, anotado para depois):** o brilho do raio do Hazak e do Pengaró começa um pouco à
frente da ponta enquanto o raio cresce; pontilhado leve no cenário escurecido do CK, visível com zoom; o clarão do
golpe do CK é verde-claro e some um pouco no fundo; um ponto rosa no chão perto do casco do Gutto enquanto o raio dele
carrega.
