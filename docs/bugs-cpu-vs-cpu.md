# Bugs do teste CPU vs CPU (Pengaró x Pengaró)

Teste feito no IKEMEN GO v1.0.0 com as duas CPUs no nível 8. Corrigidos no PR #20: tamanho do
Pengaró (escala 0.6), barras pretas (palco `stage0-720`) e nome da HUD ("Pengaro", a fonte não tem "ó").

## Ainda abertos
- Balões de fala: corrigidos no gerador (ver missão 5B), falta conferir no jogo. Balões de P1 e P2 ainda podem se
  cruzar quando os dois falam ao mesmo tempo e estão perto.
- "COUNTER HIT" / "FIRST ATTACK" pequenos e colados na margem da tela.
- Espelho sem paleta alternativa: P1 e P2 ficam com a mesma cor.
- IA gasta muito tempo em pulos e agachamentos e solta a bola de longe sem consequência.
- Conferir o chão no palco widescreen: em alguns quadros o corpo cai rente à borda de baixo.
- A bola, o whisky e as folhas novas estão no thread de redesenho do Pengaró (Blender).

## Como repetir o teste (Linux, sem tela)
Baixe o IKEMEN GO, copie `chars/pengaro`, registre no `data/select.def` e rode com `xvfb-run`:
`./Ikemen_GO_Linux -p1 pengaro -p1.ai 8 -p2 pengaro -p2.ai 8 -s stages/stage0-720.def`
