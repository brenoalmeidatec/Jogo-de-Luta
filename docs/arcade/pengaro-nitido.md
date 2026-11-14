# Pengaró nítido com o desenho de antes (Alisson, 2026-11-14)

Missão de [`../missao-alisson-2026-11-13.md`](../missao-alisson-2026-11-13.md), item 1. O Breno não gostou do
redesenho de 2026-11-13 (commit `dc3427bf`, 34 folhas novas). Ele quer o Pengaró **com o desenho de antes**, só que
nítido como o CK e o Gutto, e com a pele bem escura. O endiabrado não muda.

## O que foi feito

1. **Revert do `dc3427bf`** (`git revert`): voltaram `quadros_arcade/`, `quadros_arcade_hd/`, o `.air`, o `.sff` e o
   `gerar_pengaro.py` de antes, e saíram as `folhas_novas/` e o `converter_pengaro.py`. O gerador reproduz o `.sff`
   do `965f8013` (só os retratos novos mudam, pelo `trocar_retratos.py`).
2. **A causa do borrado**, medida: nas folhas antigas (`quadros/folhas_arcade/`, 2172x724) o Pengaró tem **~275 px**
   de altura; o CK, na folha dele do mesmo tamanho, **~550 px**. O 3x do jogo pede ~330 px. Então o CK era
   **reduzido** (nítido) e o Pengaró **ampliado** 1,2x. Em cima disso, o `hd_guiado.py` repintava cada pixel 3x só
   com as cores do 1x numa vizinhança 3x3, e o olho, a boca e o contorno do rosto sumiam.
3. **Folhas ampliadas sem redesenhar** (`ferramentas/ampliar_folhas.py`): cada folha antiga passa pelo Real-ESRGAN
   (modelo `RealESRGAN_x4plus_anime_6B`, licença BSD-3) em 4x e é reduzida para 2x. Fica em
   `quadros/folhas_arcade_sr/`: o mesmo desenho, as mesmas poses e cores, com o boneco do tamanho do CK (~550 px).
   - Os pesos (17 MB) e o `torch` ficam fora do git: `pip install torch spandrel` e baixe o `.pth` dos releases de
     `github.com/xinntao/Real-ESRGAN` (v0.2.2.4).
4. **3x direto da folha ampliada** (`ferramentas/nitidez_pengaro.py`): o quadro 1x continua a autoridade (posição,
   escala, caixas e paleta não mudam). O script acha em que escala e posição a figura foi colada no 1x (a mesma conta
   do `hd_guiado`), cola a figura da folha ampliada **reduzida** para 3x e pinta cada pixel com a cor do 1x mais
   perto em Lab numa vizinhança 5x5 (antes 3x3). O 3x continua com as 15 cores e os papéis do 1x, mas com olho,
   boca, dedos e contorno.
5. **Pele bem escura** (pedido de `pengaro.md`): troca de cor, sem redesenhar. As 5 cores de pele viram as da
   proposta (`#3A1416`, `#47201A`, `#723F1E`, `#A2753E`, `#D9A066`) no 1x, no 3x e nos quadros do meio usados.
   - **A garrafa usa as mesmas cores** no vidro e no rótulo. O script acha o rótulo em cada quadro (mancha clara
     compacta cercada de vidro escuro, perto da cor da garrafa, na posição de sempre da folha) e poupa a garrafa.
     Conferido quadro a quadro nas 34 folhas; os 22 quadros em que a regra errava ficaram corrigidos à mão em
     `GARRAFA_MAO`.
   - As 5 cores novas entraram na paleta fixa `paleta_sff.act` nas linhas de menos uso (`LINHAS_ACT`); os poucos
     pixels de efeito que usavam essas linhas foram para a cor vizinha quase igual.
   - **O endiabrado (`e_*`), a aura e os efeitos não foram tocados.**

## Como refazer

```bash
python ferramentas/ampliar_folhas.py CAMINHO/RealESRGAN_x4plus_anime_6B.pth     # ~1,5 min por folha na CPU
python ferramentas/nitidez_pengaro.py
python ferramentas/gerar_pengaro.py
python ferramentas/trocar_retratos.py pengaro
python ferramentas/nitidez_pengaro.py --contato PASTA   # folhas de contato do 3x, para olhar
```

O `nitidez_pengaro.py` pode rodar de novo: ele clareia o 1x antes de casar com a folha e escurece de novo no fim.

## O que não mudou e o que ficou

- `.air`, `.cns` e `.cmd`: iguais ao gerado antes (só pixels mudam). Caixas, alcance e frame data, iguais.
- **Ficaram em 1x ampliado** (como antes): os quadros do meio do Blender que o gerador usa (`m_*`), o `f_agarrao4/5`
  (montado por código) e a cena do Despertar (`despertar_a`, arte antiga).
- **Despertar (`despertar_a`)**: arte antiga, de outra paleta, com a pele um pouco mais clara. Não foi recolorida.
- **Rosto parecido com a foto**: não mexi no rosto (o pedido era não mudar o desenho). Se o Breno quiser, é um
  retoque à mão nas folhas ampliadas, que agora têm resolução para isso.
