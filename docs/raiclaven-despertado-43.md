# Raiclaven despertado (issues #38, #43 e #47): progresso

Atualizado em 2026-11-15 (noite). Branch de trabalho `claude/project-thread-f6tbq9`, que ainda **não** foi juntada na `mugen`.
Condição do Breno na #43: postar o **vídeo** lá antes de juntar.

## O que o Breno pediu (fase 2)

A parceira vai **amarrada nas costas dele**, num arnês de barbeiro com uma cadeirinha vermelha entre os tanques, e não sai
do assento. Ele usa o corpo todo para levar a parceira até o alvo, e ela ataca com a navalha e o secador. Ela é adulta,
a dupla é mandona, e o humor vem da dupla, nunca da deficiência dela. O cabelo continua verde. O Breno quer o despertado
louco, caótico e rápido, com raio verde e aço estourando.

## Fase 5 (17/11 tarde): agachado, golpes agachados, defesa e apanha

- **Agachado (ação 11)**: a saia esconde as pernas do kit, e dobrar coxa e canela dava linha de corte e pedaço solto.
  A metade de baixo agora vem inteira de um **doador** gerado no ChatGPT do PC de casa (duas figuras na mesma imagem:
  à esquerda a cópia do ginga/00, que dá a escala e a cor por SIFT, e à direita o agachado). `ferramentas/doador_cliente.py`
  leva o doador ao tamanho e à cor do kit; `kit_cliente.PERNAS_VAR/PERNAS_DE` usam ele e o tronco respira em cima.
- **Golpes agachados** (corpo inteiro, sem borracha): Belisco no Tornozelo (20400, garra baixa), Mordida Antiaérea
  (20410, a Cliente empina e morde para cima, garra no alto), Secador no Chão (20430, baixo) e Varrida de Garra (20440,
  arco baixo com os três braços). Caixas de golpe medidas no desenho de contato.
- **Defesa (120/130/140/150)** e **apanha (5000/5001/5002/5005)** pelo remap das ações da base
  (`kit_cliente.REMAP`, `kit_raiclaven.remap_parado` agora geral). Na defesa ele se encolhe e a Cliente se debruça por
  cima; erguer o braço mecânico deixava a barriga borrada (o desenho não tem o que fica atrás do braço), então o braço
  quase não sobe. Doador com o braço erguido já gerado (`sprites/raiclaven_cliente/doadores/defesa_cap.png`) para a
  próxima volta.
- **Braço mecânico recortado de novo**: só o metal, a lâmina e a luz verde (`SO_DO_BRACO_TRAS`); o cinto e o avental
  entre as lâminas ficam com o corpo.
- **Sem quadro do meio antes do contato** (regra de criação do Breno + meio-termo do Alisson): o `vida_pecas.py` da
  mugen já segura a antecipação (`MEIO_NO_BOTE = False`); meio só na preparação, volta e guarda.
- `raiclaven_no_jogo.py` roda o `encolher_sff.py` no fim: raiclaven.sff de 82 para 63,6 MB.
- Robô de defeitos 0/126, robô de luta 216/0. Poses em `docs/boneco-pecas/raiclaven_cliente/lote2_poses.jpg`, vídeo
  em `lote2_no_jogo.mp4`.
- Falta: pulo, andar, queda/levanta, especiais (Pescoço de Borracha estica), super, agarrões, correntes e kombo com a
  arte nova, defesa com o braço do doador e pele sem linha de corte nas juntas (pele_pecas.py).

## Fase 4 (17/11): corpo firme com vida, no jogo

O Alisson aprovou o método do boneco de peças ("corpo firme com vida") e pediu tudo no jogo; o Breno liberou
auto-aprovação. Regra nova 7.2.1 (zero erro de animação) e decisão do Alisson: a borracha (braço que estica) só no
Pescoço de Borracha e na Navalhada, sempre com o corpo do Raiclaven indo junto.

- **Folhas -> quadros**: `ferramentas/importar_cliente.py` corta as 20 folhas `c_*` em
  `sprites/raiclaven_cliente/quadros_arcade_hd/` (fora do git). Cada folha tem a sua escala, medida pelo tanque verde.
