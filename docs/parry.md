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

## Pedido para o Alisson: colocar os parries no jogo

As 10 folhas da forma base já estão prontas, em `sprites/<lutador>/quadros/folhas_arcade/parry_alto.png` e
`parry_baixo.png`. São 5 lutadores, 8 quadros, magenta, no estilo arcade, geradas no ChatGPT a partir da `defesa.png`
de cada um. Eu não liguei nada no jogo: é com você.

1. **Converter** cada folha com o conversor do lutador (paleta dele) e gerar o gêmeo 3x
   ([regra da alta resolução](regra-alta-resolucao.md)).
2. **Estados:**
   - 760/761 passam a usar `parry_alto`: quadros 1–3 na postura, 4–8 no acertou.
   - Crie 764/765 para `parry_baixo`, com o comando ↓ + c. Ele não pode pegar a provocação (c) agachado.
   - `reversal.attr`: em cima `SA, NA, SA, HA`, embaixo `C, NA, SA, HA` (tabela acima).
3. **Faísca:** troque o `sparkno = S9204` (a faísca pronta em círculo) pela faísca própria de cada lutador, pequena e
   na cor dele ([regra dos efeitos](regra-efeitos-proporcionais.md)). Nas folhas, o ChatGPT desenhou estrelinhas e um
   coração colados no corpo, nos quadros da piada. Pode deixar, se ficar bom no jogo, ou tirar e fazer como efeito.
4. **Endiabrado:** faça as folhas `e_parry_alto` e `e_parry_baixo` pela tabela abaixo.
5. **Robô:** os testes de parry continuam passando, e acrescente o parry baixo.

## Forma base: os parries engraçados (feitos nesta rodada)

| Lutador | Em cima | Embaixo |
|---|---|---|
| **Pengaró** | Põe a **mão aberta na frente** e segura o golpe **enquanto dá uma golada no whisky**, de olho fechado, sem nem olhar. Depois limpa a boca com as costas da mão (pedido do Breno). | **Negativa** da capoeira: deita de lado no chão quase dormindo, a rasteira passa por cima, e ele levanta brindando com a garrafa. |
| **Hazak** | Segura o golpe com **dois dedos**, cara de tédio, e balança o dedo da outra mão dizendo "não, não". | Pula a rasteira com os joelhos encolhidos, cai fazendo pose de karatê exagerada e pisca para a câmera. |
| **CK** | **Pêndulo exagerado**: curva o corpo para trás quase até o chão (as luvas quase encostam), o golpe passa, ele volta rindo e ajeita o boné. | Sem pular (o Hazak já pula): **levanta o pé** de leve, a rasteira passa por baixo, ele olha a sola do tênis com nojo como quem **pisou em alguma coisa**, raspa o tênis no chão e ri (pedido do Breno). |
| **Gutto** | Bloqueia com a **canela** levantada (muay thai), o golpe bate e ele **relincha** igual cavalo, sacudindo a cabeça. | Sem pular: **checa a rasteira com a canela** (muay thai), nem se mexe, olha a canela com desdém, **assopra** e bufa vapor pelo nariz como cavalo. |
| **Raiclaven** | **Prende o golpe entre as lâminas** da tesoura aberta, segura um instante e "apara" a ponta: corta um fiozinho de cabelo no ar e sopra. | Sem pular: **crava a tesoura no chão** na frente dos pés como uma parede, a rasteira bate nela, ele aproveita e **apara os pelinhos da canela** do oponente, assopra e se penteia. |

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
