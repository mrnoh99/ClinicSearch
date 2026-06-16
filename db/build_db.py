#!/usr/bin/env python3
"""
build_db.py — ClinicSearch 데이터베이스 빌더 / ETL

seed JSON(단일 진실 공급원)을 정규화된 SQLite DB로 적재하고,
다시 웹앱(js/data.js)·API용 JSON으로 내보냅니다.

사용법:
    python3 db/build_db.py                # DB 생성 + 웹앱 data.js 재생성
    python3 db/build_db.py --db custom.db # 출력 DB 경로 지정

데이터 수집(외부 API) 파이프라인:
    python3 db/scripts/ingest_hira.py     # 심평원 병원정보로 hospital 갱신
    python3 db/scripts/ingest_egen.py     # 응급의료포털 응급실/중환자실 갱신
    (수집 후 다시 build_db.py 로 내보내기)
"""
import argparse
import json
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_DIR = os.path.join(ROOT, "db", "seed")
SCHEMA = os.path.join(ROOT, "db", "schema.sql")
DEFAULT_DB = os.path.join(ROOT, "db", "clinicsearch.db")


def load_seed():
    with open(os.path.join(SEED_DIR, "hospitals.json"), encoding="utf-8") as f:
        hospitals = json.load(f)
    with open(os.path.join(SEED_DIR, "specialties.json"), encoding="utf-8") as f:
        specialties = json.load(f)
    return hospitals, specialties


def build(db_path):
    hospitals, specialties = load_seed()

    if os.path.exists(db_path):
        os.remove(db_path)
    con = sqlite3.connect(db_path)
    con.executescript(open(SCHEMA, encoding="utf-8").read())
    cur = con.cursor()

    # 전문과목 / 세부전공
    spec_id, sub_id = {}, {}
    for name, subs in specialties.items():
        cur.execute("INSERT INTO specialty(name) VALUES (?)", (name,))
        spec_id[name] = cur.lastrowid
        for s in subs:
            cur.execute(
                "INSERT INTO subspecialty(specialty_id, name) VALUES (?, ?)",
                (spec_id[name], s),
            )
            sub_id[(name, s)] = cur.lastrowid

    # 병원 / 매핑 / 의료진 / 경력
    for h in hospitals:
        cur.execute(
            """INSERT INTO hospital
               (id,name,type,address,lat,lng,phone,beds,er,er_level,icu,
                parking,transit,ambulance_bay,transfer_desk,avg_wait_min,source)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (h["id"], h["name"], h["type"], h["address"], h["lat"], h["lng"],
             h["phone"], h["beds"], int(h["er"]), h.get("erLevel"), int(h["icu"]),
             int(h["parking"]), h.get("transit"), int(h["ambulanceBay"]),
             int(h["transferDesk"]), h["avgWaitMin"], "seed"),
        )
        for sp in h["specialties"]:
            if sp in spec_id:
                cur.execute(
                    "INSERT OR IGNORE INTO hospital_specialty(hospital_id,specialty_id) VALUES (?,?)",
                    (h["id"], spec_id[sp]),
                )
        for d in h["doctors"]:
            cur.execute(
                """INSERT INTO doctor
                   (hospital_id,name,title,specialty_id,subspecialty_id,
                    school,grad_year,training,reputation,reviews)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (h["id"], d["name"], d["title"],
                 spec_id.get(d["specialty"]),
                 sub_id.get((d["specialty"], d["subspecialty"])),
                 d["school"], d["gradYear"], d["training"],
                 d["reputation"], d["reviews"]),
            )
            doc_id = cur.lastrowid
            for i, item in enumerate(d.get("career", [])):
                cur.execute(
                    "INSERT INTO doctor_career(doctor_id,seq,item) VALUES (?,?,?)",
                    (doc_id, i, item),
                )

    con.commit()

    # 통계
    n_h = cur.execute("SELECT count(*) FROM hospital").fetchone()[0]
    n_d = cur.execute("SELECT count(*) FROM doctor").fetchone()[0]
    n_s = cur.execute("SELECT count(*) FROM specialty").fetchone()[0]
    con.close()
    print(f"✅ DB 생성 완료: {db_path}")
    print(f"   병원 {n_h} · 의료진 {n_d} · 전문과목 {n_s}")


