const pageURL = 'https://www.herraidea.com/ar/hrd-1525';
export function configureProjectAR(container) {
  if (!container || container.dataset.arInitialized) return;
  container.dataset.arInitialized = 'true';
  const link = container.querySelector('[data-ar-link]');
  let supported = false;
  try { supported = link.relList.supports('ar'); } catch {}
  if (!supported) {
    if (container.hasAttribute('data-ar-page')) link.hidden = true;
    else { link.href = '/ar/hrd-1525/'; link.removeAttribute('rel'); }
  }
  const deviceHelp = container.querySelector('[data-ar-device-help]');
  if (deviceHelp) deviceHelp.hidden = supported;
  const copy = container.querySelector('[data-ar-copy]');
  copy?.addEventListener('click', async () => {
    const status = container.querySelector('[data-ar-status]');
    try {
      await navigator.clipboard.writeText(pageURL);
      status.textContent = 'Enlace copiado. Ábrelo en Safari de tu iPhone o iPad.';
    } catch { status.textContent = 'Abre esta dirección en Safari: ' + pageURL; }
  });
}
document.querySelectorAll('[data-ar-page]').forEach(configureProjectAR);
