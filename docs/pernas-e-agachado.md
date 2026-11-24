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
| Pengaró base | cabeçada agachada (410) saía em pé com a perna esticada: agora é o agachado com o tronco dobrando na cintura (`dobrar()` no `pengaro_todo.py`), caixa de ataque baixada para a testa (20,-220,120,-110); soco agachado (400) mais fundo e no tamanho do agachado, e o último quadro volta agachado | 0 | 0 de 164 ações | 189/189 | 24/11 |
| Pengaró despertado | cabeçada agachada (10410) feita do agachado dele com o tronco dobrando (`ferramentas/dobra_agachado.py`), quadros do meio na volta | 0 | — | 189/189 | 24/11 |
| Pengaró base (2ª leva) | chute baixo (430) e rasteira (440) eram desenhados uns 33% maiores que o agachado (cabeça 1,26x e 1,32x contra 0,95x): o quadro inteiro encolhe em volta do pé até o tamanho do agachado, sem mudar a pose (`ENCOLHE_ACAO` no `pengaro_todo.py`), e a Clsn1 encolheu junto no .air (alcance = onde o pé chega). Se o `gerar_pengaro.py` regerar o .air, encolher a Clsn1 do 430 e do 440 de novo (x0,75 e x0,72) | 0 | 0 | 189/189 | 24/11 |
| CK base | uppercut agachado (410) saía em pé. 1ª tentativa (a8877243) foi montada só com as peças e engrossando o braço por código: o Breno viu cintura torcida, perna entortada e buraco nas costas (no Bote também) e fez a regra do desenho original (be3c43a2). Refeito com `ck_do_original.py`: o tronco do uppercut original (cabecada/04 e 05) assentado na cintura do agachado original (cabecada/07), pela barra da camisa; Bote e Bote forte voltaram aos quadros originais da folha `caneta`; braços sem engrossar (recorte do original, aceitos na régua do corpo: o do parado tem a manga). Vídeo: antes = a versão reprovada | 0 | — | 226/226 | 24/11 |
| CK despertado (Ratão) | golpe agachado forte (10410) subia inteiro com a garrafa no alto: agora sai do agachado dele com o tronco dobrando (`dobra_agachado.py`); a garrafa do Paredão no Talo voltou ao recorte original (sem engrossar) | 0 | 0 de 52 | 226/226 | 24/11 |
| Hazak base | joelhada subindo (410) levantava inteira com o joelho no alto: agora é o agachado com o tronco entrando de ombro e testa (`dobra_agachado.py`, receita `hazak_agachado_forte`), caixa baixa (22,-186,122,-86), Clsn2 do agachado | 0 | — | 327/327 | 24/11 |
| Hazak despertado (Diabo) | a 410 no despertado mostrava o Diabo loiro em pé com a maleta: agora é o agachado do demônio dobrando (quadros próprios 41411 pelo remap); Garra Subindo (4401) do agachado dele, tronco afunda e desenrola para cima (receita `diabo_garra_subindo`) | 0 | — | 327/327 | 24/11 |
| Gbzin base | bengalada agachada (410) levantava com a bengala acima da cabeça: agora entra de tronco do agachado com a bengala (`dobra_agachado.py`, modo `REFAZER`: troca só os quadros que levantam, mesmos tiques), caixa baixa; a rasteira (440) volta para o agachado e não mais em pé | 0 | — | 236/236 | 24/11 |
| Gbzin despertado | os quatro golpes agachados (10400/10410/10430/10440) foram desenhados ~23% maiores que o agachado dele: encolhidos em volta do pé para o tamanho do agachado (caixas junto); a bengalada é a mesma troca da base | 0 | — | 236/236 | 24/11 |
| Raiclaven base | cabeçada agachada (410) levantava inteira: agora as pernas ficam as do desenho do agachado e só o tronco recua e a tesoura sobe aberta (`POSE_ACAO` no `golpes_raiclaven.py`; os golpes em pé que usam os mesmos desenhos ficam como estavam); a régua de mancha do robô de peças conta também o agachado sem braço (`piloto_raiclaven.mancha_maxima`) | 0 | 0 | 216/216 | 24/11 |

