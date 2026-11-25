# Comparativos antes x depois (Hazak e Diabo Loiro, #32 de 24/11)

O "antes" é o commit e21ea13b (antes dos pedidos de 24/11). Cada `tira_*.png` mostra ANTES em cima, DEPOIS no meio e
embaixo os dois sobrepostos: **azul = só no antes, vermelho = só no depois, cinza = igual**.

Medida honesta (pixel a pixel, depois de descontar o boneco ter só andado de lugar):

| ação | mudou de verdade? |
|---|---|
| Hazak agarrão karatê (tira_810, tira_800) | **Sim, golpe novo inteiro** (pega na gola + rajada + soco final) |
| Hazak jab (tira_200) | **Sim, mas curto**: borrão em 1 quadro e risquinhos de vento em 3; o resto é igual |
| Hazak ginga (tira_0) | **Pouco**: só as pernas, que ficaram como no desenho original (joelho dobra menos); tronco e braços iguais |
| Diabo Loiro, golpes (tira_4201, tira_4203) | **Quase nada**: a pose é idêntica (0% depois de alinhar), só recua/avança 1 a 5 px e tem 1 quadro de rastro |
| Diabo Loiro, ginga (tira_0d) | **Pouco**: mesmas 7 poses em outra ordem + respiração de 1 px |

Conclusão: o pedido "dar vida ao Diabo Loiro" NÃO foi atendido de verdade; precisa de poses novas.

Os `dif_*.png` são o painel antigo (vermelho = qualquer pixel diferente). Eles enganam: o boneco andar 1 px já pinta
tudo de vermelho. Use as tiras.

Ferramentas: `ferramentas/antes_depois/tira.py SAIDA` (tiras) e `ferramentas/antes_depois/diferenca.py` (contagem pixel a pixel).
