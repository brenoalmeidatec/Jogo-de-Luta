# Registro da fila de arte no ChatGPT

> Cópia versionada do registro que os agentes do Claude mantêm durante a geração das folhas: procedimento que funciona,
> o que mudou na interface e a tabela folha por folha. Copiado do rascunho da sessão em 2026-11-11; o índice do método
> está em [`../metodo-do-claude.md`](../metodo-do-claude.md). Caminhos `scratchpad/...` são da máquina do Alisson e não
> existem no repositório.

# Registro da fila arcade (lotes 1-3)

| personagem | folha | medidas | refeita? | defeito aceito | commit |
|---|---|---|---|---|---|
| Pengaró | soco (refeito, lote 1) | 8q, pés 520-521, pele 22.9, preto 2.04, borda 0,0 | não | — | f21788c |
| Pengaró | ginga (lote 2) | 8q, pés 518-520, pele 23.2, preto 1.81, borda 0,0 | não | ginga pouco ampla (passo curto, braços pouco cruzam) | 89dbd1a |
| Gutto | ginga (lote 1) | 8q, pés 574, pele 19.7, preto 3.21, borda 0,0 (ref_gutto mede 17.6) | sim, 1x (1ª: pele 14.5, preto 8.25) | — | cdf8a98 |
(nota: faixa de pele usada no aceite do Gutto via __mede: 16-26°, ref atual mede 17.6°)
| Gutto | anda (lote 1) | 8q, pés 572, pele 20.2, preto 3.25, borda 0,0 | sim, 1x (1ª: pele 13.4) | — | cdf8a98 |
(a partir daqui o Gutto recebe 2 anexos: gutto_ginga arcade + ref_gutto antiga, porque só a arcade deixou a pele vermelha demais)
| Gutto | defesa (lote 1) | 8q, pés 573, pele 20.7, preto 3.94, borda 0,0 | não | prompt da fila sem a canela levantada (decisão do Breno pendente na fila) | cdf8a98 |
| Gutto | agachado (lote 1) | 8q, pés 574, pele 17.3, preto 4.01, borda 0,0 | não | — | cdf8a98 |
| Raiclaven | ginga (lote 1) | 8q, pés 578, pele 11.0, preto 7.07, borda 0,0 (ref antiga mede 10.7) | não | preto puro 7% (roupa) | e96a9a3 |
| Raiclaven | anda (lote 1) | 8q, pés 577, pele 11.5, preto 7.16, borda 0,0 | reenviada (1º envio saiu sem texto) | preto puro 7% | e96a9a3 |
| Raiclaven | soco (lote 1) | 1ª: 4 "quadros" (pente encosta no quadro vizinho), pés 578, pele 13.2, preto 4.09 | sim, 2x (r1: figura 40% menor; r2: separada mas jab quase sem extensão) | ficou a 1ª: quadros 4-6 encostam no vizinho pelo pente; r2 descartada | e96a9a3 |
| Raiclaven | defesa (lote 1) | 7 "quadros" medidos (1º e 2º quase encostam; no olho separados), pés 576-577, pele 8.7, preto 7.93 | não | pele no piso da faixa (8.7); quadros 1-2 muito próximos | e96a9a3 |
| Hazaki | parado (lote 1) | 8q, pés 538, pele 23.5, preto 1.88, borda 0,0 (ref: karate.png via webp) | não | — | 415a069 |
| Hazaki | anda (lote 1) | 8q, pés 535-536, pele 24.3, preto 1.75, borda 0,0 | reenviada (1º envio: DOM velha, texto não entrou) | — | 415a069 |
| Hazaki | defesa (lote 1) | 8q, pés 538, pele 22.6, preto 2.39, borda 0,0 | não | — | 415a069 |
| Hazaki | soco (lote 1) | 8q, pés 537, pele 24.5, preto 1.67, borda 0,0; jab estende bem nos quadros 4-6 | não | — | 415a069 |
| Pengaró | defesa (lote 2) | 8q, pés 570-571, pele 22.6, preto 2.30, borda 0,0 | reenviada (1º envio ficou no composer sem sair) | — | 89dbd1a |
| Pengaró | apanha (lote 2) | 8q, pés 520, pele 17.9, preto 1.96, borda 0,0 | não | — | 89dbd1a |
| Pengaró | pulo (lote 2) | 8q, pés 322-562 (pulo), pele 18.0, preto 1.83, borda 0,0 | não | — | 89dbd1a |
| Pengaró | ar_soco (lote 2) | 8q, pés 473-484 (aéreo), pele 17.7, preto 1.92, borda 0,0 | não | soco aéreo com extensão curta | 89dbd1a |
| Pengaró | queda (lote 2) | 8q, pés 425-476 (queda), pele 23.6, preto 0.68, borda 0,0 | não | — | 89dbd1a |
| Pengaró | levanta (lote 2) | 8q, pés 437-495 (kip-up), pele 23.0, preto 1.08, borda 0,0 (refs pilot_soco + agachado) | não | — | 89dbd1a |
| Pengaró | martelo (lote 2) | 8q, pés 519, pele 19.0, preto 1.35, borda 0,0 (cotovelada) | não | — | 89dbd1a |
| Pengaró | afastar (lote 2) | 8q, pés 519, pele 19.1, preto 1.36, borda 0,0 | não | — | 89dbd1a |
| Pengaró | cabecada (lote 2) | 8q, pés 493-531 (sobe no ar), pele 22.5, preto 1.88, borda 0,0 | não | saiu sem o anexo agachado (esqueci); agachamento ficou coerente | 89dbd1a |
| Pengaró | rasteirinha (lote 2) | r2: 8q, pés 484-485, pele 21.4, preto 0.76, borda 0,0 | sim, 2x (1ª: perna encosta no quadro 6 = 7q; r1: figura 20% menor) | ficou a r2 | 89dbd1a |
| Pengaró | rasteira (lote 2) | 8q, pés 500-501, pele 20.0, preto 1.65, borda 0,0 | não | muito parecida com a rasteirinha (giro pouco visível) | 89dbd1a |
| Pengaró | bicicleta (lote 2) | 8q, pés 443-471 (aéreo), pele 21.4, preto 1.31, borda 0,0 | não | — | 89dbd1a |
| Gutto | apanha (lote 2) | 8q, pés 573, pele 20.1, preto 3.00, borda 0,0 | não | — | 86afd3a |
| Gutto | soco (lote 2) | r1: 8q, pés 550, pele 24.2, preto 3.77, borda 0,0; braço segue estendido no q6 | sim, 1x (1ª: luva encosta no vizinho = 5q) | r1 tem figura ~9% mais baixa (313 px vs 345 da ginga) | 86afd3a |
| Gutto | chute_baixo (lote 2) | 8q, pés 571-573, pele 19.7, preto 4.06, borda 0,0 | não | — | 86afd3a |
| Gutto | chute_alto (lote 2) | r2: 8q, pés 572, pele 22.7, preto 2.49, borda 0,0, altura 340 px | sim, 2x (1ª: pé encosta = 7q; r1: figura 21% menor) | ficou a r2 (prompt da fila de novo + "mesmo tamanho da 1ª folha anexada") | 86afd3a |
| Gutto | martelo (lote 2) | 8q, pés 573, pele 23.2, preto 3.99, borda 0,0 | não | cotovelada pouco projetada (contato discreto) | 86afd3a |
| Gutto | pulo (lote 2) | 8q, pés 379-613 (pulo), pele 19.3, preto 3.20, borda 0,0 | não | — | 86afd3a |
| Gutto | queda (lote 2) | r1: 8q, pés 424-513 (queda), pele 24.4, preto 1.90, borda 0,0 | sim, 1x (1ª: quadros deitados encostam = 6q) | — | 86afd3a |
| Gutto | levanta (lote 2) | 8q, pés 555-564 (do chão ao pé), pele 21.3, preto 3.65, borda 0,0 | não | — | 86afd3a |
| Gutto | baixo_soco (lote 2) | 8q, pés 550, pele 19.5, preto 2.89, borda 0,0 (refs + gutto_agachado) | não | — | 86afd3a |
| Gutto | rasteirinha (lote 2) | 8q, pés 561, pele 18.9, preto 4.07, borda 0,0 (refs + gutto_agachado) | não | — | 86afd3a |
| Gutto | cabecada (lote 2) | 8q, pés 572, pele 19.4, preto 2.35, borda 0,0 (joelhada subindo; refs + gutto_agachado) | não | joelhada sem sair do chão | 86afd3a |
| Gutto | rasteira (lote 2) | 8q, pés 522, pele 19.8, preto 4.57, borda 0,0 (refs + gutto_agachado) | não | — | 86afd3a |
| Gutto | afastar (lote 2) | 8q, pés 574, pele 18.2, preto 5.29, borda 0,0 | não | — | 86afd3a |
| Gutto | bicicleta (lote 2) | 8q, pés 495-573 (aéreo), pele 20.9, preto 4.28, borda 0,0 (joelhada aérea) | não | — | 86afd3a |
| Gutto | ar_soco (lote 2) | 8q, pés 528-557 (aéreo), pele 16.6, preto 2.54, borda 0,0 (cotovelada aérea) | não | pele 16.6, abaixo da faixa nominal 17 (dentro da 16-26 usada) | 86afd3a |
| Raiclaven | apanha (lote 2) | r1: 8q, pés 576-577, pele 14.3, preto 7.81, borda 0,0 | sim, 1x (1ª: quadros 4-5 encostam = 7q) | preto puro ~8% (roupa) | adf7fdc |
| Raiclaven | agachado (lote 2) | 8q, pés 576-577, pele 11.4, preto 7.71, borda 0,0 | não | — (vira ref das folhas agachadas) | adf7fdc |
| Raiclaven | pulo (lote 2) | 8q, pés 435-592 (pulo), pele 11.7, preto 9.20, borda 0,0 | não | preto puro 9% (roupa) | adf7fdc |
| Raiclaven | chute_alto (lote 2) | r1: 8q, pés 539-540, pele 12.9, preto 8.40, borda 0,0 | sim, 1x (1ª: pé/tesoura encostam = 6q) | — | adf7fdc |
| Raiclaven | martelo (lote 2) | r1: 8q, pés 582, pele 10.2, preto 6.30, borda 0,0 | sim, 1x (1ª: tesoura encosta = 7q) | — | adf7fdc |
| Raiclaven | chute_baixo (lote 2) | 8q, pés 574-575, pele 11.2, preto 6.25, borda 0,0 | não | — | adf7fdc |
| Raiclaven | baixo_soco (lote 2) | 8q, pés 568, pele 13.7, preto 9.51, borda 0,0 (refs + raiclaven_agachado) | não | pente estende pouco; preto 9.5% | adf7fdc |
| Raiclaven | cabecada (lote 2) | 8q, pés 632-635, pele 8.1, preto 5.93, borda 0,0 (sobe com a tesoura erguida) | não | pele no piso da faixa (8.1); figura posicionada mais baixa na folha | adf7fdc |
| Raiclaven | rasteirinha (lote 2) | 8q, pés 575, pele 12.4, preto 8.90, borda 0,0 (refs + raiclaven_agachado) | não | perna desliza pouco | adf7fdc |
| Raiclaven | rasteira (lote 2) | r1: 8q, pés 575, pele 14.2, preto 8.54, borda 0,0 | sim, 1x (1ª: vassoura longa encosta = 5q) | VASSOURA NOVA (objeto que não existia): na r1 virou vassourinha de mão e a varrida ficou pequena | adf7fdc |
| Raiclaven | queda (lote 2) | r1: 8q, pés 441-546 (queda), pele 11.7, preto 5.61, borda 0,0 | sim, 1x (1ª: 7q) | — | adf7fdc |
| Raiclaven | levanta (lote 2) | r1: 7 "quadros" medidos, pés 553-559, pele 9.8, preto 8.31, borda 0,0 | sim, 1x (1ª: 7q e pele 7.0, fora da faixa) | tesoura dos quadros 3-4 quase encosta (7q medidos) | adf7fdc |
| Raiclaven | ar_soco (lote 2) | r1: 8q, pés 496-511 (aéreo), pele 12.1, preto 8.63, borda 0,0 | sim, 1x (1ª: 7q) | — | adf7fdc |
| Raiclaven | bicicleta (lote 2) | r1: 7 "quadros" medidos, pés 511-559 (aéreo), pele 11.9, preto 5.50, borda 0,0 | sim, 1x (1ª também 7q, chute mais fraco) | pé do chute dos quadros 4-6 encosta no vizinho | adf7fdc |
| Raiclaven | afastar (lote 2) | 8q, pés 576, pele 9.3, preto 9.58, borda 0,0 | não | preto 9.6% (roupa) | adf7fdc |
| Hazaki | agachado (lote 2) | 8q, pés 536, pele 24.3, preto 1.50, borda 0,0 | não | — (vira ref das folhas agachadas) | |
| Hazaki | chute (lote 2) | 8q, pés 537-538, pele 25.4, preto 1.62, borda 0,0 | não | — | |
| Hazaki | apanha (lote 2) | r1: 7 "quadros" medidos, pés 454-527 (cai), pele 25.0, preto 1.58, borda 0,0 | sim, 1x (1ª também 7q) | quadros 5-6 (caindo) quase encostam; o prompt da fila manda cair no fim | |
| Hazaki | pulo (lote 2) | 8q, pés 310-595 (pulo), pele 25.3, preto 1.70, borda 0,0 | não | — | |
| Hazaki | baixo_soco (lote 2) | 8q, pés 520-521, pele 23.6, preto 1.57, borda 0,0 (refs + hazaki_agachado) | não | — | |
| Hazaki | rasteira (lote 2) | 8q, pés 486-488, pele 24.4, preto 1.41, borda 0,0 (refs + hazaki_agachado) | não | — | |
| Hazaki | ascensao (lote 2) | 8q, pés 538-539, pele 29.6, preto 4.11, borda 0,0 (refs + hazaki_agachado) | não | pele no teto da faixa (29.6) | |
| Hazaki | queda (lote 2) | 8q, pés 406-418 (deitado), pele 25.6, preto 2.32, borda 0,0 | não | quase tudo deitado (é o que o prompt pede) | |
| Hazaki | levanta (lote 2) | 8q, pés 530-533, pele 25.3, preto 2.17, borda 0,0 | não | — | |
| Hazaki | ar_soco (lote 2) | 8q, pés 475-496 (no ar), pele 26.2, preto 2.33, borda 0,0 | não | — | |
| Hazaki | ar_chute (lote 2) | 8q, pés 455-472 (no ar), pele 26.8, preto 2.55, borda 0,0 | não | — | |
| Hazaki | lote 2 (11 folhas) | commit f3e27bb | | | f3e27bb |

