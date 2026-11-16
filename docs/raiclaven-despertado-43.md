# Raiclaven despertado (issues #38, #43 e #47): progresso

Atualizado em 2026-11-15 (noite). Branch de trabalho `claude/project-thread-f6tbq9`, que ainda **não** foi juntada na `mugen`.
Condição do Breno na #43: postar o **vídeo** lá antes de juntar.

## O que o Breno pediu (fase 2)

A parceira vai **amarrada nas costas dele**, num arnês de barbeiro com uma cadeirinha vermelha entre os tanques, e não sai
do assento. Ele usa o corpo todo para levar a parceira até o alvo, e ela ataca com a navalha e o secador. Ela é adulta,
a dupla é mandona, e o humor vem da dupla, nunca da deficiência dela. O cabelo continua verde. O Breno quer o despertado
louco, caótico e rápido, com raio verde e aço estourando.

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
