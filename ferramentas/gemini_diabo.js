// Ajudantes do Gemini para as folhas do Diabo (#44). Cole no console (pela ferramenta javascript do Chrome).
//
// 1) Numa aba example.com (o Gemini bloqueia imagem de fora pelo CSP): __monta4('cutucao', 0) mostra a fileira 0
//    (ou 1) da folha do Hazak à esquerda e a figura do conceito à direita. Tire um print da aba INTEIRA na escala 1
//    e suba no file-input escondido do Gemini (upload_image com a ref; aparece depois de abrir "Envio e ferramentas").
// 2) Prompt: python3 ferramentas/diabo_proprio.py --fileira NOME
// 3) Na aba do Gemini, quando a imagem chegar: __gcap() põe a imagem em tamanho real no canto (1 px da imagem =
//    1 px do aparelho); dê zoom na região (0, 0, largura/dpr, altura/dpr) em coordenadas do print e recorte no tamanho
//    natural que o __gcap devolve. Depois: diabo_proprio.py --juntar NOME a.png b.png
window.__monta4 = async (n, row) => {
  const B = 'https://raw.githubusercontent.com/brenoalmeidatec/Jogo-de-Luta/7866d354/docs/diabo-44/anexos/';
  document.body.innerHTML = '';
  document.body.style.cssText = 'margin:0;background:#fff;overflow:hidden';
  const W = innerWidth, H = innerHeight;
  const fw = Math.min(W - 420, H * 3), fh = fw / 3;
  const box1 = document.createElement('div');
  box1.style.cssText = `position:fixed;left:0;top:${(H - fh) / 2}px;width:${fw}px;height:${fh}px;overflow:hidden`;
  const f = new Image(); f.src = B + n + '.jpg';
  f.style.cssText = `position:absolute;left:0;top:${-row * fh}px;width:${fw}px;height:${fh * 2}px;max-width:none`;
  box1.appendChild(f);
  const sc = H / 724, cw = 2172 * 0.18;
  const box = document.createElement('div');
  box.style.cssText = `position:fixed;top:0;left:${fw + 16}px;width:${cw * sc}px;height:${H}px;overflow:hidden`;
  const c = new Image(); c.src = B + 'conceito.jpg';
  c.style.cssText = `position:absolute;left:0;top:0;height:${H}px;width:${2172 * sc}px;max-width:none`;
  box.appendChild(c);
  document.body.append(box1, box);
  await f.decode(); await c.decode();
  return [W, H, Math.round(fw), Math.round(fh), Math.round(cw * sc)].join(' ');
};

window.__gcap = function () {
  document.getElementById('__gc')?.remove();
  const s = [...document.querySelectorAll('img')].filter(i => i.src.includes('googleusercontent') && i.naturalWidth > 500).pop();
  const d = document.createElement('div');
  d.id = '__gc';
  d.style.cssText = 'position:fixed;left:0;top:0;z-index:999999;background:#fff';
  const i = document.createElement('img');
  i.src = s.src;
  i.style.cssText = `width:${s.naturalWidth / devicePixelRatio}px;height:${s.naturalHeight / devicePixelRatio}px;image-rendering:pixelated;display:block`;
  d.appendChild(i);
  document.body.appendChild(d);
  return [s.naturalWidth, s.naturalHeight];
};