- **Kit**: `ferramentas/kit_cliente.py` (lutador `raiclaven_cliente`, referência `ginga/00`). Além do corpo de sempre, a
  criatura e os três braços dela (navalha, secador, garra) são peças (`EXTRAS`). O `firme.py` ganhou:
  - `EXTRAS`: peças a mais com polígono e osso próprios;
  - `TAPAR_FAIXA`/`TAPAR`: pinta por baixo só das peças que ficam por cima (respirar não abre buraco nem emenda);
  - `estica`: braço de borracha na linha do osso (vizinho mais próximo, sem cor nova).
- **Golpes feitos**: parado com vida, Tapa de Garra (20200), Navalhada (20210), Bota e Cuspe (20230), Pancada Tripla
  (20240). Robô de defeitos 0 de 57 (`docs/boneco-pecas/raiclaven_cliente/robo_defeitos.md`); vídeos lado a lado
  (folha do ChatGPT x corpo firme) na mesma pasta.
- **No jogo**: `kit_raiclaven.py` põe os desenhos no `.sff` como PNG (grupos 26000+, `sprites_pecas`), usa os ticks e
  a caixa do `tempos.json` nos golpes que já têm arte nova e troca o parado do despertado pelo remap (86..93 ->
  26000). O resto continua com a arte provisória até o próximo lote.

Refazer: `python3 ferramentas/importar_cliente.py`, `python3 ferramentas/firme.py cliente`, depois
`kit_raiclaven.aplicar` -> `legibilidade` -> `despertados_47` -> `kit_raiclaven --cmd` -> `aura_no_corpo` ->
`aura_silhueta` -> `luz` em `chars/raiclaven` (ou o `gerar_raiclaven.py` inteiro, com o HD do Blender).

Falta (próximo lote): agachados (x/y/a/b), aéreos, defesa, apanha, queda, levanta, andar, pulo, especiais, super e
agarrões; mancha escura atrás das costas da criatura (mangueira), correntes e kombo com a arte nova.

## Fase 3 (Breno, 15/11 19:23Z): A Cliente vira criatura de terror e o kit é todo próprio

O Breno aprovou o conceito B da criatura (`docs/previas/raiclaven-dupla/conceito-criatura-b.jpg`) e a lista de golpes
(`docs/fichas/raiclaven-despertado-golpes.md`). Regra da seção 4: no despertado nada do normal entra.

- **Kit no motor** (`ferramentas/kit_raiclaven.py`, chamado pelo `gerar_raiclaven.py`): 39 golpes só do despertado.
  - 16 normais (20200 a 20640), 4 correntes de 3 + finalizador (20301 a 20333), kombo Cobaia (20280, 20341, 20342).
  - Especiais: Peruca Viva 21000/21001 (projétil pelo chão), Pescoço de Borracha 21100/21101, Tanque Estourado 21200,
    Bigodes Carnívoros 21300 (vários acertos) e o Secador de Raio 4750 da #47.
  - Super Sala de Cirurgia 23000 (2 barras), agarrões Lavagem 24100 (↓+y) e Transplante 24200 (→↓→+y). A Cadeira
    Elétrica 4700 passou a bater com golpes do kit (`despertados_47.CFG`).
  - No `.cmd`, todo golpe do normal ganhou `var(20) = 0`; os 20 golpes antigos do despertado (herdados do Pengaró)
    saíram. Ficam nas duas formas só parry, rolamento, afastar e o Despertar.
  - **Arte provisória**: cada golpe copia os quadros de uma ação do arnês (`fonte`) até a folha da criatura chegar.
- **Folhas da criatura**: 43 pedidos em `ferramentas/folhas_criatura.py` (saem em `folhas_criatura/c_<nome>.png`).
  Fila do ChatGPT em `/mnt/project-files/imagens/fila-chatgpt.md` (Raiclaven é o 4º); Gemini até 15 no próximo ciclo.
