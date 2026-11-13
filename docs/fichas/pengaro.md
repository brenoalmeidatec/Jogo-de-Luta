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
Aura do Despertar (discreta, [regra dos efeitos proporcionais](../regra-efeitos-proporcionais.md) de 2026-11-12):
fumaça violeta-escura das sombras, à parte do corpo e toda ATRÁS dos lutadores (nunca cobre corpo nenhum): fumaça
violeta-preta baixa, do chão até o peito, saindo de um chão rachado pequeno, que fica no chão no pulo. É a coluna e o
chão da aura grande do Blender encolhidos em volta do pé (sem chicotes, fiapos, pedras nem elos), em 3x
(`sprites/pengaro/aura/`, `ferramentas/aura_blender/discreta.py`), ligada no jogo por `ferramentas/aura_pengaro.py`
(1 Explod, 9600, scale 1/3, alfa 0,5, no `[Statedef -4]`; entra em 44 ticks e sai em 34 só pelo alfa, sem crescer). O boss se vê pela arte nova, não pela aura. Liga com o Despertar
(e na transformação e no super 3100), incha nos supers, apaga junto com a forma endiabrada. Matiz média 281°: nenhum
outro lutador usa violeta (CK 72°, Gutto 350°, Hazak 30°, Raiclaven 220°). As folhas `fx_aura_*` do Lote 7 não são
mais usadas. Tamanho no pior tique (`aura.altura()`/`largura()`, com surto e deriva): 69 px de altura (teto 71) e
**176 px de largura**, ~2,5x a largura dele e o dobro da aura do CK (84 px): baixa, mas larga. A regra não põe teto
de largura; falta o Breno julgar se ainda é discreta.
Golpes do endiabrado: as mesmas faíscas da forma normal, sem o corte de sombra / poeira violeta em todo golpe e sem
o rastro (AfterImage) o Despertar inteiro (regra dos efeitos proporcionais, 2026-11-12); o rastro de 40 tiques de
cada super continua.
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
