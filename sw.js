/* Talanoa offline cache.
   sw.js is generated from tools/sw-template.js by tools/build.py; edit the template.

   Everything the board needs is kept on the tablet, so it keeps working with no
   internet. Voice clips go in their own cache ("tt-voices") that survives app
   updates; the page fills it for whichever voice is selected. */
var VERSION = '72e2a85298f1';
var CACHE = 'tt-app-' + VERSION;
var VOICE_CACHE = 'tt-voices';
var PRECACHE = [
 "./",
 "index.html",
 "credits.html",
 "library.js",
 "assets.js",
 "manifest.webmanifest",
 "icons/icon-192.png",
 "icons/icon-512.png",
 "icons/icon-512-maskable.png",
 "img/1f300.webp",
 "img/1f319.webp",
 "img/1f333.webp",
 "img/1f34e.webp",
 "img/1f354.webp",
 "img/1f355.webp",
 "img/1f357.webp",
 "img/1f35d.webp",
 "img/1f35f.webp",
 "img/1f366.webp",
 "img/1f372.webp",
 "img/1f373.webp",
 "img/1f37d-fe0f.webp",
 "img/1f37f.webp",
 "img/1f389.webp",
 "img/1f392.webp",
 "img/1f39f-fe0f.webp",
 "img/1f3a7.webp",
 "img/1f3a8.webp",
 "img/1f3ad.webp",
 "img/1f3ae.webp",
 "img/1f3b3.webp",
 "img/1f3b5.webp",
 "img/1f3c0.webp",
 "img/1f3ca.webp",
 "img/1f3d4-fe0f.webp",
 "img/1f3d8-fe0f.webp",
 "img/1f3de-fe0f.webp",
 "img/1f3e0.webp",
 "img/1f3e1.webp",
 "img/1f3ea.webp",
 "img/1f40d.webp",
 "img/1f415.webp",
 "img/1f434.webp",
 "img/1f437.webp",
 "img/1f440.webp",
 "img/1f441-fe0f.webp",
 "img/1f442.webp",
 "img/1f449.webp",
 "img/1f44b.webp",
 "img/1f44d.webp",
 "img/1f44e.webp",
 "img/1f455.webp",
 "img/1f45f.webp",
 "img/1f462.webp",
 "img/1f464.webp",
 "img/1f468.webp",
 "img/1f469.webp",
 "img/1f46a.webp",
 "img/1f474.webp",
 "img/1f475.webp",
 "img/1f47d.webp",
 "img/1f481.webp",
 "img/1f488.webp",
 "img/1f48a.webp",
 "img/1f49b.webp",
 "img/1f4a1.webp",
 "img/1f4a7.webp",
 "img/1f4aa.webp",
 "img/1f4b5.webp",
 "img/1f4c5.webp",
 "img/1f4d6.webp",
 "img/1f4da.webp",
 "img/1f4de.webp",
 "img/1f4f7.webp",
 "img/1f4fa.webp",
 "img/1f504.webp",
 "img/1f50c.webp",
 "img/1f50d.webp",
 "img/1f576-fe0f.webp",
 "img/1f57a.webp",
 "img/1f5bc-fe0f.webp",
 "img/1f5fa-fe0f.webp",
 "img/1f600.webp",
 "img/1f60a.webp",
 "img/1f60b.webp",
 "img/1f614.webp",
 "img/1f616.webp",
 "img/1f620.webp",
 "img/1f622.webp",
 "img/1f624.webp",
 "img/1f628.webp",
 "img/1f634.webp",
 "img/1f647.webp",
 "img/1f64b.webp",
 "img/1f64f.webp",
 "img/1f680.webp",
 "img/1f697.webp",
 "img/1f6aa.webp",
 "img/1f6b6.webp",
 "img/1f6bd.webp",
 "img/1f6bf.webp",
 "img/1f6c1.webp",
 "img/1f6cf-fe0f.webp",
 "img/1f6d2.webp",
 "img/1f912.webp",
 "img/1f914.webp",
 "img/1f915.webp",
 "img/1f917.webp",
 "img/1f91d.webp",
 "img/1f920.webp",
 "img/1f922.webp",
 "img/1f929.webp",
 "img/1f92b.webp",
 "img/1f92e.webp",
 "img/1f932.webp",
 "img/1f937.webp",
 "img/1f954.webp",
 "img/1f955.webp",
 "img/1f95b.webp",
 "img/1f961.webp",
 "img/1f964.webp",
 "img/1f968.webp",
 "img/1f96a.webp",
 "img/1f971.webp",
 "img/1f975.webp",
 "img/1f976.webp",
 "img/1f981.webp",
 "img/1f996.webp",
 "img/1f9b5.webp",
 "img/1f9b6.webp",
 "img/1f9b7.webp",
 "img/1f9c3.webp",
 "img/1f9d1-200d-1f91d-200d-1f9d1.webp",
 "img/1f9d1-200d-2695-fe0f.webp",
 "img/1f9d8.webp",
 "img/1f9e2.webp",
 "img/1f9e5.webp",
 "img/1f9ed.webp",
 "img/1f9f8.webp",
 "img/1f9fa.webp",
 "img/1f9fb.webp",
 "img/1f9fc.webp",
 "img/1f9fe.webp",
 "img/1fa79.webp",
 "img/1fa7a.webp",
 "img/1fa91.webp",
 "img/1faa5.webp",
 "img/1faf6.webp",
 "img/23ed-fe0f.webp",
 "img/23f0.webp",
 "img/23f3.webp",
 "img/2600-fe0f.webp",
 "img/2615.webp",
 "img/261d-fe0f.webp",
 "img/2705.webp",
 "img/270b.webp",
 "img/2753.webp",
 "img/2764-fe0f.webp",
 "img/2795.webp",
 "img/2b50.webp"
];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) {
    return c.addAll(PRECACHE.map(function (u) { return new Request(u, { cache: 'reload' }); }));
  }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) {
      return k.indexOf('tt-app-') === 0 && k !== CACHE;
    }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

