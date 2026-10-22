/* Talanoa has moved to https://chromaticmedia.us/Talanoa/ (2026-10-22).
   A phone that installed Talanoa from this old address still runs the old offline helper. When it checks for an
   update it gets this one instead, which clears the old copy, steps aside and opens the new address.
   Only Talanoa's own caches ("tt-...") go: Talanoa 2 and 3 live on this same website and keep theirs ("tt2-", "tt3-"). */
var HOME = 'https://chromaticmedia.us';
self.addEventListener('install', function () { self.skipWaiting(); });
self.addEventListener('activate', function (e) {
  e.waitUntil(self.clients.claim()
    .then(function () { return caches.keys(); })
    .then(function (keys) {
      return Promise.all(keys.filter(function (k) { return k.indexOf('tt-') === 0; }).map(function (k) { return caches.delete(k); }));
    })
    .then(function () { return self.clients.matchAll({ type: 'window' }); })
    .then(function (list) {
      return self.registration.unregister().then(function () {
        return Promise.all(list.map(function (c) {
          var u = new URL(c.url);
          return c.navigate(HOME + u.pathname + u.search + u.hash).catch(function () {});
        }));
      });
    }));
});
/* Until it has stepped aside, every request goes straight to the network (where the old address forwards). */
self.addEventListener('fetch', function () {});
