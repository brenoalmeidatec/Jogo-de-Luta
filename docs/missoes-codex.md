# Missões para o Codex

Faça na ordem. Cada missão vira uma branch `codex/<assunto>` com PR para a `mugen`, com gerador e arquivos
gerados no mesmo commit. Marque a missão como feita neste arquivo no mesmo PR.

**Regra fixa:** toda missão que mexe em lutador segue [`regras-dos-lutadores.md`](regras-dos-lutadores.md). Quando
uma missão e as regras discordarem, valem as regras.

Esta lista saiu de uma revisão dos arquivos da `mugen` no commit `26445ab`. **Ninguém viu a batalha simulada:**
abrir o `Ikemen_GO.exe` é bloqueado para o Claude neste PC. Então o que está marcado como suspeita precisa
ser confirmado rodando o jogo, com Pengaró contra Hazaki no modo Watch.

## 1. Personagem fica pequeno

O Breno viu o personagem ficar pequeno em alguns momentos da luta.

Principal suspeita: o zoom de câmera dos cenários de exemplo. `stageZ` e `interactivestage` têm `zoomout = 0.75`
e `stage3d_outline` tem `zoomout = .8`, então os lutadores encolhem quando se afastam. O `stageZ` ainda muda a
escala pela profundidade. Em `stage0`, `stage1` e `kfm` isso não acontece.

Outra suspeita: troca entre arte de escalas diferentes. Parado, andando e soco têm quadros novos, e pulo, queda
e outros golpes ainda usam as 9 poses antigas, com corpo e cabeça de tamanhos diferentes.

Pronto quando: a luta inteira roda em cenário sem zoom, o atalho deixa só esses cenários na seleção e o tamanho da
cabeça é o mesmo em todos os quadros (acrescente essa conferência ao `verificar_pengaro.py`, com tolerância de 10%).

## 2. Trocar a arte antiga pelas folhas prontas

O Breno aprovou o método das folhas desenhadas e cobrou o gingado: ele luta capoeira, então parado e andando não
podem ser guarda de boxe.

A branch `claude/folhas-pengaro` tem 30 folhas de 8 quadros já geradas, incluindo `ginga` e `anda`, com os prompts
em `ferramentas/gerar_folhas.py`. Elas ainda não foram recortadas nem conferidas uma a uma.

1. Traga as folhas para uma branch a partir da `mugen`.
2. Recorte cada uma com `ferramentas/recortar_quadros.py`, usando a âncora definida em `FOLHAS_PENGARO`.
3. Confira os quadros. Refaça a folha que tiver figura cortada, encostada na vizinha ou com personagem diferente.
4. Use `ginga` no parado (ação 0) e `anda` no andar (ações 20 e 21).
5. Troque as poses antigas nas outras ações. Ao mudar o número de quadros de um golpe, ajuste os gatilhos `AnimElem`
   do estado dele e mantenha o frame data.

Pronto quando: nenhuma ação usa as 9 poses antigas e o Pengaró ginga sem parar quando está parado.

## 3. Conferir na batalha simulada

Rode Pengaró contra Hazaki em CPU contra CPU, pelo menos 5 lutas, e registre em `docs/teste-batalha.md`:

- erros em `save/logs` e no console de debug;
- personagem preso em estado, sumindo, deslizando ou atravessando o chão;
- balões de fala fora de lugar ou espelhados (a fala é `Explod` com `id = 700`);
- golpe cujo membro visível não bate com a caixa de acerto (Ctrl+C mostra as caixas);
- se a Bola de Sombra quicando acerta quem está em pé e quem está agachado.

Cada problema achado vira uma missão nova neste arquivo.

## 4. Revisar o que ficou aberto

- Os PRs #5 e #7 foram feitos antes do commit `26445ab`. Refaça em cima da `mugen` o que ainda valer (janela curta dos
  especiais, Despertar a 30%, gerador em LF, Codex por PR) e feche o resto. Quem decide o merge é o Breno.
- O Hazaki agacha com 49 px e o Pengaró com 75 px, para 102 e 110 px em pé. Confira se o agachado do Hazaki não
  está baixo demais para os golpes acertarem.

## 5. Achados da batalha simulada (Pengaró x Hazaki, CPU 5 contra CPU 5)

