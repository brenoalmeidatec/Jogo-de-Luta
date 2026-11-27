# Plano de conserto do Pengaró: fluidez, animação e efeitos

Conferi no código as linhas que sustentam o plano. Os pontos-chave batem:
- `Air.fluido` está em 268-282 e copia a caixa com `*q[2:]` na linha 280.
- `fim_da_folha` (742-745), `caminho_fluido` (818-822), `limpar_borda` (668-683), `alinhar_endiabrado` (714-722, só dx), `preset_despertado` (761-786) e `efeitos_cns` (789-815) estão onde os achados dizem.
- Também conferi o `[Data]` com `sparkno = 2` (1413-1414), o `projetil()` sem faísca (1579-1590), o `Fim Despertar` em Time = 0 (2107), o CMD em 2398-2422, o `Q(1005)` duplicado (949/1247) e o `Q(6)`, o `Q(100)` e o `Q(3100)` (1178/1195/1266).

**Encontrei três coisas que mudam conselhos dos achados:**

1. **O Hazaki usa o mesmo gerador.** O `gerar_hazaki.py:6-10` importa `montar_air`, `montar_cns`, `montar_cmd` e `montar_sprites`. Mexer em `Air.fluido` é seguro, porque só roda com `not self.hazaki` (linha 292). Já `projetil()`, `montar_cns` e o CMD são compartilhados. O 3000 do Hazaki usa `projetil(..., 3005, 3006)` (linha 2098). Todo conserto nesses lugares precisa de guarda `if not hazaki` ou de `FAISCA_POR_FORMA`.
2. **O 3100 não é só do Despertar.** A entrada (linha 2402) exige `(var(20) > 0) || (life <= 200 && power >= 2000)`, então o despertar-6 errou ao dizer que ele sai em qualquer forma. Sai fora do Despertar só com vida baixa, e isso parece intencional.
3. **O despertar-6 e o air-cns-4 propõem consertos opostos para o mesmo defeito.** Escolhi o air-cns-4 (passo 6.1), porque não mexe em dano.

---

## Grupos de duplicatas e causa única de cada um

