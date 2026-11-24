# Regra de criação de personagem (definitiva)

Pedido do Breno em 2026-11-17: **uma regra só**, do conceito até o lutador entrar no jogo e ser revisado. Ela junta
tudo o que já foi decidido e testado. O Claude do Alisson, o Claude do Breno e qualquer outro que mexer em lutador
seguem este arquivo, passo a passo, na ordem.

**Como ler:** cada passo diz o que fazer, com o quê e o que precisa estar certo antes de passar para o próximo. O
detalhe técnico de cada assunto continua no documento dele (link no passo); aqui fica a decisão. Se um documento antigo
disser outra coisa, **vale este arquivo**, menos onde o Breno disser o contrário numa mensagem mais nova. Só o Breno
muda esta regra.

## Resumo em dez linhas

1. Ficha e conceitos (forma base e despertada) aprovados pelo Breno na issue do lutador antes de qualquer folha.
2. Folha-modelo grande (~500 px de boneco): perfil, frente e costas na mesma escala, com marca de lado na roupa.
3. **O boneco é desenhado uma vez só** e vira um kit de peças. Todo quadro sai dessas mesmas peças: é o método do
   **boneco de peças com corpo firme e vida**, regra para todos os lutadores desde 2026-11-17.
4. Ossos não mudam de tamanho, as cores são só as do kit (paleta travada), o rosto é sempre o do kit.
5. Cada golpe é posado pela anatomia: corpo inteiro, peso, base, camadas perto e longe, mão livre fora do golpe.
6. Tempo e caixas de golpe do jogo não mudam: mesma soma de ticks, mesmo tick de acerto, `Clsn1` no membro que bate.
7. Vida: quadros do meio feitos com as peças (menos entre antecipação e contato), respiração e atraso; nunca fluxo óptico.
8. Robô de defeitos com 0 defeito, sem linha de corte, e **régua do corpo todo** em 0 (`regua_corpo.py`: nenhum
   membro fino, curto ou inchado, golpe agachado não levanta); tudo em 3x mostrado em 1/3.
9. Liga no jogo com `ligar_pecas.py`, depois aura, luz e `encolher_sff.py`; robô de luta sem falha e dano igual.
10. Vídeo lado a lado e foto no jogo na issue, checklist marcado, sobe na `mugen`.

---

## 0. Quem faz o quê

- **Breno e Claude** desenham: ficha, conceitos, folhas no ChatGPT e o pedido em `.md` ou na issue. **Alisson** (e o
  Claude dele) põe no jogo ([`como-trabalhar.md`](como-trabalhar.md), 2026-11-12). O Claude só liga sprite no jogo
  quando o Breno ou o Alisson pedem.
- **Sem Codex e sem PR:** verifique e suba direto na `mugen`. Depois diga o que entrou e o que não foi testado.
- **Cada lutador tem a sua issue.** Pedido, conceito, vídeo e aprovação ficam nela. Um chat do ChatGPT por personagem,
  com o nome no título.
- O Breno liberou auto-aprovação para pôr no jogo o que passou nos dois robôs (2026-11-17). Conceito, lista de golpes do
  despertado e mudança desta regra continuam precisando do ok dele.

## 1. Ficha

- Preencha o modelo da seção 10 de [`regras-dos-lutadores.md`](regras-dos-lutadores.md) em `docs/fichas/<nome>.md`,
  com o kit mínimo da seção 3 (16 normais, 4 correntes, 4 kombos, 8 especiais, 2 projéteis, 1 ir para trás, 3
  agarrões, 2 supers, Despertar) e os golpes novos do despertado da seção 4.
- **Anote na ficha, para cada golpe, qual membro bate** (braço ou perna, da frente ou de trás).
- **Anote a marca de cada lado**: o que só existe no lado de trás (perto da câmera) e no da frente (longe). No Pengaró:
  caneleira verde e garrafa são de trás; calça branca e punho erguido são da frente. É o que impede "duas pernas
  direitas" depois.
