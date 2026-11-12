# Aura animada do Despertar

Sistema único para a aura de todo lutador despertado (regra da seção 4 de
[`regras-dos-lutadores.md`](../regras-dos-lutadores.md): aura é efeito à parte, por `Explod`). Fica em
[`ferramentas/aura.py`](../../ferramentas/aura.py). Nada na aura fica parado: os quadros do desenho andam de 2 em 2
ticks, e entre um quadro e outro o motor mexe cada camada a cada tick (posição e alfa). O que cresce, gira ou balança
é **assado no desenho**, na grade do pixel: o motor não escala nem gira nada no loop.

Kit dos cinco bosses (dicionário de aura de cada um): [`bosses_kit.md`](bosses_kit.md). Camada feita no Blender:
[`aura_blender.md`](aura_blender.md).

## Como um gerador usa

```python
import aura
F = RAIZ / "sprites/ck/quadros/folhas_arcade"
base = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura.png"), altura=236), total=28)
coluna = aura.ondular(base, amplitude=3, ondas=1.2)          # o balanço vai assado, não pelo motor
nevoa = aura.nevoa_rasteira(124, 13, 24)                     # a única coisa na frente do corpo
AURA = aura.Aura("ck", ligada="var(20) > 0", surto="StateNo = [3000, 3999] && Time = 1", base=9600, camadas=[
    aura.Camada("coluna", coluna, plano="tras", pos=(-4, 2), mov=aura.Movimento(deriva=(3, 4), alfa=0.86)),
    aura.Camada("nevoa", nevoa, plano="frente", pos=(2, 3), surto_incha=0.0, surto_alfa=0.08,
                mov=aura.Movimento(deriva=(3, 0.5), alfa=0.4)),
], particulas=[aura.Particula("anel", aura.anel_de_fumaca(26, 12), periodo=14, vida=46, vel=(0, -1.2),
                              escala=(0.8, 1.6))])
AURA.conferir(grupos=..., acoes=..., explods=...)  # falha se o lutador já usa algum número da aura
entrou = AURA.registrar(sprites)   # quadros no .sff: um grupo por camada e por partícula, de 9600 em diante
air += AURA.air()                  # [Begin Action 9600] ...
cns += AURA.cns(cabecalho=True)    # [Statedef -4] + controladores (sem cabecalho se o lutador já tem um -4)
```

- `ligada`: condição do `.cns` que vale enquanto o Despertar dura. A aura vale com `RoundState > 0` e o lutador vivo:
  segue na intro e na pose de vitória. Antes da intro de cada round (`RoundState = 0`) os `map` zeram e os `Explod`
  são removidos. Entra em 26 ticks (nasce rente ao chão e sobe: escala y de 0,08 a 1, alfa antes da altura), sai
  em 34.
- `surto`: condição que dispara o surto (padrão do kit: só os supers, `StateNo = [3000, 3999] && Time = 1`; nos
  especiais escolhidos o gerador põe `AURA.disparo_surto()` dentro do estado). Por uns 30 ticks a aura incha
  (`surto_incha`, padrão 12%), treme (`surto_tremor`), o tempo dela corre 2,6x, a animação anda 1 quadro por tick e
  as partículas nascem `surto_extra` vezes mais. Depois de um surto há folga de 90 ticks antes do próximo.
- `tique`: em que tique do passo a camada troca de quadro (padrão: índice % tempo). Camadas desenhadas juntas (as
  metades de um anel) no mesmo tique; camadas que dividem a mesma região, em tiques diferentes.
- `esconde`: expressão por camada; enquanto vale, a camada apaga (~8 ticks) e volta depois. Serve para a reação
  avulsa do gerador (o garanhão do coice, as asas que fecham) tocar no lugar da camada em loop, sem dobrar.
