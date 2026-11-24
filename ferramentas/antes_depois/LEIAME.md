# Vídeo antes/depois de um lutador

O `video_golpe.py` lê sempre `chars/<lutador>`: copiar a pasta antiga para outro lugar NÃO faz o "antes" (foi o erro
dos primeiros vídeos da #32, que mostravam o lutador novo dos dois lados). Aqui o "antes" vira um lutador temporário
`chars/<lutador>antes` (tirado de um commit do git ou de uma pasta), apagado no fim. A tela é maior (1000x560), então
a cabeça e o pé do desenho 3x não saem cortados.

```
ferramentas/antes_depois/antes_depois.sh gutto 74c33529 /tmp/v "410 430 440" "10410"   # commit ou pasta do antes
ferramentas/antes_depois/juntar.sh /tmp/v Gutto /tmp/v/gutto.mp4 "410|chute alto agachado" "10410|Garanhao chifrada"
python3 ferramentas/antes_depois/quadro_max.py /tmp/v /tmp/v/gutto.png 410 430 10410   # foto no instante que mais muda
```

Ações de 10000 para cima (e 47000+) saem com `--despertado`. Confira a foto: se antes e depois estão iguais, o
vídeo está errado.
