# Nazafight

**Nazafight** é um jogo de luta 2D em pixel art feito para rodar no [IKEMEN GO](https://github.com/ikemen-engine/Ikemen-GO),
motor gratuito e de código aberto que roda personagens de MUGEN. O motor já cuida de menus, CPU, treino,
modo times, tontura e quebra de guarda; aqui ficam os personagens.

**Todo lutador segue as [Regras de todo lutador](docs/regras-dos-lutadores.md)**: comandos no estilo Mortal Kombat,
correntes de 3 golpes + finalizador em cada botão, 8 especiais, 2 projéteis, 3 agarrões, Despertar com golpes novos,
e criação com as ferramentas e os efeitos pixelfx listados lá.

## Jogar (Windows)

Coloque `ferramentas/Jogo de Luta.bat` na Área de Trabalho (ou um atalho para ele) e dê dois cliques.
A cada clique ele baixa a versão mais nova deste repositório, instala os lutadores e abre o jogo.
Na primeira vez ele também baixa o IKEMEN GO. Tudo fica em `%USERPROFILE%\JogoDeLuta` (a pasta e o arquivo `.bat`
mantêm o nome antigo de propósito, para não quebrar o atalho nem baixar o motor de novo; a janela já abre como Nazafight).

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

Capoeirista cachaceiro: luta com uma garrafa de whisky na mão e arremessa lata de cerveja. Fica em `chars/pengaro/`.

| Mecânica | Comando |
|---|---|
| Corrida / passo para trás | frente, frente / trás, trás |
| Pulinho, pulo, hiper pulinho, super pulo | toca cima, segura cima, baixo e toca cima, baixo e segura cima |
| Rolamento | x + a (com trás rola para trás) |
| Golpe de afastar | y + b, no chão ou no ar |
| Agarrão em pé | colado, frente ou trás + y ou b (y ou b escapa) |
| Agarrão agachado | colado em quem está agachado, baixo + y: pega a perna e arremessa de rasteira (110) |
| Martelo e Garrafada (agarrão de comando) | colado, trás, frente + y: compasso de capoeira (60) e garrafa de whisky na cabeça (90) |
| Levantar rápido | x + a ao cair (não vale depois de rasteira, agarrão e super) |
| Guard cancel (1 estoque) | na defesa: x + a rola, y + b afasta |
| Correntes | cada botão (x, y, a, b) tem 3 golpes: aperte o mesmo botão de novo a cada contato. Acertando os 3, o 4º é o finalizador e derruba |
| Kombos de assinatura | **Abertura** frente + y, x, b · **Alto e Baixo** x, baixo + a, y (o último é por cima) · **Empurrão** trás + x, y, frente + b · **Lançador** a, b, baixo + y (lança para o ar) |
| Corrente de fracos | até 4 golpes fracos seguidos no contato (agachado e misturados) |

| Especial | Comando |
|---|---|
| Latada de Sombra (arremessa uma lata de cerveja) | baixo, frente + a (lenta) ou b (rápida) |
| Meia-lua de Compasso Sombria | baixo, trás + a ou b |
| Armada do Quilombo | frente, baixo + x ou y |
| Caneta | baixo, trás + x ou y |
| Chuva de Bebidas (1 estoque): garrafas e latas caem do céu no oponente | trás, frente, baixo + a ou b |
| Saideira Sombria | o mesmo comando durante o Despertar, ou com 20% de vida e 2 estoques |
| Garrafada em Arco (2º projétil, passa por cima de golpe baixo) | frente, trás + x (curta) ou y (longa) |
| Rolê por Trás (passa por dentro do oponente e chega virado; no canto fica na frente) | frente, trás + a (só passa) ou b (passa e chuta) |
| Mão de Chimpá | baixo, frente + x ou y |
| Sola de Várzea | trás, baixo + a ou b |
| Bando da Várzea (2 estoques) | trás, frente, baixo + x ou y |
| Despertar: Lata Gelada (barra cheia, gasta tudo) | x + y |

**No Despertar** (forma endiabrada) o Pengaró ganha golpes que não existem na forma normal:

| Exclusivo | Comando |
|---|---|
| Mão de Sombra (projétil novo, acelera e acerta duas vezes) | baixo, baixo + x |
| Chute da Corrente (avanço longo, derruba) | baixo, baixo + y |
| Sombra Atravessada (passa batendo e chega nas costas) | baixo, baixo + a |
| Queda Escura (mergulho que racha o chão) | baixo, baixo + b |
| Correntes novas de 4 golpes | y, y, y, y e b, b, b, b |
| Kombo Possessão | b, a, x |
| 6 normais novos | baixo + y, baixo + b, frente + y, frente + b, trás + x, trás + a |

## Gutto

Lutador de Muay Thai, de camiseta nenhuma, calção de cetim e braçadeiras de corda. Fica em `chars/gutto/`. Tem o mesmo kit
completo do Pengaró (4 correntes de 3 golpes + finalizador, 4 kombos, 8 especiais, 3 agarrões, Despertar `x + y`, golpes
exclusivos), com os mesmos comandos, só que de chute, joelhada e cotovelo.

| Especial | Comando |
|---|---|
| Beijinho (projétil reto, um coração) | baixo, frente + a (lento) ou b (rápido) |
| Beijinho em Arco (projétil em arco) | frente, trás + x (curto) ou y (longo) |
| Teleporte de Ginga (a só passa, b passa e chuta) | frente, trás + a ou b: aparece atrás do oponente |
| Chute Giratório (coice) | baixo, trás + a ou b |
| Joelhada Voadora | frente, baixo + x ou y |
| Carrinho | baixo, trás + x ou y |
| Clinch e Joelhada (agarrão de comando) | colado, trás, frente + y |

Hoje o Gutto está **sem a forma de cavalo**: o Despertar existe e funciona, mas usa uma versão escurecida das poses
normais. A arte do Endiabrado (cabeça de cavalo) e 5 folhas provisórias (`ferramentas/provisorios_gutto.py`) esperam o
limite de imagens do ChatGPT liberar. Ficha em `docs/fichas/gutto.md`; gerar com `python ferramentas/gerar_gutto.py`;
testar com `python ferramentas/testar_pengaro.py --lutador gutto`.

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