| Grupo | Achados | Causa-raiz única |
|---|---|---|
| G1 Estalo _3→_4 nos quadros do meio | alinhamento-1, fluidez-ticks-2 | `animar_folha.py:168` (`ida = t <= 0.5`). Precisa de Blender |
| G2 Amostragem pula o _4 | alinhamento-9 | `gerar_pengaro.py:280` |
| G3 Cauda parada no último desenho | fluidez-ticks-1, parte do 3, 7 e 8 | `Air.fluido`: o último elemento sem caminho fica com todos os ticks num sprite só |
| G4 Loops que vão até o desenho 7 | fluidez-ticks-4 | linha 275: `fim_da_folha` usado também em ação de loop |
| G5 Chuva desenhada no corpo | objetos-projeteis-2 | `fim_da_folha` sem teto por folha (golaco), mais `N(3400)` em `pengaro_extra.py:148` |
| G6 Clsn1 fantasma | air-cns-1, air-cns-8 (caixa) | linha 280 copia `q[2]` para os subquadros, e as caixas são constantes por golpe |
| G7 Clsn2 única por ação ou ausente | air-cns-6, air-cns-7 | `Air.acao` (300-303) só escreve `Clsn2Default`, e o 700/705 recebe `[]` (901-903) |
| G8 Corpo endiabrado furado | despertar-2, filmagem-5, despertar-3 | `limpar_borda` (tinta e erosão nos buracos internos) e `recortar_quadros.tira_fundo` |
| G9 Tamanho do endiabrado | despertar-4, filmagem-4, air-cns-9 (endiabrado) | não há escala por folha em `preset_despertado` e `alinhar_endiabrado` |
| G10 Pés do endiabrado e do meio fora do chão | alinhamento-4, despertar-5, despertar-8 (item 1) | ninguém reancora em y (`paste((dx, 0))`) |
| G11 dx medido em quadro entortado | alinhamento-3 | `alinhar_endiabrado` mede `centro_tronco` em cada m_ |
| G12 Ações montadas com desenhos soltos | alinhamento-7, fluidez-ticks-3, despertar-7, alinhamento-10 (relatório) | definições antigas (1266, 1268/`quadros_golpe`, 1234, 1269) com `TROCA_POR_FOLHA` entre folhas |
| G13 Transições secas | alinhamento-5, alinhamento-6, fluidez-ticks-5, fluidez-ticks-6, air-cns-9 (ação 6 normal) | `Q(5/6/40/47/100/120/140/12x)` antigas ou incompletas |
| G14 Emendas entre folhas | alinhamento-8, fluidez-ticks-7 (831/841/1701/2000) | `AGARRAO_WHISKY` (39-42) e `ESPECIAIS_A_MAO` |
| G15 Mesmo desenho repetido | fluidez-ticks-7 (3000) | `caminho_fluido` recusa quando `de[1] == para[1]` |
| G16 Faísca do motor nos projéteis | efeitos-1, objetos-projeteis-4, air-cns-2, filmagem-2 | `projetil()`, Dobrada, Garrafa e Mão sem `faiscas()`, mais `[Data]` 2/40 |
| G17 Acerto do projétil é a lata | efeitos-3, objetos-projeteis-3, objetos-projeteis-9, air-cns-3 | `projhitanim/remanim = 1006/3006` |
| G18 Mão de Sombra = bolão | efeitos-2, objetos-projeteis-1, filmagem-1 | `[State 3400, Mão]` usa 3005/3006 do Hazaki |
| G19 Dourado e garrafa no endiabrado | efeitos-4, efeitos-10, filmagem-3 | `projhitanim = 9200` fixo, `S9204` fixo e `projanim 3010` sem forma |
| G20 Posição dos efeitos de golpe | efeitos-5, efeitos-6, efeitos-7, efeitos-9, air-cns-8 (efeito) | `hitdef` com `sparkxy -70` literal e a heurística de `efeitos_cns` (805-808) |
| G21 Aura e sombra dos pés | filmagem-6, filmagem-7, efeitos-15 (parte) | Explods no `-3`, que roda antes do `-2` e não roda em estado custom. A 9211 tem `bindtime -1` |
| G22 "Volta ao normal no meio da luta" | despertar-1, efeitos-15 (parte), filmagem-8 (ida) | `filmar_luta.py:65-66` religa o Despertar por `gametime %`. **Não é defeito do jogo** |
| G23 Lógica do Despertar | air-cns-4 ≈ despertar-6, despertar-9, filmagem-8, despertar-10, despertar-11 | o bloco `-2` (2170-2230) e a linha 2107 |
| G24 Auditor com falso positivo | alinhamento-2, 10, 11, 12 | `auditar_pengaro.py` (`centro_tronco`, `NOVOS`, sujeira, pés) |
| Isolados | fluidez-ticks-10 (emenda andar/ginga), fluidez-ticks-11 e objetos-projeteis-10 (giro 3 ticks e `Q(1005)` duplicado), objetos-projeteis-5 (lata atrás da cabeça), objetos-projeteis-6 e 7 (onde o objeto nasce), objetos-projeteis-8 (limite de projéteis), efeitos-8 (recorte das folhas fx), efeitos-11 (doc), efeitos-12 (poeira violeta), despertar-8 (holds da 2000) | cada um na sua linha |

---

## Ordem de execução

A ordem segue três critérios. As ferramentas de medida vêm primeiro, porque sem elas não dá para verificar nada. Depois vêm as imagens, porque a escala e a âncora medem em cima delas. Por último entram o motor de animação (`Air.fluido`), as definições de ação, o CNS e a lógica do Despertar.

**Linha de base em todo passo:** rodar `auditar_pengaro`, `conferir_tempo`, `conferir_despertar`, `verificar_pengaro`, `testar_pengaro` (126 PASS ou mais) e regenerar o Hazaki (`gerar_hazaki.py`), conferindo que o .air e o .cns dele **não mudaram** (diff). Ao fim de cada fase, acrescentar uma entrada no `LOGBOOK.md`.

### Fase 0: confiar na régua (só ferramentas, sem risco)

