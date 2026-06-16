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
