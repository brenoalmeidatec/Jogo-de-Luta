# Aplicar o estudo de anatomia dos golpes nos lutadores

Pedido do Alisson em 2026-11-17: ler o estudo novo do Breno, [`estudo-anatomia-golpes.md`](estudo-anatomia-golpes.md)
(commit `21d4e7b0`), e dizer o que cada lutador muda. Este arquivo não mexe em sprite; é o guia de aplicação.

## O que o estudo traz de novo, em uma tela

O método continua o mesmo: **boneco de peças com corpo firme e vida** (kit em `sprites/<lutador>/pecas/`,
`ligar_pecas.py`, `pele_pecas.py`, `encolher_sff.py`, robô `firme.py`, regra 7.2.1). O estudo **não troca ferramenta**:
ele diz **como posar** cada pose-chave para o golpe sair com o corpo certo. São três coisas novas:

1. **12 leis do corpo** (valem para todo golpe). As que mais pegam no nosso jogo:
   - força sobe do chão: quadril e tronco se mexem **antes** do braço; o membro que bate é o último a sair e a chegar;
   - o peso vai para o lado do golpe (direto: ~60% no pé da frente; gancho gira no lugar; uppercut sobe);
   - joelhos sempre dobrados (perna reta só no apoio do chute alto);
   - a mão que não bate fica na guarda ou jogada para trás, **nunca na frente do golpe**;
   - alcance vem do ombro andando 10 a 20 px (3x) e do tronco girando, **nunca de esticar a peça**;
   - chute de perna dobrada tem **câmara** (joelho sobe primeiro, canela abre depois, volta pela câmara);
   - no chute circular e no direto o **pé de apoio gira** (calcanhar para o oponente);
   - a cabeça olha o alvo o golpe inteiro e assenta depois;
   - teste da silhueta preta: tem que dar para saber o golpe só pelo contorno.
2. **Perto e longe da câmera** (a causa das "duas pernas direitas"): "frente" é o lado do oponente, mas na guarda aberta
   **o lado da frente é o lado longe**. Membro longe nasce **atrás** do tronco e da faixa; membro perto, **na frente**.
   A ordem `CAMADAS` do kit é a do parado; **em golpe a camada muda por pose** (o montador já faz isso: "camada" e
   "esconder nesta pose"). Pé e mão são espelhados (dedão do lado de dentro): o pé que chuta não pode ser cópia do pé de
   apoio. Tem tabela de limites de junta (cotovelo ~145°, joelho ~140°, coxa esticada no máximo ~90° sem a bacia girar).
3. **Receita pose a pose** com ticks para guarda, jab, direto, gancho, uppercut, chute frontal, circular (martelo), alto,
   baixo, rasteira, giros de capoeira, cabeçada, cotovelada, joelhada e golpes no ar, e uma **lista de 12 conferências**
   antes de gravar cada pose (Parte 4 do estudo).

## O que muda em relação ao que a gente fazia

| Antes | Agora |
| --- | --- |
| Pose-chave posada no olho, "corpo inteiro acompanha" | Mesma ideia, mas com número: giro do tronco por golpe (jab 10-15°, direto 45-60°, gancho 45-60° ao contrário), ombro 10-20 px, joelho afunda 2-15 px |
| Camada fixa do parado em todo golpe | Camada **por pose**: membro longe atrás do tronco, perto na frente; cruzou o peito, troca |
| Pé de apoio igual ao do parado | Pé de apoio **girado** no direto e no circular; precisa de variante "pé girado" no kit |
| Perna que chuta podia usar o mesmo pé | Pé espelhado (dedão para dentro) |
| Perna sobe reta até o alto | Câmara antes de abrir e antes de descer; coxa acima da horizontal pede bacia inclinada e tronco para trás |
| Mão livre onde ficasse | Na guarda ou para trás, nunca tapando o golpe |

### Um ponto que bate com a regra do Alisson (quadros do meio)