def export_webapp_data(db_path):
    """DB → 웹앱(js/data.js) 재생성: DB가 단일 진실 공급원이 되도록."""
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # 외부 루프는 fetchall()로 미리 구체화 — 중첩 쿼리가 커서를 리셋하지 않도록
    specialties = {}
    for sp in cur.execute("SELECT * FROM specialty ORDER BY id").fetchall():
        subs = [r["name"] for r in cur.execute(
            "SELECT name FROM subspecialty WHERE specialty_id=? ORDER BY id", (sp["id"],)).fetchall()]
        specialties[sp["name"]] = subs

    hospitals = []
    for h in cur.execute("SELECT * FROM hospital ORDER BY id").fetchall():
        specs = [r["name"] for r in cur.execute(
            """SELECT s.name FROM hospital_specialty hs
               JOIN specialty s ON s.id=hs.specialty_id WHERE hs.hospital_id=?""", (h["id"],)).fetchall()]
        doctors = []
        for d in cur.execute("SELECT * FROM doctor WHERE hospital_id=? ORDER BY id", (h["id"],)).fetchall():
            spec = cur.execute("SELECT name FROM specialty WHERE id=?", (d["specialty_id"],)).fetchone()
            sub = cur.execute("SELECT name FROM subspecialty WHERE id=?", (d["subspecialty_id"],)).fetchone()
            career = [r["item"] for r in cur.execute(
                "SELECT item FROM doctor_career WHERE doctor_id=? ORDER BY seq", (d["id"],)).fetchall()]
            doctors.append({
                "name": d["name"], "title": d["title"],
                "specialty": spec["name"] if spec else "",
                "subspecialty": sub["name"] if sub else "",
                "school": d["school"], "gradYear": d["grad_year"],
                "training": d["training"], "career": career,
                "reputation": d["reputation"], "reviews": d["reviews"],
            })
        hospitals.append({
            "id": h["id"], "name": h["name"], "type": h["type"], "address": h["address"],
            "lat": h["lat"], "lng": h["lng"], "phone": h["phone"], "beds": h["beds"],
            "er": bool(h["er"]), "erLevel": h["er_level"], "icu": bool(h["icu"]),
            "parking": bool(h["parking"]), "transit": h["transit"],
            "ambulanceBay": bool(h["ambulance_bay"]), "transferDesk": bool(h["transfer_desk"]),
            "avgWaitMin": h["avg_wait_min"], "specialties": specs, "doctors": doctors,
        })
    con.close()

    # API 소비용 JSON
    api_dir = os.path.join(ROOT, "db", "export")
    os.makedirs(api_dir, exist_ok=True)
    with open(os.path.join(api_dir, "hospitals.json"), "w", encoding="utf-8") as f:
        json.dump(hospitals, f, ensure_ascii=False, indent=2)
    print("✅ API JSON 내보내기: db/export/hospitals.json")

    # 웹앱용 data.js 재생성 (DB → 프런트엔드)
    h_js = json.dumps(hospitals, ensure_ascii=False, indent=2)
    s_js = json.dumps(specialties, ensure_ascii=False, indent=2)
    data_js = (
        "/**\n"
        " * data.js — 자동 생성 파일 (db/build_db.py 가 SQLite DB로부터 생성)\n"
        " * 직접 수정하지 마세요. 데이터는 db/seed 또는 DB에서 수정 후 빌드하세요.\n"
        " */\n"
        f"const SPECIALTIES = {s_js};\n\n"
        f"const HOSPITALS = {h_js};\n\n"
        "window.APP_DATA = { SPECIALTIES, HOSPITALS };\n"
    )
    with open(os.path.join(ROOT, "js", "data.js"), "w", encoding="utf-8") as f:
        f.write(data_js)
    print("✅ 웹앱 data.js 재생성: js/data.js")


def main():
    ap = argparse.ArgumentParser(description="ClinicSearch DB 빌더")
    ap.add_argument("--db", default=DEFAULT_DB, help="출력 SQLite 경로")
    ap.add_argument("--no-export", action="store_true", help="JSON 내보내기 생략")
    args = ap.parse_args()

    build(args.db)
    if not args.no_export:
        export_webapp_data(args.db)


if __name__ == "__main__":
    sys.exit(main())
