/* Service Worker – App-Shell offline + data.json network-first. */
const CACHE = "immo-v2";
const SHELL = [
  "mobile.html", "index.html", "styles.css", "app.js", "render.js",
  "firebase-config.js", "manifest.webmanifest",
  "icons/icon-192.png", "icons/icon-512.png"
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // Firebase u. a. -> direkt ans Netz

  // data.json: immer frisch versuchen, offline auf letzte Kopie zurueckfallen
  if (url.pathname.endsWith("data.json")) {
    e.respondWith(
      fetch(req).then((r) => {
        const copy = r.clone();
        caches.open(CACHE).then((c) => c.put("data.json", copy));
        return r;
      }).catch(() => caches.match("data.json", { ignoreSearch: true }))
    );
    return;
  }

  // Rest: cache-first mit Hintergrund-Aktualisierung
  e.respondWith(
    caches.match(req, { ignoreSearch: true }).then((cached) =>
      cached || fetch(req).then((r) => {
        const copy = r.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
        return r;
      })
    )
  );
});
