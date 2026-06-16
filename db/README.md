# ClinicSearch 데이터베이스

병원·의료진 데이터를 **수집(ETL)** 하고 정규화된 **SQLite DB**로 관리한 뒤,
웹앱·iOS앱·API가 공유하는 단일 진실 공급원(single source of truth)으로 사용합니다.

> **현재 범위:** 정신건강의학과(정신과·신경정신과) 한정. 전문의(專門醫)를 중심 엔티티로
> 학력·수련·경력·학회·논문·자격을 통합하고, 각 자료의 **수집 출처(provenance)** 를 함께 기록합니다.

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
| `schema.sql` | 정규화 스키마(병원·전문의·학력·수련·경력·학회·논문·자격·출처) + 인덱스 + 뷰 |
| `seed/hospitals.json`, `seed/specialties.json` | 정신과 의료기관·세부전공 시드 |
| `seed/psychiatrists.json` | **정신과 전문의 통합 프로필**(사람 + 연결자료 + 출처) 시드 |
| `build_db.py` | 시드/DB → SQLite 빌드 후 `js/data.js`·`ios/.../HospitalData.swift`·`db/export/*.json` 생성 |
| `scripts/ingest_hira.py` | 심평원(HIRA) 병원정보서비스 수집 → `hospital` upsert |
| `scripts/ingest_egen.py` | 응급의료포털(E-Gen) 응급실/중환자실 정보 보강 |
| `scripts/ingest_specialists.py` | **전문의 자료 멀티소스 수집**(학회 명부·기관 홈페이지·PubMed 등) + 출처 기록 |
| `scripts/query.py` | DB 기반 전원 병원 검색 데모(앱과 동일 점수 로직) |

### 전문의(專門醫) 통합 모델

사람을 중심으로 연결된 모든 자료를 정규화하여 저장하고, `data_source` 테이블에
필드 단위로 **무엇을 / 어디서 / 어떤 방법으로 / 얼마나 신뢰**해 수집했는지 기록합니다.

| 테이블 | 내용 |
|--------|------|
| `specialist` | 전문의 핵심(면허·전문의 자격·소속·세부전공·평판) |
| `specialist_education` | 학력(의학사/석사/박사) |
| `specialist_training` | 수련(인턴/레지던트/전임의) |
| `specialist_position` | 경력/직위(현직 포함) |
| `specialist_society` | 학회 회원/임원 |
| `specialist_publication` | 논문/연구 |
| `specialist_certification` | 추가 자격/인증 |
| `specialist_interest` | 관심분야 |
| `data_source` | **출처(provenance)** — 필드별 출처·수집방법·URL·신뢰도 |
| `v_specialist_full` | 전문의 + 소속병원 + 논문/학회/출처 수 집계 뷰 |

수집 방법(가능한 모든 출처) 매핑:

- **전문의 자격/소속** ← 대한신경정신의학회(KNPA) 전문의 명부, 보건복지부 면허
- **근무기관/직위** ← 의료기관 홈페이지 의료진 소개, HIRA 병원별 의사 정보
- **논문/연구** ← PubMed E-utilities, KoreaMed, RISS (저자명·소속 매칭)
- **세부 자격/인증** ← 세부 학회(중독/수면/소아청소년/EMDR 등) 인증자 명단
- **평판/후기** ← 병원 리뷰 집계(이용약관 준수)

```bash
# 전문의 논문을 PubMed에서 수집해 특정 전문의에 연결(+출처 자동 기록)
python3 db/scripts/ingest_specialists.py --db db/clinicsearch.db \
        --pubmed "김현수" --affil "psychiatry" --specialist-id psy001
```

### 수집 → 정합(Entity Resolution) 워크플로

학회명부/공공데이터에서 전문의를 **수집**한 뒤, 기존 통합 DB와 **정합**(매칭·병합·중복제거)합니다.

