#!/usr/bin/env python3
"""Vídeo lado a lado, tira de ticks e folha antes/depois do Raiclaven no boneco de peças (o video_pecas.py do
Pengaró apontado para ele).

  python ferramentas/video_raiclaven.py docs/boneco-pecas/raiclaven
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import video_pecas as vp  # noqa: E402
from piloto_raiclaven import ATUAL, SPR  # noqa: E402

vp.SPR = SPR
vp.ATUAL = {k: v for k, v in ATUAL.items() if (SPR / "quadros_pecas_hd" / k / "tempos.json").exists()}
vp.CORTE = (360, 270, 740, 670)

if __name__ == "__main__":
    vp.main()
