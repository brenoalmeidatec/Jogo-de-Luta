# Pausa 17/11/2026: Grão-Pastor (Gbzin despertado)

## O que está pronto (na `mugen`)
- **31 estados com desenho próprio** do Grão-Pastor (folhas `e_*` em `sprites/gbzin/quadros/folhas_arcade/`), ligados pelo `GRAO_PASTOR` em `ferramentas/gerar_gbzin.py`.
- **Agarrão ligado**: base `agarrao` → `e_agarrao` com `(0, 1, 5, 6, 6, 6, 7, 0)` (pega na garganta, ergue, enterra). Vídeo: `docs/boneco-pecas/gbzin/grao_pastor_agarrao.mp4`.
- **Kit de peças próprio** (`ferramentas/kit_grao_pastor.py`, kit em `sprites/gbzin/pecas_e/corpo/`): parado, chifrada (8→10 quadros) e estampido (7→17) já posados com ele, grupo 49000 (`ligar_pecas.py --pasta quadros_e_pecas_hd`). Provas em `docs/boneco-pecas/gbzin/grao_pastor_*`.
- Robô: `python3 ferramentas/testar_pengaro.py --linux --lutador gbzin` → 236/0. Conferência das folhas: 0 defeitos.

## Próximos passos exatos
1. Repor os outros golpes do Grão-Pastor no kit (`kit_grao_pastor.py animar NOME`), usando as folhas `e_*` como guia de pose; seguir o meio-termo (quadros do meio na preparação/volta/guarda, só um borrão antes do contato) e o estudo de anatomia.
2. Pôr o kit do Grão-Pastor no `montador.py`.
3. Arte já pronta e ainda sem golpe: `e_estouro`, `e_manto_asa`, `e_berro` (golpes próprios futuros).
4. Golaço do Grão-Pastor ainda não foi filmado com barra cheia.
5. Agarrão: conferir se o "enterra" (quadro 6) cai junto com a vítima; se não, ajustar os tempos do 830.

## Regras que valem
- Fotos do rapaz real só na branch `gbzin-fotos`. Ao juntar na mugen, tirar `ferramentas/fila_gbzin_pedidos.png` (`git rm --cached`).
- Artes no ChatGPT do Chrome "Browser 2" (PC de casa); anotar cada imagem em `imagens/fila-chatgpt.md` e apagar o chat.
- Branch de trabalho: `claude/project-thread-hxlioc`.