**0.1 Auditor (G24).** Arquivo: `auditar_pengaro.py`.
- Linhas 133-135: o aviso "corpo pula" só sai quando o centróide da máscara também anda mais de 12 px.
- Linhas 122-123: um nome que está em `g.TROCA_POR_FOLHA` conta como novo, e o relatório "arte antiga" vira "cortes entre folhas", com 1-IoU acima de 0,5.
- Sujeira: pular as folhas `despertar_*`, ou acusar só pedaço que não existe nas chaves vizinhas.
- Pés absolutos (linha 125): medir por trecho de folha aérea (bicicleta, ar_soco, pulo, armada 3-5), não pelo número da ação.
- **Não** aplicar `NO_AR` ao teste do endiabrado: ele é relativo e expõe o G10.
- Acrescentar a razão de altura endiabrado/normal por ação, com alarme fora de 0,9-1,1.

Para conferir: a lista de "arte antiga" fica vazia, os avisos de "corpo pula" em 831/333/348/1100/3403/5120 somem e os avisos de pés da 5050/1200 continuam.

**0.2 Verificador.** Arquivo: `verificar_pengaro.py`. Acrescentar a regra "sobra de Clsn1 > 12 px é erro", usando a medição do `checar_air_cns.py`/`med.py` da frente air-cns. Começar como **aviso**, para não travar antes da Fase 3. Também conferir por grep que todo HitDef, Projectile e ReversalDef defensável tem `sparkno` e `guard.sparkno`.

**0.3 Filmagem (G22).** Arquivo: `filmar_luta.py` `main()`, linhas 62-67. Trocar o `gametime % N` por uma ativação única e real: `PowerSet powermax` mais `ChangeState 2000`, com o gatilho `roundstate = 2 && var(X) = 0 && gametime >= N*60 && statetype = S && ctrl`, e um `VarSet var(X) = 1`. X é uma var livre, a confirmar por grep no .cns gerado.

Para conferir: refilmar e ver que o endiabrado volta ao normal **uma vez só**, cerca de 600 ticks depois da cutscene, e que a cutscene aparece. O sintoma "volta ao normal no meio e depois volta a endiabrado" deve sumir. Se ainda aparecer um quadro normal com aura, é o G21 (passo 5.6).

### Fase 1: imagem do endiabrado (base da escala e da âncora)

**1.1 `limpar_borda` (G8, despertar-2 e filmagem-5).** Arquivo: `gerar_pengaro.py:668-693`.
- (a) Criar o parâmetro `tinta=True`. O `abrir_quadro` passa `tinta=False` quando o caminho contém `e_`, `endiabrado/`, `ginga_endiabrada/` ou `despertar_b/`.
- (b) Calcular a borda **só contra o fundo externo**: `externo` vem de um flood-fill do transparente a partir das bordas, e `borda = cheio & dilate(externo)`.
- Manter o filtro de componentes com menos de 6 px.
- **Não** usar o corte por brilho (`r > 120`), porque ele devolve a franja do normal.

Para conferir: a perda de pixels no endiabrado cai de cerca de 18-27% para menos de 5%, a perda no normal continua perto de 3%, os "pedaços soltos" da 2000 (q75-99) diminuem e o pé da ginga_endiabrada/00 volta a colar no corpo.

Riscos: o normal muda pouco, porque a borda externa é a mesma, mas a franja em volta de vãos internos legítimos vai sobrar. Conferir o soco e o compasso a olho. O Hazaki não usa `abrir_quadro`, então não é afetado.

**1.2 `tira_fundo` (despertar-3).** Arquivo: `recortar_quadros.py:23-31`. Apagar o componente magenta ligado à borda e, nos internos, só os de cor de fundo pura (mediana com `r >= 235`, `b >= 235` e `g <= 20`). O flood fill puro deixaria magenta opaco nos vãos fechados. Depois, recortar de novo **só as chaves** das folhas `e_*`, `endiabrado/` e `ginga_endiabrada` com o mesmo `--escala`.

Para conferir: os buracos internos das chaves e_ ficam perto dos do normal (0-3 px por quadro).

