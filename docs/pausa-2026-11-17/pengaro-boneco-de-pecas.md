# Pausa 17/11: Pengaró base no boneco de peças

## O que já está na `mugen` (robôs zerados)
- 154 ações base do Pengaró pelo boneco de peças, na `mugen` 34ac7869. Robô do boneco: 0 defeito. Robô de luta: 189/189,
  igual ao de antes.
- Pele sem linha de corte (`ferramentas/pele_pecas.py`). Soco com quadril e passo, chute alto com o corpo inteiro.
- Estudo de anatomia aplicado: camada por pose (`_camada`), calcanhar de trás levantado (`_ponta_tras`), câmara no chute
  alto e quadros do meio no meio-termo (antecipação segurada).
- Tornozelo estica em vez de o pé descer; .sff de 78,9 para 40,7 MB.

## Onde parou: peça nova "pé de trás girado"
Pedido: no soco direto o pé de trás gira (calcanhar para fora, apoiado na ponta). Hoje o kit só tem esse pé de frente.
- Feito: 1 imagem gerada no ChatGPT (Browser 2, chat "Gerar pé pixel art"), salva em
  `docs/boneco-pecas/pe_girado/chatgpt_pe_girado.png`. É um pé direito de lado, com o calcanhar alto e os dedos para a
  direita, e serve. A referência enviada está em `referencia_pes.png`. **Imagens geradas: 1. O chat ainda NÃO foi
  apagado**: apagar quando voltar.
- Falta, nesta ordem:
  1. Recortar o fundo branco (flood fill pela borda), cortar o topo reto na altura do tornozelo (~20% de cima), reduzir
     até ~45 px do corte ao chão (~61 px de largura, no HD 3x) e pintar com a paleta do pé de trás atual
     (`kit["pes"]["canela_tras"]`).
  2. Gravar como `kit["pes"]["canela_tras_girado"]` (mesmo formato: img, origem, tornozelo no meio do corte, fundo).
  3. Em `piloto_firme.desenhar`: com `_ponta_tras.dy >= 5`, desenhar o pé girado no lugar do de frente.
  4. `python3 ferramentas/pengaro_todo.py animar` só nas ações de soco (200 201 301 340 3433), olhar e rodar o robô.
  5. Religar: pegar os chars da mugen, rodar `ligar_pecas.py pengaro --grupo 48000 a0 a10 ...` (alternar com o 49000 que
     está lá hoje), depois `aura_no_corpo.py pengaro`, `encolher_sff.py pengaro` e `testar_pengaro.py --linux`
     (tem que dar 189/189). Por fim, juntar na mugen e comentar na #32.
