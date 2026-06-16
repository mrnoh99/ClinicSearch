#!/usr/bin/env python3
"""
knpa_parser.py — 대한신경정신의학회(KNPA) 전문의 디렉터리 파서

KNPA 회원/전문의 찾기 결과 페이지(HTML)에서 인물 레코드를 추출해
표준 명부 스키마(collect_knpa.SCHEMA_COLS)로 매핑합니다.

설계:
  - parse_directory_html(html)  : 순수 함수. HTML → 표준 스키마 dict 리스트.
                                  (네트워크 불필요 → 픽스처로 단위 검증 가능)
  - KNPAClient                  : 검색 요청·페이지네이션·세션 처리(라이브 수집).
  - 의존성 없음(표준 라이브러리 html.parser, urllib 만 사용).

견고성:
  - 헤더 행의 라벨 텍스트로 열을 매핑 → 열 순서가 바뀌어도 동작.
  - 표(table)/카드(div) 레이아웃 모두 대응.
  - 실제 DOM에 맞춰 HEADER_ALIASES / 검색 URL 템플릿만 조정하면 됩니다.
"""
import re
import sys
from html.parser import HTMLParser

# 표준 명부 스키마
SCHEMA_COLS = ["성명", "성별", "전문의자격번호", "면허번호", "졸업대학",
               "졸업연도", "수련병원", "현소속기관", "지역", "세부전공"]

# 디렉터리 헤더 라벨 → 표준 컬럼 (다양한 표기 흡수)
HEADER_ALIASES = {
    "성명": "성명", "이름": "성명", "회원명": "성명", "의사명": "성명",
    "성별": "성별",
    "전문의번호": "전문의자격번호", "전문의자격번호": "전문의자격번호",
    "자격번호": "전문의자격번호", "전문의": "전문의자격번호", "전문의자격": "전문의자격번호",
    "면허번호": "면허번호", "면허": "면허번호", "의사면허": "면허번호",
    "졸업대학": "졸업대학", "출신대학": "졸업대학", "출신학교": "졸업대학",
    "출신교": "졸업대학", "대학": "졸업대학", "학교": "졸업대학",
    "졸업연도": "졸업연도", "졸업년도": "졸업연도", "졸업": "졸업연도",
    "수련병원": "수련병원", "수련기관": "수련병원", "수련": "수련병원",
    "소속": "현소속기관", "현소속": "현소속기관", "근무기관": "현소속기관",
    "소속기관": "현소속기관", "근무지": "현소속기관", "병원명": "현소속기관", "병원": "현소속기관",
    "지역": "지역", "시도": "지역", "주소": "지역",
    "세부전공": "세부전공", "전문분야": "세부전공", "분야": "세부전공", "관심분야": "세부전공",
}


def _clean(s):
    return re.sub(r"\s+", " ", (s or "").replace("\xa0", " ")).strip()


def map_header(label):
    lab = _clean(label).replace(" ", "")
    if lab in HEADER_ALIASES:
        return HEADER_ALIASES[lab]
    for key, col in HEADER_ALIASES.items():          # 부분 일치(예: '출신대학교')
        if key in lab:
            return col
    return None


