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
    specialists = []
    spec_path = os.path.join(SEED_DIR, "psychiatrists.json")
    if os.path.exists(spec_path):
        with open(spec_path, encoding="utf-8") as f:
            specialists = json.load(f)
    return hospitals, specialties, specialists


def build(db_path):
    hospitals, specialties, specialists = load_seed()

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
                parking,transit,ambulance_bay,transfer_desk,avg_wait_min,
                closed_ward,inpatient,psych_er,day_hospital,source)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (h["id"], h["name"], h["type"], h["address"], h["lat"], h["lng"],
             h["phone"], h["beds"], int(h["er"]), h.get("erLevel"), int(h["icu"]),
             int(h["parking"]), h.get("transit"), int(h["ambulanceBay"]),
             int(h["transferDesk"]), h["avgWaitMin"],
             int(h.get("closedWard", 0)), int(h.get("inpatient", 0)),
             int(h.get("psychER", 0)), int(h.get("dayHospital", 0)), "seed"),
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

    # 전문의 통합 프로필 (사람 중심 + 연결 자료 + 출처)
    for p in specialists:
        spname = p.get("specialty", "정신건강의학과")
        cur.execute(
            """INSERT INTO specialist
               (id,name,gender,hospital_id,specialty_id,subspecialty_id,
                license_type,license_no,license_year,
                board_cert_no,board_cert_year,board_authority,
                reputation,reviews,photo_url)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (p["id"], p["name"], p.get("gender"), p.get("hospitalId"),
             spec_id.get(spname),
             sub_id.get((spname, p.get("subspecialty"))),
             (p.get("license") or {}).get("type"),
             (p.get("license") or {}).get("no"),
             (p.get("license") or {}).get("year"),
             (p.get("boardCert") or {}).get("certNo"),
             (p.get("boardCert") or {}).get("year"),
             (p.get("boardCert") or {}).get("authority"),
             p.get("reputation", 0), p.get("reviews", 0), p.get("photoUrl")),
        )
        for e in p.get("education", []):
            cur.execute(
                "INSERT INTO specialist_education(specialist_id,degree,school,year,thesis) VALUES (?,?,?,?,?)",
                (p["id"], e.get("degree"), e.get("school"), e.get("year"), e.get("thesis")))
        for t in p.get("training", []):
            cur.execute(
                "INSERT INTO specialist_training(specialist_id,role,hospital,start_year,end_year) VALUES (?,?,?,?,?)",
                (p["id"], t.get("role"), t.get("hospital"), t.get("startYear"), t.get("endYear")))
        for po in p.get("positions", []):
            cur.execute(
                "INSERT INTO specialist_position(specialist_id,org,title,start_year,end_year,is_current) VALUES (?,?,?,?,?,?)",
                (p["id"], po.get("org"), po.get("title"), po.get("startYear"),
                 po.get("endYear"), int(po.get("current", False))))
        for so in p.get("societies", []):
            cur.execute(
                "INSERT INTO specialist_society(specialist_id,name,role) VALUES (?,?,?)",
                (p["id"], so.get("name"), so.get("role")))
        for pub in p.get("publications", []):
            cur.execute(
                "INSERT INTO specialist_publication(specialist_id,title,journal,year,role) VALUES (?,?,?,?,?)",
                (p["id"], pub.get("title"), pub.get("journal"), pub.get("year"), pub.get("role")))
        for c in p.get("certifications", []):
            cur.execute(
                "INSERT INTO specialist_certification(specialist_id,name,year) VALUES (?,?,?)",
                (p["id"], c.get("name"), c.get("year")))
        for kw in p.get("interests", []):
            cur.execute(
                "INSERT INTO specialist_interest(specialist_id,keyword) VALUES (?,?)",
                (p["id"], kw))
        for s in p.get("sources", []):
            cur.execute(
                """INSERT INTO data_source(specialist_id,field,source,method,url,collected_at,confidence)
                   VALUES (?,?,?,?,?,?,?)""",
                (p["id"], s.get("field"), s.get("source"), s.get("method"),
                 s.get("url"), s.get("collectedAt"), s.get("confidence")))

    con.commit()

    # 통계
    n_h = cur.execute("SELECT count(*) FROM hospital").fetchone()[0]
    n_d = cur.execute("SELECT count(*) FROM doctor").fetchone()[0]
    n_s = cur.execute("SELECT count(*) FROM specialty").fetchone()[0]
    n_sp = cur.execute("SELECT count(*) FROM specialist").fetchone()[0]
    n_src = cur.execute("SELECT count(*) FROM data_source").fetchone()[0]
    con.close()
    print(f"✅ DB 생성 완료: {db_path}")
    print(f"   병원 {n_h} · 의료진(요약) {n_d} · 전문과목 {n_s}")
    print(f"   전문의 통합프로필 {n_sp} · 출처기록 {n_src}")


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
            "closedWard": bool(h["closed_ward"]), "inpatient": bool(h["inpatient"]),
            "psychER": bool(h["psych_er"]), "dayHospital": bool(h["day_hospital"]),
            "avgWaitMin": h["avg_wait_min"], "specialties": specs, "doctors": doctors,
        })

    # 전문의 통합 프로필 내보내기 (사람 + 연결자료 + 출처)
    specialists = []
    for sp in cur.execute("SELECT * FROM specialist ORDER BY id").fetchall():
        sid = sp["id"]
        def rows(sql):
            return [dict(r) for r in cur.execute(sql, (sid,)).fetchall()]
        sub = cur.execute("SELECT name FROM subspecialty WHERE id=?", (sp["subspecialty_id"],)).fetchone()
        specialists.append({
            "id": sp["id"], "name": sp["name"], "gender": sp["gender"],
            "hospitalId": sp["hospital_id"], "subspecialty": sub["name"] if sub else None,
            "reputation": sp["reputation"], "reviews": sp["reviews"],
            "license": {"type": sp["license_type"], "no": sp["license_no"], "year": sp["license_year"]},
            "boardCert": {"certNo": sp["board_cert_no"], "year": sp["board_cert_year"],
                          "authority": sp["board_authority"]},
            "education": rows("SELECT degree,school,year,thesis FROM specialist_education WHERE specialist_id=? ORDER BY year"),
            "training": rows("SELECT role,hospital,start_year,end_year FROM specialist_training WHERE specialist_id=? ORDER BY start_year"),
            "positions": rows("SELECT org,title,start_year,end_year,is_current FROM specialist_position WHERE specialist_id=? ORDER BY is_current DESC,start_year DESC"),
            "societies": rows("SELECT name,role FROM specialist_society WHERE specialist_id=?"),
            "publications": rows("SELECT title,journal,year,role FROM specialist_publication WHERE specialist_id=? ORDER BY year DESC"),
            "certifications": rows("SELECT name,year FROM specialist_certification WHERE specialist_id=?"),
            "interests": [r["keyword"] for r in cur.execute(
                "SELECT keyword FROM specialist_interest WHERE specialist_id=?", (sid,)).fetchall()],
            "sources": rows("SELECT field,source,method,url,collected_at,confidence FROM data_source WHERE specialist_id=?"),
        })
    con.close()

    # API 소비용 JSON
    api_dir = os.path.join(ROOT, "db", "export")
    os.makedirs(api_dir, exist_ok=True)
    with open(os.path.join(api_dir, "hospitals.json"), "w", encoding="utf-8") as f:
        json.dump(hospitals, f, ensure_ascii=False, indent=2)
    with open(os.path.join(api_dir, "specialists.json"), "w", encoding="utf-8") as f:
        json.dump(specialists, f, ensure_ascii=False, indent=2)
    print("✅ API JSON 내보내기: db/export/hospitals.json, db/export/specialists.json")

    # 웹앱용 data.js 재생성 (DB → 프런트엔드)
    h_js = json.dumps(hospitals, ensure_ascii=False, indent=2)
    s_js = json.dumps(specialties, ensure_ascii=False, indent=2)
    p_js = json.dumps(specialists, ensure_ascii=False, indent=2)
    data_js = (
        "/**\n"
        " * data.js — 자동 생성 파일 (db/build_db.py 가 SQLite DB로부터 생성)\n"
        " * 직접 수정하지 마세요. 데이터는 db/seed 또는 DB에서 수정 후 빌드하세요.\n"
        " */\n"
        f"const SPECIALTIES = {s_js};\n\n"
        f"const HOSPITALS = {h_js};\n\n"
        f"const SPECIALISTS = {p_js};\n\n"
        "window.APP_DATA = { SPECIALTIES, HOSPITALS, SPECIALISTS };\n"
    )
    with open(os.path.join(ROOT, "js", "data.js"), "w", encoding="utf-8") as f:
        f.write(data_js)
    print("✅ 웹앱 data.js 재생성: js/data.js")

    # iOS 네이티브 앱용 HospitalData.swift 재생성 (DB → SwiftUI)
    _export_swift(hospitals, specialties)


def _swift_str(v):
    if v is None:
        return "nil"
    s = str(v).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def _export_swift(hospitals, specialties):
    """DB로부터 ios/ClinicSearch/HospitalData.swift 생성 (요약 데이터)."""
    lines = [
        "// HospitalData.swift — 자동 생성 파일 (db/build_db.py 가 SQLite DB로부터 생성)",
        "// 직접 수정하지 마세요. 데이터는 db/seed 또는 DB에서 수정 후 빌드하세요.",
        "import Foundation",
        "",
        "/// 전문과목 → 세부전공 매핑",
        "let SPECIALTIES: [(name: String, subs: [String])] = [",
    ]
    for name, subs in specialties.items():
        subs_s = ", ".join(_swift_str(s) for s in subs)
        lines.append(f'    ({_swift_str(name)}, [{subs_s}]),')
    if specialties:
        lines[-1] = lines[-1].rstrip(",")
    lines += ["]", "", "/// 병원·의료진 데이터 (DB 생성)", "let HOSPITALS: [Hospital] = ["]

    for h in hospitals:
        specs = ", ".join(_swift_str(s) for s in h["specialties"])
        docs = []
        for d in h["doctors"]:
            career = ", ".join(_swift_str(c) for c in d["career"])
            docs.append(
                "            Doctor(name: {name}, title: {title}, specialty: {sp}, subspecialty: {sub},\n"
                "                   school: {school}, gradYear: {gy},\n"
                "                   training: {tr},\n"
                "                   career: [{career}],\n"
                "                   reputation: {rep}, reviews: {rev})".format(
                    name=_swift_str(d["name"]), title=_swift_str(d["title"]),
                    sp=_swift_str(d["specialty"]), sub=_swift_str(d["subspecialty"]),
                    school=_swift_str(d["school"]), gy=d["gradYear"],
                    tr=_swift_str(d["training"]), career=career,
                    rep=d["reputation"], rev=d["reviews"]))
        docs_s = ",\n".join(docs)
        lines.append(
            "    Hospital(id: {id}, name: {name}, type: {ty}, address: {addr},\n"
            "             lat: {lat}, lng: {lng}, phone: {phone}, beds: {beds},\n"
            "             er: {er}, erLevel: {erl}, icu: {icu}, parking: {pk}, transit: {tr},\n"
            "             ambulanceBay: {ab}, transferDesk: {td}, avgWaitMin: {aw},\n"
            "             closedWard: {cw}, inpatient: {inp}, psychER: {pe}, dayHospital: {dh},\n"
            "             specialties: [{specs}],\n"
            "             doctors: [\n{docs}\n             ]),".format(
                id=_swift_str(h["id"]), name=_swift_str(h["name"]), ty=_swift_str(h["type"]),
                addr=_swift_str(h["address"]), lat=h["lat"], lng=h["lng"],
                phone=_swift_str(h["phone"]), beds=h["beds"],
                er=str(h["er"]).lower(), erl=_swift_str(h["erLevel"]), icu=str(h["icu"]).lower(),
                pk=str(h["parking"]).lower(), tr=_swift_str(h["transit"]),
                ab=str(h["ambulanceBay"]).lower(), td=str(h["transferDesk"]).lower(), aw=h["avgWaitMin"],
                cw=str(h["closedWard"]).lower(), inp=str(h["inpatient"]).lower(),
                pe=str(h["psychER"]).lower(), dh=str(h["dayHospital"]).lower(),
                specs=specs, docs=docs_s))
    lines.append("]")
    lines.append("")

    out = os.path.join(ROOT, "ios", "ClinicSearch", "HospitalData.swift")
    if os.path.isdir(os.path.dirname(out)):
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print("✅ iOS HospitalData.swift 재생성: ios/ClinicSearch/HospitalData.swift")


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
