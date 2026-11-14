# Efeitos de todos os lutadores (issue #38, parte 1)

Pedido do Breno em 2026-11-14: efeitos só do **pixelfx** e do **Blender**, nada do ChatGPT, na cor de cada lutador e
da forma. Golpe normal usa pixelfx; especial, super e transformação têm efeito próprio feito no Blender.

## O que entrou

| Onde | O quê |
|---|---|
| Golpes normais (todos) | faísca do fraco (ventinho), do forte (estalo), do finalizador (impacto), defesa, rastro do golpe, poeira no chão e faísca do parry, dos desenhos do pixelfx de `assets/efeitos/`, pintados em degraus na rampa do lutador |
| Especiais (estados 1000-1999) | estouro do Blender no acerto (ação 9240, 9270 no despertado) |
| Supers (3000-3399) | explosão do Blender no acerto (9241 / 9271); o clarão da pausa da super, que era a faísca azul do motor, virou o estouro do lutador |
| Despertar (estado 2000) | pilar do Blender atrás do lutador quando a forma troca (9272) |

Cores (`CORES` em `ferramentas/efeitos.py`): whisky e violeta no Pengaró, laranja-ouro no Hazak, vermelho e brasa no
Gutto, aço com verde e verde de Cientista Louco no Raiclaven, cinza-esverdeado e verde de vidro no CK.

Temas do Blender (`RECEITAS` em `ferramentas/efeitos_blender.py`): gotas e cacos de garrafa no Pengaró, chamas e brasas
no Hazak, onda de choque e brasas no Gutto, lascas de aço e relâmpagos no Raiclaven, anéis de som e fumaça no CK.

Saiu: as faíscas que o ChatGPT desenhou para o Pengaró (que o Gutto, o Raiclaven e o CK usavam repintadas), a faísca
"rede de futebol" e o escudo de grade do pixelfx.

Folhas: `efeitos_<lutador>.png` nesta pasta. Vídeo: `luta_efeitos.mp4` (Pengaró x Hazak e Gutto x CK, CPU contra CPU,
barra cheia para a CPU soltar super e Despertar).

## Como refazer

```bash
python ferramentas/efeitos.py                       # liga tudo nos 5 lutadores (roda de novo sem duplicar)
python ferramentas/efeitos.py --folha docs/efeitos-38
bash ferramentas/efeitos_pixel/preparar_nuvem.sh && source ~/.nazafight/ambiente.sh
"$NAZAFX_PY" ferramentas/efeitos_blender.py         # renderiza de novo os efeitos do Blender (~4 min na nuvem)
python3 ferramentas/filmar_luta_linux.py saida.mp4 --p1 gutto --p2 ck --barra --despertar
```

- `efeitos.py` trabalha em cima de `chars/<l>/` (como o `parry.py`): troca só os efeitos. Os efeitos vão como PNG de
  32 bits no `.sff`, fora da paleta do corpo; o corpo não muda (conferido sprite a sprite).
- `parry.py` chama o `efeitos.py` no fim, então regerar um lutador (que chama o `parry.aplicar`) mantém os efeitos.
- `conferir_sff.py religar`/`transplantar` regravam o `.sff` sem os PNG: depois deles, rode o `efeitos.py`.

## Testado

- Robô na nuvem (`testar_pengaro.py --linux`) nos 5 lutadores, 0 falhas.
- Luta filmada no motor de verdade: pixel FX nos golpes normais, estouro dos especiais, explosão e pausa das supers,
  pilar do Despertar.

## Sugestões para depois

- Rastro do golpe: hoje é o mesmo arco para soco e chute; dá para escolher o arco pela direção da caixa do golpe.
- Gutto: a aura do Despertar dele ainda não é a do Blender (`aura_blender/gutto_aura.py` existe, mas não está ligada).
- Hazak: não tem Despertar; se ganhar, o pilar dele já tem cor (laranja-ouro).
- Efeito próprio por especial (cada golpe com o seu), em vez de um estouro por lutador.
