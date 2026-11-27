"""Rastreia separadamente as duas solas brancas na captura RGB do CK base."""
import cv2
import numpy as np


def medir(quadros, estados):
    def branco(im):
        rgb = np.array(im, dtype=np.int16)
        return ((rgb.min(2) > 145) & (rgb.max(2) - rgb.min(2) < 75)).astype(np.uint8)

    referencia = branco(quadros[5])
    # Isola a parte inferior da tela, abaixo do retrato e da bermuda.
    referencia[:int(referencia.shape[0] * .78)] = 0
    caixas = cv2.connectedComponentsWithStats(referencia)[2][1:]
    botas = sorted((x, y, w, h) for x, y, w, h, area in caixas if area > 70)
    chao = max(y+h for x, y, w, h in botas)
    botas = [b for b in botas if b[1]+b[3] >= chao-3]
    assert len(botas) == 2, botas
    for lado, (x, y, w, h) in zip(("trás", "frente"), botas):
        # Inclui fundo à volta da sola para detectar deriva nas duas direções.
        y = y+h-10
        modelo = referencia[y-2:y+13, x-3:x+w+3]
        deslocamentos = []
        for tick, (im, estado) in enumerate(zip(quadros, estados), 1):
            margem = 12
            roi = branco(im)[y-2-margem:y+13+margem, x-3-margem:x+w+3+margem]
            score = cv2.matchTemplate(roi, modelo, cv2.TM_CCORR_NORMED)
            _, qualidade, _, (mx, my) = cv2.minMaxLoc(score)
            deslocamentos.append((abs(mx-margem), abs(my-margem)))
            assert qualidade > .90, (lado, tick, estado, qualidade)
        dx, dy = np.max(deslocamentos, axis=0)
        print(f"Tênis {lado}: {len(quadros)} tiques, deslocamento máximo x={dx}, y={dy} px")
        assert dx <= 1 and dy <= 1, lado
