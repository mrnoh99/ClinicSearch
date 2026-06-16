#!/usr/bin/env python3
"""
query.py — DB 기반 전원 병원 검색 데모

SQLite DB에서 직접 거리·전원 적합도를 계산해 가까운 병원을 출력합니다.
웹/iOS 앱과 동일한 점수 로직을 DB 위에서 검증하는 용도입니다.

예시:
  python3 db/scripts/query.py --lat 37.5045 --lng 127.0492 --specialty 신경외과
  python3 db/scripts/query.py --lat 37.50 --lng 127.04 --er --icu --limit 5
"""
import argparse
import math
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "clinicsearch.db")


def haversine(lat1, lng1, lat2, lng2):
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(a))


def transfer_score(h, km):
    dist = max(0, 45 * (1 - min(km, 30) / 30))
    infra = 0
    if h["er"]: infra += 10
    if h["er_level"] == "권역응급의료센터": infra += 6
    elif h["er_level"] == "지역응급의료센터": infra += 3
    if h["icu"]: infra += 9
    infra = min(infra, 25)
    access = 0
    if h["ambulance_bay"]: access += 6
    if h["transfer_desk"]: access += 6
    if h["parking"]: access += 3
    if h["transit"]: access += 3
    access = min(access, 18)
    wait = max(0, 12 * (1 - min(max(h["avg_wait_min"] - 10, 0), 50) / 50))
    return round(dist + infra + access + wait)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lng", type=float, required=True)
    ap.add_argument("--specialty", default="")
    ap.add_argument("--subspecialty", default="")
    ap.add_argument("--er", action="store_true", help="응급실 필수")
    ap.add_argument("--icu", action="store_true", help="중환자실 필수")
    ap.add_argument("--max-km", type=float, default=0)
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--db", default=DB)
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    con.row_factory = sqlite3.Row

    sql = "SELECT DISTINCT h.* FROM hospital h"
    params = []
    where = []
    if args.specialty:
        sql += (" JOIN hospital_specialty hs ON hs.hospital_id=h.id"
                " JOIN specialty s ON s.id=hs.specialty_id")
        where.append("s.name=?"); params.append(args.specialty)
    if args.subspecialty:
        sql += (" JOIN doctor d ON d.hospital_id=h.id"
                " JOIN subspecialty sub ON sub.id=d.subspecialty_id")
        where.append("sub.name=?"); params.append(args.subspecialty)
    if args.er:
        where.append("h.er=1")
    if args.icu:
        where.append("h.icu=1")
    if where:
        sql += " WHERE " + " AND ".join(where)

    rows = con.execute(sql, params).fetchall()
    results = []
    for h in rows:
        km = haversine(args.lat, args.lng, h["lat"], h["lng"])
        if args.max_km and km > args.max_km:
            continue
        results.append((transfer_score(h, km), km, h))
    results.sort(key=lambda x: (-x[0], x[1]))

    print(f"\n기준 좌표 ({args.lat}, {args.lng}) — 조건에 맞는 전원 병원 {len(results)}곳\n")
    for i, (score, km, h) in enumerate(results[:args.limit], 1):
        drive = round(km / 28 * 60)
        flags = []
        if h["er"]: flags.append(h["er_level"] or "응급실")
        if h["icu"]: flags.append("중환자실")
        if h["transfer_desk"]: flags.append("전원코디")
        print(f"#{i}  [{score:3d}점] {h['name']}  ({h['type']})")
        print(f"      {km:5.1f} km · 약 {drive}분 · {h['beds']}병상 · 대기 {h['avg_wait_min']}분")
        print(f"      {' / '.join(flags) if flags else '-'}")
    con.close()


if __name__ == "__main__":
    main()
