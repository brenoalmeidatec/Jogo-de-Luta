"""Folhas do Diabo demônio feitas no boneco de peças, no formato do motor (pastas m_* do diabo_terno).

O motor do demônio (ferramentas/diabo_demonio.py, thread do #47) troca o quadro k de cada folha pelo quadro k da pasta
sprites/hazaki/diabo_terno/m_<folha>/NN.png. Aqui cada quadro sai do kit (firme.py + kit_diabo.py): pose casada no
desenho de hoje (ou posta à mão no kit), montada com pele nas juntas e conferida pelo robô de defeitos. O recorte é o
mesmo da pasta m_* (só a figura, sem margem); o motor ancora pela mediana do tronco e pela base.

    python3 ferramentas/diabo_exportar.py [folha ...]     # sem folha: todas as de sprites/diabo_demonio/quadros_arcade_hd
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import firme  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HD = RAIZ / "sprites/diabo_demonio/quadros_arcade_hd"
SAIDA = RAIZ / "sprites/hazaki/diabo_terno"
DOCS = RAIZ / "docs/boneco-pecas/diabo_demonio"


def quadro(kit, q, guarda):
    pose = firme.pose_de(kit, q)
    out = firme.desenhar(kit, pose)
    pintado = firme.desenhar.pintado
    esp = pose.get("_especial", {}).get("var")
    if esp:
        erros = firme.conferir(out, no_chao=firme.ys_max(firme.abrir(esp)) >= firme.EIXO[1] - 8, juntas=[],
                               buraco_ok=int(firme.buracos(firme.especial(esp)).sum()))
        return out, erros, "desenho de hoje"
    if "_ar" not in pose:
        abaixo = out[firme.EIXO[1]:, :, 3] > 0
        if 0 < abaixo.sum() <= 8:
            out[firme.EIXO[1]:] = 0
    w = firme.b.mundo(pose)
    juntas = ["braco_tras", "braco_frente", "cabeca"]
    if not pose.get("_pernas"):
        juntas += ["coxa_tras", "coxa_frente", "canela_tras", "canela_frente"]
    erros = firme.conferir(out, no_chao="_ar" not in pose, juntas=[w[s][0] for s in juntas])
    m_novo, m_hoje = firme.mancha(out, guarda)
    if pintado > getattr(firme.K, "PINTADO_MAX", 30):
        erros.append(f"peito pintado à vista {pintado} px")
    if m_novo > m_hoje + getattr(firme.K, "MANCHA_FOLGA", 60):
        erros.append(f"mancha {m_novo} px (hoje {m_hoje})")
    return out, erros, "kit"


def main():
    firme.configurar("diabo")
    kit = firme.ler_kit()
    guarda = firme.desenhar(kit, {})
    folhas = sys.argv[1:] or sorted(p.name for p in HD.iterdir() if p.is_dir())
    linhas, falhas = [], 0
    for folha in folhas:
        qs = sorted(HD.glob(f"{folha}/[0-9][0-9].png"))
        destino = SAIDA / f"m_{folha}"
        destino.mkdir(parents=True, exist_ok=True)
        W, H = 300, 380
        F = Image.new("RGB", (W * len(qs), H * 2 + 20), (60, 60, 70))
        dr = ImageDraw.Draw(F)
        for i, f in enumerate(qs):
            q = f"{folha}/{f.stem}"
            out, erros, de = quadro(kit, q, guarda)
            falhas += bool(erros)
            linhas.append(f"| {q} | {de} | {'PASS' if not erros else 'FAIL ' + '; '.join(erros)} |")
            im = Image.fromarray(out)
            im.crop(im.getbbox()).save(destino / f.name)
            for r, a in enumerate((Image.open(f).convert("RGBA"), im)):
                c = a.crop((390, 290, 390 + W, 290 + H))
                bg = Image.new("RGBA", c.size, (60, 60, 70, 255))
                bg.alpha_composite(c)
                F.paste(bg.convert("RGB"), (i * W, 20 + r * H))
            dr.text((i * W + 4, 4), f"{q} ({de}){' FAIL' if erros else ''}", fill=(255, 255, 0))
        F.save(DOCS / f"m_{folha}_hoje_kit.png")
        print(folha, len(qs), "quadros")
    rel = DOCS / "robo_folhas_m.md"
    rel.write_text("| quadro | de onde | robô de defeitos |\n|---|---|---|\n" + "\n".join(linhas) +
                   f"\n\n{falhas} de {len(linhas)} quadro(s) com defeito.\n", encoding="utf-8")
    print(f"{falhas} de {len(linhas)} quadro(s) com defeito.")


if __name__ == "__main__":
    main()
