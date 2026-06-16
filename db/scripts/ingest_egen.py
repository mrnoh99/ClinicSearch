#!/usr/bin/env python3
"""
ingest_egen.py — 응급의료포털(E-Gen) 실시간 응급실/중환자실 정보 수집기

국립중앙의료원 응급의료정보(E-Gen) OpenAPI로 응급실 운영 여부, 응급의료기관 등급,
실시간 가용 병상 등을 받아 hospital 테이블의 er / er_level / icu / avg_wait_min 등을 보강합니다.

준비:
  1) 공공데이터포털에서 '국립중앙의료원_전국 응급의료기관 정보 조회 서비스' 키 발급
  2) export EGEN_SERVICE_KEY="발급키"
  3) python3 db/scripts/ingest_egen.py --db db/clinicsearch.db --stage1 110000

참고 엔드포인트:
  - 응급실 실시간 가용정보: /getEmrrmRltmUsefulSckbdInfoInqire
  - 응급의료기관 기본정보:   /getEgytBassInfoInqire
주요 응답: dutyName(기관명), dutyEmcls(응급의료기관 분류),
          hvec(응급실 일반병상), hvicc(내과중환자실) 등 실시간 병상 수

매핑 규칙:
  - dutyEmcls 에 '권역응급의료센터' → er_level='권역응급의료센터', er=1
  - '지역응급의료센터' → er_level='지역응급의료센터', er=1
  - '지역응급의료기관' → er_level='지역응급의료기관', er=1
  - 중환자 병상(hvicc 등) > 0 → icu=1
"""
import argparse
import os
import sqlite3
import sys

BASE = "http://apis.data.go.kr/B552657/ErmctInfoInqireService"


def classify(emcls):
    for level in ("권역응급의료센터", "지역응급의료센터", "지역응급의료기관"):
        if emcls and level in emcls:
            return level
    return None


def fetch(service_key, stage1, page=1, rows=100):
    import urllib.request
    import urllib.parse
    import xml.etree.ElementTree as ET
    params = {
        "serviceKey": service_key,
        "STAGE1": stage1,         # 시도명 또는 코드(엔드포인트 규격에 맞춰 조정)
        "pageNo": page,
        "numOfRows": rows,
    }
    url = f"{BASE}/getEgytBassInfoInqire?" + urllib.parse.urlencode(params, safe="%")
    with urllib.request.urlopen(url, timeout=20) as r:
        xml = r.read().decode("utf-8")
    root = ET.fromstring(xml)
    out = []
    for item in root.iter("item"):
        get = lambda t: (item.findtext(t) or "").strip()
        out.append({
            "name": get("dutyName"),
            "emcls": get("dutyEmcls"),
            "tel": get("dutyTel1"),
            "icu_beds": sum(int(get(t) or 0) for t in ("hvicc", "hvncc", "hvccc", "hvicc")),
        })
    return out


def apply(con, recs):
    """기관명 매칭으로 응급/중환자 정보 보강 (운영 시 ykiho 매칭 권장)."""
    updated = 0
    for r in recs:
        level = classify(r["emcls"])
        cur = con.execute(
            """UPDATE hospital
                  SET er=1, er_level=COALESCE(?, er_level),
                      icu=CASE WHEN ?>0 THEN 1 ELSE icu END,
                      source='E-Gen', updated_at=datetime('now')
                WHERE name=?""",
            (level, r["icu_beds"], r["name"]),
        )
        updated += cur.rowcount
    con.commit()
    return updated


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/clinicsearch.db")
    ap.add_argument("--stage1", default="서울특별시", help="시도명 (예: 서울특별시)")
    args = ap.parse_args()

    key = os.environ.get("EGEN_SERVICE_KEY")
    if not key:
        print("⚠️  EGEN_SERVICE_KEY 환경변수가 없습니다.")
        print("    공공데이터포털에서 '전국 응급의료기관 정보 조회 서비스' 키를 발급받아 설정하세요.")
        return 1

    con = sqlite3.connect(args.db)
    try:
        recs = fetch(key, args.stage1)
    except Exception as e:
        print(f"요청 실패: {e}")
        con.close()
        return 1
    n = apply(con, recs)
    con.close()
    print(f"✅ E-Gen 보강 완료: 응급의료기관 {len(recs)}건 조회, {n}건 매칭 갱신")
    return 0


if __name__ == "__main__":
    sys.exit(main())
