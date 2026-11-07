# LOGBOOK

Registro append-only do trabalho, para quem chega sem contexto (outro chat, outra máquina, outra IA).
Entradas novas vão no fim. O estado do jogo e as regras continuam em `docs/como-trabalhar.md`.

## 2026-11-07 — Revisão do Pengaró: fluidez, efeitos e impacto estilo KOF (Claude, sessão do LightWolfMan)

**Pedido:** revisar o Pengaró inteiro seguindo as regras, achar todos os erros de animação e efeito, deixar o mais
fluido possível e dar aos golpes impacto "que parece que machuca", no estilo KOF (só mecânica, nada copiado).
Também: o jogo passa a se chamar **Nazafight**.

**Feito e commitado:**
- Nazafight na janela do IKEMEN (`WindowTitle` gravado pelo `.bat`), no console e no README. Pasta
  `%USERPROFILE%\JogoDeLuta` e arquivo `Jogo de Luta.bat` mantêm o nome antigo de propósito (atalho do Breno e motor já
  baixado).
- `conferir_tempo.py` e `conferir_despertar.py` criam a pasta de saída (quebravam sem ela).

**Linha de base medida antes de qualquer conserto (commit `3618007`):**
- gerador reproduz o commitado; `verificar_pengaro` passa; robô 126 PASS / 0 FAIL.
- regra dos 2 ticks: **117 de 217 ações** com desenho parado mais de 2 ticks.
- auditor: 142 linhas de problema (parte é falso positivo da medida `centro_tronco`).
- impacto: 94 violações dos pisos da seção 8.3 e 108 incoerências (faísca/som que não batem com a força);
  EnvShake em só 15 lugares; nenhum som próprio; 7 projéteis com a estrela branca padrão do motor.

**Auditoria (7 frentes + cético por frente):** 81 achados, 72 confirmados. Plano de conserto em 6 fases e
especificação de impacto KOF, na íntegra em `docs/revisao-pengaro/` (`plano-de-conserto.md`, `impacto-kof.md`,
`achados.json` com evidência e conserto verificado de cada achado, `impacto-tabela-antes.md`).

Principais causas confirmadas:
- "Golpe mole": `RITMO = 1.5` estica também a preparação (forte leva 10–26 ticks até encostar; KOF ~7–10);
  hitstop do atacante 2–6 em 13 golpes; faísca nasce no meio do estouro, sem clarão; sem tremida; som genérico.
- "Lata parada no meio da tela": a Mão de Sombra (3400) usa o bolão 3x da lata do Hazaki.
- Estrela branca: projéteis sem `sparkno` caem no `[Data] sparkno = 2` do motor.
- Endiabrado furado: `limpar_borda` trata o roxo como franja magenta; `tira_fundo` apaga realces.
- Endiabrado muda de tamanho entre folhas (cabeça pula 37 px ao sair da ginga); pés fora do chão.
- Clsn1 copiado para os quadros do meio que já recolheram o membro (alcance fantasma).
- Quadros do meio "estalam" entre `_3` e `_4` (`animar_folha.py` troca de chave em t=0.5) — causa só se resolve
  com Blender (Breno).
- "Volta ao normal no meio da luta" na filmagem NÃO é bug do jogo: `filmar_luta.py` religava o Despertar.

**Ambiente desta máquina:** IKEMEN GO v1.0.0 em `%USERPROFILE%\JogoDeLuta\ikemen` com `MasterVolume = 0`
(testes no mudo, pedido do dono). Sem Blender. Python 3.12 com pillow, numpy, opencv.

**Em andamento quando esta entrada foi escrita:** corrente de implementação em 7 fases (régua → endiabrado →
animação → ações → impacto → Despertar → peso/som), um commit local por fase, cada uma com portão: robô 126+ PASS,
`verificar_pengaro` passa e Hazaki byte a byte igual. O trabalho para em 80% do consumo semanal do plano; ver a
próxima entrada para onde parou.

## 2026-11-07 (fim do dia) — Onde o trabalho parou (consumo semanal do plano em ~80%)

