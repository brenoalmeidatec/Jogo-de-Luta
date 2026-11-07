// Ajudantes para gerar folhas no ChatGPT pelo navegador embutido. Veja docs/como-trabalhar.md.
// Rode este arquivo na página do chat. Eles somem se a aba recarregar.
(() => {
  const espera = ms => new Promise(r => setTimeout(r, ms));
  const gerando = () => !!document.querySelector('[data-testid=stop-button],button[aria-label*="Parar"]');
  const aperta = el => {
    const r = el.getBoundingClientRect();
    const o = { bubbles: true, cancelable: true, clientX: r.x + r.width / 2, clientY: r.y + r.height / 2, button: 0, pointerType: 'mouse' };
    el.dispatchEvent(new PointerEvent('pointerdown', o));
    el.dispatchEvent(new MouseEvent('mousedown', o));
    el.dispatchEvent(new PointerEvent('pointerup', o));
    el.dispatchEvent(new MouseEvent('mouseup', o));
    el.click();
  };
  const busca = () => document.querySelector('input[placeholder*="biblioteca" i]');
  window.__f = window.__f || {};
  window.__w = () => new Promise(r => setTimeout(() => r('espera'), 40000));

  // Anexa a referência da biblioteca: __a('Oito Movimentos', 'Sprite de Lutador Demon')
  window.__a = async (termo, inicioDoTitulo) => {
    if (!busca()) {
      aperta(document.querySelector('button[aria-label="Adicionar arquivos e mais"]'));
      await espera(1000);
      const item = [...document.querySelectorAll('*')].filter(e => e.textContent.trim() === 'Adicionar da biblioteca' && e.children.length <= 2).pop();
      if (!item) return 'sem item biblioteca';
      aperta(item.closest('[role=menuitem]') || item);
      await espera(2200);
    }
    const campo = busca();
    if (!campo) return 'sem busca';
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(campo, termo);
    campo.dispatchEvent(new Event('input', { bubbles: true }));
    await espera(2800);
    const linha = document.querySelector(`button[aria-label^="${inicioDoTitulo}"]`);
    if (!linha) return 'sem linha';
    linha.click();
    await espera(900);
    const add = [...document.querySelectorAll('button')].find(b => b.textContent.trim() === 'Adicionar ao chat');
    if (!add) return 'sem botao adicionar';
    add.click();
    await espera(2500);
    return 'anexou';
  };

  // Envia o prompt.
  window.__e = async texto => {
    const caixa = document.querySelector('[contenteditable=true]');
    caixa.focus();
    document.execCommand('insertText', false, texto);
    await espera(1200);
    const enviar = document.querySelector('[data-testid=send-button]') || document.querySelector('button[aria-label="Enviar"]');
    if (!enviar) return 'sem enviar';
    enviar.click();
    await espera(800);
    return 'enviou';
  };

  // Guarda na memória da página a última imagem gerada, com o nome da folha.
  window.__s = async nome => {
    if (gerando()) return `${nome}: AINDA GERANDO`;
    const fim = (document.querySelector('main')?.innerText || '').slice(-260);
    if (/falhou|couldn.t generate/i.test(fim)) return `${nome}: FALHOU`;
    const img = [...document.images].filter(i => /gerada/i.test(i.alt)).pop();
    if (!img) return `${nome}: SEM IMAGEM`;
    if (window.__u === img.src) return `${nome}: MESMA IMAGEM`;
    window.__u = img.src;
    const c = document.createElement('canvas');
    c.width = img.naturalWidth;
    c.height = img.naturalHeight;
    c.getContext('2d').drawImage(img, 0, 0);
    window.__f[nome] = await new Promise(r => c.toBlob(r, 'image/png'));
    return `${nome} ok ${c.width}x${c.height} total ${Object.keys(window.__f).length}`;
  };

  // Espera até 38 s a geração acabar e guarda.
  window.__sx = async nome => {
    const inicio = Date.now();
    while (gerando() && Date.now() - inicio < 38000) await espera(2000);
    await espera(1000);
    return window.__s(nome);
  };

  // Baixa tudo o que está guardado num .tar só.
  window.__pacote = async () => {
    const enc = new TextEncoder();
    const partes = [];
    for (const nome of Object.keys(window.__f)) {
      const dados = new Uint8Array(await window.__f[nome].arrayBuffer());
      const h = new Uint8Array(512);
      const poe = (s, o) => h.set(enc.encode(s), o);
      poe(`${nome}.png`, 0);
      poe('0000644\0', 100);
      poe('0000000\0', 108);
      poe('0000000\0', 116);
      poe(`${dados.length.toString(8).padStart(11, '0')}\0`, 124);
      poe('00000000000\0', 136);
      poe('        ', 148);
      poe('0', 156);
      poe('ustar\0', 257);
      poe('00', 263);
      let soma = 0;
      for (const b of h) soma += b;
      poe(`${soma.toString(8).padStart(6, '0')}\0 `, 148);
      partes.push(h, dados);
      const resto = (512 - dados.length % 512) % 512;
      if (resto) partes.push(new Uint8Array(resto));
    }
    partes.push(new Uint8Array(1024));
    const pacote = new Blob(partes, { type: 'application/x-tar' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(pacote);
    a.download = 'folhas.tar';
    document.body.appendChild(a);
    a.click();
    a.remove();
    return { folhas: Object.keys(window.__f).length, bytes: pacote.size };
  };
  return 'ajudantes prontos';
})();
