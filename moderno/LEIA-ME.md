# Nazafights Moderno (rascunho, parado)

Mecânicas do item 5 da missão `docs/missao-alisson-estilo-melty.md` (issue #51), feitas por
`ferramentas/mecanicas.py`: parry no estilo Shield, golpe final no parry da forma endiabrada, corrente
x → a → y → b → especial e dash no ar. O Arcade (`chars/`) não é tocado.

Cada pasta `moderno/chars/<lutador>/` tem só os arquivos de texto que mudam (.cns, .cmd, .air, movelist.dat).
Para jogar, copie `chars/<lutador>/` e ponha esta pasta por cima (`mecanicas.montar`).

**Estado (2026-11-15): escrito, NÃO testado no motor.** O robô ainda não rodou em nada disto e não há vídeo.
O Moderno ficou para depois da 1.0. Ao retomar: rodar `python3 ferramentas/mecanicas.py`, criar o modo
`--moderno` no `testar_pengaro.py`, escrever os roteiros (parry com congelamento, golpe final, corrente, dash) e
filmar.

Pontos em aberto para o Breno:
- "Médio" não existe nos 4 botões: a corrente ficou soco fraco → chute fraco → soco forte → chute forte.
- "Barra cheia" no Despertar não acontece (a barra zera ao despertar e a forma dura 10 s): o golpe final sai em
  qualquer parry certo na forma endiabrada e encerra o Despertar (`FINAL_BARRA` na ferramenta muda isso).
- Janela do parry foi de 4 para 6 ticks, com 8 ticks de congelamento e 8 a mais de exposição para quem erra.
