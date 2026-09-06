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
