# Jogo de Luta

Jogo de luta 2D em pixel art feito para rodar no [IKEMEN GO](https://github.com/ikemen-engine/Ikemen-GO),
motor gratuito e de código aberto que roda personagens de MUGEN. O motor já cuida de menus, CPU, treino,
modo times, tontura e quebra de guarda; aqui ficam os personagens.

**Todo lutador segue as [Regras de todo lutador](docs/regras-dos-lutadores.md)**: comandos no estilo Mortal Kombat,
correntes de 3 golpes + finalizador em cada botão, 8 especiais, 2 projéteis, 3 agarrões, Despertar com golpes novos,
e criação com as ferramentas e os efeitos pixelfx listados lá.

## Jogar (Windows)

Coloque `ferramentas/Jogo de Luta.bat` na Área de Trabalho (ou um atalho para ele) e dê dois cliques.
A cada clique ele baixa a versão mais nova deste repositório, instala os lutadores e abre o jogo.
Na primeira vez ele também baixa o IKEMEN GO. Tudo fica em `%USERPROFILE%\JogoDeLuta`.

Os botões do personagem são x (soco fraco), y (soco forte), a (chute fraco), b (chute forte) e
c (provocação). O atalho deixa o jogador 1 assim (e refaz isso a cada clique):

| Tecla | Ação |
|---|---|
| W / A / S / D | cima (pulo) / trás-esquerda / baixo (agachar) / direita |
| Seta esquerda | x, soco fraco |
| Seta cima | y, soco forte |
| Seta baixo | a, chute fraco |
| Seta direita | b, chute forte |
| C | c, provocação |
| Enter | start |

**Nos menus** (título, modos, seleção de personagem e de cenário, opções, pausa): W/A/S/D movem o cursor e
**Enter confirma**. As setas não confirmam nada nos menus, só batem na luta. Esc volta.

Outras teclas e o jogador 2 continuam nas opções do IKEMEN.

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
| Mão de Chimpá | baixo, frente + x ou y |
| Sola de Várzea | trás, baixo + a ou b |
| Bando da Várzea (2 estoques) | trás, frente, baixo + x ou y |

## Hazaki

Karateca de guarda firme, com golpes de alcance e antiaéreos. No Despertar, vira o Diabo Loiro.

| Especial | Comando |
|---|---|
| Punho de Concreto | baixo, frente + x ou y |
| Guarda de Aço | baixo, trás + x ou y |
| Ascensão de Faixa | frente, baixo + x ou y |
| Giro de Garagem | baixo, frente + a ou b |
| Corte de Base | baixo, trás + a ou b |
| Salto de Dojô | trás, baixo + a ou b |
| Faixa no Asfalto (1 estoque) | trás, frente, baixo + a ou b |
| Pose Final (2 estoques) | trás, frente, baixo + x ou y |
| Despertar: Diabo Loiro (1 estoque) | x + a + y |

Os dois podem aparar golpes físicos com frente + c. As quatro teclas de ataque têm golpes
próprios em pé, agachados e no ar. Em pé, frente + y/b e trás + x/a dão golpes direcionais.
À distância de agarrão, frente ou trás + y/b dá prioridade ao agarrão.

A lista de golpes também aparece no menu de pausa do jogo. O nome dos especiais trava na gagueira e só sai inteiro se o golpe acertar; no Despertar ele fala liso. A gagueira é só balão e nunca muda o tempo dos golpes.

## Mudar o personagem

Os arquivos de `chars/pengaro/` são gerados. Mude golpes, danos e falas em `ferramentas/gerar_pengaro.py`
e rode:

```powershell
pip install pillow
python ferramentas/gerar_pengaro.py
python ferramentas/gerar_hazaki.py
python ferramentas/verificar_pengaro.py
python ferramentas/verificar_pengaro.py --hazaki
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
