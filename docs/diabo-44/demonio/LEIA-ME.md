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

## Situação (16/11, 00:30Z)

- Folhas prontas (16 de 34): parado, anda, pe_maos, pe_pes, cobranca_garras, agachado_maos (Gemini); agachado, pulo,
  defesa, defesa_baixa, apanha, queda, levanta, recuo, provoca, agachado_pes (ChatGPT Plus, turno de 15-16/11).
- Ligados no jogo: Arranhão (x), Garra Cruzada (y), Joelhada Selvagem (a), Coice com Garra (b), Arranhão Baixo
  (↓x), Garra Subindo (↓y), Rabo Rasteiro (↓a, baixo), Varrida de Garras (↓b, derruba) e a Cobrança das Garras
  (↘a/↘b), mais os básicos das folhas prontas.
- Faltam 21 folhas: agarrao_abraco, agarrao_perna, agarrao_cutucao (16/11, combinado com a thread dos agarrões), ar_maos, ar_pes, direcionais_a/b, fins_maos/pes, bola_trevas, voo, rasgo, vira, corrida,
  vitoria, intro, derrota_sirene, parry_alto, parry_baixo, juizo_a, juizo_b. Próximo turno do ChatGPT
  (`imagens/fila-chatgpt.md`).
- ChatGPT: o `gpt_demonio.js` (`ferramentas/chatgpt_demonio.js`; troque o commit na constante C e os pedidos) anexa o conceito e a folha
  do parado do raw do GitHub, manda o pedido completo na 1ª e o `--seguinte` nas outras, e o `__cap` mostra a imagem
  reduzida a 1024 px para o zoom [0,0,628,420] do print. A escala sai igual à do Gemini (altura ~2% menor).

## Lições

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
