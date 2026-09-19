/* Google Analytics 4: public domain only; never track local previews.
   The gtag library is fetched on the first interaction, with a delayed fallback
   for engaged readers, so third-party code never competes with initial render.
   Config is queued immediately and flushes once the library loads. */
(() => {
  if (!['protectourpoconos.com', 'www.protectourpoconos.com'].includes(location.hostname)) return;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', 'G-XR259KZ2L9');

  let requested = false;
  function loadGtag() {
    if (requested) return;
    requested = true;
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=G-XR259KZ2L9';
    document.head.appendChild(tag);
  }
  for (const type of ['pointerdown', 'keydown', 'scroll', 'touchstart']) {
    window.addEventListener(type, loadGtag, { once: true, passive: true });
  }
  window.addEventListener('load', () => setTimeout(loadGtag, 30000), { once: true });
})();
