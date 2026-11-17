# Ferramenta de pixel do NazaFight (`ferramentas/pixel/`)

Pedido do Breno na #51 (2026-11-15): parar de regenerar quadro no ChatGPT e corrigir a anatomia **à mão, quadro a
quadro**, com uma ferramenta nossa que o Claude consegue usar por comando. Tudo pinta só com a paleta do lutador, grava
no mesmo formato que os conversores (`converter_*.py`) gravam (PNG RGBA de alfa seco, mesma tela e mesmo eixo) e guarda
histórico para desfazer.

## Arquivos

| Arquivo | O que faz |
|---|---|
| `pixel.py` | a linha de comando (ver, medir, pintar, copiar/colar, mover, escalar, desfazer, vídeo) |
| `quadros.py` | onde fica cada lutador, qual é a pose parada de cada forma e qual é a paleta |
| `reguas.py` | as réguas de anatomia que o robô também usa (cabeça, corpo, membro sobrando, cor fora da paleta) |
| `cores.py` | régua de cor contra o parado (deriva, salto, troca entre ações) e o conserto de tom / paleta única |
| `remendar_sff.py` | troca no .sff do jogo só os sprites dos quadros consertados, sem regerar o lutador |
| `sequencia.py` | régua de quadro intruso: peça que some e volta / quadro de outro desenho no meio da ação |
| `tira_jogo.py` | tira de cada ação como o jogo mostra (sprites do .sff na ordem do .air), para conferir com os olhos |
| `achar_quadro.py` | de qual quadro (pasta/ação/NN) saiu um sprite do .sff |
| `sprite_sff.py` | tira um sprite do .sff para PNG e põe de volta consertado (Gutto e Raiclaven, corpo HD do Blender) |

Precisa de `numpy`, `Pillow` e `opencv-python-headless` (`pip install opencv-python-headless`); o MP4 usa o `ffmpeg`.

## Endereço de quadro

`LUTADOR/ACAO/NN`, por exemplo `hazaki/agachado/03`, `diabo/d_rasteira_arco/04`, `ck/e_soco/02`.

| Lutador | Pasta | Parado (régua) |
|---|---|---|
| hazaki | `sprites/hazaki/quadros_arcade_hd` (3x) e `quadros_arcade` (1x, `--1x`) | `parado` |
| diabo | `sprites/hazaki/diabo_terno` (recortado na figura) | `d_parado` |
| ck | `sprites/ck/quadros_arcade_hd` e `quadros_arcade` | `referencia_ginga` / `e_referencia_ginga` |
| pengaro | `sprites/pengaro/quadros_arcade_hd` e `quadros_arcade` | `ginga` / `e_ginga` |
| gutto | `sprites/gutto/quadros` | `ginga` / `ginga_endiabrada` |
| raiclaven | `sprites/raiclaven/quadros` | `ginga` |

No Hazak, CK e Pengaró o 3x é o 1x ampliado 3 vezes: o `escala` faz a conta na grade do 1x e o `sincroniza` refaz o 1x
a partir do 3x depois de qualquer mexida. Os quadros do Diabo são guardados recortados na figura (o fundo da tela é o
chão); a ferramenta dá folga em volta enquanto edita e recorta de novo ao gravar, então dá para colar e esticar para
fora da tela sem pensar nisso.

## Comandos

`python3 ferramentas/pixel/pixel.py --help` mostra tudo. Os principais:

