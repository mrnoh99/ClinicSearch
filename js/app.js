/**
 * app.js — 전원 병원 찾기 (ClinicSearch)
 * 거주지 주소 또는 현재 위치를 기준으로 조건에 맞는 가장 접근성 좋은 병원을 찾아줍니다.
 */
(function () {
  "use strict";

  const { SPECIALTIES, HOSPITALS } = window.APP_DATA;

  /* ---------------------------- 상태 ---------------------------- */
  const state = {
    origin: null,          // { lat, lng, label }
    specialty: "",         // 선택된 전문과목
    subspecialty: "",      // 선택된 세부전공
    requireER: false,      // 응급실 필수
    requireICU: false,     // 중환자실 필수
    sortBy: "score",       // score | distance
    maxKm: 0,              // 0 = 제한 없음
    results: [],
    selectedId: null
  };

  /* ------------------------- DOM 참조 --------------------------- */
  const $ = (sel) => document.querySelector(sel);
  const el = {
    addr: $("#addressInput"),
    geoBtn: $("#geoBtn"),
    searchBtn: $("#searchBtn"),
    specialty: $("#specialtySelect"),
    subspecialty: $("#subspecialtySelect"),
    requireER: $("#requireER"),
    requireICU: $("#requireICU"),
    sortBy: $("#sortBy"),
    maxKm: $("#maxKm"),
    list: $("#resultList"),
    count: $("#resultCount"),
    status: $("#statusMsg"),
    detail: $("#detailPanel"),
  };

  /* ------------------------- 지도 ------------------------------- */
  let map, originMarker;
  const hospitalMarkers = new Map(); // id -> marker

  function initMap() {
    map = L.map("map", { zoomControl: true }).setView([37.5665, 126.978], 11);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);
  }

  /* ----------------------- 거리/접근성 계산 --------------------- */
  // Haversine 직선거리 (km)
  function haversine(a, b) {
    const R = 6371;
    const dLat = ((b.lat - a.lat) * Math.PI) / 180;
    const dLng = ((b.lng - a.lng) * Math.PI) / 180;
    const lat1 = (a.lat * Math.PI) / 180;
    const lat2 = (b.lat * Math.PI) / 180;
    const h =
      Math.sin(dLat / 2) ** 2 +
      Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(h));
  }

  // 도심 평균속도(약 28km/h)를 가정한 예상 이동시간(분)
  function estDriveMin(km) {
    return Math.round((km / 28) * 60);
  }

  /**
   * 전원 적합도 점수 (0~100)
   * - 거리(가까울수록 ↑): 최대 45점
   * - 응급/중환자 인프라: 최대 25점
   * - 전원 접근성(구급차 진입로/전원코디/대중교통/주차): 최대 18점
   * - 대기시간(짧을수록 ↑): 최대 12점
   * 거리는 전원 결정의 핵심이므로 가장 큰 가중치를 둡니다.
   */
  function transferScore(h, km) {
    // 거리 점수: 0km=45점, 30km=0점 (선형)
    const distScore = Math.max(0, 45 * (1 - Math.min(km, 30) / 30));

    // 인프라 점수
    let infra = 0;
    if (h.er) infra += 10;
    if (h.erLevel === "권역응급의료센터") infra += 6;
    else if (h.erLevel === "지역응급의료센터") infra += 3;
    if (h.icu) infra += 9;
    infra = Math.min(infra, 25);

    // 접근성 점수
    let access = 0;
    if (h.ambulanceBay) access += 6;
    if (h.transferDesk) access += 6;
    if (h.parking) access += 3;
    if (h.transit) access += 3;
    access = Math.min(access, 18);

    // 대기시간 점수: 10분 이하 만점, 60분 이상 0점
    const waitScore = Math.max(0, 12 * (1 - Math.min(Math.max(h.avgWaitMin - 10, 0), 50) / 50));

    return Math.round(distScore + infra + access + waitScore);
  }

  /* ------------------------ 지오코딩 ---------------------------- */
  async function geocode(query) {
    const url =
      "https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=kr&q=" +
      encodeURIComponent(query);
    const res = await fetch(url, { headers: { "Accept-Language": "ko" } });
    if (!res.ok) throw new Error("지오코딩 요청 실패");
    const data = await res.json();
    if (!data.length) throw new Error("주소를 찾을 수 없습니다");
    return {
      lat: parseFloat(data[0].lat),
      lng: parseFloat(data[0].lon),
      label: data[0].display_name
    };
  }

  /* ------------------------ 검색/필터 --------------------------- */
  function runSearch() {
    if (!state.origin) {
      setStatus("먼저 거주지 주소를 입력하거나 현재 위치를 사용하세요.", "warn");
      return;
    }

    let list = HOSPITALS.filter((h) => {
      if (state.specialty && !h.specialties.includes(state.specialty)) return false;
      if (state.subspecialty) {
        const has = h.doctors.some(
          (d) => d.subspecialty === state.subspecialty
        );
        if (!has) return false;
      }
      if (state.requireER && !h.er) return false;
      if (state.requireICU && !h.icu) return false;
      return true;
    });

    list = list.map((h) => {
      const km = haversine(state.origin, h);
      return { ...h, km, driveMin: estDriveMin(km), score: transferScore(h, km) };
    });

    if (state.maxKm > 0) list = list.filter((h) => h.km <= state.maxKm);

    list.sort((a, b) =>
      state.sortBy === "distance" ? a.km - b.km : b.score - a.score || a.km - b.km
    );

    state.results = list;
    renderResults();
    renderMarkers();

    if (list.length) {
      setStatus(
        `${state.origin.label.split(",")[0]} 기준 ${list.length}개 병원을 찾았습니다.`,
        "ok"
      );
    } else {
      setStatus("조건에 맞는 병원이 없습니다. 필터를 완화해 보세요.", "warn");
    }
  }

  /* ------------------------ 렌더링 ------------------------------ */
  function setStatus(msg, kind) {
    el.status.textContent = msg;
    el.status.className = "status " + (kind || "");
  }

  function avatarSVG(name, seed) {
    // 이름 초성/첫 글자 기반 결정적 색상 아바타 (네트워크 불필요)
    const colors = ["#2563eb", "#0d9488", "#7c3aed", "#db2777", "#ea580c", "#0891b2", "#65a30d", "#9333ea"];
    const idx = (seed.charCodeAt(0) + (seed.charCodeAt(1) || 0)) % colors.length;
    const bg = colors[idx];
    const initial = name.slice(-2); // 한국 이름: 끝 두 글자
    return `data:image/svg+xml;utf8,${encodeURIComponent(
      `<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'>
        <rect width='120' height='120' rx='16' fill='${bg}'/>
        <text x='50%' y='54%' font-size='44' fill='#fff' font-family='sans-serif'
          text-anchor='middle' dominant-baseline='middle'>${initial}</text>
      </svg>`
    )}`;
  }

  function badge(text, cls) {
    return `<span class="badge ${cls || ""}">${text}</span>`;
  }

  function renderResults() {
    el.count.textContent = state.results.length;
    if (!state.results.length) {
      el.list.innerHTML = `<li class="empty">결과가 없습니다.</li>`;
      return;
    }
    el.list.innerHTML = state.results
      .map((h, i) => {
        const top = i === 0 ? badge("최적 전원지", "best") : "";
        const er = h.er ? badge("응급실", "er") : "";
        const icu = h.icu ? badge("중환자실", "icu") : "";
        return `
        <li class="card ${state.selectedId === h.id ? "active" : ""}" data-id="${h.id}" tabindex="0" role="button">
          <div class="card-head">
            <div>
              <div class="rank">#${i + 1}</div>
              <h3>${h.name} ${top}</h3>
              <div class="muted">${h.type} · ${h.address.split(" ").slice(0, 2).join(" ")}</div>
            </div>
            <div class="score" title="전원 적합도">
              <span class="score-num">${h.score}</span><span class="score-unit">점</span>
            </div>
          </div>
          <div class="metrics">
            <span>📍 ${h.km.toFixed(1)} km</span>
            <span>🚑 약 ${h.driveMin}분</span>
            <span>🛏 ${h.beds}병상</span>
            <span>⏱ 대기 ${h.avgWaitMin}분</span>
          </div>
          <div class="badges">${er}${icu}${h.erLevel ? badge(h.erLevel, "lvl") : ""}${h.transferDesk ? badge("전원코디", "co") : ""}</div>
        </li>`;
      })
      .join("");
  }

  function renderMarkers() {
    hospitalMarkers.forEach((m) => map.removeLayer(m));
    hospitalMarkers.clear();

    const group = [];
    if (state.origin) {
      if (originMarker) map.removeLayer(originMarker);
      originMarker = L.marker([state.origin.lat, state.origin.lng], {
        icon: L.divIcon({ className: "origin-pin", html: "🏠", iconSize: [30, 30] })
      })
        .addTo(map)
        .bindPopup("기준 위치<br>" + state.origin.label.split(",")[0]);
      group.push([state.origin.lat, state.origin.lng]);
    }

    state.results.forEach((h, i) => {
      const m = L.marker([h.lat, h.lng], {
        icon: L.divIcon({
          className: "hosp-pin" + (i === 0 ? " best" : ""),
          html: `<span>${i + 1}</span>`,
          iconSize: [28, 28]
        })
      }).addTo(map);
      m.bindPopup(
        `<b>${h.name}</b><br>${h.km.toFixed(1)}km · 약 ${h.driveMin}분<br>전원 적합도 ${h.score}점`
      );
      m.on("click", () => selectHospital(h.id));
      hospitalMarkers.set(h.id, m);
      group.push([h.lat, h.lng]);
    });

    if (group.length) map.fitBounds(group, { padding: [50, 50], maxZoom: 14 });
  }

  function renderDetail(h) {
    if (!h) {
      el.detail.innerHTML = `<div class="detail-empty">병원을 선택하면 의료진과 상세 정보가 표시됩니다.</div>`;
      return;
    }
    const docs = h.doctors
      .map(
        (d) => `
      <div class="doctor">
        <img class="doc-photo" src="${avatarSVG(d.name, d.name)}" alt="${d.name}"/>
        <div class="doc-info">
          <div class="doc-name">${d.name} <span class="doc-title">${d.title}</span></div>
          <div class="doc-spec">${d.specialty}${d.subspecialty ? " · " + d.subspecialty : ""}</div>
          <div class="rep">${stars(d.reputation)} <span class="muted">${d.reputation.toFixed(1)} (${d.reviews}건)</span></div>
          <ul class="doc-meta">
            <li>🎓 ${d.school} (${d.gradYear}년 졸업)</li>
            <li>🏥 수련: ${d.training}</li>
            ${d.career.map((c) => `<li>• ${c}</li>`).join("")}
          </ul>
        </div>
      </div>`
      )
      .join("");

    const naverUrl = `https://map.naver.com/v5/search/${encodeURIComponent(h.name)}`;
    const directionUrl = state.origin
      ? `https://map.kakao.com/link/to/${encodeURIComponent(h.name)},${h.lat},${h.lng}`
      : "#";

    el.detail.innerHTML = `
      <div class="detail-head">
        <h2>${h.name}</h2>
        <div class="muted">${h.type}</div>
      </div>
      <div class="facts">
        <div><span>주소</span>${h.address}</div>
        <div><span>전화</span><a href="tel:${h.phone}">${h.phone}</a></div>
        <div><span>거리</span>${h.km ? h.km.toFixed(1) + " km · 약 " + h.driveMin + "분" : "-"}</div>
        <div><span>병상</span>${h.beds}병상</div>
        <div><span>응급</span>${h.er ? (h.erLevel || "응급실 운영") : "응급실 없음"}</div>
        <div><span>중환자실</span>${h.icu ? "운영" : "없음"}</div>
        <div><span>교통</span>${h.transit || "-"}</div>
        <div><span>주차</span>${h.parking ? "가능" : "불가"}</div>
      </div>
      <div class="transfer-box">
        <div class="transfer-title">전원 접근성</div>
        <div class="badges">
          ${h.ambulanceBay ? badge("구급차 전용 진입로", "co") : ""}
          ${h.transferDesk ? badge("전원 전담 코디네이터", "co") : ""}
          ${badge("평균 대기 " + h.avgWaitMin + "분", "lvl")}
          ${badge("적합도 " + (h.score || transferScore(h, h.km || 0)) + "점", "best")}
        </div>
      </div>
      <div class="actions">
        <a class="btn" href="${directionUrl}" target="_blank" rel="noopener">🚗 길찾기</a>
        <a class="btn ghost" href="${naverUrl}" target="_blank" rel="noopener">🔎 지도에서 보기</a>
      </div>
      <h3 class="doctors-title">의료진 (${h.doctors.length}명)</h3>
      ${docs}
    `;
  }

  function stars(r) {
    const full = Math.round(r);
    return "★★★★★☆☆☆☆☆".slice(5 - full, 10 - full);
  }

  function selectHospital(id) {
    state.selectedId = id;
    const h = state.results.find((x) => x.id === id) || HOSPITALS.find((x) => x.id === id);
    renderResults();
    renderDetail(h);
    const m = hospitalMarkers.get(id);
    if (m) {
      map.setView(m.getLatLng(), 14, { animate: true });
      m.openPopup();
    }
    // 모바일/아이패드: 상세 패널로 스크롤
    if (window.innerWidth < 980) el.detail.scrollIntoView({ behavior: "smooth" });
  }

  /* ------------------------ 셀렉트 채우기 ----------------------- */
  function populateSpecialties() {
    const opts = ['<option value="">전체 전문과목</option>'];
    Object.keys(SPECIALTIES).forEach((s) => {
      opts.push(`<option value="${s}">${s}</option>`);
    });
    el.specialty.innerHTML = opts.join("");
  }

  function populateSubspecialties() {
    const subs = SPECIALTIES[state.specialty] || [];
    if (!state.specialty || !subs.length) {
      el.subspecialty.innerHTML = '<option value="">세부전공 전체</option>';
      el.subspecialty.disabled = true;
      return;
    }
    el.subspecialty.disabled = false;
    el.subspecialty.innerHTML =
      '<option value="">세부전공 전체</option>' +
      subs.map((s) => `<option value="${s}">${s}</option>`).join("");
  }

  /* ------------------------ 이벤트 ------------------------------ */
  function bindEvents() {
    el.geoBtn.addEventListener("click", () => {
      if (!navigator.geolocation) {
        setStatus("이 기기는 위치 기능을 지원하지 않습니다.", "warn");
        return;
      }
      setStatus("현재 위치를 확인하는 중...", "");
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          state.origin = {
            lat: pos.coords.latitude,
            lng: pos.coords.longitude,
            label: "현재 위치"
          };
          el.addr.value = "현재 위치 (GPS)";
          setStatus("현재 위치를 기준으로 설정했습니다.", "ok");
          runSearch();
        },
        () => setStatus("위치 권한이 거부되었습니다. 주소를 직접 입력하세요.", "warn"),
        { enableHighAccuracy: true, timeout: 10000 }
      );
    });

    el.searchBtn.addEventListener("click", doAddressSearch);
    el.addr.addEventListener("keydown", (e) => {
      if (e.key === "Enter") doAddressSearch();
    });

    el.specialty.addEventListener("change", (e) => {
      state.specialty = e.target.value;
      state.subspecialty = "";
      populateSubspecialties();
      if (state.origin) runSearch();
    });
    el.subspecialty.addEventListener("change", (e) => {
      state.subspecialty = e.target.value;
      if (state.origin) runSearch();
    });
    el.requireER.addEventListener("change", (e) => {
      state.requireER = e.target.checked;
      if (state.origin) runSearch();
    });
    el.requireICU.addEventListener("change", (e) => {
      state.requireICU = e.target.checked;
      if (state.origin) runSearch();
    });
    el.sortBy.addEventListener("change", (e) => {
      state.sortBy = e.target.value;
      if (state.origin) runSearch();
    });
    el.maxKm.addEventListener("change", (e) => {
      state.maxKm = parseFloat(e.target.value) || 0;
      if (state.origin) runSearch();
    });

    el.list.addEventListener("click", (e) => {
      const card = e.target.closest(".card");
      if (card) selectHospital(card.dataset.id);
    });
    el.list.addEventListener("keydown", (e) => {
      const card = e.target.closest(".card");
      if (card && (e.key === "Enter" || e.key === " ")) {
        e.preventDefault();
        selectHospital(card.dataset.id);
      }
    });
  }

  async function doAddressSearch() {
    const q = el.addr.value.trim();
    if (!q || q === "현재 위치 (GPS)") {
      setStatus("거주지 주소를 입력하세요.", "warn");
      return;
    }
    setStatus("주소를 검색하는 중...", "");
    try {
      state.origin = await geocode(q);
      runSearch();
    } catch (err) {
      setStatus("주소 검색 실패: " + err.message + " (예: '서울시 강남구 테헤란로 415')", "warn");
    }
  }

  /* ------------------------ 초기화 ------------------------------ */
  function init() {
    initMap();
    populateSpecialties();
    populateSubspecialties();
    bindEvents();
    renderDetail(null);
    setStatus("거주지 주소를 입력하거나 '현재 위치 사용'을 누르면 가까운 전원 병원을 찾아드립니다.", "");

    // PWA 서비스워커 등록 (아이패드 홈 화면 설치 지원)
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("./sw.js").catch(() => {});
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
