# Efeitos de luta (pixelfx)

Folhas de sprites geradas com o [pixelfx](https://github.com/patch-gg/pixelfx) (licença MIT, Patch; partes adaptadas
de Sprite Fusion, Hugo Duprez, e Hollow Crown). Veja `LICENSE-pixelfx.txt`.

Cada efeito tem um `.png` transparente e um `.json` (estilo Aseprite) com os quadros, a duração e o `meta.pixelfx`
(fps, loop, colunas, pivô).

| Arquivo | Uso no jogo |
|---|---|
| hit-spark, hit-flash, blunt-hit | golpe fraco / médio acertando |
| crit-hit | golpe forte ou contra-ataque |
| shield-block, parry | defesa |
| heavy-landing, ground-slam | queda no chão / golpe no chão |
| uppercut | rastro do gancho |
| fireball, energy-disc | projéteis dos especiais |
| zap-hit, charge-up | especial elétrico / carregando o especial |

No Godot: importe o PNG com **Filter = Nearest** (para não borrar o pixel art) e crie um `AnimatedSprite2D`
usando os retângulos de `frames` do JSON. Para gerar mais efeitos, rode `ferramentas/exportar_efeitos.sh`.
