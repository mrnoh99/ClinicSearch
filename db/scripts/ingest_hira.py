#!/usr/bin/env python3
"""
ingest_hira.py — 건강보험심사평가원(HIRA) 병원정보서비스 수집기

공공데이터포털(data.go.kr)의 '건강보험심사평가원_병원정보서비스' OpenAPI에서
전국 의료기관 정보를 수집해 SQLite의 hospital 테이블에 upsert 합니다.

준비:
  1) https://www.data.go.kr 에서 '병원정보서비스' 활용신청 후 서비스키 발급
  2) 환경변수 설정:  export HIRA_SERVICE_KEY="발급키"
  3) 실행:          python3 db/scripts/ingest_hira.py --db db/clinicsearch.db --sido 110000

참고 엔드포인트(병원목록):
  http://apis.data.go.kr/B551182/hospInfoServicev2/getHospBasisList
주요 파라미터: sidoCd(시도), sgguCd(시군구), numOfRows, pageNo, serviceKey
응답 필드(예): yadmNm(기관명), addr(주소), telno(전화), XPos(경도), YPos(위도),
              clCdNm(종별: 상급종합/종합병원/병원...), drTotCnt(의사수) 등

※ 본 스크립트는 네트워크/키가 있을 때 동작합니다. 키가 없으면 안내 후 종료합니다.
"""
import argparse
import os
import sqlite3
import sys

API_URL = "http://apis.data.go.kr/B551182/hospInfoServicev2/getHospBasisList"

# HIRA 종별코드명 → 본 앱의 type 매핑
CL_TYPE = {
    "상급종합": "상급종합병원",
    "종합병원": "종합병원",
    "병원": "병원",
    "요양병원": "요양병원",
    "의원": "의원",
}


def fetch_page(service_key, sido, sggu, page, rows=100):
    import urllib.request
    import urllib.parse
    import json as _json
    params = {
        "serviceKey": service_key,
        "sidoCd": sido or "",
        "sgguCd": sggu or "",
        "pageNo": page,
        "numOfRows": rows,
        "_type": "json",
    }
    url = API_URL + "?" + urllib.parse.urlencode(params, safe="%")
    with urllib.request.urlopen(url, timeout=20) as r:
        data = _json.loads(r.read().decode("utf-8"))
    body = data.get("response", {}).get("body", {})
    items = body.get("items", {})
    if not items:
        return [], 0
    rows_ = items.get("item", [])
    if isinstance(rows_, dict):
        rows_ = [rows_]
    return rows_, int(body.get("totalCount", 0))


def upsert(con, rec):
    """HIRA 레코드를 hospital 테이블에 upsert (응급/접근성 등은 별도 소스에서 보강)."""
    hid = str(rec.get("ykiho") or rec.get("yadmNm"))  # 암호화요양기호 우선
    con.execute(
        """INSERT INTO hospital (id,name,type,address,lat,lng,phone,beds,source,updated_at)
           VALUES (?,?,?,?,?,?,?,?, 'HIRA', datetime('now'))
           ON CONFLICT(id) DO UPDATE SET
             name=excluded.name, type=excluded.type, address=excluded.address,
             lat=excluded.lat, lng=excluded.lng, phone=excluded.phone,
             source='HIRA', updated_at=datetime('now')""",
        (
            hid,
            rec.get("yadmNm"),
            CL_TYPE.get(rec.get("clCdNm", ""), rec.get("clCdNm")),
            rec.get("addr"),
            float(rec.get("YPos") or 0),   # 위도
            float(rec.get("XPos") or 0),   # 경도
            rec.get("telno"),
            int(rec.get("sickbedTotCnt") or 0),
        ),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/clinicsearch.db")
    ap.add_argument("--sido", default="", help="시도코드 (예: 110000=서울)")
    ap.add_argument("--sggu", default="", help="시군구코드")
    ap.add_argument("--max-pages", type=int, default=5)
    args = ap.parse_args()

    key = os.environ.get("HIRA_SERVICE_KEY")
    if not key:
        print("⚠️  HIRA_SERVICE_KEY 환경변수가 없습니다.")
        print("    공공데이터포털에서 '병원정보서비스' 키를 발급받아 설정하세요:")
        print('    export HIRA_SERVICE_KEY="발급키"')
        return 1

    con = sqlite3.connect(args.db)
    total_loaded = 0
    page = 1
    while page <= args.max_pages:
        try:
            rows, total = fetch_page(key, args.sido, args.sggu, page)
        except Exception as e:
            print(f"요청 실패(page {page}): {e}")
            break
        if not rows:
            break
        for rec in rows:
            upsert(con, rec)
            total_loaded += 1
        con.commit()
        print(f"  page {page}: {len(rows)}건 적재 (누적 {total_loaded}/{total})")
        if page * 100 >= total:
            break
        page += 1

    con.close()
    print(f"✅ HIRA 수집 완료: {total_loaded}건")
    return 0


if __name__ == "__main__":
    sys.exit(main())
