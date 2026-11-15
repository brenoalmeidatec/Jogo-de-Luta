#!/usr/bin/env python3
"""Ferramenta de pixel do NazaFight: redesenhar quadro a quadro "à mão", por comando (feita para o Claude usar) e com
uma tela simples para gente (tela.py, em construção). Tudo pinta só com a paleta da forma e guarda histórico para desfazer.

Endereço de quadro: LUTADOR/ACAO/NN (ex.: hazaki/agachado/03, diabo/d_rasteira_arco/04, ck/e_soco/02).
LUTADOR: hazaki, diabo, ck, pengaro, gutto, raiclaven. Por padrão é o desenho grande (3x) que o jogo usa; --1x usa o
pequeno (Hazak, CK e Pengaró têm os dois; `sincroniza` refaz o 1x a partir do 3x).

VER
  ver Q [--zoom 4] [--regiao x0 y0 x1 y1] [--sem-vegetal] [--saida A.png]
        quadro ampliado com grade, régua de coordenadas, papel vegetal (anterior em vermelho, seguinte em azul) e as
        linhas do parado (topo da cabeça, ombro e chão)
  tira LUTADOR/ACAO [--saida A.png]      os quadros lado a lado com as medidas e os avisos de cada um
  anima LUTADOR/ACAO [--saida A.gif|A.mp4] [--ms 80] [--zoom 2]
  compara Q|LUTADOR/ACAO [--ref HEAD]    antes (git) e depois lado a lado
  paleta Q                               lista as cores (nome, índice, hex) e salva uma amostra
  mede LUTADOR[/ACAO] [--json A.json]    réguas: escala da cabeça e do corpo contra o parado, manchas de pele
                                         (membro sobrando) e cor fora da paleta

PINTAR (COR = nome da paleta, #índice, hex rrggbb ou 'transparente')
  pinta Q COR x,y [x,y ...]
  linha Q COR x0 y0 x1 y1 [--grossura 1]
  ret Q COR x0 y0 x1 y1 [--vazio]
  balde Q COR x y                        preenche a mancha de mesma cor (4 vizinhos)
  troca Q COR_DE COR_PARA [--regiao x0 y0 x1 y1]
  apaga Q x0 y0 x1 y1 [--so COR]         (ou --poli "x,y x,y ..." no lugar do retângulo, também em copia e move)
  remenda Q x0 y0 x1 y1 [--raio 3]       tapa os buracos da região com as cores em volta (depois de apagar/mover)

MEXER EM PEDAÇOS
  copia Q x0 y0 x1 y1 [--so COR,COR]   guarda o pedaço na prancheta (com a origem)
  cola Q x y [--espelha] [--gira G] [--escala F] [--por-baixo]   (x, y = canto de cima à esquerda)
  move Q x0 y0 x1 y1 DX DY [--gira G] [--espelha] [--por-baixo]   recorta o pedaço e põe de volta deslocado/girado
  estica Q x0 y0 x1 y1 X1 Y1 [--empurra]   estica o pedaço até (X1, Y1) (alongar canela, braço...); --empurra leva
                                         junto o que vem depois (o sapato anda com a canela)
  escala Q F [--pivo eixo|pes|px,py] [--suave] [--grade N]  a figura inteira em volta do eixo (corrige proporção)
  recolore Q --matiz H0 H1 --para pele|COR,COR [--regiao ...]   troca uma família de cor por outra (claro vira claro)
  quantiza Q                             leva toda cor para a cor mais próxima da paleta

HISTÓRICO
  desfaz [Q]        volta a última alteração (do quadro, ou a última de todas)
  historico [N]     as N últimas alterações
  sincroniza LUTADOR/ACAO   refaz o 1x a partir do 3x (Hazak, CK, Pengaró)
"""
import argparse
import json
import math
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cv2  # noqa: E402
from quadros import RAIZ, Endereco, abrir, cor, paleta, salvar  # noqa: E402

CASA = Path.home() / ".nazafight" / "pixel"
HIST = CASA / "historico"
PRANCHETA = CASA / "prancheta.png"
SAIDA_PADRAO = CASA / "ver.png"


def fonte(t=12):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"):
        if Path(f).exists():
            return ImageFont.truetype(f, t)
    return ImageFont.load_default()


# ---------------------------------------------------------------------------------------------------------------------
# histórico
# ---------------------------------------------------------------------------------------------------------------------
def registrar(end, comando):
    HIST.mkdir(parents=True, exist_ok=True)
    marca = time.strftime("%Y%m%d-%H%M%S") + f"-{int(time.time() * 1000) % 1000:03d}"
    copia = HIST / f"{marca}_{end.texto().replace('/', '__')}.png"
    if end.arquivo.exists():
        shutil.copy2(end.arquivo, copia)
    with open(HIST / "log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"quando": marca, "quadro": end.texto(), "1x": end.um_x, "arquivo": end.relativo(),
                            "copia": copia.name if end.arquivo.exists() else None, "comando": comando},
                           ensure_ascii=False) + "\n")


RECORTADOS = {"diabo"}  # quadros guardados recortados na figura (a âncora é o fundo da tela): a tela acompanha o desenho


def recortar(arr):
    m = arr[..., 3] > 0
    if not m.any():
        return arr
    ys, xs = np.nonzero(m)
    return arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def folga(arr, n):
    """Tela maior em volta. Ao gravar o quadro é recortado de novo e o pixel mais baixo vira o chão, como no original."""
    return np.pad(arr, ((n, n), (n, n), (0, 0)))


def gravar(end, arr, comando):
    registrar(end, comando)
    if end.lutador in RECORTADOS:
        arr = recortar(arr)
    salvar(arr, end.arquivo)
    print(f"gravado {end.relativo()}")