```bash
# 1) 기본 DB 생성(시드)
python3 db/build_db.py

# 2) 수집: 학회명부/공공데이터 → 표준 명부 CSV
#    온라인(네트워크): KNPA 디렉터리 파서로 검색결과 페이지 순회·수집
python3 db/scripts/collect_knpa.py --region 서울 --out db/sources/knpa_roster.csv
#    오프라인: 저장한 디렉터리 HTML 파싱
python3 db/scripts/collect_knpa.py --fixture db/sources/fixtures/knpa_directory_page1.html \
        --out db/sources/knpa_roster.csv
#    명부 CSV 스키마/중복/결측 검증
python3 db/scripts/collect_knpa.py --validate db/sources/knpa_roster.csv

# 3) 정합: 명부 ↔ 통합 DB 매칭/병합 + 출처 기록 + 앱 산출물 재생성
python3 db/scripts/reconcile.py --roster db/sources/knpa_roster_sample.csv
```

#### KNPA 디렉터리 파서 (`knpa_parser.py`)

대한신경정신의학회 전문의 찾기 결과 페이지(HTML)를 표준 명부 스키마로 변환합니다.

- **순수 함수** `parse_directory_html(html)` — HTML → 레코드(네트워크 불필요, 픽스처로 검증).
- **헤더 라벨 매핑** — `전문의번호/출신대학/소속기관/전문분야` 등 표기 변형을 흡수(열 순서 무관).
- **표(table)·카드(div) 레이아웃** 모두 대응, 중첩 태그·`<br>`·공백 정리, 동명이인 보존(중복만 제거).
- **`KNPAClient`** — 검색 URL 템플릿(`{page}`)·지역 필터·페이지네이션·rate-limit 처리(라이브 수집).
  실제 사이트 DOM/엔드포인트에 맞춰 `HEADER_ALIASES`와 `KNPAClient.DEFAULT_SEARCH`만 조정하면 됩니다.

```bash
# 파서 단위 검증(저장된 픽스처로 즉시 재현)
python3 db/scripts/knpa_parser.py --fixture db/sources/fixtures/knpa_directory_page1.html
python3 db/scripts/test_knpa_parser.py     # 자체 테스트(표/변형헤더/카드/동명이인)

# 라이브 수집(네트워크 가능 환경) — 검색 URL 템플릿 지정 가능
python3 db/scripts/collect_knpa.py --search-url 'https://www.knpa.or.kr/.../search?page={page}' \
        --region 서울 --max-pages 50 --out db/sources/knpa_roster.csv
```

> 검증: 픽스처(6건) 파싱 → CSV → 정합 시 기존 2명 매칭, 신규 4명 추가, 동명이인 김현수
> (서울대/1998 ↔ 경북대/2005) 분리까지 정상 동작 확인.

**정합 규칙**
1. 결정적 매칭 — 전문의자격번호 또는 면허번호 일치 → 동일인
2. 확률적 매칭 — (정규화 이름)+(정규화 졸업대학)+(졸업연도 ±1) 일치 → 동일인
3. 동명이인 — 이름이 같아도 졸업대학/연도가 다르면 별개 인물로 분리
4. 권위 우선 — 학회명부의 자격/면허가 시드 예시값을 갱신하고 `data_source`에 출처 기록

> 표준 명부 CSV 스키마: `성명,성별,전문의자격번호,면허번호,졸업대학,졸업연도,수련병원,현소속기관,지역,세부전공`
> 동명이인 정합 정확도를 위해 (이름+졸업대학+졸업연도+소속기관/면허번호)를 함께 사용합니다.

**정합 결과(샘플 명부 18건 기준):** 매칭·갱신 14명(필드 28건), 신규 4명, 동명이인 1그룹(박민호 2명 분리),
총 18명 → 상세 리포트는 `db/export/reconciliation_report.json`.

> ⚠️ 현 실행 환경은 아웃바운드 네트워크가 차단(403)되어 라이브 수집은 불가합니다.
> 동봉한 `db/sources/knpa_roster_sample.csv`(실제 명부 스키마)로 정합을 즉시 재현할 수 있으며,
> 네트워크·키가 있는 환경에서 `collect_knpa.py`가 동일 스키마로 라이브 수집합니다.

> 동명이인 구분을 위해 (이름 + 면허번호/소속기관 + 졸업학교)로 엔티티를 정합합니다.
> 모든 수집은 출처별 이용약관·로봇정책·개인정보 보호를 준수해야 합니다.
> 현재 시드의 면허/자격번호는 예시값이며, 실데이터로 교체해야 합니다.

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