- Virada: quando o lutador vira, as camadas apagam, trocam de lado 5 ticks depois e voltam (12 ticks no total).
  `Aura(virada_fundo=0.3)` é até onde o alfa desce: 0,3 some quase tudo (bom para aura pequena); a do Pengaró usa 0,6,
  porque com 0,3 o boss sumia a cada troca de lado (pixels roxos de 52 mil para 5 mil no filme de 2026-11-12).
- `no_chao`: `True` numa camada de plano `"tras"` (uma coluna que nasce do chão) a deixa no chão no pulo e na queda,
  como a de plano `"chao"`, mas sem apagar com a altura. Presa ao corpo, a base reta da coluna do Pengaró virava um
  prato solto no ar.
- Variáveis: só `map` (`au_<nome>_f`, `_e`, `_s`, `_k`, `_t`, `_c`, `_r`, `_v`, `_l`, `_n<j>`, `_h<i>`). Não gasta
  `var()` do lutador.
- Números: ações, ids de `Explod` e grupos de sprite de `base` a `base + camadas + partículas - 1`. **`base=9600`**:
  o CK já usa 9300 a 9305 e o Pengaró 9000 a 9235.
- `registrar(sprites)` aceita os três jeitos dos geradores: `guardar(...)` (Pengaró), `add(...)`, ou uma `lista` de
  `(grupo, índice, imagem, eixo x, eixo y)` (Hazak: some o conjunto devolvido ao `manter` do `escrever_sff`, senão a
  poda tira a aura).
- `plano`: `"tras"` (sprpriority -6...), `"chao"` (-9...; fica no chão quando o lutador pula e some com a altura) e
  `"frente"` (5...). A frente é só névoa rasteira: o construtor recusa camada da frente mais alta que 13% do
  lutador acima dos pés, com alfa acima de 0,5 (contando o surto) ou que seja cópia de outra camada.
- Arte guardada: `aura.salvar_quadros(quadros, pasta)` e `aura.ler_quadros(pasta)` evitam refazer o fluxo óptico.

## O que cada peça faz

| Peça | Para quê |
|---|---|
| `recortar_folha(caminho, quadros=8, fundo=None, limiar=90)` | folha em verde `#00FF00` ou magenta vira quadros RGBA; borda corroída 1 px e repintada com a cor de dentro (franja zero) |
| `enquadrar(celulas, altura= ou largura=, ancora="base")` | mesma caixa para todos os quadros, na escala do jogo |
| `alongar_loop(desenhos, total=24, loop=True, metodo="fluxo")` | 8 desenhos viram 16 a 32; `"fluxo"` (fumaça, fogo), `"mistura"` (luz que pisca), `"dissolve"` (raio). **Nunca em corpo** |
| `ondular`, `reduzir`, `espelhar`, `girar_loop` | balanço, tamanho, espelho e giro **assados** nos quadros (giro com vizinho mais próximo: o pixel continua pixel) |
| `nevoa_rasteira` | névoa baixa com buracos, para a camada da frente |
| `medir_loop(quadros)` | mudança entre quadros vizinhos e na emenda |
| `Movimento(deriva, tremor, alfa, respira, fase)` | o que o motor mexe por tick: posição (fração de px) e alfa |
| `Camada(nome, quadros, tempo=2, plano, pos, mistura, mov, surto_incha, esconde, ...)` | um `Explod` em loop |
| `Particula(nome, quadros, periodo, vida, area, vel, vel_var, grav, escala, giro, ...)` | elos, pedras, notas, ferraduras, lascas, anéis; escala e giro da vida inteira assados em quadros |
| `fumaca_procedural`, `anel_procedural`, `pedra_procedural`, `anel_de_fumaca` | arte por código, para testar antes de a folha existir |
| `Aura.resumo()` | altura, ids, pior caso de `Explod`, e o espalhamento das partículas |

