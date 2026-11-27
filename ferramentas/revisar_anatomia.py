#!/usr/bin/env python3
"""Revisão de anatomia (#51, item 3): folha de contato de todos os desenhos e a folha marcada dos reprovados.

  python ferramentas/revisar_anatomia.py pranchas SAIDA [lutador ...]   todas as pastas, 5 por imagem (para revisar)
  python ferramentas/revisar_anatomia.py marcada                        só as pastas de ACHADOS, em docs/anatomia-51/
  python ferramentas/revisar_anatomia.py tabela                         a tabela em Markdown (colada no LEIA-ME)
  python ferramentas/revisar_anatomia.py prompts                        a linha FIX de cada folha a redesenhar

Cada linha é uma pasta de desenhos (00..07), recortada na caixa comum dos 8 e ampliada, para o tamanho relativo entre
os quadros continuar valendo. Na folha marcada: vermelho = redesenhar, amarelo = leve (decide o Breno), ciano = só cor.
ACHADOS é a revisão de 2026-11-15, feita olhando os 2.680 desenhos; ao redesenhar uma folha, tire a linha daqui.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
SPR = RAIZ / "sprites"
CW, CH = 225, 190
FONTES = {  # nome -> (lutador, pasta dos desenhos)
    "hazaki": ("hazaki", "quadros_arcade_hd"),
    "diabo_loiro": ("hazaki", "diabo_terno"),
    "ck": ("ck", "quadros_arcade_hd"),
    "pengaro": ("pengaro", "quadros_arcade_hd"),
    "gutto": ("gutto", "quadros"),
    "raiclaven": ("raiclaven", "quadros"),
}
try:
    FONTE = ImageFont.truetype("DejaVuSans.ttf", 11)
except OSError:  # sem a fonte os acentos não saem, mas a folha sai
    FONTE = ImageFont.load_default()
COR = {"G": (255, 40, 40), "L": (255, 210, 0), "C": (0, 220, 255)}

# nome -> pasta -> [(quadros, nível, defeito)]   G = redesenhar, L = leve, C = só cor/mancha
ACHADOS = {
    "hazaki": {
        "agarrao_abraco": [([5], "G", "tronco dobrado para trás com os braços para cima, cabeça abaixo das mãos")],
        "ar_soco": [([4, 5], "G", "braço que desce comprido demais e punho enorme")],
        "corrida": [([0, 2, 3, 4, 6, 7], "G", "pulseira teal foi para o bíceps e o tronco incha (fora do modelo)")],
        "cutucao_recuo": [([2, 3, 4, 5], "G", "braço estendido comprido e fino")],
        "estatueta_arremesso": [([3, 4], "G", "braço por cima da cabeça comprido e fino, a cabeça some")],
        "machado": [([2, 3], "G", "perna na vertical comprida e fina, o tronco some atrás dela")],
        "punho_chao": [([4, 5], "G", "tronco deitado some e a perna de trás estica")],
        "rasteira": [([2, 3, 4, 5], "G", "perna estendida com quase o dobro do tronco")],
        "rasteira_arco": [([1, 6], "G", "braços enormes pendurados"), ([4, 5], "G", "perna da rasteira vira um toco")],
        "soco_reto": [([3, 4, 5], "G", "tronco vira uma tábua de perfil, sem ombro")],
        "tesoura": [([4], "G", "de costas vira um bloco largo de pernas curtas com punho gigante")],
        "voadora": [([3, 4, 5], "G", "pés gigantes de frente e pernas longas demais")],
        "agarrao_perna": [([4, 5], "L", "tronco e cabeça maiores que nos vizinhos")],
        "ar_chute": [([4, 5], "L", "perna estendida comprida")],
        "calcada_levantada": [([1], "L", "braço erguido fino, tronco estreito")],
        "chute": [([6], "L", "canela pendurada torta na volta")],
        "cotovelada": [([1, 2], "L", "tronco estreito com o braço erguido")],
        "machado_curto": [([2], "L", "perna vertical fina")],
        "passagem_rapida": [([6], "L", "cabeça grande no agachado")],
        "pose_super": [([2, 3], "L", "ombros largos demais de frente")],
        "soco": [([4], "L", "punho grande além dos 15%")],
        "tapa_costas": [([2], "L", "de costas mais largo e baixo")],
    },
    "diabo_loiro": {
        "d_agarrao_abraco": [([5], "G", "mesma pose quebrada do Hazak base (tronco para trás, braços para cima)")],
        "d_agarrao_perna": [([1, 2], "G", "antebraço sem a manga do terno (sobra do Hazak base)")],
        "d_ar_joelho": [([3, 4, 5], "G", "perna estendida maior que o tronco")],
        "d_coice": [([3, 4, 5], "G", "perna do coice troca de grossura: fina, tubo grosso, fina")],
        "d_maleta_giro": [([2, 4], "G", "de costas vira um bloco de casaco com pernas curtas")],
        "d_maleta_sobe": [([4, 5], "G", "braço erguido comprido demais, corpo afina")],
        "d_pisao_ar": [([3, 4, 5], "G", "perna do pisão uma vez e meia maior, sapato enorme")],
        "d_punho_anel": [([3, 4, 5], "G", "braço que soca o chão sem manga e comprido")],
        "d_queda": [([3, 4, 5, 6, 7], "G", "chapéu caído no peito do tamanho do tronco")],
        "d_rasteira_arco": [([2, 3, 4, 5], "G", "mão de apoio enorme e perna da rasteira em toco")],
        "d_chapelada": [([2], "L", "corpo fino e alto com o braço erguido")],
        "d_chute_lateral": [([3, 4, 5], "L", "perna do chute curta e fina")],
        "d_coice_costas": [([2], "L", "de costas mais largo"), ([3, 4, 5], "L", "perna do chute curta")],
        "d_maletada_cima": [([2, 3], "L", "corpo afina com os braços para cima")],
        "d_maletada_lado": [([4, 5], "L", "braço estendido comprido e fino")],
        "d_maletada_volta": [([4, 5], "L", "braço estendido comprido e fino")],
    },
    "ck": {
        "ar_soco": [([4], "G", "tronco inflado, braço que desce comprido, luva enorme")],
        "armada": [([1, 2], "G", "giro de costas com corpo fino e mais alto, braços caídos")],
        "baixo_soco": [([3, 4], "G", "tronco vira um bloco branco inflado, cabeça pequena")],
        "cabecada": [([4], "G", "braço erguido comprido, corpo esticado")],
        "derrota": [([3], "G", "sem boné vira outro rosto (cabelo castanho claro)")],
        "lata": [([5, 6], "G", "cabeça virada e camisa de outro desenho")],
        "e_rolamento": [([6], "L", "de frente com pernas curtas e corpo largo")],
        "afastar": [([4], "L", "perna do chute curta")],
        "caneta": [([3, 4], "L", "tronco deitado comprido")],
        "chute_alto": [([4], "L", "perna do chute curta")],
        "compasso": [([2], "L", "de costas estreito")],
        "e_cabecada": [([4], "L", "corpo esticado fino")],
        "e_derrota": [([5, 6, 7], "L", "cabeça maior sentado")],
        "rasteira": [([1, 2, 3, 4, 5], "C", "luva da mão no chão ficou lilás em vez de vermelha")],
    },
    "pengaro": {
        "agarrao": [([4, 5], "G", "de costas mais baixo e largo"), ([6, 7], "G", "braço da frente comprido demais")],
        "corre": [([6, 7], "G", "perna de trás perde a caneleira, pé apagado")],
        "despertar_a": [([3], "G", "boneco sobe no quadro, pés fora do chão"), ([5], "G", "braço comprido")],
        "ginga": [([5], "G", "pernas cruzadas sem caneleira")],
        "lata": [([5], "G", "pernas cruzadas sem caneleira")],
        "soco": [([5], "G", "pernas cruzadas sem caneleira")],
        "vitoria": [([1, 2, 3, 4, 5, 6, 7], "G", "corpo mais magro que o quadro 0; a garrafa muda de tamanho")],
        "e_agarrao": [([5], "G", "de costas baixo e largo")],
        "e_armada": [([2], "G", "de costas maior que os vizinhos")],
        "e_despertar": [([0, 1, 2, 3], "G", "Pengaró de pele clara e cabelo liso no começo da segunda metade da cena do Despertar")],
        "bola": [([3], "L", "braço esticado comprido, tronco fino")],
        "e_vitoria": [([2], "L", "braço erguido comprido")],
        "golaco": [([4, 5, 6, 7], "L", "tronco afina com os braços para cima")],
        "compasso": [([5], "C", "mancha vermelha no rosto")],
        "parry_baixo": [([4], "C", "mancha magenta")],
        "rasteira": [([2], "C", "mancha magenta")],
    },
    "gutto": {
        "lata": [([1, 2, 3, 4], "G", "cabelo de outro desenho (castanho, cacheado)")],
        "e_baixo_soco": [([2], "G", "tronco de costas com pele clara, outro desenho")],
        "e_chute_alto": [([3, 4], "G", "perna do coice solta do corpo")],
        "e_armada": [([3, 4], "G", "em pé vira humanoide magro, perde o corpo do garanhão")],
        "e_cabecada": [([3, 4], "G", "em pé vira humanoide magro")],
        "e_golaco": [([3, 6, 7], "G", "em pé vira humanoide magro")],
        "e_vitoria": [([3, 4, 5], "G", "em pé vira humanoide magro")],
        "e_provoca": [([4, 5], "G", "em pé vira humanoide magro")],
        "e_martelo": [([2], "G", "em pé vira humanoide magro")],
        "e_agarrao": [([5], "G", "em pé vira humanoide magro")],
        "golaco": [([6, 7], "L", "giro de costas e de frente com o rosto diferente")],
        "chute_alto": [([2], "C", "dedos rosa")],
        "martelo": [([5, 6], "C", "cotovelo rosa")],
        "queda": [([4, 5], "C", "mãos rosa")],
        "rasteira": [([0, 5, 6], "C", "dedos rosa")],
        "rolamento": [([1, 6], "C", "mãos rosa")],
        "e_bicicleta": [([0, 6, 7], "C", "antebraço laranja claro"), ([1, 2], "C", "mancha creme na perna")],
        "e_levanta": [([1], "C", "mancha branca")],
        "e_queda": [([2], "C", "mancha rosa")],
        "e_rolamento": [([1, 5, 6], "C", "calção lilás e vermelho vivo")],
    },
    "raiclaven": {
        "agarrao": [([4], "G", "de costas mais magro e sem ombreira"), ([5], "G", "braço esticado comprido")],
        "armada": [([1, 2], "G", "giro de costas menor, a ombreira some")],
        "levanta": [([3, 4, 5], "G", "braço de metal pendurado até o chão"), ([2], "C", "calça azulada")],
        "bola": [([2], "L", "dois braços para cima, rosto diferente")],
        "cabecada": [([3, 4], "L", "em pé com a tesoura no alto o corpo afina")],
        "golaco": [([2, 5, 7], "L", "em pé o corpo afina e a ombreira encolhe")],
        "soco": [([4, 5], "L", "tronco virado, ombreira encolhe")],
        "vitoria": [([6, 7], "L", "em pé o corpo afina")],
        "rolamento": [([5], "C", "vermelho vivo na mão")],
    },
}

# O que vai na linha FIX do bloco de correção (docs/anatomia-51/LEIA-ME.md), por folha a redesenhar. Quadros 1-8, como no prompt.
FIX = {
    "hazaki": {
        "agarrao_abraco": "frame 6: the torso must stay upright while he lifts, head above the hands, spine not bent backwards",
        "ar_soco": "frames 5-6: the punching arm keeps the same length as in frame 1, the fist at most 15% larger",
        "corrida": "all frames: teal wristband on the rear WRIST only, never on the biceps; torso the same size as in the idle sheet",
        "cutucao_recuo": "frames 3-6: the extended arm keeps normal length and thickness (shoulder to fist = shoulder to hip)",
        "estatueta_arremesso": "frames 4-5: the overhead arm keeps normal length and thickness, the head stays fully visible",
        "machado": "frames 3-4: the raised leg keeps the same length and thickness as the standing leg, the torso stays visible",
        "punho_chao": "frames 5-6: the torso keeps its full size while leaning, the rear leg keeps normal length",
        "rasteira": "frames 3-6: the sweeping leg is exactly as long as the standing leg in the idle sheet",
        "rasteira_arco": "frames 2 and 7: arms of normal length, hands do not hang below the knees; frames 5-6: the sweeping leg at full length",
        "soco_reto": "frames 4-6: keep the full shoulder and chest width in three-quarter view, never a flat profile plank",
        "tesoura": "frame 5: back view with the same height, shoulder width and leg length as the front view, fists of normal size",
        "voadora": "frames 4-6: feet at most 15% larger, legs the same length as in the idle sheet",
    },
    "diabo_loiro": {
        "d_agarrao_abraco": "frame 6: the torso must stay upright while he lifts, head above the hands",
        "d_agarrao_perna": "frames 2-3: both arms keep the pinstripe jacket sleeve and shirt cuff, no bare forearm",
        "d_ar_joelho": "frames 4-6: the extended leg is exactly as long as the other leg",
        "d_coice": "frames 4-6: the kicking leg keeps one constant length and thickness, same shoe size as the standing foot",
        "d_maleta_giro": "frames 3 and 5: back view with the same height, shoulder width and leg length as the front view",
        "d_maleta_sobe": "frames 5-6: the raised arm keeps normal length, the body keeps its width",
        "d_pisao_ar": "frames 4-6: the stomping leg is exactly as long as the other leg, shoe at most 15% larger",
        "d_punho_anel": "frames 4-6: the punching arm keeps the jacket sleeve and normal length",
        "d_queda": "frames 4-8: the fallen hat keeps the same size it has on his head",
        "d_rasteira_arco": "frames 3-6: the supporting hand of normal size, the sweeping leg at full length",
    },
    "ck": {
        "ar_soco": "frame 5: torso the same size as in frame 1, the punching arm of normal length, glove at most 15% larger",
        "armada": "frames 2-3: the turning body keeps the same height and width, gloves stay up",
        "baixo_soco": "frames 4-5: torso the same size as in frame 1, head the same size",
        "cabecada": "frame 5: the raised arm of normal length, the body keeps its width",
        "derrota": "frame 4: same face and same dark hair when the cap comes off",
        "lata": "frames 6-7: same head angle, face and polo shirt as the other frames",
    },
    "pengaro": {
        "agarrao": "frames 5-6: back view with the same height and width as the front view; frames 7-8: front arm of normal length",
        "corre": "frames 7-8: the green shin guard stays on the same leg, both feet fully drawn",
        "despertar_a": "frame 4: feet on the same ground line as the other frames; frame 6: raised arm of normal length",
        "ginga": "frame 6: same wide stance as the neighbours, shin guard visible, legs not crossed",
        "lata": "frame 6: same wide stance as the neighbours, shin guard visible, legs not crossed",
        "soco": "frame 6: same wide stance as the neighbours, shin guard visible, legs not crossed",
        "vitoria": "frames 2-8: body as thick and muscular as in frame 1, the bottle always the same size",
        "e_agarrao": "frame 6: back view with the same height and width as the front view",
        "e_armada": "frame 3: back view the same size as the neighbours",
        "e_despertar": "frames 1-4: same dark brown skin and same short curly hair as the attached reference",
    },
    "gutto": {
        "lata": "frames 2-5: same black hair and same face as the attached reference",
        "e_baixo_soco": "frame 3: same dark red skin and same beast body as the other frames",
        "e_chute_alto": "frames 4-5: the kicking leg stays attached to the hip, same thickness as the other leg",
        "e_armada": "frames 4-5: standing tall he keeps the same massive hunched beast torso and thick limbs",
        "e_cabecada": "frames 4-5: standing tall he keeps the same massive hunched beast torso and thick limbs",
        "e_golaco": "frames 4, 7, 8: standing tall he keeps the same massive hunched beast torso and thick limbs",
        "e_vitoria": "frames 4-6: standing tall he keeps the same massive hunched beast torso and thick limbs",
        "e_provoca": "frames 5-6: standing tall he keeps the same massive hunched beast torso and thick limbs",
        "e_martelo": "frame 3: standing tall he keeps the same massive hunched beast torso and thick limbs",
        "e_agarrao": "frame 6: standing tall he keeps the same massive hunched beast torso and thick limbs",
    },
    "raiclaven": {
        "agarrao": "frame 5: back view with the same body width and the shoulder armor; frame 6: the reaching arm of normal length",
        "armada": "frames 2-3: the turning body keeps the same size and the shoulder armor",
        "levanta": "frames 4-6: the metal arm of normal length, the scissors never touch the ground",
    },
}


def pastas(nome):
    lut, sub = FONTES[nome]
    base = SPR / lut / sub
    return [p for p in sorted(base.iterdir()) if p.is_dir() and (p / "00.png").exists() and not p.name.startswith("folhas")]


def linha(nome, p, marcas=()):
    ims = [Image.open(f).convert("RGBA") for f in sorted(p.glob("[0-9][0-9].png"))[:8]]
    bb = None
    for im in ims:
        b = im.getbbox()
        if b:
            bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    bb = bb or (0, 0, 1, 1)
    row = Image.new("RGB", (CW * 8, CH), (70, 80, 95))
    d = ImageDraw.Draw(row)
    for k, im in enumerate(ims):
        c = im.crop(bb)
        s = min((CW - 6) / c.width, (CH - 16) / c.height)
        c = c.resize((max(1, int(c.width * s)), max(1, int(c.height * s))), Image.LANCZOS if s < 1 else Image.NEAREST)
        row.paste(c, (k * CW + (CW - c.width) // 2, CH - c.height - 2), c)
        d.line([(k * CW, 0), (k * CW, CH)], fill=(40, 45, 55))
        d.text((k * CW + 5, 16), str(k), fill=(255, 255, 0), font=FONTE)
    ordem = {"C": 0, "L": 1, "G": 2}
    nivel = {}
    for quadros, n, _ in marcas:
        for k in quadros:
            if ordem[n] >= ordem.get(nivel.get(k, "C"), 0) or k not in nivel:
                nivel[k] = n
    for k, n in nivel.items():
        for e in range(3):
            d.rectangle([k * CW + 1 + e, 13 + e, (k + 1) * CW - 2 - e, CH - 1 - e], outline=COR[n])
    d.rectangle([0, 0, CW * 8, 12], fill=(20, 20, 30))
    d.text((3, -1), f"{nome}/{p.name}" + ("   " + "; ".join(f"{q}: {t}" for q, _, t in marcas) if marcas else ""), fill=(255, 255, 255), font=FONTE)
    return row


def salvar(linhas, destino, por_imagem):
    feitos = []
    for n in range(0, len(linhas), por_imagem):
        lote = linhas[n:n + por_imagem]
        sh = Image.new("RGB", (CW * 8, CH * len(lote)))
        for r, im in enumerate(lote):
            sh.paste(im, (0, r * CH))
        arq = Path(f"{destino}_{n // por_imagem + 1:02d}.jpg")
        sh.save(arq, quality=85)
        feitos.append(arq)
    return feitos


def tabela():
    out = []
    for nome, ps in ACHADOS.items():
        g = sum(1 for m in ps.values() if any(n == "G" for _, n, _ in m))
        out.append(f"\n### {nome} ({g} folhas para redesenhar)\n\n| Folha | Quadros | Nível | Defeito |\n|---|---|---|---|")
        for pasta, marcas in sorted(ps.items(), key=lambda kv: ("GLC".index(max(kv[1], key=lambda m: -"GLC".index(m[1]))[1]), kv[0])):
            for quadros, n, t in marcas:
                out.append(f"| `{pasta}` | {', '.join(map(str, quadros))} | {dict(G='redesenhar', L='leve', C='cor')[n]} | {t} |")
    return "\n".join(out)


def prompts():
    out = []
    for nome, ps in FIX.items():
        faltam = {k for k, m in ACHADOS[nome].items() if any(n == "G" for _, n, _ in m)} ^ set(ps)
        assert not faltam, f"{nome}: FIX e ACHADOS não batem em {sorted(faltam)}"
        out.append(f"\n### {nome}\n\n| Folha | Linha FIX |\n|---|---|")
        out += [f"| `{k}` | `FIX: {t}.` |" for k, t in sorted(ps.items())]
    return "\n".join(out)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "marcada"
    if cmd == "pranchas":
        saida = Path(sys.argv[2])
        saida.mkdir(parents=True, exist_ok=True)
        for nome in sys.argv[3:] or FONTES:
            print(nome, len(salvar([linha(nome, p) for p in pastas(nome)], saida / nome, 5)), "imagens")
    elif cmd == "marcada":
        saida = RAIZ / "docs/anatomia-51"
        saida.mkdir(parents=True, exist_ok=True)
        for nome, ps in ACHADOS.items():
            lut, sub = FONTES[nome]
            for pasta in ps:
                assert (SPR / lut / sub / pasta / "00.png").exists(), f"{nome}/{pasta} não existe"
            ordem = sorted(ps, key=lambda k: ("GLC".index(min(ps[k], key=lambda m: "GLC".index(m[1]))[1]), k))
            arqs = salvar([linha(nome, SPR / lut / sub / k, ps[k]) for k in ordem], saida / f"antes_{nome}", 6)
            print(nome, len(ps), "folhas,", len(arqs), "imagens")
    elif cmd == "tabela":
        print(tabela())
    elif cmd == "prompts":
        print(prompts())


if __name__ == "__main__":
    main()
