# Pausa 17/11: Diabo demônio, motor e especiais (#47)

**O que está pronto e na `mugen` (50f21cdb):**
- Motor completo do demônio em `ferramentas/diabo_demonio.py` (normais, ar, direcionais, correntes, Banquete, Bola
  das Trevas, Voo Infernal, Rasgo Ascendente, super Juízo Infernal). Cada golpe liga sozinho quando a pasta
  `sprites/hazaki/diabo_terno/m_<folha>/07.png` existe.
- Tempos dos golpes pelo estudo de anatomia (regra 8.3).
- Arte dos 4 especiais (5 folhas: `m_bola_trevas`, `m_voo`, `m_rasgo`, `m_juizo_a`, `m_juizo_b`) feita no boneco de
  peças em `ferramentas/kit_diabo_especiais.py`. Robô de defeitos 40/0, robô de luta do Hazak 327/0.
- Vídeo: `docs/diabo-44/demonio/video/especiais-arte.mp4`. Situação detalhada: `docs/diabo-44/demonio/LEIA-ME.md`.

**Onde parou:** nada pela metade nesta frente. Faltam só as 6 folhas da thread da arte (branch
`claude/project-thread-46qshe`): `ar_maos`, `ar_pes`, `direcionais_a`, `direcionais_b`, `fins_maos`, `fins_pes`.
O patch com os meus ajustes no `firme.py` e no `diabo_exportar.py` está em project-files `diabo-44/especiais-arte.patch`.

**Próximos passos exatos (quando as 6 folhas entrarem na mugen):**
1. `python3 ferramentas/gerar_hazaki.py && python3 ferramentas/ligar_pecas.py hazaki`
2. `python3 ferramentas/testar_pengaro.py --lutador hazaki --linux` (tem que dar 0 falhas)
3. Filmar: `python3 ferramentas/filmar_robo.py --lutador hazaki --filtro "demonio" --saida <pasta>/`
4. Juntar na `mugen` e comentar na #47.
