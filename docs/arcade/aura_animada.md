# Aura animada do Despertar

Sistema único para a aura de todo lutador despertado (regra da seção 4 de
[`regras-dos-lutadores.md`](../regras-dos-lutadores.md): aura é efeito à parte, por `Explod`). Fica em
[`ferramentas/aura.py`](../../ferramentas/aura.py). Nada na aura fica parado: os quadros do desenho andam de 2 em 2
ticks, e entre um quadro e outro o motor mexe cada camada a cada tick (escala, posição, giro, alfa).

## Como um gerador usa

```python
import aura
F = RAIZ / "sprites/ck/quadros/folhas_arcade"
coluna = aura.alongar_loop(aura.enquadrar(aura.recortar_folha(F / "fx_aura.png"), altura=236), total=28)
AURA = aura.Aura("ck", ligada="var(20) > 0", surto="StateNo = [1000, 3999] && Time = 1", base=9300, camadas=[
    aura.Camada("coluna", coluna, plano="tras", mov=aura.Movimento(pulso=(0.05, 0.07), deriva=(3, 4), balanco=2.5)),
    aura.Camada("pes", coluna, plano="frente", escala=(0.5, 0.2), mov=aura.Movimento(alfa=0.5)),
], particulas=[aura.Particula("anel", aura.anel_de_fumaca(), periodo=14, vida=46, vel=(0, -1.5), escala=(0.8, 2))])
AURA.registrar(sprites)        # quadros no .sff: grupos 9300, 9301, 9302 (um por camada e por partícula)
air += AURA.air()              # [Begin Action 9300] ...
cns_menos_2 += AURA.cns()      # controladores do [Statedef -2], depois da contagem do Despertar
```

- `ligada` é a condição do `.cns` que vale enquanto o Despertar dura. A aura entra em 26 ticks (cresce dos pés e
  ganha alfa), sai em 34, e os `Explod` são removidos quando o fade chega a zero, fora do round e na morte.
- `surto` é a condição que dispara o surto (ou `AURA.disparo_surto()` dentro do estado do especial): por uns 30
  ticks a aura incha, treme, o tempo dela corre 2,6x, a animação anda 1 quadro por tick e as partículas nascem 3x mais.
- Variáveis: só `map` (`au_<nome>_f`, `_e`, `_s`, `_k`, `_t`). Não gasta `var()` do lutador.
- Números: ações, ids de `Explod` e grupos de sprite de `base` a `base + camadas + partículas - 1`.
- `plano`: `"tras"` (sprpriority -6...), `"chao"` (-9..., fica no chão quando o lutador pula e some com a altura) e
  `"frente"` (5...). Espelhar uma camada: `escala=(-0.7, 0.8)` (o motor aceita escala negativa).
- Arte guardada: `aura.salvar_quadros(quadros, pasta)` e `aura.ler_quadros(pasta)` evitam refazer o fluxo óptico.

## O que cada peça faz

| Peça | Para quê |
|---|---|
| `recortar_folha(caminho, quadros=8, fundo=None, limiar=90)` | folha em verde `#00FF00` ou magenta vira quadros RGBA; borda corroída 1 px e repintada com a cor de dentro (franja zero) |
| `enquadrar(celulas, altura= ou largura=, ancora="base")` | mesma caixa para todos os quadros, na escala do jogo |
| `alongar_loop(desenhos, total=24, loop=True, metodo="fluxo")` | 8 desenhos viram 16 a 32; `"fluxo"` (fumaça, fogo), `"mistura"` (luz que pisca), `"dissolve"` (raio). **Nunca em corpo** |
| `medir_loop(quadros)` | mudança entre quadros vizinhos e na emenda |
| `Movimento(...)` | pulso da escala, deriva, tremor, giro, balanço, alfa que respira, fase |
| `Camada(nome, quadros, tempo=2, plano, pos, escala, mistura, mov, ...)` | um `Explod` preso ao lutador |
| `Particula(nome, quadros, periodo, vida, area, vel, vel_var, grav, escala, giro, ...)` | elos, pedras, notas, ferraduras, lascas, anéis |
| `fumaca_procedural`, `anel_procedural`, `pedra_procedural`, `anel_de_fumaca` | arte por código, para testar antes de a folha existir |

`alongar_loop` reparte os quadros do meio pelo tamanho de cada mudança (velocidade igual o loop todo), faz entremeio
também do último para o primeiro desenho e, se a folha não fecha (a volta muda mais de 2,2x a mediana), usa vai-e-vem.
Os quadros do meio são levados para as cores dos desenhos: sem degradê novo, sem pontilhado.

