# Revisão de todos os golpes (issues #45 e #48)

Feita em 2026-11-14 sobre a `mugen` com os efeitos (#38), os sons (#46) e os agarrões e poderes dos despertados (#47)
já dentro. O Hazak novo (#44) ainda não entrou; quando entrar, a revisão roda de novo nele (as ferramentas abaixo são
pós-passos e refazem tudo sozinhas).

- Vídeo dos agarrões no jogo: [`agarroes.mp4`](agarroes.mp4) (cinco básicos e os três despertados da #47).
- Caixas de golpe antes e depois: [`caixas_antes_depois.png`](caixas_antes_depois.png).
- Medidas golpe a golpe: [`medidas.md`](medidas.md) (`python3 ferramentas/auditar_golpes.py`).

## 1. O que já foi consertado (erro, sem precisar de aval)

Tudo por `ferramentas/legibilidade.py` (golpes) e `ferramentas/agarrao_mk.py` (agarrões). Robô na nuvem depois:
CK 228/0, Gutto 185/0, Hazak 213/0, Pengaró 190/0, Raiclaven 185/0.

| Lutador | O que estava errado | O que foi feito |
|---|---|---|
| Todos | **Agarrão confuso**: quadros de golpes diferentes colados em sequência, o oponente preso na pose de queda no ar, pancadas emendadas sem pausa e uma faísca do tamanho dos dois corpos no final | Pega com a pose de agarrar (ação 800) e volta a ela entre as pancadas; cada pancada prepara (6 ticks), bate com congelamento de 7 ticks, faísca pequena no ponto do contato e tremida leve; o oponente fica **em pé** na pose de quem foi agarrado e reage alto ou baixo a cada pancada, recuando um pouco no tranco; o final prepara 10 ticks, congela 14, treme e arremessa (para frente, ou por cima segurando ←). Vale também para os agarrões dos despertados (#47) |
| Gutto | 136 caixas de golpe passavam até 70 px do pé ou do punho (batia no ar, "encosta longe demais") | Caixa encostada no membro desenhado + 12 px |
| Raiclaven | 167 caixas na mesma situação | Idem |
| CK | 19 caixas | Idem |
| Pengaró | 8 caixas | Idem |
| Todos | Congelamento no contato abaixo do piso em 152 golpes (pancada passava sem "peso") | Fraco 7, forte 11, finalizador e super 14 ticks |
| Todos | Golpe forte e finalizador sem tremida (215 golpes) | Tremida só quando acerta: pequena no forte, maior no finalizador |
| Todos | Reação do oponente que não batia com o golpe (90 golpes: fraco com reação pesada, finalizador com reação leve) | Fraco Light, forte Medium, finalizador Hard (Back/Up quando já era assim) |
| Gutto, Raiclaven | Faísca estourando longe da altura do golpe (20 golpes) | Faísca na altura da caixa de golpe |
| Todos | Preparo curto: 116 golpes pulavam direto para o contato | A pose de carga fica mais tempo até o piso (fraco 3, forte 7, finalizador 10 ticks; no máximo +6), com HitDef, som e efeito andando junto |

Golpes do meio de uma rajada (supers de várias passagens, como o Rapidinho do Hazak) ficaram com o tempo deles.

## 2. Ainda para consertar (pequeno)

| Lutador | Golpe | O que está errado | O que vai ser feito |
|---|---|---|---|
| CK, Gutto, Raiclaven | golpes do despertado (Desp: correntes, kombo, Passo de Sombra...) | caixa passa 14 a 36 px do membro: o desenho do despertado é mais curto que o normal no mesmo quadro | encostar a caixa pelo desenho do despertado (a ferramenta hoje usa o maior dos dois) |
| Gutto | Golpe no ar (610, 611) e Afastar no ar (650) | caixa 30 a 36 px além do pé | idem, caixa por quadro |
| Hazak | Super (3002, 3003, 3201) | contato sem preparo nas passagens | entra junto com o Hazak novo (#44) |

## 3. Golpes sem sentido ou sem graça: para o Breno decidir antes de refazer

O desenho não combina com o nome ou com o que o golpe deveria fazer. Precisa de folha nova (ChatGPT), por isso
fica com o Breno.

| Lutador | Golpe | O que está errado | Proposta |
|---|---|---|---|
| Raiclaven | Tesoura Voadora (→ ↓ + soco) | é um chute alto, não aparece tesoura voando | folha nova: ele gira e arremessa a tesoura, ou salto com a tesoura aberta à frente |
| Raiclaven | Cadeira Giratória (← ↓ + chute) | chute baixo comum, não tem cadeira | folha nova com a cadeira de barbeiro girando, ou trocar o nome para um chute |
| Raiclaven | Próximo! (→ ← + chute: "passa e chuta") | no fim ele não chuta, fica parado de tesoura na mão | folha do chute de saída |
| Raiclaven | Corrente de chute forte, final | levanta a tesoura acima da cabeça e a caixa pega o corpo todo | trocar por um chute forte de verdade |
| Raiclaven | Tesoura Helicóptero (↓ ← + chute) | só a pose de tesoura para cima, sem giro | folha do giro com rastro |
| Gutto | Joelhada Voadora (→ ↓ + soco) | o desenho é um chute alto, não joelhada | usar a joelhada voadora (já existe no clinch) ou folha nova |
| Gutto | Bando de Chutes (super ← → ↓ + soco) | o contato é um soco | sequência de chutes de Muay Thai |
| Pengaró | Mão de Chimpá / Mão Pesada (↓ → + soco) | o desenho é um chute alto, não tem mão | folha do tapão de mão aberta |
| CK | Chute da Corrente (Modo Ratão) | é um soco agachado; a caixa fica no pé | trocar o nome ou fazer o chute |
| CK | Garrafa Voadora (Modo Ratão) | a garrafa não aparece na mão antes de sair | desenhar a garrafa no quadro de arremesso |
| CK | Palma Torta (Modo Ratão) | usa o quadro da Tragada (nuvem roxa), nada de palma | folha da palmada |
| CK | Mão de Chão Possuída (Modo Ratão) | é o uppercut normal, não vai ao chão | folha da mão no chão puxando a sombra |
| Todos | Agarrões | a mão ainda não segura o oponente de verdade: a pose de agarrar é a mesma da tentativa | folha própria de agarrão (pegada e pancada segurando) por lutador |

O Hazak (Pedra, Bola de ki, Diabo Loiro) está sendo refeito na #44 e entra aqui depois.
