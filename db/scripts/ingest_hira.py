#!/usr/bin/env python3
"""
ingest_hira.py — 건강보험심사평가원(HIRA) 정신건강의학과 의료기관 수집기

심평원 공공 OpenAPI 두 가지를 결합해 정신건강의학과 진료 의료기관을 수집하고
SQLite의 hira_facility 테이블에 적재합니다.

  1) 병원정보서비스 getHospBasisList  : 기관 기본정보(기관명/종별/주소/좌표/의사수)
  2) 의료기관별 진료과목 getDgsbjtInfo : 진료과목(정신건강의학과=코드 23)과 과목별 전문의 수

준비(라이브):
  1) 공공데이터포털(data.go.kr)에서 '병원정보서비스' 활용신청 → 서비스키 발급
  2) export HIRA_SERVICE_KEY="발급키"
  3) python3 db/scripts/ingest_hira.py --db db/clinicsearch.db --sido 110000   # 서울

오프라인(네트워크 차단 환경) — 저장한 실제 형식 응답으로 동일 로직 검증/적재:
  python3 db/scripts/ingest_hira.py --db db/clinicsearch.db \
      --fixture-hosp db/sources/fixtures/hira_hosp_list.json \
      --fixture-dept db/sources/fixtures/hira_dgsbjt.json

응답 필드(예): yadmNm(기관명), clCdNm(종별), addr, telno, XPos(경도), YPos(위도),
              drTotCnt(의사수), ykiho(암호화요양기호) /  dgsbjtCd(진료과목코드, 정신과=23),
              dgsbjtCdNm, dgsbjtPrSdrCnt(과목별 전문의 수)
"""
import argparse
import json
import os
import sqlite3
import sys

HOSP_URL = "https://apis.data.go.kr/B551182/hospInfoServicev2/getHospBasisList"
DGSBJT_URL = "https://apis.data.go.kr/B551182/MadmDtlInfoService2.7/getDgsbjtInfo2.7"
PSYCH_DGSBJT_CD = "03"   # 정신건강의학과 진료과목코드(HIRA 명세 기준. 02=신경과, 23=가정의학과)

# HIRA 종별코드명 → 본 앱 type (clCd: 01 상급종합/11 종합병원/21 병원/28 요양병원/29 정신병원/31 의원)
CL_TYPE = {"상급종합": "상급종합병원", "상급종합병원": "상급종합병원",
           "종합병원": "종합병원", "병원": "병원", "요양병원": "요양병원",
           "정신병원": "정신병원", "의원": "의원", "한방병원": "한방병원", "한의원": "한의원"}


# ----------------------------- HTTP ----------------------------- #
def _encode_key(key):
    """data.go.kr 키 처리: 이미 %-인코딩된 Encoding 키면 그대로, 아니면 인코딩."""
    import urllib.parse
    return key if "%" in key else urllib.parse.quote(key, safe="")


def _get_json(url, params, key=None):
    import urllib.request
    import urllib.parse
    qs = urllib.parse.urlencode(params, safe="%")
    if key is not None:
        qs = f"ServiceKey={_encode_key(key)}&{qs}"
    with urllib.request.urlopen(f"{url}?{qs}", timeout=20) as r:
        body = r.read().decode("utf-8", errors="replace")
    return json.loads(body)


def _items(resp):
    """HIRA 표준 응답 구조에서 item 리스트 추출(단건은 dict로 옴)."""
    body = (resp or {}).get("response", {}).get("body", {}) or {}
    items = body.get("items") or {}
    if isinstance(items, str) or not items:
        return [], int(body.get("totalCount", 0) or 0)
    it = items.get("item", [])
    if isinstance(it, dict):
        it = [it]
    return it, int(body.get("totalCount", 0) or 0)


