'use strict';
(() => {
  const parts = Object.fromEntries(new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit'
  }).formatToParts(new Date()).map(part => [part.type, part.value]));
  const today = `${parts.year}-${parts.month}-${parts.day}`;
  document.querySelectorAll('[data-event-date]').forEach(card => {
    if (card.dataset.eventDate >= today) return;
    const note = document.createElement('p');
    note.className = 'past-event-note';
    note.textContent = 'This scheduled date has passed. Check the official source for the outcome and any new hearing dates.';
    card.prepend(note);
  });
})();
