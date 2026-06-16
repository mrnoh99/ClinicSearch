#!/usr/bin/env python3
"""
reconcile.py — 공공데이터/학회명부 정신과 전문의 수집·정합(Entity Resolution)

대한신경정신의학회(KNPA) 전문의 명부 등 외부 소스의 인물 레코드를
기존 통합 DB의 전문의(specialist)와 정합(매칭·병합·중복제거)합니다.

정합 규칙:
  1) 결정적(deterministic) 매칭: 전문의자격번호 또는 면허번호 일치 → 동일인
  2) 확률적(probabilistic) 매칭: (정규화 이름) + (정규화 졸업대학) + (졸업연도 ±1) 일치 → 동일인
  3) 동명이인 처리: 이름은 같으나 졸업대학/졸업연도가 다르면 서로 다른 인물로 분리
  4) 권위(authority) 우선: 학회 명부의 자격/면허 정보가 시드 예시값을 갱신(출처 기록)

산출:
  - DB 갱신: 매칭된 전문의의 자격/면허 보강, 명부-only 신규 전문의 추가
  - 출처(provenance): 갱신/추가한 모든 필드를 data_source 에 기록
  - 리포트: db/export/reconciliation_report.json + 콘솔 요약
  - 앱 산출물(js/data.js, iOS, export JSON) 자동 재생성

사용:
  python3 db/build_db.py                 # 시드로 기본 DB 생성
  python3 db/scripts/reconcile.py        # 명부 정합(기본: db/sources/knpa_roster_sample.csv)
  python3 db/scripts/reconcile.py --roster /path/to/roster.csv
"""
import argparse
import csv
import datetime
import json
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB = os.path.join(ROOT, "db", "clinicsearch.db")
DEFAULT_ROSTER = os.path.join(ROOT, "db", "sources", "knpa_roster_sample.csv")
SOURCE_NAME = "대한신경정신의학회 전문의 명부"

# ----------------------------- 정규화 ----------------------------- #
def norm_name(s):
    return (s or "").strip().replace(" ", "")

def canon_school(s):
    s2 = (s or "").replace(" ", "")
    if "대학교" in s2:
        return s2.split("대학교")[0] + "대학교"   # '서울대학교 의과대학' → '서울대학교'
    return s2

def board_year(cert_no):
    parts = (cert_no or "").split("-")
    for p in parts:
        if len(p) == 4 and p.isdigit():
            return int(p)
    return None


# ------------------------- 소스 로더(명부) ------------------------- #
def load_roster(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "name": r["성명"].strip(),
                "gender": "M" if r.get("성별", "").startswith("남") else "F",
                "board_cert_no": r["전문의자격번호"].strip(),
                "license_no": r["면허번호"].strip(),
                "school": r["졸업대학"].strip(),
                "grad_year": int(r["졸업연도"]),
                "training_hospital": r["수련병원"].strip(),
                "org": r["현소속기관"].strip(),
                "region": r.get("지역", "").strip(),
                "subspecialty": r.get("세부전공", "").strip(),
            })
    return rows


# ----------------------- 기존 전문의 스냅샷 ----------------------- #
def load_existing(cur):
    people = []
    for sp in cur.execute("SELECT * FROM specialist").fetchall():
        edu = cur.execute(
            """SELECT school, year FROM specialist_education
               WHERE specialist_id=? AND degree LIKE '%의학사%' LIMIT 1""",
            (sp["id"],)).fetchone()
        people.append({
            "id": sp["id"], "name": sp["name"],
            "board_cert_no": sp["board_cert_no"], "license_no": sp["license_no"],
            "subspecialty_id": sp["subspecialty_id"], "hospital_id": sp["hospital_id"],
            "school": edu["school"] if edu else None,
            "grad_year": edu["year"] if edu else None,
        })
    return people