## Hazak, lote 1 de `docs/arcade/fila_hazak.md` (2026-11-11)

TRAVOU ANTES DE GERAR: o navegador embutido abriu chatgpt.com deslogado (botões "Entrar"/"Cadastre-se grátis", nenhum
chat na barra lateral, sem cookie de sessão; conferido em duas cargas da página). Login é do usuário. Nada gerado, nada
baixado, nenhum commit.

Pendentes (19): novas `corrida`, `vira`, `recuo`, `defesa_baixa`, `vitima_agarrado`, `vitima_arremessado`, `soco_reto`,
`chute_baixo`, `chute_lateral`, `joelhada_baixo`, `chute_canela`, `rasteira_arco`, `ar_cotovelo`, `ar_joelho`,
`ar_chute_duplo`; refazer `queda`, `ar_soco`; retoque `defesa` (teal no pulso da frente, quadros 2-6), `levanta`
(quadros 3 e 4).

### Retomada (2026-11-11, depois do login): lote 1 gerado, commit 30c5110 (push em origin/hazak)

Chat novo "Hazak — arcade": https://chatgpt.com/c/6af456a7-ff90-83e8-838e-510e94885dc5 (conta logada não tinha chat arcade do Hazak).
Todas 2172x724, 8 quadros separados medidos por coluna magenta, borda 100% magenta. "pé" = linha do chão em px (parado = 537).

