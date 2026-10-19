// Keep a native rel=ar anchor with exactly one image child for Safari Quick Look.
import {systems} from '/ar/systems.js?v=1-92-0';
export const hasProjectAR = key => Object.prototype.hasOwnProperty.call(systems, key);
export function configureProjectAR(container, key = container?.dataset.arSystem || 'clips') {
  const system = systems[key];
  if (!container || !system) return;
  const link = container.querySelector('[data-ar-link]');
  if (!link) return;
  const pageURL = 'https://www.herraidea.com/ar/' + system.slug;
  container.dataset.arSystem = key;
  let supported = false;
  try { supported = link.relList.supports('ar'); } catch {}
  const options = new URLSearchParams({allowsContentScaling:'0', canonicalWebPageURL:pageURL,
    checkoutTitle:system.title, checkoutSubtitle:system.subtitle, callToAction:'Cotizar por WhatsApp'});
  link.href = system.asset + '#' + options.toString().replace(/\+/g, '%20');
  link.rel = 'ar';
  link.hidden = !supported && container.hasAttribute('data-ar-page');
  link.querySelector('img')?.setAttribute('alt', 'Ver en tu espacio · ' + system.title);
  if (!supported && !container.hasAttribute('data-ar-page')) {
    link.href = '/ar/' + system.slug + '/';
    link.removeAttribute('rel');
  }
  if (!link.dataset.arMessageBound) {
    link.dataset.arMessageBound = 'true';
    link.addEventListener('message', (event) => {
      const active = systems[container.dataset.arSystem];
      if (event.data === '_apple_ar_quicklook_button_tapped' && active) {
        window.location.href = 'https://wa.me/524772561695?text=' + encodeURIComponent(active.message);
      }
    });
  }
  const deviceHelp = container.querySelector('[data-ar-device-help]');
  if (deviceHelp) deviceHelp.hidden = supported;
  const copy = container.querySelector('[data-ar-copy]');
  if (copy) copy.onclick = async () => {
    const status = container.querySelector('[data-ar-status]');
    try {
      await navigator.clipboard.writeText(pageURL);
      status.textContent = 'Enlace copiado. Ábrelo en Safari de tu iPhone o iPad.';
    } catch { status.textContent = 'Abre esta dirección en Safari: ' + pageURL; }
  };
}
document.querySelectorAll('[data-ar-page]').forEach(container => configureProjectAR(container));