Limite: os `e_*/meio/` vêm do Blender e continuam furados. O paliativo é fechar no gerador buracos internos de até 40 px, cercados por corpo, só nos `e_*`, com `MORPH_CLOSE` no alfa e `inpaint` na cor. **Nunca** fechar vãos de até 300 px.

### Fase 2: geometria do endiabrado (escala, depois y, depois x)

Tudo isso fica numa única função de colagem, chamada no lugar de `alinhar_endiabrado`, com um só `paste`. Não se cria camada nova.

**2.1 Escala por folha (G9).** Em `preset_despertado` (761-786), criar um cache `fator[folha] = mediana(altura normal) / mediana(altura endiabrada)` nas 8 chaves, contando só o maior componente e limitando a 0,75-1,3.
- O **mesmo** fator vale para `e_<folha>/meio/*`, para a `ginga_endiabrada` (contra a ginga_fluida) e para o fallback `endiabrado/` e o `arte_endiabrada` (2572).
- Redimensionar com `resize NEAREST`, ancorado na base (`EIXO_Y-1`) e no centro do tronco.

Para conferir: a razão por folha fica entre 0,95 e 1,10 e a troca ginga→andar muda a altura menos de 10%. Antes, ia de 139 para 102.

Risco: as Clsn vêm do AIR normal, então não mudam. O visual do endiabrado fica menor, e é bom avisar o usuário.

**2.2 Âncora vertical (G10).**
- **No endiabrado:** `dy = base(normal) - base(endiabrado)` (última linha com alfa >= 128), aplicado só quando o normal está no chão (`|base - (EIXO_Y-1)| <= 3`), com limite de ±12. Fazer depois da escala.
- **No normal:** em `caminho_fluido`, ao registrar cada `m_` (linha 835), se a base desviar mais de 3 px da interpolação linear das bases das duas chaves e as duas chaves estiverem no chão, deslocar só em y, com limite de ±10. Isso cobre o `m_despertar_b_05_3/05_4` (226/216 contra 219).
- Não aplicar a quadros de folhas aéreas.

Para conferir: o `e_m_armada_05_3→05_4` deixa de pular 15 px, os 41 quadros com o pé fora do chão no Despertar caem para cerca de 1 e o aviso de pés do 2000 some.

**2.3 dx pelas chaves (G11).** Calcular o dx só em `f_<folha>N` contra `e_<folha>/N.png`. Para `m_<folha>_NN_k`, usar `round(lerp(dx[N], dx[N+1], k/7))`, passado como parâmetro. Manter o limite de ±24.

Para conferir: o p95 da diferença de centróide normal/endiabrado nos m_ não piora mais (hoje vai de 10,9 a 12,6).

### Fase 3: motor de animação (`Air.fluido`, 268-282). É onde a fluidez mais ganha

Fazer um sub-passo por vez, rodando o robô entre eles. A regra fixa de todos: **o tick total de cada elemento original e o `self.mapas` não mudam**.

**3.1 Amostragem (G2).** Quando o `caminho` tiver os 6 quadros do meio e `n >= 2`, incluir sempre os índices do _3 e do _4 e espalhar o resto. Isso não muda nem a soma nem o mapa. É o único paliativo do G1 sem Blender.

**3.2 Teto por folha (G5).** Criar `ULTIMO_DESENHO = {"golaco": 4}`, respeitado em `fim_da_folha` (devolve None no teto) e em `caminho_fluido`, como trava. Em `pengaro_extra.py:148`, trocar por `"golaco 1/5 2/6 3/5 4/26"`, que mantém o total e o tick do `ini[3]`.

Para conferir: a medição de pedaços soltos (`soltos.py`) dá 0 elementos com pedaço solto no 3000/13000/3400.

**3.3 Destino `seguinte` para loops (G4).** Criar `Air.acao(..., seguinte=None)`. Na linha 275, o último elemento usa `seguinte`, ou, se a ação tem `loop`, o `quadros[loop or 0][0]`. O `fim_da_folha` fica só para os golpes. Antes de marcar uma ação como loop, conferir no CNS/common que ela não acaba por AnimTime. Ações encadeadas: 10→`f_agachado4`, 40→`f_pulo1` (resolve o 40), 120/140→`f_defesa3`.