| Folha | Medida | Refez? | Observação |
|---|---|---|---|
| corrida | 8q, alt 219-294, pé 546 | sim, 2x | 1ª: teal nos dois pulsos (q1,2,5,6), q1 cortado na borda, q5-8 cópia de q1-4. 2ª: q4/q8 sem teal. Salva a 3ª: **q6 sem teal** (braço de trás só com atadura branca) |
| vira | 8q, em pé 342-344, agachado 277-280, pé 536 | não | ok; q4 e q8 de frente para a esquerda, como pede o MOTION |
| recuo | 8q, alt 276-342, pé 535 | não | ok |
| defesa_baixa | 8q, alt 228-260, pé 534 | sim, 2x | **q3 sem teal** nas três; salva a 1ª (a 3ª pôs teal nos dois pulsos no q3 e desceu o chão para 566) |
| queda (refeita) | 8q, corpo deitado 255 px, pé 485-497 | sim, 1x | 1ª: corpo de 231 px. Limite: célula tem 271 px, então deitado não chega nos ~340 px da altura dele (a antiga tinha 250) |
| vitima_agarrado | 8q, corpos 309-358 px, células desiguais | sim, 1x | salva a 1ª: **q8 sem teal** (q5 de costas). A 2ª encostou q7 e q8 |
| vitima_arremessado | 8q, corpos deitados ~256-275 px | não | escala dos deitados menor (limite da célula); q7 só mostra o pulso da frente |
| soco_reto | 8q, alt 319-345, pé 535-537 | não | ok |
| chute_baixo | 8q, alt 320-344, pé 535 | não | ok |
| chute_lateral | 8q, alt 321-343, pé 534 | não | ok |
| joelhada_baixo | 8q, agachado 207-229, em pé 338-340, pé 553 | sim, 1x | 1ª: q3 sem teal e q4-6 esticados (402 px). Salva a 2ª: teal fraca/duvidosa em q2 e q7; chão 16 px abaixo |
| chute_canela | 8q, alt 229-236, pé 502 | não | ok; chão 35 px acima do parado |
| rasteira_arco | 8q, alt 185-238, pé 498-502 | não | ok (conferida depois no arquivo) |
| ar_soco (refeita) | 8q, alt 271-323 | não | ok: martelo só com o braço da frente, teal fica atrás |
| ar_cotovelo | 8q, alt 279-311 | não | ok; alcance do cotovelo curto |
| ar_joelho | 8q, alt 281-336 | não | ok; mão de trás em lilás claro atrás do tronco em q4-6 |
| ar_chute_duplo | 8q, alt 267-324 | não | ok; os dois chutes parecem a mesma perna |
| defesa (retoque) | 8q, alt 313-343, pé 536 | não | redesenhada com defesa.png + parado.png anexadas; teal saiu do pulso da frente em q2-6; **q7 sem teal** |
| levanta (retoque) | 8q, deitado 339 px, em pé 337-338, pé 529-532, células desiguais | não | redesenhada com levanta.png + parado.png; uma teal por quadro |

