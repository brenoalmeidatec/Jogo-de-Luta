# Hazak nítido (issue #36)

Pedido do Breno (2026-11-15): refazer a forma base do Hazak porque continuava borrada, sem mudar desenho, cor, pose,
golpes, efeitos, caixas, `.air` ou `.cns`. O Diabo Loiro fica como está.

## Como foi feito

1. **Folhas novas** (`sprites/hazaki/quadros/folhas_novas/`, 64 folhas, 1536x1024, grade 4x2, boneco até ~500 px):
   geradas no ChatGPT a partir da folha de hoje (anexos em `anexos/`, pedidos em `fila.json`, montados por
   `ferramentas/fila_hazak_nitido.py`). 11 folhas levaram o conserto de anatomia da #51 (braço, perna e tronco no
   tamanho normal). Os ajudantes da página do ChatGPT estão em `ferramentas/chatgpt_grade.js`; `montar_grade.py` junta
   as duas metades capturadas.
2. **Conversão direta** (`ferramentas/converter_hazaki.py`, como o `converter_pengaro.py`, sem `hd_guiado.py`):
   escala por folha (mediana contra os desenhos de antes, commit `6e7ff73a`), posição por quadro pelo encaixe da
   silhueta, cor de cada grupo (pele, gi, debrum, faixa, atadura, munhequeira) levada para a de antes e pintura com
   `sprites/hazaki/paleta_nitida.json` (as 15 cores do Hazak + 25 tons do meio). Sai em 1x e 3x da mesma folha.
   O parry (que não tinha quadros de antes) usa como régua o corte velho do `parry.py`, e o `parry.py` agora lê os
   quadros 3x do Hazak como já fazia com o Pengaró.
3. **Caixas iguais**: o gerador mede a caixa de dano no desenho, e o desenho novo mudaria ~1900 caixas.
   `ferramentas/manter_caixas.py` devolve, quadro por quadro, as caixas de `sprites/hazaki/caixas_base.air` (o `.air`
   da mugen antes desta troca). No `.air` só mudam os números dos sprites; no `.cns` só o que é visual e medido no
   desenho (aura presa ao corpo, ponto da faísca, tabela de gêmeos do Diabo).

## Conferência

- `python3 ferramentas/converter_hazaki.py --contato PASTA`: antes (em cima) e depois (embaixo) de cada folha.
- `corpo_lado_a_lado.png` e `rosto_lado_a_lado.png`: CK, Hazak antes e Hazak depois, 1280x720.
- Robô: `python3 ferramentas/testar_pengaro.py --linux --lutador hazaki`.

## Para mexer depois

Pose com defeito: gere só aquela folha de novo (mesmo anexo e pedido do `fila.json`), rode
`python3 ferramentas/converter_hazaki.py <folha>` e `python3 ferramentas/gerar_hazaki.py`. Se um dia as caixas
tiverem de mudar de propósito, atualize `caixas_base.air` com `python3 ferramentas/manter_caixas.py hazaki --guardar <commit>`.
