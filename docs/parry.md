# Parry de cada lutador: em cima e embaixo

Pedido do Breno (2026-11-12): o parry deixa de ser a mesma pose para todos, com a faísca pronta do pixelfx (círculo preto
com raios, que parecia uma rede de futebol). Cada lutador ganha um parry **seu**, em duas versões:

| Parry | Comando | Pega | Estado |
|---|---|---|---|
| **Em cima** (alto) | → + c | golpe em pé e golpe aéreo (`reversal.attr = SA, NA, SA, HA`) | 760 (postura), 761 (acertou) |
| **Embaixo** (baixo) | ↓ + c | golpe agachado, rasteira (`reversal.attr = C, NA, SA, HA`) | 764 (postura), 765 (acertou) |

- Errar o tipo é punido. Parry em cima não pega rasteira, e parry embaixo não pega pulo nem golpe em pé.
- A janela, o congelamento e a abertura do oponente (estado 762) continuam como hoje.
- **Forma base:** parry **engraçado**, a resenha de cada um.
- **Forma endiabrada:** parry **foda**, que mostra o poder do Despertar e usa a aura do lutador
  ([regra da aura](regras-dos-lutadores.md)).
- Cada parry tem a **faísca própria** do lutador, na cor da paleta dele, e nunca a faísca pronta do pixelfx.
- **Folha:** 8 quadros, magenta, estilo arcade, em `sprites/<lutador>/quadros/folhas_arcade/parry_alto.png` e
  `parry_baixo.png` (endiabrado: `e_parry_alto.png`, `e_parry_baixo.png`).
  - Quadros 1–3 são a postura do parry: a janela, segurando.
  - Quadros 4–8 são o "acertou": a reação, que é onde mora a piada (base) ou o poder (endiabrado).
  - Depois do conversor, gere o gêmeo 3x ([regra da alta resolução](regra-alta-resolucao.md)).

## Forma base: os parries engraçados (feitos nesta rodada)

| Lutador | Em cima | Embaixo |
|---|---|---|
| **Pengaró** | Ele levanta a **garrafa de whisky** como escudo: o golpe bate na garrafa com um "tlim". Ele olha a garrafa, vê que não quebrou, dá um beijo nela e um gole de comemoração. | **Negativa** da capoeira: deita de lado no chão quase dormindo, a rasteira passa por cima, e ele levanta brindando com a garrafa. |
| **Hazak** | Segura o golpe com **dois dedos**, cara de tédio, e balança o dedo da outra mão dizendo "não, não". | Pula a rasteira com os joelhos encolhidos, cai fazendo pose de karatê exagerada e pisca para a câmera. |
| **CK** | **Pêndulo exagerado**: curva o corpo para trás quase até o chão (as luvas quase encostam), o golpe passa, ele volta rindo e ajeita o boné. | Dá **pulinhos de boxeador** em cima da rasteira, como quem pula corda, e manda um beijinho com a luva. |
| **Gutto** | Bloqueia com a **canela** levantada (muay thai), o golpe bate e ele **relincha** igual cavalo, sacudindo a cabeça. | Pulo de **coice**: salta com os dois pés juntos por cima da rasteira e cai batendo o pé no chão como casco, bufando. |
| **Raiclaven** | **Prende o golpe entre as lâminas** da tesoura aberta, segura um instante e "apara" a ponta: corta um fiozinho de cabelo no ar e sopra. | Gira no lugar como **cadeira de barbeiro**, levantando os pés, a rasteira passa por baixo, e ele para penteando o cabelo. |

Faísca de cada um, no acerto do parry:
- **Pengaró:** brilho âmbar de whisky.
- **Hazak:** estalo branco e laranja do debrum.
- **CK:** estrelinha vermelha da luva.
- **Gutto:** poeira e brasa vermelha.
- **Raiclaven:** faísca prateada de lâmina.

## Forma endiabrada: os parries foda (para o Alisson fazer)

Mesmos comandos e estados (`e_parry_alto` e `e_parry_baixo`). O desenho é na forma endiabrada de cada um e usa a aura.

| Lutador (forma) | Em cima | Embaixo |
|---|---|---|
| **Pengaró** (endiabrado, boss) | As **sombras** saem das costas e seguram o punho do oponente no ar. Ele nem se mexe, só ergue o olho violeta, e a corrente partida estala. A faísca é violeta-escura. | Afunda na **própria sombra** no chão e a rasteira passa no vazio. Reaparece em pé atrás da fumaça violeta, de braços cruzados. |
| **Hazak** (Diabo Loiro de terno) | **Abre a maleta** na frente do golpe como escudo: o golpe bate e notas de dinheiro voam. Ele fecha a maleta devagar e ajeita a gravata. A faísca é laranja-ouro. | Bate o pé no chão e uma **chama laranja-ouro** sobe em anel: a rasteira é empurrada para trás. Ele não sai do lugar e só ajeita o chapéu. |
| **CK** (Modo Ratão) | O golpe chega e ele **some na fumaça** do beck, cambaleando. Reaparece do lado rindo, com o caco de garrafa apontado para o oponente. A faísca é fumaça cinza-esverdeada. | Desliza no chão no **passinho do baile**, chinelo raspando, por baixo da rasteira, e levanta dando um gole na garrafa quebrada. |
| **Gutto** (demônio cara de cavalo) | **Empina** como cavalo nas patas de trás: o golpe bate no peito em brasa e não faz nada. Ele bufa fogo pelas narinas. A faísca é brasa vermelha. | **Coice de casco** no chão: rachadura em brasa e onda de choque, e a rasteira é jogada para longe. Ele relincha. |
| **Raiclaven** (Cientista Louco ou Surto de Tesoura, o que estiver valendo) | **Cliente Zero** (a mulher na corrente) entra na frente e segura o golpe pelos braços. Ele nem olha, anotando numa prancheta. A faísca é prata e verde de laboratório. | Uma **cobaia** sai do chão e trava a perna do oponente. Ele dá um passo para trás e ajusta os óculos. |

Antes de desenhar, confira com a ficha do lutador (`docs/fichas/<lutador>.md`) se a forma endiabrada dele mudou.
Siga as regras de conteúdo do jogo: nada de deficiência, de gente real nem de marca nova sem pedido do Breno.