# ----------------------------- 파서(순수 함수) ----------------------------- #
def parse_hosp(rec):
    return {
        "ykiho": str(rec.get("ykiho") or rec.get("yadmNm")),
        "name": rec.get("yadmNm"),
        "type": CL_TYPE.get(rec.get("clCdNm", ""), rec.get("clCdNm")),
        "sido": rec.get("sidoCdNm"),
        "sggu": rec.get("sgguCdNm"),
        "addr": rec.get("addr"),
        "tel": rec.get("telno"),
        "lat": float(rec.get("YPos") or 0) or None,
        "lng": float(rec.get("XPos") or 0) or None,
        "dr_tot_cnt": int(rec.get("drTotCnt") or 0),
    }


def psych_from_depts(dept_items):
    """진료과목 목록에서 정신건강의학과 보유 여부와 전문의 수 산출."""
    has, cnt = 0, 0
    for d in dept_items:
        code = str(d.get("dgsbjtCd") or "")
        nm = d.get("dgsbjtCdNm") or ""
        if code == PSYCH_DGSBJT_CD or "정신" in nm:
            has = 1
            cnt = int(d.get("dgsbjtPrSdrCnt") or d.get("dtlSdrCnt") or 0)
    return has, cnt


# ----------------------------- 적재 ----------------------------- #
def upsert(con, h, has_psych, psych_cnt):
    con.execute(
        """INSERT INTO hira_facility
           (ykiho,name,type,sido,sggu,addr,tel,lat,lng,dr_tot_cnt,
            psych_dr_cnt,has_psychiatry,source,collected_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?, 'HIRA', date('now'))
           ON CONFLICT(ykiho) DO UPDATE SET
             name=excluded.name, type=excluded.type, sido=excluded.sido, sggu=excluded.sggu,
             addr=excluded.addr, tel=excluded.tel, lat=excluded.lat, lng=excluded.lng,
             dr_tot_cnt=excluded.dr_tot_cnt, psych_dr_cnt=excluded.psych_dr_cnt,
             has_psychiatry=excluded.has_psychiatry, collected_at=date('now')""",
        (h["ykiho"], h["name"], h["type"], h["sido"], h["sggu"], h["addr"], h["tel"],
         h["lat"], h["lng"], h["dr_tot_cnt"], psych_cnt, has_psych))


# ----------------------------- 수집 본체 ----------------------------- #
def collect_live(con, key, sido, sggu, max_pages, psychiatry_only, hosp_url, with_dept):
    """getHospBasisList를 dgsbjtCd=03(정신건강의학과)로 필터해 직접 수집.
    과목별 전문의 수가 필요하면 --with-dept 로 의료기관별상세정보(getDgsbjtInfo) 보강."""
    page, loaded = 1, 0
    while page <= max_pages:
        params = {"pageNo": page, "numOfRows": 100, "_type": "json"}
        if sido:
            params["sidoCd"] = sido
        if sggu:
            params["sgguCd"] = sggu
        if psychiatry_only:
            params["dgsbjtCd"] = PSYCH_DGSBJT_CD       # 서버측 정신건강의학과 필터
        try:
            resp = _get_json(hosp_url, params, key=key)
        except Exception as e:
            print(f"  getHospBasisList page {page} 실패: {e}")
            break
        header = (resp.get("response", {}) or {}).get("header", {}) or {}
        code = header.get("resultCode")
        if code not in (None, "00", "0"):
            print(f"  API 오류 resultCode={code} ({header.get('resultMsg')})")
            break
        rows, total = _items(resp)
        if not rows:
            break
        for rec in rows:
            h = parse_hosp(rec)
            has_psych, cnt = (1, 0) if psychiatry_only else (0, 0)
            if with_dept:
                try:
                    dresp = _get_json(DGSBJT_URL, {"ykiho": h["ykiho"], "_type": "json"}, key=key)
                    has2, cnt = psych_from_depts(_items(dresp)[0])
                    has_psych = has_psych or has2
                except Exception:
                    pass
            if psychiatry_only and not has_psych:
                continue
            upsert(con, h, has_psych, cnt)
            loaded += 1
        con.commit()
        print(f"  page {page}: 누적 {loaded}건 적재 (total {total})")
        if page * 100 >= total:
            break
        page += 1
    return loaded


