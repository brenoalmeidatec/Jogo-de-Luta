# Especificação final de impacto estilo KOF para o Pengaró

O texto é para um único implementador. Os nomes de função, linhas e parâmetros foram conferidos em `ferramentas/gerar_pengaro.py`, `gerar_hazaki.py` e `pengaro_extra.py` na branch `mugen`. Nada no repo foi editado e nada foi testado em jogo.

## 0. Antes de tudo: o volume está zerado

O `%USERPROFILE%/JogoDeLuta/ikemen/save/config.ini` tem `MasterVolume = 0` e `PauseMasterVolume = 0`, segundo o ângulo de som. Com isso nenhum impacto sai no alto-falante, e boa parte do "não machuca" pode ser só isso. Quem decide é o usuário ou o Breno; o implementador **não deve mexer** nesse arquivo.

## 1. Conflitos entre as propostas e como resolvi

| Ponto | Escolha | Por quê |
|---|---|---|
| Congelamento do fraco: 9,9 (tempo) ou 8,8 (reação) | **8,8** | Fica acima do piso de 6 e mantém a corrente fluida; fluidez é prioridade. |
| Classe "médio" | **Entra**: dano de 45 a 84 no `cns_novo` | É a causa das 25 incoerências de faísca e som, porque `pesado=dano>=75` não bate com `forte=dano>=85`. |
| Especial: 13,13 ou 12,12 | **12,12**, igual ao forte | Uma linha a menos na tabela, e cumpre o piso de 10. |
| Golpe final do super: 22,22 ou 20,20 | **20,20** | É fluidez, e o motor já faz câmera lenta no KO. |
| Acertos do meio do 3100: 4,6 ou manter 2,6 | **3,6** | São 8 acertos, então o golpe fica só +8 ticks mais longo, não +16. |
| `freq` do EnvShake: 60, 90 ou 150 | **150** (170 nos acertos do meio do super) | É o tranco seco; o `kfm.cns` usa 176–178. |
| Projétil | **Só o P1 sobe; o P2 fica igual** | O P1 congela o projétil e não o dono, então isso é visual puro e a vantagem de quadros não muda. A exceção é a última garrafa da Chuva. |
| Contra-ataque com `pausetime` por expressão `P2MoveType` | **Rejeitado** | O HitDef avalia o valor quando liga, não no contato. No lugar, efeito extra em `MoveHit = 1 && MoveCountered` (fase 2). |
| Flash | **Só BGPalFX cinza no golpe final do super**, `time=4` | Não pinta sprite (bíblia: sem mistura), e cinza somado ao azul não fica rosa. AllPalFX está descartado. |
| PalFX de brilho no lutador durante a superpausa | **Descartado** | É camada nova. No lugar, o AfterImage `trans=add` roxo vira cinza (`palcolor=0`), que tira a armadilha do rosa sem somar efeito. |
| `palfx.*` na vítima | **Fora**, até o Breno aprovar | Contraria a bíblia ("sem mistura") e não foi visto rodando. |
| Poeira extra na vítima | **Fora** | O motor já faz F60/F7 na queda. Seria camada em cima de camada (regra global do usuário). |
| Rastro 9212–9215 | **Fica** só em médio para cima, a 0.75x, com `removetime = 8` | O golpe que erra não pode parecer acerto. |
| `.snd` próprio | **Fase 2**, com chave `SOM_PROPRIO` | O empacotador bate byte a byte com o `common.snd`, mas ninguém ouviu os sons e o motor nunca carregou o arquivo. A fase 1 usa F5,0–F5,4 do motor; F5,3 e F5,4 estão sem uso hoje. |
| `RITMO = 1.5` (o windup longo) | **Fase 3**, separada e com medição | É a maior causa do "mole", mas mexe no AIR, nos triggers `Time = N` e no robô. |

## 2. Tabela por classe

O `localcoord` é 320x240. EnvShake e `fall.envshake` vão **dentro do HitDef** (`envshake.time/freq/ampl` e `fall.envshake.time/freq/ampl`), então só tremem no acerto. O `fall.envshake` entra só quando `queda=True`.

