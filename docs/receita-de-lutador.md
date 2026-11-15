# Receita de lutador: tudo o que já foi aprendido, valendo para todo lutador novo

Regra do Breno (2026-11-15): **tudo o que foi feito na criação dos lutadores até aqui vira regra para sempre que for
criar outro**, e isso inclui as regras novas do endiabrado, da aura e do resto. Este arquivo junta essas regras em
ordem, do conceito até a `mugen`. Ele vale junto com [`regras-dos-lutadores.md`](regras-dos-lutadores.md), que tem o
kit mínimo e o checklist da seção 9, e com [`como-trabalhar.md`](como-trabalhar.md). Se os dois disserem coisas
diferentes, vale o mais novo do Breno.

Cada item diz de onde veio, para quem quiser ver o caso real.

## 1. Quem faz o quê

- O Breno e o Claude fazem a ficha, os conceitos e o pedido em `.md` ou na issue, e **mandam para o Alisson**. O
  Alisson coloca no jogo ([`como-trabalhar.md`](como-trabalhar.md), 2026-11-12).
- Cada lutador tem a sua issue. Pedidos, conceitos, vídeos e aprovações do Breno ficam nela.

## 2. Conceito antes de qualquer folha

- **Ficha primeiro**, no modelo da seção 10 das regras.
- **Lutador baseado em pessoa real:** o conceito sai **em cima das fotos** (anexadas em todo pedido no ChatGPT). Rosto,
  cabelo, barba, tom de pele e corpo iguais às fotos, só no estilo arcade. Conceito feito só pela ficha foi reprovado
  (Gbzin, #30).
- **Dois conceitos para o Breno aprovar na issue:** forma base e forma despertada. Nenhuma folha sai antes do ok nos
  dois (Gbzin, #30).
- **O despertado tem roupa própria por inteiro.** Nada da roupa da forma base aparece por baixo (regata, short, tênis).
  Mesmo rosto, corpo e altura, mas visual de chefão: o Breno reprovou o Grão-Pastor de manto por cima da regata e
  aprovou a armadura "Senhor do Rebanho" (#30).
- **O despertado tem que parecer poderoso demais.** Ideia fraca ou engraçadinha demais sai (o Deus Motoboy saiu, #30).
- **Conteúdo:** resenha pesada pode, mas nada de piada com o corpo ou a deficiência de ninguém. Personagem com
  deficiência entra com dignidade: a graça vem da situação e da dupla, nunca da deficiência (parceira do Raiclaven, #43).

## 3. Folhas nítidas desde o começo

- **Boneco grande na folha:** cerca de 500 px de altura ou mais (CK ~570, Pengaró novo ~500). Boneco pequeno (~250 a
  350 px) é ampliado pelo motor e borra. Foi a causa do Pengaró e do Hazak borrados (#32, #36).
- **Converter em 1x e 3x direto da folha grande**, como o `ferramentas/converter_pengaro.py` e o
  `ferramentas/converter_ck.py`, seguindo a [regra da alta resolução](regra-alta-resolucao.md). **Não usar o
  `hd_guiado.py` em lutador novo:** ele repinta com as cores do 1x e apaga olho e contorno do rosto.
- Reanexar a referência em toda folha (o tom de pele desvia em conversa longa).
- Estilo arcade anos 90 da [bíblia de arte](biblia-de-arte.md#estilo-arcade-anos-90), nunca 3D pixelizado.

## 4. Agarrões com animação própria

Regra do Breno (2026-11-15): **todo agarrão tem animação própria, e quem é agarrado também.**

- Os três agarrões (em pé, agachado e o de comando) têm **folhas próprias** de quem agarra: pegada, cada pancada e o
  arremesso. Não vale montar o agarrão com quadros emprestados de outros golpes.
- **Quem é agarrado tem reações próprias** para cada agarrão: preso, apanhando alto e baixo, sendo arremessado e caindo.
  Elas vão em folhas de reação de cada lutador, para que qualquer um possa agarrar qualquer outro.
- Estilo segura-e-bate clássico, com o jeito do lutador (`ferramentas/agarrao_mk.py`, #37). Cada pancada tem preparo,
  congelamento no contato, faísca pequena e tremida, e o final arremessa com direção clara (#45).
- Usar as ferramentas do jogo: folhas no ChatGPT, `animar_folha.py` para os quadros do meio e o gerador. Nada editado
  à mão em `chars/`.

## 5. O despertado

- **Dura até o fim da luta**, com a música da forma (`ferramentas/forma_permanente.py`, seção 4 das regras).
- **Cena da transformação:** tudo preto, zoom no lutador, clarão e luz voltando, na cor da forma
  ([`cena-transformacao.md`](cena-transformacao.md), #49).
- **Agarrão da forma e poder de longe** no padrão do Diabo Loiro do Hazak: grande, sombrio e pesado. Carga com o mundo
  parado, tremida forte ao soltar, fundo tingido na cor da forma e impacto que congela (#44, #47).
- Os golpes novos da seção 4 das regras, no tema da forma.

## 6. Aura

- **Aura grande e monstruosa**, de várias camadas do Blender, na cor que só ele usa (seção 4 das regras).
- **Segue o corpo em todo estado:** agachar, pulo, queda, apanhar, chão e agarrão (`ferramentas/aura_no_corpo.py`,
  #51). Asas e peças presas ao corpo giram e recolhem com ele.
- **Aura estilo anime, colada na silhueta** (Breno, 2026-11-15, #51). Ela tem o formato do corpo em todo quadro e:
  - no soco, corre pelo braço e sai pelo punho; no chute, desce pela perna e sai no pé;
  - tem física: arrasta para trás quando ele anda, passa do ponto quando ele para e assenta, e as labaredas sobem;
  - parece parte do corpo, nunca um adesivo nem um contorno contínuo;
  - não tinge o corpo e não tampa o HUD.
  A ferramenta é a `ferramentas/aura_silhueta.py` (branch `claude/project-thread-cgrwa2` até entrar na `mugen`).

## 7. Efeitos, parry e sons

- Efeitos só do **pixelfx e do Blender**, na cor do lutador e da forma, do tamanho do golpe
  ([`regra-efeitos-proporcionais.md`](regra-efeitos-proporcionais.md), #38). Sem a "rede de futebol".
- **Parry** em cima e embaixo, próprio do lutador ([`parry.md`](parry.md)).
- **Sons próprios** de ataque, ligados ao lutador ([`sons.md`](sons.md), #46).
- Golpes legíveis: caixa de golpe encostada no punho ou no pé, congelamento pela força do golpe (#45).

## 8. Antes de juntar na `mugen`

- O gerador chama `trocar_retratos.trocar("<id>")` **por último**, senão um pós-passo devolve retrato antigo (Hazak, #51).
- Robô: `python ferramentas/testar_pengaro.py --lutador <id>` sem falha.
- Vídeo de cada golpe mexido, conferido tick a tick ([`conferencia-de-golpe.md`](conferencia-de-golpe.md)).
- Foto do jogo ao lado do CK: rosto com o mesmo tamanho de pixel e olho visível.
- **Vídeo na issue para o Breno ver antes de juntar.**
- Checklist da seção 9 das regras marcado.
