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

## 2026-11-10 — Peso: .sff com link e poda, fumaça do Despertar, launcher rápido (Claude, plano de otimização)

- **Peso 1 (link)** e **Peso 3 (poda)** no `escrever_sff`: sprite repetido vira link (len 0) e o que o jogo nunca
  desenha sai do .sff (fica: `.air`, grupo 9000, `SPRITES_VITIMA` dos arremessos e destino alcançável do remap).
  .sff antes -> link -> link+poda: pengaro 15,43 -> 13,98 -> 11,72 MB; gutto 16,34 -> 14,38 -> 12,27;
  raiclaven 20,50 -> 9,20 -> 7,65; hazaki 0,92 -> 0,61 -> 0,55; total 53,2 -> 32,2 MB.
  Raiclaven x Hazaki (`medir_carga`, sem captura): pico privado 1608 -> 1152 -> 1068 MB, residente 1164 -> ~920 -> ~860 MB,
  carga ~6 s -> ~5,2 s. Pengaró x Hazaki: 1640 -> 1391 MB. Pixels: `ferramentas/conferir_sff.py` igual à linha de base.
- **Atenção:** gerar de novo nesta máquina muda o Pengaró inteiro (paleta outra, por causa do 9000,1) e o Gutto em
  `chars/` está atrás do gerador (3289 contra 3310 sprites, .air/.cns diferentes). Por isso Pengaró e Gutto foram
  religados/podados do .sff commitado com `conferir_sff.py religar ... --podar chars/<lutador>`. Quem regenerar o Gutto
  vai trazer essa diferença junto: decisão à parte.
- **Peso 2:** fumaça da saída do Despertar com `NumExplod(9215) = 0` e `id = 9215`. O caso do hitpause não foi reproduzido.
- **Peso 4:** launcher pergunta só o sha (abertura sem novidade 4-8 s -> ~0,3 s), baixa em `.part`, recupera manifesto
  estragado, `VsScreenLoading = 1` e `WindowScaleMode = 0`. Falhas simuladas numa pasta temporária, não no PC de ninguém.
- Robô igual antes e depois: Pengaró 146/0, Gutto e Raiclaven 143/1 (a falha `var(37)` no 3100 já existia).
- **Não visto no jogo por pessoa:** fluidez, a tela de VS carregando e a janela com `WindowScaleMode = 0`. O motor foi visto
  por foto do próprio framebuffer (Raiclaven x Hazaki com link, poses certas). Já existia: Hazaki arremessado pelos outros
  some (o .sff dele não tem os 25 desenhos de vítima; `verificar --hazaki` agora avisa).

## 2026-11-10 — Filmagem do jogo dentro do Windows Sandbox (Claude)

- **Feito:** `ferramentas/filmar_sandbox.py` (+ `ferramentas/robo/golpes.lua`). Monta um `.wsb` sem rede e sem vGPU
  (motor, repo, Mesa e ffmpeg somente leitura; só a saída gravável), roda P1 x P2 com OpenGL por software (Mesa 26.2.6
  llvmpipe, mesa-dist-win mingw x64, sha256 do .7z igual ao publicado, em `%USERPROFILE%/JogoDeLuta/ferramentas_sandbox/mesa`)
  e grava `luta.mp4` com gdigrab lá dentro. Motivo: `filmar_luta.py` fotografava a tela do dono.
- **Medido:** gdigrab na sandbox para em ~31 fps reais (BitBlt; `ddagrab` não abre sem GPU). Solução: jogo a 1/4
  (`setAccel` no início do round, `TickInterpolation = 0`), captura a 15 fps, retimado para 60. Prova Pengaró x Hazaki
  10 s: 1280x720, 600 quadros a 60/1, 607 ticks contados, 562 quadros distintos (os iguais são pose parada ou jitter).
  Escala de 125% herdada do host exigia `__COMPAT_LAYER=HighDpiAware` (sem isso a janela vinha 1600x900 recortada).
- **Pendente:** `--despertar` dentro da sandbox não foi filmado (lógica copiada do `filmar_luta.py`). `como-trabalhar.md`
  ainda cita o `filmar_luta.py` no estado de 2026-11-07.

## 2026-11-10 — Estilo de pose segurada nos golpes do Pengaró (Claude)

- **Feito:** `SECO()` + `Air.seco` em `gerar_pengaro.py`: golpes 200–3999 (fora projéteis, rolamento 700/705 e Despertar
  2000), reações 5000–5017, defesa 130/150, queda 5100/5120 e 10/12 viram poses paradas (sem vai-e-volta e sem quadros
  do meio). Contato num desenho só (o de maior alcance no caminho antigo) + 1 tick (fraco) ou 2 (forte) tirados da
  recuperação; smear de até 2 ticks; recuperação longa vira poses de ~9. Assert confere soma de ticks, caixa e AnimElem.
  10/12 passaram a 2 ticks (frame data). Tremida só no finalizador e no super final (metade). Faísca 8 ticks (4 x 2),
  pico ~40 px. BGPalFX branco de 4 ticks na super, AfterImage de 2 em 2. Regra 7 reescrita; `video_golpe.py` aceita
  até 9 ticks parados nessas ações. Robô na sandbox 146/0; vídeo em `%USERPROFILE%/JogoDeLuta/filmagens/estilo_seco`.
- **Pendente:** ver no jogo a sensação (contato, recuperação, sem tremida, clarão da super); o Clsn1 aparado por
  desenho agora segue a pose segurada (alcance máximo igual, ±3 px). SFF caiu de 11,7 para 6,9 MB (meio sem uso podado).
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

## 2026-11-10 (tarde) — sandbox, layout no launcher, estilo seco, pipeline arcade

- **Testes só na sandbox** (regra do dono): `ferramentas/sandbox.py` roda o IKEMEN dentro do Windows Sandbox (sem rede, sem vGPU,
  Mesa llvmpipe) e espera a vez; `testar_pengaro.py` usa a sandbox por padrão (146 PASS em 86 s); `filmar_luta.py` só com
  `--local`; `filmar_sandbox.py` filma a 60 fps de tempo de jogo (o jogo roda a 1/4 e o vídeo é retimado).
- **Layout Nazafight** (título, seleção, VS, HUD) mesclado (eee2800) e instalado pelo launcher (1684d87, 6b7f275): baixa
  `motif/` por manifesto, espelha em `ikemen/data/nazafight`, grava `Motif =` no config; `.def` por último, para queda de rede
  não ligar motif pela metade. Visto na sandbox (título → seleção → luta, sem panic). Falta: retratos 9000,x na paleta; uma
  pessoa olhar o HUD rodando.
- **Estilo seco de arcade** no Pengaró (adde1e6): golpes, reações e defesa com contato segurado no hitstop e recuperação em
  poses; sem tremida de tela; faísca 8 ticks. Filmado na sandbox; a super (clarão de 4 ticks) ainda não foi filmada.
- **Pipeline arcade** (453680f): `quantizar_folha.py` (paleta fixa 15 cores), `conferir_arte.py`, `animar_folha.py --arcade`;
  fichas e fila de 117 folhas em `docs/arcade/`. 7 folhas do Pengaró em `sprites/pengaro/quadros/folhas_arcade/` (8734ee1).
  Nada das folhas arcade está ligado nos geradores ainda.
- Blender 4.5.15 em `C:/Dev/Tools/Blender` (o 4.5.14 foi apagado a pedido).
- **Próximo:** terminar a fila no ChatGPT (um agente gerando; downloads pedem clique em Salvar), ligar `folhas_arcade` nos
  geradores (golpes como poses secas, Blender só em ginga/andar/pulo), depois pente fino de animação e anatomia em todos.
  Decisões que ficaram com o Breno: diagonal/meia-lua (a regra proíbe hoje), Hazaki rival ou boneco, transformações por
  paleta ou folha própria.

## 2026-11-10 (noite) — Nome Nazafights e estilo arcade como regra (Claude, sessão do Breno)

**Pedido do Breno:** o estilo arcade anos 90 que o Alisson montou passa a ser regra, e o jogo se chama **Nazafights**
(com "s"), em tudo, para não confundir.

- Regra escrita em `docs/como-trabalhar.md` (Regras do Breno) e no topo da seção arcade de `docs/biblia-de-arte.md`.
- Nome trocado no README, na janela (`WindowTitle` gravado pelo `.bat`), no logo da tela de título (10 letras, ~290 de
  320 lógicos; a nuvem de farinha alargou junto), nos `.def` do motif e nas fontes. Layout regerado, verificação ok.
- **Não trocado de propósito:** a pasta `motif/nazafight`, `data/nazafight`, `%USERPROFILE%\JogoDeLuta` e o nome do
  `.bat`. O `.bat` que cada um já tem procura esses caminhos; trocar deixaria o layout de fora até todos pegarem o novo.
  As entradas antigas deste LOGBOOK ficam como foram escritas.
- Ainda no estilo antigo: `folhas_gutto.py` e `folhas_raiclaven.py` (prompts `CABECA` "16-bit SNES") e as folhas do
  Gutto e do Raiclaven no jogo. Folha nova sai pelo prompt base de `docs/arcade/<lutador>.md`.
## 2026-11-10 (noite) — pausa: folhas arcade geradas, falta ligar no jogo

- Robô rodado na sandbox a pedido do Breno: 146 PASS / 0 FAIL.
- Agente do ChatGPT parado (dono desligou o note). Folhas em `sprites/<l>/quadros/folhas_arcade/`: Pengaró 20, Gutto 19, Raiclaven 19, Hazaki 15. Hazaki parou em "rolamento" (próxima da fila em `docs/arcade/fila.md`; "caneta" já aprovada pelo agente mas pode não ter sido salva).
- Notado nas folhas cruas: escala varia entre ações (Raiclaven no `pulo` maior que no `ginga`); `cabecada` do Gutto é joelhada e a do Raiclaven é tesoura (renomear no código).
- Próximo: terminar a fila do Hazaki (lote 3 dos demais, se houver), ligar `folhas_arcade` nos geradores (Pengaró primeiro: quantizar → Blender só nas ações fluidas → quantizar --meio → conferir_arte), validar na sandbox, depois o pente fino de animação/anatomia.

## 2026-11-11 — Pengaró: pente fino de anatomia (branch `anatomia`, sem push)

**Pedido do dono:** "corrija todos os erros de anatomia... quando ginga fica com três mãos, as pernas fazem movimentos
estranhos, queria que ficasse bem natural".

**Causa da ginga:** `ginga_fluida` tinha 64 quadros para 8 desenhos; os do meio eram fluxo óptico (um desenho entortado
até a metade e trocado pelo seguinte) e os próprios desenhos 2 e 6 tinham braço duplicado e caneleira na outra perna.

**Feito (4 commits):**

- Ginga e andar só com desenhos da folha arcade, sem quadro do meio: `LOOPS` em `gerar_pengaro.py`. Ginga = 8 desenhos
  de `quadros_arcade/ginga` a 6 ticks, com a ponta do pé da frente cravada no mesmo x (`PE_DA_FRENTE`); andar = desenhos
  0,2,3,4,1,5 de `quadros_arcade/anda` (o 6 da folha levanta a mesma perna do 2); correr usa os mesmos a 3 ticks.
  Pastas `ginga_fluida`, `anda_fluida`, `e_anda_fluida` apagadas; `ginga_endiabrada` ficou só com os 8 desenhos (00-07).
- Endiabrado: ginga com os desenhos limpos 0,1,2,6,7 e andar com 0,1,5,7 (`LOOPS_ENDIABRADOS`); não usa mais quadro do
  meio em nenhuma folha (`par_endiabrado`); desenhos errados trocados pelo vizinho (`TROCA_ENDIABRADA`).
- `sem_rosa` / `sem_fundo_endiabrado` no `abrir_quadro`: tiram o resto de fundo magenta de todas as folhas na carga.
- `MEIO_PROIBIDO`: corte seco onde o quadro do meio derretia (vitória, despertar_a, provocação, defesa).
- `levanta` sai de `quadros_arcade` (`ARCADE`). Intro começa com a lata na mão; defesa entra no desenho 3; derrota
  termina no 6.
- Retoques de pixel nos desenhos (não refeitos pelo Blender): `chute_baixo` 03/05 e meios, `chute_alto` 01,
  `provoca` 02/03, `e_anda` 05. **Cuidado:** rodar `animar_folha.py` nessas folhas recorta de novo da folha crua e
  desfaz o retoque.
- Os grupos do `.sff` dos loops antigos ficam reservados (`VAGAS_DO_FLUXO`) para `SPRITES_VITIMA` não mudar.
- Gutto e Raiclaven usam `gerar_pengaro` trocando `QUADROS`: tudo isso só vale quando `desenhado()` é verdadeiro. Os
  .air/.cns/.sff deles saem byte a byte iguais aos do gerador de antes (conferido por md5; os arquivos commitados em
  `chars/gutto` e `chars/raiclaven` já estavam diferentes do que o gerador da `mugen` produz, não mexi).
- `verificar_pengaro.py` falhava na `mugen` ("paleta": o .sff tem 2 paletas desde o Endiabrado na seleção); aceita 2.

**Testado:** `verificar_pengaro.py` sem erro; robô na sandbox 146 PASS / 0 FAIL; ginga e andar filmados na sandbox.
O motor só anda com tecla de verdade, então o filme do andar usa dois estados só da cópia da sandbox que tocam as
ações 20/21 com a velocidade de andar: o estado 20 de verdade não foi filmado.

**Pendente (precisa de desenho):** lista com MOTION pronta no fim de `docs/arcade/fila.md` (Lote 5). Não retocado: duas
caneleiras no ar (`ar_soco`, `bicicleta`, `pulo` 03), `caneta` 04, `agarrao` 04/05, `armada`, `bola`, `compasso`,
garrafa que muda de mão para beber, três famílias de cor nas folhas `e_`, olho furado em ~19 desenhos `e_`.


## 2026-11-11 (2ª passada) — pente fino de anatomia depois da revisão dos céticos (branch `anatomia`, sem push)

**Corrigido (tudo em `ferramentas/gerar_pengaro.py`, nada de quadro do meio novo):**

- **Ginga:** agora é um vai-e-volta só. `LOOPS["ginga_fluida"]` = desenhos 3, 7, 5, 6, 2, 1 da folha arcade (em pé, pé de
  trás na ponta, afundo, volta) a 6/6/5/7/7/5 ticks. Os desenhos 0 e 4 (base aberta com o tronco para trás) saíram: era
  entre eles e os vizinhos que a cabeça pulava 23 px e o pé de trás fazia zigue-zague. Pé da frente cravado como antes.
  `mao_sem_cordao` tira os pontos amarelos/lilás das pontas dos dedos.
- **Andar:** as duas metades da passada duram quase o mesmo (8,8 / 5,4,4,5); `perna_de_tras_na_sombra` deixa a perna sem
  caneleira lilás também no desenho 0 (a cor piscava na volta do ciclo).
- **Intro (190/191/192):** saiu o desenho de abrir o lacre (`DESENHO_PROIBIDO`, `MEIO_PROIBIDO` lata 0 e 1): tinha TRÊS
  mãos (garrafa, lata e uma abrindo o lacre). A lata já está na mão e ele vai direto para o gole.
- **Chutes em pé (230, 240, 245, 246, 260...):** a caneleira sumia das duas pernas durante o golpe e voltava de estalo.
  `caneleira_no_apoio` pinta a caneleira na canela da perna de apoio (a de trás) nos desenhos e quadros do meio do
  golpe; `canela_creme` troca a placa lilás do retoque anterior pelo creme da calça; `sem_rosa(miolo_branco=True)` tira
  a tira branca atrás da coxa no chute alto (miolo do clarão rosa do fundo).
- **Agachado parado (11):** `PES_NO_CHAO` assenta todos os desenhos na linha do chão (subia 1 px com os pés junto).
- **Endiabrado:** ginga 0, 7, 1, 2, 2, 1 com o pé da frente cravado (`PE_DA_FRENTE_ENDIABRADO`; antes os dois pés
  pulavam 20-38 px); andar só com as poses de bote 1, 5, 3 (não alterna mais com a guarda em pé) e na escala da folha
  (não engorda 18%); `calca_roxa` leva a calça marrom de metade das folhas `e_` para o roxo da ginga; `fechar_furos`
  pinta com a cor de quem está em volta (era o magenta vivo que aparecia no meio da figura) e não fecha elo de
  corrente; `sem_fundo_endiabrado` tira bloco grande de fundo também perto da cabeça (agachado); `sem_algema_da_frente`
  no `e_agachado`; `sem_farelo` no `despertar_b`.
- **Ginga do Despertar congelada (Pengaró, Gutto e Raiclaven):** `sem_ginga_9203` tira o ChangeAnim para a ação 9203. O
  estado 0 do motor (`common1.cns.zss`: `anim != 0` → ação 0) desfazia a troca todo tick e a ginga despertada ficava
  parada no 1º desenho. A ginga despertada sai da ação 0 pelo RemapPreset. O Hazaki ainda tem o bloco (não mexi).
- 17 imagens de depuração `acao_*.png` saíram da raiz (ainda estão no histórico do commit 9d19c9a: juntar os commits
  no merge).

**Testado:** `verificar_pengaro.py` sem erro; robô na sandbox: Pengaró 146 PASS / 0 FAIL; Gutto e Raiclaven 143 / 1, a
mesma falha de antes (`var(37) = 1 no meio do 3100`, checagem do robô que só vale para o Pengaró). Ginga normal e
despertada filmadas na sandbox: as duas animam (a despertada não fica mais congelada).

**Continua pendente (precisa de desenho novo, pedidos no Lote 5 de `docs/arcade/fila.md`):** ginga com desenho de
passagem de verdade; andar com as duas passadas (hoje a 2ª metade tem 4 desenhos e a 1ª tem 2, o pé patina); corrida
(usa os desenhos do andar); estilo: ginga, andar e levantada são folha arcade e o resto é a arte antiga; garrafa que
troca de mão para beber (195, 181, 2000), que pula de lado na defesa (120-140) e vai para o peito no agachar; derrota
sentado sem caneleira; duas caneleiras no ar (41, 600, 650, 700), bola, compasso; andar endiabrado sem passada de
verdade; olho endiabrado apagado nos desenhos de cabeça baixa. Gutto e Raiclaven: tudo o que os céticos listaram menos
a ginga 9203 (derrota, soco no ar, cavalo, Despertar do Gutto; objeto da mão, rasteira, rolamento, tesourada, vitória
do Raiclaven) é defeito do próprio desenho e só sai com folha nova.


## 2026-11-11 (fecho) — anatomia na mugen, Hazak em andamento, borrão do Pengaró diagnosticado

- **Anatomia:** a branch `anatomia` entrou na `mugen` num commit só (fb95f91). Detalhes nas duas entradas acima.
  Os três revisores NÃO aprovaram como "natural": o que sobra é defeito do desenho e só sai com folha nova.
- **Borrão / troca de estilo do Pengaró (queixa do Alisson):** ginga, andar e levantada já são arte arcade (16 cores,
  pixel seco); todos os golpes ainda são a arte antiga (milhares de cores, reduzida com LANCZOS = contorno mole). Na
  tela ele troca de cara a cada golpe. Conserto: converter as folhas restantes para arcade. Das 62 pastas do Pengaró,
  20 têm folha em `folhas_arcade/` e só 11 estão em `quadros_arcade/`; faltam gerar no ChatGPT ~22 normais (agarrao,
  armada, bola, caneta, compasso, derrota, golaco, lata, provoca, rolamento, vitoria, despertar...) e todas as `e_`.
  Gutto: 19 folhas arcade, nenhuma ligada (falta paleta arcade dele). Raiclaven: 19, 8 ligadas.
- **Hazak (branch `hazak`, não vai para a mugen sem o Breno aprovar):** ficha do Breno em `docs/fichas/hazaki.md`;
  fila de 120 folhas em `docs/arcade/fila_hazak.md`; especificação do gerador em `docs/arcade/hazak_gerador.md`;
  lote 1 gerado (30 folhas na pasta). Lotes 2 a 4 sendo gerados; 5 a 7 (Diabo Loiro) esperam o Breno.
  Perguntas abertas para o Breno: Nota Falsa/Suborno em ↓↑ bate com o superpulo (propus ↓←); Chuva de Dinheiro em x+y
  contra a regra de super num botão; o que continua valendo dentro do Diabo Loiro; a fala da provocação.
- **Pedido do Alisson:** forma Endiabrada do Pengaró redesenhada inteira, roupa de boss final e aura absurda (casa com
  a regra nova do Breno: toda forma despertada tem aura própria). Fazer folha de conceito para ele aprovar antes.
- **Falha 143/1 do robô em Gutto e Raiclaven** (`var(37)` no meio do 3100): já existia, ninguém investigou.
- **Hazaki** ainda tem o bloco da ação 9203 que congelava a ginga do Despertar; sai no gerador novo.


## 2026-11-11 (arcade) — golpes do Pengaró na arte arcade (branch `mugen`)

**Por quê:** ginga, andar e levantada eram arte arcade (16 cores, pixel seco) e todos os golpes a arte antiga: na tela
ele trocava de cabelo, tom de pele e caneleira a cada golpe e parecia borrado.

**Feito (`ferramentas/gerar_pengaro.py`, `sprites/pengaro/quadros_arcade/`, `chars/pengaro`):**

- `ARCADE` passou de `{levanta}` para 15 folhas: soco, chute_alto, martelo, afastar, apanha, queda, pulo, agachado,
  baixo_soco, rasteirinha, rasteira, ar_soco, bicicleta, cabecada (e levanta). Saem de `quadros_arcade/<folha>/`, 8
  desenhos segurados; quadro do meio só onde a pasta arcade tem `meio/` (soco, ar_soco, bicicleta, cabecada), e ali
  ele entra só como smear de 1-2 ticks antes do contato.
- `q_soco<i>` (soco fraco 200) lia `quadros/soco` direto; agora passa por `pasta_da_folha`.
- `PASTA_ARCADE = {"rasteira": "chute_agachado"}`: a folha arcade da rasteira foi reprovada (duas garrafas, joelheira
  verde) e a folha que veio como "chute_baixo" é um chute rasteiro agachado. Ela entra no lugar da rasteira (440 e os
  sprites `rasteira0..3` do super 3100). **Muda a cara do 440**: chute rasteiro de guarda alta em vez do giro com as
  mãos no chão. Decisão a confirmar com o dono.
- Ações escritas à mão no arcade, com os MESMOS tempos e a mesma quantidade de elementos: 240 (o desenho 5 ainda é
  perna esticada: 2 ticks, o resto vai para o 6 e o 7), 210/215 (cotovelada: armação 2-3, contato 4), 430 (contato no
  desenho 3; o 4 troca a pose do braço e está em `DESENHO_PROIBIDO`), 440.
- `DESLOCA_ARCADE`: afastar 6 em -10 px (pé de apoio plantado). Agachar (10/12) usa o desenho 0.
- Caixas: Clsn1 do 400 sobe 10 px, do 430 8 px, do 440 4 px (o membro mudou de altura). No Pengaró o agachado passa a
  `(-28,0,28,-80)` (era -70; o desenho tem 77-85 px) e o deitado a `(-70,0,70,-34)`; rolamento, caneta e levantada
  ficam em -70 (`ROLANDO`). O resto das Clsn1 é recortado sozinho pelo `ajustar_clsn1` conforme o desenho novo.
- Cabelo: a quantização levava o cabelo para os vinhos da pele em várias folhas. Repintado nos PNGs (pelos avaliadores
  em martelo, afastar, apanha, pulo, agachado, baixo_soco, rasteirinha, chute_agachado; por mim em cabecada e ar_soco,
  desenhos e `meio/`, e em queda). Scripts em `ferramentas/retoques_arcade/` (têm caminhos da sessão dentro; servem de
  registro). **Rodar `quantizar_folha.py` de novo nessas folhas desfaz o retoque** (e a escala da queda e do agachado,
  e a caneleira pintada na bicicleta 3-5).

**Conferido:** tempos (início da caixa, duração do ativo, total) de TODAS as 254 ações iguais aos de antes, comparando
os `.air`; `chars/gutto` e `chars/raiclaven` com o mesmo md5 antes e depois; `verificar_pengaro.py` sem erro; robô na
sandbox 146 PASS / 0 FAIL; filme de 8 s na sandbox (soco, chutes, agachado, rasteiras) olhado em tiras.

**Mudou no jogo (consequência do desenho, precisa de olho de quem joga):** alcance da Clsn1 pelo recorte automático:
cotovelada 210/215/216 de 48 para 41; chute alto 240 de 58 para 79 (e 323, 3401, 3432 +11 a +16); soco no ar 600 de
38 para 49; bicicleta 610/650 de 62/63 para 57. Agachado 10 px mais alto.