def collect_fixture(con, hosp_path, dept_path, psychiatry_only):
    hosp_resp = json.load(open(hosp_path, encoding="utf-8"))
    rows, _ = _items(hosp_resp)
    dept_map = json.load(open(dept_path, encoding="utf-8")) if dept_path else {}
    loaded = 0
    for rec in rows:
        h = parse_hosp(rec)
        depts, _ = _items(dept_map.get(h["ykiho"], {}))
        has_psych, cnt = psych_from_depts(depts)
        if psychiatry_only and not has_psych:
            continue
        upsert(con, h, has_psych, cnt)
        loaded += 1
    con.commit()
    return loaded


def main():
    ap = argparse.ArgumentParser(description="HIRA 정신건강의학과 의료기관 수집")
    ap.add_argument("--db", default="db/clinicsearch.db")
    ap.add_argument("--sido", default="", help="시도코드(예: 110000=서울)")
    ap.add_argument("--sggu", default="", help="시군구코드")
    ap.add_argument("--max-pages", type=int, default=10)
    ap.add_argument("--all", action="store_true", help="정신과 외 기관도 적재(기본: 정신과만)")
    ap.add_argument("--hosp-url", default=HOSP_URL, help="getHospBasisList 엔드포인트(버전 변경 시)")
    ap.add_argument("--with-dept", action="store_true",
                    help="과목별 전문의 수 보강(의료기관별상세정보 getDgsbjtInfo 별도 활용신청 필요)")
    ap.add_argument("--fixture-hosp", help="getHospBasisList 응답 JSON(오프라인)")
    ap.add_argument("--fixture-dept", help="ykiho→getDgsbjtInfo 응답 맵 JSON(오프라인)")
    ap.add_argument("--export", action="store_true", help="db/export/hira_facilities.json 내보내기")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        print("DB가 없습니다. 먼저 'python3 db/build_db.py' 실행하세요.")
        return 1
    con = sqlite3.connect(args.db)
    psychiatry_only = not args.all

    if args.fixture_hosp:
        n = collect_fixture(con, args.fixture_hosp, args.fixture_dept, psychiatry_only)
        print(f"✅ (오프라인) HIRA 픽스처 수집: {n}건 적재")
    else:
        key = os.environ.get("HIRA_SERVICE_KEY")
        if not key:
            print("⚠️  HIRA_SERVICE_KEY 환경변수가 없습니다.")
            print("    공공데이터포털에서 '병원정보서비스' 키를 발급받아 설정하거나,")
            print("    --fixture-hosp/--fixture-dept 로 저장된 응답을 적재하세요.")
            con.close()
            return 1
        n = collect_live(con, key, args.sido, args.sggu, args.max_pages,
                         psychiatry_only, args.hosp_url, args.with_dept)
        print(f"✅ HIRA 수집 완료: {n}건 적재")

    # 요약
    cur = con.cursor()
    tot = cur.execute("SELECT count(*) FROM hira_facility").fetchone()[0]
    psy = cur.execute("SELECT count(*) FROM hira_facility WHERE has_psychiatry=1").fetchone()[0]
    drs = cur.execute("SELECT COALESCE(sum(psych_dr_cnt),0) FROM hira_facility").fetchone()[0]
    print(f"   hira_facility: 총 {tot}곳 · 정신과 보유 {psy}곳 · 정신과 전문의 합계 {drs}명")

    if args.export:
        con.row_factory = sqlite3.Row
        rows = [dict(r) for r in con.execute("SELECT * FROM hira_facility ORDER BY psych_dr_cnt DESC")]
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "export")
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "hira_facilities.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        print("   → db/export/hira_facilities.json 내보내기")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
