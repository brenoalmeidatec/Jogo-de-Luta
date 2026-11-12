"""Aura DISCRETA do Despertar (regra do Breno, docs/regra-efeitos-proporcionais.md): UMA camada leve, baixa, atrás do
corpo, desenhada em 3x (no jogo o Explod usa scale 1/3) e quantizada no estilo arcade com a paleta da aura.

    python ferramentas/aura_blender/discreta.py <lutador> <pasta de trabalho>                    # render, compor, instala
    python ferramentas/aura_blender/discreta.py <lutador> <pasta de trabalho> compor instala     # sem o Blender

A pasta de trabalho é a do script da aura grande (pengaro_aura.py, ck_aura.py): ela tem o rig.blend (as malhas com
ossos já animadas pela etapa `rig`) e os recortes que ele usa de textura. Se não existir, rode antes:
    python ferramentas/aura_blender/<lutador>_aura.py <pasta de trabalho> recortes rig

O que cada etapa faz:
  render  abre o rig.blend no Blender, deixa renderizar só as peças de DISCRETA[lutador], encolhe cada uma em volta do
          pé (um vazio pai na origem, que é o pé do lutador, com escala (sx, 1, sz)) e renderiza em 6x (2160x1200),
          uma passada por peça, no laço da própria peça. Saída: <pasta>/discreta/render/<peça>_NN.png
  compor  6x -> 3x pela média 2x2 do comum.reduz (cor dos subpixels opacos, alfa por maioria); as peças empilhadas na
          ordem de DISCRETA num laço só; paleta fixa da aura (as 15 cores do aura.json) com histerese; contorno escuro
          de 2 px embaixo e dos lados; farelo apagado. Saída: <pasta>/discreta/camada/discreta_NN.png, tira e medidas
  instala apaga os PNG da aura antiga de sprites/<id>/aura/ e grava discreta_NN.png + aura.json (formato 2, escala 3)

A camada sai em 1080x600 com o pé em (540, 570): 3x da tela 360x200 da aura grande. Quem liga no jogo é o
ferramentas/aura_<lutador>.py, com aura.Camada(res=3).
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import comum as C

RES = 3          # px da camada por px do jogo
AMP = 2          # o render sai em RES * AMP e é reduzido AMP vezes
TELA = (360, 200)
PE = (180, 190)

# Por lutador: peças do rig.blend (malha, (sx, sz) em volta do pé, quadros do laço da peça), da de trás para a da
# frente. A altura e a largura da aura grande vêm do conceito; aqui elas encolhem até a aura ficar abaixo do peito.
DISCRETA = {
    "pengaro": dict(
        script="pengaro_aura.py",
        pecas=[("malha_chao", (0.55, 0.55), 96), ("malha_coluna", (0.62, 0.38), 48)],
        o_que="fumaça violeta-preta das sombras, baixa (do chão até o peito), saindo de um chão rachado pequeno"),
    "ck": dict(
        script="ck_aura.py",
        pecas=[("malha_paredao", (0.36, 0.36), 48)],
        o_que="paredão de som de fumaça cinza-esverdeada pequeno, atrás das pernas (até a cintura), cones batendo"),
}


def render(lutador, pasta):
    """Roda DENTRO do Blender, com o rig.blend já aberto."""
    import bpy
    d = DISCRETA[lutador]
    cena = bpy.context.scene
    cena.render.resolution_x, cena.render.resolution_y = TELA[0] * RES * AMP, TELA[1] * RES * AMP
    cena.render.resolution_percentage = 100
    pecas = {nome: bpy.data.objects[nome] for nome, _, _ in d["pecas"]}
    for nome, (sx, sz), _ in d["pecas"]:
        raiz = pecas[nome]
        while raiz.parent:
            raiz = raiz.parent
        vazio = bpy.data.objects.new("encolhe_" + nome, None)
        cena.collection.objects.link(vazio)
        vazio.location, vazio.scale = (0, 0, 0), (sx, 1, sz)
        raiz.parent = vazio          # sem parent inverse: o local da raiz passa a valer dentro do vazio
    malhas = [o for o in bpy.data.objects if o.type == "MESH"]
    saida = os.path.join(pasta, "discreta", "render")
    os.makedirs(saida, exist_ok=True)
    t0 = time.time()
    for nome, _, n in d["pecas"]:
        for o in malhas:
            o.hide_render = o is not pecas[nome]
        for f in range(n):
            cena.frame_set(f)
            cena.render.filepath = os.path.join(saida, f"{nome}_{f:02d}.png")
            bpy.ops.render.render(write_still=True)
    print("TEMPO_RENDER", time.time() - t0)


def _contorno2(idx):
    """Contorno escuro de 2 px (o 1 px do 1x, em 3x): o do comum.contorno e mais um anel por dentro dele."""
    from scipy import ndimage as ndi
    um = C.contorno(idx)
    m = idx >= 0
    dentro = ndi.binary_erosion(m, structure=ndi.generate_binary_structure(2, 1), border_value=0)
    miolo = idx.copy()
    miolo[~dentro] = -1
    dois = C.contorno(miolo)
    um[dentro & (dois == 0) & (miolo != 0)] = 0
    return um


def compor(lutador, pasta):
    from PIL import Image
    d = DISCRETA[lutador]
    info = json.load(open(os.path.join(C.RAIZ, "sprites", lutador, "aura", "aura.json"), encoding="utf-8"))
    pal = C.Paleta(info["paleta"])
    n = int(np.lcm.reduce([k for _, _, k in d["pecas"]]))
    def le(arq):  # em uint8: 144 quadros de 1080x600 em float passariam de 1 GB
        rgb, m = C.le_render(arq, AMP)
        return np.clip(np.round(rgb), 0, 255).astype(np.uint8), m
    pecas = {nome: [le(os.path.join(pasta, "discreta", "render", f"{nome}_{f:02d}.png")) for f in range(k)]
             for nome, _, k in d["pecas"]}
    quadros = []
    for f in range(n):
        rgb, m = None, None
        for nome, _, k in d["pecas"]:
            r, mm = pecas[nome][f % k]
            if rgb is None:
                rgb, m = r.copy(), mm.copy()
            else:
                rgb[mm], m = r[mm], m | mm
        quadros.append((rgb, m))
    idx = [C.limpa(_contorno2(q), minimo=6 * RES * RES) for q in pal.encaixa_seq(quadros)]
    cam = os.path.join(pasta, "discreta", "camada")
    C.exporta_camadas(cam, {"discreta": idx}, pal)
    mascaras = [q >= 0 for q in idx]
    linhas = np.nonzero(np.any(mascaras, axis=(0, 2)))[0]
    colunas = np.nonzero(np.any(mascaras, axis=(0, 1)))[0]
    pe_y = PE[1] * RES
    med = dict(quadros=n, tela=[TELA[0] * RES, TELA[1] * RES], pe=[PE[0] * RES, pe_y],
               altura_jogo=round((pe_y - int(linhas.min())) / RES, 1),
               largura_jogo=round((int(colunas.max()) - int(colunas.min()) + 1) / RES, 1),
               pares_consecutivos_iguais=int(sum(np.array_equal(a, b) for a, b in zip(idx, idx[1:] + idx[:1]))),
               mudanca_por_quadro=[round(float((a != b).mean() * 100), 3) for a, b in zip(idx, idx[1:] + idx[:1])][:8],
               pixels_que_nunca_mudam=int((np.all([q == idx[0] for q in idx], axis=0) & mascaras[0]).sum()))
    json.dump(med, open(os.path.join(pasta, "discreta", "medidas.json"), "w"), indent=1)
    print(json.dumps(med))
    # tira: 8 quadros sobre cinza e sobre o azul do cenário de teste, em 1x de tela (1/3)
    fundo = Image.new("RGBA", (TELA[0] * 4, TELA[1] * 2), (70, 70, 80, 255))
    for k in range(8):
        q = Image.open(os.path.join(cam, f"discreta_{k * n // 8:02d}.png")).resize(TELA, Image.BOX)
        fundo.alpha_composite(q, ((k % 4) * TELA[0], (k // 4) * TELA[1]))
    fundo.save(os.path.join(pasta, "discreta", "tira.png"))


def instala(lutador, pasta):
    import shutil
    d = DISCRETA[lutador]
    destino = os.path.join(C.RAIZ, "sprites", lutador, "aura")
    info = json.load(open(os.path.join(destino, "aura.json"), encoding="utf-8"))
    cam = os.path.join(pasta, "discreta", "camada")
    n = len([a for a in os.listdir(cam) if a.startswith("discreta_") and a.endswith(".png")])
    for a in os.listdir(destino):
        if a.endswith(".png"):
            os.remove(os.path.join(destino, a))
    for f in range(n):
        shutil.copy2(os.path.join(cam, f"discreta_{f:02d}.png"), destino)
    novo = dict(formato=2, lutador=lutador, aura="discreta", tela=[TELA[0] * RES, TELA[1] * RES],
                pe=[PE[0] * RES, PE[1] * RES], escala=RES, tiques_por_quadro=2, alfa="0 ou 255",
                arquivo="{nome}_{quadro:02d}.png",
                camadas=[dict(nome="discreta", quadros=n, plano="atras", o_que=d["o_que"])],
                paleta=info["paleta"],
                nota=("Regra dos efeitos proporcionais (Breno, 2026-11-12): uma camada leve, baixa, atrás do corpo, em 3x. "
                      "Peças do rig.blend da aura grande (" + d["script"] + ") encolhidas em volta do pé: " +
                      ", ".join(f"{nome} {sx}x{sz}" for nome, (sx, sz), _ in d["pecas"])),
                gerado_por="ferramentas/aura_blender/discreta.py")
    with open(os.path.join(destino, "aura.json"), "w", encoding="utf-8") as fo:
        json.dump(novo, fo, indent=1, ensure_ascii=False)
    print(f"instalado: {n} quadros em {destino}")


def main():
    try:
        import bpy  # noqa: F401
        args = sys.argv[sys.argv.index("--") + 1:]
        render(args[0], args[1])
        return
    except ImportError:
        pass
    sys.stdout.reconfigure(encoding="utf-8")
    lutador, pasta, *etapas = sys.argv[1:]
    assert lutador in DISCRETA, f"lutador sem aura discreta: {lutador} (há {', '.join(DISCRETA)})"
    pasta = os.path.abspath(pasta).replace("\\", "/")
    for e in etapas or ["render", "compor", "instala"]:
        t0 = time.time()
        print(f"== {e} ==", flush=True)
        if e == "render":
            blend = os.path.join(pasta, "rig.blend")
            assert os.path.exists(blend), f"sem {blend}: rode antes {DISCRETA[lutador]['script']} {pasta} recortes rig"
            log = os.path.join(pasta, "discreta_blender.log")
            with open(log, "w", encoding="utf-8", errors="replace") as fo:
                r = subprocess.run([C.BLENDER, "-b", blend, "--python", os.path.abspath(__file__), "--", lutador, pasta],
                                   stdout=fo, stderr=subprocess.STDOUT)
            saida = open(log, encoding="utf-8", errors="replace").read()
            if r.returncode != 0 or "Traceback" in saida or "TEMPO_RENDER" not in saida:
                print(saida[-3000:])
                sys.exit(f"Blender falhou (veja {log})")
            print(next(l for l in saida.splitlines() if l.startswith("TEMPO_RENDER")))
        else:
            {"compor": compor, "instala": instala}[e](lutador, pasta)
        print(f"== {e}: {time.time() - t0:.1f} s ==", flush=True)


if __name__ == "__main__":
    main()
