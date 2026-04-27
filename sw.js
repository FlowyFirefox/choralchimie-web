const CACHE_NAME = 'choralchimie-v1';
const PRECACHE_ASSETS = ['/accueil/', '/hub-chanteurs/', '/hub-musiciens/', '/planning/', '/manifest.json', '/assets/favicon_192_choralchimie.png', '/assets/favicon_512_choralchimie.png'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE_ASSETS).catch(err => console.warn('[SW] Précache partiel :', err))));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET') return;
  if (!url.origin.includes(self.location.origin)) return;
  const isHTML = event.request.headers.get('accept')?.includes('text/html');
  if (isHTML) {
    event.respondWith(fetch(event.request).then(r => { caches.open(CACHE_NAME).then(c => c.put(event.request, r.clone())); return r; }).catch(() => caches.match(event.request)));
  } else {
    event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request).then(r => { caches.open(CACHE_NAME).then(c => c.put(event.request, r.clone())); return r; })));
  }
});
