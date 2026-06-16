/* ClinicSearch service worker — 오프라인 앱 셸 캐시 (아이패드 홈 화면 설치 지원) */
const CACHE = "clinicsearch-v1";
const ASSETS = [
  "./",
  "./index.html",
  "./css/styles.css",
  "./js/data.js",
  "./js/app.js",
  "./manifest.webmanifest",
  "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
  "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS).catch(() => {})));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const { request } = e;
  // 지도 타일·지오코딩 등 외부 API는 항상 네트워크
  if (request.url.includes("tile.openstreetmap") || request.url.includes("nominatim")) {
    return;
  }
  e.respondWith(
    caches.match(request).then((cached) => cached || fetch(request))
  );
});