def log():
    p = HIST / "log.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def desfaz(alvo=None):
    linhas = log()
    for i in range(len(linhas) - 1, -1, -1):
        e = linhas[i]
        if alvo and "/" in alvo and alvo.count("/") == 2:
            alvo = Endereco(alvo).texto()
        if e.get("desfeito") or (alvo and e["quadro"] != alvo):
            continue
        destino = RAIZ / e["arquivo"]
        if e["copia"]:
            shutil.copy2(HIST / e["copia"], destino)
        else:
            destino.unlink(missing_ok=True)
        linhas[i]["desfeito"] = True
        (HIST / "log.jsonl").write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas),
                                        encoding="utf-8")
        print(f"desfeito: {e['quadro']} ({' '.join(e['comando'])})")
        return
    print("nada para desfazer")


# ---------------------------------------------------------------------------------------------------------------------
# desenho
# ---------------------------------------------------------------------------------------------------------------------
def tinta(arr, c, pts):
    h, w = arr.shape[:2]
    for x, y in pts:
        if 0 <= x < w and 0 <= y < h:
            arr[y, x] = c


def pontos_linha(x0, y0, x1, y1):
    pts, dx, dy = [], abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1:
            return pts
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def balde(arr, x, y, c):
    alvo = arr[y, x].copy()
    if (alvo == np.array(c)).all():
        return
    igual = (arr == alvo).all(-1).astype(np.uint8)
    n, rot = cv2.connectedComponents(igual, connectivity=4)
    arr[rot == rot[y, x]] = c


def mais_proxima(arr, pal):
    alvo = np.array([rgb for _, rgb in pal], np.int32)
    m = arr[..., 3] > 0
    px = arr[m][:, :3].astype(np.int32)
    idx = np.argmin(((px[:, None, :] - alvo[None]) ** 2).sum(-1), axis=1)
    out = arr.copy()
    out[..., :3][m] = alvo[idx]
    return out


def girar(pedaco, graus, espelha=False):
    """Giro de pixel art: amplia 4x por vizinho, gira, reduz pela cor mais frequente de cada bloco (sem cor nova)."""
    if espelha:
        pedaco = pedaco[:, ::-1]
    if not graus:
        return np.ascontiguousarray(pedaco), (0, 0)
    k = 4
    g = np.repeat(np.repeat(pedaco, k, 0), k, 1)
    im = Image.fromarray(g).rotate(graus, resample=Image.NEAREST, expand=True)
    a = np.array(im)
    h, w = a.shape[0] // k, a.shape[1] // k
    out = np.zeros((h, w, 4), np.uint8)
    for yy in range(h):
        for xx in range(w):
            bloco = a[yy * k:(yy + 1) * k, xx * k:(xx + 1) * k].reshape(-1, 4)
            cheio = bloco[bloco[:, 3] > 0]
            if len(cheio) * 2 >= len(bloco):
                c = Counter(map(tuple, cheio.tolist())).most_common(1)[0][0]
                out[yy, xx] = c
    dx = (w - pedaco.shape[1]) // 2
    dy = (h - pedaco.shape[0]) // 2
    return out, (dx, dy)


def colar(arr, ped, x, y, por_baixo=False):
    h, w = ped.shape[:2]
    H, W = arr.shape[:2]
    for yy in range(h):
        ty = y + yy
        if not 0 <= ty < H:
            continue
        for xx in range(w):
            tx = x + xx
            if not 0 <= tx < W or ped[yy, xx, 3] == 0:
                continue
            if por_baixo and arr[ty, tx, 3] > 0:
                continue
            arr[ty, tx] = ped[yy, xx]


def pes(arr):
    m = arr[..., 3] > 0
    ys, xs = np.nonzero(m)
    base = ys.max()
    xb = np.nonzero(m[max(0, base - 6):base + 1].any(0))[0]
    return int(round(xb.mean())), int(base)


def scale2x(a):
    """EPX/Scale2x: dobra o desenho sem borrar e arredonda as diagonais (pixel art cresce sem virar escada)."""
    h, w = a.shape[:2]
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode="edge")
    B, D, E, F, H = p[:-2, 1:-1], p[1:-1, :-2], p[1:-1, 1:-1], p[1:-1, 2:], p[2:, 1:-1]
    eq = lambda x, y: (x == y).all(-1)
    c = ~eq(B, H) & ~eq(D, F)
    o = np.zeros((h * 2, w * 2, 4), a.dtype)
    o[0::2, 0::2] = np.where((c & eq(D, B))[..., None], D, E)
    o[0::2, 1::2] = np.where((c & eq(B, F))[..., None], F, E)
    o[1::2, 0::2] = np.where((c & eq(D, H))[..., None], D, E)
    o[1::2, 1::2] = np.where((c & eq(H, F))[..., None], F, E)
    return o