# ----------------------------- 표(table) 추출 ----------------------------- #
class _TableCollector(HTMLParser):
    """모든 <table>을 rows[cells] 형태로 수집."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self._tbl, self._row, self._cell = [], None, None, None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._tbl = []
        elif tag == "tr" and self._tbl is not None:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []
        elif tag == "br" and self._cell is not None:
            self._cell.append(" ")

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None:
            self._row.append(_clean("".join(self._cell)))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._row:
                self._tbl.append(self._row)
            self._row = None
        elif tag == "table" and self._tbl is not None:
            self.tables.append(self._tbl)
            self._tbl = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def _rows_from_tables(html):
    p = _TableCollector()
    p.feed(html)
    out = []
    for tbl in p.tables:
        if len(tbl) < 2:
            continue
        # 헤더 행 탐색: 가장 많은 라벨이 매핑되는 행
        best_i, best_map = None, {}
        for i, row in enumerate(tbl[:3]):
            cmap = {j: map_header(c) for j, c in enumerate(row)}
            cmap = {j: v for j, v in cmap.items() if v}
            if "성명" in cmap.values() and len(cmap) > len(best_map):
                best_i, best_map = i, cmap
        if best_i is None:
            continue
        for row in tbl[best_i + 1:]:
            rec = {}
            for j, col in best_map.items():
                if j < len(row):
                    rec[col] = row[j]
            if rec.get("성명"):
                out.append(rec)
    return out


# ----------------------------- 카드(div) 추출 ----------------------------- #
class _CardCollector(HTMLParser):
    """class에 member/doctor/profile 류가 포함된 카드와 라벨:값 쌍 수집."""
    CARD_HINT = re.compile(r"(member|doctor|profile|physician|card|list-item)", re.I)
    LABELVAL = re.compile(r"([가-힣]{2,6})\s*[:：]\s*(.+?)(?=\s+[가-힣]{2,6}\s*[:：]|\s*[/,·]|$)")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cards, self._depth, self._buf, self._active = [], 0, [], False

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "") or ""
        if not self._active and self.CARD_HINT.search(cls):
            self._active, self._depth, self._buf = True, 1, []
        elif self._active:
            self._depth += 1

    def handle_endtag(self, tag):
        if self._active:
            self._depth -= 1
            if self._depth <= 0:
                self.cards.append(_clean(" ".join(self._buf)))
                self._active = False

    def handle_data(self, data):
        if self._active:
            self._buf.append(data)


def _rows_from_cards(html):
    p = _CardCollector()
    p.feed(html)
    out = []
    for text in p.cards:
        rec = {}
        for label, val in _CardCollector.LABELVAL.findall(text):
            col = map_header(label)
            if col:
                rec[col] = _clean(val)
        if rec.get("성명"):
            out.append(rec)
    return out


# ----------------------------- 표준화 ----------------------------- #
def to_roster_row(raw):
    row = {c: "" for c in SCHEMA_COLS}
    for k, v in raw.items():
        if k in row:
            row[k] = _clean(v)
    m = re.search(r"(19|20)\d{2}", row.get("졸업연도", ""))
    row["졸업연도"] = m.group(0) if m else row["졸업연도"]
    if not row["성별"]:
        row["성별"] = ""        # 미상 → 정합 단계에서 보정
    return row


def parse_directory_html(html):
    """KNPA 디렉터리 결과 HTML → 표준 명부 dict 리스트(순수 함수)."""
    raws = _rows_from_tables(html)
    if not raws:                 # 표가 없으면 카드 레이아웃 시도
        raws = _rows_from_cards(html)
    seen, rows = set(), []
    for r in raws:
        row = to_roster_row(r)
        key = (row["성명"], row["전문의자격번호"], row["졸업대학"], row["졸업연도"])
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)
    return rows


# ----------------------------- 라이브 클라이언트 ----------------------------- #
class KNPAClient:
    """KNPA 디렉터리 검색·페이지네이션(라이브). 실제 DOM/엔드포인트에 맞게 조정."""
    DEFAULT_SEARCH = ("https://www.knpa.or.kr/member/doctor_search.asp"
                      "?searchDept=%EC%A0%95%EC%8B%A0%EA%B1%B4%EA%B0%95%EC%9D%98%ED%95%99%EA%B3%BC"
                      "&page={page}")

    def __init__(self, search_url=None, region=None, timeout=20, delay=1.0):
        self.search_url = search_url or self.DEFAULT_SEARCH
        self.region = region
        self.timeout = timeout
        self.delay = delay         # 서버 부하 방지(rate limit)

    def _build(self, page):
        url = self.search_url.replace("{page}", str(page))
        if self.region:
            sep = "&" if "?" in url else "?"
            from urllib.parse import quote
            url += f"{sep}region={quote(self.region)}"
        return url

    def fetch_page(self, page):
        import urllib.request
        req = urllib.request.Request(self._build(page), headers={
            "User-Agent": "Mozilla/5.0 (compatible; ClinicSearch/1.0; +research)",
            "Accept-Language": "ko",
        })
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            charset = r.headers.get_content_charset() or "utf-8"
            return r.read().decode(charset, errors="replace")

    def iter_records(self, max_pages=50):
        import time
        for page in range(1, max_pages + 1):
            try:
                html = self.fetch_page(page)
            except Exception as e:
                print(f"⚠️  KNPA page {page} 요청 실패: {e}")
                break
            rows = parse_directory_html(html)
            if not rows:
                break
            for row in rows:
                yield row
            if self.delay:
                time.sleep(self.delay)


# ----------------------------- CLI(검증/수집) ----------------------------- #
def _main(argv=None):
    import argparse
    import csv
    import os
    ap = argparse.ArgumentParser(description="KNPA 전문의 디렉터리 파서")
    ap.add_argument("--fixture", help="로컬 HTML 파일 파싱(오프라인 검증)")
    ap.add_argument("--search-url", help="검색 URL 템플릿({page} 포함)")
    ap.add_argument("--region", help="지역 필터")
    ap.add_argument("--max-pages", type=int, default=50)
    ap.add_argument("--out", help="표준 명부 CSV 출력 경로")
    args = ap.parse_args(argv)

    if args.fixture:
        with open(args.fixture, encoding="utf-8") as f:
            rows = parse_directory_html(f.read())
        print(f"파싱 결과: {len(rows)}건")
        for r in rows:
            print("  ", " | ".join(f"{c}={r[c]}" for c in ("성명", "전문의자격번호", "졸업대학", "졸업연도", "현소속기관") if r[c]))
    else:
        client = KNPAClient(search_url=args.search_url, region=args.region)
        rows = list(client.iter_records(max_pages=args.max_pages))
        print(f"수집 결과: {len(rows)}건")

    if args.out and rows:
        import csv
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=SCHEMA_COLS)
            w.writeheader()
            w.writerows(rows)
        print(f"✅ 명부 CSV 작성: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
