#!/usr/bin/env python3
"""Diabo Loiro na roupa do conceito aprovado (issue #44, resposta do Breno em 2026-11-14).

A forma despertada do Hazak deixa o gi e veste o que está em `d_conceito.png`: sobretudo roxo-escuro com forro laranja,
terno risca de giz, colete com corrente de ouro, gravata laranja, chapéu de aba larga com os chifres, cabelo loiro
comprido, rabo e olhos vermelhos. As folhas `d_*` dessa roupa (8 quadros cada) estão na branch `bosses`, em
sprites/hazaki/quadros/folhas_arcade/. Cada uma foi desenhada em cima de uma folha do Hazak normal (a "base de
referência" de docs/arcade/fila_bosses.md), com os mesmos tempos. Aqui cada quadro do Hazak ganha o quadro de mesmo
número da folha `d_*` correspondente (tabela FOLHA); folha do Hazak sem `d_*` própria usa a mais parecida.

  python3 ferramentas/diabo_terno.py --montar [pasta com as folhas d_*.png]
      recorta as figuras das folhas (por padrão lê da branch origin/bosses pelo git), põe na escala do corpo 3x,
      aplica o acabamento de chefão e grava sprites/hazaki/diabo_terno/<folha>/NN.png (é o que fica no repositório)
  python3 ferramentas/diabo_terno.py --contato saida.png
      folha de conferência: Hazak e Diabo lado a lado, alinhados como entram no jogo

Quem usa: ferramentas/diabo_loiro.py (`Terno().diabo(mascara, eixo)`), chamado no fim do gerar_hazaki.py. Os golpes, as
caixas e os tempos são os do Hazak: só o desenho muda. Nenhum quadro da forma fica no gi.

Acabamento de chefão (pedido do Breno: "ainda mais poderosa, de Diabo Loiro de verdade"): forro e gravata em brasa,
ouro mais vivo, sombra mais funda no roxo, olho vermelho aceso e a luz do fogo do chão subindo pela barra do sobretudo.
"""
import io
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "ferramentas"))
import hd_guiado  # noqa: E402
from folhas_hazak_arcade import ESCALA, FATOR  # noqa: E402

HD = 3
SPRITES = RAIZ / "sprites/hazaki"
QUADROS_HD = SPRITES / "quadros_arcade_hd"
SAIDA = SPRITES / "diabo_terno"
RAMO = "origin/bosses"
PASTA_NO_RAMO = "sprites/hazaki/quadros/folhas_arcade"
CORES = 48  # cores por quadro depois do acabamento (o corpo normal tem 15; o terno precisa de mais para a risca e o ouro)

# folha do Hazak -> folha do Diabo. Em cima: a base de referência declarada na fila (mesmo golpe, mesmos tempos).
FOLHA = {
    "parado": "d_parado", "anda": "d_anda", "vira": "d_vira", "corrida": "d_corrida", "recuo": "d_recuo",
    "pulo": "d_pulo", "agachado": "d_agachado", "defesa": "d_defesa", "defesa_baixa": "d_defesa_baixa",
    "apanha": "d_apanha", "queda": "d_queda", "levanta": "d_levanta", "vitoria": "d_vitoria",
    "soco": "d_tapa_anel", "soco_reto": "d_maletada_lado", "cruzado": "d_maletada_volta",
    "cotovelada": "d_maletada_cima", "calcada_levantada": "d_negocio_fechado", "chute_baixo": "d_chute_baixo",
    "chute": "d_sapato_barriga", "chute_giratorio": "d_coice_costas", "machado": "d_pisao_chefe",
    "joelhada_baixo": "d_maleta_sobe", "machado_curto": "d_chapelada", "cutucao_recuo": "d_dedo",
    "chute_canela": "d_bico_sapato", "chute_lateral": "d_chute_lateral", "baixo_soco": "d_baixo_soco",
    "rasteira_arco": "d_rasteira_arco", "cotovelo_faixa": "d_cotovelo_faixa", "coice": "d_coice",
    "ar_soco": "d_ar_soco", "ar_cotovelo": "d_ar_cotovelo", "ar_joelho": "d_ar_joelho",
    "ar_chute_duplo": "d_pisao_ar", "giro_garagem": "d_maleta_giro", "punho_chao": "d_punho_anel",
    "voadora": "d_voadora_sapato", "rolada_tatame": "d_fumaca", "pose_super": "d_chuva_abre",
    "estatueta_arremesso": "d_chapeu_arremesso", "agarrao_abraco": "d_agarrao_abraco",
    "agarrao_perna": "d_agarrao_perna", "agarrao_cutucao": "d_agarrao_cutucao",
    # sem folha própria no terno: a mais parecida (o golpe e a caixa continuam os do Hazak)
    "ar_chute": "d_ar_joelho", "ascensao": "d_maleta_sobe", "chute_alto_rajada": "d_chute_lateral",
    "chute_gancho": "d_sapato_barriga", "cutucao": "d_tapa_anel", "jab_duplo": "d_tapa_anel",
    "guarda_aco": "d_defesa", "passagem_rapida": "d_corrida", "provoca": "d_dedo", "rasteira": "d_rasteira_arco",
    "sobe_chutando": "d_pisao_chefe", "tapa_costas": "d_tapa_anel", "tesoura": "d_voadora_sapato",
    "derrota_sirene": "d_queda", "intro": "d_vitoria", "despertar_pedido": "d_parado",
    "parry_alto": "d_defesa", "parry_baixo": "d_defesa_baixa",
    "vitima_agarrado": "d_apanha", "vitima_arremessado": "d_queda",
}
PARECIDA = {"ar_chute", "ascensao", "chute_alto_rajada", "chute_gancho", "cutucao", "jab_duplo", "guarda_aco",
            "passagem_rapida", "provoca", "rasteira", "sobe_chutando", "tapa_costas", "tesoura", "derrota_sirene",
            "intro", "despertar_pedido", "parry_alto", "parry_baixo", "vitima_agarrado", "vitima_arremessado"}


