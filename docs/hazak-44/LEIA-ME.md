# Hazak: pedra, bola de ki e Diabo Loiro (issue #44)

Pedido do Breno em 2026-11-14 para o Hazak: tirar a "rede de futebol", trocar os poderes de longe por **pedra** e
**bola de ki**, ligar o **Diabo Loiro** de ponta a ponta com a **Rajadona de Ki das Trevas** (preta, vermelha e ouro,
com fumaça e faíscas) e um agarrão próprio da forma, tudo com efeitos em laranja-ouro.

## O que entrou

| Pedido | Como ficou |
|---|---|
| Rede de futebol | Era a malha de hexágonos da defesa (9216). Já saiu no #38 (`09d76273`). |
| Pedra (↓ → + soco) | Ele chuta o chão, a poeira sobe, uma pedra grande sobe do chão e ele manda ela voando. **x** soca a pedra (mais lenta, 65), **y** chuta (mais rápida, 80). No acerto a pedra quebra em poeira. |
| Bola de ki (→ ← + soco) | Pose de carga com as **duas mãos brilhando em vermelho**, depois solta uma bola vermelha grande. **y** carrega mais (90 de dano). Estouro vermelho no acerto. |
| Diabo Loiro (x + y com a barra cheia) | Cena: ele bate o pé, a **patroa** entra, ele pergunta "Ô vida, posso despertar?", ela acena que sim e sai. Clarão de ouro, tela treme e ele vira o Diabo: **juba loira, dois chifres e olho vermelho**, gi roxo-escuro com debrum em brasa. Aura grande em 2 camadas (asas de fogo com coroa atrás, fogo e brasas no chão). Dura 10 s. Bate 25% mais forte. |
| Rajadona de Ki das Trevas (→ ← + soco, no Diabo, 1 barra) | Raio enorme e contínuo de ponta a ponta da tela: **casca preta, miolo vermelho e ouro, fumaça preta em bolhas nas bordas e faíscas de ouro**. 12 acertos de 16, chama no oponente a cada acerto, tela treme e o fundo pisca. |
| Agarrão da forma | O Abraço de Quebrada pega fogo no Diabo: chama laranja-ouro em cada pancada, estouro de ouro no final e +40 de dano, com tremida. |
| Laranja-ouro | Aura, chamas do agarrão e clarões da forma na paleta laranja-ouro. A rajadona é preta, vermelha e ouro. |

A arte do Diabo é **feita por código** (`ferramentas/diabo_arte.py`) em cima dos 360 desenhos do Hazak. Funciona, mas é
quebra-galho. Se o Breno quiser o terno de folhas do conceito, dá para fazer as folhas no ChatGPT depois e trocar só a
arte.

## Arquivos

- `transformacao.gif`, `rajadona.gif`, `agarrao_de_fogo.gif`: recortes do vídeo.
- `diabo-loiro.mp4`, `pedra-e-bola-de-ki.mp4`: o robô jogando no motor de verdade, na nuvem.

## Como refazer

```bash
bash ferramentas/efeitos_pixel/preparar_nuvem.sh && source ~/.nazafight/ambiente.sh
"$NAZAFX_PY" ferramentas/hazak_poderes_blender.py   # pedra, ki e rajadona (Blender + pixelfx, ~1 min)
python3 ferramentas/gerar_hazaki.py                  # gera o Hazak; no fim chama diabo_loiro.py e legibilidade.py
python3 ferramentas/testar_pengaro.py --linux --lutador hazaki
python3 ferramentas/filmar_robo.py --lutador hazaki --filtro "Diabo Loiro" --saida docs/hazak-44 --nome diabo-loiro.mp4
```

Peças: `diabo_arte.py` (arte da forma), `diabo_loiro.py` (pós-passo: efeitos no .sff, estados 2000/1650, -2, -4,
comandos e agarrão), `hazak_poderes_blender.py` (efeitos), `filmar_robo.py` (filma qualquer parte do robô).

Para quem mexer depois: o Diabo liga em `Time = 122` do estado 2000 (não no fim da animação), a cena usa `Pause 162`;
var(20) é o tempo do Diabo e var(37) diz se a arte está ligada.

## Próximos passos sugeridos

- Folhas desenhadas do Diabo (terno do conceito) para trocar a arte feita por código.
- Som próprio da patroa e da rajadona (hoje usa os sons de ki do #46).
- Comparar a rajadona do Blender com uma feita direto no pixelfx, como o Breno pediu na #47.
