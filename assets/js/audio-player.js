// Tiny inline audio-player wiring.
// Picks up any element with class "audio-mini" or "audio-full" and wires
// it as a click-to-play / click-to-seek player against the URL in data-src.
//
// HTML usage (full-page essay player at the top of the hero):
//   <div class="audio-full"
//        data-src="assets/audio/my-essay-en.mp3"
//        data-duration="12:34"
//        data-label="Listen to the full essay"></div>
//
// HTML usage (per-section mini player under an h2):
//   <div class="section-head">
//     <h2>N. Section title</h2>
//     <div class="audio-mini"
//          data-src="assets/audio/my-essay-sN-en.mp3"
//          data-duration="2:34"></div>
//   </div>
//
// Behaviors:
//   - Native <audio> with preload="none" — file is not downloaded until play.
//   - Full player shows elapsed/total; mini player counts down remaining.
//   - Click anywhere on the progress bar to seek.
//   - Play button toggles between ▶ and ‖‖.

(function () {
  function fmt(s) {
    var m = Math.floor(s / 60);
    var sec = Math.floor(s % 60);
    return m + ':' + (sec < 10 ? '0' : '') + sec;
  }

  function wire(el, isFull) {
    var src = el.getAttribute('data-src');
    var dur = el.getAttribute('data-duration') || '';
    var label = el.getAttribute('data-label') || '';
    var html = '';
    if (isFull && label) html += '<p class="label">' + label + '</p>';
    html += '<button class="play-btn" type="button" aria-label="Play">&#9654;</button>' +
            '<div class="progress"><div class="progress-fill"></div></div>' +
            '<span class="time">' + (isFull ? '0:00 / ' + dur : dur) + '</span>';
    el.innerHTML = html;

    var audio = new Audio();
    audio.preload = 'none';
    audio.src = src;
    var btn = el.querySelector('.play-btn');
    var prog = el.querySelector('.progress');
    var fill = el.querySelector('.progress-fill');
    var time = el.querySelector('.time');

    btn.addEventListener('click', function () {
      if (audio.paused) {
        audio.play();
        btn.innerHTML = '&#10074;&#10074;';
        btn.setAttribute('aria-label', 'Pause');
      } else {
        audio.pause();
        btn.innerHTML = '&#9654;';
        btn.setAttribute('aria-label', 'Play');
      }
    });

    audio.addEventListener('timeupdate', function () {
      if (audio.duration && isFinite(audio.duration)) {
        fill.style.width = (audio.currentTime / audio.duration * 100) + '%';
        if (isFull) {
          time.textContent = fmt(audio.currentTime) + ' / ' + fmt(audio.duration);
        } else {
          time.textContent = fmt(Math.max(0, audio.duration - audio.currentTime));
        }
      }
    });

    audio.addEventListener('ended', function () {
      btn.innerHTML = '&#9654;';
      btn.setAttribute('aria-label', 'Play');
      fill.style.width = '0%';
      time.textContent = isFull ? '0:00 / ' + dur : dur;
    });

    prog.addEventListener('click', function (e) {
      if (audio.duration && isFinite(audio.duration)) {
        var rect = prog.getBoundingClientRect();
        var pct = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width));
        audio.currentTime = pct * audio.duration;
      }
    });
  }

  function init() {
    document.querySelectorAll('.audio-mini').forEach(function (el) { wire(el, false); });
    document.querySelectorAll('.audio-full').forEach(function (el) { wire(el, true); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