**Ficou na arte antiga:** `chute_baixo` (230, 245, 231, 1500/1501, `pisa`) e `defesa` (120-150, 760): as folhas arcade
são de outro golpe / outro modelo. E as folhas sem desenho arcade: agarrao, armada, bola, caneta, compasso, derrota,
golaco, lata, provoca, rolamento, vitoria, despertar e todas as `e_` (o Endiabrado inteiro). Pedidos de desenho de
chute_baixo, defesa, rasteira e agachado (cocorinha) com os avaliadores; entram em `docs/arcade/fila.md`.

**Não conferido:** pulo e golpes no ar em movimento (o robô da filmagem não pula: `holdup` injetado não faz o motor
pular); forma endiabrada por cima dos desenhos novos (o alinhamento usa a pose normal, que mudou em agachado, rasteira
e cotovelada); `gerar_hazaki.py` não foi rodado (não usa as folhas, mas não foi medido). No 600 o contato segurado é o
desenho 5 (braço dobrando), porque a caixa fica na altura do ombro e o punho do desenho 4 passa por baixo dela; para
segurar o 4 a caixa teria de descer até o punho, o que muda o alcance do soco no ar.


## 2026-11-11 (arcade, retoque) — o que os céticos acharam na integração dos golpes arcade do Pengaró

**Corrigido (`ferramentas/gerar_pengaro.py`, `sprites/pengaro/quadros_arcade/`, `chars/pengaro`):**

- **Deitado sem caneleira** (`queda/07`, ações 5110, 5150, 5160, 5170): caneleira pintada na canela da perna visível.
  **Nó amarelo solto atrás do ombro** (`levanta/04`): apagado. Registro em
  `ferramentas/retoques_arcade/retoque2_caneleira_no.py` (não rodar de novo: parte do PNG do commit 4fc03ed).
- **Super 3100/13100 trocava de arte no meio:** no Pengaró o compasso (`gira1`) vira a bênção (`f_afastar4`) e a armada
  (`kick_alto`) vira o chute alto (`f_chute_alto4`). O super inteiro é arcade. Alcance desses dois elementos pelo
  recorte: 57 para 65 e 67 para 79 (13100: 57 para 63 e 67 para 65).
- **1701 (rolê por trás e chute) misturava as artes:** os 15 ticks do rolê (um desenho só da folha antiga `rolamento`)
  passam a ser a bola no chão da levantada arcade (`levanta 2`); `DESENHOS_ARCADE_DO_GOLPE`.
- **Caixas (Clsn1) fora do membro:** 430 vai até o pé (x 62 para 78; 10430 54 para 70); 322 e 342 seguram o desenho 3
  (o 4 é o `DESENHO_PROIBIDO`) com a caixa do 430; 600 desce até o punho (base -62 para -46; o contato segurado passa
  a ser o quadro do meio 04_6, punho esticado); 601 desce até a mão (base -40 para -24); 10240 sobe até o pé do chute
  endiabrado, que é mais alto (`CAIXA_DESPERTADA`: topo -100 para -116, alcance 56 para 65); `CAIXA_ARCADE`.
- **Teto de sobra:** ação sem variante 1xxxx usa a maior medida entre as duas formas, mas agora nunca mais de 12 px
  além do membro da forma normal (`SOBRA_MAXIMA_CLSN1`, só no Pengaró). A cabeçada 303 foi de 57 para 52 (estava 17 px
  à frente da cabeça). Nenhuma outra caixa mudou por causa disso.

**Conferido:** comparação elemento a elemento do `.air` antes e depois: só mudaram as ações 303, 322, 342, 430, 600,
601, 1701, 3100, 10240, 10430, 10600, 10601, 13100; tempos e quantidade de elementos iguais. No `.cns` só mudaram
sparkxy/pos de 7 linhas (acompanham as caixas). `chars/gutto` e `chars/raiclaven` regerados sem diferença.
`verificar_pengaro.py` sem erro; avisos de Clsn1 de 29 para 26 elementos (saíram 303 e 3100; os que sobram são todos
`[endiabrado]`). Robô na sandbox, rodado depois de regerar (12:12): 146 PASS / 0 FAIL.

**Recusado / fica como está:**

- Cabelo do apanha (tufo cheio atrás): é a cabeça jogada para trás, com a nuca à mostra; a cor é a da paleta. Mudar o
  corte é redesenhar a cabeça de 4 desenhos.
- Garrafa "pousada" na bananeira (`levanta/03`): ela está encostada na mão de apoio; lê-se como garrafa na mão.
- Agachado em -80: o desenho tem 77 a 85 px. Consequência no jogo: os golpes 301, 340 e 343 (Gutto, Raiclaven e o
  próprio Pengaró), com base da caixa em -70, agora acertam o Pengaró agachado com 10 px de folga. Precisa de olho de
  quem joga.

**Pendente (precisa de folha arcade nova):** entrada 190 (e 181, 191, 192, 195: folha `lata`, arte antiga, 115 a 121 px
contra 110 da ginga); rolamento (700, 705, 1700, 3402, 5200, 5210); compasso, armada, caneta, bola, agarrao, golaco,
provoca, vitoria, derrota, despertar, chute_baixo, defesa e todas as `e_`.

**Correções ao relato anterior:** a quantidade de elementos do `.air` mudou em várias ações (210/215, 240, 430, 440,
3200...), sem efeito: os gatilhos AnimElem foram renumerados e disparam no mesmo tick. A tabela de alcance estava
incompleta (246, 260, 331, 341, 346, 3420, 601, 611, 3403, 1400/1401, 3200, 302/311/343/344/3410/3431 e várias 1xxxx
também mudaram alguns px pelo recorte automático).

## 2026-11-11: Pengaró, Lote 6 grupos A a D gerados no ChatGPT (17 folhas em `folhas_arcade`)

Só as folhas brutas (2172x724, fundo magenta) em `sprites/pengaro/quadros/folhas_arcade/`. **Nada foi convertido nem
ligado no gerador**: falta `quantizar_folha.py` -> `animar_folha.py --arcade` -> `quantizar_folha.py --meio` ->
`conferir_arte.py` e pôr cada folha em `ARCADE` no `gerar_pengaro.py`. Nenhum teste de jogo rodado (sandbox não usada).

Chat "Pengaró — arcade": https://chatgpt.com/c/6af486c5-5ea0-83e8-ab3c-0685922066a2, `soco.png` anexada em toda
mensagem, prompt do Lote 6 de `docs/arcade/fila.md` sem mudança; nas refações, um parágrafo antes do prompt dizendo o
defeito. Conferência no disco, ampliada, quadro a quadro; medida por coluna magenta e por peça ligada (as 17 têm 8
figuras, uma por célula, sem pedaço solto). Commits c446477 (A), 41a045a (B), dc4cc4e (C), bca9a30 (D), todos em origin/mugen.

| Folha | Tentativas | Resultado |
|---|---|---|
| defesa, chute_baixo, rasteira | 1 | aprovadas (as antigas estão no scratchpad `lote6/antigas/`) |
| bola, armada, rolamento | 1 | aprovadas |
| compasso | 2 | aprovada (1ª: quadro 3 sem caneleira). Quadros 6 e 7 se sobrepõem em coluna, mas são peças separadas |
| agarrao | 3 | aprovada (1ª: garrafa do lado errado de costas, q5-6; 2ª: mão do q8 cortada na borda direita). ~3% menor |
| caneta | 3 | **com defeito**: risco rosa-avermelhado fino (contorno fantasma) acima do pé no quadro 4 |
| lata | 1 | aprovada |
| provoca | 2 | aprovada (1ª bebia com a mão da frente em q3-4) |
| derrota | 3 | aprovada (1ª: riscos de movimento na cabeça do q7; 2ª: dedos do pé do q8 cortados na borda). Chão em y=550, garrafa com gargalo à mostra |
| golaco | 3 | **com defeito**: no quadro 2 bebe com a mão da FRENTE e o braço de trás fica solto (q1 corrigido). Figura em pé ereta com ~301 px (ginga 276), chão em y=552 |
| vitoria | 3 | **com defeito** (salva a 2ª): quadros 4 a 6 bebem com a mão da FRENTE; no q7 a garrafa é segurada no peito com o polegar para cima. A 3ª tinha uma mão sem braço no q7 |
| anda, corre, recuo | 1 | aprovadas (na corre as pontas da faixa voam para trás, saindo de trás da mão da garrafa) |

O que aprendi para a próxima rodada: o modelo de imagem tende a levar a garrafa à boca com o braço do lado DIREITO da
imagem. Funcionou em `provoca` dizer "the arm on the LEFT side of the image is folded across the chest holding the bottle
to the mouth, the arm on the RIGHT side hangs empty"; em `golaco` e `vitoria` não pegou em todos os quadros. Pedir
"magenta margin on all four sides" resolve corte na borda. Pendentes do Lote 6: grupo E (agachado, rasteirinha, queda,
bicicleta), opcional.

## 2026-11-11 (Lote 6 ligado): Pengaró normal inteiro na arte arcade, menos a cena do Despertar

**Feito (`sprites/pengaro/quadros_arcade/`, `ferramentas/gerar_pengaro.py`, `chars/pengaro`):** as 17 folhas dos grupos
A a D do Lote 6 foram convertidas e ligadas. `ARCADE` ganhou chute_baixo, defesa, bola, compasso, armada, caneta,
rolamento, agarrao, golaco, lata, provoca, vitoria, derrota, corre e recuo; `rasteira` passou a ter pasta própria
(`PASTA_ARCADE` vazio; `quadros_arcade/chute_agachado/` ficou em disco, sem uso); `anda` foi trocada pela folha nova.

- **Conversão** (registro em `ferramentas/retoques_arcade/lote6_converter.py`, `lote6_cabelo.py`, `lote6_sementes.json`):
  figuras separadas por peça ligada, tronco no eixo, base no chão (só `corre` guarda a altura dos quadros de voo),
  paleta de 15 cores. Fator de escala só em `agarrao` (1.03) e `golaco` (0.917); as outras já vieram na escala da
  ginga. Cabelo repintado em todos os quadros em que a quantização o levou para os vinhos da pele (cabeça achada pelo
  topo da figura; 7 quadros com semente à mão; 12 quadros pulados porque o cabelo já estava escuro e o topo era a
  garrafa ou a mão). `conferir_arte.py`: R1, R3, R4, R5 e R7 PASS nos 8 quadros das 17 folhas. **Rodar
  `quantizar_folha.py` nessas folhas desfaz o cabelo e a escala.** Nenhum retoque de caneleira foi preciso.
- **Desenhos com defeito, repetidos por outro da mesma folha** (`REPETE_ARCADE`): golaco 1 (bebe com a mão da frente)
  vira o 0; vitoria 3 a 7 (bebe com a mão da frente, garrafa no peito) viram 2, 1, 2, 2, 2: a vitória é ginga,
  garrafa subindo, garrafa erguida, segundo brinde e pose final com a garrafa no alto.
- **Andar** (20/21): `LOOPS["anda_fluida"]` = desenhos 0, 2, 3, 4, 6, 7 em 6, 6, 5, 6, 6, 5 ticks (total 34, igual). Na
  folha nova as duas pernas alternam e a base é a da ginga; a anterior levantava duas vezes a perna da caneleira.
  `perna_de_tras_na_sombra` deixou de ser usada (era um remendo da folha antiga).
- **Correr** (100): desenho próprio, os 8 da folha `corre` a 2 ticks (ciclo de 16; era o andar em 15). **Recuo** (105):
  `recuo` 2 por 3 ticks e 3 até pousar (era a defesa inclinada). `corre` e `recuo` entraram no FIM de `FOLHAS`, para
  nenhum outro sprite mudar de número. No Despertar as duas ações continuam com o desenho endiabrado de antes
  (`ENDIABRADO_EMPRESTADO`: andar endiabrado e `e_defesa` 6).
- **Desfeito:** o improviso da 1701 com a bola da levantada (volta a usar `rolamento`); o super 3100 voltou ao giro e à
  armada (o giro agora é o compasso 4, perna esticada na frente: no 3 a perna ainda está atrás e a caixa do super não
  tinha membro dentro); a ação 440 escrita à mão para o `chute_agachado` (a rasteira nova segue os índices da
  `sequencia`); o corte da derrota no desenho 6 (vai até o 7).
- **Caixas:** 230 sobe para a perna do chute novo, que bate na barriga: `(12,-66,62,-46)` (era `(12,-56,58,-42)`).
  1500/1501: `(8,-68,60,-44)` (era `(8,-37,64,-2)`, abaixo da perna: o contato segurado caía no desenho da perna
  dobrada e o alcance ia a 23). As variantes despertadas de 230, 1500 e 1501 ficam com a caixa antiga
  (`CAIXA_DESPERTADA`), porque o `e_chute_baixo` não foi redesenhado.

**Conferido:** comparação elemento a elemento do `.air` antes e depois: ticks de cada ação, início e duração do ativo
iguais em todas, menos 100 (15 para 16), 105 (ganhou 3 ticks antes da pose sem fim) e 170 (um desenho a mais de 6
ticks antes da pose final). A quantidade de elementos caiu nas ações das folhas novas (não há quadro do meio); os
`AnimElem` do `.cns` foram renumerados pelo gerador e disparam no mesmo tick. No `.cns`, fora isso, só mudaram 4
`sparkxy` (acompanham as caixas). `chars/gutto` e `chars/raiclaven` regerados com o mesmo md5.
`verificar_pengaro.py` sem erro (16 ações com aviso de Clsn1, 29 elementos, todos `[endiabrado]`). Robô na sandbox
rodado depois de regerar a versão final (13:22 a 13:24, md5 de air/cns/sff conferido depois): **146 PASS / 0 FAIL**.
Filme de 8 s na sandbox (Pengaró x Gutto: chute 230, rasteira 440, compasso, armada, caneta, bola) olhado em tiras.
Auditoria por contagem de cores dos sprites de toda ação < 10000: **só a 2000 (cena do Despertar, `despertar_a/b`)
ainda usa arte antiga na forma normal.**

**Mudou no jogo (precisa de olho de quem joga):** alcance da Clsn1: 230 de 58 para 62 (e a caixa 10 px mais alta);
1500/1501 de 47 para 60, agora na altura da barriga (continua golpe baixo na guarda); 1100/1101 de 63 para 73
(11100/11101 de 57 para 63); 1201 de 60 para 68; 3402 de 70 para 56; 760 de 39 para 37; 312, 333, 348, 3411, 3413,
3434 +2; 313, 3422, 3423 +1; 11500/11501 (pisão despertado) de 28 para 20. Correr tem ciclo de 16 ticks. A 440 volta a
ser o giro com as mãos no chão (era o chute rasteiro de guarda alta desde o dia 11).

**Não conferido:** role_b e golaco não apareceram no filme (o golaco pede barra); vitória, derrota, entrada e
provocação só nas folhas de contato, não em movimento; o Despertar por cima das folhas novas (o robô passa, ninguém
olhou a tela); alinhamento horizontal quadro a quadro (o tronco fica no eixo, então em poses inclinadas, como
compasso 4 e corrida, o pé de apoio pode andar alguns px entre desenhos); `gerar_hazaki.py` não foi rodado.

**Pendente:** redesenhar golaco 2 e vitoria 4 a 8 se quiser os desenhos próprios; `despertar_a/b` e as `e_*`; grupo E
do Lote 6 (opcional).

## 2026-11-11 (Lote 6, retoque 2): achados da revisão cética do Pengaró arcade

**Corrigido** (`ferramentas/retoques_arcade/lote6_retoque2.py` aplica os quatro retoques de PNG; rodar de novo não muda nada):

- **Caneta flutuava 4 px** (349, 1300, 1301): `caneta` 0, 1, 2, 6, 7 terminavam na linha 214/215; desceram para a 219.
  Medido no `.sff` final: base no chão em toda ação < 9000 fora os três quadros de voo da corrida (100.2, 100.3, 100.6).
- **Mancha lilás/roxa no rosto da guarda** (`defesa` 3, 18 pixels): viraram pele e contorno.
- **Cabelo nos vinhos da pele**: `compasso` 1 a 5 e `lata` 4 repintados (vinhos ligados ao cabelo dentro da caixa da
  cabeça viram o escuro 33,2C,20).
- **Garrafa trocando de lado no agarrão**: `agarrao` 4 e 5 (de costas) espelhados. O critério da casa fica um só:
  garrafa e caneleira do lado de trás da TELA também nas vistas de costas (como já era em armada 2/3 e bola 3).
- **bola 2** (dois braços saindo do ombro de trás): `REPETE_ARCADE[("bola", 2)] = 3`. A 1000/1001 arma direto com o
  braço no alto; a 1600/1601 segura o desenho 3 por 9 + 6 ticks. Ticks iguais.
- **Caixas do chute/pisão despertados** (`CAIXA_DESPERTADA`): o `e_chute_baixo` 3 também bate na barriga (perna em
  y -78..-60, pé em x 58); a justificativa "continua baixo" estava errada. 10230: `(12,-56,39,-42)` para
  `(20,-78,54,-58)`; 11500/11501: `(8,-37,20,-2)` (0 pixel do desenho dentro) para `(16,-78,52,-58)`. **Muda no jogo:**
  alcance do pisão despertado de 20 para 52 e do chute B despertado de 39 para 54. É a única diferença no `.air`; o
  `.cns` não mudou. `verificar_pengaro.py` deixou de avisar 11500/11501 (14 ações com aviso, 27 elementos).

**Recusado, com motivo:**

- Cabelo de `rolamento` 3: está no escuro certo; a contagem é baixa porque a cabeça está de ponta-cabeça e meio
  escondida. Soco (`soco/meio/03_5`, `03_6`): a "tonsura" clara é o brilho do topo da cabeça do modelo, igual na ginga 3
  e nos desenhos-chave soco 3, 4 e 5; não é defeito de quantização.
- Armada 1200 x 1201: a diferença é de projeto (`60 + 8 * i`, fraca e forte). O ajuste automático só encurta caixa; o
  1201 aparecia com 60 porque o desenho antigo o cortava.
- Caixas 11 a 12 px além do membro (302, 311, 343, 344, 3410, 3431, 303, 3412, 3435, 3402, 3100): dentro do teto da
  regra 8.3 (12 px); vêm de `SOBRA_MAXIMA_CLSN1`, porque a ação serve também à forma endiabrada.

**Mudanças de caixa do commit 15004fb que ficaram fora da tabela dele** (conferidas, sem defeito): 840 alcance 40 para
43 (o ajuste encurta menos com o desenho novo); 440 `(12,-22,78,-6)` para `(12,-18,78,-2)` e 10440 idem (saiu a ação
escrita à mão do `chute_agachado`; voltou a caixa da `sequencia`); 3100/13100 com larguras novas nos elementos do giro
(alcance máximo 90 igual); `[RemapPreset despertado]` de 772 para 494 linhas (menos sprites de quadro do meio).

**Pendente (só sai com desenho novo ou decisão de jogo):** `bola` 2 de verdade (lata erguida com o braço da FRENTE);
840 (agarrão agachado) usa o `agarrao` 2 em pé com a caixa na altura da coxa, falta um desenho de bote baixo (o
`agarrao` 7 serviria, não troquei); 800/830 com a caixa 17 px aquém do punho (alcance de agarrão, de projeto); 3100.3 e
3100.7 com a caixa de 100 px de altura sobre a rasteira agachada; avisos `[endiabrado]` do verificador (as `e_*`).

**Conferido:** robô na sandbox depois da versão final (13:47 a 13:50, md5 de air/cns/sff igual antes e depois):
**146 PASS / 0 FAIL**. Folhas de contato com caixa em `scratchpad/lote6/r2/` (C_caneta, C_agarrao_bola, C_desp,
C_compasso_defesa_lata; z_cab2 = cabeças a 8x). **Não conferido:** nada filmado nem visto em movimento neste retoque;
o robô não prova que o pisão despertado acerta com a caixa nova (não sei se há roteiro para 11500); `e_agarrao` 4/5 não
foram espelhados (não olhei a forma endiabrada); Gutto, Raiclaven e Hazaki não foram regerados (o diff só toca
`chars/pengaro`).

---

## 2026-11-11 (bosses, kit): plano de golpes, efeitos, aura e folhas da forma despertada dos cinco (branch `efeitos`)

O dono aprovou a forma despertada de cada lutador como boss final e pediu: "eu não quero nada estático, essas auras e
esses elementos vão ter que ter uma animação para dar movimento, e eu não quero um movimento todo duro, eu quero
fluidez". Cada boss tem, só dele, aura, efeitos, especiais e estilo de ataque.

**Feito (só documento, nenhum gerador nem `chars/` tocado):**
- [`docs/arcade/bosses_kit.md`](docs/arcade/bosses_kit.md): regra do dono; regra de fluidez com critérios
  verificáveis (corpo C1 a C8, efeito E1 a E12, os números do `aura_animada.md`); uma seção por lutador (Pengaró,
  Gutto, Raiclaven, Hazak, CK) com tabela de golpes, efeitos, dicionário de aura pronto para o `ferramentas/aura.py`,
  folhas que o kit pede e a fila não tem (com MOTION em inglês) e ordem de ligação no gerador; 44 decisões numeradas.
- `docs/regras-dos-lutadores.md`, seção 9: linha nova no checklist (aura e efeitos animados em camadas, nada
  estático, fluidez conferida em vídeo).
- Nomes de folha conferidos por script contra `fila_bosses.md` (branch `bosses`) e o Lote 7 da `fila.md` (branch
  `endiabrado`): 153 folhas pedidas fora das filas (66 de prioridade 1, 44 de fluidez, 43 só com proposta aprovada).

**Achados que mudam o plano:** o kit despertado do Gutto é o do Pengaró byte a byte (`gerar_gutto.py` importa
`pengaro_extra.py`); todo golpe próprio do Pengaró reaproveita folha da base; o `retocar()` do Raiclaven apaga a arte
desperta; a fila boss do CK usa prefixo `b_`, não `e_`; a regra 5.1 (exclusivos em 5000 a 5999) bate com os estados
de dano do motor.

**Não verificado:** nada do kit rodou em motor. Os dicionários de aura não foram executados; `mistura="soma"` e
`giro` de camada nunca foram à sandbox. Tempos e danos são calculados ou alvo, não medidos. `gerar_ck.py` não existia
na leitura.

**Pendente:** as 44 decisões (seção 8 do kit), a começar pela 1 (fluidez contra a regra 7), 2 (boss jogável ou chefe
de arcade), 4 (faixa de estados) e 6 (reações da aura no `aura.py`); gerar as folhas de prioridade 1; rebase da branch
`efeitos` sobre a `mugen` (14 commits atrás).

**Próximo:** ligar a aura num lutador de verdade (Pengaró, com a coluna e o anel por código enquanto as `fx_aura_*`
não chegam), filmar na sandbox e passar o `medir_aura.py`; depois os dados próprios do Gutto (`gutto_boss.py`).

---

## 2026-11-11 (método em .md)

- **Feito:** a pedido do Alisson, o jeito de trabalhar do Claude passou a ficar versionado: `docs/metodo-do-claude.md`
  (índice: frentes por branch, ciclo fila → fazer → sandbox → céticos → retoque, arte no ChatGPT, pipeline arcade,
  endiabrado = modo de Despertar com cara de boss final, aura animada e fluidez) e `docs/arcade/registro_fila.md`
  (procedimento da automação do ChatGPT e tabela das folhas, que estava só no rascunho da sessão).
- **Pendente:** as frentes `hazak`, `ck`, `endiabrado`, `bosses` e `efeitos` ainda não entraram na `mugen`; o teste da
  asa do Hazak no Blender não terminou (se aprovado, a seção 7 do método ganha o passo a passo).
- **Próximo:** ao fechar cada frente, copiar para o repo o que os agentes anotaram fora dele e atualizar o método.

## 2026-11-11 (Hazak, arte) — 67 folhas arcade do Hazak convertidas para `quadros_arcade` (branch `hazak`)

**Feito (só arquivos do Hazak; nada de `animar_folha.py`, `quantizar_folha.py` nem `gerar_pengaro.py` foi editado):**

- `ferramentas/folhas_hazak_arcade.py` (novo): corta as 8 figuras de cada `sprites/hazaki/quadros/folhas_arcade/*.png`
  (por célula, sem magenta), põe na escala, quantiza sem dithering com as funções do `quantizar_folha` e grava
  `sprites/hazaki/quadros_arcade/<folha>/00..07.png`. Tela 360x260, eixo (centro do tronco) em x=180, base em y=220,
  igual aos outros. `--medir` (tamanhos na folha crua) e `--contato DIR` (folhas de contato).
