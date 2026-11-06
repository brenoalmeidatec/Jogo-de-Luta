# Pedidos do Codex para o Claude

Canal de ida e volta entre o Codex e o Claude. O Claude olha o repositório a cada rodada (mais ou menos de hora
em hora), faz o que foi pedido por PR para a `mugen` e devolve a resposta aqui e no próprio pedido.

## Como o Codex pede

Use um destes, o que for mais cômodo:

1. **Issue com o rótulo `claude`** (preferido para pedido avulso). Título curto com o verbo do que precisa; no corpo,
   o que fazer, os arquivos envolvidos e o critério de pronto.
2. **`[para-claude]` na descrição do PR do Codex** (como nos PRs #8 e #9): uma linha com o que o Claude deve fazer
   quando o PR entrar, mais o aceite.
3. **Uma linha na tabela "Pedidos abertos" abaixo**, no mesmo PR em que o Codex já está mexendo.

Peça só o que o Codex não consegue ou não deve fazer sozinho: revisar PR, rodar o jogo, gerar arte/folhas,
integrar lotes de animação, conferir regras. Mecânica, gerador e verificação continuam com o Codex.

## Como o Claude devolve

- Trabalha em branch `claude/<assunto>` com PR para a `mugen` (nunca `main`), seguindo
  [`regras-dos-lutadores.md`](regras-dos-lutadores.md).
- Move o pedido para "Respondidos" aqui, com o link do PR, e comenta na issue/PR de origem com `[para-claude: feito]`.
- Se faltar informação, comenta no pedido com a pergunta e deixa o pedido em aberto. Se for decisão do Breno, o
  Claude pergunta a ele.
- Notas de revisão ou testes viram entrada em [`missoes-codex.md`](missoes-codex.md), que o Codex já lê.

## Pedidos abertos

| Data | Origem | Pedido | Aceite |
|------|--------|--------|--------|
| 2026-11-06 | Breno | Refazer no Blender as animações que faltam (defesa, apanhando, queda, rasteira, especial, agarrão, ar) | Codex manda folhas de referência por golpe em `sprites/pengaro/quadros/referencias/` (veja `missoes-codex.md`) e o Claude anima no rig. |

## Respondidos

| Data | Origem | Pedido | Resposta |
|------|--------|--------|----------|
| 2026-11-05 | PR #8 | Ligar os retratos de seleção | Já na `mugen`: `gerar_pengaro.py` e `gerar_hazaki.py` usam `sprites/*-selecao-kof.png`. Falta só o PR #8 ser fechado ou mesclado. |
| 2026-11-05 | PR #9 | Usar a ficha de repertório para integrar lotes de animação | Ficha já em `docs/repertorio-de-combate.md` na `mugen`. Nada a integrar até o Codex mandar o primeiro lote; peça aqui com o lote e o aceite. |
