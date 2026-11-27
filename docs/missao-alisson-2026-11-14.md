# Missão para o Alisson (2026-11-14): telas, sons, agarrões, parry e revisão geral

Pedido do Breno. Siga as regras de sempre (`docs/como-trabalhar.md`, `docs/regras-dos-lutadores.md`, estilo arcade).
Vale junto com as missões e issues abertas: músicas e transformação (`missao-alisson-musicas-e-transformacao.md`),
cenários (`missao-alisson-cenarios.md`, issue #35), cenários de exemplo (#34), Pengaró (#32), Gbzin (#30) e Hazak (#36).

**Ordem:** primeiro os itens 1 a 5, depois a revisão (item 6) e por último o balanceamento (item 7).

## 0. Música do Katiara

O Breno escolheu e gravou: `musicas/originais/cenario_katiara.m4a` (2:52, AAC 128 kbps, tirado do vídeo sem
reconverter). Foi feita no ritmo do pagodão "bloquinho" que ele pediu: 93 bpm em tercina (12/8), percussão na frente, em
8-bit. Liga no cenário Katiara com as regras de loop da issue #33. O começo tem 1,4 s de silêncio da gravação.

## 1. Refazer o layout (antes de tudo)

O Breno viu o layout atual e **ainda não está do agrado dele**. Refaça:

- **Mais moderno**, mas ainda com cara de **jogo de luta**.
- **A imagem principal (tela de título) animada**, com movimento de verdade, não uma imagem parada.
- **HUD bem simples:** barras de vida e poder limpas, retrato pequeno, cronômetro; nada carregado na tela da luta.
- **Tela de VS:** hoje os sprites dos lutadores aparecem **grandes demais**. Diminua até caber com folga, sem cortar.
- Seleção de lutadores e de mapa (issue #35) no mesmo estilo novo.
- Arquivos: `ferramentas/gerar_layout.py`, `sprites/titulo/`, `motif/nazafight/`. Poste prévias na issue antes de juntar.

## 2. Sons novos

- **Sons novos para os golpes e o resto:** soco fraco e forte, chute, acerto, defesa, agarrão, queda, especiais,
  supers, transformação, parry, menu (mover, confirmar, voltar), contagem do round, KO.
- Cada lutador com o seu som onde fizer sentido (garrafa do Pengaró, cajado do Gbzin, luva do CK...).
- Sons próprios, sem copiar de outros jogos. Volume parelho com as músicas.

## 3. Agarrões de cada lutador (refazer)

O Breno **ainda não viu um agarrão de segurar o oponente e bater nele**, como nos jogos de luta clássicos (tipo o
Mortal Kombat): pega, segura e soca/chuta várias vezes, e no fim arremessa ou derruba.

- Refaça os agarrões de **todos os lutadores** nesse estilo: o oponente fica preso (`TargetBind`/estado do agarrado),
  leva uma sequência de golpes visíveis, cada um com acerto, som e faísca, e termina com arremesso ou queda.
- Cada um com o jeito do lutador (capoeira e garrafa no Pengaró, joelhada de Muay Thai no Gutto, boxe sujo no CK...).
- Escape do agarrão como já existe. Robô conferindo dano, duração e que o oponente volta ao controle.

## 4. Tirar a "rede de futebol" e fazer o parry certinho

- A faísca pronta do pixelfx (círculo preto com raios) **parece uma rede de futebol**. **Tire de todo lugar.**
- Faça o **parry do jeito que está em [`docs/parry.md`](parry.md)**: em cima (→ + c) e embaixo (↓ + c), um parry
  próprio de cada lutador, engraçado na forma base e foda na forma endiabrada, faísca própria na cor do lutador, o
  oponente aberto por 20 ticks e a animação cancelável. Ele precisa entrar no jogo funcionando certinho.

## 5. Pendências já pedidas

Músicas ligadas com loop limpo e transição gradual, cena da transformação com cenário destruído, efeitos de cada ataque,
mapas animados com tela de escolha de mapa (nunca aleatório), Katiara, Pengaró do Breno corrigido, Hazak nítido e Gbzin
igual à foto. Tudo está nas missões e issues citadas no começo.

## 6. Depois de tudo: revisão geral do jogo

Rode **o jogo inteiro** procurando **erros e coisas sem sentido**:

- todos os modos (título, Arcade, Versus, Treino, Assistir, opções), todas as telas e transições;
- todo lutador em toda forma: cada golpe, especial, super, agarrão, parry, transformação, vitória, derrota e tempo esgotado;
- todo cenário com a sua música;
- coisas fora do lugar: sprite cortado ou piscando, caixa de golpe sem sentido, efeito na frente do HUD, som faltando,
  música cortando seco, texto em inglês, golpe que não sai, estado que trava.

Liste o que achou numa issue, conserte e rode o robô em todos.

## 7. Por último: balanceamento

Com tudo funcionando, veja o **balanceamento**: dano, velocidade, alcance, recuperação, barra de poder e duração da
transformação de cada lutador, para nenhum ficar forte ou fraco demais. Use luta CPU x CPU e os números do robô, e
escreva no `LOGBOOK.md` o que mudou e por quê.
