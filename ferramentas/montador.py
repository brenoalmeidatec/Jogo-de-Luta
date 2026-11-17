#!/usr/bin/env python3
"""Montador do boneco de peças: página no navegador para montar as poses-chave de um golpe com as peças do kit.

  python ferramentas/montador.py                  Pengaró (kit em sprites/pengaro/pecas)
  python ferramentas/montador.py --lutador gbzin  Gbzin (kit em sprites/gbzin/pecas)
  python ferramentas/montador.py --lutador gutto  Gutto (kit em sprites/gutto/pecas)
  opções: --porta 8765   --sem-navegador

Abre http://127.0.0.1:8765 no navegador. Cada quadro é desenhado aqui no Python, com o MESMO código do piloto
(piloto_firme.desenhar para o Pengaró, gbzin_pecas.desenhar para o Gbzin): RotSprite em cor cheia, sobra nas juntas,
pés retos no chão. Então o que aparece na página é exatamente o que vai para a pasta.

A pose tem o formato do poses.json do piloto: {osso: {"ang": graus, "dx": px, "dy": px, "var": variante}}, ângulo e
deslocamento relativos à peça mãe, em pixels do 3x (tela 1080x780, pés em 540,660).

Gravar não mexe no jogo: os quadros vão para sprites/<lutador>/quadros_montador_hd/<nome>/ (3x) e
sprites/<lutador>/quadros_montador/<nome>/ (1x), com poses.json e tempos.json no formato do piloto, e o projeto
editável fica em sprites/<lutador>/montador/<nome>.json. Ligar no gerador continua sendo trabalho do Alisson.
"""
import argparse
import base64
import io
import json
import re
import shutil
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np
from PIL import Image

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
PAGINA = AQUI / "montador"
sys.path.insert(0, str(AQUI))