## O que o motor aceita (IKEMEN GO v1.0.0, lutador `mugenversion = 1.1` sem `ikemenversion`)

Conferido no fonte da tag v1.0.0 (`src/bytecode.go`, `src/char.go`, `src/compiler.go`) e na sandbox.

- `ModifyExplod` muda `scale`, `angle`, `trans`/`alpha`, `animelem`, `animelemtime` e `sprpriority` direto. Para
  `pos`, `vel`, `accel` e `facing` ele exige `postype` no mesmo controlador, e o `postype` zera `vel`/`accel` e
  refaz a posição pelo lutador. A aura manda `postype = p1` a cada tick: é isso que faz o `Explod` **virar junto**
  (sozinho, o `Explod` preso guarda o lado em que nasceu).
- `alpha` vale de 0 a 255 e só com `trans` junto. `anim` não troca por `ModifyExplod` sem `ikemenversion`.
- `interpolation.alpha` do `Explod` multiplica o alfa de partida: em mistura normal o destino nunca chega a 255,
  então não serve para sumir. O fade das partículas vai no `.air` (`AS..D..` por elemento, com
  `Interpolate Blend`, `Interpolate Scale` e `Interpolate Angle`), que o motor interpola a cada tick.
- Espelhar por `facing = -1` não se sustenta com `ModifyExplod` (o motor imita um defeito do MUGEN e desfaz o
  espelho quando o lutador olha para a esquerda). Use escala x negativa.
- Camadas com o mesmo `tempo` trocavam de quadro todas no mesmo tick, e o tick seguinte ficava quase parado. Cada
  camada nasce com `animelemtime` diferente, e todo tick tem desenho novo.
- As posições das partículas saem do `GameTime` (sem `Random`): o replay sai igual.

## Teste e aceite

```bash
python ferramentas/gerar_teste_aura.py          # chars/teste_aura (só teste: fora do select.def e do git)
python ferramentas/filmar_aura.py --saida PASTA # Windows Sandbox, 10 s, luta.mp4 + aura_log.txt (motor, por tick)
python ferramentas/medir_aura.py PASTA          # medidas.txt, 2 s quadro a quadro, tiras; sai 1 se algo falhar
```

O P1 usa a aura "ck" (folhas `fx_paredao`, `fx_aura`, `fx_fumaca`) e o P2 a "sombra" (toda por código). O roteiro
liga aos 60 ticks, surta aos 220 e 390, vira os dois aos 320 e desliga aos 480.

| Aceite | Limite | Filme de 2026-11-11 (ck / sombra) |
|---|---|---|
| mesmo quadro da camada | no máximo 3 ticks | 2 / 2 |
| mudança entre quadros do vídeo no loop | percentil 95 / mediana ≤ 2,5; maior / mediana ≤ 3,5; nenhum parado | 1,55 e 1,82 / 1,60 e 2,91; 0 parados |
| volta do loop (último para o primeiro) | ≤ 2,5x a mediana | 1,04x / 1,61x |
| escala por tick | ≤ 3% no loop, 6% no surto, 5% ligando e desligando | 0,4 a 1,1% no loop; até 5,6% no surto |
| camadas fora de fase | correlação da escala < 0,9 em módulo; elementos diferentes ao mesmo tempo | pior par 0,55 / 0,77; 4 de 4 |
| surto | escala passa do máximo calmo; animação a 1 quadro por tick | 1,05 para 1,26 |
| virada | todas as camadas no lado novo | sim / sim |
| franja verde | 0 pixel de `#00FF00` a mais | 0 / 0 |
| corpo na frente | ≥ 80% da pele igual com a aura ligada | 92% / 100% |
| tamanho | aura ≥ 2x o lutador | 251 e 255 px para 111 px (2,26x e 2,30x); na tela ela passa do topo |
| desligar | nenhum `Explod` no fim | 0 / 0, camadas somem em 35 ticks |

Limites do teste: o gravador da sandbox repete e pula quadros (27 repetidos em 390 ticks nesse filme); os repetidos
saem da conta, e por isso o salto vale pelo percentil 95. A medida do vídeo é feita na faixa acima das cabeças,
porque embaixo o corpo de teste ginga. Não foi testado: troca de round, lutador pulando (camada de chão), super
pausa, golpe recebido, e a aura num lutador de verdade.
