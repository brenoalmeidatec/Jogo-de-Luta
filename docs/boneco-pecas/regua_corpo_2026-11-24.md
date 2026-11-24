# Régua do corpo todo

## Pernas (regua_pernas.py, do Alisson)

## Agachado (golpe do tipo agachado não pode levantar)

| lutador | forma | ações agachadas | elementos que levantam |
|---|---|---|---|
| pengaro | base | 15 | 400: 3, 410: 10, 764: 1, 1300: 1, 1301: 1, 3430: 9 |
| pengaro | despertado | 15 | 3430: 9, 10410: 7, 10764: 5, 11300: 1, 11301: 1 |
| gutto | base | 15 | 764: 3, 1300: 1, 1301: 1, 3430: 5 |
| gutto | despertado | 15 | 3430: 8, 10764: 6, 11300: 3, 11301: 3 |
| ck | base | 13 | 11: 1, 400: 5, 410: 12, 440: 2, 3430: 3 |
| ck | despertado | 13 | 3430: 6, 10410: 5, 10764: 3 |
| hazaki | base | 14 | 410: 4, 764: 1 |
| hazaki | despertado | 18 | 410: 2, 4401: 3 |
| raiclaven | base | 15 | 410: 13, 764: 2, 3430: 13 |
| raiclaven | despertado | 20 | 10764: 5, 11300: 3, 11301: 3 |
| gbzin | base | 13 | 410: 5, 440: 1, 764: 1, 3430: 5, 3435: 1 |
| gbzin | despertado | 13 | 3430: 4, 3435: 7, 10400: 8, 10410: 4, 10430: 8, 10440: 7, 10764: 5 |

## Kit (variante de perna contra o parado)

| kit | peça | comparada com | grossura | área | resultado |
|---|---|---|---|---|---|
| gutto/pecas | coxa_tras_apoio | coxa_tras+canela_tras | 87% | 99% | PASS |
| gutto/pecas | coxa_frente_camara | coxa_frente+canela_frente | 110% | 86% | PASS |
| gutto/pecas | coxa_frente_esticada | coxa_frente+canela_frente | 107% | 112% | PASS |
| gutto/pecas | coxa_frente_agachada | coxa_frente+canela_frente | 86% | 76% | PASS |
| hazaki/pecas | pernas_agachado | quadril e pernas do parado | 89% | 67% | PASS |
| hazaki/pecas | pernas_canela | quadril e pernas do parado | 125% | 68% | PASS |
| hazaki/pecas | coxa_frente_camara | coxa_frente+canela_frente | 76% | 81% | PASS |
| hazaki/pecas | coxa_frente_esticada | coxa_frente+canela_frente | 82% | 91% | PASS |
| pengaro/pecas | coxa_frente_camara | coxa_frente+canela_frente | 116% | 123% | PASS |
| pengaro/pecas | coxa_frente_esticada | coxa_frente+canela_frente | 152% | 167% | PASS |
| pengaro/pecas | coxa_frente_agachada | coxa_frente+canela_frente | 96% | 98% | PASS |
| raiclaven/pecas | coxa_frente_baixa | coxa_frente+canela_frente | 78% | 72% | PASS |
| raiclaven/pecas | coxa_frente_camara | coxa_frente+canela_frente | 74% | 64% | PASS |
| raiclaven/pecas | coxa_frente_esticada | coxa_frente+canela_frente | 83% | 88% | PASS |
| raiclaven_cliente/pecas | pernas_agachado | quadril e pernas do parado | 185% | 96% | PASS |

**18 reprovação(ões).**

