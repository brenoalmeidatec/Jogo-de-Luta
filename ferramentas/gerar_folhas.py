#!/usr/bin/env python3
"""Gera as folhas de animação do Pengaró com o Codex, usando o login do ChatGPT (sem chave de API).

Cada folha tem 8 quadros em fila sobre fundo magenta, com a folha do soco como referência de
personagem e estilo. Folha que já existe é pulada, então dá para rodar de novo sem gastar.

  python ferramentas/gerar_folhas.py            gera as que faltam
  python ferramentas/gerar_folhas.py ginga anda gera só essas, mesmo que já existam

Depois recorte com ferramentas/recortar_quadros.py (ou use --recortar).
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
FOLHAS = RAIZ / "sprites/pengaro/quadros/folhas"
REFERENCIA = FOLHAS / "soco.png"
IMAGENS = Path.home() / ".codex/generated_images"

CABECA = """Generate ONE image with your image generation tool. Do not write code and do not edit any file.

The attached sprite sheet shows the exact character and art style to keep: same man, same face, hair, skin, muscles, white capoeira pants with green and yellow side stripes, yellow cord belt, teal sash, the same dark green shin guard on the same leg, barefoot. Same detailed 90s arcade pixel art.

Layout: one single row of 8 frames in 8 equal-width cells, wide image, side view, always facing right, same scale as the attached sheet, feet on the same ground line unless the move leaves the ground. Each figure stays inside its own cell and never touches the next one. Flat solid magenta background (#FF00FF) everywhere, with no shadow, no ground, no text, no numbers, no borders and no effects.

Consecutive frames differ by a small amount, so the motion looks smooth when played in sequence.

Animation: """

# nome: (âncora para o recorte, descrição do movimento)
FOLHAS_PENGARO = {
    "ginga": ("cabeca", "the real capoeira ginga, an 8-frame loop, NOT a boxing guard. The body swings side to side in a low triangle step. Frame 1 both feet parallel and wide, knees bent, torso leaning slightly forward. Frames 2 and 3 the right leg steps far back on the ball of the foot, the torso leans forward and the left arm crosses in front of the face protecting it while the other arm swings low and back. Frame 4 he starts to return. Frame 5 feet parallel and wide again. Frames 6 and 7 the left leg steps far back and the arms swap, with the right arm now crossing in front of the face. Frame 8 returning to frame 1. Relaxed, swaying, rhythmic, arms always moving, always low on the legs."),
    "anda": ("cabeca", "walking forward in capoeira ginga, an 8-frame loop, NOT a boxing walk. He advances with swaying triangle steps, low on bent legs, torso rocking side to side, arms swapping in front of the face and swinging low, like a dance. The legs swap in a full two-step cycle and frame 8 flows back into frame 1."),
    "chute_baixo": ("pes", "a fast low front kick (chapa). Frame 1 ginga stance, frames 2 and 3 the knee lifts, frames 4 and 5 the leg snaps straight at knee height with the sole forward, frames 6 and 7 the leg folds back, frame 8 ginga stance."),
    "chute_alto": ("pes", "meia-lua de frente, a high crescent kick. Frame 1 ginga stance, frame 2 weight on the support leg, frame 3 the straight leg rises from the outside, frames 4 and 5 the leg sweeps across at head height, fully extended, frames 6 and 7 the leg comes down, frame 8 ginga stance."),
    "martelo": ("pes", "a strong elbow strike (cotovelada). Frame 1 ginga stance, frame 2 torso twists back, frame 3 the elbow rises to shoulder height, frames 4 and 5 the torso whips forward with the elbow leading at chin height, frames 6 and 7 he recovers, frame 8 ginga stance."),
    "afastar": ("pes", "a heavy pushing kick that launches the opponent (bencao). Frame 1 ginga stance, frames 2 and 3 the knee chambers high against the chest, frames 4 and 5 the leg thrusts straight forward at chest height with the torso leaning back, frames 6 and 7 the foot lands forward, frame 8 ginga stance."),
    "agachado": ("pes", "going down to the capoeira cocorinha squat. Frames 1 to 4 he sinks from ginga stance into a deep squat with one hand touching the ground and the other arm protecting the face. Frames 5 to 8 he stays in the deep squat, breathing with small movements."),
    "baixo_soco": ("pes", "a low jab from the cocorinha squat. Frame 1 deep squat with one hand on the ground, frames 2 and 3 the shoulder loads, frames 4 and 5 the free arm punches straight forward at waist height, frames 6 to 8 back to the squat."),
    "cabecada": ("pes", "a rising anti-air head butt from the squat. Frame 1 deep squat, frames 2 and 3 the legs push up, frames 4 and 5 the whole body drives upward with the head first, fully stretched, frames 6 to 8 he falls back into the squat."),
    "rasteirinha": ("pes", "a quick low foot sweep from the squat. Frame 1 deep squat with a hand on the ground, frames 2 and 3 the leg slides out, frames 4 and 5 the leg is fully stretched just above the floor, frames 6 to 8 the leg pulls back."),
    "rasteira": ("pes", "a full capoeira rasteira sweep. Frame 1 deep squat with both hands on the ground, frames 2 and 3 the body pivots low, frames 4 and 5 the straight leg sweeps wide along the floor, frames 6 to 8 he gathers back into the squat."),
    "pulo": ("pes", "a jump. Frame 1 knees bent ready to jump, frame 2 pushing off the ground, frame 3 rising with legs starting to tuck, frame 4 tucked at the top like preparing a bicycle kick, frame 5 still tucked and turning, frame 6 falling with legs opening, frame 7 reaching for the ground, frame 8 landing with knees bent."),
    "ar_soco": ("pes", "a downward punch in mid air. All frames are in the air with legs tucked. Frames 1 to 3 the arm winds up, frames 4 and 5 the arm strikes down and forward, frames 6 to 8 he recovers the tucked pose."),
    "bicicleta": ("cabeca", "a mid-air bicycle kick like in football. All frames are in the air. Frame 1 tucked, frames 2 and 3 the body tilts backward, frames 4 and 5 lying back in the air, one leg kicks up and forward fully stretched, frames 6 to 8 he rotates back to tucked."),
    "defesa": ("pes", "blocking. Frame 1 ginga stance, frames 2 and 3 forearms cross in front of the face, frames 4 and 5 he holds the block with a pained grimace, frames 6 and 7 the impact pushes him back a little, frame 8 still blocking."),
    "apanha": ("pes", "getting hit in the face. Frame 1 ginga stance, frames 2 and 3 the head snaps back, mouth open, frames 4 and 5 the torso bends backward with arms flung, frames 6 to 8 he recovers to the ginga stance."),
    "queda": ("cabeca", "being knocked down. Frame 1 hit and bending back, frame 2 feet leaving the ground, frames 3 and 4 flying backward horizontally in the air, frames 5 and 6 falling onto his back, frame 7 bouncing on the floor, frame 8 lying flat on his back."),
    "levanta": ("cabeca", "getting up with a capoeira kip-up. Frame 1 flat on his back, frames 2 and 3 knees pull to the chest, hands by the head, frames 4 and 5 he kicks up off his hands, frames 6 and 7 landing crouched, frame 8 ginga stance."),
    "rolamento": ("cabeca", "a capoeira role, a low rolling dodge. Frame 1 ginga stance, frames 2 to 7 he drops one hand to the floor and spins his low body in a full turn, close to the ground like a cartwheel kept low, frame 8 back up in a crouch."),
    "agarrao": ("cabeca", "a judo-like throw. Frame 1 ginga stance, frame 2 both hands reach forward and grab, frames 3 and 4 pulling the grabbed air toward him, frames 5 and 6 turning his back with the hip low, frames 7 and 8 throwing downward with both arms. No second person is shown."),
    "bola": ("pes", "kicking a shadow ball. Frame 1 ginga stance, frames 2 and 3 he drops low with a hand on the floor, frames 4 and 5 the leg swings through low and stretched, as if kicking a ball along the ground, frames 6 to 8 he recovers to the ginga stance. No ball is shown."),
    "compasso": ("cabeca", "meia-lua de compasso, a spinning kick with a hand on the floor. Frame 1 ginga stance, frames 2 and 3 he bends forward and plants both hands on the ground, frames 4 and 5 the straight leg swings in a big high circle over the head, frames 6 and 7 the leg comes around, frame 8 ginga stance."),
    "armada": ("cabeca", "armada, a rising spinning kick. Frame 1 low stance, frames 2 and 3 he turns his back and starts to rise, frames 4 and 5 he spins in the air with the straight leg sweeping high, frames 6 and 7 falling, frame 8 landing."),
    "caneta": ("cabeca", "a low sliding tackle like football. Frame 1 ginga stance, frames 2 and 3 he drops to the floor, frames 4 and 5 sliding on one hip with the leading leg stretched forward, frames 6 and 7 getting up, frame 8 ginga stance."),
    "golaco": ("pes", "a super football kick. Frames 1 to 3 juggling in place, with the knee and the foot lifting in turns as if keeping a ball up, frames 4 and 5 winding the kicking leg far back with arms spread, frames 6 and 7 a huge full kick with the leg fully stretched forward and the torso leaning back, frame 8 follow-through. No ball is shown."),
    "lata": ("pes", "drinking a can. A generic silver can with no brand and no text in his hand. Frame 1 ginga stance holding the can, frame 2 opens it, frames 3 to 5 tilts his head back and drinks it all, frame 6 crushes the can, frame 7 burps with his head back, frame 8 wide crazy smile, ready to fight."),
    "provoca": ("pes", "a taunt, juggling and then giving up. Frames 1 to 5 keeping a ball up, with the knee and the foot lifting in turns, mouth struggling to say a word. Frame 6 he gives up with a shrug, frames 7 and 8 he raises his arm and shows the middle finger with a smirk. No ball is shown."),
    "vitoria": ("pes", "a victory celebration like a football goal. Frame 1 ginga stance, frames 2 and 3 fists pumping, frames 4 to 6 arms wide open, chest out, shouting, frames 7 and 8 pointing at the sky."),
    "endiabrado": ("pes", "the AWAKENED DEVIL FORM of the same man, an 8-pose sheet (not an animation loop, eight different poses, in this order): 1 power stance with both fists clenched low at his sides, chest out, shouting; 2 walking forward in a low menacing ginga step; 3 deep capoeira cocorinha squat with one hand on the ground; 4 straight punch with the front arm fully extended; 5 high front kick with the straight leg at head height; 6 rising uppercut with one fist high above his head and the knee lifted; 7 a long low kick that sends out a ball of purple shadow, torso leaning back; 8 mid-air jump with the knees tucked. In every pose the transformation is: skin a bit darker with faint purple veins, eyes glowing bright violet, dark violet-black smoke pouring from his feet, hands and shoulders and curling above his head like smoke horns, the white capoeira pants turned charcoal black with torn hems and violet embers along the edges, the yellow cord belt glowing, the green shin guard and teal sash kept. Proud and fierce, not a monster: same face, same hair, same muscles. Keep the same size and scale as the attached sheet."),
    "derrota": ("cabeca", "complaining after losing. Frames 1 and 2 falling to sit on the floor, frames 3 to 8 sitting on the floor with legs out and arms wide open, complaining to the referee, mouth open."),
}


def codex():
    base = Path(os.environ["LOCALAPPDATA"]) / "OpenAI/Codex/bin"
    achado = next(base.rglob("codex.exe"), None) if base.exists() else shutil.which("codex")
    if not achado:
        raise SystemExit("não achei o codex.exe")
    return str(achado)


def gerar(nome, descricao):
    r = subprocess.run([codex(), "exec", "--skip-git-repo-check", "-s", "read-only", "-i", str(REFERENCIA), "-"],
                       input=CABECA + descricao, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=FOLHAS, timeout=480)
    saida = r.stdout + r.stderr
    sessao = re.search(r"session id:\s*([0-9a-f-]{36})", saida)
    if not sessao:
        print(f"{nome}: sem sessão\n{saida[-400:]}", flush=True)
        return False
    pasta = IMAGENS / sessao.group(1)
    imagens = sorted(pasta.glob("*.png"), key=lambda f: f.stat().st_mtime) if pasta.exists() else []
    if not imagens:
        print(f"{nome}: nenhuma imagem\n{saida[-400:]}", flush=True)
        return False
    canto = Image.open(imagens[-1]).convert("RGB").getpixel((5, 5))
    if not (canto[0] > 200 and canto[1] < 60 and canto[2] > 200):
        print(f"{nome}: fundo errado {canto}", flush=True)
        return False
    shutil.copy(imagens[-1], FOLHAS / f"{nome}.png")
    print(f"{nome}: ok", flush=True)
    return True


def main():
    pedidas = sys.argv[1:]
    for nome, (ancora, descricao) in FOLHAS_PENGARO.items():
        if pedidas and nome not in pedidas:
            continue
        if not pedidas and (FOLHAS / f"{nome}.png").exists():
            continue
        for _ in range(2):
            try:
                if gerar(nome, descricao):
                    break
            except subprocess.TimeoutExpired:
                print(f"{nome}: passou do tempo", flush=True)


if __name__ == "__main__":
    main()