- Paleta: `sprites/hazaki/paleta_arcade.json`, as 15 cores da tabela (a) de `docs/arcade/hazaki.md` (contorno, pele 5,
  gi 3, debrum 2, faixa/cabelo, atadura 2, pulseira). A patroa tem `paleta_arcade_patroa.json`: as do Hazak sem a
  pulseira mais 4 próprias (cabelo castanho, mostarda, jeans, jeans sombra) = 18; com a paleta dele a camiseta virava pele.
- Escala única `109/344` (0,3169): a figura em pé tem 344 px na folha crua e sai com 109-110 px. Exceções (`FATOR`):
  `queda` 1,25-1,3; `vitima_arremessado` 1,2; `voadora` 1,12-1,25 nos quadros 1-6; `apanha` 5-7 1,08-1,12;
  `derrota_sirene` 0-1 1,15/1,1 (corpo deitado que veio menor); `obj_lasca` e `obj_estatueta` 0,5 (13-31 px);
  `patroa_*` 0,959 (100 px = 92% dele).
- Pulseira (`ferramentas/retoques_arcade/hazak_pulseira.py`, roda no fim da conversão): uma pulseira só por desenho
  (a duplicada e os pixels soltos viram sombra de atadura; duplicada de verdade em `agarrao_cutucao` 0, `ar_joelho` 7,
  `ar_soco` 6, `vitima_agarrado` 5) e pintada onde faltou, em 20 desenhos (tabela `PINTA`: parado 1 e 4,
  agarrao_perna 0 e 7, apanha 2 e 7, chute_giratorio 2, corrida 3 e 5, derrota_sirene 0 e 5, guarda_aco 2, rasteira 1,
  rasteira_arco 2, vitima_agarrado 1, vitima_arremessado 2 e 6, vitoria 1 e 2, defesa_baixa 2).

**Conferido:** 536 PNG em 67 pastas, todos 360x260, alfa só 0/255, só cores da paleta, base em y=220, nenhum cortado
na borda. Folhas de contato de todas as pastas olhadas uma vez (a 2x), e os desenhos retocados a 5x.

**Defeitos que ficaram / não conferido:**

- Pulseira com poucos pixels (5-7, não repintada): agarrao_perna 6, anda 1, apanha 6, ar_soco 5, chute_giratorio 4,
  giro_garagem 2 e 3, levanta 2. Sem pulseira: tapa_costas 2 (de costas, mãos escondidas). Não conferi desenho a desenho
  se a pulseira está no pulso CERTO nos 500 e poucos que já tinham uma; em `derrota_sirene` 4, 6 e 7 ela parece grande
  demais e no braço da frente.
- `chute_alto_rajada`: a faixa da cintura veio marrom-alaranjada na folha crua (nas outras é preta).
- `parado`: a respiração desce de 110 para 98 px (quadro 3), bastante para uma ginga; quem ligar no gerador escolhe os quadros.
- `guarda_aco` 2: a pulseira pintada ficou larga (braços cruzados, as duas ataduras formam uma mancha só).
- O eixo é o centro do tronco de cada figura: golpe que avança o corpo não avança no desenho (o gerador desloca, como
  o `DESLOCA_ARCADE` do Pengaró). Pé de apoio cravado entre quadros não foi medido.
- Nada rodado no jogo: nenhuma pasta está ligada no `gerar_hazaki.py` (é a outra parte da frente). Sem quadros do
  meio (`meio/`). O Despertar (`d_*`) não existe ainda: pendente, fora desta rodada.


## 2026-11-11 (Hazak, gerador) — gerador novo do Hazak, ficha inteira menos o Despertar (branch `hazak`)

**Feito (só arquivos do Hazak e o robô, de forma aditiva; `gerar_pengaro.py`, `repertorio.py`, `animar_folha.py` e
`quantizar_folha.py` não foram editados):**

- `ferramentas/gerar_hazaki.py` reescrito e `ferramentas/hazaki_golpes.py` novo (só dados, notação `"folha d/tA"`).
  Importa o `gerar_pengaro` como biblioteca e NÃO chama `montar_sprites/air/cns/cmd`. Lê
  `sprites/hazaki/quadros_arcade`. `--contato DIR` grava folhas de contato lidas de volta do `.sff`.
- `chars/hazaki` regerado: 16 normais, 4 correntes de 3 + finalizador, 4 kombos, 8 especiais (fraco/forte), 3 agarrões,
  2 supers, rolamento, afastar, parry, provocação, intro, vitória e derrota. Nome na tela **Hazak** (id `hazaki`).
  Vida 900, defesa 90, anda 3,4 / -2,8, corre 7,2. Paleta fixa: índices 1-15 do `.sff` = `paleta_arcade.json`
  (conferido lendo o `.sff` de volta: 0 sprites do corpo com cor fora das 15).
- **Furo "arremessado some" fechado:** os 28 grupos de `gp.SPRITES_VITIMA` existem no `.sff` do Hazak (preso =
  `vitima_agarrado` 1, curvado = `vitima_agarrado` 0, apanhando = `apanha` 2/3). Visto no filme: o Pengaró agarra
  (Martelo e Garrafada), bate, joga, e o Hazak aparece do começo ao fim.
- Robô: `testar_pengaro.py` ganhou os 21 comandos de toque do Hazak e passa `@LUTADOR@` ao `robo.lua`; no `robo.lua`
  os roteiros antigos só registram se o P1 não é o hazaki e há um bloco novo só para ele (41 roteiros). `corrente()`
  ganhou um 6º parâmetro opcional (janela, padrão 20). Para pengaro/gutto/raiclaven a lista continua com 43 roteiros
  (conferido carregando o Lua antes e depois).
- Docs: seção Hazaki do `README.md`, nota de estado no topo de `docs/arcade/hazak_gerador.md`.

**Testes (Windows Sandbox, depois da versão final dos arquivos):**

- `verificar_pengaro.py --hazaki`: 761 sprites, 162 ações, 90 estados, 42 comandos, 0 erros, 0 avisos.
- Robô `--lutador hazaki`: **151 PASS / 0 FAIL**, 41 roteiros. Danos medidos (P2 com defesa 90): correntes x 161,
  y 267, a 189, b 295; kombos 166 / 127 / 167 / 162; Cutucão Sacana 155; Puxa a Perna 111; Abraço 133; Punho de
  Concreto 67 / 78; Estatueta 78 / 89; Ascensão 89 / 122; Giro 72 / 94; Corte de Base 61 / 83; Pega Bolado 78 / 111;
  Guarda de Aço 67 (P1 sem dano); Faixa no Asfalto 268 (inteiro: 3001, 3002, 3003); Rapidinho 378 (4 passagens + voadora).
- Robô do Pengaró contra o Hazak novo: **146 PASS / 0 FAIL**, 43 roteiros (igual à linha de base).
- `chars/pengaro`, `chars/gutto`, `chars/raiclaven`: md5 de todos os arquivos igual ao de antes.
- Filmes de 8 s (Hazak x Pengaró: x, y, a, b, baixo+y, baixo+b, Punho de Concreto, Estatueta, Giro de Garagem) e de 6 s
  (Pengaró agarrando o Hazak), tiras olhadas. Folhas de contato dos sprites finais olhadas (8 de corpo, outros, efeitos).

**Consertos no caminho (com a medida):** o jab duplo era cancelado antes do 2º jab e a trava `var(11)` não contava o
2º acerto (finalizador x não saía: `FAIL foi para 303`); agora o 301 só continua depois do 2º jab e solta a trava no
2º HitDef. Efeitos do pixelfx crus viravam bloco branco e pontilhado: todos com mistura aditiva. A faísca saía ~27 px
acima do golpe (pivô do pixelfx embaixo): pivô no centro do clarão. Poeira do `ground-slam` pintada de cinza e cortada
de ~190 para 56 ticks. `rasteira` 3-5 e `rasteira_arco` 4-5 deslocadas 21-28 px (a conversão centrava pela caixa).

**Pendente / provisório / NÃO conferido:**

- **Despertar (Diabo Loiro) não existe:** sem folhas `d_*`. Sem comando, sem estado 2000, sem patroa, sem paleta `_d`
  (nem as 4 cores da patroa no `.sff`). Correntes/normais/especiais/super do Despertar da ficha: nada feito.
- Sem som (não há `.snd`): falas, sirene e bordão esperam o áudio do Breno.
- **Derrota com sirene:** escrita no `[Statedef -2]` (levanta e foge para fora da tela), NUNCA vista rodando: nenhum
  teste levou o Hazak ao nocaute nem ao fim do tempo. Intro, vitória, provocação, parry, rolamento, guard cancel,
  golpes no ar, golpe de afastar, coice, pulo, corrida e defesa também não foram vistos nem testados pelo robô.
- Escape dos agarrões (y/b nos 7 primeiros ticks): o robô não consegue conferir (preso, o P2 não roda o `-1` dele).
- Supers e agarrões do Hazak passaram no robô mas não foram filmados. Projétil da Estatueta: o robô mede o acerto,
  o voo não apareceu no recorte das tiras. Rapidinho no canto e contra oponente defendendo: não testado.
- Sem quadros do meio (8 desenhos por folha, abaixo dos mínimos da regra 7.1). Apanhar agachado usa a folha `agachado`.
  Lasca e estatueta saem das folhas `obj_` (provisório, a regra 8 pede pixelfx). A poeira aditiva lê como névoa clara
  no palco azul de teste. Retrato: o `sprites/hazaki-selecao-kof.png` antigo.
- Equilíbrio é chute meu: alcance curto compensado com passo à frente (cruzado, cotovelada, gancho, cotovelo), danos,
  hitstun e empurrão precisam de olho de quem joga. Punho de Concreto acerta o oponente que acabou de cair.
- `gerar_gutto`/`gerar_raiclaven` e os robôs deles não foram rodados (o `.cmd`/`.cns` deles não mudou; o boneco P2 mudou).
- O `hazaki=True` continua no `gerar_pengaro.py`/`repertorio.py` sem ninguém chamar: retirar quando a outra frente
  largar esses arquivos. `NOMES` do `gerar_layout.py` ainda diz "Hazaki".
- Conflitos ficha x regras e a saída adotada: seção 5 e nota de estado de `docs/arcade/hazak_gerador.md` (numeração do
  elenco em vez da 5.1; nomes repetidos da ficha; agarrão em pé H-; Rolada b com a folha `chute`).

## 2026-11-11 (Hazak, retoque) — conferência de dois céticos sobre o gerador novo (branch `hazak`)

**Corrigido (gerador, `hazaki_golpes.py`, retoques de arte; `gerar_pengaro.py` não foi editado):**

- **Derrota:** defeito de verdade achado no robô: o nocauteado ficava no `5110` para sempre (a ação `5170` terminava em
  `-1` e o `5110` do motor só passa ao `5150` com `AnimTime = 0`), então a fuga, que espera o `5150`, nunca começava.
  A `5170` agora termina. Segundo defeito, visto no filme: com o `ScreenBound` solto desde o começo da animação a câmera
  largava o caído e ele saía do quadro ainda deitado; agora a tela só solta quando ele começa a correr. O que o cético
  apontou (corre de costas) **não procede**: os desenhos 4 a 7 de `derrota_sirene` olham para trás; no filme ele levanta
  num pulo, vira de costas para o oponente e corre de frente para a saída.
- **Caixa de dano por desenho** (`caixas_do_corpo`): tronco + membro que sai dele 14 px ou mais, medidos no sprite, em
  vez de uma caixa por ação (parado, a caixa fica quase igual à antiga: -22..27 contra -24..24). Caixa de golpe alta (supers 3001/3002/3003, joelhada) encolhida até o membro (`caixa_no_membro`).
  Caixa dos agarrões 800/830 chega até a mão.
- **Pulo e golpes no ar:** desenhos centrados (os pés sobem 4 a 21 px; antes a cabeça descia 47 px com os pés presos);
  a caixa de golpe sobe junto.
- **Apanhar:** as ações 5001/5030/5035 dele usam a folha `apanha` (antes mostravam a pose de "preso" a cada golpe que
  o lançava). As vítimas dos agarrões dele passaram para as ações 5930/5931. `verificar_pengaro.py` ganhou a exceção
  por lutador `ACOES_VITIMA_DE` (aditiva).
- **Guarda de Aço x:** `reversal.attr = SA, NA, SA` (em pé e no ar; só o y pega golpe baixo). A resposta 1102/1103 ficou
  sem tremida (classe nova `contra`); os agarrões também (regra 8.3).
- **Rolada de Tatame:** travessia de verdade (9 px por tick enquanto rola, até ~126 px), não mais um `PosAdd` de um
  tick. Oponente a mais de ~90 px: a rolada acaba antes de passar. Invencível só enquanto rola (16 / 15 ticks).
- **Finalizadores:** Tá Achando Ruim? manda o oponente para o estado 304 (dois meios giros e a queda do motor); Machado
  de Dojô (333 e o fecho 3003 do super) com `fall.yvelocity = -7` (quique alto).
- **Efeitos da ficha:** rastro de velocidade de 2 ticks na corrida (`-2`), no Pega Bolado e nas passagens e na voadora
  do Rapidinho; poeira (`heavy-landing` cinza) no Giro e no Corte fortes, na arrancada e no pouso do Pega Bolado;
  cintilar dourado na Estatueta. O rastro da corrida nascia só no 8º tick (o `-2` vê o estado novo a partir do
  `Time = 1`): consertado depois de ver o filme sem rastro.
- **Estatueta:** o projétil sai do tamanho que tem na mão (~15 px, sem a base azul-marinho da folha `obj_`).
- **Alcance:** Giro de Garagem a 10,5 / 12,5 px por tick (~150 / ~200 px; a ficha pede meia tela); Pega Bolado b salta a
  9,5. **322** (chute alto) sem vai-e-volta: `0, 1, 6, 7`. 1º golpe das correntes y e b cancela em especial no contato
  (regra B.4). Movelist: `Parry` com `+`, corrida, passo para trás e golpes no ar.
- **`.sff`:** efeitos, retratos e estatueta só usam os índices 16-255 (0 pixels deles nos índices do corpo); desenhos
  vazios no fim dos efeitos cortados; `hit-flash` e `charge-up` (sem uso) saíram. 614 sprites.
- **Arte (pixel, reproduzível pelo `folhas_hazak_arcade.py`):** pulseira no pulso de trás em `vitima_agarrado` 0 e 1 e
  `agarrao_perna` 6; borrão verde-água do `guarda_aco` 2 virou tira; atadura branca no pulso do `soco_reto` 4 e 5;
  pontas da faixa do `chute_alto_rajada` 0-6 na cor da faixa (`retoques_arcade/hazak_faixa.py`, novo).

**Robô (aditivo, só no bloco do Hazak e no `.cmd` do Hazak):** `T_defende` (o P2 entra na guarda do motor quando vem
golpe e segura para trás) e 9 roteiros novos: corrente x contra defesa de verdade, Machado por cima contra defesa
agachada e em pé, Punho de Concreto contra defesa em pé e agachada, Pega Bolado defendido (1503), Guarda de Aço y e x
contra golpe baixo, derrota. Para pengaro/gutto/raiclaven a lista continua com 43 roteiros (conferido carregando o Lua).

**Testes (Windows Sandbox, depois da versão final; md5 de `chars/hazaki` igual antes e depois do robô):**

- `verificar_pengaro.py --hazaki`: 614 sprites, 162 ações, 91 estados, 42 comandos, 0 erros, 0 avisos.
- Robô `--lutador hazaki`: **176 PASS / 0 FAIL, 50 roteiros**. Danos iguais aos da rodada anterior. Defesa de verdade:
  corrente x defendida (P2 em 150/151, dano 0, `v10 = 0`, finalizador não saiu); 246 fura a defesa agachada (61) e é
  defendido em pé; lasca acerta quem defende em pé (67) e é defendida agachado (raspão 6); Pega Bolado b defendido
  pousa no 1503; Guarda de Aço y reverte o chute na canela (78, sem dano nele) e o x não (leva 24). Derrota: 5110 →
  5150, ação 171, correu para trás até sair da tela.
- Robô do Pengaró contra o Hazak novo: **146 PASS / 0 FAIL**, 43 roteiros (igual à linha de base). Uma rodada antes,
  com a caixa de membro também no punho da guarda (35 px à frente), a LATADA do Pengaró nascia dentro do Hazak e o
  roteiro 15 falhava ("projetil na tela"): por isso o limite de 14 px.
- `chars/pengaro`, `chars/gutto`, `chars/raiclaven`: sem mudança (`git status`). Robôs do Gutto e do Raiclaven não rodados.
- Filmes de 8 s e tiras em `scratchpad/hazak_gen/r2/` (`filme_derrota`, `filme_golpes`, `filme_especiais`); folhas de
  contato dos sprites finais na mesma pasta.

**Recusado (com motivo):** fuga de costas (acima); "bloco de pele" no `estatueta_arremesso` 3 (é o punho fechado);
kombos sem pose própria (a regra C diz que kombo é sequência de normais e não há folha para eles); rajadas dos supers
com congelamento 3,6 (é o padrão `super` da biblioteca, igual ao do Pengaró: 14+ só no golpe final); escala das pernas
estendidas (estilo); ginga com a cabeça oscilando 12 px (é a ginga).

**Pendente / NÃO conferido:**

- Despertar inteiro (sem folhas `d_*`), som próprio (sirene, falas), quadros do meio (regra 7.1).
- Arte que pede desenho novo: olhos que leem como óculos escuros em `chute_alto_rajada` 1/3, `ascensao` 4 e `voadora`
  4/5; pontas avermelhadas da faixa em `apanha` 1-6.
- Guarda de Aço contra golpe no ar: só por leitura (`SA`). Escape dos agarrões: o robô não consegue conferir.
- Não vistos nem testados: intro, vitória (só o começo aparece no filme da derrota), provocação, parry, rolamento,
  guard cancel, golpes no ar (as caixas mudaram de altura com o desenho centrado), afastar, coice, pulo, passo para trás.
- O giro do oponente no 304 roda (robô e filme), mas com a pose de ar do Pengaró o giro lê pouco. Poeira e asfalto
  continuam claros no palco azul de teste (mistura aditiva).
- A caixa de dano por desenho não foi vista no editor nem no combo-finder; equilíbrio continua estimativa.
- Os três filmes são de builds anteriores ao último ajuste: depois de `filme_derrota` e `filme_golpes` mudou o gatilho
  do rastro da corrida; depois de `filme_especiais` mudou só o limite de 14 px da caixa de dano (não aparece em filme).
  O robô e as folhas de contato são da versão final.

**Perguntas para o Breno:** (1) Guarda de Aço x deve pegar golpe no ar? (ficha só diz que o y pega baixo também);
(2) kombos com pose própria, e "Rasteira de Calçada" terminando em rasteira de verdade? (hoje fecha num chute lateral
em pé); (3) rajada de super com congelamento de 14+ por golpe (regra 8.3 literal) ou o padrão curto do elenco?;
(4) Rolada de Tatame com alcance limitado (~90 px) ou atravessa de qualquer distância como antes?; (5) Giro de Garagem
a ~150 / ~200 px está bom?; (6) a Estatueta do tamanho da mão (~15 px) ou maior nas duas?

## 2026-11-11 (hazak na mugen)

- **Feito:** a branch `hazak` (Hazak recriado pela ficha do Breno: gerador novo `gerar_hazaki.py` + `hazaki_golpes.py`,
  67 folhas em `quadros_arcade`, robô próprio) entrou na `mugen` com a aprovação do Alisson. Único conflito: este LOGBOOK
  (as duas pontas tinham anexado entradas; ficaram as duas). Os quatro lutadores foram regerados na árvore juntada e
  saíram com md5 idêntico ao que estava no git. Robô na sandbox, a partir da árvore juntada: Hazak **176 PASS / 0 FAIL**
  (50 roteiros), Pengaró **146 PASS / 0 FAIL** (43 roteiros).
- **Pendente:** Despertar do Hazak (Diabo Loiro: folhas `d_*` em geração na branch `bosses`), som próprio, retrato do
  Pengaró na barra de vida ainda antigo; robôs do Gutto e do Raiclaven não foram rodados contra o Hazak novo.
- **Próximo:** juntar `ck`, `endiabrado`, `bosses` e `efeitos` conforme cada frente fechar e for conferida.

## 2026-11-11 (aura pelo Blender vira padrão)

- **Feito:** teste da asa do Hazak (Diabo Loiro) animada no Blender a partir do conceito aprovado: asa com ossos batendo
  em laço de 48 quadros, notas caindo, ouro pingando, coroa e brasa, em camadas de 15 cores. O Alisson viu o vídeo e
  aprovou o método como padrão das auras. Scripts em `ferramentas/aura_blender/`, passo a passo em
  `docs/arcade/aura_blender.md`, seção 7 de `docs/metodo-do-claude.md` atualizada.
- **Pendente:** o teste foi vídeo montado fora do jogo, comparado só com o desenho parado (a folha de 8 quadros do
  ChatGPT não existia); falta ligar no motor pelo `ferramentas/aura.py` (branch `efeitos`) e fazer o rig das outras
  quatro auras. Os scripts ainda têm caminhos e medidas da asa do Hazak escritos à mão (não são genéricos).
- **Próximo:** generalizar os scripts e aplicar em Gutto, Raiclaven, CK e Pengaró quando o uso do plano permitir
  (semana em 64% no Fable às 15h; a regra é parar em 80%).

## 2026-11-11 (PARADA GERAL às 16h: onde cada frente ficou)

O Alisson pediu para parar todos os trabalhos para trocar o modelo de raciocínio do Claude. Nada está rodando. Cada
frente tem, no LOGBOOK da própria branch, uma entrada "PARADA de propósito" com o que foi feito e como retomar.
**Nenhuma dessas branches foi conferida pelo orquestrador nem entrou na `mugen`.**

| Branch | Ponta | Estado | Falta |
|---|---|---|---|
| `mugen` | esta | Pengaró normal inteiro em arte arcade (robô 146/0); Hazak novo sem o Despertar (176/0); método em `docs/metodo-do-claude.md` | nada pendente de parada |
| `ck` | `e28e79f` | CK montado (`gerar_ck.py`, `chars/ck`), 4 folhas do Ratão refeitas; relato de robô 159/0 | céticos, retoque, conferir filme, juntar |
| `endiabrado` | `0d304cc` (bom: `90e5575`) | Pengaró endiabrado boss final: 34 folhas geradas, convertidas e ligadas; a ponta guarda trabalho pela metade, não testado | terminar a ligação, céticos, retoque, robô, juntar |
| `bosses` | `f380d59` | conceitos dos 4 bosses, fila completa, 16 folhas brutas do Diabo Loiro (Hazak) | resto do Hazak; Gutto, Raiclaven e CK inteiros; converter e ligar |
| `efeitos` | `9a64d4f` (bom: `3c0b205`) | kit dos bosses (`docs/arcade/bosses_kit.md`), `ferramentas/aura.py` com lutador de teste, cético feito; a ponta guarda o retoque pela metade | terminar o retoque, refilmar, juntar |
| `auras` | `40bc95f` (bom: `3e1c429`) | auras pelo Blender dos cinco (camadas em `sprites/<id>/aura/`), cético feito; a ponta guarda os 4 retoques pela metade | terminar retoques e fecho, ligar no jogo pelo `aura.py` |
| `cenarios` | `b7ce776` | `gerar_cenario.py` provado com cenário de teste, pesquisa e projeto dos 4 cenários de Nazaré, 9 imagens brutas do Cristo | responder "Para o Alisson confirmar", resto da arte, montar, filmar |

- **Ordem sugerida para retomar:** (1) `ck`: rodar céticos e retoque e juntar; (2) `endiabrado`: voltar a `90e5575`,
  olhar o que a ponta mudou, terminar e conferir; (3) `efeitos` + `auras`: terminar retoques e ligar uma aura no jogo
  (começar pela asa do Hazak); (4) `bosses`: seguir a fila; (5) `cenarios`: depois das respostas do Alisson.
- **Na máquina:** a trava da sandbox (`%USERPROFILE%/JogoDeLuta/sandbox.trava`) foi removida depois de confirmar que
  não havia sandbox aberta. Cada branch tem um worktree em `C:/Dev/Jogo-de-Luta-<branch>`.
- **Uso do plano na parada:** perto de 65-70% da semana no Fable; a regra atual é parar só em 100%.


## 2026-11-11 (CK) — folhas revisadas e convertidas para a arte arcade (branch `ck`, itens 2 e 3 do pedido do Breno)

**Feito:**

- `quantizar_folha.py`: papéis `PAPEIS_CK` (base) e `PAPEIS_CK_RATAO`; `FORMA=ratao` troca a paleta para
  `paleta_arcade_ratao.json`. `conferir_arte.py`: rampa da pele do CK (sombra 2-10°, médio 11-19°, luz 20-30°) e a sombra
  fria da regra 4 é `branco_sombra`. `animar_folha.py`: `FOLHAS_CK`, escala 0.195 (a figura ocupa a célula inteira da
  folha), `AJUSTE` por folha, sempre por célula, e `fundo_ck` (fundo com degradê vira magenta puro; figuras vizinhas
  grudadas são separadas no ponto fino). O CK **não** entrou em `LIMPA_MAGENTA`: o `sem_magenta` apagaria o roxo do boné
  e da camisa; o magenta sai antes de quantizar.
