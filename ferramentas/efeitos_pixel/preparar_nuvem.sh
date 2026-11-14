#!/usr/bin/env bash
# Prepara uma máquina zerada (nuvem Linux) para fazer efeitos no Blender e reduzir para pixel art.
#
#   bash ferramentas/efeitos_pixel/preparar_nuvem.sh             bpy (Blender como módulo Python) + Pillow + numpy
#   bash ferramentas/efeitos_pixel/preparar_nuvem.sh --binario   também o Blender 4.5 LTS portátil (blender -b),
#                                                                que animar_folha.py e aura_blender/ usam
#   bash ferramentas/efeitos_pixel/preparar_nuvem.sh --testar    no fim, renderiza o exemplo da explosão
#
# Idempotente: o que já está pronto é pulado, então pode rodar no começo de toda tarefa (a segunda vez leva ~1 s).
# Deixa tudo em ~/.nazafight (ou NAZAFX_HOME) e escreve ~/.nazafight/ambiente.sh com NAZAFX_PY e BLENDER:
#   source ~/.nazafight/ambiente.sh && "$NAZAFX_PY" ferramentas/efeitos_pixel/exemplo_explosao.py
set -euo pipefail

BPY_VERSAO="${BPY_VERSAO:-5.3.0}"        # bpy no PyPI; a 5.3 pede Python 3.13
PY_VERSAO="${PY_VERSAO:-3.13}"
BLENDER_SERIE="${BLENDER_SERIE:-4.5}"    # LTS do projeto (docs/como-trabalhar.md)
CASA="${NAZAFX_HOME:-$HOME/.nazafight}"
VENV="$CASA/bpy-venv"
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"

BINARIO=0; TESTAR=0
for a in "$@"; do
  case "$a" in
    --binario) BINARIO=1 ;;
    --testar) TESTAR=1 ;;
    -h|--help) sed -n 2,13p "$0"; exit 0 ;;
    *) echo "Opção desconhecida: $a" >&2; exit 2 ;;
  esac
done

log() { printf '\033[1;35m[efeitos_pixel]\033[0m %s\n' "$*"; }
inicio=$(date +%s)
mkdir -p "$CASA"

# --- 1. Python 3.13 + venv com bpy, Pillow e numpy -----------------------------------------------------------------
if [ -x "$VENV/bin/python" ] && "$VENV/bin/python" -c "import bpy, PIL, numpy, sys; sys.exit(bpy.app.version_string != '$BPY_VERSAO')" 2>/dev/null; then
  log "bpy $BPY_VERSAO já está pronto em $VENV"
else
  if command -v uv >/dev/null 2>&1; then
    # uv acha (ou baixa) o Python certo e instala o wheel de 400 MB em poucos segundos
    uv venv -q --allow-existing -p "$PY_VERSAO" "$VENV"
    log "instalando bpy $BPY_VERSAO + Pillow + numpy (uv)"
    uv pip install -q -p "$VENV/bin/python" "bpy==$BPY_VERSAO" pillow numpy
  else
    PY="$(command -v "python$PY_VERSAO" || true)"
    [ -n "$PY" ] || { echo "Falta python$PY_VERSAO (ou o uv). Instale um dos dois." >&2; exit 1; }
    [ -x "$VENV/bin/python" ] || "$PY" -m venv "$VENV"
    log "instalando bpy $BPY_VERSAO + Pillow + numpy (pip)"
    "$VENV/bin/python" -m pip install -q --upgrade pip
    "$VENV/bin/python" -m pip install -q "bpy==$BPY_VERSAO" pillow numpy
  fi
  "$VENV/bin/python" -c "import bpy; print('bpy', bpy.app.version_string)"
fi

# --- 2. (opcional) Blender portátil, para os scripts que chamam `blender -b --python` ---------------------------------
BLENDER_BIN="${BLENDER:-}"
if [ "$BINARIO" = 1 ]; then
  atual="$(ls -d "$CASA"/blender-"$BLENDER_SERIE".*-linux-x64 2>/dev/null | sort -V | tail -1 || true)"
  if [ -n "$atual" ] && [ -x "$atual/blender" ]; then
    log "Blender portátil já está em $atual"
  else
    url="https://download.blender.org/release/Blender$BLENDER_SERIE/"
    nome="$(curl -fsSL "$url" | grep -o "blender-$BLENDER_SERIE\.[0-9]*-linux-x64\.tar\.xz" | sort -uV | tail -1)"
    [ -n "$nome" ] || { echo "Não achei o Blender $BLENDER_SERIE em $url" >&2; exit 1; }
    esperado="$(curl -fsSL "$url${nome%-linux-x64.tar.xz}.sha256" | awk -v n="$nome" '$2 == n {print $1}')"
    if [ ! -f "$CASA/$nome" ]; then          # um download interrompido não fica com o nome final
      log "baixando $nome"
      curl -fsSL -o "$CASA/$nome.parte" "$url$nome" && mv "$CASA/$nome.parte" "$CASA/$nome"
    fi
    obtido="$(sha256sum "$CASA/$nome" | awk '{print $1}')"
    [ "$esperado" = "$obtido" ] || { echo "sha256 não confere ($nome)" >&2; rm -f "$CASA/$nome"; exit 1; }
    tar -xJf "$CASA/$nome" -C "$CASA" && rm -f "$CASA/$nome"
    atual="$CASA/${nome%.tar.xz}"
  fi
  BLENDER_BIN="$atual/blender"
  # bibliotecas de sistema que o binário pede e a imagem mínima às vezes não tem
  faltam="$(ldd "$BLENDER_BIN" 2>/dev/null | awk '/not found/{print $1}' | tr '\n' ' ')"
  if [ -n "$faltam" ]; then
    log "faltam bibliotecas: $faltam; tentando apt"
    SUDO=""; [ "$(id -u)" = 0 ] || SUDO="sudo"
    $SUDO apt-get update -qq && $SUDO apt-get install -y -qq libx11-6 libxi6 libxxf86vm1 libxfixes3 libxrender1 \
      libxkbcommon0 libsm6 libgl1 libegl1 >/dev/null
  fi
  "$BLENDER_BIN" -b --version 2>/dev/null | head -1
fi

# --- 3. Ambiente para as próximas chamadas ---------------------------------------------------------------------------
{
  echo "# gerado por ferramentas/efeitos_pixel/preparar_nuvem.sh"
  echo "export NAZAFX_PY=\"$VENV/bin/python\""
  [ -n "$BLENDER_BIN" ] && echo "export BLENDER=\"$BLENDER_BIN\""
} > "$CASA/ambiente.sh"
log "pronto em $(( $(date +%s) - inicio )) s. Use: source $CASA/ambiente.sh"

if [ "$TESTAR" = 1 ]; then
  "$VENV/bin/python" "$RAIZ/ferramentas/efeitos_pixel/exemplo_explosao.py"
fi