Como foi feito desta vez (mudou em relação à rodada anterior):
- A interface do ChatGPT mudou: enviar é `button[aria-label="Enviar"]`; parar é `button[aria-label="Parar"]`, mas existe um "Parar" ESCONDIDO o tempo todo, então só conta se `offsetParent !== null`. Imagem gerada: `main img[alt*="gerada"]`.
- Referência sem base64 no contexto: página local (127.0.0.1) lê os PNG e guarda em `window.name`; ao navegar a mesma aba para chatgpt.com o `window.name` continua lá (9 MB passaram) e vira `File` → `DataTransfer` → `input[type=file][accept="image/*"]`. `window.open` não serve: navega a própria aba.
- `javascript_tool` estoura em 45 s: esperas de no máximo ~35 s por chamada.
- Download: um `.tar` só (42151936 bytes). O `.tmp` de tamanho exato apareceu em Downloads e foi copiado antes de qualquer clique; ficou lá `cb347129-0499-439e-8715-37c1dbabffe4.tmp` (do diálogo "Salvar como" em aberto).
- `baixar_folhas.py` grava em `quadros/folhas`; aqui a extração foi por script próprio, bytes crus do PNG (RGBA), direto em `folhas_arcade`.

## Pendência (2026-11-11): Pengaró borrado
Dono achou o Pengaró bem borrado no teste filmado na sandbox. Depois do pente fino de anatomia, conferir quadro a quadro
(ginga_fluida/anda_fluida são entremeios de fluxo óptico = suspeito nº 1; também checar escala/filtro do vídeo e do motor).
Se continuar borrado, investigar e corrigir.

