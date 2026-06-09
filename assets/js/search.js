// Tiny client-side site search.
// Loads a prebuilt JSON index (~50 KB) and matches user queries
// by AND-of-terms across title / eyebrow / description / snippet.
// Highlights matches in the displayed snippet with <mark>.

(function () {
  const STR = {
    en: {
      typing: 'type to search',
      empty: 'No matches. Try a different word.',
      counts: (n) => `${n} match${n === 1 ? '' : 'es'}`,
      passQ: 'or pass ?q=term in the URL',
    },
    es: {
      typing: 'escribe para buscar',
      empty: 'Sin coincidencias. Prueba otra palabra.',
      counts: (n) => `${n} coincidencia${n === 1 ? '' : 's'}`,
      passQ: 'o pasa ?q=término en la URL',
    },
  };

  function normalize(s) {
    return (s || '')
      .toLowerCase()
      .normalize('NFD').replace(/[̀-ͯ]/g, '')   // strip accents
      .replace(/[^\p{L}\p{N}\s'’-]/gu, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function escapeHtml(s) {
    return (s || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function highlight(text, terms) {
    if (!terms.length) return escapeHtml(text);
    let out = escapeHtml(text);
    // build a single regex that matches any of the (escaped) terms, case-insensitive,
    // accent-insensitive via Unicode property classes — simplest path: do it once per term
    terms.sort((a, b) => b.length - a.length); // long terms first
    for (const t of terms) {
      if (!t) continue;
      // accent-insensitive match: build a permissive regex via a class for each character
      const re = new RegExp('(' + t.split('').map(c => {
        const cc = c.toLowerCase();
        if (cc === 'a') return '[aáàâäãāå]';
        if (cc === 'e') return '[eéèêëē]';
        if (cc === 'i') return '[iíìîïī]';
        if (cc === 'o') return '[oóòôöõō]';
        if (cc === 'u') return '[uúùûüū]';
        if (cc === 'n') return '[nñ]';
        if (cc === 'c') return '[cç]';
        return c.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      }).join('') + ')', 'gi');
      out = out.replace(re, '<mark>$1</mark>');
    }
    return out;
  }

  function scoreEntry(entry, terms, normalizedFields) {
    let score = 0;
    for (const t of terms) {
      let any = false;
      if (normalizedFields.t.includes(t)) { score += 10; any = true; }
      if (normalizedFields.e.includes(t)) { score += 4; any = true; }
      if (normalizedFields.d.includes(t)) { score += 3; any = true; }
      if (normalizedFields.s.includes(t)) { score += 1; any = true; }
      if (!any) return 0; // AND semantics — every term must match somewhere
    }
    return score;
  }

  function render(results, terms, container, lang) {
    container.innerHTML = '';
    if (!results.length) {
      const li = document.createElement('li');
      li.className = 'search-empty';
      li.textContent = STR[lang].empty;
      container.appendChild(li);
      return;
    }
    for (const { entry } of results) {
      const li = document.createElement('li');
      li.className = 'search-result';
      const title = highlight(entry.t, terms);
      const eyebrow = entry.e ? highlight(entry.e, terms) : '';
      const snip = highlight(entry.d || entry.s || '', terms);
      li.innerHTML = `
        ${eyebrow ? `<div class="r-eyebrow">${eyebrow}</div>` : ''}
        <a class="r-title" href="${entry.u}">${title}</a>
        <p class="r-snippet">${snip}</p>
      `;
      container.appendChild(li);
    }
  }

  function searchIndex(index, q) {
    const norm = normalize(q);
    const terms = norm.split(' ').filter(Boolean);
    if (!terms.length) return [];
    const scored = [];
    for (const entry of index) {
      const nf = {
        t: normalize(entry.t),
        e: normalize(entry.e),
        d: normalize(entry.d),
        s: normalize(entry.s),
      };
      const score = scoreEntry(entry, terms, nf);
      if (score > 0) scored.push({ entry, score });
    }
    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, 40);
  }

  window.runSearch = function (cfg) {
    const lang = cfg.placeholderLang || 'en';
    const strs = STR[lang];
    const $q = document.getElementById('q');
    const $results = document.getElementById('results');
    const $meta = document.getElementById('meta');

    let index = null;
    let pendingQuery = null;

    // Detect the file:// case early — browsers block fetch() from file:// origins
    // for CORS reasons, so search will never work when previewing by double-clicking
    // an HTML file. Show a helpful message instead of letting the cryptic CORS error
    // fire through.
    if (window.location.protocol === 'file:') {
      $meta.innerHTML = 'search needs a local web server when previewing on disk &mdash; ' +
        'CORS blocks fetch() from file:// URLs. From this folder run ' +
        '<code>python3 -m http.server 8000</code> and open ' +
        '<code>http://localhost:8000/search.html</code>. (The deployed live site works fine.)';
      return;
    }

    fetch(cfg.indexUrl).then(r => {
      if (!r.ok) {
        throw new Error('HTTP ' + r.status + ' ' + r.statusText + ' for ' + cfg.indexUrl);
      }
      return r.text().then(txt => {
        try {
          return JSON.parse(txt);
        } catch (parseErr) {
          throw new Error('JSON parse failed for ' + cfg.indexUrl + ': ' + parseErr.message + ' (first 80 chars: ' + JSON.stringify(txt.slice(0, 80)) + ')');
        }
      });
    }).then(data => {
      index = data;
      if (pendingQuery !== null) doSearch(pendingQuery);
      // also seed from URL ?q=
      const url = new URL(window.location.href);
      const qParam = url.searchParams.get('q');
      if (qParam) {
        $q.value = qParam;
        doSearch(qParam);
      }
    }).catch(err => {
      $meta.textContent = 'index load failed — ' + (err.message || err);
      console.error('search index load failed', err);
    });

    function doSearch(q) {
      if (!index) { pendingQuery = q; return; }
      const terms = normalize(q).split(' ').filter(Boolean);
      const results = searchIndex(index, q);
      if (q.trim() === '') {
        $results.innerHTML = '';
        $meta.textContent = strs.typing + ' · ' + strs.passQ;
        return;
      }
      $meta.textContent = strs.counts(results.length);
      render(results, terms, $results, lang);
    }

    let t;
    $q.addEventListener('input', e => {
      clearTimeout(t);
      t = setTimeout(() => doSearch(e.target.value), 80);
    });
    $q.addEventListener('keydown', e => {
      if (e.key === 'Enter') doSearch($q.value);
    });
  };
})();