- `sprites/ck/paleta_arcade.json` e `paleta_arcade_ratao.json` (15 cores cada, medidas nas duas referências).
- `ferramentas/converter_ck.py` converte tudo de uma vez (leva ~15 min): 58 pastas em `sprites/ck/quadros_arcade/`
  (8 desenhos cada, tela 360x260, base y=219, sem quadro do meio) e os efeitos em `sprites/ck/efeitos/` (aura, fumaca,
  garrafa, paredao com 8 quadros; bone e juliet com 1, tirados das folhas do golpe; despertar_fumaca com 4).
  `--contato DIR` gera folhas de contato e `--medir` as medidas. Retoques por código em
  `ferramentas/retoques_arcade/ck.py` (rodar o converter refaz todos).
- Altura em pé: base 113 px, Ratão 109-110 px (ele fica curvado). Queda e levantada têm escala por quadro
  (`ESCALA_QUADRO` e `AJUSTE["queda"]`): o corpo deitado veio com ~65 px na folha e ficou com ~97-100.

**Retoques por código:** `e_derrota` 8 = cópia do 7 (o 8 da folha encosta na borda); `e_agarrao` 7 = cópia do 8 (a
garrafa trocava de mão); faísca amarela fora do `e_queda` 1, 5 e 6; boné, óculos e garrafa no ar fora do corpo
(`bone_voador` 6, `e_juliet_voadora` 6, `e_bola` 6); **fiapo de fumaça e cigarro fora de todas as folhas `e_`** (com
1-2 px ele virava um rabisco azul-escuro em cima da cabeça por causa do contorno de 1 px).

**Defeitos que ficaram (número do quadro como na folha, 1 a 8):**

- `queda` 5 e 6: as figuras se sobrepõem na folha; o 5 saiu sem os pés e a ponta do tênis dele ficou colada atrás da
  cabeça do 6. Usar 4 -> 7 ou refazer a folha com mais espaço.
- Garrafa na outra mão (o braço que sai do ombro da esquerda da imagem segura a garrafa e a mão vazia fica à direita):
  `e_soco` 2 a 7, `e_caneta` 3 a 5; parecido em `e_martelo` 2 a 6 e `e_ar_soco` 2 a 6 (vi só na folha de contato
  reduzida). No `e_rolamento` 7 ele está de costas e a garrafa aparece à esquerda. Não dá para resolver por código.
- As 4 já marcadas para refazer (`e_provoca`, `e_beck`, `e_golaco`, `e_juliet_voadora`) foram convertidas como estão;
  o `e_golaco` tem riscos de giro e estilhaço desenhados junto com o corpo.
- `lata` 5 (manchas escuras na polo) e 6 (clarão vermelho no ombro de trás); `provoca` 2, 3 e 6 e `golaco` 4 (risquinhos
  e luva solta desenhados); `rolamento` 2 e 3 (mancha rosa atrás do joelho); `e_vitoria` 3 sem a fumacinha (agora
  nenhuma folha `e_` tem).
- `despertar_a` 7-8 e `despertar_b` 1-2: a fumaça sai lilás na paleta do corpo (ela não tem cinza-esverdeado). Os
  mesmos 4 quadros estão com as cores certas em `efeitos/despertar_fumaca/`.
- `e_derrota`: sentado ele fica com ~50-60 px de altura (o base tem ~66).

**conferir_arte.py (58 pastas, 464 quadros):** R1, R5 e R7 passam em todos. R3 e R4 falham só nos quadros sem pele ou
sem branco (fumaça do Despertar, `afastar` 2). R10 falha em 55 pastas e R11 em 13: são do desenho (punho que cresce no
contato, antecipação), não da conversão.

**Não feito / a seguir:** quadros do meio (`animar_folha.py --arcade` + `quantizar_folha.py --meio` funcionam para o
CK, testado no `soco` e apagado); `gerar_ck.py` (item 4); refazer no ChatGPT as 4 folhas do item 1 e, se o Breno quiser,
`queda`, `e_soco` e `e_caneta`. Nada foi testado no motor: só folha de contato e script.

## 2026-11-11 (CK) — lutador montado no jogo: `gerar_ck.py`, `chars/ck`, robô e filme (branch `ck`, item 4 do pedido)

**Feito.** `ferramentas/gerar_ck.py` (no molde do `gerar_raiclaven.py`, mas só sobre o `gerar_pengaro.py`, no modo "só
desenhos") gera `chars/ck` com a ficha inteira. O kit é o do Pengaró (mesmos números de estado e nomes de comando, que
é o que o robô testa); a arte, os movimentos dos comandos e os golpes são do CK.

- **Arte:** as 58 pastas de `sprites/ck/quadros_arcade` e os efeitos de `sprites/ck/efeitos`, sem quadro do meio. O
  conversor centra cada figura na célula; nas folhas de golpe o gerador ancora o calcanhar de trás onde ele fica na
  guarda (`ANCORA`), senão o corpo escorregava até 17 px para trás ao bater e o punho ia só 34 px à frente.
- **Caixas de golpe medidas no desenho** (`caixa()`): o pedaço do corpo que passa de 24 px à frente do eixo, com 4 px
  de sobra. Os golpes só do Ratão e as variantes despertadas dos normais (`gp.CAIXA_DESPERTADA`) são medidos no
  desenho do Ratão (a chinelada alta bate na cabeça, o chute da base na barriga).
- **Braço curto:** o soco do CK vai uns 40 px à frente (o do Pengaró, 70). Para as correntes encaixarem, cada golpe
  entra com um passo (`com_passo`, avanço de 2 a 6,5 px por tick até a caixa + passo chegar a 80 px) e os normais do
  kit ganham um passo de até 3 ticks antes do contato (`NORMAIS_DO_KIT`, alvo 52 px).
- **Comandos da ficha:** Tragada `↓ →` x/y, Boné Voador `→ ←` x/y, Levanta, Comédia `→ ↓` x/y, Bote `↓ →` a/b, Bicuda
  Baixa `↓ ←` a/b, Gingado de Esquiva `← →` a/b, Contragolpe `↓ ←` x/y, Pêndulo `← ↓` a/b, Saideira `← →` y, Rajada
  `← → ↓` a/b, Nocaute `← → ↓` x/y. Ratão: Garrafa Voadora `↓ →` x/y, Tragada de Beck `↓ ↑` x/y, óculos `→ ←` x/y,
  Passinho Ratão `→ ←` a/b, Grave do Paredão `↓ ↑` a/b, Baile `← → ↓` x+y (e o comando da Rajada, que no Ratão vira o
  Baile). Kombo 4 é x, y, ↓ + y; kombo do Ratão é x, → + y, b.
- **Estados com lógica própria** (o resto é o CNS do kit): Tragada (1000/1001, nuvem que anda pouco, para e fica 150 a
  180 ticks; quem encosta leva 25 e fica 45 ticks tonto; o pod aparece na luva), Boné Voador (1600/1601, projétil
  que freia, volta e some na cabeça; ele fica sem boné esperando e põe de volta na ação 1602), Contragolpe (1300/1301
  com `ReversalDef` e o cruzado 1310), Pêndulo (1100/1101 com `NotHitBy SA` e saída no direto 1110), Rajada da
  Esquina (3000: 7 socos de 22 e a voadora de 70), Tragada de Beck (3400), Garrafa Voadora (3402: arco, estilhaça e
  deixa cacos 120 ticks), Grave do Paredão (3403), corte descendo no ar (3436).
- **Modo Ratão:** `despertar_a`/`despertar_b` com os 4 quadros de `efeitos/despertar_fumaca` no lugar dos de fumaça
  lilás; `RemapPreset` para as folhas `e_`; **aura = `fx_aura` num Explod à parte** (ação 9210, atrás do corpo, presa
  ao lutador) e PalFX esverdeado leve. Jeito chapado: nos estados 3410 a 3435 o alcance (0 a 5 px) e o tempo do
  contato (0 a 2 ticks) são sorteados; corte de garrafa sangra 3 de vida a cada 15 ticks por 90 ticks (não mata).
  Perde o Contragolpe e a esquiva do Pêndulo liga 3 ticks depois.
- **Paredão (`fx_paredao`, ação 9250):** atrás dele na entrada do round (some quando o round começa), no Despertar,
  no Baile da Esquina e no Grave.
- **Textos:** 8 falas de vitória, `movelist.dat` (o óculos aparece como "Óculos Voador": sem nome de marca em texto do
  jogo). Retrato: `sprites/ck-selecao-kof.png`, o busto do desenho 0 da `referencia_ginga` em resolução cheia.
- **Instalação e robô (só linhas novas):** `'ck'` na lista do `ferramentas/Jogo de Luta.bat`; `robo.lua` recebe o
  `--lutador` (`@LUTADOR@`) e, com `ck`, troca o kombo 4 e o kombo do Despertar e roda 5 roteiros a mais (Baile pelo
  comando próprio, Contragolpe sem apanhar e apanhando, Pêndulo e saída no direto).
- **Vítima dos agarrões:** as ações 5001 e 5030 usam os sprites 382, 384-386 e 49, que já estão em
  `gp.SPRITES_VITIMA` (os mesmos números do Gutto e do Raiclaven); o `main` confere.

**Testado (só na sandbox):**

- Robô `testar_pengaro.py --lutador ck`: **159 PASS / 0 FAIL** em 48 roteiros (1ª rodada: 158/1, a nuvem fraca nascia
  em cima de quem estava a 70 px e acertava no mesmo tick; passou a nascer junto da boca e parar a ~55 px).
- Robô do Pengaró depois das mudanças no `robo.lua`: 146 PASS / 0 FAIL em 43 roteiros, igual ao registrado antes.
- `chars/gutto`, `hazaki`, `pengaro` e `raiclaven`: md5 igual antes e depois (`85cb5631…`).
- Dois filmes CPU x CPU de 10 s contra o Pengaró (`filmar_sandbox.py`, o segundo com `--despertar 1`), olhados em
  tiras de 16 quadros a 3 por segundo e em 4 recortes em resolução cheia: ele aparece, com retrato na HUD, pés na
  linha do chão com sombra, sem pixel magenta ou verde, golpes legíveis; no Despertar o paredão fica atrás dele, a
  fumaça cobre o corpo, ele sai de Ratão com a garrafa e a aura verde sobe dos pés como efeito à parte; log do motor
  sem erro (só os avisos de `buffer time` que todos têm). Os vídeos não estão no repositório.

**Provisório (funciona, mas não é o que a ficha pede no fim):**

- **Folhas emprestadas** (não há desenho próprio): Pêndulo = `rolamento` 1-2; ganchos da corrente y e do Gingado b =
  `golaco` 3 e 5; joelhada = `chute_alto` 2; chute alto de rua = `afastar` 4; Voadora da Esquina e fim da Rajada =
  `bicicleta` (desenho de ar, no chão parece agachado); cotovelada e chute duplo no ar = `ar_soco` e `bicicleta`;
  pisão = `afastar` 5; tapa de luva = `compasso` 4; Saideira = `agarrao` + `martelo` + `chute_baixo`; Bicuda Baixa =
  `rasteirinha`; Grave = `chute_baixo`; apanhando agachado = `agachado`. No Ratão (`E_FOLHA`): `afastar` ->
  `e_chute_alto`, `baixo_soco` -> `e_agachado` (o soco agachado não aparece), `rasteirinha` -> `e_rasteira`,
  `bicicleta` -> `e_ar_soco`, `compasso` e `armada` -> `e_martelo`, `lata` -> `e_provoca`.
- **`↓ ↑` + botão:** o ↑ faz pular. A entrada aceita o pré-pulo e os 7 primeiros ticks do pulo e o golpe volta para o
  chão. O robô entra por `AssertCommand`, então **ninguém apertou isso na mão**. Se ficar ruim, a saída é `↓ ↓` como
  no Pengaró (muda a ficha: decisão do Breno).
- Tragada de Beck não segue o oponente (nuvem grande e lenta, reta). Garrafa Voadora tem uma versão só (x e y iguais)
  e os cacos nascem num ponto fixo (a 206 px), só se a garrafa não acertou antes.
- Nocaute de Rua é o super de 3 golpes do kit com os desenhos do CK e invencível no preparo: sem esquiva, câmera
  lenta nem o oponente rodando. Levanta, Comédia forte ficou invencível até o fim do ativo, sem a recuperação longa.
- Boné Voador: ele fica parado, sem boné, até o boné voltar (36 ticks no x, 59 no y).
- Golpes das correntes e kombos que valem nas duas formas (301 a 347) têm a caixa medida no desenho da base; no Ratão
  os chutes com `e_chute_alto` batem mais alto que a caixa.
- Faíscas: os desenhos do Pengaró repintados (branco na base, verde de vidro no Ratão). A ressaca depois do Despertar
  é a do kit (a ficha não fala dela). O tropeço que vira golpe baixo não foi feito.
- O gancho do Gingado b não acerta no roteiro do robô (dano 0), igual ao chute do Rolê do Pengaró no mesmo roteiro:
  é do kit e ninguém investigou.

**Não verificado:** `select.def` (não existe no repositório; quem registra é o `.bat`, que não foi rodado); o
`verificar_pengaro.py` (só conhece Pengaró e Hazaki); caixas no editor e combos no ikemen-combo-finder; treino dos dois
lados; som (desligado na sandbox); entrada do round e vitória em movimento (o filme começa com o round aberto).

**Tamanho:** em pé ele mede 113 px (Pengaró 110 na ginga, Gutto 114, Raiclaven 119), mas tem 47 px de largura contra
77 a 90 dos outros: no filme ele parece pequeno ao lado do Pengaró. É a escala 0,195 do `converter_ck.py`; mudar é
reconverter as folhas (15 min) e rodar o gerador.

**A seguir:** o Breno olhar o filme e decidir o tamanho e o `↓ ↑`; refazer as 4 folhas `e_` do item 1 e a `queda`;
pedir as folhas que faltam (Pêndulo, ganchos, joelhada, Voadora, Saideira) e trocar as emprestadas; juntar a `ck` na
`mugen` (quem junta é o orquestrador: `robo.lua`, `testar_pengaro.py` e o `.bat` têm só linhas novas).

## 2026-11-11 (CK) — item 1 do pedido: 4 folhas do Ratão refeitas no ChatGPT, mais 3 extras (branch `ck`)

**Feito** (chat novo "CK — arcade", `e_referencia_ginga.png` anexada; a `queda` com a `referencia_ginga.png`):

| Folha | Estado | Tentativas | O que ficou |
|---|---|---|---|
| `e_provoca` | aprovada | 1 | garrafa na mão mais à direita nos 8; o dedo é da mão vazia; sem risquinhos de efeito |
| `e_beck` | aprovada | 1 | garrafa visível nos 8 (antes sumia no 4 e ia para a mão de trás no 5-6); pose de soprar, sem fumaça |
| `e_golaco` | aprovada | 1 | uma garrafa só, nunca atrás da cabeça, sem cacos nem riscos de giro, nunca de costas |
| `e_juliet_voadora` | aprovada | 2 | óculos sai da mão vazia e fica solto no ar no quadro 6; sem óculos na cabeça do 3 ao 8 |
| `e_soco` (extra) | com ressalva | 2 | no quadro 5 a garrafa ainda fica na mão de trás: no conversor o 5 é cópia do 4 (`COPIA` em `retoques_arcade/ck.py`) |
| `e_caneta` (extra) | aprovada | 1 | garrafa à frente nos 8 (antes ia para trás nos quadros 3 a 5) |
| `queda` (extra, base) | aprovada com ressalva | 1 | 8 figuras separadas e inteiras (antes a 5 e a 6 se sobrepunham); deitado de joelhos dobrados, 70 px de comprido contra 96 do `levanta` |

- As 7 foram convertidas com `converter_ck.py` (mesma paleta). `AJUSTE` no `animar_folha.py`: `e_beck` saiu (a folha nova
  veio no tamanho da referência), `queda` 1.45 -> 1.20, novos `e_caneta` 1.25, `e_soco` 1.14, `e_juliet_voadora` 1.06;
  `e_golaco` continua 1.18. Em pé: 109-114 px nas seis do Ratão. `efeitos/juliet` agora tem 11x4 (era 16x6).
- `gerar_ck.py`: a queda usa os desenhos 4-5-6 e 6-7 (os mesmos e os mesmos tempos do Pengaró), agora que o 5 e o 6
  existem inteiros. `chars/ck` regenerado (o `.cns` muda porque avanço e posição da faísca são medidos no desenho).
- `folhas_ck.py`: os pedidos usados estão gravados (MOTION novo das 7; a regra da garrafa e a medida em px entram no fim
  de todo pedido do Ratão).

**Conferido:**
- Com os olhos: as 9 imagens geradas em tira de 1800 px (quadro a quadro, de que lado está a garrafa) e os 56 quadros
  convertidos em tira 2x. Não olhei em movimento: nenhum filme novo.
- Script: 8 corpos separados por folha (componentes ligados), borda 100% magenta, 2172x724; `conferir_arte.py` R1, R3,
  R4, R5 e R7 passam nos 56 quadros (R10/R11 falham como nas outras folhas: são regras do desenho).
- Robô `testar_pengaro.py --lutador ck` na sandbox: **159 PASS / 0 FAIL**, igual a antes.
- `chars/gutto`, `hazaki`, `pengaro`, `raiclaven`: md5 igual antes e depois (`85cb5631…`).

**Ficou / a seguir:**
- `e_soco` 5 (cópia do 4), `e_martelo` 7 e `e_ar_soco` 2-6 (garrafa do lado de dentro; não refiz, só vi na folha de
  contato), `e_rolamento` 7 (de costas). Os outros defeitos da entrada de conversão continuam (lata 5-6, provoca 2-3-6,
  golaco 4, rolamento 2-3).
- No Ratão os ganchos da corrente y e do Gingado b continuam emprestando `e_golaco` 3 e 5, que agora são a rasteira
  deslizando e o agachado (antes: rasteira e giro de costas). Continua provisório.
- O registro do procedimento do ChatGPT desta rodada está no `registro_fila.md` do scratchpad da sessão (não está no
  repositório); o que importa dele está em `folhas_ck.py`.

## 2026-11-11 (ck: frente PARADA de propósito às 16h)

O Alisson pediu para parar os trabalhos para trocar o modelo de raciocínio do Claude. O CK está montado no jogo
(`gerar_ck.py`, `chars/ck`, pipeline arcade das 62 folhas, as 4 folhas do Ratão refeitas e o lutador regenerado; o
agente relatou robô 159 PASS / 0 FAIL na sandbox). Os dois céticos (regras e olhos) estavam rodando e foram
interrompidos; o retoque final não rodou. Árvore limpa, tudo enviado. Falta: a conferência cética, o retoque, o
orquestrador olhar o filme, e juntar na `mugen`.

## 2026-11-11 (CK) — retoque final depois dos dois céticos (branch `ck`)

Os dois céticos (regras e olhos) rodaram sobre o `e28e79f`. O que era defeito de verdade foi consertado no
`gerar_ck.py` (nada editado à mão em `chars/ck`); o que precisa de desenho novo ficou anotado.

**Consertado (causa):**
- **Aura do Ratão**: era o desenho inteiro (coluna de fumaça + um monte no chão), opaco e preso ao lutador: virava um
  arbusto em que ele pisava e que subia junto no pulo. Agora entra só a coluna (sem as 22 linhas do monte, base
  desfeita em xadrez), translúcida (`trans = addalpha`, `alpha = 216, 100`), um pouco maior (1,5 x 1,25).
- **Baile da Esquina não encerra mais o Ratão**: o kit zerava `var(20)` no 1º tick do 3100 (regra do Pengaró) e a aura
  sumia no próprio super. No CK o bloco `Fim Despertar` sai; a ficha só diz "1 estoque, só no Despertar".
- **`← → ↓ + a/b` no Ratão volta a ser a Rajada da Esquina** (a entrada do kit que levava ao Baile saiu); o Baile é
  só `← → ↓ + x+y`.
- **Rajada, Baile e Nocaute no Ratão não piscam mais entre em pé e deitado**: a folha `golaco` (ganchos) passava para
  a `e_golaco` desenho a desenho, e na `e_golaco` refeita o 3 é a rasteira deslizando e o 5-6 o agachado. Agora os
  ganchos do Ratão usam só as estocadas em pé da `e_golaco` (1, 2, 4, 7). Isso também conserta o gancho da corrente
  y (311, 312) e o do Gingado b (1701). O soco agachado do Ratão (400) usa o agachado e a estocada rente ao chão
  (`e_golaco` 5 e 3) no lugar da `e_agachado` parada.
- **Caixas do Ratão**: as correntes e os kombos da base (301-347, que saem também no Ratão) e o 1701 ganharam a
  variante `1xxxx` com a caixa medida no desenho do Ratão (antes: caixa da base, com 0 pixels do desenho dentro no
  323, 341, 331, 345). 3000 e 3200 no Ratão: caixa das estocadas.
- **Caixas da base**: Bote (1400/1401) era do boné ao chão, agora só a faixa do braço; Rajada (3000) e Nocaute (3200)
  de 60 para 40 px de altura (ombro ao fígado).
- **Pixels soltos acima da cabeça no Ratão**: toda ilha de até 12 px sai na leitura do quadro `e_`.
- **Tragada**: a fraca para a uns 70 px (era 55 e não alcançava a meia distância), a forte a uns 175 px (era 117).
  Cada projétil trava só a si mesmo: a nuvem no ar não impede mais o Boné Voador, nem o contrário.
- **Boné Voador forte** atravessa a tela (pico a ~307 px; era 177). O CK fica preso no estado até o boné voltar (92
  ticks).
- **Encosta na Parede** (`← + x, y, → + b`): do 344 não sai mais o Gingado b (`← → b` é o mesmo movimento).
- **Agarrão em pé**: o dano de 100 sai em três socos (30, 30, 40 nos ticks 4, 9 e 14). A animação é a mesma.
- Rótulos do Pengaró no `.cmd` (Chuva de Bebidas, Mao de Sombra...) trocados pelos nomes do CK (só comentário).
- `robo.lua`: 5 roteiros novos só do CK (Baile não encerra o Ratão; Rajada no Ratão; Encosta com `role_b` junto;
  Tragada no ar não trava o Boné; agarrão em 3 socos) e uma linha mudada: o roteiro comum do 3100 aperta `baile`
  quando o lutador é o CK.

**Não era defeito (conferido com os olhos, zoom 4x-5x):**
- "`e_beck` com duas garrafas": os sprites 947/948 são da `e_bola` (Garrafa Voadora): a segunda garrafa é a que ele
  arremessa. A `e_beck` tem uma garrafa só nos 8. A Tragada não existe no Ratão (ação 11000 nunca toca).
- "Tênis vermelho na rasteira e no levanta": é a luva. Na `rasteira` ele apoia a mão no chão (braço, faixa branca do
  punho, luva); no `levanta` são as mãos no chão do kip-up.

**Conferido:**
- Robô na sandbox, depois da última geração: **CK 175 PASS / 0 FAIL** (53 roteiros), **Pengaró 146 PASS / 0 FAIL**.
- md5 de `chars/gutto|hazaki|pengaro|raiclaven` igual antes e depois (`d72661c2…` no conjunto).
- Com os olhos: folhas de ação com caixa (base e Ratão) de 311, 312, 313, 323, 331, 332, 333, 340-347, 301-303, 321,
  400, 1701, 3000, 3100, 3200, 1400, 9210; dois filmes de 10 s na sandbox (CK x Pengaró parado, golpes por roteiro, a
  barra mantida em 1 estoque por um Lua só do filme), olhados em tira de 12 em 12 quadros: Tragada forte chega longe e
  acerta, Bote, Rajada; Despertar com paredão e fumaça, aura translúcida em volta das pernas (esverdeada sobre o
  paredão, puxa para o azul-esverdeado sobre o cenário azul), aura ligada durante e depois do Baile, Rajada no Ratão
  toda em pé, gancho do Gingado. Log do motor sem erro.

**Não verificado:** Boné forte atravessando a tela (na tira o boné não aparece nítido); Nocaute de Rua no filme (não
saiu: o Lua do filme só garante 1 estoque); o agarrão em movimento; comandos por direcional de verdade (o robô aperta
por `AssertCommand`); som; entrada do round e vitória em movimento; caixas no editor; treino dos dois lados.
`conferir_arte.py` e `verificar_pengaro.py` não foram rodados.

