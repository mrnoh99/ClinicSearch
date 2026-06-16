#!/usr/bin/env python3
"""
collect_knpa.py — 정신과 전문의 '수집' 단계 (학회명부 / 공공데이터)

학회명부·공공데이터에서 정신건강의학과 전문의 인물 레코드를 수집해
표준 명부 CSV(db/sources/knpa_roster.csv)로 출력합니다. 출력 CSV는
reconcile.py 가 기존 통합 DB와 정합(매칭·병합·중복제거)하는 입력이 됩니다.

수집 출처(공공/학회):
  1) 대한신경정신의학회(KNPA) 전문의/회원 찾기 디렉터리
       https://www.knpa.or.kr  (회원/전문의 검색 → 성명·소속·전문의번호)
  2) 공공데이터포털 data.go.kr — 보건복지부/심평원 전문의 현황·면허 관련 서비스
       https://www.data.go.kr  (서비스키 필요: 환경변수 DATA_GO_KR_KEY)
  3) 의료기관 홈페이지 의료진 소개 (소속·세부전공 보강)

표준 명부 CSV 스키마(열):
  성명,성별,전문의자격번호,면허번호,졸업대학,졸업연도,수련병원,현소속기관,지역,세부전공

동작 모드:
  - 온라인(네트워크+키): 위 출처를 호출해 CSV 생성  →  --out db/sources/knpa_roster.csv
  - 오프라인/검증: 기존 CSV의 스키마·중복·결측을 점검  →  --validate db/sources/knpa_roster_sample.csv

주의: 각 출처의 이용약관·로봇정책·개인정보 보호를 준수하세요.
"""
import argparse
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCHEMA_COLS = ["성명", "성별", "전문의자격번호", "면허번호", "졸업대학",
               "졸업연도", "수련병원", "현소속기관", "지역", "세부전공"]


def fetch_knpa_directory(region=None, max_rows=1000):
    """KNPA 전문의 디렉터리 수집(온라인). 네트워크/접근 권한 필요.

    실제 구현 시 디렉터리 검색 결과 페이지를 순회하며 인물 레코드를 파싱합니다.
    본 환경은 아웃바운드 네트워크가 차단되어 있어 호출 시 사유를 안내합니다.
    """
    import urllib.request
    url = "https://www.knpa.or.kr"
    try:
        urllib.request.urlopen(url, timeout=8)
    except Exception as e:
        print(f"⚠️  KNPA 디렉터리에 접근할 수 없습니다: {e}")
        print("    (이 실행 환경은 아웃바운드 네트워크가 제한되어 있을 수 있습니다)")
        print("    네트워크가 가능한 환경에서 디렉터리 파서를 연결해 사용하세요.")
        return []
    # TODO: 디렉터리 검색 → 페이지네이션 → 레코드 파싱 (이용약관 준수)
    return []


def fetch_datagokr_specialists(service_key, sido=None, max_rows=1000):
    """공공데이터포털 전문의 현황/면허 서비스 수집(온라인). 서비스키 필요."""
    if not service_key:
        print("⚠️  DATA_GO_KR_KEY 환경변수가 없습니다. 공공데이터 수집을 건너뜁니다.")
        return []
    # TODO: data.go.kr 해당 서비스 엔드포인트 호출 → 정신건강의학과 전문의 필터 → 레코드화
    return []


def validate(path):
    """명부 CSV 스키마/중복/결측 점검."""
    if not os.path.exists(path):
        print("파일이 없습니다:", path)
        return 1
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        rows = list(reader)
    missing_cols = [c for c in SCHEMA_COLS if c not in cols]
    print(f"행 {len(rows)}건 · 열 {len(cols)}개")
    if missing_cols:
        print("❌ 누락 열:", ", ".join(missing_cols))
    else:
        print("✅ 스키마 OK")
    # 결측치
    blanks = sum(1 for r in rows for c in SCHEMA_COLS if not (r.get(c) or "").strip())
    print(f"결측 셀: {blanks}개")
    # 잠재적 동명이인
    names = {}
    for r in rows:
        names.setdefault(r["성명"].strip(), []).append(r)
    homonyms = {n: rs for n, rs in names.items() if len(rs) > 1}
    if homonyms:
        print("동명이인 후보:")
        for n, rs in homonyms.items():
            keys = {(r["졸업대학"].strip(), r["졸업연도"].strip()) for r in rs}
            tag = "분리필요(졸업대학/연도 상이)" if len(keys) > 1 else "검토(동일 졸업이력)"
            print(f"  - {n} ({len(rs)}명) → {tag}")
    # 자격/면허번호 중복(동일인 의심 또는 데이터 오류)
    for key in ["전문의자격번호", "면허번호"]:
        seen = {}
        for r in rows:
            v = r.get(key, "").strip()
            if v:
                seen.setdefault(v, 0)
                seen[v] += 1
        dups = {v: c for v, c in seen.items() if c > 1}
        if dups:
            print(f"⚠️  {key} 중복: {dups}")
    return 0


def write_csv(rows, out):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA_COLS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"✅ 명부 CSV 작성: {out} ({len(rows)}건)")


def main():
    ap = argparse.ArgumentParser(description="정신과 전문의 수집(학회명부/공공데이터)")
    ap.add_argument("--out", default=os.path.join(ROOT, "db", "sources", "knpa_roster.csv"))
    ap.add_argument("--region", help="지역 필터(예: 서울)")
    ap.add_argument("--validate", metavar="CSV", help="기존 명부 CSV 검증 모드")
    args = ap.parse_args()

    if args.validate:
        return validate(args.validate)

    rows = []
    rows += fetch_knpa_directory(region=args.region)
    rows += fetch_datagokr_specialists(os.environ.get("DATA_GO_KR_KEY"), sido=args.region)

    if not rows:
        print("\n수집된 레코드가 없습니다(네트워크/키 제한).")
        print("→ 네트워크가 가능한 환경에서 실행하거나, 표준 스키마 CSV를 직접 준비한 뒤")
        print("  python3 db/scripts/reconcile.py --roster <CSV> 로 정합하세요.")
        print(f"  스키마: {', '.join(SCHEMA_COLS)}")
        return 0
    write_csv(rows, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
