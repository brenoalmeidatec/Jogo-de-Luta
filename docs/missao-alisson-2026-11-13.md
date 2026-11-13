# Missão para o Alisson (2026-11-13)

Pedido do Breno. Para fazer em casa. Siga as regras de sempre (`docs/como-trabalhar.md`, `docs/regras-dos-lutadores.md`,
regra do 3x, estilo arcade).

## 1. Pengaró: nítido, mas igual ao de antes

- O Breno **não gostou** do Pengaró redesenhado hoje (commit `dc3427bf`, folhas em
  `sprites/pengaro/quadros/folhas_novas/`): achou cheio de erro.
- Quer o Pengaró **com o desenho de antes** (o que estava na mugen até `965f8013`), só que **nítido como o CK e o
  Gutto**.
- **O que fazer:**
  - volte os desenhos do Pengaró aos de antes: `git revert dc3427bf` resolve, ou volte `chars/pengaro/`,
    `sprites/pengaro/quadros_arcade*` e `gerar_pengaro.py` ao `965f8013`;
  - deixe esses mesmos desenhos nítidos, sem mudar o estilo nem as poses.
- **Por que borra hoje:**
  - nas folhas antigas o boneco é pequeno (uns 280 px de altura) e é ampliado;
  - o 3x vem do `hd_guiado.py`, que só repinta com as cores do 1x;
  - os quadros do meio do Blender suavizam a borda.
- **Também na missão:** a pele bem escura (`docs/arcade/pengaro.md`) e o rosto parecido com a foto. O retrato da
  seleção (`sprites/retratos/brutos/pengaro.png`) o Breno aprovou.
- **Não mexer no endiabrado** (aura grande e efeitos ficam como estão).
- O Hazak segue com você também (`docs/arcade/pedido-pengaro-hazak-nitidez.md`, branch `hazak`).

## 2. Mais mapas de Nazaré

- Faça outros cenários de Nazaré, no mesmo método do da Maria Fumaça (`cenarios/maria_fumaca/`,
  `ferramentas/gerar_cenario.py` com `tela = 1280x720`, `ferramentas/animar_cenario.py` para os figurantes).
- O projeto dos lugares (Cristo, praça da prefeitura, passarela) está na branch `cenarios`
  (`docs/arcade/cenarios_nazare.md`). O Cristo você já tinha começado.
- **Um cenário na Katiara:** com um **muro cheio de números 7 e das siglas "KT"** pichadas.
- **Figurantes:** animados em pixel. O Blender só anima o desenho, sem nada 3D.
- **Launcher:** ele já instala `stages/`. Para entrar na escolha, acrescente cada cenário em `[ExtraStages]` (ver o
  `Jogo de Luta.bat`).

## 3. Tela animada de entrada

- Uma abertura animada quando o jogo abre, antes do menu (logo Nazafights, Nazaré ao fundo), no estilo arcade.
- O menu novo e a tela de título de hoje estão em `ferramentas/gerar_layout.py` e `sprites/titulo/`.

## 4. Revisar o jogo: tem muita coisa inconsistente

O Breno pediu uma revisão geral do que dá para melhorar. Pontos já vistos:

- Pengaró e Hazak com estilo e definição diferentes dos outros (itens 1 e acima).
- Na grade da seleção, o "?" da escolha aleatória aparece desencaixado sobre a célula vazia.
- Gutto despertado: 442 sprites só ampliados, e as ações 181, 601 e 10601 misturam 3x com 1x.
- Robô: Gutto e Raiclaven falham em `var(37) = 1 no meio do 3100`.
- O parry ainda não está ligado (`docs/parry.md`).
- Os figurantes do cenário e o HUD novo (vida e poder) estão sem conferência sua.

Teste com o robô (`testar_pengaro.py`) e no jogo antes de subir. Anote no `LOGBOOK.md` o que fez e o que ficou.