- pengaro base: ação 400 (estado 400, agachado) levanta em 3 de 8 elementos; o pior sobe 48% do agachado ao em pé (elemento 5, sprite 49097,2)
- pengaro base: ação 410 (estado 410, agachado) levanta em 10 de 11 elementos; o pior sobe 102% do agachado ao em pé (elemento 7, sprite 49099,5)
- pengaro despertado: ação 10410 (estado 410, agachado) levanta em 7 de 8 elementos; o pior sobe 189% do agachado ao em pé (elemento 4, sprite 449,0)
- ck base: ação 11 (estado 11, agachado) levanta em 1 de 24 elementos; o pior sobe 52% do agachado ao em pé (elemento 16, sprite 48000,16)
- ck base: ação 400 (estado 400, agachado) levanta em 5 de 10 elementos; o pior sobe 77% do agachado ao em pé (elemento 2, sprite 48081,2)
- ck base: ação 410 (estado 410, agachado) levanta em 12 de 18 elementos; o pior sobe 126% do agachado ao em pé (elemento 6, sprite 48083,6)
- ck base: ação 440 (estado 440, agachado) levanta em 2 de 23 elementos; o pior sobe 62% do agachado ao em pé (elemento 12, sprite 48078,11)
- ck despertado: ação 10410 (estado 410, agachado) levanta em 5 de 8 elementos; o pior sobe 184% do agachado ao em pé (elemento 4, sprite 441,0)
- hazaki base: ação 410 (estado 410, agachado) levanta em 4 de 6 elementos; o pior sobe 102% do agachado ao em pé (elemento 2, sprite 1300,0)
- hazaki despertado: ação 410 (estado 410, agachado) levanta em 2 de 6 elementos; o pior sobe 159% do agachado ao em pé (elemento 2, sprite 1300,0)
- hazaki despertado: ação 4401 (estado 4401, agachado) levanta em 3 de 4 elementos; o pior sobe 96% do agachado ao em pé (elemento 3, sprite 64401,3)
- raiclaven base: ação 410 (estado 410, agachado) levanta em 13 de 17 elementos; o pior sobe 87% do agachado ao em pé (elemento 2, sprite 48032,2)
- gbzin base: ação 410 (estado 410, agachado) levanta em 5 de 8 elementos; o pior sobe 91% do agachado ao em pé (elemento 4, sprite 440,0)
- gbzin base: ação 440 (estado 440, agachado) levanta em 1 de 8 elementos; o pior sobe 171% do agachado ao em pé (elemento 7, sprite 460,0)
- gbzin despertado: ação 10400 (estado 400, agachado) levanta em 8 de 8 elementos; o pior sobe 65% do agachado ao em pé (elemento 2, sprite 432,0)
- gbzin despertado: ação 10410 (estado 410, agachado) levanta em 4 de 8 elementos; o pior sobe 143% do agachado ao em pé (elemento 4, sprite 440,0)
- gbzin despertado: ação 10430 (estado 430, agachado) levanta em 8 de 8 elementos; o pior sobe 66% do agachado ao em pé (elemento 6, sprite 450,0)
- gbzin despertado: ação 10440 (estado 440, agachado) levanta em 7 de 8 elementos; o pior sobe 70% do agachado ao em pé (elemento 6, sprite 459,0)

Avisos (especial do tipo agachado que sobe; olhar no vídeo):

