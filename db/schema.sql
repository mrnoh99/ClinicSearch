-- ClinicSearch 데이터베이스 스키마 (SQLite)
-- 전원 병원 찾기용 병원 · 의료진 · 전문과목 정규화 스키마
-- 생성:  python3 db/build_db.py
PRAGMA foreign_keys = ON;

-- 전문과목 (26개 법정 전문과목)
CREATE TABLE IF NOT EXISTS specialty (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE              -- 예: 내과, 신경외과
);

-- 세부전공 (전문과목에 종속)
CREATE TABLE IF NOT EXISTS subspecialty (
    id           INTEGER PRIMARY KEY,
    specialty_id INTEGER NOT NULL REFERENCES specialty(id) ON DELETE CASCADE,
    name         TEXT NOT NULL,               -- 예: 뇌혈관, 소화기내과
    UNIQUE (specialty_id, name)
);

-- 병원(의료기관)
CREATE TABLE IF NOT EXISTS hospital (
    id             TEXT PRIMARY KEY,          -- 심평원 암호화요양기호 또는 내부 ID
    name           TEXT NOT NULL,
    type           TEXT,                      -- 상급종합병원/종합병원/병원 등
    address        TEXT,
    lat            REAL NOT NULL,
    lng            REAL NOT NULL,
    phone          TEXT,
    beds           INTEGER DEFAULT 0,         -- 허가 병상 수
    er             INTEGER DEFAULT 0,         -- 응급실 운영 (0/1)
    er_level       TEXT,                      -- 권역/지역 응급의료센터 등
    icu            INTEGER DEFAULT 0,         -- 중환자실 (0/1)
    parking        INTEGER DEFAULT 0,
    transit        TEXT,                      -- 대중교통 접근 설명
    ambulance_bay  INTEGER DEFAULT 0,         -- 구급차 전용 진입로
    transfer_desk  INTEGER DEFAULT 0,         -- 전원 전담 코디네이터
    avg_wait_min   INTEGER DEFAULT 0,         -- 평균 대기시간(분)
    -- 정신건강의학과 전원 전용 속성
    closed_ward    INTEGER DEFAULT 0,         -- 폐쇄/보호병동 운영 (0/1)
    inpatient      INTEGER DEFAULT 0,         -- 정신과 입원 가능 (0/1)
    psych_er       INTEGER DEFAULT 0,         -- 정신응급(24시간 정신과 응급) 대응 (0/1)
    day_hospital   INTEGER DEFAULT 0,         -- 낮병원 운영 (0/1)
    source         TEXT DEFAULT 'seed',       -- 데이터 출처 (seed/HIRA/E-Gen ...)
    updated_at     TEXT DEFAULT (datetime('now'))
);

-- 병원-전문과목 매핑 (다대다)
CREATE TABLE IF NOT EXISTS hospital_specialty (
    hospital_id  TEXT NOT NULL REFERENCES hospital(id) ON DELETE CASCADE,
    specialty_id INTEGER NOT NULL REFERENCES specialty(id) ON DELETE CASCADE,
    PRIMARY KEY (hospital_id, specialty_id)
);

