# 전원 병원 찾기 · ClinicSearch 🚑

거주지 주소 또는 현재 위치(GPS)를 기준으로, **거리와 접근성**을 고려해
환자 **전원(轉院)**에 가장 적합한 병원을 찾아주는 앱입니다.

응급환자나 입원환자를 다른 병원으로 옮길 때, 가까우면서도 응급실·중환자실 등
필요한 인프라를 갖춘 병원을 빠르게 비교·결정하는 것을 목표로 합니다.

## 주요 기능

- 📍 **위치 기반 검색** — 거주지 주소 입력 또는 현재 위치(GPS) 사용
- 🗺 **지도 표시** — Leaflet + OpenStreetMap. 기준 위치와 후보 병원을 한눈에
- 🧮 **전원 적합도 점수(0~100)** — 거리·응급/중환자 인프라·전원 접근성·대기시간을 종합
  - 거리(최대 45점) · 응급/중환자실(최대 25점) · 접근성(구급차 진입로/전원코디/주차/교통, 최대 18점) · 대기시간(최대 12점)
- 🩺 **전문과목 + 세부전공 검색** — 26개 법정 전문과목 및 세부전공으로 필터
- 👨‍⚕️ **의료진 정보** — 사진, 졸업학교/졸업연도, 수련병원, 경력, 평판(별점·후기 수)
- 🚗 **길찾기 연동** — 카카오맵 길찾기 / 지도에서 보기
- 📱 **PWA 지원** — 아이패드/아이폰 Safari에서 "홈 화면에 추가" 시 앱처럼 전체화면 실행

## 실행 방법

별도 빌드 없이 정적 파일로 동작합니다. 로컬에서:

```bash
# 저장소 루트에서
python3 -m http.server 8137
# 브라우저에서 http://localhost:8137 접속
```

> 지도 타일과 주소 검색(지오코딩)은 인터넷 연결이 필요합니다.

## 아이패드 앱으로 설치 (PWA)

1. 아이패드 **Safari**로 배포된 주소(또는 로컬 서버 주소)를 엽니다.
2. 공유 버튼 → **홈 화면에 추가**를 누릅니다.
3. 홈 화면 아이콘으로 전체화면 앱처럼 실행됩니다. (`display: standalone`)

이 방식은 별도 앱스토어 심사 없이 즉시 사용할 수 있어, 사내/병원 내부용으로 적합합니다.
앱스토어 배포가 필요한 **네이티브(SwiftUI) 버전**도 추가 제작 가능합니다.

## 플랫폼

| 플랫폼 | 위치 | 비고 |
|--------|------|------|
| 웹앱 / PWA | 루트(`index.html` 등) | 아이패드 "홈 화면에 추가"로 앱처럼 사용 |
| 네이티브 iOS/iPadOS | `ios/` | SwiftUI + MapKit, Xcode로 빌드(앱스토어 배포용) |
| 데이터베이스 / ETL | `db/` | SQLite + 공공 API 수집 파이프라인 |

## 파일 구조

```
ClinicSearch/
├── index.html              # 웹앱 진입점 / 레이아웃
├── manifest.webmanifest    # PWA 매니페스트
├── sw.js                   # 서비스워커(오프라인 앱 셸 캐시)
├── css/styles.css          # 반응형 스타일(아이패드/모바일/데스크톱)
├── js/
│   ├── data.js             # 병원·의료진 데이터 (db/build_db.py 가 DB로부터 자동 생성)
│   └── app.js              # 검색·점수계산·지도·렌더링 로직
├── assets/                 # 앱 아이콘
├── ios/                    # 네이티브 SwiftUI 앱 (iPhone/iPad)
│   ├── project.yml         #   XcodeGen 설정
│   └── ClinicSearch/*.swift
└── db/                     # 데이터베이스 + 수집 파이프라인 (db/README.md 참고)
    ├── schema.sql          #   SQLite 스키마
    ├── build_db.py         #   시드/DB → SQLite + js/data.js + API JSON
    ├── seed/               #   기본 시드 데이터
    └── scripts/            #   HIRA·E-Gen 수집기, DB 검색 데모
```

## 네이티브 iOS / iPadOS 앱 (`ios/`)

SwiftUI + MapKit으로 작성한 네이티브 앱입니다. 웹앱과 **동일한 데이터·전원 적합도 점수 로직**을 사용합니다.

```bash
brew install xcodegen          # 최초 1회
cd ios && xcodegen generate    # ClinicSearch.xcodeproj 생성
open ClinicSearch.xcodeproj    # Xcode에서 실행 (iOS 17+)
```

XcodeGen 없이도 Xcode에서 빈 App 프로젝트를 만든 뒤 `ios/ClinicSearch/`의 `.swift`·`Info.plist`를 추가해 사용할 수 있습니다.

## 데이터 / 데이터베이스 (`db/`)

병원·의료진 데이터는 `db/`의 **SQLite DB + ETL 파이프라인**으로 관리되며, DB가 단일 진실 공급원입니다.
`db/build_db.py`가 DB로부터 웹앱(`js/data.js`)과 API용 JSON을 생성합니다.

- **병원 정보**: 건강보험심사평가원(HIRA) 병원정보서비스 OpenAPI
- **응급/중환자**: 응급의료포털(E-Gen) 실시간 응급실/중환자실 가용병상 API
- **의료진 정보**: 각 의료기관 제공 자료, 전문의 자격 정보
- **지오코딩**: 웹앱은 Nominatim, iOS는 CLGeocoder 사용. 대량 호출 시 카카오/네이버 지도 API 권장

자세한 내용은 [`db/README.md`](db/README.md) 참고.

## 면책

표시된 병원·의료진 정보는 데모용 예시이며 실제와 다를 수 있습니다.
실제 전원 결정 시 반드시 해당 의료기관 및 응급의료 정보망을 통해 직접 확인하세요.
