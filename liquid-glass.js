/* Event delegation also covers calculator segment buttons created after load. */
(() => {
  const selector = '.calculator-add,.calculator-share,.calculator-whatsapp,.calculator-segment>button,button.project-open,.projects-next,.project-close,.project-actions button';
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)');
  let frame = 0;
  let active = null;
  let point = null;
  const reset = () => {
    cancelAnimationFrame(frame);
    frame = 0;
    if (active) {
      active.style.removeProperty('--glass-x');
      active.style.removeProperty('--glass-y');
    }
    active = null;
  };
  document.addEventListener('pointermove', event => {
    if (reducedMotion.matches || !finePointer.matches || event.pointerType === 'touch') return;
    const target = event.target instanceof Element ? event.target.closest(selector) : null;
    if (!target || target.disabled) { reset(); return; }
    if (target !== active) { reset(); active = target; }
    point = { x:event.clientX, y:event.clientY };
    if (frame) return;
    frame = requestAnimationFrame(() => {
      frame = 0;
      if (!active?.isConnected) { reset(); return; }
      const rect = active.getBoundingClientRect();
      active.style.setProperty('--glass-x', `${Math.max(0, Math.min(100, (point.x - rect.left) / rect.width * 100))}%`);
      active.style.setProperty('--glass-y', `${Math.max(0, Math.min(100, (point.y - rect.top) / rect.height * 100))}%`);
    });
  }, {passive:true});
  document.addEventListener('pointerout', event => {
    if (active && !active.contains(event.relatedTarget)) reset();
  }, {passive:true});
  window.addEventListener('blur', reset);
  reducedMotion.addEventListener('change', reset);
  finePointer.addEventListener('change', reset);
})();