/* The page asks which version is running (shown in Settings). */
self.addEventListener('message', function (e) {
  if (e.data === 'version' && e.ports && e.ports[0]) e.ports[0].postMessage({ version: VERSION });
});

/* Audio elements ask for byte ranges. Answer them from the full cached file. */
function slice(req, res) {
  var range = req.headers.get('range');
  if (!range || !res || res.status !== 200) return res;
  return res.arrayBuffer().then(function (buf) {
    var len = buf.byteLength, m = /bytes=(\d*)-(\d*)/.exec(range);
    if (!m) return new Response(buf, { status: 200, headers: res.headers });
    var start, end;
    if (m[1] === '') { start = Math.max(0, len - Number(m[2])); end = len - 1; }
    else { start = Number(m[1]); end = m[2] === '' ? len - 1 : Math.min(Number(m[2]), len - 1); }
    if (start >= len || start > end) {
      return new Response(null, { status: 416, headers: { 'Content-Range': 'bytes */' + len } });
    }
    return new Response(buf.slice(start, end + 1), { status: 206, headers: {
      'Content-Type': res.headers.get('Content-Type') || 'audio/mpeg',
      'Content-Range': 'bytes ' + start + '-' + end + '/' + len,
      'Content-Length': String(end - start + 1),
      'Accept-Ranges': 'bytes'
    }});
  });
}

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  if (url.pathname.indexOf('/voices/') !== -1) {
    /* Fetch the whole clip once (never a partial), keep it, then serve the range asked for. */
    e.respondWith(caches.open(VOICE_CACHE).then(function (c) {
      return c.match(url.href).then(function (hit) {
        if (hit) return hit;
        return fetch(url.href).then(function (res) {
          if (res.ok) c.put(url.href, res.clone());
          return res;
        });
      });
    }).then(function (res) { return slice(req, res); }));
    return;
  }

  e.respondWith(caches.match(req, { ignoreSearch: req.mode === 'navigate' }).then(function (hit) {
    return hit || fetch(req);
  }));
});
