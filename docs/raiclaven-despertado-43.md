# Raiclaven despertado (issues #38 e #43): progresso

Atualizado em 2026-11-14. Branch de trabalho `claude/project-thread-f6tbq9`, que ainda **não** foi juntada na `mugen`.
O Breno pediu na #43 que o conceito da parceira seja aprovado antes das outras folhas.

## Pronto

- **Cabelo verde** (#43 item 1). O despertado ganhou uma paleta própria no .sff, a 3ª paleta (grupo 2, item 1).
  - Por que precisou: a paleta fixa da forma base (`sprites/raiclaven/paleta_sff.act`) não tem verde nenhum, então o cabelo saía cinza.
  - Como funciona: `gerar_pengaro.escrever_sff` lê `sprites.paleta_propria` e `gravar_sff` grava as paletas extras. `conferir_sff.py` e `parry.py` preservam a paleta e o índice de cada sprite. Antes o `parry.py` regravava o .sff e apagava essa paleta.
  - A forma base continua idêntica, byte a byte, na paleta fixa.
- **Aura** (#43 item 2), em `ferramentas/aura_raiclaven.py`, com as camadas do Blender em `sprites/raiclaven/aura/`.
  - Explod 9600: leque de lâminas, foices e raios.
  - Explod 9601: lascas e limalha.
  - Cor aço com raio branco-prata. Fica atrás do lutador e no chão durante o pulo. O surto acontece nos supers e no Despertar.
- **Dupla** (#43 item 4).
  - Conceito em `sprites/raiclaven/quadros/folhas_dupla/dupla_modelo.png`, com a prévia em `docs/previas/raiclaven-dupla/`.
  - 16 de 33 folhas estão prontas: ginga, anda, agachado, pulo, defesa, apanha, queda, levanta, soco, martelo, chute_baixo, chute_alto, afastar, baixo_soco e cabecada.
  - Para cortar: `python ferramentas/gerar_raiclaven.py --dupla [e_nome ...]`. Os quadros saem em 1x e 3x, com fator 1,16.
  - Golpe sem folha ainda empresta a folha da dupla mais parecida (`EMPRESTADA_DUPLA` em `gerar_raiclaven.py`), para o cientista sem a parceira não aparecer no meio da luta.
- **Robô na nuvem**: `testar_pengaro.py --lutador raiclaven --linux` deu 185 ok e 0 falhas.
- **Fotos e vídeo do despertado**: `python3 ferramentas/fotos_despertado.py raiclaven SAIDA --segundos 30 --video`.

## Falta (depois do aval do Breno na #43)

1. **17 folhas** restantes: rasteirinha, rasteira, ar_soco, bicicleta, bola, rolamento, pente_combo, agarrao, compasso, armada, caneta, golaco, provoca, vitoria, lata, derrota, despertar_a e despertar_b. Os prompts estão em `ferramentas/folhas_raiclaven.py` (DUPLA).
2. **Hitboxes nela**: o Clsn1 das ações 1xxxx precisa ir para a navalha e o secador.
3. **Kit próprio do Cientista Louco** (#43 item 3), seguindo a ficha. Hoje o Surto é o kit do Gutto renomeado. O agarrão e o poder de longe também ficam comigo (combinado com a thread do #47).
4. **Pose de vitória**: ainda usa o cientista antigo.
5. **Conferir o tique 56** (CIENTISTA em `aura_raiclaven.py`) contra a ação 2000.
6. **Juntar na mugen** depois do aval, com o robô e as fotos de novo.

## Como rodar tudo

```
python3 ferramentas/gerar_raiclaven.py
python3 ferramentas/conferir_sff.py transplantar <raiclaven.sff da mugen> chars/raiclaven
python3 ferramentas/trocar_retratos.py raiclaven
git checkout chars/raiclaven/raiclaven.cmd
python3 ferramentas/testar_pengaro.py --lutador raiclaven --linux
```

O HD 3x precisa de `sprites/raiclaven/quadros_hd`, que fica fora do git e é gerado com `ferramentas/hd_blender.py raiclaven`.
