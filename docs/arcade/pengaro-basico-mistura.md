# Pengaró básico: onde os desenhos misturavam (issue #42)

Pedido do Breno (2026-11-14): o Pengaró da forma básica troca de desenho no meio dos golpes. Toda ação tem de usar um
conjunto só (o redesenho dele, `folhas_novas/`), do primeiro ao último quadro.

## Como achei

Rodei o `gerar_pengaro.py` com um espião no `hd.aplicar`: para cada sprite do corpo ele diz de onde veio o desenho
(gêmeo 3x de `quadros_arcade_hd/<folha>/NN.png`, arte antiga de `quadros/<folha>/`, ou montado por código e só
ampliado), e depois cruzei com as ações do `.air`. Script: `ferramentas/auditar_origem_pengaro.py`.

## O que misturava

**1. Quadros do meio do Blender feitos em cima do Pengaró antigo** (pele clara, outro rosto). Ficaram em
`quadros_arcade/{soco,cabecada,ar_soco,bicicleta}/meio/` quando o redesenho voltou: as folhas foram trocadas, mas as
pastas `meio/` não. Não têm gêmeo 3x, então ainda apareciam ampliados de 1x. Entravam em 1 a 4 quadros de:

| Ação | Golpe | Quadros antigos |
|---|---|---|
| 200, 201, 301, 340, 3433 | soco (e os combos/endiabrado que usam a mesma animação) | `m_soco_03_5/6`, `m_soco_04_6` |
| 303, 347, 410, 810, 3412, 3430 | cabeçada / agarrão | `m_cabecada_02_6`, `03_6`, `04_4`, `05_1` |
| 600, 601 | soco no ar | `m_ar_soco_03_5/6`, `04_3`, `04_6` |
| 610, 611, 650, 3403 | bicicleta | `m_bicicleta_03_5/6` |

**Conserto:** apaguei essas quatro pastas. O gerador já sabe viver sem quadro do meio (é o estilo arcade: desenho
segurado); o tempo total de cada golpe e as caixas não mudaram. Única diferença de tempo: o agarrão em pé (810), que é
montado com pedaços dos golpes, ficou com 115 ticks em vez de 116 (cada pancada 1 tick antes).

**2. A cena do Despertar (ação 2000, primeira metade `despertar_a`)** ainda é toda do Pengaró antigo: os 8 desenhos e
32 quadros do meio de `quadros/despertar_a/`. Não existe folha nova `despertar_a` no padrão do redesenho. Precisa
gerar no ChatGPT (bebe, vê a garrafa vazia, joga no chão), com a referência anexada, e converter. A segunda metade
(`e_despertar`, o Endiabrado) já é a nova.

## Depois do conserto

Todas as outras ações da forma básica usam só desenhos das `folhas_novas/` em 3x. Falta só a `despertar_a`.
