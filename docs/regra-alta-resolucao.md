# Regra da alta resolução (HD): lutador nítido no jogo

**Regra do Breno, 2026-11-12:** todo lutador vai para o jogo em **alta resolução**: o corpo desenhado no triplo do
tamanho (3x) e o lutador mostrado em 1/3. O jogo não pode esticar o desenho. Vale para os cinco lutadores de hoje
(Pengaró, Hazak, CK, Gutto e Raiclaven) e para todo lutador novo. Lutador que vai para a `mugen` em 1x, borrado,
não passa no checklist (seção 9 de [`regras-dos-lutadores.md`](regras-dos-lutadores.md)).

## Por quê

O jogo roda em 1280x720 e os lutadores usam `localcoord = 320,240`: o motor estica cada lutador 3 vezes. Antes desta
regra, o quadro de jogo tinha o boneco com ~110 px de altura (tela de 360x260), e cada pixel virava um bloco 3x3 na
tela. A folha do ChatGPT tem o boneco com ~600 px, mas o detalhe se perdia nesse encolhe e estica: rosto, olhos e
músculos viravam borrão.

Com o sprite 3x maior (boneco de ~330 px, tela de 1080x780) e `[Size] xscale = yscale = 1/3`, o motor desenha cada
pixel do desenho num pixel da tela. O boneco fica do mesmo tamanho na tela, mas nítido.

## O que não muda

- **Tamanho na tela, velocidade, alcance, caixas de golpe e fluidez.** O gerador continua montando, medindo e
  conferindo tudo no quadro de 1x (360x260, pés em 180,220). A troca para 3x é o último passo.
- **Efeitos** (faíscas, fumaça, aura), **projéteis** e **retratos** ficam em 1x. O motor não aplica neles a escala do
  lutador: o Explod só usa a escala com `syncid` e o projétil só com `size.proj.doscale`, conferido no código do IKEMEN
  v1.0.0.
- Prova: o robô (`testar_pengaro.py --lutador <nome> --local`) deu **o mesmo dano e os mesmos estados** antes e depois
  nos cinco lutadores.

## Como funciona

1. **`ferramentas/hd.py`**, chamado no fim do `gerar_<lutador>.py`:
   - troca cada sprite do corpo pelo gêmeo 3x do mesmo quadro. O gêmeo é achado comparando pixels com o quadro de 1x;
     a comparação aceita retoque pequeno, borda limpa pelo gerador e quadro espelhado;
   - conta como corpo também o destino de todo `[RemapPreset ...]` do `.cns` (a forma despertada do kit troca o
     sprite do corpo pelo `RemapSprite`, fora do `.air`). Até 2026-11-12 isso faltava: o despertado do CK, do Pengaró,
     do Gutto e do Raiclaven saía em 1x e o motor desenhava em 1/3 do tamanho (visto no filme da integração);
   - multiplica por 3 toda caixa Clsn do `.air`;
   - põe `[Size]` em 1/3 no `.cns`;
   - deixa em 1x o sprite que só aparece em Explod, projétil ou faísca própria (`S`), e o retrato (grupo 9000);
   - quando um sprite serve ao corpo e a um efeito, copia ele para o grupo + 20000;
   - imprime quantos sprites trocou, quantos só ampliou (sem gêmeo, ficam iguais a antes) e quantos são efeito.
2. **De onde vêm os gêmeos 3x:**

   | Arte do lutador | Comando | Pasta | No git? |
   |---|---|---|---|
   | Arcade (folhas → `quadros_arcade/`): Pengaró, Hazak | `python ferramentas/hd_guiado.py <lutador> [folha ...]` | `quadros_arcade_hd/` | sim (~10 MB) |
   | Arcade do CK | `HD=3 python ferramentas/converter_ck.py [folha ...]` (ou o `hd_guiado.py`) | `quadros_arcade_hd/` | sim |
   | Antiga, com quadros do meio do Blender: Gutto, Raiclaven | `python ferramentas/hd_blender.py <lutador>` (~20 min) | `quadros_hd/` | **não** (~550 MB, `.gitignore`) |

   - O `hd_guiado.py` acha na folha original a figura que deu cada quadro de 1x, cola ela em 3x e pinta cada pixel só
     com as cores do quadro de 1x em volta. Assim o 3x herda a paleta e todos os retoques.
   - O `hd_blender.py` é o `animar_folha.py` com `HD=3`: a mesma renderização 4x do Blender, reduzida para 3x em vez de
     1x. Os quadros do meio também saem em 3x, então nada pisca no meio do golpe.

## O que fazer, sempre

- **Folha nova ou refeita:** depois do conversor de sempre, gere o gêmeo 3x dela pela tabela acima e rode o gerador do
  lutador de novo. Sem isso, o gerador usa o gêmeo velho ou só amplia.
- **Lutador novo:** no fim do `gerar_<nome>.py`, chame o `hd.aplicar(s, air, cns, [(pasta 1x, pasta 3x)],
  gp.SPRITES_VITIMA)` antes de gravar `.air`, `.cns` e `.sff`, como nos cinco geradores de hoje. Chame **depois** de
  o `.cns` estar completo (aura do `aura.py` incluída): o `hd.py` só sabe que uma ação é efeito pelo Explod que a usa;
  se a aura entrar no `.cns` depois, os sprites dela contam como corpo e saem ampliados 3x (gigantes na tela).
- **Gutto e Raiclaven numa máquina nova:** rode `python ferramentas/hd_blender.py gutto` (e `raiclaven`) antes de mexer
  no gerador. Sem `quadros_hd/`, o gerador avisa com "ATENÇÃO" e o lutador sai em 1x.
- **Antes de subir:**
  - olhe a linha `HD:` que o gerador imprime: "só ampliados" alto quer dizer gêmeo faltando;
  - tire uma foto do jogo rodando e confira se o boneco está nítido;
  - rode o robô.
- Desenho montado por código (rotação, mistura, poses coladas) não tem gêmeo e fica só ampliado. Se aparecer muito na
  luta, troque por uma folha desenhada.

## Custo

- O `.sff` fica maior: hoje o CK tem 3,9 MB, o Hazak 4,2 MB, o Pengaró 5,6 MB, o Gutto 21 MB e o Raiclaven 22 MB. O
  launcher baixa uma vez só.
- O gerador demora um pouco mais. O Gutto, o maior, leva ~1,5 min.
