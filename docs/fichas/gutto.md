# Gutto (id técnico `gutto`)

Ficha no modelo da seção 10 de [`docs/regras-dos-lutadores.md`](../regras-dos-lutadores.md). **Rascunho:** nasceu do áudio
do Breno de 2026-11-06 (transcrito com WhisperX, que erra em trechos; o que está marcado *(confirmar)* é interpretação).
As fotos de referência do Gutto ainda vão chegar e mandam na aparência. Arte no **mesmo estilo do Pengaró**: sprite 2D
de SNES/arcade desenhado à mão, nunca 3D pixelizado.

## O que o Breno disse no áudio

- É **lutador de Muay Thai**. Ataques padrão de Muay Thai, com **low kick**; "só chute" (chutes, joelhadas e cotovelos).
- **Beijinho**: um golpe de beijo, bom de ver, com **uma segunda variação** *(confirmar o que muda: alcance, trajetória ou
  efeito)*. Faz o papel de **projétil**.
- **Teleporte diferente**, de Muay Thai: levanta a perna numa ginga e dá uma "metidinha" (empurrão de pé) para a frente,
  e **aparece atrás do oponente** do nada. É o golpe de ir para trás do oponente (regra F).
- **Endiabrado (Despertar): cara de cavalo.** Fica com a cabeça de cavalo, **bufando**.
  - Chute giratório que parece **coice de cavalo**.
  - **Carrinho** (carrinho de futebol) "igual a Satanás": golpe baixo, de deslize.
  - **Corre no modo cavalo**: corrida mais rápida, galope.
- Tom: resenha entre amigos. Vale a regra do jogo: resenha pesada pode; nada de piada de escravidão nem do estereótipo da
  mulher loira.

## Ficha (proposta; ajusto quando as fotos chegarem)

**Estilo de luta:** Muay Thai: chutes baixos e altos, teep, joelhada e cotovelo; pressão e entrada rápida.
**Personalidade / falas:** a definir pelo Breno (áudios depois).
**Cores e paleta:** a partir das fotos. Altura-alvo: escala do arcade, **112 px** (normal), como o Pengaró.
**Efeitos (pixelfx e recolor):** `hit-spark` e `crit-hit` nos chutes; `heavy-landing` no carrinho; fumaça/vapor do
nariz (bufando) no Endiabrado; rastro de poeira no galope.

### Correntes (3 golpes + finalizador)

| Botão | 1º | 2º | 3º | Finalizador (derruba) |
|---|---|---|---|---|
| x | jab | direto | gancho | cotovelo giratório |
| y | cotovelo | cotovelo de cima | joelhada | joelhada voadora |
| a | low kick | low kick alto | teep | chute giratório baixo |
| b | chute alto | chute duplo | chute giratório | **chute de coice** |

### Kombos de assinatura (4), Especiais (8), Agarrões (3), Supers (2)

A preencher depois das fotos, mantendo no kit o que veio do áudio:

| Do áudio | Papel no kit |
|---|---|
| Beijinho (2 variações) | projétil (um dos 2 projéteis; o outro deve ter papel diferente) |
| Teleporte de Muay Thai | ir para trás do oponente, chega virado (regra F) |
| Low kick | golpe baixo/de chão |
| Agarrão de Muay Thai | clinch com joelhadas (agarrão em pé); agachado e o de lore a definir |

### Despertar: Endiabrado (cara de cavalo)

Ativação: barra cheia + x + y. Cara de cavalo, bufando; corrida de galope; chute giratório vira coice; carrinho de
Satanás. Regra 4: pelo menos 2 correntes novas, 6 normais novos, 4 especiais exclusivos (1 projétil novo), 1 kombo novo
e 1 super exclusivo. **Arte redesenhada**, não só recolorida.

## Passos

1. Chegar as fotos de referência; desenhar a **folha-referência** (ChatGPT, chat "Gutto", estilo do Pengaró).
2. Conferir personagem e cor; depois uma folha por movimento (8 quadros, fundo magenta `#FF00FF`).
3. `ferramentas/gerar_gutto.py` (a criar, no molde do `gerar_pengaro.py`), verificador e teste do robô.
