# Impacto atual do Pengaró — golpe a golpe

Gerado por extrair_impacto.py a partir de chars/pengaro (CNS/AIR/SFF/CMD). Corpo parado do Pengaró: 100x106 px.
Windup = ticks desde o início do estado até o primeiro tick em que há Clsn1 E o HitDef já foi ligado (projétil: tick em que sai). 'desp' = mesma conta na anim endiabrada (10000+). Sparkno 'S(ifelse(var(20)>0, 92xx+30, 92xx))' aparece como 9200/9230.

## Resumo dos problemas (impacto atual do Pengaró)

1. **O estouro da faísca chega atrasado.** As 92xx têm 22 quadros de 1 tick cada. O 1º quadro é pequeno (9200 45x29, 9230 20x19, 9202 13x13) e o pico só vem 6 a 12 ticks depois do contato (9200 no t10, 9201 no t6, 9231 no t12). Ou seja, no quadro do contato quase não aparece nada.
2. **Sujeira de recorte nas faíscas.** Pedaços do quadro vizinho da folha aparecem colados na borda direita de quase todos os quadros de 9200/9201/9205/9231/9235 (ver faiscas.png e zoom_faiscas.png). Isso infla a largura medida e no jogo aparece como lasca solta.
3. **No endiabrado, acerto fraco e defesa usam o mesmo desenho:** 9230 e 9232 são o mesmo sombra_acerto, com tamanhos idênticos quadro a quadro. Acertar e ser defendido fica igual na tela.
4. **Rastro grande sai em todo golpe, acertando ou não.** No [Statedef -3], o 9213/9212 (80x95) e o 9214/9215 (100x89) nascem no elemento ativo. Esse rastro é do tamanho da faísca forte e compete com ela: o golpe errado parece acerto, e o acerto não se destaca.
5. **sparkxy fixo em -10,-70 em todo HitDef.** Em 10 golpes baixos (322, 342, 349, 430, 440, 1300/1301, 1500/1501, 3435) a caixa de golpe fica em y≈-12 e a faísca aparece ~58 px acima do ponto de contato.
6. **EnvShake só em 15 lugares** e nenhum em forte normal (210, 240, 245, 260, 410, 440...). O super 3100 (final) e o 3200 também não tremem. Todos os que existem disparam por tempo (Time = N), não por MoveHit: tremem mesmo quando o golpe erra.
7. **Golpes fortes com faísca e som de fraco.** 25 golpes fortes ou finalizadores usam 9200 + F5,0: correntes y/b (311, 312, 331, 332), kombos 343-348, corrente do Despertar 3410-3421, 3431, 3433, 3434, 347 (finalizador) e 720. O som de impacto também só tem 3 variantes (F5,0/1/2), com F6,0 em todas as defesas.
8. **Pausetime abaixo do piso.** Os golpes do repertório (201, 216, 231, 246, 601, 611, 1400/1401, 1500/1501) usam 6,8, com P1 menor que P2 e animtype Heavy. Também ficam abaixo: 610 e 650 com 8,8, Caneta com 8,8, 3402 com 8,8 e o final do Bando da Várzea (super) com 6,8 contra piso 14.
9. **Windup fora da faixa.** Todos os fracos têm 7-10t (faixa 3-5), lentos demais. Muitos fortes têm 12-26t (faixa 7-10). O 215 tem 6t e o 323 (finalizador) tem 8t, abaixo do piso. O RITMO 1.5 esticou tudo.
10. **O forte quase não empurra mais que o fraco.** O fraco usa -4 e os fortes de corrente/kombo/Despertar -3,5 (ou -3 no repertório). Na prática o forte empurra *menos*.
11. **Projéteis sem impacto visível.** As latas, a garrafa e a Mão de Sombra não têm sparkno (cai no padrão do [Data] = fightfx 2 do motor) e o projhitanim 1006 tem 10x15 px por 6t. Na Chuva de Bebidas o sparkno é -1.
12. **Agarrões:** o impacto só vem de TargetLifeAdd + EnvShake + PlaySnd no 831/841. O agarrão comum 810 não tem tremida, faísca nem som.
13. **Nada de AllPalFX ou BGPalFX** (flash de tela) em lugar nenhum, nem no super. Só a SuperPause com darken.

