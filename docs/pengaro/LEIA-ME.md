# Pengaró: tudo num lugar só

O jogo continua usando a animação que já estava na `mugen` (parado, andando e soco com as folhas de 8 quadros).
Esta pasta guarda o que foi testado para deixar o movimento fluido, para retomar quando o Breno quiser.

## Prévias (`previas/`)
| Arquivo | O que é |
|---|---|
| `ginga-48-quadros.gif` | recortes do sprite antigo movidos por esqueleto próprio (`ferramentas/rig_pengaro.py`) |
| `ginga-pixelfx-48-quadros.gif` | personagem todo feito pelo esqueleto 3D do pixelfx, em 38 px (pixel grosso) |
| `ginga-pixelfx-112px.gif` | o mesmo em 112 px, com volume e listras, sem rosto nem abdômen |
| `ginga-sprite-do-jogo-pixelfx.gif` | **melhor resultado:** sprite do jogo (`quadros/parado/00.png`) movido pelo pixelfx |

Nenhuma delas está ligada no `.air`. O Breno decidiu deixar o jogo como está.

## Ferramentas
- `ferramentas/pixelfx_rig/` esqueleto 3D copiado do pixelfx (MIT, `LICENSE-pixelfx`), com escala para 112 px,
  `renderizar_pengaro.mjs` (pinta o Pengaró) e `trajetoria.mjs` (posição de mãos, pés e quadril por quadro).
- `ferramentas/rig_pengaro.py` recorta o sprite em partes e aplica a trajetória:
  `node ferramentas/pixelfx_rig/trajetoria.mjs ginga 48 t.json && python ferramentas/rig_pengaro.py saida.gif t.json`

## Experimentos antigos (`experimentos/`)
`pengaro_fluido.py` (deformação por fluxo óptico) e `recursos-github.md` (lista de ferramentas abertas).

## Para retomar
Falta: tirar o pedaço de ombro fora do lugar, fazer andar e soco, e ligar no `.air` com 16 a 48 desenhos por
animação (regra da seção 7 de `docs/regras-dos-lutadores.md`).
