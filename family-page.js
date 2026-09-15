(() => {
  const cards = [...document.querySelectorAll('.post-card')];
  const filters = [...document.querySelectorAll('[data-family-filter]')];
  const search = document.querySelector('#post-search');
  const count = document.querySelector('#post-result-count');
  const empty = document.querySelector('#post-no-results');
  let activeGroup = 'all';

  const normalize = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const applyFilters = () => {
    const query = normalize(search?.value).trim();
    let visible = 0;
    cards.forEach(card => {
      const matchesGroup = activeGroup === 'all' || card.dataset.group === activeGroup;
      const matchesSearch = !query || normalize(card.dataset.search).includes(query);
      card.hidden = !(matchesGroup && matchesSearch);
      if (!card.hidden) visible += 1;
    });
    filters.forEach(button => {
      const selected = button.dataset.familyFilter === activeGroup;
      button.classList.toggle('active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    if (count) count.textContent = String(visible);
    if (empty) empty.hidden = visible !== 0;
  };

  filters.forEach(button => button.addEventListener('click', () => {
    activeGroup = button.dataset.familyFilter;
    applyFilters();
    if (button.closest('.system-grid')) document.querySelector('#modelos')?.scrollIntoView({behavior:'smooth', block:'start'});
  }));
  search?.addEventListener('input', applyFilters);
})();
