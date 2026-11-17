# Diabo Loiro demônio, sem maleta (issue #47)

Pedido do Breno em 15/11 (16:58Z e 17:00Z), aprovado às 19:23Z (comentário 6899928948). O Diabo vira um demônio
descontrolado: sem maleta, chapéu e sobretudo, com garras, investidas, voo e fogo das trevas. As asas ficam. Todos os
golpes são próprios, nada do Hazak normal: 16 normais, 4 correntes, 4 especiais (1 projétil), kombo, super e
agarrões (37 folhas no total, com as 3 dos agarrões). A lista aprovada está na proposta da #47 (comentário 6898251397).

Ferramenta: `ferramentas/diabo_demonio.py`.

```
python3 ferramentas/diabo_demonio.py --fila                 # pedidos das 34 folhas (fila.json)
python3 ferramentas/diabo_demonio.py --pedido NOME          # pedido completo (chat novo, com o conceito anexo)
python3 ferramentas/diabo_demonio.py --seguinte NOME        # pedido curto para o mesmo chat
python3 ferramentas/diabo_demonio.py [NOME ...]             # folha -> sprites/hazaki/diabo_terno/m_NOME/NN.png
python3 ferramentas/diabo_demonio.py --contato SAIDA.png NOME ...   # Hazak em cima, demônio embaixo
python3 ferramentas/gerar_hazaki.py                         # liga tudo no jogo (chama o diabo_loiro no fim)
```

## Como entra no jogo

| parte | onde |
|---|---|
| folhas (8 quadros, 4x2, Gemini/ChatGPT) | `sprites/hazaki/quadros/folhas_demonio/NOME.png` |
| quadros no 3x | `sprites/hazaki/diabo_terno/m_NOME/` (escala única: o parado do demônio fica com 1,08 da altura do Hazak em pé; paleta do Diabo pelo `cores.py --consertar`) |
| básicos (parado, anda, pulo, defesa, apanha...) | `diabo_terno.FOLHA` troca a pasta `d_*` pela `m_*` assim que ela existe (`BASICOS`) |
| golpes próprios | estados 4200-4699, sprites no grupo 60000 + estado, caixas medidas no desenho (`GOLPES`, `_caixas`) |
| Cobrança das Garras | os estados 1660/1661 de sempre, com a arte `m_cobranca_garras` (investida nos quadros 2 a 4) |
| rotas | no fim do `[Statedef -1]`, com `var(20) > 0`; os golpes do Hazak ganham `var(20) <= 0` (`bloquear_base`) |
| agarrões (Garras no Pescoço, Arrasta pro Inferno, Pegada das Trevas) | folhas `agarrao_abraco/perna/cutucao` daqui, com o quadro k no papel do quadro k da folha do Hazak (`BASICOS`); tempos e caixas do `agarrao_mk.PROPRIOS["hazaki"]`; fogo do `diabo_loiro.agarrao_do_diabo`; quem filma e posta na #45 é a thread dos agarrões |
| pancadas extras da porrada | `QUADROS_EXTRAS`: o desenho do Hazak (jab, cruzado, cotovelada...) vira um quadro de preparo ou batida do `m_pe_maos`, `m_pe_pes` ou `m_agachado_maos` |
| reação de agarrado | `vitima_agarrado` -> `m_apanha`, `vitima_arremessado` -> `m_queda` |

Os golpes que ainda não têm folha não saem na forma (o botão não faz nada): o jogo só vai para a `mugen` com as 37
folhas prontas, o robô passando e o vídeo na #47.

## Situação (17/11)

- **Arte:** desde 17/11 a thread do boneco de peças (branch `claude/project-thread-46qshe`) faz toda a arte do
  demônio pelo método novo (kit de peças + poses por código, zero erro de animação): refaz as 26 folhas e faz as 11
  que faltam, direto em `sprites/hazaki/diabo_terno/m_NOME/00..07.png`, com o quadro k no papel do quadro k do
  `FOLHAS_DEMONIO`. Quem mudar o papel de um quadro avisa a outra thread.
- **Motor: completo.** Toda a lista aprovada já está no `diabo_demonio.py`, e cada golpe liga sozinho quando a pasta
  `m_` dele aparece (`disponiveis()` e `especiais()`):

