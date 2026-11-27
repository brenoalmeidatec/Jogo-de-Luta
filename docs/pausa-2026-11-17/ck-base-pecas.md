# Pausa 17/11: CK base no boneco de peças

## O que foi feito (na mugen)
- 1ª e 2ª levas: parado, jab, cruzado (direto com o braço de trás), chutes, agachar, soco agachado, rasteira, uppercut,
  levanta comédia, overhand, Bote, entrada do agarrão (800), soco no ar e voadoras.
- 3ª leva (este commit): andar (20/21/100), pulo (40-47), defesa (105-152), apanha em pé e agachado (5000-5035, 5300),
  queda (5040-5170), levanta (5120), rolamento (700/705), armada (1300/1301/1310), compasso (201), provoca (195),
  vitória (181) e derrota (170). São 87 ações e 667 desenhos.
- **Quadro especial** (regra de criação, seção 8): deitado, sentado, de costas e braço caído/aberto ficam com o desenho
  de hoje, que já usa as mesmas 16 cores do kit. A lista está em `ESPECIAIS` no `ferramentas/pecas_ck.py`. Isso é dívida.
- Robô de peças: **0 defeitos em 778 desenhos**. Robô de luta: **226/226** com o dano idêntico ao de antes.

## Onde parou
- O vídeo lado a lado da 3ª leva não foi gerado (a pausa interrompeu). Para gerar: `python3 ferramentas/pecas_ck.py video`
  (leva mais de 10 minutos).

## Próximos passos exatos
1. Gerar o vídeo e conferir tick a tick os golpes novos: apanha (inclinação para trás), pulo, armada e compasso.
2. Pagar a dívida dos quadros especiais: recortar variantes de braço (caído, punho erguido, mão no boné, mão aberta)
   das folhas armada/02, vitoria/07, vitoria/01 e provoca/05, como foi feito com `VARIANTES` (jab, direto, alto,
   overhand), e tirar esses quadros do `ESPECIAIS`. O deitado e o sentado pedem um kit de lado (como o `hazak_lado.py`).
3. Agarrão completo (830/831/840/841): o .air mistura desenhos da vítima (grupos 7820/7810), então precisa de uma
   folha própria de quem agarra.
4. Não feitos: lata (190/191), golaço (3000/3100), rasteirinha (430/1500), bola (1000/3402), boné voador (1600-1602)
   e os combos 301-349 e 3400-3436.

## Como religar depois de juntar a mugen
Se chars/ck der conflito, pegue `chars/ck/` inteiro da mugen (inclusive o .cns), rode `python3 ferramentas/ligar_pecas.py ck`
e depois `python3 ferramentas/testar_pengaro.py --linux --lutador ck`. O resultado tem que dar 226/226.
