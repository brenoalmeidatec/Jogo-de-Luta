# Pausa 17/11: Raiclaven + A Cliente (despertado) no corpo firme

Branch `claude/project-thread-f6tbq9` (já com a mugen acbdee05 juntada). **Não está na mugen**: o lote 3 ficou pronto no
kit, mas parou antes de ligar no jogo e rodar o robô de luta.

## O que está feito
- Na mugen (a9e3dab4/acbdee05): parado, agachado, 4 golpes agachados, defesa, apanha, 4 golpes de pé (lotes 1 e 2).
- No branch (lote 3, robô de peças 0 defeito em cada leva): andar, pulo, 4 golpes no ar, queda/levanta/apanha no ar
  (3 desenhos inteiros do ChatGPT em `quadros_arcade_hd/queda_d`, via `ferramentas/doador_cliente.py`), 4 direcionais,
  4 correntes, kombo, 4 especiais e o super. Detalhes em `docs/raiclaven-despertado-43.md`, Fase 6.
- ChatGPT: chat apagado e arquivos tirados da Biblioteca; imagens contadas em `imagens/fila-chatgpt.md`.

## Onde parou
A regeneração completa (`firme.py cliente`) foi interrompida no meio pela pausa: algumas pastas de
`sprites/raiclaven_cliente/quadros_pecas_hd` podem estar pela metade. Por isso o primeiro passo é gerar tudo de novo.

## Próximos passos exatos
1. `git fetch origin mugen && git merge FETCH_HEAD` (juntar a mugen antes).
2. `python3 ferramentas/doador_cliente.py` (refaz as pastas cópia e os doadores; as pastas de fora do git somem).
3. `python3 ferramentas/firme.py cliente` (todas as animações, ~30 min) e conferir "0 de N desenho(s) com defeito".
4. `python3 ferramentas/raiclaven_no_jogo.py` (~15 min, termina com encolher_sff; conferir `.sff` < 100 MB).
5. `python3 ferramentas/testar_pengaro.py --linux --lutador raiclaven` (robô de luta, tudo PASS).
6. Vídeo dos golpes novos, commit, `git push origin HEAD:mugen`, comentário na issue #43.

## Pendências conhecidas
- Pescoço de Borracha sem esticão: esticar a peça da criatura borrava o corpo dela. Pede um doador do ChatGPT com o
  pescoço esticado (a cabeça fica igual), ligado como desenho inteiro (como a queda).
- Leve risco verde/vermelho nas costas da criatura quando ela se inclina muito (pescoco, peruca): conferir no vídeo.
- Correntes começam da guarda (sem herdar a pose do golpe anterior): conferir se o encaixe no jogo fica natural.
