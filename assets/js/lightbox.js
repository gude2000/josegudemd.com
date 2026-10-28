// Click-to-enlarge for any image marked .cover-large (originally for book
// covers) or .zoomable (the general opt-in used elsewhere on the site —
// e.g. the Dalí painting thumbnails in the golden-ratio explainer, and the
// covers on Works in Progress). An image may name a larger file in
// data-full, which the overlay shows instead of the page-sized one.
// On click, opens the image in a full-screen overlay. Close by clicking
// the backdrop, the × button, or pressing Escape.
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var covers = document.querySelectorAll('.cover-large, .zoomable');
    if (!covers.length) return;

    var lb = document.createElement('div');
    lb.className = 'cover-lightbox';
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.innerHTML =
      '<button class="cover-lightbox-close" type="button" aria-label="Close">×</button>' +
      '<img alt="">';
    document.body.appendChild(lb);

    var img = lb.querySelector('img');
    var closeBtn = lb.querySelector('.cover-lightbox-close');

    function open(src, alt) {
      img.src = src;
      img.alt = alt || '';
      // Force reflow so opacity transition runs
      lb.style.display = 'flex';
      requestAnimationFrame(function () { lb.classList.add('open'); });
      document.body.style.overflow = 'hidden';
    }
    function close() {
      lb.classList.remove('open');
      document.body.style.overflow = '';
      // Hide fully after the transition completes
      setTimeout(function () {
        if (!lb.classList.contains('open')) lb.style.display = 'none';
      }, 260);
    }

    lb.addEventListener('click', function (e) {
      // Click anywhere on the backdrop or the close button closes the lightbox.
      // The image itself doesn't close, so the user can copy/save it if they want.
      if (e.target === lb || e.target === closeBtn) close();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') close();
    });

    covers.forEach(function (c) {
      // A larger file for the enlarged view, when the page names one.
      var full = c.getAttribute('data-full') || '';
      function show() { open(full || c.currentSrc || c.src, c.alt); }
      c.style.cursor = 'zoom-in';
      c.addEventListener('click', show);
      // Reachable from the keyboard too: Tab to the image, Enter or Space.
      if (!c.hasAttribute('tabindex')) c.setAttribute('tabindex', '0');
      c.setAttribute('role', 'button');
      c.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); show(); }
      });
    });
  });
})();
