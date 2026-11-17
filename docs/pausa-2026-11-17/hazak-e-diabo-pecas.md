# Pausa 17/11 — Hazak e Diabo demônio no boneco de peças (branch `claude/project-thread-46qshe`)

## O que ficou pronto
- **Diabo demônio, arte:** folha-modelo + 3 folhas de poses do ChatGPT (só guia), levadas à escala e paleta do parado
  por `ferramentas/diabo_modelo.py` (`sprites/diabo_demonio/quadros_arcade_hd/modelo/00-25`). Chat do ChatGPT apagado
  (4 imagens; arquivos ainda na Biblioteca).
- **32 folhas m_** (26 antigas + 6 novas: ar_maos, ar_pes, direcionais_a/b, fins_maos, fins_pes) exportadas por
  `ferramentas/diabo_exportar.py` em `sprites/hazaki/diabo_terno/m_*`: **robô de defeitos 0/256**
  (`docs/boneco-pecas/diabo_demonio/robo_folhas_m.md`). Mapa de cada quadro em `kit_diabo.py` (TROCA, `_NOVAS`).
  Quadro `modelo/NN` = quadro especial (dívida: vira montado quando a peça entrar no kit).
- **Hazak** regerado pelo firme com PELE e golpe seco (robô de peças 0/188), mugen 50f21cdb juntada, pipeline completo
  rodado (firme → gerar_hazaki → ligar_pecas → aura_silhueta → encolher_sff, .sff 30,2 MB).

## Onde parou (NÃO está na mugen)
Robô de luta do Hazak (`python3 ferramentas/testar_pengaro.py --linux --lutador hazaki`): **401 passaram, 2 falharam**:
- 75 "Garra no Ar (ar+x)": não acerta.
- 79 "corrente x Fúria das Garras": o finalizador (fins_maos 0-3) não acerta.

Causa provável: o motor ancora o quadro m_ pela **última linha da imagem** (`diabo_terno.ancora_demonio`, y = h-1).
Nas poses do modelo no ar o **rabo pende abaixo dos pés**, então o corpo sobe e a garra passa por cima do P2.
Na Fúria, `modelo/14` (garra que sobe) tem pouco alcance para a frente (o deslocamento dx some, a âncora x é a
mediana do tronco).

## Próximos passos exatos
1. Âncora pelos pés: o exportador grava `m_<folha>/base.json` com a linha mais baixa de pele (pé) por quadro, e
   `ancora_demonio(m, base)` usa essa linha quando existe (usos em diabo_demonio.py:620, diabo_loiro.py:277,
   diabo_terno.py:272). Combinar com a thread do motor (#47, ela é dona do motor).
2. Fúria (fins_maos/01-02): trocar `M(14)` por pose do kit com `braco_frente` esticado subindo (ang -35 e -70) e passo.
3. Reexportar só essas folhas, rodar o pipeline do Hazak de novo e o robô de luta até 0 falhas (referência: 327/0 da
   outra thread, 401 verificações agora com as folhas novas).
4. Vídeo antes/depois (`filmar_golpes_linux.py`), juntar na mugen, comentário nas issues #36/#44/#47, LOGBOOK.
5. Tirar da Biblioteca do ChatGPT (Browser 2) as 4 imagens do chat 6afc8614.