### Hazak, lotes 2, 3 e 4 + três folhas do lote 1 refeitas (2026-11-11, mesmo chat)

Commits (todos com push em origin/hazak): 47848a7 (lote 1, 3 refeitas), 43ccdcd (lote 2, 15), e1d8d50 (lote 3, 16), b7e8fc9 (lote 4, 8).
Prompt: base + frase de células + "exactly two arms..." + frase fixa "The teal wristband is on the rear wrist in EVERY one of the 8 frames..." no fim do MOTION (fora obj_ e patroa).

Lote 1 refeitas: `joelhada_baixo` e `defesa` agora com teal nos 8 quadros (aprovadas); `vitima_agarrado` 3ª tentativa: q2 sem teal (limite atingido).

Lote 2 (15): aprovadas de primeira jab_duplo, cutucao, tapa_costas (q3 de costas, pulsos escondidos), cruzado, calcada_levantada, chute_alto_rajada, chute_giratorio, chute_gancho, cotovelo_faixa, cutucao_recuo, coice. Refeitas 1x e aprovadas: cotovelada (1ª: q4-7 sem teal e cotovelo ilegível), tesoura (1ª: q2 e q5 sem teal), machado e machado_curto (1ª: q5-7 sem teal).

Lote 3 (16): aprovadas de primeira punho_chao (escala ~6% menor, chão em 514), estatueta_arremesso, giro_garagem, rolada_tatame (q4 com teal nos dois pulsos), voadora (corpo horizontal ~270 px, limite da célula), guarda_aco, agarrao_abraco, pose_super, obj_lasca e obj_estatueta (objetos com ~190 px, o dobro do antebraço pedido). Refeitas 1x e aprovadas: ascensao (gi na cor da parado; 1ª sem teal em q1-4 e q7), sobe_chutando (1ª ~10% menor e q8 sem teal), passagem_rapida (1ª com quadros encostados, 5 segmentos; a salva ficou compacta, com menos variação de pose). Salvas com defeito: agarrao_perna (1ª: q7-8 sem teal; 2ª encostou q2-3; 3ª com pulseira verde-limão) e agarrao_cutucao (1ª: q1 com teal nos dois pulsos; 2ª encostou q1-2). rasteira (retoque com rasteira.png + parado.png): teal pintada em q3-6, q2 continua sem.

