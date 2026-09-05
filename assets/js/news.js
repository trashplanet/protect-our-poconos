'use strict';
(() => {
  const form = document.querySelector('.news-filters');
  const topic = document.querySelector('#news-topic');
  const type = document.querySelector('#news-type');
  const search = document.querySelector('#news-search');
  const cards = [...document.querySelectorAll('.coverage-grid .story-card')];
  const more = document.querySelector('#news-more');
  const count = document.querySelector('#news-count');
  let limit = 6;
  const params = new URLSearchParams(location.search);
  for (const [control, key] of [[topic, 'topic'], [type, 'type']]) {
    if ([...control.options].some(option => option.value === params.get(key))) control.value = params.get(key);
  }
  search.value = params.get('q') || '';
  function render(updateURL = true) {
    const query = search.value.trim().toLocaleLowerCase();
    const matches = cards.filter(card => (!topic.value || JSON.parse(card.dataset.topics).includes(topic.value)) &&
      (!type.value || card.dataset.type === type.value) && (!query || card.textContent.toLocaleLowerCase().includes(query)));
    cards.forEach(card => { card.hidden = true; });
    matches.slice(0, limit).forEach(card => { card.hidden = false; });
    count.textContent = `${matches.length} ${matches.length === 1 ? 'article' : 'articles'} · Showing ${Math.min(limit, matches.length)} · Newest first`;
    document.querySelector('#news-empty').hidden = matches.length !== 0;
    more.hidden = limit >= matches.length;
    more.textContent = `Show more articles (${Math.max(0, matches.length - limit)} remaining)`;
    if (updateURL) {
      const url = new URL(location.href);
      for (const [key, value] of [['topic', topic.value], ['type', type.value], ['q', search.value.trim()]]) {
        if (value) url.searchParams.set(key, value); else url.searchParams.delete(key);
      }
      history.replaceState(null, '', url);
    }
  }
  form.hidden = false;
  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('input', () => { limit = 6; render(); });
  form.addEventListener('reset', () => {
    topic.value = ''; type.value = ''; search.value = ''; limit = 6; render();
  });
  more.addEventListener('click', () => {
    const hiddenBefore = cards.filter(card => card.hidden);
    limit += 6; render();
    const newlyShown = hiddenBefore.find(card => !card.hidden);
    newlyShown?.querySelector('h3 a').focus({ preventScroll: true });
  });
  // Dates stay editorially fixed; elapsed milestones are clearly marked, not advertised as upcoming.
  const today = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
  document.querySelectorAll('[data-event-date]').forEach(event => {
    if (event.dataset.eventDate < today) {
      event.classList.add('past-event');
      const label = document.createElement('p'); label.textContent = 'Past date · Check source for outcome'; event.append(label);
    }
  });
  render(false);
})();