| Classe | pausetime P1,P2 | guard.pausetime | envshake (t, f, a) | fall.envshake | Faísca (normal/endiabrado) | sparkscale | hitsound (fase 1 / fase 2) | animtype | ground.velocity / slidetime | Flash / AfterImage |
|---|---|---|---|---|---|---|---|---|---|---|
| **fraco** | 8,8 | 6,6 | — | — | S9200/9230 | 1, 1 | F5,0 / S1,0 | Light | -4 / 5 | — |
| **médio** | 10,10 | 8,8 | — | — | S9201/9231 | .9, .9 | F5,1 / S1,1 | Medium | atual (-3.5) / 7 | — |
| **forte** | 12,12 | 9,9 | 6, 150, -3 | 6, 150, -2 | S9201/9231 | 1.15, 1.15 | F5,2 / S1,1 | Heavy (Back/Up onde já estão) | -6, ou o atual se já for mais forte / 8 | rastro a 0.75x |
| **especial** | 12,12 | 9,9 | 8, 150, -3 | 6, 150, -3 | S9201/9231 | 1.15, 1.15 | F5,2 / S1,1 | o atual | o atual | AfterImage curto (fase 2) |
| **finalizador** | 16,16 | 10,10 | 12, 150, -5 | 8, 150, -3 + `fall.recovertime = 30` | S9205/9235 | 1.3, 1.3 | F5,3 / S1,2 | Heavy/Back/Up atual | o atual / 8 | — |
| **super (acertos do meio)** | 3,6 | 2,6 | 3, 170, -1 | — | S9201/9231 | 1, 1 | F5,1 / S1,0 | Medium | o atual | — |
| **super (golpe final)** | 20,20 | 12,12 | 20, 150, -6 | 12, 150, -4, `fall.recover = 0` | S9205/9235 | 1.5, 1.5 | F5,4 / S1,2 | Back/Heavy atual | o atual | BGPalFX `time=4, add=128,128,128` em `MoveHit = 1`, com `ignorehitpause = 1` |
| **projétil** (lata, garrafa) | **4**,10 (o P2 não muda) | — | — | — | S9200 (troca a fightfx) | 1, 1 | F5,1 / lata S1,0, garrafa S4,0 | Med | o atual | — |
| **projétil forte** (Mão de Sombra 3400) | **8**,10 | — | 6, 150, -3 | — | S9201 | 1.15 | F5,2 / S2,1 | Med | o atual | — |
| **Chuva de Bebidas** | garrafas 1–5: 4,10 · última: 12,14 | — | última: 8, 150, -4 | última: 8, 150, -3 | S9200 / última S9205 (hoje `-1`) | 1 / 1.3 | F5,2 / última S1,2 | atual | atual | — |
| **agarrão** (810, 831, 841) | — | — | EnvShake fora do HitDef no tick do `TargetLifeAdd`: 810 recebe 8, 150, -3 (hoje não tem nada); 831 e 841 mantêm | — | 9201 (como o 831) | — | 810 recebe `PlaySnd F5,2` | — | — | — |
| **contra-ataque** (fase 2) | igual à classe | — | EnvShake extra 4, 150, -2 em `MoveHit = 1 && MoveCountered`, `ignorehitpause = 1` | — | Explod 9207/9237 (anel gerado do quadro F, 1.2x), só no Pengaró | — | `PlaySnd F5,3` | — | — | — |
| **defesa** | — | coluna acima | — | — | **S9202 nas duas formas**, recolorida neutra | .9, .9 (`guard.sparkscale`) | `guardsound` F6,0 (fica) | — | `guard.velocity` = padrão | — |

**Posição da faísca:** `sparkxy = -10, Y`, com `Y = clamp((y1+y2)//2, -95, -10)` da Clsn1 ativa do estado. Sem caixa, fica em -70. Isso corrige os 10 golpes baixos.

**Tempo da faísca (AIR):** o maior quadro aparece no tick do contato e a faísca some em 9 a 14 ticks. `F` é o quadro de flash gerado por código.

- fraco: `F@.8x 1, F 1, q8 1, q10 1, q12 1, q14 2, q17 2` (9 ticks)
- forte e médio: `F@.9x 1, F@1.1x 2, q4 1, q6 1, q8 1, q10 2, q13 2, q16 2` (12 ticks)
- finalizador: `F 1, F@1.25x 2, q2 1, q4 1, q6 1, q8 2, q11 2, q14 2, q18 2` (14 ticks)
- defesa: `q3 1, q6 1, q9 1, q12 1, q15 2` (6 ticks)

**Reações de apanhar:** a vítima congela no 1º elemento da 5000/5001/5002 durante o shaketime. A duração total fica igual à de hoje.

- Light: `[(2,4),(3,3),(1,6)]`
- Medium: `[(3,4),(4,5),(5,5),(1,3)]`
- Hard: `[(4,6),(5,5),(3,4),(1,2)]`

Os índices são da folha `apanha`. Hoje a 5001 e a 5002 são idênticas.

## 3. Mudanças no gerador, em ordem