Lote 4 (8): aprovadas de primeira intro, provoca, patroa_chega_sim, patroa_sai. Refeitas 1x e aprovadas: despertar_pedido (1ª sem teal em q3,5,6,8), derrota_sirene (1ª com q7-8 encostados; salva: q1 e q6 sem teal, q5-8 virados para a esquerda como pede o MOTION), patroa_parada (1ª com 398 px, mais alta que ele; salva com 330 px ≈ 95% dele, respiração de ~20 px). vitoria: 3 tentativas, salva a 3ª com q2-3 sem teal (2ª tinha pulseira ciano enorme).
Patroa: prompt da fila, com o parágrafo de estilo sem "heroic anatomy/abdomen/gi/wraps" (contradizia "average build") e sem a frase da teal.

Procedimento novo: a janela do app ficou escondida e a captura de tela parou de funcionar; a conferência passou a ser no disco (pacote .tar de revisão → `contato.py` monta tiras → olhar). A fila roda sozinha na página (`__auto`), ~2 min por folha com a aba em segundo plano. Os .tar agora caem em Downloads já com o nome final (apagados no fim); ficou só `e9c21c9a-6c4e-4295-bd46-7ed34437e27a.tmp` (rasteira, diálogo pendente).
Scripts em scratchpad\hazak_l1\scripts (pega.py, contato.py, extrai.py).

### Pengaró Endiabrado, Lote 7 grupo A (2026-11-11, chat "Pengaró — arcade")

Commits em origin/endiabrado: f74719c (ginga, anda, soco, martelo), babcf84 (chute_alto, afastar, apanha, queda, levanta, defesa), 4d31165 (agachado, pulo, LOGBOOK).
Destino: C:/Dev/Jogo-de-Luta-endiabrado/sprites/pengaro/quadros/folhas_arcade/e_<golpe>.png. Tentativas guardadas em scratchpad\endiabrado\ger (e_<golpe>_vN.png), tiras em ...\endiabrado\ver.
"alt" = altura em pé com cabelo/chifres, em px (a normal mede 275-278 sem cabelo comprido). Todas passam em `tira_fundo` + `fatias(…, 8)`.