# ---------------------------------------------------------------------------------------------------------------------
# acabamento de chefão
# ---------------------------------------------------------------------------------------------------------------------
def chefao(fig):
    """`fig` RGBA (uint8) -> RGBA com forro em brasa, ouro vivo, sombra funda, olho aceso e luz de fogo vinda do chão."""
    a = fig.astype(np.float32)
    rgb, alfa = a[..., :3], a[..., 3] > 0
    hsv = cv2.cvtColor(fig[..., :3], cv2.COLOR_RGB2HSV).astype(np.float32)  # H 0..180
    h, s, v = hsv[..., 0], hsv[..., 1] / 255, hsv[..., 2] / 255
    alt = fig.shape[0]
    y = np.linspace(0, 1, alt, dtype=np.float32)[:, None] * np.ones((1, fig.shape[1]), np.float32)

    # roxo do sobretudo e do terno: sombra mais funda, com mais contraste (o claro continua claro)
    roxo = alfa & (h > 118) & (h < 160) & (s > 0.12)
    f = np.clip((v - 0.10) / 0.5, 0, 1)
    escala = 0.62 + 0.42 * f
    rgb[roxo] *= escala[roxo][:, None]
    rgb[roxo] += np.array([6, 0, 10], np.float32) * f[roxo][:, None]

    # forro, gravata e fita do chapéu (laranja vivo): viram brasa, do vermelho escuro ao amarelo quente
    brasa = alfa & (h >= 5) & (h <= 21) & (s > 0.72) & (v > 0.45)
    t = np.clip((v - 0.45) / 0.5, 0, 1)[brasa][:, None]
    quente = np.array([255, 176, 44], np.float32)
    meio = np.array([236, 92, 12], np.float32)
    frio = np.array([128, 22, 8], np.float32)
    rgb[brasa] = np.where(t < 0.5, frio + (meio - frio) * (t * 2), meio + (quente - meio) * (t * 2 - 1))

    # ouro (corrente, botões, anel, fivelas): mais vivo; o cabelo loiro é menos saturado e fica como está
    ouro = alfa & (h >= 20) & (h <= 30) & (s > 0.68) & (v > 0.55) & ~brasa
    rgb[ouro] = rgb[ouro] * np.array([1.06, 1.04, 0.72], np.float32) + np.array([14, 8, 0], np.float32)

    # olho vermelho aceso: vermelho puro e pequeno na cabeça (quarto de cima da figura)
    olho = alfa & ((h < 6) | (h > 172)) & (s > 0.7) & (v > 0.55) & (y < 0.3)
    n, rot, info, _ = cv2.connectedComponentsWithStats(olho.astype(np.uint8), connectivity=8)
    aceso = np.zeros_like(olho)
    for j in range(1, n):
        if info[j, cv2.CC_STAT_AREA] <= 90:
            aceso |= rot == j
    if aceso.any():
        halo = cv2.dilate(aceso.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & alfa & ~aceso
        rgb[halo] = rgb[halo] * 0.45 + np.array([150, 14, 10], np.float32)
        rgb[aceso] = np.array([255, 70, 40], np.float32)

    # luz do fogo do chão: a barra do sobretudo, a calça e o sapato pegam um laranja que some até a cintura
    luz = np.clip((y - 0.62) / 0.38, 0, 1) ** 1.6
    pega = alfa & ~brasa
    rgb[pega] += (np.array([120, 46, 0], np.float32) * (luz * (0.35 + 0.65 * v))[..., None])[pega]

    out = fig.copy()
    out[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    return out


def quantizar(fig):
    """Reduz a figura a CORES cores sem pontilhado (cara de sprite, e o PNG fica pequeno no .sff)."""
    alfa = fig[..., 3] >= 128
    if not alfa.any():
        return fig
    px = fig[..., :3][alfa].astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 12, 1.0)
    cv2.setRNGSeed(7)
    _, rot, centros = cv2.kmeans(px, CORES, None, crit, 1, cv2.KMEANS_PP_CENTERS)
    out = np.zeros_like(fig)
    out[..., :3][alfa] = np.clip(centros[rot.ravel()], 0, 255).astype(np.uint8)
    out[..., 3][alfa] = 255
    return out


# ---------------------------------------------------------------------------------------------------------------------
# montar: folhas d_* -> sprites/hazaki/diabo_terno/<folha>/NN.png
# ---------------------------------------------------------------------------------------------------------------------
def abrir_folha(nome, pasta):
    if pasta:
        return Image.open(Path(pasta) / f"{nome}.png").convert("RGBA")
    dados = subprocess.run(["git", "-C", str(RAIZ), "show", f"{RAMO}:{PASTA_NO_RAMO}/{nome}.png"], check=True,
                           capture_output=True).stdout
    return Image.open(io.BytesIO(dados)).convert("RGBA")


def fator_da_folha(folha_d):
    """O mesmo aumento que a folha base do Hazak leva no conversor (deitado e voando a figura vem menor na folha)."""
    for base, d in FOLHA.items():
        if d == folha_d and base in FATOR and base not in PARECIDA:
            f = FATOR[base]
            return list(f) if isinstance(f, (list, tuple)) else [f] * 8
    return [1.0] * 8


def montar(pasta=None):
    for folha_d in sorted(set(FOLHA.values())):
        figs = hd_guiado.figuras(abrir_folha(folha_d, pasta))
        assert len(figs) == 8, f"{folha_d}: {len(figs)} figuras (esperava 8)"
        fat = fator_da_folha(folha_d)
        destino = SAIDA / folha_d
        destino.mkdir(parents=True, exist_ok=True)
        for k, fig in enumerate(figs):
            e = ESCALA * HD * fat[k]
            w, h = max(1, round(fig.shape[1] * e)), max(1, round(fig.shape[0] * e))
            # alfa pré-multiplicado na redução, para a borda não puxar o preto do fundo apagado
            pre = fig.astype(np.float32)
            pre[..., :3] *= pre[..., 3:4] / 255
            red = cv2.resize(pre, (w, h), interpolation=cv2.INTER_AREA)
            al = red[..., 3:4]
            red[..., :3] = np.where(al > 0, red[..., :3] * 255 / np.maximum(al, 1), 0)
            red = np.clip(red, 0, 255).astype(np.uint8)
            red[..., 3] = np.where(red[..., 3] >= 128, 255, 0)
            red[red[..., 3] == 0] = 0
            Image.fromarray(quantizar(chefao(red))).save(destino / f"{k:02d}.png", optimize=True)
        print(f"{folha_d}: 8 quadros", flush=True)


# ---------------------------------------------------------------------------------------------------------------------
# casar cada desenho do Hazak com o quadro do terno e alinhar
# ---------------------------------------------------------------------------------------------------------------------
def recorte(m):
    ys, xs = np.nonzero(m)
    return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1], int(xs.min()), int(ys.min())


