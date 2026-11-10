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

## 2026-11-07 (noite) — Pengaró: fases 3, 4 e 6 do plano de conserto (Claude, sessão do Breno)

**Feito, publicado na `mugen` em 5 commits (pela API do GitHub, ver "Ambiente"):**
- **Fase 3 (motor de animação):** `Air.fluido` agora trata o desenho parado por mais de 2 ticks sem caixa de golpe como
  vai-e-volta de 2 ticks com os quadros do meio vizinhos (`vai_e_volta`), e a recuperação longa dividida por igual vira
  excesso em vai-e-volta no começo + caminho a 2 ticks por quadro, chegando ao próximo desenho no tempo certo. `SEGUINTE`
  (10, 11, 40, 120, 130) e `ULTIMO_DESENHO` (golaço 4) fecham o G4 e o G5; 3.8: rolamento 700/705 e 841 com caixa de corpo.
- **Fase 3.7:** `ajustar_clsn1` encurta cada Clsn1 até o pixel mais à frente do membro + 4 px (nunca aumenta, mínimo 12 px),
  medido na forma que a ação mostra (1xxxx só endiabrado; normal com 1xxxx só normal; as outras, a maior). O verificador
  passou a medir assim. 344 ganhou um passo à frente (parou de encostar).
- **Fase 4:** ações 5, 6, 47 e 100 com desenhos da folha; 201, 216, 231, 246, 601, 610, 611, 1400, 1401, 1500, 1501 e 3200
  com os desenhos de uma folha só (mesmos tempos, caixa e elementos; o Hazaki segue o caminho antigo).
- **Fase 6:** `despertar_do_pengaro` (só no `main()` do Pengaró, porque o bloco `-2` é compartilhado): 3100 fica endiabrado
  até o fim, var(20)/var(21) zeram na introdução do round, fumaça violeta (9215) quando var(20) = 12.
- **Preparo curto (item 21 da spec de impacto):** `RITMO_PREPARO = 1.0`. Os elementos antes daquele em que a caixa de golpe
  liga não são mais esticados pelo `RITMO = 1.5` (só no Pengaró; `Air.acao` e `inicios_extra` usam a mesma regra, e o
  Hazaki fica igual). Os `Time = N` do CNS já eram os tempos sem esticar, então voltaram a casar com a caixa. Ticks até a
  caixa ligar, antes -> depois: x 7 -> 4, a 7 -> 5, y perto 6 -> 4, y longe 10 -> 7, b perto 7 -> 5, b longe 14 -> 9,
  rasteira 16 -> 10, afastar 18 -> 12, tranco 12 -> 8, mão de chimpá 12 -> 8, finalizadores 12 a 16 -> 8 a 11, passo de
  letra 26 -> 17 (lento de propósito). A meta da regra 8.3 é fraco 3-5 e forte 7-10. A recuperação continua esticada
  (e o atordoamento também), então a vantagem no acerto aumentou: a corrente fica mais folgada.
- **Robô:** 126 -> 146 verificações: super 1 (Chuva de Bebidas, dano 228), super 3100 no Despertar (201, var(37) = 1 no
  meio), super 3200 (345), Passo de Letra (90), Mão de Chimpá (73), Sola de Várzea (88).

**Medido (antes -> depois):** ações com desenho parado acima de 2 ticks 116 -> 5 de 215 (sobram 800, 1005, 3010, 3011 e
3100); Clsn1 além do membro 1060 -> 101 elementos (o resto são ações que aparecem nas duas formas com alcances diferentes).
Robô 146 PASS / 0 FAIL; Hazaki `.air` e `.cns` byte a byte iguais depois de cada passo.

**De propósito NÃO feito:**
- **3100 com folha única:** tentei (jab e cruzado da folha do soco), mas a caixa passou a acompanhar o punho e o super deu
  dano 0 a 60 de distância. Voltei à definição antiga; mexer nisso muda o equilíbrio e precisa de jogo.
