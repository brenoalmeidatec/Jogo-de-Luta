# Animações no Blender (pixel art 2D a partir de um boneco 3D)

O lutador é um rig 3D simples (armature + malhas de elipsoides) montado por código. Cada quadro é posado, renderizado
de lado com câmera ortográfica (Cycles, fundo transparente) e pixelizado: 224x128, pés em (104, 119), 64 px por metro
(1,75 m = 112 px), uma paleta só para o lutador inteiro e contorno escuro de 1 px. Os quadros saem no mesmo formato
dos quadros de `sprites/pengaro/quadros/`.

```powershell
pip install bpy pillow numpy                      # o Blender como módulo Python (3.11 ou 3.13)
python ferramentas/blender/gerar.py pengaro        # todas as animações
python ferramentas/blender/gerar.py pengaro soco   # só o soco
python ferramentas/blender/gerar.py pengaro --blender "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
python ferramentas/gerar_pengaro.py                # leva os quadros novos para o .sff/.air do jogo
```

Saída em `sprites/pengaro/blender/<animacao>/NN.png`, mais `<animacao>.gif` e `<animacao>_folha.png` para ver.

## Arquivos
| Arquivo | O que faz |
|---|---|
| `rig.py` | Medidas e cores do lutador (`PENGARO`), esqueleto, malhas e a pose por ângulos. Para um lutador novo (Hazaki, Yara...), copie o dicionário `PENGARO`, mude cores/medidas e registre em `renderizar.py` (`LUTADORES`). |
| `animacoes.py` | Poses-base e quadros-chave (`GUARDA`, `SOCO_ACERTO`...) e a lista `ANIMACOES`. Ângulo positivo = para frente. As animações servem para qualquer lutador. |
| `cena.py` | Câmera, luz e render. |
| `pixelizar_quadros.py` | Reduz, paleta única, contorno. |
| `gerar.py` | Roda tudo e escreve PNGs, GIFs e folhas. |

## Como criar uma animação nova
1. Em `animacoes.py`, escreva as poses-chave (dicionários de ângulos, veja o topo de `rig.py`) e acrescente em `ANIMACOES`
   `(n_quadros, loop, [(tempo 0..1, pose), ...], ticks_por_quadro)`.
2. `python ferramentas/blender/gerar.py pengaro <nome>` e olhe o GIF.
3. Ligue ao jogo em `gerar_pengaro.py`: `NOVOS_BLENDER` (pasta de quadros inteira) ou `POSES_BLENDER` (sprite solto = animação + número do quadro).

O pé é travado no chão sozinho. No salto, a trajetória é do motor (.cns); o sprite só muda a pose.
