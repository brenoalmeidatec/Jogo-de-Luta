"""Onde ficam os desenhos de cada lutador, qual é a pose parada de cada forma e qual é a paleta.

Um quadro é endereçado como LUTADOR/ACAO/NN, por exemplo `hazaki/agachado/03`, `diabo/d_rasteira_arco/04`,
`ck/e_soco/02`. O padrão é o desenho grande (3x) que o jogo usa; `--1x` troca para o desenho pequeno quando ele existe.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
SPRITES = RAIZ / "sprites"

# lutador -> (pasta do desenho grande, pasta do 1x ou None, fator entre os dois)
PASTAS = {
    "hazaki": ("hazaki/quadros_arcade_hd", "hazaki/quadros_arcade", 3),
    "diabo": ("hazaki/diabo_terno", None, 1),
    "ck": ("ck/quadros_arcade_hd", "ck/quadros_arcade", 3),
    "pengaro": ("pengaro/quadros_arcade_hd", "pengaro/quadros_arcade", 3),
    "gutto": ("gutto/quadros", None, 1),
    "raiclaven": ("raiclaven/quadros", None, 1),
}
# pose parada de cada forma: (lutador, prefixo da ação) -> ação de referência
PARADO = {
    ("hazaki", ""): "parado",
    ("diabo", ""): "d_parado",
    ("ck", ""): "referencia_ginga", ("ck", "e_"): "e_referencia_ginga",
    ("pengaro", ""): "ginga", ("pengaro", "e_"): "e_ginga",
    ("gutto", ""): "ginga", ("gutto", "e_"): "ginga_endiabrada",
    ("raiclaven", ""): "ginga",
}
PALETA_JSON = {
    ("hazaki", ""): "hazaki/paleta_nitida.json",  # forma base nítida (#36, 40 cores)
    ("diabo", ""): "hazaki/diabo_terno/paleta.json",  # paleta única do Diabo (#51, cor entre os quadros)
    ("ck", ""): "ck/paleta_arcade.json", ("ck", "e_"): "ck/paleta_arcade_ratao.json",
    ("pengaro", ""): "pengaro/paleta_arcade.json", ("pengaro", "e_"): "pengaro/paleta_arcade_endiabrado.json",
}


class Endereco:
    def __init__(self, texto, um_x=False):
        partes = texto.strip("/").split("/")
        assert len(partes) in (2, 3), f"endereço '{texto}': use LUTADOR/ACAO ou LUTADOR/ACAO/NN"
        self.lutador, self.acao = partes[0], partes[1]
        self.n = int(partes[2]) if len(partes) == 3 else None
        assert self.lutador in PASTAS, f"lutador '{self.lutador}': use um de {', '.join(PASTAS)}"
        grande, pequeno, self.fator = PASTAS[self.lutador]
        if um_x:
            assert pequeno, f"{self.lutador} não tem desenho 1x separado"
            self.pasta = SPRITES / pequeno / self.acao
            self.fator = 1
        else:
            self.pasta = SPRITES / grande / self.acao
        self.um_x = um_x

    @property
    def forma(self):
        if PARADO.get((self.lutador, "e_")) == self.acao:  # gutto/ginga_endiabrada é o parado da forma e_
            return "e_"
        return "e_" if self.acao.startswith("e_") and self.lutador != "diabo" else ""

    @property
    def arquivo(self):
        assert self.n is not None, "falta o número do quadro (LUTADOR/ACAO/NN)"
        return self.pasta / f"{self.n:02d}.png"

    def quadros(self):
        return sorted(p for p in self.pasta.glob("[0-9][0-9].png"))

    def vizinho(self, passo):
        qs = self.quadros()
        nomes = [int(p.stem) for p in qs]
        if self.n not in nomes:
            return None
        i = (nomes.index(self.n) + passo) % len(nomes)
        return qs[i]

    def parado(self):
        acao = PARADO.get((self.lutador, self.forma)) or PARADO[(self.lutador, "")]
        e = Endereco(f"{self.lutador}/{acao}/0", self.um_x)
        return e

    def texto(self):
        return f"{self.lutador}/{self.acao}" + (f"/{self.n:02d}" if self.n is not None else "")

    def relativo(self):
        return self.arquivo.relative_to(RAIZ).as_posix()


def abrir(caminho):
    return np.array(Image.open(caminho).convert("RGBA"))


def salvar(arr, caminho):
    arr = arr.copy()
    arr[arr[..., 3] < 128] = 0
    arr[..., 3] = np.where(arr[..., 3] >= 128, 255, 0)
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr.astype(np.uint8)).save(caminho, optimize=True)


def paleta(end):
    """[(nome, (r, g, b))] da forma: o .json da paleta quando existe; senão as cores do parado e do próprio quadro
    (o Diabo e o Gutto/Raiclaven não têm .json), em ordem de uso."""
    js = PALETA_JSON.get((end.lutador, end.forma))
    if js and (SPRITES / js).exists():
        dados = json.loads((SPRITES / js).read_text(encoding="utf-8"))
        cores = [(c["id"], tuple(c["rgb"])) for c in dados["cores"]]
        # o desenho 3x pode ter as mesmas cores; se tiver outras, entram também (com nome cN)
        extra = _cores_usadas(end, limite=64)
        conhecidas = {rgb for _, rgb in cores}
        cores += [(f"c{i}", rgb) for i, rgb in enumerate(extra) if rgb not in conhecidas]
        return cores
    return [(f"c{i}", rgb) for i, rgb in enumerate(_cores_usadas(end, limite=256))]


def _cores_usadas(end, limite):
    from collections import Counter
    cont = Counter()
    fontes = end.parado().quadros()[:8]
    if end.n is not None and end.arquivo.exists():
        fontes = fontes + [end.arquivo]
    for p in fontes:
        a = abrir(p)
        px = a[a[..., 3] > 0][:, :3]
        cont.update(map(tuple, px.tolist()))
    return [tuple(int(v) for v in c) for c, _ in cont.most_common(limite)]


def cor(texto, pal):
    """'transparente', nome da paleta, índice (#3) ou hex (ff8800) -> RGBA."""
    if texto in ("transparente", "apaga", "nada"):
        return (0, 0, 0, 0)
    nomes = dict(pal)
    if texto in nomes:
        return (*nomes[texto], 255)
    if texto.startswith("#") and texto[1:].isdigit():
        return (*pal[int(texto[1:])][1], 255)
    h = texto.lstrip("#")
    assert len(h) == 6, f"cor '{texto}': use nome da paleta, #índice ou hex rrggbb"
    rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (*rgb, 255)