Para conferir: o 130 deixa de passar pelas poses 5 e 6, e o 11 e o 5300 fecham o ciclo sem salto.

**3.4 Cauda parada (G3), sem arte nova.** Só dentro do último elemento:
- (1) se o elemento anterior é recuperação (sem `q[2]`), mostrar o caminho dele com 2 ticks por sprite e passar o que sobrar para o começo do último elemento;
- (2) no resto da cauda, fazer um vai-e-volta entre `f_X7` e `m_X_06_4..6`, com no máximo 2 ticks por sprite;
- **nunca** num elemento com caixa;
- o `+6` da linha 343 continua e entra no vai-e-volta.

Para conferir: no `conferir_tempo`, o motivo `ultimo_sem_proximo` sai das ~130 ocorrências e 1797 ticks.

Risco: o AnimElem não muda, mas é bom conferir `remapear_animelem` (840).

**3.5 Mesmo desenho repetido (G15).** Quando `de == para`, ou quando elementos seguidos usam o mesmo sprite, fazer um vai-e-volta `f_golaco4 ↔ m_golaco_04_1..3` com no máximo 2 ticks, **mantendo os 7 elementos**, porque o 5º solta as bebidas por `AnimElemTime(5)`.

**3.6 Poses -1 no ar (fluidez-ticks-8).**
- No 44-46: loop com Loopstart, num vai-e-volta `f_pulo6 ↔ m_pulo_05_5/4` de 1-2 ticks.
- Nos aéreos 600, 650, 1200 e 3403: o mesmo, no fim.
- Conferir que o índice do Loopstart passa pelo `self.mapas` (linha 294).
- Deitado, vitória e derrota ficam como estão.

Confiança média: os ~11 ticks parados vêm de cálculo, não de medida no jogo.

**3.7 Clsn1 por sprite (G6).** Ficar com a **opção b** do air-cns-1. A opção a seguraria o pico por vários ticks e violaria a regra de no máximo 2 ticks. O plano:
- continuar expandindo o elemento ativo;
- recalcular o `x2` da Clsn1 de cada subquadro pelo pixel opaco mais à frente na faixa `y1..y2`, mais 4 px;
- largura mínima de 12 px, para nunca zerar a caixa num tick ativo;
- aplicar em `Air.acao` na hora de escrever o `Clsn1`, com acesso à imagem por `self.s`;
- cobrir também o `giro` (922/1249), as tuplas do `repertorio.py` e o `m.caixa`;
- **não** apagar a caixa no pós-pico.

Para conferir: as violações acima de 12 px caem de 408/593 para perto de 0, e a regra 0.2 vira **erro**.

Risco alto: o alcance encolhe, então o robô e a conferência de golpe precisam passar e é preciso avisar que o alcance mudou. A Clsn2 no membro (air-cns-1c) fica como **decisão do usuário**.

**3.8 Clsn2 (G7).** Mínimo e sem risco: passar `BAIXO` para 700/705 (901-903) e para 841/1700. Isso abre a janela de punição no fim do rolamento, então rodar o robô. Completo: Clsn2 do tronco por quadro, com o topo opaco menos 4, quantizado em degraus de 8 px. É mudança de equilíbrio e fica como decisão do usuário.

### Fase 4: redefinir ações (`acoes_folhas` e `pengaro_extra`, que ganham pela regra "primeira definição vale")

Regra para todos os passos: manter o total de ticks, o tick de início e a duração de cada caixa e, quando o CNS usa AnimElem, também a quantidade e a ordem dos elementos. Se não der, passar pelo `remapear_animelem`. **Não tocar no `repertorio.py`**, porque o Hazaki usa.

