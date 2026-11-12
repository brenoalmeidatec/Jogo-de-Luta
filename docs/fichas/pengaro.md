# Pengaró

Estilo de luta: capoeira de bar. Ginga, rasteira, compasso (parada de mão) e armada, com a garrafa de whisky na mão
de trás e lata de cerveja para arremessar. Gosta de chimpanzés (faz parte da história).
Personalidade / falas: boleiro, cachaceiro e resenhista. As falas estão desligadas (`BALOES_LIGADOS = False`) até o
Breno gravar os áudios; os textos em `BALOES` ficam de roteiro.
Cores e paleta: pele negra retinta, a mais escura do elenco (mais que o Gutto e o CK; pedido do Breno em 2026-11-12,
detalhes em `docs/arcade/pengaro.md`), calça de capoeira clara, faixa verde e amarela; no Despertar vira o endiabrado, o
boss final (conceito aprovado em 2026-11-11, `sprites/pengaro/quadros/folhas_arcade/e_conceito.png`): mesmo rosto,
corpo e altura, sem garrafa; pele marrom-escura arroxeada, olhos violeta sem pupila, cabelo comprido e revolto com
pontas violeta e dois chifres curtos de fumaça; casaco de mestre preto sem manga com friso dourado e forro roxo, barra
rasgada até a canela; rachaduras violeta no peito; corda trançada ouro e violeta com duas pontas até o joelho; calça
preta com barra em brasa violeta; algemas de corrente partida nos pulsos e tornozelos; braceletes de ouro.
Aura do Despertar: fumaça violeta-escura das sombras, em três camadas à parte do corpo: coluna de fumaça violeta-preta
atrás, anel de sombra girando no chão rachado, elos de corrente e pedras flutuando na frente (`fx_aura_coluna`,
`fx_aura_anel`, `fx_aura_detritos`, Lote 7 de `docs/arcade/fila.md`; ainda não geradas).
Efeitos (pixelfx e recolor): hit-spark nos fracos, crit-hit nos fortes e finalizadores, ground-slam na Queda Escura
e no Pisão de Bar, fumaça roxa no Despertar.

> Tudo aqui é gerado por `ferramentas/gerar_pengaro.py` e `ferramentas/pengaro_extra.py`. A arte de todos os golpes
> novos reaproveita as folhas já desenhadas (sem arte nova ainda): ver "Pendências" no fim.

## Correntes

O 1º golpe é o normal do botão. Só avança se o anterior encostou; o finalizador só sai se os 3 acertaram de verdade
(defendido não conta) e derruba. O 1º e o 2º cancelam em especial; o 3º só se acertou; o finalizador não cancela.

| Botão | 1º | 2º | 3º | Finalizador |
|---|---|---|---|---|
| x | Cutucão | Jab de Retorno | Cotovelo de Ginga | Cabeçada de Roda |
| y | Tapa de Lado / Cotovelada | Martelada | Sola de Baixo | Armada Final |
| a | Bicuda Curta | Bicuda Dupla | Ponta Rasteira (baixo) | Meia-Lua Final |
| b | Ginga Alta / Passo | Calcanhar de Roda | Chute de Afastar | Compasso de Roda |

## Kombos de assinatura (4)

| Kombo | Entrada | Observação |
|---|---|---|
| Abertura | frente + y, x, b | 3º golpe por cima (Passo de Letra Cruzado) |
| Alto e Baixo | x, baixo + a, y | 2º é baixo, 3º é por cima e derruba |
| Empurrão | trás + x, y, frente + b | empurra longe |
| Lançador | a, b, baixo + y | Cabeçada Lançadora joga para o ar |

## Especiais (8)

| Especial | Comando | Papel |
|---|---|---|
| Latada de Sombra | baixo, frente + a/b | projétil reto (lenta ou rápida) |
| Garrafada em Arco | frente, trás + x/y | projétil em arco, passa por cima de golpe baixo |
| Rolê por Trás | frente, trás + a/b | vai para trás do oponente e chega virado (b já chuta) |
| Meia-lua de Compasso Sombria | baixo, trás + a/b | avanço, derruba |
| Armada do Quilombo | frente, baixo + x/y | antiaéreo |
| Caneta | baixo, trás + x/y | golpe baixo, passa por baixo de projétil |
| Mão de Chimpá | baixo, frente + x/y | avanço |
| Sola de Várzea | trás, baixo + a/b | golpe de chão (pisão) |

## Agarrões (3)

| Agarrão | Comando | O que faz |
|---|---|---|
| Em pé | colado, frente/trás + y ou b | Giro de Camisa e Queda de Ginga |
| Agachado | colado em oponente agachado, baixo + y | Rasteira de Pegada (110) |
| De comando (lore) | colado, trás, frente + y | Martelo e Garrafada: compasso (60) + whisky na cabeça (90) |

A lore chega depois, por oponente (seção 5.5 das regras): o agarrão de comando passa a trocar animação e fala conforme
o nome do oponente. Até lá ele funciona contra todo mundo.

## Supers (2)

| Super | Custo | Comando |
|---|---|---|
| Chuva de Bebidas | 1 estoque | trás, frente, baixo + a/b |
| Bando da Várzea | 2 estoques | trás, frente, baixo + x/y |

## Despertar: Lata Gelada

Ativação: barra cheia + x + y; gasta a barra inteira, tem invencibilidade e empurra o oponente para longe. Dura 10 s.
O que ganha: dano x1,45, golpes novos, projétil que acelera. O que perde: ressaca de 1 s ao acabar (anda devagar).

### Correntes novas (2) · Normais novos (6) · Especiais exclusivos (4) · Projétil novo · Kombo novo · Super exclusivo

| O quê | Golpes |
|---|---|
| Correntes novas (4 golpes cada) | y: Revolta de Corrente, Sola de Ferro, Cabeçada Escura, Roda da Possessão · b: Calcanhar Sombrio, Afastar Pesado, Armada Torta, Chute da Corrente Partida |
| Normais novos (6) | baixo + y Mão de Chão Possuída (lança) · baixo + b Foice Escura (rasteira que derruba) · frente + y Tranco Possuído (2 acertos) · frente + b Passo de Sombra (por cima, longo) · trás + x Palma Torta · trás + a Puxada Sombria |
| Especiais exclusivos (4) | baixo, baixo + x Mão de Sombra (projétil novo) · + y Chute da Corrente · + a Sombra Atravessada · + b Queda Escura |
| Kombo novo | b, a, x (Compasso Possuído, Caneta Sombria) |
| Super exclusivo | Saideira Sombria (mesmo comando do Chuva de Bebidas durante o Despertar, ou com 20% de vida e 2 estoques) |

## Pendências (honestas)

- **Testado por robô, não por uma pessoa.** `python ferramentas/testar_pengaro.py` abre o motor numa cópia, aperta os
  botões por script e confere correntes, kombos, agarrões, projéteis, Rolê por Trás (inclusive no canto), Despertar e
  os exclusivos: 126 verificações, 0 falhas. Ainda falta um humano sentir o jogo: dano, ritmo, alcance e se a
  transformação *parece* certa na tela.
- **Arte nova:** os golpes novos reaproveitam folhas existentes com outra ordem e tempo. A regra 3B pede pose nova no 2º,
  3º e finalizador de cada corrente. Falta desenhar folhas próprias (e as `e_` do endiabrado) para eles.
- 72 de 159 ações antigas ainda têm desenho parado por mais de 2 ticks (regra 7).
- Faltam áudios das falas e `movelist` com ícones de botão conferidos no jogo.