**Commits nesta branch (`claude/pengaro-fluidez-impacto`, NÃO mesclada na `mugen`):**
- `2c11ce4` Fase 0, régua: auditor sem falsos positivos (corpo pula, arte antiga, sujeira do Despertar), verificador
  avisa Clsn1 além do membro e projétil sem faísca, `filmar_luta.py --despertar N` liga o Despertar UMA vez.
- `46b3dfc` `ferramentas/video_golpe.py` + regra de controle de qualidade (vídeo de 5 a 10 s a 60 fps e análise tick
  a tick) em `docs/conferencia-de-golpe.md` e `docs/como-trabalhar.md`.
- `f5aa8de` Fases 1 e 2, endiabrado: sem furos (perda de pixels 17,5% -> ~0%), escala por folha (razão de altura
  1,16 -> 1,00), pés no chão (0 fora), dx pelas chaves (desalinhados 17 -> 2).
- `ea08d49` Impacto estilo KOF: tabela `IMPACTO` por classe em `hitdef(classe=...)` (pausetime, guard.pausetime,
  envshake e fall.envshake dentro do HitDef, sparkscale, faísca e som por força); faíscas com clarão no 1º tick
  (9/12/14 ticks), defesa neutra; faísca na altura da caixa; projéteis com faísca própria e acerto que some na faísca
  (fim da estrela branca do motor e da lata); Mão de Sombra virou massa de sombra (ação 3012) no lugar da lata
  gigante; um projétil por vez; Garrafada bloqueada no Despertar; aura no `-2` (não aparece no ar); reações 5000-5002
  diferentes; BGPalFX curto no golpe final dos supers. Extrator de impacto: 94 violações / 108 incoerências -> 62 / 33.

Todas as fases passaram no portão: robô 126 PASS / 0 FAIL, `verificar_pengaro` e `--hazaki` ok, Hazaki byte a byte
igual. Hazaki ficou de fora de propósito (pedido: foco só no Pengaró).

**NÃO verificado por ninguém na tela nem no som:** tamanho da faísca e tremida no jogo, BGPalFX, aura, Mão de Sombra
voando, Despertar entrando/saindo uma vez. `filmar_luta.py` fotografa a ÁREA da tela: com a tela bloqueada ou outra
janela na frente ele grava a tela errada (aconteceu duas vezes; as capturas foram apagadas). Rodar com a sessão
desbloqueada e a janela do jogo livre. Motor desta máquina no mudo (`MasterVolume = 0`).

**Pendente, na ordem (detalhes em `docs/revisao-pengaro/plano-de-conserto.md` e `impacto-kof.md`):**
1. Fase 3 do plano, motor de animação (`Air.fluido`): cauda parada no último desenho (crítico), loops até o desenho
   7, amostragem pulando o `_4`, poses -1 no ar, Clsn1 fantasma por quadro (regra 8.3), Clsn2 mínima do rolamento.
   É o que mais falta para a fluidez: a análise quadro a quadro ainda acusa 179 de 254 ações, e
   116 de 215 ações seguram desenho mais de 2 ticks.
2. Fase 4, redefinir ações: virada agachado, corrida, defesas, golpes do repertório, Saideira 3100, emendas 831/841/1701.
3. Fase 6, lógica do Despertar: arte do 3100 endiabrada, zerar vars no intro, fumaça na saída.
4. Spec de impacto fases 2 e 3: preparo curto (`RITMO_PREPARO = 1.0`, maior causa restante do "golpe mole": windup
   lento em 41 golpes), contra-ataque com efeito, `.snd` próprio sintetizado (alguém precisa ouvir).
5. Item 16 da spec: recortar as folhas `fx_*` por colunas (bordas cortadas nas faíscas).
6. `filmar_luta.py` com taxa de captura maior (hoje ~3 quadros por segundo) para os vídeos curtos no jogo.
7. Precisa do Breno: Blender para refazer os quadros do meio que estalam entre `_3` e `_4`; arte nova opcional.

**Como retomar:** `git fetch origin claude/pengaro-fluidez-impacto && git switch claude/pengaro-fluidez-impacto`,
ler este LOGBOOK e o plano, rodar a linha de base (`gerar_pengaro`, `verificar_pengaro`, `testar_pengaro`,
`video_golpe.py --todas --sem-video`) e seguir pela Fase 3. Para ir ao jogo do Breno, mesclar a branch na `mugen`.