1. **6:** `Q(6, [(f("agachado", 4), 3), (f("agachado", 5), 3)], BAIXO)`. O par 4→5 mede 0,05, contra 0,63 hoje. **5** (opcional): `[("q_ginga_fluida0", 3), ("q_ginga_fluida2", 3)]`. Não usar flip a meio caminho sem testar no jogo.
2. **100:** `Q(100, [(f"q_anda_fluida{i}", 1) for i in range(0, quadros_do_loop("anda_fluida"), 3)])`, com 16 ticks. Conferir se algum trigger usa AnimElem da 100.
3. **47:** vai-e-volta `f_pulo7 ↔ m_pulo_06_6` no lugar do corte para `f_pulo0`. Um `seguinte` sozinho não liga folhas diferentes. **120/140:** defesa 1→2→3. **121/131/141:** entrar por `f_agachado5→7`, e **131/132** ganham loop de respiração como o 130. **122/132/142/152:** caminho defesa 4→5.
4. **20/21/9203 (fluidez-ticks-10):** tirar o quadro 47 (no 9203, o 63) e também os quase-repetidos de dentro do ciclo (anda 43, ginga_endiabrada 57), ou dar 1 tick a eles. Conferir se o passo não descasa no chão.
5. **3100 (G12, despertar-7):** reescrever com trechos de folha, mantendo os 8 elementos ativos com `caixa_p` nos ticks 4, 8, …, 32, 4 ticks cada, e os 20 finais. Os desenhos de passagem entram sem caixa e tiram ticks dos trechos parados. Rodar o robô (o 3100 está nos testes de super).
6. **Golpes do repertório no Pengaró** (201, 216, 231, 246, 601, 611, 1400, 1401, 1500, 1501, 3200) e **610 e 760:** versões em `ESPECIAIS_A_MAO`/`acoes_folhas` com a folha mais parecida: 246 com chute_alto 1-7, 601 com ar_soco, 611 com bicicleta, 1400/1401 com martelo, 1500/1501 com chute_baixo ou armada, 760 com defesa 2→6. Manter liga, ativo e recuperação de cada `Golpe` e o AnimElem usado pelo `cns_repertorio` (1620). Isso também resolve a caixa do pisão (air-cns-8).
7. **Emendas (G14)** do 831, 1701 e 841: escolher o desenho de emenda pelo maior IoU entre os candidatos do fim do trecho A e do começo do trecho B, sem desenho novo e mantendo os ticks dos elementos com caixa. Enquanto não houver pose de ligação, o quadro antes do corte não pode passar de 2 ticks: fazer um vai-e-volta com o m_ vizinho. O 2000 (0,39) fica como está.
8. **2000 (despertar-8):** trocar os holds do a7 (6 ticks) e do b7 (10 ticks) por vai-e-volta de no máximo 2 ticks, mantendo os 114 ticks (o Afasta e o Liga dependem disso). **Não** mudar o `movetime` da superpausa.
9. **Limpeza:** apagar o `Q(1005)` de quica (linha 1247) e o laço `quicaN` (1074-1078), depois de grep para ver que nada usa.

### Fase 5: efeitos no CNS

1. **Faíscas dos projéteis (G16).** Em `projetil()` (1579), na Dobrada (2042-2046), na Garrafa (1873-1879) e na Mão (1911-1917), acrescentar `*faiscas(9200)`, ou 9201 nos pesados. Para o Hazaki, isso troca a faísca do motor por S9200/S9202. Ou se aceita a troca (o Hazaki carrega `carregar_faiscas`, mas é preciso conferir que a 9200 existe nele), ou se põe a guarda `if FAISCA_POR_FORMA`. Na `chuva_de_bebidas`, acrescentar só o `guard.sparkno`. O `[Data]` só muda para `-1` depois que o grep do 0.2 provar que tudo é explícito. Não usar `S` no `[Data]`, que não foi conferido.
   Para conferir: não aparece mais a estrela branca na filmagem (q114).
