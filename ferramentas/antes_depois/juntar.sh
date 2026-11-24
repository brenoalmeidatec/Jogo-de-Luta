#!/bin/bash
# juntar.sh PASTA NOME_LUTADOR SAIDA.mp4 "acao|titulo" ...  (lado a lado com o mesmo tamanho, sem esticar)
P=$1; NOME=$2; SAI=$3; shift 3
F=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
cd $P; rm -f lista.txt par_*.mp4
for par in "$@"; do
  a=${par%%|*}; t=${par#*|}
  if [ $a -ge 10000 ] || [ $a -ge 47000 ]; then A=antes_d; D=depois_d; else A=antes; D=depois; fi
  wa=$(ffprobe -v error -show_entries stream=width,height -of csv=p=0 $A/acao_$a.mp4); wd=$(ffprobe -v error -show_entries stream=width,height -of csv=p=0 $D/acao_$a.mp4)
  W=$(( ${wa%,*} > ${wd%,*} ? ${wa%,*} : ${wd%,*} )); H=$(( ${wa#*,} > ${wd#*,} ? ${wa#*,} : ${wd#*,} ))
  FS=$(( (2*W+8)/26 < 30 ? (2*W+8)/26 : 30 ))
  ffmpeg -v error -y -i $A/acao_$a.mp4 -i $D/acao_$a.mp4 -filter_complex "[0:v]pad=$W:$H:(ow-iw)/2:oh-ih:color=0x28346e,drawtext=fontfile=$F:text='ANTES':x=16:y=16:fontsize=34:fontcolor=white:box=1:boxcolor=black@0.5[a];[1:v]pad=$W:$H:(ow-iw)/2:oh-ih:color=0x28346e,drawtext=fontfile=$F:text='DEPOIS':x=16:y=16:fontsize=34:fontcolor=yellow:box=1:boxcolor=black@0.5[b];[a][b]hstack=shortest=1,pad=iw+8:ih+70:4:0:color=black,drawtext=fontfile=$F:text='$NOME $t (acao $a)':x=(w-tw)/2:y=h-52:fontsize=$FS:fontcolor=white,scale=-2:720,fps=60,format=yuv420p" -t 5 -an -c:v libx264 -crf 22 par_$a.mp4 && echo "file 'par_$a.mp4'" >> lista.txt
done
ffmpeg -v error -y -f concat -safe 0 -i lista.txt -c copy $SAI; ls -la $SAI
