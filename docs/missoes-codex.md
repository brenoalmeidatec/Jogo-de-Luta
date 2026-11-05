# Missões para o Codex

Faça na ordem. Cada missão vira uma branch `codex/<assunto>` com PR para a `mugen`, com gerador e arquivos
gerados no mesmo commit. Marque a missão como feita neste arquivo no mesmo PR.

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

## 2. Tirar a imitação de chimpanzé da provocação do Pengaró

`docs/repertorio-de-combate.md`, linha 61, diz que a provocação do Pengaró é uma "imitação breve de chimpanzé".
O Pengaró é um personagem negro, e isso é piada de macaco. Tire do documento e não coloque no jogo. Use a provocação
de `prompts/pengaro-codex.md`: embaixadinha, "F-f-f-f-f...", e no fim ele desiste e mostra o dedo do meio.

## 3. Trocar a arte antiga pelas folhas prontas

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

## 4. Conferir na batalha simulada

Rode Pengaró contra Hazaki em CPU contra CPU, pelo menos 5 lutas, e registre em `docs/teste-batalha.md`:

- erros em `save/logs` e no console de debug;
- personagem preso em estado, sumindo, deslizando ou atravessando o chão;
- balões de fala fora de lugar ou espelhados (a fala é `Explod` com `id = 700`);
- golpe cujo membro visível não bate com a caixa de acerto (Ctrl+C mostra as caixas);
- se a Bola de Sombra quicando acerta quem está em pé e quem está agachado.

Cada problema achado vira uma missão nova neste arquivo.

## 5. Revisar o que ficou aberto

- Os PRs #5 e #7 foram feitos antes do commit `26445ab`. Refaça em cima da `mugen` o que ainda valer (janela curta dos
  especiais, Despertar a 30%, gerador em LF, Codex por PR) e feche o resto. Quem decide o merge é o Breno.
- O Hazaki agacha com 49 px e o Pengaró com 75 px, para 102 e 110 px em pé. Confira se o agachado do Hazaki não
  está baixo demais para os golpes acertarem.
