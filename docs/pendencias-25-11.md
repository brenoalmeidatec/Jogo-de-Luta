# Pendências sem imagem (thread de 25/11/2026)

Pedido do Alisson (25/11): levantar tudo que falta e fazer o que não depende de gerar imagem no ChatGPT/Gemini
(geração de imagem em espera até o upgrade do ChatGPT). Testes só na nuvem, robô zero defeito, comparativo com zoom
e marcação vermelha, e todo aviso ao Breno na issue com prévia visual embutida no comentário.

## De onde saiu a lista

- **Auditoria de mecânica do Breno** (#32, 24/11 19:56): 11 itens, sem conteúdo novo.
- **Recado do Breno de 25/11** (#32, 14:04): Gabriel (sprite), rework do Raiclaven, explosão vermelha do Gutto.
- `docs/meta-1.0-sem-imagem.md` (o que a thread da meta 1.0 deixou), `docs/pernas-e-agachado.md` (sobras do Pengaró).
- Fica de fora: jab e agarrão do Hazak (outra conversa, aguardando o Alisson).

## Lista e andamento

| # | Item | Precisa de imagem? | Estado |
|---|---|---|---|
| A1 | "Afastar na defesa" (y+b) saindo de graça sem barra (5 lutadores) e gastando a barra à toa no Hazak | não | feito |
| A4 | Corrente "jab, jab" que nunca sai (código morto) | não | feito |
| A7 | Defender dá a mesma vantagem que apanhar (`guard.hittime`) | não | feito |
| A8 | Combo sem desconto de dano | não | feito |
| A10 | Parry difícil demais (janela 4 tiques, buffer 1) | não | feito |
| A11 | Agarrão normal (800) sem escape | não | já existia (nada a fazer) |
| A2 | Soco forte (y) do Pengaró mostrando um chute alto | talvez (usar desenho que já existe) | precisa de desenho novo (fila de imagens) |
| A3 | Chute forte de longe do Pengaró (240): calça manchada e perna congelada; pé virado no 245 | talvez | feito (calça: melhorou, não zerou) |
| A6 | Régua que mede o quadro final do `.sff`, não só as peças | não | a fazer |
| A9 | Cinco lutadores com a mesma tabela de normais | não (números) | a fazer |
| B3 | Gutto: explosão vermelha em todo ataque → só no impacto/especial | não | feito |
| B2 | Raiclaven: rework para ler melhor + imperfeições | parte sim | a fazer (parte sem imagem) |
| B1 | Gabriel (Gbzin): o que falta e sprite novo | **sim** | espera o upgrade |
| C1 | Regras novas em `como-trabalhar.md` (prévia no email, testes só na nuvem, subagentes) | não | feito |

## Feito

Tudo medido e testado na nuvem (robô dos 6 lutadores sem falha nova). Ferramentas novas ficam na `mugen` e rodam
sozinhas no fim dos `gerar_<lutador>.py`, então uma regeração não desfaz nada.

- **A1, A4, A8, A10 (`ferramentas/mecanica.py`):** afastar de defesa só sai com 1 barra e gasta 1 barra ao sair (o
  Hazak gastava e falhava com 1000 a 1999); a corrente "jab, jab" morta saiu (menos no Hazak, onde o Diabo usa);
  parry com janela de 8 tiques e comando com 4 tiques de folga; dano de combo cai a partir do 3º acerto (80%, 70%,
  60% e daí em diante 50%), super fica fora do desconto.
- **A7 (`ferramentas/vantagem.py` + `ferramentas/calibrar_guarda.py`):** o robô mede cada golpe defendido e acertado.
  A auditoria dizia que defender dava vantagem positiva; a medida mostrou o contrário: **nenhum** golpe era positivo
  na defesa, a mediana era -24 (tudo punível com qualquer coisa). Com `guard.hittime` calibrado golpe a golpe
  (tabela em `ferramentas/mecanica_guarda.json`) a mediana foi para -8 (Hazak -5), a faixa dos jogos grandes.
  Antiaéreo e afastar de defesa ficam bem puníveis de propósito. Gráfico em `docs/mecanica-25-11/`.
- **A11:** nada a fazer. Os agarrões normais dos 6 já caem em 820/832 com escape (y ou b nos 7 primeiros tiques).
- **B3 (`ferramentas/faisca_proporcional.py`):** golpe que não derruba tem faísca do tamanho dele; o estouro vermelho
  ficou só para o que derruba, especial e super. Primeira tentativa (clarão do 9201 menor) foi reprovada na revisão
  porque parecia nuvem rosa em cima do corpo; ficou o risco de luz.
- **A3 (`ferramentas/limpar_calca_sff.py` + `.air`):** 240 sem os 3 quadros congelados (49049,7 a 9) e com manchas
  azuis e rachaduras da calça tapadas nos quadros 1 a 9; 245 com o joelho armado à frente no preparo (era o pé virado
  para trás).
- **C1:** regras do Alisson e a seção de mecânica em `como-trabalhar.md`.

## Sugestões para depois

- **A2, soco forte do Pengaró:** ele usa de propósito o desenho do "martelo" (chute). Não existe desenho de soco forte
  nem de cotovelada no kit; precisa de desenho novo. Vai para a fila de imagens.
- **Calça do 240:** sobrou uma dobra escura perto da cintura, que vem do desenho em si. Para zerar, refazer a calça a
  partir do desenho original (regra "desenho original é a base"), quando as imagens voltarem.
- **A6 (régua no quadro final):** medir no `.sff` final, não só nas peças: quadro congelado repetido, buraco
  transparente dentro do corpo, mancha escura em área clara. O `limpar_calca_sff.py` já tem a detecção de mancha e de
  rachadura; dá para virar um `--conferir` geral.
- **A9:** os 5 lutadores do kit do Pengaró têm a mesma tabela de normais (dano, tempo). Dar cara própria a cada um é
  decisão de jogo; dá para fazer só com números.
- **B2, Raiclaven:** a parte sem imagem (tempo, alcance e faíscas) dá para adiantar; o resto espera as imagens.