class Lutador:
    """Liga o montador no código de desenho do lutador."""

    def __init__(self, nome):
        self.nome = nome
        import boneco_ajuste as b
        import piloto_firme as pf
        self.b = b
        self.modulos = [b]  # módulos cujo CAMADAS o desenho lê (trocado por pose para esconder ou mandar para trás)
        if nome == "gbzin":
            import gbzin_pecas as g
            self.kit = g.ler_kit()  # já chama configurar()
            self.modulos.append(g)
            self._desenhar = g.desenhar
            self.ossos, self.camadas = g.OSSOS, g.CAMADAS
            self.guarda = "referencia_ginga/00"
        elif nome == "gutto":
            import boneco_gutto as g
            g.configurar()
            pfg = g.configurar_piloto()
            self.kit = g.separar_pes(b.ler_kit())
            def desenhar_gutto(kit, pose):
                # pose agachada lê o desenho de hoje direto do .sff (quadros_sff_hd não fica no git): extrai e tenta de novo
                for _ in range(4):
                    try:
                        return g.desenhar(pfg, kit, pose)
                    except FileNotFoundError as e:
                        g.garantir_hd([Path(e.filename).stem])
                return g.desenhar(pfg, kit, pose)
            self._desenhar = desenhar_gutto
            self.ossos, self.camadas = g.OSSOS, g.CAMADAS
            self.guarda = g.REF
        elif nome == "pengaro":
            self.kit = pf.separar_pes(b.ler_kit())
            self._desenhar = pf.desenhar
            self.ossos, self.camadas = b.OSSOS, b.CAMADAS
            self.guarda = "ginga/00"
        else:
            raise SystemExit(f"lutador sem kit no montador: {nome} (tem: pengaro, gbzin, gutto)")
        self.spr = RAIZ / "sprites" / nome
        self.trava = threading.Lock()  # o código do piloto usa variáveis globais; um desenho por vez
        self.cache = {}

    def info(self):
        variantes = {s: [] for s in self.ossos}
        for chave in self.kit["pecas"]:
            for s in self.ossos:
                if chave.startswith(s + "_") and chave != s:
                    variantes[s].append(chave[len(s) + 1:])
        return {
            "lutador": self.nome,
            "tela": list(self.b.TELA),
            "eixo": [540, 660],
            "ossos": {s: {"junta": list(j), "mae": m, "ponta": list(p)} for s, (j, m, p) in self.ossos.items()},
            "camadas": list(self.camadas),
            "variantes": variantes,
            "pecas": {k: {"origem": list(p["origem"]), "junta": list(p["junta"]),
                          "tam": [int(p["img"].shape[1]), int(p["img"].shape[0])]}
                      for k, p in self.kit["pecas"].items()},
        }

    def desenhar(self, pose):
        chave = json.dumps(pose, sort_keys=True)
        if chave in self.cache:
            return self.cache[chave]
        pose = limpar_pose(pose)
        kit, camadas = self.preparar(pose)
        with self.trava:
            antes = [m.CAMADAS for m in self.modulos]
            try:
                for m in self.modulos:
                    m.CAMADAS = camadas
                out = self._desenhar(kit, pose)
            finally:
                for m, c in zip(self.modulos, antes):
                    m.CAMADAS = c
        if len(self.cache) > 400:
            self.cache.clear()
        self.cache[chave] = out
        return out

    def preparar(self, pose):
        """Kit e ordem de camadas desta pose: peça pintada ou apagada à mão ("ret"), peça escondida ("esconde") e
        peça mandada para trás do corpo ou para a frente de tudo ("camada")."""
        kit = self.kit
        camadas = list(self.camadas)

        def copia():
            nonlocal kit
            if kit is self.kit:
                kit = dict(self.kit)
                kit["pecas"] = dict(self.kit["pecas"])
                if "pes" in self.kit:
                    kit["pes"] = dict(self.kit["pes"])
            return kit

        for slot, v in pose.items():
            if slot not in self.ossos:
                continue
            ret = v.get("ret")
            if ret and ret.get("var", "") == (v.get("var") or ""):
                k = f"{slot}_{v['var']}" if v.get("var") else slot
                p = copia()["pecas"][k]
                kit["pecas"][k] = dict(p, img=aplicar_retoque(p["img"], ret["png"]))
            if v.get("esconde"):
                if slot in camadas:
                    camadas.remove(slot)
                if "pes" in kit and slot in kit["pes"]:  # o pé é desenhado à parte, preso na canela
                    pe = copia()["pes"][slot]
                    kit["pes"][slot] = dict(pe, img=np.zeros_like(pe["img"]))
        for slot, v in pose.items():
            lugar = v.get("camada") if isinstance(v, dict) else None
            if slot not in camadas or lugar not in ("atras", "frente"):
                continue
            camadas.remove(slot)
            if lugar == "frente":
                camadas.append(slot)
            else:  # atrás do corpo: logo antes do tronco (e da cabeça, que fica por baixo do tronco)
                i = min([camadas.index(c) for c in ("cabeca", "tronco") if c in camadas] or [0])
                camadas.insert(i, slot)
        return kit, camadas

    def png(self, pose, escala=3):
        out = self.desenhar(pose)
        if escala == 1:
            out = np.ascontiguousarray(out[1::3, 1::3])  # o mesmo 1x do piloto
        buf = io.BytesIO()
        Image.fromarray(out).save(buf, "PNG", compress_level=1)
        return buf.getvalue()

    # ---------------------------------------------------------------- golpes do piloto (ponto de partida)
    def golpes_do_piloto(self):
        """As animações que o piloto já montou: poses-chave do poses.json com os ticks de hoje."""
        arq = self.spr / "quadros_pecas_hd" / "poses.json"
        if not arq.exists():
            return {}
        poses = json.loads(arq.read_text(encoding="utf-8"))
        golpes = {}
        for pasta in sorted((self.spr / "quadros_pecas_hd").iterdir()):
            t = pasta / "tempos.json"
            if not t.exists():
                continue
            tempos = json.loads(t.read_text(encoding="utf-8"))
            # junta os elementos que vêm do mesmo desenho de hoje: cada um vira uma pose-chave com a soma dos ticks
            quadros = []
            for e in tempos["elementos"]:
                q = e.get("de")
                if quadros and quadros[-1]["de"] == q:
                    quadros[-1]["ticks"] += e["ticks"]
                    quadros[-1]["caixa"] = quadros[-1]["caixa"] or e["caixa"]
                else:
                    quadros.append({"de": q, "ticks": e["ticks"], "caixa": e["caixa"],
                                    "pose": poses.get(q, {})})
            golpes[pasta.name] = {"nome": pasta.name, "acao": tempos.get("acao"), "caixa": tempos.get("caixa"),
                                  "laco": pasta.name == "parado", "quadros": quadros}
        return golpes

    # ---------------------------------------------------------------- projetos
    def pasta_projetos(self):
        p = self.spr / "montador"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def projetos(self):
        return sorted(a.stem for a in self.pasta_projetos().glob("*.json"))

    def abrir(self, nome):
        return json.loads((self.pasta_projetos() / f"{nome_seguro(nome)}.json").read_text(encoding="utf-8"))

    def gravar(self, proj):
        nome = nome_seguro(proj["nome"])
        proj["nome"] = nome
        (self.pasta_projetos() / f"{nome}.json").write_text(json.dumps(proj, indent=1, ensure_ascii=False),
                                                            encoding="utf-8")
        quadros = proj["quadros"]
        if not quadros:
            return {"nome": nome, "desenhos": 0}
        if proj.get("vida"):
            lista = self._com_vida(proj)
        else:
            lista = [(q["pose"], int(q["ticks"]), bool(q.get("caixa")), f"pose{i:02d}") for i, q in enumerate(quadros)]
        hd, x1 = self.spr / "quadros_montador_hd" / nome, self.spr / "quadros_montador" / nome
        for p in (hd, x1):
            shutil.rmtree(p, ignore_errors=True)
            p.mkdir(parents=True)
        for i, (pose, _, _, _) in enumerate(lista):
            out = self.desenhar(pose)
            Image.fromarray(out).save(hd / f"{i:02d}.png")
            Image.fromarray(np.ascontiguousarray(out[1::3, 1::3])).save(x1 / f"{i:02d}.png")
        tempos = {"acao": proj.get("acao"), "caixa": proj.get("caixa"), "origem": "montador",
                  "elementos": [{"desenho": i, "ticks": t, "caixa": c, "de": q}
                                for i, (_, t, c, q) in enumerate(lista)]}
        poses = {f"pose{i:02d}": limpar_pose(q["pose"]) for i, q in enumerate(quadros)}
        for p in (hd, x1):
            (p / "tempos.json").write_text(json.dumps(tempos, indent=1, ensure_ascii=False), encoding="utf-8")
            (p / "poses.json").write_text(json.dumps(poses, indent=1), encoding="utf-8")
        return {"nome": nome, "desenhos": len(lista), "ticks": sum(t for _, t, _, _ in lista),
                "pasta": str(hd.relative_to(RAIZ)), "pasta_1x": str(x1.relative_to(RAIZ))}

    def _com_vida(self, proj):
        """Intermediários, impacto segurado e atraso da cabeça (vida_pecas.py, o mesmo do piloto)."""
        import vida_pecas as vida
        quadros = proj["quadros"]
        poses = {f"pose{i:02d}": limpar_pose(q["pose"]) for i, q in enumerate(quadros)}
        elems = [(f"pose{i:02d}", int(q["ticks"])) for i, q in enumerate(quadros)]
        bate = next((i for i, q in enumerate(quadros) if q.get("caixa")), None)
        laco = bool(proj.get("laco"))
        # o golpe volta para a guarda (a pose vazia, o parado do kit), como no piloto
        lista = vida.animar(poses, elems, bate=bate, laco=laco, guarda={})
        if laco:
            lista = vida.respirar(lista)
        return vida.atrasar(lista, laco=laco)


