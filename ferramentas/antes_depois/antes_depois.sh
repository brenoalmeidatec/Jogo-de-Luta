#!/bin/bash
# antes_depois.sh LUT FONTE_ANTES(commit git ou pasta) SAIDA "acoes base" "acoes despertado"
# (pastas em caminho absoluto) Monta chars/<lut>antes com o lutador de antes (arquivos renomeados) e grava os vídeos de antes e de agora.
set -e
L=$1; FONTE=$2; OUT=$3; BASE=$4; DESP=$5
B=$(cd "$(dirname "$0")" && pwd); cd "$B/../.."
T=chars/${L}antes; rm -rf $T; mkdir -p $T
for e in air cns sff cmd def; do
  if [ -d "$FONTE" ]; then cp $FONTE/$L.$e $T/${L}antes.$e; else git show $FONTE:chars/$L/$L.$e > $T/${L}antes.$e; fi
done
rm -rf $OUT; mkdir -p $OUT/antes $OUT/antes_d $OUT/depois $OUT/depois_d
run() { python3 $B/vg_alto.py "$@" 2>&1 | tail -1; }
[ -n "$BASE" ] && run $OUT/antes --lutador ${L}antes --escala 1 --segundos 5 $BASE && run $OUT/depois --lutador $L --escala 1 --segundos 5 $BASE
[ -n "$DESP" ] && run $OUT/antes_d --lutador ${L}antes --escala 1 --despertado --segundos 5 $DESP && run $OUT/depois_d --lutador $L --escala 1 --despertado --segundos 5 $DESP
rm -rf $T