| golpe | estados | comando | folha |
|---|---|---|---|
| 8 normais em pé e agachado | 4200-4203, 4400-4403 | x y a b, ↓ | pe_maos, pe_pes, agachado_maos, agachado_pes |
| 4 no ar | 4600-4603 | x y a b no ar | ar_maos, ar_pes |
| Martelo Infernal (por cima), Estocada, Chicote de Rabo, Mordida | 4210-4213 | → x, → y, → b, ← y | direcionais_a/b |
| Fúria das Garras, Dilacerar (queima), Dança do Rabo, Pisoteio (por cima) | 4301-4333 | x x x x, y y y y, ↓a a a a, b b b b | pe_*, direcionais_b, fins_maos/pes |
| Banquete do Diabo (kombo) | 4200 → 4301 → 4211 → 1661 | x, x, → y, ↘ b | |
| Bola das Trevas (reta / arco) | 4500/4501, projétil 4580, carga 4582 | ↓↘→ x / y | bola_trevas + Blender `d47_poder`, `d47_carga` |
| Voo Infernal (paira, soco mergulha) | 4510-4514 | ↓↓ a / b | voo |
| Rasgo Ascendente (antiaéreo, 2 acertos) | 4520-4522 | →↓↘ x / y | rasgo |
| Juízo Infernal (super, 1 estoque) | 4650-4654, vítima 4660/4661 | ↓↘→↓↘→ x / y | juizo_a, juizo_b |

- **Especiais no jogo com arte de verdade (17/11):** `m_bola_trevas`, `m_voo`, `m_rasgo`, `m_juizo_a` e `m_juizo_b`
  feitas no boneco de peças por esta thread (`ferramentas/kit_diabo_especiais.py`, lido pelo fim do `kit_diabo.py` da
  thread da arte; só `TROCA`: poses inteiras da folha-modelo, giradas no ar, e golpes/guarda do kit). Robô de defeitos
  40/0, robô de luta 327/0. Vídeo: `video/especiais-arte.mp4` (Bola, Voo, Rasgo e Juízo), quadros em
  `video/juizo_arte.jpg`. Faltam as 6 folhas da thread da arte (ar_maos, ar_pes, direcionais_a/b, fins_maos/pes), que
  ligam o resto dos golpes quando entrarem.

  A Rajadona de Ki das Trevas (→← soco, `fb_x`) continua como o poder de longe da forma, como nos outros despertados.
- **Teste sem a arte:** `NAZA_DEMONIO_PROVISORIO=1 python3 ferramentas/gerar_hazaki.py` usa uma folha parecida no
  lugar da que falta (`PROVISORIO`), só para o robô. Nunca vai para a `mugen` assim. O robô pula sozinho o roteiro
  de golpe que não está no .cns (`@DEMONIO@` no `testar_pengaro.py`). Para pular, o robô usa o `T_pulo` (o holdup do AssertCommand
  não pula).

## Lições

- Ao fechar o turno do ChatGPT, limpe a caixa de texto: um rascunho do Diabo que ficou lá foi enviado junto no
  primeiro pedido do turno seguinte (16/11). O `__envia` só escreve o pedido quando a caixa está vazia.

- O Gemini repete a mesma pose se o pedido não insistir: o `SEGUINTE` pede poses "clearly DIFFERENT".
- O auditor de golpes (`auditar_golpes.forca`) tratava todo estado 3000+ como super e esticava o preparo do Arranhão
  para 10 ticks; a faixa 4200-4649 agora conta como golpe normal.
- Revisão independente do código (15/11): faísca nascia fora do corpo do P2 (x agora -10), eixo do golpe pulava para
  o pé de apoio (agora `diabo_terno.ancora_demonio`, mediana do tronco), o `cores.py` pintava o demônio com a paleta
  do terno (agora forma própria `m_` com `paleta_demonio.json`, nascida do `m_parado`), o Afastar do Hazak
  (260/650/720) escapava do bloqueio, o antiaéreo não tinha `NotHitBy A`, a Cobrança das Garras perdia a caixa no
  meio do deslize (ticks próprios `COBRANCA_GARRAS`). Tudo consertado; robô dos cenários do Diabo 100% PASS.
- Progresso para o Breno: `folhas_prontas.png` e `video/demonio-1.mp4` (vitrine; agachado e provocação ainda aparecem
  de sobretudo porque essas folhas ainda não existem).
