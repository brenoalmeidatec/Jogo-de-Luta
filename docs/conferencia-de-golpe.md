# Conferência de golpe

Roteiro fixo para fechar qualquer golpe ou lutador antes de subir na `mugen`. Cada linha diz como conferir.

## Arte

- [ ] As folhas têm o personagem certo e a cor certa (folha de contato; matiz da pele igual ao da referência).
- [ ] Nenhuma figura cortada, colada na vizinha ou com faixa no fundo (`animar_folha.py` corta sem erro).
- [ ] Forma transformada tem a folha equivalente, nos mesmos 8 tempos.

## Quadros

- [ ] `python ferramentas/auditar_pengaro.py PASTA` sem: pés fora do chão, corpo pulando de lugar, figura cortada,
      pedaço solto, magenta, endiabrado desalinhado. Olhe as folhas `acao_N.png` das ações citadas.
- [ ] `python ferramentas/conferir_tempo.py . PASTA`: tempo de cada golpe só muda se foi de propósito.
- [ ] `python ferramentas/conferir_despertar.py . PASTA`: cada quadro normal tem o par transformado.
- [ ] **Vídeo curto e análise quadro a quadro (obrigatório em todo controle de qualidade).**
      `python ferramentas/video_golpe.py PASTA <ações mexidas>` (ou `--suspeitas` para o lutador inteiro) grava, para
      cada ação, um vídeo de 5 a 10 s a 60 fps montado tick a tick do SFF/AIR finais (`acao_N.mp4`), a tira com
      **todos** os ticks numerados (`acao_N.png`, borda vermelha no tick acusado) e o `relatorio.md`. Assista ao vídeo
      e olhe a tira inteira, tick a tick, de toda ação que você mexeu: o que a análise acusa (desenho parado mais de
      2 ticks, pose que estala, pé que sobe ou afunda, corpo que desliza, figura que muda de tamanho, emenda de loop) e
      o que o olho pega e a régua não pega (antecipação, smear, continuação, easing; regra 7.2). Não suba ação com
      tick acusado sem dizer, na entrega, por que ele ficou. Para o movimento pela tela, faça também uma filmagem curta
      no jogo: `python ferramentas/filmar_luta.py PASTA --segundos 10`.

## Jogo

- [ ] `python ferramentas/verificar_pengaro.py` e `--hazaki` passam.
- [ ] `python ferramentas/testar_pengaro.py`: o robô entra em cada golpe, acerta e volta ao controle (126+ verificações).
- [ ] `python ferramentas/filmar_luta.py PASTA --despertar 12`: olhe a folha `contato.png` e os quadros suspeitos em
      tamanho real. Procure efeito fora do golpe, mancha, rastro escuro, troca de forma pulando de lugar.

## Efeitos

- [ ] O efeito nasce no quadro em que a caixa de golpe liga, na ponta do membro que bate.
- [ ] Cada forma usa a sua cor; nada da cor do endiabrado aparece no normal.
- [ ] Brilho com mistura de soma, sombra com subtração; nenhuma bolha sólida.

## Entrega

- [ ] Commit e `git push origin mugen`.
- [ ] Na mensagem para o Breno: o que entrou, o que foi visto rodando e o que ainda não foi testado por uma pessoa.
