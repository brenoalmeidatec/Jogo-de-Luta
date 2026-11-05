# Jogo de Luta

Jogo de luta 2D em pixel art feito para rodar no [IKEMEN GO](https://github.com/ikemen-engine/Ikemen-GO),
motor gratuito e de código aberto que roda personagens de MUGEN. O motor já cuida de menus, CPU, treino,
modo times, tontura e quebra de guarda; aqui ficam os personagens.

## Jogar (Windows)

Coloque `ferramentas/Jogo de Luta.bat` na Área de Trabalho (ou um atalho para ele) e dê dois cliques.
A cada clique ele baixa a versão mais nova deste repositório, coloca o Pengaró no motor e abre o jogo.
Na primeira vez ele também baixa o IKEMEN GO. Tudo fica em `%USERPROFILE%\JogoDeLuta`.

Os botões do personagem são x (soco fraco), y (soco forte), a (chute fraco), b (chute forte) e
c (provocação). As teclas de cada botão ficam nas opções do IKEMEN.

## Pengaró

Capoeirista e boleiro. Fica em `chars/pengaro/`.

| Mecânica | Comando |
|---|---|
| Corrida / passo para trás | frente, frente / trás, trás |
| Pulinho, pulo, hiper pulinho, super pulo | toca cima, segura cima, baixo e toca cima, baixo e segura cima |
| Rolamento | x + a (com trás rola para trás) |
| Golpe de afastar | y + b, no chão ou no ar |
| Agarrão | colado, frente ou trás + y ou b (y ou b escapa) |
| Levantar rápido | x + a ao cair (não vale depois de rasteira, agarrão e super) |
| Guard cancel (1 estoque) | na defesa: x + a rola, y + b afasta |
| Corrente de fracos | até 4 golpes fracos seguidos no contato |

| Especial | Comando |
|---|---|
| Bola de Sombra | baixo, frente + a (lenta) ou b (rápida) |
| Meia-lua de Compasso Sombria | baixo, trás + a ou b |
| Armada do Quilombo | frente, baixo + x ou y |
| Caneta | baixo, trás + x ou y |
| Golaço da Noite (1 estoque) | trás, frente, baixo + a ou b |
| Pelada Sombria | o mesmo comando durante o Despertar, ou com 20% de vida e 2 estoques |
| Despertar: Lata Gelada (1 estoque) | x + a + y |

A lista de golpes também aparece no menu de pausa do jogo. O nome dos especiais trava na gagueira e só sai inteiro se o golpe acertar; no Despertar ele fala liso. A gagueira é só balão e nunca muda o tempo dos golpes.

## Mudar o personagem

Os arquivos de `chars/pengaro/` são gerados. Mude golpes, danos e falas em `ferramentas/gerar_pengaro.py`
e rode:

```powershell
pip install pillow
python ferramentas/gerar_pengaro.py
python ferramentas/verificar_pengaro.py
```

## Gerar sprites novos (API de imagens da OpenAI)

```powershell
pip install openai pillow
$env:OPENAI_API_KEY = "sk-..."   # chave de platform.openai.com (nunca faça commit dela!)
python ferramentas/gerar_sprites.py --personagem kaio --qualidade low
```

Personagens, estilo e poses ficam em `ferramentas/personagens.json`. O `ferramentas/pixelizar.py` converte
tudo em pixel art de 112 px de altura. Veja `docs/proporcoes.md` para as proporções.

## Efeitos

Os efeitos do pixelfx continuam em `assets/efeitos/` (veja o LEIA-ME de lá), integrados aos impactos e à defesa do Pengaró.

## Animação

Nenhum golpe pula direto de uma pose para outra. Os quadros ficam em `sprites/pengaro/quadros/`;
os de chute e agachar saem de `ferramentas/quadros_intermediarios.py` (precisa de `pip install numpy opencv-python-headless`).
Recursos livres que dá para aproveitar estão em `docs/recursos-github.md`.
