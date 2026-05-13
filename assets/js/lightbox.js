// Click-to-enlarge for book covers.
// On click, opens the cover in a full-screen overlay. Close by clicking
// the overlay, the × button, or pressing Escape.
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var covers = document.querySelectorAll('.cover-large');
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
      c.style.cursor = 'zoom-in';
      c.addEventListener('click', function () {
        open(c.src, c.alt);
      });
    });
  });
})();