Partículas: a n-ésima peça nasce em `(n * A) mod 1009`, com `A/1009` perto de um irracional diferente por canal (x, y,
velocidade, lado) e por partícula; peças seguidas caem a 24% a 43% da área uma da outra (antes era `GameTime`, e
virava fila). Sem `Random`: o replay sai igual. O relógio das partículas soma `ID * 3`, e os dois lutadores não
soltam peça no mesmo tick.

## O que o motor aceita (IKEMEN GO v1.0.0, lutador `mugenversion = 1.1` sem `ikemenversion`)

Conferido no fonte da tag v1.0.0 (`src/bytecode.go`, `src/char.go`, `src/compiler.go`) e na sandbox.

- A aura roda no **`[Statedef -4]`**: no filme extra ela seguiu andando (posição e animação) em superpausa do outro, na
  superpausa do próprio dono, com o lutador em estado custom do oponente, na intro e na pose de vitória. O `-2` para
  em pausa e superpausa.
- `ModifyExplod` muda `scale`, `trans`/`alpha`, `animelem` e `animelemtime` direto. Para `pos` e `facing` ele exige
  `postype` no mesmo controlador, e o `postype` refaz a posição pelo lutador. A aura manda `postype = p1` a cada
  tick: é isso que faz o `Explod` virar junto.
- O `-4` roda antes do estado do lutador no tick. Uma camada presa (`bindtime = -1`) sobe junto no tick da decolagem
  do pulo sem que `Pos Y` ou `Vel Y` avisem. Por isso a camada `"chao"` nasce **solta** (`bindtime = 0`): o
  `ModifyExplod` a recoloca a cada tick na posição do lutador menos a altura, e ela fica no chão. Custo: em x ela
  segue o lutador com 1 tick de atraso.
- `alpha` vale de 0 a 255 e só com `trans` junto. `anim` não troca por `ModifyExplod` sem `ikemenversion`.
- `interpolation.alpha` do `Explod` multiplica o alfa de partida: não serve para sumir. O fade das partículas vai no
  `.air` (`AS..D..` por elemento, com `Interpolate Blend`). Escala e ângulo **não** vão pelo `Interpolate`: girar e
  escalar no motor, em tela de 1280, quebra a grade e vira mosaico (visto pelo cético na nuvem de 2026-11-11).
- Camadas com o mesmo `tempo` trocavam de quadro todas no mesmo tick. Cada camada nasce com `animelemtime` diferente,
  e todo tick tem desenho novo.
- HUD: o motor desenha vida, poder, retrato, nome e relógio atrás dos lutadores e dos `Explod`, a não ser que o
  elemento tenha `layerno = 1`. O `gerar_layout.py` põe isso em todos (`hud_por_cima`). Efeito colateral: lutador
  que pula alto passa por trás das barras.

## Teste e aceite

```bash
python ferramentas/gerar_teste_aura.py                         # chars/teste_aura (só teste: fora do select.def)
python ferramentas/filmar_aura.py --saida PASTA                # sandbox, 10 s: luta.mp4 + aura_log.txt (por tick)
python ferramentas/medir_aura.py PASTA                         # medidas.txt, 2 s quadro a quadro, tiras; sai 1 se falhar
python ferramentas/filmar_aura.py --roteiro extra --saida P2   # 2 rounds: superpausa, estado custom, pulo, KO, round 2
python ferramentas/medir_aura.py P2 --extra
# lutador de verdade (aura do aura.py no .cns, Despertar por var(20)): os dois lados são ele, na cor 1
python ferramentas/filmar_aura.py --lutador pengaro --saida P3
python ferramentas/filmar_aura.py --lutador pengaro --sem-aura --saida P4   # mesmo roteiro, aura desligada
python ferramentas/medir_aura.py P3 --referencia P4   # corpo medido contra o despertado sem aura, não contra a base
python ferramentas/filmar_aura.py --lutador pengaro --roteiro luta --saida P5   # perto, super 3000 de verdade, pulo,
                                                      # fim natural do Despertar do P2, KO e pose de vitória (olhar)
```

