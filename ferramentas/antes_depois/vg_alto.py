"""video_golpe.py com tela maior (o desenho 3x não cabe na tela 420x300 e o vídeo cortava cabeça e pé)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import video_golpe as vg
vg.TELA = (1000, 560)
vg.CHAO = 520
sys.argv = [sys.argv[0]] + sys.argv[1:]
vg.main()