**Ficou (precisa de desenho novo ou de decisão do Breno):**
- Folhas emprestadas no Ratão continuam: Voadora/fim da Rajada (`bicicleta` -> `e_ar_soco`), Tapa/Contragolpe
  (`compasso`, `armada` -> `e_martelo`), `lata` -> `e_provoca`, `bone_voador` -> `e_juliet_voadora`; ganchos e soco
  agachado agora são estocadas da `e_golaco`. Faltam as folhas `e_` próprias (ganchos, joelhada, voadora, Pêndulo).
- `queda`: deitado de joelhos dobrados mede 69 px contra 113 em pé e 96 no `levanta` 1: precisa de folha com o corpo
  esticado (aumentar a escala engordaria os 4 primeiros desenhos).
- Assopro na Cara (3433): a caixa é a fumaça na frente da boca, mas não há desenho de fumaça nesse golpe.
- `e_soco` 5 cópia do 4; `e_martelo` 7 e `e_ar_soco` 2-6 com a garrafa do lado de dentro; 260 quadro 7 (perna
  estendida 10 ticks na recuperação).
- Clarão do golpe final dos supers no Ratão: sai como um bloco creme-esverdeado de borda reta (é o `quadro_flash` do
  kit sobre a `sombra_forte` do Pengaró, que tem o desenho cortado na borda; no CK a cor clara deixa o corte mais
  visível). Visto no filme do Despertar. É do gerador comum: não mexi.
- Flash azul/branco do Despertar e poeira laranja (9214) são as cores do kit.
- Decisões: tamanho/largura do CK (0,195 no `converter_ck.py`); a Tragada "tonteia" só como atordoamento longo (não há
  estado de tonto no kit); Tragada de Beck que segue, tropeço do Ratão, cacos em ponto fixo e Nocaute de Rua (fora da
  ficha); agarrão que sai com `→/← + b` colado e rouba o Pisão de Rua de perto (kit); alcance curto dos normais; o Baile
  continua batendo sem o bônus de 45% do Ratão, como no kit (436 de dano no robô; com o bônus ia a 631); Boné forte deixa o CK 1,5 s parado.


## 2026-11-11 (ck: PARADA às 17h20, o Alisson precisou desligar o notebook)

Parada rápida. Último commit antes desta entrada: `e28e79f7`. Arquivos alterados sem commit na hora da parada: 7 (guardados neste commit; **não testados**, se houver). Falta o que a entrada anterior desta branch lista; a etapa em andamento (retoque ou conferência) foi interrompida.

## 2026-11-11: Endiabrado vira boss final, lote preparado (branch `endiabrado`)

- O dono aprovou o conceito do Pengaró Endiabrado como boss final: `sprites/pengaro/quadros/folhas_arcade/e_conceito.png`
  (frente sem aura, costas, frente com aura, rosto).
- `docs/arcade/fila.md` ganhou o **Lote 7**: prompt base do boss, prompt base da aura e 34 folhas com MOTION, em três
  grupos (A 12, B 12, C 10): 30 `e_<golpe>` (uma para cada folha que o gerador usa, incluindo `e_ginga`, `e_anda` e a
  `e_lata` que não existia), `e_despertar` e três `fx_aura_*` (coluna, anel, detritos) em fundo verde.
- Textos atualizados para o modelo novo: `docs/como-trabalhar.md`, `docs/fichas/pengaro.md`, `docs/arcade/pengaro.md`,
  `docs/biblia-de-arte.md`. A linha da tabela de auras em `regras-dos-lutadores.md` não mudou.
- **Nada foi gerado nem ligado no jogo**: o gerador não foi tocado e o jogo continua com a arte antiga do endiabrado.
- Pendente: gerar o grupo A começando por `e_ginga` e medir se o recorte de magenta come o violeta (se comer, passar as
  `e_` para fundo verde); definir a paleta do boss; decidir se `e_despertar` substitui só `despertar_b`; ligar as
  `fx_aura_*` por `Explod`; `e_defesa`, `e_chute_baixo` e `e_rasteira` não têm folha normal aprovada nesta branch para
  servir de referência de pose.

## 2026-11-11 — Endiabrado, Lote 7 grupo A gerado (12 folhas `e_`)

- Geradas no ChatGPT (chat "Pengaró — arcade") e salvas em `sprites/pengaro/quadros/folhas_arcade/`: `e_ginga`, `e_anda`,
  `e_soco`, `e_chute_alto`, `e_martelo`, `e_afastar`, `e_apanha`, `e_queda`, `e_levanta`, `e_defesa`, `e_agachado`, `e_pulo`.
  Cada pedido levou `e_conceito.png` + a folha normal do golpe. As 12 passam em `tira_fundo` + `fatias(…, 8)` de
  `recortar_quadros.py` (8 quadros separados). Conferidas a olho em tiras de contato; nada rodou no jogo nem em sandbox.
- Com ressalva: `e_queda` ficou ~13% menor que a normal (deitado 251 px contra 290; existe
  `ferramentas/retoques_arcade/queda_escala.py` para esse caso) e com as pernas levantadas nos quadros 4-7; `e_defesa` veio em
  2143x734; `e_anda` repete os quadros 1-4 em 5-8 como a normal (as pernas não alternam); `e_agachado` é agachado nos 8
  quadros, como a `agachado.png` normal (o MOTION da fila pedia descer da ginga: corrigir o texto da fila se for mantido assim).
- Fundo magenta: o recorte não fura o corpo (rachaduras do peito, forro e chifres ficam), mas come a beirada das brasas da
  barra da calça: ~3% da área da figura apagada contra ~2,2% nas folhas normais. Dá para seguir em magenta.
- Escala das `e_` varia entre folhas (em pé com cabelo de 297 a 313 px; `e_pulo` ~15-20% maior que a normal); o gerador já
  tem fator de escala por folha para o endiabrado.
- Pendente: grupos B e C do Lote 7; ligar as `e_` no gerador (`ARCADE`, pasta `e_ginga` x `ginga_endiabrada`); paleta do boss.

## 2026-11-11 — Endiabrado, Lote 7 grupo B gerado (12 folhas `e_`)

- Geradas no mesmo chat e salvas em `sprites/pengaro/quadros/folhas_arcade/`: `e_chute_baixo`, `e_baixo_soco`, `e_cabecada`,
  `e_rasteirinha`, `e_rasteira`, `e_ar_soco`, `e_bicicleta`, `e_bola`, `e_compasso`, `e_armada`, `e_caneta`, `e_rolamento`.
  Cada pedido levou `e_conceito.png` + a folha normal do golpe (para `chute_baixo` e `rasteira`, as refeitas do Lote 6). Todas
  em 2172x724, 8 quadros separados em `tira_fundo` + `fatias(…, 8)`. Conferidas a olho em tiras de contato ao lado da normal;
  nada rodou no gerador, no jogo nem em sandbox.
- Com ressalva: `e_caneta` ficou ~9% menor que as outras `e_` (em pé 277 px com cabelo, contra ~305) e com a perna da
  rasteira encurtada: foi o jeito de caber 8 quadros separados (a `caneta.png` normal tem os quadros 6-7 encostados);
  `e_cabecada` tem a algema do pulso da frente pouco legível nos quadros 1-3 e as rachaduras do peito puxando para o rosa.
- Escala: em pé com cabelo 292-310 px; folhas agachadas/aéreas saíram na medida da normal + cabelo depois de dar a medida em
  px no pedido (`e_baixo_soco` e `e_cabecada` precisaram de uma correção "85% do tamanho").
- Pendente: grupo C do Lote 7 (7 `e_` + 3 `fx_aura_*`); ligar as `e_` no gerador; paleta do boss.

## 2026-11-11 — Endiabrado, Lote 7 grupo C gerado (7 folhas `e_` + 3 `fx_aura_*`): lote completo

- Geradas no mesmo chat ("Pengaró — arcade"). Em `sprites/pengaro/quadros/folhas_arcade/`: `e_agarrao`, `e_golaco`, `e_lata`
  (folha nova), `e_provoca`, `e_vitoria`, `e_derrota`, `e_despertar`. Em `sprites/pengaro/quadros/folhas/` (fundo verde, de
  onde `efeitos_folha.py` lê): `fx_aura_coluna`, `fx_aura_anel`, `fx_aura_detritos`. Todas 2172x724. As `e_` dão 8 quadros em
  `tira_fundo` + `fatias(…, 8)`; as `fx_` dão 8 células em `efeitos_folha.recortar` e nenhum bloco cruza a divisão em oitavos.
  Conferidas a olho em tiras de contato; nada rodou no gerador, no jogo nem em sandbox.
- MOTION reescrito no pedido (o de `docs/arcade/fila.md` não descrevia a folha normal; fila.md NÃO foi editado):
  `e_golaco` (quadros 1-4 seguem o gole/limpar a boca da normal, de punho vazio), `e_lata`, `e_provoca`, `e_vitoria` (quadro 8
  de frente com o braço da frente estendido, como a normal, e não de braços cruzados) e `e_derrota` (cai sentado e reclama
  sentado de pernas esticadas, como a normal, e não ajoelhado socando o chão). `e_agarrao` bateu com a normal sem mudança.
- `e_despertar` (substitui `despertar_b`, 8 quadros): 1 Pengaró normal de mãos vazias com a mão no peito, 2 cai de quatro,
  3 calça escurece e mancha violeta nas costas, 4 casaco + algemas + braceletes, 5 ajoelhado de cabeça para trás com cabelo
  comprido e rachaduras, 6 num joelho só com a corda e os chifres, 7 em pé, 8 guarda do boss. Sem coluna, anel nem pedras.
  O `despertar_b` antigo é em pé o tempo todo; este ajoelha (é o MOTION do Lote 7). Dono ainda precisa confirmar.
- Ressalvas: `e_vitoria` ficou ~7% menor que as outras `e_` (em pé 287 px com cabelo; a 1ª veio 13% maior e a correção
  passou do ponto): fator ~1,07 na ligação. `e_golaco` tem as rachaduras do peito bem acesas (tronco quase todo violeta nos
  quadros 5-8). `fx_aura_detritos`: as peças PAIRAM (sobem ~14 px e voltam) em vez de subir e reentrar por baixo, para o
  laço fechar; pedras marrom-rosadas (pedido era cinza-marrom); furos dos elos com resto de verde escuro. `fx_aura_coluna`:
  a altura da coluna pulsa (478 a 568 px), base fixa em y=639; ~2% de pixels esverdeados dentro da fumaça. `fx_aura_anel`:
  saiu um disco de chão rachado com borda escura (225x80 px), não um anel vazado; a posição dentro da célula varia até 7 px.
- Lote 7 inteiro em disco (31 `e_` + 3 `fx_aura_*`). Pendente: ligar tudo no gerador (`ARCADE`, `e_ginga` x
  `ginga_endiabrada`, `e_despertar` no lugar de `despertar_b`, Explod das três camadas da aura, escala por folha), refazer
  `e_queda`, paleta do boss, e testar no sandbox.

## 2026-11-11 (endiabrado: frente PARADA de propósito às 16h)

O Alisson pediu para parar os trabalhos para trocar o modelo de raciocínio do Claude. Pengaró endiabrado boss final: as 34 folhas do Lote 7 foram geradas e convertidas e o boss foi ligado no jogo (aura em três Explod); a etapa 'converter e ligar' ainda estava rodando (mexendo em gerar_pengaro.py, na aura de detritos e no .sff) e os dois céticos e o retoque NÃO rodaram. Falta: conferir no filme da sandbox, rodar o robô depois do último estado, juntar na mugen.
Último commit feito por um agente que terminou a etapa dele: `90e5575`. O commit seguinte a esta entrada guarda o que estava
pela metade na hora da parada (**não testado, pode estar quebrado**); para voltar ao estado bom, use `90e5575`.

## 2026-11-11 (endiabrado: retomada depois da parada, estado `0d304cc` conferido na sandbox)

- O commit "INTERROMPIDO" (`0d304cc`) deixou de ser suspeito: rodei os quatro geradores (pengaro, gutto, raiclaven, hazaki)
  em cima dele e `git status` ficou limpo (o `chars/pengaro` commitado é o que o gerador produz); `chars/gutto`,
  `chars/raiclaven` e `chars/hazaki` são idênticos aos da `origin/mugen` (`git diff` vazio). A `mugen` (`e1f9dc1`) já está
  dentro da branch.
- O que o `0d304cc` mudou em relação ao `90e5575`: coluna da aura achatada (escala 1,1 x 0,68: ~1,25 vez a altura do boss,
  não entra mais na barra de vida), detritos espalhados para os lados no `lote7_converter.py` (ficavam em cima das pernas) e
  `e_despertar` do quadro 5 em diante só na paleta do boss (a pele saía laranja e trocava de cor ao entrar na ginga).
- Sandbox, tudo neste estado: robô do Pengaró **146 passaram, 0 falharam** (43 roteiros, igual ao de antes); paleta 2 da
  seleção (soco forte + Enter) pelo `robo/paleta.lua` rodado via `sandbox.py`: `var20=600 var37=1` nos ticks 30 e 700
  (começa endiabrado e fica). Dois filmes: Despertar (10 s) e boss batendo (13 s, Despertar no tick 0).
- Visto com os olhos nas tiras dos filmes: cena 2000 (garrafa quebra, cai de quatro, casaco, levanta) sem pulo de tamanho;
  roupa do conceito em todos os golpes que apareceram (socos, chutes em pé e agachado, afastar, compasso, armada, caneta);
  aura à parte em três camadas (disco no chão, coluna atrás, pedras e elos na frente), pés no chão, nenhum quadro magenta
  ou verde. Ressalvas vistas: a pele do boss no jogo está mais vermelho-vinho do que o marrom-arroxeado do conceito; os
  elos e pedras da frente passam por cima do braço/pernas do boss e às vezes do rosto do oponente; o primeiro quadro de
  `e_despertar` (Pengaró normal desenhado na folha do boss) tem a pele mais alaranjada que a `despertar_a` que vem antes.
- Ainda na arte antiga: a primeira metade da cena (`despertar_a`, 8 quadros, forma normal). Sem folha própria do boss (usam
  pose emprestada das folhas `e_`): corre (de `e_anda`), recuo (de `e_pulo`/`e_defesa`), `juliet0-3`, `mortal0-11`,
  `parado1-5`, `q_anda0-7`, `q_parado0-7`, `anda1-3`.
- Não verificado: os especiais do fim da lista do filme (Sombra, Rolê, bola, agarrão, Golaço) não couberam nos 13 s e não
  foram vistos em movimento na roupa nova (o robô passa por eles, mas robô não olha arte); queda/levanta/derrota/vitória do
  boss só vistos na folha de contato dos quadros convertidos, não no jogo; `e_queda` continua a folha com defeito (menor
  e de pernas levantadas nos quadros 4-7, compensada só por escala).
- Próximo: o dono olhar os filmes e decidir (tom da pele, detritos na frente, `e_despertar` no lugar de `despertar_b`);
  refazer `e_queda`; céticos + retoque; juntar na `mugen` (quem junta é o orquestrador).

## 2026-11-11 (endiabrado: PARADA de propósito às 16h50)

O Alisson pediu de novo para ir parando. A etapa "converter e ligar" terminou (entrada acima: estado conferido na
sandbox, robô 146/0, dois filmes). Os dois céticos estavam rodando e foram interrompidos; o retoque final não rodou.
Árvore limpa. Falta: céticos (modelo e jogo), retoque, o orquestrador olhar os filmes, e juntar na `mugen`.

## 2026-11-11 (endiabrado: PARADA às 17h20, o Alisson precisou desligar o notebook)

Parada rápida. Último commit antes desta entrada: `f3e86b1c`. Arquivos alterados sem commit na hora da parada: 0 (guardados neste commit; **não testados**, se houver). Falta o que a entrada anterior desta branch lista; a etapa em andamento (retoque ou conferência) foi interrompida.

## 2026-11-11 (notebook leve: sandbox na Iris Xe, pesados em Idle nos núcleos E)

- **Feito:** `ferramentas/leve.py` e regra "Notebook leve" na seção 1 de `docs/metodo-do-claude.md`, combinada com a
  sessão de edição de vídeo. `sandbox.py` agora liga a vGPU e o jogo desenha pelo Mesa d3d12 na Iris Xe (`dxil.dll` do
  mesmo pacote mesa-dist-win 26.2.6 copiado para `%USERPROFILE%/JogoDeLuta/ferramentas_sandbox/mesa`); processos da
  sandbox no host em Idle e núcleos E; dentro dela, motor em 2 vCPUs e `LP_NUM_THREADS=2`. Medido: carga acima do fundo
  de +40/+37 para +18/+10 pontos (P/E) na mesma luta. Robô Pengaró 146/0 com GPU; filme de 5 s (sem GPU) conferido.
- **Pendente:** filmar com GPU (gdigrab grava preto; tentar ddagrab); a VM recusa afinidade pelo host (talvez com
  administrador, não testado); aplicar `leve.aliviar` nos scripts de Blender da branch `auras`.

## 2026-11-11 (CK: conserto do que sobrou dos céticos, branch `ck`)

- **Feito (código):** `gerar_ck.py` voltou a rodar (o Lote 7 do Pengaró fazia o gerador comum ler `e_despertar`,
  `colar_boss`, `POSE_BOSS`, `REPETE_ARCADE` e as folhas `corre`/`recuo`; o CK desliga tudo isso e sai igual ao de
  antes, menos a derrota, que agora mostra os 8 desenhos). Aura do Ratão: `addalpha 128,192` (o fundo aparece) e
  `ModifyExplod` com `postype = p1` e `pos y = -Pos Y` a cada tick: no pulo fica no chão e segue só no x (visto no
  filme; sem o `postype` o motor ignorava o `pos` e a aura subia). Fim da Rajada no Ratão (13000) com o chute alto em
  pé da `e_chute_alto` 3-7 e caixa no pé. Tragada de Beck com nuvem 1004 e trava só nela. Rótulos do 831 e do `.cmd`.
- **Feito (retoque por script):** tênis do pé de apoio da `rasteira` 1-5 repintado de vermelho para o tênis
  (`retoques_arcade/ck.py`, também ligado no `converter_ck`, que não foi rodado). Sobram 1-2 px de laranja no 1 e no 4.
- **Não era defeito:** as "duas garrafas" são da `e_bola` 2-3 (não da `e_beck`): ele puxa uma segunda garrafa e a joga
  na Garrafa Voadora (3402), a dele fica no quadril. O vermelho no chão do `levanta` são as luvas (mãos no chão).
- **Visto:** robô CK 175/0 e Pengaró 146/0; filmes CPU x CPU, `--despertar 1` e um roteiro com Rajada e Tragada de Beck
  no Ratão (tiras olhadas). Camadas animadas da aura do CK existem na branch `auras` (`sprites/ck/aura/aura.json`:
  paredão, anéis, névoa): não ligadas, é outra frente.
- **Pendente (pede desenho):** fumaça do Assopro no 3433; soco agachado do Ratão com antecipação (860≡861); queda
  esticada (393-396); folhas `e_` próprias de ganchos, voadora, lata, boné e Tapa/Contragolpe; `e_soco` 5; agarrão com
  três socos; risco na testa do 989/957/965. **Pendente (código, decisão do Breno):** Tragada que tonteia (R4), alcance
  dos normais (O10), `→/← + b` colado roubando o Pisão (R9). **Achado novo:** o clarão do 1º tick das faíscas fortes
  do Ratão (verde-claro, `quadro_flash`) cobre o oponente como um bloco com borda reta (filme, quadros 238 e 565): é o
  "clarão creme dos supers" já pendente, mais visível no Ratão.
- **Próximo:** o orquestrador juntar `ck` na `mugen`; o Breno decidir R4/O10/R9 e o clarão.

## 2026-11-11 (aura pelo Blender: peças comuns)

- **Feito:** os scripts do teste da asa viraram `ferramentas/aura_blender/comum.py` (peças comuns), `hazak_asas.py`
  (a asa reescrita em cima do comum) e `aura_modelo.py` (molde de aura nova); os quatro scripts antigos saíram. A asa
  foi rodada de novo e comparada com a do teste aprovado: recortes, chão, coroa e partículas idênticos; asas com ~13
  pixels diferentes por quadro (pesos em precisão dupla), sem diferença visível na tira. Camadas finais em
  `sprites/hazaki/aura/` (288 PNG + `aura.json`). O conceito `d_conceito.png` do Hazak foi copiado da branch `bosses`
  para o mesmo caminho, para o script rodar daqui. `docs/arcade/aura_blender.md` tem os 10 passos de uma aura nova.
- **Pendente:** ligar no motor (ninguém viu isto dentro do jogo); auras do Gutto, Raiclaven, CK e Pengaró; caminho de
  aura fria (sem ouro/fogo) só foi escrito, não testado com conceito de verdade.
- **Próximo:** uma aura por lutador copiando o molde.

## 2026-11-11 — Aura do Gutto: garanhão de raio vermelho (método do Blender)

- **Feito:** `ferramentas/aura_blender/gutto_aura.py` + `sprites/gutto/aura/` (432 PNG 360x200 + `aura.json`). Cinco
  camadas: `crateras` (96 q), `garanhao` (48 q, malha de 3536 vértices e 22 ossos: dorso, pescoço, cabeça, queixo,
  duas patas de 3 juntas, três cadeias de crina de 4), `raios` (96 q, zigue-zague que sai das juntas, pisca e se
  refaz), `ferraduras` (96 q) e `vapor` (96 q, a única À FRENTE do corpo). Sem redução: escala 112/450 do conceito.
  Novidade em relação à asa: pesos por FAMÍLIA de osso (`pesos_por_familia`, no script), para a borda de uma pata não
  ser puxada pela outra. Conceito `e_conceito.png` copiado da branch `bosses` para o mesmo caminho.
- **Medido:** nenhum pixel parado em nenhuma camada, nenhum par de quadros igual, emenda do garanhão 6,68 contra
  6,64/6,57 das vizinhas, passo máximo 3,0 px (casco de cima), 15 cores.
- **Pendente:** ligar no motor (nada foi visto no jogo). O vapor sai da narina da pose parada: em golpe/pulo tem de
  seguir a cabeça ou desligar. Ferraduras estão 1,4x o conceito (com 11 px viravam anel ilegível).

## 2026-11-11 — Aura do CK: paredão de som de fumaça (método do Blender)

- **Feito:** `ferramentas/aura_blender/ck_aura.py` + `sprites/ck/aura/` (384 PNG 360x200 + `aura.json`). Cinco camadas,
  todas atrás do corpo: `paredao` (48 q, malha de ~9 mil vértices; 7 colunas de 5 ossos em chicote + 1 osso por cone
  animado em ESCALA = deformação radial; tranco do objeto a cada batida), `aneis` (96 q), `nevoa` (96 q), `cacos`
  (48 q, 15 recortes do conceito pulando no grave) e `fagulhas` (96 q, folhinhas laranja). Compasso de 4 tempos em 48
  quadros (150 bpm a 2 tiques), 1º tempo no quadro 3 para a emenda cair fora do golpe. Sem redução: escala 112/569.
- **Remendo declarado:** os rabos/anéis parados do conceito saíram da textura (cones refeitos pela simetria radial,
  braços laterais cortados) e o miolo atrás do corpo são caixas dos lados copiadas (4 grandes + 1 pequena). Contraste
  dos cones (aro escuro, miolo claro) pintado na textura; no golpe o miolo acende e corre uma onda clara.
- **Medido:** 15 cores; pixels parados 147 de 21,6 mil no paredão (0,7%, dentro dos cones) e 0 nas outras; nenhum par
  de quadros igual; emenda do paredão 2,25 contra 2,50/1,99 das vizinhas; passo máximo 1,66 px (juntas) e 2,06 px
  (raio do cone); aura 217x160 px para um corpo de 60x112.
- **Pendente:** ligar no motor (nada visto no jogo; vídeo não assistido, só tiras). Tampinhas pouco legíveis em 1x;
  névoa da mesma cor da base da parede; sobra um toco reto na borda direita da parede.

## 2026-11-11 — Aura do Pengaró: coluna de fumaça violeta-preta (método do Blender)

- **Feito:** `ferramentas/aura_blender/pengaro_aura.py` + `sprites/pengaro/aura/` (480 PNG 360x200 + `aura.json`). Seis
  camadas, na ordem de desenho: `coluna` (48 q, malha com espinha de 8 ossos em onda S que sobe + 2 ramos de base;
  depois do render o miolo é reamostrado de baixo para cima em duas fases = a textura sobe 1 px por quadro),
  `chicotes` (48 q, 6 malhas com cadeia de 3 a 6 ossos, raiz com sobra por cima da coluna), `anel_tras` (96 q, chão
  desprojetado para vista de cima e girado no Blender como disco deitado, meia volta por laço, rachaduras pulsando,
  bolhas de sombra em órbita), `fiapos` (96 q, línguas que se soltam do topo + faíscas lilás), `soltos` (96 q, 15
  pedras em placa e 4 elos com 3 ossos, cada um na sua órbita) e `anel_frente` (96 q, À FRENTE do corpo, da linha da
  sola para baixo). Sem redução: escala 112/488, a aura cabe inteira.