O P1 usa a aura "ck" (folhas `fx_paredao`, `fx_aura`, `fx_fumaca` + névoa por código) e o P2 a "sombra" (toda por
código). Roteiro padrão: liga aos 60 ticks, surta aos 220 e 390, vira os dois aos 320, desliga aos 480 e repete o
especial sem aura aos 545 (referência do corpo). O `filmar_aura.py` acusa pane do motor (Lua que não carrega,
linha `ERRO` no log) em vez de segurar a sandbox até o fim da espera.

Os números de aceite (E1 a E16) estão na seção 2.2 do [`bosses_kit.md`](bosses_kit.md). Filmes de 2026-11-11, depois
do retoque da revisão cética (código final):

| Aceite | Limite | ck / sombra |
|---|---|---|
| mesmo quadro da camada | ≤ 3 ticks | 2 / 2 |
| escala e ângulo do motor no loop | 1 e 0 | 1 e 0 em todas as camadas |
| mudança entre quadros do vídeo no loop (p95/mediana; maior/mediana; parados) | ≤ 2,5; ≤ 3,5; 0 | 1,99; 2,18; 0 / 2,04; 2,22; 0 |
| volta do loop | ≤ 2,5x a mediana | 1,18x / 0,82x |
| surto: maior salto contra os 8 quadros vizinhos | ≤ 2,5x | 1,63x / 1,86x |
| corpo legível, loop (tronco / pernas / pés) | ≥ 97 / 95 / 60% | 99,9 / 99,8 / 96,4% e 100 / 100 / 92,6% |
| corpo legível, surto (tronco / pernas / pés) | ≥ 97 / 95 / 60% | 99,9 / 99,9 / 93,4% e 100 / 100 / 91,7% |
| HUD (vida, retrato, nome, poder) | ≤ 0,5% muda | 0,00% nas 8 caixas |
| `Explod` vivos (loop calmo / pior tick) | ≤ 30 | 14 / 22 e 18 / 29 |
| virada | apaga e troca 3 a 8 ticks depois | 5 ticks / 5 ticks |
| desligar | 0 `Explod` no fim | 0 / 0, em 35 ticks |
| roteiro extra | superpausa, custom, pulo, vitória, round 2 | tudo OK: posição e animação andam em superpausa (dos dois lados) e em estado custom; anel no chão no pulo de 84 px (desvio 0,00 px); vencedor com a aura nos 261 ticks do fim do round, pose de vitória inclusa; derrotado apaga em 36 ticks; 0 Explod antes da intro do round 2; aura inteira na intro do round 2 |

Limites do teste: o gravador da sandbox repete e pula quadros (os repetidos saem da conta); a medida de mudança é
feita na faixa acima das cabeças, porque embaixo o corpo de teste ginga. O surto foi medido primeiro contra a mediana
do trecho (≤ 3,0x) e falhou no P2 (3,6x a 3,8x): o maior salto é o tremor de propósito do surto (a camada anda ±1,2 px
por tick), e a régua passou a ser o salto contra os vizinhos. Isso é régua mudada depois de ver o dado; fica dito.
A régua do corpo no loop também mudou: comparava
com o quadro de 48 ticks antes pela conta tick → quadro, e no começo do vídeo o gravador ainda não está no passo
(caía num quadro de antes do `PosSet`, com o lutador em outro lugar: 12% igual, falso); agora vale o quadro sem aura
que mais bate no tronco. A tela mostra só até 160 px acima do chão: a aura de 2,1x o lutador passa do topo (por trás do HUD).

**Não testado:** `mistura="soma"`, golpe recebido com dano, `surto_incha` negativo, a camada de chão com o lutador
andando (o atraso de 1 tick em x só foi lido no log, com o lutador parado), e a aura num lutador de verdade
(paleta de 255 cores disputada com as faíscas). Os cinco dicionários do kit só foram montados no host, com arte de
mentira.
