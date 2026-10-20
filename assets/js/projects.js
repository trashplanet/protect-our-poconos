'use strict';
(() => {
  const grid = document.querySelector('.tracker-grid');
  const cards = [...grid.querySelectorAll('.tracker-card')];
  const buttons = [...document.querySelectorAll('[data-filter]')];
  const county = document.querySelector('#county-filter');
  const sort = document.querySelector('#project-sort');
  const count = document.querySelector('#result-count');
  const clear = document.querySelector('#clear-filters');
  let category = 'all';
  const categories = new Set(buttons.map(button => button.dataset.filter));
  const countyNames = { all: 'all counties', pike: 'Pike County', monroe: 'Monroe County', luzerne: 'Luzerne County' };
  const categoryNames = { all: 'projects and sites', 'data-centers': 'data-center proposals', infrastructure: 'infrastructure projects', watchlist: 'watchlist sites', rumors: 'community rumors', watched: 'watchlist / rumor sites' };

  // Enhance existing copy only after JS loads; without JS all content stays visible.
  const previews = [];
  function addPreview(text, extraPanels = []) {
    const card = text.closest('.tracker-card');
    const button = document.createElement('button');
    const id = `${card.id}-preview-${previews.length}`;
    text.id = id;
    button.type = 'button';
    button.className = 'project-read-more';
    button.setAttribute('aria-controls', [id, ...extraPanels.map((panel, index) => {
      panel.id = `${id}-extra-${index}`;
      return panel.id;
    })].join(' '));
    const label = text.classList.contains('project-summary') ? 'description' : 'updates';
    let expanded = false;
    function render() {
      text.classList.toggle('project-preview', !expanded);
      extraPanels.forEach(panel => { panel.hidden = !expanded; });
      button.textContent = expanded ? 'Read less' : 'Read more';
      button.setAttribute('aria-expanded', String(expanded));
      button.setAttribute('aria-label', `${button.textContent}: ${card.querySelector('h2').textContent.trim()} ${label}`);
    }
    text.after(button);
    button.addEventListener('click', () => { expanded = !expanded; render(); });
    render();
    previews.push(() => {
      if (card.hidden) return;
      button.hidden = !expanded && !extraPanels.length && text.scrollHeight <= text.clientHeight + 1;
    });
  }
  cards.forEach(card => {
    addPreview(card.querySelector('.project-summary'));
    const milestones = [...card.querySelectorAll('.project-milestone')];
    // One disclosure controls a project's updates, including Hazelnut's second panel.
    if (milestones.length) addPreview(milestones[0].querySelector('p'), milestones.slice(1));
  });
  function measurePreviews() { previews.forEach(measure => measure()); }
  const previewObserver = new ResizeObserver(measurePreviews);
  previewObserver.observe(grid);
  document.fonts.ready.then(measurePreviews);

  function matchesCategory(card) {
    return category === 'all' || card.dataset.category === category ||
      (category === 'watched' && ['watchlist', 'rumors'].includes(card.dataset.category));
  }

  function applyFilters(updateURL = true) {
    const today = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
    const deadline = card => card.dataset.deadline >= today ? card.dataset.deadline : '9999-12-31';
    const ordered = [...cards].sort((a, b) => {
      if (sort.value === 'name') return a.querySelector('h2').textContent.trim().localeCompare(b.querySelector('h2').textContent.trim());
      if (sort.value === 'deadline') return deadline(a).localeCompare(deadline(b)) || Number(a.dataset.rank) - Number(b.dataset.rank);
      return Number(a.dataset.rank) - Number(b.dataset.rank);
    });
    ordered.forEach(card => {
      card.hidden = !matchesCategory(card) || (county.value !== 'all' && !card.dataset.county.split(' ').includes(county.value));
      grid.append(card);
    });
    measurePreviews();
    buttons.forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.filter === category));
      if (button.dataset.filter === 'watched') button.hidden = category !== 'watched';
    });
    const visible = cards.filter(card => !card.hidden).length;
    count.textContent = category === 'all' && county.value === 'all' ? `Showing all ${cards.length} projects and sites` : `Showing ${visible} ${categoryNames[category]} · ${countyNames[county.value]}`;
    clear.hidden = category === 'all' && county.value === 'all' && sort.value === 'relevance';
    document.querySelector('.empty-results').hidden = visible > 0;
    if (updateURL) {
      const url = new URL(location.href);
      for (const [key, value, initial] of [['type', category, 'all'], ['county', county.value, 'all'], ['sort', sort.value, 'relevance']]) {
        if (value === initial) url.searchParams.delete(key);
        else url.searchParams.set(key, value);
      }
      history.replaceState(null, '', url);
    }
  }

  function reset() {
    category = 'all'; county.value = 'all'; sort.value = 'relevance'; applyFilters();
  }
  function readURL() {
    const params = new URLSearchParams(location.search);
    category = categories.has(params.get('type')) ? params.get('type') : 'all';
    county.value = ['all', 'pike', 'monroe', 'luzerne'].includes(params.get('county')) ? params.get('county') : 'all';
    sort.value = ['relevance', 'deadline', 'name'].includes(params.get('sort')) ? params.get('sort') : 'relevance';
    applyFilters(false);
  }
  function revealAnchor() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const card = cards.find(item => item.id === id);
    if (!card) return;
    if (card.hidden) reset();
    card.querySelector('details').open = true;
    requestAnimationFrame(() => card.scrollIntoView({ block: 'start' }));
  }
  document.querySelector('.tracker-controls').addEventListener('submit', event => event.preventDefault());
  buttons.forEach(button => button.addEventListener('click', () => { category = button.dataset.filter; applyFilters(); }));
  county.addEventListener('change', () => applyFilters());
  sort.addEventListener('change', () => applyFilters());
  function resetFromControl() {
    reset();
    buttons[0].focus();
  }
  clear.addEventListener('click', resetFromControl);
  document.querySelector('[data-reset-filters]').addEventListener('click', resetFromControl);
  document.querySelectorAll('[data-quick-filter]').forEach(link => link.addEventListener('click', () => {
    category = link.dataset.quickFilter; county.value = 'all'; applyFilters();
  }));
  window.addEventListener('popstate', () => { readURL(); revealAnchor(); });
  window.addEventListener('hashchange', revealAnchor);
  readURL();
  revealAnchor();
})();