- **Remendo declarado:** a coluna atrás do corpo é fumaça clonada de cima da cabeça (fica atrás dele); o topo da
  coluna encostava na borda da folha e foi recortado em línguas; o disco do chão é a metade da frente do desenho
  copiada em meia volta (simetria para o laço fechar em 96 quadros).
- **Medido:** 15 cores; pixels parados 0 em cinco camadas e 4 de ~2,5 mil nos chicotes; nenhum par de quadros igual;
  emenda da coluna 3,06 contra 3,04/3,13 das vizinhas (chicotes 0,99 contra 0,92/1,03); passo máximo 1,92 px
  (juntas), 1 px (fluxo), 2,88 px (borda do anel); aura 192x180 px para um corpo de 99x108.
- **Armadilha achada:** `bl_renderiza` só esconde os objetos das passadas dele. Objeto de outra passada (o disco, as
  pedras) tem de ser escondido antes, senão sai em todas e a emenda de 48 quadros pula.
- **Pendente:** ligar no motor (nada visto no jogo; vídeo não assistido, só tiras). O chão em 1x lê como disco violeta
  riscado com faíscas brancas, não como lajes rachadas; elos pequenos (2 px de espessura); base da coluna carregada.

## 2026-11-11 — Aura do Raiclaven: leque de lâminas de aço (branch `auras`)

- **Feito:** `ferramentas/aura_blender/raiclaven_aura.py` + 480 PNG e `aura.json` em `sprites/raiclaven/aura/` (5 camadas
  de 96 quadros a 2 tiques, todas atrás do corpo: `leque`, `foices`, `raios`, `lascas`, `limalha`). Conceito copiado
  da branch `bosses` para `sprites/raiclaven/quadros/folhas_arcade/e_conceito.png`.
- **Como:** o leque do conceito é uma massa encavalada que não gira em laço. Recortei 7 peças inteiras (2 tesouras,
  adaga, pente, faca, navalha, foice), pus cada uma de pé e remontei em anéis REGULARES: 24 peças de fora (6 tipos x 4,
  +90° por laço), 24 pontas atrás (+45°), 10 foices (-180°). O quadro 96 cai igual ao 0 porque o anel andou um número
  inteiro de casas; a fase de cada peça usa ciclos não inteiros (m = k - w*d/n) para a onda fechar junto com o giro.
  Tesoura = duas metades rígidas no parafuso (a de baixo é o espelho da lâmina + a argola do desenho). O lilás do
  conceito foi tirado (aço cinza frio). Raios, brilho em espiral e limalha são Python em 1x.
- **Medido:** 15 cores; pixels parados 0 nas 5 camadas; nenhum par de quadros igual; emenda do leque 11,28 contra
  11,35/11,22 das vizinhas; passo máximo 2,11 px (anel de fora), 2,93 px (foices), 1,18 px (lascas); leque 182x183 px
  para um corpo de 94x130 (112 do cabelo à sola).
- **Pendente:** ligar no motor (nada visto no jogo; vídeo não assistido, só tiras). O leque virou círculo de raio 392 px
  do conceito (lá ele tem 925 de largura por ~785 de altura e é aberto embaixo). Duas cores da paleta são quase iguais
  (o contorno pintado nos recortes entrou no k-médias). O quadro 52 quase não tem raio.

## 2026-11-11 (auras: frente PARADA de propósito às 16h)

O Alisson pediu para parar os trabalhos para trocar o modelo de raciocínio do Claude. Auras pelo Blender: base comum (comum.py), asa do Hazak e as auras de Gutto, Raiclaven, CK e Pengaró foram feitas (camadas em sprites/<id>/aura/) e o cético conferiu; os quatro retoques estavam no meio (os quatro *_aura.py alterados, sem render novo). Falta: terminar os retoques, o fecho no docs/arcade/aura_blender.md, ligar no jogo pelo aura.py da branch efeitos.
Último commit feito por um agente que terminou a etapa dele: `3e1c429`. O commit seguinte a esta entrada guarda o que estava
pela metade na hora da parada (**não testado, pode estar quebrado**); para voltar ao estado bom, use `3e1c429`.

## 2026-11-11 (auras: retoque do Gutto terminado)

O gutto_aura.py que estava pela metade no commit da parada rodou inteiro sem erro e foi renderizado de novo. Defeitos do
cético consertados pela causa: raios refeitos (20 raios em 3 portes, finos, ramificados, crescendo da raiz e sumindo na
ponta, nascimentos escalonados: 5 a 9 vivos e 714 a 1786 px por quadro, nunca "nada"); buraco sem o corpo virou rabo de
raio com 3 ossos (r1-r3) que afina até o chão; vapor sombreado com contorno e penacho maior; crateras redesenhadas como
cova elíptica com lascas; topo dos raios em y>=7; carmesim menos rosa (azul limitado a verde+45). Pendente: ligar no jogo;
vídeo não assistido; o vapor continua ancorado na narina da pose parada; ferraduras seguem 1,4x.

## 2026-11-11 — Aura do CK, retoque (defeitos do cético)
- **Feito:** rodei o `ck_aura.py` que tinha ficado pela metade na parada (recortes, rig, chicote, compor, instala) e
  publiquei `sprites/ck/aura/` (384 PNG + `aura.json`). Clarão chapado da batida: o miolo do cone virou meia-bola com
  luz e sombra e só o lado da luz clareia no golpe (olhei quadros 2 a 5 em zoom: sem disco liso). Parede mais viva:
  amplitude das colunas maior (0,55° embaixo a 11° na ponta), cada pilha estica e achata no grave, tremor mais forte.
  Cones limpos trocando só o que passava por cima por outro pedaço do mesmo cone (a pincelada fica). Caixas do miolo
  espelhadas e com o cone girado (não são mais cópia direta). Anel no fim da vida encolhe por gomo em vez de virar
  lasca. Tampinhas e cacos maiores, 46 fagulhas, névoa com contorno.
- **Medido:** paredão com 7 pixels parados (antes 147; a nota anterior "dentro dos cones" nunca foi confirmada),
  silhueta muda 2,5% por quadro (antes 2,0%; asa 12,2%, mas a parede é bloco e a asa é pena fina), cintilação 5,4%
  (antes 4,5%; asa 4,3%), passo máximo 2,56 px. `cacos` tem 6 pixels parados. 15 cores, alfa 0/255.
- **Pendente:** toco reto de fumaça na borda direita (braço cortado) continua; nada visto dentro do jogo nem o vídeo
  assistido.

## 2026-11-11 (aura do Pengaró: retoque do cético)

- **Feito:** rodado e conferido o retoque que tinha ficado pela metade no `40bc95f` (`pengaro_aura.py` não mudou desde
  então). A subida da coluna em duas fases (que deixava retângulos e barra reta no miolo e trocava o desenho de uma vez)
  saiu; no lugar, `escorre` desliza o render 4x por ondas lisas antes da redução, e clarões violeta sobem em fitas pela
  rampa só do violeta. O violeta vivo que a chave de magenta comia voltou (`brilho_comido`), o topo virou lobos
  desiguais, as mechas soltas saíram do recorte (os fiapos fazem o papel), pedras e elos cresceram (1,35x / 1,5x), o
  espigão da pedra06 saiu, o chão é o desenho de frente com lajes arfando e luz correndo pelas rachaduras.
- **Medidas:** coluna muda no máximo 31,6% dos pixels por quadro (era 50%), emenda 2,13 entre vizinhas 2,16/2,21;
  480 PNG 360x200, alfa 0/255, 15 cores. Poucos pixels fixos por camada (57 coluna, 24 chicotes, 81 anel_tras, 31 anel_frente).
- **Pendente:** o chão em 1x ainda lê mais como riscos horizontais claros do que como lajes; o remendo atrás do corpo
  aparece entre as pernas como mancha violeta lisa. Nada visto no jogo.

## 2026-11-11 — Aura do Raiclaven, retoque do cético (branch `auras`)

- **Feito:** o retoque que estava pela metade em `40bc95f` (raiclaven_aura.py) rodou inteiro sem erro e foi re-renderizado.
  A forma voltou à do conceito: leque duplo (duas asas de 9 lâminas + adaga do meio), aberto embaixo, coração de 12
  foices, moldura de raio branco com clarão azul-gelo (não é mais arame de 1 px), roseta de pontas atrás do corpo
  (remendo: sem corpo não há vão nem tocos). Nada gira em roda: cada asa abre e fecha em cascata (fase cresce de cima
  para baixo, 17,7 → 33,3 quadros), lâminas estocam em onda, tesouras cortam. Paleta sem cores repetidas (menor
  distância 27). Miolo do leque muda 57,8% por quadro e a silhueta 11,9% (asa: 55% e 12,3%). Raios não tocam y=0 (y_min 1).
- **Pendente:** passo máximo das lâminas da frente 3,14 px (pouco acima de ~3); 236 px de lâmina ainda no vão de baixo
  (pontas das asas descendo ao lado das pernas); vídeo não assistido; nada visto no jogo.

## 2026-11-11 (auras pelo Blender: frente fechada)

- **Feito:** as cinco auras do Despertar estão em camadas pelo método do Blender (conceito aprovado como textura,
  ossos em cascata, efeitos em Python por cima), 2 tiques por quadro, pé em (180,190). Tabela com script, camadas,
  quadros, tamanho e pendências em `docs/arcade/aura_blender.md` ("As cinco auras").
  - **Hazak** (`hazak_asas.py`, `sprites/hazaki/aura/`, 288 PNG): asas, coroa, chão e partículas; é a referência
    aprovada, sem retoque.
  - **Gutto** (`gutto_aura.py`, `sprites/gutto/aura/`, 432 PNG, commit `2949112`): raios finos com galhos, rabo de
    raio no lugar do corte do tronco, vapor e crateras redesenhados, nada acima de y=7.
  - **Raiclaven** (`raiclaven_aura.py`, `sprites/raiclaven/aura/`, 480 PNG, commit `1356a3a`): leque duplo aberto
    embaixo, em cascata e sem roda, moldura de raio com clarão, roseta atrás do corpo.
  - **CK** (`ck_aura.py`, `sprites/ck/aura/`, 384 PNG, commit `e1be37b`): miolo do cone com volume na batida, parede
    que balança e estica, cones com pincelada, caixas do miolo espelhadas.
  - **Pengaró** (`pengaro_aura.py`, `sprites/pengaro/aura/`, 480 PNG, commit `11f8fb7`): miolo escorrendo sem
    costura, brilho violeta devolvido, topo em lobos, chão de frente.
  Render bruto, vídeos e tiras ficaram fora do repositório (pasta de trabalho de cada aura, no scratchpad da sessão).
- **Pendente:** **nada disso roda no jogo ainda**: falta ligar pelo `ferramentas/aura.py` da branch `efeitos`. Vídeos
  dos retoques não assistidos (só tiras); nada em fundo claro nem em outras poses. Por aura: Gutto, raios grandes
  ainda largos e vapor preso à narina da pose parada; Raiclaven, passo 3,14 px nas lâminas da frente; CK, toco de
  fumaça na borda direita e parede pouco viva pela métrica; Pengaró, chão ainda em riscos e mancha lisa entre as pernas.
- **Próximo:** o Alisson vê os vídeos e diz quais retoques valem; depois, ligar as cinco no motor (branch `efeitos`).

## 2026-11-11 (auras: PARADA às 17h20, o Alisson precisou desligar o notebook)

Parada rápida. Último commit antes desta entrada: `67ac213e`. Arquivos alterados sem commit na hora da parada: 0 (guardados neste commit; **não testados**, se houver). Falta o que a entrada anterior desta branch lista; a etapa em andamento (retoque ou conferência) foi interrompida.
## 2026-11-11 (efeitos: frente PARADA de propósito às 16h)

O Alisson pediu para parar os trabalhos para trocar o modelo de raciocínio do Claude. Kit dos bosses (docs/arcade/bosses_kit.md), sistema de aura animada (ferramentas/aura.py, lutador de teste, filmar_aura.py, medir_aura.py) e a conferência cética estão feitos; o retoque final da aura estava no meio (aura.py, gerar_teste_aura.py, bosses_kit.md, motif/fight.def e gerar_layout.py alterados). Falta: terminar o retoque, refilmar na sandbox, juntar na mugen.
Último commit feito por um agente que terminou a etapa dele: `3c0b205`. O commit seguinte a esta entrada guarda o que estava
pela metade na hora da parada (**não testado, pode estar quebrado**); para voltar ao estado bom, use `3c0b205`.

## 2026-11-11 (efeitos: PARADA às 17h20, o Alisson precisou desligar o notebook)

Parada rápida. Último commit antes desta entrada: `9a64d4fb`. Arquivos alterados sem commit na hora da parada: 1 (guardados neste commit; **não testados**, se houver). Falta o que a entrada anterior desta branch lista; a etapa em andamento (retoque ou conferência) foi interrompida.

## 2026-11-11 (efeitos: retoque da revisão cética da aura terminado e filmado)

Retomado do commit de parada `589511d` (o retoque estava pela metade, sem teste). Tudo refilmado na sandbox com o
código final (uma por vez, som desligado): roteiro padrão de 10 s e roteiro extra de 2 rounds.

- **Feito, conferido no filme:** HUD na frente da aura (`layerno = 1` no `fight.def` pelo `gerar_layout.py`: 0,00%
  das caixas de vida, retrato, nome e poder mudam; relógio visto na tira); só névoa rasteira na frente do corpo
  (pés 91,7% a 96,4% iguais ao desenho sem aura, pernas e tronco 99,8% a 100%, no loop e no surto); a aura segue na
  intro e na pose de vitória (`RoundState > 0`) e roda no `[Statedef -4]` (anda em superpausa e em estado custom);
  motor não escala nem gira nada no loop (crescer, girar, balançar assados); partículas em sequência de baixa
  discrepância (peças seguidas a 24% a 43% da área); surto só nos supers, com folga de 90 ticks; virada apaga e troca
  em 5 ticks; ligar cresce dos pés; `base=9600` (o CK usa 9300 a 9305); `registrar()` aceita a lista do Hazak;
  `filmar_aura.py` acusa pane do motor; a branch segue `origin/efeitos` (pull limpo). Kit: decisões 45 a 49.
- **Consertado nesta etapa:** (1) anel de chão subia 8,4 px no tick da decolagem do pulo (o `-4` roda antes do estado
  que dá a velocidade): a camada `"chao"` agora é solta (`bindtime = 0` no Explod e no ModifyExplod; sem o do
  ModifyExplod o `postype` volta a prender, visto no filme): desvio 0,00 px no pulo de 84 px. (2) régua do corpo no
  `medir_aura.py` comparava com um quadro de antes do `PosSet` (12% igual, falso): agora usa o quadro sem aura que
  mais bate no tronco. (3) `docs/arcade/aura_animada.md` reescrito (falava de `-2`, `pulso`, `balanco`, `base=9300`).
- **Medidas finais (ck / sombra):** loop p95/mediana 1,99 / 2,04, maior/mediana 2,18 / 2,22, 0 quadros parados;
  volta do loop 1,18x / 0,82x; mesmo quadro no máximo 2 ticks; surto: maior salto contra os vizinhos 1,63x / 1,86x;
  Explods 14 / 18 no loop, 22 / 29 no pior tick (teto 30); desligar em 35 ticks, 0 Explod no fim.
- **Pendente / não verificado:** a régua do surto foi trocada pelo construtor anterior depois de falhar (contra a
  mediana do trecho dá 3,8x no P2: é o tremor de propósito do surto, ±1,2 px por tick; fica dito no
  `aura_animada.md`); no surto e no ligar o motor ainda escala (até 25% no anel, ≤ 7% por tick: grade do pixel
  fora por uns 30 ticks); camada de chão com o lutador andando (atraso de 1 tick em x) não filmada; `mistura="soma"`,
  golpe recebido, aura num lutador de verdade; os cinco dicionários do kit só montados no host com arte de mentira
  (montam, pior caso 30 Explods no Pengaró). Itens do kit que são decisão do dono: 45 a 49 (seção 8).
- **Próximo:** juntar `efeitos` na `mugen` quando o Alisson aprovar; ligar a aura no primeiro gerador de verdade
  quando as folhas `fx_aura_*` existirem.
- Filmes: `scratchpad/aura/final/aura_teste.mp4` (+ `aura_teste_tira.png`), `padrao3/`, `extra4/` (medidas em
  `padrao3_medir.txt` e `extra4_medir.txt`).

## 2026-11-12 (aura-pengaro: aura do Blender ligada no Pengaró endiabrado)

Branch `aura-pengaro` (worktree `C:/Dev/Jogo-de-Luta-aurapengaro`, tem `mugen` + `auras` + `efeitos`).

- **Feito:** `ferramentas/aura_pengaro.py` (novo) liga as camadas de `sprites/pengaro/aura/` pelo `aura.py` no
  `[Statedef -4]` do Pengaró: Explods 9600 anel_tras (chão), 9601 coluna (coluna + chicotes + fiapos num desenho
  só, contornados juntos no Blender), 9602 anel_frente (chão, prioridade de frente, rasteiro: 10 px acima da sola,
  alfa até 0,49 com surto), 9603 soltos (pedras e elos). Liga com `var(20) > 0`, estado 3100 e o 2000 a partir do
  Time 83; surto nos supers 3000/3100/3200 e no Time 86 da transformação; entrada em 44 tiques. A aura antiga
  (Explods 9210/9211/9218 no `-2`, com os detritos na frente do corpo) saiu; os desenhos dela continuam no `.sff`
  só porque entram na escolha da paleta. A aura fica fora da paleta (`Sprites.fora_da_paleta`): paleta e os 711
  sprites antigos idênticos byte a byte; os outros lutadores de `chars/` com o mesmo md5. Custo: dois tons lilás
  claros da aura caem na mesma cor da paleta do corpo (o mais claro, 152,13,239, vira 139,19,216).
- **Ferramentas:** `aura.py` ganhou `Camada.tique` (padrão igual ao de antes; `teste_aura` sai igual).
  `filmar_aura.py --lutador X [--sem-aura]` filma a aura de um lutador de verdade (os dois lados na cor 1, Despertar
  e surto injetados no `.cmd`); `medir_aura.py --referencia` mede o corpo contra o filme sem aura (a forma
  despertada tem outro desenho, comparar com o começo do filme dava 10% falso).
- **Conferido:** robô `testar_pengaro.py` 146 passaram, 0 falharam; `verificar_pengaro.py` sai 0. Filme do roteiro
  padrão + referência: tronco 100%, pernas 99,9-100%, pés 95,8% (loop) e 98,1-98,2% (surto) iguais ao despertado sem
  aura; motor sem escala/giro no laço; mesmo quadro no máximo 2 tiques; volta do laço 0,69x/0,89x; ligando 3,8x/3,4x;
  surto 1,69x/1,57x contra os vizinhos; HUD 0,00%; 4 Explods; virada em 5 tiques; desliga em ~36 tiques, 0 no fim.
  Retoque pelo filme: pedras andavam junto da coluna (correlação -0,95, deriva lenta) e a coluna e as pedras trocavam
  de quadro no mesmo tique (p95/mediana 2,6-2,7); ligando dava 6,5x (entrada de 26 tiques).
- **Pendente / não verificado:** 1 falha no `medir_aura`: P1 tem 5 quadros quase parados no alto da tela (o P2 passa):
  a massa da coluna é desenhada a 2 tiques por quadro (Blender), e no tique sem troca só mexem as pedras e a deriva.
  Conserto pela causa = renderizar a coluna com o dobro de quadros a 1 tique (aumenta o `.sff` ~1,8 MB): decisão do
  dono. No pulo a coluna sobe junto com o corpo (o anel fica no chão): olhar se agrada. Surto num super de verdade,
  pose de vitória, round 2 e o roteiro extra não filmados com o Pengaró; fundo claro e outros cenários não vistos;
  nenhum vídeo assistido em tempo real, só tiras.
- **Próximo:** o Alisson olhar `pengaro_despertar_luta.mp4`; decidir o rerender a 1 tique; juntar na `mugen` quando
  aprovar. Filmes e tiras: `scratchpad/aurapengaro/` desta sessão (fora do repositório).

## 2026-11-12 — Aura do Pengaró: retoque depois das revisões céticas (branch `aura-pengaro`)

- **Consertado pela causa:** (1) o `anel_frente` (9602) tinha `sprpriority 5` e tingia os pés dos dois lutadores e o
  Pengaró caído: agora fica em -5, atrás de qualquer lutador (o mais baixo é o -3 do estado 5150), com o mesmo alfa,
  escala e posição do `anel_tras` (sem respirar nem tremer, que andam com fase por camada; as metades não descolam).
  Pés no `medir_aura`: 95,8% → 99,9-100%. (2) Virada: a aura apagava até 30% e o boss sumia a cada troca de lado
  (pixels roxos 125 mil → 14 mil); `Aura(virada_fundo=...)`, o Pengaró usa 0,6 (mínimo 50 mil). (3) No pulo a coluna
  subia junto e a base reta virava um prato no ar: `Camada(no_chao=True)` a deixa no chão (sem apagar com a altura).
  (4) A aura seguia cheia ~15 tiques em volta do corpo já de calça branca: `LIGADA` agora desliga com `var(20) > 34`
  e no 3100 com `AnimTime < -34`, o fade acaba junto com a forma endiabrada (robô: 0 camadas no tique em que o corpo
  volta, no fim natural e no fim do 3100). (5) As ações 9210/9211/9218 da aura antiga saíram do `.air`: a poda tira os
  24 desenhos do `.sff` (3,87 → 3,74 MB), paleta e os outros 1071 sprites iguais (`conferir_sff`, 0 diferenças).
  (6) Ficha `docs/fichas/pengaro.md`, `docs/arcade/pengaro.md` e Lote 7 da fila diziam pedras "na frente" e folhas
  `fx_aura_*`: corrigido. Comentário morto em `aura_pengaro.py` saiu.
- **Ferramentas:** `aura.py` ganhou `no_chao` e `virada_fundo` (padrões iguais aos de antes: `teste_aura` sai com o
  mesmo md5). Robô: 5 checagens novas da aura (4 camadas no Despertar, apagada quando o corpo volta, no fim natural e
  no fim do 3100; `T_fimdesp` injetado). `filmar_aura.py --lutador X --roteiro luta`: perto, super 3000 de verdade,
  pulo, fim natural do Despertar do P2, KO e pose de vitória. `medir_aura`: o corte do quadro repetido pelo gravador
  passou a valer também no trecho de desligar (era só até DESLIGA); no filme os dois maiores saltos ficavam ao lado de
  quadros com tudo parado, corpo inclusive. O filme antigo dá 2,89x com ou sem o corte; o novo, 2,89x (bruto igual).
- **Conferido:** robô 151 passaram, 0 falharam; `verificar_pengaro` 0; filme padrão + `--referencia filme_sem_aura`:
  tudo OK menos os quadros "parados" do laço (P1 5, P2 1). Diagnóstico confirmado: no alto da tela só a coluna mexe, e
  ela troca de quadro a cada 2 tiques (dentro do aceite de ≤ 3 do `aura.py`); nos tiques sem troca o céu do P1 muda
  ~1,0 enquanto o chão muda 2-5 (não é o gravador, que zera tudo). Filme luta olhado em tiras: Pengaró caído por cima
  do próprio anel, pés limpos por cima do anel do outro, coluna no chão no pulo, HUD do jogo na frente, surto pelo
  super de verdade (escala 1,0 → 1,07, anéis sem tremor), aura do vencedor até o fim da pose de vitória.
- **Pendente (decisão do dono ou desenho):** coluna a 1 tique (dobro de quadros no Blender, ~+1,8 MB) se os quadros
  "parados" incomodarem; camada presa ao chão fica parada 5 tiques na virada se o lutador estiver se movendo (visto
  só com o PosSet do filme; tentar postype+facing deu lado errado); cor da coluna mais violeta saturado que o
  violeta-preto do conceito e o anel pouco legível como "anel girando" (desenho); contraste do casaco com a fumaça
  não medido; boss pela seleção (cor 2) entra na intro sem aura (o corpo também); gatilhos `StateNo` sem filtro de
  estado custom (latente, nenhum lutador manda para 2000/3000-3200); escala 1,12 do motor no surto (passageira);
  texto "VENCEU" não aparece no modo do filme (não visto); nenhum vídeo assistido em tempo real.
