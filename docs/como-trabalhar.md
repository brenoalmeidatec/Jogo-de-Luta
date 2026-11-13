# Como trabalhar neste jogo

Este é o jeito de trabalhar definido pelo Breno em 2026-11-06, e vale para o resto do jogo. Se `AGENTS.md`,
`docs/missoes-codex.md` ou `docs/pedidos-para-claude.md` disserem outra coisa, vale este arquivo. As regras dos lutadores
continuam em [`regras-dos-lutadores.md`](regras-dos-lutadores.md). Estilo e cores ficam na
[`biblia-de-arte.md`](biblia-de-arte.md), e o que conferir antes de subir, em [`conferencia-de-golpe.md`](conferencia-de-golpe.md).

## Regras do Breno

- **Sem Codex.** O Claude faz o trabalho e não pede nada ao Codex.
- **Sem PR.** Verifique e suba direto na branch `mugen`, sem perguntar. Depois diga o que entrou e o que não foi testado.
- **Não fique pedindo coisas.** Resolva sozinho e chame o Breno só para o que for impossível sem ele.
- **Imagens no ChatGPT**, pelo navegador embutido do app do Claude, com a conta do Breno. Ele faz o login.
- **Um chat por personagem**, com o nome do lutador no título, para não misturar.
- **Tudo na pasta do jogo:** `sprites/<lutador>/quadros/folhas/`. Nada fica em Downloads.
- **O jogo se chama Nazafights** (com "s"). Só os caminhos técnicos antigos (`JogoDeLuta`, `motif/nazafight`,
  `Jogo de Luta.bat`) ficam como estão, para não quebrar o launcher de quem já tem.
