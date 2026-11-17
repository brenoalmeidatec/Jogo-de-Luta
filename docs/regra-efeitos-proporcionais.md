# Regra dos efeitos: simples, sutis e do tamanho do golpe

**Regra do Breno, 2026-11-12. Quem faz: o Alisson.**

Tem golpe que solta um efeitão enorme que não combina com o que está acontecendo. O efeito tem que contar o golpe,
não roubar a cena: **simples, sutil e proporcional à força**.

## O tamanho do efeito segue a força do golpe

| Golpe | Efeito no acerto | Na defesa | Tremor de tela |
|---|---|---|---|
| Fraco (x, a, jab, bicuda) | só um **ventinho**: risco curto de ar ou poeira pequena, 3-4 quadros | faísca mínima | nenhum |
| Médio (y, b em pé, corrente no meio) | estalo pequeno no ponto do contato | faísca pequena | nenhum ou 2 ticks bem leves |
| Forte (finalizador, golpe que derruba ou joga longe) | **impacto maior**: estouro no contato, poeira no chão onde o oponente cai | faísca média | sim, curto (6-8 ticks) |
| Especial | o efeito do próprio especial (lasca, garrafa, pente, fumaça), na escala do golpe | idem, menor | só se jogar longe |
| Super / finalizador de super | é aqui que vale o efeito grande | média | sim |

- Nada de efeito grande em golpe fraco. Nada de efeito cobrindo o corpo dos lutadores.
- O efeito nasce **no ponto do contato** (a ponta do punho ou do pé), não no meio do corpo.
- O efeito dura pouco: some antes da recuperação do golpe acabar.

## O endiabrado NÃO entra nesta regra: aura monstruosa e grande

**Correção do Breno (2026-11-13):** "no modo endiabrado eu não queria que mudasse nada, eu queria daquele jeito, com as
auras monstruosas e grandes para mostrar que tem poder". A regra de 2026-11-12 foi lida errado (como "aura discreta") e
desfeita em 2026-11-13.

- **Aura do Despertar** (as auras de cada lutador da [regra da aura](regras-dos-lutadores.md)): **grande, com várias
  camadas, monstruosa**. É o que mostra que o boss tem poder. Não vale encolher, deixar translúcida nem reduzir a uma
  camada.
- **Efeitos do endiabrado** (rastro do Despertar, faísca própria do endiabrado, corte de sombra e poeira violeta em todo
  golpe): **ficam como estavam**. O endiabrado não muda.
- O que fica simples e proporcional é o efeito de combate da **forma normal** (a tabela acima).
- O que fica de pé da regra de 2026-11-12 é que a aura é efeito à parte, atrás do corpo, sem tingir o corpo. Ela também
  continua sem tampar o HUD.

## Como fazer os efeitos: no Blender

- Os efeitos novos saem do **Blender** (partículas, fumaça, poeira, risco de ar). Renderize em 3x, na mesma regra da
  [alta resolução](regra-alta-resolucao.md), e quantize em poucas cores, no estilo arcade, com contorno seco e sem
  degradê.
- Um efeito por papel, reaproveitado entre lutadores com a **cor** de cada um (a paleta de efeito do lutador):
  ventinho, estalo, impacto, poeira de queda, faísca de defesa, faísca de parry.
- O pixelfx antigo sai, conforme os efeitos novos forem entrando, inclusive a faísca de parry em círculo preto, que
  parecia uma rede de futebol.
- Lembrete do motor: Explod e projétil **não** usam a escala do lutador. O efeito em 3x precisa de `scale = 1/3` no Explod
  (ou `projscale` no projétil), para sair no tamanho certo e nítido.

## Como está feito hoje (issue #38, 2026-11-14)

Golpe normal usa os desenhos do pixelfx pintados na cor do lutador e da forma; especial, super e transformação usam
efeitos do Blender, também na cor dele. Nada do ChatGPT. Ferramentas: `ferramentas/efeitos.py` (liga tudo) e
`ferramentas/efeitos_blender.py` (renderiza). Detalhes, cores e temas em [efeitos-38/LEIA-ME.md](efeitos-38/LEIA-ME.md).

## Para conferir antes de subir

- **Filmar:** um soco fraco, um forte e um super de cada lutador. O fraco quase não tem efeito, o forte se sente, e o
  super é o único que enche a tela.
- **Despertar:** o lutador é sempre legível por cima da aura.
