'use strict';
document.documentElement.classList.replace('no-js', 'js');

const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#primary-navigation');
function closeMenu() {
  navigation.classList.remove('is-open');
  menuButton.setAttribute('aria-expanded', 'false');
}
menuButton.addEventListener('click', () => {
  const expanded = menuButton.getAttribute('aria-expanded') === 'true';
  navigation.classList.toggle('is-open', !expanded);
  menuButton.setAttribute('aria-expanded', String(!expanded));
});
navigation.addEventListener('click', (event) => {
  if (event.target.closest('a')) closeMenu();
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && navigation.classList.contains('is-open')) {
    closeMenu();
    menuButton.focus();
  }
});

const notice = document.querySelector('#site-notice');
function showNotice(title, message) {
  document.querySelector('#notice-title').textContent = title;
  document.querySelector('#notice-body').textContent = message;
  notice.showModal();
}
document.querySelectorAll('[data-notice]').forEach((link) => {
  link.addEventListener('click', (event) => {
    event.preventDefault();
    showNotice(link.dataset.noticeTitle, link.dataset.notice);
  });
});
document.querySelector('.notice-done').addEventListener('click', () => notice.close());
notice.addEventListener('click', (event) => {
  if (event.target === notice) {
    const bounds = notice.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right ||
        event.clientY < bounds.top || event.clientY > bounds.bottom) notice.close();
  }
});

// Share the actual sticky heights with native anchor navigation.
const stickyHeader = document.querySelector('.site-header');
const jumpBar = document.querySelector('.research-design-14, .faq-jump');
function measureStickyAreas() {
  document.documentElement.style.setProperty('--header-height', stickyHeader.getBoundingClientRect().height + 'px');
  const jumpHeight = jumpBar && getComputedStyle(jumpBar).position === 'sticky' ? jumpBar.getBoundingClientRect().height : 0;
  document.documentElement.style.setProperty('--jump-height', jumpHeight + 'px');
}
const stickyObserver = new ResizeObserver(measureStickyAreas);
stickyObserver.observe(stickyHeader);
if (jumpBar) stickyObserver.observe(jumpBar);
measureStickyAreas();
window.addEventListener('resize', measureStickyAreas);
// Re-align direct fragment visits once fonts and images have settled, unless the
// visitor has already started interacting with the page.
if (location.hash) {
  let interacted = false;
  for (const type of ['pointerdown', 'wheel', 'touchstart', 'keydown']) {
    window.addEventListener(type, () => { interacted = true; }, {once:true, passive:true});
  }
  window.addEventListener('load', async () => {
    await document.fonts.ready;
    if (interacted) return;
    measureStickyAreas();
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    document.getElementById(id)?.scrollIntoView({block:'start', behavior:'instant'});
  }, {once:true});
}