- 3.1 (amostragem do `_4`, sem prova de ganho), 3.6 (poses -1 no ar), 4.4 (emenda andar/ginga), 4.7 (emendas 831/841/1701),
  4.9 (limpeza do `Q(1005)`), item 16 (recorte das folhas fx), taxa de captura do `filmar_luta.py`.
- Fase 3 do impacto: **18** contra-ataque, **19** `.snd` próprio (alguém precisa ouvir) e **20** AfterImage curto.
- Decisões do Breno (6.4 barra drenando, Clsn2 no membro, garrafa no Despertar, 3100 só no Despertar) e o que exige Blender
  (G1, o estalo `_3` -> `_4`).

**Nada disto foi visto nem ouvido no jogo.** O que o robô prova: entrada dos golpes, encostar, dano, `var(37)` do 3100 e o
retorno ao controle. O que ele não prova: se o vai-e-volta da cauda parece respiração ou tremor, se a caixa mais curta
mudou o jeito de jogar, e a fumaça da saída do Despertar.

**Ambiente:** o `git fetch` desta máquina (Windows, `index-pack`) falha ou trava com os pacotes grandes desta branch; o
código e os sprites vieram por `gh api` (zip e blobs) e os commits saíram pela API de dados do git (`/git/blobs`, `/trees`,
`/commits`, `/refs`). Se acontecer, `git -c index-pack.threads=1 fetch` e paciência, ou o mesmo caminho pela API.

## 2026-11-10 — Layout NAZAFIGHT: título, seleção, VS e HUD estilo KOF na pegada de Nazaré (Claude)

**Feito:** `ferramentas/gerar_layout.py` (+ `ferramentas/layout_sff.py`, escritor/leitor SFF v2 PNG32 sem paleta) gera
`motif/nazafight/` inteiro por código: `system.def/.sff`, `fight.def/.sff` e 5 fontes bitmap (`naza_num`,
`naza_num_alerta`, `naza_tab`, `naza_menu`, `naza_menu_ativo`). Pixel art numa grade lógica ampliada 4x, só as 16 cores
da paleta (o gerador falha se achar outra), localcoord 1280x720. Título: o Jaguaripe ao fim da tarde (céu, nuvens
andando, casario na ladeira, Matriz, Cristo pequeno no morro, ponte de arcos, rio com reflexo, canoa de caxixis em 8
quadros), logo NAZAFIGHT de barro brunido com espiral de tabatinga caindo com tremor e nuvem de farinha, menu numa
tabuleta. Seleção: feira de cima, grade 4x2 com caxixi tampado nas vagas vazias, cursores dendê/rio, retrato grande sobre
pano listrado. VS: pano dividido e remos cruzados. HUD: trilho de saveiro com alça de moringa, vida folha/dendê/tauá com
fantasma de farinha, relógio num caxixi com faixa de azulejo (número em tauá vivo abaixo de 10 s), retrato com anel de
barro, vitórias em bolinhas de barro, poder com 3 caxixis que cozinham (cru → quente → cozido), ROUND/LUTA! em tabuleta e
K.O. rachando em 6 quadros. Prévias em `docs/previas-layout/` (montadas dos SFF e das posições lidas do .def).
Determinístico (2 rodadas, mesmo hash).

**Motor (cópia no scratchpad, config com `Motif = data/nazafight/system.def`):** menu título 14 s e luta rápida
pengaro x hazaki (`-rounds 2`, IA 8): sem `save/logs/Ikemen_*.log`, stdout só com os WARNINGs de comando dos lutadores,
nenhuma linha de `data/nazafight`. A luta saiu sozinha (código 0), mas em 245 s, não em menos de 90 s. A mesma luta com
o motif padrão (`-r data/ikemen1/system.def`) levou 153 s: a duração é da IA x IA, não do motif.

**Decisões fora da direção:** a fonte do menu é bitmap com acento (glifos Ç Ã Õ Ê Ô Á É Í Ó Ú nos números Unicode,
que o `LoadFntSff` do v1.0.0 aceita) em vez de TTF OFL: nada baixado e o traço fica igual ao resto. Menu com 6 itens
(ARCADE, VERSUS, TREINO, ASSISTIR, OPÇÕES, SAIR). O relógio mostra "8", não "08" (o motor escreve sem zero à esquerda).