def ancora(m):
    """(x, y) de apoio de uma máscara recortada: y é a base; x é o meio dos pés se a figura está de pé, senão a
    mediana das colunas (aguenta membro esticado, rabo e aba de chapéu sem puxar o corpo)."""
    h, w = m.shape
    if h >= 1.15 * w:
        pe = m[int(h * 0.88):]
        xs = np.nonzero(pe)[1]
        return float(xs.mean()), h - 1
    xs = np.nonzero(m)[1]
    return float(np.median(xs)), h - 1


class Terno:
    def __init__(self):
        assert SAIDA.exists(), f"faltam os quadros do terno em {SAIDA}: rode ferramentas/diabo_terno.py --montar"
        self.indice = {}
        for p in sorted(QUADROS_HD.glob("*/*.png")):
            m = np.array(Image.open(p).convert("RGBA"))[..., 3] > 0
            if m.any():
                self.indice.setdefault(recorte(m)[0].shape, []).append((p.parent.name, int(p.stem), recorte(m)[0]))
        self.cache = {}

    def casar(self, m):
        """(folha, quadro, espelhado) do quadro HD do Hazak que deu a máscara `m` (recortada)."""
        melhor = None
        for dh in (-2, -1, 0, 1, 2):
            for dw in (-2, -1, 0, 1, 2):
                for folha, k, mm in self.indice.get((m.shape[0] + dh, m.shape[1] + dw), []):
                    h, w = min(m.shape[0], mm.shape[0]), min(m.shape[1], mm.shape[1])
                    for esp in (False, True):
                        b = (mm[:, ::-1] if esp else mm)[:h, :w]
                        a = m[:h, :w]
                        iou = (a & b).sum() / max(1, (a | b).sum())
                        if melhor is None or iou > melhor[0]:
                            melhor = (iou, folha, k, esp)
        return melhor[1:] if melhor and melhor[0] > 0.9 else None

    def figura(self, folha_d, k):
        if (folha_d, k) not in self.cache:
            self.cache[(folha_d, k)] = np.array(Image.open(SAIDA / folha_d / f"{k:02d}.png").convert("RGBA"))
        return self.cache[(folha_d, k)]

    def diabo(self, mascara, eixo):
        """`mascara`: bool do desenho do Hazak no sprite; `eixo`: (x, y) dele. -> (RGBA do Diabo, (eixo x, eixo y))."""
        m, x0, y0 = recorte(mascara)
        par = self.casar(m)
        if par is None:
            return None  # não é desenho do corpo (objeto, efeito): quem chama decide
        folha, k, esp = par
        fig = self.figura(FOLHA[folha], k)
        if esp:
            fig = fig[:, ::-1]
            m = m[:, ::-1]
        ax, ay = ancora(m)
        if esp:
            ax = m.shape[1] - 1 - ax
        dx, dy = ancora(fig[..., 3] > 0)
        if esp:
            pass  # a figura já está espelhada: a âncora dela foi medida espelhada
        # eixo do Hazak em relação à âncora dele; o Diabo põe a âncora dele no mesmo lugar
        ex = dx - ((x0 + ax) - eixo[0])
        ey = dy - ((y0 + ay) - eixo[1])
        return Image.fromarray(np.ascontiguousarray(fig)), (round(ex), round(ey))


