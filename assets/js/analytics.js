/* Google Analytics 4: public domain only; never track local previews. */
(() => {
  if (!['protectourpoconos.com', 'www.protectourpoconos.com'].includes(location.hostname)) return;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', 'G-XR259KZ2L9');
  const tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=G-XR259KZ2L9';
  document.head.appendChild(tag);
})();