- pengaro base: ação 764 (estado 764, agachado) levanta em 1 de 3 elementos; o pior sobe 47% do agachado ao em pé (elemento 0, sprite 7640,0)
- pengaro base: ação 1300 (estado 1300, agachado) levanta em 1 de 7 elementos; o pior sobe 112% do agachado ao em pé (elemento 6, sprite 49016,6)
- pengaro base: ação 1301 (estado 1301, agachado) levanta em 1 de 7 elementos; o pior sobe 112% do agachado ao em pé (elemento 6, sprite 49017,6)
- pengaro base: ação 3430 (estado 3430, agachado) levanta em 9 de 10 elementos; o pior sobe 103% do agachado ao em pé (elemento 8, sprite 49084,7)
- pengaro despertado: ação 3430 (estado 3430, agachado) levanta em 9 de 10 elementos; o pior sobe 194% do agachado ao em pé (elemento 4, sprite 49084,4)
- pengaro despertado: ação 10764 (estado 764, agachado) levanta em 5 de 5 elementos; o pior sobe 79% do agachado ao em pé (elemento 4, sprite 388,0)
- pengaro despertado: ação 11300 (estado 1300, agachado) levanta em 1 de 7 elementos; o pior sobe 134% do agachado ao em pé (elemento 6, sprite 556,0)
- pengaro despertado: ação 11301 (estado 1301, agachado) levanta em 1 de 7 elementos; o pior sobe 134% do agachado ao em pé (elemento 6, sprite 556,0)
- gutto base: ação 764 (estado 764, agachado) levanta em 3 de 3 elementos; o pior sobe 99% do agachado ao em pé (elemento 1, sprite 7640,1)
- gutto base: ação 1300 (estado 1300, agachado) levanta em 1 de 8 elementos; o pior sobe 53% do agachado ao em pé (elemento 7, sprite 548,0)
- gutto base: ação 1301 (estado 1301, agachado) levanta em 1 de 8 elementos; o pior sobe 53% do agachado ao em pé (elemento 7, sprite 548,0)
- gutto base: ação 3430 (estado 3430, agachado) levanta em 5 de 9 elementos; o pior sobe 177% do agachado ao em pé (elemento 3, sprite 1116,0)
- gutto despertado: ação 3430 (estado 3430, agachado) levanta em 8 de 9 elementos; o pior sobe 344% do agachado ao em pé (elemento 3, sprite 1116,0)
- gutto despertado: ação 10764 (estado 764, agachado) levanta em 6 de 6 elementos; o pior sobe 184% do agachado ao em pé (elemento 1, sprite 375,0)
- gutto despertado: ação 11300 (estado 1300, agachado) levanta em 3 de 8 elementos; o pior sobe 184% do agachado ao em pé (elemento 7, sprite 548,0)
- gutto despertado: ação 11301 (estado 1301, agachado) levanta em 3 de 8 elementos; o pior sobe 184% do agachado ao em pé (elemento 7, sprite 548,0)
- ck base: ação 3430 (estado 3430, agachado) levanta em 3 de 8 elementos; o pior sobe 94% do agachado ao em pé (elemento 5, sprite 441,0)
- ck despertado: ação 3430 (estado 3430, agachado) levanta em 6 de 8 elementos; o pior sobe 184% do agachado ao em pé (elemento 5, sprite 441,0)
- ck despertado: ação 10764 (estado 764, agachado) levanta em 3 de 5 elementos; o pior sobe 99% do agachado ao em pé (elemento 2, sprite 376,0)
- hazaki base: ação 764 (estado 764, agachado) levanta em 1 de 3 elementos; o pior sobe 52% do agachado ao em pé (elemento 0, sprite 7640,0)
- raiclaven base: ação 764 (estado 764, agachado) levanta em 2 de 3 elementos; o pior sobe 103% do agachado ao em pé (elemento 0, sprite 7640,0)
- raiclaven base: ação 3430 (estado 3430, agachado) levanta em 13 de 18 elementos; o pior sobe 90% do agachado ao em pé (elemento 5, sprite 48027,5)
- raiclaven despertado: ação 10764 (estado 764, agachado) levanta em 5 de 6 elementos; o pior sobe 99% do agachado ao em pé (elemento 1, sprite 375,0)
- raiclaven despertado: ação 11300 (estado 1300, agachado) levanta em 3 de 8 elementos; o pior sobe 57% do agachado ao em pé (elemento 6, sprite 547,0)
- raiclaven despertado: ação 11301 (estado 1301, agachado) levanta em 3 de 8 elementos; o pior sobe 57% do agachado ao em pé (elemento 6, sprite 547,0)
- gbzin base: ação 764 (estado 764, agachado) levanta em 1 de 3 elementos; o pior sobe 102% do agachado ao em pé (elemento 0, sprite 7640,0)
- gbzin base: ação 3430 (estado 3430, agachado) levanta em 5 de 8 elementos; o pior sobe 118% do agachado ao em pé (elemento 5, sprite 441,0)
- gbzin base: ação 3435 (estado 3435, agachado) levanta em 1 de 8 elementos; o pior sobe 171% do agachado ao em pé (elemento 7, sprite 460,0)
- gbzin despertado: ação 3430 (estado 3430, agachado) levanta em 4 de 8 elementos; o pior sobe 195% do agachado ao em pé (elemento 5, sprite 441,0)
- gbzin despertado: ação 3435 (estado 3435, agachado) levanta em 7 de 8 elementos; o pior sobe 70% do agachado ao em pé (elemento 6, sprite 459,0)
- gbzin despertado: ação 10764 (estado 764, agachado) levanta em 5 de 5 elementos; o pior sobe 109% do agachado ao em pé (elemento 2, sprite 376,0)


## Braço, cabeça e tronco (variante do kit contra o parado)