def contato(saida):
    sys.path.insert(0, str(RAIZ / "ferramentas"))
    t = Terno()
    folhas = sorted(p.name for p in QUADROS_HD.iterdir() if p.name in FOLHA)
    cw, ch = 300, 260
    tela = Image.new("RGB", (cw * 8, ch * len(folhas)), (40, 60, 200))
    for j, folha in enumerate(folhas):
        for k in range(8):
            p = QUADROS_HD / folha / f"{k:02d}.png"
            if not p.exists():
                continue
            base = Image.open(p).convert("RGBA")
            m = np.array(base)[..., 3] > 0
            if not m.any():
                continue
            img, (ex, ey) = t.diabo(m, (540, 660))
            cel = Image.new("RGBA", (1080, 780), (0, 0, 0, 0))
            fantasma = base.copy()
            fantasma.putalpha(fantasma.getchannel("A").point(lambda v: 70 if v else 0))
            cel.alpha_composite(fantasma)
            cel.alpha_composite(img, (max(0, 540 - ex), max(0, 660 - ey)))
            cel = cel.crop((240, 160, 240 + 600, 160 + 520)).resize((cw, ch), Image.LANCZOS)
            tela.paste(cel, (k * cw, j * ch), cel)
    tela.save(saida)
    print(saida)


if __name__ == "__main__":
    if "--montar" in sys.argv:
        resto = [a for a in sys.argv[1:] if not a.startswith("--")]
        montar(resto[0] if resto else None)
    elif "--contato" in sys.argv:
        contato(sys.argv[sys.argv.index("--contato") + 1])
    else:
        print(__doc__)