**Obsoleto:** `ferramentas/hud_layout.json` (304x224, da era Godot). Não use; o HUD agora é o `fight.def` gerado.

**Pendente:** (1) integrar no `.bat` — o passo exato está em `motif/INSTALAR.md`; (2) **não conferido na tela**: posição
real das barras, fontes, menu e animações só com filmagem (`ferramentas/filmar_luta.py`) ou o Breno olhando; (3) a anim de
cacos do estoque (ação 700) está pronta mas sem gatilho no v1.0.0; (4) fase 2: cenários da ponte, feira e casa de farinha,
música de samba de roda própria, telas de vitória e continue.

## 2026-11-10 — Layout NAZAFIGHT, rodada 2 (crítica de direção de arte r1) (Claude)

**Feito (tudo no `ferramentas/gerar_layout.py`, regenerado):** HUD com contorno de 2 px de breu + linha de tabatinga
no trilho de vida e no relógio, testado sobre céu, parede caiada e água (`docs/previas-layout/hud*.png`); alça em
meia-lua 16 px longe da borda (trilho P1 agora em x=48, P2 em x=720); dano fantasma em tabatinga com hachura de breu;
relógio com 2 dígitos grandes (fontes novas `naza_relogio` 48x72 e `naza_relogio_alerta`, cujos glifos já vêm como
"0"+dígito: o motor escreve o tempo sem zero e só usa a fonte de alerta abaixo de 10 s, conferido no `fightscreen.go`,
que escolhe o maior `counterN` com N <= tempo); `naza_num_alerta` saiu. Azulejo virou 1 bloco escuro de cada lado.
Poder numa placa de breu com friso de madeira clara, brilho em tabatinga, moringas de verdade (gargalo, boca, alça;
crua apagada, cozida tauá com brilho) e o número do nível (`p1.counter`, fonte naza_num). Tarja de madeira atrás do
nome e das vitórias (desenhada no sprite do trilho, que o motor desenha antes de tudo); bolinha cozida com aro de
tabatinga, crua em madeira. Título: logo com contorno "sticker" de tabatinga só por fora, friso contínuo no lugar das
espirais, V com ponta no VS; céu em faixas com pontilhado só em 6 px nas trocas; casario em degraus com muro de
arrimo, telhado capa-canal, janelas 2x3 em ritmo fixo, portas e 1 casa azul; Matriz maior com frontão e 2 sineiras;
ponte em blocos, sol num arco só, talha-mar, cabeceira e casario na margem direita; reflexo de lamparina em 2 linhas;
rodapé "NAZAFIGHT - RECONCAVO BAIANO" cortado. Seleção: grade sobe para y=380 com moldura de baixo, estante virou
faixa estreita, panos e barracas em 2 cores por lado, 1P/2P em letra de tabuleta numa tarja de breu fora da célula.

**Motor (cópia no scratchpad, `Motif = data/nazafight/system.def`):** título 14 s e luta rápida pengaro x raiclaven
(`-rounds 2`, IA 8): sem `save/logs/Ikemen_*.log`, nenhuma linha de `data/nazafight` no stdout; a luta saiu sozinha em
161 s (é a IA x IA que demora; com o motif padrão leva ~153 s). Determinístico (2 rodadas, mesmo hash).

**Pendente:** (1) **retratos fora da paleta e do grid** (item 9 da crítica): os 9000,0 e 9000,1 são dos lutadores em
`chars/`, que este trabalho não toca; precisam ser quantizados (grid 4x, 16 cores + 4 tons de pele) e o 9000,0
redesenhado a 28x28 por quem mexe nos lutadores. São a única fonte das cores de fora nas prévias. (2) A linha de
origem na tabuleta ("CAPOEIRA • NAZARÉ") não cabe no motif: o `[Select Info]` do v1.0.0 só escreve o nome; teria que
vir dentro do retrato 9000,1 de cada lutador. (3) Integrar no `.bat` (`motif/INSTALAR.md`). (4) **Não conferido na
tela**: posição real das barras, das fontes e do "08" só com filmagem ou o Breno olhando.