A Lei 10 do estudo diz: **entre a antecipação e o contato não vai quadro do meio** (no máximo um borrão), porque quadro a
mais ali faz o golpe parecer lento. A regra do Alisson pede quadros do meio para fluidez. As duas cabem juntas assim:
quadros do meio **na volta, na guarda e entre guarda e antecipação**, e no trecho antecipação → contato só um borrão (ou
nada). Hoje o `vida_pecas.py` põe meio em todo elemento com 4 ticks ou mais, então a antecipação do direto (3 a 5 ticks)
e do uppercut (5 a 8) ganha meio. **Decidido (Breno, 2026-11-17):** nada de meio entre a antecipação e o contato (no máximo 1 borrão); a fluidez vem dos outros trechos. Ver a [regra de criação](regra-de-criacao-de-personagem.md#7-vida-e-fluidez).

## O que cada lutador faz

Todos: antes de gravar cada golpe, passar a lista da Parte 4 do estudo; anotar na ficha **qual lado é perto e qual é
longe** e a **marca de roupa de cada lado** (no Pengaró: caneleira verde e garrafa são de trás/perto); conferir se o
kit usa "frente" = lado do oponente (no Hazak e no Raiclaven o comentário do kit confirma que "trás" é o de perto).
Refazer só os golpes que falham na lista; o que já passou fica.

| Lutador | `CAMADAS` hoje (braço/perna) | O que conferir e mudar |
| --- | --- | --- |
| **Pengaró** (base e despertado) | braço da frente por cima de tudo; perna da frente acima do quadril | Chute alto já consertado no montador. Rever soco e direto: pé de trás girado, tronco girando, ombro andando. Qualquer pose em que o braço da frente cruza o peito: camada para trás por pose. Despertado (agarrão e poder): mesma regra de lado; marca de lado sem a garrafa. |
| **Gutto** | braço de trás por cima (certo pela regra 1); coxa e canela da frente acima do tronco | Chute alto, chute forte, joelhada e coice: perna da frente nasce **atrás** da faixa, câmara antes de abrir, bacia inclina na coxa alta. Soco forte = receita do direto. Cotovelo = gancho com braço dobrado. Rasteira: quadril desce, pé de apoio gira, cabeça alta. |
| **Garanhão** (Gutto minotauro) | braço da frente no fundo (certo) | Pisão: joelho sobe e o corpo cai com o peso (já na 7.2.1). Investida e chifrada: receita da cabeçada, tronco dobra no meio das costas e o peso vai junto, cabeça (chifre) olhando o alvo. Coice: perna que bate sai de quadril diferente da de apoio. |
| **Gbzin** (base) | braço da frente por cima de tudo | Cotovelada = gancho dobrado com giro. Bicicleta é golpe no ar: uma perna estica e a outra encolhe, nunca as duas esticadas. Conferir mão livre na frente do golpe. |
| **Grão-Pastor** (Gbzin despertado) | mesmo kit do Gbzin | Golpes próprios: aplicar as leis 1 a 5 em cada um; se tiver giro, usar a vista de costas e trocar a camada no quadro que cruza o peito. |
| **Hazak** | braço da frente no fundo (certo); perna da frente no fundo | O mais perto da regra. Conferir pé de apoio girado nos chutes circulares e a câmara nos chutes. Rasteira: receita da Parte 3. |
| **Diabo demônio** | braço da frente por cima de tudo | Arranhão e garra cruzada = gancho (corpo gira, braço é peça rígida): o braço da frente que cruza o peito vai por cima **só a partir do contato**, antes fica atrás. Joelhada: quadril empurra, tronco para trás. Coice: quadris diferentes. Cauda fora da conta de base. |
| **CK** (base) | braço da frente por cima de tudo | É o mais "boxe": jab e cruzado têm de seguir as receitas do jab e do direto ao pé da letra (jab quase não gira; cruzado gira 45-60° com pé de trás na ponta e 60% do peso na frente). Chute alto e chute de rua: câmara, pé de apoio girado, braço do lado da perna para trás. Soco agachado: corpo afunda e sobe. |
| **Ratão** (CK despertado) | braço de trás por cima | Mesma regra de lado. Golpes próprios: lista da Parte 4 em cada um. |
| **Raiclaven** (base) | braço de trás por cima (certo) | Martelo = receita do chute circular (pé de apoio de calcanhar, quadril vira por cima, braço do lado desce para trás). Cabeçada = receita da cabeçada (testa, tronco dobra no meio das costas). Soco e chute: leis 1 a 5. |
| **Raiclaven despertado + A Cliente** | braço de trás por cima | Braço esticando continua só nos golpes de borracha (exceção do Alisson); nesses o ombro e o tronco ainda puxam primeiro. A Cliente fica fora da conta de base do Raiclaven, mas olha o alvo junto. |

## O que o montador ganharia (do estudo, sem prioridade)

Ordem de camadas por pose (já existe), variantes de pé girado e pé espelhado, régua de juntas com a tabela de limites,
régua de base (vertical do umbigo contra os pés) e casca de cebola pintando o lado longe mais escuro. Hoje o montador
abre só Pengaró, Gbzin e Gutto; os outros posam pelo kit de cada um.