- Cores da ficha (pele, roupa, objeto, cor dos efeitos de cada forma), com uma rampa de efeito diferente das que já
  existem ([`biblia-de-arte.md`](biblia-de-arte.md#lutador-novo)).
- Conteúdo: resenha pesada pode; não pode piada de escravidão, o estereótipo da mulher loira, nem piada com o corpo ou a
  deficiência de alguém. Lata, garrafa e camisa sem marca. Nada de personagem, arte, nome de golpe, som ou música de
  jogo existente.

## 2. Conceitos (porta: ok do Breno)

- **Lutador baseado em pessoa real:** o conceito sai em cima das fotos, anexadas em todo pedido. Rosto, cabelo, barba,
  tom de pele e corpo iguais às fotos, no estilo arcade (Gbzin, #30).
- **Dois conceitos na issue:** forma base e forma despertada. Nenhuma folha sai antes do ok nos dois.
- **Despertado:** mesmo rosto, corpo e altura, roupa própria por inteiro (nada da roupa base por baixo), visual de
  chefão e poderoso demais. Ideia fraca ou engraçadinha sai.
- Estilo arcade anos 90 da [bíblia](biblia-de-arte.md#estilo-arcade-anos-90). **Nunca modelo 3D nem 3D pixelizado.**

## 3. Folha-modelo

- Uma folha com **perfil virado para a direita (a guarda do parado), frente e costas**, os três na mesma escala, mesma
  altura e mesma linha de chão. Boneco com **~500 px de altura ou mais** na folha: boneco pequeno borra no jogo (#32,
  #36).
- Frente e costas podem vir do ChatGPT com o perfil anexado, mas **saem medidas**: altura da cabeça ao pé e largura de
  ombro e cintura iguais às do perfil, com 2% de tolerância. Quadro de costas mais baixo ou mais largo reprova.
- Objeto preso ao corpo (garrafa, cajado, tesoura) aparece em toda vista, sempre na mesma mão.
- Reanexe a referência em toda folha: em conversa longa o tom de pele desvia.
- Grave em `sprites/<lutador>/pecas/folha_modelo.png`.

## 4. Kit de peças

O jeito de fazer qualquer quadro do jogo a partir de um desenho só.

- **Recorte o parado em peças, na resolução grande:** cabeça, pescoço, tronco, quadril (com faixa ou cinto), braço e
  antebraço de cada lado, cada mão, coxa, canela e pé de cada lado, objeto, pontas de roupa que balançam.
- **Corpo firme:** tronco, pele e rosto vêm de um desenho só, **em cor cheia** (as cores do próprio desenho, sem
  reduzir para 15). Em cada quadro o tronco só anda: gira no máximo 10°, nunca muda de escala. Braços e pernas giram
  presos nas juntas.
- **Sobra na junta:** cada peça tem desenhado o pedaço que fica por baixo da vizinha, para não abrir buraco ao girar.
  Desenhe a sobra; não estique. O que os braços tapam no parado (peito, costas da camisa) é pintado com as cores, as
  dobras e o contorno da roupa, nunca uma chapa lisa.
- **Pé é peça separada**, sempre reto e encostado no chão.
- **Rosto sempre o mesmo**, em poucas expressões (guarda, foco, esforço), todas no tamanho do parado
  (`corrigir_cabeca.py`).
- **Variantes:** peça que muda de desenho e não só de ângulo (punho de frente no contato, braço esticado, perna em
  câmara ou esticada, mão aberta, pé girado de calcanhar, pé que chuta espelhado, cabeça gritando). Vem do desenho
  aprovado ou é pedida ao ChatGPT como peça solta em cima da folha-modelo, e é medida contra a peça original antes de
  entrar, pela **régua do corpo todo** do passo 8 (`python ferramentas/regua_corpo.py <lutador>`): a variante tem a
  grossura e a área da peça do parado do mesmo osso.
- **Paleta travada:** as cores do kit são as únicas que existem no boneco. Quadro que trouxer cor de fora (outro
  boneco, pele laranja, cabelo castanho) é trocado cor a cor para as do kit. A redução para 15 cores da v1 foi
  reprovada no piloto porque tirou a nitidez; a paleta indexada do `.sff` sai no fim, pelo `encolher_sff.py`.
- **Régua:** o `kit` guarda o comprimento de cada osso medido no parado (ombro-cotovelo, cotovelo-punho,
  quadril-joelho, joelho-tornozelo, altura da cabeça, largura do ombro) e a distância entre as raízes das coxas.
- **Arquivos:** `sprites/<lutador>/pecas/` (um PNG por peça + juntas, peça mãe e ordem de camadas). O código do kit fica
  em `ferramentas/kit_<lutador>.py` e roda pelo motor comum `ferramentas/firme.py` (os lutadores antigos têm o próprio:
  `piloto_firme.py`, `pecas_ck.py`, `boneco_gutto.py`, `gbzin_pecas.py`, `pecas_raiclaven.py`). O kit continua
  separado em peças para trocar a cabeça, a expressão ou uma peça e remontar todos os golpes de uma vez.
- **O despertado tem kit próprio**, porque a roupa é outra (`sprites/<lutador>/pecas_e/`).
- Gire com **RotSprite** (ou equivalente sem misturar cor), nunca rotação bilinear.

Porta: o kit remonta o parado sem diferença visível, e a régua passa.

## 5. Posar cada golpe

Poucas poses-chave, bem escolhidas, montadas com as peças. Ferramenta: o [montador](montador.md)
(`python ferramentas/montador.py --lutador <id>`), com casca de cebola, régua, caixa de golpe e **camada por pose**; ou as
poses à mão no `kit_<lutador>.py`. Um rascunho da IA ou a folha antiga pode servir de guia de pose, mas **o quadro final
usa só as peças do kit**.

A receita de cada golpe, pose por pose e com ticks, está no
[`estudo-anatomia-golpes.md`](estudo-anatomia-golpes.md) (guarda, jab, direto, gancho, uppercut, chutes frontal,
circular, alto, baixo, rasteira, giros de capoeira, cabeçada, cotovelada, joelhada, golpes no ar). O que é lei:

**As leis do corpo** (estudo, Parte 1):

1. A força sobe do chão: quadril e tronco se mexem antes; o membro que bate sai por último e chega por último.
2. O peso vai para onde o golpe aponta (direto: ~60% no pé da frente; gancho gira no lugar; uppercut sobe).
3. Base: a vertical do umbigo cai entre os pés; no chute, em cima do pé de apoio.
4. Joelhos sempre um pouco dobrados (perna de apoio quase reta só no chute alto).
5. A mão que não bate fica na guarda ou jogada para trás. **Nunca na frente do golpe.**
6. Alcance vem do ombro andando 10 a 20 px (no 3x) e do tronco girando, **nunca de esticar a peça**.
7. O braço chega quase reto, não travado. O exagero (10 a 15% mais longo) só num quadro de contato, decidido à mão.
8. Chute de perna dobrada tem câmara: joelho sobe primeiro, canela abre depois, e volta pela câmara.
9. No chute circular e no direto o pé de apoio gira (calcanhar para o oponente).
10. Antecipação curta, contato segurado, volta mais lenta.
11. A cabeça olha o alvo o golpe inteiro e assenta depois.
12. Silhueta e linha de ação: pintada de preto, a pose ainda diz qual golpe é e qual membro bate.

**Golpe natural, com o corpo inteiro** (Alisson, 2026-11-17): o soco gira o quadril, dá um passo à frente, o ombro vai
junto e o calcanhar de trás sobe; o chute tira o peso da perna de apoio e o tronco compensa; a cabeçada leva o tronco;
o pisão sobe o joelho e o corpo cai com o peso. Esticar só o braço com o resto parado reprova.

**Camadas perto e longe** (estudo, Parte 2): "frente" é o lado do oponente, mas na guarda aberta **o lado da frente é o
lado longe da câmera**.

1. Raiz manda: membro longe nasce **atrás** do tronco e da faixa; membro perto, **na frente**.
2. Cruzou a linha do peito, troca de camada naquela pose.
3. O membro que bate nunca fica escondido no contato; se não aparece, gire o tronco.
4. A mão livre fica atrás do golpe.
5. Perna que chuta e perna de apoio saem de quadris diferentes, e as marcas da roupa conferem com o lado.
6. Pé e mão são espelhados (dedão para dentro): o pé que chuta não é cópia do pé de apoio.

**Limites das juntas:** cotovelo dobra até ~145° e nunca para fora; joelho até ~140° e nunca para a frente; coxa
esticada passa de ~90° só com a bacia inclinada e o tronco para trás. Tabela completa no estudo.

**Giros e costas:** use a vista de costas da folha-modelo, nunca o perfil girado. Peça que o kit não tem (costas,
agachado de lado, braços abertos) entra no kit primeiro, medida pela régua, e só depois vira golpe.

Antes de gravar cada pose, passe a lista de 12 conferências da Parte 4 do estudo.

## 6. Tempo e caixas: o jogo não muda

- **Mesma soma de ticks, mesmo tick em que a caixa liga, mesma caixa.** O `Clsn1` fica encostado no punho ou no pé do
  desenho de contato. Se a pose nova alcança menos que a caixa, a pose muda, ou o Breno decide encolher a caixa; nunca
  fica caixa no ar.
- Tempos de golpe pela seção 8.3 das regras: fraco 3 a 5 ticks até encostar, forte 7 a 10, finalizador 10 a 14;
  congelamento no contato pela força; contato segura o ativo mais 1 a 2 ticks; cada pose de volta segura 4 a 9.
- Quem confere: o `tempos.json` de cada ação, o `ligar_pecas.py` (que parte os elementos na fronteira antiga sem mexer
  em caixa nem tick de acerto, e com `--ajustar` leva o impacto ao tick da `Clsn1`) e o robô de luta (dano idêntico).

## 7. Vida e fluidez

- **Quadros do meio com as peças**, nunca fluxo óptico nem os 6 do Blender: `vida_pecas.py` põe um quadro a cada 2
  ticks entre as poses-chave, com a ida acelerando, o impacto segurado e a volta desacelerando, sem mudar a soma de
  ticks nem o elemento de acerto.
- Respiração no parado (peito sobe 1 px do jogo), loop sem salto do último para o primeiro.
- Atraso: cabeça, cabelo, cordão, pontas da faixa e roupa chegam atrasados e balançam até parar.
- **Entre a antecipação e o contato não vai quadro do meio** (Breno, 2026-11-17): a troca é seca, para o golpe ter
  impacto. No máximo **um** quadro de borrão (smear), e só se o golpe ficar truncado. A fluidez que o Alisson pediu
  vem dos quadros do meio **na antecipação, na volta, na guarda e no parado e nas transições** (andar, agachar, virar).
  Golpe novo já sai assim. Os golpes que já estão no jogo ainda têm meio nesse trecho (o `vida_pecas.py` põe meio
  em todo intervalo); eles se corrigem quando o `vida_pecas.py` pular o intervalo que termina no elemento de acerto e
  cada lutador for religado.
- **Anatomia vem antes da fluidez:** quadro do meio que inventa membro, troca a roupa de perna ou derrete a cabeça sai.
- O andar acompanha a velocidade do jogo: passada do tamanho do deslocamento real, pé sem patinar.

## 8. Zero erro de animação (porta: robô de defeitos com 0)

Nenhum quadro entra com estes erros (seção 7.4 das regras):

1. Membro descolando ou fresta na junta.
2. Silhueta grossa: contorno dobrado, membro inchado, figura mais larga ou mais alta que o parado sem motivo.
3. Pedaço de sprite voando junto (migalha, resto de outro quadro).
4. **Linha de corte à vista:** o boneco é de peças, mas na tela é sempre um desenho inteiro. As juntas dobram como pele
   (`pele_pecas.py`, ligado com `PELE = True`): sem emenda, degrau de cor ou contorno de peça por dentro do corpo.
5. Movimento errado: osso que muda de tamanho, junta para o lado errado, pé que desliza ou afunda, peso que não muda de
   perna.

Quem confere: o robô de defeitos (`conferir()` do `piloto_firme.py`/`firme.py`) tem que dar **0 defeitos** em todos os
desenhos, inclusive os do meio. A régua reprova osso que mudou mais de 5% (até 15% só no membro que bate, no quadro de
contato marcado). O erro 5 se confere no vídeo lado a lado, tick a tick.

### Régua do corpo todo (Alisson, 2026-11-24; regra do Breno no mesmo dia)

O Breno viu no jogo pernas finas e compridas e agachado que estica a perna (issue #32, 22/11). O Alisson fez a régua
das pernas e o Breno mandou valer para o corpo inteiro. Ela entra junto com o robô de defeitos e também tem que dar
**0 reprovações**:

```
python ferramentas/regua_corpo.py            # todos: pernas (regua_pernas.py) + braço, cabeça e tronco
python ferramentas/regua_corpo.py gutto      # um lutador
```

1. **Agachado não levanta** (`regua_pernas.py`): golpe, defesa e apanhar do tipo agachado não podem subir o centro do
   corpo mais de 45% do caminho do agachado ao em pé, na base e no despertado. Especial que sobe de propósito (gancho
   que sai do chão) só vira aviso e se confere no vídeo. Se a perna não alcança a pose dobrada, use a variante de
   perna dobrada no kit; nunca estique a peça.
2. **Cada peça variante na proporção do parado**, comparada com a peça do parado do mesmo osso:
   - **Perna** (`regua_pernas.py`): esticada com grossura de 80% a 160% e área acima de 70%; dobrada com área de 60% a
     140%.
   - **Braço** (`regua_corpo.py`): grossura acima de 75% (braço fino, manga que some) e área acima de 60% (braço curto
     ou sumido). Sem teto, porque o braço da guarda é visto encurtado.
   - **Cabeça:** as expressões (dor, esforço, riso) com área e comprimento dentro de 15% da cabeça do parado. A cabeça
     não muda de tamanho.
   - **Tronco e quadril:** área dentro de 30% e grossura acima de 80%; a peça agachada é comparada com quadril e pernas.
3. Variante que reprova é **redesenhada na grossura do parado** (como a perna esticada nova do Gutto, que saiu do
   calção), não aceita. Só entra em `ACEITAS` no `regua_corpo.py` a peça conferida no olho em que a conta erra, com o
   motivo escrito (ex.: braço do Hazak de lado contra o bíceps contraído do parado).
4. Prova: antes e depois do lutador (tira e vídeo) na issue, régua em 0, robô de peças em 0 e robô de luta igual.

**Quadro especial:** onde o kit de frente não monta (deitado, de costas sem peça de costas, agachado muito fundo), o
quadro pode ser o desenho de hoje com o rosto do kit e a paleta travada. Ele também passa no robô. Quadro especial é
dívida: quando a peça que falta entrar no kit, ele vira quadro montado.

## 9. Alta resolução

- O corpo vai para o jogo **desenhado em 3x e mostrado em 1/3** ([`regra-alta-resolucao.md`](regra-alta-resolucao.md)).
  As peças saem da folha grande; o 3x (`quadros_pecas_hd/`, tela 1080x780, pés em 540,660) e o 1x (`quadros_pecas/`,
  360x260, pés em 180,220) saem direto do kit.
- Não use o `hd_guiado.py` em lutador novo: ele repinta com as cores do 1x e apaga olho e contorno.
- Proporção de KOF: boneco em escala 1, cerca de 110 de 180 de altura de tela ([`proporcoes.md`](proporcoes.md)).

## 10. Agarrões, despertado, aura, efeitos e sons

Tudo o que a [`receita-de-lutador.md`](receita-de-lutador.md) pede continua valendo, agora feito com as peças:

- **Agarrões** com animação própria de quem agarra e reações próprias de quem é agarrado (preso, apanhando alto e baixo,
  arremessado, caindo), em folhas de reação de cada lutador.
- **Despertado:** dura até o fim da luta, com cena de transformação; luta totalmente diferente do normal (todos os golpes
  novos, nada reaproveitado da base); lista de golpes aprovada pelo Breno antes de desenhar; kit próprio.
- **Aura** grande e monstruosa, colada na silhueta, saindo pelo membro que bate, com física, seguindo o corpo em todo
  estado (`aura_silhueta.py`); **luz** de aura e de todo efeito que brilha (`luz.py`).
- **Efeitos** do pixelfx e do Blender, do tamanho do golpe ([`regra-efeitos-proporcionais.md`](regra-efeitos-proporcionais.md));
  o endiabrado mantém os efeitos grandes. **Parry** próprio ([`parry.md`](parry.md)) e **sons** próprios ([`sons.md`](sons.md)).

## 11. Pôr no jogo

Na ordem, sem pular:

1. `python ferramentas/ligar_pecas.py <lutador>` com **todos** os golpes da pasta (o grupo é o número do golpe em ordem
   alfabética), a partir do `chars/<lutador>` de antes de qualquer ligação. Ele liga os quadros no `.sff` (grupos
   48000+), reescreve o `.air` com as mesmas caixas e o mesmo tick de acerto, troca `AnimElem` no `.cns`, põe o remap do
   despertado e refaz as ações da aura. Despertado com kit próprio: `--de <kit> --grupo 49000 --ajustar`.
2. `python ferramentas/aura_silhueta.py <lutador>` (a luz roda no fim dele).
3. O gerador chama `trocar_retratos.trocar("<id>")` por último.
4. `python ferramentas/encolher_sff.py <lutador> [--indexar 49000-49099]` **por último de tudo**: tira desenho que nada
   usa, indexa o corpo firme numa paleta própria e confere que todo desenho saiu igual.
5. Nada editado à mão em `chars/<lutador>/`.

## 12. Revisão (porta: Breno vê antes de dar por pronto)

- **Robô de defeitos:** 0 defeitos (passo 8).
- **Robô de luta:** `python ferramentas/testar_pengaro.py --lutador <id>` sem falha, com o **dano idêntico** ao de antes
  da ligação.
- **Vídeo lado a lado** (atual à esquerda, novo à direita, 60 fps) e tira com todos os ticks de cada golpe mexido
  (`video_golpe.py`), olhados tick a tick ([`conferencia-de-golpe.md`](conferencia-de-golpe.md)).
- **Folha de contato antes e depois**, mesma escala, e olhar em zoom 3x: nada de borrão, cor nova, contorno quebrado na
  junta, rosto ou pele diferente entre quadros.
- **Foto no jogo** ao lado do CK: mesmo tamanho de pixel no rosto, olho visível.
- Vídeo e foto **na issue do lutador**, com o que entrou, o que foi visto rodando e o que ninguém testou ainda.
- `LOGBOOK.md`: o que foi feito, o que não foi testado e quanto tempo levou.
- Checklist da seção 9 de [`regras-dos-lutadores.md`](regras-dos-lutadores.md) marcado, mais estas três linhas:

```
[ ] kit de peças do parado (e kit próprio do despertado); ossos medidos; régua passa em todo quadro
[ ] todo golpe posado pelas 12 leis e pela regra de camadas perto/longe; mão livre fora do golpe
[ ] mesma soma de ticks, mesmo tick de acerto e caixa no membro; robô de defeitos 0; robô de luta com dano igual
```

Commit e `git push origin mugen`. O atalho do Breno baixa no clique seguinte.

## Lutador que já existe

Mesma regra, na mesma ordem, a partir do passo 3: kit do parado aprovado, depois os golpes que o jogador mais vê e os
golpes confusos (os que a revisão apontou), um por vez. O que já passa na lista de conferência do estudo fica como está.
O guia de quem muda o quê em cada lutador é o [`aplicar-estudo-anatomia.md`](aplicar-estudo-anatomia.md).

## De onde veio cada decisão

| Decisão | Origem |
| --- | --- |
| Boneco de peças em vez de desenho do zero | [`estudo-animacao.md`](estudo-animacao.md), Breno, 2026-11-15 |
| Piloto e critérios (ossos, paleta travada, tempo e caixas iguais) | [`missao-alisson-boneco-de-pecas.md`](missao-alisson-boneco-de-pecas.md), issue #32 |
| Corpo firme (v3) no lugar das peças com 15 cores (v1) e do conserto só da cabeça (v2) | Alisson, 2026-11-16, issue #32 |
| Vida, robô de defeitos, método para todos | Alisson, 2026-11-16, issue #32 |
| Boneco de peças é a regra | Breno, 2026-11-17, issue #32 |
| Zero erro de animação, golpe natural, sem linha de corte | Alisson, 2026-11-17, seção 7.4 das regras |
| Leis do corpo, camadas perto e longe, limites de junta, receitas | [`estudo-anatomia-golpes.md`](estudo-anatomia-golpes.md), Breno, 2026-11-17 |
| Sem quadro do meio entre antecipação e contato (no máximo 1 borrão) | Breno, 2026-11-17, nesta regra |
| Montador, pintar e apagar na peça, camada por pose | [`montador.md`](montador.md), Breno, 2026-11-17 |
| Régua das pernas (agachado não levanta, perna do kit na grossura do parado) | Alisson, 2026-11-24, issue #32 ([`pernas-e-agachado.md`](pernas-e-agachado.md)) |
| Régua do corpo todo (braço, cabeça e tronco na mesma conta) | Breno, 2026-11-24, nesta regra |
| Conceito, despertado, aura, luz, agarrões | [`receita-de-lutador.md`](receita-de-lutador.md), Breno, 2026-11-15 |
