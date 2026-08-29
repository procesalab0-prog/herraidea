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
  let lastFamily = -1;

  function updateScroll() {
    if (innerWidth > 900 && heroTrack) {
      const max = heroTrack.offsetHeight - innerHeight + 82;
      const p = clamp(-heroTrack.getBoundingClientRect().top / Math.max(max, 1));
      heroCopy.style.opacity = String(clamp(1 - p * 2.4));
      heroCopy.style.transform = `translateY(${-p * 55}px)`;
      heroImage.style.transform = `scale(${1 + p * .08})`;
      scrim.style.opacity = String(clamp(1 - p * 1.7));
      dark.style.opacity = String(clamp((p - .22) * 1.8));
      workshop.style.opacity = String(clamp((p - .48) * 2.8));
      workshop.style.transform = `translateY(${(1 - clamp((p - .45) * 2.5)) * 38}px)`;
      hint.style.opacity = String(clamp(1 - p * 5));
    } else if (heroCopy) {
      heroCopy.removeAttribute('style'); heroImage.removeAttribute('style');
      scrim.removeAttribute('style'); dark.removeAttribute('style');
    }
    if (engineering) {
      const rect = engineering.getBoundingClientRect();
      const p = clamp(-rect.top / Math.max(engineering.offsetHeight - innerHeight, 1));
      const idx = Math.min(2, Math.floor(p * 3));
      if (idx !== lastFamily) {
        panels.forEach((el, i) => el.classList.toggle('active', i === idx));
        dots.forEach((el, i) => el.classList.toggle('active', i === idx));
        if (modelLink) modelLink.href = `#${families[idx]}`;
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
  fetch('/content/catalog/products.json').then(r => {
    if (!r.ok) throw new Error('No se pudo cargar el catálogo');
    return r.json();
  }).then(products => {
    const host = document.querySelector('#catalog-families');
    const order = ['pipetas', 'postes', 'conectores', 'jaladeras'];
    host.innerHTML = order.map(key => {
      const items = products.filter(p => String(p.category).toLowerCase() === key);
      const [title, description] = labels[key];
      return `<section class="family" id="${key}"><div class="family-header"><div><span class="eyebrow">${items.length} modelos</span><h3>${title}</h3></div><p>${description}</p></div><div class="product-grid">${items.map(p => {
        const code = escapeHTML(p.code || p.model || '');
        const name = escapeHTML(p.name);
        const message = encodeURIComponent(`Hola Herraidea, me interesa cotizar ${code} — ${p.name}.`);
        return `<a class="product-card" href="https://wa.me/524772561695?text=${message}" target="_blank" rel="noopener"><figure><img src="/content/catalog/${escapeHTML(p.image)}" alt="${name} ${code}" loading="lazy"></figure><div class="product-info"><b>${code}</b><span>${name}</span></div></a>`;
      }).join('')}</div></section>`;
    }).join('');
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