Legenda: **[C]** é comum com o Hazaki (ele herda via `montar_cns(hazaki=True)`), **[P]** é só do Pengaró.

### Fase 1: só código, sem arte e sem áudio novo

1. **[C] Tabela `IMPACTO`** logo acima de `hitdef()` (l.1343). Cada classe mapeia para (pausa, guarda_pausa, shake, fall_shake, faísca, escala, som), com os valores da seção 2. Classes: `"fraco", "medio", "forte", "especial", "final", "super", "super_final"`.

2. **[C] `hitdef()`** ganha `classe=None` e `pausa=None`.
   - Com `classe`, escreve: `pausetime` (o `pausa=` explícito vence, se vier), `guard.pausetime`, `faiscas(numero)` da classe, `sparkscale`, `guard.sparkscale = .9,.9`, `hitsound = F5,k`, `envshake.*` e, quando `queda=True`, `fall.envshake.*`. Quando `queda=True`, `recupera=True` e a classe for final, escreve também `fall.recovertime = 30`.
   - Sem `classe`, mantém o comportamento atual com `pesado` (alias provisório).

3. **[C] `faiscas()`** (l.1334): o `guard.sparkno` passa a ser sempre `S9202`, sem o `ifelse(...9232...)`.

4. **[C] `cns_novo()`** (l.1831):
   - A classe é escolhida nesta ordem: `final` → `"final"`, `dano >= 85` → `"forte"`, `dano >= 45` → `"medio"`, senão `"fraco"`. A chamada deixa de passar `pausa=` e `pesado=`. `animtype`, hit, escorrega e vel ficam como estão.
   - **Apagar** o bloco `[State …, Treme]` (l.1857–1859). Isso também remove as tremidas por `Time` de 303/313/323/333/347/3401/3413/3423/3430/3432/3435, que saem desse mesmo bloco.

5. **[C] Chamadas de `normal()` em `montar_cns`** (l.1964–1979) e 720 (l.1995): passar `classe="forte"` e remover `pausa=`/`pesado=` em 210, 215, 240, 245, 260, 410, 440, 610, 650 e 720.
   - Os fracos 200, 230, 400, 430 e 600 recebem `classe="fraco"`.
   - O 720 tem dano 0: deixar o `envshake` dele, porque é contra-golpe de defesa e afasta.

6. **[C] `cns_repertorio()`** (l.1655–1660):
   - Sem custo: `classe="especial"`.
   - Com custo: `"super"` nos acertos do meio e `"super_final"` no último. O golpe final ganha o BGPalFX (`trigger1 = MoveHit = 1`, `ignorehitpause = 1`).
   - Remover `pausa=(6, 8)` e `pesado=`.
   - **Compensar a vantagem** que cai 2 ticks quando P1 e P2 ficam iguais: `hit = 20 if final else 23`. Com o `RITMO`, 20 vira 30 e 23 vira 34; o `round` do Python arredonda 28,5 para 28. Isso vale só para a classe especial; no super final, que derruba, a vantagem não importa.

7. **[C] Especiais em `montar_cns`:**
   - 1100/1101 (l.2054) e 1200/1201 (l.2063): `classe="especial"`.
   - 1300/1301: `"especial"`.
   - 3100 (l.2111–2112): `"super"` nos acertos do meio e `"super_final"` no golpe final, com BGPalFX em `MoveHit = 1 && Time >= 36`.

8. **[P] `cns_especiais_extra()`:**
   - 1701 (l.1899) e 3402 (l.1904): `"especial"`.
   - 3403 (l.1928): `"especial"`. O EnvShake de pouso (l.1931) ganha `&& MoveHit`.
   - Garrafa 1600/1601 (l.1873–1879, inline): `pausetime = 4, 10`, `sparkno = S9200`, `sparkscale = 1,1`.
   - 3400 "Mão" (inline, ~l.1914): `pausetime = 8, 10`, `sparkno = S9201`, `sparkscale = 1.15,1.15` e `envshake` 6/150/-3.

9. **[C] `projetil()`** (l.1579) ganha `forte=False`, que escreve `pausetime` 4,10 (ou 8,10), `sparkno = S9200` (ou `S9201`) e `sparkscale`. Aplicar também no "Dobrada" inline da l.2045 (`pausetime = 4, 10`, `sparkno = S9200`).
   - O super do Hazaki (l.2098, `hits=5`) usa `forte=False`. O P2 não muda, então o espaçamento entre os acertos não muda.

10. **[C] `chuva_de_bebidas()`** (l.1592):
    - `sparkno = S9200` no lugar de `-1`.
    - A última garrafa recebe `pausetime = 12, 14`, `sparkno = S9205`, `sparkscale = 1.3,1.3`, `hitsound = F5,3`, `envshake` 8/150/-4 e `fall.envshake` 8/150/-3.

