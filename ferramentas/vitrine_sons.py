"""Vitrine dos sons do Nazafights: junta os sons dos .snd num .mp3 só, para ouvir no fone, e escreve os tempos.

Uso:  python ferramentas/vitrine_sons.py            gera sons/vitrine-dos-sons.mp3 e sons/vitrine-dos-sons.md
      python ferramentas/vitrine_sons.py --pasta X  grava em outra pasta

Lê o que o gerar_sons.py gravou (motif/nazafight/*.snd e chars/<lutador>/<lutador>.snd), então rode ele antes.
Cada trecho é uma lista de "golpes"; um golpe é uma sequência de sons ((arquivo, grupo, número), atraso em s) tocados
juntos, como no jogo (o vento sai no começo e o acerto logo depois). Precisa do ffmpeg para o .mp3.
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_sons as g  # noqa: E402

F, N, S = "common", "fight", "system"


def golpe(*sons):
    """sons: (arquivo, 'g,n', atraso) ou (arquivo, 'g,n')."""
    return [(s[0], s[1], s[2] if len(s) > 2 else 0.0) for s in sons]


def acerto(l, vento, hit, atraso=0.09):
    return golpe((F if vento.startswith("F") else l, vento.lstrip("F"), 0), (l, hit, atraso))


def trechos():
    t = [("Menu: mover, confirmar, voltar", [golpe((S, "100,0")), golpe((S, "100,1")), golpe((S, "100,2"))]),
         ("Narrador: primeiro round, luta", [golpe((N, "0,1")), golpe((N, "1,0"))]),
         ("Defesa, quedas, agarrão (pega, arremesso, escape), parry base e endiabrado",
          [golpe((F, "6,0")), golpe((F, "6,1")), golpe((F, "7,0")), golpe((F, "7,2")), golpe((F, "35,0")),
           golpe((F, "35,1")), golpe((F, "35,2")), golpe((F, "30,0")), golpe((F, "30,1"))]),
         ("Super (início), barra de poder, transformação",
          [golpe((F, "20,0")), golpe((N, "21,0")), golpe((N, "21,1")), golpe((F, "31,0"), (F, "31,1", 1.1))])]
    p, ck, gu, hz, rc = "pengaro", "ck", "gutto", "hazaki", "raiclaven"
    t += [
        ("Pengaró: soco, chute, garrafa (acerto), latinha (Latada: voa e bate), Garrafada em Arco, Mão de Chimpá",
         [acerto(p, "F40,0", "51,1"), acerto(p, "F40,3", "52,2"), golpe((p, "54,2")),
          golpe((p, "50,4"), (p, "50,5", 0.35)), golpe((p, "50,8"), (p, "50,0", 0.3)), golpe((p, "50,6"))]),
        ("Pengaró: Chuva de Bebidas (latas e garrafas), Despertar (gole, vidro, possessão), corrente e sombra",
         [golpe((p, "50,5"), (p, "54,2", 0.25), (p, "50,5", 0.5), (p, "54,2", 0.75), (p, "50,1", 1.0)),
          golpe((p, "50,2"), (p, "50,1", 0.6), (p, "50,3", 1.0), (F, "31,1", 1.0)),
          golpe((p, "50,7"), (p, "53,2", 0.2)), golpe((p, "53,3"))]),
        ("CK: luva fraca e forte, Boné Voador (vai e acerta), Tragada, Grave do Paredão",
         [acerto(ck, "F40,0", "51,0"), acerto(ck, "F40,1", "51,2"), golpe((ck, "50,0"), (ck, "50,4", 0.4)),
          golpe((ck, "50,1")), golpe((ck, "50,2"))]),
        ("CK: Despertar (paredão tocando, garrafa quebrando), Modo Ratão (caco de garrafa), Garrafa Voadora",
         [golpe((ck, "50,5"), (ck, "50,6", 0.9), (F, "31,1", 1.3)), acerto(ck, "F40,4", "53,1"),
          acerto(ck, "F40,4", "53,3"), golpe((F, "36,0"), (ck, "50,3", 0.3))]),
        ("Gutto: jab, canela de Muay Thai fraca e forte, cotovelo e joelhada, Joelhada Voadora, beijinho",
         [acerto(gu, "F40,0", "51,1"), acerto(gu, "F40,2", "52,0"), acerto(gu, "F40,3", "52,2"),
          acerto(gu, "F40,1", "54,2"), golpe((gu, "50,1")), golpe((gu, "50,0"))]),
        ("Gutto endiabrado: bufada, galope, coice, casco, relincho",
         [golpe((gu, "50,4")), golpe((gu, "50,2")), golpe((gu, "50,5")), acerto(gu, "F40,4", "53,2"),
          golpe((gu, "50,3"))]),
        ("Hazak: soco de concreto, pedra (chuta do chão, voa e bate), estatueta, guarda de aço, faixa",
         [acerto(hz, "F40,1", "51,2"), golpe((hz, "50,4"), (hz, "50,5", 0.3), (hz, "50,9", 0.65)),
          golpe((hz, "50,1")), golpe((hz, "50,2")), golpe((hz, "50,3"))]),
        ("Hazak: carga e bola de ki; Diabo Loiro: rajada de ki das trevas, golpe das trevas",
         [golpe((hz, "50,6"), (hz, "50,7", 0.9)), golpe((hz, "50,8")), acerto(hz, "F40,4", "53,2")]),
        ("Raiclaven: pente (x), tesoura abrindo e cortando (y fraco e forte), Tesoura Helicóptero, Tesourão",
         [acerto(rc, "F40,0", "51,1"), acerto(rc, "55,0", "54,0"), acerto(rc, "55,1", "54,2", 0.12),
          golpe((rc, "50,4"), (rc, "54,2", 0.5)), acerto(rc, "55,1", "54,3", 0.12)]),
        ("Raiclaven: Pente Voador, Borrifada, Varrida, Cadeira, Próximo! (talco), Toalha Quente, Cabeça na Pia",
         [golpe((rc, "50,2")), golpe((rc, "50,1")), golpe((rc, "50,5")), golpe((rc, "50,3")), golpe((rc, "50,6")),
          golpe((rc, "50,10")), golpe((rc, "50,11"))]),
        ("Raiclaven: Máquina Explosiva (zumbe e explode), Surto: Navalha de Sombra e corte de serra",
         [golpe((rc, "50,7"), (rc, "50,8", 1.0)), golpe((rc, "50,9")), acerto(rc, "55,1", "53,2", 0.12)]),
        ("Narrador: nocaute, você venceu, perfeito", [golpe((N, "2,0")), golpe((N, "2,3")), golpe((N, "2,6"))]),
    ]
    return t


def carregar():
    arqs = {F: g.MOTIF / "common.snd", N: g.MOTIF / "fight.snd", S: g.MOTIF / "system.snd"}
    arqs.update({n: g.RAIZ / "chars" / n / f"{n}.snd" for n in g.LUTADORES})
    out = {}
    for k, a in arqs.items():
        for (gr, n), w in g.ler_snd(a).items():
            out[(k, f"{gr},{n}")] = np.frombuffer(w[44:], "<i2") / 32768
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasta", default=str(g.RAIZ / "sons"))
    a = ap.parse_args()
    sons = carregar()
    pista, tempos, pos = [], [], 0.0
    for titulo, golpes in trechos():
        tempos.append((pos, titulo))
        for gp in golpes:
            x = g.mix(*[(sons[(arq, gn)], at) for arq, gn, at in gp])
            x = np.concatenate([x, np.zeros(g._n(0.35))])
            pista.append(x)
            pos += len(x) / g.SR
        pista.append(np.zeros(g._n(0.6)))
        pos += 0.6
    x = np.clip(np.concatenate(pista), -1, 1)
    pasta = Path(a.pasta)
    wav = pasta / "vitrine-dos-sons.wav"
    g.gravar_wav(wav, x)
    mp3 = pasta / "vitrine-dos-sons.mp3"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", "alimiter=limit=0.7:level=false", "-b:a", "160k", str(mp3)], check=True)
    wav.unlink()
    linhas = ["# Vitrine dos sons (ouvir no fone)", "",
              "Arquivo: vitrine-dos-sons.mp3, feito por `ferramentas/vitrine_sons.py` com os .snd do jogo. Tempos:", ""]
    linhas += [f"- {int(t // 60)}:{t % 60:04.1f}  {tt}" for t, tt in tempos]
    linhas += ["", "Tudo sintetizado por `ferramentas/gerar_sons.py`. Tabela completa em `docs/sons.md`."]
    (pasta / "vitrine-dos-sons.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(mp3, f"{pos:.1f} s")


if __name__ == "__main__":
    main()
