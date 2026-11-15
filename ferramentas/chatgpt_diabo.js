// Ajudantes das folhas próprias do Diabo Loiro (#44) para a aba do ChatGPT (cópia do chatgpt_grade.js do #36 com DOIS
// anexos: a folha nítida do Hazak e o conceito). Somem se a aba recarregar: cole de novo.
// O pedido de cada folha vem do docs/diabo-44/fila.json: __fila() carrega (ou ponha window.__pedidos à mão, o fetch pode ser
// barrado), __anexa(nome) anexa, __envia(nome) envia, __pronta() espera. Captura em 4 quartos de 768x512 (__cap4(0..3) e
// zoom de 768/dpr x 512/dpr px no canto), que cabem em tela baixa.
// Uma folha por lote: __pronta(), __cap2(0), zoom [0,0,490,637] salvo em disco, __cap2(1), zoom, __cap2(-1),
// __anexa(proxima), espera 5 s, __envia(conserto). Depois: python ferramentas/montar_grade.py <folha> ESQ.png DIR.png
(() => {
  const espera = ms => new Promise(r => setTimeout(r, ms));
  const BASE = 'https://raw.githubusercontent.com/brenoalmeidatec/Jogo-de-Luta/COMMIT/docs/diabo-44/';
  window.__ult = () => [...document.images].filter(i => /gerada|generated/i.test(i.alt)).pop();

  const arquivo = async n => {
    const im = new Image();
    im.crossOrigin = 'anonymous';
    im.src = BASE + 'anexos/' + n + '.jpg';
    await im.decode();
    const c = document.createElement('canvas');
    c.width = im.naturalWidth;
    c.height = im.naturalHeight;
    c.getContext('2d').drawImage(im, 0, 0);
    const blob = await new Promise(r => c.toBlob(r, 'image/png'));
    return new File([blob], n + '.png', { type: 'image/png' });
  };

  // Pedidos da fila (docs/diabo-44/fila.json), por folha sem o "d_".
  window.__fila = async () => {
    const r = await fetch(BASE + 'fila.json');
    window.__pedidos = Object.fromEntries((await r.json()).map(p => [p.folha.slice(2), p.prompt]));
    return Object.keys(window.__pedidos).length + ' pedidos';
  };

  // Anexa a folha nítida do Hazak (1º) e o conceito (2º).
  window.__anexa = async n => {
    const dt = new DataTransfer();
    dt.items.add(await arquivo(n));
    dt.items.add(await arquivo('conceito'));
    const inp = [...document.querySelectorAll('input[type=file]')].find(i => /image/.test(i.accept || '')) || document.querySelector('input[type=file]');
    inp.files = dt.files;
    inp.dispatchEvent(new Event('change', { bubbles: true }));
    return n + ' + conceito';
  };

  // Escreve o pedido da folha n (mais um conserto, se houver) e envia.
  window.__envia = async (n, extra) => {
    await espera(3500);
    const caixa = document.querySelector('[contenteditable=true]');
    caixa.focus();
    document.execCommand('insertText', false, window.__pedidos[n] + (extra ? ' ' + extra : ''));
    await espera(1500);
    const u = window.__ult();
    window.__src0 = u ? u.src : '';
    const b = document.querySelector('[data-testid=send-button]') || document.querySelector('button[aria-label="Enviar"]');
    if (!b || b.disabled) throw new Error('sem botao enviar');
    b.click();
    return 'enviou';
  };

  // Espera até 40 s a imagem nova chegar.
  window.__pronta = async () => {
    const t0 = Date.now();
    while (Date.now() - t0 < 40000) {
      const u = window.__ult();
      if (!document.querySelector('[data-testid=stop-button]') && u && u.src !== window.__src0 && u.complete && u.naturalWidth > 0) return 'pronta ' + u.naturalWidth + 'x' + u.naturalHeight;
      await espera(2000);
    }
    return 'ainda: ' + (document.querySelector('main')?.innerText || '').slice(-300).replace(/\s+/g, ' ');
  };

  // Mostra a metade n (0 esquerda, 1 direita) da imagem nova no canto da tela, 1 pixel da imagem = 1 pixel da tela,
  // com preto em volta, para o zoom do navegador salvar sem reduzir. -1 tira.
  window.__cap2 = n => {
    document.getElementById('__cap')?.remove();
    if (n < 0) return 'limpo';
    const u = window.__ult();
    if (!u || u.src === window.__src0 || document.querySelector('[data-testid=stop-button]')) throw new Error('imagem nova ainda nao chegou');
    if (u.naturalWidth !== 1536 || u.naturalHeight !== 1024) throw new Error('tamanho ' + u.naturalWidth + 'x' + u.naturalHeight);
    const dpr = devicePixelRatio;
    const d = document.createElement('div');
    d.id = '__cap';
    d.style.cssText = 'position:fixed;left:0;top:0;width:100vw;height:100vh;background:#000;z-index:2147483647';
    const c = document.createElement('div');
    c.style.cssText = `position:absolute;left:0;top:0;overflow:hidden;width:${u.naturalWidth / 2 / dpr}px;height:${u.naturalHeight / dpr}px`;
    const im = document.createElement('img');
    im.src = u.src;
    im.style.cssText = `position:absolute;left:${-n * u.naturalWidth / 2 / dpr}px;top:0;width:${u.naturalWidth / dpr}px;height:${u.naturalHeight / dpr}px;max-width:none;image-rendering:pixelated`;
    c.appendChild(im);
    d.appendChild(c);
    document.body.appendChild(d);
    return [u.naturalWidth, u.naturalHeight, n].join(' ');
  };
  // Quarto n (0 e 1 em cima, 2 e 3 embaixo) da imagem nova, 1 pixel da imagem = 1 pixel da tela: cabe em tela baixa.
  window.__cap4 = n => {
    document.getElementById('__cap')?.remove();
    if (n < 0) return 'limpo';
    const u = window.__ult();
    if (!u || u.src === window.__src0 || document.querySelector('[data-testid=stop-button]')) throw new Error('imagem nova ainda nao chegou');
    if (u.naturalWidth !== 1536 || u.naturalHeight !== 1024) throw new Error('tamanho ' + u.naturalWidth + 'x' + u.naturalHeight);
    const dpr = devicePixelRatio, cx = n % 2, cy = Math.floor(n / 2);
    const d = document.createElement('div');
    d.id = '__cap';
    d.style.cssText = 'position:fixed;left:0;top:0;width:100vw;height:100vh;background:#000;z-index:2147483647';
    const c = document.createElement('div');
    c.style.cssText = `position:absolute;left:0;top:0;overflow:hidden;width:${768 / dpr}px;height:${512 / dpr}px`;
    const im = document.createElement('img');
    im.src = u.src;
    im.style.cssText = `position:absolute;left:${-cx * 768 / dpr}px;top:${-cy * 512 / dpr}px;width:${1536 / dpr}px;height:${1024 / dpr}px;max-width:none;image-rendering:pixelated`;
    c.appendChild(im);
    d.appendChild(c);
    document.body.appendChild(d);
    return [u.naturalWidth, u.naturalHeight, n].join(' ');
  };
  return 'ajudantes prontos';
})();
