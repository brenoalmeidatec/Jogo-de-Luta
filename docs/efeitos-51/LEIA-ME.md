# Efeitos de acerto todos no pixelfx (issue #51, item 2)

Pedido do Breno em 2026-11-14 (`docs/missao-alisson-estilo-melty.md`, item 2): todo efeito de acerto feito no
**pixelfx**, sem imagem do ChatGPT e sem a faísca pronta de círculo com raios, mantendo o tamanho, o peso, a tremida e
o clarão do nível do Hazak.

## Lista de todos os efeitos e de onde vem o desenho

Vale para Pengaró, Gutto, CK e Raiclaven, nas duas formas. A origem "pixelfx" são as folhas de `assets/efeitos/`,
pintadas em degraus na cor do lutador pelo `ferramentas/efeitos.py`.

| Efeito | Ação | Antes desta entrega | Agora | Trocado |
|---|---|---|---|---|
| Faísca do golpe fraco | 9200 / 9230 | pixelfx (hit-spark) | igual | já era |
| Faísca do golpe forte | 9201 / 9231 | pixelfx (blunt-hit) | igual | já era |
| Faísca do finalizador | 9205 / 9235 | pixelfx (crit-hit sem o anel, blunt-hit) | igual | já era |
| Faísca de defesa | 9202 / 9232 / 9234 | pixelfx (hit-spark) | igual | já era |
| Rastro do golpe | 9213 / 9212 | pixelfx (uppercut) | igual | já era |
| Poeira | 9214 / 9215 | pixelfx (heavy-landing) | igual | já era |
| Parry | 7690 / 7691 | pixelfx (crit-hit, só a estrela) | igual | já era |
| Agarrão (pancadas e final) | usa 9200 e 9201 | pixelfx | igual | já era |
| **Estouro de especial** | 9240 / 9270 | Blender (anel com miolo) | pixelfx: blunt-hit + estrela do crit-hit + camada do lutador | ✅ |
| **Explosão de super** | 9241 / 9271 | Blender (anel com miolo) | pixelfx: cinco estouros em sequência + camada do lutador | ✅ |
| **Carga do especial e da super** | 9243 / 9273, 9244 / 9274 | Blender (anel fechando) | pixelfx: charge-up (só as faíscas que juntam) + estrela | ✅ |
| **Corte da forma (especial 3400)** | 3012 | **ChatGPT** (corte roxo, grupo 9212) | pixelfx: energy-disc (Pengaró, Raiclaven), fireball (Gutto), na cor da forma | ✅ |
| **Nuvem do CK** (especiais 1000, 1001, 3400) | 1005, 1006, 9253 | **ChatGPT** (nuvem, grupo 9300) | pixelfx: fumaça do ground-slam | ✅ |

Camada de cada lutador nos estouros: respingo para os dois lados no Pengaró, segunda pancada no Gutto, relâmpago no
Raiclaven e onda baixa de poeira no CK.

O que **não** é efeito de acerto e ficou como estava (para o Breno decidir):

| O quê | Origem | Observação |
|---|---|---|
| Pilar da transformação (9272) | Blender | não é ChatGPT; é da cena do Despertar |
| Estouros e chamas do Hazak (9240, 9241, pedra, ki, rajadona) | Blender | aprovados na #44 |
| Agarrão e poder de longe dos despertados (47000 a 47004) | Blender | aprovados na #47 |
| Auras (9600 a 9603) | folhas de arte | são o item 1 da #51 (auras presas ao corpo) |
| Objetos arremessados: garrafa e latinha do Pengaró, coração do Gutto, pente do Raiclaven, garrafa e paredão do CK | arte do lutador (ChatGPT) | são objetos, não efeitos; dá para refazer se o Breno quiser |

Sem a "rede de futebol": o anel do crit-hit, o círculo pontilhado do charge-up e a grade do shield-block não entram em
nenhum efeito.

## Arquivos

- `destaques.jpg`: quadros das lutas.
- `pixelfx_gutto_ck.mp4`, `pixelfx_pengaro_raiclaven.mp4`: CPU contra CPU com a barra cheia (o segundo com Despertar).
- `efeitos_<lutador>.png`: todos os efeitos quadro a quadro.

## Como refazer

```bash
python3 ferramentas/efeitos.py                       # aplica nos 5 lutadores (pode rodar de novo)
python3 ferramentas/efeitos.py --folha docs/efeitos-51
python3 ferramentas/filmar_luta_linux.py saida.mp4 --p1 gutto --p2 ck --barra
```

Onde mexer no `efeitos.py`: `camadas` e `TEMA` (estouros e carga), `PROJETEIS` (corte e nuvem), `CORES` (cor).

## Testado

Robô na nuvem nos 5 lutadores, 0 falhas: Pengaró 190, Gutto 185, CK 228, Raiclaven 185, Hazak 238.

## Sugestões para depois

- Rodar o gerador do pixelfx para desenhos novos e exclusivos (hoje só dá para usar as 13 folhas de `assets/efeitos/`,
  porque rodar o gerador está bloqueado na nuvem); com ele cada especial poderia ter o seu estouro.
- Refazer os objetos arremessados em pixel art feita à mão, se o Breno quiser tudo fora do ChatGPT.
- Os renders antigos de `sprites/efeitos_blender/<lutador>/especial_*`, `super_*` e `carga_*` não são mais usados por
  Pengaró, Gutto, CK e Raiclaven; podem sair do repositório depois do OK do Breno.
