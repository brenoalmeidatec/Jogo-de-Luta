#!/usr/bin/env bash
# Exporta efeitos do pixelfx como folhas de sprites para assets/efeitos/. Precisa de git e Node 18+.
#   bash ferramentas/exportar_efeitos.sh impacts/hit-spark fire/fireball
# Lista de efeitos: https://patch-gg.github.io/pixelfx/
set -e
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
TMP="${TMPDIR:-/tmp}/pixelfx"
[ -d "$TMP" ] || git clone --depth 1 https://github.com/patch-gg/pixelfx.git "$TMP"
EFEITOS="${@:-impacts/hit-spark impacts/blunt-hit impacts/crit-hit impacts/shield-block impacts/parry}"
(cd "$TMP" && node tools/render.mjs $EFEITOS --sheet --no-actor --bg none --out "$TMP/out")
for d in "$TMP"/out/*/*/; do n=$(basename "$d"); cp "$d/$n.png" "$d/$n.json" "$RAIZ/assets/efeitos/"; done
echo "Efeitos copiados para assets/efeitos/"