| Estado | Golpe | Classe | Windup (t) normal/desp | Ativo | Anim total | Dano | Pausetime P1,P2 | Hitsound | Guardsound | Sparkno (tamanho, duração) | Guard spark | Sparkxy | Animtype | Ground.type | Ground.vel | Air.vel | Fall | Hittime/Slide | EnvShake | Explods de efeito | Superpausa |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 200 | Soco fraco | fraco | 7 | 7–12 | 22 | 40, 0 | 8,8 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Light | High | -4 | -1.4,-3 | 0 | 21/5 | — | 9212 (80x95px, 22t) [-3, elem 8, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 8, normal; sai no ativo, acerte ou não] | — |
| 201 | Mão de Ginga | fraco | 9 | 9–13 | 31 | 47, 0 | 6,8 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -3 | -2,-3 | 0 | 28/5 | — | 9212 (80x95px, 22t) [-3, elem 2, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 2, normal; sai no ativo, acerte ou não] | — |
| 210 | Soco forte longe | forte | 10 | 10–16 | 41 | 85, 0 | 10,10 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -6 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 11, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 11, normal; sai no ativo, acerte ou não] | — |
| 215 | Soco forte perto | forte | 6 | 6–11 | 32 | 80, 0 | 10,10 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 7, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 7, normal; sai no ativo, acerte ou não] | — |
| 216 | Tranco de Ombro | forte | 12 | 12–16 | 37 | 76, 0 | 6,8 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -3 | -2,-3 | 0 | 28/5 | — | 9212 (80x95px, 22t) [-3, elem 2, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 2, normal; sai no ativo, acerte ou não] | — |
| 230 | Chute fraco | fraco | 7 | 7–12 | 24 | 45, 0 | 8,8 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Light | High | -4 | -1.4,-3 | 0 | 21/5 | — | 9212 (80x95px, 22t) [-3, elem 8, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 8, normal; sai no ativo, acerte ou não] | — |
| 231 | Puxada de Sola | forte | 12 | 12–16 | 37 | 57, 0 | 6,8 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -3 | -2,-3 | 0 | 28/5 | — | 9212 (80x95px, 22t) [-3, elem 2, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 2, normal; sai no ativo, acerte ou não] | — |
| 240 | Chute forte longe | forte | 14 | 14–20 | 47 | 95, 0 | 11,11 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -7 | -1.4,-3 | 0 | 32/8 | — | 9212 (80x95px, 22t) [-3, elem 14, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 14, normal; sai no ativo, acerte ou não] | — |
| 245 | Chute forte perto | forte | 7 | 7–12 | 37 | 85, 0 | 10,10 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 8, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 8, normal; sai no ativo, acerte ou não] | — |
| 246 | Passo de Letra | forte | 26 | 26–32 | 62 | 90, 0 | 6,8 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -3 | -2,-3 | 0 | 28/5 | — | 9212 (80x95px, 22t) [-3, elem 2, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 2, normal; sai no ativo, acerte ou não] | — |
| 260 | Afastar | forte | 18 | 18–24 | 54 | 90, 0 | 12,12 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Back | High | -7,-5 | -5,-5 | 1 | 18/5 | — | 9212 (80x95px, 22t) [-3, elem 15, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 15, normal; sai no ativo, acerte ou não] | — |
| 301 | Jab de Retorno | fraco | 7 | 7–14 | 26 | 35, 0 | 6,6 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Light | High | -2.5 | -1.4,-3 | 0 | 21/5 | — | 9212 (80x95px, 22t) [-3, elem 8, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 8, normal; sai no ativo, acerte ou não] | — |
| 302 | Cotovelo de Ginga | fraco | 10 | 10–18 | 34 | 45, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 11, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 11, normal; sai no ativo, acerte ou não] | — |
| 303 | Cabeçada de Roda | finalizador | 16 | 16–24 | 48 | 90, 0 | 14,14 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -4,-5 | -3,-6 | 1 | 32/8 | t16 (no tempo, sai no whiff) time=10 freq=60 ampl=-5 | 9212 (80x95px, 22t) [-3, elem 17, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 17, normal; sai no ativo, acerte ou não] | — |
| 311 | Martelada | forte | 14 | 14–24 | 43 | 60, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 14, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 14, normal; sai no ativo, acerte ou não] | — |
| 312 | Sola de Baixo | forte | 12 | 12–22 | 49 | 70, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 13, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 13, normal; sai no ativo, acerte ou não] | — |
| 313 | Armada Final | finalizador | 16 | 16–34 | 58 | 110, 0 | 14,14 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -5,-4 | -4,-5 | 1 | 32/8 | t16 (no tempo, sai no whiff) time=10 freq=60 ampl=-5 | 9212 (80x95px, 22t) [-3, elem 15, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 15, normal; sai no ativo, acerte ou não] | — |
| 321 | Bicuda Dupla | fraco | 7 | 7–14 | 32 | 35, 0 | 6,6 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Light | High | -2.5 | -1.4,-3 | 0 | 21/5 | — | 9212 (80x95px, 22t) [-3, elem 8, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 8, normal; sai no ativo, acerte ou não] | — |
| 322 | Ponta Rasteira | fraco | 8 | 8–16 | 38 | 40, 0 | 6,6 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Light | Low | -2.5 | -1.4,-3 | 0 | 21/5 | — | 9214 (100x89px, 22t) [-3, elem 9, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 9, desp; sai no ativo, acerte ou não] | — |
| 323 | Meia-Lua Final | finalizador | 8 | 8–16 | 42 | 85, 0 | 14,14 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -5,-4 | -4,-5 | 1 | 32/8 | t8 (no tempo, sai no whiff) time=10 freq=60 ampl=-5 | 9212 (80x95px, 22t) [-3, elem 9, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 9, normal; sai no ativo, acerte ou não] | — |
| 331 | Calcanhar de Roda | forte | 12 | 12–22 | 49 | 60, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 13, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 13, normal; sai no ativo, acerte ou não] | — |
| 332 | Chute de Afastar | forte | 12 | 12–22 | 49 | 70, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -6 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 13, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 13, normal; sai no ativo, acerte ou não] | — |
| 333 | Compasso de Roda | finalizador | 12 | 12–20 | 47 | 110, 0 | 14,14 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -5,-4 | -4,-5 | 1 | 32/8 | t12 (no tempo, sai no whiff) time=10 freq=60 ampl=-5 | 9212 (80x95px, 22t) [-3, elem 13, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 13, normal; sai no ativo, acerte ou não] | — |
| 340 | Ombrada Rápida | fraco | 7 | 7–14 | 26 | 40, 0 | 6,6 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Light | High | -2.5 | -1.4,-3 | 0 | 21/5 | — | 9212 (80x95px, 22t) [-3, elem 8, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 8, normal; sai no ativo, acerte ou não] | — |
| 341 | Passo de Letra Cruzado | forte | 12 | 12–22 | 49 | 80, 0 | 10,10 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 13, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 13, normal; sai no ativo, acerte ou não] | — |
| 342 | Ponta de Esquiva | fraco | 8 | 8–16 | 38 | 35, 0 | 6,6 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Light | Low | -2.5 | -1.4,-3 | 0 | 21/5 | — | 9214 (100x89px, 22t) [-3, elem 9, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 9, desp; sai no ativo, acerte ou não] | — |
| 343 | Martelo por Cima | forte | 14 | 14–24 | 42 | 70, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -4,-4 | -3,-5 | 1 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 14, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 14, normal; sai no ativo, acerte ou não] | — |
| 344 | Cotovelada de Recuo | forte | 10 | 10–18 | 34 | 55, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 11, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 11, normal; sai no ativo, acerte ou não] | — |
| 345 | Empurrão de Sola | forte | 12 | 12–22 | 49 | 65, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -9 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 13, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 13, normal; sai no ativo, acerte ou não] | — |
| 346 | Calcanhar de Entrada | forte | 8 | 8–18 | 42 | 55, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 9, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 9, normal; sai no ativo, acerte ou não] | — |
| 347 | Cabeçada Lançadora | finalizador | 16 | 16–24 | 48 | 70, 0 | 14,14 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -2,-4 | -2,-9 | 1 | 32/8 | t16 (no tempo, sai no whiff) time=10 freq=60 ampl=-5 | 9212 (80x95px, 22t) [-3, elem 17, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 17, normal; sai no ativo, acerte ou não] | — |
| 348 | Compasso Possuído | forte | 12 | 12–20 | 47 | 65, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 13, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 13, normal; sai no ativo, acerte ou não] | — |
| 349 | Caneta Sombria | forte | 12 | 12–24 | 50 | 80, 0 | 10,10 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | Low | -3,-3 | -3,-4 | 1 | 30/7 | — | 9214 (100x89px, 22t) [-3, elem 13, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 13, desp; sai no ativo, acerte ou não] | — |
| 400 | Agachado soco fraco | fraco | 7 | 7–12 | 22 | 35, 0 | 8,8 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Light | Low | -4 | -1.4,-3 | 0 | 20/5 | — | 9212 (80x95px, 22t) [-3, elem 8, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 8, normal; sai no ativo, acerte ou não] | — |
| 410 | Agachado soco forte | forte | 8 | 8–16 | 43 | 90, 0 | 10,10 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Up | High | -3 | -2,-7 | 0 | 30/5 | — | 9212 (80x95px, 22t) [-3, elem 9, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 9, normal; sai no ativo, acerte ou não] | — |
| 430 | Agachado chute fraco | fraco | 7 | 7–12 | 26 | 35, 0 | 8,8 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Light | Low | -4 | -1.4,-3 | 0 | 21/5 | — | 9214 (100x89px, 22t) [-3, elem 8, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 8, desp; sai no ativo, acerte ou não] | — |
| 440 | Agachado chute forte | forte | 16 | 16–22 | 54 | 80, 0 | 10,10 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Back | Trip | -3,-2 | -3,-2 | 1 | 18/5 | — | 9214 (100x89px, 22t) [-3, elem 15, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 15, desp; sai no ativo, acerte ou não] | — |
| 600 | Golpe no ar | fraco | 7 | 7–19 | 19 | 60, 0 | 8,8 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Light | High | -4 | -1.4,-3 | 0 | 24/5 | — | 9212 (80x95px, 22t) [-3, elem 8, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 8, normal; sai no ativo, acerte ou não] | — |
| 601 | Golpe no ar | forte | 10 | 10–18 | 18 | 79, 0 | 6,8 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -3 | -2,-3 | 0 | 28/5 | — | 9212 (80x95px, 22t) [-3, elem 2, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 2, normal; sai no ativo, acerte ou não] | — |
| 610 | Golpe no ar | forte | 9 | 9–24 | 24 | 75, 0 | 8,8 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -4 | -1.4,-3 | 0 | 27/5 | — | 9212 (80x95px, 22t) [-3, elem 2, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 2, normal; sai no ativo, acerte ou não] | — |
| 611 | Golpe no ar | forte | 14 | 14–23 | 23 | 88, 0 | 6,8 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -3 | -2,-3 | 0 | 28/5 | — | 9212 (80x95px, 22t) [-3, elem 2, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 2, normal; sai no ativo, acerte ou não] | — |
| 650 | Afastar no ar | forte | 10 | 10–19 | 19 | 80, 0 | 8,8 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Back | High | -5,-4 | -4,-4 | 1 | 18/5 | — | 9214 (100x89px, 22t) [-3, elem 11, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 11, desp; sai no ativo, acerte ou não] | — |
| 720 | Afastar de defesa | forte | 18 | 18–24 | 54 | 0, 0 | 12,12 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Back | High | -7,-5 | -5,-5 | 1 | 18/5 | — | 9212 (80x95px, 22t) [-3, elem 15, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 15, normal; sai no ativo, acerte ou não] | — |
| 800 | Agarrao | agarrão | 0 | 0–4 | 4 | None | None,None | - | - | -1 | - | - | (Light) | (High) | - | - | 1 | -/- | — | 9212 (80x95px, 22t) [-3, elem 1, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 1, normal; sai no ativo, acerte ou não] | — |
| 830 | Agarrao whisky | agarrão | 0 | 0–4 | 22 | None | None,None | - | - | -1 | - | - | (Light) | (High) | - | - | 1 | -/- | — | 9212 (80x95px, 22t) [-3, elem 1, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 1, normal; sai no ativo, acerte ou não] | — |
| 840 | Agarrão agachado | agarrão | 0 | 0–4 | 22 | None | None,None | - | - | -1 | - | - | (Light) | (High) | - | - | 1 | -/- | — | 9214 (100x89px, 22t) [-3, elem 1, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 1, desp; sai no ativo, acerte ou não] | — |
| 1000 | Latada de Sombra fraca #1/2 | projétil | 12 | - | 62 | 70, 4 | 2,10 | F5,1 | F6,0 | (padrão do [Data]: fightfx 2); projhitanim 1006 (10x15px, 6t) | - | 0, 0 | Med | High | -4 | -2,-3.5 | 0 | 27/12 | — | — | — |
| 1000 | Latada de Sombra fraca #2/2 | projétil | 20 | - | 62 | 50, 4 | 2,10 | F5,1 | F6,0 | (padrão do [Data]: fightfx 2); projhitanim 1006 (10x15px, 6t) | - | - | Med | High | -4 | -2,-3.5 | 0 | 27/12 | — | — | — |
| 1001 | Latada de Sombra forte #1/2 | projétil | 12 | - | 68 | 70, 4 | 2,10 | F5,1 | F6,0 | (padrão do [Data]: fightfx 2); projhitanim 1006 (10x15px, 6t) | - | 0, 0 | Med | High | -4 | -2,-3.5 | 0 | 27/12 | — | — | — |
| 1001 | Latada de Sombra forte #2/2 | projétil | 20 | - | 68 | 50, 4 | 2,10 | F5,1 | F6,0 | (padrão do [Data]: fightfx 2); projhitanim 1006 (10x15px, 6t) | - | - | Med | High | -4 | -2,-3.5 | 0 | 27/12 | — | — | — |
| 1100 | Meia-lua de Compasso | especial | 12 | 12–36 | 57 | 110, 0 | 10,10 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -5,-4 | -4,-4 | 1 | 18/5 | — | 9214 (100x89px, 22t) [-3, elem 8, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 8, desp; sai no ativo, acerte ou não] | — |
| 1101 | Meia-lua de Compasso (forte) | especial | 12 | 12–36 | 66 | 132, 0 | 10,10 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -5,-4 | -4,-4 | 1 | 18/5 | — | 9214 (100x89px, 22t) [-3, elem 8, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 8, desp; sai no ativo, acerte ou não] | — |
| 1200 | Armada do Quilombo | especial | 6 | 6–15 | 27 | 120, 0 | 11,11 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Up | High | -2,-7 | -2,-7 | 1 | 18/5 | — | 9212 (80x95px, 22t) [-3, elem 7, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 7, normal; sai no ativo, acerte ou não] | — |
| 1201 | Armada do Quilombo (forte) | especial | 6 | 6–15 | 27 | 144, 0 | 11,11 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Up | High | -2,-7 | -2,-7 | 1 | 18/5 | — | 9212 (80x95px, 22t) [-3, elem 7, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 7, normal; sai no ativo, acerte ou não] | — |
| 1300 | Caneta | especial | 15 | 15–27 | 57 | 70, 0 | 8,8 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Back | Trip | -2,-2 | -2,-2 | 1 | 18/5 | — | 9214 (100x89px, 22t) [-3, elem 15, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 15, desp; sai no ativo, acerte ou não] | — |
| 1301 | Caneta (forte) | especial | 15 | 15–27 | 66 | 92, 0 | 8,8 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Back | Trip | -2,-2 | -2,-2 | 1 | 18/5 | — | 9214 (100x89px, 22t) [-3, elem 15, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 15, desp; sai no ativo, acerte ou não] | — |
| 1400 | Mão de Chimpá | especial | 12 | 12–18 | 42 | 73, 0 | 6,8 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -3 | -3,-3.5 | 0 | 28/5 | — | 9212 (80x95px, 22t) [-3, elem 2, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 2, normal; sai no ativo, acerte ou não] | — |
| 1401 | Mão de Chimpá (forte) | especial | 16 | 16–25 | 59 | 95, 0 | 6,8 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -3 | -3,-3.5 | 0 | 28/5 | — | 9212 (80x95px, 22t) [-3, elem 2, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 2, normal; sai no ativo, acerte ou não] | — |
| 1500 | Sola de Várzea | especial | 12 | 12–18 | 42 | 88, 0 | 6,8 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | Low | -3 | -3,-3.5 | 0 | 28/5 | — | 9214 (100x89px, 22t) [-3, elem 2, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 2, desp; sai no ativo, acerte ou não]<br>9235 (80x101px, 22t)/9205 (80x91px, 22t) [AnimElem = 2 var(20) > 0; scale=1; trans=-] | — |
| 1501 | Sola de Várzea (forte) | especial | 16 | 16–25 | 59 | 110, 0 | 6,8 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | Low | -3,-3.5 | -3,-3.5 | 1 | 28/5 | — | 9214 (100x89px, 22t) [-3, elem 2, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 2, desp; sai no ativo, acerte ou não]<br>9235 (80x101px, 22t)/9205 (80x91px, 22t) [AnimElem = 2 var(20) > 0; scale=1; trans=-] | — |
| 1600 | Garrafada em Arco fraca | projétil | 23 | - | 73 | 75, 5 | 2,10 | F5,1 | F6,0 | (padrão do [Data]: fightfx 2); projhitanim 1006 (10x15px, 6t) | - | 0, 0 | Med | High | -4 | -2,-3.5 | 0 | 27/12 | — | — | — |
| 1601 | Garrafada em Arco forte | projétil | 23 | - | 79 | 75, 5 | 2,10 | F5,1 | F6,0 | (padrão do [Data]: fightfx 2); projhitanim 1006 (10x15px, 6t) | - | 0, 0 | Med | High | -4 | -2,-3.5 | 0 | 27/12 | — | — | — |
| 1701 | Rolê por Trás e Chute | especial | 24 | 24–32 | 52 | 70, 0 | 10,10 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 22, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 22, normal; sai no ativo, acerte ou não] | — |
| 3000 | Chuva de Bebidas #1/6 | projétil (super) | 36 | - | 96 | 42, 6 | 4,10 | F5,2 | F6,0 | -1; projhitanim 9200 (60x75px, 22t) | - | - | Med | High | -2 | -2,-3 | 0 | 24/10 | — | — | time=30 darken=1 anim=100 som=F20,0 |
| 3000 | Chuva de Bebidas #2/6 | projétil (super) | 42 | - | 96 | 42, 6 | 4,10 | F5,2 | F6,0 | -1; projhitanim 9200 (60x75px, 22t) | - | - | Med | High | -2 | -2,-3 | 0 | 24/10 | — | — | time=30 darken=1 anim=100 som=F20,0 |
| 3000 | Chuva de Bebidas #3/6 | projétil (super) | 48 | - | 96 | 42, 6 | 4,10 | F5,2 | F6,0 | -1; projhitanim 9200 (60x75px, 22t) | - | - | Med | High | -2 | -2,-3 | 0 | 24/10 | — | — | time=30 darken=1 anim=100 som=F20,0 |
| 3000 | Chuva de Bebidas #4/6 | projétil (super) | 54 | - | 96 | 42, 6 | 4,10 | F5,2 | F6,0 | -1; projhitanim 9200 (60x75px, 22t) | - | - | Med | High | -2 | -2,-3 | 0 | 24/10 | — | — | time=30 darken=1 anim=100 som=F20,0 |
| 3000 | Chuva de Bebidas #5/6 | projétil (super) | 60 | - | 96 | 42, 6 | 4,10 | F5,2 | F6,0 | -1; projhitanim 9200 (60x75px, 22t) | - | - | Med | High | -2 | -2,-3 | 0 | 24/10 | — | — | time=30 darken=1 anim=100 som=F20,0 |
| 3000 | Chuva de Bebidas #6/6 | projétil (super) | 66 | - | 96 | 60, 6 | 4,10 | F5,2 | F6,0 | -1; projhitanim 9200 (60x75px, 22t) | - | - | Heavy | High | -2 | -2,-3 | 1 | 24/10 | — | — | time=30 darken=1 anim=100 som=F20,0 |
| 3100 | Saideira Sombria #1/2 | super | 6 | 6–54 | 84 | 47, 0 | 2,6 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -1 | -1,-3 | 0 | 24/4 | — | 9215 (96x80px, 24t) [-3, elem 2, desp; sai no ativo, acerte ou não] | time=30 darken=1 anim=100 som=F20,0 |
| 3100 | Saideira Sombria #2/2 | super-final | 36 | 36–54 | 84 | 60, 0 | 14,14 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Back | High | -7,-6 | -7,-6 | 1 | 18/5 | — | 9215 (96x80px, 24t) [-3, elem 2, desp; sai no ativo, acerte ou não] | time=30 darken=1 anim=100 som=F20,0 |
| 3200 | Bando da Várzea #1/3 | super | 16 | 16–41 | 80 | 115, 0 | 6,8 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -1 | -2,-3 | 0 | 32/5 | — | 9212 (80x95px, 22t) [-3, elem 2, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 2, normal; sai no ativo, acerte ou não] | time=30 darken=1 anim=100 som=F20,0 |
| 3200 | Bando da Várzea #2/3 | super | 24 | 24–41 | 80 | 115, 0 | 6,8 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -1 | -2,-3 | 0 | 32/5 | — | 9212 (80x95px, 22t) [-3, elem 2, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 2, normal; sai no ativo, acerte ou não] | time=30 darken=1 anim=100 som=F20,0 |
| 3200 | Bando da Várzea #3/3 | super-final | 32 | 32–41 | 80 | 115, 0 | 6,8 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -2,-3 | -2,-3 | 1 | 28/5 | — | 9212 (80x95px, 22t) [-3, elem 2, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 2, normal; sai no ativo, acerte ou não] | time=30 darken=1 anim=100 som=F20,0 |
| 3400 | Mão de Sombra | projétil | 25 | - | 64 | 50, 5 | 2,10 | F5,1 | F6,0 | (padrão do [Data]: fightfx 2); projhitanim 3006 (30x45px, 6t) | - | 0, 0 | Med | High | -3 | -2,-3.5 | 0 | 30/14 | — | — | — |
| 3401 | Chute da Corrente | finalizador | 14 | 14–24 | 57 | 115, 0 | 14,14 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -6,-4 | -5,-5 | 1 | 32/8 | t14 (no tempo, sai no whiff) time=10 freq=60 ampl=-5 | 9212 (80x95px, 22t) [-3, elem 14, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 14, normal; sai no ativo, acerte ou não] | — |
| 3402 | Sombra Atravessada | especial | 8 | 8–16 | 43 | 75, 0 | 8,8 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -1 | -1,-3 | 0 | 33/7 | — | 9214 (100x89px, 22t) [-3, elem 9, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 9, desp; sai no ativo, acerte ou não] | — |
| 3403 | Queda Escura | especial | 18 | 18–30 | 30 | 105, 0 | 12,12 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -4,-6 | -4,-6 | 1 | 33/8 | tNone (no tempo, sai no whiff) time=10 freq=60 ampl=-4 | 9214 (100x89px, 22t) [-3, elem 19, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 19, desp; sai no ativo, acerte ou não]<br>9235 (80x101px, 22t)/9205 (80x91px, 22t) [Pos Y >= 0 && Vel Y > 0; scale=1; trans=-] | — |
| 3410 | Revolta de Corrente | forte | 10 | 10–18 | 34 | 55, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 11, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 11, normal; sai no ativo, acerte ou não] | — |
| 3411 | Sola de Ferro | forte | 10 | 10–18 | 42 | 60, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 11, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 11, normal; sai no ativo, acerte ou não] | — |
| 3412 | Cabeçada Escura | forte | 14 | 14–22 | 40 | 70, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 15, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 15, normal; sai no ativo, acerte ou não] | — |
| 3413 | Roda da Possessão | finalizador | 12 | 12–20 | 47 | 120, 0 | 14,14 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -6,-4 | -5,-5 | 1 | 32/8 | t12 (no tempo, sai no whiff) time=10 freq=60 ampl=-5 | 9212 (80x95px, 22t) [-3, elem 13, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 13, normal; sai no ativo, acerte ou não] | — |
| 3420 | Calcanhar Sombrio | forte | 10 | 10–18 | 42 | 60, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 11, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 11, normal; sai no ativo, acerte ou não] | — |
| 3421 | Afastar Pesado | forte | 10 | 10–18 | 42 | 70, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -7 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 11, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 11, normal; sai no ativo, acerte ou não] | — |
| 3422 | Armada Torta | forte | 12 | 12–24 | 42 | 75, 0 | 10,10 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 13, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 13, normal; sai no ativo, acerte ou não] | — |
| 3423 | Chute da Corrente Partida | finalizador | 16 | 16–34 | 58 | 125, 0 | 14,14 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -6,-4 | -5,-5 | 1 | 32/8 | t16 (no tempo, sai no whiff) time=10 freq=60 ampl=-5 | 9212 (80x95px, 22t) [-3, elem 15, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 15, normal; sai no ativo, acerte ou não] | — |
| 3430 | Mão de Chão Possuída | forte | 16 | 16–24 | 44 | 95, 0 | 11,11 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -2,-4 | -2,-10 | 1 | 32/8 | t16 (no tempo, sai no whiff) time=7 freq=60 ampl=-3 | 9212 (80x95px, 22t) [-3, elem 17, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 17, normal; sai no ativo, acerte ou não] | — |
| 3431 | Tranco Possuído #1/2 | forte | 14 | 14–18 | 47 | 50, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 14, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 14, normal; sai no ativo, acerte ou não] | — |
| 3431 | Tranco Possuído #2/2 | forte | 21 | 21–25 | 47 | 60, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 14, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 14, normal; sai no ativo, acerte ou não] | — |
| 3432 | Passo de Sombra | forte | 17 | 17–27 | 57 | 100, 0 | 11,11 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | High | -7 | -1.4,-3 | 0 | 32/8 | t17 (no tempo, sai no whiff) time=7 freq=60 ampl=-3 | 9212 (80x95px, 22t) [-3, elem 15, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 15, normal; sai no ativo, acerte ou não] | — |
| 3433 | Palma Torta | forte | 7 | 7–14 | 26 | 58, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3.5 | -1.4,-3 | 0 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 8, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 8, normal; sai no ativo, acerte ou não] | — |
| 3434 | Puxada Sombria | forte | 10 | 10–18 | 42 | 70, 0 | 10,10 | F5,0 | F6,0 | 9230 (60x73px, 22t)/9200 (60x75px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Medium | High | -3,-3 | -3,-4 | 1 | 30/7 | — | 9212 (80x95px, 22t) [-3, elem 11, desp; sai no ativo, acerte ou não]<br>9213 (80x95px, 22t) [-3, elem 11, normal; sai no ativo, acerte ou não] | — |
| 3435 | Foice Escura | forte | 17 | 17–27 | 60 | 100, 0 | 11,11 | F5,2 | F6,0 | 9231 (80x101px, 22t)/9201 (80x91px, 22t) | S(ifelse(var(20) > 0, 9232, 9202)) | -10, -70 | Heavy | Trip | -3,-2 | -3,-2 | 1 | 32/8 | t17 (no tempo, sai no whiff) time=7 freq=60 ampl=-3 | 9214 (100x89px, 22t) [-3, elem 15, normal; sai no ativo, acerte ou não]<br>9215 (96x80px, 24t) [-3, elem 15, desp; sai no ativo, acerte ou não] | — |

## Faíscas e efeitos (SFF/AIR)

| Ação | Sprites | Quadros | Duração (t) | Maior caixa opaca | Quadro/tick do pico | Caixa por quadro |
|---|---|---|---|---|---|---|
| 9200 | 9200,* | 22 | 22 | 60x75 | 10 / t10 | 45x29 46x31 60x43 60x49 60x53 59x59 60x64 60x64 55x74 56x75 58x74 58x73 58x73 57x72 54x61 53x62 52x59 50x55 50x54 49x51 37x38 36x38 |
| 9201 | 9205,* | 22 | 22 | 80x91 | 6 / t6 | 63x53 66x54 74x70 80x82 80x84 78x86 80x90 79x87 78x91 78x90 78x86 79x76 79x75 78x72 79x71 80x68 79x68 73x66 72x66 71x59 46x49 46x47 |
| 9202 | 9204,* | 22 | 22 | 48x59 | 9 / t9 | 13x13 13x14 45x40 47x42 48x44 39x50 42x58 41x57 45x59 47x59 47x56 44x52 44x50 42x47 36x42 36x39 35x36 33x36 33x35 33x31 26x24 26x23 |
| 9230 | 9230,* | 22 | 22 | 60x73 | 6 / t6 | 20x19 20x19 56x52 60x56 60x53 57x65 60x73 58x70 58x65 60x68 59x65 57x62 56x60 54x55 50x54 48x52 46x49 38x43 37x46 35x41 22x35 23x37 |
| 9231 | 9235,* | 22 | 22 | 80x101 | 12 / t12 | 67x51 70x55 77x73 79x81 79x86 77x86 79x98 80x98 79x99 74x101 76x101 78x99 80x99 78x99 74x77 73x76 70x74 61x71 61x70 60x65 57x59 56x56 |
| 9232 | 9234,* | 22 | 22 | 60x73 | 6 / t6 | 20x19 20x19 56x52 60x56 60x53 57x65 60x73 58x70 58x65 60x68 59x65 57x62 56x60 54x55 50x54 48x52 46x49 38x43 37x46 35x41 22x35 23x37 |
| 9204 | 9204,* | 22 | 22 | 48x59 | 9 / t9 | 13x13 13x14 45x40 47x42 48x44 39x50 42x58 41x57 45x59 47x59 47x56 44x52 44x50 42x47 36x42 36x39 35x36 33x36 33x35 33x31 26x24 26x23 |
| 9205 | 9205,* | 22 | 22 | 80x91 | 6 / t6 | 63x53 66x54 74x70 80x82 80x84 78x86 80x90 79x87 78x91 78x90 78x86 79x76 79x75 78x72 79x71 80x68 79x68 73x66 72x66 71x59 46x49 46x47 |
| 9235 | 9235,* | 22 | 22 | 80x101 | 12 / t12 | 67x51 70x55 77x73 79x81 79x86 77x86 79x98 80x98 79x99 74x101 76x101 78x99 80x99 78x99 74x77 73x76 70x74 61x71 61x70 60x65 57x59 56x56 |
| 9212 | 9212,* | 22 | 22 | 80x95 | 9 / t9 | 35x28 39x32 72x45 76x51 72x57 77x70 79x75 79x79 75x88 80x95 77x93 73x86 72x83 71x80 68x74 67x74 64x67 63x58 60x59 58x56 54x50 52x48 |
| 9213 | 9213,* | 22 | 22 | 80x95 | 9 / t9 | 66x23 67x25 76x60 79x65 79x68 80x76 79x85 68x85 76x91 79x95 78x95 72x88 71x86 70x82 65x78 79x75 79x73 79x70 80x68 61x66 48x63 46x61 |
| 9214 | 9214,* | 22 | 22 | 100x89 | 9 / t9 | 79x20 80x20 96x40 99x49 100x48 97x66 99x74 99x78 95x86 99x89 99x83 98x67 99x65 95x60 100x50 99x47 96x43 100x28 99x28 93x27 63x14 64x15 |
| 9215 | 9215,* | 24 | 24 | 96x80 | 10 / t10 | 89x30 90x32 88x49 90x51 92x55 92x65 94x69 95x69 95x80 96x79 96x80 95x71 95x72 95x68 93x63 93x62 91x58 92x46 91x44 88x41 89x31 88x30 88x30 89x30 |

## Agarrões e estados ligados (sem HitDef de dano)

- **800 Agarrao**: HitDef [Time = 0] pausetime=None
- **810 Agarrão (joga)**: TargetBind [Time < 14]; TargetLifeAdd -100 [Time = 14]; TargetState [Time = 14]
- **830 Agarrao whisky**: HitDef [Time = 0] pausetime=None
- **831 Agarrão whisky (bate)**: TargetBind [Time < 66]; TargetLifeAdd -60 [Time = 26 NumTarget]; TargetState [Time = 26 NumTarget]; EnvShake [Time = 26] time=8 ampl=-4; Explod 9231 (80x101px, 22t)/9201 (80x91px, 22t) [Time = 26] scale=1; PlaySnd F5, 2 [Time = 26]; Explod 3010 (44x44px, 12t) [Time = 53] scale=1; TargetLifeAdd -90 [Time = 66 NumTarget]; Explod 9231 (80x101px, 22t)/9201 (80x91px, 22t) [Time = 66] scale=1; EnvShake [Time = 66] time=12 ampl=-5; PlaySnd F5, 2 [Time = 66]; TargetState [Time = 66 NumTarget]
- **832 ?**: nada de impacto
- **833 ?**: nada de impacto
- **840 Agarrão agachado**: HitDef [Time = 0] pausetime=None
- **841 Rasteira de Pegada**: TargetBind [Time < 20]; TargetLifeAdd -110 [Time = 20 NumTarget]; EnvShake [Time = 20] time=10 ampl=-4; PlaySnd F5, 2 [Time = 20]; TargetState [Time = 20 NumTarget]
- **762 Parry (contra-ataque)**: nada de impacto
- **763 ?**: nada de impacto

## Violações dos pisos da seção 8.3 (94)

- 200 Soco fraco (fraco): windup 7t acima da faixa 3–5 (lento para a classe)
- 201 Mão de Ginga (fraco): windup 9t acima da faixa 3–5 (lento para a classe)
- 210 Soco forte longe (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 215 Soco forte perto (forte): windup 6t < piso 7–10
- 215 Soco forte perto (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 216 Tranco de Ombro (forte): windup 12t acima da faixa 7–10 (lento para a classe)
- 216 Tranco de Ombro (forte): pausetime 6,8 < piso 10
- 216 Tranco de Ombro (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 230 Chute fraco (fraco): windup 7t acima da faixa 3–5 (lento para a classe)
- 231 Puxada de Sola (forte): windup 12t acima da faixa 7–10 (lento para a classe)
- 231 Puxada de Sola (forte): pausetime 6,8 < piso 10
- 231 Puxada de Sola (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 240 Chute forte longe (forte): windup 14t acima da faixa 7–10 (lento para a classe)
- 240 Chute forte longe (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 245 Chute forte perto (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 246 Passo de Letra (forte): windup 26t acima da faixa 7–10 (lento para a classe)
- 246 Passo de Letra (forte): pausetime 6,8 < piso 10
- 246 Passo de Letra (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 260 Afastar (forte): windup 18t acima da faixa 7–10 (lento para a classe)
- 260 Afastar (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 301 Jab de Retorno (fraco): windup 7t acima da faixa 3–5 (lento para a classe)
- 302 Cotovelo de Ginga (fraco): windup 10t acima da faixa 3–5 (lento para a classe)
- 303 Cabeçada de Roda (finalizador): windup 16t acima da faixa 10–14 (lento para a classe)
- 311 Martelada (forte): windup 14t acima da faixa 7–10 (lento para a classe)
- 311 Martelada (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 312 Sola de Baixo (forte): windup 12t acima da faixa 7–10 (lento para a classe)
- 312 Sola de Baixo (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 313 Armada Final (finalizador): windup 16t acima da faixa 10–14 (lento para a classe)
- 321 Bicuda Dupla (fraco): windup 7t acima da faixa 3–5 (lento para a classe)
- 322 Ponta Rasteira (fraco): windup 8t acima da faixa 3–5 (lento para a classe)
- 323 Meia-Lua Final (finalizador): windup 8t < piso 10–14
- 331 Calcanhar de Roda (forte): windup 12t acima da faixa 7–10 (lento para a classe)
- 331 Calcanhar de Roda (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 332 Chute de Afastar (forte): windup 12t acima da faixa 7–10 (lento para a classe)
- 332 Chute de Afastar (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 340 Ombrada Rápida (fraco): windup 7t acima da faixa 3–5 (lento para a classe)
- 341 Passo de Letra Cruzado (forte): windup 12t acima da faixa 7–10 (lento para a classe)
- 341 Passo de Letra Cruzado (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 342 Ponta de Esquiva (fraco): windup 8t acima da faixa 3–5 (lento para a classe)
- 343 Martelo por Cima (forte): windup 14t acima da faixa 7–10 (lento para a classe)
- 343 Martelo por Cima (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 344 Cotovelada de Recuo (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 345 Empurrão de Sola (forte): windup 12t acima da faixa 7–10 (lento para a classe)
- 345 Empurrão de Sola (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 346 Calcanhar de Entrada (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 347 Cabeçada Lançadora (finalizador): windup 16t acima da faixa 10–14 (lento para a classe)
- 348 Compasso Possuído (forte): windup 12t acima da faixa 7–10 (lento para a classe)
- 348 Compasso Possuído (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 349 Caneta Sombria (forte): windup 12t acima da faixa 7–10 (lento para a classe)
- 349 Caneta Sombria (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 400 Agachado soco fraco (fraco): windup 7t acima da faixa 3–5 (lento para a classe)
- 410 Agachado soco forte (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 430 Agachado chute fraco (fraco): windup 7t acima da faixa 3–5 (lento para a classe)
- 440 Agachado chute forte (forte): windup 16t acima da faixa 7–10 (lento para a classe)
- 440 Agachado chute forte (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 600 Golpe no ar (fraco): windup 7t acima da faixa 3–5 (lento para a classe)
- 601 Golpe no ar (forte): pausetime 6,8 < piso 10
- 601 Golpe no ar (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 610 Golpe no ar (forte): pausetime 8,8 < piso 10
- 610 Golpe no ar (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 611 Golpe no ar (forte): windup 14t acima da faixa 7–10 (lento para a classe)
- 611 Golpe no ar (forte): pausetime 6,8 < piso 10
- 611 Golpe no ar (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 650 Afastar no ar (forte): pausetime 8,8 < piso 10
- 650 Afastar no ar (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 720 Afastar de defesa (forte): windup 18t acima da faixa 7–10 (lento para a classe)
- 720 Afastar de defesa (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 1300 Caneta (especial): pausetime 8,8 < piso 10 (especial: piso de forte por analogia)
- 1301 Caneta (forte) (especial): pausetime 8,8 < piso 10 (especial: piso de forte por analogia)
- 1400 Mão de Chimpá (especial): pausetime 6,8 < piso 10 (especial: piso de forte por analogia)
- 1401 Mão de Chimpá (forte) (especial): pausetime 6,8 < piso 10 (especial: piso de forte por analogia)
- 1500 Sola de Várzea (especial): pausetime 6,8 < piso 10 (especial: piso de forte por analogia)
- 1501 Sola de Várzea (forte) (especial): pausetime 6,8 < piso 10 (especial: piso de forte por analogia)
- 3100 Saideira Sombria (super-final, golpe 2/2): sem EnvShake (8.3 pede em forte/finalizador/super)
- 3200 Bando da Várzea (super-final, golpe 3/3): pausetime 6,8 < piso 14
- 3200 Bando da Várzea (super-final, golpe 3/3): sem EnvShake (8.3 pede em forte/finalizador/super)
- 3402 Sombra Atravessada (especial): pausetime 8,8 < piso 10 (especial: piso de forte por analogia)
- 3410 Revolta de Corrente (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 3411 Sola de Ferro (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 3412 Cabeçada Escura (forte): windup 14t acima da faixa 7–10 (lento para a classe)
- 3412 Cabeçada Escura (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 3420 Calcanhar Sombrio (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 3421 Afastar Pesado (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 3422 Armada Torta (forte): windup 12t acima da faixa 7–10 (lento para a classe)
- 3422 Armada Torta (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 3423 Chute da Corrente Partida (finalizador): windup 16t acima da faixa 10–14 (lento para a classe)
- 3430 Mão de Chão Possuída (forte): windup 16t acima da faixa 7–10 (lento para a classe)
- 3431 Tranco Possuído (forte, golpe 1/2): windup 14t acima da faixa 7–10 (lento para a classe)
- 3431 Tranco Possuído (forte, golpe 1/2): sem EnvShake (8.3 pede em forte/finalizador/super)
- 3431 Tranco Possuído (forte, golpe 2/2): sem EnvShake (8.3 pede em forte/finalizador/super)
- 3432 Passo de Sombra (forte): windup 17t acima da faixa 7–10 (lento para a classe)
- 3433 Palma Torta (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 3434 Puxada Sombria (forte): sem EnvShake (8.3 pede em forte/finalizador/super)
- 3435 Foice Escura (forte): windup 17t acima da faixa 7–10 (lento para a classe)

## Incoerências (108)

- 201 Mão de Ginga (fraco): animtype Heavy não casa com fraco
- 231 Puxada de Sola (forte): faísca de fraco (9200) em golpe forte
- 231 Puxada de Sola (forte): som de fraco (F5,0) em golpe forte
- 302 Cotovelo de Ginga (fraco): animtype Medium não casa com fraco
- 303 Cabeçada de Roda (finalizador): EnvShake por tempo (t16), treme mesmo errando e não sincroniza com o hitpause
- 311 Martelada (forte): faísca de fraco (9200) em golpe forte
- 311 Martelada (forte): som de fraco (F5,0) em golpe forte
- 312 Sola de Baixo (forte): faísca de fraco (9200) em golpe forte
- 312 Sola de Baixo (forte): som de fraco (F5,0) em golpe forte
- 313 Armada Final (finalizador): EnvShake por tempo (t16), treme mesmo errando e não sincroniza com o hitpause
- 323 Meia-Lua Final (finalizador): EnvShake por tempo (t8), treme mesmo errando e não sincroniza com o hitpause
- 331 Calcanhar de Roda (forte): faísca de fraco (9200) em golpe forte
- 331 Calcanhar de Roda (forte): som de fraco (F5,0) em golpe forte
- 332 Chute de Afastar (forte): faísca de fraco (9200) em golpe forte
- 332 Chute de Afastar (forte): som de fraco (F5,0) em golpe forte
- 333 Compasso de Roda (finalizador): EnvShake por tempo (t12), treme mesmo errando e não sincroniza com o hitpause
- 343 Martelo por Cima (forte): faísca de fraco (9200) em golpe forte
- 343 Martelo por Cima (forte): som de fraco (F5,0) em golpe forte
- 344 Cotovelada de Recuo (forte): faísca de fraco (9200) em golpe forte
- 344 Cotovelada de Recuo (forte): som de fraco (F5,0) em golpe forte
- 345 Empurrão de Sola (forte): faísca de fraco (9200) em golpe forte
- 345 Empurrão de Sola (forte): som de fraco (F5,0) em golpe forte
- 346 Calcanhar de Entrada (forte): faísca de fraco (9200) em golpe forte
- 346 Calcanhar de Entrada (forte): som de fraco (F5,0) em golpe forte
- 347 Cabeçada Lançadora (finalizador): EnvShake por tempo (t16), treme mesmo errando e não sincroniza com o hitpause
- 347 Cabeçada Lançadora (finalizador): faísca de fraco (9200) em golpe finalizador
- 347 Cabeçada Lançadora (finalizador): som de fraco (F5,0) em golpe finalizador
- 348 Compasso Possuído (forte): faísca de fraco (9200) em golpe forte
- 348 Compasso Possuído (forte): som de fraco (F5,0) em golpe forte
- 720 Afastar de defesa (forte): faísca de fraco (9200) em golpe forte
- 720 Afastar de defesa (forte): som de fraco (F5,0) em golpe forte
- 800 Agarrao (agarrão): sem faísca de acerto (sparkno = -1)
- 830 Agarrao whisky (agarrão): sem faísca de acerto (sparkno = -1)
- 840 Agarrão agachado (agarrão): sem faísca de acerto (sparkno = -1)
- 3000 Chuva de Bebidas (projétil (super), golpe 1/6): sem faísca de acerto (sparkno = -1)
- 3000 Chuva de Bebidas (projétil (super), golpe 2/6): sem faísca de acerto (sparkno = -1)
- 3000 Chuva de Bebidas (projétil (super), golpe 3/6): sem faísca de acerto (sparkno = -1)
- 3000 Chuva de Bebidas (projétil (super), golpe 4/6): sem faísca de acerto (sparkno = -1)
- 3000 Chuva de Bebidas (projétil (super), golpe 5/6): sem faísca de acerto (sparkno = -1)
- 3000 Chuva de Bebidas (projétil (super), golpe 6/6): sem faísca de acerto (sparkno = -1)
- 3100 Saideira Sombria (super, golpe 1/2): P1 2 bem menor que P2 6 (o atacante não 'sente' o contato)
- 3401 Chute da Corrente (finalizador): EnvShake por tempo (t14), treme mesmo errando e não sincroniza com o hitpause
- 3403 Queda Escura (especial): EnvShake por tempo (tNone), treme mesmo errando e não sincroniza com o hitpause
- 3410 Revolta de Corrente (forte): faísca de fraco (9200) em golpe forte
- 3410 Revolta de Corrente (forte): som de fraco (F5,0) em golpe forte
- 3411 Sola de Ferro (forte): faísca de fraco (9200) em golpe forte
- 3411 Sola de Ferro (forte): som de fraco (F5,0) em golpe forte
- 3412 Cabeçada Escura (forte): faísca de fraco (9200) em golpe forte
- 3412 Cabeçada Escura (forte): som de fraco (F5,0) em golpe forte
- 3413 Roda da Possessão (finalizador): EnvShake por tempo (t12), treme mesmo errando e não sincroniza com o hitpause
- 3420 Calcanhar Sombrio (forte): faísca de fraco (9200) em golpe forte
- 3420 Calcanhar Sombrio (forte): som de fraco (F5,0) em golpe forte
- 3421 Afastar Pesado (forte): faísca de fraco (9200) em golpe forte
- 3421 Afastar Pesado (forte): som de fraco (F5,0) em golpe forte
- 3423 Chute da Corrente Partida (finalizador): EnvShake por tempo (t16), treme mesmo errando e não sincroniza com o hitpause
- 3430 Mão de Chão Possuída (forte): EnvShake por tempo (t16), treme mesmo errando e não sincroniza com o hitpause
- 3431 Tranco Possuído (forte, golpe 1/2): faísca de fraco (9200) em golpe forte
- 3431 Tranco Possuído (forte, golpe 1/2): som de fraco (F5,0) em golpe forte
- 3431 Tranco Possuído (forte, golpe 2/2): faísca de fraco (9200) em golpe forte
- 3431 Tranco Possuído (forte, golpe 2/2): som de fraco (F5,0) em golpe forte
- 3432 Passo de Sombra (forte): EnvShake por tempo (t17), treme mesmo errando e não sincroniza com o hitpause
- 3433 Palma Torta (forte): faísca de fraco (9200) em golpe forte
- 3433 Palma Torta (forte): som de fraco (F5,0) em golpe forte
- 3434 Puxada Sombria (forte): faísca de fraco (9200) em golpe forte
- 3434 Puxada Sombria (forte): som de fraco (F5,0) em golpe forte
- 3435 Foice Escura (forte): EnvShake por tempo (t17), treme mesmo errando e não sincroniza com o hitpause
- 322 Ponta Rasteira (fraco): faísca em y=-70 mas a caixa de golpe está em y≈-12 (chão): o brilho aparece longe do ponto de contato
- 342 Ponta de Esquiva (fraco): faísca em y=-70 mas a caixa de golpe está em y≈-12 (chão): o brilho aparece longe do ponto de contato
- 349 Caneta Sombria (forte): faísca em y=-70 mas a caixa de golpe está em y≈-12 (chão): o brilho aparece longe do ponto de contato
- 430 Agachado chute fraco (fraco): faísca em y=-70 mas a caixa de golpe está em y≈-11 (chão): o brilho aparece longe do ponto de contato
- 440 Agachado chute forte (forte): faísca em y=-70 mas a caixa de golpe está em y≈-10 (chão): o brilho aparece longe do ponto de contato
- 1300 Caneta (especial): faísca em y=-70 mas a caixa de golpe está em y≈-12 (chão): o brilho aparece longe do ponto de contato
- 1301 Caneta (forte) (especial): faísca em y=-70 mas a caixa de golpe está em y≈-12 (chão): o brilho aparece longe do ponto de contato
- 1500 Sola de Várzea (especial): faísca em y=-70 mas a caixa de golpe está em y≈-20 (chão): o brilho aparece longe do ponto de contato
- 1501 Sola de Várzea (forte) (especial): faísca em y=-70 mas a caixa de golpe está em y≈-20 (chão): o brilho aparece longe do ponto de contato
- 3435 Foice Escura (forte): faísca em y=-70 mas a caixa de golpe está em y≈-11 (chão): o brilho aparece longe do ponto de contato
- 1000 Latada de Sombra fraca (projétil): acerto sem faísca própria (sparkno do [Data] = fightfx 2 do motor) e projhitanim 1006 de 10x15px por 6t: impacto quase invisível
- 216 Tranco de Ombro (forte): ground.velocity -3 não empurra mais que o fraco mais forte (|4.0|)
- 231 Puxada de Sola (forte): ground.velocity -3 não empurra mais que o fraco mais forte (|4.0|)
- 246 Passo de Letra (forte): ground.velocity -3 não empurra mais que o fraco mais forte (|4.0|)
- 311 Martelada (forte): ground.velocity -3.5 não empurra mais que o fraco mais forte (|4.0|)
- 312 Sola de Baixo (forte): ground.velocity -3.5 não empurra mais que o fraco mais forte (|4.0|)
- 331 Calcanhar de Roda (forte): ground.velocity -3.5 não empurra mais que o fraco mais forte (|4.0|)
- 341 Passo de Letra Cruzado (forte): ground.velocity -3.5 não empurra mais que o fraco mais forte (|4.0|)
- 344 Cotovelada de Recuo (forte): ground.velocity -3.5 não empurra mais que o fraco mais forte (|4.0|)
- 346 Calcanhar de Entrada (forte): ground.velocity -3.5 não empurra mais que o fraco mais forte (|4.0|)
- 348 Compasso Possuído (forte): ground.velocity -3.5 não empurra mais que o fraco mais forte (|4.0|)
- 410 Agachado soco forte (forte): ground.velocity -3 não empurra mais que o fraco mais forte (|4.0|)
- 601 Golpe no ar (forte): ground.velocity -3 não empurra mais que o fraco mais forte (|4.0|)
- 610 Golpe no ar (forte): ground.velocity -4 não empurra mais que o fraco mais forte (|4.0|)
- 611 Golpe no ar (forte): ground.velocity -3 não empurra mais que o fraco mais forte (|4.0|)
- 3410 Revolta de Corrente (forte): ground.velocity -3.5 não empurra mais que o fraco mais forte (|4.0|)
- 3411 Sola de Ferro (forte): ground.velocity -3.5 não empurra mais que o fraco mais forte (|4.0|)
- 3412 Cabeçada Escura (forte): ground.velocity -3.5 não empurra mais que o fraco mais forte (|4.0|)
- 3420 Calcanhar Sombrio (forte): ground.velocity -3.5 não empurra mais que o fraco mais forte (|4.0|)
- 3422 Armada Torta (forte): ground.velocity -3.5 não empurra mais que o fraco mais forte (|4.0|)
- 3431 Tranco Possuído (forte): ground.velocity -3.5 não empurra mais que o fraco mais forte (|4.0|)
- 3431 Tranco Possuído (forte): ground.velocity -3.5 não empurra mais que o fraco mais forte (|4.0|)
- 3433 Palma Torta (forte): ground.velocity -3.5 não empurra mais que o fraco mais forte (|4.0|)
- faísca 9200: 1º quadro 45x29 contra pico 60x75 no tick 10 — o estouro chega 10 ticks depois do contato, em vez de nascer grande
- faísca 9202: 1º quadro 13x13 contra pico 48x59 no tick 9 — o estouro chega 9 ticks depois do contato, em vez de nascer grande
- faísca 9230: 1º quadro 20x19 contra pico 60x73 no tick 6 — o estouro chega 6 ticks depois do contato, em vez de nascer grande
- faísca 9232: 1º quadro 20x19 contra pico 60x73 no tick 6 — o estouro chega 6 ticks depois do contato, em vez de nascer grande
- faísca 9204: 1º quadro 13x13 contra pico 48x59 no tick 9 — o estouro chega 9 ticks depois do contato, em vez de nascer grande
- faísca 9212: 1º quadro 35x28 contra pico 80x95 no tick 9 — o estouro chega 9 ticks depois do contato, em vez de nascer grande
- faísca 9213: 1º quadro 66x23 contra pico 80x95 no tick 9 — o estouro chega 9 ticks depois do contato, em vez de nascer grande
- faísca 9214: 1º quadro 79x20 contra pico 100x89 no tick 9 — o estouro chega 9 ticks depois do contato, em vez de nascer grande
- faísca 9215: 1º quadro 89x30 contra pico 96x80 no tick 10 — o estouro chega 10 ticks depois do contato, em vez de nascer grande
