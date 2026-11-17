# Pausa 17/11/2026: Gbzin no boneco de peças

## Estado (tudo na `mugen`, última b58d6dd7; branch claude/project-thread-y90n0e igual)

- **Corpo firme:** os 36 golpes têm cabeça do kit e paleta travada (`gbzin_pecas.py firmes`).
- **Folhas novas do ChatGPT:** bicicleta, cotovelada e Passinho de Pinguim entraram por `TROCA_QUADRO`/`SO_DESENHO`.
- **Pele nas juntas:** os quadros do kit usam `pele_pecas.py`, com a ordem de camadas do próprio Gbzin (`PELE_CAMADAS`).
- **Estudo de anatomia:** conferido nos 36 golpes, ver `docs/boneco-pecas/gbzin/anatomia.md`. A pasta `cabecada` é o
  antiaéreo da bengala (receita do uppercut) e fica como está.
- **Quadros do meio no meio-termo:** parado, soco e chute alto foram ligados no jogo com `ligar_pecas`. O
  `gerar_gbzin.py` roda sozinho no fim, nesta ordem: `ligar_pecas`, o kit do Grão-Pastor, `aura_silhueta` e `encolher_sff`.
- **Folhas de vítima da base:** ligadas só no Gbzin, como reação própria de quem é agarrado (ações 5940 a 5944).
- **Robôs:** robô de defeitos 0 e robô de luta 236/236.

## Próximos passos

1. Ver no jogo o Gbzin sendo agarrado. O robô usa sempre o Hazak como oponente, então isso ainda não foi visto.
2. Variante "pé girado" no kit, para quando entrar um chute circular.
3. Especiais com 20 a 40 desenhos, quando sair o pedido.
4. Expressões do rosto casadas com as falas, quando o Alisson gravar.
5. Ao regerar o Gbzin, rodar sempre o `gerar_gbzin.py` inteiro (não só uma parte) e depois
   `testar_pengaro.py --linux --lutador gbzin`.