O Breno abriu o jogo em modo Watch e o Claude gravou cerca de 40 quadros da tela, mais um quadro de um segundo round.
Os prints estão em `docs/batalha-2026-11-05/`. O jogo abriu e não gerou nenhum log de erro novo. Os achados abaixo
são do que apareceu na tela, e cada um precisa ser reproduzido antes de consertar.

**A. Lutadores cortados na borda da tela.** `longe-e-cortado.png`: quando os dois se afastam, a câmera não afasta o
bastante, e o Pengaró fica cortado à esquerda e o Hazaki à direita. `recortado-na-borda.png` mostra o mesmo no
mortal. Confira `zoomout` e `boundleft/boundright` do cenário usado, e a largura (`ground.front/back`) dos dois.
Isso é o contrário do "personagem pequeno" que o Breno relatou, que **não apareceu** nesses quadros: o tamanho
na tela foi de 40% a 50% da altura da janela o tempo todo, com leve zoom. Pergunte ao Breno qual cenário e qual
momento da luta ele viu pequeno, e use o mesmo.

**B. Balões de fala sobrepostos e cortados.** `sequencia-baloes-e-ko.png`: "F-f-f-foi falta, porra!" e "CANETA,
PASSOU POR BAIXO!" aparecem um em cima do outro. O "K.O.! ...ou, no caso dele" sai cortado na borda direita.
Todo balão usa `id = 700`, mas um novo não apaga o antigo. Faça `RemoveExplod` do id 700 antes de criar um balão e
mantenha o balão dentro da tela (limite pela posição do lutador e `Explod` com `postype = left`/`right` na borda).
No Despertar a fala "liso" repete o nome do golpe em todo uso e fica na tela por tempo demais.

**C. Aura cor-de-rosa e roxa fica no K.O.** No Despertar o Pengaró fica rosa e roxo, e isso continua depois do K.O.
(`sequencia-baloes-e-ko.png`, linha 2). Zere o `PalFX` e o rastro quando o personagem não está vivo ou quando o round
acaba, e confira se o rosa é o que a ficha pede (fumaça roxo-escura ou preta e olhos roxos, não o corpo todo).

**D. O "ó" some do nome.** A barra de vida mostra "Pengar". A fonte da barra do IKEMEN não tem acento. Troque a fonte
dos nomes por uma que tenha, ou grave o nome da barra já com o "ó" desenhado.

**E. Retratos.** A barra usa o retrato novo (`sprites/pengaro-selecao-kof.png`), e o rosto não bate com o do sprite
em jogo (cabelo, barba e traços). Confira se é o mesmo personagem.

**F. Pose de mortal.** `mortal-de-cabeca.png`: o pulo para frente (ação 42) gira de cabeça para baixo, com a cabeça
perto do chão. Parece forte demais para um pulo comum. Troque por quadros do pulo da missão 2 e deixe o mortal
só no golpe que a ficha pede (bicicleta).

**G. Fim de round demora.** Depois do K.O. o tempo ficou parado em 23 por cerca de 15 segundos até começar o
round seguinte, com o Pengaró caído e uma fala de ressaca repetida nesse meio-tempo. Veja se a pose de vitória do
Hazaki (ação 181 dele) e a de derrota do Pengaró estão curtas o bastante, e tire a fala da ressaca quando ele está
caído.

**H. Barra de vida verde no round 2.** No quadro do segundo round a barra do Pengaró está verde, enquanto a do Hazaki
está amarela (`longe-e-cortado.png`). Se isso vier de efeito do motor (por exemplo vida recuperada ou "red life"),
ok, e se não vier, confira o que o Pengaró faz com a vida entre os rounds.

## 6. Adequar Pengaró e Hazaki às regras de todo lutador

As [regras](regras-dos-lutadores.md) chegaram depois dos dois. Compare cada um com o checklist da seção 9 de lá e
anote em `docs/fichas/pengaro.md` e `docs/fichas/hazaki.md` o que já existe e o que falta. Depois, em PRs separados:

1. Correntes de 3 golpes + finalizador nos quatro botões (substitui a corrente de até 4 fracos atual).
2. Despertar com barra cheia e x + y (hoje é x + a + y com 1 estoque).
3. Segundo projétil, golpe de ir para trás do oponente e agarrão agachado + agarrão de comando.
4. O que faltar de kombos, especiais e golpes exclusivos do Despertar.

Pronto quando: os dois passam no checklist inteiro.