## 2026-11-10 — Layout NAZAFIGHT, rodada 3 (crítica de direção de arte r2) (Claude)

**Feito (tudo no `ferramentas/gerar_layout.py`, regenerado):** HUD: a vida do P1 e do P2 fica presa na ponta de fora,
junto do retrato, e o dano abre junto do relógio. Confirmei no `fightscreen.go` v1.0.0 (`calcBarFillRect`) que a
ponta presa é o 1º valor de `range.x`: P1 `16,399`, P2 `399,16`, e o poder segue a mesma regra. O enchimento ficou
liso, com 1 fileira de friso no topo e 2 de sombra; o friso é tabatinga na folha, tauá escuro no dendê e tauá vivo
no tauá. O fantasma é farinha lisa e o vazio é breu liso. A placa de nome de 288x80 virou uma tarja de 32 px (y 88 a
120) colada embaixo do trilho, com as vitórias ao lado do nome. O retrato (moldura 29x29 → 116, retrato 25x25 em
escala 4, fundo liso de rio) agora encosta na alça, em (4,4) e (1160,4), e o HUD de cima termina em y=120 (o
relógio desce até 152). Com isso o trilho encolheu para 104 lógicos e a vida para 96 → 384 px. A vitória crua é madeira
clara com contorno breu. O azulejo do relógio saiu. A placa de poder ficou com 436x48 no canto (y 668 a 716): trilho
de 64, 3 moringas e o número, e as cavilhas soltas das pontas saíram. Título: o logo virou letra por letra com 4 px de
breu entre elas, sentado numa contra-forma de breu (2 px em volta e cheia nos vãos, então o céu não vaza no F nem no
G), com anel de tabatinga e sombra (2,2). O N ganhou diagonal franca, o A ganhou furo em boca de moringa (aba, gargalo e
bojo) e há espiral de tabatinga de 1 px nas hastes. As faixas retas saíram, e o logo agora tem ~262 lógicos. A Matriz
desceu para um adro de pedra, com a torre inteira à esquerda do logo e o frontão logo abaixo dele. O sol subiu para trás
do parapeito, e por baixo dos arcos aparecem morro, beira e água (um arco com o reflexo do sol). O "F1: INFO" saiu.
Seleção: o fundo agora é tabuleiro de tábuas compridas, com panos de caxixis no meio e dos dois lados da grade. Os
retratos grandes ficam em fundo liso de rio, com a borda listrada do lado (P1 tauá, P2 rio), e as tabuletas de nome
estão centradas sob cada retrato (retrato P2 em x=808, altura 216, grade em y=392). O cursor P2 é reflexo com
contorno breu, a etiqueta 2P fica em cima à direita, espelhando a 1P, e `portrait.offset` passou para 12 (grade de 4).
VS: listras tom sobre tom (tauá/tauá escuro e rio/mangue).

**Motor (cópia nova em `scratchpad/motor_r3`, `Motif = data/nazafight/system.def`):** o título rodou 14 s e a luta
rápida pengaro x raiclaven (`-rounds 2`, IA 8) saiu sozinha com código 0 em 220 s. Não houve `save/logs/Ikemen_*.log`,
e os únicos avisos são de comando dos lutadores, nenhum de `data/nazafight`. Os 220 s passam dos 90 s do critério,
mas é a luta IA x IA que demora (153 s com o motif padrão na rodada 2), e a duração varia de luta para luta. O gerador é
determinístico: rodei 2 vezes e deu o mesmo hash.

**Pendente:** (1) os retratos 9000,0 e 9000,1 ainda estão fora da paleta (140 cores no HUD, 515 na seleção e 247 no
VS); o certo é redesenhar o 9000,0 em 25x25 na paleta, em `chars/`. (2) O `.bat` (`motif/INSTALAR.md`) não mudou. (3)
**Não conferido na tela:** a direção real do esvaziamento, a posição da tarja e do retrato e o "08" só se confirmam com
filmagem (`ferramentas/filmar_luta.py`) ou com o Breno olhando.
