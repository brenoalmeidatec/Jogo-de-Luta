"""Folhas PROVISÓRIAS do Gutto, para o personagem montar enquanto a arte de verdade não existe.

O ChatGPT (plano Plus) tem limite diário de imagens. Estas cinco folhas ficaram sem gerar e entram aqui como cópia de
outra folha, só para o gerador fechar. Troque pelas verdadeiras (pedidos em folhas_gutto.py) e apague este arquivo:

  derrota      cópia de queda       (cai e fica deitado)
  lata         cópia de provoca     (aquecimento da intro)
  despertar_a  cópia de provoca     (transformação, parte 1: precisa da arte do cavalo)
  despertar_b  cópia de vitoria     (transformação, parte 2: precisa da arte do cavalo)
  endiabrado   as 8 poses da forma de cavalo: ver gerar_gutto.py (escurece e avermelha as poses normais)

Uso: python ferramentas/provisorios_gutto.py   (só cria o que não existe)
"""
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FOLHAS = RAIZ / "sprites/gutto/quadros/folhas"
COPIAS = {"derrota": "queda", "lata": "provoca", "despertar_a": "provoca", "despertar_b": "vitoria"}

if __name__ == "__main__":
    feitos = []
    for novo, origem in COPIAS.items():
        destino = FOLHAS / f"{novo}.png"
        if not destino.exists():
            shutil.copy(FOLHAS / f"{origem}.png", destino)
            feitos.append(novo)
    (FOLHAS / "PROVISORIAS.txt").write_text(
        "Folhas provisórias (cópias): " + ", ".join(COPIAS) + "\nTroque pelas verdadeiras e apague este arquivo.\n",
        encoding="utf-8")
    print("provisórias criadas:", feitos or "nenhuma (já existiam)")
