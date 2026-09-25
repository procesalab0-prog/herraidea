(() => {
  const clamp = (n, min = 0, max = 1) => Math.max(min, Math.min(max, n));
  const guideSection = document.querySelector('#asesoria');
  const projectsSection = document.querySelector('#proyectos');
  if (guideSection && projectsSection) projectsSection.insertAdjacentElement('afterend', guideSection);
  const menuButton = document.querySelector('.menu-toggle');
  const menu = document.querySelector('.main-nav');
  menuButton?.addEventListener('click', () => {
    const open = menu.classList.toggle('open');
    menuButton.setAttribute('aria-expanded', String(open));
  });
  menu?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    menu.classList.remove('open'); menuButton?.setAttribute('aria-expanded', 'false');
  }));

  const brand = document.querySelector('.brand');
  const creditsDialog = document.querySelector('#credits-dialog');
  let logoTaps = 0, logoTimer;
  const openCredits = async () => {
    try {
      const data = await fetch('/content/version-history.json').then(r => r.json());
      document.querySelector('#credits-version').textContent = data.current;
      document.querySelector('#version-list').innerHTML = data.versions.map((item, index) => `<article class="${index === 0 ? 'current' : ''}"><b>v${item.version}</b><div><strong>${item.title}</strong><p>${item.summary}</p></div><time>${item.date}</time></article>`).join('');
    } catch {}
    creditsDialog?.showModal(); document.body.classList.add('dialog-open');
  };
  brand?.addEventListener('click', event => {
    event.preventDefault(); logoTaps += 1;
    brand.classList.remove('secret-tap'); void brand.offsetWidth; brand.classList.add('secret-tap');
    clearTimeout(logoTimer);
    if (logoTaps >= 6) { logoTaps = 0; openCredits(); return; }
    logoTimer = setTimeout(() => { if (logoTaps === 1) location.hash = 'inicio'; logoTaps = 0; }, 3000);
  });
  document.querySelector('.credits-close')?.addEventListener('click', () => { creditsDialog?.close(); document.body.classList.remove('dialog-open'); });
  creditsDialog?.addEventListener('close', () => document.body.classList.remove('dialog-open'));
  creditsDialog?.addEventListener('click', event => { if (event.target === creditsDialog) { creditsDialog.close(); document.body.classList.remove('dialog-open'); } });

  const heroTrack = document.querySelector('.hero-track');
  const heroCopy = document.querySelector('.hero-copy');
  const heroImage = document.querySelector('.hero-image');
  const heroNight = document.querySelector('.hero-night');
  const scrim = document.querySelector('.hero-scrim');
  const dark = document.querySelector('.hero-dark');
  const workshop = document.querySelector('.workshop-panel');
  const hint = document.querySelector('.scroll-hint');
  const aboutSection = document.querySelector('.about-section');
  const aboutOrigin = document.querySelector('.about-origin');
  const aboutOriginCopy = document.querySelector('.about-origin-copy');
  const valueCards = [...document.querySelectorAll('.values article')];
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const engineering = document.querySelector('.engineering-track');
  const panels = [...document.querySelectorAll('.spec-panel')];
  const dots = [...document.querySelectorAll('.model-dots i')];
  const modelLink = document.querySelector('#model-link');
  const families = ['pipetas', 'conectores', 'postes'];
  const mobileModels = [
    { family: 'Familia 01 · Pipetas', name: 'Pipeta Chapetón', code: 'HRD 1101', labels: ['Vidrio 8–12 mm', 'Acero T-304', 'Salida 28 mm'], summary: 'Conector vidrio–muro para cristal templado. Acero inoxidable con acabado satín.' },
    { family: 'Familia 02 · Conectores', name: 'Conector 44 × 40 mm', code: 'HRD 1303', labels: ['Diámetro 44 mm', 'Cuerpo 40 mm', 'Tapa 10 mm'], summary: 'Botón vidrio–muro con empaque integrado y fijación Allen central. Para vidrio de 8–12 mm.' },
    { family: 'Familia 03 · Postes', name: 'Mini Poste con tope', code: 'HRD 1206 × 450', labels: ['Altura 450 mm', 'Ranura 300 mm', 'Base 100 × 100 mm'], summary: 'Poste rectangular con ranura de 300 mm y placa base. Fabricado en acero inoxidable T-304.' }
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
      if (heroNight) heroNight.style.opacity = String(clamp((p - .16) * 1.75));
      scrim.style.opacity = String(clamp(1 - p * (mobile ? 1.45 : 1.7)));
      dark.style.opacity = String(clamp((p - (mobile ? .18 : .22)) * (mobile ? 2.1 : 1.8)) * (mobile ? .44 : .5));
      workshop.style.opacity = String(clamp((p - (mobile ? .42 : .48)) * (mobile ? 3.2 : 2.8)));
      workshop.style.transform = `translateY(${(1 - clamp((p - (mobile ? .4 : .45)) * 2.5)) * (mobile ? 28 : 38)}px)`;
      if (hint) hint.style.opacity = String(clamp(1 - p * 5));
    }
    if (aboutSection && aboutOrigin) {
      const rect = aboutOrigin.getBoundingClientRect();
      const p = clamp((innerHeight * .86 - rect.top) / Math.max(innerHeight * .9, 1));
      const night = reduceMotion.matches ? 0 : clamp((p - .25) * 1.65);
      aboutSection.style.setProperty('--evolution-progress', String(reduceMotion.matches ? 0 : p));
      aboutSection.style.setProperty('--evolution-night', String(night));
      if (aboutOriginCopy) {
        const copyProgress = reduceMotion.matches ? 1 : clamp(p * 1.9);
        aboutOriginCopy.style.opacity = String(.56 + copyProgress * .44);
        aboutOriginCopy.style.transform = `translateY(${(1 - copyProgress) * 24}px)`;
      }
      const valuesRect = document.querySelector('.values')?.getBoundingClientRect();
      if (valuesRect) {
        const valuesProgress = reduceMotion.matches ? 1 : clamp((innerHeight * .9 - valuesRect.top) / Math.max(innerHeight * .42, 1));
        valueCards.forEach((card, index) => {
          const cardProgress = clamp(valuesProgress * 1.45 - index * .16);
          card.style.opacity = String(.5 + cardProgress * .5);
          card.style.transform = `translateY(${(1 - cardProgress) * 26}px)`;
        });
      }
    }
    if (engineering) {
      const rect = engineering.getBoundingClientRect();
      const p = clamp(-rect.top / Math.max(engineering.offsetHeight - innerHeight, 1));
      const idx = Math.min(2, Math.floor(p * 3));
      document.documentElement.style.setProperty('--technical-progress', `${p * 100}%`);
      const mobileHint = document.querySelector('#mobile-scroll-hint');
      if (mobileHint) mobileHint.style.opacity = String(clamp(1 - p * 10));
      const mobileSummary = document.querySelector('#mobile-tech-summary');
      if (mobileSummary) mobileSummary.style.opacity = String(clamp((p - .025) * 14));
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
          document.querySelector('#mobile-tech-summary').textContent = model.summary;
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
    pipetas: ['Pipetas', 'Conectores cilíndricos para vidrio-muro y vidrio-vidrio, en versiones chapetón, avellanado, allen y ajustable.', '/assets/catalog/pictograms/pipetas.png?v=1211'],
    postes: ['Postes', 'Mini postes sólidos, huecos, rectangulares y de solera, con placa base barrenada y versiones con tope.', '/assets/catalog/pictograms/postes.png?v=1211'],
    conectores: ['Conectores', 'Botones y conectores para vidrio-muro y vidrio-vidrio, fabricados para distintos espesores y configuraciones.', '/assets/catalog/pictograms/conectores.png?v=1211'],
    jaladeras: ['Jaladeras', 'Jaladeras tubulares de acero inoxidable para puertas de cristal templado.', '/assets/catalog/pictograms/jaladeras.png?v=1211']
  };
  const escapeHTML = value => String(value ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  const productDialog = document.querySelector('#product-dialog');
  let catalogDetails = [];
  const normalizeCatalogText = value => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const productSystem = product => {
    const code = normalizeCatalogText(product.code);
    const text = normalizeCatalogText(`${product.code} ${product.name} ${product.description}`);
    if (/hrd 1517|hrd 1518/.test(code)) return 'tubo';
    if (/hrd 1519|hrd 1520|hrd 1525|hrd 1526/.test(code)) return 'clips';
    if (/hrd 1616/.test(code)) return 'cable';
    if (/hrd 1221|hrd 1223|hrd 1715|hrd 1716|hrd 1717/.test(code) || text.includes('solera')) return 'solera';
    return '';
  };
  const productApplication = product => {
    const category = normalizeCatalogText(product.category);
    const text = normalizeCatalogText(`${product.name} ${product.description} ${(product.specifications || []).join(' ')}`);
    if (text.includes('vidrio-muro') || text.includes('vidrio a muro')) return 'vidrio-muro';
    if (text.includes('vidrio-vidrio') || text.includes('vidrio a vidrio')) return 'vidrio-vidrio';
    if (category === 'jaladeras' || /jaladera|bisagra|pomo/.test(text)) return 'puerta';
    if (category === 'postes' || /barandal|pasamanos/.test(text)) return 'barandal';
    return '';
  };
  const systemLabels = {
    clips: 'Postes con clips + vidrio',
    tubo: 'Sistema de tubo de 1/2 pulgada',
    cable: 'Poste cuadrado + cable de acero',
    solera: 'Postes y brazos de solera'
  };
  const systemProjectIds = { clips: 'clips', tubo: 'hrd1518', cable: 'hrd1616' };
  const productSlug = code => String(code).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  const openProduct = product => {
    if (!product || !productDialog) return;
    document.querySelector('#dialog-category').textContent = `${product.category} · ${product.code}`;
    document.querySelector('#product-dialog-title').textContent = product.name;
    document.querySelector('#dialog-description').textContent = product.description;
    document.querySelector('#dialog-specs').innerHTML = product.specifications.map(spec => `<li>${escapeHTML(spec)}</li>`).join('');
    const images = product.detailImages.length ? product.detailImages : [`/content/catalog/${product.image}`];
    document.querySelector('#dialog-gallery').innerHTML = images.map((src, index) => `<figure class="${index === 0 ? 'primary' : ''}"><img src="${escapeHTML(src)}" alt="${escapeHTML(product.name)} ${index ? 'plano o detalle técnico' : ''}" loading="eager"></figure>`).join('');
    if (product.assemblyAnimation) document.querySelector('#dialog-gallery').insertAdjacentHTML('beforeend', `<figure class="primary"><details open><summary>Armado animado · mostrar / ocultar</summary><picture><source media="(prefers-reduced-motion: reduce)" srcset="${escapeHTML(product.assemblyPoster)}"><img src="${escapeHTML(product.assemblyAnimation)}" alt="Armado por etapas del ${escapeHTML(product.code)}, con la tapa al final" loading="lazy"></picture></details><figcaption>Armado por etapas · <a href="/?proyecto=hrd1220">Explorar despiece 3D</a></figcaption></figure>`);
    const system = productSystem(product);
    const systemSection = document.querySelector('#dialog-system');
    if (system && systemSection) {
      const related = catalogDetails.filter(item => item.code !== product.code && productSystem(item) === system).slice(0, 4);
      document.querySelector('#dialog-system-title').textContent = systemLabels[system];
      document.querySelector('#dialog-related-products').innerHTML = related.length ? related.map(item => `<button type="button" data-related-product="${escapeHTML(item.code)}"><b>${escapeHTML(item.code)}</b><span>${escapeHTML(item.name)}</span></button>`).join('') : '<p>Este modelo identifica el sistema completo.</p>';
      const systemLink = document.querySelector('#dialog-system-link');
      const projectId = systemProjectIds[system];
      systemLink.hidden = !projectId;
      systemLink.dataset.projectTarget = projectId || '';
      systemSection.hidden = false;
    } else if (systemSection) systemSection.hidden = true;
    const message = encodeURIComponent(`Hola Herraidea, me interesa cotizar ${product.code} — ${product.name}.`);
    document.querySelector('#dialog-whatsapp').href = `https://wa.me/524772561695?text=${message}`;
    const pageLink = document.querySelector('#dialog-page');
    if (pageLink) pageLink.href = `/productos/${productSlug(product.code)}`;
    const pdfLink = document.querySelector('#dialog-pdf');
    const pdfFile = `/output/pdf/fichas/${productSlug(product.code)}.pdf`;
    if (pdfLink) { pdfLink.hidden = false; pdfLink.href = pdfFile; }
    const url = new URL(location.href); url.searchParams.set('producto', productSlug(product.code));
    history.pushState({ product: product.code }, '', url);
    if (!productDialog.open) productDialog.showModal();
    document.body.classList.add('dialog-open');
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
    const product = catalogDetails.find(item => productSlug(item.code) === new URL(location.href).searchParams.get('producto'));
    const shareUrl = product ? `${location.origin}/productos/${productSlug(product.code)}` : location.href;
    try { await navigator.clipboard.writeText(shareUrl); event.currentTarget.textContent = 'Enlace copiado'; }
    catch { event.currentTarget.textContent = 'Copia la URL del navegador'; }
  });
  document.querySelector('#dialog-related-products')?.addEventListener('click', event => {
    const button = event.target.closest('[data-related-product]');
    if (button) openProduct(catalogDetails.find(product => product.code === button.dataset.relatedProduct));
  });
  document.querySelector('#dialog-system-link')?.addEventListener('click', event => {
    const projectId = event.currentTarget.dataset.projectTarget;
    closeProduct();
    if (!projectId) return;
    const card = document.querySelector(`[data-project="${projectId}"]`);
    requestAnimationFrame(() => card?.scrollIntoView({ behavior: 'smooth', block: 'center' }));
  });
  addEventListener('popstate', () => closeProduct(false));

  fetch('/content/catalog/details.json?v=1-57-0').then(r => {
    if (!r.ok) throw new Error('No se pudo cargar el catálogo');
    return r.json();
  }).then(products => {
    catalogDetails = products;
    const host = document.querySelector('#catalog-families');
    const order = ['pipetas', 'postes', 'conectores', 'jaladeras'];
    host.innerHTML = order.map((key, familyIndex) => {
      const items = products.filter(p => String(p.category).toLowerCase() === key);
      const [title, description, pictogram] = labels[key];
      return `<section class="family" id="${key}"><button class="family-toggle" type="button" aria-expanded="false"><span class="family-bar"></span><span class="family-number">0${familyIndex + 1}</span><span class="family-pictogram" aria-hidden="true"><img src="${pictogram}" alt=""></span><span class="family-title"><h3>${title}</h3><small>${items.length} modelos</small></span><p>${description}</p><span class="family-mark" aria-hidden="true"></span></button><div class="family-products">${items.map((p, productIndex) => {
        const code = escapeHTML(p.code || p.model || '');
        const name = escapeHTML(p.name);
        const searchable = escapeHTML(normalizeCatalogText(`${p.code} ${p.name} ${p.description} ${(p.specifications || []).join(' ')}`));
        return `<button class="product-card" type="button" data-product="${escapeHTML(p.code)}" data-search="${searchable}" data-application="${productApplication(p)}" data-system="${productSystem(p)}" aria-label="Ver ficha de ${name} ${code}" style="animation-delay:${Math.min(productIndex,16)*.035}s"><figure><img src="/content/catalog/${escapeHTML(p.image)}" alt="${name} ${code}" loading="lazy"></figure><div class="product-info"><b>${code}</b><span>${name}</span><em>Ver ficha técnica →</em></div></button>`;
      }).join('')}</div></section>`;
    }).join('');
    const familyEls = [...host.querySelectorAll('.family')];
    const toggleFamily = (family, forceOpen = false) => {
      const shouldOpen = forceOpen || !family.classList.contains('open');
      familyEls.forEach(el => { const open = el === family && shouldOpen; el.classList.toggle('open', open); el.querySelector('.family-toggle').setAttribute('aria-expanded', String(open)); });
    };
    // Abrir una familia cierra las demás y cambia la altura del catálogo. Sin compensar,
    // el encabezado recién tocado se va de la pantalla mientras dura la animación.
    const mantenerEnPantalla = (referencia, destino, duracion = 900) => {
      const limite = performance.now() + duracion;
      let cancelado = false;
      const cancelar = () => { cancelado = true; };
      addEventListener('wheel', cancelar, {once:true, passive:true});
      addEventListener('touchmove', cancelar, {once:true, passive:true});
      addEventListener('keydown', cancelar, {once:true});
      const paso = () => {
        if (cancelado) return;
        const desfase = referencia.getBoundingClientRect().top - destino;
        if (Math.abs(desfase) > .5) scrollBy({top: desfase, behavior: 'instant'});
        if (performance.now() < limite) requestAnimationFrame(paso);
        else { removeEventListener('wheel', cancelar); removeEventListener('touchmove', cancelar); removeEventListener('keydown', cancelar); }
      };
      requestAnimationFrame(paso);
    };
    familyEls.forEach(family => {
      const toggle = family.querySelector('.family-toggle');
      toggle.addEventListener('click', () => {
        // La posición se mide ANTES de tocar el DOM: es la que hay que conservar.
        const destino = toggle.getBoundingClientRect().top;
        toggleFamily(family);
        mantenerEnPantalla(toggle, destino);
      });
    });
    const searchInput = document.querySelector('#catalog-search');
    const familyFilter = document.querySelector('#catalog-family-filter');
    const applicationFilter = document.querySelector('#catalog-application-filter');
    const systemFilter = document.querySelector('#catalog-system-filter');
    const resultCount = document.querySelector('#catalog-result-count');
    const emptyState = document.querySelector('#catalog-empty');
    const clearSearch = document.querySelector('#catalog-search-clear');
    const filterCatalog = () => {
      const query = normalizeCatalogText(searchInput?.value).trim();
      const selectedFamily = familyFilter?.value || 'all';
      const selectedApplication = applicationFilter?.value || 'all';
      const selectedSystem = systemFilter?.value || 'all';
      let visibleCount = 0;
      familyEls.forEach(family => {
        let familyCount = 0;
        family.querySelectorAll('.product-card').forEach(card => {
          const visible = (!query || card.dataset.search.includes(query)) && (selectedFamily === 'all' || family.id === selectedFamily) && (selectedApplication === 'all' || card.dataset.application === selectedApplication) && (selectedSystem === 'all' || card.dataset.system === selectedSystem);
          card.hidden = !visible;
          if (visible) { visibleCount += 1; familyCount += 1; }
        });
        family.hidden = familyCount === 0;
        if (query || selectedFamily !== 'all' || selectedApplication !== 'all' || selectedSystem !== 'all') {
          family.classList.toggle('open', familyCount > 0);
          family.querySelector('.family-toggle').setAttribute('aria-expanded', String(familyCount > 0));
        }
      });
      if (resultCount) resultCount.textContent = String(visibleCount);
      if (emptyState) emptyState.hidden = visibleCount !== 0;
      if (clearSearch) clearSearch.hidden = !query;
    };
    [searchInput, familyFilter, applicationFilter, systemFilter].forEach(control => control?.addEventListener(control === searchInput ? 'input' : 'change', filterCatalog));
    clearSearch?.addEventListener('click', () => { searchInput.value = ''; searchInput.focus(); filterCatalog(); });
    document.querySelector('#catalog-known-product')?.addEventListener('click', () => {
      const disclosure = document.querySelector('#catalog-tools-disclosure');
      if (disclosure) disclosure.open = true;
      document.querySelector('#catalog-tools')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setTimeout(() => searchInput?.focus({ preventScroll: true }), 450);
    });
    document.querySelectorAll('[data-open-family]').forEach(button => button.addEventListener('click', () => {
      const family = document.querySelector(`#${button.dataset.openFamily}`); if (!family) return;
      if (familyFilter) familyFilter.value = button.dataset.openFamily;
      filterCatalog();
      // Sin la animación de altura el catálogo queda en su tamaño final antes de calcular
      // el destino, así el scroll aterriza en la familia y no donde estaba el contenido.
      host.classList.add('sin-animacion');
      toggleFamily(family, true);
      void host.offsetHeight;
      family.scrollIntoView({behavior:'smooth', block:'start'});
      requestAnimationFrame(() => requestAnimationFrame(() => host.classList.remove('sin-animacion')));
    }));
    host.querySelectorAll('[data-product]').forEach(card => card.addEventListener('click', () => openProduct(catalogDetails.find(p => p.code === card.dataset.product))));
    const requested = new URL(location.href).searchParams.get('producto');
    if (requested) openProduct(catalogDetails.find(p => productSlug(p.code) === requested));
  }).catch(err => {
    document.querySelector('#catalog-families').innerHTML = `<p>${escapeHTML(err.message)}. Escríbenos por WhatsApp para recibirlo.</p>`;
  });

  document.addEventListener('hrd-city', event => {
    const label = document.querySelector('#shipping-city'); if (label) label.textContent = `Cobertura · ${event.detail}`;
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

  const guide = document.querySelector('#project-guide');
  if (guide) {
    const steps = [...guide.querySelectorAll('.guide-step')];
    const result = guide.querySelector('#guide-result');
    const actions = guide.querySelector('#guide-actions');
    const back = guide.querySelector('#guide-back');
    const next = guide.querySelector('#guide-next');
    const progressLabel = document.querySelector('#guide-progress-label');
    const progressBar = document.querySelector('#guide-progress-bar');
    let currentStep = 0;

    const fieldNames = ['proyecto', 'ubicacion', 'base', 'aplicacion'];
    const selectedValue = step => guide.querySelector(`input[name="${fieldNames[step]}"]:checked`)?.value || '';
    const renderGuide = () => {
      steps.forEach((step, index) => {
        const active = index === currentStep;
        step.hidden = !active;
        step.classList.toggle('active', active);
      });
      result.hidden = true;
      actions.hidden = false;
      back.disabled = currentStep === 0;
      next.disabled = !selectedValue(currentStep);
      next.innerHTML = currentStep === steps.length - 1 ? 'Ver resumen <span>→</span>' : 'Siguiente <span>→</span>';
      progressLabel.textContent = `0${currentStep + 1} / 04`;
      progressBar.style.width = `${((currentStep + 1) / steps.length) * 100}%`;
    };

    guide.addEventListener('change', event => {
      if (!event.target.matches('input[type="radio"]')) return;
      next.disabled = false;
    });
    back.addEventListener('click', () => { if (currentStep > 0) { currentStep -= 1; renderGuide(); } });
    next.addEventListener('click', () => {
      if (!selectedValue(currentStep)) return;
      if (currentStep < steps.length - 1) { currentStep += 1; renderGuide(); return; }
      const values = {
        proyecto: selectedValue(0),
        ubicacion: selectedValue(1),
        base: selectedValue(2),
        aplicacion: selectedValue(3)
      };
      steps.forEach(step => { step.hidden = true; step.classList.remove('active'); });
      actions.hidden = true;
      result.hidden = false;
      document.querySelector('#guide-project').textContent = values.proyecto;
      document.querySelector('#guide-location').textContent = values.ubicacion;
      document.querySelector('#guide-base').textContent = values.base;
      document.querySelector('#guide-application').textContent = values.aplicacion;
      progressLabel.textContent = '04 / 04';
      progressBar.style.width = '100%';
      const railingApplications = ['Barandal', 'Escalera', 'Balcón o terraza'];
      const suggestion = railingApplications.includes(values.aplicacion) ? {
        kicker: 'Punto de partida · HRD 1525',
        title: 'Postes con clips + vidrio',
        description: 'Un sistema completo que reúne postes, pinzas, cristal y pasamanos.',
        parts: ['Postes', 'Clips o pinzas', 'Pasamanos y fijaciones'],
        image: '/assets/projects/clip-system/portada-estudio.jpg',
        alt: 'Sistema de barandal con postes, clips y vidrio',
        href: '#proyectos', label: 'Explorar solución 3D', project: 'clips'
      } : values.aplicacion === 'Cancel o división' ? {
        kicker: 'Punto de partida · Familia de producto',
        title: 'Conectores para vidrio',
        description: 'Herrajes para unir, soportar y resolver encuentros entre paneles de vidrio.',
        parts: ['Conectores', 'Pipetas', 'Fijaciones compatibles'],
        image: '/content/catalog/images/conectores-hrd-1301.jpg',
        alt: 'Conectores Herraidea para soluciones con vidrio',
        href: '#conectores', label: 'Ver familia de conectores', project: ''
      } : {
        kicker: 'Punto de partida · Fabricación especial',
        title: 'Una solución a la medida',
        description: 'Partimos de una idea, fotografía, muestra o medida para revisar cómo fabricarla.',
        parts: ['Idea o muestra', 'Medidas del proyecto', 'Revisión de fabricación'],
        image: '/assets/fabricacion/torno-cnc-haas.jpg',
        alt: 'Fabricación a la medida en Herraidea',
        href: '#soluciones', label: 'Conocer capacidades', project: ''
      };
      document.querySelector('#guide-solution-kicker').textContent = suggestion.kicker;
      document.querySelector('#guide-solution-title').textContent = suggestion.title;
      document.querySelector('#guide-solution-description').textContent = suggestion.description;
      const solutionImage = document.querySelector('#guide-solution-image');
      solutionImage.src = suggestion.image; solutionImage.alt = suggestion.alt;
      document.querySelector('#guide-solution-parts').innerHTML = suggestion.parts.map(part => `<li>${escapeHTML(part)}</li>`).join('');
      const solutionLink = document.querySelector('#guide-solution-link');
      solutionLink.href = suggestion.href;
      solutionLink.dataset.guideProject = suggestion.project;
      solutionLink.innerHTML = `${suggestion.label} <span>→</span>`;
      const message = ['Hola Herraidea, quiero asesoría para un proyecto:', `Tipo: ${values.proyecto}`, `Ubicación: ${values.ubicacion}`, `Base de montaje: ${values.base}`, `Necesito resolver: ${values.aplicacion}`, `Punto de partida sugerido: ${suggestion.title}`, 'Quiero revisar qué solución se adapta mejor.'].join('\n');
      document.querySelector('#guide-whatsapp').href = `https://wa.me/524772561695?text=${encodeURIComponent(message)}`;
      result.querySelector('h3')?.focus?.();
    });
    document.querySelector('#guide-restart')?.addEventListener('click', () => {
      guide.reset(); currentStep = 0; renderGuide();
    });
    renderGuide();
  }

  document.querySelector('#guide-solution-link')?.addEventListener('click', event => {
    const project = event.currentTarget.dataset.guideProject;
    if (!project) return;
    event.preventDefault();
    document.querySelector(`.project-card [data-open-project="${project}"]`)?.click();
  });

  document.querySelector('#new-project-form')?.addEventListener('submit', event => {
    event.preventDefault();
    const idea = String(new FormData(event.currentTarget).get('proyecto-nuevo') || '').trim();
    if (!idea) return;
    const message = ['Hola Herraidea, tengo otro proyecto en mente:', idea, 'Quiero revisar si pueden ayudarme a desarrollarlo.'].join('\n');
    window.open(`https://wa.me/524772561695?text=${encodeURIComponent(message)}`, '_blank', 'noopener');
  });
})();
