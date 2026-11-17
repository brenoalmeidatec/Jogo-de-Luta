# Pausa 17/11 — Raiclaven base no boneco de peças

**Feito e na `mugen`:** 43 ações da base do Raiclaven montadas pelo kit. São parado, soco, chute alto, martelo e
martelo forte, cabeçada, agachar, rasteira, golaço, armada, agarrão, pente combo, soco no ar e levantar. O robô de
peças está com 0 defeito e o robô de luta deu 216/216, com dano igual ao da mugen. O `.sff` tem 65,5 MB. Os avisos
foram na #43.

**Como refazer:**
1. `python3 ferramentas/golpes_raiclaven.py` (poses em `POSE`; `ESP(q)` = desenho de hoje inteiro). Parado, soco e
   chute alto estão em `ferramentas/piloto_raiclaven.py --so-pose`.
2. `python3 ferramentas/raiclaven_no_jogo.py`. Roda **em cima do chars/raiclaven da mugen atual** e preserva o
   despertado com A Cliente. Leva ~15 min e termina com `encolher_sff.py`.
3. `python3 ferramentas/testar_pengaro.py --linux --lutador raiclaven`, comparando as linhas de `dano` com a mugen.
4. Vídeo: `python3 ferramentas/video_golpes_raiclaven.py N:nome ...`.

**Onde parou / próximos passos:**
- Testar `ferramentas/pele_pecas.py` (dica do Pengaró: pele que dobra nas juntas, sem linha de corte) no lugar do
  `R.desenhar` por peças rígidas. O Raiclaven tem desenho próprio (costas, agachado, perna levantada, `tapar_furos`),
  então é preciso adaptar e não só trocar a chamada.
- Revisar os golpes com a lista de 12 conferências do `docs/estudo-anatomia-golpes.md`, como pé de apoio girado e
  mão livre na guarda.
- O despertado 20410 (baixo+y) não acerta no robô (dano 0). Isso já vinha da mugen a9e3dab4 e é da thread do
  despertado.