def limpar_pose(pose):
    """Só o que o código de desenho entende (tira o "custo" do encaixe do piloto e os zeros)."""
    out = {}
    for osso, v in pose.items():
        if not isinstance(v, dict):
            continue
        if osso.startswith("_"):  # extras do piloto (_bolinhas, _baixo) passam como vieram
            out[osso] = v
            continue
        w = {}
        for k in ("ang", "dx", "dy"):
            n = float(v.get(k) or 0)
            if n:
                w[k] = round(n, 2)
        if v.get("pe") is not None:
            w["pe"] = round(float(v["pe"]), 1)
        if v.get("var"):
            w["var"] = str(v["var"])
        if v.get("estica") not in (None, 1, 1.0):
            w["estica"] = float(v["estica"])
        if v.get("esconde"):
            w["esconde"] = True
        if v.get("camada") in ("atras", "frente"):
            w["camada"] = v["camada"]
        if isinstance(v.get("ret"), dict) and v["ret"].get("png"):
            w["ret"] = {"var": str(v["ret"].get("var") or ""), "png": str(v["ret"]["png"])}
        if w:
            out[osso] = w
    return out


APAGA = (255, 0, 255, 128)  # no PNG do retoque: pixel que a borracha apagou


def aplicar_retoque(img, png):
    """Pinta e apaga na peça (antes de girar, então a pintura gira junto). `png` é um data URL do tamanho da peça:
    alfa 255 pinta aquela cor, magenta com alfa 128 apaga, o resto deixa como está."""
    if "," in png:
        png = png.split(",", 1)[1]
    r = np.asarray(Image.open(io.BytesIO(base64.b64decode(png))).convert("RGBA"))
    h, w = img.shape[:2]
    r = r[:h, :w]
    out = img.copy()
    sub = out[:r.shape[0], :r.shape[1]]
    pinta = r[..., 3] == 255
    apaga = (r[..., 3] == APAGA[3]) & (r[..., 0] == 255) & (r[..., 1] == 0) & (r[..., 2] == 255)
    sub[pinta] = r[pinta]
    sub[apaga] = 0
    return out


