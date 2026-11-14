# Agarrão e poder de longe dos despertados (issue #47)

Pedido do Breno em 2026-11-14: todo despertado ganha um **agarrão com a cara da forma** e um **poder foda de soltar de
longe**, com efeitos do Blender na cor da forma e sons próprios. Aqui estão o Pengaró, o Gutto e o CK. O Hazak (Diabo
Loiro, com a rajadona de ki das trevas) fica na issue #44 e o Raiclaven (a parceira ataca por ele) na #43.

## O que entrou

| Lutador | Agarrão da forma (y ou b com → ou ← colado, no Despertar) | Poder de longe (↓ → ↓ → + soco, no Despertar) |
|---|---|---|
| Pengaró endiabrado | **Algema das Sombras**: correntes de sombra sobem do chão e enrolam o oponente enquanto ele apanha (palma torta, revolta de corrente, mão de chão, roda da possessão); no final os elos voam | **Maré das Correntes**: onda de sombra violeta rolando, com duas correntes chicoteando na frente |
| Gutto despertado | **Coice do Garanhão**: raios caem em cima do oponente preso; o coice final solta ferraduras de raio | **Estouro do Garanhão**: um garanhão de raio vermelho galopando pela tela |
| CK despertado | **Paredão na Cara**: as caixas de som estouram no oponente a cada pancada; o final é um estrondo | **Paredão no Talo**: paredão de anéis de som andando, com fumaça atrás |

- Agarrão: 3 pancadas + final, 140 de dano (o básico tem 120), mesma pega e mesmo escape do agarrão segura-e-bate.
  Fora do Despertar o agarrão continua o básico.
- Poder: carga na mão, projétil grande de 3 acertos de 42 que derruba, um por vez na tela, sem custo de barra
  (é lento para sair, dá para punir de perto). Estouro próprio quando acerta ou some.
- Sons das formas (#46): corrente no Pengaró, relincho, galope e coice no Gutto, paredão no CK.
- Lista de golpes (`movelist.dat`) com as duas entradas novas em "Exclusivos do Despertar".

Folhas: `efeitos_<lutador>.png` nesta pasta. Vídeo: `despertados_47.mp4` (motor de verdade, na nuvem; cada lutador
desperta, solta o poder e dá o agarrão no Hazak). Tira: `luta.png`.

## Como refazer

```bash
bash ferramentas/efeitos_pixel/preparar_nuvem.sh && source ~/.nazafight/ambiente.sh
"$NAZAFX_PY" ferramentas/despertados_47_blender.py     # renderiza os 12 efeitos (~1 min na nuvem)
python3 ferramentas/despertados_47.py                  # liga no .sff/.air/.cns/.cmd e no movelist (roda de novo sem duplicar)
python3 ferramentas/filmar_47.py saida.mp4 --p1 gutto  # filma o agarrão e o poder no motor
```

Ordem num lutador regerado: gerador, `parry.py`/`efeitos.py`, depois `despertados_47.py` (os outros regravam o `.sff`).
O `gerar_sons.py` não mexe nos estados 4700, 4710 e 4750; os sons deles vêm do `despertados_47.py`.

## Testado

- Robô na nuvem (`testar_pengaro.py --linux`) nos três: 0 falhas.
- Vídeo no motor: agarrão pega, segura, bate e arremessa com o efeito da forma; poder sai, acerta e derruba.

## Sugestões para depois

- Pose própria: hoje o poder usa a pose de lançar da Mão de Sombra (3400) e o agarrão usa quadros dos golpes da
  forma. Uma folha `e_poder` e `e_algema` por lutador deixaria mais marcante.
- Gbzin: quando ele entrar na `mugen`, o motoboy pede o mesmo par (CFG em `despertados_47.py`).
- A CPU quase não usa ↓ → ↓ →; dá para pôr uma chance na IA quando ela estiver longe.
