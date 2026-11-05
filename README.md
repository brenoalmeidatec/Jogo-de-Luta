# Jogo de Luta

Jogo de luta 2D original.

## Gerar sprites com a API da OpenAI

O script `ferramentas/gerar_sprites.py` cria os sprites dos personagens (definidos em
`ferramentas/personagens.json`) usando a API de imagens da OpenAI.

```powershell
pip install openai
$env:OPENAI_API_KEY = "sk-..."   # sua chave de platform.openai.com (não faça commit dela!)
python ferramentas/gerar_sprites.py --personagem kaio --qualidade low
```

As imagens saem em `sprites/<personagem>/` com fundo transparente.
