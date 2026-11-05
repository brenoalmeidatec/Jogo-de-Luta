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