-- 의료진
CREATE TABLE IF NOT EXISTS doctor (
    id              INTEGER PRIMARY KEY,
    hospital_id     TEXT NOT NULL REFERENCES hospital(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    title           TEXT,                     -- 교수/원장/과장
    specialty_id    INTEGER REFERENCES specialty(id),
    subspecialty_id INTEGER REFERENCES subspecialty(id),
    school          TEXT,                     -- 졸업학교
    grad_year       INTEGER,                  -- 졸업연도
    training        TEXT,                     -- 수련병원
    reputation      REAL DEFAULT 0,           -- 평판 0~5
    reviews         INTEGER DEFAULT 0,        -- 후기 수
    photo_url       TEXT
);

-- 의료진 경력 (1:N)
CREATE TABLE IF NOT EXISTS doctor_career (
    id         INTEGER PRIMARY KEY,
    doctor_id  INTEGER NOT NULL REFERENCES doctor(id) ON DELETE CASCADE,
    seq        INTEGER DEFAULT 0,
    item       TEXT NOT NULL
);

-- 조회 성능 인덱스
CREATE INDEX IF NOT EXISTS idx_hospital_geo       ON hospital(lat, lng);
CREATE INDEX IF NOT EXISTS idx_hospital_er         ON hospital(er, icu);
CREATE INDEX IF NOT EXISTS idx_doctor_hospital     ON doctor(hospital_id);
CREATE INDEX IF NOT EXISTS idx_doctor_specialty    ON doctor(specialty_id, subspecialty_id);
CREATE INDEX IF NOT EXISTS idx_hospspec_specialty  ON hospital_specialty(specialty_id);

-- 편의 뷰: 병원 + 전문과목 목록
CREATE VIEW IF NOT EXISTS v_hospital_full AS
SELECT h.*,
       (SELECT group_concat(s.name, ',')
          FROM hospital_specialty hs JOIN specialty s ON s.id = hs.specialty_id
         WHERE hs.hospital_id = h.id) AS specialties,
       (SELECT count(*) FROM doctor d WHERE d.hospital_id = h.id) AS doctor_count
FROM hospital h;

/* ================================================================== */
/*  전문의(專門醫) 중심 통합 프로필 — 사람과 연결된 모든 자료를 통합     */
/*  수집 출처는 data_source(provenance) 테이블에 필드 단위로 기록       */
/* ================================================================== */

-- 전문의 핵심 레코드
CREATE TABLE IF NOT EXISTS specialist (
    id               TEXT PRIMARY KEY,         -- psy001 ...
    name             TEXT NOT NULL,
    gender           TEXT,                     -- M/F
    hospital_id      TEXT REFERENCES hospital(id) ON DELETE SET NULL,  -- 현재 소속
    specialty_id     INTEGER REFERENCES specialty(id),
    subspecialty_id  INTEGER REFERENCES subspecialty(id),
    -- 면허 / 전문의 자격
    license_type     TEXT,                     -- 의사면허 등
    license_no       TEXT,                     -- 면허번호(예시/마스킹)
    license_year     INTEGER,
    board_cert_no    TEXT,                     -- 전문의 자격번호
    board_cert_year  INTEGER,                  -- 전문의 취득연도
    board_authority  TEXT,                     -- 발급기관
    reputation       REAL DEFAULT 0,
    reviews          INTEGER DEFAULT 0,
    photo_url        TEXT,
    updated_at       TEXT DEFAULT (datetime('now'))
);

-- 학력 (1:N)  의학사/석사/박사 등
CREATE TABLE IF NOT EXISTS specialist_education (
    id            INTEGER PRIMARY KEY,
    specialist_id TEXT NOT NULL REFERENCES specialist(id) ON DELETE CASCADE,
    degree        TEXT,                        -- 의학사/의학석사/의학박사
    school        TEXT,
    year          INTEGER,
    thesis        TEXT
);

-- 수련 (1:N)  인턴/레지던트/전임의
CREATE TABLE IF NOT EXISTS specialist_training (
    id            INTEGER PRIMARY KEY,
    specialist_id TEXT NOT NULL REFERENCES specialist(id) ON DELETE CASCADE,
    role          TEXT,                        -- 인턴/레지던트/전임의
    hospital      TEXT,                        -- 수련병원
    start_year    INTEGER,
    end_year      INTEGER
);

-- 경력 / 소속 (1:N)
CREATE TABLE IF NOT EXISTS specialist_position (
    id            INTEGER PRIMARY KEY,
    specialist_id TEXT NOT NULL REFERENCES specialist(id) ON DELETE CASCADE,
    org           TEXT,
    title         TEXT,
    start_year    INTEGER,
    end_year      INTEGER,
    is_current    INTEGER DEFAULT 0
);

-- 학회 회원/임원 (1:N)
CREATE TABLE IF NOT EXISTS specialist_society (
    id            INTEGER PRIMARY KEY,
    specialist_id TEXT NOT NULL REFERENCES specialist(id) ON DELETE CASCADE,
    name          TEXT,
    role          TEXT                         -- 정회원/이사/회원 등
);

-- 논문 / 연구 (1:N)
CREATE TABLE IF NOT EXISTS specialist_publication (
    id            INTEGER PRIMARY KEY,
    specialist_id TEXT NOT NULL REFERENCES specialist(id) ON DELETE CASCADE,
    title         TEXT,
    journal       TEXT,
    year          INTEGER,
    role          TEXT                         -- 제1저자/공저자/교신저자
);

-- 추가 자격/인증 (1:N)
CREATE TABLE IF NOT EXISTS specialist_certification (
    id            INTEGER PRIMARY KEY,
    specialist_id TEXT NOT NULL REFERENCES specialist(id) ON DELETE CASCADE,
    name          TEXT,
    year          INTEGER
);

-- 관심분야 (1:N, 자유 텍스트)
CREATE TABLE IF NOT EXISTS specialist_interest (
    id            INTEGER PRIMARY KEY,
    specialist_id TEXT NOT NULL REFERENCES specialist(id) ON DELETE CASCADE,
    keyword       TEXT
);

-- 데이터 출처(provenance) — "어떤 자료를 어떤 방법으로 어디서 수집했는가"
CREATE TABLE IF NOT EXISTS data_source (
    id            INTEGER PRIMARY KEY,
    specialist_id TEXT NOT NULL REFERENCES specialist(id) ON DELETE CASCADE,
    field         TEXT,                        -- 출처가 적용되는 필드(boardCert/positions/publications...)
    source        TEXT,                        -- 출처명(학회 명부/기관 홈페이지/PubMed...)
    method        TEXT,                        -- 수집 방법(명부 조회/홈페이지 수집/저자 검색...)
    url           TEXT,
    collected_at  TEXT,
    confidence    TEXT                         -- high/medium/low
);

CREATE INDEX IF NOT EXISTS idx_spec_hospital   ON specialist(hospital_id);
CREATE INDEX IF NOT EXISTS idx_spec_sub        ON specialist(subspecialty_id);
CREATE INDEX IF NOT EXISTS idx_src_specialist  ON data_source(specialist_id);

-- 통합 뷰: 전문의 + 소속병원 + 세부전공 + 학력/경력 수 집계
CREATE VIEW IF NOT EXISTS v_specialist_full AS
SELECT sp.id, sp.name, sp.gender, sp.reputation, sp.reviews,
       sp.board_cert_year, sp.board_cert_no,
       h.name AS hospital_name, h.address AS hospital_address,
       sub.name AS subspecialty,
       (SELECT org FROM specialist_position p
         WHERE p.specialist_id = sp.id AND p.is_current = 1 LIMIT 1) AS current_org,
       (SELECT count(*) FROM specialist_publication pu WHERE pu.specialist_id = sp.id) AS publication_count,
       (SELECT count(*) FROM specialist_society so WHERE so.specialist_id = sp.id) AS society_count,
       (SELECT count(*) FROM data_source ds WHERE ds.specialist_id = sp.id) AS source_count
FROM specialist sp
LEFT JOIN hospital h ON h.id = sp.hospital_id
LEFT JOIN subspecialty sub ON sub.id = sp.subspecialty_id;