- **Estilo arcade anos 90 é a regra** (definido pelo Alisson, confirmado pelo Breno em 2026-11-10): toda arte nova de
  lutador, efeito e transformação segue a seção
  [Estilo arcade anos 90 da bíblia](biblia-de-arte.md#estilo-arcade-anos-90), com as 12 regras, a paleta fixa e o
  pipeline `quantizar_folha` → `animar_folha --arcade` → `conferir_arte`. A arte antiga sai conforme as folhas arcade
  forem entrando. Nunca 3D pixelizado: o boneco 3D do PR #17 foi rejeitado.
- **Quem faz o quê** (Breno, 2026-11-12): o Breno e o Claude desenham, isto é, ficha, folhas no ChatGPT e o pedido em
  `.md`, e **mandam para o Alisson**. O Alisson coloca no jogo, sempre na regra do 3x
  ([`regra-alta-resolucao.md`](regra-alta-resolucao.md)) e com os efeitos pela
  [`regra-efeitos-proporcionais.md`](regra-efeitos-proporcionais.md). O Claude não liga sprite novo no jogo, a não ser
  que o Breno peça.
- **Efeitos simples e do tamanho do golpe** (Breno, 2026-11-12): golpe fraco tem só um ventinho, e golpe forte que joga
  longe tem impacto maior. **O endiabrado não muda:** aura grande e monstruosa e os efeitos dele como eram (correção do
  Breno, 2026-11-13). Efeitos novos são feitos no Blender. Tudo em
  [`regra-efeitos-proporcionais.md`](regra-efeitos-proporcionais.md).
- **Lutador em alta resolução é a regra** (Breno, 2026-11-12): o corpo vai para o jogo desenhado em 3x e mostrado em
  1/3, para o motor não esticar e o boneco não ficar borrado. Folha nova ou refeita ganha o gêmeo 3x antes de subir.
  Tudo em [`regra-alta-resolucao.md`](regra-alta-resolucao.md).
- **Blender só deforma os sprites desenhados** para criar os quadros do meio. Nunca modela o personagem.
- **Proporção de KOF:** os lutadores em escala 1, cerca de 110 de 180 de altura de tela.
- **Conteúdo:** resenha pesada pode. Não pode piada de escravidão nem o estereótipo da mulher loira. Lata e garrafa sem
  marca. Gostar de chimpanzés faz parte da história do Pengaró.

## Personagem do Pengaró

- Forma normal: garrafa de whisky na mão de trás, desenhada em todo quadro.
- Despertar: ele bebe, vê a garrafa vazia, joga no chão, ela quebra e as sombras o possuem.
- Endiabrado: **boss final** (conceito aprovado em 2026-11-11, `sprites/pengaro/quadros/folhas_arcade/e_conceito.png`).
  Mesmo rosto, corpo e altura, **sem garrafa**; pele marrom-escura arroxeada, olhos violeta sem pupila, cabelo comprido
  e revolto com pontas violeta, dois chifres curtos de fumaça; casaco de mestre preto sem manga com friso dourado e
  forro roxo, barra rasgada até a canela; rachaduras violeta no peito; corda trançada ouro e violeta; calça preta com
  barra em brasa; algemas de corrente partida nos dois pulsos e nos dois tornozelos; braceletes de ouro. A aura (coluna
  de fumaça, anel de sombra no chão, elos e pedras flutuando) é efeito à parte, em três Explod. Lote 7 ligado em
  2026-11-11: `quadros_arcade/e_<golpe>/` (paleta `paleta_arcade_endiabrado.json`, conversão em
  `ferramentas/retoques_arcade/lote7_converter.py`); só a primeira metade da cena do Despertar (`despertar_a`) segue antiga.

## Preparar outra máquina

```bash
git clone https://github.com/brenoalmeidatec/Jogo-de-Luta.git
```

```bash
git switch mugen
```

```bash
pip install pillow numpy opencv-python-headless
```

O Blender é a versão portátil 4.5 LTS, baixada de `download.blender.org/release/Blender4.5/` e conferida pelo `.sha256`.
`animar_folha.py` usa a variável `BLENDER` ou acha o mais novo `blender-4.5.*-windows-x64` em `~/blender` ou
`C:/Dev/Tools/Blender` (onde fica no PC de teste: 4.5.15). Sem Blender dá para trabalhar em tudo, menos nos quadros do meio novos.

O jogo roda no IKEMEN GO v1.0.0. O Claude não consegue abrir o `Ikemen_GO.exe` neste PC do trabalho; quem testa é o Breno.
O atalho `Jogo de Luta.lnk` baixa a `mugen` ao abrir. Antes de concluir qual versão ele testou, compare o tamanho do `.sff`
em `ikemen\chars\<lutador>`. Erros ficam em `ikemen\save\logs`.

## Como fazer um lutador ou um golpe novo

1. **Ficha:** siga a seção 10 das regras e liste os golpes.
2. **Folha-referência:** gere uma folha boa e confira personagem e cor. Ela fica na biblioteca do ChatGPT.
3. **Folhas:** uma por movimento, com 8 quadros em fila e fundo magenta `#FF00FF`.
   Mande sempre a referência anexada. Use `ferramentas/chatgpt_folhas.js` para automatizar a página.
4. **Revisão:** monte uma folha de contato e olhe todas. Meça o matiz da pele, porque o personagem desvia sem aviso.
5. **Blender:** `python ferramentas/animar_folha.py <nomes>` ou `--todas`. Cada intervalo entre desenhos ganha 6 quadros do
   meio, em `quadros/<nome>/meio/`.
6. **Gerador:** ligue no `gerar_<lutador>.py`. O gerador usa até um desenho por tick, sem mudar caixas nem frame data.
7. **Verificar:** `python ferramentas/verificar_pengaro.py` e `--hazaki`, depois `ferramentas/conferir_tempo.py` e
   `ferramentas/conferir_despertar.py`. **Sempre** feche o controle de qualidade com vídeo curto e análise quadro a
   quadro: `python ferramentas/video_golpe.py PASTA <ações>` (5 a 10 s a 60 fps, tira com todos os ticks) e assista
   tick a tick a toda ação mexida, como manda a [`conferencia-de-golpe.md`](conferencia-de-golpe.md).
8. **Subir:** commit e `git push origin mugen`.

Formas transformadas: gere a folha `e_<golpe>` para cada movimento, nos mesmos 8 tempos da normal. O
`[RemapPreset despertado]` troca os sprites em qualquer animação, sem mexer na lógica dos estados.

## ChatGPT na prática

Chats, na conta do Breno:

- Pengaró: `chatgpt.com/c/6aedc940-1554-83e9-8fd3-f7f26e9b8c02`, referência "Socos" na biblioteca.
- Pengaró endiabrado: `chatgpt.com/c/6aedf8e0-e03c-83e9-90ac-d2df1778cdca`. É o chat da arte antiga (referência `e_soco.png`
  antiga, corpo quase preto). Para o boss final (Lote 7 de `docs/arcade/fila.md`) abra um chat novo e anexe em toda
  mensagem `folhas_arcade/e_conceito.png` mais a folha arcade normal do golpe.
- Efeitos do Pengaró: `chatgpt.com/c/6aef1007-b9b0-83e8-9958-ca11fa475ce5`, fundo verde. Título "Generate Pixel Art Sprite
  Sheet"; renomeie.
- Anexar sem a janela de arquivo: um `File` feito do blob guardado em `__f` vai para o `input[type=file]` da página por
  `DataTransfer`. Assim a referência entra mesmo quando a biblioteca ainda não mostra a imagem nova.

Fluxo: cole `ferramentas/chatgpt_folhas.js` pela ferramenta de JavaScript do navegador e, para cada folha, rode
`__a(busca)`, `__e(prompt)`, espere e rode `__sx(nome)`. No fim, `__pacote()` baixa tudo num `.tar` só, e
`python ferramentas/baixar_folhas.py pengaro` extrai na pasta do jogo.

Armadilhas já pagas:

- **Reanexe a referência em toda folha.** Sem isso, em conversa longa o tom de pele foi de 23° a 32° e ele perdeu a faixa.
- **Espere uma folha terminar antes de enviar a próxima.** Dois envios seguidos viram uma mensagem só.
- **Diga "standing tall"** nas folhas em pé. Depois de folhas agachadas ele passa a usar a guarda baixa.
- Algumas folhas vêm com faixa branca ou cinza em cima e embaixo. Pinte de magenta antes do recorte.
- As folhas vêm em tamanhos diferentes; `animar_folha.py` ajusta a escala pela largura.
- **Não anexa sozinho na primeira vez:** a primeira imagem enviada do disco precisa do Breno. O Claude não controla a
  janela de arquivo. Depois disso ela fica na biblioteca.
- Download por botão abre "Salvar como" a cada folha. Por isso o `__pacote()`. Copie o `.tmp` de Downloads na hora, porque
  ele some quando a janela fecha.
- Limites do navegador: 25 ações e uns 200 s por lote, 45 s por script.

## Testes só na sandbox (regra do dono, 2026-11-10)

No PC de teste, nada abre o `Ikemen_GO.exe` na máquina local: robô, filmagem e validação do motor rodam dentro do
Windows Sandbox (sem rede, sem vGPU, OpenGL por software do Mesa). `ferramentas/sandbox.py` é a base (copia o motor,
aplica uma pasta por cima, roda e traz `save/logs` e o arquivo de resultado de volta; espera a vez se outra sandbox estiver
aberta). `testar_pengaro.py` usa a sandbox por padrão e `filmar_sandbox.py` filma. `filmar_luta.py` só roda com `--local`.

## Regras técnicas aprendidas

- Com `localcoord = 320,240` e palco 16:9, a tela em unidades do lutador é 320 x 180. `ScreenWidth` e `ScreenPos` já vêm
  nessa unidade.
- `RITMO = 1.5` em `gerar_pengaro.py` alonga os golpes dos dois lutadores, com o atordoamento junto. Mostrar 8 desenhos no
  tempo antigo parecia o jogo em 2x.
  No Pengaró o **preparo** (os desenhos antes da caixa de golpe) não é esticado (`RITMO_PREPARO = 1.0`): só o resto do golpe
  e o atordoamento usam o `RITMO`. Fraco 3-5 ticks até encostar, forte 7-10 (regra 8.3).
- Desenhos a mais de 3 de distância ficam em corte seco. Atravessar tudo no meio fazia o corpo se debater.
- Ciclos de ginga levam uns 2 segundos, com 64 quadros a 2 ticks.
- `remapear_animelem` ajusta o `AnimElem` do `.cns`, porque os quadros do meio mudam a contagem.
- Regenerar os dois lutadores: `gerar_pengaro.py` e `gerar_hazaki.py`. Confira o diff do `.cns` do outro lutador.

## Estado em 2026-11-07

- O IKEMEN roda neste PC: `ferramentas/filmar_luta.py PASTA --despertar 12` filma uma luta CPU x CPU, e
  `ferramentas/auditar_pengaro.py PASTA` mede cada quadro.
- Quadros alinhados pelo tronco, bordas limpas e endiabrado alinhado ao normal: desalinhados caíram de ~152 ações para
  33 quadros, todos de altura no pulo.
- Efeitos encaixados no elemento em que a caixa de golpe liga. Normal: faísca e brilho dourados de whisky, poeira
  dourada na rasteira. Endiabrado: aura violeta pulsando, sombra girando nos pés, corte e poeira violeta nos golpes.
  Rastro do especial em soma violeta (o Hazaki também ganhou esse rastro).
- Visto na filmagem; ainda não jogado por uma pessoa. O roxo forte do endiabrado vem das folhas do ChatGPT, não do
  gerador. Os buracos de fumaça nas pernas também são do desenho.

## Estado em 2026-11-06 (atualizado no fim do dia)

O kit do Pengaró passou a ter, no código, tudo que o checklist da seção 9 pede: 4 correntes de 3 golpes + finalizador,
4 kombos, 8 especiais (2º projétil em arco e Rolê por Trás), 3 agarrões, Despertar em `x + y` com barra cheia e os 20 golpes
exclusivos (dados em `ferramentas/pengaro_extra.py`, ficha em `docs/fichas/pengaro.md`). A arte desses golpes novos ainda
reaproveita folhas existentes. Há um teste automático (`python ferramentas/testar_pengaro.py`, robô em `ferramentas/robo/`): 126
verificações passam. Nenhuma pessoa jogou ainda; o que o robô não sente é ritmo, peso e se a transformação parece certa.

Estado anterior, do commit `68af3ec`:

Ainda **não testado no jogo** por ninguém, desde o commit `68af3ec`: ritmo novo, escala 1, golpes de capoeira, Despertar sem
garrafa e transformação. Primeiro passo em casa: abrir uma luta e conferir isso.

Conferir com atenção:

- se o Despertar vira endiabrado de verdade: `RemapSprite` foi lido no código do motor, nunca visto rodando;
- pés, caixas de golpe e correntes com `RITMO = 1.5`.

Pendências:

- 72 de 159 ações têm desenho acima de 2 ticks (regra 7);
- pontinhos de fumaça soltos em quadros da possessão;
- falas: os balões estão desligados (`BALOES_LIGADOS` em `gerar_pengaro.py`). O Breno vai gravar os áudios e mandar; aí
  eles entram no jogo. Os textos em `BALOES` ficam como roteiro;
- `golaco` usa o início da folha, porque os quadros com chuva passam da tela;
- Barbeiro: ficha pronta em `docs/fichas/barbeiro.md`, lutador ainda não feito.
