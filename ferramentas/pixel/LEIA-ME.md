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
pixel.py move Q x0 y0 x1 y1 DX DY [--gira G] [--espelha]
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
- **Diabo:** ver `docs/anatomia-51/`.

## Ideias para depois

- Tela para gente (`tela.py` + navegador): tela com lápis, borracha, balde, papel vegetal e salvar, usando as mesmas
  funções.
- Régua de ombro e de mão/pé por pontos marcados no parado (hoje só cabeça e corpo).
- Ligar `mede` no robô (`testar_pengaro.py`) como etapa que falha com cabeça acima de 6%.
