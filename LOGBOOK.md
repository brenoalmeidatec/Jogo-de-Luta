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
