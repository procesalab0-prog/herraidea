// Promotional footage only: the approved interactive models remain unchanged.
(() => {
  const video = document.querySelector('.project-cover-video');
  if (!video || !('IntersectionObserver' in window)) return;
  const card = video.closest('.project-card');
  const dialog = document.querySelector('#project-dialog');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const connection = navigator.connection;
  let visible = false;
  const update = () => {
    const staticOnly = motion.matches || connection?.saveData;
    if (staticOnly) video.classList.remove('is-ready');
    if (!visible || document.hidden || dialog?.open || staticOnly) {
      video.pause();
      return;
    }
    if (!video.getAttribute('src')) video.src = video.dataset.src;
    // One short play per visit, not an endless moving background.
    if (!video.ended) video.play().catch(() => {});
  };
  video.muted = true;
  video.addEventListener('playing', () => video.classList.add('is-ready'));
  video.addEventListener('error', () => video.classList.remove('is-ready'));
  new IntersectionObserver(([entry]) => {
    const wasVisible = visible;
    visible = entry.isIntersecting && entry.intersectionRatio >= 0.55;
    if (visible && !wasVisible && video.ended) video.currentTime = 0;
    update();
  }, { threshold: [0, 0.55] }).observe(card);
  document.addEventListener('visibilitychange', update);
  motion.addEventListener('change', update);
  connection?.addEventListener('change', update);
  if (dialog) new MutationObserver(update).observe(dialog, { attributes: true, attributeFilter: ['open'] });
})();
