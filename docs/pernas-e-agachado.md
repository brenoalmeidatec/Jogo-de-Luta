# Pernas e agachado (pedido do Breno na #32, 22/11)

O que o Breno pediu: agachado com perna esticando (agachar, golpes agachados, defesa baixa), pernas desproporcionais
(fina, comprida, torta, fora do quadril), robô mais rigoroso, vídeo antes/depois de cada lutador e só entrar na `mugen`
com o robô em zero.

## Régua das pernas (`ferramentas/regua_pernas.py`)

```
python3 ferramentas/regua_pernas.py                 # todos (pengaro gutto ck hazaki raiclaven gbzin), base e despertado
python3 ferramentas/regua_pernas.py gutto           # um lutador
python3 ferramentas/regua_pernas.py gutto --so-agachado | --so-kit | --relatorio ARQ.md
```

Precisa de `scikit-image` (`pip install scikit-image`). Sai com código 1 se reprovar.

1. **Agachado não levanta.** Para cada estado do tipo agachado (`type = C` no .cns, mais 10, 11, 12, 131, 141 e 151),
   mede a altura do centro de massa do corpo (depois de uma abertura morfológica que tira braço e perna esticados) e
   compara com o agachado (11) e o em pé (0). Golpe básico agachado (400 a 499 e comuns) que sobe mais de 45% do
   caminho agachado -> em pé reprova. As transições 10 e 12 podem ir até o em pé. Especial do tipo agachado (parry
   764, levantar 1300, 3430...) só vira aviso para olhar no vídeo. No despertado usa a ação do ChangeAnim com `var(20)`
   e o `[RemapPreset despertado]`.
2. **Perna do kit na grossura do parado.** Cada variante de perna do kit (`coxa_*_<var>`, `pernas_*`) é comparada com a
   perna do parado (coxa + canela): grossura (mediana da distância ao esqueleto) e área. Perna esticada reprova com
   grossura abaixo de 80% (fina) ou acima de 160% (calça larga balançando passa), ou área abaixo de 70%. Perna dobrada
   (câmara, agachada, apoio, `pernas_*`) reprova com área fora de 60% a 140%.

## Andamento

| lutador | o que mudou | régua | robô de peças | robô de luta | na mugen |
|---|---|---|---|---|---|
| Gutto base | perna da frente esticada e agachada novas (saem do calção, grossura 107% e 86% do parado); 9 chutes refeitos: chute alto, quina, coice, chute forte, super chutes, super beijinhos, chute alto e baixo agachados, rasteira | 0 | 0 de 193 | 186/186 | 24/11 |
| Gutto despertado (Garanhão) | chifrada que sobe (10410) fica de quatro, só tronco, cabeça e patas sobem; golpes agachados do kit voltam para o agachado, não para o em pé (`AGACHADOS` no kit, `firme.py`) | 0 | 0 de 242 | 186/186 | 24/11 |

Vídeo e tiras: `docs/boneco-pecas/gutto/pernas_antes_depois.mp4` e `.png`.

## Ferramentas que mudaram

- `firme.py`: kit com `AGACHADOS = {...}` faz o golpe voltar para o primeiro quadro (agachado) em vez do parado; rodar
  só algumas animações não apaga mais as outras do `poses.json`.
- `boneco_gutto.py`: variantes `esticada` (do 449, com o calção) e `agachada` (do 359) da coxa da frente; `GIRO_ESTICADA`.

## Falta

Pengaró, CK, Hazak, Raiclaven e Gbzin (base e despertado), na régua de 24/11: golpe agachado 410 levanta em quase
todos; 400/440 no CK e Gbzin; kits com grossura fora (Hazak, Pengaró, Raiclaven, Cliente). Depois: sobras do Pengaró
(manchas na calça, ombro de trás, pé girado).

**Regra (Breno, 24/11):** a régua virou regra e foi levada para o corpo todo em `ferramentas/regua_corpo.py` (braço,
cabeça e tronco na mesma conta, mais esta régua inteira). Está no passo 8 da `regra-de-criacao-de-personagem.md`, no
`como-trabalhar.md` e no checklist da seção 9 das regras. Na primeira rodada (24/11) o braço reprovou em 3 peças:
CK `braco_tras_direto` (73%) e `braco_tras_overhand` (74%), e CK despertado `braco_tras_garrafa` (71%), todos mais
finos que o braço do parado e sem a manga; entram na fila do CK junto com as pernas.
Tira dos braços reprovados (e do braço do Hazak aceito no olho): `docs/boneco-pecas/regua_corpo_bracos.png`.
Relatório completo da primeira rodada: `docs/boneco-pecas/regua_corpo_2026-11-24.md` (o agachado reprovado é o mesmo da fila acima).