def nome_seguro(nome):
    n = re.sub(r"[^a-z0-9_\-]", "_", str(nome).strip().lower())
    return n.strip("_") or "golpe"


def servidor(lut, porta):
    class Pedido(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def enviar(self, corpo, tipo="application/json", codigo=200):
            if isinstance(corpo, (dict, list)):
                corpo = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
                tipo = "application/json; charset=utf-8"
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(corpo)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(corpo)

        def corpo(self):
            n = int(self.headers.get("Content-Length", 0))
            return json.loads(self.rfile.read(n) or b"{}")

        def do_GET(self):
            caminho = self.path.split("?")[0]
            arg = dict(p.split("=", 1) for p in self.path.split("?", 1)[1].split("&")) if "?" in self.path else {}
            try:
                if caminho in ("/", "/index.html"):
                    return self.enviar((PAGINA / "index.html").read_bytes(), "text/html; charset=utf-8")
                if caminho == "/api/info":
                    return self.enviar(lut.info())
                if caminho == "/api/piloto":
                    return self.enviar(lut.golpes_do_piloto())
                if caminho == "/api/projetos":
                    return self.enviar(lut.projetos())
                if caminho == "/api/projeto":
                    return self.enviar(lut.abrir(arg.get("nome", "")))
                return self.enviar({"erro": "não achei"}, codigo=404)
            except Exception as e:  # noqa: BLE001 - erro volta para a página
                return self.enviar({"erro": str(e)}, codigo=500)

        def do_POST(self):
            try:
                if self.path.startswith("/api/desenhar"):
                    d = self.corpo()
                    return self.enviar(lut.png(d.get("pose", {}), 1 if d.get("escala") == 1 else 3), "image/png")
                if self.path.startswith("/api/gravar"):
                    return self.enviar(lut.gravar(self.corpo()))
                return self.enviar({"erro": "não achei"}, codigo=404)
            except Exception as e:  # noqa: BLE001
                return self.enviar({"erro": f"{type(e).__name__}: {e}"}, codigo=500)

    return ThreadingHTTPServer(("127.0.0.1", porta), Pedido)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lutador", default="pengaro")
    ap.add_argument("--porta", type=int, default=8765)
    ap.add_argument("--sem-navegador", action="store_true")
    a = ap.parse_args()
    print(f"carregando o kit de {a.lutador}...")
    lut = Lutador(a.lutador)
    lut.desenhar({})  # aquece
    srv = servidor(lut, a.porta)
    url = f"http://127.0.0.1:{a.porta}/"
    print(f"montador aberto em {url}  (Ctrl+C para sair)")
    if not a.sem_navegador:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
