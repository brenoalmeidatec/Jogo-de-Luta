# Jogo de Luta

Jogo de luta 2D original em pixel art (Godot), no estilo do [pixelfx](https://patch-gg.github.io/pixelfx/).

## Gerar os personagens (API de imagens da OpenAI)

```powershell
pip install openai pillow
$env:OPENAI_API_KEY = "sk-..."   # chave de platform.openai.com (nunca faça commit dela!)
python ferramentas/gerar_sprites.py --personagem kaio --qualidade low
```

1. Gera uma imagem de referência do personagem e uma imagem por pose (`sprites/kaio/`).
2. Converte tudo em pixel art com `ferramentas/pixelizar.py`: 112 px de altura (escala KOF), 24 cores chapadas
   e contorno escuro de 1 px (`sprites/kaio/pixel/`), mais a folha `kaio.png` + `kaio.json`.

Personagens, estilo e poses ficam em `ferramentas/personagens.json`.

## Efeitos (pixelfx)

Faíscas de golpe, defesa, impacto e projéteis já exportados em `assets/efeitos/` (veja o LEIA-ME de lá).

No Godot, importe os PNGs com **Filter = Nearest**.

## Proporções e HUD

Tela base 304x224, personagens de 104 a 128 px. Veja `docs/proporcoes.md` e `ferramentas/hud_layout.json`.

## Jogar (Godot)

1. Instale a [Godot 4.3](https://godotengine.org/download) ou mais nova (versão padrão, não precisa da .NET).
2. Na Godot, clique em **Importar**, escolha o `project.godot` desta pasta e depois em **Importar e editar**.
3. Aperte **F5** para jogar.

Ou use o atalho `ferramentas/Jogo de Luta.bat` (Windows): coloque na área de trabalho e dê dois cliques.
Ele baixa a versão mais nova do GitHub, usa a Godot 4.3+ que já estiver no computador (ou baixa uma) e abre o jogo.
Tudo fica em `%LOCALAPPDATA%\JogoDeLuta`.

A tela base é 304x224 (resolução de arcade, proporção do KOF), ampliada 4x numa janela de 1216x896.
Os personagens normais têm 112 px, metade da altura da tela, e o HUD segue `ferramentas/hud_layout.json`.

### Controles

| | Jogador 1 | Jogador 2 | Controle |
|---|---|---|---|
| Mover / pular / agachar | W A S D | Setas | Direcional ou analógico |
| Soco fraco / forte | U / I | Numpad 4 / 5 | X / Y |
| Chute fraco / forte | J / K | Numpad 1 / 2 | A / B |
| Mostrar hitboxes | F1 | | |

Segurar **trás** defende. Golpes baixos só são defendidos agachado (baixo-trás). Golpes no ar só em pé.

### Golpes

| Golpe | Comando |
|---|---|
| Socos e chutes em pé, agachado e no ar | botão (com baixo para agachado) |
| Gancho anti-aéreo | baixo + soco forte |
| Rasteira (derruba) | baixo + chute forte |
| **Rajada** (projétil) | baixo, baixo-frente, frente + soco |
| **Chute Ciclone** (avança e derruba) | baixo, baixo-trás, trás + chute |

Golpes fracos, o soco forte e os golpes agachados podem ser **cancelados** num especial quando acertam,
por exemplo: agachado chute fraco, agachado soco fraco, Rajada.

### Como o código está organizado

| Arquivo | O que faz |
|---|---|
| `scripts/match.gd` | a luta: rounds, tempo, câmera, colisão dos golpes, congelamento no impacto |
| `scripts/fighter.gd` | o lutador: estados, física, dados de quadro de cada golpe, comandos de especial |
| `scripts/hud.gd` | barras de vida e especial, tempo, retratos, combos, mensagens |
| `scripts/effects.gd`, `scripts/fx_library.gd` | faíscas e efeitos do pixelfx |
| `scripts/projectile.gd` | o projétil da Rajada |
| `scripts/controls.gd` | teclas e controles |

Toda a lógica roda em quadros fixos (60 por segundo), sem depender do tempo real. Isso mantém os combos
consistentes e deixa o caminho aberto para um modo online com rollback.

Enquanto os sprites não existem, os lutadores são desenhados com formas simples. Quando houver
`sprites/kaio/pixel/kaio.png` + `kaio.json` (gerados por `ferramentas/pixelizar.py`), o jogo usa o sprite
automaticamente. O jogador 1 é o Kaio e o jogador 2 é o Brutus (`scripts/match.gd`).
