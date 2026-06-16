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