def escalar(arr, f, pivo, pal, suave=False, grade=1):
    """A figura inteira f vezes em volta do pivô. `grade` é o tamanho do pixel do desenho (3 no Hazak/CK/Pengaró, cujo
    3x é o 1x ampliado): a conta é feita no 1x e o resultado volta ampliado, para não nascer pixel de tamanho torto.
    Para crescer usa Scale2x três vezes (8x) e amostra; para encolher, a cor mais comum de cada célula."""
    g = grade
    peq = arr[g // 2::g, g // 2::g] if g > 1 else arr
    px, py = pivo[0] / g, pivo[1] / g
    H, W = peq.shape[:2]
    if suave:
        pre = peq.astype(np.float32)
        pre[..., :3] *= pre[..., 3:4] / 255
        M = np.float32([[f, 0, px - px * f], [0, f, py - py * f]])
        red = cv2.warpAffine(pre, M, (W, H), flags=cv2.INTER_AREA if f < 1 else cv2.INTER_LINEAR)
        al = red[..., 3:4]
        red[..., :3] = np.where(al > 0, red[..., :3] * 255 / np.maximum(al, 1), 0)
        nova = np.clip(red, 0, 255).astype(np.uint8)
        nova[..., 3] = np.where(nova[..., 3] >= 128, 255, 0)
        nova = mais_proxima(nova, pal)
    else:
        k = 8 if f > 1 else 1
        big = scale2x(scale2x(scale2x(peq))) if k == 8 else peq
        ys, xs = np.mgrid[0:H, 0:W]
        sx = np.floor((px + (xs + 0.5 - px) / f) * k).astype(int)
        sy = np.floor((py + (ys + 0.5 - py) / f) * k).astype(int)
        ok = (sx >= 0) & (sy >= 0) & (sx < W * k) & (sy < H * k)
        nova = np.zeros_like(peq)
        nova[ok] = big[sy[ok], sx[ok]]
    if g > 1:
        nova = nova.repeat(g, 0).repeat(g, 1)
        out = np.zeros_like(arr)
        out[:nova.shape[0], :nova.shape[1]] = nova[:arr.shape[0], :arr.shape[1]]
        return out
    return nova


def eixo(end):
    """Pés do parado (quadro 0): o eixo do lutador, igual em todos os quadros da pasta."""
    return pes(abrir(end.parado().quadros()[0]))


# ---------------------------------------------------------------------------------------------------------------------
# ver
# ---------------------------------------------------------------------------------------------------------------------
def linhas_do_parado(end):
    """(topo da cabeça, ombro, chão) do parado, em y do quadro (todo quadro da pasta tem a mesma tela e o mesmo eixo)."""
    from reguas import cabeca_do_parado
    q = end.parado().quadros()
    a = abrir(q[0])
    _, (x0, y0, x1, y1) = cabeca_do_parado(a)
    m = a[..., 3] > 0
    ys = np.nonzero(m)[0]
    return {"cabeça": int(ys.min()), "queixo": int(y1), "chão": int(ys.max())}


def ver(end, zoom=4, regiao=None, vegetal=True, saida=None, marcas=()):
    a = abrir(end.arquivo)
    camadas = []
    if vegetal:
        for passo, tom in ((-1, (230, 60, 60)), (1, (60, 120, 240))):
            p = end.vizinho(passo)
            if p is not None and p != end.arquivo:
                v = abrir(p)
                if v.shape == a.shape:
                    camadas.append((v, tom))
    H, W = a.shape[:2]
    if regiao:
        x0, y0, x1, y1 = regiao
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    else:
        m = a[..., 3] > 0
        for v, _ in camadas:
            m = m | (v[..., 3] > 0)
        ys, xs = np.nonzero(m)
        x0, y0 = max(0, xs.min() - 8), max(0, ys.min() - 8)
        x1, y1 = min(W, xs.max() + 9), min(H, ys.max() + 9)
    if end.lutador == "diabo":  # quadros recortados: as linhas do parado não valem nesta tela
        linhas = {}
    else:
        linhas = linhas_do_parado(end)
    cw, ch = x1 - x0, y1 - y0
    if not regiao:
        zoom = max(1, min(zoom, 1600 // max(cw, ch)))
    margem = 34
    img = Image.new("RGB", (cw * zoom + margem, ch * zoom + margem), (32, 32, 40))
    # xadrez de fundo
    fundo = np.zeros((ch, cw, 3), np.uint8)
    yy, xx = np.mgrid[0:ch, 0:cw]
    fundo[:] = np.where((((yy + y0) // 8 + (xx + x0) // 8) % 2 == 0)[..., None], 58, 48)
    base = fundo.astype(np.float32)
    for v, tom in camadas:
        vv = v[y0:y1, x0:x1]
        mm = vv[..., 3] > 0
        base[mm] = base[mm] * 0.45 + np.array(tom, np.float32) * 0.55
    cur = a[y0:y1, x0:x1]
    mm = cur[..., 3] > 0
    base[mm] = cur[..., :3][mm]
    big = np.repeat(np.repeat(base.astype(np.uint8), zoom, 0), zoom, 1)
    img.paste(Image.fromarray(big), (margem, margem))
    d = ImageDraw.Draw(img)
    f = fonte(11)
    if zoom >= 6:
        for gx in range(cw + 1):
            X = margem + gx * zoom
            d.line([(X, margem), (X, margem + ch * zoom)], fill=(20, 20, 26) if (gx + x0) % 10 else (90, 90, 110))
        for gy in range(ch + 1):
            Y = margem + gy * zoom
            d.line([(margem, Y), (margem + cw * zoom, Y)], fill=(20, 20, 26) if (gy + y0) % 10 else (90, 90, 110))
    passo = 10 if zoom >= 6 else (20 if zoom >= 3 else 50)
    for gx in range((x0 // passo + 1) * passo, x1, passo):
        X = margem + (gx - x0) * zoom
        d.line([(X, margem - 6), (X, margem)], fill="white")
        d.text((X + 2, 2), str(gx), fill="white", font=f)
    for gy in range((y0 // passo + 1) * passo, y1, passo):
        Y = margem + (gy - y0) * zoom
        d.line([(margem - 6, Y), (margem, Y)], fill="white")
        d.text((1, Y + 1), str(gy), fill="white", font=f)
    for nome, y in linhas.items():
        if y0 <= y <= y1:
            Y = margem + (y - y0) * zoom
            d.line([(margem, Y), (margem + cw * zoom, Y)], fill=(255, 220, 0), width=1)
            d.text((margem + cw * zoom - 60, Y - 13), nome, fill=(255, 220, 0), font=f)
    for (mx, my, rotulo) in marcas:
        X, Y = margem + (mx - x0) * zoom, margem + (my - y0) * zoom
        d.ellipse([X - 6, Y - 6, X + 6, Y + 6], outline=(0, 255, 120), width=2)
        d.text((X + 8, Y - 8), rotulo, fill=(0, 255, 120), font=f)
    d.text((margem + 4, margem + 2), f"{end.texto()}  x{zoom}  vermelho=anterior azul=seguinte", fill="white", font=f)
    saida = Path(saida or SAIDA_PADRAO)
    saida.parent.mkdir(parents=True, exist_ok=True)
    img.save(saida)
    print(f"{saida}  (região {x0},{y0}-{x1},{y1}, zoom {zoom})")
    return saida


def tira(end, saida=None, regua=None, quadros=None, rotulo=""):
    from reguas import Regua
    regua = regua or Regua(end)
    qs = quadros or end.quadros()
    imgs = [abrir(p) for p in qs]
    m = np.zeros(imgs[0].shape[:2], bool)
    for a in imgs:
        if a.shape[:2] == m.shape:
            m |= a[..., 3] > 0
    if end.lutador == "diabo":
        larg = max(a.shape[1] for a in imgs)
        alt = max(a.shape[0] for a in imgs)
        cortes = [a for a in imgs]
    else:
        ys, xs = np.nonzero(m)
        x0, y0, x1, y1 = xs.min() - 6, ys.min() - 6, xs.max() + 7, ys.max() + 7
        cortes = [a[y0:y1, x0:x1] for a in imgs]
        larg, alt = x1 - x0, y1 - y0
    esc = min(1.0, 260 / alt)
    cw, chh = int(larg * esc) + 10, int(alt * esc) + 70
    img = Image.new("RGB", (cw * len(cortes), chh + 22), (32, 32, 40))
    d = ImageDraw.Draw(img)
    f = fonte(12)
    linhas = {} if end.lutador == "diabo" else linhas_do_parado(end)
    d.text((4, 2), f"{end.lutador}/{end.acao} {rotulo}", fill="white", font=f)
    for i, (a, p) in enumerate(zip(cortes, qs)):
        r = regua.medir(abrir(p))
        av = regua.avisos(r)
        q = Image.fromarray(a).resize((max(1, int(a.shape[1] * esc)), max(1, int(a.shape[0] * esc))), Image.NEAREST)
        X = i * cw + 5
        Y = 22 + (int(alt * esc) - q.size[1] if end.lutador == "diabo" else 0)
        cor_borda = (230, 70, 70) if av else (70, 160, 90)
        d.rectangle([i * cw + 1, 20, (i + 1) * cw - 2, chh + 20], outline=cor_borda)
        img.paste(q, (X, Y), q)
        if end.lutador != "diabo":
            for nome, y in linhas.items():
                yy = 22 + int((y - (np.nonzero(m)[0].min() - 6)) * esc)
                d.line([(i * cw + 2, yy), ((i + 1) * cw - 3, yy)], fill=(255, 220, 0))
        texto = f"{p.stem}  cab {r.get('cabeca', 0):.2f} ({r.get('nota', 0):.2f})  corpo {r.get('corpo', 0):.2f}"
        if "pele" in r:
            texto += f"  pele {r['pele']}"
        d.text((X, chh - 46 + 20), texto, fill="white", font=fonte(10))
        for k, t in enumerate(av[:2]):
            d.text((X, chh - 32 + 20 + 12 * k), t, fill=(255, 120, 120), font=fonte(10))
    saida = Path(saida or CASA / f"tira_{end.lutador}_{end.acao}.png")
    saida.parent.mkdir(parents=True, exist_ok=True)
    img.save(saida)
    print(saida)
    return saida


def anima(end, saida=None, ms=80, zoom=2):
    qs = end.quadros()
    imgs = [abrir(p) for p in qs]
    if end.lutador == "diabo":
        W = max(a.shape[1] for a in imgs)
        H = max(a.shape[0] for a in imgs)
        quadros = []
        for a in imgs:
            c = np.zeros((H, W, 4), np.uint8)
            c[H - a.shape[0]:, (W - a.shape[1]) // 2:(W - a.shape[1]) // 2 + a.shape[1]] = a
            quadros.append(c)
    else:
        m = np.zeros(imgs[0].shape[:2], bool)
        for a in imgs:
            m |= a[..., 3] > 0
        ys, xs = np.nonzero(m)
        quadros = [a[ys.min() - 4:ys.max() + 5, xs.min() - 4:xs.max() + 5] for a in imgs]
    frames = []
    for a in quadros:
        fundo = Image.new("RGBA", (a.shape[1], a.shape[0]), (40, 44, 70, 255))
        fundo.alpha_composite(Image.fromarray(a))
        fr = fundo.convert("RGB")
        if zoom != 1:
            fr = fr.resize((fr.width * zoom // (end.fator if end.fator > 1 else 1),
                            fr.height * zoom // (end.fator if end.fator > 1 else 1)), Image.NEAREST)
        frames.append(fr)
    saida = Path(saida or CASA / f"{end.lutador}_{end.acao}.gif")
    saida.parent.mkdir(parents=True, exist_ok=True)
    if saida.suffix == ".mp4":
        tmp = CASA / "_anima"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True)
        for i, fr in enumerate(frames * 4):
            fr.save(tmp / f"{i:04d}.png")
        w, h = frames[0].size
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(1000 / ms), "-i", str(tmp / "%04d.png"),
                        "-vf", f"scale={w // 2 * 2}:{h // 2 * 2}:flags=neighbor", "-pix_fmt", "yuv420p", str(saida)],
                       check=True)
    else:
        frames[0].save(saida, save_all=True, append_images=frames[1:], duration=ms, loop=0)
    print(saida)
    return saida


def do_git(rel, ref):
    r = subprocess.run(["git", "-C", str(RAIZ), "show", f"{ref}:{rel}"], capture_output=True)
    if r.returncode:
        return None
    import io
    return np.array(Image.open(io.BytesIO(r.stdout)).convert("RGBA"))


def compara(end, ref="HEAD", saida=None):
    qs = [end.arquivo] if end.n is not None else end.quadros()
    pares = []
    for p in qs:
        rel = p.relative_to(RAIZ).as_posix()
        antes = do_git(rel, ref)
        depois = abrir(p)
        if antes is None:
            antes = np.zeros_like(depois)
        pares.append((antes, depois))
    m = None
    for a, b in pares:
        if a.shape == b.shape:
            mm = (a[..., 3] > 0) | (b[..., 3] > 0)
            m = mm if m is None else (m | mm if m.shape == mm.shape else m)
    linhas = []
    for a, b in pares:
        if m is not None and a.shape == b.shape == m.shape + (4,):
            ys, xs = np.nonzero(m)
            a = a[ys.min() - 4:ys.max() + 5, xs.min() - 4:xs.max() + 5]
            b = b[ys.min() - 4:ys.max() + 5, xs.min() - 4:xs.max() + 5]
        linhas.append((a, b))
    esc = min(1.0, 300 / max(max(a.shape[0], b.shape[0]) for a, b in linhas))
    cw = max(max(a.shape[1], b.shape[1]) for a, b in linhas)
    ch = max(max(a.shape[0], b.shape[0]) for a, b in linhas)
    cw, ch = int(cw * esc) + 8, int(ch * esc) + 8
    img = Image.new("RGB", (cw * len(linhas), 2 * ch + 40), (32, 32, 40))
    d = ImageDraw.Draw(img)
    d.text((4, 4), f"antes ({ref})", fill="white", font=fonte(13))
    d.text((4, ch + 22), "depois", fill="white", font=fonte(13))
    for i, (a, b) in enumerate(linhas):
        for j, x in enumerate((a, b)):
            q = Image.fromarray(x).resize((max(1, int(x.shape[1] * esc)), max(1, int(x.shape[0] * esc))),
                                          Image.NEAREST)
            img.paste(q, (i * cw + 4, 20 + j * (ch + 18) + ch - 8 - q.size[1]), q)
    saida = Path(saida or CASA / f"compara_{end.lutador}_{end.acao}.png")
    img.save(saida)
    print(saida)
    return saida


# ---------------------------------------------------------------------------------------------------------------------
# medir
# ---------------------------------------------------------------------------------------------------------------------
_REGUAS = {}


def _mede_acao(args):
    lut, acao, um_x = args
    from reguas import Regua
    end = Endereco(f"{lut}/{acao}", um_x)
    if end.forma not in _REGUAS:
        _REGUAS[end.forma] = Regua(end)
    rg = _REGUAS[end.forma]
    out = {}
    for p in end.quadros():
        r = rg.medir(abrir(p))
        av = rg.avisos(r)
        r.pop("manchas", None)
        r.pop("onde", None)
        out[f"{acao}/{p.stem}"] = {"medidas": r, "avisos": av}
    return out


def mede(texto, saida_json=None, um_x=False, processos=None):
    """Réguas em todos os quadros de um lutador (ou de uma ação), em paralelo."""
    from multiprocessing import Pool
    partes = texto.strip("/").split("/")
    lut = partes[0]
    base = Endereco(f"{lut}/x", um_x)
    acoes = [partes[1]] if len(partes) > 1 else sorted(p.name for p in base.pasta.parent.iterdir()
                                                         if p.is_dir() and list(p.glob("[0-9][0-9].png")))
    res = {}
    if len(acoes) == 1:
        res = _mede_acao((lut, acoes[0], um_x))
    else:
        with Pool(processos) as pool:
            for r in pool.imap(_mede_acao, [(lut, a, um_x) for a in acoes]):
                res.update(r)
    n_av = 0
    for k, v in res.items():
        if v["avisos"]:
            n_av += 1
            print(f"{lut}/{k}: " + "; ".join(v["avisos"]))
    print(f"{lut}: {len(res)} quadros, {n_av} com aviso")
    if saida_json:
        Path(saida_json).write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    return res


# ---------------------------------------------------------------------------------------------------------------------
# linha de comando
# ---------------------------------------------------------------------------------------------------------------------
def xy(t):
    x, y = t.split(",")
    return int(x), int(y)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--1x", dest="um_x", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def s(nome, *args, **kw):
        p = sub.add_parser(nome)
        for a in args:
            p.add_argument(a)
        return p

    p = s("ver", "q"); p.add_argument("--zoom", type=int, default=4); p.add_argument("--regiao", type=int, nargs=4)
    p.add_argument("--sem-vegetal", action="store_true"); p.add_argument("--saida")
    p = s("tira", "q"); p.add_argument("--saida")
    p = s("anima", "q"); p.add_argument("--saida"); p.add_argument("--ms", type=int, default=80)
    p.add_argument("--zoom", type=int, default=2)
    p = s("compara", "q"); p.add_argument("--ref", default="HEAD"); p.add_argument("--saida")
    p = s("paleta", "q")
    p = s("mede", "q"); p.add_argument("--json")
    p = s("pinta", "q", "cor"); p.add_argument("pontos", nargs="+")
    p = s("linha", "q", "cor"); p.add_argument("c", type=int, nargs=4); p.add_argument("--grossura", type=int, default=1)
    p = s("ret", "q", "cor"); p.add_argument("c", type=int, nargs=4); p.add_argument("--vazio", action="store_true")
    p = s("balde", "q", "cor"); p.add_argument("x", type=int); p.add_argument("y", type=int)
    p = s("troca", "q", "de", "para"); p.add_argument("--regiao", type=int, nargs=4)
    p = s("apaga", "q"); p.add_argument("c", type=int, nargs="*"); p.add_argument("--so"); p.add_argument("--poli")
    p = s("copia", "q"); p.add_argument("c", type=int, nargs="*"); p.add_argument("--so"); p.add_argument("--poli")
    p = s("remenda", "q"); p.add_argument("c", type=int, nargs="*"); p.add_argument("--poli")
    p.add_argument("--raio", type=int, default=3)
    p = s("cola", "q"); p.add_argument("x", type=int); p.add_argument("y", type=int)
    p.add_argument("--espelha", action="store_true"); p.add_argument("--gira", type=float, default=0)
    p.add_argument("--escala", type=float, default=1); p.add_argument("--por-baixo", action="store_true")
    p = s("move", "q"); p.add_argument("c", type=int, nargs="*"); p.add_argument("dx", type=int)
    p.add_argument("--poli"); p.add_argument("--escala", type=float, default=1,
                                           help="encolhe/cresce o pedaço em volta do meio da base dele (mão no chão)")
    p.add_argument("dy", type=int); p.add_argument("--gira", type=float, default=0)
    p.add_argument("--espelha", action="store_true"); p.add_argument("--por-baixo", action="store_true")
    p = s("recolore", "q"); p.add_argument("--matiz", type=int, nargs=2, required=True,
                                           help="faixa de matiz em graus (0-360) dos pixels a trocar, ex.: 160 210 = verde-água")
    p.add_argument("--sat", type=float, default=0.25, help="saturação mínima (0-1) para entrar na troca")
    p.add_argument("--para", required=True, help="cores de destino (vírgula), 'pele' ou 'matiz:H0-H1' (cores vizinhas nessa faixa)")
    p.add_argument("--regiao", type=int, nargs=4)
    p = s("estica", "q"); p.add_argument("c", type=int, nargs=4); p.add_argument("para", type=int, nargs=2)
    p.add_argument("--empurra", action="store_true")
    p = s("escala", "q"); p.add_argument("f", type=float); p.add_argument("--pivo", default="eixo")
    p.add_argument("--suave", action="store_true")
    p.add_argument("--grade", type=int, help="tamanho do pixel do desenho (padrão: 3 no desenho grande do Hazak/CK/Pengaró)")
    p = s("quantiza", "q")
    p = sub.add_parser("desfaz"); p.add_argument("q", nargs="?")
    p = sub.add_parser("historico"); p.add_argument("n", nargs="?", type=int, default=15)
    p = s("sincroniza", "q")
    a = ap.parse_args(argv)

    if a.cmd == "desfaz":
        return desfaz(a.q)
    if a.cmd == "historico":
        for e in log()[-a.n:]:
            print(f"{e['quando']} {'(desfeito) ' if e.get('desfeito') else ''}{e['quadro']}: {' '.join(e['comando'])}")
        return
    if a.cmd == "mede":
        return mede(a.q, a.json, a.um_x)
    end = Endereco(a.q, a.um_x)
    if a.cmd == "ver":
        return ver(end, a.zoom, a.regiao, not a.sem_vegetal, a.saida)
    if a.cmd == "tira":
        return tira(end, a.saida)
    if a.cmd == "anima":
        return anima(end, a.saida, a.ms, a.zoom)
    if a.cmd == "compara":
        return compara(end, a.ref, a.saida)
    if a.cmd == "sincroniza":
        return sincroniza(end)
    pal = paleta(end)
    if a.cmd == "paleta":
        for i, (n, rgb) in enumerate(pal):
            print(f"#{i:<3} {n:22s} {'%02x%02x%02x' % rgb}")
        amostra = Image.new("RGB", (24 * min(len(pal), 32), 24 * ((len(pal) + 31) // 32)))
        for i, (_, rgb) in enumerate(pal):
            ImageDraw.Draw(amostra).rectangle([(i % 32) * 24, (i // 32) * 24, (i % 32) * 24 + 23,
                                               (i // 32) * 24 + 23], fill=rgb)
        amostra.save(CASA / "paleta.png")
        return
    comando = sys.argv[1:] if argv is None else list(argv)
    arr = abrir(end.arquivo)
    margem = 0
    if end.lutador in RECORTADOS:
        # o quadro recortado ganha folga para colar/mover/escalar para fora; as coordenadas do comando continuam as do
        # arquivo (a folga é descontada) e a tela volta a ser recortada ao gravar
        margem = int(max(arr.shape[:2]) * 0.6)
        arr = folga(arr, margem)
        for nome in ("c", "regiao"):
            if getattr(a, nome, None):
                setattr(a, nome, [v + margem for v in getattr(a, nome)])
        for nome in ("x", "y"):
            if isinstance(getattr(a, nome, None), int):
                setattr(a, nome, getattr(a, nome) + margem)
        if getattr(a, "pontos", None):
            a.pontos = [f"{xy(t)[0] + margem},{xy(t)[1] + margem}" for t in a.pontos]
        if getattr(a, "poli", None):
            a.poli = " ".join(f"{xy(t)[0] + margem},{xy(t)[1] + margem}" for t in a.poli.split())

    def selecao(caixa_ok=True):
        """Máscara do quadro todo: o polígono (--poli "x,y x,y ...") ou o retângulo, filtrada pelas cores de --so."""
        sel = np.zeros(arr.shape[:2], bool)
        if getattr(a, "poli", None):
            pts = np.array([xy(t) for t in a.poli.split()], np.int32)
            m = np.zeros(arr.shape[:2], np.uint8)
            cv2.fillPoly(m, [pts], 1)
            cv2.polylines(m, [pts], True, 1)
            sel = m.astype(bool)
        elif a.c:
            x0, y0, x1, y1 = a.c[:4]
            sel[y0:y1 + 1, x0:x1 + 1] = True
        else:
            sys.exit("diga a região: x0 y0 x1 y1 ou --poli \"x,y x,y ...\"")
        if getattr(a, "so", None):
            cores = np.zeros_like(sel)
            for t in a.so.split(","):
                cores |= (arr == np.array(cor(t, pal), np.uint8)).all(-1)
            sel &= cores
        return sel

    def caixa_de(sel):
        ys, xs = np.nonzero(sel)
        return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())

    def c_ok(t):
        c = cor(t, pal)
        if c[3] and c[:3] not in {rgb for _, rgb in pal}:
            sys.exit(f"a cor {t} não está na paleta de {end.lutador}{' ' + end.forma if end.forma else ''}: "
                     f"veja `pixel.py paleta {end.texto()}`")
        return np.array(c, np.uint8)

    if a.cmd == "pinta":
        tinta(arr, c_ok(a.cor), [xy(t) for t in a.pontos])
    elif a.cmd == "linha":
        c = c_ok(a.cor)
        for (x, y) in pontos_linha(*a.c):
            r = a.grossura // 2
            tinta(arr, c, [(x + i, y + j) for i in range(-r, a.grossura - r) for j in range(-r, a.grossura - r)])
    elif a.cmd == "ret":
        c = c_ok(a.cor)
        x0, y0, x1, y1 = a.c
        if a.vazio:
            for seg in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
                tinta(arr, c, pontos_linha(*seg))
        else:
            arr[y0:y1 + 1, x0:x1 + 1] = c
    elif a.cmd == "balde":
        balde(arr, a.x, a.y, c_ok(a.cor))
    elif a.cmd == "troca":
        de, para = np.array(cor(a.de, pal), np.uint8), c_ok(a.para)
        sel = (arr == de).all(-1)
        if a.regiao:
            x0, y0, x1, y1 = a.regiao
            caixa = np.zeros_like(sel)
            caixa[y0:y1 + 1, x0:x1 + 1] = True
            sel &= caixa
        arr[sel] = para
        print(f"{int(sel.sum())} pixels trocados")
    elif a.cmd == "apaga":
        sel = selecao()
        arr[sel] = 0
        print(f"{int(sel.sum())} pixels apagados")
    elif a.cmd == "remenda":
        # tapa os buracos (pixels vazios) da região com as cores de volta (inpaint) e leva para a paleta
        sel = selecao() & (arr[..., 3] == 0)
        rgb = np.ascontiguousarray(arr[..., :3])
        tapado = cv2.inpaint(rgb, sel.astype(np.uint8), a.raio, cv2.INPAINT_TELEA)
        novo = arr.copy()
        novo[sel, :3] = tapado[sel]
        novo[sel, 3] = 255
        q = mais_proxima(novo, pal)
        arr[sel] = q[sel]
        print(f"{int(sel.sum())} pixels remendados")
    elif a.cmd == "copia":
        sel = selecao()
        x0, y0, x1, y1 = caixa_de(sel)
        ped = arr[y0:y1 + 1, x0:x1 + 1].copy()
        ped[~sel[y0:y1 + 1, x0:x1 + 1]] = 0
        CASA.mkdir(parents=True, exist_ok=True)
        Image.fromarray(ped).save(PRANCHETA)
        caixa = [x0 - margem, y0 - margem, x1 - margem, y1 - margem]
        (CASA / "prancheta.json").write_text(json.dumps({"de": end.texto(), "caixa": caixa}), encoding="utf-8")
        print(f"prancheta: {ped.shape[1]}x{ped.shape[0]} de {end.texto()} {caixa}")
        return
    elif a.cmd == "cola":
        ped = np.array(Image.open(PRANCHETA).convert("RGBA"))
        if a.escala != 1:
            ped = cv2.resize(ped, (max(1, round(ped.shape[1] * a.escala)), max(1, round(ped.shape[0] * a.escala))),
                             interpolation=cv2.INTER_NEAREST)
        ped, (dx, dy) = girar(ped, a.gira, a.espelha)
        colar(arr, ped, a.x - dx, a.y - dy, a.por_baixo)
    elif a.cmd == "move":
        sel = selecao()
        x0, y0, x1, y1 = caixa_de(sel)
        ped = arr[y0:y1 + 1, x0:x1 + 1].copy()
        ped[~sel[y0:y1 + 1, x0:x1 + 1]] = 0
        arr[sel] = 0
        if a.escala != 1:
            h, w = ped.shape[:2]
            nw, nh = max(1, round(w * a.escala)), max(1, round(h * a.escala))
            grande = scale2x(scale2x(scale2x(ped))) if a.escala > 1 else ped
            ped = cv2.resize(grande, (nw, nh), interpolation=cv2.INTER_NEAREST)
            x0 += (w - nw) // 2
            y0 += h - nh
        ped, (dx, dy) = girar(ped, a.gira, a.espelha)
        colar(arr, ped, x0 + a.dx - dx, y0 + a.dy - dy, a.por_baixo)
    elif a.cmd == "recolore":
        # troca uma cor errada (ex.: a munhequeira verde-água do Hazak que sobrou no Diabo) por outra família de cores,
        # mantendo o claro/escuro: o pixel mais claro vai para a cor de destino mais clara
        hsv = cv2.cvtColor(np.ascontiguousarray(arr[..., :3]), cv2.COLOR_RGB2HSV)
        h, sat = hsv[..., 0].astype(int) * 2, hsv[..., 1] / 255
        sel = (arr[..., 3] > 0) & (h >= a.matiz[0]) & (h <= a.matiz[1]) & (sat >= a.sat)
        if a.regiao:
            x0, y0, x1, y1 = a.regiao
            caixa = np.zeros_like(sel)
            caixa[y0:y1 + 1, x0:x1 + 1] = True
            sel &= caixa
        if a.para == "pele" or a.para.startswith("matiz:"):
            # as cores vizinhas (até 8 px da mancha) na faixa pedida: 'pele' é a mão/o braço logo ao lado;
            # 'matiz:250-300' pega, por exemplo, o roxo do terno em volta
            h0, h1, smin, vmin = (10, 45, 0.35, 0.45) if a.para == "pele" else (
                *map(int, a.para[6:].split("-")), 0.15, 0.05)
            perto = cv2.dilate(sel.astype(np.uint8), np.ones((17, 17), np.uint8)).astype(bool) & ~sel
            v = hsv[..., 2] / 255
            mp = perto & (arr[..., 3] > 0) & (h >= h0) & (h <= h1) & (sat > smin) & (v > vmin)
            if mp.sum() < 10:
                sys.exit("não achei pele perto da mancha: passe --para COR,COR")
            cont = Counter(map(tuple, arr[mp][:, :3].tolist()))
            alvos = [np.array(c) for c, _ in cont.most_common(4)]
        else:
            alvos = [c_ok(t)[:3].astype(int) for t in a.para.split(",")]
        alvos.sort(key=lambda c: int(c.sum()))
        if sel.any():
            lum = arr[sel][:, :3].astype(int).sum(-1)
            ordem = np.argsort(np.argsort(lum, kind="stable"), kind="stable") / max(1, len(lum) - 1)
            # quantis do claro/escuro da cor errada viram as cores de destino na mesma ordem
            idx = np.minimum((ordem * len(alvos)).astype(int), len(alvos) - 1)
            novo = arr[sel].copy()
            novo[:, :3] = np.array(alvos)[idx]
            arr[sel] = novo
        print(f"{int(sel.sum())} pixels recoloridos")
    elif a.cmd == "estica":
        x0, y0, x1, y1 = a.c
        nx1, ny1 = a.para[0] + margem, a.para[1] + margem
        ped = arr[y0:y1 + 1, x0:x1 + 1].copy()
        w, h = nx1 - x0 + 1, ny1 - y0 + 1
        f = max(w / ped.shape[1], h / ped.shape[0])
        if f > 1:  # cresce pelo Scale2x para não fazer degrau
            ped = scale2x(scale2x(scale2x(ped)))
        ped = cv2.resize(ped, (w, h), interpolation=cv2.INTER_NEAREST)
        if a.empurra:  # o que estava à direita/abaixo do pedaço anda junto (ex.: o sapato depois da canela)
            dx, dy = nx1 - x1, ny1 - y1
            if dx:
                resto = arr[y0:y1 + 1, x1 + 1:].copy()
                arr[y0:y1 + 1, x1 + 1:] = 0
                colar(arr, resto[:, :max(0, arr.shape[1] - x1 - 1 - dx)], x1 + 1 + dx, y0)
            if dy:
                resto = arr[y1 + 1:, x0:x1 + 1].copy()
                arr[y1 + 1:, x0:x1 + 1] = 0
                colar(arr, resto[:max(0, arr.shape[0] - y1 - 1 - dy)], x0, y1 + 1 + dy)
        arr[y0:y0 + h, x0:x0 + w][ped[..., 3] > 0] = ped[ped[..., 3] > 0]
    elif a.cmd == "escala":
        if a.pivo == "pes" or (a.pivo == "eixo" and margem):
            pivo = pes(arr)
        elif a.pivo == "eixo":
            pivo = eixo(end)
        else:
            pivo = tuple(v + margem for v in xy(a.pivo))
        arr = escalar(arr, a.f, pivo, pal, a.suave, a.grade or end.fator)
    elif a.cmd == "quantiza":
        arr = mais_proxima(arr, pal)
    gravar(end, arr, comando)


def sincroniza(end):
    """1x a partir do 3x: cada bloco 3x3 vira a cor mais frequente dele (cheio se 5 dos 9 pixels estão pintados)."""
    assert end.fator == 3 and not end.um_x, "sincroniza vale para Hazak, CK e Pengaró, a partir do desenho 3x"
    peq = Endereco(f"{end.lutador}/{end.acao}", um_x=True)
    for p in end.quadros():
        g = abrir(p)
        h, w = g.shape[0] // 3, g.shape[1] // 3
        blocos = g[:h * 3, :w * 3].reshape(h, 3, w, 3, 4).transpose(0, 2, 1, 3, 4).reshape(h, w, 9, 4)
        out = np.zeros((h, w, 4), np.uint8)
        cheio = (blocos[..., 3] > 0).sum(-1) >= 5
        for yy, xx in zip(*np.nonzero(cheio)):
            b = blocos[yy, xx]
            b = b[b[:, 3] > 0]
            out[yy, xx] = Counter(map(tuple, b.tolist())).most_common(1)[0][0]
        e1 = Endereco(f"{peq.lutador}/{peq.acao}/{int(p.stem)}", um_x=True)
        gravar(e1, out, ["sincroniza", end.texto()])


if __name__ == "__main__":
    main()
