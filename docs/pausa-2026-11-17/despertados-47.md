# Pausa 17/11: despertados da #47 (agarrão, poder, especiais)

## Pronto e na `mugen` (robô 0 defeito, vídeos em docs/despertados-47/pecas/)
- Pengaró despertado: agarrão e poder de longe no boneco de peças.
- Ratão (CK despertado): Paredão na Cara e Talo Aceso (kit `ferramentas/kit_ck_e.py` + `ck_e_pecas.py`).
- Garanhão (Gutto despertado): Levanta e Arremessa e Estouro (kit `kit_garanhao_47.py` + `garanhao_47_pecas.py`).
- Tudo religado com o meio-termo (antecipação segurada) e com aura nos agarrões.

## Parado no meio (só nesta branch, `claude/project-thread-fm5ilj`, NÃO está na mugen)
`ferramentas/especiais_garanhao.py`: Bufada de Fogo (↓→x/y, projétil de labareda), Investida do Touro (↓→a/b, aguenta
1 golpe), Pisão Racha-Chão (↓↓a/b, rachadura baixa), Chifrada Ascendente (→↓→x/y, antiaéreo) e a super Fúria do
Minotauro (←→↓a/b: carrega até a parede, joga no alto, pisa no chão). Grupos 47200-47252, ações/estados 4800-4952.
Já roda sem erro e grava .sff/.air/.cns/.cmd/movelist, mas ainda NÃO passou no robô nem foi filmado.
Também: `aura_silhueta.py` aceita grupos 47100-47249 e `filmar_47.py` ganhou `--golpes "estado:dist:ticks,..."`.

## Próximos passos exatos
1. `git fetch origin mugen && git merge origin/mugen` (perguntar à thread do Gutto se estão mexendo no gutto.sff).
2. `python3 ferramentas/despertados_47.py gutto` (só se a mugen trouxe gutto.sff novo) e então
   `python3 ferramentas/especiais_garanhao.py`.
3. `python3 ferramentas/aura_silhueta.py gutto` (demora mais de 2 min, rodar em segundo plano) e
   `python3 ferramentas/encolher_sff.py gutto --indexar 49000-49099` (limite 100 MB do GitHub).
4. Robô: `python3 ferramentas/testar_pengaro.py --linux --lutador gutto` (esperado 186/0).
5. Vídeo: `python3 ferramentas/filmar_47.py docs/despertados-47/pecas/garanhao_especiais.mp4 --p1 gutto
   --golpes 4800:300:150,4810:300:120,4820:200:120,4830:60:120,4900:200:330 --segundos 30 --fotos <pasta>`.
   Pontos a conferir no vídeo: 4816 (investida depois de aguentar) recomeça a anim 4810 do quadro 0; altura das chamas.
6. Comentar na #47, juntar na mugen, avisar o Alisson.

## Depois
- Levanta e Arremessa: garra só um pouco acima da cabeça (ver conferencia-parte4.md); refazer a pose do erguer.
- Passar `pele_pecas.py` (PELE=True) nos kits do firme (ck_e, garanhao_47) para sumir a linha de corte.
- Resto dos golpes novos do Pengaró e do CK despertados (docs/despertados-47/golpes-novos.md).
