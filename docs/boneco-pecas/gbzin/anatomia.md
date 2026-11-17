# Gbzin: estudo de anatomia aplicado (17/11/2026)

Esta é a conferência dos 36 golpes do Gbzin base contra a Parte 4 de [`estudo-anatomia-golpes.md`](../../estudo-anatomia-golpes.md),
seguindo o guia [`aplicar-estudo-anatomia.md`](../../aplicar-estudo-anatomia.md). Folhas olhadas: `sprites/gbzin/quadros_firmes_hd/`.

## Ficha: perto e longe

Na guarda, virado para a direita, o Gbzin fica de peito aberto para a câmera.

| Lado | Em relação ao oponente | Em relação à câmera | Marca da roupa | Camada na raiz |
| --- | --- | --- | --- | --- |
| esquerdo | frente | longe | mão em garra, sem relógio | atrás do tronco e da faixa |
| direito | trás | perto | mão da bengala, relógio dourado no pulso | na frente |

`CAMADAS` do kit: a coxa da frente vai antes do quadril, então a perna longe nasce atrás da faixa (certo). O braço da
frente vai por cima de tudo, o que só funciona enquanto ele não cruza o peito.

A pele nas juntas (`pele_pecas.py`) usava a ordem do Pengaró, que tem a perna da frente por cima do corpo. Agora o
Gbzin usa a ordem dele (`PELE_CAMADAS` em `gbzin_pecas.py`).

## Golpe a golpe

| Golpe | Resultado | Nota |
| --- | --- | --- |
| soco | passa | Passo e giro do quadril vindos do desenho do passo. A cotovelada (04-05) é um gancho dobrado: cotovelo armado antes, quadril girado no contato, mão da bengala na cintura. |
| chute_alto | passa | É um chute frontal no peito: tem câmara (02), perna esticada no 04 e volta pela câmara (05). A perna longe nasce atrás da faixa. A mão em garra fica na guarda, acima da perna. |
| bicicleta | passa | No ar: uma perna estica e a outra fica dobrada embaixo, nunca as duas esticadas (folha nova de 17/11). |
| chute_baixo, rasteirinha, rasteira | passa | Joelhos dobrados e cabeça alta. Na rasteira a perna varre rente ao chão. |
| martelo, compasso, cajado_chao, bola, lata, ar_soco | passa | São golpes de bengala: o corpo inclina e dá o passo antes do braço estender. |
| afastar | passa (exceção) | É um coice de dois pés sentado no chão. As duas pernas esticadas juntas são o golpe, e a regra do "golpe no ar" não vale porque ele está apoiado. |
| armada, parry_baixo, caneta | passa (exceção) | Não são os giros de capoeira do estudo, são golpes de jiu-jitsu da ficha do Gbzin (guarda fechada, rolamento de costas, chave de braço voadora). |
| cabecada | rever depois | No 04 e 05 o golpe é a bengala erguida, não a testa. Bate com o pedido da folha, mas não com a receita da cabeçada do estudo. Fica para o Breno decidir. |
| demais (anda, corre, pulo, defesa, apanha, queda, levanta, provoca, vitoria, derrota, despertar_a, golaco, agarrao, agachado, recuo, rolamento, referencia_ginga, parry_alto) | passa | Não são golpes de contato, ou a pose já segue as leis 1 a 5. |

Quadros do meio: vale a regra de fluidez do Alisson até ele decidir o cartão da Lei 10.

## Ainda falta

- Pé de apoio girado (variante "pé girado" no kit) para o dia em que entrar um chute circular de verdade.
- Especiais com 20 a 40 desenhos (regras), quando sair o pedido.