| kit | peça | comparada com | grossura | área | comprimento | resultado |
|---|---|---|---|---|---|---|
| ck/pecas | braco_frente_jab | braco_frente | 94% | 124% | 125% | PASS |
| ck/pecas | braco_frente_direto | braco_frente | 94% | 138% | 129% | PASS |
| ck/pecas | braco_frente_alto | braco_frente | 93% | 191% | 175% | PASS |
| ck/pecas | braco_tras_direto | braco_tras | 73% | 63% | 110% | FAIL grossura 73% |
| ck/pecas | braco_tras_overhand | braco_tras | 74% | 73% | 111% | FAIL grossura 74% |
| ck_e/pecas | braco_tras_aberta | braco_tras | 79% | 101% | 122% | PASS |
| ck_e/pecas | braco_tras_punho | braco_tras | 98% | 98% | 114% | PASS |
| ck_e/pecas | braco_tras_garrafa | braco_tras | 71% | 65% | 95% | FAIL grossura 71% |
| garanhao_47/pecas | braco_frente_frente | braco_frente | 92% | 91% | 87% | PASS |
| garanhao_47/pecas | braco_frente_alto | braco_frente | 81% | 112% | 111% | PASS |
| gbzin/pecas | braco_frente_recolhido | braco_frente | 101% | 87% | 81% | PASS |
| gbzin/pecas | braco_frente_tapa | braco_frente | 104% | 109% | 141% | PASS |
| gutto/pecas | braco_frente_cotovelo | braco_frente | 136% | 141% | 148% | PASS |
| gutto/pecas | braco_frente_esticado | braco_frente | 106% | 133% | 169% | PASS |
| hazaki/pecas | braco_tras_cruzado | braco_tras+antebraco_tras (aceita: conferido em 24/11: braço inteiro visto de lado, na grossura certa; o do parado é o bíceps contraído em escorço, que puxa a régua para cima) | 70% | 123% | 188% | PASS |
| hazaki/pecas | braco_frente_esticado | braco_frente | 98% | 136% | 184% | PASS |
| pengaro/pecas | braco_frente_punho | braco_frente | 81% | 67% | 83% | PASS |
| pengaro/pecas | braco_frente_esticado | braco_frente | 99% | 114% | 131% | PASS |
| pengaro/pecas | cabeca_foco | cabeca | 102% | 101% | 100% | PASS |
| pengaro/pecas | cabeca_esforco | cabeca | 100% | 101% | 100% | PASS |
| pengaro/pecas | cabeca_dor | cabeca | 102% | 102% | 100% | PASS |
| pengaro/pecas | cabeca_riso | cabeca | 101% | 107% | 101% | PASS |
| pengaro_e/pecas | braco_frente_aberta | braco_frente | 83% | 91% | 111% | PASS |
| pengaro_e/pecas | braco_frente_punho | braco_frente | 104% | 88% | 105% | PASS |
| pengaro_e/pecas | braco_frente_alto | braco_frente | 106% | 90% | 105% | PASS |
| pengaro_e/pecas | braco_frente_garra | braco_frente | 109% | 118% | 133% | PASS |
| raiclaven/pecas | braco_tras_frente | braco_tras+antebraco_tras | 61% | 88% | 99% | PASS |
| raiclaven/pecas | braco_tras_armado | braco_tras+antebraco_tras | 99% | 101% | 92% | PASS |
| raiclaven/pecas | braco_tras_alto | braco_tras+antebraco_tras | 100% | 112% | 119% | PASS |
| raiclaven/pecas | braco_tras_estocada | braco_tras+antebraco_tras | 61% | 75% | 105% | PASS |
| raiclaven/pecas | braco_frente_arremesso | braco_frente | 94% | 81% | 106% | PASS |
| raiclaven/pecas | braco_frente_cabelo | braco_frente | 85% | 88% | 93% | PASS |
| raiclaven/pecas | braco_frente_agarra | braco_frente | 95% | 91% | 103% | PASS |
| raiclaven/pecas | braco_frente_vassoura | braco_frente | 118% | 151% | 191% | PASS |
| raiclaven/pecas | braco_frente_varre | braco_frente | 126% | 140% | 139% | PASS |
| raiclaven/pecas | quadril_agachado | quadril e pernas do parado | 126% | 86% | 101% | PASS |

**4 reprovação(ões).**

- régua das pernas reprovou (detalhes acima)
- kit ck/pecas: braco_tras_direto contra braco_tras: grossura 73%
- kit ck/pecas: braco_tras_overhand contra braco_tras: grossura 74%
- kit ck_e/pecas: braco_tras_garrafa contra braco_tras: grossura 71%
