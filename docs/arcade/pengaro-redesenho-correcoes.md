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
| agarrao | 4, 5 | de costas, garrafa troca de mão | refazer 4 e 5 com a garrafa na mão de sempre |
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
