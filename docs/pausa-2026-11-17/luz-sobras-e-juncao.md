# Pausa 2026-11-17: sobras da luz e energia juntando na mão (#51 item 2)

**Pedido:** o Alisson aprovou a luz nos efeitos (mugen 4a973a2e) e pediu tudo da lista de sobras e a aura juntando na mão
antes do especial. **Onde está:** branch `claude/project-thread-cgrwa2`, **NÃO juntado na `mugen`** (a 2ª conferência
quadro a quadro não terminou). Robôs de luta passaram na 1ª versão: Hazak 284/0, Gutto 186/0, Pengaró 189/0, CK 226/0,
Raiclaven 216/0. Nenhum desenho dos lutadores muda (conferido pixel a pixel).

## Feito (detalhes em `docs/auras-51/LEIA-ME.md`, sétima volta)

- `ferramentas/luz_junta.py` (novo): fagulhas + anel + miolo branco entrando no ponto de onde o poder nasce, nos 22
  tiques antes de cada Projectile que brilha. Chamado no fim do `luz.aplicar`.
- `luz.assar_feixes`: o raio leva a luz do contorno assada numa cópia da ação dele (ações 9780+, grupo 9729), com
  `projanim = 9780 ; luz assada de <ação>`. Motivo: o Explod irmão não para quando o Projectile para no acerto, e no
  raio do KO a luz corria na frente e virava névoa (achado da 1ª conferência).
- Orbe da boca só no raio parado (era a mancha rosa no casco do Gutto); clarão do golpe com miolo branco (CK e Gutto);
  borda fraca da luz zerada (`CORTE`, pontinhos no escuro do CK); `filmar_aura_corpo.py` loga `9660 junta`.

## Próximos passos exatos

1. `git checkout claude/project-thread-cgrwa2 && git merge origin/mugen` (se a mugen andou e mexeu em chars dos 5,
   pegue os chars da mugen e rode `python3 -c "import luz; [luz.aplicar(l) for l in luz.LIGADOS]"` em `ferramentas/`).
2. Filmar: script do scratchpad não existe mais; usar `filmar_aura_corpo.filmar(l, saida, extra=[(170,3400),(965,4750),(467,200)])`
   (Hazak: 1600 e 1650; CK: 3000 e 4750) e montar antes/agora lado a lado.
3. Conferir quadro a quadro: (a) a luz do raio do KO de Gutto/Pengaró/Hazak não pode virar névoa nem correr na frente;
   (b) a junção aparece antes do poder (no Gutto o 3400 é o sopro de fogo; ela estava apagada em cima da aura vermelha
   e foi reforçada com cabeça branca e anel, ainda não filmada).
4. Robôs `testar_pengaro.py --linux --lutador <l>` nos 5; se tudo OK, ff na `mugen`, comentar na #51 com os vídeos.

Fora do pedido, para depois: Gbzin ainda não está em `luz.LIGADOS` (precisa da revisão do que acende em `luz_classes.json`).