- **Robô**: 71/0 nos roteiros do despertado novo (todos os golpes, correntes, kombo, agarrões, super e "o super do
  normal não sai").

Falta: as folhas, cortar com `--criatura` e trocar a arte provisória, efeitos e sons dos golpes novos, vídeo na #43.

## Pronto (fase 2, parceira humana no arnês, vai ser trocada pela criatura)

- **Conceito do arnês**: `docs/previas/raiclaven-dupla/conceito-arnes.jpg`, também em `folhas_dupla/dupla_modelo.png`.
- **Folhas da dupla**: 16 de 40, em `sprites/raiclaven/quadros/folhas_dupla/`.
  - Do ChatGPT: ginga, anda, agachado, pulo, defesa, apanha, queda, levanta e soco.
  - Do Gemini: martelo, chute_baixo, raio, choque, piao, agarra_forma e vitoria (a vitória é a pose de comemoração do agarra).
  - Golpe sem folha empresta a folha mais parecida (`EMPRESTADA_DUPLA`). O kit da forma (raio, choque, pião e agarra)
    entra no lugar dos especiais do Surto.
- **Gemini**: cada imagem dá 4 quadros. `ferramentas/compor_gemini_raiclaven.py NOME A.jpg - [ordem]` monta a folha
  3136x560 e escala pela lente verde do braço. Depois roda `gerar_raiclaven.py --dupla e_NOME`.
- **Caixa de golpe na arma** (`ferramentas/caixas_dupla.py`): nas ações 10000 a 12999, a Clsn1 vai para a ponta que
  chega na frente: navalha, secador, tesoura ou bota. Os supers ficam com a caixa grande. Prévia em
  `docs/previas/raiclaven-dupla/caixas-dupla.png`.
- **Kit da forma** (`despertados_47.py` e `despertados_47_blender.py`, CFG raiclaven), no padrão do Diabo Loiro:
  - **Cadeira Elétrica** (agarrão 4700/4710).
  - **Secador de Raio** (poder 4750, ↓→↓→+soco).
  - Efeitos do Blender + pixelfx em aço e verde. Prévia em `docs/previas/raiclaven-dupla/agarrao-e-poder.jpg`.
- **Aura**:
  - A aura grande (lâminas e raios) agora fica presa ao corpo (`aura_no_corpo.py`).
  - A aura de anime colada na silhueta dos dois sai em verde (`aura_silhueta.py`, TONS). Prévia em
    `docs/previas/raiclaven-dupla/aura-silhueta.jpg`.
- **Conserto do .sff**: o transplante regravava os efeitos PNG como pixel indexado (o .sff da mugen sai torto no
  8200,0) e o `efeitos.gravar` perdia a 3ª paleta. Agora os dois preservam PNG, o índice de paleta e as paletas extras.
- **Robô**: 186 ok, 0 falhas.

## Falta

1. **24 folhas**: chute_alto, afastar, baixo_soco, cabecada, rasteirinha, rasteira, ar_soco, bicicleta, bola,
   rolamento, pente_combo, agarrao, compasso, armada, caneta, golaco, provoca, lata, derrota, despertar_a,
   despertar_b, mergulho, atravessa e joga_forma.
   - Prompts em `ferramentas/folhas_raiclaven.py` (DUPLA).
   - O Gemini Pro segura umas 35 imagens por ciclo somando todas as threads (contador em
     `/mnt/project-files/imagens/contador-gemini.md`). O ChatGPT Go volta às 23:26.
2. **Vídeo na #43**. Depois do aval, juntar na mugen e mandar o hash para a #47.

## Como rodar tudo

```
python3 ferramentas/gerar_raiclaven.py          # já chama caixas_dupla, despertados_47, aura_no_corpo e aura_silhueta
python3 ferramentas/conferir_sff.py transplantar <raiclaven.sff da mugen> chars/raiclaven
python3 ferramentas/trocar_retratos.py raiclaven
git checkout chars/raiclaven/raiclaven.cmd      # o .cmd do git já tem o 4700/4750 (despertados_47.ligar_cmd)
python3 ferramentas/testar_pengaro.py --lutador raiclaven --linux
python3 ferramentas/filmar_47.py SAIDA.mp4 --p1 raiclaven --p2 gutto          # agarrão e poder no motor
python3 ferramentas/fotos_despertado.py raiclaven SAIDA --segundos 30 --video
```

Os efeitos da #47 se refazem com `"$NAZAFX_PY" ferramentas/despertados_47_blender.py raiclaven`, depois de
`bash ferramentas/efeitos_pixel/preparar_nuvem.sh`. O HD 3x precisa de `sprites/raiclaven/quadros_hd`, que fica fora do
git e é gerado com `ferramentas/hd_blender.py raiclaven`.