```
# ver e medir
pixel.py ver hazaki/agachado/03 --zoom 6 --regiao 450 400 650 670   # ampliado, grade, papel vegetal, linhas do parado
pixel.py tira hazaki/rasteira                                        # quadros lado a lado com régua e avisos
pixel.py mede hazaki --json docs/anatomia-51/reguas/hazaki.json     # régua em todas as ações do lutador
pixel.py compara hazaki/rasteira --ref HEAD                          # antes (git) e depois
pixel.py anima diabo/d_rasteira_arco --saida rasteira.mp4            # GIF ou MP4

# pintar (só cores da paleta: nome, #índice ou hex; `pixel.py paleta Q` lista)
pixel.py pinta Q COR x,y x,y ...
pixel.py linha Q COR x0 y0 x1 y1 --grossura 2
pixel.py ret Q COR x0 y0 x1 y1 [--vazio]
pixel.py balde Q COR x y
pixel.py troca Q COR_DE COR_PARA [--regiao x0 y0 x1 y1]
pixel.py apaga Q x0 y0 x1 y1 [--so COR]

# pedaços e proporção
pixel.py copia Q x0 y0 x1 y1            # vai para a prancheta (~/.nazafight/pixel/prancheta.png)
pixel.py cola Q2 x y [--espelha] [--gira 15] [--escala 0.8] [--por-baixo]
pixel.py move Q x0 y0 x1 y1 DX DY [--gira G] [--espelha] [--escala F]   (ou --poli "x,y x,y ..." no lugar da caixa)
pixel.py estica Q x0 y0 x1 y1 X1 Y1 --empurra   # alonga o pedaço (canela) e leva junto o que vem depois (sapato)
pixel.py remenda Q x0 y0 x1 y1         # tapa os buracos com as cores em volta, na paleta
pixel.py recolore Q --matiz 160 210 --para pele   # troca uma família de cor por outra, claro vira claro
pixel.py escala Q 1.20                  # figura inteira em volta do eixo (pés do parado); cresce com Scale2x, sem borrar
pixel.py sincroniza hazaki/rasteira     # 1x a partir do 3x

# histórico
pixel.py historico 20
pixel.py desfaz [Q]
```

O histórico e as cópias de cada quadro antes de cada mexida ficam em `~/.nazafight/pixel/historico/`.

## Réguas (`reguas.py`)

| Régua | Como mede | Aviso |
|---|---|---|
| Escala da cabeça | acha a cabeça do parado (faixa de cima, 13% da altura) no quadro, testando tamanhos de 80% a 125% e giros; normaliza pela mediana do parado | passou de 3% |
| Corpo | raiz da área pintada contra o parado (só quando a cabeça não foi medida: agachado tira área de verdade) | passou de 12% |
| Membro sobrando | manchas de pele separadas (mãos, antebraços, rosto) contra o parado | mais que o parado + 1 |
| Cor fora da paleta | pixels com cor que a forma não tem | qualquer um |

**Precisão:** a régua da cabeça acerta bem quando o desenho é o mesmo em outro tamanho (pegou a rasteira do Hazak 18%
menor em todos os quadros, do mesmo jeito). Num quadro redesenhado ou reamostrado a curva fica achatada e a incerteza
sobe para uns 4 a 5%, então trate aviso entre 3% e 6% como "olhar o quadro", não como prova.

## Primeiros resultados (teste 1 da #51)

- **Agachar do Hazak:** passou. Cabeça a 98% do parado em todos os quadros; o pé parece menor só porque a calça cobre.
- **Rasteira do Hazak:** a cabeça estava a 82% em todos os 8 quadros (o golpe inteiro 18% menor). `escala ... 1.20`
  levou para ~98%. O teste não foi gravado no Hazak base porque a #36 vai refazer a forma base inteira; o defeito vai no
  pedido das folhas novas.
- **Diabo:** o "braço a mais" era o antebraço do Hazak (faixa e munhequeira verde-água) que sobrou entre a manga e o
  punho. `recolore --matiz 160 210 --para pele` tirou a munhequeira dos 337 quadros; no parado o antebraço nu virou manga
  (`recolore --matiz 0 45 --regiao ... --para matiz:250-320`). Rasteira (`d_rasteira_arco`): `estica ... --empurra` na
  canela, `move --poli ... --escala 0.78` na mão de apoio, `remenda` nos buracos e `escala 1.07` no golpe inteiro.
  Antes/depois e vídeo em `docs/anatomia-51/teste1/`.
- **Blender (recorte com malha), mesmo quadro:** dá o mesmo resultado na perna, mas a mão velha continua embaixo da nova:
  no recorte cada pedaço precisa virar camada e o que fica atrás precisa ser pintado. Para consertar quadro existente a
  ferramenta de pixel ganha; o Blender serve para animação nova montada de peças (asas, cabelo, casaco).

## Régua de cor (`cores.py`, #51 "cor mudando entre os quadros")

O parado de cada forma vira 14 grupos de cor (k-means em Lab: pele, pele na sombra, roupa, cabelo...). Para cada quadro:

- **deriva**: quanto a média de cada grupo foge da do parado (delta E, média pesada). Até ~3 é o normal de pose
  diferente; acima de 4 já se vê; acima de 6 é aviso.
- **salto**: quanto as cores pulam de um quadro para o seguinte.
- **entra / sai**: a troca parado -> 1º quadro e último quadro -> parado (as trocas entre ações).
- **fora**: fração de pixel longe de qualquer cor do parado (efeito, objeto ou mancha).

