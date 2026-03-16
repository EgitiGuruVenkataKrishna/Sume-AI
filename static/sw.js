/*
 * Sume AI — Service Worker
 * Caches the app shell for offline launch and uses network-first for API calls.
 */

const CACHE_VERSION = 'sume-ai-v2';
const APP_SHELL = [
    '/',
    '/static/styles.css',
    '/static/manifest.json',
];

// Google Fonts to cache
const FONT_URLS = [
    'https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600;700&display=swap',
];

// ── Install: Cache app shell ────────────────────────────────────────────────
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_VERSION).then((cache) => {
            return cache.addAll(APP_SHELL);
        })
    );
    self.skipWaiting();
});

// ── Activate: Clean old caches ──────────────────────────────────────────────
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys
                    .filter((key) => key !== CACHE_VERSION)
                    .map((key) => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

// ── Fetch: Network-first for API, cache-first for assets ────────────────────
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Skip non-GET requests
    if (event.request.method !== 'GET') return;

    // API calls: network only (don't cache analysis results in SW)
    if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/analyze')) {
        return;
    }

    // App shell & assets: stale-while-revalidate
    event.respondWith(
        caches.match(event.request).then((cached) => {
            const fetchPromise = fetch(event.request)
                .then((response) => {
                    // Only cache successful responses
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_VERSION).then((cache) => {
                            cache.put(event.request, clone);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    // If offline and not cached, return a simple offline message
                    if (!cached && event.request.destination === 'document') {
                        return new Response(
                            '<html><body style="background:#070b14;color:#f1f5f9;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0"><div style="text-align:center"><h1>Sume AI</h1><p>You are offline. Please reconnect to analyze resumes.</p></div></body></html>',
                            { headers: { 'Content-Type': 'text/html' } }
                        );
                    }
                    return cached;
                });

            return cached || fetchPromise;
        })
    );
});
