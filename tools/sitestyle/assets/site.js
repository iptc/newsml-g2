/* NewsML-G2 documentation site: search and the "On this page" highlight.

   Search covers the whole site: both books' section headings and the text
   under them, and the schema reference's elements and attributes. Each part's
   search-index.json is fetched on the first keystroke; a part that is missing
   (a book or the reference built on its own) is skipped. Matches in a heading
   or name rank above matches in text. */
(function () {
  var PARTS = [['specification', 'Specification'], ['guidelines', 'Guidelines'], ['reference', null]];
  var box = document.getElementById('q'), out = document.getElementById('r'), idx = null, sel = -1;

  function esc(s) {
    return s.replace(/[&<>"]/g, function (c) {
      return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c];
    });
  }

  function load() {
    if (idx) return idx;
    idx = Promise.all(PARTS.map(function (part) {
      return fetch('../' + part[0] + '/search-index.json')
        .then(function (r) { return r.ok ? r.json() : []; })
        .catch(function () { return []; })
        .then(function (entries) {
          return entries.map(function (e) {
            var book = !!part[1];
            return {
              u: '../' + part[0] + '/' + e.u, t: e.t, x: e.x || '', b: e.b || '', s: e.s || '',
              k: part[1] || (e.k === 'a' ? 'attribute' : 'element'),
              // a book result names its chapter; a reference result its scope and definition
              line: book ? (e.s || e.x || '') : [e.s, e.x].filter(Boolean).join(' — '),
              attr: e.k === 'a'
            };
          });
        });
    })).then(function (all) { return [].concat.apply([], all); });
    return idx;
  }

  function run() {
    var raw = box.value.trim().toLowerCase();
    var q = raw.replace(/^[@<]/, '');
    if (q.length < 2) { out.classList.remove('open'); out.innerHTML = ''; sel = -1; return; }
    load().then(function (entries) {
      if (box.value.trim().toLowerCase() !== raw) return;
      var hits = [];
      entries.forEach(function (e) {
        var t = e.t.toLowerCase().replace(/^[\d.]+\s*/, '').replace(/^[<@]/, '');
        var p = t.indexOf(q), rank;
        if (p > -1) rank = p === 0 ? 0 : 2;
        else if (e.x.toLowerCase().indexOf(q) > -1 || e.b.indexOf(q) > -1 ||
                 e.s.toLowerCase().indexOf(q) > -1) rank = 4;
        else return;
        hits.push({e: e, s: rank + (e.attr ? 1 : 0)});
      });
      hits.sort(function (a, b) { return a.s - b.s || a.e.t.length - b.e.t.length; });
      hits = hits.slice(0, 30); sel = -1;
      if (!hits.length) {
        out.innerHTML = '<div class="none">No match for &ldquo;' + esc(raw) + '&rdquo;</div>';
      } else {
        out.innerHTML = hits.map(function (h) {
          var e = h.e;
          return '<a href="' + esc(e.u) + '" title="' + esc(e.t + (e.line ? ' — ' + e.line : '')) + '">' +
            '<span class="kind">' + esc(e.k) + '</span><span class="t">' + esc(e.t) + '</span>' +
            '<span class="x">' + esc(e.line.slice(0, 120)) + '</span></a>';
        }).join('');
      }
      out.classList.add('open');
    });
  }

  if (box) {
    box.addEventListener('input', run);
    box.addEventListener('keydown', function (e) {
      var links = out.querySelectorAll('a');
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (!links.length) return;
        if (sel > -1) links[sel].classList.remove('sel');
        sel = e.key === 'ArrowDown' ? (sel + 1) % links.length : (sel <= 0 ? links.length - 1 : sel - 1);
        links[sel].classList.add('sel');
        links[sel].scrollIntoView({block: 'nearest'});
      } else if (e.key === 'Enter') {
        var go = links[sel > -1 ? sel : 0];
        if (go) { e.preventDefault(); go.click(); }
      } else if (e.key === 'Escape') {
        out.classList.remove('open'); box.blur();
      }
    });
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.search')) out.classList.remove('open');
    });
    document.addEventListener('keydown', function (e) {
      var tag = (document.activeElement || {}).tagName;
      if (e.key === '/' && document.activeElement !== box && tag !== 'INPUT' && tag !== 'TEXTAREA') {
        e.preventDefault(); box.focus();
      }
    });
  }

  // Highlight the "On this page" entry for the section on screen.
  var toc = {};
  [].forEach.call(document.querySelectorAll('nav.toc a'), function (a) {
    toc[decodeURIComponent(a.getAttribute('href').slice(1))] = a;
  });
  var heads = [].filter.call(document.querySelectorAll('main [id]'), function (h) { return toc[h.id]; });
  var pending = false, current = null;
  function mark() {
    pending = false;
    // the last heading scrolled past the top bar, or the first if none is
    var here = heads[0];
    for (var i = 0; i < heads.length && heads[i].getBoundingClientRect().top < 120; i++) here = heads[i];
    if (!here || here === current) return;
    if (current) toc[current.id].classList.remove('active');
    toc[here.id].classList.add('active');
    current = here;
    // keep it in view inside the column, without scrolling the page
    var link = toc[here.id], column = link.parentNode;
    if (link.offsetTop < column.scrollTop || link.offsetTop > column.scrollTop + column.clientHeight - 40)
      column.scrollTop = link.offsetTop - column.clientHeight / 3;
  }
  if (heads.length) {
    window.addEventListener('scroll', function () {
      if (!pending) { pending = true; requestAnimationFrame(mark); }
    }, {passive: true});
    mark();
  }
})();