| Folha | Estado | Tent. | Observação |
|---|---|---|---|
| e_ginga | aprovada | 2 | 1ª: q6-7 encostados e pulso da frente sem algema. Salva: alt 309-313, pé 522-525; pontinho magenta no punho de trás em q3 e q7 |
| e_anda | aprovada | 2 | 1ª: 6% maior (331). Salva: alt 306-312, pé 530. q5-8 repetem q1-4, igual à normal (pernas não alternam) |
| e_soco | aprovada | 1 | alt 297, pé 524; rachaduras do peito apagadas em q1-4, 7, 8 |
| e_chute_alto | aprovada | 2 | 1ª: q5-6 encostados e rachaduras rosa. Salva: alt 307-315, pé 527-529 |
| e_martelo | aprovada | 1 | alt 307-315, pé 531; alcance do cotovelo curto como na normal |
| e_afastar | aprovada | 2 | 1ª: tornozelo da perna erguida sem algema em q2, 3, 6. Salva: alt 298-316, pé 531 |
| e_apanha | aprovada | 2 | 1ª: 7% maior (334, pé 555). Salva: alt 300-310, pé 541 |
| e_queda | com defeito | 3 | salva a 2ª: figura ~13% menor que a normal (em pé 214, deitado 251 contra 290), pernas levantadas em q4-7 (a normal tem as pernas no chão). 1ª: q1-3 encostados e grande demais (deitado 330). 3ª (ger/e_queda_v3.png): escala certa (deitado 293) mas a pele perdeu o roxo e ficou marrom-alaranjada |
| e_levanta | aprovada | 1 | alt final 274; q4 é o apoio nas mãos da normal (o gerador remenda e_levanta 3-4) |
| e_defesa | aprovada | 2 | 1ª: pulso da frente sem algema nos 8 e 27% maior (350). Salva: alt 295-305, pé 537; **imagem 2143x734** (as outras são 2172x724) |
| e_agachado | aprovada | 2 | 1ª seguiu o MOTION (desce da ginga, 414 px em pé) e não a normal. Salva: agachado nos 8 quadros como a agachado.png, alt 253-271, pé 525, margem esquerda de 8 px; algema do pulso da frente pouco legível |
| e_pulo | aprovada | 1 | figura ~15-20% maior que a normal (agachado 307 contra 246); q4-5 encolhido em pé, a normal está quase deitada no q4 |

O que mudou no procedimento:
- Anexos: uma página local só (`srv/load.html?f=a,b,c` em 127.0.0.1:8765) pôs 13 PNG + os 12 prompts prontos (`prompts.json`) em `window.name`: 37 MB passaram de uma vez. Na aba do ChatGPT um objeto `window.__e` faz tudo: `ask(folha, extra)` anexa conceito + normal, digita (quebras de linha trocadas por espaço) e envia; `w(nome, proxima)` espera até 36 s, baixa e já dispara a próxima folha; `FX(nome, texto)` pede correção.
- Correção com fila andando: como a próxima folha já está gerando, "edite a última imagem" não serve. O blob baixado fica em `__e.blobs[nome]` e a correção reanexa a própria imagem ("the attached image is the sheet you made, redraw it exactly, changing only…"). Funciona bem UMA vez; na segunda cópia da cópia (e_queda v3) a cor da pele já derivou.
- Download: o primeiro `<a download>` da aba não gravou nada; do segundo em diante o arquivo cai em Downloads com o nome final ou como .tmp do tamanho exato. `scripts/pega1.py <bytes> <nome_vN> <normal>` copia por tamanho, mede com o `tira_fundo` de verdade e monta a tira (boss recortado sobre verde, nativo, + normal reduzida); `scripts/corte.py <nome> <q,q>` junta só alguns quadros. Os e_*_vN.png de Downloads foram apagados no fim.
- Geração: 60-120 s por folha; nenhum limite de imagens nem pedido de login em 22 imagens.
- Fundo magenta: não fura o corpo; come só a beirada das brasas da barra da calça (~3% da figura apagada contra ~2,2% numa folha normal).

O que fez o modelo sair certo:
- Anexar conceito + folha normal: o modelo saiu igual ao conceito em todas, de primeira, e as poses seguem a normal quadro a quadro. Quando MOTION e folha normal discordam (e_agachado), ele segue o MOTION: o MOTION tem de descrever a folha normal.
- Frase que resolveu quadros encostados (casaco e corrente invadem o vizinho): "every frame sits in its own column, with at least 40 pixels of empty magenta between neighbouring frames; no coat tail, chain, rope end or hair of one frame may enter the column of another frame".
- Algemas: as que somem são a do pulso da FRENTE (fica só o bracelete) e a do tornozelo da perna erguida. Ajuda dizer "both wrists show the iron shackle with its 3 chain links below the gold bracer, also on the front arm" e "both ankles keep their shackle even when a leg is raised".
- Escala: ele tende a desenhar o boss 6-27% maior. Dar número em px ("a standing frame measures about 310 pixels from the top of the hair to the soles, soles at about y=525") ajudou na correção, mas no primeiro pedido nem sempre é obedecido (e_defesa veio com 350, e_pulo grande). Folhas com corpo deitado (queda) precisam do tamanho da normal dito em px (em pé ~245, deitado ~290).
