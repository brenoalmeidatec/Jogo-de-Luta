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
