# Pengaró do Breno de volta: plano de correção das 34 folhas

Pedido do Breno na issue #32 (2026-11-14): tirar o Pengaró antigo nítido (6ebee79 / merge eca5688), voltar o
redesenho dele (dc3427b) mantendo o que a revisão geral 118326d mudou, conferir as 34 folhas quadro a quadro e
consertar só o quadro ou a folha com defeito. Endiabrado sem mudar. Foto ao lado do CK na issue antes de juntar na `mugen`.

## O que já está feito nesta branch (`claude/project-thread-xhv5a2`, ainda fora da mugen)

| Commit | O que faz |
|---|---|
| 5c65e330 | desfaz as imagens de comparação do Pengaró antigo nítido |
| 1308b154 | desfaz o Pengaró antigo nítido (scripts `ampliar_folhas.py`, `nitidez_pengaro.py`, doc e sff) |
| b0489d8d | traz de volta o redesenho dc3427b inteiro (34 folhas em `folhas_novas/`, `converter_pengaro.py`, quadros 1x/3x, .air, .sff) |
| 86ac50e7 | regera o sff com o `gerar_pengaro.py` da revisão geral (gêmeos 3x do endiabrado continuam) |

Diferença para o dc3427b em `chars/pengaro`, `sprites/pengaro` e `gerar_pengaro.py`: só o que a revisão 118326d
mudou no gerador (`GEMEOS_HD`, `marcar_origem`, `gemeo_endiabrado`). O Endiabrado não foi tocado.

## Conferência quadro a quadro (primeira passada, feita por mim)

Folhas de contato dos quadros 3x: `docs/arcade/img/pengaro_revisao_r00.jpg` a `r08.jpg`, 4 folhas por imagem,
em ordem alfabética. O Breno vai mandar os erros dele na issue; esta lista junta com a dele.

| Folha | Quadro | Defeito que vi | Conserto proposto |
|---|---|---|---|
| agachado | 0, 1, 7 | em pé (transição de entrada/saída?) | confirmar com o Breno se é de propósito |
| agarrao | 4, 5 | de costas, a garrafa aparece do outro lado | **não é erro**: de costas a mesma mão fica do outro lado da tela (a joelheira também troca) |
| corre | 1, 3, 5, 6, 7 | riscos coloridos atrás da garrafa e chuvisco de cor nas pernas | limpar os quadros (apagar o rastro) |
| lata | 4 | mancha rosa/vermelha perto da garrafa/cintura | limpar o quadro |
| compasso | 4, 5 | mancha avermelhada perto das mãos/rosto (cabeça para baixo) | limpar os quadros |
| parry_baixo | 1 a 3, 6 | sequência estranha: deita no chão (1-3) e ergue a garrafa (6); mancha roxa no pé (4) | confirmar a intenção; limpar o 4 |
| parry_alto | todos | em pé com ~264 px de altura contra ~340 do parado | reescalar a folha inteira |
| pulo | 2, 3, 4 | riscos vermelhos perto da garrafa e nos cordões | limpar os quadros |
| queda | 0 | maior que o parado (378 px) | reescalar o quadro 0 |
| rasteira | 2 | mancha rosa perto do pé | limpar o quadro |
| vitoria | 4 | ponto roxo na cintura | limpar o quadro |

Mão, rosto, pés e ordem das poses no resto (afastar, anda, apanha, ar_soco, armada, baixo_soco, bicicleta, bola,
cabecada, caneta, chute_alto, chute_baixo, defesa, derrota, ginga, golaco, levanta, martelo, parado, provoca,
rasteirinha, recuo, rolamento, soco) estão coerentes nesta primeira passada.

### Tamanho entre folhas (altura do boneco no quadro 3x, em px)

Em pé, quase todas as folhas ficam entre 320 e 350 px (parado 344, anda 336, soco 337, recuo 339, chute_alto 345).
Fora disso, sem ser pose agachada/deitada/pulando: `parry_alto` (~264, pequeno demais) e `queda` 0 (378, grande demais).

## Como cada conserto vai ser feito

1. Defeito pequeno (mancha, risco, ponto): limpo direto no PNG da folha em `folhas_novas/`, sem redesenhar.
2. Quadro errado (mão trocada, pose): refaço só aquele quadro, com o mesmo traço, e colo na folha.
3. Tamanho: ajusto a escala da folha (ou do quadro) no `converter_pengaro.py`, que já tem escala por folha.
4. Depois de cada lote: `converter_pengaro.py` → `gerar_pengaro.py` → `trocar_retratos.py pengaro` → robô
   (`ferramentas/testar_pengaro.py`, roda na nuvem com Xvfb) → foto do Pengaró ao lado do CK na issue #32.
5. Só junto na `mugen` com o aval do Alisson depois da foto.

## Perguntas abertas para o Breno

- Pele: no redesenho ela puxa para marrom avermelhado. Está no tom que ele quer ou escureço mais?
- agachado 0/1/7 em pé e parry_baixo deitando: é de propósito?

## Feito em 2026-11-14 (segunda passada)

- **Agachado no jogo** (o erro que aparecia na luta): a folha nova é a descida inteira (0 em pé, 4 o mais baixo, 7 meio
  em pé), mas o jogo ainda usava a ordem da folha antiga, e o boneco subia até o 7 no meio do agachado e usava o 0
  (em pé) na troca. Agora a troca usa o 2 e a base agachada respira entre o 4 e o 5 (`gerar_pengaro.py`, ações 10/11/12
  e `TROCA_POR_FOLHA`). O Endiabrado não mudou (as ações dele são outras).
- **Riscos soltos** apagados direto na folha com `ferramentas/limpar_riscos_pengaro.py` (corre 1-7, afastar 1-5,
  pulo 2-5, rasteira 2 e 5): só some o pixel fino, longe do corpo, que não é pele, cordão nem contorno.
  Antes (em cima) e depois (embaixo): `img/pengaro_riscos_antes_depois.png`. O rastro laranja colado na garrafa da corrida
  ficou, porque tem a cor do cordão. Mancha de compasso 4/5, lata 4 e vitoria 4 ficaram como estão: o filtro de rosa
  furava a calça branca (o sombreado dela puxa para lilás) e foi descartado.
- **Tamanho do parry**: as folhas `parry_alto`/`parry_baixo` não têm desenho antigo para medir a escala e saíam pequenas.
  O `converter_pengaro.py` agora iguala o quadro 0 delas à mesma pose já convertida (guarda da defesa; base agachada da
  rasteirinha). As folhas de parry ainda não entram no jogo (docs/parry.md).
- **queda 0** maior que o parado: o quadro 0 não é usado no jogo (a queda começa no 1). Ficou.
- Robô na nuvem: **151/0**. Foto do Pengaró ao lado do CK no jogo: `img/pengaro_ck_redesenho.png`.
