(() => {
  const clamp = (n, min = 0, max = 1) => Math.max(min, Math.min(max, n));
  const menuButton = document.querySelector('.menu-toggle');
  const menu = document.querySelector('.main-nav');
  menuButton?.addEventListener('click', () => {
    const open = menu.classList.toggle('open');
    menuButton.setAttribute('aria-expanded', String(open));
  });
  menu?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    menu.classList.remove('open'); menuButton?.setAttribute('aria-expanded', 'false');
  }));

  const heroTrack = document.querySelector('.hero-track');
  const heroCopy = document.querySelector('.hero-copy');
  const heroImage = document.querySelector('.hero-image');
  const scrim = document.querySelector('.hero-scrim');
  const dark = document.querySelector('.hero-dark');
  const workshop = document.querySelector('.workshop-panel');
  const hint = document.querySelector('.scroll-hint');
  const engineering = document.querySelector('.engineering-track');
  const panels = [...document.querySelectorAll('.spec-panel')];
  const dots = [...document.querySelectorAll('.model-dots i')];
  const modelLink = document.querySelector('#model-link');
  const families = ['pipetas', 'conectores', 'postes'];
  const mobileModels = [
    { family: 'Familia 01 · Pipetas', name: 'Pipeta Chapetón', code: 'HRD 1101', labels: ['Vidrio 8–12 mm', 'Acero T-304', 'Salida 28 mm'] },
    { family: 'Familia 02 · Conectores', name: 'Conector 44 × 40 mm', code: 'HRD 1303', labels: ['Diámetro 44 mm', 'Cuerpo 40 mm', 'Tapa 10 mm'] },
    { family: 'Familia 03 · Postes', name: 'Mini Poste con tope', code: 'HRD 1206 × 450', labels: ['Altura 450 mm', 'Ranura 300 mm', 'Base 100 × 100 mm'] }
  ];
  let lastFamily = -1;

  function updateScroll() {
    if (heroTrack) {
      const mobile = innerWidth <= 900;
      const headerHeight = mobile ? 72 : 82;
      const max = heroTrack.offsetHeight - innerHeight + headerHeight;
      const p = clamp((headerHeight - heroTrack.getBoundingClientRect().top) / Math.max(max, 1));
      heroCopy.style.opacity = String(clamp(1 - p * 2.4));
      heroCopy.style.transform = `translateY(${-p * (mobile ? 34 : 55)}px)`;
      heroImage.style.transform = `translateY(${-p * (mobile ? 22 : 0)}px) scale(${1 + p * (mobile ? .11 : .08)})`;
      scrim.style.opacity = String(clamp(1 - p * (mobile ? 1.45 : 1.7)));
      dark.style.opacity = String(clamp((p - (mobile ? .18 : .22)) * (mobile ? 2.1 : 1.8)));
      workshop.style.opacity = String(clamp((p - (mobile ? .42 : .48)) * (mobile ? 3.2 : 2.8)));
      workshop.style.transform = `translateY(${(1 - clamp((p - (mobile ? .4 : .45)) * 2.5)) * (mobile ? 28 : 38)}px)`;
      if (hint) hint.style.opacity = String(clamp(1 - p * 5));
    }
    if (engineering) {
      const rect = engineering.getBoundingClientRect();
      const p = clamp(-rect.top / Math.max(engineering.offsetHeight - innerHeight, 1));
      const idx = Math.min(2, Math.floor(p * 3));
      document.documentElement.style.setProperty('--technical-progress', `${p * 100}%`);
      const mobileHint = document.querySelector('#mobile-scroll-hint');
      if (mobileHint) mobileHint.style.opacity = String(clamp(1 - p * 10));
      if (idx !== lastFamily) {
        panels.forEach((el, i) => el.classList.toggle('active', i === idx));
        dots.forEach((el, i) => el.classList.toggle('active', i === idx));
        if (modelLink) modelLink.href = `#${families[idx]}`;
        const model = mobileModels[idx];
        const techUI = document.querySelector('.mobile-tech-ui');
        if (techUI && model) {
          document.querySelector('#mobile-family').textContent = model.family;
          document.querySelector('#mobile-model').textContent = model.name;
          document.querySelector('#mobile-code').textContent = model.code;
          document.querySelector('#mobile-step').textContent = `0${idx + 1}`;
          model.labels.forEach((label, i) => { document.querySelector(`#callout-${['one','two','three'][i]}`).textContent = label; });
          techUI.classList.remove('tech-enter'); void techUI.offsetWidth; techUI.classList.add('tech-enter');
        }
        lastFamily = idx;
      }
    }
  }
  addEventListener('scroll', updateScroll, { passive: true });
  addEventListener('resize', updateScroll); updateScroll();

  const labels = {
    pipetas: ['Pipetas', 'Conectores cilíndricos para vidrio-muro y vidrio-vidrio, en versiones chapetón, avellanado, allen y ajustable.'],
    postes: ['Postes', 'Mini postes sólidos, huecos, rectangulares y de solera, con placa base barrenada y versiones con tope.'],
    conectores: ['Conectores', 'Botones y conectores para vidrio-muro y vidrio-vidrio, fabricados para distintos espesores y configuraciones.'],
    jaladeras: ['Jaladeras', 'Jaladeras tubulares de acero inoxidable para puertas de cristal templado.']
  };
  const escapeHTML = value => String(value ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  const productDialog = document.querySelector('#product-dialog');
  let catalogDetails = [];
  const productSlug = code => String(code).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  const openProduct = product => {
    if (!product || !productDialog) return;
    document.querySelector('#dialog-category').textContent = `${product.category} · ${product.code}`;
    document.querySelector('#product-dialog-title').textContent = product.name;
    document.querySelector('#dialog-description').textContent = product.description;
    document.querySelector('#dialog-specs').innerHTML = product.specifications.map(spec => `<li>${escapeHTML(spec)}</li>`).join('');
    const images = product.detailImages.length ? product.detailImages : [`/content/catalog/${product.image}`];
    document.querySelector('#dialog-gallery').innerHTML = images.map((src, index) => `<figure class="${index === 0 ? 'primary' : ''}"><img src="${escapeHTML(src)}" alt="${escapeHTML(product.name)} ${index ? 'plano o detalle técnico' : ''}" loading="eager"></figure>`).join('');
    const message = encodeURIComponent(`Hola Herraidea, me interesa cotizar ${product.code} — ${product.name}.`);
    document.querySelector('#dialog-whatsapp').href = `https://wa.me/524772561695?text=${message}`;
    const url = new URL(location.href); url.searchParams.set('producto', productSlug(product.code));
    history.pushState({ product: product.code }, '', url);
    productDialog.showModal(); document.body.classList.add('dialog-open');
  };
  const closeProduct = (updateUrl = true) => {
    if (!productDialog?.open) return;
    productDialog.close(); document.body.classList.remove('dialog-open');
    if (updateUrl) { const url = new URL(location.href); url.searchParams.delete('producto'); history.pushState({}, '', url); }
  };
  document.querySelector('.dialog-close')?.addEventListener('click', () => closeProduct());
  productDialog?.addEventListener('click', event => { if (event.target === productDialog) closeProduct(); });
  productDialog?.addEventListener('cancel', event => { event.preventDefault(); closeProduct(); });
  document.querySelector('#dialog-share')?.addEventListener('click', async event => {
    try { await navigator.clipboard.writeText(location.href); event.currentTarget.textContent = 'Enlace copiado'; }
    catch { event.currentTarget.textContent = 'Copia la URL del navegador'; }
  });
  addEventListener('popstate', () => closeProduct(false));

  fetch('/content/catalog/details.json').then(r => {
    if (!r.ok) throw new Error('No se pudo cargar el catálogo');
    return r.json();
  }).then(products => {
    catalogDetails = products;
    const host = document.querySelector('#catalog-families');
    const order = ['pipetas', 'postes', 'conectores', 'jaladeras'];
    host.innerHTML = order.map(key => {
      const items = products.filter(p => String(p.category).toLowerCase() === key);
      const [title, description] = labels[key];
      return `<section class="family" id="${key}"><div class="family-header"><div><span class="eyebrow">${items.length} modelos</span><h3>${title}</h3></div><p>${description}</p></div><div class="product-grid">${items.map(p => {
        const code = escapeHTML(p.code || p.model || '');
        const name = escapeHTML(p.name);
        return `<button class="product-card" type="button" data-product="${escapeHTML(p.code)}" aria-label="Ver ficha de ${name} ${code}"><figure><img src="/content/catalog/${escapeHTML(p.image)}" alt="${name} ${code}" loading="lazy"></figure><div class="product-info"><b>${code}</b><span>${name}</span><em>Ver ficha técnica →</em></div></button>`;
      }).join('')}</div></section>`;
    }).join('');
    host.querySelectorAll('[data-product]').forEach(card => card.addEventListener('click', () => openProduct(catalogDetails.find(p => p.code === card.dataset.product))));
    const requested = new URL(location.href).searchParams.get('producto');
    if (requested) openProduct(catalogDetails.find(p => productSlug(p.code) === requested));
  }).catch(err => {
    document.querySelector('#catalog-families').innerHTML = `<p>${escapeHTML(err.message)}. Escríbenos por WhatsApp para recibirlo.</p>`;
  });

  document.querySelector('#contact-form')?.addEventListener('submit', event => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const lines = ['Hola Herraidea, quiero solicitar información:', `Nombre: ${data.get('nombre')}`];
    for (const [key, label] of [['email','Correo'],['whatsapp','WhatsApp'],['tipo','Proyecto'],['modelos','Modelos'],['mensaje','Mensaje']]) {
      const value = String(data.get(key) || '').trim(); if (value) lines.push(`${label}: ${value}`);
    }
    window.open(`https://wa.me/524772561695?text=${encodeURIComponent(lines.join('\n'))}`, '_blank', 'noopener');
  });
})();