- Filmes, tiras e medidas: `scratchpad/aurapengaro/final/` desta sessão (fora do repositório).

## 2026-11-12 — Aura do CK (Modo Ratão) ligada no jogo (branch `aura-ck`)

- **Feito:** `ferramentas/aura_ck.py` (molde do `aura_pengaro.py`) liga as camadas do Blender de `sprites/ck/aura/`
  pelo `aura.py`, no `[Statedef -4]`, Explods 9600 a 9602 (os efeitos do CK seguem em 9300-9305): **paredão+anéis**
  numa camada (os anéis saem dos cones; separados descolariam), **chão** (névoa+cacos) e **fagulhas**. Todas atrás de
  qualquer lutador (-7, -6, -5; o mais baixo de lutador é -3) e no chão no pulo (`no_chao`); paredão troca de quadro no
  tique ímpar, chão e fagulhas no par; entrada 44, virada a 60%. Nasce quando o Ratão sai da fumaça (estado 2000,
  tique 69); surto nos supers, no Grave (3403) e na quebra da garrafa (2000, tique 90); desliga 34 tiques antes do
  var(20) acabar (no Baile, pelo AnimTime). O paredão da aura usa `esconde`: some enquanto o paredão de cena (Explod
  9250: cena, Baile, Grave) está na tela e volta depois, sem dois paredões. A fumaça verde antiga (`aura_cns`, ação
  9210) saiu: os desenhos dela ficam só pela paleta e a poda os tira do `.sff`.
- **Conferido:** `conferir_sff` paleta igual e os 658 sprites antigos iguais (só os 288 da aura entram, os 8 da 9210
  saem; `.sff` 1,20 → 3,13 MB); md5 de `chars/` dos outros lutadores igual. Robô CK 191/0 (antes 175/0; checagens
  novas: sem aura antes do tique 69, 3 camadas e paredão escondido enquanto o de cena toca — ele sai no tique 84, a
  superpausa de 30 conta no `removetime` —, aura apaga até 2 tiques depois do corpo voltar, aura inteira depois do
  Baile, paredão some e volta no Grave). Robô Pengaró 151/0. Filme padrão + `--referencia` sem aura: tudo OK menos
  "tamanho" (abaixo); laço p95/mediana 1,93/2,02, 0 quadros parados (o paredão e as fagulhas trocam em tiques
  diferentes); surto 1,91x/1,89x contra os vizinhos; corpo tronco/pernas/pés ≥ 99,3%; HUD 0,00%; 3 Explods; virada em
  5 tiques; desliga em 36. Filme luta olhado em tira: pés limpos, CK pula por cima do paredão, fim natural do P2 apaga
  junto com a volta do corpo, aura do vencedor na pose de vitória.
- **Pendente / não verificado:** `medir_aura` falha em "tamanho": a aura sobe 130-142 px (aceite 1,4x o lutador =
  155 px). É a proporção do conceito aprovado (paredão ~1,25x o CK); subir pede rerender no Blender ou escala no motor
  (proibida): decisão do dono. Cores: a aura é levada para a paleta do CK (fora da escolha da paleta) e o cinza-verde
  sai um pouco mais verde e as fagulhas mais amarelas (distância até 21 nas cores do paredão, 47 no laranja). O
  paredão de cena some e o da aura volta noutra posição (x -46 contra 0): troca vista só no robô, não em filme. Cena
  do Despertar, Baile e Grave não filmados; dois Ratões perto viram um paredão só, enorme; nenhum vídeo assistido em
  tempo real, só tiras.
- Filmes, tiras e medidas: `scratchpad/aurack/` desta sessão (fora do repositório).

## 2026-11-12 — PARADA a pedido do Alisson (aura do CK, branch aura-ck)

- O Alisson pediu para parar ("vou ter que começar outro trabalho"). A aura do Blender do CK está ligada no Modo Ratão
  (f53a4fbd, 6543bcce) e o retoque dos céticos andou até 73ebc8b9; este commit guarda o que o retoque tinha mexido
  (docs e `filmar_aura.py`) sem ter refilmado nem rodado o robô de novo.
- **Próximo:** retomar o workflow `aura-ck-no-jogo` (run wf_2d43efbc-ea1) ou refazer só o fim do retoque: robô CK e
  Pengaró na sandbox, filme final, tira olhada, veredito. Não juntar na `mugen` sem o Alisson (depende da `efeitos`,
  que põe o HUD por cima no jogo inteiro).

## 2026-11-12 — Lutadores em alta resolução: fim do borrado (Claude, sessão do Breno)

**Pedido do Breno:** no jogo o Pengaró, o Hazak e o CK pareciam borrados, embora as folhas estivessem nítidas. Ele
pediu para resolver sem perder a fluidez.

**Causa (medida numa foto do jogo):** o boneco do quadro de jogo tem ~110 px de altura e o motor estica 3x
(localcoord 320x240 numa tela de 720). A folha do ChatGPT tem o boneco com ~600 px: o detalhe se perdia no encolhe e
estica, e o rosto, os olhos e os músculos viravam blocos 3x3.

**Feito:**
- `ferramentas/hd.py`: no fim do gerador, cada sprite do corpo é trocado pelo gêmeo 3x do mesmo quadro (achado pela
  comparação de pixels com o 1x, aceita retoque pequeno e espelho). As Clsn multiplicam por 3 e `[Size]` fica em 1/3.
  Efeito, projétil, faísca própria e retrato ficam em 1x: conferido no código do IKEMEN v1.0.0 (Explod só usa a escala
  com syncid; projétil só com `size.proj.doscale`). Um sprite usado no corpo e num efeito ao mesmo tempo é copiado
  (grupo + 20000).
- `ferramentas/hd_guiado.py <lutador>`: recria `quadros_arcade_hd/` a partir das folhas originais, guiado pelo quadro de
  1x. Ele registra escala e posição pela silhueta e pinta cada pixel 3x só com as cores do 1x na vizinhança 3x3, então
  herda paleta e retoques. O CK também ganhou `HD=3` no `converter_ck.py`, com os limiares em px do `retoques_arcade/ck.py`
  escalados.
- `rle8` e a quantização do `escrever_sff` passaram para numpy: mesmo resultado (testado contra o laço antigo) com 9x
  mais pixels.
- Ligado no Pengaró, no Hazak e no CK. Robô antes e depois (`testar_pengaro.py --local`, mesmo motor): CK 175/175,
  **mesmo dano e mesmos estados** nos 53 roteiros; Pengaró 146/146 e Hazak 175/176 (a mesma falha de antes), sem nenhuma diferença entre antes e depois.
- `.sff`: CK de 1,1 para 3,9 MB, Pengaró de 2 para 5,5 MB, Hazak de 1,1 para 4,2 MB.

**Depois, no mesmo dia: Gutto e Raiclaven.** `animar_folha.py` ganhou `HD=3` (a mesma renderização 4x do Blender reduzida
para 3x, em `quadros_hd/`). Os quadros do meio também saem em 3x, então nada pisca. `ferramentas/hd_blender.py <lutador>`
roda tudo em ~20 min. `quadros_hd` do Gutto e do Raiclaven fica fora do git (~550 MB), e o gerador avisa se faltar.
O `hd.py` passou a aceitar recorte 1-4 px diferente, porque o gerador limpa a borda (Gutto: de 260 para 575 sprites em
3x), com pré-filtro por assinatura 8x8 (de 16 min para 86 s). Robô antes e depois: Gutto 143/144 e Raiclaven 143/144
(a mesma falha de antes), sem diferença. `.sff`: Gutto 21 MB, Raiclaven 22 MB.

**Pendente:**
- Quadros montados por código continuam só ampliados: no Pengaró, parte do Despertar e alguns aéreos (104 sprites).
- Se uma folha for refeita, rode o `hd_guiado.py` dela, senão o gerador usa o gêmeo velho ou amplia.

## 2026-11-12 — Aura do CK, fim do retoque (branch `aura-ck`)

- **Feito:** o retoque dos céticos já estava em 73ebc8b9 e e9c2336e (saída presa ao var(20) pelo `resta`, entrada e
  saída só pelo alfa, sem caixa preta no Baile e no Grave, caixa da cena apagando atrás da nuvem, sem PalFX nem
  AfterImage no Ratão, docs da ficha e da tabela de auras, roteiro `cena` no `filmar_aura.py`). Esta rodada só
  conferiu: o `gerar_ck.py` reproduz o `chars/ck` do commit byte a byte.
- **Conferido na sandbox (uma por vez):** robô CK 191/0, robô Pengaró 151/0. Filme `--roteiro cena` (caminho de
  verdade: 2000 → Baile 3100 → Grave 3403 → fim natural) olhado em tira: a caixa preta apaga sob a nuvem e o paredão
  de fumaça nasce no lugar, sem buraco e sem dois paredões; Baile e Grave sem caixa preta, paredão inchando no surto;
  corpo do Ratão sem halo nem tinta; a aura acaba de apagar no tique em que o corpo volta (fumaça branca de saída).
  Filme padrão + `--referencia` (refilmada, o corpo mudou sem o PalFX): HUD 0,00%, corpo ≥ 99,4%, ligando 1,73x/1,50x,
  desligando 0,07x, virada 5 tiques, 3 Explods. **Falham:** tamanho (129/142 px contra 155) e, nesta captura, laço
  (1 quadro parado) e surto (2,60x/2,71x contra os vizinhos, tique 279). Os dois últimos são a mesma causa, vista na
  diferença por quadro: o paredão (a massa grande) troca de desenho a cada 2 tiques, então os quadros alternam
  mudança grande/pequena (~10 contra ~2). O filme do construtor passou nisso por sorte da captura.
- **Pendente (decisão do dono ou desenho):** rerender do paredão no Blender com o dobro de quadros (troca a cada
  tique; ~+1 MB no `.sff`) resolve o laço e o surto; o tamanho (paredão ~1,25x o CK, conceito aprovado) pede
  rerender maior se o dono quiser "aura enorme" de verdade; dois Ratões perto viram um paredão que cobre a tela;
  o muro espelha na virada (fica 60% e translúcido uns 10 tiques); nenhum vídeo assistido em tempo real.
  Não juntar na `mugen` sem o Alisson.
- Filmes, tiras, robôs e medidas: `scratchpad/aurack/final/` desta sessão (fora do repositório).

## 2026-11-12 — Cenário da Maria Fumaça montado e ligado no launcher (Claude)

**Pedido do Breno:** cenário de Nazaré com a Maria Fumaça (o Alisson faz o do Cristo), feito por nós, não pelo Alisson.

- Fundo: `sprites/cenarios/maria_fumaca/esbocos/esboco1.png`, aprovado pelo Breno, usado do tamanho em que saiu
  (1672x941) num cenário de `localcoord 1280,720` (o `gerar_cenario.py` da branch `cenarios` ganhou o campo `tela`).
  A câmera anda 196 px para cada lado e sobe 160.
- Camadas (`cenarios/maria_fumaca/cenario.json`): `fora` (o esboço inteiro), `dioquevara` e o `paredao` com a
  `galera` passando na rua, `grade` (barras azuis de fora, na frente deles), `salao` (o esboço com os dois arcos vazados),
  `banco` (três jovens) e `mesas` (pizza e cerveja).
- Figurantes: folhas de 8 poses no ChatGPT (`sprites/cenarios/maria_fumaca/folhas/`) e quadros do meio no Blender pelo
  `ferramentas/animar_cenario.py` (o desenho é entortado, nada de 3D). A Dioquevara é prima do Breno e topou aparecer.
  Ela passa a cada ~40 s, e o paredão a cada ~70 s.
- O maluco da caixa de som foi feito e tirado a pedido do Breno.
- Launcher: baixa também `stages/`, copia para o motor sem `/MIR` e põe `stages/maria_fumaca.def` como cenário dos
  cinco lutadores e em `[ExtraStages]`.

## 2026-11-12 — integra-mugen: HD do Despertar e aura discreta do CK e do Pengaró (Claude, construtor do orquestrador)

**O que entrou** (branch `integra-mugen`, ainda NÃO na `mugen`: quem sobe é o orquestrador depois dos céticos):

- **Merge da mugen** (parry, Maria Fumaça, `docs/regra-efeitos-proporcionais.md`): conflito só no LOGBOOK, as duas
  entradas mantidas na ordem (aura do CK, depois Maria Fumaça). Depois, mais um merge só de docs (método do ChatGPT).
- **HD do Despertar** (`ferramentas/hd.py`): o `[RemapPreset despertado]` vira corpo e ganha o gêmeo 3x; a paleta sai
  do desenho de 1x (`paleta_de`), então a forma base fica byte a byte igual (RGBA e paleta conferidos).
  Linhas `HD:` — CK 461 trocados / 93 só ampliados / 202 efeito em 1x; Pengaró 477 / 113 / 287; Gutto 607 / 570 / 54;
  Raiclaven 1057 / 118 / 54; Hazak 404 / 0 / 208 (sem RemapPreset, gerador byte-idêntico). Despertado com gêmeo /
  só ampliado: CK 191/34, Pengaró 215/23, Raiclaven 464/0, **Gutto 32/442** (a forma dele quase não tem desenho 3x
  próprio: falta folha, não código).
- **Aura discreta** (regra dos efeitos proporcionais): Pengaró e CK com UMA camada em 3x (`scale` 1/3), alfa 0,5,
  atrás, no chão, até 65% da altura do lutador. Desenho: `ferramentas/aura_blender/discreta.py` (rig de antes encolhido,
  2 sub-quadros por quadro do rig, um desenho novo por tique, 192 quadros no Pengaró e 96 no CK). Entra e sai só pelo
  alfa (`cresce=False`, `entra=44`); sem crescer, o alfa usa a entrada inteira (`aura.py`). `aura.conferir_discreta()`
  trava no gerador o teto (1 camada, 3x, 65%, alfa 0,65). Baile e Grave do CK voltaram a pôr o paredão do golpe (9250).
- **Medição**: `medir_aura.py --discreta --lutador X --referencia filme_sem_aura` (faixa baixa fora dos corpos,
  tamanho máximo, opacidade, corpo ≥ 99%). `filmar_sandbox.py` grava com `-g 9999`: com o quadro-chave padrão do x264
  (a cada 250) a tela inteira mudava ~0,5 por pixel no quadro 500, nos dois filmes, e isso caía no "desligando".

**Números** (sandbox, um por vez):
- Robôs: CK 191/0, Pengaró 151/0 (iguais à rodada anterior em estados, vidas e danos), Gutto 143/1, Raiclaven 143/1,
  Hazak 176/0. Nos roteiros em comum, iguais à mugen (a falha do Gutto e do Raiclaven é a mesma da mugen:
  `var(37) = 1 (arte endiabrada) no meio do 3100`).
- `medir_aura` CK (`ck_padrao4`): 61 OK, 0 falha. Loop 0,73/0,33 de mudança por quadro, ligando 1,31x/1,22x,
  surto 1,42x/1,47x contra os vizinhos, desligando 0,73x, tamanho 41 px (teto 72), alfa mediano 0,49, corpo ≥ 99,5%.
- `medir_aura` Pengaró (`pengaro_padrao7`, versão final): 58 OK, **1 falha**: 1 quadro "parado" no loop do P1
  (tique 169, 0,20x a mediana, no limite; o P2 cai para 0,40x no mesmo tique e não há passo dobrado depois). Os
  desenhos consecutivos mudam todos (menor par 5113 px contra mediana 6353), e o filme anterior da MESMA aura passou
  o loop (menor 0,40x): leio como captura, sem prova. Resto: ligando 1,66x/2,55x, surto 1,53x/1,67x, desligando
  1,40x, tamanho 15/10 px, alfa mediano 0,48/0,49, corpo ≥ 99,8%.

**Não verificado / observado**:
- Ninguém viu em tempo real; só tiras (`t_pengaro_luta4`, `t_ck_cena3`). Os filmes `luta` e `cena` são da versão de
  antes do alfa novo (só a entrada e a saída mudaram).
- O rastro azul que aparece atrás do Pengaró despertado no filme de luta NÃO é a aura: é o `AfterImage` aditivo
  (`[State 2000/3000, Rastro]` + `AfterImageTime` enquanto `var(20) > 0`), que já está na mugen. Pela regra dos
  efeitos proporcionais ele pode estar grande demais: decisão do Breno.

**Próximos passos**:
- Efeitos por golpe do endiabrado (Pengaró e outros): não mexi, ficam para a próxima rodada da regra proporcional.
- Gutto despertado: 442 sprites só ampliados, pede folhas 3x da forma.
- Breno olhar a aura discreta no jogo (cor e tamanho) e o rastro do Pengaró.
- Filmes, tiras e medidas: `scratchpad/integra2/` da sessão do construtor (fora do repositório).

## 2026-11-12 — integra-mugen, rodada 3: o que os céticos acharam (Claude, construtor do orquestrador)

**Correção da entrada de cima:** no `f559931a` a forma base do Gutto e do Raiclaven NÃO era igual à da mugen. Os
`quadros_hd/` regerados nesta máquina (`hd_blender.py`, fora do git) saem diferentes dos do Breno, e a paleta mudou
junto (223 e 157 cores de 256 em comum, ~750 sprites requantizados, retratos inclusive). Consertado abaixo.

**O que mudou** (commits `cc5d57c2` e o seguinte):
- **Despertado inteiro em 3x** (`hd.py`): a caixa do quadro ignora pontinhos soltos de até 12 px. O gerador do CK apaga
  essas ilhas do quadro do Ratão e o PNG de 1x ainda as tinha; a caixa saía 3 a 5 px mais alta e o gêmeo não era
  achado. A ginga parada do CK alternava 3x com 1x ampliado (HHHAHAHH). Agora o gerador imprime
  `HD do despertado: N ações misturam 3x com 1x ampliado`: **CK 0 (antes 72), Pengaró 0 (antes 74), Raiclaven 0**;
  Gutto 3 (181, 601, 10601) e 198 inteiras só ampliadas (a arte dele é reescalada pelo `fator_endiabrado`, e o gêmeo
  3x não acompanha escala: é código a fazer, não folha). Linhas `HD:` — CK 501 / 47 / 165, Pengaró 501 / 83 / 266,
  Gutto 606 / 565 / 40, Raiclaven 1057 / 112 / 40, Hazak 404 / 0 / 208 (Hazak byte a byte igual).
- **Paleta fixa** (`sprites/<l>/paleta_sff.act` = a paleta da mugen; `escrever_sff` usa ela; `conferir_sff.py paleta`
  regrava): sem ela o gêmeo a mais refazia o MEDIANCUT e mudava a cor de 19% dos pixels da forma base do CK.
- **Gutto e Raiclaven com a base da mugen** (`conferir_sff.py transplantar base.sff chars/<l>`): só o despertado vem do
  gerador. Contra a `origin/mugen`: paleta igual e **0 sprite fora do despertado diferente** nos quatro. CK e Pengaró
  mudam fora do RemapPreset só em sprites do Despertar (CK 265/267 da 9203, Pengaró 601 da 2000, agora 3x) e nos 4 da
  3012 do CK (a cópia HD saiu, o próprio sprite virou HD).
- **Endiabrado sem efeito a mais** (regra dos efeitos proporcionais): saiu o `AfterImageTime` do Despertar inteiro
  (fantasma azul) do kit, para todos; saíram a faísca própria do endiabrado (92xx + 30) e o corte de sombra / poeira
  violeta em todo golpe (9212/9215 no `[Statedef -3]`). O endiabrado usa as faíscas da forma normal; o rastro de 40
  tiques de cada super continua.
- **HUD com `layerno = 2`** (`gerar_layout.py`): com 1 a faísca de acerto (camada de cima do motor) ainda tampava o
  relógio e a vida do P2 no super 3000 do Pengaró. `gerar_layout.py` agora reproduz o `fight.def` (slow.*, over.*).
- `aura.altura()` com surto e deriva (CK 55 px, Pengaró 69 px, teto 71); `aura.largura()` no resumo (CK 84, **Pengaró
  176 px**, anotado na ficha para o Breno). `bosses_kit.md` avisa que a regra de 2026-11-12 vale acima dele.
  `regra-alta-resolucao.md`: hd_blender entre máquinas, paleta fixa, tamanhos (CK 7,3 MB, Pengaró 12,6, Gutto 30,8,
  Raiclaven 23,1, Hazak 4,4). Checklist da seção 9 com a linha do despertado e a do endiabrado.

**Números** (sandbox, um por vez):
- Robôs: CK 191/0, Pengaró 151/0, Gutto 143/1, Raiclaven 143/1; estados, vidas e danos iguais à rodada anterior (CK,
  Pengaró) e à mugen (Gutto, Raiclaven; a falha é a mesma da mugen, `var(37) = 1 (arte endiabrada) no meio do 3100`).
- `medir_aura --discreta`: CK 61 OK / 0 falha, Pengaró 59 OK / 0 falha (refilme; o 1º filme de cada deu 3 e 1 falhas
  de captura — quadro "parado" e salto no surto, com o motor andando 1 desenho por tique, como já tinha acontecido).
  CK: loop 0,74/0,33, surto 1,42x/1,50x contra os vizinhos, 41 px, alfa 0,49, pernas ≥ 99,5%. Pengaró: loop
  0,47/0,22, surto 1,39x/1,76x, 15/10 px, alfa 0,48/0,49, pernas ≥ 99,9%.
- Filmes: Pengaró `luta` sem o fantasma azul (pulo e parado); no super 3000 o HUD fica na frente da faísca. CK `cena`:
  ginga do despertado nítida em todos os quadros (q452 a q485, eram q458/q470 em blocão). Sem quadro preso nem piscada.

**Pendente:**
- A faísca final dos supers (9205, `FAISCA_FINAL`: clarão branco de ~150 px com borda reta de caixa, nas duas formas,
  já na mugen) cobre o tronco do P2 por ~4 quadros. A regra deixa o super ter o efeito grande; a arte nova sai na
  missão dos efeitos do Blender.
- Gutto despertado só ampliado (escala do `fator_endiabrado`). Gutto e Raiclaven ainda têm o PalFX que tinge o corpo
  no Despertar (o CK e o Pengaró já não têm).
- Parry: nenhum roteiro do robô cobre; não filmado.
- Breno: ver no jogo a largura da aura do Pengaró (176 px) e a cor das duas auras.

## 2026-11-12, 23:58 — Junção sobe na mugen; folhas boss prontas na branch bosses (Claude, orquestrador)

**Subiu na mugen:** o integra-mugen inteiro (até este commit). Dois céticos novos conferiram a rodada 3 (e6750263), um
por código e outro na sandbox, e nenhum achou defeito alto. Conferido por eles:
- forma base de CK, Pengaró, Gutto, Raiclaven e Hazak igual à da mugen (paleta byte a byte; só 3 sprites do CK e do
  Pengaró trocaram 1x ampliado pelo 3x certo);
- despertado do tamanho da forma base (era 1/3 na mugen), CK/Pengaró/Raiclaven 100% com gêmeo 3x;
- fantasma azul permanente fora; HUD na frente da faísca; `gerar_layout.py`, `gerar_ck.py` e `gerar_pengaro.py`
  reproduzem `chars/` byte a byte.

**Pendências dos céticos (nenhuma piora a mugen):**
- Gutto despertado: 442 de 474 sprites só ampliados, e as ações 181, 601 e 10601 misturam 3x com 1x (piscam).
- Gutto e Raiclaven sem aura própria em sprite (só o PalFX de tinta).
- O `.sff` do Gutto e do Raiclaven depende do `conferir_sff.py transplantar` (documentado em `regra-alta-resolucao.md`).
- Rastro de 40 tiques do super do Pengaró despertado ainda grande; clarão 9205 cobre o tronco do P2 por uns quadros.
  Breno decide se entram na regra dos efeitos proporcionais.

**Folhas boss (branch `bosses`, a8009718, não entra na mugen ainda):** Hazak 55/55, Gutto 36, Raiclaven e CK com todo
o corpo; folhas `fx_*` ficam para o Blender. Ainda com defeito: CK `b_ar_soco` e `b_martelo` (parcial), Raiclaven
`b_corrente_chicotada` e `b_corrente_mangual` (~9% menores). Detalhes no LOGBOOK da `bosses`.

**ChatGPT:** os 4 chats boss (Gutto, Raiclaven, CK, Hazak) foram apagados e conferidos (404). Ficaram, para o dono
decidir: "Hazak — arcade", "CK — arcade", "Pengaró — arcade", "Generate Hazak Image", "Generate Sunset Background" e
uns de pixel art de 2026-11-08 de origem incerta. Refazer folha boss agora pede chat novo com o conceito anexado do disco.

**Próximo:** missão do Breno (Pengaró e Hazak no estilo do CK e do Gutto), efeitos `fx_*` no Blender, pendências acima,
cenários.

## 2026-11-13, 07:35 — Menu enxuto e Modo Super (Claude, sessão do menu)

