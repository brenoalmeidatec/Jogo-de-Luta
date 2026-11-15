# Diabo Loiro: desenhos próprios e especial novo (issue #44)

> **Mudou em 15/11 às 16:58Z (Breno, #47):** o despertado tem todos os golpes próprios e o Diabo Loiro vira um
> demônio descontrolado, **sem maleta** (garras, investidas, voo, fogo das trevas; as asas ficam). As folhas "na roupa do
> sobretudo batendo com o Hazak" desta página **pararam**. Design e lista de golpes novos esperando aprovação na #47
> (comentário 6898251397). A Cobrança (1660/1661) fica no jogo até o jogo novo de golpes entrar; a ideia dela (investida
> que atravessa projétil e rouba barra) continua como "Cobrança das Garras". As ferramentas daqui (`--juntar`,
> `harmonizar`, contato) servem para as folhas novas.

Pedido do Breno na #44 (comentários de 15/11):

1. **Sai o Chapéu Bumerangue** (3400/3401, `fx_chapeu`). No lugar entra um especial que não é projétil e não repete
   golpe de outro lutador, escolhido por nós.
2. **Desenho próprio para os golpes do Diabo** que hoje usam a folha "mais parecida", na roupa de sobretudo, com o
   mesmo movimento e as mesmas caixas do golpe do Hazak.
3. Força dos efeitos: decisão nossa.
4. Robô passando + vídeo conferido quadro a quadro, aí junta na `mugen` e posta o vídeo na #44.

## 1. O especial novo: Cobrança do Diabo (1660 / 1661)

Investida de ombro em brasa, `↘ + chute` (só na forma do Diabo, no lugar do Giro de Garagem).

| | fraca (`df_a`) | forte (`df_b`) |
|---|---|---|
| velocidade / duração | 6,5 / 12 ticks | 8,5 / 14 ticks |
| dano | 60 | 80, derruba |
| barra | tira 150 de quem apanha e dá 150 ao Diabo | igual |

- Atravessa projétil (`NotHitBy SCA, NP, SP, HP` durante a investida): é a resposta do Diabo a quem fica soltando bola.
- Efeitos: rastro de brasa a cada 3 ticks, AfterImage em brasa, explosão no pé na saída e faísca no acerto.
- Por que essa: nenhum outro lutador tem golpe que **rouba barra**, e combina com o Diabo cobrador (pasta, terno, ouro).
- Código: `ferramentas/diabo_loiro.py` (`COBRANCA`, `acao_cobranca`, `cns_cobranca`), robô em
  `ferramentas/robo/robo.lua` ("Cobranca do Diabo"), golpe na movelist por `ferramentas/hazaki_golpes.py`.

## 2. Folhas próprias

Ferramenta: `ferramentas/diabo_proprio.py`.

```
python3 ferramentas/diabo_proprio.py --fila                  # anexos e prompts (docs/diabo-44/fila.json)
python3 ferramentas/diabo_proprio.py --juntar NOME a.png b.png [--ordem "a0 a1 a2 a3 b0 b1 b2 b3"]
python3 ferramentas/diabo_proprio.py NOME                    # folha -> sprites/hazaki/diabo_terno/d_NOME/
python3 ferramentas/diabo_proprio.py --contato SAIDA NOME    # Hazak em cima, Diabo embaixo
python3 ferramentas/pixel/cores.py diabo d_NOME              # confere a paleta única (deriva até ~3 é normal)
```

- **ChatGPT**: uma folha 4x2 por pedido (`ferramentas/chatgpt_diabo.js`).
- **Gemini** (aprovado pelo Breno): desenha melhor com 4 quadros por imagem 16:9, então cada folha vem em 2 pedidos
  (fileira de cima e de baixo). O `--juntar` separa as 4 figuras de cada fileira por costuras de pouca tinta (capa e
  soco que se encostam não grudam), iguala as fileiras pela figura mais alta e monta a folha larga de 8.
- A escala segue a do Diabo antigo (1,15 da altura do Hazak em pé, com chapéu e chifres).
- Assim que existe `d_NOME/`, o `diabo_terno.py` usa a folha própria no lugar da "mais parecida" (`PROPRIAS`).

### Situação (15/11)

| folha | estado |
|---|---|
| provoca, cobranca | prontas (ChatGPT) |
| jab_duplo | fileira de cima feita no Gemini; quadros de guarda saíram sem sobretudo e sem pasta, conserto pedido quando o limite do Gemini voltar |
| cutucao, tapa_costas, chute_gancho, rasteira | Gemini, depois do limite (volta 15/11 16:13, hora da Bahia) |
| intro, chute_alto_rajada, tesoura, ar_chute, ascensao, sobe_chutando, passagem_rapida, guarda_aco, parry_alto, parry_baixo, estatueta_arremesso, despertar_pedido, vitima_agarrado, vitima_arremessado, derrota_sirene | ChatGPT, depois das 23:26 |

Limites de imagem: o Gemini Pro aguentou ~35 imagens na conta antes de barrar; o ChatGPT GO, 2 folhas por janela.
Contador compartilhado entre as threads nos arquivos do projeto (`imagens/contador-gemini.md`).

## 3. Lições

- Pedir os quadros de **guarda** com a pasta e o sobretudo escritos no prompt: o Gemini tende a tirar o casaco nos
  quadros parados (guarda com o punho de trás no peito briga com "pasta na mão de trás").
- Pedir espaço de magenta entre as figuras; quando encostam, o `--juntar` resolve pela costura.