```
python3 cores.py diabo                          # mede todas as ações (ou só as que vierem depois)
python3 cores.py gutto lata e_bicicleta --tom   # grava: puxa o tom de cada grupo ao do parado (desenhos e meio/)
python3 cores.py diabo --consertar              # grava: tom + paleta única da forma (cria hazaki/diabo_terno/paleta.json)
python3 remendar_sff.py gutto A.sff B.sff       # troca no .sff do jogo só os sprites dos quadros consertados
```

O conserto só mexe na cor: pose, alfa, tamanho, caixa e tempo ficam. Pixel longe de toda cor do parado (fumaça, fogo,
objeto) não é puxado. `ginga_endiabrada` do Gutto é o parado da forma e_ (não começa com e_).

**Por que o `remendar_sff.py`:** o `gerar_<l>.py` sozinho não refaz os pós-passos que já estão em chars/<l>/ e, no
Gutto e no Raiclaven, o corpo do jogo é o HD do Blender (fora do git). A e B são o lutador gerado nesta máquina com os
quadros de antes e de depois; o sprite que mudou entre eles é trocado no .sff do jogo (igual ao de B quando o do jogo é
igual ao de A; senão, o próprio sprite do jogo passa pelo mesmo conserto de tom). Se outra thread regravar o .sff,
rode de novo em cima do novo.

Resultado na #51 (2026-11-15): Diabo com paleta única de 80 cores (pior ação de 7,5 para 3,9); Pengaró queda,
compasso, parry_baixo e afastar; Gutto armada, derrota, lata, levanta, queda, rolamento e e_baixo_soco, e_bicicleta,
e_bola, e_caneta, e_queda (todos abaixo de 2,6). CK é de paleta indexada e já sai sem deriva. Hazak base só tem
deriva nos objetos e na patroa (não é ele). Raiclaven: defesa, cabecada, armada e pente_combo um pouco acima de 4,
passado para a thread dele. Transformações (despertar, endiabrado) mudam de cor de propósito.

## Membro sobrando: o jab do Pengaró de três braços (#51, 2026-11-15)

O Breno achou o Pengaró segurando a garrafa e dando soco com outro braço por cima. Era `soco/05`: um quadro de outra
geração de desenho (sem a joelheira, pernas em outra pose) com o braço do soco saindo do mesmo ombro da garrafa. A régua
de manchas de pele não pega (tronco nu e braços viram uma mancha só), então a conferência agora tem três passos:

1. `tira_jogo.py L --saida DIR` tira cada ação como o jogo mostra; olhar tira por tira contando cabeça, braços (de qual
   ombro sai cada um), mãos e pernas. Foi assim que saíram os 29 erros da #51.
2. `sequencia.py L` (ou `--todos`) avisa do quadro intruso: grupo de cor do parado (joelheira, cabelo, luva) que está
   nos dois vizinhos e some neste quadro, ou aparece só nele, com o contorno fugindo dos vizinhos. Pegou o jab, a
   lata/05, a ginga/05 e o anda/06 do Pengaró (todos do mesmo desenho sem joelheira). "olhar" é só contorno.
3. `achar_quadro.py L G,I` diz de qual arquivo saiu o sprite; conserta com `pixel.py` (ou `sprite_sff.py` no HD do
   Gutto/Raiclaven) e põe no .sff com `remendar_sff.py`.

```
python3 tira_jogo.py pengaro --saida /tmp/tiras          # ações < 9000; --despertado usa o RemapPreset
python3 sequencia.py --todos                            # quadros intrusos de todos
python3 achar_quadro.py pengaro 91,0                    # -> pengaro/quadros_arcade_hd/soco/05.png
python3 sprite_sff.py extrair gutto 467,0 /tmp/s.png    # ... conserta ... e:
python3 sprite_sff.py repor gutto 467,0 /tmp/s.png
```

`pixel.py sincroniza L/ACAO/NN` agora refaz só aquele quadro do 1x (sem NN, a ação inteira, que regrava os outros 1x).

## Ideias para depois

- Tela para gente (`tela.py` + navegador): tela com lápis, borracha, balde, papel vegetal e salvar, usando as mesmas
  funções.
- Régua de ombro e de mão/pé por pontos marcados no parado (hoje só cabeça e corpo).
- Ligar `mede` no robô (`testar_pengaro.py`) como etapa que falha com cabeça acima de 6%.
- Régua de cor no robô: aviso com deriva acima de 6 fora das cenas de transformação.
