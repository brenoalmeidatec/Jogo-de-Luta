# Estudo: como deixar os lutadores consistentes

Estudo pedido pelo Breno em 2026-11-15. Cópia do relatório
[no Claude](https://claude.ai/artifact/St9ULungSxHymy3eq4kxWy). A missão que põe isto em prática é a
[`missao-alisson-boneco-de-pecas.md`](missao-alisson-boneco-de-pecas.md).

Os bonecos deformam porque hoje cada quadro é desenhado do zero pela IA, e nenhum jogo de luta profissional trabalha
assim: todos partem de um modelo fixo e constroem cada quadro em cima do anterior. A recomendação é trocar a unidade de
trabalho: a IA faz o modelo e as peças, e as poses saem de um boneco de peças montado por código, retocado pixel a pixel.

## Por que os nossos deformam

O defeito vem do processo, não de falta de capricho: a IA de imagem não guarda um boneco, ela reinventa o corpo a cada
desenho. Quando pedimos uma folha de 8 quadros, ela redesenha a anatomia 8 vezes, e o Blender depois cria 6 quadros do
meio entre cada par, espalhando o erro para os vizinhos.

A revisão da #51 ([`anatomia-51/LEIA-ME.md`](anatomia-51/LEIA-ME.md)) confirma: 2.680 desenhos olhados, **123 para
redesenhar** e mais 56 leves. Os quatro defeitos que mais se repetem são todos sintomas de "desenho do zero":

| Defeito (revisão #51) | Por que acontece com IA | Como um estúdio evita |
| --- | --- | --- |
| Membro que estica muito no contato | a IA exagera o "15% maior" do prompt sem régua | o braço é o mesmo desenho, só gira; o exagero é decidido à mão, num quadro só |
| Quadro de costas com outra altura e largura | a IA não tem a vista de costas do boneco | folha-modelo com frente, perfil e costas na mesma escala, aprovada antes |
| Corpo que muda de modelo (Garanhão magro, Pengaró emagrece) | cada folha é uma pessoa nova parecida | todo quadro é traçado em cima do modelo ou do quadro anterior |
| Sobras de outro desenho (pele clara, cabelo castanho) | a IA mistura memórias da conversa | paleta indexada fixa: cor errada nem existe no arquivo |

Dá para continuar consertando quadro a quadro, mas o erro volta em cada golpe novo. O conserto de verdade é tirar da IA
a tarefa de **manter o boneco igual**, que é exatamente o que ela faz mal.

## Como os jogos de luta profissionais fazem

Nenhum estúdio grande deixa cada quadro ser inventado sozinho. Todos têm uma âncora fixa (modelo 3D, folha-modelo ou o
próprio quadro anterior) e desenham por cima dela. Estudamos só as técnicas, sem copiar personagem nem arte de ninguém.

| Jogo | Âncora que mantém o boneco igual | Números públicos | O que serve para nós |
| --- | --- | --- | --- |
| [KOF XII/XIII](https://kotaku.com/snk-talk-kofxiis-gorgeous-gorgeous-graphics-5052085) (SNK) | desenho à mão, retocado quadro a quadro | 400 a 600 sprites por lutador; até 16 meses de um artista sozinho | boneco grande multiplica o trabalho de corrigir erro: cada pixel conta |
| [Street Fighter III 3rd Strike](https://www.guinnessworldrecords.com/world-records/98823-most-frames-of-animation-in-a-2d-fighter-videogame) (Capcom) | desenho tradicional digitalizado e traçado em pixel, depois muita limpeza ([relato da comunidade](https://www.neogaf.com/threads/street-fighter-iii-and-capcoms-pixel-art-process.1363079/)) | 23.039 quadros no jogo, recorde do Guinness | a qualidade veio de limpar, não de gerar mais quadros |
| [Skullgirls](https://80.lv/articles/tips-on-making-fluid-and-powerful-animations) (Lab Zero) | rascunho → limpeza → cor, sempre em cima do quadro anterior | ~1.200 a 1.500 quadros e ~2.000 horas por lutador ([tese](https://core.ac.uk/download/38089441.pdf)) | poucos quadros bem escolhidos, antecipação, "overshoot" e borrão (smear) |
| [Guilty Gear Xrd](https://www.ggxrd.com/Motomura_Junya_GuiltyGearXrd.pdf) (Arc System Works) | modelo 3D com ~500 ossos, pose feita à mão em cada quadro | sem interpolação: "todo quadro é quadro-chave" | animação lisa demais parece 3D; segurar poses parece 2D |
| Tese de animação de luta para MUGEN ([Rantala, 2013](https://core.ac.uk/download/38089441.pdf)) | render 3D como guia, traçado por cima, metade dos quadros escondida | soco forte com 13 desenhos; cada desenho segurado 3 ticks (20 por segundo num jogo de 60) | tirar quadros de preparação deixou o soco "mais forte" |

**As lições que valem para o Nazafights:**

1. **Pose-chave primeiro, e poucas.** Os profissionais escolhem 3 a 5 poses que contam o golpe (guarda, preparação,
   contato, recuperação) e capricham nelas. O resto é enchimento.
2. **Segurar é melhor que interpolar.** O Guilty Gear testou animação cheia e desistiu porque "não parecia 2D". Os nossos
   6 quadros do meio do Blender por intervalo fazem o contrário: deixam o golpe mole e espalham o defeito. Um desenho
   segurado 2 a 4 ticks, com congelamento no contato, lê melhor.
3. **Exagero é decisão, não acidente.** O Skullgirls e o Guilty Gear esticam membros e quebram a anatomia de propósito,
   num quadro só (o borrão ou o contato). O nosso problema é a IA esticar onde ninguém pediu.
4. **Silhueta clara.** Em luta rápida, o jogador lê a silhueta. Cada pose-chave tem que ser legível só pelo contorno.
5. **Folha-modelo antes de animar.** A tese conclui que o erro dela foi não fazer a folha-modelo (frente, perfil, costas,
   paleta, escala) depois de fechar o estilo. É o nosso caso dos quadros de costas.
6. **Paleta indexada fixa.** O MUGEN e os arcades trabalham com paleta indexada. Cor que não está na paleta não entra, e
   a troca de cor da forma despertada vira só troca de paleta.

## Ferramentas para editar pixel a pixel

O Claude já consegue editar pixel por pixel: um PNG é só uma grade de números, e com Python (Pillow + numpy, que o
projeto já usa) dá para ler, pintar, girar, recortar e conferir cada pixel. O que falta é o editor visual, com camadas e
casca de cebola (ver o quadro anterior transparente por baixo).

| Ferramenta | Preço e licença | Por código (para o Claude) | Para quem |
| --- | --- | --- | --- |
| [Aseprite](https://www.aseprite.org/docs/cli/) | cerca de US$ 20; o código é aberto para compilar só para uso próprio ([EULA](https://github.com/aseprite/aseprite)) | linha de comando em lote (`-b`), scripts Lua (`--script`), exporta folha, quadros, camadas, paleta e modo indexado | **recomendado** para o Alisson e para o pipeline |
| [pixel-mcp](http://github.com/willibrandon/pixel-mcp) | grátis (MIT), precisa do Aseprite 1.3+ | servidor MCP: o Claude desenha pixel, linha, preenche, mexe em camadas, quadros, paleta, contorno e exporta | ponte direta Claude ↔ Aseprite |
| LibreSprite | grátis (GPL), é o Aseprite antigo de código livre | scripts em JavaScript | alternativa grátis |
| [Pixelorama](https://www.github.com/Orama-Interactive/Pixelorama/discussions/579) | grátis (MIT), feito no Godot | exportação básica pela linha de comando (recente, conferir a versão) | editor grátis, menos automático |
| Python (Pillow, numpy, OpenCV) | grátis, já instalado no projeto | tudo: o Claude edita direto | já é o que os `ferramentas/*.py` usam |
| [PixelLab](https://www.pixellab.ai/docs/tools/skeleton-animation) | pago por créditos, tem API e MCP | animação por esqueleto, pintura parcial (inpainting) | só teste: a tela vai até 128x128, serve para o 1x, não para o 3x |

**Técnicas de consistência que esses editores dão e o ChatGPT não dá:**

- **Casca de cebola:** o quadro anterior aparece transparente por baixo; redesenha-se só o que muda.
- **Camadas por parte do corpo:** cabeça, tronco, braço, antebraço, perna em camadas separadas. Mexer o braço não muda a
  cabeça.
- **Rotação RotSprite:** gira uma peça de pixel art sem borrar (o Aseprite tem). É o que torna o boneco de peças possível.
- **Paleta indexada travada:** só as 15 cores da paleta existem; cor errada não tem como entrar.
- **Linha de chão e eixo fixos:** grade com a linha do pé e o centro do tronco, igual em todo quadro.

## Ecossistema MUGEN/IKEMEN: o que serve para nós

Ajuda mais na montagem e na conferência do que no desenho. A comunidade sempre desenhou à mão ou editou sprites de jogos
comerciais, e essa segunda parte não serve para nós.

| Recurso | O que é | Uso para o Nazafights |
| --- | --- | --- |
| [Fighter Factory Studio](https://chronocrash.com/forum/resources/fighter-factory-studio.124/) (3.7.4.4, Windows, Mac e Linux) | editor clássico de personagem: SFF, AIR, CNS, paleta, caixas Clsn, editor de imagem com camadas | conferir caixas de golpe e tempos visualmente; não substitui o gerador por código |
| [IKEMEN GO](https://github.com/ikemen-engine/Ikemen-GO) (MIT) e a [wiki](https://github.com/ikemen-engine/Ikemen-GO/wiki) | o motor que usamos | já usamos o 3x mostrado em 1/3; ler a wiki sobre paletas e PalFX antes da troca do Despertar por paleta |
| [Documentação da Elecbyte](https://www.elecbyte.com/mugendocs/sprmake2.html) | formatos SFF, AIR e o lutador de exemplo (Kung Fu Man) | referência de numeração de animações e tempo por quadro |
| Fóruns [Mugen Guild](https://mugenguild.com) e [ChronoCrash](https://chronocrash.com) | comunidades de criadores | dúvida de motor e ferramentas |
| Bases e "frankenspriting" | montar boneco com pedaços de sprites de jogos comerciais | **não usar**: é cópia de arte alheia ([guia](https://scrollboss.illmosis.net/tutorial_spritebases.php)) |
| Bases grátis do itch.io e OpenGameArt | manequins de pixel com licença livre | só estudo de proporção |

A lição mais útil do MUGEN: quem faz lutador bom ali trabalha com **paleta indexada e reaproveitamento de peças**. Um
mesmo braço aparece em vários golpes, só girado e retocado.

## O método novo: boneco de peças + retoque

A IA desenha o boneco **uma vez só**, bem feito, e todos os quadros saem desse mesmo desenho. Como os pixels do braço são
sempre os mesmos, o braço não tem como crescer, sumir ou virar outro. Continua no estilo arcade desenhado, nunca 3D
pixelizado, e o Blender continua só deformando sprite, como manda a regra.

1. **Folha-modelo aprovada:** frente, perfil e costas na mesma escala e na mesma linha de chão, mais a paleta de 15 cores.
2. **Kit de peças:** o desenho do parado vira camadas (cabeça, tronco, braço, antebraço, mão, coxa, canela, pé, garrafa,
   faixa), cada uma com o ponto de junta marcado. Mãos e cabeças extras são pedidas à IA como peça solta.
3. **Esqueleto por lutador:** comprimento de cada osso medido no parado. É a régua.
4. **Poses-chave por código:** um script monta cada pose girando e movendo as peças (RotSprite, sem borrar). A pose pode
   vir guiada por um rascunho da IA, mas o quadro final usa só as peças.
5. **Retoque pixel a pixel:** emendas das juntas, dobra da calça, músculo que muda com o ângulo e o exagero do contato.
6. **Poucos quadros, bem segurados:** 4 a 6 desenhos por golpe, cada um segurado 2 a 4 ticks, congelamento no contato e no
   máximo 1 ou 2 quadros do meio onde precisar. Borrão (smear) desenhado no golpe forte.
7. **Conferência automática:** régua de ossos e de silhueta (altura e largura contra o parado), além das 12 regras.

| Caminho | Quanto resolve a deformação | Custo | Quando usar |
| --- | --- | --- | --- |
| Boneco de peças + retoque (recomendado) | quase tudo: o corpo é o mesmo desenho | alto no primeiro lutador, baixo depois | golpes novos e as 51 folhas da #51 |
| IA editando o quadro anterior em vez de gerar folha nova | médio | baixo | conserto rápido de quadro isolado |
| IA com guia de pose (manequim anexado + referência) | médio: melhora a pose, não a identidade | baixo | rascunho de pose para o passo 4 |
| Treinar modelo próprio (LoRA) do lutador | médio a alto ([guia](https://aigaming.nuilab.org/workflows/character-consistency/)) | 15 a 40 imagens boas e placa de 24 GB | só se o jogo crescer muito |
| Continuar como hoje | baixo: o erro volta a cada golpe | alto e para sempre | não recomendado |

O que **não** muda: ficha, conceitos e aprovação do Breno na issue, estilo arcade e as 12 regras, o 3x e o gerador. Muda
só de onde vem cada quadro.

## Plano em fases

1. **Piloto: o soco do Pengaró**, feito pelo Claude do Alisson
   ([missão](missao-alisson-boneco-de-pecas.md)). Porta: o Breno assiste lado a lado e diz se ficou melhor. Se gostar, o
   método vira regra.
2. **Ferramentas:** Aseprite (ou LibreSprite), pixel-mcp ligado ao Claude, régua de ossos e silhueta no `conferir_arte.py`.
3. **Kit dos cinco lutadores**, nas duas formas (o despertado tem kit próprio, a roupa é outra).
4. **Refazer as 51 folhas da #51**, começando pelos golpes mais vistos e pelo Hazak e o Diabo Loiro.
5. **Revisar os quadros do meio:** desenhos segurados e congelamento no contato no lugar dos 6 do Blender por intervalo.
6. **Virar regra** na `receita-de-lutador.md` e na bíblia de arte (o Gbzin seria o primeiro já nascido assim).

## Fontes

- [GDC: animação de Guilty Gear Xrd, Junya Motomura (PDF)](https://www.ggxrd.com/Motomura_Junya_GuiltyGearXrd.pdf)
- [Dicas de animação fluida do Skullgirls, Mariel Cartwright (80.lv)](https://80.lv/articles/tips-on-making-fluid-and-powerful-animations)
- [SNK sobre os gráficos do KOF XII (Kotaku)](https://kotaku.com/snk-talk-kofxiis-gorgeous-gorgeous-graphics-5052085)
- [Recorde de quadros do SF III 3rd Strike (Guinness)](https://www.guinnessworldrecords.com/world-records/98823-most-frames-of-animation-in-a-2d-fighter-videogame)
- [Processo de pixel art da Capcom, relato da comunidade (NeoGAF)](https://www.neogaf.com/threads/street-fighter-iii-and-capcoms-pixel-art-process.1363079/)
- [Tese: animação 2D de luta para MUGEN, Rantala 2013 (PDF)](https://core.ac.uk/download/38089441.pdf)
- [Aseprite: linha de comando](https://www.aseprite.org/docs/cli/) e [licença](https://github.com/aseprite/aseprite)
- [pixel-mcp](http://github.com/willibrandon/pixel-mcp)
- [Pixelorama: linha de comando](https://www.github.com/Orama-Interactive/Pixelorama/discussions/579)
- [PixelLab: animação por esqueleto](https://www.pixellab.ai/docs/tools/skeleton-animation)
- [Sprite Sheet Diffusion (artigo)](https://arxiv.org/html/2412.03685v2)
- [Consistência de personagem com IA (NUILab)](https://aigaming.nuilab.org/workflows/character-consistency/)
- [Fighter Factory Studio](https://chronocrash.com/forum/resources/fighter-factory-studio.124/)
- [IKEMEN GO](https://github.com/ikemen-engine/Ikemen-GO)
- [Guia de bases de sprite e frankenspriting](https://scrollboss.illmosis.net/tutorial_spritebases.php)