2. **Acerto do projétil (G17).** `projhitanim/remanim = {fx_forma(9200)}` na Latada e na Dobrada, e `{fx_forma(9201)}` na Garrafa e na Mão. Se o hitanim fizer o papel da faísca, usar `sparkno = -1` para não duplicar. Depois, tirar o 1006 (e o 3006 no Pengaró) do gerador e do "livres" do `verificar_pengaro.py:97`. **O `Q(3005)/Q(3006)` vai para dentro de `if hazaki`**, porque o Hazaki usa no 3000.
3. **Forma (G19).** Chuva com `projhitanim/remanim = {fx_forma(9200)}`. `reversao()` (1755) com `S(ifelse(var(20) > 0, 9234, 9204))` quando `FAISCA_POR_FORMA`. Garrafa no Despertar: acrescentar `var(20) = 0` na lista `garrafa` do CMD (linha 2413), que é a opção mais barata. Se o usuário preferir arte, ver a seção do Breno. Conferir a IA e os cancelamentos que entram no 1600/1601.
4. **Limite de projéteis (objetos-projeteis-8).** Linhas 2410/2414/2420: `numprojid(1000) + numprojid(1001) + numprojid(1002) + numprojid(1003) = 0`. Não usar `numproj`, que contaria a chuva.
5. **Posição dos efeitos (G20).**
   - `hitdef(..., caixa=None)` com `sparkxy = -10, clamp(-70, min(y)+4, max(y)-4)`.
   - Em `efeitos_cns`: `x = max(x1, x2) - 8` na faísca e na poeira.
   - Chão só se `max(y) >= -25 and abs(y2 - y1) <= 30` e a ação não for aérea (600-699, 3403).
   - Tirar de `efeitos_cns` a 760/10760, a 800/830/840 com as 1xxxx, a 1500/1501 e a 3403, porque já têm o Impacto/Estouro 9235.
   - Gerar a forma `var(20) > 0` da ação normal só quando `anim + 10000` não estiver em `ativos`, o que elimina o código morto.
6. **Aura (G21).** Mover o Explod e os RemoveExplod da 9210/9211 do `-3` para o `-2`, logo depois de "Volta ao normal". O gatilho de remoção é `var(20) <= 0 || !alive`. A 9211 ganha ainda `statetype != A` na criação e `|| statetype = A` na remoção. Não usar `ModifyExplod` por tick.
   Para conferir: q98 sem aura sobre o normal e q94 sem o anel no ar.

### Fase 6: lógica do Despertar (bloco `-2` e linha 2107)

1. **Arte do 3100 (air-cns-4, no lugar do despertar-6).** Manter `var(20) = 0` em Time = 0, o que preserva o dano (`AttackMul 1.45`) e o custo. No `-2`:
   - aplicar o preset com `trigger1 = (var(20) > 0 || stateno = 3100) && var(37) = 0`;
   - resetar com `var(20) <= 0 && stateno != 3100 && var(37) = 1`.

   Ressaca: hoje ela é pulada, porque "Ressaca começa" exige `var(20) = 1`. Se a ressaca for desejada, a opção é `var(20) = 2` em Time = 0 (o `-2` decrementa para 1 e a ressaca dispara). Só vale depois de conferir a ordem real de "Conta Despertar" e "Ressaca começa" no texto gerado. Confiança média.
   Para conferir: o 3100 no Despertar aparece endiabrado do começo ao fim, e o robô do super passa.
2. **Zerar no intro (despertar-11).** No `-2`, antes de "Conta Despertar", acrescentar `VarSet var(20)/var(21)/var(37) = 0` com `roundstate < 2`. O motor só zera as vars no primeiro round (`common1 5900`).
3. **Saída com fumaça (despertar-9, filmagem-8).** Com `var(20) = 12`, Explod 9215 (fumaça violeta), uns 20 ticks, `postype p1`, `ownpal 1`, `sprpriority` acima do corpo, `ignorehitpause` e `supermovetime -1`. Fazer depois da Fase 2, para não haver mais salto de tamanho.
4. **Barra drenando (despertar-10). Decisão do usuário.** A proposta: tirar o `PowerAdd -3000`, drenar `-5` por tick no `-2` e encerrar com `power <= 5`. Também é preciso decidir sobre o ganho de barra ao acertar e apanhar. O robô pode depender de `power >= powermax`.

---

## O que precisa do Breno (arte nova ou Blender) e o que se resolve só com código

