#!/usr/bin/env python3
"""KNPA 파서 자체 검증 (의존성 없는 간이 테스트).
실행: python3 db/scripts/test_knpa_parser.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import knpa_parser as kp

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIXTURE = os.path.join(ROOT, "db", "sources", "fixtures", "knpa_directory_page1.html")

CARD_HTML = """
<div class="doctor-card">
  <span>성명: 한도윤</span> / <span>전문의번호: 정신건강의학과-2012-001999</span>
  <span>출신대학: 충북대학교</span> · <span>졸업연도: 2007</span>
  <span>소속: 청주햇살정신건강의학과의원</span> <span>전문분야: 수면의학</span>
</div>
"""

def check(cond, msg):
    print(("✅" if cond else "❌"), msg)
    if not cond:
        raise AssertionError(msg)


def main():
    # 1) 표 레이아웃 + 변형 헤더 라벨 매핑
    rows = kp.parse_directory_html(open(FIXTURE, encoding="utf-8").read())
    check(len(rows) == 6, f"표 6행 파싱 (실제 {len(rows)})")
    k = next(r for r in rows if r["성명"] == "김현수" and r["졸업대학"] == "서울대학교")
    check(k["전문의자격번호"] == "정신건강의학과-2003-000457", "전문의번호→전문의자격번호 매핑")
    check(k["현소속기관"] == "국립서울정신건강병원", "소속기관→현소속기관 매핑(중첩 태그 제거)")
    check(k["세부전공"] == "조현병·정신증", "전문분야→세부전공 매핑")

    # 2) 동명이인 보존(병합 금지)
    kims = [r for r in rows if r["성명"] == "김현수"]
    check(len(kims) == 2, "동명이인 김현수 2건 보존")
    check({r["졸업대학"] for r in kims} == {"서울대학교", "경북대학교"}, "동명이인 졸업대학 구분")

    # 3) 모든 표준 컬럼 존재
    check(all(c in rows[0] for c in kp.SCHEMA_COLS), "표준 스키마 컬럼 완비")

    # 4) 카드 레이아웃 폴백
    cards = kp.parse_directory_html(CARD_HTML)
    check(len(cards) == 1 and cards[0]["성명"] == "한도윤", "카드 레이아웃 파싱")
    check(cards[0]["현소속기관"] == "청주햇살정신건강의학과의원", "카드 라벨:값 매핑")

    print("\n모든 파서 테스트 통과 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
