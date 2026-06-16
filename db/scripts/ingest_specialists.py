#!/usr/bin/env python3
"""
ingest_specialists.py — 정신과 전문의(專門醫) 통합 자료 수집 파이프라인

"수집된 사람과 연결된 자료를 가능한 모든 방법으로 수집"하기 위한 멀티소스 수집기 골격입니다.
한 전문의를 기준으로 아래 출처들을 순회하며 학력·수련·경력·학회·논문·자격을 모으고,
각 항목마다 data_source(provenance)에 '무엇을/어디서/어떻게' 수집했는지 기록합니다.

수집 출처(가능한 방법)와 매핑:
  1) 전문의 자격/소속      ← 대한신경정신의학회(KNPA) 회원/전문의 명부, 보건복지부 면허
  2) 근무기관/직위         ← 의료기관 홈페이지 의료진 소개(크롤링), HIRA 병원별 의사 정보
  3) 학력/수련             ← 의료기관·수련병원 이력, 학회 프로필
  4) 논문/연구             ← PubMed E-utilities, KoreaMed, RISS(저자명·소속 매칭)
  5) 세부 자격/인증        ← 세부 학회(중독/수면/소아청소년/EMDR 등) 인증자 명단
  6) 평판/후기             ← 병원 리뷰 집계(이용약관 준수)

주의:
  - 각 출처는 이용약관/로봇 정책/개인정보 보호를 준수해야 합니다.
  - 동명이인 구분을 위해 (이름 + 면허번호/소속기관 + 졸업학교)로 엔티티를 정합(resolution)합니다.
  - 현재 골격은 시드(JSON) 기반 적재 + PubMed 조회 예시를 제공합니다.
    실제 운영 시 각 fetch_* 함수에 출처별 수집 로직을 채워 넣으세요.

사용:
  python3 db/scripts/ingest_specialists.py --db db/clinicsearch.db --from-seed
  python3 db/scripts/ingest_specialists.py --db db/clinicsearch.db --pubmed "김현수" --affil "정신건강의학과"
"""
import argparse
import json
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEED = os.path.join(ROOT, "db", "seed", "psychiatrists.json")


def record_source(con, sid, field, source, method, url=None, confidence="medium"):
    """수집한 자료의 출처(provenance)를 기록한다."""
    con.execute(
        """INSERT INTO data_source(specialist_id,field,source,method,url,collected_at,confidence)
           VALUES (?,?,?,?,?, date('now'), ?)""",
        (sid, field, source, method, url, confidence),
    )


def fetch_pubmed(author, affiliation=None, retmax=10):
    """PubMed E-utilities로 저자 논문을 조회(공개 API, 키 선택)."""
    import urllib.request
    import urllib.parse
    term = f'{author}[Author]'
    if affiliation:
        term += f' AND {affiliation}[Affiliation]'
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    q = urllib.parse.urlencode({"db": "pubmed", "term": term, "retmax": retmax, "retmode": "json"})
    try:
        with urllib.request.urlopen(f"{base}/esearch.fcgi?{q}", timeout=20) as r:
            ids = json.loads(r.read()).get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        print(f"  PubMed 조회 실패: {e}")
        return []
    if not ids:
        return []
    q2 = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
    try:
        with urllib.request.urlopen(f"{base}/esummary.fcgi?{q2}", timeout=20) as r:
            res = json.loads(r.read()).get("result", {})
    except Exception as e:
        print(f"  PubMed 요약 실패: {e}")
        return []
    out = []
    for pid in ids:
        item = res.get(pid, {})
        year = (item.get("pubdate", "") or "")[:4]
        out.append({"title": item.get("title"), "journal": item.get("fulljournalname"),
                    "year": int(year) if year.isdigit() else None, "pmid": pid})
    return out


def load_from_seed(con):
    """시드 JSON의 통합 프로필을 적재(없으면 build_db.py 가 이미 수행)."""
    if not os.path.exists(SEED):
        print("시드 파일이 없습니다:", SEED)
        return 0
    data = json.load(open(SEED, encoding="utf-8"))
    n = con.execute("SELECT count(*) FROM specialist").fetchone()[0]
    print(f"현재 DB 전문의 {n}명 · 시드 {len(data)}명")
    print("※ 시드 기반 적재는 build_db.py 가 수행합니다. 본 스크립트는 외부 출처 보강용입니다.")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.path.join(ROOT, "db", "clinicsearch.db"))
    ap.add_argument("--from-seed", action="store_true", help="시드 적재 상태 확인")
    ap.add_argument("--pubmed", help="이 저자명으로 PubMed 논문 수집")
    ap.add_argument("--affil", help="소속(논문 동명이인 구분)")
    ap.add_argument("--specialist-id", help="수집 결과를 연결할 전문의 ID")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    con.row_factory = sqlite3.Row

    if args.from_seed:
        load_from_seed(con)

    if args.pubmed:
        pubs = fetch_pubmed(args.pubmed, args.affil)
        print(f"PubMed 논문 {len(pubs)}건 수집:")
        for p in pubs:
            print(f"  - {p['title']} ({p['journal']}, {p['year']}) PMID {p['pmid']}")
        sid = args.specialist_id
        if sid and pubs:
            for p in pubs:
                con.execute(
                    "INSERT INTO specialist_publication(specialist_id,title,journal,year,role) VALUES (?,?,?,?,?)",
                    (sid, p["title"], p["journal"], p["year"], "저자"))
                record_source(con, sid, "publications", "PubMed",
                              "E-utilities 저자 검색", f"https://pubmed.ncbi.nlm.nih.gov/{p['pmid']}/", "medium")
            con.commit()
            print(f"  → 전문의 {sid} 에 {len(pubs)}건 적재 및 출처 기록 완료")

    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