**Pedido do Breno:** menu só com Versus, Arcade, Assistir e Opções, mais um modo em que as barras de power ficam
sempre cheias.

**Entrou:**
- Menu principal: **ARCADE, VERSUS, MODO SUPER, ASSISTIR, OPÇÕES**. Os itens padrão do motor (team, survival, co-op,
  treino, sair) saem com nome vazio no `system.def`, feito pelo `gerar_layout.py` (lista `escondidos`). Antes, eles
  ficavam depois do SAIR, cortados no pé da tabuleta. Para fechar o jogo: Esc no menu ou o X da janela.
- **Modo Super** (`motif/nazafight/modo_super.lua`, ligado por `[Files] module` no `system.def`; o launcher já leva a
  pasta do motif inteira para o motor). É o versus 1 contra 1, e a cada quadro de luta o power dos lutadores volta ao
  máximo (`hook loop#versus` + `setPower(powerMax())`). Vida normal. Nada nos lutadores. O motor roda como `versus`
  (telas, pausa e placar iguais); a tela de seleção mostra "MODO SUPER". Qualquer outro modo escolhido desliga.
- O super fica entre Versus e Assistir porque é uma variação do versus (mesma seleção, dois jogadores).
- `menu.window.margins.y` de 12 para 48: o motor cortava o alto do 1º item (ARCADE) e a tábua ativa ficava vazia.
  Já acontecia antes desta mudança.

**Conferido no jogo** (cópia do motor nesta máquina, janela capturada por PrintWindow): menu com os 5 itens e o
ARCADE inteiro; MODO SUPER abre a seleção com o título certo; luta CPU x CPU (só no teste) por 37 s com a barra de power
dos dois em nível 3 em todos os quadros, inclusive logo depois de um super e do Despertar do Pengaró. A vida caiu normal.

**Não testado:** Modo Super com duas pessoas no teclado (o caminho do power é o mesmo); o launcher novo baixando isso.

## 2026-11-13, 08:20 — Abertura nova: Nazaré ao pôr do sol (Claude, sessão do menu)

**Pedido do Breno:** "olha ai nazare e monta uma arte legal para ser a abertura e menu do jogo".

**Entrou:**
- Fundo da abertura gerado no ChatGPT (`sprites/titulo/fundo_chatgpt.png`): o Jaguaripe ao pôr do sol, a ponte, o
  casario colorido, a Igreja Matriz de N. S. de Nazaré e o Cristo no morro, saveiros, caxixis e farinha na feira. O
  `gerar_layout.py` (`fundo_titulo`) corta para 16:9 e passa para pixel art de grade 2x (640x360 de desenho, 64 cores,
  sem pontilhado).
- Logo NAZAFIGHTS novo com a faixa RECÔNCAVO • BAHIA nas cores da Bahia (`sprites/titulo/logo_chatgpt.png`, fundo verde
  vira transparente em `logo_titulo`), 640 px, no céu da esquerda para não tapar a Matriz e o Cristo. Continua caindo
  e quicando ao abrir.
- Menu numa faixa escura translúcida com borda dourada (`faixa_menu` + `trans = addalpha`, `alpha = 192,64`: o motor
  não mistura o alfa parcial do PNG). A tábua de destaque agora acompanha o cursor (`menu.item.active.bg.spacing`;
  antes ficava presa na 1ª linha e tapava o ARCADE).
- Saiu do gerador o título antigo desenhado por código (céu, nuvens, cidade, rio, brilho, canoa, nuvem de farinha,
  subtítulo, tabuleta). As letras de barro (`logo()`) ficam, porque o emblema do VS usa.
- Essa arte fica fora da paleta de 16 cores e da grade 4x do resto do layout (decisão desta tarefa).

**Conferido no jogo** (cópia do motor, PrintWindow): abertura com logo, faixa translúcida e destaque seguindo o cursor
até MODO SUPER; a seleção e a luta abrem.

**Pendente:** o Breno ver se gosta. Se quiser outro ponto da cidade ou outro logo, é só refazer as duas imagens em
`sprites/titulo/` e rodar o gerador.

## 2026-11-13 — Retratos novos dos cinco e HUD novo (Claude, sessão do Breno)

**Pedido do Breno:** retratos bonitos de todos para a seleção e um HUD "que condiz com um jogo de luta": o antigo era
feio, alto (o pote do relógio descia até y = 150) e a barra de poder ficava na linha dos pés (y 668 a 716).

- **Retratos:** busto de cada lutador no ChatGPT (estilo arcade, rosto tirado das referências das fotos:
  `sprites/<l>-selecao-kof.png` para Pengaró, Hazak e CK, folha-referência para Gutto e Raiclaven). Brutos em
  `sprites/retratos/brutos/`. `ferramentas/preparar_retratos.py` recorta o busto 448x216 (9000,1) e o rosto 100x100
  (9000,0). `ferramentas/trocar_retratos.py` grava os dois no `.sff` do lutador como PNG de 32 bits (formato 12, no
  bloco tdata), sem mexer no corpo nem na paleta.
  - **Atenção:** o `gerar_<lutador>.py` regrava o `.sff` com os retratos antigos. Depois de gerar qualquer lutador,
    rode `python ferramentas/trocar_retratos.py <lutador>`.
  - O motor amplia 4x o sprite do lutador, então o layout usa escala 1/4: grade, seleção e HUD com 0.25, VS com 0.5.
- **HUD (`gerar_layout.py`, fight.def):**
  - Em cima: retrato com moldura de ouro, barra de vida fina com a ponta do relógio inclinada, plaquinha do nome e
    caixa compacta do relógio. Tudo termina em y = 120.
  - Embaixo: trilho de poder fino com 3 pedrinhas de estoque, de y 688 a 716. Saiu o número do nível.
  - Peças novas: `moldura_dourada()`, `trilho_vida()`, `relogio()`, `PLACA`/`composto_poder()`.
- **Conferido no jogo** (1280x720, motor desta máquina): luta com os cinco, seleção e menu novo da outra sessão.
  As prévias em `docs/previas-layout` também foram refeitas.
- **Não feito:**
  - O "?" da escolha aleatória aparece desencaixado sobre a célula vazia da grade.
  - O sprite de luta do Pengaró continua de pele clara (missão do Alisson em
    `docs/arcade/pedido-pengaro-hazak-nitidez.md`).

## 2026-11-13 — Auras grandes e efeitos do endiabrado de volta (Claude, sessão do Breno)

**Correção do Breno:** "eu queria que os efeitos de combate ficassem mais simples, e eu falei que no modo endiabrado eu
não queria que mudasse nada, queria as auras monstruosas e grandes para mostrar que tem poder". A regra de 2026-11-12
foi lida como "aura discreta" (o erro começou no texto que eu escrevi na `regra-efeitos-proporcionais.md`). Desfeito:

- **Aura grande do CK e do Pengaró:** `aura_ck.py`, `aura_pengaro.py` e `sprites/{ck,pengaro}/aura/` voltaram à versão
  de antes do 624030c9 (Pengaró com 4 camadas, 9600 a 9603; CK com 3, 9600 a 9602). No CK, o Baile e o Grave voltam
  a usar o paredão da aura em surto, sem a caixa preta 9250.
- **Efeitos do endiabrado:** os blocos de efeito do cc5d57c2 foram desfeitos no `gerar_pengaro.py`, `gerar_ck.py` e
  `gerar_hazaki.py`. Voltaram o rastro do Despertar (AfterImageTime), a faísca própria do endiabrado (92xx + 30) e o
  corte de sombra e a poeira violeta em todo golpe.
  - Ficaram a paleta fixa, o despertado em 3x e o HUD na frente da faísca.
- **Lutadores:** o CK e o Pengaró foram gerados de novo. O Gutto e o Raiclaven também, e depois passaram pelo
  `conferir_sff.py transplantar` com a base do ca786230 (a forma base é a da mugen). Os retratos novos foram regravados
  (`trocar_retratos.py`, que agora não duplica se rodar duas vezes). O Hazak não mudou.
- **Robô** (`testar_pengaro.py --local`, `robo.lua` de volta às checagens da aura grande):

  | Lutador | Passou | Falhou |
  |---|---|---|
  | Pengaró | 151 | 0 |
  | CK | 191 | 0 |
  | Gutto | 143 | 1 |
  | Raiclaven | 143 | 1 |

  A falha do Gutto e do Raiclaven é a mesma de antes na mugen.
- **Docs:** a regra dos efeitos, as regras dos lutadores (seção 4 e checklist), `como-trabalhar`, `bosses_kit` e
  avisos em `aura_animada`, `aura_blender` e nas fichas. **Não use `discreta.py` nem `conferir_discreta()` em
  lutador de verdade.**
- **Não visto em tempo real:** o filme de aura só roda na sandbox. O robô confere as camadas vivas no Despertar.

## 2026-11-14 — Pengaró de volta ao desenho antigo, nítido e com a pele bem escura (Claude, thread do Alisson)

**Pedido do Breno** (`docs/missao-alisson-2026-11-13.md`, item 1): o redesenho do `dc3427bf` saiu; o Pengaró volta ao
desenho de antes, nítido como o CK e o Gutto, com a pele bem escura, e o endiabrado não muda.

- **Folhas:** 34 folhas da forma normal no ChatGPT, em `sprites/pengaro/quadros/folhas_novas/`. Cada uma foi pedida
  com a referência nova e a folha antiga anexadas, copiando as 8 poses da antiga. A queda foi refeita duas vezes:
  na 1ª veio com o rosto antigo, na 2ª fora de ordem. **O endiabrado não foi tocado** (pedido do Breno).
- **Conversão:** `ferramentas/converter_pengaro.py` gera `quadros_arcade/<folha>` em 1x e `quadros_arcade_hd/<folha>`
  em 3x, os dois direto da folha grande (o 3x tem detalhe próprio, não é o 1x ampliado), com alfa seco.
  - A escala é folha por folha: a mediana do tamanho contra os desenhos antigos da mesma pose (git `965f8013`).
  - Com escala única, várias folhas saíam pequenas, e o robô acusou golpes sem alcance.
- **Gerador:** saíram `REPETE_ARCADE` e `DESLOCA_ARCADE`, que corrigiam defeitos dos desenhos antigos.
- **Conferido:**
  - robô 151/0;
  - luta no jogo: o rosto ficou com o mesmo nível de definição do CK;
  - retratos regravados com `trocar_retratos.py`.
- **Por que o Pengaró antigo borrava:** a folha tinha o boneco pequeno (~280 px), que era ampliado. Em cima disso, os
  quadros do meio do Blender suavizavam a borda.
- **Pendente:**
  - o Hazak segue no estilo antigo (a recriação está com o Alisson, branch `hazak`);
  - as pastas `meio/` antigas em `quadros_arcade/` ficaram no disco, sem uso.

## 2026-11-14 — Revisão geral: "?" da seleção, robô no 3100 e Gutto despertado em 3x (Claude, sessão do Alisson)

Itens da seção 4 de `docs/missao-alisson-2026-11-13.md`.

**Feito:**
- **"?" da escolha aleatória encaixado** (`gerar_layout.py`): o IKEMEN desenha `cell.random.spr` somando o
  `portrait.offset` (14,14), e a célula vazia não (`start.lua`, `updateDrawList`). O sprite 300,1 ganhou eixo 14,14
  (`RETRATO_NA_CELULA`), a checagem de grade aceita esse caso e a prévia `selecao.png` passou a desenhar o "?" como o
  motor desenha. O resto do layout continua igual (as outras prévias mudam só na compressão do PNG; não subiram).
- **Robô do Gutto e do Raiclaven no 3100**: o super zera `var(20)` no tick 0 e o corpo voltava à forma base no meio
  do golpe. As quatro trocas que o Pengaró e o CK já tinham (`stateno = 3100` segura `var(37) = 1` e o RemapSprite)
  viraram `gp.super_3100_endiabrado()`, chamada também em `gerar_gutto.py` e `gerar_raiclaven.py`. Os dois `.cns`
  receberam as mesmas 4 linhas.
- **Gutto despertado em 3x**: o `colar_endiabrado` reescala a figura pelo `fator_endiabrado`, e o `hd.py` não achava o
  gêmeo 3x comparando pixels. Agora o gerador monta o gêmeo junto (`gerar_pengaro.GEMEOS_HD`: mesmo recorte, mesma
  escala, mesmo lugar, em 3x, com o alfa limitado ao corpo do 1x; o `move` leva o gêmeo junto) e o `hd.aplicar(...,
  gemeos=)` usa ele quando a comparação não acha. Resultado: `HD: 1052 trocados (446 montados), 125 só ampliados`
  (era 606 / 565) e **0 ações misturando 3x com 1x** (eram 181, 601 e 10601). No `.sff`: dos 472 sprites do
  despertado usados, **0 só ampliados** (eram 440). Forma base, paleta e retratos iguais à `mugen` byte a byte
  (`conferir_sff.py transplantar` + `trocar_retratos.py gutto`).
- `conferir_sff.py ler/transplantar` aceita retrato em PNG (grupo 9000, do `trocar_retratos.py`) na base.

**Como foi gerado:** `quadros_hd/` do Gutto feitos na nuvem com o Blender 4.5.16 como módulo Python (`bpy`, Cycles
CPU), pelo `hd_blender.py`. Pengaró e CK regerados com o código novo saem iguais aos regerados com o código antigo na
mesma máquina (o código novo não muda nada neles).

**Não testado:** robô e jogo (o IKEMEN não roda na nuvem). Rodar `python ferramentas/testar_pengaro.py --lutador
gutto` e `raiclaven` antes de subir; o esperado é 144/0 nos dois. Raiclaven não foi regerado (só o `.cns`).

**Ficou:** parry (`docs/parry.md`), figurantes e HUD novo sem conferência, Pengaró e Hazak (itens 1 da missão).

- **Revert do `dc3427bf`.** O gerador reproduz o `.sff` do `965f8013`.
- **Causa do borrado, medida:** na folha antiga o Pengaró tem ~275 px; o CK, ~550 px. O 3x (~330 px) ampliava o
  Pengaró e reduzia o CK.
- **Nítido sem redesenhar:** `ferramentas/ampliar_folhas.py` passa as 33 folhas antigas no Real-ESRGAN (anime_6B, 4x
  e reduz para 2x; `quadros/folhas_arcade_sr/`, 62 MB). `ferramentas/nitidez_pengaro.py` tira o 3x dessa folha
  (reduzida, como no CK) e pinta com as 15 cores do 1x numa vizinhança 5x5. Posição, escala, caixas e `.air`/`.cns`
  iguais. HD: 504 sprites trocados pelo 3x (antes 501), 86 só ampliados.
- **Pele bem escura** (paleta de `docs/arcade/pengaro.md`) por troca de cor no 1x, no 3x e nos quadros do meio usados.
  A garrafa (mesmas cores no vidro e no rótulo) é achada em cada quadro e poupada; conferido quadro a quadro nas 34
  folhas, 22 quadros corrigidos à mão (`GARRAFA_MAO`). A calça branca e a corda, que usam o creme e o âmbar da pele,
  ficaram como eram. As 5 cores entraram no `paleta_sff.act` nas linhas de menos uso.
- **Endiabrado:** nenhum sprite do corpo mudou (conferido sprite a sprite contra o `.sff` anterior). Seis sprites de
  efeito do endiabrado e 56 de efeito da forma normal tiveram de 1 a 124 pixels trocados por uma cor vizinha quase igual
  (as linhas da paleta que receberam a pele).
- **Não testado no motor:** o robô e a luta rodam no Windows (sandbox ou PC do Breno). Só pixels mudaram, então o
  robô deve dar o mesmo 151/0, mas falta rodar e tirar a foto ao lado do CK.
- **Ficou:** a cena do Despertar (`despertar_a`, arte antiga) com a pele de antes; quadros do meio e `f_agarrao4/5` em 1x
  ampliado; o rosto parecido com a foto (não mexi no desenho). Detalhes em `docs/arcade/pengaro-nitido.md`.

## 2026-11-14 — Robô de teste roda no Linux sem tela (Claude, sessão do LightWolfMan)

**Pedido:** rodar o robô (`ferramentas/testar_pengaro.py`) na nuvem Linux, sem depender do PC/notebook do Alisson.

**Feito:** modo `--linux` (padrão quando o sistema é Linux) no `testar_pengaro.py`. Baixa o IKEMEN GO v1.0.0 Linux
para `~/.cache/nazafight/ikemen` na primeira vez (abre o motor 20 s para nascer o `save/config.ini`), copia o motor
para uma pasta temporária e roda a luta no Xvfb com Mesa llvmpipe (`xvfb-run`, som `dummy`). Modo Windows/sandbox
intocado. Requisito: `apt install xvfb libgl1-mesa-dri`.

**Resultados (cada luta ~60 s, 4 núcleos):**
- branch `claude/project-thread-j4685w`: Gutto 146/0, Raiclaven 146/0 (var(37) = 1 no meio do 3100: falha sumiu).
- branch `claude/project-thread-xhv5a2`: Pengaró 151/0. `mugen`: Pengaró 151/0 (motor baixado do zero).

No Linux o robô instala o layout `motif/nazafight` (como o `.bat`); sem ele o HUD do motor puro mostrava o retrato HD
gigante e cortado no print. **Sugestões:** o robô ainda não tira print sozinho; dá para tirar com `import -display :99 -window root` durante a luta.
Um GitHub Action com esse modo rodaria o robô a cada push.
- **Mugen final** (revisão geral + Pengaró nítido + robô no Linux, `c5d10f43`): Gutto 146/0, Raiclaven 146/0,
  Pengaró 151/0, rodados na nuvem.
## 2026-11-11 (cenários animados: base pronta, branch `cenarios`)

- **Feito:** `ferramentas/gerar_cenario.py` (descrição em JSON com camadas PNG → `stages/<id>.def` + `.sff` RGBA, com
  simulação da câmera, recusa de furo e prévia em GIF), `ferramentas/cenario_teste.py` (cenário de teste por código, em
  `cenarios/teste/` e `stages/teste.*`), `ferramentas/filmar_cenario.py` + `ferramentas/robo/passeio.lua` (filme do
  passeio pelas duas pontas, com tiras). `sandbox.py` e `filmar_sandbox.py` copiam `stages/` para o motor da sandbox; o
  `filmar_sandbox.py` ganhou `--cenario` e `--passeio` (mudanças aditivas). Método e medidas da arte em
  `docs/arcade/cenarios.md`. Provado em dois filmes de 8 s na sandbox: cenário carrega, pés na linha do chão (y = 165),
  nenhuma borda preta nas pontas nem com a câmera no alto, paralaxe, nuvens, rio e bandeira em quadros, balão em seno,
  barco por BGCtrl, camada de frente, luz somada e reflexo.
- **Pendente:** a arte dos quatro lugares (Cristo, Maria Fumaça, praça da prefeitura, passarela) não existe; o launcher
  não baixa nem instala `stages/` e o `select.def` não lista cenário (o que falta está na seção 7 do `cenarios.md`); o
  padrão do jogo continua `stage0-720`. Não provado: tremor de tela, `subtrai`/`alfa`, outros BGCtrl, escolha pelo menu.
- **Próximo:** referência dos lugares, fila de prompts das camadas, converter a arte para a malha 320x180 e gerar os
  quatro cenários; depois ligar no launcher.

## 2026-11-11 (cenários de Nazaré: projeto e fila de arte, branch `cenarios`)

- **Feito:** `docs/arcade/cenarios_nazare.md`: projeto dos quatro cenários pedidos pelo Alisson (Cristo ao entardecer,
  Maria Fumaça de noite dentro do galpão da estação, praça da prefeitura em manhã de sol, passarela ao amanhecer com
  neblina), cada um com lugar real e fontes, camadas com tamanho e delta, paleta, lista do que se mexe (10 ou 11 por
  cenário) e a fila de 64 imagens para o ChatGPT com prompt pronto (14 + 14 + 13 + 17 + 6 comuns).
- **Pendente:** nenhuma imagem gerada; a ferramenta de conversão (recorte pela cor de fundo, redução, quantização, fatia
  das folhas) e o script de montagem de cada cenário (luzes por código + `cenario.json`) não existem; posições são de
  prancheta, sem prévia nem motor. O topo do documento tem 11 perguntas para o Alisson (qual Cristo, cor da prefeitura,
  locomotiva dentro do galpão ou na rua, passarela nova ou antiga, luta na beira ou em cima dela, horas do dia).
- **Próximo:** respostas do Alisson; gerar o lote piloto (4 primeiras imagens de cada cenário); escrever a conversão;
  montar e filmar um cenário inteiro (sugestão: a praça) antes de pedir o resto.

## 2026-11-11 (cenários: frente PARADA de propósito às 15h50)

O Alisson pediu para ir parando os trabalhos aos poucos, para mudar o modelo de trabalho com segurança. Esta frente
(cenários animados de Nazaré: Cristo, Maria Fumaça, praça da prefeitura e passarela) foi interrompida durante a
geração da arte do primeiro cenário.

- **Feito e no git:** `ferramentas/gerar_cenario.py` (camadas, paralaxe, quadros, velocidade, seno, camada de frente),
  `filmar_cenario.py`, cenário de teste `stages/teste.def` provado na sandbox, `sandbox.py` levando `stages/` ao motor;
  método e medidas em `docs/arcade/cenarios.md`; pesquisa dos quatro lugares, projeto e fila de 64 imagens com prompt
  em `docs/arcade/cenarios_nazare.md`; 9 imagens brutas do Cristo em `sprites/cenarios/cristo/bruto/` (céu, chão,
  cristo, morro, torres, longe, nuvens longe e perto, cerca).
- **Não feito:** o resto da arte do Cristo; toda a arte da Maria Fumaça, da praça e da passarela; a montagem dos quatro
  cenários, o filme na sandbox e a conferência. Nenhum cenário de Nazaré existe no jogo ainda.
- **Antes de retomar:** responder a lista "Para o Alisson confirmar" no topo de `docs/arcade/cenarios_nazare.md`
  (qual Cristo, como ele está hoje, onde fica a Maria Fumaça, qual passarela). Depois seguir a fila do mesmo arquivo a
  partir da primeira imagem do Cristo que não está em `bruto/`.

## 2026-11-14 — Pengaró redesenhado do Breno de volta, com correções (Claude, sessão do Alisson)

**Pedido do Breno (#32):** tirar o Pengaró antigo nítido, voltar o redesenho `dc3427b` mantendo a revisão `118326d`,
conferir as 34 folhas e consertar só o que estiver errado, robô e foto ao lado do CK antes da mugen.

**Feito:** reverts do antigo nítido + reapply do `dc3427b`, sff regerado com o gerador da revisão. Agachado no jogo usa a
ordem da folha nova (antes subia até um quadro meio em pé no meio do agachado). Riscos soltos apagados nas folhas corre,
afastar, pulo e rasteira (`ferramentas/limpar_riscos_pengaro.py`). Escala das folhas de parry pela mesma pose.
Robô 151/0 na nuvem. Plano e lista quadro a quadro: `docs/arcade/pengaro-redesenho-correcoes.md`.
**Sugestões:** os rastros que sobraram (laranja atrás da garrafa na corrida, mancha em compasso 4/5) pedem retoque à mão
ou refazer esses quadros no ChatGPT; esperar a lista de erros do Breno na #32.
## 2026-11-14 — Trilha sonora ligada no jogo (Claude, thread do Alisson)

**Pedido:** avaliar a trilha que o Breno subiu e ligá-la (Alisson aprovou); depois o Breno pediu na #33 loop sem
emenda e a música do cenário baixando até sumir antes da do boss.

**Feito:** as 11 faixas em OGG (-14 LUFS, loop em batida com crossfade de 120 ms assado, `musicas/loops.json`), ligadas
no título, na seleção, na Maria Fumaça e no Despertar do Pengaró, CK, Gutto e Raiclaven (fade de 45 tiques com
`ModifyBGM`, depois `PlayBGM`; a do cenário volta no fim). Ferramentas novas: `converter_musicas.py` e
`testar_musica.py`. Tudo em [`docs/trilha-sonora.md`](docs/trilha-sonora.md).

**Conferido:** `testar_musica.py` (cenário toca, fade 100→0, entra a do boss, volta a do cenário; volta do loop no
`loopstart`); robô `--linux`: Pengaró 151/0, CK 191/0, Gutto 146/0, Raiclaven 146/0.

**Não feito / não verificado:** ninguém ouviu as emendas (som `dummy` na nuvem). Os `.cns` de Gutto e Raiclaven
receberam só o bloco da música (o gerador sem `sprites/*/quadros_hd` sairia em 1x); `.sff`/`.cmd` de todos ficaram
como estavam. Hazak sem Despertar, então sem música de boss ainda. Cristo, praça e passarela esperam os cenários.