Vídeos e fotos (`.mp4` e `.png`, a foto no instante em que antes e depois mais diferem): `docs/boneco-pecas/gutto/`,
`docs/boneco-pecas/todo/` (Pengaró), `docs/boneco-pecas/ck/`, `docs/boneco-pecas/hazaki/`, `docs/boneco-pecas/gbzin/` e `docs/boneco-pecas/raiclaven/`, todos `pernas_antes_depois`. Os primeiros vídeos (24/11
de manhã) mostravam o lutador novo dos dois lados, porque o `video_golpe.py` lê sempre `chars/<lutador>`; refeitos com
`ferramentas/antes_depois/` (o antes sai de um commit do git, tela maior sem cortar cabeça e pé). O Alisson pegou.

## Ferramentas que mudaram

- `firme.py`: kit com `AGACHADOS = {...}` faz o golpe voltar para o primeiro quadro (agachado) em vez do parado; rodar
  só algumas animações não apaga mais as outras do `poses.json`.
- `pengaro_todo.py`: `DOBRA` (quadro feito do agachado com o tronco dobrado), `MAIS_FUNDO` (agacha mais fundo e volta
  ao tamanho do agachado), `AGACHADAS` (fim do golpe volta para o agachado), `volta_dobrada()` (quadros do meio).
- `dobra_agachado.py`: o mesmo dobrar para arte própria sem kit (despertados); receitas em `RECEITAS`. Aceita desenho
  em PNG (arte do despertado) e `desp=` para a ação da base que o despertado vê pelo remap (escreve o `[RemapPreset]`).
  Modo `REFAZER` (elemento a elemento: troca, encolhe e dobra só o que precisa) e `--lutador X` para rodar tudo de um
  lutador. **Quem regerar um lutador com o `gerar_<lutador>.py` roda `dobra_agachado.py --lutador X` de novo** (o
  `gerar_gbzin.py` já chama).
- `gerar_pengaro.py`: caixa da 410 na testa abaixada.
- `ck_do_original.py`: Bote, Bote forte e uppercut agachado do CK a partir do desenho original (regra de 24/11);
  `pecas_ck.py` pula esses (`DO_ORIGINAL`). O `ENGROSSAR` (engordar peça por código) foi tirado: é proibido.
- `regua_pernas.py`: o quadro só conta como "levantou" se o centro de massa E a altura do corpo sobem além do limite
  (o agachado raso do CK dava falso positivo só pelo centro).
- `ferramentas/antes_depois/`: vídeo e foto antes/depois certos (ver o LEIAME de lá).
- `boneco_gutto.py`: variantes `esticada` (do 449, com o calção) e `agachada` (do 359) da coxa da frente; `GIRO_ESTICADA`.

## Falta

Nenhum golpe agachado básico levanta mais (régua das pernas em 0 nos seis lutadores, base e despertado). Ficam só os
avisos de especiais (parry 764, 3430/3435), para olhar no vídeo. A aura do Gutto foi religada
(`aura_no_corpo.py gutto`) depois dos desenhos novos. Depois: sobras do Pengaró (manchas na calça, ombro de trás, pé girado).

**Regra (Breno, 24/11):** a régua virou regra e foi levada para o corpo todo em `ferramentas/regua_corpo.py` (braço,
cabeça e tronco na mesma conta, mais esta régua inteira). Está no passo 8 da `regra-de-criacao-de-personagem.md`, no
`como-trabalhar.md` e no checklist da seção 9 das regras. Na primeira rodada (24/11) o braço reprovou em 3 peças:
CK `braco_tras_direto` (73%) e `braco_tras_overhand` (74%), e CK despertado `braco_tras_garrafa` (71%), todos mais
finos que o braço do parado e sem a manga. Engrossar por código foi tentado e desfeito (regra do desenho original);
ficaram em `ACEITAS` no `regua_corpo.py`: são recortes do próprio desenho original, e o braço do parado tem a manga.
Tira dos braços reprovados (e do braço do Hazak aceito no olho): `docs/boneco-pecas/regua_corpo_bracos.png`.
Relatório completo da primeira rodada: `docs/boneco-pecas/regua_corpo_2026-11-24.md` (o agachado reprovado é o mesmo da fila acima).
