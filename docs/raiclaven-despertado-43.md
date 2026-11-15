# Raiclaven despertado (issues #38, #43 e #47): progresso

Atualizado em 2026-11-15. Branch de trabalho `claude/project-thread-f6tbq9`, que ainda **não** foi juntada na `mugen`.
Condição do Breno na #43: postar o **vídeo** lá antes de juntar.

## O que o Breno pediu (fase 2)

A parceira vai **amarrada nas costas dele**, num arnês de barbeiro com uma cadeirinha vermelha entre os tanques, e não sai
do assento. Ele usa o corpo todo para levar a parceira até o alvo, e ela ataca com a navalha e o secador. Ela é adulta,
a dupla é mandona, e o humor vem da dupla, nunca da deficiência dela. O cabelo continua verde. O Breno quer o despertado
louco, caótico e rápido, com raio verde e aço estourando.

## Pronto

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