**Precisa de arte ou Blender (fica para o Breno):**
- **G1 (estalo _3→_4):** renderizar de novo os `meio/` com mistura dos dois fluxos no `animar_folha.py`, ou desenhar chaves extras para as passagens do `piores_intervalos.txt`. No gerador, só o 3.1 ajuda um pouco. **Não** adotar o "corte seco acima de 0,6" (medido, piora) nem o DIS duplo sem aprovação visual quadro a quadro. Registrar no LOGBOOK como limitação conhecida.
- `e_*/meio/` furados (o resto do G8) e com tamanho e pé errados: o gerador remenda (Fases 1 e 2), mas a causa está no render.
- Arte da **Mão de Sombra**, uma folha `fx_mao_sombra` em ações **livres**, como 3007/3008. **Não** usar 3420/3421, que já são golpes. Clsn1 tirada do contorno, com tamanho perto de 40x30 para não mudar o alcance. Paliativo: sombra violeta com caixa do desenho. A 9212 não serve, porque não tem Clsn1.
- **Projétil endiabrado** (lata ou garrafa de sombra) para a Latada e a Garrafada no Despertar, se o usuário não quiser só bloquear a Garrafada.
- Folha de **corrida** própria (o 4.2 é paliativo), **poses de ligação** para 831/1701/841, **pontes `m_volta_*`** para a ginga e **cacos** da 2000 (conferir antes se eles somem mesmo no corte a7→b0).
- Troca lata→garrafa e garrafa que fica na mão de trás na folha `bola` (objetos-projeteis-6b e 7.4).
- Folha própria de **poeira violeta** (efeitos-12). O paliativo em código é apontar a 9215 para `sombra_forte` no CHAO, depois do efeitos-8.

**Só com código, sem arte:**
- Fases 0 a 6 inteiras.
- **efeitos-8:** o recorte por componentes em `efeitos_folha.py` `recortar()` e `enquadrar()`, rodando de novo sobre as folhas fx que já existem. Critério: 0 quadros com corte reto de 8 px ou mais nas laterais e no topo.
- Lata solta em `bola/05` e nos `meio/04_*` (objetos-projeteis-5): limpar na fonte com a ferramenta de recorte, ou um filtro de componente restrito à folha `bola`, conferindo que nenhum item preso à mão sai junto.
- Ponto onde o objeto nasce (objetos-projeteis-6 e 7): mudar só o elemento do trigger e o offset, **medidos no sprite** (não remedi os números dos achados), e uma garrafa voando em escala 1. Atenção: a Clsn menor encolhe o alcance da Garrafada, então rodar o robô.
- Giro de 8 rotações dos projéteis (fluidez-ticks-11), em pixel art à mão no `itens_pengaro.py`. Baixa prioridade.

## Decisões que são do usuário

- **efeitos-11:** a recomendação é manter o efeito opaco e corrigir `docs/conferencia-de-golpe.md:29`.
- **despertar-10:** barra drenando, e o que fazer com o ganho de barra durante o Despertar.
- **air-cns-1c e air-cns-6:** Clsn2 no membro e Clsn2 por quadro, que mudam o equilíbrio.
- **efeitos-10 e filmagem-3:** arte nova ou bloqueio da Garrafada no Despertar.
- **3100:** manter a regra de vida baixa fora do Despertar, ou deixar só no Despertar.

## Riscos transversais

- Frame data: os passos 3.7, 3.8, 4.5, 4.6 e 5.2 mexem em alcance, janela ou elementos. Rodar o robô depois de **cada** um.
- AnimElem: 3000 (elemento 5), 1000 (elemento 13 remapeado), cns_repertorio e 3100. Nada pode mudar a quantidade de elementos sem passar pelo `remapear_animelem`.
- Hazaki: tudo o que toca `montar_cns`/`montar_cmd`/`projetil`/`Q(3005)`/`Q(3006)` precisa de guarda, e o diff do .air e do .cns do Hazaki tem que dar vazio.
- No jogo: nada deste plano foi visto rodando. A filmagem (com o 0.3 consertado) e o robô são a verificação no nível do jogador. O que não der para observar fica declarado como não verificado, e não como "funcionou".