# ----------------------------- 매칭 ----------------------------- #
def match(rrow, existing):
    # 1) 결정적: 자격/면허 번호 일치
    for e in existing:
        if e["board_cert_no"] and e["board_cert_no"] == rrow["board_cert_no"]:
            return e, "deterministic:board_cert_no"
        if e["license_no"] and e["license_no"] == rrow["license_no"]:
            return e, "deterministic:license_no"
    # 2) 확률적: 이름 + 졸업대학 + 졸업연도(±1)
    cands = []
    for e in existing:
        if norm_name(e["name"]) == norm_name(rrow["name"]) \
           and canon_school(e["school"]) == canon_school(rrow["school"]) \
           and e["grad_year"] is not None \
           and abs(e["grad_year"] - rrow["grad_year"]) <= 1:
            cands.append(e)
    if len(cands) == 1:
        return cands[0], "probabilistic:name+school+gradYear"
    if len(cands) > 1:
        return None, "ambiguous"
    return None, "none"


def main():
    ap = argparse.ArgumentParser(description="정신과 전문의 명부 정합")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--roster", default=DEFAULT_ROSTER)
    ap.add_argument("--no-export", action="store_true", help="앱 산출물 재생성 생략")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        print("DB가 없습니다. 먼저 'python3 db/build_db.py' 실행하세요.")
        return 1
    if not os.path.exists(args.roster):
        print("명부 파일이 없습니다:", args.roster)
        return 1

    roster = load_roster(args.roster)
    con = sqlite3.connect(args.db)
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # 멱등성: 이전 명부 정합 결과 제거 후 재적용
    cur.execute("DELETE FROM data_source WHERE method LIKE '%명부%'")
    cur.execute("DELETE FROM specialist WHERE id LIKE 'knpa_%'")

    existing = load_existing(cur)
    psych_id = cur.execute("SELECT id FROM specialty WHERE name='정신건강의학과'").fetchone()
    psych_id = psych_id["id"] if psych_id else None

    def sub_id(name):
        r = cur.execute("SELECT id FROM subspecialty WHERE name=?", (name,)).fetchone()
        return r["id"] if r else None

    def add_source(sid, field, method, confidence="high", url="https://www.knpa.or.kr"):
        cur.execute(
            """INSERT INTO data_source(specialist_id,field,source,method,url,collected_at,confidence)
               VALUES (?,?,?,?,?, date('now'), ?)""",
            (sid, field, SOURCE_NAME, method, url, confidence))

    report = {"generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
              "roster_source": os.path.relpath(args.roster, ROOT), "roster_rows": len(roster),
              "matched": [], "new_specialists": [], "homonyms": [], "unmatched": []}

    # 동명이인 사전 탐지(이름은 같으나 졸업대학/연도가 다른 그룹)
    by_name = {}
    for r in roster:
        by_name.setdefault(norm_name(r["name"]), []).append(r)
    for nm, rs in by_name.items():
        keys = {(canon_school(r["school"]), r["grad_year"]) for r in rs}
        if len(keys) > 1:
            report["homonyms"].append({
                "name": rs[0]["name"], "count": len(rs),
                "distinguished_by": [f"{r['school']}/{r['grad_year']}/{r['region']}" for r in rs]})

    new_seq = 0
    for r in roster:
        e, how = match(r, existing)
        if e:  # ── 매칭: 권위 소스로 자격/면허 갱신
            changes = {}
            new_by = board_year(r["board_cert_no"])
            for col, val, field in [
                ("board_cert_no", r["board_cert_no"], "boardCert"),
                ("license_no", r["license_no"], "license"),
            ]:
                old = e[col]
                if old != val:
                    changes[col] = [old, val]
                    cur.execute(f"UPDATE specialist SET {col}=? WHERE id=?", (val, e["id"]))
                    add_source(e["id"], field, f"학회 명부 정합({how.split(':')[0]})")
            cur.execute(
                "UPDATE specialist SET board_cert_year=?, board_authority=? WHERE id=?",
                (new_by, "대한신경정신의학회/보건복지부", e["id"]))
            # 세부전공 비어 있으면 보강
            if e["subspecialty_id"] is None and r["subspecialty"]:
                sid2 = sub_id(r["subspecialty"])
                if sid2:
                    cur.execute("UPDATE specialist SET subspecialty_id=? WHERE id=?", (sid2, e["id"]))
            report["matched"].append({
                "name": e["name"], "specialist_id": e["id"], "method": how,
                "school": r["school"], "grad_year": r["grad_year"], "changes": changes})
        else:  # ── 명부-only 신규 인물 추가
            new_seq += 1
            sid = f"knpa_{new_seq:03d}"
            hosp = cur.execute(
                "SELECT id FROM hospital WHERE name=? OR name LIKE ?",
                (r["org"], r["org"] + "%")).fetchone()
            hospital_id = hosp["id"] if hosp else None
            cur.execute(
                """INSERT INTO specialist
                   (id,name,gender,hospital_id,specialty_id,subspecialty_id,
                    license_type,license_no,board_cert_no,board_cert_year,board_authority,
                    reputation,reviews)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (sid, r["name"], r["gender"], hospital_id, psych_id, sub_id(r["subspecialty"]),
                 "의사면허", r["license_no"], r["board_cert_no"], board_year(r["board_cert_no"]),
                 "대한신경정신의학회/보건복지부", 0, 0))
            cur.execute(
                "INSERT INTO specialist_education(specialist_id,degree,school,year) VALUES (?,?,?,?)",
                (sid, "의학사", r["school"], r["grad_year"]))
            cur.execute(
                "INSERT INTO specialist_training(specialist_id,role,hospital,start_year,end_year) VALUES (?,?,?,?,?)",
                (sid, "레지던트", r["training_hospital"], r["grad_year"] + 1, r["grad_year"] + 5))
            cur.execute(
                "INSERT INTO specialist_position(specialist_id,org,title,is_current) VALUES (?,?,?,1)",
                (sid, r["org"], "전문의"))
            if r["subspecialty"]:
                cur.execute("INSERT INTO specialist_interest(specialist_id,keyword) VALUES (?,?)",
                            (sid, r["subspecialty"]))
            add_source(sid, "roster", "학회 명부 수집·정합")
            add_source(sid, "affiliation",
                       "소속기관 매칭(명부→병원DB)" if hospital_id else "소속기관(병원DB 미등록)",
                       confidence="high" if hospital_id else "medium")
            report["new_specialists"].append({
                "id": sid, "name": r["name"], "school": r["school"], "grad_year": r["grad_year"],
                "affiliation": r["org"], "hospital_matched": bool(hospital_id),
                "homonym": len(by_name[norm_name(r["name"])]) > 1})

    con.commit()

    report["summary"] = {
        "matched": len(report["matched"]),
        "fields_updated": sum(len(m["changes"]) for m in report["matched"]),
        "new_specialists": len(report["new_specialists"]),
        "homonym_groups": len(report["homonyms"]),
        "total_specialists_after": cur.execute("SELECT count(*) FROM specialist").fetchone()[0],
    }

    out = os.path.join(ROOT, "db", "export")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "reconciliation_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    con.close()

    # 콘솔 요약
    s = report["summary"]
    print("=" * 56)
    print(f"  정신과 전문의 명부 정합 결과  (명부 {report['roster_rows']}건)")
    print("=" * 56)
    print(f"  ✓ 매칭·갱신   : {s['matched']}명 (필드 {s['fields_updated']}건 갱신)")
    print(f"  ✓ 신규 추가   : {s['new_specialists']}명")
    print(f"  ✓ 동명이인 그룹: {s['homonym_groups']}건")
    print(f"  ✓ DB 전문의 합 : {s['total_specialists_after']}명")
    if report["homonyms"]:
        print("  · 동명이인 분리:")
        for h in report["homonyms"]:
            print(f"     - {h['name']} ({h['count']}명): {', '.join(h['distinguished_by'])}")
    print(f"  → 리포트: db/export/reconciliation_report.json")

    # 앱 산출물 재생성 (정합 결과 반영)
    if not args.no_export:
        sys.path.insert(0, os.path.join(ROOT, "db"))
        try:
            import build_db
            build_db.export_webapp_data(args.db)
        except Exception as ex:
            print("앱 산출물 재생성 건너뜀:", ex)
    return 0


if __name__ == "__main__":
    sys.exit(main())