11. **[C] `superpausa()`** (l.1612): o AfterImage passa a ser `palcolor = 0`, `palbright = 40,40,40`, `paladd = 0,0,0`, `palmul = .6,.6,.6`, `length = 6`, `timegap = 1`, `framegap = 2`. Sai o `trans = add` roxo; o resto fica como está.

12. **[C] Agarrão 810** (l.2020): no mesmo tick (`Time = 14`), acrescentar `EnvShake` (8, 150, -3) e `PlaySnd` com `value = F5,2`.

13. **[C] Função nova `ajustar_sparkxy(cns, ativos)`.**
    - É uma regex por bloco `[State N, Golpe]` que troca `sparkxy = -10, -70` pelo Y da caixa de `ativos[N]`, ou de `ativos[N+10000]` quando só existe o endiabrado. Sem caixa, mantém.
    - Chamar no `main()` do Pengaró (l.2597, depois de `remapear_animelem`) e no `main()` do Hazaki (`gerar_hazaki.py` l.105, onde `a.ativos` existe).

14. **[P] `efeitos_cns()`** (l.789):
    - Recebe o dicionário `classe_por_anim`, preenchido enquanto o CNS é montado. Pula as anims da classe fraco.
    - Nas demais: `scale = .75,.75` e `removetime = 8` no lugar de `-2`.

15. **[P] Faíscas** (`FX_PENGARO` l.412, `carregar_proprios` l.428):
    - O 3º campo deixa de ser ticks e passa a ser a lista de `(índice | "F", ticks, escala)` da seção 2.
    - Nova `quadro_flash(q, cor_clara, contorno)`: a silhueta do quadro de pico vira creme (255,250,232) onde a luminância passa de 0,5 e a cor clara no resto. A cor clara é (255,215,120) no whisky e (235,200,255) na sombra. O contorno de 1 px é (60,25,5) no whisky e (25,0,40) na sombra. Tudo opaco, escalado com `Image.NEAREST`.
    - 9202/9204: `pintar(defesa, NEUTRA)` nas duas formas, com `NEUTRA = ((0,(40,40,50)),(.5,(170,170,185)),(1,(255,252,240)))`.

16. **[P] `ferramentas/efeitos_folha.py` `recortar()`** (l.29):
    - Cortar pelas colunas vazias (sem pixel não-verde). Se não sair o número de faixas esperado, voltar para a grade atual e apagar as componentes conectadas que tocam a borda da célula e não são a maior.
    - Recentralizar pelo centroide do quadro de pico antes de `enquadrar()` (l.50).
    - Rodar `python ferramentas/efeitos_folha.py pengaro`, que regrava `sprites/pengaro/efeitos/*`.

17. **[P] Reações** em `acoes_folhas()` (l.888–893): as listas `leve`, `medio` e `pesado` da seção 2, com 5001 diferente de 5002. O caminho de poses do Hazaki (`montar_air` l.1272–1278) fica como está.

### Fase 2: depende de aprovação ou de teste de fumaça

18. **[P] Contra-ataque:** ação 9207/9237 gerada do quadro F (`F@1.2x 2, q4 1, q8 1, q12 2`), mais Explod, EnvShake e PlaySnd em `MoveHit = 1 && MoveCountered`, com `ignorehitpause = 1`. A 9206 é do Hazaki, então ele **não** recebe isso.

19. **[C] SND próprio:**
    - Módulo novo `ferramentas/sons_pengaro.py` com `banco()` e `escrever_snd()`, copiados de `scratchpad/impacto/sintetizar_impactos.py`. Grupos: S1 = acerto, S2 = sombra, S3 = whoosh, S4 = vidro. As falas do Breno ficam no grupo 10 em diante.
    - Chave `SOM_PROPRIO`. `DEF` com `sound = pengaro.snd`. O `main()` grava `chars/pengaro/pengaro.snd`, e o `gerar_hazaki.main()` **tem que** gravar `chars/hazaki/hazaki.snd`, porque o `DEF.replace("pengaro","hazaki")` aponta para ele.
    - O whoosh vai no `efeitos_cns()`: `PlaySnd S3,0` em `AnimElemTime(elemento) = -5` (S3,1 em -8 no finalizador), só da classe forte para cima.
    - **Pré-requisitos:** o Breno ouve `scratchpad/impacto/wav/*.wav` nas caixas dele, e um teste de fumaça confirma que o IKEMEN carrega o `.snd`.

