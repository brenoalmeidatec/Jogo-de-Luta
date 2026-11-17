# Pausa 17/11: braço novo do Gutto (soco forte direto + chute alto)

Branch: `claude/project-thread-zoipeb` (NÃO está na mugen: falta conferir, ligar e passar nos robôs).

## O que foi feito
- Arte nova do ChatGPT (Browser 2): `sprites/gutto/arte_braco/` (`chatgpt_original.png`; `9901_0_grande.png` = direto,
  `9902_0_grande.png` = chute com braço para trás). `ferramentas/arte_braco_gutto_cor.py` gera `9901_0.png`/`9902_0.png`
  na escala do kit (0,8) com a cor de pele do Gutto. `boneco_gutto.garantir_hd` copia a arte para `quadros_sff_hd`.
- `ferramentas/boneco_gutto.py`, VARIANTES novas:
  - `braco_tras: direto` (braço de perto esticado, com a corda) e `tronco: direto` (tronco virado do mesmo desenho:
    sem isso aparecia o peito pintado chapado que o braço de trás tapa no parado). As juntas batem entre si (o braço
    fica onde estava na arte).
  - `braco_frente: atras` (só antebraço e mão, atrás do tronco com `_atras`) para o chute alto 957_0.
- ANIM `soco_forte` virou direto (mesmos ticks e caixa: `tempos.json` igual, dá para usar `trocar_desenhos.py`).
  ANIM `chute_alto` 957_0 usa `braco_frente atras` + `_atras`.
- `animar soco_forte chute_alto` roda com 0 defeito no robô de peças. Visual do direto (quadros 02-04) ficou bom.

## Onde parou
- Conferindo quadro a quadro. Faltava olhar: o chute alto 05/06 (se a mão atrás das costas aparece certa ou some),
  a aba recortada perto do ombro da frente no quadro 01 da antecipação (já existia antes) e os fiapos nos pés do 970.

## Próximos passos exatos
1. `python3 ferramentas/boneco_gutto.py animar soco_forte chute_alto` e olhar `sprites/gutto/quadros_pecas_hd/<golpe>/`.
2. `python3 ferramentas/trocar_desenhos.py gutto soco_forte chute_alto` (tempos iguais), depois
   `python3 ferramentas/aura_silhueta.py gutto` e `python3 ferramentas/encolher_sff.py gutto --indexar 49000-49099`.
3. Robô: `python3 ferramentas/testar_pengaro.py --linux --lutador gutto` (tem que dar 186/186) e vídeo com
   `ferramentas/filmar_golpes_linux.py`.
4. Juntar na mugen (atualizar antes), comentar na issue #48.
5. ChatGPT: contar 1 imagem em `/mnt/project-files/imagens/fila-chatgpt.md` e apagar o chat "Generate pixel art poses"
   (6afc946a) com "Excluir também os arquivos".
