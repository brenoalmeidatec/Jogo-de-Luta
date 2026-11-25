# Régua do quadro final (25/11/2026)

Item 6 da auditoria do Breno (#32, 24/11): medir o que vai para a tela (o sprite do `.sff` na ação do `.air`), não só
as peças. Ferramenta: `python3 ferramentas/regua_sff.py [lutador ...] [--relatorio ARQ.md] [--ver PASTA]`.

**O que já foi consertado:** `--consertar` tapou os buracos transparentes que ficam no meio de uma área pintada
(o cenário aparecia por dentro da roupa): Pengaró 23 sprites, Hazak 3, CK 15, Gutto 6, Raiclaven 172 e Gbzin 27.
Ficou de fora, de propósito: o rastro em scanline (Diabo Loiro, agarrão do Hazak), vão entre garras, dedos e pontas de
corda, efeito solto (a meia-lua do vento) e as rachaduras violeta do peito no despertar do Pengaró (ação 2000), que
saíram transparentes e precisam ser **pintadas** de violeta (fila de imagens). Prévia em
`docs/mecanica-25-11/regua_buracos_antes_depois.png`. Os `gerar_<lutador>.py` chamam o conserto no fim.

**O que a tabela abaixo ainda mostra (para decidir, não é tudo defeito):**
- **congelado:** o quadro do contato segura igual por 10 a 17 tiques. Nos 4 lutadores do kit (CK, Gutto, Raiclaven,
  Gbzin) é quase todo golpe, a mesma estrutura de tempo (ver item A9, normais com cara própria). O Pengaró não tem,
  porque o "corpo firme com vida" mexe um pouco a cada quadro. O `normais_proprios.py` tirou o parado que vinha
  depois da caixa de ataque; o resto é o tempo do golpe pegando e precisa de um desenho de acompanhamento.
- **pedaço solto:** conferido no olho numa amostra de 10: é efeito desenhado junto do boneco, de propósito (coração e
  risquinhos de "!" nas poses 760 a 765, garrafa e pente jogados, brilho). Não é defeito.
- **salto de tamanho:** Gbzin 2000 (despertar) alterna pose curvada com o pau e pose de pé quadro sim, quadro não;
  vale olhar no jogo. Os outros são efeito.
- **rachadura** que sobrou: a do despertar do Pengaró e poucas outras que encostam na borda.

| lutador | ação | tipo | sprite | o que | aceito? |
|---|---|---|---|---|---|
| pengaro | 765 | pedaco_solto | 7640,3 | 3 pedaço(s), 1051 px, soltos do corpo só no elemento 1 | não |
| pengaro | 765 | pedaco_solto | 7640,6 | 3 pedaço(s), 950 px, soltos do corpo só no elemento 4 | não |
| pengaro | 765 | salto_tamanho | 7640,6 | altura 266 -> 365 -> 291 px (elemento 4) | não |
| pengaro | 830 | congelado | 7820,1 | elementos 2 a 4 quase iguais por 12 tiques | não |
| pengaro | 840 | congelado | 7810,1 | elementos 2 a 4 quase iguais por 12 tiques | não |
| pengaro | 2000 | rachadura | 597,0 | 65 px de buraco dentro do corpo (elemento 9) | não |
| pengaro | 2000 | rachadura | 598,0 | 70 px de buraco dentro do corpo (elemento 10) | não |
| pengaro | 2000 | rachadura | 601,0 | 53 px de buraco dentro do corpo (elemento 13) | não |
| pengaro | 2000 | rachadura | 602,0 | 215 px de buraco dentro do corpo (elemento 14) | não |
| pengaro | 2000 | rachadura | 603,0 | 321 px de buraco dentro do corpo (elemento 15) | não |
| pengaro | 2000 | rachadura | 604,0 | 455 px de buraco dentro do corpo (elemento 16) | não |
| pengaro | 2000 | pedaco_solto | 595,0 | 1 pedaço(s), 148 px, soltos do corpo só no elemento 7 | não |
| hazaki | 761 | pedaco_solto | 7600,6 | 1 pedaço(s), 63 px, soltos do corpo só no elemento 4 | não |
| hazaki | 764 | pedaco_solto | 7640,2 | 2 pedaço(s), 148 px, soltos do corpo só no elemento 3 | não |
| hazaki | 765 | pedaco_solto | 7640,5 | 2 pedaço(s), 476 px, soltos do corpo só no elemento 3 | não |
| hazaki | 841 | congelado | 1026,0 | elementos 10 a 11 quase iguais por 11 tiques | não |
| hazaki | 1201 | congelado | 1093,0 | elementos 4 a 5 quase iguais por 11 tiques | não |
| hazaki | 4582 | pedaco_solto | 7481,0 | 9 pedaço(s), 921 px, soltos do corpo só no elemento 1 | não |
| ck | 311 | congelado | 575,0 | elementos 2 a 5 quase iguais por 15 tiques | não |
| ck | 312 | congelado | 578,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| ck | 313 | congelado | 441,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| ck | 321 | congelado | 418,0 | elementos 6 a 7 quase iguais por 11 tiques | não |
| ck | 323 | congelado | 425,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| ck | 331 | congelado | 553,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| ck | 332 | congelado | 417,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| ck | 333 | congelado | 473,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| ck | 341 | congelado | 425,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| ck | 342 | congelado | 450,0 | elementos 6 a 7 quase iguais por 13 tiques | não |
| ck | 343 | congelado | 561,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| ck | 344 | congelado | 570,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| ck | 345 | congelado | 553,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| ck | 346 | congelado | 570,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| ck | 347 | congelado | 441,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| ck | 349 | congelado | 425,0 | elementos 3 a 5 quase iguais por 14 tiques | não |
| ck | 601 | congelado | 465,0 | elementos 4 a 5 quase iguais por 10 tiques | não |
| ck | 611 | congelado | 473,0 | elementos 4 a 5 quase iguais por 11 tiques | não |
| ck | 761 | rachadura | 7600,4 | 17 px de buraco dentro do corpo (elemento 2) | não |
| ck | 761 | rachadura | 7600,5 | 25 px de buraco dentro do corpo (elemento 3) | não |
| ck | 761 | rachadura | 7600,6 | 49 px de buraco dentro do corpo (elemento 4) | não |
| ck | 765 | pedaco_solto | 7640,3 | 2 pedaço(s), 362 px, soltos do corpo só no elemento 1 | não |
| ck | 765 | pedaco_solto | 7640,5 | 2 pedaço(s), 160 px, soltos do corpo só no elemento 3 | não |
| ck | 765 | pedaco_solto | 7640,6 | 3 pedaço(s), 519 px, soltos do corpo só no elemento 4 | não |
| ck | 830 | congelado | 7820,1 | elementos 2 a 4 quase iguais por 12 tiques | não |
| ck | 840 | congelado | 7810,1 | elementos 2 a 4 quase iguais por 12 tiques | não |
| ck | 1501 | congelado | 449,0 | elementos 3 a 4 quase iguais por 11 tiques | não |
| ck | 1701 | congelado | 407,0 | elementos 1 a 5 quase iguais por 15 tiques | não |
| ck | 1701 | congelado | 575,0 | elementos 6 a 9 quase iguais por 13 tiques | não |
| ck | 2000 | pedaco_solto | 592,0 | 3 pedaço(s), 306 px, soltos do corpo só no elemento 8 | não |
| ck | 2000 | pedaco_solto | 594,0 | 2 pedaço(s), 204 px, soltos do corpo só no elemento 10 | não |
| ck | 3200 | congelado | 538,0 | elementos 4 a 5 quase iguais por 11 tiques | não |
| ck | 3401 | congelado | 545,0 | elementos 3 a 4 quase iguais por 10 tiques | não |
| ck | 3403 | congelado | 417,0 | elementos 3 a 4 quase iguais por 11 tiques | não |
| ck | 3410 | congelado | 567,0 | elementos 2 a 4 quase iguais por 10 tiques | não |
| ck | 3411 | congelado | 568,0 | elementos 2 a 4 quase iguais por 10 tiques | não |
| ck | 3412 | congelado | 570,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| ck | 3413 | congelado | 441,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| ck | 3420 | congelado | 425,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| ck | 3421 | congelado | 416,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| ck | 3422 | congelado | 457,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| ck | 3423 | congelado | 545,0 | elementos 3 a 5 quase iguais por 14 tiques | não |
| ck | 3430 | congelado | 441,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| ck | 3431 | congelado | 561,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| ck | 3432 | congelado | 416,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| ck | 3433 | congelado | 608,0 | elementos 1 a 3 quase iguais por 12 tiques | não |
| ck | 3434 | congelado | 416,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| ck | 3435 | congelado | 457,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| ck | 3436 | congelado | 465,0 | elementos 3 a 4 quase iguais por 17 tiques | não |
| gutto | 302 | congelado | 561,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| gutto | 303 | congelado | 1118,0 | elementos 5 a 7 quase iguais por 10 tiques | não |
| gutto | 311 | congelado | 561,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| gutto | 312 | congelado | 417,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| gutto | 321 | congelado | 418,0 | elementos 7 a 8 quase iguais por 11 tiques | não |
| gutto | 322 | congelado | 450,0 | elementos 7 a 8 quase iguais por 13 tiques | não |
| gutto | 323 | congelado | 957,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| gutto | 331 | congelado | 957,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| gutto | 332 | congelado | 992,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| gutto | 333 | congelado | 1019,0 | elementos 5 a 7 quase iguais por 10 tiques | não |
| gutto | 341 | congelado | 957,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| gutto | 342 | congelado | 450,0 | elementos 7 a 8 quase iguais por 13 tiques | não |
| gutto | 343 | congelado | 561,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| gutto | 344 | congelado | 561,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| gutto | 345 | congelado | 992,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| gutto | 346 | congelado | 957,0 | elementos 4 a 6 quase iguais por 12 tiques | não |
| gutto | 347 | congelado | 1118,0 | elementos 5 a 7 quase iguais por 10 tiques | não |
| gutto | 348 | congelado | 1019,0 | elementos 5 a 7 quase iguais por 10 tiques | não |
| gutto | 349 | congelado | 545,0 | elementos 5 a 7 quase iguais por 14 tiques | não |
| gutto | 600 | congelado | 465,0 | elementos 4 a 5 quase iguais por 13 tiques | não |
| gutto | 601 | congelado | 465,0 | elementos 4 a 5 quase iguais por 10 tiques | não |
| gutto | 610 | congelado | 473,0 | elementos 4 a 5 quase iguais por 17 tiques | não |
| gutto | 611 | congelado | 473,0 | elementos 4 a 5 quase iguais por 11 tiques | não |
| gutto | 650 | congelado | 473,0 | elementos 5 a 6 quase iguais por 11 tiques | não |
| gutto | 761 | pedaco_solto | 7600,5 | 1 pedaço(s), 570 px, soltos do corpo só no elemento 3 | não |
| gutto | 761 | pedaco_solto | 7600,6 | 2 pedaço(s), 513 px, soltos do corpo só no elemento 4 | não |
| gutto | 830 | congelado | 7820,1 | elementos 2 a 4 quase iguais por 12 tiques | não |
| gutto | 840 | congelado | 7810,1 | elementos 2 a 4 quase iguais por 12 tiques | não |
| gutto | 1000 | pedaco_solto | 521,0 | 1 pedaço(s), 43 px, soltos do corpo só no elemento 2 | não |
| gutto | 1000 | pedaco_solto | 522,0 | 1 pedaço(s), 1052 px, soltos do corpo só no elemento 3 | não |
| gutto | 1001 | pedaco_solto | 521,0 | 1 pedaço(s), 43 px, soltos do corpo só no elemento 2 | não |
| gutto | 1001 | pedaco_solto | 522,0 | 1 pedaço(s), 1052 px, soltos do corpo só no elemento 3 | não |
| gutto | 1201 | congelado | 1050,0 | elementos 4 a 5 quase iguais por 11 tiques | não |
| gutto | 1300 | congelado | 545,0 | elementos 4 a 5 quase iguais por 14 tiques | não |
| gutto | 1301 | congelado | 545,0 | elementos 4 a 5 quase iguais por 14 tiques | não |
| gutto | 1401 | congelado | 561,0 | elementos 4 a 5 quase iguais por 11 tiques | não |
| gutto | 1501 | congelado | 417,0 | elementos 4 a 5 quase iguais por 11 tiques | não |
| gutto | 1600 | pedaco_solto | 521,0 | 1 pedaço(s), 43 px, soltos do corpo só no elemento 4 | não |
| gutto | 1600 | pedaco_solto | 522,0 | 1 pedaço(s), 1052 px, soltos do corpo só no elemento 5 | não |
| gutto | 1601 | pedaco_solto | 521,0 | 1 pedaço(s), 43 px, soltos do corpo só no elemento 4 | não |
| gutto | 1601 | pedaco_solto | 522,0 | 1 pedaço(s), 1052 px, soltos do corpo só no elemento 5 | não |
| gutto | 1701 | congelado | 410,0 | elementos 1 a 5 quase iguais por 15 tiques | não |
| gutto | 1701 | congelado | 957,0 | elementos 8 a 10 quase iguais por 10 tiques | não |
| gutto | 3200 | congelado | 1216,0 | elementos 6 a 7 quase iguais por 11 tiques | não |
| gutto | 3401 | congelado | 957,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| gutto | 3402 | congelado | 916,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| gutto | 3403 | congelado | 473,0 | elementos 6 a 8 quase iguais por 14 tiques | não |
| gutto | 3410 | congelado | 561,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| gutto | 3411 | congelado | 417,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| gutto | 3412 | congelado | 1118,0 | elementos 5 a 7 quase iguais por 10 tiques | não |
| gutto | 3413 | congelado | 1019,0 | elementos 5 a 7 quase iguais por 10 tiques | não |
| gutto | 3420 | congelado | 957,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| gutto | 3421 | congelado | 992,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| gutto | 3430 | congelado | 1118,0 | elementos 5 a 7 quase iguais por 10 tiques | não |
| gutto | 3432 | congelado | 957,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| gutto | 3434 | congelado | 417,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| gutto | 3435 | congelado | 457,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| raiclaven | 201 | rachadura | 571,0 | 23 px de buraco dentro do corpo (elemento 6) | não |
| raiclaven | 201 | rachadura | 572,0 | 68 px de buraco dentro do corpo (elemento 7) | não |
| raiclaven | 312 | congelado | 417,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| raiclaven | 321 | congelado | 418,0 | elementos 7 a 8 quase iguais por 11 tiques | não |
| raiclaven | 322 | congelado | 450,0 | elementos 6 a 7 quase iguais por 13 tiques | não |
| raiclaven | 322 | rachadura | 447,0 | 29 px de buraco dentro do corpo (elemento 1) | não |
| raiclaven | 322 | rachadura | 449,0 | 18 px de buraco dentro do corpo (elemento 3) | não |
| raiclaven | 323 | congelado | 425,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| raiclaven | 331 | congelado | 425,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| raiclaven | 332 | congelado | 911,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| raiclaven | 333 | congelado | 936,0 | elementos 5 a 7 quase iguais por 10 tiques | não |
| raiclaven | 341 | congelado | 425,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| raiclaven | 342 | congelado | 450,0 | elementos 6 a 7 quase iguais por 13 tiques | não |
| raiclaven | 345 | congelado | 911,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| raiclaven | 346 | congelado | 425,0 | elementos 4 a 6 quase iguais por 12 tiques | não |
| raiclaven | 348 | congelado | 936,0 | elementos 5 a 7 quase iguais por 10 tiques | não |
| raiclaven | 349 | congelado | 974,0 | elementos 5 a 7 quase iguais por 14 tiques | não |
| raiclaven | 610 | congelado | 473,0 | elementos 2 a 3 quase iguais por 17 tiques | não |
| raiclaven | 611 | congelado | 473,0 | elementos 2 a 3 quase iguais por 11 tiques | não |
| raiclaven | 650 | congelado | 473,0 | elementos 3 a 4 quase iguais por 11 tiques | não |
| raiclaven | 700 | rachadura | 407,0 | 14 px de buraco dentro do corpo (elemento 13) | não |
| raiclaven | 700 | rachadura | 828,0 | 28 px de buraco dentro do corpo (elemento 17) | não |
| raiclaven | 700 | rachadura | 408,0 | 12 px de buraco dentro do corpo (elemento 19) | não |
| raiclaven | 700 | rachadura | 832,0 | 21 px de buraco dentro do corpo (elemento 21) | não |
| raiclaven | 700 | rachadura | 841,0 | 50 px de buraco dentro do corpo (elemento 30) | não |
| raiclaven | 700 | pedaco_solto | 827,0 | 1 pedaço(s), 137 px, soltos do corpo só no elemento 16 | não |
| raiclaven | 705 | pedaco_solto | 827,0 | 1 pedaço(s), 137 px, soltos do corpo só no elemento 26 | não |
| raiclaven | 705 | pedaco_solto | 407,0 | 1 pedaço(s), 141 px, soltos do corpo só no elemento 28 | não |
| raiclaven | 705 | pedaco_solto | 823,0 | 1 pedaço(s), 141 px, soltos do corpo só no elemento 30 | não |
| raiclaven | 761 | pedaco_solto | 7600,3 | 3 pedaço(s), 1110 px, soltos do corpo só no elemento 1 | não |
| raiclaven | 761 | pedaco_solto | 7600,5 | 1 pedaço(s), 49 px, soltos do corpo só no elemento 3 | não |
| raiclaven | 761 | pedaco_solto | 7600,7 | 1 pedaço(s), 97 px, soltos do corpo só no elemento 5 | não |
| raiclaven | 765 | pedaco_solto | 7640,5 | 3 pedaço(s), 290 px, soltos do corpo só no elemento 3 | não |
| raiclaven | 765 | pedaco_solto | 7640,6 | 3 pedaço(s), 271 px, soltos do corpo só no elemento 4 | não |
| raiclaven | 1300 | congelado | 547,0 | elementos 4 a 5 quase iguais por 14 tiques | não |
| raiclaven | 1301 | congelado | 547,0 | elementos 4 a 5 quase iguais por 14 tiques | não |
| raiclaven | 1501 | congelado | 857,0 | elementos 4 a 5 quase iguais por 11 tiques | não |
| raiclaven | 1700 | pedaco_solto | 407,0 | 2 pedaço(s), 842 px, soltos do corpo só no elemento 2 | não |
| raiclaven | 1700 | pedaco_solto | 408,0 | 1 pedaço(s), 333 px, soltos do corpo só no elemento 3 | não |
| raiclaven | 3401 | congelado | 425,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| raiclaven | 3402 | congelado | 840,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| raiclaven | 3402 | pedaco_solto | 407,0 | 2 pedaço(s), 842 px, soltos do corpo só no elemento 2 | não |
| raiclaven | 3402 | pedaco_solto | 830,0 | 1 pedaço(s), 332 px, soltos do corpo só no elemento 3 | não |
| raiclaven | 3403 | congelado | 474,0 | elementos 4 a 6 quase iguais por 14 tiques | não |
| raiclaven | 3411 | congelado | 417,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| raiclaven | 3413 | congelado | 936,0 | elementos 5 a 7 quase iguais por 10 tiques | não |
| raiclaven | 3420 | congelado | 425,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| raiclaven | 3421 | congelado | 911,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| raiclaven | 3432 | congelado | 425,0 | elementos 5 a 7 quase iguais por 12 tiques | não |
| raiclaven | 3434 | congelado | 417,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| gbzin | 210 | congelado | 571,0 | elementos 6 a 7 quase iguais por 15 tiques | não |
| gbzin | 215 | congelado | 571,0 | elementos 6 a 7 quase iguais por 13 tiques | não |
| gbzin | 246 | congelado | 552,0 | elementos 1 a 2 quase iguais por 17 tiques | não |
| gbzin | 260 | congelado | 552,0 | elementos 3 a 6 quase iguais por 12 tiques | não |
| gbzin | 311 | congelado | 575,0 | elementos 2 a 5 quase iguais por 15 tiques | não |
| gbzin | 312 | congelado | 578,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| gbzin | 313 | congelado | 441,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| gbzin | 321 | congelado | 418,0 | elementos 6 a 7 quase iguais por 11 tiques | não |
| gbzin | 323 | congelado | 424,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| gbzin | 331 | congelado | 552,0 | elementos 2 a 5 quase iguais por 16 tiques | não |
| gbzin | 332 | congelado | 417,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| gbzin | 333 | congelado | 473,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| gbzin | 341 | congelado | 424,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| gbzin | 342 | congelado | 450,0 | elementos 6 a 7 quase iguais por 13 tiques | não |
| gbzin | 343 | congelado | 560,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| gbzin | 344 | congelado | 570,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| gbzin | 345 | congelado | 552,0 | elementos 2 a 5 quase iguais por 16 tiques | não |
| gbzin | 346 | congelado | 570,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| gbzin | 347 | congelado | 441,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| gbzin | 349 | congelado | 424,0 | elementos 3 a 5 quase iguais por 14 tiques | não |
| gbzin | 600 | congelado | 465,0 | elementos 3 a 4 quase iguais por 13 tiques | não |
| gbzin | 601 | congelado | 465,0 | elementos 4 a 5 quase iguais por 10 tiques | não |
| gbzin | 610 | congelado | 474,0 | elementos 4 a 5 quase iguais por 17 tiques | não |
| gbzin | 611 | congelado | 474,0 | elementos 4 a 5 quase iguais por 11 tiques | não |
| gbzin | 650 | congelado | 474,0 | elementos 3 a 4 quase iguais por 11 tiques | não |
| gbzin | 705 | congelado | 408,0 | elementos 3 a 4 quase iguais por 17 tiques | não |
| gbzin | 765 | rachadura | 7640,3 | 29 px de buraco dentro do corpo (elemento 1) | não |
| gbzin | 810 | congelado | 441,0 | elementos 19 a 21 quase iguais por 14 tiques | não |
| gbzin | 841 | congelado | 423,0 | elementos 5 a 6 quase iguais por 14 tiques | não |
| gbzin | 1200 | congelado | 441,0 | elementos 3 a 4 quase iguais por 11 tiques | não |
| gbzin | 1201 | congelado | 441,0 | elementos 3 a 4 quase iguais por 11 tiques | não |
| gbzin | 1300 | congelado | 535,0 | elementos 2 a 3 quase iguais por 26 tiques | não |
| gbzin | 1301 | congelado | 535,0 | elementos 2 a 3 quase iguais por 32 tiques | não |
| gbzin | 1310 | congelado | 538,0 | elementos 3 a 4 quase iguais por 11 tiques | não |
| gbzin | 1401 | congelado | 545,0 | elementos 3 a 4 quase iguais por 11 tiques | não |
| gbzin | 1501 | congelado | 449,0 | elementos 3 a 4 quase iguais por 11 tiques | não |
| gbzin | 1701 | congelado | 407,0 | elementos 1 a 5 quase iguais por 15 tiques | não |
| gbzin | 1701 | congelado | 575,0 | elementos 6 a 9 quase iguais por 13 tiques | não |
| gbzin | 2000 | congelado | 587,0 | elementos 9 a 11 quase iguais por 21 tiques | não |
| gbzin | 2000 | salto_tamanho | 584,0 | altura 227 -> 435 -> 227 px (elemento 4) | não |
| gbzin | 2000 | salto_tamanho | 585,0 | altura 435 -> 227 -> 435 px (elemento 5) | não |
| gbzin | 2000 | salto_tamanho | 586,0 | altura 227 -> 435 -> 227 px (elemento 6) | não |
| gbzin | 2000 | salto_tamanho | 585,0 | altura 435 -> 227 -> 435 px (elemento 7) | não |
| gbzin | 2000 | salto_tamanho | 586,0 | altura 227 -> 435 -> 227 px (elemento 8) | não |
| gbzin | 3000 | salto_tamanho | 371,0 | altura 236 -> 312 -> 256 px (elemento 13) | não |
| gbzin | 3200 | congelado | 538,0 | elementos 4 a 5 quase iguais por 11 tiques | não |
| gbzin | 3401 | congelado | 544,0 | elementos 3 a 5 quase iguais por 13 tiques | não |
| gbzin | 3403 | congelado | 417,0 | elementos 3 a 4 quase iguais por 11 tiques | não |
| gbzin | 3410 | congelado | 567,0 | elementos 2 a 4 quase iguais por 10 tiques | não |
| gbzin | 3411 | congelado | 568,0 | elementos 2 a 4 quase iguais por 10 tiques | não |
| gbzin | 3412 | congelado | 570,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| gbzin | 3413 | congelado | 441,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| gbzin | 3420 | congelado | 424,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| gbzin | 3421 | congelado | 417,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| gbzin | 3422 | congelado | 457,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| gbzin | 3423 | congelado | 544,0 | elementos 3 a 5 quase iguais por 14 tiques | não |
| gbzin | 3430 | congelado | 441,0 | elementos 4 a 6 quase iguais por 10 tiques | não |
| gbzin | 3431 | congelado | 561,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| gbzin | 3432 | congelado | 417,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| gbzin | 3433 | congelado | 512,0 | elementos 1 a 3 quase iguais por 12 tiques | não |
| gbzin | 3434 | congelado | 417,0 | elementos 3 a 5 quase iguais por 10 tiques | não |
| gbzin | 3435 | congelado | 457,0 | elementos 3 a 5 quase iguais por 12 tiques | não |
| gbzin | 3436 | congelado | 465,0 | elementos 3 a 4 quase iguais por 17 tiques | não |