20. **[C] AfterImage curto** (`length = 4`, cinza, `time` = janela ativa) em 1100/1200/1701/3401.

### Fase 3: preparação curta (o maior ganho de "não ficar mole", e o mais arriscado)

21. **[C] `RITMO` separado.** Os quadros **antes** do elemento ativo usam `RITMO_PREPARO = 1.0`; os de depois continuam com `RITMO = 1.5`.
    - Precisa mudar juntos: `acao()` (l.291), `inicios_extra()` (l.1812) e `tempos_agarrao_whisky()` (l.50).
    - Os triggers fixos `Time = N` dos `normal()` (l.1964–1979) **têm que** virar `AnimElem = <elemento ativo>`. Se não virarem, a caixa liga antes do HitDef e o golpe erra.
    - A regex do hittime (l.2255) continua igual, porque a recuperação continua com 1.5.
    - Meta da seção 8.3: fraco 3–5, forte 7–10, finalizador 10–14 ticks.

## 4. Só código agora vs. arte vs. áudio

**Só código, agora:** os itens 1 a 17 da fase 1. O flash F, a re-temporização, a defesa neutra, o recorte limpo e o anel de contra-ataque saem dos `fx_*` que já existem. Os itens 18, 20 e 21 também são só código, mas precisam de teste antes.

**Arte nova (ChatGPT, opcional):**
- `fx_estouro_final`: estouro radial de linhas retas para finalizador e super;
- `fx_contra`: anel ou estilhaço próprio;
- pose de apanhar Hard de verdade e pose de apanhar agachado (hoje a 5010–5012 reaproveita a reação em pé).

**Áudio (Breno):** aprovar os sons sintetizados, que viabilizam o item 19. As falas gravadas entram no mesmo `.snd`.

## 5. Como verificar

1. **Teste de fumaça antes do resto**, com um golpe só (210, por exemplo) e o build gerado. Confirmar na tela:
   - `sparkscale` (a faísca cresce);
   - `envshake.*` do HitDef tremendo só no acerto;
   - `guard.pausetime`;
   - `MoveCountered`.

   Se o `sparkscale` não funcionar, o plano B é gerar cópias escaladas no SFF. Isso custa sprites, não arte.

2. **Janela de cancelamento.** Hoje é `movecontact <= 8` / `movehit <= 8` em `montar_cmd`/`entradas_extra` (l.2290, 2388, 2390, 2393, 2457, 2481).
   - Medir com o robô se o `movecontact` conta durante o hitpause: logar o valor no 1º tick depois do congelamento de um forte de 12 ticks.
   - **Se contar**, criar a constante `JANELA = 8 + 16` (8 + o maior P1 de golpe que cancela) e usar nesses 6 pontos.
   - **Se não contar**, nada muda.
   - As correntes que cancelam por `var(10)` não são afetadas.

3. `python ferramentas/verificar_pengaro.py`.

4. `python ferramentas/testar_pengaro.py` precisa dar **126+ PASS**, e depois `python ferramentas/testar_pengaro.py --lutador hazaki`.
   - Se um `wait` fixo (50/60/130 em `robo/robo.lua`) cortar o dano do super, porque o 3100 fica cerca de 8 ticks e o final cerca de 6 ticks mais longos, aumentar o `wait` do robô. Não reduzir o pausetime.
   - Se um kombo parar de encostar (`mc = 0`), conferir o empurrão. O médio não mudou de propósito; o forte foi para -6.

5. **Remedir os números:**

   ```
   python C:/Users/Dell/AppData/Local/Temp/claude/fa6dad62f37f9236/94958ba2-a1bd-44d1-a4cf-e337fe84b592/scratchpad/impacto/extrair_impacto.py C:/Dev/Jogo-de-Luta <saida>
   ```

   Use uma saída nova, porque ele sobrescreve o `tabela.md`. Esperado: zero violação de pausetime e de EnvShake, zero incoerência entre faísca e som, e zero EnvShake por `Time` fora de 831/841/3403.

6. `python ferramentas/filmar_luta.py <pasta> --segundos 40 --despertar 10`. Conferir quadro a quadro:
   - faísca grande no tick do contato e parada durante o congelamento;
   - golpe errado sem rastro grande;
   - faísca dos golpes baixos rente ao chão;
   - defesa diferente do acerto no endiabrado;
   - nada rosa sobre o palco azul.

   **Sem som:** ouvir de verdade fica com o Breno, depois de ele conferir o `MasterVolume`.

7. **Entrada datada no `LOGBOOK.md`** ao fim do bloco: o que entrou, o que ficou para as fases 2 e 3, e o resultado do teste de fumaça.