"""
Gera sprites de personagens ORIGINAIS usando a API de imagens da OpenAI.

Como usar:
  1. pip install openai
  2. Defina a chave como variável de ambiente (NUNCA coloque a chave no código):
       Windows (PowerShell):  $env:OPENAI_API_KEY = "sk-..."
       Linux/macOS:           export OPENAI_API_KEY="sk-..."
  3. python ferramentas/gerar_sprites.py --personagem kaio
       (gera base.png e depois uma imagem por pose em sprites/kaio/)

Opções úteis:
  --poses soco chute      gera só essas poses
  --qualidade low         mais barato para testar (low | medium | high)
  --refazer-base          gera de novo a imagem de referência do personagem

Personagens, estilo e poses ficam em ferramentas/personagens.json.
"""
import argparse
import base64
import json
import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    sys.exit("Instale a biblioteca primeiro:  pip install openai")

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = Path(__file__).resolve().parent / "personagens.json"
MODELO = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")


def salvar(resposta, destino: Path):
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(base64.b64decode(resposta.data[0].b64_json))
    print(f"  salvo: {destino.relative_to(RAIZ)}")


def main():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    p = argparse.ArgumentParser(description="Gera sprites com a API da OpenAI")
    p.add_argument("--personagem", required=True, choices=sorted(cfg["personagens"]))
    p.add_argument("--poses", nargs="*", choices=sorted(cfg["poses"]),
                   help="poses a gerar (padrão: todas)")
    p.add_argument("--qualidade", default="medium", choices=["low", "medium", "high"])
    p.add_argument("--refazer-base", action="store_true")
    args = p.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Defina a variável de ambiente OPENAI_API_KEY antes de rodar.")

    cliente = OpenAI()
    pasta = RAIZ / "sprites" / args.personagem
    descricao = cfg["personagens"][args.personagem]["descricao"]
    estilo = cfg["estilo"]
    base = pasta / "base.png"

    # 1) Imagem de referência do personagem (usada para manter o visual igual em todas as poses)
    if args.refazer_base or not base.exists():
        print(f"Gerando referência de {args.personagem}...")
        r = cliente.images.generate(
            model=MODELO,
            prompt=f"{descricao}. Idle fighting stance. {estilo}",
            size="1024x1024",
            quality=args.qualidade,
            background="transparent",
            output_format="png",
        )
        salvar(r, base)

    # 2) Uma imagem por pose, usando a referência para manter o mesmo personagem
    for nome in args.poses or cfg["poses"]:
        print(f"Gerando pose '{nome}'...")
        with open(base, "rb") as ref:
            r = cliente.images.edit(
                model=MODELO,
                image=ref,
                prompt=(
                    "Same exact character as the reference image (same face, hair, clothes, colors "
                    f"and art style). Pose: {cfg['poses'][nome]}. {estilo}"
                ),
                size="1024x1024",
                quality=args.qualidade,
                background="transparent",
                output_format="png",
            )
        salvar(r, pasta / f"{nome}.png")

    print("Pronto!")


if __name__ == "__main__":
    main()
