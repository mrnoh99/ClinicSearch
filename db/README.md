# ClinicSearch 데이터베이스

병원·의료진 데이터를 **수집(ETL)** 하고 정규화된 **SQLite DB**로 관리한 뒤,
웹앱·iOS앱·API가 공유하는 단일 진실 공급원(single source of truth)으로 사용합니다.

```
            ┌────────────────────┐
 외부 API → │  ingest_*.py (ETL) │ → SQLite(clinicsearch.db)
 (HIRA,     └────────────────────┘          │
  E-Gen)                                     ├─→ js/data.js        (웹앱)
            db/seed/*.json (수기/기본값) ─┘   ├─→ db/export/*.json  (REST API용)
                                              └─→ (iOS는 동일 스키마로 동기화)
```

## 구성

| 파일 | 설명 |
|------|------|
| `schema.sql` | 정규화 스키마(병원·의료진·전문과목·세부전공·경력·매핑) + 인덱스 + 뷰 |
| `seed/hospitals.json`, `seed/specialties.json` | 기본/수기 시드 데이터(단일 진실 공급원의 시작점) |
| `build_db.py` | 시드/DB → SQLite 빌드 후 `js/data.js`·`db/export/hospitals.json` 내보내기 |
| `scripts/ingest_hira.py` | 심평원(HIRA) 병원정보서비스 수집 → `hospital` upsert |
| `scripts/ingest_egen.py` | 응급의료포털(E-Gen) 응급실/중환자실 정보 보강 |
| `scripts/query.py` | DB 기반 전원 병원 검색 데모(앱과 동일 점수 로직) |

> 별도 패키지 설치가 필요 없습니다. Python 표준 라이브러리(sqlite3)만 사용합니다.

## 빠른 시작

```bash
# 1) 시드로부터 DB 빌드 + 프런트엔드/ API JSON 생성
python3 db/build_db.py

# 2) DB 기반 검색 테스트
python3 db/scripts/query.py --lat 37.5045 --lng 127.0492 --specialty 신경외과
```

## 실데이터 수집 파이프라인

```bash
# 공공데이터포털에서 서비스키 발급 후 환경변수 설정
export HIRA_SERVICE_KEY="발급키"
export EGEN_SERVICE_KEY="발급키"

# 전국/지역 병원 기본정보 수집 (예: 서울 110000)
python3 db/scripts/ingest_hira.py --db db/clinicsearch.db --sido 110000

# 응급실·중환자실 등급/가용병상 보강
python3 db/scripts/ingest_egen.py --db db/clinicsearch.db --stage1 서울특별시

# 수집 결과를 앱/ API로 다시 내보내기
python3 db/build_db.py --db db/clinicsearch.db
```

### 데이터 출처

- **건강보험심사평가원(HIRA)** 병원정보서비스 — 기관명, 종별, 주소, 좌표, 전화, 병상 수
- **국립중앙의료원 응급의료포털(E-Gen)** — 응급의료기관 등급, 실시간 응급실/중환자실 가용 병상
- **의료진 정보**(사진·졸업학교·졸업연도·수련병원·경력·평판) — 각 의료기관 제공 자료로 보강

> 공개 API의 데이터는 출처별 이용약관·사용량 제한을 준수해 사용하세요.
> 의료진 평판/후기 데이터는 신뢰 가능한 출처에서 수집·검증 후 반영해야 합니다.

## 스키마 요약

- `hospital` — 병원 기본정보 + 응급/접근성 플래그(er, icu, ambulance_bay, transfer_desk, avg_wait_min)
- `specialty` / `subspecialty` — 전문과목 / 세부전공(1:N)
- `hospital_specialty` — 병원-전문과목 매핑(N:M)
- `doctor` / `doctor_career` — 의료진 + 경력(1:N)
- `v_hospital_full` — 병원 + 전문과목 목록 + 의료진 수 집계 뷰
